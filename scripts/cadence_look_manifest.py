#!/usr/bin/env python3
"""Validate a look manifest (RL-150 R4, RL-166); pin a draft's hashes. Opens no energy, power, meter or custody file.

    python3 -B scripts/cadence_look_manifest.py validate MANIFEST.json [--final]
        [--repo DIR [--kit KIT.json ...]] [--span-ledger LEDGER.json [--roster-out ROSTER.json]] [--looks LOOKS.json]
    python3 -B scripts/cadence_look_manifest.py pin MANIFEST.json --repo DIR [--write]
    python3 -B scripts/cadence_look_manifest.py assemble --manifest MANIFEST.json --stage1 STAGE1.json
        --fit FIT.json --step3 STEP3.json --analyst-seat NAME [--hold-cleared FLAG=RL-n ...] [--allow-draft]
        --out OUTPUT.json

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
        if args.output:
            out_problems = check_output(args.output, args.manifest, Path(args.repo) if args.repo else
                                        Path(args.manifest).resolve().parents[4])
            if out_problems:
                raise lm.ManifestError(out_problems)
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


HELD_FLAGS = ("onsets_before_116_s.to_research_lead", "meter_clock.to_research_lead", "tripwires.any")


def _flag(stage1, flag):
    if flag == "tripwires.any":
        return (stage1.get("tripwires") or {}).get("any") is True
    node = stage1.get(flag.split(".")[0])
    return isinstance(node, dict) and node.get("to_research_lead") is True


# The stages' exact code sets are defined in manifest.py (shared with the energy readers' pre-energy check). The
# two literals below are read, not imported, by cadence_look_run.stage1_code_set (round 4); a test holds them
# equal to manifest.py's until that reader takes manifest.STAGE1_CODE.
_SHARED_CODE = ("joulewise/__init__.py", "joulewise/cadence_looks/__init__.py", "joulewise/cadence_looks/manifest.py",
                "joulewise/cadence_looks/schema_check.py", "joulewise/axi_decode_config.py",
                "joulewise/idle_admission.py", "joulewise/schemas.py", "joulewise/validation.py")
STAGE1_CODE = _SHARED_CODE + ("joulewise/cadence_looks/fit_interim.py", "joulewise/cadence_looks/inclusion_34.py",
                              "scripts/cadence_look_run.py")
STAGE2_CODE, STEP3_CODE = lm.STAGE2_CODE, lm.STEP3_CODE
STAGE_ONLY_DEPENDENCIES = lm.STAGE_ONLY_DEPENDENCIES


def _schemas(repo):
    return lm.look_schemas(repo)


def _provenance(name, rec, doc, manifest_sha, pins, *, exact=None):
    return lm.provenance_problems(name, rec, manifest_sha, pins, exact=exact)


def _gate_problems(named):
    """Mythos round-4 N6: a record carries a ledger gate exactly when it was not made under --allow-draft."""
    out = []
    for name, rec in named:
        gate, draft = rec.get("ledger_gate"), rec.get("allow_draft") is True
        if draft and gate is not None:
            out.append(f"{name} was made under --allow-draft but records a ledger gate")
        if not draft and not isinstance(gate, dict):
            out.append(f"{name} was not made under --allow-draft but records no ledger gate")
    return out


def _coefficient_problems(fit):
    """Mythos round-3 N9: a channel's coefficient maps carry its own columns and nothing else."""
    problems = []
    channels = fit.get("channels") if isinstance(fit.get("channels"), dict) else {}
    for ch_name, ch in channels.items():
        if not isinstance(ch, dict):
            continue
        cols = set(ch.get("columns") or [])
        if set(ch.get("coefficients") or {}) != cols:
            problems.append(f"the fit's {ch_name} coefficients are not exactly its columns")
        for day, vec in (ch.get("fold_coefficients") or {}).items():
            if not set(vec or {}) <= cols:
                problems.append(f"the fit's {ch_name} fold {day} carries a key outside its columns")
        without = (ch.get("marked_sensitivity") or {}).get("coefficients_without")
        if isinstance(without, dict) and not set(without) <= cols:
            problems.append(f"the fit's {ch_name} coefficients_without carries a key outside its columns")
    return problems


