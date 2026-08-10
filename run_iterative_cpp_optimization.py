#!/usr/bin/env python3

from __future__ import annotations
import argparse
import json
import math
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Optional, List, Set, Dict

from llmo.config import *
from llmo.command import run_command, write_json, write_json_atomic, sha256_sum, sanitize_name, CommandResult
from llmo.project import llm_target_source_files, other_sources_for_replacement, source_function_name
from llmo.source import extract_code_block, contains_target_function_definition, read_support_headers
from llmo.abi import run_abi_symbol_check, load_abi_check_outcome
from llmo.benchmark import run_benchmarks_for_lib, run_benchmarks_paired
from llmo.benchmark_protocol import BenchmarkProtocol, BenchmarkMeasurement, BenchmarkComparison, calculate_benchmark_statistics, compare_benchmarks
from llmo.naming import make_run_id, make_artifact_id, make_logical_artifact_id, get_standard_path, sanitize_identifier
from llmo import llama
from llmo.llama import (
    LlmModelConfig, start_llama_server, stop_process, 
    wait_for_llama_ready, call_llm, warm_up_llm, tokenize, count_tokens, ChatCompletionResult, save_llm_call
)
from llmo.remarks import parse_remarks, prioritize_remarks, filter_remarks, batch_remarks, Remark
from llmo.build import find_libsut, compile_replacement_artifact_for_check
from llmo.reporting import confirmation_fields, normalized_timing

# =============================================================================
# Configuration & Constants
# =============================================================================

ITERATIVE_ARTIFACT_ROOT = BUILD_ROOT / "llm-cpp-remarks"
CPP_REMARK_OPTIMIZATION_PASSES = int(os.environ.get("CPP_REMARK_OPTIMIZATION_PASSES", "3"))
CPP_MAX_REPAIR_ATTEMPTS = int(os.environ.get("CPP_MAX_REPAIR_ATTEMPTS", "2"))
CONTEXT_SAFETY_MARGIN_TOKENS = int(os.environ.get("CONTEXT_SAFETY_MARGIN_TOKENS", "1000"))

# =============================================================================
# Prompt Builders
# =============================================================================

def make_optimization_feedback_prompt(
    target_name: str, 
    iteration: int, 
    total_iterations: int,
    headers: str,
    source: str,
    remarks_text: str
) -> str:
    return f"""You are an expert C++23 performance engineer.

You are iteratively optimizing {target_name}.
Optimization iteration {iteration} of {total_iterations}

The current implementation compiles successfully and preserves the required ABI.

Clang was run at {LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL} and emitted the optimization remarks below. These remarks describe optimizations Clang performed, missed, or analyzed.

Use them as diagnostic evidence to identify C++-level changes that could enable better generated code or improve the algorithm beyond what the compiler can do automatically.

Do not blindly follow every remark. Some remarks only explain a compiler decision and changing the source may not be beneficial.

Prefer meaningful runtime improvements such as:
- better algorithms or data structures;
- reducing allocations and copies;
- improving memory locality;
- simplifying dependencies that prevent vectorization;
- eliminating unnecessary work;
- making aliasing/lifetime/control-flow properties clearer when they are actually guaranteed by the API;
- exposing profitable transformations to the compiler.

Do not make unsafe assumptions merely to satisfy an optimization remark. A vectorizer remark might suggest aliasing is blocking vectorization, for example. That does NOT mean you are allowed to add restrict semantics unless those semantics are actually guaranteed by the API/program behavior.

Hard requirements:
- Return one complete replacement for {target_name}.
- Preserve the public C ABI exactly as declared in library.h.
- Do not change exported names, parameter types, return types, struct layouts, ownership rules, or allocation/free conventions.
- Do not implement unrelated exported functions.
- Preserve externally observable behavior for all valid inputs.
- Do not specialize for benchmark constants or hard-code benchmark results.
- Exceptions must not escape through extern "C" APIs.
- Do not modify library.h or sut_common.h.
- Return raw C++ only.
- No Markdown, explanation, notes, or code fences.

Headers:
{headers}

Current {target_name}:
{source}

Clang optimization remarks:
{remarks_text}
"""

