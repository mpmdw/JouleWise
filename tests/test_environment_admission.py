"""P2-038.3 environment-admission reconstruction coverage."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import tempfile
import unittest

from joulewise import environment_admission
from joulewise.uncertainty_evidence import CLOCK_METHOD_V3
from tests.test_powermetrics import FIXTURE


class EnvironmentAdmissionAnchorEraTests(unittest.TestCase):
    def test_v3_stored_method_drives_thermal_window_reconstruction(self) -> None:
        # A v2 native intersection can be empty for this shape while the
        # rate-aware v3 reconstruction is bounded.  The environment reader
        # must dispatch the stored v3 method rather than retrying v2.
        record = SimpleNamespace(
            timestamp_s=102.0,
            elapsed_ns=2_000_000_000,
            thermal_pressure="nominal",
        )
        metadata = {
            "environment_admission": {
                "attempts": [{"attempt": 1, "start_s": 90.0, "end_s": 100.0}]
            },
            "uncertainty_evidence": {
                "clock_anchor": {
                    "method": CLOCK_METHOD_V3,
                    "clock_stamps": {},
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw").mkdir()
            (root / "raw" / "powermetrics_idle.plist").write_bytes(FIXTURE.read_bytes())
            (root / "raw" / "powermetrics.plist").write_bytes(FIXTURE.read_bytes())
            with (
                patch(
                    "joulewise.adapters.powermetrics.parse_powermetrics_records",
                    side_effect=([record], [record], [record]),
                ),
                patch(
                    "joulewise.adapters.powermetrics.anchor_records_from_powermetrics",
                    return_value=[],
                ),
                patch(
                    "joulewise.uncertainty_evidence.resolve_anchor_reconstructor",
                    return_value=lambda **_kwargs: {
                        "status": "bounded",
                        "first_sample_end_point_epoch_s": 102.0,
                    },
                ) as resolver,
            ):
                reasons = environment_admission._window_thermal_pressure_refusals(
                    metadata,
                    bundle_path=root,
                    measured_window_start_s=100.0,
                    measured_window_end_s=102.0,
                )
        self.assertEqual(reasons, ())
        resolver.assert_called_once_with(CLOCK_METHOD_V3)


if __name__ == "__main__":
    unittest.main()
