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
from concurrent.futures import ProcessPoolExecutor
import dataclasses
from contextlib import nullcontext
import base64
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
from joulewise.analysis_engine.claims import evaluate_claim, ordered_reason_codes
from joulewise.analysis_engine.multiplicity import adjust_p_values, holm_adjust
from joulewise.analysis_engine.registry import validate_analysis_manifest_v2, validate_analysis_registry_v2
from joulewise.analysis_manifest import validate_analysis_manifest, validate_analysis_registry
from joulewise.analysis_manifest_v3 import (
    validate_analysis_manifest_v3,
    validate_finalized_analysis_manifest_v3,
    validate_prospective_analysis_manifest_v3,
)
from scripts import epoch_equivalence_check as epoch

GOLDEN = ROOT / "tests/golden/claimgate_v1_replay.json"
CORPUS_BASES = ROOT / "tests/golden/claimgate_v1_corpus_bases"
SELECTED_PATHS = (
    "configs/analysis_registry/ap_spec_draft_front.v2.json",
    "configs/analysis_registry/ap_spec_native_mtp_front.v2.json",
    "configs/analysis_registry/slice_2m_ap2.v1.json",
    "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json",
    "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/analysis_manifest_v3.json",
    "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/analysis_manifest_v3.json",
    "configs/campaigns/splitwise_decode_v1/analysis_manifest_v3.json",
    "docs/paper/fill-rehearsal/dominance-not-reproduced-gamma-claim-verdicts.json",
    "docs/paper/fill-rehearsal/dominance-reproduced-gamma-claim-verdicts.json",
    "tests/fixtures/axi_ap_spec/analysis_manifest.json",
    "tests/fixtures/axi_ap_spec/draft_analysis_manifest.json",
    "tests/fixtures/axi_ap_spec/native_analysis_manifest.json",
)


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=1,
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


def _record(call, *args, **kwargs) -> dict[str, object]:
    try:
        return {"result": call(*args, **kwargs)}
    except Exception as exc:
        return {"raised": type(exc).__name__, "message": str(exc)}


def _corpus_batch(task) -> dict[str, list[str]]:
    name, raw, descriptors = task
    base = json.loads(raw)
    cases = {}
    for pointer, route, value in descriptors:
        operations = []
        if route:
            operations.append(("drop", None, True))
        if value is None:
            pass
        elif isinstance(value, bool):
            operations.extend((("null", None, False), ("wrong_type", "true", False)))
        elif isinstance(value, (int, float)):
            operations.extend((("null", None, False), ("wrong_type", "x", False),
                               ("nan", float("nan"), False)))
            if value != 0:
                operations.append(("sign_flip", -value, False))
            operations.append(("off_by_one", value + 1, False))
        elif isinstance(value, str):
            operations.extend((("null", None, False), ("wrong_type", 0, False),
                               ("off_by_one", value + "x", False), ("empty", "", False),
                               ("swap_enum", "__not_an_enum__", False)))
        elif isinstance(value, list):
            operations.extend((("null", None, False), ("wrong_type", {}, False),
                               ("empty", [], False)))
        elif isinstance(value, dict):
            operations.extend((("null", None, False), ("wrong_type", [], False),
                               ("empty", {}, False)))
        for op, replacement, drop in operations:
            if not drop and replacement == value:
                continue
            candidate = copy.deepcopy(base)
            if route:
                parent = candidate
                for step in route[:-1]:
                    parent = parent[step]
                if drop:
                    del parent[route[-1]]
                else:
                    parent[route[-1]] = replacement
            else:
                candidate = replacement
            cases[f"{name}|{pointer}|{op}"] = _errors(validate_claim_verdicts, candidate)
    return cases


