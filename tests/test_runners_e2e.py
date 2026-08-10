import pytest
import json
import sys
from unittest.mock import MagicMock, patch
from pathlib import Path
import run_ir_optimization
import run_naive_cpp_optimization

def _mock_comparison(classification="unchanged_within_noise", change=0.0):
    from llmo.benchmark_protocol import BenchmarkComparison, BenchmarkStatistics
    stats = BenchmarkStatistics(1, 1, 100.0, 100.0, 100.0, 100.0, 0.0)
    return BenchmarkComparison(
        baseline_artifact_id="baseline",
        candidate_artifact_id="candidate",
        baseline_statistics=stats,
        candidate_statistics=stats,
        relative_change_percent=change,
        classification=classification,
        sequence=["baseline", "candidate"],
        noise_threshold_percent=2.0,
    )

@pytest.fixture
def mock_env(tmp_path, monkeypatch):
    # Mock LLM Models config
    monkeypatch.setattr("run_ir_optimization.LLM_MODELS", [{"name": "test-model", "hf_repo": "repo", "alias": "test-model"}])
    monkeypatch.setattr("run_naive_cpp_optimization.LLM_MODELS", [{"name": "test-model", "hf_repo": "repo", "alias": "test-model"}])
    
    # Mock target discovery
    fib_cpp = tmp_path / "SUT" / "fibonacci.cpp"
    fib_cpp.parent.mkdir(parents=True)
    fib_cpp.write_text("int fibonacci() { return 0; }")
    monkeypatch.setattr("run_ir_optimization.llm_target_source_files", MagicMock(return_value=[fib_cpp]))
    monkeypatch.setattr("run_naive_cpp_optimization.llm_target_source_files", MagicMock(return_value=[fib_cpp]))
    
    # Mock server
    monkeypatch.setattr("run_ir_optimization.start_llama_server", MagicMock(return_value=(MagicMock(), ["cmd"])))
    monkeypatch.setattr("run_ir_optimization.wait_for_llama_ready", MagicMock())
    monkeypatch.setattr("run_ir_optimization.warm_up_llm", MagicMock())
    
    monkeypatch.setattr("run_naive_cpp_optimization.start_llama_server", MagicMock(return_value=(MagicMock(), ["cmd"])))
    monkeypatch.setattr("run_naive_cpp_optimization.wait_for_llama_ready", MagicMock())
    monkeypatch.setattr("run_naive_cpp_optimization.warm_up_llm", MagicMock())
    
    # Mock count_tokens
    monkeypatch.setattr("run_ir_optimization.count_tokens", MagicMock(return_value=10))
    monkeypatch.setattr("run_naive_cpp_optimization.count_tokens", MagicMock(return_value=10))
    # Mock LLAMA context
    import llmo.llama
    monkeypatch.setattr(llmo.llama, "EFFECTIVE_LLAMA_CTX_SIZE", 32768)

    return tmp_path

