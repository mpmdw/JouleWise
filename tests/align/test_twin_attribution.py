"""Twin agreement for lane A4 (``joulewise/align/attribution.py``).

Runs the lane's public functions and the independent twin
(``tests/align/twins/attribution_twin.py``) on the same seeded,
production-shaped worlds and compares every number they both define the same
way. Written by the round-1 executing reviewer; neither implementation's
author wrote it.

Worlds. Twenty-turn agent episodes with randomly timed phases (integer ns,
never aligned to the sensor grid): prefill from 200-4000 prompt tokens at
2000-8000 tokens/s, decode from 20-600 tokens at 30-60 tokens/s, one tool call
per turn of 0.2-30 s (log-uniform), inter-turn gaps of 5-700 ms. The true power
is piecewise linear (a level per phase, a ramp across each decode), so its
integral over any interval is known exactly. Four sensor shapes sample it:
INA3221-like points at 1 kHz, NVML-power-like 25 ms window means every 100 ms,
powermetrics-like whole 100 ms window means, and an NVML-energy-like mJ
counter every 100 ms; each with +-2 ms sample-time jitter, a random grid
phase, bounded noise and quantisation, in a foreign clock domain with a large
integer offset.

Bars (set by the orchestrator for this review, not chosen here):
- ``joules`` has a printed half-width: the two implementations agree within 1%
  of the smaller of their two half-widths for that estimate.
- Outputs with no printed uncertainty (half-widths themselves, duty fractions):
  1e-6 relative, or 1e-6 absolute in the output's unit when below 1.
- Segment boundaries, turn indices, kinds and base method names are integers
  or strings: compared exactly.

Where the two read an open sentence of the brief differently, the comparison
is restricted to the domain where the readings coincide, and the divergence is
named (READING-x below). Two divergences are lane defects found in review, not
readings; ``LaneDefectRepro`` holds them and fails until they are fixed:
tool calls the runner records after the model call returns are dropped, and a
counter reset produces a negative energy far outside its own half-width.

READING-A (half-width, window sensors): the lane takes the interpolation term
  on its own reconstruction spans (constant window means and linear gap
  bridges); the twin takes it on the raw sample intervals. Half-widths of
  window_average_W estimates are therefore not compared.
READING-B (half-width, both ends inside one sample interval): the lane's start
  term covers [t0, span end] and its stop term [span start, t1] even when the
  other end lies inside the same span; the twin clips each to [t0, t1].
  Such estimates are excluded from the half-width comparison and counted.
READING-C (partial coverage): the lane subtracts idle power and charges the
  resolution term over the whole requested interval and takes the clock term at
  the requested ends; the twin uses the covered overlap for all three. Partial
  coverage is compared on gross joules (idle 0) only.
READING-D (format): the lane writes ``;duty.uncovered_fraction=<f>`` with f over
  the requested interval; the twin ``;duty.uncovered=<f>`` over the overlap.
  With full coverage the two fractions are the same number and are compared.
READING-E (half-width, counter start end): for a cumulative counter the lane
  charges half the linear increment over [t0, next sample]; the twin half the
  increment over [previous sample, t0] (hold minus line with the hold's jump at
  the next sample included). Hand case: 0/100/300 J at 0/1/2 s, [0.25 s, 1.5 s]
  gives 87.5 J (lane) and 62.5 J (twin); both give 175 J. Counter half-widths
  are not compared.
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
SEEDS = range(8)  # eight worlds per sensor shape; each has about 100 segments


# ---------------------------------------------------------------- truth timeline

class Truth:
    """Piecewise-linear true power: contiguous pieces (start_ns, end_ns, w_start, w_end)."""

    def __init__(self, pieces):
        self.pieces = pieces
        self.starts = [p[0] for p in pieces]

    def watts(self, t):
        i = min(max(bisect.bisect_right(self.starts, t) - 1, 0), len(self.pieces) - 1)
        a, b, pa, pb = self.pieces[i]
        return pa + (pb - pa) * ((t - a) / (b - a))

    def integral(self, x, y):
        terms = []
        i = max(bisect.bisect_right(self.starts, x) - 1, 0)
        for a, b, pa, pb in self.pieces[i:]:
            if a >= y:
                break
            lo, hi = max(a, x), min(b, y)
            if hi > lo:
                p_lo = pa + (pb - pa) * ((lo - a) / (b - a))
                p_hi = pa + (pb - pa) * ((hi - a) / (b - a))
                terms.append(0.5 * (p_lo + p_hi) * ((hi - lo) / NS))
        return math.fsum(terms)


@dataclass(frozen=True)
class Shape:
    source: str
    channel: str
    unit: str
    period_ns: int
    window_ns: int | None
    resolution: float
    levels: tuple[float, float, float, float]  # gap, prefill, decode, tool (W)


SHAPES = (
    # INA3221: 1 kHz instantaneous rail samples; 40 uV shunt LSB / 5 mOhm * 5 V = 0.04 W quantum.
    Shape("ina3221", "VDD_IN", "W", MS, None, 0.04, (3.0, 18.0, 12.0, 5.0)),
    # NVML power: a 25 ms averaged slice of each 100 ms; NVML reports integer mW.
    Shape("nvml_power", "gpu0", "W", 100 * MS, 25 * MS, 0.001, (70.0, 330.0, 240.0, 90.0)),
    # powermetrics-like: whole 100 ms window means, printed in mW.
    Shape("powermetrics", "package", "W", 100 * MS, 100 * MS, 0.001, (8.0, 45.0, 30.0, 12.0)),
    # NVML energy counter: integer mJ, polled every 100 ms.
    Shape("nvml_energy", "gpu0", "J_cumulative", 100 * MS, None, 0.001, (70.0, 330.0, 240.0, 90.0)),
)


def build_world(seed, shape, *, tools="inside", trace_starts_late_ns=0, same_domain=False,
                counter_reset=False, clock_uncertainty_ns=MS):
    """One production-shaped episode and its exact truth.

    tools="inside": each tool call lies inside its turn (prefill, decode, tool, decode).
    tools="runner": each turn is one model call and its tool runs after the call
    returns, before the next turn, as ``joulewise/align/runner.py`` records them.
    """
    rng = random.Random(f"{shape.source}-{seed}-{tools}")
    origin = 10**18 + rng.randrange(NS)  # epochs where binary64 cannot hold single ns
    gap_w, prefill_w, decode_w, tool_w = (lvl * rng.uniform(0.9, 1.1) for lvl in shape.levels)
    pieces = []
    cursor = origin

    def piece(duration, w0, w1):
        nonlocal cursor
        pieces.append((cursor, cursor + duration, w0, w1))
        cursor += duration

    def gap():
        piece(rng.randint(5 * MS, 700 * MS), gap_w, gap_w)

    def decode_piece(duration, frac0, frac1):
        # Decode power ramps up 6% across the decode as the KV cache grows.
        piece(duration, decode_w * (1 + 0.06 * frac0), decode_w * (1 + 0.06 * frac1))

    turns = []
    context = 1024
    pre_lead = 3 * shape.period_ns + (shape.window_ns or 0)
    piece(pre_lead, gap_w, gap_w)  # idle before the episode, so the sensor covers its start
    start_ns = cursor
    gap()
    for index in range(20):
        prefill_tokens = rng.randint(200, 4000)
        decode_tokens = rng.randint(20, 600)
        prefill_ns = int(prefill_tokens / rng.uniform(2000, 8000) * NS)
        decode_ns = int(decode_tokens / rng.uniform(30, 60) * NS)
        tool_ns = int(math.exp(rng.uniform(math.log(0.2), math.log(30.0))) * NS)
        t_start = cursor
        piece(prefill_ns, prefill_w, prefill_w)
        first = cursor
        if tools == "inside":
            split = rng.uniform(0.2, 0.8)
            decode_piece(int(decode_ns * split), 0.0, split)
            c0 = cursor
            piece(tool_ns, tool_w, tool_w)
            c1 = cursor
            decode_piece(decode_ns - int(decode_ns * split), split, 1.0)
            t_end = cursor
        else:
            decode_piece(decode_ns, 0.0, 1.0)
            t_end = cursor
            c0 = cursor + rng.randint(0, 3 * MS)  # tool dispatch latency after the call returns
            if c0 > cursor:
                piece(c0 - cursor, gap_w, gap_w)
            piece(tool_ns, tool_w, tool_w)
            c1 = cursor
        call = ToolCall("search" if index % 2 else "exec", c0, c1, rng.randint(64, 1024),
                        rng.randint(512, 8192), logged=index % 6 != 3)
        turns.append(Turn(index, t_start, t_end, context, prefill_tokens, decode_tokens,
                          hidden_tokens=decode_tokens // 4, first_token_ns=first,
                          tool_calls=(call,), logged=index % 7 != 5))
        context += prefill_tokens + decode_tokens
        gap()
    end_ns = cursor
    piece(4 * shape.period_ns, gap_w, gap_w)  # idle after, so the sensor covers the end
    truth = Truth(pieces)

    # Sample grid: random phase and +-2 ms poll jitter (a quarter period at most, so times stay
    # strictly increasing). Whole-window sensors report back-to-back windows: no jitter there,
    # since one fixed averaging_window_ns could not describe jittered windows.
    whole_window = shape.window_ns is not None and shape.window_ns >= shape.period_ns
    jitter = 0 if whole_window else min(2 * MS, shape.period_ns // 4)
    first_t = start_ns - 2 * shape.period_ns + rng.randrange(shape.period_ns) + trace_starts_late_ns
    times, t = [], first_t
    while t < end_ns + 2 * shape.period_ns:
        times.append(t + rng.randint(-jitter, jitter) if jitter else t)
        t += shape.period_ns
    values = []
    reset_at = len(times) // 2 if counter_reset else None
    base = rng.uniform(1e5, 5e6)  # an energy counter running since driver load
    for k, tk in enumerate(times):
        if shape.unit == "J_cumulative":
            if reset_at is not None and k >= reset_at:
                reset_t = times[reset_at - 1] + (times[reset_at] - times[reset_at - 1]) // 2
                value = truth.integral(reset_t, tk)
            else:
                value = base + truth.integral(pieces[0][0], tk)
            values.append(math.floor(value / shape.resolution) * shape.resolution)
            continue
        if shape.window_ns is None:
            value = truth.watts(tk)
        else:
            value = truth.integral(tk - shape.window_ns, tk) / (shape.window_ns / NS)
        value += rng.uniform(-shape.resolution / 2, shape.resolution / 2)
        values.append(round(value / shape.resolution) * shape.resolution)
    offset = 0 if same_domain else rng.randint(-10**12, 10**12)
    domain = "host" if same_domain else "meter"
    trace = PowerTrace(shape.source, shape.channel, domain, tuple(tk - offset for tk in times),
                       tuple(values), shape.unit, shape.period_ns,
                       averaging_window_ns=shape.window_ns,
                       duty_fraction=None if shape.window_ns is None else shape.window_ns / shape.period_ns,
                       resolution=shape.resolution)
    mappings = () if same_domain else (
        ClockMapping("meter", "host", offset, clock_uncertainty_ns, "synthetic sync bracket"),)
    episode = Episode(f"twin-{shape.source}-{seed}", "shade/synthetic", "sabotage", "local-8b",
                      "mock:vllm", seed, "host", start_ns, end_ns, tuple(turns),
                      power_traces=(trace,), clock_mappings=mappings, flags=("synthetic",))
    return episode, truth


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


def both_ends_in_one_interval(trace, mapping, a, b):
    """READING-B: True when [a, b] (episode domain) lies strictly inside one sample interval."""
    off = mapping.offset_ns if mapping is not None else 0
    times = trace.t_ns
    i = bisect.bisect_right(times, a - off)
    return 0 < i < len(times) and b - off < times[i] and times[i - 1] < a - off


@unittest.skipUnless(lane is not None, "joulewise.align.attribution (lane A4) is not on this branch")
class TwinAgreement(unittest.TestCase):

    def compare_estimates(self, lane_e, twin_e, *, trace, mapping, a, b, compare_hw, where):
        bar = 0.01 * min(lane_e.half_width_j, twin_e.half_width_j)
        if bar == 0.0:
            bar = no_uncertainty_bar(lane_e.joules, twin_e.joules)
        self.assertLessEqual(abs(lane_e.joules - twin_e.joules), bar,
                             f"{where}: joules lane {lane_e.joules!r} twin {twin_e.joules!r}")
        lane_base, lane_f = duty_fraction(lane_e.method)
        twin_base, twin_f = duty_fraction(twin_e.method)
        self.assertEqual(lane_base, twin_base, where)
        self.assertLessEqual(abs(lane_f - twin_f), no_uncertainty_bar(lane_f, twin_f), where)
        self.assertEqual("duty.uncovered" in lane_e.flags, "duty.uncovered" in twin_e.flags, where)
        if compare_hw and not both_ends_in_one_interval(trace, mapping, a, b):
            self.assertLessEqual(abs(lane_e.half_width_j - twin_e.half_width_j),
                                 no_uncertainty_bar(lane_e.half_width_j, twin_e.half_width_j),
                                 f"{where}: half-width lane {lane_e.half_width_j!r} "
                                 f"twin {twin_e.half_width_j!r}")
            return 1
        return 0

    def run_world(self, shape, seed, *, idle_watts=0.0, same_domain=False, episode=None):
        if episode is None:
            episode, _ = build_world(seed, shape, same_domain=same_domain)
        lane_r = lane.attribute_episode(episode, source=shape.source, channel=shape.channel,
                                        idle_watts=idle_watts)
        twin_r = twin.attribute_episode(episode, source=shape.source, channel=shape.channel,
                                        idle_watts=idle_watts)
        self.assertEqual([(s.turn, s.kind, s.start_ns, s.end_ns) for s in lane_r.segments],
                         [(s.turn, s.kind, s.start_ns, s.end_ns) for s in twin_r.segments])
        trace = episode.power_traces[0]
        mapping = episode.clock_mappings[0] if episode.clock_mappings else None
        compare_hw = shape.window_ns is None and shape.unit == "W"  # READING-A, READING-E
        hw_compared = 0
        pairs = [(lane_r.total, twin_r.total, episode.start_ns, episode.end_ns, "total")]
        pairs += [(ls.energy, ts.energy, ls.start_ns, ls.end_ns, f"segment {i} {ls.kind}")
                  for i, (ls, ts) in enumerate(zip(lane_r.segments, twin_r.segments))]
        for lane_e, twin_e, a, b, label in pairs:
            hw_compared += self.compare_estimates(
                lane_e, twin_e, trace=trace, mapping=mapping, a=a, b=b, compare_hw=compare_hw,
                where=f"{shape.source} seed {seed} idle {idle_watts} {label}")
        self.assertNotIn("trace.partial_coverage", lane_r.total.flags)
        return len(pairs), hw_compared

    def test_full_coverage_worlds_agree(self):
        for shape in SHAPES:
            compared = hw_compared = 0
            for seed in SEEDS:
                episode, _ = build_world(seed, shape)
                for idle in (0.0, shape.levels[0]):
                    with self.subTest(sensor=shape.source, seed=seed, idle=idle):
                        n, h = self.run_world(shape, seed, idle_watts=idle, episode=episode)
                        compared += n
                        hw_compared += h
            if shape.window_ns is None and shape.unit == "W":
                # READING-B excludes only estimates inside one sample interval; the
                # episode total always spans many, so at least one per world is compared.
                self.assertGreaterEqual(hw_compared, 2 * len(SEEDS))
            print(f"twin agreement {shape.source}: {compared} estimates compared on joules, "
                  f"{hw_compared} on half-width")

    def test_same_clock_domain_agrees(self):
        # A sensor on the episode's own host clock (NVML or INA3221 polled by the runner).
        for shape in (SHAPES[0], SHAPES[3]):
            for seed in range(3):
                with self.subTest(sensor=shape.source, seed=seed):
                    self.run_world(shape, seed, same_domain=True)

    def test_trace_starting_after_episode_start_gross_agrees(self):
        # READING-C: compare gross joules (idle 0) where the sensor starts 20 s late.
        for shape in SHAPES:
            for seed in range(3):
                with self.subTest(sensor=shape.source, seed=seed):
                    episode, _ = build_world(seed, shape, trace_starts_late_ns=20 * NS)
                    lane_r = lane.attribute_episode(episode, source=shape.source, channel=shape.channel)
                    twin_r = twin.attribute_episode(episode, source=shape.source, channel=shape.channel)
                    self.assertIn("trace.partial_coverage", lane_r.total.flags)
                    self.assertIn("trace.partial_coverage", twin_r.total.flags)
                    for ls, ts in zip((lane_r.total,) + tuple(s.energy for s in lane_r.segments),
                                      (twin_r.total,) + tuple(s.energy for s in twin_r.segments)):
                        bar = 0.01 * min(ls.half_width_j, ts.half_width_j)
                        self.assertLessEqual(abs(ls.joules - ts.joules), bar or no_uncertainty_bar(
                            ls.joules, ts.joules))


@unittest.skipUnless(lane is not None, "joulewise.align.attribution (lane A4) is not on this branch")
class LaneDefectRepro(unittest.TestCase):
    """Review round 1 findings that change a number; each fails until fixed or ruled."""

    def test_runner_recorded_tool_calls_get_tool_segments(self):
        # The runner (joulewise/align/runner.py) records Turn = one model call and
        # starts each ToolCall after the call returns. The brief: "each tool call as tool".
        for shape in (SHAPES[0], SHAPES[1]):
            episode, truth = build_world(0, shape, tools="runner")
            lane_r = lane.attribute_episode(episode, source=shape.source, channel=shape.channel)
            twin_r = twin.attribute_episode(episode, source=shape.source, channel=shape.channel)
            twin_tools = [(s.turn, s.start_ns, s.end_ns) for s in twin_r.segments if s.kind == "tool"]
            lane_tools = [(s.turn, s.start_ns, s.end_ns) for s in lane_r.segments if s.kind == "tool"]
            self.assertEqual(len(twin_tools), 20)
            self.assertEqual(lane_tools, twin_tools, f"{shape.source}: lane has {len(lane_tools)} tool segments")

    def test_counter_reset_energy_within_its_half_width_of_truth(self):
        shape = SHAPES[3]
        episode, truth = build_world(0, shape, counter_reset=True)
        lane_r = lane.attribute_episode(episode, source=shape.source, channel=shape.channel)
        exact = truth.integral(episode.start_ns, episode.end_ns)
        self.assertIn("counter.wrap", lane_r.flags)
        # The reset discards at most one 100 ms poll step at <= 400 W, so a
        # restart-from-zero reading errs by at most 40 J; the printed half-width
        # must at least cover the truth.
        self.assertLessEqual(abs(lane_r.total.joules - exact), lane_r.total.half_width_j + 40.0,
                             f"lane total {lane_r.total.joules!r} truth {exact!r}")


if __name__ == "__main__":
    unittest.main()
