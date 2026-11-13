"""S-16 row E (scripts/b6_s16_block5_pstar.py): the read adapter and the replay, on synthetic Block 5 roots.

The pinned desk function is used when the pinned commit is in this clone; otherwise those tests skip and a stub
with the same interface checks the adapter.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("b6_s16_block5_pstar", ROOT / "scripts" / "b6_s16_block5_pstar.py")
ps = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = ps
_SPEC.loader.exec_module(ps)

PLANS = {"alpha": "v5-b5-alpha-a1-20261009T2312Z", "beta": "v5-b5-beta-a6-20261011T2011Z",
         "gamma": "v5-b5-gamma-a1-20261012T0420Z"}


def has_pinned_commit() -> bool:
    r = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{ps.PINNED_COMMIT}^{{commit}}"],
                       capture_output=True)
    return r.returncode == 0


def idle_plist(gpu_mw: float, ane_mw: float = 0.0, frames: int = 3) -> bytes:
    rows = [plistlib.dumps({"elapsed_ns": 100_000_000, "processor": {"gpu_power": gpu_mw, "ane_power": ane_mw}})
            for _ in range(frames)]
    return b"\0".join(rows) + b"\0"


def make_root(tmp: Path, pack: str, idle_mw: dict[str, float], *, aux: int = 1) -> Path:
    plan_id = PLANS[pack]
    root = tmp / f"harvest-{plan_id}"
    sources = root / "sources"
    members, spans, sums = [], {}, {}
    t = 1_000_000_000
    for i, (rid, mw) in enumerate(idle_mw.items()):
        phase = "decode" if i % 2 == 0 else "prefill-p2048"
        members.append({"kind": "science", "run_id": rid,
                        "units": [{"cell_id": f"df-ph-{phase}-x", "stratum": "a", "unit_id": f"u{i}"}]})
        bundle = sources / "claim-runs" / rid
        (bundle / "raw").mkdir(parents=True)
        files = {
            "metadata.json": json.dumps({"model": {"name": "Qwen3-8B-4bit"}, "energy_j": 999}).encode(),
            "summary_metrics.json": json.dumps({"status": "succeeded", "phase_energy_j": {"decode": 123}}).encode(),
            "raw/powermetrics_idle.plist": idle_plist(mw),
        }
        for rel, data in files.items():
            (bundle / rel).write_bytes(data)
            sums[f"claim-runs/{rid}/{rel}"] = hashlib.sha256(data).hexdigest()
        spans[rid] = {"member": [t, t + 9_000_000_000], "request": [t + 1_000_000_000, t + 3_000_000_000]}
        t += 10_000_000_000
    for j in range(aux):
        members.append({"kind": "auxiliary", "run_id": f"neg8-ref-{j}", "units": []})
    journal = [{"schema": "joulewise.hazard_journal.v1", "module": "contention", "kind": "session_start"}]
    start = 0
    while start < t + 10_000_000_000:
        journal.append({"schema": "joulewise.hazard_journal.v1", "module": "contention", "kind": "interval",
                        "error": None, "values": {"interval": {"monotonic_ns": [start, start + 10_000_000_000]},
                                                  "outside_total_cpu_s_per_s": 0.05}})
        start += 10_000_000_000
    jbytes = "".join(json.dumps(r) + "\n" for r in journal).encode()
    jpath = root / ps.CONTENTION_JOURNAL
    jpath.parent.mkdir(parents=True, exist_ok=True)
    jpath.write_bytes(jbytes)
    sums[ps.CONTENTION_JOURNAL[len("sources/"):]] = hashlib.sha256(jbytes).hexdigest()
    (sources / "SHA256SUMS").write_text("".join(f"{d}  {rel}\n" for rel, d in sorted(sums.items())))
    (root / "derived").mkdir(parents=True)
    (root / "derived/roster.json").write_text(json.dumps({"plan_id": plan_id, "members": members}))
    (root / "withheld").mkdir()
    (root / "withheld/spans.json").write_text(json.dumps({"schema": "x", "spans": spans}))
    return root


class StubRefusal(ValueError):
    pass


def stub_desk(session, sizing):
    """Same read pattern as the pinned function; records what the adapter handed it."""
    r = session.reader
    spans = r.json(session.archive / "withheld/spans.json", "spans")["spans"]
    r.lines(session.archive / session.input_pin["contention_journal"], "contention_journal")
    records, removed = {}, []
    for m in session.roster["members"]:
        if m.get("kind") != "science":
            continue
        rid = m["run_id"]
        root = session.claim_root / rid
        meta = r.json(root / "metadata.json", rid)
        summ = r.json(root / "summary_metrics.json", rid)
        assert set(meta) == {"model"} and set(summ) == {"status"}, (meta, summ)
        assert set(spans[rid]) == {"request"}
        px = sum(plistlib.loads(f)["processor"]["gpu_power"] for f in r.raw(root / "raw/powermetrics_idle.plist", rid)
                 .split(b"\0") if f.strip()) / 3 / 1000.
        line = 0.0723
        records[rid] = {"P_x_w": px, "P_star_w": line, "per_model_would_remove": px >= line}
        if px >= line:
            removed.append(rid)
    return {"records": records, "power_removed": removed}


class Adapter(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def roots(self, gamma_hot: float = 1.0) -> list[Path]:
        return [make_root(self.tmp, "alpha", {"a0": 1.0, "a1": 2.0}),
                make_root(self.tmp, "beta", {"b0": 1.5}),
                make_root(self.tmp, "gamma", {"g0": gamma_hot, "g1": 0.5})]

    def test_counts_and_sentence(self) -> None:
        out = ps.replay(self.roots(gamma_hot=80.0), stub_desk, StubRefusal, {}, pinned=False)
        self.assertEqual(out["runs"], 3 + 2 + 3)
        self.assertEqual(out["science_runs_examined"], 5)
        self.assertEqual(out["removed_by_pack"], {"alpha": 0, "beta": 0, "gamma": 1})
        self.assertEqual(out["sentence"], "removes 1 of 8 runs (0, 0, 1); largest baseline mean 80.00 mW against "
                                          "the lowest line 0.0723 W")

    def test_tampered_source_refuses(self) -> None:
        roots = self.roots()
        (roots[0] / "sources/claim-runs/a0/raw/powermetrics_idle.plist").write_bytes(idle_plist(0.0))
        with self.assertRaisesRegex(ps.Refusal, "source_digest_mismatch"):
            ps.replay(roots, stub_desk, StubRefusal, {}, pinned=False)

    def test_pinned_mode_refuses_synthetic_roots(self) -> None:
        with self.assertRaisesRegex(ps.Refusal, "session_input_digest_mismatch"):
            ps.replay(self.roots(), stub_desk, StubRefusal, {}, pinned=True)

    def test_function_refusal_is_a_stop(self) -> None:
        def refusing(session, sizing):
            raise StubRefusal("contention_request_uncovered")
        with self.assertRaisesRegex(ps.Refusal, "STOP: pinned desk function refused .*contention_request_uncovered"):
            ps.replay(self.roots(), refusing, StubRefusal, {}, pinned=False)

    def test_adapter_refuses_unexpected_reads(self) -> None:
        session = ps.session_for(self.roots()[0], pinned=False)
        (session.archive / "derived/exclusions.json").write_text("{}")
        with self.assertRaisesRegex(ps.Refusal, "unexpected_raw_read"):
            session.reader.raw(session.claim_root / "a0/raw/powermetrics.plist", "a0")
        with self.assertRaisesRegex(ps.Refusal, "unexpected_json_read"):
            session.reader.json(session.archive / "derived/exclusions.json", "x")


@unittest.skipUnless(has_pinned_commit(), "pinned commit not in this clone")
class PinnedFunction(unittest.TestCase):
    def test_pinned_desk_function_reads_a_block5_shaped_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            roots = [make_root(tmp, "alpha", {"a0": 300.0, "a1": 1.0}),
                     make_root(tmp, "beta", {"b0": 1.0}),
                     make_root(tmp, "gamma", {"g0": 1.0})]
            code = subprocess.run(
                [sys.executable, "-B", str(ROOT / "scripts/b6_s16_block5_pstar.py"), "--unpinned",
                 "--json-out", str(tmp / "out.json")] + [a for r in roots for a in ("--session", str(r))],
                capture_output=True, text=True)
            self.assertEqual(code.returncode, 0, code.stderr)
            out = json.loads((tmp / "out.json").read_text())
            # ALPHA decode line: 1.9 / (4 x 1.9957762 s) = 0.238 W; a0 (300 mW, a decode run) is removed.
            self.assertEqual(out["removed_by_pack"], {"alpha": 1, "beta": 0, "gamma": 0})
            self.assertEqual(out["desk_sha256"], ps.DESK_SHA256)


if __name__ == "__main__":
    unittest.main()
