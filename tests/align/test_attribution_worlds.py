"""Production-shaped synthetic sensor worlds, through records and attribution.

The oracle integrates independent rectangular true-power intervals. It never
calls the attribution reconstruction or the legacy reducer. Sensor noise is
bounded by half one sensor quantum before rounding; total measurement error
therefore stays within one quantum per observation. Seed coverage below is
empirical coverage of these stated worlds, not a universal confidence level.
"""

from bisect import bisect_right
from dataclasses import dataclass, replace
import json
import math
import random
import sys
import unittest

from joulewise.align.attribution import attribute_episode, trace_energy
from joulewise.align.records import ClockMapping, Episode, PowerTrace, ToolCall, Turn, from_json, to_json


NS = 1_000_000_000  # Definition of a second in nanoseconds.
ORIGIN = 10**18  # Exercise epochs whose float representation loses nanoseconds.


@dataclass(frozen=True)
class Sensor:
    source: str
    channel: str
    period_ns: int
    window_ns: int | None
    resolution: float
    clock_half_width_ns: int
    levels: tuple[float, float, float, float]  # gap, prefill, decode, tool


SENSORS = (
    # Mock sync bracket spans one 100 ms poll: half-width 50 ms.
    Sensor("nvml_power", "gpu0", NS // 10, NS // 40, 1.0, NS // 20,
           (70.0, 330.0, 240.0, 90.0)),
    # A one-sample 1 ms timestamp bracket gives a 0.5 ms half-width.
    Sensor("ina3221", "VDD_IN", NS // 1000, None, 0.02, NS // 2000,
           (3.0, 18.0, 12.0, 5.0)),
    # 20 ms mock clock bracket: 2 * 45 W * 10 ms is about the M3's 1 J
    # attribution limit, before its 0.1 W resolution term.
    Sensor("powermetrics", "package", NS // 10, NS // 10, 0.1, NS // 100,
           (8.0, 45.0, 30.0, 12.0)),
)


class Timeline:
    def __init__(self, spans, levels):
        self.spans = spans
        self.starts = [span[2] for span in spans]
        self.levels = levels

    def watts(self, t):
        i = bisect_right(self.starts, t) - 1
        if i < 0 or t >= self.spans[-1][3]:
            return self.levels["gap"]
        return self.levels[self.spans[i][1]]

    def integral(self, start, end):
        # Outside episode support is the known idle plateau used for padding.
        terms = []
        if start < 0:
            terms.append(self.levels["gap"] * (min(end, 0) - start) / NS)
        stop = self.spans[-1][3]
        if end > stop:
            terms.append(self.levels["gap"] * (end - max(start, stop)) / NS)
        lo = max(0, bisect_right(self.starts, start) - 1)
        for _, kind, a, b in self.spans[lo:]:
            if a >= end:
                break
            overlap = min(end, b) - max(start, a)
            if overlap > 0:
                terms.append(self.levels[kind] * overlap / NS)
        return math.fsum(terms)


