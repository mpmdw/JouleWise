"""Hand-computable P2-044 idle-dependence fixtures."""

from __future__ import annotations

import math
import plistlib
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from joulewise.bundle_read import BundleReader
from joulewise.idle_dependence import (
    REASON_CODES,
    derive_idle_mean_uncertainty,
    estimate_newey_west_bartlett,
    idle_mean_energy_variance_j2,
)
from joulewise.schemas import IdleBaseline, TelemetryBackend


def powermetrics_stream(powers_w: list[float], intervals_s: list[float]) -> bytes:
    documents = []
    for power_w, interval_s in zip(powers_w, intervals_s, strict=True):
        documents.append(
            {
                "timestamp": datetime(2026, 7, 11, tzinfo=timezone.utc),
                "elapsed_ns": int(interval_s * 1_000_000_000),
                "processor": {
                    "cpu_power": power_w * 1000.0,
                    "gpu_power": 0.0,
                    "ane_power": 0.0,
                    "cpu_energy": 0,
                    "gpu_energy": 0,
                    "ane_energy": 0,
                },
            }
        )
    return b"\0".join(plistlib.dumps(document) for document in documents)


def baseline(powers_w: list[float], intervals_s: list[float]) -> IdleBaseline:
    mean_w = math.fsum(powers_w) / len(powers_w)
    stddev_w = math.sqrt(
        math.fsum((value - mean_w) ** 2 for value in powers_w)
        / (len(powers_w) - 1)
    )
    return IdleBaseline(
        power_w_mean=mean_w,
        power_w_stddev=stddev_w,
        duration_s=math.fsum(intervals_s),
        sample_count=len(powers_w),
        telemetry_backend=TelemetryBackend.POWERMETRICS,
    )


class HandComputableFixtureTests(unittest.TestCase):
    def test_iid_floor_fixture_exact_values(self) -> None:
        estimate = estimate_newey_west_bartlett([0.0, 2.0, 0.0, 2.0], 3)

        self.assertAlmostEqual(estimate.sample_variance_w2, 4 / 3, places=15)
        self.assertAlmostEqual(estimate.iid_variance_of_mean_w2, 1 / 3, places=15)
        self.assertEqual(estimate.hac_variance_of_mean_w2, 1 / 16)
        self.assertAlmostEqual(
            estimate.governed_variance_of_mean_w2, 1 / 3, places=15
        )
        self.assertEqual(estimate.effective_sample_size, 4.0)

    def test_correlated_fixture_exact_values(self) -> None:
        estimate = estimate_newey_west_bartlett(
            [0.0, 0.0, 0.0, 2.0, 2.0, 2.0], 2
        )

        self.assertAlmostEqual(estimate.sample_variance_w2, 6 / 5, places=15)
        self.assertAlmostEqual(estimate.iid_variance_of_mean_w2, 1 / 5, places=15)
        self.assertAlmostEqual(estimate.hac_variance_of_mean_w2, 5 / 18, places=15)
        self.assertAlmostEqual(
            estimate.governed_variance_of_mean_w2, 5 / 18, places=15
        )
        self.assertAlmostEqual(estimate.effective_sample_size, 108 / 25, places=15)

    def test_correlated_fixture_corrected_energy_variance_is_five_halves(self) -> None:
        estimate = estimate_newey_west_bartlett(
            [0.0, 0.0, 0.0, 2.0, 2.0, 2.0], 2
        )

        self.assertEqual(
            idle_mean_energy_variance_j2(
                3.0, estimate.governed_variance_of_mean_w2
            ),
            5 / 2,
        )

    def test_degenerate_fixture_has_zero_variance_and_raw_ess(self) -> None:
        estimate = estimate_newey_west_bartlett([5.0, 5.0, 5.0, 5.0], 3)

        self.assertEqual(estimate.sample_variance_w2, 0.0)
        self.assertEqual(estimate.iid_variance_of_mean_w2, 0.0)
        self.assertEqual(estimate.hac_variance_of_mean_w2, 0.0)
        self.assertEqual(estimate.governed_variance_of_mean_w2, 0.0)
        self.assertEqual(estimate.effective_sample_size, 4.0)

    def test_eligibility_fixture_below_three_bandwidths_is_not_estimable(self) -> None:
        powers_w = [5.0] * 20
        intervals_s = [1.0] * 20
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "raw").mkdir()
            (bundle / "raw" / "powermetrics_idle.plist").write_bytes(
                powermetrics_stream(powers_w, intervals_s)
            )
            result = derive_idle_mean_uncertainty(
                BundleReader(bundle), baseline(powers_w, intervals_s)
            )

        self.assertEqual(result["status"], "not_estimable")
        self.assertEqual(
            result["reason_codes"], ["idle_trace_span_below_three_bandwidths"]
        )
        self.assertIsNone(result["governed_variance_of_mean_w2"])
        self.assertIsNone(result["effective_sample_size"])


