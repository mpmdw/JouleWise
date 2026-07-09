"""P2-039 detection-floor calculator (D-054 false-effect guard).

Implements the P2-039 DRAFT spec (``docs/specs/c027/p2-039_floor_artifact.md``):

- the absolute and comparative D-054 false-effect floors with the frozen
  small-sample guard factor;
- the exact ABBA block delta ``(B1 + B2 - A1 - A2) / 2``;
- emit/validate for the versioned ``joulewise.detection_floor_artifact.v1``
  calculation records; and
- the pure conservative regime-transport refusal rule
  (``same_stack_componentwise_worst_case.v1``).

Pure calculation module: no I/O, no CLI integration (integration into
``cli.py``/``reduce.py`` is deferred to lead adjudication of the DRAFT spec).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from joulewise.aggregate import student_t_critical_95

__all__ = [
    "SCHEMA_VERSION",
    "METHOD_ID",
    "GUARD_RULE_ID",
    "TRANSPORT_RULE_ID",
    "GUARD_REFERENCE_N",
    "GUARD_MINIMUM_N",
    "TRANSPORT_REASON_CODES",
    "FloorEstimate",
    "small_sample_guard_factor",
    "absolute_false_effect_floor",
    "comparative_false_effect_floor",
    "abba_delta",
    "build_method_block",
    "build_absolute_record",
    "build_comparative_record",
    "build_floor_cell",
    "build_transport_group",
    "build_floor_artifact",
    "compose_transport_group",
    "validate_floor_artifact",
    "transport_refusal_reasons",
]

SCHEMA_VERSION = "joulewise.detection_floor_artifact.v1"
METHOD_ID = "d054_false_effect_guard.v1"
GUARD_RULE_ID = "residual_df_ratio_to_n10.v1"
TRANSPORT_RULE_ID = "same_stack_componentwise_worst_case.v1"

# ADJUDICATION-PENDING (P2-039 DRAFT spec Unit 2.3): the small-sample guard
# below is the spec's frozen *proposal* — g(n) = max(1, sqrt((10-1)/(n-1)))
# for n >= 5, i.e. the square root of the residual-degrees-of-freedom deficit
# relative to the n=10 design point (g(5) = 1.5, joining exactly to 1.0 at
# n=10). It has NOT yet been lead-adjudicated into D-054; do not treat it as
# an accepted rule or describe it as a coverage/confidence guarantee.
GUARD_REFERENCE_N = 10
GUARD_MINIMUM_N = 5

_CALIBRATION_SCOPES = ("window_a", "window_b_revalidation", "smoke")
_WINDOW_CLASSES = ("request", "phase", "item", "level", "session")
_USE_ROLES = ("primary_claim_gate", "smoke_only", "staleness_sentinel")
_STATUSES = ("claim_ready", "smoke_only", "incomplete", "stale")
_APPLICABILITIES = ("required", "not_applicable", "unknown")
_BOUND_TERMS = ("clock_anchor_bound_s", "interpolation_bound_j", "idle_drift_bound_j")
_ENVELOPE_MIN_FIELDS = ("mean_power_w_min", "window_duration_s_min", "cadence_ratio_min")
_ENVELOPE_MAX_FIELDS = (
    "mean_power_w_max",
    "window_duration_s_max",
    "p95_sample_gap_s_max",
    "bracketing_sample_gap_s_max",
)
_ENVELOPE_FIELDS = _ENVELOPE_MIN_FIELDS + _ENVELOPE_MAX_FIELDS

# Closed v1 reason set (spec Unit 6.3).
TRANSPORT_REASON_CODES = (
    "artifact_hash_mismatch",
    "artifact_schema_invalid",
    "cell_missing",
    "cell_not_claim_ready",
    "cell_stale",
    "condition_not_predeclared",
    "stack_mismatch",
    "power_outside_calibrated_envelope",
    "duration_outside_calibrated_envelope",
    "cadence_harder_than_calibration",
    "clock_anchor_harder_than_calibration",
    "interpolation_harder_than_calibration",
    "drift_harder_than_calibration",
    "consumer_term_unknown",
    "transport_group_incomplete",
)


# ---------------------------------------------------------------------------
# Pure D-054 math
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FloorEstimate:
    """Full calculation record for one floor component."""

    kind: str  # "absolute" | "comparative"
    n: int
    mean_j: float
    deviations_j: tuple  # residuals (absolute) or block deltas (comparative)
    sample_stddev_j: float
    max_abs_deviation_j: float
    t_critical: float
    prediction_component_j: float
    unguarded_floor_j: float
    guard_factor: Optional[float]  # None when n < GUARD_MINIMUM_N (smoke only)
    guarded_floor_j: Optional[float]


def small_sample_guard_factor(n: int) -> float:
    """Frozen (ADJUDICATION-PENDING) small-sample guard g(n) for n >= 5."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an int (bool rejected)")
    if n < GUARD_MINIMUM_N:
        raise ValueError(f"guard factor undefined below n={GUARD_MINIMUM_N} (smoke only)")
    if n >= GUARD_REFERENCE_N:
        return 1.0
    return math.sqrt((GUARD_REFERENCE_N - 1) / (n - 1))


