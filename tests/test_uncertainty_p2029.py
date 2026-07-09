from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path
from typing import Any

from joulewise import reduce as reduce_module
from joulewise.aggregate import aggregate_experiment
from joulewise.bundle import RunBundleWriter
from joulewise.clock import FakeClock
from joulewise.interfaces import PowerSample, RuntimeEvent
from joulewise.schemas import BenchmarkConfig, RunStatus

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"

DEFAULT_IDLE = {
    "power_w_mean": 5.0,
    "power_w_stddev": 0.0,
    "duration_s": 1.0,
    "sample_count": 2,
    "telemetry_backend": "mock",
}


def load_config(run_id: str) -> BenchmarkConfig:
    data = json.loads(EXAMPLE_CONFIG.read_text())
    data["run_id"] = run_id
    return BenchmarkConfig.from_mapping(data)


def constant_samples(
    start_s: float, end_s: float, hz: float, power_w: float
) -> list[PowerSample]:
    samples: list[PowerSample] = []
    index = 0
    while True:
        t = start_s + index / hz
        if t > end_s + 1e-12:
            break
        samples.append(PowerSample(t, power_w, "mock", "mock"))
        index += 1
    return samples


class BundleBuilder:
    def __init__(self, runs_root: Path, run_id: str) -> None:
        self.writer = RunBundleWriter.create(
            runs_root, load_config(run_id), FakeClock(start=1_700_000_000.0)
        )

    @property
    def path(self) -> Path:
        return self.writer.path

    def add_event(
        self,
        event_type: str,
        phase: str,
        timestamp_s: float,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.writer.append_event(
            RuntimeEvent(
                timestamp_s=timestamp_s,
                event_type=event_type,
                phase=phase,
                message=f"{event_type} {phase}",
                metadata=metadata or {},
            )
        )

    def measured_window(self, start_s: float, end_s: float) -> None:
        self.add_event("stage_started", "measured_run", start_s)
        self.add_event("stage_completed", "measured_run", end_s)

    def phase_window(self, phase: str, start_s: float, end_s: float) -> None:
        self.add_event("phase_start", phase, start_s)
        self.add_event("phase_end", phase, end_s)

    def write_trace(self, samples: list[PowerSample]) -> None:
        self.writer.write_power_trace(samples)

    def write_metadata(
        self,
        *,
        idle: dict[str, Any] | None = DEFAULT_IDLE,
        clock_anchor_bound_s: float | None = 0.0,
        idle_drift_bound_w: float | None = None,
    ) -> None:
        metadata: dict[str, Any] = {
            "device": {"telemetry": "mock", "rail_manifest": ["mock"]},
            "adapters": {"telemetry": {"name": "mock"}},
        }
        if idle is not None:
            metadata["idle_baseline"] = idle
        if clock_anchor_bound_s is not None:
            metadata["clock_anchor_bound_s"] = clock_anchor_bound_s
        if idle_drift_bound_w is not None:
            metadata["idle_drift_bound_w"] = idle_drift_bound_w
        self.writer.write_metadata(metadata)


class ReducerUncertaintyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.counter = 0

    def builder(self) -> BundleBuilder:
        self.counter += 1
        return BundleBuilder(self.runs_root, f"p2029-{self.counter}")


class ReducerPropagationTests(ReducerUncertaintyTestCase):
    def test_single_bundle_is_not_estimable_but_keeps_point_and_quality(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 10.0)
        builder.write_trace(constant_samples(0.0, 10.0, hz=1.0, power_w=7.5))
        builder.write_metadata(idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertEqual(summary.energy_uncertainty_status, "not_estimable")
        self.assertAlmostEqual(summary.gross_energy_j or 0.0, 75.0, places=9)
        self.assertAlmostEqual(summary.energy_request_j or 0.0, 25.0, places=9)
        self.assertIsNotNone(summary.measurement_quality)
        self.assertIsNotNone(summary.energy_variance_terms_j2)
        self.assertIn("E_gross_repetition_j2", summary.energy_variance_terms_j2)

    def test_idle_mean_variance_term_uses_duration_squared(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 10.0)
        builder.write_trace(constant_samples(0.0, 10.0, hz=1.0, power_w=7.5))
        idle = {**DEFAULT_IDLE, "power_w_stddev": 2.0, "sample_count": 4}
        builder.write_metadata(idle=idle, idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNotNone(summary.energy_variance_terms_j2)
        self.assertAlmostEqual(
            summary.energy_variance_terms_j2["E_idle_mean_j2"], 100.0, places=12
        )

    def test_drift_bound_is_duration_times_recorded_power_bound(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 8.0)
        builder.write_trace(constant_samples(0.0, 8.0, hz=1.0, power_w=7.5))
        builder.write_metadata(idle_drift_bound_w=0.25)

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNotNone(summary.energy_bound_terms_j)
        self.assertAlmostEqual(
            summary.energy_bound_terms_j["E_drift_bound_j"], 2.0, places=12
        )
        self.assertNotIn(
            "E_drift_bound_j", summary.energy_variance_terms_j2 or {}
        )


class ClaimGateTests(ReducerUncertaintyTestCase):
    def test_under_resolved_phase_is_claim_ineligible_for_sample_count(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.phase_window("short", 0.0, 1.0)
        builder.write_trace(constant_samples(0.0, 4.0, hz=1.0, power_w=8.0))
        builder.write_metadata(idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        phase = (summary.claim_eligibility or {})["phase"]["short"]
        self.assertFalse(phase["eligible"])
        self.assertIn("insufficient_in_window_samples", phase["reasons"])

    def test_phase_cadence_ratio_two_passes_but_request_ratio_four_fails(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.phase_window("coarse", 0.0, 4.0)
        builder.write_trace(
            [
                PowerSample(0.0, 8.0, "mock", "mock"),
                PowerSample(2.0, 8.0, "mock", "mock"),
                PowerSample(4.0, 8.0, "mock", "mock"),
            ]
        )
        builder.write_metadata(idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        gates = summary.claim_eligibility or {}
        self.assertFalse(gates["request"]["eligible"])
        self.assertIn("cadence_ratio_below_threshold", gates["request"]["reasons"])
        self.assertTrue(gates["phase"]["coarse"]["eligible"])

    def test_phase_cadence_ratio_below_two_fails(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 5.0)
        builder.phase_window("coarser", 0.0, 3.0)
        builder.write_trace(
            [
                PowerSample(0.0, 8.0, "mock", "mock"),
                PowerSample(1.5, 8.0, "mock", "mock"),
                PowerSample(3.0, 8.0, "mock", "mock"),
                PowerSample(5.0, 8.0, "mock", "mock"),
            ]
        )
        builder.write_metadata(idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        phase = (summary.claim_eligibility or {})["phase"]["coarser"]
        self.assertFalse(phase["eligible"])
        self.assertIn("cadence_ratio_below_threshold", phase["reasons"])

    def test_clock_bound_exceeding_quarter_window_fails(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.phase_window("clocked", 0.0, 4.0)
        builder.write_trace(constant_samples(0.0, 4.0, hz=1.0, power_w=8.0))
        builder.write_metadata(clock_anchor_bound_s=1.1, idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        phase = (summary.claim_eligibility or {})["phase"]["clocked"]
        self.assertFalse(phase["eligible"])
        self.assertIn("clock_bound_exceeds_quarter_window", phase["reasons"])

    def test_missing_clock_bound_is_unknown_input_failure(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.phase_window("unknown_clock", 0.0, 4.0)
        builder.write_trace(constant_samples(0.0, 4.0, hz=1.0, power_w=8.0))
        builder.write_metadata(clock_anchor_bound_s=None, idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        phase = (summary.claim_eligibility or {})["phase"]["unknown_clock"]
        self.assertFalse(phase["eligible"])
        self.assertIn("clock_bound_unrecorded", phase["reasons"])

    def test_interpolation_edge_bound_is_recorded_for_phase_window(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.phase_window("interpolated", 1.0, 3.0)
        builder.write_trace(
            [
                PowerSample(0.0, 10.0, "mock", "mock"),
                PowerSample(2.0, 14.0, "mock", "mock"),
                PowerSample(4.0, 10.0, "mock", "mock"),
            ]
        )
        builder.write_metadata(idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        phase = (summary.claim_eligibility or {})["phase"]["interpolated"][
            "windows"
        ][0]
        self.assertAlmostEqual(phase["interpolation_edge_bound_j"], 4.0, places=12)

    def test_request_without_drift_evidence_is_ineligible(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.write_trace(constant_samples(0.0, 4.0, hz=2.0, power_w=8.0))
        builder.write_metadata()

        summary = reduce_module.reduce_bundle(builder.path)

        request = (summary.claim_eligibility or {})["request"]
        self.assertFalse(request["eligible"])
        self.assertIn("drift_term_unknown", request["reasons"])
        self.assertIsNone((summary.energy_bound_terms_j or {})["E_drift_bound_j"])


def _write_summary(runs_root: Path, member: str, summary: dict[str, Any]) -> None:
    bundle = runs_root / member
    bundle.mkdir(parents=True, exist_ok=True)
    bundle.joinpath("summary_metrics.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )


class AggregatorPropagationTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.runs_root.mkdir()

    def test_request_uncertainty_propagates_gross_and_idle_variance_terms(self) -> None:
        members = []
        for index, (gross, request, idle_var) in enumerate(
            [(10.0, 5.0, 1.0), (12.0, 7.0, 4.0), (14.0, 9.0, 9.0)],
            start=1,
        ):
            member = f"r{index}"
            members.append(member)
            _write_summary(
                self.runs_root,
                member,
                {
                    "status": "succeeded",
                    "energy_request_j": request,
                    "idle_subtracted_energy_j": request,
                    "gross_energy_j": gross,
                    "energy_variance_terms_j2": {"E_idle_mean_j2": idle_var},
                    "energy_bound_terms_j": {
                        "E_drift_bound_j": 0.5 * index,
                        "E_interpolation_edge_bound_j": 0.1 * index,
                    },
                },
            )

        aggregate = aggregate_experiment(self.runs_root, {"members": members})
        metric = aggregate["metrics"]["energy_request_j"]

        expected_gross_variance = 4.0
        expected_idle_variance = (1.0 + 4.0 + 9.0) / 3.0
        self.assertAlmostEqual(
            metric["energy_variance_terms_j2"]["E_gross_repetition_j2"],
            expected_gross_variance,
            places=12,
        )
        self.assertAlmostEqual(
            metric["energy_variance_terms_j2"]["E_idle_mean_j2"],
            expected_idle_variance,
            places=12,
        )
        self.assertAlmostEqual(
            metric["energy_variance_terms_j2"]["E_idle_sub_total_j2"],
            expected_gross_variance + expected_idle_variance,
            places=12,
        )
        self.assertEqual(metric["energy_uncertainty_status"], "estimated")
        self.assertEqual(metric["energy_bound_terms_j"]["E_drift_bound_j"], 1.5)
        self.assertTrue(
            math.isclose(
                metric["energy_bound_terms_j"]["E_interpolation_edge_bound_j"], 0.3
            )
        )


if __name__ == "__main__":
    unittest.main()
