"""Independent twin of ``joulewise.align.power.duty`` (lane A2 "nvml").

Twinned: ``plan_offsets``, ``estimate_energy`` and the ``DutyEstimate`` record.

Written from three texts only: the lane brief (night-archive
forward-20261021/align/briefs/nvml.md, item 2), the ``PowerTrace`` record in
``joulewise/align/records.py`` and ``docs/align/PIPELINE.md``. The lane's own
module was not read. The twin is run beside that module on the same inputs; a
disagreement points at a defect in one of the two or at a sentence of the brief
the two read differently (the READINGS block below lists this twin's readings).

Stdlib only. Written for transparency over speed: each quantity is a direct
formula that can be checked by hand, with no vectorised or incremental tricks.

The brief's item 2, quoted (the contract):

    "when the sensor reports power averaged over only a fraction d of each
    period T, a single run's energy is under-sampled. Repeating a deterministic
    workload with start offsets spread over the period recovers it. Implement:
    plan_offsets(period_ns, duty_fraction, repeats) -> list[int] (offsets that
    tile the period) and estimate_energy(runs: Sequence[tuple[PowerTrace, int,
    int]]) -> DutyEstimate(joules, half_width_j, coverage_fraction, flags),
    where each run is a trace with its workload start and end in the trace
    clock; align the runs on workload start, pool the windows each sample
    actually covered, and integrate the pooled coverage. The half-width is
    derived from the covered fraction, the sensor resolution and the
    run-to-run spread (state the derivation in the docstring)."

READINGS
========

Where the brief leaves a choice open, this twin takes the most literal reading.

R1  Offsets are spread evenly over the period: offset_k = floor(k * T / n) for
    k = 0 .. n-1, integer nanoseconds, ascending, measured from a sensor period
    boundary (offset_k is the phase within the period at which run k's
    workload starts). Integer floor division, not round(): the two differ by at
    most 1 ns.

R2  "Offsets that tile the period" is read as a guarantee. A window of length
    d*T placed at each offset (modulo T) must cover the whole period, which is
    possible only when n * d >= 1. Fewer repeats raise ValueError instead of
    returning offsets that leave gaps. Apart from this check, plan_offsets does
    not use duty_fraction. The check allows one machine epsilon, the rounding
    carried by duty_fraction itself and by the product n * d (half an ulp
    each), so that, for example, n = 49 with d = 1/49 passes.

R3  A sample at t_ns covers the window [t_ns - w, t_ns] in the trace clock,
    with w = averaging_window_ns. This follows the PowerTrace docstring: "the
    sensor's reading at t_ns, averaged over averaging_window_ns ending at
    t_ns". When a trace has no averaging_window_ns, w = nominal_interval_ns
    (the sample stands for the interval since the previous nominal sample)
    and the flag "averaging_window_unknown" is raised. estimate_energy needs
    neither duty_fraction nor the period.

R4  Each window is cut down to its own run's workload [start, end]. The reading
    (the mean over the whole window) is assigned unchanged to the part that
    remains. Every window is used as recorded. Two samples of one run whose
    windows overlap (polling faster than the window) are both kept and are not
    merged.

R5  Runs are aligned on workload start: aligned time u = t - start. The pooled
    power p(u) is the plain mean of the readings of every window, from any run,
    that covers u, with each window weighted equally.

R6  joules = integral of p(u) over the covered set C only. Time that no window
    covers adds nothing to joules: gaps are not filled with an assumed power.
    The missing energy appears instead in the half-width (R8a).

R7  coverage_fraction = |C| / max_r D_r, where D_r = end_r - start_r. After
    alignment the workloads together span [0, max_r D_r].

R8  half_width_j is the plain sum (not a root-sum-square) of three terms:
    (a) coverage: (max_r D_r - |C|) * P_max, where P_max is the largest
        |reading| among windows that overlap a workload. This is the most
        energy the uncovered time can hold if its power stays at or below the
        largest reading the sensor reported.
    (b) resolution: q * |C|, where q is the largest PowerTrace.resolution among
        the runs. A quantised reading lies within one quantum of the true
        window mean whether the sensor rounds or truncates (q/2 would hold only
        for rounding, which is not recorded). Any mean of such readings is
        also within q, and integrating over the covered time gives q * |C|.
        A trace with resolution None adds 0 and raises "resolution_unknown".
    (c) run-to-run spread: each run with coverage gives its own single-run
        estimate E_r = D_r * pbar_r, where pbar_r is the time-mean of that run's
        own pooled readings over its own covered set. With m such runs,
        term = t(0.975, m-1) * stdev(E_r) / sqrt(m): the two-sided 95% Student
        t half-width of the mean of the E_r. When m < 2 the term is 0 and the
        flag "spread_unavailable" is raised.
    Terms (a) and (b) are worst-case bounds, not standard errors, so adding in
    quadrature would be wrong; they add linearly to (c).

R9  Refused with ValueError: an empty runs sequence; a trace whose unit is not
    "W" (an energy-counter trace has no duty-cycle problem and is not the
    input this function integrates); a run with end <= start. Every other
    condition is a flag: "incomplete_coverage" (coverage_fraction < 1),
    "durations_differ" (not every D_r is equal, compared as integers),
    "mixed_channels" (the runs do not share one (source, channel)),
    "run_without_coverage" (some run's windows miss its workload), and
    "no_coverage" (no window covers any workload: joules 0, half-width inf).
    flags is a sorted, de-duplicated tuple.

R10 Units: each piece of the integral is computed in watt-nanoseconds,
    summed with math.fsum (correctly rounded) and divided by 1e9 once. The
    integer divisor 10**9 is exact.
"""

