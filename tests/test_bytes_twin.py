"""Tests for the BYTES twin (scripts/bytes_twin.py): hand-computed worked examples and the twin's own
synthetic bytes-is-truth world (tests/fixtures/bytes/twin_synth.py).  The agreement with the analysis on
the lane's production-shaped campaigns is tests/test_bytes_agreement.py.

Run from the repository root:
    JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m pytest tests/test_bytes_twin.py -q
"""
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import bytes_twin as bt

ROOT = Path(__file__).resolve().parents[1]
_synth_spec = importlib.util.spec_from_file_location("twin_synth", ROOT / "tests/fixtures/bytes/twin_synth.py")
synth = importlib.util.module_from_spec(_synth_spec)
_synth_spec.loader.exec_module(synth)


def quantity_bar(a, b):
    """COMMON: an algebraic oracle without a printed half-width uses 1e-6 relative,
    or 1e-6 absolute in its unit near zero. This exceeds 1e6 * 2.2e-16 = 2.2e-10
    relative floating-point noise. Tests of recovery use their uncertainty instead.
    """
    return 1e-6 * max(1.0, abs(a), abs(b))


class QuantityTestCase(unittest.TestCase):
    """Closed-form algebra checks without printed cells use quantity_bar in the quantity's unit."""
    def assertQuantityEqual(self, a, b):
        self.assertAlmostEqual(a, b, delta=quantity_bar(a, b))

    def assertQuantityDifferent(self, a, b):
        self.assertGreater(abs(a - b), quantity_bar(a, b))

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


