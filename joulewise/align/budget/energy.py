"""Gross episode integration with explicit edge, clock and sensor uncertainty.

Point power is estimated with piecewise-linear interpolation; window means
are constant over their recorded supports. The half-width also
bounds arbitrary transitions within intervals whose sensor readings change,
plus quantization and bracket edges. Identical sampled levels cannot reveal
unseen excursions; no undocumented sensor-accuracy bound is claimed.
"""

from __future__ import annotations

import json
import math
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from typing import Sequence

from joulewise.align.records import Episode, PowerTrace
from joulewise.align.power.windows import window_supports


@dataclass(frozen=True)
class Energy:
    joules: float | None
    uncertainty_j: float | None = None
    flags: tuple[str, ...] = ()


def trace_flags(trace: PowerTrace) -> tuple[str, ...]:
    """Read sampler flags from structured notes without changing PowerTrace."""
    try:
        notes = json.loads(trace.notes)
        return tuple(str(f) for f in notes.get("flags", ())) if isinstance(notes, dict) else ()
    except (ValueError, TypeError):
        return ()


def _notes(trace: PowerTrace) -> dict:
    try:
        value = json.loads(trace.notes)
        return value if isinstance(value, dict) else {}
    except (ValueError, TypeError):
        return {}


def _edge(trace: PowerTrace, t: int) -> tuple[float, float]:
    """Interpolated value and enclosing counter increment."""
    i = bisect_left(trace.t_ns, t)
    if i < len(trace.t_ns) and trace.t_ns[i] == t:
        return trace.values[i], 0.0
    a, b = trace.t_ns[i - 1], trace.t_ns[i]
    x, y = trace.values[i - 1], trace.values[i]
    return x + (y - x) * ((t - a) / (b - a)), y - x


def _interpolate(trace: PowerTrace, t: int) -> float:
    return _edge(trace, t)[0]


def _window_integral(supports, values, start, end, maximum):
    """Overlap allocation and nonnegative-Pmax enclosure of cut windows.

    A window of width w and mean p contains p*w joules. Its overlap of
    length L contains between max(0, p*w-Pmax*(w-L)) and min(p*w, Pmax*L).
    Full windows therefore have no within-window allocation error.
    """
    energies, bounds = [], []
    previous = None
    for (a, b), value in zip(supports, values):
        if previous is not None:
            t, power = previous
            lo, hi = max(start, t), min(end, a)
            if hi > lo:
                left = power + (value-power)*(lo-t)/(a-t)
                right = power + (value-power)*(hi-t)/(a-t)
                area = (hi-lo)/1_000_000_000*(left+right)/2
                energies.append(area)
                bounds.append(max(area, maximum*(hi-lo)/1_000_000_000-area)
                              if maximum is not None else math.inf)
        lo, hi = max(start, a), min(end, b)
        if hi > lo:
            width, overlap = (b-a)/1_000_000_000, (hi-lo)/1_000_000_000
            area = value*overlap
            energies.append(area)
            if lo != a or hi != b:
                lower = max(0., value*width-maximum*(width-overlap)) if maximum is not None else 0.
                upper = min(value*width, maximum*overlap) if maximum is not None else math.inf
                bounds.append(max(area-lower, upper-area))
        previous = b, value
    return math.fsum(energies), math.fsum(bounds)


