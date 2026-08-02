from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Tuple
import statistics

@dataclass(frozen=True)
class BenchmarkProtocol:
    repetitions: int
    seed: int
    noise_threshold_percent: float
    ordering: str # "paired", "randomized", "fixed"
    require_all_repetitions: bool = True

@dataclass
class BenchmarkMeasurement:
    artifact_id: str
    benchmark_id: int
    benchmark_name: str
    repetition: int
    sequence_index: int
    calls_per_second: float | None
    wall_us: int | None
    cpu_us: int | None
    checksum: str | int | None
    returncode: int
    parsed_result: dict[str, Any] | None
    stdout_path: str
    stderr_path: str

@dataclass
class BenchmarkStatistics:
    requested_repetitions: int
    successful_repetitions: int
    median_calls_per_second: float | None = None
    minimum_calls_per_second: float | None = None
    maximum_calls_per_second: float | None = None
    mean_calls_per_second: float | None = None
    median_absolute_deviation: float | None = None

@dataclass
class BenchmarkComparison:
    baseline_artifact_id: str
    candidate_artifact_id: str
    baseline_statistics: BenchmarkStatistics
    candidate_statistics: BenchmarkStatistics
    relative_change_percent: float | None
    classification: str # improved, unchanged_within_noise, regressed, benchmark_incomplete, benchmark_failed
    sequence: list[str]
    noise_threshold_percent: float

def calculate_benchmark_statistics(measurements: List[BenchmarkMeasurement], requested_repetitions: int = 0) -> BenchmarkStatistics:
    successful = [m for m in measurements if m.returncode == 0 and m.calls_per_second is not None and m.calls_per_second > 0]
    count = len(successful)
    
    if count == 0:
        return BenchmarkStatistics(requested_repetitions=requested_repetitions, successful_repetitions=0)
    
    cps_values = [m.calls_per_second for m in successful]
    
    median_cps = statistics.median(cps_values)
    mad = statistics.median([abs(x - median_cps) for x in cps_values])
    
    return BenchmarkStatistics(
        requested_repetitions=requested_repetitions or count,
        successful_repetitions=count,
        median_calls_per_second=median_cps,
        minimum_calls_per_second=min(cps_values),
        maximum_calls_per_second=max(cps_values),
        mean_calls_per_second=statistics.mean(cps_values),
        median_absolute_deviation=mad
    )

def compare_benchmarks(
    candidate_stats: BenchmarkStatistics, 
    baseline_stats: BenchmarkStatistics, 
    noise_threshold_percent: float,
    baseline_id: str,
    candidate_id: str,
    sequence: list[str]
) -> BenchmarkComparison:
    b_cps = baseline_stats.median_calls_per_second
    c_cps = candidate_stats.median_calls_per_second
    
    if baseline_stats.successful_repetitions == 0 or candidate_stats.successful_repetitions == 0:
        classification = "benchmark_failed"
        return BenchmarkComparison(
            baseline_artifact_id=baseline_id,
            candidate_artifact_id=candidate_id,
            baseline_statistics=baseline_stats,
            candidate_statistics=candidate_stats,
            relative_change_percent=None,
            classification=classification,
            sequence=sequence,
            noise_threshold_percent=noise_threshold_percent
        )

    if (baseline_stats.successful_repetitions < baseline_stats.requested_repetitions or 
        candidate_stats.successful_repetitions < candidate_stats.requested_repetitions):
        classification = "benchmark_incomplete"
    else:
        improvement = (c_cps - b_cps) / b_cps
        threshold = noise_threshold_percent / 100.0
        
        # change > threshold => improved
        # change < -threshold => regressed
        # otherwise => unchanged_within_noise
        if improvement > threshold:
            classification = "improved"
        elif improvement < -threshold:
            classification = "regressed"
        else:
            classification = "unchanged_within_noise"
            
    return BenchmarkComparison(
        baseline_artifact_id=baseline_id,
        candidate_artifact_id=candidate_id,
        baseline_statistics=baseline_stats,
        candidate_statistics=candidate_stats,
        relative_change_percent=(c_cps - b_cps) / b_cps * 100.0,
        classification=classification,
        sequence=sequence,
        noise_threshold_percent=noise_threshold_percent
    )
