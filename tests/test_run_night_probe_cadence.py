"""The calibration probe uses a fake sampler with the production argv."""

from pathlib import Path
import tempfile
import unittest

from scripts.run_night import _probe_cadence


FAKE = '''#!/usr/bin/env python3
import datetime, plistlib, sys, time
from pathlib import Path
args = sys.argv[1:]
if "--samplers" not in args or args[args.index("--samplers") + 1] != "cpu_power,gpu_power,ane_power,thermal":
    sys.exit(4)
if args[args.index("-n") + 1] != "300" or args[args.index("-i") + 1] != "100":
    sys.exit(5)
if {timeout!r}:
    time.sleep(1)
    sys.exit(6)
output = Path(args[args.index("-o") + 1])
with output.open("wb") as stream:
    for index in range(300):
        interval = {spike!r} if index == 140 and {spike!r} else {interval!r}
        stream.write(plistlib.dumps({{
            "timestamp": datetime.datetime(2026, 9, 25, tzinfo=datetime.timezone.utc),
            "elapsed_ns": interval * 1000000,
            "processor": {{"cpu_power": 1000, "gpu_power": 1000, "ane_power": 1000,
                          "cpu_energy": 1, "gpu_energy": 1, "ane_energy": 1}},
        }}))
        stream.write(b"\\0")
'''


class ProbeCadenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def capture(self, interval, spike=0, timeout=False):
        fake = self.root / "fake-powermetrics"
        fake.write_text(FAKE.format(interval=interval, spike=spike, timeout=timeout))
        fake.chmod(0o755)
        return _probe_cadence(self.root, executable=str(fake), privilege_prefix=(),
                              capture_timeout_s=0.05 if timeout else None)

    def test_132_ms_passes(self):
        result = self.capture(132)
        self.assertTrue(result["passed"], result)
        self.assertEqual((300, 132, 132, 132), tuple(result[k] for k in
            ("count", "median_ms", "p95_ms", "max_ms")))
        self.assertEqual(55, result["bound_s"])

    def test_248_ms_refuses_on_median_and_max(self):
        result = self.capture(248)
        self.assertFalse(result["passed"])
        self.assertEqual((248, 248), (result["median_ms"], result["max_ms"]))

    def test_one_210_ms_frame_refuses_on_max(self):
        result = self.capture(132, spike=210)
        self.assertFalse(result["passed"])
        self.assertEqual((132, 210), (result["median_ms"], result["max_ms"]))

    def test_timeout_refuses(self):
        result = self.capture(132, timeout=True)
        self.assertFalse(result["passed"])
        self.assertEqual(0, result["count"])
        self.assertIn("timed out", result["detail"])

    def test_timeout_retains_220_complete_slow_frames_after_term_delay(self):
        fake = self.root / "fake-partial-powermetrics"
        term_marker = self.root / "term-grace-observed"
        source = FAKE.format(interval=248, spike=0, timeout=False)
        source = source.replace("import datetime, plistlib, sys, time",
            "import datetime, plistlib, sys, time, signal\n"
            "def on_term(number, frame):\n    time.sleep(0.2)\n"
            f"    Path({str(term_marker)!r}).write_text('TERM relayed')\n"
            "    sys.exit(0)\nsignal.signal(signal.SIGTERM, on_term)")
        source = source.replace("for index in range(300):", "for index in range(220):")
        source += "\ntime.sleep(5)\n"
        fake.write_text(source)
        fake.chmod(0o755)
        result = _probe_cadence(self.root, executable=str(fake), privilege_prefix=(),
                                capture_timeout_s=0.5)
        self.assertFalse(result["passed"])
        self.assertEqual((220, 248, 248, 248), tuple(result[k] for k in
            ("count", "median_ms", "p95_ms", "max_ms")))
        self.assertIn("timed out", result["detail"])
        self.assertEqual(55, result["bound_s"])
        self.assertIsInstance(result["elapsed_s"], float)
        self.assertGreater(result["elapsed_s"], 0)
        self.assertLessEqual(result["elapsed_s"], result["bound_s"])
        self.assertEqual("TERM relayed", term_marker.read_text())

    def test_nonzero_exit_retains_complete_frames(self):
        fake = self.root / "fake-failing-powermetrics"
        source = FAKE.format(interval=248, spike=0, timeout=False)
        source = source.replace("for index in range(300):", "for index in range(120):")
        source += "\nsys.exit(7)\n"
        fake.write_text(source)
        fake.chmod(0o755)
        result = _probe_cadence(self.root, executable=str(fake), privilege_prefix=())
        self.assertFalse(result["passed"])
        self.assertEqual(120, result["count"])
        self.assertEqual(248, result["median_ms"])
        self.assertIn("exited 7", result["detail"])


if __name__ == "__main__":
    unittest.main()
