"""Production-shaped synthetic episodes and independent averaging checks."""

import math
import unittest

from joulewise.align.records import Episode, ToolCall, Turn
from joulewise.align.sensor_sim import (
    PowerInterval, SensorModel, Timeline, TimelineModel, simulate, timeline_from_episode,
)


def model():
    # Explicit synthetic workload parameters, not fitted hardware constants.
    return TimelineModel(idle_w=5, prefill_base_w=15, prefill_token_w=0.002,
                         context_token_w=0.0001, decode_w=8, ripple_w=0.1,
                         prefill_tokens_per_s=2000)


def world(seed=0, tool_duration_ns=250_000_000, tools=True):
    """Four turns, 512 fresh tokens each, 96 decoded tokens, growing KV cache."""
    import random
    rng = random.Random(seed)
    # Random alignment spans one 100 ms slow-sensor period, exercising aliasing.
    t = 500_000_000 + rng.randrange(100_000_000)
    turns = []
    for index in range(4):
        # 512 tokens / 2000 tokens/s = 256 ms prefill; decode is 96 / 64 = 1.5 s.
        first = t + 256_000_000
        end = first + 1_500_000_000
        calls = ((ToolCall("lookup", end, end + tool_duration_ns, 128, 2048),)
                 if tools and index < 3 else ())
        turns.append(Turn(index, t, end, index * (512 + 96), 512, 96,
                          first_token_ns=first, tool_calls=calls))
        t = end + (tool_duration_ns if calls else 0)
    return Episode(f"synthetic-{seed}", "synthetic/multiturn", "benign", "local-8b",
                   "mock:local", seed, "host.monotonic", 0, t + 500_000_000, tuple(turns))


class SensorSimTest(unittest.TestCase):
    def test_complete_episode_chain_reproducible_and_tools_omitted_only_from_log(self):
        from dataclasses import replace
        episode = world()
        timeline = timeline_from_episode(episode, model())
        sensor = SensorModel.nvml(noise_sd_w=0.05, quantum_w=0.01, seed=4)
        trace = simulate(timeline, sensor)
        altered = replace(episode, turns=tuple(
            replace(t, tool_calls=tuple(replace(c, logged=False) for c in t.tool_calls))
            for t in episode.turns))
        # Identical code on identical true activity must give bit-identical traces.
        self.assertEqual(trace, simulate(timeline_from_episode(altered, model()), sensor))
        self.assertEqual(episode.totals()["decode_tokens"], 384)
        self.assertEqual(episode.totals()["tool_calls"], 3)
        self.assertTrue(any(s.label == "prefill" for s in timeline.intervals))
        self.assertTrue(any(s.label == "decode" for s in timeline.intervals))
        self.assertTrue(any(s.label == "tool_wait" for s in timeline.intervals))

    def test_window_average_and_duty_do_not_scale_watts(self):
        timeline = Timeline(0, 200_000_000, "host.monotonic", 0,
                            (PowerInterval(0, 100_000_000, 100, "decode"),))
        nvml = simulate(timeline, SensorModel.nvml(noise_sd_w=0, quantum_w=0))
        whole = simulate(timeline, SensorModel.powermetrics(noise_sd_w=0, quantum_w=0))
        # At 100 ms both windows contain 100 W throughout; no uncertainty: 1e-6 relative.
        for trace in (nvml, whole):
            self.assertAlmostEqual(trace.values[0], 100, delta=100 * 1e-6)
        # A 25 ms burst in a 100 ms whole window yields 25 W.
        pulse = Timeline(0, 200_000_000, "host.monotonic", 0,
                         (PowerInterval(75_000_000, 100_000_000, 100, "prefill"),))
        self.assertAlmostEqual(simulate(pulse, SensorModel.powermetrics(
            noise_sd_w=0, quantum_w=0)).values[0], 25, delta=25 * 1e-6)

    def test_independent_midpoint_oracle_including_ripple_and_partial_overlap(self):
        # Independent arithmetic design supplied by the gpt-6-astra review seat.
        span = PowerInterval(25_000_000, 175_000_000, 13, "decode", 0.2,
                             15_625_000, 25_000_000)  # 64 tokens/s.
        timeline = Timeline(0, 200_000_000, "host.monotonic", 5, (span,))
        sensor = SensorModel.powermetrics(noise_sd_w=0, quantum_w=0)
        trace = simulate(timeline, sensor)
        for t, actual in zip(trace.t_ns, trace.values):
            left, right = max(t - 100_000_000, span.start_ns), min(t, span.end_ns)
            length = max(0, right - left)
            # Composite midpoint error <= |A|*omega^2*L^3/(24*m^2*window).
            # Choose m from a 1e-6-relative numerical budget, independently of
            # the analytic sinusoidal antiderivative used by Timeline.integral.
            omega = math.tau / span.ripple_period_ns
            budget = 5 * 1e-6  # 1e-6 of the 5 W idle floor.
            coefficient = abs(span.ripple_w) * omega**2 * length**3 / (24 * 100_000_000)
            count = max(1, math.ceil(math.sqrt(coefficient / budget)))
            step = length / count
            sampled = math.fsum(8 + span.ripple_w * math.sin(
                omega * (left + (j + 0.5) * step - span.start_ns))
                for j in range(count))
            expected = 5 + sampled * step / 100_000_000
            bound = coefficient / count**2 + 1e-6 * abs(expected)
            self.assertLessEqual(abs(actual - expected), bound)

    def test_clock_quantum_and_invalid_sensor_flags(self):
        episode = world()
        sensor = SensorModel.ina3221(cadence_ns=1_000_000, noise_sd_w=0.05,
                                     quantum_w=0.01, seed=7, clock_offset_ns=7_000_000,
                                     clock_domain="meter.monotonic")
        trace = simulate(timeline_from_episode(episode, model()), sensor)
        self.assertEqual(trace.t_ns[0], -6_000_000)  # 1 ms first sample minus 7 ms offset.
        for value in trace.values:
            # Values are rounded to 0.01 W bins; use 1e-6 relative in bin units.
            bins = value / sensor.quantum_w
            self.assertLessEqual(abs(bins - round(bins)), abs(bins) * 1e-6)
        invalid = simulate(timeline_from_episode(episode, model()),
                           SensorModel(0, 0, 1, 0, 0))
        self.assertIn("invalid_sensor_model", invalid.notes)
        self.assertEqual(len(invalid.values), 0)

    def test_in_turn_wait_overrides_turn_envelope(self):
        episode = world()
        from dataclasses import replace
        turn = episode.turns[0]
        call = ToolCall("lookup", turn.first_token_ns + 500_000_000,
                        turn.first_token_ns + 750_000_000, 128, 2048)
        episode = replace(episode, turns=(replace(turn, tool_calls=(call,)),) + episode.turns[1:])
        timeline = timeline_from_episode(episode, model())
        # A 250 ms wait is wholly inside the turn envelope, still near-idle.
        self.assertAlmostEqual(timeline.power_at(call.start_ns + 100_000_000),
                               5, delta=5 * 1e-6)


if __name__ == "__main__":
    unittest.main()