def _median_interval_ns(intervals: list[int]) -> float:
    """Select the observed median in linear time, preserving the reducer's scaling."""
    def select(values: list[int], rank: int) -> int:
        # Median-of-five pivots discard at least 3n/10 values per selection.
        # T(n) <= T(n/5) + T(7n/10) + O(n), hence O(n), unlike sorting all polls.
        if len(values) <= 5:
            return sorted(values)[rank]
        groups = [values[i:i + 5] for i in range(0, len(values), 5)]
        medians = [sorted(group)[len(group) // 2] for group in groups]
        pivot = select(medians, len(medians) // 2)
        lower = [v for v in values if v < pivot]
        equal = sum(v == pivot for v in values)
        if rank < len(lower):
            return select(lower, rank)
        if rank < len(lower) + equal:
            return pivot
        return select([v for v in values if v > pivot], rank - len(lower) - equal)

    middle = len(intervals) // 2
    upper = select(intervals, middle)
    if len(intervals) % 2:
        return float(upper)
    return (select(intervals, middle - 1) + upper) / 2


def episode_energy(episode: Episode, *,
                   channels: Sequence[tuple[str, str]] | None = None,
                   power_max_w: float | None = None,
                   gap_factor: float = 1.5) -> Energy:
    """Select nonoverlapping channels explicitly; no implicit choice among sensors.

    power_max_w is a prospective physical envelope, also accepted from the
    sampler's JSON notes (power_bound_w) or episode.hardware. An unknown envelope
    yields an infinite power interpolation bound, with a flag, while retaining J.
    Summaries export that as an unknown bound rather than a nonfinite JSON number.

    gap_factor is an operator parameter: 1.5 is the midpoint between one
    completed sampling cycle and a missed cycle near twice that duration.
    Estimate the cycle from the median observed interval (minimum for fewer
    than three intervals), including event.wait and acquisition overhead, with
    the nominal wait as a lower bound. This diagnostic assumes normal cycles
    remain observable; it never discards energy.
    """
    traces = episode.power_traces
    if not traces:
        return Energy(None, flags=("energy_trace_missing",))
    if channels is None:
        if len(traces) != 1:
            return Energy(None, flags=("energy_channels_unspecified",))
    else:
        keys = set(map(tuple, channels))
        traces = tuple(t for t in traces if (t.source, t.channel) in keys)
        if len(traces) != len(keys):
            return Energy(None, flags=("energy_channel_missing_or_duplicate",))
    if not traces:
        return Energy(None, flags=("energy_channel_missing",))
    values, bounds, flags = [], [], list(episode.flags)
    for trace in traces:
        flags.extend(trace_flags(trace))
        if (trace.resolution is not None
                and (not math.isfinite(trace.resolution) or trace.resolution < 0)):
            return Energy(None, flags=("energy_resolution_invalid",))
        if trace.averaging_window_ns is not None and trace.averaging_window_ns < 0:
            return Energy(None, flags=("energy_averaging_window_invalid",))
        offset, uncertainty_ns = 0, 0
        if trace.clock_domain != episode.clock_domain:
            mappings = [m for m in episode.clock_mappings
                        if m.trace_domain == trace.clock_domain
                        and m.episode_domain == episode.clock_domain]
            if len(mappings) != 1 or mappings[0].uncertainty_ns < 0:
                return Energy(None, flags=("energy_clock_mapping_invalid",))
            if mappings[0].method == "unmeasured":
                return Energy(None, flags=("energy_clock_mapping_unmeasured",))
            offset, uncertainty_ns = mappings[0].offset_ns, mappings[0].uncertainty_ns
        start, end = episode.start_ns - offset, episode.end_ns - offset
        try:
            supports = window_supports(trace, flags=flags)
        except ValueError:
            return Energy(None, flags=("energy_window_support_invalid",))
        if supports is not None:
            if any(s is None for s in supports):
                return Energy(None, flags=("energy_window_support_unknown",))
            # Conversion-quantum disagreements have already been snapped and
            # counted by window_supports; any remaining overlap is real.
            if any(b > c for (_, b), (c, _) in zip(supports, supports[1:])):
                return Energy(None, flags=("energy_window_overlap",))
        coverage_start = supports[0][0] if supports else (trace.t_ns[0] if trace.t_ns else 0)
        if (len(trace.t_ns) < (1 if supports else 2) or coverage_start > start + uncertainty_ns
                or trace.t_ns[-1] < end - uncertainty_ns):
            return Energy(None, flags=("energy_trace_unbracketed",))
        # A synchronous first poll can lie inside the mapping's uncertainty
        # bracket, even though it preceded the true call. Retain the measured
        # overlap and bound the missing sliver, rather than discarding J.
        # This exception is limited to +/- the stated clock half-width:
        # a same-domain missing bracket still has no estimate.
        partial = (coverage_start > start - uncertainty_ns
                   or trace.t_ns[-1] < end + uncertainty_ns)
        if partial:
            flags.append("energy_clock_bracket_partial")
        measured_start = max(start, coverage_start)
        measured_end = min(end, trace.t_ns[-1])
        if measured_start > measured_end:
            return Energy(None, flags=("energy_trace_unbracketed",))
        if any(not math.isfinite(v) or v < 0 for v in trace.values):
            return Energy(None, flags=("energy_samples_invalid",))
        if supports is None:
            first, delta_a = _edge(trace, measured_start)
            last, delta_b = _edge(trace, measured_end)
        duration_s = (end - start) / 1_000_000_000
        maximum = power_max_w
        if maximum is None:
            maximum = _notes(trace).get("power_bound_w")
            if maximum is None:
                maximum = episode.hardware.get("power_max_w")
        if maximum is not None and (not math.isfinite(maximum) or maximum < 0
                                    or (trace.unit == "W" and maximum < max(trace.values))):
            flags.append("energy_power_max_invalid")
            maximum = None
        if trace.unit == "J_cumulative":
            if any(b < a for a, b in zip(trace.values, trace.values[1:])):
                return Energy(None, flags=("energy_counter_reset",))
            joules = last - first
            # Monotonic counter truth at an edge lies between enclosing readings.
            # Their entire increment bounds interpolation error without a Pmax.
            # Include the clock-shift enclosure too, so no average-power estimate
            # is mistaken for a bound on a subinterval.
            edge_bound = delta_a + delta_b
            if uncertainty_ns:
                for t in (start, end):
                    lo = max(0, bisect_left(trace.t_ns, t - uncertainty_ns) - 1)
                    hi = min(len(trace.t_ns) - 1, bisect_left(trace.t_ns, t + uncertainty_ns))
                    edge_bound += trace.values[hi] - trace.values[lo]
            # Outside the sampled clock envelope a cumulative counter gives
            # no increment. Its missing duration needs a prospective Pmax;
            # without one retain J with an explicitly unbounded half-width.
            missing_ns = (max(0, trace.t_ns[0] - (start - uncertainty_ns))
                          + max(0, end + uncertainty_ns - trace.t_ns[-1]))
            if missing_ns:
                if maximum is None:
                    flags.append("energy_power_max_missing")
                edge_bound += maximum * missing_ns / 1_000_000_000 if maximum is not None else math.inf
            bound = None if trace.resolution is None else trace.resolution + edge_bound
        elif supports is not None:
            joules, allocation_bound = _window_integral(
                supports, trace.values, measured_start, measured_end, maximum)
            missing_ns = max(0, coverage_start-start) + max(0, end-trace.t_ns[-1])
            edge_ns = missing_ns + 2*uncertainty_ns
            edge_bound = (maximum*edge_ns/1_000_000_000 if maximum is not None
                          else (math.inf if edge_ns else 0.))
            bound = (None if trace.resolution is None else
                     trace.resolution*duration_s/2 + allocation_bound + edge_bound)
            if maximum is None:
                flags.append("energy_power_max_missing")
            if any(b < c for (_, b), (c, _) in zip(supports, supports[1:])):
                flags.append("energy_window_gap")
            flags.append("energy_window_average_over_support")
        else:
            # Walk the interior once; only the two edges need binary search.
            interior = [(t, v) for t, v in zip(trace.t_ns, trace.values)
                        if measured_start < t < measured_end]
            points = [(measured_start, first), *interior, (measured_end, last)]
            joules = math.fsum((b - a) / 1_000_000_000 * (x + y) / 2
                              for (a, x), (b, y) in zip(points, points[1:]))
            if maximum is None:
                flags.append("energy_power_max_missing")
            # An unsynchronised edge segment extends to the poll INSIDE the
            # episode. With power in [0, Pmax], its error is at most Pmax times
            # that inward distance, even when the outer poll is much closer.
            # A clock shift can carry an edge over a poll into an interval
            # formerly treated as interior. Use the first poll strictly past
            # start+u and last poll strictly before end-u. The additional 2*u
            # covers displacement of the two integration limits themselves.
            # At u=0 preserve zero width at an exactly synchronized poll.
            if uncertainty_ns:
                ia = min(len(trace.t_ns) - 1, bisect_right(trace.t_ns, start + uncertainty_ns))
                ib = max(0, bisect_left(trace.t_ns, end - uncertainty_ns) - 1)
                inward_a = max(0, trace.t_ns[ia] - start)
                inward_b = max(0, end - trace.t_ns[ib])
            else:
                ia, ib = bisect_left(trace.t_ns, start), bisect_left(trace.t_ns, end)
                inward_a = trace.t_ns[ia] - start
                inward_b = 0 if trace.t_ns[ib] == end else end - trace.t_ns[ib - 1]
            edge_seconds = (inward_a + inward_b + 2 * uncertainty_ns
                            + 2 * (trace.averaging_window_ns or 0)) / 1_000_000_000
            bound = None if trace.resolution is None else trace.resolution * duration_s / 2
            if bound is not None:
                bound += maximum * edge_seconds if maximum is not None else math.inf
                # A changed sensor level may hide multiple phase transitions
                # (e.g. decode -> wait -> prefill) within that poll interval.
                # Its true integral is in [0, Pmax*dt]; the furthest endpoint
                # from the trapezoid gives the physical error bound below.
                # Repeated identical sensor codes define constant-level
                # interiors in this conditional model. Equality here tests
                # reported code identity, not numerical agreement. Unseen
                # excursions returning to the same code remain unidentifiable.
                # A declared linear synthetic trace needs no transition term.
                if _notes(trace).get("interior_model") != "piecewise_linear":
                    if maximum is not None:
                        bound += math.fsum((b - a) / 1_000_000_000
                                           * max((x + y) / 2, maximum - (x + y) / 2)
                                           for (a, x), (b, y) in zip(points, points[1:]) if x != y)
                    flags.append("energy_transition_interpolation_bound")
        if trace.resolution is None:
            flags.append("energy_resolution_unknown")
        if trace.duty_fraction is not None and trace.duty_fraction < 1:
            flags.append("energy_duty_cycled_requires_repetitions")
            bound = None
        intervals = [b - a for a, b in zip(trace.t_ns, trace.t_ns[1:])]
        # event.wait(T) followed by acquisition A has cycle T+A, not T.
        # A missed cycle is near 2*(T+A); 1.5 is their midpoint. The observed
        # median estimates T+A without treating normal acquisition as a gap.
        # After one dropped poll, one of n intervals is doubled. For n >= 3,
        # the n-1 normal intervals are a strict majority, so both median ranks
        # are normal. For n=2 the median mixes normal and doubled intervals;
        # use the minimum instead. A lone interval cannot identify a lost poll.
        observed_cycle = (min(intervals) if 0 < len(intervals) < 3
                          else _median_interval_ns(intervals) if intervals else 0)
        cycle_ns = max(trace.nominal_interval_ns, observed_cycle)
        if any(interval > gap_factor * cycle_ns for interval in intervals):
            flags.append("energy_sample_gap")
        if supports is None:
            flags.append("energy_piecewise_linear_between_samples")
        values.append(joules)
        bounds.append(bound)
    total_bound = math.fsum(bounds) if all(b is not None for b in bounds) else None
    if any(trace.source == "powermetrics" for trace in traces):
        # The ~1 J attribution minimum belongs to the run total, including
        # a total over multiple disjoint rails; never sum one floor per rail.
        flags.append("energy_powermetrics_attribution_floor")
        total_bound = None if total_bound is None else max(1.0, total_bound)
    return Energy(math.fsum(values), total_bound,
                  tuple(sorted(set(flags))))
