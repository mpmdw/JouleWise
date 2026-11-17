#!/usr/bin/env python3
"""The Air desk under AIR-QUIET.lock. No energy is opened. Wire format: docs/process/cadence_desk_format.md.

    python3.13 -B scripts/air/cadence_desk.py final --plan-id PLAN --repo CLONE \\
        --bundle-ref refs/remotes/origin/desk-bundles/PLAN --allowed-signers SIGNERS \\
        --kit KIT.json --out DIR [--queue QUEUE.json] \\
        --history-prefix refs/remotes/origin/cadence-desk-final/ --history-signers DESK_SIGNERS \\
        [--hand-table hand_table.json] [--hand-sample] [--lock PATH]
    python3.13 -B scripts/air/cadence_desk.py publish --plan-id PLAN --out DIR --repo CLONE --signing-key KEY
    python3.13 -B scripts/air/cadence_desk.py sample-plan --queue QUEUE.json --kit KIT.json
    python3.13 -B scripts/air/cadence_desk.py build --plan-id PLAN --input DIR --out DIR \\
        (--kit KIT.json | --adapter r1-journal-v1) [--history H.json] [--lock PATH]

``final`` is the only path to desk-final (RL-172 section (c); ``joulewise.cadence.desk_final``). It verifies
the controller's SSH-signed bundle commit (``desk_transport.extract_bundle``), judges it against the queue
entry and the kit, and always writes ``desk_verdict.json`` (``desk_final`` true/false with reasons), a negative
or error result included. ``--bundle DIR --manifest-sha256 HEX --allow-unsigned`` judges an unsigned directory
for synthetic runs; that verdict says ``signed: false`` and never counts. Exit 0 desk-final with nothing held,
3 the verdict is not final or holds the next arm, 1 the desk refused or erred (verdict written), 4 the lock
is held or stale (nothing run, no verdict), 2 usage.

``publish`` commits the verdict record SSH-signed by the Air's key to ``refs/heads/cadence-desk-final/PLAN``
and pushes it; the controller reads it with ``desk_transport.read_verdict``. ``sample-plan`` prints the
seeded stratified hand-table draw for a queue at READY.

``build`` is the frozen table builder kept for the R1 adapter and by-hand use. It writes a verdict with
``desk_final: false`` ("no expected roster, no authentication"), so it can never satisfy line 9.
Exit 0 built with no named stop, 3 built and a named stop fired (page), 4 the
lock is held or stale (nothing run), 1 refused (a guard fired; nothing written), 2 usage.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import json
from pathlib import Path
import shutil
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from joulewise.cadence import desk, desk_final, desk_transport, kit as kitmod  # noqa: E402

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
    signed = args.bundle_ref is not None
    if signed == (args.bundle is not None):
        print("USAGE give --repo/--bundle-ref/--allowed-signers (signed) or --bundle with --manifest-sha256")
        return 2
    if signed and not (args.repo and args.allowed_signers):
        print("USAGE --bundle-ref needs --repo and --allowed-signers")
        return 2
    if not signed and not (args.manifest_sha256 and args.allow_unsigned):
        print("USAGE an unsigned --bundle directory needs --manifest-sha256 and --allow-unsigned (synthetic only)")
        return 2
    if args.history_prefix and not args.history_signers:
        print("USAGE --history-prefix needs --history-signers (the allowed-signers file naming the desk's key, "
              "cadence-desk; the verdict records are signed by it, not by the controller)")
        return 2
    if args.history_empty and not args.history_prefix:
        print("USAGE --history-empty needs --history-prefix")
        return 2
    if not signed and not args.queue:
        print("USAGE an unsigned --bundle directory needs --queue")
        return 2
    with ExitStack() as held:
        try:
            held.enter_context(desk.air_quiet_lock(f"cadence-desk-final:{args.plan_id}", Path(args.lock)))
        except desk.LockBusy as error:
            print(f"LOCK {error}")
            return 4
        except OSError as error:
            print(f"LOCK unavailable ({type(error).__name__}): {error.strerror}; create the --lock parent directory")
            return 4
        return _final_locked(args, signed)


def _final_locked(args, signed):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    transport, bundle, anchor, tmp, refusal = None, args.bundle, args.manifest_sha256, None, None
    refusal_code = "DESK_UNAUTHENTICATED"
    history, history_source = [], "none"
    queue = args.queue
    try:
        if signed:
            tmp, transport = desk_transport.extract_to_temp(args.repo, args.bundle_ref, out,
                                                            allowed_signers=args.allowed_signers,
                                                            plan_id=args.plan_id, principal=args.signer)
            bundle, anchor = tmp / "bundle", transport["manifest_sha256"]
            if queue is None:   # the queue bytes the span armed from, as the signed transition record names them
                queue = desk_transport.queue_from_transition(args.repo, transport["transition"], tmp / "QUEUE.json")
        if args.history:
            history, history_source = json.loads(Path(args.history).read_text()), "file"
        elif args.history_prefix:
            kit, _ = kitmod.load_kit(args.kit)
            # A prefix with no record at all cannot be told from one never fetched (gate 3, Mythos T5): it is refused
            # unless the operator states the desk has no records yet (--history-empty).
            history_repo = args.history_repo or args.repo
            listed = desk_transport.list_history_refs(history_repo, args.history_prefix, probe=True)
            if not listed and not args.history_empty:
                raise desk_transport.TransportRefusal(
                    f"no verdict record under {args.history_prefix} (were the verdict refs fetched?): give "
                    "--history-empty only when this desk has published none")
            history = desk_transport.history_from_records(
                history_repo, args.history_prefix,
                allowed_signers=args.history_signers, principal=args.history_principal,
                campaign_id=kit["campaign_id"], exclude_plan_id=args.plan_id,
                expected_ref=listed[0] if listed else None)
            history_source = "signed-records"

    except desk_final.DeniedContent as error:
        refusal, refusal_code = f"{type(error).__name__}: {error}", "DESK_DENIED_CONTENT"
    except (desk_transport.TransportRefusal, kitmod.KitError, OSError, ValueError) as error:
        refusal = f"{type(error).__name__}: {error}"
    try:
        verdict = desk_final.judge_span(
            plan_id=args.plan_id, bundle_dir=bundle if refusal is None else out / ".no-bundle",
            manifest_sha256=anchor if refusal is None else None, queue_path=queue or out / ".no-queue",
            kit_path=args.kit,
            out_dir=out, history=history, hand_table_path=args.hand_table, hand_sample=args.hand_sample,
            allow_mock=args.allow_mock, transport=transport, allow_unsigned=args.allow_unsigned and not signed,
            history_source=history_source, history_empty_asserted=args.history_empty,
            refusal=refusal, refusal_code=refusal_code)
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)
    for s in verdict["named_stops"]:
        print(f"STOP {s['code']} ({s['kind']}) {s['detail']}")
    for g in verdict["hand_gates"]:
        print(f"{g['status'].upper()} {g['gate']} ({g['ruling']})")
    print(f"desk_final {str(verdict['desk_final']).lower()}; next_arm_hold {str(verdict['next_arm_hold']).lower()}; "
          f"verdict {out / desk_final.VERDICT_NAME}")
    if verdict["error"] is not None:
        return 1
    return 0 if verdict["desk_final"] and not verdict["next_arm_hold"] else 3


def publish(args):
    try:
        sha = desk_transport.publish_verdict(args.repo, args.out, plan_id=args.plan_id, signing_key=args.signing_key,
                                             remote=args.remote, ref_prefix=args.ref_prefix, push=not args.no_push,
                                             principal=args.principal)
    except desk_transport.TransportRefusal as error:
        print(f"REFUSE {error}")
        return 1
    print(f"published {args.ref_prefix}{args.plan_id} at {sha}")
    return 0


def sample_plan(args):
    kit, sha = kitmod.load_kit(args.kit)
    queue = json.loads(Path(args.queue).read_text())
    from joulewise.cadence import queue as queuemod
    rows = []
    for span in queue["spans"]:
        if span["kit"]["sha256"] == sha:
            draw = desk_final.hand_sample(queue, queuemod.plan_id(span), kit, sha)
            rows.append({"plan_id": queuemod.plan_id(span), **draw})
    print(json.dumps({"law": desk_final.HAND_SAMPLE_LAW, "seed": desk_final.HAND_SAMPLE_SEED,
                      "rate": desk_final.HAND_SAMPLE_RATE, "kit_sha256": sha,
                      "note": "prospective: the hash part is exact; first_of_group uses the queue in place of the "
                              "history. At the desk a span is first of its group when no span of the group in the "
                              "signed history started before it", "spans": rows}, indent=1))
    return 0


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
    f.add_argument("--plan-id", required=True)
    f.add_argument("--repo", help="a clone holding the signed bundle ref")
    f.add_argument("--bundle-ref", help="the signed bundle commit, e.g. refs/remotes/origin/desk-bundles/<plan_id>")
    f.add_argument("--allowed-signers", help="ssh allowed-signers file naming the controller's key")
    f.add_argument("--signer", default=desk_transport.CONTROLLER_PRINCIPAL)
    f.add_argument("--bundle", help="synthetic only: an unsigned bundle directory (needs --allow-unsigned)")
    f.add_argument("--manifest-sha256", help="synthetic only: the unsigned bundle's manifest sha256")
    f.add_argument("--allow-unsigned", action="store_true", help="synthetic only (the verdict says signed: false)")
    f.add_argument("--queue", help="QUEUE.json (default with --bundle-ref: the queue the transition record names)")
    f.add_argument("--kit", required=True)
    f.add_argument("--out", required=True)
    h = f.add_mutually_exclusive_group()
    h.add_argument("--history", help="a JSON list of earlier desk summaries (verdict says history_source: file)")
    h.add_argument("--history-prefix", help="rebuild the history from signed verdict refs under this prefix")
    f.add_argument("--history-repo")
    f.add_argument("--history-signers", help="allowed-signers file naming the desk's key (cadence-desk); "
                                             "required with --history-prefix")
    f.add_argument("--history-empty", action="store_true",
                   help="assert this desk has published no history record yet (recorded as history_empty_asserted; "
                        "use only after fetching its full verdict prefix)")
    f.add_argument("--history-principal", default=desk_transport.DESK_PRINCIPAL,
                   help="the principal that signed the history records: cadence-desk (the Air or Actions desk), or "
                        "cadence-controller for the MBP desk's own records (RL-173 B; FORMAT section 6)")
    f.add_argument("--hand-table", help="the lead's hand table (hand_table.json), compared field by field")
    f.add_argument("--hand-sample", action="store_true", help="the lead selects this span for a hand table")
    f.add_argument("--allow-mock", action="store_true",
                   help="synthetic bundles only: accept a mock receipt (the verdict says mock: true)")
    f.add_argument("--lock", default=str(desk.QUIET_LOCK))
    u = sub.add_parser("publish", help="commit and push the signed verdict record (Air key)")
    u.add_argument("--plan-id", required=True); u.add_argument("--out", required=True)
    u.add_argument("--repo", required=True); u.add_argument("--signing-key", required=True)
    u.add_argument("--remote", default="origin"); u.add_argument("--ref-prefix", default=desk_transport.VERDICT_REF_PREFIX)
    u.add_argument("--no-push", action="store_true", help="update the local ref only (synthetic; the MBP desk)")
    u.add_argument("--principal", default=desk_transport.DESK_PRINCIPAL,
                   help="the signer's principal (cadence-desk; cadence-controller for the MBP desk, RL-173 B)")
    s = sub.add_parser("sample-plan", help="print the seeded stratified hand-table draw for a queue (prospective)")
    s.add_argument("--queue", required=True); s.add_argument("--kit", required=True)
    args = p.parse_args(argv)
    return {"final": final, "build": build, "publish": publish, "sample-plan": sample_plan}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
