from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from .command import run_command, CommandResult
from .config import CLANG_CXX_COMPILER, LLM_IR_OPTIMIZATION_LEVEL, SUT_DIR, PROJECT_ROOT, LLVM_OPT_TOOL, IR_VERIFY_TIMEOUT_SECONDS, LLM_COMPILE_TIMEOUT_SECONDS
from .command import sanitize_name

@dataclass
class IrOperationResult:
    command_result: CommandResult
    output_path: Optional[Path] = None

def generate_llvm_ir(output_dir: Path, source_file: Path) -> IrOperationResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_ir = output_dir / f"{source_file.stem}_{sanitize_name(LLM_IR_OPTIMIZATION_LEVEL)}.ll"
    command = [
        CLANG_CXX_COMPILER,
        "-std=c++23",
        LLM_IR_OPTIMIZATION_LEVEL,
        "-DNDEBUG",
        "-fPIC",
        "-S",
        "-emit-llvm",
        "-fno-discard-value-names",
        "-I", str(SUT_DIR),
        "-I", str(PROJECT_ROOT),
        str(source_file),
        "-o", str(output_ir),
    ]
    res = run_command(command, PROJECT_ROOT, output_dir / "generate_ir_stdout.txt", output_dir / "generate_ir_stderr.txt")
    return IrOperationResult(res, output_ir if res.returncode == 0 and output_ir.exists() else None)

def verify_llvm_ir(build_dir: Path, llvm_ir_file: Path) -> CommandResult:
    build_dir.mkdir(parents=True, exist_ok=True)
    command = [LLVM_OPT_TOOL, "-passes=verify", "-disable-output", str(llvm_ir_file)]
    return run_command(
        command,
        PROJECT_ROOT,
        build_dir / "verify_ir_stdout.txt",
        build_dir / "verify_ir_stderr.txt",
        timeout_seconds=IR_VERIFY_TIMEOUT_SECONDS,
    )

def compile_llvm_ir_to_lib(
    output_dir: Path,
    llvm_ir_file: Path,
    other_sources: list[Path],
    opt_level: str = "-O3"
) -> IrOperationResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    libsut_path = output_dir / "libSUT.so"
    command = [
        CLANG_CXX_COMPILER,
        "-std=c++23",
        opt_level,
        "-DNDEBUG",
        "-shared",
        "-fPIC",
        "-I", str(SUT_DIR),
        "-I", str(PROJECT_ROOT),
        str(llvm_ir_file)
    ]
    for source in other_sources:
        command.append(str(source))
    command.extend(["-o", str(libsut_path)])
    
    res = run_command(
        command,
        PROJECT_ROOT,
        output_dir / f"compile_ir_{sanitize_name(opt_level)}_stdout.txt",
        output_dir / f"compile_ir_{sanitize_name(opt_level)}_stderr.txt",
        timeout_seconds=LLM_COMPILE_TIMEOUT_SECONDS
    )
    return IrOperationResult(res, libsut_path if res.returncode == 0 and libsut_path.exists() else None)

def cleanup_llvm_ir(output_dir: Path, input_ir: Path) -> IrOperationResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_ir = output_dir / f"{input_ir.stem}_cleaned.ll"
    command = [
        LLVM_OPT_TOOL,
        "-passes=globaldce,strip-dead-prototypes",
        "-S",
        str(input_ir),
        "-o", str(output_ir)
    ]
    res = run_command(
        command,
        PROJECT_ROOT,
        output_dir / "cleanup_ir_stdout.txt",
        output_dir / "cleanup_ir_stderr.txt",
        timeout_seconds=IR_VERIFY_TIMEOUT_SECONDS
    )
    return IrOperationResult(res, output_ir if res.returncode == 0 and output_ir.exists() else None)
