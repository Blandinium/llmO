from pathlib import Path
from typing import Optional
from .command import run_command, write_json, CommandResult
from .config import REQUIRED_ABI_SYMBOLS

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
