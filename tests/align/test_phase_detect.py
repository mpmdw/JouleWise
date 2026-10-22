"""End-to-end phase and hidden-wait sensitivity on production-shaped traces."""

import json
import math
import statistics
import sys
import unittest
from dataclasses import replace

from joulewise.align.phase_detect import detect_phases, estimate_noise_sd, match_tool_calls
from joulewise.align.records import ClockMapping, PowerTrace
from joulewise.align.sensor_sim import SensorModel, simulate, timeline_from_episode
from tests.align.test_sensor_sim import model, world


def sensor_models(seed):
    # These are specified synthetic instruments, not characterized hardware.
    # 1 ms INA cadence is a scenario parameter; real Orin cadence must be measured.
    return (
        ("ina3221_1ms", SensorModel.ina3221(
            cadence_ns=1_000_000, noise_sd_w=0.05, quantum_w=0.01, seed=seed)),
        ("nvml_100ms_25ms", SensorModel.nvml(noise_sd_w=0.05, quantum_w=0.01, seed=seed)),
        ("powermetrics_100ms", SensorModel.powermetrics(
            noise_sd_w=0.05, quantum_w=0.01, seed=seed)),
    )


def run_duration_study(*, seeds=range(64), durations_ns=(
        1_000_000, 5_000_000, 10_000_000, 25_000_000, 50_000_000,
        100_000_000, 250_000_000, 500_000_000)):
    """Return empirical duration curves, including separate no-tool controls.

    90% recall and <5% episode false alarms are user-specified reporting
    conventions. They are not physical constants or confidence guarantees.
    """
    seeds = tuple(seeds)
    results = []
    for duration in durations_ns:
        totals = {}
        for seed in seeds:
            episode = world(seed, duration)
            null = world(seed, duration, tools=False)
            for name, sensor in sensor_models(seed):
                segments = detect_phases(simulate(timeline_from_episode(episode, model()), sensor))
                full = match_tool_calls(segments, episode)
                # Remove one actual call from the visible log without modifying power.
                hidden_call = episode.turns[1].tool_calls[0]
                altered = replace(episode, turns=tuple(
                    replace(t, tool_calls=tuple(replace(c, logged=False) if c == hidden_call else c
                                                for c in t.tool_calls)) for t in episode.turns))
                visible = match_tool_calls(segments, altered)
                bound = sensor.sample_interval_ns + sensor.averaging_window_ns
                hidden_detected = any(abs(s.start_ns - hidden_call.start_ns) <= bound and
                                      abs(s.end_ns - hidden_call.end_ns) <= bound
                                      for s in visible.unlogged_candidates)
                null_match = match_tool_calls(detect_phases(simulate(
                    timeline_from_episode(null, model()), sensor)), null)
                row = totals.setdefault(name, [0, 0, 0, 0, 0])
                row[0] += full.matched_count
                row[1] += episode.totals()["tool_calls"]
                row[2] += bool(full.unlogged_candidates)
                row[3] += bool(null_match.unlogged_candidates)
                row[4] += hidden_detected
        for name, row in totals.items():
            results.append(dict(sensor=name, duration_ms=duration / 1_000_000,
                                episodes=len(seeds), calls=row[1],
                                recall=row[0] / row[1],
                                hidden_call_recall=row[4] / len(seeds),
                                false_alarm_per_episode=row[2] / len(seeds),
                                null_false_alarm_per_episode=row[3] / len(seeds)))
    shortest = {}
    for row in results:
        # Targets are the reporting conventions specified by this lane brief.
        if (row["hidden_call_recall"] >= 0.90 and row["recall"] >= 0.90 and
                row["false_alarm_per_episode"] < 0.05 and
                row["null_false_alarm_per_episode"] < 0.05):
            shortest.setdefault(row["sensor"], row["duration_ms"])
    return {"rows": results, "shortest_passing_duration_ms": shortest,
            "status": "synthetic_empirical_grid_only",
            "seed_count": len(seeds), "false_alarm_rate_resolution": 1 / len(seeds)}


