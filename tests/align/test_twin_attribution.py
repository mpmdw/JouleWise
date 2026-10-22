"""Twin agreement for lane A4 (``joulewise/align/attribution.py``), review round 2.

Runs the lane's public functions and the independent twin
(``tests/align/twins/attribution_twin.py``) on the same seeded,
production-shaped worlds and compares every number they both define the same
way. Written by the executing reviewers (round 1, rewritten in round 2);
neither implementation's author wrote it.

Worlds (round 2). Agent episodes recorded the way the runner lane records them
(``joulewise/align/runner.py``): a Turn is one model call [start, end] with its
first token inside, and its 0-3 tool calls run back to back AFTER the call
returns, before the next turn. One world in three instead nests one tool call
inside the turn's decode (a server-side tool), so both placements run. 24-36
turns per episode, prefill time from 300-6000 new tokens at 3000-12000 tok/s
plus a context-length term, decode from 20-900 tokens at 25-60 tok/s, tools
0.2-30 s log-uniform, client gaps 5-400 ms, one unlogged turn and one unlogged
tool call per episode. Phase times are integer ns, never aligned to any sensor
grid. True power is piecewise linear: each phase has a level, a 2-8 ms slew at
its start, and a ripple knot every 4-30 ms (decode +-8%, prefill +-3%, tool and
gap +-5%), so the integral over any interval is exact and window means and duty
gaps meet real within-phase structure. Four sensor shapes sample it:

- INA3221-like points at 1 kHz with +-50 us timestamp jitter; quantum 0.04 W
  (40 uV shunt LSB / 5 mOhm * 5 V); meter clock, 1 ms mapping half-width.
- NVML power: a 25 ms mean ending at each 100 ms poll, +-2 ms poll jitter,
  integer mW (0.001 W); host clock, no ClockMapping (as the NVML lane records).
- powermetrics-like whole 100 ms window means, back to back (no jitter, since
  one averaging_window_ns cannot describe jittered windows), integer mW;
  its own clock, 1 ms mapping half-width.
- NVML energy counter: integer mJ (0.001 J) since driver load, 100 ms polls
  with +-2 ms jitter, host clock; one world in four has a driver reset
  mid-episode (the counter restarts from 0 halfway through a poll interval).

Bars (set by the orchestrator for this review, not chosen here):
- ``joules`` has a printed half-width: the two implementations agree within 1%
  of the smaller of their two half-widths for that estimate. Each such bar is
  also checked to sit above 1e6 ulp of the estimate's magnitude (float noise),
  so it is a real agreement bar.
- Outputs with no printed uncertainty (the half-widths themselves, duty
  fractions): 1e-6 relative, or 1e-6 absolute in the output's unit when the
  value is below 1.
- Segment boundaries, turn indices, kinds and base method names are integers
  or strings: compared exactly. Flag presence is compared only for flags both
  sides define with the same meaning.

Readings that still differ after fix round 1 (the comparison is restricted to
where they coincide, and each divergence is named):

READING-C (partial coverage, unchanged from round 1): the lane subtracts idle
  and charges resolution over the whole requested interval and takes the clock
  term at the requested ends; the twin uses the covered overlap. Partial
  coverage is compared on gross joules (idle 0) only.
READING-D (format): lane ``;duty.uncovered_fraction=<f>`` over the requested
  interval, twin ``;duty.uncovered=<f>`` over the overlap; equal under full
  coverage, where they are compared.
READING-F (counter reset): both restart from zero (same joules). The lane adds
  a sensitivity term (reset-interval overlap x observed peak step power); the
  twin adds none. On reset worlds the half-width difference must equal that
  term, recomputed here independently.
READING-G (degenerate traces): with no matching trace the lane prints
  (0 J, inf, its base method) and the twin (0 J, 0, "none"); joules compared.

READING-A, -B and -E of round 1 are closed: the lane now takes the window
interpolation term on raw sample brackets, clips both end terms to the query,
and includes the held counter's jump, so those half-widths are compared.
"""

from __future__ import annotations

