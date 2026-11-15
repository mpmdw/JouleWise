"""Freeze 2's coefficient file and predict path (RL-173 §E). Synthetic data only: every input is written by
scripts/cadence_look_synth.py with planted parameters. No custody, campaign or v4 file exists in these tests."""
from __future__ import annotations

import builtins
import copy
import hashlib
import io
import json
from pathlib import Path
import unittest
import unittest.mock

try:  # the fit needs numpy; the dependency-free core shards run without it (CI's look-fit job installs it)
    import numpy as np

    from joulewise.cadence_looks import fit_interim as F
    from joulewise.cadence_looks import schema_check as SC
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


SCHEMA = Path(__file__).resolve().parents[2] / "docs/process/cadence/looks/lm-interim-01.coefficients.schema.json"
MANIFEST_SHA = "ab" * 32
SCENARIOS = ("noisy", "onset_not_estimable", "inactive_fan")
REL = 1e-9

_RUNS = {}


def run(scenario):
    """(look_input, stage1, stage1_sha, fit, coefficients), built once per scenario (deep-copied for the caller)."""
    if scenario not in _RUNS:
        li, en, _ = synth.build(scenario)
        s1 = F.stage1(li, hashlib.sha256(synth.dump(li)).hexdigest())
        s1_sha = hashlib.sha256(F.dump(s1)).hexdigest()
        fit = F.stage2(s1, s1_sha, en)
        co = F.write_coefficients(s1, s1_sha, fit, MANIFEST_SHA)
        _RUNS[scenario] = (li, s1, s1_sha, fit, co)
    return copy.deepcopy(_RUNS[scenario])


def main_fitted(s1, fit, ch):
    """The main fit's fitted values X_full @ b_full per energy-fit leg, from fit_interim's own design (the main
    onset model as stage 2 builds it, the fit's columns and coefficients). Also each leg's heat contribution and
    the main fit's prefix predictions."""
    legs = [L for L in s1["legs"] if L["in_energy_fit"]]
    on = s1["onset"]
    model = ({"cols": list(on["predictors"]), "beta": np.array([on["coefficients"][c] for c in on["predictors"]]),
              "sigma": on["sigma_s"]} if on["status"] == "estimable" else None)
    c = fit["channels"][ch]
    cols = c["columns"]
    b = np.array([c["coefficients"][x] for x in cols])
    fold = F._Fold(legs, cols, F._onsets(legs, model))
    heat = np.array([x in F.HEAT_COLS or x == F.DELTA_COL for x in cols])
    out = {}
    for L in legs:
        X = np.asarray(fold.rows(L))
        out[L["leg_key"]] = {
            "segments": X @ b, "heat": X[:, heat] @ b[heat],
            "prefix": {str(p): (float((np.asarray(fold.prefix_rows(L, p)) @ b).sum()) if p < L["decode_tokens"]
                                else None) for p in F.PREFIX.values()},
            "L": L}
    return out


def close(a, b):
    return abs(a - b) <= REL * max(abs(a), abs(b), 1e-300)