def run_twin(world: Path, stage: str, *, archives=True, key_dir=True, extra=()) -> dict:
    out = world / f"twin-{stage}.json"
    argv = [*extra, "--export-dir", str(world / "exports"), "--manifest", str(world / "bytes_manifest.json"),
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


class ConstantsTests(QuantityTestCase):
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
        self.assertQuantityEqual(q["e_j_per_step"], 2.0)
        self.assertQuantityEqual(q["tau_s_per_step"], 0.01)
        self.assertQuantityEqual(q["BW_GB_per_s"], 200.0)
        self.assertQuantityEqual(q["e_printed_j_per_token"], 2.0)
        self.assertEqual(q["printed_label"], bt.PER_TOKEN_LABEL)
        self.assertQuantityEqual(q["e_half_width_j_per_step"], 24.0 / 512)


class StudentTTests(QuantityTestCase):
    def test_exact_quantiles_of_the_analysis_plan(self):
        for df, expected in ((9, 2.262157162798205), (8, 2.306004135204166), (7, 2.364624251592785),
                             (6, 2.446911851), (5, 2.570581836), (4, 2.776445105)):
            self.assertQuantityEqual(bt.t_quantile(0.975, df), expected)

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
        self.assertQuantityEqual(bt.t_cdf(bt.t_two_sided(0.05 / 21, 9), 9), 1 - 0.05 / 42)


def members(values, bounds, prefix):
    return [{"id": f"{prefix}{i}", "E": e, "T": 1.0, "bounds": dict(bounds)} for i, e in enumerate(values, 1)]


def quads(values, bounds, prefix):
    return [{"id": f"{prefix}{i}", "members": members([e] * 4, bounds, f"{prefix}{i}m")} for i, e in enumerate(values, 1)]


class PhaseEstimateTests(QuantityTestCase):
    R = [10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8, 10.1, 10.0, 9.6]
    B = [10.4, 10.1, 10.3, 10.2, 10.5, 10.0, 10.2, 10.3, 10.1, 9.9]
    KINDS = ("k1", "k2", "k3")
    BOUNDS = {"k1": 0.010, "k2": 0.0, "k3": 0.050}

    def test_worked_example_all_units_kept(self):
        cell = bt.phase_estimate(members(self.R, self.BOUNDS, "r"), quads(self.B, self.BOUNDS, "q"), self.KINDS)
        self.assertEqual(cell["status"], "ok")
        self.assertQuantityEqual(cell["mean_j"], 10.16)
        # Half of the worked value's last printed digit (registration §14).
        self.assertAlmostEqual(cell["h95_j"], 0.10833, delta=0.5 * 10 ** -5)
        self.assertQuantityEqual(cell["B_j"], 0.060)
        # Half of the worked value's last printed digit (registration §14).
        self.assertAlmostEqual(cell["lower95_j"], 9.9917, delta=0.5 * 10 ** -4)
        # Half of the worked value's last printed digit (registration §14).
        self.assertAlmostEqual(cell["upper95_j"], 10.3283, delta=0.5 * 10 ** -4)
        # Half of the worked value's last printed digit (registration §14).
        self.assertAlmostEqual(cell["per_token_j"], 0.019844, delta=0.5 * 10 ** -6)
        self.assertEqual(cell["df"], 9)

    def test_worked_example_units_removed(self):
        reps = [m for m in members(self.R, self.BOUNDS, "r") if m["id"] != "r6"]
        qs = [q for q in quads(self.B, self.BOUNDS, "q") if q["id"] not in ("q5", "q9")]
        cell = bt.phase_estimate(reps, qs, self.KINDS)
        self.assertEqual((cell["n_r"], cell["n_b"], cell["df"]), (9, 8, 7))
        # Half of the worked value's last printed digit (registration §14).
        self.assertAlmostEqual(cell["mean_j"], 10.13333, delta=0.5 * 10 ** -5)
        # Half of the worked value's last printed digit (registration §14).
        self.assertAlmostEqual(cell["h95_j"], 0.11519, delta=0.5 * 10 ** -5)
        # Half of the worked value's last printed digit (registration §14).
        self.assertAlmostEqual(cell["lower95_j"], 9.9581, delta=0.5 * 10 ** -4)
        # Half of the worked value's last printed digit (registration §14).
        self.assertAlmostEqual(cell["upper95_j"], 10.3085, delta=0.5 * 10 ** -4)
        # Half of the worked value's last printed digit (registration §14).
        self.assertAlmostEqual(cell["per_token_j"], 0.019792, delta=0.5 * 10 ** -6)

    def test_family_alpha_widens_only_h(self):
        full = bt.phase_estimate(members(self.R, self.BOUNDS, "r"), quads(self.B, self.BOUNDS, "q"), self.KINDS)
        wide = bt.phase_estimate(members(self.R, self.BOUNDS, "r"), quads(self.B, self.BOUNDS, "q"), self.KINDS,
                                 alpha=0.05 / 21)
        self.assertEqual(full["mean_j"], wide["mean_j"])
        self.assertEqual(full["B_j"], wide["B_j"])
        self.assertGreater(wide["h_j"], full["h_j"])
        self.assertQuantityEqual(wide["h_j"], bt.h_at(full, 0.05 / 21))

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
        self.assertQuantityDifferent(cell["mean_j"], plain)
        # Half of the worked value's last printed digit (registration §14).
        self.assertAlmostEqual(plain, 10.12927, delta=0.5 * 10 ** -5)


class Neg8Tests(QuantityTestCase):
    def test_count_adjusted_bound_by_hand(self):
        bound = bt.neg8_bound([1, 2, 3, 4, 5, 6], 2, 2)
        self.assertQuantityEqual(bound["envelope_j"], 4.0)
        expected = 2.571 * 1.8708286933869707 * math.sqrt(1.0)   # Addendum 7 D8: the three-decimal table
        self.assertQuantityEqual(bound["prediction_j"], expected)
        self.assertQuantityDifferent(bound["prediction_j"], bt.t_quantile(0.975, 5) * 1.8708286933869707)
        self.assertQuantityEqual(bound["bound_j"], max(4.0, expected))
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
        self.assertQuantityEqual(record["trajectory_excursion_j"], 0.8)
        self.assertEqual(record["allowance_j"], max(0.8, record["bound_terms"]["bound_j"]))
        self.assertQuantityEqual(record["T_ref_s"], 2.0)
        lost = [r for r in rows if r["role"] != "midpoint"]
        self.assertTrue(bt.neg8_allowance(lost)["midpoint_lost"])
        self.assertQuantityEqual(bt.neg8_allowance(lost)["trajectory_excursion_j"], 0.1)
        self.assertEqual(bt.neg8_allowance(rows[:5])["status"], "undefined_references_insufficient")


class RegressionTests(QuantityTestCase):
    def test_exact_line(self):
        fit = bt.ols([[1], [2], [4]], [3.0, 5.0, 9.0])
        self.assertQuantityEqual(fit["coef"][0], 1.0)
        self.assertQuantityEqual(fit["coef"][1], 2.0)
        self.assertQuantityEqual(fit["s2"], 0.0)
        self.assertQuantityEqual(bt.ols_predict(fit, [10])["yhat"], 21.0)

    def test_simple_regression_against_textbook_formulas(self):
        xs, ys = [1, 2, 3, 4, 5], [2.1, 3.9, 6.2, 7.8, 10.1]
        fit = bt.ols([[x] for x in xs], ys)
        mx, my = sum(xs) / 5, sum(ys) / 5
        sxx = sum((x - mx) ** 2 for x in xs)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
        rss = sum((y - (my - slope * mx) - slope * x) ** 2 for x, y in zip(xs, ys))
        se = math.sqrt(rss / 3 / sxx)
        interval = bt.coef_interval(fit, 1, 0.05)
        self.assertQuantityEqual(interval["value"], slope)
        self.assertQuantityEqual(interval["ols"]["half_width"], bt.t_quantile(0.975, 3) * se)

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
                self.assertQuantityEqual(fit["cov_hc3"][a][b], expected[a][b])
        interval = bt.coef_interval(fit, 1, 0.05)
        self.assertEqual(interval["se_method"], "HC3")
        self.assertQuantityEqual(interval["half_width"], bt.t_quantile(0.975, 4) * math.sqrt(expected[1][1]))
        self.assertEqual(interval["ols"]["se_method"], "OLS")
        self.assertQuantityEqual(interval["ols"]["half_width"], bt.t_quantile(0.975, 4) * math.sqrt(fit["cov"][1][1]))
        pred = bt.ols_predict(fit, [7])
        var = sum([1.0, 7.0][a] * expected[a][b] * [1.0, 7.0][b] for a in range(2) for b in range(2))
        self.assertQuantityEqual(pred["se_pred_hc3"], math.sqrt(var + fit["s2"]))
        self.assertQuantityEqual(pred["se_mean_hc3"], math.sqrt(var))

    def test_two_regressors(self):
        rows = [[1, 1], [2, 1], [3, 2], [4, 3], [5, 5], [6, 8]]
        ys = [2 + 3 * a + 0.5 * b for a, b in rows]
        fit = bt.ols(rows, ys)
        for value, expected in zip(fit["coef"], (2, 3, 0.5)):
            self.assertQuantityEqual(value, expected)


class H1Tests(QuantityTestCase):
    def points(self):
        return {"a": {"x": {"bytes": 1.0, "resident": 1.0, "time": 1.0}, "e": 1.0, "w": 0.1, "kind": "fit"},
                "b": {"x": {"bytes": 2.0, "resident": 2.0, "time": 1.5}, "e": 2.0, "w": 0.1, "kind": "fit"},
                "c": {"x": {"bytes": 4.0, "resident": 4.0, "time": 2.0}, "e": 4.0, "w": 0.1, "kind": "fit"}}

    def test_corner_interval_brackets_the_central_line(self):
        lines = bt.h1_lines(self.points())
        self.assertEqual(len(lines["bytes"]["corners"]), 8)
        pred = bt.h1_predict(lines, "bytes", 10.0)
        self.assertQuantityEqual(pred["central"], 10.0)
        self.assertLess(pred["lower"], 10.0)
        self.assertGreater(pred["upper"], 10.0)
        # The all-up and all-down corners shift the whole line by exactly w, so the interval is at
        # least 2w wide, and mixed corners tilt it further out at x far from the fit points.
        self.assertGreaterEqual(pred["upper"], 10.1 - quantity_bar(10.1, pred["upper"]))
        self.assertLessEqual(pred["lower"], 9.9 + quantity_bar(9.9, pred["lower"]))
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
            self.assertQuantityEqual(words["models"][name]["checks"]["bytes"]["ln_measured_over_predicted"], 0.0)
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


class MeterTests(QuantityTestCase):
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
        # Independently placed edges: use u in J, plus three SEs of the fixture's
        # 0.02 W iid sample noise and half a 28 V * 1 microamp payload digit.
        noise_w = 3 * .02 / math.sqrt(joined["samples"]) + 0.5 * 28e-6
        self.assertLessEqual(abs(joined["meter_gross_j"] - expected_power * joined["decode_span_s"]),
                             joined["meter_phase_edge_j"] + noise_w * joined["decode_span_s"])
        # Same synthetic sampler noise and payload quantization on the idle mean.
        self.assertLessEqual(abs(joined["idle_power_w"] - truth["DC_IDLE_W"]),
                             3 * .02 / math.sqrt(joined["idle_samples"]) + 0.5 * 28e-6)
        self.assertGreaterEqual(joined["edge_bound_j"], 0.0)

    def test_item3_edge_term_is_edge_powers_times_r_max_plus_dt(self):
        archive_root = next(iter(sorted((WORLD["one"] / "archives").iterdir())))
        archive = bt.load_archive(archive_root)
        roster = json.loads((archive_root / "derived/roster.json").read_text())
        run_id = next(m["run_id"] for m in roster["members"] if m["role"] == "science")
        joined = bt.dc_join(archive, run_id)
        terms = joined["edge_terms"]
        self.assertQuantityEqual(joined["edge_bound_j"], (terms["P_start_w"] + terms["P_end_w"]) * (terms["r_max_s"] + terms["dt_meter_s"]))
        self.assertQuantityEqual(terms["dt_meter_s"], synth.STEP_MS / 1e3)
        self.assertQuantityEqual(terms["r_max_s"], joined["clock_fit"]["excess_latency_ms_absmax"] / 1e3)
        self.assertGreater(terms["r_max_s"], 0.001)
        self.assertIn("request_energy_j", joined)
        self.assertGreater(joined["request_energy_j"], joined["decode_energy_j"])
        self.assertGreater(terms["P_start_w"], 0.0)
        self.assertGreater(terms["P_end_w"], 0.0)
        # The edge term is a two-edge bound: both edge powers enter, and it is positive even with no jitter.
        self.assertGreaterEqual(joined["edge_bound_j"], (terms["P_start_w"] + terms["P_end_w"]) * terms["dt_meter_s"])


class BatteryTermsTests(QuantityTestCase):
    def test_not_evaluated_reason_names_only_kept_rows_including_atomic_quads(self):
        rows = []
        for stratum, units, size in (("repeat", 10, 1), ("quad", 10, 4)):
            for unit in range(units):
                for member in range(size):
                    run = f"{stratum}-{unit}-{member}"
                    rows.append({"run_id": run, "order_index": member, "status": "succeeded", "excluded": False,
                        "exclusion_codes": "", "flag_codes": "", "phase_decode_j": 12.0,
                        "dur_decode_s": 1.0, "idle_power_w": 1.0,
                        "bound_E_clock_anchor_shift_bound_j": .1,
                        "bound_E_interpolation_joint_edge_bound_j": 0.0,
                        "cell_ids": "cell", "strata": stratum, "unit_ids": str(unit),
                        "_decode_assisted": False})
        missing = next(r for r in rows if r["run_id"] == "repeat-0-0")
        missing.update(_decode_assisted=None, _decode_assist_reason="no polls (run repeat-0-0)")
        bad = next(r for r in rows if r["run_id"] == "quad-0-0")
        bad.update(status="failed", excluded=True, exclusion_codes="member.status_not_succeeded")
        sibling = next(r for r in rows if r["run_id"] == "quad-0-1")
        sibling.update(_decode_assisted=None, _decode_assist_reason="spans unreadable (run quad-0-1)")
        allowances = {("rails", v): {"status": "ok", "family": v, "allowance_j": .2,
                                    "E_ref_j": 12.0, "T_ref_s": 1.0} for v in ("gross", "idle")}
        with patch.object(bt, "_scaled_allowance", return_value=(.1, {"status": "ok", "scale": 1.0})):
            cell = bt.compute_cell(rows, "rails", {}, allowances, .05)
        for variant in ("gross", "idle_subtracted", "flagged_inclusive", "idle_flagged_inclusive"):
            self.assertEqual(cell[variant]["status"], "ok")
            self.assertEqual(cell[variant]["without_assisted"]["reason"], "no polls (run repeat-0-0)")
            self.assertEqual(cell[variant]["decode_assisted_member_counts_reason"], "no polls (run repeat-0-0)")

    def test_missing_bundle_and_spans_have_their_own_marker_reasons(self):
        for status in ("bundle_missing", "spans_unreadable"):
            with self.subTest(status=status), patch.object(bt, "_bundle", return_value=(
                    None if status == "bundle_missing" else Path("unused"))), patch.object(
                    bt, "member_spans", return_value=None):
                result = bt.dc_join({"root": Path("unused"), "streams": []}, "member")
                self.assertEqual(result["status"], status)
                reason = result["decode_assist_evaluated_reason"]
                self.assertNotIn("no mapped meter stream has polls", reason)
                self.assertIn("(run member)", reason)

    def test_blinded_stage_does_not_open_raw_meter_streams(self):
        with patch.object(bt, "load_archive", side_effect=AssertionError("blinded raw meter read")):
            result = run_twin(WORLD["one"], "blinded")
        cell = next(iter(result["cells"].values()))["pass1"]["boundaries"]["rails"]
        self.assertIsNone(cell["gross"]["decode_assisted_member_counts"])
        self.assertEqual(cell["without_assisted"]["status"], "not_evaluated")

    def stream(self):
        # 1 s polls give tau = 2 * 1 s SMC publication + 1 s poll = 3 s.
        # Signed 12 W discharge and -6 W charge are above the ~1 J attribution limit.
        power = [0.0] * 13
        power[3], power[5], power[6], power[9] = 24.0, 12.0, -6.0, 12.0
        return {"poll_ns": [i * 1_000_000_000 for i in range(13)], "battery_watts": power,
                "battery_current_ma": [-1000 if p > 0 else 500 if p < 0 else 0 for p in power]}

    def test_signed_energy_and_forward_edges_and_delayed_marker(self):
        r = bt.battery_terms(self.stream(), [4_000_000_000, 8_000_000_000], [0, 2_000_000_000])
        self.assertEqual(r["status"], "ok")
        self.assertQuantityEqual(r["battery_gross_j"], 6)  # (4 s / 4 polls) * (12 - 6) W
        self.assertQuantityEqual(r["battery_secondary_j"], 6)  # zero idle current
        self.assertQuantityEqual(r["battery_v_start_j"], 18)  # |12| + |-6| W in [4, 7) s
        self.assertQuantityEqual(r["battery_v_end_j"], 12)  # delayed discharge in [8, 11) s
        self.assertQuantityEqual(r["battery_tau_s"], 3)
        self.assertTrue(r["decode_assisted"])  # negative current at 9 s lies in [7, 11)

    def test_marker_poll_count_uses_integer_nanoseconds_at_both_edges(self):
        gap = 100_000_001
        times = [i * gap for i in range(11)]
        tau = 2_000_000_000 + gap
        stream = {"aligned": False, "raw_offset_ns": 0, "poll_ns": times,
                  "battery_watts": [12.0] * len(times), "battery_current_ma": [-1000] * len(times)}
        edge = times[-1] - tau
        for window, count in (([edge, edge + 1], 1), ([edge - 1, edge], 0)):
            with self.subTest(window=window):
                result = bt.battery_terms(stream, window, [0, 1])
                self.assertEqual(result["battery_marker_polls"], count)
                spans = {"decode_ns": window, "idle_ns": [0, 1]}
                with patch.object(bt, "_bundle", return_value=Path("unused")), patch.object(
                        bt, "member_spans", return_value=spans):
                    joined = bt.dc_join({"root": Path("unused"), "streams": [stream]}, "member")
                self.assertIs(joined.get("decode_assisted"), True if count else None)

    def test_missing_voltage_does_not_erase_the_current_marker(self):
        s = self.stream()
        s["battery_watts"][4:8] = [None] * 4
        r = bt.battery_terms(s, [4_000_000_000, 8_000_000_000], [0, 2_000_000_000])
        self.assertEqual(r["status"], "battery reading missing")
        self.assertTrue(r["decode_assisted"])

    def test_idle_charging_is_subtracted_with_its_sign(self):
        s = self.stream()
        s["battery_watts"][:2] = [-6.0, -6.0]
        r = bt.battery_terms(s, [4_000_000_000, 8_000_000_000], [0, 2_000_000_000])
        self.assertQuantityEqual(r["battery_secondary_j"], 30)  # 6 J - (-6 W * 4 s)

    def test_request_span_keeps_battery_energy_outside_decode(self):
        r = bt.battery_terms(self.stream(), [2_000_000_000, 8_000_000_000], [0, 2_000_000_000])
        # NEG-8 requests integrate the whole request: 24 J before decode plus its signed 6 J.
        self.assertQuantityEqual(r["battery_gross_j"], 30)

    def test_delay_uses_a_poll_gap_outside_decode(self):
        s = self.stream()
        s["poll_ns"].insert(0, -5_000_000_000)
        s["battery_watts"].insert(0, None)
        s["battery_current_ma"].insert(0, None)
        r = bt.battery_terms(s, [4_000_000_000, 8_000_000_000], [0, 2_000_000_000])
        self.assertQuantityEqual(r["battery_tau_s"], 7)  # 2 * 1 s SMC + stream-wide 5 s poll gap

    def test_unresolved_anchor_cannot_return_on_the_inclusive_line(self):
        for code in ("member.anchor_not_bounded",):
            row = {"status": "succeeded", "phase_decode_j": 12.0, "dur_decode_s": 1.0,
                   "excluded": True, "exclusion_codes": code}
            self.assertFalse(bt.restorable(row))
            self.assertFalse(bt._kept(row, restore_load_correlated=True))

    def test_precheck_exclusion_with_valid_energy_is_restored(self):
        row = {"status": "succeeded", "phase_decode_j": 12.0, "dur_decode_s": 1.0,
               "excluded": True, "exclusion_codes": "member.target_phase_precheck_failed"}
        self.assertTrue(bt.restorable(row))
        self.assertTrue(bt._kept(row, restore_load_correlated=True))

    def test_incomplete_marker_window_is_evaluated_on_available_polls(self):
        for current, expected in ((0, False), (-1000, True), (None, False)):
            with self.subTest(current=current):
                s = self.stream()
                # End + tau = 11 s; the stream ends at 9 s, inside that window.
                for key in ("poll_ns", "battery_watts", "battery_current_ma"):
                    s[key] = s[key][:10]
                s["battery_current_ma"][7:] = [current] * 3
                r = bt.battery_terms(s, [4_000_000_000, 8_000_000_000], [0, 2_000_000_000])
                self.assertFalse(r["battery_end_window_complete"])
                self.assertIs(r["decode_assisted"], expected)

    def test_later_covering_stream_can_supply_missing_battery_readings(self):
        good = {**self.stream(), "aligned": True, "raw_offset_ns": 0, "name": "good",
                "host_ns": [i * 1_000_000_000 for i in range(13)], "watts": [10.0] * 13,
                "step_ms": 1000, "fit": dict.fromkeys(("excess_latency_ms_absmax", "excess_latency_ms_p95",
                    "excess_latency_ms_max", "excess_latency_ms_min", "clock_rate_ppm"), 0.0)}
        bad = {**good, "name": "missing-voltage", "battery_watts": [None] * 13}
        spans = {"decode_ns": [4_000_000_000, 8_000_000_000], "idle_ns": [0, 2_000_000_000],
                 "request_ns": [2_000_000_000, 8_000_000_000]}
        with patch.object(bt, "_bundle", return_value=Path("unused")), patch.object(bt, "member_spans", return_value=spans):
            result = bt.dc_join({"root": Path("unused"), "streams": [bad, good]}, "member")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["stream"], "good")
        self.assertQuantityEqual(result["battery_gross_j"], 6)

    def test_marker_is_evaluated_without_decode_coverage_on_every_mapped_stream(self):
        assisted = {**self.stream(), "aligned": True, "raw_offset_ns": 0,
                    "host_ns": [6_000_000_000, 12_000_000_000]}
        quiet = {**assisted, "battery_current_ma": [0] * 13}
        spans = {"decode_ns": [4_000_000_000, 8_000_000_000], "idle_ns": [0, 2_000_000_000]}
        for streams in ([assisted, quiet], [quiet, assisted]):
            with self.subTest(assisted_first=streams[0] is assisted):
                with patch.object(bt, "_bundle", return_value=Path("unused")), patch.object(bt, "member_spans", return_value=spans):
                    result = bt.dc_join({"root": Path("unused"), "streams": streams}, "member")
                self.assertEqual(result["status"], "no_aligned_stream_covers_span")
                self.assertIs(result.get("decode_assisted"), True)
                self.assertIs(result.get("battery_end_window_complete"), True)

    def test_marker_without_decode_coverage_distinguishes_quiet_polls_from_no_polls(self):
        spans = {"decode_ns": [4_000_000_000, 8_000_000_000], "idle_ns": [0, 2_000_000_000]}
        for count, expected in ((13, False), (6, None)):
            stream = {**self.stream(), "aligned": True, "raw_offset_ns": 0,
                      "host_ns": [6_000_000_000, 12_000_000_000],
                      "poll_ns": self.stream()["poll_ns"][:count], "battery_current_ma": [0] * count}
            with self.subTest(polls=count):
                with patch.object(bt, "_bundle", return_value=Path("unused")), patch.object(bt, "member_spans", return_value=spans):
                    result = bt.dc_join({"root": Path("unused"), "streams": [stream]}, "member")
                self.assertIs(result.get("decode_assisted"), expected)

    def test_unknown_marker_in_one_pass_keeps_the_mean_description_unknown(self):
        computed = {"status": "ok", "E_dec_j": 2.0, "T_dec_s": 1.0, "e_j_per_step": 2 / 512,
                    "tau_s_per_step": 1 / 512, "e_half_width_j_per_step": .1 / 512,
                    "e_printed_j_per_token": 2 / 512}
        for diagnostics in ((computed, {"status": "not_evaluated"}),
                            ({"status": "not_evaluated"}, computed)):
            with self.subTest(unknown_first=diagnostics[0]["status"] == "not_evaluated"):
                result = bt.mean_of_passes([{**computed, "without_assisted": d} for d in diagnostics])
                self.assertEqual(result["status"], "ok")
                self.assertEqual(result["passes_computed"], 2)
                self.assertEqual(result["without_assisted"]["status"], "not_evaluated")

    def test_pass_mean_marker_reason_keeps_the_actual_pass_identity(self):
        computed = {"status": "ok", "E_dec_j": 2.0, "T_dec_s": 1.0, "e_j_per_step": 2 / 512,
                    "tau_s_per_step": 1 / 512, "e_half_width_j_per_step": .1 / 512, "e_printed_j_per_token": 2 / 512}
        reason = "no mapped meter stream has polls in the marker window (run member)"
        unknown = {**computed, "without_assisted": {"status": "not_evaluated", "reason": reason}}
        result = bt.mean_of_passes([computed, unknown], pass_ids=[1, 2])
        self.assertEqual(result["without_assisted"]["reason"], "pass 2: " + reason)
        result = bt.mean_of_passes([{"status": "missing"}, unknown], pass_ids=[1, 2])
        self.assertEqual(result["without_assisted"]["reason"], "pass 2: " + reason)
        blinded = {**computed, "without_assisted": {"status": "not_evaluated", "reason": "not evaluated at the blinded stage"}}
        self.assertEqual(bt.mean_of_passes([blinded])["without_assisted"]["reason"], "not evaluated at the blinded stage")


