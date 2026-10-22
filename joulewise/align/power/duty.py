"""Reconstruct deterministic workload energy from repeated sensor windows.

This is a lane-local adapter around PowerTrace. It pools the actual covered
windows, rather than connecting sparse readings with a line. Diagnostics are
flags, including cases in which a finite uncertainty cannot be identified.
"""

from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Sequence

from joulewise.align.records import PowerTrace

# A declared reporting convention, not a data-dependent acceptance threshold.
# The Monte Carlo test checks this nominal 95% interval under its stated model.
DUTY_CONFIDENCE = 0.95
_NS_PER_S = 1_000_000_000


@dataclass(frozen=True)
class DutyEstimate:
    joules: float
    half_width_j: float
    coverage_fraction: float
    flags: tuple[str, ...]


@dataclass(frozen=True)
class _Window:
    run: int
    left: int
    right: int
    watts: float
    resolution: float
    timing_ns: int


def plan_offsets(period_ns: int, duty_fraction: float, repeats: int) -> list[int]:
    """Tile the period, then repeat those phases to measure repeatability.

    ceil(1/d) phases suffice to cover a period with d*period-wide windows.
    Fewer requested repeats spread the available phases evenly. Integer floor
    division places each phase within one nanosecond of its ideal location.
    Invalid plans return an empty list, since this signature has no flags field.
    """
    if (not isinstance(period_ns, int) or isinstance(period_ns, bool) or period_ns <= 0
            or not isinstance(repeats, int) or isinstance(repeats, bool) or repeats <= 0
            or not math.isfinite(duty_fraction) or not 0 < duty_fraction <= 1):
        return []
    phases = repeats if duty_fraction*repeats <= 1 else math.ceil(1 / duty_fraction)
    return [(index % phases) * period_ns // phases for index in range(repeats)]


def _beta_fraction(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta, using the continued fraction expansion."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    if x > (a + 1) / (a + b + 2):
        return 1 - _beta_fraction(b, a, 1 - x)
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                     + a * math.log(x) + b * math.log1p(-x))
    # Lentz's fraction needs a nonzero denominator. sqrt(min-normal) avoids
    # reciprocal overflow; the convergence bar is 1e-6 relative (the brief's
    # bar for computations without a separately printed uncertainty).
    tiny = math.sqrt(float.fromhex("0x1.0p-1022"))
    c, d = 1.0, 1 - (a + b) * x / (a + 1)
    d = 1 / max(abs(d), tiny) * (1 if d >= 0 else -1)
    result = d
    for m in range(1, 10001):  # Numerical iteration budget, not a measurement cut.
        for coefficient in (
            m * (b - m) * x / ((a + 2*m - 1) * (a + 2*m)),
            -(a + m) * (a + b + m) * x / ((a + 2*m) * (a + 2*m + 1)),
        ):
            d = 1 + coefficient * d
            c = 1 + coefficient / c
            if abs(d) < tiny:
                d = math.copysign(tiny, d)
            if abs(c) < tiny:
                c = math.copysign(tiny, c)
            d = 1 / d
            change = d * c
            result *= change
        if abs(change - 1) <= 1e-12:
            # This is six orders tighter than the required 1e-6 relative
            # numerical agreement, leaving that budget for summation.
            return front * result / a
    raise ArithmeticError("incomplete beta did not converge")


def _student_quantile(probability: float, df: float) -> float:
    """Positive Student-t quantile, inverted independently of optional scipy."""
    if probability == 0.5:
        return 0.0
    if probability < 0.5:
        return -_student_quantile(1 - probability, df)
    if not 0 < probability < 1 or df <= 0:
        raise ValueError("invalid Student-t probability or degrees of freedom")

    def cdf(value: float) -> float:
        return 1 - _beta_fraction(df / 2, 0.5, df / (df + value*value)) / 2

    lower, upper = 0.0, 1.0
    while cdf(upper) < probability:
        upper *= 2
    while upper - lower > 1e-10 * max(1.0, upper):
        # 1e-10 relative is below 1% of a printed 1e-6 uncertainty,
        # and above a million double-precision ulps near unit scale.
        middle = (lower + upper) / 2
        if cdf(middle) < probability:
            lower = middle
        else:
            upper = middle
    return (lower + upper) / 2


def _metadata(notes: str) -> dict[str, Any]:
    try:
        value = json.loads(notes)
        return value if isinstance(value, dict) else {}
    except (TypeError, ValueError):
        return {}


def estimate_energy(runs: Sequence[tuple[PowerTrace, int, int]]) -> DutyEstimate:
    """Pool aligned sensor windows and report a nominal 95% energy interval.

    A reading y_i is a mean over its original W_i-wide window. On every atom
    of the union inside the workload, average the active readings and integrate.
    Divide by covered fraction C to extrapolate the covered mean over gaps.
    This defines coefficients c_i (seconds), so E = sum(c_i*y_i).

    Half-width is the SUM of three separately derived terms:
    * Quantization: sum(abs(c_i)*q_i/2), with q_i the sensor's stated quantum.
    * Repeatability: group runs with identical aligned window geometry. For
      each run z_r=sum(its c_i*y_i); group g contributes n_g*var(z_r) to the
      variance. A Welch-Satterthwaite Student-t interval combines the groups.
      It assumes independent Gaussian run shifts and a deterministic workload;
      phase replicas are required, because different phases contain real work.
    * Coverage/smoothing/timing: K(t)=sum(c_i/W_i on original windows).
      With a caller-justified 0<=P(t)<=B, bias is bounded by B times the larger
      positive/negative area of K(t)-1_workload. A whole-window timing shift
      bounded by delta adds B*sum(abs(c_i)*min(delta/W_i,1)). This also handles
      means whose windows straddle the workload boundaries without pretending
      the clipped mean was measured.

    Optional JSON notes repeat_group labels planned sensor phases under scheduler
    jitter. Actual endpoints and the requested E stay unchanged. Let h_r=sum c
    for run r and H_g=sum h in a declared group of n runs. An auxiliary estimate
    uses d_ri=(H_g/n)*c_ri/h_r, so every normalized run contribution has the same
    Gaussian run-shift noise scale. Its variance is H_g**2*var(z_r/h_r)/n.
    Compute all quantum/kernel/timing bounds with d and widen by abs(E-E_aux).
    Triangle inequality transfers that interval to the requested E. Unequal
    deterministic means inflate the residual spread; Welch remains approximate,
    and this optional path is explicitly provisional. A label is never inferred
    by rounding observed timestamps or changing the integration geometry.

    Without B, nonzero uncovered/smoothing/timing bias has unbounded half-width.
    Unknown resolution, unreplicated phases and unknown sensor age also produce
    infinite width plus a flag, never a refusal. Bounds cover sensor quantum,
    not unprovided calibration accuracy. Counter traces are not power windows.
    """
    flags = {"deterministic_workload_assumed", "nominal_95pct_gaussian_repeatability",
             "sensor_accuracy_not_included"}
    windows: list[_Window] = []
    signatures: dict[int, tuple[tuple[int, int], ...]] = {}
    labels: dict[int, str | int] = {}
    bounds: list[float] = []
    duration: int | None = None
    unknown_timing = False
    for run_index, item in enumerate(runs):
        try:
            trace, start, end = item
            if (not isinstance(start, int) or not isinstance(end, int) or end <= start
                    or isinstance(start, bool) or isinstance(end, bool)
                    or trace.unit != "W" or not isinstance(trace.averaging_window_ns, int)
                    or isinstance(trace.averaging_window_ns, bool)
                    or trace.averaging_window_ns <= 0 or trace.duty_fraction is None):
                flags.add("invalid_or_unknown_sensor_run")
                continue
            metadata = _metadata(trace.notes)
            if "output_average_not_single_window" in metadata.get("flags", ()):
                flags.add("output_average_not_single_window")
                continue
            if any(not math.isfinite(value) or value < 0 for value in trace.values):
                flags.add("invalid_power_run")
                continue
            run_duration = end - start
            if duration is not None and run_duration != duration:
                flags.add("duration_mismatch")
                continue
            quantum = trace.resolution
            if quantum is None or not math.isfinite(quantum) or quantum <= 0:
                flags.add("sensor_resolution_unknown")
                continue
            timing = metadata.get("window_timing_half_width_ns",
                                  metadata.get("timing_half_width_ns"))
            endpoints = metadata.get("window_end_ns", trace.t_ns)
            if timing is None:
                timing = [0] * len(trace.values)
                flags.add("timing_uncertainty_unreported")
            if (len(timing) != len(trace.values) or len(endpoints) != len(trace.values)
                    or any(not isinstance(x, int) or x < 0 for x in timing)
                    or any(not isinstance(x, int) for x in endpoints)):
                flags.add("invalid_window_timing")
                continue
            run_unknown_timing = False
            if any(flag in metadata.get("flags", ()) for flag in
                   ("sensor_update_phase_unreported", "driver_field_timestamp_is_wall_clock")):
                if "window_end_ns" not in metadata:
                    run_unknown_timing = True
                    flags.add("sensor_window_time_unknown")
            run_windows = [
                _Window(run_index, timestamp - start - trace.averaging_window_ns,
                        timestamp - start, value, quantum, bracket)
                for timestamp, value, bracket in zip(endpoints, trace.values, timing)
                if timestamp - start > 0
                and timestamp - start - trace.averaging_window_ns < run_duration
            ]
            if not run_windows:
                flags.add("run_without_coverage")
                continue
            candidate = metadata.get("power_bound_w")
            if isinstance(candidate, (int, float)) and math.isfinite(candidate) and candidate > 0:
                bounds.append(float(candidate))
                if any(window.watts > candidate for window in run_windows):
                    flags.add("power_bound_violated")
                    run_unknown_timing = True
            else:
                bounds.append(math.inf)
            duration = run_duration
            unknown_timing |= run_unknown_timing
            label = metadata.get("repeat_group")
            if isinstance(label, (str, int)) and not isinstance(label, bool):
                labels[run_index] = label
            signatures[run_index] = tuple((window.left, window.right) for window in run_windows)
            windows.extend(run_windows)
        except (TypeError, ValueError, AttributeError, OverflowError):
            flags.add("malformed_run")
    if not windows or duration is None:
        flags.add("no_covered_work")
        return DutyEstimate(0.0, math.inf, 0.0, tuple(sorted(flags)))

    # Event sweep uses exact rational geometry, so exact tilings have exactly
    # zero missing/smoothing area even when the coefficients are repeating.
    events: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for index, window in enumerate(windows):
        events[max(0, window.left)].append((index, 1))
        events[min(duration, window.right)].append((index, -1))
    coefficients = [Fraction() for _ in windows]  # nanoseconds
    active: set[int] = set()
    covered = 0
    previous = 0
    for boundary in sorted(events):
        if active and boundary > previous:
            span = boundary - previous
            covered += span
            weight = Fraction(span, len(active))
            for index in active:
                coefficients[index] += weight
        for index, sign in events[boundary]:
            active.add(index) if sign == 1 else active.discard(index)
        previous = boundary
    if covered == 0:
        flags.add("no_covered_work")
        return DutyEstimate(0.0, math.inf, 0.0, tuple(sorted(flags)))
    coefficients = [weight * Fraction(duration, covered) for weight in coefficients]
    if covered < duration:
        flags.add("partial_coverage")
    seconds = [float(weight / _NS_PER_S) for weight in coefficients]
    joules = math.fsum(weight * window.watts for weight, window in zip(seconds, windows))
    interval_coefficients = coefficients
    center_widening = 0.0
    declared_groups: dict[Any, list[int]] = defaultdict(list)
    auxiliary_variances: list[tuple[float, int]] = []
    if labels:
        flags.add("declared_phase_groups_auxiliary_interval")
        flags.add("repeatability_interval_provisional")
        for run_index, signature in signatures.items():
            key = ("label", type(labels[run_index]).__name__, labels[run_index]) if run_index in labels else (
                "geometry", signature)
            declared_groups[key].append(run_index)
        run_weights: dict[int, Fraction] = defaultdict(Fraction)
        run_contributions: dict[int, list[float]] = defaultdict(list)
        for coefficient, weight, window in zip(coefficients, seconds, windows):
            run_weights[window.run] += coefficient
            run_contributions[window.run].append(weight*window.watts)
        interval_coefficients = list(coefficients)
        for members in declared_groups.values():
            total = sum((run_weights[index] for index in members), Fraction())
            normalized = [
                math.fsum(run_contributions[index])/float(run_weights[index]/_NS_PER_S)
                for index in members]
            if len({signatures[index] for index in members}) > 1:
                flags.add("phase_geometry_varies")
            for index, window in enumerate(windows):
                if window.run in members:
                    interval_coefficients[index] *= total/(len(members)*run_weights[window.run])
            if len(members) >= 2:
                auxiliary_variances.append((
                    float(total/_NS_PER_S)**2/len(members)*statistics.variance(normalized),
                    len(members)-1))
        interval_seconds = [float(weight/_NS_PER_S) for weight in interval_coefficients]
        auxiliary_energy = math.fsum(
            weight*window.watts for weight, window in zip(interval_seconds, windows))
        center_widening = abs(joules-auxiliary_energy)
    else:
        interval_seconds = seconds
    quantization = math.fsum(weight * window.resolution / 2
                             for weight, window in zip(interval_seconds, windows))

    # Original, unclipped windows matter: boundary-straddling means contain
    # power from outside the workload, which cannot be removed by clipping.
    kernel_events: dict[int, Fraction] = defaultdict(Fraction)
    kernel_events[0] -= 1
    kernel_events[duration] += 1
    timing_area = Fraction()
    for coefficient, window in zip(interval_coefficients, windows):
        kernel_weight = coefficient / (window.right - window.left)
        kernel_events[window.left] += kernel_weight
        kernel_events[window.right] -= kernel_weight
        timing_area += coefficient * min(Fraction(window.timing_ns,
                                                   window.right - window.left), 1)
    positive = negative = Fraction()
    kernel = Fraction()
    previous = min(kernel_events)
    for boundary in sorted(kernel_events):
        area = kernel * (boundary - previous)
        positive += max(area, 0)
        negative += max(-area, 0)
        kernel += kernel_events[boundary]
        previous = boundary
    mismatch = max(positive, negative) + timing_area
    bound = max(bounds) if bounds else math.inf
    bias = float(mismatch / _NS_PER_S) * bound if mismatch else 0.0
    if mismatch:
        flags.add("coverage_smoothing_or_timing_bound")
        if not math.isfinite(bound):
            flags.add("power_bound_required")
    if unknown_timing:
        bias = math.inf

    variances: list[tuple[float, int]] = []
    spread = 0.0
    if labels:
        variances = auxiliary_variances
        if any(len(members) < 2 for members in declared_groups.values()):
            flags.add("phase_without_replicates")
            spread = math.inf
    else:
        contributions: dict[int, list[float]] = defaultdict(list)
        for weight, window in zip(seconds, windows):
            contributions[window.run].append(weight*window.watts)
        groups: dict[tuple[tuple[int, int], ...], list[float]] = defaultdict(list)
        for index, signature in signatures.items():
            groups[signature].append(math.fsum(contributions[index]))
        for values in groups.values():
            if len(values) < 2:
                flags.add("phase_without_replicates")
                spread = math.inf
            else:
                variances.append((len(values)*statistics.variance(values), len(values)-1))
    if math.isfinite(spread):
        variance = math.fsum(value for value, _ in variances)
        if variance > 0:
            denominator = math.fsum(value*value / df for value, df in variances)
            degrees = variance*variance / denominator
            spread = _student_quantile((1 + DUTY_CONFIDENCE) / 2, degrees) * math.sqrt(variance)
    return DutyEstimate(joules, quantization + bias + spread + center_widening, covered / duration,
                        tuple(sorted(flags)))


__all__ = ["DutyEstimate", "DUTY_CONFIDENCE", "plan_offsets", "estimate_energy"]
