#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent
SUT_DIR = PROJECT_ROOT / "SUT"
BUILD_ROOT = PROJECT_ROOT / "benchmark-builds"
LLM_ARTIFACT_ROOT = BUILD_ROOT / "llm-artifacts-split-sources"

CLANG_C_COMPILER = "clang"
CLANG_CXX_COMPILER = "clang++"
CMAKE_GENERATOR: Optional[str] = "Ninja"

OPTIMIZATION_LEVELS = ["-O0", "-O1", "-O2", "-O3", "-Ofast", "-Os", "-Oz"]
LLM_IR_OPTIMIZATION_LEVEL = "-O1"
LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL = "-O3"

BENCHMARK_FUNCTIONS = {
    0: "fibonacci",
    1: "format_list",
    2: "repeated_sort",
    3: "count_matches",
    4: "top_words_from_file",
}

# Only these source files are sent to the LLM by default. Shared support files are
# linked in unchanged unless you override this with LLM_TARGET_FILES.
DEFAULT_LLM_TARGET_FILES = [
    "fibonacci.cpp",
    "format_list.cpp",
    "repeated_sort.cpp",
    "count_matches.cpp",
    "top_words_from_file.cpp",
]

# Comma-separated override, for example:
#   LLM_TARGET_FILES=count_matches.cpp,top_words_from_file.cpp ./run_builds_split_sources.py
LLM_TARGET_FILES = [
    item.strip()
    for item in os.environ.get("LLM_TARGET_FILES", "").split(",")
    if item.strip()
]

CLEAN_BEFORE_BUILD = True
PARALLEL_BUILD_JOBS = os.cpu_count()
RUNNER_EXECUTABLE_NAME = PROJECT_ROOT / "cmake-build-release-llvm-20/librunner/librunner"
RUNNER_ARGS: list[str] = []

# llama.cpp server configuration.
LLAMA_SERVER_EXECUTABLE = os.environ.get("LLAMA_SERVER", "llama-server")
LLAMA_HOST = os.environ.get("LLAMA_HOST", "127.0.0.1")
LLAMA_PORT = int(os.environ.get("LLAMA_PORT", "8001"))
LLAMA_BASE_URL = os.environ.get("LLAMA_BASE_URL", f"http://{LLAMA_HOST}:{LLAMA_PORT}").rstrip("/")
LLAMA_API_KEY = os.environ.get("LLAMA_API_KEY", "")
LLAMA_CTX_SIZE = int(os.environ.get("LLAMA_CTX_SIZE", "32768"))
LLAMA_THREADS = int(os.environ.get("LLAMA_THREADS", "12"))
LLAMA_THREADS_BATCH = int(os.environ.get("LLAMA_THREADS_BATCH", "24"))
LLAMA_BATCH_SIZE = int(os.environ.get("LLAMA_BATCH_SIZE", "2048"))
LLAMA_UBATCH_SIZE = int(os.environ.get("LLAMA_UBATCH_SIZE", "512"))
LLAMA_FLASH_ATTN = os.environ.get("LLAMA_FLASH_ATTN", "auto")
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.0"))
LLM_TOP_P = float(os.environ.get("LLM_TOP_P", "1.0"))
LLM_SEED = int(os.environ.get("LLM_SEED", "1234"))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "4096"))
LLAMA_READY_TIMEOUT = int(os.environ.get("LLAMA_READY_TIMEOUT", "1800"))
LLAMA_REQUEST_TIMEOUT = int(os.environ.get("LLAMA_REQUEST_TIMEOUT", "10800"))

LLM_MODELS: list[dict[str, Optional[str]]] = [
    {
        "name": "qwen3-14b-q4km",
        "hf_repo": "Qwen/Qwen3-14B-GGUF:Q4_K_M",
        "alias": "qwen3-14b-q4km",
    },
    {
        "name": "qwen2.5-coder-14b-q4km",
        "hf_repo": "Qwen/Qwen2.5-Coder-14B-Instruct-GGUF:Q4_K_M",
        "alias": "qwen2.5-coder-14b-q4km",
    },
    {
        "name": "gemma-4-12b-it-qat-udq4xl",
        "hf_repo": "unsloth/gemma-4-12B-it-qat-GGUF:UD-Q4_K_XL",
        "alias": "gemma-4-12b-it-qat-udq4xl",
    },
    {
        "name": "llm-compiler-7b-ftd-q4km",
        "hf_repo": "second-state/llm-compiler-7b-ftd-GGUF:Q4_K_M",
        "alias": "llm-compiler-7b-ftd-q4km",
    },
    {
        "name": "llm-compiler-13b-ftd-q4km",
        "hf_repo": "second-state/llm-compiler-13b-ftd-GGUF:Q4_K_M",
        "alias": "llm-compiler-13b-ftd-q4km",
    },
]

