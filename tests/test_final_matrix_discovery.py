import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import run_final_benchmark_matrix as final_matrix

from run_final_benchmark_matrix import (
    ArtifactConflictError,
    ArtifactDefinition,
    build_benchmark_report,
    discover_artifacts,
    discover_selected_runs,
)
import pytest
from llmo.benchmark_protocol import BenchmarkStatistics
from llmo.benchmark_protocol import BenchmarkMeasurement


def test_discovers_nested_guided_artifact(tmp_path: Path):
    artifact_dir = tmp_path / "guided-cpp" / "run-1" / "model" / "fibonacci_cpp" / "artifacts" / "guided__final"
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "libSUT.so").write_bytes(b"so")
    (artifact_dir / "artifact.json").write_text(json.dumps({
        "artifact_id": "guided__final",
        "experiment_type": "guided-cpp",
        "run_id": "run-1",
        "benchmark_name": "fibonacci",
        "pipeline_id": "cpp-llm-guided-remarks__clang-o3",
        "paths": {"libsut": str(artifact_dir / "libSUT.so")},
    }))

    artifacts = discover_artifacts(tmp_path)
    assert len(artifacts) == 1
    assert artifacts[0].artifact_id == "guided__final"
    assert artifacts[0].benchmark_name == "fibonacci"
    assert artifacts[0].library_path == artifact_dir / "libSUT.so"


def _write_artifact(root: Path, location: str, *, artifact_id: str = "guided__final",
                    experiment_type: str = "guided-cpp", run_id: str = "run-1",
                    model_id: str = "qwen3", benchmark: str = "fibonacci",
                    pipeline: str = "cpp-guided-o3", content: bytes = b"same") -> Path:
    artifact_dir = root / location
    artifact_dir.mkdir(parents=True)
    library = artifact_dir / "libSUT.so"
    library.write_bytes(content)
    (artifact_dir / "artifact.json").write_text(json.dumps({
        "artifact_id": artifact_id,
        "experiment_type": experiment_type,
        "run_id": run_id,
        "model_id": model_id,
        "benchmark_name": benchmark,
        "pipeline_id": pipeline,
        "is_final_artifact": True,
        "paths": {"libsut": str(library)},
    }))
    return artifact_dir


def test_same_logical_artifact_in_two_paths_is_one_candidate(tmp_path: Path):
    canonical = _write_artifact(tmp_path, "task/artifacts/guided__final")
    alias = _write_artifact(tmp_path, "task/export/guided__final")

    artifacts = discover_artifacts(tmp_path)

    assert len(artifacts) == 1
    assert artifacts[0].library_path == canonical / "libSUT.so"
    assert artifacts[0].alias_paths == [alias / "artifact.json"]


def test_conflicting_duplicate_fails_loudly(tmp_path: Path):
    first = _write_artifact(tmp_path, "task/artifacts/guided__final", content=b"first")
    second = _write_artifact(tmp_path, "task/export/guided__final", content=b"second")

    with pytest.raises(ArtifactConflictError) as error:
        discover_artifacts(tmp_path)

    message = str(error.value)
    assert "guided-cpp/run-1/qwen3/fibonacci/cpp-guided-o3/guided__final" in message
    assert str(first / "libSUT.so") in message
    assert str(second / "libSUT.so") in message
    assert "sha256" in message


def test_similar_but_distinct_artifacts_are_not_deduplicated(tmp_path: Path):
    _write_artifact(tmp_path, "guided-qwen3", model_id="qwen3")
    _write_artifact(tmp_path, "guided-qwen25", artifact_id="guided_qwen25__final", model_id="qwen2.5-coder")
    _write_artifact(tmp_path, "naive-qwen3", artifact_id="naive__final", experiment_type="naive-cpp", model_id="qwen3")
    _write_artifact(tmp_path, "llvm-o2", artifact_id="llvm__o2", experiment_type="llvm", model_id="", pipeline="clang-o2")
    _write_artifact(tmp_path, "llvm-o3", artifact_id="llvm__o3", experiment_type="llvm", model_id="", pipeline="clang-o3")

    artifacts = discover_artifacts(tmp_path)

    assert len(artifacts) == 5
    assert len({artifact.logical_artifact_id for artifact in artifacts}) == 5


