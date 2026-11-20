#!/usr/bin/env python3
"""Timing-ledger wrapper (RL-127 term 7).

    timing_ledger.py run --stage <name> [--budget-s N | --predicted-s P] -- <cmd...>
    timing_ledger.py phase --stage <name> --name <phase> --start-epoch-s A --end-epoch-s B [--budget-s N]
    timing_ledger.py tail [-n 20]

`run` executes the command with inherited stdio and exits exactly as it did
(same code, or the same signal). It appends a start marker and an end row to
the ledger (default /Volumes/JW-EXT/ledger/timing.jsonl; `--ledger` or
JW_TIMING_LEDGER overrides). A ledger failure never changes the command's
outcome. Without `--budget-s`, the stage's RL-127 default applies;
`--predicted-s P` on a dry-run stop sets the budget to 2 x P.
Never run it inside a measured window.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.pipeline_time import budgets, ledger  # noqa: E402


def parse(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="mode", required=True)
    run = sub.add_parser("run", help="run a command under the ledger")
    run.add_argument("--stage", required=True)
    group = run.add_mutually_exclusive_group()
    group.add_argument("--budget-s", type=float)
    group.add_argument("--predicted-s", type=float, help="dry-run stop: budget = 2 x prediction")
    run.add_argument("--ledger")
    run.add_argument("--note", help="short free text kept on the record (no outcome-bearing content)")
    run.add_argument("command", nargs=argparse.REMAINDER)
    ph = sub.add_parser("phase", help="record an already-finished phase from its stamps")
    ph.add_argument("--stage", required=True)
    ph.add_argument("--name", required=True)
    ph.add_argument("--start-epoch-s", type=float, required=True)
    ph.add_argument("--end-epoch-s", type=float, required=True)
    ph.add_argument("--budget-s", type=float)
    ph.add_argument("--exit-code", type=int, default=0)
    ph.add_argument("--ledger")
    tail = sub.add_parser("tail", help="print the last rows")
    tail.add_argument("-n", type=int, default=20)
    tail.add_argument("--ledger")
    args = parser.parse_args(argv)
    if args.mode == "run":
        command = list(args.command)
        if command[:1] == ["--"]:
            command = command[1:]
        if not command:
            parser.error("run needs a command after --")
        args.command = command
    return args


def main(argv=None):
    args = parse(sys.argv[1:] if argv is None else argv)
    if args.mode == "run":
        budget = args.budget_s
        if args.predicted_s is not None:
            budget = budgets.dry_run_budget_s(args.predicted_s)
        status = ledger.run_wrapped(args.command, args.stage, budget_s=budget, path=args.ledger, note=args.note)
        ledger.exit_like(status)
    if args.mode == "phase":
        written = ledger.record_phase(args.name, args.stage, args.start_epoch_s, args.end_epoch_s,
                                      budget_s=args.budget_s, exit_code=args.exit_code, path=args.ledger)
        print(written or "timing_ledger: not written", file=sys.stderr if not written else sys.stdout)
        return 0 if written else 1
    rows = ledger.read_ledger(args.ledger)
    for row in rows[-args.n:]:
        print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
