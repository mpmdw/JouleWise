import unittest

from joulewise.align.apple import v4_estimands as v4


class Ruling2Tests(unittest.TestCase):
    def test_subturn_h_star_uses_registered_exact_grid(self):
        result = v4.subturn_h_star([(128, .1), (256, .7), (384, 1.1)], 1)
        self.assertEqual(384, result["h_star"])
        self.assertEqual("registered_secondary", result["status"])

    def test_carrier_curve_is_leave_one_out_and_bootstraps_windows(self):
        rows = []
        for window in ("D1", "D2"):
            for carrier in range(6):
                for h in (128, 256, 512):
                    rows.append({"pair": "bank", "window": window,
                                 "carrier": f"{window}-{carrier}", "h": h,
                                 "score": carrier + h/128})
        result = v4.benign_carrier_curve(rows, bootstrap_replicates=20, seed=4)
        self.assertEqual("window", result["bootstrap_unit"])
        self.assertIn("H50", result["pairs"]["bank"])
        self.assertIn("window_cluster_bootstrap", result["pairs"]["bank"])

    def test_full_omission_also_strips_later_prompt_and_context(self):
        rows = [{"turn": 1, "kind": "reasoning"}, {"turn": 1, "kind": "answer"},
                {"turn": 2, "kind": "P"}, {"turn": 2, "kind": "C"},
                {"turn": 2, "kind": "decode"}]
        result = v4.full_omission_rows(rows, 1)
        self.assertEqual([{"turn": 1, "kind": "answer"}, {"turn": 2, "kind": "decode"}], result["rows"])
        self.assertEqual("print_only", result["status"])

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
    @staticmethod
    def rows(effect=12, delivered=True):
        rows = []
        for stage in (0, 1):
            for template in ("X", "Y"):
                for arm in ("G", "S"):
                    rows.append({"stage": stage, "template": template, "arm": arm,
                                 "energy_j": 100 + 20*stage + (effect if arm == "S" else 0),
                                 "admission_slow_c": 8 if arm == "S" and delivered else 5,
                                 "g1_wait_s_by_turn": [0, 0]})
        return rows

    def test_verdict_is_conditional_on_delivery(self):
        result = v4.contrast_verdict(self.rows(delivered=False), delta_slow_c=2)
        self.assertEqual("treatment not delivered", result["verdict"])

    def test_contrast_model_includes_stage_and_has_three_df(self):
        result = v4.contrast_verdict(self.rows(), delta_slow_c=2)
        self.assertEqual("energy ~ arm * template + stage", result["model"])
        self.assertEqual(3, result["df"])
        self.assertEqual("T CONFIRMED", result["verdict"])

    def test_negative_same_sign_effect_is_not_confirmed(self):
        rows = self.rows(effect=-12)
        # Deliver by actual G1 waits, independent of the sign of the outcome.
        for row in rows:
            if row["arm"] == "G":
                row["g1_wait_s_by_turn"] = [1, 1]
        self.assertNotEqual("T CONFIRMED", v4.contrast_verdict(rows, delta_slow_c=2)["verdict"])


class Ruling10Tests(unittest.TestCase):
    def test_d_slot_mismatch_sets_instrument_false(self):
        config = dict(max_episode_decode_tokens=4096, deadman_s=1086, max_tokens=4096, max_turns=4)
        result = v4.d_configuration_assertion([
            {"configuration": config}, {"configuration": {**config, "max_turns": 3}}])
        self.assertFalse(result["one_cohort"])
        self.assertFalse(result["instrument_ok"])

    def test_all_four_fixed_slots_make_one_cohort(self):
        config = dict(max_episode_decode_tokens=4096, deadman_s=1086, max_tokens=4096, max_turns=4)
        self.assertTrue(v4.d_configuration_assertion([{"configuration": config}])["instrument_ok"])


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
