"""Executing probes for BY-THERM-LINES fix rounds 2-3 (V1 direction, stops, verify, U1, blinding).

Run with the seat env sourced:  JW=/tmp/jw python3.13 probes_v.py
Prints PROBE <name> <observed>. Observations, not assertions; REPORT.md says which are defects.
"""
import csv, hashlib, io, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

JW = Path(os.environ.get("JW", "/tmp/jw"))
sys.path.insert(0, str(JW))
from scripts import bytes_thermal_lines as t  # noqa: E402
from tests.b6 import test_bytes_p2_thermal_window as fx  # noqa: E402

NS = 10**9
SCRIPT = JW / "scripts/bytes_thermal_lines.py"


def out(name, value):
    print("PROBE", name, value, flush=True)


def cli(*args, script=SCRIPT):
    p = subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True)
    tail = (p.stdout + p.stderr).strip().splitlines()
    return p.returncode, tail[-1] if tail else ""


def rec(o):
    p = Path(o) / "thermal_line.json"
    return json.loads(p.read_text()) if p.is_file() else None


def summary(o):
    r = rec(o)
    if r is None:
        return "NO RECORD"
    return {"members": {m["run_id"]: m["status"] for m in r["member_statuses"]},
            "eq": r["equals_registered_line"], "status": r["status"],
            "dropped": [d["run_id"] for d in r["dropped_members"]],
            "notices": sorted({n["code"] for n in r["notices"]})}


class Arch:
    """a carries thermal.os_level_nonzero, b does not; both science, plus reference r."""

    def __init__(self, root, codes=("a",), bytes_pass=None, nonzero=(90,), seal=True):
        self.root = Path(root)
        self.a = self.root / "archive"
        self.put("derived/b6-acceptance.json", {"session_id": "s", "excluding": [
            {"scope": "member", "run_id": r, "code": t.CODE} for r in codes]})
        self.put("derived/roster.json", {"members": [
            {"run_id": r, "kind": "science", "units": []} for r in ("a", "b")]
            + [{"run_id": "r", "kind": "reference", "units": []}]})
        self.put("withheld/spans.json", {"spans": {
            r: {"member": [20 * NS, 100 * NS], "request": [40 * NS, 80 * NS]} for r in ("a", "b")}})
        if bytes_pass is not None:
            self.put("sources/repo/plan_tree.json", {"bytes_pass": bytes_pass})
        self.journal = self.a / "sources/night-custody/hazards/monitor/thermal.jsonl"
        self.journal.parent.mkdir(parents=True)
        fx.thermal_journal(range(0, 126, 5), set(nonzero)).dump(self.journal)
        if seal:
            self.seal()

    def seal(self, digest=None):
        self.put("derived/window_flags.json", {"hazards": {"thermal": {"continuous": {"journal": {
            "sha256": digest or hashlib.sha256(self.journal.read_bytes()).hexdigest()}}}}})

    def put(self, name, data, raw=False):
        p = self.a / name
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():
            p.chmod(0o644)
        p.write_text(data if raw else json.dumps(data))
        return p

    def hull(self, a=None, b=None):
        members = {}
        for run, value in (("a", a), ("b", b)):
            if value is not None:
                members[run] = {t.FIELD: value}
        self.put("withheld/member-assessments.json", {"members": members})


OK = {"excluded": True, "journal_available": True}
NO = {"excluded": False, "journal_available": True}