class BlindingTests(QuantityTestCase):
    def test_config_filename_and_factor_product(self):
        import hashlib
        self.assertEqual(bt.config_filename("k"), "config-" + hashlib.sha256(b"k").hexdigest()[:16] + ".json")
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "pack.json").write_text('{"factor": 1.1}')
            Path(tmp, bt.config_filename("k")).write_text('{"factor": 0.99}')
            self.assertQuantityEqual(bt.stored_factor(tmp, "k"), 1.1 * 0.99)
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


class ManifestTests(QuantityTestCase):
    def test_dict_and_list_forms(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "m.json")
            path.write_text(json.dumps({"models": {"mlx-community/Qwen3-8B-4bit": {"W_bytes": 4e9, "KV_bytes": 3e8, "R_bytes": 4.6e9}}}))
            m = bt.read_manifest(path)
            self.assertQuantityEqual(m["qwen3-8b-4bit"]["b_GB"], 4.3)
            self.assertQuantityEqual(m["qwen3-8b-4bit"]["R_GB"], 4.6)
            path.write_text(json.dumps([{"model": "Qwen3-4B-4bit", "W_GB": 2.0, "KV_GB": 0.5, "R_GB": 2.1}]))
            m = bt.read_manifest(path)
            self.assertQuantityEqual(m["qwen3-4b-4bit"]["b_GB"], 2.5)
        self.assertEqual(bt.canon("mlx-community/Qwen3_8B-4bit"), "qwen3-8b-4bit")
        self.assertEqual(bt.canon("Qwen3.5-122B-A10B-4bit (pinned jw_models copy, read only)"), "qwen3.5-122b-a10b-4bit")