def _clean_values(values_j: Sequence[float], label: str) -> list:
    cleaned = []
    for value in values_j:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{label} must be finite numbers")
        value = float(value)
        if not math.isfinite(value):
            raise ValueError(f"{label} must be finite")
        cleaned.append(value)
    if len(cleaned) < 2:
        raise ValueError(f"need at least 2 {label} for a sample standard deviation")
    return cleaned


def _floor_estimate(kind: str, deviations: Sequence[float], mean: float, prediction_extra: float) -> FloorEstimate:
    n = len(deviations)
    dev_mean = sum(deviations) / n
    s = math.sqrt(sum((d - dev_mean) ** 2 for d in deviations) / (n - 1))
    t_critical = student_t_critical_95(n - 1)
    prediction = prediction_extra + t_critical * s * math.sqrt(1.0 + 1.0 / n)
    max_abs = max(abs(d) for d in deviations)
    unguarded = max(max_abs, prediction)
    if n >= GUARD_MINIMUM_N:
        guard: Optional[float] = small_sample_guard_factor(n)
        guarded: Optional[float] = guard * unguarded
    else:
        # Smoke-only diagnostics: unguarded components emitted, floor is null.
        guard = None
        guarded = None
    return FloorEstimate(
        kind=kind,
        n=n,
        mean_j=mean,
        deviations_j=tuple(deviations),
        sample_stddev_j=s,
        max_abs_deviation_j=max_abs,
        t_critical=t_critical,
        prediction_component_j=prediction,
        unguarded_floor_j=unguarded,
        guard_factor=guard,
        guarded_floor_j=guarded,
    )


def absolute_false_effect_floor(values_j: Sequence[float]) -> FloorEstimate:
    """D-054 absolute false-effect floor over bundle-clustered energies."""
    values = _clean_values(values_j, "energies")
    mean = sum(values) / len(values)
    residuals = [v - mean for v in values]
    return _floor_estimate("absolute", residuals, mean, 0.0)


def comparative_false_effect_floor(block_deltas_j: Sequence[float]) -> FloorEstimate:
    """D-054 comparative false-effect floor over ABBA block deltas.

    The prediction component includes ``abs(mean_delta)`` — deltas are never
    re-centered before the floor is computed.
    """
    deltas = _clean_values(block_deltas_j, "block deltas")
    mean = sum(deltas) / len(deltas)
    return _floor_estimate("comparative", deltas, mean, abs(mean))


def abba_delta(a1_j: float, b1_j: float, b2_j: float, a2_j: float) -> float:
    """Exact ABBA block delta ``(B1 + B2 - A1 - A2) / 2``; sign is B - A."""
    members = _clean_values([a1_j, b1_j, b2_j, a2_j], "ABBA members")
    a1, b1, b2, a2 = members
    return (b1 + b2 - a1 - a2) / 2.0


# ---------------------------------------------------------------------------
# Artifact emit (joulewise.detection_floor_artifact.v1)
# ---------------------------------------------------------------------------


def build_method_block() -> dict:
    return {
        "method_id": METHOD_ID,
        "confidence": 0.95,
        "t_critical_source": "joulewise.aggregate.student_t_critical_95.v1",
        "absolute_formula": "max(max_abs_residual_j,t_critical*sample_stddev_j*sqrt(1+1/n))",
        "comparative_formula": "max(max_abs_delta_j,abs(mean_delta_j)+t_critical*sample_stddev_j*sqrt(1+1/n))",
        "abba_delta_formula": "(B1+B2-A1-A2)/2",
        "small_sample_guard": {
            "rule_id": GUARD_RULE_ID,
            "formula": "max(1,sqrt((10-1)/(n-1)))",
            "reference_n": GUARD_REFERENCE_N,
            "minimum_n": GUARD_MINIMUM_N,
            "maximum_guarded_n_exclusive": GUARD_REFERENCE_N,
            "frozen_before_calibration": True,
        },
    }


def build_absolute_record(estimate: FloorEstimate, bundle_observations: Sequence[Mapping]) -> dict:
    if estimate.kind != "absolute":
        raise ValueError("absolute record requires an absolute FloorEstimate")
    if len(bundle_observations) != estimate.n:
        raise ValueError("bundle_observations length must equal n")
    return {
        "n": estimate.n,
        "mean_j": estimate.mean_j,
        "residuals_j": list(estimate.deviations_j),
        "sample_stddev_j": estimate.sample_stddev_j,
        "max_abs_residual_j": estimate.max_abs_deviation_j,
        "t_critical": estimate.t_critical,
        "prediction_component_j": estimate.prediction_component_j,
        "unguarded_floor_j": estimate.unguarded_floor_j,
        "guard_factor": estimate.guard_factor,
        "guarded_floor_j": estimate.guarded_floor_j,
        "bundle_observations": [dict(obs) for obs in bundle_observations],
    }