class GovernedEvidenceTests(unittest.TestCase):
    def test_reason_code_vocabulary_is_frozen(self) -> None:
        self.assertEqual(
            REASON_CODES,
            (
                "raw_idle_trace_unavailable",
                "raw_idle_trace_invalid",
                "nonfinite_idle_power",
                "insufficient_idle_samples",
                "idle_trace_span_below_three_bandwidths",
                "idle_cadence_irregular",
                "idle_metadata_mismatch",
                "backend_policy_not_frozen",
            ),
        )

    def test_raw_metadata_mismatch_withholds_estimate(self) -> None:
        powers_w = [5.0] * 33
        intervals_s = [1.0] * 33
        mismatched = baseline(powers_w, intervals_s)
        mismatched = IdleBaseline(
            power_w_mean=5.1,
            power_w_stddev=mismatched.power_w_stddev,
            duration_s=mismatched.duration_s,
            sample_count=mismatched.sample_count,
            telemetry_backend=mismatched.telemetry_backend,
        )
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "raw").mkdir()
            (bundle / "raw" / "powermetrics_idle.plist").write_bytes(
                powermetrics_stream(powers_w, intervals_s)
            )
            result = derive_idle_mean_uncertainty(BundleReader(bundle), mismatched)

        self.assertEqual(result["status"], "not_estimable")
        self.assertEqual(result["reason_codes"], ["idle_metadata_mismatch"])

    def test_eligible_regular_trace_is_estimated(self) -> None:
        powers_w = [5.0] * 33
        intervals_s = [1.0] * 33
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "raw").mkdir()
            (bundle / "raw" / "powermetrics_idle.plist").write_bytes(
                powermetrics_stream(powers_w, intervals_s)
            )
            result = derive_idle_mean_uncertainty(
                BundleReader(bundle), baseline(powers_w, intervals_s)
            )

        self.assertEqual(result["status"], "estimated")
        self.assertEqual(result["lag_count"], 10)
        self.assertEqual(result["effective_sample_size"], 33.0)
        self.assertEqual(result["reason_codes"], [])

    def test_irregular_cadence_fails_closed_without_resampling(self) -> None:
        powers_w = [5.0] * 33
        intervals_s = [0.5] * 4 + [1.0] * 25 + [2.0] * 4
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "raw").mkdir()
            (bundle / "raw" / "powermetrics_idle.plist").write_bytes(
                powermetrics_stream(powers_w, intervals_s)
            )
            result = derive_idle_mean_uncertainty(
                BundleReader(bundle), baseline(powers_w, intervals_s)
            )

        self.assertEqual(result["status"], "not_estimable")
        self.assertEqual(result["reason_codes"], ["idle_cadence_irregular"])
        self.assertIsNone(result["governed_variance_of_mean_w2"])

    def test_other_physical_backend_has_no_inherited_policy(self) -> None:
        other = IdleBaseline(
            power_w_mean=5.0,
            power_w_stddev=1.0,
            duration_s=30.0,
            sample_count=300,
            telemetry_backend=TelemetryBackend.NVIDIA_SMI,
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = derive_idle_mean_uncertainty(BundleReader(Path(tmp)), other)
        self.assertEqual(result["status"], "not_estimable")
        self.assertEqual(result["reason_codes"], ["backend_policy_not_frozen"])

    def test_nonfinite_raw_idle_power_has_specific_reason(self) -> None:
        powers_w = [5.0] * 33
        powers_w[10] = math.nan
        intervals_s = [1.0] * 33
        recorded = baseline([5.0] * 33, intervals_s)
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "raw").mkdir()
            (bundle / "raw" / "powermetrics_idle.plist").write_bytes(
                powermetrics_stream(powers_w, intervals_s)
            )
            result = derive_idle_mean_uncertainty(BundleReader(bundle), recorded)

        self.assertEqual(result["status"], "not_estimable")
        self.assertEqual(result["reason_codes"], ["nonfinite_idle_power"])