def _validator_corpus() -> dict[str, object]:
    """Enumerate deterministic mutations of the two tracked, clean bases."""
    cases: dict[str, list[str]] = {}
    bases: dict[str, str] = {}
    def pointer_part(part: object) -> str:
        return str(part).replace("~", "~0").replace("/", "~1")
    def nodes(value, pointer="", route=()):
        yield pointer, route, value
        if isinstance(value, dict):
            for key in sorted(value):
                yield from nodes(value[key], pointer + "/" + pointer_part(key), route + (key,))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                yield from nodes(item, pointer + "/" + str(index), route + (index,))
    tasks = []
    for name in ("gate_fixture", "minimal"):
        raw = (CORPUS_BASES / f"{name}.json").read_bytes()
        bases[name] = _blob_sha(raw)
        base = json.loads(raw)
        descriptors = list(nodes(base))
        for start in range(0, len(descriptors), 250):
            tasks.append((name, raw, descriptors[start:start + 250]))
    with ProcessPoolExecutor(max_workers=8) as pool:
        for batch in pool.map(_corpus_batch, tasks):
            cases.update(batch)
    return {"bases": bases, "spec_version": 1, "case_count": len(cases), "cases": cases}


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
    invalid = json.loads((ROOT / sources["s9-pass"]).read_bytes())
    retained = copy.deepcopy(invalid["retained"])
    retained[0]["b_fiducial_s"] = "invalid-decimal"
    session = SimpleNamespace(**invalid["session"])
    with mock.patch.object(epoch, "_slot_outcomes", return_value=(invalid["slot_outcomes"], retained)):
        try:
            epoch.evaluate_session(session, session.session_id, invalid["reference_envelope"])
        except Exception as exc:
            result["invalid_decimal"] = {"raised": type(exc).__name__}
        else:
            result["invalid_decimal"] = {"raised": None}
    minimum_retained = copy.deepcopy(invalid["retained"][:epoch.MINIMUM_RETAINED_M])
    with mock.patch.object(epoch, "_slot_outcomes", return_value=(invalid["slot_outcomes"], minimum_retained)):
        result["at_minimum_m"] = _record(epoch.evaluate_session, session, session.session_id,
                                          invalid["reference_envelope"])
    edge = copy.deepcopy(invalid)
    values = [epoch.Decimal(item["b_fiducial_s"]) for item in edge["retained"]]
    edge["reference_envelope"]["bracket_screen_s"] = str(max(values) - min(values))
    with mock.patch.object(epoch, "_slot_outcomes", return_value=(edge["slot_outcomes"], edge["retained"])):
        result["bracket_at_edge"] = _record(epoch.evaluate_session, session, session.session_id,
                                             edge["reference_envelope"])
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
        "direction_negative": {"estimate": -2.0,
                               "metrology_aware_ci95": {"lower": -2.5, "upper": -1.5},
                               "decision_interval": {"lower": -2.75, "upper": -1.25}},
        "direction_below_floor": {"estimate": 0.5},
        "multiplicity_not_rejected": {"adjusted_rejected": False},
        "legacy_l1": {"evidence_class": "legacy_l1"},
        "non_confirmatory": {"confirmatory_status": "exploratory"},
        "sensitivity_blocking": {"sensitivity_blocking": True},
        "direction_mismatch": {"hypothesized_direction": "negative"},
        "floor_none": {"floor_gate_j": None},
        "floor_zero": {"floor_gate_j": 0.0},
        "floor_negative": {"floor_gate_j": -1.0},
        "metrology_straddles_zero": {"metrology_aware_ci95": {"lower": -0.1, "upper": 2.5}},
        "metrology_bad_lower": {"metrology_aware_ci95": {"lower": "invalid", "upper": 2.5}},
        "metrology_lower_zero": {"metrology_aware_ci95": {"lower": 0.0, "upper": 2.5}},
        "metrology_upper_zero": {"estimate": -2.0, "metrology_aware_ci95": {"lower": -2.5, "upper": 0.0},
                                 "decision_interval": {"lower": -2.75, "upper": -1.25}},
        "decision_lower_zero": {"decision_interval": {"lower": 0.0, "upper": 2.75}},
        "decision_upper_zero": {"estimate": -2.0, "metrology_aware_ci95": {"lower": -2.5, "upper": -1.5},
                                "decision_interval": {"lower": -2.75, "upper": 0.0}},
        "decision_lower_zero_metrology_clear": {"decision_interval": {"lower": 0.0, "upper": 2.75}},
        "decision_upper_zero_metrology_clear": {"estimate": -2.0,
                                                 "metrology_aware_ci95": {"lower": -2.5, "upper": -1.5},
                                                 "decision_interval": {"lower": -2.75, "upper": 0.0}},
        "decision_straddles_zero_metrology_clear": {"decision_interval": {"lower": -0.1, "upper": 2.75}},
        "decision_straddles_metrology_negative": {
            "metrology_aware_ci95": {"lower": -2.5, "upper": -1.5},
            "decision_interval": {"lower": -0.1, "upper": 2.75}},
        "valid_floor_metadata": {"floor_metadata": valid_metadata},
        "invalid_floor_metadata": {"floor_metadata": {**valid_metadata, "floor_source": "wrong"}},
        "floor_metadata_bad_discipline": {"floor_metadata": {**valid_metadata, "single_count_discipline": {}}},
        "floor_metadata_not_mapping": {"floor_metadata": "invalid"},
        "floor_metadata_missing_key": {"floor_metadata": {"floor_source": ATTRIBUTION_FLOOR_SOURCE}},
        "floor_metadata_keys_as_list": {"floor_metadata": list(valid_metadata)},
        "floor_metadata_extra_key": {"floor_metadata": {**valid_metadata, "extra": True}},
        "floor_metadata_bad_limit": {"floor_metadata": {**valid_metadata, "floor_limit_class": "wrong"}},
        "floor_metadata_bad_point": {"floor_metadata": {**valid_metadata, "point_floor_diagnostics": "invalid"}},
        "interval_inverted": {"decision_interval": {"lower": 3.0, "upper": 2.0}},
        "interval_bad_lower": {"decision_interval": {"lower": "invalid", "upper": 2.0}},
        "interval_bad_upper": {"decision_interval": {"lower": 1.0, "upper": "invalid"}},
        "estimate_bool": {"estimate": True},
        "base_not_resolvable": {"base_reason_codes": ["floor_row_missing"]},
        "base_reason_not_resolvable": {"base_reason_codes": ["floor_row_missing"]},
        "base_unresolved": {"base_reason_codes": ["multiplicity_not_rejected"]},
        "base_sensitivity": {"base_reason_codes": ["randomization_sensitivity_disagrees"]},
        "claim_role_other": {"claim_role": "exploratory"},
        "equivalence_margin_at_floor_inside": {"equivalence": {"method": "tost_v1", "margin": 1.0}, "metrology_aware_ci95": {"lower": -0.5, "upper": 0.5}, "decision_interval": {"lower": -0.75, "upper": 0.75}},
        "equivalence_present_below_floor": {"estimate": 0.5, "equivalence": {"method": "tost_v1", "margin": 3.0}},
        "equivalence_margin_at_floor_outside": {"equivalence": {"method": "tost_v1", "margin": 1.0}},
        "equivalence_margin_above_floor_inside": {"equivalence": {"method": "tost_v1", "margin": 3.0}},
        "equivalence_registered_direction": {"equivalence": {"method": "tost_v1", "margin": 3.0},
                                             "hypothesized_direction": "positive"},
        "equivalence_margin_above_floor_outside": {"equivalence": {"method": "tost_v1", "margin": 1.5}},
        "equivalence_lower_outside": {"equivalence": {"method": "tost_v1", "margin": 3.0},
                                      "metrology_aware_ci95": {"lower": -3.0, "upper": 1.0}},
        "equivalence_bad_method": {"equivalence": {"method": "other", "margin": 3.0}},
        "equivalence_zero_margin": {"equivalence": {"method": "tost_v1", "margin": 0.0}},
        "equivalence_no_margin": {"equivalence": {"method": "tost_v1"}},
        "equivalence_not_mapping": {"equivalence": "invalid"},
        "equivalence_inside_not_rejected": {"equivalence": {"method": "tost_v1", "margin": 3.0}, "adjusted_rejected": False},
        "equivalence_edge_at_margin": {"equivalence": {"method": "tost_v1", "margin": 2.75}},
    }
    result = {name: {"inputs": arguments, "output": evaluate_claim(**arguments)}
            for name, override in cases.items()
            for arguments in [{**base, **override}]}
    for name in ("floor_metadata_keys_as_list", "floor_metadata_extra_key",
                 "base_reason_not_resolvable", "equivalence_present_below_floor",
                 "metrology_lower_zero", "metrology_upper_zero", "decision_lower_zero",
                 "decision_upper_zero", "decision_lower_zero_metrology_clear",
                 "decision_upper_zero_metrology_clear"):
        result[name] = _record(evaluate_claim, **{**base, **cases[name]})
    result["ordered_reason_codes"] = {"unknown_code": _record(ordered_reason_codes, ["not_a_code"])}
    multiplicity_cases = {
        "holm_valid": ({"a": .01, "b": .04, "c": .03}, "holm", 3, .05, None),
        "bh_valid": ({"a": .01, "b": .04, "c": .03}, "benjamini_hochberg", 3, None, .05),
        "bh_clamp": ({"a": .6, "b": .7}, "benjamini_hochberg", 2, None, .05),
        "exploratory_valid": ({"a": .01}, "exploratory_none", 1, None, None),
        "holm_at_threshold": ({"a": .05}, "holm", 1, .05, None),
        "bh_at_threshold": ({"a": .05}, "benjamini_hochberg", 1, None, .05),
        "unsupported_method": ({"a": .01}, "unknown", 1, .05, None),
        "holm_with_q": ({"a": .01}, "holm", 1, .05, .05),
        "bh_with_alpha": ({"a": .01}, "benjamini_hochberg", 1, .05, .05),
        "exploratory_with_alpha": ({"a": .01}, "exploratory_none", 1, .05, None),
        "m_zero": ({"a": .01}, "holm", 0, .05, None),
        "m_bool": ({"a": .01}, "holm", True, .05, None),
        "m_mismatch": ({"a": .01}, "holm", 2, .05, None),
        "p_values_not_mapping": ([.01], "holm", 1, .05, None),
        "contrast_id_empty": ({"": .01}, "holm", 1, .05, None),
        "contrast_id_not_str": ({1: .01}, "holm", 1, .05, None),
        "p_str": ({"a": ".01"}, "holm", 1, .05, None),
        "p_bool": ({"a": True}, "holm", 1, .05, None),
        "p_above_one": ({"a": 1.01}, "holm", 1, .05, None),
        "p_nan": ({"a": float("nan")}, "holm", 1, .05, None),
        "p_negative": ({"a": -.01}, "holm", 1, .05, None),
        "threshold_zero": ({"a": .01}, "holm", 1, 0, None),
        "threshold_above_one": ({"a": .01}, "holm", 1, 1.01, None),
        "threshold_str": ({"a": .01}, "holm", 1, "0.05", None),
        "threshold_bool": ({"a": .01}, "holm", 1, True, None),
        "threshold_nan": ({"a": .01}, "holm", 1, float("nan"), None),
    }
    result["multiplicity"] = {
        name: _record(adjust_p_values, values, method=method, m=m, alpha=alpha, q=q)
        for name, (values, method, m, alpha, q) in multiplicity_cases.items()
    }
    result["holm_adjust"] = {}
    from joulewise.analysis_engine.claims import _finite
    result["finite_nonfinite"] = {"input": "Infinity", "output": _finite(float("inf"))}
    for name, values, m in (
        ("three_complete", {"a": .01, "b": .04, "c": .03}, 3),
        ("two_for_three_refused", {"a": .6, "b": .7}, 3),
        ("above_one_clamp", {"a": .6, "b": .7, "c": None}, 3),
        ("one_missing", {"a": .02, "b": None}, 2),
    ):
        try:
            outcome = {"adjusted": holm_adjust(values, m=m)}
        except Exception as exc:
            outcome = {"raised": type(exc).__name__}
        result["holm_adjust"][name] = {"p_values": values, "m": m, **outcome}
    return result


