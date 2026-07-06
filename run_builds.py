#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional


# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent

BUILD_ROOT = PROJECT_ROOT / "benchmark-builds"
LLM_ARTIFACT_ROOT = BUILD_ROOT / "llm-artifacts"

CLANG_C_COMPILER = "clang"
CLANG_CXX_COMPILER = "clang++"

# Set it to None to let CMake use its default generator
CMAKE_GENERATOR: Optional[str] = "Ninja"

OPTIMIZATION_LEVELS = [
    "-O0",
    "-O1",
    "-O2",
    "-O3",
    "-Ofast",
    "-Os",
    "-Oz",
]

# The IR that is sent to the LLM. This is intentionally separate from the
# normal benchmark variants.
LLM_IR_OPTIMIZATION_LEVEL = "-O1"

BENCHMARK_FUNCTIONS = {
    0: "fibonacci",
    1: "format_list",
    2: "repeated_sort",
    3: "count_matches",
    4: "top_words_from_file",
}

CLEAN_BEFORE_BUILD = True

PARALLEL_BUILD_JOBS = os.cpu_count()

RUNNER_EXECUTABLE_NAME = PROJECT_ROOT / "cmake-build-release-llvm-20/librunner/librunner"

# Add arguments here if librunner needs any.
RUNNER_ARGS: list[str] = []

# llama.cpp server configuration. The script can either start one llama-server
# per model, or use an already running OpenAI-compatible endpoint.
LLAMA_SERVER_EXECUTABLE = os.environ.get("LLAMA_SERVER", "llama-server")
LLAMA_HOST = os.environ.get("LLAMA_HOST", "127.0.0.1")
LLAMA_PORT = int(os.environ.get("LLAMA_PORT", "8001"))
LLAMA_BASE_URL = os.environ.get("LLAMA_BASE_URL", f"http://{LLAMA_HOST}:{LLAMA_PORT}").rstrip("/")
LLAMA_API_KEY = os.environ.get("LLAMA_API_KEY", "")
LLAMA_CTX_SIZE = int(os.environ.get("LLAMA_CTX_SIZE", "8192"))
LLAMA_THREADS = int(os.environ.get("LLAMA_THREADS", "12"))
LLAMA_THREADS_BATCH = int(os.environ.get("LLAMA_THREADS_BATCH", "24"))
LLAMA_BATCH_SIZE = int(os.environ.get("LLAMA_BATCH_SIZE", "2048"))
LLAMA_UBATCH_SIZE = int(os.environ.get("LLAMA_UBATCH_SIZE", "512"))
LLAMA_FLASH_ATTN = os.environ.get("LLAMA_FLASH_ATTN", "auto")
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.0"))
LLM_TOP_P = float(os.environ.get("LLM_TOP_P", "1.0"))
LLM_SEED = int(os.environ.get("LLM_SEED", "1234"))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "8192"))
LLAMA_READY_TIMEOUT = int(
    os.environ.get("LLAMA_READY_TIMEOUT", "1800")
)
LLAMA_REQUEST_TIMEOUT = int(
    os.environ.get("LLAMA_REQUEST_TIMEOUT", "10800")
)


# -----------------------------------------------------------------------------
# LLM benchmark configuration
# -----------------------------------------------------------------------------
# Put the old models.json content here. Leave this list empty to run only the
# existing Clang optimization-level benchmarks.
#
# llama.cpp will download/cache GGUF models from Hugging Face via -hf.
# The hf_repo value is passed directly to:
#
#     llama-server -hf <user>/<model>[:quant]
#
# Examples:
# LLM_MODELS = [
#     {
#         "name": "qwen3-1.7b-q8",
#         "hf_repo": "Qwen/Qwen3-1.7B-GGUF:Q8_0",
#         "alias": "qwen3-1.7b-q8",
#     },
#     {
#         "name": "qwen3-4b-q4km",
#         "hf_repo": "Qwen/Qwen3-4B-GGUF:Q4_K_M",
#         "alias": "qwen3-4b-q4km",
#     },
# ]
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

# If true, also asks the model to optimize its first optimized LLVM IR output.
RUN_LLM_SECOND_IR_PASS = False

# The LLM output is still compiled to native code before benchmarking. This flag
# controls that final backend/codegen build, not the IR input sent to the LLM.
LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL = "-O3"


# =============================================================================
# Data structures
# =============================================================================

@dataclass
class BuildVariant:
    name: str
    clang_optimization_flag: str

    # Reserved for future LLM-based variants
    llm_cpp_model: Optional[str] = None
    llm_cpp_prompt: Optional[str] = None
    llm_ir_model: Optional[str] = None
    llm_ir_prompt: Optional[str] = None


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