def test_ir_runner_mocked(mock_env, monkeypatch):
    tmp_path = mock_env
    
    # Mock LLM response
    from llmo.llama import ChatCompletionResult
    mock_res = ChatCompletionResult(
        content='target triple = "x86_64"\ntarget datalayout = "e"\ndefine i32 @fibonacci() {\nret i32 0\n}',
        finish_reason="stop",
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
        raw_response={"choices": [{"finish_reason": "stop", "message": {"content": "..."}}], "usage": {}}
    )
    monkeypatch.setattr("run_ir_optimization.call_llm", MagicMock(return_value=mock_res))
    
    # Mock LLVM tools
    from llmo.command import CommandResult
    mock_ir_res = MagicMock()
    mock_ir_res.output_path = tmp_path / "fibonacci.ll"
    mock_ir_res.output_path.write_text(mock_res.content)
    mock_ir_res.command_result = CommandResult([], ".", 0, 0.1, "out", "err")
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir", MagicMock(return_value=mock_ir_res))
    monkeypatch.setattr("run_ir_optimization.verify_llvm_ir", MagicMock(return_value=CommandResult([], ".", 0, 0.1, "out", "err")))
    
    # Mock compile
    from llmo.llvm import IrOperationResult
    mock_comp = IrOperationResult(
        command_result=CommandResult([], ".", 0, 0.1, "out", "err"),
        output_path=tmp_path / "libSUT.so"
    )
    mock_comp.output_path.touch()
    monkeypatch.setattr("run_ir_optimization.compile_llvm_ir_to_lib", MagicMock(return_value=mock_comp))
    
    # Mock ABI check
    from llmo.command import CommandResult
    def mock_abi(build_dir, lib, required_symbols=None):
        build_dir.mkdir(parents=True, exist_ok=True)
        (build_dir / "abi_symbols.json").write_text('{"success": true}')
        return CommandResult(["nm"], ".", 0, 0.1, "out", "err")
    monkeypatch.setattr("run_ir_optimization.run_abi_symbol_check", mock_abi)
    
    # Mock benchmarks
    from llmo.benchmark_protocol import BenchmarkMeasurement
    mock_m = BenchmarkMeasurement("a", 0, "fibonacci", 0, 0, 100.0, 1, 1, 0, 0, {}, "out", "err")
    monkeypatch.setattr("run_ir_optimization.run_benchmarks_for_lib", MagicMock(return_value=[mock_m]))
    monkeypatch.setattr("run_ir_optimization.run_benchmarks_paired", MagicMock(return_value=_mock_comparison()))

    # Run main
    args = ["run_ir_optimization.py", "--model", "test-model", "--only", "fibonacci", "--output-root", str(tmp_path), "--backend-opt-level", "O3", "--benchmark-repetitions", "1", "--run-id", "test-run"]
    with patch("sys.argv", args):
        run_ir_optimization.main()
    
    # Verify results
    summary_path = tmp_path / "llm-ir" / "test-run" / "test-model" / "fibonacci_cpp" / "summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text())
    assert summary["status"] == "completed"
    assert "backend_results" in summary
    assert "-O3" in summary["backend_results"]
    assert set(summary["timing"]) == {
        "llm_inference_seconds", "repair_inference_seconds", "total_llm_seconds", "optimization_pipeline_seconds"
    }
    candidate_id = summary["backend_results"]["-O3"]["artifact_id"]
    artifact = json.loads((tmp_path / "llm-ir" / "test-run" / "artifacts" / candidate_id / "artifact.json").read_text())
    assert artifact["timing"]["total_llm_seconds"] == summary["timing"]["total_llm_seconds"]

def test_naive_runner_mocked(mock_env, monkeypatch):
    tmp_path = mock_env
    
    # Mock LLM response
    from llmo.llama import ChatCompletionResult
    mock_res = ChatCompletionResult(
        content="uint64_t fibonacci() { return 0; }",
        finish_reason="stop",
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
        raw_response={"choices": [{"finish_reason": "stop", "message": {"content": "uint64_t fibonacci() { return 0; }"}},]}
    )
    monkeypatch.setattr("run_naive_cpp_optimization.call_llm", MagicMock(return_value=mock_res))
    
    # Mock compile
    from llmo.build import CompileResult
    from llmo.command import CommandResult
    mock_comp = CompileResult(
        command_result=CommandResult([], ".", 0, 0.1, "out", "err"),
        libsut_path=tmp_path / "libSUT.so"
    )
    mock_comp.libsut_path.touch()
    monkeypatch.setattr("run_naive_cpp_optimization.compile_replacement_artifact_for_check", MagicMock(return_value=mock_comp))
    
    # Mock ABI check
    def mock_abi_naive(build_dir, lib, required_symbols=None):
        build_dir.mkdir(parents=True, exist_ok=True)
        (build_dir / "abi_symbols.json").write_text('{"success": true}')
        return CommandResult(["nm"], ".", 0, 0.1, "out", "err")
    monkeypatch.setattr("run_naive_cpp_optimization.run_abi_symbol_check", mock_abi_naive)
    
    # Mock benchmarks
    from llmo.benchmark_protocol import BenchmarkMeasurement
    mock_m = BenchmarkMeasurement("a", 0, "fibonacci", 0, 0, 100.0, 1, 1, 0, 0, {}, "out", "err")
    monkeypatch.setattr("run_naive_cpp_optimization.run_benchmarks_for_lib", MagicMock(return_value=[mock_m]))
    monkeypatch.setattr("run_naive_cpp_optimization.run_benchmarks_paired", MagicMock(return_value=_mock_comparison()))

    # Run main
    args = ["run_naive_cpp_optimization.py", "--model", "test-model", "--only", "fibonacci", "--output-root", str(tmp_path), "--benchmark-repetitions", "1", "--run-id", "test-run-naive"]
    with patch("sys.argv", args):
        run_naive_cpp_optimization.main()
    
    # Verify results
    summary_path = tmp_path / "naive-cpp" / "test-run-naive" / "test-model" / "fibonacci_cpp" / "summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text())
    assert summary["status"] == "completed"
    assert summary["timing"]["total_llm_seconds"] >= 0
    assert summary["confirmation_status"] == "not-required"
    assert summary["confirmed_improvement"] is False