def _window_engine() -> dict[str, object]:
    """Replay the existing v1 artifact and v3 window test builders."""
    from joulewise.analysis_engine import _resolve_contrast_floor
    from joulewise.analysis_engine.inputs import FloorEvidenceBinding, FloorRequest, LoadedAnalysisInputs
    from tests.test_analysis_claims import minimal_artifact
    from tests.test_analysis_integration import _v3_fixture_artifact

    scenarios = {"minimal_v1_artifact": minimal_artifact()}
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
    from tests.test_analysis_integration import make_artifact
    floor = make_artifact()
    binding = FloorEvidenceBinding(frozenset(), {}, {}, frozenset(), {}, ())
    manifest = json.loads((ROOT / "configs/campaigns/splitwise_decode_v1/analysis_manifest_v3.json").read_bytes())
    inputs = LoadedAnalysisInputs(
        manifest=manifest, manifest_sha256="b" * 64, floor_artifact=floor,
        floor_sha256="a" * 64, registered={}, effective={}, extra_audits=(),
        valid_replacements=(), unregistered_matching=(), top_up_entry_ids=frozenset())
    selector = {"floor_selector": {"condition_family_ids": ["condition-a"],
                                   "metric": "gross_energy_j", "window_class": "request"}}
    def resolved(current_inputs, factory, included=None, seam=None):
        try:
            context = (mock.patch("joulewise.analysis_engine._floor_request_or_refusal", return_value=seam)
                       if seam is not None else nullcontext())
            with context:
                resolutions = _resolve_contrast_floor(current_inputs, selector, included or {}, factory)
            return [{"status": row.status, "reason_codes": list(row.reason_codes)} for row in resolutions]
        except Exception as exc:
            return {"raised": type(exc).__name__}
    matching = FloorRequest(backend="mlx", metric="gross_energy_j", window_class="request",
                            condition_family_id="condition-a", condition_family_sha256="b" * 64,
                            stack_identity_sha256="c" * 64, consumer_stress={})
    v1_inputs = SimpleNamespace(manifest={"schema_version": "joulewise.analysis_manifest.v1",
                                "arms": ["malformed"]}, floor_artifact=floor,
                                floor_binding=binding, floor_sha256="a" * 64)
    faulty_binding = dataclasses.replace(binding, global_problems=("calibration_plan_bytes_hash_mismatch",))
    faulty_inputs = SimpleNamespace(manifest=manifest, floor_artifact=floor,
                                    floor_binding=faulty_binding, floor_sha256="a" * 64)
    empty_inputs = SimpleNamespace(manifest=manifest, floor_artifact=floor,
                                   floor_binding=binding, floor_sha256="a" * 64)
    cell_binding = dataclasses.replace(binding, problems_by_cell={"cell-1": ("calibration_plan_bytes_hash_mismatch",)})
    cell_inputs = SimpleNamespace(manifest=manifest, floor_artifact=floor,
                                  floor_binding=cell_binding, floor_sha256="a" * 64)
    matching_manifest = copy.deepcopy(manifest)
    matching_manifest["arms"].append({"condition_family_id": "condition-a",
                                      "condition_family_sha256": "b" * 64})
    matching_inputs = SimpleNamespace(manifest=matching_manifest, floor_artifact=floor,
                                      floor_binding=binding, floor_sha256="a" * 64)
    result["floor_request_refusal"] = {
        "no_request": resolved(inputs, None),
        "empty_binding": resolved(empty_inputs, None),
        "bad_binding": resolved(faulty_inputs, None),
        "bad_cell_binding": resolved(cell_inputs, None),
        "no_factory_with_evidence": resolved(inputs, None, {"condition-a": [SimpleNamespace(raw_config={})]}),
        "request_refused": resolved(inputs, None, seam=("consumer_identity_undeclared",)),
        "production_request": resolved(matching_inputs, None, seam=matching),
        "factory_none": resolved(inputs, lambda *_: None),
        "metric_mismatch": resolved(inputs, lambda *_: dataclasses.replace(matching, metric="wrong")),
        "window_mismatch": resolved(inputs, lambda *_: dataclasses.replace(matching, window_class="wrong")),
        "condition_mismatch": resolved(inputs, lambda *_: dataclasses.replace(matching, condition_family_id="wrong")),
        "hash_mismatch": resolved(inputs, lambda *_: matching),
        "v3_match": resolved(matching_inputs, lambda *_: matching),
        "v1_match": resolved(v1_inputs, lambda *_: matching),
    }
    malformed_inputs = dataclasses.replace(inputs, floor_artifact={**floor, "cells": [None, {"cell_id": 7}]})
    result["request_window_class_mismatch"] = _record(
        resolved, matching_inputs, lambda *_: dataclasses.replace(matching, window_class="wrong"))
    result["request_condition_mismatch"] = _record(
        resolved, matching_inputs, lambda *_: dataclasses.replace(matching, condition_family_id="wrong"))
    result["binding_seam_differs"] = _record(
        resolved, matching_inputs, lambda *_: matching,
        seam=dataclasses.replace(matching, condition_family_id="wrong"))
    result["malformed_cells"] = _record(resolved, malformed_inputs, lambda *_: matching)
    return result


