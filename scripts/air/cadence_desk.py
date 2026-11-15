#!/usr/bin/env python3
"""Build one span's Air desk table under AIR-QUIET.lock. No energy is opened.

    python3.13 -B scripts/air/cadence_desk.py final --plan-id PLAN --bundle DIR --manifest-sha256 HEX \\
        --queue QUEUE.json --kit KIT.json --out DIR [--history H.json] [--hand-table hand_table.json] \\
        [--hand-sample] [--lock PATH]
    python3.13 -B scripts/air/cadence_desk.py build --plan-id PLAN --input DIR --out DIR \\
        (--kit KIT.json | --adapter r1-journal-v1) [--history H.json] [--lock PATH]

``final`` is the only path to desk-final (RL-172 section (c); ``joulewise.cadence.desk_final``): the
authenticated bundle against the queue entry's roster and the kit's identities. It always writes
``desk_verdict.json`` (``desk_final`` true/false with reasons), a negative or error result included.
Exit 0 desk-final with nothing held, 3 the verdict is not final or holds the next arm (a named stop, a
hand-table disagreement, or a hand table due), 1 the desk refused or erred (verdict written), 4 the lock
is held or stale (nothing run, no verdict), 2 usage.

``build`` is the frozen table builder kept for the R1 adapter and by-hand use. It writes a verdict with
``desk_final: false`` ("no expected roster, no authentication"), so it can never satisfy line 9.
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

from joulewise.cadence import desk, desk_final, kit as kitmod  # noqa: E402

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
    legacy = {"schema": desk_final.VERDICT_SCHEMA, "plan_id": args.plan_id, "desk_final": False,
              "reasons": ["legacy build: no expected roster, no authenticated bundle (RL-172 section (c)); "
                          "use cadence_desk.py final"], "named_stops": stops, "next_arm_hold": bool(stops)}
    (Path(args.out) / desk_final.VERDICT_NAME).write_text(
        json.dumps(desk_final._finish(legacy), sort_keys=True, indent=1) + "\n", encoding="utf-8")
    print(f"built {Path(args.out) / 'JOURNAL-TABLE.md'}; stops {len(stops)}; not desk-final (legacy build)")
    return 3 if stops else 0


def final(args):
    history = json.loads(Path(args.history).read_text()) if args.history else []
    try:
        with desk.air_quiet_lock(f"cadence-desk-final:{args.plan_id}", Path(args.lock)):
            verdict = desk_final.judge_span(
                plan_id=args.plan_id, bundle_dir=args.bundle, manifest_sha256=args.manifest_sha256,
                queue_path=args.queue, kit_path=args.kit, out_dir=args.out, history=history,
                hand_table_path=args.hand_table, hand_sample=args.hand_sample, allow_mock=args.allow_mock)
    except desk.LockBusy as error:
        print(f"LOCK {error}")
        return 4
    for s in verdict["named_stops"]:
        print(f"STOP {s['code']} ({s['kind']}) {s['detail']}")
    for g in verdict["hand_gates"]:
        print(f"HAND GATE REQUIRED {g['gate']} ({g['ruling']})")
    print(f"desk_final {str(verdict['desk_final']).lower()}; next_arm_hold {str(verdict['next_arm_hold']).lower()}; "
          f"verdict {Path(args.out) / desk_final.VERDICT_NAME}")
    if verdict["error"] is not None:
        return 1
    return 0 if verdict["desk_final"] and not verdict["next_arm_hold"] else 3


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--plan-id", required=True); b.add_argument("--input", required=True)
    b.add_argument("--out", required=True)
    g = b.add_mutually_exclusive_group(required=True)
    g.add_argument("--kit"); g.add_argument("--adapter", choices=sorted(desk.ALLOWED_FILES))
    b.add_argument("--history"); b.add_argument("--lock", default=str(desk.QUIET_LOCK))
    f = sub.add_parser("final", help="desk-final verdict on an authenticated bundle (RL-172 section (c))")
    f.add_argument("--plan-id", required=True); f.add_argument("--bundle", required=True)
    f.add_argument("--manifest-sha256", required=True,
                   help="the bundle manifest's sha256 from the controller's per-span record (the anchor)")
    f.add_argument("--queue", required=True); f.add_argument("--kit", required=True)
    f.add_argument("--out", required=True); f.add_argument("--history")
    f.add_argument("--hand-table", help="the lead's hand table (hand_table.json), compared field by field")
    f.add_argument("--hand-sample", action="store_true", help="the lead's seeded draw selected this span")
    f.add_argument("--allow-mock", action="store_true",
                   help="synthetic bundles only: accept a mock receipt (the verdict says mock: true)")
    f.add_argument("--lock", default=str(desk.QUIET_LOCK))
    args = p.parse_args(argv)
    return final(args) if args.cmd == "final" else build(args)


if __name__ == "__main__":
    raise SystemExit(main())
