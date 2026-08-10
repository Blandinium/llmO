#!/usr/bin/env python3

import argparse
import sys
import time
import shutil
import json
import random
import platform
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import asdict, replace

from llmo.config import *
from llmo.command import sanitize_name, write_json, write_json_atomic, sha256_sum, CommandResult
from llmo.project import llm_target_source_files, other_sources_for_replacement, source_function_name
from llmo.source import extract_code_block, contains_target_function_definition, read_support_headers
from llmo.abi import run_abi_symbol_check, load_abi_check_outcome
from llmo.benchmark import run_benchmarks_for_lib, run_benchmarks_paired
from llmo.benchmark_protocol import BenchmarkProtocol, BenchmarkMeasurement, calculate_benchmark_statistics, compare_benchmarks
from llmo.naming import make_run_id, make_artifact_id, make_logical_artifact_id, get_standard_path, sanitize_identifier
from llmo import llama
from llmo.llama import (
    LlmModelConfig, start_llama_server, stop_process, 
    wait_for_llama_ready, call_llm, warm_up_llm, calculate_token_budget, count_tokens, ChatCompletionResult, save_llm_call
)
from llmo.build import find_libsut, compile_replacement_artifact_for_check, CompileResult
from llmo.metadata import get_run_metadata, get_file_sha256
from llmo.reporting import confirmation_fields, normalized_timing


def write_target_summary(path: Path, metadata: Dict[str, Any], pipeline_start: float) -> None:
    """Persist a summary with normalized timing, including failure exits."""
    pipeline_seconds = time.perf_counter() - pipeline_start
    metadata["timing"] = normalized_timing(
        metadata.get("optimization_inference_seconds", 0),
        metadata.get("repair_inference_seconds", 0),
        pipeline_seconds,
    )
    write_json_atomic(path, metadata)

def make_naive_cpp_optimization_prompt(target_name: str, headers: str, source: str) -> str:
    return f"""You are an expert C++23 performance engineer.
Task: optimize the C++ function {target_name} for maximum runtime performance.

Only rewrite the function when you identify a concrete optimization that is
unlikely to be recovered automatically by Clang -O3. If no such safe
transformation exists, return the original function unchanged.

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
"""

def is_terminal_summary(summary: Dict[str, Any]) -> bool:
    terminal_statuses = {
        "completed", "baseline_compile_failed", "baseline_abi_failed", 
        "baseline_benchmark_failed", "response_truncated", 
        "source_extraction_failed", "candidate_compile_failed", 
        "candidate_abi_failed", "candidate_benchmark_failed", "preflight_failed"
    }
    return summary.get("status") in terminal_statuses

