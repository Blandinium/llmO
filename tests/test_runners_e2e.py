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
    assert "validation_skipped" not in artifact
    assert "validation_outcome" not in artifact
    assert "response_mode" not in artifact

def test_extracted_ir_uses_reduced_context_and_distinct_metadata(mock_env, monkeypatch):
    tmp_path = mock_env
    from llmo.command import CommandResult
    from llmo.llvm import IrOperationResult
    from llmo.llama import ChatCompletionResult

    full_ir = tmp_path / "full.ll"
    full_ir.write_text('target triple = "x86_64"\ntarget datalayout = "e"\n' + "; padding\n" * 100 + 'define i32 @fibonacci() { ret i32 0 }\n')
    reduced_ir = tmp_path / "reduced.ll"
    reduced_text = 'target triple = "x86_64"\ntarget datalayout = "e"\ndefine i32 @fibonacci() { ret i32 0 }\n'
    reduced_ir.write_text(reduced_text)
    repaired_text = reduced_text.replace("ret i32 0", "ret i32 1")
    reconstructed = tmp_path / "reconstructed.ll"
    reconstructed.write_text(full_ir.read_text())
    ok = CommandResult([], ".", 0, 0.1, "out", "err")
    verifier_error = tmp_path / "verifier-error.txt"
    verifier_error.write_text("invalid test module")
    invalid = CommandResult([], ".", 1, 0.1, "out", str(verifier_error))

    monkeypatch.setattr("run_ir_optimization.shutil.which", MagicMock(return_value="/mock/llvm-tool"))
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir", MagicMock(return_value=IrOperationResult(ok, full_ir)))
    monkeypatch.setattr("run_ir_optimization.llvm_ir_defines_symbol", MagicMock(return_value=True))
    monkeypatch.setattr("run_ir_optimization.extract_llvm_function", MagicMock(return_value=IrOperationResult(ok, reduced_ir)))
    monkeypatch.setattr("run_ir_optimization.validate_llvm_ir_with_assembler", MagicMock(side_effect=[
        IrOperationResult(ok, tmp_path / "valid-input.bc"),
        IrOperationResult(invalid, None),
        IrOperationResult(ok, tmp_path / "valid-repair.bc"),
    ]))
    monkeypatch.setattr("run_ir_optimization.reintegrate_llvm_function", MagicMock(return_value=IrOperationResult(ok, reconstructed)))
    monkeypatch.setattr("run_ir_optimization.verify_llvm_ir", MagicMock(return_value=ok))
    initial_function = "define " + reduced_text.split("define ", 1)[1]
    repaired_function = "define " + repaired_text.split("define ", 1)[1]
    monkeypatch.setattr("run_ir_optimization.call_llm", MagicMock(side_effect=[
        ChatCompletionResult(content="BEGIN_REPLACEMENT_FUNCTION\n" + initial_function + "END_REPLACEMENT_FUNCTION", finish_reason="stop", prompt_tokens=10,
                             completion_tokens=10, total_tokens=20, raw_response={"choices": [], "usage": {}}),
        ChatCompletionResult(content="BEGIN_REPLACEMENT_FUNCTION\n" + repaired_function + "END_REPLACEMENT_FUNCTION", finish_reason="stop", prompt_tokens=10,
                             completion_tokens=10, total_tokens=20, raw_response={"choices": [], "usage": {}}),
    ]))
    lib = tmp_path / "libSUT.so"
    lib.touch()
    monkeypatch.setattr("run_ir_optimization.compile_llvm_ir_to_lib", MagicMock(return_value=IrOperationResult(ok, lib)))
    def mock_abi(build_dir, library, required_symbols=None):
        build_dir.mkdir(parents=True, exist_ok=True)
        (build_dir / "abi_symbols.json").write_text('{"success": true}')
        return ok
    monkeypatch.setattr("run_ir_optimization.run_abi_symbol_check", mock_abi)
    monkeypatch.setattr("run_ir_optimization.run_benchmarks_paired", MagicMock(return_value=_mock_comparison()))
    token_counter = MagicMock(side_effect=lambda text: len(text))
    monkeypatch.setattr("run_ir_optimization.count_tokens", token_counter)

    argv = ["run_ir_optimization.py", "--mode", "extracted-ir", "--model", "test-model",
            "--only", "fibonacci", "--output-root", str(tmp_path), "--backend-opt-level", "O3",
            "--benchmark-repetitions", "1", "--run-id", "extracted-test"]
    with patch("sys.argv", argv):
        run_ir_optimization.main()

    summary_path = tmp_path / "extracted-ir" / "extracted-test" / "test-model" / "fibonacci_cpp" / "summary.json"
    summary = json.loads(summary_path.read_text())
    assert summary["status"] == "completed"
    assert summary["experiment_type"] == "extracted-ir"
    assert summary["optimization_mode"] == "extracted-ir"
    assert summary["original_estimated_input_tokens"] == len(full_ir.read_text())
    assert summary["extracted_estimated_input_tokens"] == len(reduced_text)
    assert summary["original_ir_bytes"] > summary["extracted_ir_bytes"]
    from llmo.metadata import get_file_sha256
    assert summary["input_ir_sha256"] == get_file_sha256(reduced_ir)
    assert summary["original_ir_sha256"] == get_file_sha256(full_ir)
    assert summary["extracted_ir_sha256"] == get_file_sha256(reduced_ir)
    assert summary["original_ir_sha256"] != summary["extracted_ir_sha256"]
    assert summary["optimized_extracted_ir_sha256"] == get_file_sha256(
        summary_path.parent / "optimized_extracted.ll"
    )
    assert summary["optimized_extracted_ir_sha256"] == get_file_sha256(
        summary_path.parent / "repaired.ll"
    )
    assert summary["optimized_extracted_ir_sha256"] != summary["extracted_module_sha256"]
    assert summary["reconstructed_ir_sha256"] == get_file_sha256(reconstructed)
    assert summary["response_mode"] == "replacement_function"
    assert summary["validation"]["validation_skipped"] is False
    assert summary["validation"]["initial_verification_passed"] is False
    assert summary["validation"]["repair_verification_passed"] is True
    assert summary["validation"]["final_verification_passed"] is True
    artifact_id = summary["backend_results"]["-O3"]["artifact_id"]
    assert artifact_id.startswith("extracted-ir__")
    artifact = json.loads((tmp_path / "extracted-ir" / "extracted-test" / "artifacts" / artifact_id / "artifact.json").read_text())
    assert artifact["experiment_type"] == "extracted-ir"
    assert artifact["response_mode"] == "replacement_function"
    assert artifact["validation_skipped"] is False
    assert artifact["validation_outcome"] == "repaired_code"
    assert artifact["validation"]["repair_verification_passed"] is True


