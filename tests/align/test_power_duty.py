"""Production-shaped agent episodes through duty reconstruction and serialization."""

from __future__ import annotations

import json
import math
import random
import unittest

from joulewise.align.power.duty import (
    DUTY_CONFIDENCE, DutyEstimate, _student_quantile, estimate_energy, plan_offsets,
)
from joulewise.align.records import Episode, PowerTrace, ToolCall, Turn, from_json, to_json

TICK_NS = 25_000_000
PERIOD_NS = 100_000_000
EPOCH_NS = 10**15


def agent_world() -> tuple[Episode, tuple[float, ...], float]:
    """Six 1 s turns: 75 ms prefill, 775 ms decode, 150 ms tool wait.

    This models a small local model at roughly 40-60 decode tokens/s, with
    512-1024 prompt tokens per turn and growing context. Quarter-period power
    bins are exact integrals of a piecewise-constant synthetic board waveform.
    Prefill is 320 W, decode is 210 W with 20 W ripple, tool wait is 45 W.
    These are declared synthetic parameters, never hardware measurements.
    """
    turns = []
    powers = []
    context = 1024
    for index in range(6):
        start = EPOCH_NS + index*1_000_000_000
        first = start + 3*TICK_NS
        end = start + 1_000_000_000
        prefill = 512 + 256*(index % 3)
        decode = 32 + 8*(index % 3)
        tool = ToolCall("local_lookup", end-6*TICK_NS, end, 512, 2048)
        turns.append(Turn(index, start, end, context, prefill, decode, 8,
                          first_token_ns=first, tool_calls=(tool,)))
        context += prefill + decode
        for tick in range(40):
            if tick < 3:
                power = 320.0
            elif tick >= 34:
                power = 45.0
            else:
                power = 210 + 20*math.sin(2*math.pi*tick/4)
            powers.append(power)
    episode = Episode(
        "synthetic-nvml-agent", "synthetic/multiturn-tools", "benign",
        "local-small-open-weight", "mock-local", 0, "synthetic:monotonic",
        EPOCH_NS, EPOCH_NS+len(powers)*TICK_NS, tuple(turns),
        hardware={"whole_gpu": True, "sensor": "synthetic 25-of-100 ms"},
        flags=("synthetic_only",))
    truth = math.fsum(powers)*(TICK_NS/1_000_000_000)
    return episode, tuple(powers), truth


