#!/usr/bin/env python3
"""BYTES stage 1 on real data: census, analysis manifest, and the pre-commit run.

Registration `docs/registrations/bytes_pack_v1.md` section 11 fixes the order this
program follows and adds nothing to:

1. ``census``: structure only. Every counting session's export is present, carries
   the ``bytes`` group's withheld locator, has no clock column, and shows no
   held-out configuration row (ruling item 1: held-out rows never enter the
   analysis export before the stage-1 hash is recorded). No energy column is read
   and no withheld store is opened.
2. ``manifest``: the analysis manifest is the registered manifest
   (``configs/bytes/bytes_manifest.json``, section 4) plus one ``sessions`` row per
   counting session (id, archive, pass id from the export sidecar, test 7 false).
3. ``run``: in the desk order of ``tests/test_bytes_agreement.py`` ``run_both``:
   the blinded analysis and twin (rails only), the registered comparer on them,
   stage 1 without released keys on both sides (both must refuse), the stage-1
   key release (fit set plus ``neg8_reference``, by ``scripts/b6_release_subset.py``),
   then stage 1 (``--stage fit`` / twin ``--stage 1``) and the comparer again.
   It stops before the release if the blinded agreement has a difference above
   section 12's bar or a refusal mismatch: a difference is attributed and ruled
   first (section 12).

The output of ``run`` is ``a-fit/predictions.json`` with ``predictions.sha256``,
the commitment of section 11. Committing it in git, before any held-out row enters
the export, is the operator's step (``docs/run_reports/2026-11-07-bytes-stage1-plan.md``).
Nothing here reads a held-out key, a withheld store or a stage-2 output.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise import bytes_analysis as ba  # noqa: E402
from joulewise.b6 import blinding  # noqa: E402

GROUP = "bytes"
# Registration section 13 / section 21 item 2: the agreeing estimator digest both passes bind.
REGISTERED_ESTIMATOR_SHA256 = "18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71"
PACKS = tuple(f"bytes-s{n}-p{p}" for p in (1, 2) for n in range(1, 7))
PACK_RE = re.compile(r"bytes-s([1-6])-p([12])")
# Section 11 item 2 (timing closure): "no run_start_utc or any other clock" before the stage-1
# commit. A column is clock-like when its name ends in _utc, or one of its underscore-separated
# words says when something happened. Durations (dur_*_s, ttft_s) are not clocks, and the
# exporter's bound_E_clock_anchor_shift_bound_j is an energy bound, so "clock" is a word only
# when it stands alone.
CLOCK_WORDS = frozenset({"utc", "timestamp", "datetime", "date", "epoch", "wall", "time", "ts",
                         "started", "ended", "start", "end", "finished", "created"})


def clock_columns(header):
    found = []
    for name in header:
        lowered = str(name).lower()
        words = set(re.split(r"[^a-z0-9]+", lowered))
        if lowered.endswith("_utc") or lowered == "clock" or words & CLOCK_WORDS:
            found.append(name)
    return found

REFERENCE_ROLES = ("corpus", "start", "midpoint", "end")


class Stage1Error(Exception):
    pass


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _visible(root, pattern):
    """Paths under root matching pattern, never inside a ``withheld`` directory (the registered
    layout is withheld/<pack_id>/<session_id>.runs.csv). Listing only; nothing is opened here."""
    for path in root.rglob(pattern):
        if "withheld" not in path.relative_to(root).parts[:-1] and not path.name.endswith(".withheld.csv"):
            yield path


def _sessions_in(export_dirs):
    """(session_id, csv path, sidecar path) for every exported session under the given roots."""
    found = {}
    for root in export_dirs:
        root = Path(root)
        if not root.is_dir():
            raise Stage1Error(f"export directory missing: {root}")
        names = {p.name.removesuffix(".runs.csv") for p in _visible(root, "*.runs.csv")} | {
            p.name.removesuffix(".session.json") for p in _visible(root, "*.session.json")}
        for session_id in sorted(names):
            sidecars = list(_visible(root, session_id + ".session.json"))
            tables = list(_visible(root, session_id + ".runs.csv"))
            if session_id in found or len(sidecars) > 1 or len(tables) > 1:
                raise Stage1Error(f"session exported more than once: {session_id}")
            found[session_id] = (tables[0] if tables else None, sidecars[0] if sidecars else None)
    return found


def _config_is_fit(record):
    """The row's configuration is a fit configuration: its model_name is a fit model and the
    config_key names that same model (key form ``<model>|<workload>|<tokens>``), so a held-out
    configuration key under a fit model_name is seen (review of #701, F1)."""
    model = record.get("model_name")
    key = record.get("config_key")
    return model in blinding.FIT_MODELS and isinstance(key, str) and key.split("|", 1)[0] == model


def census(export_dirs, *, expect_packs=PACKS):
    """Structure-only check of the stage-1 export; returns (record, reasons).

    A missing withheld store is a recorded flag (``record["warnings"]``), never a reason
    (registration section 11 item 4)."""
    reasons, warnings, sessions = [], [], []
    found = _sessions_in(export_dirs)
    packs_seen = {}
    for session_id, (table, sidecar) in sorted(found.items()):
        row = {"session_id": session_id, "csv": str(table) if table else None,
               "sidecar": str(sidecar) if sidecar else None}
        sessions.append(row)
        if table is None or sidecar is None:
            reasons.append(f"{session_id}: export needs both <session>.runs.csv and <session>.session.json")
            continue
        side = json.loads(sidecar.read_text(encoding="utf-8"))
        pack_id = side.get("pack_id")
        block = side.get("blinding") or {}
        withheld = block.get("withheld") or {}
        match = PACK_RE.fullmatch(pack_id or "")
        row.update(pack_id=pack_id, pass_id=block.get("pass_id"), group=block.get("group"),
                   counting=side.get("counting"), verdict=side.get("verdict"),
                   withheld_row_count=withheld.get("row_count"))
        if match is None:
            reasons.append(f"{session_id}: pack_id {pack_id!r} is not a registered BYTES sub-pack")
        elif block.get("pass_id") != int(match.group(2)):
            reasons.append(f"{session_id}: sidecar pass_id {block.get('pass_id')!r} disagrees with {pack_id}")
        if block.get("group") != GROUP or block.get("applied") is not True:
            reasons.append(f"{session_id}: export is not blinded in group {GROUP!r}")
        if side.get("non_claim"):
            reasons.append(f"{session_id}: export is non-claim")
        if side.get("counting") is not True:
            reasons.append(f"{session_id}: sidecar does not mark the session counting")
        locator = withheld.get("path")
        if not isinstance(locator, str) or not locator or not isinstance(withheld.get("row_count"), int):
            reasons.append(f"{session_id}: sidecar lacks the withheld store locator and row count")
            row["withheld_store_present"] = False
        else:
            # Existence only: the store holds held-out rows and is never opened here.
            row["withheld_store_present"] = (sidecar.parent / locator).is_file()
            if not row["withheld_store_present"]:
                warnings.append(f"bytes.withheld_missing: {session_id}: withheld store missing at its locator "
                                "(section 11 item 4: a flag, not a refusal; explain it before the commit)")
        if pack_id in packs_seen:
            reasons.append(f"{pack_id}: more than one session ({packs_seen[pack_id]}, {session_id})")
        packs_seen[pack_id] = session_id
        with table.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            header = reader.fieldnames or []
            clocks = clock_columns(header)
            if clocks:
                reasons.append(f"{session_id}: clock column(s) {clocks} visible before the stage-1 commit")
            roles, models, heldout = {}, set(), []
            # Identity columns only; no energy, power or duration field is read.
            for record in reader:
                role = record.get("role")
                roles[role] = roles.get(role, 0) + 1
                if role in REFERENCE_ROLES:
                    if record.get("config_key") != blinding.REFERENCE_KEY:
                        heldout.append(record.get("run_id"))
                    continue
                models.add(record.get("model_name"))
                if not _config_is_fit(record):
                    heldout.append(record.get("run_id"))
        row.update(rows_by_role=dict(sorted(roles.items(), key=lambda kv: str(kv[0]))),
                   visible_science_models=sorted(m for m in models if m))
        if heldout:
            reasons.append(f"{session_id}: {len(heldout)} held-out row(s) visible in the export "
                           "(registration section 11 item 1); stop and do not run stage 1")
    missing = sorted(set(expect_packs) - set(packs_seen))
    extra = sorted(set(packs_seen) - set(expect_packs))
    if missing:
        reasons.append("no session for: " + ", ".join(missing))
    if extra:
        reasons.append("unexpected pack(s): " + ", ".join(str(p) for p in extra))
    record = {"schema": "joulewise.bytes_stage1_census.v1", "verdict": "OK" if not reasons else "REFUSED",
              "reasons": reasons, "warnings": warnings, "sessions": sessions}
    return record, reasons


def build_manifest(sessions, *, registered=ROOT / "configs/bytes/bytes_manifest.json"):
    """Registered manifest plus one sessions row per (session_id, archive, export_dir)."""
    raw = Path(registered).read_bytes()
    if hashlib.sha256(raw).hexdigest() != ba.REGISTERED_MANIFEST_SHA256:
        raise Stage1Error("registered manifest digest differs from registration section 4")
    manifest = json.loads(raw)
    if "sessions" in manifest or manifest.get("synthetic"):
        raise Stage1Error("registered manifest unexpectedly carries sessions or a synthetic flag")
    rows = []
    for session_id, archive, export_dir in sessions:
        archive = Path(archive).resolve()
        found = _sessions_in([export_dir])
        if session_id not in found or found[session_id][1] is None:
            raise Stage1Error(f"{session_id}: no export sidecar under {export_dir}")
        side = json.loads(found[session_id][1].read_text(encoding="utf-8"))
        acceptance = ba.read_json(archive / "derived/b6-acceptance.json")
        if acceptance.get("session_id") != session_id or acceptance.get("pack_id") != side.get("pack_id"):
            raise Stage1Error(f"{session_id}: archive acceptance names {acceptance.get('session_id')!r}/"
                              f"{acceptance.get('pack_id')!r}, export names {session_id!r}/{side.get('pack_id')!r}")
        pass_id = (side.get("blinding") or {}).get("pass_id")
        match = PACK_RE.fullmatch(side.get("pack_id") or "")
        if match is None or pass_id != int(match.group(2)):
            raise Stage1Error(f"{session_id}: pass identity unresolved")
        rows.append({"session_id": session_id, "archive": str(archive), "pass_id": pass_id,
                     "test7_passed": False, "pack_id": side["pack_id"]})
    rows.sort(key=lambda r: (r["pass_id"], int(PACK_RE.fullmatch(r["pack_id"]).group(1))))
    if sorted(r["pack_id"] for r in rows) != sorted(PACKS):
        raise Stage1Error("manifest needs exactly one session for each of the twelve sub-packs")
    manifest["sessions"] = rows
    ba.validate_manifest(json.loads(json.dumps(manifest)))
    return manifest


def _git_state():
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"],
                                             cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip())
    except (OSError, subprocess.CalledProcessError):
        head, dirty = None, None
    return head, dirty


