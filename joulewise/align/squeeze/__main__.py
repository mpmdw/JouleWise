"""Emit a JSON planning sweep using synthetic scores only; no file inputs."""

import argparse
from dataclasses import asdict
import json
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--heldout-size", type=int, required=True,
                        help="explicit planning/test size; no registered size is assumed")
    parser.add_argument("--m", type=int, nargs="+", default=[20, 39, 28],
                        help="calibration sizes; 28 is the public v3 pilot pool")
    parser.add_argument("--hidden-tokens", type=float, nargs="+",
                        default=[0, 128, 256, 300, 512, 1024, 2048])
    parser.add_argument("--residual-sd", type=float, nargs="+", default=[19, 38, 58])
    parser.add_argument("--replay-sd", type=float, default=2.0)
    parser.add_argument("--correlation", type=float, default=0.0)
    parser.add_argument("--student-df", type=float)
    parser.add_argument("--coefficients", type=float, nargs=5,
                        default=[2, 0.001, 0.30, 0.00004, 0.0000002],
                        metavar=("B0", "BP", "BD", "BCD", "BCP"))
    parser.add_argument("--form", choices=["sequence", "turn"], default="sequence")
    parser.add_argument("--monitor-tokens-per-score", type=float, default=128.0)
    parser.add_argument("--trials", type=int, default=256)
    parser.add_argument("--selection-size", type=int, default=256)
    parser.add_argument("--seed", type=int, default=20261107)
    args = parser.parse_args(argv)
    try:
        from .adversary import MonitorResponse, Noise, attack_effect, attack_families
        from .detection import JointScore
        from .power import adaptive_frontier, estimate_power
        from .residual import Carrier, ResidualModel
        import numpy as np
    except ImportError as exc:
        parser.exit(2, f"squeeze requires the optional NumPy extra (.[squeeze]): {exc}\n")
    try:
        model = ResidualModel(tuple(args.coefficients), args.form)
        carrier = Carrier()
        monitor = MonitorResponse(args.monitor_tokens_per_score)
        families = attack_families()
        output = {"status": "DRAFT_SYNTHETIC_ONLY_NOT_REGISTERED",
                  "heldout_size_status": "caller_supplied_not_verified_against_a_locked_cohort",
                  "seed": args.seed, "model": asdict(model), "carrier": asdict(carrier),
                  "monitor_response_assumption": asdict(monitor),
                  "attack_grids": {k: [asdict(a) for a in v] for k, v in families.items()},
                  "assumptions": ["iid calibration/test episodes and frozen score",
                                  "whole-episode trusted external DC integral",
                                  "2 J replay SD is included in total residual SD",
                                  "monitor response and attack cost ratios are unvalidated",
                                  "cohort probabilities account for a shared random threshold"],
                  "power": [], "frontiers": []}
        stream = 0
        for sd in args.residual_sd:
            noise = Noise(sd, args.replay_sd, args.correlation, args.student_df)
            for m in args.m:
                for h in args.hidden_tokens:
                    for family, attacks in families.items():
                        # Unique deterministic streams per table row.
                        stream += 1
                        row = estimate_power(model, m=m, heldout_size=args.heldout_size,
                                             hidden_work_tokens=h, attacks=attacks, noise=noise,
                                             carrier=carrier, monitor=monitor, trials=args.trials,
                                             selection_size=args.selection_size, seed=args.seed+stream)
                        output["power"].append({"family": family, "noise": asdict(noise),
                                                **row.to_dict()})
                    stream += 1
                    rule = JointScore(sd)
                    calibration = noise.sample(np.random.default_rng(args.seed+stream), m)
                    threshold = rule.calibrate(calibration)
                    # Fixed-threshold frontier: independent of power table re-calibrations.
                    stream += 1
                    rows = adaptive_frontier(model, threshold=threshold,
                                             attacks=families["combined"], hidden_work_tokens=h,
                                             heldout_size=args.heldout_size, noise=noise,
                                             carrier=carrier, monitor=monitor,
                                             selection_size=args.selection_size, seed=args.seed+stream)
                    output["frontiers"].append({"m": m, "hidden_work_tokens": h,
                                                "noise": asdict(noise),
                                                "threshold": asdict(threshold), "points": rows})
        # Print supplied effects explicitly so a result can be re-derived in joules.
        output["effect_example"] = asdict(attack_effect(
            model, carrier, families["combined"][0], args.hidden_tokens[-1], monitor))
        json.dump(output, sys.stdout, indent=2, allow_nan=False)
        sys.stdout.write("\n")
    except (ValueError, OverflowError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
