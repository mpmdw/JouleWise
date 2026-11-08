"""Fast synthetic frontier accounting and matched-bootstrap contracts."""

from dataclasses import replace
import math
import random
import unittest

from joulewise.interp_energy.behaviour_channel import (
    Answer, EnergyModel, answer_energy, compare_answers, summarize_answers,
)
from joulewise.interp_energy.edit_frontier import Variant, analyze_variants, pareto_frontier


MODEL = EnergyModel(0.1, 0.1, 0.01, coefficient_basis="gross", source="synthetic only")


def answers(n=12, *, p=10, d=20, correct=9):
    return [Answer(str(i), p, d + i, i < correct) for i in range(n)]


def variant(name="base", rows=None, model=MODEL, **kwargs):
    return Variant(name, 200, model, answers() if rows is None else rows, **kwargs)


def analyze(variants=None, **kwargs):
    return analyze_variants(variants or [variant(), variant("edit")], baseline="base",
                            model_id="synthetic model + dtype + runtime",
                            boundary="dc", evaluation_id="synthetic items v1",
                            bootstrap_samples=100, **kwargs)


def percentile(values, q):
    ordered = sorted(values)
    position = (len(values) - 1) * q
    lo = int(position)
    return ordered[lo] + (position - lo) * (ordered[min(lo + 1, len(values) - 1)] - ordered[lo])


class FrontierTests(unittest.TestCase):
    def test_dominance_tradeoffs_ties_and_undefined_cost(self):
        self.assertEqual(pareto_frontier({
            "cheap": (5, 0.5), "accurate": (9, 0.9), "dominated": (7, 0.4),
            "tie": (5, 0.5), "same_cost_worse": (5, 0.4), "undefined": (None, 0),
        }), ["accurate", "cheap", "tie"])
        for point in ((-1, .5), (float("nan"), .5), (2, 1.1), (2, float("inf"))):
            with self.subTest(point=point), self.assertRaises(ValueError):
                pareto_frontier({"bad": point})

    def test_context_law_reverses_token_frontier(self):
        # Equal accuracy; A has fewer tokens but more integrated context exposure.
        a = [Answer(str(i), 0, 40, True) for i in range(4)]
        b = [Answer(str(i), 36, 5, True) for i in range(4)]
        report = analyze([variant(rows=a), variant("edit", b)])
        self.assertEqual(report["frontiers"]["tokens_per_answer"]["members"], ["base"])
        self.assertEqual(report["frontiers"]["predicted_per_answer"]["members"], ["edit"])
        self.assertEqual(report["frontiers"]["predicted_per_correct"]["members"], ["edit"])
        self.assertAlmostEqual(report["variants"]["base"]["metrics"]["predicted_per_answer"]["estimate"], 11.8)

    def test_all_attempt_energy_is_charged_in_j_per_correct(self):
        rows = [Answer(str(i), 2, d, i == 0) for i, d in enumerate((1, 10, 100))]
        report = analyze([variant(rows=rows), variant("edit", rows)])
        point = report["variants"]["base"]
        expected = sum(answer_energy(a, MODEL)["gross_j"] for a in rows)
        self.assertAlmostEqual(point["metrics"]["predicted_per_correct"]["estimate"], expected)
        self.assertTrue(point["sparse_correct"])
        self.assertEqual(point["behaviour_channel_summary"], summarize_answers(rows, MODEL))

    def test_bootstrap_matches_manual_joint_ratio_resampling(self):
        rows = sorted(answers(n=12, correct=9), key=lambda row: row.problem_id)
        report = analyze([variant(rows=rows), variant("edit", rows)], seed=21)
        rng = random.Random(21)
        expected = []
        for _ in range(100):
            sample = [rows[rng.randrange(12)] for _ in rows]
            expected.append(sum(answer_energy(a, MODEL)["gross_j"] for a in sample)
                            / sum(a.correct for a in sample))
        interval = report["variants"]["base"]["metrics"]["predicted_per_correct"]
        self.assertAlmostEqual(interval["lower"], percentile(expected, .025))
        self.assertAlmostEqual(interval["upper"], percentile(expected, .975))

    def test_identical_paired_variants_have_zero_contrast_width(self):
        report = analyze()
        for interval in report["comparisons_to_baseline"]["edit"].values():
            self.assertEqual((interval["estimate"], interval["lower"], interval["upper"]), (0, 0, 0))
        self.assertEqual(report["frontiers"]["predicted_per_answer"]["inclusion_frequency"],
                         {"base": 1.0, "edit": 1.0})

    def test_comparison_agrees_with_existing_behaviour_channel(self):
        base = sorted(answers(), key=lambda row: row.problem_id)
        edit = [replace(row, decode_tokens=10 + i) for i, row in enumerate(base)]
        old = compare_answers(base, edit, MODEL, bootstrap_samples=100, seed=7)
        new = analyze([variant(rows=base), variant("edit", edit)], seed=7)
        for unit in ("answer", "correct"):
            result = new["comparisons_to_baseline"]["edit"]["predicted_per_" + unit]
            expected = old["per_" + unit]["delta_j"]
            self.assertAlmostEqual(result["estimate"], expected["estimate"])
            for endpoint in ("lower", "upper"):
                self.assertAlmostEqual(result[endpoint], expected["bootstrap_percentile"][endpoint])

    def test_observed_residual_and_separate_frontier(self):
        rows = answers(correct=12)
        base_obs = {a.problem_id: answer_energy(a, MODEL)["gross_j"] + 2 for a in rows}
        edit_obs = {a.problem_id: answer_energy(a, MODEL)["gross_j"] + 5 for a in rows}
        report = analyze([
            variant(rows=rows, observed_gross_j=base_obs, observation_source="synthetic base"),
            variant("edit", rows, observed_gross_j=edit_obs, observation_source="synthetic edit"),
        ])
        comparison = report["comparisons_to_baseline"]["edit"]
        for unit in ("answer", "correct"):
            interval = comparison["residual_per_" + unit]
            for field in ("estimate", "lower", "upper"):
                self.assertAlmostEqual(interval[field], 3)
        self.assertEqual(report["frontiers"]["observed_per_answer"]["members"], ["base"])
        self.assertEqual(report["frontiers"]["predicted_per_answer"]["members"], ["base", "edit"])

    def test_zero_correct_keeps_answer_frontier_and_withholds_ratio_stability(self):
        rows = answers(correct=0)
        report = analyze([variant(rows=rows), variant("edit")])
        metric = report["variants"]["base"]["metrics"]["predicted_per_correct"]
        self.assertEqual(metric["status"], "zero_correct")
        self.assertIsNone(metric["estimate"])
        frontier = report["frontiers"]["predicted_per_correct"]
        self.assertEqual(frontier["excluded_undefined"], ["base"])
        self.assertEqual(frontier["undefined_resamples"], 100)
        self.assertTrue(all(value is None for value in frontier["inclusion_frequency"].values()))
        self.assertEqual(report["frontiers"]["predicted_per_answer"]["bootstrap_status"], "ok")

    def test_zero_correct_draws_are_not_dropped_or_conditioned_away(self):
        rows = answers(n=4, correct=1)
        report = analyze([variant(rows=rows), variant("edit", rows)])
        metric = report["variants"]["base"]["metrics"]["predicted_per_correct"]
        self.assertEqual(metric["status"], "undefined_zero_correct_resamples")
        self.assertGreater(metric["undefined_resamples"], 0)
        self.assertIsNone(metric["lower"])

    def test_seed_and_input_order_are_reproducible(self):
        first = analyze(seed=12)
        second = analyze([variant("edit", list(reversed(answers()))), variant()], seed=12)
        self.assertEqual(first, second)
        self.assertNotEqual(first, analyze(seed=13))

    def test_different_caps_are_retained_as_treatment_settings(self):
        report = analyze([variant(), replace(variant("edit"), cap_tokens=31)])
        self.assertEqual(report["variants"]["edit"]["cap_tokens"], 31)
        self.assertEqual(report["variants"]["edit"]["cap_hits"], 1)

    def test_above_idle_uses_duration_and_restores_gross_energy(self):
        model = EnergyModel(.1, .2, .01, idle_w=2, source="synthetic")
        rows = [Answer(str(i), 2, 3, True, 5) for i in range(4)]
        report = analyze([variant(rows=rows, model=model), variant("edit", rows, model)])
        self.assertEqual(report["energy_basis"], "gross")
        self.assertAlmostEqual(report["variants"]["base"]["metrics"]["predicted_per_answer"]["estimate"], 10.89)
        with self.assertRaisesRegex(ValueError, "duration_s"):
            analyze([variant(model=model), variant("edit", model=model)])


