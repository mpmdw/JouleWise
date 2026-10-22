"""Twin agreement for lane A4 (``joulewise/align/attribution.py``), review round 3.

Runs the lane's public functions and the independent twin
(``tests/align/twins/attribution_twin.py``) on the same seeded,
production-shaped worlds and compares every number they both define. Written
by the round-3 executing reviewer; neither implementation's author wrote it,
and the worlds are new in round 3 (rounds 1 and 2 used different generators).

Worlds (round 3). An agent episode as the runner records it: a Turn is one
model call [start, end] with its first token inside (unknown on one turn in
ten); 0-3 tool calls run back to back after the call returns (0-30 ms apart),
then a 2-400 ms client gap before the next turn. One world in four also nests a
server-side tool call inside one turn's decode. Turn counts cycle through
1, 2, 8, 20 and 32. Prefill time comes from 150-60000 new tokens (one turn in
twenty: 100k-250k) at 4000-15000 tok/s plus a context term; decode from 4-2500
tokens at 25-70 tok/s, capped at 45 s; tools 0.2-30 s log-uniform. One turn
and one tool per episode are unlogged. Logged times are integer ns from an
epoch of 7e17 ns, where a float second cannot hold single nanoseconds.

True power is piecewise linear, so every integral is exact. Each phase has a
level (GPU watts: gap 55-75, prefill 330-430, decode 210-300 drifting up to 8%
over the phase, tool 75-110), a 0.5-4 ms slew at its start, and ripple knots
every 5-40 ms (decode +-4%, prefill +-2%, tool and gap +-5%). With ``lag`` on,
the real power edge trails or leads the logged boundary by -2..+6 ms (the GPU
starts work after the host logs it); with ``lag`` off the edge is exactly at
the logged boundary. Lags and slews are clamped to a third of the shorter
neighbouring phase so phases keep their order.

Sensor shapes (fixture choices, each derived beside its value in SHAPES):
INA3221 point samples at 1 kHz, NVML 25 ms window means every 100 ms, NVML
with a meter-clock mapping, powermetrics back-to-back 100 ms windows, and the
NVML cumulative energy counter (integer mJ, truncated, with a driver restart
in one world in three).

Bars (set by the orchestrator for this review, not chosen here):
- ``joules`` has a printed half-width: agree within 1% of the smaller of the
  two implementations' half-widths for that estimate.
- Outputs with no printed uncertainty (the half-widths themselves, duty
  fractions): 1e-6 relative, or 1e-6 absolute in the output's unit when the
  value is below 1.
- Segment boundaries, turn indices, kinds and base method names: exact
  (integers and strings, so bit identity is the real property).
- Flags: compared as sets on the names both sides define with one meaning.

Known reading differences (the comparison accounts for each; none is a defect):
- C2 (lane, ordered by fix round 2 and awaiting the lead's ruling): the lane's
  interpolation term is the full |hold - linear| difference (the twin's is
  half), and window sensors add the duty-gap and window-cut one-step terms.
  The expected lane half-width is therefore twin + twin interpolation term +
  C2(a) + C2(b) + reset sensitivity, with C2 and the reset term recomputed
  here from the fix-round-2 brief text, not from either implementation.
- Counter restart: both count the restart reading; the lane adds (reset poll
  overlap) x (observed peak step power), recomputed here.
- Partial coverage (R2-m4, awaiting a ruling): the lane subtracts idle over the
  requested interval, the twin over the overlap. Partial-coverage worlds
  compare gross joules (idle 0) only.
- Duty fraction: lane ``;duty.uncovered_fraction=`` over the request, twin
  ``;duty.uncovered=`` over the overlap; equal under full coverage.

Result at lane head 0d9deed40: 11344 estimates (segments and totals, five
shapes, lag on and off, idle 0 and the gap level) agree; the largest
|lane - twin| joules difference is 2.1e-7 of its bar, and every lane
half-width equals the twin's plus the recomputed C1, C2 and reset terms within
1e-6 relative. This file replaces the round-2 comparison, whose half-width
checks predate C2; the round-2 worlds stay in history at 43e9ffed1.
"""

