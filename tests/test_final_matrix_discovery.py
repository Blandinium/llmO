import json
from pathlib import Path

from run_final_benchmark_matrix import discover_artifacts


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
