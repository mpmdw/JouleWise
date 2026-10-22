"""Twin agreement for lane A4 (``joulewise/align/attribution.py``), review round 2b.

Runs the lane's public functions and the independent twin
(``tests/align/twins/attribution_twin.py``) on the same seeded,
production-shaped worlds and compares every number both define. Written by a
review-round-2b executing reviewer who wrote neither implementation. The world
generator is new in this round (rounds 1, 2 and 3 used other generators).

Worlds. An agent episode as the runner (lane A5) records it: a Turn is one
model call whose adapter stamps lie 1-5 ms inside the measured call; 0-3 tool
calls run after the call returns, back to back (0-500 us apart, one pair in
five exactly touching); a 2-300 ms client gap precedes the next call. One world
in three nests a server-side tool inside one turn's decode. Prefill time comes
from new tokens (80-9000, first turn 2000-30000) at 5000-12000 tok/s, decode
from 15-2500 tokens at 30-65 tok/s (capped at 60 s); tools last 0.2-30 s
log-uniform, and 15% last 20-200 ms. One turn in ten has no first-token stamp.
Turn counts cycle through 1, 4, 12 and 24. Logged times sit on an epoch near
6e17 ns, where a float second cannot hold single nanoseconds.

True power is piecewise linear on integer-ns knots, so every integral is exact
up to float summation. Each phase has a level (GPU watts: gap 60-75, prefill
340-430, decode 220-300 with up to 8% drift, tool 70-110), ripple knots every
3-30 ms (gap 5%, prefill 2%, decode 6%, tool 8%), a 0.3-4 ms slew, and a
-2..+6 ms lag between the logged boundary and the real power edge.

Sensor shapes (all fixture choices):
- ina3221/VDD_IN: 1 kHz point samples, +-20 us jitter, quantum
  40 uV / 5 mOhm x 5 V = 0.04 W, meter clock with a 0.5 ms mapping half-width
  and a true offset error drawn inside it.
- nvml_power/gpu0: 25 ms window means every 100 ms (+-2 ms poll jitter),
  integer mW (0.001 W), host clock, no mapping.
- nvml_power/gpu1: the same on its own clock, mapping half-width 1 ms.
- powermetrics/package: back-to-back exact 100 ms windows, integer mW, 1 ms.
- powermetrics/package_jit: back-to-back windows whose real length is
  100 +- 3 ms while the record says 100 ms (window.overlap / duty gaps).
- nvml_energy/gpu0: cumulative counter every 100 ms (+-2 ms), integer mJ
  truncated, a 1e5-5e6 J driver baseline, a driver restart in one world in
  three.

Bars (set by the orchestrator for this review, not chosen here):
- joules carries a printed half-width: |lane - twin| <= 1% of the smaller of the
  two half-widths of that estimate.
- outputs with no printed uncertainty (the half-widths themselves, the duty
  fraction): 1e-6 relative, or 1e-6 absolute in the output's unit when the
  value is below 1.
- segment boundaries, turns, kinds, base method names: exact (integers and
  strings: bit identity is the real property).
- flags: compared as sets on names both define with one meaning
  (duty.uncovered, trace.partial_coverage, counter.wrap).

Known reading differences, each accounted for (none is a defect of either):
- C1/C2 (fix round 2, awaiting the lead's ruling): the lane's interpolation term
  is the full |hold - linear| (the twin's is half), and window sensors add the
  duty-gap term |P_k - P_(k-1)| x gap overlap / 2 and the window-cut term
  (range of P_(k-1), P_k, P_(k+1)) x w / 4. Counter decreases add the poll's
  overlap x the peak of the non-decreasing steps. The expected lane half-width
  is twin + twin interpolation + C2(a) + C2(b) + reset, with C2 and the reset
  term recomputed here from the fix-round-2 text, not from either module.
- Partial coverage (R2-m4, awaiting a ruling): the lane takes idle, resolution
  and the clock ends over the request, the twin over the overlap. The
  partial-coverage case compares gross joules (idle 0) and tiling only.
- Duty fraction: lane ``;duty.uncovered_fraction=`` over the request, twin
  ``;duty.uncovered=`` over the overlap; equal under full coverage.
"""

from __future__ import annotations

import bisect
import math
import json
import random
import sys
import unittest
from dataclasses import replace

from joulewise.align.records import ClockMapping, Episode, PowerTrace, ToolCall, Turn
from tests.align.twins import attribution_twin as twin

try:  # The lane module exists only once the lane branch is merged with this one.
    from joulewise.align import attribution as lane
