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
        # Use uint64_t to match contains_target_function_definition
        self.target_source.write_text("uint64_t fibonacci(int n) { return n; }", encoding="utf-8")
        
        self.headers = "// library.h\n"
        
    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_successful_optimization_flow(self, mock_find_libsut, mock_bench, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.command import CommandResult
        from llmo.remarks import Remark
        # Setup mocks
        mock_compile.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        
        # Create dummy remark file so .exists() is true
        iter_dir = self.temp_dir / "output" / "iteration_01" / "attempt_01"
        iter_dir.mkdir(parents=True, exist_ok=True)
        (iter_dir / "optimization_record.yaml").write_text("dummy", encoding="utf-8")
        
        mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fibonacci.cpp", 10, 1, "msg", "RAW")]
        
        mock_llm.return_value = "```cpp\nuint64_t fibonacci(int n) { return n + 1; }\n```"
        mock_build.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        mock_abi_res = CommandResult(["nm"], ".", 0, 0.1, str(self.temp_dir/"abi_stdout.txt"), str(self.temp_dir/"abi_stderr.txt"))
        mock_abi.return_value = mock_abi_res
        
        mock_find_libsut.return_value = self.temp_dir / "libSUT.so"
        (self.temp_dir / "libSUT.so").write_text("dummy", encoding="utf-8")

        # Run
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False, False
        )
        
        self.assertEqual(res["completed_optimization_passes"], 1)
        self.assertEqual(res["stopped_reason"], "completed")
        self.assertTrue(Path(res["final_source"]).exists())
        
        # Verify self-contained final directory
        final_dir = self.temp_dir / "output" / "final"
        self.assertTrue((final_dir / "optimized_fibonacci.cpp").exists())
        self.assertTrue((final_dir / "libSUT.so").exists())
        self.assertTrue((final_dir / "final_metadata.json").exists())
        
    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_repair_step")
    def test_compile_failure_repair_flow(self, mock_repair, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        # 1. First call to LLM produces uncompilable code
        mock_compile.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        
        # Create dummy remark file so .exists() is true
        iter_dir = self.temp_dir / "output" / "iteration_01" / "attempt_01"
        iter_dir.mkdir(parents=True, exist_ok=True)
        (iter_dir / "optimization_record.yaml").write_text("dummy", encoding="utf-8")

        from llmo.remarks import Remark
        mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fibonacci.cpp", 10, 1, "msg", "RAW")]
        
        mock_llm.return_value = "```cpp\nuint64_t fibonacci(int n) { syntax error }\n```"
        
        # Build fails
        mock_build.return_value = CommandResult([], "", 1, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        
        # 2. Repair step produces compilable code
        repaired_source = self.temp_dir / "repaired.cpp"
        repaired_source.write_text("uint64_t fibonacci(int n) { return n; }", encoding="utf-8")
        
        from run_iterative_cpp_optimization import IterationResult
        mock_repair_res = IterationResult(
            iteration=1, type="repair_01", success=True, 
            source_file=repaired_source, metadata={"duration_seconds": 1.0}
        )
        mock_repair.return_value = mock_repair_res
        
        # ABI succeeds
        mock_abi.returncode = 0
        mock_abi.return_value = mock_abi
        
        # Run
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False, False
        )
        
        self.assertEqual(res["completed_optimization_passes"], 1)
        self.assertEqual(res["repair_attempts"], 1)
        self.assertTrue(mock_repair.called)

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    def test_no_unseen_remarks(self, mock_compile, mock_parse):
        mock_compile.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        # Mock returns empty list
        mock_parse.return_value = []
        
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False, False
        )
        
        self.assertEqual(res["completed_optimization_passes"], 0)
        self.assertEqual(res["stopped_reason"], "no_unseen_remarks")

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_repair_step")
    def test_repair_exhaustion(self, mock_repair, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.command import CommandResult
        from llmo.remarks import Remark
        from run_iterative_cpp_optimization import IterationResult

        mock_compile.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        iter_dir = self.temp_dir / "output" / "iteration_01" / "attempt_01"
        iter_dir.mkdir(parents=True, exist_ok=True)
        (iter_dir / "optimization_record.yaml").write_text("dummy", encoding="utf-8")
        mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fibonacci.cpp", 10, 1, "msg", "RAW")]
        
        mock_llm.return_value = "```cpp\nuint64_t fibonacci(int n) { syntax error }\n```"
        mock_build.return_value = CommandResult([], "", 1, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        
        # Repair also fails
        mock_repair_res = IterationResult(
            iteration=1, type="repair_01", success=False, 
            source_file=self.temp_dir / "failed.cpp", metadata={"duration_seconds": 1.0}
        )
        mock_repair.return_value = mock_repair_res
        
        # Run
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False, False
        )
        
        self.assertEqual(res["completed_optimization_passes"], 0)
        self.assertIn("repair_failed", res["stopped_reason"])

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_benchmarks_for_lib")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_benchmark_each_iteration_best_selection(self, mock_find_libsut, mock_bench, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.command import CommandResult
        from llmo.remarks import Remark
        
        def mock_compile_side_effect(source_file, output_dir):
            (output_dir / "optimization_record.yaml").write_text("dummy", encoding="utf-8")
            return CommandResult([], "", 0, 0.1, str(output_dir/"stdout.txt"), str(output_dir/"stderr.txt"))
        mock_compile.side_effect = mock_compile_side_effect

        from llmo.remarks import Remark
        mock_parse.side_effect = [
            [Remark("Missed", "p1", "n1", "fibonacci", "fibonacci.cpp", 10, 1, "msg1", "RAW1")],
            [Remark("Missed", "p2", "n2", "fibonacci", "fibonacci.cpp", 11, 1, "msg2", "RAW2")],
            [Remark("Missed", "p3", "n3", "fibonacci", "fibonacci.cpp", 12, 1, "msg3", "RAW3")]
        ]
        
        # Iteration 1: 100 calls/s
        # Iteration 2: 140 calls/s (best)
        # Iteration 3: 120 calls/s (final)
        mock_llm.side_effect = [
            "```cpp\nuint64_t fibonacci(int n) { return n + 1; }\n```",
            "```cpp\nuint64_t fibonacci(int n) { return n + 2; }\n```",
            "```cpp\nuint64_t fibonacci(int n) { return n + 3; }\n```"
        ]
        
        mock_build.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        mock_abi.return_value = CommandResult(["nm"], ".", 0, 0.1, str(self.temp_dir/"abi_stdout.txt"), str(self.temp_dir/"abi_stderr.txt"))
        
        def mock_bench_side_effect(build_dir, libsut, target, run_all):
            # Create a fake results file
            cps = 100.0
            if "iteration_02" in str(build_dir): cps = 140.0
            elif "iteration_03" in str(build_dir): cps = 120.0
            
            res_file = build_dir / f"benchmark_0_fibonacci_results.json"
            res_file.write_text(json.dumps({"calls_per_second": cps}), encoding="utf-8")
            return []
            
        mock_bench.side_effect = mock_bench_side_effect
        mock_find_libsut.side_effect = lambda d: d / "libSUT.so"

        # Mocking find_libsut to return a path and creating that file
        def mock_find_libsut_impl(d):
            p = d / "libSUT.so"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("dummy", encoding="utf-8")
            return p
        mock_find_libsut.side_effect = mock_find_libsut_impl

        # Run
        res = script.optimize_target(
            self.model_config, self.target_source, 3, self.temp_dir / "output", 
            self.headers, False, True # benchmark_each=True
        )
        
        self.assertEqual(res["completed_optimization_passes"], 3)
        self.assertEqual(res["best_iteration"], 2)
        self.assertEqual(res["best_calls_per_second"], 140.0)
        self.assertTrue((self.temp_dir / "output" / "best").exists())
        self.assertTrue((self.temp_dir / "output" / "best" / "libSUT.so").exists())

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_repair_step")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_abi_failure_repair_flow(self, mock_find_libsut, mock_repair, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.command import CommandResult
        from llmo.remarks import Remark
        from run_iterative_cpp_optimization import IterationResult

        def mock_compile_side_effect(source_file, output_dir):
            (output_dir / "optimization_record.yaml").write_text("dummy", encoding="utf-8")
            return CommandResult([], "", 0, 0.1, str(output_dir/"stdout.txt"), str(output_dir/"stderr.txt"))
        mock_compile.side_effect = mock_compile_side_effect
        mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fibonacci.cpp", 10, 1, "msg", "RAW")]
        
        mock_llm.return_value = "```cpp\nuint64_t fibonacci(int n) { return n + 1; }\n```"
        mock_build.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        
        # ABI fails first time
        mock_abi.side_effect = [
            CommandResult(["nm"], ".", 1, 0.1, str(self.temp_dir/"abi_stdout.txt"), str(self.temp_dir/"abi_stderr.txt")),
            CommandResult(["nm"], ".", 0, 0.1, str(self.temp_dir/"abi_stdout.txt"), str(self.temp_dir/"abi_stderr.txt"))
        ]
        
        mock_find_libsut.return_value = self.temp_dir / "libSUT.so"
        (self.temp_dir / "libSUT.so").write_text("dummy", encoding="utf-8")

        # Repair succeeds
        repaired_source = self.temp_dir / "repaired_abi.cpp"
        repaired_source.write_text("uint64_t fibonacci(int n) { return n; }", encoding="utf-8")
        mock_repair.return_value = IterationResult(1, "repair_01", True, repaired_source, metadata={"duration_seconds": 1.0})
        
        # Run
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False, False
        )
        
        self.assertEqual(res["completed_optimization_passes"], 1)
        self.assertTrue(mock_repair.called)

    @patch("llmo.llama.tokenize")
    @patch("llmo.llama.estimate_tokens")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.parse_remarks")
    def test_tokenizer_unavailable_fallback(self, mock_parse, mock_compile, mock_est, mock_tokenize):
        from llmo.remarks import Remark
        from llmo.command import CommandResult
        
        def mock_compile_side_effect(s, d):
            d.mkdir(parents=True, exist_ok=True)
            (d / "optimization_record.yaml").write_text("dummy", encoding="utf-8")
            return CommandResult([], "", 0, 0.1, "", "")
        mock_compile.side_effect = mock_compile_side_effect
        mock_parse.return_value = [Remark("Missed", "p", "n", "fibonacci", "fibonacci.cpp", 10, 1, "msg", "RAW")]
        
        # Tokenizer returns empty
        mock_tokenize.return_value = []
        mock_est.return_value = 100
        
        # We just want to see if count_tokens (via run_optimization_iteration) calls estimate_tokens
        # We'll run run_optimization_iteration directly
        from run_iterative_cpp_optimization import run_optimization_iteration
        
        res = run_optimization_iteration(
            "model", self.target_source, self.target_source, 1, 1, 1, 
            self.temp_dir / "opt_iter", set(), self.headers
        )
        
        self.assertTrue(mock_est.called)

    @patch("run_iterative_cpp_optimization.write_json")
    @patch("run_iterative_cpp_optimization.batch_remarks")
    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.find_libsut")
    def test_no_change_limit(self, mock_find_libsut, mock_abi, mock_build, mock_llm, mock_compile, mock_parse, mock_batch, mock_write_json):
        from llmo.remarks import Remark
        # Setup mocks to simulate no change
        def side_effect_compile(source, output_dir):
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "optimization_record.yaml").write_text("dummy", encoding="utf-8")
            return CommandResult([], "", 0, 0.1, str(output_dir/"stdout.txt"), str(output_dir/"stderr.txt"))
        mock_compile.side_effect = side_effect_compile
        
        remarks = [
            Remark("Missed", "p", f"n{i}", "fibonacci", "fibonacci.cpp", 10+i, 1, "msg", f"RAW{i}")
            for i in range(10)
        ]
        mock_parse.return_value = remarks
        
        def side_effect_batch(unseen, budget, count_fn):
            if not unseen: return [], []
            return [unseen[0]], unseen[1:]
        mock_batch.side_effect = side_effect_batch
        
        mock_llm.return_value = "uint64_t fibonacci(int n) { return n; }\n"
        self.target_source.write_text("uint64_t fibonacci(int n) { return n; }\n", encoding="utf-8")
        
        mock_build.return_value = CommandResult([], "", 0, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        mock_find_libsut.return_value = self.temp_dir / "libSUT.so"
        (self.temp_dir / "libSUT.so").write_text("dummy", encoding="utf-8")

        with patch("run_iterative_cpp_optimization.CPP_MAX_NO_CHANGE_ATTEMPTS", 2):
            res = script.optimize_target(
                self.model_config, self.target_source, 3, self.temp_dir / "output", 
                self.headers, False, False
            )
        
        self.assertEqual(res["stopped_reason"], "repeated_no_change")
        self.assertTrue((self.temp_dir / "output" / "iteration_01" / "attempt_02").exists())
        self.assertFalse((self.temp_dir / "output" / "iteration_01" / "attempt_03").exists())

    @patch("run_iterative_cpp_optimization.parse_remarks")
    @patch("run_iterative_cpp_optimization.compile_for_remarks")
    @patch("run_iterative_cpp_optimization.call_llm")
    @patch("run_iterative_cpp_optimization.build_full_library")
    @patch("run_iterative_cpp_optimization.run_abi_symbol_check")
    @patch("run_iterative_cpp_optimization.run_repair_step")
    def test_too_many_attempts_safety_cap(self, mock_repair, mock_abi, mock_build, mock_llm, mock_compile, mock_parse):
        from llmo.remarks import Remark
        from run_iterative_cpp_optimization import IterationResult
        mock_compile.return_value = CommandResult([], "", 1, 0.1, str(self.temp_dir/"stdout.txt"), str(self.temp_dir/"stderr.txt"))
        
        repaired_source = self.temp_dir / "repaired.cpp"
        repaired_source.write_text("uint64_t fibonacci(int n) { return n; }", encoding="utf-8")
        
        mock_repair.return_value = IterationResult(
            iteration=1, type="repair_01", success=True, 
            source_file=repaired_source, metadata={"duration_seconds": 0.1}
        )
        
        res = script.optimize_target(
            self.model_config, self.target_source, 1, self.temp_dir / "output", 
            self.headers, False, False
        )
        
        self.assertEqual(res["stopped_reason"], "too_many_attempts")
        self.assertTrue((self.temp_dir / "output" / "iteration_01" / "attempt_10").exists())

if __name__ == '__main__':
    unittest.main()
