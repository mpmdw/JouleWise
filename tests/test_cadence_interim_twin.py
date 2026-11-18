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
        from scripts.cadence_interim_twin import span_dirs, span_identities

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "a").mkdir()
            override = root / "alternate"
            runtime = override / "legs" / "sample" / "runtime" / "attempt"
            runtime.mkdir(parents=True)
            record = runtime.parents[1] / "leg_record.json"
            record.write_text('{"result":{"bundle":"attempt"}}')
            (override / "runner_receipt.json").write_text('{"roster":["sample"]}')
            directories = span_dirs(root, [f"b={override}"], {"a", "b"})
            self.assertEqual(directories, {"a": root / "a", "b": override})
            self.assertEqual(span_identities(directories["b"])[1], {"sample": "legs/sample/runtime/attempt"})
            record.write_text('{"result":{"bundle":"../../.."}}')
            with self.assertRaises(ValueError):
                span_identities(directories["b"])

    def test_meter_decoder_import_boundary(self):
        from scripts.cadence_interim_twin import meter_decoder

        decoder_with_extra_import = b"from joulewise.aggregate import student_t_critical_95\n"
        with self.assertRaises(ImportError):
            meter_decoder((SCRIPT, decoder_with_extra_import))

    def test_gpu_rows_and_raw_meter_time_identities(self):
        import struct
        from scripts.cadence_interim_twin import digest, gpu_rows, gpu_time_digest, meter_time_digest, power_intervals

        raw = (b"source,rail,interval_start_s,interval_end_s,timestamp_s,power_w\n"
               b"powermetrics,gpu_power,0,1,1,3\n"
               b"powermetrics,cpu_power,0,2,2,99\n"
               b"powermetrics,gpu_power,1,2,2,7\n")
        gpu = gpu_rows(raw)
        self.assertEqual(power_intervals(gpu, 0.5, 1.25), (3.25, 1.0))
        self.assertEqual(power_intervals(gpu, 0.5, 2.5), (8.5, 0.75))
        with self.assertRaises(ValueError):
            power_intervals(gpu, 0.5, 4.1)

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
    def test_step3_temperature_at_unsnapped_cut_and_block_mean(self):
        from scripts.cadence_interim_twin import step3_observations

        tokens = [1 + 0.1 * i for i in range(512)] + [56.0]
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
        fresh[8]["values"]["status"]["os_level"] = 1
        _, _, _, journal, power = step3_records(lines(events), lines(turns), lines(fresh), lines(rich), native)
        self.assertEqual(step3_cut(start, decoded, journal, power), 6)
        fresh[0]["values"]["status"]["os_level"] = 1
        _, _, _, journal, power = step3_records(lines(events), lines(turns), lines(fresh), lines(rich), native)
        self.assertIsNone(step3_cut(start, decoded, journal, power))


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
        # Gap counts and context offsets derived by hand for 1,025 stamped tokens.
        layout = ((255, 128), (256, 383.5), (256, 639.5), (256, 895.5), (1, 1024))
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
            for index, day in enumerate(days):
                span = custody / day
                operational = {}
                native_identity = {}
                roster = ["a", "b", "c"] + (["d"] if index == 0 else [])
                operational["runner_receipt.json"] = write(span / "runner_receipt.json", json_bytes({"roster": roster}))
                header = {"k": "h", "schema": "synthetic", "status": "streaming", "rate_idx": 0, "sps": 2,
                          "poll_s": 0.5, "start_raw_ns": 10**10, "start_real_ns": 0, "start_mono_ns": 10**10}
                polls, poll_preimages = [], []
                for leg_index, (leg, prompt) in enumerate(zip(roster[:3], (2, 4, 8), strict=True)):
                    wall = leg_index * 48
                    bundle = f"legs/{leg}/runtime/mock"
                    record = f"legs/{leg}/leg_record.json"
                    operational[record] = write(span / record, json_bytes({"spec": {"leg_type": "A"},
                                                                         "result": {"bundle": "mock"}}))
                    gpu, dc = segment_values(prompt, "gpu_rail"), segment_values(prompt, "dc_in")
                    trace = "source,rail,interval_start_s,interval_end_s,timestamp_s,power_w\n"
                    endpoints = [(wall + i * 8, wall + (i + 1) * 8) for i in range(6)]
                    segments = []
                    for i, (a, b) in enumerate(endpoints):
                        trace += f"powermetrics,gpu_power,{a},{b},{b},{gpu[i] / 8!r}\n"
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
                    trace_hash = sha(json.dumps([[float(a), float(b)] for a, b in endpoints]).encode())
                    token_times = [wall + 8 + 8 * i / 255 for i in range(256)]
                    for block in range(1, 4):
                        token_times.extend(wall + 8 + block * 8 + 8 * i / 256 for i in range(1, 257))
                    token_times.append(wall + 48)
                    sources = {
                        "events.jsonl": lines({"event_type": "token", "timestamp_s": t,
                                              "metadata": {"index": j, "align_turn_index": 0}}
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
                    native = b"\0".join(plistlib.dumps({"elapsed_ns": 10**9, "thermal_pressure": "Nominal"})
                                        for _ in rich_times)
                    write(span / bundle / "rich_telemetry.jsonl", rich)
                    write(span / bundle / "raw/powermetrics.plist", native)
                    native_identity[bundle] = sha(json_bytes([[[str(t), "1000000000"] for t in rich_times],
                                                             [["1000000000", "4e6f6d696e616c"] for _ in rich_times],
                                                             len(rich_times)]))
                    records.append({"leg_key": f"{day}/{leg}", "day": day, "span_id": day, "role": "fit",
                                    "leg_type": "A", "included": True, "in_energy_fit": True,
                                    "cell_prompt_tokens": prompt, "prefill_tokens": prompt, "decode_tokens": 1025,
                                    "start": {**readings, "state": "in_state"}, "segments": segments,
                                    "prefix_tails": [{"prefix_len": 510, "wall_start_s": wall + 16,
                                                      "wall_end_s": wall + 23.9375}],
                                    "state": {"onset_use": "left_out_state_unobserved", "first_off_s": 28},
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
                fixture_files.extend(path for path in span.rglob("*") if path.is_file())

            local_script = root / "scripts" / SCRIPT.name
            local_script.parent.mkdir()
            shutil.copyfile(SCRIPT, local_script)
            script_pin = {"path": f"scripts/{SCRIPT.name}", "sha256": sha(SCRIPT.read_bytes())}
            decoder_dir = os.environ.get("JW_TWIN_DECODER_FIXTURE_DIR")
            decoder = root / "joulewise/external/km003c_parse.py"
            package = decoder.with_name("__init__.py")
            decoder_bytes = (Path(decoder_dir) / decoder.name).read_bytes() if decoder_dir else FIXTURE_DECODER.encode()
            package_bytes = (Path(decoder_dir) / package.name).read_bytes() if decoder_dir else b"# Synthetic dependency pin.\n"
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
                marked_days = days[:2]
                marked_view = {"columns": list(names), "coefficients": values,
                               "fold_coefficients": dict.fromkeys(marked_days, values),
                               "fold_coefficients_no_heat": dict.fromkeys(marked_days, values),
                               "trace_coverage": {"min": 1.0, "n_legs_under_0_99": 0}, "lodo": {
                                   "hot": {"verdict": "not_evaluable"},
                                   "no_heat": {"hot": {"verdict": "not_evaluable"}}, "folds_delta_dropped": marked_days}}
                full.update({**base, "fold_coefficients_no_heat": dict.fromkeys(days, values),
                             "marked_sensitivity": {"coefficients_without": values, "fit_without": marked_view},
                             "lodo": {"hot": qualified, "no_heat": {"hot": qualified}, "folds_delta_dropped": days}})
            inventory = {"files": [{"path": str(path), "sha256": sha(path.read_bytes())} for path in fixture_files]}
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
                    "--span-dir", f"{days[0]}={custody / days[0]}", "--coefficients", str(c),
                    "--coefficients-sha256", ch, "--fit", str(f), "--step3", str(d)]

            for mode, expected, error in (("match", "yes", None), ("perturbation", "no", None),
                    ("stage1 meter identity", "not_evaluable", "ValueError"),
                    ("decoder pin", "not_evaluable", "ValueError"), ("package pin", "not_evaluable", "ValueError"),
                    ("missing coefficient", "not_evaluable", "FileNotFoundError")):
                with self.subTest(mode=mode):
                    if mode == "perturbation":
                        primary_c["channels"]["dc_in"]["coefficients"]["p1"] *= 1.001
                        argv[argv.index("--coefficients-sha256") + 1] = write(c, json_bytes(primary_c))
                    elif mode == "stage1 meter identity":
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
                    with (private / "stdout").open("wb") as stdout, (private / "stderr").open("wb") as stderr:
                        process = subprocess.run([sys.executable, "-I", "-B", str(local_script), *argv],
                                                 stdout=stdout, stderr=stderr, check=False)
                    frame_bytes = (private / "stdout").read_bytes()
                    error_bytes = (private / "stderr").read_bytes()
                    if error is None:
                        self.assertEqual(process.returncode, 0, error_bytes)
                        self.assertEqual(error_bytes, b"")
                        self.assertEqual(frame_bytes.count(b"\n"), 1)
                        frame = json.loads(frame_bytes)
                        self.assertEqual(set(frame), {"schema", "coefficients", "censored_fit", "verdicts",
                                                       "trace_coverage", "soak_retries", "max_relative_difference"})
                    else:
                        self.assertEqual(process.returncode, 1)
                        self.assertEqual(frame_bytes, b"")
                        self.assertEqual(error_bytes, f"stage2_error\n{error}\n".encode())
                        frame = None
                    agreement = parent_agreement(frame)
                    self.assertEqual(agreement, expected)
                    self.assertIsNone(re.search(rb"[0-9]", json_bytes({"twin_agrees": agreement})))
                    self.assertEqual(before, {path: sha(path.read_bytes()) for path in root.rglob("*") if path.is_file()
                                             and path.name not in ("stdout", "stderr")})
