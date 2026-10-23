"""Tests for the BYTES twin (scripts/bytes_twin.py): hand-computed worked examples and the twin's own
synthetic bytes-is-truth world (tests/fixtures/bytes/twin_synth.py).  The agreement with the analysis on
the lane's production-shaped campaigns is tests/test_bytes_agreement.py.

Run from the repository root:
    JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m pytest tests/test_bytes_twin.py -q
"""
import importlib.util
import json
import math
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from scripts import bytes_twin as bt

ROOT = Path(__file__).resolve().parents[1]
_synth_spec = importlib.util.spec_from_file_location("twin_synth", ROOT / "tests/fixtures/bytes/twin_synth.py")
synth = importlib.util.module_from_spec(_synth_spec)
_synth_spec.loader.exec_module(synth)

WORLD = {}


def setUpModule():
    WORLD["dir"] = tempfile.TemporaryDirectory(prefix="bytes-twin-")
    root = Path(WORLD["dir"].name)
    WORLD["one"] = root / "one"
    WORLD["truth_one"] = synth.generate(WORLD["one"], seed=7, passes=1, defects=True)
    WORLD["two"] = root / "two"
    WORLD["truth_two"] = synth.generate(WORLD["two"], seed=11, passes=2, defects=False)
    WORLD["refused"] = root / "refused"
    WORLD["truth_refused"] = synth.generate(WORLD["refused"], seed=5, passes=2, defects=False,
                                            refuse_pass=("Qwen3-14B-4bit", 1))


def tearDownModule():
    WORLD["dir"].cleanup()


def run_twin(world: Path, stage: str, *, archives=True, key_dir=True) -> dict:
    out = world / f"twin-{stage}.json"
    argv = ["--export-dir", str(world / "exports"), "--manifest", str(world / "bytes_manifest.json"),
            "--stage", stage, "--out", str(out)]
    if archives:
        for archive in sorted((world / "archives").iterdir()):
            argv += ["--archive", str(archive)]
    if key_dir:
        argv += ["--key-dir", str(world / "keys")]
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        assert bt.main(argv) == 0
    return json.loads(out.read_text())


class ConstantsTests(unittest.TestCase):
    def test_addendum5_512_decode_passes(self):
        self.assertEqual(bt.DECODE_STEPS, 512)
        self.assertEqual(bt.PRINTED_TOKENS, 512)
        self.assertEqual(bt.PER_TOKEN_LABEL, "512 decode forward passes, one of which yields no returned token")
        self.assertEqual(synth.DECODE_STEPS, 512)

    def test_e_tau_and_bw_use_512(self):
        est = {"status": "ok", "mean_j": 1024.0, "lower_j": 1000.0, "upper_j": 1048.0, "lower95_j": 1010.0,
               "upper95_j": 1038.0, "duration_s": 5.12, "n_r": 10, "n_b": 10, "h_j": 1.0, "B_j": 11.0,
               "variance": 0.1, "df": 9}
        q = bt.quantities({"gross": est}, {"b_GB": 2.0, "R_GB": 4.0})["gross"]
        self.assertAlmostEqual(q["e_j_per_step"], 2.0)
        self.assertAlmostEqual(q["tau_s_per_step"], 0.01)
        self.assertAlmostEqual(q["BW_GB_per_s"], 200.0)
        self.assertAlmostEqual(q["e_printed_j_per_token"], 2.0)
        self.assertEqual(q["printed_label"], bt.PER_TOKEN_LABEL)
        self.assertAlmostEqual(q["e_half_width_j_per_step"], 24.0 / 512)


class BatteryWorkedExamples(unittest.TestCase):
    @staticmethod
    def stream():
        # 1 V makes signed powers exactly -current_mA/1000 W. Decode [4,8)
        # has 2,4,2,4 W; own idle [0,2) charges at -1 W. All values/results
        # below are exact binary fractions, so equality (no bar) is intended.
        powers = {0: -1, 1: -1, 4: 2, 5: 4, 6: 2, 7: 4, 8: 3, 9: 5, 10: 7}
        return {"poll_ns": [t * 10**9 for t in range(15)],
                "smc": [{"B0AC": -1000 * powers.get(t, 0), "B0AV": 1000} for t in range(15)]}

    def test_signed_bases_and_two_forward_edges_have_closed_form_values(self):
        got = bt.battery_phase(self.stream(), [4 * 10**9, 8 * 10**9], [0, 2 * 10**9])
        # Decode 4*3=12 J; subtract own charging idle -> 12-(-1)*4=16 J.
        # tau=1+1+1=3 s; T/n=1 s. Forward sums are 2+4+2=8 and 3+5+7=15 J.
        for key, value in {"battery_gross_j": 12, "battery_secondary_j": 16,
                           "battery_idle_power_w": -1, "battery_v_start_j": 8,
                           "battery_v_end_j": 15, "battery_phase_edge_j": 23,
                           "battery_tau_s": 3, "battery_poll_interval_max_s": 1,
                           "battery_n": 4, "battery_n_idle": 2}.items():
            self.assertEqual(got[key], value, key)
        self.assertIs(got["decode_battery_assist"], True)
        self.assertIs(got["battery_end_window_complete"], True)

    def test_partial_voltage_poll_is_not_integrated_but_its_current_marks_assist(self):
        stream = self.stream()
        for values in stream["smc"]:
            values["B0AC"] = 0
        stream["smc"][7] = {"B0AC": -2000, "B0AV": None}
        got = bt.battery_phase(stream, [4 * 10**9, 8 * 10**9], [0, 2 * 10**9])
        self.assertEqual((got["battery_gross_j"], got["battery_n"]), (0, 3))
        self.assertIs(got["decode_battery_assist"], True)
        for t in (4, 5, 6):
            stream["smc"][t]["B0AV"] = None
        stream.pop("_battery_data")
        self.assertIsNone(bt.battery_phase(stream, [4 * 10**9, 8 * 10**9], [0, 2 * 10**9]))
        self.assertIs(bt.battery_marker(stream, [4 * 10**9, 8 * 10**9]), True)

    def test_delay_uses_polls_outside_the_phase_and_marker_is_half_open(self):
        stream = self.stream()
        # Remove receive times 12 and 13: the largest interval is 3 s outside
        # decode. BAT-2's average+hold adds exactly 2 s, giving tau=5 s.
        for key in ("poll_ns", "smc"):
            stream[key] = [v for i, v in enumerate(stream[key]) if i not in (12, 13)]
        self.assertEqual(bt.battery_data(stream)[3], 5)
        stream = self.stream()
        for values in stream["smc"]:
            values["B0AC"] = 0
        stream["smc"][6]["B0AC"] = stream["smc"][11]["B0AC"] = -1000
        self.assertIs(bt.battery_marker(stream, [4 * 10**9, 8 * 10**9]), False)
        stream["smc"][7]["B0AC"] = -1000
        self.assertIs(bt.battery_marker(stream, [4 * 10**9, 8 * 10**9]), True)

    def test_empty_meter_batches_retain_ordered_current_polls_without_a_clock_fit(self):
        records = [{"k": "h", "rate_idx": synth.RATE_IDX, "start_raw_ns": 10 * 10**9,
                    "start_mono_ns": 9 * 10**9}]
        for second in (13, 11, 12):
            records.append({"k": "b", "rx": second * 10**9, "n": 0, "p": "",
                            "smc": {"B0AC": -1000 if second == 13 else 0,
                                    "B0AV": None if second == 13 else 1000}})
        records.append({"k": "t", "end_raw_ns": 20 * 10**9, "end_mono_ns": 19 * 10**9})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stream.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in records))
            stream = bt.parse_meter_stream(path)
        self.assertIs(stream["aligned"], False)
        self.assertEqual(stream["raw_offset_ns"], 10**9)
        self.assertEqual(stream["poll_ns"], [11 * 10**9, 12 * 10**9, 13 * 10**9])
        # Raw decode [10,12), delay 3 s -> marker [13,15). The incomplete
        # voltage at 13 s still marks assist; no meter fit is needed.
        self.assertIs(bt.battery_marker(stream, [10 * 10**9, 12 * 10**9]), True)


class StudentTTests(unittest.TestCase):
    def test_exact_quantiles_of_the_analysis_plan(self):
        for df, expected in ((9, 2.262157162798205), (8, 2.306004135204166), (7, 2.364624251592785),
                             (6, 2.446911851), (5, 2.570581836), (4, 2.776445105)):
            self.assertAlmostEqual(bt.t_quantile(0.975, df), expected, places=8)

    def test_d8_block5_three_decimal_table_reproduced(self):
        for df, value in ((9, 2.262), (8, 2.306), (7, 2.365), (6, 2.447), (5, 2.571), (4, 2.776), (11, 2.201)):
            self.assertEqual(bt.student_t_critical_95(df), value)
        # Every listed value is the exact two-sided 95% quantile rounded to three decimals (the
        # table's own precision), so the reproduction is pinned to the arithmetic, not copied blind.
        self.assertEqual(sorted(bt.T_TABLE_95), [*range(1, 31), 40, 60, 120])
        for df, value in bt.T_TABLE_95.items():
            self.assertEqual(value, round(bt.t_quantile(0.975, df), 3), df)
        # Block 5's floor rule for an unlisted df: the largest listed df below it.
        self.assertEqual(bt.student_t_critical_95(35), 2.042)
        self.assertEqual(bt.student_t_critical_95(59), 2.021)
        self.assertEqual(bt.student_t_critical_95(121), 1.980)
        self.assertEqual(bt.student_t_critical_95(1000), 1.980)
        with self.assertRaises(ValueError):
            bt.student_t_critical_95(0)

    def test_bonferroni_level_is_wider_than_95(self):
        self.assertGreater(bt.t_two_sided(0.05 / 21, 9), bt.t_two_sided(0.05, 9))
        self.assertAlmostEqual(bt.t_cdf(bt.t_two_sided(0.05 / 21, 9), 9), 1 - 0.05 / 42, places=12)


