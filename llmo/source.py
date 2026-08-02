import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional
from .config import SUT_DIR, PROJECT_ROOT, REQUIRED_ABI_SYMBOLS

def extract_code_block(text: str) -> str:
    marker = "```"
    first = text.find(marker)
    if first == -1:
        return text.strip() + "\n"

    block_start = first + len(marker)
    second = text.find(marker, block_start)

    block = text[block_start:] if second == -1 else text[block_start:second]
    lines = block.splitlines()
    if lines:
        language = lines[0].strip().lower()
        if language in {"cpp", "c++", "cc", "cxx", "llvm", "llvm-ir", "ir", "ll"}:
            lines = lines[1:]
    return "\n".join(lines).strip() + "\n"

@dataclass
class ValidationResult:
    response_received: bool = False
    response_complete: bool = False
    module_extracted: bool = False
    preflight_passed: bool = False
    errors: List[str] = field(default_factory=list)

def validate_llvm_ir_module(ir_content: str, target_function: Optional[str] = None, raw_response: Optional[str] = None) -> ValidationResult:
    result = ValidationResult()
    
    if not ir_content.strip():
        result.errors.append("Empty response")
        return result
    
    result.response_received = True
    
    if raw_response:
        marker = "```"
        if raw_response.count(marker) > 2:
             result.errors.append("Multiple fenced code blocks detected")
    
    # Check for prose or multiple modules
    if "target triple =" not in ir_content:
        result.errors.append("Missing 'target triple'")
    if "target datalayout =" not in ir_content:
        result.errors.append("Missing 'target datalayout'")
    
    if ir_content.count("target triple =") > 1:
        result.errors.append("Multiple modules detected")
    
    # Check for required ABI symbols if it's a full module
    if target_function:
        # Regex for define ... @function(
        # Handles quoted names: @"func name"
        pattern = rf'define\s+[^@]*@(?:"{re.escape(target_function)}"|{re.escape(target_function)})\s*\('
        if not re.search(pattern, ir_content):
            result.errors.append(f"Missing required function definition: {target_function}")
    
    # Check for obvious truncation (unmatched braces)
    if ir_content.count("{") != ir_content.count("}"):
        result.errors.append("Unmatched braces (possibly truncated)")
    
    if not result.errors:
        result.response_complete = True
        # Note: module_extracted should be set by the caller if they successfully extracted it
        result.preflight_passed = True
    
    return result

def contains_target_function_definition(source: str, target_source_name: str) -> bool:
    # Cheap preflight filter to reject header echoes and empty responses. The real
    # correctness check remains compile + librunner.
    target = target_source_name.removesuffix(".cpp")
    if target == "top_words_from_file":
        needle = "WordCount* top_words_from_file("
    elif target == "count_matches":
        needle = "size_t count_matches("
    elif target == "repeated_sort":
        needle = "int64_t repeated_sort("
    elif target == "format_list":
        needle = "char* format_list("
    elif target == "fibonacci":
        needle = "uint64_t fibonacci("
    else:
        return True
    return needle in source and "{" in source[source.find(needle):source.find(needle) + 500]

def read_support_headers() -> str:
    parts: list[str] = []
    for header in [SUT_DIR / "library.h", SUT_DIR / "sut_common.h"]:
        if header.exists():
            parts.append(f"// {header.name}\n" + header.read_text(encoding="utf-8"))
    return "\n\n".join(parts)
