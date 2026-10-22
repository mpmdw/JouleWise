"""Independent reference twin of lane A4's attribution functions (docs/align/PIPELINE.md).

Lane A4 builds ``joulewise/align/attribution.py``: energy per turn, phase and
tool call from a ``PowerTrace`` and an ``Episode``'s timestamps. This module is
a second implementation of its number-producing functions, written from the
lane brief alone (the "Public API" and "Semantics" of
``night-archive/forward-20261021/align/briefs/attribution.md``) without reading
the lane's own code. Both are run on the same inputs; a disagreement points at
a defect in one of them, or at a sentence of the brief the two read
differently (listed below under READINGS).

It is written for transparency, not speed: every quantity is a direct formula
evaluated one sample interval at a time. Times stay integer nanoseconds, and a
duration becomes seconds only where watts multiply it (W x s = J). Stdlib only.

Brief sentences are quoted in each docstring as "BRIEF: ...".

READINGS (where the brief leaves a choice open, the most literal reading is taken)

R1  Method. ``unit == "J_cumulative"`` -> "counter_J" (any averaging window is
    ignored). ``unit == "W"`` with ``averaging_window_ns`` None or <= 0 ->
    "trapezoid_W" (a zero-length window averages nothing). ``unit == "W"`` with a
    positive window -> "window_average_W". ``PowerTrace.duty_fraction`` is not
    read: which time is covered follows from the window and the actual sample
    times.

R2  Coverage (the span the trace says anything about, in the episode domain):
    trapezoid_W and counter_J: [first sample, last sample]; window_average_W:
    [first sample - w, last sample], since the first sample averages
    [t_0 - w, t_0]. Nothing is extrapolated outside it.

R3  Overlapping windows (w longer than the spacing to the previous sample):
    sample k is held over (max(t_{k-1}, t_k - w), t_k]; each instant takes the
    earliest-ending window that contains it, so no instant is counted twice.

R4  Uncovered fill: on the gap (t_{k-1}, t_k - w) power is the straight line
    from P_{k-1} at t_{k-1} (where window k-1 ends) to P_k at t_k - w (where
    window k starts), so the reconstruction is continuous at the gap edges.

R5  duty.uncovered format: the flag is "duty.uncovered" and the method string is
    "window_average_W;duty.uncovered=<f>", where <f> is ``repr`` of the float
    (uncovered ns inside the integrated interval) / (integrated interval ns).
    Written only when f > 0; ``split_method`` parses it.

R6  Partial coverage. "The estimate covers only the overlap" governs every term
    of the estimate: the gross energy, the idle subtraction (idle_watts x
    overlap seconds, not x (t1 - t0); the two agree whenever coverage is full),
    and the interpolation, clock and resolution terms. The uncovered part enters
    only as (uncovered seconds) x (trace peak power). Trace peak power is
    max |sample| in W over the whole trace, idle not subtracted; for a counter,
    max |step energy / step duration| over the whole trace. The flag
    "trace.partial_coverage" is set when t0 < coverage start or t1 > coverage end.

R7  Clock term. The ends are the two ends of the integrated interval (the
    overlap). "The samples adjacent to an end" are the samples bounding every
    sample interval [t_k, t_{k+1}] that contains the end (closed): an end strictly
    inside one interval gives {k, k+1}; an end on sample k gives {k-1, k, k+1};
    an end outside every interval (before the first sample, inside the first
    window) gives the nearest sample. For a counter the power "at" those samples
    is |step energy / step duration| of each step touching the end. Term =
    peak x uncertainty_ns x 1e-9 s/ns, at each end. ``mapping is None`` means the
    uncertainty is unknown, so the term is missing: 0 plus the flag
    "half_width.missing.clock".

R8  Interpolation term. "Sample-and-hold" is the zero-order hold forward
    (sample k's value held on [t_k, t_{k+1})); "linear" is the straight line
    between samples k and k+1. Both are applied to the raw samples for every
    method (window means for window_average_W, cumulative joules for counter_J).
    The partial sample interval at the start end a is [a, min(b, t_{k+1})] when
    t_k < a < t_{k+1}; at the stop end b it is [max(a, t_j), b] when
    t_j < b < t_{j+1}. An end on a sample, or outside every sample interval, has
    no partial interval and contributes 0 (no flag: nothing is missing). When
    both ends fall inside the same sample interval each end counts its own
    (identical) partial interval, so that interval counts twice.

R9  Resolution term: W: resolution x overlap seconds; counter: 2 x resolution.
    ``resolution is None`` -> 0 plus "half_width.missing.resolution". When the
    overlap has zero length no reading is used and every overlap term
    (energy, idle, interpolation, clock, resolution) is 0.

R10 Counter wrap. The brief gives no modulus, so a decrease between consecutive
    cumulative samples is read as the counter restarting from zero (the
    Prometheus ``increase`` convention): that step's energy is the later
    sample's value. Flag "counter.wrap"; no half-width term is added (the brief
    names none).

R11 Degenerate traces. Zero samples -> joules 0.0 and flag "trace.empty". The
    coverage term needs a peak power; when there is none (no samples, or a
    counter with fewer than two) and some duration is uncovered, the term is
    missing: 0 plus "half_width.missing.coverage".

R12 Segmentation (attribute_episode). Tool calls take precedence everywhere: the
    brief subtracts them from decode, and since the segments must tile with no
    overlap the same subtraction applies to prefill and to gaps (in production
    tool calls run between model calls, i.e. inside gaps). A tool segment's
    ``turn`` is the index of the Turn record that holds the call, wherever the
    call lies. Calls are clipped to the episode ("tool.outside_episode").
    Overlapping calls: the one starting first owns the overlap (ties: lower turn
    index, then earlier in the turn's tuple) and "tool.overlap" is flagged.
    Overlapping turns: the lower index owns the overlap ("turn.overlap").
    Touching pieces with the same kind, turn and call merge; a decode split by a
    tool gives two decode segments; zero-duration pieces give no segment
    (a zero-length tool call therefore has no segment). Unlogged turns and tool
    calls are included: power sees them.

R13 Trace selection: the first trace with ``source == source`` and
    ``channel == channel`` ("trace.ambiguous" when more than one matches). When
    none matches, every segment and the total carry
    EnergyEstimate(0.0, 0.0, "none", ("trace.missing",)) and the attribution
    carries "trace.missing": a flag, never a refusal.

R14 Mapping: a trace in the episode's own clock domain gets ``mapping=None``.
    Otherwise the first ClockMapping with ``trace_domain`` equal to the trace's
    domain and ``episode_domain`` equal to the episode's; if only a
    ``trace_domain`` match exists it is used and "clock.mapping_domain_mismatch"
    is flagged (``trace_energy`` flags the same when handed a mapping whose
    ``trace_domain`` differs from the trace's).

R15 Flags. ``EpisodeAttribution.flags`` holds attribution-level conditions only
    (turn.no_first_token, trace.*, tool.*, turn.overlap, clock.*), each once, in
    order of first occurrence; per-interval conditions stay in each
    ``EnergyEstimate.flags``. Flag order carries no meaning: compare as sets.

R16 ``trace_energy`` with t1 < t0 raises ValueError: a caller error, not a
    measured condition.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass

from joulewise.align.records import ClockMapping, Episode, PowerTrace

NS_PER_S = 1_000_000_000

METHOD_TRAPEZOID = "trapezoid_W"
METHOD_WINDOW = "window_average_W"
METHOD_COUNTER = "counter_J"
METHOD_NONE = "none"  # R13: no trace matched

FLAG_DUTY_UNCOVERED = "duty.uncovered"
FLAG_PARTIAL = "trace.partial_coverage"
FLAG_EMPTY = "trace.empty"
FLAG_MISSING_TRACE = "trace.missing"
FLAG_AMBIGUOUS_TRACE = "trace.ambiguous"
FLAG_WRAP = "counter.wrap"
FLAG_MISSING_CLOCK = "half_width.missing.clock"
FLAG_MISSING_RESOLUTION = "half_width.missing.resolution"
FLAG_MISSING_COVERAGE = "half_width.missing.coverage"
FLAG_MAPPING_MISMATCH = "clock.mapping_domain_mismatch"
FLAG_NO_FIRST_TOKEN = "turn.no_first_token"
FLAG_TOOL_OUTSIDE = "tool.outside_episode"
FLAG_TOOL_OVERLAP = "tool.overlap"
FLAG_TURN_OVERLAP = "turn.overlap"


# ---------------------------------------------------------------- public records

@dataclass(frozen=True)
class EnergyEstimate:
    """BRIEF: ``joules: float; half_width_j: float; method: str  # "trapezoid_W",
    "window_average_W", "counter_J"; flags: tuple[str, ...]``."""

    joules: float
    half_width_j: float
    method: str
    flags: tuple[str, ...]


@dataclass(frozen=True)
class SegmentEnergy:
    """BRIEF: ``turn: int | None  # None for gaps between turns; kind: str  # "prefill",
    "decode", "tool", "gap"; start_ns: int; end_ns: int; energy: EnergyEstimate``."""

    turn: int | None
    kind: str
    start_ns: int
    end_ns: int
    energy: EnergyEstimate


@dataclass(frozen=True)
class EpisodeAttribution:
    """BRIEF: ``episode_id: str; channel: str; total: EnergyEstimate;
    segments: tuple[SegmentEnergy, ...]; flags: tuple[str, ...]``."""

    episode_id: str
    channel: str
    total: EnergyEstimate
    segments: tuple[SegmentEnergy, ...]
    flags: tuple[str, ...]


def split_method(method: str) -> tuple[str, dict[str, float]]:
    """Split a method string into its base method and companion fields (R5).

    ``"window_average_W;duty.uncovered=0.75"`` -> ``("window_average_W",
    {"duty.uncovered": 0.75})``.
    """
    base, *fields = method.split(";")
    companions: dict[str, float] = {}
    for item in fields:
        name, value = item.split("=", 1)
        companions[name] = float(value)
    return base, companions


# ---------------------------------------------------------------- small helpers

def _seconds(ns: int) -> float:
    """Integer nanoseconds to float seconds (one correctly rounded division)."""
    return ns / NS_PER_S


def _lerp(x0: int, y0: float, x1: int, y1: float, x: int) -> float:
    """Value at x of the straight line through (x0, y0) and (x1, y1); requires x0 < x1."""
    return y0 + (y1 - y0) * ((x - x0) / (x1 - x0))


def _add(flags: list[str], name: str) -> None:
    if name not in flags:
        flags.append(name)


def _method_of(trace: PowerTrace) -> str:
    """R1."""
    if trace.unit == "J_cumulative":
        return METHOD_COUNTER
    if trace.averaging_window_ns is None or trace.averaging_window_ns <= 0:
        return METHOD_TRAPEZOID
    return METHOD_WINDOW


def _unwrapped(values: tuple[float, ...]) -> tuple[list[float], bool]:
    """R10: cumulative series with every decrease read as a restart from zero.

    U_k = value_k + offset_k, where offset_k grows by value_{k-1} at each
    decrease, so the step over a decrease adds value_k (the counter restarted
    from 0) and every other step adds value_k - value_{k-1} exactly as recorded.
    """
    unwrapped: list[float] = []
    offset = 0.0
    wrapped = False
    for k, value in enumerate(values):
        if k > 0 and value < values[k - 1]:
            offset += values[k - 1]
            wrapped = True
        unwrapped.append(float(value) + offset)
    return unwrapped, wrapped


# ---------------------------------------------------------------- reconstructions

def _trapezoid_joules(times: tuple[int, ...], watts: tuple[float, ...], a: int, b: int) -> float:
    """BRIEF: "piecewise-linear power between samples, integrated exactly over [t0, t1]
    (the interval ends are interpolated, not snapped to samples)".

    For times[0] <= a <= b <= times[-1]: the sum over sample intervals of the
    trapezoid of the straight line on that interval's part inside [a, b].
    """
    joules = 0.0
    first = max(0, bisect_right(times, a) - 1)
    for k in range(first, len(times) - 1):
        if times[k] >= b:
            break
        lo = max(a, times[k])
        hi = min(b, times[k + 1])
        if hi <= lo:
            continue
        p_lo = _lerp(times[k], watts[k], times[k + 1], watts[k + 1], lo)
        p_hi = _lerp(times[k], watts[k], times[k + 1], watts[k + 1], hi)
        joules += 0.5 * (p_lo + p_hi) * _seconds(hi - lo)
    return joules


def _window_pieces(times: tuple[int, ...], watts: tuple[float, ...], w: int,
                   k: int) -> list[tuple[int, int, float, float, bool]]:
    """The reconstruction on sample k's stretch (t_{k-1}, t_k], as linear pieces.

    BRIEF: "the sample at t is the mean power over [t - w, t]; treat each sample
    as a constant over its own window ... parts not covered by any window ...
    are filled by linear interpolation between neighbouring window means".
    Each piece is (start, end, watts at start, watts at end, covered). R3, R4.
    """
    if k == 0:
        return [(times[0] - w, times[0], watts[0], watts[0], True)]
    held_from = max(times[k] - w, times[k - 1])
    pieces: list[tuple[int, int, float, float, bool]] = []
    if held_from > times[k - 1]:
        pieces.append((times[k - 1], held_from, watts[k - 1], watts[k], False))
    pieces.append((held_from, times[k], watts[k], watts[k], True))
    return pieces


def _window_joules(times: tuple[int, ...], watts: tuple[float, ...], w: int,
                   a: int, b: int) -> tuple[float, int]:
    """BRIEF: "integrate the covered part of [t0, t1]" plus the linear fill of the rest.

    For times[0] - w <= a <= b <= times[-1]. Returns (joules, uncovered ns
    inside [a, b]).
    """
    joules = 0.0
    uncovered_ns = 0
    k_first = bisect_left(times, a)  # first sample at or after a: its stretch holds a
    k_last = min(len(times) - 1, bisect_left(times, b))  # its stretch holds b
    for k in range(k_first, k_last + 1):
        for start, end, p_start, p_end, covered in _window_pieces(times, watts, w, k):
            lo = max(a, start)
            hi = min(b, end)
            if hi <= lo:
                continue
            p_lo = _lerp(start, p_start, end, p_end, lo)
            p_hi = _lerp(start, p_start, end, p_end, hi)
            joules += 0.5 * (p_lo + p_hi) * _seconds(hi - lo)
            if not covered:
                uncovered_ns += hi - lo
    return joules, uncovered_ns


def _counter_linear(times: tuple[int, ...], cumulative: list[float], x: int) -> float:
    """The cumulative counter at x, linearly interpolated between samples (times[0] <= x <= times[-1])."""
    k = bisect_right(times, x) - 1  # last sample at or before x
    if k >= len(times) - 1:
        return cumulative[-1]
    return _lerp(times[k], cumulative[k], times[k + 1], cumulative[k + 1], x)


def _counter_hold(times: tuple[int, ...], cumulative: tuple[float, ...] | list[float], x: int) -> float:
    """The cumulative counter at x under a forward sample-and-hold (R8)."""
    return cumulative[bisect_right(times, x) - 1]


# ---------------------------------------------------------------- half-width terms

def _interval_strictly_containing(times: tuple[int, ...], x: int) -> int | None:
    """k with times[k] < x < times[k+1], or None when x is on a sample or outside every interval."""
    k = bisect_right(times, x) - 1
    if k < 0 or k >= len(times) - 1 or times[k] == x:
        return None
    return k


def _interpolation_term(times: tuple[int, ...], series: tuple[float, ...] | list[float],
                        a: int, b: int, *, cumulative: bool) -> float:
    """BRIEF: "(ii) interpolation: at each end, half the absolute energy difference
    between the sample-and-hold and the linear reconstruction over the partial
    sample interval at that end". R8.
    """

    def hold_minus_linear(k: int, p: int, q: int) -> float:
        """Energy over [p, q] (inside sample interval k) under the hold minus under the line."""
        if cumulative:
            hold = _counter_hold(times, series, q) - _counter_hold(times, series, p)
            linear = (_lerp(times[k], series[k], times[k + 1], series[k + 1], q)
                      - _lerp(times[k], series[k], times[k + 1], series[k + 1], p))
        else:
            hold = series[k] * _seconds(q - p)
            p_p = _lerp(times[k], series[k], times[k + 1], series[k + 1], p)
            p_q = _lerp(times[k], series[k], times[k + 1], series[k + 1], q)
            linear = 0.5 * (p_p + p_q) * _seconds(q - p)
        return hold - linear

    term = 0.0
    k = _interval_strictly_containing(times, a)
    if k is not None:
        term += 0.5 * abs(hold_minus_linear(k, a, min(b, times[k + 1])))
    j = _interval_strictly_containing(times, b)
    if j is not None:
        term += 0.5 * abs(hold_minus_linear(j, max(a, times[j]), b))
    return term


def _intervals_touching(times: tuple[int, ...], e: int) -> list[int]:
    """Every k with times[k] <= e <= times[k+1] (R7)."""
    touching = []
    lo = max(0, bisect_left(times, e) - 1)
    hi = min(len(times) - 2, bisect_right(times, e))
    for k in range(lo, hi + 1):
        if times[k] <= e <= times[k + 1]:
            touching.append(k)
    return touching


def _peak_adjacent_watts(times: tuple[int, ...], values: tuple[float, ...],
                         cumulative: list[float] | None, e: int) -> float:
    """BRIEF: "peak |P| over the samples adjacent to each end". R7."""
    touching = _intervals_touching(times, e)
    if cumulative is None:
        if touching:
            indices = sorted({i for k in touching for i in (k, k + 1)})
        else:
            indices = [0 if e < times[0] else len(times) - 1]
        return max(abs(values[i]) for i in indices)
    if len(times) < 2:
        return 0.0
    if not touching:
        touching = [0 if e < times[0] else len(times) - 2]
    return max(abs(cumulative[k + 1] - cumulative[k]) / _seconds(times[k + 1] - times[k]) for k in touching)


def _trace_peak_watts(trace: PowerTrace, cumulative: list[float] | None) -> float | None:
    """R6: the whole trace's peak |power|; None when it has none (R11)."""
    if cumulative is None:
        if not trace.values:
            return None
        return max(abs(v) for v in trace.values)
    if len(trace.t_ns) < 2:
        return None
    return max(abs(cumulative[k + 1] - cumulative[k]) / _seconds(trace.t_ns[k + 1] - trace.t_ns[k])
               for k in range(len(trace.t_ns) - 1))


