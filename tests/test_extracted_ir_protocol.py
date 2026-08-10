import shutil
from pathlib import Path

import pytest

from llmo.extracted_ir import (
    BEGIN_MARKER, END_MARKER, function_abi_header,
    parse_extracted_ir_response, reconstruct_extracted_module,
)
from llmo.llvm import validate_llvm_ir_with_assembler


FUNCTION = "define i32 @target(i32 %x) {\n  %v = add i32 %x, 1\n  ret i32 %v\n}"
MODULE = ('target datalayout = "e"\ntarget triple = "x86_64-unknown-linux-gnu"\n'
          'declare i32 @helper(i32)\n\n' + FUNCTION + "\n")


def wrapped(function=FUNCTION):
    return f"{BEGIN_MARKER}\n{function}\n{END_MARKER}"


@pytest.mark.parametrize("raw", ["NO_CHANGE", " \nNO_CHANGE\n", "```\nNO_CHANGE\n```"])
def test_no_change_parses(raw):
    assert parse_extracted_ir_response(raw, "target").mode == "no_change"


def test_no_change_with_prose_is_rejected():
    assert parse_extracted_ir_response("NO_CHANGE because it is optimal", "target").mode == "invalid_response"


def test_valid_replacement_parses():
    parsed = parse_extracted_ir_response(wrapped(), "target")
    assert parsed.mode == "replacement_function"
    assert parsed.replacement.strip() == FUNCTION


@pytest.mark.parametrize("raw", [
    FUNCTION,
    wrapped() + "\n" + wrapped(),
    wrapped(FUNCTION.replace("@target", "@wrong")),
    wrapped(FUNCTION + "\n" + FUNCTION.replace("@target", "@other")),
    wrapped('target triple = "x86_64"\n' + FUNCTION),
])
def test_invalid_replacement_forms_are_rejected(raw):
    assert parse_extracted_ir_response(raw, "target").mode == "invalid_response"


def test_reconstruction_replaces_only_target_definition():
    replacement = FUNCTION.replace("add i32 %x, 1", "add i32 %x, 2")
    result = reconstruct_extracted_module(MODULE, replacement, "target")
    assert "declare i32 @helper(i32)" in result
    assert "add i32 %x, 2" in result
    assert result.count("define ") == 1


def test_abi_signature_mismatch_is_detectable():
    changed = reconstruct_extracted_module(MODULE, FUNCTION.replace("i32 @target(i32", "i64 @target(i64"), "target")
    assert function_abi_header(MODULE, "target") != function_abi_header(changed, "target")


@pytest.mark.skipif(not all(shutil.which(tool) for tool in ("llvm-as", "opt")), reason="LLVM tools unavailable")
def test_reconstructed_module_passes_llvm_verification(tmp_path: Path):
    candidate = tmp_path / "optimized_extracted.ll"
    candidate.write_text(reconstruct_extracted_module(MODULE, FUNCTION.replace("add i32 %x, 1", "add i32 %x, 2"), "target"))
    assert validate_llvm_ir_with_assembler(tmp_path / "verify", candidate).output_path is not None
