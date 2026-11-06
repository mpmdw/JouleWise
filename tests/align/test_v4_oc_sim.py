"""Closed-form oracles for the print-only ALIGN v4 OC simulation."""
import importlib.util
import math
import pathlib
import unittest

P = pathlib.Path(__file__).parents[2] / "scripts" / "align_v4_oc_sim.py"
S = importlib.util.spec_from_file_location("align_v4_oc_sim", P)
M = importlib.util.module_from_spec(S)
S.loader.exec_module(M)


def _t_cdf(x: float, df: int, steps: int = 20000) -> float:
    """Student-t CDF by Simpson integration of the density on [0, x]."""
    c = math.gamma((df + 1) / 2) / (math.sqrt(df * math.pi) * math.gamma(df / 2))
    f = lambda t: c * (1 + t * t / df) ** (-(df + 1) / 2)
    h = x / steps
    s = f(0) + f(x) + sum((4 if i % 2 else 2) * f(i * h) for i in range(1, steps))
    return 0.5 + s * h / 3


class OCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.small = M.simulate(400, 17)

    def test_seeded_report_is_deterministic(self):
        self.assertEqual(M.simulate(200, 5), M.simulate(200, 5))

    def test_binomial_closed_form(self):
        self.assertAlmostEqual(M.binomial_tail(2, .5, 1), .75)
        self.assertAlmostEqual(M.binomial_tail(21, .95, 21), .95 ** 21)

    def test_extension_d3_is_21_benign_per_pair(self):
        # Chair ruling 3: P(m >= 19 of 21) = 0.92, 0.65, 0.42 at 5, 10, 14 %.
        ext = self.small["extension"]
        for rate, want in (("0.05", 0.91510), ("0.1", 0.64841), ("0.14", 0.42048)):
            self.assertAlmostEqual(ext[rate]["D3"]["m>=19"], want, places=4)
        self.assertAlmostEqual(ext["0.05"]["D3"]["m>=21"], .95 ** 21, places=10)
        self.assertEqual(ext["0.05"]["D4"]["n_benign_per_pair"], 28)

    def test_extension_stop_needs_three_sabotage(self):
        # One pair, all windows pass, D3: benign 21/21 kept and 3/3 sabotage kept.
        got = M.extension_stop_prob(.10, 3, 1.0)
        self.assertAlmostEqual(got, .9 ** 21 * .9 ** 3, places=12)
        # A failed window contributes nothing: with window pass 0 nothing stops.
        self.assertEqual(M.extension_stop_prob(.05, 5, 0.0), 0.0)

    def test_conformal_rank_and_fpr_closed_forms(self):
        for m in range(1, 400):
            r = (19 * (m + 1) + 19) // 20
            self.assertEqual(M.conformal_rank(m), r if r <= m else None)
        self.assertIsNone(M.conformal_rank(18))
        self.assertEqual(M.conformal_rank(19), 19)
        self.assertAlmostEqual(M.marginal_fpr(21), 1 / 22)
        self.assertEqual(M.conformal_rank_coverage(9), 1.0)
        # Chair ruling 12: P(FPR > 5 %) = 0.34, realized FPR <= 10.4 % at 90 %.
        self.assertAlmostEqual(M.realized_fpr_exceedance(21, .05), .95 ** 21, places=12)
        self.assertAlmostEqual(M.realized_fpr_upper(21), 1 - .1 ** (1 / 21), places=9)

    def test_contrast_rule_is_the_registered_fd_rule(self):
        v = M.contrast_verdict
        self.assertEqual(v(12, 11, 1.0, 20.0), "T_CONFIRMED")       # CI lower bound < 10 is fine
        self.assertEqual(v(-12, -11, -20.0, -1.0), "INCONCLUSIVE")  # ruling 9(c): d > 0
        self.assertEqual(v(-12, -11, -20.0, -1.0, require_positive=False), "T_CONFIRMED")
        self.assertEqual(v(12, 9, 1.0, 20.0), "INCONCLUSIVE")
        self.assertEqual(v(2, -3, -5.5, 5.9), "T_REJECTED")
        self.assertEqual(v(2, -3, -7.0, 5.0), "INCONCLUSIVE")       # CI not inside [-6, 6]
        self.assertEqual(v(7, 0, -1.0, 5.0), "INCONCLUSIVE")        # |d_X| > 6

    def test_contrast_design_se_and_df(self):
        plain, stage = M.contrast_design(False), M.contrast_design(True)
        self.assertEqual((plain["df"], stage["df"]), (4, 3))
        self.assertAlmostEqual(plain["se_factor"], math.sqrt(.5), places=3)   # chair: 0.707 sigma
        self.assertGreater(stage["se_factor"], 0.8)                           # stage costs precision
        for df, t in M.T95.items():
            self.assertAlmostEqual(_t_cdf(t, df), 0.95, places=7)

    def test_contrast_ci_uses_estimated_sd(self):
        # Under delta = 0 a 90 % Student-t CI excludes 0 with probability 0.10;
        # a known-sigma half-width with a t critical value gives ~0.033.
        for stage in (False, True):
            rate = M.ci_excludes_zero_rate(20000, 3, stage)
            self.assertLess(abs(rate - 0.10), 0.008, (stage, rate))

    def test_acceptance_set_is_computed_not_asserted(self):
        acc = self.small["acceptance"]
        self.assertTrue(acc["U5"].startswith("PENDING"))
        self.assertTrue(acc["series"].startswith("PENDING"))
        self.assertAlmostEqual(acc["U1b"]["members=18,rate=0.02"],
                               .98 ** 18 + 18 * .02 * .98 ** 17, places=12)
        self.assertAlmostEqual(M.u3_pair_fail(2.97, 2.97), 2 * (1 - 0.9986501019683699), places=9)
        for crit in ("U4", "U6"):
            for cell in acc[crit].values():
                self.assertAlmostEqual(sum(cell.values()), 1.0)

    def test_u6_ruled_margin_is_rarely_passable_at_planned_m(self):
        # Chair ruling 6: 7 v 7 half-width ~0.95 s_r per pair; pooled over two
        # pairs it is still > 0.5 s_r, so a pass needs an unusually small SD.
        import random
        cell = M.u6_oc(4000, random.Random(1), 14, 0.5)
        self.assertLess(cell["pass"], 0.10)

    def test_mde_is_section_c_tokens(self):
        self.assertAlmostEqual(M.mde_tokens(2.5, 190, 3.6), 2.5 * 190 / 3.6)
        cell = self.small["mde_tokens"]["model=A,q=well_behaved,inflation=none"]
        self.assertGreaterEqual(cell["min"], 2.5 * 190 / 4.5)
        self.assertLessEqual(cell["max"], 3.0 * 260 / 3.0)
        heavy = self.small["mde_tokens"]["model=B,q=heavy_tail,inflation=1.2-1.5"]
        self.assertLessEqual(heavy["max"], 7 * 0.017 * 35000 * 1.5 / 3.0)


if __name__ == "__main__":
    unittest.main()