def build_comparative_record(estimate: FloorEstimate, blocks: Sequence[Mapping]) -> dict:
    if estimate.kind != "comparative":
        raise ValueError("comparative record requires a comparative FloorEstimate")
    if len(blocks) != estimate.n:
        raise ValueError("blocks length must equal n_blocks")
    return {
        "n_blocks": estimate.n,
        "mean_delta_j": estimate.mean_j,
        "block_deltas_j": list(estimate.deviations_j),
        "sample_stddev_j": estimate.sample_stddev_j,
        "max_abs_delta_j": estimate.max_abs_deviation_j,
        "t_critical": estimate.t_critical,
        "prediction_component_j": estimate.prediction_component_j,
        "unguarded_floor_j": estimate.unguarded_floor_j,
        "guard_factor": estimate.guard_factor,
        "guarded_floor_j": estimate.guarded_floor_j,
        "blocks": [dict(block) for block in blocks],
    }


def build_floor_cell(
    *,
    cell_id: str,
    key: Mapping,
    eligibility: Mapping,
    absolute: Optional[Mapping],
    comparative: Optional[Mapping],
    source_regime: Mapping,
    transport_group_id: str,
    provenance: Mapping,
) -> dict:
    floor_abs = absolute.get("guarded_floor_j") if absolute is not None else None
    floor_cmp = comparative.get("guarded_floor_j") if comparative is not None else None
    if floor_abs is not None and floor_cmp is not None:
        floor_gate: Optional[float] = max(floor_abs, floor_cmp)
    else:
        floor_gate = None
    return {
        "cell_id": cell_id,
        "key": dict(key),
        "eligibility": dict(eligibility),
        "floor_abs_j": floor_abs,
        "floor_cmp_j": floor_cmp,
        "floor_gate_j": floor_gate,
        "absolute": dict(absolute) if absolute is not None else None,
        "comparative": dict(comparative) if comparative is not None else None,
        "source_regime": dict(source_regime),
        "transport_group_id": transport_group_id,
        "provenance": dict(provenance),
    }


def compose_transport_group(source_cells: Sequence[Mapping]) -> dict:
    """Componentwise worst-case composition over all source cells (Unit 6.2).

    Maxima/minima are taken independently per field, so the composed corner
    may combine values from different source cells. Bound-term maxima compose
    to the max over ``required`` numeric maxima; if any source term is
    ``unknown`` the composed term is null (fail-closed for consumers that
    need it).
    """
    if not source_cells:
        raise ValueError("transport group requires at least one source cell")
    observed = [cell["source_regime"]["stress_observed"] for cell in source_cells]
    envelope: dict = {}
    for field in _ENVELOPE_MIN_FIELDS:
        envelope[field] = min(o[field] for o in observed)
    for field in _ENVELOPE_MAX_FIELDS:
        envelope[field] = max(o[field] for o in observed)
    bound_maxima: dict = {}
    for term in _BOUND_TERMS:
        maxima = []
        unknown = False
        for o in observed:
            entry = o["bound_terms"][term]
            if entry["applicability"] == "unknown":
                unknown = True
            elif entry["applicability"] == "required":
                maxima.append(entry["maximum"])
        bound_maxima[term] = None if (unknown or not maxima) else max(maxima)
    envelope["bound_term_maxima"] = bound_maxima
    return {
        "composed_floor_abs_j": max(cell["floor_abs_j"] for cell in source_cells),
        "composed_floor_cmp_j": max(cell["floor_cmp_j"] for cell in source_cells),
        "composed_floor_gate_j": max(cell["floor_gate_j"] for cell in source_cells),
        "stress_envelope": envelope,
    }


def build_transport_group(
    *,
    transport_group_id: str,
    backend: str,
    metric: str,
    window_class: str,
    stack_identity_sha256: str,
    source_cells: Sequence[Mapping],
    allowed_consumer_condition_families: Sequence[Mapping],
) -> dict:
    composed = compose_transport_group(source_cells)
    return {
        "transport_group_id": transport_group_id,
        "rule_id": TRANSPORT_RULE_ID,
        "backend": backend,
        "metric": metric,
        "window_class": window_class,
        "stack_identity_sha256": stack_identity_sha256,
        "source_cell_ids": [cell["cell_id"] for cell in source_cells],
        "allowed_consumer_condition_families": [dict(f) for f in allowed_consumer_condition_families],
        "composed_floor_abs_j": composed["composed_floor_abs_j"],
        "composed_floor_cmp_j": composed["composed_floor_cmp_j"],
        "composed_floor_gate_j": composed["composed_floor_gate_j"],
        "stress_envelope": composed["stress_envelope"],
    }


