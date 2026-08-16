"""Normalize optimization results for poster-quality reporting.

This module deliberately contains no plotting code so its interpretation of the
experiment artifacts can be tested independently.
"""
from __future__ import annotations

import json
import math
import re
import warnings
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

BENCHMARKS = ["fibonacci", "format_list", "repeated_sort", "count_matches", "top_words_from_file"]
TECHNIQUES = ["naive_cpp", "guided_cpp", "full_ir", "extracted_ir"]
TECHNIQUE_LABELS = {"naive_cpp": "Naive C++", "guided_cpp": "Guided C++", "full_ir": "Full IR", "extracted_ir": "Extracted IR"}
RESULT_DIRS = {"naive_cpp": "naive-cpp", "guided_cpp": "guided-cpp", "full_ir": "llm-ir", "extracted_ir": "extracted-ir"}
EXPERIMENT_TYPES = {"naive_cpp": "naive-cpp", "guided_cpp": "guided-cpp", "full_ir": "llm-ir", "extracted_ir": "extracted-ir"}
OUTCOMES = ["valid", "compile_or_assemble_failure", "correctness_or_benchmark_failure", "response_truncated", "context_insufficient", "other_failure"]
NOISE_THRESHOLD_PERCENT = 2.0
GUIDED_RESPONSE_RE = re.compile(r"^(?:optimization|repair)_\d+_response\.json$")

def speedup_percent(candidate_cps: float, o3_cps: float) -> float:
    return 100.0 * (candidate_cps / o3_cps - 1.0)

def speedup_ratio(candidate_cps: float, o3_cps: float) -> float:
    """Candidate throughput divided by Clang -O3 throughput (1.0 is parity)."""
    return candidate_cps / o3_cps

def is_meaningful_improvement(speedup: float | None, threshold: float = NOISE_THRESHOLD_PERCENT) -> bool:
    return speedup is not None and speedup > threshold and not math.isclose(speedup, threshold, rel_tol=1e-12, abs_tol=1e-12)

def performance_success_flags(valid_candidate: bool, speedup: float | None,
                              threshold: float = NOISE_THRESHOLD_PERCENT) -> tuple[bool, bool]:
    """Return (>noise threshold, >noise threshold), gated on LLM validity.

    Both legacy ``beats_o3`` and the precise new metric intentionally use the
    experiment noise threshold.  Keeping the legacy flag avoids breaking CSV
    consumers while removing its former ambiguous >0% meaning.
    """
    faster = bool(valid_candidate and is_meaningful_improvement(speedup, threshold))
    return faster, faster


def _num(value: Any) -> float | None:
    if value is None or isinstance(value, bool): return None
    try: return float(value)
    except (TypeError, ValueError): return None

def canonical_model(value: Any) -> str:
    return str(value).replace("qwen2.5-", "qwen2-5-")


def classify_status(status: str | None) -> str:
    """Map runner terminal states to exactly one poster reliability outcome."""
    s = (status or "").lower()
    if s in {"completed", "valid", "success", "no_change", "improved", "regressed", "unchanged"}: return "valid"
    if "context" in s and any(x in s for x in ("insufficient", "large", "fit")): return "context_insufficient"
    if "truncat" in s or s in {"length", "repair_response_truncated"}: return "response_truncated"
    if any(x in s for x in ("compile", "assemble", "verifier", "verification", "invalid_after_repair", "invalid_response", "preflight", "repair_unchanged_invalid")):
        return "compile_or_assemble_failure"
    if any(x in s for x in ("benchmark", "correctness", "regression_failed", "validation_failed")):
        return "correctness_or_benchmark_failure"
    return "other_failure"


