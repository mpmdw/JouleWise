"""R5(n) cadence report uses only raw plist intervals and is pin-free."""
from __future__ import annotations

import json
import contextlib
import io
from pathlib import Path
import plistlib
import tempfile
import unittest
from tests.fixtures.epoch_bootstrap.build import Slot, build_derivation_ledger

from scripts import calibration_cadence_report as report


ROOT = Path(__file__).resolve().parents[1]


def write_capture(root: Path, name: str, lengths_ms: list[int]) -> None:
    path = root / name / "raw" / "powermetrics.plist"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x00".join(
        plistlib.dumps({"elapsed_ns": value * 1_000_000})
        for value in lengths_ms
    ) + b"\x00")


class CadenceReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._ledger_tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls._ledger_tmp.cleanup)
        root = Path(cls._ledger_tmp.name)
        cls.clean = build_derivation_ledger(root / "clean", [Slot("0.02")])
        cls.charging = build_derivation_ledger(
            root / "charging", [Slot("0.02", battery_mode="charging")],
        )

    def session_args(self, fixture: dict[str, Path] | None = None) -> dict:
        source = self.clean if fixture is None else fixture
        return {"ledger": source["ledger"], "head_pin": source["pin"],
                "session_id": "derivation-night-1"}

    def test_median_of_capture_medians_controls_strict_stop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_capture(root, "d01", [999, 100, 120, 140])
            write_capture(root, "d02", [999, 150, 150, 200])
            row = report.report_window("W1", root, **self.session_args())
            self.assertNotIn("diagnostic_only", row)
            self.assertEqual([c["median_native_frame_ms"] for c in row["captures"]], [120, 150])
            self.assertEqual(row["median_of_capture_medians_ms"], 135)
            self.assertEqual(row["max_native_frame_ms"], 200)
            self.assertEqual(row["r5_n_verdict"], "CONTINUE")
            write_capture(root, "d02", [999, 200, 200, 250])
            self.assertEqual(report.report_window("W1", root, **self.session_args())["r5_n_verdict"], "STOP")

    def test_charging_session_is_diagnostic_with_cadence_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_capture(root, "d01", [999, 100, 120])
            row = report.report_window("W1", root, **self.session_args(self.charging))
            self.assertEqual(row["diagnostic_only"], "battery_float_confounded")
            self.assertEqual(row["median_native_frame_ms"], 110)

    def test_invalid_or_short_stream_refuses(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least two"):
            report.native_intervals_ms(plistlib.dumps({"elapsed_ns": 100_000_000}))
        with self.assertRaisesRegex(ValueError, "invalid elapsed_ns"):
            report.native_intervals_ms(b"\x00".join([
                plistlib.dumps({"elapsed_ns": 100_000_000}),
                plistlib.dumps({"elapsed_ns": True}),
            ]))

    def test_cli_reports_each_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first, second = root / "W1", root / "W2"
            write_capture(first, "d01", [999, 140, 150])
            write_capture(second, "d01", [999, 160, 170])
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(report.main([
                    "--window", f"W1={first}", "--window", f"W2={second}",
                    "--calibration-ledger", str(self.clean["ledger"]),
                    "--head-pin", str(self.clean["pin"]),
                    "--session", "W1=derivation-night-1", "--session", "W2=derivation-night-1",
                ]), 0)
            rows = json.loads(output.getvalue())["windows"]
            self.assertEqual([row["r5_n_verdict"] for row in rows], ["CONTINUE", "STOP"])

    def test_cli_refuses_unpaired_window_and_session_labels(self) -> None:
        with self.assertRaises(SystemExit) as caught, contextlib.redirect_stderr(io.StringIO()):
            report.main([
                "--window", "W1=/tmp/capture", "--calibration-ledger", str(self.clean["ledger"]),
                "--session", "W2=derivation-night-1",
            ])
        self.assertEqual(caught.exception.code, 2)

    def test_report_imports_none_of_the_four_pinned_modules(self) -> None:
        text = (ROOT / "scripts/calibration_cadence_report.py").read_text()
        for name in ("powermetrics_fiducial", "uncertainty_evidence", "adapters.powermetrics", "joulewise.reduce"):
            self.assertNotIn(name, text)


if __name__ == "__main__":
    unittest.main()
