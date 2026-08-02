import re
from datetime import datetime
from pathlib import Path
from typing import Optional

def sanitize_identifier(value: str) -> str:
    # Use lowercase kebab-case for directory names and identifiers
    # Replace anything not alphanumeric or hyphen/underscore with hyphen
    # Preserve underscores if they are already there
    s = value.lower()
    # Source/IR filenames retain a readable extension separator as an underscore;
    # dots inside model/version identifiers are normalized to hyphens.
    if re.search(r"\.(?:cpp|cc|cxx|c|h|hpp|ll|so|json|txt)$", s):
        head, ext = s.rsplit(".", 1)
        s = f"{head}_{ext}"
    else:
        s = s.replace(".", "-")
    s = re.sub(r'[^a-z0-9_]+', '-', s)
    # Collapse repeated separators while preserving meaningful single underscores.
    s = re.sub(r"-+", "-", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("-_")

def make_run_id(explicit_id: Optional[str] = None) -> str:
    if explicit_id:
        return sanitize_identifier(explicit_id)
    return datetime.now().strftime("%Y%m%dT%H%M%S_%f")

def make_artifact_id(
    experiment_type: str,
    benchmark_name: str,
    model_id: Optional[str] = None,
    pipeline_id: Optional[str] = None,
    suffix: Optional[str] = None
) -> str:
    components = [experiment_type]
    if model_id:
        components.append(model_id)
    components.append(benchmark_name)
    if pipeline_id:
        components.append(pipeline_id)
    if suffix:
        components.append(suffix)
    
    sanitized = [sanitize_identifier(c) for c in components]
    return "__".join(sanitized)

def get_standard_path(
    output_root: Path,
    experiment_type: str,
    run_id: str,
    artifact_id: Optional[str] = None
) -> Path:
    # results/<experiment_type>/<run_id>/artifacts/<artifact_id>/
    path = output_root / sanitize_identifier(experiment_type) / run_id
    if artifact_id:
        path = path / "artifacts" / artifact_id
    return path