from __future__ import annotations

import bisect
import math
import random
import unittest
from dataclasses import dataclass

from joulewise.align.records import ClockMapping, Episode, PowerTrace, ToolCall, Turn
from tests.align.twins import attribution_twin as twin

try:  # The lane module exists only once the lane branch is merged with this one.
    from joulewise.align import attribution as lane
except ImportError:  # pragma: no cover - twin branch alone
    lane = None

NS = 1_000_000_000  # ns per second, by definition
MS = 1_000_000  # ns per millisecond, by definition
US = 1_000  # ns per microsecond, by definition
ORIGIN = 7 * 10**17  # host monotonic epoch (ns); 7e8 s, where a float second spacing is ~1e-7 s
TURN_COUNTS = (1, 2, 8, 20, 32)  # one-turn, short and long agent episodes


# ---------------------------------------------------------------- truth timeline

class Truth:
    """Piecewise-linear true power through knots (t_ns relative to ORIGIN, watts)."""

    def __init__(self, knots):
        self.t = [k[0] for k in knots]
        self.p = [k[1] for k in knots]
        # Cumulative energy by Neumaier summation. Its error is about
        # 2 eps x sum|terms| = 2 * 1.1e-16 * 2e5 J = 4e-11 J at the largest
        # world (640 s at about 300 W). The truth is used only by the
        # reviewer's coverage probes, never by the agreement assertions below;
        # there it is compared with printed half-widths no smaller than
        # 2.0e-4 J (measured over every world of this file), 5e6 times its error.
        self.cum = [0.0]
        total = comp = 0.0
        for i in range(len(self.t) - 1):
            term = 0.5 * (self.p[i] + self.p[i + 1]) * ((self.t[i + 1] - self.t[i]) / NS)
            new = total + term
            comp += (total - new) + term if abs(total) >= abs(term) else (term - new) + total
            total = new
            self.cum.append(total + comp)

    def watts(self, x):
        i = bisect.bisect_right(self.t, x) - 1
        if i < 0:
            return self.p[0]
        if i >= len(self.t) - 1:
            return self.p[-1]
        t0, t1, p0, p1 = self.t[i], self.t[i + 1], self.p[i], self.p[i + 1]
        return p0 + (p1 - p0) * ((x - t0) / (t1 - t0))

    def _energy_to(self, x):
        """Energy from the first knot to x (J); flat power outside the knots."""
        if x <= self.t[0]:
            return self.p[0] * ((x - self.t[0]) / NS)
        if x >= self.t[-1]:
            return self.cum[-1] + self.p[-1] * ((x - self.t[-1]) / NS)
        i = bisect.bisect_right(self.t, x) - 1
        return self.cum[i] + 0.5 * (self.p[i] + self.watts(x)) * ((x - self.t[i]) / NS)

    def integral(self, x, y):
        """Exact integral in J over [x, y] (ns relative to ORIGIN)."""
        return 0.0 if y <= x else self._energy_to(y) - self._energy_to(x)


# ---------------------------------------------------------------- sensor shapes

@dataclass(frozen=True)
class Shape:
    name: str
    source: str
    channel: str
    unit: str
    period_ns: int
    window_ns: int | None
    resolution: float
    jitter_ns: int
    scale: float  # multiplies the GPU-watt levels to this device's watts
    clock: str  # "host" (no mapping) or "meter" (ClockMapping with uncertainty)
    clock_half_width_ns: int


