"""Inserted-gap transfer-fiducial diagnostics (TRANSFER-FIDUCIAL-01).

This module is deliberately diagnostic-only.  It classifies bundles by
structural config/event evidence, reuses the governed powermetrics pulse
estimator without modifying its rules, and assembles a capture that can never
mint a floor or license a claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from joulewise import powermetrics_fiducial
from joulewise.powermetrics_fiducial import (
    FIT_HALF_RANGE_S,
    MIN_AUTHENTICATED_BASELINE_S,
    MIN_AUTHENTICATED_PULSE_DURATION_S,
    PRIMARY_RAIL,
    CommandedPulse,
    TraceInterval,
    clock_stamp_half_width_s,
)
from joulewise.uncertainty_evidence import (
    ANCHOR_METHOD_VERSIONS,
    stamp_from_mapping,
    valid_clock_stamp,
)

TRANSFER_FIDUCIAL_GAP_S_V1 = 0.5
TRANSFER_FIDUCIAL_DIAGNOSTIC_KIND = "transfer_fiducial_v1"
TRANSFER_FIDUCIAL_CLAIM_REFUSAL = "transfer_fiducial_claim_ineligible"
TRANSFER_FIDUCIAL_CLASS_INCONSISTENT = (
    "transfer_fiducial_class_inconsistent"
)
TRANSFER_FIDUCIAL_CAPTURE_SCHEMA = "joulewise.transfer_fiducial_capture.v1"
TRANSFER_FIDUCIAL_PLAN_SCHEMA = "joulewise.transfer_fiducial_plan.v1"
TRANSFER_FIDUCIAL_PRE_DATA_RECEIPT_SCHEMA = (
    "joulewise.transfer_fiducial_pre_data_receipt.v1"
)
TRANSFER_FIDUCIAL_BOUNDARY_SEMANTICS = "first_yield_one_step_queued"
TRANSFER_FIDUCIAL_ESTIMATOR_SHA256 = (
    "386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92"
)

_GAP_EVENT_TYPES = frozenset({"fiducial_gap_start", "fiducial_gap_end"})
_FIT_SUCCESS = "fitted"
_INCONCLUSIVE = "inconclusive"
_FITTER_SOURCE_REL = Path("scripts/fit_transfer_fiducial.py")
_POST_WINDOW_SAMPLING_DWELL_S = 6.0
_RADIUS_RULE = (
    "radius = max(abs(residual_lower_s), abs(residual_upper_s)) "
    "+ effective_clock_anchor_bound_s"
)
_SUPPORTED_RULE = "supported iff residual_transfer_s <= b_pulse_s"


class TransferFiducialError(ValueError):
    """A malformed plan or capture input that cannot be interpreted."""


def transfer_fiducial_rule_constants() -> dict[str, Any]:
    """Return every value or rule string that can decide a transfer verdict."""

    return {
        "minimum_prefill_s": MIN_AUTHENTICATED_PULSE_DURATION_S,
        "minimum_decode_s": MIN_AUTHENTICATED_PULSE_DURATION_S,
        "post_window_sampling_dwell_s": _POST_WINDOW_SAMPLING_DWELL_S,
        "minimum_outside_baseline_s": MIN_AUTHENTICATED_BASELINE_S,
        "radius_rule": _RADIUS_RULE,
        "supported_rule": _SUPPORTED_RULE,
    }


@dataclass(frozen=True)
class TransferFiducialClass:
    """Structural diagnostic class derived independently from config/events."""

    is_diagnostic: bool
    by_config: bool
    by_events: bool
    inconsistent: bool


@dataclass(frozen=True)
class TransferFiducialRunFit:
    """Complete fit receipt for one planned diagnostic bundle."""

    bundle_id: str
    verdict: str
    reasons: tuple[str, ...]
    classification: TransferFiducialClass
    config_sha256: str | None = None
    source_commit: str | None = None
    model: Mapping[str, Any] | None = None
    quantization: Mapping[str, Any] | None = None
    hardware_target: Mapping[str, Any] | None = None
    workload_profile: Mapping[str, Any] | None = None
    device_identity: Mapping[str, Any] | None = None
    instrument_calibration: Mapping[str, Any] | None = None
    boundary_events: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    gap_events: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    commanded_gap_s: float | None = None
    observed_gap_s: float | None = None
    active_window_durations_s: tuple[float, float] | None = None
    trace_anchor_method: str | None = None
    effective_clock_anchor_bound_s: float | None = None
    outside_baseline_after_margins_s: float | None = None
    requested_post_window_sampling_dwell_s: float | None = None
    constructed_pulses: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    pulse_fits: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    detector: Mapping[str, Any] | None = None
    target_edges: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def classify_bundle(
    config_mapping: Mapping[str, Any] | None,
    events_rows: Sequence[Mapping[str, Any]] | None,
) -> TransferFiducialClass:
    """Classify by config OR event evidence, never by tags or prose."""

    workload = (
        config_mapping.get("workload_profile")
        if isinstance(config_mapping, Mapping)
        else None
    )
    by_config = bool(
        isinstance(workload, Mapping)
        and workload.get("transfer_fiducial_gap_s") is not None
    )
    by_events = any(
        isinstance(row, Mapping) and row.get("event_type") in _GAP_EVENT_TYPES
        for row in (events_rows or ())
    )
    return TransferFiducialClass(
        is_diagnostic=by_config or by_events,
        by_config=by_config,
        by_events=by_events,
        inconsistent=by_config != by_events,
    )


def classification_reason_codes(
    classification: TransferFiducialClass,
) -> tuple[str, ...]:
    """Return canonical claim refusals for one structural class."""

    if not classification.is_diagnostic:
        return ()
    reasons = [TRANSFER_FIDUCIAL_CLAIM_REFUSAL]
    if classification.inconsistent:
        reasons.append(TRANSFER_FIDUCIAL_CLASS_INCONSISTENT)
    return tuple(reasons)


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _finite_nonnegative(value: Any) -> float | None:
    if (
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(float(value))
        or float(value) < 0.0
    ):
        return None
    return float(value)


def _event_rows_by_key(
    events: Sequence[Mapping[str, Any]], event_type: str, phase: str
) -> list[Mapping[str, Any]]:
    return [
        row
        for row in events
        if row.get("event_type") == event_type and row.get("phase") == phase
    ]


def _authenticated_event_stamp(
    row: Mapping[str, Any], label: str
) -> tuple[Any | None, str | None]:
    metadata = row.get("metadata")
    stamp_row = metadata.get("clock_stamp") if isinstance(metadata, Mapping) else None
    if not isinstance(stamp_row, Mapping):
        return None, f"{label}_clock_stamp_missing"
    try:
        stamp = stamp_from_mapping(stamp_row)
    except (KeyError, OverflowError, TypeError, ValueError):
        return None, f"{label}_clock_stamp_malformed"
    if not valid_clock_stamp(stamp):
        return None, f"{label}_clock_stamp_malformed"
    timestamp_s = row.get("timestamp_s")
    if (
        isinstance(timestamp_s, bool)
        or not isinstance(timestamp_s, int | float)
        or not math.isfinite(float(timestamp_s))
        or float(timestamp_s) != stamp.epoch_s
    ):
        return None, f"{label}_event_stamp_disagrees"
    return stamp, None


def _inconclusive_fit(
    bundle_id: str,
    classification: TransferFiducialClass,
    reasons: Sequence[str],
    **fields: Any,
) -> TransferFiducialRunFit:
    return TransferFiducialRunFit(
        bundle_id=bundle_id,
        verdict=_INCONCLUSIVE,
        reasons=tuple(sorted(dict.fromkeys(reasons))),
        classification=classification,
        **fields,
    )


def _crop_intervals(
    intervals: Sequence[TraceInterval], prefill_start_s: float
) -> list[TraceInterval]:
    threshold = prefill_start_s - FIT_HALF_RANGE_S
    eligible = [
        index
        for index, interval in enumerate(intervals)
        if interval.start_s <= threshold
    ]
    if not eligible:
        return []
    return list(intervals[max(eligible) :])


def _target_edge(
    *,
    name: str,
    fit: Any,
    edge: str,
    run_bound_s: float,
) -> dict[str, Any] | None:
    if edge == "offset":
        delta = fit.delta_off_s
        lower = fit.offset_residual_lower_s
        upper = fit.offset_residual_upper_s
    else:
        delta = fit.delta_on_s
        lower = fit.onset_residual_lower_s
        upper = fit.onset_residual_upper_s
    if any(
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(float(value))
        for value in (delta, lower, upper)
    ):
        return None
    radius = max(abs(float(lower)), abs(float(upper))) + run_bound_s
    return {
        "edge": name,
        "pulse_index": fit.pulse_index,
        "fit_delta_s": float(delta),
        "residual_lower_s": float(lower),
        "residual_upper_s": float(upper),
        "effective_clock_anchor_bound_s": run_bound_s,
        "radius_s": radius,
    }


def fit_run(bundle_path: Path) -> TransferFiducialRunFit:
    """Fit the two active windows surrounding one inserted diagnostic gap.

    The raw powermetrics plist is re-anchored from the bundle's stored clock
    evidence.  Exactly two :class:`CommandedPulse` objects are passed to the
    governed :func:`powermetrics_fiducial.detect_pulses` implementation.
    """

    # Local imports avoid a cycle: BundleReader itself exposes this module's
    # classifier, while the powermetrics adapter imports the schema module.
    from joulewise.adapters.powermetrics import parse_powermetrics_records
    from joulewise.bundle_read import BundleReadError, BundleReader

    path = Path(bundle_path)
    bundle_id = path.name
    reader = BundleReader(path)
    raw_config = reader.raw_config()
    try:
        events = reader.events()
    except BundleReadError as exc:
        classification = classify_bundle(raw_config, ())
        return _inconclusive_fit(
            bundle_id,
            classification,
            [f"events_unreadable:{exc}"],
        )
    classification = classify_bundle(raw_config, events)
    reasons = list(classification_reason_codes(classification)[1:])
    if not classification.is_diagnostic:
        reasons.append("transfer_fiducial_class_absent")
    if not isinstance(raw_config, Mapping):
        return _inconclusive_fit(
            bundle_id, classification, [*reasons, "config_unreadable"]
        )

    config_path = path / "config.json"
    config_sha256 = _sha256_file(config_path) if config_path.is_file() else None
    workload = raw_config.get("workload_profile")
    commanded_gap = (
        workload.get("transfer_fiducial_gap_s")
        if isinstance(workload, Mapping)
        else None
    )
    if commanded_gap != TRANSFER_FIDUCIAL_GAP_S_V1:
        reasons.append("commanded_gap_invalid")

    event_specs = (
        ("prefill_start", "phase_start", "prefill"),
        ("gap_start", "fiducial_gap_start", "fiducial_gap"),
        ("prefill_end", "phase_end", "prefill"),
        ("gap_end", "fiducial_gap_end", "fiducial_gap"),
        ("decode_start", "phase_start", "decode"),
        ("decode_end", "phase_end", "decode"),
    )
    selected: dict[str, Mapping[str, Any]] = {}
    stamps: dict[str, Any] = {}
    for label, event_type, phase in event_specs:
        matches = _event_rows_by_key(events, event_type, phase)
        if len(matches) != 1:
            reasons.append(f"{label}_event_count_invalid")
            continue
        selected[label] = matches[0]
        stamp, problem = _authenticated_event_stamp(matches[0], label)
        if problem is not None:
            reasons.append(problem)
        else:
            stamps[label] = stamp

    gap_events = tuple(
        selected[label]
        for label in ("gap_start", "gap_end")
        if label in selected
    )
    boundary_events = tuple(
        selected[label]
        for label in ("prefill_start", "prefill_end", "decode_start", "decode_end")
        if label in selected
    )
    for label in ("gap_start", "gap_end"):
        row = selected.get(label)
        metadata = row.get("metadata") if isinstance(row, Mapping) else None
        if not isinstance(metadata, Mapping):
            continue
        if metadata.get("boundary_semantics") != TRANSFER_FIDUCIAL_BOUNDARY_SEMANTICS:
            reasons.append(f"{label}_boundary_semantics_missing")
        if metadata.get("diagnostic_kind") != TRANSFER_FIDUCIAL_DIAGNOSTIC_KIND:
            reasons.append(f"{label}_diagnostic_kind_invalid")

    if all(label in stamps for label in ("gap_start", "prefill_end")) and (
        stamps["gap_start"].epoch_s != stamps["prefill_end"].epoch_s
    ):
        reasons.append("prefill_end_gap_start_not_shared")
    if all(label in stamps for label in ("gap_end", "decode_start")) and (
        stamps["gap_end"].epoch_s != stamps["decode_start"].epoch_s
    ):
        reasons.append("gap_end_decode_start_not_shared")

    required_stamps = {
        "prefill_start",
        "gap_start",
        "prefill_end",
        "gap_end",
        "decode_start",
        "decode_end",
    }
    if set(stamps) != required_stamps:
        return _inconclusive_fit(
            bundle_id,
            classification,
            reasons,
            config_sha256=config_sha256,
            source_commit=None,
            model=raw_config.get("model"),
            quantization=raw_config.get("quantization"),
            hardware_target=raw_config.get("hardware_target"),
            workload_profile=workload,
            boundary_events=boundary_events,
            gap_events=gap_events,
            commanded_gap_s=(float(commanded_gap) if commanded_gap == 0.5 else None),
        )

    prefill_start = stamps["prefill_start"]
    gap_start = stamps["gap_start"]
    gap_end = stamps["gap_end"]
    decode_end = stamps["decode_end"]
    observed_gap_s = gap_end.epoch_s - gap_start.epoch_s
    if (
        not math.isfinite(observed_gap_s)
        or observed_gap_s < TRANSFER_FIDUCIAL_GAP_S_V1
    ):
        reasons.append("observed_gap_duration_invalid")

    pulses = (
        CommandedPulse(
            on_s=prefill_start.epoch_s,
            off_s=gap_start.epoch_s,
            on_uncertainty_s=clock_stamp_half_width_s(prefill_start),
            off_uncertainty_s=clock_stamp_half_width_s(gap_start),
        ),
        CommandedPulse(
            on_s=gap_end.epoch_s,
            off_s=decode_end.epoch_s,
            on_uncertainty_s=clock_stamp_half_width_s(gap_end),
            off_uncertainty_s=clock_stamp_half_width_s(decode_end),
        ),
    )
    durations = (pulses[0].off_s - pulses[0].on_s, pulses[1].off_s - pulses[1].on_s)
    if any(
        not math.isfinite(duration)
        or duration < MIN_AUTHENTICATED_PULSE_DURATION_S
        for duration in durations
    ):
        reasons.append("active_window_duration_below_0p8_s")

    metadata = reader.raw_metadata()
    uncertainty = (
        metadata.get("uncertainty_evidence")
        if isinstance(metadata, Mapping)
        else None
    )
    anchor = (
        uncertainty.get("clock_anchor")
        if isinstance(uncertainty, Mapping)
        else None
    )
    anchor_method = anchor.get("method") if isinstance(anchor, Mapping) else None
    first_endpoint = (
        _finite_nonnegative(anchor.get("first_sample_end_point_epoch_s"))
        if isinstance(anchor, Mapping)
        else None
    )
    run_bound = (
        _finite_nonnegative(anchor.get("effective_clock_anchor_bound_s"))
        if isinstance(anchor, Mapping)
        else None
    )
    if (
        not isinstance(anchor, Mapping)
        or anchor.get("status") != "bounded"
        or anchor_method not in ANCHOR_METHOD_VERSIONS
        or first_endpoint is None
        or run_bound is None
    ):
        reasons.append("clock_anchor_invalid")

    raw_powermetrics = None
    try:
        raw_powermetrics = reader.raw_artifact_bytes("powermetrics.plist")
    except BundleReadError:
        pass
    if raw_powermetrics is None:
        reasons.append("raw_powermetrics_missing")

    constructed_pulses = tuple(asdict(pulse) for pulse in pulses)
    common_fields = {
        "config_sha256": config_sha256,
        "source_commit": (
            metadata.get("git_commit") if isinstance(metadata, Mapping) else None
        ),
        "model": raw_config.get("model"),
        "quantization": raw_config.get("quantization"),
        "hardware_target": raw_config.get("hardware_target"),
        "workload_profile": workload,
        "device_identity": (
            {
                "hardware_model": metadata.get("device", {}).get("hw_model"),
                "os_build": metadata.get("device", {}).get("kern_osversion"),
                "hardware_target_id": raw_config.get("hardware_target", {}).get("id"),
            }
            if isinstance(metadata, Mapping)
            and isinstance(metadata.get("device"), Mapping)
            and isinstance(raw_config.get("hardware_target"), Mapping)
            else None
        ),
        "instrument_calibration": (
            metadata.get("instrument_calibration")
            if isinstance(metadata, Mapping)
            and isinstance(metadata.get("instrument_calibration"), Mapping)
            else None
        ),
        "boundary_events": boundary_events,
        "gap_events": gap_events,
        "commanded_gap_s": (
            float(commanded_gap)
            if isinstance(commanded_gap, int | float)
            and not isinstance(commanded_gap, bool)
            else None
        ),
        "observed_gap_s": observed_gap_s,
        "active_window_durations_s": durations,
        "trace_anchor_method": (
            str(anchor_method) if isinstance(anchor_method, str) else None
        ),
        "effective_clock_anchor_bound_s": run_bound,
        "requested_post_window_sampling_dwell_s": (
            _finite_nonnegative(
                metadata.get("trace_window_margins", {}).get(
                    "requested_post_window_dwell_s"
                )
            )
            if isinstance(metadata, Mapping)
            and isinstance(metadata.get("trace_window_margins"), Mapping)
            else None
        ),
        "constructed_pulses": constructed_pulses,
    }
    if reasons or raw_powermetrics is None or first_endpoint is None or run_bound is None:
        return _inconclusive_fit(
            bundle_id, classification, reasons, **common_fields
        )

    try:
        records = parse_powermetrics_records(
            raw_powermetrics,
            first_record_endpoint_s=first_endpoint,
        )
        intervals = [
            TraceInterval(
                start_s=record.timestamp_s
                - record.elapsed_ns / 1_000_000_000.0,
                end_s=record.timestamp_s,
                power_w=record.rail_power_w[PRIMARY_RAIL],
            )
            for record in records
        ]
    except (KeyError, OverflowError, TypeError, ValueError) as exc:
        return _inconclusive_fit(
            bundle_id,
            classification,
            [f"raw_powermetrics_invalid:{exc}"],
            **common_fields,
        )
    cropped = _crop_intervals(intervals, prefill_start.epoch_s)
    if not cropped:
        return _inconclusive_fit(
            bundle_id,
            classification,
            ["prefill_edge_coverage_missing"],
            **common_fields,
        )
    baseline_start_s = decode_end.epoch_s + powermetrics_fiducial.LOCAL_MARGIN_S
    outside_baseline_s = max(
        0.0, max(interval.end_s for interval in cropped) - baseline_start_s
    )
    common_fields["outside_baseline_after_margins_s"] = outside_baseline_s
    if outside_baseline_s < MIN_AUTHENTICATED_BASELINE_S:
        return _inconclusive_fit(
            bundle_id,
            classification,
            ["outside_baseline_after_margins_too_short"],
            **common_fields,
        )

    try:
        detection = powermetrics_fiducial.detect_pulses(
            cropped,
            pulses,
            trace_anchor_bound_s=run_bound,
        )
    except (OverflowError, TypeError, ValueError) as exc:
        return _inconclusive_fit(
            bundle_id,
            classification,
            [f"pulse_detection_failed:{exc}"],
            **common_fields,
        )
    pulse_fits = tuple(asdict(fit) for fit in detection.fits)
    detector_record = {
        "baseline_w": detection.baseline_w,
        "robust_sigma_w": detection.robust_sigma_w,
        "all_pulses_detected": detection.all_pulses_detected,
        "spurious_plateau_count": detection.spurious_plateau_count,
        "reasons": list(detection.reasons),
        "projection_evaluated_cell_count": detection.projection_evaluated_cell_count,
        "projection_evaluated_cell_budget": detection.projection_evaluated_cell_budget,
        "projection_wall_budget_s": detection.projection_wall_budget_s,
        "projection_disposition": detection.projection_disposition,
    }
    common_fields["pulse_fits"] = pulse_fits
    common_fields["detector"] = detector_record
    fit_reasons: list[str] = list(detection.reasons)
    if len(detection.fits) != 2 or not detection.all_pulses_detected:
        fit_reasons.append("not_all_pulses_detected")
    if detection.spurious_plateau_count != 0:
        fit_reasons.append("spurious_plateau_detected")
    residual_fields = (
        "onset_residual_lower_s",
        "onset_residual_upper_s",
        "offset_residual_lower_s",
        "offset_residual_upper_s",
    )
    if any(
        isinstance(getattr(fit, field_name), bool)
        or not isinstance(getattr(fit, field_name), int | float)
        or not math.isfinite(float(getattr(fit, field_name)))
        for fit in detection.fits
        for field_name in residual_fields
    ):
        fit_reasons.append("residual_interval_unbounded")

    targets: list[dict[str, Any]] = []
    if len(detection.fits) == 2:
        falling = _target_edge(
            name="falling_gap_edge",
            fit=detection.fits[0],
            edge="offset",
            run_bound_s=run_bound,
        )
        rising = _target_edge(
            name="rising_gap_edge",
            fit=detection.fits[1],
            edge="onset",
            run_bound_s=run_bound,
        )
        if falling is None or rising is None:
            fit_reasons.append("target_edge_residual_unbounded")
        else:
            targets.extend((falling, rising))
    common_fields["target_edges"] = tuple(targets)
    if fit_reasons:
        return _inconclusive_fit(
            bundle_id,
            classification,
            fit_reasons,
            **common_fields,
        )
    return TransferFiducialRunFit(
        bundle_id=bundle_id,
        verdict=_FIT_SUCCESS,
        reasons=(),
        classification=classification,
        **common_fields,
    )


def _load_json_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TransferFiducialError(f"{label} is unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise TransferFiducialError(f"{label} must be a JSON object")
    return value, raw


def _validate_plan(plan: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    if plan.get("schema_version") != TRANSFER_FIDUCIAL_PLAN_SCHEMA:
        raise TransferFiducialError("transfer plan schema_version is invalid")
    if plan.get("diagnostic") is not True or plan.get("claim_bearing") is not False:
        raise TransferFiducialError("transfer plan must be diagnostic and non-claim-bearing")
    if plan.get("diagnostic_kind") != TRANSFER_FIDUCIAL_DIAGNOSTIC_KIND:
        raise TransferFiducialError("transfer plan diagnostic_kind is invalid")
    if plan.get("pooling") != "forbidden":
        raise TransferFiducialError("transfer plan must forbid pooling across strata")
    strata = plan.get("strata")
    if not isinstance(strata, list) or not strata:
        raise TransferFiducialError("transfer plan requires at least one stratum")
    ids: set[str] = set()
    for stratum in strata:
        if not isinstance(stratum, Mapping):
            raise TransferFiducialError("transfer plan stratum must be an object")
        stratum_id = stratum.get("stratum_id")
        if not isinstance(stratum_id, str) or not stratum_id or stratum_id in ids:
            raise TransferFiducialError("transfer plan stratum_id is invalid or duplicated")
        ids.add(stratum_id)
        configs = stratum.get("configs")
        if (
            not isinstance(configs, list)
            or len(configs) != 10
            or stratum.get("planned_runs") != 10
        ):
            raise TransferFiducialError("each transfer stratum requires exactly 10 planned runs")
    return strata


def _plan_rule_reasons(
    plan: Mapping[str, Any], strata: Sequence[Mapping[str, Any]]
) -> list[str]:
    """Name every plan rule that differs from the rule the fitter executes."""

    expected = transfer_fiducial_rule_constants()
    reasons: list[str] = []
    if plan.get("pre_data_receipt_required") is True and plan.get(
        "fit_rule_constants"
    ) != expected:
        reasons.append("plan_fit_rule_constants_do_not_match_fitter")
    for stratum in strata:
        stratum_id = stratum.get("stratum_id", "unknown")
        for field_name in (
            "minimum_prefill_s",
            "minimum_decode_s",
            "post_window_sampling_dwell_s",
        ):
            expected_value = expected[field_name]
            value = stratum.get(field_name)
            if (
                isinstance(value, bool)
                or not isinstance(value, int | float)
                or not math.isfinite(float(value))
                or float(value) != float(expected_value)
            ):
                reasons.append(
                    f"{stratum_id}:plan_{field_name}_does_not_match_fitter"
                )
    return reasons


def _git_head() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[1],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value if len(value) == 40 else None


def _nearest_rank_p95(values: Sequence[float]) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def summarize_target_edge_radii(values: Sequence[float]) -> dict[str, Any]:
    """Return the normative max and diagnostic-only distribution summaries."""

    radii = [float(value) for value in values]
    if not radii or any(not math.isfinite(value) or value < 0.0 for value in radii):
        raise TransferFiducialError("target-edge radii must be finite and nonnegative")
    return {
        "residual_transfer_s": max(radii),
        "residual_median_s_diagnostic_only": statistics.median(radii),
        "residual_p95_s_diagnostic_only": _nearest_rank_p95(radii),
        "target_edge_sample_count": len(radii),
    }


def _calibration_record(
    calibration_dir: Path,
) -> tuple[dict[str, Any], list[str]]:
    evidence_path = calibration_dir / "instrument_evidence.json"
    evidence, raw = _load_json_object(evidence_path, "pulse calibration evidence")
    reasons: list[str] = []
    bindings = evidence.get("bindings")
    protocol_id = evidence.get("protocol_id")
    b_pulse_s = _finite_nonnegative(evidence.get("b_fiducial_s"))
    if evidence.get("status") != "valid" or evidence.get("reasons") not in ([], ()): 
        reasons.append("pulse_calibration_invalid")
    if not isinstance(bindings, Mapping):
        bindings = {}
        reasons.append("pulse_calibration_bindings_missing")
    if protocol_id != bindings.get("pulse_protocol_id"):
        reasons.append("pulse_calibration_protocol_mismatch")
    if (
        evidence.get("residual_region_method")
        != powermetrics_fiducial.RESIDUAL_REGION_METHOD
        or bindings.get("estimator_revision")
        != powermetrics_fiducial.RESIDUAL_REGION_METHOD
    ):
        reasons.append("pulse_calibration_estimator_revision_mismatch")
    for field_name in ("power_policy", "hardware_model", "os_build"):
        if not isinstance(bindings.get(field_name), str) or not bindings[field_name]:
            reasons.append(f"pulse_calibration_{field_name}_missing")
    if b_pulse_s is None:
        reasons.append("pulse_calibration_bound_invalid")
    return (
        {
            "directory": str(calibration_dir.resolve()),
            "artifact_path": str(evidence_path.resolve()),
            "instrument_evidence_sha256": _sha256_bytes(raw),
            "validation_id": evidence.get("validation_id"),
            "capture_wall_time_s": evidence.get("capture_wall_time_s"),
            "protocol_id": protocol_id,
            "estimator_revision": evidence.get("residual_region_method"),
            "bindings": dict(bindings),
            "b_pulse_s": b_pulse_s,
        },
        reasons,
    )


def _calibration_identity(calibration: Mapping[str, Any]) -> dict[str, Any]:
    """The calibration directory identity that must survive to the fit."""

    return {
        "directory": calibration.get("directory"),
        "instrument_evidence_sha256": calibration.get("instrument_evidence_sha256"),
        "validation_id": calibration.get("validation_id"),
        "capture_wall_time_s": calibration.get("capture_wall_time_s"),
    }


def _config_hashes_from_plan(
    strata: Sequence[Mapping[str, Any]],
) -> dict[str, str] | None:
    hashes: dict[str, str] = {}
    for stratum in strata:
        descriptors = stratum.get("configs")
        if not isinstance(descriptors, list):
            return None
        for descriptor in descriptors:
            if not isinstance(descriptor, Mapping):
                return None
            bundle_id = descriptor.get("bundle_id")
            config_sha256 = descriptor.get("config_sha256")
            if (
                not isinstance(bundle_id, str)
                or not bundle_id
                or bundle_id in hashes
                or not isinstance(config_sha256, str)
                or len(config_sha256) != 64
            ):
                return None
            hashes[bundle_id] = config_sha256
    return hashes if len(hashes) == 10 else None


def _config_source_hashes(
    strata: Sequence[Mapping[str, Any]],
) -> dict[str, str] | None:
    """Rehash the ten source configurations named by the plan descriptors."""

    from joulewise.schemas import BenchmarkConfig

    hashes: dict[str, str] = {}
    for stratum in strata:
        descriptors = stratum.get("configs")
        if not isinstance(descriptors, list):
            return None
        for descriptor in descriptors:
            if not isinstance(descriptor, Mapping):
                return None
            bundle_id = descriptor.get("bundle_id")
            config_source = descriptor.get("config_path")
            if (
                not isinstance(bundle_id, str)
                or not bundle_id
                or bundle_id in hashes
                or not isinstance(config_source, str)
                or not config_source
            ):
                return None
            source_path = Path(config_source)
            if not source_path.is_absolute():
                source_path = Path(__file__).resolve().parents[1] / source_path
            try:
                source_mapping, _ = _load_json_object(
                    source_path, f"{bundle_id} planned config"
                )
                normalized = (
                    json.dumps(
                        BenchmarkConfig.from_mapping(source_mapping).to_dict(),
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n"
                ).encode("utf-8")
            except (TransferFiducialError, ValueError):
                return None
            hashes[bundle_id] = _sha256_bytes(normalized)
    return hashes if len(hashes) == 10 else None


def _fitter_source_sha256() -> str:
    return _sha256_file(Path(__file__).resolve().parents[1] / _FITTER_SOURCE_REL)


def issue_pre_data_receipt(
    *, plan_path: Path, pulse_calibration_dir: Path
) -> dict[str, Any]:
    """Freeze the declared plan, fitter, estimator, calibration, and rules.

    This function is intentionally callable only before the diagnostic bundles
    are collected.  It reads no run directory, so it cannot select a rule after
    looking at a result.
    """

    plan, plan_raw = _load_json_object(Path(plan_path), "transfer plan")
    strata = _validate_plan(plan)
    plan_reasons = _plan_rule_reasons(plan, strata)
    config_hashes = _config_hashes_from_plan(strata)
    source_config_hashes = _config_source_hashes(strata)
    calibration, calibration_reasons = _calibration_record(
        Path(pulse_calibration_dir)
    )
    estimator_path = Path(powermetrics_fiducial.__file__).resolve()
    estimator_sha256 = _sha256_file(estimator_path)
    reasons = [*plan_reasons, *calibration_reasons]
    if config_hashes is None:
        reasons.append("pre_data_receipt_plan_config_hashes_invalid")
    elif source_config_hashes != config_hashes:
        reasons.append("pre_data_receipt_config_source_sha256_mismatch")
    if estimator_sha256 != TRANSFER_FIDUCIAL_ESTIMATOR_SHA256:
        reasons.append("transfer_estimator_source_digest_mismatch")
    if reasons:
        raise TransferFiducialError(
            "pre_data_receipt_refused:" + ",".join(sorted(dict.fromkeys(reasons)))
        )
    return {
        "schema_version": TRANSFER_FIDUCIAL_PRE_DATA_RECEIPT_SCHEMA,
        "plan_sha256": _sha256_bytes(plan_raw),
        "config_sha256": config_hashes,
        "fitter_source": {
            "path": _FITTER_SOURCE_REL.as_posix(),
            "sha256": _fitter_source_sha256(),
        },
        "estimator_source": {
            "path": "joulewise/powermetrics_fiducial.py",
            "sha256": estimator_sha256,
            "pinned_sha256": TRANSFER_FIDUCIAL_ESTIMATOR_SHA256,
        },
        "calibration_directory": _calibration_identity(calibration),
        "fit_rule_constants": transfer_fiducial_rule_constants(),
    }


def _receipt_record(
    receipt_path: Path | None,
    *,
    plan_raw: bytes,
    strata: Sequence[Mapping[str, Any]],
    calibration: Mapping[str, Any],
    estimator_sha256: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Compare a pre-data receipt with the inputs visible when fitting."""

    if receipt_path is None:
        return None, ["pre_data_receipt_missing"]
    try:
        receipt, receipt_raw = _load_json_object(receipt_path, "pre-data receipt")
    except TransferFiducialError:
        return None, ["pre_data_receipt_unreadable"]
    expected_keys = {
        "schema_version",
        "plan_sha256",
        "config_sha256",
        "fitter_source",
        "estimator_source",
        "calibration_directory",
        "fit_rule_constants",
    }
    reasons: list[str] = []
    if set(receipt) != expected_keys or receipt.get("schema_version") != (
        TRANSFER_FIDUCIAL_PRE_DATA_RECEIPT_SCHEMA
    ):
        reasons.append("pre_data_receipt_schema_mismatch")
    if receipt.get("plan_sha256") != _sha256_bytes(plan_raw):
        reasons.append("pre_data_receipt_plan_sha256_mismatch")
    if receipt.get("config_sha256") != _config_hashes_from_plan(strata):
        reasons.append("pre_data_receipt_config_sha256_mismatch")
    elif _config_source_hashes(strata) != _config_hashes_from_plan(strata):
        reasons.append("pre_data_receipt_config_source_sha256_mismatch")
    if receipt.get("fitter_source") != {
        "path": _FITTER_SOURCE_REL.as_posix(),
        "sha256": _fitter_source_sha256(),
    }:
        reasons.append("pre_data_receipt_fitter_source_sha256_mismatch")
    if receipt.get("estimator_source") != {
        "path": "joulewise/powermetrics_fiducial.py",
        "sha256": estimator_sha256,
        "pinned_sha256": TRANSFER_FIDUCIAL_ESTIMATOR_SHA256,
    }:
        reasons.append("pre_data_receipt_estimator_source_sha256_mismatch")
    if receipt.get("calibration_directory") != _calibration_identity(calibration):
        reasons.append("pre_data_receipt_calibration_identity_mismatch")
    if receipt.get("fit_rule_constants") != transfer_fiducial_rule_constants():
        reasons.append("pre_data_receipt_fit_rule_constants_mismatch")
    return (
        {
            "path": str(Path(receipt_path).resolve()),
            "sha256": _sha256_bytes(receipt_raw),
        },
        reasons,
    )


