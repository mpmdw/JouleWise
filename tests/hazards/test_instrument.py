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


def _kill_group(pgid: int) -> None:
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


if __name__ == "__main__":
    unittest.main()
