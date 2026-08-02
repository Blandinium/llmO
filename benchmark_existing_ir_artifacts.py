#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from llmo.config import *
from llmo.command import CommandResult, run_command, write_json, sanitize_name
from llmo.abi import run_abi_symbol_check, load_abi_check_outcome
from llmo.benchmark import run_benchmarks_for_lib
from llmo.benchmark_protocol import BenchmarkMeasurement, calculate_benchmark_statistics
from llmo.project import all_sut_cpp_files, other_sources_for_replacement
from llmo.llvm import verify_llvm_ir
from llmo.build import compile_replacement_artifact_for_check

# =============================================================================
# Configuration
# =============================================================================

MANUAL_ROOT = PROJECT_ROOT / "manual"
OUTPUT_ROOT = BUILD_ROOT / "ir-artifact-benchmarks"

COMPILE_OPTIMIZATION_LEVEL = os.environ.get("IR_COMPILE_OPT_LEVEL", "-O3")
RUNNER_EXECUTABLE = RUNNER_EXECUTABLE_NAME

CLEAN_BEFORE_BUILD = os.environ.get("CLEAN_BEFORE_BUILD", "1") != "0"
RUN_ALL_BENCHMARKS = os.environ.get("RUN_ALL_BENCHMARKS", "0") != "0"


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
    benchmarks: list[BenchmarkRunResult]
    libsut_path: Optional[str]
    runner_path: str
    total_duration_seconds: float


# =============================================================================
# Artifact discovery
# =============================================================================


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



def variant_name_for_artifact(artifact: IrArtifact) -> str:
    return "ir_{}_{}_{}".format(
        sanitize_name(artifact.source_group),
        sanitize_name(artifact.producer),
        sanitize_name(artifact.function_name),
    )


def benchmark_artifact(artifact: IrArtifact, output_root: Path, repetitions: int = 1) -> ArtifactBenchmarkMetadata:
    variant_name = variant_name_for_artifact(artifact)
    build_dir = output_root / variant_name
    if CLEAN_BEFORE_BUILD and build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    total_start = time.perf_counter()
    libsut_path = build_dir / "libSUT.so"
    verify_result = verify_llvm_ir(build_dir, artifact.ir_file)
    abi_result: Optional[CommandResult] = None
    all_measurements: list[BenchmarkMeasurement] = []

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
        compile_result = compile_replacement_artifact_for_check(
            build_dir, artifact.function_name, artifact.ir_file, "ir",
            CLANG_CXX_COMPILER, COMPILE_OPTIMIZATION_LEVEL,
            SUT_DIR, PROJECT_ROOT, LLM_COMPILE_TIMEOUT_SECONDS,
            other_sources_for_replacement(artifact.function_name)
        )
        if compile_result.returncode == 0 and libsut_path.exists():
            abi_cmd = run_abi_symbol_check(build_dir, libsut_path)
            abi_outcome = load_abi_check_outcome(build_dir, abi_cmd)
            abi_result = abi_cmd
            if abi_outcome.success:
                for rep in range(repetitions):
                    measurements = run_benchmarks_for_lib(
                        build_dir,
                        libsut_path,
                        target_function_name=artifact.function_name,
                        run_all=RUN_ALL_BENCHMARKS,
                        iteration=rep,
                        artifact_id=variant_name,
                        sequence_index=rep
                    )
                    all_measurements.extend(measurements)

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
        benchmarks=all_measurements,
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
    parser.add_argument("--benchmark-repetitions", type=int, default=1)
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
            metadata = benchmark_artifact(artifact, output_root, repetitions=args.benchmark_repetitions)
            verify_ok = metadata.verify.returncode == 0
            compile_ok = metadata.compile.returncode == 0
            abi_ok = metadata.abi_check is not None and metadata.abi_check.returncode == 0
            benchmark_ok = bool(metadata.benchmarks) and all(
                m.returncode == 0 for m in metadata.benchmarks
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
                        m.returncode for m in metadata.benchmarks
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