def members(values, bounds, prefix):
    return [{"id": f"{prefix}{i}", "E": e, "T": 1.0, "bounds": dict(bounds)} for i, e in enumerate(values, 1)]


def quads(values, bounds, prefix):
    return [{"id": f"{prefix}{i}", "members": members([e] * 4, bounds, f"{prefix}{i}m")} for i, e in enumerate(values, 1)]


class PhaseEstimateTests(unittest.TestCase):
    R = [10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8, 10.1, 10.0, 9.6]
    B = [10.4, 10.1, 10.3, 10.2, 10.5, 10.0, 10.2, 10.3, 10.1, 9.9]
    KINDS = ("k1", "k2", "k3")
    BOUNDS = {"k1": 0.010, "k2": 0.0, "k3": 0.050}

    def test_worked_example_all_units_kept(self):
        cell = bt.phase_estimate(members(self.R, self.BOUNDS, "r"), quads(self.B, self.BOUNDS, "q"), self.KINDS)
        self.assertEqual(cell["status"], "ok")
        self.assertAlmostEqual(cell["mean_j"], 10.16, places=12)
        self.assertAlmostEqual(cell["h95_j"], 0.10833, places=5)
        self.assertAlmostEqual(cell["B_j"], 0.060, places=12)
        self.assertAlmostEqual(cell["lower95_j"], 9.9917, places=4)
        self.assertAlmostEqual(cell["upper95_j"], 10.3283, places=4)
        self.assertAlmostEqual(cell["per_token_j"], 0.019844, places=6)
        self.assertEqual(cell["df"], 9)

    def test_worked_example_units_removed(self):
        reps = [m for m in members(self.R, self.BOUNDS, "r") if m["id"] != "r6"]
        qs = [q for q in quads(self.B, self.BOUNDS, "q") if q["id"] not in ("q5", "q9")]
        cell = bt.phase_estimate(reps, qs, self.KINDS)
        self.assertEqual((cell["n_r"], cell["n_b"], cell["df"]), (9, 8, 7))
        self.assertAlmostEqual(cell["mean_j"], 10.13333, places=5)
        self.assertAlmostEqual(cell["h95_j"], 0.11519, places=5)
        self.assertAlmostEqual(cell["lower95_j"], 9.9581, places=4)
        self.assertAlmostEqual(cell["upper95_j"], 10.3085, places=4)
        self.assertAlmostEqual(cell["per_token_j"], 0.019792, places=6)

    def test_family_alpha_widens_only_h(self):
        full = bt.phase_estimate(members(self.R, self.BOUNDS, "r"), quads(self.B, self.BOUNDS, "q"), self.KINDS)
        wide = bt.phase_estimate(members(self.R, self.BOUNDS, "r"), quads(self.B, self.BOUNDS, "q"), self.KINDS,
                                 alpha=0.05 / 21)
        self.assertEqual(full["mean_j"], wide["mean_j"])
        self.assertEqual(full["B_j"], wide["B_j"])
        self.assertGreater(wide["h_j"], full["h_j"])
        self.assertAlmostEqual(wide["h_j"], bt.h_at(full, 0.05 / 21), places=12)

    def test_below_minimum_and_missing_kind_refuse(self):
        reps = members(self.R[:4], self.BOUNDS, "r")
        self.assertEqual(bt.phase_estimate(reps, quads(self.B, self.BOUNDS, "q"), self.KINDS)["status"],
                         "refused_below_minimum")
        cell = bt.phase_estimate(members(self.R, self.BOUNDS, "r"), quads(self.B, self.BOUNDS, "q"), ("k1", "k9"))
        self.assertEqual(cell["status"], "refused_bound_kind_missing")

    def test_stratified_mean_not_plain_mean_when_units_removed(self):
        reps = [m for m in members(self.R, self.BOUNDS, "r") if m["id"] != "r6"]
        qs = [q for q in quads(self.B, self.BOUNDS, "q") if q["id"] not in ("q5", "q9")]
        cell = bt.phase_estimate(reps, qs, self.KINDS)
        plain = (sum(self.R) - 10.3 + 4 * (sum(self.B) - 10.5 - 10.1)) / 41
        self.assertNotAlmostEqual(cell["mean_j"], plain, places=4)
        self.assertAlmostEqual(plain, 10.12927, places=5)


class Neg8Tests(unittest.TestCase):
    def test_count_adjusted_bound_by_hand(self):
        bound = bt.neg8_bound([1, 2, 3, 4, 5, 6], 2, 2)
        self.assertAlmostEqual(bound["envelope_j"], 4.0)
        expected = 2.571 * 1.8708286933869707 * math.sqrt(1.0)   # Addendum 7 D8: the three-decimal table
        self.assertAlmostEqual(bound["prediction_j"], expected, places=9)
        self.assertNotAlmostEqual(bound["prediction_j"], bt.t_quantile(0.975, 5) * 1.8708286933869707, places=9)
        self.assertAlmostEqual(bound["bound_j"], max(4.0, expected), places=9)
        self.assertIsNone(bt.neg8_bound([1.0], 1, 1))

    def test_allowance_from_session_rows(self):
        def row(role, index, e, dur=2.0):
            return {"role": role, "order_index": index, "status": "succeeded", "excluded": False, "run_id": f"{role}{index}",
                    "gross_energy_j": e, "dur_tokenize_s": 0, "dur_generation_setup_s": 0, "dur_prefill_s": dur / 2,
                    "dur_decode_s": dur / 2}
        rows = [row("corpus", i, 37.0 + 0.1 * i) for i in range(18)]
        rows += [row("start", 20 + i, 37.5) for i in range(3)] + [row("midpoint", 30, 38.3)] + [row("end", 40 + i, 37.6) for i in range(3)]
        record = bt.neg8_allowance(rows)
        self.assertEqual(record["status"], "ok")
        self.assertEqual(record["corpus_n"], 12)           # the desk cap
        self.assertAlmostEqual(record["trajectory_excursion_j"], 0.8, places=9)
        self.assertEqual(record["allowance_j"], max(0.8, record["bound_terms"]["bound_j"]))
        self.assertAlmostEqual(record["T_ref_s"], 2.0)
        lost = [r for r in rows if r["role"] != "midpoint"]
        self.assertTrue(bt.neg8_allowance(lost)["midpoint_lost"])
        self.assertAlmostEqual(bt.neg8_allowance(lost)["trajectory_excursion_j"], 0.1, places=9)
        self.assertEqual(bt.neg8_allowance(rows[:5])["status"], "undefined_references_insufficient")


class RegressionTests(unittest.TestCase):
    def test_exact_line(self):
        fit = bt.ols([[1], [2], [4]], [3.0, 5.0, 9.0])
        self.assertAlmostEqual(fit["coef"][0], 1.0)
        self.assertAlmostEqual(fit["coef"][1], 2.0)
        self.assertAlmostEqual(fit["s2"], 0.0)
        self.assertAlmostEqual(bt.ols_predict(fit, [10])["yhat"], 21.0)

    def test_simple_regression_against_textbook_formulas(self):
        xs, ys = [1, 2, 3, 4, 5], [2.1, 3.9, 6.2, 7.8, 10.1]
        fit = bt.ols([[x] for x in xs], ys)
        mx, my = sum(xs) / 5, sum(ys) / 5
        sxx = sum((x - mx) ** 2 for x in xs)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
        rss = sum((y - (my - slope * mx) - slope * x) ** 2 for x, y in zip(xs, ys))
        se = math.sqrt(rss / 3 / sxx)
        interval = bt.coef_interval(fit, 1, 0.05)
        self.assertAlmostEqual(interval["value"], slope, places=12)
        self.assertAlmostEqual(interval["ols"]["half_width"], bt.t_quantile(0.975, 3) * se, places=12)

    def test_d1_hc3_covariance_by_hand_and_ols_printed_beside(self):
        xs, ys = [1, 2, 3, 4, 5, 6], [1.0, 2.3, 2.9, 4.4, 4.9, 6.6]
        fit = bt.ols([[x] for x in xs], ys)
        n = len(xs)
        design = [[1.0, float(x)] for x in xs]
        inv = fit["xtx_inv"]
        meat = [[0.0, 0.0], [0.0, 0.0]]
        for i in range(n):
            h = sum(design[i][a] * inv[a][b] * design[i][b] for a in range(2) for b in range(2))
            w = (fit["residuals"][i] / (1 - h)) ** 2
            for a in range(2):
                for b in range(2):
                    meat[a][b] += design[i][a] * w * design[i][b]
        expected = [[sum(inv[a][c] * meat[c][d] * inv[d][b] for c in range(2) for d in range(2)) for b in range(2)] for a in range(2)]
        for a in range(2):
            for b in range(2):
                self.assertAlmostEqual(fit["cov_hc3"][a][b], expected[a][b], places=12)
        interval = bt.coef_interval(fit, 1, 0.05)
        self.assertEqual(interval["se_method"], "HC3")
        self.assertAlmostEqual(interval["half_width"], bt.t_quantile(0.975, 4) * math.sqrt(expected[1][1]), places=12)
        self.assertEqual(interval["ols"]["se_method"], "OLS")
        self.assertAlmostEqual(interval["ols"]["half_width"], bt.t_quantile(0.975, 4) * math.sqrt(fit["cov"][1][1]), places=12)
        pred = bt.ols_predict(fit, [7])
        var = sum([1.0, 7.0][a] * expected[a][b] * [1.0, 7.0][b] for a in range(2) for b in range(2))
        self.assertAlmostEqual(pred["se_pred_hc3"], math.sqrt(var + fit["s2"]), places=12)
        self.assertAlmostEqual(pred["se_mean_hc3"], math.sqrt(var), places=12)

    def test_two_regressors(self):
        rows = [[1, 1], [2, 1], [3, 2], [4, 3], [5, 5], [6, 8]]
        ys = [2 + 3 * a + 0.5 * b for a, b in rows]
        fit = bt.ols(rows, ys)
        for value, expected in zip(fit["coef"], (2, 3, 0.5)):
            self.assertAlmostEqual(value, expected, places=9)


