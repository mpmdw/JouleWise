"""Production-shaped agent episodes through duty reconstruction and serialization."""

from __future__ import annotations

import bisect
import ctypes
import json
import math
import random
import threading
import unittest
import time

from joulewise.align.power.duty import (
    DUTY_CONFIDENCE, DutyEstimate, _student_quantile, estimate_energy, plan_offsets,
)
from joulewise.align.power.nvml import NvmlSampler
from tests.align.test_power_nvml import FakeNvmlLibrary
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
                 # Diagnostic bound only: above the 320 W deterministic peak;
                 # Gaussian shifts are unbounded. F5 excludes it from nominal width.
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


class ReplayWorld:
    """One agent turn with 1500 prefill tokens, 135 decoded tokens and a tool.

    Prefill lasts 187.5 ms at 350 W (~8k tokens/s). Decode lasts 3 s at
    220 W with 15 W, 7 Hz ripple represented by 1 ms constant steps (~45
    tokens/s). A 483.271 ms tool wait draws 75 W; idle is 55 W. Durations
    are deliberately not multiples of the sensor's 100 ms period.
    These are world parameters, not measurement thresholds.
    """
    def __init__(self) -> None:
        self.edges = [0, 187_500_137]
        self.watts = [350.0]
        for step in range(3000):
            self.edges.append(self.edges[-1]+1_000_000)
            self.watts.append(220+15*math.sin(2*math.pi*7*step/1000))
        self.edges.append(self.edges[-1]+483_271_299)
        self.watts.append(75.0)
        self.duration = self.edges[-1]
        self.prefix = [0.0]
        for left, right, level in zip(self.edges, self.edges[1:], self.watts):
            self.prefix.append(self.prefix[-1]+(right-left)*level)

    def integral(self, left: int, right: int, duration: int, shift: float) -> float:
        def primitive(t: int) -> float:
            if t <= 0:
                return 55.0*t
            inside = min(t, duration)
            base = min(inside, self.duration)
            index = min(bisect.bisect_right(self.edges, base)-1, len(self.watts)-1)
            total = self.prefix[index]+(base-self.edges[index])*self.watts[index]
            total += max(0, inside-self.duration)*self.watts[-1]+inside*shift
            return total+max(0, t-duration)*55.0
        return primitive(right)-primitive(left)