class SyntheticWorldTests(QuantityTestCase):
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
            # Truth recovery: the cell's registered (h+B)/512 interval, not an agreement tolerance.
            self.assertLessEqual(abs(q["e_j_per_step"] - expected), q["e_half_width_j_per_step"], model)
            self.assertLess(q["e_lower_j_per_step"], expected)
            self.assertGreater(q["e_upper_j_per_step"], expected)
            self.assertQuantityEqual(q["e_printed_j_per_token"] * bt.PRINTED_TOKENS, q["E_dec_j"])

    def test_rest_is_dc_minus_rails_and_idle_lines_are_lower(self):
        for model, block in self.result["cells"].items():
            b = block["pass1"]["boundaries"]
            rails, dc, rest = (b[k]["quantities"]["gross"] for k in bt.BOUNDARIES)
            self.assertQuantityEqual(rest["E_dec_j"], dc["E_dec_j"] - rails["E_dec_j"])
            for k in bt.BOUNDARIES:
                self.assertLess(b[k]["quantities"]["idle_subtracted"]["E_dec_j"], b[k]["quantities"]["gross"]["E_dec_j"])
            self.assertQuantityEqual(b["rails"]["gross"]["B_j"], sum(b["rails"]["gross"]["kind_averages_j"].values()))
            self.assertEqual(set(b["rails"]["gross"]["kind_averages_j"]), set(bt.RAILS_KINDS))
            self.assertEqual(set(b["dc_input"]["gross"]["kind_averages_j"]), set(bt.DC_KINDS))
            self.assertEqual(set(b["rest"]["gross"]["kind_averages_j"]), set(bt.REST_KINDS))

    def test_defects_change_kept_units_and_secondary_lines(self):
        cell = self.result["cells"]["qwen3-4b-4bit"]["pass1"]["boundaries"]["rails"]
        self.assertEqual((cell["gross"]["n_r"], cell["gross"]["n_b"]), (8, 8))
        self.assertEqual(cell["gross"]["df"], 7)
        # A request-level harvest disclosure alone cannot select the BAT-2 decode diagnostic.
        self.assertNotIn("without_assisted", cell)
        self.assertEqual(cell["gross"]["decode_assisted_member_counts"], {"repeat": 0, "quad": 0})
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
            self.assertQuantityEqual(dev["half_width_w"], expected)
            self.assertGreater(dev["half_width_w"], q["P_half_width_w"])
            self.assertQuantityEqual(dev["deviation_w"], q["P_mean_w"] - pred["yhat"])

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
                self.assertQuantityEqual(record["scale"], expected)
                self.assertQuantityEqual(cell["gross"]["kind_averages_j"]["E_whole_window_drift_allowance_j"], record["half_allowance_scaled_j"])

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
        self.assertQuantityEqual(session["dc_input/gross"]["E_ref_j"], sum(joined) / len(joined))
        self.assertQuantityEqual(session["rest/gross"]["E_ref_j"] + session["rails/gross"]["E_ref_j"], session["dc_input/gross"]["E_ref_j"])
        self.assertLess(session["rails/idle"]["E_ref_j"], session["rails/gross"]["E_ref_j"])
        # D6: the idle-subtracted line carries the idle family's own allowance, at the cell's one
        # gross scale (Addendum 3 item 2: E_ref is the mean gross energy of the references)
        for b in bt.BOUNDARIES:
            idle = block[b]["drift_allowance_idle_family"]
            self.assertQuantityEqual(block[b]["idle_subtracted"]["kind_averages_j"]["E_whole_window_drift_allowance_j"], idle["half_allowance_scaled_j"])
            self.assertEqual(idle["scale"], block[b]["drift_allowance"]["scale"])
            self.assertNotEqual(idle["allowance_j"], block[b]["drift_allowance"]["allowance_j"])
            self.assertQuantityEqual(idle["half_allowance_scaled_j"], idle["allowance_j"] / 2 * idle["scale"])
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
            # These noisy fit points test recovery through the registered prediction interval.
            self.assertTrue(h1["models"][model]["checks"]["bytes"]["consistent"])
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
        # Truth recovery: zero must be in the intercept's registered HC3 interval.
        self.assertLessEqual(abs(h2["simple"]["P0_w"]), h2["simple"]["P0"]["half_width"])
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
        self.assertQuantityDifferent(eps["half_width"], eps["ols"]["half_width"])
        self.assertEqual(h2["se_method"], "HC3 primary, OLS beside")
        for dev in h2["tier"]["deviations"].values():
            self.assertEqual(dev["se_method"], "HC3")
            alpha = self.result["multiplicity"]["H2"]["rails"]["pass1"]["alpha_per_interval"]
            t = bt.t_two_sided(alpha, h2["tier"]["df"])
            self.assertQuantityEqual(dev["half_width_w"], t * dev["se_pred_hc3_w"] + dev["measured_half_width_w"])
            self.assertQuantityEqual(dev["ols"]["half_width_w"], t * dev["ols"]["se_pred_w"] + dev["measured_half_width_w"])

    def test_multiplicity_levels(self):
        m = self.result["multiplicity"]
        self.assertEqual(m["H1"]["family_size"], 21)
        self.assertQuantityEqual(m["H1"]["alpha_per_check"], 0.05 / 21)
        self.assertEqual(m["H2"]["rails"]["pass1"]["k_primary_intervals"], 9)
        self.assertEqual(m["H2"]["rest"]["pass1"]["k_primary_intervals"], 11)
        cell = self.result["cells"]["qwen3-8b-4bit"]["pass1"]["boundaries"]["rails"]["gross"]
        self.assertQuantityEqual(cell["alpha_family"], 0.05 / 21)
        self.assertGreater(cell["h_j"], cell["h95_j"])

    def test_neg8_record_per_session(self):
        for session_id, record in self.result["sessions"].items():
            neg8 = record["neg8"]["rails/gross"]
            self.assertEqual(neg8["status"], "ok", session_id)
            self.assertEqual(neg8["corpus_n"], 12)
            self.assertTrue(neg8["screen_passed"])
            self.assertEqual(neg8["midpoint_lost"], session_id in ("p1-s5", "p1-s6"))
            self.assertEqual(neg8["bound_terms"]["prediction_j"] / (bt.student_t_critical_95(11)), neg8["bound_terms"]["prediction_j"] / 2.201)


