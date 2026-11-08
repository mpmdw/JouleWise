#!/usr/bin/env python3
"""Synthetic desk power planning. No file inputs, collectors or model downloads.

Run from the repo: python3 scripts/interp_energy/power_analysis.py --paired-only
Omit --paired-only for a NumPy Monte Carlo comparison at equal acquisition time.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import math
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from joulewise.interp_energy.power import plan_power, study_reference


def compare_synthetic(args) -> dict:
    from joulewise.interp_energy.lockin import (
        NoiseModel, Schedule, _numpy, demodulate, estimate_abba, make_schedule, simulate_trace,
    )

    np = _numpy()
    if args.trials < 30:
        raise ValueError("at least 30 Monte Carlo trials are required")
    if args.baseline_w <= 0 or not math.isfinite(args.baseline_w):
        raise ValueError("baseline_w must be finite and positive")
    noise = NoiseModel(args.white_sd_w, args.pink_sd_w, args.thermal_amplitude_w,
                       args.thermal_tau_seconds, tuple(args.step), args.burst_rate_hz,
                       args.burst_mean_seconds, args.burst_amplitude_w)
    rows = {}
    for name, chip, kind in (("slow_abba", args.slow_chip_seconds, "randomized_abba"),
                             ("lockin", args.chip_seconds, args.schedule)):
        if not math.isfinite(chip) or chip <= 0:
            raise ValueError("chip durations must be finite and positive")
        n_blocks = args.simulation_seconds / (4 * chip)
        if not math.isfinite(n_blocks) or n_blocks < 8 or not math.isclose(n_blocks, round(n_blocks)):
            raise ValueError("simulation_seconds must contain >=8 whole four-chip blocks for both designs")
        estimates, covered, rejected = [], 0, 0
        # Each trial is a new independent synthetic session. Randomize schedule
        # independently of noise, including global square-wave polarity. Slow
        # and fast designs see the SAME per-trial noise realization.
        for trial in range(args.trials):
            schedule_seed = args.seed + 2 * trial
            schedule = make_schedule(round(n_blocks), chip, kind=kind, seed=schedule_seed)
            if kind == "square":
                polarity = int(np.random.default_rng(schedule_seed).choice([-1, 1]))
                schedule = Schedule(tuple(polarity * x for x in schedule.chips), chip, kind)
            trace = simulate_trace(schedule, sample_rate_hz=args.sample_rate_hz,
                                   baseline_w=args.baseline_w, effect_fraction=args.effect_fraction,
                                   noise=noise, seed=args.seed + 2 * trial + 1)
            result = (estimate_abba(trace) if name == "slow_abba" else demodulate(trace))
            estimates.append(result.contrast_w)
            covered += result.ci_low_w <= trace.contrast_w <= result.ci_high_w
            rejected += result.ci_low_w > 0 or result.ci_high_w < 0
        sd = float(np.std(estimates, ddof=1))
        plan = plan_power(effect_fraction=args.effect_fraction,
                          unit_sd_fraction=sd / args.baseline_w,
                          unit_seconds=args.simulation_seconds, budget_hours=args.budget_hours,
                          alpha=args.alpha, target_power=args.target_power,
                          systematic_bound_fraction=args.systematic_bound_fraction)
        rows[name] = {"schedule": kind, "chip_seconds": chip,
                      "blocks_per_session": round(n_blocks), "session_seconds": args.simulation_seconds,
                      "mean_estimate_w": float(np.mean(estimates)),
                      "bias_w": float(np.mean(estimates)) - args.baseline_w * args.effect_fraction,
                      "session_sd_w": sd, "coverage_95": covered / args.trials,
                      "coverage_mc_se": math.sqrt(0.95 * 0.05 / args.trials),
                      "ci_warnings": result.warnings,
                      "empirical_rejection_rate_95": rejected / args.trials,
                      "plan_independent_sessions": asdict(plan)}
    fast_sd, slow_sd = rows["lockin"]["session_sd_w"], rows["slow_abba"]["session_sd_w"]
    return {"status": "SYNTHETIC_UNCALIBRATED", "noise_model": asdict(noise),
            "sample_rate_hz": args.sample_rate_hz, "trials": args.trials, "seed": args.seed,
            "designs": rows,
            "variance_ratio_slow_over_lockin": (slow_sd / fast_sd) ** 2 if fast_sd else None,
            "assumptions": [
                "Independent sessions, independently randomized schedules; no continuous-trace sqrt(time) claim.",
                "White SD is per sampling window; kHz is a simulation cadence, not a KM003C specification.",
                "Coverage/rejections use exploratory 95% HAC CIs with automatic lags; sizing uses requested alpha/power.",
                "Session SD and the variance ratio have Monte Carlo uncertainty; gains depend on these noise assumptions.",
                "No replay count is assigned to in-process swap chips; required_units means independent sessions.",
                "Acquisition hours omit setup, warm-up and guards; systematic bounds never average down."]}


def _step(value: str) -> tuple[float, float]:
    try:
        time, watts = map(float, value.split(":"))
        return time, watts
    except ValueError as exc:
        raise argparse.ArgumentTypeError("step must be SECONDS:SIGNED_WATTS") from exc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paired-only", action="store_true", help="stdlib-only study reproduction and pair sizing")
    parser.add_argument("--effect-fraction", type=float, default=1e-5)
    parser.add_argument("--budget-hours", type=float, default=1.0)
    parser.add_argument("--replay-seconds", type=float, default=100.0, help="illustrative pair member duration")
    parser.add_argument("--pair-sd-j", type=float, default=2.97)
    parser.add_argument("--baseline-energy-j", type=float, default=2700.0)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--target-power", type=float, default=0.8)
    parser.add_argument("--systematic-bound-fraction", type=float, default=0.0)
    parser.add_argument("--simulation-seconds", type=float, default=1024.0)
    parser.add_argument("--sample-rate-hz", type=float, default=8.0)
    parser.add_argument("--chip-seconds", type=float, default=2.0)
    parser.add_argument("--slow-chip-seconds", type=float, default=16.0)
    parser.add_argument("--schedule", choices=("square", "randomized_abba", "manchester"), default="randomized_abba")
    parser.add_argument("--baseline-w", type=float, default=27.0)
    parser.add_argument("--white-sd-w", type=float, default=0.03)
    parser.add_argument("--pink-sd-w", type=float, default=0.1)
    parser.add_argument("--thermal-amplitude-w", type=float, default=0.1)
    parser.add_argument("--thermal-tau-seconds", type=float, default=300.0)
    parser.add_argument("--step", type=_step, action="append", default=[])
    parser.add_argument("--burst-rate-hz", type=float, default=0.01)
    parser.add_argument("--burst-mean-seconds", type=float, default=1.0)
    parser.add_argument("--burst-amplitude-w", type=float, default=0.1)
    parser.add_argument("--trials", type=int, default=128)
    parser.add_argument("--seed", type=int, default=20261107)
    args = parser.parse_args(argv)
    try:
        if args.baseline_energy_j <= 0 or not math.isfinite(args.baseline_energy_j):
            raise ValueError("baseline_energy_j must be finite and positive")
        plan = plan_power(effect_fraction=args.effect_fraction,
                          unit_sd_fraction=args.pair_sd_j / args.baseline_energy_j,
                          unit_seconds=2 * args.replay_seconds, budget_hours=args.budget_hours,
                          alpha=args.alpha, target_power=args.target_power,
                          systematic_bound_fraction=args.systematic_bound_fraction)
        report = {"schema": "joulewise.interp_energy.power.v1", "status": "DESK_ONLY",
                  "study_reference": study_reference(replay_seconds=args.replay_seconds),
                  "paired_plan": {**asdict(plan), "required_pairs": plan.required_units,
                                  "required_replays": 2 * plan.required_units,
                                  "baseline_energy_j": args.baseline_energy_j, "pair_sd_j": args.pair_sd_j},
                  "notes": ["Fraction means B-A divided by unmodulated baseline energy/power at equal duration.",
                            "Study reproduction always uses alpha=.05 and power=.8; paired_plan uses requested values.",
                            "Statistical plans are not registered claim/equivalence intervals or hardware validation."]}
        if not args.paired_only:
            report["synthetic_comparison"] = compare_synthetic(args)
        print(json.dumps(report, indent=2, allow_nan=False))
    except (ValueError, RuntimeError, OverflowError) as exc:
        print(json.dumps({"status": "invalid_plan", "error": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
