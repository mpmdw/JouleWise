"""BYTES worked examples and synthetic archive tests; never run inference."""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import math
import random
import statistics
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise import bytes_analysis as ba
from joulewise.external import km003c_parse as kp
from scripts import bytes_analyze

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/bytes"


def fit_points():
    return [{"bytes": x, "resident": x, "time": x, "e": 2 * x,
             "lower": 2 * x - 1, "upper": 2 * x + 1} for x in (1, 2, 3)]


def query(b=2, r=10, t=20, e=4, width=0):
    return {"bytes": b, "resident": r, "time": t, "e": e,
            "lower": e - width, "upper": e + width}


class H1WorkedExamples(unittest.TestCase):
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


class H2WorkedExamples(unittest.TestCase):
    def test_two_term_hand_computed(self):
        # Centered x [-2,-1,0,1,2]; residuals [1,-2,2,-2,1] are orthogonal
        # to intercept and x. beta=[3,2], SSE=14, MSE=14/3, Sxx=10.
        fit = ba.ols([[x] for x in range(5)], [4, 3, 9, 7, 12], family_size=1)
        self.assertAlmostEqual(fit["coefficients"][0], 3)
        self.assertAlmostEqual(fit["coefficients"][1], 2)
        self.assertAlmostEqual(fit["mse"], 14 / 3)
        self.assertAlmostEqual(fit["covariance"][1][1], 7 / 15)
        self.assertAlmostEqual(fit["critical"], 3.182446305, places=8)
        half = fit["critical"] * math.sqrt(7 / 15)
        self.assertAlmostEqual(fit["intervals"][1][0], 2 - half)
        self.assertAlmostEqual(fit["intervals"][1][1], 2 + half)
        delta = ba.deviation(fit, [2], 8)
        self.assertAlmostEqual(delta["deviation_w"], 1)
        self.assertAlmostEqual(delta["upper_w"] - 1, fit["critical"] * math.sqrt(14 / 3 * 1.2))

    def test_extended_and_rest_coefficients_by_orthogonal_design(self):
        # All eight corners of a cube; x1,x2 and noise x3 are orthogonal.
        rows = [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
        fit = ba.ols([[a, b] for a, b, _ in rows], [5 + 2*a + 3*b + c for a, b, c in rows])
        for actual, expected in zip(fit["coefficients"], (5, 2, 3)):
            self.assertAlmostEqual(actual, expected)
        self.assertAlmostEqual(fit["mse"], 8 / 5)
        for i in range(3):
            self.assertAlmostEqual(fit["covariance"][i][i], 1 / 5)
        self.assertEqual(fit["family_size"], 23)
        self.assertGreater(fit["critical"], ba.student_t_quantile(.975, 5))

    def test_scale_invariance_and_singular_refusal(self):
        fit = ba.ols([[x * 1e9] for x in range(5)], [4, 3, 9, 7, 12])
        self.assertAlmostEqual(fit["coefficients"][1] * 1e9, 2)
        with self.assertRaises(ba.AnalysisError):
            ba.ols([[x, 2*x] for x in range(5)], list(range(5)))


class MeterWorkedExamples(unittest.TestCase):
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


class RegisteredArithmeticTests(unittest.TestCase):
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


class BoundaryAndStagingTests(unittest.TestCase):
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
        records[10]["nonphysical_excluded"] = True
        self.assertEqual(len(ba._kept(records, True)[0]), 46)
        records[10]["nonphysical_excluded"] = False
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
                self.assertAlmostEqual(result["rest"]["coefficients"][2], .4, delta=.03)
        self.assertEqual(len(primary), 23)

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


def archive_campaign(root, *, world="bytes", seed=1100):
    """1000 on-disk runs: real mock trace reducer -> harvest layout -> B6 export.

    No calibration hardware is claimed: the zero phase envelope is explicitly
    synthetic, with missing operative evidence disclosed. Each energy passes
    through reduce_bundle and the full CLI, not a summary oracle.
    """
    from types import SimpleNamespace
    from joulewise.b6 import export_runs, calibration
    from decimal import Decimal
    from tests.b6.support import document
    from joulewise.clock import FakeClock
    from joulewise.bundle import sanitize_id_component, _capture_source_state
    from joulewise.reduce import reduce_bundle
    from tests.test_reduce import BundleBuilder, load_config
    from joulewise.interfaces import PowerSample
    design = ba.read_json(FIXTURES / "campaign_design.json")
    manifest = {"synthetic": True, "models": design["models"], "sessions": []}
    rng = random.Random(seed)
    source_state = _capture_source_state()
    for pass_id in (1, 2):
        session_id = "bytes-p" + str(pass_id)
        archive = root / session_id
        bundles = archive / "sources/claim-runs"
        roster, evidence_members, meter_samples = [], [], []
        # Native meter samples at 10 Hz; zero-latency synthetic clock, no wrap shortcut.
        tick = 1000
        meter_samples.extend([(.2, tick - 2), (.2, tick - 1)])
        for model in manifest["models"]:
            b = (model["W_bytes"] + model["KV_bytes"]) / 1e9
            resident = model["R_bytes"] / 1e9
            duration = model["synthetic_duration_s"]
            tau = duration / 511
            truth = .01 * b if world == "bytes" else 3 * tau if world == "time" else .01 * resident
            for ordinal in range(50):
                run_id = sanitize_id_component(model["model"] + "-" + str(ordinal))
                energy = truth * 511 * (1 + rng.gauss(0, .002))
                power = energy / duration
                start = tick / 10
                decode_start, end = start + 2, start + 2 + duration
                config = load_config(run_id=run_id, model={"name": model["model"], "family": "mock",
                    "weight_format": "mock", "context_window": 4096}, workload_profile={"name": "bytes-synthetic",
                    "prompt_tokens": 2048, "output_tokens": 512, "repetitions": 1, "warmup_runs": 1})
                with patch("joulewise.bundle._capture_source_state", return_value=source_state):
                    builder = BundleBuilder(bundles, config, FakeClock(start=1000))
                builder.measured_window(start + 1, end)
                builder.add_event("stage_started", "idle_baseline", start)
                builder.add_event("stage_completed", "idle_baseline", start + 1)
                builder.add_phase("prefill", start + 1, decode_start)
                builder.add_phase("decode", decode_start, end,
                    metadata={"output_tokens": 512, "requested_output_tokens": 512})
                # Compact constant-power point trace: all phase edges and at least
                # three records per phase, retaining the full pilot-scale span.
                stamps = [start+1, start+1.25, start+1.5, start+1.75,
                          decode_start, decode_start+duration/3,
                          decode_start+2*duration/3, end, end+.1]
                builder.write_trace([PowerSample(timestamp_s=t, power_w=power,
                    source="mock", rail="mock") for t in stamps])
                with patch("joulewise.bundle._capture_source_state", return_value=source_state):
                    bundle = builder.write_metadata(rail_manifest=["mock"], workload_observed={"output_token_count": 512})
                # Real desk reducer under the repository's mock telemetry path.
                summary = reduce_bundle(bundle).to_dict()
                actual = summary["phase_energy_j"]["decode"]
                if not math.isclose(actual, energy, rel_tol=1e-7):
                    raise AssertionError((actual, energy))
                summary.update(status="succeeded", bytes_synthetic_timing_fixture=True, energy_anchor_shift_envelopes={"/phase_energy_j/decode": {
                    "point_j": actual, "lower_j": actual, "upper_j": actual, "max_abs_delta_j": 0}},
                    energy_bound_terms_j={"E_interpolation_joint_edge_bound_j": 0})
                _write_json(archive / "withheld/reductions" / (run_id + ".summary_metrics.rereduced.json"), summary)
                metadata = ba.read_json(bundle / "metadata.json")
                metadata["uncertainty_evidence"] = {"clock_anchor": {"clock_stamps": {
                    "sampling_started": {"epoch_s": start, "monotonic_before_s": start}}}}
                _write_json(bundle / "metadata.json", metadata)
                unit = {"cell_id": model["cell_ids"][0], "stratum": "repeat" if ordinal < 10 else "quad",
                        "unit_id": str(ordinal if ordinal < 10 else (ordinal - 10) // 4)}
                roster.append({"run_id": run_id, "stage_id": "decode", "role": "science", "units": [unit]})
                evidence_members.append(SimpleNamespace(run_id=run_id, stage_id="decode", role="science",
                                                       status="succeeded", config_key=model["model"]))
                end_tick = tick + 20 + round(duration * 10)
                meter_samples.extend((.2 if t < tick + 20 else 2 * power, t) for t in range(tick, end_tick))
                meter_samples.extend([(.2, end_tick), (.2, end_tick + 1)])
                tick = end_tick + 2
        header = {"k": "h", "status": "streaming", "rate_idx": 1, "start_raw_ns": 0, "start_mono_ns": 0}
        batches = []
        for i in range(0, len(meter_samples), 10):
            part = meter_samples[i:i + 10]
            payload = b"".join(kp.SAMPLE.pack((t * 100) % kp.WRAP, 0, 1_000_000,
                round(w * 1e6), 0, 0, 0, 0) for w, t in part)
            stamp = part[-1][1] * 100_000_000
            batches.append({"k": "b", "tx": stamp, "rx": stamp, "n": len(part), "p": payload.hex(), "smc": {"B0AC": 0}})
        stream = archive / "sources/night-custody/hazards/meter/stream-001.jsonl"
        stream.parent.mkdir(parents=True)
        trailer = {"k": "t", "end_raw_ns": tick * 100_000_000, "end_mono_ns": tick * 100_000_000}
        stream.write_text("".join(json.dumps(item) + "\n" for item in (header, *batches, trailer)))
        _write_json(archive / "derived/roster.json", {"pack_id": "bytes", "attempt": 1, "members": roster})
        acceptance = {"pack_id": "bytes", "session_id": session_id, "verdict": "PASS", "counting": True,
                      "excluding": [], "flag_counts": {}, "emitted_flags": [],
                      "calibration": calibration.evaluate(calibration.Capture(Decimal(".040"), "valid"),
                          calibration.Capture(Decimal(".030"), "valid"), document(), [], [session_id], False)}
        _write_json(archive / "derived/b6-acceptance.json", acceptance)
        (archive / "derived/flags.jsonl").write_text("")
        evidence = SimpleNamespace(stages=[SimpleNamespace(members=evidence_members)], runtime={}, session_id=session_id)
        export_runs.export(archive, {}, root / "registration", root / "keys", root / "export", non_claim=True,
                           evidence=evidence, acceptance_record=acceptance)
        manifest["sessions"].append({"session_id": session_id, "archive": str(archive), "pass_id": pass_id,
            "drift_allowance_j": dict.fromkeys(ba.BOUNDARIES, .01),
            "drift_reference": {"energy_j": dict.fromkeys(ba.BOUNDARIES, 10), "duration_s": 3, "test7_passed": False}})
    return manifest


class ProductionArchiveTests(unittest.TestCase):
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
                self.assertAlmostEqual(row["meter"]["gross_j"], 2 * row["rails_j"], delta=1e-3)
            _write_json(root/"manifest.json",manifest)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(bytes_analyze.main(["--export",str(root/"export"),"--manifest",str(root/"manifest.json"),
                    "--stage","fit","--out",str(root/"fit")]),0)
                prediction_bytes = (root/"fit/predictions.json").read_bytes()
                self.assertEqual(bytes_analyze.main(["--export",str(root/"export"),"--manifest",str(root/"manifest.json"),
                    "--stage","heldout","--predictions",str(root/"fit/predictions.json"),"--out",str(root/"heldout")]),0)
            self.assertEqual((root/"fit/predictions.json").read_bytes(),prediction_bytes)
            self.assertEqual(len(ba.read_json(root/"heldout/h1.json")),120)
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
            self.assertTrue(all(r["boundary"]=="rails" for r in evaluated["h1"]))
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


class CampaignWordRates(unittest.TestCase):
    def test_twenty_production_shaped_campaigns_per_world(self):
        from collections import Counter
        design = ba.read_json(FIXTURES / "campaign_design.json")
        report = []
        for world, seeds in design["seeds"].items():
            words, coverage = Counter(), Counter()
            held_models = [m["model"] for m in design["models"] if m["role"]=="heldout"]
            # Population OLS slope for the fixed ten-model design; resident
            # world also reports the structural epsilon of the extended fit.
            xs = [(m["W_bytes"]+m["KV_bytes"])/1e9*511/m["synthetic_duration_s"] for m in design["models"]]
            ys = [.01*x if world=="bytes" else 3 if world=="time" else
                  .01*m["R_bytes"]/1e9*511/m["synthetic_duration_s"] for x,m in zip(xs,design["models"])]
            mx,my = statistics.fmean(xs),statistics.fmean(ys)
            epsilon = math.fsum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.fsum((x-mx)**2 for x in xs)
            for seed in seeds:
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    manifest = archive_campaign(root, world=world, seed=seed)
                    _write_json(root/"manifest.json",manifest)
                    with contextlib.redirect_stdout(io.StringIO()):
                        code = bytes_analyze.main(["--export",str(root/"export"),"--manifest",str(root/"manifest.json"),
                                                   "--stage","all","--out",str(root/"out")])
                    self.assertEqual(code,0)
                    self.assertEqual(ba.read_json(root/"out/unavailable.json"),[])
                    for row in ba.read_json(root/"out/h1.json"):
                        if row["selection"]=="primary" and row["basis"]=="gross primary" and row["role"]=="heldout":
                            words[row["boundary"],row["model"],row["word"]] += 1
                    for row in ba.read_json(root/"out/h2.json"):
                        if row["selection"]=="primary" and row["basis"]=="gross primary":
                            factor = 2 if row["boundary"]=="DC input" else 1
                            for fit,truth in (("two_term",epsilon*factor),
                                              ("resident_extended",(.01 if world=="bytes" else 0)*factor)):
                                lo,hi = row[fit]["intervals"][1]
                                coverage[row["boundary"],fit] += lo<=truth<=hi
                print(f"BYTES synthetic {world} seed {seed} complete",flush=True)
            n = len(seeds)
            self.assertGreaterEqual(n,20)
            rate = lambda count: {"rate":count/n,"MCSE":math.sqrt((count/n)*(1-count/n)/n)}
            word_rows = []
            for boundary in ba.BOUNDARIES:
                for model in held_models:
                    counts = {w:words[boundary,model,w] for w in (*ba.HYPOTHESES,"unresolved","neither")}
                    self.assertEqual(sum(counts.values()),n)
                    word_rows.append({"boundary":boundary,"model":model,"words":{w:rate(c) for w,c in counts.items()}})
            report.append({"world":world,"campaigns":n,"seeds":seeds,"two_term_population_epsilon":epsilon,
                "structural_extended_epsilon":.01 if world=="bytes" else 0,
                "word_rates":word_rows,"H2_coverage":[{"boundary":b,"fit":f,**rate(coverage[b,f])}
                    for b in ba.BOUNDARIES for f in ("two_term","resident_extended")]})
        print("BYTES_SIMULATION_REPORT="+json.dumps(report,sort_keys=True),flush=True)


if __name__ == "__main__":
    unittest.main()