def test_extracted_ir_large_module_no_change_is_tiny_and_skips_repair(mock_env, monkeypatch):
    tmp_path = mock_env
    from llmo.command import CommandResult
    from llmo.llvm import IrOperationResult
    from llmo.llama import ChatCompletionResult

    ok = CommandResult([], ".", 0, 0.1, "out", "err")
    full_ir = tmp_path / "format_list_full.ll"
    reduced_ir = tmp_path / "format_list_extracted.ll"
    body = "define i32 @fibonacci() { ret i32 0 }\n"
    full_ir.write_text('target triple = "x86_64"\ntarget datalayout = "e"\n' + "; large context\n" * 3000 + body)
    reduced_ir.write_text('target triple = "x86_64"\ntarget datalayout = "e"\n' + "declare i32 @helper(i32)\n" * 1000 + body)
    monkeypatch.setattr("run_ir_optimization.shutil.which", MagicMock(return_value="/mock/llvm-tool"))
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir", MagicMock(return_value=IrOperationResult(ok, full_ir)))
    monkeypatch.setattr("run_ir_optimization.llvm_ir_defines_symbol", MagicMock(return_value=True))
    monkeypatch.setattr("run_ir_optimization.extract_llvm_function", MagicMock(return_value=IrOperationResult(ok, reduced_ir)))
    validate = MagicMock(return_value=IrOperationResult(ok, tmp_path / "valid.bc"))
    monkeypatch.setattr("run_ir_optimization.validate_llvm_ir_with_assembler", validate)
    call = MagicMock(return_value=ChatCompletionResult(
        content="NO_CHANGE", finish_reason="stop", prompt_tokens=13000,
        completion_tokens=2, total_tokens=13002, raw_response={},
    ))
    monkeypatch.setattr("run_ir_optimization.call_llm", call)

    argv = ["run_ir_optimization.py", "--mode", "extracted-ir", "--model", "test-model",
            "--only", "fibonacci", "--output-root", str(tmp_path), "--backend-opt-level", "O3",
            "--benchmark-repetitions", "1", "--run-id", "format-list-regression"]
    with patch("sys.argv", argv):
        run_ir_optimization.main()

    task_dir = tmp_path / "extracted-ir" / "format-list-regression" / "test-model" / "fibonacci_cpp"
    summary = json.loads((task_dir / "summary.json").read_text())
    assert summary["status"] == "completed"
    assert summary["response_mode"] == "no_change"
    assert "-O3" in summary["backend_results"]
    assert summary["validation"]["validation_skipped"] is True
    assert summary["validation"]["preflight_passed"] is None
    assert summary["validation"]["initial_verification_passed"] is None
    assert summary["validation"]["final_verification_passed"] is None
    assert summary["validation"]["repair_attempted"] is False
    assert summary["actual_completion_tokens"] == 2
    assert (task_dir / "raw_response.txt").read_text() == "NO_CHANGE"
    assert not (task_dir / "replacement.ll").exists()
    assert validate.call_count == 1  # extracted input only; no output validation or repair
    assert call.call_count == 1


