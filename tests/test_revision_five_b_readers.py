"""Revision-5 evidence cannot reach legacy readers of calibration bounds."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.calibration_bracketing import REVISION_FIVE_EPOCH
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
        for forbidden in ("identity_epoch", "battery_float"):
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


if __name__ == "__main__":
    unittest.main()
