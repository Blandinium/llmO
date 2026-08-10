#!/usr/bin/env python3

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

from llmo.config import *
from llmo.command import CommandResult, run_command, write_json, sanitize_name, write_json_atomic
from llmo.build import BuildVariant, BuildMetadata, DirectBuildMetadata, find_libsut, compile_replacement_artifact_for_check
from llmo.llama import LlmModelConfig, LlmCallResult, start_llama_server, stop_process, wait_for_llama_ready, call_llm, warm_up_llm
from llmo.abi import run_abi_symbol_check, load_abi_check_outcome
from llmo.benchmark import run_benchmarks_for_lib, try_write_benchmark_json, get_randomized_balanced_sequence
from llmo.benchmark_protocol import BenchmarkProtocol, BenchmarkMeasurement, calculate_benchmark_statistics, compare_benchmarks
from llmo.naming import make_run_id, make_artifact_id, make_logical_artifact_id, get_standard_path
from llmo.project import all_sut_cpp_files, llm_target_source_files, other_sources_for_replacement, source_function_name
from llmo.source import extract_code_block, contains_target_function_definition, read_support_headers
from llmo.llvm import generate_llvm_ir, verify_llvm_ir

# =============================================================================
# Configuration
# =============================================================================

LLM_ARTIFACT_ROOT = BUILD_ROOT / "llm-artifacts-split-sources"

# Comma-separated override, for example:
#   LLM_TARGET_FILES=count_matches.cpp,top_words_from_file.cpp ./run_builds_split_sources.py
LLM_TARGET_FILES_ENV = [
    item.strip()
    for item in os.environ.get("LLM_TARGET_FILES", "").split(",")
    if item.strip()
]

RUN_LLM_IR_TASKS = os.environ.get("RUN_LLM_IR_TASKS", "1") != "0"
RUN_LLM_CPP_TASKS = os.environ.get("RUN_LLM_CPP_TASKS", "1") != "0"

# =============================================================================
# Helpers
# =============================================================================

def sanitize_variant_name(opt_flag: str) -> str:
    return sanitize_name(opt_flag)

def configured_llm_models() -> list[LlmModelConfig]:
    return [LlmModelConfig(**item) for item in LLM_MODELS]

# =============================================================================
# LLM prompts
# =============================================================================

def make_cpp_optimization_prompt(target_source: Path) -> str:
    headers = read_support_headers()
    source = target_source.read_text(encoding="utf-8")
    return f"""You are an expert C++23 performance engineer.

Task: optimize only {target_source.name} for runtime performance.

Hard requirements:
- Return one complete replacement for {target_source.name}.
- Preserve the public C ABI exactly as declared in library.h.
- Do not change any exported function name, parameter type, return type, struct layout, ownership rule, or allocation/freeing convention visible in library.h.
- Keep this file focused on its existing exported function. Do not add implementations for unrelated exported functions from library.h.
- You may freely restructure internal helpers in this file.
- You may keep using helpers declared in sut_common.h if useful.
- Preserve observable behavior for all valid inputs expected by the existing API and benchmark runner.
- Preserve the error-handling style: invalid pointer/length combinations and internal exceptions should not escape through extern "C" functions.
- Do not modify library.h or sut_common.h.
- Do not include markdown, commentary, explanations, benchmarking notes, or code fences in your answer.
Headers:
```cpp
{headers}
```

Current {target_source.name}:
```cpp
{source}
```
"""


def make_cpp_compile_fix_prompt(target_source: Path, failed_source: str, compiler_stdout: str, compiler_stderr: str) -> str:
    headers = read_support_headers()
    return f"""You are an expert C++23 build-fix and performance engineer.

Task: fix this optimized {target_source.name} so the whole SUT shared library compiles successfully.

Hard requirements:
- Return one complete replacement for {target_source.name}.
- Preserve the public C ABI exactly as declared in library.h.
- Do not change any exported function name, parameter type, return type, struct layout, ownership rule, or allocation/freeing convention visible in library.h.
- Do not add implementations for unrelated exported functions from library.h.
- Preserve the intended optimized behavior and runtime-performance focus as much as possible.
- Do not modify library.h or sut_common.h.
- Do not include markdown, commentary, explanations, benchmarking notes, or code fences in your answer.
Headers:
```cpp
{headers}
```

Failed {target_source.name}:
```cpp
{failed_source}
```

Compiler stdout:
```text
{compiler_stdout[-12000:]}
```

Compiler stderr:
```text
{compiler_stderr[-12000:]}
```
"""