except ImportError:  # pragma: no cover - twin branch on its own
    lane = None

NS = 1_000_000_000  # ns per s, by definition
MS = 1_000_000
US = 1_000
EPS = sys.float_info.epsilon


# ------------------------------------------------------------------ true power

class Truth:
    """Piecewise-linear true power on integer-ns knots (episode-relative times)."""

    def __init__(self, knots_t, knots_p):
        self.T, self.P = knots_t, knots_p
        cumulative = [0.0]
        running = compensation = 0.0  # Neumaier sum keeps the prefix exact to ~1 ulp
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
        dt = t - T[k]
        p = P[k] + (P[k + 1] - P[k]) * (dt / (T[k + 1] - T[k]))
        return C[k] + 0.5 * (P[k] + p) * (dt / NS)

    def integral(self, a, b):
        return self.F(b) - self.F(a)


LEVELS = dict(gap=(60.0, 75.0), prefill=(340.0, 430.0), decode=(220.0, 300.0), tool=(70.0, 110.0))
RIPPLE = dict(gap=0.05, prefill=0.02, decode=0.06, tool=0.08)
SHAPES = (("ina3221", "VDD_IN"), ("nvml_power", "gpu0"), ("nvml_power", "gpu1"),
          ("powermetrics", "package"), ("powermetrics", "package_jit"), ("nvml_energy", "gpu0"))


def _oracle(pieces):
    out = []
    for owner, kind, a, b in pieces:
        if b <= a:
            continue
        if (out and out[-1][0] == owner and out[-1][1] == kind and kind != "tool"
                and out[-1][3] == a):
            out[-1] = (owner, kind, out[-1][2], b)
        else:
            out.append((owner, kind, a, b))
    return out