import bisect
import math
import random
import unittest
from dataclasses import dataclass, replace

from joulewise.align.records import ClockMapping, Episode, PowerTrace, ToolCall, Turn
from tests.align.twins import attribution_twin as twin

try:  # The lane module exists only once the lane branch is merged with this one.
    from joulewise.align import attribution as lane
except ImportError:  # pragma: no cover - twin branch alone
    lane = None

NS = 1_000_000_000  # ns per second, by definition
MS = 1_000_000  # ns per millisecond, by definition
US = 1_000  # ns per microsecond, by definition
SEEDS = range(10)  # ten worlds per sensor shape, each about 150-250 segments


# ---------------------------------------------------------------- truth timeline

class Truth:
    """Piecewise-linear true power through knots (t_ns, watts), t strictly increasing."""

    def __init__(self, knots):
        self.t = [k[0] for k in knots]
        self.p = [k[1] for k in knots]
        # Cumulative energy at each knot, by compensated (Neumaier) summation: the running
        # value errs by about 2 eps x the sum of |terms| (2 * 1.1e-16 * 4e5 J = 1e-10 J at
        # the largest world), against printed half-widths no smaller than one sensor
        # quantum over the shortest 5 ms segment (0.001 W * 0.005 s = 5e-6 J).
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

    def _F(self, x):
        """Energy from the first knot to x (J), flat extension outside the knots."""
        if x <= self.t[0]:
            return self.p[0] * ((x - self.t[0]) / NS)
        if x >= self.t[-1]:
            return self.cum[-1] + self.p[-1] * ((x - self.t[-1]) / NS)
        i = bisect.bisect_right(self.t, x) - 1
        return self.cum[i] + 0.5 * (self.p[i] + self.watts(x)) * ((x - self.t[i]) / NS)

    def integral(self, x, y):
        """Integral in J over [x, y] (ns)."""
        return 0.0 if y <= x else self._F(y) - self._F(x)


@dataclass(frozen=True)
class Shape:
    source: str
    channel: str
    unit: str
    period_ns: int
    window_ns: int | None
    resolution: float
    jitter_ns: int
    levels: tuple[float, float, float, float]  # gap, prefill, decode, tool (W)
    host_clock: bool


SHAPES = (
    # INA3221: 1 kHz rail samples; 40 uV shunt LSB / 5 mOhm * 5 V = 0.04 W quantum.
    Shape("ina3221", "VDD_IN", "W", MS, None, 0.04, 50 * US, (4.0, 22.0, 15.0, 6.0), False),
    # NVML power (A100/H100): 25 ms averaged slice of each 100 ms; integer mW.
    Shape("nvml_power", "gpu0", "W", 100 * MS, 25 * MS, 0.001, 2 * MS, (70.0, 330.0, 250.0, 85.0), True),
    # powermetrics-like: whole 100 ms window means, printed in mW.
    Shape("powermetrics", "package", "W", 100 * MS, 100 * MS, 0.001, 0, (9.0, 48.0, 32.0, 13.0), False),
    # NVML energy counter: integer mJ since driver load, polled every 100 ms.
    Shape("nvml_energy", "gpu0", "J_cumulative", 100 * MS, None, 0.001, 2 * MS,
          (70.0, 330.0, 250.0, 85.0), True),
)


