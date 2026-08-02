import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from llmo.benchmark import run_benchmarks_for_lib, BenchmarkRunResult
from llmo.command import CommandResult

class TestBenchmarkContract(unittest.TestCase):
    @patch("llmo.benchmark.run_command")
    def test_run_benchmarks_contract(self, mock_run):
        tmp_path = Path("./test_bench_contract")
        tmp_path.mkdir(parents=True, exist_ok=True)
        try:
            stdout_file = tmp_path / "benchmark_0_fibonacci_stdout.txt"
            stdout_file.write_text(
                "function=fibonacci\nwall_us=1000000\ncpu_us=990000\ncalls_per_second=1234.5\nchecksum=42\n",
                encoding="utf-8"
            )
            
            mock_run.return_value = CommandResult(
                command=["runner"],
                cwd=str(tmp_path),
                returncode=0,
                duration_seconds=0.1,
                stdout_file=str(stdout_file),
                stderr_file=str(tmp_path / "stderr.txt")
            )
            
            results = run_benchmarks_for_lib(tmp_path, tmp_path / "libSUT.so", target_function_name="fibonacci", run_all=False)
            
            self.assertEqual(len(results), 1)
            result = results[0]
            self.assertIsInstance(result, BenchmarkRunResult)
            self.assertEqual(result.command_result.returncode, 0)
            self.assertEqual(result.function_name, "fibonacci")
            self.assertIsNotNone(result.parsed_result)
            self.assertEqual(result.parsed_result["calls_per_second"], 1234.5)
            self.assertEqual(result.parsed_result["function"], "fibonacci")
        finally:
            import shutil
            if tmp_path.exists():
                shutil.rmtree(tmp_path)

if __name__ == "__main__":
    unittest.main()
