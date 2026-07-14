#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent
SUT_DIR = PROJECT_ROOT / "SUT"
MANUAL_ROOT = PROJECT_ROOT / "manual"
BUILD_ROOT = PROJECT_ROOT / "benchmark-builds"
OUTPUT_ROOT = BUILD_ROOT / "ir-artifact-benchmarks"

CLANG_CXX_COMPILER = os.environ.get("CLANG_CXX_COMPILER", "clang++")
LLVM_OPT_TOOL = os.environ.get("LLVM_OPT_TOOL", "opt")
COMPILE_OPTIMIZATION_LEVEL = os.environ.get("IR_COMPILE_OPT_LEVEL", "-O3")
RUNNER_EXECUTABLE = Path(
    os.environ.get(
        "RUNNER_EXECUTABLE",
        str(PROJECT_ROOT / "cmake-build-release-llvm-20/librunner/librunner"),
    )
)
RUNNER_ARGS: list[str] = []

CLEAN_BEFORE_BUILD = os.environ.get("CLEAN_BEFORE_BUILD", "1") != "0"
RUN_ALL_BENCHMARKS = os.environ.get("RUN_ALL_BENCHMARKS", "0") != "0"
IR_VERIFY_TIMEOUT_SECONDS = int(os.environ.get("IR_VERIFY_TIMEOUT_SECONDS", "120"))
COMPILE_TIMEOUT_SECONDS = int(os.environ.get("IR_COMPILE_TIMEOUT_SECONDS", "300"))
BENCHMARK_TIMEOUT_SECONDS = int(os.environ.get("BENCHMARK_TIMEOUT_SECONDS", "900"))

BENCHMARK_FUNCTIONS = {
    0: "fibonacci",
    1: "format_list",
    2: "repeated_sort",
    3: "count_matches",
    4: "top_words_from_file",
}
FUNCTION_TO_BENCHMARK_ID = {name: function_id for function_id, name in BENCHMARK_FUNCTIONS.items()}

REQUIRED_ABI_SYMBOLS = [
    "fibonacci",
    "format_list",
    "free_string",
    "repeated_sort",
    "count_matches",
    "top_words_from_file",
    "free_word_counts",
]


# =============================================================================
# Data structures
# =============================================================================

@dataclass(frozen=True)
class IrArtifact:
    source_group: str
    producer: str
    function_name: str
    ir_file: Path


@dataclass
class CommandResult:
    command: list[str]
    cwd: str
    returncode: int
    duration_seconds: float
    stdout_file: str
    stderr_file: str


@dataclass
class ArtifactBenchmarkMetadata:
    variant_name: str
    source_group: str
    producer: str
    function_name: str
    ir_file: str
    build_dir: str
    compile_optimization_level: str
    verify: CommandResult
    compile: CommandResult
    abi_check: Optional[CommandResult]
    benchmarks: list[CommandResult]
    libsut_path: Optional[str]
    runner_path: str
    total_duration_seconds: float


# =============================================================================
# General helpers
# =============================================================================

