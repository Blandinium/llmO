from __future__ import annotations
import json
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, List
from .config import (
    LLAMA_SERVER_EXECUTABLE, LLAMA_HOST, LLAMA_PORT, LLAMA_CTX_SIZE,
    LLAMA_THREADS, LLAMA_THREADS_BATCH, LLAMA_BATCH_SIZE, LLAMA_UBATCH_SIZE,
    LLAMA_FLASH_ATTN, PROJECT_ROOT, LLAMA_API_KEY, LLAMA_BASE_URL,
    LLM_TEMPERATURE, LLM_TOP_P, LLM_SEED, LLM_MAX_TOKENS, LLAMA_REQUEST_TIMEOUT,
    LLAMA_READY_TIMEOUT
)
from .command import write_json

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

def call_llm(model_name: str, prompt: str, system_prompt: str = "You are a compiler and C++ optimization assistant. Return only the requested source code.") -> str:
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": LLM_TEMPERATURE,
        "top_p": LLM_TOP_P,
        "seed": LLM_SEED,
        "max_tokens": LLM_MAX_TOKENS,
    }
    response = http_json("POST", f"{LLAMA_BASE_URL}/v1/chat/completions", payload, timeout=LLAMA_REQUEST_TIMEOUT)
    return response["choices"][0]["message"]["content"]

def tokenize(text: str) -> List[int]:
    try:
        payload = {"content": text}
        response = http_json("POST", f"{LLAMA_BASE_URL}/tokenize", payload, timeout=60)
        return response.get("tokens", [])
    except Exception:
        return []

def estimate_tokens(text: str) -> int:
    # Fallback estimator: 4 chars per token is a common rule of thumb for code/technical text
    # We use 3.5 to be more conservative (more tokens estimated)
    return max(1, len(text) // 3)

def count_tokens(text: str) -> int:
    tokens = tokenize(text)
    if tokens:
        return len(tokens)
    return estimate_tokens(text)

def warm_up_llm(model_name: str, output_dir: Path) -> None:
    prompt = "Optimize this C++ function. Return only code: int f(int x) { return x + 0; }"
    start = time.perf_counter()
    response = call_llm(model_name, prompt)
    duration = time.perf_counter() - start
    (output_dir / "warmup_prompt.txt").write_text(prompt, encoding="utf-8")
    (output_dir / "warmup_response.txt").write_text(response, encoding="utf-8")
    write_json(output_dir / "warmup_metadata.json", {"duration_seconds": duration})
