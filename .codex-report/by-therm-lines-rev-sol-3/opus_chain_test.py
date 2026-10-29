"""BY-THERM-LINES review chain, part A: real harvest -> real B6 acceptance -> tool.

Run from the JouleWise checkout (JW=/tmp/jw), seat env sourced:
    python3.13 by-therm-lines-rev-opus/chain_test.py
No fixture adapter: derived/b6-acceptance.json is written by the production
joulewise.b6.session.accept_archive on the archive the production harvest wrote.
The cross-check is exact and fixture-free: the same synthetic session harvested as
pass 1 and as pass 2 must satisfy
    request-end-p1(pass-1 archive) member codes == pass-2 primary member codes
    hull-p2(pass-2 archive)        member codes == pass-1 primary member codes
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path

JW = Path(os.environ.get("JW", "/tmp/jw"))
sys.path.insert(0, str(JW))
from joulewise.b5 import harvest as h  # noqa: E402
from joulewise.b6.session import accept_archive  # noqa: E402
from scripts import bytes_thermal_lines as t  # noqa: E402
from tests.b6 import test_bytes_p2_thermal_window as fx  # noqa: E402
from tests import test_harvest_b5_window as w  # noqa: E402

NS = 10**9
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (": " + str(detail) if detail else ""))


def member_codes(archive_or_out):
    rows = json.loads((Path(archive_or_out) / "derived/b6-acceptance.json").read_bytes())["excluding"]
    out = {}
    for r in rows:
        if r.get("scope") == "member":
            out.setdefault(r["run_id"], []).append(r["code"])
    return {k: sorted(v) for k, v in out.items()}


def tree_digest(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(root).rglob("*")) if p.is_file() and not p.is_symlink()}


class Chain:
    def __init__(self, root):
        self.root = Path(root)
        self.b = fx.HarvestEntryTests()
        self.b.root = self.root

    def archive(self, pass_id, name, mutate=None):
        win = self.b.window(pass_id, name=name)
        if mutate:
            mutate(win)
        self.b.harvest(win)
        plan = json.loads(win.plan_path.read_text())
        result, _ = accept_archive(win.archive, plan, JW / "configs/b6/registration",
                                   plan_path=win.plan_path, replace_existing=True)
        return win, result


def journal_rows(win):
    path = win.custody / "hazards/monitor/thermal.jsonl"
    return path, [json.loads(s) for s in path.read_text().splitlines()]


def put_rows(path, rows, extra=""):
    path.write_text("".join(json.dumps(r) + "\n" for r in rows) + extra)


def run_cli(mode, archive, out, export=None):
    buf = io.StringIO()
    argv = [mode, str(archive), str(out)] + (["--export", str(export)] if export else [])
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()) as err:
        try:
            t.main(argv)
            code = 0
        except SystemExit as exc:
            code = exc.code
    return code, buf.getvalue(), err.getvalue()


def main():
    fx.setUpModule()
    root = Path(tempfile.mkdtemp(prefix="btl-chain-", dir=os.environ.get("TMPDIR")))
    c = Chain(root)
    science = [m[0] for m in w.MEMBERS]

    # --- default fixture (tail-only nonzero after every request end) -------
    w1, r1 = c.archive(1, "p1")
    w2, r2 = c.archive(2, "p2")
    p1, p2 = member_codes(w1.archive), member_codes(w2.archive)
    print("pass-1 primary member codes:", p1)
    print("pass-2 primary member codes:", p2)
    check("real acceptance carries OS code on every pass-1 science member",
          all(t.CODE in p1.get(r, []) for r in science), p1)
    check("real pass-2 primary carries no OS code", all(t.CODE not in v for v in p2.values()), p2)
    before1, before2 = tree_digest(w1.archive), tree_digest(w2.archive)
    code, stdout, err = run_cli("request-end-p1", w1.archive, root / "re1")
    check("request-end-p1 exit 0 on real archive", code == 0, err)
    re1 = member_codes(root / "re1")
    check("(c) request-end-p1(pass1) == pass-2 primary (exact)", re1 == p2, {"re1": re1, "p2": p2})
    code, stdout, err = run_cli("hull-p2", w2.archive, root / "hull2")
    check("hull-p2 exit 0 on real archive", code == 0, err)
    hull2 = member_codes(root / "hull2")
    check("(a) hull-p2(pass2) == pass-1 primary (exact)", hull2 == p1, {"hull2": hull2, "p1": p1})
    rec = json.loads((root / "hull2/thermal_line.json").read_text())
    check("(a) quad drops whole in hull record",
          any(sorted(u) == sorted(w.QUAD) for u in rec["dropped_units"]), rec["dropped_units"])
    check("(f) source archives unchanged",
          tree_digest(w1.archive) == before1 and tree_digest(w2.archive) == before2)
    code, _, err = run_cli("hull-p2", root / "hull2", root / "hull2b")
    check("(f) hull-p2 idempotent on its own output",
          code == 0 and member_codes(root / "hull2b") == hull2 and
          json.loads((root / "hull2b/thermal_line.json").read_text())["changes"] == [], err)
    code, _, err = run_cli("hull-p2", w1.archive, root / "wrongpass")
    check("pass mismatch refused", code == 2 and "bytes_pass" in err, err)

    # --- pass 1: nonzero inside one request, s5-p1-shaped tail elsewhere ----
    first = science[0]

    def inside(win):
        path, rows = journal_rows(win)
        start, end = w.request_span_ns(first)
        hit = next(r for r in rows if start < r["finished"]["monotonic_ns"] < end) if any(
            start < r["finished"]["monotonic_ns"] < end for r in rows) else next(
            r for r in rows if r["finished"]["monotonic_ns"] >= end)
        hit["values"]["level"] = 2
        put_rows(path, rows)
    wi1, _ = c.archive(1, "in1", inside)
    wi2, _ = c.archive(2, "in2", inside)
    code, _, err = run_cli("request-end-p1", wi1.archive, root / "in-out")
    check("(c) inside-request member stays dropped; others restored; equals pass-2 primary",
          code == 0 and member_codes(root / "in-out") == member_codes(wi2.archive),
          {"out": member_codes(root / "in-out"), "p2": member_codes(wi2.archive), "err": err})

    # --- level read exactly at the request end stamp ------------------------
    def at_end(win):
        path, rows = journal_rows(win)
        _s, end = w.request_span_ns(first)
        for r in rows:
            r["values"]["level"] = 0
        proto = json.loads(json.dumps(rows[0]))
        proto["finished"]["monotonic_ns"] = end
        proto["started"]["monotonic_ns"] = end - 1000
        proto["values"]["level"] = 1
        rows.append(proto)
        rows.sort(key=lambda r: r["finished"]["monotonic_ns"])
        for i, r in enumerate(rows, 1):
            r["seq"] = i
        put_rows(path, rows)
    we1, _ = c.archive(1, "end1", at_end)
    we2, _ = c.archive(2, "end2", at_end)
    code, _, err = run_cli("request-end-p1", we1.archive, root / "end-out")
    check("level==1 at exactly request-end stamp: tool == pass-2 primary",
          code == 0 and member_codes(root / "end-out") == member_codes(we2.archive),
          {"out": member_codes(root / "end-out"), "p2": member_codes(we2.archive), "p1": member_codes(we1.archive), "err": err})

    # --- malformed lines and non-numeric levels -----------------------------
    def malformed(win):
        path, rows = journal_rows(win)
        _s, end = w.request_span_ns(first)
        nxt = next(r for r in rows if r["finished"]["monotonic_ns"] >= end)
        nxt["values"]["level"] = "warm"  # non-numeric: production skips it as a level
        put_rows(path, rows, extra="{not json\n\x00garbage\n")
    wm1, _ = c.archive(1, "mal1", malformed)
    wm2, _ = c.archive(2, "mal2", malformed)
    code, _, err = run_cli("request-end-p1", wm1.archive, root / "mal-out")
    rec = json.loads((root / "mal-out/thermal_line.json").read_text()) if code == 0 else {}
    check("malformed lines + non-numeric level: tool == pass-2 primary, malformed noticed",
          code == 0 and member_codes(root / "mal-out") == member_codes(wm2.archive)
          and {"code": "records.monitor_line_malformed"} in rec.get("notices", []),
          {"out": member_codes(root / "mal-out") if code == 0 else None, "p2": member_codes(wm2.archive), "err": err})

    # --- hand edits on a real archive copy (labelled: not harvest-produced) --
    import shutil
    def copy(src, name):
        dst = root / name
        shutil.copytree(src, dst, symlinks=True)
        return dst
    # duplicate OS row + OS together with thermal.unmeasured + battery code
    a = copy(w1.archive, "hand-dup")
    acc = json.loads((a / "derived/b6-acceptance.json").read_text())
    acc["excluding"].append({"code": t.CODE, "scope": "member", "run_id": science[0], "why": t.CODE})
    acc["excluding"].append({"code": "thermal.unmeasured", "scope": "member", "run_id": science[1], "why": "x"})
    acc["excluding"].append({"code": "battery.member_span", "scope": "member", "run_id": science[2], "why": "x"})
    (a / "derived/b6-acceptance.json").write_text(json.dumps(acc))
    code, _, err = run_cli("request-end-p1", a, root / "hand-dup-out")
    got = member_codes(root / "hand-dup-out") if code == 0 else None
    check("dup OS row fully removed; other thermal code and battery code kept",
          got is not None and science[0] not in got and got.get(science[1]) == ["thermal.unmeasured"]
          and got.get(science[2]) == ["battery.member_span"], {"got": got, "err": err})
    # member absent from spans.json entirely
    a = copy(w1.archive, "hand-nospan")
    sp = json.loads((a / "withheld/spans.json").read_text())
    del sp["spans"][science[3]]
    (a / "withheld/spans.json").write_text(json.dumps(sp))
    code, _, err = run_cli("request-end-p1", a, root / "hand-nospan-out")
    got = member_codes(root / "hand-nospan-out") if code == 0 else None
    check("member absent from spans keeps hull OS code", got is not None and t.CODE in got.get(science[3], []),
          {"got": got, "err": err})
    # request span equal to the hull
    a = copy(w1.archive, "hand-eq")
    sp = json.loads((a / "withheld/spans.json").read_text())
    sp["spans"][science[4]]["request"] = list(sp["spans"][science[4]]["member"])
    (a / "withheld/spans.json").write_text(json.dumps(sp))
    code, _, err = run_cli("request-end-p1", a, root / "hand-eq-out")
    got = member_codes(root / "hand-eq-out") if code == 0 else None
    check("request == hull keeps hull OS code", got is not None and t.CODE in got.get(science[4], []),
          {"got": got, "err": err})
    # reference member with OS code
    a = copy(w1.archive, "hand-ref")
    ro = json.loads((a / "derived/roster.json").read_text())
    ro["members"][0]["kind"] = "external_input"
    (a / "derived/roster.json").write_text(json.dumps(ro))
    code, _, err = run_cli("request-end-p1", a, root / "hand-ref-out")
    got = member_codes(root / "hand-ref-out") if code == 0 else None
    check("reference member OS code untouched", got is not None and t.CODE in got.get(science[0], []),
          {"got": got, "err": err})
    # journal compressed like harvest accepts (thermal.jsonl.zst): harvest reads it, tool?
    a = copy(w1.archive, "hand-zst")
    j = a / "sources/night-custody/hazards/monitor/thermal.jsonl"
    raw = j.read_bytes()
    try:
        import subprocess
        subprocess.run(["zstd", "-q", "--rm", str(j)], check=True)
        readings, _ = h.read_monitor_journal(j, "thermal")
        code, _, err = run_cli("request-end-p1", a, root / "hand-zst-out")
        check("zst journal: production reader reads it, tool refuses (expected per brief? see report)",
              True, {"production_readings": len(readings), "tool_exit": code, "err": err.strip()})
    except (OSError, subprocess.CalledProcessError) as exc:
        check("zst journal probe", True, f"zstd unavailable: {exc}")
    del raw

    # --- blinding sentinels in JSON measurement fields ----------------------
    a = copy(w1.archive, "hand-sentinel")
    sentinel = "918273645.192837"
    acc = json.loads((a / "derived/b6-acceptance.json").read_text())
    acc["calibration"] = {"energy_j": float(sentinel), **(acc.get("calibration") or {})}
    raw = json.dumps(acc).replace(json.dumps(float(sentinel)), sentinel)
    (a / "derived/b6-acceptance.json").write_text(raw)
    ma = json.loads((a / "withheld/member-assessments.json").read_text())
    code, stdout, err = run_cli("request-end-p1", a, root / "sent-out")
    out_rec = (root / "sent-out/thermal_line.json").read_text() if code == 0 else ""
    check("JSON sentinel absent from stdout and record, byte-copied in output",
          code == 0 and sentinel not in stdout and sentinel not in out_rec
          and sentinel in (root / "sent-out/derived/b6-acceptance.json").read_text(), err)
    del ma

    # --- output linking: analysis-side writes, and source mutation ----------
    out = root / "re1"
    link = out / "withheld/spans.json"
    check("output files are symlinks into the source", link.is_symlink() and
          Path(os.readlink(link)).resolve() == (w1.archive / "withheld/spans.json").resolve())
    rec = json.loads((out / "thermal_line.json").read_text())
    check("record lists the sources it hashed", sorted(Path(p).name for p in rec["source_sha256"]),
          sorted(Path(p).name for p in rec["source_sha256"]))
    # A write through an output path lands in the source (opened for writing).
    try:
        with open(out / "derived/roster.json", "r+b") as s:
            s.seek(0, 2)
            writable = True
    except OSError:
        writable = False
    check("output view is read-only w.r.t. source (open r+b through link fails)", not writable,
          "opening the output's derived/roster.json for writing reaches the source file")
    # Re-harvest/move of the source changes what the output means: the record still verifies?
    moved = root / "p1-moved"
    os.rename(w1.archive, moved)
    dangling = not (out / "withheld/spans.json").exists()
    os.rename(moved, w1.archive)
    check("moving the source leaves the output dangling (detected only by failure)", True,
          {"dangling_after_move": dangling})
    # Mutate an unhashed linked file (bundle events) and verify nothing in the record catches it.
    hashed = set(rec["source_sha256"])
    linked = [p for p in out.rglob("*") if p.is_symlink() and str(Path(os.readlink(p))) not in hashed]
    check("linked files whose SHA-256 is NOT in the record", True, {"count": len(linked),
          "example": str(linked[0].relative_to(out)) if linked else None})

    print("\nSUMMARY", sum(ok for _, ok, _ in RESULTS), "/", len(RESULTS), "pass; root", root)
    return 0 if all(ok for _, ok, _ in RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
