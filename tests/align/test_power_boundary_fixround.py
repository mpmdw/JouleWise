"""Boundary fix-round worlds; synthetic sensor windows, never hardware evidence."""
from __future__ import annotations
import bisect
import json
import math
import random
import statistics
import unittest
import warnings
from dataclasses import replace
from joulewise.align.records import PowerTrace
from joulewise.align.power import duty as lane

MS = 1_000_000
PERIOD = 100 * MS  # A100/H100 class: a 25 ms slice of every 100 ms (records.PowerTrace)
WINDOW = 25 * MS
QUANTUM = 0.001  # NVML reports integer milliwatts
EPOCH = 10**15  # a host-clock period boundary in the trace clock

COVERAGE_ABS = 1e-6  # orchestrator bar: value below 1, no printed uncertainty
REL = 1e-6  # orchestrator bar: no printed uncertainty
# Lead's Monte Carlo bar for a bounds-dominated interval at S seeds: the miss
# fraction may not exceed nominal 0.05 by more than 4 binomial standard errors.
NOMINAL_MISS = 0.05


def one_sided_ceiling(seeds: int) -> float:
    return NOMINAL_MISS + 4 * math.sqrt(NOMINAL_MISS * (1 - NOMINAL_MISS) / seeds)


class Wave:
    """Piecewise-constant board power of one run on aligned time u (ns); idle outside [0, D]."""

    def __init__(self, edges: list[int], watts: list[float], idle_w: float) -> None:
        self.edges, self.watts, self.idle = edges, watts, idle_w
        self.duration = edges[-1]
        self.prefix = [0.0]
        for a, b, w in zip(edges, edges[1:], watts):
            self.prefix.append(self.prefix[-1] + w * (b - a))

    def _inside(self, a: int, b: int) -> float:
        if b <= a:
            return 0.0
        i = bisect.bisect_right(self.edges, a) - 1
        j = bisect.bisect_right(self.edges, b) - 1
        if i == j:
            return self.watts[i] * (b - a)
        total = self.watts[i] * (self.edges[i + 1] - a) + (self.prefix[j] - self.prefix[i + 1])
        if j < len(self.watts):
            total += self.watts[j] * (b - self.edges[j])
        return total

    def integral_w_ns(self, a: int, b: int, shift_w: float = 0.0) -> float:
        total = 0.0
        if a < 0:
            total += self.idle * (min(b, 0) - a)
        if b > self.duration:
            total += self.idle * (b - max(a, self.duration))
        lo, hi = max(a, 0), min(b, self.duration)
        if hi > lo:
            total += self._inside(lo, hi) + shift_w * (hi - lo)
        return total

    def truth_j(self) -> float:
        return self._inside(0, self.duration) / 1e9


def make_script(rng: random.Random, turns: int, *, short_first: bool = False,
                short_decode: bool = False) -> dict:
    """A deterministic agent episode (what each replay repeats), small model on an A100-class board.

    Per turn: prefill of 300-3000 tokens at ~10k tokens/s (30-300 ms, 300-390 W)
    or, for half of the follow-up turns, a short 60-400 token tool result;
    a 1-4 ms launch transient 30-80 W above the prefill level; decode of
    20-300 tokens (3-40 if short_decode) at 15-35 ms per token on a 190-250 W
    plateau, each token 75% compute at +a and 25% sampling/sync at -3a
    (a = 5-30 W); a 80-1500 ms tool wait at 65-90 W between turns; idle
    50-60 W. short_first: the system prompt is in the prefix cache and only a
    60-200 token user message is prefilled (6-20 ms).
    """
    script = {"idle": rng.uniform(50, 60), "tool": rng.uniform(65, 90), "turns": []}
    for k in range(turns):
        tokens = rng.randint(60, 400) if (k > 0 and rng.random() < 0.5) else rng.randint(300, 3000)
        if short_first and k == 0:
            tokens = rng.randint(60, 200)
        prefill_w = rng.uniform(300, 390)
        script["turns"].append({
            "prefill_ns": int(tokens / 10000 * 1e9) + rng.randint(1, 999), "prefill_w": prefill_w,
            "spike": (rng.randint(1 * MS, 4 * MS), prefill_w + rng.uniform(30, 80)),
            "decode": rng.randint(3, 40) if short_decode else rng.randint(20, 300),
            "token_ns": rng.randint(15 * MS, 35 * MS) + rng.randint(1, 999),
            "base": rng.uniform(190, 250), "amp": rng.uniform(5, 30),
            "tool_ns": rng.randint(80 * MS, 1500 * MS) + rng.randint(1, 999) if k < turns - 1 else 0})
    return script


