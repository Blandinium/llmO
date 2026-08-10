"""Shared reporting metadata for optimization and final benchmarking."""

from __future__ import annotations

from typing import Any, Mapping


def normalized_timing(
    llm_inference_seconds: float = 0.0,
    repair_inference_seconds: float = 0.0,
    optimization_pipeline_seconds: float = 0.0,
) -> dict[str, float]:
    """Return the common optimization timing schema."""
    main = float(llm_inference_seconds or 0.0)
    repair = float(repair_inference_seconds or 0.0)
    return {
        "llm_inference_seconds": main,
        "repair_inference_seconds": repair,
        "total_llm_seconds": main + repair,
        "optimization_pipeline_seconds": float(optimization_pipeline_seconds or 0.0),
    }


def confirmation_fields(selection_status: str, confirmation_status: str) -> dict[str, Any]:
    """Create consistent, explicit selection/confirmation metadata."""
    return {
        "selection_status": selection_status,
        "confirmation_status": confirmation_status,
        "confirmed_improvement": confirmation_status == "improved",
    }


def calculate_break_even(
    baseline_calls_per_second: float | None,
    optimized_calls_per_second: float | None,
    timing: Mapping[str, Any] | None,
    calls_per_execution: int | float | None = None,
) -> dict[str, float | None]:
    """Calculate reporting-only amortization values for one candidate."""
    result: dict[str, float | None] = {
        "baseline_time_per_call_seconds": None,
        "optimized_time_per_call_seconds": None,
        "saving_per_call_seconds": None,
        "break_even_calls_llm": None,
        "break_even_calls_pipeline": None,
        "break_even_executions_llm": None,
        "break_even_executions_pipeline": None,
        "break_even_baseline_runtime_seconds_llm": None,
        "break_even_baseline_runtime_seconds_pipeline": None,
    }
    if not baseline_calls_per_second or not optimized_calls_per_second:
        return result
    baseline_per_call = 1.0 / baseline_calls_per_second
    optimized_per_call = 1.0 / optimized_calls_per_second
    saving = baseline_per_call - optimized_per_call
    result.update({
        "baseline_time_per_call_seconds": baseline_per_call,
        "optimized_time_per_call_seconds": optimized_per_call,
        "saving_per_call_seconds": saving,
    })
    if saving <= 0 or not timing:
        return result
    for cost_name, suffix in (("total_llm_seconds", "llm"), ("optimization_pipeline_seconds", "pipeline")):
        cost = timing.get(cost_name)
        if cost is None:
            continue
        calls = float(cost) / saving
        result[f"break_even_calls_{suffix}"] = calls
        result[f"break_even_baseline_runtime_seconds_{suffix}"] = calls / baseline_calls_per_second
        if calls_per_execution:
            result[f"break_even_executions_{suffix}"] = calls / float(calls_per_execution)
    return result
