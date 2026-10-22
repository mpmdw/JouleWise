"""End-to-end synthetic Stage B worlds and independent numerical comparisons."""

from __future__ import annotations

import math
import json
import random
import statistics
import unittest
from dataclasses import replace

from joulewise.align.records import ClockMapping, Episode, RouterLog, from_json, to_json
from joulewise.align.moe_stage_b import (
    OffloadConfig, PowerPulse, SensorModel, TokenWindow, TrafficResult,
    TransferPulse, decode_reuse, episode_token_windows, expert_size_from_config,
    extract_features, model_traffic, pearson, plan_detectability,
    recover_routing, required_correlation, simulate_episode, simulate_trace,
    nvml_sensor,
)
from joulewise.align.moe_stage_b.analysis import RoutingObservation
from joulewise.align.moe_stage_b.experiment import (
    WorldConfig, default_sensors, run_world, synthetic_episode, world_offload,
)
from joulewise.align.moe_stage_b.reference import (
    reference_transfers, reference_window_samples, reference_pearson,
    reference_linear_prediction, reference_required_correlation,
    reference_interval_energies, reference_spectrum_amplitude,
    reference_detection_forecast,
)


class StageBAssertions(unittest.TestCase):
    def assertRelative(self, actual: float, expected: float, *, scale: float = 0.0) -> None:
        # No uncertainty is attached to deterministic algebra: brief rule 3
        # specifies 1e-6 relative. scale is a named input scale for zero results.
        self.assertLessEqual(abs(actual-expected), 1e-6*max(abs(expected), scale))


def small_config(**changes) -> OffloadConfig:
    # Ten-byte tensors intentionally make cache policy hand-checkable. Their
    # integer accounting is checked separately from realistic-sized worlds.
    config = OffloadConfig({0: 10}, frozenset(), 20, "slru", 1e9, 1e-9,
                            "synthetic-memory", "fixture parameter", "fixture parameter",
                            prefill_mode="serial")
    return replace(config, **changes)


def one_layer(ids, *, phases=None, top_k=1) -> RouterLog:
    return RouterLog("synthetic-policy", 64, top_k, (0,),
                     tuple(phases or ("decode",)*len(ids)),
                     tuple((tuple(row),) for row in ids))