def _claim_gate_context(artifact: dict, manifest: dict, floor: dict, sidecar: bytes) -> custody._GateContext:
    supply = json.loads((ROOT / "configs/paper_supply/supply_map.json").read_bytes())
    role = "fixture.claim_evidence"
    sources = tuple(custody._BoundFile(
        row["base"], Path(row["path"]), row["expected_sha256"],
        custody.InputRole(row["role"]), row["authority"])
        for row in supply["roles"][role]["inputs"])
    raws = {
        custody.InputRole.CLAIM_VERDICTS: canonical_bytes(artifact),
        custody.InputRole.CLAIM_SIDE_BOUND: sidecar,
        custody.InputRole.FINALIZED_MANIFEST: canonical_bytes(manifest),
        custody.InputRole.FLOOR_ARTIFACT: base64.b64decode(
            artifact["inputs"]["floor_artifact"]["embedded_bytes_base64"]),
    }
    return custody._GateContext("claim_evidence", role, "production", "claim-evidence.v1",
                                (artifact["contrasts"][0]["contrast_id"],), ROOT, ROOT, "",
                                sources, (), raws, None)


def _replay_record(replay: custody._FamilyReplay) -> dict[str, object]:
    return {"authentic": replay.authentic, "admitted": replay.admitted,
            "validator_codes": [getattr(code, "reason_code", str(code)) for code in replay.validator_codes],
            "grants": [{"kind": grant.kind, "subject_id": grant.subject_id} for grant in replay.grants]}


