"""BY-THERM-LINES review chain, part B: tool -> UNCHANGED bytes_analysis on the real
grouped-blind BYTES export layout (tests/fixtures/bytes/campaign.py, subpack_sessions=True,
real joulewise.b6.export_runs.export: fit-config and reference rows in the public
*.runs.csv, heldout-config science rows in the withheld store under key custody).

The campaign fixture writes the harvest layout directly (no harvest run), so the thermal
inputs (one OS code, spans, thresholds, journal) are injected by hand as in the builder's
BoundAnalysisReplayTests; these injections are labelled. Everything downstream of the
tool is the unchanged analysis.

    python3.13 by-therm-lines-rev-opus/chain_analysis.py
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

JW = Path(os.environ.get("JW", "/tmp/jw"))
sys.path.insert(0, str(JW))
from joulewise import bytes_analysis as ba  # noqa: E402
from scripts import bytes_thermal_lines as t  # noqa: E402
from tests.b6 import test_bytes_p2_thermal_window as fx  # noqa: E402
from tests import test_harvest_b5_window as w  # noqa: E402
from tests.test_bytes_analysis import archive_campaign, release_keys  # noqa: E402

NS = fx.NS
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (": " + str(detail) if detail else ""))


def rewrite_csv(path, run, code):
    with path.open(newline="") as s:
        r = csv.DictReader(s)
        fields, rows = r.fieldnames, list(r)
    hit = False
    for row in rows:
        if row["run_id"] == run:
            row["exclusion_codes"] = code
            row["excluded"] = "True"
            hit = True
    with path.open("w", newline="") as s:
        wr = csv.DictWriter(s, fields)
        wr.writeheader()
        wr.writerows(rows)
    return hit


def cell(records, manifest, model):
    try:
        cells = ba.reduce_models(records, manifest, boundaries=("rails",))
    except ba.AnalysisError as exc:
        return {"status": "error:" + str(exc)}
    c = next((c for c in cells if c["model"] == model), None)
    if c is None:
        return {"status": "model absent from reduced cells", "records": sum(r.get("model") == model for r in records)}
    return {k: c.get(k) for k in ("status", "n_b", "removed_runs")}


def main():
    fx.setUpModule()
    root = Path(tempfile.mkdtemp(prefix="btl-ana-", dir=os.environ.get("TMPDIR")))
    manifest = archive_campaign(root, non_claim=False, release="none", subpack_sessions=True)
    models = {m["model"]: m for m in manifest["models"]}
    for sid in ("bytes-s5-p1", "bytes-s2-p1", "bytes-s2-p2"):
        session = next(s for s in manifest["sessions"] if s["session_id"] == sid)
        source = Path(session["archive"])
        export = root / "export" / sid
        side = json.loads((export / (sid + ".session.json")).read_text())["blinding"]["withheld"]
        store = (export / side["path"]).resolve()
        roster_path = source / "derived/roster.json"
        roster = json.loads(roster_path.read_bytes())
        for m in roster["members"]:  # real harvest rosters carry kind; this fixture carries role
            m["kind"] = "science" if m["role"] == "science" else "external_input"
        roster_path.write_text(json.dumps(roster))
        science = [m for m in roster["members"] if m["role"] == "science"]
        # choose the target: a heldout-config member when one exists (s5, s2), else fit
        heldout = [m for m in science if models[next(x["model"] for x in manifest["models"]
                   if m["units"][0]["cell_id"] in x["cell_ids"])]["role"] == "heldout"
                   and m["units"][0]["stratum"] == "quad"]
        fit = [m for m in science if m not in heldout and m["units"][0]["stratum"] == "quad"
               and models[next(x["model"] for x in manifest["models"]
                          if m["units"][0]["cell_id"] in x["cell_ids"])]["role"] == "fit"]
        for label, pool in (("heldout", heldout), ("fit", fit)):
            if not pool:
                continue
            target = pool[0]
            run = target["run_id"]
            model = next(x for x in manifest["models"] if target["units"][0]["cell_id"] in x["cell_ids"])
            work = root / f"{sid}-{label}"
            import shutil
            shutil.copytree(source, work / "archive", symlinks=True)
            shutil.copytree(export, work / "export", symlinks=True)
            wstore = work / "store.runs.csv"
            if store.is_file():
                shutil.copyfile(store, wstore)
                sc = json.loads((work / "export" / (sid + ".session.json")).read_text())
                sc["blinding"]["withheld"]["path"] = os.path.relpath(wstore, work / "export")
                (work / "export" / (sid + ".session.json")).write_text(json.dumps(sc, sort_keys=True, indent=2) + "\n")
            arch = work / "archive"
            acc_path = arch / "derived/b6-acceptance.json"
            acc = json.loads(acc_path.read_bytes())
            pass_id = session["pass_id"]
            # LABELLED INJECTION (no harvest in this fixture)
            if pass_id == 2:
                values = {m["run_id"]: {t.FIELD: {"excluded": m is target, "journal_available": True,
                          "samples": [], "span_monotonic_ns": [20 * NS, 110 * NS]}} for m in science}
                (arch / "withheld/member-assessments.json").write_text(json.dumps({"members": values}))
                mode = "hull-p2"
            else:
                acc["excluding"].append({"scope": "member", "run_id": run, "code": t.CODE, "why": t.CODE})
                acc_path.write_text(json.dumps(acc))
                spans = {m["run_id"]: {"member": None, "request": None} for m in science}
                spans[run] = {"member": [20 * NS, 110 * NS], "request": [40 * NS, 80 * NS]}
                (arch / "withheld/spans.json").write_text(json.dumps({"spans": spans}))
                (arch / "derived/harvest-thresholds.json").write_text(json.dumps({"values": w.REGISTERED_HARVEST_THRESHOLDS}))
                j = arch / "sources/night-custody/hazards/monitor/thermal.jsonl"
                j.parent.mkdir(parents=True, exist_ok=True)
                fx.thermal_journal(range(0, 126, 5), {90}).dump(j)  # s5-p1 shape: first nonzero 10 s after request end
                csv_hit = rewrite_csv(work / "export" / (sid + ".runs.csv"), run, t.CODE)
                if not csv_hit and wstore.is_file():
                    rewrite_csv(wstore, run, t.CODE)
                mode = "request-end-p1"
            # tool, archive-only and blinded
            out_a = work / "line-archive"
            rec_a = t.transform(mode, arch, out_a)
            check(f"{sid}/{label}: archive-stage transform changes exactly the target",
                  [c["run_id"] for c in rec_a["changes"]] == [run], rec_a["changes"])
            out_b = work / "line-blinded"
            try:
                rec_b = t.transform(mode, arch, out_b, work / "export")
                blinded_err = None
            except ValueError as exc:
                rec_b, blinded_err = None, str(exc)
            check(f"{sid}/{label}: blinded transform result", True,
                  {"refused": blinded_err, "in_public_csv": run in (work / "export" / (sid + ".runs.csv")).read_text()})
            # analysis: source vs output, archive stage (stage=all via export ingress, archive locator -> out)
            local = copy.deepcopy(manifest)
            local["sessions"] = [copy.deepcopy(session)]
            release_keys(root, manifest, "all")
            local["sessions"][0]["released_key_dir"] = str((root / "released-keys/bytes/blinding").resolve())
            one = work / "one-export"
            one.mkdir(exist_ok=True)
            for name in (sid + ".runs.csv", sid + ".session.json"):
                if not (one / name).exists():
                    (one / name).symlink_to(work / "export" / name)
            local["sessions"][0]["archive"] = str(arch)
            src = cell(ba.load_records(one, local, stage="all"), local, model["model"])
            local_out = copy.deepcopy(local)
            local_out["sessions"][0]["archive"] = str(out_a)
            new = cell(ba.load_records(one, local_out, stage="all"), local_out, model["model"])
            check(f"{sid}/{label}: archive stage source vs line ({model['model']})", True, {"source": src, "line": new})
            # direct archive ingress (load_records on the archive root) as the builder's test does
            try:
                d_src = cell(ba.load_records(arch, local, stage="all"), local, model["model"])
                d_new = cell(ba.load_records(out_a, local_out, stage="all"), local_out, model["model"])
            except Exception as exc:  # noqa: BLE001
                d_src = d_new = "error " + type(exc).__name__ + ": " + str(exc)[:200]
            check(f"{sid}/{label}: archive-root ingress source vs line", True, {"source": d_src, "line": d_new})
            # blinded stage: pre-commit and post-commit (stage1_commit) on source vs output export
            for commit in (None, "a" * 40):
                b_src = cell(ba.load_records(one, local, stage="blinded", stage1_commit=commit), local, model["model"])
                if rec_b is not None:
                    b_new = cell(ba.load_records(out_b / "export", local, stage="blinded", stage1_commit=commit),
                                 local, model["model"])
                else:
                    b_new = "no output (refused)"
                check(f"{sid}/{label}: blinded stage commit={bool(commit)} source vs line", True,
                      {"source": b_src, "line": b_new,
                       "line_export_files": sorted(p.name for p in (out_b / "export").iterdir()) if rec_b else None})
    print("\nSUMMARY", sum(ok for _, ok, _ in RESULTS), "/", len(RESULTS), "; root", root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
