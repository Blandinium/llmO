from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import re
from .command import run_command, CommandResult
from .config import (
    CLANG_CXX_COMPILER, LLM_IR_OPTIMIZATION_LEVEL, SUT_DIR, PROJECT_ROOT,
    LLVM_OPT_TOOL, LLVM_AS_TOOL, LLVM_EXTRACT_TOOL, LLVM_LINK_TOOL,
    IR_VERIFY_TIMEOUT_SECONDS, LLM_COMPILE_TIMEOUT_SECONDS,
)
from .command import sanitize_name

@dataclass
class IrOperationResult:
    command_result: CommandResult
    output_path: Optional[Path] = None

def llvm_ir_defines_symbol(ir_file: Path, symbol: str) -> bool:
    """Test a generated textual module for an exact function definition."""
    content = ir_file.read_text(encoding="utf-8", errors="replace")
    quoted = re.escape(symbol)
    return re.search(rf'^define\s+[^@\n]*@(?:"{quoted}"|{quoted})\s*\(', content, re.MULTILINE) is not None

def assemble_llvm_ir(output_dir: Path, llvm_ir_file: Path, name: str = "module.bc") -> IrOperationResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_bc = output_dir / name
    res = run_command(
        [LLVM_AS_TOOL, str(llvm_ir_file), "-o", str(output_bc)], PROJECT_ROOT,
        output_dir / "assemble_stdout.txt", output_dir / "assemble_stderr.txt",
        timeout_seconds=IR_VERIFY_TIMEOUT_SECONDS,
    )
    return IrOperationResult(res, output_bc if res.returncode == 0 and output_bc.exists() else None)

def extract_llvm_function(
    output_dir: Path, input_ir: Path, symbol: str, recursive: bool = False
) -> IrOperationResult:
    """Produce a valid reduced module with one definition using llvm-extract."""
    assembled = assemble_llvm_ir(output_dir / "assemble", input_ir, "input.bc")
    if not assembled.output_path:
        return assembled
    output_dir.mkdir(parents=True, exist_ok=True)
    output_ir = output_dir / "extracted_input.ll"
    command = [LLVM_EXTRACT_TOOL, f"--func={symbol}"]
    if recursive:
        command.append("--recursive")
    command.extend(["-S", str(assembled.output_path), "-o", str(output_ir)])
    res = run_command(
        command, PROJECT_ROOT, output_dir / "extract_stdout.txt", output_dir / "extract_stderr.txt",
        timeout_seconds=IR_VERIFY_TIMEOUT_SECONDS,
    )
    return IrOperationResult(res, output_ir if res.returncode == 0 and output_ir.exists() else None)

def validate_llvm_ir_with_assembler(output_dir: Path, llvm_ir_file: Path) -> IrOperationResult:
    """Parse with llvm-as and run the LLVM verifier on the resulting bitcode."""
    assembled = assemble_llvm_ir(output_dir, llvm_ir_file, "validated.bc")
    if not assembled.output_path:
        return assembled
    verified = verify_llvm_ir(output_dir / "verify", assembled.output_path)
    return IrOperationResult(verified, assembled.output_path if verified.returncode == 0 else None)

def reintegrate_llvm_function(
    output_dir: Path, original_ir: Path, optimized_extracted_ir: Path, symbol: str
) -> IrOperationResult:
    """Replace a definition through llvm-extract --delete plus llvm-link."""
    output_dir.mkdir(parents=True, exist_ok=True)
    original = assemble_llvm_ir(output_dir / "assemble_original", original_ir, "original.bc")
    if not original.output_path:
        return original
    optimized = assemble_llvm_ir(output_dir / "assemble_optimized", optimized_extracted_ir, "optimized.bc")
    if not optimized.output_path:
        return optimized
    remainder = output_dir / "original_without_target.bc"
    delete_res = run_command(
        [LLVM_EXTRACT_TOOL, "--delete", f"--func={symbol}", str(original.output_path), "-o", str(remainder)],
        PROJECT_ROOT, output_dir / "delete_stdout.txt", output_dir / "delete_stderr.txt",
        timeout_seconds=IR_VERIFY_TIMEOUT_SECONDS,
    )
    if delete_res.returncode != 0 or not remainder.exists():
        return IrOperationResult(delete_res)
    reconstructed = output_dir / "reconstructed_optimized.ll"
    link_res = run_command(
        [LLVM_LINK_TOOL, str(remainder), str(optimized.output_path), "-S", "-o", str(reconstructed)],
        PROJECT_ROOT, output_dir / "link_stdout.txt", output_dir / "link_stderr.txt",
        timeout_seconds=IR_VERIFY_TIMEOUT_SECONDS,
    )
    if link_res.returncode != 0 or not reconstructed.exists():
        return IrOperationResult(link_res)
    validation = validate_llvm_ir_with_assembler(output_dir / "validate", reconstructed)
    return IrOperationResult(validation.command_result, reconstructed if validation.output_path else None)

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