def _release_fit(pack_records_root, keys, out):
    from scripts.b6_release_subset import release
    return release(pack_records_root, GROUP, ROOT / "configs/b6/packs", ROOT, keys, "fit", out)


def _counts(recorder):
    above = [{k: row[k] for k in ("stage", "group", "key", "status") if k in row} for row in recorder.above()]
    return {**recorder.counts(), "above_bar_fields": above}


def run_stage1(manifest_path, export_dirs, pack_records_root, out_root, *, python=sys.executable,
               release_fn=_release_fit, require_registered_estimator=True, wrap=lambda command: command,
               census_sessions=None, census_warnings=(), check_registered_models=True):
    """Pre-commit stage-1 sequence. Returns (exit code, summary).

    The summary is written even when a later step raises (verdict ABORTED_ON_ERROR)."""
    from tests.test_bytes_agreement import compare_campaign   # the registered comparer (section 12)
    out_root = Path(out_root)
    if out_root.exists():
        raise Stage1Error("output root must be a new directory")
    estimator = sha256_file(ROOT / "joulewise/bytes_analysis.py")
    if require_registered_estimator and estimator != REGISTERED_ESTIMATOR_SHA256:
        raise Stage1Error(f"joulewise/bytes_analysis.py is {estimator}, not the registered {REGISTERED_ESTIMATOR_SHA256}")
    manifest = ba.validate_manifest(ba.read_json(manifest_path))
    if check_registered_models:
        registered = json.loads((ROOT / "configs/bytes/bytes_manifest.json").read_bytes())
        if manifest["models"] != registered["models"]:
            raise Stage1Error("manifest models differ from the registered section 4 models")
    if census_sessions is not None and sorted(s["session_id"] for s in manifest["sessions"]) != sorted(census_sessions):
        raise Stage1Error("manifest sessions differ from the census sessions")
    heads = _git_state()
    o = out_root / "out"
    o.mkdir(parents=True)
    empty = out_root / "no-keys"
    empty.mkdir()
    released = out_root / "released-keys"
    summary = {"schema": "joulewise.bytes_stage1_run.v1", "producing_commit": heads[0],
               "producing_tree_dirty": heads[1], "bytes_analysis_sha256": estimator,
               "manifest_file_sha256": sha256_file(manifest_path), "manifest_sha256": ba.digest(manifest),
               "exports": [str(Path(d).resolve()) for d in export_dirs], "exits": {},
               "census_warnings": list(census_warnings)}
    analysis = [python, str(ROOT / "scripts/bytes_analyze.py"), "--manifest", str(manifest_path), "--export",
                *[str(d) for d in export_dirs]]
    twin = [python, str(ROOT / "scripts/bytes_twin.py"), "--manifest", str(manifest_path)]
    if len(export_dirs) == 1:
        twin += ["--export-dir", str(export_dirs[0])]
    else:
        for table, _sidecar in _sessions_in(export_dirs).values():
            twin += ["--export", str(table)]
    for session in manifest["sessions"]:
        twin += ["--archive", session["archive"]]

    def run(tag, command):
        result = subprocess.run(wrap(command), cwd=ROOT, capture_output=True, text=True, check=False)
        (o / (tag + ".exit")).write_text(str(result.returncode) + "\n")
        (o / (tag + ".stdout")).write_text(result.stdout)
        (o / (tag + ".stderr")).write_text(result.stderr)
        summary["exits"][tag] = result.returncode
        return result.returncode

    def finish(code, verdict):
        summary.update(verdict=verdict, exit=code)
        (out_root / "stage1-summary.json").write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n")
        return code, summary

    try:
        run("a-blinded", analysis + ["--stage", "blinded", "--out", str(o / "a-blinded")])
        run("t-blinded", twin + ["--stage", "blinded", "--out", str(o / "t-blinded.json")])
        recorder = compare_campaign(out_root)
        summary["blinded_agreement"] = _counts(recorder)
        (out_root / "agreement-blinded.json").write_text(json.dumps(recorder.rows, sort_keys=True, indent=1, default=str) + "\n")
        if summary["exits"]["a-blinded"] or summary["exits"]["t-blinded"]:
            return finish(2, "STOPPED_BLINDED_REFUSED")
        if recorder.above():
            return finish(3, "STOPPED_BLINDED_DISAGREEMENT")
        run("a-fit-nokeys", analysis + ["--stage", "fit", "--key-dir", str(empty), "--out", str(o / "a-fit-nokeys")])
        run("t-1-nokeys", twin + ["--stage", "1", "--key-dir", str(empty), "--out", str(o / "t-1-nokeys.json")])
        if summary["exits"]["a-fit-nokeys"] == 0 or summary["exits"]["t-1-nokeys"] == 0:
            return finish(4, "STOPPED_STAGE1_RAN_WITHOUT_KEYS")
        keys = sorted({blinding.REFERENCE_KEY, *(m["config_key"] for m in manifest["models"] if m["role"] == "fit")})
        record = release_fn(pack_records_root, keys, released)
        summary["release"] = {"keys": keys, "record": {k: record.get(k) for k in ("stage", "keys", "sha256", "released_utc")}}
        run("a-fit", analysis + ["--stage", "fit", "--key-dir", str(released), "--out", str(o / "a-fit")])
        run("t-1", twin + ["--stage", "1", "--key-dir", str(released), "--out", str(o / "t-1.json")])
        recorder = compare_campaign(out_root)
        summary["stage1_agreement"] = _counts(recorder)
        (out_root / "agreement-stage1.json").write_text(json.dumps(recorder.rows, sort_keys=True, indent=1, default=str) + "\n")
        predictions = o / "a-fit/predictions.json"
        if summary["exits"]["a-fit"] or not predictions.is_file():
            return finish(5, "STOPPED_STAGE1_REFUSED")
        summary["predictions_sha256"] = sha256_file(predictions)
        if (o / "a-fit/predictions.sha256").read_text().split()[0] != summary["predictions_sha256"]:
            return finish(6, "STOPPED_PREDICTIONS_HASH_MISMATCH")
        if summary["exits"]["t-1"] or recorder.above():
            return finish(7, "PREDICTIONS_WRITTEN_STAGE1_DISAGREEMENT")
        return finish(0, "READY_TO_COMMIT")
    except BaseException as exc:
        if "verdict" not in summary:
            summary["error"] = f"{type(exc).__name__}: {exc}"
            finish(1, "ABORTED_ON_ERROR")
        raise


