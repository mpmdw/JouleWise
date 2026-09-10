"""Epoch-representation allowances must not admit physically missing evidence."""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import statistics
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise import environment_admission
from joulewise.bundle_read import TracePoint, Window
from joulewise.clock import FakeClock
from joulewise.controller import cooldown_gate
from joulewise.load_transition_alignment import (
    build_alignment_artifact,
    validate_alignment_artifact,
)
from joulewise.reduce import (
    _anchor_coverage_ok,
    _anchor_shift_envelope,
    _derive_anchor_context,
)
from joulewise.schemas import BenchmarkConfig, IdleBaseline, TelemetryBackend


ROOT = Path(__file__).resolve().parents[1]
EPOCH_S = 1_789_000_000.0


class AdmissionRoundingTests(unittest.TestCase):
    def _refusals(self, duration_s=30.0, capture_shift_s=0.0):
        start_s = EPOCH_S
        end_s = float(start_s + 30.00000001)
        observation = {
            "capture_skipped": False,
            "errors": {},
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "captured_at_s": end_s + 2.0,
        }
        admission = {
            "schema_version": environment_admission.ADMISSION_SCHEMA,
            "critical_environment_passed": True,
            "reference_provenance_present": True,
            "per_run_environment_evaluation": {
                "schema_version": environment_admission.EVALUATION_SCHEMA,
                "snapshot_sha256": "0" * 64,
                "eligible": True,
            },
            "decision": "admitted",
            "claim_reason": None,
            "attempts": [{
                "attempt": 1,
                "start_s": start_s,
                "end_s": end_s,
                "baseline": {"duration_s": duration_s},
                "admitted": True,
                "cpu_admission": {"admitted": True},
                "cpu_admission_enforced": True,
            }],
            "guard_observations": [
                dict(observation, phase=phase)
                for phase in ("before_attempt_1", "after_attempt_1")
            ],
        }
        metadata = {
            "environment_admission": admission,
            "environment": {"post_run_observation": observation},
        }
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "rich_telemetry_idle.jsonl").write_text(json.dumps({
                "timestamp_s": end_s + capture_shift_s,
                "elapsed_ns": 30_000_000_000,
            }) + "\n")
            # Isolate timing from policy authentication and raw thermal reconstruction;
            # admission structure, rich-record parsing, and containment run for real.
            with (
                patch.object(environment_admission,
                             "_recomputed_environment_evaluation_refusals", return_value=()),
                patch.object(environment_admission,
                             "_window_thermal_pressure_refusals", return_value=()),
            ):
                return environment_admission.current_environment_refusals(
                    metadata, bundle_path=bundle,
                    measured_window_start_s=end_s + 1.0,
                    measured_window_end_s=end_s + 2.0,
                )

    def test_r1_admits_interval_sum_rounded_out_of_epoch_duration(self):
        """A 10 ns native-sum excess disappears when the epoch end is stored."""
        duration_s = 30.00000001
        self.assertGreater(duration_s, float(EPOCH_S + duration_s) - EPOCH_S + 1e-9)
        self.assertEqual(self._refusals(duration_s=duration_s), ())

    def test_r1_admits_one_epoch_ulp_at_either_capture_endpoint(self):
        """Independent endpoint arithmetic can round either boundary outward."""
        for shift_s in (-math.ulp(EPOCH_S), math.ulp(EPOCH_S)):
            with self.subTest(shift_s=shift_s):
                self.assertEqual(self._refusals(capture_shift_s=shift_s), ())

    def test_r1_refuses_ten_microsecond_duration_excess(self):
        self.assertEqual(self._refusals(duration_s=30.00001),
                         ("environment_admission_missing",))

    def test_r1_refuses_capture_outside_attempt_by_one_sample(self):
        """The representation allowance cannot hide a 100 ms stage violation."""
        for shift_s in (-0.1, 0.1):
            with self.subTest(shift_s=shift_s):
                self.assertEqual(self._refusals(capture_shift_s=shift_s),
                                 ("environment_admission_missing",))


class AnchorCoverageRoundingTests(unittest.TestCase):
    def _contributions(self, edge, deficit_s):
        window = Window(EPOCH_S - 1.0, 1789000000.0001)
        bound_s = 0.009724
        start_s = math.fsum((window.start_s, -bound_s))
        end_s = math.fsum((window.end_s, bound_s))
        if edge == "left":
            start_s += deficit_s
        else:
            end_s -= deficit_s
        curve = [TracePoint(end_s, 10.0, start_s, end_s)]
        return [(curve, [window])], bound_s