RUN_LLM_IR_TASKS = os.environ.get("RUN_LLM_IR_TASKS", "1") != "0"
RUN_LLM_CPP_TASKS = os.environ.get("RUN_LLM_CPP_TASKS", "1") != "0"

# =============================================================================
# Data structures
# =============================================================================

@dataclass
class BuildVariant:
    name: str
    clang_optimization_flag: str


@dataclass
class CommandResult:
    command: list[str]
    cwd: str
    returncode: int
    duration_seconds: float
    stdout_file: str
    stderr_file: str


@dataclass
class BuildMetadata:
    variant: BuildVariant
    project_root: str
    build_dir: str
    c_compiler: str
    cxx_compiler: str
    cmake_generator: Optional[str]
    configure: CommandResult
    build: CommandResult
    benchmark: list[CommandResult]
    libsut_path: Optional[str]
    runner_path: Optional[str]
    total_duration_seconds: float


@dataclass
class LlmModelConfig:
    name: str
    hf_repo: Optional[str] = None
    alias: Optional[str] = None


@dataclass
class LlmCallResult:
    model: str
    task: str
    target_source: str
    duration_seconds: float
    prompt_file: str
    raw_response_file: str
    output_file: str
    success: bool
    error: Optional[str] = None


@dataclass
class DirectBuildMetadata:
    variant_name: str
    source_kind: str
    target_source: str
    source_file: str
    build_dir: str
    compile: CommandResult
    benchmark: list[CommandResult]
    libsut_path: Optional[str]
    runner_path: str
    total_duration_seconds: float
    model: Optional[str] = None
    llm_task: Optional[str] = None

# =============================================================================
# Helpers
# =============================================================================

def run_command(command: list[str], cwd: Path, stdout_file: Path, stderr_file: Path, env: Optional[dict[str, str]] = None) -> CommandResult:
    start = time.perf_counter()
    stdout_file.parent.mkdir(parents=True, exist_ok=True)
    stderr_file.parent.mkdir(parents=True, exist_ok=True)
    with stdout_file.open("w", encoding="utf-8") as out, stderr_file.open("w", encoding="utf-8") as err:
        completed = subprocess.run(command, cwd=str(cwd), stdout=out, stderr=err, text=True, env=env)
    return CommandResult(command, str(cwd), completed.returncode, time.perf_counter() - start, str(stdout_file), str(stderr_file))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def sanitize_name(value: str) -> str:
    return value.replace("/", "_").replace("\\", "_").replace("-", "_").replace("+", "plus").replace("=", "_").replace(":", "_").replace(".", "_")


def sanitize_variant_name(opt_flag: str) -> str:
    return sanitize_name(opt_flag).lstrip("_")


def find_libsut(build_dir: Path) -> Optional[Path]:
    candidates = list(build_dir.rglob("libSUT.so"))
    return candidates[0] if candidates else None


def try_write_benchmark_json(stdout_file: Path, output_json_file: Path) -> None:
    text = stdout_file.read_text(encoding="utf-8").strip()
    if not text:
        return
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return
    write_json(output_json_file, parsed)


def configured_llm_models() -> list[LlmModelConfig]:
    return [LlmModelConfig(**item) for item in LLM_MODELS]


def all_sut_cpp_files() -> list[Path]:
    files = sorted(SUT_DIR.glob("*.cpp"))
    return [path for path in files if not path.name.endswith("_original.cpp")]


def llm_target_source_files() -> list[Path]:
    names = LLM_TARGET_FILES or DEFAULT_LLM_TARGET_FILES
    paths = [SUT_DIR / name for name in names]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing LLM target source files: " + ", ".join(missing))
    return paths


def source_function_name(source_file: Path) -> str:
    return source_file.stem