def main():
    parser = argparse.ArgumentParser(description="Naïve C++ optimization using LLM.")
    parser.add_argument("--model", action="append", help="Run only for these models.")
    parser.add_argument("--only", action="append", help="Optimize only this target function.")
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "results", help="Output directory.")
    parser.add_argument("--resume", action="store_true", help="Resume an interrupted run.")
    parser.add_argument("--seed", type=int, default=LLM_SEED, help="Random seed.")
    parser.add_argument("--benchmark-repetitions", type=int, default=3, help="Number of benchmark repetitions.")
    parser.add_argument("--noise-threshold-percent", type=float, default=2.0, help="Noise threshold for performance classification.")
    parser.add_argument("--full-regression-threshold-percent", type=float, default=2.0, help="Minimum improvement to run full regression check.")
    parser.add_argument("--full-regression-check", action="store_true", help="Always run full regression check.")
    parser.add_argument("--run-id", help="Explicit run ID (timestamp used if omitted).")
    args = parser.parse_args()

    run_id = make_run_id(args.run_id)
    experiment_type = "naive-cpp"
    
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
        
    headers = read_support_headers()
    
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
            
            for target in targets:
                task_start_time = time.perf_counter()
                target_dir = model_run_dir / sanitize_name(target.name)
                if args.resume and (target_dir / "summary.json").exists():
                    try:
                        existing_summary = json.loads((target_dir / "summary.json").read_text())
                        if is_terminal_summary(existing_summary):
                            print(f"Skipping {target.name} for {model_name} (already completed)")
                            continue
                    except Exception:
                        pass
                
                target_dir.mkdir(parents=True, exist_ok=True)
                source_content = target.read_text(encoding="utf-8")
                prompt = make_naive_cpp_optimization_prompt(target.stem, headers, source_content)
                (target_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
                
                # Artifact ID
                base_aid = make_artifact_id(experiment_type, target.stem, model_id, suffix="baseline")
                cand_aid = make_artifact_id(experiment_type, target.stem, model_id, suffix="candidate")
                final_aid = make_artifact_id(experiment_type, target.stem, model_id, suffix="final")

                target_meta = {
                    "artifact_id": cand_aid,
                    "run_id": run_id,
                    "experiment_type": experiment_type,
                    "model_id": model_id,
                    "benchmark_name": target.stem,
                    "logical_artifact_id": make_logical_artifact_id(
                        experiment_type, run_id, cand_aid, target.stem, model_id
                    ),
                    "input_file": str(target),
                    "input_sha256": get_file_sha256(target),
                    "prompt_sha256": sha256_sum(prompt),
                    "artifact_role": "candidate",
                    "is_final_artifact": True,
                    **confirmation_fields("not-run", "not-run"),
                }

                print(f"Optimizing {target.name} with {model_name}...")
                
                # 1. Baseline Build
                baseline_dir = target_dir / "baseline"
                baseline_res = compile_replacement_artifact_for_check(
                    baseline_dir, target.name, target, "cpp", CLANG_CXX_COMPILER, 
                    LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL, SUT_DIR, PROJECT_ROOT, 
                    LLM_COMPILE_TIMEOUT_SECONDS, other_sources_for_replacement(target.name)
                )
                
                if not baseline_res.libsut_path:
                    print(f"  Baseline compilation failed for {target.name}")
                    target_meta["status"] = "baseline_compile_failed"
                    write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                    continue
                
                # 2. Baseline ABI Check
                baseline_abi_cmd = run_abi_symbol_check(baseline_dir, baseline_res.libsut_path)
                baseline_abi_outcome = load_abi_check_outcome(baseline_dir, baseline_abi_cmd)
                if not baseline_abi_outcome.success:
                    print(f"  Baseline ABI check failed for {target.name}: {baseline_abi_outcome.error}")
                    target_meta["status"] = "baseline_abi_failed"
                    target_meta["abi_error"] = baseline_abi_outcome.error
                    write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                    continue

                # 3. LLM Call
                llm_call_start = time.perf_counter()
                llm_result = call_llm(model_name, prompt, seed=args.seed)
                llm_call_duration = time.perf_counter() - llm_call_start
                
                resp_file = save_llm_call(target_dir, "optimization", llm_result)
                target_meta["raw_response_file"] = resp_file
                target_meta["raw_response_sha256"] = sha256_sum(llm_result.content)
                target_meta["llm_result"] = {
                    "finish_reason": llm_result.finish_reason,
                    "prompt_tokens": llm_result.prompt_tokens,
                    "completion_tokens": llm_result.completion_tokens,
                    "total_tokens": llm_result.total_tokens,
                    "request_started_at": datetime.fromtimestamp(time.time() - llm_call_duration).isoformat(),
                    "request_finished_at": datetime.now().isoformat(),
                    "duration_seconds": llm_call_duration
                }
                target_meta["optimization_inference_seconds"] = llm_call_duration

                if llm_result.finish_reason == "length":
                    print(f"  Truncated response for {target.name}")
                    target_meta["status"] = "response_truncated"
                    write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                    continue

                # 4. Source Extraction & Preflight
                new_source = extract_code_block(llm_result.content)
                if not new_source.strip():
                    target_meta["status"] = "source_extraction_failed"
                    write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                    continue
                
                if not contains_target_function_definition(new_source, target.name):
                    target_meta["status"] = "preflight_failed"
                    write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                    continue

                optimized_source_file = target_dir / "optimized.cpp"
                optimized_source_file.write_text(new_source, encoding="utf-8")
                
                # 5. Candidate Build
                candidate_dir = target_dir / "candidate"
                candidate_res = compile_replacement_artifact_for_check(
                    candidate_dir, target.name, optimized_source_file, "cpp", CLANG_CXX_COMPILER, 
                    LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL, SUT_DIR, PROJECT_ROOT, 
                    LLM_COMPILE_TIMEOUT_SECONDS, other_sources_for_replacement(target.name)
                )
                
                if not candidate_res.libsut_path:
                    print(f"  Candidate compilation failed for {target.name}")
                    target_meta["status"] = "candidate_compile_failed"
                    write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                    continue
                
                # 6. Candidate ABI Check
                candidate_abi_cmd = run_abi_symbol_check(candidate_dir, candidate_res.libsut_path)
                candidate_abi_outcome = load_abi_check_outcome(candidate_dir, candidate_abi_cmd)
                if not candidate_abi_outcome.success:
                    print(f"  Candidate ABI check failed for {target.name}: {candidate_abi_outcome.error}")
                    target_meta["status"] = "candidate_abi_failed"
                    target_meta["abi_error"] = candidate_abi_outcome.error
                    write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                    continue

                # 7. Selection Benchmarking
                print(f"  Comparing candidate against baseline...")
                comparison = run_benchmarks_paired(
                    candidate_res.libsut_path, baseline_res.libsut_path, target.stem, 
                    protocol=protocol,
                    candidate_id=cand_aid,
                    baseline_id=base_aid
                )
                
                target_meta["selection_comparison"] = asdict(comparison)
                target_meta.update(confirmation_fields(comparison.classification, "not-required"))
                
                if comparison.classification == "benchmark_failed":
                    target_meta["status"] = "candidate_benchmark_failed"
                else:
                    target_meta["status"] = "completed"
                    
                # 8. Final Confirmation Benchmarking
                if comparison.classification == "improved":
                     print(f"  Accepted as improved ({comparison.relative_change_percent:+.1f}%). Performing final confirmation...")
                     # In naive runner, if only one candidate, final is the same as selection but we record it separately
                     # or we could run it again with more reps? The requirement says "fresh final confirmation comparison".
                     # I'll run it again.
                     confirmation_protocol = replace(protocol, seed=protocol.seed + 1)
                     target_meta["confirmation_seed"] = confirmation_protocol.seed
                     final_comparison = run_benchmarks_paired(
                        candidate_res.libsut_path, baseline_res.libsut_path, target.stem, 
                        protocol=confirmation_protocol,
                        candidate_id=final_aid,
                        baseline_id=base_aid
                     )
                     target_meta["final_confirmation"] = asdict(final_comparison)
                     target_meta.update(confirmation_fields(comparison.classification, final_comparison.classification))
                     if target_meta["confirmed_improvement"]:
                         final_dir = get_standard_path(args.output_root, experiment_type, run_id, final_aid)
                         final_dir.mkdir(parents=True, exist_ok=True)
                         shutil.copy2(optimized_source_file, final_dir / "optimized.cpp")
                         shutil.copy2(candidate_res.libsut_path, final_dir / "libSUT.so")
                
                # Full regression check if requested or promising
                if comparison.relative_change_percent and (args.full_regression_check or comparison.relative_change_percent > args.full_regression_threshold_percent):
                    print(f"  Running full regression check...")
                    full_res = run_benchmarks_for_lib(candidate_dir, candidate_res.libsut_path, run_all=True)
                    target_meta["full_regression_measurements"] = [asdict(m) for m in full_res]
                
                target_meta["total_inference_seconds"] = target_meta.get("optimization_inference_seconds", 0)
                target_meta["total_task_seconds"] = time.perf_counter() - task_start_time
                target_meta["timing"] = normalized_timing(
                    target_meta.get("optimization_inference_seconds", 0),
                    0.0,
                    target_meta["total_task_seconds"],
                )
                target_meta["paths"] = {
                    "source": str(optimized_source_file),
                    "libsut": str(candidate_res.libsut_path),
                }
                write_target_summary(target_dir / "summary.json", target_meta, task_start_time)
                
                # Write artifact metadata
                write_json_atomic(target_dir / "artifact.json", target_meta)
                if target_meta.get("confirmed_improvement"):
                    final_meta = {
                        **target_meta,
                        "artifact_id": final_aid,
                        "logical_artifact_id": make_logical_artifact_id(
                            experiment_type, run_id, final_aid, target.stem, model_id
                        ),
                        "artifact_role": "final",
                        "paths": {
                            "source": str(final_dir / "optimized.cpp"),
                            "libsut": str(final_dir / "libSUT.so"),
                        },
                    }
                    write_json_atomic(final_dir / "artifact.json", final_meta)
                
        finally:
            stop_process(server_process)

if __name__ == "__main__":
    main()