def run_command(
    command: list[str],
    cwd: Path,
    stdout_file: Path,
    stderr_file: Path,
    env: Optional[dict[str, str]] = None,
) -> CommandResult:
    start = time.perf_counter()

    with stdout_file.open("w", encoding="utf-8") as out, stderr_file.open("w", encoding="utf-8") as err:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            stdout=out,
            stderr=err,
            text=True,
            env=env,
        )

    duration = time.perf_counter() - start

    return CommandResult(
        command=command,
        cwd=str(cwd),
        returncode=completed.returncode,
        duration_seconds=duration,
        stdout_file=str(stdout_file),
        stderr_file=str(stderr_file),
    )


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def sanitize_name(value: str) -> str:
    return (
        value.replace("/", "_")
        .replace("\\", "_")
        .replace("-", "_")
        .replace("+", "plus")
        .replace("=", "_")
        .replace(":", "_")
        .replace(".", "_")
    )


def sanitize_variant_name(opt_flag: str) -> str:
    return sanitize_name(opt_flag).lstrip("_")


def find_libsut(build_dir: Path) -> Optional[Path]:
    candidates = list(build_dir.rglob("libSUT.so"))
    return candidates[0] if candidates else None


def is_executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def try_write_benchmark_json(stdout_file: Path, output_json_file: Path) -> None:
    """
    If librunner prints JSON to stdout, save a parsed copy.
    If it prints plain text, this simply does nothing.
    The raw stdout is always saved.
    """
    text = stdout_file.read_text(encoding="utf-8").strip()

    if not text:
        return

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return

    write_json(output_json_file, parsed)


def find_sut_file(filename: str) -> Path:
    """Find SUT/library.cpp or SUT/library.h, with a flat-layout fallback."""
    candidates = [
        PROJECT_ROOT / "SUT" / filename,
        PROJECT_ROOT / filename,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"Could not find {filename}. Checked: "
        + ", ".join(str(candidate) for candidate in candidates)
    )


def extract_code_block(text: str) -> str:
    """
    Prefer a fenced code block if the model returned one.
    Otherwise return the whole response. This keeps the prompt simple while
    tolerating models that ignore 'code only'.
    """
    marker = "```"
    first = text.find(marker)
    if first == -1:
        return text.strip() + "\n"

    second = text.find(marker, first + len(marker))
    if second == -1:
        return text.strip() + "\n"

    block = text[first + len(marker):second]
    lines = block.splitlines()
    if lines and lines[0].strip().lower() in {"cpp", "c++", "llvm", "llvm-ir", "ir", "ll"}:
        lines = lines[1:]

    return "\n".join(lines).strip() + "\n"


# =============================================================================
# LLM prompting and artifact generation
# =============================================================================

def make_cpp_optimization_prompt(library_h: str, library_cpp: str) -> str:
    return f"""You are an expert C++23 performance engineer.

Task: optimize the implementation in library.cpp for runtime performance.

Hard requirements:
- Preserve the public C ABI exactly as declared in library.h.
- Do not change any function name, parameter type, return type, struct layout, ownership rule, or allocation/freeing convention visible in library.h.
- You may freely restructure the internals of library.cpp: rewrite algorithms, remove helper functions, add helper functions, inline functions, change containers, replace recursion with loops, precompute values, and simplify control flow.
- Preserve observable behavior for all valid inputs expected by the existing API and benchmark runner.
- Preserve the error-handling style of the API: invalid pointer/length combinations and internal exceptions should not escape through the extern "C" functions.
- Returned char* values must still be allocated with malloc-compatible allocation and released by free_string.
- Returned WordCount arrays and WordCount.word strings must still be released correctly by free_word_counts.
- Keep the result as a single complete replacement for library.cpp.
- Do not modify library.h.
- Do not include markdown, commentary, explanations, benchmarking notes, or code fences in your answer.

library.h:
```cpp
{library_h}
```

Current library.cpp:
```cpp
{library_cpp}
```
"""


def make_cpp_compile_fix_prompt(
    library_h: str,
    failed_library_cpp: str,
    compiler_stdout: str,
    compiler_stderr: str,
) -> str:
    return f"""You are an expert C++23 build-fix and performance engineer.

Task: fix this LLM-optimized library.cpp so it compiles successfully.

Hard requirements:
- Return one complete replacement for library.cpp.
- Preserve the public C ABI exactly as declared in library.h.
- Do not change any function name, parameter type, return type, struct layout, ownership rule, or allocation/freeing convention visible in library.h.
- Preserve the intended optimized behavior and runtime-performance focus as much as possible.
- Preserve the error-handling style of the API: invalid pointer/length combinations and internal exceptions should not escape through the extern "C" functions.
- Returned char* values must still be allocated with malloc-compatible allocation and released by free_string.
- Returned WordCount arrays and WordCount.word strings must still be released correctly by free_word_counts.
- Do not modify library.h.
- Do not include markdown, commentary, explanations, benchmarking notes, or code fences in your answer.

library.h:
```cpp
{library_h}
```

Failed library.cpp:
```cpp
{failed_library_cpp}
```

Compiler stdout:
```text
{compiler_stdout}
```

Compiler stderr:
```text
{compiler_stderr}
```
"""