def make_compile_repair_prompt(
    target_name: str,
    headers: str,
    source: str,
    diagnostics: str,
    max_diag_chars: int = 24000
) -> str:
    return f"""You are an expert C++23 build-fix and performance engineer.

Task: fix this optimized {target_name} so the whole SUT shared library compiles successfully.
The immediate goal is to restore a valid build.

Hard requirements:
- Return one complete replacement for {target_name}.
- Preserve the public C ABI exactly as declared in library.h.
- Do not change any exported function name, parameter type, return type, struct layout, ownership rule, or allocation/freeing convention visible in library.h.
- Do not add implementations for unrelated exported functions from library.h.
- Preserve the intended optimized behavior and runtime-performance focus as much as possible.
- Do not modify library.h or sut_common.h.
- Return raw C++ only.
- No Markdown, explanation, notes, or code fences.

Headers:
{headers}

Failed {target_name}:
{source}

Diagnostics:
{diagnostics[-max_diag_chars:]}
"""

# =============================================================================
# Build & Diagnostic Helpers
# =============================================================================

def compile_for_remarks(
    source_file: Path, 
    output_dir: Path
) -> CommandResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    obj_file = output_dir / f"{source_file.stem}.o"
    remark_file = output_dir / "optimization_record.yaml"
    
    command = [
        CLANG_CXX_COMPILER, "-std=c++23", LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL, "-DNDEBUG", "-fPIC",
        "-fsave-optimization-record=yaml",
        f"-foptimization-record-file={remark_file}",
        "-I", str(SUT_DIR),
        "-I", str(PROJECT_ROOT),
        "-c", str(source_file),
        "-o", str(obj_file)
    ]
    
    return run_command(
        command, 
        PROJECT_ROOT, 
        output_dir / "compile_remarks_stdout.txt", 
        output_dir / "compile_remarks_stderr.txt",
        timeout_seconds=LLM_COMPILE_TIMEOUT_SECONDS
    )

def build_full_library(
    output_dir: Path,
    target_source_name: str,
    replacement_file: Path
) -> CommandResult:
    result = compile_replacement_artifact_for_check(
        output_dir=output_dir,
        target_source_name=target_source_name,
        replacement_file=replacement_file,
        source_kind="cpp",
        cxx_compiler=CLANG_CXX_COMPILER,
        opt_level=LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL,
        sut_dir=SUT_DIR,
        project_root=PROJECT_ROOT,
        timeout=LLM_COMPILE_TIMEOUT_SECONDS,
        other_sources=other_sources_for_replacement(target_source_name)
    )
    return result.command_result

