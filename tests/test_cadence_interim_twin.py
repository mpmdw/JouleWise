import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cadence_interim_twin.py"
HAS_NUMPY = importlib.util.find_spec("numpy") is not None


def example_outputs():
    channels = {}
    for channel, coefficient in (("gpu_rail", 2.0), ("dc_in", 4.0)):
        channels[channel] = {
            "columns": ["p1"], "coefficients": {"p1": coefficient},
            "fold_coefficients": {"day1": {"p1": coefficient}},
            "fold_coefficients_no_heat": {"day1": {"p1": coefficient}},
            "qualified": "not_run",
            "lodo": {"hot": {"verdict": "passes"}, "no_heat": {"hot": {"verdict": "fails"}},
                     "folds_delta_dropped": []},
            "trace_coverage": {"min": 1.0, "n_legs_under_0_99": 0},
            "marked_sensitivity": {"coefficients_without": None, "fit_without": None},
        }
    stage1 = {"tripwires": {key: {"trips": False} for key in (
        "dev_included_below_45", "days_below_4", "cell_below_10", "start_reading_invalid_over_10pct", "hp01_below_9",
    )}, "soak_retries": {"spans_with_retry": 0}}
    sharing = {"qualified_interim_half": {"verdict": "passes"}, "channels": channels}
    coefficients = {**sharing, "delta_column": "kept", "onset": {"sigma_s": 2.0}}
    fit = {**sharing, "soak_retries": {"spans_with_retry": 0}, "ledger_gate": "ignored"}
    step3 = {"cells": [{"prompt_tokens": 2, "status": "ok", "gamma_estimable": True}],
             "tripwire": {"decision": "within", "trips": False}}
    return stage1, coefficients, fit, step3


def parent_agreement(frame):
    """Test-only parent checker for the fields and tolerances this child emits."""
    if frame is None:
        return "not_evaluable"
    def equal(left, right, tolerance):
        if type(left) != type(right):
            return False
        if isinstance(left, dict):
            return left.keys() == right.keys() and all(equal(left[k], right[k], tolerance) for k in left)
        if isinstance(left, list):
            return len(left) == len(right) and all(equal(a, b, tolerance) for a, b in zip(left, right))
        if type(left) in (int, float) and tolerance:
            return abs(left - right) <= tolerance * max(abs(left), abs(right))
        return left == right

    pairs = [(p, 1e-8) for p in frame["coefficients"].values()]
    pairs += [(p, 0) for p in frame["trace_coverage"].values()]
    pairs += [(frame["censored_fit"], 1e-6), (frame["verdicts"], 0), (frame["soak_retries"], 0)]
    return "yes" if all(equal(p["primary"], p["twin"], t) for p, t in pairs) else "no"


def soak_attempt(number, refused=None, output_dir="soak"):
    return {"attempt": number, "started_epoch_s": 100.0 + number, "refused": refused, "output_dir": output_dir}


def soak_refused_step(number, reason):
    name = "soak" if number == 1 else f"soak.a{number}"
    return {"name": name, "rc": 2, "error": f"SoakRefusal: {reason}"}


class ComparisonTests(unittest.TestCase):
    def test_rl184_f06_f07_near_zero_still_returns_no(self):
        from copy import deepcopy
        from scripts.cadence_interim_twin import comparison_frame, projections

        stage1, coefficients, fit, step3 = example_outputs()
        left = projections(stage1, coefficients, fit, step3)
        for metric, tolerance in (("gpu_rail", 1e-8), ("censored_fit", 1e-6)):
            with self.subTest(metric=metric):
                primary, twin = deepcopy(left), deepcopy(left)
                if metric == "gpu_rail":
                    primary["coefficients"][metric] = {"p1": 1.0361e-14}
                    twin["coefficients"][metric] = {"p1": -3.3672e-14}
                else:
                    primary[metric] = {"t_p_s": 1.7286e-17}
                    twin[metric] = {"t_p_s": -5.2905e-17}
                frame = comparison_frame(primary, twin)
                self.assertEqual(parent_agreement(frame), "no")
                self.assertGreater(frame["max_relative_difference"][metric], tolerance)
                self.assertTrue(all(value == 0 for key, value in frame["max_relative_difference"].items()
                                    if key != metric))

    def test_registered_projection_and_parent_derived_agreement(self):
        from scripts.cadence_interim_twin import comparison_frame, projections

        stage1, c, f, step3 = example_outputs()
        primary = projections(stage1, c, f, step3)
        self.assertEqual(primary["verdicts"]["D#/cells"], {"2": {"gamma_estimable": True, "status": "ok"}})
        f["ledger_gate"] = "changed"
        match = comparison_frame(primary, projections(stage1, c, f, step3))
        self.assertNotIn("agreement", match)
        self.assertEqual(parent_agreement(match), "yes")
        self.assertTrue(all(value == 0 for value in match["max_relative_difference"].values()))

        for channel in ("dc_in", "gpu_rail"):
            for path, field in ((f"C#/channels/{channel}/coefficients", None),
                                (f"F#/channels/{channel}/fold_coefficients_no_heat", "day1")):
                for factor, expected in ((0.9, "yes"), (1.1, "no")):
                    twin = projections(*example_outputs())
                    values = twin["coefficients"][channel][path]
                    if field is not None:
                        values = values[field]
                    values["p1"] *= 1 + factor * 1e-8
                    frame = comparison_frame(projections(*example_outputs()), twin)
                    self.assertEqual(parent_agreement(frame), expected)
                    self.assertGreater(frame["max_relative_difference"][channel], 0.0)

        for section, path in (("censored_fit", "C#/onset"), ("verdicts", "D#/cells"),
                              ("soak_retries", "F#/soak_retries")):
            twin = projections(*example_outputs())
            del twin[section][path]
            self.assertEqual(parent_agreement(comparison_frame(projections(*example_outputs()), twin)), "no")

    def test_audit_p01_p02_frame_preserves_coverage_and_valid_cell_keys(self):
        from copy import deepcopy
        from scripts.cadence_interim_twin import comparison_frame, projections

        stage1, coefficients, fit, step3 = example_outputs()
        fit["channels"]["gpu_rail"]["trace_coverage"]["min"] = 1.5
        step3["cells"].append({"prompt_tokens": 4, "status": "not_run", "gamma_estimable": None})
        primary = projections(stage1, coefficients, fit, step3)
        frame = comparison_frame(primary, deepcopy(primary))
        overlap = frame["trace_coverage"]["gpu_rail"]
        for side in ("primary", "twin"):
            self.assertEqual(overlap[side]["F#/channels/gpu_rail/trace_coverage"]["min"], 1.5)
        self.assertEqual(parent_agreement(frame), "yes")

        twin_step3 = {**step3, "cells": step3["cells"][:1]}
        frame = comparison_frame(primary, projections(stage1, coefficients, fit, twin_step3))
        self.assertEqual(set(frame["verdicts"]["primary"]["D#/cells"]), {"2", "4"})
        self.assertEqual(set(frame["verdicts"]["twin"]["D#/cells"]), {"2"})
        self.assertEqual(parent_agreement(frame), "no")

    def test_isolated_child_private_capture_and_closed_failure(self):
        launcher = """
import importlib.util, os, pathlib, runpy, sys, warnings
run_child = runpy.run_path(sys.argv[1])["run_child"]
root = pathlib.Path(sys.argv[2])
def evaluate():
    assert sys.flags.isolated
    spec = importlib.util.spec_from_file_location("synthetic_import", root / "synthetic_import.py")
    spec.loader.exec_module(importlib.util.module_from_spec(spec))
    value = (root / "synthetic-input").read_text()
    print(value, flush=True)
    sys.stderr.write(value)
    os.write(1, value.encode())
    os.write(2, value.encode())
    warnings.warn(value)
    if sys.argv[3] == "error":
        raise RuntimeError(value)
    if sys.argv[3] == "spoof":
        raise type("Leak_987654", (Exception,), {"__module__": "builtins"})(value)
    return {"canary": float(value)}
run_child(evaluate)
"""
        for case, expected_error in (("ok", None), ("missing", b"FileNotFoundError"),
                                     ("error", b"RuntimeError"), ("spoof", b"OtherError")):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                private = root / "fixture-output"
                private.mkdir()
                (root / "synthetic_import.py").write_text("# Detect import cache writes.\n")
                if case != "missing":
                    (root / "synthetic-input").write_text("987654.321")
                original = set(root.iterdir())
                stdout, stderr = private / "stdout", private / "stderr"
                with stdout.open("wb") as out, stderr.open("wb") as err:
                    process = subprocess.run([sys.executable, "-I", "-c", launcher, str(SCRIPT), tmp, case],
                                             stdout=out, stderr=err, check=False)
                self.assertEqual(set(root.iterdir()), original)
                self.assertEqual(set(private.iterdir()), {stdout, stderr})
                if expected_error is None:
                    self.assertEqual(process.returncode, 0)
                    self.assertEqual(stdout.read_bytes(), b'{"canary":987654.321}\n')
                    self.assertEqual(stderr.read_bytes(), b"")
                else:
                    self.assertEqual(process.returncode, 1)
                    self.assertEqual(stdout.read_bytes(), b"")
                    self.assertEqual(stderr.read_bytes(), b"stage2_error\n" + expected_error + b"\n")
                # A parent projects its public agreement decision in the outer stream.
                public = json.dumps({"twin_agrees": "yes" if process.returncode == 0 else "not_evaluable"}).encode()
                errors_without_fixed_line = stderr.read_bytes().removeprefix(b"stage2_error\n")
                self.assertIsNone(re.search(rb"[0-9]", public + errors_without_fixed_line))


