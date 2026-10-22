"""Energy attribution from power traces to episode phases and tool intervals.

Point power is linear between samples; a window mean owns [t-window, t].
Uncovered duty intervals bridge the neighbouring window means linearly.
Their measured fraction is encoded as
window_average_W;duty.uncovered_fraction=<repr(float)>; the corresponding
flag is duty.uncovered. Fractions refer to the requested interval, excluding
out-of-trace time (which instead carries trace.partial_coverage).

The half-width is the additive sensitivity bound required by A4, not a
statistical confidence interval or a guarantee against unsampled work.
Missing uncertainty metadata contributes zero and an explicit flag.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections.abc import Sequence
from dataclasses import dataclass
import math
from typing import overload

from joulewise.align.records import ClockMapping, Episode, PowerTrace
from joulewise.bundle_read import TracePoint
from joulewise.reduce import _integrate


_NS_PER_S = 1_000_000_000  # Definition of the nanosecond, not an estimator constant.


@dataclass(frozen=True)
class EnergyEstimate:
    joules: float
    half_width_j: float
    method: str
    flags: tuple[str, ...]


@dataclass(frozen=True)
class SegmentEnergy:
    turn: int | None
    kind: str
    start_ns: int
    end_ns: int
    energy: EnergyEstimate


@dataclass(frozen=True)
class EpisodeAttribution:
    episode_id: str
    channel: str
    total: EnergyEstimate
    segments: tuple[SegmentEnergy, ...]
    flags: tuple[str, ...]


@dataclass(frozen=True)
class _Span:
    start: int
    end: int
    left: float
    right: float
    uncovered: bool = False

    def integral(self, start: int, end: int) -> float:
        # Subtract integer epochs BEFORE conversion, as phase_share does.
        # Import the established reducer instead of duplicating its trapezoid.
        duration = (self.end - self.start) / _NS_PER_S
        return _integrate(
            [TracePoint(t=0.0, power_w=self.left),
             TracePoint(t=duration, power_w=self.right)],
            (start - self.start) / _NS_PER_S,
            (end - self.start) / _NS_PER_S,
        )


class _OffsetTimes(Sequence[int]):
    """Translate integer epochs on access without copying a whole trace."""

    def __init__(self, times: tuple[int, ...], offset: int) -> None:
        self.times = times
        self.offset = offset

    def __len__(self) -> int:
        return len(self.times)

    @overload
    def __getitem__(self, index: int) -> int: ...

    @overload
    def __getitem__(self, index: slice) -> tuple[int, ...]: ...

    def __getitem__(self, index: int | slice) -> int | tuple[int, ...]:
        if isinstance(index, slice):
            return tuple(self.times[i] + self.offset for i in range(*index.indices(len(self))))
        return self.times[index] + self.offset


class _PointSpans(Sequence[_Span]):
    """Materialize only queried point-power brackets, including cold calls."""

    def __init__(self, times: Sequence[int], values: tuple[float, ...]) -> None:
        self.times = times
        self.values = values

    def __len__(self) -> int:
        return max(0, len(self.times) - 1)

    @overload
    def __getitem__(self, index: int) -> _Span: ...

    @overload
    def __getitem__(self, index: slice) -> tuple[_Span, ...]: ...

    def __getitem__(self, index: int | slice) -> _Span | tuple[_Span, ...]:
        if isinstance(index, slice):
            return tuple(self[i] for i in range(*index.indices(len(self))))
        if index < 0:
            index += len(self)
        if not 0 <= index < len(self):
            raise IndexError(index)
        return _Span(self.times[index], self.times[index + 1],
                     self.values[index], self.values[index + 1])


def _flags(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))


class _Trace:
    """Lane-local, reusable reconstruction; prepare once for a whole episode."""

    def __init__(self, trace: PowerTrace, mapping: ClockMapping | None) -> None:
        self.trace = trace
        self.mapping = mapping
        self.flags: list[str] = []
        self.counter = trace.unit == "J_cumulative"
        self.method = "counter_J" if self.counter else "trapezoid_W"
        offset = mapping.offset_ns if mapping is not None else 0
        if mapping is None:
            self.flags.append("clock.uncertainty_missing")
        elif mapping.trace_domain != trace.clock_domain:
            self.flags.append("clock.domain_mismatch")
        if trace.resolution is None:
            self.flags.append("resolution.missing")
        elif not math.isfinite(trace.resolution) or trace.resolution < 0:
            self.flags.append("resolution.invalid")
        window = trace.averaging_window_ns
        if window is not None and window <= 0:
            self.flags.append("window.invalid")
            window = None
        self.window = window
        self.times: Sequence[int]
        if not self.counter and window is None and all(map(math.isfinite, trace.values)):
            # Retain global nonfinite-sample semantics, but avoid allocating
            # O(n) pairs, translated epochs and spans for a short point query.
            self.times = trace.t_ns if offset == 0 else _OffsetTimes(trace.t_ns, offset)
            self.values = trace.values
            pairs = []
        else:
            pairs = [(t + offset, v) for t, v in zip(trace.t_ns, trace.values)
                     if math.isfinite(v)]
            if len(pairs) != len(trace.t_ns):
                self.flags.append("trace.nonfinite_samples")
            self.times = tuple(t for t, _ in pairs)
            self.values = tuple(v for _, v in pairs)
        spans: list[_Span] = []
        self.resets: list[tuple[int, int, str]] = []
        self.counter_peak_missing = False
        if self.counter:
            # A restart reading can contain at most one poll's work:
            # new_J <= poll_s * peak_W from nondecreasing counter steps.
            # Establish that peak BEFORE classifying drops so an implausible
            # megajoule reading cannot certify itself as a restart.
            observed_peak = max(((y - x) / ((b - a) / _NS_PER_S)
                                 for (a, x), (b, y) in zip(pairs, pairs[1:])
                                 if y >= x), default=None)
            self.counter_peak_missing = observed_peak is None and len(pairs) > 1
            if self.counter_peak_missing:
                self.flags.append("counter.peak_missing")
            for (a, x), (b, y) in zip(pairs, pairs[1:]):
                increment = y - x
                if y < x:
                    if observed_peak is None or y < 0 or y > (b - a) / _NS_PER_S * observed_peak:
                        # No physical restart can produce this new reading
                        # at the observed peak. Count no work for the glitch,
                        # but retain one poll's sensitivity below. With no
                        # non-reset step, that missing sensitivity is infinite.
                        increment = 0.0
                        self.flags.append("counter.decrease")
                        self.resets.append((a, b, "counter.decrease_interval"))
                    else:
                        increment = y
                        self.flags.extend(("counter.wrap", "counter.reset"))
                        self.resets.append((a, b, "counter.reset_interval"))
                watts = increment / ((b - a) / _NS_PER_S)
                spans.append(_Span(a, b, watts, watts))
        elif window is not None:
            self.method = "window_average_W"
            for i, (t, value) in enumerate(pairs):
                start = t - window
                if i:
                    previous_t, previous_value = pairs[i - 1]
                    if start > previous_t:
                        spans.append(_Span(previous_t, start, previous_value, value, True))
                    elif start < previous_t:
                        # Earlier-ending windows own shared support; flag this
                        # unsupported sensor shape rather than double counting.
                        self.flags.append("window.overlap")
                    start = max(start, previous_t)
                spans.append(_Span(start, t, value, value))
        if trace.duty_fraction is not None and trace.duty_fraction < 1 and window is None:
            self.flags.append("duty.window_missing")
        self.spans: Sequence[_Span]
        self.starts: Sequence[int]
        if not self.counter and window is None:
            self.spans = _PointSpans(self.times, self.values)
            # The final sample has no following span. Sequence slicing clips
            # that harmless extra knot when a query reaches/passes coverage.
            self.starts = self.times
        else:
            self.spans = tuple(spans)
            self.starts = tuple(span.start for span in spans)
        # Interior W queries do not need the whole-trace peak. Compute it
        # lazily only for missing coverage, retaining the same exact maximum.
        self._peak = (max((max(abs(span.left), abs(span.right)) for span in spans),
                          default=0.0) if self.counter else None)
        if not self.spans:
            self.flags.extend(("trace.insufficient_samples", "interpolation.missing"))

    @property
    def peak(self) -> float:
        if self._peak is None:
            self._peak = max((abs(v) for v in self.values), default=0.0)
        return self._peak

    def _adjacent_peak(self, t: int) -> float:
        if self.counter:
            i = bisect_right(self.starts, t) - 1
            i = max(0, min(i, len(self.spans) - 1))
            if not self.spans:
                return 0.0
            adjacent = [self.spans[i]]
            if t == self.spans[i].start and i:
                adjacent.append(self.spans[i - 1])
            return max(max(abs(s.left), abs(s.right)) for s in adjacent)
        i = bisect_left(self.times, t)
        # At a knot both touching intervals matter; elsewhere use the bracket.
        lo = max(0, i - 1)
        hi = min(len(self.times), i + (2 if i < len(self.times) and self.times[i] == t else 1))
        return max((abs(v) for v in self.values[lo:hi]), default=0.0)

    def _interpolation(self, t: int, t0: int, t1: int, *, start: bool) -> float:
        if not self.spans:
            return 0.0
        if self.window is not None and not self.counter:
            # "Partial sample interval" refers to the timestamp bracket.
            # A constant window reconstruction can still straddle a true edge.
            i = bisect_right(self.times, t) - 1
            if i < 0 or i + 1 >= len(self.times):
                return 0.0
            span = _Span(self.times[i], self.times[i + 1],
                         self.values[i], self.values[i + 1])
        else:
            i = bisect_right(self.starts, t) - 1
            if i < 0 or i >= len(self.spans):
                return 0.0
            span = self.spans[i]
        if not span.start < t < span.end:
            return 0.0
        a, b = (t, min(t1, span.end)) if start else (max(t0, span.start), t)
        linear = span.integral(a, b)
        if self.counter:
            # A left-held cumulative reading jumps by the full increment at
            # the right sample. Include that jump when the partial interval
            # reaches it; otherwise the held counter contributes no increment.
            held = span.integral(span.start, span.end) if b == span.end else 0.0
        else:
            held = span.left * ((b - a) / _NS_PER_S)
        # C1: use the full hold-versus-line difference. With at most one
        # step dP at fraction u of a partial interval L, the point-sensor
        # error is (1-u)*dP*L/2, bounded by (1+u)*dP*L/2 here.
        # A counter's full held jump likewise bounds its linear allocation;
        # halving the difference only bounds the point error for u >= 1/3.
        return abs(linear - held)

    def _window_uncertainty(self, t0: int, t1: int) -> float:
        if self.counter or self.window is None:
            return 0.0
        terms = []
        k0 = max(1, bisect_left(self.times, t0))
        for k in range(k0, len(self.times)):
            if self.times[k - 1] >= t1:
                break
            a, b = self.times[k - 1], self.times[k] - self.window
            overlap = max(0, min(t1, b) - max(t0, a))
            if overlap:
                # C2(a), assuming at most one step per duty gap: a step
                # dP versus its linear fill differs by at most the triangle
                # |dP|*L/2 on the gap length L inside this query.
                terms.append(abs(self.values[k] - self.values[k - 1])
                             * (overlap / _NS_PER_S) / 2)
        for t in (t0, t1):
            k = bisect_left(self.times, t)
            if k < len(self.times) and self.times[k] - self.window < t < self.times[k]:
                neighbours = self.values[max(0, k - 1):k + 2]
                # C2(b), assuming at most one step per window: allocating
                # a trailing mean across a cut errs by dP*w*u*(1-u).
                # Its maximum is |dP|*w/4 at the midpoint. Use the range
                # of adjacent means as the observed step sensitivity;
                # an unseen burst or an unobserved larger step is unbounded.
                terms.append((max(neighbours) - min(neighbours))
                             * (self.window / _NS_PER_S) / 4)
        return math.fsum(terms)

    def energy(self, t0: int, t1: int, idle_watts: float) -> EnergyEstimate:
        flags = list(self.flags)
        if t1 < t0:
            return EnergyEstimate(0.0, math.inf, self.method, _flags(flags + ["interval.reversed"]))
        if not math.isfinite(idle_watts):
            return EnergyEstimate(math.nan, math.inf, self.method, _flags(flags + ["idle.nonfinite"]))
        if t1 == t0:
            # Identical integration limits contain neither energy nor support
            # on which any endpoint, resolution or coverage term can act.
            return EnergyEstimate(0.0, 0.0, self.method, _flags(flags))
        if not self.spans:
            # No observed gross energy exists from which to subtract idle.
            # Infinity prevents an empty sensor from claiming precision.
            return EnergyEstimate(0.0, math.inf, self.method,
                                  _flags(flags + ["trace.partial_coverage",
                                                  "coverage.peak_missing"]))
        duration = (t1 - t0) / _NS_PER_S
        energies: list[float] = []
        uncovered_ns = 0
        covered_ns = 0
        if self.spans:
            lo = max(0, bisect_right(self.starts, t0) - 1)
            hi = bisect_left(self.starts, t1)
            for span in self.spans[lo:hi]:
                a, b = max(t0, span.start), min(t1, span.end)
                if b > a:
                    energies.append(span.integral(a, b))
                    covered_ns += b - a
                    if span.uncovered:
                        uncovered_ns += b - a
        missing_ns = (t1 - t0) - covered_ns
        bounds: list[float] = []
        if missing_ns:
            flags.append("trace.partial_coverage")
            bounds.append(math.inf if self.counter_peak_missing else
                          missing_ns / _NS_PER_S * self.peak)
            if not self.values or self.counter_peak_missing:
                flags.append("coverage.peak_missing")
        if self.mapping is not None:
            uncertainty = self.mapping.uncertainty_ns
            if uncertainty < 0:
                flags.append("clock.uncertainty_invalid")
            else:
                bounds.append((self._adjacent_peak(t0) + self._adjacent_peak(t1))
                              * uncertainty / _NS_PER_S)
        bounds.extend((self._interpolation(t0, t0, t1, start=True),
                       self._interpolation(t1, t0, t1, start=False),
                       self._window_uncertainty(t0, t1)))
        for a, b, interval_flag in self.resets:
            reset_overlap = max(0, min(t1, b) - max(t0, a))
            if reset_overlap:
                # A reset or ignored dip can hide one poll's work. Its
                # overlap duration * observed peak is the sensitivity, as
                # for partial coverage; unseen larger spikes are unbounded.
                bounds.append(math.inf if self.counter_peak_missing else
                              reset_overlap / _NS_PER_S * self.peak)
                flags.append(interval_flag)
        resolution = self.trace.resolution
        if resolution is not None and math.isfinite(resolution) and resolution >= 0:
            bounds.append(2 * resolution if self.counter else resolution * duration)
        method = self.method
        if self.window is not None:
            # C2 is a one-step sensitivity, not a bound on arbitrary work
            # hidden inside a window or unobserved duty gap.
            for t in (t0, t1):
                i = bisect_right(self.starts, t) - 1
                if i >= 0 and self.spans[i].start < t < self.spans[i].end:
                    flags.append("window.edge_allocation_unresolved")
                    break
        if uncovered_ns:
            flags.append("duty.uncovered")
            method += ";duty.uncovered_fraction=" + repr(uncovered_ns / (t1 - t0))
        energy = math.fsum(energies) - idle_watts * duration
        if energy < 0:
            flags.append("energy.negative")
        return EnergyEstimate(energy, math.fsum(bounds), method, _flags(flags))


# A single active immutable trace is retained for repeated public queries.
# Identity avoids hashing millions of tuple entries. Replacing the active
# trace releases its preparation; this cache cannot grow with episode count.
_last_reconstruction: _Trace | None = None


def trace_energy(
    trace: PowerTrace, t0_ns: int, t1_ns: int, *,
    mapping: ClockMapping | None = None, idle_watts: float = 0.0,
) -> EnergyEstimate:
    """Integrate exactly the selected reconstruction, retaining quality flags.

    Idle power is subtracted over the FULL requested interval, including any
    out-of-trace duration, as specified by A4. Missing gross energy is zero
    with a peak-power sensitivity allowance. A physically plausible counter
    restart counts from zero with counter.wrap/counter.reset. An implausible
    drop counts zero with counter.decrease. Both add the affected poll's
    observed-peak sensitivity; if no non-reset step sets a peak, it is infinite.

    Endpoint hold-versus-line comparisons are clipped to the query itself.
    Windowed sensors compare raw sample brackets and add the C2 duty-gap
    and within-window allocation sensitivities under a one-step assumption.
    window.edge_allocation_unresolved retains the warning that arbitrary
    unsampled work is unbounded. A held counter jumps
    at the right sample; that jump counts when the partial interval reaches it.
    Empty reconstructions return zero energy with infinite uncertainty.
    Point spans are built only for requested support. The most recent trace
    and mapping preparation is cached for repeated interval queries.
    """
    global _last_reconstruction
    reconstruction = _last_reconstruction
    if reconstruction is None or reconstruction.trace is not trace or reconstruction.mapping != mapping:
        reconstruction = _Trace(trace, mapping)
        _last_reconstruction = reconstruction
    return reconstruction.energy(t0_ns, t1_ns, idle_watts)


def _segments(episode: Episode, flags: list[str]) -> list[tuple[int | None, str, int, int]]:
    # Construct model/gap support first, then overlay every recorded tool.
    # Runner tools execute after their model call; ownership is not containment.
    parts: list[tuple[int | None, str, int, int, int | None]] = []
    cursor = episode.start_ns
    turns = sorted(episode.turns, key=lambda turn: (turn.start_ns, turn.index))
    if tuple(turns) != episode.turns:
        flags.append("turn.out_of_order")
    for turn in turns:
        start, end = max(cursor, turn.start_ns), turn.end_ns
        if turn.start_ns < cursor:
            flags.append("turn.overlap")
        if start > cursor:
            parts.append((None, "gap", cursor, start, None))
            cursor = start
        if end <= start:
            continue
        first = turn.first_token_ns
        if first is None:
            flags.append("turn.no_first_token")
        elif start < min(end, first):
            parts.append((turn.index, "prefill", start, min(end, first), None))
            start = min(end, first)
        if start < end:
            parts.append((turn.index, "decode", start, end, None))
        cursor = end
    if cursor < episode.end_ns:
        parts.append((None, "gap", cursor, episode.end_ns, None))

    calls = sorted(((call.start_ns, call.end_ns, turn.index, position, turn, call)
                    for turn in turns for position, call in enumerate(turn.tool_calls)),
                   key=lambda item: item[:4])
    tools = []
    previous_end = episode.start_ns
    for identity, (_, _, _, _, turn, call) in enumerate(calls):
        a = max(episode.start_ns, call.start_ns)
        b = min(episode.end_ns, call.end_ns)
        if call.start_ns < episode.start_ns or call.end_ns > episode.end_ns:
            flags.append("tool.outside_episode")
        if b <= a:
            continue
        if a < previous_end:
            flags.append("tool.overlap")
        a = max(a, previous_end)
        if b <= a:
            continue
        if turn.first_token_ns is not None and a < turn.first_token_ns:
            flags.append("tool.prefill_overlap")
        tools.append((turn.index, "tool", a, b, identity))
        previous_end = b

    for owner, kind, a, b, identity in tools:
        overlaid = []
        for turn, phase, start, end, call_id in parts:
            if end <= a or start >= b:
                overlaid.append((turn, phase, start, end, call_id))
                continue
            if start < a:
                overlaid.append((turn, phase, start, a, call_id))
            overlaid.append((owner, kind, max(start, a), min(end, b), identity))
            if end > b:
                overlaid.append((turn, phase, b, end, call_id))
        parts = overlaid

    # Coalesce tools crossing model/gap boundaries, retaining distinct calls
    # even when two calls from the same turn are back-to-back.
    merged: list[tuple[int | None, str, int, int, int | None]] = []
    for turn, kind, start, end, identity in parts:
        if (merged and merged[-1][0:2] == (turn, kind)
                and merged[-1][3] == start and merged[-1][4] == identity):
            previous = merged[-1]
            merged[-1] = (turn, kind, previous[2], end, identity)
        else:
            merged.append((turn, kind, start, end, identity))
    return [(turn, kind, start, end) for turn, kind, start, end, _ in merged]


def attribute_episode(
    episode: Episode, *, source: str, channel: str, idle_watts: float = 0.0,
) -> EpisodeAttribution:
    """Tile an episode, then attribute one selected sensor channel.

    All recorded turns and tools count, including logged=False tamper evidence.
    Missing or ambiguous trace/mapping selection is flagged. For malformed
    overlapping turns/calls, earlier-starting intervals own shared time, with
    tools taking precedence over model phases; no time is counted twice.
    """
    flags = list(episode.flags)
    traces = [trace for trace in episode.power_traces
              if trace.source == source and trace.channel == channel]
    if not traces:
        flags.append("trace.missing")
        trace = PowerTrace(source="mock", channel=channel, clock_domain=episode.clock_domain,
                           t_ns=(), values=(), unit="W", nominal_interval_ns=0)
    else:
        trace = traces[0]
        if len(traces) > 1:
            flags.append("trace.ambiguous")
    mapping = None
    if trace.clock_domain != episode.clock_domain:
        mappings = [m for m in episode.clock_mappings
                    if m.trace_domain == trace.clock_domain and m.episode_domain == episode.clock_domain]
        if mappings:
            mapping = mappings[0]
            if len(mappings) > 1:
                flags.append("clock.mapping_ambiguous")
        else:
            loose = [m for m in episode.clock_mappings if m.trace_domain == trace.clock_domain]
            if loose:
                mapping = loose[0]
                flags.append("clock.episode_domain_mismatch")
                if len(loose) > 1:
                    flags.append("clock.mapping_ambiguous")
            else:
                flags.append("clock.mapping_missing")
    reconstruction = _Trace(trace, mapping)

    def estimate(start: int, end: int) -> EnergyEstimate:
        energy = reconstruction.energy(start, end, idle_watts)
        if not traces:
            return EnergyEstimate(0.0, math.inf, energy.method,
                                  _flags(list(energy.flags) + ["trace.missing"]))
        return energy

    total = estimate(episode.start_ns, episode.end_ns)
    segments = tuple(SegmentEnergy(turn, kind, start, end, estimate(start, end))
                     for turn, kind, start, end in _segments(episode, flags))
    flags.extend(total.flags)
    for segment in segments:
        flags.extend(segment.energy.flags)
    return EpisodeAttribution(episode.episode_id, channel, total, segments, _flags(flags))


__all__ = ["EnergyEstimate", "SegmentEnergy", "EpisodeAttribution", "trace_energy", "attribute_episode"]
