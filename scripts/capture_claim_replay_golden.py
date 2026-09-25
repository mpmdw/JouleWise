#!/usr/bin/env python3
"""Capture the checked-in v1 claim and validator decisions before CG-4.

Refresh the resulting blob only in a reviewed PR, together with its test pin.
The 09-19 source records contain authenticated slot outcomes; their underlying
measurement bundles are outside this repository.  Replay the public decision
function from those recorded outcomes, without claiming to reauthenticate them.
"""

from __future__ import annotations

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
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
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
        return [getattr(item, "reason_code", getattr(item, "code", str(item)))
                for item in result] if result is not None else []
    except (ValueError, TypeError) as exc:
        return [f"{type(exc).__name__}: {exc}"]
    except Exception as exc:
        # Admission validators use typed refusal exceptions, not one common base.
        return [f"{type(exc).__name__}: {getattr(exc, 'code', str(exc))}"]


def _families() -> dict[str, object]:
    supply = json.loads((ROOT / "configs/paper_supply/supply_map.json").read_text())
    result = {}
    for role, entry in sorted(supply["roles"].items()):
        if not role.startswith("fixture."):
            continue
        family = role.removeprefix("fixture.")
        sources = tuple(custody._BoundFile(
            row["base"], Path(row["path"]), row["expected_sha256"],
            custody.InputRole(row["role"]), row["authority"])
            for row in entry["inputs"])
        raws = {binding.role: canonical_bytes({
            "family": family, "marker": "synthetic-no-measurement-value",
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
        result[rel] = {
            "file_sha256": _sha(path),
            "manifest_id": artifact["inputs"]["analysis_manifest"]["manifest_id"],
            "validator_errors": validate_claim_verdicts(artifact),
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
    return result


def capture() -> dict[str, object]:
    paths = _tracked_json()
    return {"schema_version": "joulewise.claimgate_v1_replay_golden.v1",
            "fixture_families": _families(),
            "claim_verdicts": _claim_artifacts(paths),
            "validator_outcomes": _validators(paths),
            "epoch_replays": _epoch_replays()}


def main() -> None:
    GOLDEN.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN.write_bytes(canonical_bytes(capture()))
    print(f"wrote {GOLDEN.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