class H1Tests(unittest.TestCase):
    def points(self):
        return {"a": {"x": {"bytes": 1.0, "resident": 1.0, "time": 1.0}, "e": 1.0, "w": 0.1, "kind": "fit"},
                "b": {"x": {"bytes": 2.0, "resident": 2.0, "time": 1.5}, "e": 2.0, "w": 0.1, "kind": "fit"},
                "c": {"x": {"bytes": 4.0, "resident": 4.0, "time": 2.0}, "e": 4.0, "w": 0.1, "kind": "fit"}}

    def test_corner_interval_brackets_the_central_line(self):
        lines = bt.h1_lines(self.points())
        self.assertEqual(len(lines["bytes"]["corners"]), 8)
        pred = bt.h1_predict(lines, "bytes", 10.0)
        self.assertAlmostEqual(pred["central"], 10.0, places=9)
        self.assertLess(pred["lower"], 10.0)
        self.assertGreater(pred["upper"], 10.0)
        # The all-up and all-down corners shift the whole line by exactly w, so the interval is at
        # least 2w wide, and mixed corners tilt it further out at x far from the fit points.
        self.assertGreaterEqual(pred["upper"], 10.1 - 1e-9)
        self.assertLessEqual(pred["lower"], 9.9 + 1e-9)
        self.assertGreater(pred["upper"] - pred["lower"], 0.2)
        near = bt.h1_predict(lines, "bytes", 2.0)
        self.assertLess(near["upper"] - near["lower"], pred["upper"] - pred["lower"])

    def test_words_and_active_answer(self):
        fit = self.points()
        held = {**fit}
        # a MoE model: few bytes, large resident, slow: bytes line matches, resident far above.
        for name in bt.MOE:
            held[name] = {"x": {"bytes": 2.0, "resident": 40.0, "time": 1.9}, "e": 2.0, "w": 0.15, "kind": "moe"}
        held["qwen3-14b-4bit"] = {"x": {"bytes": 8.0, "resident": 8.0, "time": 3.0}, "e": 8.0, "w": 0.2, "kind": "dense"}
        lines = bt.h1_lines(fit)
        words = bt.h1_words(lines, held)
        for name in bt.MOE:
            self.assertEqual(words["models"][name]["word"], "bytes")
            self.assertEqual(words["models"][name]["checks"]["resident"]["miss"], "prediction_above")
            self.assertAlmostEqual(words["models"][name]["checks"]["bytes"]["ln_measured_over_predicted"], 0.0, places=9)
        self.assertEqual(words["active_or_resident"]["answer"], "active")
        self.assertEqual(words["models"]["qwen3-14b-4bit"]["word"], "unresolved")
        self.assertIsNone(words["models"]["a"]["word"])

    def test_neither_and_mixed(self):
        lines = bt.h1_lines(self.points())
        held = dict(self.points())
        held["qwen3-30b-a3b-4bit"] = {"x": {"bytes": 2.0, "resident": 40.0, "time": 1.9}, "e": 20.0, "w": 0.1, "kind": "moe"}
        words = bt.h1_words(lines, held)
        self.assertEqual(words["models"]["qwen3-30b-a3b-4bit"]["word"], "neither")
        self.assertEqual(words["active_or_resident"]["answer"], "mixed")
        self.assertTrue(words["active_or_resident"]["misses"])


