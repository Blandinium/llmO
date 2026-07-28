import unittest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import shutil
import json
import os

import run_iterative_cpp_optimization as script
from llmo.command import CommandResult
from llmo.remarks import Remark
from run_iterative_cpp_optimization import IterationResult

class TestRegressionFixes(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path("./test_regression_artifacts")
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True)
        
        self.model_config = script.LlmModelConfig(name="test-model", alias="test-model")
        self.target_source = self.temp_dir / "fibonacci.cpp"
        self.target_source.write_text("uint64_t fibonacci(int n) { return n; }", encoding="utf-8")
        self.headers = "// library.h\n"

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def _setup_baseline_mocks(self, mock_build, mock_find_libsut, mock_abi, mock_bench=None):
        mock_build.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        mock_find_libsut.return_value = self.temp_dir / "libSUT.so"
        (self.temp_dir / "libSUT.so").touch()
        mock_abi.return_value = CommandResult(["nm"], ".", 0, 0.1, str(self.temp_dir/"abi_stdout.txt"), str(self.temp_dir/"abi_stderr.txt"))
        if mock_bench:
            def mock_bench_baseline(build_dir, libsut, target, run_all):
                res_file = build_dir / f"benchmark_0_fibonacci_results.json"
                res_file.write_text(json.dumps({"calls_per_second": 100.0}), encoding="utf-8")
                return [CommandResult([], "", 0, 0.1, str(res_file.with_suffix(".txt")), "")]
            mock_bench.side_effect = mock_bench_baseline

    @patch("run_iterative_cpp_optimization.call_llm")
    def test_abi_failure_diagnostics_in_prompt(self, mock_llm):
        # Setup: Compilation succeeds, ABI fails
        compile_res = CommandResult(["clang++"], ".", 0, 0.1, str(self.temp_dir/"c_out.txt"), str(self.temp_dir/"c_err.txt"))
        abi_res = CommandResult(["nm"], ".", 1, 0.1, str(self.temp_dir/"abi_out.txt"), str(self.temp_dir/"abi_err.txt"))
        
        (self.temp_dir/"c_out.txt").write_text("compile success", encoding="utf-8")
        (self.temp_dir/"c_err.txt").write_text("", encoding="utf-8")
        (self.temp_dir/"abi_out.txt").write_text("missing symbol: fibonacci", encoding="utf-8")
        (self.temp_dir/"abi_err.txt").write_text("ABI check failed", encoding="utf-8")
        
        mock_llm.return_value = "uint64_t fibonacci(int n) { return n; }"
        
        repair_dir = self.temp_dir / "repair"
        script.run_repair_step(
            "model", self.target_source, self.target_source, 1, 1, repair_dir, self.headers,
            compile_result=compile_res, abi_result=abi_res
        )
        
        # Verify call_llm was called with a prompt containing ABI diagnostics
        args, kwargs = mock_llm.call_args
        prompt = args[1]
        self.assertIn("ABI validation diagnostics:", prompt)
        self.assertIn("missing symbol: fibonacci", prompt)
        self.assertIn("ABI check failed", prompt)

    @patch("run_iterative_cpp_optimization.run_repair_step")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.find_libsut")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    def test_fresh_diagnostics_in_initial_repair_loop(self, mock_bench, mock_abi, mock_libsut, mock_build, mock_compile, mock_repair):
        self._setup_baseline_mocks(mock_build, mock_libsut, mock_abi, mock_bench)
        # Setup: opt_res fails initially
        initial_comp_res = CommandResult(["clang++"], ".", 1, 0.1, str(self.temp_dir/"initial_out.txt"), str(self.temp_dir/"initial_err.txt"))
        
        # We need to distinguish between baseline build (success) and remarks build (fail)
        mock_compile.return_value = initial_comp_res
        (self.temp_dir/"initial_err.txt").write_text("error A", encoding="utf-8")
        
        with patch("run_iterative_cpp_optimization.LLM_MODELS", []):
            res = script.optimize_target(
                self.model_config, self.target_source, 1, self.temp_dir / "output",
                self.headers, False
            )
        
        # It should have stopped because remark compilation failed and we no longer repair it here (terminal stop choice)
        self.assertEqual(res["stopped_reason"], "remark_compilation_failed")
        self.assertEqual(mock_repair.call_count, 0)

    @patch("run_iterative_cpp_optimization.run_optimization_iteration")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.find_libsut")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    def test_stop_on_no_change(self, mock_bench, mock_find, mock_abi, mock_build, mock_opt):
        self._setup_baseline_mocks(mock_build, mock_find, mock_abi, mock_bench)
        
        # First iteration: no change
        source_1 = self.temp_dir / "source1.cpp"
        source_1.write_text(self.target_source.read_text(), encoding="utf-8")
        
        mock_opt.side_effect = [
            IterationResult(1, "optimization", True, source_1, metadata={"remark_count_remaining": 1}),
        ]
        
        res = script.optimize_target(
            self.model_config, self.target_source, 2, self.temp_dir / "output",
            self.headers, False
        )
        
        self.assertEqual(res["stopped_reason"], "no_change")
        self.assertEqual(mock_opt.call_count, 1)

if __name__ == "__main__":
    unittest.main()
