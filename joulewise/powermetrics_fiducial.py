"""Pulse-fiducial validation harness for the powermetrics clock anchor (D-078).

A calibration run drives k rectangular GPU pulses with commanded on/off
events captured as paired :class:`joulewise.clock.ClockStamp` records, then
fits the interval-average model

    y_i = b + A * |I_i INTERSECT [t_on + d_on, t_off + d_off]| / |I_i|

per pulse with a robust constrained loss. The instrument residual bound
``B_fiducial`` is the max over all per-pulse onset/offset residual intervals
of ``max(|r_lower|, |r_upper|)`` - a deterministic worst-case bound, never a
percentile. Detection NEVER timestamps the first above-threshold interval
endpoint (that bakes in up to one cadence of bias); MLX dispatch/fence
latency stays inside the bound and is never subtracted.

Pure functions here are exercised by synthetic CI tests; the live [QUIET-MAC]
capture is lead-owned and driven by ``scripts/validate_powermetrics_fiducial.py``.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from joulewise.uncertainty_evidence import (
    CLOCK_METHOD_V2,
    derive_powermetrics_anchor_v2,
    stamp_from_mapping,
)

LEGACY_PROTOCOL_ID = "powermetrics_pulse_fiducial_v1"
PROTOCOL_ID = "powermetrics_pulse_fiducial_v2"
SUPPORTED_PROTOCOL_IDS = frozenset({LEGACY_PROTOCOL_ID, PROTOCOL_ID})
PROTOCOL_V2_SHA256 = "82d8c3125ef25437a89916429578d60fe47cbba2beb5bf54eb39b55935cc3783"
# The 0.5.1/0.6.1 replay arms froze their binding expectation at the
# protocol_v2.json bytes current when they were minted; re-keying the live
# constant must never change frozen replay dispositions.
REPLAY_PROTOCOL_V2_SHA256 = (
    "7c7cebd0ee5c117cd4edc196eae37a037015474c972767ae9bf594e2e0e7e3da"
)
CAPTURE_TIME_FIELD = "capture_wall_time_s"
MAX_AGE_S = 86400
PULSE_COUNT = 40
WARMUP_PULSE_COUNT = 3
PULSE_DURATION_S = 1.0
PULSE_GAP_BASE_S = 1.5
BASELINE_S = 5.0
SAMPLING_INTERVAL_MS = 100
MATRIX_SIDE = 4096
MATRIX_DTYPE = "float16"
PRIMARY_RAIL = "gpu_power"
CORROBORATION_RAILS = ("cpu_power", "gpu_power")
MIN_PLATEAU_W = 10.0
MIN_ROBUST_SNR = 10.0
FIT_HALF_RANGE_S = 0.75
FIT_COARSE_STEP_S = 0.005
FIT_FINE_STEP_S = 0.0005
REGION_COVERAGE_RESOLUTION_S = 0.0001
MAX_VALIDATED_EDGE_SHIFT_S = 0.50
HUBER_DELTA = 1.345
PLATEAU_INSET_S = 0.25
LOCAL_MARGIN_S = 0.75
SPURIOUS_MIN_CONSECUTIVE = 2
# Binding fields (hash-referenced): any change invalidates the calibration.
LEGACY_BINDING_FIELDS = (
    "hardware_model",
    "os_build",
    "powermetrics_sha256",
    "sampling_interval_ms",
    "anchor_method_version",
    "mlx_version",
    "pulse_protocol_id",
    "power_policy",
)
V2_BINDING_FIELDS = LEGACY_BINDING_FIELDS + (
    "estimator_revision",
    "protocol_sha256",
)
BINDING_FIELDS = V2_BINDING_FIELDS

# Closed serializer vocabulary.  Prefix-coded diagnostics are represented by
# their registered prefix including the trailing colon.
FIDUCIAL_DIAGNOSTIC_CODES = frozenset(
    {
        "no_plateau_interior_intervals",
        "plateau_below_minimum",
        "robust_snr_below_minimum",
        "edge_coverage_missing",
        "model_fit_not_significant",
        "fitted_shift_exceeds_validation_limit",
        "pulse_detection_incomplete",
        "spurious_plateau_detected",
        "residual_interval_unbounded",
        "not_all_pulses_detected",
        "binding_fields_missing:",
        "pulse_count_below_protocol:",
        "raw_or_event_hash_missing_or_invalid",
        "capture_time_missing_or_invalid",
    }
)

RESIDUAL_REGION_METHOD = "joint_loss_sublevel_interval_branch_v2"


def diagnostic_reason_registered(reason: Any) -> bool:
    """Return whether one serialized diagnostic uses the closed vocabulary."""

    if not isinstance(reason, str) or not reason:
        return False
    return any(
        reason.startswith(code) if code.endswith(":") else reason == code
        for code in FIDUCIAL_DIAGNOSTIC_CODES
    )


def protocol_definition(protocol_id: str = PROTOCOL_ID) -> dict[str, Any]:
    """Canonical executable description for one immutable protocol identity."""

    if protocol_id == LEGACY_PROTOCOL_ID:
        return {
            "schema_version": "joulewise.pulse_fiducial_protocol.v1",
            "protocol_id": LEGACY_PROTOCOL_ID,
            "workload": {
                "kind": "mlx_matmul",
                "matrix_side": MATRIX_SIDE,
                "dtype": MATRIX_DTYPE,
                "preallocated": True,
                "gpu_fence": "mx.eval per matmul",
            },
            "warmup_pulses": WARMUP_PULSE_COUNT,
            "pulse_count": PULSE_COUNT,
            "pulse_duration_s": PULSE_DURATION_S,
            "pulse_gap_s": "1.5 + van_der_corput_base2(j)",
            "baseline_before_s": BASELINE_S,
            "baseline_after_s": BASELINE_S,
            "sampling_interval_ms": SAMPLING_INTERVAL_MS,
            "primary_rail": PRIMARY_RAIL,
            "corroboration": "cpu_power + gpu_power combined, corroboration only",
            "gates": {
                "plateau_min_w_over_baseline": MIN_PLATEAU_W,
                "robust_snr_min": MIN_ROBUST_SNR,
                "all_pulses_detected": True,
                "no_spurious_plateaus": True,
            },
            "b_fiducial": (
                "max over per-pulse onset/offset residual intervals of "
                "max(|r_lower|, |r_upper|); median/p95 are diagnostic only"
            ),
            "estimator_rules": [
                "fit the interval-average overlap model with a robust constrained loss",
                "never timestamp the first above-threshold interval endpoint",
                "MLX dispatch/fence latency stays inside the bound, never subtracted",
                "event-stamp uncertainty widens every residual interval",
            ],
        }
    if protocol_id != PROTOCOL_ID:
        raise ValueError(f"unsupported fiducial protocol: {protocol_id!r}")

    return {
        "schema_version": "joulewise.pulse_fiducial_protocol.v2",
        "protocol_id": PROTOCOL_ID,
        "estimator_revision": RESIDUAL_REGION_METHOD,
        "workload": {
            "kind": "mlx_matmul",
            "matrix_side": MATRIX_SIDE,
            "dtype": MATRIX_DTYPE,
            "preallocated": True,
            "gpu_fence": "mx.eval per matmul",
        },
        "warmup_pulses": WARMUP_PULSE_COUNT,
        "pulse_count": PULSE_COUNT,
        "pulse_duration_s": PULSE_DURATION_S,
        "pulse_gap_s": "1.5 + van_der_corput_base2(j)",
        "baseline_before_s": BASELINE_S,
        "baseline_after_s": BASELINE_S,
        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
        "capture_time_field": CAPTURE_TIME_FIELD,
        "max_age_s": MAX_AGE_S,
        "primary_rail": PRIMARY_RAIL,
        "corroboration": (
            "cpu_power + gpu_power combined, corroboration only"
        ),
        "gates": {
            "plateau_min_w_over_baseline": MIN_PLATEAU_W,
            "robust_snr_min": MIN_ROBUST_SNR,
            "all_pulses_detected": True,
            "no_spurious_plateaus": True,
            "edge_coverage_across_full_fit_range": True,
        },
        "b_fiducial": (
            "max over per-pulse onset/offset residual intervals of "
            "max(|r_lower|, |r_upper|), plus the calibration capture's own "
            "effective trace-anchor bound; median/p95 are diagnostic only"
        ),
        "estimator_rules": [
            "fit the interval-average overlap model with a robust constrained loss",
            "never timestamp the first above-threshold interval endpoint",
            "MLX dispatch/fence latency stays inside the bound, never subtracted",
            "event-stamp uncertainty widens every residual interval",
            (
                "the capture effective trace-anchor bound additively widens "
                "the final physical bound"
            ),
            (
                "analytic interval branch-and-bound covers the complete "
                "accepted two-dimensional loss region"
            ),
        ],
        "coverage_resolution_s": REGION_COVERAGE_RESOLUTION_S,
    }


def protocol_definition_matches(payload: Any) -> bool:
    """Fail-closed equality check between JSON protocol and executable pins."""

    if not isinstance(payload, dict):
        return False
    protocol_id = payload.get("protocol_id")
    try:
        return payload == protocol_definition(protocol_id)
    except ValueError:
        return False


def van_der_corput(index: int, base: int = 2) -> float:
    """The base-``base`` van der Corput low-discrepancy sequence value."""

    if index < 0:
        raise ValueError("van der Corput index must be >= 0")
    result = 0.0
    denominator = 1.0
    remaining = index
    while remaining > 0:
        remaining, digit = divmod(remaining, base)
        denominator *= base
        result += digit / denominator
    return result


def pulse_gap_s(pulse_index: int) -> float:
    """Deterministic low-discrepancy gap after pulse ``pulse_index``.

    ``1.5 + vdC_2(j)`` seconds avoids phase-locking the pulse edges to the
    ~10 Hz powermetrics cadence: consecutive gaps are never congruent modulo
    the 0.1 s sampling interval.
    """

    return PULSE_GAP_BASE_S + van_der_corput(pulse_index)


def pulse_schedule(
    count: int = PULSE_COUNT,
    *,
    start_s: float = 0.0,
    duration_s: float = PULSE_DURATION_S,
) -> list[tuple[float, float]]:
    """Commanded (on, off) offsets for ``count`` pulses starting at ``start_s``."""

    if count < 1:
        raise ValueError("pulse count must be >= 1")
    schedule: list[tuple[float, float]] = []
    cursor = start_s
    for index in range(1, count + 1):
        on_s = cursor
        off_s = on_s + duration_s
        schedule.append((on_s, off_s))
        cursor = off_s + pulse_gap_s(index)
    return schedule


@dataclass(frozen=True)
class TraceInterval:
    """One interval-average power observation on the primary rail."""

    start_s: float
    end_s: float
    power_w: float

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s


@dataclass(frozen=True)
class CommandedPulse:
    """One commanded pulse with event-stamp half-width uncertainties."""

    on_s: float
    off_s: float
    on_uncertainty_s: float = 0.0
    off_uncertainty_s: float = 0.0


@dataclass(frozen=True)
class PulseFit:
    pulse_index: int
    detected: bool
    reasons: tuple[str, ...]
    amplitude_w: float | None = None
    robust_snr: float | None = None
    delta_on_s: float | None = None
    delta_off_s: float | None = None
    onset_residual_lower_s: float | None = None
    onset_residual_upper_s: float | None = None
    offset_residual_lower_s: float | None = None
    offset_residual_upper_s: float | None = None


@dataclass(frozen=True)
class FiducialDetection:
    baseline_w: float
    robust_sigma_w: float
    fits: tuple[PulseFit, ...]
    spurious_plateau_count: int
    all_pulses_detected: bool
    b_fiducial_s: float | None
    residual_median_s: float | None
    residual_p95_s: float | None
    reasons: tuple[str, ...] = field(default_factory=tuple)


def _huber(value: float) -> float:
    magnitude = abs(value)
    if magnitude <= HUBER_DELTA:
        return 0.5 * magnitude * magnitude
    return HUBER_DELTA * (magnitude - 0.5 * HUBER_DELTA)


def _overlap_fraction(
    interval: TraceInterval, on_s: float, off_s: float
) -> float:
    if interval.duration_s <= 0.0:
        return 0.0
    overlap = min(interval.end_s, off_s) - max(interval.start_s, on_s)
    return max(0.0, overlap) / interval.duration_s


def _pulse_loss(
    local: Sequence[TraceInterval],
    baseline_w: float,
    amplitude_w: float,
    sigma_w: float,
    on_s: float,
    off_s: float,
) -> float:
    return math.fsum(
        _huber(
            (
                interval.power_w
                - baseline_w
                - amplitude_w * _overlap_fraction(interval, on_s, off_s)
            )
            / sigma_w
        )
        for interval in local
    )


def _pulse_loss_cell_lower_bound(
    local: Sequence[TraceInterval],
    baseline_w: float,
    amplitude_w: float,
    sigma_w: float,
    pulse: CommandedPulse,
    onset_lower_s: float,
    onset_upper_s: float,
    offset_lower_s: float,
    offset_upper_s: float,
) -> float:
    """Rigorous lower loss bound over one edge-shift rectangle.

    Overlap is monotone decreasing in onset and increasing in offset.  For
    each trace interval the two opposite rectangle corners therefore bound
    every possible model prediction.  Summing each observation's minimum
    Huber loss over that prediction interval is a (possibly loose) analytic
    lower bound on the joint loss throughout the rectangle.
    """

    total = 0.0
    for interval in local:
        overlap_lower = _overlap_fraction(
            interval,
            pulse.on_s + onset_upper_s,
            pulse.off_s + offset_lower_s,
        )
        overlap_upper = _overlap_fraction(
            interval,
            pulse.on_s + onset_lower_s,
            pulse.off_s + offset_upper_s,
        )
        observed = (interval.power_w - baseline_w) / sigma_w
        predicted_lower = amplitude_w * overlap_lower / sigma_w
        predicted_upper = amplitude_w * overlap_upper / sigma_w
        if predicted_lower <= observed <= predicted_upper:
            distance = 0.0
        else:
            distance = min(
                abs(observed - predicted_lower),
                abs(observed - predicted_upper),
            )
        total += _huber(distance)
    return total


def _accepted_region_projection(
    *,
    local: Sequence[TraceInterval],
    baseline_w: float,
    amplitude_w: float,
    sigma_w: float,
    pulse: CommandedPulse,
    loss_limit: float,
) -> tuple[float, float, float, float]:
    """Conservatively project the complete accepted 2-D loss region.

    This is an analytic interval branch-and-bound, not directional sampling.
    A rectangle is discarded only when its rigorous loss lower bound exceeds
    ``loss_limit``. Remaining rectangles are bisected until every dimension
    is at most :data:`REGION_COVERAGE_RESOLUTION_S`; their complete extents
    are retained. Thus every accepted point is enclosed, including points
    between the resolution cells, while the old axes/diagonals blind spots
    are impossible by construction.
    """

    stack = [
        (
            -FIT_HALF_RANGE_S,
            FIT_HALF_RANGE_S,
            -FIT_HALF_RANGE_S,
            FIT_HALF_RANGE_S,
        )
    ]
    retained: list[tuple[float, float, float, float]] = []
    while stack:
        onset_lower, onset_upper, offset_lower, offset_upper = stack.pop()
        lower_bound = _pulse_loss_cell_lower_bound(
            local,
            baseline_w,
            amplitude_w,
            sigma_w,
            pulse,
            onset_lower,
            onset_upper,
            offset_lower,
            offset_upper,
        )
        if lower_bound > loss_limit:
            continue
        onset_width = onset_upper - onset_lower
        offset_width = offset_upper - offset_lower
        if max(onset_width, offset_width) <= REGION_COVERAGE_RESOLUTION_S:
            retained.append(
                (onset_lower, onset_upper, offset_lower, offset_upper)
            )
            continue
        if onset_width >= offset_width:
            midpoint = (onset_lower + onset_upper) / 2.0
            stack.append((onset_lower, midpoint, offset_lower, offset_upper))
            stack.append((midpoint, onset_upper, offset_lower, offset_upper))
        else:
            midpoint = (offset_lower + offset_upper) / 2.0
            stack.append((onset_lower, onset_upper, offset_lower, midpoint))
            stack.append((onset_lower, onset_upper, midpoint, offset_upper))
    if not retained:
        raise ValueError("accepted loss region unexpectedly empty")
    return (
        min(cell[0] for cell in retained),
        max(cell[1] for cell in retained),
        min(cell[2] for cell in retained),
        max(cell[3] for cell in retained),
    )


def _grid(center_s: float, half_range_s: float, step_s: float) -> list[float]:
    count = int(math.ceil(half_range_s / step_s))
    return [center_s + step_s * offset for offset in range(-count, count + 1)]


def _baseline_stats(
    intervals: Sequence[TraceInterval],
    pulses: Sequence[CommandedPulse],
) -> tuple[float, float, list[TraceInterval]]:
    outside = [
        interval
        for interval in intervals
        if not any(
            min(interval.end_s, pulse.off_s + LOCAL_MARGIN_S)
            > max(interval.start_s, pulse.on_s - LOCAL_MARGIN_S)
            for pulse in pulses
        )
    ]
    if len(outside) < 3:
        raise ValueError(
            "pulse fiducial requires at least 3 baseline intervals outside "
            "every pulse margin"
        )
    powers = [interval.power_w for interval in outside]
    baseline_w = statistics.median(powers)
    mad = statistics.median([abs(power - baseline_w) for power in powers])
    sigma_w = max(1.4826 * mad, 1e-3)
    return baseline_w, sigma_w, outside


def _fit_pulse(
    pulse_index: int,
    pulse: CommandedPulse,
    intervals: Sequence[TraceInterval],
    baseline_w: float,
    sigma_w: float,
) -> PulseFit:
    local = [
        interval
        for interval in intervals
        if min(interval.end_s, pulse.off_s + LOCAL_MARGIN_S)
        > max(interval.start_s, pulse.on_s - LOCAL_MARGIN_S)
    ]
    interior = [
        interval
        for interval in local
        if interval.start_s >= pulse.on_s + PLATEAU_INSET_S
        and interval.end_s <= pulse.off_s - PLATEAU_INSET_S
    ]
    if not interior:
        return PulseFit(
            pulse_index=pulse_index,
            detected=False,
            reasons=("no_plateau_interior_intervals",),
        )
    amplitude_w = (
        statistics.median([interval.power_w for interval in interior]) - baseline_w
    )
    robust_snr = amplitude_w / sigma_w
    reasons: list[str] = []
    if amplitude_w < MIN_PLATEAU_W:
        reasons.append("plateau_below_minimum")
    if robust_snr < MIN_ROBUST_SNR:
        reasons.append("robust_snr_below_minimum")
    if reasons:
        return PulseFit(
            pulse_index=pulse_index,
            detected=False,
            reasons=tuple(reasons),
            amplitude_w=amplitude_w,
            robust_snr=robust_snr,
        )
    # Trace coverage across both commanded edges over the whole fit range;
    # a truncated capture cannot certify either edge (fail closed).
    trace_start_s = min(interval.start_s for interval in local)
    trace_end_s = max(interval.end_s for interval in local)
    if (
        trace_start_s > pulse.on_s - FIT_HALF_RANGE_S
        or trace_end_s < pulse.off_s + FIT_HALF_RANGE_S
    ):
        return PulseFit(
            pulse_index=pulse_index,
            detected=False,
            reasons=("edge_coverage_missing",),
            amplitude_w=amplitude_w,
            robust_snr=robust_snr,
        )

    def loss(delta_on_s: float, delta_off_s: float) -> float:
        return _pulse_loss(
            local,
            baseline_w,
            amplitude_w,
            sigma_w,
            pulse.on_s + delta_on_s,
            pulse.off_s + delta_off_s,
        )

    # Constrained coordinate descent: amplitude is pinned to the plateau
    # median, only the two edge shifts move.
    delta_on_s = 0.0
    delta_off_s = 0.0
    for step_s in (FIT_COARSE_STEP_S, FIT_FINE_STEP_S):
        for _round in range(2):
            candidates = [
                delta
                for delta in _grid(delta_on_s, FIT_HALF_RANGE_S, step_s)
                if abs(delta) <= FIT_HALF_RANGE_S
            ]
            delta_on_s = min(
                candidates, key=lambda delta: loss(delta, delta_off_s)
            )
            candidates = [
                delta
                for delta in _grid(delta_off_s, FIT_HALF_RANGE_S, step_s)
                if abs(delta) <= FIT_HALF_RANGE_S
            ]
            delta_off_s = min(
                candidates, key=lambda delta: loss(delta_on_s, delta)
            )
    best_loss = loss(delta_on_s, delta_off_s)
    flat_loss = math.fsum(
        _huber((interval.power_w - baseline_w) / sigma_w) for interval in local
    )
    if not best_loss < 0.5 * flat_loss:
        return PulseFit(
            pulse_index=pulse_index,
            detected=False,
            reasons=("model_fit_not_significant",),
            amplitude_w=amplitude_w,
            robust_snr=robust_snr,
        )
    if (
        abs(delta_on_s) >= MAX_VALIDATED_EDGE_SHIFT_S
        or abs(delta_off_s) >= MAX_VALIDATED_EDGE_SHIFT_S
    ):
        return PulseFit(
            pulse_index=pulse_index,
            detected=False,
            reasons=("fitted_shift_exceeds_validation_limit",),
            amplitude_w=amplitude_w,
            robust_snr=robust_snr,
            delta_on_s=delta_on_s,
            delta_off_s=delta_off_s,
        )

    # Residual intervals: the contiguous loss-tolerance region around each
    # fitted edge, widened by the commanded-event stamp uncertainty.
    tolerance = max(1.0, 0.05 * best_loss)

    (
        onset_lower_s,
        onset_upper_s,
        offset_lower_s,
        offset_upper_s,
    ) = _accepted_region_projection(
        local=local,
        baseline_w=baseline_w,
        amplitude_w=amplitude_w,
        sigma_w=sigma_w,
        pulse=pulse,
        loss_limit=best_loss + tolerance,
    )
    onset_lower_s -= pulse.on_uncertainty_s
    onset_upper_s += pulse.on_uncertainty_s
    offset_lower_s -= pulse.off_uncertainty_s
    offset_upper_s += pulse.off_uncertainty_s
    return PulseFit(
        pulse_index=pulse_index,
        detected=True,
        reasons=(),
        amplitude_w=amplitude_w,
        robust_snr=robust_snr,
        delta_on_s=delta_on_s,
        delta_off_s=delta_off_s,
        onset_residual_lower_s=onset_lower_s,
        onset_residual_upper_s=onset_upper_s,
        offset_residual_lower_s=offset_lower_s,
        offset_residual_upper_s=offset_upper_s,
    )


def _spurious_plateau_count(
    outside: Sequence[TraceInterval],
    baseline_w: float,
    sigma_w: float,
) -> int:
    threshold_w = baseline_w + max(0.5 * MIN_PLATEAU_W, 5.0 * sigma_w)
    ordered = sorted(outside, key=lambda interval: interval.start_s)
    count = 0
    consecutive = 0
    for interval in ordered:
        if interval.power_w > threshold_w:
            consecutive += 1
            if consecutive == SPURIOUS_MIN_CONSECUTIVE:
                count += 1
        else:
            consecutive = 0
    return count


def detect_pulses(
    intervals: Sequence[TraceInterval],
    pulses: Sequence[CommandedPulse],
    *,
    trace_anchor_bound_s: float = 0.0,
) -> FiducialDetection:
    """Fit every commanded pulse and derive the worst-case residual bound.

    Fails closed: ``b_fiducial_s`` is ``None`` unless every pulse is
    detected, no spurious plateau exists outside the commanded windows, and
    every residual interval is finite.
    """

    if not pulses:
        raise ValueError("pulse fiducial requires at least one commanded pulse")
    if (
        isinstance(trace_anchor_bound_s, bool)
        or not isinstance(trace_anchor_bound_s, int | float)
        or not math.isfinite(float(trace_anchor_bound_s))
        or float(trace_anchor_bound_s) < 0.0
    ):
        raise ValueError("trace_anchor_bound_s must be finite and >= 0")
    baseline_w, sigma_w, outside = _baseline_stats(intervals, pulses)
    fits = tuple(
        _fit_pulse(index, pulse, intervals, baseline_w, sigma_w)
        for index, pulse in enumerate(pulses)
    )
    spurious = _spurious_plateau_count(outside, baseline_w, sigma_w)
    all_detected = all(fit.detected for fit in fits)
    reasons: list[str] = []
    if not all_detected:
        reasons.append("pulse_detection_incomplete")
    if spurious > 0:
        reasons.append("spurious_plateau_detected")
    b_fiducial_s: float | None = None
    residual_median_s: float | None = None
    residual_p95_s: float | None = None
    if not reasons:
        worst_per_edge: list[float] = []
        for fit in fits:
            for lower, upper in (
                (fit.onset_residual_lower_s, fit.onset_residual_upper_s),
                (fit.offset_residual_lower_s, fit.offset_residual_upper_s),
            ):
                if (
                    lower is None
                    or upper is None
                    or not math.isfinite(lower)
                    or not math.isfinite(upper)
                ):
                    reasons.append("residual_interval_unbounded")
                    break
                worst_per_edge.append(max(abs(lower), abs(upper)))
            if reasons:
                break
        if not reasons:
            # The capture's own trace anchor is an independent causal shift of
            # every fitted trace interval. It is additive to the estimator's
            # worst residual excursion and can never shrink the old bound.
            b_fiducial_s = max(worst_per_edge) + float(trace_anchor_bound_s)
            ordered = sorted(worst_per_edge)
            residual_median_s = statistics.median(ordered)
            residual_p95_s = ordered[
                max(0, math.ceil(0.95 * len(ordered)) - 1)
            ]
    return FiducialDetection(
        baseline_w=baseline_w,
        robust_sigma_w=sigma_w,
        fits=fits,
        spurious_plateau_count=spurious,
        all_pulses_detected=all_detected,
        b_fiducial_s=b_fiducial_s,
        residual_median_s=residual_median_s,
        residual_p95_s=residual_p95_s,
        reasons=tuple(reasons),
    )


def clock_stamp_half_width_s(stamp: Any) -> float:
    """Conservative half-width of one paired wall/monotonic stamp."""

    return (stamp.monotonic_after_s - stamp.monotonic_before_s) / 2.0 + max(
        stamp.wall_resolution_s, stamp.monotonic_resolution_s
    )


def trim_trace_after_pulses(
    intervals: Sequence[TraceInterval], pulses: Sequence[CommandedPulse]
) -> list[TraceInterval]:
    """Remove intervals through the final commanded pre-protocol pulse."""

    if not pulses:
        return list(intervals)
    cutoff_s = max(pulse.off_s for pulse in pulses)
    return [interval for interval in intervals if interval.start_s >= cutoff_s]


def rederive_detection_from_artifacts(
    raw_powermetrics: bytes,
    events_jsonl: bytes,
    recorded_clock_anchor: Mapping[str, Any],
) -> FiducialDetection:
    """Re-run calibration physics from hash-verified primary bytes.

    The stored pulse rows and bound are not inputs. Native records plus the
    recorded causal ClockStamps re-derive the trace anchor; pulse command
    stamps come only from ``events.jsonl``; the shared detector then refits
    every pulse and includes the capture's freshly derived anchor bound.
    """

    from joulewise.adapters.powermetrics import (  # noqa: PLC0415
        anchor_records_from_powermetrics,
        parse_powermetrics_records,
    )

    if not isinstance(recorded_clock_anchor, Mapping):
        raise ValueError("calibration clock anchor is missing")
    stamp_rows = recorded_clock_anchor.get("clock_stamps")
    if not isinstance(stamp_rows, Mapping):
        raise ValueError("calibration clock stamps are missing")
    try:
        anchor_stamps = {
            name: stamp_from_mapping(row)
            for name, row in stamp_rows.items()
            if isinstance(row, Mapping)
        }
        native_records = parse_powermetrics_records(raw_powermetrics)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("calibration anchor evidence is malformed") from exc
    derived_anchor = derive_powermetrics_anchor_v2(
        stamps=anchor_stamps,
        records=anchor_records_from_powermetrics(native_records),
    )
    if derived_anchor.get("status") != "bounded":
        raise ValueError("calibration trace anchor is unresolved")
    for field in (
        "method",
        "first_sample_end_point_epoch_s",
        "effective_clock_anchor_bound_s",
    ):
        recorded = recorded_clock_anchor.get(field)
        derived = derived_anchor.get(field)
        if isinstance(derived, float):
            if (
                isinstance(recorded, bool)
                or not isinstance(recorded, int | float)
                or not math.isclose(
                    float(recorded), derived, rel_tol=0.0, abs_tol=1e-12
                )
            ):
                raise ValueError("calibration clock anchor disagrees with raw bytes")
        elif recorded != derived:
            raise ValueError("calibration clock anchor method disagrees")

    try:
        text = events_jsonl.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("calibration events are not UTF-8") from exc
    pairs: dict[str, list[CommandedPulse]] = {"warmup": [], "pulse": []}
    pending: dict[str, Any] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError("calibration event JSON is malformed") from exc
        if not isinstance(row, Mapping):
            raise ValueError("calibration event row is not an object")
        event_type = row.get("event_type")
        if event_type not in {
            "warmup_command_on",
            "warmup_command_off",
            "pulse_command_on",
            "pulse_command_off",
        }:
            continue
        kind, edge = str(event_type).split("_command_", 1)
        metadata = row.get("metadata")
        stamp_row = metadata.get("clock_stamp") if isinstance(metadata, Mapping) else None
        if not isinstance(stamp_row, Mapping):
            raise ValueError("calibration pulse event lacks a ClockStamp")
        try:
            stamp = stamp_from_mapping(stamp_row)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("calibration pulse ClockStamp is malformed") from exc
        if edge == "on":
            if kind in pending:
                raise ValueError("calibration pulse on/off events are ambiguous")
            pending[kind] = stamp
        else:
            on_stamp = pending.pop(kind, None)
            if on_stamp is None or stamp.epoch_s <= on_stamp.epoch_s:
                raise ValueError("calibration pulse on/off events are unpaired")
            pairs[kind].append(
                CommandedPulse(
                    on_s=on_stamp.epoch_s,
                    off_s=stamp.epoch_s,
                    on_uncertainty_s=clock_stamp_half_width_s(on_stamp),
                    off_uncertainty_s=clock_stamp_half_width_s(stamp),
                )
            )
    if pending:
        raise ValueError("calibration pulse event ledger is incomplete")
    if (
        len(pairs["warmup"]) != WARMUP_PULSE_COUNT
        or len(pairs["pulse"]) != PULSE_COUNT
    ):
        raise ValueError("calibration pulse event count disagrees with protocol")

    anchor_s = float(derived_anchor["first_sample_end_point_epoch_s"])
    anchored = parse_powermetrics_records(
        raw_powermetrics, first_record_endpoint_s=anchor_s
    )
    intervals = [
        TraceInterval(
            start_s=record.timestamp_s - record.elapsed_ns / 1_000_000_000.0,
            end_s=record.timestamp_s,
            power_w=record.rail_power_w[PRIMARY_RAIL],
        )
        for record in anchored
    ]
    return detect_pulses(
        trim_trace_after_pulses(intervals, pairs["warmup"]),
        pairs["pulse"],
        trace_anchor_bound_s=float(
            derived_anchor["effective_clock_anchor_bound_s"]
        ),
    )


def verify_stored_evidence_physics(
    evidence: Mapping[str, Any],
    raw_powermetrics: bytes,
    events_jsonl: bytes,
) -> float:
    """Authenticate a valid artifact against its primary physical evidence.

    Returns the widen-only effective bound. Stored status bits, diagnostic
    strings, pulse rows, and the scalar bound cannot substitute for a refit.
    """

    if evidence.get("protocol_id") not in SUPPORTED_PROTOCOL_IDS:
        raise ValueError("instrument protocol is unsupported")
    reasons = evidence.get("reasons")
    if evidence.get("status") != "valid" or not isinstance(reasons, list) or reasons:
        raise ValueError("valid instrument evidence must have no reasons")
    if any(not diagnostic_reason_registered(reason) for reason in reasons):
        raise ValueError("instrument evidence has an unknown reason")
    pulses = evidence.get("pulses")
    if not isinstance(pulses, list) or len(pulses) != PULSE_COUNT:
        raise ValueError("instrument pulse rows are incomplete")
    fresh = rederive_detection_from_artifacts(
        raw_powermetrics, events_jsonl, evidence.get("clock_anchor")
    )
    if (
        fresh.b_fiducial_s is None
        or not fresh.all_pulses_detected
        or fresh.spurious_plateau_count != 0
        or fresh.reasons
        or len(fresh.fits) != len(pulses)
    ):
        raise ValueError("instrument physics does not satisfy the protocol")
    for expected_index, (stored, derived) in enumerate(
        zip(pulses, fresh.fits, strict=True)
    ):
        stored_reasons = stored.get("reasons") if isinstance(stored, Mapping) else None
        if (
            not isinstance(stored, Mapping)
            or stored.get("pulse_index") != expected_index
            or stored.get("detected") is not True
            or not isinstance(stored_reasons, list)
            or stored_reasons
            or any(not diagnostic_reason_registered(reason) for reason in stored_reasons)
            or not derived.detected
            or derived.reasons
        ):
            raise ValueError("stored pulse predicate is invalid")
        for lower_name, upper_name, fitted_name in (
            ("onset_residual_lower_s", "onset_residual_upper_s", "delta_on_s"),
            ("offset_residual_lower_s", "offset_residual_upper_s", "delta_off_s"),
        ):
            lower = stored.get(lower_name)
            upper = stored.get(upper_name)
            fitted = getattr(derived, fitted_name)
            if (
                isinstance(lower, bool)
                or isinstance(upper, bool)
                or not isinstance(lower, int | float)
                or not isinstance(upper, int | float)
                or fitted is None
                or not (float(lower) <= fitted <= float(upper))
            ):
                raise ValueError("stored pulse residual does not contain the refit")
    stored_bound = evidence.get("b_fiducial_s")
    if (
        isinstance(stored_bound, bool)
        or not isinstance(stored_bound, int | float)
        or not math.isfinite(float(stored_bound))
        or float(stored_bound) < 0.0
    ):
        raise ValueError("stored instrument bound is malformed")
    return max(float(stored_bound), float(fresh.b_fiducial_s))


def window_license_min_duration_s(
    b_effective_s: float, cadence_min_duration_s: float
) -> float:
    """T_min = max(4 * B_effective, the existing cadence/sample requirement)."""

    if not math.isfinite(b_effective_s) or b_effective_s < 0.0:
        raise ValueError("B_effective must be finite and >= 0")
    return max(4.0 * b_effective_s, cadence_min_duration_s)


def instrument_evidence(
    detection: FiducialDetection,
    *,
    bindings: Mapping[str, Any],
    validation_id: str,
    artifact_sha256: Mapping[str, str],
    protocol_pulse_count: int = PULSE_COUNT,
    protocol_id: str = PROTOCOL_ID,
    capture_wall_time_s: float | None = None,
) -> dict[str, Any]:
    """Assemble ``instrument_evidence.json`` content, failing closed.

    ``bindings`` must supply every :data:`BINDING_FIELDS` entry non-empty;
    production bundles reference the result by sha256, and any bound-field
    change invalidates the calibration. The v1 protocol binds ALL
    ``protocol_pulse_count`` pulses detected: a run with a fitted bound but
    fewer than the protocol count (or any undetected pulse) is ``invalid``.
    """

    if protocol_id not in SUPPORTED_PROTOCOL_IDS:
        raise ValueError(f"unsupported fiducial protocol: {protocol_id!r}")
    binding_fields = (
        V2_BINDING_FIELDS if protocol_id == PROTOCOL_ID else LEGACY_BINDING_FIELDS
    )
    missing = [
        name
        for name in binding_fields
        if bindings.get(name) in (None, "")
    ]
    pulse_count = len(detection.fits)
    count_ok = pulse_count == protocol_pulse_count
    required_hashes_ok = all(
        isinstance(artifact_sha256.get(name), str)
        and len(artifact_sha256[name]) == 64
        and all(char in "0123456789abcdef" for char in artifact_sha256[name])
        for name in ("raw/powermetrics.plist", "events.jsonl")
    )
    detection_reasons_ok = not detection.reasons
    capture_time_ok = (
        protocol_id != PROTOCOL_ID
        or (
            not isinstance(capture_wall_time_s, bool)
            and isinstance(capture_wall_time_s, int | float)
            and math.isfinite(float(capture_wall_time_s))
            and float(capture_wall_time_s) >= 0.0
        )
    )
    valid = (
        detection.b_fiducial_s is not None
        and not missing
        and detection.all_pulses_detected
        and detection.spurious_plateau_count == 0
        and count_ok
        and required_hashes_ok
        and detection_reasons_ok
        and capture_time_ok
    )
    reasons = list(detection.reasons)
    if missing:
        reasons.append("binding_fields_missing:" + ",".join(sorted(missing)))
    if not detection.all_pulses_detected:
        reasons.append("not_all_pulses_detected")
    if not count_ok:
        reasons.append(
            f"pulse_count_below_protocol:{pulse_count}!={protocol_pulse_count}"
        )
    if detection.spurious_plateau_count != 0:
        reasons.append("spurious_plateau_detected")
    if not required_hashes_ok:
        reasons.append("raw_or_event_hash_missing_or_invalid")
    if not capture_time_ok:
        reasons.append("capture_time_missing_or_invalid")
    payload = {
        "schema_version": "joulewise.instrument_evidence.v1",
        "protocol_id": protocol_id,
        "validation_id": validation_id,
        "status": "valid" if valid else "invalid",
        "reasons": sorted(set(reasons)),
        "anchor_method_version": CLOCK_METHOD_V2,
        "b_fiducial_s": detection.b_fiducial_s,
        "residual_median_s_diagnostic_only": detection.residual_median_s,
        "residual_p95_s_diagnostic_only": detection.residual_p95_s,
        "residual_region_method": RESIDUAL_REGION_METHOD,
        "residual_region_coverage_assumption": (
            "Analytic interval branch-and-bound encloses the complete accepted "
            "two-dimensional joint loss region. A cell is discarded only when "
            "its rigorous overlap-model loss lower bound exceeds the tolerance; "
            "all retained cell extents are included through the stated coverage "
            "resolution. This is deterministic coverage, not a probabilistic "
            "confidence region."
        ),
        "residual_region_coverage_resolution_s": REGION_COVERAGE_RESOLUTION_S,
        "baseline_w": detection.baseline_w,
        "robust_sigma_w": detection.robust_sigma_w,
        "pulse_count": len(detection.fits),
        "all_pulses_detected": detection.all_pulses_detected,
        "spurious_plateau_count": detection.spurious_plateau_count,
        "bindings": {name: bindings.get(name) for name in binding_fields},
        "binding_evidence": {
            "schema_version": "joulewise.instrument_binding_evidence.v1",
            "binding_vector_sha256": hashlib.sha256(
                json.dumps(
                    {name: bindings.get(name) for name in binding_fields},
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                ).encode("utf-8")
            ).hexdigest(),
            "powermetrics_binary": {
                "path": "/usr/bin/powermetrics",
                "sha256": bindings.get("powermetrics_sha256"),
            },
            "power_policy": {"id": bindings.get("power_policy")},
        },
        "artifact_sha256": dict(artifact_sha256),
        "pulses": [
            {
                "pulse_index": fit.pulse_index,
                "detected": fit.detected,
                "reasons": list(fit.reasons),
                "amplitude_w": fit.amplitude_w,
                "robust_snr": fit.robust_snr,
                "delta_on_s": fit.delta_on_s,
                "delta_off_s": fit.delta_off_s,
                "onset_residual_lower_s": fit.onset_residual_lower_s,
                "onset_residual_upper_s": fit.onset_residual_upper_s,
                "offset_residual_lower_s": fit.offset_residual_lower_s,
                "offset_residual_upper_s": fit.offset_residual_upper_s,
            }
            for fit in detection.fits
        ],
    }
    if protocol_id == PROTOCOL_ID:
        payload[CAPTURE_TIME_FIELD] = capture_wall_time_s
        payload["max_age_s"] = MAX_AGE_S
    return payload


def run_matmul_pulse(duration_s: float, buffers: Any = None) -> int:
    """Drive one GPU pulse of preallocated FP16 MLX matmuls with fencing.

    Returns the number of fenced matmuls issued. Requires ``mlx`` (live
    [QUIET-MAC] runs only; never imported at module load so CI stays pure).
    """

    import time

    import mlx.core as mx  # noqa: PLC0415 - live-run-only dependency

    if buffers is None:
        buffers = allocate_matmul_buffers()
    left, right = buffers
    issued = 0
    deadline = time.monotonic() + duration_s
    while time.monotonic() < deadline:
        product = mx.matmul(left, right)
        mx.eval(product)  # GPU fence: the pulse edge stays honest
        issued += 1
    return issued


def allocate_matmul_buffers() -> tuple[Any, Any]:
    """Preallocate the pulse workload buffers (outside any pulse window)."""

    import mlx.core as mx  # noqa: PLC0415 - live-run-only dependency

    left = mx.random.normal((MATRIX_SIDE, MATRIX_SIDE)).astype(mx.float16)
    right = mx.random.normal((MATRIX_SIDE, MATRIX_SIDE)).astype(mx.float16)
    mx.eval(left, right)
    return left, right
