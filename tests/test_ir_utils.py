import pytest
import llmo.llama
from pathlib import Path
from llmo.llama import ChatCompletionResult
from llmo.source import extract_code_block, validate_llvm_ir_module
from llmo.benchmark import calculate_benchmark_statistics, compare_benchmarks, parse_key_value_lines
from llmo.benchmark_protocol import BenchmarkMeasurement, BenchmarkStatistics
from llmo.project import source_function_name
from run_ir_optimization import require_preserved_target_configuration

def test_completion_metadata_parsing():
    # Mock result
    raw_response = {
        "choices": [{"finish_reason": "stop", "message": {"content": "test"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    }
    result = ChatCompletionResult(
        content="test",
        finish_reason="stop",
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
        raw_response=raw_response
    )
    assert result.finish_reason == "stop"
    assert result.prompt_tokens == 10

def test_truncation_detection():
    raw_response = {
        "choices": [{"finish_reason": "length", "message": {"content": "truncated..."}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 100, "total_tokens": 110}
    }
    result = ChatCompletionResult(
        content="truncated...",
        finish_reason="length",
        prompt_tokens=10,
        completion_tokens=100,
        total_tokens=110,
        raw_response=raw_response
    )
    assert result.finish_reason == "length"

def test_context_budget_calculations(monkeypatch):
    monkeypatch.setattr(llmo.llama, "EFFECTIVE_LLAMA_CTX_SIZE", 32768)
    monkeypatch.setattr(llmo.llama, "count_tokens", lambda x: len(x) // 3)
    
    prompt = "A" * 300
    system_prompt = "B" * 150
    requested_max = 1000
    safety = 500
    min_expected = 4096
    
    budget = llmo.llama.calculate_token_budget(prompt, system_prompt, requested_max, minimum_expected_output_tokens=min_expected, safety_margin=safety)
    
    expected_prompt_tokens = (len(prompt) // 3) + (len(system_prompt) // 3) + 50
    expected_available = 32768 - expected_prompt_tokens - safety
    
    assert budget.prompt_tokens == expected_prompt_tokens
    assert budget.available_output_tokens == expected_available
    assert budget.can_fit_requested_maximum == (expected_available >= requested_max)
    assert budget.can_fit_minimum_expected_output == (expected_available >= min_expected)

def test_ir_extraction():
    fenced = "Here is the IR:\n```llvm\n%1 = add i32 %a, %b\nret i32 %1\n```\nHope it helps!"
    extracted = extract_code_block(fenced)
    assert "%1 = add i32 %a, %b\nret i32 %1" in extracted
    assert "Here is the IR" not in extracted
    assert "Hope it helps" not in extracted
    
    raw = "%1 = add i32 %a, %b\nret i32 %1\n"
    assert extract_code_block(raw).strip() == raw.strip()

def test_incomplete_module_rejection():
    incomplete = "target triple = \"x86_64-unknown-linux-gnu\"\ndefine i32 @test() {"
    val = validate_llvm_ir_module(incomplete, "test")
    assert not val.preflight_passed
    assert any("braces" in e.lower() or "truncated" in e.lower() for e in val.errors)
    
    missing_triple = "define i32 @test() {\nret i32 0\n}"
    val = validate_llvm_ir_module(missing_triple, "test")
    assert not val.preflight_passed
    assert any("triple" in e.lower() for e in val.errors)

def test_extracted_ir_must_preserve_target_configuration():
    original = 'target datalayout = "e"\ntarget triple = "x86_64"\ndefine i32 @test() { ret i32 0 }\n'
    changed = original.replace('target triple = "x86_64"', 'target triple = "aarch64"')
    val = validate_llvm_ir_module(changed, "test")
    require_preserved_target_configuration(val, changed, original)
    assert not val.preflight_passed
    assert "Changed required target triple" in val.errors

def test_performance_summary_and_noise():
    m1 = BenchmarkMeasurement("a", 0, "fib", 0, 0, 100.0, 1, 1, 0, 0, {}, "out", "err")
    m2 = BenchmarkMeasurement("a", 0, "fib", 1, 1, 110.0, 1, 1, 0, 0, {}, "out", "err")
    m3 = BenchmarkMeasurement("a", 0, "fib", 2, 2, 105.0, 1, 1, 0, 0, {}, "out", "err")
    
    stats = calculate_benchmark_statistics([m1, m2, m3])
    assert stats.median_calls_per_second == 105.0
    assert stats.minimum_calls_per_second == 100.0
    assert stats.maximum_calls_per_second == 110.0
    
    baseline_stats = BenchmarkStatistics(3, 3, 100.0)
    # 105 vs 100 -> 5% improvement. Noise threshold 2%.
    comp = compare_benchmarks(stats, baseline_stats, 2.0, "base", "cand", [])
    assert comp.classification == "improved"
    
    # 101 vs 100 -> 1% improvement. Noise threshold 2%.
    cand_stats_low = BenchmarkStatistics(3, 3, 101.0)
    comp_low = compare_benchmarks(cand_stats_low, baseline_stats, 2.0, "base", "cand", [])
    assert comp_low.classification == "unchanged_within_noise"
    
    # 95 vs 100 -> 5% regression.
    cand_stats_reg = BenchmarkStatistics(3, 3, 95.0)
    comp_reg = compare_benchmarks(cand_stats_reg, baseline_stats, 2.0, "base", "cand", [])
    assert comp_reg.classification == "regressed"

def test_source_to_benchmark_mapping():
    path = Path("SUT/fibonacci.cpp")
    assert source_function_name(path) == "fibonacci"
    
    path_ir = Path("fibonacci.ll")
    assert path_ir.stem == "fibonacci"

def test_key_value_parsing():
    text = """function=fibonacci
wall_us=1000000
cpu_us=999000
calls_per_second=1234.5
checksum=42
"""
    parsed = parse_key_value_lines(text)
    assert parsed["function"] == "fibonacci"
    assert parsed["wall_us"] == 1000000
    assert parsed["calls_per_second"] == 1234.5
    assert parsed["checksum"] == 42