def make_ir_optimization_prompt(library_h: str, llvm_ir: str) -> str:
    return f"""You are an expert LLVM optimizer.

Task: optimize the following LLVM IR for runtime performance.

Hard requirements:
- Return one complete LLVM IR module that can be compiled by clang++/LLVM.
- Preserve the public C ABI exactly as declared in library.h.
- Do not change exported function names, parameter types, return types, struct layout, allocation/freeing convention, or externally observable behavior.
- You may freely restructure internal IR, helper functions, control flow, loops, allocations, and calls if semantics are preserved.
- Preserve compatibility with C++ runtime behavior needed by the original module.
- Do not remove definitions that are required by the public API.
- Do not include markdown, commentary, explanations, benchmarking notes, or code fences in your answer.

library.h public API reference:
```cpp
{library_h}
```

LLVM IR produced from library.cpp with {LLM_IR_OPTIMIZATION_LEVEL}:
```llvm
{llvm_ir}
```
"""


def configured_llm_models() -> list[LlmModelConfig]:
    """Return embedded model configuration from LLM_MODELS."""
    return [LlmModelConfig(**item) for item in LLM_MODELS]


def start_llama_server(model: LlmModelConfig, log_dir: Path) -> subprocess.Popen[str]:
    """Start llama-server for this Hugging Face model."""
    if not model.hf_repo:
        raise ValueError(
            f"LLM model {model.name!r} is missing hf_repo. "
            "Set hf_repo to something like 'Qwen/Qwen3-4B-GGUF:Q4_K_M'."
        )

    log_dir.mkdir(parents=True, exist_ok=True)
    stdout = (log_dir / "llama_server_stdout.txt").open("w", encoding="utf-8")
    stderr = (log_dir / "llama_server_stderr.txt").open("w", encoding="utf-8")

    command = [
        LLAMA_SERVER_EXECUTABLE,
        "-hf",
        model.hf_repo,
        "--alias",
        model.alias or model.name,
        "--host",
        LLAMA_HOST,
        "--port",
        str(LLAMA_PORT),
        "--ctx-size",
        str(LLAMA_CTX_SIZE),
        "--threads",
        str(LLAMA_THREADS),
        "--threads-batch",
        str(LLAMA_THREADS_BATCH),
        "--batch-size",
        str(LLAMA_BATCH_SIZE),
        "--ubatch-size",
        str(LLAMA_UBATCH_SIZE),
        "--flash-attn",
        LLAMA_FLASH_ATTN,
        "--no-webui",
    ]

    print("Starting llama-server:", " ".join(command))
    process = subprocess.Popen(
        command,
        cwd=str(PROJECT_ROOT),
        stdout=stdout,
        stderr=stderr,
        text=True,
    )
    return process

def stop_process(process: Optional[subprocess.Popen[str]]) -> None:
    if process is None:
        return

    if process.poll() is not None:
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


def wait_for_llama_ready(process: subprocess.Popen[str],
                         timeout_seconds: int = LLAMA_READY_TIMEOUT) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Optional[str] = None

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"llama-server exited with code {process.returncode}"
            )
        try:
            http_json("GET", f"{LLAMA_BASE_URL}/health", timeout=5)
            return
        except Exception as exc:  # noqa: BLE001 - transient while server starts
            last_error = str(exc)
            time.sleep(1)

    raise TimeoutError(f"llama-server did not become ready: {last_error}")


def call_llm(model_name: str, prompt: str) -> str:
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": "You are a compiler and C++ optimization assistant. Return only the requested source code.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": LLM_TEMPERATURE,
        "top_p": LLM_TOP_P,
        "seed": LLM_SEED,
        "max_tokens": LLM_MAX_TOKENS,
    }

    response = http_json("POST", f"{LLAMA_BASE_URL}/v1/chat/completions", payload=payload, timeout=LLAMA_REQUEST_TIMEOUT)
    return response["choices"][0]["message"]["content"]


def warm_up_llm(model_name: str, output_dir: Path) -> None:
    prompt = "Optimize this C++ function. Return only code: int f(int x) { return x + 0; }"
    start = time.perf_counter()
    response = call_llm(model_name, prompt)
    duration = time.perf_counter() - start
    (output_dir / "warmup_prompt.txt").write_text(prompt, encoding="utf-8")
    (output_dir / "warmup_response.txt").write_text(response, encoding="utf-8")
    write_json(output_dir / "warmup_metadata.json", {"duration_seconds": duration})