from __future__ import annotations

import math
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:  # annotation only; the twin reads PowerTrace by attribute
    from joulewise.align.records import PowerTrace

NS_PER_S = 1_000_000_000

# Two-sided level of the run-to-run spread term (R8c).
SPREAD_LEVEL = 0.95


@dataclass(frozen=True)
class DutyEstimate:
    """The brief's ``DutyEstimate(joules, half_width_j, coverage_fraction, flags)``."""

    joules: float
    half_width_j: float
    coverage_fraction: float
    flags: tuple[str, ...] = ()


def plan_offsets(period_ns: int, duty_fraction: float, repeats: int) -> list[int]:
    """Start offsets for ``repeats`` runs, spread evenly over one sensor period.

    Implements the brief's "plan_offsets(period_ns, duty_fraction, repeats) ->
    list[int] (offsets that tile the period)" and "start offsets spread over
    the period".

    offset_k = floor(k * period_ns / repeats), k = 0 .. repeats-1 (R1). A
    window of length duty_fraction * period_ns starting at each offset covers
    the period only if repeats * duty_fraction >= 1; fewer repeats cannot tile
    the period and raise ValueError (R2).
    """
    if not isinstance(period_ns, int) or isinstance(period_ns, bool) or period_ns <= 0:
        raise ValueError("period_ns must be a positive integer")
    if not isinstance(repeats, int) or isinstance(repeats, bool) or repeats < 1:
        raise ValueError("repeats must be a positive integer")
    if not 0.0 < duty_fraction <= 1.0:
        raise ValueError("duty_fraction must lie in (0, 1]")
    # n * d >= 1, allowing one machine epsilon: duty_fraction carries up to half
    # an ulp of representation error and the product another half ulp (R2).
    if repeats * duty_fraction < 1.0 - sys.float_info.epsilon:
        need = math.ceil(1.0 / duty_fraction)
        raise ValueError(
            f"{repeats} windows of {duty_fraction} of the period cannot tile it; need at least {need}")
    return [k * period_ns // repeats for k in range(repeats)]


def estimate_energy(runs: Sequence[tuple["PowerTrace", int, int]]) -> DutyEstimate:
    """Energy of one execution of a repeated deterministic workload, from duty-cycled power traces.

    Implements the brief's "align the runs on workload start, pool the windows
    each sample actually covered, and integrate the pooled coverage", with
    "the half-width ... derived from the covered fraction, the sensor
    resolution and the run-to-run spread".

    Each run is ``(trace, start_ns, end_ns)`` with start and end in the trace
    clock.

    Estimate. Sample i of run r covers W_ri = [t_i - w_r, t_i] (R3), cut to
    [start_r, end_r] and shifted to aligned time u = t - start_r (R4, R5). At
    each u, p(u) is the mean of the readings of every window that covers u.
    The breakpoints of all windows split the aligned axis into elementary
    intervals, and p is constant on each one, so

        joules = (1/1e9) * sum over covered elementary intervals [x0, x1) of
                 mean(readings covering it) * (x1 - x0)          [W * ns -> J]

    (R6). coverage_fraction = |C| / D, where |C| is the total length of the
    covered intervals and D = max_r (end_r - start_r) (R7).

    Half-width derivation (R8), in joules:

    (a) Covered fraction. The uncovered time D - |C| = (1 - coverage) * D
        carries energy that no window saw. Power is non-negative, and the
        assumption is that it does not exceed P_max, the largest reading. The
        missing energy then lies in [0, (1 - coverage) * D * P_max], so a
        half-width of that size around joules contains it.
            hw_cov = (1 - coverage_fraction) * D * P_max
    (b) Sensor resolution. Each reading lies within one quantum q of its
        window's true mean power. So does p(u), a mean of such readings, at
        every covered u, and integrating over |C| gives
            hw_res = q * |C|.
    (c) Run-to-run spread. Run r alone gives E_r = D_r * pbar_r, where pbar_r
        = (integral of run r's own pooled readings) / |C_r|. If the runs'
        phases were drawn independently and uniformly over the period, the
        E_r would be independent estimates of the run energy, scattered by
        real run-to-run variation and by the part of the waveform each run's
        windows happened to see. Their mean would then carry the Student t
        half-width
            hw_spread = t(0.975, m - 1) * stdev(E_1..E_m) / sqrt(m)
        at the two-sided 95% level, over the m runs with coverage. Planned
        offsets (plan_offsets) spread the phases more evenly than random
        draws, so this half-width is conservative for them.

        half_width_j = hw_cov + hw_res + hw_spread.

    Bounds (a) and (b) are added linearly to the statistical term (c),
    because they are worst cases and not standard errors.
    """
    if len(runs) == 0:
        raise ValueError("estimate_energy needs at least one run")

    flags: set[str] = set()
    all_windows: list[tuple[int, int, float]] = []
    per_run_windows: list[list[tuple[int, int, float]]] = []
    durations: list[int] = []
    resolutions: list[float] = []
    channels: set[tuple[str, str]] = set()

    for trace, start_ns, end_ns in runs:
        if trace.unit != "W":
            raise ValueError(f"estimate_energy integrates power traces (unit 'W'), got {trace.unit!r}")
        if end_ns <= start_ns:
            raise ValueError("each run's workload must end after it starts")
        durations.append(end_ns - start_ns)
        channels.add((trace.source, trace.channel))
        if trace.resolution is None:
            flags.add("resolution_unknown")
        else:
            resolutions.append(float(trace.resolution))
        window_ns = trace.averaging_window_ns
        if window_ns is None:
            window_ns = trace.nominal_interval_ns
            flags.add("averaging_window_unknown")
        run_windows = sample_windows(trace.t_ns, trace.values, window_ns, start_ns, end_ns)
        per_run_windows.append(run_windows)
        all_windows.extend(run_windows)

    if len(channels) > 1:
        flags.add("mixed_channels")
    if len(set(durations)) > 1:
        flags.add("durations_differ")

    reference_ns = max(durations)
    integral_w_ns, covered_ns = pooled_integral(all_windows)
    joules = integral_w_ns / NS_PER_S
    coverage_fraction = covered_ns / reference_ns
    if covered_ns < reference_ns:
        flags.add("incomplete_coverage")

    # (a) covered-fraction term
    uncovered_ns = reference_ns - covered_ns
    if not all_windows:
        flags.add("no_coverage")
        hw_cov = math.inf
    else:
        p_max = max(abs(value) for _, _, value in all_windows)
        hw_cov = uncovered_ns * p_max / NS_PER_S

    # (b) resolution term
    quantum = max(resolutions) if resolutions else 0.0
    hw_res = quantum * covered_ns / NS_PER_S

    # (c) run-to-run spread term
    single_run = single_run_estimates(per_run_windows, durations)
    if len(single_run) < len(runs):
        flags.add("run_without_coverage")
    if len(single_run) >= 2:
        m = len(single_run)
        hw_spread = student_t_quantile(SPREAD_LEVEL, m - 1) * statistics.stdev(single_run) / math.sqrt(m)
    else:
        flags.add("spread_unavailable")
        hw_spread = 0.0

    return DutyEstimate(
        joules=joules,
        half_width_j=hw_cov + hw_res + hw_spread,
        coverage_fraction=coverage_fraction,
        flags=tuple(sorted(flags)),
    )


# ------------------------------------------------------------------ helpers

def sample_windows(t_ns: Sequence[int], values: Sequence[float], window_ns: int,
                   start_ns: int, end_ns: int) -> list[tuple[int, int, float]]:
    """The window each sample covered, cut to the workload and in aligned time (R3, R4, R5).

    Sample (t, v) covers [t - window_ns, t]; the part inside [start_ns, end_ns]
    is returned as (a - start_ns, b - start_ns, v). Windows that miss the
    workload, or touch it in a single point, are dropped.
    """
    out: list[tuple[int, int, float]] = []
    for t, value in zip(t_ns, values):
        a = max(t - window_ns, start_ns)
        b = min(t, end_ns)
        if b > a:
            out.append((a - start_ns, b - start_ns, float(value)))
    return out


def pooled_integral(windows: Sequence[tuple[int, int, float]]) -> tuple[float, int]:
    """Integral of the pooled power over the covered set, and the covered length (R5, R6).

    ``windows`` holds (a, b, reading) intervals in aligned ns. The breakpoints
    of all windows split the axis into elementary intervals [x0, x1). On each
    one the covering set does not change, and p = mean of the covering
    readings. Returns (sum of p * (x1 - x0) over covered intervals [W*ns],
    sum of (x1 - x0) over covered intervals [ns]).

    The covering set is kept by a left-to-right sweep. At each breakpoint the
    windows that end there leave and the windows that start there enter, so a
    window [a, b] counts on [a, b).
    """
    if not windows:
        return 0.0, 0
    starts: dict[int, list[int]] = defaultdict(list)
    ends: dict[int, list[int]] = defaultdict(list)
    for index, (a, b, _) in enumerate(windows):
        starts[a].append(index)
        ends[b].append(index)
    breakpoints = sorted(set(starts) | set(ends))

    active: dict[int, float] = {}
    pieces: list[float] = []
    covered_ns = 0
    for x0, x1 in zip(breakpoints, breakpoints[1:]):
        for index in ends.get(x0, ()):
            del active[index]
        for index in starts.get(x0, ()):
            active[index] = windows[index][2]
        if active:
            mean_w = math.fsum(active.values()) / len(active)
            pieces.append(mean_w * (x1 - x0))
            covered_ns += x1 - x0
    return math.fsum(pieces), covered_ns


def single_run_estimates(per_run_windows: Sequence[Sequence[tuple[int, int, float]]],
                         durations: Sequence[int]) -> list[float]:
    """E_r = D_r * pbar_r in joules, for each run whose windows cover any of its workload (R8c)."""
    estimates: list[float] = []
    for run_windows, duration_ns in zip(per_run_windows, durations):
        integral_w_ns, covered_ns = pooled_integral(run_windows)
        if covered_ns > 0:
            mean_power_w = integral_w_ns / covered_ns
            estimates.append(duration_ns * mean_power_w / NS_PER_S)
    return estimates


def student_t_two_sided_mass(t: float, dof: int) -> float:
    """P(|T| <= t) for Student's t with integer ``dof`` degrees of freedom.

    Closed-form finite series of Abramowitz and Stegun (1964), 26.7.3 (odd
    dof) and 26.7.4 (even dof), with theta = atan(t / sqrt(dof)):

      dof = 1:     A = 2 theta / pi
      dof odd > 1: A = (2/pi) [theta + sin(theta) (cos(theta)
                     + (2/3) cos^3(theta) + ...
                     + (2*4*...*(dof-3)) / (1*3*...*(dof-2)) cos^(dof-2)(theta))]
      dof even:    A = sin(theta) [1 + (1/2) cos^2(theta)
                     + (1*3)/(2*4) cos^4(theta) + ...
                     + (1*3*...*(dof-3)) / (2*4*...*(dof-2)) cos^(dof-2)(theta)]
    """
    if dof < 1:
        raise ValueError("dof must be a positive integer")
    theta = math.atan(t / math.sqrt(dof))
    s, c = math.sin(theta), math.cos(theta)
    if dof == 1:
        return 2.0 * theta / math.pi
    if dof % 2 == 1:
        term = c
        series = [term]
        for k in range(1, (dof - 3) // 2 + 1):
            term = term * (2 * k) / (2 * k + 1) * c * c
            series.append(term)
        return (2.0 / math.pi) * (theta + s * math.fsum(series))
    term = 1.0
    series = [term]
    for k in range(1, (dof - 2) // 2 + 1):
        term = term * (2 * k - 1) / (2 * k) * c * c
        series.append(term)
    return s * math.fsum(series)


def student_t_quantile(level: float, dof: int) -> float:
    """t such that P(|T| <= t) = level (the two-sided ``level`` half-width multiplier).

    Bisection on student_t_two_sided_mass, which increases with t. The search
    stops when the midpoint equals an endpoint, meaning the bracket is down
    to adjacent floats.
    """
    if not 0.0 < level < 1.0:
        raise ValueError("level must lie in (0, 1)")
    lo, hi = 0.0, 1.0
    while student_t_two_sided_mass(hi, dof) < level:
        lo, hi = hi, hi * 2.0
    while True:
        mid = 0.5 * (lo + hi)
        if mid <= lo or mid >= hi:
            return hi
        if student_t_two_sided_mass(mid, dof) < level:
            lo = mid
        else:
            hi = mid


__all__ = ["DutyEstimate", "plan_offsets", "estimate_energy"]