def build_floor_artifact(
    *,
    artifact_id: str,
    calibration_scope: str,
    provenance: Mapping,
    cells: Sequence[Mapping],
    transport_groups: Sequence[Mapping],
) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "calibration_scope": calibration_scope,
        "method": build_method_block(),
        "provenance": dict(provenance),
        "cells": [dict(cell) for cell in cells],
        "transport_groups": [dict(group) for group in transport_groups],
    }


# ---------------------------------------------------------------------------
# Artifact validation
# ---------------------------------------------------------------------------

_TOP_KEYS = {
    "schema_version",
    "artifact_id",
    "calibration_scope",
    "method",
    "provenance",
    "cells",
    "transport_groups",
}
_CELL_KEYS = {
    "cell_id",
    "key",
    "eligibility",
    "floor_abs_j",
    "floor_cmp_j",
    "floor_gate_j",
    "absolute",
    "comparative",
    "source_regime",
    "transport_group_id",
    "provenance",
}
_KEY_KEYS = {"backend", "metric", "window_class", "condition_family_id", "condition_family_sha256"}
_ELIGIBILITY_KEYS = {"use_role", "minimum_claim_n", "status", "claim_usable", "reason_codes"}
_ABS_KEYS = {
    "n",
    "mean_j",
    "residuals_j",
    "sample_stddev_j",
    "max_abs_residual_j",
    "t_critical",
    "prediction_component_j",
    "unguarded_floor_j",
    "guard_factor",
    "guarded_floor_j",
    "bundle_observations",
}
_CMP_KEYS = {
    "n_blocks",
    "mean_delta_j",
    "block_deltas_j",
    "sample_stddev_j",
    "max_abs_delta_j",
    "t_critical",
    "prediction_component_j",
    "unguarded_floor_j",
    "guard_factor",
    "guarded_floor_j",
    "blocks",
}
_OBS_KEYS = {"bundle_id", "bundle_sha256", "config_sha256", "metric_value_j"}
_BLOCK_KEYS = {"block_id", "executed_labels", "members", "delta_j"}
_MEMBER_KEYS = {"position", "bundle_id", "bundle_sha256", "config_sha256", "metric_value_j"}
_GROUP_KEYS = {
    "transport_group_id",
    "rule_id",
    "backend",
    "metric",
    "window_class",
    "stack_identity_sha256",
    "source_cell_ids",
    "allowed_consumer_condition_families",
    "composed_floor_abs_j",
    "composed_floor_cmp_j",
    "composed_floor_gate_j",
    "stress_envelope",
}


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _close(actual, expected) -> bool:
    if actual is None or expected is None:
        return actual is None and expected is None
    if not _is_number(actual):
        return False
    return abs(actual - expected) <= max(1e-12, 1e-12 * abs(expected))


def _is_hex(value, length: int = 64) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(c in "0123456789abcdef" for c in value)
    )


def _check_keys(mapping, allowed, where, errors) -> bool:
    if not isinstance(mapping, Mapping):
        errors.append(f"{where}: expected an object")
        return False
    unknown = set(mapping) - allowed
    missing = allowed - set(mapping)
    for key in sorted(unknown):
        errors.append(f"{where}: unrecognized key {key!r}")
    for key in sorted(missing):
        errors.append(f"{where}: missing key {key!r}")
    return not missing


def _validate_estimate_math(record, where, deviations, mean, prediction_extra, errors) -> None:
    n = len(deviations)
    est = _floor_estimate("absolute", list(deviations), mean, prediction_extra)
    stddev_key = "sample_stddev_j"
    checks = [
        (stddev_key, est.sample_stddev_j),
        ("t_critical", est.t_critical),
        ("prediction_component_j", est.prediction_component_j),
        ("unguarded_floor_j", est.unguarded_floor_j),
    ]
    for key, expected in checks:
        if not _close(record.get(key), expected):
            errors.append(f"{where}: stored {key} does not match recomputed value")
    expected_guard = small_sample_guard_factor(n) if n >= GUARD_MINIMUM_N else None
    if expected_guard is None:
        if record.get("guard_factor") is not None or record.get("guarded_floor_j") is not None:
            errors.append(f"{where}: guard values must be null when n < {GUARD_MINIMUM_N}")
    else:
        if not _close(record.get("guard_factor"), expected_guard):
            errors.append(f"{where}: stored guard_factor does not match recomputed value")
        if not _close(record.get("guarded_floor_j"), expected_guard * est.unguarded_floor_j):
            errors.append(f"{where}: stored guarded_floor_j does not match recomputed value")


def _validate_bound_terms(terms, where, errors) -> None:
    if not isinstance(terms, Mapping) or set(terms) != set(_BOUND_TERMS):
        errors.append(f"{where}: bound_terms must contain exactly {sorted(_BOUND_TERMS)}")
        return
    for term in _BOUND_TERMS:
        entry = terms[term]
        if not _check_keys(entry, {"applicability", "maximum"}, f"{where}.{term}", errors):
            continue
        applicability = entry["applicability"]
        maximum = entry["maximum"]
        if applicability not in _APPLICABILITIES:
            errors.append(f"{where}.{term}: invalid applicability {applicability!r}")
        elif applicability == "required":
            if not _is_number(maximum) or maximum < 0:
                errors.append(f"{where}.{term}: required term needs a finite nonnegative maximum")
        elif maximum is not None:
            errors.append(f"{where}.{term}: maximum must be null when {applicability}")