class Reproduces(unittest.TestCase):
    """predict(coefficients, leg) equals the main fit's fitted values on every energy-fit leg, both channels."""

    def check(self, scenario):
        li, s1, _, fit, co = run(scenario)
        spans = {s["span_id"]: s for s in li["spans"]}
        legs_r = {leg["leg_key"]: leg for leg in li["legs"]}
        n = 0
        for ch in F.CHANNELS:
            want = main_fitted(s1, fit, ch)
            self.assertTrue(want)
            for k, w in want.items():
                leg = legs_r[k]
                p = F.predict(co, leg, spans[leg["span_id"]]["soak_reference_tv0h_c"])
                got = p["channels"][ch]
                self.assertEqual(len(got["segments"]), len(w["segments"]), k)
                for a, b in zip(got["segments"], w["segments"]):
                    self.assertTrue(close(a, float(b)), f"{scenario} {ch} {k}: {a} vs {b}")
                for a, b in zip(got["heat"], w["heat"]):
                    self.assertLessEqual(abs(a - float(b)), REL * max(1.0, max(abs(x) for x in w["segments"])), k)
                self.assertTrue(close(got["H_hat"], float(np.sum(w["heat"]))) or abs(got["H_hat"]) < 1e-6, k)
                self.assertAlmostEqual(got["H_hat"], sum(got["heat"]), delta=1e-9 * max(1.0, abs(got["total"])))
                self.assertTrue(close(got["total"], float(np.sum(w["segments"]))), k)
                self.assertEqual(set(got["prefix_tails"]), {str(x) for x in F.PREFIX.values()})
                for plen, v in got["prefix_tails"].items():
                    if w["prefix"][plen] is None:
                        self.assertIsNone(v)
                    else:
                        self.assertTrue(close(v, w["prefix"][plen]), f"{k} prefix {plen}")
                # stage 1's per-leg arithmetic, recomputed from the coefficient file alone
                L = w["L"]
                self.assertEqual(p["leg_key"], k)
                self.assertTrue(close(p["t_p_s"], L["t_p_s"]) and close(p["load_s"], L["load_s"]), k)
                self.assertEqual(p["start"]["state"], L["start"]["state"])
                self.assertEqual(p["start"]["extrapolated"], L["start"]["extrapolated"])
                self.assertEqual(p["start"]["status"], "ok")
                for a, b in zip(p["start"]["z"], L["start"]["z"]):
                    self.assertAlmostEqual(a, b, delta=1e-12)
                if L["tau_hat_s"] is None:
                    self.assertIsNone(p["tau_hat_s"])
                else:
                    self.assertTrue(close(p["tau_hat_s"], L["tau_hat_s"]) or abs(L["tau_hat_s"]) < 1e-12, k)
                n += 1
        return n, fit, co

    def test_noisy(self):
        n, fit, co = self.check("noisy")
        self.assertGreater(n, 0)
        self.assertEqual(co["delta_column"], "kept")
        self.assertEqual(co["onset"]["status"], "estimable")

    def test_onset_not_estimable(self):
        n, fit, co = self.check("onset_not_estimable")
        self.assertEqual(co["delta_column"], "dropped_onset_not_estimable")
        self.assertIsNone(co["onset"]["coefficients"])
        for ch in F.CHANNELS:
            self.assertNotIn("delta", co["channels"][ch]["columns"])

    def test_inactive_reading(self):
        n, fit, co = self.check("inactive_fan")
        self.assertFalse(co["active_readings"]["fan_rpm"])
        for ch in F.CHANNELS:
            self.assertNotIn("k_fan", co["channels"][ch]["columns"])

    def test_heat_is_the_heat_columns(self):
        """H_hat is the k_* and delta contribution: zeroing those coefficients zeroes it and leaves the base."""
        li, _, _, _, co = run("noisy")
        spans = {s["span_id"]: s for s in li["spans"]}
        leg = next(lg for lg in li["legs"] if lg["leg_type"] == "A" and lg["turn"] is not None
                   and F.start_reading(lg["turn"], spans[lg["span_id"]]["soak_reference_tv0h_c"])[0] == "ok")
        ref = spans[leg["span_id"]]["soak_reference_tv0h_c"]
        p = F.predict(co, leg, ref)
        co0 = copy.deepcopy(co)
        for ch in F.CHANNELS:
            for col in co0["channels"][ch]["coefficients"]:
                if col in F.HEAT_COLS or col == F.DELTA_COL:
                    co0["channels"][ch]["coefficients"][col] = 0.0
        p0 = F.predict(co0, leg, ref)
        for ch in F.CHANNELS:
            self.assertEqual(p0["channels"][ch]["H_hat"], 0.0)
            self.assertAlmostEqual(p0["channels"][ch]["total"] + p["channels"][ch]["H_hat"],
                                   p["channels"][ch]["total"], delta=1e-9 * abs(p["channels"][ch]["total"]))


