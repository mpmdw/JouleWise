"""BYTES worked examples and synthetic archive tests; never run inference."""
from __future__ import annotations

import contextlib
import copy
import csv
import hashlib
import io
import json
import math
import os
import random
import statistics
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise import bytes_analysis as ba
from joulewise.external import km003c_parse as kp
from scripts import bytes_analyze

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/bytes"


class NumericTestCase(unittest.TestCase):
    def assertAlmostEqual(self, first, second, places=None, msg=None, delta=None):
        # With no printed half-width, the brief specifies 1e-6 relative or
        # absolute in the quantity's unit. This replaces magnitude-blind seven
        # decimal places, including in the small hand-worked examples.
        if delta is None:
            delta = 1e-6 * max(1.0, abs(first), abs(second))
        return super().assertAlmostEqual(first, second, msg=msg, delta=delta)


def assert_d3_exercised(test, records, manifest):
    """Run the competing D3 method: substitute rails allowance AND scale."""
    changed = []
    for record in records:
        refs = record["neg8_inputs"]
        changed.append(dict(record, neg8_inputs={**refs, "boundaries": {
            **refs["boundaries"], "rest": refs["boundaries"]["rails"]}}))
    correct, substituted = [], []
    for inclusive in (False, True):
        correct += ba.reduce_models(records, manifest, inclusive=inclusive, boundaries=("rest",))
        substituted += ba.reduce_models(changed, manifest, inclusive=inclusive, boundaries=("rest",))
    # Check both passes and their primary mean, both idle families and both
    # selections: ten models * (two passes + mean) * two bases * two selections.
    pairs = list(zip(correct, substituted)) + list(zip(ba.combine_passes(correct), ba.combine_passes(substituted)))
    test.assertEqual(len(pairs), len(manifest["models"]) * 3 * 2 * 2)
    ratios, agreement_bars = [], []
    for actual, wrong in pairs:
        test.assertEqual(actual["status"], "computed")
        test.assertEqual(wrong["status"], "computed")
        gap = abs(actual["B_j"] - wrong["B_j"])
        label = (actual["model"], actual.get("pass_id", "mean"), actual["basis"], actual["selection"])
        # P3/Addendum 8.4: at least 10% of rest B, ten 1%-B bars.
        test.assertGreaterEqual(gap, .10 * actual["B_j"], label)
        # The actual energy agreement bar is 1% of (h+B), Addendum 8.1/5.
        # Ensure this fixture clears ten of those bars too, including h.
        test.assertGreaterEqual(gap, 10 * .01 * (actual["h_j"] + actual["B_j"]), label)
        ratios.append(gap / actual["B_j"])
        agreement_bars.append(gap / (.01 * (actual["h_j"] + actual["B_j"])))
    return {"rest_cells": len(pairs), "min_gap_over_B": min(ratios),
            "min_agreement_bars": min(agreement_bars)}



def cli_stage_chain(root, manifest):
    """Run the real CLI with actual key releases and an immutable commitment."""
    _write_json(root / "manifest.json", manifest)
    args = [sys.executable, str(ROOT / "scripts/bytes_analyze.py"),
            "--export", str(root / "export"), "--manifest", str(root / "manifest.json")]
    def stage(name, output, predictions=None):
        command = args + ["--stage", name, "--out", str(output)]
        if predictions is not None:
            command += ["--predictions", str(predictions)]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
    stage("blinded", root / "blinded")
    release_keys(root, manifest, "fit")
    # The CLI calls stages 1 and 2 fit and heldout; those are the registered stages.
    stage("fit", root / "stage1")
    predictions = root / "stage1/predictions.json"
    commitment = predictions.read_bytes()
    release_keys(root, manifest, "all")
    stage("heldout", root / "out", predictions)
    # Exact identity is the property: stage 2 must never rewrite predictions.
    assert predictions.read_bytes() == commitment
    assert predictions.with_suffix(".sha256").read_text().strip() == hashlib.sha256(commitment).hexdigest()
    return root / "out"


def fit_points():
    return [{"bytes": x, "resident": x, "time": x, "e": 2 * x,
             "lower": 2 * x - 1, "upper": 2 * x + 1} for x in (1, 2, 3)]


def query(b=2, r=10, t=20, e=4, width=0):
    return {"bytes": b, "resident": r, "time": t, "e": e,
            "lower": e - width, "upper": e + width}


class H1WorkedExamples(NumericTestCase):
    def test_line_and_all_eight_corners_by_hand(self):
        frozen = ba.freeze_lines(fit_points())
        self.assertEqual(frozen["bytes"]["line"], [0, 2])
        self.assertEqual(len(frozen["bytes"]["corners"]), 8)
        # x=4 prediction weights are [-2/3, 1/3, 4/3].
        expected = [7, 29 / 3, 23 / 3, 31 / 3, 17 / 3, 25 / 3, 19 / 3, 9]
        for coefficient, value in zip(frozen["bytes"]["corners"], expected):
            self.assertAlmostEqual(ba.predict(coefficient, 4), value)
        result = ba.h1_point(frozen, query(b=4, e=8))
        self.assertAlmostEqual(result["checks"][0]["prediction_lower"], 17 / 3)
        self.assertAlmostEqual(result["checks"][0]["prediction_upper"], 31 / 3)

    def test_every_word_and_log_ratio(self):
        frozen = ba.freeze_lines(fit_points())
        examples = [(query(), "bytes"), (query(b=10, r=2), "resident"),
                    (query(b=10, t=2), "time"), (query(r=2), "unresolved"),
                    (query(b=10), "neither")]
        for point, expected in examples:
            with self.subTest(word=expected):
                result = ba.h1_point(frozen, point)
                self.assertEqual(result["word"], expected)
                for check in result["checks"]:
                    self.assertAlmostEqual(check["log_ratio"], math.log(point["e"] / check["predicted"]))

    def test_interval_touching_counts_as_consistent(self):
        frozen = ba.freeze_lines(fit_points())
        self.assertTrue(ba.h1_point(frozen, query(e=5))["checks"][0]["consistent"])
        self.assertFalse(ba.h1_point(frozen, query(e=5.000001))["checks"][0]["consistent"])

    def test_negative_diagnostic_is_kept_and_log_is_explicit(self):
        frozen = ba.freeze_lines(fit_points())
        result = ba.h1_point(frozen, query(e=-2))
        self.assertEqual(result["word"], "neither")
        self.assertEqual(result["checks"][0]["log_status"], "undefined_nonpositive")
        self.assertIsNone(result["checks"][0]["log_ratio"])

    def test_active_resident_mixed_and_misses(self):
        frozen = ba.freeze_lines(fit_points())
        active = ba.h1_point(frozen, query())
        resident = ba.h1_point(frozen, query(e=20))
        mixed = ba.h1_point(frozen, query(r=2))
        for result, word in ((active, "active"), (resident, "resident"), (mixed, "mixed")):
            answer = ba.active_or_resident([(str(i), result) for i in range(3)])
            self.assertEqual(answer["answer"], word)
            self.assertEqual(len(answer["misses"]), 3)

    def test_singular_fit_and_wrong_counts_refuse(self):
        with self.assertRaises(ba.AnalysisError):
            ba.line([1, 1], [1, 2])
        with self.assertRaises(ba.AnalysisError):
            ba.freeze_lines(fit_points()[:2])
        with self.assertRaises(ba.AnalysisError):
            ba.active_or_resident([])


