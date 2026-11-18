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


class ComparisonTests(unittest.TestCase):
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


class ReaderTests(unittest.TestCase):
    def test_span_override_and_runtime_bundle_containment(self):
        from scripts.cadence_interim_twin import bundle_directory, span_dirs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "a").mkdir()
            override = root / "alternate"
            runtime = override / "legs" / "sample" / "runtime" / "attempt"
            runtime.mkdir(parents=True)
            record = runtime.parents[1] / "leg_record.json"
            record.write_text('{"result":{"bundle":"attempt"}}')
            directories = span_dirs(root, [f"b={override}"], {"a", "b"})
            self.assertEqual(directories, {"a": root / "a", "b": override})
            self.assertEqual(bundle_directory(directories["b"], "sample", Path.read_bytes), runtime)
            record.write_text('{"result":{"bundle":"../../.."}}')
            with self.assertRaises(ValueError):
                bundle_directory(directories["b"], "sample", Path.read_bytes)

    def test_gpu_rows_and_meter_payload_are_independently_decoded(self):
        import struct
        from scripts.cadence_interim_twin import gpu_rows, meter_records, power_intervals

        raw = (b"source,rail,interval_start_s,interval_end_s,timestamp_s,power_w\n"
               b"powermetrics,gpu_power,0,1,1,3\n"
               b"powermetrics,cpu_power,0,2,2,99\n"
               b"powermetrics,gpu_power,1,2,2,7\n")
        gpu = gpu_rows(raw)
        self.assertEqual(power_intervals(gpu, 0.5, 1.25), (3.25, 1.0))
        self.assertEqual(power_intervals(gpu, 0.5, 2.5), (8.5, 0.75))
        with self.assertRaises(ValueError):
            power_intervals(gpu, 0.5, 4.1)

        payload = struct.pack("<HHiiHHHH", 22, 0, 20_000_000, -250_000, 0, 0, 0, 0)
        rows = [{"k": "h", "sps": 100, "status": "streaming"},
                {"k": "b", "n": 1, "p": payload.hex()}, {"k": "t"}]
        stream = b"\n".join(json.dumps(row).encode() for row in rows)
        self.assertEqual(meter_records(stream)[1][0][1], [(22, -5.0)])
        rows[1]["n"] = 2
        malformed = b"\n".join(json.dumps(row).encode() for row in rows)
        with self.assertRaises(ValueError):
            meter_records(malformed)

    def test_soak_retries_read_legacy_and_current_receipts(self):
        from scripts.cadence_interim_twin import soak_summary

        receipts = {"a": {}, "b": {
            "steps": [{"name": "soak", "rc": 1}, {"name": "soak.a3", "rc": 0}],
            "soak_attempts": [{"attempt": 1, "refused": "refused", "refusal_kind": "load"},
                              {"attempt": 2, "refused": "refused", "refusal_kind": "load"},
                              {"attempt": 3, "refused": None}],
            "soak_refusals": [{"attempt": 1, "kind": "slope"}],
        }, "c": {"steps": [{"name": "soak.a2", "rc": None}],
                   "soak_attempts": [{"attempt": 1, "refused": "refused"},
                                     {"attempt": 2, "refused": "refused"}]}}
        summary = soak_summary(receipts)
        self.assertEqual(summary["spans"]["a"], {"attempts": 1, "field_present": False,
                                                "accepted": True, "retried": []})
        self.assertEqual(summary["spans"]["b"]["retried"], [
            {"attempt": 1, "kind": "slope", "read_from": "receipt soak_refusals[].kind"},
            {"attempt": 2, "kind": "load", "read_from": "receipt soak_attempts[].refusal_kind"},
        ])
        self.assertEqual(summary["spans"]["c"]["retried"], [
            {"attempt": 1, "kind": "kind not recorded", "read_from": None},
        ])
        self.assertEqual(summary["spans_with_retry"], 2)
        self.assertEqual(summary["retried_by_kind"], {"slope": 1, "load": 1, "kind not recorded": 1})
        self.assertEqual(summary["accepted_after_retry"], 1)
        self.assertEqual(summary["stopped_by_soak"], 1)

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