def assemble(args):
    """The look's output file (RL-149 §2.6: the lead checks it against the output schema). Refuses before writing
    anything unless:
    * the pins verify (``manifest.verify_pins``) and, unless --allow-draft, the committed LOOKS.json names the
      stage-1 file's sha256 and its roster (``require_stage1_committed``);
    * the stage-1 file, the fit and step 3's file each pass their pinned schema, and so does the assembled output
      (Sol N3: nothing unknown, no per-leg energy, reaches the output);
    * all three name the stage-1 hash and were made under this manifest, and the code hashes they recorded are the
      pins exactly (Sol N2);
    * --allow-draft only on synthetic input, and no input made under --allow-draft without it (Mythos N2);
    * every held flag of stage 1 has its clearing ruling (RL-166 Q8; RL-166c §2 row 7)."""
    import datetime
    import re as _re
    from joulewise.cadence_looks import schema_check as sc
    repo = Path(args.manifest).resolve().parents[4]
    raw = Path(args.stage1).read_bytes()
    s1 = hashlib.sha256(raw).hexdigest()
    manifest_sha = lm.sha256_file(args.manifest)
    stage1 = json.loads(raw)
    fit, step3 = lm.load_json(args.fit), lm.load_json(args.step3)
    problems = [f"a repository module may have run from cached bytecode: {m}" for m in lm.cached_bytecode(repo)]
    try:
        doc = lm.verify_pins(args.manifest, repo, allow_draft=args.allow_draft, running=[Path(__file__).resolve()],
                             ledger_ref=args.ledger_ref)
        if not args.allow_draft:
            lm.require_stage1_committed(repo, doc["look_id"], s1, stage1_doc=stage1, ledger_ref=args.ledger_ref)
    except lm.ManifestError as error:
        problems += error.problems
        doc = lm.load_json(args.manifest)
    s1_schema, out_schema = _schemas(repo)
    problems += lm.stage1_problems(repo, doc, stage1, manifest_sha, allow_draft=args.allow_draft)   # as the readers
    for name, inst, schema in (("the fit", fit, sc.sub_schema(out_schema, "fit_output")),
                               ("step 3", step3, sc.sub_schema(out_schema, "step3_output"))):
        problems += [f"{name} does not pass its schema: {e}" for e in sc.errors(inst, schema)[:20]]
    problems += [f"{name} names stage-1 sha256 {str(rec.get('stage1_sha256'))[:12]}, not {s1[:12]}"
                 for name, rec in (("the fit", fit), ("step 3", step3)) if rec.get("stage1_sha256") != s1]
    pins = {path: sha for _, path, sha in lm.code_refs(doc)}
    stage2_set = (set(STAGE2_CODE) | {d["path"] for d in (doc.get("fit") or {}).get("dependencies") or []}) \
        - STAGE_ONLY_DEPENDENCIES
    problems += _provenance("the fit", fit, doc, manifest_sha, pins, exact=stage2_set)
    problems += _provenance("step 3", step3, doc, manifest_sha, pins, exact=set(STEP3_CODE))
    # Sol round-3 NEW-4: step 3 applied the manifest's drift threshold, whichever the research lead rules
    drift = next((d for d in doc.get("decisions") or [] if d.get("id") == "drift_tripwire"), {})
    applied = (step3.get("tripwire") or {}).get("threshold_applied")
    if applied != drift.get("threshold"):
        problems.append(f"step 3 applied the drift threshold {applied}, not the manifest's {drift.get('threshold')}")
    problems += _coefficient_problems(fit)
    drafted = [name for name, rec in (("stage 1", stage1), ("the fit", fit), ("step 3", step3))
               if rec.get("allow_draft") is True]
    problems += _gate_problems((("stage 1", stage1), ("the fit", fit), ("step 3", step3)))
    if args.allow_draft:
        if stage1.get("synthetic") is not True:
            problems.append("--allow-draft on a stage-1 file that is not synthetic (Mythos N2)")
    elif drafted:
        problems.append(f"{', '.join(drafted)} made under --allow-draft; a real output cannot use it (Mythos N2)")
    raised = [f for f in HELD_FLAGS if _flag(stage1, f)]
    cleared = dict(c.split("=", 1) for c in (args.hold_cleared or []) if "=" in c)
    for f in raised:
        if not _re.fullmatch(r"RL-\d+[a-z]?(?: .*)?", cleared.get(f, "")):
            problems.append(f"stage 1 shows {f} true: stage 2 was held; name the clearing ruling with --hold-cleared {f}=RL-n")
    for f in sorted(set(cleared) - set(raised)):
        problems.append(f"--hold-cleared {f}: stage 1 does not show that flag true")
    if problems:
        for p in problems:
            print(f"REFUSE {p}")
        return 1
    q = (fit.get("qualified_interim_half") or {}).get("verdict")
    code = dict(fit.get("code_sha256") or {})
    code.update({k: v for k, v in (step3.get("code_sha256") or {}).items()})
    code["scripts/cadence_look_manifest.py"] = pins["scripts/cadence_look_manifest.py"]
    gate = None if args.allow_draft else lm.ledger_gate(repo, args.ledger_ref)
    # RL-158 Q5: legs whose realized prompt count is more than 5 % from nominal, from stage 1's own fields
    realized = [{"leg_key": leg["leg_key"], "nominal": leg["cell_prompt_tokens"], "realized": leg["prefill_tokens"]}
                for leg in stage1.get("legs") or []
                if isinstance(leg.get("prefill_tokens"), int) and isinstance(leg.get("cell_prompt_tokens"), int)
                and abs(leg["prefill_tokens"] - leg["cell_prompt_tokens"]) > 0.05 * leg["cell_prompt_tokens"]]
    out = {"schema": "joulewise.cadence_look_output.interim.v1", "look_id": "lm-interim-01",
           "manifest_sha256": manifest_sha, "stage1_sha256": s1, "fit": fit, "step3": step3,
           "allow_draft": bool(args.allow_draft), "synthetic": stage1.get("synthetic") is True,
           "realized_prompt_tokens": realized, "soak_retries": stage1.get("soak_retries"),   # RL-172a
           "decisions": {"drift_tripwire": step3["tripwire"]["decision"], "qualified_interim_half": q,
                         "extension_rule": "none written; any extension needs a ruling"},
           "disclosure": {"date": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                          "code_sha256": code, "ledger_gate": gate, "stage1_sha256": s1,
                          "analyst_seat": args.analyst_seat,
                          "numpy_version": fit.get("numpy_version", ""),
                          "holds_cleared": [{"flag": f, "cleared_by": cleared[f]} for f in raised],
                          "statement": "An energy read on conditionless campaign legs only, by frozen code at the "
                                       "interim look (RL-149 section 2.6; RL-150 R6): none comes from a run with a "
                                       "sabotage instruction, a slot or a v4 member."}}
    out_errors = sc.errors(out, out_schema)
    if out_errors:
        for e in out_errors[:20]:
            print(f"REFUSE the assembled output does not pass its schema: {e}")
        return 1
    unpinned = lm.unpinned_loaded_modules(doc, repo)                    # Mythos N6
    if unpinned:
        print("REFUSE loaded repository modules the manifest does not pin: " + ", ".join(unpinned[:6]))
        return 1
    text = json.dumps(out, indent=1, allow_nan=False) + "\n"
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"wrote {args.out} sha256={hashlib.sha256(text.encode('utf-8')).hexdigest()}")
    return 0