def test_naive_confirmation_is_independent_and_authoritative(mock_env, monkeypatch):
    tmp_path = mock_env
    from llmo.llama import ChatCompletionResult
    from llmo.build import CompileResult
    from llmo.command import CommandResult

    monkeypatch.setattr("run_naive_cpp_optimization.call_llm", MagicMock(return_value=ChatCompletionResult(
        content="uint64_t fibonacci() { return 1; }", finish_reason="stop",
        prompt_tokens=1, completion_tokens=1, total_tokens=2, raw_response={},
    )))
    lib = tmp_path / "candidate.so"
    lib.touch()
    monkeypatch.setattr("run_naive_cpp_optimization.compile_replacement_artifact_for_check", MagicMock(return_value=CompileResult(
        CommandResult([], ".", 0, 0.1, "out", "err"), lib,
    )))

    def mock_abi(build_dir, library, required_symbols=None):
        build_dir.mkdir(parents=True, exist_ok=True)
        (build_dir / "abi_symbols.json").write_text('{"success": true}')
        return CommandResult([], ".", 0, 0.1, "out", "err")

    monkeypatch.setattr("run_naive_cpp_optimization.run_abi_symbol_check", mock_abi)
    comparisons = MagicMock(side_effect=[
        _mock_comparison("improved", 5.0),
        _mock_comparison("unchanged_within_noise", 1.0),
    ])
    monkeypatch.setattr("run_naive_cpp_optimization.run_benchmarks_paired", comparisons)
    monkeypatch.setattr("run_naive_cpp_optimization.run_benchmarks_for_lib", MagicMock(return_value=[]))

    args = ["run_naive_cpp_optimization.py", "--model", "test-model", "--only", "fibonacci",
            "--output-root", str(tmp_path), "--run-id", "confirmation", "--seed", "17"]
    with patch("sys.argv", args):
        run_naive_cpp_optimization.main()

    summary = json.loads((tmp_path / "naive-cpp" / "confirmation" / "test-model" / "fibonacci_cpp" / "summary.json").read_text())
    assert summary["selection_status"] == "improved"
    assert summary["confirmation_status"] == "unchanged_within_noise"
    assert summary["confirmed_improvement"] is False
    assert summary["confirmation_seed"] == 18
    assert comparisons.call_args_list[0].kwargs["protocol"].seed == 17
    assert comparisons.call_args_list[1].kwargs["protocol"].seed == 18
    assert not (tmp_path / "naive-cpp" / "confirmation" / "artifacts" / "naive-cpp__test-model__fibonacci__final").exists()
    assert (tmp_path / "candidate.so").exists()

