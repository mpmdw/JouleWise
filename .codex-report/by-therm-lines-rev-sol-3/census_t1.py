"""T1 census on the native grouped-blind export (independent of the builder's test).

Native archive_campaign (grouped, subpack sessions) for s2 and s5, both passes. Per
session: one changed public (fit) member where the session has one, and one changed
withheld (heldout) member. Transform with --export, then check (a) public+withheld row
census, (b) model census of the unchanged analysis, (c) code rewrite == change list with
all other fields equal, (d) copied store name, and which CSV files the analysis opens at
each blinded stage (before / after the stage-1 commit).
Run:  python3.13 census_t1.py   (seat env sourced; JW defaults to /tmp/jw; ~5 min)
"""
import copy, csv, json, os, shutil, sys, tempfile
from pathlib import Path

JW = Path(os.environ.get("JW", "/tmp/jw"))
sys.path.insert(0, str(JW))
os.environ["JW_B5_SYNTHETIC_ONLY"] = "1"
from tests.test_bytes_analysis import archive_campaign  # noqa: E402
from tests.b6.test_bytes_p2_thermal_window import thermal_journal, NS  # noqa: E402
from scripts import bytes_thermal_lines as t  # noqa: E402
from joulewise import bytes_analysis as ba  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" :: " + str(detail) if detail else ""), flush=True)
    if not ok:
        FAILS.append(name)


def put(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v))


def get(p):
    return json.loads(p.read_bytes())


def rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tables(export, sid):
    side = get(export / (sid + ".session.json"))
    store = export / side["blinding"]["withheld"]["path"]
    return export / (sid + ".runs.csv"), store


OPENED = []
_real = ba._export_rows


def spy(path):
    OPENED.append(Path(path).resolve())
    return _real(path)


ba._export_rows = spy