class DeskBundleReadTests(unittest.TestCase):
    def test_missing_files_keep_existing_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            self.assertEqual(bt.read_json(bundle / "metadata.json", {"missing": True}), {"missing": True})
            self.assertIsNone(bt.member_spans(bundle))

    @unittest.skipUnless(shutil.which("zstd"), "compressed twin reader requires zstd on PATH")
    def test_compressed_json_and_events_and_plain_precedence(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            metadata = {"uncertainty_evidence": {"clock_anchor": {"clock_stamps": {
                "sampling_started": {"epoch_s": 2000, "monotonic_before_s": 1000}}}}}
            events = [{"event_type": "phase_start", "phase": "decode", "timestamp_s": 2000},
                      {"event_type": "phase_end", "phase": "decode", "timestamp_s": 2001}]
            for name, text in (("metadata.json", json.dumps(metadata)),
                               ("events.jsonl", "".join(json.dumps(e) + "\n" for e in events))):
                path = bundle / name
                path.write_text(text, encoding="utf-8")
                subprocess.run(["zstd", "-q", str(path), "-o", str(path) + ".zst"], check=True)
                path.unlink()
            self.assertEqual(bt.read_json(bundle / "metadata.json"), metadata)
            # Exact integer ns: one second after the 1000 s monotonic anchor.
            self.assertEqual(bt.member_spans(bundle), {
                "decode_ns": [1_000_000_000_000, 1_001_000_000_000],
                "request_ns": [1_000_000_000_000, 1_001_000_000_000], "idle_ns": None})
            (bundle / "metadata.json").write_text('{"plain":true}', encoding="utf-8")
            self.assertEqual(bt.read_json(bundle / "metadata.json"), {"plain": True})

    @unittest.skipUnless(shutil.which("zstd"), "compressed twin reader requires zstd on PATH")
    def test_existing_unreadable_compressed_files_refuse_instead_of_defaulting(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "metadata.json.zst").write_bytes(b"not a zstd frame")
            with self.assertRaisesRegex(RuntimeError, "compressed file unreadable: "):
                bt.read_json(bundle / "metadata.json", {"missing": True})
            with self.assertRaisesRegex(RuntimeError, "compressed file unreadable: "):
                bt.member_spans(bundle)
            (bundle / "metadata.json").write_text(json.dumps({"uncertainty_evidence": {
                "clock_anchor": {"clock_stamps": {"sampling_started": {
                    "epoch_s": 2000, "monotonic_before_s": 1000}}}}}), encoding="utf-8")
            (bundle / "events.jsonl.zst").write_bytes(b"not a zstd frame")
            with self.assertRaisesRegex(RuntimeError, "compressed file unreadable: "):
                bt.member_spans(bundle)
            # Analysis marks these runs unusable; the independent twin refuses
            # under D7, as it does for a truncated plain events.jsonl.
            for name in ("metadata.json", "events.jsonl"):
                path = bundle / name
                raw = path.read_bytes() if path.exists() else None
                for payload in (b"\xff", b"not JSON"):
                    with self.subTest(name=name, payload=payload):
                        result = subprocess.run(["zstd", "-qc"], input=payload,
                                                capture_output=True, check=True)
                        Path(str(path) + ".zst").write_bytes(result.stdout)
                        path.unlink(missing_ok=True)
                        with self.assertRaises((RuntimeError, ValueError)):
                            bt.read_json(path) if name == "metadata.json" else bt.member_spans(bundle)
                if raw is not None:
                    path.write_bytes(raw)

    def test_present_plain_files_refuse_read_and_parse_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.json"
            for payload in (b"\xff", b"not JSON"):
                with self.subTest(payload=payload):
                    path.write_bytes(payload)
                    with self.assertRaises(ValueError):
                        bt.read_json(path, {"missing": True})
            with patch.object(Path, "read_text", side_effect=PermissionError("unreadable")):
                with self.assertRaises(PermissionError):
                    bt.read_json(path, {"missing": True})

    @unittest.skipUnless(shutil.which("zstd"), "compressed twin reader requires zstd on PATH")
    def test_present_non_file_compressed_sibling_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.json"
            Path(str(path) + ".zst").mkdir()
            with self.assertRaisesRegex(RuntimeError, "compressed file unreadable: "):
                bt.read_json(path, {"missing": True})

    def test_compressed_reader_resolves_path_or_homebrew_fallback_independently(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.json"
            Path(str(path) + ".zst").write_bytes(b"synthetic frame; subprocess mocked")
            for executable in ("/synthetic/bin/zstd", None):
                with self.subTest(executable=executable), \
                        patch.object(shutil, "which", return_value=executable), \
                        patch.object(bt.subprocess, "run", return_value=subprocess.CompletedProcess(
                            [], 0, stdout=b'{}')) as run:
                    self.assertEqual(bt.read_json(path), {})
                    self.assertEqual(run.call_args.args[0],
                                     [executable or "/opt/homebrew/bin/zstd", "-dc", str(path) + ".zst"])

    def test_present_compressed_file_refuses_when_zstd_cannot_execute(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            for name in ("metadata.json", "events.jsonl"):
                path = bundle / name
                compressed = Path(str(path) + ".zst")
                compressed.write_bytes(b"synthetic frame; subprocess mocked")
                for error in (FileNotFoundError("zstd"), PermissionError("zstd")):
                    with self.subTest(name=name, error=type(error).__name__), \
                            patch.object(shutil, "which", return_value=None), \
                            patch.object(bt.subprocess, "run", side_effect=error):
                        with self.assertRaisesRegex(RuntimeError, "zstd unavailable: ") as caught:
                            bt.read_json(path) if name == "metadata.json" else bt.member_spans(bundle)
                        self.assertEqual(str(caught.exception), "zstd unavailable: " + str(compressed))
                # Supply the anchor for the events reader, without a decompressor.
                if name == "metadata.json":
                    path.write_text(json.dumps({"uncertainty_evidence": {"clock_anchor": {
                        "clock_stamps": {"sampling_started": {
                            "epoch_s": 2000, "monotonic_before_s": 1000}}}}}), encoding="utf-8")


class MeterTests(unittest.TestCase):
    def test_integrate_mean_power_times_duration(self):
        times = [0, 1_000_000_000, 2_000_000_000, 3_000_000_000]
        energy, n = bt.integrate(times, [1.0, 2.0, 3.0, 4.0], 0, 2_000_000_000)
        self.assertEqual((energy, n), (3.0, 2))
        self.assertEqual(bt.integrate(times, [1.0, 2.0, 3.0, 4.0], 5_000_000_000, 6_000_000_000), (None, 0))
        with self.assertRaises(ValueError):
            bt.integrate(times, [1.0], 2, 1)

    def test_synthetic_stream_parses_and_aligns(self):
        archive = next(iter(sorted((WORLD["one"] / "archives").iterdir())))
        stream = bt.parse_meter_stream(archive / "sources/night-custody/hazards/meter/stream-001.jsonl")
        self.assertTrue(stream["aligned"])
        self.assertEqual(stream["raw_offset_ns"], synth.RAW_MINUS_MONO_NS)
        self.assertLess(abs(stream["fit"]["clock_rate_ppm"]), 1.0)
        self.assertEqual(stream["host_ns"], sorted(stream["host_ns"]))
        # Addendum 7 item 12: the generator's polls carry 1 to 3.5 ms of latency, so r_max is non-zero
        # and absolute: at least the largest positive and the largest negative excess.
        fit = stream["fit"]
        self.assertGreater(fit["excess_latency_ms_absmax"], 1.0)
        self.assertGreaterEqual(fit["excess_latency_ms_absmax"], fit["excess_latency_ms_max"])
        self.assertGreaterEqual(fit["excess_latency_ms_absmax"], -fit["excess_latency_ms_min"])

    def test_d4_edge_power_is_the_larger_adjacent_sample(self):
        times = [0, 1_000_000_000, 2_000_000_000, 3_000_000_000, 4_000_000_000]
        watts = [5.0, 1.0, 9.0, 2.0, 7.0]
        # start edge between samples 1 (1.0) and 2 (9.0); end edge between samples 3 (2.0) and 4 (7.0)
        self.assertEqual(bt.edge_powers(times, watts, [1_500_000_000, 3_500_000_000]), (9.0, 7.0))
        # an edge exactly on a sample: the start edge's neighbours are the sample before and the sample
        # at it (1.0, 9.0); the end edge's are the last inside and the first outside (9.0, 2.0)
        self.assertEqual(bt.edge_powers(times, watts, [2_000_000_000, 3_000_000_000]), (9.0, 9.0))
        self.assertEqual(bt.edge_powers(times, watts, [0, 4_000_000_000]), (5.0, 7.0))

    def test_n1_span_ends_round_to_nearest_ns(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "metadata.json").write_text(json.dumps({"uncertainty_evidence": {"clock_anchor": {"clock_stamps": {
                "sampling_started": {"epoch_s": 2000.0, "monotonic_before_s": 1000.0}}}}}))
            events = [{"event_type": "phase_start", "phase": "prefill", "timestamp_s": 2000.0},
                      {"event_type": "phase_start", "phase": "decode", "timestamp_s": 2000.0000000006},
                      {"event_type": "phase_end", "phase": "decode", "timestamp_s": 2001.0000000004}]
            (bundle / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
            spans = bt.member_spans(bundle)
        self.assertEqual(spans["decode_ns"], [1_000_000_000_001, 1_001_000_000_000])
        self.assertEqual(spans["request_ns"][0], 1_000_000_000_000)

    def test_dc_join_recovers_the_decode_energy(self):
        archive_root = next(iter(sorted((WORLD["one"] / "archives").iterdir())))
        archive = bt.load_archive(archive_root)
        roster = json.loads((archive_root / "derived/roster.json").read_text())
        run_id = next(m["run_id"] for m in roster["members"] if m["role"] == "science")
        joined = bt.dc_join(archive, run_id)
        self.assertEqual(joined["status"], "ok")
        summary = json.loads((archive_root / "withheld/reductions" / (run_id + ".summary_metrics.rereduced.json")).read_text())
        rails = summary["phase_energy_j"]["decode"]
        truth = WORLD["truth_one"]
        config = json.loads((archive_root / "sources/claim-runs" / run_id / "config.json").read_text())
        resident = truth["models"][config["model"]["name"]]["R_GB"]
        expected_power = (truth["DC_BASE_w"] + truth["DC_GAIN"] * rails / summary["decode_latency_s"]
                          + truth["REST_PER_RESIDENT_W_PER_GB"] * resident)
        self.assertGreater(expected_power, truth["DC_BASE_w"])
        self.assertAlmostEqual(joined["mean_power_w"] / expected_power, 1.0, delta=0.03)
        self.assertAlmostEqual(joined["idle_power_w"], truth["DC_IDLE_W"], delta=0.1)
        self.assertGreaterEqual(joined["edge_bound_j"], 0.0)

    def test_item3_edge_term_is_edge_powers_times_r_max_plus_dt(self):
        archive_root = next(iter(sorted((WORLD["one"] / "archives").iterdir())))
        archive = bt.load_archive(archive_root)
        roster = json.loads((archive_root / "derived/roster.json").read_text())
        run_id = next(m["run_id"] for m in roster["members"] if m["role"] == "science")
        joined = bt.dc_join(archive, run_id)
        terms = joined["edge_terms"]
        self.assertAlmostEqual(joined["edge_bound_j"],
                               (terms["P_start_w"] + terms["P_end_w"]) * (terms["r_max_s"] + terms["dt_meter_s"]), places=12)
        self.assertAlmostEqual(terms["dt_meter_s"], synth.STEP_MS / 1e3)
        self.assertAlmostEqual(terms["r_max_s"], joined["clock_fit"]["excess_latency_ms_absmax"] / 1e3)
        self.assertGreater(terms["r_max_s"], 0.001)
        self.assertIn("request_energy_j", joined)
        self.assertGreater(joined["request_energy_j"], joined["decode_energy_j"])
        self.assertGreater(terms["P_start_w"], 0.0)
        self.assertGreater(terms["P_end_w"], 0.0)
        # The edge term is a two-edge bound: both edge powers enter, and it is positive even with no jitter.
        self.assertGreaterEqual(joined["edge_bound_j"], (terms["P_start_w"] + terms["P_end_w"]) * terms["dt_meter_s"])


class BlindingTests(unittest.TestCase):
    def test_config_filename_and_factor_product(self):
        import hashlib
        self.assertEqual(bt.config_filename("k"), "config-" + hashlib.sha256(b"k").hexdigest()[:16] + ".json")
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "pack.json").write_text('{"factor": 1.1}')
            Path(tmp, bt.config_filename("k")).write_text('{"factor": 0.99}')
            self.assertAlmostEqual(bt.stored_factor(tmp, "k"), 1.1 * 0.99)
            with self.assertRaises(ValueError):
                bt.stored_factor(tmp, "other")

    def test_unblind_row_degrees(self):
        row = {"phase_decode_j": 2.0, "idle_power_w": 4.0, "idle_variance_of_mean_w2": 8.0, "dur_decode_s": 3.0, "run_id": "x"}
        out = bt.unblind_row(row, 2.0)
        self.assertEqual((out["phase_decode_j"], out["idle_power_w"], out["idle_variance_of_mean_w2"], out["dur_decode_s"]),
                         (1.0, 2.0, 2.0, 3.0))
        self.assertTrue(out["_unblinded"])

    def test_d7_release_only_from_the_key_directory_and_refusals_print(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "x.runs.csv")
            path.write_text("run_id,config_key,non_claim,phase_decode_j\nr,k,True,2.0\n")
            rows = bt.read_export(path)
            self.assertFalse(rows[0]["_unblinded"])          # the non_claim column releases nothing
            self.assertEqual(bt.unblind(rows, tmp, set())[0]["phase_decode_j"], 2.0)
            with self.assertRaises(ValueError):
                bt.unblind(rows, tmp, {"k"})                  # no key: a refusal, not a release
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = bt.main(["--export", str(path), "--manifest", str(WORLD["one"] / "bytes_manifest.json"),
                                "--key-dir", tmp, "--stage", "2", "--out", str(Path(tmp, "o.json"))])
            self.assertEqual(code, 1)
            self.assertTrue(out.getvalue().startswith("refused: "))
            self.assertNotIn("Traceback", out.getvalue())
            self.assertFalse(Path(tmp, "o.json").exists())


class ManifestTests(unittest.TestCase):
    def test_dict_and_list_forms(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "m.json")
            path.write_text(json.dumps({"models": {"mlx-community/Qwen3-8B-4bit": {"W_bytes": 4e9, "KV_bytes": 3e8, "R_bytes": 4.6e9}}}))
            m = bt.read_manifest(path)
            self.assertAlmostEqual(m["qwen3-8b-4bit"]["b_GB"], 4.3)
            self.assertAlmostEqual(m["qwen3-8b-4bit"]["R_GB"], 4.6)
            path.write_text(json.dumps([{"model": "Qwen3-4B-4bit", "W_GB": 2.0, "KV_GB": 0.5, "R_GB": 2.1}]))
            m = bt.read_manifest(path)
            self.assertAlmostEqual(m["qwen3-4b-4bit"]["b_GB"], 2.5)
        self.assertEqual(bt.canon("mlx-community/Qwen3_8B-4bit"), "qwen3-8b-4bit")
        self.assertEqual(bt.canon("Qwen3.5-122B-A10B-4bit (pinned jw_models copy, read only)"), "qwen3.5-122b-a10b-4bit")


class SyntheticWorldTests(unittest.TestCase):
    """One pass with defects: a thermal exclusion, a failed quad member and an assist flag on 4B and 30B-A3B."""

    @classmethod
    def setUpClass(cls):
        cls.result = run_twin(WORLD["one"], "2")
        cls.truth = WORLD["truth_one"]

    def truth_of(self, model):
        return next(v for k, v in self.truth["models"].items() if bt.canon(k) == model)

    def test_every_model_every_boundary_has_a_cell(self):
        self.assertEqual(sorted(self.result["cells"]), sorted(bt.ROSTER))
        for model, block in self.result["cells"].items():
            cell = block["pass1"]
            self.assertEqual(set(cell["dc_join_status"].values()), {"ok"}, model)
            for boundary in bt.BOUNDARIES:
                self.assertEqual(cell["boundaries"][boundary]["gross"]["status"], "ok", (model, boundary))

    def test_rails_energy_per_step_matches_the_truth(self):
        for model, block in self.result["cells"].items():
            q = block["pass1"]["boundaries"]["rails"]["quantities"]["gross"]
            expected = self.truth["S_BYTES_j_per_GB"] * self.truth_of(model)["b_GB"]
            self.assertAlmostEqual(q["e_j_per_step"] / expected, 1.0, delta=0.005, msg=model)
            self.assertLess(q["e_lower_j_per_step"], expected)
            self.assertGreater(q["e_upper_j_per_step"], expected)
            self.assertAlmostEqual(q["e_printed_j_per_token"] * bt.PRINTED_TOKENS, q["E_dec_j"], places=9)

    def test_rest_is_dc_minus_rails_and_idle_lines_are_lower(self):
        for model, block in self.result["cells"].items():
            b = block["pass1"]["boundaries"]
            rails, dc, rest = (b[k]["quantities"]["gross"] for k in bt.BOUNDARIES)
            self.assertAlmostEqual(rest["E_dec_j"], dc["E_dec_j"] - rails["E_dec_j"], places=6)
            for k in bt.BOUNDARIES:
                self.assertLess(b[k]["quantities"]["idle_subtracted"]["E_dec_j"], b[k]["quantities"]["gross"]["E_dec_j"])
            self.assertAlmostEqual(b["rails"]["gross"]["B_j"], sum(b["rails"]["gross"]["kind_averages_j"].values()), places=9)
            self.assertEqual(set(b["rails"]["gross"]["kind_averages_j"]), set(bt.RAILS_KINDS))
            self.assertEqual(set(b["dc_input"]["gross"]["kind_averages_j"]), set(bt.DC_KINDS))
            self.assertEqual(set(b["rest"]["gross"]["kind_averages_j"]), set(bt.REST_KINDS))

    def test_defects_change_kept_units_and_secondary_lines(self):
        cell = self.result["cells"]["qwen3-4b-4bit"]["pass1"]["boundaries"]["rails"]
        self.assertEqual((cell["gross"]["n_r"], cell["gross"]["n_b"]), (8, 8))
        self.assertEqual(cell["gross"]["df"], 7)
        # BAT-2: this world plants only a harvest flag, while every SMC
        # current remains zero. The flag alone selects no diagnostic unit.
        self.assertNotIn("without_assisted", cell)
        self.assertEqual(cell["harvest_assisted_member_counts"], {"repeat": 1, "quad": 0})
        codes = {r["codes"]: r["restorable"] for r in cell["removed_members"]}
        self.assertEqual(codes, {"thermal.os_level_nonzero": True, "member.status_not_succeeded": False,
                                 "battery.member_span": True, "member.cooldown_cap_hit": True})

    def test_item8_flagged_inclusive_restores_hazard_exclusions_with_valid_records_only(self):
        cell = self.result["cells"]["qwen3-4b-4bit"]["pass1"]["boundaries"]["rails"]
        # the thermal and cooldown repeats and the battery.member_span quad member come back (D5:
        # NUMBER class included); the failed quad member never does
        self.assertEqual((cell["flagged_inclusive"]["n_r"], cell["flagged_inclusive"]["n_b"]), (10, 9))
        restored = set(cell["flagged_inclusive"]["kept_repeat_ids"]) - set(cell["gross"]["kept_repeat_ids"])
        self.assertEqual(restored, {"p1-s1-m-qwen3-4b-4bit-abs-r06", "p1-s1-m-qwen3-4b-4bit-abs-r08"})
        self.assertTrue(bt.restorable({"status": "succeeded", "phase_decode_j": 1.0, "dur_decode_s": 1.0,
                                       "exclusion_codes": "member.cooldown_cap_hit"}))
        self.assertFalse(bt.restorable({"status": "succeeded", "phase_decode_j": 1.0, "dur_decode_s": 1.0,
                                        "exclusion_codes": "member.bytes_missing"}))
        self.assertFalse(bt.restorable({"status": "succeeded", "phase_decode_j": 1.0, "dur_decode_s": 1.0,
                                        "exclusion_codes": "member.anchor_not_bounded"}))
        self.assertFalse(bt.restorable({"status": "succeeded", "phase_decode_j": 1.0, "dur_decode_s": 1.0,
                                        "exclusion_codes": "roster.not_in_plan"}))
        self.assertIn("p1-s1-m-qwen3-4b-4bit-b02", cell["flagged_inclusive"]["kept_quad_ids"])
        self.assertNotIn("p1-s1-m-qwen3-4b-4bit-b05", cell["flagged_inclusive"]["kept_quad_ids"])
        self.assertFalse(bt.restorable({"status": "failed", "phase_decode_j": None, "dur_decode_s": 1.0,
                                        "exclusion_codes": "member.status_not_succeeded"}))
        self.assertFalse(bt.restorable({"status": "succeeded", "phase_decode_j": 1.0, "dur_decode_s": 1.0,
                                        "exclusion_codes": "clock.step_overlap;member.token_count_mismatch"}))
        self.assertTrue(bt.restorable({"status": "succeeded", "phase_decode_j": 1.0, "dur_decode_s": 1.0,
                                       "exclusion_codes": "clock.step_overlap;contention.request_overlap"}))

    def test_item3_meter_attribution_floor_is_the_largest_u(self):
        for boundary in ("dc_input", "rest"):
            cell = self.result["cells"]["qwen3-8b-4bit"]["pass1"]["boundaries"][boundary]
            floor = cell["meter_attribution_floor"]
            self.assertEqual(floor["kind"], "E_meter_edge_bound_j")
            self.assertFalse(floor["composed"])
            self.assertGreaterEqual(floor["value_j"], floor["min_j"])
            self.assertGreaterEqual(floor["value_j"], cell["gross"]["kind_averages_j"]["E_meter_edge_bound_j"])
            self.assertIn(floor["member"], cell["gross"]["kept_repeat_ids"] + [m for q in cell["gross"]["members"]["quads"].values() for m in q])
        rails = self.result["cells"]["qwen3-8b-4bit"]["pass1"]["boundaries"]["rails"]
        self.assertEqual(rails["attribution_floor"]["kind"], "E_clock_anchor_shift_bound_j")
        self.assertNotIn("meter_attribution_floor", rails)

    def test_item7_deviation_interval_adds_the_measured_half_width(self):
        h2 = self.result["h2"]["rails"]["pass1"]
        tier = h2["tier"]
        alpha = self.result["multiplicity"]["H2"]["rails"]["pass1"]["alpha_per_interval"]
        points = {m: self.result["cells"][m]["pass1"]["boundaries"]["rails"]["quantities"]["gross"] for m in tier["models"]}
        fit = bt.ols([[points[m]["BW_GB_per_s"], points[m]["R_over_tau_GB_per_s"]] for m in tier["models"]],
                     [points[m]["P_mean_w"] for m in tier["models"]])
        for model, dev in tier["deviations"].items():
            q = self.result["cells"][model]["pass1"]["boundaries"]["rails"]["quantities"]["gross"]
            pred = bt.ols_predict(fit, [q["BW_GB_per_s"], q["R_over_tau_GB_per_s"]])
            expected = bt.t_two_sided(alpha, fit["df"]) * pred["se_pred_hc3"] + q["P_half_width_w"]
            self.assertAlmostEqual(dev["half_width_w"], expected, places=9)
            self.assertGreater(dev["half_width_w"], q["P_half_width_w"])
            self.assertAlmostEqual(dev["deviation_w"], q["P_mean_w"] - pred["yhat"], places=9)

    def test_item9_vif_printed_beside_lambda(self):
        rest = self.result["h2"]["rest"]["pass1"]["rest_model"]
        self.assertIn("vif_BW_and_P_rails", rest)
        self.assertGreater(rest["vif_BW_and_P_rails"], 1.0)
        self.assertIsNone(rest["word_drawn"])
        self.assertNotIn("rest_model", self.result["h2"]["rails"]["pass1"])
        clean = self.result["cells"]["qwen3-8b-4bit"]["pass1"]["boundaries"]["rails"]
        self.assertEqual((clean["gross"]["n_r"], clean["gross"]["n_b"], clean["gross"]["df"]), (10, 10, 9))
        self.assertNotIn("without_assisted", clean)

    def test_drift_allowance_scaled_by_energy_or_time(self):
        for model, block in self.result["cells"].items():
            for boundary in bt.BOUNDARIES:
                cell = block["pass1"]["boundaries"][boundary]
                record = cell["drift_allowance"]
                self.assertEqual(record["status"], "ok", (model, boundary))
                self.assertGreaterEqual(record["scale"], 1.0)
                expected = max(1.0, record["E_first_pass_j"] / record["E_ref_j"], record["T_first_pass_s"] / record["T_ref_s"])
                self.assertAlmostEqual(record["scale"], expected, places=9)
                self.assertAlmostEqual(cell["gross"]["kind_averages_j"]["E_whole_window_drift_allowance_j"],
                                       record["half_allowance_scaled_j"], places=9)

    def test_d2_d3_d6_each_boundary_and_family_has_its_own_allowance(self):
        block = self.result["cells"]["qwen3-8b-4bit"]["pass1"]["boundaries"]
        families = {b: (block[b]["drift_allowance"]["family"], block[b]["drift_allowance_idle_family"]["family"])
                    for b in bt.BOUNDARIES}
        self.assertEqual(families, {"rails": ("gross", "idle_subtracted"), "dc_input": ("dc_gross", "dc_idle_subtracted"),
                                    "rest": ("rest_gross", "rest_idle_subtracted")})
        session = self.result["sessions"]["p1-s2"]["neg8"]
        self.assertEqual(set(session), {"rails/gross", "rails/idle", "dc_input/gross", "dc_input/idle", "rest/gross", "rest/idle"})
        for record in session.values():
            self.assertEqual(record["status"], "ok")
        # the DC family's reference energy is the references' meter energy over their request
        archive = bt.load_archive(WORLD["one"] / "archives/p1-s2")
        rows = bt.read_export(WORLD["one"] / "exports/bytes-s2-p1/p1-s2.runs.csv")
        refs = [r for r in rows if r["role"] in ("start", "midpoint", "end")]
        joined = [bt.dc_join(archive, r["run_id"])["request_energy_j"] for r in refs]
        self.assertAlmostEqual(session["dc_input/gross"]["E_ref_j"], sum(joined) / len(joined), places=6)
        self.assertAlmostEqual(session["rest/gross"]["E_ref_j"] + session["rails/gross"]["E_ref_j"],
                               session["dc_input/gross"]["E_ref_j"], places=6)
        self.assertLess(session["rails/idle"]["E_ref_j"], session["rails/gross"]["E_ref_j"])
        # D6: the idle-subtracted line carries the idle family's own allowance, at the cell's one
        # gross scale (Addendum 3 item 2: E_ref is the mean gross energy of the references)
        for b in bt.BOUNDARIES:
            idle = block[b]["drift_allowance_idle_family"]
            self.assertAlmostEqual(block[b]["idle_subtracted"]["kind_averages_j"]["E_whole_window_drift_allowance_j"],
                                   idle["half_allowance_scaled_j"], places=9)
            self.assertEqual(idle["scale"], block[b]["drift_allowance"]["scale"])
            self.assertNotEqual(idle["allowance_j"], block[b]["drift_allowance"]["allowance_j"])
            self.assertAlmostEqual(idle["half_allowance_scaled_j"], idle["allowance_j"] / 2 * idle["scale"], places=12)
        # D2/D3: u is added to B beside the allowance, never substituted
        for b in ("dc_input", "rest"):
            kinds = block[b]["gross"]["kind_averages_j"]
            self.assertGreater(kinds["E_meter_edge_bound_j"], 0.0)
            self.assertGreater(kinds["E_whole_window_drift_allowance_j"], 0.0)

    def test_h1_rails_finds_bytes(self):
        h1 = self.result["h1"]["rails"]["pass1"]
        self.assertEqual(h1["status"], "ok")
        for model in bt.MOE:
            self.assertEqual(h1["models"][model]["word"], "bytes", model)
        self.assertEqual(h1["active_or_resident"]["answer"], "active")
        for model in bt.FIT_SET:
            self.assertIsNone(h1["models"][model]["word"])
            self.assertAlmostEqual(h1["models"][model]["checks"]["bytes"]["ln_measured_over_predicted"], 0.0, delta=0.01)
        for model in bt.HELD_OUT:
            self.assertIn(h1["models"][model]["word"], ("bytes", "unresolved"))
            self.assertTrue(h1["models"][model]["checks"]["bytes"]["consistent"])
        self.assertEqual(set(h1["held_out_predictions_at_manifest_x"]), set(bt.HELD_OUT))

    def test_h2_rails_recovers_epsilon_and_resident_adds_nothing(self):
        h2 = self.result["h2"]["rails"]["pass1"]
        self.assertEqual(h2["n"], 10)
        eps = h2["simple"]["epsilon_j_per_GB"]
        self.assertLess(eps["lower"], self.truth["S_BYTES_j_per_GB"])
        self.assertGreater(eps["upper"], self.truth["S_BYTES_j_per_GB"])
        self.assertAlmostEqual(h2["simple"]["P0_w"], 0.0, delta=0.5)
        self.assertTrue(h2["resident_extended"]["resident_adds_nothing"])
        self.assertEqual(sorted(h2["tier"]["models"]), sorted(bt.TIER))
        self.assertEqual(set(h2["tier"]["deviations"]), {m for m in bt.ROSTER if m not in bt.TIER})
        for dev in h2["tier"]["deviations"].values():
            self.assertLess(dev["lower_w"], 0.0)
            self.assertGreater(dev["upper_w"], 0.0)
        self.assertEqual(len(h2["leave_one_out"]), 10)
        self.assertIn("rest_model", self.result["h2"]["rest"]["pass1"])
        self.assertNotIn("rest_model", h2)
        self.assertEqual(h2["one_pass_models"], [])
        self.assertNotIn("two_pass_sensitivity", self.result["h2"]["rails"]["passes_mean"])

    def test_d1_h2_intervals_are_hc3_with_ols_beside(self):
        h2 = self.result["h2"]["rails"]["pass1"]
        eps = h2["simple"]["epsilon_j_per_GB"]
        self.assertEqual(eps["se_method"], "HC3")
        self.assertEqual(eps["ols"]["se_method"], "OLS")
        self.assertNotAlmostEqual(eps["half_width"], eps["ols"]["half_width"], places=12)
        self.assertEqual(h2["se_method"], "HC3 primary, OLS beside")
        for dev in h2["tier"]["deviations"].values():
            self.assertEqual(dev["se_method"], "HC3")
            alpha = self.result["multiplicity"]["H2"]["rails"]["pass1"]["alpha_per_interval"]
            t = bt.t_two_sided(alpha, h2["tier"]["df"])
            self.assertAlmostEqual(dev["half_width_w"], t * dev["se_pred_hc3_w"] + dev["measured_half_width_w"], places=9)
            self.assertAlmostEqual(dev["ols"]["half_width_w"], t * dev["ols"]["se_pred_w"] + dev["measured_half_width_w"], places=9)

    def test_multiplicity_levels(self):
        m = self.result["multiplicity"]
        self.assertEqual(m["H1"]["family_size"], 21)
        self.assertAlmostEqual(m["H1"]["alpha_per_check"], 0.05 / 21)
        self.assertEqual(m["H2"]["rails"]["pass1"]["k_primary_intervals"], 9)
        self.assertEqual(m["H2"]["rest"]["pass1"]["k_primary_intervals"], 11)
        cell = self.result["cells"]["qwen3-8b-4bit"]["pass1"]["boundaries"]["rails"]["gross"]
        self.assertAlmostEqual(cell["alpha_family"], 0.05 / 21)
        self.assertGreater(cell["h_j"], cell["h95_j"])

    def test_neg8_record_per_session(self):
        for session_id, record in self.result["sessions"].items():
            neg8 = record["neg8"]["rails/gross"]
            self.assertEqual(neg8["status"], "ok", session_id)
            self.assertEqual(neg8["corpus_n"], 12)
            self.assertTrue(neg8["screen_passed"])
            self.assertEqual(neg8["midpoint_lost"], session_id in ("p1-s5", "p1-s6"))
            self.assertEqual(neg8["bound_terms"]["prediction_j"] / (bt.student_t_critical_95(11)), neg8["bound_terms"]["prediction_j"] / 2.201)


class TwoStageTests(unittest.TestCase):
    def test_stage_one_commits_what_stage_two_recomputes(self):
        one = run_twin(WORLD["two"], "1")
        two = run_twin(WORLD["two"], "2")
        blinded = run_twin(WORLD["two"], "blinded", key_dir=False)
        self.assertEqual(sorted(one["cells"]), sorted(bt.FIT_SET))
        self.assertEqual(one["stage1_commit"]["sha256"], two["stage1_commit"]["sha256"])
        self.assertNotEqual(blinded["stage1_commit"]["sha256"], two["stage1_commit"]["sha256"])
        self.assertEqual(one["stage1_commit"]["sha256"], bt.sha256_of(two["stage1_commit"]["content"]))
        self.assertEqual(sorted(blinded["cells"]), sorted(bt.ROSTER))
        self.assertTrue(any("DC-input skipped" in note for note in blinded["notes"]))
        self.assertEqual(blinded["cells"]["qwen3-8b-4bit"]["pass1"]["boundaries"]["dc_input"]["status"], "no_archive_join")
        self.assertIn("h1_lines", two["stage1_commit"]["content"])
        self.assertIn("h2_tier1_inputs", two["stage1_commit"]["content"])

    def test_item5_single_pass_mean_is_the_pass_and_passes_mean_is_primary(self):
        one = run_twin(WORLD["one"], "2")
        self.assertEqual(one["primary_pass_key"], "passes_mean")
        self.assertEqual(one["pass_keys"]["description"], ["pass1"])
        for model, block in one["cells"].items():
            self.assertEqual(block["passes_mean"]["n_passes"], 1)
            q1 = block["passes_mean"]["boundaries"]["rails"]["quantities"]["gross"]
            self.assertEqual(q1["label"], "one_pass")
            self.assertFalse(q1["one_pass_after_refusal"])    # collected once: labelled, not degraded
            q, p = (block[k]["boundaries"]["rails"]["quantities"]["gross"] for k in ("passes_mean", "pass1"))
            self.assertAlmostEqual(q["E_dec_j"], p["E_dec_j"], places=12)
            self.assertAlmostEqual(q["e_half_width_j_per_step"], p["e_half_width_j_per_step"], places=12)
            self.assertIsNone(q["pass_difference_E_dec_j"])
        self.assertEqual(one["h1"]["rails"]["passes_mean"]["active_or_resident"]["answer"],
                         one["h1"]["rails"]["pass1"]["active_or_resident"]["answer"])

    def test_item5_two_pass_half_width_is_the_mean_of_h_plus_B(self):
        two = run_twin(WORLD["two"], "2")
        self.assertEqual(two["primary_pass_key"], "passes_mean")
        self.assertEqual(sorted(two["pass_keys"]["description"]), ["pass1", "pass2"])
        for model, block in two["cells"].items():
            cells = [block[k]["boundaries"]["rails"]["gross"] for k in ("pass1", "pass2")]
            q = block["passes_mean"]["boundaries"]["rails"]["quantities"]["gross"]
            expected = sum(c["h_j"] + c["B_j"] for c in cells) / 2
            self.assertAlmostEqual(q["e_half_width_j_per_step"] * bt.DECODE_STEPS, expected, places=9)
            self.assertAlmostEqual(q["E_dec_j"], sum(c["mean_j"] for c in cells) / 2, places=9)
            # Addendum 7 item 12: P of the pass mean is mean E / mean T, half-width (mean h + mean B) / mean T
            mean_t = sum(c["duration_s"] for c in cells) / 2
            self.assertAlmostEqual(q["P_mean_w"], q["E_dec_j"] / mean_t, places=9)
            self.assertAlmostEqual(q["P_half_width_w"], expected / mean_t, places=9)
            self.assertNotAlmostEqual(cells[0]["duration_s"], cells[1]["duration_s"], places=3)   # unequal passes
            self.assertEqual(q["label"], "pass_mean")
            for stored, c in zip(q["pass_half_widths_j"], cells):
                self.assertAlmostEqual(stored, c["h_j"] + c["B_j"], places=9)
        fit = two["stage1_commit"]["content"]["fit_cells"]["rails"]
        self.assertIn("passes_mean", fit)

    def test_passes_are_ordered_by_registered_identity_and_their_mean_is_reported(self):
        two = run_twin(WORLD["two"], "2")
        truth = WORLD["truth_two"]
        for session_id, record in two["sessions"].items():
            identity = record["pass_identity"]
            self.assertEqual(identity["source"], "export sidecar pack_id", session_id)
            self.assertEqual(identity["pass_id"], int(session_id[1]))
            self.assertEqual(identity["flags"], [])
        for model, block in two["cells"].items():
            self.assertEqual(sorted(block), ["pass1", "pass2", "passes_mean"])
            self.assertTrue(block["pass1"]["session_id"].startswith("p1-"))
            self.assertTrue(block["pass2"]["session_id"].startswith("p2-"))
            q = block["passes_mean"]["boundaries"]["rails"]["quantities"]["gross"]
            p1 = block["pass1"]["boundaries"]["rails"]["quantities"]["gross"]["E_dec_j"]
            p2 = block["pass2"]["boundaries"]["rails"]["quantities"]["gross"]["E_dec_j"]
            self.assertAlmostEqual(q["E_dec_j"], (p1 + p2) / 2, places=9)
            self.assertAlmostEqual(q["pass_difference_E_dec_j"], p2 - p1, places=9)
        for pass_key in ("pass1", "pass2", "passes_mean"):
            self.assertEqual(two["h1"]["rails"][pass_key]["active_or_resident"]["answer"], "active")
            eps = two["h2"]["rails"][pass_key]["simple"]["epsilon_j_per_GB"]
            self.assertLess(eps["lower"], truth["S_BYTES_j_per_GB"])
            self.assertGreater(eps["upper"], truth["S_BYTES_j_per_GB"])
        self.assertEqual(two["sessions"]["p2-s1"]["pass_of"]["qwen3-4b-4bit"], 2)


class OnePassFallbackTests(unittest.TestCase):
    """Addendum 7 D9 on a two-pass world where Qwen3-14B's pass 1 refuses (four kept repeats)."""

    @classmethod
    def setUpClass(cls):
        cls.result = run_twin(WORLD["refused"], "2")

    def test_a_surviving_pass_is_the_point_labelled_one_pass(self):
        block = self.result["cells"]["qwen3-14b-4bit"]
        self.assertEqual(block["pass1"]["boundaries"]["rails"]["gross"]["status"], "refused_below_minimum")
        self.assertEqual(block["pass1"]["boundaries"]["rails"]["gross"]["n_r"], 4)
        q = block["passes_mean"]["boundaries"]["rails"]["quantities"]["gross"]
        p2 = block["pass2"]["boundaries"]["rails"]["quantities"]["gross"]
        self.assertEqual((q["label"], q["passes_collected"], q["passes_computed"]), ("one_pass", 2, 1))
        self.assertTrue(q["one_pass_after_refusal"])
        single = self.result["cells"]["qwen3-8b-4bit"]["passes_mean"]["boundaries"]["rails"]["quantities"]["gross"]
        self.assertFalse(single["one_pass_after_refusal"])
        self.assertEqual(q["pass_statuses"], ["refused_below_minimum", "ok"])
        self.assertAlmostEqual(q["E_dec_j"], p2["E_dec_j"], places=12)
        self.assertAlmostEqual(q["e_half_width_j_per_step"], p2["e_half_width_j_per_step"], places=12)
        h1 = self.result["h1"]["rails"]["passes_mean"]
        self.assertEqual(h1["models"]["qwen3-14b-4bit"]["label"], "one_pass")
        self.assertIsNotNone(h1["models"]["qwen3-14b-4bit"]["word"])
        self.assertEqual(h1["models"]["qwen3-8b-4bit"]["label"], "pass_mean")
        self.assertEqual(h1["active_or_resident"]["answer"], "active")

    def test_c_two_pass_sensitivity_line_beside_the_primary_h2(self):
        for boundary in bt.BOUNDARIES:
            h2 = self.result["h2"][boundary]["passes_mean"]
            self.assertEqual(h2["status"], "ok")
            self.assertEqual(h2["n"], 10)
            self.assertEqual(h2["one_pass_models"], ["qwen3-14b-4bit"])
            sens = h2["two_pass_sensitivity"]
            self.assertEqual(sens["excluded_models"], ["qwen3-14b-4bit"])
            self.assertEqual(sens["n"], 9)
            self.assertNotIn("qwen3-14b-4bit", sens["models"])
            self.assertEqual(sens["status"], "ok")
            self.assertTrue(sens["label"].startswith("sensitivity"))
            self.assertNotIn("two_pass_sensitivity", self.result["h2"][boundary]["pass2"])
        self.assertEqual(self.result["multiplicity"]["H2"]["rails"]["passes_mean"]["k_primary_intervals"], 9)

    def test_b_both_passes_refused_and_small_fits_refuse(self):
        merged = bt.mean_of_passes([{"status": "refused_below_minimum"}, {"status": "refused_bound_kind_missing"}])
        self.assertEqual(merged["status"], "refused_no_pass_computed")
        self.assertEqual(merged["passes_computed"], 0)
        points = {m: {"status": "ok", "P": 10.0 + i, "BW": 100.0 + 10 * i, "R_over_tau": 50.0 + 7 * i * i,
                      "P_half_width": 0.1, "label": "pass_mean"} for i, m in enumerate(bt.TIER[:3])}
        self.assertEqual(bt.h2_fits(points, 0.05)["status"], "refused_n_minus_p_below_2")
        self.assertEqual(bt.h2_primary_count(points, "rails"), 0)
        four = {**points, bt.TIER[3]: {"status": "ok", "P": 14.5, "BW": 131.0, "R_over_tau": 90.0, "P_half_width": 0.1, "label": "pass_mean"}}
        fit = bt.h2_fits(four, 0.05)
        self.assertEqual(fit["status"], "ok")                 # simple fit: n - p = 2
        self.assertNotIn("resident_extended", fit)            # extended fit: n - p = 1, refused
        self.assertNotIn("tier", fit)
        self.assertEqual(bt.h2_primary_count(four, "rails"), 1)


class ExportShapeTests(unittest.TestCase):
    def test_synthetic_export_has_the_export_runs_columns(self):
        import csv
        path = next((WORLD["one"] / "exports/bytes-s1-p1").glob("*.runs.csv"))
        with path.open(newline="") as stream:
            reader = csv.DictReader(stream)
            columns = reader.fieldnames
            rows = list(reader)
        self.assertEqual(tuple(columns), synth.COLUMNS)
        roles = {row["role"] for row in rows}
        self.assertEqual(roles, {"corpus", "start", "midpoint", "end", "science"})
        science = [row for row in rows if row["role"] == "science"]
        self.assertEqual(len(science), 100)
        self.assertEqual({row["strata"] for row in science}, {"repeat", "quad"})
        self.assertEqual(sum(1 for row in science if row["abba_label"] == "A"), 40)
        failed = [row for row in rows if row["status"] == "failed"]
        for row in failed:
            self.assertEqual(row["phase_decode_j"], "")
            self.assertEqual(row["excluded"], "True")
        sidecar = json.loads(path.with_name(path.name.replace(".runs.csv", ".session.json")).read_text())
        self.assertEqual(sidecar["schema"], "joulewise.b6_export_session.v1")
        self.assertTrue(sidecar["blinding"]["applied"])

    def test_export_energies_are_blinded_by_pack_times_config(self):
        rows = bt.read_export(next((WORLD["one"] / "exports").glob("*/p1-s2.runs.csv")))
        truth = WORLD["truth_one"]
        row = next(r for r in rows if r["role"] == "science" and r["status"] == "succeeded")
        factor = truth["factors"]["pack"] * truth["factors"]["config"][row["config_key"]]
        archive = WORLD["one"] / "archives/p1-s2/withheld/reductions" / (row["run_id"] + ".summary_metrics.rereduced.json")
        summary = json.loads(archive.read_text())
        self.assertAlmostEqual(row["phase_decode_j"], summary["phase_energy_j"]["decode"] * factor, places=9)
        self.assertAlmostEqual(bt.stored_factor(WORLD["one"] / "keys", row["config_key"]), factor, places=12)


class PassIdentityTests(unittest.TestCase):
    """Lead ruling 2026-10-20 item 2: ordering by registered pass identity, never by a clock."""

    def test_identity_sources_in_order(self):
        listed = {"s": {"session_id": "s", "pass_id": 2}}
        sidecar = {"pack_id": "bytes-s3-p1"}
        self.assertEqual(bt.pass_identity("s", listed, sidecar)["pass_id"], 2)           # the manifest wins
        self.assertEqual(bt.pass_identity("s", listed, sidecar)["source"], "manifest.sessions.pass_id")
        self.assertEqual(bt.pass_identity("t", listed, sidecar), {"pass_id": 1, "source": "export sidecar pack_id",
                                                                   "pack_id": "bytes-s3-p1", "flags": []})
        for bad in ({}, {"pack_id": "bytes"}, {"pack_id": "alpha-p0"}, {"pack_id": "bytes-s3-p2x"}):
            self.assertEqual(bt.pass_identity("t", {}, bad), {"pass_id": None, "source": None,
                                                              "flags": ["pass_identity_missing"]})
        self.assertEqual(bt.pass_identity("u", {"u": {"session_id": "u", "pass_id": "2"}}, {})["flags"],
                         ["pass_identity_missing"])                                  # a string is not an id

    def test_order_follows_the_pass_id_not_the_session_id_or_any_clock(self):
        rows = lambda sid: [{"role": "science", "model_name": "Qwen3-8B-4bit", "session_id": sid,
                             "run_start_utc": "2099-01-01T00:00:00+00:00"}]
        # session ids and the (unread) clock both say "zz" first; the registered identity says "aa" is pass 2
        sessions = {"zz": rows("zz"), "aa": rows("aa"), "mm": rows("mm")}
        identities = {"zz": {"pass_id": 1}, "aa": {"pass_id": 2}, "mm": {"pass_id": None}}
        self.assertEqual(bt.passes_by_model(sessions, identities), {"qwen3-8b-4bit": ["zz", "aa", "mm"]})
        identities = {"zz": {"pass_id": 2}, "aa": {"pass_id": 1}, "mm": {"pass_id": None}}
        self.assertEqual(bt.passes_by_model(sessions, identities), {"qwen3-8b-4bit": ["aa", "zz", "mm"]})

    def test_no_printed_field_moves_without_the_clock_column(self):
        """The export's run_start_utc is blanked and the session ids are renamed so that their lexical
        order reverses the pass order; the twin's output is identical apart from the renamed ids."""
        import csv
        import shutil
        reference = run_twin(WORLD["two"], "2")
        with tempfile.TemporaryDirectory() as tmp:
            world = Path(tmp) / "world"
            shutil.copytree(WORLD["two"], world)
            rename = {"p1": "zz", "p2": "aa"}       # pass 1 sorts last by session id
            for path in sorted((world / "exports").rglob("*.runs.csv")):
                old_sid = path.name[: -len(".runs.csv")]
                new_sid = rename[old_sid[:2]] + old_sid[2:]
                with path.open(newline="", encoding="utf-8") as stream:
                    reader = csv.DictReader(stream)
                    columns, rows = reader.fieldnames, list(reader)
                for row in rows:
                    row["run_start_utc"] = ""
                    row["session_id"] = new_sid
                path.unlink()
                with (path.parent / (new_sid + ".runs.csv")).open("w", newline="", encoding="utf-8") as stream:
                    writer = csv.DictWriter(stream, fieldnames=columns)
                    writer.writeheader()
                    writer.writerows(rows)
                sidecar = path.with_name(old_sid + ".session.json")
                data = json.loads(sidecar.read_text())
                data["session_id"] = new_sid                     # pack_id (the identity) is unchanged
                sidecar.unlink()
                (path.parent / (new_sid + ".session.json")).write_text(json.dumps(data))
                archive = world / "archives" / old_sid
                acceptance = json.loads((archive / "derived/b6-acceptance.json").read_text())
                acceptance["session_id"] = new_sid
                (archive / "derived/b6-acceptance.json").write_text(json.dumps(acceptance))
                archive.rename(world / "archives" / new_sid)
            renamed = run_twin(world, "2")

        back = {"zz-": "p1-", "aa-": "p2-"}

        def normalise(value):
            if isinstance(value, dict):
                return {normalise(k): normalise(v) for k, v in value.items() if k != "inputs"}
            if isinstance(value, list):
                return [normalise(v) for v in value]
            if isinstance(value, str):
                for new, old in back.items():
                    value = value.replace(new, old)
            return value
        self.assertEqual(normalise(renamed), normalise(reference))
        for model, block in renamed["cells"].items():
            self.assertTrue(block["pass1"]["session_id"].startswith("zz-"), model)
            self.assertTrue(block["pass2"]["session_id"].startswith("aa-"), model)

    def test_missing_identity_is_a_flag_and_a_missing_model_prints_missing(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            world = Path(tmp) / "world"
            shutil.copytree(WORLD["one"], world)
            # strip the identity from one session's sidecar, and remove another model's rows entirely
            sidecar = world / "exports/bytes-s1-p1/p1-s1.session.json"
            data = json.loads(sidecar.read_text())
            data["pack_id"] = "bytes"
            sidecar.write_text(json.dumps(data))
            shutil.rmtree(world / "exports/bytes-s5-p1")
            result = run_twin(world, "2")
        self.assertEqual(result["sessions"]["p1-s1"]["pass_identity"],
                         {"pass_id": None, "source": None, "flags": ["pass_identity_missing"]})
        self.assertIn({"flag": "pass_identity_missing", "session_id": "p1-s1"}, result["flags"])
        self.assertIn({"flag": "rows_missing", "model": "llama-3.3-70b-instruct-4bit"}, result["flags"])
        self.assertNotIn("llama-3.3-70b-instruct-4bit", result["cells"])
        for boundary in bt.BOUNDARIES:
            row = result["h1"][boundary]["passes_mean"]["models"]["llama-3.3-70b-instruct-4bit"]
            self.assertEqual((row["word"], row["status"], row["flags"]), ("missing", "missing", ["rows_missing"]))
        self.assertEqual(result["h2"]["rails"]["passes_mean"]["n"], 9)        # fitted on the models with points
        self.assertEqual(result["cells"]["qwen3-1.7b-4bit"]["passes_mean"]["n_passes"], 1)   # still computed


if __name__ == "__main__":
    unittest.main()