@unittest.skipUnless(HAS_NUMPY, "NumPy is required for the fit")
class FitTests(unittest.TestCase):
    def test_interim_fit_uses_only_full_decode_blocks(self):
        from scripts.cadence_interim_twin import FitLeg, fit_channels, predict

        legs = [FitLeg(day, prompt, (), 0.0, 2.0, 4095, 55.0)
                for day, prompt in (("a", 2), ("b", 4), ("c", 8))]
        columns = ("p1", "p2", "a0", "a1", "a2")
        counts = [(255, 128), *((256, k * 256 + 127.5) for k in range(1, 15))]
        observations = [[2 * leg.prompt_tokens + 3 * leg.prompt_tokens**2] + [
            n * (4 + 5 * (leg.prompt_tokens + c) + 6 * leg.prompt_tokens) for n, c in counts
        ] for leg in legs]
        self.assertEqual(len(observations[0]), 16)
        responses = {channel: observations for channel in ("gpu_rail", "dc_in")}
        fitted = fit_channels(legs, (2.0, 256.0), (), responses, None)
        for coefficients in fitted.values():
            self.assertEqual(set(coefficients), set(columns))
            for name, truth in zip(columns, (2, 3, 4, 5, 6), strict=True):
                self.assertAlmostEqual(coefficients[name], truth, places=8)
            _, predictions = predict(legs[0], (2.0, 256.0), (), coefficients)
            self.assertEqual(len(predictions), 16)
            _, with_tail = predict(legs[0], (2.0, 256.0), (), coefficients, include_prefix_tail=True)
            self.assertEqual(len(with_tail), 17)

    def test_no_main_delta_disables_individually_estimable_folds(self):
        from scripts.cadence_interim_twin import OnsetRow, fit_onset, fit_projection

        # Nine observed onsets are too few for B-3, but every fold independently
        # meets B-4 and has a finite optimum in each cell.
        days = ["a", "b", "c"]
        roster, records, responses = [], [], []
        for shift, day in enumerate(days):
            for prompt, time in ((2, 10), (2, 11), (4, 14)):
                elapsed = time + shift
                roster.append(OnsetRow(day, prompt, (), float(prompt), elapsed, True))
                records.append({"day": day, "cell_prompt_tokens": prompt, "prefill_tokens": prompt,
                    "decode_tokens": 512, "start": {"state": "in_state"}, "state": {
                        "onset_use": "uncensored", "first_off_s": elapsed,
                    }, "segments": [{"wall_start_s": i * 10, "wall_end_s": (i + 1) * 10, "hot": False}
                                    for i in range(3)]})
                values = [2 * prompt + 3 * prompt**2, 255 * (4 + 5 * (prompt + 128) + 6 * prompt),
                          256 * (4 + 5 * (prompt + 383.5) + 6 * prompt)]
                responses.append({channel: {"segments": values, "coverage_min": 1.0}
                                  for channel in ("gpu_rail", "dc_in")})
        self.assertIsNone(fit_onset(roster))
        self.assertTrue(all(fit_onset(roster, held_out_day=day) is not None for day in days))
        fit = fit_projection(records, (), {}, (1.0, 10.0), days, responses)
        self.assertEqual(fit["onset"]["folds"], dict.fromkeys(days))
        for channel in fit["channels"].values():
            self.assertEqual(channel["lodo"]["folds_delta_dropped"], [])
            self.assertTrue(all("delta" not in values for values in channel["fold_coefficients"].values()))

    def test_hand_derived_rows_full_fit_and_prediction(self):
        from scripts.cadence_interim_twin import (
            FitLeg, design_rows, fit_channels, predict, token_rates,
        )

        legs = [
            FitLeg(day, prompt, (z,), 1, 1 + prompt / 2, 513,
                   1 + prompt / 2 + 512 / 256)
            for day, prompt, z in (("a", 2, -1), ("b", 4, 1), ("c", 8, 2))
        ]
        rates = token_rates(legs)
        self.assertEqual(rates, (2.0, 256.0))
        # The first leg has prefill [0,1], followed by token intervals
        # 0–255, 255–511, then a one-gap tail. Context begins at P + 128.
        names, rows = design_rows(legs[0], rates, ("k_tf08",), include_prefix_tail=True)
        self.assertEqual(names, ("p1", "p2", "a0", "a1", "a2", "k_tf08"))
        self.assertEqual(rows[0], (2, 4, 0, 0, 0, -0.5))
        self.assertEqual(rows[1], (0, 0, 255, 255 * 130, 510, -(511**2 - 256**2) / (2 * 256**2)))
        self.assertEqual(rows[2][2:5], (256, 256 * 385.5, 512))
        self.assertEqual(rows[3][2:5], (1, 514, 2))

        # Independent planted measurements. Use a distinct exact vector on each channel.
        measurements = {}
        truth = {}
        for channel, factor in (("gpu_rail", 1), ("dc_in", 3)):
            coefficients = [factor * v for v in (2, 5, 11, 17, 23, -31)]
            truth[channel] = coefficients
            p1, p2, a0, a1, a2, k = coefficients
            measured = []
            for leg in legs:
                prompt, (z,) = leg.prompt_tokens, leg.readings
                t = prompt / 2
                segments = [p1 * prompt + p2 * prompt**2 + k * z * t**2 / 2]
                for lo, hi, n, offset in ((0, 255, 255, 128), (255, 511, 256, 383.5)):
                    ramp = ((t + hi / 256)**2 - (t + lo / 256)**2) / 2
                    segments.append(n * (a0 + a1 * (prompt + offset) + a2 * prompt) + k * z * ramp)
                measured.append(segments)
            measurements[channel] = measured

        full = fit_channels(legs, rates, ("k_tf08",), measurements, None)
        contaminated = {channel: [*values[:2], [3 * v for v in values[2]]]
                        for channel, values in measurements.items()}
        fold = fit_channels(legs, rates, ("k_tf08",), contaminated, None, exclude_day="c")
        for fitted in (full, fold):
            for channel, coefficients in truth.items():
                for name, coefficient in zip(names, coefficients):
                    self.assertTrue(math.isclose(fitted[channel][name], coefficient, rel_tol=1e-8), name)
                heat, predictions = predict(legs[0], rates, ("k_tf08",), fitted[channel])
                self.assertAlmostEqual(heat, -0.5 * (1 + 511 / 256)**2 * coefficients[-1])
                for prediction, energy in zip(predictions, measurements[channel][0], strict=True):
                    self.assertTrue(math.isclose(prediction, energy, rel_tol=1e-8))
                full_heat, _ = predict(legs[0], rates, ("k_tf08",), fitted[channel], include_prefix_tail=True)
                self.assertAlmostEqual(full_heat, -4.5 * coefficients[-1])

    def test_right_censored_normal_with_analytic_optimum(self):
        from scripts.cadence_interim_twin import censored_normal

        # At mu == censor time, the tail score is sqrt(2/pi)/sigma.
        # Place two observed values with sum -sqrt(2/pi) and squared sum 2
        # relative to mu, so both likelihood scores vanish at sigma == 1.
        offset = -math.sqrt(2 / math.pi)
        gap = math.sqrt(4 - offset**2)
        for scale in (1, 37):
            origin = 4 * scale
            ends = [origin + scale * (offset + gap) / 2,
                    origin + scale * (offset - gap) / 2, origin]
            fit = censored_normal([[1], [1], [1]], ends, [True, True, False])
            self.assertTrue(math.isclose(fit.coefficients[0], origin, rel_tol=1e-6))
            self.assertTrue(math.isclose(fit.sigma_s, scale, rel_tol=1e-6))

    def test_expected_hot_seconds(self):
        from scripts.cadence_interim_twin import expected_hot_seconds

        # Symmetry around the mean gives half the interval, for any sigma.
        self.assertAlmostEqual(expected_hot_seconds(2, 8, 5, 1.25), 3)
        self.assertEqual(expected_hot_seconds(2, 8, 5, 1e-7), 3)
        self.assertAlmostEqual(expected_hot_seconds(0, 2, -1, 1), 1.9170666837293613, places=12)

    def test_onset_gate_counts_uncensored_by_day_and_cell(self):
        from scripts.cadence_interim_twin import OnsetRow, fit_onset

        rows = [OnsetRow(day, str(cell), (), cell, 4 + 2 * cell + noise, True)
                for day in ("a", "b", "c") for cell in (1, 2) for noise in (-1, 1)]
        fit = fit_onset(rows)
        self.assertAlmostEqual(fit.coefficients[0], 4)
        self.assertAlmostEqual(fit.coefficients[1], 2)
        two_days = [r for r in rows if r.day != "a"]
        self.assertIsNone(fit_onset(two_days))
        self.assertAlmostEqual(fit_onset(rows, held_out_day="a").sigma_s, 1)
        one_cell = [OnsetRow(r.day, "1", r.readings, r.prefill_s, r.end_s, r.observed) for r in rows]
        self.assertIsNone(fit_onset(one_cell))
        self.assertIsNone(fit_onset(one_cell, held_out_day="a"))

    def test_no_main_delta_is_not_reported_as_a_fold_drop(self):
        from unittest.mock import patch
        from scripts.cadence_interim_twin import OnsetFit, fit_projection

        days = [f"2026-01-0{day}" for day in range(1, 6)]
        records, responses = [], []
        for day_index, day in enumerate(days):
            for prompt in (2, 2, 2, 4):
                records.append({"day": day, "cell_prompt_tokens": prompt, "prefill_tokens": prompt,
                    "decode_tokens": 512, "start": {"state": "in_state"}, "state": {
                        "onset_use": "uncensored" if prompt == 2 else "censored",
                        "first_off_s": 10 + day_index, "censored_at_s": 30,
                    }, "segments": [{"wall_start_s": i * 10, "wall_end_s": (i + 1) * 10, "hot": False}
                                    for i in range(3)]})
                values = [2 * prompt + 3 * prompt**2, 255 * (4 + 5 * (prompt + 128) + 6 * prompt),
                          256 * (4 + 5 * (prompt + 383.5) + 6 * prompt)]
                responses.append({channel: {"segments": values, "coverage_min": 1.0}
                                  for channel in ("gpu_rail", "dc_in")})
        fit = fit_projection(records, (), {}, (1.0, 10.0), days, responses)
        self.assertEqual(fit["delta_column"], "dropped_onset_not_estimable")
        for channel in fit["channels"].values():
            self.assertEqual(channel["lodo"]["folds_delta_dropped"], [])
            self.assertEqual(set(channel["fold_coefficients"]), set(days))

        kept = OnsetFit((12.0, 0.15), 2.0)
        with patch("scripts.cadence_interim_twin.fit_onset",
                   side_effect=lambda rows, held_out_day=None, **kw: None if held_out_day == days[2] else kept):
            fit = fit_projection(records, (), {}, (1.0, 10.0), days, responses)
        for channel in fit["channels"].values():
            self.assertEqual(channel["lodo"]["folds_delta_dropped"], [days[2]])
            self.assertIn("delta", channel["fold_coefficients"][days[0]])
            self.assertNotIn("delta", channel["fold_coefficients"][days[2]])

    def test_census_t01_t02_marked_onset_mask_and_required_refit(self):
        from scripts.cadence_interim_twin import READINGS, fit_leg, fit_onset, onset_roster, recompute_fit

        def run(days, prompts, keep):
            records, responses = [], []
            for day in days:
                for i, prompt in enumerate(prompts):
                    records.append({"day": day, "span_id": f"{day}/{i}", "cell_prompt_tokens": prompt,
                        "prefill_tokens": prompt, "decode_tokens": 512, "start": {"state": "in_state"},
                        "state": {"onset_use": "uncensored", "first_off_s": 6 + day + i + prompt},
                        "segments": [{"wall_start_s": j * 10, "wall_end_s": (j + 1) * 10, "hot": j == 2}
                                     for j in range(3)]})
                    values = [2 * prompt + 3 * prompt**2, 255 * (4 + 5 * (prompt + 128) + 6 * prompt),
                              256 * (4 + 5 * (prompt + 383.5) + 6 * prompt) + day]
                    responses.append({channel: {"segments": values, "coverage_min": 1.0}
                                      for channel in ("gpu_rail", "dc_in")})
            stage1 = {"active_readings": {name: {"active": False} for name in READINGS},
                      "rates": {"r_p": 1.0, "r_d": 10.0}, "centring": {}, "roster": {"fit_days": days}}
            reduced = [row for row in records if keep(row)]
            onset = fit_onset(onset_roster(reduced, [fit_leg(row, (), {}) for row in reduced], (1.0, 10.0)),
                              sensitivity=True)
            return onset, recompute_fit(stage1, records, responses, {r["span_id"] for r in records if not keep(r)})

        # Primary census outcomes for few_hot_days and reduced_gate.
        onset, fit = run([1, 2, 3], (2, 2, 4), lambda row: row["day"] < 3)
        self.assertIsNotNone(onset)
        self.assertEqual(fit["delta_column"], "dropped_onset_not_estimable")
        for channel in fit["channels"].values():
            reduced = channel["marked_sensitivity"]["fit_without"]
            self.assertEqual(reduced["columns"], ["p1", "p2", "a0", "a1", "a2"])
            self.assertEqual(reduced["lodo"]["folds_delta_dropped"], [])
            self.assertTrue(all("delta" not in row for row in reduced["fold_coefficients"].values()))

        onset, fit = run([1, 2, 3, 4, 5], (2, 4, 2, 4),
                         lambda row: row["day"] < 3 and row["span_id"].endswith(("/0", "/1")))
        self.assertIsNone(onset)
        self.assertEqual(fit["delta_column"], "kept")
        for channel in fit["channels"].values():
            self.assertEqual(channel["marked_sensitivity"], {"coefficients_without": None, "fit_without": None})

        onset, fit = run([1, 2, 3, 4, 5], (2, 4, 2, 4), lambda row: row["day"] < 3)
        self.assertIsNotNone(onset)
        for channel in fit["channels"].values():
            reduced = channel["marked_sensitivity"]["fit_without"]
            self.assertIn("delta", reduced["coefficients"])
            self.assertEqual(reduced["lodo"]["folds_delta_dropped"], [1, 2])

    def test_census_t16_refuses_each_registered_denominator(self):
        from scripts.cadence_interim_twin import FitUnavailable, fit_projection

        def fit(values, onset_use):
            records, responses = [], []
            for day in ("a", "b", "c"):
                for prompt in (2, 4):
                    records.append({"day": day, "cell_prompt_tokens": prompt, "prefill_tokens": prompt,
                                    "decode_tokens": 768, "start": {"state": "in_state"},
                                    "state": {"onset_use": onset_use, "first_off_s": 20},
                                    "segments": [{"wall_start_s": i * 10, "wall_end_s": (i + 1) * 10,
                                                  "hot": i >= 2} for i in range(4)]})
                    responses.append({c: {"segments": [10, 10, 10, 10], "coverage_min": 1.0}
                                      for c in ("gpu_rail", "dc_in")})
            responses[0]["gpu_rail"]["segments"] = values
            return fit_projection(records, (), {}, (1, 10), ["a", "b", "c"], responses)

        for values, reason in (([0, 0, 0, 0], "leg total"), ([10, 10, 0, 0], "hot total"),
                               ([10, 0, 10, 10], "onset-profile block")):
            with self.subTest(reason=reason), self.assertRaisesRegex(FitUnavailable, reason):
                fit(values, "uncensored")
        # The P-3 pre-hot offset is applicable only for an observed onset.
        self.assertIn("channels", fit([10, 0, 10, 10], "left_out_state_unobserved"))
        self.assertIn("channels", fit([0, 10, 10, 10], "uncensored"))