class CooldownRoundingTests(unittest.TestCase):
    def _run(self, *, span_deficit_s=0.0, coverage_deficit_s=0.0,
             thermal_recovery_s=0.0, step_s=5.0):
        clock = FakeClock(EPOCH_S)
        config = BenchmarkConfig.from_mapping(json.loads(
            (ROOT / "configs/examples/mock_local.json").read_text()))
        reference = IdleBaseline(5.0, 0.0, 30.0, 30, TelemetryBackend.POWERMETRICS)

        class Telemetry:
            count = 0

            def measure_idle(self, config):
                self.count += 1
                # Only the sixth endpoint is moved, preserving the first capture start.
                step = step_s - span_deficit_s if self.count == 6 else step_s
                clock.sleep(step)
                return IdleBaseline(5.0, 0.0, 4.0 - coverage_deficit_s / 6.0,
                                    40, TelemetryBackend.POWERMETRICS)

            def thermal_state(self, config):
                return SimpleNamespace(thermal_pressure=(
                    "nominal" if clock.now() - EPOCH_S >= thermal_recovery_s else "serious"
                ))

        return cooldown_gate(Telemetry(), reference, config, clock)

    def test_r3_admits_thirty_second_span_rounded_inward_one_epoch_ulp(self):
        note = self._run(span_deficit_s=math.ulp(EPOCH_S))
        self.assertEqual(note["result"], "recovered")
        self.assertEqual(len(note["_trace"]), 6)
        self.assertEqual(note["window_span_s"], 29.99999976158142)
        self.assertTrue(note["span_complete"])

    def test_r3_admits_six_four_second_contributions_with_inward_epoch_rounding(self):
        """Six inward ULPs exceed 1 μs but fit the summed endpoint allowance."""
        note = self._run(coverage_deficit_s=6 * math.ulp(EPOCH_S))
        self.assertEqual(note["result"], "recovered")
        self.assertEqual(len(note["_trace"]), 6)
        self.assertGreater(24.0 - note["window_coverage_s"], 1e-6)
        self.assertEqual(note["window_coverage_s"], 24.0 - 6 * math.ulp(EPOCH_S))
        self.assertTrue(note["coverage_complete"])

    def test_r3_refuses_ten_microsecond_span_deficit(self):
        note = self._run(span_deficit_s=1e-5)
        sixth = note["_trace"][5]
        self.assertFalse(sixth["span_complete"])
        self.assertFalse(sixth["release"])

    def test_r3_refuses_ten_microsecond_coverage_deficit(self):
        note = self._run(coverage_deficit_s=1e-5)
        self.assertEqual(note["result"], "cap_hit")
        self.assertFalse(note["_trace"][5]["coverage_complete"])
        self.assertFalse(any(row["release"] for row in note["_trace"]))

    def test_r3_refuses_one_missing_sample_of_coverage(self):
        """Endpoint ULP accounting cannot credit a missing 100 ms sample."""
        note = self._run(coverage_deficit_s=0.1)
        self.assertEqual(note["result"], "cap_hit")
        self.assertFalse(any(row["release"] for row in note["_trace"]))

    def test_r3_refuses_first_recovery_at_or_after_three_hundred_second_cap(self):
        """Numerical completion never overrides the cap-first thermal conjunct."""
        for step_s in (5.0, 5.01):
            with self.subTest(step_s=step_s):
                note = self._run(thermal_recovery_s=300.0, step_s=step_s)
                self.assertEqual(note["result"], "cap_hit")
                self.assertGreaterEqual(note["waited_s"], 300.0)
                self.assertTrue(note["_trace"][-1]["release_criteria_met_late"])
                self.assertFalse(any(row["release"] for row in note["_trace"]))


class TransitionMidpointRoundingTests(unittest.TestCase):
    def _artifact(self):
        manifest = json.loads((ROOT / "configs/calibration/p2_046_load_transition/manifest.json").read_text())
        observations = json.loads((ROOT / "tests/fixtures/p2046/valid_observations.json").read_text())
        for index, row in enumerate(observations["transitions"]):
            marker_s = EPOCH_S + index * 10.0
            row["marker_epoch_s"] = marker_s
            rising = row["direction"] == "idle_to_load"
            row["samples"] = [
                {"interval_start_s": marker_s - 0.1, "interval_end_s": marker_s,
                 "mean_power_w": 1.0 if rising else 9.0},
                {"interval_start_s": marker_s + 0.1, "interval_end_s": marker_s + 0.2,
                 "mean_power_w": 9.0 if rising else 1.0},
                {"interval_start_s": marker_s + 0.2, "interval_end_s": marker_s + 0.3,
                 "mean_power_w": 9.0 if rising else 1.0},
            ]
        return build_alignment_artifact(manifest, observations)

    def test_r4_admits_eight_epoch_markers_using_endpoint_offset_midpoints(self):
        """Subtracting the marker before averaging avoids a spurious 119 ns error."""
        artifact = self._artifact()
        self.assertEqual(len(artifact["transitions"]), 8)
        self.assertEqual(validate_alignment_artifact(artifact), [])
        for summary in artifact["direction_summaries"]:
            rows = [row for row in artifact["transitions"] if row["direction"] == summary["direction"]]
            offsets = [(row["response_support_start_offset_s"] + row["response_support_end_offset_s"]) / 2
                       for row in rows]
            center = statistics.median(offsets)
            self.assertEqual(summary["center_offset_s"], center)
            for row, offset in zip(rows, offsets):
                self.assertEqual(row["offset_s"], offset)
                self.assertEqual(row["direction_center_offset_s"], center)
                self.assertEqual(row["residual_s"], offset - center)

    def test_r4_refuses_one_microsecond_offset_mutation_with_unchanged_support(self):
        artifact = self._artifact()
        original = copy.deepcopy(artifact["transitions"][0])
        row = artifact["transitions"][0]
        row["offset_s"] += 1e-6
        self.assertEqual(row["response_support_start_offset_s"], original["response_support_start_offset_s"])
        self.assertEqual(row["response_support_end_offset_s"], original["response_support_end_offset_s"])
        self.assertIn("transitions[0].offset_s does not equal support midpoint",
                      validate_alignment_artifact(artifact))


if __name__ == "__main__":
    unittest.main()
