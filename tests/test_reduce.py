"""Tests for the reducer (Slice 2D; D-002, D-018, D-019).

Bundles are assembled with the real :class:`RunBundleWriter` plus hand-authored
events and traces under a :class:`FakeClock`, so every expected energy is a
closed form computed by hand and asserted to 9 decimal places. The reducer is a
pure function over the on-disk artifacts, so the synthetic bundles are not
finalized - the reducer reads a not-yet-finalized directory exactly as the
controller invokes it before ``finalize()``.
"""

from __future__ import annotations

import importlib.util
import json
import math
import plistlib
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from joulewise import reduce as reduce_module
from joulewise.adapters.powermetrics import duration_weighted_mean_and_sample_variance
from joulewise.bundle import RunBundleWriter
from joulewise.clock import FakeClock
from joulewise.cli import validate_bundle
from joulewise.controller import run_benchmark
from joulewise.idle_dependence import estimate_newey_west_bartlett
from joulewise.interfaces import PowerSample, RuntimeEvent
from joulewise.schemas import (
    BenchmarkConfig,
    EnergyEvidence,
    FailureReason,
    RunStatus,
    TelemetryBackend,
)
from joulewise.suite import suite_manifest_sha256

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"
SUITE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_suite_local.json"
SUITE_MANIFEST_PATH = REPO_ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json"

#: Idle-baseline metadata block the controller writes (asdict of IdleBaseline).
DEFAULT_IDLE = {
    "power_w_mean": 5.0,
    "power_w_stddev": 0.0,
    "duration_s": 1.0,
    "sample_count": 2,
    "telemetry_backend": "mock",
}


def load_config(**overrides) -> BenchmarkConfig:
    data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
    for key, value in overrides.items():
        data[key] = value
    return BenchmarkConfig.from_mapping(data)


def load_suite_config(run_id: str) -> BenchmarkConfig:
    data = json.loads(SUITE_CONFIG_PATH.read_text())
    manifest = json.loads(SUITE_MANIFEST_PATH.read_text())
    data["run_id"] = run_id
    data["workload_profile"]["suite_manifest_ref"] = str(SUITE_MANIFEST_PATH)
    data["workload_profile"]["suite_manifest_sha256"] = suite_manifest_sha256(manifest)
    return BenchmarkConfig.from_mapping(data)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records))


def powermetrics_stream(powers_w: list[float], intervals_s: list[float]) -> bytes:
    documents = []
    for power_w, interval_s in zip(powers_w, intervals_s, strict=True):
        documents.append(
            {
                "timestamp": datetime(2026, 7, 14, tzinfo=timezone.utc),
                "elapsed_ns": int(interval_s * 1_000_000_000),
                "processor": {
                    "cpu_power": power_w * 1000.0,
                    "gpu_power": 0.0,
                    "ane_power": 0.0,
                    "cpu_energy": power_w * interval_s * 1000.0,
                    "gpu_energy": 0.0,
                    "ane_energy": 0.0,
                },
            }
        )
    return b"\0".join(plistlib.dumps(document) for document in documents)


class BundleBuilder:
    """Assemble a synthetic bundle directory for the reducer to read."""

    def __init__(self, runs_root: Path, config: BenchmarkConfig, clock: FakeClock) -> None:
        self._writer = RunBundleWriter.create(runs_root, config, clock)

    @property
    def path(self) -> Path:
        return self._writer.path

    def add_event(
        self,
        event_type: str,
        phase: str,
        timestamp_s: float,
        *,
        message: str = "",
        metadata: dict | None = None,
    ) -> None:
        self._writer.append_event(
            RuntimeEvent(
                timestamp_s=timestamp_s,
                event_type=event_type,
                phase=phase,
                message=message or f"{event_type} {phase}",
                metadata=metadata or {},
            )
        )

    def measured_window(self, start_s: float, end_s: float) -> None:
        self.add_event("stage_started", "measured_run", start_s)
        self.add_event("stage_completed", "measured_run", end_s)

    def add_token(
        self,
        index: int,
        timestamp_s: float,
        *,
        metadata: dict | None = None,
    ) -> None:
        self.add_event(
            "token", "decode", timestamp_s, message=f"token {index}",
            metadata={"index": index, **(metadata or {})},
        )

    def add_phase(
        self,
        phase: str,
        start_s: float,
        end_s: float,
        *,
        metadata: dict | None = None,
    ) -> None:
        self.add_event("phase_start", phase, start_s, metadata=metadata)
        self.add_event("phase_end", phase, end_s, metadata=metadata)

    def write_trace(self, samples: list[PowerSample]) -> None:
        self._writer.write_power_trace(samples)

    def write_metadata(
        self,
        *,
        rail_manifest: list[str],
        idle: dict | None = DEFAULT_IDLE,
        thermal_pre_c: float | None = None,
        thermal_post_c: float | None = None,
        workload_observed: dict | None = None,
    ) -> Path:
        extra: dict = {
            "device": {"telemetry": "mock", "rail_manifest": rail_manifest},
            "adapters": {"telemetry": {"name": "mock"}},
        }
        if idle is not None:
            extra["idle_baseline"] = idle
        if thermal_pre_c is not None:
            extra["thermal_pre"] = {"timestamp_s": 0.0, "temperature_c": thermal_pre_c}
        if thermal_post_c is not None:
            extra["thermal_post"] = {"timestamp_s": 0.0, "temperature_c": thermal_post_c}
        if workload_observed is not None:
            extra["workload_observed"] = workload_observed
        self._writer.write_metadata(extra)
        return self.path


def constant_samples(
    start_s: float, end_s: float, hz: float, power_w: float, rail: str = "mock"
) -> list[PowerSample]:
    """Samples at ``hz`` from ``start_s`` to ``end_s`` inclusive, constant power."""
    samples: list[PowerSample] = []
    k = 0
    while True:
        t = start_s + k / hz
        if t > end_s + 1e-12:
            break
        samples.append(PowerSample(timestamp_s=t, power_w=power_w, source="mock", rail=rail))
        k += 1
    return samples


class ReduceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self._counter = 0

    def builder(self, run_id: str | None = None, **config_overrides) -> BundleBuilder:
        self._counter += 1
        rid = run_id or f"reduce-test-{self._counter}"
        config = load_config(run_id=rid, **config_overrides)
        return BundleBuilder(self.runs_root, config, FakeClock(start=1_700_000_000.0))