# ---------------------------------------------------------------- trace_energy

def trace_energy(trace: PowerTrace, t0_ns: int, t1_ns: int, *, mapping: ClockMapping | None = None,
                 idle_watts: float = 0.0) -> EnergyEstimate:
    """Energy drawn on one trace's channel over [t0_ns, t1_ns] of the episode's clock.

    BRIEF, times: "t0_ns, t1_ns are in the episode's clock domain; the trace's
    timestamps map into it by t + mapping.offset_ns (mapping None means the
    trace is already in the episode domain)." Equivalently, and exactly in
    integers, the interval maps into the trace's domain by t - offset_ns; the
    work below is done there.
    BRIEF, energy: trapezoid_W, window_average_W, counter_J as in the
    reconstruction helpers above; "J_cumulative: counter difference, linearly
    interpolated at both ends".
    BRIEF, idle: "idle_watts is subtracted as a constant power over [t0, t1]" (R6).
    BRIEF, half-width: "the sum of: (i) clock ... (ii) interpolation ... (iii)
    resolution ... A missing term contributes 0 and adds a flag naming it."
    BRIEF, coverage: "if [t0, t1] extends beyond the trace, the estimate covers
    only the overlap, is flagged trace.partial_coverage, and its half-width adds
    the uncovered duration times the trace's peak power."
    """
    if t1_ns < t0_ns:
        raise ValueError(f"trace_energy: t1_ns {t1_ns} before t0_ns {t0_ns}")
    flags: list[str] = []
    method = _method_of(trace)

    if mapping is None:
        offset_ns = 0
        _add(flags, FLAG_MISSING_CLOCK)
    else:
        offset_ns = mapping.offset_ns
        if mapping.trace_domain != trace.clock_domain:
            _add(flags, FLAG_MAPPING_MISMATCH)

    times = trace.t_ns
    values = trace.values
    a_req = t0_ns - offset_ns  # the requested interval in the trace's domain
    b_req = t1_ns - offset_ns
    window_ns = trace.averaging_window_ns if method == METHOD_WINDOW else None

    cumulative: list[float] | None = None
    if method == METHOD_COUNTER:
        cumulative, wrapped = _unwrapped(values)
        if wrapped:
            _add(flags, FLAG_WRAP)

    # Coverage and overlap (R2, R6).
    if not times:
        _add(flags, FLAG_EMPTY)
        covered_from = covered_to = None
        overlap_ns = 0
    else:
        covered_from = times[0] - window_ns if window_ns is not None else times[0]
        covered_to = times[-1]
        a = max(a_req, covered_from)
        b = min(b_req, covered_to)
        overlap_ns = max(0, b - a)
    uncovered_ns = (b_req - a_req) - overlap_ns
    if covered_from is None or a_req < covered_from or b_req > covered_to:
        _add(flags, FLAG_PARTIAL)

    gross_j = 0.0
    interpolation_j = 0.0
    clock_j = 0.0
    resolution_j = 0.0
    duty_uncovered_ns = 0
    if overlap_ns > 0:
        if method == METHOD_TRAPEZOID:
            gross_j = _trapezoid_joules(times, values, a, b)
        elif method == METHOD_WINDOW:
            gross_j, duty_uncovered_ns = _window_joules(times, values, window_ns, a, b)
        else:
            gross_j = _counter_linear(times, cumulative, b) - _counter_linear(times, cumulative, a)

        if method == METHOD_COUNTER:
            interpolation_j = _interpolation_term(times, cumulative, a, b, cumulative=True)
        else:
            interpolation_j = _interpolation_term(times, values, a, b, cumulative=False)

        if mapping is not None:
            uncertainty_s = _seconds(mapping.uncertainty_ns)
            clock_j = (_peak_adjacent_watts(times, values, cumulative, a) * uncertainty_s
                       + _peak_adjacent_watts(times, values, cumulative, b) * uncertainty_s)

        if trace.resolution is not None:
            if method == METHOD_COUNTER:
                resolution_j = 2.0 * trace.resolution
            else:
                resolution_j = trace.resolution * _seconds(overlap_ns)
    if trace.resolution is None:
        _add(flags, FLAG_MISSING_RESOLUTION)

    coverage_j = 0.0
    if uncovered_ns > 0:
        peak = _trace_peak_watts(trace, cumulative)
        if peak is None:
            _add(flags, FLAG_MISSING_COVERAGE)
        else:
            coverage_j = _seconds(uncovered_ns) * peak

    method_text = method
    if duty_uncovered_ns > 0:
        _add(flags, FLAG_DUTY_UNCOVERED)
        fraction = duty_uncovered_ns / overlap_ns
        method_text = f"{method};{FLAG_DUTY_UNCOVERED}={fraction!r}"

    joules = gross_j - idle_watts * _seconds(overlap_ns)
    half_width_j = interpolation_j + clock_j + resolution_j + coverage_j
    return EnergyEstimate(joules=joules, half_width_j=half_width_j, method=method_text, flags=tuple(flags))


