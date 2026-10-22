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
    # NVML reports integer mW: 1 mW / 1000 = .001 W. Host polling uses
    # the episode clock; the primary world test supplies no ClockMapping.
    Sensor("nvml_power", "gpu0", NS // 10, NS // 40, 0.001, 0,
           (70.0, 330.0, 240.0, 90.0)),
    # INA3221 shunt LSB 40 uV / fixture shunt 5 mOhm * bus 5 V = .04 W.
    # A one-sample 1 ms timestamp bracket gives a .5 ms clock half-width.
    Sensor("ina3221", "VDD_IN", NS // 1000, None, 40e-6 / 5e-3 * 5, NS // 2000,
           (3.0, 18.0, 12.0, 5.0)),
    # Powermetrics prints integer mW: .001 W. A synthetic 2 ms clock
    # bracket gives 1 ms half-width; it does not stand in for the M3's
    # separate approximately 1 J phase-attribution limitation.
    Sensor("powermetrics", "package", NS // 10, NS // 10, 0.001, NS // 1000,
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


def world(seed, sensor, *, load_variation_fraction=0.05, clock_offset_ns=17_000_000,
          same_domain=False, grid_phase_fraction=0.37, poll_jitter_ns=2_000_000,
          tools_after_turn=False):
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
        # Integer-ns phase lengths deliberately avoid the sensor grid.
        prefill_ns = rng.randint(NS // 2, 2 * NS)
        before_ns = rng.randint(NS, 7 * NS // 2)
        after_ns = rng.randint(NS, 3 * NS)
        add(index, "prefill", prefill_ns)
        first = cursor
        add(index, "decode", before_ns + after_ns if tools_after_turn else before_ns)
        model_end = cursor
        tool_start = cursor
        add(index, "tool", tool_ticks * NS // 10)
        tool_end = cursor
        if not tools_after_turn:
            add(index, "decode", after_ns)
            model_end = cursor
        # 600 prompt tokens/s and 40 generated tokens/s are chosen synthetic
        # serving rates; the token counts and context grow as in an agent loop.
        prefill_tokens = prefill_ns * 600 // NS
        decode_tokens = (before_ns + after_ns) * 40 // NS
        call = ToolCall("local_search" if index % 2 else "local_exec",
                        ORIGIN + tool_start, ORIGIN + tool_end,
                        rng.randint(128, 1024), rng.randint(1024, 8192),
                        logged=index % 5 != 0)
        turns.append(Turn(index, ORIGIN + start, ORIGIN + model_end,
                          context, prefill_tokens, decode_tokens,
                          hidden_tokens=decode_tokens // 3, first_token_ns=ORIGIN + first,
                          tool_calls=(call,), logged=index % 7 != 0))
        context += prefill_tokens + decode_tokens
        add(None, "gap", rng.randint(NS // 5, 7 * NS // 10))
    gain = rng.uniform(1 - load_variation_fraction, 1 + load_variation_fraction)
    levels = {kind: power * gain for kind, power in zip(("gap", "prefill", "decode", "tool"),
                                                       sensor.levels)}
    truth = Timeline(parts, levels)
    period = sensor.period_ns
    # 37% of a poll is an explicit fixture phase parameter, independent of
    # all phase lengths. Point/duty sensors jitter by up to a quarter period;
    # back-to-back whole windows retain regular, nonoverlapping support.
    phase = int(period * grid_phase_fraction)
    jitter = (0 if sensor.window_ns == period else min(poll_jitter_ns, period // 4))
    times = tuple(t + rng.randint(-jitter, jitter)
                  for t in range(-period + phase, cursor + 2 * period, period))
    values = []
    for t in times:
        value = (truth.watts(t) if sensor.window_ns is None else
                 truth.integral(t - sensor.window_ns, t) / (sensor.window_ns / NS))
        # Half-quantum bounded analogue noise plus half-quantum rounding gives
        # at most one resolution quantum per observation, the required budget.
        noisy = value + rng.uniform(-sensor.resolution / 2, sensor.resolution / 2)
        values.append(round(noisy / sensor.resolution) * sensor.resolution)
    domain = "host" if same_domain else "meter"
    offset = 0 if same_domain else clock_offset_ns
    power = PowerTrace(
        sensor.source, sensor.channel, domain,
        tuple(ORIGIN + t - offset for t in times), tuple(values), "W", period,
        averaging_window_ns=sensor.window_ns,
        duty_fraction=(None if sensor.window_ns is None else sensor.window_ns / period),
        resolution=sensor.resolution,
    )
    clock = ClockMapping("meter", "host", offset, sensor.clock_half_width_ns,
                         "synthetic round-trip bracket")
    record = Episode("world-" + str(seed), "shade/synthetic-agent-loop", "sabotage",
                     "qwen3-8b", "mock:local-vllm", seed, "host",
                     ORIGIN, ORIGIN + cursor, tuple(turns), power_traces=(power,),
                     clock_mappings=() if same_domain else (clock,),
                     flags=("synthetic.provisional",))
    return record, truth


class ProductionWorldsTest(unittest.TestCase):
    statistics = {}

    def check_worlds(self, sensor):
        if sensor.source in self.statistics:
            return self.statistics[sensor.source]
        errors, widths, totals, clearances = [], [], [], []
        inside = total_inside = 0
        # Five fixed seeds are a deterministic empirical regression set.
        # Coverage remains 100% of segments in every one of these five seeds.
        seeds = range(5)
        for seed in seeds:
            record, truth = world(seed, sensor, same_domain=sensor.source == "nvml_power")
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
            if sensor.source == "nvml_power":
                self.assertEqual(record.clock_mappings, ())
                self.assertIn("clock.uncertainty_missing", result.flags)
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
                inside += error <= segment.energy.half_width_j
                if segment.kind == "tool":
                    # The 0.2 s minimum tool must clear its printed width.
                    drop = (truth.levels["decode"] - truth.levels["tool"]) * (b - a) / NS
                    clearance = drop - segment.energy.half_width_j
                    clearances.append(clearance)
                    self.assertGreater(clearance, 0.0)
            exact_total = truth.integral(0, record.end_ns - ORIGIN)
            total_inside += abs(result.total.joules - exact_total) <= result.total.half_width_j
            values = [s.energy.joules for s in result.segments]
            # Sixteen rounded operations per span/segment conservatively
            # bound interpolation and quadrature. This is an accumulation
            # property, not an agreement bar between independent estimators.
            operations = 16 * (len(record.power_traces[0].t_ns) + len(values) + 1)
            gamma = operations * sys.float_info.epsilon / (1 - operations * sys.float_info.epsilon)
            self.assertLessEqual(abs(math.fsum(values) - result.total.joules),
                                 gamma * math.fsum(abs(v) for v in values))
            totals.append(result.total.joules)
        stats = dict(sensor=sensor.source, seeds=len(seeds), segments=len(errors),
                     segments_inside=inside, totals_inside=total_inside,
                     duration_s=(record.end_ns - record.start_ns) / NS,
                     maximum_error_j=max(errors), minimum_half_width_j=min(widths),
                     minimum_tool_clearance_j=min(clearances),
                     total_j_range=(min(totals), max(totals)))
        print("attribution unaligned worlds: " + json.dumps(stats, sort_keys=True))
        self.statistics[sensor.source] = stats
        return stats

    def test_twenty_turn_structure_and_detectable_tools(self):
        # Run structural, conservation and effect-clearance assertions outside
        # expectedFailure so that M2 cannot hide an unrelated regression.
        for sensor in SENSORS:
            with self.subTest(sensor=sensor.source):
                self.check_worlds(sensor)

    def assert_coverage(self, sensor):
        stats = self.check_worlds(sensor)
        # M2 retains the original requirement: every segment within its own
        # physical half-width, with no empirical widening or reduced fraction.
        self.assertEqual(stats["segments_inside"], stats["segments"], stats)
        self.assertEqual(stats["totals_inside"], stats["seeds"], stats)

    def test_twenty_turn_ina3221_worlds_cover_every_segment(self):
        self.assert_coverage(SENSORS[1])

    @unittest.expectedFailure
    def test_twenty_turn_nvml_worlds_cover_every_segment(self):
        """M2: measured coverage pending execution; required coverage is 100%."""
        self.assert_coverage(SENSORS[0])

    @unittest.expectedFailure
    def test_twenty_turn_powermetrics_worlds_cover_every_segment(self):
        """M2: measured coverage pending execution; required coverage is 100%."""
        self.assert_coverage(SENSORS[2])

    def test_twenty_runner_turns_retain_each_post_model_tool(self):
        for sensor in SENSORS[:2]:
            with self.subTest(sensor=sensor.source):
                record, truth = world(0, sensor, tools_after_turn=True,
                                      same_domain=sensor.source == "nvml_power")
                record = from_json(Episode, to_json(record))
                result = attribute_episode(record, source=sensor.source, channel=sensor.channel)
                self.assertEqual([(s.turn, s.kind, s.start_ns, s.end_ns) for s in result.segments],
                                 [(owner, kind, ORIGIN + a, ORIGIN + b)
                                  for owner, kind, a, b in truth.spans])
                tools = [s for s in result.segments if s.kind == "tool"]
                self.assertEqual(len(tools), 20)
                self.assertNotIn("tool.outside_turn", result.flags)
                self.assertNotIn("tool.outside_episode", result.flags)
                # Every physical power level in this fixture is positive:
                # losing tool attribution would produce no segments/zero J.
                self.assertGreater(math.fsum(s.energy.joules for s in tools), 0.0)
                print("attribution runner tools: " + json.dumps(dict(
                    sensor=sensor.source, tools=len(tools),
                    joules=math.fsum(s.energy.joules for s in tools),
                    true_joules=math.fsum(truth.integral(s.start_ns - ORIGIN,
                                                       s.end_ns - ORIGIN) for s in tools)),
                    sort_keys=True))

    def test_counter_reset_in_twenty_turn_episode(self):
        record, truth = world(0, SENSORS[0])
        old = record.power_traces[0]
        offset = record.clock_mappings[0].offset_ns
        times = tuple(t + offset - ORIGIN for t in old.t_ns)
        reset_index = len(times) // 2
        reset_time = (times[reset_index - 1] + times[reset_index]) // 2
        quantum = 0.001  # NVML integer mJ reporting quantum.
        values = []
        for k, t in enumerate(times):
            # A driver running for hours has a large positive baseline;
            # restart halfway through a polling interval loses pre-reset work.
            value = (5_000_000 + truth.integral(times[0], t) if k < reset_index
                     else truth.integral(reset_time, t))
            values.append(math.floor(value / quantum) * quantum)
        counter = replace(old, source="nvml_energy", unit="J_cumulative",
                          values=tuple(values), averaging_window_ns=None,
                          duty_fraction=None, resolution=quantum)
        record = from_json(Episode, to_json(replace(record, power_traces=(counter,))))
        result = attribute_episode(record, source="nvml_energy", channel="gpu0")
        exact = truth.integral(0, record.end_ns - ORIGIN)
        self.assertEqual(sum(s.kind == "tool" for s in result.segments), 20)
        self.assertIn("counter.reset", result.flags)
        self.assertIn("counter.reset_interval", result.flags)
        self.assertLessEqual(abs(result.total.joules - exact), result.total.half_width_j)
        self.assertTrue(all(s.energy.joules >= 0 for s in result.segments))
        # Nonnegative true phase powers bound any observed counter slope by
        # max true W plus two endpoint quanta divided by the shortest poll.
        peak = max(truth.levels.values()) + 2 * quantum / (min(
            b - a for a, b in zip(times, times[1:])) / NS)
        before = trace_energy(counter, record.start_ns - NS, record.start_ns,
                              mapping=record.clock_mappings[0])
        # Requested duration is 1 s. Missing coverage is at most 1 s at peak;
        # the stop's partial-counter term is at most half one longest poll.
        longest_poll_s = max(b - a for a, b in zip(times, times[1:])) / NS
        limit = peak * (1 + longest_poll_s / 2) + 2 * quantum
        self.assertLessEqual(before.half_width_j, limit)
        print("attribution reset world: " + json.dumps(dict(
            joules=result.total.joules, true_joules=exact,
            half_width_j=result.total.half_width_j, before_half_width_j=before.half_width_j),
            sort_keys=True))

    def test_idle_subtraction_reaches_every_segment(self):
        record, truth = world(0, SENSORS[0])
        idle = truth.levels["gap"]
        gross = attribute_episode(record, source="nvml_power", channel="gpu0")
        net = attribute_episode(record, source="nvml_power", channel="gpu0", idle_watts=idle)
        for a, b in zip(gross.segments, net.segments):
            expected = a.energy.joules - idle * (a.end_ns - a.start_ns) / NS
            # Agreement uses 1% of the smaller printed half-width; that bar
            # must also clear the brief's one-million-ulp float-noise floor.
            bar = 0.01 * min(a.energy.half_width_j, b.energy.half_width_j)
            scale = max(abs(a.energy.joules), abs(expected))
            self.assertGreaterEqual(bar, 1e6 * math.ulp(scale))
            self.assertLessEqual(abs(b.energy.joules - expected), bar)

    def test_unsampled_burst_is_flagged_but_not_certified_by_nominal_bound(self):
        # A 100 ms NVML poll observes only its final 25 ms. A 400 W excess
        # pulse for 50 ms fits entirely in the 75 ms unobserved gap.
        sensor = PowerTrace("nvml_power", "gpu0", "meter", (0, NS // 10),
                            (70.0, 70.0), "W", NS // 10,
                            averaging_window_ns=NS // 40, duty_fraction=0.25,
                            resolution=0.001)  # Integer mW reporting quantum.
        estimate = trace_energy(sensor, 0, NS // 10,
                                mapping=ClockMapping("meter", "host", 0, 0, "exact synthetic offset"))
        actual = 70 * 0.1 + 400 * 0.05
        self.assertIn("duty.uncovered", estimate.flags)
        # The invisible 20 J burst clears the .001 W * .1 s = .0001 J
        # resolution-only width. This catches a false completeness guarantee.
        self.assertGreater(abs(actual - estimate.joules), estimate.half_width_j)


if __name__ == "__main__":
    unittest.main()
