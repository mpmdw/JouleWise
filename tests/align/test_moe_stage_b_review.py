"""Review-round probes through production worlds; no hardware or network access.

This port is the brief's no-shell CI fallback. Worlds and sensor inputs match
p1--p5. Evidence is printed before assertions so failures retain their numbers.
"""

from __future__ import annotations

import json
import math
import os
import statistics
import time
import unittest
from dataclasses import asdict, replace
from unittest.mock import patch

import joulewise.align.moe_stage_b.experiment as ex
from joulewise.align.moe_stage_b import apply_decode_stalls, extract_features, simulate_episode, model_traffic
from joulewise.align.records import RouterLog

DESIGN = dict(stage_a_effect_sd=1.0, n_per_condition=50, alpha=.05, power=.8, comparisons=3)


def feature_summary(value):
    if value is None:
        return None
    return {key: value.get(key) for key in (
        "within_condition_held_out_correlation", "within_condition_held_out_interval_95",
        "held_out_episodes", "held_out_effective_n", "flags", "verdict")}


def compact(result):
    energy = result["recovery"]["energy_per_decode_token_j"] if result["recovery"] else {}
    forecast = result.get("forecast") or {}
    return dict(
        within_r=energy.get("within_condition_held_out_correlation"),
        ci=energy.get("within_condition_held_out_interval_95"),
        verdict=result.get("stage_b_verdict"), forecast_r=forecast.get("model_correlation"),
        contrast=forecast.get("contrast_energy_j"), bound=forecast.get("contrast_half_width_j"),
        worst_case_bound_j=forecast.get("worst_case_same_sign_quantization_bound_j"),
        apparent=result.get("apparent_extra_j_per_decode_token_range"),
        true=result.get("true_extra_j_per_decode_token_range"),
        timing=feature_summary(result.get("recovery", {}).get("decode_seconds_per_token")) if result["recovery"] else None,
        increment=feature_summary(result.get("power_increment_over_timing")),
        mean_power=feature_summary(result.get("recovery", {}).get("mean_decode_power_w")) if result["recovery"] else None,
        episodes=result["episodes"], status=result.get("status", "ok"),
        required_r=result.get("requirement", {}).get("minimum_absolute_correlation"),
        recovery_meets=result.get("empirical_recovery_meets_requirement", {}).get("energy_per_decode_token_j"),
        phase_err_sd_J=result.get("phase_sweep_energy_error_std_j"),
    )


def emit(tag, result):
    print("STAGEB_REVIEW " + tag + " " + json.dumps(result, sort_keys=True, allow_nan=False), flush=True)


