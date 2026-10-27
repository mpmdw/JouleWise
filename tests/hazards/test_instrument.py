"""Instrument hazard: the real cadence probe path (child process, production
adapter command and parser) against a fake powermetrics replaying archived
real frame intervals."""
from __future__ import annotations

import io
import json
import os
import signal
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise.hazards import base, instrument
from tests.hazards.fakes import FAKE_POWERMETRICS, INSTRUMENT, FakeClocks

LIMITS = dict(instrument.DEFAULT_THRESHOLDS)
LAUNCHD_0919 = INSTRUMENT / "cadence-20260919-n1-d01-launchd.json"
BLOCK3 = INSTRUMENT / "cadence-20261004-block3-idle.json"


class CadenceProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.tmp.cleanup)
        self.raw = Path(self.tmp.name)

    def probe(self, fixture: Path, *, prefix=(), executable=str(FAKE_POWERMETRICS), **env):
        values = {"FAKE_PM_FIXTURE": str(fixture), **{key: str(value) for key, value in env.items()}}
        with mock.patch.dict(os.environ, values):
            measurement = instrument.measure(base.Context(raw_dir=self.raw, clocks=FakeClocks()),
                                             executable=executable, privilege_prefix=prefix)
        pgid = measurement.values.get("pgid")
        if pgid:
            self.addCleanup(_kill_group, pgid)
        return measurement, instrument.judge(measurement, LIMITS)

    def test_0919_launchd_capture_at_244_to_250_ms_refuses(self):
        measurement, verdict = self.probe(LAUNCHD_0919)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertAlmostEqual(measurement.values["median_ms"], 249.7, delta=0.1)
        self.assertGreater(measurement.values["max_ms"], 200)
        self.assertTrue(any("median interval" in reason for reason in verdict.reasons))

    def test_block3_interactive_capture_at_130_ms_passes(self):
        measurement, verdict = self.probe(BLOCK3)
        self.assertEqual(verdict.status, base.PASS, verdict.reasons)
        self.assertEqual(measurement.values["frames"], 300)
        self.assertEqual(measurement.raw[0].name, "powermetrics-idle.plist")
        self.assertTrue((self.raw / "powermetrics-idle.plist").exists())

    def test_nonzero_exit_refuses(self):
        _measurement, verdict = self.probe(BLOCK3, FAKE_PM_EXIT=1)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("exited 1", verdict.reasons[0])

    def test_one_frame_short_refuses(self):
        _measurement, verdict = self.probe(BLOCK3, FAKE_PM_FRAMES=299)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertTrue(any("299 frames" in reason for reason in verdict.reasons))

    def test_zero_duration_frames_are_unmeasured(self):
        self.check_frame_intervals(0, all_frames=True)

    def test_one_zero_duration_frame_is_unmeasured(self):
        self.check_frame_intervals(0, all_frames=False)

    def test_negative_duration_frames_are_unmeasured(self):
        # -1 ns is one elapsed_ns representation quantum below the physical
        # boundary: a measured frame duration must be strictly positive.
        self.check_frame_intervals(-1, all_frames=True)

    def test_one_negative_duration_frame_is_unmeasured(self):
        self.check_frame_intervals(-1, all_frames=False)

    def test_positive_duration_frame_control_passes(self):
        # 10 Hz means 1/10 s per frame, the production requested cadence.
        self.check_frame_intervals(1_000_000_000 // 10, all_frames=True, expected=base.PASS)

    def check_frame_intervals(self, duration_ns, *, all_frames, expected=base.UNMEASURED):
        fixture = json.loads(BLOCK3.read_text())
        # Production captures 30 s at 10 Hz (300 frames). Other durations
        # are 1/10 s, so a single impossible frame hides below both existing
        # upper cadence bounds unless every parsed interval is validated.
        intervals = [1_000_000_000 // 10] * LIMITS["frames"]
        if all_frames:
            intervals = [duration_ns] * LIMITS["frames"]
        else:
            intervals[len(intervals) // 2] = duration_ns
        fixture["elapsed_ns"] = intervals
        path = self.raw / "nonpositive.json"
        path.write_text(json.dumps(fixture))
        # Process-group census is a separate gate, unavailable in a sandbox
        # without sysmond. Fake only that seam inside the real capture child;
        # the subprocess, plist bytes, production parser and judge stay real.
        bootstrap = instrument.CHILD_BOOTSTRAP.replace(
            "raise SystemExit", "from joulewise.hazards import instrument; "
            "instrument.group_absent = lambda pgid: (True, []); raise SystemExit")
        with mock.patch.object(instrument, "CHILD_BOOTSTRAP", bootstrap):
            measurement, verdict = self.probe(path)
        self.assertEqual(verdict.status, expected, verdict.reasons)
        self.assertEqual(measurement.values["frames"], LIMITS["frames"])
        self.assertEqual(measurement.values["intervals_ns"], intervals)
        self.assertEqual(len(measurement.raw), 1)  # retain the invalid capture as evidence
        if expected == base.UNMEASURED:
            self.assertIsNone(measurement.values.get("median_ms"))
            self.assertIsNone(measurement.values.get("max_ms"))

    def test_surviving_process_in_the_capture_group_refuses(self):
        measurement, verdict = self.probe(BLOCK3, FAKE_PM_SPAWN_ORPHAN=1)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertFalse(measurement.values["group_gone"])

    def test_powermetrics_that_cannot_start_is_unmeasured(self):
        _measurement, verdict = self.probe(BLOCK3, executable=str(self.raw / "no-such-binary"))
        self.assertEqual(verdict.status, base.UNMEASURED)

    def test_child_that_cannot_run_is_unmeasured(self):
        with mock.patch.dict(os.environ, {"FAKE_PM_FIXTURE": str(BLOCK3)}):
            measurement = instrument.measure(base.Context(raw_dir=self.raw, clocks=FakeClocks()),
                                             executable=str(FAKE_POWERMETRICS), privilege_prefix=(),
                                             python=str(self.raw / "no-python"))
        self.assertEqual(instrument.judge(measurement, LIMITS).status, base.UNMEASURED)

    def test_privilege_prefix_is_prepended_to_the_adapter_command(self):
        measurement, verdict = self.probe(BLOCK3, prefix=("/usr/bin/env",))
        self.assertEqual(verdict.status, base.PASS, verdict.reasons)
        self.assertEqual(measurement.values["argv"][:2], ["/usr/bin/env", str(FAKE_POWERMETRICS)])
        self.assertEqual(measurement.values["argv"][2:13],
                         ["-n", "300", "-b", "0", "-i", "100", "--samplers",
                          "cpu_power,gpu_power,ane_power,thermal", "--format", "plist", "-o"])


class ProductionCommandTests(unittest.TestCase):
    def test_production_command_is_the_block3_receipt_argv(self):
        from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
        adapter = PowermetricsTelemetryAdapter(None)
        config = SimpleNamespace(sampling=SimpleNamespace(power_hz=10.0, idle_seconds=30.0))
        count = adapter._idle_count(config)
        self.assertEqual(count, LIMITS["frames"])
        self.assertEqual(adapter._capture_timeout_s(config, count), LIMITS["bound_s"])
        # night_probe_receipt.json of block 3 (1305Z) recorded this argv
        self.assertEqual(adapter._command(config, Path("/x.plist"), count=count),
                         ["sudo", "-n", "/usr/bin/powermetrics", "-n", "300", "-b", "0", "-i", "100",
                          "--samplers", "cpu_power,gpu_power,ane_power,thermal", "--format",
                          "plist", "-o", "/x.plist"])
        self.assertEqual((instrument.POWERMETRICS, instrument.PRIVILEGE_PREFIX),
                         ("/usr/bin/powermetrics", ("sudo", "-n")))

    def test_timeout_kills_the_capture_group(self):
        from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as directory:
            out = io.StringIO()
            env = {"FAKE_PM_FIXTURE": str(BLOCK3), "FAKE_PM_SLEEP_S": "30"}
            with mock.patch.dict(os.environ, env), \
                    mock.patch.object(PowermetricsTelemetryAdapter, "_capture_timeout_s",
                                      return_value=1.0), redirect_stdout(out):
                instrument._child_main(["--output", f"{directory}/p.plist", "--executable",
                                        str(FAKE_POWERMETRICS), "--privilege-prefix", "[]"])
        report = json.loads(out.getvalue())
        self.assertTrue(report["timed_out"])
        self.assertTrue(report["group_gone"])
        measurement = base.Measurement("instrument", "instant", {**report, **instrument.cadence_statistics(
            report["intervals_ns"])}, (), FakeClocks().stamp(), FakeClocks().stamp())
        verdict = instrument.judge(measurement, {**LIMITS, "bound_s": 1.0})
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertIn("did not finish", verdict.reasons[0])


class JudgeBoundTests(unittest.TestCase):
    """The maximum-interval and elapsed bounds, each alone (review test gaps)."""

    def judge(self, **changes):
        values = {"count_expected": 300, "frames": 300, "returncode": 0, "timed_out": False,
                  "elapsed_s": 39.8, "median_ms": 120.0, "p95_ms": 140.0, "max_ms": 180.0,
                  "group_gone": True, "group_census": []}
        values.update(changes)
        stamp = FakeClocks().stamp()
        return instrument.judge(base.Measurement("instrument", "instant", values, (), stamp, stamp),
                                LIMITS)

    def test_the_baseline_passes(self):
        self.assertEqual(self.judge().status, base.PASS)

    def test_one_250_ms_gap_at_a_120_ms_median_flags(self):
        verdict = self.judge(max_ms=250.0)
        self.assertEqual(verdict.status, base.PASS)
        self.assertEqual(verdict.observed["flags"][0]["code"], "instrument.single_interval_above_screen")

    def test_200_ms_is_inside_the_bound(self):
        self.assertEqual(self.judge(max_ms=200.0).status, base.PASS)

    def test_elapsed_beyond_55_s_refuses(self):
        verdict = self.judge(elapsed_s=55.5)
        self.assertEqual(verdict.status, base.REFUSE)
        self.assertEqual(verdict.reasons, ("elapsed 55.5 s exceeds the 55.0 s bound",))

    def test_missing_elapsed_refuses(self):
        self.assertEqual(self.judge(elapsed_s=None).status, base.REFUSE)


def _kill_group(pgid: int) -> None:
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


if __name__ == "__main__":
    unittest.main()