class ValidationTests(unittest.TestCase):
    def test_invalid_variants(self):
        for changes in ({"name": ""}, {"cap_tokens": True}, {"cap_tokens": 0},
                        {"cap_tokens": 2}, {"answers": answers(n=1)},
                        {"answers": [answers()[0]] * 2}, {"model": "not a model"},
                        {"observation_source": "no values"},
                        {"observed_gross_j": {"unknown": 3}, "observation_source": "fixture"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace(variant(), **changes)

    def test_invalid_observations(self):
        for value in (-1, math.nan, math.inf, True, "1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                variant(observed_gross_j={a.problem_id: value for a in answers()},
                        observation_source="synthetic")
        with self.assertRaisesRegex(ValueError, "observation_source"):
            variant(observed_gross_j={a.problem_id: 1 for a in answers()})

    def test_mismatched_rosters_partial_observations_and_mixed_bases(self):
        cases = [
            [variant(), variant("edit", [replace(a, problem_id="x" + a.problem_id) for a in answers()])],
            [variant(), variant("edit", observed_gross_j={a.problem_id: 1 for a in answers()},
                                observation_source="synthetic")],
            [variant(), variant("edit", model=replace(MODEL, coefficient_basis="above_idle"))],
            [variant(), variant()], [variant("other"), variant("edit")], [variant()],
        ]
        for variants in cases:
            with self.subTest(names=[v.name for v in variants]), self.assertRaises(ValueError):
                analyze(variants)

    def test_invalid_inference_options(self):
        for kwargs in ({"confidence": 0}, {"confidence": 1}, {"confidence": math.nan},
                       {"confidence": True}, {"seed": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                analyze(**kwargs)
        for kwargs in ({"bootstrap_samples": 99}, {"model_id": ""}, {"boundary": "unknown"},
                       {"evaluation_id": ""}, {"baseline": "missing"}):
            params = dict(baseline="base", model_id="synthetic", boundary="dc",
                          evaluation_id="synthetic", bootstrap_samples=100)
            params.update(kwargs)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                analyze_variants([variant(), variant("edit")], **params)


if __name__ == "__main__":
    unittest.main()
