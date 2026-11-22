#!/usr/bin/env python3
"""Campaign kit, span queue and BLOCK-QUEUE ledger: validate, decide, report. Read-only.

    python3.13 -B scripts/cadence_queue.py validate-kit KIT.json [--repo PATH] [--batch-window HH:MM-HH:MM]
    python3.13 -B scripts/cadence_queue.py gen-legs --campaign-id ID --master-seed N --n-legs N \\
        --bands a,b,c --prefill-tokens N --decode-tokens N
    python3.13 -B scripts/cadence_queue.py gen-legs --law sha256-cells-v1 --campaign-id ID --master-seed N \\
        --n-legs N --bands q0 --prompt-tokens 2000,10000,19458 --g0-shapes own --decode-tokens N
    python3.13 -B scripts/cadence_queue.py validate-queue [QUEUE.json] [--kits-root .]
    python3.13 -B scripts/cadence_queue.py next [--queue Q] [--evidence E.json] [--issues I.json] [--now EPOCH]
    python3.13 -B scripts/cadence_queue.py checklist --kit KIT.json --kit-sha256 HEX --observations O.json \\
        [--batch-window HH:MM-HH:MM]
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

from joulewise.cadence import blocks, ctl, kit as kitmod, kit_v11, queue as q  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _fail(problems):
    for p in problems:
        print(f"REFUSE {p}")
    return 1


def _window(text):
    if not text:
        return kitmod.OS_BATCH_WINDOW
    h0, m0, h1, m1 = (int(x) for x in text.replace("-", ":").split(":"))
    return ((h0, m0), (h1, m1))


def cmd_validate_kit(args):
    try:
        kit, sha = kitmod.load_kit(args.kit, batch_window=_window(args.batch_window))
    except kitmod.KitError as error:
        return _fail(error.problems)
    problems = kitmod.verify_frozen(kit, args.repo) if args.repo else []
    if problems:
        return _fail(problems)
    print(json.dumps({"ok": True, "campaign_id": kit["campaign_id"], "kit_sha256": sha,
                      "frozen_commit": kit["frozen"]["commit"], "legs": len(kit["legs"]),
                      "frozen_paths_verified": bool(args.repo)}, sort_keys=True))
    return 0


def _pairs(text):
    """``"19458:3724:4096,19458:3151:4096"`` -> sha256-qual-v1's ``pairs`` (prefill:cap:cap per pair)."""
    out = []
    for item in text.split(","):
        tokens, *caps = (int(x) for x in item.split(":"))
        out.append({"prefill_tokens": tokens, "decode_tokens": caps})
    return out


def cmd_gen_legs(args):
    if args.law == kit_v11.QUAL_LAW:
        if not (args.spans and args.span_a_tokens and args.pairs and args.g0_shapes):
            print("REFUSE gen-legs --law sha256-qual-v1 needs --spans, --span-a-tokens, --pairs and --g0-shapes")
            return 2
        law = {"method": kit_v11.QUAL_LAW, "master_seed": args.master_seed, "n_legs": args.n_legs,
               "bands": args.bands.split(","), "spans": args.spans,
               "span_a_tokens": [int(x) for x in args.span_a_tokens.split(",")], "pairs": _pairs(args.pairs),
               "g0_shapes": args.g0_shapes.split(",")}
        problems = []
        kit_v11._check_law(law, problems)
        try:
            if problems:
                raise kitmod.KitError(problems)
            legs = kit_v11.generate_legs(args.campaign_id, law, {"decode_tokens": args.decode_tokens})
        except kitmod.KitError as error:
            return _fail(error.problems)
        print(json.dumps({"seed_law": law, "legs": legs}, indent=1))
        return 0
    if args.law == kit_v11.LAW:
        if not (args.prompt_tokens and args.g0_shapes):
            print("REFUSE gen-legs --law sha256-cells-v1 needs --prompt-tokens and --g0-shapes")
            return 2
        law = {"method": kit_v11.LAW, "master_seed": args.master_seed, "n_legs": args.n_legs,
               "bands": args.bands.split(","), "prompt_tokens": [int(x) for x in args.prompt_tokens.split(",")],
               "g0_shapes": args.g0_shapes.split(",")}
        try:
            legs = kit_v11.generate_legs(args.campaign_id, law, {"decode_tokens": args.decode_tokens})
        except kitmod.KitError as error:
            return _fail(error.problems)
        print(json.dumps({"seed_law": law, "legs": legs}, indent=1))
        return 0
    if args.prefill_tokens is None:
        print("REFUSE gen-legs --law sha256-v1 needs --prefill-tokens")
        return 2
    law = {"method": "sha256-v1", "master_seed": args.master_seed, "n_legs": args.n_legs,
           "bands": args.bands.split(",")}
    legs = kitmod.generate_legs(args.campaign_id, law, {"prefill_tokens": args.prefill_tokens,
                                                        "decode_tokens": args.decode_tokens})
    print(json.dumps({"seed_law": law, "legs": legs}, indent=1))
    return 0


