from __future__ import annotations
import json
import subprocess
import time
import urllib.request
import urllib.error
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Optional, List, Dict
from .config import (
    LLAMA_SERVER_EXECUTABLE, LLAMA_HOST, LLAMA_PORT, LLAMA_CTX_SIZE,
    LLAMA_THREADS, LLAMA_THREADS_BATCH, LLAMA_BATCH_SIZE, LLAMA_UBATCH_SIZE,
    LLAMA_FLASH_ATTN, PROJECT_ROOT, LLAMA_API_KEY, LLAMA_BASE_URL,
    LLM_TEMPERATURE, LLM_TOP_P, LLM_SEED, LLM_MAX_TOKENS, LLAMA_REQUEST_TIMEOUT,
    LLAMA_READY_TIMEOUT
)
from .command import write_json

EFFECTIVE_LLAMA_CTX_SIZE = LLAMA_CTX_SIZE

@dataclass
class ChatCompletionResult:
    content: str
    finish_reason: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    raw_response: Dict[str, Any]

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

def start_llama_server(model: LlmModelConfig, log_dir: Path) -> tuple[subprocess.Popen[str], list[str]]:
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
        "--parallel", "1",
        "--threads", str(LLAMA_THREADS),
        "--threads-batch", str(LLAMA_THREADS_BATCH),
        "--batch-size", str(LLAMA_BATCH_SIZE),
        "--ubatch-size", str(LLAMA_UBATCH_SIZE),
        "--flash-attn", LLAMA_FLASH_ATTN,
        "--no-webui",
    ]
    print("Starting llama-server:", " ".join(command))
    process = subprocess.Popen(command, cwd=str(PROJECT_ROOT), stdout=stdout, stderr=stderr, text=True)
    return process, command

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
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
        return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Response body: {error_body}")
        raise
    except Exception:
        raise

def wait_for_llama_ready(process: subprocess.Popen[str], log_dir: Optional[Path] = None, timeout_seconds: int = LLAMA_READY_TIMEOUT) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Optional[str] = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"llama-server exited with code {process.returncode}")
        try:
            http_json("GET", f"{LLAMA_BASE_URL}/health", timeout=5)
            if log_dir:
                detect_effective_context(log_dir)
            return
        except Exception as exc:
            last_error = str(exc)
            time.sleep(1)
    raise TimeoutError(f"llama-server did not become ready: {last_error}")

def detect_effective_context(log_dir: Path) -> int:
    global EFFECTIVE_LLAMA_CTX_SIZE
    
    requested = LLAMA_CTX_SIZE
    slots_ctxs = []
    props_ctx = None
    log_slot_ctx = None
    log_train_ctx = None
    
    # 1. GET /slots
    try:
        slots = http_json("GET", f"{LLAMA_BASE_URL}/slots", timeout=5)
        if isinstance(slots, list):
            slots_ctxs = [int(s["n_ctx"]) for s in slots if int(s.get("n_ctx", 0)) > 0]
    except Exception:
        pass
    
    # 2. GET /props
    try:
        props = http_json("GET", f"{LLAMA_BASE_URL}/props", timeout=5)
        if "default_generation_settings" in props and "n_ctx" in props["default_generation_settings"]:
            props_ctx = int(props["default_generation_settings"]["n_ctx"])
        elif "n_ctx" in props:
            props_ctx = int(props["n_ctx"])
    except Exception:
        pass
        
    # 3. Parse logs
    stderr_path = log_dir / "llama_server_stderr.txt"
    if stderr_path.exists():
        content = stderr_path.read_text(encoding="utf-8", errors="replace")
        
        slot_match = re.search(r"slot\s+\d+,\s+n_ctx\s+(\d+)", content, re.MULTILINE)
        if slot_match:
            log_slot_ctx = int(slot_match.group(1))
        else:
            slot_match = re.search(r"\"n_ctx\":\s*(\d+)", content)
            if slot_match:
                log_slot_ctx = int(slot_match.group(1))
        
        train_match = re.search(r"llm_load_print_meta: n_ctx_train\s+=\s+(\d+)", content)
        if train_match:
            log_train_ctx = int(train_match.group(1))

    # Selection logic following priority
    effective = requested
    source = "fallback (requested context)"
    
    if slots_ctxs:
        effective = min(slots_ctxs)
        source = "/slots"
    elif props_ctx is not None:
        effective = props_ctx
        source = "/props"
    elif log_slot_ctx is not None:
        effective = log_slot_ctx
        source = "startup-log n_ctx_slot"
    elif log_train_ctx is not None:
        effective = min(requested, log_train_ctx)
        source = "min(requested, n_ctx_train)"
    else:
        print("WARNING: Could not detect effective context size from server. Falling back to requested size.")

    # Logging
    print(f"Requested context : {requested}")
    if slots_ctxs:
        print(f"Parallel slots    : {len(slots_ctxs)}")
        print(f"Slot contexts     : {slots_ctxs}")
    
    if log_train_ctx is not None and log_train_ctx < requested and not slots_ctxs:
        print(f"Model context     : {log_train_ctx}")

    print(f"Effective context : {effective} (from {source})")
    
    EFFECTIVE_LLAMA_CTX_SIZE = effective
    return effective