# ---------------------------------------------------------------- attribute_episode

def _tile_episode(episode: Episode, flags: list[str]) -> list[tuple[str, int | None, int, int]]:
    """BRIEF: "segments per turn are prefill [start, first_token) when first_token_ns
    is known (else the whole turn is "decode" plus the flag turn.no_first_token),
    decode [first_token, end) minus the tool-call intervals inside the turn, each
    tool call as "tool", and the gaps between consecutive turns (and from the
    episode start to the first turn, and from the last turn to the episode end)
    as "gap". The segments tile [episode.start, episode.end] with no overlap".

    Done as elementary intervals: cut the episode at every turn start, end and
    first token and every (clipped) tool-call start and end; label each piece by
    precedence tool > turn (prefill/decode) > gap (R12); merge touching pieces
    with the same label. Returns (kind, turn, start_ns, end_ns) in time order.
    """
    e0, e1 = episode.start_ns, episode.end_ns

    calls: list[tuple[int, int, int, int]] = []  # (start, end, turn index, position in turn)
    for turn in episode.turns:
        if turn.first_token_ns is None:
            _add(flags, FLAG_NO_FIRST_TOKEN)
        for position, call in enumerate(turn.tool_calls):
            start = min(max(call.start_ns, e0), e1)
            end = min(max(call.end_ns, e0), e1)
            if (start, end) != (call.start_ns, call.end_ns):
                _add(flags, FLAG_TOOL_OUTSIDE)
            calls.append((start, end, turn.index, position))
    calls.sort(key=lambda c: (c[0], c[2], c[3]))

    cuts = {e0, e1}
    for turn in episode.turns:
        cuts.update((turn.start_ns, turn.end_ns))
        if turn.first_token_ns is not None:
            cuts.add(turn.first_token_ns)
    for start, end, _, _ in calls:
        cuts.update((start, end))
    ordered = sorted(cuts)

    tiles: list[list] = []  # [label, start, end]; label = (kind, turn, call identity)
    for x, y in zip(ordered, ordered[1:]):
        inside_calls = [c for c in calls if c[0] <= x and y <= c[1]]
        inside_turns = [t for t in episode.turns if t.start_ns <= x and y <= t.end_ns]
        if len(inside_calls) > 1:
            _add(flags, FLAG_TOOL_OVERLAP)
        if len(inside_turns) > 1:
            _add(flags, FLAG_TURN_OVERLAP)
        if inside_calls:
            owner = inside_calls[0]
            label = ("tool", owner[2], (owner[2], owner[3]))
        elif inside_turns:
            turn = inside_turns[0]
            if turn.first_token_ns is not None and y <= turn.first_token_ns:
                label = ("prefill", turn.index, None)
            else:
                label = ("decode", turn.index, None)
        else:
            label = ("gap", None, None)
        if tiles and tiles[-1][0] == label and tiles[-1][2] == x:
            tiles[-1][2] = y
        else:
            tiles.append([label, x, y])
    return [(label[0], label[1], start, end) for label, start, end in tiles]


