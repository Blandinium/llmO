import json
import subprocess
import time
from dataclasses import dataclass, is_dataclass, asdict
from pathlib import Path
from typing import Any, Optional

class LLMoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, set):
            return sorted(list(obj))
        return super().default(obj)

@dataclass
class CommandResult:
    command: list[str]
    cwd: str
    returncode: int
    duration_seconds: float
    stdout_file: str
    stderr_file: str

def run_command(
    command: list[str],
    cwd: Path,
    stdout_file: Path,
    stderr_file: Path,
    env: Optional[dict[str, str]] = None,
    timeout_seconds: Optional[int] = None,
) -> CommandResult:
    start = time.perf_counter()
    stdout_file.parent.mkdir(parents=True, exist_ok=True)
    stderr_file.parent.mkdir(parents=True, exist_ok=True)
    with stdout_file.open("w", encoding="utf-8") as out, stderr_file.open("w", encoding="utf-8") as err:
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd),
                stdout=out,
                stderr=err,
                text=True,
                env=env,
                timeout=timeout_seconds,
            )
            returncode = completed.returncode
        except subprocess.TimeoutExpired:
            returncode = 124
            err.write(f"\nCommand timed out after {timeout_seconds} seconds.\n")
        except FileNotFoundError as exc:
            returncode = 127
            err.write(f"\nCommand not found: {exc}\n")
    return CommandResult(command, str(cwd), returncode, time.perf_counter() - start, str(stdout_file), str(stderr_file))

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, cls=LLMoJsonEncoder), encoding="utf-8")

def sanitize_name(value: str) -> str:
    # Combining sanitization logic from both scripts
    result = value.replace("/", "_").replace("\\", "_").replace("-", "_").replace("+", "plus").replace("=", "_").replace(":", "_").replace(".", "_").replace(" ", "_")
    return result.strip("_")