def realize(script: dict, rng: random.Random | None, tool_jitter_ns: int = 0) -> Wave:
    """One replay; tool-wait latency varies by up to +-tool_jitter_ns (duration variation)."""
    edges, watts = [0], []

    def seg(length: int, level: float) -> None:
        if length > 0:
            edges.append(edges[-1] + length)
            watts.append(level)

    for turn in script["turns"]:
        spike_ns, spike_w = turn["spike"]
        seg(spike_ns, spike_w)
        seg(max(turn["prefill_ns"] - spike_ns, 1), turn["prefill_w"])
        high = int(turn["token_ns"] * 0.75)
        for _ in range(turn["decode"]):
            seg(high, turn["base"] + turn["amp"])
            seg(turn["token_ns"] - high, turn["base"] - 3 * turn["amp"])
        if turn["tool_ns"]:
            jitter = rng.randint(-tool_jitter_ns, tool_jitter_ns) if (rng and tool_jitter_ns) else 0
            seg(turn["tool_ns"] + jitter, script["tool"])
    return Wave(edges, watts, script["idle"])


def sampled_run(wave: Wave, start: int, phi: int, rng: random.Random, *, shift_w: float = 0.0,
                noise_w: float = 0.3, label: str | None = None, window: int = WINDOW,
                period: int = PERIOD, roll_ns: int = 300 * MS, first_after_ns: int | None = None,
                timing_ns: int = 3000) -> tuple[PowerTrace, int, int]:
    """Sensor windows of ``window`` ns ending at EPOCH + phi + k*period, around one run.

    Each reading is the exact window mean of the run's power plus Gaussian
    noise, rounded to the NVML milliwatt. t_ns is the reported window end,
    within +-timing_ns of the true end; the notes carry it as the mapped
    driver endpoint with that half-width (the sampler's notes shape).
    """
    end = start + wave.duration
    k0 = (start - roll_ns - EPOCH - phi) // period
    k1 = (end + roll_ns - EPOCH - phi) // period + 1
    times, values = [], []
    for k in range(k0, k1 + 1):
        t = EPOCH + phi + k * period
        if t < start - roll_ns or t > end + roll_ns:
            continue
        if first_after_ns is not None and t - start < first_after_ns:
            continue
        mean = wave.integral_w_ns(t - window - start, t - start, shift_w) / window
        if noise_w:
            mean += rng.gauss(0.0, noise_w)
        reported = t + (rng.randint(-timing_ns, timing_ns) if timing_ns else 0)
        if times and reported <= times[-1]:
            reported = times[-1] + 1
        times.append(reported)
        values.append(max(round(mean / QUANTUM) * QUANTUM, 0.0))
    notes = {"flags": ["driver_field_timestamp_is_wall_clock"], "window_end_ns": times,
             "window_timing_half_width_ns": [timing_ns] * len(times)}
    if label is not None:
        notes["repeat_group"] = label
    trace = PowerTrace("nvml_power", "gpu0:power_instant", "host:monotonic", tuple(times),
                       tuple(values), "W", 10 * MS, window, window / period, QUANTUM,
                       json.dumps(notes))
    return trace, start, end