class DiagnosticsTests(unittest.TestCase):
    def test_rl184_f08_unrounded_inclusive_hot_cutoff_and_exact_words(self):
        from copy import deepcopy
        from scripts.cadence_interim_twin import comparison_frame, interim_verdict, projections

        for predicted, expected in ((math.nextafter(49.0, -math.inf), "passes"),
                                    (49.0, "passes"), (math.nextafter(49.0, math.inf), "fails")):
            with self.subTest(predicted=predicted):
                self.assertEqual(interim_verdict(dict.fromkeys("abc", [(predicted, 48), (1, 1), (1, 1)])), expected)
        baseline = projections(*example_outputs())
        changed = deepcopy(baseline)
        word = next(key for key in changed["verdicts"] if key.endswith("/lodo/hot/verdict"))
        changed["verdicts"][word] = "fails"
        self.assertEqual(parent_agreement(comparison_frame(baseline, changed)), "no")

    def test_hand_derived_trapezoid_and_coverage(self):
        from scripts.cadence_interim_twin import dc_segment, trace_coverage

        # Samples fall on p(t) = 2 + 4t. The integral on [0.25,1.75] is 9.
        self.assertAlmostEqual(dc_segment([0, 1, 2], [2, 6, 10], 0.25, 1.75), 9)
        with self.assertRaises(ValueError):
            dc_segment([0, 3], [2, 14], 0.25, 1.75)
        self.assertEqual(trace_coverage([0.98, 0.99, 1.0]), (0.98, 1))

    def test_day_qualification_uses_sums_and_hot_leg_counts(self):
        from scripts.cadence_interim_twin import interim_verdict

        days = {"a": [(100, 100), (300, 300), (110, 100)],
                "b": [(102, 100)] * 3, "c": [(100, 100)] * 3,
                "d": [(500, 100)] * 2}
        self.assertEqual(interim_verdict(days), "passes")
        days["a"][2] = (111, 100)
        self.assertEqual(interim_verdict(days), "fails")
        del days["c"]
        self.assertEqual(interim_verdict(days), "not_evaluable")


