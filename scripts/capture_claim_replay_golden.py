#!/usr/bin/env python3
"""Capture the checked-in v1 claim and validator decisions before CG-4.

Requires a Git checkout. Refresh the resulting blob only in a reviewed PR,
together with its test pin.
The 09-19 source records contain authenticated slot outcomes; their underlying
measurement bundles are outside this repository.  Replay the public decision
function from those recorded outcomes, without claiming to reauthenticate them.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise import paper_custody as custody
from joulewise.analysis_engine.artifact import validate_claim_verdicts
from joulewise.analysis_engine.claims import evaluate_claim
from joulewise.analysis_engine.registry import validate_analysis_manifest_v2, validate_analysis_registry_v2
from joulewise.analysis_manifest import validate_analysis_manifest, validate_analysis_registry
from joulewise.analysis_manifest_v3 import (
    validate_analysis_manifest_v3,
    validate_finalized_analysis_manifest_v3,
    validate_prospective_analysis_manifest_v3,
)
from scripts import epoch_equivalence_check as epoch

GOLDEN = ROOT / "tests/golden/claimgate_v1_replay.json"


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=1,
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _tracked_json() -> list[Path]:
    paths = subprocess.check_output(["git", "ls-files", "-z", "--", "*.json"], cwd=ROOT)
    return [ROOT / p.decode("utf-8") for p in sorted(paths.split(b"\0")) if p]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_bytes())
    except (ValueError, UnicodeError):
        return None


def _errors(call, *args, **kwargs) -> list[str]:
    try:
        result = call(*args, **kwargs)
        return [item if isinstance(item, str) else
                getattr(item, "reason_code", getattr(item, "code", type(item).__name__))
                for item in result] if result is not None else []
    except Exception as exc:
        return [f"{type(exc).__name__}: {getattr(exc, 'code', type(exc).__name__)}"]


def _families() -> dict[str, object]:
    supply = json.loads((ROOT / "configs/paper_supply/supply_map.json").read_text())
    catalog = json.loads((ROOT / "tests/fixtures/paper_custody/family_catalog.json").read_bytes())
    result = {}
    for role, entry in sorted(supply["roles"].items()):
        if not role.startswith("fixture."):
            continue
        family = role.removeprefix("fixture.")
        sources = tuple(custody._BoundFile(
            row["base"], Path(row["path"]), row["expected_sha256"],
            custody.InputRole(row["role"]), row["authority"])
            for row in entry["inputs"])
        # The fixture schema is represented by the checked-in catalog; no
        # production measurement bytes are present in this family.
        raws = {binding.role: canonical_bytes({
            "family": family, "marker": catalog["marker"],
            "role": binding.role.value, "schema_version": "joulewise.paper_custody_fixture.v1",
        }) for binding in sources}
        ctx = custody._GateContext(family, role, "test_fixture_non_issuing", None,
                                   tuple(entry.get("subjects", ())), ROOT, ROOT, "", sources,
                                   (), raws, None)
        replay = custody._replay_family(ctx)
        result[family] = {
            "authentic": replay.authentic, "admitted": replay.admitted,
            "grants": [{"kind": grant.kind, "subject_id": grant.subject_id}
                       for grant in replay.grants],
            "validator_codes": list(replay.validator_codes),
        }
    return result


def _claim_artifacts(paths: list[Path]) -> dict[str, object]:
    result = {}
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        if not ((rel.startswith("docs/paper/fill-rehearsal/") and rel.endswith("claim-verdicts.json"))
                or (rel.startswith("tests/fixtures/") and "claim" in path.name
                    and "verdict" in path.name)):
            continue
        artifact = json.loads(path.read_bytes())
        if artifact.get("schema_version") != "joulewise.claim_verdicts.v1":
            continue
        evaluations = []
        for contrast in artifact["contrasts"]:
            floor = contrast["floor"]
            keys = {"floor_limit_class", "floor_source", "point_floor_diagnostics",
                    "single_count_discipline"}
            arguments = {
                "estimate": contrast["estimator"]["estimate"],
                "metrology_aware_ci95": contrast["estimator"]["metrology_aware_CI95"],
                "decision_interval": contrast["deterministic_bounds"]["decision_interval"],
                "floor_gate_j": floor["active_floor_j"],
                "adjusted_rejected": contrast["multiplicity"]["rejected"] is True,
                "base_reason_codes": contrast["claim_evaluation"]["reason_codes"],
                "equivalence": contrast.get("equivalence"),
                "claim_role": contrast["claim_role"],
                "confirmatory_status": contrast["sampling"]["confirmatory_status"],
                "evidence_class": artifact.get("evidence_class", "current"),
                "floor_metadata": {key: floor[key] for key in keys} if keys <= floor.keys() else None,
                "hypothesized_direction": contrast.get("hypothesized_direction"),
            }
            evaluations.append({"contrast_id": contrast["contrast_id"],
                                "arguments": arguments,
                                "recorded": contrast["claim_evaluation"],
                                "evaluated": evaluate_claim(**arguments)})
            if evaluations[-1]["evaluated"] != evaluations[-1]["recorded"]:
                raise ValueError(f"claim replay disagrees: {rel}:{contrast['contrast_id']}")
        without_scalars = copy.deepcopy(artifact)
        without_scalars.pop("_synthetic_scalars", None)
        result[rel] = {
            "file_sha256": _sha(path),
            "manifest_id": artifact["inputs"]["analysis_manifest"]["manifest_id"],
            "validator_errors": validate_claim_verdicts(artifact),
            "validator_errors_without_synthetic_scalars": validate_claim_verdicts(without_scalars),
            "evaluations": evaluations,
        }
    return result


def _validators(paths: list[Path]) -> dict[str, object]:
    registries = {}
    manifests = {}
    registry_values = {}
    for path in paths:
        value = _read_json(path)
        if not isinstance(value, dict):
            continue
        schema = value.get("schema_version")
        rel = path.relative_to(ROOT).as_posix()
        if schema == "joulewise.analysis_registry.v1":
            errors = _errors(validate_analysis_registry, value)
        elif schema == "joulewise.analysis_registry.v2":
            errors = _errors(validate_analysis_registry_v2, value)
        else:
            continue
        registries[rel] = {"file_sha256": _sha(path), "schema_version": schema,
                           "validator_errors": errors}
        registry_values[value["registry_id"]] = value
    for path in paths:
        value = _read_json(path)
        if not isinstance(value, dict):
            continue
        schema = value.get("schema_version")
        rel = path.relative_to(ROOT).as_posix()
        if schema == "joulewise.analysis_manifest.v2":
            registry = registry_values.get(value.get("registry", {}).get("registry_id"))
            if registry:
                configs = {entry["config"]: (ROOT / entry["config"]).read_bytes()
                           for entry in value["entries"]}
                roster = (ROOT / value["request_roster"]["path"]).read_bytes()
                errors = _errors(validate_analysis_manifest_v2, value, registry,
                                 manifest_bytes=path.read_bytes(), configs=configs,
                                 roster_bytes=roster)
            else:
                errors = ["registry_missing"]
        elif schema == "joulewise.analysis_manifest.v3":
            errors = _errors(validate_analysis_manifest_v3, value, manifest_dir=path.parent)
        elif schema == "joulewise.analysis_manifest.v3.prospective":
            errors = _errors(validate_prospective_analysis_manifest_v3, value,
                             manifest_dir=path.parent, plan_tree_path=path.parent / "plan_tree.json")
        elif schema == "joulewise.analysis_manifest.v1":
            errors = _errors(validate_analysis_manifest, value, manifest_dir=path.parent,
                             repository_root=ROOT)
        elif schema == "joulewise.analysis_manifest.v3.finalized":
            errors = _errors(validate_finalized_analysis_manifest_v3, value,
                             manifest_path=path, custody_root=ROOT)
        else:
            continue
        manifests[rel] = {"file_sha256": _sha(path), "schema_version": schema,
                          "manifest_id": value.get("manifest_id"),
                          "validator_errors": errors}
    return {"manifests": manifests, "registries": registries}


def _epoch_replays() -> dict[str, object]:
    sources = {
        "09-19-n1": "docs/process_traces/2026-09-19-activation-b165c535/01-harvest-evidence/epoch-equivalence-record-2.json",
        "09-19-n2": "docs/process_traces/2026-09-19-activation-d0b83820/01-harvest-evidence/epoch-equivalence-record-2.json",
        "s9-pass": "tests/fixtures/epoch_continuation/s9-pass.json",
        "s9-fail-bracket": "tests/fixtures/epoch_continuation/s9-fail-bracket.json",
        "s9-fail-level": "tests/fixtures/epoch_continuation/s9-fail-level.json",
    }
    result = {}
    for name, rel in sources.items():
        path = ROOT / rel
        recorded = json.loads(path.read_bytes())
        session = SimpleNamespace(**recorded["session"])
        with mock.patch.object(epoch, "_slot_outcomes", return_value=(
            recorded["slot_outcomes"], recorded["retained"])):
            replay = epoch.evaluate_session(session, session.session_id,
                                            recorded["reference_envelope"])
        result[name] = {"source": rel, "source_sha256": _sha(path),
                        "recorded": recorded, "replayed": replay}
        if {key: recorded[key] for key in replay} != replay:
            raise ValueError(f"epoch replay disagrees: {name}")
    return result


def _claim_matrix() -> dict[str, object]:
    # Attribution metadata is the validated wire on an existing v1 verdict.
    from joulewise.detection_floor import (
        ATTRIBUTION_FLOOR_SOURCE, ATTRIBUTION_LIMIT_CLASS,
        attribution_single_count_discipline,
    )
    valid_metadata = {
        "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
        "floor_source": ATTRIBUTION_FLOOR_SOURCE,
        "point_floor_diagnostics": {},
        "single_count_discipline": attribution_single_count_discipline(),
    }
    base = {"estimate": 2.0, "metrology_aware_ci95": {"lower": 1.5, "upper": 2.5},
            "decision_interval": {"lower": 1.25, "upper": 2.75}, "floor_gate_j": 1.0,
            "adjusted_rejected": True}
    cases = {
        "direction_above": {}, "direction_at_floor": {"estimate": 1.0},
        "direction_below_floor": {"estimate": 0.5},
        "multiplicity_not_rejected": {"adjusted_rejected": False},
        "legacy_l1": {"evidence_class": "legacy_l1"},
        "non_confirmatory": {"confirmatory_status": "exploratory"},
        "sensitivity_blocking": {"sensitivity_blocking": True},
        "direction_mismatch": {"hypothesized_direction": "negative"},
        "floor_none": {"floor_gate_j": None},
        "floor_negative": {"floor_gate_j": -1.0},
        "valid_floor_metadata": {"floor_metadata": valid_metadata},
        "invalid_floor_metadata": {"floor_metadata": {**valid_metadata, "floor_source": "wrong"}},
        "equivalence_margin_at_floor_inside": {"equivalence": {"method": "tost_v1", "margin": 1.0}, "metrology_aware_ci95": {"lower": -0.5, "upper": 0.5}, "decision_interval": {"lower": -0.75, "upper": 0.75}},
        "equivalence_margin_at_floor_outside": {"equivalence": {"method": "tost_v1", "margin": 1.0}},
        "equivalence_margin_above_floor_inside": {"equivalence": {"method": "tost_v1", "margin": 3.0}},
        "equivalence_margin_above_floor_outside": {"equivalence": {"method": "tost_v1", "margin": 1.5}},
    }
    return {name: {"inputs": arguments, "output": evaluate_claim(**arguments)}
            for name, override in cases.items()
            for arguments in [{**base, **override}]}


def _window_engine() -> dict[str, object]:
    """Replay the existing v1 artifact and v3 window test builders."""
    from joulewise.analysis_engine import _resolve_contrast_floor
    from joulewise.analysis_engine.inputs import FloorRequest
    from tests.test_analysis_claims import minimal_artifact
    from tests.test_analysis_integration import _v3_fixture_artifact

    scenarios = {"minimal_v1_artifact": minimal_artifact(),
                 "v3_window_clean": _v3_fixture_artifact(),
                 "v3_window_supersession_diverged": _v3_fixture_artifact(diverged=True)}
    result = {}
    for name, artifact in scenarios.items():
        result[name] = {
            "manifest_id": artifact["inputs"]["analysis_manifest"]["manifest_id"],
            "validator_errors": validate_claim_verdicts(artifact),
            "contrasts": {row["contrast_id"]: row["claim_evaluation"]
                          for row in artifact["contrasts"]},
        }
    # The existing v3 window builder runs analyze_claims with its established
    # patches. The captured artifact above is its returned value.
    inputs = SimpleNamespace(manifest={"schema_version": "joulewise.analysis_manifest.v1"},
                             floor_artifact={"artifact_id": "df-selector-control"},
                             floor_sha256="a" * 64)
    selector = {"floor_selector": {"condition_family_ids": ["condition-a"],
                                   "metric": "gross_energy_j", "window_class": "request"}}
    request = FloorRequest(backend="mlx", metric="wrong_metric", window_class="request",
                           condition_family_id="condition-a", condition_family_sha256="b" * 64,
                           stack_identity_sha256="c" * 64, consumer_stress={})
    resolutions = _resolve_contrast_floor(inputs, selector, {},
                                          lambda *_: request)
    result["metric_selector_mismatch"] = {
        "inputs": {"selector": selector["floor_selector"], "request_metric": request.metric},
        "resolutions": [{"status": row.status, "reason_codes": list(row.reason_codes)}
                        for row in resolutions],
    }
    return result


def _issuance_gate() -> dict[str, object]:
    """Use the existing v1 window builder at the production issuance seam."""
    import base64
    from joulewise.analysis_engine import claim_side_bound
    from joulewise import analysis_manifest_v3
    from tests.test_analysis_integration import _v3_fixture_artifact
    from tests.test_paper_custody import RoundFiveTests

    artifact = _v3_fixture_artifact()
    artifact["evidence_class"] = "current"  # Existing custody test's v1 gate wire.
    manifest_path = ROOT / "configs/campaigns/splitwise_decode_v1/analysis_manifest_v3.json"
    manifest = json.loads(manifest_path.read_bytes())
    case = RoundFiveTests()
    ctx = case.context("claim_evidence")
    floor_raw = base64.b64decode(artifact["inputs"]["floor_artifact"]["embedded_bytes_base64"])
    ctx.raws[custody.InputRole.FLOOR_ARTIFACT] = floor_raw
    ctx.raws[custody.InputRole.FINALIZED_MANIFEST] = canonical_bytes(manifest)
    ctx.raws[custody.InputRole.CLAIM_SIDE_BOUND] = b"{}"
    ctx = dataclasses.replace(ctx, subjects=(artifact["contrasts"][0]["contrast_id"],))
    cases = {}
    for name, value in (("admitting_v1_wire", artifact),
                        ("invalid_verdict_wire", {**artifact, "claim_verdicts_id": "cv-invalid"})):
        ctx.raws[custody.InputRole.CLAIM_VERDICTS] = canonical_bytes(value)
        with mock.patch.object(claim_side_bound, "validate_claim_side_bound", return_value=[]), \
             mock.patch.object(analysis_manifest_v3, "validate_finalized_analysis_manifest_v3", return_value=[]), \
             mock.patch.object(custody, "_validate_floor_acceptance", return_value=None), \
             (mock.patch("joulewise.analysis_engine.artifact.validate_claim_verdicts", return_value=[])
              if name == "admitting_v1_wire" else nullcontext()):
            replay = custody._claim_issuance_gate(ctx)
        cases[name] = {"authentic": replay.authentic, "admitted": replay.admitted,
                       "validator_codes": [getattr(code, "reason_code", str(code))
                                           for code in replay.validator_codes],
                       "grants": [{"kind": grant.kind, "subject_id": grant.subject_id}
                                  for grant in replay.grants]}
    return {"manifest_id": artifact["inputs"]["analysis_manifest"]["manifest_id"],
            "subject": ctx.subjects[0], "scenarios": cases,
            "test_seams": ["finalized manifest validation", "sidecar validation", "floor acceptance",
                           "valid case verdict validation (existing custody v1 wire shape)"]}


def capture() -> dict[str, object]:
    pinned = json.loads(GOLDEN.read_bytes())
    selected = pinned.get("selected_paths") or sorted(
        set(pinned["claim_verdicts"])
        | set(pinned["validator_outcomes"]["manifests"])
        | set(pinned["validator_outcomes"]["registries"]))
    paths = [ROOT / rel for rel in selected]
    validators = _validators(paths)
    v1_ids = sorted({row["manifest_id"] for row in validators["manifests"].values()
                     if row["schema_version"] in {"joulewise.analysis_manifest.v1",
                                                  "joulewise.analysis_manifest.v3.finalized"}
                     and not row["validator_errors"] and row["manifest_id"]})
    return {"schema_version": "joulewise.claimgate_v1_replay_golden.v1",
            "selected_paths": selected,
            "selection_rules": {
                "selected_paths": "Pinned checked-in claim-verdict, manifest, and registry JSON paths selected for PR-0; discovery is informational only.",
                "v1_golden_manifest_ids": "Sorted manifest_id values from selected finalized v1 or v3.finalized manifests with no validator errors. No such checked-in finalized manifest exists at PR-0, so the list is empty; drafts and synthetic artifact IDs do not count.",
                "fixture_families": "Fixture authentication only; the non-issuing mode always refuses admission. No non-fixture replay is available from these checked-in fixture bytes; production issuance is sampled separately below.",
            },
            "v1_golden_manifest_ids": v1_ids,
            "fixture_families": _families(),
            "claim_matrix": _claim_matrix(),
            "claim_verdicts": _claim_artifacts(paths),
            "validator_outcomes": validators,
            "window_engine": _window_engine(),
            "issuance_gate": _issuance_gate(),
            "epoch_replays": _epoch_replays()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-dirty-for-tests", action="store_true")
    args = parser.parse_args()
    if not args.allow_dirty_for_tests:
        subprocess.run(["git", "rev-parse", "--verify", "origin/main"],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        committed = subprocess.run(["git", "diff", "--quiet", "origin/main", "HEAD", "--", "joulewise/"], cwd=ROOT)
        working = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "joulewise/"], cwd=ROOT)
        untracked = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard", "--", "joulewise/"], cwd=ROOT)
        if committed.returncode or working.returncode or untracked:
            raise SystemExit("refusing golden refresh: joulewise/ differs from origin/main")
    GOLDEN.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN.write_bytes(canonical_bytes(capture()))
    print(f"wrote {GOLDEN.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
