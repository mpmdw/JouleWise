"""R1 selection uses physical step statistics; R0 never pins sensors."""
import math
import unittest

from joulewise.align.apple import smc_enumeration as r0
from scripts import align_smc_enumerate as cli


def capture(specs=None):
    # tau_heat, tau_cool, rise, idle noise; every sample is synthetic.
    specs = specs or {"TDIE": (2, 2, 18, .15), "THEA": (80, 100, 8, .08)}
    samples = []
    for t in range(1500):
        phase = "idle" if t < 300 else "load" if t < 900 else "recovery"
        values = {}
        for key, (heat, cool, rise, noise) in specs.items():
            response = 0 if t < 300 else (1-math.exp(-(t-300)/heat) if t < 900 else
                        (1-math.exp(-600/heat))*math.exp(-(t-900)/cool))
            values[key] = 30 + rise*response + noise*math.sin(t*1.7)
        samples.append({"phase": phase, "elapsed_s": t, "started": {"monotonic_ns": t*10**9},
                        "finished": {"monotonic_ns": t*10**9+1000},
                        "values": {"sensors": values, "errors": {}}})
    return {"started": {"monotonic_ns": 0},
            "inventory": {"keys": [{"key": key, "unit": "degC", "data_type": "flt "} for key in specs]},
            "samples": samples, "phases": [{"phase": "idle", "start_s": 0, "end_s": 300},
                                           {"phase": "load", "start_s": 300, "end_s": 900},
                                           {"phase": "recovery", "start_s": 900, "end_s": 1500}]}


