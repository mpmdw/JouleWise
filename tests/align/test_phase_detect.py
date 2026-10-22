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
from tests.align.test_sensor_sim import model, production_world, world


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


def production_sensor_models(seed, *, ina_cadence_ns=1_000_000,
                             shunt_resistance_ohm=0.005,
                             operating_voltage_v=5.0, operating_current_a=2.0,
                             noise_sd_by_sensor=None):
    """Resolution-derived study instruments, distinct from fixed repro worlds.

    INA cadence is an explicit scenario input, not measured Orin evidence.
    P3767 L4T device tree: shunt-resistor-micro-ohms = <5000> (OE4T mirror,
    patches-rel-36/tegra234-p3767.dtsi). Verify the borrowed board's DT.
    Independent Gaussian read sd defaults to one uniform LSB / sqrt(12);
    actual read noise is unknown and can be supplied per sensor.
    """
    # INA3221: bus LSB 8 mV, shunt LSB 40 uV. I=Vshunt/R.
    dv = 8e-3
    di = 40e-6 / shunt_resistance_ohm
    ina_quantum = abs(operating_voltage_v) * di + abs(operating_current_a) * dv + dv * di
    quanta = {"ina3221_1ms": ina_quantum,
              "nvml_100ms_25ms": 1e-3,  # NVML power usage is integer mW.
              "powermetrics_100ms": 1e-3}  # Selected mW output precision.
    supplied = noise_sd_by_sensor or {}
    noise = {key: supplied.get(key, quantum / math.sqrt(12)) for key, quantum in quanta.items()}
    return (
        ("ina3221_1ms", SensorModel.ina3221(
            cadence_ns=ina_cadence_ns, noise_sd_w=noise["ina3221_1ms"],
            quantum_w=ina_quantum, seed=seed)),
        ("nvml_100ms_25ms", SensorModel.nvml(
            noise_sd_w=noise["nvml_100ms_25ms"], quantum_w=1e-3, seed=seed)),
        ("powermetrics_100ms", SensorModel.powermetrics(
            noise_sd_w=noise["powermetrics_100ms"], quantum_w=1e-3, seed=seed)),
    )


def clopper_pearson(successes, trials, *, confidence=0.95):
    """Exact equal-tail binomial interval; confidence is a reporting convention."""
    if not trials:
        return (0.0, 1.0)  # No observations: the entire probability space.
    alpha = 1 - confidence

    def cdf(k, p):
        if p <= 0:
            return 1.0
        if p >= 1:
            return 1.0 if k >= trials else 0.0
        # Log-sum-exp avoids underflow for minute-scale call counts.
        logs = [math.lgamma(trials + 1) - math.lgamma(j + 1) -
                math.lgamma(trials - j + 1) + j * math.log(p) +
                (trials - j) * math.log1p(-p) for j in range(k + 1)]
        largest = max(logs)
        return min(1.0, math.exp(largest) * math.fsum(math.exp(x - largest) for x in logs))

    def invert(k, target):
        left, right = 0.0, 1.0
        # Binary64 has sys.float_info.mant_dig bits of precision; after that
        # many bisections the interval cannot contain distinguishable points.
        for _ in range(sys.float_info.mant_dig):
            middle = (left + right) / 2
            if cdf(k, middle) > target:
                left = middle
            else:
                right = middle
        return (left + right) / 2

    lower = invert(successes - 1, 1 - alpha / 2) if successes else 0.0
    upper = invert(successes, alpha / 2) if successes < trials else 1.0
    return (lower, upper)