class RectangleTests(ReduceTestCase):
    def test_constant_power_exact_energy(self) -> None:
        # Constant 7.5 W over a 10 s window, idle 5.0 W.
        builder = self.builder()
        start_s, end_s = 100.0, 110.0
        builder.measured_window(start_s, end_s)
        builder.write_trace(constant_samples(start_s, end_s, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"])
        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNone(summary.failure_reason)
        self.assertAlmostEqual(summary.gross_energy_j, 75.0, places=9)
        self.assertAlmostEqual(summary.idle_subtracted_energy_j, 25.0, places=9)
        self.assertAlmostEqual(summary.energy_request_j, 25.0, places=9)
        self.assertIsNotNone(summary.idle_baseline)
        self.assertEqual(summary.idle_baseline.telemetry_backend, TelemetryBackend.MOCK)

    def test_idle_baseline_sample_count_rejects_non_integer_values(self) -> None:
        cases = [1.9, "3"]
        for value in cases:
            with self.subTest(value=value):
                builder = self.builder()
                start_s, end_s = 100.0, 110.0
                builder.measured_window(start_s, end_s)
                builder.write_trace(constant_samples(start_s, end_s, hz=1.0, power_w=7.5))
                idle = {**DEFAULT_IDLE, "sample_count": value}
                builder.write_metadata(rail_manifest=["mock"], idle=idle)

                summary = reduce_module.reduce_bundle(builder.path)

                self.assertEqual(summary.status, RunStatus.FAILED)
                self.assertIn("idle_baseline.sample_count must be an integer", summary.failure_message)


class IdleDependencePropagationTests(ReduceTestCase):
    def test_reducer_uses_governed_variance_for_corrected_energy_term(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 3.0)
        builder.write_trace(constant_samples(0.0, 3.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"])
        governed = {
            "status": "estimated",
            "governed_variance_of_mean_w2": 5 / 18,
        }

        with patch(
            "joulewise.reduce.derive_idle_mean_uncertainty",
            return_value=governed,
        ):
            summary = reduce_module.reduce_bundle(builder.path)

        self.assertIs(summary.idle_mean_uncertainty, governed)
        self.assertEqual(
            summary.energy_variance_terms_j2["E_idle_mean_j2"], 5 / 2
        )


class RampTests(ReduceTestCase):
    def test_linear_ramp_exact_trapezoid(self) -> None:
        # Power ramps 0 -> 10 W across a 10 s window; integral of a triangle is
        # 0.5 * base * height = 0.5 * 10 * 10 = 50.0 J exactly.
        builder = self.builder()
        start_s, end_s = 0.0, 10.0
        samples = [
            PowerSample(timestamp_s=float(t), power_w=float(t), source="mock", rail="mock")
            for t in range(11)
        ]
        builder.measured_window(start_s, end_s)
        builder.write_trace(samples)
        builder.write_metadata(rail_manifest=["mock"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertAlmostEqual(summary.gross_energy_j, 50.0, places=9)

    def test_window_starts_and_ends_between_samples(self) -> None:
        # Samples at integer seconds 0..10 with power == t (ramp 0 -> 10 W).
        # Window [2.5, 7.5] starts/ends between samples. Interpolated power at
        # the edges equals t (2.5 and 7.5). Energy = integral of t dt over
        # [2.5, 7.5] = (7.5^2 - 2.5^2)/2 = (56.25 - 6.25)/2 = 25.0 J.
        builder = self.builder()
        samples = [
            PowerSample(timestamp_s=float(t), power_w=float(t), source="mock", rail="mock")
            for t in range(11)
        ]
        builder.measured_window(2.5, 7.5)
        builder.write_trace(samples)
        builder.write_metadata(rail_manifest=["mock"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertAlmostEqual(summary.gross_energy_j, 25.0, places=9)

    def test_window_edge_outside_sample_span_is_clamped(self) -> None:
        # Samples cover [2, 8] with power == t. Window [0, 10] extends past the
        # span on both ends; the curve is held flat at the nearest sample:
        #   [0, 2]:  flat 2 W            -> 2 * 2  = 4
        #   [2, 8]:  ramp 2 -> 8 W       -> (8^2-2^2)/2 = 30
        #   [8, 10]: flat 8 W            -> 8 * 2  = 16
        # total = 50.0 J exactly.
        builder = self.builder()
        samples = [
            PowerSample(timestamp_s=float(t), power_w=float(t), source="mock", rail="mock")
            for t in range(2, 9)
        ]
        builder.measured_window(0.0, 10.0)
        builder.write_trace(samples)
        builder.write_metadata(rail_manifest=["mock"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertAlmostEqual(summary.gross_energy_j, 50.0, places=9)


class GappedTraceTests(ReduceTestCase):
    def test_dropped_samples_and_observed_hz(self) -> None:
        # Nominal 1 Hz; timestamps with a single 3 s gap between 3 and 6.
        # Gaps: 1,1,1,3,1,1 -> exactly one gap > 2x nominal (2 s) => 1 dropped.
        # Median of {1,1,1,3,1,1} is 1.0 -> observed_sampling_hz == 1.0.
        builder = self.builder()
        times = [0.0, 1.0, 2.0, 3.0, 6.0, 7.0, 8.0]
        samples = [
            PowerSample(timestamp_s=t, power_w=10.0, source="mock", rail="mock")
            for t in times
        ]
        builder.measured_window(0.0, 8.0)
        builder.write_trace(samples)
        builder.write_metadata(rail_manifest=["mock"])
        summary = reduce_module.reduce_bundle(builder.path)
        quality = summary.measurement_quality
        self.assertEqual(quality.dropped_samples, 1)
        self.assertAlmostEqual(quality.observed_sampling_hz, 1.0, places=9)
        self.assertEqual(quality.requested_sampling_hz, 2.0)

    def test_idle_window_suspect_is_copied_from_idle_baseline_metadata(self) -> None:
        builder = self.builder()
        idle = {
            **DEFAULT_IDLE,
            "gpu_idle_ratio_mean": 0.4,
            "gpu_idle_ratio_min": 0.0,
            "gpu_freq_mhz_mean": 1363.0,
            "gpu_freq_hz_mean": 1363.0,
            "idle_window_suspect": True,
        }
        builder.measured_window(0.0, 2.0)
        builder.write_trace(constant_samples(0.0, 2.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"], idle=idle)
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertIs(summary.idle_baseline.idle_window_suspect, True)
        self.assertEqual(summary.idle_baseline.gpu_freq_mhz_mean, 1363.0)
        self.assertEqual(summary.idle_baseline.gpu_freq_hz_mean, 1363.0)
        self.assertIs(summary.measurement_quality.idle_window_suspect, True)

    def test_legacy_false_hz_metadata_populates_additive_mhz_field(self) -> None:
        builder = self.builder()
        idle = {**DEFAULT_IDLE, "gpu_freq_hz_mean": 325.9148}
        builder.measured_window(0.0, 2.0)
        builder.write_trace(constant_samples(0.0, 2.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"], idle=idle)

        serialized = reduce_module.reduce_bundle(builder.path).to_dict()["idle_baseline"]

        self.assertEqual(serialized["gpu_freq_mhz_mean"], 325.9148)
        self.assertEqual(serialized["gpu_freq_hz_mean"], 325.9148)

    def test_old_idle_baseline_metadata_lacks_idle_window_suspect(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 2.0)
        builder.write_trace(constant_samples(0.0, 2.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"], idle=DEFAULT_IDLE)
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertIsNone(summary.idle_baseline.idle_window_suspect)
        self.assertIsNone(summary.measurement_quality.idle_window_suspect)


class RailSplitTests(ReduceTestCase):
    def test_two_manifest_rails_sum_and_third_ignored(self) -> None:
        # Rails "a" (3 W) and "b" (4 W) are in the manifest; "c" (99 W) is not.
        # Summed curve is a constant 7 W; over a 10 s window energy = 70 J.
        builder = self.builder()
        start_s, end_s = 0.0, 10.0
        samples: list[PowerSample] = []
        t = start_s
        while t <= end_s + 1e-12:
            samples.append(PowerSample(timestamp_s=t, power_w=3.0, source="mock", rail="a"))
            samples.append(PowerSample(timestamp_s=t, power_w=4.0, source="mock", rail="b"))
            samples.append(PowerSample(timestamp_s=t, power_w=99.0, source="mock", rail="c"))
            t += 1.0
        builder.measured_window(start_s, end_s)
        builder.write_trace(samples)
        builder.write_metadata(rail_manifest=["a", "b"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertAlmostEqual(summary.gross_energy_j, 70.0, places=9)


class PhaseAttributionTests(ReduceTestCase):
    def test_known_phase_windows_and_zero_length_phase(self) -> None:
        # Constant 7.5 W over [0, 10]. tokenize = [0, 1] -> 7.5 J; prefill =
        # [1, 2] -> 7.5 J; decode = [2, 8] -> 45 J; a zero-length serialize
        # phase at t=8 -> 0.0 J.
        builder = self.builder()
        start_s, end_s = 0.0, 10.0
        builder.measured_window(start_s, end_s)
        builder.add_phase("tokenize", 0.0, 1.0)
        builder.add_phase("prefill", 1.0, 2.0)
        builder.add_phase("decode", 2.0, 8.0)
        builder.add_phase("serialize", 8.0, 8.0)
        builder.write_trace(constant_samples(start_s, end_s, hz=2.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertIsNotNone(summary.phase_energy_j)
        self.assertAlmostEqual(summary.phase_energy_j["tokenize"], 7.5, places=9)
        self.assertAlmostEqual(summary.phase_energy_j["prefill"], 7.5, places=9)
        self.assertAlmostEqual(summary.phase_energy_j["decode"], 45.0, places=9)
        self.assertAlmostEqual(summary.phase_energy_j["serialize"], 0.0, places=9)
        self.assertEqual(
            summary.measurement_quality.phase_identifiability,
            {
                "tokenize": "identifiable",
                "prefill": "identifiable",
                "decode": "identifiable",
                "serialize": "identifiable",
            },
        )

    def test_repeated_phase_name_sums(self) -> None:
        # Two decode intervals [1,3] and [5,7] over a constant 2 W curve sum:
        # 2 W * 2 s + 2 W * 2 s = 8.0 J.
        builder = self.builder()
        builder.measured_window(0.0, 10.0)
        builder.add_phase("decode", 1.0, 3.0)
        builder.add_phase("decode", 5.0, 7.0)
        builder.write_trace(constant_samples(0.0, 10.0, hz=1.0, power_w=2.0))
        builder.write_metadata(rail_manifest=["mock"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertAlmostEqual(summary.phase_energy_j["decode"], 8.0, places=9)

    def test_phase_identifiability_requires_three_samples_per_nonzero_interval(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 10.0)
        builder.add_phase("prefill", 0.0, 0.5)
        builder.add_phase("decode", 0.5, 3.0)
        builder.write_trace(constant_samples(0.0, 10.0, hz=1.0, power_w=2.0))
        builder.write_metadata(rail_manifest=["mock"])

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(
            summary.measurement_quality.phase_identifiability,
            {
                "prefill": "not_resolvable_sample_count",
                "decode": "identifiable",
            },
        )

    def test_malformed_phase_markers_fail_before_attribution(self) -> None:
        cases = {
            "unmatched": (
                [("phase_start", "decode", 1.0)],
                "no paired phase_end",
            ),
            "overlap": (
                [
                    ("phase_start", "prefill", 1.0),
                    ("phase_start", "decode", 2.0),
                    ("phase_end", "prefill", 3.0),
                    ("phase_end", "decode", 4.0),
                ],
                "same_source_phase_overlap",
            ),
        }
        for label, (events, expected) in cases.items():
            with self.subTest(label=label):
                builder = self.builder(run_id=f"phase-{label}")
                builder.measured_window(0.0, 10.0)
                for event_type, phase, timestamp_s in events:
                    builder.add_event(event_type, phase, timestamp_s)
                builder.add_token(0, 2.5)
                builder.write_trace(
                    constant_samples(0.0, 10.0, hz=1.0, power_w=2.0)
                )
                builder.write_metadata(rail_manifest=["mock"])

                summary = reduce_module.reduce_bundle(builder.path)

                self.assertEqual(summary.status, RunStatus.FAILED)
                self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
                self.assertIn(expected, summary.failure_message)
                self.assertIsNone(summary.phase_energy_j)
                self.assertIsNone(summary.energy_output_token_j)

    def test_same_source_8j_vs_6j_overlap_fails_closed(self) -> None:
        builder = self.builder(run_id="same-source-overlap")
        builder.measured_window(0.0, 10.0)
        first = {"node_role": "prefill", "node_id": "node-a"}
        second = {"node_role": "decode", "node_id": "node-a"}
        for event_type, timestamp_s, metadata in (
            ("phase_start", 1.0, first),
            ("phase_start", 2.0, second),
            ("phase_end", 3.0, first),
            ("phase_end", 4.0, second),
        ):
            builder.add_event(event_type, "decode", timestamp_s, metadata=metadata)
        builder.write_trace(constant_samples(0.0, 10.0, hz=1.0, power_w=2.0))
        builder.write_metadata(rail_manifest=["mock"])

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("same_source_phase_overlap", summary.failure_message)
        self.assertIsNone(summary.phase_energy_j)

    def test_distinct_source_8j_overlap_sums_legitimately(self) -> None:
        builder = self.builder(run_id="distinct-source-overlap")
        builder.measured_window(0.0, 10.0)
        node_a = {"node_role": "decode", "node_id": "node-a"}
        node_b = {"node_role": "decode", "node_id": "node-b"}
        builder.add_event("phase_start", "decode", 1.0, metadata=node_a)
        builder.add_event("phase_start", "decode", 2.0, metadata=node_b)
        builder.add_event("phase_end", "decode", 3.0, metadata=node_a)
        builder.add_event("phase_end", "decode", 4.0, metadata=node_b)
        builder.write_trace(constant_samples(0.0, 10.0, hz=1.0, power_w=2.0))
        builder.write_metadata(rail_manifest=["mock"])

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertEqual(summary.phase_energy_j, {"decode": 8.0})

    def test_role_only_split_streams_sum_concurrent_phase_energy(self) -> None:
        builder = self.builder(run_id="role-only-split-overlap")
        builder.measured_window(0.0, 10.0)
        prefill_role = {"node_role": "prefill"}
        decode_role = {"node_role": "decode"}
        builder.add_event("phase_start", "decode", 1.0, metadata=prefill_role)
        builder.add_event("phase_end", "decode", 3.0, metadata=prefill_role)
        builder.add_event("phase_start", "decode", 2.0, metadata=decode_role)
        builder.add_event("phase_end", "decode", 4.0, metadata=decode_role)
        builder.write_trace(
            constant_samples(0.0, 10.0, hz=1.0, power_w=2.0)
        )
        builder.write_metadata(rail_manifest=["mock"])

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertEqual(summary.phase_energy_j, {"decode": 8.0})


class DegenerateTests(ReduceTestCase):
    def test_no_idle_baseline_is_succeeded_absent_energy_evidence(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 2.0)
        builder.write_trace(constant_samples(0.0, 2.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"], idle=None)

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNone(summary.energy_request_j)
        self.assertEqual(summary.gross_energy_j, 15.0)
        request_gate = summary.window_evidence_precheck["idle_subtracted_request"]
        self.assertEqual(
            request_gate["energy_evidence"], EnergyEvidence.ABSENT.value
        )
        self.assertFalse(request_gate["eligible"])
        self.assertIn("idle_baseline_unrecorded", request_gate["reasons"])
        summary.to_dict()

    def test_fewer_than_two_samples_is_structured_failure(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 10.0)
        builder.write_trace(
            [PowerSample(timestamp_s=1.0, power_w=7.5, source="mock", rail="mock")]
        )
        builder.write_metadata(rail_manifest=["mock"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIsNotNone(summary.failure_message)
        # Schema-valid failure summary (status/failure_reason consistent).
        summary.to_dict()

    def test_missing_measured_window_is_structured_failure(self) -> None:
        builder = self.builder()
        builder.write_trace(constant_samples(0.0, 10.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)

    def test_zero_length_window_is_structured_failure(self) -> None:
        # P2-040 FIX-1 (ARC-3): a nonpositive measured window fails closed.
        builder = self.builder()
        builder.measured_window(5.0, 5.0)
        builder.write_trace(
            [PowerSample(timestamp_s=5.0, power_w=7.5, source="mock", rail="mock")]
        )
        builder.write_metadata(rail_manifest=["mock"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertTrue(
            summary.failure_message.startswith(
                "measured_run window duration must be > 0 s; got "
            ),
            summary.failure_message,
        )
        self.assertIsNone(summary.gross_energy_j)
        self.assertIsNone(summary.idle_subtracted_energy_j)
        self.assertIsNone(summary.energy_request_j)
        self.assertIsNone(summary.energy_token_j)
        # Schema-valid failure summary (status/failure_reason consistent).
        summary.to_dict()

    def test_runtime_cleanup_quality_is_copied_from_bundle_events(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 2.0)
        builder.add_event(
            "stage_completed",
            "cleanup",
            3.0,
            metadata={"cleanup_ok": False},
        )
        builder.write_trace(constant_samples(0.0, 2.0, hz=2.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"])

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIs(summary.measurement_quality.runtime_cleanup_ok, False)

    def test_zero_length_window_emits_no_derived_phase_metrics(self) -> None:
        # P2-040 FIX-1: an invalid measured window must not carry derived
        # phase/suite metrics into the structured failure summary.
        builder = self.builder()
        builder.measured_window(5.0, 5.0)  # stage_started ts == stage_completed ts
        builder.add_phase("prefill", 0.0, 2.0)
        builder.write_trace(constant_samples(0.0, 10.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIsNone(summary.phase_energy_j)
        self.assertIsNone(summary.suite_metrics)


class MockEndToEndTests(ReduceTestCase):
    """Reduce a real mock bundle produced by the controller (Slice 2C path)."""

    def reduce_mock_run(self) -> tuple[Path, object]:
        config = load_config(run_id="reduce-mock-e2e")
        clock = FakeClock(start=1_700_000_000.0)
        return run_benchmark(config, self.runs_root, clock)

    def measured_window_from_events(self, bundle_path: Path) -> tuple[float, float]:
        start = end = None
        for line in (bundle_path / "events.jsonl").read_text().splitlines():
            event = json.loads(line)
            if event["phase"] != "measured_run":
                continue
            if event["event_type"] == "stage_started":
                start = event["timestamp_s"]
            elif event["event_type"] == "stage_completed":
                end = event["timestamp_s"]
        assert start is not None and end is not None
        return start, end

    def phase_durations(self, bundle_path: Path) -> dict[str, float]:
        starts: dict[str, float] = {}
        durations: dict[str, float] = {}
        for line in (bundle_path / "events.jsonl").read_text().splitlines():
            event = json.loads(line)
            if event["event_type"] == "phase_start":
                starts[event["phase"]] = event["timestamp_s"]
            elif event["event_type"] == "phase_end":
                durations[event["phase"]] = event["timestamp_s"] - starts[event["phase"]]
        return durations

    def token_timestamps(self, bundle_path: Path) -> list[float]:
        return [
            json.loads(line)["timestamp_s"]
            for line in (bundle_path / "events.jsonl").read_text().splitlines()
            if json.loads(line)["event_type"] == "token"
        ]

    def test_mock_summary_matches_closed_form(self) -> None:
        # Mock constants: 32 prompt tokens, 8 output tokens; measured power
        # 7.5 W, idle 5.0 W. window = prompt*0.001 + output*0.010. gross =
        # 7.5*window; idle-subtracted = (7.5-5.0)*window = 2.5*window. The
        # window and per-phase durations are read back from the bundle so the
        # assertion is exact under FakeClock's float accumulation.
        bundle_path, summary = self.reduce_mock_run()
        start_s, end_s = self.measured_window_from_events(bundle_path)
        window = end_s - start_s
        durations = self.phase_durations(bundle_path)
        tokens = self.token_timestamps(bundle_path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertAlmostEqual(summary.gross_energy_j, 7.5 * window, places=9)
        self.assertAlmostEqual(summary.idle_subtracted_energy_j, 2.5 * window, places=9)
        self.assertAlmostEqual(summary.energy_request_j, 2.5 * window, places=9)
        self.assertAlmostEqual(summary.energy_token_j, (2.5 * window) / 40, places=9)
        self.assertAlmostEqual(summary.energy_output_token_j, (2.5 * window) / 8, places=9)

        # TTFT == prompt*0.001 + 0.010 (first token after prefill + 1 decode).
        # The disk-derived form is exact; the idealized-constant cross-check is
        # looser because the FakeClock accumulates tiny increments atop a ~1.7e9
        # epoch base (float cancellation ~1e-8).
        self.assertAlmostEqual(summary.ttft_s, tokens[0] - start_s, places=9)
        self.assertAlmostEqual(summary.ttft_s, 32 * 0.001 + 0.010, places=6)

        # The legacy convention counts 8 tokens over the 7 inter-token
        # intervals. The governed steady-state metric counts those 7
        # intervals over the same first-to-last span.
        span = tokens[-1] - tokens[0]
        self.assertAlmostEqual(summary.throughput_tokens_s, 8 / span, places=9)
        self.assertAlmostEqual(
            summary.inter_token_throughput_tokens_s, 7 / span, places=9
        )
        self.assertAlmostEqual(summary.decode_latency_s, span, places=9)

        self.assertAlmostEqual(
            summary.phase_energy_j["prefill"], 7.5 * durations["prefill"], places=9
        )
        self.assertAlmostEqual(
            summary.phase_energy_j["decode"], 7.5 * durations["decode"], places=9
        )

    def test_throughput_conventions_match_hand_computed_extremes(self) -> None:
        # Integer timestamps make both hand-computed fixtures exact. At N=8,
        # legacy exceeds inter-token throughput by 1/7 = 14.2857%; at N=512,
        # the excess is 1/511 = 0.1957%.
        for token_count in (8, 512):
            with self.subTest(token_count=token_count):
                timestamps = [float(index) for index in range(token_count)]
                span = float(token_count - 1)
                legacy = reduce_module._throughput_tokens_s(
                    timestamps, token_count
                )
                inter_token = reduce_module._inter_token_throughput_tokens_s(
                    timestamps, token_count
                )

                expected_legacy = {8: 8 / 7, 512: 512 / 511}[token_count]
                expected_excess = {8: 1 / 7, 512: 1 / 511}[token_count]
                self.assertEqual(legacy, expected_legacy)
                self.assertEqual(inter_token, 1.0)
                self.assertAlmostEqual(
                    legacy / inter_token - 1.0,
                    expected_excess,
                    places=15,
                )

    def test_mock_bundle_reducer_is_default_and_events_intact(self) -> None:
        # The controller's default reducer produced real energy numbers (not
        # the minimal-summary shape), and the event-flush restructuring left
        # events.jsonl ending with run_finalized and free of duplicates.
        bundle_path, summary = self.reduce_mock_run()
        self.assertIsNotNone(summary.gross_energy_j)
        self.assertIsNotNone(summary.phase_energy_j)

        lines = (bundle_path / "events.jsonl").read_text().splitlines()
        events = [json.loads(line) for line in lines]
        self.assertEqual(events[-1]["event_type"], "run_finalized")
        self.assertEqual(sum(1 for e in events if e["event_type"] == "run_finalized"), 1)
        # No duplicate event records.
        keys = [
            (e["event_type"], e["phase"], e["timestamp_s"], json.dumps(e["metadata"], sort_keys=True))
            for e in events
        ]
        self.assertEqual(len(keys), len(set(keys)))


class ThermalDriftTests(ReduceTestCase):
    def test_thermal_drift_from_pre_and_post(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 10.0)
        builder.write_trace(constant_samples(0.0, 10.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"], thermal_pre_c=40.0, thermal_post_c=43.5)
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertAlmostEqual(summary.measurement_quality.thermal_drift_c, 3.5, places=9)


class TokenFallbackTests(ReduceTestCase):
    """Slice 2N.3: energy_token_j falls back to the runtime's observed token
    counts in metadata when the config supplies no prompt_tokens, and the
    summary records which source was used."""

    PROMPT_TEXT_PROFILE = {"name": "prompt-text-only", "prompt_text": "count the joules"}

    def build(self, *, workload_profile: dict | None = None, workload_observed: dict | None = None):
        overrides = {}
        if workload_profile is not None:
            overrides["workload_profile"] = workload_profile
        builder = self.builder(**overrides)
        start_s, end_s = 100.0, 110.0
        builder.measured_window(start_s, end_s)
        builder.add_phase("decode", 101.0, 109.0)
        # 4 tokens inside the window so output_token_count comes from events.
        for index, t in enumerate((102.0, 104.0, 106.0, 108.0)):
            builder.add_token(index, t)
        builder.write_trace(constant_samples(start_s, end_s, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"], workload_observed=workload_observed)
        return reduce_module.reduce_bundle(builder.path)

    def test_prompt_text_only_uses_runtime_observed_total(self) -> None:
        # D-058: runtime observation is the authoritative denominator, not a
        # fallback.
        summary = self.build(
            workload_profile=self.PROMPT_TEXT_PROFILE,
            workload_observed={"token_count": 20, "output_token_count": 4},
        )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        # energy_request = 75 - 50 = 25 J over 20 observed total tokens.
        self.assertAlmostEqual(summary.energy_token_j, 25.0 / 20.0, places=9)
        self.assertEqual(
            summary.measurement_quality.token_count_source, "runtime_observed"
        )

    def test_runtime_observed_total_wins_over_configured_counts(self) -> None:
        # D-058 (P2-040 FIX-4): the example config pins prompt_tokens=32 and 4
        # token events are observed, but the runtime-observed total (999) is
        # the only governed denominator.
        summary = self.build(
            workload_observed={"token_count": 999, "output_token_count": 4},
        )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertAlmostEqual(summary.energy_token_j, 25.0 / 999.0, places=9)
        self.assertEqual(
            summary.measurement_quality.token_count_source, "runtime_observed"
        )

    def test_server_usage_is_eligible_and_wins_over_chunk_event_count(self) -> None:
        summary = self.build(
            workload_observed={
                "token_count": 20,
                "output_token_count": 3,
                "token_count_source": "server_usage",
            },
        )

        self.assertAlmostEqual(summary.energy_token_j, 25.0 / 20.0, places=9)
        self.assertAlmostEqual(summary.energy_output_token_j, 25.0 / 3.0, places=9)
        self.assertAlmostEqual(summary.throughput_tokens_s, 3.0 / 6.0, places=9)
        self.assertAlmostEqual(
            summary.inter_token_throughput_tokens_s, 2.0 / 6.0, places=9
        )
        self.assertEqual(summary.measurement_quality.token_count_source, "server_usage")
        self.assertEqual(summary.measurement_quality.token_counts_source, "server_usage")
        self.assertEqual(
            summary.window_evidence_precheck["per_token"],
            {
                "eligible": True,
                "reasons": [],
                "token_count_source": "server_usage",
            },
        )

    def test_stream_chunk_fallback_nulls_per_token_metrics_and_is_ineligible(self) -> None:
        summary = self.build(
            workload_observed={
                "token_count": 20,
                "output_token_count": 4,
                "token_count_source": "stream_chunk_fallback",
            },
        )

        self.assertIsNone(summary.energy_token_j)
        self.assertIsNone(summary.energy_output_token_j)
        self.assertIsNone(summary.throughput_tokens_s)
        self.assertIsNone(summary.inter_token_throughput_tokens_s)
        self.assertEqual(
            summary.measurement_quality.token_count_source,
            "stream_chunk_fallback",
        )
        self.assertEqual(
            summary.measurement_quality.token_counts_source,
            "stream_chunk_fallback",
        )
        self.assertEqual(
            summary.window_evidence_precheck["per_token"],
            {
                "eligible": False,
                "reasons": ["stream_chunk_fallback"],
                "token_count_source": "stream_chunk_fallback",
            },
        )

    def test_config_plus_output_events_does_not_fabricate_total_denominator(self) -> None:
        # P2-040 FIX-4 mutation test: configured prompt count plus output
        # events must not fabricate a governed total without a
        # runtime-observed total.
        summary = self.build()
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNone(summary.energy_token_j)
        self.assertIsNone(summary.measurement_quality.token_count_source)
        # The per-output-token metric keeps its runtime-observed denominator.
        self.assertAlmostEqual(summary.energy_output_token_j, 25.0 / 4.0, places=9)

    def test_neither_source_yields_none_unchanged(self) -> None:
        summary = self.build(workload_profile=self.PROMPT_TEXT_PROFILE)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNone(summary.energy_token_j)
        self.assertIsNone(summary.measurement_quality.token_count_source)
        # The per-output-token metric never needed prompt counts and is intact.
        self.assertAlmostEqual(summary.energy_output_token_j, 25.0 / 4.0, places=9)

    def test_config_output_token_fallback_is_flagged_and_output_metrics_null(self) -> None:
        builder = self.builder()
        start_s, end_s = 100.0, 110.0
        builder.measured_window(start_s, end_s)
        builder.write_trace(constant_samples(start_s, end_s, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"])

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNone(summary.energy_output_token_j)
        self.assertIsNone(summary.energy_token_j)
        self.assertEqual(summary.measurement_quality.token_counts_source, "config_fallback")

    def test_prompt_side_token_events_do_not_count_as_runtime_output_tokens(self) -> None:
        builder = self.builder()
        start_s, end_s = 100.0, 110.0
        builder.measured_window(start_s, end_s)
        builder.add_phase("prefill", 101.0, 103.0)
        for index, t in enumerate((101.25, 101.5, 101.75)):
            builder.add_event(
                "token",
                "prefill",
                t,
                message=f"prompt token {index}",
                metadata={"index": index},
            )
        builder.write_trace(constant_samples(start_s, end_s, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"], workload_observed={"token_count": 35})

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNone(summary.energy_output_token_j)
        self.assertIsNone(summary.throughput_tokens_s)
        self.assertIsNone(summary.inter_token_throughput_tokens_s)
        self.assertEqual(summary.measurement_quality.token_counts_source, "config_fallback")
        self.assertEqual(summary.measurement_quality.token_count_source, "runtime_observed")


class StructuredReadFailureTests(ReduceTestCase):
    """Slice 2N.6: missing/corrupt artifacts reduce to structured failures,
    never tracebacks (the docstring's 'never crashes' promise, now kept)."""

    def test_corrupt_config_is_structured_failure(self) -> None:
        builder = self.builder()
        builder.measured_window(100.0, 110.0)
        builder.write_trace(constant_samples(100.0, 110.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"])
        (builder.path / "config.json").write_text("{broken json")
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("config.json", summary.failure_message)

    def test_missing_metadata_is_structured_failure(self) -> None:
        builder = self.builder()
        builder.measured_window(100.0, 110.0)
        builder.write_trace(constant_samples(100.0, 110.0, hz=1.0, power_w=7.5))
        # write_metadata never called: metadata.json is absent.
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("metadata.json", summary.failure_message)

    def test_malformed_event_line_is_structured_failure(self) -> None:
        builder = self.builder()
        builder.write_trace(constant_samples(100.0, 110.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"])
        (builder.path / "events.jsonl").write_text("not json\n")
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertIn("events.jsonl", summary.failure_message)

    def test_nonnumeric_event_timestamp_is_structured_failure(self) -> None:
        # 2026-07-06 status review P1 repro: a corrupted marker timestamp
        # must reduce to a structured failure, not raise ValueError.
        builder = self.builder()
        builder.add_event("sampling_started", "measured_run", 100.0)
        builder.add_event("sampling_stopped", "measured_run", 110.0)
        builder.write_trace(constant_samples(100.0, 110.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"])
        events_path = builder.path / "events.jsonl"
        corrupted = events_path.read_text().replace('100.0', '"not-a-number"', 1)
        events_path.write_text(corrupted)
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("timestamp_s is not a finite number", summary.failure_message)


class RailMisalignmentTests(ReduceTestCase):
    """D-027 (2N.4): skewed per-rail timestamps are a structured reduction
    failure naming the misalignment - never a silently undersummed curve."""

    def test_skewed_rails_reduce_to_structured_failure(self) -> None:
        builder = self.builder()
        builder.measured_window(0.0, 2.0)
        samples = [
            PowerSample(timestamp_s=0.0, power_w=3.0, source="m", rail="a"),
            PowerSample(timestamp_s=0.001, power_w=4.0, source="m", rail="b"),
            PowerSample(timestamp_s=1.0, power_w=3.0, source="m", rail="a"),
            PowerSample(timestamp_s=1.001, power_w=4.0, source="m", rail="b"),
        ]
        builder.write_trace(samples)
        builder.write_metadata(rail_manifest=["a", "b"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("misaligned", summary.failure_message)
        # Quality context still present (config/metadata were readable).
        self.assertIsNotNone(summary.measurement_quality)

    def test_aligned_rails_unchanged_to_nine_decimals(self) -> None:
        # The aligned twin of the skewed fixture: identical powers, shared
        # timestamps; sums exactly per D-018.
        builder = self.builder()
        builder.measured_window(0.0, 2.0)
        samples = []
        for t in (0.0, 1.0, 2.0):
            samples.append(PowerSample(timestamp_s=t, power_w=3.0, source="m", rail="a"))
            samples.append(PowerSample(timestamp_s=t, power_w=4.0, source="m", rail="b"))
        builder.write_trace(samples)
        builder.write_metadata(rail_manifest=["a", "b"])
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertAlmostEqual(summary.gross_energy_j, 14.0, places=9)


class SuiteReduceTests(ReduceTestCase):
    def test_suite_metrics_are_reducible_from_mock_bundle(self) -> None:
        bundle_path, _ = run_benchmark(
            load_suite_config("reduce-suite"),
            self.runs_root,
            FakeClock(start=0.0),
        )
        summary = reduce_module.reduce_bundle(bundle_path)
        suite = summary.suite_metrics
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNotNone(suite)
        self.assertEqual(suite.planned_item_count, 5)
        self.assertEqual(suite.executed_item_count, 5)
        self.assertEqual(suite.status_counts["succeeded"], 5)
        self.assertEqual(suite.floor_source, "none_pending_P2-015")
        self.assertIsNone(suite.floor_abs_j)
        self.assertIsNone(suite.floor_cmp_j)
        self.assertEqual([item.item_index for item in suite.items], [0, 1, 2, 3, 4])
        # Mock suite durations derive from D-019 constants at 7.5 W:
        # (4ms+30ms, 4ms+20ms, 5ms+10ms, 2ms+10ms, 2ms+10ms) * 7.5 W.
        expected_item_j = [0.255, 0.18, 0.1125, 0.09, 0.09]
        for item, expected in zip(suite.items, expected_item_j, strict=True):
            self.assertAlmostEqual(item.energy_gross_j, expected, places=9)
        self.assertEqual(
            [item.item_index for item in suite.items if item.item_id == "mock_sentinel_repeat"],
            [3, 4],
        )
        blocks = {block.group_id: block for block in suite.blocks}
        self.assertEqual(set(blocks), {"block_a", "block_b"})
        self.assertAlmostEqual(blocks["block_a"].energy_gross_j, 0.435, places=9)
        self.assertAlmostEqual(blocks["block_b"].energy_gross_j, 0.2925, places=9)
        self.assertAlmostEqual(summary.gross_energy_j, 0.7275, places=9)
        self.assertIn("block_a/level_1", {level.group_id for level in suite.levels})
        self.assertIn("block_b/level_1", {level.group_id for level in suite.levels})

    def test_zero_window_suite_bundle_is_structured_failure(self) -> None:
        bundle_path, _ = run_benchmark(
            load_suite_config("reduce-suite-zero-window"),
            self.runs_root,
            FakeClock(start=1_700_000_000.0),
        )
        events_path = bundle_path / "events.jsonl"
        events = read_jsonl(events_path)
        sampling_start = next(
            event["timestamp_s"] for event in events if event["event_type"] == "sampling_started"
        )
        for event in events:
            if event["event_type"] == "sampling_stopped" or event["phase"] == "suite":
                event["timestamp_s"] = sampling_start
        write_jsonl(events_path, events)

        summary = reduce_module.reduce_bundle(bundle_path)

        # P2-040 FIX-1: a zero-length measured window is a structured failure,
        # never a succeeded suite summary with degenerate metrics.
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertTrue(
            summary.failure_message.startswith(
                "measured_run window duration must be > 0 s; got "
            ),
            summary.failure_message,
        )
        self.assertIsNone(summary.suite_metrics)

    def test_single_prompt_reduction_has_null_suite_metrics(self) -> None:
        bundle_path, _ = run_benchmark(
            load_config(run_id="reduce-single-suite-null"),
            self.runs_root,
            FakeClock(start=1_700_000_000.0),
        )
        summary = reduce_module.reduce_bundle(bundle_path)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNone(summary.suite_metrics)
        self.assertEqual(
            summary.summary_provenance["reducer_version"],
            reduce_module.REDUCER_VERSION,
        )

    def test_authentic_frozen_v1_and_current_v2_summaries_each_revalidate(self) -> None:
        powers_w = [4.0] * 27 + [10.0] * 6
        intervals_s = [1.0] * 27 + [1.2] * 6
        raw_idle = powermetrics_stream(powers_w, intervals_s)
        arithmetic_mean_w = math.fsum(powers_w) / len(powers_w)
        arithmetic_variance_w2 = math.fsum(
            (value - arithmetic_mean_w) ** 2 for value in powers_w
        ) / (len(powers_w) - 1)
        weighted_mean_w, weighted_variance_w2 = (
            duration_weighted_mean_and_sample_variance(powers_w, intervals_s)
        )
        expected_v1 = estimate_newey_west_bartlett(powers_w, 10)
        expected_v2 = estimate_newey_west_bartlett(
            powers_w, 10, intervals_s
        )
        self.assertNotEqual(
            expected_v1.governed_variance_of_mean_w2,
            expected_v2.governed_variance_of_mean_w2,
        )

        def make_bundle(run_id: str, *, frozen: bool) -> Path:
            bundle_path, _ = run_benchmark(
                load_config(run_id=run_id),
                self.runs_root,
                FakeClock(start=1_700_000_000.0),
            )
            (bundle_path / "raw" / "powermetrics_idle.plist").write_bytes(
                raw_idle
            )
            metadata_path = bundle_path / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["idle_baseline"] = {
                "power_w_mean": (
                    arithmetic_mean_w if frozen else weighted_mean_w
                ),
                "power_w_stddev": math.sqrt(
                    arithmetic_variance_w2 if frozen else weighted_variance_w2
                ),
                "duration_s": math.fsum(intervals_s),
                "sample_count": len(powers_w),
                "telemetry_backend": "powermetrics",
            }
            metadata_path.write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n"
            )
            return bundle_path

        current_bundle = make_bundle("current-v2-unequal-duration", frozen=False)
        current_summary = reduce_module.reduce_bundle(current_bundle).to_dict()
        (current_bundle / "summary_metrics.json").write_text(
            json.dumps(current_summary, indent=2, sort_keys=True) + "\n"
        )
        self.assertEqual(
            current_summary["summary_provenance"]["reducer_version"],
            reduce_module.REDUCER_VERSION,
        )
        self.assertEqual(
            current_summary["idle_mean_uncertainty"]["method"],
            "duration_weighted_newey_west_bartlett_10s_iid_floor_v2",
        )
        self.assertAlmostEqual(
            current_summary["idle_mean_uncertainty"][
                "governed_variance_of_mean_w2"
            ],
            expected_v2.governed_variance_of_mean_w2,
        )
        self.assertEqual(validate_bundle(current_bundle, strict=True), [])

        for version in ("0.4.1", "0.4.2"):
            with self.subTest(version=version):
                bundle_path = make_bundle(
                    f"frozen-v1-unequal-duration-{version}", frozen=True
                )
                summary_path = bundle_path / "summary_metrics.json"
                summary = reduce_module.reduce_bundle(
                    bundle_path, reducer_version=version
                ).to_dict()
                summary["idle_baseline"].pop("gpu_freq_mhz_mean")
                if version == "0.4.1":
                    summary.pop("inter_token_throughput_tokens_s")
                summary_path.write_text(
                    json.dumps(summary, indent=2, sort_keys=True) + "\n"
                )

                self.assertEqual(
                    summary["summary_provenance"]["reducer_version"], version
                )
                self.assertEqual(
                    summary["idle_mean_uncertainty"]["method"],
                    "newey_west_bartlett_10s_iid_floor_v1",
                )
                self.assertAlmostEqual(
                    summary["idle_mean_uncertainty"][
                        "governed_variance_of_mean_w2"
                    ],
                    expected_v1.governed_variance_of_mean_w2,
                )
                self.assertNotEqual(
                    summary["idle_mean_uncertainty"][
                        "governed_variance_of_mean_w2"
                    ],
                    current_summary["idle_mean_uncertainty"][
                        "governed_variance_of_mean_w2"
                    ],
                )
                self.assertEqual(
                    (bundle_path / "raw" / "powermetrics_idle.plist").read_bytes(),
                    (current_bundle / "raw" / "powermetrics_idle.plist").read_bytes(),
                )
                self.assertEqual(validate_bundle(bundle_path, strict=True), [])

    def test_reconciliation_script_verify_interface_builds_and_verifies_receipt(
        self,
    ) -> None:
        script_path = REPO_ROOT / "scripts" / "reconcile_retained_powermetrics.py"
        spec = importlib.util.spec_from_file_location(
            "reconcile_retained_powermetrics", script_path
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        runs_root = self.runs_root / "reconciliation-corpus"
        target_pct = -0.4980639151088995
        legacy_gross_j = 1.0 * (1.0 + target_pct / 100.0)
        stage_duration_s = legacy_gross_j / (1.0 - 0.0093)
        raw = powermetrics_stream([1.0], [2.0])
        bundle_names = [
            "example-mac-mlx-qwen35-122b-512t__r1",
            "a",
            "b",
            "c",
            "d",
            "e",
        ]
        for bundle_name in bundle_names:
            bundle = runs_root / bundle_name
            (bundle / "raw").mkdir(parents=True)
            (bundle / "raw" / "powermetrics.plist").write_bytes(raw)
            (bundle / "raw" / "powermetrics_idle.plist").write_bytes(raw)
            (bundle / "metadata.json").write_text(
                json.dumps(
                    {
                        "run_id": bundle_name,
                        "uncertainty_evidence": {
                            "clock_anchor": {
                                "first_sample_end_point_epoch_s": 2.0
                            }
                        },
                    }
                )
                + "\n"
            )
            events = [
                {
                    "timestamp_s": timestamp_s,
                    "event_type": event_type,
                    "phase": "measured_run",
                    "message": event_type,
                    "metadata": {},
                }
                for timestamp_s, event_type in (
                    (0.5, "sampling_started"),
                    (1.5, "sampling_stopped"),
                    (0.5, "stage_started"),
                    (0.5 + stage_duration_s, "stage_completed"),
                )
            ]
            write_jsonl(
                bundle / "events.jsonl",
                sorted(events, key=lambda event: event["timestamp_s"]),
            )
            (bundle / "summary_metrics.json").write_text(
                json.dumps(
                    {
                        "gross_energy_j": legacy_gross_j,
                        "idle_subtracted_energy_j": legacy_gross_j - 0.5,
                    }
                )
                + "\n"
            )

        output = self.runs_root / "reconciliation.json"
        exit_code = module.main(
            [
                "--runs-root",
                str(runs_root),
                "--output",
                str(output),
                "--verify",
            ]
        )

        self.assertEqual(exit_code, 0)
        receipt = json.loads(output.read_text())
        self.assertEqual(receipt["corpus"]["bundle_count"], 6)
        self.assertAlmostEqual(
            receipt["t07_reconciliation"]["scanner_reconstruction_pct"],
            target_pct,
        )
        self.assertAlmostEqual(
            receipt["t07_reconciliation"]["verifier_reconstruction_pct"],
            -0.93,
        )
        self.assertTrue(
            all(
                row["counter_consistency"]["all_records_within_tolerance"]
                for row in receipt["bundles"]
            )
        )

    def test_powermetrics_interval_partial_edges_use_overlap_not_trapezoids(self) -> None:
        curve = [
            reduce_module.TracePoint(1.0, 10.0, 0.0, 1.0),
            reduce_module.TracePoint(2.0, 20.0, 1.0, 2.0),
            reduce_module.TracePoint(3.0, 30.0, 2.0, 3.0),
        ]

        self.assertEqual(reduce_module._integrate(curve, 0.5, 2.25), 32.5)
        self.assertEqual(
            reduce_module._in_window_sample_count(
                curve, reduce_module.Window(0.5, 2.25)
            ),
            3,
        )


if __name__ == "__main__":
    unittest.main()


class D078AnchorEnvelopeTests(unittest.TestCase):
    """Continuous common-shift envelope math (D-078)."""

    @staticmethod
    def interval_curve(specs):
        from joulewise.bundle_read import TracePoint

        return [
            TracePoint(
                t=end_s,
                power_w=power_w,
                support_start_s=start_s,
                support_end_s=end_s,
            )
            for start_s, end_s, power_w in specs
        ]

    def test_interior_extremum_defeats_endpoint_only_evaluation(self) -> None:
        from joulewise.bundle_read import Window
        from joulewise.reduce import _anchor_shift_envelope, _shift_energy_j

        curve = self.interval_curve(
            [
                (-2.0, -1.0, 0.0),
                (-1.0, 0.0, 0.0),
                (0.0, 1.0, 10.0),
                (1.0, 2.0, 0.0),
                (2.0, 3.0, 0.0),
            ]
        )
        window = Window(0.3, 1.2)
        bound_s = 0.5
        contributions = [(curve, [window])]
        envelope = _anchor_shift_envelope(contributions, bound_s)
        self.assertIsNotNone(envelope)
        self.assertAlmostEqual(envelope["point_j"], 7.0, places=9)
        # The true maximum (support fully inside the window) is interior.
        self.assertAlmostEqual(envelope["upper_j"], 9.0, places=9)
        endpoint_only = max(
            _shift_energy_j(contributions, -bound_s),
            _shift_energy_j(contributions, bound_s),
        )
        self.assertLess(endpoint_only, envelope["upper_j"] - 1.0)
        self.assertAlmostEqual(envelope["lower_j"], 2.0, places=9)
        self.assertLessEqual(envelope["lower_j"], envelope["point_j"])
        self.assertLessEqual(envelope["point_j"], envelope["upper_j"])

    def test_common_shift_multiwindow_beats_independent_maximization(self) -> None:
        from joulewise.bundle_read import Window
        from joulewise.reduce import _anchor_shift_envelope

        curve = self.interval_curve(
            [
                (-1.0, 0.0, 0.0),
                (0.0, 1.0, 10.0),
                (1.0, 2.0, 0.0),
                (2.0, 3.0, 10.0),
                (3.0, 4.0, 0.0),
            ]
        )
        window_a = Window(0.3, 1.2)   # maximized near delta = +0.25
        window_b = Window(1.55, 2.45)  # maximized near delta = -0.5
        bound_s = 0.6
        joint = _anchor_shift_envelope([(curve, [window_a, window_b])], bound_s)
        self.assertIsNotNone(joint)
        upper_a = _anchor_shift_envelope([(curve, [window_a])], bound_s)["upper_j"]
        upper_b = _anchor_shift_envelope([(curve, [window_b])], bound_s)["upper_j"]
        self.assertAlmostEqual(upper_a, 9.0, places=9)
        self.assertAlmostEqual(upper_b, 9.0, places=9)
        # Independently maximizing each window would claim 18 J; the shared
        # anchor shift cannot realize both extremes simultaneously.
        self.assertLess(joint["upper_j"], upper_a + upper_b - 4.0)

    def test_missing_edge_coverage_under_any_shift_withholds_envelope(self) -> None:
        from joulewise.bundle_read import Window
        from joulewise.reduce import _anchor_shift_envelope

        curve = self.interval_curve([(0.0, 1.0, 10.0), (1.0, 2.0, 5.0)])
        # Trace [0, 2] cannot cover window end 1.95 under delta = -0.5.
        self.assertIsNone(
            _anchor_shift_envelope([(curve, [Window(0.5, 1.95)])], 0.5)
        )
        # ... but a fully covered window records an envelope.
        self.assertIsNotNone(
            _anchor_shift_envelope([(curve, [Window(0.6, 1.4)])], 0.5)
        )

    def test_zero_bound_degenerates_to_point(self) -> None:
        from joulewise.bundle_read import Window
        from joulewise.reduce import _anchor_shift_envelope

        curve = self.interval_curve(
            [(0.0, 1.0, 3.0), (1.0, 2.0, 3.0), (2.0, 3.0, 3.0)]
        )
        envelope = _anchor_shift_envelope([(curve, [Window(0.5, 2.5)])], 0.0)
        self.assertEqual(envelope["lower_j"], envelope["point_j"])
        self.assertEqual(envelope["upper_j"], envelope["point_j"])
        self.assertEqual(envelope["max_abs_delta_j"], 0.0)

    def test_point_curve_quadratic_refinement_matches_dense_grid(self) -> None:
        from joulewise.bundle_read import TracePoint, Window
        from joulewise.reduce import _anchor_shift_envelope, _shift_energy_j

        curve = [
            TracePoint(t=float(index) / 4.0, power_w=power_w)
            for index, power_w in enumerate(
                [1.0, 2.0, 6.0, 9.0, 4.0, 2.0, 1.5, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5]
            )
        ]
        window = Window(0.4, 2.1)
        bound_s = 0.3
        contributions = [(curve, [window])]
        envelope = _anchor_shift_envelope(contributions, bound_s)
        self.assertIsNotNone(envelope)
        dense = [
            _shift_energy_j(contributions, -bound_s + step * (2 * bound_s / 3000))
            for step in range(3001)
        ]
        self.assertLessEqual(envelope["lower_j"], min(dense) + 1e-9)
        self.assertGreaterEqual(envelope["upper_j"], max(dense) - 1e-9)

    def test_translate_and_scale_preserve_envelope_shape(self) -> None:
        from joulewise.reduce import _scale_envelope, _translate_envelope

        base = {
            "method": "common_trace_shift_interval_overlap_v1",
            "anchor_bound_s": 0.1,
            "point_j": 10.0,
            "lower_j": 9.0,
            "upper_j": 12.0,
            "max_abs_delta_j": 2.0,
        }
        translated = _translate_envelope(base, -4.0)
        self.assertEqual(translated["point_j"], 6.0)
        self.assertEqual(translated["lower_j"], 5.0)
        self.assertEqual(translated["upper_j"], 8.0)
        scaled = _scale_envelope(base, 0.5)
        self.assertEqual(scaled["point_j"], 5.0)
        self.assertEqual(scaled["lower_j"], 4.5)
        self.assertEqual(scaled["upper_j"], 6.0)
        self.assertEqual(scaled["max_abs_delta_j"], 1.0)


class D078R01RegressionTests(unittest.TestCase):
    """Sealed-evidence regressions for the D-078 anchor correction."""

    FIXTURE = REPO_ROOT / "tests" / "fixtures" / "d078_r01"
    RAW_SHA256 = "cb25bfddc13610150795732a44be1183c154dcc4990b857425943028fd8edf81"

    def test_fixture_raw_matches_sealed_evidence(self) -> None:
        import hashlib

        self.assertEqual(
            hashlib.sha256(
                (self.FIXTURE / "raw" / "powermetrics.plist").read_bytes()
            ).hexdigest(),
            self.RAW_SHA256,
        )

    def test_frozen_050_dispatch_reproduces_recorded_gross(self) -> None:
        summary = reduce_module.reduce_bundle(self.FIXTURE, reducer_version="0.5.0")
        stored = json.loads((self.FIXTURE / "summary_metrics.json").read_text())
        self.assertEqual(summary.gross_energy_j, stored["gross_energy_j"])
        self.assertEqual(summary.gross_energy_j, 0.2742679692914486)
        payload = summary.to_dict()
        self.assertNotIn("energy_anchor_shift_envelopes", payload)
        self.assertNotIn(
            "E_clock_anchor_shift_bound_j", payload["energy_bound_terms_j"]
        )
        # Default dispatch replays the recorded 0.5.0 arm.
        self.assertEqual(
            reduce_module.reduce_bundle(self.FIXTURE).summary_provenance[
                "reducer_version"
            ],
            "0.5.0",
        )

    def test_051_derives_corrected_anchor_gross_and_envelope(self) -> None:
        summary = reduce_module.reduce_bundle(self.FIXTURE, reducer_version="0.5.1")
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        # Anchor midpoint of the admissible interval (lead-verified oracle).
        self.assertAlmostEqual(summary.gross_energy_j, 7.664158853340149, places=6)
        envelopes = summary.energy_anchor_shift_envelopes
        self.assertIsNotNone(envelopes)
        gross = envelopes["/gross_energy_j"]
        self.assertEqual(
            gross["method"], "common_trace_shift_interval_overlap_v1"
        )
        self.assertAlmostEqual(gross["lower_j"], 6.765943, delta=1e-3)
        self.assertAlmostEqual(gross["upper_j"], 7.682065, delta=1e-3)
        self.assertLessEqual(gross["lower_j"], gross["point_j"])
        self.assertLessEqual(gross["point_j"], gross["upper_j"])
        self.assertAlmostEqual(gross["anchor_bound_s"], 0.05656, delta=5e-4)
        self.assertEqual(
            summary.energy_bound_terms_j["E_clock_anchor_shift_bound_j"],
            gross["max_abs_delta_j"],
        )
        self.assertEqual(summary.energy_uncertainty_status, "bounded")
        # Idle subtraction translates the gross envelope.
        idle = envelopes["/idle_subtracted_energy_j"]
        self.assertAlmostEqual(
            gross["point_j"] - idle["point_j"],
            gross["lower_j"] - idle["lower_j"],
            places=9,
        )

    def test_051_interior_extremum_present_on_r01(self) -> None:
        from joulewise.bundle_read import BundleReader
        from joulewise.reduce import (
            _derive_anchor_context,
            _shift_energy_j,
        )

        reader = BundleReader(self.FIXTURE)
        context = _derive_anchor_context(reader, reader.metadata())
        self.assertFalse(context.unresolved)
        window = reader.measured_window()
        contributions = [(context.curve, [window])]
        summary = reduce_module.reduce_bundle(self.FIXTURE, reducer_version="0.5.1")
        upper = summary.energy_anchor_shift_envelopes["/gross_energy_j"]["upper_j"]
        endpoint_only = max(
            _shift_energy_j(contributions, -context.bound_s),
            _shift_energy_j(contributions, context.bound_s),
        )
        # r01's maximum lies strictly inside (-B, +B): endpoint-only
        # evaluation is unsound.
        self.assertGreater(upper, endpoint_only + 0.5)

    def test_051_does_not_launder_precheck_eligibility(self) -> None:
        summary = reduce_module.reduce_bundle(self.FIXTURE, reducer_version="0.5.1")
        gate = summary.window_evidence_precheck["gross_request"]
        self.assertFalse(gate["eligible"])
        self.assertIn("cadence_ratio_below_threshold", gate["reasons"])
        self.assertLess(gate["cadence_ratio"], 4.0)
        self.assertAlmostEqual(gate["cadence_ratio"], 3.23, delta=0.11)
        # The corrected anchor bound replaces the stale 1.13 s recorded bound.
        self.assertLess(gate["clock_anchor_bound_s"], 0.06)
        self.assertNotIn("clock_bound_exceeds_quarter_window", gate["reasons"])

    def test_051_trace_tamper_fails_closed(self) -> None:
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            shutil.copytree(self.FIXTURE, bundle)
            trace = (bundle / "power_trace.csv").read_text().splitlines()
            row = trace[2].split(",")
            row[1] = str(float(row[1]) + 0.5)
            trace[2] = ",".join(row)
            (bundle / "power_trace.csv").write_text("\n".join(trace) + "\n")
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            self.assertEqual(summary.status, RunStatus.FAILED)
            self.assertIn(
                "does not match raw powermetrics evidence",
                summary.failure_message,
            )

    def test_051_unresolved_anchor_is_a_claim_barrier_not_a_fallback(self) -> None:
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            shutil.copytree(self.FIXTURE, bundle)
            metadata = json.loads((bundle / "metadata.json").read_text())
            del metadata["uncertainty_evidence"]["clock_anchor"]["clock_stamps"][
                "pre_spawn"
            ]
            (bundle / "metadata.json").write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n"
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            self.assertEqual(summary.status, RunStatus.SUCCEEDED)
            self.assertIsNone(summary.energy_anchor_shift_envelopes)
            self.assertIsNone(
                summary.energy_bound_terms_j["E_clock_anchor_shift_bound_j"]
            )
            self.assertEqual(summary.energy_uncertainty_status, "not_estimable")
            for gate_name in ("gross_request", "idle_subtracted_request"):
                gate = summary.window_evidence_precheck[gate_name]
                self.assertFalse(gate["eligible"])
                self.assertIn("clock_anchor_unresolved", gate["reasons"])
            # The un-anchored gross falls back to the stored timeline value.
            self.assertAlmostEqual(
                summary.gross_energy_j, 0.2742679692914486, places=9
            )

    def test_051_missing_raw_capture_is_unresolved(self) -> None:
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            shutil.copytree(self.FIXTURE, bundle)
            (bundle / "raw" / "powermetrics.plist").unlink()
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            self.assertEqual(summary.status, RunStatus.SUCCEEDED)
            self.assertIn(
                "clock_anchor_unresolved",
                summary.window_evidence_precheck["gross_request"]["reasons"],
            )

    def test_051_invalid_instrument_calibration_fails_closed(self) -> None:
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            shutil.copytree(self.FIXTURE, bundle)
            metadata = json.loads((bundle / "metadata.json").read_text())
            metadata["instrument_calibration"] = {"b_fiducial_s": -1.0}
            (bundle / "metadata.json").write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n"
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            self.assertIn(
                "clock_anchor_unresolved",
                summary.window_evidence_precheck["gross_request"]["reasons"],
            )

    def test_051_fiducial_bound_widens_effective_bound(self) -> None:
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            shutil.copytree(self.FIXTURE, bundle)
            metadata = json.loads((bundle / "metadata.json").read_text())
            metadata["instrument_calibration"] = {
                "b_fiducial_s": 0.08,
                "artifact_sha256": "ab" * 32,
            }
            (bundle / "metadata.json").write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n"
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            gross = summary.energy_anchor_shift_envelopes["/gross_energy_j"]
            self.assertEqual(gross["anchor_bound_s"], 0.08)
            self.assertEqual(
                summary.window_evidence_precheck["gross_request"][
                    "clock_anchor_bound_s"
                ],
                0.08,
            )

    def test_051_golden_summary(self) -> None:
        golden_path = REPO_ROOT / "tests" / "goldens" / "d078_r01_reducer_051.json"
        summary = reduce_module.reduce_bundle(
            self.FIXTURE, reducer_version="0.5.1"
        ).to_dict()
        self.assertEqual(summary, json.loads(golden_path.read_text()))
