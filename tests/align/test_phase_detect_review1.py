"""End-to-end regressions ported from the independent first review."""

import json
import unittest
from dataclasses import replace

from joulewise.align.phase_detect import detect_phases, estimate_noise_sd, match_tool_calls
from joulewise.align.records import PowerTrace
from joulewise.align.sensor_sim import SensorModel, simulate, timeline_from_episode
from tests.align.test_sensor_sim import model, production_world, world
from tests.align.test_phase_detect import clopper_pearson, production_sensor_models, sensor_models


class PhaseReviewTest(unittest.TestCase):
    def test_thirty_turn_transition_edges_have_no_false_waits_or_extra_prefills(self):
        episode = production_world(1, 500_000_000)
        timeline = timeline_from_episode(episode, model())
        for name, sensor in sensor_models(1):
            with self.subTest(sensor=name):
                segments = detect_phases(simulate(timeline, sensor))
                matches = match_tool_calls(segments, episode)
                # Brief convention >=90% call recall and <5% episode FA;
                # one fully logged control requires zero false candidates.
                self.assertGreaterEqual(matches.recall, .90)
                self.assertEqual(len(matches.unlogged_candidates), 0)
                # A sensor may miss sub-window prefills; it cannot invent an
                # extra prefill (the pipeline's hidden-turn signature).
                self.assertLessEqual(sum(s.label == "prefill" for s in segments),
                                     len(episode.turns))

    def test_exact_binomial_bounds_against_closed_form_oracles(self):
        import math
        # Equal-tail 95% is the brief's reporting convention. At zero/all
        # successes, binomial tail inversion has an independent closed form.
        confidence, trials = 0.95, 64
        alpha = 1 - confidence
        lower, upper = clopper_pearson(0, trials, confidence=confidence)
        expected = 1 - (alpha / 2) ** (1 / trials)
        self.assertEqual(lower, 0.0)  # Definitional probability endpoint.
        self.assertAlmostEqual(upper, expected, delta=expected * 1e-6)
        lower, upper = clopper_pearson(trials, trials, confidence=confidence)
        expected = (alpha / 2) ** (1 / trials)
        self.assertAlmostEqual(lower, expected, delta=expected * 1e-6)
        self.assertEqual(upper, 1.0)
        # With one success in two trials, solve the quadratic tails directly.
        low, high = clopper_pearson(1, 2, confidence=confidence)
        expected_low = 1 - math.sqrt(1 - alpha / 2)
        expected_high = math.sqrt(1 - alpha / 2)
        self.assertAlmostEqual(low, expected_low, delta=expected_low * 1e-6)
        self.assertAlmostEqual(high, expected_high, delta=expected_high * 1e-6)

    def test_production_sensor_resolution_uses_shunt_and_output_units(self):
        import math
        sensors = dict(production_sensor_models(0))
        # P3767 DT 5 milliohm shunt: 40 uV / 5 milliohm = 8 mA.
        # At 5 V, 2 A, dP = 5*.008 + 2*.008 + .008*.008 W.
        expected = 5 * .008 + 2 * .008 + .008 * .008
        self.assertAlmostEqual(sensors["ina3221_1ms"].quantum_w, expected,
                               delta=expected * 1e-6)
        for name in ("nvml_100ms_25ms", "powermetrics_100ms"):
            sensor = sensors[name]
            self.assertAlmostEqual(sensor.quantum_w, .001, delta=.001 * 1e-6)
            expected = .001 / math.sqrt(12)  # Uniform one-LSB rounding sd.
            self.assertAlmostEqual(sensor.noise_sd_w, expected, delta=expected * 1e-6)

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
                               tuple(values), "W", 1_000_000,
                               averaging_window_ns=hold * 1_000_000,
                               notes=json.dumps({"register_refresh_period_ns": hold * 1_000_000,
                                                 "hold_latency_ns": hold * 1_000_000}))
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
                    matches = match_tool_calls(segments, episode)
                    # Three actual logged waits must survive every low-noise
                    # row, including sd=0 with quantized whole-window readings.
                    self.assertEqual(matches.matched_count, 3)
                    self.assertEqual(len(matches.unlogged_candidates), 0)
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

    def test_single_exposure_trough_survives_mixed_neighbors(self):
        # Fixed E5 worlds; seed 50 has a 250 ms wait with one clean 100 ms
        # exposure between mixed samples (12.97/6.73/5.02/9.31 W in review).
        # Durations and seeds are scenario inputs; counts are ground truth.
        for duration in (250_000_000, 500_000_000):
            for seed in (0, 50, 63):
                episode = world(seed, duration)
                timeline = timeline_from_episode(episode, model())
                for name, sensor in sensor_models(seed):
                    with self.subTest(duration=duration, seed=seed, sensor=name):
                        segments = detect_phases(simulate(timeline, sensor))
                        result = match_tool_calls(segments, episode)
                        self.assertEqual(result.matched_count, 3)  # All three true calls.
                        self.assertEqual(len(result.unlogged_candidates), 0)
                        # Consolidated edge samples cannot invent hidden turns.
                        self.assertLessEqual(sum(s.label == "prefill" for s in segments),
                                             len(episode.turns))

    def test_quantized_plateaus_keep_zero_noise_evidence(self):
        # Quantized native-rate phases: exact repeats within a plateau are
        # informative, while consecutive mixed readings show the sensor moves
        # at the poll rate. More than half the differences are exactly zero,
        # hence their MAD is exactly zero, not the scale of phase transitions.
        values = ((5.0,) * 8 + (9.0, 17.0) + (21.0,) * 8 +
                  (17.0, 13.0) + (13.0,) * 16 + (9.0, 5.0) + (5.0,) * 8)
        self.assertEqual(estimate_noise_sd(values), 0.0)
        trace = PowerTrace("mock", "x", "host.monotonic",
                           tuple((i + 1) * 100_000_000 for i in range(len(values))),
                           values, "W", 100_000_000, 100_000_000, resolution=0.01)
        segments = detect_phases(trace)
        self.assertFalse(any("held_values_cadence_inferred" in s.flags for s in segments))
        self.assertEqual([s.label for s in segments], ["idle", "prefill", "decode", "idle"])

    def test_trace_cut_inside_wait_is_indeterminate_not_unlogged(self):
        episode = world(4, 500_000_000)
        trace = simulate(timeline_from_episode(episode, model()),
                         SensorModel.ina3221(cadence_ns=1_000_000,
                                             noise_sd_w=0.05, quantum_w=0.01, seed=2))
        call = episode.turns[1].tool_calls[0]
        cut = (call.start_ns + call.end_ns) // 2  # Half of a true wait is unobserved.
        kept = [(t, v) for t, v in zip(trace.t_ns, trace.values) if t > cut]
        cropped = replace(trace, t_ns=tuple(t for t, _ in kept),
                          values=tuple(v for _, v in kept))
        result = match_tool_calls(detect_phases(cropped), episode)
        self.assertEqual(len(result.unlogged_candidates), 0)
        self.assertTrue(result.indeterminate_candidates)
        self.assertIn("tool_wait_indeterminate_trace_edge", result.flags)

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
