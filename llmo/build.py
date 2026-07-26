from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from .command import CommandResult, run_command

@dataclass
class BuildVariant:
    name: str
    clang_optimization_flag: str

def find_libsut(build_dir: Path) -> Optional[Path]:
    candidates = list(build_dir.rglob("libSUT.so"))
    return candidates[0] if candidates else None

def compile_replacement_artifact_for_check(
    output_dir: Path,
    target_source_name: str,
    replacement_file: Path,
    source_kind: str,
    cxx_compiler: str,
    opt_level: str,
    sut_dir: Path,
    project_root: Path,
    timeout: int,
    other_sources: list[Path]
) -> CommandResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    libsut_path = output_dir / "libSUT.so"
    include_dirs = [replacement_file.parent, sut_dir, project_root]
    command = [cxx_compiler, "-std=c++23", opt_level, "-DNDEBUG", "-shared", "-fPIC"]
    for include_dir in include_dirs:
        if include_dir.exists():
            command.extend(["-I", str(include_dir)])
    command.append(str(replacement_file))
    for source in other_sources:
        command.append(str(source))
    command.extend(["-o", str(libsut_path)])
    return run_command(command, project_root, output_dir / "compile_stdout.txt", output_dir / "compile_stderr.txt", timeout_seconds=timeout)

@dataclass
class BuildMetadata:
    variant: BuildVariant
    project_root: str
    build_dir: str
    c_compiler: str
    cxx_compiler: str
    cmake_generator: Optional[str]
    configure: CommandResult
    build: CommandResult
    benchmark: list[CommandResult]
    abi_check: Optional[CommandResult]
    libsut_path: Optional[str]
    runner_path: Optional[str]
    total_duration_seconds: float

@dataclass
class DirectBuildMetadata:
    variant_name: str
    source_kind: str
    target_source: str
    source_file: str
    build_dir: str
    compile: CommandResult
    benchmark: list[CommandResult]
    abi_check: Optional[CommandResult]
    libsut_path: Optional[str]
    runner_path: str
    total_duration_seconds: float
    model: Optional[str] = None
    llm_task: Optional[str] = None
    ir_verify: Optional[CommandResult] = None
