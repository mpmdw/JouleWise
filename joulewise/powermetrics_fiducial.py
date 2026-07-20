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

import math
import statistics
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from joulewise.uncertainty_evidence import CLOCK_METHOD_V2

PROTOCOL_ID = "powermetrics_pulse_fiducial_v1"
PULSE_COUNT = 40
WARMUP_PULSE_COUNT = 3
PULSE_DURATION_S = 1.0
PULSE_GAP_BASE_S = 1.5
BASELINE_S = 5.0
MATRIX_SIDE = 4096
MATRIX_DTYPE = "float16"
PRIMARY_RAIL = "gpu_power"
CORROBORATION_RAILS = ("cpu_power", "gpu_power")
MIN_PLATEAU_W = 10.0
MIN_ROBUST_SNR = 10.0
FIT_HALF_RANGE_S = 0.75
FIT_COARSE_STEP_S = 0.005
FIT_FINE_STEP_S = 0.0005
HUBER_DELTA = 1.345
PLATEAU_INSET_S = 0.25
LOCAL_MARGIN_S = 0.75
SPURIOUS_MIN_CONSECUTIVE = 2
# Binding fields (hash-referenced): any change invalidates the calibration.
BINDING_FIELDS = (
    "hardware_model",
    "os_build",
    "powermetrics_sha256",
    "sampling_interval_ms",
    "anchor_method_version",
    "mlx_version",
    "pulse_protocol_id",
    "power_policy",
)


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

    # Residual intervals: the contiguous loss-tolerance region around each
    # fitted edge, widened by the commanded-event stamp uncertainty.
    tolerance = max(1.0, 0.05 * best_loss)

    def residual_interval(
        fitted_s: float, evaluate: Any, stamp_uncertainty_s: float
    ) -> tuple[float, float]:
        lower = fitted_s
        upper = fitted_s
        for delta in _grid(fitted_s, FIT_HALF_RANGE_S, FIT_FINE_STEP_S):
            if abs(delta) > FIT_HALF_RANGE_S:
                continue
            if evaluate(delta) <= best_loss + tolerance:
                lower = min(lower, delta)
                upper = max(upper, delta)
        return lower - stamp_uncertainty_s, upper + stamp_uncertainty_s

    onset_lower_s, onset_upper_s = residual_interval(
        delta_on_s,
        lambda delta: loss(delta, delta_off_s),
        pulse.on_uncertainty_s,
    )
    offset_lower_s, offset_upper_s = residual_interval(
        delta_off_s,
        lambda delta: loss(delta_on_s, delta),
        pulse.off_uncertainty_s,
    )
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
) -> FiducialDetection:
    """Fit every commanded pulse and derive the worst-case residual bound.

    Fails closed: ``b_fiducial_s`` is ``None`` unless every pulse is
    detected, no spurious plateau exists outside the commanded windows, and
    every residual interval is finite.
    """

    if not pulses:
        raise ValueError("pulse fiducial requires at least one commanded pulse")
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
            b_fiducial_s = max(worst_per_edge)
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
) -> dict[str, Any]:
    """Assemble ``instrument_evidence.json`` content, failing closed.

    ``bindings`` must supply every :data:`BINDING_FIELDS` entry non-empty;
    production bundles reference the result by sha256, and any bound-field
    change invalidates the calibration.
    """

    missing = [
        name
        for name in BINDING_FIELDS
        if bindings.get(name) in (None, "")
    ]
    valid = detection.b_fiducial_s is not None and not missing
    reasons = list(detection.reasons)
    if missing:
        reasons.append("binding_fields_missing:" + ",".join(sorted(missing)))
    return {
        "schema_version": "joulewise.instrument_evidence.v1",
        "protocol_id": PROTOCOL_ID,
        "validation_id": validation_id,
        "status": "valid" if valid else "invalid",
        "reasons": sorted(reasons),
        "anchor_method_version": CLOCK_METHOD_V2,
        "b_fiducial_s": detection.b_fiducial_s,
        "residual_median_s_diagnostic_only": detection.residual_median_s,
        "residual_p95_s_diagnostic_only": detection.residual_p95_s,
        "baseline_w": detection.baseline_w,
        "robust_sigma_w": detection.robust_sigma_w,
        "pulse_count": len(detection.fits),
        "all_pulses_detected": detection.all_pulses_detected,
        "spurious_plateau_count": detection.spurious_plateau_count,
        "bindings": {name: bindings.get(name) for name in BINDING_FIELDS},
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
