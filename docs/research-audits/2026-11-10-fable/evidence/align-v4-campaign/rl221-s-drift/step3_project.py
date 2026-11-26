#!/usr/bin/env python3
"""RL-221 named read. Projects the drift tripwire's members out of lm-interim-01's RESTRICTED/step3.json.

Usage (a detached command outside a seat; the source is custody):
    python3 -I -B step3_project.py <RESTRICTED/step3.json> <output.json>

Written to the output, and nothing else from the source:
  * the tripwire object: value, cell, trips, decision, the two thresholds and the one applied;
  * per prompt-size cell: prompt_tokens, status, n_legs, the NUMBER of failed legs, gamma_estimable, statistic (iii)
    in its linear and exp forms, the SIGN of the all-legs gamma ("+", "-", "0" or null), and whether every reported
    gamma (all legs, and each leave-one-leg-out fit) has that same sign;
  * the sha256 of the source file.
Not written: any gamma value or standard error, any temperature, (iv), (v), (vi), any per-leg or per-block entry,
any leg id, the custody record.

Standard output is one line: the source sha256, the output sha256 and the number of cells. No value is printed.
An exception prints its type only. The output is created exclusively (an existing file refuses)."""
import hashlib
import json
import sys


def sign(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return "+" if value > 0 else "-" if value < 0 else "0"


def cell_view(cell):
    gamma = cell.get("ii_gamma") or {}
    detail = ((cell.get("details") or {}).get("ii_gamma_per_degC") or {})
    all_legs = (gamma.get("all_nine_legs") or {}).get("slope")
    reported = [all_legs, (gamma.get("without_two_high_power_legs") or {}).get("slope")]
    reported += list((detail.get("leave_one_leg_out") or {}).values())
    signs = {sign(v) for v in reported if sign(v) is not None}
    return {
        "prompt_tokens": cell.get("prompt_tokens"),
        "status": cell.get("status"),
        "n_legs": cell.get("n_legs"),
        "failed_legs": len(cell.get("failed_legs") or []),
        "gamma_estimable": cell.get("gamma_estimable"),
        "iii_drift_fraction_linear": cell.get("iii_drift_fraction_linear"),
        "iii_drift_fraction_exp_form": cell.get("iii_drift_fraction_exp_form"),
        "gamma_sign_all_legs": sign(all_legs),
        "gamma_signs_agree": len(signs) == 1,
        "gamma_fits_reported": len([v for v in reported if sign(v) is not None]),
    }


TRIPWIRE_KEYS = ("value", "cell", "trips", "decision", "threshold", "fallback_threshold", "threshold_applied")


def main(argv):
    if len(argv) != 3:
        print("usage: step3_project.py <step3.json> <output.json>")
        return 2
    try:
        raw = open(argv[1], "rb").read()
        doc = json.loads(raw)
        tripwire = doc["tripwire"]
        out = {
            "schema": "rl221.step3_tripwire_projection.v1",
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "tripwire": {key: tripwire.get(key) for key in TRIPWIRE_KEYS},
            "cells": [cell_view(cell) for cell in doc["cells"]],
        }
        data = (json.dumps(out, sort_keys=True, indent=1, allow_nan=False) + "\n").encode()
        with open(argv[2], "xb") as handle:
            handle.write(data)
    except Exception as error:  # never the message: it could carry a value
        print("refused:", type(error).__name__)
        return 1
    print(out["source_sha256"], hashlib.sha256(data).hexdigest(), len(out["cells"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
