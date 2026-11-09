"""Synthetic confirmation-seat witnesses for release-tools 8ba59ac55.

These are observational review witnesses: the omission tests deliberately assert
the current false AGREE. Convert them to rejection tests when the lead fixes the
coverage gap. No real measurement/custody input is used.
"""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from tests.v4_release import support

sys.path.insert(0, str(support.REPO / "scripts"))
import compare_v4_recompute as comparator
import release_v4 as release


@unittest.skipUnless(support.have_commits(), "pinned build objects unavailable")
class RemainingCoverageWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = support.rehearsal("full")
        cls.tmp = tempfile.TemporaryDirectory(prefix="jw-v4-confirm-sol-")
        cls.root = Path(cls.tmp.name)
        cls.fill = json.loads((cls.base / "engine-out/fill.json").read_text())
        cls.rec = json.loads((cls.base / "recompute-out.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def compare(self, label, fill, rec=None):
        # An internally consistent inventory is not an independent row manifest.
        self.inventory(fill)
        fp = self.root / (label + "-fill.json")
        fp.write_text(json.dumps(fill))
        rp = self.base / "recompute-out.json"
        if rec is not None:
            rp = self.root / (label + "-rec.json")
            rp.write_text(json.dumps(rec))
        return comparator.compare(fp, self.base / "engine-out/verdict.json", rp,
                                  self.base / "crosswalk.json", release.RELEASE_BARS,
                                  identity_path=support.engine_identity_file())

    @staticmethod
    def inventory(fill):
        body = {k: v for k, v in fill.items() if k != "leaf_inventory"}
        fill["leaf_inventory"] = [
            dict(pointer=p, kind="null" if v is None else "bool" if type(v) is bool
                 else "number" if type(v) in (int, float) else "string")
            for p, v in comparator.leaves(body).items()
        ]

    def assert_false_agree(self, label, fill, rec=None):
        public, detail, code = self.compare(label, fill, rec)
        self.assertEqual((code, public["verdict"], public["unmapped_leaves"]),
                         (0, "agree", 0))
        self.assertEqual(public["families"]["row_completeness"]["verdict"], "agree")
        return detail

    def test_baseline_agrees(self):
        self.assert_false_agree("baseline", copy.deepcopy(self.fill))

    def test_missing_u4_window_hides_a_real_comparison_failure(self):
        """A14/R20: a missing cumulative window verdict escapes the new manifest."""
        rec = copy.deepcopy(self.rec)
        self.assertIn("C5", self.fill["U4"]["per_window"])
        row = rec["acceptance"]["U4"]["per_window"]["C5"]
        self.assertNotEqual(row.get("status"), "skipped")
        self.assertGreaterEqual(row["W"], 3)
        row["verdict"] = "fail" if row["verdict"] != "fail" else "pass"
        public, _, code = self.compare("u4-present", copy.deepcopy(self.fill), rec)
        self.assertEqual((code, public["families"]["u4"]["verdict"]), (1, "hold"))
        fill = copy.deepcopy(self.fill)
        del fill["U4"]["per_window"]["C5"]
        self.assert_false_agree("u4-omitted", fill, rec)

    def test_missing_u4_interval_endpoint_hides_a_numeric_disagreement(self):
        """A14: the interval is compared by iterating its printed prefix only."""
        rec = copy.deepcopy(self.rec)
        row = rec["acceptance"]["U4"]["per_window"]["C5"]
        self.assertEqual(len(row["interval"]), 2)
        row["interval"][1] += 0.1
        public, _, code = self.compare("u4-ci-present", copy.deepcopy(self.fill), rec)
        self.assertEqual((code, public["families"]["u4_values"]["verdict"]), (1, "hold"))
        fill = copy.deepcopy(self.fill)
        self.assertEqual(len(fill["U4"]["per_window"]["C5"]["ci90_fraction"]), 2)
        fill["U4"]["per_window"]["C5"]["ci90_fraction"].pop()
        self.assert_false_agree("u4-ci-omitted", fill, rec)

    def test_missing_u6_position_hides_a_numeric_disagreement(self):
        """A16: a lost turn-position cell does not change the pair-level unit count."""
        rec = copy.deepcopy(self.rec)
        pos = next(iter(self.fill["U6"]["spam"]["turn_position_residual_means"]["means_j"]))
        rec["acceptance"]["U6"]["spam"]["per_position_print_only"][pos]["mean"] += 1.0
        public, _, code = self.compare("u6-position-present", copy.deepcopy(self.fill), rec)
        self.assertEqual((code, public["families"]["u6_values"]["verdict"]), (1, "hold"))
        fill = copy.deepcopy(self.fill)
        for key in ("means_j", "trajectory_counts", "evaluable"):
            del fill["U6"]["spam"]["turn_position_residual_means"][key][pos]
        self.assert_false_agree("u6-position-omitted", fill, rec)

    def test_both_sides_omitting_an_undefined_h_star_still_agree(self):
        """R26: required H* presence is inferred from the recompute's printout."""
        fill, rec = copy.deepcopy(self.fill), copy.deepcopy(self.rec)
        fit, score = next(
            (fit, score) for fit in fill["fits"]
            if fit["window"].startswith("C") and fit["convention"] == "counts_logged"
            for score in fit["scores"]
            if score.get("H_star", {}).get("undefined_missing_grid_doses")
        )
        self.assertIsNone(score["H_star"]["h_star"])
        pair = comparator.PAIR_SHORT[fit["pair"]]
        carrier = next(c for c in rec["claim"]["carrier_curve"][pair]["carriers"]
                       if c["run_id"] == score["run_id"] and c["window_id"] == fit["window"])
        self.assertIsNone(carrier["h_star"]["h_star"])
        del score["H_star"]
        public, _, code = self.compare("h-star-engine-only", copy.deepcopy(fill), rec)
        self.assertEqual((code, public["families"]["row_completeness"]["verdict"]), (2, "refused"))
        del carrier["h_star"]
        self.assert_false_agree("h-star-both-omitted", fill, rec)

    def test_release_accepts_a_recorded_fill_missing_a_u4_window(self):
        """The wrapper's digest/producer checks do not repair the missing row."""
        custody = self.root / "omitted-u4-custody"
        shutil.copytree(self.base, custody, copy_function=os.link)
        fill = copy.deepcopy(self.fill)
        del fill["U4"]["per_window"]["C5"]
        self.inventory(fill)
        fp = custody / "engine-out/fill.json"
        fp.unlink()  # never change the immutable synthetic fixture's inode
        fp.write_text(json.dumps(fill))
        (custody / "engine-run-record.json").unlink()
        support.write_record(custody)
        checkout = support.release_checkout(self.root / "release-checkout")
        code, public, _ = support.run_release(checkout, custody, self.root / "synthetic-private")
        self.assertEqual((code, public["verdict"]), (0, "agree"))
        self.assertEqual(public["stages"]["digests"]["engine_producer_identity"], "verified")
        self.assertEqual(public["stages"]["comparator"]["unmapped_leaves"], 0)


if __name__ == "__main__":
    unittest.main()
