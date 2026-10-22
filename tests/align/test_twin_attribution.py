"""Twin agreement for lane A4 (``joulewise/align/attribution.py``), review round 3 after fix round 2b.

Runs the lane's public functions and the independent twin
(``tests/align/twins/attribution_twin.py``) on the same seeded,
production-shaped worlds and compares every number both define. Written by the
round-3 executing reviewer, who wrote neither implementation. The world
generator is new in this round; earlier rounds' generators stay in history
(2084d5ec4, 43e9ffed1, 0cd90bd4f, e46e1df2d).

Worlds. An agent episode as the runner (lane A5) records it. A Turn is one
model call. The first prefill is 3000-40000 uncached tokens at 3000-9000 tok/s;
later prefills are cached appends of 40-3000 tokens at 6000-15000 tok/s
(3-500 ms, so many are shorter than one 100 ms poll), plus 1-15 ms
time-to-first-token overhead. Decode is 1-3000 tokens, log-uniform, at 20-80
tok/s, capped at 45 s (one-token decodes last 12-50 ms). After the call
returns, a 0.2-40 ms dispatch gap, then 0-4 tool calls back to back (0-2 ms
apart, one pair in five touching), each 5 ms-30 s log-uniform, then a
1-250 ms client gap. One turn in eight has no first-token stamp. One world in
three nests a server-side tool inside one decode. Turn counts cycle through
1, 3, 9, 20 and 32. Logged times sit on an epoch near 3e17 ns, where a float
second cannot hold single nanoseconds.

True power is piecewise linear on integer-ns knots, so every integral is exact
up to float summation. Phase levels (GPU watts): gap 55-80, prefill 300-450,
decode 180-320 with up to 10% drift, tool 60-120 (one tool in ten runs GPU work
at 250-350). Each phase edge slews over 0.2-3 ms and lags the logged boundary
by -3..+8 ms (clamped to a third of the shorter neighbour); ripple knots every
2-25 ms.

Sensor shapes (fixture choices; each quantum derived beside it):
- ina3221/VDD_IN: 1 kHz point samples, +-20 us jitter; meter clock whose
  mapping half-width cycles 0.2, 2 and 5 ms by seed, with the true offset error
  drawn inside it.
- nvml_power/gpu0:power_instant: the NVML lane's own shape (its default 10 ms
  poll; window ends deduplicated to the 100 ms sensor refresh): 25 ms means
  every 100 ms (+-0.5 ms), nominal_interval_ns = 10 ms, host clock, no mapping.
- nvml_power/gpu1: 25 ms means every 100 ms (+-2 ms), nominal 100 ms, its own
  clock with a 1 ms mapping half-width.
- powermetrics/package: back-to-back exact 100 ms windows, 1 ms half-width.
- powermetrics/package_pt: the same windows recorded as point samples
  (averaging_window_ns None), as the Apple lane records variable widths.
- nvml_energy/gpu0: cumulative counter, 100 ms polls (+-2 ms), integer mJ
  truncated, 1e5-5e6 J driver baseline, a restart in one world in three.

Bars (set by the orchestrator for this review, not chosen here):
- joules carries a printed half-width: |lane - twin| <= 1% of the smaller of the
  two half-widths of that estimate.
- outputs with no printed uncertainty (the half-widths themselves, the duty
  fraction): 1e-6 relative, or 1e-6 absolute in the output's unit below 1.
- segment boundaries, turns, kinds, base method names: exact (integers and
  strings: bit identity is the real property).
- flags: compared as sets on names both define with one meaning
  (duty.uncovered, trace.partial_coverage, counter.wrap).

Known reading differences, each accounted for (none is a defect of either; the
lead's rulings on C1/C2 and on partial coverage are pending):
- C1: the lane's interpolation term is the full |hold - linear| (the twin's is
  half), so the lane's width includes the twin's term twice.
- C2 (fix rounds 2 and 2b): window sensors add the duty-gap term
  |P_k - P_(k-1)| x (gap overlap) / 2 and, once per window cut by an end,
  range(P_(k-1), P_k, P_(k+1)) x min(w / 4, overlap of the query with that
  window). Counter decreases add (poll overlap) x (peak non-decreasing step).
  Overlapping windows make the lane's width infinite. All recomputed below
  from the fix-round text, not from either module.
- Partial coverage (R2-m4 / R2b-m3): the lane takes idle, resolution and clock
  ends over the request, the twin over the overlap. Partial-coverage cases
  compare gross joules (idle 0) and tiling only.
- Duty fraction: lane ``;duty.uncovered_fraction=`` over the request, twin
  ``;duty.uncovered=`` over the overlap; equal under full coverage.
"""

