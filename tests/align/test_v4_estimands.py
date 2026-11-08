import unittest

from joulewise.align.apple import v4_estimands as v4


class Ruling2Tests(unittest.TestCase):
    def test_subturn_h_star_uses_registered_exact_grid(self):
        result = v4.subturn_h_star([(128, .1), (256, .7), (384, 1.1)], 1)
        self.assertEqual(384, result["h_star"])
        self.assertEqual("registered_secondary", result["status"])

    def test_h_star_refuses_invalid_rows_and_never_skips_unobserved_grid_doses(self):
        for rows in ([(128.9, 2.)], [(128, 2.), (128, 0.)], [(-128, 2.)], [(True, 2.)], [(128, float('nan'))],
                     [(128, True)], [(128, '2')]):         # L9: a bool or string score is not a score
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                v4.subturn_h_star(rows, 1.)
        skipped = v4.subturn_h_star([(128, 0.), (384, 2.)], 1.)
        self.assertIsNone(skipped['h_star'])
        self.assertEqual(skipped['undefined_missing_grid_doses'], [256])
        self.assertEqual(v4.subturn_h_star([(256, 2.), (128, 0.)], 1.)['h_star'], 256)
        self.assertEqual(v4.subturn_h_star([(128, 1.)], 1.)['h_star'], None)   # strict exceedance
        self.assertEqual(v4.subturn_h_star([(128, 0.), (100, 5.)], 1.)['off_grid_doses'], [100])

    def test_carrier_curve_is_leave_one_out_and_bootstraps_windows(self):
        rows = [dict(pair='bank', window=f'D{i//8}', carrier=str(i), h=h, score=i+h)
                for i in range(40) for h in (0, 128, 256, 512)]
        result = v4.benign_carrier_curve(rows, bootstrap_replicates=20, seed=4)
        self.assertEqual('window', result['bootstrap_unit'])
        self.assertEqual(result['pairs']['bank']['H50'], 128)
        self.assertIn('window_cluster_bootstrap', result['pairs']['bank'])

    def test_carrier_threshold_uses_39_other_untouched_carriers(self):
        rows = [dict(pair='spam', window='D1', carrier=str(i), h=h, score=i+h)
                for i in range(40) for h in (0, 256)]
        curve = v4.benign_carrier_curve(rows, bootstrap_replicates=0)['pairs']['spam']['curve']
        self.assertEqual([(0, 1/40), (256, 1.)], curve)
        few = [r for r in rows if r['carrier'] != '39']
        result = v4.benign_carrier_curve(few, bootstrap_replicates=0)['pairs']['spam']
        self.assertEqual('insufficient_calibration', result['status'])
        self.assertIsNone(result['curve'][0][1])

    def test_residuals_are_printed_against_hold_count_per_trajectory(self):
        result = v4.residual_by_hold_count([
            {"trajectory": "a", "hold_count": 2, "residual_j": 1},
            {"trajectory": "a", "hold_count": 2, "residual_j": 3}])
        self.assertEqual(2, result["rows"][0]["mean_residual_j"])


class Ruling6Tests(unittest.TestCase):
    def test_u6_margin_is_half_cell_sd_and_se_clusters_trajectories(self):
        rows = [{"trajectory": trajectory, "half": half, "residual_j": value}
                for trajectory, values in (("a", (0, 1)), ("b", (1, 2)), ("c", (-1, 0)))
                for half, value in zip(("early", "late"), values)]
        result = v4.u6_stability(rows, cell_residual_sd=10)
        self.assertEqual(5, result["margin_j"])
        self.assertEqual("trajectory_clustered", result["se_kind"])

    def test_d_reports_position_means_not_slope(self):
        result = v4.d_turn_position_means([
            {"turn_position": 1, "residual_j": 1}, {"turn_position": 1, "residual_j": 3},
            {"turn_position": 2, "residual_j": 8}])
        self.assertEqual({1: 2, 2: 8}, result["means_j"])
        self.assertNotIn("slope", result)

    def test_u4_counts_w1_and_uses_four_run_reference(self):
        result = v4.u4_reference([10, 14], [12, 16], {"D1": [11], "D2": [13], "D3": [15]})
        self.assertEqual(13, result["E_ref_j"])
        self.assertEqual(4, result["window_count"])
        self.assertEqual("print_only", result["sigma_w_30b"]["status"])

    def test_u1a_and_u2b_are_implementation_checks(self):
        labels = v4.acceptance_labels()
        self.assertEqual("implementation_check", labels["U1(a)"])
        self.assertEqual("implementation_check", labels["U2(b)"])