def test_canonical_task_metadata_disables_legacy_summary_fallback(tmp_path: Path):
    task = tmp_path / "guided-cpp" / "run-1" / "qwen3" / "fibonacci_cpp"
    baseline = task / "artifacts" / "guided__baseline"
    baseline.mkdir(parents=True)
    (baseline / "libSUT.so").write_bytes(b"baseline")
    _write_artifact(task, "artifacts/guided__final", content=b"final")
    (task / "summary.json").write_text(json.dumps({
        "experiment_type": "guided-cpp",
        "run_id": "run-1",
        "final_confirmation_id": "guided__final",
    }))

    artifacts = discover_artifacts(tmp_path)

    assert len(artifacts) == 1
    assert artifacts[0].library_path.read_bytes() == b"final"


def test_discovers_canonical_llvm_artifact(tmp_path: Path):
    artifact_dir = tmp_path / "llvm" / "run-1" / "artifacts" / "llvm__o3"
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "libSUT.so").write_bytes(b"so")
    (artifact_dir / "artifact.json").write_text(json.dumps({
        "artifact_id": "llvm__o3",
        "experiment_type": "llvm",
        "run_id": "run-1",
        "benchmark_name": "all",
        "pipeline_id": "cpp-clang-o3",
        "paths": {"canonical_libsut": str(artifact_dir / "libSUT.so")},
    }))

    artifacts = discover_artifacts(tmp_path)
    assert len(artifacts) == 1
    assert artifacts[0].benchmark_name == "all"
    assert artifacts[0].library_path.exists()


def test_ignores_list_valued_legacy_summary(tmp_path: Path):
    run_dir = tmp_path / "guided-cpp" / "run-1"
    run_dir.mkdir(parents=True)
    (run_dir / "summary.json").write_text(json.dumps([
        {"benchmark_name": "fibonacci", "status": "completed"}
    ]))
    (run_dir / "libSUT.so").write_bytes(b"so")

    assert discover_artifacts(tmp_path) == []


def test_ignores_non_object_artifact_metadata(tmp_path: Path):
    artifact_dir = tmp_path / "llvm" / "run-1" / "artifacts" / "bad"
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "libSUT.so").write_bytes(b"so")
    (artifact_dir / "artifact.json").write_text(json.dumps([
        {"artifact_id": "not-an-object"}
    ]))

    assert discover_artifacts(tmp_path) == []


def test_guided_intermediate_artifacts_filtered_by_default(tmp_path: Path):
    base = tmp_path / "guided-cpp" / "run-1" / "model" / "count_matches_cpp" / "artifacts"
    for suffix in ("baseline", "iteration-01", "final"):
        artifact_id = f"guided-cpp__model__count_matches__{suffix}"
        artifact_dir = base / artifact_id
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "libSUT.so").write_bytes(b"so")
        (artifact_dir / "artifact.json").write_text(json.dumps({
            "artifact_id": artifact_id,
            "experiment_type": "guided-cpp",
            "run_id": "run-1",
            "benchmark_name": "count_matches",
            "paths": {"libsut": str(artifact_dir / "libSUT.so")},
        }))

    default = discover_artifacts(tmp_path)
    assert [a.artifact_id for a in default] == ["guided-cpp__model__count_matches__final"]

    diagnostic = discover_artifacts(tmp_path, include_intermediate=True)
    assert {a.artifact_id for a in diagnostic} == {
        "guided-cpp__model__count_matches__baseline",
        "guided-cpp__model__count_matches__iteration-01",
        "guided-cpp__model__count_matches__final",
    }


