import json
from pathlib import Path

from run_ir_optimization import publish_ir_backend_artifact
from run_final_benchmark_matrix import discover_artifacts


def test_publish_ir_backend_artifact_is_canonical_and_discoverable(tmp_path: Path):
    build = tmp_path / "build"
    build.mkdir()
    lib = build / "libSUT.so"
    ir = build / "optimized.ll"
    lib.write_bytes(b"shared-library")
    ir.write_text("target datalayout = \"x\"\ntarget triple = \"x86_64\"\n")

    aid = "llm-ir__model__count_matches__ir-o1_backend-o3__candidate"
    artifact_dir = publish_ir_backend_artifact(
        tmp_path,
        "run-1",
        aid,
        model_id="model",
        benchmark_name="count_matches",
        pipeline_id="ir-o1__backend-o3",
        role="candidate",
        library_path=lib,
        ir_path=ir,
        comparison={"classification": "unchanged_within_noise"},
    )

    meta = json.loads((artifact_dir / "artifact.json").read_text())
    assert meta["artifact_id"] == aid
    assert meta["artifact_role"] == "candidate"
    assert meta["is_final_artifact"] is True
    assert (artifact_dir / "libSUT.so").exists()
    assert (artifact_dir / "optimized.ll").exists()

    discovered = discover_artifacts(tmp_path)
    assert [a.artifact_id for a in discovered] == [aid]
