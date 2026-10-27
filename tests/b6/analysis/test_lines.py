"""A3 to A5: §10's summary, §11.1's table, §11.2's word and §11.4's admission.

The worked examples are the registration's own synthetic numbers.
"""
from __future__ import annotations

import unittest

from joulewise.b6.analysis import inclusive, replication, summary
from joulewise.b6.analysis.adapter import SessionAnalysis
from joulewise.b6.analysis.census import census_from_state
from tests.b6.analysis.fakes import attempt_line

RULES = {"not_registered_experiment": {"W1": ["model.files_differ_from_registered"],
                                       "W2": ["model.stack_differs_from_registered"],
                                       "W3": ["code.number_bearing_unreviewed"],
                                       "S1": ["structure.chain_crashed"]},
         "minimum_kept_units_per_stratum": 5}


def session(session_id, pack="alpha", **quantities):
    return SessionAnalysis(session_id, pack, "ok", b_op_defined=True, drift_screen="passed", quantities=quantities)


def gamma(session_id, outcome, dbar):
    return SessionAnalysis(session_id, "gamma", "ok", b_op_defined=True, drift_screen="passed",
                           contrasts={"decode": {"outcome": outcome, "dbar": dbar}})


class BetweenSessionSummary(unittest.TestCase):
    Q = "reported/qwen3-1p7b/prefill-p2048/mean_j"

    def test_registration_worked_example(self):
        """§10: 26.10 (block 5), 26.31, 25.97, 26.22: n 4, mean 26.15, sd 0.148."""
        b5 = session("block5", **{self.Q: 26.10})
        b6 = [session("s1", **{self.Q: 26.31}), session("s2", **{self.Q: 25.97}), session("s3", **{self.Q: 26.22})]
        row = summary.pack_summary(b5, b6)["quantities"][self.Q]
        self.assertEqual(row["n"], 4)
        self.assertEqual(row["sessions"], ["block5", "s1", "s2", "s3"])
        self.assertAlmostEqual(row["mean"], 26.15, places=12)
        self.assertEqual(round(row["sd"], 3), 0.148)

    def test_flagged_inclusive_worked_example(self):
        """§10: a fourth, non-counting block-6 session at 26.48: n 5, mean 26.216, sd 0.195."""
        b5 = session("block5", **{self.Q: 26.10})
        b6 = [session(s, **{self.Q: v}) for s, v in (("s1", 26.31), ("s2", 25.97), ("s3", 26.22), ("s4", 26.48))]
        row = summary.pack_summary(b5, b6)["quantities"][self.Q]
        self.assertEqual(row["n"], 5)
        self.assertAlmostEqual(row["mean"], 26.216, places=12)
        self.assertEqual(round(row["sd"], 3), 0.195)

    def test_side_by_side_worked_example(self):
        """§11.1: block-6 mean 26.1667, delta +0.0667, own differences +0.21, -0.13, +0.12."""
        b5 = session("block5", **{self.Q: 26.10})
        b6 = [session("s1", **{self.Q: 26.31}), session("s2", **{self.Q: 25.97}), session("s3", **{self.Q: 26.22})]
        row = summary.side_by_side(b5, b6)["quantities"][self.Q]
        self.assertAlmostEqual(row["block6_mean"], 26.166666666666668, places=12)
        self.assertAlmostEqual(row["delta"], 0.0667, places=4)
        self.assertEqual({k: round(v, 2) for k, v in row["session_differences"].items()},
                         {"s1": 0.21, "s2": -0.13, "s3": 0.12})

    def test_only_mean_and_sd_no_ratio_no_interval(self):
        row = summary.describe([("a", 1.0, None), ("b", 3.0, None)])
        self.assertEqual(set(row), {"n", "sessions", "missing", "block5", "mean", "sd", "note"})
        self.assertEqual((row["mean"], row["sd"]), (2.0, 2.0 ** 0.5))

    def test_a_session_not_computable_is_left_out_and_named(self):
        """Design §10 edge case (lead ruling of 2026-10-27)."""
        row = summary.describe([("block5", 1.0, None), ("s1", None, "not_estimable"), ("s2", 2.0, None),
                                ("s3", float("nan"), "value_undefined")])
        self.assertEqual((row["n"], row["sessions"], row["mean"]), (2, ["block5", "s2"], 1.5))
        self.assertEqual(row["missing"], [{"session": "s1", "reason": "not_estimable"},
                                          {"session": "s3", "reason": "value_undefined"}])
        self.assertEqual((row["note"], row["block5"]), (None, None))

    def test_one_value_gives_the_value_and_an_undefined_deviation(self):
        """Design §10: n = 1 gives Q̄ = Q_1 and s_Q "not defined (n = 1)"."""
        row = summary.describe([("block5", 26.10, None), ("s1", None, "not_estimable")])
        self.assertEqual((row["n"], row["mean"], row["sd"], row["note"]), (1, 26.10, None, "not defined (n = 1)"))

    def test_no_value_is_not_computable(self):
        row = summary.describe([("block5", None, "not_estimable"), ("s1", None, "value_undefined")])
        self.assertEqual((row["n"], row["mean"], row["sd"], row["note"]), (0, None, None, "not computable (n = 0)"))

    def test_block5_not_computed_counts_block6_sessions_only(self):
        row = summary.describe([("block5", None, "quantity_absent"), ("s1", 58.71, None), ("s2", 57.96, None)])
        self.assertEqual((row["n"], row["sessions"], row["block5"]), (2, ["s1", "s2"], "block 5: not computed"))

    def test_design_worked_examples(self):
        """Design §10 (synthetic): BETA prefill 58.475 / 0.388 J; per token 0.02855225 / 0.00018955 J;
        dbar 3.000 / 0.155 J; R 3.785 / 0.211 (bar B2: half a unit of the last printed digit)."""
        cases = (((58.40, 58.71, 57.96, 58.83), 58.475, 0.388, 3),
                 ((58.40 / 2048, 58.71 / 2048, 57.96 / 2048, 58.83 / 2048), 0.02855225, 0.00018955, 8),
                 ((3.00, 2.84, 3.21, 2.95), 3.000, 0.155, 3),
                 ((3.84, 3.51, 4.02, 3.77), 3.785, 0.211, 3))
        for values, mean, sd, places in cases:
            row = summary.describe([(f"s{i}", v, None) for i, v in enumerate(values)])
            self.assertLessEqual(abs(row["mean"] - mean), 0.5 * 10 ** -places)
            self.assertLessEqual(abs(row["sd"] - sd), 0.5 * 10 ** -places)

    def test_the_reason_comes_from_the_session(self):
        b5 = gamma("block5", "direction_supported", 3.0)
        s1 = gamma("s1", "not_estimable", None)
        s2 = gamma("s2", "direction_supported", 2.0)
        s3 = SessionAnalysis("s3", "gamma", "ok", contrasts={"decode": {"outcome": "x", "dbar": 1.0}},
                             quantities={"q": None}, reasons={"q": "cell_below_minimum"})
        row = summary.pack_summary(b5, [s1, s2, s3])["quantities"]["contrast/decode/dbar_j"]
        self.assertEqual((row["n"], row["missing"]), (3, [{"session": "s1", "reason": "not_estimable"}]))
        q = summary.pack_summary(b5, [s1, s2, s3])["quantities"]["q"]
        self.assertEqual(q["missing"][-1], {"session": "s3", "reason": "cell_below_minimum"})
        self.assertEqual(q["missing"][0], {"session": "block5", "reason": "quantity_absent"})

    def test_side_by_side_over_the_sessions_with_a_value(self):
        b5 = session("block5", **{self.Q: 26.10})
        b6 = [session("s1", **{self.Q: 26.31}), session("s2", **{self.Q: None}), session("s3", **{self.Q: 26.21})]
        row = summary.side_by_side(b5, b6)["quantities"][self.Q]
        self.assertEqual(row["block6_n"], 2)
        self.assertAlmostEqual(row["block6_mean"], 26.26, places=12)
        self.assertEqual(row["block6_missing"], [{"session": "s2", "reason": "value_undefined"}])

    def test_contrast_dbar_is_a_summarised_quantity(self):
        b5, s1 = gamma("block5", "direction_supported", 3.0), gamma("s1", "direction_supported", 2.0)
        row = summary.pack_summary(b5, [s1])["quantities"]["contrast/decode/dbar_j"]
        self.assertEqual((row["n"], row["mean"]), (2, 2.5))

    def test_no_pooling_each_session_contributes_one_value(self):
        # The summary sees one value per session, whatever its run counts.
        b5 = session("block5", **{self.Q: 1.0})
        sessions = [session(f"s{i}", **{self.Q: float(i)}) for i in range(1, 4)]
        row = summary.pack_summary(b5, sessions)["quantities"][self.Q]
        self.assertEqual(row["n"], 4)


