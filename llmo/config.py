import os
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUT_DIR = PROJECT_ROOT / "SUT"
BUILD_ROOT = PROJECT_ROOT / "benchmark-builds"

CLANG_C_COMPILER = os.environ.get("CLANG_C_COMPILER", "clang")
CLANG_CXX_COMPILER = os.environ.get("CLANG_CXX_COMPILER", "clang++")
LLVM_OPT_TOOL = os.environ.get("LLVM_OPT_TOOL", "opt")
LLVM_AS_TOOL = os.environ.get("LLVM_AS_TOOL", "llvm-as")
LLVM_EXTRACT_TOOL = os.environ.get("LLVM_EXTRACT_TOOL", "llvm-extract")
LLVM_LINK_TOOL = os.environ.get("LLVM_LINK_TOOL", "llvm-link")
CMAKE_GENERATOR: Optional[str] = "Ninja"

OPTIMIZATION_LEVELS = ["-O0", "-O1", "-O2", "-O3", "-Ofast", "-Os", "-Oz"]
LLM_IR_OPTIMIZATION_LEVEL = os.environ.get("LLM_IR_OPTIMIZATION_LEVEL", "-O1")
LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL = os.environ.get("LLM_OUTPUT_COMPILE_OPTIMIZATION_LEVEL", "-O3")

BENCHMARK_FUNCTIONS = {
    0: "fibonacci",
    1: "format_list",
    2: "repeated_sort",
    3: "count_matches",
    4: "top_words_from_file",
}

FUNCTION_TO_BENCHMARK_ID = {name: function_id for function_id, name in BENCHMARK_FUNCTIONS.items()}

REQUIRED_ABI_SYMBOLS = [
    "fibonacci",
    "format_list",
    "free_string",
    "repeated_sort",
    "count_matches",
    "top_words_from_file",
    "free_word_counts",
]

DEFAULT_LLM_TARGET_FILES = [
    "fibonacci.cpp",
    "format_list.cpp",
    "repeated_sort.cpp",
    "count_matches.cpp",
    "top_words_from_file.cpp",
]

CLEAN_BEFORE_BUILD = os.environ.get("CLEAN_BEFORE_BUILD", "1") != "0"
PARALLEL_BUILD_JOBS = os.cpu_count()
RUNNER_EXECUTABLE_NAME = Path(os.environ.get("RUNNER_EXECUTABLE", str(PROJECT_ROOT / "cmake-build-release-llvm-20/librunner/librunner")))
RUNNER_ARGS: list[str] = []

IR_VERIFY_TIMEOUT_SECONDS = int(os.environ.get("IR_VERIFY_TIMEOUT_SECONDS", "120"))
LLM_COMPILE_TIMEOUT_SECONDS = int(os.environ.get("LLM_COMPILE_TIMEOUT_SECONDS", "300"))
BENCHMARK_TIMEOUT_SECONDS = int(os.environ.get("BENCHMARK_TIMEOUT_SECONDS", "900"))

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

LLM_MODELS = [
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
        "name": "llm-compiler-7b-q4km",
        "hf_repo": "second-state/llm-compiler-7b-GGUF:Q4_K_M",
        "alias": "llm-compiler-7b-q4km",
    },
    {
        "name": "llm-compiler-13b-q4km",
        "hf_repo": "second-state/llm-compiler-13b-GGUF:Q4_K_M",
        "alias": "llm-compiler-13b-q4km",
    },
    {
        "name": "ministral-3-14b-instruct-q4km",
        "hf_repo": "mistralai/Ministral-3-14B-Instruct-2512-GGUF:Q4_K_M",
        "alias": "ministral-3-14b-instruct-q4km",
    },
    {
        "name": "gpt-oss-20b-mxfp4",
        "hf_repo": "ggml-org/gpt-oss-20b-GGUF:MXFP4",
        "alias": "gpt-oss-20b-mxfp4",
    },
    {
        "name": "devstral-small-2-24b-q4km",
        "hf_repo": "unsloth/Devstral-Small-2-24B-Instruct-2512-GGUF:Q4_K_M",
        "alias": "devstral-small-2-24b-q4km",
    },
]
