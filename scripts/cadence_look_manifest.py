#!/usr/bin/env python3
"""Validate a look manifest (RL-150 R4, RL-166); pin a draft's hashes. Opens no energy, power, meter or custody file.

    python3 -B scripts/cadence_look_manifest.py validate MANIFEST.json [--final]
        [--repo DIR [--kit KIT.json ...]] [--span-ledger LEDGER.json] [--looks LOOKS.json]
    python3 -B scripts/cadence_look_manifest.py pin MANIFEST.json --repo DIR [--write]
    python3 -B scripts/cadence_look_manifest.py assemble --manifest MANIFEST.json --stage1 STAGE1.json
        --fit FIT.json --step3 STEP3.json --analyst-seat NAME [--hp-table HP.json] --out OUTPUT.json

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

assemble: the look's output file (lm-interim-01.output.schema.json): level O from the stage-2 CLI, step 3's file
from step3_roster.py, the High Power table if it ran, the decisions read from those, and the disclosure. Refuses
unless the fit and step 3 files name the stage-1 file's sha256. It reads no energy: its inputs are derived files.

Exit 0 valid (a draft prints its open placeholders), 1 refused (every problem printed), 2 usage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise.cadence_looks import manifest as lm  # noqa: E402


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
        roster = None
        if args.span_ledger:
            roster = lm.resolve_roster(doc, lm.load_json(args.span_ledger), lm.sha256_file(args.manifest))
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


def assemble(args):
    import datetime
    raw = Path(args.stage1).read_bytes()
    s1 = hashlib.sha256(raw).hexdigest()
    fit, step3 = lm.load_json(args.fit), lm.load_json(args.step3)
    problems = [f"{name} names stage-1 sha256 {doc.get('stage1_sha256')}, not {s1}"
                for name, doc in (("fit", fit), ("step3", step3)) if doc.get("stage1_sha256") != s1]
    if problems:
        for p in problems:
            print(f"REFUSE {p}")
        return 1
    hp = lm.load_json(args.hp_table) if args.hp_table else None
    q = (fit.get("qualified_interim_half") or {}).get("verdict")
    code = dict(fit.get("code_sha256") or {})
    for rel in ("joulewise/cadence_looks/step3_roster.py", "joulewise/cadence_looks/inclusion_34.py",
                "joulewise/cadence_looks/step3_energy_ratios.py"):
        f = Path(args.manifest).resolve().parents[4] / rel
        if f.is_file():
            code[rel] = lm.sha256_file(f)
    out = {"schema": "joulewise.cadence_look_output.interim.v1", "look_id": "lm-interim-01",
           "manifest_sha256": lm.sha256_file(args.manifest), "stage1_sha256": s1, "fit": fit, "step3": step3,
           "high_power_table": hp,
           "decisions": {"drift_tripwire": step3["tripwire"]["decision"], "qualified_interim_half": q,
                         "hp01_table": "in this output" if hp is not None else "later, as its own disclosed read (RL-166 Q9)",
                         "extension_rule": "none written; any extension needs a ruling"},
           "disclosure": {"date": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                          "code_sha256": code, "stage1_sha256": s1, "analyst_seat": args.analyst_seat,
                          "numpy_version": fit.get("numpy_version", ""),
                          "statement": "An energy read on conditionless campaign legs only, by frozen code at the "
                                       "interim look (RL-149 section 2.6; RL-150 R6): none comes from a run with a "
                                       "sabotage instruction, a slot or a v4 member."}}
    text = json.dumps(out, indent=1, allow_nan=False) + "\n"
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"wrote {args.out} sha256={hashlib.sha256(text.encode('utf-8')).hexdigest()}")
    return 0


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
    w = sub.add_parser("pin")
    w.add_argument("manifest")
    w.add_argument("--repo", required=True)
    w.add_argument("--write", action="store_true")
    a = sub.add_parser("assemble")
    for k in ("--manifest", "--stage1", "--fit", "--step3", "--analyst-seat", "--out"):
        a.add_argument(k, required=True)
    a.add_argument("--hp-table")
    args = p.parse_args(argv)
    if args.cmd == "validate":
        if args.kit and not args.repo:
            p.error("--kit needs --repo")
        return validate(args)
    if args.cmd == "assemble":
        return assemble(args)
    return pin(args)


if __name__ == "__main__":
    raise SystemExit(main())
