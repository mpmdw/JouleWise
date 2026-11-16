"""The interim look's fit (RL-166, RL-166a). Synthetic data only: every input is written by
scripts/cadence_look_synth.py with planted parameters. No custody, campaign or v4 file exists in these tests."""
from __future__ import annotations

import builtins
import copy
import hashlib
import io
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
import unittest.mock

try:  # the fit needs numpy; the dependency-free core shards run without it (CI's look-fit job installs it)
    import numpy as np

    from joulewise.cadence_looks import fit_interim as F
    from scripts import cadence_look_synth as synth
except ModuleNotFoundError as _exc:  # pragma: no cover
    if _exc.name != "numpy":
        raise
    _NUMPY_MISSING = str(_exc)
else:
    _NUMPY_MISSING = None


def load_tests(loader, tests, pattern):
    """Without numpy the module loads and reports one skip, so shard discovery does not error."""
    if _NUMPY_MISSING is None:
        return tests

    class NumpyMissing(unittest.TestCase):
        @unittest.skip("numpy is not installed; this module runs in CI's look-fit job")
        def test_needs_numpy(self):
            pass
    return loader.loadTestsFromTestCase(NumpyMissing)


_CACHE = {}


def dataset(scenario):
    """(look_input, energy, truth, input_sha256), built once per scenario (deep-copied for the caller)."""
    if scenario not in _CACHE:
        li, en, tr = synth.build(scenario)
        _CACHE[scenario] = (li, en, tr, hashlib.sha256(synth.dump(li)).hexdigest())
    li, en, tr, sha = _CACHE[scenario]
    return copy.deepcopy(li), copy.deepcopy(en), tr, sha


_S1 = {}


def stage1_of(scenario):
    if scenario not in _S1:
        li, _, _, sha = dataset(scenario)
        _S1[scenario] = F.stage1(li, sha)
    return copy.deepcopy(_S1[scenario])


def rehash(s1):
    return hashlib.sha256(F.dump(s1)).hexdigest()


def plant_onset(s1, truth):
    """Replace the fitted onset model by the planted one (the exact-arithmetic test)."""
    on = truth["params"]["onset"]
    s1["onset"]["coefficients"] = {c: float(on[c]) for c in s1["onset"]["predictors"]}
    s1["onset"]["sigma_s"] = float(on["sigma_s"])
    return s1


class Exact(unittest.TestCase):
    """No noise, exact stamps: given the planted onset model, stage 2 recovers every planted coefficient."""

    def test_rates_and_centring_are_the_planted_ones(self):
        s1 = stage1_of("exact")
        _, _, tr, _ = dataset("exact")
        self.assertAlmostEqual(s1["rates"]["r_p"] / tr["params"]["rates"]["r_p"], 1.0, delta=1e-9)
        self.assertAlmostEqual(s1["rates"]["r_d"] / tr["params"]["rates"]["r_d"], 1.0, delta=1e-9)
        for k, v in tr["centring"].items():
            self.assertAlmostEqual(s1["centring"][k], v, delta=1e-9)

    def test_nine_coefficients_recovered_to_1e8(self):
        _, en, tr, _ = dataset("exact")
        s1 = plant_onset(stage1_of("exact"), tr)
        out = F.stage2(s1, rehash(s1), en)
        self.assertEqual(out["delta_column"], "kept")
        for ch in F.CHANNELS:
            got = out["channels"][ch]["coefficients"]
            self.assertEqual(list(got), list(F.BASE_COLS + F.HEAT_COLS) + ["delta"])
            for c, v in got.items():
                want = tr["params"][ch][c]
                self.assertLess(abs(v - want) / abs(want), 1e-8, f"{ch}.{c}")
            # no noise at all: the hot-stretch error of the full fit is zero; LODO refits the onset per fold
            self.assertLess(out["channels"][ch]["lodo"]["hot"]["max_abs"], 0.01)

    def test_planted_hot_flags_and_onsets(self):
        s1 = stage1_of("exact")
        _, _, tr, _ = dataset("exact")
        for L in s1["legs"]:
            t = tr["legs"][L["leg_key"]]
            if not L["segments"]:
                continue
            self.assertEqual([s["hot"] for s in L["segments"]], t["hot"], L["leg_key"])
            if t["first_off_observed_s"] is None:
                self.assertIsNone(L["state"]["first_off_s"])
            else:
                self.assertAlmostEqual(L["state"]["first_off_s"], t["first_off_observed_s"], delta=1e-6)
            for s, u, v in zip(L["segments"], t["u_s"], t["v_s"]):
                self.assertAlmostEqual(s["u_s"], u, delta=1e-6)
                self.assertAlmostEqual(s["v_s"], v, delta=1e-6)

    def test_inclusion_and_onset_bookkeeping(self):
        s1 = stage1_of("exact")
        _, _, tr, _ = dataset("exact")
        by = {L["leg_key"]: L for L in s1["legs"]}
        for k, t in tr["legs"].items():
            self.assertEqual(by[k]["in_energy_fit"], t["in_energy_fit"], k)
            self.assertEqual(by[k]["hp_describe"], t["hp_describe"], k)
            if t["out_of_state"] and t["in_energy_fit"]:
                self.assertEqual(by[k]["state"]["onset_use"], "left_out_start_out_of_state")
                self.assertEqual(by[k]["tau_hat_s"], 0.0)
            if t["unobserved"] and t["in_energy_fit"]:
                self.assertEqual(by[k]["state"]["onset_use"], "left_out_state_unobserved")
            if t["start_unknown"]:                               # RL-167 row 6
                self.assertEqual(by[k]["start"]["state"], "start_state_unobserved")
                self.assertTrue(by[k]["in_energy_fit"])
                self.assertEqual(by[k]["state"]["onset_use"], "left_out_state_unobserved")
                beta = np.array([s1["onset"]["coefficients"][c] for c in F.ONSET_COLS])
                z = by[k]["start"]["z"]
                self.assertAlmostEqual(by[k]["tau_hat_s"],
                                       max(0.0, float(np.array([1.0, *z, by[k]["t_p_s"]]) @ beta)), delta=1e-9)
                self.assertGreater(by[k]["tau_hat_s"], 0.0)
            if t["missing_start"]:
                self.assertEqual(by[k]["start"]["status"], "start_reading_missing")
                self.assertFalse(by[k]["in_energy_fit"])
        left = s1["onset"]["left_out"]
        self.assertEqual(left["start_out_of_state"], 2)
        self.assertEqual(left["state_unobserved"], 3)          # two in-turn gaps and one Unknown start
        self.assertEqual(left["start_reading_missing"], 2)
        self.assertEqual(s1["counts"]["type_T"], 1)
        # one planted km003c failure, plus the G0 timeout (no leg interval for rules 3 and 4)
        self.assertEqual(s1["counts"]["excluded_by_rule"]["km003c_clean"], 2)
        self.assertEqual(s1["counts"]["excluded_by_rule"]["ran_to_cap"], 1)
        self.assertFalse(s1["tripwires"]["any"])


