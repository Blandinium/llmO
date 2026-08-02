from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any
import json
from .command import run_command, write_json, CommandResult
from .config import REQUIRED_ABI_SYMBOLS

@dataclass
class AbiCheckOutcome:
    success: bool
    command_result: CommandResult
    report_path: Path
    report: dict[str, Any] | None
    error: str | None

def parse_defined_symbols(nm_stdout: str) -> set[str]:
    symbols: set[str] = set()
    for raw_line in nm_stdout.splitlines():
        parts = raw_line.split()
        if not parts:
            continue
        symbols.add(parts[-1])
    return symbols

def run_abi_symbol_check(build_dir: Path, libsut_path: Path, required_symbols: Optional[list[str]] = None) -> CommandResult:
    required = required_symbols or REQUIRED_ABI_SYMBOLS
    stdout_file = build_dir / "abi_symbols_stdout.txt"
    stderr_file = build_dir / "abi_symbols_stderr.txt"
    result = run_command(["nm", "-D", "--defined-only", str(libsut_path)], build_dir, stdout_file, stderr_file)

    nm_stdout = stdout_file.read_text(encoding="utf-8", errors="replace") if stdout_file.exists() else ""
    present = parse_defined_symbols(nm_stdout)
    missing = [symbol for symbol in required if symbol not in present]
    metadata = {
        "libsut_path": str(libsut_path),
        "required_symbols": required,
        "missing_symbols": missing,
        "present_required_symbols": [symbol for symbol in required if symbol in present],
        "defined_symbols": sorted(present),
        "nm_returncode": result.returncode,
        "success": result.returncode == 0 and not missing,
    }
    write_json(build_dir / "abi_symbols.json", metadata)

    if missing and stderr_file.exists():
        with stderr_file.open("a", encoding="utf-8") as err:
            err.write("\nMissing required ABI symbols: " + ", ".join(missing) + "\n")

    if result.returncode == 0 and missing:
        return CommandResult(result.command, result.cwd, 1, result.duration_seconds, result.stdout_file, result.stderr_file)
    return result

def load_abi_check_outcome(build_dir: Path, result: Optional[CommandResult]) -> AbiCheckOutcome:
    report_path = build_dir / "abi_symbols.json"
    report = None
    error = None
    success = False
    
    if result is None:
        error = "ABI check not performed (no result provided)"
    elif result.returncode != 0:
        error = f"ABI command failed with returncode {result.returncode}"
    elif not report_path.exists():
        error = "ABI report file missing"
    else:
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if not isinstance(report, dict):
                 error = "ABI report contains invalid JSON (not a dictionary)"
            elif "success" not in report:
                 error = "ABI report missing 'success' field"
            else:
                 success = report.get("success", False)
                 if not success:
                      error = "ABI check failed: missing symbols"
        except json.JSONDecodeError as e:
            error = f"ABI report contains malformed JSON: {e}"
            
    return AbiCheckOutcome(
        success=success,
        command_result=result,
        report_path=report_path,
        report=report,
        error=error
    )