def make_ir_optimization_prompt(target_source: Path, llvm_ir: str) -> str:
    return f"""You are an LLVM optimization pass focused on runtime performance.

Task:

Rewrite the LLVM IR module below to improve runtime performance on the target described by the module.
The input module has already been processed by LLVM -O1. Seek meaningful improvements beyond cosmetic control-flow cleanup or canonicalization that standard LLVM -O2/-O3 passes are likely to reproduce automatically.

Optimization policy:

Optimize for runtime performance unless the module explicitly provides a different objective.
You may replace function bodies and substantially restructure algorithms, loops, memory access patterns, and control flow.
Consider vectorization, unrolling, loop versioning, specialization, branch reduction, common-subexpression elimination, reduced allocation, improved locality, and algorithmic changes when valid and plausibly profitable.
Use target information, function attributes, metadata, constants, and profile information present in the module.
When no profile information is available, optimize for broadly reasonable performance rather than assuming benchmark-specific input values.
Do not restrict the result to simple or minimally changed IR merely because more substantial transformations are harder to express.
Do not perform transformations whose correctness depends on assumptions not established by LLVM IR semantics, attributes, metadata, or control flow.

Output requirements:

Return exactly one complete LLVM IR module.
Return raw LLVM IR only.
Do not include Markdown, code fences, explanations, notes, or benchmarking text.
The output must be accepted by llvm-as, opt -passes=verify, and clang++.

ABI and module requirements:

Preserve every externally visible function definition in the input module.
Preserve every externally visible function name, signature, linkage, visibility, storage class, and calling convention exactly.
Do not add, remove, rename, or redefine externally visible functions.
Do not define functions that are only declared in the input module.
Preserve target datalayout and target triple.
Preserve externally observable functional behaviour.
Preserve ownership and allocation conventions that are externally observable.
Do not introduce benchmark-specific constants or hard-coded results.

Permitted changes:

You may add private or internal helper functions.
You may add correctly typed LLVM intrinsic declarations.
You may keep external declarations required by the rewritten module.
You may remove unused declarations.
You may add, remove, or update attributes and metadata when justified by the rewritten implementation.
You may remove unused personality functions and exception-handling declarations when no remaining instruction requires them.

IR correctness:

Every SSA value must dominate all uses.
Every PHI node must have one incoming value for each predecessor.
All types must be correct.
Memory accesses must remain valid for every execution allowed by the input IR.
Vectorized or unrolled loops must handle remainders and small sizes correctly.
Exception-handling structures must remain valid where used.

LLVM IR module produced with {LLM_IR_OPTIMIZATION_LEVEL}:
{llvm_ir}
"""

def llm_target_source_files_local() -> list[Path]:
    return llm_target_source_files(LLM_TARGET_FILES_ENV)

# =============================================================================
# llama.cpp server calls
# =============================================================================

# These are now mostly in llmo.llama

# =============================================================================
# Build helpers for direct LLM artifacts
# =============================================================================



