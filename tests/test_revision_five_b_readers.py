"""Revision-5 evidence cannot reach legacy readers of calibration bounds."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.calibration_bracketing import REVISION_FIVE_EPOCH
from joulewise import battery_float
from joulewise.controller import _load_instrument_calibration_attachment
from scripts import calibration_ledger_backfill as backfill
from tests.fixtures.epoch_bootstrap.build import TARGET_EPOCH


class RevisionFiveBReaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def evidence(self, forbidden: str) -> dict:
        self.assertEqual(TARGET_EPOCH, REVISION_FIVE_EPOCH)
        bindings = dict(TARGET_EPOCH)
        if forbidden == "battery_float":
            bindings["os_build"] = "25G99"
        evidence = {
            "validation_id": "capture",
            "status": "valid",
            "bindings": bindings,
            "b_fiducial_s": 0.031,
        }
        if forbidden == "battery_float":
            evidence["battery_float"] = {}
        return evidence

    def test_backfill_refuses_revision_five_before_bound(self) -> None:
        class BoundGuard(dict):
            def get(self, key, default=None):
                if key == "b_fiducial_s":
                    raise AssertionError("B read")
                return super().get(key, default)

            def __getitem__(self, key):
                if key == "b_fiducial_s":
                    raise AssertionError("B read")
                return super().__getitem__(key)

        for forbidden in ("identity_epoch", "battery_float"):
            with self.subTest(forbidden=forbidden):
                directory = self.root / forbidden
                directory.mkdir()
                (directory / "manifest.json").write_text('{"artifacts": {}}')
                evidence = self.evidence(forbidden)
                (directory / "instrument_evidence.json").write_text(json.dumps(evidence))
                with patch.object(backfill, "_json_object", side_effect=[
                    {"artifacts": {}}, BoundGuard(evidence),
                ]):
                    with self.assertRaisesRegex(ValueError, "revision_five"):
                        backfill._candidate(directory)

    def test_controller_attachment_refuses_before_physics_or_bound(self) -> None:
        for forbidden in ("identity_epoch",):
            with self.subTest(forbidden=forbidden):
                directory = self.root / f"attachment-{forbidden}"
                directory.mkdir()
                evidence = self.evidence(forbidden)
                evidence["bindings"].update(powermetrics_sha256="a" * 64)
                raw = json.dumps(evidence).encode()
                (directory / "instrument_evidence.json").write_bytes(raw)
                (directory / "raw").mkdir()
                (directory / "raw/powermetrics.plist").write_bytes(b"raw")
                (directory / "events.jsonl").write_bytes(b"events")
                (directory / "manifest.json").write_text(json.dumps({
                    "schema_version": "joulewise.instrument_validation_manifest.v1",
                    "artifacts": {
                        "instrument_evidence.json": hashlib.sha256(raw).hexdigest(),
                        "raw/powermetrics.plist": hashlib.sha256(b"raw").hexdigest(),
                        "events.jsonl": hashlib.sha256(b"events").hexdigest(),
                    },
                }))
                with patch("joulewise.powermetrics_fiducial.verify_stored_evidence_physics",
                           side_effect=AssertionError("B read")) as physics:
                    with self.assertRaisesRegex(ValueError, "revision_five"):
                        _load_instrument_calibration_attachment(
                            directory, power_policy="ac_high_power",
                            runtime_powermetrics_sha256="a" * 64,
                            runtime_power_policy="ac_high_power",
                        )
                physics.assert_not_called()

    def test_charging_capture_refuses_attachment_before_physics(self) -> None:
        directory = self.root / "charging-capture"
        (directory / "raw").mkdir(parents=True)
        pair = {}
        artifacts = {}
        for phase in ("pre", "post"):
            relative = f"raw/battery_float.{phase}.ioreg"
            raw = (Path(__file__).parent / "fixtures/battery_float" /
                   ("charging-synthetic-from-real.ioreg" if phase == "pre" else "float.ioreg")).read_bytes()
            (directory / relative).write_bytes(raw)
            artifacts[relative] = hashlib.sha256(raw).hexdigest()
            stamps = iter((10, 20) if phase == "pre" else (80, 90))
            pair[phase], _ = battery_float.observe(
                phase=f"slot_{phase}", raw_path=relative,
                wall_time_s=1790373526, monotonic_ns=lambda: next(stamps),
                runner=lambda argv, body=raw: subprocess.CompletedProcess(argv, 0, body, b""),
            )
        evidence = self.evidence("battery_float")
        evidence["battery_float"] = pair
        evidence["bindings"]["powermetrics_sha256"] = "a" * 64
        for relative, raw in (
            ("instrument_evidence.json", json.dumps(evidence).encode()),
            ("raw/powermetrics.plist", b"raw"),
            ("events.jsonl", b"events"),
        ):
            (directory / relative).write_bytes(raw)
            artifacts[relative] = hashlib.sha256(raw).hexdigest()
        (directory / "manifest.json").write_text(json.dumps({
            "schema_version": "joulewise.instrument_validation_manifest.v1",
            "artifacts": artifacts,
        }))
        with patch("joulewise.powermetrics_fiducial.verify_stored_evidence_physics",
                   side_effect=AssertionError("physics read")) as physics:
            with self.assertRaisesRegex(ValueError, "battery_float_confounded"):
                _load_instrument_calibration_attachment(
                    directory, power_policy="ac_high_power",
                    runtime_powermetrics_sha256="a" * 64,
                    runtime_power_policy="ac_high_power",
                )
        physics.assert_not_called()

    def test_passing_non_revision_five_capture_attaches_raw_pair(self) -> None:
        directory = self.root / "passing-capture"
        (directory / "raw").mkdir(parents=True)
        pair = {}
        artifacts = {}
        raw = (Path(__file__).parent / "fixtures/battery_float/float.ioreg").read_bytes()
        for phase in ("pre", "post"):
            relative = f"raw/battery_float.{phase}.ioreg"
            (directory / relative).write_bytes(raw)
            stamps = iter((10, 20) if phase == "pre" else (80, 90))
            pair[phase], _ = battery_float.observe(
                phase=f"slot_{phase}", raw_path=relative,
                wall_time_s=1790373526, monotonic_ns=lambda: next(stamps),
                runner=lambda argv: subprocess.CompletedProcess(argv, 0, raw, b""),
            )
        evidence = self.evidence("battery_float")
        evidence["battery_float"] = pair
        evidence["bindings"]["powermetrics_sha256"] = "a" * 64
        for relative, body in (
            ("instrument_evidence.json", json.dumps(evidence).encode()),
            ("raw/powermetrics.plist", b"raw"),
            ("events.jsonl", b"events"),
        ):
            (directory / relative).write_bytes(body)
            artifacts[relative] = hashlib.sha256(body).hexdigest()
        (directory / "manifest.json").write_text(json.dumps({
            "schema_version": "joulewise.instrument_validation_manifest.v1",
            "artifacts": artifacts,
        }))
        with patch("joulewise.powermetrics_fiducial.verify_stored_evidence_physics",
                   return_value=0.031) as physics:
            attachment = _load_instrument_calibration_attachment(
                directory, power_policy="ac_high_power",
                runtime_powermetrics_sha256="a" * 64,
                runtime_power_policy="ac_high_power",
            )
        physics.assert_called_once()
        self.assertEqual(attachment.metadata["b_fiducial_s"], 0.031)
        for phase in ("pre", "post"):
            self.assertEqual(attachment.files[f"raw/battery_float.{phase}.ioreg"], raw)


if __name__ == "__main__":
    unittest.main()