def compile_cpp_artifact_for_check(output_dir: Path, source_file: Path) -> CommandResult:
    """Compile an LLM-produced library.cpp without running benchmarks.

This is used while the model server is still running, so a failed C++ artifact
can be sent back to the same model once for repair before the real benchmark
phase starts.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    libsut_path = output_dir / "libSUT.so"

    include_dirs = [source_file.parent, PROJECT_ROOT / "SUT", PROJECT_ROOT]
    command = [
        CLANG_CXX_COMPILER,
        "-std=c++23",
        LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL,
        "-DNDEBUG",
        "-shared",
        "-fPIC",
    ]
    for include_dir in include_dirs:
        if include_dir.exists():
            command.extend(["-I", str(include_dir)])
    command.extend([str(source_file), "-o", str(libsut_path)])

    return run_command(
        command,
        cwd=PROJECT_ROOT,
        stdout_file=output_dir / "compile_stdout.txt",
        stderr_file=output_dir / "compile_stderr.txt",
    )


def maybe_fix_cpp_compile_failure(
    model_name: str,
    model_display_name: str,
    library_h: str,
    cpp_result: LlmCallResult,
    model_dir: Path,
) -> LlmCallResult:
    """Give the LLM one repair attempt if its optimized C++ does not compile."""
    source_file = Path(cpp_result.output_file)
    check_dir = model_dir / "compile_check_cpp_initial"
    compile_result = compile_cpp_artifact_for_check(check_dir, source_file)
    write_json(check_dir / "compile_metadata.json", asdict(compile_result))

    if compile_result.returncode == 0:
        return cpp_result

    print(f"Optimized C++ from {model_display_name} failed to compile; asking model for one fix attempt")

    compiler_stdout = Path(compile_result.stdout_file).read_text(encoding="utf-8", errors="replace")
    compiler_stderr = Path(compile_result.stderr_file).read_text(encoding="utf-8", errors="replace")
    failed_cpp = source_file.read_text(encoding="utf-8", errors="replace")

    fix_prompt = make_cpp_compile_fix_prompt(
        library_h=library_h,
        failed_library_cpp=failed_cpp,
        compiler_stdout=compiler_stdout,
        compiler_stderr=compiler_stderr,
    )

    prompt_file = model_dir / "prompt_cpp_fix_compile.txt"
    raw_response_file = model_dir / "raw_response_cpp_fix_compile.txt"
    fixed_output_file = model_dir / "optimized_library.fixed.cpp"
    prompt_file.write_text(fix_prompt, encoding="utf-8")

    start = time.perf_counter()
    try:
        response = call_llm(model_name, fix_prompt)
        duration = time.perf_counter() - start
        raw_response_file.write_text(response, encoding="utf-8")
        fixed_output_file.write_text(extract_code_block(response), encoding="utf-8")

        fix_result = LlmCallResult(
            model=model_display_name,
            task="cpp_fix_compile",
            duration_seconds=duration,
            prompt_file=str(prompt_file),
            raw_response_file=str(raw_response_file),
            output_file=str(fixed_output_file),
            success=True,
        )

        recheck_dir = model_dir / "compile_check_cpp_fixed"
        fixed_compile_result = compile_cpp_artifact_for_check(recheck_dir, fixed_output_file)
        write_json(recheck_dir / "compile_metadata.json", asdict(fixed_compile_result))

        if fixed_compile_result.returncode != 0:
            fix_result.success = False
            fix_result.error = (
                "C++ compile-fix attempt still failed. See "
                f"{fixed_compile_result.stderr_file}"
            )
            write_json(model_dir / "result_cpp_fix_compile.json", asdict(fix_result))
            cpp_result.success = False
            cpp_result.error = (
                "Initial optimized C++ failed to compile and the one allowed "
                "LLM repair attempt also failed."
            )
            return cpp_result

        write_json(model_dir / "result_cpp_fix_compile.json", asdict(fix_result))

        # Benchmark the repaired source as the C++ artifact for this model.
        cpp_result.output_file = str(fixed_output_file)
        cpp_result.error = f"Initial C++ failed to compile; using one-shot fixed source from {fixed_output_file}"
        return cpp_result
    except Exception as exc:  # noqa: BLE001
        duration = time.perf_counter() - start
        fix_result = LlmCallResult(
            model=model_display_name,
            task="cpp_fix_compile",
            duration_seconds=duration,
            prompt_file=str(prompt_file),
            raw_response_file=str(raw_response_file),
            output_file=str(fixed_output_file),
            success=False,
            error=str(exc),
        )
        write_json(model_dir / "result_cpp_fix_compile.json", asdict(fix_result))
        cpp_result.success = False
        cpp_result.error = f"Initial optimized C++ failed to compile and repair request failed: {exc}"
        return cpp_result


def generate_o1_llvm_ir(output_dir: Path, library_cpp: Path) -> CommandResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_ir = output_dir / "library_O1.ll"

    include_dirs = [library_cpp.parent, PROJECT_ROOT, PROJECT_ROOT / "SUT"]
    command = [
        CLANG_CXX_COMPILER,
        "-std=c++23",
        LLM_IR_OPTIMIZATION_LEVEL,
        "-DNDEBUG",
        "-fPIC",
        "-S",
        "-emit-llvm",
        "-fno-discard-value-names",
    ]

    for include_dir in include_dirs:
        if include_dir.exists():
            command.extend(["-I", str(include_dir)])

    command.extend([str(library_cpp), "-o", str(output_ir)])

    return run_command(
        command,
        cwd=PROJECT_ROOT,
        stdout_file=output_dir / "generate_ir_stdout.txt",
        stderr_file=output_dir / "generate_ir_stderr.txt",
    )


def run_llm_artifact_generation() -> tuple[int, list[dict[str, Any]]]:
    library_cpp_path = find_sut_file("library.cpp")
    library_h_path = find_sut_file("library.h")
    models = configured_llm_models()

    LLM_ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    input_dir = LLM_ARTIFACT_ROOT / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    library_cpp = library_cpp_path.read_text(encoding="utf-8")
    library_h = library_h_path.read_text(encoding="utf-8")
    shutil.copy2(library_cpp_path, input_dir / "library.cpp")
    shutil.copy2(library_h_path, input_dir / "library.h")

    # The C++ optimization path is independent from the LLVM IR path.  Generate
    # the C++ prompt unconditionally first.  IR generation failure should only
    # disable the IR artifact tasks, not the C++ artifact tasks.
    cpp_prompt = make_cpp_optimization_prompt(library_h=library_h, library_cpp=library_cpp)
    (input_dir / "prompt_cpp_template.txt").write_text(cpp_prompt, encoding="utf-8")

    ir_prompt: Optional[str] = None
    print(f"Generating {LLM_IR_OPTIMIZATION_LEVEL} LLVM IR from: {library_cpp_path}")
    ir_result = generate_o1_llvm_ir(input_dir, library_cpp_path)
    write_json(input_dir / "generate_ir_metadata.json", asdict(ir_result))
    if ir_result.returncode == 0:
        llvm_ir = (input_dir / "library_O1.ll").read_text(encoding="utf-8")
        ir_prompt = make_ir_optimization_prompt(library_h=library_h, llvm_ir=llvm_ir)
        (input_dir / "prompt_ir_template.txt").write_text(ir_prompt, encoding="utf-8")
    else:
        print(
            f"IR generation failed. C++ LLM optimization will still run. See {ir_result.stderr_file}",
            file=sys.stderr,
        )

    all_results: list[dict[str, Any]] = []
    include_ir2 = RUN_LLM_SECOND_IR_PASS

    for model in models:
        model_name = model.alias or model.name
        model_dir = LLM_ARTIFACT_ROOT / sanitize_name(model.name)
        model_dir.mkdir(parents=True, exist_ok=True)

        server_process: Optional[subprocess.Popen[str]] = None
        try:
            server_process = start_llama_server(model, model_dir)
            wait_for_llama_ready(server_process)
            warm_up_llm(model_name, model_dir)

            tasks: list[tuple[str, str, Path]] = [
                ("cpp", cpp_prompt, model_dir / "optimized_library.cpp"),
            ]
            if ir_prompt is not None:
                tasks.append(("ir", ir_prompt, model_dir / "optimized_library.ll"))

            if include_ir2:
                # This pass uses the model's first IR output as input. It is
                # useful later, but keep it opt-in so the base experiment stays simple.
                pass

            for task_name, prompt, output_file in tasks:
                prompt_file = model_dir / f"prompt_{task_name}.txt"
                raw_response_file = model_dir / f"raw_response_{task_name}.txt"
                prompt_file.write_text(prompt, encoding="utf-8")

                print(f"Running {task_name} optimization with {model.name}")
                start = time.perf_counter()
                try:
                    response = call_llm(model_name, prompt)
                    duration = time.perf_counter() - start
                    raw_response_file.write_text(response, encoding="utf-8")
                    output_file.write_text(extract_code_block(response), encoding="utf-8")
                    call_result = LlmCallResult(
                        model=model.name,
                        task=task_name,
                        duration_seconds=duration,
                        prompt_file=str(prompt_file),
                        raw_response_file=str(raw_response_file),
                        output_file=str(output_file),
                        success=True,
                    )

                    if task_name == "cpp":
                        call_result = maybe_fix_cpp_compile_failure(
                            model_name=model_name,
                            model_display_name=model.name,
                            library_h=library_h,
                            cpp_result=call_result,
                            model_dir=model_dir,
                        )
                except Exception as exc:  # noqa: BLE001 - save failure in metadata
                    duration = time.perf_counter() - start
                    call_result = LlmCallResult(
                        model=model.name,
                        task=task_name,
                        duration_seconds=duration,
                        prompt_file=str(prompt_file),
                        raw_response_file=str(raw_response_file),
                        output_file=str(output_file),
                        success=False,
                        error=str(exc),
                    )

                write_json(model_dir / f"result_{task_name}.json", asdict(call_result))
                all_results.append(asdict(call_result))

            if include_ir2:
                first_ir_path = model_dir / "optimized_library.ll"
                if first_ir_path.exists():
                    ir2_prompt = make_ir_optimization_prompt(
                        library_h=library_h,
                        llvm_ir=first_ir_path.read_text(encoding="utf-8"),
                    )
                    prompt_file = model_dir / "prompt_ir2.txt"
                    raw_response_file = model_dir / "raw_response_ir2.txt"
                    output_file = model_dir / "optimized_library_pass2.ll"
                    prompt_file.write_text(ir2_prompt, encoding="utf-8")

                    print(f"Running second IR optimization pass with {model.name}")
                    start = time.perf_counter()
                    try:
                        response = call_llm(model_name, ir2_prompt)
                        duration = time.perf_counter() - start
                        raw_response_file.write_text(response, encoding="utf-8")
                        output_file.write_text(extract_code_block(response), encoding="utf-8")
                        call_result = LlmCallResult(
                            model=model.name,
                            task="ir2",
                            duration_seconds=duration,
                            prompt_file=str(prompt_file),
                            raw_response_file=str(raw_response_file),
                            output_file=str(output_file),
                            success=True,
                        )
                    except Exception as exc:  # noqa: BLE001
                        duration = time.perf_counter() - start
                        call_result = LlmCallResult(
                            model=model.name,
                            task="ir2",
                            duration_seconds=duration,
                            prompt_file=str(prompt_file),
                            raw_response_file=str(raw_response_file),
                            output_file=str(output_file),
                            success=False,
                            error=str(exc),
                        )

                    write_json(model_dir / "result_ir2.json", asdict(call_result))
                    all_results.append(asdict(call_result))
        except Exception as e:
            failure = {
                "model": model.name,
                "task": "model_setup",
                "duration_seconds": 0.0,
                "prompt_file": "",
                "raw_response_file": "",
                "output_file": "",
                "success": False,
                "error": str(e),
            }
            write_json(model_dir / "result_model_setup.json", failure)
            all_results.append(failure)
            continue
        finally:
            stop_process(server_process)

    if ir_prompt is None:
        all_results.append(
            {
                "model": "<input>",
                "task": "ir_input_generation",
                "duration_seconds": ir_result.duration_seconds,
                "prompt_file": "",
                "raw_response_file": "",
                "output_file": str(input_dir / "library_O1.ll"),
                "success": False,
                "error": f"IR generation failed. See {ir_result.stderr_file}",
            }
        )

    write_json(LLM_ARTIFACT_ROOT / "summary.json", all_results)
    print(f"LLM artifacts written to: {LLM_ARTIFACT_ROOT}")

    return (0 if all(item.get("success") for item in all_results) else 1), all_results

def run_benchmarks_for_lib(build_dir: Path, libsut_path: Path) -> list[CommandResult]:
    env = os.environ.copy()
    old_ld_library_path = env.get("LD_LIBRARY_PATH")
    if old_ld_library_path:
        env["LD_LIBRARY_PATH"] = f"{libsut_path.parent}:{old_ld_library_path}"
    else:
        env["LD_LIBRARY_PATH"] = str(libsut_path.parent)

    benchmark_results: list[CommandResult] = []

    for function_id, function_name in BENCHMARK_FUNCTIONS.items():
        benchmark_stdout = build_dir / f"benchmark_{function_id}_{function_name}_stdout.txt"
        benchmark_stderr = build_dir / f"benchmark_{function_id}_{function_name}_stderr.txt"

        benchmark_command = [
            str(RUNNER_EXECUTABLE_NAME),
            str(libsut_path),
            str(function_id),
            *RUNNER_ARGS,
        ]

        result = run_command(
            benchmark_command,
            cwd=build_dir,
            stdout_file=benchmark_stdout,
            stderr_file=benchmark_stderr,
            env=env,
        )

        benchmark_results.append(result)
        try_write_benchmark_json(
            stdout_file=benchmark_stdout,
            output_json_file=build_dir / f"benchmark_{function_id}_{function_name}_results.json",
        )

    return benchmark_results


def build_and_benchmark_direct_llm_variant(
    variant_name: str,
    source_file: Path,
    source_kind: str,
    model_name: str,
    llm_task: str,
) -> DirectBuildMetadata:
    """Compile an LLM-produced C++ or LLVM IR artifact into libSUT.so and benchmark it."""
    build_dir = BUILD_ROOT / variant_name
    if CLEAN_BEFORE_BUILD and build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    total_start = time.perf_counter()
    libsut_path = build_dir / "libSUT.so"

    if source_kind == "cpp":
        include_dirs = [source_file.parent, PROJECT_ROOT / "SUT", PROJECT_ROOT]
        compile_command = [
            CLANG_CXX_COMPILER,
            "-std=c++23",
            LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL,
            "-DNDEBUG",
            "-shared",
            "-fPIC",
        ]
        for include_dir in include_dirs:
            if include_dir.exists():
                compile_command.extend(["-I", str(include_dir)])
        compile_command.extend([str(source_file), "-o", str(libsut_path)])
    elif source_kind == "ir":
        compile_command = [
            CLANG_CXX_COMPILER,
            LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL,
            "-shared",
            "-fPIC",
            str(source_file),
            "-o",
            str(libsut_path),
        ]
    else:
        raise ValueError(f"Unsupported source_kind: {source_kind}")

    compile_result = run_command(
        compile_command,
        cwd=PROJECT_ROOT,
        stdout_file=build_dir / "compile_stdout.txt",
        stderr_file=build_dir / "compile_stderr.txt",
    )

    benchmark_results: list[CommandResult] = []
    if compile_result.returncode == 0 and libsut_path.exists():
        benchmark_results = run_benchmarks_for_lib(build_dir=build_dir, libsut_path=libsut_path)

    metadata = DirectBuildMetadata(
        variant_name=variant_name,
        source_kind=source_kind,
        source_file=str(source_file),
        build_dir=str(build_dir),
        compile=compile_result,
        benchmark=benchmark_results,
        libsut_path=str(libsut_path) if libsut_path.exists() else None,
        runner_path=str(RUNNER_EXECUTABLE_NAME),
        total_duration_seconds=time.perf_counter() - total_start,
        model=model_name,
        llm_task=llm_task,
    )
    write_json(build_dir / "build_metadata.json", asdict(metadata))
    return metadata


def benchmark_llm_artifacts(llm_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build and benchmark all successful LLM outputs."""
    benchmark_summary: list[dict[str, Any]] = []

    for result in llm_results:
        if not result.get("success"):
            continue

        task = result["task"]
        if task == "cpp":
            source_kind = "cpp"
        elif task in {"ir", "ir2"}:
            source_kind = "ir"
        else:
            continue

        output_file = Path(result["output_file"])
        if not output_file.exists():
            benchmark_summary.append({**result, "failed": True, "error": "LLM output file missing"})
            continue

        model_name = result["model"]
        variant_name = f"llm_{sanitize_name(model_name)}_{sanitize_name(task)}"
        print()
        print(f"=== {variant_name} ({output_file.name}) ===")

        try:
            metadata = build_and_benchmark_direct_llm_variant(
                variant_name=variant_name,
                source_file=output_file,
                source_kind=source_kind,
                model_name=model_name,
                llm_task=task,
            )
            compile_ok = metadata.compile.returncode == 0
            benchmark_ok = bool(metadata.benchmark) and all(
                item.returncode == 0 for item in metadata.benchmark
            )
            print(f"compile:   {'ok' if compile_ok else 'failed'}")
            print(f"benchmark: {'ok' if benchmark_ok else 'failed'}")
            print(f"folder:    {metadata.build_dir}")
            benchmark_summary.append(
                {
                    "variant_type": "llm",
                    "model": model_name,
                    "task": task,
                    "failed": not benchmark_ok,
                    "compile_returncode": metadata.compile.returncode,
                    "benchmark_returncodes": [item.returncode for item in metadata.benchmark],
                    "total_duration_seconds": metadata.total_duration_seconds,
                    "build_dir": metadata.build_dir,
                    "metadata_file": str(Path(metadata.build_dir) / "build_metadata.json"),
                    "source_file": str(output_file),
                }
            )
        except Exception as exc:  # noqa: BLE001
            print(f"failed: {exc}", file=sys.stderr)
            benchmark_summary.append(
                {
                    "variant_type": "llm",
                    "model": model_name,
                    "task": task,
                    "failed": True,
                    "error": str(exc),
                    "source_file": str(output_file),
                }
            )

    write_json(BUILD_ROOT / "llm_benchmark_summary.json", benchmark_summary)
    return benchmark_summary


