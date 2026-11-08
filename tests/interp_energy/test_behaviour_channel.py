"""Fast synthetic arithmetic, inference and projection checks; no study data."""

from dataclasses import replace
import math
import random
import subprocess
import sys
import unittest

from joulewise.interp_energy.behaviour_channel import (
    Answer, CapScenario, EnergyModel, answer_energy, compare_answers,
    compare_scenarios, summarize_answers,
)


class EnergyTests(unittest.TestCase):
    def test_prefill_decode_context_idle_and_fixed_units(self):
        model = EnergyModel(0.25, 0.5, 0.125, idle_w=2, fixed_j=3)
        answer = Answer("one", 4, 3, False, duration_s=10)
        # Contexts 4, 5, 6: 15 token-context pairs, not final-context * d.
        self.assertEqual(answer.context_exposure, 15)
        energy = answer_energy(answer, model)
        self.assertEqual(energy["gross_j"], 27.375)
        self.assertEqual(energy["above_idle_j"], 7.375)
        self.assertEqual(sum(energy["components_j"].values()), energy["gross_j"])

    def test_no_decode_and_no_tokens_still_have_overhead(self):
        model = EnergyModel(1, 2, 3, fixed_j=4)
        self.assertEqual(answer_energy(Answer("p", 3, 0, True), model)["gross_j"], 7)
        self.assertEqual(answer_energy(Answer("empty", 0, 0, False), model)["gross_j"], 4)

    def test_all_attempts_count_towards_energy_per_correct(self):
        answers = [Answer("right", 0, 10, True), Answer("wrong", 0, 90, False)]
        summary = summarize_answers(answers, EnergyModel(0, 1))
        self.assertEqual(summary["gross_j_per_answer"], 50)
        self.assertEqual(summary["gross_j_per_correct"], 100)
        self.assertEqual(summary["total_gross_j"], 100)

    def test_duration_and_gross_basis_prevent_idle_double_counting(self):
        answer = Answer("a", 1, 2, True)
        with self.assertRaisesRegex(ValueError, "duration_s"):
            answer_energy(answer, EnergyModel(1, 2, idle_w=3))
        with self.assertRaisesRegex(ValueError, "double counting"):
            EnergyModel(1, 2, coefficient_basis="gross", idle_w=3)
        energy = answer_energy(answer, EnergyModel(1, 2, coefficient_basis="gross"))
        self.assertEqual(energy["gross_j"], 5)
        self.assertIsNone(energy["above_idle_j"])

    def test_invalid_counts_correctness_rates_and_empty_samples(self):
        for counts in (-1, 1.5, True, "3"):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                Answer("a", 0, counts, True)
        for correct in (1, "true", None):
            with self.subTest(correct=correct), self.assertRaises(ValueError):
                Answer("a", 0, 1, correct)
        for field in ("prefill_j_per_token", "decode_j_per_token",
                      "context_j_per_token_squared", "fixed_j", "idle_w"):
            for value in (-1, float("nan"), float("inf"), True, "1"):
                data = {"prefill_j_per_token": 0, "decode_j_per_token": 1, field: value}
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    EnergyModel(**data)
        with self.assertRaises(ValueError):
            summarize_answers([], EnergyModel(0, 1))
        with self.assertRaises(ValueError):
            Answer(" ", 0, 1, True)
        with self.assertRaises(ValueError):
            EnergyModel(0, 1, source="")

    def test_import_never_requests_optional_runtime(self):
        code = """
import importlib.abc, sys
class NoRuntime(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'mlx', 'mlx_lm', 'torch', 'transformers'}:
            raise AssertionError('unexpected optional import: ' + fullname)
sys.meta_path.insert(0, NoRuntime())
import joulewise.interp_energy.behaviour_channel
"""
        process = subprocess.run([sys.executable, "-B", "-c", code],
                                 text=True, capture_output=True, timeout=20)
        self.assertEqual(process.returncode, 0, process.stderr)


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.base = [Answer(str(i), 4 + i, 16 + i * 4, i % 2 == 0, 8 + i)
                     for i in range(4)]
        self.edited = [Answer(str(i), 2 + i, 8 + i * 2, i != 0, 4 + i)
                       for i in range(4)]
        self.base_model = EnergyModel(0.25, 0.5, 0.125, idle_w=2, fixed_j=4)
        self.edited_model = EnergyModel(0.5, 0.25, 0.25, idle_w=1, fixed_j=8)

    def compare(self, **kwargs):
        return compare_answers(self.base, self.edited, self.base_model,
                               self.edited_model, bootstrap_samples=100, **kwargs)

    def test_symmetric_decomposition_sums_exactly(self):
        report = self.compare()
        metrics = report["per_answer"]
        point = lambda name: metrics[name]["estimate"]
        self.assertEqual(point("delta_j"), point("behaviour_j") + point("rate_j"))
        self.assertEqual(point("behaviour_j"), point("token_count_j")
                         + point("idle_duration_j") + point("fixed_count_j"))
        self.assertEqual(point("rate_j"), point("per_token_j")
                         + point("idle_power_j") + point("fixed_rate_j"))
        self.assertEqual(point("delta_j"), report["edited"]["gross_j_per_answer"]
                         - report["base"]["gross_j_per_answer"])
        for basis in ("per_answer", "per_correct"):
            values = {name: metric["estimate"] for name, metric in report[basis].items()}
            self.assertAlmostEqual(values["delta_j"], values["behaviour_j"] + values["rate_j"], places=11)

    def test_matches_average_of_both_sequential_counterfactuals(self):
        report = self.compare()
        eb_b = summarize_answers(self.base, self.base_model)["gross_j_per_answer"]
        ee_b = summarize_answers(self.edited, self.base_model)["gross_j_per_answer"]
        eb_e = summarize_answers(self.base, self.edited_model)["gross_j_per_answer"]
        ee_e = summarize_answers(self.edited, self.edited_model)["gross_j_per_answer"]
        self.assertEqual(report["per_answer"]["behaviour_j"]["estimate"],
                         ((ee_b - eb_b) + (ee_e - eb_e)) / 2)
        self.assertEqual(report["per_answer"]["rate_j"]["estimate"],
                         ((eb_e - eb_b) + (ee_e - ee_b)) / 2)

    def test_shared_rates_make_rate_term_zero_by_assumption(self):
        report = compare_answers(self.base, self.edited, self.base_model, bootstrap_samples=100)
        self.assertEqual(report["per_answer"]["rate_j"]["estimate"], 0)
        self.assertEqual(report["per_answer"]["per_token_j"]["delta_method"]["standard_error"], 0)

    def test_pairing_uses_ids_not_row_position_and_seed_repeats(self):
        first = self.compare(seed=42)
        second = compare_answers(self.base, list(reversed(self.edited)), self.base_model,
                                 self.edited_model, bootstrap_samples=100, seed=42)
        self.assertEqual(first, second)
        self.assertEqual(first, self.compare(seed=42))
        third = self.compare(seed=43)
        self.assertNotEqual(first["per_answer"]["delta_j"]["bootstrap_percentile"],
                            third["per_answer"]["delta_j"]["bootstrap_percentile"])

    def test_identical_pair_covariance_cancels_but_independent_does_not(self):
        shared = compare_answers(self.base, self.base, self.base_model, bootstrap_samples=100)
        independent = compare_answers(self.base, self.base, self.base_model,
                                      paired=False, bootstrap_samples=100)
        for basis in ("per_answer", "per_correct"):
            self.assertEqual(shared[basis]["delta_j"]["delta_method"]["standard_error"], 0)
            self.assertGreater(independent[basis]["delta_j"]["delta_method"]["standard_error"], 0)

    def test_ratio_delta_method_retains_correctness_energy_covariance(self):
        answers = [Answer(str(i), 0, 100 * (i + 1), i >= 2) for i in range(4)]
        report = compare_answers(answers, answers, EnergyModel(0, 1), bootstrap_samples=100)
        # Analytic influences are [200, 400, -400, -200].
        expected_se = math.sqrt((200**2 + 400**2 + 400**2 + 200**2) / 12)
        self.assertAlmostEqual(report["per_correct"]["base_j"]["delta_method"]["standard_error"],
                               expected_se)

    def test_correctness_only_change_affects_per_correct_not_per_answer(self):
        edited = [replace(a, correct=True) for a in self.base]
        report = compare_answers(self.base, edited, self.base_model, bootstrap_samples=100)
        self.assertEqual(report["per_answer"]["delta_j"]["estimate"], 0)
        self.assertLess(report["per_correct"]["delta_j"]["estimate"], 0)
        self.assertLess(report["per_correct"]["fixed_count_j"]["estimate"], 0)

    def test_sparse_denominator_resamples_are_reported_not_dropped(self):
        base = [Answer(str(i), 0, 10, i == 0) for i in range(10)]
        edited = [replace(a, correct=True) for a in base]
        report = compare_answers(base, edited, EnergyModel(0, 1), bootstrap_samples=100, seed=3)
        interval = report["per_correct"]["delta_j"]["bootstrap_percentile"]
        self.assertEqual(interval["status"], "undefined_zero_correct_resamples")
        self.assertGreater(interval["undefined_resamples"], 0)
        self.assertIsNone(interval["lower"])
        self.assertEqual(report["per_answer"]["delta_j"]["bootstrap_percentile"]["status"], "ok")
        self.assertEqual(report["per_correct"]["edited_j"]["bootstrap_percentile"]["status"], "ok")

    def test_no_correct_answers_keeps_energy_and_withholds_ratio(self):
        base = [replace(a, correct=False) for a in self.base]
        report = compare_answers(base, self.edited, self.base_model, bootstrap_samples=100)
        self.assertIsNone(report["base"]["gross_j_per_correct"])
        self.assertIsNone(report["per_correct"]["delta_j"]["estimate"])
        self.assertEqual(report["per_correct"]["delta_j"]["delta_method"]["status"], "zero_correct")
        self.assertIsNotNone(report["per_answer"]["delta_j"]["estimate"])

    def test_missing_and_duplicate_pairs_or_too_small_samples_refuse(self):
        for base, edited in ((self.base, self.edited[:-1]),
                             (self.base, self.edited + [self.edited[0]]),
                             (self.base[:1], self.edited[:1])):
            with self.subTest(n=(len(base), len(edited))), self.assertRaises(ValueError):
                compare_answers(base, edited, self.base_model, bootstrap_samples=100)
        for kwargs in ({"confidence": 1}, {"confidence": float("nan")},
                       {"bootstrap_samples": 99}, {"paired": "yes"}, {"seed": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                compare_answers(self.base, self.edited, self.base_model, **kwargs)

    def test_unpaired_allows_different_ids_and_sizes(self):
        edited = [replace(a, problem_id="other-" + a.problem_id) for a in self.edited[:3]]
        report = compare_answers(self.base, edited, self.base_model, paired=False, bootstrap_samples=100)
        self.assertEqual(report["edited"]["n_answers"], 3)
        self.assertEqual(report["per_answer"]["delta_j"]["bootstrap_percentile"]["status"], "ok")

    def test_coefficient_basis_must_match(self):
        with self.assertRaisesRegex(ValueError, "same coefficient_basis"):
            compare_answers(self.base, self.edited, self.base_model,
                            EnergyModel(0, 1, coefficient_basis="gross"), bootstrap_samples=100)

    def test_idle_rate_change_requires_duration_even_in_zero_idle_arm(self):
        base = [replace(a, duration_s=None) for a in self.base]
        with self.assertRaisesRegex(ValueError, "duration_s.*both arms"):
            compare_answers(base, self.edited, EnergyModel(0, 1),
                            EnergyModel(0, 1, idle_w=1), bootstrap_samples=100)
        b, e = CapScenario(0.9, 0.25, 8), CapScenario(0.3, 0.5, 4, duration_s=5)
        with self.assertRaisesRegex(ValueError, "duration_s.*both scenarios"):
            compare_scenarios(b, e, EnergyModel(0, 1), EnergyModel(0, 1, idle_w=1))


class ScenarioTests(unittest.TestCase):
    def test_decomposition_closes_and_reverses_across_synthetic_models(self):
        rng = random.Random(91)
        for _ in range(64):
            b = CapScenario(rng.random(), rng.uniform(0.1, 1), rng.randrange(1, 30), 8, 32, 10)
            e = CapScenario(rng.random(), rng.uniform(0.1, 1), rng.randrange(1, 30), 8, 32, 6)
            mb = EnergyModel(rng.random(), rng.random(), rng.random() / 100,
                             idle_w=rng.random(), fixed_j=rng.random())
            me = EnergyModel(rng.random(), rng.random(), rng.random() / 100,
                             idle_w=rng.random(), fixed_j=rng.random())
            forward = compare_scenarios(b, e, mb, me)
            reverse = compare_scenarios(e, b, me, mb)
            for basis in ("per_answer", "per_correct"):
                values = forward[basis]
                self.assertAlmostEqual(values["delta_j"], values["behaviour_j"] + values["rate_j"], places=10)
                for name, value in values.items():
                    if name not in ("base_j", "edited_j"):
                        self.assertAlmostEqual(value, -reverse[basis][name], places=10)

    def test_astra_published_rate_arithmetic_and_synthetic_energy(self):
        model = EnergyModel(0, 0.1)
        for length, expected_ratio in ((3000, 14.5), (5000, 13.2), (8000, 11.7)):
            base = CapScenario(0.93, 0.079, length)
            edited = CapScenario(0.331, 0.481, length)
            report = compare_scenarios(base, edited, model)
            self.assertAlmostEqual(report["decode_tokens_per_correct_reduction_factor"], expected_ratio, delta=0.06)
            expected_delta = 0.1 * (0.331 - 0.93) * (32768 - length)
            self.assertAlmostEqual(report["per_answer"]["delta_j"], expected_delta)
            self.assertEqual(report["per_answer"]["rate_j"], 0)
            self.assertAlmostEqual(report["energy_per_correct_reduction_factor"],
                                   report["decode_tokens_per_correct_reduction_factor"])
            self.assertNotIn("bootstrap_percentile", report["per_answer"])

    def test_mixture_integrates_context_before_averaging(self):
        scenario = CapScenario(0.5, 0.5, 2, prefill_tokens=3, cap_tokens=10)
        model = EnergyModel(0, 0, 1)
        report = compare_scenarios(scenario, scenario, model)
        # K(3, 10)=75, K(3, 2)=7; average 41, rather than K(3, 6)=33.
        self.assertEqual(report["base"]["mean_context_exposure"], 41)
        self.assertEqual(report["base"]["gross_j_per_answer"], 41)

    def test_context_baseline_and_rates_decompose_in_scenarios(self):
        b = CapScenario(0.9, 0.25, 8, 4, 32, 10)
        e = CapScenario(0.3, 0.5, 4, 4, 32, 5)
        report = compare_scenarios(b, e, EnergyModel(1, 2, 0.01, idle_w=2, fixed_j=1),
                                   EnergyModel(2, 1, 0.02, idle_w=1, fixed_j=3))
        for basis in ("per_answer", "per_correct"):
            metrics = report[basis]
            self.assertAlmostEqual(metrics["delta_j"], metrics["behaviour_j"] + metrics["rate_j"])
        with self.assertRaisesRegex(ValueError, "duration_s"):
            compare_scenarios(replace(b, duration_s=None), e, EnergyModel(0, 1, idle_w=1))

    def test_zero_accuracy_and_invalid_scenarios(self):
        report = compare_scenarios(CapScenario(1, 0, 2), CapScenario(0, 1, 2), EnergyModel(0, 1))
        self.assertIsNone(report["energy_per_correct_reduction_factor"])
        self.assertIsNone(report["per_correct"]["delta_j"])
        for kwargs in ({"cap_hit_fraction": 1.1}, {"accuracy": -0.1},
                       {"cap_tokens": 0}, {"noncap_decode_tokens": 32768}):
            data = {"cap_hit_fraction": 0.5, "accuracy": 0.5, "noncap_decode_tokens": 2, **kwargs}
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                CapScenario(**data)


class CoverageTests(unittest.TestCase):
    def test_delta_and_bootstrap_cover_known_synthetic_effects(self):
        # A bounded Monte Carlo regression, not a general coverage guarantee.
        # Correctness affects length, so ignoring its covariance changes ratio SEs.
        rng = random.Random(8127)
        truths = {("per_answer", "delta_j"): -16.5,
                  ("per_answer", "behaviour_j"): -36,
                  ("per_answer", "rate_j"): 19.5,
                  ("per_correct", "delta_j"): -60.625}
        covered = {(basis, name, method): 0 for basis, name in truths
                   for method in ("delta_method", "bootstrap_percentile")}
        for repetition in range(32):
            base, edited = [], []
            for i in range(160):
                draw = rng.random()
                correct_b, correct_e = draw < 0.6, draw < 0.8
                noise = int(rng.gauss(0, 40))
                base.append(Answer(str(i), 100, 1000 + noise - 100 * correct_b, correct_b))
                edited.append(Answer(str(i), 100, 700 + noise + int(rng.gauss(0, 30))
                                     - 100 * correct_e, correct_e))
            report = compare_answers(base, edited, EnergyModel(0.02, 0.1),
                                     EnergyModel(0.02, 0.125), bootstrap_samples=200, seed=repetition)
            for (basis, name), truth in truths.items():
                for method in ("delta_method", "bootstrap_percentile"):
                    interval = report[basis][name][method]
                    self.assertEqual(interval["status"], "ok")
                    covered[basis, name, method] += interval["lower"] <= truth <= interval["upper"]
        for key, count in covered.items():
            with self.subTest(metric=key, covered=count):
                self.assertGreaterEqual(count, 26, "synthetic 95% coverage regression fell below 26/32")


if __name__ == "__main__":
    unittest.main()
