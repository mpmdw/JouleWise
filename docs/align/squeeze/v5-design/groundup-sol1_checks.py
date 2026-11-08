"""Synthetic arithmetic checks for the independent ground-up design; stdlib only.

Run: python3.13 -B docs/align/squeeze/v5-design/groundup-sol1_checks.py
No model, measurement, environment config, or external file is consulted.
"""

import json
import math
from pathlib import Path
import re
import unittest


def binomial_cdf(k, n, p):
    return math.fsum(math.comb(n, i) * p**i * (1 - p)**(n - i)
                     for i in range(k + 1))


def cp_upper(k, n, alpha=0.05):
    if k == n:
        return 1.0
    low, high = 0.0, 1.0
    for _ in range(80):
        mid = (low + high) / 2
        if binomial_cdf(k, n, mid) > alpha:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def window_seconds(members, member_s):
    return 60 * math.ceil((members * member_s + 4995 + 17700) / 60)


def paired_n(b, c, z_alpha=1.959963984540054):
    delta, discordant = b - c, b + c
    return ((z_alpha * math.sqrt(discordant)
             + 1.2815515655446004 * math.sqrt(discordant - delta**2))
            / delta)**2


class GroundupArithmetic(unittest.TestCase):
    def test_report_allocation_and_matched_fpr(self):
        report = Path(__file__).with_name("groundup-sol1.md").read_text()
        match = re.search(r"<!-- arithmetic-inputs -->\s*```json\s*(.*?)\s*```",
                          report, re.S)
        self.assertIsNotNone(match, "missing reproducible design inputs")
        plan = json.loads(match.group(1))
        self.assertEqual(plan["calibration_per_pair"], 79)
        self.assertEqual(2 * plan["calibration_per_pair"] + 10, 7 * 24)
        self.assertEqual(plan["test_attempts"], 240)
        self.assertEqual(2 * 13 * plan["coverage_per_pair_per_class"]
                         + plan["optimized_attempts"], plan["test_attempts"])
        self.assertEqual(2 * 6 * plan["coverage_per_pair_per_class"]
                         + plan["optimized_attempts"],
                         plan["external_opportunity_attempts"])
        self.assertEqual(plan["test_benign"], 240)
        self.assertEqual(plan["test_positive_controls"], 48)
        self.assertEqual(sum(plan[k] for k in (
            "test_attempts", "test_benign", "test_positive_controls",
            "test_sentinels")), 24 * 24)
        self.assertEqual(plan["primary_nights"], sum(plan["night_allocation"].values()))
        self.assertEqual(plan["primary_nights"], 52)
        self.assertEqual(plan["reserve_nights"], 13)
        self.assertEqual(plan["primary_nights"] + plan["reserve_nights"], 65)
        self.assertEqual(2 * 39 + 240 + 240, 558)
        self.assertLess(558 * 420 * 1.25 / 3600, 6 * 51540 / 3600)
        self.assertEqual(2 / (plan["calibration_per_pair"] + 1), 1 / (39 + 1))

    def test_maximum_ranks_and_infeasible_ranks(self):
        # Integer/rational arithmetic avoids floating quantile off-by-one errors.
        self.assertEqual(math.ceil(79 * (79 + 1) / 80), 79)
        self.assertEqual(math.ceil(39 * (39 + 1) / 40), 39)
        self.assertEqual(math.ceil(39 * (20 + 1) / 40), 21)

    def test_member_and_window_envelopes(self):
        self.assertAlmostEqual(516.575127 + 1.135444370 * 420, 993.4617624)
        self.assertEqual(window_seconds(24, 1200), 51540)
        self.assertEqual(window_seconds(24, 1800), 65940)
        self.assertEqual(math.floor((43200 - 4995 - 17700) / 1200), 17)
        self.assertEqual(window_seconds(16, 1200), 41940)

    def test_exact_binomial_limits(self):
        self.assertAlmostEqual(cp_upper(0, 240), 1 - 0.05**(1 / 240))
        self.assertAlmostEqual(cp_upper(6, 240), 0.04874425244)
        self.assertAlmostEqual(cp_upper(12, 240), 0.07975311285)
        self.assertAlmostEqual(cp_upper(6, 120), 0.09629631738)
        self.assertGreater(cp_upper(0, 24), .10)

    def test_escape_power_and_pairing(self):
        cutoff = max(k for k in range(240) if binomial_cdf(k, 240, .10) <= .05)
        self.assertEqual(cutoff, 16)
        self.assertAlmostEqual(binomial_cdf(cutoff, 240, .05), 0.9042766965)
        self.assertAlmostEqual(binomial_cdf(cutoff, 240, .03), 0.9989446836)
        self.assertAlmostEqual(binomial_cdf(7, 136, .03), 0.9467568501)
        self.assertAlmostEqual(binomial_cdf(4, 94, .03), 0.8474016453)
        self.assertAlmostEqual(paired_n(.20, .02), 67.09258, places=3)
        self.assertAlmostEqual(paired_n(.12, .04), 258.50576, places=2)

    def test_clustering_is_a_cost_not_extra_replicates(self):
        design_effect = 1 + (10 - 1) * .05
        self.assertAlmostEqual(design_effect, 1.45)
        self.assertAlmostEqual(240 / design_effect, 165.5172413793)
        self.assertGreater(1 - .05**(1 / 79), 1 / 80)
        per_copy = (186751297.489 + 512401.339 * 1200) * 24 + 4035540899
        self.assertAlmostEqual(per_copy / 1e9, 23.274730601936)


if __name__ == "__main__":
    unittest.main()
