#!/usr/bin/env python3
"""Validate a look manifest (RL-150 R4, RL-166); pin a draft's hashes. Opens no energy, power, meter or custody file.

    python3 -B scripts/cadence_look_manifest.py validate MANIFEST.json [--final]
        [--repo DIR [--kit KIT.json ...]] [--span-ledger LEDGER.json [--roster-out ROSTER.json]] [--looks LOOKS.json]
    python3 -B scripts/cadence_look_manifest.py pin MANIFEST.json --repo DIR [--write]
    python3 -B scripts/cadence_look_manifest.py pin-inputs MANIFEST.json --repo DIR --plan PLAN.json [--write]
    python3 -B scripts/cadence_look_manifest.py check-inputs MANIFEST.json --repo DIR
        [--run-state RUN_STATE.md] [--roster ROSTER.json]
    python3 -B scripts/cadence_look_manifest.py row --manifest MANIFEST.json --repo DIR
        (--roster ROSTER.json --verdicts VERDICTS.json | --stage1 STAGE1.json
         | --output | --error-type TYPE | --interrupted) [--write]

validate:
* structure and ruling invariants always; ``--final`` treats it as committed (no placeholder left);
* ``--repo``: the pinned hashes, no frozen kit path imports look code, look code never reads
  ``condition``; ``--kit`` names the leg kits to check (default: every kit under
  docs/process/cadence/kits/ in the repo); with ``--repo`` the look ledger LOOKS.json is checked too;
* ``--span-ledger``: resolve the spans the look reads and refuse unsealed, out-of-phase or
  not-desk-final spans, or a ledger that carries another manifest hash. The analyst seat runs this at
  the look before opening anything.

pin (draft manifests only): set the sha256 of every pinned file that exists in the repository, then
the manifest's row in LOOKS.json. Prints the changes; writes only with ``--write``. A committed manifest
is never re-pinned: it changes only by a ruling and a new manifest id (RL-166 section 2).

pin-inputs (RL-194; draft manifests only) writes the look's inputs file: for each roster span, the lines of the
span's offload manifest (SHA256SUMS) become its pins, in order. PLAN.json is a list of
``{span_id, runner_commit, close_item, check_item, offload_manifest, span_dir}``. No custody file is opened and no
digest is computed from one: the digests are the offload manifest's, and each file's size is read from its directory
entry. A span directory whose files are not exactly the offload manifest's, or that holds a symlink, refuses. Run
``pin --write`` afterwards to bind the new inputs file in the manifest.

check-inputs (RL-194 condition 2) checks the pin list a manifest names: its shape, that each span's pins rebuild the
offload manifest digest the span carries, and that each span's public RUN_STATE Check item names that digest
(``--run-state`` reads a file; the default is RUN_STATE.md on origin/main). ``--roster`` also requires the pinned
spans to be exactly the roster's. Prints how each Check item names its digest (in full or abbreviated).

row records an execution from its public report or the delivered RL-180 failure type.
Use --interrupted after confirming a reservation ended without a notice or completed report (RL-183).

Exit 0 valid (a draft prints its open placeholders), 1 refused (every problem printed), 2 usage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

def _fresh_bytecode_cache():
    """Mythos round-4 N4, Sol round-4 NEW-2: -B stops Python writing bytecode, not reading it. A fresh, empty
    pycache prefix (removed at exit) means no repository module can run from a stale __pycache__ entry beside its
    pinned source: each compiles from the bytes verify_pins hashes. Called below, before the first repository import, when
    this file runs as a program; manifest.cached_bytecode() confirms it before custody opens."""
    import atexit
    import shutil
    import tempfile
    sys.dont_write_bytecode = True
    prefix = tempfile.mkdtemp(prefix="jw-look-pyc-")
    sys.pycache_prefix = prefix
    atexit.register(shutil.rmtree, prefix, True)


if __name__ == "__main__":
    _fresh_bytecode_cache()
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise.cadence_looks import interim_release as release, manifest as lm  # noqa: E402


def validate(args):
    doc = lm.load_json(args.manifest)
    try:
        pending = lm.validate_manifest(doc, final=True if args.final else None)
        if args.repo:
            kits = args.kit or sorted(str(p) for p in (Path(args.repo) / "docs/process/cadence/kits").glob("*.json"))
            warnings = lm.check_repo(doc, args.repo, kits, final=True if args.final else None)
            looks = Path(args.looks) if args.looks else Path(args.repo) / lm.LOOK_LEDGER_PATH
            if looks.is_file():
                lm.validate_look_ledger(lm.load_json(looks), args.repo)
        if args.final and "supersedes" in doc:
            if not args.repo:
                raise lm.ManifestError(["validate --final needs --repo for a successor look"])
            lm.require_successor_ruling(doc, lm.load_json(looks))
        roster = None
        if args.span_ledger:
            roster = lm.resolve_roster(doc, lm.load_json(args.span_ledger), lm.sha256_file(args.manifest))
        elif args.roster_out:
            raise lm.ManifestError(["--roster-out needs --span-ledger"])
    except lm.ManifestError as error:
        for p in error.problems:
            print(f"REFUSE {p}")
        return 1
    print(f"ok {doc['look_id']} ({doc['status']}); open placeholders: {len(pending)}")
    for w in (warnings if args.repo else []):
        print(f"  WARN {w}")
    for path, qid in pending:
        print(f"  PENDING {qid} at {path}")
    if roster is not None:
        days = sorted({r['t0_local_date'] for r in roster if r['role'] == 'fit'})
        print(f"roster: {len(roster)} span(s); fit days {len(days)}: {', '.join(days)}")
        for r in roster:
            print(f"  {r['block_id']:<10} {r['span_id']:<16} {r['role']:<8} {r['t0_local_date']}")
        if args.roster_out:
            # The one roster shape (a JSON list), written by this command only; its sha256 goes into LOOKS.json's
            # roster_sha256 when stage 1 is committed (Mythos cold seat 8).
            text = json.dumps(roster, indent=1) + "\n"
            Path(args.roster_out).write_text(text, encoding="utf-8")
            print(f"wrote {args.roster_out} sha256={hashlib.sha256(text.encode('utf-8')).hexdigest()}")
    return 0


def _set_pins(node, repo, changes, path="$"):
    """Fill {path, sha256} references in place from the repository's files; record each change."""
    if isinstance(node, dict):
        if set(node) == {"path", "sha256"} and isinstance(node.get("path"), str):
            f = Path(repo) / node["path"]
            if lm._repo_path_ok(node["path"]) and f.is_file():
                sha = lm.sha256_file(f)
                if node["sha256"] != sha:
                    changes.append(f"{path}: {node['path']} {str(node['sha256'])[:12]} -> {sha[:12]}")
                    node["sha256"] = sha
            return
        for k, v in node.items():
            _set_pins(v, repo, changes, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _set_pins(v, repo, changes, f"{path}[{i}]")


def pin(args):
    repo, mpath = Path(args.repo), Path(args.manifest)
    doc = lm.load_json(mpath)
    if doc.get("status") != "draft":
        print("REFUSE a committed manifest is never re-pinned (RL-166 section 2)")
        return 1
    changes = []
    _set_pins(doc, repo, changes)
    text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    rel = mpath.resolve().relative_to(repo.resolve()).as_posix()
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    looks_path = repo / lm.LOOK_LEDGER_PATH
    looks = lm.load_json(looks_path) if looks_path.is_file() else {"schema": lm.LOOK_LEDGER_SCHEMA, "looks": []}
    row = next((r for r in looks["looks"] if r.get("look_id") == doc["look_id"]), None)
    if row is None:
        row = {"look_id": doc["look_id"], "manifest_path": rel, "sha256": "", "status": "draft"}
        looks["looks"].append(row)
        changes.append(f"LOOKS.json: new row {doc['look_id']}")
    elif row.get("status") != "draft":
        print(f"REFUSE LOOKS.json row {doc['look_id']} is {row.get('status')}, not draft")
        return 1
    if row["sha256"] != sha or row["manifest_path"] != rel:
        changes.append(f"LOOKS.json {doc['look_id']}: {row['sha256'][:12] or '-'} -> {sha[:12]}")
        row.update(manifest_path=rel, sha256=sha)
    for c in changes:
        print(c)
    if args.write:
        mpath.write_text(text, encoding="utf-8")
        looks_path.write_text(json.dumps(looks, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {rel} and {lm.LOOK_LEDGER_PATH}")
    else:
        print(f"{len(changes)} change(s); nothing written without --write")
    return 0


def row(args):
    """Record input commitments, the public report or the fixed failure type without opening custody."""
    repo = Path(args.repo).resolve()
    looks_path = repo / lm.LOOK_LEDGER_PATH
    looks = lm.validate_look_ledger(lm.load_json(looks_path))
    doc = lm.load_json(args.manifest)
    r = next((x for x in looks.get("looks") or [] if x.get("look_id") == doc.get("look_id")), None)
    problems = []
    if r is None:
        problems.append(f"LOOKS.json has no row for {doc.get('look_id')}")
    elif r.get("sha256") != lm.sha256_file(args.manifest):
        problems.append("LOOKS.json's row does not name this manifest's sha256")
    changes = {}
    if not problems and (args.output or args.error_type or args.interrupted):
        if r.get("status") != "stage1_committed" or lm.look_spent(repo, doc["look_id"], "HEAD"):
            problems.append("only an unspent stage-1 commitment can record an execution outcome")
        elif args.error_type:
            changes = {"status": "failed", "error_type": args.error_type}
        elif args.interrupted:
            public_root = r.get("public_root")
            if not public_root or os.path.lexists(repo / public_root / r["look_id"] / "PUBLIC.json"):
                problems.append("an interrupted look needs a registered public root with no completed report")
            else:
                changes = {"status": "interrupted", "error_type": "none_recorded"}
        else:
            try:
                changes = public_row(repo, r)
            except (OSError, ValueError, KeyError) as error:
                problems.append(str(error))
    elif not problems and args.stage1:
        stage1 = json.loads(Path(args.stage1).read_bytes())
        problems += lm.stage1_problems(repo, doc, stage1, lm.sha256_file(args.manifest), allow_draft=False)
        rec = stage1.get("code_sha256") or {}
        for field, key in (("roster_sha256", "input:roster_sha256"), ("verdicts_sha256", "input:rules_3_4_sha256")):
            if r.get(field) != rec.get(key):
                problems.append(f"the stage-1 file records {key} {rec.get(key)}, the row names {r.get(field)}")
        if r.get("status") != "committed":
            problems.append(f"the row is {r.get('status')!r}: a stage-1 hash is written on a committed row")
        changes = {"stage1_sha256": lm.sha256_file(args.stage1), "status": "stage1_committed"}
    elif not problems:
        if r.get("status") != "committed" or r.get("stage1_sha256") is not None:
            problems.append("the inputs are written on a committed row with no stage-1 hash")
        changes = {"roster_sha256": lm.sha256_file(args.roster), "verdicts_sha256": lm.sha256_file(args.verdicts)}
    if problems:
        for p_ in problems:
            print(f"REFUSE {p_}")
        return 1
    for k, v in changes.items():
        print(f"LOOKS.json {doc['look_id']}.{k}: {r.get(k)} -> {v}")
    r.update(changes)
    lm.validate_look_ledger(looks)
    if args.write:
        looks_path.write_text(json.dumps(looks, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {lm.LOOK_LEDGER_PATH} (commit and push it; the stages read the committed ledger)")
    else:
        print("nothing written without --write")
    return 0


def public_row(repo, row):
    """Read only the registered public report and verify its committed source bindings."""
    public_path = repo / row["public_root"] / row["look_id"] / "PUBLIC.json"
    if public_path.resolve() != public_path:
        raise ValueError("the registered public report must be a canonical path")
    raw = public_path.read_bytes()
    _, schema = lm.look_schemas(repo)
    public = release.read_public(raw, schema, look_id=row["look_id"])
    if (public["look_id"], public["manifest_sha256"], public["stage1_sha256"]) != (
            row["look_id"], row["sha256"], row["stage1_sha256"]):
        raise ValueError("the public report names different commitments from the look ledger")
    commit = public["commit"]
    ref, _ = lm.shared_ref(repo)
    if lm._git(repo, "merge-base", "--is-ancestor", commit, ref)[0]:
        raise ValueError("the public report's execution commit is not on the shared ref")
    rc, ledger_raw, _ = lm._git(repo, "show", f"{commit}:{lm.LOOK_LEDGER_PATH}")
    if rc or lm._look_row(json.loads(ledger_raw), row["look_id"]) != row:
        raise ValueError("the execution commit does not authenticate this stage-1 ledger row")
    return {"status": "run", "output_sha256": hashlib.sha256(raw).hexdigest(),
            "coefficients_sha256": public["coefficients_sha256"]}


def _span_sizes(directory):
    """{relative path: size} of a span directory from its entries alone: nothing is opened. A symlink refuses."""
    sizes, pending = {}, [""]
    while pending:
        prefix = pending.pop()
        with os.scandir(os.path.join(directory, prefix) if prefix else directory) as entries:
            for entry in entries:
                rel = f"{prefix}/{entry.name}" if prefix else entry.name
                if entry.is_symlink():
                    raise lm.custody_pins.PinRefusal(f"{rel}: a symlink in the span directory")
                if entry.is_dir(follow_symlinks=False):
                    pending.append(rel)
                elif entry.is_file(follow_symlinks=False):
                    sizes[rel] = entry.stat(follow_symlinks=False).st_size
                else:
                    raise lm.custody_pins.PinRefusal(f"{rel}: neither a regular file nor a directory")
    return sizes


def pin_inputs(args):
    """RL-194: the inputs file from each roster span's offload manifest. Hashes nothing in custody."""
    pins = lm.custody_pins
    repo = Path(args.repo)
    doc = lm.load_json(Path(args.manifest))
    if doc.get("status") != "draft":
        print("REFUSE a committed manifest's inputs are never re-pinned (RL-194 section 2: a changed roster redoes "
              "the pins before the manifest is final)")
        return 1
    plan = lm.load_json(Path(args.plan))
    keys = {"span_id", "runner_commit", "close_item", "check_item", "offload_manifest", "span_dir"}
    if not isinstance(plan, list) or not plan or not all(isinstance(row, dict) and set(row) == keys for row in plan):
        print(f"REFUSE the plan is a non-empty list of {{{', '.join(sorted(keys))}}}")
        return 1
    spans = []
    try:
        for row in plan:
            raw = Path(row["offload_manifest"]).read_bytes()
            span = pins.span_pins(row["span_id"], raw, _span_sizes(row["span_dir"]), runner_commit=row["runner_commit"],
                                  close_item=row["close_item"], check_item=row["check_item"])
            spans.append(span)
            print(f"{span['span_id']}: {len(span['files'])} files, {sum(f['size'] for f in span['files'])} bytes, "
                  f"offload manifest {span['offload_manifest_sha256']}, Check {span['check_item']}")
        out = {"schema": pins.SCHEMA, "spans": spans}
        problems = pins.pin_list_problems(out, complete=True)
    except (OSError, pins.PinRefusal) as error:
        print(f"REFUSE {error}")
        return 1
    if problems:
        for problem in problems:
            print(f"REFUSE {problem}")
        return 1
    text = json.dumps(out, indent=1) + "\n"
    target = repo / doc["inputs"]["pins"]["path"]
    print(f"inputs file sha256 {hashlib.sha256(text.encode('utf-8')).hexdigest()} "
          f"({len(spans)} spans, {sum(len(s['files']) for s in spans)} files)")
    if args.write:
        target.write_text(text, encoding="utf-8")
        print(f"wrote {doc['inputs']['pins']['path']}; now run: pin {args.manifest} --repo {args.repo} --write")
    else:
        print("(dry run; --write to apply)")
    return 0


def check_inputs(args):
    """RL-194 condition 2: the pin list's shape, its chain to each offload manifest and to each public Check item."""
    pins = lm.custody_pins
    try:
        doc = lm.load_json(Path(args.manifest))
        pin_list, sha = lm.input_pins(args.repo, doc, complete=True)
        if hashlib.sha256((Path(args.repo) / doc["inputs"]["pins"]["path"]).read_bytes()).hexdigest() != doc["inputs"]["pins"]["sha256"]:
            raise lm.ManifestError(["inputs.pins: the inputs file's sha256 differs from the manifest's pin"])
        text = (Path(args.run_state).read_text(encoding="utf-8") if args.run_state else lm.public_run_state(args.repo))
    except lm.ManifestError as error:
        for problem in error.problems:
            print(f"REFUSE {problem}")
        return 1
    problems = pins.check_chain_problems(pin_list, text)
    if args.roster:
        roster = sorted(span["span_id"] for span in lm.load_json(Path(args.roster)))
        if roster != sorted(span["span_id"] for span in pin_list["spans"]):
            problems.append("the pinned spans are not exactly the roster's spans")
    links = pins.chain_link(pin_list, text)
    for span in pin_list["spans"]:
        print(f"{span['span_id']}: {len(span['files'])} files, {sum(f['size'] for f in span['files'])} bytes; "
              f"pins rebuild offload manifest {span['offload_manifest_sha256']}; "
              f"Check {span['check_item']} names it: {links[span['span_id']]}")
    for problem in problems:
        print(f"REFUSE {problem}")
    if not problems:
        print(f"ok inputs file sha256 {sha}: {len(pin_list['spans'])} spans, "
              f"{sum(len(s['files']) for s in pin_list['spans'])} files, each chained to its Check item")
    return 1 if problems else 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    auth = sub.add_parser("authorize-freeze2", help="verify the public mainline freeze commitment")
    auth.add_argument("--repo", required=True)
    auth.add_argument("--look-id", required=True, choices=("lm-interim-01",))
    auth.add_argument("--expected-coefficients-sha256", required=True)
    port = sub.add_parser("port-files", help="list the verified dependency pins for a main-targeted port")
    port.add_argument("manifest")
    port.add_argument("--repo", required=True)
    v = sub.add_parser("validate")
    v.add_argument("manifest")
    v.add_argument("--final", action="store_true")
    v.add_argument("--repo")
    v.add_argument("--kit", action="append")
    v.add_argument("--span-ledger")
    v.add_argument("--looks")
    v.add_argument("--roster-out", help="write the resolved roster (needs --span-ledger)")
    w = sub.add_parser("pin")
    w.add_argument("manifest")
    w.add_argument("--repo", required=True)
    w.add_argument("--write", action="store_true")
    pi = sub.add_parser("pin-inputs", help="RL-194: write the inputs file from the roster's offload manifests")
    pi.add_argument("manifest")
    pi.add_argument("--repo", required=True)
    pi.add_argument("--plan", required=True)
    pi.add_argument("--write", action="store_true")
    ci = sub.add_parser("check-inputs", help="RL-194: check the pin list and its chain to the public Check items")
    ci.add_argument("manifest")
    ci.add_argument("--repo", required=True)
    ci.add_argument("--run-state")
    ci.add_argument("--roster")
    rw = sub.add_parser("row", help="write the LOOKS.json row's hashes from the files (Mythos r5 N3)")
    rw.add_argument("--manifest", required=True)
    rw.add_argument("--repo", required=True)
    g = rw.add_mutually_exclusive_group(required=True)
    g.add_argument("--stage1")
    g.add_argument("--roster")
    g.add_argument("--output", action="store_true", help="record the registered public report and coefficient commitment")
    g.add_argument("--error-type", choices=sorted(release.ERROR_TYPES), help="record the second line of the fixed failure notice")
    g.add_argument("--interrupted", action="store_true", help="attest a spent reservation with no notice or report")
    rw.add_argument("--verdicts")
    rw.add_argument("--write", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "authorize-freeze2":
        if not lm.SHA_RE.fullmatch(args.expected_coefficients_sha256):
            p.error("--expected-coefficients-sha256 must be 64 lowercase hex digits")
        try:
            _, evidence = lm.freeze2_authority(args.repo, expected_coefficients_sha256=args.expected_coefficients_sha256)
        except (OSError, ValueError, TypeError, KeyError):
            print("REFUSE freeze 2 public authority", file=sys.stderr)
            return 1
        sys.stdout.buffer.write(release.dump(evidence))
        return 0
    if args.cmd == "port-files":
        try:
            doc = lm.verify_pins(args.manifest, args.repo, allow_draft=True)
            lm.check_repo(doc, args.repo)
        except lm.ManifestError as error:
            for problem in error.problems:
                print(f"REFUSE {problem}", file=sys.stderr)
            return 1
        paths = {path: sha for _, path, sha in lm.code_refs(doc)}
        paths.update(lm.EVIDENCE)
        paths[lm.Q11_EVIDENCE["path"]] = lm.Q11_EVIDENCE["sha256"]
        sys.stdout.buffer.write(release.dump(paths))
        return 0
    if args.cmd == "validate":
        if args.kit and not args.repo:
            p.error("--kit needs --repo")
        return validate(args)
    if args.cmd == "pin-inputs":
        return pin_inputs(args)
    if args.cmd == "check-inputs":
        return check_inputs(args)
    if args.cmd == "row":
        if bool(args.roster) != bool(args.verdicts):
            p.error("--roster needs --verdicts")
        try:
            return row(args)
        except lm.ManifestError as error:
            for p_ in error.problems:
                print(f"REFUSE {p_}")
            return 1
    return pin(args)


if __name__ == "__main__":
    raise SystemExit(main())