@pytest.mark.parametrize("verification_results, expected_status, expected_initial, expected_repair, expected_final", [
    ([True], "completed", True, None, True),
    ([False, False], "invalid_after_repair", False, False, False),
])
def test_extracted_ir_replacement_validation_metadata(
    mock_env, monkeypatch, verification_results, expected_status,
    expected_initial, expected_repair, expected_final,
):
    from llmo.command import CommandResult
    from llmo.llvm import IrOperationResult
    from llmo.llama import ChatCompletionResult

    ok = CommandResult([], ".", 0, 0.1, "out", "err")
    error_file = mock_env / "llvm-error.txt"
    error_file.write_text("invalid LLVM IR")
    failed = CommandResult([], ".", 1, 0.1, "out", str(error_file))
    full_ir = mock_env / "validation_full.ll"
    extracted_ir = mock_env / "validation_extracted.ll"
    module = ('target triple = "x86_64"\ntarget datalayout = "e"\n'
              'define i32 @fibonacci() { ret i32 0 }\n')
    full_ir.write_text(module)
    extracted_ir.write_text(module)
    initial = "define i32 @fibonacci() { ret i32 1 }\n"
    repaired = "define i32 @fibonacci() { ret i32 2 }\n"
    responses = [initial] if verification_results == [True] else [initial, repaired]
    llm_results = [ChatCompletionResult(
        content=f"BEGIN_REPLACEMENT_FUNCTION\n{function}END_REPLACEMENT_FUNCTION",
        finish_reason="stop", prompt_tokens=10, completion_tokens=10,
        total_tokens=20, raw_response={},
    ) for function in responses]

    monkeypatch.setattr("run_ir_optimization.shutil.which", MagicMock(return_value="/mock/llvm-tool"))
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir", MagicMock(return_value=IrOperationResult(ok, full_ir)))
    monkeypatch.setattr("run_ir_optimization.llvm_ir_defines_symbol", MagicMock(return_value=True))
    monkeypatch.setattr("run_ir_optimization.extract_llvm_function", MagicMock(return_value=IrOperationResult(ok, extracted_ir)))
    validations = [IrOperationResult(ok, mock_env / "input.bc")]
    validations.extend(IrOperationResult(ok if passed else failed, mock_env / "valid.bc" if passed else None)
                       for passed in verification_results)
    monkeypatch.setattr("run_ir_optimization.validate_llvm_ir_with_assembler", MagicMock(side_effect=validations))
    monkeypatch.setattr("run_ir_optimization.call_llm", MagicMock(side_effect=llm_results))

    if verification_results == [True]:
        reconstructed = mock_env / "validation_reconstructed.ll"
        reconstructed.write_text(module)
        monkeypatch.setattr("run_ir_optimization.reintegrate_llvm_function", MagicMock(return_value=IrOperationResult(ok, reconstructed)))
        library = mock_env / "validation.so"
        library.touch()
        monkeypatch.setattr("run_ir_optimization.compile_llvm_ir_to_lib", MagicMock(return_value=IrOperationResult(ok, library)))
        def mock_abi(build_dir, library_path, required_symbols=None):
            build_dir.mkdir(parents=True, exist_ok=True)
            (build_dir / "abi_symbols.json").write_text('{"success": true}')
            return ok
        monkeypatch.setattr("run_ir_optimization.run_abi_symbol_check", mock_abi)
        monkeypatch.setattr("run_ir_optimization.run_benchmarks_paired", MagicMock(return_value=_mock_comparison()))

    run_id = "replacement-valid" if verification_results == [True] else "replacement-invalid"
    argv = ["run_ir_optimization.py", "--mode", "extracted-ir", "--model", "test-model",
            "--only", "fibonacci", "--output-root", str(mock_env), "--backend-opt-level", "O3",
            "--benchmark-repetitions", "1", "--run-id", run_id]
    with patch("sys.argv", argv):
        run_ir_optimization.main()

    summary = json.loads((mock_env / "extracted-ir" / run_id / "test-model" /
                          "fibonacci_cpp" / "summary.json").read_text())
    assert summary["status"] == expected_status
    assert summary["response_mode"] == "replacement_function"
    assert summary["validation"]["validation_skipped"] is False
    assert summary["validation"]["initial_verification_passed"] is expected_initial
    assert summary["validation"]["repair_verification_passed"] is expected_repair
    assert summary["validation"]["final_verification_passed"] is expected_final
    if verification_results == [True]:
        candidate_id = summary["backend_results"]["-O3"]["artifact_id"]
        baseline_id = summary["backend_results"]["-O3"]["baseline_artifact_id"]
        artifacts_dir = mock_env / "extracted-ir" / run_id / "artifacts"
        candidate_metadata = json.loads((artifacts_dir / candidate_id / "artifact.json").read_text())
        baseline_metadata = json.loads((artifacts_dir / baseline_id / "artifact.json").read_text())
        assert candidate_metadata["response_mode"] == "replacement_function"
        assert candidate_metadata["validation_skipped"] is False
        assert candidate_metadata["validation_outcome"] == "valid_code"
        assert candidate_metadata["actual_completion_tokens"] == 10
        assert "validation_skipped" not in baseline_metadata
        assert "validation_outcome" not in baseline_metadata

        from run_final_benchmark_matrix import discover_artifacts
        discovered = next(
            artifact for artifact in discover_artifacts(mock_env / "extracted-ir" / run_id)
            if artifact.artifact_id == candidate_id
        )
        identity = discovered.report_identity()
        assert identity["response_mode"] == "replacement_function"
        assert identity["validation_skipped"] is False
        assert identity["validation_outcome"] == "valid_code"


