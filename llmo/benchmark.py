from dataclasses import dataclass
import json
import os
import statistics
import random
from pathlib import Path
from typing import Any, List, Dict, Optional, Tuple
from .command import run_command, write_json, CommandResult
from .config import BENCHMARK_FUNCTIONS, RUNNER_EXECUTABLE_NAME, BENCHMARK_TIMEOUT_SECONDS, RUNNER_ARGS, FUNCTION_TO_BENCHMARK_ID

@dataclass
class BenchmarkRunResult:
    command_result: CommandResult
    function_id: int
    function_name: str
    iteration: int
    parsed_result: dict[str, Any] | None

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

def try_parse_benchmark_result(stdout_file: Path) -> Optional[dict[str, Any]]:
    if not stdout_file.exists():
        return None
    text = stdout_file.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return parse_key_value_lines(text)

def try_write_benchmark_json(stdout_file: Path, output_json_file: Path) -> None:
    parsed = try_parse_benchmark_result(stdout_file)
    if parsed:
        write_json(output_json_file, parsed)

def run_benchmarks_for_lib(build_dir: Path, libsut_path: Path, target_function_name: str = None, run_all: bool = True, iteration: int = 0) -> list[BenchmarkRunResult]:
    env = os.environ.copy()
    old_ld_library_path = env.get("LD_LIBRARY_PATH")
    env["LD_LIBRARY_PATH"] = f"{libsut_path.parent}:{old_ld_library_path}" if old_ld_library_path else str(libsut_path.parent)
    
    if run_all or target_function_name is None:
        selected = list(BENCHMARK_FUNCTIONS.items())
    else:
        function_id = FUNCTION_TO_BENCHMARK_ID[target_function_name]
        selected = [(function_id, target_function_name)]

    benchmark_results: list[BenchmarkRunResult] = []
    for function_id, function_name in selected:
        suffix = f"_iter{iteration}" if iteration > 0 else ""
        stdout = build_dir / f"benchmark_{function_id}_{function_name}{suffix}_stdout.txt"
        stderr = build_dir / f"benchmark_{function_id}_{function_name}{suffix}_stderr.txt"
        command = [str(RUNNER_EXECUTABLE_NAME), str(libsut_path), str(function_id), *RUNNER_ARGS]
        result = run_command(command, build_dir, stdout, stderr, env, timeout_seconds=BENCHMARK_TIMEOUT_SECONDS)
        
        parsed = None
        if result.returncode == 0:
            parsed = try_parse_benchmark_result(stdout)
            if parsed:
                try_write_benchmark_json(stdout, build_dir / f"benchmark_{function_id}_{function_name}{suffix}_results.json")
        
        benchmark_results.append(BenchmarkRunResult(
            command_result=result,
            function_id=function_id,
            function_name=function_name,
            iteration=iteration,
            parsed_result=parsed
        ))
    return benchmark_results

def calculate_benchmark_statistics(results: List[Dict[str, Any]], expected_count: int = 0) -> Dict[str, Any]:
    if not results:
        return {}
    
    cps_values = [r.get("calls_per_second", 0.0) for r in results if isinstance(r.get("calls_per_second"), (int, float)) and r.get("calls_per_second", 0.0) > 0]
    wall_times = [r.get("wall_time_s", 0.0) for r in results if isinstance(r.get("wall_time_s"), (int, float))]
    
    if not cps_values:
        return {}
    
    stats = {
        "median_calls_per_second": statistics.median(cps_values),
        "min_calls_per_second": min(cps_values),
        "max_calls_per_second": max(cps_values),
        "median_wall_time": statistics.median(wall_times) if wall_times else 0.0,
        "count": len(cps_values),
        "expected_count": expected_count,
        "raw_results": results
    }
    
    if expected_count > 0 and len(cps_values) < expected_count:
        stats["incomplete"] = True
    
    if len(cps_values) > 1:
        stats["stdev_calls_per_second"] = statistics.stdev(cps_values)
        # Median Absolute Deviation (MAD)
        median = stats["median_calls_per_second"]
        stats["mad_calls_per_second"] = statistics.median([abs(x - median) for x in cps_values])
        
    return stats

def classify_performance(candidate_stats: Dict[str, Any], baseline_stats: Dict[str, Any], noise_threshold: float = 0.02) -> str:
    c_cps = candidate_stats.get("median_calls_per_second", 0.0)
    b_cps = baseline_stats.get("median_calls_per_second", 0.0)
    
    if b_cps <= 0:
        return "unknown"
    
    improvement = (c_cps - b_cps) / b_cps
    
    if improvement > noise_threshold:
        return "improved"
    if improvement < -noise_threshold:
        return "regressed"
    return "unchanged_within_noise"

def run_benchmarks_paired(
    candidate_lib: Path,
    baseline_lib: Path,
    target_name: str,
    repetitions: int = 3,
    seed: int = 42
) -> Tuple[Dict[str, Any], Dict[str, Any], List[str]]:
    rng = random.Random(seed)
    
    baseline_results = []
    candidate_results = []
    
    # Paired sequence
    order = []
    for i in range(repetitions):
        pair = ["baseline", "candidate"]
        rng.shuffle(pair)
        order.extend(pair)
    
    for i, variant in enumerate(order):
        lib = baseline_lib if variant == "baseline" else candidate_lib
        res = run_benchmarks_for_lib(lib.parent, lib, target_name, run_all=False, iteration=i)
        
        # Parse result
        for r in res:
            if r.command_result.returncode == 0 and r.parsed_result:
                if variant == "baseline":
                    baseline_results.append(r.parsed_result)
                else:
                    candidate_results.append(r.parsed_result)
                    
    return calculate_benchmark_statistics(candidate_results, expected_count=repetitions), \
           calculate_benchmark_statistics(baseline_results, expected_count=repetitions), \
           order