# =============================================================================
# Build and benchmark
# =============================================================================

def build_and_benchmark_variant(variant: BuildVariant) -> BuildMetadata:
    build_dir = BUILD_ROOT / variant.name

    if CLEAN_BEFORE_BUILD and build_dir.exists():
        shutil.rmtree(build_dir)

    build_dir.mkdir(parents=True, exist_ok=True)

    total_start = time.perf_counter()

    configure_command = [
        "cmake",
        "-S",
        str(PROJECT_ROOT),
        "-B",
        str(build_dir),
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

    configure_result = run_command(
        configure_command,
        cwd=PROJECT_ROOT,
        stdout_file=build_dir / "configure_stdout.txt",
        stderr_file=build_dir / "configure_stderr.txt",
    )

    build_result = CommandResult(
        command=[],
        cwd=str(PROJECT_ROOT),
        returncode=-1,
        duration_seconds=0.0,
        stdout_file=str(build_dir / "build_stdout.txt"),
        stderr_file=str(build_dir / "build_stderr.txt"),
    )

    benchmark_results: list[CommandResult] = []
    libsut_path: Optional[Path] = None
    runner_path: Optional[Path] = None

    if configure_result.returncode == 0:
        build_command = [
            "cmake",
            "--build",
            str(build_dir),
        ]

        if PARALLEL_BUILD_JOBS is not None:
            build_command.extend(["--parallel", str(PARALLEL_BUILD_JOBS)])

        build_result = run_command(
            build_command,
            cwd=PROJECT_ROOT,
            stdout_file=build_dir / "build_stdout.txt",
            stderr_file=build_dir / "build_stderr.txt",
        )

    if build_result.returncode == 0:
        libsut_path = find_libsut(build_dir)

        env = os.environ.copy()

        # Help librunner find libSUT.so.
        if libsut_path is not None:
            old_ld_library_path = env.get("LD_LIBRARY_PATH")
            if old_ld_library_path:
                env["LD_LIBRARY_PATH"] = f"{libsut_path.parent}:{old_ld_library_path}"
            else:
                env["LD_LIBRARY_PATH"] = str(libsut_path.parent)

        benchmark_results = []

        for function_id, function_name in BENCHMARK_FUNCTIONS.items():
            benchmark_stdout = build_dir / f"benchmark_{function_id}_{function_name}_stdout.txt"
            benchmark_stderr = build_dir / f"benchmark_{function_id}_{function_name}_stderr.txt"

            benchmark_command = [
                str(RUNNER_EXECUTABLE_NAME),
                str(libsut_path),
                str(function_id),
                *RUNNER_ARGS,
            ]

            result = run_command(
                benchmark_command,
                cwd=build_dir,
                stdout_file=benchmark_stdout,
                stderr_file=benchmark_stderr,
                env=env,
            )

            benchmark_results.append(result)

            try_write_benchmark_json(
                stdout_file=benchmark_stdout,
                output_json_file=build_dir / f"benchmark_{function_id}_{function_name}_results.json",
            )

    total_duration = time.perf_counter() - total_start

    metadata = BuildMetadata(
        variant=variant,
        project_root=str(PROJECT_ROOT),
        build_dir=str(build_dir),
        c_compiler=CLANG_C_COMPILER,
        cxx_compiler=CLANG_CXX_COMPILER,
        cmake_generator=CMAKE_GENERATOR,
        configure=configure_result,
        build=build_result,
        benchmark=benchmark_results,
        libsut_path=str(libsut_path) if libsut_path else None,
        runner_path=str(runner_path) if runner_path else None,
        total_duration_seconds=total_duration,
    )

    write_json(build_dir / "build_metadata.json", asdict(metadata))

    return metadata


def run_build_benchmarks() -> tuple[int, list[dict[str, Any]]]:
    if not (PROJECT_ROOT / "CMakeLists.txt").exists():
        print(f"Error: no CMakeLists.txt found in {PROJECT_ROOT}", file=sys.stderr)
        return 2, []

    BUILD_ROOT.mkdir(parents=True, exist_ok=True)

    variants = [
        BuildVariant(
            name=f"clang_{sanitize_variant_name(opt)}",
            clang_optimization_flag=opt,
        )
        for opt in OPTIMIZATION_LEVELS
    ]

    summary = []

    for variant in variants:
        print()
        print(f"=== {variant.name} ({variant.clang_optimization_flag}) ===")

        try:
            metadata = build_and_benchmark_variant(variant)
        except Exception as exc:
            print(f"failed: {exc}", file=sys.stderr)
            summary.append(
                {
                    "variant": asdict(variant),
                    "failed": True,
                    "error": str(exc),
                }
            )
            continue

        configure_ok = metadata.configure.returncode == 0
        build_ok = metadata.build.returncode == 0
        benchmark_ok = bool(metadata.benchmark) and all(
            result.returncode == 0 for result in metadata.benchmark
        )

        print(f"configure: {'ok' if configure_ok else 'failed'}")
        print(f"build:     {'ok' if build_ok else 'failed'}")
        print(f"benchmark: {'ok' if benchmark_ok else 'failed'}")
        print(f"folder:    {metadata.build_dir}")

        summary.append(
            {
                "variant": asdict(variant),
                "failed": not benchmark_ok,
                "configure_returncode": metadata.configure.returncode,
                "build_returncode": metadata.build.returncode,
                "benchmark_returncodes": [
                    result.returncode for result in metadata.benchmark
                ],
                "total_duration_seconds": metadata.total_duration_seconds,
                "build_dir": metadata.build_dir,
                "metadata_file": str(Path(metadata.build_dir) / "build_metadata.json"),
            }
        )

    summary_file = BUILD_ROOT / "summary.json"
    write_json(summary_file, summary)

    print()
    print(f"Summary written to: {summary_file}")

    failed = [result for result in summary if result.get("failed")]
    return (1 if failed else 0), summary


def run_overnight_benchmarks() -> int:
    clang_status, clang_summary = run_build_benchmarks()
    all_summary: list[dict[str, Any]] = [
        {"variant_type": "clang", **item} for item in clang_summary
    ]

    models = configured_llm_models()
    if models:
        print()
        print(f"Configured LLM models: {len(models)}")
        llm_generation_status, llm_results = run_llm_artifact_generation()
        llm_benchmark_summary = benchmark_llm_artifacts(llm_results)
        all_summary.extend(llm_benchmark_summary)
        status = 1 if (
            clang_status
            or llm_generation_status
            or any(item.get("failed") for item in llm_benchmark_summary)
        ) else 0
    else:
        print()
        print("No LLM models configured; ran Clang benchmark sweep only.")
        status = clang_status

    write_json(BUILD_ROOT / "summary_all.json", all_summary)
    print(f"Combined summary written to: {BUILD_ROOT / 'summary_all.json'}")
    return status


def main() -> int:
    return run_overnight_benchmarks()


if __name__ == "__main__":
    raise SystemExit(main())
