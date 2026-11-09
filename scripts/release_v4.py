#!/usr/bin/env python3
"""ALIGN v4 release check: digests, independent recompute, blinded comparator. Standard library only.

Modelled on scripts/release_b5.py (DLE-1). It runs BEFORE anything is unsealed and prints a blinded verdict.

Stages:
- (a) digests. The release checkout is clean; the bars file hashes to RELEASE_BARS_SHA256; the engine run
  record names the pinned engine commit and the engine input; the engine's fill, verdict and threshold freeze
  hash to the record; every series- and window-level engine source is an input-census row, every census
  row re-hashes at the engine input root, and so does every {path, sha256} reference inside each raw-source
  manifest's member rows (episode, powermetrics, a referenced thermal journal, DC streams, any other); the
  engine's printed producer identity (loaded_scorer_sha256, raw_reducer_sha256 in the fill and the freeze)
  equals the identity computed from the PINNED engine tree under the release interpreter; the crosswalk
  agrees with both builds' rosters (structure only); the recompute program extracted at the pinned recompute
  commit hashes to RECOMPUTE_PROGRAM_SHA256.
- (b) recompute. The A25 two-stage contract: ``--stage calibration --freeze-out``, then the full run with
  ``--freeze-in``. After it, every member's raw sha256 in the recompute output must equal the engine's
  raw-source reference for the same member (both builds read the same bytes).
- (c) comparator. ``scripts/compare_v4_recompute.py`` with the pinned bars and the crosswalk.

Exit (precedence refused 2 > hold 1 > agree 0):
- 0 ``agree``: (a) verified, the recompute exited 0 twice, the comparator exited 0.
- 1 ``hold``: the comparator held (a family disagreed, an unexplained empty family, a manifest count out of
  range, an uncomputable sensitivity line).
- 2 ``refused``: any stage (a) failure, a recompute failure, a comparator refusal (unmapped leaf, eligible-m
  mismatch, malformed input), or a verdict that is not structure-only. A malformed input of any nested
  shape refuses with a fixed code (``release_input_malformed`` when no narrower code applies), never an
  uncaught exception.

``verdict.json`` (also stdout) carries only fixed codes, family names, counts and hex digests. Values stay in
``--restricted-out`` (mode 0700, must not exist): recompute.json, freeze.json, comparison.json, the stage
streams and refusal-location.txt. Unsealing is a separate step and needs Ed's OK.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

SCHEMA = "joulewise.v4_release_verdict.v1"
ROOT = Path(__file__).resolve().parents[1]
RELEASE_BARS = ROOT / "configs" / "analysis" / "v4" / "recompute_bars.json"
RELEASE_BARS_SHA256 = "17a268152f709fd075035598805b70cbe030361d74147c893351161e7b6fbcd4"
COMPARATOR = ROOT / "scripts" / "compare_v4_recompute.py"
RECOMPUTE_PROGRAM_PATH = "scripts/independent_recompute_v4.py"
# The recompute's own pin (tests/independent_recompute_v4/test_hygiene.py at 9f8a8749e, R23-R26 + R23h + R22-2/R24/R25 + r23j exports + R26 amendment).
RECOMPUTE_PROGRAM_SHA256 = "f01e7dbe46a106025b61ba9717306fec5a39617026b4d3955ddd7a1e1d84c55a"
ENGINE_RECORD_SCHEMA = "joulewise.v4_engine_run_record.v1"
# The builds this release check certifies (the commits the synthetic rehearsal agreed on). Any other
# commit refuses; re-pin only with a fresh AGREE rehearsal (RELEASE-RUNBOOK-v4.md section 5).
RELEASE_ENGINE_COMMIT = "de4a54db9d3c863805c1ba019732dc521e507cba"   # origin/engine-r23k
RELEASE_RECOMPUTE_COMMIT = "7b9d215ff833e727c98a1e6a5b2c4b2cac01c8f3"   # align/2026-11-08-v4-recompute-opus
HEX40, HEX64 = re.compile(r"[0-9a-f]{40}"), re.compile(r"[0-9a-f]{64}")
FLOAT_TOKEN = re.compile(r"(?<![A-Za-z0-9])(?:\d+\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)(?![A-Za-z0-9])")
CODE = re.compile(r"[a-z0-9_:]+")
EXIT = {"agree": 0, "hold": 1, "refused": 2}


class Refused(Exception):
    def __init__(self, code, location=None):
        super().__init__(code)
        self.code, self.location = code, location


def sha256_file(path):
    """Regular files only, opened non-blocking (a FIFO or device refuses instead of hanging)."""
    p = Path(path)
    if p.is_symlink() or not p.is_file():
        raise Refused("release_digest_differs_from_record", str(path))
    fd = os.open(p, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    h = hashlib.sha256()
    with os.fdopen(fd, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def strict_json(path, code):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise Refused(code, str(path))
            out[k] = v
        return out
    try:
        return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refused(code, str(path))))
    except Refused:
        raise
    except (OSError, ValueError):
        raise Refused(code, str(path))


def local(root, rel):
    """A relative reference under root; no absolute path, traversal or symbolic link on the way."""
    p = Path(rel)
    if p.is_absolute() or not p.parts or any(part in ("", ".", "..") for part in p.parts):
        raise Refused("release_digest_differs_from_record", str(rel))
    cursor = Path(root)
    for part in p.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise Refused("release_digest_differs_from_record", str(rel))
    return cursor


SERIES_SOURCE_KEYS = ("series_source", "selection_source")
WINDOW_SOURCE_KEYS = ("raw_source", "thermal_source", "residual_source", "terminal_result_source")
CROSSWALK_KEYS = ("window", "attempt_id", "ordinal", "engine_run_id", "recompute_window_id", "recompute_run_id",
                  "captured")


def is_ref(ref):
    return (isinstance(ref, dict) and isinstance(ref.get("path"), str) and isinstance(ref.get("sha256"), str)
            and HEX64.fullmatch(ref["sha256"]) is not None)


def member_refs(member, key=None):
    """Every {path, sha256} reference anywhere in a raw-source member row, with its top-level key."""
    out = []
    def walk(value, top):
        if isinstance(value, dict):
            if "path" in value or "sha256" in value:
                if not is_ref(value):
                    raise Refused("engine_census_malformed", "member reference")
                out.append((top, value))
                return
            for v in value.values():
                walk(v, top)
        elif isinstance(value, list):
            for v in value:
                walk(v, top)
    for k, v in member.items():
        walk(v, k)
    return out


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if r.returncode:
        raise Refused("git_unavailable", " ".join(args[:2]))
    return r.stdout


# ------------------------------------------------------------------------------------------------ stage (a)

def stage_digests(a, restricted):
    out = {"status": "verified"}
    # Release checkout: clean, so the programs that run are the committed ones.
    try:
        dirty = git(ROOT, "status", "--porcelain", "--untracked-files=all")
        commit = git(ROOT, "rev-parse", "HEAD").decode().strip()
    except Refused:
        raise Refused("release_checkout_unavailable")
    if dirty.strip():
        raise Refused("release_checkout_not_clean")
    out["release_checkout_commit"] = commit
    if sha256_file(RELEASE_BARS) != RELEASE_BARS_SHA256:
        raise Refused("release_bars_differ")
    for name in ("engine_commit", "recompute_commit"):
        if not HEX40.fullmatch(getattr(a, name) or ""):
            raise Refused("pinned_commit_invalid", name)
    if a.engine_commit != RELEASE_ENGINE_COMMIT:
        raise Refused("engine_commit_not_pinned")
    if a.recompute_commit != RELEASE_RECOMPUTE_COMMIT:
        raise Refused("recompute_commit_not_pinned")
    repo = a.programs_repo
    for name in ("engine_commit", "recompute_commit"):
        try:
            git(repo, "cat-file", "-e", getattr(a, name) + "^{commit}")
        except Refused:
            raise Refused("pinned_commit_unavailable", name)
    # Engine run record and outputs.
    record = strict_json(a.engine_record, "engine_record_invalid")
    need = ("schema", "engine_commit", "input_sha256", "fill_sha256", "verdict_sha256", "thresholds_sha256")
    if not isinstance(record, dict) or any(k not in record for k in need) or record["schema"] != ENGINE_RECORD_SCHEMA:
        raise Refused("engine_record_invalid")
    if record["engine_commit"] != a.engine_commit:
        raise Refused("release_digest_differs_from_record", "engine_commit")
    if sha256_file(a.engine_input) != record["input_sha256"]:
        raise Refused("release_digest_differs_from_record", "engine_input")
    eo = Path(a.engine_out)
    for name, key in (("fill.json", "fill_sha256"), ("verdict.json", "verdict_sha256"),
                      ("thresholds.json", "thresholds_sha256")):
        if sha256_file(eo / name) != record[key]:
            raise Refused("release_digest_differs_from_record", name)
    verdict = strict_json(eo / "verdict.json", "engine_output_unreadable")
    if not isinstance(verdict, dict) or verdict.get("status") == "refused":
        raise Refused("engine_run_refused")
    fill = strict_json(eo / "fill.json", "engine_output_unreadable")
    # Engine input census, and every file reference the engine's raw adapter reads (seat 2 F4): window- and
    # series-level sources must each be a census row; inside each raw-source manifest every member
    # reference ({path, sha256}: episode, powermetrics, a referenced thermal journal, DC streams, and any
    # other) is rehashed at the engine input root.
    root = Path(a.engine_input).resolve().parent
    rows = fill.get("input_census") if isinstance(fill, dict) else None
    if not isinstance(rows, list) or not rows:
        raise Refused("engine_census_missing")
    if not all(is_ref(row) and set(row) == {"path", "sha256"} for row in rows):
        raise Refused("engine_census_malformed")
    engine_doc = strict_json(a.engine_input, "engine_input_invalid")
    windows = engine_doc.get("windows") if isinstance(engine_doc, dict) else None
    if not isinstance(windows, list) or not windows or not all(isinstance(w, dict) for w in windows):
        raise Refused("engine_input_invalid")
    census = {(row["path"], row["sha256"]) for row in rows}
    declared = [engine_doc[k] for k in SERIES_SOURCE_KEYS if k in engine_doc]
    declared += [w[k] for w in windows for k in WINDOW_SOURCE_KEYS if k in w]
    if not all(is_ref(ref) for ref in declared):
        raise Refused("engine_input_invalid", "source reference")
    if any((ref["path"], ref["sha256"]) not in census for ref in declared):
        raise Refused("engine_census_incomplete")
    raw_paths = {w["raw_source"]["path"] for w in windows if "raw_source" in w}
    raw_refs = {}
    files = 0
    for row in rows:
        target = local(root, row["path"])
        if sha256_file(target) != row["sha256"]:
            raise Refused("release_digest_differs_from_record", row["path"])
        files += 1
        if row["path"] not in raw_paths:
            continue
        manifest = strict_json(target, "engine_census_unreadable")
        members = manifest.get("members") if isinstance(manifest, dict) else None
        if not isinstance(members, list) or not all(isinstance(m, dict) and isinstance(m.get("run_id"), str)
                                                     for m in members):
            raise Refused("engine_census_malformed", row["path"])
        for m in members:
            for key, ref in member_refs(m):
                if sha256_file(local(root, ref["path"])) != ref["sha256"]:
                    raise Refused("release_digest_differs_from_record", ref["path"])
                files += 1
                if key == "powermetrics":
                    raw_refs[(row["path"], m["run_id"])] = ref["sha256"]
    out["engine_files_rehashed"] = files
    # Producer identity: the loaded scorer and raw reducer the engine printed must be the pinned build's,
    # computed under CPython 3.13 (the engine's runtime calibration identity check pins it).
    check_python(a.python)
    ident = engine_identity(a.programs_repo, a.engine_commit, a.python, restricted)
    check_producer_identity(ident, fill, strict_json(eo / "thresholds.json", "engine_output_unreadable"))
    (Path(restricted) / "engine-identity.json").write_text(json.dumps(ident, sort_keys=True) + "\n")
    out["engine_producer_identity"] = "verified"
    # Crosswalk: structure-only agreement with both rosters.
    cross = strict_json(a.crosswalk, "crosswalk_invalid")
    members = cross.get("members") if isinstance(cross, dict) else None
    if not isinstance(members, list) or not members:
        raise Refused("crosswalk_invalid")
    if not all(isinstance(m, dict) and all(k in m for k in CROSSWALK_KEYS) for m in members):
        raise Refused("crosswalk_invalid")
    if not all(isinstance(w.get("attempt_id"), str) and isinstance(w.get("roster"), list)
               and all(isinstance(r, dict) and "run_id" in r and "ordinal" in r for r in w["roster"]) for w in windows):
        raise Refused("engine_input_invalid", "roster")
    eng_roster = {(w["attempt_id"], s["run_id"], s["ordinal"]) for w in windows for s in w["roster"]}
    if {(m["attempt_id"], m["engine_run_id"], m["ordinal"]) for m in members} != eng_roster:
        raise Refused("crosswalk_differs_from_roster", "engine")
    rec_roster = set()
    for m in members:
        rec_roster.add(m["recompute_window_id"])
    rec_rows = set()
    for wid in sorted(rec_roster):
        win = strict_json(local(a.recompute_root, f"windows/{wid}/window.json"), "recompute_input_invalid")
        wm = win.get("members") if isinstance(win, dict) else None
        if not isinstance(wm, list) or not all(isinstance(r, dict) and "run_id" in r and "ordinal" in r for r in wm):
            raise Refused("recompute_input_invalid", wid)
        rec_rows |= {(wid, r["run_id"], r["ordinal"]) for r in wm}
    if {(m["recompute_window_id"], m["recompute_run_id"], m["ordinal"]) for m in members} != rec_rows:
        raise Refused("crosswalk_differs_from_roster", "recompute")
    a.attempt_sources = {w["attempt_id"]: (w.get("raw_source") or {}).get("path") for w in windows}
    out["crosswalk_members"] = len(members)
    out["crosswalk_sha256"] = sha256_file(a.crosswalk)
    # Recompute program at the pinned commit.
    program = Path(restricted) / "program" / "independent_recompute_v4.py"
    program.parent.mkdir(mode=0o700)
    try:
        program.write_bytes(git(repo, "show", f"{a.recompute_commit}:{RECOMPUTE_PROGRAM_PATH}"))
    except Refused:
        raise Refused("pinned_commit_unavailable", "recompute_program")
    if sha256_file(program) != RECOMPUTE_PROGRAM_SHA256:
        raise Refused("recompute_program_differs")
    out["recompute_program_sha256"] = RECOMPUTE_PROGRAM_SHA256
    return out, program, raw_refs, members


PRODUCER_KEYS = ("loaded_scorer_sha256", "raw_reducer_sha256")
IDENTITY_SNIPPET = (
    "import json, sys; sys.path.insert(0, sys.argv[1]); "
    "from joulewise.align.v4_analysis.engine import scorer_identity; "
    "from joulewise.align.apple.reduce_sol import producer_sha256; "
    "print(json.dumps(dict(loaded_scorer_sha256=scorer_identity(), raw_reducer_sha256=producer_sha256(), "
    "python=sys.version.split()[0])))")


ENGINE_PYTHON = (3, 13)      # engine-r23j's runtime calibration identity check pins CPython 3.13.x


def check_python(python):
    """The release interpreter must be CPython 3.13.x: engine-r23j refuses calibration_identity_drift under any
    other version, and the loaded-scorer identity is version-specific."""
    r = subprocess.run([python, "-c", "import json, platform, sys; print(json.dumps([platform.python_implementation(), "
                                      "list(sys.version_info[:2])]))"], capture_output=True)
    try:
        impl, ver = json.loads(r.stdout) if r.returncode == 0 else (None, None)
    except ValueError:
        impl, ver = None, None
    if impl != "CPython" or tuple(ver or ()) != ENGINE_PYTHON:
        raise Refused("release_python_not_3_13")


def engine_identity(repo, commit, python, workdir):
    """The engine's producer identity (seat 1 F4 / seat 2 F3), computed from the PINNED engine tree under the
    release interpreter: its own scorer_identity() (loaded function code, which depends on the Python
    version) and its raw reducer digest. The engine is run as a subprocess; nothing here imports it."""
    tree = Path(workdir) / "engine-tree"
    tree.mkdir(mode=0o700)
    try:
        archive = git(repo, "archive", commit, "joulewise")
    except Refused:
        raise Refused("pinned_commit_unavailable", "engine_tree")
    r = subprocess.run(["tar", "-x", "-C", str(tree)], input=archive, capture_output=True)
    if r.returncode:
        raise Refused("pinned_commit_unavailable", "engine_tree")
    r = subprocess.run([python, "-B", "-I", "-c", IDENTITY_SNIPPET, str(tree)], capture_output=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    try:
        ident = json.loads(r.stdout) if r.returncode == 0 else None
    except ValueError:
        ident = None
    if not isinstance(ident, dict) or not all(HEX64.fullmatch(str(ident.get(k))) for k in PRODUCER_KEYS):
        raise Refused("engine_identity_unavailable")
    return ident


def check_producer_identity(ident, fill, freeze):
    """Refuse unless the engine's printed producer identity is the pinned build's."""
    for doc in (fill.get("threshold_freeze") if isinstance(fill, dict) else None, freeze):
        if not isinstance(doc, dict) or any(doc.get(k) != ident[k] for k in PRODUCER_KEYS):
            raise Refused("engine_producer_identity_differs")


# ------------------------------------------------------------------------------------------------ stages (b), (c)

def run(cmd, restricted, label):
    with open(Path(restricted) / f"{label}.stdout", "wb") as so, open(Path(restricted) / f"{label}.stderr", "wb") as se:
        return subprocess.run(cmd, stdout=so, stderr=se).returncode


def stage_recompute(a, program, restricted, raw_refs, members):
    r = Path(restricted)
    started = time.monotonic()
    py = a.python
    code1 = run([py, "-B", "-I", str(program), "--root", str(a.recompute_root), "--out", str(r / "calibration.json"),
                 "--stage", "calibration", "--freeze-out", str(r / "freeze.json")], r, "recompute-calibration")
    if code1 != 0:
        raise Refused("recompute_failed", "calibration")
    code2 = run([py, "-B", "-I", str(program), "--root", str(a.recompute_root), "--out", str(r / "recompute.json"),
                 "--freeze-in", str(r / "freeze.json"), "--workers", str(a.workers)], r, "recompute-full")
    if code2 != 0:
        raise Refused("recompute_failed", "full")
    status = {"exit": 0, "workers": a.workers, "wall_ms": int((time.monotonic() - started) * 1000)}
    rec = strict_json(r / "recompute.json", "recompute_output_unreadable")
    # Shared bytes: every captured member's raw digest equals the engine's raw-source reference.
    by_member = {}
    for m in members:
        if not m["captured"]:
            continue
        raw = (rec.get("reduction") or {}).get(m["recompute_run_id"], {}).get("raw_sha256")
        eng = raw_refs.get((a.attempt_sources.get(m["attempt_id"]), m["engine_run_id"]))
        by_member[(m["attempt_id"], m["ordinal"])] = (raw, eng)
    if any(raw is None or raw != eng for raw, eng in by_member.values()):
        raise Refused("builds_read_different_bytes")
    status["shared_raw_members"] = len(by_member)
    return status


def stage_compare(a, restricted):
    r = Path(restricted)
    started = time.monotonic()
    eo = Path(a.engine_out)
    code = run([a.python, "-B", "-I", str(COMPARATOR), "--fill", str(eo / "fill.json"), "--verdict",
                str(eo / "verdict.json"), "--recompute", str(r / "recompute.json"), "--crosswalk", str(a.crosswalk),
                "--bars", str(RELEASE_BARS), "--engine-identity", str(r / "engine-identity.json"),
                "--out", str(r / "comparison.json")], r, "comparator")
    status = {"exit": code, "wall_ms": int((time.monotonic() - started) * 1000), "bars_sha256": RELEASE_BARS_SHA256}
    try:
        public = json.loads((r / "comparator.stdout").read_text())
    except (OSError, ValueError):
        raise Refused("comparison_output_unreadable")
    if not isinstance(public, dict) or public.get("verdict") not in ("agree", "hold", "refused"):
        raise Refused("comparison_output_unreadable")
    if code not in (0, 1, 2) or EXIT[public["verdict"]] != code:
        raise Refused("comparison_output_unreadable")
    if public["verdict"] == "refused":
        reason = public.get("reason")
        status["refused"] = reason if isinstance(reason, str) and CODE.fullmatch(reason) else "other"
        status["unmapped_leaves"] = public.get("unmapped_leaves") if isinstance(public.get("unmapped_leaves"), int) else None
        if isinstance(public.get("families"), dict):
            status["families"] = _families(public["families"])
        return status
    fams = public.get("families")
    if not isinstance(fams, dict) or not fams:
        raise Refused("comparison_output_unreadable")
    status["families"] = _families(fams)
    if not any(f["verdict"] == "agree" for f in status["families"].values()):
        raise Refused("comparison_vacuous")
    status["summary"] = public.get("summary") if isinstance(public.get("summary"), str) else None
    status["unmapped_leaves"] = public.get("unmapped_leaves")
    return status


def _families(fams):
    out = {}
    for name, f in sorted(fams.items()):
        if not CODE.fullmatch(name) or not isinstance(f, dict):
            raise Refused("comparison_output_unreadable")
        v = f.get("verdict")
        if not isinstance(v, str) or not CODE.fullmatch(v):
            raise Refused("comparison_output_unreadable")
        out[name] = {"verdict": v, "pass": int(f.get("pass", 0)), "fail": int(f.get("fail", 0)),
                     "classification": f.get("classification") if f.get("classification") in
                     ("recomputed", "integrity_only", "exempt") else None}
    return out


# ------------------------------------------------------------------------------------------------ main

def precedence(*verdicts):
    """refused 2 > hold 1 > agree 0."""
    return max(verdicts, key=lambda v: EXIT[v])


def release(a):
    restricted = Path(a.restricted_out)
    verdict = {"schema": SCHEMA, "verdict": "agree", "reason": None, "stages": {}}
    if restricted.exists():
        raise Refused("restricted_out_exists")
    restricted.mkdir(mode=0o700, parents=False)
    try:
        digests, program, raw_refs, members = stage_digests(a, restricted)
        verdict["stages"]["digests"] = digests
        verdict["release_checkout"] = {"commit": digests.pop("release_checkout_commit")}
        verdict["stages"]["recompute"] = stage_recompute(a, program, restricted, raw_refs, members)
        cmp_status = stage_compare(a, restricted)
        verdict["stages"]["comparator"] = cmp_status
        word = {0: "agree", 1: "hold", 2: "refused"}[cmp_status["exit"]]
        verdict["verdict"] = precedence("agree", word)
        verdict["reason"] = {"agree": None, "hold": "comparator_disagreement",
                             "refused": "comparator_refused"}[word]
    except Refused as r:
        verdict["verdict"], verdict["reason"] = "refused", r.code
        (restricted / "refusal-location.txt").write_text(str(r.location or "") + "\n")
    except Exception as e:      # seat 2 F5: a malformed input never escapes as an uncaught exit 1 (= hold)
        verdict["verdict"], verdict["reason"] = "refused", "release_input_malformed"
        (restricted / "refusal-location.txt").write_text(type(e).__name__ + "\n")
    return verdict


def guard(verdict):
    text = json.dumps(verdict, sort_keys=True)
    if FLOAT_TOKEN.search(text):
        return {"schema": SCHEMA, "verdict": "refused", "reason": "verdict_not_structure_only"}
    return verdict


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--engine-input", required=True, help="engine input manifest (its sources resolve beside it)")
    ap.add_argument("--engine-out", required=True, help="engine output folder: fill.json, verdict.json, thresholds.json")
    ap.add_argument("--engine-record", required=True, help="engine run record (" + ENGINE_RECORD_SCHEMA + ")")
    ap.add_argument("--engine-commit", default=RELEASE_ENGINE_COMMIT)
    ap.add_argument("--recompute-root", required=True)
    ap.add_argument("--recompute-commit", default=RELEASE_RECOMPUTE_COMMIT)
    ap.add_argument("--crosswalk", required=True)
    ap.add_argument("--restricted-out", required=True)
    ap.add_argument("--programs-repo", default=str(ROOT), help="git repository holding the pinned commits")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--python", default=sys.executable)
    a = ap.parse_args(argv)
    try:
        verdict = release(a)
    except Refused as r:
        verdict = {"schema": SCHEMA, "verdict": "refused", "reason": r.code}
    except Exception:
        verdict = {"schema": SCHEMA, "verdict": "refused", "reason": "release_input_malformed"}
    verdict = guard(verdict)
    text = json.dumps(verdict, sort_keys=True)
    restricted = Path(a.restricted_out)
    if restricted.is_dir() and verdict.get("reason") != "restricted_out_exists":
        (restricted / "verdict.json").write_text(text + "\n")
    print(text)
    return EXIT[verdict["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