class ReaderTests(unittest.TestCase):
    def test_rl184_f01_admits_only_literal_relative_posix_paths(self):
        from scripts.cadence_interim_twin import inventory_path, span_identities

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            span = root / "staged-span"
            runtime = span / "legs/a/runtime"
            (span / "runner_receipt.json").parent.mkdir()
            (span / "runner_receipt.json").write_text('{"roster":["a"],"steps":[]}')
            record = runtime.parent / "leg_record.json"
            for spelling in ("leaf", "runs/cadence-leg"):
                with self.subTest(spelling=spelling):
                    bundle = runtime / spelling
                    (bundle / "raw").mkdir(parents=True)
                    for name in ("events.jsonl", "rich_telemetry.jsonl", "raw/powermetrics.plist"):
                        (bundle / name).touch()
                    record.write_text(json.dumps({"result": {"bundle": spelling}}))
                    _, bundles, operations, native = span_identities(span)
                    expected = f"legs/a/runtime/{spelling}"
                    self.assertEqual(bundles, {"a": expected})
                    self.assertIn(f"{expected}/events.jsonl", operations)
                    self.assertEqual(set(native), {expected})
                    self.assertEqual(inventory_path(root, {"s": span}, Path(f"s/{expected}/events.jsonl")),
                                     bundle / "events.jsonl")
            record.write_text('{"result":{"bundle":null}}')
            self.assertEqual(span_identities(span)[1], {})
            for spelling in ("./runs/./cadence-leg", "runs//cadence-leg", "runs/cadence-leg/", "",
                             "runs/../runs/cadence-leg", str(bundle), ".", "contains\0null", False):
                with self.subTest(spelling=spelling), self.assertRaisesRegex(ValueError, "runtime bundle path"):
                    record.write_text(json.dumps({"result": {"bundle": spelling}}))
                    span_identities(span)

    def test_inventory_uses_the_selected_span_for_logical_paths(self):
        from scripts.cadence_interim_twin import check_custody_inventory, digest, span_dirs

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            root, staged = base / "input", base / "staged"
            root.mkdir()
            staged.mkdir()
            selected = staged / "sample"
            selected.write_bytes(b"synthetic")
            dirs = span_dirs(root, [f"s1={staged}"], ["s1"])
            sha256 = digest(b"synthetic")
            for alias in ("s1/sample", str(root / "s1/sample"), str(selected)):
                inventory = {"files": [{"path": alias, "sha256": sha256}]}
                self.assertEqual(check_custody_inventory(root, dirs, inventory), {selected: sha256})
            (root / "s1").mkdir()
            (root / "s1/sample").write_bytes(b"stale synthetic copy")
            logical = {"files": [{"path": "s1/sample", "sha256": sha256}]}
            self.assertEqual(check_custody_inventory(root, dirs, logical), {selected: sha256})
            (staged / "escape").symlink_to(root / "s1/sample")
            for outside in ("s1/escape", "s1/../input/s1/sample", "other/sample"):
                invalid = {"files": [{"path": outside, "sha256": sha256}]}
                with self.subTest(outside=outside), self.assertRaises(ValueError):
                    check_custody_inventory(root, dirs, invalid)

            # An absolute path may already name a selected override, even
            # when that directory lies below a different logical span key.
            nested = root / "s1/staged-s2"
            nested.mkdir()
            (nested / "sample").write_bytes(b"synthetic")
            two_spans = {**dirs, "s2": nested}
            physical = {"files": [{"path": str(nested / "sample"), "sha256": sha256}]}
            self.assertEqual(check_custody_inventory(root, two_spans, physical), {nested / "sample": sha256})

    def test_span_override_and_runtime_bundle_containment(self):
        from scripts.cadence_interim_twin import span_dirs, span_identities

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "a").mkdir()
            override = root / "alternate"
            runtime = override / "legs" / "sample" / "runtime"
            (runtime / "runs/cadence-leg").mkdir(parents=True)
            record = runtime.parent / "leg_record.json"
            record.write_text('{"result":{"bundle":"runs/cadence-leg"}}')
            (override / "runner_receipt.json").write_text('{"roster":["sample"]}')
            directories = span_dirs(root, [f"b={override}"], {"a", "b"})
            self.assertEqual(directories, {"a": root / "a", "b": override})
            self.assertEqual(span_identities(directories["b"])[1], {"sample": "legs/sample/runtime/runs/cadence-leg"})
            (runtime / "runs/escape").symlink_to(runtime.parent)
            for outside in ("../../..", "runs/../../sample", "runs/escape", str(override)):
                record.write_text(json.dumps({"result": {"bundle": outside}}))
                with self.subTest(outside=outside), self.assertRaises(ValueError):
                    span_identities(directories["b"])

    def test_gpu_overlap_counts_every_row_in_trace_energy_and_coverage(self):
        from scripts.cadence_interim_twin import power_intervals, trace_coverage

        # The registered Trace applies both rows to the shared second.
        rows = [(0.0, 2.0, 2.0, 2.0), (1.0, 3.0, 3.0, 5.0)]
        self.assertEqual(power_intervals(rows, 0.0, 3.0), (14.0, 4 / 3))
        self.assertEqual(power_intervals(rows, 0.5, 2.5), (10.5, 1.5))
        self.assertEqual(trace_coverage([4 / 3, 1.5]), (4 / 3, 0))
        # The nested row contributes energy without moving the right edge back.
        nested = [(0.0, 4.0, 4.0, 2.0), (0.5, 1.0, 1.0, 6.0)]
        self.assertEqual(power_intervals(nested, 0.0, 4.0), (11.0, 1.125))

    def test_gpu_backstop_checks_connected_response_intervals(self):
        from scripts.cadence_interim_twin import responses_for_leg

        rows = [(0.0, 0.5, 0.5, 1.0), (3.5, 4.0, 4.0, 1.0)]

        def segment(start, end):
            return {"wall_start_s": start, "wall_end_s": end}

        def dc(start, end):
            return end - start, 1.0

        with self.assertRaisesRegex(ValueError, "GPU trace hole"):
            responses_for_leg({"segments": [segment(0, 2), segment(2, 4)], "prefix_tails": []}, rows, dc)
        with self.assertRaisesRegex(ValueError, "GPU trace hole"):
            responses_for_leg({"segments": [segment(0, 1.8), segment(2.2, 4)],
                               "prefix_tails": [{**segment(1, 2.5), "prefix_len": 12}]}, rows, dc)
        fit = responses_for_leg({"segments": [segment(0, 0.5), segment(3.5, 4)], "prefix_tails": []}, rows, dc)
        self.assertEqual(fit["gpu_rail"]["segments"], [0.5, 0.5])

    def test_census_t03_empty_prefix_within_a_permitted_fit_gap(self):
        from scripts.cadence_interim_twin import power_intervals, responses_for_leg

        gpu = [(0, 2, 2, 2), (3, 4, 4, 4)]
        record = {"segments": [{"wall_start_s": 0, "wall_end_s": 4}],
                  "prefix_tails": [{"wall_start_s": 2, "wall_end_s": 3, "prefix_len": 3724}]}
        response = responses_for_leg(record, gpu, lambda lo, hi: (hi - lo, 1.0))["gpu_rail"]
        self.assertEqual(response, {"segments": [8.0], "prefix_tails": {"3724": 0.0}, "coverage_min": 0.75})
        self.assertEqual(power_intervals(gpu, 2, 3), (0.0, 0.0))
        self.assertEqual(power_intervals(gpu, 2, 2), (0.0, None))

    def test_meter_decoder_import_boundary(self):
        from scripts.cadence_interim_twin import meter_decoder

        for attempted in (b"import joulewise.aggregate", b"from joulewise.desk_compress import write_bytes",
                          b"from joulewise.aggregate import student_t_critical_95, mean", b"import other_package"):
            with self.subTest(attempted=attempted), self.assertRaises(ImportError):
                meter_decoder((SCRIPT, attempted + b"\n"), ())

    def test_meter_shim_reads_only_the_active_verified_stream(self):
        from scripts.cadence_interim_twin import MeterInput, digest, meter_decoder

        data = b"synthetic stream bytes\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            first, second = root / "stream-first.jsonl", root / "stream-second.jsonl"
            for path in (first, second):
                path.write_bytes(data)
            streams = tuple(MeterInput(path, path, digest(data)) for path in (first, second))
            source = b"""
from joulewise.desk_compress import read_bytes
def parse(path):
    if path.name == 'stream-first.jsonl':
        return read_bytes(path.with_name('stream-second.jsonl'))
    return read_bytes(path)
"""
            parse = meter_decoder((SCRIPT, source), streams)
            self.assertEqual(parse(second), data)
            with self.assertRaises(PermissionError):
                parse(first)
            with self.assertRaises(PermissionError):
                parse(root / "unlisted.jsonl")
            self.assertEqual(parse(second), data)
            second.with_name(second.name + ".zst").write_bytes(data)
            with self.assertRaises(ValueError):
                parse(second)
            second.with_name(second.name + ".zst").unlink()
            second.write_bytes(data + b"changed")
            with self.assertRaises(ValueError):
                parse(second)

    def test_meter_shim_refuses_t_diagnostic(self):
        from scripts.cadence_interim_twin import MeterInput, digest, meter_decoder

        source = b"""
from joulewise.aggregate import student_t_critical_95
def parse(path):
    return student_t_critical_95(10)
"""
        with tempfile.TemporaryDirectory() as tmp:
            stream = Path(tmp).resolve() / "stream.jsonl"
            stream.write_bytes(b"synthetic stream\n")
            parse = meter_decoder((SCRIPT, source), (MeterInput(stream, stream, digest(stream.read_bytes())),))
            with self.assertRaises(RuntimeError):
                parse(stream)

    def test_gpu_rows_and_raw_meter_time_identities(self):
        import struct
        from scripts.cadence_interim_twin import (
            digest, gpu_rows, gpu_time_digest, meter_time_digest, power_intervals, require_gpu_gap_bound,
        )

        raw = (b"source,rail,interval_start_s,interval_end_s,timestamp_s,power_w\n"
               b"powermetrics,gpu_power,0,1,1,3\n"
               b"powermetrics,cpu_power,0,2,2,99\n"
               b"powermetrics,gpu_power,1,2,2,7\n")
        gpu = gpu_rows(raw)
        self.assertEqual(power_intervals(gpu, 0.5, 1.25), (3.25, 1.0))
        self.assertEqual(power_intervals(gpu, 0.5, 2.5), (8.5, 0.75))
        with self.assertRaises(ValueError):
            require_gpu_gap_bound(gpu, 0.5, 4.1)

        self.assertEqual(gpu_time_digest(raw), digest(b"[[0.0, 1.0], [1.0, 2.0]]"))
        payload = struct.pack("<HHiiHHHH", 22, 0, 20_000_000, -250_000, 0, 0, 0, 0)
        rows = [{"k": "h", "sps": 100, "unknown": 23}, {"k": "b", "n": 1, "p": payload.hex()},
                {"k": "b", "tx": 1, "rx": 2, "rt": 3, "n": 0}, {"k": "t"}]
        stream = b"\n".join(json.dumps(row).encode() for row in rows)
        expected = (b'["stream-a.jsonl", {"k": "h", "sps": 100}, {"k": "t"}, 1]'
                    b'[null, null, null, 1, [22]][1, 2, 3, 0, []]')
        self.assertEqual(meter_time_digest([("stream-a.jsonl", stream + b"\nnot JSON\npartial")]),
                         digest(expected))
        changed_power = struct.pack("<HHiiHHHH", 22, 0, 7, 8, 9, 10, 11, 12)
        changed = stream.replace(payload.hex().encode(), changed_power.hex().encode())
        self.assertEqual(meter_time_digest([("stream-a.jsonl", stream)]),
                         meter_time_digest([("stream-a.jsonl", changed)]))

    def test_meter_ties_and_span_wide_period(self):
        from types import SimpleNamespace
        from scripts.cadence_interim_twin import pooled_meter, sample_coverage

        def make(samples, idx):
            return SimpleNamespace(present=True, aligned=True, header={
                "rate_idx": idx, "start_real_ns": 0, "start_raw_ns": 0,
            }, host_ns=[round(t * 1e9) for t, _ in samples], watts=[w for _, w in samples])

        streams = {"a": make([(0.0, 1), (1.0, 3)], 1),
                   "b": make([(1.0, 7), (2.0, 9)], 1),
                   "c": make([(4.5, 0), (5.0, 0)], 0)}
        measure = pooled_meter(sorted(streams), streams.__getitem__)
        self.assertEqual(measure(0, 2), (10.0, 0.5))
        self.assertEqual(measure(0, 1), (2.0, 0.5))
        self.assertEqual(measure(1, 2), (8.0, 0.5))
        self.assertEqual(sample_coverage((-0.125, 0.375, 1.125), 0.5, 0, 1), 0.75)
        with self.assertRaises(ValueError):
            measure(2, 4.5)

    def test_native_digest_preserves_spelling_and_paired_prefix(self):
        from scripts.cadence_interim_twin import digest, native_time_digest

        rich = b'{"elapsed_ns":10,"timestamp_s":1.00}\n{"timestamp_s" :2}\n'
        native = (b'<key>elapsed_ns</key><integer>10</integer><key>thermal_pressure</key><string>N</string>'
                  b'\0<key>thermal_pressure</key><string>&amp;</string>\0extra')
        expected = b'[[["1.00","10"],[null,null]],[["10","4e"],[null,"26616d703b"]],3]'
        self.assertEqual(native_time_digest(rich, native), digest(expected))

    def test_soak_retries_read_legacy_and_current_receipts(self):
        from scripts.cadence_interim_twin import soak_summary

        receipts = {"a": {"steps": [{"name": "soak", "rc": 0}]}, "b": {
            "steps": [soak_refused_step(1, "refused"), {"name": "soak.a2-blackout-wait", "rc": 0},
                      {"name": "soak.a2", "rc": 0}],
            "soak_attempts": [soak_attempt(1, "refused", "soak.rejected1"), soak_attempt(2)],
        }, "c": {"steps": [soak_refused_step(1, "refused"), soak_refused_step(2, "refused")],
                   "soak_attempts": [soak_attempt(1, "refused"), soak_attempt(2, "refused")]}}
        summary = soak_summary(receipts)
        self.assertEqual(summary["spans"]["a"], {"attempts": 1, "field_present": False,
                                                "accepted": True, "retried": []})
        self.assertEqual(summary["spans"]["b"]["retried"], [
            {"attempt": 1, "kind": "kind not recorded", "read_from": None},
        ])
        self.assertEqual(summary["spans"]["c"]["retried"], [
            {"attempt": 1, "kind": "kind not recorded", "read_from": None},
        ])
        self.assertEqual(summary["spans_with_retry"], 2)
        self.assertEqual(summary["retried_by_kind"], {"slope": 0, "load": 0, "kind not recorded": 2})
        self.assertEqual(summary["accepted_after_retry"], 1)
        self.assertEqual(summary["stopped_by_soak"], 1)

    def test_rl184_f02_empty_attempts_and_f03_incomplete_soak(self):
        from copy import deepcopy
        from scripts.cadence_interim_twin import soak_summary, span_soak

        empty_receipt = {"soak_attempts": [], "steps": [{"name": "soak-blackout-wait", "rc": 0}]}
        empty = soak_summary({"s": empty_receipt})
        self.assertEqual(empty["spans"]["s"], {"attempts": 0, "field_present": True,
                                               "accepted": False, "retried": []})
        self.assertEqual(empty["stopped_by_soak"], 0)
        with self.assertRaisesRegex(ValueError, "invalid soak attempts"):
            span_soak({**empty_receipt, "soak_attempts": None})
        with self.assertRaisesRegex(ValueError, "invalid soak step order"):
            span_soak({**empty_receipt, "steps": [{"name": "soak", "rc": 0}]})

        base = {"soak_attempts": [soak_attempt(1)], "steps": [{"name": "soak", "rc": 0}]}
        no_rc = deepcopy(base)
        del no_rc["steps"][-1]["rc"]
        self.assertFalse(span_soak(no_rc)["accepted"])
        self.assertFalse(span_soak({**base, "steps": [{"name": "soak", "rc": None}]})["accepted"])
        self.assertFalse(span_soak({**base, "steps": [{"name": "soak", "rc": 130}]})["accepted"])
        interrupted = {"soak_attempts": [soak_attempt(1, "refused", "soak.rejected1")],
                       "steps": [soak_refused_step(1, "refused"), {"name": "soak.a2-blackout-wait", "rc": 130}]}
        self.assertEqual(span_soak(interrupted), {"attempts": 1, "field_present": True,
                                                 "accepted": False, "retried": []})
        del no_rc["soak_attempts"][0]["refused"]
        with self.assertRaisesRegex(ValueError, "soak attempt fields"):
            span_soak(no_rc)
        with self.assertRaises(ValueError):
            span_soak({**base, "soak_refusals": None})

    def test_rl184_f04_f05_refuse_contradictory_history_and_unknown_kinds(self):
        from scripts.cadence_interim_twin import span_soak

        base = {"soak_attempts": [soak_attempt(1, "synthetic"), soak_attempt(2)],
                "steps": [soak_refused_step(1, "synthetic"), {"name": "soak.a2", "rc": 0}]}
        histories = [
            {"soak_attempts": [soak_attempt(1), soak_attempt(2)]},
            {"soak_attempts": [soak_attempt(True, "synthetic"), soak_attempt(2)]},
            {"soak_attempts": [soak_attempt(1, "synthetic"), soak_attempt(2, output_dir="soak.rejected2")]},
            {"soak_attempts": [soak_attempt(1, "synthetic"), soak_attempt(2, "synthetic"), soak_attempt(3)],
             "steps": [soak_refused_step(1, "synthetic"), soak_refused_step(2, "synthetic"),
                       {"name": "soak.a3", "rc": 0}]},
            {"steps": [{"name": "soak", "rc": 0}, {"name": "soak.a2", "rc": 0}]},
            {"steps": [{"name": "soak"}, {"name": "soak.a2", "rc": 0}]},
            {"steps": [{"name": "soak.a2", "rc": 0}]},
            {"steps": list(reversed(base["steps"]))},
            {"steps": [*base["steps"], {"name": "soak.a3", "rc": 0}]},
            {"steps": [None, *base["steps"]]},
            {"steps": [{}, *base["steps"]]},
            {"steps": [{"name": "soak.a2-blackout-wait", "rc": 0}, *base["steps"]]},
            *[{"soak_refusals": [{"attempt": n, "kind": "load"}]} for n in (True, 1.0, 2, 3)],
            {"soak_refusals": [{"attempt": 1, "kind": "load", "extra": 1}]},
        ]
        for overrides in histories:
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                span_soak({**base, **overrides})
        for kind in ("other", "kind not recorded", "load"):
            with self.subTest(legacy_kind=kind), self.assertRaisesRegex(ValueError, "soak attempt fields"):
                attempts = [dict(base["soak_attempts"][0], refusal_kind=kind), soak_attempt(2)]
                span_soak({**base, "soak_attempts": attempts})
        attempt_with_phantom_kind = dict(base["soak_attempts"][0], soak_refusals_kind="load")
        with self.assertRaisesRegex(ValueError, "soak attempt fields"):
            span_soak({**base, "soak_attempts": [attempt_with_phantom_kind, soak_attempt(2)]})
        for structured in ([], [{"attempt": 1, "kind": "load"}]):
            with self.subTest(structured=structured), self.assertRaisesRegex(ValueError, "rostered writers"):
                span_soak({**base, "soak_refusals": structured})

    def test_audit_f03_f04_incomplete_steps_and_fatal_waits(self):
        from scripts.cadence_interim_twin import span_soak

        for step in ({"name": "soak", "rc": None}, {"name": "soak"}, {"name": "soak", "rc": 130}):
            with self.subTest(legacy_step=step):
                self.assertEqual(span_soak({"steps": [step]}), {"attempts": 1, "field_present": False,
                                                                "accepted": False, "retried": []})
        interrupted = {"soak_attempts": [soak_attempt(1)], "steps": []}
        self.assertEqual(span_soak(interrupted), {"attempts": 1, "field_present": True,
                                                 "accepted": False, "retried": []})
        retry_interrupted = {"soak_attempts": [soak_attempt(1, "refused"), soak_attempt(2)],
                             "steps": [soak_refused_step(1, "refused")]}
        self.assertEqual(span_soak(retry_interrupted), {"attempts": 2, "field_present": True,
                         "accepted": False, "retried": [{"attempt": 1, "kind": "kind not recorded",
                                                         "read_from": None}]})
        for wait_rc in (130, None):
            wait = {"name": "soak-blackout-wait", "rc": wait_rc}
            legacy = {"steps": [wait, {"name": "soak", "rc": 0}]}
            retry = {"steps": [soak_refused_step(1, "refused"), {"name": "soak.a2-blackout-wait", "rc": wait_rc},
                               {"name": "soak.a2", "rc": 0}],
                     "soak_attempts": retry_interrupted["soak_attempts"]}
            for receipt in (legacy, {**interrupted, **legacy}, {**interrupted, "steps": [wait]}, retry):
                with self.subTest(receipt=receipt), self.assertRaisesRegex(ValueError, "failed soak wait"):
                    span_soak(receipt)
        with self.assertRaises(ValueError):
            span_soak({**interrupted, "soak_attempts": [soak_attempt(1, "refused")]})

    def test_round_two_f04_only_a_soak_refusal_can_retry(self):
        from scripts.cadence_interim_twin import span_soak

        reason = "idle check refused"
        first, second = soak_attempt(1, reason), soak_attempt(2)
        refused_step = soak_refused_step(1, reason)
        retry_step = {"name": "soak.a2", "rc": 0}
        aborted = {"name": "soak", "rc": 130, "error": "SystemExit: 130"}
        self.assertTrue(span_soak({"soak_attempts": [first, second],
                                  "steps": [refused_step, retry_step]})["accepted"])
        self.assertFalse(span_soak({"soak_attempts": [soak_attempt(1)], "steps": [aborted]})["accepted"])
        for invalid_step in (aborted,
                             dict(refused_step, error="SpanRefusal: unrelated failure"),
                             dict(refused_step, error="SoakRefusal: different reason"),
                             dict(refused_step, rc=5)):
            with self.subTest(step=invalid_step), self.assertRaises(ValueError):
                span_soak({"soak_attempts": [first, second], "steps": [invalid_step, retry_step]})
        with self.assertRaises(ValueError):
            span_soak({"soak_attempts": [first], "steps": [aborted, {"name": "soak.a2-blackout-wait", "rc": 0}]})

    def test_round_three_f04_terminal_refusal_requires_matching_step(self):
        from scripts.cadence_interim_twin import span_soak

        reason = "soak exit 5: the idle soak failed its settle or quiet check"
        aborted = {"name": "soak", "rc": 130, "error": "SystemExit: 130"}
        self.assertFalse(span_soak({"soak_attempts": [soak_attempt(1)], "steps": [aborted]})["accepted"])
        self.assertFalse(span_soak({"soak_attempts": [soak_attempt(1, reason)],
                                    "steps": [soak_refused_step(1, reason)]})["accepted"])
        for step in (aborted, {"name": "soak", "rc": 2},
                     soak_refused_step(1, "different refusal"),
                     dict(soak_refused_step(1, reason), rc=5)):
            with self.subTest(step=step), self.assertRaises(ValueError):
                span_soak({"soak_attempts": [soak_attempt(1, reason)], "steps": [step]})

    def test_step3_fixed_effect_and_tripwire_against_hand_fit(self):
        from scripts.cadence_interim_twin import mean_centered_slope, step3_projection

        # Both blocks have the same log-linear slope and different intercepts.
        legs = [(False, 4, [(block, t, intercept * math.exp(0.02 * t))
                           for block, intercept in ((1, 2), (2, 8))]) for t in (30, 33, 36)]
        self.assertAlmostEqual(mean_centered_slope([rows for _, _, rows in legs]), 0.02)
        cells = {2: (0, legs), 4: (3, legs), 8: (0, legs[:1])}
        expected = [{"prompt_tokens": 2, "status": "ok", "gamma_estimable": True},
                    {"prompt_tokens": 4, "status": "not_run", "gamma_estimable": None},
                    {"prompt_tokens": 8, "status": "ok", "gamma_estimable": False}]
        tripped = step3_projection(cells, 0.04)
        self.assertEqual(tripped["cells"], expected)
        self.assertEqual(tripped["tripwire"], {"decision": "to the research lead", "trips": True})
        self.assertEqual(step3_projection(cells, 0.1)["tripwire"], {"decision": "within", "trips": False})
        self.assertEqual(step3_projection({8: cells[8]}, 0.1)["tripwire"],
                         {"decision": "not_evaluable", "trips": None})

    def test_step3_spread_rounding_sensitivity_and_empty_cells(self):
        from scripts.cadence_interim_twin import step3_projection

        # The full spread rounds to 2.000 C. Dropping the first leg leaves
        # a sub-2 C slope of 0.120048, still eligible in the drift maximum.
        legs = [(False, 1, [(1, t, math.exp(log_energy))])
                for t, log_energy in ((30.0, 0), (31.0, 0), (31.9996, 0.12))]
        result = step3_projection({2: (0, []), 4: (1, []), 8: (0, legs)}, 0.08)
        self.assertEqual(result["cells"], [{"prompt_tokens": 4, "status": "not_run", "gamma_estimable": None},
                                           {"prompt_tokens": 8, "status": "ok", "gamma_estimable": True}])
        self.assertEqual(result["tripwire"], {"decision": "to the research lead", "trips": True})
        empty = step3_projection({2: (0, []), 4: (1, [])}, 0.08)
        self.assertEqual(empty["tripwire"], {"decision": "not_evaluable", "trips": None})




