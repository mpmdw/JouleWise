"""Small analytical checks; no repository runtime or study-data imports."""
import importlib.util
import math
from pathlib import Path
import sys
import unittest

_SPEC = importlib.util.spec_from_file_location("b3_sim_sol2", Path(__file__).with_name("simulate_sol2.py"))
sim = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = sim
_SPEC.loader.exec_module(sim)


class SyntheticSimulationTests(unittest.TestCase):
    def test_both_pairs_and_final_window_boundary(self):
        counts = [(7*n, 6*n) for n in range(1, 9)]
        self.assertEqual(sim.stop_window(counts, 6), 7)
        self.assertEqual(sim.stop_window(counts, 7), 7)

    def test_cap_failure_never_emits_threshold(self):
        self.assertEqual(sim.stop_window([(0, 0)]*8, 6), 8)
        with self.assertRaisesRegex(ValueError, "insufficient"):
            sim.thresholds(list(range(38)))

    def test_rank_contract_at_39_and_above(self):
        for m, k in ((39, 38), (40, 39), (42, 41), (49, 48), (56, 55)):
            self.assertEqual(sim.rank05(m), k)
        self.assertEqual(sim.thresholds(list(range(1, 40))),
                         {"max": 39, "rank05": 38, "literal38": 38})
        self.assertEqual(sim.thresholds(list(range(1, 57)))["literal38"], 38)

    def test_shared_window_loss_uses_attempt_capacity(self):
        # One failed attempted window: six attempts supply only 35/pair.
        counts = [(0, 0)]+[(7*n, 7*n) for n in range(1, 8)]
        self.assertEqual(sim.stop_window(counts, 6), 7)

    def test_target_review_count_arithmetic(self):
        r = sim.exact_count_reference(.1)
        self.assertAlmostEqual(r["both_by_window"]["6"], .147184, places=6)
        self.assertAlmostEqual(r["both_by_window"]["7"], .984054, places=6)
        self.assertAlmostEqual(r["mean_count6_windows"], 6.868762, places=6)

    def test_eligibility_reweights_test_state(self):
        s = sim.Scenario("hot20", .2, True)
        self.assertAlmostEqual(sim.eligible_hot_weight(s), .15625)
        self.assertAlmostEqual(.75*s.rates()[0]+.25*s.rates()[1], .2)

    def test_tau_zero_has_exact_normal_survival(self):
        for s in sim.SCENARIOS:
            self.assertAlmostEqual(sim.future_tail(0, 0, s), .5)
            self.assertAlmostEqual(sim.future_tail(1.959963984540054, 0, s), .025)

    def test_analytic_tail_shift_and_monotonicity(self):
        s = sim.Scenario("hot10", .1, True)
        self.assertAlmostEqual(sim.future_tail(2, .5, s, .5), sim.future_tail(1.5, .5, s))
        self.assertGreater(sim.future_tail(2, .5, s), sim.future_tail(3, .5, s))
        self.assertAlmostEqual(sim.future_tail(-100, .5, s), 1)
        self.assertAlmostEqual(sim.future_tail(100, .5, s), 0)

    def test_bounded_drift_allowance_covers_all_state_pairs(self):
        for tau in sim.SCALES:
            for cal in (-tau/math.sqrt(3), math.sqrt(3)*tau):
                for test in (-tau/math.sqrt(3), math.sqrt(3)*tau):
                    self.assertGreaterEqual(sim.transport_allowance(tau)+cal+1e-15, test+tau)

    def test_pair_average_mc_uses_tapes(self):
        stat = sim.PairMoments()
        stat.add((0, 1))
        stat.add((1, 0))
        self.assertEqual(stat.result()["pair_average"]["n"], 2)
        self.assertEqual(stat.result()["pair_average"]["mc_se"], 0)

    def test_exact_clustered_counterexample(self):
        oracle = sim.review_counterexample()
        self.assertAlmostEqual(oracle["count6"]["fpr_given_success"], .05316705, places=8)
        self.assertAlmostEqual(oracle["fixed8"]["fpr_given_success"], .04306531, places=8)
        self.assertGreater(oracle["count7"]["fpr_given_success"], oracle["fixed8"]["fpr_given_success"])


if __name__ == "__main__":
    unittest.main()