SHAPES = (
    # INA3221 rail at 1 kHz: shunt LSB 40 uV / 10 mOhm fixture shunt = 4 mA, times
    # a 5 V bus = 0.02 W quantum. +-30 us timestamp jitter; meter clock with a
    # 0.4 ms mapping half-width (a 0.8 ms round-trip bracket). Jetson-scale power.
    Shape("ina3221", "ina3221", "VDD_IN", "W", MS, None, 0.02, 30 * US, 0.055, "meter", 400 * US),
    # NVML power: a 25 ms mean ending at each 100 ms poll, +-3 ms poll jitter,
    # integer mW (0.001 W); host clock, so no ClockMapping (as the NVML lane records).
    Shape("nvml_power", "nvml_power", "gpu0", "W", 100 * MS, 25 * MS, 0.001, 3 * MS, 1.0, "host", 0),
    # The same NVML sensor read through a meter-clock mapping with a 0.2 ms
    # half-width, so the clock term runs on a duty-cycled window sensor.
    Shape("nvml_power_mapped", "nvml_power", "gpu0", "W", 100 * MS, 25 * MS, 0.001, 3 * MS, 1.0,
          "meter", 200 * US),
    # powermetrics-like whole 100 ms windows, back to back, integer mW; meter
    # clock with a 1 ms half-width. M3 Max package scale.
    Shape("powermetrics", "powermetrics", "package", "W", 100 * MS, 100 * MS, 0.001, 0, 0.12,
          "meter", MS),
    # NVML cumulative energy counter: integer mJ (0.001 J), truncated as the
    # driver reports it; 100 ms polls with +-3 ms jitter; host clock.
    Shape("nvml_energy", "nvml_energy", "gpu0", "J_cumulative", 100 * MS, None, 0.001, 3 * MS, 1.0,
          "host", 0),
)
SHAPE = {shape.name: shape for shape in SHAPES}
METER_OFFSET_NS = 3_141_592_653_589  # fixture: t_host = t_meter + this offset (ns)


def _loguniform(rng, lo, hi):
    return math.exp(rng.uniform(math.log(lo), math.log(hi)))


