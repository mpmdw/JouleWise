"""Production-shaped controls for gap, resolution and local phase-label regressions."""

import json
import unittest
from dataclasses import replace

from joulewise.align.phase_detect import detect_phases, estimate_noise_sd, match_tool_calls
from joulewise.align.records import Episode, PowerTrace, ToolCall, Turn
from joulewise.align.sensor_sim import SensorModel, simulate, timeline_from_episode
from tests.align.test_phase_detect import production_sensor_models, sensor_models
from tests.align.test_sensor_sim import model, production_world, world


class PhaseReviewTwoTest(unittest.TestCase):
    def test_tool_free_client_latency_is_explained_by_every_visible_gap(self):
        for seed in (0, 1):
            base = production_world(seed, tools=False)
            gap = 20_000_000  # Production client-latency scenario, retained without tools.
            episode = replace(base, turns=tuple(replace(
                turn, start_ns=turn.start_ns + i * gap, end_ns=turn.end_ns + i * gap,
                first_token_ns=turn.first_token_ns + i * gap)
                for i, turn in enumerate(base.turns)), end_ns=base.end_ns + len(base.turns) * gap)
            for name, sensor in production_sensor_models(seed):
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
        # Production scenario: 20 turns, 1800 initial prefill tokens and
        # 30..400 decode tokens per turn, with growing context.
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

    def test_observed_mid_turn_omission_keeps_full_log_control_clean(self):
        base = world(3, 500_000_000)
        first = base.turns[0]
        original = first.tool_calls[0]
        duration = original.end_ns - original.start_ns
        middle = first.first_token_ns + (first.end_ns - first.first_token_ns) // 2
        call = replace(original, start_ns=middle, end_ns=middle + duration)
        first = replace(first, end_ns=first.end_ns + duration, tool_calls=(call,))
        episode = replace(base, turns=(first,) + base.turns[1:])
        hidden = replace(episode, turns=(replace(first, tool_calls=(replace(call, logged=False),)),)
                         + episode.turns[1:])
        for name, sensor in sensor_models(3):
            with self.subTest(sensor=name):
                phases = detect_phases(simulate(timeline_from_episode(episode, model()), sensor))
                full = match_tool_calls(phases, episode)
                self.assertEqual(full.matched_count, 3)
                self.assertEqual(len(full.unlogged_candidates), 0)
                omitted = match_tool_calls(phases, hidden)
                # 500 ms spans five 100 ms samples of the slowest sensor;
                # the visible generation envelope claims the whole call.
                self.assertTrue(any(2 * max(0, min(s.end_ns, call.end_ns) -
                                            max(s.start_ns, call.start_ns)) >= duration
                                    for s in omitted.unlogged_candidates))

    def test_unobserved_covered_call_has_identical_sensor_counterfactual(self):
        # Production token counts, two turns and a 20 ms client gap. The
        # hidden 5 ms call lies in NVML's unobserved 75 ms of each 100 ms.
        ms = 1_000_000
        call = ToolCall('lookup', 1769 * ms, 1774 * ms, 128, 2048)
        first = Turn(0, 500 * ms, 1769 * ms, 0, 512, 64,
                     first_token_ns=756 * ms, tool_calls=(call,))
        second = Turn(1, 1794 * ms, 3550 * ms, 576, 512, 96,
                      first_token_ns=2050 * ms)
        true = Episode('blind-call', 'synthetic/covered', 'benign', 'local-8b',
                       'mock:local', 3, 'host.monotonic', 0, 4050 * ms, (first, second))
        visible = replace(true, turns=(replace(first, end_ns=call.end_ns,
                          tool_calls=(replace(call, logged=False),)), second))
        counterfactual = replace(visible, turns=(replace(visible.turns[0], tool_calls=()), second))
        sensor = SensorModel.nvml(noise_sd_w=.05, quantum_w=.01, seed=3)
        tm = replace(model(), ripple_w=0)  # Valid no-surviving-ripple world.
        actual = simulate(timeline_from_episode(true, tm), sensor)
        absent = simulate(timeline_from_episode(counterfactual, tm), sensor)
        # Every exposure is disjoint from the call; this is an exact integer
        # interval property. Same sampled physical inputs and noise seed
        # give bit-identical output, so no power-only classifier can separate.
        self.assertTrue(all(min(t, call.end_ns) <= max(t - sensor.averaging_window_ns,
                                                      call.start_ns) for t in actual.t_ns))
        self.assertEqual(actual.values, absent.values)
        phases = detect_phases(actual)
        self.assertEqual(match_tool_calls(phases, visible),
                         match_tool_calls(detect_phases(absent), counterfactual))

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
                               'W', 1_000_000, conversion, resolution=.01,
                               notes=json.dumps({'register_refresh_period_ns': conversion,
                                                 'hold_latency_ns': conversion}))
            # Nonzero read-noise input must not become zero merely because
            # a conversion is held. This checks the probability endpoint.
            self.assertGreater(estimate_noise_sd(trace.values), 0)
            result = match_tool_calls(detect_phases(trace), episode)
            self.assertEqual(result.matched_count, 3)
            self.assertEqual(len(result.unlogged_candidates), 0)


if __name__ == '__main__':
    unittest.main()