def session(script: dict, rng: random.Random, offsets: list[int], *, phi: int | None = None,
            shift_sd: float = 0.0, start_jitter_ns: int = 1 * MS, tool_jitter_ns: int = 0,
            labels: bool = True, **kw) -> list[tuple[PowerTrace, int, int]]:
    """Replays at the planned offsets from host-clock period boundaries; one sensor phase phi."""
    phi = rng.randrange(PERIOD) if phi is None else phi
    runs = []
    for index, offset in enumerate(offsets):
        wave = realize(script, rng, tool_jitter_ns)
        start = (EPOCH + (index + 10) * 37 * PERIOD + offset
                 + (rng.randint(0, start_jitter_ns) if start_jitter_ns else 0))
        runs.append(sampled_run(wave, start, phi, rng,
                                shift_w=rng.gauss(0.0, shift_sd) if shift_sd else 0.0,
                                label=f"phase-{offset}" if labels else None, **kw))
    return runs


def plan(repeats: int) -> list[int]:
    with warnings.catch_warnings():  # under-tiled plans warn; partial coverage is the point
        warnings.simplefilter("ignore", RuntimeWarning)
        return lane.plan_offsets(PERIOD, 0.25, repeats)


def corrected_mean_run_reference(runs):
    """Independent direct-grid implementation of the documented deconvolution.

    z=(w*y-o_start*b_start-o_end*b_end)/i, then integral A(u)*mean(z)
    on covered u, multiplied by mean duration/covered active duration.
    This enumerates every atom rather than calling the lane's sweep/helpers.
    """
    durations = [end-start for _, start, end in runs]
    pieces = []
    for trace, start, end in runs:
        w, duration = trace.averaging_window_ns, end-start
        raw = [(t-start-w, t-start, y) for t, y in zip(trace.t_ns, trace.values)]
        before = [item for item in raw if item[1] <= 0]
        after = [item for item in raw if item[0] >= duration]
        for a, b, y in raw:
            left, right = max(0, a), min(duration, b)
            if right <= left:
                continue
            baselines = (max(before, key=lambda x: x[1])[2] if before else y,
                         min(after, key=lambda x: x[0])[2] if after else y)
            z = (w*y-max(0, -a)*baselines[0]-max(0, b-duration)*baselines[1])/(right-left)
            pieces.append((left, right, z))
    cuts = sorted({0, *durations, *(a for a, _, _ in pieces), *(b for _, b, _ in pieces)})
    integrals, covered = [], []
    for a, b in zip(cuts, cuts[1:]):
        active = [z for left, right, z in pieces if left <= a and b <= right]
        if active:
            mass = (b-a)*sum(d > a for d in durations)/len(durations)
            covered.append(mass)
            integrals.append(mass*statistics.fmean(active))
    return math.fsum(integrals)/1e9*statistics.fmean(durations)/math.fsum(covered)


