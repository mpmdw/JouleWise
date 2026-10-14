import contextlib
import io
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from joulewise.flags import core
from scripts import validate_powermetrics_fiducial as writer


class MeasurementReached(BaseException):
    pass


class CaptureToolTests(unittest.TestCase):
    def test_hazard_preflight_failure_flags_and_reaches_stub_measurement_legacy_refuses(self):
        for hazard in (object(), None):
            with self.subTest(hazard=hazard is not None), tempfile.TemporaryDirectory() as tmp, contextlib.ExitStack() as stack:
                root = Path(tmp)
                argv = ["--allow-live", "--power-policy", "desk", "--output-root", str(root / "capture"),
                        "--ledger", str(root / "ledger"), "--head-pin", str(root / "head-pin"),
                        "--sampler-binary", str(root / "fake-sampler"), "--sampler-direct-for-test"]
                stack.enter_context(patch.object(writer, "authenticate_calibration_writer_launch_lineage"))
                stack.enter_context(patch.object(writer, "_sysctl_identity", return_value="desk"))
                stack.enter_context(patch.object(writer, "load_calibration_ledger_snapshot", return_value=MagicMock()))
                stack.enter_context(patch.object(core, "hazard_flag_context", return_value=hazard))
                flags = stack.enter_context(patch.object(core, "emit"))
                stack.enter_context(patch.object(writer, "_derive_preflight_systematic_screen_s",
                    side_effect=writer._AcceptancePreflightError("desk-unverified", shape="fixture")))
                lifecycle = stack.enter_context(patch.object(writer, "_CaptureLedgerLifecycle"))
                lifecycle.return_value.session_custody = None
                stack.enter_context(patch.object(writer, "normalize_calibration_custody_path", return_value="fixture"))
                stack.enter_context(patch.object(writer, "_planned_t1_bindings", return_value={}))
                stack.enter_context(patch.object(writer, "_writer_stage"))
                stack.enter_context(patch.object(writer.atexit, "register"))
                # This is the first measurement step; it is always a stub.
                measure = stack.enter_context(patch.object(writer.battery_float, "observe", side_effect=MeasurementReached))
                sampler = stack.enter_context(patch.object(writer, "_sampler_lifetime", side_effect=AssertionError("sampler must remain stubbed")))
                mlx = types.ModuleType("mlx")
                mlx.core = types.ModuleType("mlx.core")
                stack.enter_context(patch.dict("sys.modules", {"mlx": mlx, "mlx.core": mlx.core}))
                stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
                if hazard is not None:
                    with self.assertRaises(MeasurementReached):
                        writer.main(argv)
                    measure.assert_called_once()
                    preflight = [call for call in flags.call_args_list if call.args[1] == "calibration.acceptance_preflight_unverified"]
                    self.assertEqual(len(preflight), 1)
                    self.assertEqual(preflight[0].kwargs["observed"], {"reason": "desk-unverified", "context": {"shape": "fixture"}})
                else:
                    self.assertEqual(writer.main(argv), 2)
                    flags.assert_not_called()
                    measure.assert_not_called()
                sampler.assert_not_called()