def v1(base):
    n = iter(range(1000))

    def run(mode, A, *extra):
        o = base / f"o{next(n)}"
        rc = cli(mode, A.a, o, *extra)
        return rc, summary(o)

    # --- hull-p2, pass-2 archive
    A = Arch(base / "h1", bytes_pass=2); A.hull(a=OK, b=OK)
    out("V1 hull baseline b added", run("hull-p2", A))
    A = Arch(base / "h2", bytes_pass=2)
    out("V1 hull assessment-file-absent", run("hull-p2", A))
    A = Arch(base / "h3", bytes_pass=2); A.put("withheld/member-assessments.json", "{bad", raw=True)
    out("V1 hull assessment-not-json", run("hull-p2", A))
    A = Arch(base / "h4", bytes_pass=2); A.hull(a=OK)
    out("V1 hull b-field-missing", run("hull-p2", A))
    A = Arch(base / "h5", bytes_pass=2); A.hull(a=OK, b={"excluded": None, "journal_available": True})
    out("V1 hull b-excluded-null", run("hull-p2", A))
    A = Arch(base / "h6", bytes_pass=2); A.hull(a=OK, b={"excluded": False, "journal_available": False})
    out("V1 hull b-journal-unavailable", run("hull-p2", A))
    A = Arch(base / "h7", bytes_pass=2); A.hull(a={"excluded": False, "journal_available": False}, b=NO)
    out("V1 hull a-journal-unavailable-keeps", run("hull-p2", A))
    A = Arch(base / "h8", bytes_pass=2, codes=("a", "b"))
    out("V1 hull absent-all-carry-code", run("hull-p2", A))
    A = Arch(base / "h9", bytes_pass=1); A.hull(a=OK, b=OK)
    out("V1 hull pass-mismatch(p1 archive)", run("hull-p2", A))
    A = Arch(base / "h10", bytes_pass=None); A.hull(a=OK, b=OK)
    out("V1 hull no-plan_tree", run("hull-p2", A))
    A = Arch(base / "h11", bytes_pass=None); A.put("sources/repo/plan_tree.json", {"blinding_group": "bytes"})
    A.hull(a=OK, b=OK)
    out("V1 hull plan_tree-without-bytes_pass", run("hull-p2", A))
    A = Arch(base / "h12", bytes_pass=2); A.hull(a=OK, b=OK)
    A.put("derived/b6-acceptance.json", {"session_id": "s", "excluding": None})
    out("V1 hull acceptance-excluding-null", run("hull-p2", A))
    A = Arch(base / "h13", bytes_pass=2); A.hull(a=OK, b={"excluded": "yes", "journal_available": True})
    out("V1 hull b-excluded-nonbool", run("hull-p2", A))

    # --- request-end-p1, pass-1 archive; journal nonzero at 90 s lies outside request end (80 s)
    A = Arch(base / "r1", bytes_pass=1)
    out("V1 req baseline a removed", run("request-end-p1", A))
    A = Arch(base / "r2", bytes_pass=1); A.journal.unlink()
    out("V1 req journal-absent", run("request-end-p1", A))
    A = Arch(base / "r3", bytes_pass=1); (A.a / "withheld/spans.json").unlink()
    out("V1 req spans-absent", run("request-end-p1", A))
    A = Arch(base / "r4", bytes_pass=2)
    out("V1 req pass-mismatch(p2 archive)", run("request-end-p1", A))
    A = Arch(base / "r5", bytes_pass=1, seal=False)
    out("V1 req provenance-absent journal-would-remove", run("request-end-p1", A))
    # unverified journal says KEEP a (nonzero at 60 s, inside request); the true sealed one may remove it
    A = Arch(base / "r6", bytes_pass=1, nonzero=(60,), seal=False)
    out("V1 req provenance-absent journal-would-keep", run("request-end-p1", A))
    A = Arch(base / "r7", bytes_pass=1, nonzero=(90,))
    fx.thermal_journal(range(0, 126, 5), {60}).dump(A.journal)  # archived journal differs from the seal
    out("V1 req mismatch journal-would-keep", run("request-end-p1", A))
    A = Arch(base / "r8", bytes_pass=1, nonzero=(60,))
    fx.thermal_journal(range(0, 126, 5), {90}).dump(A.journal)
    out("V1 req mismatch journal-would-remove", run("request-end-p1", A))
    A = Arch(base / "r9", bytes_pass=1, codes=(), nonzero=(60,))
    out("V1 req matching-seal would-add (stop expected)", run("request-end-p1", A))
    A = Arch(base / "r10", bytes_pass=1, codes=(), nonzero=(90,))
    fx.thermal_journal(range(0, 126, 5), {60}).dump(A.journal)
    out("V1 req mismatch would-add", run("request-end-p1", A))
    A = Arch(base / "r11", bytes_pass=1, nonzero=(60,), seal=False)
    A.put("derived/window_flags.json", {"hazards": {"thermal": {"continuous": {"journal": None}}}})
    out("V1 req sealed-null journal-would-keep", run("request-end-p1", A))
    # Decisive cases: b's request-end window [70,80] s holds no nonzero sample in either journal,
    # so only a's determination is in question. The harvest's sealed journal (nonzero at 90 s only)
    # removes a's code; the archived journal that differs from the seal (nonzero at 60 s) keeps it.
    for name, seal in (("mismatch", "sealed"), ("provenance-absent", None)):
        A = Arch(base / ("r12" + name), bytes_pass=1, nonzero=(90,), seal=seal is not None)
        A.put("withheld/spans.json", {"spans": {"a": {"member": [20 * NS, 100 * NS], "request": [40 * NS, 80 * NS]},
                                                "b": {"member": [70 * NS, 100 * NS], "request": [75 * NS, 80 * NS]}}})
        truth = run("request-end-p1", A)
        fx.thermal_journal(range(0, 126, 5), {60}).dump(A.journal)
        out(f"V1 req {name} sealed-journal-truth", truth)
        out(f"V1 req {name} differing-journal-keeps-a", run("request-end-p1", A))


