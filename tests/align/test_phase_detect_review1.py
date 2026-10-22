"""End-to-end regressions ported from the independent first review."""

import unittest
from dataclasses import replace

from joulewise.align.phase_detect import detect_phases, match_tool_calls
from joulewise.align.records import PowerTrace
from joulewise.align.sensor_sim import SensorModel, simulate, timeline_from_episode
from tests.align.test_sensor_sim import model, world
from tests.align.test_phase_detect import sensor_models


class PhaseReviewTest(unittest.TestCase):
    def test_held_reads_with_estimated_and_supplied_noise(self):
        episode = world(5, 250_000_000)
        timeline = timeline_from_episode(episode, model())
        controls = {}
        for hold in (1, 2, 4, 8):
            original = simulate(timeline, SensorModel.ina3221(
                cadence_ns=hold * 1_000_000, noise_sd_w=0.05, quantum_w=0.01, seed=5))
            times = tuple(range(original.t_ns[0], original.t_ns[-1] + 1, 1_000_000))
            values, index = [], 0
            for timestamp in times:
                while index + 1 < len(original.t_ns) and original.t_ns[index + 1] <= timestamp:
                    index += 1
                values.append(original.values[index])
            trace = PowerTrace("ina3221", "VDD_IN", "host.monotonic", times,
                               tuple(values), "W", 1_000_000)
            for sd in (None, 0.05):
                with self.subTest(hold=hold, sd=sd):
                    segments = detect_phases(trace, noise_sd_w=sd)
                    result = match_tool_calls(segments, episode)
                    self.assertEqual(result.matched_count, 3)  # Three true calls.
                    self.assertEqual(len(result.unlogged_candidates), 0)
                    if hold == 1:
                        controls[sd] = len(segments)
                    # Repeating a conversion adds no phase information.
                    self.assertLessEqual(len(segments), controls[sd])

    def test_back_to_back_calls_and_client_gap_count_calls_inside_run(self):
        base = world(11, 500_000_000)
        from joulewise.align.records import ToolCall
        turns = []
        shift = 0
        gap = 20_000_000  # Scenario: 20 ms client/serving latency per turn.
        for turn in base.turns:
            calls = tuple(
                ToolCall("tool", c.start_ns + shift + k * 250_000_000,
                         c.start_ns + shift + (k + 1) * 250_000_000, 128, 1024)
                for c in turn.tool_calls for k in range(2))
            turns.append(replace(turn, start_ns=turn.start_ns + shift,
                                 first_token_ns=turn.first_token_ns + shift,
                                 end_ns=turn.end_ns + shift, tool_calls=calls))
            if calls:
                shift += gap
        episode = replace(base, turns=tuple(turns), end_ns=base.end_ns + shift)
        for name, sensor in sensor_models(11):
            with self.subTest(sensor=name):
                segments = detect_phases(simulate(timeline_from_episode(episode, model()), sensor))
                result = match_tool_calls(segments, episode)
                self.assertEqual(result.matched_count, 6)  # Two calls in each of three runs.
                self.assertEqual(len(result.unlogged_candidates), 0)
                self.assertIn("back_to_back_calls_temporally_unresolved", result.flags)
                self.assertLessEqual(result.precision, 1.0)  # A probability's upper endpoint.

    def test_less_read_noise_does_not_split_token_ripple_into_phases(self):
        episode = world(3, 250_000_000)
        timeline = timeline_from_episode(episode, model())
        controls = {}
        for sd, quantum in ((0.05, 0.01), (0.02, 0.01), (0.01, 0.01),
                            (0.005, 0.0), (0.0, 0.0), (0.0, 0.01)):
            for name, sensor in (
                    ("ina", SensorModel.ina3221(cadence_ns=1_000_000,
                                               noise_sd_w=sd, quantum_w=quantum, seed=3)),
                    ("pm", SensorModel.powermetrics(noise_sd_w=sd, quantum_w=quantum, seed=3))):
                with self.subTest(sd=sd, quantum=quantum, sensor=name):
                    segments = detect_phases(simulate(timeline, sensor))
                    if sd == 0.05:
                        controls[name] = len(segments)
                    self.assertLessEqual(len(segments), controls[name])
                    self.assertFalse(any("level_duration_model_mismatch" in s.flags for s in segments))
                    for turn in episode.turns:
                        # One exposure plus one sampling period bounds mixed edges.
                        margin = sensor.averaging_window_ns + sensor.sample_interval_ns
                        self.assertFalse(any(
                            s.label == "prefill" and s.start_ns < turn.end_ns - margin and
                            s.end_ns > turn.first_token_ns + margin for s in segments))

    def test_missed_read_widens_boundary_or_is_indeterminate(self):
        episode = world(4, 500_000_000)
        trace = simulate(timeline_from_episode(episode, model()),
                         SensorModel.ina3221(cadence_ns=1_000_000,
                                             noise_sd_w=0.05, quantum_w=0.01, seed=2))
        call = episode.turns[1].tool_calls[0]
        # Lose 1 s across the decode/wait boundary, as in review E10.
        left, right = call.start_ns - 800_000_000, call.start_ns + 200_000_000
        keep = [(t, v) for t, v in zip(trace.t_ns, trace.values) if not left <= t < right]
        gapped = replace(trace, t_ns=tuple(t for t, _ in keep),
                         values=tuple(v for _, v in keep))
        segments = detect_phases(gapped)
        result = match_tool_calls(segments, episode)
        self.assertEqual(len(result.unlogged_candidates), 0)
        self.assertTrue(result.matched_count == 3 or result.indeterminate_candidates)
        self.assertTrue(any(s.boundary_uncertainty_ns >= right - left for s in segments))

    def test_scheduler_jitter_below_one_missed_period_is_not_a_gap(self):
        # Alternating +/-0.1 ms jitter stays below 2 nominal 1 ms bins.
        times = tuple((i + 1) * 1_000_000 + (i % 2) * 100_000 for i in range(500))
        trace = PowerTrace("mock", "x", "host.monotonic", times, (5.0,) * len(times),
                           "W", 1_000_000, 1_000_000)
        self.assertNotIn("sample_gaps", detect_phases(trace)[0].flags)


if __name__ == "__main__":
    unittest.main()