def test_naive_confirmed_candidate_copy_is_filtered_in_favor_of_final(tmp_path: Path):
    base = tmp_path / "naive-cpp" / "run-1" / "qwen3" / "fibonacci_cpp"
    candidate = _write_artifact(
        base, "candidate", artifact_id="naive__candidate",
        experiment_type="naive-cpp", content=b"accepted",
    )
    candidate_meta = json.loads((candidate / "artifact.json").read_text())
    candidate_meta.update({"artifact_role": "candidate", "confirmed_improvement": True})
    (candidate / "artifact.json").write_text(json.dumps(candidate_meta))
    _write_artifact(
        base, "final", artifact_id="naive__final",
        experiment_type="naive-cpp", content=b"accepted",
    )

    artifacts = discover_artifacts(tmp_path)

    assert [artifact.artifact_id for artifact in artifacts] == ["naive__final"]


def test_expands_legacy_ir_summary_without_vague_artifact(tmp_path: Path):
    target = tmp_path / "llm-ir" / "run-1" / "model-a" / "count_matches_cpp"
    target.mkdir(parents=True)
    (target / "summary.json").write_text(json.dumps({
        "run_id": "run-1",
        "experiment_type": "llm-ir",
        "model_id": "model-a",
        "benchmark_name": "count_matches",
        "backend_results": {"-O0": {}, "-O3": {}},
    }))
    for level in ("O0", "O3"):
        for role in ("baseline", "candidate"):
            d = target / f"backend_{level}" / role
            d.mkdir(parents=True)
            (d / "libSUT.so").write_bytes(b"so")

    artifacts = discover_artifacts(tmp_path)
    assert len(artifacts) == 4
    ids = {a.artifact_id for a in artifacts}
    assert "count_matches_cpp" not in ids
    assert "llm-ir__model-a__count_matches__ir-o1_backend-o0__candidate" in ids
    assert "llm-ir__model-a__count_matches__ir-o1_backend-o3__baseline" in ids


def test_explicit_runs_keep_duplicate_ids_unambiguous(tmp_path: Path):
    runs = []
    for run_id in ("smoke", "final"):
        run = tmp_path / "naive-cpp" / run_id
        artifact_dir = run / "model" / "count_matches_cpp"
        artifact_dir.mkdir(parents=True)
        (artifact_dir / "libSUT.so").write_bytes(run_id.encode())
        (artifact_dir / "artifact.json").write_text(json.dumps({
            "artifact_id": "naive-cpp__model__count-matches__candidate",
            "experiment_type": "naive-cpp",
            "run_id": run_id,
            "benchmark_name": "count_matches",
            "paths": {"libsut": str(artifact_dir / "libSUT.so")},
        }))
        runs.append(run)

    selected = discover_selected_runs(runs)
    assert len(selected) == 2
    assert selected[0].artifact_id == selected[1].artifact_id
    assert selected[0].matrix_key != selected[1].matrix_key
    assert {a.source_run_path for a in selected} == {p.resolve() for p in runs}
    isolated = discover_selected_runs([runs[1]])
    assert len(isolated) == 1
    assert isolated[0].run_id == "final"
    assert isolated[0].library_path.read_bytes() == b"final"


