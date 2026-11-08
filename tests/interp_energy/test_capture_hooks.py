import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from joulewise.clock import FakeClock
from joulewise.interp_energy.capture_hooks import existing_capture

ROOT = Path(__file__).resolve().parents[2]


class CaptureHookTests(unittest.TestCase):
    def test_powermetrics_delegates_existing_current_era_api(self):
        adapter = Mock()
        adapter.start_sampling.return_value = SimpleNamespace(ok=True, metadata={"synthetic": True})
        adapter.stop_sampling_with_evidence.return_value = SimpleNamespace(samples=[1, 2], uncertainty_evidence={"fixture": True})
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            output = Path(temporary) / "capture"
            with patch("joulewise.adapters.powermetrics.PowermetricsTelemetryAdapter", return_value=adapter):
                with existing_capture(output, FakeClock(123), powermetrics=True) as metadata:
                    self.assertTrue(metadata["powermetrics"]["ready"])
            self.assertEqual(metadata["powermetrics"]["sample_count"], 2)
            self.assertEqual(metadata["powermetrics"]["clock_evidence"], {"fixture": True})
            config, context = adapter.start_sampling.call_args.args
            self.assertEqual(context.raw_dir, output / "raw")
            self.assertEqual(config.sampling.power_hz, 10)
            self.assertIn("sampling_stopped", adapter.stop_sampling_with_evidence.call_args.kwargs)
            self.assertEqual(json.loads((output / "capture.json").read_text()), metadata)

    def test_failed_start_salvages_and_never_runs_body(self):
        adapter = Mock()
        adapter.start_sampling.return_value = SimpleNamespace(ok=False, metadata={}, message="synthetic refusal")
        adapter.salvage_custody.return_value = []
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            output = Path(temporary) / "capture"
            with patch("joulewise.adapters.powermetrics.PowermetricsTelemetryAdapter", return_value=adapter):
                with self.assertRaisesRegex(RuntimeError, "synthetic refusal"):
                    with existing_capture(output, FakeClock(), powermetrics=True):
                        self.fail("failed sampler must not reach workload")
            adapter.salvage_custody.assert_called_once()
            adapter.stop_sampling_with_evidence.assert_not_called()
            self.assertIn("error", json.loads((output / "capture.json").read_text()))

    def test_meter_uses_existing_script_and_cleans_up_after_workload_error(self):
        process = Mock()
        process.poll.return_value = None
        process.wait.return_value = 0
        commands = []
        def launch(command, **kwargs):
            commands.append(command)
            output = Path(command[command.index("--out") + 1])
            output.write_text(json.dumps({"k": "h", "status": "streaming", "synthetic": True}) + "\n")
            return process
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            output = Path(temporary) / "capture"
            with patch("joulewise.interp_energy.capture_hooks.subprocess.Popen", side_effect=launch):
                with self.assertRaisesRegex(ValueError, "synthetic workload failure"):
                    with existing_capture(output, FakeClock(), km003c=True):
                        raise ValueError("synthetic workload failure")
            self.assertTrue(commands[0][2].endswith("scripts/km003c_monitor.py"))
            process.terminate.assert_called_once()
            process.wait.assert_called_once_with(timeout=10)
            self.assertIn("error", json.loads((output / "capture.json").read_text()))

    def test_absent_meter_is_explicit_failure_with_retained_metadata(self):
        process = Mock()
        process.poll.return_value = 0
        process.wait.return_value = 0
        def launch(command, **kwargs):
            Path(command[command.index("--out") + 1]).write_text('{"k":"h","status":"absent","reason":"synthetic absence"}\n')
            return process
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            output = Path(temporary) / "capture"
            with patch("joulewise.interp_energy.capture_hooks.subprocess.Popen", side_effect=launch):
                with self.assertRaisesRegex(RuntimeError, "synthetic absence"):
                    with existing_capture(output, FakeClock(), km003c=True):
                        self.fail("absent meter must not reach workload")
            self.assertTrue(json.loads((output / "capture.json").read_text())["km003c"]["exited_before_stop"])

    def test_powermetrics_stop_failure_still_stops_owned_meter(self):
        adapter, process = Mock(), Mock()
        adapter.start_sampling.return_value = SimpleNamespace(ok=True, metadata={})
        adapter.stop_sampling_with_evidence.side_effect = RuntimeError("synthetic stop failure")
        process.poll.return_value = None
        process.wait.return_value = 0
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            output = Path(temporary) / "capture"
            with patch("joulewise.adapters.powermetrics.PowermetricsTelemetryAdapter", return_value=adapter), \
                 patch("joulewise.interp_energy.capture_hooks.subprocess.Popen", return_value=process), \
                 patch("joulewise.interp_energy.capture_hooks._meter_header", return_value={"synthetic": True}):
                with self.assertRaisesRegex(RuntimeError, "synthetic stop failure"):
                    with existing_capture(output, FakeClock(), km003c=True, powermetrics=True):
                        pass
            process.terminate.assert_called_once()
            self.assertIn("powermetrics_stop_error", json.loads((output / "capture.json").read_text()))


if __name__ == "__main__":
    unittest.main()
