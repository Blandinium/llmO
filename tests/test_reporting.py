from llmo.reporting import calculate_break_even, confirmation_fields, normalized_timing


def test_normalized_timing_and_confirmation_fields():
    timing = normalized_timing(8.0, 2.0, 15.0)
    assert timing == {
        "llm_inference_seconds": 8.0,
        "repair_inference_seconds": 2.0,
        "total_llm_seconds": 10.0,
        "optimization_pipeline_seconds": 15.0,
    }
    assert confirmation_fields("improved", "regressed") == {
        "selection_status": "improved",
        "confirmation_status": "regressed",
        "confirmed_improvement": False,
    }


def test_break_even_faster_candidate():
    result = calculate_break_even(100.0, 125.0, normalized_timing(8, 2, 20), calls_per_execution=50)
    assert result["saving_per_call_seconds"] == 0.002
    assert result["break_even_calls_llm"] == 5000.0
    assert result["break_even_calls_pipeline"] == 10000.0
    assert result["break_even_executions_llm"] == 100.0
    assert result["break_even_baseline_runtime_seconds_pipeline"] == 100.0


def test_break_even_slower_or_missing_timing_is_not_applicable():
    slower = calculate_break_even(100.0, 90.0, normalized_timing(1, 0, 2))
    missing = calculate_break_even(100.0, 110.0, None)
    assert slower["break_even_calls_llm"] is None
    assert slower["break_even_calls_pipeline"] is None
    assert missing["break_even_calls_llm"] is None
    assert missing["break_even_calls_pipeline"] is None
