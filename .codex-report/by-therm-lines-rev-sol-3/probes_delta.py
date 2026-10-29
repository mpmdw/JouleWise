"""Delta probes for BY-THERM-LINES fix round 1 (T2, T3, T4, blinding).

Run with the seat env sourced:  python3.13 probes_delta.py  (JW defaults to /tmp/jw).
Each probe prints PROBE <name> <observed>. Nothing here asserts a desired outcome;
the report states which observations are defects.
"""
import contextlib, hashlib, io, json, os, random, subprocess, sys, tempfile
from pathlib import Path

JW = Path(os.environ.get("JW", "/tmp/jw"))
sys.path.insert(0, str(JW))
from scripts import bytes_thermal_lines as t  # noqa: E402
from joulewise.b5 import harvest as h  # noqa: E402
from tests.b6 import test_bytes_p2_thermal_window as fx  # noqa: E402

NS = 10**9
SCRIPT = JW / "scripts/bytes_thermal_lines.py"


def out(name, value):
    print("PROBE", name, value, flush=True)


def cli(*args):
    p = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
    tail = (p.stdout + p.stderr).strip().splitlines()
    return p.returncode, tail[-1] if tail else ""


class Arch:
    def __init__(self, root, codes=("a",)):
        self.root = Path(root)
        self.a = self.root / "archive"
        self.put("derived/b6-acceptance.json", {"session_id": "s", "excluding": [
            {"scope": "member", "run_id": r, "code": t.CODE} for r in codes]})
        self.put("derived/roster.json", {"members": [
            {"run_id": r, "kind": "science", "units": []} for r in ("a", "b")]})
        self.put("withheld/spans.json", {"spans": {
            r: {"member": [20 * NS, 100 * NS], "request": [40 * NS, 80 * NS]} for r in ("a", "b")}})
        self.journal = self.a / "sources/night-custody/hazards/monitor/thermal.jsonl"
        self.journal.parent.mkdir(parents=True)
        fx.thermal_journal(range(0, 126, 5), {90}).dump(self.journal)

    def put(self, name, data, raw=False):
        p = self.a / name
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():
            p.chmod(0o644)
        p.write_text(data if raw else json.dumps(data))
        return p


def t2(base):
    # Export CSV that lacks the exclusion_codes column (a records fault, not physics).
    A = Arch(base / "t2a")
    e = base / "t2a/export"; e.mkdir()
    (e / "s.runs.csv").write_text("run_id,excluded\na,True\nb,False\n")
    out("T2 export-without-exclusion_codes-column", cli("request-end-p1", A.a, base / "t2a/o", "--export", e)
        + ((base / "t2a/o/thermal_line.json").is_file(),))
    # Empty public CSV.
    A = Arch(base / "t2b")
    e = base / "t2b/export"; e.mkdir()
    (e / "s.runs.csv").write_text("")
    out("T2 empty-public-csv", cli("request-end-p1", A.a, base / "t2b/o", "--export", e)
        + ((base / "t2b/o/thermal_line.json").is_file(),))
    # Withheld store located by the sidecar but absent.
    A = Arch(base / "t2c")
    e = base / "t2c/export"; e.mkdir()
    (e / "s.runs.csv").write_text("run_id,exclusion_codes,excluded\nb,,False\n")
    (e / "s.session.json").write_text(json.dumps({"blinding": {"withheld": {"path": "gone.csv", "row_count": 1}}}))
    rc = cli("request-end-p1", A.a, base / "t2c/o", "--export", e)
    rec = json.loads((base / "t2c/o/thermal_line.json").read_text()) if (base / "t2c/o/thermal_line.json").is_file() else {}
    out("T2 withheld-store-absent", rc + (rec.get("status"), [m["status"] for m in rec.get("member_statuses", [])],
                                           sorted(p.name for p in (base / "t2c/o/export").rglob("*"))
                                           if (base / "t2c/o/export").is_dir() else None))
    # hull-p2 assessment record missing journal_available.
    A = Arch(base / "t2d")
    A.put("withheld/member-assessments.json", {"members": {"a": {t.FIELD: {"excluded": True}},
                                                           "b": {t.FIELD: {"excluded": False, "journal_available": True}}}})
    out("T2 hull-record-missing-journal_available", cli("hull-p2", A.a, base / "t2d/o")
        + ((base / "t2d/o/thermal_line.json").is_file(),))
    # window_flags.json absent: is the journal provenance check recorded at all?
    A = Arch(base / "t2e")
    rc = cli("request-end-p1", A.a, base / "t2e/o")
    rec = json.loads((base / "t2e/o/thermal_line.json").read_text())
    out("T3 no-window_flags.json", rc + ([n["code"] for n in rec["notices"]], [c["run_id"] for c in rec["changes"]]))
    # Harvest recorded journal None (it read no journal) but an archived journal exists.
    A = Arch(base / "t2f")
    A.put("derived/window_flags.json", {"hazards": {"thermal": {"continuous": {"phase": "continuous", "journal": None}}}})
    rc = cli("request-end-p1", A.a, base / "t2f/o")
    rec = json.loads((base / "t2f/o/thermal_line.json").read_text())
    out("T3 sealed-journal-null", rc + ([n["code"] for n in rec["notices"]], rec["status"]))
    # Mismatched journal where it would ADD the code: request-end-would-add stop driven by a records fault.
    A = Arch(base / "t2g", codes=())
    A.put("derived/window_flags.json", {"hazards": {"thermal": {"continuous": {"journal": {"sha256": "0" * 64}}}}})
    fx.thermal_journal(range(0, 126, 5), {60}).dump(A.journal)
    out("T3 mismatch-and-would-add", cli("request-end-p1", A.a, base / "t2g/o")
        + ((base / "t2g/o/thermal_line.json").is_file(),))
    # Matching seal: decision proceeds; mismatch only on journal bytes.
    A = Arch(base / "t2h")
    A.put("derived/window_flags.json", {"hazards": {"thermal": {"continuous": {"journal": {
        "sha256": hashlib.sha256(A.journal.read_bytes()).hexdigest()}}}}})
    rc = cli("request-end-p1", A.a, base / "t2h/o")
    rec = json.loads((base / "t2h/o/thermal_line.json").read_text())
    out("T3 matching-seal", rc + ([c["run_id"] for c in rec["changes"]], rec["status"]))
    A.journal.write_bytes(A.journal.read_bytes() + b"\n")
    rc = cli("request-end-p1", A.a, base / "t2h/o2")
    rec = json.loads((base / "t2h/o2/thermal_line.json").read_text())
    out("T3 one-byte-journal-change", rc + ([c["run_id"] for c in rec["changes"]], rec["status"],
                                            rec["restored_members"]))