class Ruling9Tests(unittest.TestCase):
    def test_delivery_by_admitted_temperature_or_g1_waits(self):
        def rows(s_slow, g_waits):
            return [{"arm": "S", "admission_slow_c": s_slow, "g1_wait_s_by_turn": []},
                    {"arm": "G", "admission_slow_c": 5.0, "g1_wait_s_by_turn": g_waits}]
        self.assertTrue(v4.contrast_delivery(rows(6.0, [0, 0]), delta_slow_c=2)["delivered"])
        self.assertTrue(v4.contrast_delivery(rows(5.0, [3, 0]), delta_slow_c=2)["delivered"])
        result = v4.contrast_delivery(rows(5.5, [0, 0, 4]), delta_slow_c=2)
        self.assertFalse(result["delivered"])
        self.assertEqual("implementation_check", result["status"])


class Ruling10Tests(unittest.TestCase):
    def test_d_slot_mismatch_sets_instrument_false(self):
        config = dict(max_episode_decode_tokens=4096, deadman_s=1086, max_tokens=4096, max_turns=4)
        result = v4.d_configuration_assertion([
            {"configuration": config}, {"configuration": {**config, "max_turns": 3}}])
        self.assertFalse(result["one_cohort"])
        self.assertFalse(result["instrument_ok"])

    def test_all_four_fixed_slots_make_one_cohort(self):
        config = dict(max_episode_decode_tokens=4096, deadman_s=1086, max_tokens=4096, max_turns=4)
        self.assertTrue(v4.d_configuration_assertion([{"configuration": config, 'cohort_identity': {
            'model_source': 'tiny', 'model_revision': 'synthetic', 'runtime_sha256': 'a'*64,
            'execution_policy_sha256': 'b'*64}}])["instrument_ok"])


class Ruling12Tests(unittest.TestCase):
    def test_fpr_mde_heterogeneity_and_unstable_max_are_reported(self):
        rows = [{"window": "D1", "score": 1}, {"window": "D1", "score": 2},
                {"window": "D2", "score": 3}, {"window": "D2", "score": 7}]
        result = v4.conformal_threshold_diagnostics(rows)
        self.assertAlmostEqual(.2, result["marginal_fpr_bound"])
        self.assertEqual({"rank_m": 7, "rank_m_minus_1": 3}, result["mde"])
        self.assertTrue(result["threshold_instability_flag"])
        self.assertEqual("Kruskal-Wallis", result["window_heterogeneity"]["test"])
        self.assertEqual({"D1": 1.5, "D2": 5}, result["window_heterogeneity"]["per_window_medians"])
        self.assertIn("Marginal FPR", result["fpr_statement"])


class Ruling15Tests(unittest.TestCase):
    def test_sentinel_requires_completion_clean_flags_and_three_turns(self):
        good = v4.sentinel_admissibility({"status": "completed", "x_flags": [], "turns": 3})
        bad = v4.sentinel_admissibility({"status": "completed", "x_flags": ["X2"], "turns": 3})
        self.assertTrue(good["admissible"])
        self.assertFalse(bad["admissible"])
        self.assertEqual({"seed": 93, "pair": "bank", "condition": "benign",
                          "index_role": "development"}, good["alternate"])
        self.assertIn("D member", good["predecessor_disclosure"])


class Ruling18Tests(unittest.TestCase):
    def test_reference_minus_soak_and_wait_table_are_print_only(self):
        result = v4.warm_reference_diagnostic(
            {"slow": 42, "fast": 50}, {"slow": 40, "fast": 51},
            [{"ordinal": 2, "G0_wait_s": 4, "G1_wait_s": 6},
             {"ordinal": 1, "G0_wait_s": 2, "G1_wait_s": 3}])
        self.assertEqual({"fast": -1, "slow": 2}, result["R_minus_R1_soak_c"])
        self.assertTrue(result["thermal.reference_warm"])
        self.assertEqual([1, 2], [row["ordinal"] for row in result["wait_against_ordinal"]])
        self.assertEqual("print_only", result["status"])


if __name__ == "__main__":
    unittest.main()