def run_command(
    command: list[str],
    cwd: Path,
    stdout_file: Path,
    stderr_file: Path,
    *,
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

    return CommandResult(
        command=command,
        cwd=str(cwd),
        returncode=returncode,
        duration_seconds=time.perf_counter() - start,
        stdout_file=str(stdout_file),
        stderr_file=str(stderr_file),
    )


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def sanitize_name(value: str) -> str:
    result = value
    for old, new in (
        ("/", "_"),
        ("\\", "_"),
        ("-", "_"),
        ("+", "plus"),
        ("=", "_"),
        (":", "_"),
        (".", "_"),
        (" ", "_"),
    ):
        result = result.replace(old, new)
    return result.strip("_")


def parse_scalar_value(value: str) -> Any:
    value = value.strip()
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if lower in {"null", "none"}:
        return None
    if value == "":
        return ""
    try:
        if any(character in value for character in ".eE"):
            return float(value)
        return int(value, 10)
    except ValueError:
        return value


def parse_key_value_lines(text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            parsed[key] = parse_scalar_value(value)
    return parsed


def try_write_benchmark_json(stdout_file: Path, output_json_file: Path) -> None:
    text = stdout_file.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = parse_key_value_lines(text)
    if parsed:
        write_json(output_json_file, parsed)


def all_sut_cpp_files() -> list[Path]:
    return [
        path
        for path in sorted(SUT_DIR.glob("*.cpp"))
        if not path.name.endswith("_original.cpp")
    ]


def other_sources_for_replacement(function_name: str) -> list[Path]:
    target_source_name = f"{function_name}.cpp"
    return [path for path in all_sut_cpp_files() if path.name != target_source_name]


# =============================================================================
# Artifact discovery
# =============================================================================

def function_name_from_ir_file(path: Path) -> Optional[str]:
    prefix = "optimized_"
    if not path.name.startswith(prefix) or path.suffix != ".ll":
        return None
    function_name = path.stem[len(prefix):]
    return function_name if function_name in FUNCTION_TO_BENCHMARK_ID else None


def discover_manual_artifacts(manual_root: Path) -> list[IrArtifact]:
    artifacts: list[IrArtifact] = []
    if not manual_root.exists():
        return artifacts

    for ir_file in sorted(manual_root.glob("*/optimized_*.ll")):
        function_name = function_name_from_ir_file(ir_file)
        if function_name is None:
            continue
        artifacts.append(
            IrArtifact(
                source_group="manual",
                producer=ir_file.parent.name,
                function_name=function_name,
                ir_file=ir_file.resolve(),
            )
        )
    return artifacts


def discover_previous_run_artifacts(build_root: Path, output_root: Path) -> list[IrArtifact]:
    artifacts: list[IrArtifact] = []
    if not build_root.exists():
        return artifacts

    output_root_resolved = output_root.resolve()
    for ir_file in sorted(build_root.rglob("optimized_*.ll")):
        resolved = ir_file.resolve()
        if output_root_resolved == resolved or output_root_resolved in resolved.parents:
            continue

        function_name = function_name_from_ir_file(ir_file)
        if function_name is None:
            continue

        relative = ir_file.relative_to(build_root)
        parts = relative.parts
        # Typical path:
        # llm-artifacts-split-sources/<model>/<function>_cpp/optimized_<function>.ll
        if len(parts) >= 3 and parts[0] == "llm-artifacts-split-sources":
            producer = parts[1]
        else:
            producer = "__".join(parts[:-1]) or "benchmark_builds"

        artifacts.append(
            IrArtifact(
                source_group="previous",
                producer=producer,
                function_name=function_name,
                ir_file=resolved,
            )
        )
    return artifacts


def discover_artifacts(manual_root: Path, build_root: Path, output_root: Path) -> list[IrArtifact]:
    discovered = discover_manual_artifacts(manual_root)
    discovered.extend(discover_previous_run_artifacts(build_root, output_root))

    # De-duplicate by resolved path while retaining deterministic ordering.
    unique: dict[Path, IrArtifact] = {}
    for artifact in discovered:
        unique[artifact.ir_file] = artifact
    return sorted(
        unique.values(),
        key=lambda item: (item.source_group, item.producer, item.function_name, str(item.ir_file)),
    )


# =============================================================================
# Verification, build, ABI check, and benchmarks
# =============================================================================

def verify_llvm_ir(build_dir: Path, ir_file: Path) -> CommandResult:
    return run_command(
        [LLVM_OPT_TOOL, "-passes=verify", "-disable-output", str(ir_file)],
        PROJECT_ROOT,
        build_dir / "verify_ir_stdout.txt",
        build_dir / "verify_ir_stderr.txt",
        timeout_seconds=IR_VERIFY_TIMEOUT_SECONDS,
    )


def parse_defined_symbols(nm_stdout: str) -> set[str]:
    symbols: set[str] = set()
    for raw_line in nm_stdout.splitlines():
        parts = raw_line.split()
        if parts:
            symbols.add(parts[-1])
    return symbols


def run_abi_symbol_check(build_dir: Path, libsut_path: Path) -> CommandResult:
    stdout_file = build_dir / "abi_symbols_stdout.txt"
    stderr_file = build_dir / "abi_symbols_stderr.txt"
    result = run_command(
        ["nm", "-D", "--defined-only", str(libsut_path)],
        build_dir,
        stdout_file,
        stderr_file,
    )

    nm_stdout = stdout_file.read_text(encoding="utf-8", errors="replace") if stdout_file.exists() else ""
    present = parse_defined_symbols(nm_stdout)
    missing = [symbol for symbol in REQUIRED_ABI_SYMBOLS if symbol not in present]
    write_json(
        build_dir / "abi_symbols.json",
        {
            "libsut_path": str(libsut_path),
            "required_symbols": REQUIRED_ABI_SYMBOLS,
            "missing_symbols": missing,
            "present_required_symbols": [
                symbol for symbol in REQUIRED_ABI_SYMBOLS if symbol in present
            ],
            "defined_symbols": sorted(present),
            "nm_returncode": result.returncode,
            "success": result.returncode == 0 and not missing,
        },
    )

    if missing:
        with stderr_file.open("a", encoding="utf-8") as err:
            err.write("\nMissing required ABI symbols: " + ", ".join(missing) + "\n")
        if result.returncode == 0:
            return CommandResult(
                command=result.command,
                cwd=result.cwd,
                returncode=1,
                duration_seconds=result.duration_seconds,
                stdout_file=result.stdout_file,
                stderr_file=result.stderr_file,
            )
    return result


def compile_ir_replacement(build_dir: Path, artifact: IrArtifact, libsut_path: Path) -> CommandResult:
    command = [
        CLANG_CXX_COMPILER,
        "-std=c++23",
        COMPILE_OPTIMIZATION_LEVEL,
        "-DNDEBUG",
        "-shared",
        "-fPIC",
        "-I",
        str(SUT_DIR),
        "-I",
        str(PROJECT_ROOT),
        str(artifact.ir_file),
    ]
    command.extend(str(source) for source in other_sources_for_replacement(artifact.function_name))
    command.extend(["-o", str(libsut_path)])

    return run_command(
        command,
        PROJECT_ROOT,
        build_dir / "compile_stdout.txt",
        build_dir / "compile_stderr.txt",
        timeout_seconds=COMPILE_TIMEOUT_SECONDS,
    )


def run_benchmarks_for_lib(
    build_dir: Path,
    libsut_path: Path,
    target_function_name: str,
) -> list[CommandResult]:
    env = os.environ.copy()
    old_ld_library_path = env.get("LD_LIBRARY_PATH")
    env["LD_LIBRARY_PATH"] = (
        f"{libsut_path.parent}:{old_ld_library_path}"
        if old_ld_library_path
        else str(libsut_path.parent)
    )

    if RUN_ALL_BENCHMARKS:
        selected = list(BENCHMARK_FUNCTIONS.items())
    else:
        function_id = FUNCTION_TO_BENCHMARK_ID[target_function_name]
        selected = [(function_id, target_function_name)]

    results: list[CommandResult] = []
    for function_id, function_name in selected:
        stdout_file = build_dir / f"benchmark_{function_id}_{function_name}_stdout.txt"
        stderr_file = build_dir / f"benchmark_{function_id}_{function_name}_stderr.txt"
        command = [
            str(RUNNER_EXECUTABLE),
            str(libsut_path),
            str(function_id),
            *RUNNER_ARGS,
        ]
        result = run_command(
            command,
            build_dir,
            stdout_file,
            stderr_file,
            env=env,
            timeout_seconds=BENCHMARK_TIMEOUT_SECONDS,
        )
        results.append(result)
        try_write_benchmark_json(
            stdout_file,
            build_dir / f"benchmark_{function_id}_{function_name}_results.json",
        )
    return results


def variant_name_for_artifact(artifact: IrArtifact) -> str:
    return "ir_{}_{}_{}".format(
        sanitize_name(artifact.source_group),
        sanitize_name(artifact.producer),
        sanitize_name(artifact.function_name),
    )


def benchmark_artifact(artifact: IrArtifact, output_root: Path) -> ArtifactBenchmarkMetadata:
    variant_name = variant_name_for_artifact(artifact)
    build_dir = output_root / variant_name
    if CLEAN_BEFORE_BUILD and build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    total_start = time.perf_counter()
    libsut_path = build_dir / "libSUT.so"
    verify_result = verify_llvm_ir(build_dir, artifact.ir_file)

    abi_result: Optional[CommandResult] = None
    benchmark_results: list[CommandResult] = []

    if verify_result.returncode != 0:
        compile_result = CommandResult(
            command=[],
            cwd=str(PROJECT_ROOT),
            returncode=125,
            duration_seconds=0.0,
            stdout_file=str(build_dir / "compile_stdout.txt"),
            stderr_file=str(build_dir / "compile_stderr.txt"),
        )
        Path(compile_result.stdout_file).write_text("", encoding="utf-8")
        Path(compile_result.stderr_file).write_text(
            "Compile skipped because LLVM IR verification failed.\n",
            encoding="utf-8",
        )
    else:
        compile_result = compile_ir_replacement(build_dir, artifact, libsut_path)
        if compile_result.returncode == 0 and libsut_path.exists():
            abi_result = run_abi_symbol_check(build_dir, libsut_path)
            if abi_result.returncode == 0:
                benchmark_results = run_benchmarks_for_lib(
                    build_dir,
                    libsut_path,
                    artifact.function_name,
                )

    metadata = ArtifactBenchmarkMetadata(
        variant_name=variant_name,
        source_group=artifact.source_group,
        producer=artifact.producer,
        function_name=artifact.function_name,
        ir_file=str(artifact.ir_file),
        build_dir=str(build_dir),
        compile_optimization_level=COMPILE_OPTIMIZATION_LEVEL,
        verify=verify_result,
        compile=compile_result,
        abi_check=abi_result,
        benchmarks=benchmark_results,
        libsut_path=str(libsut_path) if libsut_path.exists() else None,
        runner_path=str(RUNNER_EXECUTABLE),
        total_duration_seconds=time.perf_counter() - total_start,
    )
    write_json(build_dir / "build_metadata.json", asdict(metadata))
    return metadata


# =============================================================================
# Main
# =============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify, compile, ABI-check, and benchmark existing optimized LLVM IR "
            "files from manual/ and prior benchmark-builds/ runs."
        )
    )
    parser.add_argument("--manual-root", type=Path, default=MANUAL_ROOT)
    parser.add_argument("--build-root", type=Path, default=BUILD_ROOT)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument(
        "--only",
        action="append",
        choices=sorted(FUNCTION_TO_BENCHMARK_ID),
        help="Benchmark only this function; may be supplied more than once.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List discovered artifacts without compiling or benchmarking them.",
    )
    return parser.parse_args()