def _validate_stress_observed(observed, where, errors) -> None:
    allowed = set(_ENVELOPE_FIELDS) | {"bound_terms"}
    if not _check_keys(observed, allowed, where, errors):
        return
    for field in _ENVELOPE_FIELDS:
        value = observed[field]
        if not _is_number(value) or value < 0:
            errors.append(f"{where}.{field}: must be a finite nonnegative number")
    _validate_bound_terms(observed["bound_terms"], where, errors)


def _validate_absolute(record, where, errors) -> None:
    if not _check_keys(record, _ABS_KEYS, where, errors):
        return
    residuals = record["residuals_j"]
    observations = record["bundle_observations"]
    n = record["n"]
    if not isinstance(n, int) or isinstance(n, bool):
        errors.append(f"{where}: n must be an integer")
        return
    if not isinstance(residuals, list) or not isinstance(observations, list):
        errors.append(f"{where}: residuals_j and bundle_observations must be arrays")
        return
    if not (n == len(residuals) == len(observations)):
        errors.append(f"{where}: n, residuals_j, and bundle_observations lengths disagree")
        return
    values = []
    for i, obs in enumerate(observations):
        obs_where = f"{where}.bundle_observations[{i}]"
        if not _check_keys(obs, _OBS_KEYS, obs_where, errors):
            return
        if not _is_hex(obs["bundle_sha256"]) or not _is_hex(obs["config_sha256"]):
            errors.append(f"{obs_where}: hashes must be 64 lowercase hex chars")
        if not _is_number(obs["metric_value_j"]):
            errors.append(f"{obs_where}: metric_value_j must be finite")
            return
        values.append(obs["metric_value_j"])
    if any(not _is_number(r) for r in residuals):
        errors.append(f"{where}: residuals_j must all be finite numbers")
        return
    mean = sum(values) / n
    if not _close(record["mean_j"], mean):
        errors.append(f"{where}: stored mean_j does not match observations")
    expected_residuals = [v - mean for v in values]
    if not all(_close(r, e) for r, e in zip(residuals, expected_residuals)):
        errors.append(f"{where}: stored residuals_j do not match observations")
    if not _close(record["max_abs_residual_j"], max(abs(r) for r in expected_residuals)):
        errors.append(f"{where}: stored max_abs_residual_j does not match recomputed value")
    _validate_estimate_math(record, where, expected_residuals, mean, 0.0, errors)


def _validate_comparative(record, where, errors) -> None:
    if not _check_keys(record, _CMP_KEYS, where, errors):
        return
    deltas = record["block_deltas_j"]
    blocks = record["blocks"]
    n = record["n_blocks"]
    if not isinstance(n, int) or isinstance(n, bool):
        errors.append(f"{where}: n_blocks must be an integer")
        return
    if not isinstance(deltas, list) or not isinstance(blocks, list):
        errors.append(f"{where}: block_deltas_j and blocks must be arrays")
        return
    if not (n == len(deltas) == len(blocks)):
        errors.append(f"{where}: n_blocks, block_deltas_j, and blocks lengths disagree")
        return
    expected_deltas = []
    for i, block in enumerate(blocks):
        block_where = f"{where}.blocks[{i}]"
        if not _check_keys(block, _BLOCK_KEYS, block_where, errors):
            return
        if block["executed_labels"] != ["A", "B", "B", "A"]:
            errors.append(f"{block_where}: executed_labels must be A/B/B/A")
        members = block["members"]
        if not isinstance(members, list) or len(members) != 4:
            errors.append(f"{block_where}: exactly four members required")
            return
        by_position = {}
        for j, member in enumerate(members):
            member_where = f"{block_where}.members[{j}]"
            if not _check_keys(member, _MEMBER_KEYS, member_where, errors):
                return
            if not _is_hex(member["bundle_sha256"]) or not _is_hex(member["config_sha256"]):
                errors.append(f"{member_where}: hashes must be 64 lowercase hex chars")
            if not _is_number(member["metric_value_j"]):
                errors.append(f"{member_where}: metric_value_j must be finite")
                return
            by_position[member["position"]] = member["metric_value_j"]
        if [m["position"] for m in members] != ["A1", "B1", "B2", "A2"]:
            errors.append(f"{block_where}: member positions must be A1/B1/B2/A2 in order")
            return
        expected = abba_delta(by_position["A1"], by_position["B1"], by_position["B2"], by_position["A2"])
        expected_deltas.append(expected)
        if not _close(block["delta_j"], expected):
            errors.append(f"{block_where}: stored delta_j does not match members")
        if not _close(deltas[i], expected):
            errors.append(f"{where}: block_deltas_j[{i}] does not match block members")
    if any(not _is_number(d) for d in deltas):
        errors.append(f"{where}: block_deltas_j must all be finite numbers")
        return
    mean = sum(expected_deltas) / n
    if not _close(record["mean_delta_j"], mean):
        errors.append(f"{where}: stored mean_delta_j does not match blocks")
    if not _close(record["max_abs_delta_j"], max(abs(d) for d in expected_deltas)):
        errors.append(f"{where}: stored max_abs_delta_j does not match recomputed value")
    _validate_estimate_math(record, where, expected_deltas, mean, abs(mean), errors)