@pytest.mark.parametrize("backend_option,expected_levels", [
    ("O0", {"-O0"}), ("O3", {"-O3"}), ("both", {"-O0", "-O3"}),
])
def test_extracted_ir_backend_variants_and_resume_are_idempotent(
    mock_env, monkeypatch, backend_option, expected_levels,
):
    from llmo.command import CommandResult
    from llmo.llvm import IrOperationResult

    ok = CommandResult([], ".", 0, 0.1, "out", "err")
    full_ir = mock_env / "resume-full.ll"
    full_ir.write_text('target triple = "x86_64"\ntarget datalayout = "e"\n'
                       'define i32 @fibonacci() { ret i32 0 }\n')
    run_id = f"resume-{backend_option.lower()}"
    task_dir = mock_env / "extracted-ir" / run_id / "test-model" / "fibonacci_cpp"
    task_dir.mkdir(parents=True)
    reconstructed = task_dir / "reconstructed_full.ll"
    reconstructed.write_text(full_ir.read_text())
    (task_dir / "optimized_extracted.ll").write_text(full_ir.read_text())
    (task_dir / "summary.json").write_text(json.dumps({
        "run_id": run_id, "experiment_type": "extracted-ir",
        "model_id": "test-model", "benchmark_name": "fibonacci",
        "optimization_mode": "extracted-ir", "response_mode": "replacement_function",
        "status": "valid_on_first_attempt",
        "validation": {"initial_verification_passed": True},
    }))

    monkeypatch.setattr("run_ir_optimization.shutil.which", MagicMock(return_value="/mock/tool"))
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir",
                        MagicMock(return_value=IrOperationResult(ok, full_ir)))
    call_llm = MagicMock(side_effect=AssertionError("resume must not call the LLM"))
    monkeypatch.setattr("run_ir_optimization.call_llm", call_llm)
    library = mock_env / "resume-lib.so"
    library.touch()
    compile_mock = MagicMock(return_value=IrOperationResult(ok, library))
    monkeypatch.setattr("run_ir_optimization.compile_llvm_ir_to_lib", compile_mock)
    def mock_abi(build_dir, library_path, required_symbols=None):
        build_dir.mkdir(parents=True, exist_ok=True)
        (build_dir / "abi_symbols.json").write_text('{"success": true}')
        return ok
    monkeypatch.setattr("run_ir_optimization.run_abi_symbol_check", mock_abi)
    benchmark_mock = MagicMock(return_value=_mock_comparison())
    monkeypatch.setattr("run_ir_optimization.run_benchmarks_paired", benchmark_mock)

    argv = ["run_ir_optimization.py", "--mode", "extracted-ir", "--model", "test-model",
            "--only", "fibonacci", "--output-root", str(mock_env),
            "--backend-opt-level", backend_option, "--run-id", run_id, "--resume"]
    with patch("sys.argv", argv):
        run_ir_optimization.main()
    summary = json.loads((task_dir / "summary.json").read_text())
    assert set(summary["backend_results"]) == expected_levels
    assert benchmark_mock.call_count == len(expected_levels)
    assert call_llm.call_count == 0
    for result in summary["backend_results"].values():
        artifact = (mock_env / "extracted-ir" / run_id / "artifacts" /
                    result["artifact_id"] / "artifact.json")
        assert artifact.is_file()

    compile_count = compile_mock.call_count
    benchmark_count = benchmark_mock.call_count
    with patch("sys.argv", argv):
        run_ir_optimization.main()
    assert compile_mock.call_count == compile_count
    assert benchmark_mock.call_count == benchmark_count