class TwoStageTests(QuantityTestCase):
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
            self.assertQuantityEqual(q["E_dec_j"], p["E_dec_j"])
            self.assertQuantityEqual(q["e_half_width_j_per_step"], p["e_half_width_j_per_step"])
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
            self.assertQuantityEqual(q["e_half_width_j_per_step"] * bt.DECODE_STEPS, expected)
            self.assertQuantityEqual(q["E_dec_j"], sum(c["mean_j"] for c in cells) / 2)
            # Addendum 7 item 12: P of the pass mean is mean E / mean T, half-width (mean h + mean B) / mean T
            mean_t = sum(c["duration_s"] for c in cells) / 2
            self.assertQuantityEqual(q["P_mean_w"], q["E_dec_j"] / mean_t)
            self.assertQuantityEqual(q["P_half_width_w"], expected / mean_t)
            self.assertQuantityDifferent(cells[0]["duration_s"], cells[1]["duration_s"])   # unequal passes
            self.assertEqual(q["label"], "pass_mean")
            for stored, c in zip(q["pass_half_widths_j"], cells):
                self.assertQuantityEqual(stored, c["h_j"] + c["B_j"])
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
            self.assertQuantityEqual(q["E_dec_j"], (p1 + p2) / 2)
            self.assertQuantityEqual(q["pass_difference_E_dec_j"], p2 - p1)
        for pass_key in ("pass1", "pass2", "passes_mean"):
            self.assertEqual(two["h1"]["rails"][pass_key]["active_or_resident"]["answer"], "active")
            eps = two["h2"]["rails"][pass_key]["simple"]["epsilon_j_per_GB"]
            self.assertLess(eps["lower"], truth["S_BYTES_j_per_GB"])
            self.assertGreater(eps["upper"], truth["S_BYTES_j_per_GB"])
        self.assertEqual(two["sessions"]["p2-s1"]["pass_of"]["qwen3-4b-4bit"], 2)


class OnePassFallbackTests(QuantityTestCase):
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
        self.assertQuantityEqual(q["E_dec_j"], p2["E_dec_j"])
        self.assertQuantityEqual(q["e_half_width_j_per_step"], p2["e_half_width_j_per_step"])
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


class ExportShapeTests(QuantityTestCase):
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
        self.assertQuantityEqual(row["phase_decode_j"], summary["phase_energy_j"]["decode"] * factor)
        self.assertQuantityEqual(bt.stored_factor(WORLD["one"] / "keys", row["config_key"]), factor)


class PassIdentityTests(QuantityTestCase):
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