def run_repair_step(
    model_name: str,
    target_source: Path,
    failed_source_file: Path,
    iteration: int,
    repair_attempt: int,
    repair_dir: Path,
    headers: str,
    compile_result: Optional[CommandResult] = None,
    abi_result: Optional[CommandResult] = None
) -> IterationResult:
    repair_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(failed_source_file, repair_dir / "source_input.cpp")
    
    diagnostics = []
    if compile_result:
        stdout = ""
        stderr = ""
        if Path(compile_result.stdout_file).exists():
            stdout = Path(compile_result.stdout_file).read_text(encoding="utf-8", errors="replace")
        if Path(compile_result.stderr_file).exists():
            stderr = Path(compile_result.stderr_file).read_text(encoding="utf-8", errors="replace")
        
        if stdout or stderr:
            diagnostics.append("Compiler/linker diagnostics:")
            if stdout: diagnostics.append(f"STDOUT:\n{stdout}")
            if stderr: diagnostics.append(f"STDERR:\n{stderr}")
            
    if abi_result:
        stdout = ""
        stderr = ""
        if Path(abi_result.stdout_file).exists():
            stdout = Path(abi_result.stdout_file).read_text(encoding="utf-8", errors="replace")
        if Path(abi_result.stderr_file).exists():
            stderr = Path(abi_result.stderr_file).read_text(encoding="utf-8", errors="replace")
            
        if stdout or stderr:
            diagnostics.append("ABI validation diagnostics:")
            if stdout: diagnostics.append(f"STDOUT:\n{stdout}")
            if stderr: diagnostics.append(f"STDERR:\n{stderr}")
            
    all_diagnostics = "\n\n".join(diagnostics)
    failed_source = failed_source_file.read_text(encoding="utf-8", errors="replace")
    
    # Budgeting for repair prompt
    system_prompt = "You are a compiler and C++ optimization assistant. Return only the requested source code."
    dummy_prompt = make_compile_repair_prompt(target_source.name, headers, failed_source, "")
    fixed_tokens = count_tokens(dummy_prompt) + count_tokens(system_prompt)
    available_tokens = llama.EFFECTIVE_LLAMA_CTX_SIZE - fixed_tokens - LLM_MAX_TOKENS - CONTEXT_SAFETY_MARGIN_TOKENS
    
    # Conservative truncation: 2 chars per token
    max_diag_chars = max(1000, available_tokens * 2)
    
    prompt = make_compile_repair_prompt(target_source.name, headers, failed_source, all_diagnostics, max_diag_chars=max_diag_chars)
    
    # Final pre-flight check
    prompt_tokens = count_tokens(prompt)
    system_prompt_tokens = count_tokens(system_prompt)
    total_requested_tokens = prompt_tokens + system_prompt_tokens + LLM_MAX_TOKENS
    if total_requested_tokens > llama.EFFECTIVE_LLAMA_CTX_SIZE:
        # Even more aggressive truncation if still too large
        max_diag_chars = max(500, max_diag_chars // 2)
        prompt = make_compile_repair_prompt(target_source.name, headers, failed_source, all_diagnostics, max_diag_chars=max_diag_chars)
        
        prompt_tokens = count_tokens(prompt)
        total_requested_tokens = prompt_tokens + system_prompt_tokens + LLM_MAX_TOKENS
        if total_requested_tokens > llama.EFFECTIVE_LLAMA_CTX_SIZE:
            error_msg = f"Repair prompt exceeds effective context budget even after truncation: {total_requested_tokens} > {llama.EFFECTIVE_LLAMA_CTX_SIZE}"
            print(f"  Error: {error_msg}")
            return IterationResult(iteration, f"repair_{repair_attempt:02d}", False, failed_source_file, metadata={"error": error_msg})

    (repair_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    
    print(f"  Iteration {iteration:02d} Repair {repair_attempt:02d}: Calling LLM for repair...")
    start_time = time.perf_counter()
    try:
        result = call_llm(model_name, prompt, system_prompt)
        duration = time.perf_counter() - start_time
        
        resp_file = save_llm_call(repair_dir, f"repair_{repair_attempt:02d}", result)
        
        if result.finish_reason == "length":
            print(f"  Iteration {iteration:02d} Repair {repair_attempt:02d}: Truncated response.")
            return IterationResult(iteration, f"repair_{repair_attempt:02d}", False, failed_source_file, metadata={"error": "response_truncated", "duration_seconds": duration, "raw_response_file": resp_file})

        new_source = extract_code_block(result.content)
        output_file = repair_dir / "source_output.cpp"
        output_file.write_text(new_source, encoding="utf-8")
        
        if not contains_target_function_definition(new_source, target_source.name):
            return IterationResult(iteration, f"repair_{repair_attempt:02d}", False, output_file, metadata={"error": "Target function missing", "duration_seconds": duration, "llm_result": asdict(result), "raw_response_file": resp_file})

        # Compile and ABI check the repaired source
        comp_res = build_full_library(repair_dir, target_source.name, output_file)
        if comp_res.returncode == 0:
            libsut = find_libsut(repair_dir)
            if libsut:
                abi_res_cmd = run_abi_symbol_check(repair_dir, libsut)
                abi_outcome = load_abi_check_outcome(repair_dir, abi_res_cmd)
                if abi_outcome.success:
                    return IterationResult(iteration, f"repair_{repair_attempt:02d}", True, output_file, compile_result=comp_res, abi_result=abi_res_cmd, metadata={"duration_seconds": duration, "llm_result": asdict(result), "abi_error": abi_outcome.error})
                return IterationResult(iteration, f"repair_{repair_attempt:02d}", False, output_file, compile_result=comp_res, abi_result=abi_res_cmd, metadata={"duration_seconds": duration, "llm_result": asdict(result), "abi_error": abi_outcome.error})
        
        return IterationResult(iteration, f"repair_{repair_attempt:02d}", False, output_file, compile_result=comp_res, metadata={"duration_seconds": duration, "llm_result": asdict(result)})
        
    except Exception as exc:
        print(f"  Repair LLM call failed: {exc}")
        return IterationResult(iteration, f"repair_{repair_attempt:02d}", False, failed_source_file, metadata={"error": str(exc)})

# =============================================================================
# Iteration Manager
# =============================================================================

@dataclass
class IterationResult:
    iteration: int
    type: str # optimization, repair
    success: bool
    source_file: Path
    compile_result: Optional[CommandResult] = None
    abi_result: Optional[CommandResult] = None
    remarks_file: Optional[Path] = None
    metadata: Optional[Dict[str, Any]] = None
    shown_remarks: Optional[List[str]] = None
    accepted_remarks: Optional[List[str]] = None

def run_optimization_iteration(
    model_name: str,
    target_source: Path,
    current_source_file: Path,
    iteration: int,
    attempt: int,
    total_iterations: int,
    iter_dir: Path,
    shown_fingerprints: Set[str],
    headers: str
) -> IterationResult:
    iter_dir.mkdir(parents=True, exist_ok=True)
    
    # Save input source
    shutil.copy2(current_source_file, iter_dir / "source_input.cpp")
    
    # 1. Compile for remarks
    print(f"  Iteration {iteration:02d} Attempt {attempt:02d}: Compiling for remarks...")
    comp_remarks = compile_for_remarks(current_source_file, iter_dir)
    if comp_remarks.returncode != 0:
        return IterationResult(iteration, "optimization", False, current_source_file, compile_result=comp_remarks)
    
    # 2. Parse and batch remarks
    remark_file = iter_dir / "optimization_record.yaml"
    remarks = []
    if remark_file.exists():
        remarks = parse_remarks(remark_file.read_text(encoding="utf-8"))
    
    prioritized = prioritize_remarks(remarks, target_source.name)
    unseen = filter_remarks(prioritized, shown_fingerprints)
    
    if not unseen:
        print(f"  Iteration {iteration:02d}: No unseen optimization remarks found.")
        return IterationResult(iteration, "optimization", False, current_source_file, metadata={"stop_reason": "no_unseen_remarks"})

    # Budget context
    # Reserve tokens for: system prompt, response, safety margin
    system_prompt = "You are a compiler and C++ optimization assistant. Return only the requested source code."
    fixed_parts = system_prompt + headers + current_source_file.read_text(encoding="utf-8")
    fixed_tokens = count_tokens(fixed_parts)
    
    # Also reserve for instructions in the optimization prompt
    dummy_remarks = "REMARKS_HERE"
    full_prompt_template = make_optimization_feedback_prompt(target_source.name, iteration, total_iterations, headers, current_source_file.read_text(encoding="utf-8"), dummy_remarks)
    template_tokens = count_tokens(full_prompt_template)
    
    available_tokens = llama.EFFECTIVE_LLAMA_CTX_SIZE - template_tokens - LLM_MAX_TOKENS - CONTEXT_SAFETY_MARGIN_TOKENS
    if available_tokens < 100:
        print(f"  Warning: very low token budget for remarks ({available_tokens}).")
    
    selected, remaining = batch_remarks(unseen, available_tokens, count_tokens)
    
    if not selected:
        print(f"  Iteration {iteration:02d}: No remarks could fit in context.")
        return IterationResult(iteration, "optimization", False, current_source_file, metadata={"stop_reason": "no_unseen_remarks"})

    remarks_text = "\n---\n".join(r.raw for r in selected) if selected else "No relevant optimization remarks found for this batch."
    (iter_dir / "selected_remarks.txt").write_text(remarks_text, encoding="utf-8")
    
    shown_in_this_batch = [r.fingerprint() for r in selected]
    
    selection_metadata = {
        "context_size": llama.EFFECTIVE_LLAMA_CTX_SIZE,
        "max_output_tokens": LLM_MAX_TOKENS,
        "fixed_tokens_est": fixed_tokens,
        "template_tokens_est": template_tokens,
        "remark_count_total": len(remarks),
        "remark_count_prioritized": len(prioritized),
        "remark_count_unseen": len(unseen),
        "remark_count_in_prompt": len(selected),
        "remark_count_remaining": len(remaining),
        "available_tokens_for_remarks": available_tokens
    }
    write_json(iter_dir / "remark_selection.json", selection_metadata)
    
    # 3. Call LLM
    prompt = make_optimization_feedback_prompt(target_source.name, iteration, total_iterations, headers, current_source_file.read_text(encoding="utf-8"), remarks_text)
    
    # Final pre-flight check
    prompt_tokens = count_tokens(prompt)
    system_prompt_tokens = count_tokens(system_prompt)
    total_requested_tokens = prompt_tokens + system_prompt_tokens + LLM_MAX_TOKENS
    if total_requested_tokens > llama.EFFECTIVE_LLAMA_CTX_SIZE:
        error_msg = f"Prompt exceeds effective context budget: {total_requested_tokens} > {llama.EFFECTIVE_LLAMA_CTX_SIZE}"
        print(f"  Error: {error_msg}")
        return IterationResult(iteration, "optimization", False, current_source_file, metadata={"error": error_msg})

    (iter_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    
    print(f"  Iteration {iteration:02d} Attempt {attempt:02d}: Calling LLM for optimization...")
    start_time = time.perf_counter()
    try:
        result = call_llm(model_name, prompt, system_prompt)
        duration = time.perf_counter() - start_time
        
        resp_file = save_llm_call(iter_dir, f"optimization_{attempt:02d}", result)
        
        if result.finish_reason == "length":
             print(f"  Iteration {iteration:02d} Attempt {attempt:02d}: Truncated response.")
             return IterationResult(iteration, "optimization", False, current_source_file, metadata={"error": "response_truncated", "duration_seconds": duration, "raw_response_file": resp_file})

        new_source = extract_code_block(result.content)
        output_file = iter_dir / "source_output.cpp"
        output_file.write_text(new_source, encoding="utf-8")
        
        return IterationResult(
            iteration, "optimization", True, output_file, 
            remarks_file=remark_file, 
            metadata={"duration_seconds": duration, "llm_result": asdict(result), "raw_response_file": resp_file, **selection_metadata},
            shown_remarks=shown_in_this_batch
        )
    except Exception as exc:
        print(f"  LLM call failed: {exc}")
        return IterationResult(iteration, "optimization", False, current_source_file, metadata={"error": str(exc)})

def optimize_target(
    model_config: LlmModelConfig,
    target_source: Path,
    num_passes: int,
    target_output_dir: Path,
    headers: str,
    benchmark_all: bool,
    protocol: BenchmarkProtocol,
    run_id: str
) -> Dict[str, Any]:
    model_name = model_config.alias or model_config.name
    model_id = sanitize_identifier(model_config.name)
    experiment_type = "guided-cpp"
    pipeline_start_time = time.perf_counter()
    def failure_result(error: str, **extra: Any) -> Dict[str, Any]:
        timing = normalized_timing(0.0, 0.0, time.perf_counter() - pipeline_start_time)
        return {
            "success": False,
            "error": error,
            "stopped_reason": error,
            "timing": timing,
            **confirmation_fields("failed", "not-run"),
            **extra,
        }
    print(f"\n=== Optimizing {target_source.name} with {model_name} ===")

    # 2. Prevent stale benchmark/artifact reuse
    if target_output_dir.exists():
        shutil.rmtree(target_output_dir)
    target_output_dir.mkdir(parents=True, exist_ok=True)
    
    shown_fingerprints = set()
    all_shown_fingerprints = set()
    accepted_fingerprints = set()
    
    # 0. Baseline Artifact
    print(f"  Establishing baseline for {target_source.name}...")
    baseline_id = make_artifact_id(experiment_type, target_source.stem, model_id, suffix="baseline")
    baseline_dir = target_output_dir / "artifacts" / baseline_id
    baseline_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target_source, baseline_dir / target_source.name)
    
    comp_res = build_full_library(baseline_dir, target_source.name, target_source)
    if comp_res.returncode != 0:
        print(f"  ERROR: Baseline compilation failed for {target_source.name}.")
        return failure_result("baseline_compilation_failed")
    
    libsut = find_libsut(baseline_dir)
    if not libsut:
        print(f"  ERROR: Could not find libSUT.so for baseline.")
        return failure_result("baseline_libsut_not_found")
        
    abi_res_cmd = run_abi_symbol_check(baseline_dir, libsut)
    abi_outcome = load_abi_check_outcome(baseline_dir, abi_res_cmd)
    if not abi_outcome.success:
        print(f"  ERROR: Baseline ABI check failed: {abi_outcome.error}")
        return failure_result("baseline_abi_failed", abi_error=abi_outcome.error)
        
    # We'll use this as the initial "best" artifact
    current_best_id = baseline_id
    current_best_dir = baseline_dir
    current_best_libsut = libsut
    current_best_source = baseline_dir / target_source.name
    best_is_baseline = True
    best_iteration = 0
    
    # We still need initial baseline stats for iteration 0
    baseline_measurements = run_benchmarks_for_lib(baseline_dir, libsut, target_source.stem, run_all=False, artifact_id=baseline_id)
    baseline_stats = calculate_benchmark_statistics(baseline_measurements, protocol.repetitions)
    
    iterations_meta = []
    
    stop_reason = "completed"
    total_repair_attempts = 0
    optimization_llm_duration = 0.0
    repair_llm_duration = 0.0
    
    completed_passes = 0
    attempt_idx = 1
    while completed_passes < num_passes:
        if attempt_idx > 10:
            print(f"  Iteration {completed_passes + 1:02d}: Maximum total attempts reached (10).")
            stop_reason = "too_many_attempts"
            break
            
        iter_idx = completed_passes + 1
        cand_id = make_artifact_id(experiment_type, target_source.stem, model_id, suffix=f"iteration-{iter_idx:02d}")
        iter_dir = target_output_dir / "artifacts" / cand_id
        
        # 1. Optimization step
        opt_res = run_optimization_iteration(
            model_name, target_source, current_best_source, 
            iter_idx, attempt_idx, num_passes, iter_dir, shown_fingerprints, headers
        )
        optimization_llm_duration += opt_res.metadata.get("duration_seconds", 0.0) if opt_res.metadata else 0.0
        
        if not opt_res.success:
            if opt_res.metadata and opt_res.metadata.get("stop_reason") == "no_unseen_remarks":
                stop_reason = "no_unseen_remarks"
                break
            elif opt_res.compile_result and opt_res.compile_result.returncode != 0:
                print(f"  Iteration {iter_idx:02d}: Compilation for remarks failed on current best.")
                stop_reason = "remark_compilation_failed"
                break
            else:
                stop_reason = f"optimization_failed_pass_{iter_idx}"
                iterations_meta.append(asdict(opt_res))
                break
        
        if opt_res.shown_remarks:
            for f in opt_res.shown_remarks:
                shown_fingerprints.add(f)
                all_shown_fingerprints.add(f)
            
        # 2. Detect unchanged source
        new_source = opt_res.source_file.read_text(encoding="utf-8")
        if new_source.strip() == current_best_source.read_text(encoding="utf-8").strip():
            print(f"  Iteration {iter_idx:02d} Attempt {attempt_idx:02d}: No change detected in source. Stopping.")
            opt_res.metadata["no_change"] = True
            opt_res.metadata["accepted_as_best"] = False
            iterations_meta.append(asdict(opt_res))
            write_json(iter_dir / "iteration_metadata.json", asdict(opt_res))
            stop_reason = "no_change"
            break
            
        # 3. Validation & Repair loop
        valid = False
        repair_source_file = opt_res.source_file
        final_opt_res = opt_res
        
        if not contains_target_function_definition(new_source, target_source.name):
            print(f"  Iteration {iter_idx:02d}: Target function missing. Repairing...")
            comp_res = None
            abi_res_cmd = None
        else:
            comp_res = build_full_library(iter_dir, target_source.name, repair_source_file)
            if comp_res.returncode == 0:
                libsut = find_libsut(iter_dir)
                if libsut:
                    abi_res_cmd = run_abi_symbol_check(iter_dir, libsut)
                    abi_outcome = load_abi_check_outcome(iter_dir, abi_res_cmd)
                    if abi_outcome.success:
                        valid = True
                        final_opt_res.compile_result = comp_res
                        final_opt_res.abi_result = abi_res_cmd
                        final_opt_res.metadata["libsut"] = str(libsut)
                else:
                    abi_res_cmd = None
            else:
                abi_res_cmd = None

        if not valid:
            for repair_attempt in range(1, CPP_MAX_REPAIR_ATTEMPTS + 1):
                repair_dir = iter_dir / f"repair_{repair_attempt:02d}"
                repair_res = run_repair_step(
                    model_name, target_source, repair_source_file,
                    iter_idx, repair_attempt, repair_dir, headers,
                    compile_result=comp_res, abi_result=abi_res_cmd
                )
                repair_llm_duration += repair_res.metadata.get("duration_seconds", 0.0) if repair_res.metadata else 0.0
                total_repair_attempts += 1
                iterations_meta.append(asdict(repair_res))

                if repair_res.success:
                    valid = True
                    final_opt_res = repair_res
                    break

                repair_source_file = repair_res.source_file
                comp_res = repair_res.compile_result
                abi_res_cmd = repair_res.abi_result

        if valid:
            # 4. Paired repeated benchmark comparison against the current best.
            print(f"  Iteration {iter_idx:02d}: Valid candidate produced. Comparing against current best...")
            iter_libsut = find_libsut(final_opt_res.source_file.parent)
            if not iter_libsut:
                stop_reason = f"candidate_libsut_not_found_pass_{iter_idx}"
                iterations_meta.append(asdict(final_opt_res))
                write_json_atomic(iter_dir / "iteration_metadata.json", asdict(final_opt_res))
                break

            comparison = run_benchmarks_paired(
                iter_libsut,
                current_best_libsut,
                target_source.stem,
                protocol,
                candidate_id=cand_id,
                baseline_id=current_best_id
            )
            final_opt_res.metadata["benchmark_comparison"] = asdict(comparison)

            art_meta = {
                "schema_version": 2,
                "artifact_id": cand_id,
                "run_id": run_id,
                "experiment_type": experiment_type,
                "model_id": model_id,
                "benchmark_name": target_source.stem,
                "pipeline_id": f"cpp-llm-iterative-pass-{iter_idx:02d}__clang-o3",
                "parent_artifact_id": current_best_id,
                "paths": {
                    "source": str(final_opt_res.source_file),
                    "libsut": str(iter_libsut)
                },
                "comparison_vs_previous_best": asdict(comparison),
                "timing": normalized_timing(
                    optimization_llm_duration,
                    repair_llm_duration,
                    time.perf_counter() - pipeline_start_time,
                ),
                **confirmation_fields(comparison.classification, "not-run"),
            }
            write_json_atomic(final_opt_res.source_file.parent / "artifact.json", art_meta)

            if comparison.classification == "improved":
                improvement = comparison.relative_change_percent
                print(f"  Iteration {iter_idx:02d}: Accepted as new best ({improvement:+.1f}%)")
                current_best_id = cand_id
                current_best_dir = final_opt_res.source_file.parent
                current_best_libsut = iter_libsut
                current_best_source = final_opt_res.source_file
                best_is_baseline = False
                best_iteration = iter_idx
                shown_fingerprints.clear()
                final_opt_res.metadata["accepted_as_best"] = True
                if opt_res.shown_remarks:
                    accepted_fingerprints.update(opt_res.shown_remarks)
            else:
                change = comparison.relative_change_percent
                change_text = f"{change:+.1f}%" if change is not None else "unavailable"
                print(f"  Iteration {iter_idx:02d}: Rejected ({comparison.classification}). Change: {change_text}")
                final_opt_res.metadata["accepted_as_best"] = False

            completed_passes += 1
            attempt_idx = 1
            iterations_meta.append(asdict(final_opt_res))
            write_json_atomic(final_opt_res.source_file.parent / "iteration_metadata.json", asdict(final_opt_res))
        else:
            print(f"  Iteration {iter_idx:02d}: Failed to produce a valid build after repair attempts.")
            stop_reason = f"repair_failed_pass_{iter_idx}"
            iterations_meta.append(asdict(opt_res))
            write_json_atomic(iter_dir / "iteration_metadata.json", asdict(opt_res))
            break

    # 5. Final Confirmation Comparison
    final_id = make_artifact_id(experiment_type, target_source.stem, model_id, suffix="final")
    final_dir = target_output_dir / "artifacts" / final_id
    final_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nPerforming final confirmation comparison for {target_source.name}...")
    shutil.copy2(current_best_source, final_dir / f"optimized_{target_source.name}")
    shutil.copy2(current_best_libsut, final_dir / "libSUT.so")
    
    baseline_libsut = find_libsut(baseline_dir)
    if best_is_baseline:
        final_comparison = BenchmarkComparison(
            baseline_artifact_id=baseline_id,
            candidate_artifact_id=final_id,
            baseline_statistics=baseline_stats,
            candidate_statistics=baseline_stats,
            relative_change_percent=0.0,
            classification="unchanged_within_noise",
            sequence=[],
            noise_threshold_percent=protocol.noise_threshold_percent,
        )
    else:
        confirmation_protocol = replace(protocol, seed=protocol.seed + 1)
        final_comparison = run_benchmarks_paired(
            current_best_libsut,
            baseline_libsut,
            target_source.stem,
            confirmation_protocol,
            candidate_id=final_id,
            baseline_id=baseline_id
        )
    
    pipeline_seconds = time.perf_counter() - pipeline_start_time
    timing = normalized_timing(optimization_llm_duration, repair_llm_duration, pipeline_seconds)
    selection_status = "unchanged_within_noise" if best_is_baseline else "improved"
    confirmation_status = "not-required" if best_is_baseline else final_comparison.classification
    status_fields = confirmation_fields(selection_status, confirmation_status)
    art_meta = {
        "schema_version": 2,
        "artifact_id": final_id,
        "run_id": run_id,
        "experiment_type": experiment_type,
        "model_id": model_id,
        "benchmark_name": target_source.stem,
        "pipeline_id": "cpp-llm-guided-remarks__clang-o3",
        "logical_artifact_id": make_logical_artifact_id(
            experiment_type, run_id, final_id, target_source.stem, model_id,
            "cpp-llm-guided-remarks__clang-o3",
        ),
        "parent_artifact_id": baseline_id,
        "source_provenance": f"iteration-{best_iteration:02d}" if not best_is_baseline else "original",
        "paths": {
            "source": str(final_dir / f"optimized_{target_source.name}"),
            "libsut": str(final_dir / "libSUT.so")
        },
        "final_comparison_vs_original": asdict(final_comparison),
        "confirmation_seed": protocol.seed + 1 if not best_is_baseline else None,
        "timing": timing,
        **status_fields,
    }
    write_json_atomic(final_dir / "artifact.json", art_meta)

    summary = {
        "model": model_config.name,
        "target": target_source.name,
        "run_id": run_id,
        "experiment_type": experiment_type,
        "requested_optimization_passes": num_passes,
        "completed_optimization_passes": completed_passes,
        "repair_attempts": total_repair_attempts,
        "stopped_reason": stop_reason,
        "best_iteration": best_iteration,
        "best_is_baseline": best_is_baseline,
        "final_artifact_id": current_best_id,
        "final_confirmation_id": final_id,
        "llm_duration_seconds": timing["total_llm_seconds"],
        "total_duration_seconds": pipeline_seconds,
        "timing": timing,
        "confirmation_seed": protocol.seed + 1 if not best_is_baseline else None,
        **status_fields,
        "shown_remarks": sorted(list(all_shown_fingerprints)),
        "accepted_remarks": sorted(list(accepted_fingerprints)),
        "iterations": iterations_meta
    }
    
    write_json_atomic(target_output_dir / "summary.json", summary)
    return summary

def main() -> int:
    parser = argparse.ArgumentParser(description="Iterative C++ optimization using Clang remarks and LLM.")
    parser.add_argument("--only", action="append", help="Optimize only this target function.")
    parser.add_argument("--model", action="append", help="Run only for these models.")
    parser.add_argument("--passes", type=int, default=CPP_REMARK_OPTIMIZATION_PASSES, help="Number of optimization passes.")
    parser.add_argument("--benchmark-repetitions", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--noise-threshold-percent", type=float, default=2.0)
    parser.add_argument("--run-id", help="Explicit run ID.")
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "results")
    args = parser.parse_args()
    
    run_id = make_run_id(args.run_id)
    output_root = args.output_root
    
    protocol = BenchmarkProtocol(
        repetitions=args.benchmark_repetitions,
        seed=args.seed,
        noise_threshold_percent=args.noise_threshold_percent,
        ordering="paired"
    )
    
    # Discovery
    targets = llm_target_source_files()
    if args.only:
        targets = [t for t in targets if t.stem in args.only]
        
    models_configs = [LlmModelConfig(**m) for m in LLM_MODELS]
    if args.model:
        models_configs = [m for m in models_configs if m.name in args.model or m.alias in args.model]
        
    if not targets:
        print("No targets selected.")
        return 1
    if not models_configs:
        print("No models selected.")
        return 1
        
    # Preparation
    headers = read_support_headers()
    
    from llmo.metadata import get_run_metadata
    run_meta = get_run_metadata()
    run_meta.update({
        "run_id": run_id,
        "experiment_type": "guided-cpp",
        "benchmark_protocol": asdict(protocol)
    })
    
    run_dir = output_root / "guided-cpp" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(run_dir / "run.json", run_meta)
    
    overall_summary = []
    
    for model in models_configs:
        model_name = model.alias or model.name
        
        server_process = None
        try:
            server_process, _ = start_llama_server(model, run_dir)
            wait_for_llama_ready(server_process, run_dir)
            warm_up_llm(model_name, run_dir)
            
            # Record per-model metadata
            run_meta.setdefault("models", {})[model.name] = {
                "model_name": model.name,
                "alias": model.alias,
                "hf_repo": model.hf_repo,
                "effective_context_size": llama.EFFECTIVE_LLAMA_CTX_SIZE,
            }
            write_json_atomic(run_dir / "run.json", run_meta)

            for target in targets:
                target_dir = run_dir / sanitize_identifier(model.name) / sanitize_name(target.name)
                try:
                    res = optimize_target(
                        model, target, args.passes, target_dir, 
                        headers, False, protocol, run_id
                    )
                    overall_summary.append(res)
                except Exception as exc:
                    print(f"  Target {target.name} failed with exception: {exc}")
                    import traceback
                    traceback.print_exc()
                    overall_summary.append({
                        "model": model.name,
                        "target": target.name,
                        "success": False,
                        "error": str(exc)
                    })
                write_json_atomic(run_dir / "summary.json", overall_summary)
                
        except Exception as exc:
            print(f"Model {model.name} failed: {exc}")
            overall_summary.append({"model": model.name, "error": str(exc)})
            write_json_atomic(run_dir / "summary.json", overall_summary)
        finally:
            stop_process(server_process)
            
    return 0

if __name__ == "__main__":
    sys.exit(main())
