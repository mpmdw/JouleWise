"""P2-038.3 environment-admission reconstruction coverage."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import tempfile
import unittest

from joulewise import environment_admission
from joulewise.clock import ClockStamp
from joulewise.uncertainty_evidence import (
    CLOCK_METHOD_V3,
    NativeAnchorRecord,
    derive_powermetrics_anchor_v2,
    derive_powermetrics_anchor_v3,
)
from tests.test_powermetrics import FIXTURE


class EnvironmentAdmissionAnchorEraTests(unittest.TestCase):
    def test_rate_aware_knife_edge_resolves_real_v3_shape(self) -> None:
        """A native-intersection v2 failure is reconstructed under stored v3.

        This is the root-cause shape: float-era elapsed values accumulate past
        a native-second boundary, while the v3 exact-nanosecond record fields
        retain the rate-aware feasible set.  The environment consumer must use
        the stored v3 method and admit the fully nominal coverage interval.
        """

        base_s = 1_700_000_000.0
        stamps = {
            "pre_spawn": ClockStamp(base_s, 100.0, 100.000002, 1e-6, 1e-6),
            "first_parse": ClockStamp(
                base_s + 1.001, 101.001, 101.001002, 1e-6, 1e-6
            ),
            "sampling_started": ClockStamp(
                base_s + 2.0, 102.0, 102.000002, 1e-6, 1e-6
            ),
            "sampling_stopped": ClockStamp(
                base_s + 103.0, 203.0, 203.000002, 1e-6, 1e-6
            ),
            "post_parse": ClockStamp(
                base_s + 103.1, 203.1, 203.100002, 1e-6, 1e-6
            ),
        }
        native = [
            NativeAnchorRecord(
                elapsed_s=1.01,
                native_timestamp_s=base_s + index + 1,
                power_w=2.0,
                energy_j=2.02,
                is_delta=True,
                elapsed_ns=1_000_000_000,
                native_timestamp_ns=round((base_s + index + 1) * 1_000_000_000),
            )
            for index in range(101)
        ]
        v2 = derive_powermetrics_anchor_v2(stamps=stamps, records=native)
        v3 = derive_powermetrics_anchor_v3(stamps=stamps, records=native)
        self.assertEqual(v2["detail"], "native_intersection_empty")
        self.assertEqual(v3["status"], "bounded")

        nominal = SimpleNamespace(
            timestamp_s=base_s + 1.0,
            elapsed_ns=1_000_000_000,
            thermal_pressure="nominal",
        )
        metadata = {
            "environment_admission": {
                "attempts": [{"attempt": 1, "start_s": base_s - 1.0, "end_s": base_s}]
            },
            "uncertainty_evidence": {"clock_anchor": v3},
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "raw").mkdir()
            (root / "raw" / "powermetrics_idle.plist").write_bytes(b"fixture")
            (root / "raw" / "powermetrics.plist").write_bytes(b"fixture")
            with (
                patch(
                    "joulewise.adapters.powermetrics.parse_powermetrics_records",
                    side_effect=([nominal], [nominal], [nominal, SimpleNamespace(
                        timestamp_s=base_s + 2.0,
                        elapsed_ns=1_000_000_000,
                        thermal_pressure="nominal",
                    )]),
                ),
                patch(
                    "joulewise.adapters.powermetrics.anchor_records_from_powermetrics",
                    return_value=native,
                ),
            ):
                reasons = environment_admission._window_thermal_pressure_refusals(
                    metadata,
                    bundle_path=root,
                    measured_window_start_s=base_s + 1.0,
                    measured_window_end_s=base_s + 2.0,
                )
        self.assertEqual(reasons, ())

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
