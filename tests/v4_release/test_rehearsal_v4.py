"""Synthetic full-series rehearsal (RUN_STATE 230 "Next"): engine against recompute on one common series.

Series: W1, C1-C8 with C3's first attempt a zero-capture refusal retried in the same slot, T1-T3 with T3
escalated to 24 members (R20 ordinals 23/24). Planted CODE mutations in each build (a patched copy of the
pinned tree, never the build's branch) must turn a named comparator family away from agree.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import support  # noqa: E402


@unittest.skipUnless(support.have_commits(), "pinned build commits unavailable in this clone")
class RehearsalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = support.rehearsal("full")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_series_shape(self):
        cross = json.loads((self.full / "crosswalk.json").read_text())["members"]
        attempts = {m["attempt_id"] for m in cross}
        self.assertEqual(len({m["window"] for m in cross}), 12)          # W1 + 11
        for w in ("C3", "T2"):
            self.assertIn(w + "#1", attempts)
            self.assertIn(w + "#2", attempts)
            self.assertFalse(any(m["captured"] for m in cross if m["attempt_id"] == w + "#1"))
        self.assertFalse(any(m["captured"] for m in cross if m["attempt_id"] == "C3#1"))
        self.assertEqual(sum(1 for m in cross if m["attempt_id"] == "T3#1"), 24)

    def test_recompute_handles_the_zero_capture_retry(self):
        self.assertEqual(json.loads((self.full / "timings.json").read_text())["recompute_exit"], 0)
        rec = json.loads((self.full / "recompute-out.json").read_text())
        stop = rec["calibration"]["stop"]
        self.assertEqual((stop["counted_windows"], stop["status"]), (8, "calibration_complete"))
        self.assertTrue(any(not w["counted"] and w["final"] for w in stop["windows"]))

    def test_engine_runs_the_full_series(self):
        # E1 (fixed in engine-r23): a zero-capture window no longer refuses the whole analysis.
        self.assertEqual(json.loads((self.full / "engine-exit.json").read_text())["exit"], 0)

    def test_a37_seam_fixture_has_both_sides_of_the_bar(self):
        seams = json.loads((self.full / "seams.json").read_text())
        self.assertGreater(seams["C5#1"]["gap_le_1us"] + seams["C5#1"]["overlap_le_1us"], 0)
        self.assertEqual(seams["C5#1"]["gap_gt_1us"] + seams["C5#1"]["overlap_gt_1us"], 0)
        self.assertNotIn("C6#1", seams)
        probe = json.loads((support.rehearsal("probes") / "seams.json").read_text())
        self.assertGreater(probe["C6#1"]["gap_gt_1us"], 0)
        self.assertEqual(probe["C6#1"]["gap_le_1us"] + probe["C6#1"]["overlap_le_1us"], 0)

    def test_probe_series_holds_only_on_the_classified_findings(self):
        # The probe plan adds a G1 timeout to W1 anchor 2 and > 1 us A37 seams to C6 (RELEASE-RUNBOOK-v4
        # section 6, P1 and P2). Each is a classified cross-build hold, so this series must not agree.
        probes = support.rehearsal("probes")
        self.assertEqual(json.loads((probes / "engine-exit.json").read_text())["exit"], 0)
        code, pub, res = support.compare(probes, self.dir / "probes.json")
        self.assertEqual((code, pub["verdict"], pub["reason"]), (2, "refused", "refusing_family_disagrees"))
        self.assertEqual(pub["unmapped_leaves"], 0)
        fails = [r for r in res["rows"] if not r["ok"]]
        self.assertIn(["W1", "30B", "thermal_excluded_members"], [r["key"] for r in fails])      # P1
        self.assertIn("W1_anchor_block", [r["key"] for r in fails])                                # P1
        self.assertTrue(any(r["family"] == "member_eligibility" and r["key"][0] == "C6#1" for r in fails))  # P2

    def _patched(self, commit, rel, old, new):
        src = support.tree(commit)
        dest = self.dir / f"tree-{commit[:7]}-{abs(hash(rel + new)) % 10**6}"
        shutil.copytree(src, dest)
        p = dest / rel
        text = p.read_text()
        self.assertEqual(text.count(old), 1, (rel, old))
        p.write_text(text.replace(old, new))
        return dest

    def _custody(self, name):
        dest = self.dir / name
        shutil.copytree(self.full, dest, ignore=shutil.ignore_patterns("recompute-out.json", "engine-out*"),
                        copy_function=os.link)   # hard links; nothing below writes through them
        return dest

    def test_recompute_code_mutation_disagrees(self):
        tree = self._patched(support.RECOMPUTE_COMMIT, "scripts/independent_recompute_v4.py",
                             "rng = random.Random(0)", "rng = random.Random(1)")
        c = self._custody("mut-rec")
        (c / "engine-out").symlink_to(self.full / "engine-out")
        self.assertEqual(support.run_recompute(c, tree_dir=tree), 0)
        code, pub, _ = support.compare(c, self.dir / "mut-rec.json")
        self.assertEqual(pub["families"]["carrier_bootstrap"]["verdict"], "hold")

    def test_engine_code_mutation_disagrees(self):
        tree = self._patched(support.ENGINE_COMMIT, "joulewise/align/v4_analysis/acceptance.py",
                             "beta = .025 if heavy else .05", "beta = .025 if heavy else .04")
        c = self._custody("mut-eng")
        shutil.copy2(self.full / "recompute-out.json", c / "recompute-out.json")
        code, verdict = support.run_engine(c, tree_dir=tree)
        self.assertEqual(code, 0)
        code, pub, _ = support.compare(c, self.dir / "mut-eng.json")
        self.assertEqual(pub["families"]["u3_bar"]["verdict"], "hold")
        self.assertEqual(pub["families"]["u3_bar_values"]["verdict"], "hold")


if __name__ == "__main__":
    unittest.main()
