#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import sys
import time
import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

from llmo.config import *
from llmo.command import run_command, write_json, write_json_atomic, CommandResult, sanitize_name
from llmo.benchmark import run_benchmarks_for_lib, get_randomized_balanced_sequence
from llmo.benchmark_protocol import BenchmarkProtocol, BenchmarkMeasurement, calculate_benchmark_statistics, compare_benchmarks
from llmo.naming import make_run_id, make_artifact_id, get_standard_path, sanitize_identifier
from llmo.metadata import get_run_metadata
from llmo.abi import run_abi_symbol_check, load_abi_check_outcome
from llmo.reporting import calculate_break_even

@dataclass
class ArtifactDefinition:
    artifact_id: str
    experiment_type: str
    benchmark_name: str
    library_path: Path
    model_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    run_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    source_run_path: Optional[Path] = None
    artifact_metadata_path: Optional[Path] = None

    @property
    def matrix_key(self) -> str:
        """Unique scheduling key; artifact IDs are intentionally only labels."""
        identity = str((self.artifact_metadata_path or self.library_path).resolve())
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
        return f"{self.artifact_id}__source-{digest}"

    def report_identity(self) -> Dict[str, Any]:
        return {
            "matrix_key": self.matrix_key,
            "artifact_id": self.artifact_id,
            "experiment_type": self.experiment_type,
            "model_id": self.model_id,
            "pipeline_id": self.pipeline_id,
            "run_id": self.run_id,
            "source_run_path": str(self.source_run_path.resolve()) if self.source_run_path else None,
            "artifact_metadata_path": str(self.artifact_metadata_path.resolve()) if self.artifact_metadata_path else None,
            "library_path": str(self.library_path.resolve()),
        }


def _is_intermediate_artifact(artifact: ArtifactDefinition) -> bool:
    """Return True for optimizer-internal artifacts excluded from final reports."""
    meta = artifact.metadata or {}
    if meta.get("is_final_artifact") is True:
        return False
    if artifact.experiment_type == "guided-cpp":
        suffix = artifact.artifact_id.rsplit("__", 1)[-1]
        return suffix == "baseline" or suffix.startswith("iteration-")
    if artifact.experiment_type == "naive-cpp":
        # A confirmed candidate is also published under its final ID. Keep the
        # candidate metadata on disk for provenance without measuring it twice.
        return meta.get("artifact_role") == "candidate" and meta.get("confirmed_improvement") is True
    return False


def _legacy_ir_artifacts_from_summary(
    summary_path: Path, meta: Dict[str, Any], results_root: Path
) -> List[ArtifactDefinition]:
    """Expand pre-canonical IR summaries into backend baseline/candidate artifacts."""
    try:
        rel = summary_path.relative_to(results_root)
    except ValueError:
        return []
    if not rel.parts or rel.parts[0] != "llm-ir":
        return []
    benchmark_name = meta.get("benchmark_name") or summary_path.parent.name.removesuffix("_cpp")
    model_id = meta.get("model_id") or (rel.parts[-3] if len(rel.parts) >= 3 else "unknown")
    run_id = meta.get("run_id") or (rel.parts[1] if len(rel.parts) > 1 else None)
    results: list[ArtifactDefinition] = []
    for opt_level in ("-O0", "-O3"):
        level_key = opt_level.removeprefix("-")
        pipeline_id = f"ir-o1__backend-{level_key.lower()}"
        backend_dir = summary_path.parent / f"backend_{level_key}"
        for role in ("baseline", "candidate"):
            lib = backend_dir / role / "libSUT.so"
            if not lib.exists():
                continue
            aid = make_artifact_id("llm-ir", benchmark_name, model_id, pipeline_id=pipeline_id, suffix=role)
            results.append(ArtifactDefinition(
                artifact_id=aid,
                experiment_type="llm-ir",
                benchmark_name=benchmark_name,
                library_path=lib,
                model_id=model_id,
                pipeline_id=pipeline_id,
                run_id=run_id,
                metadata={
                    "schema_version": 1,
                    "artifact_id": aid,
                    "experiment_type": "llm-ir",
                    "artifact_role": role,
                    "is_final_artifact": True,
                    "legacy_discovery": True,
                },
            ))
    return results