def build_world(seed, shape, *, inside_tools=None, counter_reset=None, trace_shift_ns=0,
                n_turns=None):
    """One production-shaped episode, its exact truth, and the expected tiling.

    Returns (episode, truth, expected) where expected is the list of
    (turn, kind, start_ns, end_ns) the construction itself defines.
    """
    rng = random.Random(f"r2-{shape.source}-{seed}")
    inside_tools = (seed % 3 == 2) if inside_tools is None else inside_tools
    counter_reset = (shape.unit == "J_cumulative" and seed % 4 == 1) if counter_reset is None \
        else counter_reset
    n_turns = rng.randint(24, 36) if n_turns is None else n_turns
    origin = 10**18 + rng.randrange(NS)  # an epoch where binary64 cannot hold single ns
    gain = rng.uniform(0.9, 1.1)
    gap_w, prefill_w, decode_w, tool_w = (lvl * gain for lvl in shape.levels)
    ripple = {"gap": 0.05, "prefill": 0.03, "decode": 0.08, "tool": 0.05}
    level = {"gap": gap_w, "prefill": prefill_w, "decode": decode_w, "tool": tool_w}

    phases = []  # (turn, kind, start, end) in time order, contiguous
    cursor = origin

    def phase(turn, kind, duration):
        nonlocal cursor
        if duration > 0:
            phases.append((turn, kind, cursor, cursor + duration))
            cursor += duration

    lead = 5 * shape.period_ns + (shape.window_ns or 0)
    phase(None, "lead", lead)  # idle before the episode, so the sensor covers its start
    start_ns = cursor
    phase(None, "gap", rng.randint(5 * MS, 400 * MS))
    turns = []
    context = rng.randint(800, 3000)
    unlogged_turn = rng.randrange(n_turns)
    unlogged_tool_turn = rng.randrange(n_turns - 1)
    for index in range(n_turns):
        new_tokens = rng.randint(300, 6000)
        decode_tokens = rng.randint(20, 900)
        prefill_ns = int((new_tokens / rng.uniform(3000, 12000) + context * 2e-6) * NS)
        decode_ns = int(decode_tokens / rng.uniform(25, 60) * NS)
        t_start = cursor
        phase(index, "prefill", prefill_ns)
        first = cursor
        last = index == n_turns - 1
        n_calls = 0 if last else rng.choice((1, 1, 1, 2, 2, 3))
        calls = []
        if inside_tools and n_calls:
            split = int(decode_ns * rng.uniform(0.2, 0.8))
            phase(index, "decode", split)
            c0 = cursor
            phase(index, "tool", int(math.exp(rng.uniform(math.log(0.2), math.log(30.0))) * NS))
            calls.append((c0, cursor))
            phase(index, "decode", decode_ns - split)
            t_end = cursor
        else:
            phase(index, "decode", decode_ns)
            t_end = cursor
            for k in range(n_calls):
                # dispatch latency after the call returns, then back-to-back calls
                phase(None, "gap", rng.randint(0, 3 * MS) if k == 0 else rng.randint(0, MS))
                c0 = cursor
                phase(index, "tool", int(math.exp(rng.uniform(math.log(0.2), math.log(30.0))) * NS))
                calls.append((c0, cursor))
        tool_calls = tuple(
            ToolCall("search" if (index + k) % 2 else "exec", c0, c1, rng.randint(64, 1024),
                     rng.randint(256, 16384), logged=not (index == unlogged_tool_turn and k == 0))
            for k, (c0, c1) in enumerate(calls))
        hidden = rng.randint(0, decode_tokens // 2)
        turns.append(Turn(index, t_start, t_end, context, new_tokens, decode_tokens,
                          hidden_tokens=hidden, first_token_ns=first, tool_calls=tool_calls,
                          logged=index != unlogged_turn))
        context += new_tokens + decode_tokens
        if not last:
            phase(None, "gap", rng.randint(5 * MS, 400 * MS))
    phase(None, "gap", rng.randint(5 * MS, 400 * MS))
    end_ns = cursor
    phase(None, "lead", 6 * shape.period_ns)

    # True power knots: a 2-8 ms slew at each phase start, then ripple knots.
    knots = [(phases[0][2], gap_w)]
    for _, kind, a, b in phases:
        base = level["gap" if kind == "lead" else kind]
        amp = ripple["gap" if kind == "lead" else kind]
        t = a + min(rng.randint(2 * MS, 8 * MS), (b - a) // 2)
        while t < b:
            if t > knots[-1][0]:
                knots.append((t, base * (1 + rng.uniform(-amp, amp))))
            t += rng.randint(4 * MS, 30 * MS)
        if b > knots[-1][0]:
            knots.append((b, base * (1 + rng.uniform(-amp, amp))))
    truth = Truth(knots)

    expected = []
    for turn, kind, a, b in phases:
        if kind == "lead":
            continue
        label = (None if kind == "gap" else turn, kind)
        if expected and expected[-1][:2] == label and expected[-1][3] == a and kind == "gap":
            expected[-1] = (label[0], kind, expected[-1][2], b)
        else:
            expected.append((label[0], kind, a, b))

    # Sample grid: random phase, poll jitter (much less than a period, so times stay increasing).
    first_t = start_ns - 3 * shape.period_ns + rng.randrange(shape.period_ns) + trace_shift_ns
    times, t = [], first_t
    while t < end_ns + 3 * shape.period_ns:
        times.append(t + (rng.randint(-shape.jitter_ns, shape.jitter_ns) if shape.jitter_ns else 0))
        t += shape.period_ns
    values = []
    base = rng.uniform(1e5, 5e7)  # an energy counter running since driver load (J)
    reset_at = len(times) // 2 if counter_reset else None
    reset_t = None
    for k, tk in enumerate(times):
        if shape.unit == "J_cumulative":
            if reset_at is not None and k >= reset_at:
                reset_t = times[reset_at - 1] + (times[reset_at] - times[reset_at - 1]) // 2
                value = truth.integral(reset_t, tk)
            else:
                value = base + truth.integral(knots[0][0], tk)
            values.append(math.floor(value / shape.resolution) * shape.resolution)
            continue
        if shape.window_ns is None:
            value = truth.watts(tk)
        else:
            value = truth.integral(tk - shape.window_ns, tk) / (shape.window_ns / NS)
        value += rng.uniform(-shape.resolution / 2, shape.resolution / 2)
        values.append(round(value / shape.resolution) * shape.resolution)
    offset = 0 if shape.host_clock else rng.randint(-10**12, 10**12)
    domain = "host" if shape.host_clock else "meter"
    trace = PowerTrace(shape.source, shape.channel, domain, tuple(tk - offset for tk in times),
                       tuple(values), shape.unit, shape.period_ns,
                       averaging_window_ns=shape.window_ns,
                       duty_fraction=None if shape.window_ns is None else shape.window_ns / shape.period_ns,
                       resolution=shape.resolution)
    mappings = () if shape.host_clock else (
        ClockMapping("meter", "host", offset, MS, "synthetic sync bracket"),)
    episode = Episode(f"r2-{shape.source}-{seed}", "shade/synthetic", "sabotage", "local-8b",
                      "mock:vllm", seed, "host", start_ns, end_ns, tuple(turns),
                      power_traces=(trace,), clock_mappings=mappings, flags=("synthetic",))
    return episode, truth, expected


# ---------------------------------------------------------------- comparison helpers

def no_uncertainty_bar(x, y):
    """1e-6 relative, or 1e-6 absolute in the unit when the value is below 1."""
    scale = max(abs(x), abs(y))
    return 1e-6 * scale if scale >= 1 else 1e-6


def duty_fraction(method):
    base, *fields = method.split(";")
    for item in fields:
        name, value = item.split("=", 1)
        if name in ("duty.uncovered", "duty.uncovered_fraction"):
            return base, float(value)
    return base, 0.0


def reset_term(trace, mapping, a, b):
    """READING-F: the lane's reset sensitivity term, recomputed from the record."""
    off = mapping.offset_ns if mapping is not None else 0
    t = [x + off for x in trace.t_ns]
    v = trace.values
    steps = []
    resets = []
    for k in range(len(t) - 1):
        inc = v[k + 1] if v[k + 1] < v[k] else v[k + 1] - v[k]
        steps.append(abs(inc) / ((t[k + 1] - t[k]) / NS))
        if v[k + 1] < v[k]:
            resets.append((t[k], t[k + 1]))
    peak = max(steps)
    return math.fsum(max(0, min(b, y) - max(a, x)) / NS * peak for x, y in resets)


def segments_of(result):
    return [(s.turn, s.kind, s.start_ns, s.end_ns) for s in result.segments]


@unittest.skipUnless(lane is not None, "joulewise.align.attribution (lane A4) is not on this branch")
class TwinAgreement(unittest.TestCase):

    def compare(self, lane_e, twin_e, *, where, hw_offset=0.0, compare_hw=True, compare_fraction=True,
                idle_j=0.0):
        bar = 0.01 * min(lane_e.half_width_j, twin_e.half_width_j)
        if bar == 0.0 or math.isinf(bar):
            bar = no_uncertainty_bar(lane_e.joules, twin_e.joules)
        else:
            # The 1%-of-half-width bar must clear float noise by 1e6 ulp to mean anything. The
            # noise scale is the gross energy (net joules plus the idle energy subtracted).
            gross = max(abs(lane_e.joules), abs(twin_e.joules)) + abs(idle_j)
            self.assertGreaterEqual(bar, 1e6 * math.ulp(gross),
                                    f"{where}: half-width {bar * 100!r} J is below float noise")
        self.assertLessEqual(abs(lane_e.joules - twin_e.joules), bar,
                             f"{where}: joules lane {lane_e.joules!r} twin {twin_e.joules!r}")
        lane_base, lane_f = duty_fraction(lane_e.method)
        twin_base, twin_f = duty_fraction(twin_e.method)
        self.assertEqual(lane_base, twin_base, where)
        if compare_fraction:  # READING-D: the denominators differ only under partial coverage
            self.assertLessEqual(abs(lane_f - twin_f), no_uncertainty_bar(lane_f, twin_f), where)
        for flag in ("duty.uncovered", "trace.partial_coverage", "counter.wrap"):
            self.assertEqual(flag in lane_e.flags, flag in twin_e.flags, f"{where}: {flag}")
        if compare_hw:
            lane_hw = lane_e.half_width_j - hw_offset
            self.assertLessEqual(abs(lane_hw - twin_e.half_width_j),
                                 no_uncertainty_bar(lane_hw, twin_e.half_width_j),
                                 f"{where}: half-width lane {lane_e.half_width_j!r} (-{hw_offset!r}) "
                                 f"twin {twin_e.half_width_j!r}")

    def run_world(self, shape, seed, *, idle_watts=0.0, **world_kw):
        episode, _, expected = build_world(seed, shape, **world_kw)
        lane_r = lane.attribute_episode(episode, source=shape.source, channel=shape.channel,
                                        idle_watts=idle_watts)
        twin_r = twin.attribute_episode(episode, source=shape.source, channel=shape.channel,
                                        idle_watts=idle_watts)
        # Tiling is integer: exact against the construction and against the twin.
        self.assertEqual(segments_of(lane_r), expected, f"{shape.source} seed {seed}")
        self.assertEqual(segments_of(lane_r), segments_of(twin_r))
        trace = episode.power_traces[0]
        mapping = episode.clock_mappings[0] if episode.clock_mappings else None
        pairs = [(lane_r.total, twin_r.total, episode.start_ns, episode.end_ns, "total")]
        pairs += [(ls.energy, ts.energy, ls.start_ns, ls.end_ns, f"segment {i} {ls.kind}")
                  for i, (ls, ts) in enumerate(zip(lane_r.segments, twin_r.segments))]
        for lane_e, twin_e, a, b, label in pairs:
            offset = reset_term(trace, mapping, a, b) if "counter.wrap" in lane_e.flags else 0.0
            self.compare(lane_e, twin_e, hw_offset=offset, idle_j=idle_watts * (b - a) / NS,
                         where=f"{shape.source} seed {seed} idle {idle_watts} {label}")
        self.assertNotIn("trace.partial_coverage", lane_r.total.flags)
        return len(pairs)

    def test_full_coverage_worlds_agree(self):
        for shape in SHAPES:
            compared = 0
            # 1 kHz worlds hold about 1e6 samples each; three seeds keep the run short.
            for seed in (SEEDS if shape.period_ns >= 100 * MS else range(3)):
                for idle in (0.0, shape.levels[0]):
                    with self.subTest(sensor=shape.source, seed=seed, idle=idle):
                        compared += self.run_world(shape, seed, idle_watts=idle)
            print(f"twin agreement r2 {shape.source}: {compared} estimates compared on joules "
                  f"and half-width")

    def test_partial_coverage_gross_agrees(self):
        # READING-C: the sensor starts 20 s after the episode does; gross joules (idle 0).
        for shape in SHAPES:
            for seed in range(3):
                with self.subTest(sensor=shape.source, seed=seed):
                    episode, _, _ = build_world(seed, shape, trace_shift_ns=20 * NS, counter_reset=False)
                    lane_r = lane.attribute_episode(episode, source=shape.source, channel=shape.channel)
                    twin_r = twin.attribute_episode(episode, source=shape.source, channel=shape.channel)
                    self.assertEqual(segments_of(lane_r), segments_of(twin_r))
                    self.assertIn("trace.partial_coverage", lane_r.total.flags)
                    for ls, ts in zip((lane_r.total,) + tuple(s.energy for s in lane_r.segments),
                                      (twin_r.total,) + tuple(s.energy for s in twin_r.segments)):
                        self.compare(ls, ts, compare_hw=False, compare_fraction=False,
                                     where=f"{shape.source} seed {seed} late")

    def test_missing_trace_joules_agree(self):
        # READING-G: no trace matches the requested channel.
        episode, _, _ = build_world(0, SHAPES[1])
        lane_r = lane.attribute_episode(episode, source="nvml_power", channel="gpu7", idle_watts=70.0)
        twin_r = twin.attribute_episode(episode, source="nvml_power", channel="gpu7", idle_watts=70.0)
        self.assertEqual(segments_of(lane_r), segments_of(twin_r))
        self.assertIn("trace.missing", lane_r.flags)
        for ls, ts in zip((lane_r.total,) + tuple(s.energy for s in lane_r.segments),
                          (twin_r.total,) + tuple(s.energy for s in twin_r.segments)):
            self.assertEqual((ls.joules, ts.joules), (0.0, 0.0))  # both define it as exactly zero
            self.assertTrue(math.isinf(ls.half_width_j))


@unittest.skipUnless(lane is not None, "joulewise.align.attribution (lane A4) is not on this branch")
class RoundOneRegressions(unittest.TestCase):
    """Round-1 findings that changed a number (B1, M1); fixed in e3db70aeb, kept as regressions."""

    def test_runner_recorded_tool_calls_get_tool_segments(self):
        # Runner-recorded calls lie after their Turn ends; each must be its own "tool" segment
        # with the owning turn's index (brief: "each tool call as tool").
        for shape in SHAPES[:2]:
            episode, _, _ = build_world(0, shape, inside_tools=False)
            lane_r = lane.attribute_episode(episode, source=shape.source, channel=shape.channel)
            calls = sorted((c.start_ns, c.end_ns, t.index) for t in episode.turns for c in t.tool_calls)
            tools = [(s.start_ns, s.end_ns, s.turn) for s in lane_r.segments if s.kind == "tool"]
            self.assertEqual(tools, calls)

    def test_counter_reset_energy_within_its_half_width_of_truth(self):
        shape = SHAPES[3]
        for seed in range(4):
            episode, truth, _ = build_world(seed, shape, counter_reset=True)
            lane_r = lane.attribute_episode(episode, source=shape.source, channel=shape.channel)
            exact = truth.integral(episode.start_ns, episode.end_ns)
            self.assertIn("counter.wrap", lane_r.flags)
            self.assertTrue(all(s.energy.joules >= 0 for s in lane_r.segments))
            # The restart loses the pre-reset part of one poll step; the reset sensitivity term
            # (one poll at the observed peak) must cover it plus the ordinary end terms.
            self.assertLessEqual(abs(lane_r.total.joules - exact), lane_r.total.half_width_j,
                                 f"seed {seed}: lane total {lane_r.total.joules!r} truth {exact!r}")


if __name__ == "__main__":
    unittest.main()
