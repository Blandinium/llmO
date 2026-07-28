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
        mock_abi.return_value = CommandResult(["nm"], ".", 0, 0.1, str(self.temp_dir/"abi_stdout.txt"), str(self.temp_dir/"abi_stderr.txt"))
        
        def mock_bench_baseline(build_dir, libsut, target, run_all):
            res_file = build_dir / f"benchmark_0_fibonacci_results.json"
            res_file.write_text(json.dumps({"calls_per_second": 100.0}), encoding="utf-8")
            return [CommandResult([], "", 0, 0.1, str(res_file.with_suffix(".txt")), "")]
        mock_bench.side_effect = mock_bench_baseline

    def _setup_iteration_mocks(self, mock_compile, mock_parse):
        def side_effect_compile(source, output_dir):
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "optimization_record.yaml").write_text("dummy", encoding="utf-8")
            return CommandResult([], "", 0, 0.1, "", "")
        mock_compile.side_effect = side_effect_compile

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_successful_optimization_hill_climbing(self, mock_find_libsut, mock_bench, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.remarks import Remark
        self._setup_baseline_mocks(mock_build, mock_find_libsut, mock_abi, mock_bench)
        self._setup_iteration_mocks(mock_compile, mock_parse)
        
        # Iteration 1: 150 calls/s (better)
        mock_compile.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fibonacci.cpp", 10, 1, "msg", "RAW")]
        mock_llm.return_value = "```cpp\nuint64_t fibonacci(int n) { return n + 1; }\n```"
        
        orig_bench_side_effect = mock_bench.side_effect
        def mock_bench_iterative(build_dir, libsut, target, run_all):
            if "baseline" in str(build_dir):
                return orig_bench_side_effect(build_dir, libsut, target, run_all)
            cps = 150.0
            res_file = build_dir / f"benchmark_0_fibonacci_results.json"
            res_file.write_text(json.dumps({"calls_per_second": cps}), encoding="utf-8")
            return [CommandResult([], "", 0, 0.1, str(res_file.with_suffix(".txt")), "")]
        mock_bench.side_effect = mock_bench_iterative

        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False
        )
        
        self.assertEqual(res["completed_optimization_passes"], 1)
        self.assertEqual(res["best_iteration"], 1)
        self.assertEqual(res["best_calls_per_second"], 150.0)
        self.assertFalse(res["best_is_baseline"])
        
    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_rejected_slower_candidate(self, mock_find_libsut, mock_bench, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.remarks import Remark
        self._setup_baseline_mocks(mock_build, mock_find_libsut, mock_abi, mock_bench)
        self._setup_iteration_mocks(mock_compile, mock_parse)
        
        # Iteration 1: 80 calls/s (worse)
        mock_compile.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fibonacci.cpp", 10, 1, "msg", "RAW")]
        mock_llm.return_value = "```cpp\nuint64_t fibonacci(int n) { return n - 1; }\n```"
        
        orig_bench_side_effect = mock_bench.side_effect
        def mock_bench_iterative(build_dir, libsut, target, run_all):
            if "baseline" in str(build_dir):
                return orig_bench_side_effect(build_dir, libsut, target, run_all)
            cps = 80.0
            res_file = build_dir / f"benchmark_0_fibonacci_results.json"
            res_file.write_text(json.dumps({"calls_per_second": cps}), encoding="utf-8")
            return [CommandResult([], "", 0, 0.1, str(res_file.with_suffix(".txt")), "")]
        mock_bench.side_effect = mock_bench_iterative

        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False
        )
        
        self.assertEqual(res["completed_optimization_passes"], 1)
        self.assertEqual(res["best_iteration"], 0)
        self.assertEqual(res["best_calls_per_second"], 100.0)
        self.assertTrue(res["best_is_baseline"])
        self.assertEqual(res["message"], "Optimization attempts made, but baseline remains best.")

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    def test_no_change_immediate_stop(self, mock_llm, mock_compile, mock_parse):
        from llmo.remarks import Remark
        # We need to mock baseline first
        with patch("run_iterative_cpp_optimization.build_full_library") as mock_build, \
             patch("run_iterative_cpp_optimization.find_libsut") as mock_find, \
             patch("run_iterative_cpp_optimization.run_abi_symbol_check") as mock_abi, \
             patch("run_iterative_cpp_optimization.run_benchmarks_for_lib") as mock_bench:
            
            self._setup_baseline_mocks(mock_build, mock_find, mock_abi, mock_bench)
            self._setup_iteration_mocks(mock_compile, mock_parse)
            
            mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fibonacci.cpp", 10, 1, "msg", "RAW")]
            # Return identical source
            mock_llm.return_value = "uint64_t fibonacci(int n) { return n; }"
            
            res = script.optimize_target(
                self.model_config, self.target_source, 3, self.temp_dir / "output", 
                self.headers, False
            )
            
            self.assertEqual(res["stopped_reason"], "no_change")
            self.assertEqual(mock_llm.call_count, 1)

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.find_libsut")
    @patch("run_iterative_cpp_optimization.count_tokens")
    def test_regression_after_improvement_hill_climbing(self, mock_count, mock_find_libsut, mock_bench, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.remarks import Remark
        self._setup_baseline_mocks(mock_build, mock_find_libsut, mock_abi, mock_bench)
        self._setup_iteration_mocks(mock_compile, mock_parse)
        mock_count.return_value = 10
        
        # Iteration 1: 150 calls/s (better than 100)
        # Iteration 2: 120 calls/s (worse than 150)
        # Iteration 3: 180 calls/s (better than 150)
        
        mock_llm.side_effect = [
            "uint64_t fibonacci(int n) { return n + 1; }", # Iter 1
            "uint64_t fibonacci(int n) { return n + 2; }", # Iter 2
            "uint64_t fibonacci(int n) { return n + 3; }"  # Iter 3
        ]
        
        cps_values = [100.0, 150.0, 120.0, 180.0]
        cps_iter = iter(cps_values)
        
        def mock_bench_hill(build_dir, libsut, target, run_all):
            cps = next(cps_iter)
            res_file = build_dir / f"benchmark_0_fibonacci_results.json"
            res_file.write_text(json.dumps({"calls_per_second": cps}), encoding="utf-8")
            return [CommandResult([], "", 0, 0.1, str(res_file.with_suffix(".txt")), "")]
        mock_bench.side_effect = mock_bench_hill

        sources_compiled = []
        def side_effect_compile(source, output_dir):
            sources_compiled.append(source.read_text())
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "optimization_record.yaml").write_text("dummy", encoding="utf-8")
            return CommandResult([], "", 0, 0.1, "", "")
        mock_compile.side_effect = side_effect_compile

        # Provide unique remarks for each iteration call to ensure it keeps going
        remark1 = Remark("Missed", "p", "n1", "fibonacci", "fib.cpp", 1, 1, "msg1", "RAW1")
        remark2 = Remark("Missed", "p", "n2", "fibonacci", "fib.cpp", 2, 2, "msg2", "RAW2")
        remark3 = Remark("Missed", "p", "n3", "fibonacci", "fib.cpp", 3, 3, "msg3", "RAW3")
        
        mock_parse.side_effect = [
            [remark1],
            [remark2],
            [remark3]
        ]

        res = script.optimize_target(
            self.model_config, self.target_source, 3, self.temp_dir / "output", 
            self.headers, False
        )
        
        self.assertEqual(res["completed_optimization_passes"], 3)
        self.assertEqual(res["best_iteration"], 3)
        self.assertEqual(res["best_calls_per_second"], 180.0)
        
        # Check source passed to each optimization pass (compilation for remarks)
        self.assertEqual(sources_compiled[0], "uint64_t fibonacci(int n) { return n; }")       # Baseline
        self.assertEqual(sources_compiled[1], "uint64_t fibonacci(int n) { return n + 1; }\n") # Iter 1 (accepted)
        self.assertEqual(sources_compiled[2], "uint64_t fibonacci(int n) { return n + 1; }\n") # Iter 1 again (Iter 2 rejected)

    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.find_libsut")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.call_llm")
    def test_baseline_benchmark_command_fails(self, mock_llm, mock_bench, mock_abi, mock_find_libsut, mock_build):
        mock_build.return_value = CommandResult([], "", 0, 0.1, "", "")
        mock_find_libsut.return_value = self.temp_dir / "libSUT.so"
        (self.temp_dir / "libSUT.so").write_text("dummy", encoding="utf-8")
        mock_abi.return_value = CommandResult([], "", 0, 0.1, "", "")
        
        # Benchmark command exits non-zero
        mock_bench.return_value = [CommandResult(["runner"], ".", 1, 0.1, str(self.temp_dir/"stdout.txt"), "")]
        
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False
        )
        
        self.assertEqual(res["success"], False)
        self.assertEqual(res["stopped_reason"], "baseline_benchmark_failed")
        mock_llm.assert_not_called()

    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.find_libsut")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.call_llm")
    def test_baseline_missing_json(self, mock_llm, mock_bench, mock_abi, mock_find_libsut, mock_build):
        mock_build.return_value = CommandResult([], "", 0, 0.1, "", "")
        mock_find_libsut.return_value = self.temp_dir / "libSUT.so"
        (self.temp_dir / "libSUT.so").touch()
        mock_abi.return_value = CommandResult([], "", 0, 0.1, "", "")
        
        # Benchmark command succeeds but no JSON file is created
        mock_bench.return_value = [CommandResult(["runner"], ".", 0, 0.1, str(self.temp_dir/"stdout.txt"), "")]
        
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False
        )
        
        self.assertEqual(res["success"], False)
        self.assertEqual(res["stopped_reason"], "baseline_benchmark_failed")

    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.find_libsut")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.call_llm")
    def test_baseline_invalid_cps(self, mock_llm, mock_bench, mock_abi, mock_find_libsut, mock_build):
        mock_build.return_value = CommandResult([], "", 0, 0.1, "", "")
        mock_find_libsut.return_value = self.temp_dir / "libSUT.so"
        (self.temp_dir / "libSUT.so").write_text("dummy", encoding="utf-8")
        mock_abi.return_value = CommandResult([], "", 0, 0.1, "", "")
        
        def mock_bench_invalid(build_dir, libsut, target, run_all):
            res_file = build_dir / f"benchmark_0_fibonacci_results.json"
            res_file.write_text(json.dumps({"calls_per_second": -5.0}), encoding="utf-8")
            return [CommandResult([], "", 0, 0.1, str(res_file.with_suffix(".txt")), "")]
        mock_bench.side_effect = mock_bench_invalid
        
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False
        )
        
        self.assertEqual(res["success"], False)
        self.assertEqual(res["stopped_reason"], "baseline_benchmark_failed")

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_repaired_candidate_performance_check(self, mock_find_libsut, mock_bench, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.remarks import Remark
        self._setup_baseline_mocks(mock_build, mock_find_libsut, mock_abi, mock_bench)
        self._setup_iteration_mocks(mock_compile, mock_parse)
        
        mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fib.cpp", 1, 1, "msg", "RAW")]
        mock_llm.return_value = "```cpp\nsyntax error\n```"
        
        # Build fails for candidate
        mock_build.side_effect = [
            CommandResult([], "", 0, 0.1, "", ""), # Baseline
            CommandResult([], "", 1, 0.1, "", "")  # Candidate fails
        ]
        
        # Repair succeeds but performance is worse
        repaired_source = self.temp_dir / "repaired.cpp"
        repaired_source.write_text("uint64_t fibonacci(int n) { return n - 1; }", encoding="utf-8")
        
        with patch("run_iterative_cpp_optimization.run_repair_step") as mock_repair:
            from run_iterative_cpp_optimization import IterationResult
            mock_repair.return_value = IterationResult(
                iteration=1, type="repair_01", success=True, 
                source_file=repaired_source, metadata={"duration_seconds": 1.0}
            )
            
            # 80 calls/s for repaired candidate (baseline is 100)
            cps_iter = iter([100.0, 80.0])
            def mock_bench_cps(build_dir, libsut, target, run_all):
                cps = next(cps_iter)
                res_file = build_dir / f"benchmark_0_fibonacci_results.json"
                res_file.write_text(json.dumps({"calls_per_second": cps}), encoding="utf-8")
                return [CommandResult([], "", 0, 0.1, str(res_file.with_suffix(".txt")), "")]
            mock_bench.side_effect = mock_bench_cps

            res = script.optimize_target(
                self.model_config, self.target_source, 1, self.temp_dir / "output", 
                self.headers, False
            )
            
            # Candidate should be rejected
            self.assertEqual(res["best_iteration"], 0)
            self.assertTrue(res["best_is_baseline"])
            # The iteration result metadata should show it was rejected
            self.assertEqual(res["iterations"][-1]["metadata"]["accepted_as_best"], False)
            self.assertEqual(res["iterations"][-1]["metadata"]["candidate_calls_per_second"], 80.0)

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_remark_consumption_after_rejection(self, mock_find_libsut, mock_bench, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.remarks import Remark
        self._setup_baseline_mocks(mock_build, mock_find_libsut, mock_abi, mock_bench)
        self._setup_iteration_mocks(mock_compile, mock_parse)
        
        remark1 = Remark("Missed", "pass1", "name1", "fibonacci", "fib.cpp", 1, 1, "msg1", "RAW1")
        remark2 = Remark("Missed", "pass2", "name2", "fibonacci", "fib.cpp", 2, 2, "msg2", "RAW2")
        
        # First pass sees remark1. Second pass sees both.
        mock_parse.side_effect = [
            [remark1],
            [remark1, remark2]
        ]
        
        prompts = []
        def mock_llm_capture(model, prompt, system=None):
            prompts.append(prompt)
            return "uint64_t fibonacci(int n) { return n - 1; }"
        mock_llm.side_effect = mock_llm_capture
        
        # All candidates are 80 calls/s (rejected)
        cps_iter = iter([100.0, 80.0, 80.0])
        def mock_bench_cps(build_dir, libsut, target, run_all):
            cps = next(cps_iter)
            res_file = build_dir / f"benchmark_0_fibonacci_results.json"
            res_file.write_text(json.dumps({"calls_per_second": cps}), encoding="utf-8")
            return [CommandResult([], "", 0, 0.1, str(res_file.with_suffix(".txt")), "")]
        mock_bench.side_effect = mock_bench_cps

        script.optimize_target(
            self.model_config, self.target_source, 2, self.temp_dir / "output", 
            self.headers, False
        )
        
        self.assertIn("RAW1", prompts[0])
        # remark1 should be filtered out in the second prompt even though Iter 1 was rejected
        self.assertNotIn("RAW1", prompts[1])
        self.assertIn("RAW2", prompts[1])

if __name__ == '__main__':
    unittest.main()
