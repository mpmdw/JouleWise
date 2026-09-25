"""Offline checks for the OSCTX launch and reduction diagnostic."""
from __future__ import annotations

import ctypes
from datetime import datetime, timezone
import json
from pathlib import Path
import plistlib
import tempfile
import unittest

from scripts.diagnostics.osctx_mvp import analyze, cell, common, runner


class OSCTXTests(unittest.TestCase):
    def setUp(self):
        self.config = common.load_config()

    def test_rendered_plists_and_order(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            actions = runner.plan(out, common.DEFAULT_CONFIG, self.config, ["A"], "/usr/bin/python3")
            self.assertEqual([x["context"] for x in actions], self.config["order"])
            self.assertEqual(len({x["label"] for x in actions}), len(actions))
            for action in actions:
                with Path(action["plist"]).open("rb") as stream:
                    rendered = plistlib.load(stream)
                self.assertNotIn("KeepAlive", rendered)
                self.assertTrue(rendered["RunAtLoad"])
                self.assertEqual(rendered["Label"], action["label"])
                self.assertEqual(rendered["EnvironmentVariables"]["HF_HUB_OFFLINE"], "1")
                self.assertIn("HOME", rendered["EnvironmentVariables"])
                expected = self.config["contexts"][action["context"]]
                if expected is None:
                    self.assertNotIn("ProcessType", rendered)
                else:
                    self.assertEqual(rendered["ProcessType"], expected)
            self.assertTrue((out / "command_sequence.json").exists())

    def test_idle_gate_rechecks_and_logs_pause(self):
        readings = iter([599, 601, 1, 600])
        sleeps, events = [], []
        def read():
            return next(readings)
        def log(**values):
            events.append(values)
        runner.wait_for_idle(600, 15, read=read, sleep=sleeps.append, log=log)
        runner.wait_for_idle(600, 15, read=read, sleep=sleeps.append, log=log)
        self.assertEqual(sleeps, [15, 15])
        self.assertEqual([e["event"] for e in events].count("hid_pause_start"), 2)

    def test_synthetic_nul_plist_energy_and_cadence(self):
        epoch = 1000.0
        records = []
        for i in range(11):
            record = {"timestamp": datetime.fromtimestamp(epoch + i * .1, tz=timezone.utc),
                      "elapsed_ns": 100_000_000,
                      "processor": {"cpu_power": 6000, "gpu_power": 3000, "ane_power": 1000,
                                    "cpu_energy": 600, "gpu_energy": 300, "ane_energy": 100}}
            records.append(plistlib.dumps(record))
        raw = b"\0".join(records) + b"\0"
        bounds = [{"name": "idle", "repeat": 1, "edge": "start", "wall_ns": 1000_050_000_000},
                  {"name": "idle", "repeat": 1, "edge": "end", "wall_ns": 1000_850_000_000}]
        result = analyze.reduce_trace(raw, bounds, epoch)
        self.assertAlmostEqual(result["idle.1"]["energy_j"], 8.0, delta=8e-6)
        self.assertEqual(result["idle.1"]["cadence"]["n"], 8)
        self.assertAlmostEqual(result["idle.1"]["cadence"]["median_ms"], 100.0)
        self.assertAlmostEqual(result["idle.1"]["cadence"]["p95_ms"], 100.0)

    def test_decisions_and_harness_failure(self):
        def rows(d_ratio=1.0, b_ratio=2.0, cadence=125.0):
            result = []
            for state in self.config["states"]:
                for context in self.config["contexts"]:
                    for number in range(1, 4):
                        value = 10.0 * (d_ratio if context == "D" and state == "U" else b_ratio if context == "B" else 1.0)
                        result.append({"state": state, "context": context, "cell_id": number,
                                       "metrics": {"cpu_seconds": value, "gpu_seconds": value,
                                                   "lm_seconds": value, "lm_j_per_token": value,
                                                   "lm_cadence_median_ms": cadence}})
            return result
        failed = analyze.decision_table(rows(b_ratio=1.2), self.config)
        self.assertEqual(failed["verdicts"]["harness"], "HARNESS FAILURE")
        self.assertEqual(failed["verdicts"]["q1"], "PENDING")
        compromised = analyze.decision_table(rows(d_ratio=1.05), self.config)
        self.assertEqual(compromised["verdicts"]["q1"], "COMPROMISED")
        self.assertEqual(compromised["states"]["U"]["pairs"]["D/I"]["cpu_seconds"], ["+"] * 3)
        cure = analyze.decision_table(rows(), self.config)
        self.assertEqual(cure["verdicts"]["q2"], "CURE CONFIRMED")

    def test_qos_uses_pointer_signatures(self):
        class Function:
            def __init__(self, fn):
                self.fn = fn
            def __call__(self, *args):
                return self.fn(*args)
        class Lib:
            pass
        fake = Lib()
        fake.pthread_self = Function(lambda: 12345)
        def get_qos(thread, qos, relative):
            self.assertEqual(thread, 12345)
            ctypes.cast(qos, ctypes.POINTER(ctypes.c_uint))[0] = 0x15
            ctypes.cast(relative, ctypes.POINTER(ctypes.c_int))[0] = -1
            return 0
        fake.pthread_get_qos_class_np = Function(get_qos)
        result = cell.qos_class(fake)
        self.assertEqual(result, {"class": "0x15", "relative_priority": -1})
        self.assertEqual(fake.pthread_self.restype, ctypes.c_void_p)
        self.assertEqual(fake.pthread_get_qos_class_np.argtypes[0], ctypes.c_void_p)


if __name__ == "__main__":
    unittest.main()