class SelectionTests(unittest.TestCase):
    def test_r0_emits_provisional_sensor_classification(self):
        result = r0.rank(capture())
        self.assertEqual(result["s_fast"], "TDIE")
        self.assertEqual(result["s_slow"], "THEA")
        self.assertTrue(result["picks_provisional"])
        report = {"response": result, "inventory": {"keys": [], "unsupported_types": {
            "TUNK": {"data_type": "zzzz", "error": "unsupported"}}},
            "coverage": {"all_keys": {"sample_fraction": 1}}}
        summary = cli.markdown(report, "a"*64)
        self.assertIn("R1", summary)
        self.assertIn("docs/align/council-2026-11-05/FINAL-DESIGN.md", summary)
        self.assertIn("TUNK", summary)
        self.assertNotIn('"smc_temperature"', summary)
        self.assertNotIn("Candidate campaign-policy", summary)

    def test_flat_and_near_constant_idle_cannot_beat_physical_rise(self):
        data = capture({"TDIE": (2, 2, 18, .15), "TFLT": (2, 2, .6, 0),
                        "TQST": (2, 2, .6, .00001), "THEA": (80, 100, 8, .08)})
        result = r0.rank(data, stage="r1")
        self.assertEqual(result["s_fast"], "TDIE")
        rows = {r["key"]: r for r in result["ranking"]}
        self.assertFalse(rows["TFLT"]["eligible"])
        self.assertGreaterEqual(rows["TQST"]["noise_floor"], .05)

    def test_summary_prints_pick_aliases_and_receipt_cell_quantity(self):
        data = capture({'TDIE': (3, 25, 18, .02), 'TCOP': (3, 25, 18, .02),
                        'THEA': (60, 90, 8, .02)})
        result = r0.rank(data)
        summary = cli.markdown({'response': result, 'inventory': data['inventory'],
                                'coverage': {'all_keys': {'sample_fraction': 1}}}, 'a'*64)
        self.assertIn('Exact-duplicate aliases of picks (report only)', summary)
        self.assertIn('"TCOP": ["TDIE"]', summary)
        self.assertIn('"THEA": []', summary)
        self.assertIn('Max consecutive empty cells per phase (receipt)', summary)
        self.assertIn('D1(d) reference `TCOP`', summary)
        self.assertIn('reference rise', summary)
        self.assertIn('excluded keys: `[]`', summary)
        self.assertIn('Class cooling tau s', summary)
        self.assertIn('Stable reference cooling s', summary)
        self.assertNotIn('total phase time >=600', summary)
        self.assertIn('band hold <=300 s', summary)
        # A single different reported value breaks exact identity, even if
        # both keys remain eligible and their role is unchanged.
        data['samples'][700]['values']['sensors']['TDIE'] += .02
        self.assertEqual(r0.rank(data)['selected_key_aliases']['TCOP'], [])

    def test_role_pick_order_and_lexical_ties(self):
        # Fast ranks by rise. Slow ranks by tau*ln(rise/1 degC), not tau.
        rows = [{"key": "TFAS", "class": "die", "observed_rise": 18},
                {"key": "TA00", "class": "die", "observed_rise": 18},
                {"key": "TLNG", "class": "heatsink", "tau_s": 120, "t_band_s": 120*math.log(4)},
                {"key": "THLD", "class": "heatsink", "tau_s": 90, "t_band_s": 90*math.log(20)}]
        self.assertEqual(r0.select_keys(rows), {"s_fast": "TA00", "s_slow": "THLD"})
        rows[-1]['clamped'] = True
        self.assertEqual(r0.select_keys(rows)['s_slow'], 'TLNG')

    def test_one_degree_quantized_small_rise_cannot_win(self):
        data = capture({"TDIE": (2, 2, 18, .15), "TINT": (2, 2, 3, .2)})
        for row in data["samples"]:
            if row["phase"] == "idle":
                row["values"]["sensors"]["TINT"] = 29 + int(row["elapsed_s"]) % 3
            else:
                row["values"]["sensors"]["TINT"] = round(row["values"]["sensors"]["TINT"])
        result = r0.rank(data, stage="r1")
        self.assertEqual(result["s_fast"], "TDIE")
        self.assertGreaterEqual(next(r for r in result["ranking"] if r["key"] == "TINT")["noise_floor"], 1)

    def test_slow_selects_longest_band_hold_with_three_degree_floor(self):
        data = capture({"TDIE": (2, 2, 18, .15), "THEA": (80, 100, 8, .08),
                        "TCHS": (450, 450, 10, .01), "TSML": (200, 200, .4, .001)})
        result = r0.rank(data, stage="r1")
        self.assertEqual(result["s_slow"], "THEA")
        rows = {r["key"]: r for r in result["ranking"]}
        self.assertGreater(rows["TCHS"]["tau_s"], 300)
        # Cooling tau is 100 s; noise/slope and 1 Hz interpolation fit within ten seconds.
        self.assertAlmostEqual(rows["THEA"]["tau_s"], 100, delta=10)

    def test_one_percent_read_errors_are_rejected_but_less_is_accepted(self):
        for failures in (5, 6):
            data = capture()
            # Isolated missed cells exercise the error-fraction bar alone;
            # consecutive misses now independently fail Erratum 2 D6.
            for i in range(failures):
                data["samples"][400+2*i]["values"]["errors"]["TDIE"] = "read failed"
            result = r0.rank(data, stage="r1")
            with self.subTest(failures=failures):
                self.assertEqual(result["s_fast"], "TDIE" if failures == 5 else None)

    def test_model_free_t63_handles_two_timescales_and_unresolved_cooling(self):
        data = capture({"TMIX": (2, 30, 18, .1)})
        # Half a fast die response and half a slower component: a single fitted
        # tau would conflate heating and cooling. Here each crossing is explicit.
        for row in data["samples"]:
            if row["phase"] == "load":
                t = row["elapsed_s"]-300
                row["values"]["sensors"]["TMIX"] = 30+9*(1-math.exp(-t/2))+9*(1-math.exp(-t/200))
        result = r0.rank(data, stage="r1")
        self.assertGreater(result["ranking"][0]["t63_end_s"], 5)
        self.assertLessEqual(result["ranking"][0]["t63_s"], 5)
        self.assertEqual(result["s_fast"], "TMIX")
        data["samples"] = [r for r in data["samples"] if r["elapsed_s"] < 920]
        data["phases"][2]["end_s"] = 920
        self.assertIsNone(r0.rank(data, stage="r1")["s_slow"])

    def test_rpm_cannot_enter_temperature_selection(self):
        data = capture({"F0Ac": (2, 200, 18, .1)})
        data["inventory"]["keys"][0]["unit"] = "rpm"
        result = r0.rank(data, stage="r1")
        self.assertIsNone(result["s_fast"])
        self.assertIsNone(result["s_slow"])

    def test_allowed_missing_initial_cooling_reads_do_not_shift_tau(self):
        data = capture({"THEA": (90, 90, 8, .001)})
        # Erratum 2 allows one empty cell, including a phase's leading cell.
        data["samples"][900]["values"]["errors"]["THEA"] = "read failed"
        result = r0.rank(data, stage="r1")
        self.assertEqual(result["s_slow"], "THEA")
        # A missing prefix moves the reference peak/time, leaving tau at 90 s.
        # Linear interpolation of one-second cells resolves this to one second.
        self.assertAlmostEqual(result["ranking"][0]["tau_s"], 90, delta=1)