class Noisy(unittest.TestCase):
    """Realistic noise, per-leg rate jitter, onsets fitted: every planted coefficient within 4 cluster SEs."""

    @classmethod
    def setUpClass(cls):
        _, en, cls.truth, _ = dataset("noisy")
        s1 = stage1_of("noisy")
        cls.s1 = s1
        cls.out = F.stage2(s1, rehash(s1), en)

    def test_coefficients_within_4_se(self):
        for ch in F.CHANNELS:
            c = self.out["channels"][ch]
            for i, name in enumerate(c["columns"]):
                se = math.sqrt(c["covariance"][i][i])
                want = self.truth["params"][ch][name]
                self.assertLess(abs(c["coefficients"][name] - want), 4 * se, f"{ch}.{name}")

    def test_onset_recovered(self):
        on, got = self.truth["params"]["onset"], self.s1["onset"]
        self.assertEqual(got["status"], "estimable")
        self.assertTrue(got["converged"])
        tol = {"intercept": 15.0, "tf08_c": 1.5, "fan_rpm": 0.003, "tv0h_excess_c": 1.5, "t_p_s": 0.25}
        for k, t in tol.items():
            self.assertLess(abs(got["coefficients"][k] - on[k]), t, k)
        self.assertLess(abs(got["sigma_s"] - on["sigma_s"]), 4.0)
        self.assertEqual(got["count_only_cut"]["form"], "tau_hat_minus_2rms")
        self.assertAlmostEqual(got["count_only_cut"]["offset_s"], 2 * got["lodo"]["rms_s"])

    def test_hot_stretch_passes_and_heat_columns_matter(self):
        g = self.out["channels"]["gpu_rail"]["lodo"]
        self.assertEqual(g["hot"]["verdict"], "passes")
        self.assertGreater(g["no_heat"]["hot"]["max_abs"], 3 * g["hot"]["max_abs"])
        self.assertEqual(self.out["qualified_interim_half"]["verdict"], "passes")
        self.assertEqual(sorted(g["hot"]["counted_days"]),
                         sorted(d for d, n in g["hot"]["n_hot_legs_per_day"].items() if n >= 3))

    def test_output_has_no_per_leg_energy(self):
        F.output_check(self.out)
        text = json.dumps(self.out).lower().replace("joulewise", "")
        for word in ("joule", "watt", "power", "energy"):
            self.assertFalse(word in text, word)
        for ch in F.CHANNELS:
            for v in self.out["channels"][ch]["residuals"]["leg"].values():
                self.assertLess(abs(v), 0.2)

    def test_prefix_bias_has_three_lengths_and_intervals(self):
        for ch in F.CHANNELS:
            pb = self.out["channels"][ch]["prefix_bias"]
            self.assertEqual({k: v["prefix_len"] for k, v in pb.items()}, {"1.10": 3724, "1.30": 3151, "1.374": 2981})
            for v in pb.values():
                lo, hi = v["ci90"]
                self.assertLess(lo, v["estimate"])
                self.assertLess(v["estimate"], hi)
                self.assertEqual(v["n_days"], 5)

    def test_marked_span_print(self):
        ms = self.out["channels"]["gpu_rail"]["marked_sensitivity"]
        self.assertEqual(ms["marked_spans"], ["dev-04-s02"])
        self.assertLess(ms["n_legs_without"], self.out["channels"]["gpu_rail"]["n_legs"])
        self.assertIsNotNone(ms["coefficients_without"])


class Branches(unittest.TestCase):

    def run2(self, scenario):
        _, en, tr, _ = dataset(scenario)
        s1 = stage1_of(scenario)
        return s1, F.stage2(s1, rehash(s1), en), tr

    def test_onset_not_estimable_drops_delta_and_keeps_116(self):
        s1, out, _ = self.run2("onset_not_estimable")
        self.assertEqual(s1["onset"]["status"], "not_estimable")
        self.assertEqual(s1["onset"]["count_only_cut"], {"form": "fixed_116_s", "offset_s": None, "fixed_s": 116.0})
        self.assertEqual(out["delta_column"], "dropped_onset_not_estimable")
        for ch in F.CHANNELS:
            self.assertNotIn("delta", out["channels"][ch]["columns"])
            self.assertEqual(len(out["channels"][ch]["covariance"]), 8)
        self.assertTrue(all(L["tau_hat_s"] is None for L in s1["legs"]
                            if not (L.get("start") and L["start"]["state"] == "start_out_of_state")))

    def test_few_hot_days_is_not_evaluable(self):
        _, out, _ = self.run2("few_hot_days")
        self.assertEqual(out["channels"]["gpu_rail"]["lodo"]["hot"]["verdict"], "not_evaluable")
        self.assertEqual(out["qualified_interim_half"]["verdict"], "not_evaluable")

    def test_no_heat_world_gives_heat_terms_near_zero(self):
        _, out, tr = self.run2("no_heat")
        for ch in F.CHANNELS:
            c = out["channels"][ch]
            for i, name in enumerate(c["columns"]):
                if name in F.HEAT_COLS + (F.DELTA_COL,):
                    self.assertLess(abs(c["coefficients"][name]), 4 * math.sqrt(c["covariance"][i][i]), name)

    def test_estimable_needs_12_uncensored_on_3_days(self):
        cells = [2000] * 6 + [10000] * 6
        self.assertEqual(F.onset_estimable([False] * 12, ["a"] * 4 + ["b"] * 4 + ["c"] * 4, cells)[0], True)
        self.assertEqual(F.onset_estimable([False] * 11 + [True], ["a"] * 4 + ["b"] * 4 + ["c"] * 4, cells)[0], False)
        self.assertEqual(F.onset_estimable([False] * 12, ["a"] * 6 + ["b"] * 6, cells)[0], False)
        # RL-166b B-3: at least 4 uncensored in each of at least two cells
        self.assertEqual(F.onset_estimable([False] * 12, ["a"] * 4 + ["b"] * 4 + ["c"] * 4,
                                           [2000] * 9 + [10000] * 3)[0], False)
        self.assertEqual(F.onset_estimable([False] * 12, ["a"] * 4 + ["b"] * 4 + ["c"] * 4,
                                           [2000] * 8 + [10000] * 4)[0], True)

    def test_tripwires(self):
        li, _, _, _ = dataset("noisy")
        for leg in li["legs"]:
            if leg["span_id"].startswith(("dev-04", "dev-05", "hp-01")):
                leg["inclusion"]["g0_released"] = False
        s1 = F.stage1(li, "0" * 64)
        t = s1["tripwires"]
        self.assertTrue(t["dev_included_below_45"]["trips"])
        self.assertTrue(t["hp01_below_9"]["trips"])
        self.assertEqual(t["hp01_below_9"]["value"], 0)
        self.assertTrue(t["any"])


class Conventions(unittest.TestCase):
    """RL-166a's column, unit by unit."""

    def leg(self):
        return {"prefill_tokens": 10000, "start": {"z": [1.0, 2.0, 3.0]}}

    def test_block0_n_255_and_c_P_plus_128(self):
        s = {"kind": "decode", "edge_lo": 0, "edge_hi": 255, "tok_first": 0, "tok_last": 255, "n_tokens": 256,
             "u_s": 10.0, "v_s": 30.0}
        row = F._design_row(self.leg(), s, "decode", list(F.BASE_COLS), None)
        self.assertEqual(row[2], 255.0)
        self.assertEqual(row[3], 255.0 * 10128.0)
        self.assertEqual(row[4], 255.0 * 10000.0)

    def test_block_k_n_256_and_c(self):
        k = 3
        s = {"kind": "decode", "edge_lo": 256 * k - 1, "edge_hi": 256 * k + 255, "tok_first": 256 * k,
             "tok_last": 256 * k + 255, "n_tokens": 256, "u_s": 10.0, "v_s": 30.0}
        row = F._design_row(self.leg(), s, "decode", list(F.BASE_COLS), None)
        self.assertEqual(row[2], 256.0)
        self.assertEqual(row[3], 256.0 * (10000 + 256 * k + 127.5))

    def test_tail_n_and_c(self):
        s = {"kind": "prefix_tail", "edge_lo": 3583, "edge_hi": 3723, "tok_first": 3584, "tok_last": 3723,
             "n_tokens": 140, "u_s": 10.0, "v_s": 30.0}
        row = F._design_row(self.leg(), s, "decode", list(F.BASE_COLS), None)
        self.assertEqual(row[2], 140.0)
        self.assertEqual(row[3], 140.0 * (10000 + (3584 + 3723) / 2))

    def test_heat_and_step_columns(self):
        s = {"kind": "decode", "edge_lo": 255, "edge_hi": 511, "tok_first": 256, "tok_last": 511, "n_tokens": 256,
             "u_s": 10.0, "v_s": 30.0}
        cols = list(F.BASE_COLS + F.HEAT_COLS) + ["delta"]
        tiny = 1e-9                                       # sigma under 1e-6 s: the old overlap (B-1)
        row = dict(zip(cols, F._design_row(self.leg(), s, "decode", cols, (25.0, tiny, False))))
        self.assertEqual(row["k_tf08"], 20.0 * 20.0 * 1.0)
        self.assertEqual(row["k_fan"], 20.0 * 20.0 * 2.0)
        self.assertEqual(row["k_tv0h"], 20.0 * 20.0 * 3.0)
        self.assertEqual(row["delta"], 5.0)
        self.assertEqual(dict(zip(cols, F._design_row(self.leg(), s, "decode", cols, (-5.0, tiny, False))))["delta"], 20.0)
        self.assertEqual(dict(zip(cols, F._design_row(self.leg(), s, "decode", cols, (40.0, tiny, False))))["delta"], 0.0)
        self.assertEqual(dict(zip(cols, F._design_row(self.leg(), s, "decode", cols, (900.0, 15.0, True))))["delta"], 20.0)

    def test_turn_sum_of_heat_is_half_T_squared(self):
        """Q1: summed over the tiling segments, d*m sums to T^2/2 and the step to max(0, T - tau)."""
        s1 = stage1_of("exact")
        L = next(L for L in s1["legs"] if L["in_energy_fit"])
        cols = list(F.BASE_COLS + F.HEAT_COLS) + ["delta"]
        rows = [dict(zip(cols, F._design_row(L, s, s["kind"], cols, (100.0, 1e-9, False)))) for s in L["segments"]]
        T = L["segments"][-1]["v_s"]
        self.assertAlmostEqual(T, L["load_s"], delta=1e-9)
        self.assertAlmostEqual(sum(r["k_tf08"] for r in rows), 0.5 * T * T * L["start"]["z"][0], delta=1e-6)
        self.assertAlmostEqual(sum(r["delta"] for r in rows), T - 100.0, delta=1e-9)

    def test_rates_use_n_minus_1(self):
        s1 = stage1_of("exact")
        self.assertAlmostEqual(s1["rates"]["r_d"], 12.8, delta=1e-9)

    def test_off_state_definitions(self):
        turn = {"turn_start_s": 100.0, "last_token_s": 200.0,
                "journal": [{"t_s": 99.0, "os_level": 1, "pm_state": "Nominal", "pm_fresh": True},
                            {"t_s": 150.0, "os_level": 0, "pm_state": "Unknown", "pm_fresh": True},
                            {"t_s": 160.0, "os_level": 2, "pm_state": "Nominal", "pm_fresh": False},
                            {"t_s": 170.0, "os_level": 0, "pm_state": "Moderate", "pm_fresh": True}],
                "native_pm": [{"t_end_s": 155.0, "state": None}, {"t_end_s": 165.0, "state": "Heavy"}]}
        self.assertEqual(F.first_off(turn), (60.0, "os_level_above_0"))
        turn["journal"][2]["os_level"] = 0
        self.assertEqual(F.first_off(turn), (65.0, "native_pm_state_off"))
        turn["native_pm"][1]["t_end_s"] = 200.5          # outside (start, last token]
        self.assertEqual(F.first_off(turn), (70.0, "journal_pm_state_off"))

    def test_t_quantile(self):
        self.assertAlmostEqual(F.t_quantile(0.95, 4), 2.131847, places=5)
        self.assertAlmostEqual(F.t_quantile(0.95, 1), 6.313752, places=5)
        self.assertAlmostEqual(F.t_quantile(0.95, 30), 1.697261, places=5)


