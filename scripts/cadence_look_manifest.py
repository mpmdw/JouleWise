#!/usr/bin/env python3
"""Validate a look manifest (RL-150 R4, RL-166); pin a draft's hashes. Opens no energy, power, meter or custody file.

    python3 -B scripts/cadence_look_manifest.py validate MANIFEST.json [--final]
        [--repo DIR [--kit KIT.json ...]] [--span-ledger LEDGER.json [--roster-out ROSTER.json]] [--looks LOOKS.json]
    python3 -B scripts/cadence_look_manifest.py pin MANIFEST.json --repo DIR [--write]
    python3 -B scripts/cadence_look_manifest.py row --manifest MANIFEST.json --repo DIR
        (--roster ROSTER.json --verdicts VERDICTS.json | --stage1 STAGE1.json) [--write]

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

row can also record the registered PUBLIC.json or the fixed RL-180 failure type.

Exit 0 valid (a draft prints its open placeholders), 1 refused (every problem printed), 2 usage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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
    if not problems and (args.output or args.error_type):
        if r.get("status") != "stage1_committed" or lm.look_spent(repo, doc["look_id"], "HEAD"):
            problems.append("only an unspent stage-1 commitment can record an execution outcome")
        elif args.error_type:
            changes = {"status": "failed", "error_type": args.error_type}
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
    public = release.read_public(raw, schema)
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


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
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
    rw = sub.add_parser("row", help="write the LOOKS.json row's hashes from the files (Mythos r5 N3)")
    rw.add_argument("--manifest", required=True)
    rw.add_argument("--repo", required=True)
    g = rw.add_mutually_exclusive_group(required=True)
    g.add_argument("--stage1")
    g.add_argument("--roster")
    g.add_argument("--output", action="store_true", help="record the registered public report and coefficient commitment")
    g.add_argument("--error-type", choices=sorted(release.ERROR_TYPES), help="record the second line of the fixed failure notice")
    rw.add_argument("--verdicts")
    rw.add_argument("--write", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "validate":
        if args.kit and not args.repo:
            p.error("--kit needs --repo")
        return validate(args)
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