def run_duration_study(*, seeds=range(64), durations_ns=(
        1_000_000, 5_000_000, 10_000_000, 25_000_000, 50_000_000,
        100_000_000, 250_000_000, 500_000_000), turns=30,
        client_gap_ns=20_000_000, sensors=production_sensor_models):
    """Production worlds with isolated and shared-run omission controls.

    90% recall and <5% episode false alarms are brief reporting conventions;
    64 seeds is a configurable computational budget. CP bounds use one
    independently seeded Bernoulli trial per episode: one uniformly chosen
    omitted call, an isolated/shared control, or any episode false alarm. Pooled
    call recall is descriptive, not incorrectly treated as independent calls.
    """
    seeds = tuple(seeds)
    results = []
    for duration in durations_ns:
        totals = {}
        for seed in seeds:
            episode = production_world(seed, duration, turns=turns, client_gap_ns=client_gap_ns)
            null = production_world(seed, duration, tools=False, turns=turns)
            timeline = timeline_from_episode(episode, model())
            null_timeline = timeline_from_episode(null, model())
            isolated = episode.turns[0].tool_calls[0]
            shared = episode.turns[1].tool_calls[-1]  # Immediately after another logged call.
            def omit(call):
                return replace(episode, turns=tuple(
                    replace(turn, tool_calls=tuple(
                        replace(c, logged=False) if c == call else c for c in turn.tool_calls))
                    for turn in episode.turns))
            import random
            mixed = random.Random(seed).choice([c for t in episode.turns for c in t.tool_calls])
            isolated_log, shared_log, mixed_log = omit(isolated), omit(shared), omit(mixed)
            for name, sensor in sensors(seed):
                segments = detect_phases(simulate(timeline, sensor))
                full = match_tool_calls(segments, episode)
                hidden = match_tool_calls(segments, isolated_log)
                hidden_shared = match_tool_calls(segments, shared_log)
                hidden_mixed = match_tool_calls(segments, mixed_log)
                # The log implies call.end + client gap as the trough end.
                def found(match, call):
                    return any(abs(s.start_ns - call.start_ns) <= match.tolerance_ns and
                               s.end_ns >= call.end_ns - match.tolerance_ns and
                               s.end_ns <= call.end_ns + client_gap_ns + match.tolerance_ns
                               for s in match.unlogged_candidates)
                isolated_detected = found(hidden, isolated)
                shared_detected = found(hidden_shared, shared)
                null_match = match_tool_calls(detect_phases(simulate(null_timeline, sensor)), null)
                row = totals.setdefault(name, dict(matched=0, calls=0, false=0, null_false=0,
                                                  hidden=0, isolated_hidden=0, shared_hidden=0, true_prefills=0,
                                                  detected_prefills=0, duration_ns=0,
                                                  shared_concealed=0, shared_trials=0,
                                                  sensor=dict(interval_ns=sensor.sample_interval_ns,
                                                              window_ns=sensor.averaging_window_ns,
                                                              quantum_w=sensor.quantum_w,
                                                              noise_sd_w=sensor.noise_sd_w)))
                row["matched"] += full.matched_count
                row["calls"] += episode.totals()["tool_calls"]
                row["false"] += bool(full.unlogged_candidates)
                row["null_false"] += bool(null_match.unlogged_candidates)
                row["hidden"] += found(hidden_mixed, mixed)
                row["isolated_hidden"] += isolated_detected
                row["shared_hidden"] += shared_detected
                # Measure the identifiability limit only when the full trace
                # detected the underlying run; otherwise it is a sensor miss.
                shared_run_seen = shared not in full.unmatched_logged
                row["shared_trials"] += shared_run_seen
                row["shared_concealed"] += shared_run_seen and not shared_detected
                row["true_prefills"] += len(episode.turns)
                row["detected_prefills"] += sum(s.label == "prefill" for s in segments)
                row["duration_ns"] += episode.end_ns - episode.start_ns
        for name, row in totals.items():
            count = len(seeds)
            results.append(dict(
                sensor=name, duration_ms=duration / 1_000_000, episodes=count, calls=row["calls"],
                recall=row["matched"] / row["calls"],
                pooled_logged_call_recall=row["matched"] / row["calls"],
                hidden_call_recall=row["hidden"] / count,
                hidden_call_recall_95=clopper_pearson(row["hidden"], count),
                isolated_hidden_call_recall=row["isolated_hidden"] / count,
                isolated_hidden_call_recall_95=clopper_pearson(row["isolated_hidden"], count),
                shared_run_hidden_call_recall=row["shared_hidden"] / count,
                shared_run_hidden_call_recall_95=clopper_pearson(row["shared_hidden"], count),
                shared_run_concealed=row["shared_concealed"], shared_run_trials=row["shared_trials"],
                shared_run_concealment_rate=(row["shared_concealed"] / row["shared_trials"]
                                            if row["shared_trials"] else None),
                false_alarm_per_episode=row["false"] / count,
                false_alarm_per_episode_95=clopper_pearson(row["false"], count),
                null_false_alarm_per_episode=row["null_false"] / count,
                null_false_alarm_per_episode_95=clopper_pearson(row["null_false"], count),
                detected_prefills=row["detected_prefills"], true_prefills=row["true_prefills"],
                mean_episode_duration_s=row["duration_ns"] / count / 1e9,
                sensor_parameters=row["sensor"]))
    shortest, bounded, isolated_shortest, isolated_bounded = {}, {}, {}, {}
    for row in results:
        # Targets are supplied reporting conventions, not fitted constants.
        if (row["hidden_call_recall"] >= 0.90 and row["recall"] >= 0.90 and
                row["false_alarm_per_episode"] < 0.05 and row["null_false_alarm_per_episode"] < 0.05):
            shortest.setdefault(row["sensor"], row["duration_ms"])
        if (row["hidden_call_recall_95"][0] >= 0.90 and row["false_alarm_per_episode_95"][1] < 0.05 and
                row["null_false_alarm_per_episode_95"][1] < 0.05):
            bounded.setdefault(row["sensor"], row["duration_ms"])
        if (row["isolated_hidden_call_recall"] >= 0.90 and row["recall"] >= 0.90 and
                row["false_alarm_per_episode"] < 0.05 and row["null_false_alarm_per_episode"] < 0.05):
            isolated_shortest.setdefault(row["sensor"], row["duration_ms"])
        if (row["isolated_hidden_call_recall_95"][0] >= 0.90 and
                row["false_alarm_per_episode_95"][1] < 0.05 and
                row["null_false_alarm_per_episode_95"][1] < 0.05):
            isolated_bounded.setdefault(row["sensor"], row["duration_ms"])
    return {"rows": results, "shortest_passing_duration_ms": shortest,
            "shortest_passing_duration_ms_from_95_bounds": bounded,
            "isolated_only_shortest_passing_duration_ms": isolated_shortest,
            "isolated_only_shortest_passing_duration_ms_from_95_bounds": isolated_bounded,
            "hidden_recall_estimand": "one uniformly chosen unlogged call per independently seeded episode",
            "shared_run_control": "hide the second back-to-back call; report concealment separately",
            "status": "synthetic_grid_only", "seed_count": len(seeds), "turns": turns,
            "client_gap_ns": client_gap_ns, "false_alarm_rate_resolution": 1 / len(seeds),
            "needs_ruling": ({"question": "Use point estimates or 95% bounds for shortest-duration reporting?",
                              "point_estimates_ms": shortest, "bounds_ms": bounded,
                              "isolated_only_point_estimates_ms": isolated_shortest,
                              "isolated_only_bounds_ms": isolated_bounded,
                              "recommendation": "print both; treat bounds as the supported limit"}
                             if shortest != bounded or isolated_shortest != isolated_bounded else None)}


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
                    replace(t, end_ns=max(t.end_ns, hidden.end_ns) if hidden in t.tool_calls else t.end_ns,
                            tool_calls=tuple(replace(c, logged=False) if c == hidden else c
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