class BoundaryFixRoundTests(unittest.TestCase):
    def test_lane_half_width_contains_truth_when_a_short_prefill_starts_the_workload(self) -> None:
        # Review-3 finding, exact world (no noise, no jitter, no shift): idle
        # 55 W; 10 ms prefill at 350 W, then 200 W decode to D = 1.2345 s;
        # sensor windows end 12.5 ms after each host period boundary; 16
        # replays. Every start-straddling window has inside length 12.5 ms:
        # y = (12.5*55 + 10*350 + 2.5*200)/25 = 187.5 W, so the start edge is
        # off by 12.5*187.5 - 4000 = -1656.25 W*ms. The lane's start term is
        # 12.5 * (1 - 0.5) * R_b with R_b = 200 - 55 = 145 W from the nearest
        # 25 ms averages: 906.25 W*ms. The 25 ms averages never see 350 W.
        # Lane: 246.361 +- 1.290 J; truth 248.400 J.
        duration = 1_234_500_000
        wave = Wave([0, 10 * MS, duration], [350.0, 200.0], 55.0)
        runs = [sampled_run(wave, EPOCH + 50 * PERIOD + o, 12_500_000, random.Random(0),
                            noise_w=0.0, timing_ns=0, label=f"phase-{o}") for o in plan(16)]
        a = lane.estimate_energy(runs)
        self.assertLessEqual(abs(a.joules - wave.truth_j()), a.half_width_j, (a, wave.truth_j()))

    def test_lane_half_width_calibrates_on_one_turn_short_prefill_replays(self) -> None:
        # Review-3 finding, production-shaped: one model call whose system
        # prompt is prefix-cached (6-20 ms prefill), 20-300 decode tokens,
        # 0.3 W noise, 0-1 ms dispatch jitter, random sensor phase, the
        # runbook's 16 replays. The reviewer's 400-seed run gives 206 misses;
        # the one-sided ceiling at S = 40 is 0.188 (7 misses).
        seeds, misses = 40, 0
        for seed in range(seeds):
            rng = random.Random(6000 + seed)
            script = make_script(rng, 1, short_first=True)
            a = lane.estimate_energy(session(script, rng, plan(16)))
            misses += abs(a.joules - realize(script, None).truth_j()) > a.half_width_j
        print("TWIN nvml r3 one-turn short-prefill replays: lane misses", misses, "of", seeds)
        self.assertLessEqual(misses / seeds, one_sided_ceiling(seeds), misses)

    def test_full_window_start_burst(self):
        duration = 1_987_500_000
        wave = Wave([0, WINDOW, duration], [360.0, 210.0], 55.0)
        runs = [sampled_run(wave, EPOCH+50*PERIOD+o, 12_500_000, random.Random(0),
                            noise_w=0.0, timing_ns=0, label=f"phase-{o}") for o in plan(16)]
        estimate = lane.estimate_energy(runs)
        self.assertLessEqual(abs(estimate.joules-wave.truth_j()), estimate.half_width_j)
        # Agreement bar: 1% of the estimate's printed half-width.
        self.assertLessEqual(abs(estimate.joules-corrected_mean_run_reference(runs)),
                             0.01*estimate.half_width_j)

    def test_corrected_center_independent_reference_with_jitter_and_duration_changes(self):
        for seed in range(12):
            rng = random.Random(8100+seed)
            runs = session(make_script(rng, 2, short_first=True), rng, plan(16), tool_jitter_ns=20*MS)
            estimate = lane.estimate_energy(runs)
            # Agreement bar: 1% of the printed half-width, including correction noise.
            self.assertLessEqual(abs(estimate.joules-corrected_mean_run_reference(runs)),
                                 0.01*estimate.half_width_j)

    def test_both_edges_and_missing_baseline_fallback(self):
        # One 25 ms window: 5 ms before at 50 W, 10 ms run at 300 W,
        # 10 ms after at 80 W. Two fully outside readings anchor both edges.
        width, duration = 25*MS, 10*MS
        trace = PowerTrace("mock", "gpu0", "host", (-25*MS, 20*MS, 50*MS),
                           (50.0, (5*50+10*300+10*80)/25, 80.0), "W", 25*MS,
                           width, 1.0, 0.001,
                           json.dumps({"timing_half_width_ns": [0, 0, 0]}))
        estimate = lane.estimate_energy([(trace, 0, duration)]*2)
        # 300 W * .010 s = 3 J; numerical agreement uses 1% of width.
        self.assertLessEqual(abs(estimate.joules-3.0), 0.01*estimate.half_width_j)
        self.assertIn("outside_baseline_stationarity_assumed", estimate.flags)
        stripped = replace(trace, t_ns=(20*MS,), values=(trace.values[1],),
                           notes=json.dumps({"timing_half_width_ns": [0]}))
        missing = lane.estimate_energy([(stripped, 0, duration)]*2)
        self.assertTrue(math.isinf(missing.half_width_j))
        self.assertIn("boundary_baseline_missing", missing.flags)
        bounded = replace(stripped, notes=json.dumps({"power_bound_w": 400.0, "timing_half_width_ns": [0]}))
        fallback = lane.estimate_energy([(bounded, 0, duration)]*2)
        term = float(next(f.split("=",1)[1] for f in fallback.flags if f.startswith("boundary_bound_j=")))
        # d/i=1 for one fully covered run; outside=.015 s, B=400 W => 6 J.
        self.assertAlmostEqual(term, .015*400, delta=1e-6*.015*400)
        self.assertLessEqual(abs(fallback.joules-3.0), fallback.half_width_j)
        # Only the post edge is missing; its .010 s * B term remains finite.
        one_side = replace(trace, t_ns=trace.t_ns[:2], values=trace.values[:2],
                           notes=json.dumps({"power_bound_w":400.0, "timing_half_width_ns":[0,0]}))
        partial = lane.estimate_energy([(one_side,0,duration)]*2)
        self.assertLessEqual(abs(partial.joules-3.0), partial.half_width_j)
        partial_term = float(next(f.split("=",1)[1] for f in partial.flags if f.startswith("boundary_bound_j=")))
        self.assertAlmostEqual(partial_term, .010*400, delta=1e-6*.010*400)

    def test_zero_power_bound_is_a_physical_fallback(self):
        # [0,B] is the singleton {0} when B=0: missing outside baseline
        # cannot introduce boundary energy. Keep finite rounding sensitivity.
        trace = PowerTrace("mock","gpu0","host",(20*MS,),(0.,),"W",25*MS,
                           25*MS,1.,.001,json.dumps({"power_bound_w":0.,"timing_half_width_ns":[0]}))
        estimate=lane.estimate_energy([(trace,0,10*MS)]*2)
        self.assertTrue(math.isfinite(estimate.half_width_j))
        term=float(next(f.split("=",1)[1] for f in estimate.flags if f.startswith("boundary_bound_j=")))
        self.assertAlmostEqual(term,0.,delta=1e-6)  # Below 1 J: 1e-6 J absolute.
        self.assertIn("boundary_power_bound_fallback",estimate.flags)

    def test_outside_range_and_nearest_baseline(self):
        # Closest before baseline is 60 W, closest after 80 W. Each edge's
        # outside range is 20 W; distant levels must not set the center.
        trace = PowerTrace("mock", "gpu0", "host", (-50*MS,-25*MS,20*MS,50*MS,75*MS),
                           (40.0,60.0,(5*60+10*300+10*80)/25,80.0,100.0),
                           "W",25*MS,25*MS,1.0,0.001)
        estimate = lane.estimate_energy([(trace,0,10*MS)]*2)
        term = float(next(f.split("=",1)[1] for f in estimate.flags if f.startswith("boundary_bound_j=")))
        # d/i=1, total outside .015 s, edge range 20 W => .3 J.
        self.assertAlmostEqual(term,.015*20,delta=1e-6)  # Below 1: 1e-6 J absolute.
        self.assertLessEqual(abs(estimate.joules-3),.01*estimate.half_width_j)

    def test_baseline_noise_enters_run_repeatability(self):
        # Both replicas have identical y; only the nearest baseline changes.
        # w=25 ms, i=o=12.5 ms, so z=2*y-b and SD(z)=SD(b).
        base = PowerTrace("mock","gpu0","host",(-25*MS,12_500_000),
                          (50.0,175.0),"W",100*MS,25*MS,.25,.001)
        runs = [(replace(base,values=(b,175.0)),0,12_500_000) for b in (49.,51.,48.,52.)]
        estimate = lane.estimate_energy(runs)
        spread = float(next(f.split("=",1)[1] for f in estimate.flags if f.startswith("repeatability_half_width_j=")))
        # Student 97.5% quantile at 3 df, rounded to 6 decimals; all run
        # weight .0125 s, SD(b)/sqrt(4). No uncertainty on width: 1e-6 rel.
        expected = 3.182446*.0125*statistics.stdev([49.,51.,48.,52.])/math.sqrt(4)
        self.assertAlmostEqual(spread,expected,delta=1e-6*expected)

    def test_noisy_one_turn_short_prefill_monte_carlo(self):
        # Independent Gaussian run shifts and .3 W read noise, plus dispatch
        # and timestamp jitter, through the production estimator, 16 replays.
        seeds, misses = 80, 0
        for seed in range(seeds):
            rng = random.Random(9200+seed)
            script = make_script(rng,1,short_first=True)
            runs = session(script,rng,plan(16),shift_sd=.5)
            estimate = lane.estimate_energy(runs)
            misses += abs(estimate.joules-realize(script,None).truth_j()) > estimate.half_width_j
        print("POWER noisy short-prefill Monte Carlo:",misses,"/",seeds)
        # Nominal 5% misses plus four binomial standard errors at S seeds.
        self.assertLessEqual(misses/seeds,one_sided_ceiling(seeds))