def t3_gap():
    """thermal.os_level_nonzero decision vs. gap threshold, on journals with real gaps."""
    rng = random.Random(598)
    checked = differ = with_holes = 0
    for _ in range(3000):
        stamps = sorted(rng.sample(range(0, 300), rng.randint(0, 40)))
        nonzero = {s for s in stamps if rng.random() < 0.15}
        J = fx.thermal_journal(stamps, nonzero)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "thermal.jsonl"
            J.dump(p)
            readings, _ = h.read_monitor_journal(p, "thermal")
        a = rng.randint(0, 250); b = rng.randint(a, 300)
        span = [a * NS + rng.choice([0, 1, -1, 500]), b * NS + rng.choice([0, 1, 7])]
        base = {c for c, *_ in h.thermal_member_flags(span, readings, {"thermal_unmeasured_gap_s": 0})}
        for gap in (1e-9, 1, 6, 15, 120, 1e6, "6", 0.5):
            got = {c for c, *_ in h.thermal_member_flags(span, readings, {"thermal_unmeasured_gap_s": gap})}
            checked += 1
            with_holes += "thermal.unmeasured" in got
            differ += (t.CODE in got) != (t.CODE in base)
    out("T3 gap-independence", {"comparisons": checked, "os_decision_differs": differ,
                                "comparisons_with_unmeasured_holes": with_holes})