def classify_guided(summary: dict[str, Any]) -> tuple[str, int, int]:
    # A repaired optimization pass is recorded by older guided runs with a
    # ``repair_XX`` type; it is still one attempted LLM optimization iteration.
    iterations = list(summary.get("iterations", []))
    completed = int(summary.get("completed_optimization_passes") or 0)
    if completed > 0: return "valid", len(iterations), completed
    statuses = [str(summary.get("status") or ""), str(summary.get("stopped_reason") or "")]
    for i in iterations:
        statuses.extend(str(i.get(k, "")) for k in ("status", "failure_reason", "stopped_reason"))
        md = i.get("metadata") or {}
        statuses.extend(str(md.get(k, "")) for k in ("error", "status", "failure_reason"))
        llm = md.get("llm_result") or {}
        if llm.get("finish_reason") == "length": statuses.append("response_truncated")
        cr = i.get("compile_result") or {}
        if cr.get("returncode") not in (None, 0): statuses.append("compile_failed")
        if i.get("benchmark_result") is False: statuses.append("benchmark_failed")
    mapped = [classify_status(s) for s in statuses if s]
    for outcome in ("response_truncated", "context_insufficient", "compile_or_assemble_failure", "correctness_or_benchmark_failure"):
        if outcome in mapped: return outcome, len(iterations), 0
    return "other_failure", len(iterations), 0


def old_guided_validity(summary: dict[str, Any]) -> bool:
    """Former permissive rule, retained only for migration diagnostics."""
    return any(bool(iteration.get("success")) for iteration in summary.get("iterations", []))


def _raw_guided_call(metadata: dict[str, Any], task_dir: Path | None, context: str) -> dict[str, Any] | None:
    name = metadata.get("raw_response_file")
    if not name or task_dir is None:
        return None
    requested = Path(str(name))
    candidates = [task_dir / requested]
    if not requested.is_absolute():
        candidates.extend(sorted(task_dir.rglob(requested.name)))
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        warnings.warn(f"guided token recovery failed ({context}): missing raw response {task_dir / requested}")
        return None
    try:
        raw = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        warnings.warn(f"guided token recovery failed ({context}): malformed raw response {path}: {exc}")
        return None
    usage = raw.get("usage") if isinstance(raw, dict) else None
    if not isinstance(usage, dict):
        warnings.warn(f"guided token recovery failed ({context}): no usage object in {path}")
        return None
    choices = raw.get("choices") or []
    return {"prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "finish_reason": choices[0].get("finish_reason") if choices and isinstance(choices[0], dict) else None,
            "_token_origin": "raw_response", "_raw_response_path": str(path)}