def _validate_cell(cell, where, errors) -> None:
    if not _check_keys(cell, _CELL_KEYS, where, errors):
        return
    if _check_keys(cell["key"], _KEY_KEYS, f"{where}.key", errors):
        if cell["key"]["window_class"] not in _WINDOW_CLASSES:
            errors.append(f"{where}.key: invalid window_class")
        if not _is_hex(cell["key"]["condition_family_sha256"]):
            errors.append(f"{where}.key: condition_family_sha256 must be 64 lowercase hex chars")
    if _check_keys(cell["eligibility"], _ELIGIBILITY_KEYS, f"{where}.eligibility", errors):
        eligibility = cell["eligibility"]
        if eligibility["use_role"] not in _USE_ROLES:
            errors.append(f"{where}.eligibility: invalid use_role")
        if eligibility["status"] not in _STATUSES:
            errors.append(f"{where}.eligibility: invalid status")
        if not isinstance(eligibility["minimum_claim_n"], int) or isinstance(
            eligibility["minimum_claim_n"], bool
        ) or eligibility["minimum_claim_n"] < GUARD_MINIMUM_N:
            errors.append(f"{where}.eligibility: minimum_claim_n must be an integer >= {GUARD_MINIMUM_N}")
        if not isinstance(eligibility["claim_usable"], bool):
            errors.append(f"{where}.eligibility: claim_usable must be a boolean")

    if cell["absolute"] is not None:
        _validate_absolute(cell["absolute"], f"{where}.absolute", errors)
    if cell["comparative"] is not None:
        _validate_comparative(cell["comparative"], f"{where}.comparative", errors)

    expected_abs = None if cell["absolute"] is None else cell["absolute"].get("guarded_floor_j")
    expected_cmp = None if cell["comparative"] is None else cell["comparative"].get("guarded_floor_j")
    if not _close(cell["floor_abs_j"], expected_abs):
        errors.append(f"{where}: floor_abs_j does not equal the absolute guarded floor")
    if not _close(cell["floor_cmp_j"], expected_cmp):
        errors.append(f"{where}: floor_cmp_j does not equal the comparative guarded floor")
    if expected_abs is not None and expected_cmp is not None:
        if not _close(cell["floor_gate_j"], max(expected_abs, expected_cmp)):
            errors.append(f"{where}: floor_gate_j must equal max(floor_abs_j, floor_cmp_j)")
    elif cell["floor_gate_j"] is not None:
        errors.append(f"{where}: floor_gate_j must be null when either component is null")

    regime = cell["source_regime"]
    if _check_keys(regime, {"stack_identity", "stress_observed"}, f"{where}.source_regime", errors):
        stack = regime["stack_identity"]
        if isinstance(stack, Mapping):
            for field, value in stack.items():
                if field.endswith("_sha256") and not _is_hex(value):
                    errors.append(f"{where}.source_regime.stack_identity.{field}: must be 64 lowercase hex chars")
        else:
            errors.append(f"{where}.source_regime.stack_identity: expected an object")
        _validate_stress_observed(regime["stress_observed"], f"{where}.source_regime.stress_observed", errors)

    if not isinstance(cell["transport_group_id"], str) or not cell["transport_group_id"]:
        errors.append(f"{where}: transport_group_id must be a nonempty string")