from __future__ import annotations

import bisect
import math
import random
import unittest
from dataclasses import replace

from joulewise.align.records import ClockMapping, Episode, PowerTrace, ToolCall, Turn
from tests.align.twins import attribution_twin as twin

try:  # The lane module exists only once the lane branch is merged with this one.
    from joulewise.align import attribution as lane
except ImportError:  # pragma: no cover - twin branch on its own
    lane = None

NS = 1_000_000_000  # ns per s, by definition
MS = 1_000_000  # ns per ms, by definition
US = 1_000  # ns per us, by definition
TURN_COUNTS = (1, 3, 9, 20, 32)  # one-turn, short and long agent episodes
INA_CLOCK_HALF_WIDTHS = (200 * US, 2 * MS, 5 * MS)  # fixture mapping brackets, cycled by seed


# ------------------------------------------------------------------ true power

class Truth:
    """Piecewise-linear true power on integer-ns knots (episode-relative times)."""

    def __init__(self, knots_t, knots_p):
        self.T, self.P = knots_t, knots_p
        # Prefix energy by Neumaier summation: error about 2 eps x sum|terms|
        # = 2 x 1.1e-16 x 2e5 J = 4e-11 J at the largest world. Used only by
        # coverage probes and counter readings, never by agreement assertions.
        cumulative = [0.0]
        running = compensation = 0.0
        for i in range(1, len(knots_t)):
            x = 0.5 * (knots_p[i - 1] + knots_p[i]) * ((knots_t[i] - knots_t[i - 1]) / NS)
            t = running + x
            compensation += (running - t) + x if abs(running) >= abs(x) else (x - t) + running
            running = t
            cumulative.append(running + compensation)
        self.C = cumulative

    def watts(self, t):
        T, P = self.T, self.P
        if t <= T[0]:
            return P[0]
        if t >= T[-1]:
            return P[-1]
        k = bisect.bisect_right(T, t) - 1
        return P[k] + (P[k + 1] - P[k]) * ((t - T[k]) / (T[k + 1] - T[k]))

    def F(self, t):
        T, P, C = self.T, self.P, self.C
        if t <= T[0]:
            return P[0] * ((t - T[0]) / NS)
        if t >= T[-1]:
            return C[-1] + P[-1] * ((t - T[-1]) / NS)
        k = bisect.bisect_right(T, t) - 1
        return C[k] + 0.5 * (P[k] + self.watts(t)) * ((t - T[k]) / NS)

    def integral(self, a, b):
        return self.F(b) - self.F(a)


LEVELS = dict(gap=(55.0, 80.0), prefill=(300.0, 450.0), decode=(180.0, 320.0),
              tool=(60.0, 120.0), gputool=(250.0, 350.0))
RIPPLE = dict(gap=0.05, prefill=0.03, decode=0.06, tool=0.08, gputool=0.05)
SHAPES = (("ina3221", "VDD_IN"), ("nvml_power", "gpu0:power_instant"), ("nvml_power", "gpu1"),
          ("powermetrics", "package"), ("powermetrics", "package_pt"), ("nvml_energy", "gpu0"))


def _loguniform(rng, lo, hi):
    return math.exp(rng.uniform(math.log(lo), math.log(hi)))


def _oracle(pieces):
    """Merge touching model/gap pieces of one owner and kind; tools stay separate calls."""
    out = []
    for owner, kind, a, b in pieces:
        if b <= a:
            continue
        if out and out[-1][:2] == (owner, kind) and kind != "tool" and out[-1][3] == a:
            out[-1] = (owner, kind, out[-1][2], b)
        else:
            out.append((owner, kind, a, b))
    return out