def _gate_fixture() -> tuple[dict, dict, dict, bytes]:
    from joulewise.analysis_engine import claim_side_bound
    from tests.test_analysis_integration import _v3_fixture_artifact

    artifact = _v3_fixture_artifact()
    # The integration builder's synthetic resolution names are not cells in
    # its embedded floor. Bind the synthetic row to the embedded cell so the
    # production sidecar validator can execute without a seam.
    for contrast in artifact["contrasts"]:
        for resolution in contrast["floor"]["resolutions"]:
            resolution["source_cell_ids"] = ["cell-1"]
        contrast["floor"]["floor_row_ids"] = ["cell-1"]
    from joulewise.analysis_engine.artifact import calculate_claim_verdicts_id
    artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
    manifest = json.loads((ROOT / "configs/campaigns/splitwise_decode_v1/analysis_manifest_v3.json").read_bytes())
    floor = json.loads(base64.b64decode(artifact["inputs"]["floor_artifact"]["embedded_bytes_base64"]))
    raw = canonical_bytes(artifact)
    sidecar = claim_side_bound.produce_claim_side_bound(raw, finalized_manifest=manifest, floor_artifact=floor)
    return artifact, manifest, floor, sidecar


def _issuance_gate() -> dict[str, object]:
    """Pin the real v1 wire at the production replay boundary."""
    from joulewise.analysis_engine import claim_side_bound
    from joulewise import analysis_manifest_v3
    artifact, manifest, floor, sidecar = _gate_fixture()
    ctx = _claim_gate_context(artifact, manifest, floor, sidecar)
    seams = (mock.patch.object(analysis_manifest_v3, "validate_finalized_analysis_manifest_v3", return_value=[]),
             mock.patch.object(custody, "_validate_floor_acceptance", return_value=None))
    with seams[0], seams[1]:
        replay = custody._replay_family(ctx)
        try:
            custody._claim_issuance_gate(ctx)
        except KeyError as exc:
            direct = {"raised": "KeyError", "key": str(exc.args[0])}
        else:
            direct = {"raised": None}
        shim = copy.deepcopy(artifact)
        shim["evidence_class"] = shim["inputs"]["evidence_class"]
        shimsidecar = claim_side_bound.produce_claim_side_bound(
            canonical_bytes(shim), finalized_manifest=manifest, floor_artifact=floor)
        shimctx = _claim_gate_context(shim, manifest, floor, shimsidecar)
        with mock.patch("joulewise.analysis_engine.artifact.validate_claim_verdicts", return_value=[]):
            admitted = custody._replay_family(shimctx)
    return {"pre": {**_replay_record(replay), "direct_call": direct},
            "post": {**_replay_record(admitted),
                     "shim": "top-level evidence_class copied from inputs.evidence_class; validate_claim_verdicts patched to []"}}


