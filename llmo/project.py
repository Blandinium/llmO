from pathlib import Path
from .config import SUT_DIR, DEFAULT_LLM_TARGET_FILES

def all_sut_cpp_files() -> list[Path]:
    files = sorted(SUT_DIR.glob("*.cpp"))
    return [path for path in files if not path.name.endswith("_original.cpp")]

def llm_target_source_files(target_files_override: list[str] = None) -> list[Path]:
    names = target_files_override or DEFAULT_LLM_TARGET_FILES
    paths = [SUT_DIR / name for name in names]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing LLM target source files: " + ", ".join(missing))
    return paths

def other_sources_for_replacement(target_source_name: str) -> list[Path]:
    return [path for path in all_sut_cpp_files() if path.name != target_source_name]

def source_function_name(source_file: Path) -> str:
    return source_file.stem