class TestMoeStageBTraffic(StageBAssertions):
    def test_expert_storage_from_architecture_and_blocks(self):
        result = expert_size_from_config(
            {"hidden_size": 2048, "intermediate_size": 1024},
            block_elements=32, block_bytes=18)
        # Three 2048x1024 gated-FFN matrices; Q4_0 stores 32 weights in 18 bytes.
        self.assertEqual(result.bytes_per_expert, 3_538_944)
        self.assertFalse(result.flags)
        qwen = expert_size_from_config(
            {"hidden_size": 2048, "moe_intermediate_size": 1024, "intermediate_size": 8192},
            block_elements=32, block_bytes=18)
        self.assertEqual(qwen.bytes_per_expert, result.bytes_per_expert)
        bad = expert_size_from_config({"hidden_size": 33, "intermediate_size": 32},
                                      block_elements=32, block_bytes=18)
        self.assertIn("quantized_rows_not_block_aligned", bad.flags)

    def test_lru_and_slru_have_different_physical_miss_counts(self):
        log = one_layer([(0,), (1,), (0,), (2,), (3,), (0,)])
        for policy, expected in (
                ("lru", (10, 10, 0, 10, 10, 10)),
                ("slru", (10, 10, 0, 10, 10, 0))):
            traffic = model_traffic(log, small_config(cache_policy=policy))
            self.assertEqual(tuple(t.bytes_moved for t in traffic.tokens), expected)
            oracle = reference_transfers(log, small_config(cache_policy=policy))
            self.assertEqual(tuple(t.bytes_moved for t in traffic.tokens),
                             tuple(t.moved_bytes for t in oracle))
            self.assertRelative(traffic.total_energy_j, sum(expected)*1e-9)

    def test_request_hits_are_protected_before_misses(self):
        log = one_layer([(0, 1), (2, 0), (0, 2)], top_k=2)
        traffic = model_traffic(log, small_config(cache_policy="lru"))
        # Token 2 touches its selected hit (0) before filling miss (2), evicting
        # unselected 1. Both selected experts therefore hit on token 3.
        self.assertEqual(tuple(t.bytes_moved for t in traffic.tokens), (20, 10, 0))

    def test_independent_oracle_on_real_sized_multiturn_routes(self):
        world = WorldConfig(turns=2)
        episode = synthetic_episode(world, group=0, condition="sabotage", hot_probability=0.45)
        base = world_offload(world)
        timing = episode_token_windows(episode)
        for policy in ("none", "lru", "slru"):
            for batch in (1, world.prefill_tokens_per_turn):
                config = replace(base, cache_policy=policy, prefill_batch_tokens=batch)
                traffic = model_traffic(episode.router_log, config, windows=timing.windows)
                oracle = reference_transfers(episode.router_log, config)
                self.assertEqual(tuple(t.bytes_moved for t in traffic.tokens),
                                 tuple(t.moved_bytes for t in oracle))
                for actual, expected in zip(traffic.tokens, oracle):
                    self.assertRelative(actual.energy_j, expected.energy_j,
                                        scale=config.joules_per_byte)

    def test_layer_keys_and_pinned_residency(self):
        log = RouterLog("layers", 64, 1, (3, 9), ("decode", "decode"),
                        (((0,), (0,)), ((0,), (0,))))
        config = small_config(expert_bytes={3: 10, 9: 20},
                              resident=frozenset({(3, 0)}), cache_capacity_bytes=20)
        traffic = model_traffic(log, config)
        self.assertEqual(tuple(t.bytes_moved for t in traffic.tokens), (20, 0))
        self.assertEqual(tuple(t.resident_hits for t in traffic.tokens), (1, 1))

    def test_batch_union_and_capacity_are_explicit(self):
        log = one_layer([(0, 1), (1, 2), (0, 2), (0, 1)],
                        phases=("prefill", "prefill", "decode", "decode"), top_k=2)
        config = small_config(prefill_mode="bypass", prefill_batch_tokens=2)
        traffic = model_traffic(log, config)
        # A two-token batch needs experts {0,1,2} once: 30 bytes; prefill does
        # not warm the dynamic cache, so the first decode loads {0,2}.
        self.assertEqual(tuple(t.bytes_moved for t in traffic.tokens), (20, 10, 20, 10))
        self.assertEqual(traffic.tokens[1].batch_reuse, 1)
        self.assertIn("prefill_batch_union_profile_assumption", traffic.flags)
        tiny = model_traffic(log, replace(config, cache_capacity_bytes=10))
        self.assertIn("request_exceeds_cache_capacity", tiny.flags)
        self.assertEqual(tiny.tokens[-1].bytes_moved, 20)

    def test_mixed_size_slru_and_ordered_multi_hit_match_oracle(self):
        rng = random.Random(20261022)
        log = RouterLog("mixed-layout-sensitivity", 64, 2, (0, 1),
                        ("decode",)*128,
                        tuple(tuple(tuple(rng.sample(range(6), 2)) for _ in range(2))
                              for _ in range(128)))
        # The byte budget deliberately spans unequal 10/15-byte experts.
        # Its odd 49-byte capacity also exercises the floor(capacity/2) rule.
        config = small_config(expert_bytes={0: 10, 1: 15}, cache_capacity_bytes=49)
        actual, expected = model_traffic(log, config), reference_transfers(log, config)
        self.assertEqual(tuple(t.bytes_moved for t in actual.tokens),
                         tuple(t.moved_bytes for t in expected))
        ordered = one_layer([(0, 1), (1, 0), (2, 3), (0, 2)], top_k=2)
        actual = model_traffic(ordered, small_config(cache_capacity_bytes=30))
        expected = reference_transfers(ordered, small_config(cache_capacity_bytes=30))
        # Correct first-occurrence hit order retains expert 0; sorting those
        # touches instead evicts 0 and adds ten bytes on the final request.
        self.assertEqual(tuple(t.bytes_moved for t in actual.tokens), (20, 0, 20, 0))
        self.assertEqual(tuple(t.bytes_moved for t in actual.tokens),
                         tuple(t.moved_bytes for t in expected))

    def test_invalid_inputs_are_flags_and_do_not_refuse(self):
        log = one_layer([(0,)])
        for config, flag in (
                (small_config(bandwidth_bytes_s=math.nan), "invalid_bandwidth"),
                (small_config(energy_source=""), "missing_parameter_provenance"),
                (small_config(cache_policy="mystery"), "invalid_cache_policy"),
                (small_config(prefill_batch_tokens=0), "invalid_prefill_batch_size"),
                (small_config(expert_bytes={}), "missing_or_invalid_expert_size")):
            self.assertIn(flag, model_traffic(log, config).flags)
        self.assertIn("invalid_token_windows", model_traffic(
            log, small_config(), windows=(TokenWindow(0, 10, 10),)).flags)

    def test_overloaded_link_retains_energy_and_flags_queued_work(self):
        log = one_layer([(0,), (1,)])
        windows = (TokenWindow(0, 0, 1_000_000), TokenWindow(1, 1_000_000, 2_000_000))
        traffic = model_traffic(log, small_config(bandwidth_bytes_s=1000.0), windows=windows)
        self.assertIn("transfer_exceeds_token_window", traffic.flags)
        self.assertEqual(traffic.total_bytes, 20)
        self.assertEqual(traffic.pulses[-1].end_ns, 20_000_000)