def _calibration_precedes_all_runs(
    calibration: Mapping[str, Any], fits: Sequence[TransferFiducialRunFit]
) -> list[str]:
    """Require calibration capture to predate the prefill start of every run."""

    capture_time = _finite_nonnegative(calibration.get("capture_wall_time_s"))
    if capture_time is None:
        return ["pre_data_receipt_calibration_capture_time_invalid"]
    reasons: list[str] = []
    for fit in fits:
        prefill_starts = [
            _finite_nonnegative(row.get("timestamp_s"))
            for row in fit.boundary_events
            if row.get("event_type") == "phase_start" and row.get("phase") == "prefill"
        ]
        if len(prefill_starts) != 1 or prefill_starts[0] is None:
            reasons.append(f"{fit.bundle_id}:pre_data_receipt_run_start_missing")
        elif capture_time >= prefill_starts[0]:
            reasons.append(f"{fit.bundle_id}:pre_data_receipt_calibration_not_earlier")
    return reasons


def _mapping_contains(expected: Mapping[str, Any], observed: Any) -> bool:
    return isinstance(observed, Mapping) and all(
        key in observed and observed[key] == value for key, value in expected.items()
    )


def _run_binding_reasons(
    fit: TransferFiducialRunFit,
    descriptor: Mapping[str, Any],
    stratum: Mapping[str, Any],
    calibration: Mapping[str, Any],
) -> list[str]:
    reasons: list[str] = []
    if fit.config_sha256 != descriptor.get("config_sha256"):
        reasons.append(f"{fit.bundle_id}:config_sha256_mismatch")
    for field_name in ("model", "quantization", "hardware_target"):
        expected = stratum.get(field_name)
        observed = getattr(fit, field_name)
        if not isinstance(expected, Mapping) or not _mapping_contains(expected, observed):
            reasons.append(f"{fit.bundle_id}:{field_name}_mismatch")
    workload = fit.workload_profile
    for field_name in (
        "output_tokens",
        "repetitions",
        "transfer_fiducial_gap_s",
    ):
        if (
            not isinstance(workload, Mapping)
            or workload.get(field_name) != stratum.get(field_name)
        ):
            reasons.append(f"{fit.bundle_id}:workload_{field_name}_mismatch")
    expected_prompt_tokens = stratum.get("prompt_tokens")
    prompt_text = workload.get("prompt_text") if isinstance(workload, Mapping) else None
    if isinstance(prompt_text, str):
        if (
            not isinstance(stratum.get("prompt_text_utf8_sha256"), str)
            or _sha256_bytes(prompt_text.encode("utf-8"))
            != stratum.get("prompt_text_utf8_sha256")
        ):
            reasons.append(f"{fit.bundle_id}:workload_prompt_text_hash_mismatch")
    elif (
        not isinstance(workload, Mapping)
        or workload.get("prompt_tokens") != expected_prompt_tokens
    ):
        reasons.append(f"{fit.bundle_id}:workload_prompt_tokens_mismatch")
    if fit.requested_post_window_sampling_dwell_s != stratum.get(
        "post_window_sampling_dwell_s"
    ):
        reasons.append(f"{fit.bundle_id}:post_window_sampling_dwell_mismatch")
    attachment = fit.instrument_calibration
    calibration_bindings = calibration.get("bindings")
    if not isinstance(attachment, Mapping):
        reasons.append(f"{fit.bundle_id}:instrument_calibration_missing")
    else:
        if (
            attachment.get("artifact_sha256")
            != calibration.get("instrument_evidence_sha256")
        ):
            reasons.append(f"{fit.bundle_id}:pulse_calibration_sha256_mismatch")
        if attachment.get("bindings") != calibration_bindings:
            reasons.append(f"{fit.bundle_id}:pulse_calibration_bindings_mismatch")
        observations = attachment.get("binding_observations")
        if (
            not isinstance(observations, Mapping)
            or observations.get("power_policy")
            != calibration_bindings.get("power_policy")
        ):
            reasons.append(f"{fit.bundle_id}:power_policy_observation_mismatch")
    identity = fit.device_identity
    if not isinstance(identity, Mapping) or not isinstance(calibration_bindings, Mapping):
        reasons.append(f"{fit.bundle_id}:device_identity_missing")
    else:
        if identity.get("hardware_model") != calibration_bindings.get("hardware_model"):
            reasons.append(f"{fit.bundle_id}:hardware_model_mismatch")
        if identity.get("os_build") != calibration_bindings.get("os_build"):
            reasons.append(f"{fit.bundle_id}:os_build_mismatch")
    return reasons