def guided_llm_calls(summary: dict[str, Any], task_dir: Path | None = None,
                     context: str = "guided task") -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Collect each Guided request once; on-disk responses are authoritative."""
    calls, unavailable, finish_reasons = [], 0, []
    structured = recovered = 0
    discovered_files: list[Path] = []
    if task_dir is not None and task_dir.is_dir():
        # Resolve paths before deduplication: the same file may be reachable via
        # multiple summary references, but is still exactly one LLM request.
        discovered_files = sorted({p.resolve() for p in task_dir.rglob("*_response.json")
                                   if GUIDED_RESPONSE_RE.match(p.name)})
    for path in discovered_files:
        try:
            raw = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            warnings.warn(f"guided token recovery failed ({context}): malformed raw response {path}: {exc}")
            unavailable += 1; continue
        usage = raw.get("usage") if isinstance(raw, dict) else None
        if not isinstance(usage, dict):
            warnings.warn(f"guided token recovery failed ({context}): no usage object in {path}")
            unavailable += 1; continue
        choices = raw.get("choices") or []
        call = {"prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "finish_reason": choices[0].get("finish_reason") if choices and isinstance(choices[0], dict) else None,
                "_token_origin": "raw_response", "_raw_response_path": str(path), "_response_id": raw.get("id")}
        calls.append(call); recovered += 1
        if call.get("finish_reason"): finish_reasons.append(str(call["finish_reason"]))
    # Current Guided runs publish every executed request as a raw response.  A
    # structured-only fallback keeps older/minimal fixtures usable, but mixing
    # it into a discovered raw inventory would re-count the same requests.
    if discovered_files:
        return calls, {"structured_calls": 0, "raw_recovered_calls": recovered,
                       "unavailable_calls": unavailable, "finish_reasons": finish_reasons,
                       "discovered_raw_files": len(discovered_files), "unique_raw_files": len(discovered_files),
                       "raw_response_files": [str(p) for p in discovered_files]}
    request_records = []
    for iteration in summary.get("iterations", []):
        request_records.append((iteration.get("metadata") or {}, iteration.get("iteration") or iteration.get("type")))
        for repair in iteration.get("repairs", []):
            request_records.append((repair.get("metadata") or repair, repair.get("iteration") or repair.get("type") or "repair"))
    for metadata, iteration in request_records:
        llm = metadata.get("llm_result")
        if isinstance(llm, dict):
            call = dict(llm); call["_token_origin"] = "structured"; structured += 1
        else:
            call = _raw_guided_call(metadata, task_dir, f"{context}, iteration {iteration}")
            if call is not None: recovered += 1
        if call is None:
            unavailable += 1; continue
        calls.append(call)
        if call.get("finish_reason"): finish_reasons.append(str(call["finish_reason"]))
    return calls, {"structured_calls": structured, "raw_recovered_calls": recovered,
                   "unavailable_calls": unavailable, "finish_reasons": finish_reasons,
                   "discovered_raw_files": 0, "unique_raw_files": 0, "raw_response_files": []}


def aggregate_llm(summary: dict[str, Any], guided: bool = False, task_dir: Path | None = None,
                  context: str = "guided task") -> tuple[float | None, float | None, float | None, float | None]:
    calls: list[dict[str, Any]] = []
    if guided:
        calls, _ = guided_llm_calls(summary, task_dir, context)
    else:
        calls = [x for x in (summary.get("llm_result"), summary.get("repair_result")) if isinstance(x, dict)]
    def total(field: str) -> float | None:
        vals = [_num(x.get(field)) for x in calls]
        vals = [x for x in vals if x is not None]
        return sum(vals) if vals else None
    seconds = _num(summary.get("total_inference_seconds"))
    if seconds is None: seconds = _num((summary.get("timing") or {}).get("total_llm_seconds"))
    if seconds is None and guided: seconds = _num(summary.get("llm_duration_seconds"))
    if seconds is None: seconds = total("duration_seconds")
    return total("prompt_tokens"), total("completion_tokens"), total("total_tokens"), seconds


def prompt_token_cost(summary: dict[str, Any], guided: bool = False, task_dir: Path | None = None) -> tuple[float | None, str]:
    """Total actual prompt tokens, or one preflight estimate if no call ran."""
    actual, _, _, _ = aggregate_llm(summary, guided, task_dir)
    if actual is not None:
        return actual, "actual"
    estimated = _num(summary.get("estimated_prompt_tokens"))
    if estimated is None:
        estimated = _num((summary.get("token_budget") or {}).get("prompt_tokens"))
    return (estimated, "estimated") if estimated is not None else (None, "unavailable")


def discover_run(results: Path, parent: str, explicit: str | None) -> Path:
    base = results / parent
    if explicit:
        path = Path(explicit)
        if not path.is_absolute(): path = base / explicit
        if not path.is_dir(): raise ValueError(f"run does not exist: {path}")
        return path
    runs = sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []
    if not runs: raise ValueError(f"no runs found under {base}")
    if len(runs) > 1:
        newest = max(runs, key=lambda p: (p.stat().st_mtime, p.name))
        warnings.warn(f"multiple runs under {base}; selected latest {newest.name}. Use an explicit run option to override")
        return newest
    return runs[0]


def load_task_summaries(run: Path) -> tuple[list[tuple[Path, dict[str, Any]]], list[tuple[str, str]]]:
    rows, duplicates = [], []
    seen: dict[tuple[str, str], Path] = {}
    for path in sorted(run.glob("*/*_cpp/summary.json")):
        data = json.loads(path.read_text())
        if not isinstance(data, dict): continue
        model = canonical_model(data.get("model_id") or data.get("model") or path.parent.parent.name)
        benchmark = str(data.get("benchmark_name") or data.get("target") or path.parent.name.removesuffix("_cpp")).removesuffix(".cpp")
        key = model, benchmark
        if key in seen: duplicates.append(key)
        seen[key] = path; rows.append((path, data))
    return rows, duplicates


def matrix_performance(matrix_run: Path) -> tuple[dict[tuple[str, str, str], tuple[float, float]], set[tuple[str, str, str]]]:
    perf, artifacts = {}, set()
    for benchmark in BENCHMARKS:
        path = matrix_run / "benchmarks" / benchmark / "summary.json"
        if not path.exists(): continue
        data = json.loads(path.read_text())
        entries = data.get("artifacts", [])
        o3 = next((_num(a.get("median_calls_per_second")) for a in entries if a.get("artifact_id") == "llvm__o3"), None)
        if not o3: continue
        for technique in TECHNIQUES:
            et = EXPERIMENT_TYPES[technique]
            candidates = [a for a in entries if a.get("experiment_type") == et and a.get("model_id")]
            if technique in {"full_ir", "extracted_ir"}:
                candidates = [a for a in candidates if str(a.get("artifact_id", "")).endswith("__candidate") and str(a.get("pipeline_id", "")).lower().endswith("backend-o3")]
            elif technique == "guided_cpp":
                candidates = [a for a in candidates if str(a.get("artifact_id", "")).endswith("__final")]
            else:
                # Successful tasks publish candidate/final; fallback aliases have neither.
                candidates = [a for a in candidates if str(a.get("artifact_id", "")).endswith(("__candidate", "__final"))]
            grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for a in candidates: grouped[str(a["model_id"])].append(a)
            for model, group in grouped.items():
                if len(group) > 1: warnings.warn(f"duplicate final matrix candidates for {technique}/{model}/{benchmark}; using highest median")
                a = max(group, key=lambda x: _num(x.get("median_calls_per_second")) or -math.inf)
                cps = _num(a.get("median_calls_per_second"))
                if cps is not None: perf[(technique, model, benchmark)] = (cps, o3)
                artifacts.add((technique, model, benchmark))
    return perf, artifacts


def normalize(runs: dict[str, Path], matrix_run: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    perf, matrix_artifacts = matrix_performance(matrix_run)
    rows, diag = [], {"duplicates": {}, "missing": {}, "source_without_matrix": [], "matrix_without_source": []}
    source_keys = set()
    for technique in TECHNIQUES:
        tasks, duplicates = load_task_summaries(runs[technique]); diag["duplicates"][technique] = duplicates
        models = sorted({canonical_model(x.get("model_id") or x.get("model") or p.parent.parent.name) for p, x in tasks})
        found = set()
        for path, data in tasks:
            model = canonical_model(data.get("model_id") or data.get("model") or path.parent.parent.name)
            benchmark = str(data.get("benchmark_name") or data.get("target") or path.parent.name.removesuffix("_cpp")).removesuffix(".cpp")
            found.add((model, benchmark)); source_keys.add((technique, model, benchmark))
            if technique == "guided_cpp": outcome, attempted, successful = classify_guided(data)
            else: outcome, attempted, successful = classify_status(data.get("status")), None, None
            context_label = f"{technique}/{model}/{benchmark}"
            prompt, completion, total, seconds = aggregate_llm(data, technique == "guided_cpp", path.parent, context_label)
            if prompt is not None:
                prompt_cost, prompt_cost_source = prompt, "actual"
            else:
                estimated_cost = _num(data.get("estimated_prompt_tokens"))
                if estimated_cost is None: estimated_cost = _num((data.get("token_budget") or {}).get("prompt_tokens"))
                prompt_cost, prompt_cost_source = ((estimated_cost, "estimated") if estimated_cost is not None else (None, "unavailable"))
            recovery = {"structured_calls": 0, "raw_recovered_calls": 0, "unavailable_calls": 0, "finish_reasons": [],
                        "discovered_raw_files": 0, "unique_raw_files": 0, "raw_response_files": []}
            if technique == "guided_cpp":
                guided_calls, recovery = guided_llm_calls(data, path.parent, context_label)
                if recovery["discovered_raw_files"]:
                    for field, normalized_value in (("prompt_tokens", prompt), ("completion_tokens", completion), ("total_tokens", total)):
                        raw_values = [_num(call.get(field)) for call in guided_calls]
                        raw_values = [value for value in raw_values if value is not None]
                        raw_sum = sum(raw_values) if raw_values else None
                        if raw_sum != normalized_value:
                            raise AssertionError(f"Guided raw-response {field} mismatch for {model}/{benchmark}: raw={raw_sum}, normalized={normalized_value}")
            estimated = _num(data.get("estimated_prompt_tokens") or (data.get("token_budget") or {}).get("prompt_tokens"))
            context = _num(data.get("model_context_size") or (data.get("token_budget") or {}).get("effective_context_size"))
            candidate, o3 = perf.get((technique, model, benchmark), (None, None))
            speedup = speedup_percent(candidate, o3) if candidate is not None and o3 else None
            ratio = speedup_ratio(candidate, o3) if candidate is not None and o3 else None
            valid_candidate = outcome == "valid"
            faster_than_o3, legacy_beats = performance_success_flags(valid_candidate, speedup)
            rows.append({"technique": technique, "model": model, "benchmark": benchmark, "status": data.get("status") or data.get("stopped_reason"),
                "valid_candidate": valid_candidate, "failure_type": "" if outcome == "valid" else outcome,
                "prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total,
                "total_prompt_tokens_processed": prompt_cost, "prompt_token_source": prompt_cost_source,
                "structured_token_calls": recovery["structured_calls"], "raw_recovered_token_calls": recovery["raw_recovered_calls"],
                "unavailable_token_calls": recovery["unavailable_calls"], "llm_finish_reasons": ";".join(recovery["finish_reasons"]),
                "guided_actual_call_count": recovery["raw_recovered_calls"] + recovery["structured_calls"],
                "guided_raw_response_file_count": recovery["unique_raw_files"],
                "estimated_prompt_tokens": estimated, "model_context_size": context,
                "context_usage_percent": 100 * estimated / context if estimated is not None and context else None,
                "llm_seconds": seconds, "task_seconds": _num(data.get("total_task_seconds") or data.get("total_duration_seconds")),
                "candidate_cps": candidate, "o3_cps": o3, "speedup_vs_o3_percent": speedup,
                "speedup_vs_o3": ratio,
                "meaningfully_faster_than_o3": faster_than_o3, "beats_o3": legacy_beats,
                "iterations_attempted": attempted, "successful_iterations": successful, "best_iteration": data.get("best_iteration"),
                "completed_optimization_passes": data.get("completed_optimization_passes") if technique == "guided_cpp" else None,
                "old_guided_valid_candidate": old_guided_validity(data) if technique == "guided_cpp" else None,
                "valid_iteration_fraction": successful / attempted if attempted else None, "source_file": str(path)})
        diag["missing"][technique] = sorted(set((m, b) for m in models for b in BENCHMARKS) - found)
    diag["source_without_matrix"] = sorted(k for k in source_keys if k not in matrix_artifacts and next(r for r in rows if (r["technique"],r["model"],r["benchmark"]) == k)["valid_candidate"])
    diag["matrix_without_source"] = sorted(matrix_artifacts - source_keys)
    return rows, diag


def outcome_counts(rows: Iterable[dict[str, Any]]) -> dict[str, Counter]:
    result = {t: Counter() for t in TECHNIQUES}
    for row in rows: result[row["technique"]]["valid" if row["valid_candidate"] else row["failure_type"]] += 1
    return result
