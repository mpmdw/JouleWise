"""Pure P2-046A load-transition alignment analysis.

This module only analyzes frozen observations.  It never launches a sampler,
generates load, or adjudicates a physical Mac bound.  Fixture artifacts are
``PROVISIONAL_FIXTURE_ONLY``; later Part-B artifacts remain
``PROVISIONAL_REAL_MAC_UNADJUDICATED`` until lead review.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


MANIFEST_SCHEMA_VERSION = "joulewise.load_transition_manifest.v1"
OBSERVATIONS_SCHEMA_VERSION = "joulewise.load_transition_observations.v1"
ARTIFACT_SCHEMA_VERSION = "joulewise.load_transition_alignment_artifact.v1"
EVIDENCE_STATUS = "PROVISIONAL_FIXTURE_ONLY"
MANIFEST_STATUS = "PROVISIONAL_PRE_EXECUTION"
REAL_MAC_STATUS = "PROVISIONAL_REAL_MAC_UNADJUDICATED"
OBSERVATION_STATUSES = (EVIDENCE_STATUS, REAL_MAC_STATUS)
METHOD_ID = "plateau_midpoint_sample_support.v1"
ARTIFACT_HASH_DOMAIN = "joulewise.load_transition_alignment_artifact.v1"
DIRECTIONS = ("idle_to_load", "load_to_idle")

__all__ = [
    "AlignmentRefusal",
    "ARTIFACT_SCHEMA_VERSION",
    "EVIDENCE_STATUS",
    "MANIFEST_SCHEMA_VERSION",
    "METHOD_ID",
    "OBSERVATIONS_SCHEMA_VERSION",
    "build_alignment_artifact",
    "canonical_sha256",
    "render_artifact",
    "validate_alignment_artifact",
    "write_artifact_atomic",
]


class AlignmentRefusal(ValueError):
    """Fail-closed input or artifact refusal with a stable reason code."""

    def __init__(self, reason_code: str, detail: str):
        super().__init__(detail)
        self.reason_code = reason_code


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise AlignmentRefusal("input_not_canonical_json", str(exc)) from exc


def canonical_sha256(value: Mapping[str, Any]) -> str:
    """Return a deterministic canonical-JSON SHA-256 for provenance."""

    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _artifact_id(value_without_id: Mapping[str, Any]) -> str:
    payload = ARTIFACT_HASH_DOMAIN.encode("utf-8") + b"\0" + _canonical_bytes(value_without_id)
    return "lta-" + hashlib.sha256(payload).hexdigest()


def _require_exact_keys(
    value: Mapping[str, Any], expected: set[str], label: str, reason: str
) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise AlignmentRefusal(reason, f"{label} keys differ: missing={missing}, extra={extra}")


def _finite_number(value: Any, label: str, reason: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AlignmentRefusal(reason, f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise AlignmentRefusal(reason, f"{label} must be a finite number")
    return result


def _positive_int(value: Any, label: str, reason: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise AlignmentRefusal(reason, f"{label} must be a positive integer")
    return value


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return value == value.lower()


def _validate_manifest(manifest: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    reason = "manifest_schema_invalid"
    _require_exact_keys(
        manifest,
        {
            "schema_version",
            "manifest_id",
            "freeze_status",
            "evidence_status",
            "scope",
            "analysis",
            "execution_plan",
            "refusal_policy",
        },
        "manifest",
        reason,
    )
    if manifest["schema_version"] != MANIFEST_SCHEMA_VERSION:
        raise AlignmentRefusal(reason, "unsupported manifest schema_version")
    if not isinstance(manifest["manifest_id"], str) or not manifest["manifest_id"]:
        raise AlignmentRefusal(reason, "manifest_id must be a non-empty string")
    if manifest["freeze_status"] != "frozen_pre_execution":
        raise AlignmentRefusal(reason, "freeze_status must be frozen_pre_execution")
    if manifest["evidence_status"] != MANIFEST_STATUS:
        raise AlignmentRefusal(reason, f"evidence_status must be {MANIFEST_STATUS}")
    if not isinstance(manifest["scope"], Mapping):
        raise AlignmentRefusal(reason, "scope must be an object")
    _require_exact_keys(
        manifest["scope"],
        {"part", "lane", "physical_claims_allowed", "quiet_mac_execution_status"},
        "manifest.scope",
        reason,
    )
    if manifest["scope"] != {
        "part": "P2-046A_PREP_FOR_P2-046B",
        "lane": "A_AGENT_B_QUIET_MAC",
        "physical_claims_allowed": False,
        "quiet_mac_execution_status": "NOT_EXECUTED_REQUIRES_LEAD_CONTROLLED_QUIET_MAC",
    }:
        raise AlignmentRefusal(reason, "scope does not preserve the P2-046A fixture-only boundary")

    analysis = manifest["analysis"]
    if not isinstance(analysis, Mapping):
        raise AlignmentRefusal(reason, "analysis must be an object")
    _require_exact_keys(
        analysis,
        {
            "method_id",
            "target_threshold_rule",
            "plateau_definition",
            "minimum_plateau_samples_per_state",
            "required_consecutive_target_samples",
            "offset_definition",
            "center_definition",
            "residual_definition",
            "conservative_bound_definition",
            "minimum_transitions_per_direction",
        },
        "manifest.analysis",
        reason,
    )
    if analysis["method_id"] != METHOD_ID:
        raise AlignmentRefusal(reason, "analysis.method_id is unsupported")
    if analysis["target_threshold_rule"] != "midpoint(low_plateau_w,high_plateau_w)":
        raise AlignmentRefusal(reason, "analysis target threshold rule is unsupported")
    if analysis["plateau_definition"] != "median_of_declared_stable_state_samples":
        raise AlignmentRefusal(reason, "analysis plateau definition is unsupported")
    minimum_plateau_samples = _positive_int(
        analysis["minimum_plateau_samples_per_state"],
        "analysis.minimum_plateau_samples_per_state",
        reason,
    )
    if minimum_plateau_samples < 2:
        raise AlignmentRefusal(reason, "at least two plateau samples per state are required")
    if analysis["offset_definition"] != "response_sample_midpoint_s-marker_epoch_s":
        raise AlignmentRefusal(reason, "analysis offset definition is unsupported")
    if analysis["center_definition"] != "median_offset_by_direction":
        raise AlignmentRefusal(reason, "analysis center definition is unsupported")
    if analysis["residual_definition"] != "offset_s-direction_center_offset_s":
        raise AlignmentRefusal(reason, "analysis residual definition is unsupported")
    if analysis["conservative_bound_definition"] != "max_abs_response_support_endpoint_from_marker":
        raise AlignmentRefusal(reason, "analysis conservative bound definition is unsupported")
    required_consecutive = _positive_int(
        analysis["required_consecutive_target_samples"],
        "analysis.required_consecutive_target_samples",
        reason,
    )
    if required_consecutive < 2:
        raise AlignmentRefusal(reason, "at least two consecutive target samples are required")
    minimum = _positive_int(
        analysis["minimum_transitions_per_direction"],
        "analysis.minimum_transitions_per_direction",
        reason,
    )

    plan = manifest["execution_plan"]
    if not isinstance(plan, list) or not plan:
        raise AlignmentRefusal(reason, "execution_plan must be a non-empty array")
    seen_ids: set[str] = set()
    counts = {direction: 0 for direction in DIRECTIONS}
    previous_index = 0
    for position, row in enumerate(plan):
        if not isinstance(row, Mapping):
            raise AlignmentRefusal(reason, f"execution_plan[{position}] must be an object")
        _require_exact_keys(
            row,
            {"transition_id", "block_id", "execution_index", "position_in_block", "direction", "precondition"},
            f"execution_plan[{position}]",
            reason,
        )
        transition_id = row["transition_id"]
        if not isinstance(transition_id, str) or not transition_id or transition_id in seen_ids:
            raise AlignmentRefusal(reason, "execution_plan transition_id values must be unique strings")
        seen_ids.add(transition_id)
        execution_index = _positive_int(row["execution_index"], "execution_index", reason)
        if execution_index != previous_index + 1:
            raise AlignmentRefusal(reason, "execution_plan execution_index must be contiguous from 1")
        previous_index = execution_index
        direction = row["direction"]
        if direction not in DIRECTIONS:
            raise AlignmentRefusal(reason, f"unsupported transition direction: {direction!r}")
        expected_precondition = "stable_idle" if direction == "idle_to_load" else "stable_load"
        if row["precondition"] != expected_precondition:
            raise AlignmentRefusal(reason, f"precondition does not match {direction}")
        if not isinstance(row["block_id"], str) or not row["block_id"]:
            raise AlignmentRefusal(reason, "block_id must be a non-empty string")
        if row["position_in_block"] not in (1, 2):
            raise AlignmentRefusal(reason, "position_in_block must be 1 or 2")
        counts[direction] += 1
    if any(count < minimum for count in counts.values()):
        raise AlignmentRefusal(reason, f"execution_plan needs at least {minimum} transitions per direction")

    refusal_policy = manifest["refusal_policy"]
    if not isinstance(refusal_policy, Mapping):
        raise AlignmentRefusal(reason, "refusal_policy must be an object")
    _require_exact_keys(
        refusal_policy,
        {"missing_planned_transition", "malformed_transition", "unobserved_transition"},
        "manifest.refusal_policy",
        reason,
    )
    expected_reasons = {
        "missing_planned_transition": "transition_set_mismatch",
        "malformed_transition": "transition_malformed",
        "unobserved_transition": "transition_not_observed",
    }
    if dict(refusal_policy) != expected_reasons:
        raise AlignmentRefusal(reason, "refusal_policy reason codes differ from the frozen policy")
    return plan


def _validate_observation_header(observations: Mapping[str, Any], manifest_id: str) -> Sequence[Any]:
    reason = "observations_schema_invalid"
    _require_exact_keys(
        observations,
        {"schema_version", "observation_set_id", "manifest_id", "evidence_status", "source", "transitions"},
        "observations",
        reason,
    )
    if observations["schema_version"] != OBSERVATIONS_SCHEMA_VERSION:
        raise AlignmentRefusal(reason, "unsupported observations schema_version")
    if observations["manifest_id"] != manifest_id:
        raise AlignmentRefusal("manifest_mismatch", "observations.manifest_id does not match manifest")
    if observations["evidence_status"] not in OBSERVATION_STATUSES:
        raise AlignmentRefusal(reason, f"evidence_status must be one of {OBSERVATION_STATUSES}")
    source = observations["source"]
    if not isinstance(source, Mapping):
        raise AlignmentRefusal(reason, "source must be an object")
    _require_exact_keys(
        source,
        {"capture_class", "raw_samples_sha256", "markers_sha256"},
        "observations.source",
        reason,
    )
    if observations["evidence_status"] == EVIDENCE_STATUS:
        if source != {
            "capture_class": "synthetic_fixture",
            "raw_samples_sha256": None,
            "markers_sha256": None,
        }:
            raise AlignmentRefusal(reason, "fixture observations must use null synthetic source hashes")
    elif (
        source["capture_class"] != "real_mac_capture"
        or not _is_sha256(source["raw_samples_sha256"])
        or not _is_sha256(source["markers_sha256"])
    ):
        raise AlignmentRefusal(reason, "real-Mac observations require lowercase SHA-256 source hashes")
    if not isinstance(observations["observation_set_id"], str) or not observations["observation_set_id"]:
        raise AlignmentRefusal(reason, "observation_set_id must be a non-empty string")
    if not isinstance(observations["transitions"], list):
        raise AlignmentRefusal(reason, "transitions must be an array")
    return observations["transitions"]


def _transition_result(
    planned: Mapping[str, Any],
    observed: Mapping[str, Any],
    required_consecutive: int,
    minimum_plateau_samples: int,
) -> dict[str, Any]:
    reason = "transition_malformed"
    _require_exact_keys(
        observed,
        {
            "transition_id",
            "block_id",
            "execution_index",
            "position_in_block",
            "direction",
            "marker_epoch_s",
            "low_plateau_samples_w",
            "high_plateau_samples_w",
            "samples",
        },
        f"transition {planned['transition_id']}",
        reason,
    )
    for key in ("transition_id", "block_id", "execution_index", "position_in_block", "direction"):
        if observed[key] != planned[key]:
            raise AlignmentRefusal(reason, f"transition {planned['transition_id']} differs from plan at {key}")
    marker_s = _finite_number(observed["marker_epoch_s"], "marker_epoch_s", reason)
    plateau_values: dict[str, list[float]] = {}
    for state in ("low", "high"):
        key = f"{state}_plateau_samples_w"
        values = observed[key]
        if not isinstance(values, list) or len(values) < minimum_plateau_samples:
            raise AlignmentRefusal(reason, f"{key} must contain at least {minimum_plateau_samples} values")
        plateau_values[state] = [
            _finite_number(value, f"{key}[{index}]", reason)
            for index, value in enumerate(values)
        ]
        if any(value < 0.0 for value in plateau_values[state]):
            raise AlignmentRefusal(reason, f"{key} values must be nonnegative")
    low_w = float(statistics.median(plateau_values["low"]))
    high_w = float(statistics.median(plateau_values["high"]))
    if low_w < 0.0 or high_w <= low_w:
        raise AlignmentRefusal(reason, "plateaus must satisfy 0 <= low_plateau_w < high_plateau_w")
    threshold_w = (low_w + high_w) / 2.0
    samples = observed["samples"]
    if not isinstance(samples, list) or len(samples) < required_consecutive + 1:
        raise AlignmentRefusal(reason, "samples do not contain baseline plus required target persistence")

    parsed: list[tuple[float, float, float, bool]] = []
    previous_end: float | None = None
    for index, sample in enumerate(samples):
        if not isinstance(sample, Mapping):
            raise AlignmentRefusal(reason, f"samples[{index}] must be an object")
        _require_exact_keys(sample, {"interval_start_s", "interval_end_s", "mean_power_w"}, f"samples[{index}]", reason)
        start_s = _finite_number(sample["interval_start_s"], "interval_start_s", reason)
        end_s = _finite_number(sample["interval_end_s"], "interval_end_s", reason)
        power_w = _finite_number(sample["mean_power_w"], "mean_power_w", reason)
        if end_s <= start_s:
            raise AlignmentRefusal(reason, f"samples[{index}] interval must have positive width")
        if previous_end is not None and start_s < previous_end:
            raise AlignmentRefusal(reason, f"samples[{index}] overlaps or reverses the prior sample")
        if power_w < 0.0:
            raise AlignmentRefusal(reason, f"samples[{index}] mean_power_w must be nonnegative")
        target = power_w >= threshold_w if observed["direction"] == "idle_to_load" else power_w <= threshold_w
        parsed.append((start_s, end_s, power_w, target))
        previous_end = end_s

    response_index: int | None = None
    for index in range(len(parsed) - required_consecutive + 1):
        run = parsed[index : index + required_consecutive]
        if all(sample[3] for sample in run) and parsed[index][1] >= marker_s:
            response_index = index
            break
    if response_index is None:
        raise AlignmentRefusal(
            "transition_not_observed",
            f"transition {planned['transition_id']} has no persistent target-state response",
        )
    if not any((not target) and end_s <= marker_s for _, end_s, _, target in parsed[:response_index]):
        raise AlignmentRefusal(
            "transition_not_observed",
            f"transition {planned['transition_id']} lacks a baseline-state sample ending before the marker",
        )

    response_start_s, response_end_s, response_power_w, _ = parsed[response_index]
    support_start_offset_s = response_start_s - marker_s
    support_end_offset_s = response_end_s - marker_s
    offset_s = (response_start_s + response_end_s) / 2.0 - marker_s
    bound_s = max(abs(support_start_offset_s), abs(support_end_offset_s))
    return {
        "transition_id": planned["transition_id"],
        "block_id": planned["block_id"],
        "execution_index": planned["execution_index"],
        "position_in_block": planned["position_in_block"],
        "direction": planned["direction"],
        "marker_epoch_s": marker_s,
        "low_plateau_w": low_w,
        "high_plateau_w": high_w,
        "target_threshold_w": threshold_w,
        "response_sample_index": response_index,
        "response_sample_mean_power_w": response_power_w,
        "response_support_start_offset_s": support_start_offset_s,
        "response_support_end_offset_s": support_end_offset_s,
        "offset_s": offset_s,
        "direction_center_offset_s": None,
        "residual_s": None,
        "per_transition_conservative_bound_s": bound_s,
    }


def build_alignment_artifact(
    manifest: Mapping[str, Any],
    observations: Mapping[str, Any],
    *,
    manifest_sha256: str | None = None,
    observations_sha256: str | None = None,
) -> dict[str, Any]:
    """Validate frozen inputs and build a deterministic fixture-only artifact."""

    plan = _validate_manifest(manifest)
    observed_rows = _validate_observation_header(observations, manifest["manifest_id"])
    observed_by_id: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(observed_rows):
        if not isinstance(row, Mapping):
            raise AlignmentRefusal("transition_malformed", f"transitions[{index}] must be an object")
        transition_id = row.get("transition_id")
        if not isinstance(transition_id, str) or not transition_id or transition_id in observed_by_id:
            raise AlignmentRefusal("transition_malformed", "observed transition_id values must be unique strings")
        observed_by_id[transition_id] = row
    planned_ids = {row["transition_id"] for row in plan}
    observed_ids = set(observed_by_id)
    if observed_ids != planned_ids:
        raise AlignmentRefusal(
            "transition_set_mismatch",
            f"planned/observed transition IDs differ: missing={sorted(planned_ids - observed_ids)}, extra={sorted(observed_ids - planned_ids)}",
        )

    required_consecutive = manifest["analysis"]["required_consecutive_target_samples"]
    minimum_plateau_samples = manifest["analysis"]["minimum_plateau_samples_per_state"]
    results = [
        _transition_result(
            row,
            observed_by_id[row["transition_id"]],
            required_consecutive,
            minimum_plateau_samples,
        )
        for row in plan
    ]
    summaries: list[dict[str, Any]] = []
    for direction in DIRECTIONS:
        selected = [row for row in results if row["direction"] == direction]
        center_s = float(statistics.median(row["offset_s"] for row in selected))
        for row in selected:
            row["direction_center_offset_s"] = center_s
            row["residual_s"] = row["offset_s"] - center_s
        summaries.append(
            {
                "direction": direction,
                "n_transitions": len(selected),
                "center_offset_s": center_s,
                "max_abs_residual_s": max(abs(row["residual_s"]) for row in selected),
                "conservative_bound_s": max(row["per_transition_conservative_bound_s"] for row in selected),
            }
        )
    overall_bound_s = max(row["per_transition_conservative_bound_s"] for row in results)
    evidence_status = observations["evidence_status"]
    claim_disposition = (
        "NO_PHYSICAL_BOUND_CONCLUSION_PART_B_NOT_EXECUTED"
        if evidence_status == EVIDENCE_STATUS
        else "PROVISIONAL_PHYSICAL_BOUND_REVIEW_REQUIRED"
    )
    value_without_id: dict[str, Any] = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "evidence_status": evidence_status,
        "claim_disposition": claim_disposition,
        "manifest": {
            "manifest_id": manifest["manifest_id"],
            "sha256": manifest_sha256 or canonical_sha256(manifest),
        },
        "observations": {
            "schema_version": observations["schema_version"],
            "observation_set_id": observations["observation_set_id"],
            "sha256": observations_sha256 or canonical_sha256(observations),
            "source": dict(observations["source"]),
        },
        "method": dict(manifest["analysis"]),
        "transitions": results,
        "direction_summaries": summaries,
        "conservative_bound": {
            "value_s": overall_bound_s,
            "definition": manifest["analysis"]["conservative_bound_definition"],
            "coverage_scope": "fixture_response_sample_support_only",
            "p2_038_disposition": "UNASSESSED_PENDING_P2_046B_QUIET_MAC",
        },
        "limitations": [
            "Fixture observations are synthetic and do not validate powermetrics physical averaging behavior.",
            "The bound is not a confidence interval, tolerance interval, or reusable production constant.",
            "P2-038 per-run lifecycle bounds remain authoritative unless Part B is executed and adjudicated.",
        ],
    }
    artifact = {"artifact_id": _artifact_id(value_without_id), **value_without_id}
    errors = validate_alignment_artifact(artifact)
    if errors:
        raise AlignmentRefusal("artifact_schema_invalid", "; ".join(errors))
    return artifact


_ARTIFACT_TOP_KEYS = {
    "artifact_id",
    "schema_version",
    "evidence_status",
    "claim_disposition",
    "manifest",
    "observations",
    "method",
    "transitions",
    "direction_summaries",
    "conservative_bound",
    "limitations",
}
_ARTIFACT_TRANSITION_KEYS = {
    "transition_id",
    "block_id",
    "execution_index",
    "position_in_block",
    "direction",
    "marker_epoch_s",
    "low_plateau_w",
    "high_plateau_w",
    "target_threshold_w",
    "response_sample_index",
    "response_sample_mean_power_w",
    "response_support_start_offset_s",
    "response_support_end_offset_s",
    "offset_s",
    "direction_center_offset_s",
    "residual_s",
    "per_transition_conservative_bound_s",
}


def validate_alignment_artifact(value: Mapping[str, Any]) -> list[str]:
    """Validate v1 schema shape, identifiers, and closed-form arithmetic."""

    errors: list[str] = []
    if not isinstance(value, Mapping):
        return ["artifact must be an object"]
    if set(value) != _ARTIFACT_TOP_KEYS:
        errors.append("artifact top-level keys differ from v1 schema")
        return errors
    if value["schema_version"] != ARTIFACT_SCHEMA_VERSION:
        errors.append("artifact schema_version is unsupported")
    if value["evidence_status"] not in OBSERVATION_STATUSES:
        errors.append(f"artifact evidence_status must be one of {OBSERVATION_STATUSES}")
    expected_disposition = (
        "NO_PHYSICAL_BOUND_CONCLUSION_PART_B_NOT_EXECUTED"
        if value["evidence_status"] == EVIDENCE_STATUS
        else "PROVISIONAL_PHYSICAL_BOUND_REVIEW_REQUIRED"
    )
    if value["claim_disposition"] != expected_disposition:
        errors.append("artifact claim_disposition does not match evidence status")
    method = value["method"]
    method_keys = {
        "method_id",
        "target_threshold_rule",
        "plateau_definition",
        "minimum_plateau_samples_per_state",
        "required_consecutive_target_samples",
        "offset_definition",
        "center_definition",
        "residual_definition",
        "conservative_bound_definition",
        "minimum_transitions_per_direction",
    }
    if not isinstance(method, Mapping) or set(method) != method_keys:
        errors.append("method block differs from v1 schema")
    else:
        expected_method_values = {
            "method_id": METHOD_ID,
            "target_threshold_rule": "midpoint(low_plateau_w,high_plateau_w)",
            "plateau_definition": "median_of_declared_stable_state_samples",
            "offset_definition": "response_sample_midpoint_s-marker_epoch_s",
            "center_definition": "median_offset_by_direction",
            "residual_definition": "offset_s-direction_center_offset_s",
            "conservative_bound_definition": "max_abs_response_support_endpoint_from_marker",
        }
        if any(method[key] != expected for key, expected in expected_method_values.items()):
            errors.append("method block contains an unsupported v1 definition")
        for key in (
            "minimum_plateau_samples_per_state",
            "required_consecutive_target_samples",
            "minimum_transitions_per_direction",
        ):
            if isinstance(method[key], bool) or not isinstance(method[key], int) or method[key] < 2:
                errors.append(f"method.{key} must be an integer of at least 2")
    manifest_record = value["manifest"]
    if (
        not isinstance(manifest_record, Mapping)
        or set(manifest_record) != {"manifest_id", "sha256"}
        or not isinstance(manifest_record.get("manifest_id"), str)
        or not manifest_record.get("manifest_id")
        or not _is_sha256(manifest_record.get("sha256"))
    ):
        errors.append("manifest provenance record differs from v1 schema")
    observation_record = value["observations"]
    if not isinstance(observation_record, Mapping) or set(observation_record) != {
        "schema_version",
        "observation_set_id",
        "sha256",
        "source",
    }:
        errors.append("observations provenance record differs from v1 schema")
    else:
        if observation_record["schema_version"] != OBSERVATIONS_SCHEMA_VERSION:
            errors.append("observations provenance schema_version is unsupported")
        if not isinstance(observation_record["observation_set_id"], str) or not observation_record["observation_set_id"]:
            errors.append("observations provenance observation_set_id is invalid")
        if not _is_sha256(observation_record["sha256"]):
            errors.append("observations provenance sha256 is invalid")
        source = observation_record["source"]
        expected_source_keys = {"capture_class", "raw_samples_sha256", "markers_sha256"}
        if not isinstance(source, Mapping) or set(source) != expected_source_keys:
            errors.append("observations source record differs from v1 schema")
        elif value["evidence_status"] == EVIDENCE_STATUS:
            if source != {"capture_class": "synthetic_fixture", "raw_samples_sha256": None, "markers_sha256": None}:
                errors.append("fixture artifact source provenance is invalid")
        elif (
            source["capture_class"] != "real_mac_capture"
            or not _is_sha256(source["raw_samples_sha256"])
            or not _is_sha256(source["markers_sha256"])
        ):
            errors.append("real-Mac artifact source provenance is invalid")
    artifact_id = value["artifact_id"]
    if not isinstance(artifact_id, str) or not artifact_id.startswith("lta-") or len(artifact_id) != 68:
        errors.append("artifact_id must be lta- plus 64 lowercase hex digits")
    else:
        try:
            int(artifact_id[4:], 16)
        except ValueError:
            errors.append("artifact_id must be lta- plus 64 lowercase hex digits")
    transitions = value["transitions"]
    if not isinstance(transitions, list) or not transitions:
        errors.append("transitions must be a non-empty array")
        return errors
    by_direction: dict[str, list[Mapping[str, Any]]] = {direction: [] for direction in DIRECTIONS}
    transition_ids: set[str] = set()
    for index, row in enumerate(transitions):
        if not isinstance(row, Mapping) or set(row) != _ARTIFACT_TRANSITION_KEYS:
            errors.append(f"transitions[{index}] keys differ from v1 schema")
            continue
        direction = row["direction"]
        if direction not in DIRECTIONS:
            errors.append(f"transitions[{index}].direction is unsupported")
            continue
        transition_id = row["transition_id"]
        if not isinstance(transition_id, str) or not transition_id or transition_id in transition_ids:
            errors.append(f"transitions[{index}].transition_id is invalid or duplicated")
        else:
            transition_ids.add(transition_id)
        if (
            isinstance(row["execution_index"], bool)
            or not isinstance(row["execution_index"], int)
            or row["execution_index"] < 1
        ):
            errors.append(f"transitions[{index}].execution_index must be a positive integer")
        if row["position_in_block"] not in (1, 2):
            errors.append(f"transitions[{index}].position_in_block must be 1 or 2")
        numeric_keys = (
            "marker_epoch_s",
            "low_plateau_w",
            "high_plateau_w",
            "target_threshold_w",
            "response_sample_mean_power_w",
            "response_support_start_offset_s",
            "response_support_end_offset_s",
            "offset_s",
            "direction_center_offset_s",
            "residual_s",
            "per_transition_conservative_bound_s",
        )
        if any(isinstance(row[key], bool) or not isinstance(row[key], (int, float)) or not math.isfinite(float(row[key])) for key in numeric_keys):
            errors.append(f"transitions[{index}] arithmetic fields must be finite numbers")
            continue
        if (
            isinstance(row["response_sample_index"], bool)
            or not isinstance(row["response_sample_index"], int)
            or row["response_sample_index"] < 0
        ):
            errors.append(f"transitions[{index}].response_sample_index must be a nonnegative integer")
        low_w = float(row["low_plateau_w"])
        high_w = float(row["high_plateau_w"])
        if low_w < 0.0 or high_w <= low_w:
            errors.append(f"transitions[{index}] plateau ordering is invalid")
        if not math.isclose(float(row["target_threshold_w"]), (low_w + high_w) / 2.0, rel_tol=0.0, abs_tol=1e-12):
            errors.append(f"transitions[{index}].target_threshold_w differs from plateau midpoint")
        response_w = float(row["response_sample_mean_power_w"])
        threshold_w = float(row["target_threshold_w"])
        if (direction == "idle_to_load" and response_w < threshold_w) or (
            direction == "load_to_idle" and response_w > threshold_w
        ):
            errors.append(f"transitions[{index}] response sample is not in the target state")
        start_s = float(row["response_support_start_offset_s"])
        end_s = float(row["response_support_end_offset_s"])
        offset_s = float(row["offset_s"])
        center_s = float(row["direction_center_offset_s"])
        if end_s <= start_s:
            errors.append(f"transitions[{index}] response support is not positive-width")
        if not math.isclose(offset_s, (start_s + end_s) / 2.0, rel_tol=0.0, abs_tol=1e-12):
            errors.append(f"transitions[{index}].offset_s does not equal support midpoint")
        if not math.isclose(float(row["residual_s"]), offset_s - center_s, rel_tol=0.0, abs_tol=1e-12):
            errors.append(f"transitions[{index}].residual_s does not equal offset minus center")
        expected_bound = max(abs(start_s), abs(end_s))
        if not math.isclose(float(row["per_transition_conservative_bound_s"]), expected_bound, rel_tol=0.0, abs_tol=1e-12):
            errors.append(f"transitions[{index}] conservative bound arithmetic differs")
        by_direction[direction].append(row)

    summaries = value["direction_summaries"]
    expected_summary_keys = {"direction", "n_transitions", "center_offset_s", "max_abs_residual_s", "conservative_bound_s"}
    if not isinstance(summaries, list) or [row.get("direction") if isinstance(row, Mapping) else None for row in summaries] != list(DIRECTIONS):
        errors.append("direction_summaries must enumerate directions in frozen order")
    else:
        for summary in summaries:
            if set(summary) != expected_summary_keys:
                errors.append(f"direction summary {summary.get('direction')} keys differ from v1 schema")
                continue
            selected = by_direction[summary["direction"]]
            if not selected:
                errors.append(f"direction summary {summary['direction']} has no transitions")
                continue
            expected_center = float(statistics.median(float(row["offset_s"]) for row in selected))
            expected_residual = max(abs(float(row["residual_s"])) for row in selected)
            expected_bound = max(float(row["per_transition_conservative_bound_s"]) for row in selected)
            expected = (len(selected), expected_center, expected_residual, expected_bound)
            actual = (
                summary["n_transitions"],
                summary["center_offset_s"],
                summary["max_abs_residual_s"],
                summary["conservative_bound_s"],
            )
            if actual[0] != expected[0] or any(
                isinstance(a, bool) or not isinstance(a, (int, float)) or not math.isclose(float(a), float(e), rel_tol=0.0, abs_tol=1e-12)
                for a, e in zip(actual[1:], expected[1:])
            ):
                errors.append(f"direction summary {summary['direction']} arithmetic differs")
            for row in selected:
                if not math.isclose(float(row["direction_center_offset_s"]), expected_center, rel_tol=0.0, abs_tol=1e-12):
                    errors.append(f"transition {row['transition_id']} center differs from direction median")

    bound = value["conservative_bound"]
    expected_bound_keys = {"value_s", "definition", "coverage_scope", "p2_038_disposition"}
    if not isinstance(bound, Mapping) or set(bound) != expected_bound_keys:
        errors.append("conservative_bound keys differ from v1 schema")
    else:
        valid_transition_rows = [row for rows in by_direction.values() for row in rows]
        if valid_transition_rows:
            expected_overall = max(float(row["per_transition_conservative_bound_s"]) for row in valid_transition_rows)
            if isinstance(bound["value_s"], bool) or not isinstance(bound["value_s"], (int, float)) or not math.isclose(float(bound["value_s"]), expected_overall, rel_tol=0.0, abs_tol=1e-12):
                errors.append("conservative_bound.value_s arithmetic differs")
        else:
            errors.append("conservative_bound cannot be re-derived without valid transitions")
        if bound["definition"] != "max_abs_response_support_endpoint_from_marker":
            errors.append("conservative_bound.definition is unsupported")
        if bound["coverage_scope"] != "fixture_response_sample_support_only":
            errors.append("conservative_bound.coverage_scope is not fixture-only")
        if bound["p2_038_disposition"] != "UNASSESSED_PENDING_P2_046B_QUIET_MAC":
            errors.append("conservative_bound P2-038 disposition is not pending")
    if not isinstance(value["limitations"], list) or len(value["limitations"]) < 3 or not all(isinstance(item, str) and item for item in value["limitations"]):
        errors.append("limitations must contain at least three non-empty strings")
    if isinstance(artifact_id, str):
        without_id = {key: item for key, item in value.items() if key != "artifact_id"}
        try:
            expected_artifact_id = _artifact_id(without_id)
        except AlignmentRefusal:
            errors.append("artifact content is not canonical JSON")
        else:
            if artifact_id != expected_artifact_id:
                errors.append("artifact_id does not match canonical artifact content")
    return errors


def render_artifact(value: Mapping[str, Any]) -> bytes:
    """Render deterministic UTF-8 JSON with sorted keys and one LF."""

    errors = validate_alignment_artifact(value)
    if errors:
        raise AlignmentRefusal("artifact_schema_invalid", "; ".join(errors))
    try:
        return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise AlignmentRefusal("artifact_schema_invalid", str(exc)) from exc


def write_artifact_atomic(path: Path, value: Mapping[str, Any]) -> None:
    """Atomically replace ``path`` with deterministic artifact bytes."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = render_artifact(value)
    handle = tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}.", delete=False)
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise
