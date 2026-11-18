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


def result():
    # Internal comparison values, generated here. This is not the parent wire format.
    return {
        "coefficients": {
            "gpu_rail": {"main": {"p1": 2.0}, "folds": {"day1": {"p1": 3.0}}},
            "dc_in": {"main": {"p1": 4.0}, "folds": {"day1": {"p1": 5.0}}},
        },
        "censored_fit": {"sigma_s": 2.0, "lodo": {"rms_s": 3.0}},
        "verdicts": {"gpu_rail": {"qualified": "yes"}, "dc_in": {"qualified": "no"}},
        "trace_coverage": {"gpu_rail": [1.0, 0], "dc_in": [1.0, 0]},
        "soak_retries": {"span1": [{"attempt": 1, "kind": "not recorded"}]},
    }


class ComparisonTests(unittest.TestCase):
    def test_all_registered_fields_on_both_channels(self):
        from scripts.cadence_interim_twin import compare

        def verdict(data):
            data["verdicts"]["dc_in"]["qualified"] = "yes"

        def coverage(data):
            data["trace_coverage"]["gpu_rail"][0] -= 1e-12

        def retries(data):
            data["soak_retries"]["span1"][0]["attempt"] += 1

        for change in (verdict, coverage, retries):
            with self.subTest(change=change.__name__):
                primary = result()
                change(primary)
                self.assertEqual(compare(result(), primary), "no")
        primary = result()
        primary["ledger_gate"] = "different"
        self.assertEqual(compare(result(), primary), "yes")

    def test_relative_tolerances_and_missing_inputs(self):
        from scripts.cadence_interim_twin import compare

        for channel in ("dc_in", "gpu_rail"):
            for section, field in (("main", None), ("folds", "day1")):
                for scale, expected in ((0.9, "yes"), (1.1, "no")):
                    with self.subTest(channel=channel, section=section, scale=scale):
                        primary = result()
                        values = primary["coefficients"][channel][section]
                        if field is not None:
                            values = values[field]
                        values["p1"] *= 1 + scale * 1e-8
                        self.assertEqual(compare(result(), primary), expected)

        for scale, expected in ((0.9, "yes"), (1.1, "no")):
            primary = result()
            primary["censored_fit"]["lodo"]["rms_s"] *= 1 + scale * 1e-6
            self.assertEqual(compare(result(), primary), expected)

        primary = result()
        del primary["soak_retries"]
        self.assertEqual(compare(result(), primary), "not_evaluable")
        primary = result()
        primary["coefficients"]["dc_in"]["main"]["p1"] = math.nan
        self.assertEqual(compare(result(), primary), "not_evaluable")

    def test_isolated_child_byte_scan_and_write_boundary(self):
        launcher = """
import importlib.util, json, os, pathlib, runpy, sys, warnings
run_child = runpy.run_path(sys.argv[1])["run_child"]
root = pathlib.Path(sys.argv[2])
def evaluate():
    assert sys.flags.isolated
    spec = importlib.util.spec_from_file_location("synthetic_import", root / "synthetic_import.py")
    spec.loader.exec_module(importlib.util.module_from_spec(spec))
    data = json.loads((root / "synthetic.json").read_bytes())
    canary = str(data["canary"])
    print(canary, flush=True)
    sys.stderr.write(canary)
    os.write(1, canary.encode())
    os.write(2, canary.encode())
    warnings.warn(canary)
    if sys.argv[3] == "error":
        raise RuntimeError(canary)
    return data["twin"], data["primary"]
run_child(root / "fixture-output", evaluate)
"""
        for mode, expected in (
            ("match", b"yes\n"),
            ("mismatch", b"no\n"),
            ("missing", b"not_evaluable\n"),
            ("error", b"not_evaluable\n"),
            ("occupied", b"not_evaluable\n"),
        ):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                private = root / "fixture-output"
                private.mkdir()
                (root / "synthetic_import.py").write_text("# Test import-side file creation.\n")
                initial = {"fixture-output", "synthetic_import.py"}
                if mode != "missing":
                    primary = result()
                    if mode == "mismatch":
                        primary["coefficients"]["dc_in"]["main"]["p1"] *= 1.001
                    (root / "synthetic.json").write_text(json.dumps({
                        "canary": 987654.321, "twin": result(), "primary": primary,
                    }))
                    initial.add("synthetic.json")
                if mode == "occupied":
                    (private / "twin.json").symlink_to(root / "synthetic.json")
                completed = subprocess.run(
                    [sys.executable, "-I", "-c", launcher, str(SCRIPT), tmp, mode],
                    capture_output=True, check=True,
                )
                self.assertEqual(completed.stdout, expected)
                self.assertEqual(completed.stderr, b"")
                self.assertIsNone(re.search(rb"[0-9]", completed.stdout + completed.stderr))
                self.assertEqual({p.name for p in root.iterdir()}, initial)
                if expected in (b"yes\n", b"no\n"):
                    self.assertEqual({p.name for p in private.iterdir()}, {"twin.json"})
                    saved = json.loads((private / "twin.json").read_bytes())
                    self.assertEqual(saved["agreement"], expected.decode().strip())
                elif mode == "occupied":
                    self.assertTrue((private / "twin.json").is_symlink())
                    self.assertEqual(json.loads((root / "synthetic.json").read_bytes())["twin"], result())
                else:
                    self.assertEqual(list(private.iterdir()), [])

    def test_direct_entrypoint_refuses_unbound_inputs(self):
        completed = subprocess.run([sys.executable, "-I", "-B", str(SCRIPT)],
                                   capture_output=True, check=True)
        self.assertEqual(completed.stdout, b"not_evaluable\n")
        self.assertEqual(completed.stderr, b"")


@unittest.skipUnless(HAS_NUMPY, "NumPy is required for the fit")
class FitTests(unittest.TestCase):
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
        names, rows = design_rows(legs[0], rates, ("k_tf08",))
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
                for lo, hi, n, offset in ((0, 255, 255, 128), (255, 511, 256, 383.5),
                                          (511, 512, 1, 512)):
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
                self.assertAlmostEqual(heat, -4.5 * coefficients[-1])
                for prediction, energy in zip(predictions, measurements[channel][0]):
                    self.assertTrue(math.isclose(prediction, energy, rel_tol=1e-8))

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


class DiagnosticsTests(unittest.TestCase):
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