class Step3CutTests(unittest.TestCase):
    def test_round_two_clock_rounding_fires_at_first_eligible_window(self):
        from scripts.cadence_interim_twin import step3_cut

        tokens = [8 + i / 32 for i in range(1281)]
        journal = [(t, t * 10**9, 34, {"os_level": 0, "pm_state": "Nominal", "pm_observed_ns": t * 10**9})
                   for t in range(49)]
        for elapsed, unit in ((1_100_000_000, 1000), (7_000_000_001, 3)):
            with self.subTest(elapsed=elapsed, unit=unit):
                states = [(1000, 7 * unit), (900, 3 * unit)]
                power = [(t, elapsed, None, states) for t in range(1, 49)]
                self.assertEqual(step3_cut(0, tokens, journal, power), 18)

    def test_step3_temperature_at_unsnapped_cut_and_block_mean(self):
        from scripts.cadence_interim_twin import step3_observations

        tokens = [1 + 0.1 * i for i in range(512)] + [56 + i / 128 for i in range(512)]
        # The accepted block ends at 52.1. A reading at 52.5 must still
        # supply the rise to the guarded wall-time cut at 52.8.
        stamps = [*range(55), 52.5, 54.8]
        journal = [(t, round(t * 1e9), 17 if t == 52.5 else 11, {
            "os_level": int(t == 54.8), "pm_state": "Nominal", "pm_observed_ns": round(t * 1e9),
        }) for t in sorted(stamps)]
        power = [(t, 10**9, "Nominal", [(1000, 100)]) for t in range(1, 57)]
        result = step3_observations(0, tokens, journal, power, [(0, 60, 60, 2)])
        self.assertEqual(result[:2], (False, 6))
        self.assertEqual(len(result[2]), 1)
        block, temperature, energy = result[2][0]
        self.assertEqual((block, temperature), (1, 11.0))
        self.assertAlmostEqual(energy, 51.2)

    def test_step3_raw_records_guard_and_clock(self):
        import plistlib
        from scripts.cadence_interim_twin import step3_cut, step3_records

        def lines(rows):
            return b"\n".join(json.dumps(row).encode() for row in rows)

        tokens = list(range(1, 31))
        events = [{"event_type": "token", "metadata": {"index": i, "align_turn_index": 0},
                   "timestamp_s": stamp} for i, stamp in enumerate(tokens)]
        turns = [{"start_stamp": {"epoch_s": 0}, "end_stamp": {"epoch_s": 30},
                  "generation": {"output_token_ids": [1] * len(tokens)}}]
        fresh = [{"kind": "reading", "error": None, "started": {"monotonic_ns": i * 10**9},
                  "finished": {"wall_ns": i * 10**9},
                  "values": {"sensors": {"TV0h": 30}, "status": {
                      "os_level": 0, "pm_state": "Nominal", "pm_observed_ns": i * 10**9,
                  }}} for i in range(31)]
        rich = [{"timestamp_s": i, "elapsed_ns": 10**9, "gpu": {"gpu_energy": 0,
                 "dvfm_states": [{"freq": 1_000 if i <= 11 else 500, "used_ns": 10**9}]}}
                for i in tokens]
        native = b"\0".join(plistlib.dumps({"elapsed_ns": 10**9, "thermal_pressure": "Nominal"}) for _ in tokens)
        start, _, decoded, journal, power = step3_records(lines(events), lines(turns), lines(fresh), lines(rich), native)
        self.assertEqual(decoded, tokens)
        self.assertEqual(step3_cut(start, decoded, journal, power), 11)
        no_pressure = b"\0".join(plistlib.dumps({"elapsed_ns": 10**9}) for _ in tokens)
        _, _, _, journal, pressure_optional = step3_records(
            lines(events), lines(turns), lines(fresh), lines(rich), no_pressure,
        )
        self.assertEqual(len(pressure_optional), len(tokens))
        self.assertEqual(step3_cut(start, decoded, journal, pressure_optional), 11)
        fresh[8]["values"]["status"]["os_level"] = 1
        _, _, _, journal, power = step3_records(lines(events), lines(turns), lines(fresh), lines(rich), native)
        self.assertEqual(step3_cut(start, decoded, journal, power), 6)
        fresh[0]["values"]["status"]["os_level"] = 1
        _, _, _, journal, power = step3_records(lines(events), lines(turns), lines(fresh), lines(rich), native)
        self.assertIsNone(step3_cut(start, decoded, journal, power))