class CensoredNormal(unittest.TestCase):

    def test_recovers_a_large_tobit(self):
        rng = np.random.default_rng(7)
        n = 3000
        X = np.column_stack([np.ones(n), rng.normal(0, 1, n), rng.normal(0, 2, n)])
        beta = np.array([200.0, -15.0, 6.0])
        ystar = X @ beta + rng.normal(0, 12.0, n)
        c = rng.uniform(170, 260, n)
        cen = ystar > c
        y = np.where(cen, c, ystar)
        f = F.censored_normal_fit(X, y, cen)
        self.assertTrue(f["converged"])
        self.assertLess(np.max(np.abs(f["beta"] - beta) / np.array([1.0, 1.0, 1.0])), 1.0)
        self.assertLess(abs(f["sigma"] - 12.0), 0.6)

    def test_no_censoring_equals_ols(self):
        rng = np.random.default_rng(8)
        X = np.column_stack([np.ones(40), rng.normal(0, 1, 40)])
        y = X @ np.array([5.0, 2.0]) + rng.normal(0, 1, 40)
        f = F.censored_normal_fit(X, y, np.zeros(40, dtype=bool))
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        self.assertLess(np.max(np.abs(f["beta"] - b)), 1e-8)
        res = y - X @ b
        self.assertAlmostEqual(f["sigma"], math.sqrt(res @ res / 40), delta=1e-8)   # ML sigma


class Blind(unittest.TestCase):
    """Stage 1 is a function of non-energy fields only; no in-turn reading enters the energy fit."""

    def test_stage1_ignores_in_turn_readings(self):
        li, en, _, _ = dataset("noisy")
        s1 = F.stage1(li, "a" * 64)
        for leg in li["legs"]:
            if leg["turn"]:
                ts = leg["turn"]["turn_start_s"]
                for r in leg["turn"]["journal"]:
                    if r["t_s"] > ts:
                        r["tf08_c"], r["fan_rpm"], r["tv0h_c"] = 99.0, 9999.0, 99.0
        self.assertEqual(F.dump(F.stage1(li, "a" * 64)), F.dump(s1))

    def test_stage1_reads_no_energy_argument(self):
        li, _, _, sha = dataset("exact")
        with unittest.mock.patch.object(builtins, "open", side_effect=AssertionError("stage 1 opened a file")):
            F.stage1(li, sha)


class Refusals(unittest.TestCase):

    def refuse1(self, mutate):
        li, _, _, _ = dataset("exact")
        mutate(li)
        with self.assertRaises(F.LookInputError):
            F.stage1(li, "0" * 64)

    def first_turn(self, li):
        return next(leg for leg in li["legs"] if leg["turn"])

    def test_unknown_and_missing_keys(self):
        self.refuse1(lambda li: self.first_turn(li).update(extra=1))
        self.refuse1(lambda li: self.first_turn(li).pop("g0_role"))
        self.refuse1(lambda li: self.first_turn(li)["turn"]["journal"][0].update(tv1h_c=1.0))

    def test_forbidden_fields(self):
        for k in ("condition", "slot_id", "instruction", "start_band"):
            self.refuse1(lambda li, k=k: self.first_turn(li)["turn"]["journal"][0].update({k: 1}))

    def test_repeated_leg_and_unknown_span(self):
        self.refuse1(lambda li: li["legs"].append(copy.deepcopy(self.first_turn(li))))
        self.refuse1(lambda li: self.first_turn(li).update(span_id="nope"))

    def test_bad_numbers_and_order(self):
        self.refuse1(lambda li: self.first_turn(li)["turn"].update(turn_start_s=float("nan")))
        self.refuse1(lambda li: self.first_turn(li)["turn"]["segments"].reverse())
        self.refuse1(lambda li: self.first_turn(li)["turn"]["segments"].pop())
        self.refuse1(lambda li: self.first_turn(li)["turn"].update(decode_tokens=4000))
        self.refuse1(lambda li: self.first_turn(li)["turn"]["segments"][3].update(edge_lo=700))
        self.refuse1(lambda li: self.first_turn(li)["turn"]["journal"].reverse())
        self.refuse1(lambda li: self.first_turn(li)["turn"]["journal"].append(
            dict(self.first_turn(li)["turn"]["journal"][-1], t_s=1e12)))
        self.refuse1(lambda li: self.first_turn(li)["turn"]["prefix_tails"].pop())

    def test_type_t_with_a_turn(self):
        def m(li):
            t = next(leg for leg in li["legs"] if leg["leg_type"] == "T")
            t["turn"] = copy.deepcopy(self.first_turn(li)["turn"])
        self.refuse1(m)

    def test_stage2_refusals(self):
        _, en, tr, _ = dataset("exact")
        s1 = stage1_of("exact")
        h = rehash(s1)
        with self.assertRaises(F.LookInputError):
            F.stage2(s1, "0" * 64, en)                     # stage-1 hash mismatch
        e2 = copy.deepcopy(en)
        e2["input_sha256"] = "0" * 64
        with self.assertRaises(F.LookInputError):
            F.stage2(s1, h, e2)                            # energy bound to another input
        e2 = copy.deepcopy(en)
        e2["legs"].pop(next(iter(e2["legs"])))
        with self.assertRaises(F.LookInputError):
            F.stage2(s1, h, e2)                            # a leg missing
        e2 = copy.deepcopy(en)
        e2["legs"]["dev-01-s02/L005"] = copy.deepcopy(next(iter(en["legs"].values())))   # an excluded leg
        with self.assertRaises(F.LookInputError):
            F.stage2(s1, h, e2)
        e2 = copy.deepcopy(en)
        next(iter(e2["legs"].values()))["gpu_rail"]["segments"].pop()
        with self.assertRaises(F.LookInputError):
            F.stage2(s1, h, e2)
        e2 = copy.deepcopy(en)
        next(iter(e2["legs"].values()))["dc_in"]["segments"][2] = float("inf")
        with self.assertRaises(F.LookInputError):
            F.stage2(s1, h, e2)

    def test_output_check_refuses_energy(self):
        with self.assertRaises(ValueError):
            F.output_check({"channels": {"gpu_rail": {"leg_energy": 1.0}}})
        with self.assertRaises(ValueError):
            F.output_check({"x": {"dev-01-s01/L001": 0.01}})
        # Sol cold seat 3: a relative residual of any finite size is valid (a ratio by construction)
        F.output_check({"channels": {"gpu_rail": {"residuals": {"leg": {"dev-01-s01/L001": 5.12},
                                                                "hot_stretch": {"dev-01-s01/L001": -1.5}}}}})
        with self.assertRaises(ValueError):
            F.output_check({"channels": {"gpu_rail": {"residuals": {"leg": {"dev-01-s01/L001": float("inf")}}}}})