class Document(unittest.TestCase):

    def test_schema_and_determinism(self):
        schema = json.loads(SCHEMA.read_text())
        for sc in SCENARIOS:
            _, s1, s1_sha, fit, co = run(sc)
            self.assertEqual(SC.errors(co, schema), [], sc)
            again = F.write_coefficients(s1, s1_sha, fit, MANIFEST_SHA)
            self.assertEqual(F.dump(co), F.dump(again), sc)
            self.assertEqual(co["schema"], F.COEFFICIENTS_SCHEMA)
            self.assertEqual(co["stage1_sha256"], s1_sha)
            self.assertEqual(co["fit_sha256"], hashlib.sha256(F.dump(fit)).hexdigest())
            self.assertEqual(co["manifest_sha256"], MANIFEST_SHA)
            for ch in F.CHANNELS:
                c = fit["channels"][ch]
                self.assertEqual(co["channels"][ch]["hot_rms_over_legs"], c["lodo"]["hot_rms_over_legs"])
                self.assertEqual(co["channels"][ch]["model_sha256"], c["model_sha256"])
            if s1["onset"]["status"] == "estimable":
                self.assertEqual(co["onset"]["lodo_rms_s"], s1["onset"]["lodo"]["rms_s"])
            F.output_check(co)
            text = json.dumps(co).lower().replace("joulewise", "")
            for word in ("joule", "watt", "power", "energy"):
                self.assertNotIn(word, text)

    def test_schema_refuses_an_inconsistent_onset(self):
        schema = json.loads(SCHEMA.read_text())
        co = run("noisy")[4]
        bad = copy.deepcopy(co)
        bad["delta_column"] = "dropped_onset_not_estimable"
        self.assertNotEqual(SC.errors(bad, schema), [])
        bad = copy.deepcopy(co)
        bad["onset"]["sigma_s"] = None
        self.assertNotEqual(SC.errors(bad, schema), [])
        bad = copy.deepcopy(co)
        bad["extra"] = 1
        self.assertNotEqual(SC.errors(bad, schema), [])
        co = run("onset_not_estimable")[4]
        bad = copy.deepcopy(co)
        bad["onset"]["coefficients"] = {"intercept": 1.0, "t_p_s": 0.0}
        self.assertNotEqual(SC.errors(bad, schema), [])

    def test_wrong_stage1_sha_refuses(self):
        _, s1, s1_sha, fit, _ = run("noisy")
        with self.assertRaisesRegex(F.LookInputError, "stage-1"):
            F.write_coefficients(s1, "0" * 64, fit, MANIFEST_SHA)
        other = copy.deepcopy(fit)
        other["stage1_sha256"] = "1" * 64
        with self.assertRaisesRegex(F.LookInputError, "stage1_sha256"):
            F.write_coefficients(s1, s1_sha, other, MANIFEST_SHA)
        with self.assertRaises(F.LookInputError):
            F.write_coefficients(s1, s1_sha, fit, "not-a-hash")


class Refusals(unittest.TestCase):

    def setUp(self):
        self.li, _, _, _, self.co = run("noisy")
        self.spans = {s["span_id"]: s for s in self.li["spans"]}

    def ref(self, leg):
        return self.spans[leg["span_id"]]["soak_reference_tv0h_c"]

    def test_missing_start_reading_refuses_by_name(self):
        legs = [lg for lg in self.li["legs"] if lg["leg_type"] == "A" and lg["turn"] is not None
                and F.start_reading(lg["turn"], self.ref(lg))[0] != "ok"]
        self.assertTrue(legs, "the noisy scenario plants missing start readings")
        for leg in legs:
            with self.assertRaisesRegex(F.LookInputError, leg["leg_key"]):
                F.predict(self.co, leg, self.ref(leg))
        # and a good leg made bad: no journal reading before the turn start, or no soak reference
        leg = next(lg for lg in self.li["legs"] if lg["leg_type"] == "A" and lg["turn"] is not None
                   and F.start_reading(lg["turn"], self.ref(lg))[0] == "ok")
        with self.assertRaisesRegex(F.LookInputError, leg["leg_key"]):
            F.predict(self.co, leg, None)
        bad = copy.deepcopy(leg)
        bad["turn"]["journal"] = [r for r in bad["turn"]["journal"] if r["t_s"] > bad["turn"]["turn_start_s"]]
        with self.assertRaisesRegex(F.LookInputError, leg["leg_key"]):
            F.predict(self.co, bad, self.ref(leg))

    def test_type_t_and_no_turn_refuse_by_name(self):
        for leg in self.li["legs"]:
            if leg["leg_type"] == "T" or leg["turn"] is None:
                with self.assertRaisesRegex(F.LookInputError, leg["leg_key"]):
                    F.predict(self.co, leg, self.ref(leg))
        leg = copy.deepcopy(next(lg for lg in self.li["legs"] if lg["turn"] is not None))
        leg["leg_type"] = "T"
        with self.assertRaisesRegex(F.LookInputError, leg["leg_key"]):
            F.predict(self.co, leg, self.ref(leg))

    def test_predict_reads_nothing_but_its_arguments(self):
        leg = next(lg for lg in self.li["legs"] if lg["leg_type"] == "A" and lg["turn"] is not None
                   and F.start_reading(lg["turn"], self.ref(lg))[0] == "ok")
        want = F.predict(self.co, leg, self.ref(leg))

        def no_open(*a, **k):
            raise AssertionError("predict opened a file")
        with unittest.mock.patch.object(builtins, "open", no_open), \
                unittest.mock.patch.object(io, "open", no_open), \
                unittest.mock.patch.object(Path, "open", no_open):
            got = F.predict(self.co, leg, self.ref(leg))
        self.assertEqual(got, want)

    def test_not_a_coefficient_file_refuses(self):
        leg = next(lg for lg in self.li["legs"] if lg["turn"] is not None)
        bad = copy.deepcopy(self.co)
        bad["schema"] = F.FIT_SCHEMA
        with self.assertRaises(F.LookInputError):
            F.predict(bad, leg, self.ref(leg))


if __name__ == "__main__":
    unittest.main()
