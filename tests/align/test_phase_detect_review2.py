"""Production-shaped controls for gap, resolution and local phase-label regressions."""

import unittest
from dataclasses import replace

from joulewise.align.phase_detect import detect_phases, estimate_noise_sd, match_tool_calls
from joulewise.align.records import PowerTrace
from joulewise.align.sensor_sim import SensorModel, simulate, timeline_from_episode
from tests.align.test_phase_detect import production_sensor_models, sensor_models
from tests.align.test_sensor_sim import model, production_world, world


class PhaseReviewTwoTest(unittest.TestCase):
    def test_tool_free_client_latency_is_explained_by_every_visible_gap(self):
        base = production_world(0, tools=False)
        gap = 20_000_000  # Production client-latency scenario, retained without tools.
        episode = replace(base, turns=tuple(replace(
            turn, start_ns=turn.start_ns + i * gap, end_ns=turn.end_ns + i * gap,
            first_token_ns=turn.first_token_ns + i * gap)
            for i, turn in enumerate(base.turns)), end_ns=base.end_ns + len(base.turns) * gap)
        for name, sensor in production_sensor_models(0):
            with self.subTest(sensor=name):
                result = match_tool_calls(detect_phases(simulate(
                    timeline_from_episode(episode, model()), sensor)), episode)
                self.assertEqual(len(result.unlogged_candidates), 0)

    def test_zero_ripple_cannot_shift_all_labels_by_one_quantum(self):
        for seed in (0, 5):  # Fixed failure/control seeds, not a statistical budget.
            episode = production_world(seed, 500_000_000)
            timeline = timeline_from_episode(episode, replace(model(), ripple_w=0))
            for name, sensor in production_sensor_models(seed):
                with self.subTest(seed=seed, sensor=name):
                    result = match_tool_calls(detect_phases(simulate(timeline, sensor)), episode)
                    self.assertEqual(result.matched_count, episode.totals()['tool_calls'])
                    self.assertEqual(len(result.unlogged_candidates), 0)

    def test_near_idle_waits_context_rise_and_active_only_span(self):
        # Fixed four-turn timing is production-shaped (512 prefill tokens,
        # 96 decoded tokens); replicate 20 turns via the production builder.
        episode = production_world(2, 500_000_000, turns=20, client_gap_ns=0)
        tm = replace(model(), idle_w=6, decode_w=1)
        base = timeline_from_episode(episode, tm)
        for name, sensor in sensor_models(2):
            for delta in (0.0, 0.5, 1.0):
                # 0.5 W is halfway from 6 W idle to 7 W decode. At +1 W
                # the levels coincide, so the result must name that ambiguity.
                timeline = replace(base, intervals=tuple(
                    replace(iv, mean_w=iv.mean_w + delta) if iv.label == 'tool_wait' else iv
                    for iv in base.intervals))
                with self.subTest(sensor=name, wait_delta=delta):
                    result = match_tool_calls(detect_phases(simulate(timeline, sensor)), episode)
                    self.assertEqual(len(result.unlogged_candidates), 0)
                    if delta < 1:
                        self.assertEqual(result.matched_count, episode.totals()['tool_calls'])
                    else:
                        self.assertIn('tool_wait_not_separated_from_decode_level', result.flags)
            risen = replace(base, intervals=tuple(replace(
                iv, mean_w=iv.mean_w + 3 * (iv.start_ns - episode.start_ns) /
                (episode.end_ns - episode.start_ns)) if iv.label == 'decode' else iv
                for iv in base.intervals))  # Scenario: +3 W KV-context growth.
            phases = detect_phases(simulate(risen, sensor))
            self.assertEqual(sum(s.label == 'prefill' for s in phases), len(episode.turns))
            self.assertEqual(sum(s.label == 'decode' for s in phases), len(episode.turns))
        null = production_world(2, tools=False, turns=12)
        for _, sensor in sensor_models(2):
            trace = simulate(timeline_from_episode(null, model()), sensor)
            kept = [(t, v) for t, v in zip(trace.t_ns, trace.values)
                    if null.turns[0].start_ns + sensor.averaging_window_ns < t <= null.turns[-1].end_ns]
            cropped = replace(trace, t_ns=tuple(t for t, _ in kept), values=tuple(v for _, v in kept))
            self.assertEqual(len(match_tool_calls(detect_phases(cropped), null).unlogged_candidates), 0)

    def test_held_noninteger_ratio_noise_is_nonzero_and_calls_survive(self):
        episode = world(3, 500_000_000)
        for conversion in (1_500_000, 1_900_000):
            original = simulate(timeline_from_episode(episode, replace(model(), ripple_w=0)),
                                SensorModel.ina3221(cadence_ns=conversion, noise_sd_w=.05,
                                                     quantum_w=.01, seed=3))
            times = tuple(range(original.t_ns[0], original.t_ns[-1] + 1, 1_000_000))
            values, j = [], 0
            for t in times:
                while j + 1 < len(original.t_ns) and original.t_ns[j + 1] <= t:
                    j += 1
                values.append(original.values[j])
            trace = PowerTrace('ina3221', 'VDD_IN', episode.clock_domain, times, tuple(values),
                               'W', 1_000_000, conversion, resolution=.01)
            # Nonzero read-noise input must not become zero merely because
            # a conversion is held. This checks the probability endpoint.
            self.assertGreater(estimate_noise_sd(trace.values), 0)
            result = match_tool_calls(detect_phases(trace), episode)
            self.assertEqual(result.matched_count, 3)
            self.assertEqual(len(result.unlogged_candidates), 0)


if __name__ == '__main__':
    unittest.main()