if __name__ == "__main__":
    unittest.main()


class Pins(unittest.TestCase):
    """The ruled constants (RL-166 Q3, Q4, Q8; RL-149 §1.3)."""

    def test_constants(self):
        self.assertEqual(F.QUALIFIED_THRESHOLD, 0.02)
        self.assertEqual((F.MIN_COUNTED_DAYS, F.MIN_HOT_LEGS_PER_DAY), (3, 3))
        self.assertEqual((F.ONSET_MIN_UNCENSORED, F.ONSET_MIN_DAYS, F.COUNT_ONLY_CUT_FIXED_S), (12, 3, 116.0))
        self.assertEqual((F.START_MAX_AGE_S, F.UNOBSERVED_GAP_S, F.BLOCK), (2.0, 2.0, 256))
        self.assertEqual(F.PREFIX, {"1.10": 3724, "1.30": 3151, "1.374": 2981})
        self.assertEqual(F.TRIP, {"dev_included": 45, "days": 4, "cell": 10, "start_invalid_frac": 0.10, "hp01": 9})
        self.assertEqual(F.OK_PM, ("Nominal", "Unknown", None))


class Stage2Internals(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _, cls.en, cls.tr, _ = dataset("noisy")
        cls.s1 = stage1_of("noisy")

    def test_stage2_runs_the_output_check(self):
        with unittest.mock.patch.object(F, "output_check", side_effect=ValueError("checked")):
            with self.assertRaises(ValueError):
                F.stage2(self.s1, rehash(self.s1), self.en)

    def test_covariance_is_cr1_clustered_by_leg(self):
        """An independent sandwich, clustered by leg, on the full-data design."""
        out = F.stage2(self.s1, rehash(self.s1), self.en)
        c = out["channels"]["gpu_rail"]
        on = self.s1["onset"]
        model = {"cols": on["predictors"], "beta": np.array([on["coefficients"][k] for k in on["predictors"]]),
                 "sigma": on["sigma_s"]}
        X, y, g = [], [], []
        onsets = F._onsets([L for L in self.s1["legs"] if L["in_energy_fit"]], model)
        for L in self.s1["legs"]:
            if not L["in_energy_fit"]:
                continue
            for s, e in zip(L["segments"], self.en["legs"][L["leg_key"]]["gpu_rail"]["segments"]):
                X.append(F._design_row(L, s, s["kind"], c["columns"], onsets[L["leg_key"]]))
                y.append(e)
                g.append(L["leg_key"])
        X, y = np.array(X), np.array(y)
        b = np.array([c["coefficients"][k] for k in c["columns"]])
        with np.errstate(all="ignore"):
            e = y - X @ b
            bread = np.linalg.inv(X.T @ X)
            meat = sum(np.outer(X[[i for i, h in enumerate(g) if h == k]].T @ e[[i for i, h in enumerate(g) if h == k]],
                                X[[i for i, h in enumerate(g) if h == k]].T @ e[[i for i, h in enumerate(g) if h == k]])
                       for k in sorted(set(g)))
            n, p, G = len(y), X.shape[1], len(set(g))
            V = (G / (G - 1)) * ((n - 1) / (n - p)) * bread @ meat @ bread
        got = np.array(c["covariance"])
        for i in range(p):
            self.assertAlmostEqual(got[i, i] / V[i, i], 1.0, delta=1e-6, msg=c["columns"][i])

    def test_prefix_bias_sign(self):
        """Measured prefixes made 1 % dearer: short residuals rise, so long minus short falls (R-11)."""
        base = F.stage2(self.s1, rehash(self.s1), self.en)["channels"]["gpu_rail"]["prefix_bias"]
        en = copy.deepcopy(self.en)
        for e in en["legs"].values():
            for k in e["gpu_rail"]["prefix_tails"]:
                e["gpu_rail"]["prefix_tails"][k] *= 1.0 + 0.01 * 30
        bumped = F.stage2(self.s1, rehash(self.s1), en)["channels"]["gpu_rail"]["prefix_bias"]
        for lab in F.PREFIX:
            self.assertLess(bumped[lab]["estimate"], base[lab]["estimate"] - 0.05, lab)

    def test_fold_with_under_6_uncensored_drops_delta(self):
        """RL-167 row 7: a fold fits its onset with at least 6 uncensored onsets (no 12-on-3 rule); the fold
        holding out the day with 7 of 12 uncensored onsets keeps 5 and drops delta; the others keep it."""
        s1 = copy.deepcopy(self.s1)
        unc = {}
        for L in s1["legs"]:
            if L["in_energy_fit"] and L["state"]["onset_use"] == "uncensored":
                unc.setdefault(L["day"], []).append(L["leg_key"])
        days = sorted(unc, key=lambda d: -len(unc[d]))
        quota = {days[0]: 7, days[1]: 3, days[2]: 2}
        keep = {k for d, n in quota.items() for k in unc[d][:n]}
        for L in s1["legs"]:
            st = L.get("state")
            if L["in_energy_fit"] and st["onset_use"] == "uncensored" and L["leg_key"] not in keep:
                st["onset_use"] = "censored"
                st["censored_at_s"] = L["load_s"] + 1000.0
                st["first_off_s"] = None
        out = F.stage2(s1, rehash(s1), self.en)
        self.assertEqual(out["delta_column"], "kept")
        for ch in F.CHANNELS:
            self.assertEqual(out["channels"][ch]["lodo"]["folds_delta_dropped"], [days[0]])


class Guards(unittest.TestCase):

    def test_start_reading_needs_a_fresh_stamp(self):
        turn = {"turn_start_s": 100.0, "journal": [{"t_s": 99.5, "os_level": 0, "pm_state": "Nominal",
                                                     "pm_fresh": False, "tf08_c": 40.0, "fan_rpm": 2000.0,
                                                     "tv0h_c": 60.0}]}
        self.assertEqual(F.start_reading(turn, 58.0)[0], "start_reading_missing")
        turn["journal"][0]["pm_fresh"] = True
        self.assertEqual(F.start_reading(turn, 58.0)[:2], ("ok", "in_state"))
        turn["journal"][0]["t_s"] = 97.9
        self.assertEqual(F.start_reading(turn, 58.0)[0], "start_reading_missing")

    def test_tau_hat_is_floored_at_zero(self):
        L = {"start": {"state": "in_state", "z": [0.0, 0.0, 0.0]}, "t_p_s": 10.0}
        cols = list(F.ONSET_COLS)
        self.assertEqual(F.tau_hat(L, {"cols": cols, "beta": np.array([-50.0, 0, 0, 0, 1.0]), "sigma": 1.0}), 0.0)
        self.assertEqual(F.tau_hat(L, {"cols": cols, "beta": np.array([50.0, 0, 0, 0, 1.0]), "sigma": 1.0}), 60.0)

    def test_forbidden_fields_anywhere(self):
        for k in ("condition", "Slot_ID", "instruction_kind", "start_band"):
            with self.assertRaises(F.LookInputError):
                F._no_forbidden({"a": [{"b": {k: 1}}]})


class RL167(unittest.TestCase):
    """RL-167 §2's analyst rows, each with a test that fails without the change."""

    def turn(self, journal, native=()):
        return {"turn_start_s": 100.0, "last_token_s": 200.0, "journal": journal, "native_pm": list(native)}

    def j(self, t, lvl=0, pm="Nominal", fresh=True):
        return {"t_s": t, "os_level": lvl, "pm_state": pm, "pm_fresh": fresh, "tf08_c": 40.0, "fan_rpm": 2000.0,
                "tv0h_c": 60.0}

    def test_row6_start_state(self):
        self.assertEqual(F.start_state_of(self.j(0, 0, "Nominal")), "in_state")
        self.assertEqual(F.start_state_of(self.j(0, 0, "Unknown")), "start_state_unobserved")
        self.assertEqual(F.start_state_of(self.j(0, 0, None)), "start_state_unobserved")
        self.assertEqual(F.start_state_of(self.j(0, None, "Nominal")), "start_state_unobserved")
        self.assertEqual(F.start_state_of(self.j(0, 1, "Unknown")), "start_out_of_state")
        self.assertEqual(F.start_state_of(self.j(0, None, "Moderate")), "start_out_of_state")
        t = self.turn([self.j(99.5, 0, "Unknown")])
        self.assertEqual(F.start_reading(t, 58.0)[:2], ("ok", "start_state_unobserved"))

    def test_row4_only_fresh_state_counts_against_the_gap(self):
        base = [self.j(99.5)] + [self.j(100.5 + i) for i in range(100)]
        self.assertIsNone(F.unobserved_at(self.turn(base)))
        for bad in ({"pm_state": "Unknown"}, {"pm_state": None}, {"os_level": None}, {"pm_fresh": False}):
            jj = [dict(r) for r in base]
            for r in jj[10:14]:                        # readings at 109.5 .. 112.5 do not count
                r.update(bad)
            self.assertEqual(F.unobserved_at(self.turn(jj)), 8.5, bad)
        # native rows never count: a journal gap stays a gap however many native rows fall in it
        jj = base[:10] + base[14:]
        self.assertEqual(F.unobserved_at(self.turn(jj, [{"t_end_s": 110.0 + i * 0.5, "state": "Nominal"}
                                                        for i in range(8)])), 8.5)

    def test_row5_anchor_at_turn_start_without_fresh_carry_in(self):
        later = [self.j(102.5 + i) for i in range(98)]
        # carry-in not fresh state: anchor 100.0; next fresh-state reading at 102.5 -> gap 2.5 s fires at 0
        self.assertEqual(F.unobserved_at(self.turn([self.j(99.5, 0, "Unknown")] + later)), 0.0)
        # fresh carry-in at 99.9: 99.9 -> 102.5 is 2.6 s; the earlier anchor less the start, floored at 0
        self.assertEqual(F.unobserved_at(self.turn([self.j(99.9)] + later)), 0.0)
        # fresh carry-in and a fresh reading at 101 bridge it
        self.assertIsNone(F.unobserved_at(self.turn([self.j(99.9), self.j(101.0)] + later)))

    def test_row8_main_fit_not_converged_is_not_estimable(self):
        li, _, _, sha = dataset("noisy")
        real = F.censored_normal_fit

        def no_conv(*a, **k):
            f = real(*a, **k)
            f["converged"] = False
            return f
        with unittest.mock.patch.object(F, "censored_normal_fit", no_conv):
            s1 = F.stage1(li, sha)
        on = s1["onset"]
        self.assertEqual((on["status"], on["converged"], on["coefficients"]), ("not_estimable", False, None))
        self.assertEqual(on["count_only_cut"]["form"], "fixed_116_s")

    def test_row12_pooled_is_every_hot_block(self):
        _, en, _, _ = dataset("noisy")
        s1 = stage1_of("noisy")
        # leave one day with fewer than three hot legs, so counted days and all days differ
        days = sorted({L["day"] for L in s1["legs"] if L["in_energy_fit"]})
        thin = days[0]
        hot_legs = [L for L in s1["legs"] if L["in_energy_fit"] and L["day"] == thin and any(s["hot"] for s in L["segments"])]
        for L in hot_legs[2:]:
            for s in L["segments"]:
                s["hot"] = False
        out = F.stage2(s1, rehash(s1), en)
        hot = out["channels"]["gpu_rail"]["lodo"]["hot"]
        self.assertNotIn(thin, hot["counted_days"])
        M = {}
        for L in s1["legs"]:
            if L["in_energy_fit"]:
                y = en["legs"][L["leg_key"]]["gpu_rail"]["segments"]
                M[L["day"]] = M.get(L["day"], 0.0) + sum(e for e, s in zip(y, L["segments"]) if s["hot"])
        want = sum(hot["per_day"][d] * M[d] for d in hot["per_day"]) / sum(M[d] for d in hot["per_day"])
        self.assertAlmostEqual(hot["pooled"], want, delta=1e-12)
        self.assertIn(thin, hot["per_day"])

    def test_row16_marked_print_refits_onset_on_remaining_legs(self):
        _, en, _, _ = dataset("noisy")
        s1 = stage1_of("noisy")
        calls = []
        real = F.fit_onset_fold

        def spy(legs_d, keys, cols):
            calls.append(sorted(keys))
            return real(legs_d, keys, cols)
        with unittest.mock.patch.object(F, "fit_onset_fold", spy):
            F.stage2(s1, rehash(s1), en)
        keep = sorted(L["leg_key"] for L in s1["legs"] if L["in_energy_fit"] and not L["marks"])
        self.assertIn(keep, calls)
        with unittest.mock.patch.object(F, "fit_onset_fold", lambda legs_d, keys, cols: None):
            out = F.stage2(s1, rehash(s1), en)
        ms = out["channels"]["gpu_rail"]["marked_sensitivity"]
        self.assertIsNone(ms["coefficients_without"])
        self.assertIsNone(ms["lodo_hot_max_abs_without"])

    def test_row20_null_key_and_row21_hp_type_a(self):
        s1 = stage1_of("noisy")
        self.assertIn("null", s1["counts"]["by_g0_role"])
        self.assertNotIn("None", s1["counts"]["by_g0_role"])
        li, _, _, _ = dataset("noisy")
        hp = next(leg for leg in li["legs"] if leg["span_id"].startswith("hp-01") and leg["turn"]
                  and all(leg["inclusion"].values()))
        before = F.stage1(copy.deepcopy(li), "0" * 64)["tripwires"]["hp01_below_9"]["value"]
        hp["leg_type"], hp["turn"] = "T", None
        after = F.stage1(li, "0" * 64)
        self.assertEqual(after["tripwires"]["hp01_below_9"]["value"], before - 1)
        L = next(x for x in after["legs"] if x["leg_key"] == hp["leg_key"])
        self.assertEqual(L["not_in_fit_reason"], "type_T")

    def test_reason_precedence_type_t_before_excluded(self):
        li, _, _, _ = dataset("noisy")
        t = next(leg for leg in li["legs"] if leg["leg_type"] == "T")
        t["inclusion"]["g0_released"] = False
        L = next(x for x in F.stage1(li, "0" * 64)["legs"] if x["leg_key"] == t["leg_key"])
        self.assertEqual(L["not_in_fit_reason"], "type_T")

    def test_row22_level_e_is_energy_fit_legs_only(self):
        _, en, _, _ = dataset("noisy")
        s1 = stage1_of("noisy")
        self.assertEqual(set(en["legs"]), {L["leg_key"] for L in s1["legs"] if L["in_energy_fit"]})
        hp = next(L for L in s1["legs"] if L["hp_describe"])
        e2 = copy.deepcopy(en)
        e2["legs"][hp["leg_key"]] = copy.deepcopy(next(iter(en["legs"].values())))
        with self.assertRaises(F.LookInputError):
            F.stage2(s1, rehash(s1), e2)

    def test_r18_non_positive_measured_refuses(self):
        _, en, _, _ = dataset("noisy")
        s1 = stage1_of("noisy")
        e2 = copy.deepcopy(en)
        cold = next(L for L in s1["legs"] if L["in_energy_fit"] and not any(s["hot"] for s in L["segments"]))
        e = e2["legs"][cold["leg_key"]]["gpu_rail"]           # no hot block: only the leg rule can see it
        e["segments"] = [-abs(x) for x in e["segments"]]
        with self.assertRaises(F.LookInputError) as raised:
            F.stage2(s1, rehash(s1), e2)
        self.assertIn(cold["leg_key"], str(raised.exception))
        self.assertIn("gpu_rail: measured energy is not positive (R-18)", str(raised.exception))

    def test_r11_prefix_n_days_and_floor(self):
        out = F.stage2(stage1_of("noisy"), rehash(stage1_of("noisy")), dataset("noisy")[1])
        for v in out["channels"]["gpu_rail"]["prefix_bias"].values():
            self.assertEqual(v["n_days"], 5)
        self.assertEqual(F.SD_FLOOR_J, 1e-12)
        self.assertEqual(F.FOLD_MIN_UNCENSORED, 6)

    def test_r20_meter_clock_print(self):
        spans = [{"span_id": "a", "meter_offsets_ns": {"header": 10**9, "end": 10**9 + 50_000_000}},
                 {"span_id": "b", "meter_offsets_ns": {"header": 5, "end": None}}]
        mc = F.meter_clock(spans)
        self.assertEqual(mc["spans"]["a"], {"form": "two_pairs", "end_minus_header_s": 0.05})
        self.assertEqual(mc["spans"]["b"]["form"], "single_offset")
        self.assertFalse(mc["to_research_lead"])
        spans[0]["meter_offsets_ns"]["end"] = 10**9 + 150_000_000
        self.assertTrue(F.meter_clock(spans)["to_research_lead"])
        s1 = stage1_of("noisy")
        self.assertEqual(s1["meter_clock"]["max_abs_s"], 0.0)


class RL167b(unittest.TestCase):

    def test_r11_prefix_bias_nulls_and_days(self):
        two = [("a/L001", "d1", 1.0, 2.0), ("a/L002", "d2", 3.0, 1.0)]
        self.assertEqual(F.prefix_bias(3724, two),
                         {"prefix_len": 3724, "estimate": None, "ci90": None, "n_pairs": 2, "n_days": 2})
        flat = [(f"a/L00{i}", f"d{i % 3}", 5.0, float(i)) for i in range(6)]
        r = F.prefix_bias(3151, flat)
        self.assertEqual((r["estimate"], r["ci90"], r["n_days"]), (None, None, 3))
        one_day = [(f"a/L00{i}", "d", float(i), float(i * i)) for i in range(4)]
        r = F.prefix_bias(2981, one_day)
        self.assertIsNotNone(r["estimate"])
        self.assertIsNone(r["ci90"])
        self.assertEqual(r["n_days"], 1)

    def test_row16_marked_fit_uses_the_refitted_onset(self):
        _, en, _, _ = dataset("noisy")
        s1 = stage1_of("noisy")
        keep = sorted(L["leg_key"] for L in s1["legs"] if L["in_energy_fit"] and not L["marks"])
        real = F.fit_onset_fold
        base = F.stage2(s1, rehash(s1), en)["channels"]["gpu_rail"]["marked_sensitivity"]["coefficients_without"]

        def shifted(legs_d, keys, cols):
            m = real(legs_d, keys, cols)
            if sorted(keys) == keep and m is not None:
                m = dict(m, beta=m["beta"] + np.eye(len(cols))[0] * 400.0)   # onset pushed past every turn's end
            return m
        with unittest.mock.patch.object(F, "fit_onset_fold", shifted):
            moved = F.stage2(s1, rehash(s1), en)["channels"]["gpu_rail"]["marked_sensitivity"]["coefficients_without"]
        self.assertGreater(max(abs(moved[k] - base[k]) / abs(base[k]) for k in base), 1e-2)

    def test_fold_lists_wire_fields(self):
        """The two lists RL-167 row 7 names: level D onset.lodo.folds_not_estimable and level O
        channels.<ch>.lodo.folds_delta_dropped; sorted day strings, [] when none."""
        s1 = stage1_of("noisy")
        self.assertEqual(s1["onset"]["lodo"]["folds_not_estimable"], [])
        out = F.stage2(s1, rehash(s1), dataset("noisy")[1])
        for ch in F.CHANNELS:
            self.assertEqual(out["channels"][ch]["lodo"]["folds_delta_dropped"], [])
            self.assertNotIn("folds_delta_dropped", out["channels"][ch]["lodo"]["no_heat"])


class RL166b(unittest.TestCase):
    """RL-166b B-1 to B-7 and P-1 to P-4, each with a test that fails without it."""

    def test_b1_expected_hot_seconds_is_the_integral_of_phi(self):
        from math import erfc, sqrt
        for (u, v, ell, sig) in ((0.0, 10.0, -30.0, 15.0), (100.0, 120.0, 110.0, 12.0), (5.0, 25.0, 40.0, 3.0),
                                 (300.0, 320.0, 290.0, 0.5)):
            n = 20000
            h = (v - u) / n
            f = [0.5 * erfc(-((u + i * h) - ell) / sig / sqrt(2)) for i in range(n + 1)]
            want = h * (sum(f) - 0.5 * (f[0] + f[-1]))
            self.assertAlmostEqual(F.expected_hot_seconds(u, v, (ell, sig, False)), want, delta=1e-6)
        # the ends, the out-of-state leg and the tiny-sigma limit
        self.assertAlmostEqual(F.expected_hot_seconds(0.0, 20.0, (500.0, 10.0, False)), 0.0, delta=1e-12)
        self.assertAlmostEqual(F.expected_hot_seconds(400.0, 420.0, (10.0, 10.0, False)), 20.0, delta=1e-9)
        self.assertEqual(F.expected_hot_seconds(0.0, 20.0, (500.0, 10.0, True)), 20.0)
        self.assertEqual(F.expected_hot_seconds(0.0, 20.0, (12.0, 1e-7, False)), 8.0)
        self.assertEqual(F.expected_hot_seconds(0.0, 20.0, (-12.0, 1e-7, False)), 20.0)
        self.assertEqual(F.SIGMA_MIN_S, 1e-6)

    def test_b1_ell_is_not_clipped(self):
        L = {"leg_key": "x/L001", "start": {"state": "in_state", "z": [0.0, 0.0, 0.0]}, "t_p_s": 10.0}
        model = {"cols": ["intercept", "t_p_s"], "beta": np.array([-40.0, 1.0]), "sigma": 15.0}
        self.assertEqual(F._onsets([L], model)["x/L001"], (-30.0, 15.0, False))
        self.assertEqual(F.tau_hat(L, model), 0.0)

    def test_b1_folds_use_their_own_sigma(self):
        _, en, _, _ = dataset("noisy")
        s1 = stage1_of("noisy")
        base = F.stage2(s1, rehash(s1), en)["channels"]["gpu_rail"]["fold_coefficients"]
        real = F.fit_onset_fold

        def sharp(legs_d, keys, cols):
            m = real(legs_d, keys, cols)
            return None if m is None else dict(m, sigma=1e-9)
        with unittest.mock.patch.object(F, "fit_onset_fold", sharp):
            moved = F.stage2(s1, rehash(s1), en)["channels"]["gpu_rail"]["fold_coefficients"]
        d = next(iter(base))
        self.assertGreater(abs(moved[d]["delta"] - base[d]["delta"]) / abs(base[d]["delta"]), 1e-3)

    def test_b2_reading_active_rule(self):
        days = ["a", "b"]
        six_each = [("a", 1.0)] * 6 + [("b", 1.0)] * 6
        self.assertEqual(F.reading_active(six_each, days, 0.25), (True, 6))
        self.assertEqual(F.reading_active(six_each[1:], days, 0.25), (False, 5))
        at_tol = [("a", 0.25)] * 6 + [("b", -0.25)] * 6          # |z| must be ABOVE the tolerance
        self.assertEqual(F.reading_active(at_tol, days, 0.25), (False, 0))
        self.assertEqual((F.ACTIVE_TOL, F.ACTIVE_MIN_LEGS),
                         ({"tf08_c": 0.25, "fan_rpm": 25.0, "tv0h_excess_c": 0.25}, 6))

    def test_b2_inactive_reading_is_dropped_everywhere(self):
        li, en, _, sha = dataset("inactive_fan")
        s1 = F.stage1(li, sha)
        self.assertFalse(s1["active_readings"]["fan_rpm"]["active"])
        self.assertTrue(s1["active_readings"]["tf08_c"]["active"])
        self.assertNotIn("fan_rpm", s1["onset"]["predictors"])
        self.assertNotIn("fan_rpm", s1["onset"]["coefficients"])
        out = F.stage2(s1, rehash(s1), en)
        for ch in F.CHANNELS:
            c = out["channels"][ch]
            self.assertEqual(c["columns"], ["p1", "p2", "a0", "a1", "a2", "k_tf08", "k_tv0h", "delta"])
            self.assertEqual(len(c["covariance"]), 8)
            for v in c["fold_coefficients"].values():
                self.assertNotIn("k_fan", v)
            self.assertNotIn("k_fan", c["marked_sensitivity"]["coefficients_without"])

    def test_b3_onsets_in_one_cell_are_not_estimable(self):
        li, _, _, sha = dataset("onsets_one_cell")
        s1 = F.stage1(li, sha)
        on = s1["onset"]
        self.assertEqual(on["status"], "not_estimable")
        self.assertIsNone(on["converged"])
        self.assertEqual([k for k, v in on["n_uncensored_by_cell"].items() if v], ["19458"])
        self.assertGreaterEqual(on["n_uncensored"], 12)
        self.assertEqual(F.ONSET_MIN_PER_CELL, 4)

    def test_b4_fold_needs_two_in_each_of_two_cells(self):
        s1 = stage1_of("noisy")
        legs_d = {L["leg_key"]: L for L in s1["legs"]}
        unc = [L for L in s1["legs"] if L["in_energy_fit"] and L["state"]["onset_use"] == "uncensored"]
        cens = [L["leg_key"] for L in s1["legs"] if L["in_energy_fit"] and L["state"]["onset_use"] == "censored"]
        big = [L["leg_key"] for L in unc if L["cell_prompt_tokens"] == 19458]
        other = [L["leg_key"] for L in unc if L["cell_prompt_tokens"] == 2000]
        cols = s1["onset"]["predictors"]
        self.assertIsNone(F.fit_onset_fold(legs_d, big + cens, cols))                  # one cell only
        self.assertIsNone(F.fit_onset_fold(legs_d, big + other[:1] + cens, cols))      # one in the second cell
        self.assertIsNotNone(F.fit_onset_fold(legs_d, big + other[:2] + cens, cols))
        self.assertEqual((F.FOLD_MIN_UNCENSORED, F.FOLD_MIN_PER_CELL), (6, 2))

    def test_b5_convergence_test(self):
        rng = np.random.default_rng(3)
        X = np.column_stack([np.ones(200), rng.normal(0, 1, 200)])
        y = X @ np.array([10.0, 3.0]) + rng.normal(0, 2.0, 200)
        cen = y > 12.0
        y = np.where(cen, 12.0, y)
        f = F.censored_normal_fit(X, y, cen)
        self.assertTrue(f["converged"])
        self.assertLessEqual(f["decrement"], 1e-8)
        # away from the optimum the decrement is large
        q = np.array([1.0, 0.0, 1.0])
        _, G, H = F._tobit(X / np.sqrt((X * X).mean(axis=0)), y / math.sqrt((y * y).mean()), cen, q)
        t = F.convergence_test(q, G, H)
        self.assertFalse(t["passes"])
        self.assertGreater(t["decrement"], 1e-8)
        # a singular Hessian (two identical columns) fails
        X2 = np.column_stack([X, X[:, 1]])
        self.assertFalse(F.censored_normal_fit(X2, y, cen)["converged"])
        # eta at or below 0 fails
        self.assertFalse(F.convergence_test(np.array([1.0, 0.0, -1.0]), np.zeros(3), -np.eye(3))["passes"])
        # condition number over 1e10 fails
        self.assertFalse(F.convergence_test(np.array([1.0, 1.0]), np.zeros(2), -np.diag([1.0, 1e-11]))["passes"])
        self.assertTrue(F.convergence_test(np.array([1.0, 1.0]), np.zeros(2), -np.diag([1.0, 1e-9]))["passes"])
        self.assertEqual((F.CONV_DECREMENT, F.CONV_MAX_COND), (1e-8, 1e10))

    def test_b6_rank_rule_and_svd_solve(self):
        rng = np.random.default_rng(4)
        X = rng.normal(0, 1, (60, 3)) * np.array([1.0, 1e6, 1e-6])
        y = X @ np.array([1.0, 2e-6, 3e6]) + rng.normal(0, 0.01, 60)
        b, cov = F._ols(X, y, list(range(60)))
        ref, *_ = np.linalg.lstsq(X / np.sqrt((X * X).mean(axis=0)), y, rcond=None)
        np.testing.assert_allclose(b, ref / np.sqrt((X * X).mean(axis=0)), rtol=1e-9)
        Xd = np.column_stack([X, X[:, 0] + 1e-12 * rng.normal(0, 1, 60)])     # singular value ratio < 1e-10
        with self.assertRaises(F.LookInputError):
            F._ols(Xd, y, list(range(60)))
        Xok = np.column_stack([X, X[:, 0] + 1e-6 * rng.normal(0, 1, 60)])     # ratio ~1e-6: kept
        F._ols(Xok, y, list(range(60)))
        self.assertEqual(F.RANK_RTOL, 1e-10)

    def test_b7_days_tripwire_under_4(self):
        li, _, _, _ = dataset("noisy")
        for leg in li["legs"]:
            if leg["span_id"].startswith("dev-05"):
                leg["inclusion"]["g0_released"] = False
        t = F.stage1(li, "0" * 64)["tripwires"]
        self.assertEqual(t["days_below_4"]["value"], 4)
        self.assertFalse(t["days_below_4"]["trips"])
        for leg in li["legs"]:
            if leg["span_id"] == "dev-01-s01":
                leg["inclusion"]["g0_released"] = False
        t = F.stage1(li, "0" * 64)["tripwires"]
        self.assertEqual(t["days_below_4"]["value"], 3)
        self.assertTrue(t["days_below_4"]["trips"])

    def test_p1_p2_p3_prints(self):
        _, en, _, _ = dataset("noisy")
        s1 = stage1_of("noisy")
        out = F.stage2(s1, rehash(s1), en)
        c = out["channels"]["gpu_rail"]
        fit_days = sorted({L["day"] for L in s1["legs"] if L["in_energy_fit"]})
        self.assertEqual(sorted(c["fold_coefficients"]), fit_days)
        for v in c["fold_coefficients"].values():
            self.assertEqual(list(v), c["columns"])
        # P-2: s pooled within counted days, from the printed per-leg hot-stretch errors
        res = c["residuals"]["hot_stretch"]
        day_of = {L["leg_key"]: L["day"] for L in s1["legs"]}
        ss = df = 0.0
        for D in c["lodo"]["hot"]["counted_days"]:
            e = [v for k, v in res.items() if v is not None and day_of[k] == D]
            mu = sum(e) / len(e)
            ss += sum((x - mu) ** 2 for x in e)
            df += len(e) - 1
        self.assertAlmostEqual(c["day_detail"]["s_with_heat"], math.sqrt(ss / df), delta=1e-12)
        for D, v in c["day_detail"]["days"].items():
            self.assertAlmostEqual(v["se_with_heat"], c["day_detail"]["s_with_heat"] / math.sqrt(v["legs_with_hot_block"]),
                                   delta=1e-15)
            self.assertEqual(v["legs_with_hot_block"], c["lodo"]["hot"]["n_hot_legs_per_day"][D])
        self.assertEqual(sorted(c["day_detail"]["days"]), sorted(c["lodo"]["hot"]["counted_days"]))
        # P-3: offset 0 holds every leg with an observed onset and a hot block
        n0 = sum(1 for L in s1["legs"] if L["in_energy_fit"] and L["state"]["onset_use"] == "uncensored"
                 and any(s["hot"] for s in L["segments"]))
        n_any_off = sum(1 for L in s1["legs"] if L["in_energy_fit"] and L["state"]["first_off_s"] is not None
                        and any(s["hot"] for s in L["segments"]))
        self.assertLess(n0, n_any_off)            # out-of-state starts and gapped legs are left out (RL-166c row 4)
        oo = c["onset_offset_residuals"]
        self.assertEqual(oo["offsets"]["0"]["n"], n0)
        self.assertEqual(sorted(oo["offsets"], key=int), [str(i) for i in range(-2, 6)])
        self.assertGreater(oo["rms_offsets_m2_to_p3"]["no_heat"], oo["rms_offsets_m2_to_p3"]["with_heat"])
        n_m2 = 0
        for L in s1["legs"]:
            if L["in_energy_fit"] and L["state"]["onset_use"] == "uncensored":
                blocks = [s for s in L["segments"] if s["kind"] == "decode"]
                hot = [i for i, s in enumerate(blocks) if s["hot"]]
                n_m2 += bool(hot) and hot[0] >= 2
        self.assertEqual(oo["offsets"]["-2"]["n"], n_m2)
        self.assertGreater(n_m2, 0)

    def test_p4_onsets_before_116(self):
        li, _, _, sha = dataset("onsets_one_cell")
        s1 = F.stage1(li, sha)
        want = {"null": 0, "capture": 0, "consume": 0}
        for L in s1["legs"]:
            if (L["in_energy_fit"] and L["start"]["state"] == "in_state" and L["state"]["first_off_s"] is not None
                    and L["state"]["first_off_s"] < 116.0):
                want["null" if L["g0_role"] is None else L["g0_role"]] += 1
        p4 = s1["onsets_before_116_s"]
        self.assertEqual(p4["by_g0_role"], want)
        self.assertEqual(p4["to_research_lead"], p4["total"] > 0)
        # plant an early onset on an in-state leg: the 116 s cut no longer stands by default
        leg = next(x for x in li["legs"] if x["turn"] and x["span_id"].startswith("dev-02")
                   and all(x["inclusion"].values()) and x["g0_role"] is None)
        ts = leg["turn"]["turn_start_s"]
        for r in leg["turn"]["journal"]:
            if r["t_s"] > ts + 50.0:
                r["os_level"] = 1
        s1 = F.stage1(li, "0" * 64)
        p4 = s1["onsets_before_116_s"]
        self.assertEqual(p4["onset_status"], "not_estimable")
        self.assertGreater(p4["by_g0_role"]["null"], want["null"])
        self.assertTrue(p4["to_research_lead"])


PENDING_O_CHANNEL_FIELDS = ("trace_coverage",)


class Schemas(unittest.TestCase):
    """Level D and level O validate against the manifest builder's schemas (#793), on every planted scenario."""

    LOOKS = Path(__file__).resolve().parents[2] / "docs/process/cadence/looks"

    def test_outputs_validate(self):
        from tests.cadence import schema_lite as V
        s1_schema = json.loads((self.LOOKS / "lm-interim-01.stage1.schema.json").read_text())
        out_schema = json.loads((self.LOOKS / "lm-interim-01.output.schema.json").read_text())
        fit_schema = {"$ref": "#/$defs/fit_output", "$defs": out_schema["$defs"]}
        for sc in ("exact", "noisy", "onset_not_estimable", "few_hot_days", "inactive_fan", "onsets_one_cell"):
            _, en, _, _ = dataset(sc)
            s1 = stage1_of(sc)
            stamp = {"allow_draft": True, "manifest_sha256": "0" * 64, "ledger_gate": None}   # the CLI stamps these
            d1 = dict(json.loads(json.dumps(s1)), **stamp)        # RL-172a: stage 1 computes soak_retries itself
            self.assertIn("soak_retries", s1)
            self.assertEqual(V.errors(d1, s1_schema), [], sc)
            # the CLI stamps custody: null for a level-E (--energy) run, the record of what it read otherwise
            out = dict(json.loads(json.dumps(F.stage2(s1, rehash(s1), en))), **stamp, custody=None)
            for ch in F.CHANNELS:                  # PENDING in #793's schema (Mythos cold seat 9's print)
                for k in PENDING_O_CHANNEL_FIELDS:
                    if k not in out_schema["$defs"]["channel_fit"]["properties"]:
                        out["channels"][ch].pop(k)
            self.assertEqual(V.errors(out, fit_schema), [], sc)
            out["custody"] = {"root": "/c", "span_dirs": [{"span_id": "dev-01-s01", "path": "/x/dev-01-s01"}],
                              "files": [{"path": "dev-01-s01/legs/L001/runtime/b/power_trace.csv", "sha256": "a" * 64}]}
            self.assertEqual(V.errors(out, fit_schema), [], sc)
            del out["custody"]
            self.assertTrue(V.errors(out, fit_schema), sc)          # custody is required (null or the record)


class RL166c(unittest.TestCase):

    def test_row5_empty_offsets_have_all_keys(self):
        """No uncensored onset (few_hot_days has its onset model not estimable but observed onsets on two days;
        onsets_one_cell has uncensored legs): use a stage-1 copy with every onset censored."""
        _, en, _, _ = dataset("noisy")
        s1 = stage1_of("noisy")
        for L in s1["legs"]:
            if L.get("state") and L["state"]["onset_use"] == "uncensored":
                L["state"]["onset_use"] = "censored"
        out = F.stage2(s1, rehash(s1), en)
        oo = out["channels"]["gpu_rail"]["onset_offset_residuals"]
        self.assertEqual(sorted(oo["offsets"], key=int), [str(i) for i in range(-2, 6)])
        for v in oo["offsets"].values():
            self.assertEqual(v, {"n": 0, "mean_with_heat": None, "rms_with_heat": None, "mean_no_heat": None,
                                 "rms_no_heat": None})
        self.assertEqual(oo["rms_offsets_m2_to_p3"], {"with_heat": None, "no_heat": None})

    def _p3_leg_block(self, s1):
        """(leg_key, segment index) of a decode block that enters P-3 but no other refusal: an uncensored leg's
        first hot block."""
        for L in s1["legs"]:
            hot = [i for i, s in enumerate(L["segments"]) if s["hot"]]
            if L["in_energy_fit"] and L["state"]["onset_use"] == "uncensored" and len(hot) >= 3:
                return L["leg_key"], hot[0]
        raise AssertionError("no P-3 block")

    def test_row5_non_positive_block_refuses(self):
        _, en, _, _ = dataset("noisy")
        s1 = stage1_of("noisy")
        k, i = self._p3_leg_block(s1)
        for bad in (0.0, -5.0):
            e2 = copy.deepcopy(en)
            for ch in F.CHANNELS:
                seg = e2["legs"][k][ch]["segments"]
                seg[0] += seg[i] - bad            # keep the leg's and the day's sums positive and unchanged
                seg[i] = bad
            with self.assertRaisesRegex(F.LookInputError, "P-3"):
                F.stage2(s1, rehash(s1), e2)

    def test_r18_non_positive_hot_stretch_refuses(self):
        _, en, _, _ = dataset("noisy")
        s1 = stage1_of("noisy")
        L = next(L for L in s1["legs"] if L["in_energy_fit"] and any(s["hot"] for s in L["segments"]))
        e2 = copy.deepcopy(en)
        seg = e2["legs"][L["leg_key"]]["gpu_rail"]["segments"]
        for i, s in enumerate(L["segments"]):
            if s["hot"]:
                seg[0] += seg[i]
                seg[i] = 0.0
        with self.assertRaisesRegex(F.LookInputError, "hot-stretch"):
            F.stage2(s1, rehash(s1), e2)


class Agreement(unittest.TestCase):
    """The two level-D fields the first twin agreement run found (lead's ruling on F1 and F2)."""

    def test_f1_simultaneous_kinds_join_in_interface_order(self):
        turn = {"turn_start_s": 100.0, "last_token_s": 200.0,
                "journal": [{"t_s": 150.0, "os_level": 1, "pm_state": "Moderate", "pm_fresh": True}],
                "native_pm": [{"t_end_s": 150.0, "state": "Heavy"}]}
        self.assertEqual(F.first_off(turn), (50.0, "os_level_above_0+journal_pm_state_off+native_pm_state_off"))
        turn["journal"][0]["os_level"] = 0
        self.assertEqual(F.first_off(turn), (50.0, "journal_pm_state_off+native_pm_state_off"))
        turn["journal"][0].update(os_level=2, pm_state="Nominal")
        self.assertEqual(F.first_off(turn), (50.0, "os_level_above_0+native_pm_state_off"))

    def test_f2_out_of_state_tau_is_zero_when_not_estimable(self):
        s1 = stage1_of("onset_not_estimable")
        self.assertEqual(s1["onset"]["status"], "not_estimable")
        oos = [L for L in s1["legs"] if L.get("start") and L["start"]["state"] == "start_out_of_state"]
        self.assertTrue(oos)
        for L in oos:
            self.assertEqual(L["tau_hat_s"], 0.0, L["leg_key"])
        ins = [L for L in s1["legs"] if L["in_energy_fit"] and L["start"]["state"] == "in_state"]
        self.assertTrue(all(L["tau_hat_s"] is None for L in ins))