def build_world(seed, shape, *, lag=True, partial=None, n_turns=None):
    """One episode on one sensor shape. Returns (episode, truth, meta).

    ``partial``: None (the trace covers the episode with 1 s to spare), "late"
    (the trace starts 3.3 s after the episode starts) or "early" (it ends 2.7 s
    before the episode ends).
    """
    rng = random.Random(seed * 1009 + 17)
    if n_turns is None:
        n_turns = TURN_COUNTS[seed % len(TURN_COUNTS)]
    phases = []  # (owner, kind, start, end) logged, ns from ORIGIN
    cursor = 0

    def add(owner, kind, duration):
        nonlocal cursor
        phases.append((owner, kind, cursor, cursor + duration))
        cursor += duration

    add(None, "gap", rng.randint(100 * MS, 2 * NS))
    turns = []
    context = rng.randint(500, 4000)
    nested_turn = rng.randrange(n_turns) if seed % 4 == 0 else None
    unlogged_turn = rng.randrange(n_turns)
    for index in range(n_turns):
        prefill_tokens = int(_loguniform(rng, 150, 60000))
        if rng.random() < 0.05:
            prefill_tokens = rng.randint(100_000, 250_000)
        prefill_ns = int((prefill_tokens / rng.uniform(4000, 15000) + context * 1e-7) * NS)
        prefill_ns += rng.randint(MS, 5 * MS)
        decode_tokens = int(_loguniform(rng, 4, 2500))
        decode_ns = min(45 * NS, max(2 * MS, int(decode_tokens / rng.uniform(25, 70) * NS)))
        start = cursor
        add(index, "prefill", prefill_ns)
        first = cursor
        calls = []
        if index == nested_turn and decode_ns > 3 * NS:
            before = rng.randint(NS // 2, decode_ns // 2)
            tool_ns = int(_loguniform(rng, 0.2, 3.0) * NS)
            add(index, "decode", before)
            calls.append(ToolCall("server_search", ORIGIN + cursor, ORIGIN + cursor + tool_ns,
                                  rng.randint(64, 512), rng.randint(512, 8192)))
            add(index, "tool", tool_ns)
            add(index, "decode", decode_ns - before)
        else:
            add(index, "decode", decode_ns)
        end = cursor
        for position in range(rng.choice((0, 1, 1, 2, 3))):
            if position:
                add(None, "gap", rng.randint(0, 30 * MS))
            tool_ns = int(_loguniform(rng, 0.2, 30.0) * NS)
            calls.append(ToolCall(rng.choice(("bash", "search", "read_file", "send_email")),
                                  ORIGIN + cursor, ORIGIN + cursor + tool_ns,
                                  rng.randint(64, 4096), rng.randint(256, 65536)))
            add(index, "tool", tool_ns)
        hidden = rng.randint(0, decode_tokens)
        turns.append(dict(index=index, start_ns=ORIGIN + start, end_ns=ORIGIN + end,
                          context_tokens=context, prefill_tokens=prefill_tokens,
                          decode_tokens=decode_tokens, hidden_tokens=hidden,
                          first_token_ns=None if rng.random() < 0.1 else ORIGIN + first,
                          tool_calls=calls, logged=index != unlogged_turn))
        context += prefill_tokens + decode_tokens
        add(None, "gap", rng.randint(2 * MS, 400 * MS))
    add(None, "gap", rng.randint(50 * MS, NS))
    # One unlogged tool call per episode (tamper simulation), when any exists.
    tool_turns = [t for t in turns if t["tool_calls"]]
    if tool_turns:
        victim = rng.choice(tool_turns)
        k = rng.randrange(len(victim["tool_calls"]))
        c = victim["tool_calls"][k]
        victim["tool_calls"][k] = ToolCall(c.name, c.start_ns, c.end_ns, c.args_bytes, c.result_bytes,
                                           logged=False)
    # A turn without a first token is one "decode" segment in both readings; the
    # truth below keys on the logged phase list, which is unchanged by that.

    # ---- true power
    base = {"gap": rng.uniform(55, 75), "tool": rng.uniform(75, 110)}
    ripple = {"gap": 0.05, "tool": 0.05, "prefill": 0.02, "decode": 0.04}
    bounds = [p[2] for p in phases] + [phases[-1][3]]
    lengths = [b - a for a, b in zip(bounds, bounds[1:])]
    actual = [bounds[0]]
    for i in range(1, len(bounds) - 1):
        room = min(lengths[i - 1], lengths[i]) // 3
        shift = rng.randint(-2 * MS, 6 * MS) if lag else 0
        actual.append(bounds[i] + max(-room, min(room, shift)))
    actual.append(bounds[-1])
    knots = [(-30 * NS, base["gap"] * shape.scale)]
    previous_level = base["gap"]
    for i, (owner, kind, _, _) in enumerate(phases):
        a, b = actual[i], actual[i + 1]
        if kind == "prefill":
            level0 = rng.uniform(330, 430)
            level1 = level0
        elif kind == "decode":
            level0 = rng.uniform(210, 300)
            level1 = level0 * (1 + rng.uniform(0, 0.08) * min(1.0, (b - a) / (20 * NS)))
        else:
            level0 = level1 = base[kind] * rng.uniform(0.97, 1.03)
        slew = min(rng.randint(MS // 2, 4 * MS), (b - a) // 3)
        if a > knots[-1][0]:
            knots.append((a, previous_level * shape.scale))
        if slew > 0 and a + slew < b:
            knots.append((a + slew, level0 * shape.scale))
        x = a + slew
        while True:
            x += rng.randint(5 * MS, 40 * MS)
            if x >= b - MS:
                break
            frac = (x - a) / (b - a)
            level = (level0 + (level1 - level0) * frac) * (1 + rng.uniform(-1, 1) * ripple[kind])
            knots.append((x, level * shape.scale))
        if b > knots[-1][0]:
            knots.append((b, level1 * shape.scale))
        previous_level = level1
    knots.append((cursor + 30 * NS, base["gap"] * shape.scale))
    truth = Truth(knots)

    # ---- sensor samples, in the trace's own clock
    period, jitter = shape.period_ns, shape.jitter_ns
    phase0 = rng.randint(0, period - 1)  # grid phase independent of every boundary
    lo = -NS if partial != "late" else 3_300 * MS
    hi = cursor + NS if partial != "early" else cursor - 2_700 * MS
    grid = range(lo + phase0, hi, period)
    times = sorted({t + (rng.randint(-jitter, jitter) if jitter else 0) for t in grid})
    if shape.window_ns is not None:
        # The first window must start no earlier than ``lo`` for the coverage reading.
        times = [t for t in times if t - shape.window_ns >= lo - period]
    values = []
    reset_at = None
    if shape.unit == "J_cumulative" and seed % 3 == 1:
        k = len(times) // 2
        reset_at = rng.randint(times[k - 1] + 1, times[k] - 1)
    q = shape.resolution
    for t in times:
        if shape.unit == "J_cumulative":
            if reset_at is not None and t > reset_at:
                value = truth.integral(reset_at, t)
            else:
                value = 3_200_000.0 + truth.integral(times[0], t)  # driver baseline
            # Integer mJ, truncated (the driver reports whole mJ).
            values.append(math.floor(value / q) * q)
            continue
        if shape.window_ns is None:
            value = truth.watts(t)
        else:
            value = truth.integral(t - shape.window_ns, t) / (shape.window_ns / NS)
        # Analogue noise of half a quantum, then rounding to the quantum: at most
        # one quantum of error per reading, which is what the resolution term charges.
        noisy = value + rng.uniform(-q / 2, q / 2)
        values.append(round(noisy / q) * q)
    offset = METER_OFFSET_NS if shape.clock == "meter" else 0
    domain = "meter" if shape.clock == "meter" else "host"
    trace = PowerTrace(shape.source, shape.channel, domain,
                       tuple(ORIGIN + t - offset for t in times), tuple(values), shape.unit, period,
                       averaging_window_ns=shape.window_ns,
                       duty_fraction=None if shape.window_ns is None else shape.window_ns / period,
                       resolution=shape.resolution)
    mappings = ()
    if shape.clock == "meter":
        mappings = (ClockMapping("meter", "host", offset, shape.clock_half_width_ns,
                                 "synthetic round-trip bracket"),)
    episode = Episode(f"r3-{shape.name}-{seed}", "shade/synthetic", "sabotage", "local-open-weight",
                      "mock:local-vllm", seed, "host", ORIGIN, ORIGIN + cursor,
                      tuple(Turn(tool_calls=tuple(t.pop("tool_calls")), **t) for t in turns),
                      power_traces=(trace,), clock_mappings=mappings,
                      flags=("synthetic.round3",))
    meta = dict(phases=phases, reset_at=reset_at, offset=offset, n_turns=n_turns)
    return episode, truth, meta


# ---------------------------------------------------------------- independent C2 + reset terms

def _trace_domain(episode):
    trace = episode.power_traces[0]
    offset = episode.clock_mappings[0].offset_ns if episode.clock_mappings else 0
    return trace, offset


def c2_extra(trace, offset, a, b):
    """Fix round 2's C2 window terms, from the brief text, in the trace's clock.

    (a) every duty gap [t_(k-1), t_k - w] overlapping [a, b] adds
        |P_k - P_(k-1)| x (gap length inside [a, b]) / 2;
    (b) every end strictly inside a window (t_k - w < end < t_k) adds
        (max - min of the means P_(k-1), P_k, P_(k+1) that exist) x w / 4.
    """
    w = trace.averaging_window_ns
    if trace.unit != "W" or not w or w <= 0:
        return 0.0
    t, p = trace.t_ns, trace.values
    a, b = a - offset, b - offset
    terms = []
    for k in range(1, len(t)):
        g0, g1 = t[k - 1], t[k] - w
        inside = min(b, g1) - max(a, g0)
        if g1 > g0 and inside > 0:
            terms.append(abs(p[k] - p[k - 1]) * (inside / NS) / 2)
    for end in (a, b):
        for k in range(len(t)):
            if t[k] - w < end < t[k]:
                near = [p[j] for j in (k - 1, k, k + 1) if 0 <= j < len(p)]
                terms.append((max(near) - min(near)) * (w / NS) / 4)
                break
    return math.fsum(terms)


def twin_interpolation(trace, offset, a, b):
    """The twin's own interpolation term (half the hold-vs-line difference) on [a, b]."""
    if trace.unit == "J_cumulative":
        series, _ = twin._unwrapped(trace.values)
        return twin._interpolation_term(trace.t_ns, series, a - offset, b - offset, cumulative=True)
    return twin._interpolation_term(trace.t_ns, trace.values, a - offset, b - offset, cumulative=False)


def reset_extra(trace, offset, a, b):
    """Lane's counter-restart sensitivity, recomputed: for each poll whose reading
    decreased, (overlap of that poll with [a, b]) x (peak step power of the trace)."""
    if trace.unit != "J_cumulative":
        return 0.0
    t, v = trace.t_ns, trace.values
    series, _ = twin._unwrapped(v)
    peak = max(abs(series[k + 1] - series[k]) / ((t[k + 1] - t[k]) / NS) for k in range(len(t) - 1))
    a, b = a - offset, b - offset
    terms = []
    for k in range(len(t) - 1):
        if v[k + 1] < v[k]:
            overlap = min(b, t[k + 1]) - max(a, t[k])
            if overlap > 0:
                terms.append(overlap / NS * peak)
    return math.fsum(terms)


SHARED_FLAGS = {  # lane name -> twin name, for flags both define with one meaning
    "trace.partial_coverage": "trace.partial_coverage",
    "duty.uncovered": "duty.uncovered",
    "counter.wrap": "counter.wrap",
    "clock.uncertainty_missing": "half_width.missing.clock",
    "resolution.missing": "half_width.missing.resolution",
}
SHARED_EPISODE_FLAGS = {
    "trace.ambiguous": "trace.ambiguous",
    "trace.missing": "trace.missing",
    "tool.overlap": "tool.overlap",
    "tool.outside_episode": "tool.outside_episode",
    "turn.overlap": "turn.overlap",
    "turn.no_first_token": "turn.no_first_token",
}


def duty_fraction(method):
    base, _, companion = method.partition(";")
    if not companion:
        return base, 0.0
    return base, float(companion.split("=", 1)[1])


@unittest.skipIf(lane is None, "lane A4 module not on this branch")
class TwinAgreementRound3(unittest.TestCase):
    """Lane and twin on the same round-3 worlds, under the orchestrator's bars."""

    def assert_joules(self, lane_e, twin_e, label):
        widths = [w for w in (lane_e.half_width_j, twin_e.half_width_j) if 0 < w < math.inf]
        if len(widths) == 2:
            bar = 0.01 * min(widths)  # orchestrator: 1% of the smaller printed half-width
        else:
            scale = max(abs(lane_e.joules), abs(twin_e.joules))
            bar = 1e-6 * scale if scale >= 1 else 1e-6  # orchestrator: no printed width
        self.assertLessEqual(abs(lane_e.joules - twin_e.joules), bar,
                             f"{label}: joules lane {lane_e.joules!r} twin {twin_e.joules!r}")

    def assert_rel(self, actual, expected, label):
        scale = max(abs(actual), abs(expected))
        bar = 1e-6 * scale if scale >= 1 else 1e-6  # orchestrator: no printed width
        self.assertLessEqual(abs(actual - expected), bar, f"{label}: {actual!r} vs {expected!r}")

    def compare_world(self, episode, idle):
        source, channel = episode.power_traces[0].source, episode.power_traces[0].channel
        lane_r = lane.attribute_episode(episode, source=source, channel=channel, idle_watts=idle)
        twin_r = twin.attribute_episode(episode, source=source, channel=channel, idle_watts=idle)
        tag = f"{episode.episode_id} idle {idle}"
        self.assertEqual([(s.turn, s.kind, s.start_ns, s.end_ns) for s in lane_r.segments],
                         [(s.turn, s.kind, s.start_ns, s.end_ns) for s in twin_r.segments], tag)
        want = {SHARED_EPISODE_FLAGS[f] for f in lane_r.flags if f in SHARED_EPISODE_FLAGS}
        got = {f for f in twin_r.flags if f in SHARED_EPISODE_FLAGS.values()}
        self.assertEqual(want, got, tag + " episode flags")
        trace, offset = _trace_domain(episode)
        pairs = [("total", episode.start_ns, episode.end_ns, lane_r.total, twin_r.total)]
        pairs += [(f"segment {i} {ls.kind}", ls.start_ns, ls.end_ns, ls.energy, ts.energy)
                  for i, (ls, ts) in enumerate(zip(lane_r.segments, twin_r.segments))]
        for label, a, b, le, te in pairs:
            label = f"{tag} {label}"
            self.assert_joules(le, te, label)
            expected_hw = (te.half_width_j + twin_interpolation(trace, offset, a, b)
                           + c2_extra(trace, offset, a, b) + reset_extra(trace, offset, a, b))
            self.assert_rel(le.half_width_j, expected_hw, label + " half-width")
            lane_base, lane_f = duty_fraction(le.method)
            twin_base, twin_f = duty_fraction(te.method)
            self.assertEqual(lane_base, twin_base, label)
            self.assert_rel(lane_f, twin_f, label + " duty fraction")
            self.assertEqual({SHARED_FLAGS[f] for f in le.flags if f in SHARED_FLAGS},
                             {f for f in te.flags if f in SHARED_FLAGS.values()}, label + " flags")
        return len(pairs)

    def test_full_coverage_worlds_agree(self):
        compared = 0
        for shape in SHAPES:
            seeds = range(5) if shape.name == "ina3221" else range(10)  # 1 kHz worlds are slow
            for seed in seeds:
                for lag in (True, False):
                    episode, truth, _ = build_world(seed, shape, lag=lag)
                    gap_watts = truth.p[0]
                    for idle in (0.0, gap_watts):
                        with self.subTest(shape=shape.name, seed=seed, lag=lag, idle=idle):
                            compared += self.compare_world(episode, idle)
        self.assertGreater(compared, 1000)

    def test_partial_coverage_gross_joules_agree(self):
        for shape in SHAPES:
            for seed in range(3):
                for partial in ("late", "early"):
                    episode, _, _ = build_world(seed + 100, shape, partial=partial)
                    source, channel = shape.source, shape.channel
                    lane_r = lane.attribute_episode(episode, source=source, channel=channel)
                    twin_r = twin.attribute_episode(episode, source=source, channel=channel)
                    with self.subTest(shape=shape.name, seed=seed, partial=partial):
                        self.assertEqual([(s.kind, s.start_ns, s.end_ns) for s in lane_r.segments],
                                         [(s.kind, s.start_ns, s.end_ns) for s in twin_r.segments])
                        for ls, ts in zip((lane_r.total, *[s.energy for s in lane_r.segments]),
                                          (twin_r.total, *[s.energy for s in twin_r.segments])):
                            self.assert_joules(ls, ts, f"{episode.episode_id} {partial}")
                            self.assertEqual("trace.partial_coverage" in ls.flags,
                                             "trace.partial_coverage" in ts.flags)

    def test_public_trace_energy_agrees_on_random_intervals(self):
        # Random sub-intervals, including ones that start or end outside the trace,
        # through the public trace_energy of each (gross joules, idle 0).
        for shape in SHAPES:
            episode, _, _ = build_world(7, shape, n_turns=4)
            trace = episode.power_traces[0]
            mapping = episode.clock_mappings[0] if episode.clock_mappings else None
            rng = random.Random(99)
            for _ in range(200):
                a = episode.start_ns + rng.randint(-2 * NS, episode.end_ns - episode.start_ns)
                b = a + rng.choice((rng.randint(0, 10 * MS), rng.randint(0, 5 * NS)))
                le = lane.trace_energy(trace, a, b, mapping=mapping)
                te = twin.trace_energy(trace, a, b, mapping=mapping)
                with self.subTest(shape=shape.name, a=a, b=b):
                    self.assert_joules(le, te, f"{shape.name} [{a}, {b}]")


if __name__ == "__main__":
    unittest.main()