def maybe_fix_cpp_compile_failure(model_name: str, model_display_name: str, target_source: Path, cpp_result: LlmCallResult, model_dir: Path) -> LlmCallResult:
    source_file = Path(cpp_result.output_file)
    text = source_file.read_text(encoding="utf-8", errors="replace")
    if not contains_target_function_definition(text, target_source.name):
        cpp_result.success = False
        cpp_result.error = f"Output did not contain a definition for {source_function_name(target_source)}; rejecting before compile."
        return cpp_result

    check_dir = model_dir / sanitize_name(target_source.name) / "compile_check_cpp_initial"
    compile_result = compile_replacement_artifact_for_check(
        check_dir, target_source.name, source_file, "cpp",
        CLANG_CXX_COMPILER, LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL,
        SUT_DIR, PROJECT_ROOT, LLM_COMPILE_TIMEOUT_SECONDS,
        other_sources_for_replacement(target_source.name)
    )
    write_json(check_dir / "compile_metadata.json", asdict(compile_result))
    if compile_result.returncode == 0:
        abi_result = run_abi_symbol_check(check_dir, check_dir / "libSUT.so")
        if abi_result.returncode == 0:
            return cpp_result
        cpp_result.success = False
        cpp_result.error = f"Optimized C++ compiled but failed ABI symbol check. See {abi_result.stderr_file}"
        return cpp_result

    print(f"Optimized {target_source.name} from {model_display_name} failed to compile; asking model for one fix attempt")
    compiler_stdout = Path(compile_result.stdout_file).read_text(encoding="utf-8", errors="replace")
    compiler_stderr = Path(compile_result.stderr_file).read_text(encoding="utf-8", errors="replace")
    failed_source = source_file.read_text(encoding="utf-8", errors="replace")
    fix_prompt = make_cpp_compile_fix_prompt(target_source, failed_source, compiler_stdout, compiler_stderr)

    target_dir = model_dir / sanitize_name(target_source.name)
    prompt_file = target_dir / "prompt_cpp_fix_compile.txt"
    raw_response_file = target_dir / "raw_response_cpp_fix_compile.txt"
    fixed_output_file = target_dir / f"optimized_{target_source.stem}.fixed.cpp"
    prompt_file.write_text(fix_prompt, encoding="utf-8")

    start = time.perf_counter()
    try:
        response = call_llm(model_name, fix_prompt)
        duration = time.perf_counter() - start
        raw_response_file.write_text(response, encoding="utf-8")
        fixed_source = extract_code_block(response)
        fixed_output_file.write_text(fixed_source, encoding="utf-8")
        fix_result = LlmCallResult(model_display_name, "cpp_fix_compile", target_source.name, duration, str(prompt_file), str(raw_response_file), str(fixed_output_file), True)
        if not contains_target_function_definition(fixed_source, target_source.name):
            fix_result.success = False
            fix_result.error = f"Fixed output did not contain a definition for {source_function_name(target_source)}."
            write_json(target_dir / "result_cpp_fix_compile.json", asdict(fix_result))
            cpp_result.success = False
            cpp_result.error = "Initial optimized C++ failed and fixed output did not define the target function."
            return cpp_result

        recheck_dir = target_dir / "compile_check_cpp_fixed"
        fixed_compile_result = compile_replacement_artifact_for_check(
            recheck_dir, target_source.name, fixed_output_file, "cpp",
            CLANG_CXX_COMPILER, LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL,
            SUT_DIR, PROJECT_ROOT, LLM_COMPILE_TIMEOUT_SECONDS,
            other_sources_for_replacement(target_source.name)
        )
        write_json(recheck_dir / "compile_metadata.json", asdict(fixed_compile_result))
        if fixed_compile_result.returncode != 0:
            fix_result.success = False
            fix_result.error = f"C++ compile-fix attempt still failed. See {fixed_compile_result.stderr_file}"
            write_json(target_dir / "result_cpp_fix_compile.json", asdict(fix_result))
            cpp_result.success = False
            cpp_result.error = "Initial optimized C++ failed and the one allowed repair attempt also failed."
            return cpp_result

        fixed_abi_result = run_abi_symbol_check(recheck_dir, recheck_dir / "libSUT.so")
        if fixed_abi_result.returncode != 0:
            fix_result.success = False
            fix_result.error = f"C++ compile-fix attempt compiled but failed ABI symbol check. See {fixed_abi_result.stderr_file}"
            write_json(target_dir / "result_cpp_fix_compile.json", asdict(fix_result))
            cpp_result.success = False
            cpp_result.error = "Initial optimized C++ failed and the one allowed repair attempt failed ABI symbol validation."
            return cpp_result

        write_json(target_dir / "result_cpp_fix_compile.json", asdict(fix_result))
        cpp_result.output_file = str(fixed_output_file)
        cpp_result.error = f"Initial C++ failed to compile; using one-shot fixed source from {fixed_output_file}"
        return cpp_result
    except Exception as exc:
        duration = time.perf_counter() - start
        fix_result = LlmCallResult(model_display_name, "cpp_fix_compile", target_source.name, duration, str(prompt_file), str(raw_response_file), str(fixed_output_file), False, str(exc))
        write_json(target_dir / "result_cpp_fix_compile.json", asdict(fix_result))
        cpp_result.success = False
        cpp_result.error = f"Initial optimized C++ failed and repair request failed: {exc}"
        return cpp_result