class ReplicationWord(unittest.TestCase):
    def word(self, b5, sessions, **kwargs):
        kwargs.setdefault("target", 3)
        return replication.contrast_word("decode", b5, sessions, **kwargs)

    def test_registration_worked_example(self):
        b5 = gamma("block5", "direction_supported", 3.0)
        two = [gamma("s1", "direction_supported", 2.8), gamma("s2", "direction_supported", 3.3)]
        self.assertEqual(self.word(b5, two, target=2)["word"], "replicated")
        three = two + [gamma("s3", "unresolved", 0.9)]
        record = self.word(b5, three)
        self.assertEqual(record["word"], "not replicated")
        self.assertEqual([(r["outcome"], r["sign"]) for r in record["sessions"]],
                         [("direction_supported", 1), ("direction_supported", 1), ("unresolved", 1)])

    def test_a_sign_change_is_not_replicated(self):
        b5 = gamma("block5", "unresolved", 0.4)
        record = self.word(b5, [gamma("s1", "unresolved", 0.3), gamma("s2", "unresolved", -0.1),
                                gamma("s3", "unresolved", 0.2)])
        self.assertEqual(record["word"], "not replicated")

    def test_block5_not_estimable_permits_no_word(self):
        for outcome, dbar in (("not_estimable", None), ("not_estimable", 1.0), ("direction_supported", None)):
            record = self.word(gamma("block5", outcome, dbar), [gamma("s1", "not_estimable", None)])
            self.assertIsNone(record["word"])
            self.assertEqual(record["reason"], "block5_not_estimable")

    def test_short_pack_says_so(self):
        b5 = gamma("block5", "direction_supported", 3.0)
        record = self.word(b5, [gamma("s1", "direction_supported", 2.0)])
        self.assertEqual(record["short"], "short: 1 counting block-6 sessions of the 3 targeted; below the commitment of 2")
        two = self.word(b5, [gamma("s1", "direction_supported", 2.0), gamma("s2", "direction_supported", 2.5)])
        self.assertEqual(two["short"], "short: 2 counting block-6 sessions of the 3 targeted")
        self.assertEqual(record["word"], "replicated")
        self.assertIsNone(self.word(b5, [])["word"])

    def test_flagged_inclusive_words_are_beside_not_in_the_word(self):
        b5 = gamma("block5", "direction_supported", 3.0)
        counting = [gamma(f"s{i}", "direction_supported", 3.0) for i in range(3)]
        record = self.word(b5, counting, inclusive=[gamma("x", "unresolved", -1.0)])
        self.assertEqual(record["word"], "replicated")
        self.assertEqual(record["flagged_inclusive_sessions"][0]["outcome"], "unresolved")

    def test_floor_from_block5_is_labelled(self):
        b5 = gamma("block5", "direction_supported", 3.0)
        record = self.word(b5, [gamma("s1", "direction_supported", 3.0)], floor_from_block5={"s1": True})
        self.assertTrue(record["floor_from_block_5"])


