#!/usr/bin/env python3
"""Campaign kit, span queue and BLOCK-QUEUE ledger: validate, decide, report. Read-only.

    python3.13 -B scripts/cadence_queue.py validate-kit KIT.json [--repo PATH]
    python3.13 -B scripts/cadence_queue.py gen-legs --campaign-id ID --master-seed N --n-legs N \\
        --bands a,b,c --prefill-tokens N --decode-tokens N
    python3.13 -B scripts/cadence_queue.py validate-queue [QUEUE.json] [--kits-root .]
    python3.13 -B scripts/cadence_queue.py next [--queue Q] [--evidence E.json] [--issues I.json] [--now EPOCH]
    python3.13 -B scripts/cadence_queue.py checklist --kit KIT.json --kit-sha256 HEX --observations O.json
    python3.13 -B scripts/cadence_queue.py blocks [LEDGER.json] [--kits-root .]

Exit 0 ok, 1 refused (problems printed one per line), 2 usage. Nothing here
writes, arms, installs or contacts a host. Design: docs/process/cadence_queue_design.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise.cadence import blocks, kit as kitmod, queue as q  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _fail(problems):
    for p in problems:
        print(f"REFUSE {p}")
    return 1


def cmd_validate_kit(args):
    try:
        kit, sha = kitmod.load_kit(args.kit)
    except kitmod.KitError as error:
        return _fail(error.problems)
    problems = kitmod.verify_frozen(kit, args.repo) if args.repo else []
    if problems:
        return _fail(problems)
    print(json.dumps({"ok": True, "campaign_id": kit["campaign_id"], "kit_sha256": sha,
                      "frozen_commit": kit["frozen"]["commit"], "legs": len(kit["legs"]),
                      "frozen_paths_verified": bool(args.repo)}, sort_keys=True))
    return 0


def cmd_gen_legs(args):
    law = {"method": "sha256-v1", "master_seed": args.master_seed, "n_legs": args.n_legs,
           "bands": args.bands.split(",")}
    legs = kitmod.generate_legs(args.campaign_id, law, {"prefill_tokens": args.prefill_tokens,
                                                        "decode_tokens": args.decode_tokens})
    print(json.dumps({"seed_law": law, "legs": legs}, indent=1))
    return 0


def cmd_validate_queue(args):
    try:
        doc = q.load_queue(args.queue, args.kits_root)
    except q.QueueError as error:
        return _fail(error.problems)
    except (OSError, ValueError, kitmod.KitError) as error:
        return _fail([str(error)])
    print(json.dumps({"ok": True, "queue_id": doc["queue_id"], "spans": len(doc["spans"]),
                      "plan_ids": [q.plan_id(s) for s in doc["spans"]]}, sort_keys=True))
    return 0


def cmd_next(args):
    try:
        doc = q.load_queue(args.queue)
    except (q.QueueError, OSError, ValueError) as error:
        return _fail(getattr(error, "problems", [str(error)]))
    evidence = json.loads(Path(args.evidence).read_text()) if args.evidence else {}
    issues = json.loads(Path(args.issues).read_text()) if args.issues else []
    halts = q.halts_from_issues(issues, doc)
    decision = q.next_action(doc, evidence, halts, args.now if args.now is not None else time.time())
    print(json.dumps(decision.as_dict(), indent=1, sort_keys=True))
    return 0


def cmd_checklist(args):
    kit, _ = kitmod.load_kit(args.kit)
    obs = json.loads(Path(args.observations).read_text())
    rows = kitmod.evaluate_checklist(kit, obs, expected_kit_sha256=args.kit_sha256)
    for r in rows:
        print(f"{'OK  ' if r['ok'] else 'FAIL'} {r['id']:<28} {r['kind']:<24} {r['detail']}")
    ok = all(r["ok"] for r in rows)
    print("CHECKLIST " + ("PASS: every line holds" if ok else "FAIL: nothing arms"))
    return 0 if ok else 1


def cmd_blocks(args):
    try:
        doc = blocks.load_ledger(args.ledger, args.kits_root)
    except blocks.LedgerError as error:
        return _fail(error.problems)
    print("\n".join(blocks.status_lines(doc)))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("validate-kit"); s.add_argument("kit"); s.add_argument("--repo")
    s = sub.add_parser("gen-legs")
    s.add_argument("--campaign-id", required=True); s.add_argument("--master-seed", type=int, required=True)
    s.add_argument("--n-legs", type=int, required=True); s.add_argument("--bands", required=True)
    s.add_argument("--prefill-tokens", type=int, required=True); s.add_argument("--decode-tokens", type=int, required=True)
    s = sub.add_parser("validate-queue"); s.add_argument("queue", nargs="?", default=str(ROOT / q.QUEUE_PATH))
    s.add_argument("--kits-root", default=str(ROOT))
    s = sub.add_parser("next"); s.add_argument("--queue", default=str(ROOT / q.QUEUE_PATH))
    s.add_argument("--evidence"); s.add_argument("--issues"); s.add_argument("--now", type=float)
    s = sub.add_parser("checklist"); s.add_argument("--kit", required=True)
    s.add_argument("--kit-sha256", required=True); s.add_argument("--observations", required=True)
    s = sub.add_parser("blocks"); s.add_argument("ledger", nargs="?", default=str(ROOT / blocks.LEDGER_PATH))
    s.add_argument("--kits-root", default=str(ROOT))
    args = p.parse_args(argv)
    return {"validate-kit": cmd_validate_kit, "gen-legs": cmd_gen_legs, "validate-queue": cmd_validate_queue,
            "next": cmd_next, "checklist": cmd_checklist, "blocks": cmd_blocks}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