def _mapping_for(episode: Episode, trace: PowerTrace, flags: list[str]) -> ClockMapping | None:
    """R14."""
    if trace.clock_domain == episode.clock_domain:
        return None
    exact = [m for m in episode.clock_mappings
             if m.trace_domain == trace.clock_domain and m.episode_domain == episode.clock_domain]
    if exact:
        return exact[0]
    loose = [m for m in episode.clock_mappings if m.trace_domain == trace.clock_domain]
    if loose:
        _add(flags, FLAG_MAPPING_MISMATCH)
        return loose[0]
    return None  # Episode validation makes this unreachable


def attribute_episode(episode: Episode, *, source: str, channel: str,
                      idle_watts: float = 0.0) -> EpisodeAttribution:
    """Energy of every prefill, decode, tool and gap segment of one episode, and the total.

    BRIEF: "attribute_episode(episode: Episode, *, source: str, channel: str,
    idle_watts: float = 0.0) -> EpisodeAttribution"; segmentation as in
    ``_tile_episode``; "their energies sum to the total within float
    accumulation error". Each segment and the total are ``trace_energy`` over
    their own interval of the selected trace (R13) with the episode's mapping
    for that trace (R14).
    """
    flags: list[str] = []
    matches = [t for t in episode.power_traces if t.source == source and t.channel == channel]
    trace = matches[0] if matches else None
    if len(matches) > 1:
        _add(flags, FLAG_AMBIGUOUS_TRACE)
    if trace is None:
        _add(flags, FLAG_MISSING_TRACE)
        mapping = None
    else:
        mapping = _mapping_for(episode, trace, flags)

    def estimate(start_ns: int, end_ns: int) -> EnergyEstimate:
        if trace is None:
            return EnergyEstimate(joules=0.0, half_width_j=0.0, method=METHOD_NONE, flags=(FLAG_MISSING_TRACE,))
        return trace_energy(trace, start_ns, end_ns, mapping=mapping, idle_watts=idle_watts)

    tiles = _tile_episode(episode, flags)
    segments = tuple(SegmentEnergy(turn=turn, kind=kind, start_ns=start, end_ns=end, energy=estimate(start, end))
                     for kind, turn, start, end in tiles)
    total = estimate(episode.start_ns, episode.end_ns)
    return EpisodeAttribution(episode_id=episode.episode_id, channel=channel, total=total,
                              segments=segments, flags=tuple(flags))


__all__ = ["EnergyEstimate", "SegmentEnergy", "EpisodeAttribution", "trace_energy", "attribute_episode",
           "split_method"]