def _issuance_wire_refusals() -> dict[str, dict[str, object]]:
    """Pin three real-wire refusals before the v1 evidence-class defect."""
    from joulewise import analysis_manifest_v3

    expected = {
        "floor_anchor_mismatch_wire": {
            "admitted": False, "authentic": False, "grants": [],
            "validator_codes": ["claim_floor_anchor_mismatch"],
        },
        "binding_mismatch_wire": {
            "raised": "PaperCustodyRefusal", "message": "paper_custody_binding_mismatch",
        },
        "empty_subjects_wire": {
            "raised": "PaperCustodyRefusal", "message": "paper_custody_binding_mismatch",
        },
    }
    result = {}
    for name in expected:
        artifact, manifest, floor, sidecar = _gate_fixture()
        ctx = _claim_gate_context(artifact, manifest, floor, sidecar)
        if name == "floor_anchor_mismatch_wire":
            raws = dict(ctx.raws)
            raws[custody.InputRole.FLOOR_ARTIFACT] += b"\n"
            ctx = dataclasses.replace(ctx, raws=raws)
        elif name == "binding_mismatch_wire":
            ctx = dataclasses.replace(ctx, subjects=("not-a-contrast",))
        else:
            ctx = dataclasses.replace(ctx, subjects=())
        with mock.patch.object(analysis_manifest_v3, "validate_finalized_analysis_manifest_v3", return_value=[]), \
             mock.patch.object(custody, "_validate_floor_acceptance", return_value=None):
            try:
                record = _replay_record(custody._replay_family(ctx))
            except Exception as exc:
                record = {"raised": type(exc).__name__, "message": str(exc)}
        if record != expected[name]:
            raise RuntimeError(f"{name} protocol failure: {record!r}")
        result[name] = {"pre": record, "post": record}
    return result


