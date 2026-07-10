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

    def item_window(
        self, item_id: str, item_index: int, start_s: float, end_s: float
    ) -> None:
        self.add_event(
            "item_start",
            "suite",
            start_s,
            metadata={"item_id": item_id, "item_index": item_index},
        )
        self.add_event(
            "item_end",
            "suite",
            end_s,
            metadata={
                "item_id": item_id,
                "item_index": item_index,
                "status": "succeeded",
            },
        )

    def write_trace(self, samples: list[PowerSample]) -> None:
        self.writer.write_power_trace(samples)

    def write_metadata(
        self,
        *,
        idle: dict[str, Any] | None = DEFAULT_IDLE,
        clock_anchor_bound_s: float | None = 0.0,
        idle_drift_bound_w: float | None = None,
        extra_idle_drift_bound_w: float | None = None,
        calibration_power_w_bound: float | None = None,
        drift_power_w_bound: float | None = None,
        idle_drift_power_w_abs_bound: float | None = None,
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
        if extra_idle_drift_bound_w is not None:
            metadata["extra"] = {"idle_drift_bound_w": extra_idle_drift_bound_w}
        if calibration_power_w_bound is not None:
            metadata["calibration"] = {"power_w_bound": calibration_power_w_bound}
        if drift_power_w_bound is not None:
            metadata["drift"] = {"power_w_bound": drift_power_w_bound}
        if idle_drift_power_w_abs_bound is not None:
            metadata["idle_drift"] = {
                "power_w_abs_bound": idle_drift_power_w_abs_bound
            }
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
        self.assertIsNone(
            summary.energy_variance_terms_j2["E_gross_repetition_j2"]
        )

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

    def test_drift_bound_accepts_only_documented_key_paths(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 8.0)
        builder.write_trace(constant_samples(0.0, 8.0, hz=1.0, power_w=7.5))
        builder.write_metadata(
            extra_idle_drift_bound_w=0.25, calibration_power_w_bound=99.0
        )

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNotNone(summary.energy_bound_terms_j)
        self.assertAlmostEqual(
            summary.energy_bound_terms_j["E_drift_bound_j"], 2.0, places=12
        )

    def test_drift_bound_rejects_alias_only_key_paths(self) -> None:
        alias_only_fixtures = [
            {"calibration_power_w_bound": 99.0},
            {"drift_power_w_bound": 99.0},
            {"idle_drift_power_w_abs_bound": 99.0},
        ]
        for fixture in alias_only_fixtures:
            with self.subTest(fixture=fixture):
                builder = self.builder()
                builder.measured_window(0.0, 4.0)
                builder.write_trace(
                    constant_samples(0.0, 4.0, hz=2.0, power_w=8.0)
                )
                builder.write_metadata(**fixture)

                summary = reduce_module.reduce_bundle(builder.path)

                gates = summary.claim_eligibility or {}
                self.assertIsNone(
                    (summary.energy_bound_terms_j or {})["E_drift_bound_j"]
                )
                self.assertFalse(gates["request"]["eligible"])
                self.assertEqual(gates["request"]["reasons"], ["drift_term_unknown"])
                self.assertFalse(gates["idle_subtracted_request"]["eligible"])
                self.assertEqual(
                    gates["idle_subtracted_request"]["reasons"],
                    ["drift_term_unknown"],
                )
                # Unsupported drift aliases do not affect the gross gate.
                self.assertTrue(gates["gross_request"]["eligible"])


class ReducerJointEdgeBoundTests(ReducerUncertaintyTestCase):
    def test_joint_edge_bound_moves_both_edges(self) -> None:
        # P2-040 FIX-3 mutation test: constant 8 W, one-second gaps, window
        # [2.5, 6.5]. Joint +/- half-gap shifts change energy by 8 J; the
        # legacy one-edge sensitivity stays 4 J.
        builder = self.builder()
        builder.measured_window(2.5, 6.5)
        builder.write_trace(constant_samples(0.0, 9.0, hz=1.0, power_w=8.0))
        builder.write_metadata(idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        bounds = summary.energy_bound_terms_j or {}
        self.assertAlmostEqual(bounds["E_interpolation_edge_bound_j"], 4.0, places=12)
        self.assertAlmostEqual(
            bounds["E_interpolation_joint_edge_bound_j"], 8.0, places=12
        )


class ClaimGateTests(ReducerUncertaintyTestCase):
    def test_zero_duration_phase_has_nonpositive_window_reason(self) -> None:
        # P2-040 FIX-1: a zero-duration subwindow inside a valid positive
        # measured window carries the D-057 additive reason and is never
        # eligible.
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.phase_window("instant", 2.0, 2.0)
        builder.write_trace(constant_samples(0.0, 4.0, hz=2.0, power_w=8.0))
        builder.write_metadata(idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        phase = (summary.claim_eligibility or {})["phase"]["instant"]
        self.assertFalse(phase["eligible"])
        self.assertIn("nonpositive_window_duration", phase["reasons"])
        window_entry = phase["windows"][0]
        self.assertFalse(window_entry["eligible"])
        self.assertIn("nonpositive_window_duration", window_entry["reasons"])

    def test_gross_request_without_idle_model_passes_while_idle_subtracted_fails(self) -> None:
        # P2-040 FIX-2 mutation test: valid cadence/clock, a recorded drift
        # bound, but no idle baseline.
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.write_trace(constant_samples(0.0, 4.0, hz=1.0, power_w=8.0))
        builder.write_metadata(idle=None, idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        gates = summary.claim_eligibility or {}
        self.assertTrue(gates["gross_request"]["eligible"])
        self.assertEqual(gates["gross_request"]["reasons"], [])
        self.assertEqual(gates["gross_request"]["metric_name"], "gross_energy_j")
        self.assertEqual(gates["gross_request"]["window_class"], "gross_request")
        self.assertFalse(gates["idle_subtracted_request"]["eligible"])
        self.assertEqual(
            gates["idle_subtracted_request"]["reasons"],
            ["idle_baseline_unrecorded"],
        )
        self.assertEqual(
            gates["idle_subtracted_request"]["metric_name"],
            "idle_subtracted_energy_j",
        )

    def test_request_window_at_cadence_and_clock_boundaries_is_eligible(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.write_trace(constant_samples(0.0, 4.0, hz=1.0, power_w=8.0))
        builder.write_metadata(clock_anchor_bound_s=1.0, idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        # Deprecated alias plus both P2-040 metric-specific entries.
        for key in ("gross_request", "idle_subtracted_request"):
            entry = (summary.claim_eligibility or {})[key]
            self.assertTrue(entry["eligible"], key)
            self.assertEqual(entry["reasons"], [], key)
        request = (summary.claim_eligibility or {})["request"]
        self.assertTrue(request["eligible"])
        self.assertEqual(request["reasons"], [])
        self.assertEqual(request["cadence_ratio"], 4.0)
        self.assertEqual(request["cadence_ratio_min"], 4.0)
        self.assertNotIn(
            "clock_bound_exceeds_quarter_window", request["reasons"]
        )

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
        self.assertAlmostEqual(phase["interpolation_edge_bound_j"], 13.0, places=12)
        # P2-040 FIX-3 hand computation: gaps at both edges are 2.0 s, so the
        # joint inward candidate is the zero-duration window [2,2] (allowed at
        # equality): |0 - 26| = 26 J dominates.
        self.assertAlmostEqual(
            phase["interpolation_joint_edge_bound_j"], 26.0, places=12
        )

    def test_interpolation_edge_bound_uses_edge_perturbation_recipe(self) -> None:
        builder = self.builder()
        builder.measured_window(2.5, 6.5)
        builder.write_trace(constant_samples(0.0, 9.0, hz=1.0, power_w=8.0))
        builder.write_metadata(idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNotNone(summary.energy_bound_terms_j)
        # Legacy one-edge sensitivity is retained unchanged...
        self.assertAlmostEqual(
            summary.energy_bound_terms_j["E_interpolation_edge_bound_j"],
            4.0,
            places=12,
        )
        # ...while the governed P2-040 FIX-3 joint bound shifts both edges
        # simultaneously (joint inward/outward changes energy by 8 J).
        self.assertAlmostEqual(
            summary.energy_bound_terms_j["E_interpolation_joint_edge_bound_j"],
            8.0,
            places=12,
        )
        # The new metric-specific prechecks expose and consume the joint field.
        for key in ("gross_request", "idle_subtracted_request"):
            entry = (summary.claim_eligibility or {})[key]
            self.assertAlmostEqual(
                entry["interpolation_joint_edge_bound_j"], 8.0, places=12, msg=key
            )
            self.assertNotIn("interpolation_bound_unrecorded", entry["reasons"])
        request = (summary.claim_eligibility or {})["request"]
        self.assertNotIn("interpolation_joint_edge_bound_j", request)
        self.assertAlmostEqual(request["interpolation_edge_bound_j"], 4.0, places=12)

    def test_deprecated_request_uses_one_edge_when_joint_bound_is_unrecorded(self) -> None:
        curve = [
            reduce_module.TracePoint(0.0, 10.0),
            reduce_module.TracePoint(1.0, 10.0),
            reduce_module.TracePoint(1.1, 10.0),
            reduce_module.TracePoint(3.0, 10.0),
        ]
        window = reduce_module.Window(0.75, 1.25)
        terms = {
            "E_interpolation_edge_bound_j": 10.0,
            "E_interpolation_joint_edge_bound_j": None,
            "E_drift_bound_j": 1.0,
        }
        legacy = reduce_module._window_claim_eligibility(
            curve,
            {"clock_anchor_bound_s": 0.0},
            window,
            cadence_ratio_min=0.0,
            require_sample_count=False,
            require_drift=True,
            bound_terms_j=terms,
            legacy_interpolation_edge=True,
        )
        current = reduce_module._window_claim_eligibility(
            curve,
            {"clock_anchor_bound_s": 0.0},
            window,
            cadence_ratio_min=0.0,
            require_sample_count=False,
            require_drift=True,
            bound_terms_j=terms,
        )
        self.assertTrue(legacy["eligible"])
        self.assertNotIn("interpolation_joint_edge_bound_j", legacy)
        self.assertFalse(current["eligible"])
        self.assertIn("interpolation_bound_unrecorded", current["reasons"])

    def test_asymmetric_joint_edge_fixture_recomputes_thirty_joules(self) -> None:
        builder = self.builder()
        builder.measured_window(2.0, 8.0)
        builder.write_trace(
            [PowerSample(t, 10.0, "mock", "mock") for t in (0.0, 2.0, 4.0, 8.0, 12.0)]
        )
        builder.write_metadata(idle_drift_bound_w=0.1)
        terms = reduce_module.reduce_bundle(builder.path).energy_bound_terms_j or {}
        self.assertEqual(terms["E_interpolation_edge_bound_j"], 20.0)
        self.assertEqual(terms["E_interpolation_joint_edge_bound_j"], 30.0)

    def test_negative_measured_window_is_structured_reducer_failure(self) -> None:
        builder = self.builder()
        builder.measured_window(2.0, 1.0)
        builder.write_trace(constant_samples(0.0, 3.0, hz=2.0, power_w=8.0))
        builder.write_metadata()
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertTrue(
            (summary.failure_message or "").startswith(
                "measured_run window duration must be > 0 s; got "
            )
        )

    def test_request_without_drift_evidence_is_ineligible(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.write_trace(constant_samples(0.0, 4.0, hz=2.0, power_w=8.0))
        builder.write_metadata()

        summary = reduce_module.reduce_bundle(builder.path)

        gates = summary.claim_eligibility or {}
        self.assertFalse(gates["request"]["eligible"])
        self.assertEqual(gates["request"]["reasons"], ["drift_term_unknown"])
        self.assertFalse(gates["idle_subtracted_request"]["eligible"])
        self.assertEqual(
            gates["idle_subtracted_request"]["reasons"], ["drift_term_unknown"]
        )
        # Gross request energy needs no idle-drift evidence (P2-040 FIX-2).
        self.assertTrue(gates["gross_request"]["eligible"])
        self.assertEqual(gates["gross_request"]["reasons"], [])
        self.assertIsNone((summary.energy_bound_terms_j or {})["E_drift_bound_j"])

    def test_missing_bracketing_gap_records_no_cadence_ratio(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.write_trace(constant_samples(1.0, 4.0, hz=1.0, power_w=8.0))
        builder.write_metadata(idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        request = (summary.claim_eligibility or {})["request"]
        self.assertIsNone(request["observed_bracketing_max_sample_gap_s"])
        self.assertIsNone(request["cadence_ratio"])
        self.assertIn("cadence_ratio_unrecorded", request["reasons"])

    def test_item_claim_gate_uses_short_window_threshold_and_sample_count(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 4.0)
        builder.item_window("item_ok", 0, 0.0, 2.0)
        builder.item_window("item_short", 1, 2.0, 3.0)
        builder.write_trace(constant_samples(0.0, 4.0, hz=1.0, power_w=8.0))
        builder.write_metadata(idle_drift_bound_w=0.1)

        summary = reduce_module.reduce_bundle(builder.path)

        item_gates = (summary.claim_eligibility or {})["item"]
        eligible = item_gates["0:item_ok"]
        self.assertTrue(eligible["eligible"])
        self.assertEqual(eligible["reasons"], [])
        self.assertEqual(eligible["cadence_ratio"], 2.0)
        self.assertEqual(eligible["cadence_ratio_min"], 2.0)
        short = item_gates["1:item_short"]
        self.assertFalse(short["eligible"])
        self.assertIn("insufficient_in_window_samples", short["reasons"])


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
            [(10.0, 5.0, 1.0), (13.0, 7.0, 4.0), (14.0, 9.0, 9.0)],
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
                        "E_interpolation_joint_edge_bound_j": 0.2 * index,
                    },
                },
            )

        aggregate = aggregate_experiment(self.runs_root, {"members": members})
        metric = aggregate["metrics"]["energy_request_j"]

        expected_gross_variance = 13.0 / 3.0
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
        self.assertTrue(
            math.isclose(
                metric["energy_bound_terms_j"][
                    "E_interpolation_joint_edge_bound_j"
                ],
                0.6,
            )
        )

    def test_joint_edge_bound_is_null_when_any_member_lacks_it(self) -> None:
        members = []
        for index in range(1, 3):
            member = f"r{index}"
            members.append(member)
            bound_terms: dict[str, Any] = {
                "E_drift_bound_j": 0.5,
                "E_interpolation_edge_bound_j": 0.1,
            }
            if index == 1:
                bound_terms["E_interpolation_joint_edge_bound_j"] = 0.2
            _write_summary(
                self.runs_root,
                member,
                {
                    "status": "succeeded",
                    "energy_request_j": float(index),
                    "idle_subtracted_energy_j": float(index),
                    "gross_energy_j": float(index + 10),
                    "energy_variance_terms_j2": {"E_idle_mean_j2": 1.0},
                    "energy_bound_terms_j": bound_terms,
                },
            )

        aggregate = aggregate_experiment(self.runs_root, {"members": members})
        metric = aggregate["metrics"]["energy_request_j"]

        # All-members-known rule: one member without the joint bound nulls it,
        # while the fully known legacy bound still propagates.
        self.assertIsNone(
            metric["energy_bound_terms_j"]["E_interpolation_joint_edge_bound_j"]
        )
        self.assertTrue(
            math.isclose(
                metric["energy_bound_terms_j"]["E_interpolation_edge_bound_j"], 0.1
            )
        )

    def test_joint_edge_bound_uses_max_when_all_members_present(self) -> None:
        members = []
        for index, bound in enumerate((0.2, 0.7), start=1):
            member = f"joint-r{index}"
            members.append(member)
            _write_summary(
                self.runs_root,
                member,
                {
                    "status": "succeeded",
                    "energy_request_j": float(index),
                    "idle_subtracted_energy_j": float(index),
                    "gross_energy_j": float(index + 10),
                    "energy_variance_terms_j2": {"E_idle_mean_j2": 1.0},
                    "energy_bound_terms_j": {
                        "E_drift_bound_j": 0.1,
                        "E_interpolation_edge_bound_j": 0.1,
                        "E_interpolation_joint_edge_bound_j": bound,
                    },
                },
            )
        aggregate = aggregate_experiment(self.runs_root, {"members": members})
        self.assertEqual(
            aggregate["metrics"]["energy_request_j"]["energy_bound_terms_j"]
            ["E_interpolation_joint_edge_bound_j"],
            0.7,
        )

    def test_request_uncertainty_is_not_estimable_without_all_idle_terms(self) -> None:
        members = []
        for index in range(1, 3):
            member = f"r{index}"
            members.append(member)
            summary: dict[str, Any] = {
                "status": "succeeded",
                "energy_request_j": float(index),
                "idle_subtracted_energy_j": float(index),
                "gross_energy_j": float(index + 10),
                "energy_bound_terms_j": {
                    "E_drift_bound_j": 0.5,
                    "E_interpolation_edge_bound_j": 0.1,
                },
            }
            if index == 1:
                summary["energy_variance_terms_j2"] = {"E_idle_mean_j2": 1.0}
            _write_summary(self.runs_root, member, summary)

        aggregate = aggregate_experiment(self.runs_root, {"members": members})
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["energy_uncertainty_status"], "not_estimable")
        self.assertIsNone(metric["energy_variance_terms_j2"]["E_idle_mean_j2"])
        self.assertIsNone(metric["energy_variance_terms_j2"]["E_idle_sub_total_j2"])

    def test_gross_repetition_variance_requires_all_point_members(self) -> None:
        members = []
        for index in range(1, 4):
            member = f"r{index}"
            members.append(member)
            summary: dict[str, Any] = {
                "status": "succeeded",
                "energy_request_j": float(index),
                "idle_subtracted_energy_j": float(index),
                "energy_variance_terms_j2": {"E_idle_mean_j2": 1.0},
                "energy_bound_terms_j": {
                    "E_drift_bound_j": 0.5,
                    "E_interpolation_edge_bound_j": 0.1,
                },
            }
            if index != 3:
                summary["gross_energy_j"] = float(index + 10)
            _write_summary(self.runs_root, member, summary)

        aggregate = aggregate_experiment(self.runs_root, {"members": members})
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["energy_uncertainty_status"], "not_estimable")
        self.assertIsNone(metric["energy_variance_terms_j2"]["E_gross_repetition_j2"])
        self.assertIsNone(metric["energy_variance_terms_j2"]["E_idle_sub_total_j2"])

    def test_gross_repetition_variance_overflow_degrades_to_not_estimable(self) -> None:
        members = []
        for index, gross in enumerate((-1e308, 1e308), start=1):
            member = f"r{index}"
            members.append(member)
            _write_summary(
                self.runs_root,
                member,
                {
                    "status": "succeeded",
                    "energy_request_j": float(index),
                    "idle_subtracted_energy_j": float(index),
                    "gross_energy_j": gross,
                    "energy_variance_terms_j2": {"E_idle_mean_j2": 1.0},
                    "energy_bound_terms_j": {
                        "E_drift_bound_j": 0.5,
                        "E_interpolation_edge_bound_j": 0.1,
                    },
                },
            )

        aggregate = aggregate_experiment(self.runs_root, {"members": members})
        metric = aggregate["metrics"]["energy_request_j"]

        self.assertEqual(metric["energy_uncertainty_status"], "not_estimable")
        self.assertIsNone(metric["energy_variance_terms_j2"]["E_gross_repetition_j2"])
        self.assertIsNone(metric["energy_variance_terms_j2"]["E_idle_sub_total_j2"])


if __name__ == "__main__":
    unittest.main()
