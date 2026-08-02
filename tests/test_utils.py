from pathlib import Path
from typing import Any, Optional
from llmo.benchmark import BenchmarkRunResult
from llmo.command import CommandResult

def make_benchmark_result(
    tmp_path: Path,
    *,
    function_name: str = "fibonacci",
    function_id: int = 0,
    returncode: int = 0,
    calls_per_second: float | None = 100.0,
    iteration: int = 0,
) -> BenchmarkRunResult:
    stdout_file = tmp_path / f"benchmark_{function_id}_{function_name}_iter{iteration}_stdout.txt"
    stderr_file = tmp_path / f"benchmark_{function_id}_{function_name}_iter{iteration}_stderr.txt"
    
    parsed_result = None
    if returncode == 0 and calls_per_second is not None:
        parsed_result = {
            "function": function_name,
            "wall_us": 1000000,
            "cpu_us": 990000,
            "calls_per_second": calls_per_second,
            "checksum": 42
        }
        stdout_file.write_text(
            f"function={function_name}\nwall_us=1000000\ncpu_us=990000\ncalls_per_second={calls_per_second}\nchecksum=42\n",
            encoding="utf-8"
        )
    else:
        stdout_file.write_text("failure", encoding="utf-8")
        
    stderr_file.write_text("", encoding="utf-8")
    
    cmd_res = CommandResult(
        command=["runner", "dummy.so", str(function_id)],
        cwd=str(tmp_path),
        returncode=returncode,
        duration_seconds=0.1,
        stdout_file=str(stdout_file),
        stderr_file=str(stderr_file)
    )
    
    return BenchmarkRunResult(
        command_result=cmd_res,
        function_id=function_id,
        function_name=function_name,
        iteration=iteration,
        parsed_result=parsed_result
    )

def mock_abi_check_success(build_dir: Path) -> CommandResult:
    (build_dir / "abi_symbols.json").write_text('{"success": true}', encoding="utf-8")
    return CommandResult(["nm"], str(build_dir), 0, 0.1, str(build_dir/"abi_stdout.txt"), str(build_dir/"abi_stderr.txt"))
