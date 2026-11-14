#!/usr/bin/env python3
"""Build one span's Air desk table under AIR-QUIET.lock. No energy is opened.

    python3.13 -B scripts/air/cadence_desk.py build --plan-id PLAN --input DIR --out DIR \\
        (--kit KIT.json | --adapter r1-journal-v1) [--history H.json] [--lock PATH]

Exit 0 built with no named stop, 3 built and a named stop fired (page), 4 the
lock is held or stale (nothing run), 1 refused (a guard fired; nothing written), 2 usage.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from joulewise.cadence import desk, kit as kitmod  # noqa: E402

DEFAULT_RULES = {"instrument_fault": True, "refusal": True, "contaminated_redos_max": 3,
                 "contaminated_redos_scope": "span", "band_unreachable_max": 2,
                 "band_unreachable_scope": "span", "leg_time_factor": 1.5}


def build(args):
    if args.kit:
        kit, _ = kitmod.load_kit(args.kit)
        adapter, rules = kit["desk"]["adapter"], kit["stop_rules"]
    else:
        adapter, rules = args.adapter, DEFAULT_RULES
    history = json.loads(Path(args.history).read_text()) if args.history else []
    try:
        with desk.air_quiet_lock(f"cadence-desk:{args.plan_id}", Path(args.lock)):
            _, stops = desk.build_desk(plan_id=args.plan_id, input_dir=args.input, out_dir=args.out,
                                       adapter=adapter, stop_rules=rules, history=history)
    except desk.LockBusy as error:
        print(f"LOCK {error}")
        return 4
    except desk.DeskRefusal as error:
        print(f"REFUSE {error}")
        return 1
    for s in stops:
        print(f"STOP {s['code']} {s['detail']}")
    print(f"built {Path(args.out) / 'JOURNAL-TABLE.md'}; stops {len(stops)}")
    return 3 if stops else 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--plan-id", required=True); b.add_argument("--input", required=True)
    b.add_argument("--out", required=True)
    g = b.add_mutually_exclusive_group(required=True)
    g.add_argument("--kit"); g.add_argument("--adapter", choices=sorted(desk.ALLOWED_FILES))
    b.add_argument("--history"); b.add_argument("--lock", default=str(desk.QUIET_LOCK))
    args = p.parse_args(argv)
    return build(args)


if __name__ == "__main__":
    raise SystemExit(main())