def _validate_transport_group(group, where, cells_by_id, errors) -> None:
    if not _check_keys(group, _GROUP_KEYS, where, errors):
        return
    if group["rule_id"] != TRANSPORT_RULE_ID:
        errors.append(f"{where}: rule_id must be {TRANSPORT_RULE_ID!r}")
    if not _is_hex(group["stack_identity_sha256"]):
        errors.append(f"{where}: stack_identity_sha256 must be 64 lowercase hex chars")
    source_ids = group["source_cell_ids"]
    if not isinstance(source_ids, list) or not source_ids:
        errors.append(f"{where}: source_cell_ids must be a nonempty array")
        return
    sources = []
    for cell_id in source_ids:
        cell = cells_by_id.get(cell_id)
        if cell is None:
            errors.append(f"{where}: source cell {cell_id!r} not found in artifact")
            return
        sources.append(cell)
        for field in ("backend", "metric", "window_class"):
            if cell["key"].get(field) != group[field]:
                errors.append(f"{where}: source cell {cell_id!r} {field} differs from group")
        stack_sha = cell["source_regime"]["stack_identity"].get("stack_identity_sha256")
        if stack_sha != group["stack_identity_sha256"]:
            errors.append(f"{where}: source cell {cell_id!r} stack identity differs from group")
    if any(not _is_number(cell.get("floor_gate_j")) for cell in sources):
        errors.append(f"{where}: every source cell needs numeric floors")
        return
    composed = compose_transport_group(sources)
    for field in ("composed_floor_abs_j", "composed_floor_cmp_j", "composed_floor_gate_j"):
        if not _close(group[field], composed[field]):
            errors.append(f"{where}: stored {field} does not match recomputed composition")
    envelope = group["stress_envelope"]
    expected_envelope = composed["stress_envelope"]
    if _check_keys(envelope, set(_ENVELOPE_FIELDS) | {"bound_term_maxima"}, f"{where}.stress_envelope", errors):
        for field in _ENVELOPE_FIELDS:
            if not _close(envelope[field], expected_envelope[field]):
                errors.append(f"{where}.stress_envelope.{field}: does not match recomputed composition")
        stored_terms = envelope["bound_term_maxima"]
        if not isinstance(stored_terms, Mapping) or set(stored_terms) != set(_BOUND_TERMS):
            errors.append(f"{where}.stress_envelope.bound_term_maxima: must contain exactly {sorted(_BOUND_TERMS)}")
        else:
            for term in _BOUND_TERMS:
                if not _close(stored_terms[term], expected_envelope["bound_term_maxima"][term]):
                    errors.append(f"{where}.stress_envelope.bound_term_maxima.{term}: does not match recomputed composition")
    families = group["allowed_consumer_condition_families"]
    if not isinstance(families, list):
        errors.append(f"{where}: allowed_consumer_condition_families must be an array")
    else:
        for i, family in enumerate(families):
            family_where = f"{where}.allowed_consumer_condition_families[{i}]"
            if _check_keys(family, {"condition_family_id", "condition_family_sha256"}, family_where, errors):
                if not _is_hex(family["condition_family_sha256"]):
                    errors.append(f"{family_where}: condition_family_sha256 must be 64 lowercase hex chars")


def validate_floor_artifact(value: Mapping) -> list:
    """Validate a ``joulewise.detection_floor_artifact.v1`` document.

    Returns a list of error strings; an empty list means valid. Recomputes
    every residual, delta, mean, stddev, prediction, unguarded/guarded floor,
    guard factor, cell gate, and transport composition against the stored
    values within ``max(1e-12, 1e-12 * abs(expected))``.
    """
    errors: list = []
    if not _check_keys(value, _TOP_KEYS, "artifact", errors):
        return errors
    if value["schema_version"] != SCHEMA_VERSION:
        errors.append(f"artifact: schema_version must be {SCHEMA_VERSION!r}")
    if value["calibration_scope"] not in _CALIBRATION_SCOPES:
        errors.append("artifact: invalid calibration_scope")
    if not isinstance(value["artifact_id"], str) or not value["artifact_id"]:
        errors.append("artifact: artifact_id must be a nonempty string")
    if value["method"] != build_method_block():
        errors.append("artifact: method block does not match the canonical v1 method")
    if not isinstance(value["provenance"], Mapping):
        errors.append("artifact: provenance must be an object")

    cells = value["cells"]
    if not isinstance(cells, list):
        errors.append("artifact: cells must be an array")
        return errors
    cells_by_id: dict = {}
    seen_keys = set()
    for i, cell in enumerate(cells):
        where = f"cells[{i}]"
        _validate_cell(cell, where, errors)
        if isinstance(cell, Mapping):
            cell_id = cell.get("cell_id")
            if cell_id in cells_by_id:
                errors.append(f"{where}: duplicate cell_id {cell_id!r}")
            elif isinstance(cell_id, str):
                cells_by_id[cell_id] = cell
            key = cell.get("key")
            if isinstance(key, Mapping):
                key_tuple = tuple(sorted((str(k), str(v)) for k, v in key.items()))
                if key_tuple in seen_keys:
                    errors.append(f"{where}: duplicate cell key")
                seen_keys.add(key_tuple)

    groups = value["transport_groups"]
    if not isinstance(groups, list):
        errors.append("artifact: transport_groups must be an array")
        return errors
    group_ids = set()
    for i, group in enumerate(groups):
        where = f"transport_groups[{i}]"
        _validate_transport_group(group, where, cells_by_id, errors)
        if isinstance(group, Mapping):
            group_id = group.get("transport_group_id")
            if group_id in group_ids:
                errors.append(f"{where}: duplicate transport_group_id {group_id!r}")
            group_ids.add(group_id)
    for i, cell in enumerate(cells):
        if isinstance(cell, Mapping) and cell.get("transport_group_id") not in group_ids:
            errors.append(f"cells[{i}]: transport_group_id references no transport group")
    return errors