class TestMoeStageBSensors(StageBAssertions):
    def test_sensor_cadence_and_quantum_come_from_rail_parameters(self):
        ina, nvml = default_sensors()
        # Three enabled channels, each 1.1ms shunt + 1.1ms bus: 6.6ms.
        # Polling is 10ms, so effective independent read interval is 10ms.
        self.assertEqual(ina.averaging_window_ns, 6_600_000)
        self.assertEqual(ina.interval_ns, 10_000_000)
        # P=VI; 40uV/10mOhm * 5V + 8mV*2A + product of both LSBs.
        self.assertRelative(ina.quantum_w, 0.036032)
        self.assertEqual(nvml.interval_ns, 100_000_000)
        self.assertEqual(nvml.averaging_window_ns, 25_000_000)

    def test_analytic_sensor_acquisition_matches_independent_overlap_oracle(self):
        traffic = TrafficResult((), (
            TransferPulse(0, 0, 2_000_000_000, 4000, 4.0),
            TransferPulse(1, 1_500_000_000, 2_200_000_000, 2000, 0.7)))
        loads = (PowerPulse(1_000_000_000, 3_000_000_000, 1.0),)
        sensor = SensorModel("fixture", "mock", "test", 100_000_000,
                             250_000_000, 0.001, 0.0, phase_ns=17_000_000)
        sampled = simulate_trace(traffic, sensor, start_ns=0, end_ns=3_000_000_000,
                                 clock_domain="test", baseline_w=3.0, loads=loads)
        trace = sampled.trace
        expected = reference_window_samples(
            trace.t_ns, sensor.averaging_window_ns,
            transfers=tuple((p.start_ns, p.end_ns, p.energy_j) for p in traffic.pulses),
            loads=tuple((p.start_ns, p.end_ns, p.watts) for p in loads), baseline_watts=3.0)
        # Compare the same quantized observable. q/400 is below 1% of its q/2
        # displayed half-width and far above 1e6 floating rounding noise here.
        bar = sensor.quantum_w/400
        for actual, raw in zip(trace.values, expected):
            self.assertLessEqual(abs(actual-round(raw/sensor.quantum_w)*sensor.quantum_w), bar)
        self.assertIn("overlapping_acquisition_windows", sampled.flags)

    def test_nvml_blind_phase_and_visible_phase_exercise_real_simulator(self):
        # A 1J/10ms (100W) transfer every 100ms is large compared with the
        # 0.001W reporting quantum, yet fits wholly inside the 75ms blind gap.
        pulses = tuple(TransferPulse(i, i*100_000_000, i*100_000_000+10_000_000,
                                     1_000_000, 1.0) for i in range(10))
        traffic = TrafficResult((), pulses)
        traces = []
        for phase in (50_000_000, 10_000_000):
            traces.append(simulate_trace(
                traffic, nvml_sensor(noise_std_w=0.0, quantum_w=0.001, phase_ns=phase),
                start_ns=0, end_ns=1_000_000_000, clock_domain="test", baseline_w=10.0).trace)
        quantum = traces[0].resolution
        self.assertLessEqual(max(abs(v-10.0) for v in traces[0].values), quantum/2)
        # The visible window contains 1J over 25ms: exactly 40W extra.
        self.assertLessEqual(abs(max(traces[1].values)-10.0-1.0/0.025), quantum/400)

    def test_missing_sensor_data_is_flagged(self):
        sensor = replace(default_sensors()[0], interval_ns=0)
        result = simulate_trace(TrafficResult((), ()), sensor, start_ns=0,
                                end_ns=1_000_000_000, clock_domain="test", baseline_w=8.0)
        self.assertIsNone(result.trace)
        self.assertIn("invalid_sensor_or_profile", result.flags)