def build_capture(
    *,
    plan_path: Path,
    runs_root: Path,
    pulse_calibration_dir: Path,
    pre_data_receipt_path: Path | None = None,
) -> dict[str, Any]:
    """Build one fail-closed, non-pooled transfer-fiducial capture record."""

    plan_path = Path(plan_path)
    runs_root = Path(runs_root)
    calibration_dir = Path(pulse_calibration_dir)
    plan, plan_raw = _load_json_object(plan_path, "transfer plan")
    strata = _validate_plan(plan)
    calibration, reasons = _calibration_record(calibration_dir)
    reasons.extend(_plan_rule_reasons(plan, strata))
    estimator_path = Path(powermetrics_fiducial.__file__).resolve()
    estimator_sha256 = _sha256_file(estimator_path)
    if estimator_sha256 != TRANSFER_FIDUCIAL_ESTIMATOR_SHA256:
        reasons.append("transfer_estimator_source_digest_mismatch")
    pre_data_receipt, receipt_reasons = _receipt_record(
        pre_data_receipt_path,
        plan_raw=plan_raw,
        strata=strata,
        calibration=calibration,
        estimator_sha256=estimator_sha256,
    )
    reasons.extend(receipt_reasons)

    stratum_records: list[dict[str, Any]] = []
    all_fits: list[TransferFiducialRunFit] = []
    for stratum in strata:
        fit_rows: list[TransferFiducialRunFit] = []
        stratum_reasons: list[str] = []
        descriptors = stratum["configs"]
        for descriptor in descriptors:
            if not isinstance(descriptor, Mapping):
                raise TransferFiducialError("transfer config descriptor must be an object")
            bundle_id = descriptor.get("bundle_id")
            if not isinstance(bundle_id, str) or not bundle_id:
                raise TransferFiducialError("transfer config descriptor bundle_id is invalid")
            config_source = descriptor.get("config_path")
            if not isinstance(config_source, str) or not config_source:
                raise TransferFiducialError("transfer config descriptor config_path is invalid")
            source_path = Path(config_source)
            if not source_path.is_absolute():
                source_path = Path(__file__).resolve().parents[1] / source_path
            try:
                from joulewise.schemas import BenchmarkConfig

                source_mapping, _ = _load_json_object(
                    source_path, f"{bundle_id} planned config"
                )
                normalized = (
                    json.dumps(
                        BenchmarkConfig.from_mapping(source_mapping).to_dict(),
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n"
                ).encode("utf-8")
            except (TransferFiducialError, ValueError):
                stratum_reasons.append(
                    f"{bundle_id}:planned_config_unreadable_or_invalid"
                )
                normalized = None
            if normalized is None or _sha256_bytes(normalized) != descriptor.get(
                "config_sha256"
            ):
                stratum_reasons.append(
                    f"{bundle_id}:planned_config_sha256_mismatch"
                )
            fit = fit_run(runs_root / bundle_id)
            fit_rows.append(fit)
            all_fits.append(fit)
            if fit.verdict != _FIT_SUCCESS:
                stratum_reasons.extend(
                    f"{bundle_id}:{reason}" for reason in fit.reasons
                )
            stratum_reasons.extend(
                _run_binding_reasons(fit, descriptor, stratum, calibration)
            )
        radii = [
            float(edge["radius_s"])
            for fit in fit_rows
            for edge in fit.target_edges
            if isinstance(edge.get("radius_s"), int | float)
            and not isinstance(edge.get("radius_s"), bool)
            and math.isfinite(float(edge["radius_s"]))
        ]
        expected_edges = 2 * int(stratum["planned_runs"])
        if len(radii) != expected_edges:
            stratum_reasons.append("target_edge_sample_count_incomplete")
        radius_summary = (
            summarize_target_edge_radii(radii)
            if len(radii) == expected_edges
            else {
                "residual_transfer_s": None,
                "residual_median_s_diagnostic_only": None,
                "residual_p95_s_diagnostic_only": None,
                "target_edge_sample_count": len(radii),
            }
        )
        residual_transfer_s = radius_summary["residual_transfer_s"]
        stratum_records.append(
            {
                "stratum_id": stratum["stratum_id"],
                "model_load_identity": {
                    "model": stratum.get("model"),
                    "quantization": stratum.get("quantization"),
                    "hardware_target": stratum.get("hardware_target"),
                    "prompt_tokens": stratum.get("prompt_tokens"),
                    "output_tokens": stratum.get("output_tokens"),
                    "commanded_gap_s": stratum.get("transfer_fiducial_gap_s"),
                },
                "planned_runs": stratum["planned_runs"],
                "observed_runs": len(fit_rows),
                "runs": [fit.to_dict() for fit in fit_rows],
                "target_edge_sample_count": radius_summary["target_edge_sample_count"],
                "residual_transfer_s": residual_transfer_s,
                "residual_median_s_diagnostic_only": radius_summary[
                    "residual_median_s_diagnostic_only"
                ],
                "residual_p95_s_diagnostic_only": radius_summary[
                    "residual_p95_s_diagnostic_only"
                ],
                "reasons": sorted(dict.fromkeys(stratum_reasons)),
            }
        )
        reasons.extend(stratum_reasons)

    commits = sorted(
        {
            fit.source_commit
            for fit in all_fits
            if isinstance(fit.source_commit, str) and fit.source_commit
        }
    )
    if len(commits) != 1:
        reasons.append("source_commit_inconsistent_or_missing")
    reasons.extend(_calibration_precedes_all_runs(calibration, all_fits))
    # The ruled v1 file contains one stratum.  The schema and record retain a
    # list so a later separately-verdictable stratum can be added without
    # pooling observations.
    residual_transfer_s = (
        stratum_records[0]["residual_transfer_s"]
        if len(stratum_records) == 1
        else None
    )
    if len(stratum_records) != 1:
        reasons.append("capture_top_level_verdict_requires_one_stratum")
    b_pulse_s = calibration.get("b_pulse_s")
    reasons = sorted(dict.fromkeys(reasons))
    if reasons or residual_transfer_s is None or b_pulse_s is None:
        verdict = "inconclusive"
        excess_s = 0.0
    elif residual_transfer_s <= b_pulse_s:
        verdict = "supported"
        excess_s = 0.0
    else:
        verdict = "exceeds_bound"
        excess_s = residual_transfer_s - b_pulse_s
    first_stratum = stratum_records[0] if len(stratum_records) == 1 else {}
    return {
        "schema_version": TRANSFER_FIDUCIAL_CAPTURE_SCHEMA,
        "diagnostic_protocol_id": TRANSFER_FIDUCIAL_DIAGNOSTIC_KIND,
        "diagnostic": True,
        "claim_bearing": False,
        "source_commit": commits[0] if len(commits) == 1 else None,
        "fit_source_commit": _git_head(),
        "plan": {
            "path": str(plan_path.resolve()),
            "sha256": _sha256_bytes(plan_raw),
            "pooling": "forbidden",
            "stratum_count": len(strata),
        },
        "pre_data_receipt": pre_data_receipt,
        "strata": stratum_records,
        "config_sha256": {
            fit.bundle_id: fit.config_sha256 for fit in all_fits
        },
        "bundle_ids": [fit.bundle_id for fit in all_fits],
        "pulse_calibration": calibration,
        "estimator_revision": powermetrics_fiducial.RESIDUAL_REGION_METHOD,
        "estimator_source": "joulewise/powermetrics_fiducial.py",
        "estimator_source_sha256": estimator_sha256,
        "b_pulse_s": b_pulse_s,
        "residual_transfer_s": residual_transfer_s,
        "residual_median_s_diagnostic_only": first_stratum.get(
            "residual_median_s_diagnostic_only"
        ),
        "residual_p95_s_diagnostic_only": first_stratum.get(
            "residual_p95_s_diagnostic_only"
        ),
        "target_edge_sample_count": first_stratum.get(
            "target_edge_sample_count", 0
        ),
        "excess_s": excess_s,
        "verdict": verdict,
        "reasons": reasons,
        "boundary_semantics": TRANSFER_FIDUCIAL_BOUNDARY_SEMANTICS,
        "pipeline_caveat": (
            "At the first mlx_lm stream yield one decode step is already queued. "
            "The start stamp precedes mx.synchronize(); queued-work drain and "
            "redispatch latency remain inside the measured residual and are never "
            "subtracted. This is an inserted first-yield transport fiducial, not "
            "a computation-exact natural phase boundary."
        ),
        "synchronization": "mlx.core.synchronize_after_gap_start_stamp",
    }


__all__ = [
    "TRANSFER_FIDUCIAL_BOUNDARY_SEMANTICS",
    "TRANSFER_FIDUCIAL_CAPTURE_SCHEMA",
    "TRANSFER_FIDUCIAL_CLAIM_REFUSAL",
    "TRANSFER_FIDUCIAL_CLASS_INCONSISTENT",
    "TRANSFER_FIDUCIAL_DIAGNOSTIC_KIND",
    "TRANSFER_FIDUCIAL_ESTIMATOR_SHA256",
    "TRANSFER_FIDUCIAL_GAP_S_V1",
    "TRANSFER_FIDUCIAL_PLAN_SCHEMA",
    "TRANSFER_FIDUCIAL_PRE_DATA_RECEIPT_SCHEMA",
    "TransferFiducialClass",
    "TransferFiducialError",
    "TransferFiducialRunFit",
    "build_capture",
    "classification_reason_codes",
    "classify_bundle",
    "fit_run",
    "issue_pre_data_receipt",
    "summarize_target_edge_radii",
    "transfer_fiducial_rule_constants",
]
