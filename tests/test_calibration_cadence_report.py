"""R5(n) cadence report uses only raw plist intervals and is pin-free."""
from __future__ import annotations

import json
import contextlib
import io
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import unittest
from tests.fixtures.epoch_bootstrap.build import (
    PREREGISTRATION_SHA256, Slot, build_derivation_ledger)

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
        # Each window carries its committed harvest verdict (obligations v1.1
        # §4.5): the report refuses to run before the record exists.
        cls.clean = build_derivation_ledger(root / "clean", [Slot("0.02", native_frames=True)],
                                            verdict_records=True)
        cls.charging = build_derivation_ledger(
            root / "charging", [Slot("0.02", battery_mode="charging", native_frames=True,
                                     native_frame_lengths_ms=(999, 100, 120))], verdict_records=True,
        )

    def session_args(self, fixture: dict[str, Path] | None = None) -> dict:
        source = self.clean if fixture is None else fixture
        return {"ledger": source["ledger"], "head_pin": source["pin"],
                "session_id": "derivation-night-1",
                "preregistration_sha256": PREREGISTRATION_SHA256}

    def test_median_of_capture_medians_controls_strict_stop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = build_derivation_ledger(root / "continue", [
                Slot("0.02", native_frames=True, native_frame_lengths_ms=(999, 100, 120, 140)),
                Slot("0.02", native_frames=True, native_frame_lengths_ms=(999, 150, 150, 200)),
            ], verdict_records=True)
            row = report.report_window("W1", fixture["runs"] / "instrument_validation",
                                       **self.session_args(fixture))
            self.assertNotIn("diagnostic_only", row)
            self.assertEqual([c["median_native_frame_ms"] for c in row["captures"]], [120, 150])
            self.assertEqual(row["median_of_capture_medians_ms"], 135)
            self.assertEqual(row["max_native_frame_ms"], 200)
            self.assertEqual(row["r5_n_verdict"], "CONTINUE")
            stopped = build_derivation_ledger(root / "stop", [
                Slot("0.02", native_frames=True, native_frame_lengths_ms=(999, 100, 120, 140)),
                Slot("0.02", native_frames=True, native_frame_lengths_ms=(999, 200, 200, 250)),
            ], verdict_records=True)
            self.assertEqual(report.report_window(
                "W1", stopped["runs"] / "instrument_validation",
                **self.session_args(stopped))["r5_n_verdict"], "STOP")

    def test_charging_session_is_diagnostic_with_cadence_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = report.report_window("W1", self.charging["runs"] / "instrument_validation",
                                       **self.session_args(self.charging))
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
            fixture = build_derivation_ledger(root / "both", [
                Slot("0.02", native_frames=True, native_frame_lengths_ms=(999, 140, 150))],
                session_id="W1", second_session=("W2", [
                    Slot("0.02", native_frames=True, native_frame_lengths_ms=(999, 160, 170))]),
                verdict_records=True)
            first = fixture["runs"] / "instrument_validation/W1-*"
            second = fixture["runs"] / "instrument_validation/W2-*"
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(report.main([
                    "--window", f"W1={first}", "--window", f"W2={second}",
                    "--calibration-ledger", str(fixture["ledger"]),
                    "--head-pin", str(fixture["pin"]),
                    "--session", "W1=W1", "--session", "W2=W2",
                    "--preregistration-sha256", PREREGISTRATION_SHA256,
                ]), 0)
            rows = json.loads(output.getvalue())["windows"]
            self.assertEqual([row["r5_n_verdict"] for row in rows], ["CONTINUE", "STOP"])

    def test_cli_refuses_unpaired_window_and_session_labels(self) -> None:
        with self.assertRaises(SystemExit) as caught, contextlib.redirect_stderr(io.StringIO()):
            report.main([
                "--window", "W1=/tmp/capture", "--calibration-ledger", str(self.clean["ledger"]),
                "--session", "W2=derivation-night-1",
                "--preregistration-sha256", PREREGISTRATION_SHA256,
            ])
        self.assertEqual(caught.exception.code, 2)

    def test_swapped_session_extra_captures_and_tamper_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "both", [Slot("0.02", native_frames=True)],
                session_id="W1", second_session=("W2", [Slot("0.02", native_frames=True)]),
                verdict_records=True)
            inventory = fixture["runs"] / "instrument_validation"
            args = {"ledger": fixture["ledger"], "head_pin": fixture["pin"],
                    "preregistration_sha256": PREREGISTRATION_SHA256}
            with self.assertRaisesRegex(ValueError, "capture paths disagree"):
                report.report_window("W1", inventory / "W2-d01/raw/powermetrics.plist",
                                     session_id="W1", **args)
            with self.assertRaisesRegex(ValueError, "capture paths disagree"):
                report.report_window("W1", inventory, session_id="W1", **args)
            path = inventory / "W1-d01/raw/powermetrics.plist"
            path.write_bytes(path.read_bytes() + b"tampered")
            with self.assertRaisesRegex(ValueError, "digest disagrees"):
                report.report_window("W1", path, session_id="W1", **args)

    def test_registration_digest_missing_and_wrong_refuse(self) -> None:
        window = self.clean["runs"] / "instrument_validation"
        with self.assertRaisesRegex(ValueError, "preregistration-sha256 is required"):
            report.report_window("W1", window, ledger=self.clean["ledger"],
                                 head_pin=self.clean["pin"], session_id="derivation-night-1")
        with self.assertRaisesRegex(ValueError, "preregistration_sha256"):
            report.report_window("W1", window, **{**self.session_args(),
                                                  "preregistration_sha256": "0" * 64})

    def test_cli_bootstraps_repo_from_clean_tmp_cwd(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/calibration_cadence_report.py"), "--help"],
            cwd="/tmp", env={key: value for key, value in os.environ.items()
                             if key not in {"PYTHONPATH", "PYTHONHOME"}},
            capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_report_imports_none_of_the_four_pinned_modules(self) -> None:
        text = (ROOT / "scripts/calibration_cadence_report.py").read_text()
        for name in ("powermetrics_fiducial", "uncertainty_evidence", "adapters.powermetrics", "joulewise.reduce"):
            self.assertNotIn(name, text)


if __name__ == "__main__":
    unittest.main()