def _invalid_issuance_gate() -> dict[str, object]:
    from joulewise.analysis_engine import claim_side_bound
    from joulewise import analysis_manifest_v3
    artifact, manifest, floor, _ = _gate_fixture()
    artifact["claim_verdicts_id"] = "cv-invalid"
    raw = canonical_bytes(artifact)
    sidecar = claim_side_bound.produce_claim_side_bound(raw, finalized_manifest=manifest,
                                                       floor_artifact=floor)
    ctx = _claim_gate_context(artifact, manifest, floor, sidecar)
    with mock.patch.object(analysis_manifest_v3, "validate_finalized_analysis_manifest_v3", return_value=[]), \
         mock.patch.object(custody, "_validate_floor_acceptance", return_value=None):
        return _replay_record(custody._replay_family(ctx))


def _claim_side_bound() -> dict[str, object]:
    from joulewise.analysis_engine.claim_side_bound import (
        produce_claim_side_bound, validate_claim_side_bound,
    )
    from tests.test_analysis_integration import _v3_fixture_artifact
    artifact = _v3_fixture_artifact()
    manifest = json.loads((ROOT / "configs/campaigns/splitwise_decode_v1/analysis_manifest_v3.json").read_bytes())
    floor = json.loads(base64.b64decode(artifact["inputs"]["floor_artifact"]["embedded_bytes_base64"]))
    raw = canonical_bytes(artifact)
    try:
        sidecar = produce_claim_side_bound(raw, finalized_manifest=manifest, floor_artifact=floor)
        codes = validate_claim_side_bound(sidecar, claim_verdicts_raw=raw,
                                          finalized_manifest=manifest, floor_artifact=floor)
        return {"sha256": hashlib.sha256(sidecar).hexdigest(), "validator_codes": list(codes)}
    except Exception as exc:
        return {"raised": type(exc).__name__}


