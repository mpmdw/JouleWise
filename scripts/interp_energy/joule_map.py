#!/usr/bin/env python3
"""Desk-only JOULE-MAP plan/demo/reducer. No capture or model execution path."""

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from joulewise.interp_energy.joule_map import Episode, analyze_map, desk_plan, synthetic_demo


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--plan-only", action="store_true")
    modes.add_argument("--demo", action="store_true")
    modes.add_argument("--input", type=Path, help="read this one episode JSON; no paths inside are followed")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--bootstrap-replicates", type=int, default=2000)
    parser.add_argument("--bootstrap-block-units", type=int, default=1)
    parser.add_argument("--confidence", type=float, default=.95)
    args = parser.parse_args(argv)
    try:
        if args.plan_only:
            result = desk_plan()
        else:
            if args.demo:
                rows, audits = synthetic_demo(seed=args.seed)
            else:
                payload = json.loads(args.input.read_text(encoding="utf-8"), object_pairs_hook=_unique_object,
                                     parse_constant=lambda v: (_ for _ in ()).throw(ValueError(f"nonfinite JSON: {v}")))
                if not isinstance(payload, dict) or set(payload) != {"episodes", "additivity"}:
                    raise ValueError("input must contain exactly episodes and additivity arrays")
                if not isinstance(payload["episodes"], list) or not isinstance(payload["additivity"], list):
                    raise ValueError("episodes and additivity must be arrays")
                rows = [Episode(**row) for row in payload["episodes"]]
                audits = payload["additivity"]
            result = analyze_map(rows, confidence=args.confidence,
                                 bootstrap_replicates=args.bootstrap_replicates,
                                 bootstrap_block_units=args.bootstrap_block_units,
                                 seed=args.seed, additivity=audits)
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
        return 0
    except (ValueError, TypeError, OSError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
