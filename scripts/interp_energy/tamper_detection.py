#!/usr/bin/env python3
"""DESK only: print a synthetic detector report and independently sized design.

No file inputs, collectors, native backends, model weights or network access.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from joulewise.interp_energy.tamper_challenge import equivalence_power, plan_binary
from joulewise.interp_energy.tamper_detection import StressNoise, edit_catalogue, simulate_detector


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design-only", action="store_true", help="stdlib-only power arithmetic")
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--mode", choices=("replay", "episode"), default="replay")
    parser.add_argument("--copies", type=int, help="simulation count only; does not change the sized design")
    parser.add_argument("--alternative", type=float, default=.6, help="forced-choice probability under the alternative")
    args = parser.parse_args(argv)
    try:
        # Sham is an FPR control. Every remaining class is searched, even if a
        # particular expected effect is zero; do not omit it from multiplicity.
        families = len(edit_catalogue()) - 1
        binary = plan_binary(families=families, alternative_probability=args.alternative)
        copies = binary.copies_per_class
        total_copies = 2 * families * copies  # separate matched sham for each
        report = {"status": "SYNTHETIC_DESIGN_NOT_REGISTERED", "binary_plan": asdict(binary),
                  "replays_per_copy_assumed": 8, "total_copies_with_matched_shams": total_copies,
                  "acquisition_hours_excluding_overhead": total_copies * 8 * 200 / 3600,
                  "equivalence_sensitivity": {
                      str(sessions): equivalence_power(copies=copies, replays_per_copy=8,
                                                       sessions=sessions, margin_j=2.7,
                                                       systematic_bound_j=.5, alpha=.05 / families)
                      for sessions in (4, 16, 64, 128)},
                  "limits": ["Copies are independent edit realizations; replays do not increase binary n.",
                             "Raw acquisition hours omit setup, load, thermal and custody overhead.",
                             "Planning alone is not authorization or a registered experiment."]}
        if not args.design_only:
            noise = (StressNoise() if args.mode == "replay"
                     else StressNoise(gpu_sd_j=35, dc_sd_j=80, time_sd_s=1.5))
            report["simulation"] = simulate_detector(copies_per_class=(
                copies if args.copies is None else args.copies), seed=args.seed, noise=noise)
        print(json.dumps(report, indent=2, allow_nan=False))
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
