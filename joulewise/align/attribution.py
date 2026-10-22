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
from dataclasses import dataclass
import math

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
        pairs = [(t + offset, v) for t, v in zip(trace.t_ns, trace.values)
                 if math.isfinite(v)]
        if len(pairs) != len(trace.t_ns):
            self.flags.append("trace.nonfinite_samples")
        self.times = tuple(t for t, _ in pairs)
        self.values = tuple(v for _, v in pairs)
        spans: list[_Span] = []
        window = trace.averaging_window_ns
        if window is not None and window <= 0:
            self.flags.append("window.invalid")
            window = None
        if self.counter:
            for (a, x), (b, y) in zip(pairs, pairs[1:]):
                if y < x:
                    # No modulus/reset metadata exists: preserve the signed
                    # observed difference, never invent an unwrapping modulus.
                    self.flags.append("counter.wrap")
                watts = (y - x) / ((b - a) / _NS_PER_S)
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
        else:
            spans = [_Span(a, b, x, y) for (a, x), (b, y) in zip(pairs, pairs[1:])]
        if trace.duty_fraction is not None and trace.duty_fraction < 1 and window is None:
            self.flags.append("duty.window_missing")
        self.spans = tuple(spans)
        self.starts = tuple(span.start for span in spans)
        self.peak = max((max(abs(span.left), abs(span.right)) for span in spans), default=0.0)
        if not self.counter:
            self.peak = max(self.peak, max((abs(v) for v in self.values), default=0.0))
        if not spans:
            self.flags.extend(("trace.insufficient_samples", "interpolation.missing"))

    def _adjacent_peak(self, t: int) -> float:
        if self.counter:
            i = bisect_left(self.starts, t)
            adjacent = self.spans[max(0, i - 1):i + 1]
            return max((max(abs(s.left), abs(s.right)) for s in adjacent), default=0.0)
        i = bisect_left(self.times, t)
        # At a knot both touching intervals matter; elsewhere use the bracket.
        lo = max(0, i - 1)
        hi = min(len(self.times), i + (2 if i < len(self.times) and self.times[i] == t else 1))
        return max((abs(v) for v in self.values[lo:hi]), default=0.0)

    def _interpolation(self, t: int, *, start: bool) -> float:
        if not self.spans:
            return 0.0
        i = bisect_right(self.starts, t) - 1
        if i < 0 or i >= len(self.spans):
            return 0.0
        span = self.spans[i]
        if not span.start < t < span.end:
            return 0.0
        a, b = (t, span.end) if start else (span.start, t)
        if self.counter:
            # A held cumulative reading has no partial counter increment;
            # linear interpolation allocates this partial observed increment.
            return abs(span.integral(a, b)) / 2
        held = span.left * ((b - a) / _NS_PER_S)
        return abs(span.integral(a, b) - held) / 2

    def energy(self, t0: int, t1: int, idle_watts: float) -> EnergyEstimate:
        flags = list(self.flags)
        if t1 < t0:
            return EnergyEstimate(0.0, math.inf, self.method, _flags(flags + ["interval.reversed"]))
        if not math.isfinite(idle_watts):
            return EnergyEstimate(math.nan, math.inf, self.method, _flags(flags + ["idle.nonfinite"]))
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
            bounds.append(missing_ns / _NS_PER_S * self.peak)
            if not self.values:
                flags.append("coverage.peak_missing")
        if self.mapping is not None:
            uncertainty = self.mapping.uncertainty_ns
            if uncertainty < 0:
                flags.append("clock.uncertainty_invalid")
            else:
                bounds.append((self._adjacent_peak(t0) + self._adjacent_peak(t1))
                              * uncertainty / _NS_PER_S)
        bounds.extend((self._interpolation(t0, start=True),
                       self._interpolation(t1, start=False)))
        resolution = self.trace.resolution
        if resolution is not None and math.isfinite(resolution) and resolution >= 0:
            bounds.append(2 * resolution if self.counter else resolution * duration)
        method = self.method
        if uncovered_ns:
            flags.append("duty.uncovered")
            method += ";duty.uncovered_fraction=" + repr(uncovered_ns / (t1 - t0))
        energy = math.fsum(energies) - idle_watts * duration
        if energy < 0:
            flags.append("energy.negative")
        return EnergyEstimate(energy, math.fsum(bounds), method, _flags(flags))


def trace_energy(
    trace: PowerTrace, t0_ns: int, t1_ns: int, *,
    mapping: ClockMapping | None = None, idle_watts: float = 0.0,
) -> EnergyEstimate:
    """Integrate exactly the selected reconstruction, retaining quality flags.

    Idle power is subtracted over the FULL requested interval, including any
    out-of-trace duration, as specified by A4. Missing gross energy is zero
    with a peak-power sensitivity allowance. For counter wraps the observed
    signed difference is retained and flagged; no modulus is guessed.

    At a partially cut reconstruction span, interpolation uncertainty is half
    the energy difference from a left hold: [t0, span.end] at the start and
    [span.start, t1] at the end. Constant window support has zero such
    difference. A counter hold allocates zero increment on a partial span.
    """
    return _Trace(trace, mapping).energy(t0_ns, t1_ns, idle_watts)


def _segments(episode: Episode, flags: list[str]) -> list[tuple[int | None, str, int, int]]:
    parts: list[tuple[int | None, str, int, int]] = []
    cursor = episode.start_ns
    turns = sorted(episode.turns, key=lambda turn: (turn.start_ns, turn.index))
    if tuple(turns) != episode.turns:
        flags.append("turn.out_of_order")
    for turn in turns:
        start, end = max(cursor, turn.start_ns), turn.end_ns
        if turn.start_ns < cursor:
            flags.append("turn.overlap")
        if start > cursor:
            parts.append((None, "gap", cursor, start))
        if end <= start:
            continue
        first = turn.first_token_ns
        if first is None:
            flags.append("turn.no_first_token")

        def model_parts(a: int, b: int) -> None:
            if first is not None and a < min(b, first):
                parts.append((turn.index, "prefill", a, min(b, first)))
                a = min(b, first)
            if a < b:
                parts.append((turn.index, "decode", a, b))

        tool_cursor = start
        for call in sorted(turn.tool_calls, key=lambda call: (call.start_ns, call.end_ns)):
            a, b = max(start, call.start_ns), min(end, call.end_ns)
            if call.start_ns < start or call.end_ns > end:
                flags.append("tool.outside_turn")
            if b <= a:
                continue
            if a < tool_cursor:
                flags.append("tool.overlap")
            a = max(a, tool_cursor)
            if b <= a:
                continue
            if first is not None and a < first:
                flags.append("tool.prefill_overlap")
            model_parts(tool_cursor, a)
            parts.append((turn.index, "tool", a, b))
            tool_cursor = b
        model_parts(tool_cursor, end)
        cursor = end
    if cursor < episode.end_ns:
        parts.append((None, "gap", cursor, episode.end_ns))
    return parts


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
            flags.append("clock.mapping_missing")
    reconstruction = _Trace(trace, mapping)
    total = reconstruction.energy(episode.start_ns, episode.end_ns, idle_watts)
    segments = tuple(SegmentEnergy(turn, kind, start, end,
                                   reconstruction.energy(start, end, idle_watts))
                     for turn, kind, start, end in _segments(episode, flags))
    flags.extend(total.flags)
    for segment in segments:
        flags.extend(segment.energy.flags)
    return EpisodeAttribution(episode.episode_id, channel, total, segments, _flags(flags))


__all__ = ["EnergyEstimate", "SegmentEnergy", "EpisodeAttribution", "trace_energy", "attribute_episode"]
