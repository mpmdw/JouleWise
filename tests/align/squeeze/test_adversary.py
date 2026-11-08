import math
import unittest

try:
    import numpy as np
except ImportError:
    np = None

if np is not None:
    from joulewise.align.squeeze.adversary import (
        Attack, MonitorResponse, Noise, attack_effect, attack_families, simulate,
    )
    from joulewise.align.squeeze.residual import Carrier, ResidualModel, design


@unittest.skipUnless(np is not None, "optional NumPy extra unavailable")
class ResidualTests(unittest.TestCase):
    def test_five_term_forms(self):
        np.testing.assert_array_equal(design(3, 4, 5), [1, 3, 4, 40, 19.5])
        np.testing.assert_array_equal(design(3, 4, 5, form="turn"), [1, 3, 4, 20, 15])
        self.assertEqual(design([1, 2], 3, 4).shape, (2, 5))

    def test_sequence_hidden_increment_includes_quadratic(self):
        model = ResidualModel((2, .001, .3, .00004, .0000002))
        h, p, d, c = 300, 128, 512, 4096
        expected = .3*h + .00004*((c+p+d)*h + h*h/2)
        self.assertAlmostEqual(model.hidden_increment(h, prefill=p, decode=d, context=c), expected)
        self.assertAlmostEqual(model.predict(p, d+h, c) - model.predict(p, d, c), expected)

    def test_turn_form_at_mean_context_and_intercept(self):
        model = ResidualModel((999, 5, .35, .15/4096, 3), form="turn")
        self.assertEqual(model.hidden_increment(10, prefill=0, decode=0, context=4096), 5)
        self.assertEqual(model.predict(0, 0, 0), 999)

    def test_sum_design_prediction(self):
        beta = np.array([1, .02, .3, .001, .0002])
        rows = design([10, 20], [30, 40], [50, 60])
        model = ResidualModel(tuple(beta))
        np.testing.assert_allclose(model.predict([10, 20], [30, 40], [50, 60]).sum(),
                                   rows.sum(axis=0) @ beta)

    def test_invalid_design_and_model(self):
        for bad in (-1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                design(bad, 1, 2)
        for coefficients in ((1, 2), (1, 2, 3, 4, math.nan)):
            with self.assertRaises(ValueError):
                ResidualModel(coefficients)
        with self.assertRaises(ValueError):
            Carrier(decode=-1)


@unittest.skipUnless(np is not None, "optional NumPy extra unavailable")
class AdversaryTests(unittest.TestCase):
    def setUp(self):
        self.model = ResidualModel((2, .01, .5, 0, 0), form="turn")
        self.carrier = Carrier()

    def effect(self, attack, h=256, model=None):
        return attack_effect(model or self.model, self.carrier, attack, h)

    def test_work_and_energy_conservation(self):
        e = self.effect(Attack("mixed", logged_fraction=.25, tool_fraction=.5))
        self.assertEqual(e.logged_work_tokens + e.local_unlogged_tokens + e.tool_tokens, 256)
        self.assertEqual((e.logged_work_tokens, e.local_unlogged_tokens, e.tool_tokens), (64, 96, 96))
        self.assertEqual(e.residual_shift_j, 96*.5 + 96*.25)
        self.assertEqual(e.physical_extra_j-e.predicted_extra_j, e.residual_shift_j)

    def test_honest_padding_does_not_cancel_hidden_work(self):
        a = self.effect(Attack("none"))
        b = self.effect(Attack("honest-padding", padding_tokens=1024))
        self.assertEqual(a.residual_shift_j, b.residual_shift_j)
        self.assertEqual(b.physical_extra_j-a.physical_extra_j, 512)
        self.assertEqual(b.predicted_extra_j-a.predicted_extra_j, 512)
        seq = ResidualModel((2, .01, .5, .001, 0))
        self.assertGreater(self.effect(Attack("pad", padding_tokens=1024), model=seq).residual_shift_j,
                           self.effect(Attack("none"), model=seq).residual_shift_j)

    def test_relabelling_trades_meter_for_monitor(self):
        effects = [self.effect(Attack(str(f), logged_fraction=f)) for f in (0, .5, 1)]
        self.assertEqual([e.residual_shift_j for e in effects], [128, 64, 0])
        self.assertEqual([e.monitor_shift for e in effects], [0, 1, 2])

    def test_smoothing_scales_joules_but_does_not_erase_integral(self):
        self.assertEqual(self.effect(Attack("smooth", smoothing_cost_ratio=.7)).residual_shift_j, 89.6)
        with self.assertRaises(ValueError):
            Attack("zero-cost", smoothing_cost_ratio=0)

    def test_tool_meter_boundary_and_monitor_visibility(self):
        local = self.effect(Attack("local-tool", tool_fraction=1))
        self.assertEqual((local.residual_shift_j, local.monitor_shift), (64, 2))
        escaped = self.effect(Attack("remote-opaque", tool_fraction=1,
                                     tool_meter_fraction=0, tool_monitor_visibility=0))
        self.assertEqual((escaped.residual_shift_j, escaped.monitor_shift), (0, 0))
        self.assertIn("tool_work_outside_meter_boundary", escaped.flags)

    def test_opaque_logged_work_is_a_counterexample(self):
        e = self.effect(Attack("opaque", logged_fraction=1, monitor_visibility=0))
        self.assertEqual((e.residual_shift_j, e.monitor_shift), (0, 0))
        self.assertIn("assumed_monitor_evasion", e.flags)

    def test_fabricated_counts_are_explicit_and_can_cancel_signal(self):
        e = self.effect(Attack("forged", phantom_logged_tokens=256))
        self.assertEqual(e.residual_shift_j, 0)
        self.assertIn("fabricated_counts_threat", e.flags)

    def test_hidden_counts_not_increased_by_extra_benign_padding(self):
        e = self.effect(Attack("pad", padding_tokens=1000), h=0)
        self.assertEqual(e.total_work_tokens, 0)
        self.assertEqual((e.residual_shift_j, e.monitor_shift), (0, 0))
        self.assertIn("zero_dose_control_not_hidden_work_detection", e.flags)

    def test_negative_fit_not_silently_clipped(self):
        e = self.effect(Attack("baseline"), model=ResidualModel((0, 0, -1, 0, 0)))
        self.assertEqual(e.residual_shift_j, -256)
        self.assertIn("negative_fitted_work_cost", e.flags)

    def test_grids_and_input_refusal(self):
        self.assertEqual(set(attack_families()), {"padding", "smoothing", "tool_shifting", "combined"})
        for kwargs in ({"logged_fraction": -1}, {"tool_fraction": 2},
                       {"padding_tokens": -1}, {"monitor_visibility": math.nan}):
            with self.assertRaises(ValueError):
                Attack("invalid", **kwargs)
        with self.assertRaises(ValueError):
            MonitorResponse(0)


@unittest.skipUnless(np is not None, "optional NumPy extra unavailable")
class NoiseTests(unittest.TestCase):
    def test_total_sd_and_correlated_channels(self):
        n = Noise(38, 2, correlation=.6)
        a = n.sample(np.random.default_rng(104), 30000)
        self.assertAlmostEqual(float(a[:, 1].std()), 38, delta=.8)
        self.assertAlmostEqual(float(a[:, 0].std()), 1, delta=.025)
        self.assertAlmostEqual(float(np.corrcoef(a.T)[0, 1]), .6, delta=.025)

    def test_zero_correlation_keeps_energy_noise_in_batched_power_draws(self):
        for shape in ((512, 64), (512, 256), (512, 40)):
            with self.subTest(shape=shape):
                a = Noise(19).sample(np.random.default_rng(22), shape)
                self.assertAlmostEqual(float(a[..., 1].std()), 19, delta=.6)
                self.assertAlmostEqual(float(a[..., 0].std()), 1, delta=.03)
                self.assertAlmostEqual(float(np.corrcoef(a.reshape(-1, 2).T)[0, 1]),
                                       0, delta=.03)
                self.assertFalse(a.flags.writeable)

    def test_replay_not_substituted_for_task_sd(self):
        n = Noise(58, 2)
        a = n.replay_pairs(np.random.default_rng(2), 30000)
        self.assertAlmostEqual(float(np.diff(a, axis=1).std()), math.sqrt(2)*2, delta=.08)
        self.assertAlmostEqual(float(a[:, 0].std()), 58, delta=1)

    def test_heavy_tails_finite_sd_and_determinism(self):
        n = Noise(19, 2, student_df=8)
        a = n.sample(np.random.default_rng(3), 30000)
        b = n.sample(np.random.default_rng(3), 30000)
        np.testing.assert_array_equal(a, b)
        self.assertAlmostEqual(float(a[:, 1].std()), 19, delta=.6)
        e = attack_effect(ResidualModel((0, 0, .5, 0, 0)), Carrier(), Attack("hidden"), 128)
        self.assertEqual(simulate(e, n, 3).shape, (3, 2))

    def test_noise_validation(self):
        for kwargs in ({"residual_sd_j": 0}, {"residual_sd_j": 1, "replay_sd_j": 2},
                       {"correlation": 2}, {"student_df": 2}):
            with self.assertRaises(ValueError):
                Noise(**kwargs)


if __name__ == "__main__":
    unittest.main()