def test_ir_runner_repair_unchanged(mock_env, monkeypatch):
    tmp_path = mock_env
    
    # Mock LLM initial response (invalid)
    from llmo.llama import ChatCompletionResult
    invalid_content = 'target triple = "x86_64"\ntarget datalayout = "e"\ndefine i32 @fibonacci() {\nret i32 0\n}'
    mock_res = ChatCompletionResult(
        content=invalid_content,
        finish_reason="stop",
        prompt_tokens=10, completion_tokens=20, total_tokens=30,
        raw_response={"choices": [{"finish_reason": "stop", "message": {"content": "..."}}], "usage": {}}
    )
    
    # Mock repair response (same as invalid)
    mock_repair_res = ChatCompletionResult(
        content=invalid_content,
        finish_reason="stop",
        prompt_tokens=10, completion_tokens=20, total_tokens=30,
        raw_response={"choices": [{"finish_reason": "stop", "message": {"content": "..."}}], "usage": {}}
    )
    
    call_llm_mock = MagicMock(side_effect=[mock_res, mock_repair_res])
    monkeypatch.setattr("run_ir_optimization.call_llm", call_llm_mock)
    
    # Mock LLVM tools
    from llmo.command import CommandResult
    mock_ir_res = MagicMock()
    mock_ir_res.output_path = tmp_path / "fibonacci.ll"
    mock_ir_res.output_path.write_text(invalid_content)
    mock_ir_res.command_result = CommandResult([], ".", 0, 0.1, "out", "err")
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir", MagicMock(return_value=mock_ir_res))
    
    # Mock verification: fails twice
    mock_verify = MagicMock(side_effect=[
        CommandResult([], ".", 1, 0.1, "out", str(tmp_path / "err.txt")),
        CommandResult([], ".", 1, 0.1, "out", str(tmp_path / "err2.txt"))
    ])
    (tmp_path / "err.txt").write_text("Instruction does not dominate all uses")
    (tmp_path / "err2.txt").write_text("Instruction does not dominate all uses")
    monkeypatch.setattr("run_ir_optimization.verify_llvm_ir", mock_verify)

    # Run main
    args = ["run_ir_optimization.py", "--model", "test-model", "--only", "fibonacci", "--output-root", str(tmp_path), "--run-id", "test-repair-unchanged"]
    with patch("sys.argv", args):
        run_ir_optimization.main()
    
    # Verify results
    summary_path = tmp_path / "llm-ir" / "test-repair-unchanged" / "test-model" / "fibonacci_cpp" / "summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text())
    assert summary["status"] == "repair_unchanged_invalid"
    assert summary["validation"]["repair_attempted"] is True
    assert summary["validation"]["repair_verification_passed"] is False
    assert summary["repair_module_changed"] is False
    assert "initial_verifier_error_excerpt" in summary
    assert "repair_inference_seconds" in summary

def test_ir_runner_initial_extraction_fails(mock_env, monkeypatch):
    tmp_path = mock_env
    from llmo.llama import ChatCompletionResult
    mock_res = ChatCompletionResult(
        content='   ',
        finish_reason="stop",
        prompt_tokens=10, completion_tokens=20, total_tokens=30,
        raw_response={}
    )
    monkeypatch.setattr("run_ir_optimization.call_llm", MagicMock(return_value=mock_res))
    
    from llmo.command import CommandResult
    mock_ir_res = MagicMock()
    mock_ir_res.output_path = tmp_path / "fibonacci.ll"
    mock_ir_res.output_path.write_text("...")
    mock_ir_res.command_result = CommandResult([], ".", 0, 0.1, "out", "err")
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir", MagicMock(return_value=mock_ir_res))

    args = ["run_ir_optimization.py", "--model", "test-model", "--only", "fibonacci", "--output-root", str(tmp_path), "--run-id", "test-extract-fail"]
    with patch("sys.argv", args):
        run_ir_optimization.main()
    
    summary_path = tmp_path / "llm-ir" / "test-extract-fail" / "test-model" / "fibonacci_cpp" / "summary.json"
    summary = json.loads(summary_path.read_text())
    assert summary["status"] == "response_empty"
    assert summary["validation"]["module_extracted"] is False

def test_ir_runner_repair_truncated(mock_env, monkeypatch):
    tmp_path = mock_env
    from llmo.llama import ChatCompletionResult
    valid_preflight = 'target triple = "x86_64"\ntarget datalayout = "e"\ndefine i32 @fibonacci() {\nret i32 0\n}'
    mock_res = ChatCompletionResult(
        content=valid_preflight,
        finish_reason="stop",
        prompt_tokens=10, completion_tokens=20, total_tokens=30,
        raw_response={}
    )
    mock_repair_res = ChatCompletionResult(
        content=valid_preflight,
        finish_reason="length",
        prompt_tokens=10, completion_tokens=20, total_tokens=30,
        raw_response={}
    )
    monkeypatch.setattr("run_ir_optimization.call_llm", MagicMock(side_effect=[mock_res, mock_repair_res]))
    
    from llmo.command import CommandResult
    mock_ir_res = MagicMock()
    mock_ir_res.output_path = tmp_path / "fibonacci.ll"
    mock_ir_res.output_path.write_text("...")
    mock_ir_res.command_result = CommandResult([], ".", 0, 0.1, "out", "err")
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir", MagicMock(return_value=mock_ir_res))
    
    # Initial verify fails
    monkeypatch.setattr("run_ir_optimization.verify_llvm_ir", MagicMock(return_value=CommandResult([], ".", 1, 0.1, "out", str(tmp_path/"err.txt"))))
    (tmp_path/"err.txt").touch()

    args = ["run_ir_optimization.py", "--model", "test-model", "--only", "fibonacci", "--output-root", str(tmp_path), "--run-id", "test-repair-truncated"]
    with patch("sys.argv", args):
        run_ir_optimization.main()
    
    summary_path = tmp_path / "llm-ir" / "test-repair-truncated" / "test-model" / "fibonacci_cpp" / "summary.json"
    summary = json.loads(summary_path.read_text())
    assert summary["status"] == "repair_response_truncated"
    assert summary["validation"]["repair_attempted"] is True
    assert summary["validation"]["repair_response_complete"] is False

