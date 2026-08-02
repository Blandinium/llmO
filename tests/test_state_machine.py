import unittest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import shutil
import json
import os

# Import the stuff we want to test
import run_iterative_cpp_optimization as script
from llmo.command import CommandResult
from llmo.llama import LlmModelConfig, LlmCallResult
from tests.test_utils import make_benchmark_result, mock_abi_check_success
from llmo.benchmark_protocol import BenchmarkProtocol, BenchmarkComparison, BenchmarkStatistics

class TestStateMachine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path("./test_artifacts")
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True)
        
        self.model_config = LlmModelConfig(name="test-model", alias="test-model")
        self.target_source = self.temp_dir / "fibonacci.cpp"
        self.target_source.write_text("uint64_t fibonacci(int n) { return n; }", encoding="utf-8")
        
        self.headers = "// library.h\n"
        
    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def _setup_baseline_mocks(self, mock_build, mock_find_libsut, mock_abi, mock_bench):
        mock_build.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        mock_find_libsut.return_value = self.temp_dir / "libSUT.so"
        (self.temp_dir / "libSUT.so").write_text("dummy", encoding="utf-8")
        
        def mock_abi_impl(build_dir, libsut, required_symbols=None):
            return mock_abi_check_success(build_dir)
        mock_abi.side_effect = mock_abi_impl
        
        def mock_bench_baseline(build_dir, libsut, target, run_all, artifact_id="unknown", iteration=0, sequence_index=0):
            return [make_benchmark_result(build_dir, function_name=target, calls_per_second=100.0, artifact_id=artifact_id, iteration=iteration, sequence_index=sequence_index)]
        mock_bench.side_effect = mock_bench_baseline

    def _setup_iteration_mocks(self, mock_compile, mock_parse):
        def side_effect_compile(source, output_dir):
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "optimization_record.yaml").write_text("dummy", encoding="utf-8")
            return CommandResult([], "", 0, 0.1, "", "")
        mock_compile.side_effect = side_effect_compile

    def _setup_comparison_mock(self, mock_paired, classification="improved", improvement=10.0):
        def mock_paired_impl(cand_lib, base_lib, target, protocol, candidate_id, baseline_id):
            return BenchmarkComparison(
                baseline_artifact_id=baseline_id,
                candidate_artifact_id=candidate_id,
                baseline_statistics=BenchmarkStatistics(protocol.repetitions, protocol.repetitions, 100.0),
                candidate_statistics=BenchmarkStatistics(protocol.repetitions, protocol.repetitions, 100.0 * (1 + improvement/100.0)),
                relative_change_percent=improvement,
                classification=classification,
                sequence=[baseline_id, candidate_id],
                noise_threshold_percent=protocol.noise_threshold_percent
            )
        mock_paired.side_effect = mock_paired_impl

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.run_benchmarks_paired")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_successful_optimization_hill_climbing(self, mock_find_libsut, mock_paired, mock_bench, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.remarks import Remark
        from llmo.llama import ChatCompletionResult
        self._setup_baseline_mocks(mock_build, mock_find_libsut, mock_abi, mock_bench)
        self._setup_iteration_mocks(mock_compile, mock_parse)
        self._setup_comparison_mock(mock_paired, "improved", 50.0)
        
        # Iteration 1
        mock_compile.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fibonacci.cpp", 10, 1, "msg", "RAW")]
        
        mock_llm.return_value = ChatCompletionResult(
            content="```cpp\nuint64_t fibonacci(int n) { return n + 1; }\n```",
            finish_reason="stop",
            prompt_tokens=100, completion_tokens=100, total_tokens=200,
            raw_response={}
        )
        
        protocol = BenchmarkProtocol(3, 42, 2.0, "paired")
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False, protocol, "test-run"
        )
        
        self.assertEqual(res["completed_optimization_passes"], 1)
        self.assertEqual(res["best_iteration"], 1)
        self.assertFalse(res["best_is_baseline"])
        
    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.run_benchmarks_paired")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_rejected_slower_candidate(self, mock_find_libsut, mock_paired, mock_bench, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.remarks import Remark
        from llmo.llama import ChatCompletionResult
        self._setup_baseline_mocks(mock_build, mock_find_libsut, mock_abi, mock_bench)
        self._setup_iteration_mocks(mock_compile, mock_parse)
        self._setup_comparison_mock(mock_paired, "regressed", -20.0)
        
        mock_compile.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fibonacci.cpp", 10, 1, "msg", "RAW")]
        
        mock_llm.return_value = ChatCompletionResult(
            content="```cpp\nuint64_t fibonacci(int n) { return n - 1; }\n```",
            finish_reason="stop",
            prompt_tokens=100, completion_tokens=100, total_tokens=200,
            raw_response={}
        )
        
        protocol = BenchmarkProtocol(3, 42, 2.0, "paired")
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False, protocol, "test-run"
        )
        
        self.assertEqual(res["completed_optimization_passes"], 1)
        self.assertEqual(res["best_iteration"], 0)
        self.assertTrue(res["best_is_baseline"])

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.run_benchmarks_paired")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_rejected_due_to_noise(self, mock_find_libsut, mock_paired, mock_bench, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.remarks import Remark
        from llmo.llama import ChatCompletionResult
        self._setup_baseline_mocks(mock_build, mock_find_libsut, mock_abi, mock_bench)
        self._setup_iteration_mocks(mock_compile, mock_parse)
        self._setup_comparison_mock(mock_paired, "unchanged_within_noise", 1.0)
        
        mock_llm.return_value = ChatCompletionResult(
            content="uint64_t fibonacci(int n) { return n + 1; }",
            finish_reason="stop",
            prompt_tokens=100, completion_tokens=100, total_tokens=200,
            raw_response={}
        )
        
        protocol = BenchmarkProtocol(3, 42, 2.0, "paired")
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False, protocol, "test-run"
        )
        
        self.assertEqual(res["best_iteration"], 0)
        self.assertTrue(res["best_is_baseline"])

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    def test_no_change_immediate_stop(self, mock_llm, mock_compile, mock_parse):
        from llmo.remarks import Remark
        from llmo.llama import ChatCompletionResult
        with patch("run_iterative_cpp_optimization.build_full_library") as mock_build, \
             patch("run_iterative_cpp_optimization.find_libsut") as mock_find, \
             patch("run_iterative_cpp_optimization.run_abi_symbol_check") as mock_abi, \
             patch("run_iterative_cpp_optimization.run_benchmarks_for_lib") as mock_bench, \
             patch("run_iterative_cpp_optimization.run_benchmarks_paired") as mock_paired:
            
            self._setup_baseline_mocks(mock_build, mock_find, mock_abi, mock_bench)
            self._setup_iteration_mocks(mock_compile, mock_parse)
            
            mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fibonacci.cpp", 10, 1, "msg", "RAW")]
            mock_llm.return_value = ChatCompletionResult(
                content="uint64_t fibonacci(int n) { return n; }",
                finish_reason="stop",
                prompt_tokens=100, completion_tokens=100, total_tokens=200,
                raw_response={}
            )
            
            protocol = BenchmarkProtocol(3, 42, 2.0, "paired")
            res = script.optimize_target(
                self.model_config, self.target_source, 3, self.temp_dir / "output", 
                self.headers, False, protocol, "test-run"
            )
            
            self.assertEqual(res["stopped_reason"], "no_change")
            self.assertEqual(mock_llm.call_count, 1)

if __name__ == '__main__':
    unittest.main()
