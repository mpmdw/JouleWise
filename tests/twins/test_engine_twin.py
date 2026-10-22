"""Synthetic checks of the independently derived registered engine twin."""

import math
import unittest

from joulewise.twins.engine_twin import (
    Block, Run, adjust, descriptive, estimate, family, outcome,
    t_critical, t_two_sided,
)


def quads(differences, *, prefix="q", drift=0.0, bound=0.0, variance=0.0):
    """Add linear drift in acquisition order A1,B1,B2,A2."""
    result = []
    for i, difference in enumerate(differences):
        base = 10.0 + i*7*drift
        def run(energy):
            return Run(energy, variance, {"E_clock_anchor_shift_bound_j": bound})
        result.append(Block(f"{prefix}{i}",
                            (run(base), run(base+3*drift)),
                            (run(base+difference+drift), run(base+difference+2*drift))))
    return result


class TwinFromTextTests(unittest.TestCase):
    def test_registered_quantiles_and_cauchy_tail(self):
        for df, expected in enumerate((2.776, 2.571, 2.447, 2.365, 2.306, 2.262), 4):
            self.assertEqual(t_critical(df), expected)
        self.assertAlmostEqual(t_critical(9, rounded=False), 2.262157162798205, places=12)
        for x in (0, 0.2, 1, 2, 10, 100):
            self.assertAlmostEqual(t_two_sided(x, 1), 1-2*math.atan(x)/math.pi, places=13)

    def test_registered_kept_quad_worked_example(self):
        differences = [3.1, 2.9, 3.3, 3.0, 2.8, 3.2, 3.1, 2.9, 3.0, 2.7]
        rows = quads(differences, bound=0.025)
        rows.pop(3)
        result = estimate(rows)
        self.assertEqual(result.n, 9)
        self.assertAlmostEqual(result.point, 3.0)
        self.assertAlmostEqual(result.sd, math.sqrt(0.0375))
        self.assertAlmostEqual(result.se_repeat, math.sqrt(0.0375/9))
        self.assertEqual(result.se_metrology, 0)
        self.assertAlmostEqual(result.ci[0], 3-2.306*math.sqrt(0.0375/9))
        self.assertAlmostEqual(result.decision[0], result.ci[0]-0.05)
        self.assertEqual(outcome(result, 1.2, 2*result.p), "direction_supported")
        self.assertEqual(family({"decode": rows, "prefill": rows}, {"decode": 1.2, "prefill": 1.2})["decode"]["ceiling"], "L2")

    def test_abba_cancels_linear_drift(self):
        baseline = estimate(quads([1, 2, 3, 4, 5]))
        drifting = estimate(quads([1, 2, 3, 4, 5], drift=17))
        self.assertEqual(baseline, drifting)

    def test_variance_uses_arm_mean_then_mean_of_blocks(self):
        value = estimate(quads([2]*5, variance=4))
        self.assertEqual(value.se_repeat, 0)
        # Each two-run arm mean has variance 4/2=2; contrast 4; mean 4/5.
        self.assertAlmostEqual(value.se_metrology, math.sqrt(4/5))
        self.assertGreater(value.ci[1]-value.ci[0], 0)

    def test_contrast_bound_precedence_and_mean_not_sum(self):
        rows = quads([2]*5, bound=3)
        rows = [Block(b.key, b.a, b.b, {"E_clock_anchor_shift_bound_j": 0.25}) for b in rows]
        value = estimate(rows)
        self.assertEqual(value.bounds["E_clock_anchor_shift_bound_j"], 0.25)
        self.assertEqual(value.decision, (1.75, 2.25))

    def test_holm_and_bh_keep_missing_member(self):
        p = {"a": 0.01, "b": 0.04, "c": None}
        self.assertEqual(adjust(p, 3), {"a": 0.03, "b": 0.08, "c": None})
        self.assertEqual(adjust(p, 3, "bh"), {"a": 0.03, "b": 0.06, "c": None})
        self.assertEqual(adjust({"b": 0.01, "a": 0.01}, 2), {"b": 0.02, "a": 0.02})

    def test_outcome_precedence_and_strict_gates(self):
        value = estimate(quads([2]*5))
        self.assertEqual(outcome(None, None, None), "not_estimable")
        self.assertEqual(outcome(value, 1, 0, reasons=["metric_missing_or_nonfinite"]), "not_estimable")
        self.assertEqual(outcome(value, None, 0), "not_resolvable")
        self.assertEqual(outcome(value, 2, 0), "not_resolvable")
        self.assertEqual(outcome(value, 1, 0.051), "unresolved")
        self.assertEqual(outcome(value, 1, 0.05), "direction_supported")
        widened = estimate(quads([2]*5, bound=1))
        self.assertEqual(outcome(widened, 1, 0), "not_resolvable")
        zero_ci = estimate(quads([-2, -1, 1, 2, 3]))
        self.assertEqual(outcome(zero_ci, 0.1, 0), "unresolved")
        interpolation = [Block(b.key, b.a, b.b, {"E_interpolation_joint_edge_bound_j": 1}) for b in quads([4]*5)]
        self.assertEqual(outcome(estimate(interpolation), 1, 0), "not_resolvable")

    def test_zero_scatter_and_sign(self):
        self.assertEqual(estimate(quads([0]*5)).p, 1)
        self.assertEqual(estimate(quads([-3]*5)).p, 0)
        results = family({"a": quads([-3]*5), "b": quads([3]*5)}, {"a": 1, "b": 1})
        self.assertEqual(results["a"]["outcome"], "direction_supported")
        self.assertEqual(results["a"]["ceiling"], "L1")
        self.assertEqual(results["b"]["ceiling"], "L2")

    def test_loo_and_demotion(self):
        results = family({"a": quads([0.2]*4+[10]), "b": quads([3]*5)}, {"a": 1, "b": 1})
        self.assertTrue(any("floor" in x["triggers"] for x in results["a"]["loo"]))
        self.assertEqual(results["a"]["ceiling"], "L1")
        for kwargs in ({"confirmatory": False}, {"current": False}):
            self.assertEqual(family({"a": quads([3]*5)}, {"a": 1}, **kwargs)["a"]["ceiling"], "L1")

    def test_registered_descriptive_ratio_and_token_scaling(self):
        result = descriptive(quads([10]*5), 512)
        self.assertAlmostEqual(result["ratio"], 2)
        self.assertAlmostEqual(result["ratio_interval"][0], 2)
        self.assertEqual(result["per_token"], 10/512)

    def test_bad_arithmetic_inputs_refuse(self):
        for rows in ([], quads([1]), [Block("q", (), (Run(1),))]*2,
                     quads([float("nan"), 2])):
            with self.assertRaises(ValueError):
                estimate(rows)


if __name__ == "__main__":
    unittest.main()
