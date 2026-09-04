"""Tests for the reducer (Slice 2D; D-002, D-018, D-019).

Bundles are assembled with the real :class:`RunBundleWriter` plus hand-authored
events and traces under a :class:`FakeClock`, so every expected energy is a
closed form computed by hand and asserted to 9 decimal places. The reducer is a
pure function over the on-disk artifacts, so the synthetic bundles are not
finalized - the reducer reads a not-yet-finalized directory exactly as the
controller invokes it before ``finalize()``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import plistlib
import tempfile
import unittest
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from joulewise import reduce as reduce_module
from joulewise.adapters.powermetrics import duration_weighted_mean_and_sample_variance
from joulewise.analysis_engine.inputs import (
    AnalysisInputError,
    BundleEvidence,
    _require_common_launch_lineage,
)
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
from joulewise.uncertainty_evidence import ACTIVE_CAPTURE_ANCHOR_METHOD

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

_SELF_CONSISTENT_CALIBRATIONS: dict[
    tuple[float, tuple[tuple[float, float], ...], str, str],
    tuple[dict, bytes, bytes],
] = {}


def self_consistent_calibration(
    *,
    first_endpoint_s: float | None = None,
    commanded_edges: list[tuple[float, float]] | None = None,
    protocol_id: str | None = None,
    anchor_method: str = ACTIVE_CAPTURE_ANCHOR_METHOD,
) -> tuple[dict, bytes, bytes]:
    """Build a physically consistent protocol calibration for reducer tests."""

    from joulewise.uncertainty_evidence import (
        resolve_anchor_deriver,
    )
    from joulewise.adapters.powermetrics import (
        anchor_records_from_powermetrics,
        parse_powermetrics_records,
    )
    from joulewise.clock import ClockStamp
    from joulewise.powermetrics_fiducial import (
        LEGACY_PULSE_COUNT,
        PROTOCOL_ID,
        PROTOCOL_V2_ID,
        PROTOCOL_V2_SHA256,
        PROTOCOL_V3_SHA256,
        RESIDUAL_REGION_METHOD,
        CommandedPulse,
        instrument_evidence,
        LEGACY_PROTOCOL_ID,
        protocol_pulse_count,
        pulse_schedule,
        rederive_detection_from_artifacts,
    )
    # Keep the synthetic calibration on the same epoch scale as the retained
    # D-078 measuring bundle.  Freshness now covers the measured-window end,
    # so a calibration living near epoch 1000 would be correctly stale for a
    # 2026 bundle even though its relative pulse geometry is self-consistent.
    protocol_id = protocol_id or LEGACY_PROTOCOL_ID
    if first_endpoint_s is None:
        first_endpoint_s = 1_784_490_850.05
    nanoseconds_per_second = 1_000_000_000
    cadence_ns = 100_000_000
    cadence_s = cadence_ns / nanoseconds_per_second
    warmup_edges = [
        (first_endpoint_s + 1.95, first_endpoint_s + 2.95),
        (first_endpoint_s + 4.45, first_endpoint_s + 5.45),
        (first_endpoint_s + 6.95, first_endpoint_s + 7.95),
    ]
    if commanded_edges is None:
        commanded_edges = pulse_schedule(
            protocol_pulse_count(protocol_id),
            start_s=first_endpoint_s + 14.95,
        )
    cache_key = (
        first_endpoint_s,
        tuple(commanded_edges),
        protocol_id,
        anchor_method,
    )
    if cache_key in _SELF_CONSISTENT_CALIBRATIONS:
        evidence, raw, events = _SELF_CONSISTENT_CALIBRATIONS[cache_key]
        return json.loads(json.dumps(evidence)), raw, events
    true_edges = [(on_s + 0.02, off_s + 0.02) for on_s, off_s in commanded_edges]
    capture_end_s = true_edges[-1][1] + 5.0

    documents: list[dict] = []
    first_endpoint_ns = round(first_endpoint_s * nanoseconds_per_second)
    # Keep the established synthetic waveform byte-for-byte stable for its
    # many reducer callers. Its float phase affects only overlap/power values;
    # record endpoints and native-second labels come exclusively from the
    # integer grid below, so it cannot corrupt clock-anchor consistency.
    signal_endpoint_s = first_endpoint_s
    record_index = 0
    while signal_endpoint_s <= capture_end_s + 1e-12:
        endpoint_ns = first_endpoint_ns + record_index * cadence_ns
        endpoint_s = endpoint_ns / nanoseconds_per_second
        whole_second_s = endpoint_ns // nanoseconds_per_second
        if math.floor(endpoint_s) != whole_second_s:
            raise AssertionError("integer endpoint lost its whole-second label")
        start_s = signal_endpoint_s - cadence_s
        overlap = math.fsum(
            max(
                0.0,
                min(signal_endpoint_s, off_s) - max(start_s, on_s),
            )
            / cadence_s
            for on_s, off_s in (*warmup_edges, *true_edges)
        )
        gpu_w = 2.0 + 20.0 * overlap
        documents.append(
            {
                "timestamp": datetime.fromtimestamp(
                    whole_second_s, tz=timezone.utc
                ),
                "elapsed_ns": cadence_ns,
                "is_delta": True,
                "hw_model": "Mac15,9",
                "kern_osversion": "25F84",
                "processor": {
                    "cpu_power": 0.0,
                    "gpu_power": gpu_w * 1000.0,
                    "ane_power": 0.0,
                    "cpu_energy": 0,
                    "gpu_energy": round(gpu_w * cadence_s * 1000.0),
                    "ane_energy": 0,
                },
            }
        )
        record_index += 1
        signal_endpoint_s += cadence_s
    raw = b"\0".join(plistlib.dumps(document) for document in documents)

    def stamp(epoch_s: float) -> ClockStamp:
        mono = epoch_s - (first_endpoint_s - 50.0)
        return ClockStamp(
            epoch_s=epoch_s,
            monotonic_before_s=mono - 1e-6,
            monotonic_after_s=mono + 1e-6,
            wall_resolution_s=1e-6,
            monotonic_resolution_s=1e-6,
        )

    anchor_stamps = {
        # Tight but non-zero causal bracket around the true 1000.05 endpoint;
        # this keeps the synthetic production calibration representative of a
        # usable live bound rather than a deliberately wide 50 ms half-width.
        "pre_spawn": stamp(first_endpoint_s - 0.101),
        "first_parse": stamp(first_endpoint_s + 0.001),
        "sampling_started": stamp(first_endpoint_s + 0.15),
        "sampling_stopped": stamp(capture_end_s + 0.5),
        "post_parse": stamp(capture_end_s + 1.0),
    }
    native = parse_powermetrics_records(raw)
    clock_anchor = resolve_anchor_deriver(anchor_method)(
        stamps=anchor_stamps,
        records=anchor_records_from_powermetrics(native),
    )
    if clock_anchor.get("status") != "bounded":
        raise AssertionError(clock_anchor)
    if clock_anchor.get("method") != anchor_method:
        raise AssertionError(clock_anchor)

    event_rows: list[dict] = []

    def add_pair(kind: str, on_s: float, off_s: float, index: int) -> None:
        for edge, epoch_s in (("on", on_s), ("off", off_s)):
            event_rows.append(
                {
                    "timestamp_s": epoch_s,
                    "event_type": f"{kind}_command_{edge}",
                    "phase": "instrument_validation",
                    "message": f"{kind}_command_{edge}",
                    "metadata": {
                        "clock_stamp": asdict(stamp(epoch_s)),
                        f"{kind}_index": index,
                    },
                }
            )

    for index, (on_s, off_s) in enumerate(warmup_edges):
        add_pair("warmup", on_s, off_s, index)
    for index, (on_s, off_s) in enumerate(commanded_edges):
        add_pair("pulse", on_s, off_s, index)
    events = "".join(
        json.dumps(row, sort_keys=True) + "\n" for row in event_rows
    ).encode("utf-8")
    detection = rederive_detection_from_artifacts(
        raw, events, clock_anchor, protocol_id=protocol_id
    )
    bindings = {
        "hardware_model": "Mac15,9",
        "os_build": "25F84",
        "powermetrics_sha256": "ab" * 32,
        "sampling_interval_ms": 100,
        "anchor_method_version": anchor_method,
        "mlx_version": "0.31.2",
        "pulse_protocol_id": protocol_id,
        "power_policy": "ac_high_power",
    }
    if protocol_id in {PROTOCOL_V2_ID, PROTOCOL_ID}:
        bindings.update(
            {
                "estimator_revision": RESIDUAL_REGION_METHOD,
                "protocol_sha256": (
                    PROTOCOL_V2_SHA256
                    if protocol_id == PROTOCOL_V2_ID
                    else PROTOCOL_V3_SHA256
                ),
            }
        )
    evidence = instrument_evidence(
        detection,
        bindings=bindings,
        validation_id="synthetic-self-consistent-v1",
        artifact_sha256={
            "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
            "events.jsonl": hashlib.sha256(events).hexdigest(),
        },
        protocol_id=protocol_id,
        protocol_pulse_count=protocol_pulse_count(protocol_id),
        capture_wall_time_s=(
            min(float(row["timestamp_s"]) for row in event_rows)
            if protocol_id in {PROTOCOL_V2_ID, PROTOCOL_ID}
            else None
        ),
    )
    evidence["clock_anchor"] = clock_anchor
    evidence["clock_anchor_resolved"] = True
    if evidence["status"] != "valid":
        raise AssertionError(evidence["reasons"])
    _SELF_CONSISTENT_CALIBRATIONS[cache_key] = (evidence, raw, events)
    return json.loads(json.dumps(evidence)), raw, events


class SelfConsistentCalibrationTests(unittest.TestCase):
    def test_clock_anchor_resolves_around_every_cadence_boundary(self) -> None:
        base_ns = 1_790_000_000_000_000_000
        cadence_ns = 100_000_000
        offsets_us = (0, -65, 65, -130, 130, -200, 200)

        # Pulse fitting is orthogonal to this regression and expensive. Keep
        # the real plist serialization, parsing, and clock-anchor derivation
        # for every phase while replacing only the downstream evidence work.
        with patch(
            "joulewise.powermetrics_fiducial.rederive_detection_from_artifacts",
            return_value={},
        ), patch(
            "joulewise.powermetrics_fiducial.instrument_evidence",
            return_value={"status": "valid", "reasons": []},
        ):
            for boundary_index in range(10):
                for offset_us in offsets_us:
                    with self.subTest(
                        boundary_index=boundary_index,
                        offset_us=offset_us,
                    ):
                        first_endpoint_ns = (
                            base_ns
                            + boundary_index * cadence_ns
                            + offset_us * 1_000
                        )
                        evidence, _raw, _events = self_consistent_calibration(
                            first_endpoint_s=(
                                first_endpoint_ns / 1_000_000_000
                            )
                        )
                        self.assertNotEqual(
                            evidence["clock_anchor"]["status"], "unknown"
                        )
                        self.assertTrue(evidence["clock_anchor_resolved"])


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
    def _digest_bound_raw_bundle(self, run_id: str) -> BundleBuilder:
        builder = self.builder(run_id=run_id)
        builder.measured_window(100.0, 110.0)
        builder.write_trace(
            constant_samples(100.0, 110.0, hz=1.0, power_w=7.5)
        )
        builder._writer.write_raw("powermetrics.plist", b"captured bytes\x00")
        builder.write_metadata(rail_manifest=["mock"])
        return builder

    def test_mutated_raw_capture_refuses_before_reduction(self) -> None:
        builder = self._digest_bound_raw_bundle("raw-byte-mutation")
        raw_path = builder.path / "raw" / "powermetrics.plist"
        mutated = bytearray(raw_path.read_bytes())
        mutated[0] ^= 0x01
        raw_path.write_bytes(mutated)

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("raw_capture_digest_mismatch", summary.failure_message)

    def test_successor_bundle_without_raw_digest_map_refuses(self) -> None:
        builder = self._digest_bound_raw_bundle("successor-map-missing")
        metadata_path = builder.path / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        del metadata["raw_sha256"]
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertIn("raw_capture_digest_missing", summary.failure_message)

    def test_legacy_bundle_without_raw_digest_map_remains_readable(self) -> None:
        builder = self._digest_bound_raw_bundle("legacy-map-absent")
        metadata_path = builder.path / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        del metadata["raw_sha256"]
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        (builder.path / "summary_metrics.json").write_text(
            json.dumps(
                {
                    "summary_provenance": {
                        "reducer_version": (
                            reduce_module.POINT_ANCHOR_FROZEN_REDUCER_VERSION
                        )
                    }
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )

        summary = reduce_module.reduce_bundle(
            builder.path,
            reducer_version=reduce_module.REDUCER_VERSION,
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)

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

    def test_negative_rail_power_is_claim_ineligible(self) -> None:
        # Nonnegative power is the premise for independent-edge monotonicity;
        # pre-fix code integrated a negative rail and left the energy eligible.
        builder = self.builder()
        builder.measured_window(100.0, 110.0)
        builder.write_trace(
            constant_samples(100.0, 110.0, hz=1.0, power_w=-1.0)
        )
        builder.write_metadata(rail_manifest=["mock"])

        summary = reduce_module.reduce_bundle(builder.path)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIn(
            "negative_power_sample",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )
        self.assertFalse(
            summary.window_evidence_precheck["gross_request"]["eligible"]
        )

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
                "reasons": ["token_count_stream_chunk_fallback"],
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
            metadata["raw_sha256"] = {
                path.relative_to(bundle_path).as_posix(): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in sorted((bundle_path / "raw").iterdir())
                if path.is_file()
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

    def test_current_corner_integrals_are_epoch_translation_invariant(self) -> None:
        # G7(c) defect shape: adding a 2026-scale epoch changed a 50 us corner
        # excursion by several microjoules because (epoch + delta) was rounded
        # before association with the window endpoint.  Current-wire corner
        # math must integrate in anchor-relative coordinates.
        from joulewise.bundle_read import Window
        from joulewise.reduce import _corner_composed_anchor_shift_envelope

        def envelope(origin_s: float):
            curve = self.interval_curve(
                [
                    (origin_s, origin_s + 0.5, 0.0),
                    (origin_s + 0.5, origin_s + 1.0, 100.0),
                    (origin_s + 1.0, origin_s + 1.5, 0.0),
                ]
            )
            return _corner_composed_anchor_shift_envelope(
                [(curve, [Window(origin_s + 0.5, origin_s + 1.25)])],
                0.00005,
                0.0,
            )

        relative = envelope(0.0)
        epoch = envelope(1_784_490_850.0)
        self.assertIsNotNone(relative)
        self.assertIsNotNone(epoch)
        for field in ("point_j", "lower_j", "upper_j", "max_abs_delta_j"):
            self.assertAlmostEqual(epoch[field], relative[field], places=12)

    def test_clock_step_span_adds_independent_opposite_edge_shift_bound(self) -> None:
        # F14 audit reproduction: two 100 W supports touch opposite request
        # edges.  A common +/-4 ms translation leaves their summed 0.8 J
        # overlap unchanged, while a piecewise wall-clock step can move the
        # two edges in opposite directions for a 1.6 J energy excursion.
        from joulewise.bundle_read import Window
        from joulewise.reduce import _anchor_shift_envelope

        curve = self.interval_curve(
            [(0.0, 1.004, 100.0), (3.996, 5.0, 100.0)]
        )
        envelope = _anchor_shift_envelope(
            [(curve, [Window(1.0, 2.0), Window(3.0, 4.0)])],
            0.0,
            independent_edge_span_s=0.004,
        )
        self.assertIsNotNone(envelope)
        self.assertAlmostEqual(envelope["point_j"], 0.8, places=9)
        self.assertGreaterEqual(envelope["independent_edge_shift_bound_j"], 1.6)
        self.assertGreaterEqual(envelope["max_abs_delta_j"], 1.6)

    def test_flat_power_independent_edges_restore_two_p_b_excursion(self) -> None:
        # Pre-fix reproduction: a common translation cannot change the energy
        # of a flat trace, but independent start=-B/stop=+B expands the window
        # by 2B and attains an additional 2*P*B joules.
        from joulewise.bundle_read import Window
        from joulewise.reduce import (
            _anchor_shift_envelope,
            _corner_composed_anchor_shift_envelope,
        )

        power_w = 10.0
        b_fiducial_s = 0.1
        curve = self.interval_curve([(-1.0, 2.0, power_w)])
        contributions = [(curve, [Window(0.2, 0.8)])]
        old = _anchor_shift_envelope(contributions, b_fiducial_s)
        repaired = _corner_composed_anchor_shift_envelope(
            contributions, 0.0, b_fiducial_s
        )
        attainable_j = old["point_j"] + 2.0 * power_w * b_fiducial_s

        self.assertLess(old["upper_j"], attainable_j)
        self.assertAlmostEqual(repaired["upper_j"], attainable_j, places=12)
        self.assertEqual(
            repaired["method"],
            "common_trace_shift_plus_independent_edge_corners_v3",
        )

    def test_wall_minus_monotonic_span_widens_corner_edges(self) -> None:
        # Lead delta-review regression: the wall-minus-monotonic span is an
        # independent per-edge clock error like the fiducial lag; a corner
        # envelope that only RECORDS it under-covers by 2*P*span on a flat
        # trace. The repaired corners evaluate at +/-(B_fiducial + span).
        from joulewise.bundle_read import Window
        from joulewise.reduce import _corner_composed_anchor_shift_envelope

        power_w = 10.0
        b_fiducial_s = 0.1
        span_s = 0.05
        curve = self.interval_curve([(-1.0, 2.0, power_w)])
        contributions = [(curve, [Window(0.2, 0.8)])]
        without_span = _corner_composed_anchor_shift_envelope(
            contributions, 0.0, b_fiducial_s
        )
        with_span = _corner_composed_anchor_shift_envelope(
            contributions, 0.0, b_fiducial_s, span_s
        )
        attainable_j = (
            without_span["point_j"]
            + 2.0 * power_w * (b_fiducial_s + span_s)
        )

        self.assertLess(without_span["upper_j"], attainable_j)
        self.assertAlmostEqual(with_span["upper_j"], attainable_j, places=12)
        self.assertAlmostEqual(
            with_span["anchor_bound_s"], b_fiducial_s + span_s, places=12
        )
        self.assertAlmostEqual(
            with_span["wall_minus_monotonic_independent_edge_span_s"],
            span_s,
            places=12,
        )

    def test_idle_subtracted_envelope_widens_for_duration_variation(self) -> None:
        # Delta re-audit P1 regression: idle subtraction removes
        # P_idle * duration, and independent edges change the duration by up
        # to 2*edge_bound; pure translation of the gross envelope under-covers
        # whenever window-edge power < idle mean power. The translated
        # envelope must widen by 2 * edge_bound * P_idle.
        from joulewise.reduce import _translate_envelope

        gross = {
            "method": "m",
            "anchor_bound_s": 0.1,
            "point_j": 10.0,
            "lower_j": 9.0,
            "upper_j": 11.0,
            "max_abs_delta_j": 1.0,
        }
        p_idle_w = 5.0
        edge_bound_s = 0.1
        duration_s = 2.0
        widen_j = 2.0 * edge_bound_s * p_idle_w
        translated = _translate_envelope(
            gross, -p_idle_w * duration_s, widen_j
        )
        self.assertAlmostEqual(translated["point_j"], 0.0, places=12)
        self.assertAlmostEqual(translated["lower_j"], -1.0 - widen_j, places=12)
        self.assertAlmostEqual(translated["upper_j"], 1.0 + widen_j, places=12)
        self.assertAlmostEqual(
            translated["max_abs_delta_j"], 1.0 + widen_j, places=12
        )

    def test_neg8_shaped_independent_edge_energy_is_licensed(self) -> None:
        # NEG-8 audit numbers: 38.8307 J is attainable while the collapsed
        # common-shift license stopped at 38.5743 J.
        from joulewise.bundle_read import Window
        from joulewise.reduce import (
            _anchor_shift_envelope,
            _corner_composed_anchor_shift_envelope,
        )

        curve = self.interval_curve([(-1.0, 6.0, 10.0)])
        window = Window(0.5, 4.35743)
        contributions = [(curve, [window])]
        b_fiducial_s = 0.01282
        old = _anchor_shift_envelope(contributions, 0.0)
        repaired = _corner_composed_anchor_shift_envelope(
            contributions, 0.0, b_fiducial_s
        )

        self.assertAlmostEqual(old["upper_j"], 38.5743, places=9)
        self.assertLess(old["upper_j"], 38.8307)
        self.assertGreaterEqual(repaired["upper_j"], 38.8307 - 1e-12)

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

    def test_suite_item_block_level_envelopes_are_emitted(self) -> None:
        from joulewise.bundle_read import Window
        from joulewise.reduce import _energy_anchor_envelopes_v05

        # A wide interval-support curve so every suite window stays covered
        # under +-bound_s.
        curve = self.interval_curve(
            [(-0.5 + 0.1 * i, -0.4 + 0.1 * i, 10.0) for i in range(20)]
        )
        envelopes = _energy_anchor_envelopes_v05(
            curve=curve,
            window=Window(0.0, 1.0),
            phase_windows={},
            idle_baseline=None,
            total_tokens=None,
            output_token_count=None,
            bound_s=0.05,
            item_windows=[("0:itemA", Window(0.0, 0.5))],
            block_windows={"blk1": [Window(0.0, 0.5)]},
            level_windows={"blk1/lvl1": [Window(0.0, 0.5)]},
        )
        self.assertIn("/suite_item_energy_j/0:itemA", envelopes)
        self.assertIn("/suite_block_energy_j/blk1", envelopes)
        # The level key's "/" is JSON-Pointer escaped to "~1".
        self.assertIn("/suite_level_energy_j/blk1~1lvl1", envelopes)

    def test_resolved_anchor_gates_suite_item_block_level_energy(self) -> None:
        # Regression: before the fix, the RESOLVED branch of
        # _apply_anchor_claim_gates never touched item/block/level gates, so a
        # granular gross-energy claim could stay eligible with no anchor-shift
        # envelope recorded. Every suite gate must now be enveloped or barred.
        from joulewise.reduce import _AnchorContext, _apply_anchor_claim_gates

        anchor_ctx = _AnchorContext(
            telemetry_is_powermetrics=True,
            unresolved=False,
            bound_s=0.05,
            curve=None,
            anchor_epoch_s=0.0,
            bundle_bound_s=0.05,
            fiducial_bound_s=None,
            detail=None,
        )
        prechecks = {
            "gross_request": {"eligible": True, "reasons": []},
            "idle_subtracted_request": {"eligible": True, "reasons": []},
            "item": {"0:itemA": {"eligible": True, "reasons": []}},
            "block": {"blk1": {"eligible": True, "reasons": []}},
            "level": {"blk1/lvl1": {"eligible": True, "reasons": []}},
        }
        envelopes = {
            "/gross_energy_j": {
                "point_j": 10.0,
                "lower_j": 9.9,
                "upper_j": 10.1,
            },
            # item envelope stays within 25% -> eligible
            "/suite_item_energy_j/0:itemA": {
                "point_j": 4.0,
                "lower_j": 3.9,
                "upper_j": 4.1,
            },
            # block envelope deviates > 25% of its own point energy
            "/suite_block_energy_j/blk1": {
                "point_j": 4.0,
                "lower_j": 1.0,
                "upper_j": 7.0,
            },
            # no level pointer at all -> unrecorded fail-closed
        }
        _apply_anchor_claim_gates(
            prechecks,
            anchor_ctx,
            envelopes,
            gross_pointer="/gross_energy_j",
            request_joint_bound_j=0.0,
        )
        self.assertTrue(prechecks["item"]["0:itemA"]["eligible"])
        self.assertEqual(prechecks["item"]["0:itemA"]["reasons"], [])
        self.assertFalse(prechecks["block"]["blk1"]["eligible"])
        self.assertIn(
            "anchor_energy_envelope_exceeds_quarter_metric",
            prechecks["block"]["blk1"]["reasons"],
        )
        self.assertFalse(prechecks["level"]["blk1/lvl1"]["eligible"])
        self.assertIn(
            "anchor_energy_envelope_unrecorded",
            prechecks["level"]["blk1/lvl1"]["reasons"],
        )

    def test_current_anchor_barrier_stamps_inner_rollup_windows(self) -> None:
        from joulewise.reduce import _AnchorContext, _apply_anchor_claim_gates

        anchor_ctx = _AnchorContext(
            telemetry_is_powermetrics=True,
            unresolved=True,
            bound_s=None,
            curve=None,
            anchor_epoch_s=None,
            bundle_bound_s=None,
            fiducial_bound_s=None,
            detail="instrument_calibration_invalid",
        )
        prechecks = {
            "gross_request": {"eligible": True, "reasons": []},
            "phase": {
                "decode": {
                    "eligible": True,
                    "reasons": [],
                    "windows": [{"eligible": True, "reasons": []}],
                }
            },
            "block": {
                "b": {
                    "eligible": True,
                    "reasons": [],
                    "windows": [{"eligible": True, "reasons": []}],
                }
            },
            "level": {
                "b/l": {
                    "eligible": True,
                    "reasons": [],
                    "windows": [{"eligible": True, "reasons": []}],
                }
            },
        }
        _apply_anchor_claim_gates(
            prechecks,
            anchor_ctx,
            {},
            gross_pointer="/gross_energy_j",
            request_joint_bound_j=0.0,
            include_inner_windows=True,
        )

        for group in ("phase", "block", "level"):
            rollup = next(iter(prechecks[group].values()))
            self.assertFalse(rollup["windows"][0]["eligible"])
            self.assertIn(
                "clock_anchor_unresolved", rollup["windows"][0]["reasons"]
            )


class D078R01RegressionTests(unittest.TestCase):
    """Sealed-evidence regressions for the D-078 anchor correction."""

    FIXTURE = REPO_ROOT / "tests" / "fixtures" / "d078_r01"
    RAW_SHA256 = "cb25bfddc13610150795732a44be1183c154dcc4990b857425943028fd8edf81"

    @staticmethod
    def _claim_gates() -> dict:
        return {
            name: {"eligible": True, "reasons": []}
            for name in (
                "gross_request",
                "gross_batch_group",
                "idle_subtracted_request",
            )
        }

    @staticmethod
    def _clean_environment_admission() -> dict:
        return {
            "schema_version": "joulewise.environment_admission.v1",
            "critical_environment_passed": True,
            "reference_provenance_present": True,
            "per_run_environment_evaluation": {
                "schema_version": "joulewise.environment_evaluation.v1",
                "eligible": True,
                "snapshot_sha256": "ab" * 32,
            },
            "decision": "admitted",
            "claim_reason": None,
            "attempts": [
                {
                    "attempt": 1,
                    "start_s": 1.0,
                    "end_s": 2.0,
                    "admitted": True,
                    "cpu_admission_enforced": True,
                    "cpu_admission": {"admitted": True},
                }
            ],
            "guard_observations": [
                {
                    "phase": phase,
                    "capture_skipped": False,
                    "display_power_state": "all_asleep",
                    "screensaver_engaged": False,
                    "errors": {},
                }
                for phase in ("before_attempt_1", "after_attempt_1")
            ],
        }

    def test_contradictory_environment_object_is_fail_closed(self) -> None:
        from joulewise.environment_admission import environment_admission_refusals

        contradictory = self._clean_environment_admission()
        contradictory["critical_environment_passed"] = False
        contradictory["reference_provenance_present"] = False
        contradictory["per_run_environment_evaluation"]["eligible"] = False

        self.assertTrue(environment_admission_refusals(contradictory))
        self.assertIn(
            "environment_admission_failed",
            environment_admission_refusals(contradictory),
        )

    def test_current_admission_recomputes_snapshot_instead_of_trusting_eligible_true(self) -> None:
        # H3(b) exact defect: the stored decision and hashes used to be trusted
        # even after the embedded snapshot changed to an ineligible state.
        from joulewise.environment import evaluate_environment_policy
        from joulewise.environment_admission import (
            _recomputed_environment_evaluation_refusals,
        )
        from joulewise.schemas import CampaignPolicy

        policy_path = REPO_ROOT / "configs/campaign_policies/quiet_mac_p2_production.json"
        raw = policy_path.read_bytes()
        policy = CampaignPolicy.from_mapping(json.loads(raw))
        snapshot = {
            "power_source": "AC Power",
            "power": {"external_connected": True},
            "low_power_mode": False,
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "thermal_pressure": "nominal",
        }
        stored = evaluate_environment_policy(snapshot, policy.environment_guard)
        stored["snapshot"] = json.loads(json.dumps(snapshot))
        metadata = {
            "campaign_policy": {"sha256": hashlib.sha256(raw).hexdigest()},
            "environment_admission": {
                "per_run_environment_evaluation": stored,
            },
        }
        self.assertEqual(_recomputed_environment_evaluation_refusals(metadata), ())
        metadata["environment_admission"]["per_run_environment_evaluation"][
            "snapshot"
        ]["thermal_pressure"] = "elevated"
        self.assertEqual(
            _recomputed_environment_evaluation_refusals(metadata),
            ("environment_admission_failed",),
        )

    def test_current_thermal_scan_refuses_elevated_or_missing_interval_pressure(self) -> None:
        # H3(a) exact defects: nominal endpoint snapshots used to hide an
        # elevated per-interval record, while a missing record did not fail
        # closed as absent window-enforced environment evidence.
        from types import SimpleNamespace
        from joulewise.environment_admission import _window_thermal_pressure_refusals

        def record(end_s: float, pressure):
            return SimpleNamespace(
                timestamp_s=end_s,
                elapsed_ns=1_000_000_000,
                thermal_pressure=pressure,
            )

        from joulewise.uncertainty_evidence import CLOCK_METHOD_V2

        metadata = {
            "environment_admission": {
                "attempts": [{"attempt": 1, "start_s": 0.0, "end_s": 1.0}]
            },
            "uncertainty_evidence": {
                "clock_anchor": {
                    "method": CLOCK_METHOD_V2,
                    "clock_stamps": {"x": {}},
                }
            },
        }
        for label, pressure, expected in (
            (
                "elevated",
                "Elevated",
                ("thermal_pressure_elevated_in_window",),
            ),
            ("missing", None, ("environment_admission_missing",)),
        ):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp)
                (bundle / "raw").mkdir()
                (bundle / "raw/powermetrics_idle.plist").write_bytes(b"idle")
                (bundle / "raw/powermetrics.plist").write_bytes(b"measured")
                with (
                    patch(
                        "joulewise.adapters.powermetrics.parse_powermetrics_records",
                        side_effect=[
                            [record(1.0, "Nominal")],
                            [record(2.0, "Nominal")],
                            [record(2.0, "Nominal"), record(3.0, pressure)],
                        ],
                    ),
                    patch(
                        "joulewise.adapters.powermetrics.anchor_records_from_powermetrics",
                        return_value=[],
                    ),
                    patch(
                        "joulewise.environment_admission.stamp_from_mapping",
                        create=True,
                    ),
                    patch(
                        "joulewise.uncertainty_evidence.stamp_from_mapping",
                        return_value=object(),
                    ),
                    patch(
                        "joulewise.uncertainty_evidence.resolve_anchor_reconstructor",
                        return_value=lambda **_kwargs: {
                            "status": "bounded",
                            "first_sample_end_point_epoch_s": 2.0,
                        },
                    ),
                ):
                    reasons = _window_thermal_pressure_refusals(
                        metadata,
                        bundle_path=bundle,
                        measured_window_start_s=2.0,
                        measured_window_end_s=3.0,
                    )
            self.assertEqual(reasons, expected)

    def test_environment_schema_and_guard_structure_are_fail_closed(self) -> None:
        from joulewise.environment_admission import environment_admission_refusals

        cases = {}
        wrong_schema = self._clean_environment_admission()
        wrong_schema["schema_version"] = "joulewise.environment_admission.v0"
        cases["admission_schema"] = wrong_schema
        wrong_evaluation = self._clean_environment_admission()
        wrong_evaluation["per_run_environment_evaluation"]["schema_version"] = (
            "joulewise.environment_evaluation.v0"
        )
        cases["evaluation_schema"] = wrong_evaluation
        missing_guards = self._clean_environment_admission()
        missing_guards["guard_observations"] = []
        cases["missing_guards"] = missing_guards
        malformed_guard = self._clean_environment_admission()
        malformed_guard["guard_observations"][0]["screensaver_engaged"] = "false"
        cases["malformed_guard"] = malformed_guard

        for label, admission in cases.items():
            with self.subTest(label=label):
                self.assertTrue(environment_admission_refusals(admission))

    def test_current_attempt_timing_rejects_missing_overlap_and_nonmonotonic_rows(
        self,
    ) -> None:
        # F7 defect shape: ordinals were contiguous but the declared physical
        # attempt windows could overlap, run backwards, or be absent.  Frozen
        # replay keeps the pre-timing default; current-mint validation opts in.
        from joulewise.environment_admission import environment_admission_refusals

        missing = self._clean_environment_admission()
        missing["attempts"][0].pop("start_s")
        missing["attempts"][0].pop("end_s")
        self.assertEqual(environment_admission_refusals(missing), ())
        self.assertEqual(
            environment_admission_refusals(
                missing, require_attempt_timing=True
            ),
            ("environment_admission_missing",),
        )

        for label, windows in (
            ("overlap", ((1.0, 3.0), (2.0, 4.0))),
            ("reversed", ((3.0, 2.0),)),
            ("nonmonotonic", ((4.0, 5.0), (1.0, 2.0))),
        ):
            admission = self._clean_environment_admission()
            template = admission["attempts"][0]
            admission["attempts"] = [
                {
                    **template,
                    "attempt": index,
                    "start_s": start_s,
                    "end_s": end_s,
                }
                for index, (start_s, end_s) in enumerate(windows, start=1)
            ]
            admission["guard_observations"] = [
                {
                    "phase": phase,
                    "capture_skipped": False,
                    "display_power_state": "all_asleep",
                    "screensaver_engaged": False,
                    "errors": {},
                }
                for index in range(1, len(windows) + 1)
                for phase in (f"before_attempt_{index}", f"after_attempt_{index}")
            ]
            with self.subTest(label=label):
                self.assertEqual(
                    environment_admission_refusals(
                        admission, require_attempt_timing=True
                    ),
                    ("environment_admission_missing",),
                )

        boundary = self._clean_environment_admission()
        template = boundary["attempts"][0]
        boundary["attempts"] = [
            {**template, "attempt": 1, "start_s": 1.0, "end_s": 2.0},
            {**template, "attempt": 2, "start_s": 2.0, "end_s": 3.0},
        ]
        boundary["guard_observations"] = [
            {
                "phase": phase,
                "capture_skipped": False,
                "display_power_state": "all_asleep",
                "screensaver_engaged": False,
                "errors": {},
            }
            for phase in (
                "before_attempt_1",
                "after_attempt_1",
                "before_attempt_2",
                "after_attempt_2",
            )
        ]
        self.assertEqual(
            environment_admission_refusals(
                boundary, require_attempt_timing=True
            ),
            (),
        )

    def test_current_admission_is_causally_bound_to_epoch_measured_window(self) -> None:
        # G2 exact repro: a tiny synthetic-looking admission [1,2] and post
        # observation at 3 must not admit an epoch-scale measured window.
        from joulewise.environment_admission import current_environment_refusals

        metadata = {
            "environment_admission": self._clean_environment_admission(),
            "environment": {
                "post_run_observation": {
                    "capture_skipped": False,
                    "captured_at_s": 3.0,
                    "display_power_state": "all_asleep",
                    "screensaver_engaged": False,
                    "errors": {},
                }
            },
        }
        metadata["environment_admission"]["attempts"][0]["baseline"] = {
            "duration_s": 1.0
        }
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            (bundle / "rich_telemetry_idle.jsonl").write_text(
                json.dumps({"timestamp_s": 1.5, "elapsed_ns": 500_000_000})
                + "\n",
                encoding="utf-8",
            )
            reasons = current_environment_refusals(
                metadata,
                bundle_path=bundle,
                measured_window_start_s=1_784_490_850.0,
                measured_window_end_s=1_784_490_851.0,
            )
        self.assertIn("environment_admission_missing", reasons)

    def test_current_admission_gap_overlap_and_post_bracket_fail_independently(self) -> None:
        from joulewise.bundle_read import BundleReader
        from joulewise.environment_admission import current_environment_refusals
        from tests.test_p2038_production_path import P2038ProductionPathTests

        with tempfile.TemporaryDirectory() as tmp:
            bundle, summary = P2038ProductionPathTests().run_mode(Path(tmp), "normal")
            self.assertEqual(summary.status, RunStatus.SUCCEEDED)
            reader = BundleReader(bundle)
            measured_window = reader.measured_window()
            self.assertIsNotNone(measured_window)
            assert measured_window is not None
            clean_metadata = reader.metadata()
            clean_attempt = clean_metadata["environment_admission"]["attempts"][0]
            attempt_span_s = clean_attempt["end_s"] - clean_attempt["start_s"]
            cases = (
                ("gap_over_600s", "gap", True),
                ("attempt_overlaps_measurement", "overlap", True),
                ("post_observation_precedes_end", "post", True),
                ("coherent_bracket", "clean", False),
            )
            for label, mutation, expected_missing in cases:
                metadata = json.loads(json.dumps(clean_metadata))
                attempt = metadata["environment_admission"]["attempts"][0]
                if mutation == "gap":
                    attempt["end_s"] = measured_window.start_s - 600.5
                    attempt["start_s"] = attempt["end_s"] - attempt_span_s
                elif mutation == "overlap":
                    attempt["end_s"] = measured_window.start_s + 0.1
                    attempt["start_s"] = attempt["end_s"] - attempt_span_s
                elif mutation == "post":
                    metadata["environment"]["post_run_observation"][
                        "captured_at_s"
                    ] = measured_window.end_s - 0.1
                with self.subTest(label=label):
                    # The p2038 v3 fixture binds a local test policy rather
                    # than a checked-in campaign policy.  Keep this regression
                    # focused on causal admission timing and the stored-method
                    # thermal scan; recomputed-policy custody has its own test.
                    with patch(
                        "joulewise.environment_admission."
                        "_recomputed_environment_evaluation_refusals",
                        return_value=(),
                    ):
                        reasons = current_environment_refusals(
                            metadata,
                            bundle_path=bundle,
                            measured_window_start_s=measured_window.start_s,
                            measured_window_end_s=measured_window.end_s,
                        )
                    self.assertEqual(
                        "environment_admission_missing" in reasons,
                        expected_missing,
                    )

    def test_current_attempt_window_must_contain_idle_capture_evidence(self) -> None:
        # G5 defect shapes are independent: a one-second attempt cannot claim
        # a two-second baseline, and endpoint-stamped rich-idle evidence must
        # not sit outside the attempt it is attributed to.
        from joulewise.environment_admission import current_environment_refusals

        clean_metadata = {
            "environment_admission": self._clean_environment_admission(),
            "environment": {
                "post_run_observation": {
                    "capture_skipped": False,
                    "captured_at_s": 11.0,
                    "display_power_state": "all_asleep",
                    "screensaver_engaged": False,
                    "errors": {},
                }
            },
        }
        for label, duration_s, endpoint_s, expected_missing in (
            ("baseline_longer_than_attempt", 2.0, 8.5, True),
            ("capture_outside_attempt", 0.5, 7.5, True),
            ("coherent_endpoint_capture", 0.5, 8.5, False),
        ):
            metadata = json.loads(json.dumps(clean_metadata))
            metadata["environment_admission"]["attempts"][0].update(
                {
                    "start_s": 8.0,
                    "end_s": 9.0,
                    "baseline": {"duration_s": duration_s},
                }
            )
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp)
                (bundle / "rich_telemetry_idle.jsonl").write_text(
                    json.dumps(
                        {"timestamp_s": endpoint_s, "elapsed_ns": 500_000_000}
                    )
                    + "\n",
                    encoding="utf-8",
                )
                with (
                    patch(
                        "joulewise.environment_admission._recomputed_environment_evaluation_refusals",
                        return_value=(),
                    ),
                    patch(
                        "joulewise.environment_admission._window_thermal_pressure_refusals",
                        return_value=(),
                    ),
                ):
                    reasons = current_environment_refusals(
                        metadata,
                        bundle_path=bundle,
                        measured_window_start_s=10.0,
                        measured_window_end_s=10.5,
                    )
            self.assertEqual(
                "environment_admission_missing" in reasons,
                expected_missing,
            )

    def test_post_run_critical_environment_failure_bars_claim(self) -> None:
        metadata = {
            "adapters": {"telemetry": {"name": "powermetrics"}},
            "environment_admission": self._clean_environment_admission(),
            "environment": {
                "post_run_observation": {
                    "capture_skipped": False,
                    "display_power_state": "all_asleep",
                    "screensaver_engaged": False,
                    "errors": {},
                }
            },
        }
        self.assertEqual(reduce_module._environment_claim_reasons(metadata), [])
        metadata["environment"]["post_run_observation"][
            "display_power_state"
        ] = "any_awake"
        self.assertIn(
            "environment_admission_failed",
            reduce_module._environment_claim_reasons(metadata),
        )

    def test_environment_claim_reason_channel_is_closed_and_decision_bound(self) -> None:
        # F1 exact defect: the misspelling on a flagged decision used to return
        # no reason; the inverse contradiction minted a refusal on admitted.
        cases = (
            ("flagged", "environment_admisson_failed"),
            ("flagged", None),
            ("admitted", "environment_admission_failed"),
        )
        for decision, claim_reason in cases:
            with self.subTest(decision=decision, claim_reason=claim_reason):
                gates = self._claim_gates()
                reduce_module._apply_environment_claim_barrier(
                    gates,
                    {
                        "adapters": {"telemetry": {"name": "mock"}},
                        "environment_admission": {
                            **self._clean_environment_admission(),
                            "decision": decision,
                            "claim_reason": claim_reason,
                        }
                    },
                )
                for gate in gates.values():
                    self.assertFalse(gate["eligible"])
                    self.assertIn("environment_admission_failed", gate["reasons"])

        clean = self._claim_gates()
        reduce_module._apply_environment_claim_barrier(
            clean,
            {
                "adapters": {"telemetry": {"name": "mock"}},
                "environment_admission": self._clean_environment_admission(),
            },
        )
        self.assertTrue(all(gate["eligible"] for gate in clean.values()))

    def test_cpu_admission_ledger_shape_and_top_decision_are_fail_closed(self) -> None:
        # F8 exact reproduced ledgers: every malformed shape must stamp all
        # three claim gates, while a single clean row remains admitted.
        clean_row = {
            "attempt": 1,
            "start_s": 1.0,
            "end_s": 2.0,
            "admitted": True,
            "cpu_admission_enforced": True,
            "cpu_admission": {"admitted": True},
        }
        cases = (
            ([clean_row, {**clean_row, "attempt": 1}], "admitted"),
            ([{**clean_row, "attempt": 2}, clean_row], "admitted"),
            ([clean_row], "failed"),
            ([{key: value for key, value in clean_row.items() if key != "cpu_admission_enforced"}], "admitted"),
        )
        for attempts, decision in cases:
            with self.subTest(attempts=attempts, decision=decision):
                gates = self._claim_gates()
                reduce_module._apply_cpu_admission_claim_barrier(
                    gates,
                    {
                        "adapters": {"telemetry": {"name": "powermetrics"}},
                        "environment_admission": {
                            **self._clean_environment_admission(),
                            "decision": decision,
                            "attempts": attempts,
                        },
                    },
                )
                for gate in gates.values():
                    self.assertFalse(gate["eligible"])
                    self.assertTrue(gate["reasons"])

        gates = self._claim_gates()
        reduce_module._apply_cpu_admission_claim_barrier(
            gates,
            {
                "adapters": {"telemetry": {"name": "powermetrics"}},
                "environment_admission": self._clean_environment_admission(),
            },
        )
        self.assertTrue(all(gate["eligible"] for gate in gates.values()))

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
            gross["method"], "common_trace_shift_plus_independent_edge_span_v2"
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
        context = _derive_anchor_context(
            reader, reader.metadata(), reducer_version="0.5.1"
        )
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
        self.assertIn("instrument_calibration_missing", gate["reasons"])

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
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
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
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
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
            # Frozen 0.5.1 replay pins this EXACT unresolved-anchor reason set;
            # in particular the envelope-gate stamp must never reach an
            # unresolved context (lost-early-return regression, 2026-07-21
            # delta re-audit).
            self.assertEqual(
                summary.window_evidence_precheck["gross_request"]["reasons"],
                [
                    "cadence_ratio_below_threshold",
                    "clock_anchor_unresolved",
                    "clock_bound_exceeds_quarter_window",
                    "environment_admission_missing",
                ],
            )
            self.assertNotIn(
                "anchor_energy_envelope_unrecorded",
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

    def test_051_missing_cpu_admission_record_is_claim_ineligible(self) -> None:
        summary = reduce_module.reduce_bundle(self.FIXTURE, reducer_version="0.5.1")
        reasons = summary.window_evidence_precheck["gross_request"]["reasons"]
        self.assertIn("environment_admission_missing", reasons)

    def test_051_explicit_cpu_admission_bypass_is_claim_ineligible(self) -> None:
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            shutil.copytree(self.FIXTURE, bundle)
            metadata_path = bundle / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            final = metadata["environment_admission"]["attempts"][-1]
            final["cpu_admission"] = {"admitted": True, "decision": "admitted"}
            final["cpu_admission_enforced"] = False
            metadata_path.write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n"
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            self.assertIn(
                "cpu_admission_unenforced",
                summary.window_evidence_precheck["gross_request"]["reasons"],
            )

    @staticmethod
    def _valid_instrument_evidence(**overrides) -> dict:
        from joulewise.powermetrics_fiducial import (
            MAX_AGE_S,
            PROTOCOL_ID,
            PROTOCOL_V2_ID,
            PROTOCOL_V2_SHA256,
            PROTOCOL_V3_SHA256,
            RESIDUAL_REGION_METHOD,
        )

        protocol_id = overrides.pop("protocol_id", PROTOCOL_V2_ID)
        anchor_method = overrides.pop("anchor_method", ACTIVE_CAPTURE_ANCHOR_METHOD)
        first_endpoint_s = overrides.pop("first_endpoint_s", None)
        evidence, _raw, calibration_events = self_consistent_calibration(
            protocol_id=protocol_id if protocol_id == PROTOCOL_ID else None,
            anchor_method=anchor_method,
            first_endpoint_s=first_endpoint_s,
        )
        if protocol_id in {PROTOCOL_V2_ID, PROTOCOL_ID}:
            event_rows = [
                json.loads(line) for line in calibration_events.splitlines()
            ]
            evidence["protocol_id"] = protocol_id
            evidence["capture_wall_time_s"] = min(
                float(row["timestamp_s"]) for row in event_rows
            )
            evidence["max_age_s"] = MAX_AGE_S
            evidence["bindings"].update(
                {
                    "pulse_protocol_id": protocol_id,
                    "estimator_revision": RESIDUAL_REGION_METHOD,
                    "protocol_sha256": (
                        PROTOCOL_V2_SHA256
                        if protocol_id == PROTOCOL_V2_ID
                        else PROTOCOL_V3_SHA256
                    ),
                }
            )
        bindings_override = overrides.pop("bindings", None)
        evidence.update(overrides)
        if bindings_override:
            evidence["bindings"] = {**evidence["bindings"], **bindings_override}
        canonical = json.dumps(
            evidence["bindings"], sort_keys=True, separators=(",", ":")
        ).encode()
        evidence["binding_evidence"] = {
            "schema_version": "joulewise.instrument_binding_evidence.v1",
            "binding_vector_sha256": hashlib.sha256(canonical).hexdigest(),
            "powermetrics_binary": {
                "path": "/usr/bin/powermetrics",
                "sha256": evidence["bindings"]["powermetrics_sha256"],
            },
            "power_policy": {"id": evidence["bindings"]["power_policy"]},
        }
        return evidence

    @staticmethod
    def _replay_era(evidence: dict) -> dict:
        """Rebind evidence to the frozen 5093355-era protocol identity.

        The 0.5.1/0.6.1 replay arms expect the protocol_v2.json bytes current
        at their mint; a current-era artifact legitimately mismatches them.
        """

        from joulewise.powermetrics_fiducial import REPLAY_PROTOCOL_V2_SHA256

        evidence = json.loads(json.dumps(evidence))
        evidence["bindings"]["protocol_sha256"] = REPLAY_PROTOCOL_V2_SHA256
        evidence["binding_evidence"]["binding_vector_sha256"] = hashlib.sha256(
            json.dumps(
                evidence["bindings"], sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        return evidence

    def _bundle_with_calibration(
        self,
        tmp,
        *,
        evidence,
        b_fiducial_s=None,
        mutate_bytes=None,
        calibration_events_override=None,
        measurement_fixture: Path | None = None,
    ) -> Path:
        import shutil

        bundle = Path(tmp) / "bundle"
        shutil.copytree(measurement_fixture or self.FIXTURE, bundle)
        evidence = json.loads(json.dumps(evidence))
        evidence_protocol_id = evidence.get("protocol_id")
        calibration_first_endpoint_s = None
        capture_wall_time_s = evidence.get("capture_wall_time_s")
        if (
            evidence_protocol_id in {
                "powermetrics_pulse_fiducial_v2",
                "powermetrics_pulse_fiducial_v3",
            }
            and isinstance(capture_wall_time_s, int | float)
            and not isinstance(capture_wall_time_s, bool)
        ):
            # ``self_consistent_calibration`` records its first command at
            # first_endpoint + 1.95 s.  Rebuild its primary bytes at the
            # evidence's declared epoch so a dynamic v3 measuring fixture
            # cannot carry a stale but internally inconsistent calibration.
            calibration_first_endpoint_s = float(capture_wall_time_s) - 1.95
        _canonical_evidence, calibration_raw, calibration_events = (
            self_consistent_calibration(
                protocol_id=(
                    evidence_protocol_id
                    if evidence_protocol_id
                    == "powermetrics_pulse_fiducial_v3"
                    else None
                ),
                first_endpoint_s=calibration_first_endpoint_s,
            )
        )
        if calibration_events_override is not None:
            calibration_events = calibration_events_override
        artifact_dir = bundle / "calibration"
        (artifact_dir / "raw").mkdir(parents=True)
        (artifact_dir / "raw" / "powermetrics.plist").write_bytes(
            calibration_raw
        )
        (artifact_dir / "events.jsonl").write_bytes(calibration_events)
        calibration_trace = (
            b"timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
        )
        (artifact_dir / "power_trace.csv").write_bytes(calibration_trace)
        hashes = evidence.get("artifact_sha256")
        if isinstance(hashes, dict) and set(
            ("raw/powermetrics.plist", "events.jsonl")
        ).issubset(hashes):
            hashes["raw/powermetrics.plist"] = hashlib.sha256(
                calibration_raw
            ).hexdigest()
            hashes["events.jsonl"] = hashlib.sha256(
                calibration_events
            ).hexdigest()
        raw = (
            json.dumps(evidence, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        artifact_file = artifact_dir / "instrument_evidence.json"
        artifact_file.write_bytes(raw)
        artifact_sha256 = hashlib.sha256(raw).hexdigest()
        if mutate_bytes is not None:
            artifact_file.write_bytes(mutate_bytes)
        manifest = {
            "schema_version": "joulewise.instrument_validation_manifest.v1",
            "validation_id": evidence.get("validation_id"),
            "protocol_id": evidence.get("protocol_id"),
            "pulse_count": evidence.get("pulse_count"),
            "artifacts": {
                "events.jsonl": hashlib.sha256(calibration_events).hexdigest(),
                "power_trace.csv": hashlib.sha256(calibration_trace).hexdigest(),
                "instrument_evidence.json": hashlib.sha256(
                    artifact_file.read_bytes()
                ).hexdigest(),
                "raw/powermetrics.plist": hashlib.sha256(
                    calibration_raw
                ).hexdigest(),
            },
        }
        manifest_raw = (
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        (artifact_dir / "manifest.json").write_bytes(manifest_raw)
        if (
            evidence.get("protocol_id") == "powermetrics_pulse_fiducial_v2"
            and isinstance(evidence.get("capture_wall_time_s"), int | float)
        ):
            events_path = bundle / "events.jsonl"
            rows = [json.loads(line) for line in events_path.read_text().splitlines()]
            run_started = next(
                row for row in rows if row["event_type"] == "run_started"
            )
            capture_s = float(evidence["capture_wall_time_s"])
            if not capture_s <= float(run_started["timestamp_s"]) <= (
                capture_s + 86400.0
            ):
                # Relabel-fresh tests deliberately move the declaration while
                # keeping primary calibration bytes fixed.  Preserve the old
                # attack shape by moving only the declared measuring start.
                run_started["timestamp_s"] = capture_s + 1.0
                events_path.write_text(
                    "".join(json.dumps(row) + "\n" for row in rows),
                    encoding="utf-8",
                )
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata.setdefault("device", {})["powermetrics"] = {
            "executable_path": "/usr/bin/powermetrics",
            "executable_sha256": evidence.get("bindings", {}).get(
                "powermetrics_sha256"
            )
        }
        metadata["instrument_calibration"] = {
            "artifact_path": "calibration/instrument_evidence.json",
            "artifact_sha256": artifact_sha256,
            "validation_manifest_path": "calibration/manifest.json",
            "validation_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "b_fiducial_s": (
                evidence.get("b_fiducial_s")
                if b_fiducial_s is None
                else b_fiducial_s
            ),
            "bindings": evidence.get("bindings"),
            "binding_observations": {
                "powermetrics_sha256": evidence.get("bindings", {}).get(
                    "powermetrics_sha256"
                ),
                "power_policy": evidence.get("bindings", {}).get("power_policy"),
            },
        }
        (bundle / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n"
        )
        return bundle

    def _v3_measurement_bundle_with_calibration(
        self,
        tmp: str,
        *,
        calibration_age_s: float,
    ) -> Path:
        """Attach a calibration to a real current-era production fixture."""

        from joulewise.bundle_read import BundleReader
        from joulewise.powermetrics_fiducial import MAX_AGE_S
        from joulewise.uncertainty_evidence import (
            CLOCK_METHOD_V3,
            SCHEMA_VERSION_V3,
        )
        from tests.test_p2038_production_path import P2038ProductionPathTests

        root = Path(tmp)
        measurement, source_summary = P2038ProductionPathTests().run_mode(
            root / "v3-measurement-source", "normal"
        )
        self.assertEqual(source_summary.status, RunStatus.SUCCEEDED)
        source_reader = BundleReader(measurement)
        source_metadata = source_reader.metadata()
        source_window = source_reader.measured_window()
        self.assertIsNotNone(source_window)
        uncertainty = source_metadata["uncertainty_evidence"]
        self.assertEqual(uncertainty["schema_version"], SCHEMA_VERSION_V3)
        self.assertEqual(
            uncertainty["clock_anchor"]["method"], CLOCK_METHOD_V3
        )
        calibration_first_endpoint_s = source_window.start_s - calibration_age_s
        self.assertLess(
            calibration_first_endpoint_s + 1.95,
            source_window.start_s - MAX_AGE_S,
        )
        device = source_metadata["device"]
        snapshot = source_metadata["campaign_environment_preflight"]["snapshot"]
        power_hz = source_reader.raw_config()["sampling"]["power_hz"]
        evidence = self._valid_instrument_evidence(
            first_endpoint_s=calibration_first_endpoint_s,
            bindings={
                "hardware_model": device["hw_model"],
                "os_build": device["kern_osversion"],
                "sampling_interval_ms": 1000.0 / power_hz,
                "mlx_version": snapshot["python_packages"]["mlx"]["version"],
            },
        )
        return self._bundle_with_calibration(
            root / "v3-calibration",
            evidence=evidence,
            measurement_fixture=measurement,
        )

    def test_051_fiducial_bound_widens_effective_bound(self) -> None:
        from joulewise.bundle_read import BundleReader

        evidence = self._replay_era(self._valid_instrument_evidence())
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(
                tmp, evidence=evidence
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            reader = BundleReader(bundle)
            context = reduce_module._derive_anchor_context(
                reader,
                reader.metadata(),
                reducer_version="0.5.1",
                strict_calibration=False,
            )
            gross = summary.energy_anchor_shift_envelopes["/gross_energy_j"]
            self.assertEqual(context.fiducial_bound_s, evidence["b_fiducial_s"])
            self.assertEqual(
                gross["anchor_bound_s"],
                max(context.bundle_bound_s, context.fiducial_bound_s),
            )
            self.assertEqual(
                summary.window_evidence_precheck["gross_request"][
                    "clock_anchor_bound_s"
                ],
                gross["anchor_bound_s"],
            )

    def test_052_causal_bounds_add_while_frozen_replay_uses_max(self) -> None:
        from joulewise.bundle_read import BundleReader

        evidence = self._valid_instrument_evidence()
        # One bundle per era: each arm's binding expectation is pinned to the
        # protocol_v2.json bytes current at its mint, so no single artifact
        # can satisfy both.
        with tempfile.TemporaryDirectory() as tmp:
            replay_bundle = self._bundle_with_calibration(
                tmp, evidence=self._replay_era(evidence)
            )
            replay = reduce_module.reduce_bundle(
                replay_bundle, reducer_version="0.5.1"
            )
            replay_reader = BundleReader(replay_bundle)
            replay_context = reduce_module._derive_anchor_context(
                replay_reader,
                replay_reader.metadata(),
                reducer_version="0.5.1",
                strict_calibration=False,
            )
        with tempfile.TemporaryDirectory() as tmp:
            mint_bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            mint = reduce_module.reduce_bundle(
                mint_bundle, reducer_version="0.5.2"
            )
            mint_reader = BundleReader(mint_bundle)
            mint_context = reduce_module._derive_anchor_context(
                mint_reader,
                mint_reader.metadata(),
                reducer_version="0.5.2",
            )
        bundle_bound = replay_context.bundle_bound_s
        fiducial_bound = replay_context.fiducial_bound_s
        self.assertIsNotNone(bundle_bound)
        self.assertIsNotNone(fiducial_bound)
        self.assertEqual(replay_context.bound_s, max(bundle_bound, fiducial_bound))
        self.assertEqual(
            mint_context.bound_s,
            bundle_bound + fiducial_bound + mint_context.edge_span_s,
        )
        self.assertEqual(
            replay.energy_anchor_shift_envelopes["/gross_energy_j"]["anchor_bound_s"],
            replay_context.bound_s,
        )
        self.assertEqual(
            mint.energy_anchor_shift_envelopes["/gross_energy_j"]["anchor_bound_s"],
            mint_context.bound_s,
        )
        for version, expected in (
            ("0.6.1", max(bundle_bound, fiducial_bound)),
            ("0.6.2", bundle_bound + fiducial_bound),
        ):
            with self.subTest(version=version):
                self.assertEqual(
                    reduce_module._compose_causal_anchor_bound_s(
                        bundle_bound,
                        fiducial_bound,
                        reducer_version=version,
                    ),
                    expected,
                )

    def test_052_four_b_license_refuses_case_accepted_by_051_max(self) -> None:
        evidence = self._valid_instrument_evidence()

        def shortened(bundle: Path) -> Path:
            events_path = bundle / "events.jsonl"
            rows = [
                json.loads(line) for line in events_path.read_text().splitlines()
            ]
            started = next(
                row for row in rows if row["event_type"] == "sampling_started"
            )
            stopped = next(
                row for row in rows if row["event_type"] == "sampling_stopped"
            )
            stopped["timestamp_s"] = started["timestamp_s"] + 0.3
            events_path.write_text(
                "".join(json.dumps(row) + "\n" for row in rows),
                encoding="utf-8",
            )
            return bundle

        # Era-matched bundles: each arm's binding expectation is pinned to
        # the protocol_v2.json bytes current at its mint.
        with tempfile.TemporaryDirectory() as tmp:
            replay = reduce_module.reduce_bundle(
                shortened(
                    self._bundle_with_calibration(
                        tmp, evidence=self._replay_era(evidence)
                    )
                ),
                reducer_version="0.5.1",
            )
        with tempfile.TemporaryDirectory() as tmp:
            mint = reduce_module.reduce_bundle(
                shortened(self._bundle_with_calibration(tmp, evidence=evidence)),
                reducer_version="0.5.2",
            )
        replay_gate = replay.window_evidence_precheck["gross_request"]
        mint_gate = mint.window_evidence_precheck["gross_request"]
        self.assertNotIn("clock_bound_exceeds_quarter_window", replay_gate["reasons"])
        self.assertIn("clock_bound_exceeds_quarter_window", mint_gate["reasons"])

    def test_052_post_window_trace_tail_shorter_than_composed_bound_refuses(self) -> None:
        # R4 defect shape: the causal envelope needs trace support after the
        # measured stop.  A current mint must not claim through a short tail,
        # while the frozen 0.5.1 replay wire remains byte-semantics compatible.
        import shutil
        from joulewise.bundle_read import BundleReader

        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            shutil.copytree(self.FIXTURE, bundle)
            reader = BundleReader(bundle)
            original = reduce_module._derive_anchor_context(
                reader, reader.metadata(), reducer_version="0.5.2"
            )
            self.assertIsNotNone(original.curve)
            self.assertIsNotNone(original.bound_s)
            short_stop_s = original.curve[-1].support_end_s - original.bound_s / 2
            events_path = bundle / "events.jsonl"
            rows = [json.loads(line) for line in events_path.read_text().splitlines()]
            stopped = next(row for row in rows if row["event_type"] == "sampling_stopped")
            stopped["timestamp_s"] = short_stop_s
            events_path.write_text(
                "".join(json.dumps(row) + "\n" for row in rows),
                encoding="utf-8",
            )
            replay = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            mint = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        reason = "post_window_trace_tail_shorter_than_anchor_bound"
        self.assertNotIn(
            reason, replay.window_evidence_precheck["gross_request"]["reasons"]
        )
        self.assertIn(
            reason, mint.window_evidence_precheck["gross_request"]["reasons"]
        )

    def test_052_post_window_tail_exact_epoch_equality_is_inclusive(self) -> None:
        # F8c defect shape: subtracting epoch-valued floats first could make
        # an exact composed-bound tail appear fractionally short.
        import shutil
        from joulewise.bundle_read import BundleReader

        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            shutil.copytree(self.FIXTURE, bundle)
            reader = BundleReader(bundle)
            context = reduce_module._derive_anchor_context(
                reader, reader.metadata(), reducer_version="0.5.2"
            )
            assert context.curve is not None and context.bound_s is not None
            trace_end_s = context.curve[-1].support_end_s
            exact_stop_s = trace_end_s - context.bound_s
            events_path = bundle / "events.jsonl"
            rows = [json.loads(line) for line in events_path.read_text().splitlines()]
            stopped = next(
                row for row in rows if row["event_type"] == "sampling_stopped"
            )
            stopped["timestamp_s"] = exact_stop_s
            events_path.write_text(
                "".join(json.dumps(row) + "\n" for row in rows),
                encoding="utf-8",
            )
            equal = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")

            stopped["timestamp_s"] = exact_stop_s + 4.0 * math.ulp(exact_stop_s)
            events_path.write_text(
                "".join(json.dumps(row) + "\n" for row in rows),
                encoding="utf-8",
            )
            short = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")

        reason = "post_window_trace_tail_shorter_than_anchor_bound"
        self.assertNotIn(
            reason, equal.window_evidence_precheck["gross_request"]["reasons"]
        )
        self.assertIn(
            reason, short.window_evidence_precheck["gross_request"]["reasons"]
        )

    def test_051_forged_zero_residual_calibration_is_physically_rejected(self) -> None:
        # F2 exact exploit: valid hashes plus forty hand-authored detected rows,
        # zero residuals, and B=0 used to pass without fitting the raw bytes.
        evidence = self._valid_instrument_evidence(b_fiducial_s=0.0)
        for pulse in evidence["pulses"]:
            for field in (
                "onset_residual_lower_s",
                "onset_residual_upper_s",
                "offset_residual_lower_s",
                "offset_residual_upper_s",
            ):
                pulse[field] = 0.0
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(
                tmp, evidence=evidence, b_fiducial_s=0.0
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_051_freshly_wider_bound_cannot_be_shrunk_by_declaration(self) -> None:
        from joulewise.bundle_read import BundleReader

        # The old live artifact shape can declare the fit/event residual bound
        # without the newly added capture-anchor component. Structural rows
        # remain valid, but downstream must consume the freshly wider bound.
        evidence = self._valid_instrument_evidence()
        fresh_bound = evidence["b_fiducial_s"]
        declared = max(
            abs(float(pulse[field]))
            for pulse in evidence["pulses"]
            for field in (
                "onset_residual_lower_s",
                "onset_residual_upper_s",
                "offset_residual_lower_s",
                "offset_residual_upper_s",
            )
        )
        self.assertLess(declared, fresh_bound)
        evidence["b_fiducial_s"] = declared
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(
                tmp, evidence=evidence, b_fiducial_s=declared
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
            reader = BundleReader(bundle)
            context = reduce_module._derive_anchor_context(
                reader, reader.metadata(), reducer_version="0.5.2"
            )
        gross = summary.energy_anchor_shift_envelopes["/gross_energy_j"]
        self.assertAlmostEqual(context.fiducial_bound_s, fresh_bound, places=12)
        self.assertAlmostEqual(
            gross["anchor_bound_s"],
            context.bundle_bound_s + fresh_bound + context.edge_span_s,
            places=12,
        )
        self.assertAlmostEqual(gross["anchor_bound_s"], context.bound_s, places=12)

    def test_051_conservatively_wider_declared_bound_remains_valid(self) -> None:
        from joulewise.bundle_read import BundleReader

        evidence = self._valid_instrument_evidence()
        evidence["b_fiducial_s"] += 0.05
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
            reader = BundleReader(bundle)
            context = reduce_module._derive_anchor_context(
                reader,
                reader.metadata(),
                reducer_version="0.5.2",
            )
        self.assertEqual(
            summary.energy_anchor_shift_envelopes["/gross_energy_j"][
                "anchor_bound_s"
            ],
            context.bundle_bound_s
            + evidence["b_fiducial_s"]
            + context.edge_span_s,
        )

    def test_052_missing_max_age_refuses_invalid_v2_shape(self) -> None:
        # F6: max_age_s is authenticated v2 protocol shape.  Omitting it is
        # invalid evidence, distinct from a well-shaped artifact that is old.
        evidence = self._valid_instrument_evidence()
        del evidence["max_age_s"]
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_051_replay_ignores_custody_manifest_and_keeps_frozen_protocol_sha(
        self,
    ) -> None:
        # Delta re-audit P0 regression: the custody-manifest gate and the
        # re-keyed PROTOCOL_V2_SHA256 are current-mint (0.5.2/0.6.2) gates.
        # A manifest-less bundle whose bindings carry the 5093355-era
        # protocol sha must keep its committed 0.5.1 replay disposition
        # (anchor resolved), and the same bundle must refuse under 0.5.2.
        from joulewise.powermetrics_fiducial import REPLAY_PROTOCOL_V2_SHA256

        evidence = self._valid_instrument_evidence()
        evidence["bindings"]["protocol_sha256"] = REPLAY_PROTOCOL_V2_SHA256
        evidence["binding_evidence"]["binding_vector_sha256"] = hashlib.sha256(
            json.dumps(
                evidence["bindings"], sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            (bundle / "calibration" / "manifest.json").unlink()
            metadata = json.loads((bundle / "metadata.json").read_text())
            del metadata["instrument_calibration"]["validation_manifest_path"]
            del metadata["instrument_calibration"]["validation_manifest_sha256"]
            (bundle / "metadata.json").write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n"
            )
            replay = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            mint = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        replay_reasons = replay.window_evidence_precheck["gross_request"]["reasons"]
        self.assertNotIn("clock_anchor_unresolved", replay_reasons)
        self.assertNotIn("instrument_calibration_invalid", replay_reasons)
        mint_reasons = mint.window_evidence_precheck["gross_request"]["reasons"]
        self.assertIn("instrument_calibration_invalid", mint_reasons)

    def test_051_unregistered_instrument_reason_spelling_refuses(self) -> None:
        # F5 exact defect: a status=valid artifact with an unknown diagnostic
        # spelling formerly survived reducer consumption.
        evidence = self._valid_instrument_evidence(
            reasons=["pulse_detecton_incomplete"]
        )
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_052_valid_status_with_registered_reason_refuses(self) -> None:
        # A known diagnostic is still incompatible with status=valid.  The
        # vocabulary check must not turn a physically adverse reason into an
        # accepted calibration merely because its spelling is registered.
        evidence = self._valid_instrument_evidence(
            reasons=["pulse_detection_incomplete"]
        )
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_052_valid_status_with_any_per_pulse_reason_refuses(self) -> None:
        for reason in ("pulse_detecton_incomplete", "pulse_detection_incomplete"):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as tmp:
                evidence = self._valid_instrument_evidence()
                evidence["pulses"][0]["reasons"] = [reason]
                bundle = self._bundle_with_calibration(tmp, evidence=evidence)
                summary = reduce_module.reduce_bundle(
                    bundle, reducer_version="0.5.2"
                )
                self.assertIn(
                    "instrument_calibration_invalid",
                    summary.window_evidence_precheck["gross_request"]["reasons"],
                )

    def test_052_environment_attacks_refuse_through_reducer_path(self) -> None:
        clean_row = {
            "attempt": 1,
            "start_s": 1.0,
            "end_s": 2.0,
            "admitted": True,
            "cpu_admission_enforced": True,
            "cpu_admission": {"admitted": True},
        }
        cases = {
            "flagged_typo": {
                "decision": "flagged",
                "claim_reason": "environment_admisson_failed",
                "attempts": [{**clean_row, "admitted": False}],
            },
            "flagged_null": {
                "decision": "flagged",
                "claim_reason": None,
                "attempts": [{**clean_row, "admitted": False}],
            },
            "duplicate": {
                "decision": "admitted",
                "claim_reason": None,
                "attempts": [clean_row, clean_row],
            },
            "reordered": {
                "decision": "admitted",
                "claim_reason": None,
                "attempts": [{**clean_row, "attempt": 2}, clean_row],
            },
            "cpu_unenforced": {
                "decision": "admitted",
                "claim_reason": None,
                "attempts": [
                    {
                        key: value
                        for key, value in clean_row.items()
                        if key != "cpu_admission_enforced"
                    }
                ],
            },
        }
        import shutil

        for label, admission in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp) / "bundle"
                shutil.copytree(self.FIXTURE, bundle)
                metadata_path = bundle / "metadata.json"
                metadata = json.loads(metadata_path.read_text())
                metadata["environment_admission"] = admission
                metadata_path.write_text(
                    json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                summary = reduce_module.reduce_bundle(
                    bundle, reducer_version="0.5.2"
                )
                reasons = summary.window_evidence_precheck["gross_request"][
                    "reasons"
                ]
                self.assertTrue(reasons)
                if label == "cpu_unenforced":
                    self.assertIn("cpu_admission_unenforced", reasons)
                else:
                    self.assertTrue(
                        {"environment_admission_failed", "environment_admission_missing"}
                        & set(reasons)
                    )

    def test_051_self_asserted_fiducial_without_artifact_fails_closed(self) -> None:
        # Regression for the exact defect: a bundle supplying a b_fiducial_s and
        # a 64-hex artifact_sha256 but NO real artifact must NOT suppress the
        # fiducial floor - it fails closed instead of trusting the scalar.
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bundle"
            shutil.copytree(self.FIXTURE, bundle)
            metadata = json.loads((bundle / "metadata.json").read_text())
            metadata["instrument_calibration"] = {
                "artifact_path": "instrument_evidence.json",
                "b_fiducial_s": 0.0,
                "artifact_sha256": "ab" * 32,
            }
            (bundle / "metadata.json").write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n"
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            self.assertIn(
                "clock_anchor_unresolved",
                summary.window_evidence_precheck["gross_request"]["reasons"],
            )

    def test_051_calibration_artifact_hash_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(
                tmp,
                evidence=self._valid_instrument_evidence(),
                mutate_bytes=b'{"schema_version": "tampered"}\n',
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            self.assertIn(
                "clock_anchor_unresolved",
                summary.window_evidence_precheck["gross_request"]["reasons"],
            )

    def test_052_calibration_manifest_path_traversal_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(
                tmp, evidence=self._valid_instrument_evidence()
            )
            metadata_path = bundle / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["instrument_calibration"]["validation_manifest_path"] = (
                "../../outside-or-missing"
            )
            metadata_path.write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n"
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_052_deleted_manifest_member_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(
                tmp, evidence=self._valid_instrument_evidence()
            )
            (bundle / "calibration" / "power_trace.csv").unlink()
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_052_calibration_age_horizon_is_inclusive_and_then_stale(self) -> None:
        from joulewise.powermetrics_fiducial import MAX_AGE_S

        evidence = self._valid_instrument_evidence()
        capture_s = evidence["capture_wall_time_s"]
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            events_path = bundle / "events.jsonl"
            rows = [json.loads(line) for line in events_path.read_text().splitlines()]
            started = next(row for row in rows if row["event_type"] == "run_started")
            stopped = next(
                row for row in rows if row["event_type"] == "sampling_stopped"
            )
            started["timestamp_s"] = capture_s + 1.0
            stopped["timestamp_s"] = capture_s + MAX_AGE_S
            events_path.write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )
            boundary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
            stopped["timestamp_s"] = capture_s + MAX_AGE_S + 0.001
            events_path.write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )
            stale = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        self.assertNotIn(
            "instrument_calibration_stale",
            boundary.window_evidence_precheck["gross_request"]["reasons"],
        )
        self.assertIn(
            "instrument_calibration_stale",
            stale.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_052_v3_relabelled_capture_time_refuses_its_own_taxonomy(self) -> None:
        """F1: re-hashing a relabelled time cannot masquerade as staleness."""

        from joulewise.powermetrics_fiducial import MAX_AGE_S

        def reduced_reasons(*, relabel_capture_time: bool) -> list[str]:
            with tempfile.TemporaryDirectory() as tmp:
                bundle = self._v3_measurement_bundle_with_calibration(
                    tmp,
                    calibration_age_s=MAX_AGE_S + 100.0,
                )
                if relabel_capture_time:
                    # The adversary changes only the declared evidence time,
                    # then re-hashes the evidence and its custody manifest.
                    # The immutable calibration events retain the true epoch.
                    evidence_path = bundle / "calibration" / "instrument_evidence.json"
                    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
                    evidence["capture_wall_time_s"] += 10_000_000.0
                    evidence_raw = (
                        json.dumps(evidence, indent=2, sort_keys=True) + "\n"
                    ).encode("utf-8")
                    evidence_path.write_bytes(evidence_raw)
                    manifest_path = bundle / "calibration" / "manifest.json"
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    manifest["artifacts"]["instrument_evidence.json"] = (
                        hashlib.sha256(evidence_raw).hexdigest()
                    )
                    manifest_raw = (
                        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
                    ).encode("utf-8")
                    manifest_path.write_bytes(manifest_raw)
                    metadata_path = bundle / "metadata.json"
                    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                    metadata["instrument_calibration"].update(
                        {
                            "artifact_sha256": hashlib.sha256(evidence_raw).hexdigest(),
                            "validation_manifest_sha256": hashlib.sha256(
                                manifest_raw
                            ).hexdigest(),
                        }
                    )
                    metadata_path.write_text(
                        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
                return summary.window_evidence_precheck["gross_request"]["reasons"]

        attacked = reduced_reasons(relabel_capture_time=True)
        control = reduced_reasons(relabel_capture_time=False)
        self.assertIn("instrument_calibration_capture_time_mismatch", attacked)
        self.assertNotIn("instrument_calibration_stale", attacked)
        # Removing the one attack line restores the honest stale-horizon arm,
        # so this assertion cannot pass merely because all v3 calibrations
        # are stale in this deliberately aged fixture.
        self.assertIn("instrument_calibration_stale", control)
        self.assertNotIn("instrument_calibration_capture_time_mismatch", control)

    def test_052_v3_measurement_stale_calibration_still_refuses_stale(self) -> None:
        """A p2-038.3 bundle with only an expired calibration keeps the stale pin."""

        from joulewise.bundle_read import BundleReader
        from joulewise.powermetrics_fiducial import MAX_AGE_S

        with tempfile.TemporaryDirectory() as tmp:
            source_root = Path(tmp) / "v3-measurement-source"
            # Give the otherwise valid v3 calibration one complete freshness
            # horizon of age without changing its bytes, bindings, or era.
            bundle = self._v3_measurement_bundle_with_calibration(
                tmp,
                calibration_age_s=MAX_AGE_S + 100.0,
            )
            reader = BundleReader(bundle)
            source_window = BundleReader(
                source_root / "p2038-production-shaped"
            ).measured_window()
            self.assertIsNotNone(source_window)
            artifact = json.loads(
                (bundle / "calibration" / "instrument_evidence.json").read_text()
            )
            self.assertGreater(
                source_window.start_s - artifact["capture_wall_time_s"], MAX_AGE_S
            )
            bound, detail = reduce_module._verify_instrument_calibration(
                reader,
                reader.metadata(),
                reader.metadata()["instrument_calibration"],
                strict_physics=True,
            )
            self.assertIsNone(bound)
            self.assertEqual(detail, "instrument_calibration_stale")
            # The p2038 fixture uses a local policy.  Keep this probe about the
            # calibration horizon rather than its independent policy custody.
            with (
                patch(
                    "joulewise.reduce.current_environment_refusals",
                    return_value=(),
                ),
                patch(
                    "joulewise.reduce.environment_admission_refusals",
                    return_value=(),
                ),
            ):
                summary = reduce_module.reduce_bundle(
                    bundle, reducer_version="0.5.2"
                )
        self.assertIn(
            "instrument_calibration_stale",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_052_shifted_event_clock_cannot_relabel_calibration_fresh(self) -> None:
        # L1 exact defect: moving every top-level event time authenticated a
        # fresh capture while the embedded ClockStamp epochs (and raw physics)
        # stayed fixed. Rehashing the otherwise-valid bytes must still refuse.
        evidence = self._valid_instrument_evidence()
        _source, _raw, calibration_events = self_consistent_calibration()
        shifted_rows = [
            json.loads(line) for line in calibration_events.splitlines()
        ]
        for row in shifted_rows:
            row["timestamp_s"] += 100_000.0
        shifted_events = "".join(
            json.dumps(row, sort_keys=True) + "\n" for row in shifted_rows
        ).encode("utf-8")
        evidence["capture_wall_time_s"] += 100_000.0
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(
                tmp,
                evidence=evidence,
                calibration_events_override=shifted_events,
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_052_command_clockstamp_physical_defects_are_invalid(self) -> None:
        evidence = self._valid_instrument_evidence()
        _source, _raw, calibration_events = self_consistent_calibration()
        for defect in ("negative_resolution", "reversed_monotonic_bracket"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as tmp:
                rows = [
                    json.loads(line) for line in calibration_events.splitlines()
                ]
                stamp = rows[0]["metadata"]["clock_stamp"]
                if defect == "negative_resolution":
                    stamp["wall_resolution_s"] = -1e-6
                else:
                    stamp["monotonic_after_s"] = (
                        stamp["monotonic_before_s"] - 1e-6
                    )
                mutated_events = "".join(
                    json.dumps(row, sort_keys=True) + "\n" for row in rows
                ).encode("utf-8")
                bundle = self._bundle_with_calibration(
                    tmp,
                    evidence=evidence,
                    calibration_events_override=mutated_events,
                )
                summary = reduce_module.reduce_bundle(
                    bundle, reducer_version="0.5.2"
                )
                reasons = summary.window_evidence_precheck["gross_request"][
                    "reasons"
                ]
                self.assertIn("instrument_calibration_invalid", reasons)

    def test_052_oversized_command_clock_values_are_invalid_not_stale(self) -> None:
        evidence = self._valid_instrument_evidence()
        _source, _raw, calibration_events = self_consistent_calibration()
        for defect in ("timestamp_s", "embedded_epoch_s"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as tmp:
                rows = [
                    json.loads(line) for line in calibration_events.splitlines()
                ]
                if defect == "timestamp_s":
                    rows[0]["timestamp_s"] = 10**400
                else:
                    rows[0]["metadata"]["clock_stamp"]["epoch_s"] = 10**400
                mutated_events = "".join(
                    json.dumps(row, sort_keys=True) + "\n" for row in rows
                ).encode("utf-8")
                bundle = self._bundle_with_calibration(
                    tmp,
                    evidence=evidence,
                    calibration_events_override=mutated_events,
                )
                summary = reduce_module.reduce_bundle(
                    bundle, reducer_version="0.5.2"
                )
                reasons = summary.window_evidence_precheck["gross_request"][
                    "reasons"
                ]
                self.assertIn("instrument_calibration_invalid", reasons)
                self.assertNotIn("instrument_calibration_stale", reasons)

    def test_052_relabelled_v1_body_as_v2_refuses_protocol_shape(self) -> None:
        # F6 defect shape: protocol_id and bindings were re-keyed to v2 while
        # the body retained the legacy residual-region shape.
        from joulewise.powermetrics_fiducial import (
            MAX_AGE_S,
            PROTOCOL_V2_ID,
            PROTOCOL_V2_SHA256,
            RESIDUAL_REGION_METHOD,
            capture_wall_time_from_events,
        )

        evidence = self._valid_instrument_evidence(
            protocol_id="powermetrics_pulse_fiducial_v1"
        )
        _source, _raw, calibration_events = self_consistent_calibration()
        evidence["protocol_id"] = PROTOCOL_V2_ID
        evidence["capture_wall_time_s"] = capture_wall_time_from_events(
            calibration_events
        )
        evidence["max_age_s"] = MAX_AGE_S
        evidence["bindings"].update(
            {
                "pulse_protocol_id": PROTOCOL_V2_ID,
                "estimator_revision": RESIDUAL_REGION_METHOD,
                "protocol_sha256": PROTOCOL_V2_SHA256,
            }
        )
        for field in (
            "residual_region_method",
            "residual_region_coverage_assumption",
            "residual_region_coverage_resolution_s",
        ):
            evidence.pop(field, None)
        canonical = json.dumps(
            evidence["bindings"], sort_keys=True, separators=(",", ":")
        ).encode()
        evidence["binding_evidence"] = {
            "schema_version": "joulewise.instrument_binding_evidence.v1",
            "binding_vector_sha256": hashlib.sha256(canonical).hexdigest(),
            "powermetrics_binary": {
                "path": "/usr/bin/powermetrics",
                "sha256": evidence["bindings"]["powermetrics_sha256"],
            },
            "power_policy": {"id": evidence["bindings"]["power_policy"]},
        }
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_052_current_claim_refuses_v1_calibration_artifact(self) -> None:
        from joulewise.powermetrics_fiducial import LEGACY_PROTOCOL_ID

        evidence = self._valid_instrument_evidence(protocol_id=LEGACY_PROTOCOL_ID)
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_051_frozen_replay_does_not_learn_protocol_v3(self) -> None:
        # H1 frozen-arm drift guard: adding the prospective v3 identity to the
        # current strict path must not expand the 0.5.1 replay accept set.
        from joulewise.powermetrics_fiducial import PROTOCOL_ID

        evidence = self._valid_instrument_evidence(protocol_id=PROTOCOL_ID)
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_052_missing_capture_time_refuses_invalid_v2_shape(self) -> None:
        evidence = self._valid_instrument_evidence()
        del evidence["capture_wall_time_s"]
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.2")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_051_calibration_bound_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # Metadata scalar disagrees with the artifact's own b_fiducial_s.
            bundle = self._bundle_with_calibration(
                tmp,
                evidence=self._valid_instrument_evidence(b_fiducial_s=0.08),
                b_fiducial_s=0.20,
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            self.assertIn(
                "clock_anchor_unresolved",
                summary.window_evidence_precheck["gross_request"]["reasons"],
            )

    def test_051_calibration_binding_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(
                tmp,
                evidence=self._valid_instrument_evidence(
                    bindings={"hardware_model": "Mac16,1"}
                ),
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            self.assertIn(
                "clock_anchor_unresolved",
                summary.window_evidence_precheck["gross_request"]["reasons"],
            )
            self.assertIn(
                "instrument_calibration_mismatch",
                summary.window_evidence_precheck["gross_request"]["reasons"],
            )

    def test_051_every_declared_calibration_binding_is_enforced(self) -> None:
        # W2 defect shape: pre-fix only hardware/OS/anchor were compared, so
        # changing any of these five fields still admitted the calibration.
        for field, changed in (
            ("powermetrics_sha256", "ff" * 32),
            ("sampling_interval_ms", 200),
            ("mlx_version", "999.0"),
            ("pulse_protocol_id", "wrong-protocol"),
            ("power_policy", "battery-low-power"),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                evidence = self._valid_instrument_evidence()
                bundle = self._bundle_with_calibration(tmp, evidence=evidence)
                metadata_path = bundle / "metadata.json"
                metadata = json.loads(metadata_path.read_text())
                metadata["instrument_calibration"]["bindings"][field] = changed
                metadata_path.write_text(
                    json.dumps(metadata, indent=2, sort_keys=True) + "\n"
                )
                summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
                self.assertIn(
                    "instrument_calibration_mismatch",
                    summary.window_evidence_precheck["gross_request"]["reasons"],
                )

    def test_051_forged_valid_status_cannot_bypass_pulse_predicate(self) -> None:
        # W2 defect shape: status='valid' was trusted despite impossible pulse
        # evidence.  Each internal predicate violation now maps to invalid.
        mutations = (
            lambda value: value.update(pulse_count=0, pulses=[]),
            lambda value: value.update(all_pulses_detected=False),
            lambda value: value.update(spurious_plateau_count=1),
            lambda value: value.update(pulses=[]),
            lambda value: value.update(artifact_sha256={}),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(mutation=index), tempfile.TemporaryDirectory() as tmp:
                evidence = self._valid_instrument_evidence()
                mutate(evidence)
                bundle = self._bundle_with_calibration(tmp, evidence=evidence)
                summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
                self.assertIn(
                    "instrument_calibration_invalid",
                    summary.window_evidence_precheck["gross_request"]["reasons"],
                )

    def test_051_detected_only_pulses_without_residual_intervals_refuse(self) -> None:
        # F1 defect shape: forty detected bits, plausible hashes, and B=0 used
        # to return a trusted zero bound despite containing no timing evidence.
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._valid_instrument_evidence(b_fiducial_s=0.0)
            evidence["pulses"] = [
                {"pulse_index": index, "detected": True} for index in range(40)
            ]
            bundle = self._bundle_with_calibration(
                tmp, evidence=evidence, b_fiducial_s=0.0
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
        self.assertIn(
            "instrument_calibration_invalid",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_051_invalid_status_calibration_artifact_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(
                tmp,
                evidence=self._valid_instrument_evidence(status="invalid"),
            )
            summary = reduce_module.reduce_bundle(bundle, reducer_version="0.5.1")
            self.assertIn(
                "clock_anchor_unresolved",
                summary.window_evidence_precheck["gross_request"]["reasons"],
            )

    def test_051_golden_summary(self) -> None:
        golden_path = REPO_ROOT / "tests" / "goldens" / "d078_r01_reducer_051.json"
        summary_object = reduce_module.reduce_bundle(
            self.FIXTURE, reducer_version="0.5.1"
        )
        summary = summary_object.to_dict()
        self.assertEqual(summary, json.loads(golden_path.read_text()))
        self.assertEqual(
            (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode(),
            golden_path.read_bytes(),
        )

    def test_052_golden_mints_strict_semantics_without_changing_physics(self) -> None:
        golden_path = REPO_ROOT / "tests" / "goldens" / "d078_r01_reducer_052.json"
        summary = reduce_module.reduce_bundle(
            self.FIXTURE, reducer_version="0.5.2"
        )
        payload = summary.to_dict()
        self.assertEqual(
            (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode(),
            golden_path.read_bytes(),
        )
        self.assertAlmostEqual(payload["gross_energy_j"], 7.664158853340149)
        gross = payload["energy_anchor_shift_envelopes"]["/gross_energy_j"]
        # Independently recomputed with Decimal interval overlaps after one
        # shared epoch subtraction: point=7.664158853340148765..., lower=
        # 6.765501506995912139..., upper=7.682118047887086708....
        self.assertAlmostEqual(gross["lower_j"], 6.7655015069959115)
        self.assertAlmostEqual(gross["upper_j"], 7.682118047887087)
        self.assertFalse(payload["window_evidence_precheck"]["gross_request"]["eligible"])

    def test_d078_golden_filename_version_matches_minter(self) -> None:
        for suffix in ("051", "052"):
            with self.subTest(suffix=suffix):
                payload = json.loads(
                    (
                        REPO_ROOT
                        / "tests"
                        / "goldens"
                        / f"d078_r01_reducer_{suffix}.json"
                    ).read_text()
                )
                expected = f"0.5.{int(suffix[-1])}"
                self.assertEqual(
                    payload["summary_provenance"]["reducer_version"], expected
                )

    def test_anchor_reconstruction_dispatches_on_stored_v3_method(self) -> None:
        import copy

        from joulewise.bundle_read import BundleReader
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V3

        reader = BundleReader(self.FIXTURE)
        metadata = copy.deepcopy(reader.metadata())
        stored_anchor = metadata["uncertainty_evidence"]["clock_anchor"]
        stored_anchor["method"] = CLOCK_METHOD_V3
        derived = {
            "status": "bounded",
            "first_sample_end_point_epoch_s": stored_anchor[
                "first_sample_end_point_epoch_s"
            ],
            "effective_clock_anchor_bound_s": 0.002,
            "wall_minus_monotonic_span_s": 0.001,
        }
        with patch.object(
            reduce_module,
            "resolve_anchor_reconstructor",
            return_value=lambda **_kwargs: derived,
        ) as resolver:
            context = reduce_module._derive_anchor_context(
                reader, metadata, reducer_version="0.5.2"
            )
        resolver.assert_called_once_with(CLOCK_METHOD_V3)
        self.assertFalse(context.unresolved)
        self.assertEqual(context.bundle_bound_s, 0.002)
        self.assertEqual(context.edge_span_s, 0.001)

    def test_unregistered_anchor_reconstruction_refuses_before_fallback(self) -> None:
        import copy

        from joulewise.bundle_read import BundleReader

        reader = BundleReader(self.FIXTURE)
        metadata = copy.deepcopy(reader.metadata())
        metadata["uncertainty_evidence"]["clock_anchor"]["method"] = (
            "powermetrics_not_a_registered_anchor_method_v9"
        )
        context = reduce_module._derive_anchor_context(
            reader, metadata, reducer_version="0.5.2"
        )
        self.assertTrue(context.unresolved)
        self.assertEqual(context.detail, "anchor_method_unregistered")
        self.assertIsNone(context.curve)

    def test_legacy_p2_038_1_label_keeps_its_historical_reconstruction(self) -> None:
        """The pre-v2 envelope label must reconstruct exactly as it always has.

        Reconstruction has always run the v2 censored-intersection estimator
        regardless of the stored label, so registering the historical label
        must not change any reconstructed number -- while the label still
        cannot satisfy a calibration artifact's anchor_method_version binding.
        """

        from joulewise.bundle_read import BundleReader
        from joulewise.uncertainty_evidence import (
            ANCHOR_METHOD_VERSIONS,
            CLOCK_METHOD,
            derive_powermetrics_anchor_v2,
            resolve_anchor_reconstructor,
        )

        self.assertNotIn(CLOCK_METHOD, ANCHOR_METHOD_VERSIONS)
        self.assertIs(
            resolve_anchor_reconstructor(CLOCK_METHOD),
            derive_powermetrics_anchor_v2,
        )
        reader = BundleReader(self.FIXTURE)
        metadata = reader.metadata()
        self.assertEqual(
            metadata["uncertainty_evidence"]["clock_anchor"]["method"], CLOCK_METHOD
        )
        context = reduce_module._derive_anchor_context(
            reader, metadata, reducer_version="0.5.2"
        )
        self.assertFalse(context.unresolved)

    def test_calibration_binding_accepts_registered_v3_and_rejects_unregistered(
        self,
    ) -> None:
        """A calibration may declare any REGISTERED anchor method.

        The calibration artifact describes a separate instrument-validation
        capture, so its anchor method is deliberately independent of the
        measurement bundle's own stored anchor method; only membership in the
        registered set and agreement with its own hash-bound bindings row are
        enforced.
        """

        from joulewise.bundle_read import BundleReader
        from joulewise.uncertainty_evidence import CLOCK_METHOD, CLOCK_METHOD_V3

        evidence = self._replay_era(
            self._valid_instrument_evidence(
                anchor_method_version=CLOCK_METHOD_V3,
                bindings={"anchor_method_version": CLOCK_METHOD_V3},
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=evidence)
            reader = BundleReader(bundle)
            metadata = reader.metadata()
            bound, detail = reduce_module._verify_instrument_calibration(
                reader,
                metadata,
                metadata["instrument_calibration"],
                strict_physics=False,
            )
            self.assertIsNotNone(bound)
            self.assertIsNone(detail)

        # The pre-v2 envelope label is a reconstruction-compatibility entry
        # only: it can never satisfy a calibration artifact's binding.
        unregistered = self._replay_era(
            self._valid_instrument_evidence(
                anchor_method_version=CLOCK_METHOD,
                bindings={"anchor_method_version": CLOCK_METHOD},
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle_with_calibration(tmp, evidence=unregistered)
            reader = BundleReader(bundle)
            metadata = reader.metadata()
            bound, detail = reduce_module._verify_instrument_calibration(
                reader,
                metadata,
                metadata["instrument_calibration"],
                strict_physics=False,
            )
            self.assertIsNone(bound)
            self.assertEqual(
                detail, "instrument_calibration_anchor_method_mismatch"
            )


class ReductionLaunchLineageBoundaryTests(unittest.TestCase):
    """Post-hoc admission lives beside callers, not in the pinned reducer."""

    @staticmethod
    def _lineage(*, plan_id: str = "plan-1") -> dict:
        return {
            "schema_version": "joulewise.launch_lineage.v1",
            "collection_boot_session_id": (
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
            ),
            "pack_id": "pack-1",
            "plan_id": plan_id,
            "window_id": "window-1",
            "bracket_session_id": "bracket-1",
            "consumption": {"path": "/receipts/consume.json", "sha256": "a" * 64},
            "start": {"path": "/receipts/start.json", "sha256": "b" * 64},
            "settle": {"path": "/receipts/settle.json", "sha256": "c" * 64},
            "completion": None,
        }

    @classmethod
    def _evidence(cls, bundle_id: str, lineage: dict | None) -> BundleEvidence:
        return BundleEvidence(
            entry={"entry_id": bundle_id},
            bundle_id=bundle_id,
            relative_path=bundle_id,
            path=Path(bundle_id),
            summary={},
            metadata={},
            raw_config=(
                {
                    "run_metadata": {
                        "tags": ["launch_lineage_required"]
                    }
                }
                if lineage is not None
                else {}
            ),
            strict_problems=(),
            base_reason_codes=(),
            config_sha256=None,
            summary_sha256=None,
            replacement_classification="registered",
            inclusion_status="included",
            launch_lineage=(
                {"launch_lineage": lineage} if lineage is not None else None
            ),
        )

    def test_legacy_reduction_remains_dormant(self) -> None:
        legacy = self._evidence("legacy", None)

        self.assertIsNone(_require_common_launch_lineage((legacy,)))
        self.assertNotIn("launch_lineage", legacy.audit_row()["window_prechecks"])

    def test_admissible_reduction_carries_full_authenticated_lineage(self) -> None:
        lineage = self._lineage()
        members = (
            self._evidence("member-1", lineage),
            self._evidence("member-2", lineage),
        )

        self.assertEqual(_require_common_launch_lineage(members), lineage)
        self.assertEqual(
            members[0].audit_row()["window_prechecks"]["launch_lineage"],
            lineage,
        )

    def test_mixed_or_nonidentical_reduction_lineages_refuse(self) -> None:
        lineage = self._lineage()
        cases = (
            (
                self._evidence("marker", lineage),
                self._evidence("legacy", None),
            ),
            (
                self._evidence("member-1", lineage),
                self._evidence(
                    "member-2",
                    self._lineage(plan_id="plan-2"),
                ),
            ),
        )
        for members in cases:
            with self.subTest(members=[row.bundle_id for row in members]):
                with self.assertRaisesRegex(
                    AnalysisInputError,
                    "launch_lineage_conflict",
                ):
                    _require_common_launch_lineage(members)