def entry(status="not_counting", codes=(), structure_ok=True):
    state = {"attempts": [attempt_line("x", "alpha", 2, status, codes=codes, structure_ok=structure_ok)]}
    return census_from_state(state).get("x")


def analysed(n=10, b_op=True, drift="passed", status="ok"):
    return SessionAnalysis("x", "alpha", status, b_op_defined=b_op, drift_screen=drift,
                           kept_units={"c": {"repeat": n, "null_quad": n}})


class FlaggedInclusiveAdmission(unittest.TestCase):
    def test_counting_session(self):
        self.assertEqual(inclusive.admission(entry("counting"), analysed(), RULES), ("counting", []))

    def test_session_level_physics_and_drift_flags_are_ignored(self):
        for status, codes in (("physics_stopped", ()), ("not_counting", ("neg8.survivor_screen_failed",)),
                              ("not_counting", ("calibration.operative_bound_above_stop",))):
            self.assertEqual(inclusive.admission(entry(status, codes), analysed(drift="failed"), RULES), ("added", []))

    def test_not_the_registered_experiment(self):
        self.assertEqual(inclusive.pre_admission(entry(codes=("model.files_differ_from_registered",)), RULES),
                         ("not_registered_experiment", ["W1"]))
        self.assertEqual(inclusive.pre_admission(entry(structure_ok=False), RULES), ("not_registered_experiment", ["S1"]))

    def test_not_computable_is_decided_from_the_analysis(self):
        # An N code does not stop the analysis: (ii) is read from its results.
        self.assertEqual(inclusive.pre_admission(entry(codes=("neg8.survivor_screen_undefined",)), RULES),
                         ("candidate", []))
        self.assertEqual(inclusive.admission(entry(), analysed(n=4), RULES), ("not_computable", ["N3"]))
        self.assertEqual(inclusive.admission(entry(), analysed(b_op=False), RULES), ("not_computable", ["b_op_undefined"]))
        self.assertEqual(inclusive.admission(entry(), analysed(drift="undefined"), RULES),
                         ("not_computable", ["drift_screen_undefined"]))
        self.assertEqual(inclusive.admission(entry(), analysed(status="tooling_refusal"), RULES),
                         ("not_computable", ["analysis_not_completed"]))
        self.assertEqual(inclusive.admission(entry(), None, RULES), ("not_computable", ["analysis_not_completed"]))

    def test_undecided_session_is_indexed_not_harvested(self):
        self.assertEqual(inclusive.pre_admission(entry("pending_harvest"), RULES), ("not_harvested", []))

    def test_five_kept_units_suffice(self):
        self.assertEqual(inclusive.admission(entry(), analysed(n=5), RULES), ("added", []))


if __name__ == "__main__":
    unittest.main()
