"""Exact synthetic power and blinding tests. Standard library only."""

from collections import Counter
import math
import unittest

from joulewise.interp_energy._common import canonical_sha256
from joulewise.interp_energy.tamper_challenge import (
    binomial_tail, equivalence_power, make_challenge, plan_binary,
)


class BinaryPowerTests(unittest.TestCase):
    def test_tails_match_enumeration_and_three_copies_cannot_reject_chance(self):
        for n in (3, 8, 24):
            for p in (.05, .5, .6):
                for k in (0, 1, n // 2, n, n + 1):
                    expected = sum(math.comb(n, i) * p**i * (1-p)**(n-i)
                                   for i in range(k, n + 1))
                    self.assertAlmostEqual(binomial_tail(n, p, k), expected, places=12)
        self.assertAlmostEqual(binomial_tail(3, .5, 3), .125)

    def test_plan_is_powered_and_all_smaller_n_fail(self):
        plan = plan_binary(families=3)
        self.assertLessEqual(plan.achieved_size, .05 / 3)
        self.assertGreaterEqual(plan.achieved_power, .8)
        self.assertGreater(plan.copies_per_class, 100)
        # Independent direct-combination oracle for every smaller n; no mirrored
        # recursion or size/power shortcut from the production implementation.
        for n in range(1, plan.copies_per_class):
            size, power = 0., 0.
            for k in range(n, -1, -1):
                size += math.comb(n, k) * .5**n
                if size > .05 / 3:
                    break
                power += math.comb(n, k) * .6**k * .4**(n-k)
            self.assertLess(power, .8)

    def test_multiplicity_and_sensitivity_plans(self):
        self.assertGreaterEqual(plan_binary(families=8).copies_per_class,
                                plan_binary(families=1).copies_per_class)
        sensitivity = plan_binary(null_probability=.05, alternative_probability=.15)
        self.assertGreaterEqual(sensitivity.achieved_power, .8)
        self.assertLessEqual(sensitivity.achieved_size, .05)

    def test_bad_or_infeasible_plans_are_refused(self):
        for kwargs in ({"families": True}, {"alternative_probability": .5},
                       {"family_alpha": 0}, {"max_copies": 3}, {"target_power": 1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                plan_binary(**kwargs)


class EquivalencePlanningTests(unittest.TestCase):
    def values(self, **kwargs):
        return equivalence_power(**(dict(copies=256, replays_per_copy=8, sessions=16,
                                        margin_j=2.7, systematic_bound_j=.5) | kwargs))

    def test_replays_do_not_remove_copy_session_or_systematic_terms(self):
        base = self.values()
        more_replays = self.values(replays_per_copy=80000)
        self.assertGreater(more_replays["standard_error_j"], 4.7 / 4)
        self.assertAlmostEqual(base["standard_error_j"], more_replays["standard_error_j"], delta=.01)
        self.assertGreater(self.values(sessions=128)["power_at_true_zero"], base["power_at_true_zero"])
        self.assertEqual(self.values(systematic_bound_j=2.7)["power_at_true_zero"], 0)

    def test_pure_independent_pair_tost_known_sigma(self):
        result = self.values(copies=13, replays_per_copy=1, sessions=1,
                             copy_sd_j=0, session_sd_j=0, systematic_bound_j=0)
        self.assertGreater(result["power_at_true_zero"], .8)
        self.assertLess(result["power_at_true_zero"], .9)

    def test_impossible_session_geometry(self):
        with self.assertRaises(ValueError):
            self.values(sessions=10000)


class BlindedRosterTests(unittest.TestCase):
    def test_copies_repeats_pairing_blinding_digest_and_reproducibility(self):
        public, curator = make_challenge(("surgery", "precision"), seed=23, replays_per_copy=2)
        self.assertEqual((public, curator), make_challenge(("surgery", "precision"), seed=23, replays_per_copy=2))
        self.assertEqual(public["roster_sha256"], canonical_sha256({
            k: v for k, v in public.items() if k != "roster_sha256"}))
        self.assertEqual(curator["roster_sha256"], public["roster_sha256"])
        self.assertTrue(all(set(row) == {"copy_id", "repeat"} for row in public["slots"]))
        self.assertEqual(set(Counter(r["copy_id"] for r in public["slots"]).values()), {2})
        labels = Counter(v["class"] for v in curator["copies"].values())
        n = public["binary_plan"]["copies_per_class"]
        self.assertEqual(labels, {"surgery": n, "precision": n, "sham": 2*n})
        pairs = {}
        for row in curator["copies"].values():
            pairs.setdefault(row["matched_pair"], []).append(row["class"])
        self.assertTrue(all(len(pair) == 2 and "sham" in pair for pair in pairs.values()))
        self.assertEqual(public["acquisition_hours_excluding_overhead"], len(public["slots"]) * 200 / 3600)
        self.assertNotEqual(public["slots"], make_challenge(("surgery", "precision"), seed=24,
                                                         replays_per_copy=2)[0]["slots"])

    def test_bad_rosters_are_refused(self):
        for classes, kwargs in (((), {}), (("x", "x"), {}), (("",), {}), (("sham",), {}),
                                (("a", "b"), {"families": 1}), (("a",), {"replays_per_copy": 0})):
            with self.subTest(classes=classes, kwargs=kwargs), self.assertRaises(ValueError):
                make_challenge(classes, seed=0, **kwargs)


if __name__ == "__main__":
    unittest.main()