def test_category_winners_and_references_come_from_matrix_statistics(tmp_path: Path):
    def artifact(aid, exp, cps, pipeline, timing=None):
        lib = tmp_path / f"{aid}.so"
        lib.write_bytes(b"so")
        art = ArtifactDefinition(aid, exp, "fib", lib, pipeline_id=pipeline, metadata={"timing": timing} if timing else {})
        stats[art.matrix_key] = BenchmarkStatistics(5, 5, cps, cps, cps, cps, 0)
        return art

    stats = {}
    llvm_o1 = artifact("llvm__o1", "llvm", 100, "cpp-clang-o1")
    llvm_o3 = artifact("llvm__o3", "llvm", 120, "cpp-clang-o3")
    naive = artifact("naive__candidate", "naive-cpp", 130, "cpp-llm-naive")
    guided = artifact("guided__final", "guided-cpp", 140, "cpp-llm-guided")
    ir = artifact("ir__candidate", "llm-ir", 135, "ir-o1__backend-o3")
    report = build_benchmark_report("fib", [llvm_o1, llvm_o3, naive, guided, ir], stats, llvm_o1.matrix_key)
    assert report["winners"]["fastest_llvm"]["artifact_id"] == "llvm__o3"
    assert report["winners"]["fastest_naive_cpp"]["artifact_id"] == "naive__candidate"
    assert report["winners"]["fastest_guided_cpp"]["artifact_id"] == "guided__final"
    assert report["winners"]["fastest_llm_ir"]["artifact_id"] == "ir__candidate"
    assert report["winners"]["fastest_overall"]["artifact_id"] == "guided__final"
    assert report["references"]["llvm_o1"]["artifact_id"] == "llvm__o1"
    assert report["references"]["original_cpp_clang_o3"]["artifact_id"] == "llvm__o3"
    assert report["references"]["original_cpp_o3"] == report["references"]["original_cpp_clang_o3"]


def test_break_even_uses_o1_and_stronger_llvm_references(tmp_path: Path):
    stats = {}

    def artifact(aid, exp, cps, pipeline, timing=None):
        lib = tmp_path / f"{aid}.so"
        lib.write_bytes(b"so")
        art = ArtifactDefinition(aid, exp, "fib", lib, pipeline_id=pipeline, metadata={"timing": timing} if timing else {})
        stats[art.matrix_key] = BenchmarkStatistics(5, 5, cps, cps, cps, cps, 0)
        return art

    llvm_o1 = artifact("llvm__o1", "llvm", 100, "cpp-clang-o1")
    llvm_o3 = artifact("llvm__o3", "llvm", 130, "cpp-clang-o3")
    timing = {"total_llm_seconds": 10.0, "optimization_pipeline_seconds": 20.0}
    slower_than_llvm = artifact("naive__125", "naive-cpp", 125, "cpp-llm-naive", timing)
    faster_than_llvm = artifact("guided__140", "guided-cpp", 140, "cpp-llm-guided", timing)
    artifacts = [llvm_o1, llvm_o3, slower_than_llvm, faster_than_llvm]
    report = build_benchmark_report("fib", artifacts, stats, llvm_o1.matrix_key)
    by_id = {entry["artifact_id"]: entry for entry in report["artifacts"]}

    slower = by_id["naive__125"]["break_even"]
    assert slower["selected_reference"]["break_even_calls_llm"] is not None
    assert slower["llvm_o1"]["break_even_calls_llm"] is not None
    assert slower["fastest_llvm"]["reference_artifact_id"] == "llvm__o3"
    assert slower["fastest_llvm"]["break_even_calls_llm"] is None
    assert slower["original_cpp_clang_o3"]["break_even_calls_pipeline"] is None

    faster = by_id["guided__140"]["break_even"]
    assert faster["fastest_llvm"]["break_even_calls_llm"] is not None
    assert faster["original_cpp_clang_o3"]["break_even_calls_pipeline"] is not None


def test_break_even_reports_missing_llvm_references_as_unavailable(tmp_path: Path):
    lib = tmp_path / "candidate.so"
    lib.write_bytes(b"so")
    candidate = ArtifactDefinition(
        "naive", "naive-cpp", "fib", lib,
        metadata={"timing": {"total_llm_seconds": 1.0, "optimization_pipeline_seconds": 2.0}},
    )
    stats = {candidate.matrix_key: BenchmarkStatistics(5, 5, 120, 120, 120, 120, 0)}
    report = build_benchmark_report("fib", [candidate], stats, candidate.matrix_key)
    break_even = report["artifacts"][0]["break_even"]
    assert break_even["llvm_o1"] is None
    assert break_even["fastest_llvm"] is None
    assert break_even["original_cpp_clang_o3"] is None