class MeterOffsetArithmeticTests(QuantityTestCase):
    """Addendum 9 (NR1) by hand: C_j with an exact A, the M1 normalisation, the sensitivity's sign,
    the L1/L2 flags."""

    def test_a_matrix_and_coefficient_c_with_an_exact_design(self):
        # y on [1, x], x = 0, 1, 2: X'X = [[3, 3], [3, 5]], (X'X)^-1 = [[5, -3], [-3, 3]] / 6, so
        # A = (X'X)^-1 X' has rows (5, 2, -1) / 6 and (-1, 0, 1) / 2.
        fit = bt.ols([[0.0], [1.0], [2.0]], [1.0, 2.0, 4.0])
        for a, expected in zip(fit["A"], ([5 / 6, 2 / 6, -1 / 6], [-0.5, 0.0, 0.5])):
            for v, e in zip(a, expected):
                self.assertQuantityEqual(v, e)
        # beta = A y: intercept 5/6 + 4/6 - 4/6 = 5/6, slope (4 - 1) / 2 = 1.5.
        self.assertQuantityEqual(fit["coef"][0], 5 / 6)
        self.assertQuantityEqual(fit["coef"][1], 1.5)
        # C_j = sum_i |A_ji| bound_w_i with bounds (1.2, 0.6, 2.4) W: C_0 = (6 + 1.2 + 2.4) / 6 = 1.6,
        # C_1 = 0.6 + 0 + 1.2 = 1.8 (the absolute value: the slope's weights have both signs).
        # dbeta_j/ddelta = sum_i A_ji sens_i / T_i per second with sens (3, -6, 9) W over T (1, 2, 3) s,
        # i.e. (3, -3, 3) W/s: slope (-1.5 + 0 + 1.5) / 1000 = 0; intercept (2.5 - 1 - 0.5) / 1000 = 1e-3.
        points = [{"bound_w": 1.2, "sensitivity_w": 3.0, "T": 1.0}, {"bound_w": 0.6, "sensitivity_w": -6.0, "T": 2.0},
                  {"bound_w": 2.4, "sensitivity_w": 9.0, "T": 3.0}]
        iv = {"value": 1.5, "half_width": 0.5, "lower": 1.0, "upper": 2.0, "ols": {"half_width": 0.25}}
        o = bt.offset_alternative(fit, 1, iv, points, "J/GB")
        self.assertQuantityEqual(o["coefficient_C"], 1.8)
        self.assertQuantityEqual(o["offset_lower"], 1.5 - 2.3)       # beta - (t SE + C)
        self.assertQuantityEqual(o["offset_upper"], 1.5 + 2.3)
        self.assertQuantityEqual(o["offset_ols_lower"], 1.5 - 2.05)
        self.assertQuantityEqual(o["d_beta_d_delta_per_ms"], 0.0)
        self.assertEqual((o["coefficient_decision"], o["offset_decision"], o["offset_ols_decision"]),
                         ("positive", "contains zero", "contains zero"))
        self.assertEqual(o["sensitivity_units"], "J/GB per ms")
        self.assertIsNone(o["systematics_flag"])
        self.assertIsNone(o["sensitivity_flag"])
        o0 = bt.offset_alternative(fit, 0, {"value": 5 / 6, "half_width": 0.1, "lower": 5 / 6 - 0.1, "upper": 5 / 6 + 0.1,
                                            "ols": {"half_width": 0.1}}, points, "W")
        self.assertQuantityEqual(o0["coefficient_C"], 1.6)
        self.assertQuantityEqual(o0["d_beta_d_delta_per_ms"], 1e-3)
        self.assertEqual(o0["sensitivity_units"], "W per ms")
        self.assertEqual(bt.offset_alternative(fit, 1, iv, points, "")["sensitivity_units"], "per ms")

    def test_m1_normalisation_pass_averaged_joules_over_the_mean_decode_time(self):
        # Cold disposition M1: the bound is carried in joules, averaged over the passes as B is, and
        # divided by the point's mean decode time: (4 J + 2 J) / 2 over (2 s + 4 s) / 2 = 1.0 W, not
        # the mean of the per-pass ratios (2 W + 0.5 W) / 2 = 1.25 W.
        def pas(E, T, bound, sens):
            return {"status": "ok", "E_dec_j": E, "T_dec_s": T, "e_j_per_step": E / 512, "tau_s_per_step": T / 512,
                    "e_half_width_j_per_step": 0.01, "e_printed_j_per_token": E / 512,
                    "meter_offset_bound_j": bound, "meter_offset_sensitivity_w": sens,
                    "meter_offset_bound_flag": None, "meter_offset_sensitivity_flag": None}
        q = bt.mean_of_passes([pas(20.0, 2.0, 4.0, -3.0), pas(20.0, 4.0, 2.0, -1.0)])
        self.assertQuantityEqual(q["meter_offset_bound_j"], 3.0)
        self.assertQuantityEqual(q["meter_offset_bound_w"], 1.0)
        self.assertQuantityDifferent(q["meter_offset_bound_w"], 1.25)
        self.assertQuantityEqual(q["meter_offset_sensitivity_w"], -2.0)   # watts, pass mean
        self.assertQuantityEqual(q["P_mean_w"], 20.0 / 3.0)               # the same ratio of means
        # A flagged pass flags the point and withholds the bound; the sensitivity survives on its own.
        flagged = {**pas(20.0, 2.0, None, -3.0), "meter_offset_bound_flag": "meter offset bound negative on run(s) r1"}
        q = bt.mean_of_passes([flagged, pas(20.0, 4.0, 2.0, -1.0)])
        self.assertIsNone(q["meter_offset_bound_w"])
        self.assertIn("r1", q["meter_offset_bound_flag"])
        self.assertQuantityEqual(q["meter_offset_sensitivity_w"], -2.0)

    def test_sensitivity_sign_and_per_run_bound_from_the_meter_samples(self):
        # Samples at 0, 100, ..., 400 ms: idle 0.2 W before 200 ms and after 400 ms, 5 W inside.  A
        # decode window [150, 350) ms starts in idle and ends under load: a label offset delta > 0
        # pulls the idle sample before the start in and pushes the loaded sample before the end out,
        # so dE/ddelta = P_before-start - P_before-end = 0.2 - 5 = -4.8 W (energy falls with delta).
        times = [t * 1_000_000 for t in (0, 100, 200, 300, 400)]
        watts = [0.2, 0.2, 5.0, 5.0, 0.2]
        window = (150_000_000, 350_000_000)
        self.assertEqual(bt.before_edge_powers(times, watts, window), (0.2, 5.0))
        self.assertEqual(bt.edge_powers(times, watts, window), (5.0, 5.0))      # D4: the larger neighbour
        # The per-run bound is max(P_start, P_end)(r_max + dt): 5 W x (8 ms + 100 ms) = 0.54 J, half of
        # u = (P_start + P_end)(r_max + dt) = 1.08 J when the two edge powers are equal.
        p_start, p_end = bt.edge_powers(times, watts, window)
        self.assertQuantityEqual(max(p_start, p_end) * (0.008 + 0.1), 0.54)
        self.assertQuantityEqual((p_start + p_end) * (0.008 + 0.1), 1.08)
        # The reverse window (load before the start, idle before the end) has the opposite sign.
        self.assertEqual(bt.before_edge_powers(times, watts, (250_000_000, 450_000_000)), (5.0, 0.2))

    def test_offset_terms_use_the_strata_weights_and_flag_bad_runs_without_refusing(self):
        def member(i, bound, sens):
            return {"id": f"m{i}", "E": 1.0, "T": 1.0, "bounds": {}, "offset": {"bound_j": bound, "sensitivity_w": sens}}
        repeats = [member(i, 1.0, -1.0) for i in range(5)]
        quads = [{"id": f"q{k}", "members": [member(f"{k}{j}", 2.0, -3.0) for j in range(4)]} for k in range(5)]
        terms = bt.offset_terms(repeats, quads)
        self.assertQuantityEqual(terms["bound_j"], 0.2 * 1.0 + 0.8 * 2.0)
        self.assertQuantityEqual(terms["sensitivity_w"], 0.2 * -1.0 + 0.8 * -3.0)
        self.assertEqual((terms["bound_flag"], terms["sensitivity_flag"], terms["n_runs"]), (None, None, 25))
        # L1/L2: one negative bound flags the bound and names the run; one non-finite sensitivity
        # flags the sensitivity; each leaves the other term computed and nothing refuses.
        bad = bt.offset_terms([member(0, -0.5, -1.0), *repeats[1:]], quads)
        self.assertIsNone(bad["bound_j"])
        self.assertIn("m0", bad["bound_flag"])
        self.assertQuantityEqual(bad["sensitivity_w"], -2.6)
        bad = bt.offset_terms(repeats, [{"id": "q9", "members": [member("x", 2.0, float("nan"))] * 4}, *quads[1:]])
        self.assertIsNone(bad["sensitivity_w"])
        self.assertIn("mx", bad["sensitivity_flag"])
        self.assertQuantityEqual(bad["bound_j"], 1.8)
        bad = bt.offset_terms([member(0, None, -1.0), *repeats[1:]], quads)
        self.assertIn("m0", bad["bound_flag"])
        # Through the fit: a flagged point gives the systematics flag and keeps the registered interval.
        fit = bt.ols([[0.0], [1.0], [2.0]], [1.0, 2.0, 4.0])
        iv = {"value": 1.5, "half_width": 0.5, "lower": 1.0, "upper": 2.0, "ols": {"half_width": 0.25}}
        points = [{"bound_w": 1.0, "sensitivity_w": 1.0, "T": 1.0}] * 2 + [{"bound_w": None, "sensitivity_w": float("inf"), "T": 1.0,
                                                                            "bound_flag": bad["bound_flag"]}]
        o = bt.offset_alternative(fit, 1, iv, points, "J/GB")
        self.assertIsNone(o["coefficient_C"])
        self.assertIsNone(o["offset_lower"])
        self.assertIn("m0", o["systematics_flag"])
        self.assertIsNotNone(o["sensitivity_flag"])
        self.assertIsNone(o["d_beta_d_delta_per_ms"])
        self.assertEqual(o["coefficient_decision"], "positive")      # the registered interval is kept

    def test_rails_has_no_c_term_and_dc_and_rest_carry_the_alternative_on_the_synthetic_world(self):
        result = run_twin(WORLD["two"], "2")
        rails = result["h2"]["rails"]["passes_mean"]
        self.assertNotIn("offset", rails["resident_extended"]["epsilon_j_per_GB"])
        self.assertNotIn("offset_disclosure", rails)
        self.assertEqual(rails["interval_scope"], bt.INTERVAL_SCOPE)
        for boundary in ("dc_input", "rest"):
            h2 = result["h2"][boundary]["passes_mean"]
            self.assertIn("22 to 25 ms", h2["offset_disclosure"])
            self.assertIn("M13", h2["offset_disclosure"])
            self.assertEqual(h2["offset_delta_structural_bound_ms"], [22, 25])
            for fit_name, terms in (("simple", ("P0", "epsilon_j_per_GB")), ("resident_extended", ("P0", "epsilon_j_per_GB", "rho_j_per_GB")),
                                    ("tier", ("P0", "epsilon_j_per_GB", "rho_j_per_GB"))):
                for term in terms:
                    o = h2[fit_name][term]["offset"]
                    self.assertGreater(o["coefficient_C"], 0.0)
                    self.assertLess(o["offset_lower"], h2[fit_name][term]["lower"])
                    self.assertGreater(o["offset_upper"], h2[fit_name][term]["upper"])
                    self.assertIsNone(o["systematics_flag"])
                    self.assertTrue(math.isfinite(o["d_beta_d_delta_per_ms"]))
            self.assertIn("resident_adds_nothing_offset", h2["resident_extended"])
            self.assertTrue(h2["resident_extended"]["resident_adds_nothing_offset"])   # rho is 0 in this world
        rest = result["h2"]["rest"]["passes_mean"]["rest_model"]
        self.assertEqual(rest["lambda"]["offset"]["sensitivity_units"], "per ms")
        self.assertEqual(rest["c"]["offset"]["sensitivity_units"], "W per ms")
        self.assertEqual(rest["epsilon_rest_j_per_GB"]["offset"]["sensitivity_units"], "J/GB per ms")
        # Per point: the bound in W is the pass-averaged joules over the mean decode time (M1).
        q = result["cells"]["qwen3-8b-4bit"]["passes_mean"]["boundaries"]["dc_input"]["quantities"]["gross"]
        self.assertQuantityEqual(q["meter_offset_bound_w"], q["meter_offset_bound_j"] / q["T_dec_s"])
        p1 = result["cells"]["qwen3-8b-4bit"]["pass1"]["boundaries"]["dc_input"]["gross"]["meter_offset"]
        p2 = result["cells"]["qwen3-8b-4bit"]["pass2"]["boundaries"]["dc_input"]["gross"]["meter_offset"]
        self.assertQuantityEqual(q["meter_offset_bound_j"], (p1["bound_j"] + p2["bound_j"]) / 2)
        self.assertNotIn("meter_offset", result["cells"]["qwen3-8b-4bit"]["pass1"]["boundaries"]["rails"]["gross"])


