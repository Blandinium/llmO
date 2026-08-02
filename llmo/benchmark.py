from dataclasses import dataclass
import json
import os
import statistics
import random
from pathlib import Path
from typing import Any, List, Dict, Optional, Tuple
from .command import run_command, write_json, CommandResult
from .config import BENCHMARK_FUNCTIONS, RUNNER_EXECUTABLE_NAME, BENCHMARK_TIMEOUT_SECONDS, RUNNER_ARGS, FUNCTION_TO_BENCHMARK_ID
from .benchmark_protocol import (
    BenchmarkMeasurement, 
    BenchmarkStatistics, 
    BenchmarkComparison, 
    BenchmarkProtocol, 
    calculate_benchmark_statistics, 
    compare_benchmarks
)

# Backward compatibility alias
def classify_performance(candidate_cps: float, baseline_cps: float, noise_threshold: float = 0.02) -> str:
    """Backward-compatible scalar performance classification.

    ``noise_threshold`` is a fraction (0.02 == 2%). New code should prefer
    :func:`compare_benchmarks`, which also handles incomplete measurements.
    """
    if baseline_cps <= 0 or candidate_cps <= 0:
        return "benchmark_failed"
    change = (candidate_cps - baseline_cps) / baseline_cps
    if change > noise_threshold:
        return "improved"
    if change < -noise_threshold:
        return "regressed"
    return "unchanged_within_noise"

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

def run_benchmarks_for_lib(
    build_dir: Path, 
    libsut_path: Path, 
    target_function_name: str = None, 
    run_all: bool = True, 
    iteration: int = 0,
    artifact_id: str = "unknown",
    sequence_index: int = 0
) -> list[BenchmarkMeasurement]:
    env = os.environ.copy()
    old_ld_library_path = env.get("LD_LIBRARY_PATH")
    env["LD_LIBRARY_PATH"] = f"{libsut_path.parent}:{old_ld_library_path}" if old_ld_library_path else str(libsut_path.parent)
    
    if run_all or target_function_name is None:
        selected = list(BENCHMARK_FUNCTIONS.items())
    else:
        function_id = FUNCTION_TO_BENCHMARK_ID[target_function_name]
        selected = [(function_id, target_function_name)]

    measurements: list[BenchmarkMeasurement] = []
    for function_id, function_name in selected:
        suffix = f"_seq{sequence_index:03d}"
        stdout = build_dir / f"benchmark_{function_name}{suffix}_stdout.txt"
        stderr = build_dir / f"benchmark_{function_name}{suffix}_stderr.txt"
        command = [str(RUNNER_EXECUTABLE_NAME), str(libsut_path), str(function_id), *RUNNER_ARGS]
        result = run_command(command, build_dir, stdout, stderr, env, timeout_seconds=BENCHMARK_TIMEOUT_SECONDS)
        
        parsed = None
        if result.returncode == 0:
            parsed = try_parse_benchmark_result(stdout)
            if parsed:
                try_write_benchmark_json(stdout, build_dir / f"benchmark_{function_name}{suffix}_results.json")
        
        measurements.append(BenchmarkMeasurement(
            artifact_id=artifact_id,
            benchmark_id=function_id,
            benchmark_name=function_name,
            repetition=iteration,
            sequence_index=sequence_index,
            calls_per_second=parsed.get("calls_per_second") if parsed else None,
            wall_us=parsed.get("wall_us") if parsed else None,
            cpu_us=parsed.get("cpu_us") if parsed else None,
            checksum=parsed.get("checksum") if parsed else None,
            returncode=result.returncode,
            parsed_result=parsed,
            stdout_path=str(stdout),
            stderr_path=str(stderr)
        ))
    return measurements

def get_randomized_balanced_sequence(
    artifact_ids: List[str],
    repetitions: int,
    seed: int
) -> List[str]:
    rng = random.Random(seed)
    sequence = []
    for i in range(repetitions):
        block = list(artifact_ids)
        rng.shuffle(block)
        sequence.extend(block)
    return sequence

def run_benchmarks_paired(
    candidate_lib: Path,
    baseline_lib: Path,
    target_name: str,
    protocol: BenchmarkProtocol,
    candidate_id: str = "candidate",
    baseline_id: str = "baseline"
) -> BenchmarkComparison:
    sequence = get_randomized_balanced_sequence([baseline_id, candidate_id], protocol.repetitions, protocol.seed)
    
    all_measurements: List[BenchmarkMeasurement] = []
    
    # Map repetition count per artifact
    reps = {baseline_id: 0, candidate_id: 0}
    
    for i, variant_id in enumerate(sequence):
        lib = baseline_lib if variant_id == baseline_id else candidate_lib
        iteration = reps[variant_id]
        reps[variant_id] += 1
        
        measurements = run_benchmarks_for_lib(
            lib.parent, lib, target_name, 
            run_all=False, 
            iteration=iteration,
            artifact_id=variant_id,
            sequence_index=i
        )
        all_measurements.extend(measurements)
    
    baseline_measurements = [m for m in all_measurements if m.artifact_id == baseline_id]
    candidate_measurements = [m for m in all_measurements if m.artifact_id == candidate_id]
    
    baseline_stats = calculate_benchmark_statistics(baseline_measurements, protocol.repetitions)
    candidate_stats = calculate_benchmark_statistics(candidate_measurements, protocol.repetitions)
    
    return compare_benchmarks(
        candidate_stats, 
        baseline_stats, 
        protocol.noise_threshold_percent,
        baseline_id,
        candidate_id,
        sequence
    )
