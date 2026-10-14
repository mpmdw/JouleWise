"""Small synthetic registrations and evidence, created only in test TMPDIR."""

import json
from pathlib import Path

from joulewise.b6.acceptance import ACCEPTANCE
from joulewise.b6.acceptance_interface import CaptureEvidence, MemberEvidence, SessionEvidence, StageEvidence

ROOT = Path(__file__).resolve().parents[2]
IDENTITY = {"model_source": "synthetic-model", "model_artifact_sha256": "a" * 64,
            "status": "ok", "packages": {"mlx": "1", "mlx-lm": "2", "transformers": "3"},
            "quantization": {"name": "int4", "bits": 4}, "runtime": "mlx"}


def document() -> dict:
    return {"schema": "joulewise.b6_acceptance_registration.v1", "pack_id": "desk-pack",
            "registered_commit": "unused-without-executed-head",
            "neg8": {"corpus_minimum": 6, "corpus_cap": 12,
                     "planned": {"start": 3, "midpoint": 1, "end": 3}},
            "calibration": {"alignment_reference_s": "0.036462861644980",
                            "bracket_screen_s": "0.014531", "max_budgetable_drift_s": "0.015502",
                            "operative_bound_stop_s": "0.092", "acceptance_corpus": ["0.028"] * 24}}


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def registration_dir(root: Path) -> Path:
    target = root / "registration"
    write_json(target / "acceptance.json", document())
    write_json(target / "identity_pins.json", {
        "runtime_versions": {"packages": IDENTITY["packages"]}, "units": {"desk": {
            "model_source": IDENTITY["model_source"], "model_artifact_sha256": IDENTITY["model_artifact_sha256"],
            "stack_identity": {"runtime_version": {"name": "mlx"}, "quantization": IDENTITY["quantization"]}}}})
    return target


def prepared(root: Path, *, rows=(), tree=None):
    return ACCEPTANCE.prepare(ledger_path=root / "list.jsonl", ledger_rows=rows,
                              plan_tree=tree or {}, registration_dir=registration_dir(root),
                              code_identity={})


def session(n: int = 5, *, synthetic: bool = True) -> SessionEvidence:
    members = tuple(MemberEvidence("science", f"s{i}", "succeeded", (),
                                   (("decode", "repeat", str(i)),), runtime=IDENTITY) for i in range(n))
    return SessionEvidence("desk-pack", (StageEvidence("science", "campaign_collection", n, members),),
                           (CaptureEvidence("pre", 28.0, "valid", synthetic),
                            CaptureEvidence("post", 28.0, "valid", synthetic)),
                           IDENTITY, synthetic, ("closing_capture", "actual_losses"), "desk-session", "completed")