def withhold(world: Path, session_id: str, model: str, *, store_present: bool):
    """Turn one of the twin's synthetic sessions into a grouped export (lead ruling 2026-10-20 item 1):
    the model's science rows leave the public CSV for a withheld store under the custody root, and
    the sidecar records the count-only locator.  store_present False removes the store afterwards."""
    import csv
    import hashlib
    pack = f"bytes-{session_id.split('-')[1]}-p{session_id[1]}"
    csv_path = world / "exports" / pack / (session_id + ".runs.csv")
    with csv_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        columns, rows = reader.fieldnames, list(reader)
    key = "bytes-decode-" + synth.canon(model)
    kept = [r for r in rows if r["config_key"] != key]
    withheld = [r for r in rows if r["config_key"] == key]
    store = world / "withheld" / pack / (session_id + ".runs.csv")
    for path, part in ((csv_path, kept), (store, withheld)):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(part)
    sidecar = csv_path.with_name(session_id + ".session.json")
    data = json.loads(sidecar.read_text())
    data["blinding"]["withheld"] = {"path": "../../withheld/" + pack + "/" + session_id + ".runs.csv",
                                    "row_count": len(withheld),
                                    "config_key_sha256": {hashlib.sha256(key.encode()).hexdigest(): len(withheld)}}
    sidecar.write_text(json.dumps(data))
    if not store_present:
        store.unlink()
    return len(withheld)


