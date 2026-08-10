#!/usr/bin/env python3

import argparse
import sys
import time
import shutil
import random
import json
import hashlib
import platform
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import asdict

from llmo.config import *
from llmo.command import sanitize_name, write_json, write_json_atomic, sha256_sum, CommandResult
from llmo.project import llm_target_source_files, other_sources_for_replacement, source_function_name
from llmo.source import extract_code_block, validate_llvm_ir_module, ValidationResult, read_support_headers
from llmo.abi import run_abi_symbol_check, load_abi_check_outcome
from llmo.benchmark import run_benchmarks_for_lib, run_benchmarks_paired
from llmo.benchmark_protocol import BenchmarkProtocol, BenchmarkMeasurement, calculate_benchmark_statistics, compare_benchmarks
from llmo.naming import make_run_id, make_artifact_id, make_logical_artifact_id, get_standard_path, sanitize_identifier
from llmo import llama
from llmo.llama import (
    LlmModelConfig, start_llama_server, stop_process, 
    wait_for_llama_ready, call_llm, warm_up_llm, calculate_token_budget, count_tokens, ChatCompletionResult, TokenBudget, save_llm_call
)
from llmo.build import find_libsut, CompileResult
from llmo.llvm import (
    generate_llvm_ir, verify_llvm_ir, compile_llvm_ir_to_lib, cleanup_llvm_ir,
    extract_llvm_function, reintegrate_llvm_function,
    validate_llvm_ir_with_assembler, llvm_ir_defines_symbol, IrOperationResult,
)
from llmo.metadata import get_run_metadata, get_file_sha256
from llmo.reporting import normalized_timing


def write_target_summary(path: Path, metadata: Dict[str, Any], pipeline_start: float) -> None:
    pipeline_seconds = time.perf_counter() - pipeline_start
    metadata["timing"] = normalized_timing(
        metadata.get("optimization_inference_seconds", 0),
        metadata.get("repair_inference_seconds", 0),
        pipeline_seconds,
    )
    write_json_atomic(path, metadata)


def write_run_attempt_summary(run_dir: Path) -> None:
    """Write a compact, queryable outcome table for IR context experiments."""
    attempts = []
    for path in sorted(run_dir.glob("*/*/summary.json")):
        try:
            summary = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        status = summary.get("status")
        outcome = status
        backend = summary.get("backend_results", {})
        comparisons = [item.get("comparison") for item in backend.values() if item.get("comparison")]
        if any(item.get("status") == "benchmark_incomplete" for item in backend.values()):
            outcome = "benchmark_incomplete"
        elif status in {"failed", "completed_with_errors"} and not comparisons:
            outcome = "benchmark_failed"
        elif status in {"completed", "completed_with_errors"}:
            outcome = "improved" if any(c.get("classification") == "improved" for c in comparisons) else "valid_not_improved"
        attempts.append({
            "model_id": summary.get("model_id"),
            "benchmark_name": summary.get("benchmark_name"),
            "mode": summary.get("optimization_mode", "ir"),
            "status": status,
            "outcome": outcome,
            "original_ir_bytes": summary.get("original_ir_bytes"),
            "extracted_ir_bytes": summary.get("extracted_ir_bytes"),
            "original_estimated_input_tokens": summary.get("original_estimated_input_tokens"),
            "extracted_estimated_input_tokens": summary.get("extracted_estimated_input_tokens"),
            "model_context_size": summary.get("model_context_size"),
            "estimated_prompt_tokens": summary.get("estimated_prompt_tokens"),
            "estimated_available_output_tokens": summary.get("estimated_available_output_tokens"),
        })
    counts: Dict[str, int] = {}
    for attempt in attempts:
        counts[attempt["outcome"]] = counts.get(attempt["outcome"], 0) + 1
    write_json_atomic(run_dir / "attempt_summary.json", {"attempts": attempts, "outcome_counts": counts})