def test_extracted_ir_resume_keeps_invalid_candidate_terminal(mock_env, monkeypatch):
    run_id = "resume-invalid"
    task_dir = mock_env / "extracted-ir" / run_id / "test-model" / "fibonacci_cpp"
    task_dir.mkdir(parents=True)
    (task_dir / "summary.json").write_text(json.dumps({
        "optimization_mode": "extracted-ir", "status": "invalid_after_repair",
        "validation": {"final_verification_passed": False},
    }))
    monkeypatch.setattr("run_ir_optimization.shutil.which", MagicMock(return_value="/mock/tool"))
    generate = MagicMock(side_effect=AssertionError("terminal invalid result must be skipped"))
    call_llm = MagicMock(side_effect=AssertionError("terminal invalid result must not call LLM"))
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir", generate)
    monkeypatch.setattr("run_ir_optimization.call_llm", call_llm)
    argv = ["run_ir_optimization.py", "--mode", "extracted-ir", "--model", "test-model",
            "--only", "fibonacci", "--output-root", str(mock_env),
            "--backend-opt-level", "both", "--run-id", run_id, "--resume"]
    with patch("sys.argv", argv):
        run_ir_optimization.main()
    assert generate.call_count == call_llm.call_count == 0
    assert not (mock_env / "extracted-ir" / run_id / "artifacts").exists()


def _configure_constrained_extracted_ir(mock_env, monkeypatch, available_output_tokens):
    from llmo.command import CommandResult
    from llmo.llvm import IrOperationResult

    ok = CommandResult([], ".", 0, 0.1, "out", "err")
    full_ir = mock_env / "constrained_full.ll"
    reduced_ir = mock_env / "constrained_extracted.ll"
    module = ('target triple = "x86_64"\ntarget datalayout = "e"\n'
              'define i32 @fibonacci() { ret i32 0 }\n')
    full_ir.write_text(module)
    reduced_ir.write_text(module)
    monkeypatch.setattr("run_ir_optimization.shutil.which", MagicMock(return_value="/mock/llvm-tool"))
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir", MagicMock(return_value=IrOperationResult(ok, full_ir)))
    monkeypatch.setattr("run_ir_optimization.llvm_ir_defines_symbol", MagicMock(return_value=True))
    monkeypatch.setattr("run_ir_optimization.extract_llvm_function", MagicMock(return_value=IrOperationResult(ok, reduced_ir)))
    monkeypatch.setattr("run_ir_optimization.validate_llvm_ir_with_assembler", MagicMock(return_value=IrOperationResult(ok, mock_env / "valid.bc")))
    monkeypatch.setattr("run_ir_optimization.count_tokens", lambda text: 2000 if text.lstrip().startswith("define ") else 100)

    # calculate_token_budget adds two token counts, 50 template tokens, and a
    # 1024-token safety margin.
    monkeypatch.setattr("llmo.llama.count_tokens", lambda text: 100)
    monkeypatch.setattr("llmo.llama.EFFECTIVE_LLAMA_CTX_SIZE", available_output_tokens + 1274)
    return ok


