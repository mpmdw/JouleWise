"""R1 selection uses physical step statistics; R0 never pins sensors."""
import math
import unittest

from joulewise.align.apple import smc_enumeration as r0
from scripts import align_smc_enumerate as cli


def capture(specs=None):
    # tau_heat, tau_cool, rise, idle noise; every sample is synthetic.
    specs = specs or {"TDIE": (2, 2, 18, .15), "THEA": (180, 180, 8, .08)}
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
    def test_r0_emits_no_sensor_classification_or_policy(self):
        result = r0.rank(capture())
        self.assertIsNone(result["s_fast"])
        self.assertIsNone(result["s_slow"])
        report = {"response": result, "inventory": {"keys": [], "unsupported_types": {
            "TUNK": {"data_type": "zzzz", "error": "unsupported"}}},
            "coverage": {"all_keys": {"sample_fraction": 1}}}
        summary = cli.markdown(report, "a"*64)
        self.assertIn("R1", summary)
        self.assertIn("TUNK", summary)
        self.assertNotIn('"smc_temperature"', summary)
        self.assertNotIn("Candidate campaign-policy", summary)

    def test_flat_and_near_constant_idle_cannot_beat_physical_rise(self):
        data = capture({"TDIE": (2, 2, 18, .15), "TFLT": (2, 2, .6, 0),
                        "TQST": (2, 2, .6, .00001), "THEA": (180, 180, 8, .08)})
        result = r0.rank(data, stage="r1")
        self.assertEqual(result["s_fast"], "TDIE")
        rows = {r["key"]: r for r in result["ranking"]}
        self.assertFalse(rows["TFLT"]["eligible"])
        self.assertGreaterEqual(rows["TQST"]["noise_floor"], .05)

    def test_design_boundaries_and_physical_tie_breaks(self):
        def row(key, rise, t63, tau):
            return {"key": key, "observed_rise": rise, "t63_s": t63,
                    "tau_s": tau, "eligible": True, "amplitude_to_noise": 1e9}
        result = r0.select_keys([row("TFAS", 18, 5, 2), row("TNOT", 99, 5.001, 2),
                                 row("THEA", 3, 80, 300), row("TSML", 2.999, 80, 299),
                                 row("TCHS", 50, 100, 300.001)])
        self.assertEqual(result, {"s_fast": "TFAS", "s_slow": "THEA"})
        self.assertEqual(r0.select_keys([row("TB00", 18, 2, 200), row("TA00", 18, 2, 200)]),
                         {"s_fast": "TA00", "s_slow": "TA00"})

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

    def test_slow_selects_longest_cooling_tau_with_three_degree_floor(self):
        data = capture({"TDIE": (2, 2, 18, .15), "THEA": (180, 180, 8, .08),
                        "TCHS": (450, 450, 10, .01), "TSML": (200, 200, .4, .001)})
        result = r0.rank(data, stage="r1")
        self.assertEqual(result["s_slow"], "THEA")
        rows = {r["key"]: r for r in result["ranking"]}
        self.assertGreater(rows["TCHS"]["tau_s"], 300)
        self.assertAlmostEqual(rows["THEA"]["tau_s"], 180, delta=10)

    def test_one_percent_read_errors_are_rejected_but_less_is_accepted(self):
        for failures in (5, 6):
            data = capture()
            for row in data["samples"][400:400+failures]:
                row["values"]["errors"]["TDIE"] = "read failed"
            result = r0.rank(data, stage="r1")
            with self.subTest(failures=failures):
                self.assertEqual(result["s_fast"], "TDIE" if failures == 5 else None)

    def test_model_free_t63_handles_two_timescales_and_unresolved_cooling(self):
        data = capture({"TMIX": (2, 200, 18, .1)})
        # Half a fast die response and half a slower component: a single fitted
        # tau would conflate heating and cooling. Here each crossing is explicit.
        for row in data["samples"]:
            if row["phase"] == "load":
                t = row["elapsed_s"]-300
                row["values"]["sensors"]["TMIX"] = 30+9*(1-math.exp(-t/2))+9*(1-math.exp(-t/200))
        result = r0.rank(data, stage="r1")
        self.assertGreater(result["ranking"][0]["t63_s"], 5)
        self.assertIsNone(result["s_fast"])
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
        data = capture({"THEA": (299, 299, 8, .001)})
        for row in data["samples"][900:905]:
            row["values"]["errors"]["THEA"] = "read failed"
        result = r0.rank(data, stage="r1")
        self.assertEqual(result["s_slow"], "THEA")
        self.assertAlmostEqual(result["ranking"][0]["tau_s"], 299, delta=1)
