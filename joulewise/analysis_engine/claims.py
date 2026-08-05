"""Fail-closed five-outcome claim evaluation for P2-037.

This module owns outcome precedence only.  Estimation, multiplicity, floor
resolution, and sensitivity calculations remain separate so a missing input
cannot be mistaken for a supported scientific result.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from typing import Any

from joulewise.detection_floor import (
    ATTRIBUTION_FLOOR_SOURCE,
    ATTRIBUTION_LIMIT_CLASS,
    attribution_single_count_discipline,
)
from joulewise.calibration_ledger import REFUSAL_TAXONOMY


CLAIM_OUTCOMES = frozenset(
    {
        "not_estimable",
        "not_resolvable",
        "unresolved",
        "direction_supported",
        "equivalent",
    }
)

# D-057 reducer vocabulary currently present on main.  The analysis engine
# copies these spellings verbatim and never treats an unknown spelling as a
# passing gate.  The three ``anchor``/``clock_anchor`` barriers are the
# 2026-07-19 measurement-soundness-audit additions (D-078): reducer 0.5.1 and
# AXI 0.6.1 mint them for the trace-time-anchor gate, registered here like the
# D-077 environment barriers so stored prechecks carrying them stay readable
# and fail-closed instead of collapsing into ``window_evidence_precheck_missing``.
REDUCER_REASON_CODES = frozenset(
    {
        "nonpositive_window_duration",
        "insufficient_in_window_samples",
        "cadence_ratio_unrecorded",
        "cadence_ratio_below_threshold",
        "clock_bound_unrecorded",
        "clock_bound_exceeds_quarter_window",
        "interpolation_bound_unrecorded",
        "whole_window_drift_allowance_unrecorded",
        "mock_telemetry_claim_ineligible",
        "drift_term_unknown",
        "idle_baseline_unrecorded",
        "cooldown_cap_hit",
        "environment_admission_failed",
        "environment_admission_missing",
        "cpu_admission_unenforced",
        "environment_override",
        "clock_anchor_unresolved",
        "instrument_calibration_missing",
        "instrument_calibration_mismatch",
        "instrument_calibration_invalid",
        "instrument_calibration_stale",
        "calibration_acceptance_bound_stale",
        "instrument_calibration_bracket_missing",
        "thermal_pressure_elevated_in_window",
        "negative_power_sample",
        "post_window_trace_tail_shorter_than_anchor_bound",
        "anchor_energy_envelope_unrecorded",
        "anchor_energy_envelope_exceeds_quarter_metric",
        "token_count_stream_chunk_fallback",
        "pulse_calibration_rollover_gate_timeout",
    }
)

ENGINE_REASON_CODES = frozenset(
    {
        # These originate at the D-109 authenticated-consumer boundary, not
        # in reducer wire output. Preserve the exact ledger taxonomy without
        # misclassifying it as reducer vocabulary.
        *REFUSAL_TAXONOMY,
        "analysis_manifest_invalid",
        "analysis_manifest_not_frozen",
        "order_manifest_hash_mismatch",
        "config_hash_mismatch",
        "bundle_missing",
        "bundle_strict_invalid",
        "bundle_status_not_succeeded",
        "metric_missing_or_nonfinite",
        "paired_block_incomplete",
        "insufficient_complete_blocks",
        "multiplicity_family_incomplete",
        "fixed_n_plan_incomplete",
        "window_evidence_precheck_missing",
        "campaign_cooldown_evidence_missing",
        "idle_window_suspect",
        "idle_window_suspect_unknown",
        "floor_artifact_invalid",
        "floor_row_missing",
        "floor_row_ambiguous",
        "floor_row_stale",
        "floor_transport_inapplicable",
        "floor_abs_missing",
        "floor_cmp_missing",
        "effect_not_above_floor",
        "interpolation_bound_exceeds_floor",
        "interpolation_bound_exceeds_half_effect",
        "deterministic_bound_obscures_direction",
        "required_error_term_unknown",
        "required_covariance_unknown",
        "runtime_token_denominator_required",
        "stop_reason_required",
        "output_policy_required",
        "tokenizer_identity_mismatch",
        "ratio_floor_conversion_undefined",
        "multiplicity_family_incomplete",
        "multiplicity_not_rejected",
        "equivalence_margin_not_above_floor",
        "equivalence_not_supported",
        "randomization_check_insufficient_blocks",
        "randomization_sensitivity_disagrees",
        "loo_verdict_influential",
        "loo_magnitude_influential",
        "outcome_dependent_top_up",
        "legacy_l1_mechanics_only",
        "whole_window_neg8_verdict_missing",
        "whole_window_neg8_verdict_failed",
        "adapter_continuity_evidence_missing",
        "adapter_continuity_failed",
        "cpu_admission_core_missing",
        "cpu_admission_core_failed",
        "whole_window_verdict_coverage_incomplete",
        "whole_window_verdict_provenance_invalid",
        "whole_window_verdict_conflict",
        "calibration_bracket_exceeds_minted_bound",
    }
)

REASON_CODES = REDUCER_REASON_CODES | ENGINE_REASON_CODES

_NOT_ESTIMABLE = frozenset(
    {
        "analysis_manifest_invalid",
        "analysis_manifest_not_frozen",
        "order_manifest_hash_mismatch",
        "floor_artifact_invalid",
        "metric_missing_or_nonfinite",
        "insufficient_complete_blocks",
        "runtime_token_denominator_required",
        "stop_reason_required",
        "output_policy_required",
        "tokenizer_identity_mismatch",
    }
)

_NOT_RESOLVABLE = frozenset(
    {
        "config_hash_mismatch",
        "bundle_missing",
        "bundle_strict_invalid",
        "bundle_status_not_succeeded",
        "whole_window_neg8_verdict_missing",
        "whole_window_neg8_verdict_failed",
        "adapter_continuity_evidence_missing",
        "adapter_continuity_failed",
        "cpu_admission_core_missing",
        "cpu_admission_core_failed",
        "whole_window_verdict_coverage_incomplete",
        "whole_window_verdict_provenance_invalid",
        "whole_window_verdict_conflict",
        "calibration_bracket_exceeds_minted_bound",
        "paired_block_incomplete",
        "fixed_n_plan_incomplete",
        "window_evidence_precheck_missing",
        "campaign_cooldown_evidence_missing",
        "idle_window_suspect",
        "idle_window_suspect_unknown",
        "floor_row_missing",
        "floor_row_ambiguous",
        "floor_row_stale",
        "floor_transport_inapplicable",
        "floor_abs_missing",
        "floor_cmp_missing",
        "effect_not_above_floor",
        "interpolation_bound_exceeds_floor",
        "interpolation_bound_exceeds_half_effect",
        "deterministic_bound_obscures_direction",
        "required_error_term_unknown",
        "required_covariance_unknown",
        "ratio_floor_conversion_undefined",
        "equivalence_margin_not_above_floor",
    }
) | REDUCER_REASON_CODES | set(REFUSAL_TAXONOMY)

_UNRESOLVED = frozenset(
    {
        "multiplicity_not_rejected",
        "equivalence_not_supported",
    }
)

_SENSITIVITY = frozenset(
    {
        "randomization_check_insufficient_blocks",
        "randomization_sensitivity_disagrees",
        "loo_verdict_influential",
        "loo_magnitude_influential",
        "outcome_dependent_top_up",
        "legacy_l1_mechanics_only",
    }
)

_REASON_PRECEDENCE = (_NOT_ESTIMABLE, _NOT_RESOLVABLE, _UNRESOLVED, _SENSITIVITY)


def ordered_reason_codes(reason_codes: Iterable[str]) -> list[str]:
    """Validate, de-duplicate, and deterministically order reason codes."""

    values = set(reason_codes)
    unknown = sorted(values - REASON_CODES)
    if unknown:
        raise ValueError(f"unknown claim reason code(s): {', '.join(unknown)}")
    result: list[str] = []
    remaining = set(values)
    for group in _REASON_PRECEDENCE:
        selected = sorted(remaining & group)
        result.extend(selected)
        remaining.difference_update(selected)
    result.extend(sorted(remaining))
    return result


def _finite(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def _interval(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, Mapping):
        return None
    lower = _finite(value.get("lower"))
    upper = _finite(value.get("upper"))
    if lower is None or upper is None or lower > upper:
        return None
    return lower, upper


def _inside_equivalence(interval: tuple[float, float], margin: float) -> bool:
    return interval[0] > -margin and interval[1] < margin


def evaluate_claim(
    *,
    estimate: float | None,
    metrology_aware_ci95: Mapping[str, Any] | None,
    decision_interval: Mapping[str, Any] | None,
    floor_gate_j: float | None,
    adjusted_rejected: bool,
    base_reason_codes: Iterable[str] = (),
    equivalence: Mapping[str, Any] | None = None,
    claim_role: str = "primary",
    confirmatory_status: str = "confirmatory",
    evidence_class: str = "current",
    sensitivity_blocking: bool = False,
    floor_metadata: Mapping[str, Any] | None = None,
    hypothesized_direction: str | None = None,
) -> dict[str, Any]:
    """Apply the adjudicated five-outcome precedence.

    ``adjusted_rejected`` is the frozen-family Holm/BH decision.  Equivalence
    callers pass their adjusted TOST decision through the same argument.
    Sensitivity and D-062 demotion can lower the claim ceiling without erasing
    the point outcome.
    """

    reasons = set(base_reason_codes)
    numeric_estimate = _finite(estimate)
    metrology_interval = _interval(metrology_aware_ci95)
    decision = _interval(decision_interval)
    floor = _finite(floor_gate_j)
    attribution_metadata: dict[str, Any] | None = None
    if floor_metadata is not None:
        expected_keys = {
            "floor_limit_class",
            "floor_source",
            "point_floor_diagnostics",
            "single_count_discipline",
        }
        if (
            not isinstance(floor_metadata, Mapping)
            or set(floor_metadata) != expected_keys
            or floor_metadata.get("floor_limit_class")
            != ATTRIBUTION_LIMIT_CLASS
            or floor_metadata.get("floor_source") != ATTRIBUTION_FLOOR_SOURCE
            or not isinstance(
                floor_metadata.get("point_floor_diagnostics"), Mapping
            )
            or floor_metadata.get("single_count_discipline")
            != attribution_single_count_discipline()
        ):
            reasons.add("floor_artifact_invalid")
        else:
            attribution_metadata = {
                "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
                "floor_source": ATTRIBUTION_FLOOR_SOURCE,
                "published_floor_j": floor,
                "point_floor_diagnostics": dict(
                    floor_metadata["point_floor_diagnostics"]
                ),
                "single_count_discipline": attribution_single_count_discipline(),
            }

    if numeric_estimate is None or metrology_interval is None or decision is None:
        reasons.add("metric_missing_or_nonfinite")
    if floor is None:
        reasons.add("floor_abs_missing")
        reasons.add("floor_cmp_missing")
    elif floor < 0.0:
        reasons.add("floor_artifact_invalid")

    outcome: str
    if reasons & _NOT_ESTIMABLE:
        outcome = "not_estimable"
    else:
        assert numeric_estimate is not None
        assert metrology_interval is not None
        assert decision is not None
        if floor is None or reasons & _NOT_RESOLVABLE:
            outcome = "not_resolvable"
        else:
            if equivalence is None and abs(numeric_estimate) <= floor:
                reasons.add("effect_not_above_floor")

            if equivalence is not None:
                margin = _finite(equivalence.get("margin")) if isinstance(equivalence, Mapping) else None
                method = equivalence.get("method") if isinstance(equivalence, Mapping) else None
                if margin is None or margin <= 0.0 or method != "tost_v1":
                    reasons.add("equivalence_not_supported")
                elif margin <= floor:
                    reasons.add("equivalence_margin_not_above_floor")

            if reasons & _NOT_RESOLVABLE:
                outcome = "not_resolvable"
            elif reasons & _UNRESOLVED:
                outcome = "unresolved"
            elif equivalence is not None:
                margin = float(equivalence["margin"])
                if (
                    not _inside_equivalence(metrology_interval, margin)
                    or not _inside_equivalence(decision, margin)
                    or not adjusted_rejected
                ):
                    reasons.add("equivalence_not_supported")
                    outcome = "unresolved"
                else:
                    outcome = "equivalent"
            elif (
                metrology_interval[0] <= 0.0 <= metrology_interval[1]
                or decision[0] <= 0.0 <= decision[1]
            ):
                if not (metrology_interval[0] <= 0.0 <= metrology_interval[1]):
                    reasons.add("deterministic_bound_obscures_direction")
                    outcome = "not_resolvable"
                else:
                    outcome = "unresolved"
            elif not adjusted_rejected:
                reasons.add("multiplicity_not_rejected")
                outcome = "unresolved"
            else:
                outcome = "direction_supported"

    direction = None
    if outcome == "direction_supported" and numeric_estimate is not None:
        direction = "positive" if numeric_estimate > 0.0 else "negative"

    demoted = confirmatory_status != "confirmatory"
    legacy = evidence_class == "legacy_l1"
    sensitivity_reasons = reasons & {
        "randomization_sensitivity_disagrees",
        "loo_verdict_influential",
        "randomization_check_insufficient_blocks",
    }
    direction_matches_registration = bool(
        hypothesized_direction not in {"positive", "negative"}
        or outcome == "equivalent"
        or direction == hypothesized_direction
    )
    claim_ready = bool(
        outcome in {"direction_supported", "equivalent"}
        and claim_role in {"primary", "secondary"}
        and not demoted
        and not legacy
        and not sensitivity_blocking
        and not sensitivity_reasons
        and direction_matches_registration
    )
    ceiling = "L2" if claim_ready else "L1"

    ordered = ordered_reason_codes(reasons)
    result = {
        "outcome": outcome,
        "direction": direction,
        "reason_codes": ordered,
        "claim_ready_for_l2_l3": claim_ready,
        "claim_level_ceiling": ceiling,
    }
    if attribution_metadata is not None:
        result["floor_limit"] = attribution_metadata
    return result


__all__ = [
    "CLAIM_OUTCOMES",
    "ENGINE_REASON_CODES",
    "REASON_CODES",
    "REDUCER_REASON_CODES",
    "evaluate_claim",
    "ordered_reason_codes",
]