class TestMoeStageBAnalysis(StageBAssertions):
    @classmethod
    def setUpClass(cls):
        cls.world = WorldConfig(turns=3)
        episode = synthetic_episode(cls.world, group=0, condition="benign", hot_probability=0.8)
        cls.sensor = replace(default_sensors()[0], noise_std_w=0.0, phase_ns=3_000_000)
        cls.simulated = simulate_episode(
            episode, world_offload(cls.world), cls.sensor,
            baseline_w=cls.world.baseline_w, prefill_load_w=cls.world.prefill_load_w,
            decode_load_w=cls.world.decode_load_w, tool_load_w=cls.world.tool_load_w)

    def features(self, episode=None, trace=None):
        episode = episode or self.simulated.episode
        trace = trace or episode.power_traces[-1]
        return extract_features(episode, trace,
                                baseline_w=self.world.baseline_w+self.world.decode_load_w,
                                noise_std_w=0.0, noise_multiplier=1.0, attribution_floor_j=0.0)

    def test_decode_features_match_independent_interval_and_spectrum(self):
        episode = self.simulated.episode
        trace = episode.power_traces[-1]
        features = self.features()
        timing = episode_token_windows(episode)
        windows = [(w.start_ns, w.end_ns) for w, p in
                   zip(timing.windows, episode.router_log.phase) if p == "decode"]
        expected = reference_interval_energies(trace, windows,
                                               self.world.baseline_w+self.world.decode_load_w)
        self.assertRelative(features.energy_per_decode_token_j, statistics.fmean(expected))
        self.assertRelative(features.token_energy_variance_j2, statistics.pvariance(expected))
        weights = [sum(max(0, min(t, right)-max(
            max(t-trace.nominal_interval_ns, trace.t_ns[i-1] if i else t-trace.nominal_interval_ns),
            left))/1e9 for left, right in windows) for i, t in enumerate(trace.t_ns)]
        selected = [(t, v, w) for t, v, w in zip(trace.t_ns, trace.values, weights) if w]
        amplitude = reference_spectrum_amplitude(
            [t for t, _, _ in selected], [v for _, v, _ in selected],
            [w for _, _, w in selected], features.token_rate_hz, episode.start_ns)
        self.assertRelative(features.token_rate_amplitude_w, amplitude)
        self.assertRelative(features.coverage_fraction, 1.0)

    def test_clock_mapping_and_shared_record_round_trip(self):
        episode = from_json(Episode, to_json(self.simulated.episode))
        trace = episode.power_traces[-1]
        # A 2-second sensor-clock offset is exact fixture metadata; 1ms mapping
        # uncertainty is separately propagated to the reported energy bound.
        shifted = replace(trace, clock_domain="sensor", t_ns=tuple(t-2_000_000_000 for t in trace.t_ns))
        mapped = replace(episode, power_traces=(shifted,), clock_mappings=(
            ClockMapping("sensor", episode.clock_domain, 2_000_000_000, 1_000_000, "fixture"),))
        actual, expected = self.features(mapped), self.features(episode)
        self.assertRelative(actual.energy_per_decode_token_j, expected.energy_per_decode_token_j)
        self.assertGreater(actual.energy_half_width_per_token_j, expected.energy_half_width_per_token_j)
        self.assertIn("clock_mapping_uncertainty", actual.flags)

    def test_missing_coverage_and_missing_router_are_flags(self):
        episode = self.simulated.episode
        trace = replace(episode.power_traces[-1], t_ns=(episode.end_ns+10_000_000_000,), values=(8.0,))
        features = self.features(episode, trace)
        self.assertIsNone(features.energy_per_decode_token_j)
        self.assertIn("no_decode_sample_coverage", features.flags)
        bad = replace(episode, router_log=None)
        self.assertIn("missing_router_log", simulate_episode(
            bad, world_offload(self.world), self.sensor, baseline_w=8.0,
            prefill_load_w=6.0, decode_load_w=4.0, tool_load_w=1.0).flags)

    def test_missing_samples_are_not_filled(self):
        episode = self.simulated.episode
        trace = episode.power_traces[-1]
        # Drop every second sensor update: a full nominal interval is missing
        # each time, much larger than timestamp or floating-point precision.
        sparse = replace(trace, t_ns=trace.t_ns[::2], values=trace.values[::2])
        result = self.features(episode, sparse)
        self.assertIn("incomplete_decode_coverage", result.flags)
        self.assertIn("irregular_sample_cadence", result.flags)
        self.assertLess(result.coverage_fraction, 1.0)

    def test_grouped_predictions_match_independent_held_out_regression(self):
        original = self.features()
        observations = tuple(RoutingObservation(
            str(i), f"task-{i//2}", 0.1+0.05*i,
            replace(original, energy_per_decode_token_j=0.01+0.003*i+0.0001*(i%2)))
            for i in range(12))
        result = recover_routing(observations, feature_name="energy_per_decode_token_j")
        for observation, (_, actual) in zip(observations, result.predictions):
            train = [o for o in observations if o.group != observation.group]
            expected = reference_linear_prediction(
                [o.features.energy_per_decode_token_j for o in train],
                [o.routing_statistic for o in train],
                [observation.features.energy_per_decode_token_j])[0]
            self.assertRelative(actual, expected)
        self.assertRelative(result.observed_correlation, reference_pearson(
            [o.routing_statistic for o in observations],
            [o.features.energy_per_decode_token_j for o in observations]))
        # One task group cannot train itself, even when the linear relation is exact.
        isolated = recover_routing([replace(o, group="same-task") for o in observations],
                                  feature_name="energy_per_decode_token_j")
        self.assertTrue(all(value is None for _, value in isolated.predictions))
        self.assertIn("insufficient_grouped_training_data", isolated.flags)

    def test_parameterized_detection_requirement_and_forecast(self):
        kwargs = dict(stage_a_effect_sd=1.0, n_per_condition=50, alpha=0.05,
                      power=0.8, comparisons=3)
        requirement = required_correlation(**kwargs)
        expected = reference_required_correlation(1.0, 50, alpha=0.05, power=0.8, comparisons=3)
        self.assertRelative(requirement.minimum_absolute_correlation, expected.minimum_correlation)
        sensor = default_sensors()[0]
        forecast = plan_detectability(
            sensor, **kwargs, routing_stat_sd=0.2, traffic_energy_slope_j_per_token=0.05,
            decode_tokens=512, decode_duration_s=25.6, phase_bias_std_j=0.1,
            systematic_contrast_half_width_j=1.0)
        oracle = reference_detection_forecast(
            sensor.noise_std_w, sensor.interval_ns, sensor.averaging_window_ns,
            sensor.quantum_w, 0.2, 0.05, 512, 25.6, 0.1, 1.0, 1.0)
        self.assertRelative(forecast.model_correlation, oracle.model_correlation)
        self.assertRelative(forecast.contrast_energy_j, oracle.contrast_j)
        self.assertRelative(forecast.contrast_half_width_j, oracle.contrast_half_width_j)
        # A 100-fold smaller Stage A effect demands 100-fold greater correlation;
        # since correlations cannot exceed 1, this design becomes impossible.
        impossible = required_correlation(**dict(kwargs, stage_a_effect_sd=0.01))
        self.assertFalse(impossible.feasible)
        self.assertIn("required_correlation_exceeds_one", impossible.flags)
        self.assertIn("stage_a_has_no_effect", required_correlation(
            **dict(kwargs, stage_a_effect_sd=0.0)).flags)
        self.assertIsNone(pearson((1.0, 1.0), (0.0, 1.0)))

    def test_finite_scale_correlation_and_invalid_design_edges(self):
        for scale in (1e-100, 1e100):
            # Scale changes units, not correlation. The old variance product
            # underflowed/overflowed although each independent variance was finite.
            values = tuple(scale*i for i in (1, 2, 3))
            self.assertRelative(pearson(values, values), reference_pearson(values, values))
        base = dict(stage_a_effect_sd=1.0, n_per_condition=50,
                    alpha=0.05, power=0.8, comparisons=3)
        for count in (math.inf, 1.5, True):
            self.assertIn("invalid_detection_design", required_correlation(
                **dict(base, n_per_condition=count)).flags)
        # Smallest positive binary64 alpha: dividing it by 2 underflows.
        self.assertIn("design_tail_below_float_range", required_correlation(
            **dict(base, alpha=float.fromhex("0x0.0000000000001p-1022"), comparisons=1)).flags)
        self.assertTrue(required_correlation(**dict(base, power=0.5)).feasible)
        forecast = plan_detectability(
            default_sensors()[0], **dict(base, stage_a_effect_sd=math.nan),
            routing_stat_sd=0.2, traffic_energy_slope_j_per_token=0.05,
            decode_tokens=512, decode_duration_s=25.6, phase_bias_std_j=0.1,
            systematic_contrast_half_width_j=1.0)
        self.assertIsNone(forecast.contrast_energy_j)
        self.assertIn("invalid_sensor_forecast", forecast.flags)

    def test_forecast_rejects_noninteger_token_and_sensor_time_inputs_with_flags(self):
        sensor = default_sensors()[0]
        base = dict(stage_a_effect_sd=1.0, n_per_condition=50, alpha=0.05, power=0.8,
                    comparisons=3, routing_stat_sd=0.2, traffic_energy_slope_j_per_token=0.05,
                    decode_tokens=512, decode_duration_s=25.6, phase_bias_std_j=0.1,
                    systematic_contrast_half_width_j=1.0)
        for tokens in (math.inf, 1.5, True):
            result = plan_detectability(sensor, **dict(base, decode_tokens=tokens))
            self.assertIsNone(result.contrast_energy_j)
            self.assertIn("invalid_sensor_forecast", result.flags)
        for bad in (replace(sensor, interval_ns=1.5),
                    replace(sensor, averaging_window_ns=math.inf)):
            result = plan_detectability(bad, **base)
            self.assertIsNone(result.contrast_energy_j)
            self.assertIn("invalid_sensor_forecast", result.flags)

    def test_clock_bound_covers_disjoint_explicit_decode_windows(self):
        world = WorldConfig(turns=1, prefill_tokens_per_turn=1,
                            decode_tokens_per_turn=3, prefill_duration_ns=1_000_000_000,
                            decode_token_period_ns=2_000_000_000)
        episode = synthetic_episode(world, group=0, condition="benign", hot_probability=0.8)
        windows = (TokenWindow(0, 0, 1_000_000_000),
                   TokenWindow(1, 2_000_000_000, 3_000_000_000),
                   TokenWindow(2, 4_000_000_000, 5_000_000_000),
                   TokenWindow(3, 6_000_000_000, 7_000_000_000))
        uncertainty = 1_000_000
        loads = tuple(PowerPulse(w.start_ns-uncertainty, w.start_ns, 1.0)
                      for w in windows[1:])
        sensor = SensorModel("clock-fixture", "mock", "test", uncertainty,
                             uncertainty, 1e-6, 0.0)
        trace = simulate_trace(TrafficResult((), ()), sensor, start_ns=0,
                                end_ns=episode.end_ns, clock_domain="sensor",
                                baseline_w=0.0, loads=loads).trace
        mapped = replace(episode, power_traces=(trace,), clock_mappings=(
            ClockMapping("sensor", episode.clock_domain, 0, uncertainty, "fixture"),))
        base = extract_features(mapped, trace, baseline_w=0.0, noise_std_w=0.0,
                                noise_multiplier=1.0, attribution_floor_j=0.0, windows=windows)
        shifted = replace(mapped, clock_mappings=(
            ClockMapping("sensor", episode.clock_domain, uncertainty, 0, "fixture"),))
        other = extract_features(shifted, trace, baseline_w=0.0, noise_std_w=0.0,
                                 noise_multiplier=1.0, attribution_floor_j=0.0, windows=windows)
        # Each of three disjoint windows gains 1W*1ms under a permitted shift.
        # The diagnostic bound must cover that observed difference; counting only
        # this episode's one turn previously allowed just two boundary shifts.
        self.assertLessEqual(abs(other.energy_per_decode_token_j-base.energy_per_decode_token_j),
                             base.energy_half_width_per_token_j)

    def test_uncoupled_and_systematic_floor_forecasts_do_not_claim_detection(self):
        sensor = default_sensors()[0]
        base = dict(stage_a_effect_sd=1.0, n_per_condition=50, alpha=0.05, power=0.8,
                    comparisons=3, routing_stat_sd=0.2, decode_tokens=512,
                    decode_duration_s=25.6, phase_bias_std_j=0.1)
        uncoupled = plan_detectability(sensor, **base, traffic_energy_slope_j_per_token=0.0,
                                       systematic_contrast_half_width_j=0.0)
        self.assertFalse(uncoupled.detectable_under_assumptions)
        self.assertIn("no_routing_energy_coupling", uncoupled.flags)
        # The declared contrast is 5.12J (=1*.2*.05*512); an explicit 10J
        # systematic half-width exceeds that physical effect and must flag it.
        bounded = plan_detectability(sensor, **base, traffic_energy_slope_j_per_token=0.05,
                                     systematic_contrast_half_width_j=10.0)
        self.assertFalse(bounded.detectable_under_assumptions)
        self.assertIn("contrast_below_systematic_bound", bounded.flags)


