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
        # Permanent large-epoch windows (lead ruling on P2): C7 at 4.3e9 s stays <= 1 us, C6 at 9e9 s > 1 us.
        self.assertEqual(seams["C7#1"]["gap_gt_1us"] + seams["C7#1"]["overlap_gt_1us"], 0)
        self.assertEqual(seams["C7#1"]["max_abs_seam_ns"], 954)
        self.assertGreater(seams["C6#1"]["gap_gt_1us"], 0)
        self.assertEqual(seams["C6#1"]["gap_le_1us"] + seams["C6#1"]["overlap_le_1us"], 0)

    def test_probe_series_agrees(self):
        # The probe plan swaps W1 anchor 2's B code for a G1 timeout that stops its episode (lead ruling on P1:
        # X2 is re-derived, A9 union). Both builds must exclude it: W1_anchor_block "excluded:X2" (K = 10 with C6).
        probes = support.rehearsal("probes")
        self.assertEqual(json.loads((probes / "engine-exit.json").read_text())["exit"], 0)
        code, pub, res = support.compare(probes, self.dir / "probes.json")
        self.assertEqual((code, pub["verdict"], pub["unmapped_leaves"]), (0, "agree", 0))
        rec = json.loads((probes / "recompute-out.json").read_text())
        self.assertEqual(rec["acceptance"]["U4"]["anchor_sigma_w_print_only"]["W1_anchor_block"], "excluded:X2")

    def test_owned_time_and_large_epoch_fixtures(self):
        # A2(4) at owned-time level and the permanent large-epoch A37 windows (lead rulings, 2026-11-08).
        rec = json.loads((self.full / "recompute-out.json").read_text())
        ex = rec["exclusions"]
        self.assertEqual(ex["W1"]["align-v4-w1-episodes-e08"]["classes"], ["energy_unavailable"])   # edge partial
        self.assertTrue(ex["C8"]["align-v4-c8-episodes-b-e12"]["eligible"])                       # gate-only seams
        self.assertFalse(rec["members"]["C8"]["align-v4-c8-episodes-b-e12"]["pm"]["episode_covered"])  # disclosed
        self.assertTrue(all(not e.get("eligible") for e in ex["C6"].values()))                     # > 1 us seams
        self.assertTrue(any(e.get("eligible") for e in ex["C7"].values()))                         # 954 ns snapped
        self.assertEqual(rec["acceptance"]["U4"]["anchor_sigma_w_print_only"]["W1_anchor_block"], "excluded:B")

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