def test_ir_runner_repair_success(mock_env, monkeypatch):
    tmp_path = mock_env
    from llmo.llama import ChatCompletionResult
    valid_preflight = 'target triple = "x86_64"\ntarget datalayout = "e"\ndefine i32 @fibonacci() {\nret i32 0\n}'
    mock_res = ChatCompletionResult(
        content=valid_preflight,
        finish_reason="stop",
        prompt_tokens=10, completion_tokens=20, total_tokens=30,
        raw_response={}
    )
    mock_repair_res = ChatCompletionResult(
        content='target triple = "x86_64"\ntarget datalayout = "e"\ndefine i32 @fibonacci() {\nret i32 0\n}',
        finish_reason="stop",
        prompt_tokens=10, completion_tokens=20, total_tokens=30,
        raw_response={}
    )
    monkeypatch.setattr("run_ir_optimization.call_llm", MagicMock(side_effect=[mock_res, mock_repair_res]))
    
    from llmo.command import CommandResult
    mock_ir_res = MagicMock()
    mock_ir_res.output_path = tmp_path / "fibonacci.ll"
    mock_ir_res.output_path.write_text("...")
    mock_ir_res.command_result = CommandResult([], ".", 0, 0.1, "out", "err")
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir", MagicMock(return_value=mock_ir_res))
    
    # Mock verification: first fails, second passes
    monkeypatch.setattr("run_ir_optimization.verify_llvm_ir", MagicMock(side_effect=[
        CommandResult([], ".", 1, 0.1, "out", str(tmp_path/"err.txt")),
        CommandResult([], ".", 0, 0.1, "out", "err")
    ]))
    (tmp_path/"err.txt").touch()

    # Mock compilation and benchmark to skip them or make them pass
    from llmo.llvm import IrOperationResult
    mock_comp = IrOperationResult(CommandResult([], ".", 0, 0.1, "out", "err"), tmp_path / "libSUT.so")
    mock_comp.output_path.touch()
    monkeypatch.setattr("run_ir_optimization.compile_llvm_ir_to_lib", MagicMock(return_value=mock_comp))
    
    from llmo.command import CommandResult
    def mock_abi(build_dir, lib, required_symbols=None):
        build_dir.mkdir(parents=True, exist_ok=True)
        (build_dir / "abi_symbols.json").write_text('{"success": true}')
        return CommandResult(["nm"], ".", 0, 0.1, "out", "err")
    monkeypatch.setattr("run_ir_optimization.run_abi_symbol_check", mock_abi)

    from llmo.benchmark_protocol import BenchmarkMeasurement, BenchmarkComparison, BenchmarkStatistics
    mock_comp = BenchmarkComparison(
        baseline_artifact_id="base", candidate_artifact_id="cand",
        baseline_statistics=BenchmarkStatistics(1, 1, 100.0),
        candidate_statistics=BenchmarkStatistics(1, 1, 110.0),
        relative_change_percent=10.0, classification="improved",
        sequence=["base", "cand"], noise_threshold_percent=2.0
    )
    monkeypatch.setattr("run_ir_optimization.run_benchmarks_paired", MagicMock(return_value=mock_comp))

    args = ["run_ir_optimization.py", "--model", "test-model", "--only", "fibonacci", "--output-root", str(tmp_path), "--run-id", "test-repair-success", "--backend-opt-level", "O3", "--benchmark-repetitions", "1"]
    with patch("sys.argv", args):
        run_ir_optimization.main()
    
    summary_path = tmp_path / "llm-ir" / "test-repair-success" / "test-model" / "fibonacci_cpp" / "summary.json"
    summary = json.loads(summary_path.read_text())
    assert summary["status"] == "completed"
    assert summary["validation"]["repair_verification_passed"] is True
