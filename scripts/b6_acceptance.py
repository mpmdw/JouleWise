#!/usr/bin/env python3
"""Write one structure-only block-six acceptance and its emitted flags."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b6.session import accept_archive


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--registration-dir", type=Path, required=True)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args(argv)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        result, _ = accept_archive(args.archive, plan, args.registration_dir, ledger_path=args.ledger,
                                   plan_path=args.plan, smoke=args.smoke)
        print(json.dumps({"verdict": result.verdict, "counting": result.counting,
                          "structural": result.structural, "flag_counts": result.record["flag_counts"]}, sort_keys=True))
        return 0
    except Exception as exc:
        print("block-six acceptance program fault: " + type(exc).__name__, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
