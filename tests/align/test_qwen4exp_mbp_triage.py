import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).parents[2] / "scripts/qwen4exp_mbp_triage.py"
SPEC = importlib.util.spec_from_file_location("qwen4exp_mbp_triage", SCRIPT)
triage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(triage)


class FakeLog:
    def __init__(self, text=""):
        self.text = text
        self.calls = []

    def __call__(self, argv, **kwargs):
        self.calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, self.text, "")


class TriageClassesTest(unittest.TestCase):
    def classify(self, report=None, worker=None, log="", monitor=None, rungs=None, kernel=""):
        return triage.classify(report or {}, worker or {}, log, monitor or [], rungs or [],
                               log_runner=FakeLog(kernel), ips_reader=lambda: [], clock=lambda: 1000)

    def test_every_non_crash_class(self):
        cases = [
            ("PREFLIGHT_SWAP", {"abort": "preflight: swap present", "initial_swap_used_bytes": 1}, {}, "", []),
            ("ABORT_SWAP", {"abort": "swap present or swapouts changed"}, {}, "", []),
            ("ABORT_PRESSURE", {"abort": "kernel memory pressure level 2 (not normal 1)"}, {}, "", []),
            ("ABORT_FLOOR_ONLY", {"abort": "memory_pressure free percentage 9 below 10", "pressure_levels": [1], "max_compressor_growth_bytes": 2e9}, {}, "", []),
            ("ABORT_COMPRESSOR", {"abort": "compressor grew by more than 2 GB"}, {}, "", []),
            ("METAL_CAP", {}, {}, "ValueError: Metal peak exceeds default working-set cap", []),
            ("PLE_CAP", {}, {}, "ValueError: PLE resident file pages exceed operational 21.5 GB cap", []),
            ("PREDICTION_FAIL", {"verdict": "fail"}, {}, "", [{"prediction": {"relative_error": .11}}]),
            ("PY_EXCEPTION", {}, {}, 'Traceback (most recent call last):\n  File "/tmp/x.py", line 7, in go\n    bad()\nValueError: bad', []),
            ("REFUSED", {}, {}, "REFUSED: manifest pin mismatch", []),
            ("INCOMPLETE", {"verdict": "incomplete"}, {}, "", []),
            ("COMPLETED", {"verdict": "completed", "worker_returncode": 0}, {"verdict": "completed"}, "", []),
        ]
        for expected, report, worker, log, rungs in cases:
            with self.subTest(expected):
                result = self.classify(report, worker, log, rungs=rungs)
                self.assertEqual(expected, result["classification"])
                self.assertEqual(triage.ACTIONS[expected], result["next_action"])

    def test_minus_nine_without_watcher_reason_is_confirmed_by_kernel_only_log(self):
        kernel = json.dumps({"process": "kernel", "eventMessage": "memorystatus: jetsam Python"})
        fake = FakeLog(kernel)
        result = triage.classify({"worker_returncode": -9}, {}, "", [{"time": 10}, {"time": 20}], [],
                                 log_runner=fake, ips_reader=lambda: [], clock=lambda: 30)
        self.assertEqual("JETSAM_KILL", result["classification"])
        self.assertIn('process == "kernel"', fake.calls[0][fake.calls[0].index("--predicate") + 1])
        self.assertEqual("log", fake.calls[0][0])

    def test_traceback_mixed_with_metal_error_is_metal_error(self):
        log = ('Traceback (most recent call last):\n  File "/tmp/x.py", line 3, in f\n'
               "RuntimeError: Command buffer execution failed")
        self.assertEqual("METAL_ERROR", self.classify(log=log)["classification"])

    def test_python_exception_records_type_and_last_frame(self):
        log = ('Traceback (most recent call last):\n  File "/tmp/a.py", line 2, in outer\n'
               '  File "/tmp/b.py", line 9, in inner\nKeyError: no')
        result = self.classify(log=log)
        self.assertEqual("PY_EXCEPTION", result["classification"])
        self.assertEqual("KeyError", result["exception"]["type"])
        self.assertEqual({"file": "/tmp/b.py", "line": 9, "function": "inner"},
                         result["exception"]["last_frame"])

    def test_signal_crash_selects_newest_ips_inside_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            old, newest, outside = (Path(tmp) / name for name in ("Python-old.ips", "Python-new.ips", "Python-late.ips"))
            for path in (old, newest, outside):
                path.write_text("fixture")
            import os
            os.utime(old, (11, 11)); os.utime(newest, (19, 19)); os.utime(outside, (21, 21))
            result = triage.classify({"worker_returncode": -6}, {}, "", [{"time": 10}, {"time": 20}], [],
                                     log_runner=FakeLog(), ips_reader=lambda: [old, newest, outside], clock=lambda: 30)
            self.assertEqual("SIGNAL_CRASH", result["classification"])
            self.assertEqual(str(newest), result["ips_source"])

    def test_all_declared_classes_have_exactly_one_action(self):
        self.assertEqual(set(triage.CLASSES), set(triage.ACTIONS))

    def test_script_does_not_import_mlx(self):
        self.assertNotIn("mlx", sys.modules)


if __name__ == "__main__":
    unittest.main()