class CensusStep3Tests(unittest.TestCase):
    def measurements(self, directory, leg, case):
        import plistlib
        from scripts.cadence_interim_twin import step3_measurements

        name, option = case
        tokens = [8 + 8 * i / 255 for i in range(256)]
        tokens += [16 + (i + 1) / 32 for i in range(768)] + [48]
        if name == "short":
            tokens = tokens[:512]
        if name == "before_start":
            tokens = [time - 9 for time in tokens]
        if name == "clock_left_boundary":
            tokens[-1] = 80
        if name == "ties":
            tokens[2] = tokens[1]
        events = [{"event_type": "token", "timestamp_s": str(t) if name == "stampstr" else t,
                   "metadata": {"index": str(i) if name == "indexstr" else i, "align_turn_index": 0}}
                  for i, t in enumerate(tokens)]

        def alter(mapping, field):
            if option == "absent":
                mapping.pop(field)
            else:
                mapping[field] = None

        for event in events:
            if name == "index":
                alter(event["metadata"], "align_turn_index")
            if name == "event_type":
                alter(event, "event_type")
            if name == "marker":
                event["metadata"]["align_turn_index"] = 1
        if name == "phase":
            events.insert(0, {"event_type": "phase_start", "timestamp_s": 12, "phase": "align_thermal_hold",
                              "metadata": option})
        if name == "hold_missing_stamp":
            events.append({"event_type": option, "phase": "align_thermal_hold"})
        if name == "hold_nan":
            events.append({"event_type": "phase_start", "phase": "align_thermal_hold", "timestamp_s": "NaN"})
        if name == "token_null_metadata":
            events[0]["metadata"] = None

        turns = [{"start_stamp": {"epoch_s": 0}, "end_stamp": {"epoch_s": 39 if name == "end_early" else 48},
                  "generation": {"output_token_ids": [1] * len(tokens)}}]
        if name == "multi":
            turns *= 2
        if name == "clock_left_boundary":
            turns[0]["start_stamp"]["epoch_s"], turns[0]["end_stamp"]["epoch_s"] = 65, 80
        readings = []
        for t in range(81 if name == "clock_left_boundary" else 49):
            observed = t * 10**9
            if name == "future":
                observed += 10**7
            if name == "guard" and t == 24:
                observed -= 3 * 10**9
            level = (0.0 if name == "start_float" and t == 0 else
                     int((name == "guard" and t >= 26) or (name == "zero_last" and t >= 28)))
            unknown = (name == "unknown_mid" and 9 <= t < 29) or (name == "guard" and t == 25)
            status = {"os_level": level, "pm_state": "Unknown" if unknown else "Nominal", "pm_observed_ns": observed}
            sensors = {"TV0h": 30 + leg * 3 + t / 50}
            values = {"sensors": sensors, "status": status}
            reading = {"kind": "reading", "started": {"monotonic_ns": t * 10**9},
                       "finished": {"wall_ns": t * 10**9}, "values": values}
            if name in ("values", "kind"):
                alter(reading, name)
            if name in ("status", "sensors"):
                alter(values, name)
            if name in status:
                alter(status, name)
            if name == "TV0h":
                alter(sensors, name)
            if name == "missing_freshness_sources":
                status.pop("pm_observed_ns")
                reading.pop("started")
            if name == "started_without_clock":
                reading.pop("started")
            if name == "off_float" and t == 9:
                status["os_level"] = 1.0
            if name == "zero_before_cut" and t == 12:
                status["os_level"] = 1
            if name == "bad_temperature_after_cut":
                if t == 12:
                    status["os_level"] = 1
                if t == 28:
                    sensors["TV0h"] = "bad"
            if name == "all_error":
                reading["error"] = "synthetic"
            readings.append(reading)
        if name in ("freshness_bad_before_start", "freshness_bad_after_turn"):
            stamp = -1 if name == "freshness_bad_before_start" else 49
            reading = dict(readings[-1], finished={"wall_ns": stamp * 10**9}, started={"monotonic_ns": None})
            readings.append(reading)
        if name == "malformed_journal_sensors" and leg == 0:
            last = readings[-1]
            readings.append(dict(last, finished={"wall_ns": last["finished"]["wall_ns"] + 10**12},
                                 values=dict(last["values"], sensors=[5])))

        rich, native = [], []
        if name != "native_empty":
            for t in range(1, 49):
                elapsed = 0 if name == "zero_elapsed" else 10**9
                state = {"freq": 1000, "used_ns": 1000}
                if name in ("clock_overlap", "clock_far_overlap"):
                    if t == 28:
                        state["freq"] = 100
                    if t == 45 and name == "clock_overlap":
                        elapsed, state["used_ns"] = 45 * 10**9, 4_500_000
                if name == "used_ns":
                    alter(state, name)
                gpu = {"dvfm_states": [state]}
                if name == "clock_state_without_use":
                    gpu["dvfm_states"] = [{}]
                if name == "clock_mixed_empty_state" and t == 20:
                    gpu["dvfm_states"].append({})
                if name == "clock_null_state" and leg == 0 and t == 1:
                    gpu["dvfm_states"].append(None)
                if name == "clock_used_string" and t == 20:
                    state["used_ns"] = "1000"
                if name == "clock_left_boundary" and t == 28:
                    state.update(freq=100, used_ns=100000)
                if name == "clock_exact_boundary":
                    elapsed, unit = option or (1_100_000_000, 1000)
                    gpu["dvfm_states"] = [{"freq": 1000, "used_ns": 7 * unit}, {"freq": 900, "used_ns": 3 * unit}]
                if name == "bad_gpu_energy" and t == 20:
                    gpu["gpu_energy"] = "bad"
                if name == "gpu_energy_before_decode" and t == 1:
                    gpu["gpu_energy"] = "bad"
                if name == "gpu_energy_string_in_decode" and t == 20:
                    gpu["gpu_energy"] = "2"
                if name == "native_default_elapsed" and t == 1:
                    elapsed = option
                frame = {"timestamp_s": t, "elapsed_ns": elapsed, "gpu": gpu}
                if name == "rich_elapsed_string" and t == 20:
                    frame["elapsed_ns"] = str(elapsed)
                if name == "rich_elapsed_fraction" and t == 20:
                    frame["elapsed_ns"] += 0.5
                if name == "dvfm_states":
                    alter(gpu, name)
                if name == "gpu":
                    alter(frame, name)
                rich.append(frame)
                raw = {"elapsed_ns": str(elapsed) if name == "native_elapsed" else elapsed}
                if name == "native_default_elapsed" and t == 1:
                    raw.clear()
                if name == "pressure" and (option != "UnregisteredState" or leg == 0):
                    raw["thermal_pressure"] = option
                if name == "pressure_sentinel" and t == 9:
                    raw["thermal_pressure"] = "not_read"
                if name == "pressure_registered_output_key" and t == 45:
                    raw["thermal_pressure"] = option
                native.append(plistlib.dumps(raw))
        if name == "native_truncated" and leg == 0:
            native[19] = b'<?xml version="1.0"?><plist><dict>'
        if name == "native_bad_date" and leg == 0:
            native[7] = native[7].replace(b"</dict>", b"<key>date</key><date>bad</date></dict>", 1)
        if name == "pressure_at_start":
            rich.insert(0, dict(rich[0], timestamp_s=0))
            native.insert(0, plistlib.dumps({"elapsed_ns": 10**9, "thermal_pressure": "UnregisteredState"}))
        if name == "native_count":
            native = native[:len(native) + option] if option < 0 else native + [b"unused suffix"] * option
        if name == "native_outside":
            rich.append(dict(rich[-1], timestamp_s=1000))
            native.append(b"invalid plist outside the load window")
        if name == "pressure_after_turn":
            rich.append(dict(rich[-1], timestamp_s=49))
            native.append(plistlib.dumps({"elapsed_ns": 10**9, "thermal_pressure": "UnregisteredState"}))
        if name in ("clock_far_overlap", "clock_far_reference"):
            frequency = 2000 if name == "clock_far_reference" else 1000
            rich.append({"timestamp_s": 100, "elapsed_ns": 100 * 10**9,
                         "gpu": {"dvfm_states": [{"freq": frequency, "used_ns": 100_000_000}]}})
            native.append(plistlib.dumps({}))
        if name == "gpu_energy_beyond_rich_window":
            stamp = rich[-1]["timestamp_s"] + 120
            elapsed = (stamp - rich[0]["timestamp_s"] + 10) * 10**9
            rich.append({"timestamp_s": stamp, "elapsed_ns": elapsed, "gpu": {"gpu_energy": "bad"}})
            native.append(plistlib.dumps({"elapsed_ns": elapsed}))

        gpu = [(t, t + 8, 2 if t < 32 or name != "zero_last" else 0) for t in range(0, 48, 8)]
        if name == "gap_part":
            gpu[2:3] = [(16, 19, 2), (22, 24, 2)]
        if name == "nonpositive_width":
            gpu.append((*option, 100))
        if name == "zero_before_cut":
            gpu[1] = (10, 16, 2)
        trace = "source,rail,interval_start_s,interval_end_s,timestamp_s,power_w\n"
        trace += "".join(f"powermetrics,gpu_power,{start},{stop},{stop},{power}\n" for start, stop, power in gpu)
        for path, rows in (("events.jsonl", events), ("outputs/align_turns.jsonl", turns),
                           ("outputs/align_thermal.jsonl", readings), ("rich_telemetry.jsonl", rich)):
            target = directory / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("".join(json.dumps(row) + "\n" for row in rows))
            if path == "events.jsonl" and name == "hold_overflow":
                with target.open("ab") as stream:
                    stream.write(b'{"event_type":"phase_start","phase":"align_thermal_hold","timestamp_s":1e309}\n')
        (directory / "raw").mkdir()
        (directory / "raw/powermetrics.plist").write_bytes(b"\0".join(native))
        (directory / "power_trace.csv").write_text(trace)
        return step3_measurements(directory)

    def test_round_one_step3_witnesses(self):
        from scripts.cadence_interim_twin import step3_cells

        within = ("within", False, "ok", True)
        not_run = ("not_evaluable", None, "not_run", None)
        unestimable = ("not_evaluable", None, "ok", False)
        cases = [
            ("T05", "hold_missing_stamp", "phase_start", 3, not_run),
            ("T05", "hold_missing_stamp", "phase_end", 3, not_run),
            ("T05", "token_null_metadata", None, 3, not_run),
            ("T07", "missing_freshness_sources", None, 3, unestimable),
            ("T07", "started_without_clock", None, 3, not_run),
            ("T08", "off_float", None, 3, within),
            ("T09", "TV0h", "absent", 1, not_run),
            ("T10", "clock_state_without_use", None, 3, within),
            ("T11", "native_default_elapsed", -1, 3, within),
            ("T11", "native_default_elapsed", 1, 3, not_run),
            ("T12", "pressure_after_turn", None, 3, within),
            ("T13", "clock_far_overlap", None, 3, unestimable),
            ("T13", "clock_far_reference", None, 3, unestimable),
            ("T14", "bad_gpu_energy", None, 3, not_run),
            ("T14", "zero_before_cut", None, 3, not_run),
        ]
        for clause, name, option, count, expected in cases:
            with self.subTest(clause=clause, case=name, option=option), tempfile.TemporaryDirectory() as tmp:
                entrants = [(2000, lambda i=i: self.measurements(Path(tmp) / str(i), i, (name, option)))
                            for i in range(count)]
                result = step3_cells(entrants, 0.08)
                cell, = result["cells"]
                self.assertEqual((result["tripwire"]["decision"], result["tripwire"]["trips"],
                                  cell["status"], cell["gamma_estimable"]), expected)

    def test_round_two_step3_witnesses(self):
        from scripts.cadence_interim_twin import step3_cells

        within = ("within", False, "ok", True)
        not_run = ("not_evaluable", None, "not_run", None)
        unestimable = ("not_evaluable", None, "ok", False)
        cases = [
            ("T05", "hold_nan", within),
            ("T07", "freshness_bad_after_turn", not_run),
            ("T07", "freshness_bad_before_start", not_run),
            ("T08", "pressure_sentinel", within),
            ("T10", "clock_mixed_empty_state", not_run),
            ("T10", "clock_used_string", not_run),
            ("T11", "native_truncated", within),
            ("T11", "rich_elapsed_string", not_run),
            ("T12", "pressure_at_start", within),
            ("T13", "clock_exact_boundary", unestimable),
            ("T13", "clock_left_boundary", within),
            ("T14", "gpu_energy_before_decode", within),
            ("T14", "gpu_energy_string_in_decode", not_run),
            ("T14", "bad_temperature_after_cut", not_run),
        ]
        for clause, name, expected in cases:
            with self.subTest(clause=clause, case=name), tempfile.TemporaryDirectory() as tmp:
                entrants = [(2000, lambda i=i: self.measurements(Path(tmp) / str(i), i, (name, None)))
                            for i in range(3)]
                result = step3_cells(entrants, 0.08)
                cell, = result["cells"]
                self.assertEqual((result["tripwire"]["decision"], result["tripwire"]["trips"],
                                  cell["status"], cell["gamma_estimable"]), expected)

    def test_round_three_step3_witnesses(self):
        from scripts.cadence_interim_twin import step3_cells

        within = ("within", False, "ok", True)
        unestimable = ("not_evaluable", None, "ok", False)
        cases = [
            ("T05", "hold_overflow", None, within),
            ("T07", "malformed_journal_sensors", None, within),
            ("T10", "clock_null_state", None, within),
            ("T11", "native_bad_date", None, within),
            ("T11", "rich_elapsed_fraction", None, within),
            ("T12", "pressure_registered_output_key", "slope", within),
            ("T13", "clock_exact_boundary", (7_000_000_001, 3), unestimable),
            ("T14", "gpu_energy_beyond_rich_window", None, within),
        ]
        for clause, name, option, expected in cases:
            with self.subTest(clause=clause, case=name, option=option), tempfile.TemporaryDirectory() as tmp:
                entrants = [(2000, lambda i=i: self.measurements(Path(tmp) / str(i), i, (name, option)))
                            for i in range(3)]
                result = step3_cells(entrants, 0.08)
                cell, = result["cells"]
                self.assertEqual((result["tripwire"]["decision"], result["tripwire"]["trips"],
                                  cell["status"], cell["gamma_estimable"]), expected)

    def test_census_t04_through_t15_step3_primary_outcomes(self):
        from scripts.cadence_interim_twin import step3_cells

        # Primary categorical outcomes were recorded by Astra in the synthetic census.
        within = ("within", False, "ok", True)
        not_run = ("not_evaluable", None, "not_run", None)
        unestimable = ("not_evaluable", None, "ok", False)
        cases = [
            ("T04", "nonpositive_width", (1, 1), within),
            ("T04", "nonpositive_width", (2, 1), within),
            ("T05", "index", "absent", within), ("T05", "index", "null", within),
            ("T05", "event_type", "absent", not_run), ("T05", "event_type", "null", not_run),
            ("T05", "marker", None, not_run), ("T05", "multi", None, not_run),
            ("T05", "phase", {"align_turn_index": 0, "index": 0}, within),
            ("T05", "phase", None, within),
            ("T06", "ties", None, within), ("T06", "indexstr", None, within),
            ("T06", "stampstr", None, within), ("T06", "end_early", None, within),
            ("T06", "before_start", None, ("not_evaluable", None, "ok", True)),
            *[("T07", name, opt, unestimable)
              for name in ("values", "status", "kind", "os_level", "pm_state", "pm_observed_ns")
              for opt in ("absent", "null")],
            ("T07", "all_error", None, unestimable),
            *[("T08", name, None, within) for name in ("future", "unknown_mid", "guard", "start_float")],
            ("T09", "TV0h", "absent", not_run), ("T09", "TV0h", "null", not_run),
            ("T09", "sensors", "absent", not_run), ("T09", "sensors", "null", not_run),
            *[("T10", name, opt, within) for name in ("gpu", "dvfm_states") for opt in ("absent", "null")],
            ("T10", "used_ns", "absent", within), ("T10", "used_ns", "null", not_run),
            ("T10", "native_empty", None, within), ("T10", "zero_elapsed", None, within),
            ("T11", "native_count", -1, not_run), ("T11", "native_count", 2, not_run),
            ("T11", "native_count", 1, within), ("T11", "native_outside", None, within),
            ("T11", "native_elapsed", None, within),
            ("T12", "pressure", False, within), ("T12", "pressure", "UnregisteredState", not_run),
            ("T13", "clock_overlap", None, within),
            ("T14", "short", None, not_run), ("T14", "zero_last", None, not_run),
            ("T15", "gap_part", None, within),
        ]
        for clause, name, option, primary in cases:
            with self.subTest(clause=clause, case=name, option=option), tempfile.TemporaryDirectory() as tmp:
                entrants = [(2000, lambda i=i: self.measurements(Path(tmp) / str(i), i, (name, option)))
                            for i in range(3)]
                result = step3_cells(entrants, 0.08)
                cell, = result["cells"]
                self.assertEqual(cell["prompt_tokens"], 2000)
                self.assertEqual((result["tripwire"]["decision"], result["tripwire"]["trips"],
                                  cell["status"], cell["gamma_estimable"]), primary)


