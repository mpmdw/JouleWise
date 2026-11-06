import importlib.util
import json
from pathlib import Path
import os
import re
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
                               log_runner=FakeLog(kernel), ips_reader=lambda: [], clock=lambda: 1000,
                               swap_reader=lambda: 0)

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
        kernel = json.dumps({"process": "kernel", "eventMessage":
                             "memorystatus: killing_top_process pid 4242 [Python] (vm-pageshortage 4) 99000000KB"})
        fake = FakeLog(kernel)
        result = triage.classify({"worker_returncode": -9}, {}, "", [{"time": 10}, {"time": 20}], [],
                                 log_runner=fake, ips_reader=lambda: [], clock=lambda: 30)
        self.assertEqual("JETSAM_KILL", result["classification"])
        self.assertIn('process == "kernel"', fake.calls[0][fake.calls[0].index("--predicate") + 1])
        self.assertEqual("log", fake.calls[0][0])

    def test_log_show_times_use_a_format_log_accepts(self):
        fake = FakeLog()
        triage._log_show(1_700_000_000, 1_700_000_100, fake)
        argv = fake.calls[0]
        for flag in ("--start", "--end"):
            self.assertRegex(argv[argv.index(flag) + 1], r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d[+-]\d{4}$")

    @unittest.skipUnless(sys.platform == "darwin", "macOS unified log")
    def test_log_show_argv_is_accepted_by_real_log_command(self):
        end = triage.time.time() - 5
        output = triage._log_show(end - 5, end, subprocess.run)
        self.assertIsNotNone(output, "log show rejected the generated argv")

    def test_routine_memorystatus_lines_do_not_make_a_sigkill_jetsam(self):
        noise = "\n".join(json.dumps({"process": "kernel", "eventMessage": message}) for message in (
            "memorystatus: Denying dirty-tracking opt-in for managed com.apple.x [123]",
            "memorystatus: killing_idle_process pid 51234 [cfprefsd] jetsam_reason->osr_code: 9"))
        result = triage.classify({"worker_returncode": -9}, {}, "", [{"time": 10}, {"time": 20}], [],
                                 log_runner=FakeLog(noise), ips_reader=lambda: [], clock=lambda: 30)
        self.assertEqual("SIGNAL_CRASH", result["classification"])

    def test_kernel_log_timeout_is_a_signal_crash_not_a_triage_crash(self):
        def slow(argv, **kwargs):
            raise subprocess.TimeoutExpired(argv, kwargs.get("timeout"))
        result = triage.classify({"worker_returncode": -9}, {}, "", [{"time": 0}, {"time": 36000}], [],
                                 log_runner=slow, ips_reader=lambda: [], clock=lambda: 36001)
        self.assertEqual("SIGNAL_CRASH", result["classification"])
        self.assertEqual("unavailable", result["kernel_log"])

    def test_kernel_log_window_is_bounded_before_the_death(self):
        fake = FakeLog()
        triage.classify({"worker_returncode": -9}, {}, "", [{"time": 0}, {"time": 36000}], [],
                        log_runner=fake, ips_reader=lambda: [], clock=lambda: 36001)
        argv = fake.calls[0]
        start = triage.dt.datetime.strptime(argv[argv.index("--start") + 1], triage.LOG_TIME_FORMAT).timestamp()
        self.assertGreaterEqual(start, 36000 - triage.KERNEL_LOOKBACK_SECONDS)

    def test_preflight_refusal_leaves_no_evidence_and_is_classified_from_live_swap(self):
        for swap, expected in ((2**30, "PREFLIGHT_SWAP"), (0, "REFUSED")):
            with self.subTest(swap=swap):
                result = triage.classify({}, {}, "", [], [], log_runner=FakeLog(), ips_reader=lambda: [],
                                         clock=lambda: 30, swap_reader=lambda: swap)
                self.assertEqual(expected, result["classification"])
                self.assertTrue(result["no_evidence"])

    def test_post_run_swap_abort_with_worker_output_is_abort_swap(self):
        # A finished worker's JSON always carries "tokenizer_preflight".
        report = {"abort": "swap present or swapouts changed", "worker_returncode": 0,
                  "initial_swap_used_bytes": 0, "verdict": "aborted"}
        worker = {"verdict": "completed", "tokenizer_preflight": {"ok": True}, "note": "swap"}
        self.assertEqual("ABORT_SWAP", self.classify(report, worker)["classification"])

    def test_crash_report_written_after_final_sample_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            late = Path(tmp) / "Python-2026-11-07-120000.ips"
            late.write_text("fixture")
            os.utime(late, (25, 25))  # ReportCrash finishes after the last monitor sample
            result = triage.classify({"worker_returncode": -11}, {}, "", [{"time": 10}, {"time": 20}], [],
                                     log_runner=FakeLog(), ips_reader=lambda: [late], clock=lambda: 30)
            self.assertEqual(str(late), result["ips_source"])

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
            late = 20 + triage.IPS_GRACE_SECONDS + 1
            os.utime(old, (11, 11)); os.utime(newest, (19, 19)); os.utime(outside, (late, late))
            result = triage.classify({"worker_returncode": -6}, {}, "", [{"time": 10}, {"time": 20}], [],
                                     log_runner=FakeLog(), ips_reader=lambda: [old, newest, outside], clock=lambda: 30)
            self.assertEqual("SIGNAL_CRASH", result["classification"])
            self.assertEqual(str(newest), result["ips_source"])

    def test_all_declared_classes_have_exactly_one_action(self):
        self.assertEqual(set(triage.CLASSES), set(triage.ACTIONS))

    def test_script_does_not_import_mlx(self):
        # Fresh interpreter: in a shared test process another module may
        # already have imported MLX, which says nothing about this script.
        code = ("import importlib.util, sys; "
                f"spec = importlib.util.spec_from_file_location('t', {str(SCRIPT)!r}); "
                "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); "
                "print(any(k == 'mlx' or k.startswith('mlx.') for k in sys.modules))")
        out = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True, check=True)
        self.assertEqual(out.stdout.strip(), "False")


if __name__ == "__main__":
    unittest.main()