def stops(base):
    def ex(name, A, csv_text, mode="request-end-p1", sidecar=None):
        e = A.root / "export"; e.mkdir()
        (e / "s.runs.csv").write_bytes(csv_text if isinstance(csv_text, bytes) else csv_text.encode())
        if sidecar is not None:
            (e / "s.session.json").write_text(json.dumps(sidecar))
        o = A.root / "o"
        out("STOP " + name, (cli(mode, A.a, o, "--export", e), summary(o)))

    ex("empty-csv", Arch(base / "s1", bytes_pass=1), "")
    ex("header-only-no-codes-col", Arch(base / "s2", bytes_pass=1), "run_id,excluded\r\n")
    ex("non-utf8-csv", Arch(base / "s3", bytes_pass=1), b"run_id,exclusion_codes,excluded\r\na,\xff,True\r\n")
    ex("ragged-row", Arch(base / "s4", bytes_pass=1), "run_id,exclusion_codes,excluded\r\na," + t.CODE + "\r\n")
    A = Arch(base / "s5", bytes_pass=1)
    A.put("derived/b6-acceptance.json", {"excluding": [{"scope": "member", "run_id": "a", "code": t.CODE}]})
    ex("acceptance-missing-session_id", A, "run_id,exclusion_codes,excluded\r\na," + t.CODE + ",True\r\n")
    A = Arch(base / "s6", bytes_pass=1)
    A.put("derived/b6-acceptance.json", {"session_id": "s", "excluding": [{"scope": "member", "run_id": "a"}]})
    o = A.root / "o"; out("STOP exclusion-row-missing-code", (cli("request-end-p1", A.a, o), summary(o)))
    A = Arch(base / "s7", bytes_pass=1)
    A.put("derived/roster.json", {"members": [{"kind": "science"}]})
    o = A.root / "o"; out("STOP roster-member-missing-run_id", (cli("request-end-p1", A.a, o), summary(o)))
    # sidecar with a locator whose store is absent
    ex("withheld-store-absent", Arch(base / "s8", bytes_pass=1),
       "run_id,exclusion_codes,excluded\r\nb,,False\r\n",
       sidecar={"blinding": {"withheld": {"path": "gone.csv", "row_count": 1}}})
    # outside a git work tree
    ng = base / "nogit"; ng.mkdir()
    shutil.copytree(JW / "scripts", ng / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(JW / "joulewise", ng / "joulewise", ignore=shutil.ignore_patterns("__pycache__"))
    A = Arch(base / "s9", bytes_pass=1); o = A.root / "o"
    rc = cli("request-end-p1", A.a, o, script=ng / "scripts/bytes_thermal_lines.py")
    r = rec(o) or {}
    out("STOP outside-git", (rc, r.get("producing_commit", "NO RECORD"), r.get("producing_tree_dirty", "NO RECORD")))


def verify_probes(base):
    cases = {
        "record-notices-not-dicts": lambda o: patch(o, notices=[1]),
        "record-notice-without-code": lambda o: patch(o, notices=[{"x": 1}]),
        "record-source_sha256-list": lambda o: patch(o, source_sha256=[]),
        "record-is-list": lambda o: write(o / "thermal_line.json", "[]"),
        "record-missing-manifest-binding": lambda o: patch(o, view_manifest_sha256=None, drop=True),
        "record-member-status-edited": lambda o: patch(o, equals_registered_line=True),
        "manifest-entry-size-float": lambda o: manifest_edit(o, lambda m: m["files"][0].update(size=1.0)),
        "moved-source-acceptance": lambda o: (o.parent / "archive/derived/b6-acceptance.json").write_text("{}"),
        "added-view-file": lambda o: (o / "derived/extra.json").write_text("{}"),
        "deleted-view-file": lambda o: (o / "derived/roster.json").unlink(),
    }
    for i, (name, act) in enumerate(cases.items()):
        A = Arch(base / f"v{i}", bytes_pass=1); o = A.root / "o"
        cli("request-end-p1", A.a, o)
        p = A.a / "derived/b6-acceptance.json"; p.chmod(0o644)
        act(o)
        rc = cli("verify", o)
        r = rec(o)
        flag = r.get("records.thermal_view_changed") if isinstance(r, dict) else type(r).__name__
        out("VERIFY " + name, (rc, "flag=" + str(flag)))
    # verify through a symlinked path to a valid view
    A = Arch(base / "vl", bytes_pass=1); o = A.root / "o"
    cli("request-end-p1", A.a, o)
    link = A.root / "link"; link.symlink_to(o)
    out("VERIFY via-symlinked-output-path", cli("verify", link))
    out("VERIFY nonexistent-output", (cli("verify", base / "nope"), (base / "nope").exists()))


def write(p, text):
    if p.exists():
        p.chmod(0o644)
    p.write_text(text)


def patch(o, drop=False, **kw):
    r = rec(o)
    for k, v in kw.items():
        if drop:
            r.pop(k, None)
        else:
            r[k] = v
    write(o / "thermal_line.json", json.dumps(r))


def manifest_edit(o, fn):
    p = o / "view_manifest.json"
    m = json.loads(p.read_text()); fn(m)
    write(p, json.dumps(m))


def u1(base):
    A = Arch(base / "u", bytes_pass=1)
    e = A.root / "export"; e.mkdir()
    (e / "s.runs.csv").write_text("run_id,exclusion_codes,excluded\r\na," + t.CODE + ",True\r\nb,,False\r\n")
    snap = lambda: {str(p): p.read_bytes() for root in (A.a, e) for p in root.rglob("*") if p.is_file()}
    before = snap()
    ex = A.root / "exists"; ex.mkdir()
    out("U1 existing-output", (cli("request-end-p1", A.a, ex, "--export", e), sorted(os.listdir(ex))))
    dl = A.root / "dangling"; dl.symlink_to(A.root / "nowhere")
    out("U1 dangling-symlink-output", (cli("request-end-p1", A.a, dl, "--export", e), (A.root / "nowhere").exists()))
    sl = A.root / "slink"; sl.symlink_to(A.root / "elsewhere", target_is_directory=True); (A.root / "elsewhere").mkdir()
    out("U1 symlink-to-existing-dir-output", (cli("request-end-p1", A.a, sl, "--export", e),
                                              sorted(os.listdir(A.root / "elsewhere"))))
    out("U1 output-inside-archive", cli("request-end-p1", A.a, A.a / "derived/new", "--export", e))
    out("U1 output-inside-export", cli("request-end-p1", A.a, e / "new", "--export", e))
    pl = A.root / "plink"; pl.symlink_to(A.a / "derived")
    out("U1 output-parent-symlink-into-source", cli("request-end-p1", A.a, pl / "new", "--export", e))
    out("U1 archive-inside-output", cli("request-end-p1", A.a, A.root, "--export", e))
    out("U1 sources-unchanged", snap() == before)
    o1, o2 = A.root / "f1", A.root / "f2"
    cli("request-end-p1", A.a, o1, "--export", e); cli("request-end-p1", A.a, o2, "--export", e)
    r1, r2 = rec(o1), rec(o2)
    out("U1 two-fresh-manifests-identical", (o1 / "view_manifest.json").read_bytes() == (o2 / "view_manifest.json").read_bytes())
    out("U1 two-fresh-changes-identical", json.dumps(r1["changes"]) == json.dumps(r2["changes"])
        and r1["changes"] != [])
    out("U1 two-fresh-records-identical", (o1 / "thermal_line.json").read_bytes() == (o2 / "thermal_line.json").read_bytes())
    out("U1 two-fresh-export-identical", (o1 / "export/s.runs.csv").read_bytes() == (o2 / "export/s.runs.csv").read_bytes())


def dictwriter(base):
    """Withheld copy vs the exporter's own DictWriter (export_runs.py:735,744: csv.DictWriter(stream, fieldnames))."""
    S = ["918273645.192837", "827364519.283746", "736451928.374655", "645192837.465564"]
    cols = ["run_id", "status", "excluded", "exclusion_codes", "flag_codes", "gross_energy_j", "idle_power_w",
            "ttft_s", "bound_rail_j", "pass_id"]

    def render(rows):
        s = io.StringIO(newline="")
        w = csv.DictWriter(s, fieldnames=cols); w.writeheader()
        for r in rows:
            w.writerow(r)
        return s.getvalue().encode()

    def row(run, codes, extra=""):
        return {"run_id": run, "status": "ok", "excluded": bool(codes), "exclusion_codes": ";".join(codes),
                "flag_codes": "x;y", "gross_energy_j": S[0] + extra, "idle_power_w": S[1], "ttft_s": S[2],
                "bound_rail_j": S[3], "pass_id": 1}
    A = Arch(base / "dw", bytes_pass=1, codes=("a", "b"), nonzero=(90,))
    A.put("derived/b6-acceptance.json", {"session_id": "s", "excluding": [
        {"scope": "member", "run_id": r, "code": c} for r, c in (("a", t.CODE), ("b", t.CODE), ("b", "battery.x"))]})
    e = A.root / "export"; e.mkdir(); priv = A.root / "keys"; priv.mkdir()
    (e / "s.runs.csv").write_bytes(render([row("b", [t.CODE, "battery.x"])]))
    (priv / "s.withheld.csv").write_bytes(render([row("a", [t.CODE], ',\r\n"q"')]))
    (e / "s.session.json").write_text(json.dumps({"blinding": {"withheld": {
        "path": os.path.relpath(priv / "s.withheld.csv", e), "row_count": 1}}}))
    o = A.root / "o"
    rc = cli("request-end-p1", A.a, o, "--export", e)
    out("DW run", (rc, summary(o)))
    out("DW withheld == DictWriter(after)", (o / "export/withheld/s.withheld.csv").read_bytes()
        == render([row("a", [], ',\r\n"q"')]))
    out("DW public == DictWriter(after)", (o / "export/s.runs.csv").read_bytes() == render([row("b", ["battery.x"])]))
    out("DW public excluded stays True with battery code", b"b,ok,True,battery.x" in (o / "export/s.runs.csv").read_bytes())


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        base = Path(d)
        for fn in (v1, stops, verify_probes, u1, dictwriter):
            (base / fn.__name__).mkdir()
            fn(base / fn.__name__)