def call_llm(
    model_name: str,
    prompt: str,
    system_prompt: str = "You are a compiler and C++ optimization assistant. Return only the requested source code.",
    max_tokens: int = LLM_MAX_TOKENS,
    temperature: float = LLM_TEMPERATURE,
    seed: int = LLM_SEED
) -> ChatCompletionResult:
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "top_p": LLM_TOP_P,
        "seed": seed,
        "max_tokens": max_tokens,
    }
    response = http_json("POST", f"{LLAMA_BASE_URL}/v1/chat/completions", payload, timeout=LLAMA_REQUEST_TIMEOUT)
    
    choice = response["choices"][0]
    usage = response.get("usage", {})
    
    return ChatCompletionResult(
        content=choice["message"]["content"],
        finish_reason=choice.get("finish_reason"),
        prompt_tokens=usage.get("prompt_tokens"),
        completion_tokens=usage.get("completion_tokens"),
        total_tokens=usage.get("total_tokens"),
        raw_response=response
    )

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

@dataclass
class TokenBudget:
    effective_context_size: int
    prompt_tokens: int
    available_output_tokens: int
    can_fit_requested_maximum: bool
    can_fit_minimum_expected_output: bool
    minimum_expected_output_tokens: int
    requested_max_tokens: int

def calculate_token_budget(
    prompt: str,
    system_prompt: str,
    requested_max_tokens: int,
    minimum_expected_output_tokens: int = 4096,
    safety_margin: int = 1024
) -> TokenBudget:
    prompt_tokens = count_tokens(prompt) + count_tokens(system_prompt) + 50 # Add some overhead for template
    effective_context = EFFECTIVE_LLAMA_CTX_SIZE
    
    # Available for completion
    available = max(0, effective_context - prompt_tokens - safety_margin)
    
    can_fit_requested_maximum = available >= requested_max_tokens
    can_fit_minimum_expected_output = available >= minimum_expected_output_tokens
    
    return TokenBudget(
        effective_context_size=effective_context,
        prompt_tokens=prompt_tokens,
        available_output_tokens=available,
        can_fit_requested_maximum=can_fit_requested_maximum,
        can_fit_minimum_expected_output=can_fit_minimum_expected_output,
        minimum_expected_output_tokens=minimum_expected_output_tokens,
        requested_max_tokens=requested_max_tokens
    )

def warm_up_llm(model_name: str, output_dir: Path) -> None:
    prompt = "Optimize this C++ function. Return only code: int f(int x) { return x + 0; }"
    start = time.perf_counter()
    response = call_llm(model_name, prompt)
    duration = time.perf_counter() - start
    (output_dir / "warmup_prompt.txt").write_text(prompt, encoding="utf-8")
    (output_dir / "warmup_response.txt").write_text(response.content, encoding="utf-8")
    write_json(output_dir / "warmup_metadata.json", {"duration_seconds": duration})

def save_llm_call(target_dir: Path, name: str, result: ChatCompletionResult) -> str:
    filename = f"{name}_response.json"
    path = target_dir / filename
    write_json(path, result.raw_response)
    return filename
