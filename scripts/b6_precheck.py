#!/usr/bin/env python3
"""Collect pre-session evidence without arming a session."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.b6.precheck import run_precheck, exit_code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("pack", "measurement-root", "state-root", "out"):
        parser.add_argument("--" + name, required=True, type=str if name == "pack" else Path)
    for name in ("ledger", "registration-dir", "thresholds", "disk-targets"):
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args(argv)
    try:
        result = run_precheck(args.pack, args.measurement_root, args.state_root, out=args.out,
                              ledger=args.ledger, registration_dir=args.registration_dir,
                              thresholds=json.loads(args.thresholds.read_text()) if args.thresholds else None,
                              disk_targets=json.loads(args.disk_targets.read_text()) if args.disk_targets else None)
    except Exception as exc:
        print(f"precheck internal error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(result["decision"])
    return exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