def qual_roster_problems(doc, kits_root):
    """RL-165 section 8.1 on a ``sha256-qual-v1`` kit's queued rosters (#794 cold seat F2): a span lies inside
    one of the law's spans, does not split a type-L pair, and does not start on a pair member (which would make
    that leg the span's capture). A re-run that needs any of these goes to the research lead, not to a queue."""
    problems = []
    for span in doc.get("spans", []):
        path = (span.get("kit") or {}).get("path")
        if not isinstance(path, str) or not (Path(kits_root) / path).is_file():
            continue
        kit, _ = kitmod.load_kit(Path(kits_root) / path)
        law = kit.get("seed_law") or {}
        if law.get("method") != kit_v11.QUAL_LAW:
            continue
        per = len(kit["legs"]) // law["spans"]
        index = {leg["leg_id"]: i for i, leg in enumerate(kit["legs"])}
        roster = [index.get(leg_id) for leg_id in span.get("legs", [])]
        sid = span.get("span_id")
        if not roster or None in roster:
            continue   # validate_queue names unknown legs
        if len({i // per for i in roster}) != 1:
            problems.append(f"{sid}: roster crosses the law's spans of {per} (sha256-qual-v1; RL-165 section 8.1)")
        pairs = {}
        for leg in kit["legs"]:
            if leg.get("pair"):
                pairs.setdefault(leg["pair"], set()).add(leg["leg_id"])
        names = set(span.get("legs", []))
        for pair, members in sorted(pairs.items()):
            if 0 < len(members & names) < len(members):
                problems.append(f"{sid}: roster splits type-L pair {pair} ({', '.join(sorted(members))}); "
                                "the research lead rules a re-run that splits a pair")
        first = kit["legs"][roster[0]]
        if first.get("leg_type") != "A" or first.get("pair") is not None:
            problems.append(f"{sid}: roster starts on {first['leg_id']}, a type-L pair member; a span's first leg "
                            "is type A (RL-165 section 8.1)")
    return problems


def cmd_validate_queue(args):
    try:
        doc = q.load_queue(args.queue, args.kits_root)
        problems = qual_roster_problems(doc, args.kits_root)
    except q.QueueError as error:
        return _fail(error.problems)
    except (OSError, ValueError, kitmod.KitError) as error:
        return _fail([str(error)])
    if problems:
        return _fail(problems)
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
    kit, sha = kitmod.load_kit(args.kit, batch_window=_window(args.batch_window))
    obs = json.loads(Path(args.observations).read_text())
    if kit["schema"] in (kit_v11.SCHEMA, ctl.SCHEMA):
        rows = kit_v11.evaluate_checklist(kit, obs, expected_kit_sha256=args.kit_sha256,
                                          batch_window=_window(args.batch_window) if args.batch_window else None)
        if kit["schema"] == ctl.SCHEMA:
            for name, check, values in (("ctl_authority", ctl.require_issued, (kit,)),
                                        ("ctl_queue_hash", ctl.require_queue_kit_hash, (args.kit_sha256, sha))):
                try:
                    check(*values)
                except kitmod.KitError as error:
                    rows.append({"id": name, "kind": name, "ok": False, "detail": str(error)})
    else:
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
    s.add_argument("--batch-window", help="HH:MM-HH:MM local blackout for the template check "
                                          "(default 11:45-13:15; RL-149 section 2.9 item 4 rules 02:00-02:35)")
    s = sub.add_parser("gen-legs")
    s.add_argument("--law", choices=("sha256-v1", *kit_v11.LAWS), default="sha256-v1")
    s.add_argument("--campaign-id", required=True); s.add_argument("--master-seed", type=int, required=True)
    s.add_argument("--n-legs", type=int, required=True); s.add_argument("--bands", required=True)
    s.add_argument("--prefill-tokens", type=int, help="sha256-v1: every leg's prompt size")
    s.add_argument("--prompt-tokens", help="sha256-cells-v1: the sizes, comma-separated")
    s.add_argument("--g0-shapes", help="sha256-cells-v1 and sha256-qual-v1: own (own-shaped) or own,span")
    s.add_argument("--spans", type=int, help="sha256-qual-v1: the number of spans of equal length")
    s.add_argument("--span-a-tokens", help="sha256-qual-v1: each span's type-A sizes, comma-separated")
    s.add_argument("--pairs", help="sha256-qual-v1: one type-L pair per span, prefill:cap:cap, comma-separated")
    s.add_argument("--decode-tokens", type=int, required=True)
    s = sub.add_parser("validate-queue"); s.add_argument("queue", nargs="?", default=str(ROOT / q.QUEUE_PATH))
    s.add_argument("--kits-root", default=str(ROOT))
    s = sub.add_parser("next"); s.add_argument("--queue", default=str(ROOT / q.QUEUE_PATH))
    s.add_argument("--evidence"); s.add_argument("--issues"); s.add_argument("--now", type=float)
    s = sub.add_parser("checklist"); s.add_argument("--kit", required=True)
    s.add_argument("--kit-sha256", required=True); s.add_argument("--observations", required=True)
    s.add_argument("--batch-window", help="HH:MM-HH:MM local blackout (v1.1 span_window line; default none, RL-171)")
    s = sub.add_parser("blocks"); s.add_argument("ledger", nargs="?", default=str(ROOT / blocks.LEDGER_PATH))
    s.add_argument("--kits-root", default=str(ROOT))
    args = p.parse_args(argv)
    return {"validate-kit": cmd_validate_kit, "gen-legs": cmd_gen_legs, "validate-queue": cmd_validate_queue,
            "next": cmd_next, "checklist": cmd_checklist, "blocks": cmd_blocks}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