def publish_ir_backend_artifact(
    output_root: Path,
    run_id: str,
    artifact_id: str,
    *,
    model_id: str,
    benchmark_name: str,
    pipeline_id: str,
    role: str,
    library_path: Path,
    ir_path: Path,
    comparison: Optional[Dict[str, Any]] = None,
    timing: Optional[Dict[str, float]] = None,
    experiment_type: str = "llm-ir",
) -> Path:
    """Publish one canonical, independently discoverable IR artifact."""
    artifact_dir = get_standard_path(output_root, experiment_type, run_id, artifact_id)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    canonical_lib = artifact_dir / "libSUT.so"
    canonical_ir = artifact_dir / ("input.ll" if role == "baseline" else "optimized.ll")
    shutil.copy2(library_path, canonical_lib)
    shutil.copy2(ir_path, canonical_ir)
    metadata = {
        "schema_version": 2,
        "artifact_id": artifact_id,
        "run_id": run_id,
        "experiment_type": experiment_type,
        "model_id": model_id,
        "benchmark_name": benchmark_name,
        "pipeline_id": pipeline_id,
        "logical_artifact_id": make_logical_artifact_id(
            experiment_type, run_id, artifact_id, benchmark_name, model_id, pipeline_id
        ),
        "artifact_role": role,
        "is_final_artifact": True,
        "paths": {
            "canonical_libsut": str(canonical_lib),
            "libsut": str(canonical_lib),
            "ir": str(canonical_ir),
        },
    }
    if comparison is not None:
        metadata["comparison"] = comparison
    if timing is not None:
        metadata["timing"] = timing
    write_json_atomic(artifact_dir / "artifact.json", metadata)
    return artifact_dir


def make_ir_optimization_prompt(ir_module: str, extracted: bool = False) -> str:
    reduced_context = "" if not extracted else """
This is a reduced module produced by llvm-extract. It contains the target
function and only the declarations/module infrastructure LLVM retained.
Dependency functions may intentionally be declarations. Do not invent their
implementations merely because their bodies are absent. Optimize the target
function, preserve required declarations/types/globals, and return the complete
valid reduced module rather than a patch or function fragment.
"""
    return f"""You are an expert LLVM IR performance engineer.
Task: optimize the following LLVM IR module for maximum runtime performance.
{reduced_context}

Only rewrite the module when you identify a concrete optimization that is
unlikely to be recovered automatically by LLVM -O3. If no such safe
transformation exists, return the original module unchanged.

Prioritize:
1. Algorithmic improvements.
2. Better data structures.
3. Reduced allocation or copying.
4. Removal of unnecessary library/runtime work.
5. Safe specialization based only on guaranteed semantics.
6. Only then low-level loop or SSA transformations.

De-emphasize transformations LLVM already performs reliably, such as:
- ordinary common-subexpression elimination
- routine branch simplification
- basic dead-code elimination
- trivial inlining
- simple loop cleanup

Warning: Do not manually expand standard-library implementations or replace concise library calls with larger hand-written IR unless there is a concrete algorithmic or allocation advantage.

Environment:
- LLVM/Clang version 20.1.8
- Input generated from C++ at -O1
- x86-64 target
- The target triple and datalayout must remain unchanged
- The exported ABI must remain unchanged

Hard requirements:
- Return one complete raw LLVM IR module.
- No Markdown, explanation, notes, or code fences.
- No prose before or after the module.

Input IR:
{ir_module}
"""

def make_ir_repair_prompt(invalid_ir: str, errors: str) -> str:
    return f"""You are an expert LLVM IR performance engineer.
The following LLVM IR module is invalid according to the LLVM verifier.

Task: repair the validity of the module.
- Repair validity only.
- Preserve the intended transformation and external ABI.
- Return one complete raw LLVM module with no Markdown or explanation.

LLVM version: 20.1.8

Verifier error output:
{errors}

Invalid IR:
{invalid_ir}
"""


def require_preserved_target_configuration(
    validation: ValidationResult, candidate_ir: str, input_ir: str
) -> None:
    """Reject target configuration changes before invoking LLVM tooling."""
    for directive in ("target triple", "target datalayout"):
        pattern = rf'^\s*{re.escape(directive)}\s*=\s*"[^"]*"\s*$'
        expected = re.search(pattern, input_ir, re.MULTILINE)
        actual = re.search(pattern, candidate_ir, re.MULTILINE)
        if expected and actual and expected.group(0).strip() != actual.group(0).strip():
            validation.errors.append(f"Changed required {directive}")
    if validation.errors:
        validation.preflight_passed = False