def run_llm_artifact_generation() -> tuple[int, list[dict[str, Any]]]:
    models = configured_llm_models()
    targets = llm_target_source_files_local()
    LLM_ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    input_dir = LLM_ARTIFACT_ROOT / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    # Save split-source inputs for reproducibility.
    for source in all_sut_cpp_files() + list(SUT_DIR.glob("*.h")):
        shutil.copy2(source, input_dir / source.name)

    cpp_prompts: dict[str, str] = {}
    ir_prompts: dict[str, str] = {}
    if RUN_LLM_CPP_TASKS:
        for target in targets:
            prompt = make_cpp_optimization_prompt(target)
            cpp_prompts[target.name] = prompt
            (input_dir / f"prompt_cpp_{target.stem}.txt").write_text(prompt, encoding="utf-8")

    if RUN_LLM_IR_TASKS:
        for target in targets:
            print(f"Generating {LLM_IR_OPTIMIZATION_LEVEL} LLVM IR from: {target}")
            ir_dir = input_dir / "ir" / target.stem
            ir_result = generate_llvm_ir(ir_dir, target)
            write_json(ir_dir / "generate_ir_metadata.json", asdict(ir_result))
            if ir_result.returncode != 0:
                print(f"IR generation failed for {target.name}. See {ir_result.stderr_file}", file=sys.stderr)
                continue
            ir_file = ir_dir / f"{target.stem}_{sanitize_name(LLM_IR_OPTIMIZATION_LEVEL)}.ll"
            llvm_ir = ir_file.read_text(encoding="utf-8")
            prompt = make_ir_optimization_prompt(target, llvm_ir)
            ir_prompts[target.name] = prompt
            (input_dir / f"prompt_ir_{target.stem}.txt").write_text(prompt, encoding="utf-8")

    all_results: list[dict[str, Any]] = []
    for model in models:
        model_name = model.alias or model.name
        model_dir = LLM_ARTIFACT_ROOT / sanitize_name(model.name)
        model_dir.mkdir(parents=True, exist_ok=True)
        server_process: Optional[subprocess.Popen[str]] = None
        try:
            server_process = start_llama_server(model, model_dir)
            wait_for_llama_ready(server_process)
            warm_up_llm(model_name, model_dir)

            tasks: list[tuple[str, Path, str, Path]] = []
            for target in targets:
                target_dir = model_dir / sanitize_name(target.name)
                target_dir.mkdir(parents=True, exist_ok=True)
                if target.name in cpp_prompts:
                    tasks.append(("cpp", target, cpp_prompts[target.name], target_dir / f"optimized_{target.stem}.cpp"))
                if target.name in ir_prompts:
                    tasks.append(("ir", target, ir_prompts[target.name], target_dir / f"optimized_{target.stem}.ll"))

            for task_name, target, prompt, output_file in tasks:
                prompt_file = output_file.parent / f"prompt_{task_name}_{target.stem}.txt"
                raw_response_file = output_file.parent / f"raw_response_{task_name}_{target.stem}.txt"
                prompt_file.write_text(prompt, encoding="utf-8")
                print(f"Running {task_name} optimization for {target.name} with {model.name}")
                start = time.perf_counter()
                try:
                    response = call_llm(model_name, prompt)
                    duration = time.perf_counter() - start
                    raw_response_file.write_text(response, encoding="utf-8")
                    output_file.write_text(extract_code_block(response), encoding="utf-8")
                    call_result = LlmCallResult(model.name, task_name, target.name, duration, str(prompt_file), str(raw_response_file), str(output_file), True)
                    if task_name == "cpp":
                        call_result = maybe_fix_cpp_compile_failure(model_name, model.name, target, call_result, model_dir)
                except Exception as exc:
                    duration = time.perf_counter() - start
                    call_result = LlmCallResult(model.name, task_name, target.name, duration, str(prompt_file), str(raw_response_file), str(output_file), False, str(exc))
                write_json(output_file.parent / f"result_{task_name}_{target.stem}.json", asdict(call_result))
                all_results.append(asdict(call_result))
        except Exception as exc:
            failure = {"model": model.name, "task": "model_setup", "target_source": "", "duration_seconds": 0.0, "prompt_file": "", "raw_response_file": "", "output_file": "", "success": False, "error": str(exc)}
            write_json(model_dir / "result_model_setup.json", failure)
            all_results.append(failure)
        finally:
            stop_process(server_process)

    write_json(LLM_ARTIFACT_ROOT / "summary.json", all_results)
    print(f"LLM artifacts written to: {LLM_ARTIFACT_ROOT}")
    return (0 if all(item.get("success") for item in all_results) else 1), all_results