def sampled_runs(episode: Episode, powers: tuple[float, ...], repeats: int, *,
                 seed: int, noise_sigma_w: float = 0.0,
                 power_bound_w: float | None = 400.0) -> list[tuple[PowerTrace, int, int]]:
    rng = random.Random(seed)
    runs = []
    for offset in plan_offsets(PERIOD_NS, 0.25, repeats):
        # One independent Gaussian run shift models repeatability drift
        # shared by all samples of that run. Same-phase replicas estimate it.
        shift = rng.gauss(0, noise_sigma_w)
        timestamps = []
        readings = []
        end = offset
        while end <= episode.end_ns-episode.start_ns:
            if end >= TICK_NS:
                timestamps.append(episode.start_ns+end)
                # Aligned offsets and W=25 ms give exactly one waveform bin.
                readings.append(round((powers[end//TICK_NS-1]+shift)/0.001)*0.001)
            end += PERIOD_NS
        notes = {"timing_half_width_ns": [0]*len(readings)}
        if power_bound_w is not None:
            notes["power_bound_w"] = power_bound_w
        trace = PowerTrace(
            "nvml_power", "gpu0:power_instant", episode.clock_domain,
            tuple(timestamps), tuple(readings), "W", PERIOD_NS,
            TICK_NS, 0.25, 0.001, json.dumps(notes))
        runs.append((trace, episode.start_ns, episode.end_ns))
    return runs


class DutyWorldTests(unittest.TestCase):
    def test_phase_plan_tiles_then_replicates(self) -> None:
        self.assertEqual(plan_offsets(PERIOD_NS, 0.25, 8),
                         [0, 25_000_000, 50_000_000, 75_000_000]*2)
        self.assertEqual(plan_offsets(PERIOD_NS, 0.25, 2), [0, 50_000_000])
        self.assertEqual(plan_offsets(100, 1.0, 3), [0, 0, 0])
        for args in ((0, 0.25, 4), (100, 0.0, 4), (100, 0.25, 0)):
            self.assertEqual(plan_offsets(*args), [])

    def test_multiturn_episode_reconstructs_known_integral_and_round_trips(self) -> None:
        episode, powers, truth = agent_world()
        results = []
        for repeats in (1, 2, 4, 8, 16):
            runs = sampled_runs(episode, powers, repeats, seed=0)
            result = estimate_energy(runs)
            results.append(result)
            if repeats >= 8:
                # 1% of the quantization half-width (D*q/2 = 0.003 J).
                # This bar is far above 1e6 float ulps of a ~1 kJ integral.
                tolerance_j = 0.01 * result.half_width_j
                self.assertLessEqual(abs(result.joules-truth), tolerance_j)
                self.assertEqual(result.coverage_fraction, 1.0)
                self.assertTrue(math.isfinite(result.half_width_j))
        print("NVML DUTY WORLD", json.dumps({
            "truth_j": truth, "turns": 6, "tool_calls": 6, "prefill_tokens": 4608,
            "decode_tokens": 240, "duration_s": 6,
            "estimates": [{"repeats": n, "joules": result.joules,
                           "half_width_j": str(result.half_width_j),
                           "coverage": result.coverage_fraction}
                          for n, result in zip((1, 2, 4, 8, 16), results)]}))
        single_error = abs(results[0].joules-truth)
        repeated_error = abs(results[-1].joules-truth)
        # The comparison bar comes from the repeated estimate's own finite
        # uncertainty; omitting phase tiling must visibly fail this world.
        self.assertGreater(single_error, results[-1].half_width_j)
        self.assertLessEqual(repeated_error, results[-1].half_width_j)
        episode = Episode(**{
            **episode.__dict__, "power_traces": tuple(
                run[0] for run in sampled_runs(episode, powers, 8, seed=0))})
        restored = from_json(Episode, to_json(episode))
        self.assertEqual(restored, episode)  # Exact serialized record identity.
        self.assertEqual(episode.totals()["turns"], 6)
        self.assertEqual(episode.totals()["tool_calls"], 6)
        self.assertEqual(episode.totals()["decode_tokens"], 240)

    def test_seed_coverage_matches_declared_nominal_level(self) -> None:
        episode, powers, truth = agent_world()
        seed_count, repeats = 1000, 64
        outside = 0
        for seed in range(seed_count):
            result = estimate_energy(sampled_runs(
                episode, powers, repeats, seed=seed, noise_sigma_w=2.0))
            self.assertTrue(math.isfinite(result.half_width_j))
            outside += abs(result.joules-truth) > result.half_width_j
        alpha = 1-DUTY_CONFIDENCE
        fraction = outside/seed_count
        # The requested one-binomial-standard-error calibration bar. Seeds
        # 0..999 and 64 repeats are declared before inspecting any result.
        bar = math.sqrt(alpha*(1-alpha)/seed_count)
        print("NVML DUTY CALIBRATION", json.dumps({
            "seeds": seed_count, "repeats": repeats, "outside": outside,
            "outside_fraction": fraction, "nominal_alpha": alpha, "binomial_se": bar}))
        self.assertLessEqual(abs(fraction-alpha), bar,
                             (outside, seed_count, fraction, alpha, bar))

    def test_missing_coverage_needs_an_explicit_power_bound(self) -> None:
        episode, powers, _ = agent_world()
        result = estimate_energy(sampled_runs(
            episode, powers, 2, seed=0, power_bound_w=None))
        self.assertLess(result.coverage_fraction, 1.0)
        self.assertTrue(math.isinf(result.half_width_j))
        self.assertIn("partial_coverage", result.flags)
        self.assertIn("power_bound_required", result.flags)

    def test_a_fully_observed_tiling_does_not_need_a_power_bound(self) -> None:
        episode, powers, truth = agent_world()
        result = estimate_energy(sampled_runs(
            episode, powers, 8, seed=0, power_bound_w=None))
        # q/2 * 6 s is the whole-episode quantum bound; its 1% is the
        # independent-computation agreement bar used throughout this world.
        self.assertLessEqual(abs(result.joules-truth), 0.01*result.half_width_j)
        self.assertTrue(math.isfinite(result.half_width_j))

    def test_sensor_window_timing_and_call_timing_remain_distinct(self) -> None:
        episode, powers, truth = agent_world()
        runs = sampled_runs(episode, powers, 8, seed=0)
        shifted = []
        for trace, start, end in runs:
            metadata = json.loads(trace.notes)
            metadata["window_end_ns"] = list(trace.t_ns)
            metadata["window_timing_half_width_ns"] = [0]*len(trace.values)
            metadata["flags"] = ["driver_field_timestamp_is_wall_clock"]
            # Calls occur 7 ms after the driver sample; actual windows retain
            # their original endpoints through the lane-local notes adapter.
            trace = PowerTrace(**{
                **trace.__dict__, "t_ns": tuple(t+7_000_000 for t in trace.t_ns),
                "notes": json.dumps(metadata)})
            shifted.append((trace, start, end))
        result = estimate_energy(shifted)
        self.assertLessEqual(abs(result.joules-truth), 0.01*result.half_width_j)

    def test_unknown_sensor_age_and_output_average_are_flags(self) -> None:
        episode, powers, _ = agent_world()
        runs = sampled_runs(episode, powers, 8, seed=0)
        modified = []
        for trace, start, end in runs:
            notes = json.loads(trace.notes)
            notes["flags"] = ["sensor_update_phase_unreported"]
            modified.append((PowerTrace(**{**trace.__dict__, "notes": json.dumps(notes)}),
                             start, end))
        result = estimate_energy(modified)
        self.assertTrue(math.isinf(result.half_width_j))
        self.assertIn("sensor_window_time_unknown", result.flags)
        trace, start, end = runs[0]
        averaged = PowerTrace(**{
            **trace.__dict__, "notes": json.dumps({"flags": ["output_average_not_single_window"]})})
        result = estimate_energy([(averaged, start, end)])
        self.assertIn("output_average_not_single_window", result.flags)
        self.assertIn("no_covered_work", result.flags)

    def test_invalid_and_noncontributing_runs_do_not_change_valid_estimate(self) -> None:
        episode, powers, _ = agent_world()
        runs = sampled_runs(episode, powers, 8, seed=0)
        expected = estimate_energy(runs)
        trace, start, end = runs[0]
        invalid = PowerTrace(**{**trace.__dict__, "resolution": None})
        outside = PowerTrace(**{
            **trace.__dict__, "t_ns": tuple(t-2*(end-start) for t in trace.t_ns),
            "notes": json.dumps({"flags": ["sensor_update_phase_unreported"]})})
        for prefix in ([(invalid, start, end+1)], [(outside, start, end+1)]):
            actual = estimate_energy(prefix+runs)
            # Same contributing samples and identical code must be bit
            # identical; rejected/nonoverlapping inputs have zero weight.
            self.assertEqual((actual.joules, actual.half_width_j, actual.coverage_fraction),
                             (expected.joules, expected.half_width_j, expected.coverage_fraction))

    def test_student_quantile_has_independent_closed_form_checks(self) -> None:
        for probability in (0.95, 0.975, 0.995):
            # t_1 is Cauchy; t_2 CDF inversion follows from
            # F(x)=1/2 + x/(2*sqrt(2+x*x)).
            cauchy = math.tan(math.pi*(probability-0.5))
            v = 2*probability-1
            t2 = math.sqrt(2)*v/math.sqrt(1-v*v)
            for df, expected in ((1, cauchy), (2, t2)):
                self.assertTrue(math.isclose(
                    _student_quantile(probability, df), expected, rel_tol=1e-6))
                # No printed uncertainty for this pure numerical identity:
                # the brief specifies 1e-6 relative agreement.


if __name__ == "__main__":
    unittest.main()