def read_support_headers() -> str:
    parts: list[str] = []
    for header in [SUT_DIR / "library.h", SUT_DIR / "sut_common.h"]:
        if header.exists():
            parts.append(f"// {header.name}\n" + header.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def other_sources_for_replacement(target_source_name: str) -> list[Path]:
    return [path for path in all_sut_cpp_files() if path.name != target_source_name]


def extract_code_block(text: str) -> str:
    marker = "```"
    first = text.find(marker)
    if first == -1:
        return text.strip() + "\n"
    second = text.find(marker, first + len(marker))
    if second == -1:
        return text.strip() + "\n"
    block = text[first + len(marker):second]
    lines = block.splitlines()
    if lines and lines[0].strip().lower() in {"cpp", "c++", "cc", "llvm", "llvm-ir", "ir", "ll"}:
        lines = lines[1:]
    return "\n".join(lines).strip() + "\n"


def contains_target_function_definition(source: str, target_source_name: str) -> bool:
    # Cheap preflight filter to reject header echoes and empty responses. The real
    # correctness check remains compile + librunner.
    target = target_source_name.removesuffix(".cpp")
    if target == "top_words_from_file":
        needle = "WordCount* top_words_from_file("
    elif target == "count_matches":
        needle = "size_t count_matches("
    elif target == "repeated_sort":
        needle = "int64_t repeated_sort("
    elif target == "format_list":
        needle = "char* format_list("
    elif target == "fibonacci":
        needle = "uint64_t fibonacci("
    else:
        return True
    return needle in source and "{" in source[source.find(needle):source.find(needle) + 500]

# =============================================================================
# LLM prompts
# =============================================================================

def function_specific_notes(target_source: Path) -> str:
    name = target_source.stem
    if name == "top_words_from_file":
        return """
Function-specific invariants for top_words_from_file:
- Words consist only of alphabetic characters according to std::isalpha on unsigned char.
- Case is normalized with std::tolower on unsigned char.
- Ignore words are normalized with the same word-character and lowercase logic.
- Results are ordered by descending count.
- Ties are ordered lexicographically ascending by word.
- result_length is set to 0 before failure returns and to the returned entry count on success.
- Return nullptr if max_results is 0 or no words remain.
- Every returned WordCount.word must be malloc-compatible and must be released by free_word_counts.
- Do not define free_word_counts in this file; it is provided by free_functions.cpp.
"""
    if name == "count_matches":
        return """
Function-specific invariants for count_matches:
- Invalid pointer/length combinations return 0.
- A query contributes exactly 1 match if its value is present at least once in allowed.
- Duplicate values in queries are counted independently.
- Duplicate values in allowed must not multiply the count for one query value.
"""
    if name == "format_list":
        return """
Function-specific invariants for format_list:
- Format is exactly [1, 2, 3] with comma+space between values and no trailing comma.
- Empty input produces [].
- The returned char* must be malloc-compatible and freed by free_string.
"""
    if name == "repeated_sort":
        return """
Function-specific invariants for repeated_sort:
- Invalid pointer/length combinations return 0.
- Empty input returns 0.
- For each round r, sort a fresh copy, add the median, then add values[r % values.size()].
- For even length, median is integer average of the two middle values using int64_t before conversion to int.
"""
    if name == "fibonacci":
        return """
Function-specific invariants for fibonacci:
- Preserve uint64_t wraparound behavior of the public API.
- fibonacci(0) == 0 and fibonacci(1) == 1.
"""
    return ""


def make_cpp_optimization_prompt(target_source: Path) -> str:
    headers = read_support_headers()
    source = target_source.read_text(encoding="utf-8")
    notes = function_specific_notes(target_source)
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
{notes}
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
    notes = function_specific_notes(target_source)
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
{notes}
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
    headers = read_support_headers()
    notes = function_specific_notes(target_source)
    return f"""You are an expert LLVM optimizer.

Task: optimize the LLVM IR for {target_source.name} for runtime performance.

Hard requirements:
- Return one complete LLVM IR module that can be compiled by clang++/LLVM.
- Preserve the exported ABI exactly as declared in library.h.
- Do not define unrelated exported functions from library.h.
- Preserve externally observable behavior and allocation/freeing conventions.
- Keep any external declarations needed to link against the other SUT object files.
- Do not include markdown, commentary, explanations, benchmarking notes, or code fences in your answer.
{notes}
Headers:
```cpp
{headers}
```

LLVM IR for {target_source.name}, produced with {LLM_IR_OPTIMIZATION_LEVEL}:
```llvm
{llvm_ir}
```
"""

# =============================================================================
# llama.cpp server calls
# =============================================================================

def start_llama_server(model: LlmModelConfig, log_dir: Path) -> subprocess.Popen[str]:
    if not model.hf_repo:
        raise ValueError(f"LLM model {model.name!r} is missing hf_repo")
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout = (log_dir / "llama_server_stdout.txt").open("w", encoding="utf-8")
    stderr = (log_dir / "llama_server_stderr.txt").open("w", encoding="utf-8")
    command = [
        LLAMA_SERVER_EXECUTABLE,
        "-hf", model.hf_repo,
        "--alias", model.alias or model.name,
        "--host", LLAMA_HOST,
        "--port", str(LLAMA_PORT),
        "--ctx-size", str(LLAMA_CTX_SIZE),
        "--threads", str(LLAMA_THREADS),
        "--threads-batch", str(LLAMA_THREADS_BATCH),
        "--batch-size", str(LLAMA_BATCH_SIZE),
        "--ubatch-size", str(LLAMA_UBATCH_SIZE),
        "--flash-attn", LLAMA_FLASH_ATTN,
        "--no-webui",
    ]
    print("Starting llama-server:", " ".join(command))
    return subprocess.Popen(command, cwd=str(PROJECT_ROOT), stdout=stdout, stderr=stderr, text=True)


def stop_process(process: Optional[subprocess.Popen[str]]) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=15)


