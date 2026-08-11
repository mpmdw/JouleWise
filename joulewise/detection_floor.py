"""P2-039 detection-floor calculator (D-054 false-effect guard).

Implements the accepted P2-039 operational spec
(``docs/specs/c027/p2-039_floor_artifact.md``):

- the absolute and comparative D-054 false-effect floors with the frozen
  small-sample guard factor;
- the exact ABBA block delta ``(B1 + B2 - A1 - A2) / 2``;
- emit/validate for the versioned ``joulewise.detection_floor_artifact.v2``
  calculation records; and
- the pure conservative regime-transport refusal rule
  (``same_stack_componentwise_worst_case.v1``).

The artifact's compact bundle pins use :func:`complete_bundle_sha256`.  The
analysis input loader composes that primitive with strict validation, metric
re-extraction, and campaign-order verification before a floor is consumable.
The calculator still has no CLI or ``reduce.py`` hook.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import stat
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Mapping, Optional, Sequence

from joulewise.aggregate import student_t_critical_95
from joulewise.authentication_io import (
    read_authentication_input,
    sha256_authentication_input,
)
from joulewise.whole_window import (
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    MINTED_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
)

__all__ = [
    "SCHEMA_VERSION",
    "FLOOR_METRIC_CATALOG",
    "METHOD_ID",
    "GUARD_RULE_ID",
    "TRANSPORT_RULE_ID",
    "GUARD_REFERENCE_N",
    "GUARD_MINIMUM_N",
    "MAX_EXACT_ADMISSIBLE_CORNER_N",
    "ATTRIBUTION_LIMIT_CLASS",
    "ATTRIBUTION_FLOOR_SOURCE",
    "SINGLE_COUNT_DISCIPLINE_ID",
    "COMMON_MODE_ESTIMATOR_ID",
    "COMMON_MODE_ESTIMATOR_VERSION",
    "COMMON_MODE_PARAMETER_SHA256",
    "COMMON_MODE_REFUSAL_CODES",
    "TRANSPORT_REASON_CODES",
    "STACK_IDENTITY_DOMAIN",
    "CONDITION_FAMILY_DOMAIN",
    "FloorEstimate",
    "CommonModeEstimatorRefusal",
    "small_sample_guard_factor",
    "admissible_set_uncertainty_dominates_point_floor",
    "attribution_single_count_discipline",
    "absolute_false_effect_floor",
    "comparative_false_effect_floor",
    "two_shared_edge_common_mode_registration",
    "validate_common_mode_estimator_registration",
    "registered_common_mode_operative_bound",
    "two_shared_edge_common_mode_floor",
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
    "canonical_domain_sha256",
    "complete_bundle_sha256",
    "validate_floor_metric_window_class",
]

SCHEMA_VERSION = "joulewise.detection_floor_artifact.v2"
METHOD_ID = "d054_false_effect_guard.v1"
GUARD_RULE_ID = "residual_df_ratio_to_n10.v1"
TRANSPORT_RULE_ID = "same_stack_componentwise_worst_case.v1"
STACK_IDENTITY_DOMAIN = "joulewise.stack_identity.v1"
CONDITION_FAMILY_DOMAIN = "joulewise.condition_family.v1"

# Frozen operational safety factor, ACCEPTED by C-028 ADJUDICATION.md:
# g(n) = max(1, sqrt((10-1)/(n-1))) for n >= 5. It is the square root of
# the residual-degrees-of-freedom deficit relative to the n=10 design point.
# It is not a tolerance, percentile-coverage, confidence, or power guarantee.
GUARD_REFERENCE_N = 10
GUARD_MINIMUM_N = 5
MAX_EXACT_ADMISSIBLE_CORNER_N = 16
ATTRIBUTION_LIMIT_CLASS = "attribution_limited"
ATTRIBUTION_FLOOR_SOURCE = "E_clock_anchor_shift_bound_j"
SINGLE_COUNT_DISCIPLINE_ID = "attribution_floor_plus_claim_side_bound.v1"
COMMON_MODE_ESTIMATOR_ID = "d124_two_shared_edge_common_mode.v1"
COMMON_MODE_ESTIMATOR_VERSION = "v1"
COMMON_MODE_REFUSAL_CODES = (
    "common_mode_allowance_application_invalid",
    "common_mode_nonseparable_window_domain",
    "common_mode_precondition_failed",
    "common_mode_zero_point_divergence_out_of_domain",
)
_MAX_FLOOR_J = 1e6
_MAX_RECOMPUTATION_ABS_DELTA_J = 1e-6

_COMMON_MODE_EVIDENCE_REFERENCE = (
    "docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md"
)
_COMMON_MODE_COVARIANCE_TREATMENT = (
    "two_shared_edges_plus_bundle_specific_adversarial_terms"
)
_COMMON_MODE_PARAMETER_DOMAIN = "joulewise.d124_common_mode_parameters.v1"
_COMMON_MODE_PARAMETERS = {
    "estimator_id": COMMON_MODE_ESTIMATOR_ID,
    "abba_positions": ["A1", "B1", "B2", "A2"],
    "abba_coefficients": ["-0.5", "0.5", "0.5", "-0.5"],
    "shared_parameters": ["onset_shift_s", "offset_shift_s"],
    "shared_candidate_rule": (
        "interval_support_edges_union_plus_zero_and_operative_bounds"
    ),
    "shared_extrema_rule": (
        "separable_onset_offset_excursion_composition_about_swept_zero_point_"
        "on_strict_noncollapse_domain"
    ),
    "shared_extrema_zero_point_rule": (
        "zero_point_contrast_is_an_explicit_registered_input_present_by_exact_"
        "equality_in_both_sweeps_never_recovered_by_tolerance"
    ),
    "shared_extrema_centre_offset_rule": (
        "abs_zero_point_minus_block_delta_added_outward_exactly_once_"
        "separate_from_the_numerical_enclosure"
    ),
    "shared_extrema_domain_precondition": (
        "all_admitted_abba_member_windows_outward_rounding_prove_"
        "start_plus_bound_lt_end_minus_bound"
    ),
    "shared_extrema_domain_refusal_reason": (
        "common_mode_nonseparable_window_domain"
    ),
    "shared_extrema_numerical_enclosure_rule": (
        "outward_enclosure_64u_times_floored_member_envelope_integral_sum"
    ),
    "shared_extrema_zero_point_divergence_refusal_reason": (
        "common_mode_zero_point_divergence_out_of_domain"
    ),
    "bundle_residual_rule": (
        "math.fsum(per_bundle_adversarial_half_width_j)/2"
    ),
    "allowance_rule": (
        "endpoint_max_plus_one_never_zero_allowance_inside_shared_bound"
    ),
}
COMMON_MODE_PARAMETER_SHA256 = hashlib.sha256(
    _COMMON_MODE_PARAMETER_DOMAIN.encode("utf-8")
    + b"\0"
    + json.dumps(
        _COMMON_MODE_PARAMETERS,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
).hexdigest()

_CALIBRATION_SCOPES = (
    "window_a",
    "window_b_revalidation",
    "production_window",
    "smoke",
)
_CONSUMPTION_SEMANTICS_IDS = {
    MINTED_CONSUMPTION_SEMANTICS_ID,
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
}
_FLOOR_MINT_PINSET_SCHEMA_VERSION = "joulewise.floor_mint_pinset.v1"
_FLOOR_MINT_PINSET_SCHEMA_VERSION_V2 = "joulewise.floor_mint_pinset.v2"
_FLOOR_MINT_TOOL_VERSION_V2 = "joulewise.floor_mint.generalized.v2"
_FLOOR_MINT_PINSET_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "scripts" / "floor_mint_pinsets"
)
_FLOOR_MINT_PINSET_KEYS = {
    "schema_version",
    "mint_tool_version",
    "plan",
    "artifact",
    "cell",
    "absolute",
    "comparative",
}
_FLOOR_MINT_PLAN_PIN_KEYS = {
    "plan_id",
    "sha256",
    "declared_calibration_scope",
    "artifact_calibration_scope",
}
_FLOOR_MINT_ARTIFACT_PIN_KEYS = {
    "cell_id",
    "transport_group_id",
    "source_class",
}
_FLOOR_MINT_CELL_PIN_KEYS = {
    "condition_family_id",
    "condition_family_sha256",
    "metric",
    "window_class",
    "target_precheck_path",
    "operative_floor_six_decimal",
}
_FLOOR_MINT_COMPONENT_PIN_KEYS = {
    "evidence_root_id",
    "calibration_cell_id",
    "evaluation_basis_sha256",
    "evaluation_basis_members",
    "extraction_spec_members",
    "expected_n",
    "drift_allowance_j",
    "order_manifest_id",
}
FLOOR_METRIC_CATALOG = (
    "gross_energy_j",
    "energy_request_j",
    "idle_subtracted_energy_j",
    "phase_energy_j.tokenize",
    "phase_energy_j.prefill",
    "phase_energy_j.decode",
    "phase_energy_j.serialize",
    "phase_energy_j.transfer",
    "phase_energy_j.deserialize",
)
# DATA FOR A FUTURE GATE, NOT ENFORCEMENT: source_class records how the
# artifact's source evidence was obtained, but it does not make that evidence
# claim-eligible. The enforcement counterpart is a separate registered task:
# claims.evaluate_claim must take a required, non-defaulting source_class.
_SOURCE_CLASSES = ("prospective", "retrospective", "synthetic")
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
_STACK_IDENTITY_FIELDS = (
    "hardware_unit",
    "os_version",
    "runtime_version",
    "kernel_library",
    "model_artifact_sha256",
    "quantization",
    "tokenizer_identity",
    "sampler_output_policy",
    "batching_concurrency_policy",
    "measurement_boundary_label",
    "telemetry_backend",
)
_STACK_IDENTITY_KEYS = set(_STACK_IDENTITY_FIELDS)
_CONDITION_FAMILY_KEYS = {
    "condition_family_id",
    "condition_family_definition",
    "condition_family_sha256",
}
_IDLE_DRIFT_GUARD_KEYS = {
    "calibration_status",
    "method",
    "guard_w",
    "n_bundles",
    "bundle_sha256",
    "cell_id",
    "artifact_sha256",
}
_IDLE_DRIFT_GUARD_METHOD = "p2_015_prediction_guard_v1"

CALIBRATION_BUNDLE_HASH_DOMAIN = "joulewise.calibration_bundle.v1"

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


def validate_floor_metric_window_class(
    metric: object,
    window_class: object,
) -> tuple[str, str]:
    """Return a governed floor metric/window pair or raise ``ValueError``."""

    if not isinstance(metric, str) or not metric:
        raise ValueError("cell metric must be a nonempty string")
    window_classes = ("request", "phase")
    if window_class not in window_classes:
        raise ValueError(
            f"cell window_class must be one of {window_classes}, "
            f"got {window_class!r}"
        )
    if metric not in FLOOR_METRIC_CATALOG:
        raise ValueError(
            f"invalid metric {metric!r}: not in FLOOR_METRIC_CATALOG"
        )
    expected_window_class = (
        "phase" if metric.startswith("phase_energy_j.") else "request"
    )
    if window_class != expected_window_class:
        if expected_window_class == "phase":
            raise ValueError(
                f"phase metric {metric!r} requires window_class 'phase', "
                f"got {window_class!r}"
            )
        raise ValueError(
            "phase cells extract only catalogued phase_energy_j metrics, "
            f"got {metric!r}"
        )
    return metric, str(window_class)


def attribution_single_count_discipline() -> dict[str, object]:
    """Return the D-078 clause-11 non-removable two-role composition rule."""

    return {
        "rule_id": SINGLE_COUNT_DISCIPLINE_ID,
        "effective_clearable_effect_formula": "floor_j + claim_side_bound_j",
        "floor_role": "calibration_false_effect_bound",
        "claim_side_bound_role": "claim_measurement_uncertainty_bound",
        "claim_side_bound_source": ATTRIBUTION_FLOOR_SOURCE,
        "both_terms_required": True,
        "apparent_double_count_removal_forbidden": True,
        "statement": (
            "effective clearable effect = floor + claim-side bound; "
            "neither term may be removed as an apparent double count"
        ),
    }


def canonical_domain_sha256(domain: str, value: Mapping) -> str:
    """Hash canonical JSON under a NUL-separated UTF-8 domain prefix."""
    canonical = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(domain.encode("utf-8") + b"\0" + canonical).hexdigest()


def complete_bundle_sha256(path: Path) -> str:
    """Hash every regular file in a completed calibration bundle.

    Relative POSIX paths are sorted; each file contributes its byte SHA-256
    and size. Symlinks and special files fail closed. Directory metadata and
    absolute paths are excluded so relocating immutable bytes preserves their
    identity.
    """

    root = Path(path)
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"calibration bundle is not a real directory: {root}")
    records: list[dict[str, object]] = []
    try:
        candidates = sorted(
            root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()
        )
    except OSError as exc:
        raise ValueError(f"cannot enumerate calibration bundle {root}: {exc}") from exc
    for candidate in candidates:
        try:
            file_stat = candidate.lstat()
            mode = file_stat.st_mode
        except OSError as exc:
            raise ValueError(
                f"cannot inspect calibration bundle member {candidate}: {exc}"
            ) from exc
        if stat.S_ISDIR(mode):
            continue
        relative = candidate.relative_to(root).as_posix()
        if not stat.S_ISREG(mode):
            raise ValueError(
                f"calibration bundle member is not a regular file: {relative}"
            )
        try:
            digest = sha256_authentication_input(
                candidate,
                label=f"complete bundle {root.name} member {relative}",
            )
        except OSError as exc:
            raise ValueError(
                f"cannot read calibration bundle member {relative}: {exc}"
            ) from exc
        records.append(
            {
                "path": relative,
                "sha256": digest,
                "size_bytes": file_stat.st_size,
            }
        )
    if not records:
        raise ValueError(f"calibration bundle contains no regular files: {root}")
    rendered = json.dumps(
        records,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(
        CALIBRATION_BUNDLE_HASH_DOMAIN.encode("utf-8") + b"\0" + rendered
    ).hexdigest()


# ---------------------------------------------------------------------------
# Pure D-054 math
# ---------------------------------------------------------------------------


class CommonModeEstimatorRefusal(ValueError):
    """Typed fail-closed refusal from the registered D-124 estimator."""

    def __init__(self, reason: str, detail: str) -> None:
        if reason not in COMMON_MODE_REFUSAL_CODES:
            raise ValueError(f"unregistered common-mode refusal reason: {reason}")
        self.reason = reason
        self.detail = detail
        super().__init__(f"{reason}: {detail}")


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
    admissible_half_widths_j: tuple[float, ...] = ()
    corner_widened_unguarded_floor_j: Optional[float] = None
    corner_widened_guarded_floor_j: Optional[float] = None
    estimator_registration: Mapping[str, object] | None = None


def two_shared_edge_common_mode_registration() -> dict[str, object]:
    """Return the stable, pin-ready registration for the D-124 candidate."""

    treatment = _COMMON_MODE_COVARIANCE_TREATMENT
    return {
        "estimator_id": COMMON_MODE_ESTIMATOR_ID,
        "version": COMMON_MODE_ESTIMATOR_VERSION,
        "parameter_sha256": COMMON_MODE_PARAMETER_SHA256,
        "status": "registered_candidate",
        "transfer_assumption": {
            "assumption_id": "d124_block_bracket_edges_shared_within_abba.v1",
            "statement": (
                "Within one authenticated ABBA calibration bracket, onset and "
                "offset fiducial terms are shared edges while bundle-specific "
                "residual terms remain adversarial."
            ),
            "evidence_reference": _COMMON_MODE_EVIDENCE_REFERENCE,
        },
        "stationarity_transfer_assumption": {
            "assumption_id": (
                "d124_block_timescale_shared_edges_stationarity_transfer_v1"
            ),
            "statement": (
                "The shared onset and offset edge treatment calibrated on floor "
                "blocks transfers unchanged to the consuming contrast at the "
                "same block timescale."
            ),
            "evidence_reference": _COMMON_MODE_EVIDENCE_REFERENCE,
            "evidentiary_limit": (
                "The historical corpus records bounds, not realized "
                "member-level boundary errors."
            ),
        },
        "covariance_treatment": treatment,
        "calibration_treatment": treatment,
        "consuming_contrast_treatment": treatment,
        "identical_covariance_treatment_required": True,
        "allowance": {
            "rule": "max(observed_drift_s,bracket_screen_s)",
            "embedding_count": 1,
            "embedded_in": "shared_operative_bound_s",
        },
        "issued_acceptance_artifact_reopened": False,
        "raw_calibration_corpus_voided": False,
    }


def validate_common_mode_estimator_registration(value: object) -> bool:
    """Accept only the complete, parameter-hashed D-124 registration."""

    return (
        isinstance(value, Mapping)
        and dict(value) == two_shared_edge_common_mode_registration()
    )


def _common_mode_refuse(reason: str, detail: str) -> None:
    raise CommonModeEstimatorRefusal(reason, detail)


def _common_mode_finite(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def _common_mode_window_is_strictly_noncollapsed(
    start_s: object,
    end_s: object,
    shared_edge_bound_s: object,
) -> bool:
    """Prove a member window remains noncollapsed over both shared edges."""

    start = _common_mode_finite(start_s)
    end = _common_mode_finite(end_s)
    bound = _common_mode_finite(shared_edge_bound_s)
    if start is None or end is None or bound is None or bound <= 0.0:
        return False
    latest_start = math.nextafter(start + bound, math.inf)
    earliest_end = math.nextafter(end - bound, -math.inf)
    return latest_start < earliest_end


def _common_mode_outward(value: float, direction: float) -> float:
    """Add a negligible four-ULP enclosure for composed float extrema."""

    for _ in range(4):
        value = math.nextafter(value, direction)
    return value


def registered_common_mode_operative_bound(
    calibration_bracket: object,
) -> float:
    """Recover the shared bound only when D-102 was embedded exactly once.

    The authenticated bracket is the arithmetic authority.  A missing,
    zero, duplicated, or differently embedded allowance is a typed refusal;
    callers may not silently substitute the independent-member estimator.
    """

    reason = "common_mode_allowance_application_invalid"
    if not isinstance(calibration_bracket, Mapping):
        _common_mode_refuse(reason, "an authenticated calibration bracket is required")
    acceptance = calibration_bracket.get("acceptance")
    allowance_record = (
        acceptance.get("allowance") if isinstance(acceptance, Mapping) else None
    )
    endpoint = _common_mode_finite(
        calibration_bracket.get("endpoint_max_b_fiducial_s")
    )
    allowance = _common_mode_finite(
        calibration_bracket.get("calibration_drift_allowance_s")
    )
    b_fiducial = _common_mode_finite(
        calibration_bracket.get("b_fiducial_s")
    )
    operative_b_fiducial = _common_mode_finite(
        calibration_bracket.get("operative_b_fiducial_s")
    )
    both_operative_aliases_present = (
        "b_fiducial_s" in calibration_bracket
        and "operative_b_fiducial_s" in calibration_bracket
    )
    operative_aliases_agree = (
        not both_operative_aliases_present
        or (
            b_fiducial is not None
            and operative_b_fiducial is not None
            and math.isclose(
                b_fiducial,
                operative_b_fiducial,
                rel_tol=0.0,
                abs_tol=1e-12,
            )
        )
    )
    operative = (
        b_fiducial if b_fiducial is not None else operative_b_fiducial
    )
    raw_recorded_allowance = (
        allowance_record.get("value_s")
        if isinstance(allowance_record, Mapping)
        else None
    )
    try:
        recorded_allowance = float(raw_recorded_allowance)
    except (TypeError, ValueError):
        recorded_allowance = None
    if recorded_allowance is not None and not math.isfinite(recorded_allowance):
        recorded_allowance = None
    if (
        calibration_bracket.get("status") != "passed"
        or endpoint is None
        or endpoint < 0.0
        or allowance is None
        or allowance <= 0.0
        or operative is None
        or recorded_allowance is None
        or not isinstance(allowance_record, Mapping)
        or allowance_record.get("rule")
        != "max(observed_drift_s,bracket_screen_s)"
        or isinstance(allowance_record.get("embedding_count"), bool)
        or allowance_record.get("embedding_count") != 1
        or allowance_record.get("embedded_in") != "b_fiducial_s"
        or not operative_aliases_agree
        or not math.isclose(
            recorded_allowance, allowance, rel_tol=0.0, abs_tol=1e-12
        )
        or not math.isclose(
            operative, endpoint + allowance, rel_tol=0.0, abs_tol=1e-12
        )
    ):
        _common_mode_refuse(
            reason,
            "the never-zero allowance must appear exactly once in the shared operative bound",
        )
    return operative


def small_sample_guard_factor(n: int) -> float:
    """Frozen, accepted operational safety factor g(n) for n >= 5."""
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
    # math.fsum: the squared-residual reduction must be identical across
    # supported interpreters (builtins.sum float summation changed in
    # CPython 3.12); exact-golden fixtures pin this value bit-for-bit.
    s = math.sqrt(math.fsum((d - dev_mean) ** 2 for d in deviations) / (n - 1))
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


def _admissible_widths(
    widths_j: Sequence[float] | None, *, expected_n: int
) -> list[float]:
    if widths_j is None:
        raise ValueError("admissible-set half-widths are required")
    widths = _clean_values(widths_j, "admissible-set half-widths")
    if len(widths) != expected_n:
        raise ValueError("admissible-set half-width count must match point estimates")
    if any(value < 0.0 for value in widths):
        raise ValueError("admissible-set half-widths must be >= 0")
    return widths


def _linear_corner_widened_max(
    point_values_j: Sequence[float], linear_half_widths_j: Sequence[float]
) -> float:
    """Exact maximum magnitude over independent linear member intervals."""

    if len(point_values_j) != len(linear_half_widths_j):
        raise ValueError("linear half-width count must match point values")
    return max(
        abs(point) + width
        for point, width in zip(point_values_j, linear_half_widths_j, strict=True)
    )


def _apply_admissible_set_guard(
    estimate: FloorEstimate,
    uncertainty_floor_j: float,
    admissible_half_widths_j: Sequence[float],
) -> FloorEstimate:
    """Raise a point-estimate floor to cover admitted energy sets.

    The D-054 scatter calculation remains visible in its component fields, but
    the operative unguarded/guarded floors can never be smaller than the
    largest attainable magnitude of the linear residual/contrast. Otherwise a
    near-identical set of point estimates could claim a millijoule floor while
    each member is scientifically compatible with tens of joules of anchor
    displacement.
    """

    unguarded = max(estimate.unguarded_floor_j, uncertainty_floor_j)
    guarded = (
        estimate.guard_factor * unguarded
        if estimate.guard_factor is not None
        else None
    )
    return FloorEstimate(
        kind=estimate.kind,
        n=estimate.n,
        mean_j=estimate.mean_j,
        deviations_j=estimate.deviations_j,
        sample_stddev_j=estimate.sample_stddev_j,
        max_abs_deviation_j=estimate.max_abs_deviation_j,
        t_critical=estimate.t_critical,
        prediction_component_j=estimate.prediction_component_j,
        unguarded_floor_j=unguarded,
        guard_factor=estimate.guard_factor,
        guarded_floor_j=guarded,
        admissible_half_widths_j=tuple(admissible_half_widths_j),
        corner_widened_unguarded_floor_j=unguarded,
        corner_widened_guarded_floor_j=guarded,
    )


def _point_floor_diagnostic(estimate: FloorEstimate) -> dict[str, object]:
    point_unguarded = max(
        estimate.max_abs_deviation_j,
        estimate.prediction_component_j,
    )
    point_guarded = (
        estimate.guard_factor * point_unguarded
        if estimate.guard_factor is not None
        else None
    )
    return {
        "label": "repeatability_diagnostic",
        "published_claim_floor": False,
        "unguarded_floor_j": point_unguarded,
        "guard_factor": estimate.guard_factor,
        "guarded_floor_j": point_guarded,
    }


def admissible_set_uncertainty_dominates_point_floor(
    estimate: FloorEstimate,
) -> bool:
    """Classify the registered D-078 condition without turning it into refusal.

    This reproduces the original terminal gate's exact comparison: the
    largest linear residual/contrast admitted by the member anchor envelopes
    is compared with the guarded point-only false-effect floor.  The complete
    corner-maximized floor remains the published number.
    """

    widths = estimate.admissible_half_widths_j
    if not widths or not any(widths):
        return False
    diagnostic = _point_floor_diagnostic(estimate)
    point_gate = diagnostic["guarded_floor_j"]
    if point_gate is None:
        point_gate = diagnostic["unguarded_floor_j"]
    if estimate.kind == "absolute":
        n = estimate.n
        width_sum = math.fsum(widths)
        uncertainty_max = max(
            abs(residual)
            + width * (n - 1) / n
            + (width_sum - width) / n
            for residual, width in zip(
                estimate.deviations_j, widths, strict=True
            )
        )
    elif estimate.kind == "comparative":
        uncertainty_max = _linear_corner_widened_max(
            estimate.deviations_j, widths
        )
    else:
        raise ValueError(f"unknown floor kind: {estimate.kind!r}")
    return uncertainty_max > point_gate


def _add_attribution_limit_metadata(
    record: dict,
    estimate: FloorEstimate,
) -> dict:
    if not admissible_set_uncertainty_dominates_point_floor(estimate):
        return record
    return {
        **record,
        "floor_source": ATTRIBUTION_FLOOR_SOURCE,
        "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
        "point_floor_diagnostic": _point_floor_diagnostic(estimate),
        "single_count_discipline": attribution_single_count_discipline(),
    }


def _corner_maximized_unguarded_floor(
    point_values_j: Sequence[float],
    half_widths_j: Sequence[float],
    *,
    kind: str,
) -> float:
    """Return the exact full D-054 floor maximum over an interval box.

    The maximum of the complete floor (maximum absolute term, sample
    standard deviation, and Student-t prediction term) occurs at a vertex of
    the independent member/delta interval box. Enumeration is deliberately
    capped: callers must refuse rather than substitute an approximation once
    the governed exact calculation is too large.
    """

    if len(point_values_j) != len(half_widths_j):
        raise ValueError("admissible-set half-width count must match point estimates")
    if not any(half_widths_j):
        mean = sum(point_values_j) / len(point_values_j)
        deviations = (
            [value - mean for value in point_values_j]
            if kind == "absolute"
            else list(point_values_j)
        )
        prediction_extra = 0.0 if kind == "absolute" else abs(mean)
        return _floor_estimate(
            kind, deviations, mean, prediction_extra
        ).unguarded_floor_j
    if len(point_values_j) > MAX_EXACT_ADMISSIBLE_CORNER_N:
        raise ValueError(
            "exact admissible-set corner enumeration is capped at "
            f"n={MAX_EXACT_ADMISSIBLE_CORNER_N}"
        )

    maximum = 0.0
    for mask in range(1 << len(point_values_j)):
        corner = [
            point + (width if mask & (1 << index) else -width)
            for index, (point, width) in enumerate(
                zip(point_values_j, half_widths_j, strict=True)
            )
        ]
        mean = sum(corner) / len(corner)
        deviations = (
            [value - mean for value in corner]
            if kind == "absolute"
            else corner
        )
        prediction_extra = 0.0 if kind == "absolute" else abs(mean)
        maximum = max(
            maximum,
            _floor_estimate(
                kind, deviations, mean, prediction_extra
            ).unguarded_floor_j,
        )
    return maximum


def absolute_false_effect_floor(
    values_j: Sequence[float],
    *,
    admissible_half_widths_j: Sequence[float],
) -> FloorEstimate:
    """D-054 absolute floor, widened by member admissible-set uncertainty."""
    values = _clean_values(values_j, "energies")
    mean = sum(values) / len(values)
    residuals = [v - mean for v in values]
    estimate = _floor_estimate("absolute", residuals, mean, 0.0)
    widths = _admissible_widths(
        admissible_half_widths_j, expected_n=len(values)
    )
    n = len(values)
    total_width = math.fsum(widths)
    # For residual r_i = x_i - mean(x), the independent interval coefficients
    # are (n-1)/n on member i and -1/n on every other member.  Linear extrema
    # over a box occur exactly at corners, so this is an equality, not a bound.
    residual_widths = [
        width * (n - 1) / n + (total_width - width) / n
        for width in widths
    ]
    # Keep the exact linear-residual result as a cheap lower bound, but the
    # operative floor is the maximum of the COMPLETE D-054 floor at a joint
    # interval-box corner. In particular, uncertainty can maximize the
    # Student-t prediction component at a different corner.
    uncertainty_floor = max(
        _linear_corner_widened_max(residuals, residual_widths),
        _corner_maximized_unguarded_floor(values, widths, kind="absolute"),
    )
    return _apply_admissible_set_guard(estimate, uncertainty_floor, widths)


def comparative_false_effect_floor(
    block_deltas_j: Sequence[float],
    *,
    admissible_half_widths_j: Sequence[float],
) -> FloorEstimate:
    """D-054 comparative false-effect floor over ABBA block deltas.

    The prediction component includes ``abs(mean_delta)`` — deltas are never
    re-centered before the floor is computed.
    """
    deltas = _clean_values(block_deltas_j, "block deltas")
    mean = sum(deltas) / len(deltas)
    estimate = _floor_estimate("comparative", deltas, mean, abs(mean))
    widths = _admissible_widths(
        admissible_half_widths_j, expected_n=len(deltas)
    )
    uncertainty_floor = max(
        _linear_corner_widened_max(deltas, widths),
        _corner_maximized_unguarded_floor(deltas, widths, kind="comparative"),
    )
    return _apply_admissible_set_guard(estimate, uncertainty_floor, widths)


def two_shared_edge_common_mode_floor(
    block_deltas_j: Sequence[float],
    *,
    onset_sweeps_j: Sequence[Sequence[float]],
    offset_sweeps_j: Sequence[Sequence[float]],
    zero_point_contrasts_j: Sequence[float],
    bundle_residual_half_widths_j: Sequence[Sequence[float]],
    member_window_bounds_s: object = None,
    member_envelope_integral_sums_j: object = None,
    calibration_bracket: object,
    shared_edge_bound_s: float,
) -> FloorEstimate:
    """D-124 contrast floor with two shared edges and local residuals.

    ``onset_sweeps_j`` and ``offset_sweeps_j`` are float evaluations at the
    exactly enumerated shared-edge candidates.  Each explicit
    ``zero_point_contrasts_j`` entry is the sweeps' exact zero-shift
    evaluation and must occur by exact equality in both sweeps.  The shared
    extrema are composed as excursions about that zero point, then the
    centre discrepancy from the block delta is added once and outward.
    ``member_window_bounds_s`` supplies each block's aligned A1/B1/B2/A2
    normalized ``(start_s, end_s)`` bounds.  Separability gives the signed
    excursion extrema ``(min(onset)-z) + (min(offset)-z)`` and the analogous
    maximum only after every member is proven to remain strictly noncollapsed
    over the shared domain.
    Four bundle-local adversarial residual half-widths are then composed with
    the ABBA coefficients.  This one function is the registered arithmetic
    path for both calibration blocks and consuming contrasts.
    """

    try:
        deltas = _clean_values(block_deltas_j, "block deltas")
        zero_points = _clean_values(
            zero_point_contrasts_j,
            "zero-point contrasts",
        )
    except (TypeError, ValueError) as exc:
        _common_mode_refuse("common_mode_precondition_failed", str(exc))
    n = len(deltas)
    try:
        input_lengths_match = (
            len(onset_sweeps_j)
            == len(offset_sweeps_j)
            == len(zero_points)
            == len(bundle_residual_half_widths_j)
            == len(member_envelope_integral_sums_j)
            == n
        )
    except TypeError:
        input_lengths_match = False
    if not input_lengths_match:
        _common_mode_refuse(
            "common_mode_precondition_failed",
            "every block needs onset, offset, an explicit zero point, four "
            "residuals, and a member envelope integral sum",
        )
    bound = _common_mode_finite(shared_edge_bound_s)
    operative = registered_common_mode_operative_bound(calibration_bracket)
    if (
        bound is None
        or bound <= 0.0
        or not math.isclose(bound, operative, rel_tol=0.0, abs_tol=1e-12)
    ):
        _common_mode_refuse(
            "common_mode_allowance_application_invalid",
            "the sweep bound must equal the once-widened authenticated bound",
        )

    if (
        isinstance(member_window_bounds_s, (str, bytes))
        or not isinstance(member_window_bounds_s, Sequence)
        or len(member_window_bounds_s) != n
    ):
        _common_mode_refuse(
            "common_mode_nonseparable_window_domain",
            "every block needs aligned A1/B1/B2/A2 member-window bounds",
        )
    normalized_member_windows: list[tuple[tuple[float, float], ...]] = []
    for block_index, raw_block_windows in enumerate(member_window_bounds_s):
        if (
            isinstance(raw_block_windows, (str, bytes))
            or not isinstance(raw_block_windows, Sequence)
            or len(raw_block_windows) != 4
        ):
            _common_mode_refuse(
                "common_mode_nonseparable_window_domain",
                f"block {block_index} must have aligned A1/B1/B2/A2 windows",
            )
        block_windows: list[tuple[float, float]] = []
        for position, raw_window in zip(
            ("A1", "B1", "B2", "A2"),
            raw_block_windows,
            strict=True,
        ):
            if (
                isinstance(raw_window, (str, bytes))
                or not isinstance(raw_window, Sequence)
                or len(raw_window) != 2
            ):
                _common_mode_refuse(
                    "common_mode_nonseparable_window_domain",
                    f"block {block_index} {position} window must be "
                    "(start_s, end_s)",
                )
            start = _common_mode_finite(raw_window[0])
            end = _common_mode_finite(raw_window[1])
            if (
                start is None
                or end is None
                or not _common_mode_window_is_strictly_noncollapsed(
                    start,
                    end,
                    bound,
                )
            ):
                _common_mode_refuse(
                    "common_mode_nonseparable_window_domain",
                    f"block {block_index} {position} window is outside the "
                    "strict noncollapse domain",
                )
            block_windows.append((start, end))
        normalized_member_windows.append(tuple(block_windows))

    block_widths: list[float] = []
    block_inputs = zip(
        deltas,
        onset_sweeps_j,
        offset_sweeps_j,
        zero_points,
        bundle_residual_half_widths_j,
        member_envelope_integral_sums_j,
        normalized_member_windows,
        strict=True,
    )
    for index, (
        delta,
        raw_onset,
        raw_offset,
        zero_point,
        raw_residuals,
        raw_member_envelope_sum,
        _member_windows,
    ) in enumerate(
        block_inputs
    ):
        try:
            onset = _clean_values(raw_onset, f"block {index} onset sweep")
            offset = _clean_values(raw_offset, f"block {index} offset sweep")
        except (TypeError, ValueError) as exc:
            _common_mode_refuse("common_mode_precondition_failed", str(exc))
        try:
            residual_count = len(raw_residuals)
        except TypeError:
            residual_count = -1
        if residual_count != 4:
            _common_mode_refuse(
                "common_mode_precondition_failed",
                f"block {index} must have exactly four bundle residuals",
            )
        residuals: list[float] = []
        for raw in raw_residuals:
            residual = _common_mode_finite(raw)
            if residual is None or residual < 0.0:
                _common_mode_refuse(
                    "common_mode_precondition_failed",
                    f"block {index} residuals must be finite and nonnegative",
                )
            residuals.append(residual)
        if zero_point not in onset or zero_point not in offset:
            _common_mode_refuse(
                "common_mode_precondition_failed",
                f"block {index} sweeps must include the explicit zero point "
                "by exact equality",
            )
        if not math.isclose(
            zero_point,
            delta,
            rel_tol=1e-9,
            abs_tol=1e-12,
        ):
            _common_mode_refuse(
                "common_mode_zero_point_divergence_out_of_domain",
                f"block {index} zero point diverges from its block delta "
                "outside the registered provenance band",
            )
        member_envelope_sum = _common_mode_finite(raw_member_envelope_sum)
        if member_envelope_sum is None or member_envelope_sum < 0.0:
            _common_mode_refuse(
                "common_mode_precondition_failed",
                f"block {index} member envelope integral sum must be finite "
                "and nonnegative",
            )
        member_envelope_sum = max(
            member_envelope_sum,
            1.0,
            abs(delta),
            abs(zero_point),
            *(abs(value) for value in onset),
            *(abs(value) for value in offset),
        )
        # Each correctly-rounded contrast evaluation has error <=4u*S (fsum
        # exactness; cancellation shrinks the result, never the error), the
        # width composes <=3 evaluations plus one reference for <=16u*S, and
        # 64u*S gives 4x analytic headroom independent of member count and
        # magnitude ratio.
        extrema_pad = (
            64.0 * (math.ulp(1.0) / 2.0) * member_envelope_sum
        )
        excursion_lower = math.fsum(
            (min(onset), -zero_point, min(offset), -zero_point)
        )
        excursion_upper = math.fsum(
            (max(onset), -zero_point, max(offset), -zero_point)
        )
        lower = _common_mode_outward(
            math.fsum((excursion_lower, -extrema_pad)),
            -math.inf,
        )
        upper = _common_mode_outward(
            math.fsum((excursion_upper, extrema_pad)),
            math.inf,
        )
        zero_centred_width = _common_mode_outward(
            max(abs(lower), abs(upper)),
            math.inf,
        )
        shared_width = _common_mode_outward(
            math.fsum(
                (zero_centred_width, abs(zero_point - delta))
            ),
            math.inf,
        )
        local_width = math.fsum(residuals) / 2.0
        block_widths.append(
            _common_mode_outward(
                math.fsum((shared_width, local_width)),
                math.inf,
            )
        )

    estimate = comparative_false_effect_floor(
        deltas,
        admissible_half_widths_j=block_widths,
    )
    return replace(
        estimate,
        estimator_registration=two_shared_edge_common_mode_registration(),
    )


def abba_delta(a1_j: float, b1_j: float, b2_j: float, a2_j: float) -> float:
    """Exact ABBA block delta ``(B1 + B2 - A1 - A2) / 2``; sign is B - A."""
    members = _clean_values([a1_j, b1_j, b2_j, a2_j], "ABBA members")
    a1, b1, b2, a2 = members
    return (b1 + b2 - a1 - a2) / 2.0


# ---------------------------------------------------------------------------
# Artifact emit (joulewise.detection_floor_artifact.v2)
# ---------------------------------------------------------------------------


def build_method_block() -> dict:
    return {
        "method_id": METHOD_ID,
        "t_quantile": 0.975,
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


def _add_whole_window_drift_allowance(
    record: dict,
    *,
    base_unguarded_j: float,
    base_guarded_j: float | None,
    consumption_semantics_id: str,
    whole_window_drift_allowance: Mapping,
) -> dict:
    if consumption_semantics_id not in _CONSUMPTION_SEMANTICS_IDS:
        raise ValueError(
            f"unknown whole-window consumption semantics: "
            f"{consumption_semantics_id!r}"
        )
    allowance = whole_window_drift_allowance.get("allowance_j")
    if (
        isinstance(allowance, bool)
        or not isinstance(allowance, int | float)
        or not math.isfinite(float(allowance))
        or float(allowance) <= 0.0
    ):
        raise ValueError("whole-window drift allowance must be finite and > 0")
    allowance = float(allowance)
    basis_sha256 = whole_window_drift_allowance.get(
        "whole_window_evaluation_basis_sha256"
    )
    if not (
        isinstance(basis_sha256, str)
        and len(basis_sha256) == 64
        and all(character in "0123456789abcdef" for character in basis_sha256)
    ):
        raise ValueError(
            "whole-window drift allowance requires an authenticated evaluation basis"
        )
    return {
        **record,
        "whole_window_evaluation_basis_sha256": basis_sha256,
        "consumption_semantics_id": consumption_semantics_id,
        "whole_window_drift_allowance": dict(whole_window_drift_allowance),
        "drift_widened_unguarded_floor_j": base_unguarded_j + allowance,
        "drift_widened_guarded_floor_j": (
            base_guarded_j + allowance if base_guarded_j is not None else None
        ),
    }


def _strict_builder_floor_fields(
    estimate: FloorEstimate,
) -> tuple[tuple[float, ...], float, float | None]:
    widths = estimate.admissible_half_widths_j
    if not widths:
        raise ValueError(
            "floor estimate requires nonempty authenticated admissible-set widths"
        )
    if len(widths) != estimate.n:
        raise ValueError(
            "floor estimate admissible-set width count must equal estimate n"
        )
    validated_widths = tuple(
        _admissible_widths(widths, expected_n=estimate.n)
    )

    corner_unguarded = estimate.corner_widened_unguarded_floor_j
    corner_guarded = estimate.corner_widened_guarded_floor_j
    if (
        isinstance(estimate.unguarded_floor_j, bool)
        or not isinstance(estimate.unguarded_floor_j, int | float)
        or not math.isfinite(float(estimate.unguarded_floor_j))
        or float(estimate.unguarded_floor_j) < 0.0
    ):
        raise ValueError(
            "floor estimate requires a finite nonnegative unguarded floor"
        )
    unguarded_floor = float(estimate.unguarded_floor_j)
    if (
        isinstance(corner_unguarded, bool)
        or not isinstance(corner_unguarded, int | float)
        or not math.isfinite(float(corner_unguarded))
        or float(corner_unguarded) < 0.0
    ):
        raise ValueError(
            "floor estimate requires a finite nonnegative "
            "corner-widened unguarded floor"
        )
    corner_unguarded = float(corner_unguarded)

    has_guard_factor = estimate.guard_factor is not None
    has_guarded_floor = estimate.guarded_floor_j is not None
    guarded_estimate = estimate.n >= GUARD_MINIMUM_N
    if guarded_estimate and not (has_guard_factor and has_guarded_floor):
        raise ValueError(
            "guarded floor estimate requires guard_factor and guarded_floor_j"
        )
    if not guarded_estimate and (has_guard_factor or has_guarded_floor):
        raise ValueError(
            "smoke floor estimate requires null guard_factor and guarded_floor_j"
        )
    if not guarded_estimate:
        if corner_guarded is not None:
            raise ValueError(
                "smoke floor estimate requires a null corner-widened guarded floor"
            )
        return validated_widths, corner_unguarded, None

    guard_factor = estimate.guard_factor
    guarded_floor = estimate.guarded_floor_j
    if (
        isinstance(guard_factor, bool)
        or not isinstance(guard_factor, int | float)
        or not math.isfinite(float(guard_factor))
        or float(guard_factor) < 1.0
        or isinstance(guarded_floor, bool)
        or not isinstance(guarded_floor, int | float)
        or not math.isfinite(float(guarded_floor))
        or float(guarded_floor) < 0.0
    ):
        raise ValueError(
            "guarded floor estimate requires finite nonnegative guarded fields"
        )
    if (
        isinstance(corner_guarded, bool)
        or not isinstance(corner_guarded, int | float)
        or not math.isfinite(float(corner_guarded))
        or float(corner_guarded) < 0.0
    ):
        raise ValueError(
            "guarded floor estimate requires both corner-widened fields"
        )
    guard_factor = float(guard_factor)
    guarded_floor = float(guarded_floor)
    corner_guarded = float(corner_guarded)
    if guarded_floor != guard_factor * unguarded_floor:
        raise ValueError(
            "guarded floor must equal guard_factor times unguarded floor"
        )
    if corner_guarded != guard_factor * corner_unguarded:
        raise ValueError(
            "corner-widened guarded floor must equal guard_factor times "
            "corner-widened unguarded floor"
        )
    return validated_widths, corner_unguarded, corner_guarded


def build_absolute_record(
    estimate: FloorEstimate,
    bundle_observations: Sequence[Mapping],
    *,
    consumption_semantics_id: str,
    whole_window_drift_allowance: Mapping,
) -> dict:
    if estimate.kind != "absolute":
        raise ValueError("absolute record requires an absolute FloorEstimate")
    if len(bundle_observations) != estimate.n:
        raise ValueError("bundle_observations length must equal n")
    widths, widened_unguarded, widened_guarded = (
        _strict_builder_floor_fields(estimate)
    )
    record = {
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
        "admissible_half_widths_j": list(widths),
        "corner_widened_unguarded_floor_j": widened_unguarded,
        "corner_widened_guarded_floor_j": widened_guarded,
        "bundle_observations": [dict(obs) for obs in bundle_observations],
    }
    record = _add_attribution_limit_metadata(record, estimate)
    return _add_whole_window_drift_allowance(
        record,
        base_unguarded_j=widened_unguarded,
        base_guarded_j=widened_guarded,
        consumption_semantics_id=consumption_semantics_id,
        whole_window_drift_allowance=whole_window_drift_allowance,
    )


def build_comparative_record(
    estimate: FloorEstimate,
    blocks: Sequence[Mapping],
    *,
    consumption_semantics_id: str,
    whole_window_drift_allowance: Mapping,
) -> dict:
    if estimate.kind != "comparative":
        raise ValueError("comparative record requires a comparative FloorEstimate")
    if len(blocks) != estimate.n:
        raise ValueError("blocks length must equal n_blocks")
    widths, widened_unguarded, widened_guarded = (
        _strict_builder_floor_fields(estimate)
    )
    record = {
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
        "admissible_half_widths_j": list(widths),
        "corner_widened_unguarded_floor_j": widened_unguarded,
        "corner_widened_guarded_floor_j": widened_guarded,
        "blocks": [dict(block) for block in blocks],
    }
    if estimate.estimator_registration is not None:
        if not validate_common_mode_estimator_registration(
            estimate.estimator_registration
        ):
            raise ValueError("comparative estimate has an invalid estimator registration")
        record["estimator_registration"] = copy.deepcopy(
            dict(estimate.estimator_registration)
        )
    record = _add_attribution_limit_metadata(record, estimate)
    return _add_whole_window_drift_allowance(
        record,
        base_unguarded_j=widened_unguarded,
        base_guarded_j=widened_guarded,
        consumption_semantics_id=consumption_semantics_id,
        whole_window_drift_allowance=whole_window_drift_allowance,
    )


def _normalized_source_regime(source_regime: Mapping) -> dict:
    if not isinstance(source_regime, Mapping):
        raise ValueError("component provenance requires source_regime")
    record = copy.deepcopy(dict(source_regime))
    stack_identity = record.get("stack_identity")
    if not isinstance(stack_identity, Mapping):
        raise ValueError("component source_regime requires stack_identity")
    record["stack_identity_sha256"] = canonical_domain_sha256(
        STACK_IDENTITY_DOMAIN,
        stack_identity,
    )
    if not isinstance(record.get("stress_observed"), Mapping):
        raise ValueError("component source_regime requires stress_observed")
    return record


def _compose_bound_term_entries(entries: Sequence[Mapping]) -> dict:
    if any(entry.get("applicability") == "unknown" for entry in entries):
        return {"applicability": "unknown", "maximum": None}
    required = [
        entry.get("maximum")
        for entry in entries
        if entry.get("applicability") == "required"
    ]
    if required:
        return {"applicability": "required", "maximum": max(required)}
    return {"applicability": "not_applicable", "maximum": None}


def _compose_component_source_regimes(
    source_regimes: Sequence[Mapping],
) -> dict:
    if not source_regimes:
        raise ValueError("floor cell requires at least one component source_regime")
    regimes = [_normalized_source_regime(value) for value in source_regimes]
    stack_hash = regimes[0]["stack_identity_sha256"]
    if any(regime["stack_identity_sha256"] != stack_hash for regime in regimes[1:]):
        raise ValueError("component source_regime stack identities must match")
    observations = [regime["stress_observed"] for regime in regimes]
    stress_observed = {
        field: min(observed[field] for observed in observations)
        for field in _ENVELOPE_MIN_FIELDS
    }
    stress_observed.update(
        {
            field: max(observed[field] for observed in observations)
            for field in _ENVELOPE_MAX_FIELDS
        }
    )
    stress_observed["bound_terms"] = {
        term: _compose_bound_term_entries(
            [observed["bound_terms"][term] for observed in observations]
        )
        for term in _BOUND_TERMS
    }
    return {
        "stack_identity": copy.deepcopy(regimes[0]["stack_identity"]),
        "stack_identity_sha256": stack_hash,
        "stress_observed": stress_observed,
    }


def build_floor_cell(
    *,
    cell_id: str,
    key: Mapping,
    eligibility: Mapping,
    absolute: Optional[Mapping],
    comparative: Optional[Mapping],
    transport_group_id: str,
    provenance: Mapping,
) -> dict:
    key_record = dict(key)
    definition = key_record.get("condition_family_definition")
    if isinstance(definition, Mapping):
        key_record["condition_family_sha256"] = canonical_domain_sha256(
            CONDITION_FAMILY_DOMAIN, definition
        )
    provenance_record = copy.deepcopy(dict(provenance))
    component_regimes = []
    for component_name, component_record in (
        ("absolute", absolute),
        ("comparative", comparative),
    ):
        component_provenance = provenance_record.get(component_name)
        if component_record is None:
            if component_provenance is not None:
                raise ValueError(
                    f"{component_name} provenance requires a component record"
                )
            continue
        if not isinstance(component_provenance, Mapping):
            raise ValueError(
                f"{component_name} record requires component provenance"
            )
        normalized_regime = _normalized_source_regime(
            component_provenance.get("source_regime")
        )
        component_provenance = dict(component_provenance)
        component_provenance["source_regime"] = normalized_regime
        provenance_record[component_name] = component_provenance
        component_regimes.append(normalized_regime)
    regime_record = _compose_component_source_regimes(component_regimes)
    floor_abs = (
        absolute.get("drift_widened_guarded_floor_j")
        if absolute is not None
        else None
    )
    floor_cmp = (
        comparative.get("drift_widened_guarded_floor_j")
        if comparative is not None
        else None
    )
    if floor_abs is not None and floor_cmp is not None:
        floor_gate: Optional[float] = max(floor_abs, floor_cmp)
    else:
        floor_gate = None
    record = {
        "cell_id": cell_id,
        "key": key_record,
        "eligibility": dict(eligibility),
        "floor_abs_j": floor_abs,
        "floor_cmp_j": floor_cmp,
        "floor_gate_j": floor_gate,
        "absolute": dict(absolute) if absolute is not None else None,
        "comparative": dict(comparative) if comparative is not None else None,
        "source_regime": regime_record,
        "transport_group_id": transport_group_id,
        "provenance": provenance_record,
    }
    limited_records = [
        value
        for value in (absolute, comparative)
        if isinstance(value, Mapping)
        and value.get("floor_limit_class") == ATTRIBUTION_LIMIT_CLASS
    ]
    if limited_records:
        record.update(
            {
                "floor_source": ATTRIBUTION_FLOOR_SOURCE,
                "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
                "point_floor_diagnostics": {
                    name: dict(value["point_floor_diagnostic"])
                    for name, value in (
                        ("absolute", absolute),
                        ("comparative", comparative),
                    )
                    if isinstance(value, Mapping)
                    and value.get("floor_limit_class")
                    == ATTRIBUTION_LIMIT_CLASS
                },
                "single_count_discipline": attribution_single_count_discipline(),
            }
        )
    return record


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
    stack_identity: Mapping,
    source_cells: Sequence[Mapping],
    allowed_consumer_condition_families: Sequence[Mapping],
) -> dict:
    composed = compose_transport_group(source_cells)
    stack = dict(stack_identity)
    stack_hash = canonical_domain_sha256(STACK_IDENTITY_DOMAIN, stack)
    record = {
        "transport_group_id": transport_group_id,
        "rule_id": TRANSPORT_RULE_ID,
        "backend": backend,
        "metric": metric,
        "window_class": window_class,
        "stack_identity": stack,
        "stack_identity_sha256": stack_hash,
        "source_cell_ids": [cell["cell_id"] for cell in source_cells],
        "allowed_consumer_condition_families": [dict(f) for f in allowed_consumer_condition_families],
        "composed_floor_abs_j": composed["composed_floor_abs_j"],
        "composed_floor_cmp_j": composed["composed_floor_cmp_j"],
        "composed_floor_gate_j": composed["composed_floor_gate_j"],
        "stress_envelope": composed["stress_envelope"],
    }
    limited_sources = [
        cell
        for cell in source_cells
        if cell.get("floor_limit_class") == ATTRIBUTION_LIMIT_CLASS
    ]
    if limited_sources:
        record.update(
            {
                "floor_source": ATTRIBUTION_FLOOR_SOURCE,
                "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
                "point_floor_diagnostics": {
                    str(cell["cell_id"]): copy.deepcopy(
                        cell["point_floor_diagnostics"]
                    )
                    for cell in limited_sources
                },
                "single_count_discipline": attribution_single_count_discipline(),
            }
        )
    return record


def build_floor_artifact(
    *,
    artifact_id: str,
    calibration_scope: str,
    provenance: Mapping,
    cells: Sequence[Mapping],
    transport_groups: Sequence[Mapping],
    source_class: str,
    idle_drift_guard: Optional[Mapping] = None,
) -> dict:
    if idle_drift_guard is None:
        idle_drift_guard = {
            "calibration_status": "pending_calibration",
            "method": _IDLE_DRIFT_GUARD_METHOD,
            "guard_w": None,
            "n_bundles": 0,
            "bundle_sha256": [],
            "cell_id": None,
            "artifact_sha256": None,
        }
    cell_records = [copy.deepcopy(dict(cell)) for cell in cells]
    plan = provenance.get("calibration_plan") if isinstance(provenance, Mapping) else None
    plan_sha256 = plan.get("sha256") if isinstance(plan, Mapping) else None
    for cell in cell_records:
        comparative = cell.get("comparative")
        blocks = comparative.get("blocks") if isinstance(comparative, Mapping) else None
        if not isinstance(blocks, list):
            continue
        for block in blocks:
            if not isinstance(block, dict):
                continue
            block["calibration_plan_sha256"] = plan_sha256
            labels = block.get("executed_labels")
            members = block.get("members")
            if not isinstance(labels, list) or not isinstance(members, list):
                continue
            for index, member in enumerate(members):
                if isinstance(member, dict) and index < len(labels):
                    member["plan_label"] = labels[index]
                    member["plan_sequence_index"] = index + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "calibration_scope": calibration_scope,
        "source_class": source_class,
        "method": build_method_block(),
        "provenance": dict(provenance),
        "idle_drift_guard": dict(idle_drift_guard),
        "cells": cell_records,
        "transport_groups": [dict(group) for group in transport_groups],
    }


# ---------------------------------------------------------------------------
# Artifact validation
# ---------------------------------------------------------------------------

_TOP_KEYS = {
    "schema_version",
    "artifact_id",
    "calibration_scope",
    "source_class",
    "method",
    "provenance",
    "idle_drift_guard",
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
_KEY_KEYS = {
    "backend",
    "metric",
    "window_class",
    "condition_family_id",
    "condition_family_definition",
    "condition_family_sha256",
}
_ELIGIBILITY_KEYS = {"use_role", "minimum_claim_n", "status", "claim_usable", "reason_codes"}
_WIDENED_FLOOR_KEYS = {
    "admissible_half_widths_j",
    "corner_widened_unguarded_floor_j",
    "corner_widened_guarded_floor_j",
}
_DRIFT_WIDENED_FLOOR_KEYS = {
    "whole_window_drift_allowance",
    "drift_widened_unguarded_floor_j",
    "drift_widened_guarded_floor_j",
}
_COMPONENT_WINDOW_KEYS = {
    "whole_window_evaluation_basis_sha256",
    "consumption_semantics_id",
} | _DRIFT_WIDENED_FLOOR_KEYS
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
} | _WIDENED_FLOOR_KEYS | _COMPONENT_WINDOW_KEYS
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
} | _WIDENED_FLOOR_KEYS | _COMPONENT_WINDOW_KEYS
_ATTRIBUTION_LIMIT_RECORD_KEYS = {
    "floor_source",
    "floor_limit_class",
    "point_floor_diagnostic",
    "single_count_discipline",
}
_CMP_OPTIONAL_KEYS = _ATTRIBUTION_LIMIT_RECORD_KEYS | {
    "estimator_registration"
}
_ATTRIBUTION_LIMIT_CONTAINER_KEYS = {
    "floor_source",
    "floor_limit_class",
    "point_floor_diagnostics",
    "single_count_discipline",
}
_POINT_FLOOR_DIAGNOSTIC_KEYS = {
    "label",
    "published_claim_floor",
    "unguarded_floor_j",
    "guard_factor",
    "guarded_floor_j",
}
_WHOLE_WINDOW_DRIFT_ALLOWANCE_KEYS = {
    "claim_family",
    "allowance_j",
    "observed_trajectory_excursion_j",
    "derived_repeatability_bound_j",
    "provenance",
    "whole_window_evaluation_basis_sha256",
}
_WHOLE_WINDOW_DRIFT_PROVENANCE_KEYS = {
    "bound_derivation_sha256",
    "observed_component",
    "derived_component",
}
_OBS_KEYS = {"bundle_id", "bundle_sha256", "config_sha256", "metric_value_j"}
_BLOCK_KEYS = {
    "block_id",
    "calibration_plan_sha256",
    "executed_labels",
    "members",
    "delta_j",
}
_MEMBER_KEYS = {
    "position",
    "plan_label",
    "plan_sequence_index",
    "bundle_id",
    "bundle_sha256",
    "config_sha256",
    "metric_value_j",
}
_PROVENANCE_KEYS = {
    "calibration_plan",
    "mint_tool_version",
    "implementation",
}
_PROVENANCE_OPTIONAL_KEYS = {
    "producer_calibration_plans",
    "assurance",
    "calibration_custody_store",
}
_CALIBRATION_PLAN_KEYS = {
    "plan_id",
    "declared_calibration_scope",
    "relative_path",
    "sha256",
}
_ORDER_MANIFEST_KEYS = {"manifest_id", "sha256"}
_CAMPAIGN_LOG_KEYS = {"sha256"}
_HASH_PIN_KEYS = {"sha256"}
_IMPLEMENTATION_KEYS = {
    "project_commit",
    "project_tree_state",
    "python_package",
}
_IMPLEMENTATION_OPTIONAL_KEYS = {
    "mint_commit_contained_in_origin_main",
    "head_pin_commit_contained_in_origin_main",
}
_ASSURANCE_KEYS = {
    "profile_id",
    "independent_attestation",
    "establishes",
    "does_not_establish",
}
_CALIBRATION_CUSTODY_STORE_KEYS = {"schema_version", "manifest_sha256"}
_CALIBRATION_CUSTODY_STORE_SCHEMA = (
    "joulewise.calibration_custody_store_manifest.v1"
)
_V2_ASSURANCE_PROFILE = {
    "profile_id": "single_authority_hash_bound_replay.v1",
    "independent_attestation": False,
    "establishes": [
        "exact-byte consistency with disclosed commitments",
        "ledger and verdict consistency under the recorded code",
        "deterministic rederivability of mint inputs",
    ],
    "does_not_establish": [
        "honesty of the trusted operator",
        "independent witness of physical collection",
        "resistance to coordinated prepublication rewrite",
    ],
}
_CELL_PROVENANCE_KEYS = {"absolute", "comparative"}
_COMPONENT_PROVENANCE_KEYS = {
    "calibration_cell_id",
    "evidence_root_id",
    "order_manifest",
    "campaign_log",
    "extraction_report",
    "extraction_spec",
    "bundle_ids",
    "bundle_sha256s",
    "source_regime",
}
_GROUP_KEYS = {
    "transport_group_id",
    "rule_id",
    "backend",
    "metric",
    "window_class",
    "stack_identity",
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
    delta = abs(actual - expected)
    relative_limit = max(1e-12, 1e-12 * abs(expected))
    return delta <= min(relative_limit, _MAX_RECOMPUTATION_ABS_DELTA_J)


def _is_hex(value, length: int = 64) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(c in "0123456789abcdef" for c in value)
    )


@dataclass(frozen=True)
class _FloorMintPinsetProjection:
    family_identities: frozenset[tuple[str, str, str]]
    evidence_root_ids: frozenset[str]


def _is_trimmed_string(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def _is_positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _is_six_decimal_literal(value: object) -> bool:
    if not isinstance(value, str) or value.count(".") != 1:
        return False
    whole, fraction = value.split(".")
    return (
        bool(whole)
        and whole.isdigit()
        and (whole == "0" or not whole.startswith("0"))
        and len(fraction) == 6
        and fraction.isdigit()
    )


_V2_ROOT_KEYS = {
    "schema_version", "mint_tool_version", "producer_plans", "aggregate"
}
_V2_PLAN_KEYS = {
    "plan_id", "sha256", "declared_sha256", "sidecar_sha256", "relative_path",
    "declared_calibration_scope", "artifact_calibration_scope",
}
_V2_PRODUCER_KEYS = {
    "plan", "evidence_root_id", "component_artifact", "model_runtime_config",
    "extraction_spec", "calibration_acceptance", "cells",
}
_V2_COMPONENT_ARTIFACT_KEYS = {"artifact_id", "sha256"}
_V2_RUNTIME_KEYS = {
    "model_artifact_sha256", "runtime_identity_sha256", "config_set_sha256"
}
_V2_EXTRACTION_KEYS = {"sha256", "member_count"}
_V2_ACCEPTANCE_KEYS = {
    "acceptance_id", "artifact_sha256", "derivation_sha256", "derivation_rule_id"
}
_V2_CELL_KEYS = {
    "role", "cell_id", "transport_group_id", "condition_family_id",
    "condition_family_sha256", "metric", "window_class", "target_precheck_path",
    "allowed_consumer_condition_families", "absolute", "comparative",
    "postcollection",
}
_V2_COMPONENT_KEYS = {
    "evidence_root_id", "calibration_cell_id", "evaluation_basis_sha256",
    "evaluation_basis_members", "extraction_spec_sha256",
    "extraction_spec_members", "expected_n", "drift_allowance_j",
    "order_manifest_id", "order_manifest_sha256", "consumption_semantics_id",
    "members",
}
_V2_POSTCOLLECTION_KEYS = {
    "absolute_evaluation_basis_sha256", "absolute_evaluation_basis_members",
    "comparative_evaluation_basis_sha256", "comparative_evaluation_basis_members",
    "pre_receipt_sha256", "pre_content_sha256", "post_receipt_sha256",
    "post_content_sha256", "bracket_binding_sha256",
    "terminal_ledger_head_sha256", "observed_drift_s", "allowance_rule",
    "bracket_screen_s", "applied_allowance_s", "allowance_embedding_count",
    "extraction_report_sha256", "absolute_floor_full_precision",
    "comparative_floor_full_precision", "operative_floor_full_precision",
    "absolute_floor_six_decimal", "comparative_floor_six_decimal",
    "operative_floor_six_decimal",
}
_V2_AGGREGATE_KEYS = {
    "artifact_id", "plan_set_id", "producer_set_sha256", "calibration_scope",
    "source_class", "cell_composition_rule", "consumer_floor_rule",
    "component_artifacts", "cell_ids", "transport_allowlists",
}
_V2_AGGREGATE_COMPONENT_KEYS = {
    "plan_id", "artifact_id", "sha256", "producer_pin_sha256"
}
_V2_ALLOWLIST_KEYS = {
    "transport_group_id", "cell_ids", "allowed_consumer_condition_families"
}
_V2_FAMILY_KEYS = {"condition_family_id", "condition_family_sha256"}
_V2_MEMBER_KEYS = {"bundle_id", "config_sha256"}


def _v2_exact_mapping(value: object, keys: set[str]) -> bool:
    return isinstance(value, Mapping) and set(value) == keys


def _v2_plain_decimal(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    whole, separator, fraction = value.partition(".")
    return (
        bool(whole)
        and whole.isdigit()
        and (whole == "0" or not whole.startswith("0"))
        and (not separator or bool(fraction) and fraction.isdigit())
    )


def _v2_closed_family_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(
            _v2_exact_mapping(row, _V2_FAMILY_KEYS)
            and _is_trimmed_string(row.get("condition_family_id"))
            and _is_hex(row.get("condition_family_sha256"))
            for row in value
        )
        and len(
            {
                (row["condition_family_id"], row["condition_family_sha256"])
                for row in value
            }
        )
        == len(value)
    )


def _project_floor_mint_pinset(
    value: object,
) -> _FloorMintPinsetProjection | None:
    """Return only the family identity and exact root literals of a v1 pinset."""

    if not isinstance(value, Mapping) or set(value) != _FLOOR_MINT_PINSET_KEYS:
        return None
    if value.get("schema_version") != _FLOOR_MINT_PINSET_SCHEMA_VERSION:
        return None
    if not _is_trimmed_string(value.get("mint_tool_version")):
        return None

    plan = value.get("plan")
    artifact = value.get("artifact")
    cell = value.get("cell")
    components = (value.get("absolute"), value.get("comparative"))
    if (
        not isinstance(plan, Mapping)
        or set(plan) != _FLOOR_MINT_PLAN_PIN_KEYS
        or not isinstance(artifact, Mapping)
        or set(artifact) != _FLOOR_MINT_ARTIFACT_PIN_KEYS
        or not isinstance(cell, Mapping)
        or set(cell) != _FLOOR_MINT_CELL_PIN_KEYS
        or any(
            not isinstance(component, Mapping)
            or set(component) != _FLOOR_MINT_COMPONENT_PIN_KEYS
            for component in components
        )
    ):
        return None

    if (
        not _is_trimmed_string(plan.get("plan_id"))
        or not _is_hex(plan.get("sha256"))
        or not _is_trimmed_string(plan.get("declared_calibration_scope"))
        or not _is_trimmed_string(plan.get("artifact_calibration_scope"))
        or any(not _is_trimmed_string(item) for item in artifact.values())
    ):
        return None

    target_precheck_path = cell.get("target_precheck_path")
    if (
        not _is_trimmed_string(cell.get("condition_family_id"))
        or not _is_hex(cell.get("condition_family_sha256"))
        or not _is_trimmed_string(cell.get("metric"))
        or not _is_trimmed_string(cell.get("window_class"))
        or not isinstance(target_precheck_path, (list, tuple))
        or not target_precheck_path
        or any(not _is_trimmed_string(part) for part in target_precheck_path)
        or not _is_six_decimal_literal(cell.get("operative_floor_six_decimal"))
    ):
        return None

    root_ids = []
    for component in components:
        if (
            not _is_trimmed_string(component.get("evidence_root_id"))
            or not _is_trimmed_string(component.get("calibration_cell_id"))
            or not _is_hex(component.get("evaluation_basis_sha256"))
            or not _is_positive_int(component.get("evaluation_basis_members"))
            or not _is_positive_int(component.get("extraction_spec_members"))
            or not _is_positive_int(component.get("expected_n"))
            or not _is_number(component.get("drift_allowance_j"))
            or component.get("drift_allowance_j") < 0
            or not _is_trimmed_string(component.get("order_manifest_id"))
        ):
            return None
        root_ids.append(component["evidence_root_id"])

    return _FloorMintPinsetProjection(
        family_identities=frozenset(
            {
                (
                    value["mint_tool_version"],
                    plan["plan_id"],
                    plan["sha256"],
                )
            }
        ),
        evidence_root_ids=frozenset(root_ids),
    )


def _project_floor_mint_pinset_v2(
    value: object,
) -> _FloorMintPinsetProjection | None:
    """Project a recursively closed final-stage v2 pinset.

    Claim-side callers use this reader without importing the mint CLI, so it
    must agree with the mint on nested closure and aggregate/cell allowlists.
    """

    if not _v2_exact_mapping(value, _V2_ROOT_KEYS):
        return None
    if value.get("schema_version") != _FLOOR_MINT_PINSET_SCHEMA_VERSION_V2:
        return None
    mint_tool_version = value.get("mint_tool_version")
    producers = value.get("producer_plans")
    aggregate = value.get("aggregate")
    if (
        mint_tool_version != _FLOOR_MINT_TOOL_VERSION_V2
        or not isinstance(producers, list)
        or len(producers) != 2
        or not _v2_exact_mapping(aggregate, _V2_AGGREGATE_KEYS)
    ):
        return None
    if (
        not _is_trimmed_string(aggregate.get("artifact_id"))
        or not _is_trimmed_string(aggregate.get("plan_set_id"))
        or not _is_hex(aggregate.get("producer_set_sha256"))
        or aggregate.get("calibration_scope") != "production_window"
        or aggregate.get("source_class") != "prospective"
        or aggregate.get("cell_composition_rule")
        != "componentwise_max_never_sum.v1"
        or aggregate.get("consumer_floor_rule") != "cross_stack_armwise_max.v1"
    ):
        return None
    identities = {
        (
            mint_tool_version,
            aggregate["plan_set_id"],
            aggregate["producer_set_sha256"],
        )
    }
    root_ids: set[str] = set()
    plan_ids: list[str] = []
    cell_ids: list[str] = []
    group_ids: list[str] = []
    component_artifact_ids: list[str] = []
    component_artifact_hashes: list[str] = []
    cell_allowlists: list[list[Mapping]] = []
    for producer in producers:
        if not _v2_exact_mapping(producer, _V2_PRODUCER_KEYS):
            return None
        plan = producer.get("plan")
        cells = producer.get("cells")
        root_id = producer.get("evidence_root_id")
        if (
            not _v2_exact_mapping(plan, _V2_PLAN_KEYS)
            or not _is_trimmed_string(plan.get("plan_id"))
            or not _is_hex(plan.get("sha256"))
            or not _is_hex(plan.get("declared_sha256"))
            or plan.get("declared_sha256") != plan.get("sha256")
            or not _is_hex(plan.get("sidecar_sha256"))
            or not _is_trimmed_string(plan.get("relative_path"))
            or not _is_trimmed_string(plan.get("declared_calibration_scope"))
            or plan.get("artifact_calibration_scope") != "production_window"
            or not _is_trimmed_string(root_id)
            or not isinstance(cells, list)
            or len(cells) != 2
        ):
            return None
        component_artifact = producer.get("component_artifact")
        runtime = producer.get("model_runtime_config")
        extraction = producer.get("extraction_spec")
        acceptance = producer.get("calibration_acceptance")
        if (
            not _v2_exact_mapping(
                component_artifact, _V2_COMPONENT_ARTIFACT_KEYS
            )
            or not _is_trimmed_string(component_artifact.get("artifact_id"))
            or not _is_hex(component_artifact.get("sha256"))
            or not _v2_exact_mapping(runtime, _V2_RUNTIME_KEYS)
            or any(not _is_hex(item) for item in runtime.values())
            or not _v2_exact_mapping(extraction, _V2_EXTRACTION_KEYS)
            or not _is_hex(extraction.get("sha256"))
            or not _is_positive_int(extraction.get("member_count"))
            or not _v2_exact_mapping(acceptance, _V2_ACCEPTANCE_KEYS)
            or not _is_trimmed_string(acceptance.get("acceptance_id"))
            or not _is_hex(acceptance.get("artifact_sha256"))
            or not _is_hex(acceptance.get("derivation_sha256"))
            or not _is_trimmed_string(acceptance.get("derivation_rule_id"))
        ):
            return None
        plan_ids.append(plan["plan_id"])
        component_artifact_ids.append(component_artifact["artifact_id"])
        component_artifact_hashes.append(component_artifact["sha256"])
        identities.add((mint_tool_version, plan["plan_id"], plan["sha256"]))
        root_ids.add(root_id)
        roles: list[str] = []
        producer_members: set[str] = set()
        custody_pins: list[tuple[object, ...]] = []
        for cell in cells:
            if not _v2_exact_mapping(cell, _V2_CELL_KEYS):
                return None
            role = cell.get("role")
            expected_metric = {
                "decode": "phase_energy_j.decode",
                "prefill": "phase_energy_j.prefill",
            }.get(role)
            if (
                expected_metric is None
                or cell.get("metric") != expected_metric
                or cell.get("window_class") != "phase"
                or cell.get("target_precheck_path") != ["phase", role]
                or not _is_trimmed_string(cell.get("cell_id"))
                or not _is_trimmed_string(cell.get("transport_group_id"))
                or not _is_trimmed_string(cell.get("condition_family_id"))
                or not _is_hex(cell.get("condition_family_sha256"))
                or not _v2_closed_family_list(
                    cell.get("allowed_consumer_condition_families")
                )
            ):
                return None
            roles.append(role)
            cell_ids.append(cell["cell_id"])
            group_ids.append(cell["transport_group_id"])
            cell_allowlists.append(cell["allowed_consumer_condition_families"])
            components = []
            for component_name in ("absolute", "comparative"):
                component = cell.get(component_name)
                if (
                    not _v2_exact_mapping(component, _V2_COMPONENT_KEYS)
                    or component.get("evidence_root_id") != root_id
                    or not _is_trimmed_string(component.get("calibration_cell_id"))
                    or not _is_hex(component.get("evaluation_basis_sha256"))
                    or not _is_positive_int(
                        component.get("evaluation_basis_members")
                    )
                    or not _is_hex(component.get("extraction_spec_sha256"))
                    or component.get("extraction_spec_sha256")
                    != extraction["sha256"]
                    or not _is_positive_int(
                        component.get("extraction_spec_members")
                    )
                    or component.get("extraction_spec_members")
                    != extraction["member_count"]
                    or not _is_positive_int(component.get("expected_n"))
                    or not _is_number(component.get("drift_allowance_j"))
                    or component.get("drift_allowance_j") < 0
                    or not _is_trimmed_string(component.get("order_manifest_id"))
                    or not _is_hex(component.get("order_manifest_sha256"))
                    or component.get("consumption_semantics_id")
                    not in _CONSUMPTION_SEMANTICS_IDS
                    or not isinstance(component.get("members"), list)
                    or not component.get("members")
                ):
                    return None
                member_ids: list[str] = []
                for member in component["members"]:
                    if (
                        not _v2_exact_mapping(member, _V2_MEMBER_KEYS)
                        or not _is_trimmed_string(member.get("bundle_id"))
                        or not _is_hex(member.get("config_sha256"))
                    ):
                        return None
                    member_ids.append(member["bundle_id"])
                if len(member_ids) != len(set(member_ids)):
                    return None
                expected_member_count = component["expected_n"] * (
                    1 if component_name == "absolute" else 4
                )
                if len(member_ids) != expected_member_count:
                    return None
                producer_members.update(member_ids)
                components.append(component)
            post = cell.get("postcollection")
            if not _v2_exact_mapping(post, _V2_POSTCOLLECTION_KEYS):
                return None
            hash_fields = {
                key for key in _V2_POSTCOLLECTION_KEYS if key.endswith("sha256")
            }
            if (
                any(not _is_hex(post.get(key)) for key in hash_fields)
                or not _is_positive_int(
                    post.get("absolute_evaluation_basis_members")
                )
                or not _is_positive_int(
                    post.get("comparative_evaluation_basis_members")
                )
                or post.get("allowance_rule")
                != "max(observed_drift_s,0.010818)"
                or post.get("bracket_screen_s") != "0.010818"
                or type(post.get("allowance_embedding_count")) is not int
                or post.get("allowance_embedding_count") != 1
                or any(
                    not _v2_plain_decimal(post.get(key))
                    for key in (
                        "observed_drift_s",
                        "applied_allowance_s",
                        "absolute_floor_full_precision",
                        "comparative_floor_full_precision",
                        "operative_floor_full_precision",
                    )
                )
                or any(
                    not _is_six_decimal_literal(post.get(key))
                    or post.get(key) == "7.377086"
                    for key in (
                        "absolute_floor_six_decimal",
                        "comparative_floor_six_decimal",
                        "operative_floor_six_decimal",
                    )
                )
                or post.get("absolute_evaluation_basis_sha256")
                != components[0]["evaluation_basis_sha256"]
                or post.get("absolute_evaluation_basis_members")
                != components[0]["evaluation_basis_members"]
                or post.get("comparative_evaluation_basis_sha256")
                != components[1]["evaluation_basis_sha256"]
                or post.get("comparative_evaluation_basis_members")
                != components[1]["evaluation_basis_members"]
            ):
                return None
            try:
                observed_drift = Decimal(post["observed_drift_s"])
                applied_allowance = Decimal(post["applied_allowance_s"])
                absolute_full = Decimal(post["absolute_floor_full_precision"])
                comparative_full = Decimal(
                    post["comparative_floor_full_precision"]
                )
                operative_full = Decimal(post["operative_floor_full_precision"])
            except InvalidOperation:
                return None
            if (
                applied_allowance != max(observed_drift, Decimal("0.010818"))
                or operative_full != max(absolute_full, comparative_full)
            ):
                return None
            custody_pins.append(
                tuple(
                    post[key]
                    for key in (
                        "pre_receipt_sha256",
                        "pre_content_sha256",
                        "post_receipt_sha256",
                        "post_content_sha256",
                        "bracket_binding_sha256",
                        "terminal_ledger_head_sha256",
                        "observed_drift_s",
                        "applied_allowance_s",
                        "extraction_report_sha256",
                    )
                )
            )
        if set(roles) != {"decode", "prefill"} or len(set(roles)) != 2:
            return None
        if len(set(custody_pins)) != 1:
            return None
        # The authenticated extraction specification may govern reference
        # cells that are not inputs to the floor mint.  The explicit pinset
        # therefore closes the mint-member subset while the production
        # inventory check authenticates the complete specification census.
        if len(producer_members) > extraction["member_count"]:
            return None
    if (
        len(set(plan_ids)) != 2
        or len(cell_ids) != 4
        or len(set(cell_ids)) != 4
        or len(group_ids) != 4
        or len(set(group_ids)) != 4
        or aggregate.get("cell_ids") != cell_ids
    ):
        return None
    aggregate_components = aggregate.get("component_artifacts")
    aggregate_allowlists = aggregate.get("transport_allowlists")
    if (
        not isinstance(aggregate_components, list)
        or len(aggregate_components) != 2
        or not isinstance(aggregate_allowlists, list)
        or len(aggregate_allowlists) != 4
    ):
        return None
    for index, entry in enumerate(aggregate_components):
        if (
            not _v2_exact_mapping(entry, _V2_AGGREGATE_COMPONENT_KEYS)
            or entry.get("plan_id") != plan_ids[index]
            or entry.get("artifact_id") != component_artifact_ids[index]
            or entry.get("sha256") != component_artifact_hashes[index]
            or not _is_hex(entry.get("producer_pin_sha256"))
        ):
            return None
    for index, entry in enumerate(aggregate_allowlists):
        if (
            not _v2_exact_mapping(entry, _V2_ALLOWLIST_KEYS)
            or entry.get("transport_group_id") != group_ids[index]
            or entry.get("cell_ids") != [cell_ids[index]]
            or not _v2_closed_family_list(
                entry.get("allowed_consumer_condition_families")
            )
            or entry.get("allowed_consumer_condition_families")
            != cell_allowlists[index]
        ):
            return None
    try:
        producer_hashes = [
            hashlib.sha256(
                json.dumps(
                    producer,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                ).encode("utf-8")
            ).hexdigest()
            for producer in producers
        ]
        producer_set_sha256 = hashlib.sha256(
            json.dumps(
                producers,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
    except (TypeError, ValueError):
        return None
    if (
        producer_set_sha256 != aggregate["producer_set_sha256"]
        or any(
            entry["producer_pin_sha256"] != producer_hashes[index]
            for index, entry in enumerate(aggregate_components)
        )
    ):
        return None
    return _FloorMintPinsetProjection(
        family_identities=frozenset(identities),
        evidence_root_ids=frozenset(root_ids),
    )


def _reject_duplicate_pinset_keys(pairs) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate pinset key {key!r}")
        result[key] = value
    return result


def _read_floor_mint_pinset(
    path: Path,
    *,
    expected_sha256: str | None = None,
) -> tuple[_FloorMintPinsetProjection | None, str | None]:
    """Read one regular, non-symlink pinset and optionally authenticate bytes."""

    path = Path(path)
    if expected_sha256 is not None and not _is_hex(expected_sha256):
        return None, "expected sha256 must be 64 lowercase hexadecimal characters"
    try:
        file_stat = path.lstat()
    except OSError as exc:
        return None, f"cannot inspect pinset file: {exc.strerror or type(exc).__name__}"
    if stat.S_ISLNK(file_stat.st_mode):
        return None, "pinset file must not be a symlink"
    if not stat.S_ISREG(file_stat.st_mode):
        return None, "pinset file must be a regular file"
    try:
        raw = read_authentication_input(
            path, grammar="json", label="floor mint pinset validator read"
        )
    except OSError as exc:
        return None, f"cannot read pinset file: {exc.strerror or type(exc).__name__}"
    if expected_sha256 is not None:
        actual_sha256 = hashlib.sha256(raw).hexdigest()
        if actual_sha256 != expected_sha256:
            return (
                None,
                "pinset sha256 mismatch: "
                f"expected {expected_sha256}, observed {actual_sha256}",
            )
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_pinset_keys,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return None, f"pinset is not valid UTF-8 JSON: {exc}"
    projection = _project_floor_mint_pinset(value)
    if projection is None:
        projection = _project_floor_mint_pinset_v2(value)
    if projection is None:
        return None, "pinset does not match a closed final pinset schema"
    return projection, None


def _repository_floor_mint_pinsets(
) -> tuple[list[_FloorMintPinsetProjection], str | None]:
    projections = []
    try:
        paths = sorted(_FLOOR_MINT_PINSET_DIRECTORY.glob("*.json"))
    except OSError as exc:
        return [], f"artifact.pinset: repository pinset scan failed: {exc.strerror or type(exc).__name__}"
    for path in paths:
        if path.name == "schema_v2.json":
            continue
        projection, error = _read_floor_mint_pinset(path)
        if error is not None:
            return (
                [],
                f"artifact.pinset: repository pinset {path.name!r}: {error}",
            )
        assert projection is not None
        projections.append(projection)
    return projections, None


def _artifact_family_identity(value: Mapping) -> tuple[str, str, str] | None:
    provenance = value.get("provenance")
    if not isinstance(provenance, Mapping):
        return None
    plan = provenance.get("calibration_plan")
    mint_tool_version = provenance.get("mint_tool_version")
    if (
        not isinstance(plan, Mapping)
        or not _is_trimmed_string(mint_tool_version)
        or not _is_trimmed_string(plan.get("plan_id"))
        or not _is_hex(plan.get("sha256"))
    ):
        return None
    return mint_tool_version, plan["plan_id"], plan["sha256"]


def _resolve_evidence_root_ids(
    value: Mapping,
    pinset_path: Path | None,
    expected_pinset_sha256: str | None,
) -> tuple[frozenset[str] | None, str | None]:
    identity = _artifact_family_identity(value)
    if (pinset_path is None) != (expected_pinset_sha256 is None):
        return (
            None,
            "artifact.pinset: pinset_path and expected_pinset_sha256 "
            "must be supplied together",
        )
    if pinset_path is not None:
        projection, error = _read_floor_mint_pinset(
            pinset_path,
            expected_sha256=expected_pinset_sha256,
        )
        if error is not None:
            return None, f"artifact.pinset: explicit pinset: {error}"
        candidates = [projection]
    else:
        candidates, error = _repository_floor_mint_pinsets()
        if error is not None:
            return None, error
    matches = [
        candidate
        for candidate in candidates
        if candidate is not None and identity in candidate.family_identities
    ]
    if not matches:
        return None, "artifact.pinset: no pinset matches artifact family identity"
    if len(matches) > 1:
        return (
            None,
            "artifact.pinset: multiple pinsets match artifact family identity",
        )
    return matches[0].evidence_root_ids, None


def _has_duplicates(values) -> bool:
    return any(value in values[:index] for index, value in enumerate(values))


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


def _check_keys_with_optional(mapping, required, optional, where, errors) -> bool:
    if not isinstance(mapping, Mapping):
        errors.append(f"{where}: expected an object")
        return False
    unknown = set(mapping) - required - optional
    missing = required - set(mapping)
    for key in sorted(unknown):
        errors.append(f"{where}: unrecognized key {key!r}")
    for key in sorted(missing):
        errors.append(f"{where}: missing key {key!r}")
    return not missing


def _validate_hashed_object(
    identity,
    *,
    object_keys,
    stored_hash,
    hash_name,
    domain,
    where,
    errors,
) -> bool:
    if not _check_keys(identity, object_keys, where, errors):
        return False
    if not _is_hex(stored_hash):
        errors.append(f"{where}: {hash_name} must be 64 lowercase hex chars")
        return False
    if any(not isinstance(value, (str, Mapping)) or not value for value in identity.values()):
        errors.append(f"{where}: identity fields must be nonempty strings or objects")
        return False
    try:
        expected_hash = canonical_domain_sha256(domain, identity)
    except (TypeError, ValueError):
        errors.append(f"{where}: identity object is not canonical-JSON serializable")
        return False
    if stored_hash != expected_hash:
        errors.append(f"{where}: {hash_name} does not match recomputed {domain} hash")
        return False
    return True


def _validate_condition_family(container, where, errors) -> bool:
    if not _check_keys(container, _CONDITION_FAMILY_KEYS, where, errors):
        return False
    if not isinstance(container["condition_family_id"], str) or not container["condition_family_id"]:
        errors.append(f"{where}.condition_family_id: must be a nonempty string")
    definition = container["condition_family_definition"]
    if not isinstance(definition, Mapping) or not definition:
        errors.append(f"{where}.condition_family_definition: must be a nonempty object")
        return False
    stored_hash = container["condition_family_sha256"]
    if not _is_hex(stored_hash):
        errors.append(f"{where}.condition_family_sha256: must be 64 lowercase hex chars")
        return False
    try:
        expected_hash = canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, definition)
    except (TypeError, ValueError):
        errors.append(f"{where}.condition_family_definition: is not canonical-JSON serializable")
        return False
    if stored_hash != expected_hash:
        errors.append(
            f"{where}.condition_family_sha256: does not match recomputed "
            f"{CONDITION_FAMILY_DOMAIN} hash"
        )
        return False
    return True


def _is_floor_j(value) -> bool:
    return _is_number(value) and 0 <= value < _MAX_FLOOR_J


def _validate_idle_drift_guard(guard, where, errors) -> None:
    if not _check_keys(guard, _IDLE_DRIFT_GUARD_KEYS, where, errors):
        return
    status = guard["calibration_status"]
    if guard["method"] != _IDLE_DRIFT_GUARD_METHOD:
        errors.append(f"{where}.method: must be {_IDLE_DRIFT_GUARD_METHOD!r}")
    hashes = guard["bundle_sha256"]
    if not isinstance(hashes, list):
        errors.append(f"{where}.bundle_sha256: must be an array")
        return
    if any(not _is_hex(value) for value in hashes):
        errors.append(f"{where}.bundle_sha256: entries must be 64 lowercase hex chars")
    if _has_duplicates(hashes):
        errors.append(f"{where}.bundle_sha256: entries must be unique")
    n = guard["n_bundles"]
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        errors.append(f"{where}.n_bundles: must be a nonnegative integer")
        return
    if n != len(hashes):
        errors.append(f"{where}: n_bundles and bundle_sha256 length disagree")
    if status == "pending_calibration":
        if n != 0 or hashes:
            errors.append(f"{where}: pending_calibration must have no bundles")
        for key in ("guard_w", "cell_id", "artifact_sha256"):
            if guard[key] is not None:
                errors.append(f"{where}.{key}: must be null while pending_calibration")
    elif status == "calibrated":
        if n < 2:
            errors.append(f"{where}: calibrated guard requires at least two bundles")
        if not _is_number(guard["guard_w"]) or guard["guard_w"] < 0:
            errors.append(f"{where}.guard_w: must be a finite nonnegative number")
        if not isinstance(guard["cell_id"], str) or not guard["cell_id"]:
            errors.append(f"{where}.cell_id: must be a nonempty string")
        if not _is_hex(guard["artifact_sha256"]):
            errors.append(f"{where}.artifact_sha256: must be 64 lowercase hex chars")
    else:
        errors.append(f"{where}.calibration_status: invalid status {status!r}")


def _validate_provenance(
    provenance, where, errors
) -> frozenset[str] | None:
    if not _check_keys_with_optional(
        provenance,
        _PROVENANCE_KEYS,
        _PROVENANCE_OPTIONAL_KEYS,
        where,
        errors,
    ):
        return None

    calibration_plan_sha256 = None
    calibration_plan = provenance["calibration_plan"]
    if _check_keys(
        calibration_plan,
        _CALIBRATION_PLAN_KEYS,
        f"{where}.calibration_plan",
        errors,
    ):
        if (
            not isinstance(calibration_plan["plan_id"], str)
            or not calibration_plan["plan_id"].strip()
        ):
            errors.append(
                f"{where}.calibration_plan.plan_id: must be a nonempty string"
            )
        if not _is_hex(calibration_plan["sha256"]):
            errors.append(
                f"{where}.calibration_plan.sha256: must be 64 lowercase hex chars"
            )
        else:
            calibration_plan_sha256 = calibration_plan["sha256"]
        if calibration_plan["declared_calibration_scope"] not in (
            _CALIBRATION_SCOPES
        ):
            errors.append(
                f"{where}.calibration_plan.declared_calibration_scope: "
                "must be a recognized calibration scope"
            )
        if (
            not isinstance(calibration_plan["relative_path"], str)
            or not calibration_plan["relative_path"].strip()
        ):
            errors.append(
                f"{where}.calibration_plan.relative_path: "
                "must be a nonempty string"
            )
    if (
        not isinstance(provenance["mint_tool_version"], str)
        or not provenance["mint_tool_version"].strip()
    ):
        errors.append(f"{where}.mint_tool_version: must be a nonempty string")

    mint_tool_version = provenance["mint_tool_version"]
    is_v2 = mint_tool_version == _FLOOR_MINT_TOOL_VERSION_V2
    implementation = provenance["implementation"]
    if _check_keys_with_optional(
        implementation,
        _IMPLEMENTATION_KEYS,
        _IMPLEMENTATION_OPTIONAL_KEYS,
        f"{where}.implementation",
        errors,
    ):
        if not _is_hex(implementation["project_commit"], length=40):
            errors.append(
                f"{where}.implementation.project_commit: "
                "must be 40 lowercase hex chars"
            )
        if implementation["project_tree_state"] not in ("clean", "dirty"):
            errors.append(
                f"{where}.implementation.project_tree_state: "
                "must be 'clean' or 'dirty'"
            )
        if implementation["python_package"] != "joulewise":
            errors.append(
                f"{where}.implementation.python_package: must be 'joulewise'"
            )
        for containment_key in (
            "mint_commit_contained_in_origin_main",
            "head_pin_commit_contained_in_origin_main",
        ):
            key_present = containment_key in implementation
            contains_commit = implementation.get(containment_key)
            if is_v2 and not (
                key_present
                and (
                    contains_commit is None
                    or isinstance(contains_commit, bool)
                )
            ):
                errors.append(
                    f"{where}.implementation.{containment_key}: "
                    "required boolean-or-null for the v2 mint"
                )
            if not is_v2 and key_present:
                errors.append(
                    f"{where}.implementation.{containment_key}: "
                    "allowed only for the v2 mint"
                )
    assurance = provenance.get("assurance")
    if is_v2:
        if not _check_keys(
            assurance,
            _ASSURANCE_KEYS,
            f"{where}.assurance",
            errors,
        ) or assurance != _V2_ASSURANCE_PROFILE:
            errors.append(
                f"{where}.assurance: must equal the canonical "
                "single_authority_hash_bound_replay.v1 profile"
            )
    elif assurance is not None:
        errors.append(f"{where}.assurance: allowed only for the v2 mint")
    custody_store = provenance.get("calibration_custody_store")
    if custody_store is not None:
        custody_where = f"{where}.calibration_custody_store"
        if not is_v2:
            errors.append(
                f"{custody_where}: allowed only for the v2 mint"
            )
        elif _check_keys(
            custody_store,
            _CALIBRATION_CUSTODY_STORE_KEYS,
            custody_where,
            errors,
        ):
            if custody_store["schema_version"] != (
                _CALIBRATION_CUSTODY_STORE_SCHEMA
            ):
                errors.append(
                    f"{custody_where}.schema_version: invalid custody store schema"
                )
            if not _is_hex(custody_store["manifest_sha256"]):
                errors.append(
                    f"{custody_where}.manifest_sha256: must be 64 lowercase hex chars"
                )
    producer_plans = provenance.get("producer_calibration_plans")
    if producer_plans is None:
        return (
            frozenset({calibration_plan_sha256})
            if calibration_plan_sha256 is not None
            else None
        )
    if provenance["mint_tool_version"] != _FLOOR_MINT_TOOL_VERSION_V2:
        errors.append(
            f"{where}.producer_calibration_plans: allowed only for the v2 multi-plan mint"
        )
        return None
    if not isinstance(producer_plans, list) or len(producer_plans) < 2:
        errors.append(
            f"{where}.producer_calibration_plans: must contain at least two plans"
        )
        return None
    producer_hashes: set[str] = set()
    producer_ids: set[str] = set()
    for index, producer in enumerate(producer_plans):
        producer_where = f"{where}.producer_calibration_plans[{index}]"
        if not _check_keys(
            producer,
            _CALIBRATION_PLAN_KEYS,
            producer_where,
            errors,
        ):
            continue
        plan_id = producer["plan_id"]
        plan_sha256 = producer["sha256"]
        if not _is_trimmed_string(plan_id):
            errors.append(f"{producer_where}.plan_id: must be a nonempty string")
        elif plan_id in producer_ids:
            errors.append(f"{producer_where}.plan_id: duplicate producer plan")
        else:
            producer_ids.add(plan_id)
        if not _is_hex(plan_sha256):
            errors.append(
                f"{producer_where}.sha256: must be 64 lowercase hex chars"
            )
        elif plan_sha256 in producer_hashes:
            errors.append(f"{producer_where}.sha256: duplicate producer plan hash")
        else:
            producer_hashes.add(plan_sha256)
        if producer["declared_calibration_scope"] not in _CALIBRATION_SCOPES:
            errors.append(
                f"{producer_where}.declared_calibration_scope: must be recognized"
            )
        if not _is_trimmed_string(producer["relative_path"]):
            errors.append(
                f"{producer_where}.relative_path: must be a nonempty string"
            )
    return frozenset(producer_hashes) if producer_hashes else None


def _validate_estimate_math(
    record,
    where,
    deviations,
    mean,
    prediction_extra,
    point_values,
    kind,
    errors,
) -> None:
    n = len(deviations)
    est = _floor_estimate(kind, list(deviations), mean, prediction_extra)
    classified_estimate = est
    widened_unguarded = est.unguarded_floor_j
    widened_guarded = est.guarded_floor_j
    widths = record["admissible_half_widths_j"]
    if (
        not isinstance(widths, list)
        or len(widths) != n
        or any(not _is_number(width) or width < 0.0 for width in widths)
    ):
        errors.append(
            f"{where}: admissible_half_widths_j must contain n finite nonnegative numbers"
        )
    else:
        try:
            corner_floor = _corner_maximized_unguarded_floor(
                point_values, widths, kind=kind
            )
        except (TypeError, ValueError) as exc:
            errors.append(f"{where}: widened floor cannot be recomputed: {exc}")
        else:
            widened_unguarded = max(est.unguarded_floor_j, corner_floor)
            widened_guarded = (
                est.guard_factor * widened_unguarded
                if est.guard_factor is not None
                else None
            )
            if not _close(
                record["corner_widened_unguarded_floor_j"],
                widened_unguarded,
            ):
                errors.append(
                    f"{where}: stored corner_widened_unguarded_floor_j does not match full corner enumeration"
                )
            if not _close(
                record["corner_widened_guarded_floor_j"], widened_guarded
            ):
                errors.append(
                    f"{where}: stored corner_widened_guarded_floor_j does not match full corner enumeration"
                )
            classified_estimate = _apply_admissible_set_guard(
                est,
                widened_unguarded,
                widths,
            )
    _validate_attribution_limit_metadata(
        record,
        classified_estimate,
        where,
        errors,
    )
    basis_sha256 = record.get("whole_window_evaluation_basis_sha256")
    if not _is_hex(basis_sha256):
        errors.append(
            f"{where}.whole_window_evaluation_basis_sha256: must be 64 lowercase hex chars"
        )
    semantics_id = record.get("consumption_semantics_id")
    if semantics_id not in _CONSUMPTION_SEMANTICS_IDS:
        errors.append(
            f"{where}.consumption_semantics_id: unknown whole-window "
            "consumption semantics"
        )
    allowance_record = record.get("whole_window_drift_allowance")
    allowance: float | None = None
    if _check_keys(
        allowance_record,
        _WHOLE_WINDOW_DRIFT_ALLOWANCE_KEYS,
        f"{where}.whole_window_drift_allowance",
        errors,
    ):
        claim_family = allowance_record["claim_family"]
        if claim_family not in {"gross_energy", "idle_subtracted_energy"}:
            errors.append(
                f"{where}.whole_window_drift_allowance.claim_family: invalid family"
            )
        observed = allowance_record["observed_trajectory_excursion_j"]
        derived = allowance_record["derived_repeatability_bound_j"]
        stored_allowance = allowance_record["allowance_j"]
        if any(
            not _is_number(value) or value < 0.0
            for value in (observed, derived)
        ) or not _is_number(stored_allowance) or stored_allowance <= 0.0:
            errors.append(
                f"{where}.whole_window_drift_allowance: numeric components must be finite, nonnegative, and allowance_j > 0"
            )
        elif not _close(stored_allowance, max(observed, derived)):
            errors.append(
                f"{where}.whole_window_drift_allowance.allowance_j: must equal max(observed, derived)"
            )
        else:
            allowance = float(stored_allowance)
        if not _is_hex(
            allowance_record["whole_window_evaluation_basis_sha256"]
        ):
            errors.append(
                f"{where}.whole_window_drift_allowance.whole_window_evaluation_basis_sha256: must be 64 lowercase hex chars"
            )
        elif allowance_record[
            "whole_window_evaluation_basis_sha256"
        ] != basis_sha256:
            errors.append(
                f"{where}.whole_window_drift_allowance.whole_window_evaluation_basis_sha256: does not match record basis"
            )
        provenance = allowance_record["provenance"]
        if _check_keys(
            provenance,
            _WHOLE_WINDOW_DRIFT_PROVENANCE_KEYS,
            f"{where}.whole_window_drift_allowance.provenance",
            errors,
        ):
            if not _is_hex(provenance["bound_derivation_sha256"]):
                errors.append(
                    f"{where}.whole_window_drift_allowance.provenance.bound_derivation_sha256: must be 64 lowercase hex chars"
                )
            if provenance["observed_component"] != (
                "trajectory_excursion_max_j"
            ) or provenance["derived_component"] != (
                "derived_repeatability_bound_j"
            ):
                errors.append(
                    f"{where}.whole_window_drift_allowance.provenance: component names are invalid"
                )
    if allowance is not None:
        if not _close(
            record.get("drift_widened_unguarded_floor_j"),
            widened_unguarded + allowance,
        ):
            errors.append(
                f"{where}: drift_widened_unguarded_floor_j must equal corner-widened floor plus allowance"
            )
        expected_drift_guarded = (
            widened_guarded + allowance
            if widened_guarded is not None
            else None
        )
        if not _close(
            record.get("drift_widened_guarded_floor_j"),
            expected_drift_guarded,
        ):
            errors.append(
                f"{where}: drift_widened_guarded_floor_j must equal corner-widened guarded floor plus allowance"
            )
    stddev_key = "sample_stddev_j"
    checks = [
        (stddev_key, est.sample_stddev_j),
        ("t_critical", est.t_critical),
        ("prediction_component_j", est.prediction_component_j),
        ("unguarded_floor_j", widened_unguarded),
    ]
    for key in (
        "sample_stddev_j",
        "prediction_component_j",
        "unguarded_floor_j",
        "guarded_floor_j",
    ):
        value = record.get(key)
        if value is not None and not _is_floor_j(value):
            errors.append(f"{where}: {key} must be finite, nonnegative, and < {_MAX_FLOOR_J:g} J")
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
        if not _close(record.get("guarded_floor_j"), widened_guarded):
            errors.append(f"{where}: stored guarded_floor_j does not match recomputed value")


def _validate_attribution_limit_metadata(
    record,
    estimate: FloorEstimate,
    where,
    errors,
) -> None:
    present = set(record) & _ATTRIBUTION_LIMIT_RECORD_KEYS
    expected = admissible_set_uncertainty_dominates_point_floor(estimate)
    if present and present != _ATTRIBUTION_LIMIT_RECORD_KEYS:
        errors.append(
            f"{where}: attribution-limit metadata fields must be present together"
        )
        return
    if expected and present != _ATTRIBUTION_LIMIT_RECORD_KEYS:
        errors.append(
            f"{where}: attribution-limited floor requires labelled metadata"
        )
        return
    if not expected and present:
        errors.append(
            f"{where}: attribution-limit metadata is forbidden when uncertainty does not dominate"
        )
        return
    if not present:
        return
    if record.get("floor_source") != ATTRIBUTION_FLOOR_SOURCE:
        errors.append(
            f"{where}.floor_source: must name {ATTRIBUTION_FLOOR_SOURCE!r}"
        )
    if record.get("floor_limit_class") != ATTRIBUTION_LIMIT_CLASS:
        errors.append(
            f"{where}.floor_limit_class: must be {ATTRIBUTION_LIMIT_CLASS!r}"
        )
    diagnostic = record.get("point_floor_diagnostic")
    expected_diagnostic = _point_floor_diagnostic(estimate)
    if _check_keys(
        diagnostic,
        _POINT_FLOOR_DIAGNOSTIC_KEYS,
        f"{where}.point_floor_diagnostic",
        errors,
    ):
        if diagnostic.get("label") != "repeatability_diagnostic":
            errors.append(
                f"{where}.point_floor_diagnostic.label: must identify repeatability"
            )
        if diagnostic.get("published_claim_floor") is not False:
            errors.append(
                f"{where}.point_floor_diagnostic.published_claim_floor: must be false"
            )
        for key in ("unguarded_floor_j", "guard_factor", "guarded_floor_j"):
            if not _close(diagnostic.get(key), expected_diagnostic[key]):
                errors.append(
                    f"{where}.point_floor_diagnostic.{key}: does not match point-only floor"
                )
    if record.get("single_count_discipline") != (
        attribution_single_count_discipline()
    ):
        errors.append(
            f"{where}.single_count_discipline: must preserve the clause-11 composition rule"
        )


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


def _validate_stress_observed(observed, where, errors) -> bool:
    error_count = len(errors)
    allowed = set(_ENVELOPE_FIELDS) | {"bound_terms"}
    if not _check_keys(observed, allowed, where, errors):
        return False
    for field in _ENVELOPE_FIELDS:
        value = observed[field]
        if not _is_number(value) or value < 0:
            errors.append(f"{where}.{field}: must be a finite nonnegative number")
    _validate_bound_terms(observed["bound_terms"], where, errors)
    return len(errors) == error_count


def _validate_source_regime(regime, where, errors) -> bool:
    if not _check_keys(
        regime,
        {"stack_identity", "stack_identity_sha256", "stress_observed"},
        where,
        errors,
    ):
        return False
    stack_valid = _validate_hashed_object(
        regime["stack_identity"],
        object_keys=_STACK_IDENTITY_KEYS,
        stored_hash=regime["stack_identity_sha256"],
        hash_name="stack_identity_sha256",
        domain=STACK_IDENTITY_DOMAIN,
        where=f"{where}.stack_identity",
        errors=errors,
    )
    stress_valid = _validate_stress_observed(
        regime["stress_observed"],
        f"{where}.stress_observed",
        errors,
    )
    return stack_valid and stress_valid


def _component_bundle_rows(component_name: str, record: Mapping) -> list[Mapping]:
    if component_name == "absolute":
        observations = record.get("bundle_observations")
        return list(observations) if isinstance(observations, list) else []
    rows = []
    blocks = record.get("blocks")
    if not isinstance(blocks, list):
        return rows
    for block in blocks:
        members = block.get("members") if isinstance(block, Mapping) else None
        if isinstance(members, list):
            rows.extend(member for member in members if isinstance(member, Mapping))
    return rows


def _validate_component_provenance(
    component_name: str,
    provenance,
    record: Mapping,
    where: str,
    errors,
    evidence_root_ids: frozenset[str] | None,
) -> tuple[Mapping | None, set[str]]:
    if not _check_keys(
        provenance,
        _COMPONENT_PROVENANCE_KEYS,
        where,
        errors,
    ):
        return None, set()
    if (
        not isinstance(provenance["calibration_cell_id"], str)
        or not provenance["calibration_cell_id"].strip()
    ):
        errors.append(f"{where}.calibration_cell_id: must be a nonempty string")
    evidence_root_id = provenance["evidence_root_id"]
    if not _is_trimmed_string(evidence_root_id):
        errors.append(
            f"{where}.evidence_root_id: must be a nonempty trimmed string"
        )
    elif evidence_root_ids is not None and evidence_root_id not in evidence_root_ids:
        errors.append(
            f"{where}.evidence_root_id: not pinned by artifact family pinset"
        )
    order_manifest = provenance["order_manifest"]
    if _check_keys(
        order_manifest,
        _ORDER_MANIFEST_KEYS,
        f"{where}.order_manifest",
        errors,
    ):
        if (
            not isinstance(order_manifest["manifest_id"], str)
            or not order_manifest["manifest_id"].strip()
        ):
            errors.append(
                f"{where}.order_manifest.manifest_id: "
                "must be a nonempty string"
            )
        if not _is_hex(order_manifest["sha256"]):
            errors.append(
                f"{where}.order_manifest.sha256: "
                "must be 64 lowercase hex chars"
            )
    for descriptor_name, descriptor_keys in (
        ("campaign_log", _CAMPAIGN_LOG_KEYS),
        ("extraction_report", _HASH_PIN_KEYS),
        ("extraction_spec", _HASH_PIN_KEYS),
    ):
        descriptor = provenance[descriptor_name]
        if _check_keys(
            descriptor,
            descriptor_keys,
            f"{where}.{descriptor_name}",
            errors,
        ) and not _is_hex(descriptor["sha256"]):
            errors.append(
                f"{where}.{descriptor_name}.sha256: "
                "must be 64 lowercase hex chars"
            )
    bundle_ids = provenance["bundle_ids"]
    bundle_hashes = provenance["bundle_sha256s"]
    if not isinstance(bundle_ids, list) or not isinstance(bundle_hashes, list):
        errors.append(f"{where}: bundle_ids and bundle_sha256s must be arrays")
        bundle_ids = []
        bundle_hashes = []
    else:
        if len(bundle_ids) != len(bundle_hashes):
            errors.append(
                f"{where}: bundle_ids and bundle_sha256s lengths disagree"
            )
        if _has_duplicates(bundle_ids):
            errors.append(f"{where}: source bundle_ids must be unique")
        if any(not isinstance(value, str) or not value for value in bundle_ids):
            errors.append(f"{where}: bundle_ids must be nonempty strings")
        if any(not _is_hex(value) for value in bundle_hashes):
            errors.append(
                f"{where}: bundle_sha256s must be 64 lowercase hex chars"
            )
    component_rows = _component_bundle_rows(component_name, record)
    expected_ids = [row.get("bundle_id") for row in component_rows]
    expected_hashes = [row.get("bundle_sha256") for row in component_rows]
    if bundle_ids != expected_ids:
        errors.append(
            f"{where}.bundle_ids: must positionally equal component members"
        )
    if bundle_hashes != expected_hashes:
        errors.append(
            f"{where}.bundle_sha256s: must positionally equal component members"
        )
    regime = provenance["source_regime"]
    regime_valid = _validate_source_regime(
        regime,
        f"{where}.source_regime",
        errors,
    )
    return (
        regime if regime_valid else None,
        {value for value in bundle_ids if isinstance(value, str)},
    )


def _validate_absolute(record, where, errors) -> None:
    if not _check_keys_with_optional(
        record,
        _ABS_KEYS,
        _ATTRIBUTION_LIMIT_RECORD_KEYS,
        where,
        errors,
    ):
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
    structural_error = False
    if n < 2:
        errors.append(f"{where}: n must be at least 2")
        structural_error = True
    if not residuals:
        errors.append(f"{where}: residuals_j must be a nonempty array")
        structural_error = True
    if not observations:
        errors.append(f"{where}: bundle_observations must be a nonempty array")
        structural_error = True
    if not (n == len(residuals) == len(observations)):
        errors.append(f"{where}: n, residuals_j, and bundle_observations lengths disagree")
        structural_error = True
    if structural_error:
        return
    values = []
    bundle_ids = []
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
        bundle_ids.append(obs["bundle_id"])
    if _has_duplicates(bundle_ids):
        errors.append(f"{where}: source bundle_ids must be unique")
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
    if not _is_floor_j(record["max_abs_residual_j"]):
        errors.append(f"{where}: max_abs_residual_j must be finite, nonnegative, and < {_MAX_FLOOR_J:g} J")
    _validate_estimate_math(
        record,
        where,
        expected_residuals,
        mean,
        0.0,
        values,
        "absolute",
        errors,
    )


def _validate_comparative(
    record,
    where,
    errors,
    calibration_plan_sha256s: frozenset[str] | None = None,
) -> None:
    if not _check_keys_with_optional(
        record,
        _CMP_KEYS,
        _CMP_OPTIONAL_KEYS,
        where,
        errors,
    ):
        return
    if "estimator_registration" in record and not (
        validate_common_mode_estimator_registration(
            record["estimator_registration"]
        )
    ):
        errors.append(
            f"{where}.estimator_registration: invalid registered candidate identity"
        )
    deltas = record["block_deltas_j"]
    blocks = record["blocks"]
    n = record["n_blocks"]
    if not isinstance(n, int) or isinstance(n, bool):
        errors.append(f"{where}: n_blocks must be an integer")
        return
    if not isinstance(deltas, list) or not isinstance(blocks, list):
        errors.append(f"{where}: block_deltas_j and blocks must be arrays")
        return
    structural_error = False
    if n < 2:
        errors.append(f"{where}: n_blocks must be at least 2")
        structural_error = True
    if not deltas:
        errors.append(f"{where}: block_deltas_j must be a nonempty array")
        structural_error = True
    if not blocks:
        errors.append(f"{where}: blocks must be a nonempty array")
        structural_error = True
    if not (n == len(deltas) == len(blocks)):
        errors.append(f"{where}: n_blocks, block_deltas_j, and blocks lengths disagree")
        structural_error = True
    if structural_error:
        return
    expected_deltas = []
    source_bundle_ids = []
    for i, block in enumerate(blocks):
        block_where = f"{where}.blocks[{i}]"
        if not _check_keys(block, _BLOCK_KEYS, block_where, errors):
            return
        if not _is_hex(block["calibration_plan_sha256"]):
            errors.append(
                f"{block_where}.calibration_plan_sha256: must be 64 lowercase hex chars"
            )
        elif (
            calibration_plan_sha256s is None
            or block["calibration_plan_sha256"] not in calibration_plan_sha256s
        ):
            errors.append(
                f"{block_where}.calibration_plan_sha256: does not match artifact provenance"
            )
        expected_labels = ["A", "B", "B", "A"]
        executed_labels = block["executed_labels"]
        if executed_labels != expected_labels:
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
            expected_label = (
                executed_labels[j]
                if isinstance(executed_labels, list) and j < len(executed_labels)
                else None
            )
            if member["plan_label"] != expected_label:
                errors.append(
                    f"{member_where}.plan_label: does not match executed label sequence"
                )
            if (
                isinstance(member["plan_sequence_index"], bool)
                or member["plan_sequence_index"] != j + 1
            ):
                errors.append(
                    f"{member_where}.plan_sequence_index: must match member order"
                )
            by_position[member["position"]] = member["metric_value_j"]
            source_bundle_ids.append(member["bundle_id"])
        if [m["position"] for m in members] != ["A1", "B1", "B2", "A2"]:
            errors.append(f"{block_where}: member positions must be A1/B1/B2/A2 in order")
            return
        expected = abba_delta(by_position["A1"], by_position["B1"], by_position["B2"], by_position["A2"])
        expected_deltas.append(expected)
        if not _close(block["delta_j"], expected):
            errors.append(f"{block_where}: stored delta_j does not match members")
        if not _close(deltas[i], expected):
            errors.append(f"{where}: block_deltas_j[{i}] does not match block members")
    if _has_duplicates(source_bundle_ids):
        errors.append(f"{where}: source bundle_ids must be unique")
    if any(not _is_number(d) for d in deltas):
        errors.append(f"{where}: block_deltas_j must all be finite numbers")
        return
    mean = sum(expected_deltas) / n
    if not _close(record["mean_delta_j"], mean):
        errors.append(f"{where}: stored mean_delta_j does not match blocks")
    if not _close(record["max_abs_delta_j"], max(abs(d) for d in expected_deltas)):
        errors.append(f"{where}: stored max_abs_delta_j does not match recomputed value")
    if not _is_floor_j(record["max_abs_delta_j"]):
        errors.append(f"{where}: max_abs_delta_j must be finite, nonnegative, and < {_MAX_FLOOR_J:g} J")
    _validate_estimate_math(
        record,
        where,
        expected_deltas,
        mean,
        abs(mean),
        expected_deltas,
        "comparative",
        errors,
    )


def _validate_cell(
    cell,
    where,
    errors,
    calibration_plan_sha256s: frozenset[str] | None = None,
    evidence_root_ids: frozenset[str] | None = None,
) -> None:
    if not _check_keys_with_optional(
        cell,
        _CELL_KEYS,
        _ATTRIBUTION_LIMIT_CONTAINER_KEYS,
        where,
        errors,
    ):
        return
    if _check_keys(cell["key"], _KEY_KEYS, f"{where}.key", errors):
        try:
            validate_floor_metric_window_class(
                cell["key"]["metric"],
                cell["key"]["window_class"],
            )
        except ValueError as exc:
            errors.append(f"{where}.key: {exc}")
        _validate_condition_family(
            {
                key: cell["key"][key]
                for key in _CONDITION_FAMILY_KEYS
            },
            f"{where}.key",
            errors,
        )
    eligibility_valid = _check_keys(
        cell["eligibility"], _ELIGIBILITY_KEYS, f"{where}.eligibility", errors
    )
    if eligibility_valid:
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
        elif eligibility["claim_usable"] != (eligibility["status"] == "claim_ready"):
            errors.append(
                f"{where}.eligibility: claim_usable must equal claim_ready and not stale"
            )

    absolute = cell["absolute"]
    comparative = cell["comparative"]
    if absolute is not None:
        _validate_absolute(cell["absolute"], f"{where}.absolute", errors)
    if comparative is not None:
        _validate_comparative(
            cell["comparative"],
            f"{where}.comparative",
            errors,
            calibration_plan_sha256s,
        )
    metric = cell["key"].get("metric") if isinstance(cell["key"], Mapping) else None
    expected_claim_family = (
        "idle_subtracted_energy"
        if metric in {"energy_request_j", "idle_subtracted_energy_j"}
        else "gross_energy"
    )
    present_records = [
        record for record in (absolute, comparative) if isinstance(record, Mapping)
    ]
    limited_records = [
        record
        for record in present_records
        if record.get("floor_limit_class") == ATTRIBUTION_LIMIT_CLASS
    ]
    present_limit_keys = set(cell) & _ATTRIBUTION_LIMIT_CONTAINER_KEYS
    if limited_records:
        if present_limit_keys != _ATTRIBUTION_LIMIT_CONTAINER_KEYS:
            errors.append(
                f"{where}: attribution-limited component requires complete cell metadata"
            )
        else:
            if cell.get("floor_source") != ATTRIBUTION_FLOOR_SOURCE:
                errors.append(
                    f"{where}.floor_source: must name {ATTRIBUTION_FLOOR_SOURCE!r}"
                )
            if cell.get("floor_limit_class") != ATTRIBUTION_LIMIT_CLASS:
                errors.append(
                    f"{where}.floor_limit_class: must be {ATTRIBUTION_LIMIT_CLASS!r}"
                )
            expected_diagnostics = {
                name: record["point_floor_diagnostic"]
                for name, record in (
                    ("absolute", absolute),
                    ("comparative", comparative),
                )
                if isinstance(record, Mapping)
                and record.get("floor_limit_class")
                == ATTRIBUTION_LIMIT_CLASS
            }
            if cell.get("point_floor_diagnostics") != expected_diagnostics:
                errors.append(
                    f"{where}.point_floor_diagnostics: must match labelled components"
                )
            if cell.get("single_count_discipline") != (
                attribution_single_count_discipline()
            ):
                errors.append(
                    f"{where}.single_count_discipline: must preserve the clause-11 composition rule"
                )
    elif present_limit_keys:
        errors.append(
            f"{where}: attribution-limit cell metadata is forbidden without a labelled component"
        )
    for record in present_records:
        allowance_record = record.get("whole_window_drift_allowance")
        if (
            isinstance(allowance_record, Mapping)
            and allowance_record.get("claim_family") != expected_claim_family
        ):
            errors.append(
                f"{where}: whole-window drift allowance claim_family does not match metric"
            )

    expected_abs = (
        absolute.get("drift_widened_guarded_floor_j")
        if isinstance(absolute, Mapping)
        else None
    )
    expected_cmp = (
        comparative.get("drift_widened_guarded_floor_j")
        if isinstance(comparative, Mapping)
        else None
    )
    for key in ("floor_abs_j", "floor_cmp_j", "floor_gate_j"):
        value = cell[key]
        if value is not None and not _is_floor_j(value):
            errors.append(f"{where}: {key} must be finite, nonnegative, and < {_MAX_FLOOR_J:g} J")
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
    regime_valid = _validate_source_regime(
        regime,
        f"{where}.source_regime",
        errors,
    )

    if not isinstance(cell["transport_group_id"], str) or not cell["transport_group_id"]:
        errors.append(f"{where}: transport_group_id must be a nonempty string")

    provenance = cell["provenance"]
    component_regimes: dict[str, Mapping] = {}
    component_bundle_ids: dict[str, set[str]] = {}
    if _check_keys(provenance, _CELL_PROVENANCE_KEYS, f"{where}.provenance", errors):
        for component_name, component_record in (
            ("absolute", absolute),
            ("comparative", comparative),
        ):
            component_provenance = provenance[component_name]
            component_where = f"{where}.provenance.{component_name}"
            if component_record is None:
                if component_provenance is not None:
                    errors.append(
                        f"{component_where}: forbidden without a component record"
                    )
                continue
            if not isinstance(component_provenance, Mapping):
                errors.append(
                    f"{component_where}: required for the component record"
                )
                continue
            source_regime, bundle_ids = (
                _validate_component_provenance(
                    component_name,
                    component_provenance,
                    component_record,
                    component_where,
                    errors,
                    evidence_root_ids,
                )
            )
            if source_regime is not None:
                component_regimes[component_name] = source_regime
            component_bundle_ids[component_name] = bundle_ids
    if (
        "absolute" in component_bundle_ids
        and "comparative" in component_bundle_ids
        and component_bundle_ids["absolute"]
        & component_bundle_ids["comparative"]
    ):
        errors.append(
            f"{where}.provenance: absolute and comparative bundle members "
            "must be disjoint"
        )
    if regime_valid and component_regimes:
        cell_stack_hash = regime["stack_identity_sha256"]
        for component_name, component_regime in component_regimes.items():
            if component_regime["stack_identity_sha256"] != cell_stack_hash:
                errors.append(
                    f"{where}.provenance.{component_name}.source_regime: "
                    "stack identity must match the cell"
                )
        if len(component_regimes) == len(present_records):
            try:
                expected_regime = _compose_component_source_regimes(
                    [
                        component_regimes[name]
                        for name in ("absolute", "comparative")
                        if name in component_regimes
                    ]
                )
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(
                    f"{where}.source_regime: component composition failed: {exc}"
                )
            else:
                expected_stress = expected_regime["stress_observed"]
                actual_stress = regime["stress_observed"]
                for field in _ENVELOPE_FIELDS:
                    if not _close(actual_stress[field], expected_stress[field]):
                        errors.append(
                            f"{where}.source_regime.stress_observed.{field}: "
                            "does not match componentwise composition"
                        )
                for term in _BOUND_TERMS:
                    actual_term = actual_stress["bound_terms"][term]
                    expected_term = expected_stress["bound_terms"][term]
                    if (
                        actual_term["applicability"]
                        != expected_term["applicability"]
                        or not _close(
                            actual_term["maximum"],
                            expected_term["maximum"],
                        )
                    ):
                        errors.append(
                            f"{where}.source_regime.stress_observed.bound_terms."
                            f"{term}: does not match fail-closed component "
                            "composition"
                        )

    if eligibility_valid and cell["eligibility"]["status"] == "claim_ready":
        eligibility = cell["eligibility"]
        if eligibility["use_role"] != "primary_claim_gate":
            errors.append(f"{where}.eligibility: claim_ready requires primary_claim_gate use_role")
        if not isinstance(absolute, Mapping) or not isinstance(
            comparative,
            Mapping,
        ):
            errors.append(
                f"{where}.eligibility: claim_ready requires both absolute "
                "and comparative components"
            )
        if set(component_regimes) != {"absolute", "comparative"}:
            errors.append(
                f"{where}.eligibility: claim_ready requires component-scoped "
                "provenance for both components"
            )
        minimum_n = eligibility["minimum_claim_n"]
        if isinstance(minimum_n, int) and not isinstance(minimum_n, bool):
            absolute_n = absolute.get("n") if isinstance(absolute, Mapping) else None
            comparative_n = comparative.get("n_blocks") if isinstance(comparative, Mapping) else None
            if not isinstance(absolute_n, int) or absolute_n < minimum_n:
                errors.append(f"{where}.eligibility: claim_ready absolute n is below minimum_claim_n")
            if not isinstance(comparative_n, int) or comparative_n < minimum_n:
                errors.append(f"{where}.eligibility: claim_ready comparative n is below minimum_claim_n")
        if expected_abs is None or expected_cmp is None:
            errors.append(f"{where}.eligibility: claim_ready requires both floor components")
        if isinstance(regime, Mapping):
            terms = regime.get("stress_observed", {}).get("bound_terms", {})
            if isinstance(terms, Mapping) and any(
                isinstance(entry, Mapping) and entry.get("applicability") == "unknown"
                for entry in terms.values()
            ):
                errors.append(f"{where}.eligibility: claim_ready forbids unknown regime terms")


def _validate_transport_group(group, where, cells_by_id, errors) -> None:
    if not _check_keys_with_optional(
        group,
        _GROUP_KEYS,
        _ATTRIBUTION_LIMIT_CONTAINER_KEYS,
        where,
        errors,
    ):
        return
    if group["rule_id"] != TRANSPORT_RULE_ID:
        errors.append(f"{where}: rule_id must be {TRANSPORT_RULE_ID!r}")
    _validate_hashed_object(
        group["stack_identity"],
        object_keys=_STACK_IDENTITY_KEYS,
        stored_hash=group["stack_identity_sha256"],
        hash_name="stack_identity_sha256",
        domain=STACK_IDENTITY_DOMAIN,
        where=f"{where}.stack_identity",
        errors=errors,
    )
    source_ids = group["source_cell_ids"]
    if not isinstance(source_ids, list) or not source_ids:
        errors.append(f"{where}: source_cell_ids must be a nonempty array")
        return
    if _has_duplicates(source_ids):
        errors.append(f"{where}: source_cell_ids must be unique")
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
        stack_sha = cell["source_regime"].get("stack_identity_sha256")
        if stack_sha != group["stack_identity_sha256"]:
            errors.append(f"{where}: source cell {cell_id!r} stack identity differs from group")
    if any(not _is_number(cell.get("floor_gate_j")) for cell in sources):
        errors.append(f"{where}: every source cell needs numeric floors")
        return
    composed = compose_transport_group(sources)
    for field in ("composed_floor_abs_j", "composed_floor_cmp_j", "composed_floor_gate_j"):
        if not _is_floor_j(group[field]):
            errors.append(f"{where}: {field} must be finite, nonnegative, and < {_MAX_FLOOR_J:g} J")
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
    limited_sources = [
        cell
        for cell in sources
        if cell.get("floor_limit_class") == ATTRIBUTION_LIMIT_CLASS
    ]
    present_limit_keys = set(group) & _ATTRIBUTION_LIMIT_CONTAINER_KEYS
    if limited_sources:
        expected_diagnostics = {
            str(cell["cell_id"]): cell["point_floor_diagnostics"]
            for cell in limited_sources
        }
        if present_limit_keys != _ATTRIBUTION_LIMIT_CONTAINER_KEYS:
            errors.append(
                f"{where}: attribution-limited source requires complete group metadata"
            )
        else:
            if group.get("floor_source") != ATTRIBUTION_FLOOR_SOURCE:
                errors.append(
                    f"{where}.floor_source: must name {ATTRIBUTION_FLOOR_SOURCE!r}"
                )
            if group.get("floor_limit_class") != ATTRIBUTION_LIMIT_CLASS:
                errors.append(
                    f"{where}.floor_limit_class: must be {ATTRIBUTION_LIMIT_CLASS!r}"
                )
            if group.get("point_floor_diagnostics") != expected_diagnostics:
                errors.append(
                    f"{where}.point_floor_diagnostics: must preserve source diagnostics"
                )
            if group.get("single_count_discipline") != (
                attribution_single_count_discipline()
            ):
                errors.append(
                    f"{where}.single_count_discipline: must preserve the clause-11 composition rule"
                )
    elif present_limit_keys:
        errors.append(
            f"{where}: attribution-limit group metadata is forbidden without a labelled source"
        )
    families = group["allowed_consumer_condition_families"]
    if not isinstance(families, list):
        errors.append(f"{where}: allowed_consumer_condition_families must be an array")
    else:
        for i, family in enumerate(families):
            family_where = f"{where}.allowed_consumer_condition_families[{i}]"
            _validate_condition_family(family, family_where, errors)


def validate_floor_artifact(
    value: Mapping,
    *,
    pinset_path: Path | None = None,
    expected_pinset_sha256: str | None = None,
) -> list:
    """Validate a ``joulewise.detection_floor_artifact.v2`` document.

    Returns a list of error strings; an empty list means valid. Recomputes
    every residual, delta, mean, stddev, prediction, unguarded/guarded floor,
    guard factor, cell gate, and transport composition against the stored
    values within ``max(1e-12, 1e-12 * abs(expected))``. Evidence-root ids
    must be exact literals in the uniquely matching family pinset. The default
    route resolves reviewed repository pinsets. The explicit route requires
    both ``pinset_path`` and ``expected_pinset_sha256``; this function re-reads
    the file, rejects symlinks/non-regular files, authenticates the exact bytes,
    and only then parses the closed pinset schema.
    """
    errors: list = []
    if not _check_keys(value, _TOP_KEYS, "artifact", errors):
        return errors
    if value["schema_version"] != SCHEMA_VERSION:
        errors.append(f"artifact: schema_version must be {SCHEMA_VERSION!r}")
    if value["calibration_scope"] not in _CALIBRATION_SCOPES:
        errors.append("artifact: invalid calibration_scope")
    if value["source_class"] not in _SOURCE_CLASSES:
        errors.append("artifact: invalid source_class")
    if not isinstance(value["artifact_id"], str) or not value["artifact_id"]:
        errors.append("artifact: artifact_id must be a nonempty string")
    evidence_root_ids, pinset_error = _resolve_evidence_root_ids(
        value,
        pinset_path,
        expected_pinset_sha256,
    )
    if pinset_error is not None:
        errors.append(pinset_error)
    if value["method"] != build_method_block():
        errors.append("artifact: method block does not match the canonical v1 method")
    calibration_plan_sha256s = _validate_provenance(
        value["provenance"],
        "artifact.provenance",
        errors,
    )
    _validate_idle_drift_guard(value["idle_drift_guard"], "artifact.idle_drift_guard", errors)

    cells = value["cells"]
    if not isinstance(cells, list):
        errors.append("artifact: cells must be an array")
        return errors
    if not cells:
        errors.append("artifact: cells must be a nonempty array")
    cells_by_id: dict = {}
    seen_keys = set()
    for i, cell in enumerate(cells):
        where = f"cells[{i}]"
        _validate_cell(
            cell,
            where,
            errors,
            calibration_plan_sha256s,
            evidence_root_ids,
        )
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
    if not groups:
        errors.append("artifact: transport_groups must be a nonempty array")
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
            continue
        if not isinstance(cell, Mapping):
            continue
        group = next(
            (
                candidate
                for candidate in groups
                if isinstance(candidate, Mapping)
                and candidate.get("transport_group_id") == cell.get("transport_group_id")
            ),
            None,
        )
        if group is None:
            continue
        eligibility = cell.get("eligibility", {})
        if eligibility.get("status") != "claim_ready":
            continue
        if cell.get("cell_id") not in (group.get("source_cell_ids") or []):
            errors.append(f"cells[{i}].eligibility: claim_ready requires complete transport membership")
        key = cell.get("key", {})
        if not any(
            isinstance(family, Mapping)
            and family.get("condition_family_id") == key.get("condition_family_id")
            and family.get("condition_family_sha256") == key.get("condition_family_sha256")
            and family.get("condition_family_definition") == key.get("condition_family_definition")
            for family in (group.get("allowed_consumer_condition_families") or [])
        ):
            errors.append(
                f"cells[{i}].eligibility: claim_ready condition family missing from transport group"
            )
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
    *,
    artifact_sha256: Optional[str] = None,
    expected_artifact_sha256: Optional[str] = None,
    artifact_schema_valid: bool = True,
) -> tuple:
    """Pure Unit 6.2 transport check; empty tuple means transport is allowed.

    A floor cell/group must refuse to bound a different regime unless every
    predeclared conservative check passes: exact stack identity, predeclared
    condition family, consumer power/duration inside the measured bracket,
    and consumer cadence/clock/interpolation/drift evidence no worse than the
    composed calibration envelope. Missing or unknown consumer evidence
    refuses (``consumer_term_unknown``); nothing is extrapolated and no ad hoc
    margin is added. Optional artifact hash and schema-validation inputs make
    the two artifact-level refusal codes reachable before transport checks.
    """
    reasons: list = []

    def refuse(reason: str) -> None:
        if reason not in reasons:
            reasons.append(reason)

    if not artifact_schema_valid:
        refuse("artifact_schema_invalid")
    if expected_artifact_sha256 is not None and artifact_sha256 != expected_artifact_sha256:
        refuse("artifact_hash_mismatch")

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