@unittest.skipUnless(HAS_NUMPY, "NumPy is required for the fit")
class EndToEndProjectionTests(unittest.TestCase):
    def test_authenticated_argv_and_private_frame_with_hand_fit(self):
        import hashlib
        import shutil
        import numpy as np
        from scripts.cadence_interim_twin import COEFFICIENT_KEYS

        # Medium-scale, varying wall energy fixtures with identical count-clock coefficients.
        # Divide the total 513 decode tokens over two full blocks and a 1-token tail.
        vectors = {"gpu_rail": (2, 5, 11, 17, 23), "dc_in": (3, 7, 13, 19, 29)}
        names = ("p1", "p2", "a0", "a1", "a2")
        layout = ((255, 128), (256, 383.5), (1, 512))
        days = ["day1", "day2", "day3"]
        records, responses = [], []
        for day in days:
            for prompt in (2, 4, 8):
                records.append({
                    "day": day, "span_id": day, "cell_prompt_tokens": prompt, "prefill_tokens": prompt,
                    "decode_tokens": 513, "start": {"state": "in_state"},
                    "state": {"onset_use": "left_out_state_unobserved"},
                    "segments": [{"wall_start_s": i, "wall_end_s": i + 1, "hot": i > 0} for i in range(4)],
                })
                channels = {}
                for channel, (p1, p2, a0, a1, a2) in vectors.items():
                    channels[channel] = {"segments": [p1 * prompt + p2 * prompt**2] + [
                        n * (a0 + a1 * (prompt + mean_context) + a2 * prompt) for n, mean_context in layout
                    ], "coverage_min": 1.0}
                responses.append(channels)

        stage1, _, primary_fit, primary_step3 = example_outputs()
        onset = {"status": "not_estimable", "predictors": ["intercept", "t_p_s"], "coefficients": None,
                 "sigma_s": None, "count_only_cut": {"form": "fixed_116_s", "offset_s": None, "fixed_s": 116.0}}
        stage1.update({
            "look_id": "lm-interim-01", "numpy_version": np.__version__, "synthetic": True,
            "rates": {"r_p": 2.0, "r_d": 256.0}, "centring": {},
            "active_readings": {name: {"active": False} for name in ("tf08_c", "fan_rpm", "tv0h_excess_c")},
            "roster": {"fit_days": days}, "onset": {**onset, "lodo": None},
        })
        primary_c = dict.fromkeys(COEFFICIENT_KEYS)
        primary_c.update({
            "look_id": "lm-interim-01", "numpy_version": np.__version__, "synthetic": True,
            "delta_column": "dropped_onset_not_estimable", "qualified_interim_half": {"verdict": "passes"},
            "channels": {}, "onset": {**onset, "folds": dict.fromkeys(days), "lodo_rms_s": None},
        })
        for channel, vector in vectors.items():
            coefficients = dict(zip(names, map(float, vector), strict=True))
            base = {"columns": list(names), "coefficients": coefficients,
                    "fold_coefficients": dict.fromkeys(days, coefficients)}
            primary_c["channels"][channel] = base
            primary_fit["channels"][channel].update({
                **base, "fold_coefficients_no_heat": dict.fromkeys(days, coefficients),
                "lodo": {"hot": {"verdict": "passes"}, "no_heat": {"hot": {"verdict": "passes"}},
                         "folds_delta_dropped": days},
            })
        primary_fit["custody"] = primary_step3["custody"] = {"files": []}
        launcher = """
import json, runpy, sys
child = runpy.run_path(sys.argv[1])
rows, observations, step3 = json.loads(sys.argv[2])
def derive(args, manifest, stage1, fit_identity, step3_identity):
    fit = child['recompute_fit'](stage1, rows, observations, set())
    fit['soak_retries'] = {'spans_with_retry': 0}
    return fit, step3
child['run_child'](lambda: child['child_frame'](child['child_arguments'](sys.argv[3:]), derive))
"""
        def write(path, value):
            data = json.dumps(value, allow_nan=False).encode()
            path.write_bytes(data)
            return hashlib.sha256(data).hexdigest()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private = root / "private-fixture"
            private.mkdir()
            local_script = root / "scripts" / SCRIPT.name
            local_script.parent.mkdir()
            shutil.copyfile(SCRIPT, local_script)
            script_pin = {"path": f"scripts/{SCRIPT.name}", "sha256": hashlib.sha256(SCRIPT.read_bytes()).hexdigest()}
            stub = b"a synthetic code or schema pin"
            (root / "stub").write_bytes(stub)
            pin = {"path": "stub", "sha256": hashlib.sha256(stub).hexdigest()}
            manifest = {"look_id": "lm-interim-01", "fit": {"twin": script_pin, "code": [pin],
                        "dependencies": [pin], "step3": {"code": pin, "adapter": pin}},
                        "stages": {"stage1": {"schema": pin}}, "freeze2": {"schema": pin}, "outputs": {"schema": pin}}
            m, s1 = root / "manifest.json", root / "stage1.json"
            c, f, d = (private / name for name in ("coefficients.json", "fit.json", "step3.json"))
            mh = write(m, manifest)
            stage1["manifest_sha256"] = mh
            sh = write(s1, stage1)
            primary_c.update({"manifest_sha256": mh, "stage1_sha256": sh})
            ch = write(c, primary_c)
            write(f, primary_fit)
            write(d, primary_step3)
            argv = ["--manifest", str(m), "--manifest-sha256", mh, "--ledger-commit", "a" * 40,
                    "--stage1", str(s1), "--stage1-sha256", sh, "--custody", str(root),
                    "--coefficients", str(c), "--coefficients-sha256", ch, "--fit", str(f), "--step3", str(d)]
            direct = subprocess.run([sys.executable, "-I", "-B", str(local_script), *argv],
                                    capture_output=True, check=False)
            self.assertEqual(direct.returncode, 1)
            self.assertEqual(direct.stdout, b"")
            self.assertEqual(direct.stderr, b"stage2_error\nNotImplementedError\n")
            for mode, expected in (("match", "yes"), ("changed", "no"), ("unbound", "not_evaluable"),
                                   ("missing", "not_evaluable")):
                with self.subTest(mode=mode):
                    if mode == "changed":
                        changed = primary_c["channels"]["dc_in"]["coefficients"]
                        changed["p1"] *= 1.001
                        argv[argv.index("--coefficients-sha256") + 1] = write(c, primary_c)
                    elif mode == "unbound":
                        c.write_bytes(c.read_bytes() + b" ")
                    elif mode == "missing":
                        c.unlink()
                    before = c.read_bytes() if c.exists() else None
                    with (private / "stdout").open("wb") as out, (private / "stderr").open("wb") as err:
                        process = subprocess.run([sys.executable, "-I", "-B", "-c", launcher, str(local_script),
                                                  json.dumps([records, responses, primary_step3]), *argv],
                                                 stdout=out, stderr=err, check=False)
                    stdout, stderr = (private / "stdout").read_bytes(), (private / "stderr").read_bytes()
                    if expected == "not_evaluable":
                        self.assertEqual(process.returncode, 1)
                        self.assertEqual(stdout, b"")
                        self.assertEqual(stderr, b"stage2_error\n" + (b"FileNotFoundError" if mode == "missing" else b"ValueError") + b"\n")
                        frame = None
                    else:
                        self.assertEqual(process.returncode, 0, stderr)
                        self.assertEqual(stderr, b"")
                        self.assertEqual(stdout.count(b"\n"), 1)
                        frame = json.loads(stdout)
                        self.assertEqual(set(frame), {"schema", "coefficients", "censored_fit", "verdicts",
                                                       "trace_coverage", "soak_retries", "max_relative_difference"})
                        self.assertIn(b"max_relative_difference", stdout)
                    self.assertEqual(parent_agreement(frame), expected)
                    self.assertEqual(c.read_bytes() if c.exists() else None, before)
                    self.assertFalse((private / "twin.json").exists())


class Step3CutTests(unittest.TestCase):
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
        fresh = [{"kind": "sample", "error": None, "started": {"monotonic_ns": i * 10**9},
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
        fresh[8]["values"]["status"]["os_level"] = 1
        _, _, _, journal, power = step3_records(lines(events), lines(turns), lines(fresh), lines(rich), native)
        self.assertEqual(step3_cut(start, decoded, journal, power), 6)
        fresh[0]["values"]["status"]["os_level"] = 1
        _, _, _, journal, power = step3_records(lines(events), lines(turns), lines(fresh), lines(rich), native)
        self.assertIsNone(step3_cut(start, decoded, journal, power))