def http_json(method: str, url: str, payload: Optional[dict[str, Any]] = None, timeout: int = 600) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if LLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {LLAMA_API_KEY}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def wait_for_llama_ready(process: subprocess.Popen[str], timeout_seconds: int = LLAMA_READY_TIMEOUT) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Optional[str] = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"llama-server exited with code {process.returncode}")
        try:
            http_json("GET", f"{LLAMA_BASE_URL}/health", timeout=5)
            return
        except Exception as exc:
            last_error = str(exc)
            time.sleep(1)
    raise TimeoutError(f"llama-server did not become ready: {last_error}")


def call_llm(model_name: str, prompt: str) -> str:
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a compiler and C++ optimization assistant. Return only the requested source code."},
            {"role": "user", "content": prompt},
        ],
        "temperature": LLM_TEMPERATURE,
        "top_p": LLM_TOP_P,
        "seed": LLM_SEED,
        "max_tokens": LLM_MAX_TOKENS,
    }
    response = http_json("POST", f"{LLAMA_BASE_URL}/v1/chat/completions", payload, timeout=LLAMA_REQUEST_TIMEOUT)
    return response["choices"][0]["message"]["content"]


def warm_up_llm(model_name: str, output_dir: Path) -> None:
    prompt = "Optimize this C++ function. Return only code: int f(int x) { return x + 0; }"
    start = time.perf_counter()
    response = call_llm(model_name, prompt)
    duration = time.perf_counter() - start
    (output_dir / "warmup_prompt.txt").write_text(prompt, encoding="utf-8")
    (output_dir / "warmup_response.txt").write_text(response, encoding="utf-8")
    write_json(output_dir / "warmup_metadata.json", {"duration_seconds": duration})

# =============================================================================
# Build helpers for direct LLM artifacts
# =============================================================================

def compile_replacement_artifact_for_check(output_dir: Path, target_source_name: str, replacement_file: Path, source_kind: str) -> CommandResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    libsut_path = output_dir / "libSUT.so"
    include_dirs = [replacement_file.parent, SUT_DIR, PROJECT_ROOT]
    command = [CLANG_CXX_COMPILER, "-std=c++23", LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL, "-DNDEBUG", "-shared", "-fPIC"]
    for include_dir in include_dirs:
        if include_dir.exists():
            command.extend(["-I", str(include_dir)])
    command.append(str(replacement_file))
    for source in other_sources_for_replacement(target_source_name):
        command.append(str(source))
    command.extend(["-o", str(libsut_path)])
    return run_command(command, PROJECT_ROOT, output_dir / "compile_stdout.txt", output_dir / "compile_stderr.txt")