# =============================================================================
# Benchmarking
# =============================================================================



def build_and_benchmark_direct_llm_variant(variant_name: str, source_file: Path, source_kind: str, target_source_name: str, model_name: str, llm_task: str) -> DirectBuildMetadata:
    build_dir = BUILD_ROOT / variant_name
    if CLEAN_BEFORE_BUILD and build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    total_start = time.perf_counter()
    libsut_path = build_dir / "libSUT.so"

    command = [CLANG_CXX_COMPILER, "-std=c++23", LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL, "-DNDEBUG", "-shared", "-fPIC", "-I", str(SUT_DIR), "-I", str(PROJECT_ROOT), str(source_file)]
    for source in other_sources_for_replacement(target_source_name):
        command.append(str(source))
    command.extend(["-o", str(libsut_path)])

    ir_verify_result: Optional[CommandResult] = None
    abi_check: Optional[CommandResult] = None
    benchmark_results: list[CommandResult] = []

    if source_kind == "ir":
        ir_verify_result = verify_llvm_ir(build_dir, source_file)

    if ir_verify_result is not None and ir_verify_result.returncode != 0:
        compile_result = CommandResult([], str(PROJECT_ROOT), 125, 0.0, str(build_dir / "compile_stdout.txt"), str(build_dir / "compile_stderr.txt"))
        Path(compile_result.stdout_file).write_text("", encoding="utf-8")
        Path(compile_result.stderr_file).write_text(
            f"Skipping compile because opt -passes=verify failed. See {ir_verify_result.stderr_file}\n",
            encoding="utf-8",
        )
    else:
        compile_result = run_command(
            command,
            PROJECT_ROOT,
            build_dir / "compile_stdout.txt",
            build_dir / "compile_stderr.txt",
            timeout_seconds=LLM_COMPILE_TIMEOUT_SECONDS,
        )
        if compile_result.returncode == 0 and libsut_path.exists():
            abi_check = run_abi_symbol_check(build_dir, libsut_path)
            if abi_check.returncode == 0:
                benchmark_results = run_benchmarks_for_lib(build_dir, libsut_path)

    metadata = DirectBuildMetadata(variant_name, source_kind, target_source_name, str(source_file), str(build_dir), compile_result, benchmark_results, abi_check, str(libsut_path) if libsut_path.exists() else None, str(RUNNER_EXECUTABLE_NAME), time.perf_counter() - total_start, model_name, llm_task, ir_verify_result)
    write_json(build_dir / "build_metadata.json", asdict(metadata))
    return metadata