def build_world(seed, *, n_turns=None, ina=True):
    """Returns (episode, truth, epoch, oracle tiling in relative ns, gpu_tool flags by call start)."""
    rng = random.Random(10_007 * seed + 3)
    if n_turns is None:
        n_turns = TURN_COUNTS[seed % len(TURN_COUNTS)]
    epoch = 3 * 10**17 + rng.randrange(10**12)
    pieces, turns, gpu_tools = [], [], set()
    cursor = rng.randint(1 * MS, 20 * MS)
    pieces.append((None, "gap", 0, cursor))
    context = 0
    nested_turn = rng.randrange(n_turns) if seed % 3 == 0 else -1
    for i in range(n_turns):
        t_start = cursor
        if i == 0:
            new = rng.randint(3000, 40000)
            rate = rng.uniform(3000, 9000)
        else:
            new = int(_loguniform(rng, 40, 3000))
            rate = rng.uniform(6000, 15000)
        prefill_ns = int(new / rate * NS) + rng.randint(1 * MS, 15 * MS)
        decode_tokens = int(_loguniform(rng, 1, 3000))
        decode_ns = min(int(decode_tokens / rng.uniform(20, 80) * NS), 45 * NS)
        first = t_start + prefill_ns
        t_end = first + decode_ns
        known = rng.random() >= 0.125
        head = "prefill" if known else "decode"
        calls = []
        if i == nested_turn and decode_ns > 2 * NS:
            a = first + rng.randint(decode_ns // 5, decode_ns // 2)
            b = a + rng.randint(200 * MS, min(5 * NS, decode_ns // 3))
            t_end += b - a
            pieces += [(i, head, t_start, first), (i, "decode", first, a), (i, "tool", a, b),
                       (i, "decode", b, t_end)]
            calls.append(ToolCall("server_search", epoch + a, epoch + b, 200, 4000))
        else:
            pieces += [(i, head, t_start, first), (i, "decode", first, t_end)]
        cursor = t_end
        if i < n_turns - 1:
            dispatch = rng.randint(200 * US, 40 * MS)
            pieces.append((None, "gap", cursor, cursor + dispatch))
            cursor += dispatch
            for _ in range(rng.choice((0, 1, 1, 2, 2, 3, 4))):
                duration = int(_loguniform(rng, 5 * MS, 30 * NS))
                a, b = cursor, cursor + duration
                if rng.random() < 0.1:
                    gpu_tools.add(a)
                calls.append(ToolCall(rng.choice(("bash", "read_file", "search", "python")),
                                      epoch + a, epoch + b, rng.randint(50, 4000),
                                      rng.randint(100, 80000), logged=rng.random() > 0.1))
                pieces.append((i, "tool", a, b))
                gap = 0 if rng.random() < 0.2 else rng.randint(1 * US, 2 * MS)
                pieces.append((None, "gap", b, b + gap))
                cursor = b + gap
            client = rng.randint(1 * MS, 250 * MS)
            pieces.append((None, "gap", cursor, cursor + client))
            cursor += client
        turns.append(Turn(i, epoch + t_start, epoch + t_end, context, new, decode_tokens,
                          hidden_tokens=decode_tokens // 4,
                          first_token_ns=(epoch + first) if known else None,
                          tool_calls=tuple(calls), logged=rng.random() > 0.05))
        context += new + decode_tokens
    end = cursor + rng.randint(1 * MS, 30 * MS)
    pieces.append((None, "gap", cursor, end))
    oracle = _oracle(pieces)

    # Power phases: merge same-level neighbours, then move each edge by its lag.
    phases = []
    for owner, kind, a, b in [(None, "gap", -4 * NS, 0)] + oracle + [(None, "gap", end, end + 4 * NS)]:
        level = "gputool" if kind == "tool" and a in gpu_tools else kind
        if phases and phases[-1][1] == level and phases[-1][3] == a:
            phases[-1] = (None, level, phases[-1][2], b)
        else:
            phases.append((owner, level, a, b))
    edges = [p[2] for p in phases] + [phases[-1][3]]
    moved = list(edges)
    for k in range(1, len(edges) - 1):
        limit = min(edges[k] - edges[k - 1], edges[k + 1] - edges[k]) // 3
        moved[k] = edges[k] + max(-limit, min(limit, rng.randint(-3 * MS, 8 * MS)))
    T, P = [], []
    last = rng.uniform(*LEVELS["gap"])
    for k, (_, level, _, _) in enumerate(phases):
        s, e = moved[k], moved[k + 1]
        base = rng.uniform(*LEVELS[level])
        drift = rng.uniform(-0.10, 0.10) if level == "decode" else 0.0
        if not T or s > T[-1]:
            T.append(s)
            P.append(last)
        t = s + min(rng.randint(200 * US, 3 * MS), max(1, (e - s) // 3))
        while t < e:
            T.append(t)
            P.append(base * (1 + drift * (t - s) / max(1, e - s))
                     * (1 + rng.uniform(-RIPPLE[level], RIPPLE[level])))
            t += rng.randint(2 * MS, 25 * MS)
        last = P[-1]
    T.append(moved[-1])
    P.append(last)
    truth = Truth(T, P)

    traces, mappings = [], []

    def mapping(domain, half_width):
        offset = rng.randint(-60 * NS, 60 * NS)
        mappings.append(ClockMapping(domain, "host", offset, half_width, "synthetic round-trip bracket"))
        return offset, rng.randint(-half_width, half_width)

    if ina:
        # INA3221 shunt LSB 40 uV / 5 mOhm fixture shunt x 5 V bus = 0.04 W quantum.
        quantum = 40e-6 / 5e-3 * 5
        offset, err = mapping("jetson", INA_CLOCK_HALF_WIDTHS[seed % len(INA_CLOCK_HALF_WIDTHS)])
        ts, vs = [], []
        for t in range(-2 * NS, end + 2 * NS, MS):
            t += rng.randint(-20 * US, 20 * US)
            v = truth.watts(t + err) + rng.uniform(-quantum / 2, quantum / 2)
            ts.append(epoch + t - offset)
            vs.append(round(v / quantum) * quantum)
        traces.append(PowerTrace("ina3221", "VDD_IN", "jetson", tuple(ts), tuple(vs), "W", MS,
                                 resolution=quantum))

    def windows(channel, domain, half_width, jitter, nominal):
        offset, err = mapping(domain, half_width) if domain != "host" else (0, 0)
        ts, vs = [], []
        for t in range(-2 * NS + rng.randint(0, 100 * MS - 1), end + 2 * NS, 100 * MS):
            t += rng.randint(-jitter, jitter)
            mean = truth.integral(t + err - 25 * MS, t + err) / (25 * MS / NS)
            ts.append(epoch + t - offset)
            # Half-quantum noise then rounding to the NVML integer-mW quantum (0.001 W).
            vs.append(round((mean + rng.uniform(-0.0005, 0.0005)) / 0.001) * 0.001)
        traces.append(PowerTrace("nvml_power", channel, domain, tuple(ts), tuple(vs), "W", nominal,
                                 averaging_window_ns=25 * MS, duty_fraction=0.25, resolution=0.001))

    windows("gpu0:power_instant", "host", 0, 500 * US, 10 * MS)
    windows("gpu1", "gpuhost", 1 * MS, 2 * MS, 100 * MS)

    offset, err = mapping("mac", 1 * MS)
    ts, vs = [], []
    t = -2 * NS + rng.randint(0, 100 * MS - 1)
    while t < end + 2 * NS:
        mean = truth.integral(t + err - 100 * MS, t + err) / (100 * MS / NS)
        ts.append(epoch + t - offset)
        vs.append(round((mean + rng.uniform(-0.0005, 0.0005)) / 0.001) * 0.001)  # integer mW
        t += 100 * MS
    for channel, window in (("package", 100 * MS), ("package_pt", None)):
        traces.append(PowerTrace("powermetrics", channel, "mac", tuple(ts), tuple(vs), "W", 100 * MS,
                                 averaging_window_ns=window, duty_fraction=1.0 if window else None,
                                 resolution=0.001))

    base = rng.uniform(1e5, 5e6)
    reset_at = rng.randint(end // 4, 3 * end // 4) if seed % 3 == 1 else None
    ts, vs = [], []
    for t in range(-2 * NS + rng.randint(0, 100 * MS - 1), end + 2 * NS, 100 * MS):
        t += rng.randint(-2 * MS, 2 * MS)
        v = (truth.integral(reset_at, t) if reset_at is not None and t >= reset_at
             else base + truth.integral(-2 * NS, t))
        ts.append(epoch + t)
        vs.append(math.floor(v / 0.001) * 0.001)  # integer mJ, truncated as the driver reports
    traces.append(PowerTrace("nvml_energy", "gpu0", "host", tuple(ts), tuple(vs), "J_cumulative", 100 * MS,
                             resolution=0.001))

    record = Episode(f"rv3-{seed}", "shade/synthetic", "sabotage" if seed % 2 else "benign",
                     "qwen3-32b", "mock:vllm", seed, "host", epoch, epoch + end, tuple(turns),
                     power_traces=tuple(traces), clock_mappings=tuple(mappings), flags=("synthetic.review3",))
    return record, truth, epoch, oracle


# ------------------------------------------------- independent C1 / C2 / reset

def _episode_times(trace, mapping):
    offset = mapping.offset_ns if mapping is not None else 0
    return [t + offset for t in trace.t_ns]


def c2_terms(trace, mapping, a, b):
    """C2(a) duty-gap and query-clipped, once-per-window C2(b) terms over [a, b] (episode ns)."""
    if trace.unit != "W" or not trace.averaging_window_ns or trace.averaging_window_ns <= 0:
        return 0.0
    w = trace.averaging_window_ns
    t = _episode_times(trace, mapping)
    p = trace.values
    if any(t[k] - w < t[k - 1] for k in range(1, len(t))):
        return math.inf  # overlapping windows: unsupported shape (fix round 2b)
    terms = []
    for k in range(1, len(t)):
        overlap = min(b, t[k] - w) - max(a, t[k - 1])
        if t[k] - w > t[k - 1] and overlap > 0:
            terms.append(abs(p[k] - p[k - 1]) * (overlap / NS) / 2)
    cut = set()
    for e in (a, b):
        k = bisect.bisect_left(t, e)
        if k < len(t) and t[k] - w < e < t[k] and k not in cut:
            cut.add(k)
            neighbours = p[max(0, k - 1):k + 2]
            overlap = min(b, t[k]) - max(a, t[k] - w)
            terms.append((max(neighbours) - min(neighbours)) * (min(w / 4, overlap) / NS))
    return math.fsum(terms)


def reset_term(trace, mapping, a, b):
    """Poll overlap x peak of the non-decreasing steps, for every counter decrease."""
    if trace.unit != "J_cumulative":
        return 0.0
    t = _episode_times(trace, mapping)
    v = trace.values
    rises = [(v[k + 1] - v[k]) / ((t[k + 1] - t[k]) / NS) for k in range(len(t) - 1) if v[k + 1] >= v[k]]
    peak = max(rises) if rises else math.inf
    return math.fsum(max(0, min(b, t[k + 1]) - max(a, t[k])) / NS * peak
                     for k in range(len(t) - 1) if v[k + 1] < v[k] and min(b, t[k + 1]) > max(a, t[k]))


def twin_interpolation(trace, mapping, a, b):
    """The twin's own term (ii) (half differences) over [a, b], in the trace's domain."""
    offset = mapping.offset_ns if mapping is not None else 0
    if trace.unit == "J_cumulative":
        cumulative, _ = twin._unwrapped(trace.values)
        return twin._interpolation_term(trace.t_ns, cumulative, a - offset, b - offset, cumulative=True)
    return twin._interpolation_term(trace.t_ns, trace.values, a - offset, b - offset, cumulative=False)


def no_uncertainty_bar(value):
    # Orchestrator's bar for outputs without a printed uncertainty.
    if math.isinf(value):
        return 0.0
    return 1e-6 * abs(value) if abs(value) >= 1 else 1e-6


def lane_fraction(method):
    return float(method.split("=", 1)[1]) if ";" in method else 0.0


SHARED_FLAGS = ("duty.uncovered", "trace.partial_coverage", "counter.wrap")


def trace_and_mapping(record, shape):
    trace = next(t for t in record.power_traces if (t.source, t.channel) == shape)
    if trace.clock_domain == record.clock_domain:
        return trace, None
    return trace, next(m for m in record.clock_mappings if m.trace_domain == trace.clock_domain)


@unittest.skipUnless(lane is not None, "lane module joulewise.align.attribution not on this branch")
class TwinAgreement(unittest.TestCase):
    SEEDS = range(10)

    def compare(self, record, epoch, oracle, shape, *, idle, compare_hw=True, where=""):
        source, channel = shape
        trace, mapping = trace_and_mapping(record, shape)
        mine = lane.attribute_episode(record, source=source, channel=channel, idle_watts=idle)
        other = twin.attribute_episode(record, source=source, channel=channel, idle_watts=idle)
        tiling = [(s.turn, s.kind, s.start_ns, s.end_ns) for s in mine.segments]
        self.assertEqual(tiling, [(s.turn, s.kind, s.start_ns, s.end_ns) for s in other.segments], where)
        if oracle is not None:
            self.assertEqual(tiling, [(o, k, epoch + a, epoch + b) for o, k, a, b in oracle], where)
        pairs = [(s.start_ns, s.end_ns, s.energy, t.energy) for s, t in zip(mine.segments, other.segments)]
        pairs.append((record.start_ns, record.end_ns, mine.total, other.total))
        for a, b, le, te in pairs:
            label = f"{where} [{a - epoch}, {b - epoch}]"
            # joules: 1% of the smaller printed half-width (orchestrator's bar).
            self.assertLessEqual(abs(le.joules - te.joules), 0.01 * min(le.half_width_j, te.half_width_j),
                                 f"{label} joules lane {le.joules!r} twin {te.joules!r}")
            self.assertEqual(le.method.split(";")[0], te.method.split(";")[0], label)
            if not compare_hw:
                continue
            expected = (te.half_width_j + twin_interpolation(trace, mapping, a, b)
                        + c2_terms(trace, mapping, a, b) + reset_term(trace, mapping, a, b))
            if math.isinf(expected):
                self.assertTrue(math.isinf(le.half_width_j), f"{label} lane half-width finite")
            else:
                self.assertLessEqual(abs(le.half_width_j - expected), no_uncertainty_bar(expected),
                                     f"{label} half-width lane {le.half_width_j!r} expected {expected!r}")
            fraction = twin.split_method(te.method)[1].get("duty.uncovered", 0.0)
            self.assertLessEqual(abs(lane_fraction(le.method) - fraction), no_uncertainty_bar(fraction), label)
            for flag in SHARED_FLAGS:
                self.assertEqual(flag in le.flags, flag in te.flags, f"{label} {flag}")
        return len(pairs)

    def test_full_coverage_worlds_agree(self):
        total = 0
        for seed in self.SEEDS:
            record, truth, epoch, oracle = build_world(seed)
            idle_level = truth.watts(0)  # fixture: the episode's opening gap level as idle
            for shape in SHAPES:
                for idle in (0.0, idle_level):
                    with self.subTest(seed=seed, shape=shape, idle=idle):
                        total += self.compare(record, epoch, oracle, shape, idle=idle,
                                              where=f"seed {seed} {shape} idle {idle}")
        self.assertGreater(total, 0)

    def test_partial_coverage_agrees_on_gross_joules(self):
        for seed in range(3):
            record, truth, epoch, oracle = build_world(seed, ina=seed == 0)
            span = record.end_ns - record.start_ns
            for keep in ("late", "early"):
                cut_at = record.start_ns + (span // 3 if keep == "late" else 2 * span // 3)
                for trace in record.power_traces:
                    shape = (trace.source, trace.channel)
                    _, mapping = trace_and_mapping(record, shape)
                    offset = mapping.offset_ns if mapping is not None else 0
                    index = [k for k, t in enumerate(trace.t_ns)
                             if (t + offset >= cut_at) == (keep == "late")]
                    cut = replace(trace, t_ns=tuple(trace.t_ns[k] for k in index),
                                  values=tuple(trace.values[k] for k in index))
                    partial = replace(record, power_traces=tuple(cut if t is trace else t
                                                                 for t in record.power_traces))
                    with self.subTest(seed=seed, keep=keep, shape=shape):
                        self.compare(partial, epoch, oracle, shape, idle=0.0, compare_hw=False,
                                     where=f"partial {keep} seed {seed} {shape}")
                        result = lane.attribute_episode(partial, source=shape[0], channel=shape[1])
                        self.assertIn("trace.partial_coverage", result.total.flags)

    def test_edge_episodes_agree(self):
        record, truth, epoch, oracle = build_world(4, n_turns=1, ina=False)
        cases = {
            "one turn": record,
            "no turns": replace(record, turns=()),
            "zero-length episode": replace(record, turns=(), end_ns=record.start_ns),
        }
        for name, case in cases.items():
            for shape in SHAPES[1:]:
                with self.subTest(case=name, shape=shape):
                    expected = oracle if name == "one turn" else None
                    self.compare(case, epoch, expected, shape, idle=0.0, where=f"{name} {shape}")