def blinded(export, local, commit):
    OPENED.clear()
    rec = ba.load_records(export, local, stage="blinded", stage1_commit="synthetic-committed" if commit else None)
    models = sorted((x["model"], x["status"], x.get("n_b")) for x in ba.reduce_models(rec, local, boundaries=("rails",)))
    return rec, models, list(OPENED)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        skipped = [f"bytes-s{s}-p{p}" for s in range(1, 7) for p in (1, 2) if s not in (2, 5)]
        manifest = archive_campaign(root, non_claim=False, subpack_sessions=True, uncollected_sessions=skipped, release="none")
        private = root / "private-keys/bytes/blinding"; released = root / "released-keys/bytes/blinding"
        released.mkdir(parents=True, exist_ok=True)
        for path in private.glob("*.json"):
            shutil.copyfile(path, released / path.name)
        for session in manifest["sessions"]:
            a = Path(session["archive"]); p = session["pass_id"]; sid = session["session_id"]
            exp = root / "export" / sid
            roster = get(a / "derived/roster.json")
            for m in roster["members"]:
                m["kind"] = "science" if m["role"] == "science" else "external_input"
            put(a / "derived/roster.json", roster)
            science = [m for m in roster["members"] if m["role"] == "science"]
            public, store = tables(exp, sid)
            pub_ids = {r["run_id"] for r in rows(public)}
            wh_ids = {r["run_id"] for r in rows(store)}
            quads = [m for m in science if m["units"][0]["stratum"] == "quad"]
            targets = [next(m["run_id"] for m in quads if m["run_id"] in wh_ids)]
            fit = [m["run_id"] for m in quads if m["run_id"] in pub_ids]
            if fit:
                targets.append(fit[0])
            if p == 2:
                put(a / "withheld/member-assessments.json", {"members": {m["run_id"]: {t.FIELD: {
                    "excluded": m["run_id"] in targets, "journal_available": True}} for m in science}})
            else:
                ac = get(a / "derived/b6-acceptance.json")
                ac["excluding"] += [{"scope": "member", "run_id": r, "code": t.CODE} for r in targets]
                put(a / "derived/b6-acceptance.json", ac)
                put(a / "withheld/spans.json", {"spans": {m["run_id"]: {"member": [20 * NS, 100 * NS],
                                                                       "request": [40 * NS, 80 * NS]} for m in science}})
                j = a / "sources/night-custody/hazards/monitor/thermal.jsonl"
                j.parent.mkdir(parents=True, exist_ok=True)
                thermal_journal(range(0, 126, 5), {90}).dump(j)
                for path in (public, store):
                    with path.open(newline="") as f:
                        reader = csv.DictReader(f); fields = reader.fieldnames; rs = list(reader)
                    for r in rs:
                        if r["run_id"] in targets:
                            r["exclusion_codes"] = t.CODE; r["excluded"] = "True"
                    with path.open("w", newline="") as f:
                        w = csv.DictWriter(f, fields); w.writeheader(); w.writerows(rs)
            # Archive ingress' historical default locator (as Sol's campaign.py), absolute store path.
            legacy = root / "export/bytes"; legacy.mkdir(exist_ok=True)
            shutil.copyfile(public, legacy / (sid + ".runs.csv"))
            side = get(exp / (sid + ".session.json"))
            side["blinding"]["withheld"]["path"] = str(store.resolve())
            put(legacy / (sid + ".session.json"), side)
            mode = "hull-p2" if p == 2 else "request-end-p1"
            out = root / (sid + "-line")
            rec = t.transform(mode, a, out, exp)
            changed = {c["run_id"] for c in rec["changes"]}
            check(f"{sid} change list == targets", changed == set(targets), (sorted(changed), targets))
            oexp = out / "export"
            opub, ostore = tables(oexp, sid)
            # (d) store name and location
            check(f"{sid} (d) copied store named SESSION.withheld.csv under output",
                  ostore.resolve() == (oexp / "withheld" / (sid + ".withheld.csv")).resolve() and ostore.is_file()
                  and not ostore.is_symlink(), str(ostore.relative_to(out)))
            check(f"{sid} (d) no extra *.runs.csv under output export",
                  sorted(x.name for x in oexp.rglob("*.runs.csv")) == [sid + ".runs.csv"])
            # (a) row census
            sp, sw, op, ow = rows(public), rows(store), rows(opub), rows(ostore)
            check(f"{sid} (a) public+withheld census", (len(sp), len(sw)) == (len(op), len(ow)),
                  (len(sp), len(sw), len(op), len(ow)))
            # (c) code rewrite exactly as change list, every other field equal
            after = {}
            for x in get(out / "derived/b6-acceptance.json")["excluding"]:
                if x.get("scope") == "member":
                    after.setdefault(x["run_id"], set()).add(x["code"])
            diff_runs, other_diff = set(), []
            for s_rows, o_rows in ((sp, op), (sw, ow)):
                for s, o in zip(s_rows, o_rows):
                    if s != o:
                        diff_runs.add(s["run_id"])
                    if {k: v for k, v in s.items() if k not in ("exclusion_codes", "excluded")} != \
                       {k: v for k, v in o.items() if k not in ("exclusion_codes", "excluded")}:
                        other_diff.append(s["run_id"])
                    want = ";".join(sorted(after.get(o["run_id"], set())))
                    if o["exclusion_codes"] != want or o["excluded"] != str(bool(want)):
                        other_diff.append(("codes", o["run_id"], o["exclusion_codes"], o["excluded"]))
            check(f"{sid} (c) rows differ exactly on change list, codes==output acceptance, other fields equal",
                  diff_runs == changed and not other_diff, (sorted(diff_runs), other_diff[:3]))
            wh_changed = [m for m in rec["member_statuses"] if m["run_id"] in wh_ids and m["run_id"] in changed]
            check(f"{sid} withheld changed member: blinded_status row withheld",
                  all(m["blinded_status"] == "not defined at blinded stage (row withheld)" for m in wh_changed) and wh_changed)
            # (b) analysis model census, both blinded stages; which files are opened
            local = copy.deepcopy(manifest); local["sessions"] = [copy.deepcopy(session)]
            local["sessions"][0]["released_key_dir"] = str((a / session["released_key_dir"]).resolve())
            for commit in (False, True):
                srec, smodels, sopen = blinded(exp, local, commit)
                orec, omodels, oopen = blinded(oexp, local, commit)
                check(f"{sid} (b) commit={commit} record census source==output", len(srec) == len(orec), (len(srec), len(orec)))
                check(f"{sid} (b) commit={commit} model set source==output",
                      [m[0] for m in smodels] == [m[0] for m in omodels], (smodels, omodels))
                want_open = [opub.resolve()] + ([ostore.resolve()] if commit else [])
                check(f"{sid} (d) commit={commit} analysis opened exactly the output's own tables",
                      oopen == want_open, [str(x) for x in oopen])
                print("MODELS", sid, "commit", commit, "source", smodels, "line", omodels, flush=True)
            # archive stage: model census on the views
            for label, path in (("source", a), ("line", out)):
                arec = ba.load_records(path, local, stage="all")
                print("ARCHIVE", sid, label, sorted({(r["model"]) for r in arec}), len(arec),
                      sorted((x["model"], x["status"], x.get("n_b")) for x in ba.reduce_models(arec, local, boundaries=("rails",))),
                      flush=True)
            check(f"{sid} verify view", t.verify(out) == [])
    print("SUMMARY fails", FAILS, flush=True)


if __name__ == "__main__":
    main()
