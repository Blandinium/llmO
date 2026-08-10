"""Compact response protocol and structural replacement for extracted LLVM IR."""

from dataclasses import dataclass
import re
from typing import Literal, Optional


BEGIN_MARKER = "BEGIN_REPLACEMENT_FUNCTION"
END_MARKER = "END_REPLACEMENT_FUNCTION"


@dataclass(frozen=True)
class ExtractedIrResponse:
    mode: Literal["no_change", "replacement_function", "invalid_response"]
    replacement: Optional[str] = None
    error: Optional[str] = None


def _strip_single_fence(text: str) -> str:
    value = text.strip()
    match = re.fullmatch(r"```(?:llvm|ll)?[ \t]*\n([\s\S]*?)\n```", value)
    return match.group(1).strip() if match else value


def _symbol_pattern(symbol: str) -> str:
    escaped = re.escape(symbol)
    return rf'@(?:"{escaped}"|{escaped})(?=\s*\()'


def _find_function_spans(text: str) -> list[tuple[int, int, str]]:
    """Find top-level definitions with an LLVM-lexical, string-aware brace scan."""
    spans: list[tuple[int, int, str]] = []
    for match in re.finditer(r"(?m)^define\b", text):
        start = match.start()
        i = match.end()
        quoted = False
        escaped = False
        comment = False
        open_brace = -1
        while i < len(text):
            char = text[i]
            if comment:
                if char == "\n":
                    comment = False
            elif quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == ";":
                comment = True
            elif char == '"':
                quoted = True
            elif char == "{":
                open_brace = i
                break
            i += 1
        if open_brace < 0:
            continue
        depth = 1
        i = open_brace + 1
        quoted = escaped = comment = False
        while i < len(text) and depth:
            char = text[i]
            if comment:
                if char == "\n":
                    comment = False
            elif quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == ";":
                comment = True
            elif char == '"':
                quoted = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            i += 1
        if depth == 0:
            spans.append((start, i, text[start:open_brace].strip()))
    return spans


def parse_extracted_ir_response(raw: str, expected_symbol: str) -> ExtractedIrResponse:
    text = _strip_single_fence(raw)
    if text == "NO_CHANGE":
        return ExtractedIrResponse("no_change")
    if text.count(BEGIN_MARKER) != 1 or text.count(END_MARKER) != 1:
        return ExtractedIrResponse("invalid_response", error="expected exactly one replacement marker pair")
    begin = text.find(BEGIN_MARKER)
    end = text.find(END_MARKER)
    if begin != 0 or end < len(BEGIN_MARKER) or text[end + len(END_MARKER):].strip():
        return ExtractedIrResponse("invalid_response", error="prose or content outside replacement markers")
    replacement = text[len(BEGIN_MARKER):end].strip()
    spans = _find_function_spans(replacement)
    if len(spans) != 1:
        return ExtractedIrResponse("invalid_response", error="replacement must contain exactly one function definition")
    start, stop, _ = spans[0]
    if replacement[:start].strip() or replacement[stop:].strip():
        return ExtractedIrResponse("invalid_response", error="unrelated module content outside function definition")
    if not re.search(_symbol_pattern(expected_symbol), spans[0][2]):
        return ExtractedIrResponse("invalid_response", error="replacement defines the wrong target symbol")
    return ExtractedIrResponse("replacement_function", replacement=replacement + "\n")


def reconstruct_extracted_module(original_module: str, replacement: str, expected_symbol: str) -> str:
    """Replace one definition using lexical structure, never line offsets or a brace regex."""
    matches = [span for span in _find_function_spans(original_module)
               if re.search(_symbol_pattern(expected_symbol), span[2])]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one definition of {expected_symbol!r} in extracted module")
    replacement_spans = _find_function_spans(replacement)
    if len(replacement_spans) != 1:
        raise ValueError("replacement is not exactly one complete function definition")
    start, stop, _ = matches[0]
    return original_module[:start] + replacement.rstrip() + original_module[stop:]


def extract_target_function(module: str, symbol: str) -> str:
    matches = [span for span in _find_function_spans(module)
               if re.search(_symbol_pattern(symbol), span[2])]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one definition of {symbol!r}")
    return module[matches[0][0]:matches[0][1]]


def function_abi_header(module: str, symbol: str) -> str:
    """Return a comparison key preserving ABI-bearing header syntax, ignoring SSA names."""
    matches = [span for span in _find_function_spans(module)
               if re.search(_symbol_pattern(symbol), span[2])]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one definition of {symbol!r}")
    header = matches[0][2]
    name = re.search(_symbol_pattern(symbol), header)
    assert name is not None
    open_paren = header.find("(", name.start())
    depth = 1
    i = open_paren + 1
    quoted = escaped = False
    while i < len(header) and depth:
        char = header[i]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        i += 1
    params = header[open_paren + 1:i - 1]
    # Parameter value names occur at the end of a parameter entry; named types
    # (also prefixed with '%') must remain part of the ABI key.
    params = re.sub(
        r'%(?:"(?:\\.|[^"])*"|[-a-zA-Z$._0-9]+)(?=\s*(?:,|$))',
        "%arg", params,
    )
    key = header[:open_paren + 1] + params + header[i - 1:]
    return re.sub(r"\s+", " ", key).strip()
