from pathlib import Path
from .config import SUT_DIR, PROJECT_ROOT

def extract_code_block(text: str) -> str:
    marker = "```"
    first = text.find(marker)
    if first == -1:
        return text.strip() + "\n"

    block_start = first + len(marker)
    second = text.find(marker, block_start)

    # Some models start a fenced block but never close it. In that case, strip
    # the opening fence/language tag and keep the remainder instead of leaving
    # ```llvm or ```cpp at the top of the generated source.
    block = text[block_start:] if second == -1 else text[block_start:second]
    lines = block.splitlines()
    if lines:
        language = lines[0].strip().lower()
        if language in {"cpp", "c++", "cc", "cxx", "llvm", "llvm-ir", "ir", "ll"}:
            lines = lines[1:]
    return "\n".join(lines).strip() + "\n"

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