def maybe_fix_cpp_compile_failure(model_name: str, model_display_name: str, target_source: Path, cpp_result: LlmCallResult, model_dir: Path) -> LlmCallResult:
    source_file = Path(cpp_result.output_file)
    text = source_file.read_text(encoding="utf-8", errors="replace")
    if not contains_target_function_definition(text, target_source.name):
        cpp_result.success = False
        cpp_result.error = f"Output did not contain a definition for {source_function_name(target_source)}; rejecting before compile."
        return cpp_result

    check_dir = model_dir / sanitize_name(target_source.name) / "compile_check_cpp_initial"
    compile_result = compile_replacement_artifact_for_check(check_dir, target_source.name, source_file, "cpp")
    write_json(check_dir / "compile_metadata.json", asdict(compile_result))
    if compile_result.returncode == 0:
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
        fixed_compile_result = compile_replacement_artifact_for_check(recheck_dir, target_source.name, fixed_output_file, "cpp")
        write_json(recheck_dir / "compile_metadata.json", asdict(fixed_compile_result))
        if fixed_compile_result.returncode != 0:
            fix_result.success = False
            fix_result.error = f"C++ compile-fix attempt still failed. See {fixed_compile_result.stderr_file}"
            write_json(target_dir / "result_cpp_fix_compile.json", asdict(fix_result))
            cpp_result.success = False
            cpp_result.error = "Initial optimized C++ failed and the one allowed repair attempt also failed."
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


def generate_llvm_ir(output_dir: Path, source_file: Path) -> CommandResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_ir = output_dir / f"{source_file.stem}_{sanitize_name(LLM_IR_OPTIMIZATION_LEVEL)}.ll"
    command = [
        CLANG_CXX_COMPILER,
        "-std=c++23",
        LLM_IR_OPTIMIZATION_LEVEL,
        "-DNDEBUG",
        "-fPIC",
        "-S",
        "-emit-llvm",
        "-fno-discard-value-names",
        "-I", str(SUT_DIR),
        "-I", str(PROJECT_ROOT),
        str(source_file),
        "-o", str(output_ir),
    ]
    return run_command(command, PROJECT_ROOT, output_dir / "generate_ir_stdout.txt", output_dir / "generate_ir_stderr.txt")


def run_llm_artifact_generation() -> tuple[int, list[dict[str, Any]]]:
    models = configured_llm_models()
    targets = llm_target_source_files()
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

