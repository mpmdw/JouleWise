"""Thermal hazard: the OS pressure level from notifyutil; pmset is a diagnostic."""
from __future__ import annotations

import sys
import unittest

from joulewise.hazards import base, thermal
from tests.hazards.fakes import FakeClocks, Runner, completed

LIMITS = dict(thermal.DEFAULT_THRESHOLDS)
PMSET_NOTE = (b"Note: No thermal warning level has been recorded\n"
              b"Note: No performance warning level has been recorded\n"
              b"Note: No CPU power status has been recorded\n")


def measure(stdout: bytes = b"com.apple.system.thermalpressurelevel 0\n", *, diagnostics=False,
            **kwargs):
    runner = Runner({thermal.NOTIFYUTIL_ARGV: lambda argv: completed(argv, stdout, **kwargs),
                     thermal.PMSET_THERM_ARGV: lambda argv: completed(argv, PMSET_NOTE)})
    return thermal.measure(base.Context(run=runner, clocks=FakeClocks()), diagnostics=diagnostics)


class ThermalJudgeTests(unittest.TestCase):
    def test_level_zero_passes(self):
        verdict = thermal.judge(measure(), LIMITS)
        self.assertEqual(verdict.status, base.PASS)
        self.assertEqual(verdict.observed["level"], 0)

    def test_injected_level_1_refuses(self):
        verdict = thermal.judge(measure(b"com.apple.system.thermalpressurelevel 1\n"), LIMITS)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("level 1", verdict.reasons[0])

    def test_notifyutil_failure_is_unmeasured_and_refuses_at_arm(self):
        for kwargs in ({"returncode": 1}, {"timed_out": True}, {"error": "FileNotFoundError: x"}):
            verdict = thermal.judge(measure(**kwargs), LIMITS)
            self.assertEqual(verdict.status, base.UNMEASURED, kwargs)
            self.assertFalse(verdict.passed)

    def test_unrecognised_output_is_unmeasured(self):
        for stdout in (b"", b"com.apple.system.thermalpressurelevel\n", b"level 0\n",
                       b"com.apple.system.thermalpressurelevel 0\nextra\n"):
            self.assertEqual(thermal.judge(measure(stdout), LIMITS).status, base.UNMEASURED, stdout)

    def test_pmset_therm_is_recorded_but_never_judged(self):
        measurement = measure(diagnostics=True)
        self.assertIn("No thermal warning level", measurement.values["pmset_therm_diagnostic"]["stdout"])
        self.assertEqual(thermal.judge(measurement, LIMITS).status, base.PASS)
        hot = measure(b"com.apple.system.thermalpressurelevel 2\n", diagnostics=True)
        self.assertEqual(thermal.judge(hot, LIMITS).status, base.REFUSE)


class ThermalSpanTests(unittest.TestCase):
    def samples(self, levels):
        out = []
        for index, level in enumerate(levels):
            stamp = {"wall_ns": 0, "monotonic_ns": index * 5 * 10**9, "monotonic_raw_ns": 0}
            out.append({"started": stamp, "finished": stamp, "values": {"level": level},
                        "error": None, "raw": []})
        return out

    def test_nonzero_sample_inside_the_span_flags(self):
        samples = self.samples([0, 0, 0, 1, 0, 0, 0])
        found = thermal.span_findings(samples, {"monotonic_ns": [8 * 10**9, 22 * 10**9]})
        self.assertEqual([f["code"] for f in found], ["thermal.os_level_nonzero"])
        self.assertEqual(thermal.span_findings(samples, {"monotonic_ns": [21 * 10**9, 29 * 10**9]}),
                         [])

    def test_gap_is_unmeasured(self):
        samples = self.samples([0, 0, None, None, None, None, 0])
        codes = [f["code"] for f in thermal.span_findings(samples, {"monotonic_ns": [6 * 10**9,
                                                                                    24 * 10**9]})]
        self.assertEqual(codes, ["thermal.unmeasured"])


@unittest.skipUnless(sys.platform == "darwin", "reads the real notify bus (macOS)")
class LiveReadOnlyTests(unittest.TestCase):
    def test_live_level_reads(self):
        measurement = thermal.measure(base.Context())
        self.assertIsNone(measurement.error)
        self.assertIsInstance(measurement.values["level"], int)

    def test_in_process_notify_read_equals_notifyutil(self):
        reader = thermal.NotifyReader()
        try:
            self.assertEqual(reader.read(), thermal.measure(base.Context()).values["level"])
        finally:
            reader.close()


if __name__ == "__main__":
    unittest.main()
