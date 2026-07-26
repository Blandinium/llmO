import json
import os
from pathlib import Path
from typing import Any
from .command import run_command, write_json, CommandResult
from .config import BENCHMARK_FUNCTIONS, RUNNER_EXECUTABLE_NAME, BENCHMARK_TIMEOUT_SECONDS, RUNNER_ARGS, FUNCTION_TO_BENCHMARK_ID

def parse_scalar_value(value: str) -> Any:
    value = value.strip()
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if lower in {"", "null", "none"}:
        return None if lower in {"null", "none"} else ""
    try:
        if any(ch in value for ch in ".eE"):
            return float(value)
        return int(value, 10)
    except ValueError:
        return value

def parse_key_value_lines(text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        parsed[key] = parse_scalar_value(value)
    return parsed

def try_write_benchmark_json(stdout_file: Path, output_json_file: Path) -> None:
    text = stdout_file.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = parse_key_value_lines(text)

    if parsed:
        write_json(output_json_file, parsed)

def run_benchmarks_for_lib(build_dir: Path, libsut_path: Path, target_function_name: str = None, run_all: bool = True) -> list[CommandResult]:
    env = os.environ.copy()
    old_ld_library_path = env.get("LD_LIBRARY_PATH")
    env["LD_LIBRARY_PATH"] = f"{libsut_path.parent}:{old_ld_library_path}" if old_ld_library_path else str(libsut_path.parent)
    
    if run_all or target_function_name is None:
        selected = list(BENCHMARK_FUNCTIONS.items())
    else:
        function_id = FUNCTION_TO_BENCHMARK_ID[target_function_name]
        selected = [(function_id, target_function_name)]

    benchmark_results: list[CommandResult] = []
    for function_id, function_name in selected:
        stdout = build_dir / f"benchmark_{function_id}_{function_name}_stdout.txt"
        stderr = build_dir / f"benchmark_{function_id}_{function_name}_stderr.txt"
        command = [str(RUNNER_EXECUTABLE_NAME), str(libsut_path), str(function_id), *RUNNER_ARGS]
        result = run_command(command, build_dir, stdout, stderr, env, timeout_seconds=BENCHMARK_TIMEOUT_SECONDS)
        benchmark_results.append(result)
        try_write_benchmark_json(stdout, build_dir / f"benchmark_{function_id}_{function_name}_results.json")
    return benchmark_results