def run_benchmarks_for_lib(build_dir: Path, libsut_path: Path) -> list[CommandResult]:
    env = os.environ.copy()
    old_ld_library_path = env.get("LD_LIBRARY_PATH")
    env["LD_LIBRARY_PATH"] = f"{libsut_path.parent}:{old_ld_library_path}" if old_ld_library_path else str(libsut_path.parent)
    benchmark_results: list[CommandResult] = []
    for function_id, function_name in BENCHMARK_FUNCTIONS.items():
        stdout = build_dir / f"benchmark_{function_id}_{function_name}_stdout.txt"
        stderr = build_dir / f"benchmark_{function_id}_{function_name}_stderr.txt"
        command = [str(RUNNER_EXECUTABLE_NAME), str(libsut_path), str(function_id), *RUNNER_ARGS]
        result = run_command(command, build_dir, stdout, stderr, env)
        benchmark_results.append(result)
        try_write_benchmark_json(stdout, build_dir / f"benchmark_{function_id}_{function_name}_results.json")
    return benchmark_results


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

    compile_result = run_command(command, PROJECT_ROOT, build_dir / "compile_stdout.txt", build_dir / "compile_stderr.txt")
    benchmark_results: list[CommandResult] = []
    if compile_result.returncode == 0 and libsut_path.exists():
        benchmark_results = run_benchmarks_for_lib(build_dir, libsut_path)

    metadata = DirectBuildMetadata(variant_name, source_kind, target_source_name, str(source_file), str(build_dir), compile_result, benchmark_results, str(libsut_path) if libsut_path.exists() else None, str(RUNNER_EXECUTABLE_NAME), time.perf_counter() - total_start, model_name, llm_task)
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
            benchmark_ok = bool(metadata.benchmark) and all(item.returncode == 0 for item in metadata.benchmark)
            print(f"compile:   {'ok' if compile_ok else 'failed'}")
            print(f"benchmark: {'ok' if benchmark_ok else 'failed'}")
            print(f"folder:    {metadata.build_dir}")
            benchmark_summary.append({
                "variant_type": "llm",
                "model": model_name,
                "task": task,
                "target_source": target_source,
                "failed": not benchmark_ok,
                "compile_returncode": metadata.compile.returncode,
                "benchmark_returncodes": [item.returncode for item in metadata.benchmark],
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


def build_and_benchmark_variant(variant: BuildVariant) -> BuildMetadata:
    build_dir = BUILD_ROOT / variant.name
    if CLEAN_BEFORE_BUILD and build_dir.exists():
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
    benchmark_results: list[CommandResult] = []
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
            benchmark_results = run_benchmarks_for_lib(build_dir, libsut_path)

    metadata = BuildMetadata(variant, str(PROJECT_ROOT), str(build_dir), CLANG_C_COMPILER, CLANG_CXX_COMPILER, CMAKE_GENERATOR, configure_result, build_result, benchmark_results, str(libsut_path) if libsut_path else None, str(runner_path) if runner_path else None, time.perf_counter() - total_start)
    write_json(build_dir / "build_metadata.json", asdict(metadata))
    return metadata


def run_build_benchmarks() -> tuple[int, list[dict[str, Any]]]:
    if not (PROJECT_ROOT / "CMakeLists.txt").exists():
        print(f"Error: no CMakeLists.txt found in {PROJECT_ROOT}", file=sys.stderr)
        return 2, []
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    variants = [BuildVariant(f"clang_{sanitize_variant_name(opt)}", opt) for opt in OPTIMIZATION_LEVELS]
    summary: list[dict[str, Any]] = []
    for variant in variants:
        print(f"\n=== {variant.name} ({variant.clang_optimization_flag}) ===")
        try:
            metadata = build_and_benchmark_variant(variant)
        except Exception as exc:
            print(f"failed: {exc}", file=sys.stderr)
            summary.append({"variant": asdict(variant), "failed": True, "error": str(exc)})
            continue
        configure_ok = metadata.configure.returncode == 0
        build_ok = metadata.build.returncode == 0
        benchmark_ok = bool(metadata.benchmark) and all(result.returncode == 0 for result in metadata.benchmark)
        print(f"configure: {'ok' if configure_ok else 'failed'}")
        print(f"build:     {'ok' if build_ok else 'failed'}")
        print(f"benchmark: {'ok' if benchmark_ok else 'failed'}")
        print(f"folder:    {metadata.build_dir}")
        summary.append({
            "variant": asdict(variant),
            "failed": not benchmark_ok,
            "configure_returncode": metadata.configure.returncode,
            "build_returncode": metadata.build.returncode,
            "benchmark_returncodes": [result.returncode for result in metadata.benchmark],
            "total_duration_seconds": metadata.total_duration_seconds,
            "build_dir": metadata.build_dir,
            "metadata_file": str(Path(metadata.build_dir) / "build_metadata.json"),
        })
    write_json(BUILD_ROOT / "summary.json", summary)
    print(f"\nSummary written to: {BUILD_ROOT / 'summary.json'}")
    failed = [result for result in summary if result.get("failed")]
    return (1 if failed else 0), summary


def run_overnight_benchmarks() -> int:
    clang_status, clang_summary = run_build_benchmarks()
    all_summary: list[dict[str, Any]] = [{"variant_type": "clang", **item} for item in clang_summary]
    models = configured_llm_models()
    if models:
        print(f"\nConfigured LLM models: {len(models)}")
        print("LLM target files:", ", ".join(path.name for path in llm_target_source_files()))
        llm_generation_status, llm_results = run_llm_artifact_generation()
        llm_benchmark_summary = benchmark_llm_artifacts(llm_results)
        all_summary.extend(llm_benchmark_summary)
        status = 1 if (clang_status or llm_generation_status or any(item.get("failed") for item in llm_benchmark_summary)) else 0
    else:
        print("\nNo LLM models configured; ran Clang benchmark sweep only.")
        status = clang_status
    write_json(BUILD_ROOT / "summary_all.json", all_summary)
    print(f"Combined summary written to: {BUILD_ROOT / 'summary_all.json'}")
    return status


def main() -> int:
    return run_overnight_benchmarks()


if __name__ == "__main__":
    raise SystemExit(main())
