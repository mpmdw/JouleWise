"""Tests for the reducer (Slice 2D; D-002, D-018, D-019).

Bundles are assembled with the real :class:`RunBundleWriter` plus hand-authored
events and traces under a :class:`FakeClock`, so every expected energy is a
closed form computed by hand and asserted to 9 decimal places. The reducer is a
pure function over the on-disk artifacts, so the synthetic bundles are not
finalized - the reducer reads a not-yet-finalized directory exactly as the
controller invokes it before ``finalize()``.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise import reduce as reduce_module
from joulewise.bundle import RunBundleWriter
from joulewise.clock import FakeClock
from joulewise.controller import run_benchmark
from joulewise.interfaces import PowerSample, RuntimeEvent
from joulewise.schemas import (
    BenchmarkConfig,
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

    def add_token(self, index: int, timestamp_s: float) -> None:
        self.add_event(
            "token", "decode", timestamp_s, message=f"token {index}",
            metadata={"index": index},
        )

    def add_phase(self, phase: str, start_s: float, end_s: float) -> None:
        self.add_event("phase_start", phase, start_s)
        self.add_event("phase_end", phase, end_s)

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
            "gpu_freq_hz_mean": 1363.0,
            "idle_window_suspect": True,
        }
        builder.measured_window(0.0, 2.0)
        builder.write_trace(constant_samples(0.0, 2.0, hz=1.0, power_w=7.5))
        builder.write_metadata(rail_manifest=["mock"], idle=idle)
        summary = reduce_module.reduce_bundle(builder.path)
        self.assertIs(summary.idle_baseline.idle_window_suspect, True)
        self.assertIs(summary.measurement_quality.idle_window_suspect, True)

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
        builder.add_phase("decode", 0.0, 2.0)
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


class DegenerateTests(ReduceTestCase):
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


if __name__ == "__main__":
    unittest.main()