def build_world(seed, *, ina_hz_divisor=1):
    """Episode, Truth, epoch, oracle tiling (relative ns)."""
    rng = random.Random(seed)
    n_turns = (1, 4, 12, 24)[seed % 4]
    epoch = 6 * 10**17 + rng.randrange(10**12)
    pieces, turns = [], []
    cursor = rng.randint(1 * MS, 5 * MS)
    pieces.append((None, "gap", 0, cursor))
    context = 0
    nested_turn = rng.randrange(n_turns) if seed % 3 == 0 else -1
    for i in range(n_turns):
        t_start = cursor + rng.randint(1 * MS, 5 * MS)
        pieces.append((None, "gap", cursor, t_start))
        new = rng.randint(2000, 30000) if i == 0 else int(math.exp(rng.uniform(math.log(80), math.log(9000))))
        prefill_ns = int((new + context / 50) / rng.uniform(5000, 12000) * NS) + rng.randint(2 * MS, 40 * MS)
        decode_tokens = int(math.exp(rng.uniform(math.log(15), math.log(2500))))
        decode_ns = min(int(decode_tokens / rng.uniform(30, 65) * NS), 60 * NS)
        first = t_start + prefill_ns
        t_end = first + decode_ns
        known = rng.random() > 0.1
        calls = []
        head = "prefill" if known else "decode"
        if i == nested_turn and decode_ns > 2 * NS:
            a = first + rng.randint(decode_ns // 5, decode_ns // 2)
            b = a + rng.randint(200 * MS, min(5 * NS, decode_ns // 3))
            t_end += b - a
            pieces += [(i, head, t_start, first), (i, "decode", first, a), (i, "tool", a, b),
                       (i, "decode", b, t_end)]
            calls.append(ToolCall("server_search", epoch + a, epoch + b, 200, 4000))
        else:
            pieces += [(i, head, t_start, first), (i, "decode", first, t_end)]
        cursor = t_end + rng.randint(0, 3 * MS) + rng.randint(50 * US, 2 * MS)
        pieces.append((None, "gap", t_end, cursor))
        for _ in range(0 if i == n_turns - 1 else rng.choice((0, 1, 1, 1, 2, 2, 3))):
            if rng.random() < 0.15:
                duration = rng.randint(20 * MS, 200 * MS)
            else:
                duration = int(math.exp(rng.uniform(math.log(0.2), math.log(30.0))) * NS)
            a, b = cursor, cursor + duration
            calls.append(ToolCall(rng.choice(("bash", "read_file", "search")), epoch + a, epoch + b,
                                  rng.randint(50, 2000), rng.randint(100, 50000), logged=rng.random() > 0.1))
            pieces.append((i, "tool", a, b))
            gap = 0 if rng.random() < 0.2 else rng.randint(10 * US, 500 * US)
            pieces.append((None, "gap", b, b + gap))
            cursor = b + gap
        client = rng.randint(2 * MS, 300 * MS)
        pieces.append((None, "gap", cursor, cursor + client))
        cursor += client
        turns.append(Turn(i, epoch + t_start, epoch + t_end, context, new, decode_tokens,
                          first_token_ns=(epoch + first) if known else None,
                          tool_calls=tuple(calls), logged=rng.random() > 0.05))
        context += new + decode_tokens
    end = cursor + rng.randint(1 * MS, 10 * MS)
    pieces.append((None, "gap", cursor, end))
    oracle = _oracle(pieces)

    # Power phases: merge same-kind neighbours, move each edge by the lag.
    phases = []
    for owner, kind, a, b in [(None, "gap", -3 * NS, 0)] + oracle + [(None, "gap", end, end + 3 * NS)]:
        if phases and phases[-1][1] == kind and phases[-1][3] == a:
            phases[-1] = (None, kind, phases[-1][2], b)
        else:
            phases.append((owner, kind, a, b))
    edges = [p[2] for p in phases] + [phases[-1][3]]
    moved = list(edges)
    for k in range(1, len(edges) - 1):
        limit = min(edges[k] - edges[k - 1], edges[k + 1] - edges[k]) // 3
        moved[k] = edges[k] + max(-limit, min(limit, rng.randint(-2 * MS, 6 * MS)))
    T, P = [], []
    last = rng.uniform(*LEVELS["gap"])
    for k, (_, kind, _, _) in enumerate(phases):
        s, e = moved[k], moved[k + 1]
        base = rng.uniform(*LEVELS[kind])
        drift = rng.uniform(-0.08, 0.08) if kind == "decode" else 0.0
        if not T or s > T[-1]:
            T.append(s)
            P.append(last)
        t = s + min(rng.randint(300 * US, 4 * MS), max(1, (e - s) // 3))
        while t < e:
            P.append(base * (1 + drift * (t - s) / max(1, e - s)) * (1 + rng.uniform(-RIPPLE[kind], RIPPLE[kind])))
            T.append(t)
            t += rng.randint(3 * MS, 30 * MS)
        last = P[-1]
    T.append(moved[-1])
    P.append(last)
    truth = Truth(T, P)

    traces, mappings = [], []

    def mapping(domain, half_width):
        offset = rng.randint(-50 * NS, 50 * NS)
        mappings.append(ClockMapping(domain, "host", offset, half_width, "synthetic round-trip bracket"))
        return offset, rng.randint(-half_width, half_width)

    quantum = 40e-6 / 5e-3 * 5  # INA3221 shunt LSB / shunt * bus voltage = 0.04 W
    offset, err = mapping("jetson", 500 * US)
    ts, vs = [], []
    for t in range(-2 * NS, end + 2 * NS, MS * ina_hz_divisor):
        t += rng.randint(-20 * US, 20 * US)
        v = truth.watts(t + err) + rng.uniform(-quantum / 2, quantum / 2)
        ts.append(epoch + t - offset)
        vs.append(round(v / quantum) * quantum)
    traces.append(PowerTrace("ina3221", "VDD_IN", "jetson", tuple(ts), tuple(vs), "W",
                             MS * ina_hz_divisor, resolution=quantum))

    def windows(channel, domain, half_width):
        offset, err = mapping(domain, half_width) if domain != "host" else (0, 0)
        ts, vs = [], []
        for t in range(-2 * NS + rng.randint(0, 100 * MS - 1), end + 2 * NS, 100 * MS):
            t += rng.randint(-2 * MS, 2 * MS)
            mean = truth.integral(t + err - 25 * MS, t + err) / (25 * MS / NS)
            ts.append(epoch + t - offset)
            vs.append(round((mean + rng.uniform(-0.0005, 0.0005)) / 0.001) * 0.001)  # integer mW
        traces.append(PowerTrace("nvml_power", channel, domain, tuple(ts), tuple(vs), "W", 100 * MS,
                                 averaging_window_ns=25 * MS, duty_fraction=0.25, resolution=0.001))

    windows("gpu0", "host", 0)
    windows("gpu1", "gpuhost", 1 * MS)

    for channel, domain, jitter in (("package", "mac", 0), ("package_jit", "mac2", 3 * MS)):
        offset, err = mapping(domain, 1 * MS)
        ts, vs = [], []
        t = -2 * NS + rng.randint(0, 100 * MS - 1)
        previous = t - 100 * MS
        while t < end + 2 * NS:
            mean = truth.integral(previous + err, t + err) / ((t - previous) / NS)
            ts.append(epoch + t - offset)
            vs.append(round((mean + rng.uniform(-0.0005, 0.0005)) / 0.001) * 0.001)
            previous = t
            t += 100 * MS + (rng.randint(-jitter, jitter) if jitter else 0)
        traces.append(PowerTrace("powermetrics", channel, domain, tuple(ts), tuple(vs), "W", 100 * MS,
                                 averaging_window_ns=100 * MS, duty_fraction=1.0, resolution=0.001))

    base = rng.uniform(1e5, 5e6)
    reset_at = rng.randint(end // 4, 3 * end // 4) if seed % 3 == 1 else None
    ts, vs = [], []
    for t in range(-2 * NS + rng.randint(0, 100 * MS - 1), end + 2 * NS, 100 * MS):
        t += rng.randint(-2 * MS, 2 * MS)
        v = (truth.integral(reset_at, t) if reset_at is not None and t >= reset_at
             else base + truth.integral(-2 * NS, t))
        ts.append(epoch + t)
        vs.append(math.floor(v / 0.001) * 0.001)  # integer mJ, truncated
    traces.append(PowerTrace("nvml_energy", "gpu0", "host", tuple(ts), tuple(vs), "J_cumulative", 100 * MS,
                             resolution=0.001, notes=json.dumps({"unknown_sensor_age_bound_ns":0})))

    record = Episode(f"rv2b-{seed}", "shade/synthetic", "sabotage" if seed % 2 else "benign",
                     "qwen3-32b", "mock:vllm", seed, "host", epoch, epoch + end, tuple(turns),
                     power_traces=tuple(traces), clock_mappings=tuple(mappings), flags=("synthetic.review",))
    return record, truth, epoch, oracle


# ------------------------------------------------------- independent C2 / reset

def _episode_times(trace, mapping):
    offset = mapping.offset_ns if mapping is not None else 0
    return [t + offset for t in trace.t_ns]


def c2_terms(trace, mapping, a, b):
    """C2(a) duty-gap and C2(b) window-cut terms over [a, b] (episode ns).

    Updated in review round 3 to fix round 2b (R2b-m1, R2b-m2): each cut window
    counts once, clipped to min(w / 4, overlap of the query with that window);
    overlapping windows give an infinite width.
    """
    if trace.unit != "W" or not trace.averaging_window_ns or trace.averaging_window_ns <= 0:
        return 0.0
    w = trace.averaging_window_ns
    t = _episode_times(trace, mapping)
    p = trace.values
    if any(t[k] - w < t[k - 1] for k in range(1, len(t))):
        return math.inf
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
    return 1e-6 * abs(value) if abs(value) >= 1 else 1e-6


def lane_fraction(method):
    return float(method.split("=", 1)[1]) if ";" in method else 0.0


SHARED_FLAGS = ("duty.uncovered", "trace.partial_coverage", "counter.wrap")


@unittest.skipUnless(lane is not None, "lane module joulewise.align.attribution not on this branch")
class TwinAgreement(unittest.TestCase):
    SEEDS = range(12)

    def compare(self, record, truth, epoch, oracle, shape, *, idle, compare_hw=True, where=""):
        source, channel = shape
        trace = next(t for t in record.power_traces if (t.source, t.channel) == shape)
        mapping = next((m for m in record.clock_mappings if m.trace_domain == trace.clock_domain), None)
        mine = lane.attribute_episode(record, source=source, channel=channel, idle_watts=idle)
        other = twin.attribute_episode(record, source=source, channel=channel, idle_watts=idle)
        tiling = [(s.turn, s.kind, s.start_ns, s.end_ns) for s in mine.segments]
        self.assertEqual(tiling, [(s.turn, s.kind, s.start_ns, s.end_ns) for s in other.segments], where)
        if oracle is not None:
            self.assertEqual(tiling, [(o, k, epoch + a, epoch + b) for o, k, a, b in oracle], where)
        # Conservation: each segment sums its own spans; the two split spans at
        # its ends cost at most 8 roundings each (two lerps, a sum, a product)
        # and the segment's addition one more, so 16 eps per segment magnitude.
        values = [s.energy.joules for s in mine.segments]
        self.assertLessEqual(abs(math.fsum(values) - mine.total.joules),
                             16 * (len(values) + 1) * EPS * math.fsum(abs(v) for v in values), where)
        pairs = [(s.start_ns, s.end_ns, s.energy, t.energy) for s, t in zip(mine.segments, other.segments)]
        pairs.append((record.start_ns, record.end_ns, mine.total, other.total))
        compared = 0
        for a, b, le, te in pairs:
            label = f"{where} [{a - epoch}, {b - epoch}]"
            # The lane models per-sample unknown timing that the twin does
            # not, so their finiteness can differ. Pin the floor policy on
            # each result rather than requiring that diagnostic to agree.
            for estimate, total in ((le, mine.total), (te, other.total)):
                self.assertEqual("powermetrics.attribution_floor" in estimate.flags,
                    estimate is total and trace.source == "powermetrics"
                    and math.isfinite(estimate.half_width_j), f"{label} printed floor")
            # joules: 1% of the smaller printed half-width (orchestrator's bar).
            self.assertLessEqual(abs(le.joules - te.joules), 0.01 * min(le.half_width_j, te.half_width_j),
                                 f"{label} joules lane {le.joules!r} twin {te.joules!r}")
            self.assertEqual(le.method.split(";")[0], te.method.split(";")[0], label)
            if compare_hw:
                from tests.align.test_twin_attribution import knot_interpolation_bound
                # Rebuild each single-query width independently. The twin's
                # total now includes tile bounds, so start from its public
                # single-query primitive rather than widening that total twice.
                def query_width(start, end):
                    base = twin.trace_energy(trace, start, end, mapping=mapping,
                                             idle_watts=idle)
                    width = (base.half_width_j
                            + knot_interpolation_bound(trace, mapping, start, end)
                            + twin_interpolation(trace, mapping, start, end)
                            + c2_terms(trace, mapping, start, end)
                            + reset_term(trace, mapping, start, end))
                    return width

                expected = query_width(a, b)
                if le is mine.total and trace.unit == "W" and trace.averaging_window_ns is None:
                    expected = max(expected, math.fsum(query_width(s.start_ns, s.end_ns)
                                                      for s in other.segments))
                if le is mine.total and trace.source == "powermetrics" and math.isfinite(expected):
                    # D-078 clause 11: the minimum belongs to the printed total.
                    expected = max(1.0, expected)
                if math.isinf(expected):
                    self.assertTrue(math.isinf(le.half_width_j), f"{label} lane half-width finite")
                else:
                    self.assertLessEqual(abs(le.half_width_j - expected), no_uncertainty_bar(expected),
                                         f"{label} half-width lane {le.half_width_j!r} expected {expected!r}")
                fraction = twin.split_method(te.method)[1].get("duty.uncovered", 0.0)
                self.assertLessEqual(abs(lane_fraction(le.method) - fraction), no_uncertainty_bar(fraction), label)
                for flag in SHARED_FLAGS:
                    self.assertEqual(flag in le.flags, flag in te.flags, f"{label} {flag}")
            compared += 1
        return compared

    def test_full_coverage_worlds_agree(self):
        total = 0
        for seed in self.SEEDS:
            record, truth, epoch, oracle = build_world(seed)
            for shape in SHAPES:
                for idle in (0.0, 65.0):  # 0 W and a mid gap-level idle (fixture)
                    with self.subTest(seed=seed, shape=shape, idle=idle):
                        total += self.compare(record, truth, epoch, oracle, shape, idle=idle,
                                              where=f"seed {seed} {shape} idle {idle}")
        self.assertGreater(total, 0)

    def test_trace_starting_after_episode_start_agrees_on_gross_joules(self):
        for seed in range(4):
            record, truth, epoch, oracle = build_world(seed)
            late = record.start_ns + (record.end_ns - record.start_ns) // 3
            for shape in SHAPES:
                trace = next(t for t in record.power_traces if (t.source, t.channel) == shape)
                mapping = next((m for m in record.clock_mappings if m.trace_domain == trace.clock_domain), None)
                offset = mapping.offset_ns if mapping is not None else 0
                keep = [k for k, t in enumerate(trace.t_ns) if t + offset >= late]
                cut = replace(trace, t_ns=tuple(trace.t_ns[k] for k in keep),
                              values=tuple(trace.values[k] for k in keep))
                partial = replace(record, power_traces=tuple(cut if t is trace else t for t in record.power_traces))
                with self.subTest(seed=seed, shape=shape):
                    self.compare(partial, truth, epoch, oracle, shape, idle=0.0, compare_hw=False,
                                 where=f"partial seed {seed} {shape}")
                    result = lane.attribute_episode(partial, source=shape[0], channel=shape[1])
                    self.assertIn("trace.partial_coverage", result.total.flags)


if __name__ == "__main__":
    unittest.main()
