from __future__ import annotations

import math
import unittest

from joulewise.clock import ClockStamp
from joulewise.uncertainty_evidence import (
    derive_idle_drift_evidence,
    derive_powermetrics_clock_evidence,
    prediction_guard_w,
)


def stamp(epoch: float, monotonic: float, width: float = 0.0) -> ClockStamp:
    return ClockStamp(epoch, monotonic, monotonic + width, 0.001, 0.0001)


class ClockEvidenceTests(unittest.TestCase):
    def evidence(self, *, stop_epoch: float = 103.0):
        stamps = {
            "pre_spawn": stamp(100.0, 10.0),
            "first_parse": stamp(100.2, 10.2),
            "sampling_started": stamp(100.21, 10.21),
            "sampling_stopped": stamp(stop_epoch, 13.0),
            "post_parse": stamp(stop_epoch + 0.1, 13.1),
        }
        return derive_powermetrics_clock_evidence(
            stamps=stamps,
            elapsed_s=[0.1, 1.0, 1.0],
            plist_timestamp_s=[100.0, 101.0, 102.0],
        )

    def test_paired_stamp_envelope_and_midpoint_timestamp_arithmetic(self) -> None:
        evidence, point = self.evidence()
        clock = evidence["clock_anchor"]
        self.assertEqual(clock["status"], "bounded")
        self.assertAlmostEqual(clock["wall_minus_monotonic_lower_s"], 89.999)
        self.assertAlmostEqual(clock["wall_minus_monotonic_upper_s"], 90.001)
        self.assertAlmostEqual(point, 100.1)
        self.assertNotAlmostEqual(point, 100.2)  # no d0 double advance

    def test_wall_clock_step_enlarges_envelope(self) -> None:
        baseline, _ = self.evidence()
        stamps = {
            "pre_spawn": stamp(100.0, 10.0),
            "first_parse": stamp(100.2, 10.2),
            "sampling_started": stamp(105.21, 10.21),
            "sampling_stopped": stamp(108.0, 13.0),
            "post_parse": stamp(108.1, 13.1),
        }
        stepped, _ = derive_powermetrics_clock_evidence(
            stamps=stamps,
            elapsed_s=[0.1, 1.0, 1.0],
            plist_timestamp_s=[100.0, 101.0, 102.0],
        )
        self.assertGreater(
            stepped["clock_anchor"]["anchor_only_bound_s"],
            baseline["clock_anchor"]["anchor_only_bound_s"],
        )

    def test_nonfinite_or_reversed_stamp_is_unknown(self) -> None:
        stamps = {name: stamp(100.0, 10.0) for name in (
            "pre_spawn", "first_parse", "sampling_started", "sampling_stopped", "post_parse"
        )}
        stamps["first_parse"] = ClockStamp(100.0, 11.0, 10.0, 0.0, 0.0)
        evidence, point = derive_powermetrics_clock_evidence(
            stamps=stamps, elapsed_s=[1.0], plist_timestamp_s=[100.0]
        )
        self.assertIsNone(point)
        self.assertEqual(evidence["clock_anchor"]["reason"], "clock_stamp_invalid")

    def test_plist_date_is_consistency_only_and_cannot_tighten_anchor(self) -> None:
        evidence, _ = self.evidence()
        self.assertAlmostEqual(evidence["clock_anchor"]["anchor_only_bound_s"], 0.101)
        inconsistent, point = derive_powermetrics_clock_evidence(
            stamps={
                "pre_spawn": stamp(100.0, 10.0),
                "first_parse": stamp(100.2, 10.2),
                "sampling_started": stamp(100.21, 10.21),
                "sampling_stopped": stamp(103.0, 13.0),
                "post_parse": stamp(103.1, 13.1),
            },
            elapsed_s=[0.1, 1.0, 1.0],
            plist_timestamp_s=[500.0, 501.0, 502.0],
        )
        self.assertIsNotNone(point)
        self.assertEqual(inconsistent["clock_anchor"]["status"], "unknown")
        self.assertEqual(
            inconsistent["clock_anchor"]["reason"], "plist_timestamp_inconsistent"
        )

    def test_effective_bound_is_maximum_of_anchor_and_both_phases(self) -> None:
        evidence, _ = self.evidence(stop_epoch=110.0)
        clock = evidence["clock_anchor"]
        phase = evidence["sample_phase"]
        self.assertEqual(
            clock["effective_clock_anchor_bound_s"],
            max(
                clock["anchor_only_bound_s"],
                phase["marker_to_first_sample_phase_bound_s"],
                phase["marker_to_last_sample_phase_bound_s"],
            ),
        )


class IdleDriftEvidenceTests(unittest.TestCase):
    def test_full_pre_post_envelope_retains_large_sample(self) -> None:
        evidence, guard, bound = derive_idle_drift_evidence(
            pre_power_w=[9.0, 10.0, 11.0],
            post_power_w=[10.0, 12.0, 50.0],
            pre_power_w_mean=10.0,
            pre_idle_window_suspect=False,
            post_idle_window_suspect=False,
        )
        self.assertEqual(bound, 40.0)
        self.assertEqual(evidence["run_observed_envelope_w"], 40.0)
        self.assertEqual(guard["n_bundles"], 0)

    def test_contamination_or_too_few_samples_withholds_scalar(self) -> None:
        for kwargs in (
            {"pre_idle_window_suspect": True, "post_idle_window_suspect": False},
            {"pre_idle_window_suspect": False, "post_idle_window_suspect": True},
        ):
            evidence, _guard, bound = derive_idle_drift_evidence(
                pre_power_w=[1.0, 1.0, 1.0],
                post_power_w=[1.0, 1.0, 1.0],
                pre_power_w_mean=1.0,
                **kwargs,
            )
            self.assertIsNone(bound)
            self.assertEqual(evidence["reason"], "sentinel_contaminated")
        evidence, _guard, bound = derive_idle_drift_evidence(
            pre_power_w=[1.0, 1.0],
            post_power_w=[1.0, 1.0, 1.0],
            pre_power_w_mean=1.0,
            pre_idle_window_suspect=False,
            post_idle_window_suspect=False,
        )
        self.assertIsNone(bound)
        self.assertEqual(evidence["reason"], "insufficient_idle_samples")

    def test_calibration_combination_is_exact_max_and_guard_formula(self) -> None:
        guard = {
            "status": "applied",
            "method": "p2_015_prediction_guard_v1",
            "guard_w": 5.0,
            "n_bundles": 5,
            "bundle_sha256": ["a" * 64],
            "cell_id": "cell",
            "artifact_sha256": "b" * 64,
        }
        evidence, _guard, bound = derive_idle_drift_evidence(
            pre_power_w=[0.0, 1.0, 2.0],
            post_power_w=[0.0, 1.0, 2.0],
            pre_power_w_mean=1.0,
            pre_idle_window_suspect=False,
            post_idle_window_suspect=False,
            calibration_guard=guard,
        )
        self.assertEqual(bound, 5.0)
        self.assertEqual(evidence["effective_bound_w"], 5.0)
        self.assertTrue(math.isfinite(prediction_guard_w([1.0, 2.0, 3.0], 4.303)))


if __name__ == "__main__":
    unittest.main()