def check_output(path, manifest_path, repo):
    """``validate --output``: an assembled output passes its pinned schema, names this manifest, and was not made
    under --allow-draft unless it is synthetic (Mythos N2). Returns problems."""
    from joulewise.cadence_looks import schema_check as sc
    out = lm.load_json(path)
    _, out_schema = _schemas(repo)
    problems = [f"output: {e}" for e in sc.errors(out, out_schema)[:20]]
    problems += [f"output: {p}" for p in _coefficient_problems(out.get("fit") or {})]
    problems += [f"output: {p}" for p in _gate_problems((("the fit", out.get("fit") or {}),
                                                         ("step 3", out.get("step3") or {})))]
    if out.get("allow_draft") is not True and not isinstance((out.get("disclosure") or {}).get("ledger_gate"), dict):
        problems.append("output: assembled without --allow-draft but records no ledger gate")
    if out.get("manifest_sha256") != lm.sha256_file(manifest_path):
        problems.append("output: made under another manifest")
    if out.get("allow_draft") is True and out.get("synthetic") is not True:
        problems.append("output: made under --allow-draft on input that is not synthetic")
    return problems


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
    v.add_argument("--output", help="also check an assembled output against the pinned schema and the draft rule")
    w = sub.add_parser("pin")
    w.add_argument("manifest")
    w.add_argument("--repo", required=True)
    w.add_argument("--write", action="store_true")
    a = sub.add_parser("assemble")
    for k in ("--manifest", "--stage1", "--fit", "--step3", "--analyst-seat", "--out"):
        a.add_argument(k, required=True)
    a.add_argument("--hold-cleared", action="append", metavar="FLAG=RL-n")
    a.add_argument("--allow-draft", action="store_true", help="synthetic runs only: a draft manifest, no LOOKS.json stage-1 row")
    a.add_argument("--ledger-ref", help="the remote-tracking branch the committed LOOKS.json must be on (default: the "
                                        "upstream, else origin/main; never HEAD or a local ref: manifest.shared_ref)")
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
