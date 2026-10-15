"""BYTES worked examples and synthetic archive tests; never run inference."""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import math
import random
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

    def test_gross_own_idle_and_separate_clock_bound(self):
        result = ba.meter_decode(self.stream(), [4_000_000_000, 6_000_000_000],
                                [1_000_000_000, 3_000_000_000], clock_bound_ns=50_000_000)
        self.assertAlmostEqual(result["gross_j"], 20)
        self.assertAlmostEqual(result["secondary_j"], 0)
        self.assertAlmostEqual(result["gross_clock_j"], 0)
        self.assertEqual(result["n"], 20)

    def test_step_envelope_and_negative_secondary(self):
        stream = self.stream([20] * 40 + [10] * 61)
        result = ba.meter_decode(stream, [4_000_000_000, 6_000_000_000],
                                [1_000_000_000, 3_000_000_000], clock_bound_ns=100_000_000)
        self.assertAlmostEqual(result["gross_j"], 20)
        self.assertAlmostEqual(result["secondary_j"], -20)
        self.assertAlmostEqual(result["gross_clock_j"], 1)

    def test_missing_mapping_empty_span_and_coverage_refuse(self):
        stream = self.stream()
        stream.header = {}
        with self.assertRaises(ba.AnalysisError):
            ba.meter_decode(stream, [4_000_000_000, 6_000_000_000], [1, 2], clock_bound_ns=0)
        with self.assertRaises(ba.AnalysisError):
            ba.meter_decode(self.stream(), [0, 6_000_000_000], [1, 2], clock_bound_ns=1)


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

    def test_real_inputs_refuse_without_operative_bracket_join(self):
        with self.assertRaisesRegex(ba.AnalysisError, "operative-bracket"):
            ba.reduce_models([], {"synthetic": False})

    def test_current_shared_kernel_gap_is_explicit(self):
        from joulewise import paper_reported_energy as registered
        self.assertTrue(callable(registered._project_cell))
        # Regression of the actual source capability, not a reimplementation.
        if not hasattr(registered, "estimate_phase_energy"):
            with self.assertRaisesRegex(ba.AnalysisError, "shared-kernel scope"):
                ba._registered_estimate([], [], [])

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
    synthetic. Each energy passes through reduce_bundle, not a summary oracle.
    """
    from types import SimpleNamespace
    from joulewise.b6 import export_runs
    from joulewise.clock import FakeClock
    from joulewise.bundle import sanitize_id_component, _capture_source_state
    from joulewise.reduce import reduce_bundle
    from tests.test_reduce import BundleBuilder, constant_samples, load_config
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
            truth = .01 + .01 * b if world == "bytes" else .01 + 3 * tau if world == "time" else .01 + .01 * resident
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
                builder.write_trace(constant_samples(start + 1, end + .1, 10, power))
                with patch("joulewise.bundle._capture_source_state", return_value=source_state):
                    bundle = builder.write_metadata(rail_manifest=["mock"], workload_observed={"output_token_count": 512})
                # Real desk reducer under the repository's mock telemetry path.
                summary = reduce_bundle(bundle).to_dict()
                actual = summary["phase_energy_j"]["decode"]
                if not math.isclose(actual, energy, rel_tol=1e-7):
                    raise AssertionError((actual, energy))
                summary.update(status="succeeded", energy_anchor_shift_envelopes={"/phase_energy_j/decode": {
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
                      "excluding": [], "flag_counts": {}, "emitted_flags": []}
        _write_json(archive / "derived/b6-acceptance.json", acceptance)
        (archive / "derived/flags.jsonl").write_text("")
        evidence = SimpleNamespace(stages=[SimpleNamespace(members=evidence_members)], runtime={}, session_id=session_id)
        export_runs.export(archive, {}, root / "registration", root / "keys", root / "export", non_claim=True,
                           evidence=evidence, acceptance_record=acceptance)
        manifest["sessions"].append({"session_id": session_id, "archive": str(archive), "pass_id": pass_id,
            "meter_clock_bound_ns": 1_000_000, "drift_allowance_j": dict.fromkeys(ba.BOUNDARIES, .01),
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
            from joulewise import paper_reported_energy as registered
            if not hasattr(registered, "estimate_phase_energy"):
                with self.assertRaisesRegex(ba.AnalysisError, "shared-kernel scope"):
                    ba.reduce_models(fit, manifest)


class CampaignWordRates(unittest.TestCase):
    def test_twenty_production_shaped_campaigns_per_world(self):
        from collections import Counter
        from joulewise import paper_reported_energy as registered
        if not hasattr(registered, "estimate_phase_energy"):
            self.skipTest("60-campaign rates blocked: registered Block-5 general estimator is outside WRITE scope")
        design = ba.read_json(FIXTURES / "campaign_design.json")
        for world, seeds in design["seeds"].items():
            words = Counter()
            campaigns = 0
            for seed in seeds:
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    manifest = archive_campaign(root, world=world, seed=seed)
                    fit = ba.load_records(root / "export", manifest, stage="fit")
                    frozen = ba.frozen_predictions(ba.combine_passes(
                        ba.reduce_models(fit, manifest) + ba.reduce_models(fit, manifest, inclusive=True)), manifest)
                    heldout = ba.load_records(root / "export", manifest, stage="heldout")
                    points = frozen["fit_points"] + ba.combine_passes(
                        ba.reduce_models(heldout, manifest) + ba.reduce_models(heldout, manifest, inclusive=True))
                    result = ba.evaluate(points, frozen)
                    moes = {m["model"] for m in manifest["models"] if m["moe"]}
                    for row in result["h1"]:
                        if row["selection"] == "primary" and row["basis"] == "gross primary" and row["model"] in moes:
                            words[row["word"]] += 1
                    campaigns += 1
            total = sum(words.values())
            print(json.dumps({"world": world, "seeds": seeds, "campaigns": campaigns,
                              "decisive_MoE_boundary_words": dict(words),
                              "correct_word_rate": words[world] / total}, sort_keys=True))
            self.assertEqual(campaigns, 20)
            self.assertEqual(total, 180)
            self.assertEqual(words[world], total)


if __name__ == "__main__":
    unittest.main()