def _window_transitions() -> dict[str, object]:
    from tests.test_analysis_integration import _v3_fixture_artifact
    result = {}
    for name, artifact in (("v3_window_clean", _v3_fixture_artifact()),
                           ("v3_window_supersession_diverged", _v3_fixture_artifact(diverged=True))):
        for row in artifact["contrasts"]:
            evaluation = row["claim_evaluation"]
            pre = {"manifest_id": artifact["inputs"]["analysis_manifest"]["manifest_id"],
                   "validator_errors": validate_claim_verdicts(artifact),
                   "claim_evaluation": evaluation}
            post = {"claim_evaluation": {**evaluation,
                                         "claim_ready_for_l2_l3": False,
                                         "claim_level_ceiling": "L1"},
                    "reason_codes_added": ["claim_rule_version_v1_closed"]}
            result[name] = {"pre": pre, "post": post}
    return result


def capture() -> dict[str, object]:
    selected = list(SELECTED_PATHS)
    paths = [ROOT / rel for rel in selected]
    validators = _validators(paths)
    v1_ids = sorted({row["manifest_id"] for row in validators["manifests"].values()
                     if row["schema_version"] in {"joulewise.analysis_manifest.v1",
                                                  "joulewise.analysis_manifest.v3.finalized"}
                     and not row["validator_errors"] and row["manifest_id"]})
    issuance = _issuance_gate()
    verdicts = _claim_artifacts(paths)
    verdicts["invalid_verdict_wire"] = _invalid_issuance_gate()
    return {"schema_version": "joulewise.claimgate_v1_replay_golden.v3",
            "selected_paths": selected,
            "selection_rules": {
                "selected_paths": "Pinned checked-in claim-verdict, manifest, and registry JSON paths selected for PR-0; discovery is informational only.",
                "v1_golden_manifest_ids": "Sorted manifest_id values from selected finalized v1 or v3.finalized manifests with no validator errors. No such checked-in finalized manifest exists at PR-0, so the list is empty; drafts and synthetic artifact IDs do not count.",
                "fixture_families": "Fixture authentication only; the non-issuing mode always refuses admission. Production issuance is sampled by the real_v1_wire transition.",
                "test_seams": ["validate_finalized_analysis_manifest_v3 → []", "_validate_floor_acceptance → None"],
            },
            "v1_golden_manifest_ids": v1_ids,
            "invariant": {
                "fixture_families": _families(),
                "claim_matrix": _claim_matrix(),
                "claim_verdicts": verdicts,
                "validator_outcomes": validators,
                "window_engine": _window_engine(),
                "claim_side_bound": _claim_side_bound(),
                "epoch_replays": _epoch_replays(),
                "validator_corpus": _validator_corpus(),
            },
            "transitions": {"WR-6": _window_transitions(),
                            "V1-ISSUANCE-GATE-EVIDENCE-CLASS-01": {
                                "real_v1_wire": issuance,
                                **_issuance_wire_refusals()}}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-corpus-bases", action="store_true")
    args = parser.parse_args()
    if subprocess.run(["git", "rev-parse", "--verify", "origin/main"], cwd=ROOT,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        print("refusing golden refresh: origin/main absent", file=sys.stderr)
        raise SystemExit(2)
    protected = ("joulewise/", "scripts/epoch_equivalence_check.py")
    committed = subprocess.run(["git", "diff", "--quiet", "origin/main", "HEAD", "--", *protected], cwd=ROOT)
    working = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *protected], cwd=ROOT)
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "--", *protected], cwd=ROOT)
    if committed.returncode or working.returncode or untracked:
        raise SystemExit("refusing golden refresh: decision source differs from origin/main")
    if args.write_corpus_bases:
        from tests.test_analysis_claims import minimal_artifact
        values = {"gate_fixture": _gate_fixture()[0], "minimal": minimal_artifact()}
        for name, value in values.items():
            errors = validate_claim_verdicts(value)
            if errors:
                raise SystemExit(f"refusing corpus base {name}: {errors}")
        CORPUS_BASES.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (CORPUS_BASES / f"{name}.json").write_bytes(canonical_bytes(value))
        print(f"wrote {CORPUS_BASES.relative_to(ROOT)}")
    else:
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_bytes(canonical_bytes(capture()))
        print(f"wrote {GOLDEN.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