class TestMoeStageBReview(unittest.TestCase):
    def setUp(self):
        guard = patch.dict(os.environ, {"JW_B5_SYNTHETIC_ONLY": "1"})
        guard.start()
        self.addCleanup(guard.stop)

    def test_reviewer_worlds_and_pass_conditions(self):
        started = time.perf_counter()
        ina, nvml = ex.default_sensors()
        real_sim = ex.simulate_episode
        real_extract = ex.extract_features
        e2e = ex.WorldConfig(groups=48, turns=3, decode_miss_stalls=True)
        results = {}
        for mode in ("e2e", "e2e_blind", "default", "default_blind"):
            world = ex.WorldConfig() if mode.startswith("default") else e2e
            def blind(episode, config, sensor, **kw):
                out = real_sim(episode, config, sensor, **kw)
                tr = out.episode.power_traces[-1]
                tr = replace(tr, values=tuple(kw["baseline_w"]+kw["decode_load_w"] for _ in tr.values))
                return replace(out, episode=replace(out.episode,
                    power_traces=out.episode.power_traces[:-1]+(tr,)))
            with patch.object(ex, "simulate_episode", blind if mode.endswith("blind") else real_sim):
                for sensor in (ina, nvml):
                    result = ex.run_world(world, sensor, all_resident=False, **DESIGN)
                    results[(mode, sensor.name)] = result
                    emit(mode+" "+sensor.name, compact(result))
        # p2: identical E2E no-stall world, sensor q is the only changed input.
        world = replace(e2e, decode_miss_stalls=False)
        captures, quant = {}, {}
        def capture(episode, trace, **kw):
            feature = real_extract(episode, trace, **kw)
            captures[episode.episode_id] = feature.energy_per_decode_token_j*feature.decode_tokens
            return feature
        with patch.object(ex, "extract_features", capture):
            for tag, sensor in (("q", ina), ("fine", replace(ina, quantum_w=1e-9))):
                result = ex.run_world(world, sensor, all_resident=False, **DESIGN)
                quant[tag] = (result, dict(captures))
                captures.clear()
                emit("p2 "+tag, compact(result))
        differences = {key: value-quant["fine"][1][key] for key, value in quant["q"][1].items()}
        means = [statistics.fmean(value for key, value in differences.items() if key.endswith("-"+condition))
                 for condition in ("benign", "sabotage")]
        emit("p2 rounding", dict(max_abs_j=max(map(abs, differences.values())),
             sd_j=statistics.pstdev(differences.values()), condition_difference_j=means[1]-means[0]))
        # p3: keep the original labelled 6.6ms alternative after shunt-slice becomes default.
        slice_sensor = replace(ina, averaging_window_ns=1_100_000)
        frame_sensor = replace(ina, averaging_window_ns=6_600_000)
        for tag, sensor in (("contiguous_6.6ms", frame_sensor), ("shunt_slice_1.1ms", slice_sensor)):
            if sensor.averaging_window_ns == ina.averaging_window_ns:
                result = quant["q"][0]
            else:
                result = ex.run_world(world, sensor, all_resident=False, **DESIGN)
            emit("p3 "+tag, compact(result))
        # p4: one dropped reading in a real-sized two-turn stalled episode.
        world = ex.WorldConfig(groups=1, turns=2)
        episode = ex.synthetic_episode(world, group=0, condition="sabotage", hot_probability=.3)
        episode, nominal = ex.synthetic_token_schedule(world, episode)
        offload = ex.world_offload(world)
        timing = apply_decode_stalls(episode, offload, windows=nominal)
        dropped_features = []
        for sensor in (ina, nvml):
            out = simulate_episode(timing.episode, offload, replace(sensor, phase_ns=1234567),
                baseline_w=world.baseline_w, prefill_load_w=world.prefill_load_w,
                decode_load_w=world.decode_load_w, tool_load_w=world.tool_load_w,
                seed=1, windows=timing.windows)
            trace = out.episode.power_traces[-1]
            kw = dict(baseline_w=world.baseline_w+world.decode_load_w, noise_std_w=sensor.noise_std_w,
                      noise_multiplier=1.0, attribution_floor_j=0.0, windows=timing.windows)
            full = extract_features(out.episode, trace,
                reference_decode_duration_ns=timing.reference_decode_duration_ns, **kw)
            first = next(w for w, phase in zip(timing.windows, episode.router_log.phase) if phase == "decode")
            k = next(i for i, t in enumerate(trace.t_ns) if t > first.start_ns+3*trace.nominal_interval_ns)
            one = replace(trace, t_ns=trace.t_ns[:k]+trace.t_ns[k+1:],
                          values=trace.values[:k]+trace.values[k+1:])
            dropped = extract_features(out.episode, one,
                reference_decode_duration_ns=timing.reference_decode_duration_ns, **kw)
            no_reference = extract_features(out.episode, one, **kw)
            dropped_features.append(dropped)
            emit("p4 "+sensor.name, dict(samples=len(trace.t_ns), full=asdict(full),
                 dropped=asdict(dropped), without_reference=asdict(no_reference),
                 change_j_per_token=(dropped.energy_per_decode_token_j-full.energy_per_decode_token_j
                      if dropped.energy_per_decode_token_j is not None else None)))
            invalid = extract_features(out.episode, trace, reference_decode_duration_ns=10**15, **kw)
            emit("p4 reference", dict(flags=invalid.flags))
        duplicate = RouterLog("dup", 64, 2, (0,), ("decode",), (((3, 3),),))
        dup_flags = model_traffic(duplicate, replace(offload, expert_bytes={0: 10}, cache_capacity_bytes=100)).flags
        bad_flags = model_traffic(duplicate, replace(offload, expert_bytes={0: 10},
                                 resident=frozenset({(5, 1)}))).flags
        emit("p4 flags", dict(duplicate=dup_flags, bad_resident=bad_flags))
        self.assertIn("duplicate_expert_ids", dup_flags)
        self.assertIn("invalid_resident_expert", bad_flags)
        # p5: drop one reading in one of the 24 episodes, preserving all routing.
        drop_results = []
        for world in (ex.WorldConfig(), ex.WorldConfig(decode_miss_stalls=False)):
            state = {"done": False}
            def drop_one(episode, config, sensor, **kw):
                out = real_sim(episode, config, sensor, **kw)
                if not state["done"] and out.episode.power_traces:
                    trace = out.episode.power_traces[-1]
                    decode = [w for w, phase in zip(kw["windows"], episode.router_log.phase) if phase == "decode"]
                    k = next(i for i, t in enumerate(trace.t_ns) if t > decode[10].start_ns+3*trace.nominal_interval_ns)
                    one = replace(trace, t_ns=trace.t_ns[:k]+trace.t_ns[k+1:],
                                  values=trace.values[:k]+trace.values[k+1:])
                    out = replace(out, episode=replace(out.episode, power_traces=out.episode.power_traces[:-1]+(one,)))
                    state["done"] = True
                return out
            with patch.object(ex, "simulate_episode", drop_one):
                result = ex.run_world(world, ina, all_resident=False, **DESIGN)
            drop_results.append(result)
            emit("p5 "+("stalls" if world.decode_miss_stalls else "no-stalls"), compact(result))
            if "episode_outcomes" in result:
                emit("p5 dropped_episode", result["episode_outcomes"][0])
        # F10 ablation: restore only the legacy noise seed, preserving all
        # routing/timing/sensor inputs. This is evidence, never the registered run.
        import random as standard_random
        from types import SimpleNamespace
        from joulewise.align.moe_stage_b import simulation
        old_rng = SimpleNamespace(Random=lambda seed: standard_random.Random(
            int(seed[6:]) if isinstance(seed, str) and seed.startswith("noise-") else seed))
        with patch.object(simulation, "random", old_rng):
            for sensor in (ina, nvml):
                result = ex.run_world(ex.WorldConfig(), sensor, all_resident=False, **DESIGN)
                emit("p10 legacy_noise_seed "+sensor.name, compact(result))
        emit("elapsed", dict(seconds=time.perf_counter()-started))
        for (mode, _), result in results.items():
            self.assertIn("decode_seconds_per_token", result["recovery"])
            self.assertIn("mean_decode_power_w", result["recovery"])
            self.assertIn("power_increment_over_timing", result)
            if mode.endswith("blind"):
                self.assertNotEqual(result["stage_b_verdict"], "yes")
                self.assertIn("constant_training_power_feature",
                              result["recovery"]["mean_decode_power_w"]["flags"])
        self.assertEqual(quant["q"][0]["stage_b_verdict"], quant["fine"][0]["stage_b_verdict"])
        for feature in dropped_features:
            self.assertTrue(math.isfinite(feature.energy_per_decode_token_j))
            self.assertIn("incomplete_decode_coverage", feature.flags)
        for result in drop_results:
            self.assertEqual(result.get("status", "ok"), "ok")
            self.assertEqual(result["episodes"], 24)  # Two conditions x the specified 12 groups.
            self.assertIsInstance(result["recovery"]["energy_per_decode_token_j"][
                "within_condition_held_out_correlation"], float)
            self.assertIn(result["stage_b_verdict"], ("yes", "no", "inconclusive at this cohort size"))
            self.assertIn("incomplete_decode_coverage", result["episode_outcomes"][0]["features"]["flags"])

    def test_prefill_32_updates_cache_and_33_preserves_it(self):
        world = ex.WorldConfig(groups=1, turns=1)
        base = replace(ex.world_offload(world), expert_bytes={0: 10}, cache_capacity_bytes=320,
                       prefill_mode="bypass", prefill_batch_tokens=128)
        for count in (32, 33):
            for probe in (0, 1):
                # Prime 32 slots (including oldest expert 1); prefill expert 0
                # evicts 1 only for the short batch. Independent final readouts
                # detect both warmth and preservation without an intervening fill.
                log = RouterLog("prefill-boundary", 64, 1, (0,),
                    ("decode",)*32+("prefill",)*count+("decode",),
                    tuple(((expert,),) for expert in range(1, 33))+(((0,),),)*count+(((probe,),),))
                result = model_traffic(log, base)
                self.assertEqual(result.tokens[-1].bytes_moved,
                                 (0 if probe == 0 else 10) if count == 32
                                 else (10 if probe == 0 else 0))
                # 32 is max_batch at pinned a37cc461 :230, used by :503;
                # 33 is the next integer. Expert bytes are exact fixture counts.
                expected = "prefill_small_batch_cache_updated" if count == 32 else "prefill_cache_bypassed"
                self.assertIn(expected, result.flags)

    def test_increment_matches_pairwise_oracle_on_real_world_features(self):
        from joulewise.align.moe_stage_b.analysis import RoutingObservation, recover_power_increment
        from joulewise.align.moe_stage_b.reference import reference_power_increment
        observations = []
        real_extract = ex.extract_features
        def capture(episode, trace, **kw):
            features = real_extract(episode, trace, **kw)
            observations.append(RoutingObservation(episode.episode_id, episode.task_pair,
                                ex.decode_reuse(episode.router_log), features))
            return features
        with patch.object(ex, "extract_features", capture):
            ex.run_world(ex.WorldConfig(groups=4, turns=2), ex.default_sensors()[0],
                         all_resident=False, **DESIGN)
        actual = recover_power_increment(observations)
        expected, count = reference_power_increment(observations)
        self.assertEqual(actual.held_out_episodes, count)
        # Algebra has no printed uncertainty: brief rule 3 gives 1e-6 relative.
        self.assertLessEqual(abs(actual.held_out_correlation-expected),
                             1e-6*abs(expected))
        blind = [replace(item, features=replace(item.features, energy_per_decode_token_j=0,
                                                mean_decode_power_w=12)) for item in observations]
        constant = recover_power_increment(blind)
        self.assertIsNone(constant.held_out_correlation)
        self.assertIn("constant_power_increment_feature", constant.flags)

    def test_averaged_ina_uses_disjoint_shunt_slices(self):
        from joulewise.align.moe_stage_b.simulation import ina3221_sensor, PowerPulse, simulate_trace
        from joulewise.align.moe_stage_b.traffic import TrafficResult
        sensor = ina3221_sensor(bus_voltage_v=5, current_a=2, shunt_ohm=.01,
            enabled_channels=3, shunt_conversion_ns=1_100_000, bus_conversion_ns=1_100_000,
            averages=4, poll_interval_ns=10_000_000, noise_std_w=0)
        # Four 1.1ms shunt slices separated by the 6.6ms six-conversion cycle.
        self.assertEqual(sensor.acquisition_slices_ns,
                         ((0, 1_100_000), (6_600_000, 7_700_000),
                          (13_200_000, 14_300_000), (19_800_000, 20_900_000)))
        stamp = 26_400_000
        # A 4W load present only during the latest slice gives a 1W mean.
        trace = simulate_trace(TrafficResult((), ()), replace(sensor, phase_ns=0),
            start_ns=0, end_ns=2*stamp, clock_domain="fixture", baseline_w=0,
            loads=(PowerPulse(stamp-1_100_000, stamp, 4),)).trace
        index = trace.t_ns.index(stamp)
        # q/400 is below 1% of the displayed q/2 half-width and far above
        # 1e6 binary64 ulps at this one-watt scale.
        expected = round(1/sensor.quantum_w)*sensor.quantum_w
        self.assertLessEqual(abs(trace.values[index]-expected), sensor.quantum_w/400)


if __name__ == "__main__":
    unittest.main()