def test_break_even_with_missing_timing_has_null_cost_results(tmp_path: Path):
    stats = {}
    llvm_lib = tmp_path / "llvm.so"
    candidate_lib = tmp_path / "candidate.so"
    llvm_lib.write_bytes(b"so")
    candidate_lib.write_bytes(b"so")
    llvm = ArtifactDefinition("llvm__o1", "llvm", "fib", llvm_lib, pipeline_id="cpp-clang-o1")
    candidate = ArtifactDefinition("naive", "naive-cpp", "fib", candidate_lib)
    stats[llvm.matrix_key] = BenchmarkStatistics(5, 5, 100, 100, 100, 100, 0)
    stats[candidate.matrix_key] = BenchmarkStatistics(5, 5, 150, 150, 150, 150, 0)
    report = build_benchmark_report("fib", [llvm, candidate], stats, llvm.matrix_key)
    candidate_report = next(entry for entry in report["artifacts"] if entry["artifact_id"] == "naive")
    assert candidate_report["break_even"]["selected_reference"]["break_even_calls_llm"] is None
    assert candidate_report["break_even"]["llvm_o1"]["break_even_calls_pipeline"] is None


def test_matrix_benchmarks_duplicate_ids_once_per_repetition(tmp_path: Path, monkeypatch):
    runs = []
    libraries = []
    for run_id in ("old-smoke", "fresh-final"):
        run = tmp_path / "naive-cpp" / run_id
        d = run / "model" / "count_matches_cpp"
        d.mkdir(parents=True)
        lib = d / "libSUT.so"
        lib.write_bytes(run_id.encode())
        (d / "artifact.json").write_text(json.dumps({
            "artifact_id": "duplicate-id",
            "experiment_type": "naive-cpp",
            "run_id": run_id,
            "benchmark_name": "count_matches",
            "paths": {"libsut": str(lib)},
        }))
        runs.append(run)
        libraries.append(lib)

    monkeypatch.setattr(final_matrix, "run_abi_symbol_check", MagicMock())
    monkeypatch.setattr(final_matrix, "load_abi_check_outcome", MagicMock(return_value=MagicMock(success=True)))
    benchmarked = []

    def fake_benchmark(output_dir, library_path, benchmark_name, **kwargs):
        artifact_id = kwargs.get("artifact_id", "correctness")
        if "iteration" in kwargs:
            benchmarked.append((Path(library_path), kwargs["iteration"], artifact_id))
        return [BenchmarkMeasurement(
            artifact_id, 0, benchmark_name, kwargs.get("iteration", 0), kwargs.get("sequence_index", 0),
            100.0, 1, 1, "ok", 0, {}, "out", "err",
        )]

    monkeypatch.setattr(final_matrix, "run_benchmarks_for_lib", fake_benchmark)
    argv = ["run_final_benchmark_matrix.py"]
    for run in runs:
        argv += ["--source-run", str(run)]
    argv += ["--benchmark-repetitions", "2", "--output-root", str(tmp_path / "out"), "--run-id", "matrix"]
    monkeypatch.setattr(sys, "argv", argv)
    assert final_matrix.main() is None

    assert len(benchmarked) == 4
    for library in libraries:
        calls = [call for call in benchmarked if call[0] == library]
        assert [call[1] for call in calls] == [0, 1]
        assert len({call[2] for call in calls}) == 1
    assert len({call[2] for call in benchmarked}) == 2

    summary = json.loads((tmp_path / "out" / "final-matrix" / "matrix" / "summary.json").read_text())
    assert len(summary[0]["artifact_sources"]) == 2
    assert {a["run_id"] for a in summary[0]["artifact_sources"]} == {"old-smoke", "fresh-final"}