def test_extracted_ir_calls_llm_when_only_compact_minimum_fits(mock_env, monkeypatch):
    from llmo.llama import ChatCompletionResult

    _configure_constrained_extracted_ir(mock_env, monkeypatch, available_output_tokens=700)
    call = MagicMock(return_value=ChatCompletionResult(
        content="NO_CHANGE", finish_reason="stop", prompt_tokens=100,
        completion_tokens=2, total_tokens=102, raw_response={},
    ))
    monkeypatch.setattr("run_ir_optimization.call_llm", call)
    argv = ["run_ir_optimization.py", "--mode", "extracted-ir", "--model", "test-model",
            "--only", "fibonacci", "--output-root", str(mock_env), "--backend-opt-level", "O3",
            "--benchmark-repetitions", "1", "--run-id", "compact-context-fits"]
    with patch("sys.argv", argv):
        run_ir_optimization.main()

    summary = json.loads((mock_env / "extracted-ir" / "compact-context-fits" / "test-model" /
                          "fibonacci_cpp" / "summary.json").read_text())
    assert summary["status"] == "completed"
    assert summary["response_mode"] == "no_change"
    assert summary["estimated_target_function_tokens"] == 2000
    assert summary["min_output_tokens"] == 512
    assert summary["estimated_available_output_tokens"] == 700
    assert summary["configured_max_output_tokens"] == 3256
    assert summary["llm_result"]["requested_max_tokens"] == 700
    assert call.call_args.kwargs["max_tokens"] == 700


def test_extracted_ir_skips_when_compact_minimum_does_not_fit(mock_env, monkeypatch):
    _configure_constrained_extracted_ir(mock_env, monkeypatch, available_output_tokens=511)
    call = MagicMock()
    monkeypatch.setattr("run_ir_optimization.call_llm", call)
    argv = ["run_ir_optimization.py", "--mode", "extracted-ir", "--model", "test-model",
            "--only", "fibonacci", "--output-root", str(mock_env), "--backend-opt-level", "O3",
            "--benchmark-repetitions", "1", "--run-id", "compact-context-too-small"]
    with patch("sys.argv", argv):
        run_ir_optimization.main()

    summary = json.loads((mock_env / "extracted-ir" / "compact-context-too-small" / "test-model" /
                          "fibonacci_cpp" / "summary.json").read_text())
    assert summary["status"] == "context_insufficient"
    assert summary["min_output_tokens"] == 512
    assert summary["estimated_available_output_tokens"] == 511
    call.assert_not_called()

def test_extracted_ir_missing_target_is_clean_status(mock_env, monkeypatch):
    tmp_path = mock_env
    from llmo.command import CommandResult
    from llmo.llvm import IrOperationResult
    full_ir = tmp_path / "missing.ll"
    full_ir.write_text('target triple = "x86_64"\ntarget datalayout = "e"\n')
    monkeypatch.setattr("run_ir_optimization.shutil.which", MagicMock(return_value="/mock/llvm-tool"))
    monkeypatch.setattr("run_ir_optimization.generate_llvm_ir", MagicMock(return_value=IrOperationResult(
        CommandResult([], ".", 0, 0.1, "out", "err"), full_ir)))
    monkeypatch.setattr("run_ir_optimization.llvm_ir_defines_symbol", MagicMock(return_value=False))
    argv = ["run_ir_optimization.py", "--mode", "extracted-ir", "--model", "test-model",
            "--only", "fibonacci", "--output-root", str(tmp_path), "--run-id", "missing-target"]
    with patch("sys.argv", argv):
        run_ir_optimization.main()
    summary = json.loads((tmp_path / "extracted-ir" / "missing-target" / "test-model" / "fibonacci_cpp" / "summary.json").read_text())
    assert summary["status"] == "extraction_target_missing"
    assert summary["target_llvm_symbol"] == "fibonacci"

def test_extracted_ir_production_preflight_rejects_missing_tools(mock_env, monkeypatch):
    monkeypatch.setattr("run_ir_optimization.shutil.which", MagicMock(return_value=None))
    with patch("sys.argv", ["run_ir_optimization.py", "--mode", "extracted-ir"]):
        assert run_ir_optimization.main() == 2
    run_ir_optimization.start_llama_server.assert_not_called()

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
