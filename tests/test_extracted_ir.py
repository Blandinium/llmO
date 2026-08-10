import shutil
from pathlib import Path

import pytest

from llmo.llvm import (
    extract_llvm_function,
    llvm_ir_defines_symbol,
    reintegrate_llvm_function,
    validate_llvm_ir_with_assembler,
)


LLVM_TOOLS = ("clang", "llvm-as", "llvm-extract", "llvm-link", "opt")
pytestmark = pytest.mark.skipif(
    any(shutil.which(tool) is None for tool in LLVM_TOOLS),
    reason="LLVM extraction toolchain is unavailable",
)


@pytest.fixture
def sample_module(tmp_path: Path) -> Path:
    source = tmp_path / "sample.c"
    source.write_text(
        "int unrelated(int x) { return x + 1; }\n"
        "__attribute__((noinline)) int dependency(int x) { return x * 2; }\n"
        "int target(int x) { return dependency(x); }\n",
        encoding="utf-8",
    )
    module = tmp_path / "sample.ll"
    import subprocess
    subprocess.run(
        ["clang", "-O1", "-S", "-emit-llvm", "-fno-discard-value-names", str(source), "-o", str(module)],
        check=True,
    )
    return module


def test_extracts_target_as_valid_module_with_declarations(sample_module: Path, tmp_path: Path):
    result = extract_llvm_function(tmp_path / "extract", sample_module, "target")
    assert result.output_path is not None
    text = result.output_path.read_text(encoding="utf-8")
    assert llvm_ir_defines_symbol(result.output_path, "target")
    assert not llvm_ir_defines_symbol(result.output_path, "unrelated")
    assert not llvm_ir_defines_symbol(result.output_path, "dependency")
    assert "declare" in text and "@dependency(" in text
    assert validate_llvm_ir_with_assembler(tmp_path / "validate", result.output_path).output_path


def test_missing_and_invalid_extraction_fail_cleanly(sample_module: Path, tmp_path: Path):
    assert not llvm_ir_defines_symbol(sample_module, "missing")
    missing = extract_llvm_function(tmp_path / "missing", sample_module, "missing")
    assert missing.output_path is None
    assert missing.command_result.returncode != 0

    invalid = tmp_path / "invalid.ll"
    invalid.write_text("this is not llvm ir", encoding="utf-8")
    failed = extract_llvm_function(tmp_path / "invalid", invalid, "target")
    assert failed.output_path is None
    assert failed.command_result.returncode != 0


def test_reintegrates_definition_and_verifies(sample_module: Path, tmp_path: Path):
    extracted = extract_llvm_function(tmp_path / "extract", sample_module, "target")
    assert extracted.output_path
    optimized = tmp_path / "optimized.ll"
    text = extracted.output_path.read_text(encoding="utf-8")
    # A visible, valid change to the target body for identity testing.
    text = text.replace("tail call i32 @dependency", "call i32 @dependency")
    optimized.write_text(text, encoding="utf-8")
    assert validate_llvm_ir_with_assembler(tmp_path / "optimized_validate", optimized).output_path

    result = reintegrate_llvm_function(tmp_path / "reintegrate", sample_module, optimized, "target")
    assert result.output_path is not None
    assert validate_llvm_ir_with_assembler(tmp_path / "reconstructed_validate", result.output_path).output_path
    assert llvm_ir_defines_symbol(result.output_path, "target")
    assert llvm_ir_defines_symbol(result.output_path, "unrelated")
    reconstructed = result.output_path.read_text(encoding="utf-8")
    assert "call i32 @dependency" in reconstructed
    assert "tail call i32 @dependency" not in reconstructed