def world(seed, sensor, *, load_variation_fraction=0.05, clock_offset_ns=17_000_000):
    """Fixture parameters choose workload variation and a known clock offset."""
    rng = random.Random(seed)
    cursor = 0
    parts = []
    turns = []
    context = 2048
    durations = [2, 4, 8, 15, 30, 50, 80, 120, 200, 300] * 2
    rng.shuffle(durations)

    def add(owner, kind, duration):
        nonlocal cursor
        parts.append((owner, kind, cursor, cursor + duration))
        cursor += duration

    add(None, "gap", NS // 2)
    for index, tool_ticks in enumerate(durations):
        start = cursor
        prefill_ns = rng.randint(5, 20) * NS // 10
        before_ns = rng.randint(10, 35) * NS // 10
        after_ns = rng.randint(10, 30) * NS // 10
        add(index, "prefill", prefill_ns)
        first = cursor
        add(index, "decode", before_ns)
        tool_start = cursor
        add(index, "tool", tool_ticks * NS // 10)
        tool_end = cursor
        add(index, "decode", after_ns)
        # 600 prompt tokens/s and 40 generated tokens/s are chosen synthetic
        # serving rates; the token counts and context grow as in an agent loop.
        prefill_tokens = prefill_ns * 600 // NS
        decode_tokens = (before_ns + after_ns) * 40 // NS
        call = ToolCall("local_search" if index % 2 else "local_exec",
                        ORIGIN + tool_start, ORIGIN + tool_end,
                        rng.randint(128, 1024), rng.randint(1024, 8192),
                        logged=index % 5 != 0)
        turns.append(Turn(index, ORIGIN + start, ORIGIN + cursor,
                          context, prefill_tokens, decode_tokens,
                          hidden_tokens=decode_tokens // 3, first_token_ns=ORIGIN + first,
                          tool_calls=(call,), logged=index % 7 != 0))
        context += prefill_tokens + decode_tokens
        add(None, "gap", rng.randint(2, 7) * NS // 10)
    gain = rng.uniform(1 - load_variation_fraction, 1 + load_variation_fraction)
    levels = {kind: power * gain for kind, power in zip(("gap", "prefill", "decode", "tool"),
                                                       sensor.levels)}
    truth = Timeline(parts, levels)
    period = sensor.period_ns
    times = tuple(range(-period, cursor + 2 * period, period))
    values = []
    for t in times:
        value = (truth.watts(t) if sensor.window_ns is None else
                 truth.integral(t - sensor.window_ns, t) / (sensor.window_ns / NS))
        # Half-quantum bounded analogue noise plus half-quantum rounding gives
        # at most one resolution quantum per observation, the required budget.
        noisy = value + rng.uniform(-sensor.resolution / 2, sensor.resolution / 2)
        values.append(round(noisy / sensor.resolution) * sensor.resolution)
    power = PowerTrace(
        sensor.source, sensor.channel, "meter",
        tuple(ORIGIN + t - clock_offset_ns for t in times), tuple(values), "W", period,
        averaging_window_ns=sensor.window_ns,
        duty_fraction=(None if sensor.window_ns is None else sensor.window_ns / period),
        resolution=sensor.resolution,
    )
    clock = ClockMapping("meter", "host", clock_offset_ns, sensor.clock_half_width_ns,
                         "synthetic round-trip bracket")
    record = Episode("world-" + str(seed), "shade/synthetic-agent-loop", "sabotage",
                     "qwen3-8b", "mock:local-vllm", seed, "host",
                     ORIGIN, ORIGIN + cursor, tuple(turns), power_traces=(power,),
                     clock_mappings=(clock,), flags=("synthetic.provisional",))
    return record, truth


class ProductionWorldsTest(unittest.TestCase):
    def test_twenty_turn_worlds_cover_each_segment_for_all_stated_seeds(self):
        statistics = []
        # Five fixed seeds test five different timing/noise realizations.
        # Requiring all five is a deterministic regression bar, not a claim
        # about the success fraction over an unobserved seed population.
        seeds = range(5)
        for sensor in SENSORS:
            errors, widths, totals, clearances = [], [], [], []
            passed = 0
            for seed in seeds:
                with self.subTest(sensor=sensor.source, seed=seed):
                    record, truth = world(seed, sensor)
                    # Exercise the actual shared-record serialization seam.
                    record = from_json(Episode, to_json(record))
                    result = attribute_episode(record, source=sensor.source, channel=sensor.channel)
                    self.assertEqual(len(record.turns), 20)
                    self.assertEqual(sum(s.kind == "tool" for s in result.segments), 20)
                    expected = [(owner, kind, ORIGIN + a, ORIGIN + b)
                                for owner, kind, a, b in truth.spans]
                    self.assertEqual([(s.turn, s.kind, s.start_ns, s.end_ns) for s in result.segments],
                                     expected)
                    self.assertIn("synthetic.provisional", result.flags)
                    self.assertNotIn("trace.partial_coverage", result.flags)
                    if sensor.window_ns is not None and sensor.window_ns < sensor.period_ns:
                        self.assertIn("duty.uncovered", result.flags)
                    else:
                        self.assertNotIn("duty.uncovered", result.flags)
                    for segment in result.segments:
                        a, b = segment.start_ns - ORIGIN, segment.end_ns - ORIGIN
                        exact = truth.integral(a, b)
                        error = abs(segment.energy.joules - exact)
                        errors.append(error)
                        widths.append(segment.energy.half_width_j)
                        # The specified physical half-width itself is the bar;
                        # there is no extra percentage or empirical multiplier.
                        self.assertLessEqual(error, segment.energy.half_width_j)
                        if segment.kind == "tool":
                            # Even the 0.2 s tool pause must have a true energy
                            # drop from decode larger than its printed width.
                            drop = (truth.levels["decode"] - truth.levels["tool"]) * (b - a) / NS
                            clearance = drop - segment.energy.half_width_j
                            clearances.append(clearance)
                            self.assertGreater(clearance, 0.0)
                    exact_total = truth.integral(0, record.end_ns - ORIGIN)
                    self.assertLessEqual(abs(result.total.joules - exact_total), result.total.half_width_j)
                    values = [s.energy.joules for s in result.segments]
                    # Sixteen operations per span/segment bound the rounded
                    # endpoint interpolation and trapezoid arithmetic. gamma_n
                    # times the absolute sum is the accumulation-error bound.
                    operations = 16 * (len(record.power_traces[0].t_ns) + len(values) + 1)
                    gamma = operations * sys.float_info.epsilon / (1 - operations * sys.float_info.epsilon)
                    self.assertLessEqual(abs(math.fsum(values) - result.total.joules),
                                         gamma * math.fsum(abs(v) for v in values))
                    totals.append(result.total.joules)
                    passed += 1
            self.assertEqual(passed, len(seeds))
            statistics.append(dict(sensor=sensor.source, seeds_passed=passed, seeds=len(seeds),
                                   segments_per_seed=len(result.segments),
                                   duration_s=(record.end_ns - record.start_ns) / NS,
                                   maximum_error_j=max(errors), minimum_half_width_j=min(widths),
                                   minimum_tool_clearance_j=min(clearances),
                                   total_j_range=(min(totals), max(totals))))
        print("attribution synthetic worlds: " + json.dumps(statistics, sort_keys=True))

    def test_idle_subtraction_reaches_every_segment(self):
        record, truth = world(0, SENSORS[0])
        idle = truth.levels["gap"]
        gross = attribute_episode(record, source="nvml_power", channel="gpu0")
        net = attribute_episode(record, source="nvml_power", channel="gpu0", idle_watts=idle)
        for a, b in zip(gross.segments, net.segments):
            expected = a.energy.joules - idle * (a.end_ns - a.start_ns) / NS
            # Identical inputs use identical code paths; net energy is one
            # rounded subtraction. Bound the alternate multiplication order
            # by four ulps (multiply, divide, subtract, subtraction in test).
            bar = 4 * math.ulp(max(abs(a.energy.joules), abs(expected)))
            self.assertLessEqual(abs(b.energy.joules - expected), bar)

    def test_unsampled_burst_is_flagged_but_not_certified_by_nominal_bound(self):
        # A 100 ms NVML poll observes only its final 25 ms. A 400 W excess
        # pulse for 50 ms fits entirely in the 75 ms unobserved gap.
        sensor = PowerTrace("nvml_power", "gpu0", "meter", (0, NS // 10),
                            (70.0, 70.0), "W", NS // 10,
                            averaging_window_ns=NS // 40, duty_fraction=0.25, resolution=1.0)
        estimate = trace_energy(sensor, 0, NS // 10,
                                mapping=ClockMapping("meter", "host", 0, NS // 20, "poll bracket"))
        actual = 70 * 0.1 + 400 * 0.05
        self.assertIn("duty.uncovered", estimate.flags)
        # The deliberately invisible 20 J burst clears the 7.1 J nominal
        # clock+resolution width. This catches a false completeness guarantee.
        self.assertGreater(abs(actual - estimate.joules), estimate.half_width_j)


if __name__ == "__main__":
    unittest.main()
