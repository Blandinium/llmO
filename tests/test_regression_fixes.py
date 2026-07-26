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
    def test_fresh_diagnostics_in_initial_repair_loop(self, mock_compile, mock_repair):
        # Setup: opt_res fails initially
        initial_comp_res = CommandResult(["clang++"], ".", 1, 0.1, str(self.temp_dir/"initial_out.txt"), str(self.temp_dir/"initial_err.txt"))
        mock_compile.return_value = initial_comp_res
        (self.temp_dir/"initial_err.txt").write_text("error A", encoding="utf-8")
        
        # First repair attempt fails with error B
        repair_source_1 = self.temp_dir / "repair1.cpp"
        repair_source_1.write_text("source B", encoding="utf-8")
        compile_res_B = CommandResult(["clang++"], ".", 1, 0.1, str(self.temp_dir/"repair1_out.txt"), str(self.temp_dir/"repair1_err.txt"))
        (self.temp_dir/"repair1_err.txt").write_text("error B", encoding="utf-8")
        
        # Second repair attempt succeeds
        repair_source_2 = self.temp_dir / "repair2.cpp"
        repair_source_2.write_text("uint64_t fibonacci(int n) { return n; }", encoding="utf-8")
        
        mock_repair.side_effect = [
            IterationResult(1, "repair_initial_01", False, repair_source_1, compile_result=compile_res_B, metadata={}),
            IterationResult(1, "repair_initial_02", True, repair_source_2, metadata={}) 
        ]
        
        # To avoid infinite loop, we make the next optimization call "stop"
        with patch("run_iterative_cpp_optimization.run_optimization_iteration") as mock_opt:
            mock_opt.side_effect = [
                IterationResult(1, "optimization", False, self.target_source, compile_result=initial_comp_res), # First optimization attempt fails
                IterationResult(1, "optimization", False, repair_source_2, metadata={"stop_reason": "no_unseen_remarks"}) # Stop after repair
            ]
            
            with patch("run_iterative_cpp_optimization.LLM_MODELS", []):
                script.optimize_target(
                    self.model_config, self.target_source, 1, self.temp_dir / "output",
                    self.headers, False, False
                )
        
        # Check second call to run_repair_step
        self.assertEqual(mock_repair.call_count, 2)
        args, kwargs = mock_repair.call_args_list[1]
        # It should have been called with compile_res_B (error B)
        self.assertEqual(kwargs["compile_result"].stderr_file, str(self.temp_dir/"repair1_err.txt"))

    @patch("run_iterative_cpp_optimization.run_optimization_iteration")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_no_overwrite_on_no_change(self, mock_find, mock_abi, mock_build, mock_opt):
        # First iteration: no change
        source_1 = self.temp_dir / "source1.cpp"
        source_1.write_text(self.target_source.read_text(), encoding="utf-8")
        
        # Second iteration: change
        source_2 = self.temp_dir / "source2.cpp"
        source_2.write_text("changed source", encoding="utf-8")
        
        mock_opt.side_effect = [
            IterationResult(1, "optimization", True, source_1, metadata={"remark_count_remaining": 1}),
            IterationResult(1, "optimization", True, source_2, metadata={"remark_count_remaining": 0})
        ]
        
        mock_build.return_value = CommandResult([], "", 0, 0.1, "", "")
        mock_abi.return_value = CommandResult([], "", 0, 0.1, "", "")
        mock_find.return_value = self.temp_dir / "libSUT.so"
        (self.temp_dir / "libSUT.so").touch()

        script.optimize_target(
            self.model_config, self.target_source, 2, self.temp_dir / "output",
            self.headers, False, False
        )
        
        # In the fixed version, there should be separate attempt directories or some way to distinguish
        # If I implement attempt_XX subdirs:
        iter1_dir = self.temp_dir / "output" / "iteration_01"
        self.assertTrue((iter1_dir / "attempt_01").exists())
        self.assertTrue((iter1_dir / "attempt_02").exists())

if __name__ == "__main__":
    unittest.main()