# ---------------------------------------------------------------------------
# Conservative regime-transport refusal rule (pure)
# ---------------------------------------------------------------------------

_CONSUMER_IDENTITY_FIELDS = ("backend", "metric", "window_class", "stack_identity_sha256")
_CONSUMER_ENVELOPE_FIELDS = _ENVELOPE_FIELDS
_BOUND_TERM_REASONS = {
    "clock_anchor_bound_s": "clock_anchor_harder_than_calibration",
    "interpolation_bound_j": "interpolation_harder_than_calibration",
    "idle_drift_bound_j": "drift_harder_than_calibration",
}


def transport_refusal_reasons(
    consumer: Mapping,
    group: Mapping,
    source_cells_by_id: Optional[Mapping] = None,
) -> tuple:
    """Pure Unit 6.2 transport check; empty tuple means transport is allowed.

    A floor cell/group must refuse to bound a different regime unless every
    predeclared conservative check passes: exact stack identity, predeclared
    condition family, consumer power/duration inside the measured bracket,
    and consumer cadence/clock/interpolation/drift evidence no worse than the
    composed calibration envelope. Missing or unknown consumer evidence
    refuses (``consumer_term_unknown``); nothing is extrapolated and no ad hoc
    margin is added.
    """
    reasons: list = []

    def refuse(reason: str) -> None:
        if reason not in reasons:
            reasons.append(reason)

    # Group completeness / source health (when the source cells are supplied).
    source_ids = group.get("source_cell_ids") or []
    if not source_ids:
        refuse("transport_group_incomplete")
    elif source_cells_by_id is not None:
        for cell_id in source_ids:
            cell = source_cells_by_id.get(cell_id)
            if cell is None:
                refuse("cell_missing")
                continue
            status = cell.get("eligibility", {}).get("status")
            if status == "stale":
                refuse("cell_stale")
            elif status != "claim_ready":
                refuse("cell_not_claim_ready")

    # Exact stack identity; any invariant difference is a stack mismatch.
    for field in _CONSUMER_IDENTITY_FIELDS:
        value = consumer.get(field)
        if value is None:
            refuse("consumer_term_unknown")
        elif value != group.get(field):
            refuse("stack_mismatch")

    # Predeclared condition family (id + hash must both match).
    family_id = consumer.get("condition_family_id")
    family_sha = consumer.get("condition_family_sha256")
    if family_id is None or family_sha is None:
        refuse("consumer_term_unknown")
    else:
        allowed = group.get("allowed_consumer_condition_families") or []
        if not any(
            family.get("condition_family_id") == family_id
            and family.get("condition_family_sha256") == family_sha
            for family in allowed
        ):
            refuse("condition_not_predeclared")

    envelope = group.get("stress_envelope") or {}
    values = {}
    for field in _CONSUMER_ENVELOPE_FIELDS:
        value = consumer.get(field)
        if not _is_number(value):
            refuse("consumer_term_unknown")
        else:
            values[field] = value

    def _have(*fields) -> bool:
        return all(f in values for f in fields)

    if _have("mean_power_w_min", "mean_power_w_max"):
        if values["mean_power_w_min"] < envelope.get("mean_power_w_min", math.inf) or values[
            "mean_power_w_max"
        ] > envelope.get("mean_power_w_max", -math.inf):
            refuse("power_outside_calibrated_envelope")
    if _have("window_duration_s_min", "window_duration_s_max"):
        if values["window_duration_s_min"] < envelope.get("window_duration_s_min", math.inf) or values[
            "window_duration_s_max"
        ] > envelope.get("window_duration_s_max", -math.inf):
            refuse("duration_outside_calibrated_envelope")
    if _have("p95_sample_gap_s_max") and values["p95_sample_gap_s_max"] > envelope.get(
        "p95_sample_gap_s_max", -math.inf
    ):
        refuse("cadence_harder_than_calibration")
    if _have("bracketing_sample_gap_s_max") and values["bracketing_sample_gap_s_max"] > envelope.get(
        "bracketing_sample_gap_s_max", -math.inf
    ):
        refuse("cadence_harder_than_calibration")
    if _have("cadence_ratio_min") and values["cadence_ratio_min"] < envelope.get("cadence_ratio_min", math.inf):
        refuse("cadence_harder_than_calibration")

    group_terms = envelope.get("bound_term_maxima") or {}
    consumer_terms = consumer.get("bound_terms") or {}
    for term, reason in _BOUND_TERM_REASONS.items():
        entry = consumer_terms.get(term)
        if entry is None:
            refuse("consumer_term_unknown")
            continue
        applicability = entry.get("applicability")
        if applicability == "not_applicable":
            continue
        if applicability == "unknown" or not _is_number(entry.get("maximum")):
            refuse("consumer_term_unknown")
            continue
        group_max = group_terms.get(term)
        if group_max is None or entry["maximum"] > group_max:
            refuse(reason)

    assert all(reason in TRANSPORT_REASON_CODES for reason in reasons)
    return tuple(reasons)
