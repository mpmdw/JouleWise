"""Regression tests for the registered dependence-sensitivity calculator."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

from joulewise.aggregate import student_t_critical_95
from joulewise.analysis_engine.estimators import (
    DeterministicBoundTerm,
    PairedObservation,
    StochasticVarianceTerm,
    estimate_paired_blocks,
)
from joulewise.analysis_engine.distributions import student_t_quantile

from scripts import dependence_sensitivity


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "dependence_sensitivity.py"
DOCUMENT = REPO_ROOT / "docs" / "paper" / "round7" / "dependence-sensitivity.md"
EXAMPLE_ARGS = (
    "--block-deltas",
    json.dumps(dependence_sensitivity.EXAMPLE_BLOCK_DELTAS_J, separators=(",", ":")),
    "--floor",
    "3.5",
    "--se-metrology",
    "0.2",
    "--deterministic-bound-total",
    "4.0",
)


class DependenceSensitivityTests(unittest.TestCase):
    def _run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

    def _assert_cli_refuses(self, *arguments: str) -> None:
        completed = self._run(*arguments)
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(completed.stdout, "")

    def _example_payload(self) -> dict[str, Any]:
        completed = self._run("--example")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_worked_example_golden_every_documented_intermediate(self) -> None:
        """Keep every number printed in the worked example aligned with the document."""

        payload = self._example_payload()
        self.assertEqual(payload["schema_version"], "joulewise.dependence_sensitivity.v1")
        self.assertEqual(payload["input"]["registered_alpha"], 0.05)
        self.assertEqual(payload["input"]["se_metrology_j"], 0.2)
        self.assertEqual(payload["input"]["deterministic_bound_total_j"], 4.0)

        summary = payload["summary"]
        self.assertEqual(round(summary["sum_j"], 6), 50.000000)
        self.assertEqual(round(summary["mean_j"], 6), 5.000000)
        self.assertEqual(round(summary["squared_deviations_sum_j2"], 6), 20.250000)
        self.assertEqual(round(summary["sample_stddev_j"], 6), 1.500000)

        rho = payload["ar1_rho_estimator"]
        self.assertEqual(round(rho["numerator"], 6), 4.657971)
        self.assertEqual(round(rho["denominator"], 6), 15.526569)
        self.assertEqual(round(rho["rho_hat"], 6), 0.300000)
        self.assertEqual(
            [round(row["term"], 6) for row in payload["ar1_variance_terms"]],
            [0.270000, 0.072000, 0.018900, 0.004860, 0.001215, 0.000292, 0.000066, 0.000013, 0.000002],
        )

        expected_models = {
            "independent_blocks": {
                "effective_n": 10.000000,
                "degrees_of_freedom": 9,
                "variance_inflation_factor": 1.000000,
                "se_repeat_j": 0.474342,
                "se_total_j": 0.514782,
                "t_critical_95": 2.262,
                "half_width_j": 1.164436,
                "repeat": (3.927039, 6.072961),
                "metrology": (3.835564, 6.164436),
                "decision": (-0.164436, 10.164436),
                "t_statistic": 9.712859,
                "raw_two_sided_p": 0.000004558,
            },
            "ar1_estimated_rho": {
                "effective_n": 5.764703,
                "degrees_of_freedom": 4,
                "variance_inflation_factor": 1.734695,
                "se_repeat_j": 0.624745,
                "se_total_j": 0.655977,
                "t_critical_95": 2.776,
                "half_width_j": 1.820993,
                "repeat": (3.265708, 6.734292),
                "metrology": (3.179007, 6.820993),
                "decision": (-0.820993, 10.820993),
                "t_statistic": 7.622214,
                "raw_two_sided_p": 0.001590617,
            },
            "fixed_effective_n_halving": {
                "effective_n": 5.000000,
                "degrees_of_freedom": 4,
                "variance_inflation_factor": 2.000000,
                "se_repeat_j": 0.670820,
                "se_total_j": 0.700000,
                "t_critical_95": 2.776,
                "half_width_j": 1.943200,
                "repeat": (3.137803, 6.862197),
                "metrology": (3.056800, 6.943200),
                "decision": (-0.943200, 10.943200),
                "t_statistic": 7.142857,
                "raw_two_sided_p": 0.002032095,
            },
        }
        for name, expected in expected_models.items():
            with self.subTest(model=name):
                model = payload["models"][name]
                self.assertEqual(round(model["effective_n"], 6), expected["effective_n"])
                self.assertEqual(model["degrees_of_freedom"], expected["degrees_of_freedom"])
                self.assertEqual(
                    round(model["variance_inflation_factor"], 6),
                    expected["variance_inflation_factor"],
                )
                self.assertEqual(round(model["se_repeat_j"], 6), expected["se_repeat_j"])
                self.assertEqual(model["se_metrology_j"], 0.2)
                self.assertEqual(round(model["se_total_j"], 6), expected["se_total_j"])
                self.assertEqual(model["deterministic_bound_total_j"], 4.0)
                self.assertEqual(model["t_critical_95"], expected["t_critical_95"])
                self.assertEqual(round(model["half_width_j"], 6), expected["half_width_j"])
                self.assertEqual(
                    tuple(round(model["repeat_only_interval_j"][edge], 6) for edge in ("lower", "upper")),
                    expected["repeat"],
                )
                self.assertEqual(
                    tuple(round(model["metrology_aware_interval_j"][edge], 6) for edge in ("lower", "upper")),
                    expected["metrology"],
                )
                self.assertEqual(
                    tuple(round(model["decision_interval_j"][edge], 6) for edge in ("lower", "upper")),
                    expected["decision"],
                )
                self.assertEqual(round(model["t_statistic"], 6), expected["t_statistic"])
                self.assertEqual(round(model["raw_two_sided_p"], 9), expected["raw_two_sided_p"])
                self.assertTrue(model["floor_gate"]["passes"])
                self.assertFalse(model["direction_gate"]["passes"])

    def test_artifact_hashes_and_omits_holm_or_claim_verdict(self) -> None:
        payload = self._example_payload()
        canonical_deltas = json.dumps(
            payload["input"]["block_deltas_j"],
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        canonical_metrology = json.dumps(
            payload["input_authentication"]["metrology_inputs"],
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        self.assertEqual(
            payload["input_authentication"]["block_deltas_json_sha256"],
            hashlib.sha256(canonical_deltas.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            payload["input_authentication"]["metrology_inputs_json_sha256"],
            hashlib.sha256(canonical_metrology.encode("utf-8")).hexdigest(),
        )
        serialized = json.dumps(payload, sort_keys=True).lower()
        self.assertNotIn("holm", serialized)
        self.assertNotIn("support", serialized)

    def test_document_retains_the_registered_contract_and_h30_replacement(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        required_text = (
            "`_v5` is the fixed name",
            "exactly ten complete blocks",
            "does not accept an alpha option",
            "registered composition with \\(n_{\\mathrm{eff}}=n\\)",
            "p_{(1)}\\le0.025",
            "p_{(2)}\\le0.05\\); equality passes",
            "Fixed effective-n halving (a named pessimistic scenario, not a bound)",
            "V=2.600391",
            "n_{\\mathrm{eff}}=3.845576",
            "n_{\\mathrm{eff}}=1.374341",
            "DS-SENS-01",
            "DS-SENS-02",
            "PG-SENS-01",
            "PG-SENS-02",
            "The existing DS-26, DS-31, PG-02, and PG-07 rows keep their suppliers and meanings.",
        )
        for required in required_text:
            with self.subTest(required=required):
                self.assertIn(required, document)
        h30_replacement = (
            "The pulse portion of the calibration bound is the largest of 118 observed onset and offset "
            "excursions from 59 commanded pulses in one capture; the clock-anchor allowance is then "
            "added. Because those pulses share one capture and the paper has not shown independence "
            "across pulse order or between onset and offset errors, this value is reported as the observed "
            "sample maximum, not as a “95/95” population-coverage bound. It is not a deterministic "
            "out-of-sample guarantee."
        )
        self.assertIn(h30_replacement, document)
        definitions = document.index("The **sample mean**")
        table = document.index("| Reported quantity |")
        self.assertLess(definitions, table)
        for required in ("**standard error**", "**critical value**", "**half-width**", "**Student-*t* statistic**", "**variance multiplier**", "**floor gate**", "**direction gate**"):
            with self.subTest(definition=required):
                self.assertLess(document.index(required), table)

    def test_registered_independent_composition_matches_engine_to_one_nanajoule(self) -> None:
        # Minimal engine mapping: a calculator delta becomes value_b - value_a
        # with value_a=0; each block carries paired stochastic variance 0.4,
        # so sum(0.4)/10^2 = 0.04 and se_metrology=0.2.  contrast_bound=4
        # maps directly to the calculator's deterministic_bound_total input.
        stochastic = StochasticVarianceTerm(
            name="sensitivity_metrology",
            variance_a=0.0,
            variance_b=0.4,
            covariance_ab=0.0,
        )
        deterministic = DeterministicBoundTerm(
            name="sensitivity_deterministic",
            bound_a=0.0,
            bound_b=0.0,
            contrast_bound=4.0,
        )
        engine = estimate_paired_blocks(
            tuple(
                PairedObservation(
                    block_id=f"block-{index}",
                    value_a=0.0,
                    value_b=delta,
                    stochastic_terms=(stochastic,),
                    deterministic_terms=(deterministic,),
                )
                for index, delta in enumerate(
                    dependence_sensitivity.EXAMPLE_BLOCK_DELTAS_J, start=1
                )
            )
        )
        calculator = dependence_sensitivity.analyze_deltas(
            dependence_sensitivity.EXAMPLE_BLOCK_DELTAS_J,
            floor_j=3.5,
            se_metrology_j=0.2,
            deterministic_bound_total_j=4.0,
        )["models"]["independent_blocks"]
        for observed, expected in (
            (calculator["metrology_aware_interval_j"]["lower"], engine.metrology_aware_ci95.lower),
            (calculator["metrology_aware_interval_j"]["upper"], engine.metrology_aware_ci95.upper),
            (calculator["decision_interval_j"]["lower"], engine.decision_interval.lower),
            (calculator["decision_interval_j"]["upper"], engine.decision_interval.upper),
        ):
            self.assertAlmostEqual(observed, expected, delta=1.0e-9)

    def test_zero_rho_ar1_collapses_to_registered_independent_composition(self) -> None:
        deltas = [6.0, 5.0, 4.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
        result = dependence_sensitivity.analyze_deltas(
            deltas,
            floor_j=1.0,
            se_metrology_j=0.2,
            deterministic_bound_total_j=0.1,
        )
        self.assertEqual(result["ar1_rho_estimator"]["rho_hat"], 0.0)
        independent = result["models"]["independent_blocks"]
        ar1 = result["models"]["ar1_estimated_rho"]
        self.assertEqual(ar1["effective_n"], independent["effective_n"])
        self.assertEqual(ar1["degrees_of_freedom"], independent["degrees_of_freedom"])
        self.assertEqual(
            ar1["metrology_aware_interval_j"],
            independent["metrology_aware_interval_j"],
        )
        self.assertEqual(ar1["decision_interval_j"], independent["decision_interval_j"])
        # At rho=0, the AR(1) repeat layer is the engine's ordinary repeat
        # layer. The per-block terms use the minimal mapping documented above.
        engine = estimate_paired_blocks(
            tuple(
                PairedObservation(
                    block_id=f"zero-rho-{index}",
                    value_a=0.0,
                    value_b=delta,
                    stochastic_terms=(
                        StochasticVarianceTerm(
                            name="sensitivity_metrology",
                            variance_a=0.0,
                            variance_b=0.4,
                            covariance_ab=0.0,
                        ),
                    ),
                    deterministic_terms=(
                        DeterministicBoundTerm(
                            name="sensitivity_deterministic",
                            bound_a=0.0,
                            bound_b=0.0,
                            contrast_bound=0.1,
                        ),
                    ),
                )
                for index, delta in enumerate(deltas, start=1)
            )
        )
        for observed, expected in (
            (ar1["metrology_aware_interval_j"]["lower"], engine.metrology_aware_ci95.lower),
            (ar1["metrology_aware_interval_j"]["upper"], engine.metrology_aware_ci95.upper),
            (ar1["decision_interval_j"]["lower"], engine.decision_interval.lower),
            (ar1["decision_interval_j"]["upper"], engine.decision_interval.upper),
        ):
            self.assertAlmostEqual(observed, expected, delta=1.0e-9)

    def test_critical_values_match_aggregate_table_for_df_one_to_nine(self) -> None:
        for degrees_of_freedom in range(1, 10):
            with self.subTest(degrees_of_freedom=degrees_of_freedom):
                self.assertEqual(
                    round(student_t_quantile(0.975, degrees_of_freedom), 3),
                    student_t_critical_95(degrees_of_freedom),
                )

    def test_strict_floor_and_direction_boundaries_fail(self) -> None:
        self.assertFalse(
            dependence_sensitivity._model_result(
                name="floor_boundary",
                description="test",
                mean_j=3.5,
                sample_stddev_j=0.0,
                n_blocks=10,
                effective_n=10.0,
                variance_inflation_factor=1.0,
                se_metrology_j=0.0,
                deterministic_bound_total_j=0.0,
                floor_j=3.5,
            )["floor_gate"]["passes"]
        )
        self.assertIsNone(dependence_sensitivity._strict_direction({"lower": 0.0, "upper": 1.0}))
        self.assertIsNone(dependence_sensitivity._strict_direction({"lower": -1.0, "upper": 0.0}))

    def test_public_ar1_guards_are_directly_exercised(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least two blocks"):
            dependence_sensitivity.ar1_variance_inflation_factor(1, 0.0)
        with self.assertRaisesRegex(ValueError, "finite number"):
            dependence_sensitivity.ar1_variance_inflation_factor(10, float("nan"))
        with self.assertRaisesRegex(ValueError, "abs\\(rho\\) < 1"):
            dependence_sensitivity.ar1_variance_inflation_factor(10, 1.0)
        with self.assertRaisesRegex(ValueError, "rho is undefined"):
            dependence_sensitivity.estimate_ar1_rho([1.0] * 10, 1.0)
        with self.assertRaisesRegex(ValueError, "abs\\(rho\\) < 1"):
            dependence_sensitivity.estimate_ar1_rho([1.0, -1.0] * 5, 0.0)

    def test_analyze_guards_are_directly_exercised(self) -> None:
        good = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        with self.assertRaisesRegex(ValueError, "block_deltas_j\\[9\\] must be a finite number"):
            dependence_sensitivity.analyze_deltas(
                good[:-1] + [float("nan")],
                floor_j=1.0,
                se_metrology_j=0.0,
                deterministic_bound_total_j=0.0,
            )
        with self.assertRaisesRegex(ValueError, "exactly ten"):
            dependence_sensitivity.analyze_deltas(good[:-1], floor_j=1.0, se_metrology_j=0.0, deterministic_bound_total_j=0.0)
        with self.assertRaisesRegex(ValueError, "exactly ten"):
            dependence_sensitivity.analyze_deltas(good + [11.0], floor_j=1.0, se_metrology_j=0.0, deterministic_bound_total_j=0.0)
        with self.assertRaisesRegex(ValueError, "floor_j must be non-negative"):
            dependence_sensitivity.analyze_deltas(good, floor_j=-0.1, se_metrology_j=0.0, deterministic_bound_total_j=0.0)
        with self.assertRaisesRegex(ValueError, "se_metrology_j must be a finite number"):
            dependence_sensitivity.analyze_deltas(good, floor_j=1.0, se_metrology_j=float("nan"), deterministic_bound_total_j=0.0)
        with self.assertRaisesRegex(ValueError, "se_metrology_j must be non-negative"):
            dependence_sensitivity.analyze_deltas(good, floor_j=1.0, se_metrology_j=-0.1, deterministic_bound_total_j=0.0)
        with self.assertRaisesRegex(ValueError, "deterministic_bound_total_j must be non-negative"):
            dependence_sensitivity.analyze_deltas(good, floor_j=1.0, se_metrology_j=0.0, deterministic_bound_total_j=-0.1)
        with self.assertRaisesRegex(ValueError, "rho is undefined"):
            dependence_sensitivity.analyze_deltas([1.0] * 10, floor_j=1.0, se_metrology_j=0.0, deterministic_bound_total_j=0.0)
        with self.assertRaisesRegex(ValueError, "abs\\(rho\\) < 1"):
            dependence_sensitivity.analyze_deltas([1.0, -1.0] * 5, floor_j=1.0, se_metrology_j=0.0, deterministic_bound_total_j=0.0)
        with self.assertRaisesRegex(ValueError, "effective sample size leaves fewer"):
            dependence_sensitivity._degrees_of_freedom(10, 1.9)

    def test_cli_refuses_each_invalid_input_with_exit_two_and_empty_stdout(self) -> None:
        base = ["--floor", "1.0", "--se-metrology", "0.2", "--deterministic-bound-total", "0.1"]
        refusal_cases = {
            "four_blocks": ["--block-deltas", "[1,2,3,4]", *base],
            "eleven_blocks": ["--block-deltas", "[1,2,3,4,5,6,7,8,9,10,11]", *base],
            "nonfinite_delta": ["--block-deltas", "[1,2,3,4,5,6,7,8,9,NaN]", *base],
            "constant_sequence": ["--block-deltas", "[1,1,1,1,1,1,1,1,1,1]", *base],
            "perfect_alternation": ["--block-deltas", "[1,-1,1,-1,1,-1,1,-1,1,-1]", *base],
            "five_blocks_effective_n": ["--block-deltas", "[0.461096,0.575454,0.238990,0.073144,-0.228373]", *base],
            "negative_floor": ["--block-deltas", "[1,2,3,4,5,6,7,8,9,10]", "--floor", "-0.1", "--se-metrology", "0.2", "--deterministic-bound-total", "0.1"],
            "nonfinite_metrology_se": ["--block-deltas", "[1,2,3,4,5,6,7,8,9,10]", "--floor", "1.0", "--se-metrology", "nan", "--deterministic-bound-total", "0.1"],
            "negative_deterministic_total": ["--block-deltas", "[1,2,3,4,5,6,7,8,9,10]", "--floor", "1.0", "--se-metrology", "0.2", "--deterministic-bound-total", "-0.1"],
            "caller_alpha": ["--example", "--alpha", "0.10"],
            "missing_metrology": ["--block-deltas", "[1,2,3,4,5,6,7,8,9,10]", "--floor", "1.0"],
        }
        for name, arguments in refusal_cases.items():
            with self.subTest(name=name):
                self._assert_cli_refuses(*arguments)

    def test_fixed_alpha_is_printed_and_cli_has_no_alpha_option(self) -> None:
        result = dependence_sensitivity.analyze_deltas(
            dependence_sensitivity.EXAMPLE_BLOCK_DELTAS_J,
            floor_j=3.5,
            se_metrology_j=0.2,
            deterministic_bound_total_j=4.0,
        )
        self.assertEqual(result["input"]["registered_alpha"], dependence_sensitivity.REGISTERED_ALPHA)
        self.assertEqual(dependence_sensitivity.REGISTERED_ALPHA, 0.05)
        self._assert_cli_refuses(*EXAMPLE_ARGS, "--alpha", "0.05")

    def test_ar1_multiplier_widens_as_rho_grows(self) -> None:
        low_rho = dependence_sensitivity.ar1_variance_inflation_factor(10, 0.1)
        high_rho = dependence_sensitivity.ar1_variance_inflation_factor(10, 0.5)
        self.assertGreater(high_rho, low_rho)
        self.assertEqual(round(high_rho, 6), 2.600391)
        self.assertTrue(math.isfinite(high_rho))


if __name__ == "__main__":
    unittest.main()