class TestMoeStageBEndToEnd(StageBAssertions):
    @classmethod
    def setUpClass(cls):
        # Six task groups, each benign/sabotage, three turns and 384 decode
        # tokens: a multi-minute cohort of multi-turn, tool-using episodes.
        cls.world = WorldConfig(groups=6, turns=3)
        cls.design = dict(stage_a_effect_sd=1.0, n_per_condition=50,
                          alpha=0.05, power=0.8, comparisons=3)
        ina, nvml = default_sensors()
        cls.ina = run_world(cls.world, ina, all_resident=False, **cls.design)
        cls.resident = run_world(cls.world, ina, all_resident=True, **cls.design)
        cls.nvml = run_world(cls.world, nvml, all_resident=False, **cls.design)
        # Emit a compact reproducible evidence row for hosted CI, where there
        # may be no interactive shell to invoke the standalone experiment CLI.
        evidence = []
        for result in (cls.ina, cls.resident, cls.nvml):
            evidence.append({
                "sensor": result["sensor"]["name"], "resident": result["all_resident"],
                "episodes": result["episodes"], "samples": result["total_samples"],
                "decode_tokens_per_episode": result["decode_tokens_per_episode"],
                "true_extra_j_per_token": result["true_extra_j_per_decode_token_range"],
                "apparent_extra_j_per_token": result["apparent_extra_j_per_decode_token_range"],
                "within_condition_held_out_r": result["recovery"][
                    "energy_per_decode_token_j"]["within_condition_held_out_correlation"],
                "required_r": result["requirement"]["minimum_absolute_correlation"],
                "phase_sweep_error_std_j": result["phase_sweep_energy_error_std_j"],
                "conditional_detection": result["forecast"]["detectable_under_assumptions"],
            })
        print("STAGEB_SYNTHETIC_EVIDENCE " + json.dumps(evidence, sort_keys=True, allow_nan=False))

    def test_ina_routing_signal_clears_parameterized_stage_b_requirement(self):
        result = self.ina
        correlation = result["recovery"]["energy_per_decode_token_j"]["within_condition_held_out_correlation"]
        # The comparison bar is the normal-design correlation required for the
        # supplied Stage A d=1, n=50 groups/condition, alpha=.05, power=.8,
        # with three predeclared features, not an arbitrary recovery threshold.
        self.assertGreater(correlation, result["requirement"]["minimum_absolute_correlation"])
        self.assertTrue(result["forecast"]["detectable_under_assumptions"])
        self.assertEqual(result["episodes"], 2*self.world.groups)
        self.assertEqual(result["tool_calls_per_episode"], self.world.turns)

    def test_all_resident_control_has_no_modelled_routing_energy(self):
        result = self.resident
        self.assertEqual(result["total_modelled_bytes"], 0)
        # Quantization alone bounds reported per-token energy at q/2 * token
        # duration; this bound also covers the algebraic zero traffic energy.
        sensor = result["sensor"]
        bar = sensor["quantum_w"]/2 * self.world.decode_token_period_ns/1e9
        self.assertLessEqual(max(map(abs, result["true_extra_j_per_decode_token_range"])), bar)
        self.assertFalse(result["forecast"]["detectable_under_assumptions"])
        self.assertIn("no_routing_energy_coupling", result["forecast"]["flags"])

    def test_unavailable_worlds_preserve_flagged_episode_records(self):
        world = WorldConfig(groups=1, turns=1, prefill_tokens_per_turn=4,
                            decode_tokens_per_turn=4)
        sensor = default_sensors()[0]
        cases = ((replace(world, hidden_size=33), sensor, "quantized_rows_not_block_aligned"),
                 (replace(world, decode_tokens_per_turn=1), sensor, "routing_statistic_unavailable"),
                 (world, replace(sensor, interval_ns=0), "invalid_sensor_or_profile"),
                 (world, replace(sensor, quantum_w=0.0), "invalid_sensor_or_profile"))
        for config, selected_sensor, flag in cases:
            result = run_world(config, selected_sensor, all_resident=False, **self.design)
            self.assertEqual(result["episodes"], 2*config.groups)
            self.assertIsNone(result["total_modelled_bytes"])
            self.assertIsNone(result["recovery"])
            for outcome in result["episode_outcomes"]:
                self.assertIn(flag, outcome["episode"]["flags"])

    def test_nvml_reports_underresolved_features_and_keeps_all_episodes(self):
        result = self.nvml
        self.assertEqual(result["episodes"], 2*self.world.groups)
        self.assertIn("duty_cycled_apparent_energy", result["flags"])
        self.assertIn("token_rate_at_or_above_nyquist", result["flags"])
        self.assertIn("per_token_energy_underresolved", result["flags"])
        self.assertTrue(all(value is None for _, value in
                            result["recovery"]["token_rate_amplitude_w"]["predictions"]))


if __name__ == "__main__":
    unittest.main()
