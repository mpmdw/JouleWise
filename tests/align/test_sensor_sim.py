"""Production-shaped synthetic episodes and independent averaging checks."""

import json
import math
import random
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


def production_world(seed=0, tool_duration_ns=250_000_000, tools=True, *,
                     turns=30, client_gap_ns=20_000_000, calls_per_turn=(1, 3),
                     bytes_per_result_token=4):
    """Minute-scale SHADE-shaped scenario; these counts/rates are inputs.

    Results feed the next prefill, cached context grows, and multiple calls
    share a contiguous idle run. First two tool turns guarantee both an
    isolated call and a shared run for the two identifiability controls.
    """
    import random
    rng = random.Random(seed)
    cursor = 500_000_000 + rng.randrange(100_000_000)  # Random slow-sensor alignment.
    context, prefill = 0, 1800  # Scenario system prompt + task input.
    output = []
    for index in range(turns):
        decoded = rng.randint(30, 400)  # Scenario production output-length distribution.
        first = cursor + round(prefill / 2000 * 1e9)  # Model's 2000 prefill tokens/s.
        end = first + round(decoded / 64 * 1e9)  # Scenario 64 decoded tokens/s.
        number = rng.randint(*calls_per_turn) if tools and index < turns - 1 else 0
        if tools and index < turns - 1:
            if index == 0:
                number = 1
            elif index == 1:
                number = 2
        # Explicit synthetic text-size ratio ties result bytes to the next
        # prefill's token count; it is not a tokenizer calibration.
        result_tokens = [rng.randint(150, 3000) for _ in range(number)]
        calls = tuple(ToolCall(
            f"lookup{k}", end + k * tool_duration_ns,
            end + (k + 1) * tool_duration_ns, 100,
            result_tokens[k] * bytes_per_result_token) for k in range(number))
        output.append(Turn(index, cursor, end, context, prefill, decoded,
                           first_token_ns=first, tool_calls=calls))
        context += prefill + decoded
        # Tool-result token volume is a scenario input, never a power constant.
        prefill = sum(result_tokens) if calls else 200
        # Null control removes tools and their round-trip/client wait; the
        # mixed-call study retains serving gaps in every tool-bearing turn.
        cursor = end + number * tool_duration_ns + (client_gap_ns if calls else 0)
    return Episode(f"production-{seed}", "shade/synthetic", "benign", "local-8b",
                   "mock:local", seed, "host.monotonic", 0, cursor + 500_000_000, tuple(output))


class SensorSimTest(unittest.TestCase):
    def test_production_world_has_results_context_and_multi_call_client_gaps(self):
        episode = production_world(11, 500_000_000)
        self.assertEqual(len(episode.turns), 30)  # Declared production study scenario.
        self.assertTrue(any(len(t.tool_calls) >= 2 for t in episode.turns))
        self.assertTrue(all(b.context_tokens > a.context_tokens
                            for a, b in zip(episode.turns, episode.turns[1:])))
        self.assertTrue(any(t.prefill_tokens != 1800 for t in episode.turns[1:]))
        for a, b in zip(episode.turns, episode.turns[1:]):
            self.assertEqual(b.start_ns - a.tool_calls[-1].end_ns, 20_000_000)
        timeline = timeline_from_episode(episode, model())
        sensor = SensorModel.powermetrics(noise_sd_w=0, quantum_w=0)
        trace = simulate(timeline, sensor)
        got = math.fsum(trace.values) * sensor.averaging_window_ns
        expected = timeline.integral(episode.start_ns, trace.t_ns[-1])
        # Tiled, noiseless windows agree with analytic energy; no printed
        # uncertainty, so the required comparison is relative 1e-6.
        self.assertAlmostEqual(got, expected, delta=abs(expected) * 1e-6)

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
        cycles = sum((s.end_ns - s.start_ns) / s.ripple_period_ns
                     for s in timeline.intervals if s.label == "decode" and
                     s.start_ns >= turn.first_token_ns and s.end_ns <= turn.end_ns)
        # The analytic token clock must retain all 96 tokens; no uncertainty,
        # so agreement uses the required 1e-6 relative bar.
        self.assertAlmostEqual(cycles, turn.decode_tokens, delta=turn.decode_tokens * 1e-6)


    def test_unheld_defaults_preserve_original_seeded_outputs(self):
        episode = world(7)
        timeline = timeline_from_episode(episode, model())
        for sensor in (SensorModel.ina3221(cadence_ns=1_000_000, noise_sd_w=.05,
                                          quantum_w=.01, seed=7),
                       SensorModel.nvml(noise_sd_w=.05, quantum_w=.01, seed=7),
                       SensorModel.powermetrics(noise_sd_w=.05, quantum_w=.01, seed=7)):
            # Frozen original sampling arithmetic: byte identity is the
            # compatibility property, so use exact equality, including notes.
            rng = random.Random(sensor.seed)
            expected = []
            for t in range(timeline.start_ns + sensor.sample_interval_ns,
                           timeline.end_ns + 1, sensor.sample_interval_ns):
                value = timeline.integral(t - sensor.averaging_window_ns, t) / sensor.averaging_window_ns
                value += rng.gauss(0, sensor.noise_sd_w)
                expected.append(round(value / sensor.quantum_w) * sensor.quantum_w)
            trace = simulate(timeline, sensor)
            self.assertEqual(trace.values, tuple(expected))
            self.assertEqual(trace.notes, json.dumps({
                "flags": list(timeline.flags), "clock_offset_uncertainty_ns": 0,
                "synthetic": True}, sort_keys=True))

    def test_register_windows_and_seeded_phase_through_episode_chain(self):
        from dataclasses import replace
        from joulewise.align.phase_detect import detect_phases, match_tool_calls
        episode = world(7)
        timeline = timeline_from_episode(episode, model())
        # Fastest datasheet sweep scenario: 140 us * bus/shunt * three rails.
        for period in (840_000, 1_500_000, 4_000_000):
            sensor = SensorModel.ina3221(cadence_ns=1_000_000,
                                        register_refresh_period_ns=period,
                                        noise_sd_w=0, quantum_w=0, seed=7)
            trace = simulate(timeline, sensor)
            phase = json.loads(trace.notes)["conversion_phase_ns"]
            self.assertEqual(phase, random.Random(sensor.seed).randrange(period))
            self.assertEqual(json.loads(trace.notes)["hold_latency_ns"], period)
            for t, value in zip(trace.t_ns, trace.values):
                end = phase + ((t - phase) // period) * period
                expected = timeline.integral(end - period, end) / period
                # No printed uncertainty: required 1e-6 relative agreement.
                self.assertAlmostEqual(value, expected, delta=abs(expected) * 1e-6)
            result = match_tool_calls(detect_phases(trace), episode)
            self.assertEqual(result.matched_count, 3)
            self.assertEqual(len(result.unlogged_candidates), 0)
            self.assertEqual(trace, simulate(timeline, sensor))
            # Hide a fully observed 250 ms wait inside a claimed envelope.
            first = episode.turns[0]
            call = first.tool_calls[0]
            hidden = replace(episode, turns=(replace(
                first, end_ns=call.end_ns, tool_calls=(replace(call, logged=False),)),)
                + episode.turns[1:])
            result = match_tool_calls(detect_phases(trace), hidden)
            self.assertTrue(any(s.start_ns < call.end_ns and s.end_ns > call.start_ns
                                for s in result.unlogged_candidates))


if __name__ == "__main__":
    unittest.main()