class H2WorkedExamples(NumericTestCase):
    def test_two_term_hand_computed(self):
        # Centered x [-2,-1,0,1,2]; residuals [1,-2,2,-2,1] are orthogonal
        # to intercept and x. beta=[3,2], SSE=14, MSE=14/3, Sxx=10.
        fit = ba.ols([[x] for x in range(5)], [4, 3, 9, 7, 12], family_size=1)
        self.assertAlmostEqual(fit["coefficients"][0], 3)
        self.assertAlmostEqual(fit["coefficients"][1], 2)
        self.assertAlmostEqual(fit["mse"], 14 / 3)
        self.assertAlmostEqual(fit["ols_covariance"][1][1], 7 / 15)
        # t(0.975) at df 3: family 1, n - p = 5 - 2.
        self.assertAlmostEqual(fit["critical"], 3.182446305)
        half = fit["critical"] * math.sqrt(fit["covariance"][1][1])
        self.assertAlmostEqual(fit["intervals"][1][0], 2 - half)
        self.assertAlmostEqual(fit["intervals"][1][1], 2 + half)
        delta = ba.deviation(fit, [2], 8)
        self.assertAlmostEqual(delta["deviation_w"], 1)
        self.assertAlmostEqual(delta["upper_w"] - 1, fit["critical"] * math.sqrt(14 / 3 + (2*(1/.4)**2 + 2*(2/.7)**2 + (2/.8)**2)/25))

    def test_extended_and_rest_coefficients_by_orthogonal_design(self):
        # All eight corners of a cube; x1,x2 and noise x3 are orthogonal.
        rows = [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
        fit = ba.ols([[a, b] for a, b, _ in rows], [5 + 2*a + 3*b + c for a, b, c in rows])
        for actual, expected in zip(fit["coefficients"], (5, 2, 3)):
            self.assertAlmostEqual(actual, expected)
        self.assertAlmostEqual(fit["mse"], 8 / 5)
        for i in range(3):
            self.assertAlmostEqual(fit["ols_covariance"][i][i], 1 / 5)
        self.assertEqual(fit["family_size"], 9)
        self.assertGreater(fit["critical"], ba.student_t_quantile(.975, 5))

    def test_inverse_guard_scales_with_matrix_and_leverage_refuses(self):
        # Scaling the same well-conditioned Gram matrix must not turn it
        # singular. 1e-14 is below the old absolute 1e-12 cutoff; the
        # condition number remains one, so no precision is lost.
        for scale in (1.0, 1e-14, 1e14):
            inverse = ba._inverse([[scale, 0.0], [0.0, scale]])
            for i in range(2):
                for j in range(2):
                    self.assertAlmostEqual(inverse[i][j] * scale, float(i == j))
        # A unique nonzero predictor is an exact unit-leverage row: HC3's
        # divisor 1-h is zero at floating-point resolution.
        with self.assertRaisesRegex(ba.AnalysisError, "unit leverage"):
            ba.ols([[0], [0], [0], [0], [1]], [1, 2, 1, 2, 3])

    def test_scale_invariance_and_singular_refusal(self):
        fit = ba.ols([[x * 1e9] for x in range(5)], [4, 3, 9, 7, 12])
        self.assertAlmostEqual(fit["coefficients"][1] * 1e9, 2)
        with self.assertRaises(ba.AnalysisError):
            ba.ols([[x, 2*x] for x in range(5)], list(range(5)))


class MeterWorkedExamples(NumericTestCase):
    def stream(self, watts=None):
        # Exact host/device clock line, with two batches; parse calls clock_fit.
        samples = kp.Samples([i * 100 for i in range(101)], [1] * 101,
                             watts or [10] * 101, [0] * 51 + [1] * 50, 0, 100)
        batches = [{"tx": 5_000_000_000, "rx": 5_000_000_000, "n": 51},
                   {"tx": 10_000_000_000, "rx": 10_000_000_000, "n": 50}]
        fit = kp.clock_fit(samples, batches)
        return kp.Stream({"start_raw_ns": 0, "start_mono_ns": 0},
            {"end_raw_ns": 10_000_000_000, "end_mono_ns": 10_000_000_000},
            batches, [], samples, fit, [fit.host_ns(d) for d in samples.dev_ms],
            samples.watts, [], [])

    def test_gross_own_idle_and_phase_edge_bound(self):
        result = ba.meter_decode(self.stream(), [4_000_000_000, 6_000_000_000],
                                 [1_000_000_000, 3_000_000_000])
        self.assertAlmostEqual(result["gross_j"], 20)
        self.assertAlmostEqual(result["secondary_j"], 0)
        self.assertAlmostEqual(result["phase_edge_j"], 2)
        self.assertEqual(result["n"], 20)

    def test_negative_residual_extreme_and_containing_edge_samples(self):
        stream = self.stream([20] * 40 + [10] * 20 + [30] * 41)
        stream.fit.stats.update(excess_latency_ms_min=-7, excess_latency_ms_max=3)
        result = ba.meter_decode(stream, [4_000_000_001, 6_000_000_001],
                                 [1_000_000_000, 3_000_000_000])
        self.assertAlmostEqual(result["secondary_j"], -18)
        self.assertEqual(result["edge_powers_w"], [10, 30])
        self.assertAlmostEqual(result["r_max_s"], .007)
        self.assertAlmostEqual(result["phase_edge_j"], 40 * .107)

    def test_missing_fit_mapping_empty_span_and_coverage_refuse(self):
        for mutation in (lambda s: setattr(s, "header", {}), lambda s: setattr(s, "fit", None)):
            stream = self.stream()
            mutation(stream)
            with self.assertRaises(ba.AnalysisError):
                ba.meter_decode(stream, [4_000_000_000, 6_000_000_000], [1, 2])
        with self.assertRaises(ba.AnalysisError):
            ba.meter_decode(self.stream(), [-1, 6_000_000_000], [1, 2])


class RegisteredArithmeticTests(NumericTestCase):
    def estimate(self, repeats, means):
        bounds = dict(zip(ba.BOUND_KINDS, (.01, 0, .05)))
        return ba.estimate_phase_energy(repeats, [[v] * 4 for v in means],
            [bounds] * len(repeats), [[bounds] * 4 for _ in means])

    def test_plan_full_and_removed_worked_examples(self):
        repeats = [10, 10.2, 9.9, 10.1, 10, 10.3, 9.8, 10.1, 10, 9.6]
        blocks = [10.4, 10.1, 10.3, 10.2, 10.5, 10, 10.2, 10.3, 10.1, 9.9]
        full = self.estimate(repeats, blocks)
        reduced = self.estimate(repeats[:5] + repeats[6:], [v for i,v in enumerate(blocks) if i not in (4,8)])
        for actual, mean, variance, df, endpoints in (
            (full, 10.16, .00229333333333333, 9, (9.9917, 10.3283)),
            (reduced, 10.1333333333333, .00237301587301587, 7, (9.9581, 10.3085))):
            self.assertAlmostEqual(actual["mean_j"], mean)
            self.assertAlmostEqual(actual["interval"]["variance"], variance)
            self.assertAlmostEqual(actual["interval"]["B_j"], .06)
            self.assertEqual(actual["interval"]["df"], df)
            # The registered worked endpoints are printed to four decimals:
            # half a 0.0001 J last digit is 0.00005 J, inside the stated
            # [2.2e-6, 1.3e-4] J admissible absolute-energy window.
            self.assertAlmostEqual(actual["lower_j"], endpoints[0], delta=.00005)
            self.assertAlmostEqual(actual["upper_j"], endpoints[1], delta=.00005)

    def test_equivalence_every_registered_shape_1200_random_inputs_and_worked_full(self):
        from joulewise import paper_reported_energy as registered
        from tests.test_paper_reported_energy import synthetic_input
        rng = random.Random(20261015)
        comparisons = 0
        for model in registered.MODELS:
            for length in registered.PREFILL_LADDER_PROMPT_TOKENS:
                fixture = synthetic_input(model, length)
                for cell, data in zip(fixture["spec"]["reported_energy_cells"], fixture["cells"]):
                    # Both model identities, all ladder phase/length shapes, 50
                    # independent random inputs each, plus the plan full example.
                    for trial in range(51):
                        rows = copy.deepcopy(data["rows"])
                        for i, row in enumerate(rows):
                            row["energy_j"] = rng.uniform(0, 10000) if trial else (
                                [10,10.2,9.9,10.1,10,10.3,9.8,10.1,10,9.6][i] if i < 10 else
                                [10.4,10.1,10.3,10.2,10.5,10,10.2,10.3,10.1,9.9][(i-10)//4])
                            row["bounds_j"] = {k: rng.random() for k in ba.BOUND_KINDS} if trial else dict(zip(ba.BOUND_KINDS,(.01,0,.05)))
                        expected = registered._project_cell(cell, rows, data["binding"])
                        actual = ba.estimate_phase_energy([r["energy_j"] for r in rows[:10]],
                            [[r["energy_j"] for r in rows[i:i+4]] for i in range(10,50,4)],
                            [r["bounds_j"] for r in rows[:10]],
                            [[r["bounds_j"] for r in rows[i:i+4]] for i in range(10,50,4)])
                        for key in ("mean_j", "lower_j", "upper_j"):
                            self.assertEqual(actual[key], expected[key])
                        for key in ("variance", "h_j", "B_j", "kind_averages_j"):
                            self.assertEqual(actual["interval"][key], expected["interval"][key])
                        comparisons += 1
        self.assertEqual(comparisons, 1224)  # Exact float equality, no tolerance needed.

    def test_general_counts_negative_secondary_and_stratified_bounds(self):
        for n_r,n_b in ((5,5),(5,9),(9,5),(17,23)):
            value = self.estimate([-10] * n_r, [-20] * n_b)
            self.assertEqual(value["mean_j"], -18)
            self.assertAlmostEqual(value["interval"]["B_j"], .06)
            self.assertEqual(value["interval"]["df"], min(n_r,n_b)-1)
        rows = [{"stratum":"repeat", "unit_id":str(i)} for i in range(5)] + [
            {"stratum":"quad", "unit_id":str(i)} for i in range(8) for _ in range(4)]
        bounds = [dict.fromkeys(ba.BOUND_KINDS, v) for v in [1]*5+[2]*32]
        result = ba._registered_estimate(rows, [-1]*37, bounds)
        self.assertAlmostEqual(result["interval"]["B_j"], 5.4)
        with self.assertRaises(ba.AnalysisError):
            ba.estimate_phase_energy([1]*4, [[1]*4]*5, bounds[:4], [bounds[:4]]*5)
        del bounds[0][ba.BOUND_KINDS[0]]
        with self.assertRaises(ba.AnalysisError):
            ba._registered_estimate(rows, [-1]*37, bounds)


class BoundaryAndStagingTests(NumericTestCase):
    def points(self):
        points = []
        for selection in ("primary", "flagged-inclusive"):
            for basis in ("gross primary", "idle-subtracted secondary"):
                for boundary in ba.BOUNDARIES:
                    for i in range(3):
                        points.append({"model": "fit-" + str(i), "selection": selection,
                            "basis": basis, "boundary": boundary, "bytes": i + 1,
                            "resident": i + 1, "time": (i + 1) / 100,
                            "e": 2 * (i + 1), "lower": 2 * (i + 1) - .1,
                            "upper": 2 * (i + 1) + .1, "BW": 100,
                            "power": 200, "tier": True, "role": "fit"})
        return points

    def test_predictions_only_fit_and_hash_is_exact_file_bytes(self):
        frozen = ba.frozen_predictions(self.points(), {"models": []})
        self.assertEqual(len(frozen["rival_lines"]), 12)
        self.assertEqual(len(frozen["fit_points"]), 36)
        self.assertTrue(all(p["role"] == "fit" for p in frozen["fit_points"]))
        with tempfile.TemporaryDirectory() as directory:
            sha = ba.write_predictions(directory, frozen)
            path = Path(directory) / "predictions.json"
            self.assertEqual(sha, hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(ba.read_predictions(path, {"models": []}), (frozen, sha))
            before = path.read_bytes()
            with self.assertRaises(ba.AnalysisError):
                ba.write_predictions(directory, frozen)
            self.assertEqual(path.read_bytes(), before)
            path.write_bytes(before + b" ")
            with self.assertRaisesRegex(ba.AnalysisError, "SHA-256"):
                ba.read_predictions(path, {"models": []})

    def test_heldout_data_cannot_enter_freeze(self):
        points = self.points()
        points[0]["role"] = "heldout"
        with self.assertRaisesRegex(ba.AnalysisError, "held-out"):
            ba.frozen_predictions(points, {})

    def test_changed_manifest_refuses_commitment(self):
        with tempfile.TemporaryDirectory() as directory:
            ba.write_predictions(directory, ba.frozen_predictions(self.points(), {}))
            with self.assertRaisesRegex(ba.AnalysisError, "manifest"):
                ba.read_predictions(Path(directory) / "predictions.json", {"changed": True})

    def test_units_atomic_thermal_exclusion_minimum_and_sensitivity(self):
        records = []
        for i in range(50):
            records.append({"run_id": str(i), "stratum": "repeat" if i < 10 else "quad",
                "unit_id": str(i if i < 10 else (i - 10) // 4),
                "excluded": i == 10, "status": "succeeded"})
        kept, removed = ba._kept(records, False)
        self.assertEqual(len(kept), 46)
        self.assertEqual(removed, ["10", "11", "12", "13"])
        self.assertEqual(len(ba._kept(records, True)[0]), 50)
        records[10]["invalid_energy_record"] = True
        self.assertEqual(len(ba._kept(records, True)[0]), 46)
        records[10]["invalid_energy_record"] = False
        for r in records[:6]:
            r["excluded"] = True
        with self.assertRaisesRegex(ba.AnalysisError, "five"):
            ba._kept(records, False)

    def test_weighted_duration_uses_unit_means(self):
        rows = [{"stratum": "repeat", "unit_id": str(i)} for i in range(5)]
        rows += [{"stratum": "quad", "unit_id": str(i)} for i in range(8) for j in range(4)]
        self.assertEqual(ba._weighted(rows, [10] * 5 + [20] * 32), 18)

    def test_h2_named_family_tier_deviations_and_rest_lambda(self):
        points = []
        for i in range(10):
            bw = 10 + i * 3
            tau = .1 + .013 * i * i
            resident = 1 + .4 * i + (i % 3)
            points.append({"model": str(i), "BW": bw, "resident": resident,
                "time": tau, "power": 4 + .2 * bw + .1 * (i % 3),
                "tier": i < 6, "boundary": "rails"})
        rails = {p["model"]: p["power"] for p in points}
        primary = []
        for boundary in ba.BOUNDARIES:
            rows = copy.deepcopy(points)
            for i, p in enumerate(rows):
                p["boundary"] = boundary
                if boundary == "rest":
                    p["power"] = 2 + .3 * p["BW"] + .4 * rails[p["model"]] + .01 * (i % 2)
            result = ba.h2(rows, rails)
            self.assertEqual(len(result["tier_deviations"]), 4)
            self.assertEqual(len(result["loo_description"]), 10)
            self.assertIsInstance(result["resident_adds_nothing"], bool)
            primary += result["primary_intervals"]
            if boundary == "rest":
                # Synthetic recovery is judged by this coefficient's own
                # ruled HC3 half-width, not an invented lambda tolerance.
                half = (result["rest"]["intervals"][2][1] - result["rest"]["intervals"][2][0]) / 2
                self.assertAlmostEqual(result["rest"]["coefficients"][2], .4, delta=half)
        self.assertEqual(len(primary), 29)

    def test_resident_adds_nothing_rule_positive_negative_and_zero(self):
        for rho, expected in ((3, False), (-3, True), (0, True)):
            points = []
            for i in range(10):
                bw = i + 1
                resident = 2 + i % 3
                power = 20 + 2 * bw + rho * resident
                # Orthogonal-ish nonzero noise gives the zero-rho fit a real interval.
                if rho == 0:
                    power += .01 * (-1) ** i
                points.append({"model": str(i), "BW": bw, "resident": resident,
                    "time": 1, "power": power, "tier": i < 6, "boundary": "rails"})
            result = ba.h2(points, {p["model"]: p["power"] for p in points})
            self.assertEqual(result["resident_adds_nothing"], expected)

    def test_join_uses_harvest_bound_and_existing_reducer_seam(self):
        from decimal import Decimal
        from joulewise.b6 import calibration
        from tests.b6.support import document
        cal = calibration.evaluate(calibration.Capture(Decimal(".028"), "valid"),
            calibration.Capture(Decimal(".048"), "valid"), document(), [], [], False)
        self.assertEqual(cal["operative_bound_s"], "0.068")
        summary = {"status":"succeeded", "energy_anchor_shift_envelopes":{
            "/phase_energy_j/decode":{"max_abs_delta_j":7}}}
        with patch("joulewise.reduce._rederive_summary_for_authenticated_fiducial_bound", return_value=summary) as seam:
            result, provenance = ba.operative_summary(Path("bundle"), {"calibration":cal})
        self.assertEqual(result, summary)
        self.assertEqual(seam.call_args.kwargs["authenticated_fiducial_bound_s"], .068)
        self.assertEqual(provenance["status"], "rereduced")
        with self.assertRaisesRegex(ba.AnalysisError, "calibration.operative_bound_s"):
            ba.operative_summary(Path("bundle"), {})

    def test_native_operative_reduction_widens_envelope_without_writing_bundle(self):
        from decimal import Decimal
        from joulewise.b6 import calibration
        from tests.b6.support import document
        from tests.test_p2038_production_path import P2038ProductionPathTests
        with tempfile.TemporaryDirectory() as directory:
            bundle, original = P2038ProductionPathTests().run_mode(Path(directory)/"native", "normal")
            before = {str(p.relative_to(bundle)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in bundle.rglob("*") if p.is_file()}
            cal = calibration.evaluate(calibration.Capture(Decimal(".060"), "valid"),
                calibration.Capture(Decimal(".028"), "valid"), document(), [], [], False)
            summary, provenance = ba.operative_summary(bundle, {"calibration":cal})
            self.assertEqual(provenance, {"status":"rereduced","operative_bound_s":.092})
            env = summary["energy_anchor_shift_envelopes"]["/phase_energy_j/decode"]
            self.assertGreater(env["max_abs_delta_j"], original.energy_anchor_shift_envelopes["/phase_energy_j/decode"]["max_abs_delta_j"])
            after = {str(p.relative_to(bundle)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in bundle.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            with self.assertRaisesRegex(ba.AnalysisError,"no decode envelope"):
                ba.operative_summary(bundle,{"calibration":{"operative_bound_s":"0"}})

    def test_import_has_no_mlx_or_collection_dependency(self):
        import subprocess
        import sys
        result = subprocess.run([sys.executable, "-B", "-c",
            "import sys; import joulewise.bytes_analysis; "
            "assert not any(m.startswith(('mlx', 'joulewise.controller', 'joulewise.adapters.mlx')) for m in sys.modules)"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")


# Keep this importable name for the reviewer's independent probes.
import importlib.util
_campaign_spec = importlib.util.spec_from_file_location("bytes_campaign", FIXTURES / "campaign.py")
_campaign = importlib.util.module_from_spec(_campaign_spec)
_campaign_spec.loader.exec_module(_campaign)
archive_campaign = _campaign.archive_campaign
release_keys = _campaign.release_keys


class ProductionArchiveTests(NumericTestCase):
    def test_nr1_offset_term_covers_constant_label_offset(self):
        fits, diagnostics = {}, {}
        for latency in (0, 10):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                manifest = archive_campaign(root, world="resident", seed=3100,
                    non_claim=False, release="none", sample_phase_ms=50, edge_phase=True,
                    min_receive_latency_ms=latency)
                output = cli_stage_chain(root, manifest)
                records = ba.load_records(root / "export", manifest, stage="all")
                rows = ba.read_json(output / "h2.json")
                fits[latency] = {row["boundary"]: row["resident_extended"] for row in rows
                    if row["selection"] == "primary" and row["basis"] == "gross primary"}
                # Integer microW payload rounding can change integrated energy by
                # at most 0.5 microW * T. Anything larger is a whole-sample flip.
                flips = sum(abs(r["meter"]["gross_j"] - 2 * r["rails_j"]) >
                            .5e-6 * r["duration_s"] for r in records)
                diagnostics[latency] = {"runs": len(records), "flips": flips,
                    "label_offset_s": manifest["synthetic_parameters"]["min_receive_latency_ms"] / 1000,
                    "sample_interval_s": records[0]["meter"]["sample_interval_s"],
                    "max_error_j": max(abs(r["meter"]["gross_j"] - 2 * r["rails_j"]) for r in records)}
        for boundary in ("DC input", "rest"):
            shifted, clean = fits[10][boundary], fits[0][boundary]
            # (a) The ruling's exercise bar is 1% of the HC3 ruled half-width,
            # Addendum 8. No tighter bar is chosen to expose the effect.
            bar = .01 * shifted["critical"] * shifted["standard_errors"][1]
            self.assertGreater(abs(shifted["coefficients"][1] - clean["coefficients"][1]), bar)
            # (b) Structural epsilon is exactly zero in this resident world.
            # Containment is the interval's decision rule, with no extra tolerance.
            for key in ("offset_intervals", "offset_ols_intervals"):
                lo, hi = shifted[key][1]
                self.assertLessEqual(lo, 0)
                self.assertGreaterEqual(hi, 0)
        # (c) A uniform science-edge phase flips with p=delta/Delta_t.
        # The ruling specifies three binomial standard errors, not a tuned bar.
        shifted = diagnostics[10]
        p = shifted["label_offset_s"] / shifted["sample_interval_s"]
        n = diagnostics[10]["runs"]
        self.assertLessEqual(abs(diagnostics[10]["flips"] / n - p),
                             3 * math.sqrt(p * (1 - p) / n))
        print("BYTES_NR1_COUNTEREXAMPLE=" + json.dumps({"diagnostics": diagnostics,
            "fits": fits}, sort_keys=True), flush=True)

    def test_synthetic_harvest_export_release_chain_uses_cli_processes(self):
        from collections import Counter
        from joulewise.b6 import blinding, export_runs

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # R2: ten full modules, 50 science members per model per pass.
            # Reuse A7.12's counterexamples: doubled pass duration and signed
            # (-8, +3) ms latency, whose negative extreme is the larger one.
            with patch.object(export_runs, "export", wraps=export_runs.export) as exported:
                manifest = archive_campaign(root, non_claim=False, release="none",
                                            pass_duration_scales=(1, 2), clock_latency_ms=(-8, 3))
            self.assertEqual(exported.call_count, len(manifest["sessions"]))
            for session in manifest["sessions"]:
                prefix = root / "export/bytes" / session["session_id"]
                sidecar = ba.read_json(prefix.with_suffix(".session.json"))
                self.assertTrue(sidecar["blinding"]["applied"])
                with prefix.with_suffix(".runs.csv").open(newline="") as stream:
                    rows = list(csv.DictReader(stream))
                self.assertEqual(Counter(r["model_name"] for r in rows if r["role"] == "science"),
                                 Counter({m["model"]: 50 for m in manifest["models"]}))
                self.assertEqual(Counter(r["role"] for r in rows if r["role"] != "science"),
                                 Counter({"corpus": 6, "start": 3, "midpoint": 1, "end": 3}))
                meter = Path(session["archive"]) / "sources/night-custody/hazards/meter/stream-001.jsonl"
                with meter.open() as stream:
                    # Native KM003C rate_idx 1 denotes the required 10 Hz.
                    self.assertEqual(json.loads(next(stream))["rate_idx"], 1)
            _write_json(root / "manifest.json", manifest)
            args = [sys.executable, str(ROOT / "scripts/bytes_analyze.py"),
                    "--export", str(root / "export"), "--manifest", str(root / "manifest.json")]

            def analyze(stage, out, *, predictions=None, expected=0):
                command = args + ["--stage", stage, "--out", str(root / out)]
                if predictions is not None:
                    command += ["--predictions", str(predictions)]
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

            private = root / "private-keys/bytes/blinding"
            released = root / "released-keys/bytes/blinding"
            self.assertEqual(list(released.iterdir()), [])
            analyze("blinded", "blinded")
            blinded = ba.read_json(root / "blinded/model_estimates.json")
            self.assertTrue(blinded)
            self.assertEqual({p["boundary"] for p in blinded}, {"rails"})
            analyze("fit", "unreleased-fit", expected=1)

            # The current CLI spells stages 1/2 "fit"/"heldout". Release actual
            # key files into the authoritative directory; never pass decoded
            # records or call an analysis-stage function from this test.
            fit_keys = {"neg8_reference", *(m["model"] + "|bytes-synthetic|512"
                        for m in manifest["models"] if m["role"] == "fit")}
            fit_files = {"pack.json", *(blinding._config_filename(k) for k in fit_keys)}
            for name in sorted(fit_files):
                shutil.copyfile(private / name, released / name)
            self.assertEqual({p.name for p in released.iterdir()}, fit_files)
            analyze("fit", "stage1")
            predictions = root / "stage1/predictions.json"
            commitment = predictions.read_bytes()
            self.assertEqual((root / "stage1/predictions.sha256").read_text().strip(),
                             hashlib.sha256(commitment).hexdigest())
            frozen = json.loads(commitment)
            self.assertEqual(frozen["bytes_analysis_sha256"], hashlib.sha256(Path(ba.__file__).read_bytes()).hexdigest())
            self.assertEqual({p["model"] for p in frozen["fit_points"]},
                             {m["model"] for m in manifest["models"] if m["role"] == "fit"})
            self.assertEqual(set(frozen["neg8_inputs"]), {s["session_id"] for s in manifest["sessions"]})
            analyze("heldout", "unreleased-heldout", predictions=predictions, expected=1)

            for path in sorted(private.glob("*.json")):
                shutil.copyfile(path, released / path.name)
            self.assertEqual({p.name for p in released.iterdir()}, {p.name for p in private.iterdir()})
            analyze("heldout", "stage2", predictions=predictions)
            self.assertEqual(predictions.read_bytes(), commitment)
            self.assertEqual(ba.read_json(root / "stage2/unavailable.json"), [])
            self.assertEqual({p["boundary"] for p in ba.read_json(root / "stage2/model_estimates.json")},
                             set(ba.BOUNDARIES))
            # 2 selections x 2 bases x 3 boundaries = 12 H2 groups.
            # Each H1 group has 10 models x (2 passes + their mean) = 30 rows,
            # so the registered complete design prints 12 x 30 = 360 H1 rows.
            self.assertEqual(len(ba.read_json(root / "stage2/h1.json")), 360)
            self.assertEqual(len(ba.read_json(root / "stage2/h2.json")), 12)

    def test_full_size_real_reducer_harvest_and_export_ingress(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = archive_campaign(root)
            ba.validate_manifest(manifest)
            fit = ba.load_records(root / "export", manifest, stage="fit")
            heldout = ba.load_records(root / "export", manifest, stage="heldout")
            self.assertEqual(len(fit), 300)
            self.assertEqual(len(heldout), 700)
            self.assertEqual(len({(r["model"], r["pass_id"]) for r in fit + heldout}), 20)
            for row in fit + heldout:
                # The independent native 10 Hz integration can move each
                # edge by r_max + 0.1 s; phase_edge_j is the resulting
                # (P_start+P_end)*dt envelope. The meter stores integer uW,
                # adding at most half a uW times the integrated duration.
                integration_bar = row["meter"]["phase_edge_j"] + .5e-6 * row["duration_s"]
                self.assertAlmostEqual(row["meter"]["gross_j"], 2 * row["rails_j"], delta=integration_bar)
            _write_json(root/"manifest.json",manifest)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(bytes_analyze.main(["--export",str(root/"export"),"--manifest",str(root/"manifest.json"),
                    "--stage","fit","--out",str(root/"fit")]),0)
                prediction_bytes = (root/"fit/predictions.json").read_bytes()
                self.assertEqual(bytes_analyze.main(["--export",str(root/"export"),"--manifest",str(root/"manifest.json"),
                    "--stage","heldout","--predictions",str(root/"fit/predictions.json"),"--out",str(root/"heldout")]),0)
            self.assertEqual((root/"fit/predictions.json").read_bytes(),prediction_bytes)
            self.assertEqual(len(ba.read_json(root/"heldout/h1.json")),360)
            self.assertEqual(len(ba.read_json(root/"heldout/h2.json")),12)
            self.assertEqual(ba.read_json(root/"heldout/unavailable.json"),[])
            with patch.object(ba, "_session_streams", return_value=[]):
                no_meter = ba.load_records(root / "export", manifest, stage="fit")
            self.assertTrue(all(r["meter"] is None for r in no_meter))
            self.assertTrue(all("bytes.meter_decode_unavailable" in r["flags"] for r in no_meter))
            missing_points = ba.combine_passes(ba.reduce_models(no_meter,manifest) +
                                               ba.reduce_models(no_meter,manifest,inclusive=True))
            frozen_missing = ba.frozen_predictions(missing_points,manifest)
            self.assertTrue(all(g["lines"] is None for g in frozen_missing["rival_lines"] if g["boundary"]!="rails"))
            no_meter_all = no_meter + [dict(r, meter=None) for r in heldout]
            missing_passes = ba.reduce_models(no_meter_all, manifest) + ba.reduce_models(no_meter_all, manifest, inclusive=True)
            missing_all = ba.combine_passes(missing_passes)
            evaluated = ba.evaluate(missing_all, frozen_missing)
            self.assertEqual(len(evaluated["unavailable"]), 8)
            words = [r for r in evaluated["h1"] if "word" in r]
            self.assertTrue(words)
            self.assertTrue(all(r["boundary"] == "rails" for r in words))
            # Q1 item 4: no-point cells retain a missing row, never an H1 word.
            missing = [r for r in evaluated["h1"] if r["boundary"] != "rails"]
            self.assertEqual(len(missing), 8 * 10)  # eight DC/rest groups, ten models
            self.assertTrue(all(r["status"] == "missing" and "word" not in r for r in missing))
            # Read actual harvest exclusions (thermal and a second physical cause)
            # plus an acceptance-emitted flag, rather than only handmade records.
            session = manifest["sessions"][0]
            acceptance_path = Path(session["archive"])/"derived/b6-acceptance.json"
            acceptance = ba.read_json(acceptance_path)
            saved = copy.deepcopy(acceptance)
            selected = [r for r in fit if r["session_id"]==session["session_id"]][:50]
            acceptance["excluding"] = [{"scope":"member","run_id":selected[i]["run_id"],"code":code}
                for i,code in ((0,"thermal.os_level_nonzero"),(10,"contention.request_overlap"))]
            acceptance["emitted_flags"] = [{"scope":{"run_id":selected[0]["run_id"]},"code":"thermal.os_level_nonzero"}]
            _write_json(acceptance_path,acceptance)
            excluded_fit = ba.load_records(root/"export",manifest,stage="fit")
            primary = ba.reduce_models(excluded_fit,manifest)
            inclusive = ba.reduce_models(excluded_fit,manifest,inclusive=True)
            target = [r for r in primary if r["session_id"]==session["session_id"] and r["model"]==selected[0]["model"]]
            self.assertTrue(all((r["n_r"],r["n_b"])==(9,9) for r in target))
            self.assertTrue(all((r["n_r"],r["n_b"])==(10,10) for r in inclusive))
            self.assertIn("thermal.os_level_nonzero", next(r for r in excluded_fit if r["run_id"]==selected[0]["run_id"])["flags"])
            _write_json(acceptance_path,saved)
            # Poison every held-out configuration and reduction: fit still reads only its own configurations.
            for session in manifest["sessions"]:
                archive = Path(session["archive"])
                for model in manifest["models"]:
                    if model["role"] == "heldout":
                        for ordinal in range(50):
                            rid = (model["model"] + "-" + str(ordinal)).lower().replace(".", "-")
                            (archive / "sources/claim-runs" / rid / "config.json").write_text("HELDOUT MUST NOT BE READ")
                            (archive / "withheld/reductions" / (rid + ".summary_metrics.rereduced.json")).write_text("HELDOUT MUST NOT BE READ")
            self.assertEqual(ba.load_records(root / "export", manifest, stage="fit"), fit)
            reduced = ba.reduce_models(fit, manifest)
            self.assertEqual(len(reduced), 36)
            self.assertTrue(all(r["status"] == "computed" for r in reduced))
            self.assertTrue(all(r["operative"][0]["status"] == "synthetic_timing_fixture" for r in reduced))
            self.assertIn("member instrument-calibration primary evidence", reduced[0]["operative"][0]["missing"])

    def test_physics_inclusive_meter_missing_and_boundary_composition(self):
        spec = ba.read_json(FIXTURES / "campaign_design.json")["models"][0]
        rows = []
        for i in range(50):
            rows.append({"run_id":str(i), "model":spec["model"], "pass_id":1, "session_id":"s",
                "stratum":"repeat" if i<10 else "quad", "unit_id":str(i if i<10 else (i-10)//4),
                "duration_s":2, "rails_j":10, "rails_secondary_j":-2, "rails_anchor_j":.3,
                "meter":{"gross_j":16,"secondary_j":-4,"phase_edge_j":.7},
                "excluded":i in (0,10), "status":"succeeded", "flags":["thermal" if i==0 else "contention"] if i in (0,10) else [],
                "operative":{"operative_bound_s":.05,"status":"rereduced"}})
        manifest = {"models":[spec], "sessions":[{"session_id":"s", "drift_allowance_j":dict.fromkeys(ba.BOUNDARIES,.2),
            "drift_reference":{"test7_passed":True}}]}
        for row in rows:
            row["neg8_inputs"] = {"test7_passed": True, "references": [], "boundaries": {
                b: {"families": {f: {"allowance_j": .2} for f in ("gross", "idle_subtracted")}}
                for b in ba.BOUNDARIES}}
        primary = ba.reduce_models(rows, manifest)
        inclusive = ba.reduce_models(rows, manifest, inclusive=True)
        self.assertTrue(all((r["n_r"],r["n_b"])==(9,9) for r in primary))
        self.assertTrue(all((r["n_r"],r["n_b"])==(10,10) for r in inclusive))
        for row in primary:
            self.assertAlmostEqual(row["B_j"], {"rails":.4,"DC input":.8,"rest":1.1}[row["boundary"]])
            self.assertAlmostEqual(row["upper_j"]-row["mean_j"], row["B_j"])
            if row["boundary"] != "rails":
                self.assertEqual(row["meter_attribution_floor_j"], .7)
            if row["basis"] == "idle-subtracted secondary":
                self.assertLess(row["mean_j"],0)
        for row in rows:
            row["excluded"] = int(row["unit_id"]) >= 5
        minimum = ba.reduce_models(rows,manifest)
        self.assertTrue(all((r["n_r"],r["n_b"])==(5,5) for r in minimum))
        for row in rows:
            row["excluded"] = int(row["run_id"]) in (0,10)
        rows[10]["meter"] = None
        limited = ba.reduce_models(rows, manifest, inclusive=True)
        self.assertEqual(next(r for r in limited if r["boundary"]=="DC input")["n_b"],9)
        for row in rows:
            row["meter"] = None
        missing = ba.reduce_models(rows, manifest)
        self.assertEqual(sum(r["status"]=="computed" for r in missing),2)
        self.assertEqual(sum(r["status"]=="unavailable" for r in missing),4)
        points = ba.combine_passes(missing)
        self.assertEqual(sum(p["status"]=="computed" for p in points),2)


class CampaignWordRates(NumericTestCase):
    def test_twenty_production_shaped_campaigns_per_world(self):
        from collections import Counter
        design = ba.read_json(FIXTURES / "campaign_design.json")
        report = []
        for world, seeds in design["seeds"].items():
            words, coverage = Counter(), Counter()
            method_coverage, estimates = Counter(), {}
            d3 = []
            duration_scale = statistics.fmean(design["main_campaign"]["pass_duration_scales"])
            held_models = [m["model"] for m in design["models"] if m["role"]=="heldout"]
            # Population OLS slope for the fixed ten-model design; resident
            # world also reports the structural epsilon of the extended fit.
            xs = [(m["W_bytes"]+m["KV_bytes"])/1e9*512/(m["synthetic_duration_s"] * duration_scale) for m in design["models"]]
            ys = [.01*x if world=="bytes" else 3 if world=="time" else
                  .01*m["R_bytes"]/1e9*512/(m["synthetic_duration_s"] * duration_scale) for x,m in zip(xs,design["models"])]
            mx,my = statistics.fmean(xs),statistics.fmean(ys)
            epsilon = math.fsum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.fsum((x-mx)**2 for x in xs)
            for seed in seeds:
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    manifest = archive_campaign(root, world=world, seed=seed,
                        pass_duration_scales=design["main_campaign"]["pass_duration_scales"],
                        clock_latency_ms=design["main_campaign"]["clock_latency_ms"], release="none")
                    cli_stage_chain(root, manifest)
                    records = ba.load_records(root / "export", manifest, stage="all")
                    d3.append(assert_d3_exercised(self, records, manifest))
                    self.assertEqual(ba.read_json(root/"out/unavailable.json"),[])
                    for row in ba.read_json(root/"out/h1.json"):
                        if row["selection"]=="primary" and row["basis"]=="gross primary" and row["role"]=="heldout" and row["pass_id"]=="mean":
                            words[row["boundary"],row["model"],row["word"]] += 1
                    for row in ba.read_json(root/"out/h2.json"):
                        if row["selection"]=="primary" and row["basis"]=="gross primary":
                            factor = 2 if row["boundary"]=="DC input" else 1
                            for fit,truth in (("two_term",epsilon*factor),
                                              ("resident_extended",(.01 if world=="bytes" else 0)*factor)):
                                fitted = row[fit]
                                lo,hi = fitted["intervals"][1]
                                coverage[row["boundary"],fit] += lo<=truth<=hi
                                # The plain interval uses the specified 95%
                                # t at n-p df; the ruled interval uses the
                                # fit's existing Bonferroni k. Report both
                                # HC3 and OLS without selecting a new method.
                                critical_95 = ba.student_t_quantile(.975, fitted["df"])
                                for method, se_key, interval_key in (("HC3", "standard_errors", "intervals"),
                                        ("OLS", "ols_standard_errors", "ols_intervals")):
                                    coefficient, se = fitted["coefficients"][1], fitted[se_key][1]
                                    key = (row["boundary"], fit, method)
                                    method_coverage[*key, "plain_95"] += abs(coefficient - truth) <= critical_95 * se
                                    lo, hi = fitted[interval_key][1]
                                    method_coverage[*key, "ruled_k"] += lo <= truth <= hi
                                    if row["boundary"] != "rails":
                                        c = fitted["coefficient_C"][1]
                                        method_coverage[*key, "offset_plain_95"] += abs(coefficient - truth) <= critical_95 * se + c
                                        alternative = "offset_intervals" if method == "HC3" else "offset_ols_intervals"
                                        lo, hi = fitted[alternative][1]
                                        method_coverage[*key, "offset_ruled_k"] += lo <= truth <= hi
                                    estimates.setdefault(key, []).append((coefficient, se, truth))
                print(f"BYTES synthetic {world} seed {seed} complete",flush=True)
            n = len(seeds)
            # R8/Addendum 4 prescribe twenty independent campaigns per world.
            self.assertGreaterEqual(n,20)
            rate = lambda count: {"rate":count/n,"MCSE":math.sqrt((count/n)*(1-count/n)/n)}
            word_rows = []
            for boundary in ba.BOUNDARIES:
                for model in held_models:
                    counts = {w:words[boundary,model,w] for w in (*ba.HYPOTHESES,"unresolved","neither")}
                    self.assertEqual(sum(counts.values()),n)
                    word_rows.append({"boundary":boundary,"model":model,"words":{w:rate(c) for w,c in counts.items()}})
            report.append({"world":world,"campaigns":n,"seeds":seeds,"two_term_population_epsilon":epsilon,
                "D3": {"rest_cells": sum(r["rest_cells"] for r in d3),
                    "min_gap_over_B": min(r["min_gap_over_B"] for r in d3),
                    "min_agreement_bars": min(r["min_agreement_bars"] for r in d3)},
                "H2_method_coverage": [{"boundary": b, "fit": f, "method": m,
                    "plain_95": rate(method_coverage[b, f, m, "plain_95"]),
                    "ruled_k": rate(method_coverage[b, f, m, "ruled_k"]), "k": ba.H2_INTERVALS[b],
                    "offset_plain_95": rate(method_coverage[b, f, m, "offset_plain_95"]) if b != "rails" else None,
                    "offset_ruled_k": rate(method_coverage[b, f, m, "offset_ruled_k"]) if b != "rails" else None,
                    "mean_estimate": statistics.fmean(v[0] for v in estimates[b, f, m]),
                    "mean_se": statistics.fmean(v[1] for v in estimates[b, f, m]),
                    "truth": estimates[b, f, m][0][2]}
                    for b in ba.BOUNDARIES for f in ("two_term", "resident_extended") for m in ("HC3", "OLS")],
                "structural_extended_epsilon":.01 if world=="bytes" else 0,
                "word_rates":word_rows,"H2_coverage":[{"boundary":b,"fit":f,**rate(coverage[b,f])}
                    for b in ba.BOUNDARIES for f in ("two_term","resident_extended")]})
        print("BYTES_SIMULATION_REPORT="+json.dumps(report,sort_keys=True),flush=True)


class Addendum4RegressionTests(NumericTestCase):
    """Each numbered test reproduces an accepted review finding on 82c014c55."""

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.manifest = archive_campaign(cls.root)
        _write_json(cls.root / "manifest.json", cls.manifest)
        cls.records = ba.load_records(cls.root / "export", cls.manifest, stage="all")
        cls.passes = ba.reduce_models(cls.records, cls.manifest) + ba.reduce_models(
            cls.records, cls.manifest, inclusive=True)
        cls.points = ba.combine_passes(cls.passes)
        cls.frozen = ba.frozen_predictions([p for p in cls.points if p["role"] == "fit"], cls.manifest)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def target(self, model="Qwen3-4B-4bit", ordinal=3, pass_id=1):
        spec = next(m for m in self.manifest["models"] if m["model"] == model)
        session = next(s for s in self.manifest["sessions"] if s["pass_id"] == pass_id)
        root = Path(session["archive"])
        roster = ba.read_json(root / "derived/roster.json")
        ids = [m["run_id"] for m in roster["members"]
               if any(u["cell_id"] in spec["cell_ids"] for u in m.get("units", []))]
        return root, session, ids[ordinal]

    @contextlib.contextmanager
    def changed_json(self, path, change):
        raw = path.read_bytes()
        value = json.loads(raw)
        change(value)
        _write_json(path, value)
        try:
            yield
        finally:
            path.write_bytes(raw)

    def test_a4_01_unusable_member_all_stages_and_nonsynthetic(self):
        # Exercise the real archive reader, with the native re-reducer faked;
        # the synthetic escape hatch is disabled in every case.
        from joulewise.b6.archive import bundle_of
        manifest = dict(self.manifest, synthetic=False)
        for stage, model in (("fit", "Qwen3-4B-4bit"), ("heldout", "Qwen3-32B-4bit"),
                             ("all", "Qwen3-4B-4bit")):
            root, session, rid = self.target(model)
            for defect in ("missing_bundle", "missing_export", "tokens", "failed_null", "failed_present", "nonfinite",
                           "missing_energy", "no_envelope", "interpolation", "validity"):
                with self.subTest(stage=stage, defect=defect), contextlib.ExitStack() as stack:
                    def summary(bundle, **kwargs):
                        value = ba.read_json(root / "withheld/reductions" / (bundle.name + ".summary_metrics.rereduced.json"))
                        if bundle.name == rid:
                            if defect.startswith("failed"):
                                value["status"] = "failed"
                            if defect == "failed_null":
                                value["phase_energy_j"]["decode"] = None
                            if defect == "nonfinite":
                                value["phase_energy_j"]["decode"] = float("nan")
                            if defect == "missing_energy":
                                value["phase_energy_j"].pop("decode")
                            if defect == "no_envelope":
                                value["energy_anchor_shift_envelopes"] = {}
                            if defect == "interpolation":
                                value["energy_bound_terms_j"]["E_interpolation_joint_edge_bound_j"] = 1
                        return value
                    stack.enter_context(patch("joulewise.reduce._rederive_summary_for_authenticated_fiducial_bound", side_effect=summary))
                    if defect == "missing_bundle":
                        stack.enter_context(patch("joulewise.b6.archive.bundle_of",
                            side_effect=lambda r, p, run_id: None if run_id == rid else bundle_of(r, p, run_id)))
                    elif defect == "missing_export":
                        import csv
                        path = root.parent/"export/bytes"/(session["session_id"]+".runs.csv")
                        original = path.read_bytes()
                        stack.callback(path.write_bytes,original)
                        reader = csv.DictReader(io.StringIO(original.decode()))
                        exported = [r for r in reader if r["run_id"] != rid]
                        with path.open("w",newline="") as handle:
                            writer = csv.DictWriter(handle,fieldnames=reader.fieldnames)
                            writer.writeheader(); writer.writerows(exported)
                    elif defect == "tokens":
                        stack.enter_context(self.changed_json(root / "sources/claim-runs" / rid / "metadata.json",
                            lambda x: x["workload_observed"].update(output_token_count=511)))
                    elif defect == "validity":
                        stack.enter_context(self.changed_json(root / "derived/b6-acceptance.json",
                            lambda x: x["excluding"].append({"scope":"member", "run_id":rid,
                                                           "code":"member.strict_validation_failed"})))
                    rows = list(ba.archive_records(root, manifest, session, stage=stage))
                    bad = next(r for r in rows if r["run_id"] == rid)
                    self.assertNotEqual(bad["status"], "succeeded")
                    self.assertIsNone(bad["meter"])
                    for inclusive in (False, True):
                        reduced = ba.reduce_models(rows, manifest, inclusive=inclusive)
                        cells = [r for r in reduced if r["model"] == model]
                        self.assertTrue(all((r["n_r"], r["n_b"]) == (9,10) for r in cells))
                        self.assertTrue(all(rid in r["removed_runs"] for r in cells))

    def test_a4_01_below_minimum_refuses_only_affected_cell(self):
        rows = copy.deepcopy(self.records)
        for row in rows:
            if row["model"] == "Qwen3-32B-4bit" and row["pass_id"] == 1 and row["stratum"] == "repeat" and int(row["unit_id"]) < 6:
                row.update(status="unusable", meter=None)
        passes = ba.reduce_models(rows, self.manifest)
        bad = [r for r in passes if r["model"] == "Qwen3-32B-4bit" and r["pass_id"] == 1]
        self.assertTrue(all(r["status"] == "unavailable" for r in bad))
        points = ba.combine_passes(passes)
        frozen = ba.frozen_predictions([p for p in points if p["role"] == "fit"], self.manifest)
        evaluated = ba.evaluate(points, frozen)
        means = [r for r in evaluated["h1"] if r["pass_id"] == "mean"]
        self.assertEqual(len(means), 60)
        self.assertTrue(all(r["pass_status"] == "one_pass" for r in means if r["model"] == "Qwen3-32B-4bit"))
        self.assertEqual(len(evaluated["h2"]), 12)  # primary plus two-pass sensitivities

    def test_a4_02_p02_primary_family_and_two_regressor_tier(self):
        for boundary in ba.BOUNDARIES:
            pts = [p for p in self.points if (p["boundary"],p["basis"],p["selection"]) ==
                   (boundary,"gross primary","primary")]
            rails = {p["model"]:p["power"] for p in self.points if (p["boundary"],p["basis"],p["selection"]) ==
                     ("rails","gross primary","primary")}
            out = ba.h2(pts, rails)
            k = 11 if boundary == "rest" else 9
            self.assertEqual(len(out["primary_intervals"]), k)
            self.assertIn("extended_epsilon", [r["term"] for r in out["primary_intervals"]])
            self.assertIn("tier_rho", [r["term"] for r in out["primary_intervals"]])
            for fit in (out["two_term"],out["resident_extended"],out["tier"]):
                self.assertEqual(fit["family_size"],k)
                self.assertEqual(fit["critical"],ba.student_t_quantile(1-.05/(2*k),fit["df"]))
            self.assertEqual(len(out["tier"]["coefficients"]),3)
            self.assertEqual(out["tier"]["df"],3)
            for d in out["tier_deviations"]:
                p = next(p for p in pts if p["model"] == d["model"])
                c = out["tier"]["coefficients"]
                self.assertAlmostEqual(d["predicted_w"],c[0]+c[1]*p["BW"]+c[2]*p["resident"]/p["time"])

    def test_a4_03_p06_deviation_adds_own_halfwidth(self):
        fit = ba.ols([[x] for x in range(5)], [4,3,9,7,12])
        bare = ba.deviation(fit,[2],8)
        full = ba.deviation(fit,[2],8,.125)
        self.assertAlmostEqual(full["lower_w"],bare["lower_w"]-.125)
        self.assertAlmostEqual(full["upper_w"],bare["upper_w"]+.125)
        p = next(p for p in self.points if (p["model"],p["boundary"],p["basis"],p["selection"]) ==
                 ("Qwen3-8B-8bit","DC input","gross primary","primary"))
        out = ba.h2([q for q in self.points if (q["boundary"],q["basis"],q["selection"]) ==
                    ("DC input","gross primary","primary")],{})
        d = next(r for r in out["tier_deviations"] if r["model"] == p["model"])
        self.assertEqual(d["measured_half_w"],(p["h_j"]+p["B_j"])/p["duration_s"])
        self.assertAlmostEqual((d["upper_w"]-d["lower_w"])/2,d["prediction_half_w"]+d["measured_half_w"])

    def test_a4_04_p05_mean_halfwidth_and_per_pass_words(self):
        for p in self.points:
            rows = [r for r in self.passes if all(r[k] == p[k] for k in ("model","boundary","basis","selection"))]
            half = statistics.fmean(r["h_j"]+r["B_j"] for r in rows)
            self.assertAlmostEqual(p["upper_j"]-p["mean_j"],half)
            self.assertAlmostEqual(p["mean_j"]-p["lower_j"],half)
        result = ba.evaluate(self.points,self.frozen)
        self.assertEqual(len(result["h1"]),360)
        self.assertEqual({r["pass_id"] for r in result["h1"]},{"mean",1,2})
        for row in result["h1"]:
            self.assertEqual(row["description_only"],row["pass_id"]!="mean")
            if row["pass_id"] == "mean":
                continue
            subset = [r for r in self.passes if r["pass_id"] == row["pass_id"] and
                      all(r[k] == row[k] for k in ("boundary","basis","selection"))]
            pts = ba.combine_passes(subset)
            lines = ba.freeze_lines([p for p in pts if p["role"] == "fit"])
            point = next(p for p in pts if p["model"] == row["model"])
            self.assertEqual(row["word"],ba.h1_point(lines,point)["word"])

    def test_a4_05_hc3_independent_sandwich_and_ols_label(self):
        # Closed-form simple-regression influence weights, independent of ba.ols.
        xs, residuals = list(range(5)), [1,-2,2,-2,1]
        leverages = [1/5 + (x-2)**2/10 for x in xs]
        slope_var = math.fsum(((x-2)/10)**2*(r/(1-h))**2 for x,r,h in zip(xs,residuals,leverages))
        fit = ba.ols([[x] for x in xs],[4,3,9,7,12],family_size=9)
        self.assertEqual(fit["se_method"],"HC3")
        self.assertAlmostEqual(fit["covariance"][1][1],slope_var)
        self.assertAlmostEqual(fit["standard_errors"][1],math.sqrt(slope_var))
        self.assertAlmostEqual(fit["ols_covariance"][1][1],7/15)
        self.assertAlmostEqual(fit["ols_standard_errors"][1],math.sqrt(7/15))
        self.assertAlmostEqual(fit["intervals"][1][0],2-fit["critical"]*math.sqrt(slope_var))

    def test_a4_05_p03_coverage(self):
        spec = importlib.util.spec_from_file_location("bytes_coverage",FIXTURES/"coverage.py")
        coverage = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(coverage)
        # p03 is the conditional member-redraw diagnostic, not a replacement
        # for native offset coverage. Its source fixture traverses every stage.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = archive_campaign(root, release="none")
            cli_stage_chain(root, manifest)
            report = coverage.run(root,400)
        self.assertEqual(len(report),36)
        self.assertEqual({r["method"] for r in report},{"HC3","OLS"})
        self.assertTrue(all(r["draws"] == 400 for r in report))
        print("BYTES_P03_COVERAGE="+json.dumps(report,sort_keys=True),flush=True)

    def test_a4_06_p08_number_exclusion_restored_validity_stays_out(self):
        root, session, rid = self.target("Qwen3-8B-4bit",20)
        _, _, bad = self.target("Qwen3-8B-4bit",24)
        def exclude(x):
            x["excluding"] += [{"scope":"member","run_id":run,"code":code} for run,code in
                ((rid,"member.cooldown_cap_hit"),(bad,"member.strict_validation_failed"))]
        with self.changed_json(root/"derived/b6-acceptance.json",exclude):
            records = list(ba.archive_records(root,self.manifest,session,stage="fit"))
        for inclusive,expected in ((False,(10,8)),(True,(10,9))):
            cells = [r for r in ba.reduce_models(records,self.manifest,inclusive=inclusive)
                     if r["model"] == "Qwen3-8B-4bit"]
            self.assertTrue(all((r["n_r"],r["n_b"])==expected for r in cells))
            if inclusive:
                self.assertTrue(all("member.cooldown_cap_hit" in r["flags"] for r in cells))
                self.assertTrue(all(rid in r["kept_runs"] and bad in r["removed_runs"] for r in cells))

    def test_a4_07_neg8_export_inputs_whole_request_and_two_families(self):
        p = next(r for r in self.passes if (r["model"],r["pass_id"],r["boundary"],r["basis"],r["selection"]) ==
                 ("Qwen3-4B-4bit",1,"rails","gross primary","primary"))
        ref = p["neg8_inputs"]["boundaries"]["rails"]
        self.assertEqual(ref["duration_s"],3)
        self.assertAlmostEqual(ref["energy_j"],(3*10+10.004+3*10.01)/7)
        self.assertEqual(len(ref["reference_run_ids"]),7)
        self.assertEqual(len(ref["corpus_run_ids"]),6)
        self.assertAlmostEqual(ref["families"]["gross"]["allowance_j"],.01)
        self.assertAlmostEqual(ref["families"]["idle_subtracted"]["allowance_j"],.0075)
        scale = max(1,p["mean_j"]/ref["energy_j"],p["duration_s"]/3)
        self.assertEqual(p["drift_scale"],scale)
        self.assertAlmostEqual(p["kind_averages_j"][ba.BOUND_KINDS[2]],.005*scale)
        secondary = next(r for r in self.passes if all(r[k]==p[k] for k in
            ("model","pass_id","boundary","selection")) and r["basis"]=="idle-subtracted secondary")
        self.assertAlmostEqual(secondary["kind_averages_j"][ba.BOUND_KINDS[2]],.00375*scale)
        # The reference's whole-request energy must come from the export even
        # when a conflicting withheld summary is present.
        root, session, _ = self.target()
        summary = root/"withheld/reductions/neg8-start-0.summary_metrics.rereduced.json"
        with self.changed_json(summary,lambda x:x.update(gross_energy_j=123456)):
            rows = list(ba.archive_records(root,self.manifest,session,stage="fit"))
        self.assertEqual(rows[0]["neg8_inputs"]["boundaries"]["rails"],ref)

    def test_a4_08_blinded_release_and_commitment_end_to_end(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = archive_campaign(root,non_claim=False,release="none")
            _write_json(root/"manifest.json",manifest)
            args = ["--export",str(root/"export"),"--manifest",str(root/"manifest.json")]
            with contextlib.redirect_stdout(io.StringIO()), patch.object(ba,"archive_records",side_effect=AssertionError("blinded opened archive")), \
                    patch.object(ba,"_session_streams",side_effect=AssertionError("blinded opened meter")):
                self.assertEqual(bytes_analyze.main(args+["--stage","blinded","--out",str(root/"blind")]),0)
            blind = ba.read_json(root/"blind/model_estimates.json")
            self.assertTrue(blind)
            self.assertTrue(all(p["boundary"]=="rails" and p["status"]=="computed" for p in blind))
            with contextlib.redirect_stderr(io.StringIO()), patch.object(ba,"_session_streams",side_effect=AssertionError("unreleased meter")):
                self.assertEqual(bytes_analyze.main(args+["--stage","fit","--out",str(root/"unreleased")]),1)
            release_keys(root,manifest,"fit")
            # Native full parsing is forbidden at fit. Instrument the actual
            # sample unpacker, so no held-out power may even be decoded.
            original_streams = ba._session_streams
            def filtered(root,spans):
                full = kp.parse(root/"sources/night-custody/hazards/meter/stream-001.jsonl")
                offset = kp.raw_offset_ns(full)
                margin = full.samples.step_ms*1_000_000
                allowed = lambda t:any(a+offset-margin<=t<=b+offset+margin for a,b in spans)
                allowed_currents = {round(w*1e6) for t,w in zip(full.host_ns,full.watts) if allowed(t)}
                forbidden = {round(w*1e6) for t,w in zip(full.host_ns,full.watts) if not allowed(t)} - allowed_currents
                self.assertTrue(forbidden)
                native_sample = kp.SAMPLE
                case = self
                class GuardSample:
                    size = native_sample.size
                    def unpack(self,raw):
                        values = native_sample.unpack(raw)
                        case.assertNotIn(values[3],forbidden,"held-out power sample decoded at fit")
                        return values
                    def iter_unpack(self,raw):
                        for pos in range(0,len(raw),self.size):
                            yield self.unpack(raw[pos:pos+self.size])
                with patch.object(kp,"SAMPLE",GuardSample()):
                    streams = original_streams(root,spans)
                for _,stream in streams:
                    self.assertTrue(all(allowed(t) for t in stream.host_ns))
                    self.assertLess(len(stream.host_ns),len(full.host_ns)/2)
                    self.assertEqual(stream.fit.stats,full.fit.stats)
                return streams
            with contextlib.redirect_stdout(io.StringIO()), patch.object(ba,"_session_streams",side_effect=filtered):
                self.assertEqual(bytes_analyze.main(args+["--stage","fit","--out",str(root/"fit")]),0)
            frozen = ba.read_json(root/"fit/predictions.json")
            self.assertEqual(frozen["bytes_analysis_sha256"],hashlib.sha256(Path(ba.__file__).read_bytes()).hexdigest())
            self.assertEqual(len(frozen["neg8_inputs"]),2)
            self.assertTrue(all(p["role"]=="fit" for p in frozen["fit_points"]))
            fit_names = {m["model"] for m in manifest["models"] if m["role"]=="fit"}
            self.assertEqual({r["model"] for r in frozen["tier_fit_inputs"]},fit_names)
            predict = ["--predictions",str(root/"fit/predictions.json")]
            with contextlib.redirect_stderr(io.StringIO()), patch.object(ba,"_session_streams",side_effect=AssertionError("heldout meter before release")):
                self.assertEqual(bytes_analyze.main(args+predict+["--stage","heldout","--out",str(root/"blocked")]),1)
            commitment = (root/"fit/predictions.json").read_bytes()
            release_keys(root,manifest,"all")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(bytes_analyze.main(args+predict+["--stage","heldout","--out",str(root/"held")]),0)
            self.assertEqual((root/"fit/predictions.json").read_bytes(),commitment)
            self.assertEqual(ba.read_json(root/"held/unavailable.json"),[])
            self.assertEqual(len(ba.read_json(root/"held/h1.json")),360)
            # Blinding factors cancel only after release; NEG-8 rails must match
            # the non-claim fixture despite random configuration offsets.
            for session_id,refs in frozen["neg8_inputs"].items():
                self.assertAlmostEqual(refs["boundaries"]["rails"]["energy_j"],(3*10+10.004+3*10.01)/7)

    def test_a4_09_p05_rest_vif(self):
        pts = [p for p in self.points if (p["boundary"],p["basis"],p["selection"]) ==
               ("rest","gross primary","primary")]
        rails = {p["model"]:p["power"] for p in self.points if (p["boundary"],p["basis"],p["selection"]) ==
                 ("rails","gross primary","primary")}
        fit = ba.h2(pts,rails)["rest"]
        corr = statistics.correlation([p["BW"] for p in pts],[rails[p["model"]] for p in pts])
        self.assertAlmostEqual(fit["vif"],1/(1-corr*corr))
        self.assertGreater(fit["vif"],1e6)

    def test_a4_10_p05_both_adjacent_edge_samples(self):
        stream = MeterWorkedExamples().stream([20]*40+[10]*20+[30]*41)
        result = ba.meter_decode(stream,[4_000_000_000,6_000_000_000],[1_000_000_000,3_000_000_000])
        self.assertEqual(result["edge_powers_w"],[20,30])
        self.assertAlmostEqual(result["phase_edge_j"],5)
        stream = MeterWorkedExamples().stream([.2]*40+[10]*20+[.2]*41)
        result = ba.meter_decode(stream,[4_000_000_000,6_000_000_000],[1_000_000_000,3_000_000_000])
        self.assertEqual(result["edge_powers_w"],[10,10])
        self.assertAlmostEqual(result["phase_edge_j"],2)

    def test_malformed_meter_is_unavailable_without_losing_rails(self):
        root,session,_ = self.target()
        path = root/"sources/night-custody/hazards/meter/stream-001.jsonl"
        original = path.read_bytes()
        try:
            path.write_text("{broken transport\n")
            records = list(ba.archive_records(root,self.manifest,session,stage="fit"))
        finally:
            path.write_bytes(original)
        self.assertTrue(all(r["status"]=="succeeded" and r["meter"] is None for r in records))
        reduced = ba.reduce_models(records,self.manifest)
        self.assertTrue(all(r["status"]=="computed" for r in reduced if r["boundary"]=="rails"))
        self.assertTrue(all(r["status"]=="unavailable" for r in reduced if r["boundary"]!="rails"))

    def test_a4_12_exact_integer_constant_zero_equivalence(self):
        from joulewise import paper_reported_energy as registered
        from tests.test_paper_reported_energy import synthetic_input
        families = {"small_ints":lambda i:i, "above_2p53":lambda i:2**53+i,
                    "large_ints":lambda i:10**17+i, "constant":lambda i:7,
                    "zero":lambda i:0, "subnormal":lambda i:(i+1)*5e-324}
        comparisons = 0
        for model in registered.MODELS:
            for length in registered.PREFILL_LADDER_PROMPT_TOKENS:
                fixture = synthetic_input(model,length)
                for cell,data in zip(fixture["spec"]["reported_energy_cells"],fixture["cells"]):
                    for name,values in families.items():
                        with self.subTest(model=model,length=length,cell=cell["cell_id"],family=name):
                            rows = copy.deepcopy(data["rows"])
                            for i,row in enumerate(rows):
                                row.update(energy_j=values(i),bounds_j=dict.fromkeys(ba.BOUND_KINDS,i%3))
                            expected = registered._project_cell(cell,rows,data["binding"])
                            actual = ba.estimate_phase_energy([r["energy_j"] for r in rows[:10]],
                                [[r["energy_j"] for r in rows[i:i+4]] for i in range(10,50,4)],
                                [r["bounds_j"] for r in rows[:10]],
                                [[r["bounds_j"] for r in rows[i:i+4]] for i in range(10,50,4)])
                            for key in ("mean_j","lower_j","upper_j"):
                                self.assertEqual(actual[key],expected[key])
                            for key in ("s_r","s_b","variance","h_j","B_j","kind_averages_j"):
                                self.assertEqual(actual["interval"][key],expected["interval"][key])
                            comparisons += 1
        self.assertEqual(comparisons,144)


class Addendum7RegressionTests(NumericTestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.manifest = archive_campaign(cls.root)
        cls.records = ba.load_records(cls.root / "export", cls.manifest, stage="all")

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def assess(self, records):
        passes = ba.reduce_models(records, self.manifest) + ba.reduce_models(records, self.manifest, inclusive=True)
        points = ba.combine_passes(passes)
        frozen = ba.frozen_predictions([p for p in points if p["role"] == "fit"], self.manifest)
        return passes, points, frozen, ba.evaluate(points, frozen)

    def refuse(self, records, models, pass_ids=(1, 2)):
        for row in records:
            if row["model"] in models and row["pass_id"] in pass_ids and row["stratum"] == "repeat" and int(row["unit_id"]) < 6:
                row.update(status="unusable", invalid_energy_record=True, meter=None)

    def test_nr1_bad_per_run_inputs_flag_without_changing_registered_fit(self):
        _, clean_points, _, clean_result = self.assess(self.records)
        # Compare every pre-NR1 field exactly on identical registered inputs.
        # Only disclosure/alternative keys can change under these injections.
        disclosure = {"meter_offset_bound_j", "meter_offset_bound_w", "meter_offset_sensitivity_w",
            "systematics_flag", "sensitivity_flag", "coefficient_C", "offset_intervals",
            "offset_ols_intervals", "coefficient_decisions", "offset_decisions",
            "coefficient_decision", "offset_decision", "resident_adds_nothing_offset",
            "d_beta_d_delta_per_ms", "sensitivity_units"}
        def registered(value):
            if isinstance(value, dict):
                return {k: registered(v) for k, v in value.items() if k not in disclosure}
            if isinstance(value, list):
                return [registered(v) for v in value]
            return value
        expected = registered(clean_result)
        for field, bad in (("bound_j", None), ("bound_j", -1.0), ("bound_j", math.nan),
                           ("bound_j", math.inf), ("sensitivity_w", None),
                           ("sensitivity_w", math.nan), ("sensitivity_w", math.inf)):
            with self.subTest(field=field, bad=bad):
                records = copy.deepcopy(self.records)
                # One bad run among fifty must flag before its contribution can
                # be diluted in a pass mean (the negative injection's failure).
                target = records[0]
                target["meter"]["offset_" + field] = bad
                passes, points, _, result = self.assess(records)
                self.assertEqual(registered(result), expected)
                flag = "systematics_flag" if field == "bound_j" else "sensitivity_flag"
                for row in passes + points:
                    if row["model"] == target["model"] and row["boundary"] != "rails" and (
                            "pass_id" not in row or row["pass_id"] == target["pass_id"]):
                        self.assertIsNone(row["meter_offset_" + field])
                        self.assertIn(target["run_id"], row[flag])
                for row in result["h2"]:
                    if row["boundary"] != "rails":
                        fit = row["resident_extended"]
                        self.assertEqual(fit["status"], "computed")
                        self.assertIn(target["run_id"], fit[flag])
                        primary = next(p for p in row["primary_intervals"]
                                       if p["term"] == "extended_epsilon")
                        self.assertEqual(primary[flag], fit[flag])
                        self.assertNotIn("coefficient_C" if field == "bound_j" else
                                         "d_beta_d_delta_per_ms", fit)
                        self.assertIn("d_beta_d_delta_per_ms" if field == "bound_j" else
                                      "coefficient_C", fit)
        rows = [p for p in clean_points if p["boundary"] == "DC input" and
                p["selection"] == "primary" and p["basis"] == "gross primary"]
        clean = ba.h2(rows, {})
        for bad in (None, math.nan, math.inf):
            with self.subTest(point_sensitivity=bad):
                changed = copy.deepcopy(rows)
                changed[0]["meter_offset_sensitivity_w"] = bad
                result = ba.h2(changed, {})
                self.assertEqual(registered(result), registered(clean))
                self.assertIn("sensitivity_flag", result["resident_extended"])
                self.assertNotIn("d_beta_d_delta_per_ms", result["resident_extended"])

    def test_a7_09_one_pass_primary_all_tables_and_two_pass_sensitivity(self):
        target = "Qwen3-30B-A3B-4bit"
        records = copy.deepcopy(self.records)
        self.refuse(records, [target], (1,))
        passes, points, frozen, result = self.assess(records)
        for point in [p for p in points if p["model"] == target]:
            self.assertEqual((point["status"], point["pass_status"], point["n_passes"]), ("computed", "one_pass", 1))
            survivor = next(r for r in point["passes"] if r["pass_id"] == 2)
            self.assertEqual(point["mean_j"], survivor["mean_j"])
            self.assertEqual(point["h_j"] + point["B_j"], survivor["h_j"] + survivor["B_j"])
            self.assertIsNone(point["pass_difference_j"])
            self.assertEqual([r["pass_status"] for r in point["passes"]], ["one_pass", "one_pass"])
        words = [r for r in result["h1"] if r["model"] == target and not r["description_only"]]
        self.assertEqual(len(words), 12)
        self.assertTrue(all(r["pass_status"] == "one_pass" for r in words))
        for row in result["h2"]:
            primary = row["analysis"] == "primary"
            self.assertEqual(row["n"], 10 if primary else 9)
            self.assertEqual(row["k"], 11 if row["boundary"] == "rest" else 9)
            self.assertEqual(row["description_only"], not primary)
            labels = {p["model"]: p for p in row["point_labels"]}
            if primary:
                self.assertEqual(labels[target]["pass_status"], "one_pass")
                self.assertEqual(next(p for p in row["tier"]["point_labels"] if p["model"] == target)["pass_status"], "one_pass")
                self.assertEqual(next(p for p in row["loo_description"] if p["model"] == target)["pass_status"], "one_pass")
            else:
                self.assertNotIn(target, labels)
                self.assertNotIn("primary_intervals", row)
        for row in result["moe"]:
            self.assertEqual(next(p for p in row["misses"] if p["model"] == target)["pass_status"], "one_pass")
        # Fit-stage commitments and emitted pass tables carry the same label.
        fit_target = "Qwen3-4B-4bit"
        self.refuse(records, [fit_target], (1,))
        def released(source, manifest, *, stage, **kw):
            return [r for r in records if (r["role"] == "fit") == (stage == "fit")]
        # Native records do not carry role; look it up from the frozen roster.
        roles = {m["model"]: m["role"] for m in self.manifest["models"]}
        for r in records:
            r["role"] = roles[r["model"]]
        with tempfile.TemporaryDirectory() as directory, patch.object(ba, "load_records", side_effect=released), contextlib.redirect_stdout(io.StringIO()):
            root = Path(directory)
            _write_json(root / "manifest.json", self.manifest)
            self.assertEqual(bytes_analyze.main(["--export", str(self.root / "export"), "--manifest", str(root / "manifest.json"),
                "--stage", "all", "--out", str(root / "out")]), 0)
            for row in ba.read_json(root / "out/fit_pass_estimates.json"):
                if row["model"] == fit_target:
                    self.assertEqual(row["pass_status"], "one_pass")
            commit = ba.read_json(root / "out/predictions.json")
            self.assertTrue(all(p["pass_status"] == "one_pass" for p in commit["tier_fit_inputs"] if p["model"] == fit_target))
            self.assertEqual(len(ba.read_json(root / "out/analysis_record.json")["H2_intervals"]), 12)

    def test_a7_09_both_refused_no_point_no_word_h2_n_and_k(self):
        target = "Qwen3-8B-8bit"  # one fewer primary non-tier deviation
        records = copy.deepcopy(self.records)
        self.refuse(records, [target])
        _, points, _, result = self.assess(records)
        self.assertTrue(all(p["status"] == "unavailable" and p["pass_status"] == "no_pass"
                            for p in points if p["model"] == target))
        absent = [r for r in result["h1"] if r["model"] == target]
        self.assertEqual(len(absent), 12)
        self.assertTrue(all(r["status"] == "missing" and "word" not in r for r in absent))
        self.assertEqual(len(result["unavailable"]), 12)
        self.assertTrue(all(r["refusals"][0]["model"] == target for r in result["unavailable"]))
        for row in result["h2"]:
            self.assertEqual(row["n"], 9)
            self.assertEqual(row["k"], 10 if row["boundary"] == "rest" else 8)
            if not row["description_only"]:
                self.assertEqual(len(row["primary_intervals"]), row["k"])
                for fit in (row["two_term"], row["resident_extended"], row["tier"]):
                    self.assertEqual(fit["family_size"], row["k"])

    def test_q1_missing_moe_has_explicit_h1_and_active_or_resident_rows(self):
        target = "Qwen3-30B-A3B-4bit"
        records = copy.deepcopy(self.records)
        self.refuse(records, [target])
        for row in records:
            if row["model"] == target:
                row["flags"] = sorted(set(row["flags"]) | {"bytes.withheld_missing"})
                row.update(withheld_row_count=50, withheld_config_row_count=50)
        _, points, frozen, _ = self.assess(records)
        bytes_analyze._missing_labels(points)
        result = ba.evaluate(points, frozen)
        absent = [r for r in result["h1"] if r["model"] == target]
        self.assertEqual(len(absent), 12)
        for row in absent:
            self.assertEqual(row["status"], "missing")
            self.assertNotIn("word", row)
            self.assertIn("bytes.withheld_missing", row["flags"])
        self.assertEqual(len(result["moe"]), 12)
        for row in result["moe"]:
            self.assertEqual((row["status"], row["answer"]), ("missing", "missing"))
            self.assertEqual([m["model"] for m in row["missing_models"]], [target])
            self.assertIn("bytes.withheld_missing", row["flags"])
        self.assertTrue(all(r["n"] == 9 for r in result["h2"]))

    def test_a7_09_each_fit_refused_below_two_df_h2_survives_missing_fit_model(self):
        # Missing fit models prevent H1, while H2 still fits the remaining points.
        records = copy.deepcopy(self.records)
        self.refuse(records, ["Qwen3-4B-4bit", "Qwen3-14B-4bit"])
        _, _, _, result = self.assess(records)
        self.assertEqual(len(result["h1"]), 24)
        self.assertTrue(all(r["status"] == "missing" and "word" not in r for r in result["h1"]))
        self.assertTrue(all(r["status"] == "missing" and r["answer"] == "missing" for r in result["moe"]))
        self.assertEqual(len(result["h2"]), 24)
        for row in result["h2"]:
            self.assertEqual(row["n"], 8)
            self.assertEqual((row["tier"]["status"], row["tier"]["n"], row["tier"]["df"]), ("refused", 4, 1))
            self.assertTrue(all(d["status"] == "refused" for d in row["tier_deviations"]))
            self.assertEqual(row["k"], 5 if row["boundary"] == "rest" else 3)
            self.assertEqual(row["two_term"]["status"], "computed")
        # Four points admit only the intercept+BW fit (df=2).
        points = ba.combine_passes(ba.reduce_models(self.records, self.manifest))
        points = [p for p in points if p["boundary"] == "rails" and p["basis"] == "gross primary"][:4]
        out = ba.h2(points, {}, boundary="rails")
        self.assertEqual((out["n"], out["k"]), (4, 1))
        self.assertEqual(out["two_term"]["df"], 2)
        self.assertEqual(out["resident_extended"]["status"], "refused")
        self.assertTrue(all(r["status"] == "refused" for r in out["loo_description"]))
        empty = ba.h2([], {}, boundary="rest")
        self.assertEqual((empty["n"], empty["k"], empty["primary_intervals"]), (0, 0, []))
        self.assertEqual(empty["rest"]["status"], "refused")

    def battery_records(self, assist_ordinals):
        records = copy.deepcopy(self.records)
        module = [r for r in records if r["model"] == "Qwen3-30B-A3B-4bit" and r["pass_id"] == 1]
        repeats = [10,10.2,9.9,10.1,10,10.3,9.8,10.1,10,9.6]
        blocks = [10.4,10.1,10.3,10.2,10.5,10,10.2,10.3,10.1,9.9]
        for i, row in enumerate(module):
            energy = repeats[i] if i < 10 else blocks[(i - 10) // 4]
            row.update(rails_j=energy, rails_secondary_j=energy - 1)
            row["meter"].update(gross_j=2 * energy, secondary_j=2 * energy - 2)
            row["flags"] = ["battery.assist"] if i in assist_ordinals else ["battery.assist_outside_request"]
        return module

    def test_a7_10_without_assisted_registered_example_all_cells_atomic_quad(self):
        records = self.battery_records({2, 34})
        for inclusive in (False, True):
            for cell in ba.reduce_models(records, self.manifest, inclusive=inclusive):
                factor = 2 if cell["boundary"] == "DC input" else 1
                offset = factor if cell["basis"] == "idle-subtracted secondary" else 0
                diagnostic = cell["without_assisted"]
                self.assertAlmostEqual(cell["mean_j"], 10.16 * factor - offset)
                self.assertAlmostEqual(diagnostic["mean_j"], (0.2 * (100.0 - 9.9) / 9 + 0.8 * (102.0 - 10.2) / 9) * factor - offset)
                self.assertEqual((diagnostic["n_r"], diagnostic["n_b"]), (9, 9))
                self.assertEqual(cell["assisted_member_counts"], {"repeat": 1, "quad": 1})
                self.assertEqual(cell["assisted_unit_counts"], {"repeat": 1, "quad": 1})
                self.assertEqual(len(diagnostic["removed_runs"]), 5)
                self.assertTrue(diagnostic["description_only"])
                self.assertFalse(diagnostic["below_minimum"])
                self.assertNotIn("battery.assist", diagnostic["flags"])
                self.assertEqual(cell["with_assisted_label"], "with assisted members")
        plain = self.battery_records(set())
        self.assertTrue(all("without_assisted" not in p for p in ba.reduce_models(plain, self.manifest)))
        # A second member in the same assisted quad changes member count only.
        records = self.battery_records({2, 34, 35})
        for cell in ba.reduce_models(records, self.manifest):
            self.assertEqual(cell["assisted_member_counts"], {"repeat": 1, "quad": 2})
            self.assertEqual(cell["assisted_unit_counts"], {"repeat": 1, "quad": 1})
            point = ba.combine_passes([cell])[0]
            self.assertEqual(point["without_assisted"]["mean_j"], cell["without_assisted"]["mean_j"])
            self.assertEqual(point["without_assisted"]["pass_status"], "one_pass")
            self.assertEqual(point["without_assisted"]["h_j"], cell["without_assisted"]["h_j"])
            self.assertTrue(point["without_assisted"]["description_only"])

    def test_a7_10_below_minimum_prints_value_counts_and_no_decision(self):
        for survivors in (4, 1, 0):
            with self.subTest(survivors=survivors):
                records = self.battery_records(set(range(10 - survivors)))
                for cell in ba.reduce_models(records, self.manifest):
                    diagnostic = cell["without_assisted"]
                    self.assertEqual((cell["n_r"], cell["n_b"]), (10, 10))
                    self.assertEqual((diagnostic["n_r"], diagnostic["n_b"]), (survivors, 10))
                    self.assertIn("below the registered minimum of 5 units", diagnostic["label"])
                    self.assertTrue(diagnostic["description_only"])
                    if survivors >= 2:
                        self.assertEqual(diagnostic["df"], survivors - 1)
                        self.assertIsNotNone(diagnostic["lower_j"])
                    elif survivors == 1:
                        self.assertIsNotNone(diagnostic["mean_j"])
                        self.assertIsNone(diagnostic["h_j"])
                    else:
                        self.assertIsNone(diagnostic["mean_j"])

    def test_a7_12_unequal_pass_duration_power_is_ratio_of_means(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = archive_campaign(root, pass_duration_scales=(1, 2))
            records = ba.load_records(root / "export", manifest, stage="all")
            passes = ba.reduce_models(records, manifest)
            for point in ba.combine_passes(passes):
                a, b = point["passes"]
                self.assertAlmostEqual(b["duration_s"], 2 * a["duration_s"])
                expected = (a["mean_j"] + b["mean_j"]) / (a["duration_s"] + b["duration_s"])
                self.assertEqual(point["power"], expected)
                if point["boundary"] != "rails":
                    # Same ratio of pass-mean joules to pass-mean seconds as
                    # power and B/T. No half-width for the point bound itself:
                    # NumericTestCase uses the brief's 1e-6 relative/absolute bar.
                    support = sum(r["meter_offset_bound_j"] for r in (a, b)) / sum(
                        r["duration_s"] for r in (a, b))
                    self.assertAlmostEqual(point["meter_offset_bound_w"], support)
                self.assertAlmostEqual(point["power_half_w"], (a["h_j"] + a["B_j"] + b["h_j"] + b["B_j"]) /
                                       (a["duration_s"] + b["duration_s"]))
                self.assertNotAlmostEqual(point["power"], .5 * (a["mean_j"] / a["duration_s"] + b["mean_j"] / b["duration_s"]), places=5)

    def test_a7_12_generated_signed_clock_latency_uses_largest_absolute_extreme(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = archive_campaign(root, clock_latency_ms=(-8, 3))
            for session in manifest["sessions"]:
                stream = kp.parse(Path(session["archive"]) / "sources/night-custody/hazards/meter/stream-001.jsonl")
                stats = stream.fit.stats
                self.assertLess(stats["excess_latency_ms_min"], 0)
                self.assertGreater(stats["excess_latency_ms_max"], 0)
                self.assertGreater(abs(stats["excess_latency_ms_min"]), stats["excess_latency_ms_max"])
            records = ba.load_records(root / "export", manifest, stage="all")
            for record in records:
                meter = record["meter"]
                extrema = [meter["clock_fit"]["excess_latency_ms_" + suffix] for suffix in ("min", "max")]
                self.assertEqual(meter["r_max_s"], max(map(abs, extrema)) / 1000)
                self.assertAlmostEqual(meter["phase_edge_j"], sum(meter["edge_powers_w"]) * (meter["r_max_s"] + .1))

    def test_a7_13_exact_512_decode_denominators_and_printed_label(self):
        self.assertEqual(ba.DECODE_STEPS, 512)
        label = "512 decode forward passes, one of which yields no returned token"
        self.assertEqual(ba.OUTPUT_LABEL, label)
        for point in ba.combine_passes(ba.reduce_models(self.records, self.manifest)):
            self.assertEqual(point["e"], point["mean_j"] / 512)
            self.assertEqual(point["printed_j_per_output_token"], point["e"])
            self.assertEqual(point["time"], point["duration_s"] / 512)
            self.assertEqual(point["BW"], point["bytes"] / point["time"])
            self.assertEqual(point["output_label"], label)

    def test_a7_02_03_08_allowances_and_registered_tabulated_t_still_hold(self):
        from joulewise.aggregate import student_t_critical_95
        for cell in ba.reduce_models(self.records, self.manifest):
            boundary = cell["boundary"]
            reference = cell["neg8_inputs"]["boundaries"][boundary]
            expected_drift = reference["families"][cell["drift_family"]]["allowance_j"] * .5 * cell["drift_scale"]
            # Addendum 8 energy agreement: 1% of this cell's (h+B),
            # above 1e6*epsilon roundoff at the fixture's energy scale.
            bar = .01 * (cell["h_j"] + cell["B_j"])
            self.assertAlmostEqual(cell["kind_averages_j"][ba.BOUND_KINDS[2]], expected_drift, delta=bar)
            if boundary != "rails":
                self.assertGreater(expected_drift, 0)
                self.assertGreaterEqual(cell["B_j"], cell["meter_phase_edge_mean_j"] + expected_drift - bar)
            bound = reference["families"][cell["drift_family"]]["bound_terms"]
            corpus = [r[boundary][cell["drift_family"]] for r in cell["neg8_inputs"]["references"] if r["role"] == "corpus"]
            # D8 pins the owning block-5 tabulated t, not an independently
            # chosen quantile. Equality is intentional: identical arithmetic
            # on identical inputs must retain the registered table value.
            self.assertEqual(bound["prediction_j"], student_t_critical_95(len(corpus) - 1) * statistics.stdev(corpus) *
                             math.sqrt(1 / bound["n_start"] + 1 / bound["n_end"]))

        # Deliberately non-proportional boundary references distinguish each
        # family's own allowance/scale from copying rails into DC or rest.
        records = copy.deepcopy(self.records[:50])
        energies = {"rails": 10, "DC input": 25, "rest": 4}
        durations = {"rails": 3, "DC input": 5, "rest": 2}
        allowances = {"rails": .12, "DC input": .45, "rest": .91}
        for record in records:
            record.update(rails_anchor_j=.3, rails_interpolation_j=.1)
            record["meter"]["phase_edge_j"] = .7
            for boundary in ba.BOUNDARIES:
                reference = record["neg8_inputs"]["boundaries"][boundary]
                reference.update(energy_j=energies[boundary], duration_s=durations[boundary])
                for family in ("gross", "idle_subtracted"):
                    reference["families"][family]["allowance_j"] = allowances[boundary] * (2 if family == "idle_subtracted" else 1)
        cells = ba.reduce_models(records, self.manifest)
        for cell in cells:
            boundary = cell["boundary"]
            gross = next(c for c in cells if c["boundary"] == boundary and c["basis"] == "gross primary")
            scale = max(1, gross["mean_j"] / energies[boundary], cell["duration_s"] / durations[boundary])
            drift = .5 * allowances[boundary] * scale * (2 if cell["drift_family"] == "idle_subtracted" else 1)
            self.assertAlmostEqual(cell["B_j"], {"rails": .4, "DC input": .7, "rest": 1.1}[boundary] + drift)

    def test_a8_d3_method_gap_exceeds_ten_agreement_bars(self):
        assert_d3_exercised(self, self.records, self.manifest)

    def test_a7_11_phase_ends_round_to_nearest_nanosecond_still_holds(self):
        metadata = {"uncertainty_evidence": {"clock_anchor": {"clock_stamps": {
            "sampling_started": {"epoch_s": 0, "monotonic_before_s": 0}}}}}
        events = [{"phase": "decode", "event_type": event, "timestamp_s": stamp}
                  for event, stamp in (("phase_start", 1.2e-9), ("phase_end", 10.8e-9))]
        self.assertEqual(ba._event_span(events, "decode", metadata), [1, 11])


class ReviewerProbeTests(NumericTestCase):
    def test_p02_p05_p06_p08_p10_fixed_tree(self):
        import runpy
        import sys
        probes = FIXTURES / "repro"
        with tempfile.TemporaryDirectory() as directory, patch.object(sys,"path",[str(probes),*sys.path]):
            work = Path(directory)/"p08"
            for script,args in (("p08_e2e_defects.py",[str(work)]),
                                ("p10_failed_member.py",[str(work)]),
                                ("p02_bonferroni_h2_family.py",[]),
                                ("p05_join_drift_passes.py",[str(work/"base")]),
                                ("p06_word_sensitivity.py",[str(work/"base")])):
                with self.subTest(probe=script), patch.object(sys,"argv",[str(probes/script),*args]):
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        runpy.run_path(str(probes/script),run_name="__main__")
                    report = output.getvalue()
                    self.assertTrue(report)
                    self.assertNotIn("exit codes [0, 1]",report)
                    self.assertNotIn("exit codes [1]",report)
                    if script == "p10_failed_member.py":
                        self.assertEqual(report.count("exit [0, 0]"),2)
                        self.assertEqual(report.count("n_r/n_b=10/9 removed=True"),12)
                    if script == "p06_word_sensitivity.py":
                        self.assertIn("differ: 0 of 801",report)
                    print("BYTES_REVIEW_PROBE="+script+"\n"+report,flush=True)


class Q1WithheldCensusTests(unittest.TestCase):
    def test_absent_csv_is_censused_from_collected_session_sidecar(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_json(root / "collected.session.json", {})
            manifest = {"models": [], "sessions": [{"session_id": "collected", "pass_id": 1,
                                                       "archive": str(root / "archive")}]}
            with patch.object(ba, "archive_records", return_value=[]) as read:
                self.assertEqual(ba.load_records(root, manifest, stage="heldout"), [])
            self.assertEqual(read.call_args.kwargs["export_path"], root / "collected.runs.csv")
            self.assertEqual(read.call_args.args[2]["session_id"], "collected")

    def test_blinded_postcommit_keeps_missing_store_and_absent_csv_placeholders(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model = {**ba.read_json(FIXTURES / "campaign_design.json")["models"][3],
                     "config_key": "registered|workload|512"}
            session = {"session_id": "collected", "pass_id": 2}
            manifest = {"models": [model], "sessions": [session]}
            info = {"path": "absent-store.csv", "row_count": 50, "config_key_sha256": {
                hashlib.sha256(model["config_key"].encode()).hexdigest(): 50}}
            _write_json(root / "collected.session.json", {"blinding": {"withheld": info}})
            public = root / "collected.runs.csv"
            public.write_text("run_id,cell_ids\n")
            for csv_present in (True, False):
                with self.subTest(csv_present=csv_present):
                    if not csv_present:
                        public.unlink()
                    with patch.object(ba, "archive_records", side_effect=AssertionError("archive read")):
                        self.assertEqual(ba.load_records(root, manifest, stage="blinded"), [])
                        records = ba.load_records(root, manifest, stage="blinded", stage1_commit="a" * 40)
                    self.assertEqual(len(records), 50)
                    passes = ba.reduce_models(records, manifest, boundaries=("rails",))
                    self.assertEqual({r["status"] for r in passes}, {"missing"})
                    self.assertTrue(all(r["withheld_row_count"] == 50 for r in passes))
                    points = ba.combine_passes(passes)
                    bytes_analyze._missing_labels(points)
                    self.assertEqual({p["status"] for p in points}, {"missing"})
                    self.assertEqual({p["pass_status"] for p in points}, {"no_pass"})

    def test_missing_labels_unions_existing_and_pass_flags_on_survivors(self):
        for status in ("computed", "unavailable"):
            with self.subTest(status=status):
                point = {"status": status, "flags": ["existing.disclosure"], "passes": [
                    {"flags": ["battery.assist"]}, {"flags": ["bytes.withheld_missing"]}]}
                bytes_analyze._missing_labels([point])
                self.assertEqual(point["flags"], ["battery.assist", "bytes.withheld_missing", "existing.disclosure"])
                self.assertEqual(point["status"], "computed" if status == "computed" else "missing")
        optional = {"status": "computed", "pass_status": "one_pass", "passes": [{"flags": []}]}
        bytes_analyze._missing_labels([optional])
        self.assertNotIn("bytes.withheld_missing", optional.get("flags", []))

    def test_missing_file_placeholders_keep_sidecar_counts_and_no_energy(self):
        model = {"model": "heldout", "config_key": "heldout|registered|512"}
        info = {"row_count": 100, "config_key_sha256": {
            hashlib.sha256(model["config_key"].encode()).hexdigest(): 50,
            hashlib.sha256(b"other|registered|512").hexdigest(): 50}}
        rows = list(ba._missing_withheld_records(info, {"models": [model]},
                    {"session_id": "s2-p2", "pass_id": 2}))
        self.assertEqual(len(rows), 50)
        self.assertEqual(len({r["run_id"] for r in rows}), 50)
        self.assertEqual(sum(r["stratum"] == "repeat" for r in rows), 10)
        self.assertEqual(len({r["unit_id"] for r in rows if r["stratum"] == "quad"}), 10)
        for row in rows:
            self.assertEqual(row["withheld_row_count"], 100)
            self.assertEqual(row["withheld_config_row_count"], 50)
            self.assertEqual(row["flags"], ["bytes.withheld_missing"])
            self.assertTrue(row["invalid_energy_record"])
            self.assertNotIn("rails_j", row)


class SubsetReleaseChainTests(unittest.TestCase):
    def command(self, *args, expected=0, cwd=ROOT):
        result = subprocess.run(list(map(str, args)), cwd=cwd, capture_output=True, text=True,
                                env={**os.environ, "JW_B5_SYNTHETIC_ONLY": "1"}, check=False)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout

    def test_export_traversal_uses_registered_pass_not_clock_named_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Filename order deliberately disagrees with the registered passes.
            for name in ("early-clock-pass2", "late-clock-pass1"):
                (root / (name + ".runs.csv")).write_text("unused")
            manifest = {"models": [], "sessions": [
                {"session_id": "early-clock-pass2", "pass_id": 2},
                {"session_id": "late-clock-pass1", "pass_id": 1}]}
            with patch.object(ba, "_export_rows", return_value=[]) as read:
                self.assertEqual(ba.load_records(root, manifest, stage="blinded"), [])
            self.assertEqual([call.args[0].name for call in read.call_args_list],
                             ["late-clock-pass1.runs.csv", "early-clock-pass2.runs.csv"])

    def test_three_worlds_full_synthetic_cli_chain_and_clock_removal(self):
        from joulewise.b6 import blinding
        # Generate full harvest-shaped campaigns in a separate process. The
        # fixture calls the real export boundary; every analysis and release is
        # another CLI process, with native keys and 10 Hz meter streams.
        for world in ("bytes", "resident", "time"):
            with self.subTest(world=world), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                generate = '''
import importlib.util, json, sys
from pathlib import Path
from unittest.mock import patch
from joulewise.b6 import export_runs
spec = importlib.util.spec_from_file_location("campaign", "tests/fixtures/bytes/campaign.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
root = Path(sys.argv[1])
original = export_runs.export
def grouped(*args, **kwargs):
    # Retain an actual pre-change full export using the very same drawn keys.
    original(*args[:4], root / "legacy-export", **kwargs)
    return original(*args, **kwargs, pack_registration={"blinding_group": "bytes", "bytes_pass": int(args[0].name[-1])})
with patch.object(export_runs, "export", side_effect=grouped):
    manifest = fixture.archive_campaign(root, world=sys.argv[2], non_claim=False, release="none",
        pass_duration_scales=(1, 2), clock_latency_ms=(-8, 3))
(root / "manifest.json").write_text(json.dumps(manifest))
'''
                self.command(sys.executable, "-B", "-c", generate, root, world)
                manifest = json.loads((root / "manifest.json").read_text())
                # Register the synthetic configurations using the native module
                # schema; the release tool reads these files, not the manifest.
                archive = Path(manifest["sessions"][0]["archive"])
                config_dirs = []
                for model in manifest["models"]:
                    rid = (model["model"] + "-0").lower().replace(".", "-")
                    dest = root / "synthetic-configs" / model["model"]
                    dest.mkdir(parents=True)
                    shutil.copyfile(archive / "sources/claim-runs" / rid / "config.json", dest / "member.json")
                    config_dirs.append(str(dest.relative_to(root)))
                _write_json(root / "registrations/bytes/registration.json", {
                    "pack_id": "bytes", "blinding_group": "bytes", "modules": [{"config_dirs": config_dirs}]})
                fit_keys = {"neg8_reference", *(m["model"] + "|bytes-synthetic|512"
                            for m in manifest["models"] if m["role"] == "fit")}
                all_keys = {"neg8_reference", *(m["model"] + "|bytes-synthetic|512" for m in manifest["models"])}
                stores = []
                for session in manifest["sessions"]:
                    path = root / "export/bytes" / (session["session_id"] + ".runs.csv")
                    with path.open() as stream:
                        rows = list(csv.DictReader(stream))
                    # R5: 3 fit models x 50 runs; A4.7: 6+3+1+3 references.
                    self.assertEqual(len(rows), 150 + 13)
                    self.assertEqual({r["config_key"] for r in rows}, fit_keys)
                    self.assertNotIn("run_start_utc", rows[0])
                    self.assertEqual([int(r["order_index"]) for r in rows], sorted(int(r["order_index"]) for r in rows))
                    info = json.loads(path.with_name(session["session_id"] + ".session.json").read_text())["blinding"]["withheld"]
                    self.assertEqual(info["row_count"], 7 * 50)  # seven held-out full modules
                    stores.append(path.parent / info["path"])

                def analyze(stage, out, *, legacy=False, keys=None, predictions=None, commit=None, expected=0):
                    args = [sys.executable, ROOT / "scripts/bytes_analyze.py", "--export",
                            root / ("legacy-export" if legacy else "export"), "--manifest", root / "manifest.json",
                            "--stage", stage, "--out", root / out]
                    if keys:
                        args += ["--key-dir", root / keys]
                    if predictions:
                        args += ["--predictions", root / predictions]
                    if commit:
                        args += ["--stage1-commit", commit]
                    return self.command(*args, expected=expected)

                def release(stage, keys, out, commit=None, expected=0):
                    args = [sys.executable, ROOT / "scripts/b6_release_subset.py", "--pack-records-root", root / "private-keys",
                        "--blinding-group", "bytes", "--registrations-root", root / "registrations", "--project-root", root,
                        "--stage", stage, "--out", root / out, "--keys", *sorted(keys)]
                    if commit:
                        args += ["--stage1-commit", commit]
                    return self.command(*args, expected=expected)

                analyze("blinded", "blind-fit")
                points = json.loads((root / "blind-fit/model_estimates.json").read_text())
                self.assertEqual({p["model"] for p in points}, {m["model"] for m in manifest["models"] if m["role"] == "fit"})
                self.assertEqual(json.loads((root / "blind-fit/h1.json").read_text()), [])
                analyze("fit", "before-release", expected=1)
                release("fit", fit_keys, "stage1-keys")
                self.assertEqual({p.name for p in (root / "stage1-keys").iterdir()},
                                 {"pack.json", "release.json", *(blinding._config_filename(k) for k in fit_keys)})
                analyze("fit", "stage1", keys="stage1-keys")
                analyze("fit", "legacy-fit", legacy=True, keys="stage1-keys")
                for name in ("predictions.json", "fit_pass_estimates.json"):
                    self.assertEqual((root / "stage1" / name).read_bytes(), (root / "legacy-fit" / name).read_bytes())
                commitment = (root / "stage1/predictions.json").read_bytes()
                release("heldout", all_keys, "uncommitted-keys", expected=1)
                self.command("git", "init", "-q", root / "stage1")
                self.command("git", "add", ".", cwd=root / "stage1")
                self.command("git", "-c", "user.name=BYTES Synthetic", "-c", "user.email=synthetic@example.invalid",
                             "commit", "-qm", "Freeze synthetic stage-1 predictions", cwd=root / "stage1")
                commit = self.command("git", "rev-parse", "HEAD", cwd=root / "stage1").strip()
                # Before releasing held-out factors, run the blinded held-out
                # agreement ingress. It reads no raw archives or meter values.
                analyze("blinded", "blind-postcommit", commit=commit)
                analyze("blinded", "legacy-blind", legacy=True)
                for name in ("model_estimates.json", "h1.json", "h2.json", "moe.json"):
                    # Exact JSON bytes here test identical inputs and arithmetic:
                    # removing unused clocks must not change a printed number.
                    self.assertEqual((root / "blind-postcommit" / name).read_bytes(), (root / "legacy-blind" / name).read_bytes())
                analyze("heldout", "before-heldout-release", keys="stage1-keys", predictions="stage1/predictions.json", expected=1)
                # Stage 2 explicitly lists all keys so its directory is complete
                # for unchanged _released_rows, including NEG-8 references.
                release("heldout", all_keys, "stage2-keys", commit)
                analyze("heldout", "stage2", keys="stage2-keys", predictions="stage1/predictions.json")
                analyze("heldout", "legacy-heldout", legacy=True, keys="stage2-keys", predictions="stage1/predictions.json")
                for name in ("model_estimates.json", "h1.json", "h2.json", "moe.json", "unavailable.json"):
                    self.assertEqual((root / "stage2" / name).read_bytes(), (root / "legacy-heldout" / name).read_bytes())
                self.assertEqual((root / "stage1/predictions.json").read_bytes(), commitment)
                # 2 selections x 2 bases x 3 boundaries = 12 H2 groups;
                # H1 prints 10 models x (2 passes + mean) x 12 = 360 rows.
                self.assertEqual(len(json.loads((root / "stage2/h1.json").read_text())), 360)
                self.assertEqual(len(json.loads((root / "stage2/h2.json").read_text())), 12)
                for path in stores:
                    path.unlink()
                analyze("heldout", "missing-store", keys="stage2-keys", predictions="stage1/predictions.json")
                missing = json.loads((root / "missing-store/model_estimates.json").read_text())
                heldout = [p for p in missing if p["role"] == "heldout"]
                self.assertTrue(heldout)
                self.assertEqual({p["status"] for p in heldout}, {"missing"})
                self.assertTrue(all("bytes.withheld_missing" in p["flags"] for p in heldout))

class Q1MissingFilesCLIChainTests(unittest.TestCase):
    target = "Qwen3-30B-A3B-4bit"

    def command(self, *args, cwd=ROOT):
        result = subprocess.run(list(map(str, args)), cwd=cwd, capture_output=True, text=True,
            env={**os.environ, "JW_B5_SYNTHETIC_ONLY": "1"}, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_one_withheld_file_missing_cli_chain(self):
        self.chain("one")

    def test_both_withheld_files_missing_cli_chain(self):
        self.chain("both")

    def test_genuinely_uncollected_optional_pass_cli_chain(self):
        self.chain("optional")

    def chain(self, case):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generate = '''
import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("campaign", "tests/fixtures/bytes/campaign.py")
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
root = Path(sys.argv[1])
manifest = f.archive_campaign(root, non_claim=False, release="none", subpack_sessions=True,
    uncollected_sessions=("bytes-s2-p2",) if sys.argv[2] == "optional" else (),
    pass_duration_scales=(1, 2), clock_latency_ms=(-8, 3))
(root / "manifest.json").write_text(json.dumps(manifest))
'''
            self.command(sys.executable, "-B", "-c", generate, root, case)
            manifest = ba.read_json(root / "manifest.json")
            expected_sessions = [f"bytes-s{s}-p1" for s in range(1, 7)] + [
                f"bytes-s{s}-p2" for s in range(6, 0, -1) if case != "optional" or s != 2]
            self.assertEqual([s["session_id"] for s in manifest["sessions"]], expected_sessions)
            self.assertEqual(len(manifest["sessions"]), 11 if case == "optional" else 12)
            paths = {p.name.removesuffix(".runs.csv"): p for p in (root / "export").rglob("*.runs.csv")}
            self.assertEqual(set(paths), set(expected_sessions))
            # Release membership is read from native registered run configs.
            config_dirs = []
            for model in manifest["models"]:
                run_id = (model["model"] + "-0").lower().replace(".", "-")
                source = next(Path(s["archive"]) / "sources/claim-runs" / run_id / "config.json"
                              for s in manifest["sessions"] if (
                                  Path(s["archive"]) / "sources/claim-runs" / run_id / "config.json").is_file())
                dest = root / "configs" / model["model"]
                dest.mkdir(parents=True)
                shutil.copyfile(source, dest / "run.json")
                config_dirs.append(str(dest.relative_to(root)))
            _write_json(root / "registrations/bytes/registration.json", {
                "pack_id": "bytes", "blinding_group": "bytes", "modules": [{"config_dirs": config_dirs}]})
            for pass_id in ((2,) if case == "one" else (1, 2) if case == "both" else ()):
                path = paths[f"bytes-s2-p{pass_id}"]
                info = ba.read_json(path.with_name(f"bytes-s2-p{pass_id}.session.json"))["blinding"]["withheld"]
                self.assertEqual(info["row_count"], 50)
                self.assertEqual(info["config_key_sha256"], {
                    hashlib.sha256(next(m["config_key"] for m in manifest["models"]
                                        if m["model"] == self.target).encode()).hexdigest(): 50})
                (path.parent / info["path"]).unlink()
            fit_keys = {"neg8_reference", *(m["config_key"] for m in manifest["models"] if m["role"] == "fit")}
            all_keys = {"neg8_reference", *(m["config_key"] for m in manifest["models"])}
            evidence = []

            def summarize(stage, out=None, stdout=""):
                def read(name):
                    path = root / out / (name + ".json") if out else None
                    return ba.read_json(path) if path and path.is_file() else []
                def primary(row):
                    return row["boundary"] == "rails" and row["basis"] == "gross primary" and row["selection"] == "primary"
                passes = read("blinded_pass_estimates") or read("heldout_pass_estimates") or read("fit_pass_estimates")
                points = [p for p in read("model_estimates") if p["model"] == self.target and primary(p)]
                evidence.append({"stage": stage, "exit": 0,
                    "passes": [{k: p[k] for k in ("pass_id", "status", "flags", "withheld_row_count", "withheld_config_row_count") if k in p}
                               for p in passes if p["model"] == self.target and primary(p)],
                    "point": [{k: p[k] for k in ("status", "pass_status", "n_passes", "flags") if k in p} for p in points],
                    "h1": [{k: p[k] for k in ("pass_id", "status", "word", "flags") if k in p}
                           for p in read("h1") if p["model"] == self.target and primary(p)],
                    "moe": [{k: p[k] for k in ("status", "answer", "flags") if k in p} for p in read("moe") if primary(p)],
                    "h2": [{k: p[k] for k in ("analysis", "n", "k")} for p in read("h2") if primary(p)],
                    "stdout": stdout.strip()})

            def analyze(stage, out, *, keys=None, predictions=None, commit=None):
                args = [sys.executable, "-B", ROOT / "scripts/bytes_analyze.py", "--export", root / "export",
                        "--manifest", root / "manifest.json", "--stage", stage, "--out", root / out]
                if keys:
                    args += ["--key-dir", root / keys]
                if predictions:
                    args += ["--predictions", root / predictions]
                if commit:
                    args += ["--stage1-commit", commit]
                stdout = self.command(*args)
                summarize(out, out, stdout)

            def release(stage, keys, out, commit=None):
                args = [sys.executable, "-B", ROOT / "scripts/b6_release_subset.py", "--pack-records-root", root / "private-keys",
                        "--blinding-group", "bytes", "--registrations-root", root / "registrations", "--project-root", root,
                        "--stage", stage, "--out", root / out, "--keys", *sorted(keys)]
                if commit:
                    args += ["--stage1-commit", commit]
                summarize(out, stdout=self.command(*args))

            analyze("blinded", "blinded-before-commit")
            pre = root / "blinded-before-commit"
            self.assertEqual({p["model"] for p in ba.read_json(pre / "model_estimates.json")},
                             {m["model"] for m in manifest["models"] if m["role"] == "fit"})
            for name in ("h1", "moe", "h2"):
                self.assertEqual(ba.read_json(pre / (name + ".json")), [])
            release("fit", fit_keys, "fit-keys")
            analyze("fit", "fit", keys="fit-keys")
            predictions = root / "fit/predictions.json"
            frozen_bytes = predictions.read_bytes()
            self.command("git", "init", "-q", root / "fit")
            self.command("git", "add", ".", cwd=root / "fit")
            self.command("git", "-c", "user.name=BYTES Synthetic", "-c", "user.email=synthetic@example.invalid",
                         "commit", "-qm", "Commit synthetic Q1 predictions", cwd=root / "fit")
            commit = self.command("git", "rev-parse", "HEAD", cwd=root / "fit").strip()
            summarize("stage1-git-commit", stdout=commit)
            analyze("blinded", "blinded-post-commit", commit=commit)
            release("heldout", all_keys, "heldout-keys", commit)
            analyze("heldout", "heldout", keys="heldout-keys", predictions="fit/predictions.json")
            self.assertEqual(predictions.read_bytes(), frozen_bytes)  # immutable identity/hash input
            for out in ("blinded-post-commit", "heldout"):
                points = [p for p in ba.read_json(root / out / "model_estimates.json") if p["model"] == self.target]
                self.assertEqual(len(points), 4 if out.startswith("blinded") else 12)
                for point in points:
                    self.assertEqual(point["pass_status"], "no_pass" if case == "both" else "one_pass")
                    self.assertEqual(point["n_passes"], 0 if case == "both" else 1)
                    self.assertEqual(point["status"], "missing" if case == "both" else "computed")
                    self.assertEqual("bytes.withheld_missing" in point.get("flags", []), case != "optional")
                    missing = [p for p in point["passes"] if p["status"] == "missing"]
                    self.assertEqual(len(missing), 2 if case == "both" else 1 if case == "one" else 0)
                    self.assertEqual({p["pass_id"] for p in point["passes"]}, {1} if case == "optional" else {1, 2})
                    for row in missing:
                        self.assertEqual(row["withheld_row_count"], 50)
                        self.assertEqual(row["withheld_config_row_count"], 50)
                        self.assertIn("bytes.withheld_missing", row["flags"])
                    if case == "both":
                        self.assertNotIn("e", point)
                h1 = [r for r in ba.read_json(root / out / "h1.json") if r["model"] == self.target]
                self.assertTrue(h1)
                for row in h1:
                    if case == "both":
                        self.assertEqual(row["status"], "missing")
                        self.assertNotIn("word", row)
                    else:
                        self.assertEqual(row["pass_status"], "one_pass")
                        self.assertIn(row["word"], {"bytes", "resident", "time", "unresolved", "neither"})
                        if case == "one" and row["pass_id"] == "mean":
                            self.assertIn("bytes.withheld_missing", row["flags"])
                moe = ba.read_json(root / out / "moe.json")
                self.assertEqual(len(moe), 4 if out.startswith("blinded") else 12)
                for row in moe:
                    self.assertEqual(row.get("status") == "missing", case == "both")
                    if case == "both":
                        self.assertEqual(row["answer"], "missing")
                        self.assertEqual([m["model"] for m in row["missing_models"]], [self.target])
                for row in ba.read_json(root / out / "h2.json"):
                    primary = row["analysis"] == "primary"
                    self.assertEqual(row["n"], (9 if case == "both" else 10) if primary else (8 if case == "optional" else 9))
                    self.assertEqual(row["k"], 11 if row["boundary"] == "rest" else 9)
                    self.assertEqual(row["description_only"], not primary)
            path = paths["bytes-s2-p1" if case == "optional" else "bytes-s2-p2"]
            stdout = self.command(sys.executable, "-B", ROOT / "scripts/b6_unblind.py", "--export", path,
                "--key-dir", root / "heldout-keys", "--stage1-commit", commit, "--out", root / "unblinded.csv")
            unblind = json.loads(stdout)
            self.assertEqual(unblind.get("flags", []), [] if case == "optional" else ["bytes.withheld_missing"])
            self.assertEqual(unblind["rows"], 113 if case == "optional" else 63)
            summarize("unblind", stdout=stdout)
            print("BYTES_Q1_CHAIN=" + json.dumps({"case": case, "sessions": len(manifest["sessions"]),
                  "evidence": evidence}, sort_keys=True), flush=True)


if __name__ == "__main__":
    unittest.main()
