#!/usr/bin/env python3
"""Prepare or desk a smoke. The loop owns launching collection."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.b6 import smoke


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--pack", required=True)
    prepare.add_argument("--code-commit", required=True)
    for name in ("claim-measurement-root", "smoke-root", "state-root", "plan-inputs", "precheck"):
        prepare.add_argument("--" + name, type=Path, required=True)
    prepare.add_argument("--registration-dir", type=Path, default=None,
                         help="block-6 registration directory (default: the clone's configs/b6/registration)")
    desk = commands.add_parser("desk")
    desk.add_argument("--state", type=Path, required=True)
    desk.add_argument("--driver-exit", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            prepared = smoke.prepare(args.pack, args.code_commit, args.claim_measurement_root, args.smoke_root,
                                     state_root=args.state_root, plan_inputs=json.loads(args.plan_inputs.read_text()),
                                     fp=json.loads(args.precheck.read_text())["fingerprint"],
                                     registration_dir=args.registration_dir)
            print(prepared.smoke_dir / "smoke-state.json")
            return 0
        prepared = smoke.SmokePrepared.from_json(json.loads(args.state.read_text()))
        result = smoke.desk(prepared, driver_exit=args.driver_exit)
        print(result["status"])
        return {"pass": 0, "physics": 10, "fail": 20}[result["status"]]
    except Exception as exc:
        print(f"smoke internal error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
