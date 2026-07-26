from pathlib import Path
from .command import run_command, CommandResult
from .config import CLANG_CXX_COMPILER, LLM_IR_OPTIMIZATION_LEVEL, SUT_DIR, PROJECT_ROOT, LLVM_OPT_TOOL, IR_VERIFY_TIMEOUT_SECONDS
from .command import sanitize_name

def generate_llvm_ir(output_dir: Path, source_file: Path) -> CommandResult:
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
    return run_command(command, PROJECT_ROOT, output_dir / "generate_ir_stdout.txt", output_dir / "generate_ir_stderr.txt")

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