def _parse_session(text):
    parts = text.split("=", 1)
    if len(parts) != 2 or ":" not in parts[1]:
        raise argparse.ArgumentTypeError("expected SESSION_ID=ARCHIVE:EXPORT_DIR")
    archive, export_dir = parts[1].split(":", 1)
    return parts[0], Path(archive), Path(export_dir)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("census", help="structure-only export check (no energy column, no withheld store read)")
    c.add_argument("--export", nargs="+", required=True, type=Path)
    c.add_argument("--out", type=Path, help="write the census JSON here (new file)")
    m = sub.add_parser("manifest", help="registered manifest plus the twelve counting sessions")
    m.add_argument("--session", action="append", required=True, type=_parse_session,
                   help="SESSION_ID=ARCHIVE:EXPORT_DIR, once per counting session")
    m.add_argument("--out", required=True, type=Path)
    r = sub.add_parser("run", help="blinded agreement, stage-1 release and stage 1 (writes predictions.json)")
    r.add_argument("--manifest", required=True, type=Path)
    r.add_argument("--export", nargs="+", required=True, type=Path)
    r.add_argument("--pack-records-root", required=True, type=Path)
    r.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "census":
            record, reasons = census(args.export)
            text = json.dumps(record, sort_keys=True, indent=2) + "\n"
            if args.out:
                if args.out.exists():
                    raise Stage1Error("census output exists")
                args.out.write_text(text)
            print(text, end="")
            return 0 if not reasons else 2
        if args.command == "manifest":
            if args.out.exists():
                raise Stage1Error("manifest output exists")
            manifest = build_manifest(args.session)
            args.out.write_text(json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n")
            print(json.dumps({"manifest": str(args.out), "sha256": ba.digest(manifest),
                              "sessions": [s["session_id"] for s in manifest["sessions"]]}))
            return 0
        record, reasons = census(args.export)
        if reasons:
            print(json.dumps(record, sort_keys=True, indent=2))
            raise Stage1Error("census refused; stage 1 not started")
        code, summary = run_stage1(args.manifest, args.export, args.pack_records_root, args.out,
                                   census_sessions=[s["session_id"] for s in record["sessions"]],
                                   census_warnings=record["warnings"])
        print(json.dumps({k: summary.get(k) for k in ("verdict", "exit", "predictions_sha256", "exits")}, sort_keys=True))
        return code
    except (Stage1Error, ba.AnalysisError, OSError, ValueError, KeyError) as exc:
        print(f"bytes stage 1 refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