def replay_runs(seed: int, start_jitter_ns: int, duration_jitter_ns: int,
                repeats: int = 16) -> tuple[list[tuple[PowerTrace, int, int]], float]:
    world = ReplayWorld()
    rng = random.Random(seed)
    runs = []
    for offset in plan_offsets(PERIOD_NS, .25, repeats):
        jitter = rng.randint(0, start_jitter_ns) if start_jitter_ns else 0
        duration = world.duration+(rng.randint(-duration_jitter_ns, duration_jitter_ns)
                                   if duration_jitter_ns else 0)
        shift = rng.gauss(0, 2.0)  # Reviewer's 2 W independent Gaussian run shifts.
        start = EPOCH_NS+offset+jitter
        times = tuple(EPOCH_NS+k*PERIOD_NS for k in range(
            -1, (offset+jitter+duration)//PERIOD_NS+3))
        values = tuple(round((world.integral(t-start-TICK_NS, t-start, duration, shift)
                              /TICK_NS+rng.gauss(0, .3))/.001)*.001 for t in times)
        trace = PowerTrace("nvml_power", "gpu0:power_instant", "synthetic:monotonic",
                           times, values, "W", PERIOD_NS, TICK_NS, .25, .001,
                           json.dumps({"repeat_group": f"phase-{offset}",
                                       "timing_half_width_ns": [0]*len(times)}))
        runs.append((trace, start, start+duration))
    return runs, world.integral(0, world.duration, world.duration, 0)/1e9


class DutyWorldTests(unittest.TestCase):
    def test_waveform_through_ctypes_threads_estimator_and_episode(self) -> None:
        episode, powers, truth = agent_world()

        class Clock:
            def __init__(self, endpoint: int) -> None:
                self.now = episode.start_ns+endpoint
                self.lock = threading.Lock()
                # A synthetic Unix origin, aligned to the driver's microsecond
                # quantum. It is not a wall-clock timestamp in the Episode.
                self.wall_origin = 1_800_000_000_000_000_000

            def monotonic(self) -> int:
                with self.lock:
                    result = self.now
                    self.now += 100
                    return result

            def wall(self) -> int:
                with self.lock:
                    return self.wall_origin+self.now-episode.start_ns

            def advance(self, endpoint: int) -> None:
                with self.lock:
                    self.now = max(self.now, episode.start_ns+endpoint)

        class WaveformLibrary(FakeNvmlLibrary):
            def __init__(self, offset: int) -> None:
                super().__init__()
                first = offset if offset else PERIOD_NS
                self.ends = list(range(first, episode.end_ns-episode.start_ns+1, PERIOD_NS))
                self.position = -1
                self.current = self.ends[0]
                self.clock = Clock(self.current)
                self.finished = threading.Event()

            def nvmlDeviceGetPowerUsage(self, handle: object, output: object) -> int:
                self.position = min(self.position+1, len(self.ends)-1)
                self.current = self.ends[self.position]
                self.clock.advance(self.current)
                self.power_calls += 1
                self._put(output, ctypes.c_uint,
                          round(powers[self.current//TICK_NS-1]*1000))
                return 0

            def nvmlDeviceGetFieldValues(self, handle: object, count: int, values: object) -> int:
                for index in range(count):
                    value = values[index]
                    value.nvmlReturn = 0
                    value.valueType = 1
                    value.value.uiVal = round(powers[self.current//TICK_NS-1]*1000)
                    value.timestamp = (self.clock.wall_origin+self.current)//1000
                    value.latencyUsec = 0
                return 0

            def nvmlDeviceGetTotalEnergyConsumption(self, handle: object, output: object) -> int:
                # This fake cumulative channel is sampled through the same
                # production binding, although reconstruction uses power.
                joules = math.fsum(powers[:self.current//TICK_NS])*TICK_NS/1_000_000_000
                self._put(output, ctypes.c_ulonglong, round(joules*1000))
                if self.position == len(self.ends)-1:
                    self.finished.set()
                return 0

        runs = []
        for offset in plan_offsets(PERIOD_NS, 0.25, 8):
            library = WaveformLibrary(offset)
            sampler = NvmlSampler(
                library=library, interval_ns=1_000_000, clock_domain=episode.clock_domain,
                clock_ns=library.clock.monotonic, wall_clock_ns=library.clock.wall,
                power_bound_w=400.0, repeat_group=f"phase-{offset}")
            sampler.start()
            try:
                self.assertTrue(library.finished.wait(timeout=5))
            finally:
                traces = sampler.stop()
            trace = next(trace for trace in traces if trace.channel.endswith(":power_instant"))
            self.assertEqual(len(trace.values), len(library.ends))
            self.assertIn("window_end_ns", json.loads(trace.notes))
            runs.append((trace, episode.start_ns, episode.end_ns))
        result = estimate_energy(runs)
        self.assertTrue(math.isfinite(result.half_width_j))
        # The driver microsecond quantum and 100 ns mapping bracket determine
        # the real-path interval. Use its 1% agreement bar, above float noise.
        self.assertLessEqual(abs(result.joules-truth), 0.01*result.half_width_j)
        preserved = Episode(**{
            **episode.__dict__, "power_traces": tuple(trace for trace, _, _ in runs)})
        restored = from_json(Episode, to_json(preserved))
        replay = estimate_energy([
            (trace, restored.start_ns, restored.end_ns) for trace in restored.power_traces])
        self.assertEqual(replay, result)  # Identical code on byte-identical record inputs.
        print("NVML DRIVER END-TO-END", json.dumps({
            "truth_j": truth, "joules": result.joules, "half_width_j": result.half_width_j,
            "coverage": result.coverage_fraction, "repeats": len(runs),
            "samples_per_run": [len(trace.values) for trace, _, _ in runs]}))

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
        # Four binomial SE per F5/N1; at S=1000, 4 SE < alpha, so both
        # a never-missing interval (m=0) and an always-missing one fail.
        bar = 4*math.sqrt(alpha*(1-alpha)/seed_count)
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
        self.assertIn("worst_case_bias_unbounded", result.flags)
        self.assertIn("phase_without_replicates", result.flags)

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
            # F2: the shared timestamp is the window end. Query midpoints
            # seven milliseconds later belong only in notes. Conflicting
            # lane-local endpoint notes must not override the shared field.
            metadata["query_midpoint_ns"] = [t+7_000_000 for t in trace.t_ns]
            metadata["window_end_ns"] = [t+7_000_000 for t in trace.t_ns]
            trace = PowerTrace(**{**trace.__dict__, "notes": json.dumps(metadata)})
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
        invalid = PowerTrace(**{**trace.__dict__, "averaging_window_ns": None})
        outside = PowerTrace(**{
            **trace.__dict__, "t_ns": tuple(t-2*(end-start) for t in trace.t_ns),
            "notes": json.dumps({"flags": ["sensor_update_phase_unreported"]})})
        for prefix in ([(invalid, start, end+1)], [(outside, start, end+1)]):
            actual = estimate_energy(prefix+runs)
            # Same contributing samples and identical code must be bit
            # identical; rejected/nonoverlapping inputs have zero weight.
            self.assertEqual((actual.joules, actual.half_width_j, actual.coverage_fraction),
                             (expected.joules, expected.half_width_j, expected.coverage_fraction))

    def test_production_replays_duration_jitter_keep_all_runs(self) -> None:
        runs, _ = replay_runs(77, 2_000_000, 300_000)
        result = estimate_energy(runs)
        self.assertIn("runs_retained=16", result.flags)
        self.assertIn("durations_differ", result.flags)
        self.assertNotIn("duration_mismatch", result.flags)
        self.assertNotIn("phase_without_replicates", result.flags)
        self.assertTrue(math.isfinite(result.half_width_j), result)

    def test_production_jitter_calibration_at_nominal_95_percent(self) -> None:
        started = time.monotonic()
        seeds = 400  # F5: >304 ensures 4 binomial SE is smaller than alpha=.05.
        alpha = 1-DUTY_CONFIDENCE
        bar = 4*math.sqrt(alpha*(1-alpha)/seeds)
        # Both m=0 and m=S must fail; an interval that always covers cannot
        # pass as calibrated. This is derived from 4 SE < alpha < 1-alpha.
        self.assertLess(bar, min(alpha, 1-alpha))
        for name, start_jitter, duration_jitter in (
                ("aligned", 0, 0), ("100us", 100_000, 0),
                ("2ms", 2_000_000, 0), ("2ms_duration300us", 2_000_000, 300_000)):
            outside = 0
            for seed in range(seeds):
                runs, truth = replay_runs(seed, start_jitter, duration_jitter)
                result = estimate_energy(runs)
                self.assertIn("runs_retained=16", result.flags)
                self.assertTrue(math.isfinite(result.half_width_j), (name, seed, result))
                outside += abs(result.joules-truth) > result.half_width_j
            fraction = outside/seeds
            print("NVML PRODUCTION CALIBRATION", json.dumps({
                "case": name, "seeds": seeds, "repeats": 16, "misses": outside,
                "fraction": fraction, "nominal_alpha": alpha, "four_se_bar": bar,
                "elapsed_s": time.monotonic()-started}))
            self.assertLessEqual(abs(fraction-alpha), bar, (name, outside, seeds))

    def test_metadata_keeps_run_and_drops_only_invalid_samples(self) -> None:
        episode, powers, _ = agent_world()
        runs = sampled_runs(episode, powers, 12, seed=5, noise_sigma_w=1.0)
        trace, start, end = runs[0]
        # Add a noncontributing pre-roll observation; changing it cannot
        # change any coefficient on the workload, including its uncertainty.
        notes = json.loads(trace.notes)
        notes["timing_half_width_ns"].insert(0, 0)
        trace = PowerTrace(**{**trace.__dict__,
            "t_ns": (start-PERIOD_NS,)+trace.t_ns,
            "values": (55.0,)+trace.values, "notes": json.dumps(notes)})
        runs[0] = trace, start, end
        baseline = estimate_energy(runs)
        for change in ({"duty_fraction": None},
                       {"values": (-0.001,)+trace.values[1:]},
                       {"resolution": None}):
            result = estimate_energy([(PowerTrace(**{**trace.__dict__, **change}), start, end)]+runs[1:])
            self.assertEqual(result.joules, baseline.joules)  # Identical contributing inputs.
            self.assertIn("runs_retained=12", result.flags)
            if "resolution" in change:
                self.assertTrue(math.isinf(result.half_width_j))
                self.assertIn("sensor_resolution_unknown", result.flags)
            else:
                self.assertEqual(result.half_width_j, baseline.half_width_j)
        mixed = PowerTrace(**{**trace.__dict__, "channel": "gpu1:power_instant",
                              "clock_domain": "other:monotonic"})
        result = estimate_energy([(mixed, start, end)]+runs[1:])
        self.assertIn("mixed_channels", result.flags)
        self.assertIn("mixed_clock_domains", result.flags)

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