def is_terminal_summary(summary: Dict[str, Any], requested_backend_levels: List[str]) -> bool:
    terminal_statuses = {
        "completed", "context_insufficient", "response_truncated", 
        "module_extraction_failed", "invalid_after_repair", "preflight_failed", "response_empty",
        "repair_unchanged_invalid", "repair_context_insufficient", "repair_response_truncated",
        "repair_module_extraction_failed", "repair_preflight_failed",
        "extraction_failed", "extraction_target_missing", "extracted_ir_invalid",
        "ir_reintegration_failed",
    }
    status = summary.get("status")
    if status not in terminal_statuses:
        return False
    
    if status == "completed":
        backend_results = summary.get("backend_results", {})
        for lvl in requested_backend_levels:
            if lvl not in backend_results:
                return False
            # If it's a success, it must have stats or a specific error
            res = backend_results[lvl]
            if "error" not in res and "comparison" not in res:
                return False
    return True


def main():
    parser = argparse.ArgumentParser(description="LLVM IR optimization using LLM.")
    parser.add_argument("--model", action="append", help="Run only for these models.")
    parser.add_argument("--only", action="append", help="Optimize only this target function.")
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "results", help="Output directory.")
    parser.add_argument("--resume", action="store_true", help="Resume an interrupted run.")
    parser.add_argument("--seed", type=int, default=LLM_SEED, help="Random seed.")
    parser.add_argument("--backend-opt-level", choices=["O0", "-O0", "O3", "-O3", "both"], default="both", help="Backend optimization level.")
    parser.add_argument("--prompt-ir-cleanup", action="store_true", help="Clean up dead prototypes/DCE before prompting.")
    parser.add_argument("--benchmark-repetitions", type=int, default=3, help="Number of benchmark repetitions.")
    parser.add_argument("--noise-threshold-percent", type=float, default=2.0, help="Noise threshold for performance classification.")
    parser.add_argument("--full-regression-threshold-percent", type=float, default=2.0, help="Minimum improvement to run full regression check.")
    parser.add_argument("--full-regression-check", action="store_true", help="Always run full regression check.")
    parser.add_argument("--run-id", help="Explicit run ID (timestamp used if omitted).")
    parser.add_argument("--max-output-tokens", type=int, default=16384, help="Maximum completion tokens for optimization.")
    parser.add_argument("--mode", choices=["ir", "extracted-ir"], default="ir",
                        help="Prompt with the full module (ir) or an llvm-extract reduced module.")
    parser.add_argument("--ir-extract-recursive", action="store_true",
                        help="Include recursively called definitions in extracted-ir (off by default).")
    args = parser.parse_args()

    run_id = make_run_id(args.run_id)
    experiment_type = "llm-ir" if args.mode == "ir" else "extracted-ir"

    if args.mode == "extracted-ir":
        missing_tools = [tool for tool in (LLVM_AS_TOOL, LLVM_OPT_TOOL, LLVM_EXTRACT_TOOL, LLVM_LINK_TOOL)
                         if shutil.which(tool) is None]
        if missing_tools:
            print("Error: extracted-ir requires missing LLVM tool(s): " + ", ".join(missing_tools))
            return 2
    
    protocol = BenchmarkProtocol(
        repetitions=args.benchmark_repetitions,
        seed=args.seed,
        noise_threshold_percent=args.noise_threshold_percent,
        ordering="paired"
    )

    run_dir = get_standard_path(args.output_root, experiment_type, run_id)
    if args.run_id and run_dir.exists() and not args.resume:
         print(f"Error: Run ID '{args.run_id}' already exists. Use --resume to continue or choose a different ID.")
         return 1

    run_dir.mkdir(parents=True, exist_ok=True)
    
    run_meta = get_run_metadata()
    run_meta.update({
        "run_id": run_id,
        "experiment_type": experiment_type,
        "benchmark_protocol": asdict(protocol),
        "args": vars(args)
    })
    write_json_atomic(run_dir / "run.json", run_meta)

    targets = llm_target_source_files()
    if args.only:
        targets = [t for t in targets if t.stem in args.only]
        
    models_configs = [LlmModelConfig(**m) for m in LLM_MODELS]
    if args.model:
        models_configs = [m for m in models_configs if m.name in args.model or m.alias in args.model]
        
    backend_levels = []
    if args.backend_opt_level == "both":
        backend_levels = ["-O0", "-O3"]
    else:
        lvl = args.backend_opt_level if args.backend_opt_level.startswith("-") else "-" + args.backend_opt_level
        backend_levels = [lvl]

    for model in models_configs:
        model_name = model.alias or model.name
        model_id = sanitize_identifier(model.name)
        model_run_dir = run_dir / model_id
        model_run_dir.mkdir(parents=True, exist_ok=True)
        
        server_process = None
        try:
            server_process, server_command = start_llama_server(model, model_run_dir)
            wait_for_llama_ready(server_process, model_run_dir)
            warm_up_llm(model_name, model_run_dir)
            
            run_meta.setdefault("models", {})[model_name] = {
                "model_name": model.name,
                "alias": model.alias,
                "hf_repo": model.hf_repo,
                "llama_server_command": server_command,
                "effective_context_size": llama.EFFECTIVE_LLAMA_CTX_SIZE,
            }
            write_json_atomic(run_dir / "run.json", run_meta)
            
            for target_source in targets:
                task_start_time = time.perf_counter()
                target_dir = model_run_dir / sanitize_name(target_source.name)
                if args.resume and (target_dir / "summary.json").exists():
                    try:
                        existing_summary = json.loads((target_dir / "summary.json").read_text())
                        if is_terminal_summary(existing_summary, backend_levels):
                            print(f"Skipping {target_source.name} for {model_name} (already completed)")
                            continue
                    except Exception:
                        pass
                
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # 1. Generate Input IR
                input_ir_res = generate_llvm_ir(target_dir, target_source)
                if not input_ir_res.output_path:
                    print(f"  Error generating IR for {target_source.name}")
                    write_target_summary(target_dir / "summary.json", {"status": "input_ir_generation_failed", "error": input_ir_res.command_result.stderr_file}, task_start_time)
                    continue
                
                input_ir_path = input_ir_res.output_path
                
                prompt_ir_path = input_ir_path
                if args.prompt_ir_cleanup:
                    cleanup_res = cleanup_llvm_ir(target_dir / "cleanup", input_ir_path)
                    if cleanup_res.output_path:
                        prompt_ir_path = cleanup_res.output_path
                    else:
                        print(f"  Error cleaning up IR for {target_source.name}")
                        write_target_summary(target_dir / "summary.json", {"status": "prompt_ir_cleanup_failed", "error": cleanup_res.command_result.stderr_file}, task_start_time)
                        continue
                
                original_ir_path = prompt_ir_path
                target_symbol = source_function_name(target_source)
                original_ir_content = original_ir_path.read_text(encoding="utf-8")
                original_ir_tokens = count_tokens(original_ir_content)

                if args.mode == "extracted-ir":
                    if not llvm_ir_defines_symbol(original_ir_path, target_symbol):
                        write_target_summary(target_dir / "summary.json", {
                            "run_id": run_id, "experiment_type": experiment_type,
                            "model_id": model_id, "benchmark_name": target_source.stem,
                            "target_llvm_symbol": target_symbol,
                            "status": "extraction_target_missing",
                        }, task_start_time)
                        continue
                    extraction_res = extract_llvm_function(
                        target_dir / "input_extraction", original_ir_path, target_symbol,
                        recursive=args.ir_extract_recursive,
                    )
                    if not extraction_res.output_path:
                        write_target_summary(target_dir / "summary.json", {
                            "run_id": run_id, "experiment_type": experiment_type,
                            "model_id": model_id, "benchmark_name": target_source.stem,
                            "target_llvm_symbol": target_symbol, "status": "extraction_failed",
                            "extraction_diagnostic": asdict(extraction_res.command_result),
                        }, task_start_time)
                        continue
                    prompt_ir_path = extraction_res.output_path
                    extracted_validation = validate_llvm_ir_with_assembler(
                        target_dir / "input_extraction" / "validation", prompt_ir_path
                    )
                    if not extracted_validation.output_path:
                        write_target_summary(target_dir / "summary.json", {
                            "run_id": run_id, "experiment_type": experiment_type,
                            "model_id": model_id, "benchmark_name": target_source.stem,
                            "target_llvm_symbol": target_symbol, "status": "extracted_ir_invalid",
                            "extracted_validation_diagnostic": asdict(extracted_validation.command_result),
                        }, task_start_time)
                        continue

                ir_content = prompt_ir_path.read_text(encoding="utf-8")
                
                # 2. Token Budgeting
                input_tokens = count_tokens(ir_content)
                min_output_tokens = max(4096, int(input_tokens * 0.8))
                
                prompt = make_ir_optimization_prompt(ir_content, extracted=args.mode == "extracted-ir")
                system_prompt = "You are a compiler and LLVM IR optimization assistant. Return only the requested IR module."
                
                budget = calculate_token_budget(prompt, system_prompt, args.max_output_tokens, minimum_expected_output_tokens=min_output_tokens)
                
                target_meta = {
                    "run_id": run_id,
                    "experiment_type": experiment_type,
                    "model_id": model_id,
                    "benchmark_name": target_source.stem,
                    "input_file": str(target_source),
                    "input_sha256": get_file_sha256(target_source),
                    "input_ir_sha256": get_file_sha256(prompt_ir_path),
                    "prompt_sha256": sha256_sum(prompt),
                    "token_budget": asdict(budget),
                    "min_output_tokens": min_output_tokens,
                    "configured_max_output_tokens": args.max_output_tokens
                }
                target_meta.update({
                    "optimization_mode": args.mode,
                    "target_llvm_symbol": target_symbol,
                    "original_ir_path": str(original_ir_path),
                    "prompt_ir_path": str(prompt_ir_path),
                    "original_ir_bytes": len(original_ir_content.encode("utf-8")),
                    "extracted_ir_bytes": len(ir_content.encode("utf-8")) if args.mode == "extracted-ir" else None,
                    "original_estimated_input_tokens": original_ir_tokens,
                    "extracted_estimated_input_tokens": input_tokens if args.mode == "extracted-ir" else None,
                    "model_context_size": llama.EFFECTIVE_LLAMA_CTX_SIZE,
                    "estimated_prompt_tokens": budget.prompt_tokens,
                    "estimated_available_output_tokens": budget.available_output_tokens,
                    "ir_extract_recursive": args.ir_extract_recursive,
                })
                if args.mode == "extracted-ir":
                    target_meta.update({
                        "original_ir_sha256": get_file_sha256(original_ir_path),
                        "extracted_ir_sha256": get_file_sha256(prompt_ir_path),
                    })
                
                if not budget.can_fit_minimum_expected_output:
                    print(f"  Skipping {target_source.name}: insufficient context ({budget.available_output_tokens} < {min_output_tokens})")
                    target_meta["status"] = "context_insufficient"
                    write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                    continue
                
                # 3. LLM Call
                print(f"Optimizing {target_source.name} IR with {model_name}...")
                requested_max = min(args.max_output_tokens, budget.available_output_tokens)
                
                validation_state = {
                    "response_received": False,
                    "response_complete": False,
                    "module_extracted": False,
                    "preflight_passed": False,
                    "initial_verification_passed": False,
                    "repair_attempted": False,
                    "repair_response_received": False,
                    "repair_response_complete": False,
                    "repair_module_extracted": False,
                    "repair_preflight_passed": False,
                    "repair_verification_passed": False,
                }
                
                llm_call_start = time.perf_counter()
                llm_result = call_llm(model_name, prompt, system_prompt, max_tokens=requested_max, seed=args.seed)
                llm_call_duration = time.perf_counter() - llm_call_start
                
                validation_state["response_received"] = True
                if llm_result.finish_reason != "length":
                    validation_state["response_complete"] = True

                resp_file = save_llm_call(target_dir, "optimization", llm_result)
                target_meta["raw_response_file"] = resp_file
                target_meta["raw_response_sha256"] = sha256_sum(llm_result.content)
                target_meta["llm_result"] = {
                    "finish_reason": llm_result.finish_reason,
                    "prompt_tokens": llm_result.prompt_tokens,
                    "completion_tokens": llm_result.completion_tokens,
                    "total_tokens": llm_result.total_tokens,
                    "requested_max_tokens": requested_max,
                    "request_started_at": datetime.fromtimestamp(time.time() - llm_call_duration).isoformat(),
                    "request_finished_at": datetime.now().isoformat(),
                    "duration_seconds": llm_call_duration
                }
                target_meta["optimization_inference_seconds"] = llm_call_duration
                
                if llm_result.finish_reason == "length":
                    print(f"  Truncated response for {target_source.name}")
                    target_meta["status"] = "response_truncated"
                    target_meta["validation"] = validation_state
                    write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                    continue
                
                # 4. Extraction & Validation
                extracted_ir = extract_code_block(llm_result.content)
                if not extracted_ir.strip():
                    target_meta["status"] = "response_empty"
                    target_meta["validation"] = validation_state
                    write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                    continue
                
                validation_state["module_extracted"] = True
                extracted_ir_path = target_dir / "extracted.ll"
                extracted_ir_path.write_text(extracted_ir, encoding="utf-8")
                initial_ir_sha256 = get_file_sha256(extracted_ir_path)
                target_meta["extracted_module_sha256"] = initial_ir_sha256
                
                val_res = validate_llvm_ir_module(extracted_ir, target_source.stem, raw_response=llm_result.content)
                if args.mode == "extracted-ir":
                    require_preserved_target_configuration(val_res, extracted_ir, ir_content)
                if val_res.preflight_passed:
                    validation_state["preflight_passed"] = True

                target_meta["preflight_validation"] = {
                    "preflight_passed": val_res.preflight_passed,
                    "errors": val_res.errors,
                }
                
                optimized_ir_path = target_dir / "optimized.ll"
                
                status = "unknown"
                if validation_state["preflight_passed"]:
                    if args.mode == "extracted-ir":
                        verify_res = validate_llvm_ir_with_assembler(
                            target_dir / "verify", extracted_ir_path
                        ).command_result
                    else:
                        verify_res = verify_llvm_ir(target_dir / "verify", extracted_ir_path)
                    target_meta["verify_first_attempt"] = asdict(verify_res)
                    target_meta["initial_verifier_stderr_path"] = verify_res.stderr_file
                    
                    if verify_res.returncode == 0:
                        validation_state["initial_verification_passed"] = True
                        status = "valid_on_first_attempt"
                        shutil.copy2(extracted_ir_path, optimized_ir_path)
                    else:
                        # 5. Repair Attempt
                        validation_state["repair_attempted"] = True
                        print(f"  IR invalid. Attempting repair...")
                        err_text = Path(verify_res.stderr_file).read_text(encoding="utf-8")
                        target_meta["initial_verifier_error_excerpt"] = err_text[:1000]
                        repair_prompt = make_ir_repair_prompt(extracted_ir, err_text)
                        
                        repair_budget = calculate_token_budget(repair_prompt, system_prompt, args.max_output_tokens, minimum_expected_output_tokens=min_output_tokens)
                        target_meta["repair_token_budget"] = asdict(repair_budget)
                        
                        if not repair_budget.can_fit_minimum_expected_output:
                            status = "repair_context_insufficient"
                        else:
                            repair_llm_start = time.perf_counter()
                            repair_requested_max = min(args.max_output_tokens, repair_budget.available_output_tokens)
                            repair_result = call_llm(model_name, repair_prompt, system_prompt, max_tokens=repair_requested_max, seed=args.seed)
                            repair_llm_duration = time.perf_counter() - repair_llm_start
                            
                            validation_state["repair_response_received"] = True
                            if repair_result.finish_reason != "length":
                                validation_state["repair_response_complete"] = True

                            repair_resp_file = save_llm_call(target_dir, "repair", repair_result)
                            target_meta["repair_raw_response_file"] = repair_resp_file
                            target_meta["repair_result"] = {
                                "finish_reason": repair_result.finish_reason,
                                "prompt_tokens": repair_result.prompt_tokens,
                                "completion_tokens": repair_result.completion_tokens,
                                "total_tokens": repair_result.total_tokens,
                                "requested_max_tokens": repair_requested_max,
                                "request_started_at": datetime.fromtimestamp(time.time() - repair_llm_duration).isoformat(),
                                "request_finished_at": datetime.now().isoformat(),
                                "duration_seconds": repair_llm_duration
                            }
                            target_meta["repair_inference_seconds"] = repair_llm_duration
                            target_meta["repair_response_sha256"] = sha256_sum(repair_result.content)
                            
                            if repair_result.finish_reason == "length":
                                status = "repair_response_truncated"
                            else:
                                repaired_ir = extract_code_block(repair_result.content)
                                if not repaired_ir.strip():
                                    status = "repair_module_extraction_failed"
                                else:
                                    validation_state["repair_module_extracted"] = True
                                    repaired_ir_path = target_dir / "repaired.ll"
                                    repaired_ir_path.write_text(repaired_ir, encoding="utf-8")
                                    repair_ir_sha256 = get_file_sha256(repaired_ir_path)
                                    target_meta["repair_module_sha256"] = repair_ir_sha256
                                    
                                    repair_val = validate_llvm_ir_module(repaired_ir, target_source.stem, raw_response=repair_result.content)
                                    if args.mode == "extracted-ir":
                                        require_preserved_target_configuration(repair_val, repaired_ir, ir_content)
                                    if repair_val.preflight_passed:
                                        validation_state["repair_preflight_passed"] = True
                                        
                                        if args.mode == "extracted-ir":
                                            repair_verify = validate_llvm_ir_with_assembler(
                                                target_dir / "repair_verify", repaired_ir_path
                                            ).command_result
                                        else:
                                            repair_verify = verify_llvm_ir(target_dir / "repair_verify", repaired_ir_path)
                                        target_meta["verify_repair_attempt"] = asdict(repair_verify)
                                        target_meta["repair_verifier_stderr_path"] = repair_verify.stderr_file
                                        
                                        if repair_verify.returncode == 0:
                                            validation_state["repair_verification_passed"] = True
                                            status = "valid_after_repair"
                                            shutil.copy2(repaired_ir_path, optimized_ir_path)
                                        else:
                                            repair_err_text = Path(repair_verify.stderr_file).read_text(encoding="utf-8")
                                            target_meta["repair_verifier_error_excerpt"] = repair_err_text[:1000]
                                            
                                            if repair_ir_sha256 == initial_ir_sha256:
                                                status = "repair_unchanged_invalid"
                                                target_meta["repair_module_changed"] = False
                                            else:
                                                status = "invalid_after_repair"
                                                target_meta["repair_module_changed"] = True
                                    else:
                                        status = "repair_preflight_failed"
                else:
                    if not validation_state["module_extracted"]:
                        status = "module_extraction_failed"
                    else:
                        status = "preflight_failed"
                
                target_meta["status"] = status
                target_meta["validation"] = validation_state
                
                # 6. Backend & Benchmarking
                if status in ["valid_on_first_attempt", "valid_after_repair"]:
                    benchmark_ir_path = optimized_ir_path
                    if args.mode == "extracted-ir":
                        target_meta["optimized_extracted_ir_sha256"] = get_file_sha256(optimized_ir_path)
                        reintegration = reintegrate_llvm_function(
                            target_dir / "reintegration", original_ir_path,
                            optimized_ir_path, target_symbol,
                        )
                        target_meta["reintegration_diagnostic"] = asdict(reintegration.command_result)
                        if not reintegration.output_path:
                            target_meta["status"] = "ir_reintegration_failed"
                            target_meta["total_inference_seconds"] = target_meta.get("optimization_inference_seconds", 0) + target_meta.get("repair_inference_seconds", 0)
                            write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                            continue
                        benchmark_ir_path = reintegration.output_path
                        target_meta["reconstructed_ir_path"] = str(benchmark_ir_path)
                        target_meta["reconstructed_ir_sha256"] = get_file_sha256(benchmark_ir_path)
                    other_sources = other_sources_for_replacement(target_source.name)
                    
                    backend_results = {}
                    for opt_level in backend_levels:
                        print(f"  Benchmarking with {opt_level}...")
                        pipeline_prefix = "extracted-ir-o1" if args.mode == "extracted-ir" else "ir-o1"
                        pipeline_id = f"{pipeline_prefix}__backend-{sanitize_name(opt_level)}"
                        level_dir = target_dir / f"backend_{sanitize_name(opt_level)}"
                        
                        # Artifact IDs
                        base_aid = make_artifact_id(experiment_type, target_source.stem, model_id, pipeline_id=pipeline_id, suffix="baseline")
                        cand_aid = make_artifact_id(experiment_type, target_source.stem, model_id, pipeline_id=pipeline_id, suffix="candidate")

                        # Baseline build
                        baseline_build_dir = level_dir / "baseline"
                        baseline_comp = compile_llvm_ir_to_lib(baseline_build_dir, original_ir_path, other_sources, opt_level=opt_level)
                        
                        # Candidate build
                        candidate_build_dir = level_dir / "candidate"
                        candidate_comp = compile_llvm_ir_to_lib(candidate_build_dir, benchmark_ir_path, other_sources, opt_level=opt_level)
                        
                        if baseline_comp.output_path and candidate_comp.output_path:
                            # ABI Check
                            baseline_abi_cmd = run_abi_symbol_check(baseline_build_dir, baseline_comp.output_path)
                            candidate_abi_cmd = run_abi_symbol_check(candidate_build_dir, candidate_comp.output_path)
                            
                            baseline_abi_outcome = load_abi_check_outcome(baseline_build_dir, baseline_abi_cmd)
                            candidate_abi_outcome = load_abi_check_outcome(candidate_build_dir, candidate_abi_cmd)
                            
                            if baseline_abi_outcome.success and candidate_abi_outcome.success:
                                comparison = run_benchmarks_paired(
                                    candidate_comp.output_path, baseline_comp.output_path, target_source.stem, 
                                    protocol=protocol,
                                    candidate_id=cand_aid,
                                    baseline_id=base_aid
                                )
                                
                                comparison_dict = asdict(comparison)
                                artifact_timing = normalized_timing(
                                    target_meta.get("optimization_inference_seconds", 0),
                                    target_meta.get("repair_inference_seconds", 0),
                                    time.perf_counter() - task_start_time,
                                )
                                publish_ir_backend_artifact(
                                    args.output_root, run_id, base_aid,
                                    model_id=model_id,
                                    benchmark_name=target_source.stem,
                                    pipeline_id=pipeline_id,
                                    role="baseline",
                                    library_path=baseline_comp.output_path,
                                    ir_path=original_ir_path,
                                    comparison=comparison_dict,
                                    timing=normalized_timing(),
                                    experiment_type=experiment_type,
                                )
                                publish_ir_backend_artifact(
                                    args.output_root, run_id, cand_aid,
                                    model_id=model_id,
                                    benchmark_name=target_source.stem,
                                    pipeline_id=pipeline_id,
                                    role="candidate",
                                    library_path=candidate_comp.output_path,
                                    ir_path=benchmark_ir_path,
                                    comparison=comparison_dict,
                                    timing=artifact_timing,
                                    experiment_type=experiment_type,
                                )
                                backend_results[opt_level] = {
                                    "baseline_artifact_id": base_aid,
                                    "artifact_id": cand_aid,
                                    "pipeline_id": pipeline_id,
                                    "comparison": comparison_dict,
                                }
                                
                                if comparison.classification == "benchmark_incomplete":
                                    backend_results[opt_level]["status"] = "benchmark_incomplete"
                                
                                # Regression check
                                if comparison.relative_change_percent and (args.full_regression_check or comparison.relative_change_percent > args.full_regression_threshold_percent):
                                    print(f"  Running full regression check...")
                                    full_res = run_benchmarks_for_lib(candidate_build_dir, candidate_comp.output_path, run_all=True)
                                    backend_results[opt_level]["full_regression_measurements"] = [asdict(m) for m in full_res]
                            else:
                                backend_results[opt_level] = {
                                    "error": "abi_check_failed",
                                    "baseline_abi_ok": baseline_abi_outcome.success,
                                    "candidate_abi_ok": candidate_abi_outcome.success,
                                    "baseline_abi_error": baseline_abi_outcome.error,
                                    "candidate_abi_error": candidate_abi_outcome.error,
                                    "baseline_abi_res": asdict(baseline_abi_outcome.command_result),
                                    "candidate_abi_res": asdict(candidate_abi_outcome.command_result)
                                }
                        else:
                            backend_results[opt_level] = {
                                "error": "compilation_failed",
                                "baseline_comp": asdict(baseline_comp.command_result),
                                "candidate_comp": asdict(candidate_comp.command_result)
                            }
                    
                    target_meta["backend_results"] = backend_results
                    if any(res.get("error") for res in backend_results.values()):
                         if not any("comparison" in res for res in backend_results.values()):
                             target_meta["status"] = "failed"
                         else:
                             target_meta["status"] = "completed_with_errors"
                    else:
                        target_meta["status"] = "completed"
                
                target_meta["total_inference_seconds"] = target_meta.get("optimization_inference_seconds", 0) + target_meta.get("repair_inference_seconds", 0)
                target_meta["total_task_seconds"] = time.perf_counter() - task_start_time
                target_meta["timing"] = normalized_timing(
                    target_meta.get("optimization_inference_seconds", 0),
                    target_meta.get("repair_inference_seconds", 0),
                    target_meta["total_task_seconds"],
                )
                for backend_result in target_meta.get("backend_results", {}).values():
                    candidate_id = backend_result.get("artifact_id")
                    if not candidate_id:
                        continue
                    artifact_json = get_standard_path(args.output_root, experiment_type, run_id, candidate_id) / "artifact.json"
                    if artifact_json.exists():
                        artifact_metadata = json.loads(artifact_json.read_text(encoding="utf-8"))
                        artifact_metadata["timing"] = target_meta["timing"]
                        write_json_atomic(artifact_json, artifact_metadata)
                write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                

        finally:
            stop_process(server_process)

    write_run_attempt_summary(run_dir)

if __name__ == "__main__":
    main()