class PhaseDetectTest(unittest.TestCase):
    def test_episode_to_sensor_to_phase_to_omitted_call(self):
        episode = world(7, tool_duration_ns=500_000_000)
        for name, sensor in sensor_models(7):
            with self.subTest(sensor=name):
                trace = simulate(timeline_from_episode(episode, model()), sensor)
                segments = detect_phases(trace)
                full = match_tool_calls(segments, episode)
                # 90% recall is the brief's reporting bar. Three 500 ms waits
                # span >=5 samples of even the slowest 100 ms instrument.
                self.assertGreaterEqual(full.recall, 0.90)
                self.assertEqual(len(full.unlogged_candidates), 0)
                hidden = episode.turns[1].tool_calls[0]
                altered = replace(episode, turns=tuple(
                    replace(t, tool_calls=tuple(replace(c, logged=False) if c == hidden else c
                                                for c in t.tool_calls)) for t in episode.turns))
                matched = match_tool_calls(segments, altered)
                self.assertEqual(len(matched.unlogged_candidates), 1)
                self.assertIn("prefill", [s.label for s in segments])
                self.assertIn("decode", [s.label for s in segments])
                for turn in episode.turns:
                    midpoint = (turn.start_ns + turn.first_token_ns) // 2
                    covering = [s for s in segments if s.start_ns <= midpoint < s.end_ns]
                    self.assertEqual(len(covering), 1)
                    self.assertEqual(covering[0].label, "prefill")

    def test_no_tool_episode_has_no_unlogged_candidate(self):
        episode = world(9, tools=False)
        for _, sensor in sensor_models(9):
            matches = match_tool_calls(detect_phases(simulate(
                timeline_from_episode(episode, model()), sensor)), episode)
            self.assertEqual(len(matches.unlogged_candidates), 0)

    def test_clock_mapping_uses_offset_and_uncertainty(self):
        episode = world(3, tool_duration_ns=500_000_000)
        # 7 ms offset and 2 ms bracket half-width are chosen synthetic inputs.
        sensor = SensorModel.nvml(noise_sd_w=0.05, quantum_w=0.01, seed=3,
                                  clock_domain="meter.monotonic", clock_offset_ns=7_000_000)
        trace = simulate(timeline_from_episode(episode, model()), sensor)
        segments = detect_phases(trace)
        missing = match_tool_calls(segments, episode)
        self.assertIn("clock_mapping_unavailable_or_ambiguous", missing.flags)
        mapped = replace(episode, power_traces=(trace,), clock_mappings=(
            ClockMapping(trace.clock_domain, episode.clock_domain, 7_000_000,
                         2_000_000, "synthetic bracket"),))
        result = match_tool_calls(segments, mapped)
        self.assertEqual(result.matched_count, 3)
        # 100 ms sampling + 25 ms averaging + 2 ms offset half-width.
        self.assertEqual(result.tolerance_ns, 127_000_000)

    def test_independent_direct_sse_split_oracle_and_noise_penalty(self):
        # Direct residual summation and exhaustive split enumeration, independent
        # arithmetic design from gpt-6-astra; production uses centered prefix sums.
        values = (5.0,) * 32 + (13.0,) * 32

        def sse(xs):
            mean = math.fsum(xs) / len(xs)
            return math.fsum((x - mean) ** 2 for x in xs)

        gains = [(sse(values) - sse(values[:k]) - sse(values[k:]), k)
                 for k in range(1, len(values))]
        gain, split = max(gains)
        # Added mean + location => 2 parameters, known-noise SSE-unit BIC.
        critical_sigma = math.sqrt(gain / (2 * math.log(len(values))))
        trace = PowerTrace("mock", "power", "host.monotonic",
                           tuple((i + 1) * 1_000_000 for i in range(len(values))),
                           values, "W", 1_000_000)
        # Half/double the critical variance gives clear decisions either side;
        # factors follow the inequality, not an empirically tuned noise cutoff.
        low = detect_phases(trace, noise_sd_w=critical_sigma / math.sqrt(2))
        high = detect_phases(trace, noise_sd_w=critical_sigma * math.sqrt(2))
        self.assertEqual(len(low), 2)
        self.assertEqual(low[0].end_ns, split * 1_000_000)
        self.assertEqual(len(high), 1)

    def test_inverted_duration_order_is_flagged(self):
        # Deliberately violate the synthetic rule: the highest level lasts
        # twice as long as the middle level, so the labels are ambiguous.
        values = (5.0,) * 10 + (13.0,) * 20 + (21.0,) * 40 + (5.0,) * 10
        trace = PowerTrace("mock", "x", "host.monotonic",
                           tuple((i + 1) * 1_000_000 for i in range(len(values))),
                           values, "W", 1_000_000, 1_000_000)
        self.assertTrue(any("level_duration_model_mismatch" in s.flags
                            for s in detect_phases(trace, noise_sd_w=0)))

    def test_noise_estimator_and_failure_flags(self):
        import random
        rng = random.Random(42)
        sigma, count = 0.05, 10000
        observed = estimate_noise_sd(tuple(rng.gauss(5, sigma) for _ in range(count)))
        # A Gaussian MAD has asymptotic relative SE 1/(4*q*phi(q)*sqrt(n)),
        # q=Phi^-1(.75). Adjacent differences share one input; sqrt(3) bounds
        # variance inflation for a one-dependent series. The 99% confidence
        # level is a stated test reporting convention, not a sensor constant.
        normal = statistics.NormalDist()
        q = normal.inv_cdf(0.75)
        phi = math.exp(-q*q/2) / math.sqrt(math.tau)
        bound = normal.inv_cdf(0.995) * math.sqrt(3) * sigma / (4*q*phi*math.sqrt(count))
        self.assertLess(abs(observed - sigma), bound)
        cumulative = PowerTrace("nvml_energy", "gpu0", "host.monotonic",
                                (0, 100_000_000), (0, 1), "J_cumulative", 100_000_000)
        self.assertIn("unsupported_cumulative_energy", detect_phases(cumulative)[0].flags)
        empty = PowerTrace("mock", "x", "host.monotonic", (), (), "W", 1_000_000)
        self.assertIn("empty_trace", detect_phases(empty)[0].flags)
        gapped = PowerTrace("mock", "x", "host.monotonic",
                            (1_000_000, 2_000_000, 100_000_000), (5, 5, 5), "W", 1_000_000)
        self.assertIn("sample_gaps", detect_phases(gapped)[0].flags)
        self.assertIn("averaging_window_unknown", detect_phases(gapped)[0].flags)


if __name__ == "__main__":
    if "--study" in sys.argv:
        print(json.dumps(run_duration_study(), sort_keys=True, indent=2))
    else:
        unittest.main()