def benchmark_llm_artifacts(llm_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    benchmark_summary: list[dict[str, Any]] = []
    for result in llm_results:
        if not result.get("success"):
            continue
        task = result["task"]
        if task == "cpp":
            source_kind = "cpp"
        elif task == "ir":
            source_kind = "ir"
        else:
            continue
        output_file = Path(result["output_file"])
        target_source = result["target_source"]
        if not output_file.exists():
            benchmark_summary.append({**result, "failed": True, "error": "LLM output file missing"})
            continue
        model_name = result["model"]
        variant_name = f"llm_{sanitize_name(model_name)}_{sanitize_name(target_source)}_{sanitize_name(task)}"
        print(f"\n=== {variant_name} ({output_file.name}) ===")
        try:
            metadata = build_and_benchmark_direct_llm_variant(variant_name, output_file, source_kind, target_source, model_name, task)
            compile_ok = metadata.compile.returncode == 0
            abi_ok = metadata.abi_check is not None and metadata.abi_check.returncode == 0
            benchmark_ok = bool(metadata.benchmark) and all(item.command_result.returncode == 0 for item in metadata.benchmark)
            print(f"compile:   {'ok' if compile_ok else 'failed'}")
            print(f"abi:       {'ok' if abi_ok else 'failed'}")
            print(f"benchmark: {'ok' if benchmark_ok else 'failed'}")
            print(f"folder:    {metadata.build_dir}")
            benchmark_summary.append({
                "variant_type": "llm",
                "model": model_name,
                "task": task,
                "target_source": target_source,
                "failed": not benchmark_ok,
                "compile_returncode": metadata.compile.returncode,
                "ir_verify_returncode": metadata.ir_verify.returncode if metadata.ir_verify else None,
                "abi_returncode": metadata.abi_check.returncode if metadata.abi_check else None,
                "benchmark_returncodes": [item.command_result.returncode for item in metadata.benchmark],
                "total_duration_seconds": metadata.total_duration_seconds,
                "build_dir": metadata.build_dir,
                "metadata_file": str(Path(metadata.build_dir) / "build_metadata.json"),
                "source_file": str(output_file),
            })
        except Exception as exc:
            print(f"failed: {exc}", file=sys.stderr)
            benchmark_summary.append({"variant_type": "llm", "model": model_name, "task": task, "target_source": target_source, "failed": True, "error": str(exc), "source_file": str(output_file)})
    write_json(BUILD_ROOT / "llm_benchmark_summary.json", benchmark_summary)
    return benchmark_summary


def build_and_benchmark_variant(variant: BuildVariant, run_dir: Path) -> BuildMetadata:
    build_dir = run_dir / "artifacts" / variant.name
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    total_start = time.perf_counter()

    configure_command = [
        "cmake", "-S", str(PROJECT_ROOT), "-B", str(build_dir),
        f"-DCMAKE_C_COMPILER={CLANG_C_COMPILER}",
        f"-DCMAKE_CXX_COMPILER={CLANG_CXX_COMPILER}",
        "-DCMAKE_BUILD_TYPE=Release",
        f"-DCMAKE_C_FLAGS={variant.clang_optimization_flag}",
        f"-DCMAKE_CXX_FLAGS={variant.clang_optimization_flag}",
        f"-DCMAKE_CXX_FLAGS_RELEASE={variant.clang_optimization_flag} -DNDEBUG",
        "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
    ]
    if CMAKE_GENERATOR is not None:
        configure_command.extend(["-G", CMAKE_GENERATOR])
    configure_result = run_command(configure_command, PROJECT_ROOT, build_dir / "configure_stdout.txt", build_dir / "configure_stderr.txt")

    build_result = CommandResult([], str(PROJECT_ROOT), -1, 0.0, str(build_dir / "build_stdout.txt"), str(build_dir / "build_stderr.txt"))
    benchmark_results: list[BenchmarkMeasurement] = []
    abi_check: Optional[CommandResult] = None
    libsut_path: Optional[Path] = None
    runner_path: Optional[Path] = None

    if configure_result.returncode == 0:
        build_command = ["cmake", "--build", str(build_dir)]
        if PARALLEL_BUILD_JOBS is not None:
            build_command.extend(["--parallel", str(PARALLEL_BUILD_JOBS)])
        build_result = run_command(build_command, PROJECT_ROOT, build_dir / "build_stdout.txt", build_dir / "build_stderr.txt")

    if build_result.returncode == 0:
        libsut_path = find_libsut(build_dir)
        if libsut_path is not None:
            abi_check = run_abi_symbol_check(build_dir, libsut_path)
            # We don't benchmark here anymore, we do it in a separate sweep
            pass

    metadata = BuildMetadata(variant, str(PROJECT_ROOT), str(build_dir), CLANG_C_COMPILER, CLANG_CXX_COMPILER, CMAKE_GENERATOR, configure_result, build_result, [], abi_check, str(libsut_path) if libsut_path else None, str(runner_path) if runner_path else None, time.perf_counter() - total_start)
    write_json(build_dir / "build_metadata.json", asdict(metadata))
    return metadata

def run_build_benchmarks(args: argparse.Namespace) -> tuple[int, list[dict[str, Any]]]:
    if not (PROJECT_ROOT / "CMakeLists.txt").exists():
        print(f"Error: no CMakeLists.txt found in {PROJECT_ROOT}", file=sys.stderr)
        return 2, []
    
    run_id = make_run_id(args.run_id)
    run_dir = get_standard_path(args.output_root, "llvm", run_id)
    run_dir.mkdir(parents=True, exist_ok=True)

    variants = [BuildVariant(make_artifact_id("llvm", sanitize_variant_name(opt)), opt) for opt in OPTIMIZATION_LEVELS]
    
    # 1. Build all variants
    builds = []
    for variant in variants:
        print(f"\n=== Building {variant.name} ({variant.clang_optimization_flag}) ===")
        try:
            metadata = build_and_benchmark_variant(variant, run_dir)
            builds.append(metadata)
        except Exception as exc:
            print(f"Build failed for {variant.name}: {exc}", file=sys.stderr)

    # 2. Benchmark variants using randomized balanced schedule
    protocol = BenchmarkProtocol(
        repetitions=args.benchmark_repetitions,
        seed=args.seed,
        noise_threshold_percent=args.noise_threshold_percent,
        ordering="randomized"
    )
    
    valid_builds = [b for b in builds if b.build.returncode == 0 and b.libsut_path and Path(b.libsut_path).exists()]
    artifact_ids = [b.variant.name for b in valid_builds]
    
    if not artifact_ids:
        print("No valid builds to benchmark.")
        return 1, []

    sequence = get_randomized_balanced_sequence(artifact_ids, protocol.repetitions, protocol.seed)
    
    all_measurements: List[BenchmarkMeasurement] = []
    reps = {aid: 0 for aid in artifact_ids}
    
    for i, aid in enumerate(sequence):
        build = next(b for b in valid_builds if b.variant.name == aid)
        libsut = Path(build.libsut_path)
        iteration = reps[aid]
        reps[aid] += 1
        
        print(f"[{i+1}/{len(sequence)}] Benchmarking {aid} (rep {iteration})...")
        measurements = run_benchmarks_for_lib(
            Path(build.build_dir), libsut, 
            run_all=True, 
            iteration=iteration,
            artifact_id=aid,
            sequence_index=i
        )
        all_measurements.extend(measurements)

    # 3. Summarize results
    summary = []
    
    # Also produce comparisons against a reference level (default O1)
    ref_level = args.comparison_baseline or "-O1"
    ref_aid = make_artifact_id("llvm", sanitize_variant_name(ref_level))
    
    for aid in artifact_ids:
        build = next(b for b in builds if b.variant.name == aid)
        variant_measurements = [m for m in all_measurements if m.artifact_id == aid]
        
        # We need to group by benchmark function
        by_bench = {}
        for m in variant_measurements:
            by_bench.setdefault(m.benchmark_name, []).append(m)
            
        bench_stats = {}
        for bname, ms in by_bench.items():
            stats = calculate_benchmark_statistics(ms, protocol.repetitions)
            bench_stats[bname] = asdict(stats)
            
        summary.append({
            "artifact_id": aid,
            "variant": asdict(build.variant),
            "build_dir": build.build_dir,
            "benchmark_statistics": bench_stats,
            "metadata_file": str(Path(build.build_dir) / "build_metadata.json"),
        })
        
        art_meta = {
            "schema_version": 2,
            "artifact_id": aid,
            "run_id": run_id,
            "experiment_type": "llvm",
            "benchmark_name": "all", # pure llvm builds contain all benchmarks
            "pipeline_id": f"cpp-clang-{sanitize_variant_name(build.variant.clang_optimization_flag)}",
            "logical_artifact_id": make_logical_artifact_id(
                "llvm", run_id, aid, "all",
                pipeline_id=f"cpp-clang-{sanitize_variant_name(build.variant.clang_optimization_flag)}",
            ),
            "compile_flags": build.variant.clang_optimization_flag,
            "paths": {
                "build_dir": build.build_dir,
                "libsut": build.libsut_path
            },
            "benchmark_statistics": bench_stats
        }
        
        # If we have a reference, add comparison
        if ref_aid in artifact_ids and aid != ref_aid:
            ref_measurements = [m for m in all_measurements if m.artifact_id == ref_aid]
            ref_by_bench = {}
            for m in ref_measurements:
                ref_by_bench.setdefault(m.benchmark_name, []).append(m)
            
            comparisons = {}
            for bname, ms in by_bench.items():
                if bname in ref_by_bench:
                    comp = compare_benchmarks(
                        calculate_benchmark_statistics(ms, protocol.repetitions),
                        calculate_benchmark_statistics(ref_by_bench[bname], protocol.repetitions),
                        protocol.noise_threshold_percent,
                        ref_aid,
                        aid,
                        sequence
                    )
                    comparisons[bname] = asdict(comp)
            summary[-1]["comparisons_vs_baseline"] = comparisons
            art_meta["comparisons_vs_baseline"] = comparisons

        # Keep build-local metadata for compatibility and also publish a canonical
        # artifact directory so the final matrix can discover every LLVM variant.
        write_json_atomic(Path(build.build_dir) / "artifact.json", art_meta)
        artifact_dir = run_dir / "artifacts" / aid
        artifact_dir.mkdir(parents=True, exist_ok=True)
        if build.libsut_path and Path(build.libsut_path).exists():
            shutil.copy2(build.libsut_path, artifact_dir / "libSUT.so")
            art_meta["paths"]["canonical_libsut"] = str(artifact_dir / "libSUT.so")
        write_json_atomic(artifact_dir / "artifact.json", art_meta)
        write_json_atomic(artifact_dir / "benchmark-statistics.json", bench_stats)

    write_json_atomic(run_dir / "summary.json", summary)
    
    # Run level metadata
    from llmo.metadata import get_run_metadata
    run_meta = get_run_metadata()
    run_meta.update({
        "run_id": run_id,
        "experiment_type": "llvm",
        "benchmark_protocol": asdict(protocol),
        "comparison_baseline": ref_level
    })
    write_json_atomic(run_dir / "run.json", run_meta)
    
    print(f"\nSummary written to: {run_dir / 'summary.json'}")
    return 0, summary


def run_overnight_benchmarks(args: argparse.Namespace) -> int:
    clang_status, clang_summary = run_build_benchmarks(args)
    # The overnight part is mostly for legacy support or broad sweeps.
    # We skip LLM generation here to keep it simple and focused on the new runners.
    return clang_status

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Build and benchmark pure LLVM optimization levels.")
    parser.add_argument("--benchmark-repetitions", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--noise-threshold-percent", type=float, default=2.0)
    parser.add_argument("--comparison-baseline", default="-O1", help="Optimization level to use as baseline (e.g. -O1).")
    parser.add_argument("--run-id", help="Explicit run ID.")
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "results")
    args = parser.parse_args()
    
    return run_overnight_benchmarks(args)


if __name__ == "__main__":
    raise SystemExit(main())