class WithheldStoreTests(QuantityTestCase):
    """Lead ruling 2026-10-20 items 1 to 4 and B6 ruling Q1 on the twin's own two-pass world, with
    Qwen3-30B-A3B's rows of each pass moved into a withheld store."""

    @classmethod
    def setUpClass(cls):
        import shutil
        cls.tmp = tempfile.TemporaryDirectory(prefix="bytes-twin-withheld-")
        cls.worlds = {}
        for case, present in (("present", (True, True)), ("one", (True, False)), ("both", (False, False))):
            world = Path(cls.tmp.name) / case
            shutil.copytree(WORLD["two"], world)
            for session_id, keep in zip(("p1-s2", "p2-s2"), present):
                withhold(world, session_id, "Qwen3-30B-A3B-4bit", store_present=keep)
            cls.worlds[case] = world

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_load_withheld_reads_the_store_or_names_the_missing_models_by_digest(self):
        manifest = bt.read_manifest(self.worlds["one"] / "bytes_manifest.json")
        self.assertEqual(manifest["qwen3-30b-a3b-4bit"]["config_key"], "bytes-decode-qwen3-30b-a3b-4bit")
        path = self.worlds["one"] / "exports/bytes-s2-p1/p1-s2.runs.csv"
        store = bt.load_withheld(path, bt.read_sidecar(path), manifest)
        self.assertEqual((len(store["rows"]), store["missing"]), (50, {}))
        path = self.worlds["one"] / "exports/bytes-s2-p2/p2-s2.runs.csv"
        store = bt.load_withheld(path, bt.read_sidecar(path), manifest)
        self.assertEqual(store["rows"], [])
        self.assertEqual(set(store["missing"]), {"qwen3-30b-a3b-4bit"})
        self.assertEqual(store["missing"]["qwen3-30b-a3b-4bit"]["row_count"], 50)
        self.assertEqual(store["missing"]["qwen3-30b-a3b-4bit"]["config_row_count"], 50)
        self.assertIsNone(bt.withheld_record(bt.read_sidecar(self.worlds["one"] / "exports/bytes-s1-p1/p1-s1.runs.csv")))

    def test_withheld_rows_enter_only_after_the_commit(self):
        world = self.worlds["present"]
        blinded = run_twin(world, "blinded", key_dir=False)
        self.assertNotIn("qwen3-30b-a3b-4bit", blinded["cells"])            # item 1: never before the commit
        self.assertFalse(blinded["inputs"]["withheld_rows_read"])
        stage1 = run_twin(world, "1")
        self.assertNotIn("qwen3-30b-a3b-4bit", stage1["cells"])
        out = world / "twin-post.json"
        argv = ["--export-dir", str(world / "exports"), "--manifest", str(world / "bytes_manifest.json"), "--stage", "blinded",
                "--stage1-commit", "0" * 40, "--out", str(out)]
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(bt.main(argv), 0)
            self.assertEqual(bt.main(argv[:-3] + ["not-a-hash", "--out", str(out)]), 1)   # refused: not a commit hash
        post = json.loads(out.read_text())
        self.assertTrue(post["inputs"]["withheld_rows_read"])
        block = post["cells"]["qwen3-30b-a3b-4bit"]
        self.assertEqual(sorted(block), ["pass1", "pass2", "passes_mean"])
        self.assertEqual(block["pass1"]["boundaries"]["rails"]["gross"]["n_r"], 10)          # blinded rails only
        self.assertEqual(block["pass1"]["boundaries"]["dc_input"]["status"], "no_archive_join")
        two = run_twin(world, "2")
        self.assertEqual(two["cells"]["qwen3-30b-a3b-4bit"]["passes_mean"]["boundaries"]["dc_input"]["quantities"]["gross"]["label"], "pass_mean")
        self.assertTrue(any(f["flag"] == "rows_withheld" and f["store_read"] for f in two["flags"]))
        self.assertEqual(two["h2"]["rails"]["passes_mean"]["n"], 10)

    def test_a_store_also_named_with_export_is_read_once(self):
        # The convention before the sidecar locator: the stage-2 caller names each withheld store
        # with --export as well.  Named first, the store must neither double the model's rows nor
        # hide the export's sidecar (tests.test_bytes_roster_drop's nine-model chain does this).
        world = self.worlds["present"]
        plain = run_twin(world, "2")
        stores = sorted((world / "withheld").rglob("*.runs.csv"))
        self.assertEqual(len(stores), 2)
        named = run_twin(world, "2", extra=[a for s in stores for a in ("--export", str(s))])
        self.assertEqual(named["sessions"], plain["sessions"])                          # row counts per session
        self.assertEqual(named["cells"], plain["cells"])                                # same function, same rows
        self.assertEqual(named["h2"], plain["h2"])
        self.assertEqual(sorted(f["session_id"] for f in named["flags"] if f["flag"] == "rows_withheld" and f["store_read"]),
                         ["p1-s2", "p2-s2"])
        p1 = named["cells"]["qwen3-30b-a3b-4bit"]["pass1"]["boundaries"]["rails"]["gross"]
        self.assertEqual((p1["n_r"], p1["n_b"]), (10, 10))       # 10 repeats, 10 quad units of 4: each run once

    def test_one_withheld_file_missing_is_a_flag_on_the_pass_and_the_point_is_one_pass(self):
        result = run_twin(self.worlds["one"], "2")
        block = result["cells"]["qwen3-30b-a3b-4bit"]
        self.assertEqual(block["pass2"]["status"], "missing")
        self.assertEqual(block["pass2"]["session_id"], "p2-s2")
        self.assertEqual(block["pass2"]["flags"], [bt.WITHHELD_MISSING])
        self.assertEqual((block["pass2"]["withheld_row_count"], block["pass2"]["withheld_config_row_count"]), (50, 50))
        for boundary in bt.BOUNDARIES:
            cell = block["pass2"]["boundaries"][boundary]
            self.assertEqual(cell["status"], "missing")
            self.assertEqual(cell["quantities"]["gross"]["status"], "missing")
            q = block["passes_mean"]["boundaries"][boundary]["quantities"]["gross"]
            self.assertEqual((q["status"], q["label"], q["flags"], q["passes_collected"], q["passes_computed"]),
                             ("ok", "one_pass", [bt.WITHHELD_MISSING], 2, 1))
            self.assertTrue(q["one_pass_after_refusal"])
            p1 = block["pass1"]["boundaries"][boundary]["quantities"]["gross"]
            self.assertQuantityEqual(q["E_dec_j"], p1["E_dec_j"])                  # D9 (a): the surviving pass
            h1 = result["h1"][boundary]["passes_mean"]["models"]["qwen3-30b-a3b-4bit"]
            self.assertIsNotNone(h1["word"])
            self.assertEqual((h1["label"], h1["flags"]), ("one_pass", [bt.WITHHELD_MISSING]))
            self.assertEqual(result["h1"][boundary]["pass2"]["models"]["qwen3-30b-a3b-4bit"]["status"], "missing")
            self.assertEqual(result["h1"][boundary]["pass1"]["models"]["qwen3-30b-a3b-4bit"]["label"], "one_pass")
            moe = result["h1"][boundary]["passes_mean"]["active_or_resident"]
            self.assertNotEqual(moe["answer"], "missing")                                  # three MoE points remain
            self.assertEqual(moe["missing_models"], [])
            h2 = result["h2"][boundary]["passes_mean"]
            self.assertEqual(h2["n"], 10)                                                  # H2 uses the point
            self.assertEqual(h2["one_pass_models"], ["qwen3-30b-a3b-4bit"])
            self.assertEqual(h2["two_pass_sensitivity"]["n"], 9)                           # D9 (c)
        self.assertIn({"flag": bt.WITHHELD_MISSING, "session_id": "p2-s2", "model": "qwen3-30b-a3b-4bit",
                       "withheld_row_count": 50, "withheld_config_row_count": 50}, result["flags"])
        self.assertEqual(result["multiplicity"]["H2"]["rest"]["passes_mean"]["k_primary_intervals"], 11)

    def test_both_withheld_files_missing_prints_the_model_missing_with_no_point_and_no_word(self):
        result = run_twin(self.worlds["both"], "2")
        block = result["cells"]["qwen3-30b-a3b-4bit"]
        self.assertEqual({k: block[k]["status"] for k in ("pass1", "pass2")}, {"pass1": "missing", "pass2": "missing"})
        for boundary in bt.BOUNDARIES:
            q = block["passes_mean"]["boundaries"][boundary]["quantities"]["gross"]
            self.assertEqual((q["status"], q["label"], q["flags"], q["passes_computed"]), ("missing", "no_pass", [bt.WITHHELD_MISSING], 0))
            self.assertNotIn("E_dec_j", q)
            h1 = result["h1"][boundary]["passes_mean"]["models"]["qwen3-30b-a3b-4bit"]
            self.assertEqual((h1["word"], h1["status"], h1["flags"]), (None, "missing", [bt.WITHHELD_MISSING]))
            moe = result["h1"][boundary]["passes_mean"]["active_or_resident"]
            self.assertEqual((moe["answer"], moe["missing_models"], moe["flags"]), ("missing", ["qwen3-30b-a3b-4bit"], [bt.WITHHELD_MISSING]))
            h2 = result["h2"][boundary]["passes_mean"]
            self.assertEqual((h2["status"], h2["n"]), ("ok", 9))                            # D9 (b): the models with points
            self.assertEqual(h2["two_pass_sensitivity"]["n"], 9)                           # D9 (c)
            self.assertEqual(h2["two_pass_sensitivity"]["excluded_models"], ["qwen3-30b-a3b-4bit"])
        self.assertEqual(result["multiplicity"]["H2"]["rails"]["passes_mean"]["k_primary_intervals"], 9)

    def test_genuinely_uncollected_optional_pass_is_one_pass_without_the_flag(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            world = Path(tmp) / "world"
            shutil.copytree(WORLD["two"], world)
            shutil.rmtree(world / "exports/bytes-s2-p2")         # the session was never collected (R6)
            shutil.rmtree(world / "archives/p2-s2")
            result = run_twin(world, "2")
        for model in ("qwen3-30b-a3b-4bit", "qwen3-8b-4bit"):
            block = result["cells"][model]
            self.assertEqual(sorted(block), ["pass1", "passes_mean"])
            q = block["passes_mean"]["boundaries"]["rails"]["quantities"]["gross"]
            self.assertEqual((q["label"], q["flags"], q["passes_collected"], q["passes_computed"]), ("one_pass", [], 1, 1))
            self.assertFalse(q["one_pass_after_refusal"])
            self.assertEqual(result["h1"]["rails"]["passes_mean"]["models"][model].get("flags"), [])
        self.assertEqual(result["h1"]["rails"]["passes_mean"]["models"]["qwen3-30b-a3b-4bit"]["label"], "one_pass")
        self.assertEqual([f for f in result["flags"] if f["flag"] == bt.WITHHELD_MISSING], [])
        h2 = result["h2"]["rails"]["passes_mean"]
        self.assertEqual(h2["n"], 10)
        # D9 (c) as the twin reads it: a point on fewer than two computed passes, however it came
        # about, prints the two-pass sensitivity line beside the primary fit.
        self.assertEqual(h2["two_pass_sensitivity"]["n"], 8)
        self.assertEqual(h2["two_pass_sensitivity"]["excluded_models"], ["qwen3-8b-4bit", "qwen3-30b-a3b-4bit"])
        self.assertNotIn("two_pass_sensitivity", run_twin(WORLD["one"], "2")["h2"]["rails"]["passes_mean"])


if __name__ == "__main__":
    unittest.main()