def validate_environment() -> list[str]:
    errors: list[str] = []
    if not SUT_DIR.is_dir():
        errors.append(f"Missing SUT directory: {SUT_DIR}")
    if not RUNNER_EXECUTABLE.is_file():
        errors.append(f"Missing librunner executable: {RUNNER_EXECUTABLE}")
    for function_name in FUNCTION_TO_BENCHMARK_ID:
        source = SUT_DIR / f"{function_name}.cpp"
        if not source.is_file():
            errors.append(f"Missing SUT source: {source}")
    return errors


def main() -> int:
    args = parse_args()
    manual_root = args.manual_root.resolve()
    build_root = args.build_root.resolve()
    output_root = args.output_root.resolve()

    artifacts = discover_artifacts(manual_root, build_root, output_root)
    if args.only:
        selected_functions = set(args.only)
        artifacts = [item for item in artifacts if item.function_name in selected_functions]

    print(f"Discovered {len(artifacts)} optimized IR artifact(s).")
    for artifact in artifacts:
        print(
            f"  {artifact.source_group:8} {artifact.producer:30} "
            f"{artifact.function_name:20} {artifact.ir_file}"
        )

    if args.list:
        return 0

    environment_errors = validate_environment()
    if environment_errors:
        for error in environment_errors:
            print(f"Error: {error}", file=sys.stderr)
        return 2
    if not artifacts:
        print("Error: no optimized_*.ll artifacts found.", file=sys.stderr)
        return 2

    output_root.mkdir(parents=True, exist_ok=True)
    summary: list[dict[str, Any]] = []

    for index, artifact in enumerate(artifacts, start=1):
        variant_name = variant_name_for_artifact(artifact)
        print(f"\n[{index}/{len(artifacts)}] === {variant_name} ===")
        try:
            metadata = benchmark_artifact(artifact, output_root)
            verify_ok = metadata.verify.returncode == 0
            compile_ok = metadata.compile.returncode == 0
            abi_ok = metadata.abi_check is not None and metadata.abi_check.returncode == 0
            benchmark_ok = bool(metadata.benchmarks) and all(
                result.returncode == 0 for result in metadata.benchmarks
            )
            print(f"verify:    {'ok' if verify_ok else 'failed'}")
            print(f"compile:   {'ok' if compile_ok else 'failed'}")
            print(f"abi:       {'ok' if abi_ok else 'failed'}")
            print(f"benchmark: {'ok' if benchmark_ok else 'failed'}")
            print(f"folder:    {metadata.build_dir}")

            summary.append(
                {
                    "variant_name": variant_name,
                    "source_group": artifact.source_group,
                    "producer": artifact.producer,
                    "function_name": artifact.function_name,
                    "ir_file": str(artifact.ir_file),
                    "failed": not benchmark_ok,
                    "verify_returncode": metadata.verify.returncode,
                    "compile_returncode": metadata.compile.returncode,
                    "abi_returncode": (
                        metadata.abi_check.returncode if metadata.abi_check else None
                    ),
                    "benchmark_returncodes": [
                        result.returncode for result in metadata.benchmarks
                    ],
                    "total_duration_seconds": metadata.total_duration_seconds,
                    "build_dir": metadata.build_dir,
                    "metadata_file": str(Path(metadata.build_dir) / "build_metadata.json"),
                }
            )
        except Exception as exc:
            print(f"failed: {exc}", file=sys.stderr)
            summary.append(
                {
                    "variant_name": variant_name,
                    "source_group": artifact.source_group,
                    "producer": artifact.producer,
                    "function_name": artifact.function_name,
                    "ir_file": str(artifact.ir_file),
                    "failed": True,
                    "error": str(exc),
                }
            )

        write_json(output_root / "summary.json", summary)

    failed_count = sum(1 for item in summary if item.get("failed"))
    print(f"\nSummary written to: {output_root / 'summary.json'}")
    print(f"Succeeded: {len(summary) - failed_count}; failed: {failed_count}")
    return 1 if failed_count else 0


if __name__ == "__main__":
    raise SystemExit(main())

