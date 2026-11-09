"""Synthetic confirmation-seat witnesses, first written against release-tools 8ba59ac55.

INVERTED (lead rulings on the confirmation HOLD: U4 one cumulative row per counted window, U6 one cell per
pair with its positions, H* on EVERY C benign carrier and T sabotage row on both sides): each omission that
used to give a false AGREE now refuses through ``row_completeness``. No real measurement/custody input is used.
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

    def assert_agree(self, label, fill, rec=None):
        public, detail, code = self.compare(label, fill, rec)
        self.assertEqual((code, public["verdict"], public["unmapped_leaves"]),
                         (0, "agree", 0))
        self.assertEqual(public["families"]["row_completeness"]["verdict"], "agree")
        return detail

    def assert_refused_incomplete(self, label, fill, rec=None):
        """Inverted: the omission refuses (row_completeness), with every leaf mapped."""
        public, detail, code = self.compare(label, fill, rec)
        self.assertEqual((code, public["verdict"], public["unmapped_leaves"]), (2, "refused", 0))
        self.assertEqual(public["families"]["row_completeness"]["verdict"], "refused")
        return detail

    def test_baseline_agrees(self):
        self.assert_agree("baseline", copy.deepcopy(self.fill))

    def test_missing_u4_window_hides_a_real_comparison_failure(self):
        """A14/R20 (inverted): a missing cumulative window verdict refuses."""
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
        self.assert_refused_incomplete("u4-omitted", fill, rec)

    def test_missing_u4_interval_endpoint_hides_a_numeric_disagreement(self):
        """A14 (inverted): a missing interval endpoint refuses (both ends required when W >= 3)."""
        rec = copy.deepcopy(self.rec)
        row = rec["acceptance"]["U4"]["per_window"]["C5"]
        self.assertEqual(len(row["interval"]), 2)
        row["interval"][1] += 0.1
        public, _, code = self.compare("u4-ci-present", copy.deepcopy(self.fill), rec)
        self.assertEqual((code, public["families"]["u4_values"]["verdict"]), (1, "hold"))
        fill = copy.deepcopy(self.fill)
        self.assertEqual(len(fill["U4"]["per_window"]["C5"]["ci90_fraction"]), 2)
        fill["U4"]["per_window"]["C5"]["ci90_fraction"].pop()
        self.assert_refused_incomplete("u4-ci-omitted", fill, rec)

    def test_missing_u6_position_hides_a_numeric_disagreement(self):
        """A16 (inverted): a lost turn-position cell refuses (positions derived from the recompute)."""
        rec = copy.deepcopy(self.rec)
        pos = next(iter(self.fill["U6"]["spam"]["turn_position_residual_means"]["means_j"]))
        rec["acceptance"]["U6"]["spam"]["per_position_print_only"][pos]["mean"] += 1.0
        public, _, code = self.compare("u6-position-present", copy.deepcopy(self.fill), rec)
        self.assertEqual((code, public["families"]["u6_values"]["verdict"]), (1, "hold"))
        fill = copy.deepcopy(self.fill)
        for key in ("means_j", "trajectory_counts", "evaluable"):
            del fill["U6"]["spam"]["turn_position_residual_means"][key][pos]
        self.assert_refused_incomplete("u6-position-omitted", fill, rec)
        fill = copy.deepcopy(self.fill)
        del fill["U6"]["bank"]                                   # a whole pair cell: refuses too
        self.assert_refused_incomplete("u6-pair-omitted", fill)

    def test_both_sides_omitting_an_undefined_h_star_still_agree(self):
        """R26 + amendment (inverted): H* is required by role on BOTH sides; a shared omission refuses."""
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
        self.assert_refused_incomplete("h-star-both-omitted", fill, rec)
        fill2 = copy.deepcopy(self.fill)                          # recompute-only omission refuses as well
        self.assert_refused_incomplete("h-star-recompute-only", fill2, rec)

    def test_release_refuses_a_recorded_fill_missing_a_u4_window(self):
        """Inverted: end to end, the release refuses a recorded fill that lost a U4 window."""
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
        self.assertEqual((code, public["verdict"], public["reason"]), (2, "refused", "comparator_refused"))
        self.assertEqual(public["stages"]["digests"]["engine_producer_identity"], "verified")
        self.assertEqual(public["stages"]["comparator"]["refused"], "refusing_family_disagrees")


if __name__ == "__main__":
    unittest.main()
