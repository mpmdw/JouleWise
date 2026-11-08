"""Refusals on missing or malformed required inputs (exit 2, nothing written), and member-level
defects that exclude a member without refusing the run. Synthetic only."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from .support import SMALL, rc, run_cli, synth


class RefusalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name) / "base"
        synth.write_series(cls.base, windows=["C1", "T1"], **SMALL)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def copy(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "s"
        shutil.copytree(self.base, root)
        return root

    def refused(self, root, code):
        out = root.parent / "out.json"
        rc_, stdout, stderr = run_cli("--root", root, "--out", out, "--workers", 1)
        self.assertEqual(rc_, 2)
        self.assertEqual(json.loads(stderr), {"refused": code})
        self.assertEqual(stdout, "")
        self.assertFalse(out.exists())

    def test_missing_and_malformed_series(self):
        root = self.copy()
        (root / "series.json").unlink()
        self.refused(root, "series_missing")
        (root / "series.json").write_text("{not json")
        self.refused(root, "series_malformed")
        (root / "series.json").write_text(json.dumps({"windows": []}))
        self.refused(root, "series_malformed")
        (root / "series.json").write_text(json.dumps({"windows": [{"window_id": "C1", "role": "fit"}]}))
        self.refused(root, "series_malformed")

    def test_window_record_defects(self):
        root = self.copy()
        path = root / "windows/C1/window.json"
        record = json.loads(path.read_text())
        path.unlink()
        self.refused(root, "window_missing")
        bad = dict(record, role="test")
        path.write_text(json.dumps(bad))
        self.refused(root, "window_malformed")
        dup = dict(record, members=record["members"] + [dict(record["members"][0], ordinal=99)])
        path.write_text(json.dumps(dup))
        self.refused(root, "window_malformed")
        odd = dict(record, members=[dict(record["members"][0], kind="fit")] + record["members"][1:])
        path.write_text(json.dumps(odd))
        self.refused(root, "window_malformed")
        noadj = {k: v for k, v in record.items() if k != "adjudication"}
        path.write_text(json.dumps(noadj))
        self.refused(root, "window_malformed")
        path.write_text(json.dumps(record))
        u3 = root / "u3_bar.json"
        u3.write_text("[")
        self.refused(root, "u3_bar_malformed")

    def test_member_defects_exclude_without_refusing(self):
        root = self.copy()
        members = root / "windows/C1/members"
        # e06: episode malformed (a turn index out of order)
        ep_path = members / "align-v4-c1-e06/outputs/align_episode.json"
        ep = json.loads(ep_path.read_text())
        ep["turns"][0]["index"] = 5
        ep_path.write_text(json.dumps(ep))
        # e07: raw plist missing; e08: truncated last frame; e10: no clock anchor; e11: PM ends early
        (members / "align-v4-c1-e07/raw/powermetrics.plist").unlink()
        raw = members / "align-v4-c1-e08/raw/powermetrics.plist"
        raw.write_bytes(raw.read_bytes() + b"<?xml version")
        meta = members / "align-v4-c1-e10/metadata.json"
        meta.write_text(json.dumps({"sampling": {"power_period_ns": 10**10}}))   # no clock anchor
        raw = members / "align-v4-c1-e11/raw/powermetrics.plist"
        frames = raw.read_bytes().split(b"\x00")
        raw.write_bytes(b"\x00".join(frames[: len(frames) // 3]) + b"\x00")
        # e12: never captured
        shutil.rmtree(members / "align-v4-c1-e12")
        out = rc.recompute(root, workers=1)
        flags = {rid: m["flags"] for rid, m in out["members"]["C1"].items()}
        self.assertEqual(flags["align-v4-c1-e06"], ["episode_malformed"])
        self.assertEqual(flags["align-v4-c1-e07"], ["pm_raw_missing"])
        self.assertEqual(flags["align-v4-c1-e08"], ["pm_unreadable"])
        self.assertEqual(flags["align-v4-c1-e10"], ["clock_anchor_missing"])
        self.assertIn("pm_turn_span_uncovered", flags["align-v4-c1-e11"])
        excl = out["exclusions"]["C1"]
        for rid in ("e06", "e07", "e08", "e10", "e11"):
            self.assertIn("energy_unavailable", excl["align-v4-c1-" + rid]["classes"], rid)
            self.assertFalse(excl["align-v4-c1-" + rid]["eligible"])
        self.assertEqual(excl["align-v4-c1-e12"]["classes"], ["not_captured"])
        # e11's truncated PM is a U1(c) PM gap: the D model-window fails U1, so C1 is barred and, under
        # R21 A24, never fitted or scored; it still counts toward the 8 with zero calibrators.
        self.assertFalse(out["acceptance"]["U1"]["C1"]["D"]["parts"]["c_pm_gaps"])
        self.assertNotIn("C1", out["fits"])
        row = out["calibration"]["stop"]["windows"][0]
        self.assertEqual((row["counted"], row["pool_barred"], row["eligible_benign"]), (True, True, {"bank": 0, "spam": 0}))


if __name__ == "__main__":
    unittest.main()