def _artifact_from_metadata(art_json_path: Path, results_root: Path) -> Optional[ArtifactDefinition]:
    try:
        meta = json.loads(art_json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Warning: failed to load artifact metadata from {art_json_path}: {exc}")
        return None

    if not isinstance(meta, dict):
        print(
            f"Warning: ignoring artifact metadata with unsupported top-level "
            f"type {type(meta).__name__}: {art_json_path}"
        )
        return None

    # Older IR runners wrote the task summary as artifact.json. It represents
    # several backend libraries and must never be inferred as one artifact.
    if meta.get("experiment_type") == "llm-ir" and not meta.get("artifact_id") and meta.get("backend_results"):
        return None

    aid = meta.get("artifact_id", art_json_path.parent.name)
    paths = meta.get("paths") or {}
    candidates: list[Path] = []
    # Older task-level metadata may name the candidate artifact without a
    # paths section. Prefer the role-specific build directory before a broad
    # recursive search, otherwise baseline/libSUT.so may be selected.
    role = meta.get("artifact_role") or str(meta.get("artifact_id", "")).rsplit("__", 1)[-1]
    if role in {"baseline", "candidate", "final"}:
        candidates.append(art_json_path.parent / role / "libSUT.so")
    for key in ("canonical_libsut", "libsut", "library_path"):
        value = paths.get(key) or meta.get(key)
        if value:
            candidate = Path(value)
            if not candidate.is_absolute():
                candidate = (art_json_path.parent / candidate).resolve()
            candidates.append(candidate)
    candidates.extend([
        art_json_path.parent / "libSUT.so",
        *art_json_path.parent.rglob("libSUT.so"),
    ])
    lib_path = next((candidate for candidate in candidates if candidate.exists()), None)
    if lib_path is None:
        return None

    try:
        rel = art_json_path.relative_to(results_root)
        exp_type = meta.get("experiment_type") or rel.parts[0]
        run_id = meta.get("run_id") or (rel.parts[1] if len(rel.parts) > 1 else None)
    except ValueError:
        exp_type = meta.get("experiment_type", "unknown")
        run_id = meta.get("run_id")

    benchmark_name = meta.get("benchmark_name")
    if not benchmark_name or benchmark_name == "all":
        # Whole-library LLVM artifacts participate in every benchmark and are
        # expanded later by the caller.
        benchmark_name = "all"
    return ArtifactDefinition(
        artifact_id=aid,
        experiment_type=exp_type,
        benchmark_name=benchmark_name,
        library_path=lib_path,
        model_id=meta.get("model_id"),
        pipeline_id=meta.get("pipeline_id"),
        run_id=run_id,
        metadata=meta,
        artifact_metadata_path=art_json_path,
    )


def discover_artifacts(results_root: Path, include_intermediate: bool = False) -> List[ArtifactDefinition]:
    if not results_root.exists():
        return []
    artifacts: list[ArtifactDefinition] = []
    seen: set[tuple[str, str]] = set()

    # Search recursively because guided/IR artifacts may be nested below a
    # model and target while pure LLVM artifacts live directly under artifacts/.
    for art_json_path in results_root.rglob("artifact.json"):
        if "final-matrix" in art_json_path.parts:
            continue
        artifact = _artifact_from_metadata(art_json_path, results_root)
        if artifact is None:
            continue
        if not include_intermediate and _is_intermediate_artifact(artifact):
            continue
        key = (artifact.artifact_id, str(artifact.library_path.resolve()))
        if key not in seen:
            seen.add(key)
            artifacts.append(artifact)

    # Compatibility fallback for older runs that only have summary.json.
    for summary_path in results_root.rglob("summary.json"):
        if "final-matrix" in summary_path.parts:
            continue
        adjacent_artifact = summary_path.parent / "artifact.json"
        if adjacent_artifact.exists() and _artifact_from_metadata(adjacent_artifact, results_root) is not None:
            continue
        try:
            meta = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        # Run-level and final-matrix summaries may legitimately be arrays.
        # They do not describe one discoverable artifact, so the legacy
        # summary fallback must ignore them rather than calling dict methods.
        if not isinstance(meta, dict):
            continue
        legacy_ir = _legacy_ir_artifacts_from_summary(summary_path, meta, results_root)
        if legacy_ir:
            for artifact in legacy_ir:
                key = (artifact.artifact_id, str(artifact.library_path.resolve()))
                if key not in seen:
                    seen.add(key)
                    artifacts.append(artifact)
            continue

        libs = list(summary_path.parent.rglob("libSUT.so"))
        if not libs:
            continue
        rel = summary_path.relative_to(results_root)
        exp_type = meta.get("experiment_type") or rel.parts[0]
        # Never infer one vague artifact from an IR task containing multiple
        # backend libraries. Legacy IR is handled explicitly above.
        if exp_type == "llm-ir":
            continue
        model_id = rel.parts[-3] if len(rel.parts) >= 3 else None
        target_name = rel.parts[-2] if len(rel.parts) >= 2 else "unknown"
        benchmark_name = target_name.removesuffix("_cpp").removesuffix(".cpp")
        aid = meta.get("final_confirmation_id") or meta.get("final_artifact_id") or f"{exp_type}__{model_id or 'unknown'}__{benchmark_name}"
        key = (aid, str(libs[0].resolve()))
        if key in seen:
            continue
        seen.add(key)
        artifacts.append(ArtifactDefinition(
            artifact_id=aid,
            experiment_type=exp_type,
            benchmark_name=benchmark_name,
            library_path=libs[0],
            model_id=model_id,
            run_id=meta.get("run_id"),
            metadata=meta,
        ))
    return artifacts


def discover_selected_runs(run_paths: List[Path], include_intermediate: bool = False) -> List[ArtifactDefinition]:
    """Discover only explicitly selected run directories and retain provenance."""
    artifacts: list[ArtifactDefinition] = []
    for run_path in run_paths:
        resolved = run_path.resolve()
        if not resolved.is_dir():
            raise ValueError(f"Selected source run is not a directory: {run_path}")
        selected = discover_artifacts(resolved, include_intermediate=include_intermediate)
        if not selected:
            raise ValueError(f"Selected source run contains no benchmark artifacts: {run_path}")
        for artifact in selected:
            artifact.source_run_path = resolved
        artifacts.extend(selected)
    keys = [artifact.matrix_key for artifact in artifacts]
    if len(keys) != len(set(keys)):
        raise ValueError("The selected runs contain the same artifact path more than once; remove overlapping --source-run entries.")
    return artifacts


def _median(stats: Any) -> Optional[float]:
    return stats.median_calls_per_second if stats else None


def build_benchmark_report(
    benchmark_name: str,
    artifacts: List[ArtifactDefinition],
    stats_map: Dict[str, Any],
    reference_key: str,
) -> Dict[str, Any]:
    """Derive winners, references, percentage changes, and amortization."""
    valid = [a for a in artifacts if _median(stats_map.get(a.matrix_key)) is not None]
    categories = {
        "fastest_llvm": lambda a: a.experiment_type == "llvm",
        "fastest_naive_cpp": lambda a: a.experiment_type == "naive-cpp",
        "fastest_guided_cpp": lambda a: a.experiment_type in {"guided-cpp", "iterative-cpp"},
        "fastest_llm_ir": lambda a: a.experiment_type == "llm-ir",
        "fastest_overall": lambda a: True,
    }

    def winner(predicate):
        candidates = [a for a in valid if predicate(a)]
        if not candidates:
            return None
        art = max(candidates, key=lambda a: _median(stats_map[a.matrix_key]))
        return {**art.report_identity(), "median_calls_per_second": _median(stats_map[art.matrix_key])}

    winners = {name: winner(predicate) for name, predicate in categories.items()}
    llvm = [a for a in valid if a.experiment_type == "llvm"]
    llvm_o1 = next((a for a in llvm if "o1" in (a.pipeline_id or "").lower() or "__o1" in a.artifact_id.lower()), None)
    llvm_o3 = next((a for a in llvm if "o3" in (a.pipeline_id or "").lower() or "__o3" in a.artifact_id.lower()), None)
    fastest_llvm = max(llvm, key=lambda a: _median(stats_map[a.matrix_key])) if llvm else None
    references = {
        "llvm_o1": llvm_o1,
        "fastest_llvm": fastest_llvm,
        "original_cpp_clang_o3": llvm_o3,
    }
    reference_report = {name: (art.report_identity() if art else None) for name, art in references.items()}
    # Compatibility alias for consumers of the original report schema.
    reference_report["original_cpp_o3"] = reference_report["original_cpp_clang_o3"]

    artifact_reports = []
    baseline = next((a for a in artifacts if a.matrix_key == reference_key), None)
    baseline_cps = _median(stats_map.get(reference_key))
    for artifact in artifacts:
        cps = _median(stats_map.get(artifact.matrix_key))
        changes = {}
        for name, ref in references.items():
            ref_cps = _median(stats_map.get(ref.matrix_key)) if ref else None
            changes[name] = ((cps - ref_cps) / ref_cps * 100.0) if cps is not None and ref_cps else None
        changes["original_cpp_o3"] = changes["original_cpp_clang_o3"]
        timing = (artifact.metadata or {}).get("timing")
        break_even_references = {
            "selected_reference": baseline,
            **references,
        }
        break_even = {}
        for name, reference in break_even_references.items():
            if reference is None:
                break_even[name] = None
                continue
            reference_cps = _median(stats_map.get(reference.matrix_key))
            break_even[name] = {
                "reference_artifact_id": reference.artifact_id,
                "reference_matrix_key": reference.matrix_key,
                **calculate_break_even(reference_cps, cps, timing),
            }
        artifact_reports.append({
            **artifact.report_identity(),
            "median_calls_per_second": cps,
            "percentage_change_vs": changes,
            "timing": timing,
            "break_even_vs_reference": calculate_break_even(baseline_cps, cps, timing),
            "break_even": break_even,
        })
    return {
        "benchmark_name": benchmark_name,
        "reference": baseline.report_identity() if baseline else None,
        "references": reference_report,
        "winners": winners,
        "artifacts": artifact_reports,
    }

def main():
    parser = argparse.ArgumentParser(description="Unified final benchmark matrix for cross-experiment comparison.")
    parser.add_argument("--results-root", type=Path, default=PROJECT_ROOT / "results", help="Root directory for experiment results.")
    parser.add_argument("--artifact-manifest", type=Path, help="JSON manifest of artifacts to benchmark.")
    parser.add_argument("--source-run", action="append", type=Path, help="Exact optimization run directory to include; repeat for LLVM, naive C++, guided C++, and IR runs.")
    parser.add_argument("--allow-recursive-discovery", action="store_true", help="Legacy diagnostic mode: recursively discover results-root. Not recommended for definitive runs.")
    parser.add_argument("--only", action="append", help="Benchmark only these functions.")
    parser.add_argument("--benchmark-repetitions", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--noise-threshold-percent", type=float, default=2.0)
    parser.add_argument("--reference-artifact", help="Artifact ID to use as reference for comparisons.")
    parser.add_argument("--include-intermediate-artifacts", action="store_true", help="Include guided baselines and iteration candidates for diagnostics.")
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "results")
    parser.add_argument("--run-id", help="Explicit run ID.")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    run_id = make_run_id(args.run_id)
    experiment_type = "final-matrix"
    run_dir = get_standard_path(args.output_root, experiment_type, run_id)
    if args.run_id and run_dir.exists() and not args.resume:
        print(f"Error: Run ID '{args.run_id}' already exists. Use --resume or choose another ID.")
        return 2
    run_dir.mkdir(parents=True, exist_ok=True)
    
    protocol = BenchmarkProtocol(
        repetitions=args.benchmark_repetitions,
        seed=args.seed,
        noise_threshold_percent=args.noise_threshold_percent,
        ordering="randomized"
    )
    
    run_meta = get_run_metadata()
    run_meta.update({
        "run_id": run_id,
        "experiment_type": experiment_type,
        "benchmark_protocol": asdict(protocol),
        "args": vars(args)
    })
    write_json_atomic(run_dir / "run.json", run_meta)

    # 1. Discover Artifacts
    selection_mode = None
    selected_source_runs: list[str] = []
    if args.artifact_manifest and args.source_run:
        print("Error: use either --artifact-manifest or --source-run, not both.")
        return 2
    if args.artifact_manifest:
        selection_mode = "artifact_manifest"
        with open(args.artifact_manifest) as f:
            manifest = json.load(f)
            artifacts = []
            for entry in manifest.get("artifacts", []):
                item = dict(entry)
                item["library_path"] = Path(item["library_path"])
                if item.get("source_run_path"):
                    item["source_run_path"] = Path(item["source_run_path"])
                if item.get("artifact_metadata_path"):
                    item["artifact_metadata_path"] = Path(item["artifact_metadata_path"])
                metadata_path = item.get("artifact_metadata_path")
                if not item.get("metadata") and metadata_path and metadata_path.exists():
                    item["metadata"] = json.loads(metadata_path.read_text(encoding="utf-8"))
                artifacts.append(ArtifactDefinition(**item))
        selected_source_runs = sorted({str(a.source_run_path.resolve()) for a in artifacts if a.source_run_path})
    elif args.source_run:
        selection_mode = "explicit_source_runs"
        try:
            artifacts = discover_selected_runs(args.source_run, include_intermediate=args.include_intermediate_artifacts)
        except ValueError as exc:
            print(f"Error: {exc}")
            return 2
        selected_source_runs = [str(path.resolve()) for path in args.source_run]
    elif args.allow_recursive_discovery:
        selection_mode = "legacy_recursive_discovery"
        print(f"Warning: recursively discovering artifacts in {args.results_root}; use explicit source runs for final experiments.")
        artifacts = discover_artifacts(args.results_root, include_intermediate=args.include_intermediate_artifacts)
    else:
        print("Error: explicitly select artifacts with --source-run (repeatable) or --artifact-manifest. "
              "Use --allow-recursive-discovery only for legacy diagnostics.")
        return 2

    run_meta["artifact_selection"] = {
        "mode": selection_mode,
        "manifest_path": str(args.artifact_manifest.resolve()) if args.artifact_manifest else None,
        "source_run_paths": selected_source_runs,
    }
    write_json_atomic(run_dir / "run.json", run_meta)
    

    # Whole-library artifacts (notably pure LLVM builds) are valid for every
    # benchmark. Expand them before applying --only and grouping.
    expanded_artifacts: list[ArtifactDefinition] = []
    for artifact in artifacts:
        if artifact.benchmark_name == "all":
            for benchmark_name in FUNCTION_TO_BENCHMARK_ID:
                expanded_artifacts.append(ArtifactDefinition(
                    artifact_id=artifact.artifact_id,
                    experiment_type=artifact.experiment_type,
                    benchmark_name=benchmark_name,
                    library_path=artifact.library_path,
                    model_id=artifact.model_id,
                    pipeline_id=artifact.pipeline_id,
                    run_id=artifact.run_id,
                    metadata=artifact.metadata,
                    source_run_path=artifact.source_run_path,
                    artifact_metadata_path=artifact.artifact_metadata_path,
                ))
        else:
            expanded_artifacts.append(artifact)
    artifacts = expanded_artifacts

    if args.reference_artifact:
        exact_keys = [a for a in artifacts if a.matrix_key == args.reference_artifact]
        matching_ids = [a for a in artifacts if a.artifact_id == args.reference_artifact]
        if not exact_keys and len(matching_ids) > 1:
            print(f"Error: reference artifact ID '{args.reference_artifact}' is ambiguous across selected runs. "
                  "Use one of the matrix keys recorded in a prior summary or select fewer runs.")
            return 2

    if args.only:
        artifacts = [a for a in artifacts if a.benchmark_name in args.only]
    
    if not artifacts:
        print("No artifacts found.")
        return 0

    print(f"Found {len(artifacts)} artifacts across {len(set(a.benchmark_name for a in artifacts))} benchmarks.")

    # 2. Group by Benchmark
    by_benchmark = {}
    for a in artifacts:
        by_benchmark.setdefault(a.benchmark_name, []).append(a)

    all_summaries = []

    # 3. Process each benchmark group
    for bname, arts in by_benchmark.items():
        print(f"\n=== Benchmarking {bname} matrix ({len(arts)} artifacts) ===")
        
        # Validate artifacts
        valid_arts = []
        for a in arts:
            if not a.library_path.exists():
                print(f"  Skipping {a.artifact_id}: library missing at {a.library_path}")
                continue
            
            # ABI Check
            abi_dir = run_dir / "validation" / sanitize_name(a.matrix_key)
            abi_dir.mkdir(parents=True, exist_ok=True)
            abi_cmd = run_abi_symbol_check(abi_dir, a.library_path)
            abi_outcome = load_abi_check_outcome(abi_dir, abi_cmd)
            if not abi_outcome.success:
                print(f"  Skipping {a.artifact_id}: ABI check failed: {abi_outcome.error}")
                continue
            
            # Correctness Check (one run)
            print(f"  Verifying correctness for {a.artifact_id}...")
            corr_res = run_benchmarks_for_lib(abi_dir, a.library_path, bname, run_all=False, artifact_id=a.artifact_id)
            if not all(m.returncode == 0 for m in corr_res):
                print(f"  Skipping {a.artifact_id}: Correctness test failed.")
                continue
            
            valid_arts.append(a)

        if not valid_arts:
            print(f"  No valid artifacts for {bname}.")
            continue

        # Balanced Randomized Schedule
        matrix_keys = [a.matrix_key for a in valid_arts]
        sequence = get_randomized_balanced_sequence(matrix_keys, protocol.repetitions, protocol.seed)
        
        all_measurements: List[BenchmarkMeasurement] = []
        reps = {key: 0 for key in matrix_keys}
        
        for i, matrix_key in enumerate(sequence):
            art = next(a for a in valid_arts if a.matrix_key == matrix_key)
            iteration = reps[matrix_key]
            reps[matrix_key] += 1
            
            print(f"  [{i+1}/{len(sequence)}] {art.artifact_id} [{matrix_key}] (rep {iteration})...")
            measurements = run_benchmarks_for_lib(
                run_dir / "benchmarks" / sanitize_name(matrix_key),
                art.library_path, 
                bname,
                run_all=False, 
                iteration=iteration,
                artifact_id=matrix_key,
                sequence_index=i
            )
            all_measurements.extend(measurements)

        # Statistics and Comparisons
        stats_map = {}
        for matrix_key in matrix_keys:
            ms = [m for m in all_measurements if m.artifact_id == matrix_key]
            stats = calculate_benchmark_statistics(ms, protocol.repetitions)
            stats_map[matrix_key] = stats

        # Reference artifact for this benchmark
        ref_key = next((a.matrix_key for a in valid_arts if args.reference_artifact in {a.artifact_id, a.matrix_key}), None) if args.reference_artifact else None
        if not ref_key:
            # Fallback: look for llvm__o1 or llvm__o3 or any llvm
            ref_candidates = [a for a in valid_arts if a.experiment_type == "llvm"]
            if ref_candidates:
                ref_art = ref_candidates[0]
                # Prefer O1 if available
                o1_cands = [a for a in ref_candidates if "o1" in (a.pipeline_id or "").lower() or "__o1" in a.artifact_id.lower()]
                if o1_cands: ref_art = o1_cands[0]
                ref_key = ref_art.matrix_key
            else:
                ref_key = matrix_keys[0]
        
        ref_artifact = next(a for a in valid_arts if a.matrix_key == ref_key)
        print(f"  Reference artifact: {ref_artifact.artifact_id} [{ref_key}]")
        
        comparisons = {}
        for matrix_key in matrix_keys:
            if matrix_key == ref_key: continue
            comp = compare_benchmarks(
                stats_map[matrix_key],
                stats_map[ref_key],
                protocol.noise_threshold_percent,
                ref_key,
                matrix_key,
                sequence
            )
            comparisons[matrix_key] = asdict(comp)

        bench_summary = {
            "benchmark_name": bname,
            "artifact_ids": [a.artifact_id for a in valid_arts],
            "artifact_keys": matrix_keys,
            "artifact_sources": [a.report_identity() for a in valid_arts],
            "reference_artifact_id": ref_artifact.artifact_id,
            "reference_artifact_key": ref_key,
            "statistics": {key: asdict(s) for key, s in stats_map.items()},
            "comparisons_vs_reference": comparisons,
            "sequence": sequence,
            **build_benchmark_report(bname, valid_arts, stats_map, ref_key),
        }
        
        bench_dir = run_dir / "benchmarks" / bname
        bench_dir.mkdir(parents=True, exist_ok=True)
        write_json_atomic(bench_dir / "summary.json", bench_summary)
        all_summaries.append(bench_summary)

    write_json_atomic(run_dir / "summary.json", all_summaries)
    print(f"\nFinal matrix summary written to: {run_dir / 'summary.json'}")

if __name__ == "__main__":
    main()