def t4(base):
    A = Arch(base / "t4")
    A.put("withheld/reductions/a.json", {"x": "opaque"})
    o = base / "t4/o"
    cli("request-end-p1", A.a, o)
    modes = {str(p.relative_to(o)): oct(p.stat().st_mode & 0o777) for p in o.rglob("*")
             if p.is_file() and not p.is_symlink()}
    out("T4 modes-of-copies", modes)
    out("T4 baseline", cli("verify", o))
    # byte-identical replacement (new inode), as an atomic re-write would do
    p = A.a / "withheld/reductions/a.json"
    raw = p.read_bytes(); tmp = p.with_suffix(".tmp"); tmp.write_bytes(raw); os.replace(tmp, p)
    out("T4 identical-bytes-new-inode", cli("verify", o))
    # restore not possible (inode moved); fresh output per case
    cases = {
        "identical-bytes-touch-only": lambda: os.utime(A.a / "derived/roster.json", ns=(1, 1)),
        "deleted-linked-source": lambda: (A.a / "withheld/spans.json").unlink(),
        "added-file-in-view": lambda: (o2 / "derived/extra.json").write_text("{}"),
        "deleted-file-in-view": lambda: (o2 / "derived/roster.json").unlink(),
        "manifest-not-json": lambda: (os.chmod(o2 / "view_manifest.json", 0o644),
                                      (o2 / "view_manifest.json").write_text("{not json")),
        "manifest-deleted": lambda: (o2 / "view_manifest.json").unlink(),
        "manifest-files-list-of-ints": lambda: (os.chmod(o2 / "view_manifest.json", 0o644),
                                                (o2 / "view_manifest.json").write_text('{"files":[1]}')),
        "thermal_line-deleted": lambda: (o2 / "thermal_line.json").unlink(),
        "thermal_line-not-json": lambda: (os.chmod(o2 / "thermal_line.json", 0o644),
                                          (o2 / "thermal_line.json").write_text("{bad")),
        "source-acceptance-only-changed": lambda: A.put("derived/b6-acceptance.json", {
            "session_id": "s", "excluding": [{"scope": "member", "run_id": r, "code": t.CODE} for r in ("a", "b")]}),
    }
    for i, (name, act) in enumerate(cases.items()):
        A = Arch(base / f"t4c{i}")
        o2 = base / f"t4c{i}/o"
        cli("request-end-p1", A.a, o2)
        act()
        rc, tail = cli("verify", o2)
        flag = None
        try:
            flag = json.loads((o2 / "thermal_line.json").read_text())["records.thermal_view_changed"]
        except Exception as exc:  # noqa: BLE001
            flag = type(exc).__name__
        out("T4 " + name, (rc, tail, "flag=" + str(flag)))
    # Re-export of the source export after transform (copied CSV goes stale).
    A = Arch(base / "t4x")
    e = base / "t4x/export"; e.mkdir()
    (e / "s.runs.csv").write_text("run_id,exclusion_codes,excluded\na," + t.CODE + ",True\nb,,False\n")
    o3 = base / "t4x/o"
    cli("request-end-p1", A.a, o3, "--export", e)
    (e / "s.runs.csv").write_text("run_id,exclusion_codes,excluded\na," + t.CODE + ",True\nb," + t.CODE + ",True\n")
    out("T4 source-export-rewritten-after-transform", cli("verify", o3))


def blinding(base):
    S = ["918273645.192837", "827364519.283746", "736451928.374655", "645192837.465564", "554433221.112233"]
    A = Arch(base / "bl")
    acc = json.loads((A.a / "derived/b6-acceptance.json").read_text())
    acc["calibration"] = {"operative_bound_s": float(S[0]), "energy_j": float(S[1])}
    A.put("derived/b6-acceptance.json", acc)
    A.put("derived/window_flags.json", {"hazards": {"thermal": {"continuous": {"journal": {
        "sha256": hashlib.sha256(A.journal.read_bytes()).hexdigest(), "readings": 26}}},
        "battery": {"energy_j": float(S[2])}}})
    e = base / "bl/export"; e.mkdir()
    hdr = "run_id,exclusion_codes,excluded,gross_energy_j,idle_power_w,ttft_s,bound_rail_j\r\n"
    (e / "s.runs.csv").write_bytes((hdr + f"b,,False,{S[0]},\"{S[1]}\",{S[2]},{S[3]}\r\n").encode())
    priv = base / "bl/keys/withheld/pack"; priv.mkdir(parents=True)
    (priv / "s.runs.csv").write_bytes((hdr + f"a,{t.CODE},True,\"{S[4]},\r\n{S[0]}\",{S[1]},{S[2]},{S[3]}\r\n").encode())
    (e / "s.session.json").write_text(json.dumps({"operative_bound_s": float(S[3]), "blinding": {
        "withheld": {"path": os.path.relpath(priv / "s.runs.csv", e), "row_count": 1}}}))
    seen = []
    real_loads, real_decode = t.json.loads, t.decode_field

    def guarded_loads(raw, *a, **k):
        r = raw.decode() if isinstance(raw, bytes) else raw
        seen.extend(s for s in S if s in r)
        return real_loads(raw, *a, **k)

    def guarded_decode(raw, span):
        v = real_decode(raw, span)
        seen.extend(s for s in S if s in v)
        return v
    t.json.loads, t.decode_field = guarded_loads, guarded_decode
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            t.main(["request-end-p1", str(A.a), str(base / "bl/o"), "--export", str(e)])
            t.main(["verify", str(base / "bl/o")])
    finally:
        t.json.loads, t.decode_field = real_loads, real_decode
    o = base / "bl/o"
    rec_text = (o / "thermal_line.json").read_text() + (o / "view_manifest.json").read_text()
    store = (o / "export/withheld/s.withheld.csv").read_bytes()
    out("BLIND decoded-sentinels", seen)
    out("BLIND sentinels-in-stdout-or-record", [s for s in S if s in buf.getvalue() or s in rec_text])
    out("BLIND withheld-copy-bytes", (store == (priv / "s.runs.csv").read_bytes().replace(
        f"a,{t.CODE},True".encode(), b"a,,False"), store.count(S[0].encode())))
    out("BLIND sidecar-copy", (o / "export/s.session.json").read_text())


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        base = Path(d)
        t2(base)
        t4(base)
        blinding(base)
    t3_gap()