FIXTURE_DECODER = '''
# Test double: a poll contains exactly one sample already anchored at rx.
import json
import struct
import sys
from pathlib import Path
from types import SimpleNamespace

def parse(path):
    assert not any(k == 'joulewise' or k.startswith('joulewise.') for k in sys.modules)
    header, *polls, trailer = [json.loads(line) for line in Path(path).read_text().splitlines()]
    watts = []
    for poll in polls:
        _, _, voltage, current, *_ = struct.unpack('<HHiiHHHH', bytes.fromhex(poll['p']))
        watts.append((voltage / 1e6) * (current / 1e6))
    return SimpleNamespace(header=header, present=True, aligned=True,
                           host_ns=[row['rx'] for row in polls], watts=watts)
'''

FIXTURE_PARENT = """
import json, pathlib, runpy, subprocess, sys
test = runpy.run_path(sys.argv[1])
private = pathlib.Path(sys.argv[2])
child_stdout, child_stderr = private / 'stdout', private / 'stderr'
with child_stdout.open('wb') as stdout, child_stderr.open('wb') as stderr:
    child = subprocess.run(sys.argv[3:], stdout=stdout, stderr=stderr, check=False)
assert child.returncode in (0, 1)
frame = json.loads(child_stdout.read_bytes()) if child.returncode == 0 else None
print(json.dumps({'twin_agrees': test['parent_agreement'](frame)}, separators=(',', ':')))
"""

IMPORT_AUDIT_CHILD = """
import builtins, runpy, sys
search_path, import_hook = sys.path[:], builtins.__import__
helpers = ('joulewise.aggregate', 'joulewise.desk_compress')
assert all(name not in sys.modules for name in helpers)
twin = runpy.run_path(sys.argv[1])
def evaluate():
    frame = twin['child_frame'](twin['child_arguments'](sys.argv[2:]))
    assert all(name not in sys.modules for name in helpers)
    assert sys.path == search_path and builtins.__import__ is import_hook
    return frame
twin['run_child'](evaluate)
"""


