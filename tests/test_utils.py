from pathlib import Path
from typing import Any, Optional
from llmo.benchmark_protocol import BenchmarkMeasurement
from llmo.command import CommandResult

def make_benchmark_result(
    tmp_path: Path,
    *,
    function_name: str = "fibonacci",
    function_id: int = 0,
    returncode: int = 0,
    calls_per_second: float | None = 100.0,
    iteration: int = 0,
    artifact_id: str = "unknown",
    sequence_index: int = 0
) -> BenchmarkMeasurement:
    stdout_file = tmp_path / f"benchmark_{function_name}_seq{sequence_index:03d}_stdout.txt"
    stderr_file = tmp_path / f"benchmark_{function_name}_seq{sequence_index:03d}_stderr.txt"
    
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
        stdout_file.parent.mkdir(parents=True, exist_ok=True)
        stdout_file.write_text("failure", encoding="utf-8")
        
    stderr_file.parent.mkdir(parents=True, exist_ok=True)
    stderr_file.write_text("", encoding="utf-8")
    
    return BenchmarkMeasurement(
        artifact_id=artifact_id,
        benchmark_id=function_id,
        benchmark_name=function_name,
        repetition=iteration,
        sequence_index=sequence_index,
        calls_per_second=calls_per_second,
        wall_us=1000000 if returncode == 0 else None,
        cpu_us=990000 if returncode == 0 else None,
        checksum=42 if returncode == 0 else None,
        returncode=returncode,
        parsed_result=parsed_result,
        stdout_path=str(stdout_file),
        stderr_path=str(stderr_file)
    )

def mock_abi_check_success(build_dir: Path) -> CommandResult:
    (build_dir / "abi_symbols.json").write_text('{"success": true}', encoding="utf-8")
    return CommandResult(["nm"], str(build_dir), 0, 0.1, str(build_dir/"abi_stdout.txt"), str(build_dir/"abi_stderr.txt"))
