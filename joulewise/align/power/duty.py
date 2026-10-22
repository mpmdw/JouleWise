"""Reconstruct deterministic workload energy from repeated sensor windows.

This is a lane-local adapter around PowerTrace. It pools the actual covered
windows, rather than connecting sparse readings with a line. Diagnostics are
flags, including cases in which a finite uncertainty cannot be identified.
"""

from __future__ import annotations

import json
import math
import statistics
import warnings
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
    At least ceil(1/d) repeats are needed to tile (four for 25-of-100 ms).
    Fewer repeats emit RuntimeWarning and spread the available phases evenly;
    estimate_energy retains their data with partial_coverage and a bound.
    Two replicas per phase identify within-phase repeatability. Integer floor
    division places each phase within one nanosecond of its ideal location.
    Invalid plans return an empty list, since this signature has no flags field.
    """
    if (not isinstance(period_ns, int) or isinstance(period_ns, bool) or period_ns <= 0
            or not isinstance(repeats, int) or isinstance(repeats, bool) or repeats <= 0
            or not math.isfinite(duty_fraction) or not 0 < duty_fraction <= 1):
        return []
    minimum = math.ceil(1 / duty_fraction)
    if repeats < minimum:
        warnings.warn(f"{repeats} repeats cannot tile the period; need at least {minimum}",
                      RuntimeWarning, stacklevel=2)
    phases = min(repeats, minimum)
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
        # Four orders tighter than the required 1e-6 relative agreement
        # leaves numerical error budget for the CDF evaluation.
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
    """Estimate the mean run's energy from aligned sensor windows.

    Let A(u)=count{r:D_r>u}/n be the fraction of retained runs still active.
    Integrate A(u) times the mean of readings covering u; each window is
    clipped to its own [0,D_r]. M=integral A=mean(D_r), C=integral_covered A.
    Multiply by M/C: E=sum(c_i*y_i), sum(c_i)=M seconds. This targets the
    mean run, including duration-varying tails, rather than the longest run.

    The statistical term is the existing two-sided 95% Gaussian/Welch
    repeatability interval. Phase groups use exact geometry or repeat_group.
    If h_r=sum(c_i) for run r and H_g=sum(h_r), auxiliary coefficients are
    d_i=(H_g/n_g)*c_i/h_r. Normalize each run's weighted mean, multiply by
    D_r/mean(D_g) to include duration spread, and combine independent group
    variances with Welch-Satterthwaite degrees of freedom. Add the center
    displacement |sum(c_i*y_i)-sum(d_i*y_i)| by triangle inequality.
    Quantum contributes sum(|d_i|*q_i/2), assuming rounding to the quantum.

    Add these systematic BOUNDS linearly, not in quadrature. R is the range
    of valid readings from retained traces, INCLUDING pre/post-roll:
    * Coverage: (M-C)*R. Extrapolation error is missing time times the
      difference of missing and covered mean powers. Assumption: power over
      uncovered time stays in the observed range.
    * Boundary: sum(|d_i|*(1-l_i/w_i)*R_b), w_i the original window width
      and l_i its inside length. A whole-window mean differs from its
      inside mean by outside_fraction*(outside_mean-inside_mean). R_b is
      the range across each run's nearest fully inside and fully outside
      readings at that boundary. This assumes the boundary contrast stays
      within that observed LOCAL range. If any run lacks either bracketing
      window, use global R. A window straddling both edges uses max(R_b).
      Selection uses actual endpoints, with no fixed neighborhood radius.
    * Known timing: sum(|d_i|*min(h_i/w_i,1)*R), since translating a
      w_i-wide mean by at most h_i replaces at most min(h_i,w_i) of it.
      Timing assumes the underlying displaced-window contrast stays within
      global R; window averages cannot establish these range assumptions.
    * An unreplicated phase cannot identify its variance. Its group mass
      times R is a finite center-error envelope under the additional
      unreplicated_phase_observed_range_assumed assumption. It is flagged,
      not an identified Gaussian variance; use two replicas per phase.

    Numeric flags expose each term and the range assumption is explicit.
    power_bound_w is NEVER required for these terms. The independent
    worst_case_bias_j=<value> diagnostic still uses a supplied instantaneous
    bound B times the original-window kernel mismatch plus timing area; a
    missing B can make that diagnostic infinite without changing the width.

    Unknown sensor age is not a known endpoint bracket: a contributing
    legacy poll-time proxy gives infinite width, even if notes bound its
    maximum age. Unknown resolution/timing also keeps the energy and gives
    infinite width. Unknown duty with a known window is only a flag.
    Invalid readings are counted and omitted individually. Mixed channels
    or clocks are flagged. Sensor calibration accuracy is not included.
    """
    flags = {"deterministic_workload_assumed",
             "nominal_95pct_gaussian_repeatability_plus_observed_range_bounds",
             "observed_range_bounds_assumed", "sensor_accuracy_not_included"}
    windows: list[_Window] = []
    signatures: dict[int, tuple[tuple[int, int], ...]] = {}
    labels: dict[int, str | int] = {}
    bounds: list[float] = []
    duration: int | None = None
    durations: dict[int, int] = {}
    unknown_timing = False
    unknown_resolution = False
    channels: set[str] = set()
    clocks: set[str] = set()
    invalid_samples = 0
    observed: list[float] = []
    boundary_readings: list[list[float]] = [[], []]
    boundary_bracketed = [True, True]
    for run_index, item in enumerate(runs):
        try:
            trace, start, end = item
            channels.add(trace.channel)
            clocks.add(trace.clock_domain)
            if (not isinstance(start, int) or not isinstance(end, int) or end <= start
                    or isinstance(start, bool) or isinstance(end, bool)
                    or trace.unit != "W" or not isinstance(trace.averaging_window_ns, int)
                    or isinstance(trace.averaging_window_ns, bool)
                    or trace.averaging_window_ns <= 0):
                flags.add("invalid_or_unknown_sensor_run")
                continue
            metadata = _metadata(trace.notes)
            if "output_average_not_single_window" in metadata.get("flags", ()):
                flags.add("output_average_not_single_window")
                continue
            if trace.duty_fraction is None:
                flags.add("sensor_duty_unknown")
            run_duration = end - start
            quantum = trace.resolution
            run_unknown_resolution = (not isinstance(quantum, (int, float)) or
                                      not math.isfinite(quantum) or quantum <= 0)
            if run_unknown_resolution:
                flags.add("sensor_resolution_unknown")
                quantum = 0.0  # Resolution affects uncertainty, never the energy estimate.
            timing = metadata.get("window_timing_half_width_ns",
                                  metadata.get("timing_half_width_ns"))
            endpoints = trace.t_ns  # Shared record contract: ends of averaging windows.
            if timing is None:
                timing = [0] * len(trace.values)
                flags.add("timing_uncertainty_unreported")
            if (not isinstance(timing, (list, tuple)) or len(timing) != len(trace.values)
                    or any(x is not None and (not isinstance(x, int) or x < 0) for x in timing)):
                flags.add("invalid_window_timing")
                # Metadata cannot remove otherwise usable sensor readings.
                # Keep the energy; unidentified timing makes width infinite.
                timing = [None]*len(trace.values)
            if any(not isinstance(x, int) for x in endpoints):
                flags.add("invalid_window_endpoints")
                continue
            run_unknown_timing = any(x is None for x in timing)
            reported_flags = metadata.get("flags", ())
            if ("sensor_age_unknown" in reported_flags
                    and not isinstance(metadata.get("window_end_ns"), (list, tuple))):
                # A maximum age is not a measured sensor window endpoint.
                # Per-sample endpoint notes below isolate contributing unknowns.
                run_unknown_timing = True
            if any(flag in reported_flags for flag in
                   ("sensor_update_phase_unreported", "driver_field_timestamp_is_wall_clock")):
                if "window_end_ns" not in metadata:
                    run_unknown_timing = True
            window_ends = metadata.get("window_end_ns")
            if isinstance(window_ends, (list, tuple)):
                run_unknown_timing |= any(
                    endpoint is None and timestamp-start > 0
                    and timestamp-start-trace.averaging_window_ns < run_duration
                    for timestamp, endpoint in zip(endpoints, window_ends))
            valid_readings = [math.isfinite(value) and value >= 0 for value in trace.values]
            invalid_samples += sum(not valid for valid in valid_readings)
            run_windows = [
                _Window(run_index, timestamp - start - trace.averaging_window_ns,
                        timestamp - start, value, quantum, bracket or 0)
                for timestamp, value, bracket, valid in zip(endpoints, trace.values, timing, valid_readings)
                if valid and timestamp - start > 0
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
                    bounds[-1] = math.inf  # Invalid bound only voids the systematic receipt.
            else:
                bounds.append(math.inf)
            observed.extend(value for value, valid in zip(trace.values, valid_readings) if valid)
            all_windows = [(timestamp-start-trace.averaging_window_ns,
                            timestamp-start, value)
                           for timestamp, value, valid in zip(endpoints, trace.values, valid_readings)
                           if valid]
            inside = [item for item in all_windows if item[0] >= 0 and item[1] <= run_duration]
            outside = ([item for item in all_windows if item[1] <= 0],
                       [item for item in all_windows if item[0] >= run_duration])
            # Nearest observed full windows bracket each edge. No arbitrary
            # neighborhood radius: actual window endpoints select the data.
            for edge in (0, 1):
                if not inside or not outside[edge]:
                    boundary_bracketed[edge] = False
                    continue
                inner = (min(inside, key=lambda item: item[0]) if edge == 0 else
                         max(inside, key=lambda item: item[1]))
                outer = (max(outside[edge], key=lambda item: item[1]) if edge == 0 else
                         min(outside[edge], key=lambda item: item[0]))
                boundary_readings[edge].extend((inner[2], outer[2]))
            durations[run_index] = run_duration
            duration = max(durations.values())
            unknown_resolution |= run_unknown_resolution
            unknown_timing |= run_unknown_timing
            label = metadata.get("repeat_group")
            if isinstance(label, (str, int)) and not isinstance(label, bool):
                labels[run_index] = label
            # Exact sensor-grid phase is independent of how many terminal
            # windows a duration happens to include. Never round timestamps to
            # merge jittered phases: those require explicit repeat_group labels.
            differences = [b-a for a, b in zip(endpoints, endpoints[1:])]
            period = int(statistics.median(differences)) if differences else trace.nominal_interval_ns
            signatures[run_index] = ((period, trace.averaging_window_ns),
                                     (run_windows[0].right % period, 0)) if period > 0 else tuple(
                                         (w.left, w.right) for w in run_windows)
            windows.extend(run_windows)
        except (TypeError, ValueError, AttributeError, OverflowError):
            flags.add("malformed_run")
    if len(channels) > 1:
        flags.add("mixed_channels")
    if len(clocks) > 1:
        flags.add("mixed_clock_domains")
    if invalid_samples:
        flags.add(f"invalid_power_samples:{invalid_samples}")
    flags.add(f"runs_retained={len(durations)}")
    if len(set(durations.values())) > 1:
        flags.add("durations_differ")
        flags.add(f"duration_spread_ns={max(durations.values())-min(durations.values())}")
    if not windows or duration is None:
        flags.add("no_covered_work")
        return DutyEstimate(0.0, math.inf, 0.0, tuple(sorted(flags)))

    # Event sweep uses exact rational geometry, so exact tilings have exactly
    # zero missing/smoothing area even when the coefficients are repeating.
    events: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for index, window in enumerate(windows):
        events[max(0, window.left)].append((index, 1))
        events[min(durations[window.run], window.right)].append((index, -1))
    coefficients = [Fraction() for _ in windows]  # nanoseconds
    run_count = len(durations)
    mean_duration = Fraction(sum(durations.values()), run_count)
    ending_runs: dict[int, int] = defaultdict(int)
    for run_duration in durations.values():
        ending_runs[run_duration] += 1
        events[run_duration]  # Split tails even at an endpoint without a window.
    remaining = run_count
    active: set[int] = set()
    covered = Fraction()
    previous = 0
    for boundary in sorted(events):
        if active and boundary > previous:
            span = boundary - previous
            mass = Fraction(span * remaining, run_count)
            covered += mass
            weight = mass / len(active)
            for index in active:
                coefficients[index] += weight
        for index, sign in events[boundary]:
            active.add(index) if sign == 1 else active.discard(index)
        remaining -= ending_runs[boundary]
        previous = boundary
    if covered == 0:
        flags.add("no_covered_work")
        return DutyEstimate(0.0, math.inf, 0.0, tuple(sorted(flags)))
    coefficients = [weight * mean_duration / covered for weight in coefficients]
    if covered < mean_duration:
        flags.add("partial_coverage")
    seconds = [float(weight / _NS_PER_S) for weight in coefficients]
    joules = math.fsum(weight * window.watts for weight, window in zip(seconds, windows))
    interval_coefficients = coefficients
    center_widening = 0.0
    declared_groups: dict[Any, list[int]] = defaultdict(list)
    auxiliary_variances: list[tuple[float, int]] = []
    if signatures:
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
            group_duration = statistics.mean(durations[index] for index in members)
            normalized = [
                math.fsum(run_contributions[index])/float(run_weights[index]/_NS_PER_S)
                * durations[index]/group_duration
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
    for run_duration in durations.values():
        kernel_events[run_duration] += Fraction(1, run_count)
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
            flags.add("worst_case_bias_unbounded")
    if unknown_timing:
        flags.add("sensor_window_time_unknown")
        bias = math.inf
    flags.add(f"worst_case_bias_j={bias!r}")

    reading_range = max(observed)-min(observed)
    flags.add(f"observed_reading_range_w={reading_range!r}")
    coverage_bound = float((mean_duration-covered)/_NS_PER_S)*reading_range
    boundary_ranges = [max(readings)-min(readings) if complete else reading_range
                       for readings, complete in zip(boundary_readings, boundary_bracketed)]
    flags.add("boundary_observed_range_assumed")
    if not all(boundary_bracketed):
        flags.add("boundary_range_fallback_global")
    flags.add(f"boundary_start_range_w={boundary_ranges[0]!r}")
    flags.add(f"boundary_end_range_w={boundary_ranges[1]!r}")
    boundary_bound = math.fsum(
        weight * (1-Fraction(min(window.right, durations[window.run])-max(window.left, 0),
                            window.right-window.left)) * max(
                                boundary_ranges[0] if window.left < 0 else 0.0,
                                boundary_ranges[1] if window.right > durations[window.run] else 0.0)
        for weight, window in zip(interval_seconds, windows))
    timing_bound = float(timing_area/_NS_PER_S)*reading_range
    unreplicated_bound = 0.0
    if any(len(members) < 2 for members in declared_groups.values()):
        flags.add("phase_without_replicates")
        flags.add("unreplicated_phase_observed_range_assumed")
        unreplicated_bound = math.fsum(
            float(sum((run_weights[index] for index in members), Fraction())/_NS_PER_S)
            * reading_range for members in declared_groups.values() if len(members) < 2)

    variances = auxiliary_variances
    spread = 0.0
    if math.isfinite(spread):
        variance = math.fsum(value for value, _ in variances)
        if variance > 0:
            denominator = math.fsum(value*value / df for value, df in variances)
            degrees = variance*variance / denominator
            spread = _student_quantile((1 + DUTY_CONFIDENCE) / 2, degrees) * math.sqrt(variance)
    for name, value in (("coverage_bound_j", coverage_bound),
                        ("boundary_bound_j", boundary_bound),
                        ("timing_bound_j", timing_bound),
                        ("unreplicated_phase_bound_j", unreplicated_bound),
                        ("repeatability_half_width_j", spread),
                        ("resolution_bound_j", quantization),
                        ("auxiliary_center_bound_j", center_widening)):
        flags.add(f"{name}={value!r}")
    half_width = (quantization + spread + center_widening + coverage_bound
                  + boundary_bound + timing_bound + unreplicated_bound)
    if unknown_resolution or unknown_timing:
        half_width = math.inf
    return DutyEstimate(joules, half_width, float(covered / mean_duration),
                        tuple(sorted(flags)))


__all__ = ["DutyEstimate", "DUTY_CONFIDENCE", "plan_offsets", "estimate_energy"]