@unittest.skipUnless(HAS_NUMPY, "NumPy is required for the fit")
class RawBundleTests(unittest.TestCase):
    def test_actual_child_argv_on_fully_bound_raw_bundle(self):
        import hashlib
        import os
        import plistlib
        import shutil
        import struct
        import numpy as np
        from scripts.cadence_interim_twin import COEFFICIENT_KEYS

        def sha(data):
            return hashlib.sha256(data).hexdigest()

        def json_bytes(value):
            return json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True).encode()

        def lines(rows):
            return b"".join(json_bytes(row) + b"\n" for row in rows)

        def write(path, value):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
            return sha(value)

        vectors = {"gpu_rail": [n * 0.004 for n in (2, 5, 11, 17, 23)],
                   "dc_in": [n * 0.000064 for n in (3, 7, 13, 19, 29)]}
        names = ("p1", "p2", "a0", "a1", "a2")
        # The last of 1,025 tokens is outside the four full decode blocks.
        layout = ((255, 128), (256, 383.5), (256, 639.5), (256, 895.5))
        days = ["2026-01-01", "2026-01-02", "2026-01-03"]
        readings = {"tf08_c": 40.0, "fan_rpm": 1000.0, "tv0h_excess_c": 0.0}
        onset = {"status": "not_estimable", "predictors": ["intercept", "t_p_s"], "coefficients": None,
                 "sigma_s": None, "count_only_cut": {"form": "fixed_116_s", "offset_s": None, "fixed_s": 116.0}}

        def segment_values(prompt, channel):
            p1, p2, a0, a1, a2 = vectors[channel]
            return [p1 * prompt + p2 * prompt**2] + [
                count * (a0 + a1 * (prompt + offset) + a2 * prompt) for count, offset in layout
            ]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            custody, private = root / "synthetic-spans", root / "private-fixture"
            private.mkdir()
            stage1, _, primary_fit, _ = example_outputs()
            spans, records = [], []
            fixture_files = []
            staged_span = root / "staged-span"
            for index, day in enumerate(days):
                span = staged_span if index == 0 else custody / day
                operational = {}
                native_identity = {}
                roster = ["a", "b", "c"] + (["d"] if index == 0 else [])
                operational["runner_receipt.json"] = write(span / "runner_receipt.json",
                                                           json_bytes({"roster": roster, "steps": []}))
                header = {"k": "h", "schema": "synthetic", "status": "streaming", "rate_idx": 0, "sps": 2,
                          "poll_s": 0.5, "start_raw_ns": 10**10, "start_real_ns": 0, "start_mono_ns": 10**10}
                polls, poll_preimages = [], []
                for leg_index, (leg, prompt) in enumerate(zip(roster[:3], (2, 4, 8), strict=True)):
                    wall = leg_index * 48
                    bundle_name = "runs/cadence-leg"
                    bundle = f"legs/{leg}/runtime/{bundle_name}"
                    record = f"legs/{leg}/leg_record.json"
                    operational[record] = write(span / record, json_bytes({"spec": {"leg_type": "A"},
                                                                         "result": {"bundle": bundle_name}}))
                    gpu = segment_values(prompt, "gpu_rail") + [0.5]
                    dc = segment_values(prompt, "dc_in") + [0.5]
                    trace = "source,rail,interval_start_s,interval_end_s,timestamp_s,power_w\n"
                    endpoints = [(wall + i * 8, wall + (i + 1) * 8) for i in range(6)]
                    gpu_intervals = []
                    segments = []
                    for i, (a, b) in enumerate(endpoints):
                        # Each row contributes half the hand-derived response.
                        # The first leg's one-second prefix-only piece has no GPU support.
                        trace_start = a + 1 if i == 5 and leg_index == 0 else a
                        trace += f"powermetrics,gpu_power,{trace_start},{b},{b},{gpu[i] / 16!r}\n"
                        trace += f"powermetrics,gpu_power,{a + 2},{b - 2},{b - 2},{gpu[i] / 8!r}\n"
                        gpu_intervals.extend(([float(trace_start), float(b)], [float(a + 2), float(b - 2)]))
                        if i <= len(layout):
                            segments.append({"seg": i, "wall_start_s": a, "wall_end_s": b, "hot": i == 4})
                        for offset in range(16):
                            sample_index = 2 * a + offset
                            rx = 10**10 + sample_index * 500_000_000
                            counter = (65_000 + sample_index * 500) % 65_536
                            current_microamps = round((dc[i] / 4) * (1 - abs(offset - 8) / 8) * 10**6)
                            payload = struct.pack("<HHiiHHHH", counter, 0, 1_000_000, current_microamps, 0, 0, 0, 0)
                            polls.append({"k": "b", "n": 1, "tx": rx - 1000, "rx": rx,
                                          "rt": rx - 10**10, "p": payload.hex(), "smc": {}})
                            poll_preimages.append([rx - 1000, rx, rx - 10**10, 1, [counter]])
                    trace_path = span / bundle / "power_trace.csv"
                    write(trace_path, trace.encode())
                    trace_hash = sha(json.dumps(sorted(gpu_intervals)).encode())
                    token_times = [wall + 8 + 8 * i / 255 for i in range(256)]
                    for block in range(1, 4):
                        token_times.extend(wall + 8 + block * 8 + 8 * i / 256 for i in range(1, 257))
                    token_times.append(wall + 48)
                    sources = {
                        "events.jsonl": lines({"event_type": "token", "timestamp_s": t,
                                              "metadata": {"index": j}}
                                             for j, t in enumerate(token_times)),
                        "outputs/align_turns.jsonl": lines([{"start_stamp": {"epoch_s": wall},
                                                            "end_stamp": {"epoch_s": wall + 48},
                                                            "generation": {"output_token_ids": [1] * 1025}}]),
                        "outputs/align_thermal.jsonl": lines({"kind": "reading", "error": None,
                            "started": {"monotonic_ns": (wall + j) * 10**9},
                            "finished": {"wall_ns": (wall + j) * 10**9}, "values": {
                                "sensors": {"TV0h": 30 + index * 3}, "status": {"os_level": int(j >= 28),
                                 "pm_state": "Nominal", "pm_observed_ns": (wall + j) * 10**9}}}
                            for j in range(49) if j not in (25, 26, 27)),
                    }
                    for name, data in sources.items():
                        operational[f"{bundle}/{name}"] = write(span / bundle / name, data)
                    rich_times = list(range(wall + 1, wall + 49))
                    rich = lines({"timestamp_s": t, "elapsed_ns": 10**9, "gpu": {"gpu_energy": 0,
                                  "dvfm_states": [{"freq": 1000, "used_ns": 1000}]}} for t in rich_times)
                    native = b"\0".join(plistlib.dumps({"elapsed_ns": 10**9}) for _ in rich_times)
                    write(span / bundle / "rich_telemetry.jsonl", rich)
                    write(span / bundle / "raw/powermetrics.plist", native)
                    native_identity[bundle] = sha(json_bytes([[[str(t), "1000000000"] for t in rich_times],
                                                             [["1000000000", None] for _ in rich_times],
                                                             len(rich_times)]))
                    records.append({"leg_key": f"{day}/{leg}", "day": day, "span_id": day, "role": "fit",
                                    "leg_type": "A", "included": True, "in_energy_fit": True,
                                    "cell_prompt_tokens": prompt, "prefill_tokens": prompt, "decode_tokens": 1025,
                                    "start": {**readings, "state": "in_state"}, "segments": segments,
                                    "prefix_tails": ([{"prefix_len": 1024, "wall_start_s": wall + 40,
                                                       "wall_end_s": wall + 41}] if leg_index == 0 else
                                                     [{"prefix_len": 510, "wall_start_s": wall + 16,
                                                       "wall_end_s": wall + 23.9375}]),
                                    "state": {"onset_use": "uncensored" if prompt == 2 else "left_out_state_unobserved",
                                              "first_off_s": 28},
                                    "trace_holes": {"gpu_rail": {"rows_sha256": trace_hash}}})
                if index == 0:
                    operational["legs/d/leg_record.json"] = write(span / "legs/d/leg_record.json", json_bytes({
                        "spec": {"leg_type": "A"}, "result": {"bundle": "missing-mock"}}))
                    records.append({"leg_key": f"{day}/d", "day": day, "span_id": day, "role": "fit", "leg_type": "A",
                                    "included": True, "in_energy_fit": False, "cell_prompt_tokens": 16})
                rx = 10**10 + 144 * 10**9
                counter = (65_000 + 288 * 500) % 65_536
                end_sample = struct.pack("<HHiiHHHH", counter, 0, 1_000_000, 0, 0, 0, 0, 0)
                polls.append({"k": "b", "n": 1, "tx": rx - 1000, "rx": rx,
                              "rt": rx - 10**10, "p": end_sample.hex(), "smc": {}})
                poll_preimages.append([rx - 1000, rx, rx - 10**10, 1, [counter]])
                trailer = {"k": "t", "polls": len(polls), "stop_reason": "normal"}
                stream = "stream-a.jsonl"
                write(span / "hazards" / "meter" / stream, lines([header, *polls, trailer]))
                time_digest = sha(json.dumps([stream, header, trailer, 0], sort_keys=True).encode() +
                                  b"".join(json.dumps(row).encode() for row in poll_preimages))
                spans.append({"span_id": day, "role": "fit", "marks": ["reference from a redo"] if index == 2 else [],
                              "t0_local_date": day, "custody": {"files_sha256": operational,
                                  "meter_time_sha256": time_digest, "native_pm_sha256": native_identity}})
                for path in sorted(span.rglob("*")):
                    if path.is_file():
                        inventory_path = Path(day) / path.relative_to(span) if index == 0 else path
                        fixture_files.append({"path": str(inventory_path), "sha256": sha(path.read_bytes())})

            empty_span = "2026-01-04"
            empty_receipt = custody / empty_span / "runner_receipt.json"
            empty_digest = write(empty_receipt, json_bytes({"roster": [], "soak_attempts": [],
                                "steps": [{"name": "deadline", "rc": 130}, {"name": "restore", "rc": 0}]}))
            fixture_files.append({"path": str(empty_receipt), "sha256": empty_digest})
            spans.append({"span_id": empty_span, "role": "describe", "marks": [],
                          "t0_local_date": empty_span, "custody": {"files_sha256": {"runner_receipt.json": empty_digest},
                              "meter_time_sha256": None, "native_pm_sha256": {}}})

            local_script = root / "scripts" / SCRIPT.name
            local_script.parent.mkdir()
            shutil.copyfile(SCRIPT, local_script)
            script_pin = {"path": f"scripts/{SCRIPT.name}", "sha256": sha(SCRIPT.read_bytes())}
            decoder_dir = os.environ.get("JW_TWIN_DECODER_FIXTURE_DIR")
            decoder = root / "joulewise/external/km003c_parse.py"
            package = decoder.with_name("__init__.py")
            decoder_bytes = (Path(decoder_dir) / decoder.name).read_bytes() if decoder_dir else FIXTURE_DECODER.encode()
            package_bytes = (Path(decoder_dir) / package.name).read_bytes() if decoder_dir else b"# Synthetic dependency pin.\n"
            if decoder_dir:
                self.assertEqual(sha(decoder_bytes), "6b2e4f57776f03ba39ea644e395d4649d4e7a4ded27dd1e008eda77601fa6e0e")
                self.assertEqual(sha(package_bytes), "368cf26e48aa87f2bf0816009947df03bfaa75276c58e30e2cdbc84e3f14835c")
            decoder_pin = {"path": decoder.relative_to(root).as_posix(), "sha256": write(decoder, decoder_bytes)}
            package_pin = {"path": package.relative_to(root).as_posix(), "sha256": write(package, package_bytes)}
            stub = b"synthetic code and schema placeholder pinned by the fixture manifest"
            pin = {"path": "stub", "sha256": write(root / "stub", stub)}
            manifest = {"look_id": "lm-interim-01", "fit": {"twin": script_pin, "code": [pin],
                        "dependencies": [decoder_pin, package_pin], "step3": {"code": pin, "adapter": pin}},
                        "decisions": [{"id": "drift_tripwire", "threshold": 0.08}],
                        "stages": {"stage1": {"schema": pin}}, "freeze2": {"schema": pin}, "outputs": {"schema": pin}}
            m, s1 = root / "manifest.json", root / "stage1.json"
            mh = write(m, json_bytes(manifest))
            soak = {"spans": {day: {"attempts": 1, "field_present": False, "accepted": True, "retried": []}
                              for day in days}, "spans_with_retry": 0, "accepted_after_retry": 0, "stopped_by_soak": 0,
                    "retried_by_kind": {"slope": 0, "load": 0, "kind not recorded": 0}}
            soak["spans"][empty_span] = {"attempts": 0, "field_present": True, "accepted": False, "retried": []}
            stage1.update({"look_id": "lm-interim-01", "manifest_sha256": mh, "numpy_version": np.__version__,
                "synthetic": True, "rates": {"r_p": 14 / 24, "r_d": 1024 / 40}, "centring": readings,
                "active_readings": {name: {"active": False} for name in readings}, "calibrated_range": {},
                "roster": {"fit_days": days, "spans": spans}, "legs": records, "soak_retries": soak,
                "onset": {**onset, "lodo": None}})
            sh = write(s1, json_bytes(stage1))
            primary_c = dict.fromkeys(COEFFICIENT_KEYS)
            qualified = {"verdict": "passes"}
            primary_c.update({"look_id": "lm-interim-01", "manifest_sha256": mh, "stage1_sha256": sh,
                               "numpy_version": np.__version__, "synthetic": True,
                               "delta_column": "dropped_onset_not_estimable", "qualified_interim_half": qualified,
                               "channels": {}, "onset": {**onset, "folds": dict.fromkeys(days), "lodo_rms_s": None}})
            for channel, vector in vectors.items():
                values = dict(zip(names, vector, strict=True))
                base = {"columns": list(names), "coefficients": values, "fold_coefficients": dict.fromkeys(days, values)}
                primary_c["channels"][channel] = base
                full = primary_fit["channels"][channel]
                coverage = {"min": 1.5 if channel == "gpu_rail" else 1.0, "n_legs_under_0_99": 0}
                marked_days = days[:2]
                marked_view = {"columns": list(names), "coefficients": values,
                               "fold_coefficients": dict.fromkeys(marked_days, values),
                               "fold_coefficients_no_heat": dict.fromkeys(marked_days, values),
                               "trace_coverage": coverage, "lodo": {
                                   "hot": {"verdict": "not_evaluable"},
                                   "no_heat": {"hot": {"verdict": "not_evaluable"}}, "folds_delta_dropped": []}}
                full.update({**base, "fold_coefficients_no_heat": dict.fromkeys(days, values),
                             "trace_coverage": coverage,
                             "marked_sensitivity": {"coefficients_without": values, "fit_without": marked_view},
                             "lodo": {"hot": qualified, "no_heat": {"hot": qualified}, "folds_delta_dropped": []}})
            inventory = {"files": fixture_files}
            primary_fit.update({"custody": inventory, "soak_retries": soak})
            step3 = {"custody": inventory, "cells": [{"prompt_tokens": p, "status": "ok", "gamma_estimable": True}
                      for p in (2, 4, 8)] + [{"prompt_tokens": 16, "status": "not_run", "gamma_estimable": None}],
                     "tripwire": {"decision": "within", "trips": False, "threshold_applied": 0.08}}
            c, f, d = (private / name for name in ("coefficients.json", "fit.json", "step3.json"))
            ch = write(c, json_bytes(primary_c))
            write(f, json_bytes(primary_fit))
            write(d, json_bytes(step3))
            argv = ["--manifest", str(m), "--manifest-sha256", mh, "--ledger-commit", "a" * 40,
                    "--stage1", str(s1), "--stage1-sha256", sh, "--custody", str(custody),
                    "--span-dir", f"{days[0]}={staged_span}", "--coefficients", str(c),
                    "--coefficients-sha256", ch, "--fit", str(f), "--step3", str(d)]

            def bind_modified_inputs():
                stage1_hash = write(s1, json_bytes(stage1))
                primary_c["stage1_sha256"] = stage1_hash
                argv[argv.index("--stage1-sha256") + 1] = stage1_hash
                argv[argv.index("--coefficients-sha256") + 1] = write(c, json_bytes(primary_c))
                write(f, json_bytes(primary_fit))
                write(d, json_bytes(step3))

            original_empty_receipt = empty_receipt.read_bytes()
            empty_inventory = fixture_files[-1]
            empty_operational = spans[-1]["custody"]["files_sha256"]

            def bind_soak_receipt(receipt_bytes, span_soak, retries):
                receipt_hash = write(empty_receipt, receipt_bytes)
                empty_inventory["sha256"] = empty_operational["runner_receipt.json"] = receipt_hash
                soak["spans"][empty_span] = span_soak
                soak["spans_with_retry"] = soak["accepted_after_retry"] = retries
                soak["retried_by_kind"]["kind not recorded"] = retries
                soak["stopped_by_soak"] = int(span_soak["attempts"] > 0 and not span_soak["accepted"])

            empty_soak = soak["spans"][empty_span]
            stream = staged_span / "hazards/meter/stream-a.jsonl"
            original_stream = stream.read_bytes()
            for mode, expected, error in (("match", "yes", None), ("import audit", "yes", None),
                    ("retry after interruption", "not_evaluable", "ValueError"),
                    ("terminal refusal after interruption", "not_evaluable", "ValueError"),
                    ("hold with overflowing JSON number", "yes", None),
                    ("hold with NaN timestamp", "yes", None),
                    ("hold without timestamp", "yes", None),
                    ("perturbation", "no", None), ("missing stream", "not_evaluable", "FileNotFoundError"),
                    ("stage1 meter identity", "not_evaluable", "ValueError"),
                    ("decoder pin", "not_evaluable", "ValueError"), ("package pin", "not_evaluable", "ValueError"),
                    ("missing coefficient", "not_evaluable", "FileNotFoundError")):
                with self.subTest(mode=mode):
                    if mode == "retry after interruption":
                        receipt = {"roster": [], "soak_attempts": [soak_attempt(1, "refused"), soak_attempt(2)],
                                   "steps": [{"name": "soak", "rc": 130, "error": "SystemExit: 130"},
                                             {"name": "soak.a2", "rc": 0}]}
                        impossible = {"attempts": 2, "field_present": True, "accepted": True,
                                      "retried": [{"attempt": 1, "kind": "kind not recorded", "read_from": None}]}
                        bind_soak_receipt(json_bytes(receipt), impossible, 1)
                        bind_modified_inputs()
                    elif mode == "terminal refusal after interruption":
                        reason = "soak exit 5: the idle soak failed its settle or quiet check"
                        receipt = {"roster": [], "soak_attempts": [soak_attempt(1, reason)],
                                   "steps": [{"name": "soak", "rc": 130, "error": "SystemExit: 130"}]}
                        impossible = {"attempts": 1, "field_present": True, "accepted": False, "retried": []}
                        bind_soak_receipt(json_bytes(receipt), impossible, 0)
                        bind_modified_inputs()
                    elif mode.startswith("hold "):
                        event = {"event_type": "phase_start", "phase": "align_thermal_hold"}
                        if mode == "hold with overflowing JSON number":
                            bind_soak_receipt(original_empty_receipt, empty_soak, 0)
                            hold = b'{"event_type":"phase_start","phase":"align_thermal_hold","timestamp_s":1e309}\n'
                        elif mode == "hold with NaN timestamp":
                            hold = lines([dict(event, timestamp_s="NaN")])
                        else:
                            hold = lines([event])
                        file_entries = {file["path"]: file for file in fixture_files}
                        for span in spans[:len(days)]:
                            day = span["span_id"]
                            directory = staged_span if day == days[0] else custody / day
                            operational = span["custody"]["files_sha256"]
                            for name in operational:
                                if not name.endswith("/events.jsonl"):
                                    continue
                                path = directory / name
                                updated = write(path, path.read_bytes() + hold)
                                inventory_key = Path(day) / name if day == days[0] else path
                                operational[name] = updated
                                file_entries[str(inventory_key)]["sha256"] = updated
                        if mode == "hold without timestamp":
                            step3["cells"] = [dict(cell, status="not_run", gamma_estimable=None)
                                              for cell in step3["cells"]]
                            step3["tripwire"].update(decision="not_evaluable", trips=None)
                        bind_modified_inputs()
                    elif mode == "perturbation":
                        primary_c["channels"]["dc_in"]["coefficients"]["p1"] *= 1.001
                        argv[argv.index("--coefficients-sha256") + 1] = write(c, json_bytes(primary_c))
                    elif mode == "missing stream":
                        stream.unlink()
                    elif mode == "stage1 meter identity":
                        write(stream, original_stream)
                        spans[0]["custody"]["meter_time_sha256"] = "b" * 64
                        altered = write(s1, json_bytes(stage1))
                        primary_c["stage1_sha256"] = altered
                        argv[argv.index("--stage1-sha256") + 1] = altered
                        argv[argv.index("--coefficients-sha256") + 1] = write(c, json_bytes(primary_c))
                    elif mode == "decoder pin":
                        write(decoder, decoder_bytes + b"\n")
                    elif mode == "package pin":
                        write(decoder, decoder_bytes)
                        write(package, package_bytes + b"\n")
                    elif mode == "missing coefficient":
                        write(package, package_bytes)
                        c.unlink()
                    before = {path: sha(path.read_bytes()) for path in root.rglob("*") if path.is_file()
                              and path.name not in ("stdout", "stderr")}
                    child = [sys.executable, "-I", "-B"]
                    if mode == "import audit":
                        child.extend(("-c", IMPORT_AUDIT_CHILD))
                    child.extend((str(local_script), *argv))
                    outer = subprocess.run([sys.executable, "-I", "-B", "-c", FIXTURE_PARENT,
                                            str(Path(__file__).resolve()), str(private), *child],
                                           capture_output=True, check=True)
                    self.assertEqual(outer.stderr, b"")
                    self.assertEqual(outer.stdout, json_bytes({"twin_agrees": expected}) + b"\n")
                    self.assertIsNone(re.search(rb"[0-9]", outer.stdout + outer.stderr))
                    frame_bytes = (private / "stdout").read_bytes()
                    error_bytes = (private / "stderr").read_bytes()
                    if error is None:
                        self.assertEqual(error_bytes, b"")
                        self.assertEqual(frame_bytes.count(b"\n"), 1)
                        frame = json.loads(frame_bytes)
                        self.assertEqual(set(frame), {"schema", "coefficients", "censored_fit", "verdicts",
                                                       "trace_coverage", "soak_retries", "max_relative_difference"})
                    else:
                        self.assertEqual(frame_bytes, b"")
                        self.assertEqual(error_bytes, f"stage2_error\n{error}\n".encode())
                        frame = None
                    self.assertEqual(parent_agreement(frame), expected)
                    self.assertEqual(before, {path: sha(path.read_bytes()) for path in root.rglob("*") if path.is_file()
                                             and path.name not in ("stdout", "stderr")})
