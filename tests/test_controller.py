"""Tests for the controller lifecycle (Slice 2C; D-011, D-012, D-013, D-019)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

import joulewise.adapters as adapters
from joulewise.clock import Clock, FakeClock
from joulewise.controller import STATUS_BY_REASON, run_benchmark
from joulewise.interfaces import AdapterResult
from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    RunStatus,
    SummaryMetrics,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"

EVENT_KEYS = {"timestamp_s", "event_type", "phase", "message", "metadata"}

#: Artifacts every finalized bundle must contain, success or failure (D-011).
COMPLETE_BUNDLE_ARTIFACTS = (
    "config.json",
    "metadata.json",
    "events.jsonl",
    "summary_metrics.json",
    "logs/controller.log",
    "logs/runtime.log",
    "logs/telemetry.log",
)

HAPPY_PATH_SEQUENCE = (
    [
        ("run_started", "run"),
        ("stage_started", "validate"),
        ("stage_completed", "validate"),
        ("stage_started", "prepare"),
        ("stage_completed", "prepare"),
        ("stage_started", "idle_baseline"),
        ("stage_completed", "idle_baseline"),
        ("stage_started", "warmup"),
        ("stage_completed", "warmup"),
        ("stage_started", "measured_run"),
        ("sampling_started", "measured_run"),
        ("phase_start", "prefill"),
        ("phase_end", "prefill"),
        ("phase_start", "decode"),
    ]
    + [("token", "decode")] * 8
    + [
        ("phase_end", "decode"),
        ("sampling_stopped", "measured_run"),
        ("stage_completed", "measured_run"),
        ("stage_started", "cleanup"),
        ("stage_completed", "cleanup"),
        ("stage_started", "reduce"),
        ("stage_completed", "reduce"),
        ("run_finalized", "run"),
    ]
)


def make_config(
    run_id: str,
    *,
    model_name: str | None = None,
    notes: str | None = None,
) -> BenchmarkConfig:
    """Build a config from the example mock JSON with ``run_id`` replaced."""
    data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
    data["run_id"] = run_id
    if model_name is not None:
        data["model"]["name"] = model_name
    if notes is not None:
        data["hardware_target"]["notes"] = notes
    return BenchmarkConfig.from_mapping(data)


class ExplodingRuntime:
    """Runtime whose measured workload raises an unexpected exception."""

    name = "exploding"

    def prepare(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return AdapterResult(ok=True, metadata={"adapter": "exploding"})

    def warmup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return AdapterResult(ok=True)

    def run_workload(self, config: BenchmarkConfig, context=None) -> Any:
        raise RuntimeError("injected workload explosion")

    def cleanup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return AdapterResult(ok=True)


class ExplodingRegistry:
    """Delegates to the real registry except for the exploding runtime."""

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return ExplodingRuntime(), None

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_telemetry(config, clock)

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class PoisonTelemetry:
    """Wraps the real mock telemetry but returns non-JSON-serializable device
    metadata AND fails start_sampling (to drive the structured failure path)."""

    name = "poison-telemetry"

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def device_metadata(self, config: BenchmarkConfig, context=None) -> dict:
        # An object() is not JSON-serializable; write_metadata must coerce it
        # via default=str rather than abort the bundle (D-011).
        return {"poison": object()}

    def measure_idle(self, config: BenchmarkConfig, context=None):
        return self._inner.measure_idle(config)

    def thermal_state(self, config: BenchmarkConfig, context=None):
        return self._inner.thermal_state(config)

    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return AdapterResult(
            ok=False,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            message="injected start_sampling failure",
        )

    def stop_sampling(self, config: BenchmarkConfig, context=None):
        return self._inner.stop_sampling(config)


class PoisonRegistry:
    """Real runtime + transport, telemetry wrapped to poison metadata + fail."""

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        if telemetry is not None:
            telemetry = PoisonTelemetry(telemetry)
        return telemetry, failure

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class ControllerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.clock = FakeClock(start=1_700_000_000.0)

    def read_events(self, bundle_path: Path) -> list[dict[str, Any]]:
        lines = (bundle_path / "events.jsonl").read_text().splitlines()
        return [json.loads(line) for line in lines]

    def assert_complete_bundle(self, bundle_path: Path) -> None:
        for artifact in COMPLETE_BUNDLE_ARTIFACTS:
            self.assertTrue((bundle_path / artifact).is_file(), artifact)
        self.assertTrue((bundle_path / "raw").is_dir())

    def assert_summary_round_trips(self, bundle_path: Path) -> dict[str, Any]:
        """summary_metrics.json parses and its status/failure_reason validate."""
        data = json.loads((bundle_path / "summary_metrics.json").read_text())
        status = RunStatus(data["status"])
        reason = (
            FailureReason(data["failure_reason"])
            if data["failure_reason"] is not None
            else None
        )
        SummaryMetrics(
            status=status,
            failure_reason=reason,
            failure_message=data["failure_message"],
        ).validate()
        return data

    def assert_run_finalized_last(self, events: list[dict[str, Any]]) -> None:
        self.assertEqual(events[-1]["event_type"], "run_finalized")
        self.assertEqual(events[-1]["phase"], "run")

    def assert_timestamps_non_decreasing(self, events: list[dict[str, Any]]) -> None:
        timestamps = [event["timestamp_s"] for event in events]
        self.assertEqual(timestamps, sorted(timestamps))


class StatusByReasonTests(unittest.TestCase):
    def test_d012_table_exact(self) -> None:
        self.assertEqual(
            STATUS_BY_REASON,
            {
                FailureReason.DID_NOT_FIT: RunStatus.UNSUPPORTED,
                FailureReason.FORMAT_UNAVAILABLE: RunStatus.UNSUPPORTED,
                FailureReason.UNSUPPORTED_WORKLOAD: RunStatus.UNSUPPORTED,
                FailureReason.RUNTIME_UNAVAILABLE: RunStatus.UNSUPPORTED,
                FailureReason.TELEMETRY_UNAVAILABLE: RunStatus.UNSUPPORTED,
                FailureReason.PERMISSION_DENIED: RunStatus.FAILED,
                FailureReason.TRANSPORT_UNAVAILABLE: RunStatus.FAILED,
                FailureReason.UNKNOWN_ERROR: RunStatus.FAILED,
            },
        )

    def test_every_failure_reason_is_mapped(self) -> None:
        self.assertEqual(set(STATUS_BY_REASON), set(FailureReason))


class HappyPathTests(ControllerTestCase):
    def run_happy(self) -> tuple[Path, SummaryMetrics]:
        config = make_config("controller-happy")
        return run_benchmark(config, self.runs_root, self.clock)

    def test_returns_bundle_path_and_succeeded_summary(self) -> None:
        bundle_path, summary = self.run_happy()
        self.assertEqual(bundle_path, self.runs_root / "controller-happy")
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNone(summary.failure_reason)

    def test_every_artifact_exists(self) -> None:
        bundle_path, _ = self.run_happy()
        self.assert_complete_bundle(bundle_path)
        for artifact in (
            "power_trace.csv",
            "outputs/response.txt",
            "outputs/tokens.jsonl",
        ):
            self.assertTrue((bundle_path / artifact).is_file(), artifact)

    def test_exact_event_sequence(self) -> None:
        bundle_path, _ = self.run_happy()
        events = self.read_events(bundle_path)
        sequence = [(event["event_type"], event["phase"]) for event in events]
        self.assertEqual(sequence, HAPPY_PATH_SEQUENCE)

    def test_event_records_well_formed_and_ordered(self) -> None:
        bundle_path, _ = self.run_happy()
        events = self.read_events(bundle_path)
        for event in events:
            self.assertEqual(set(event), EVENT_KEYS)
        self.assert_timestamps_non_decreasing(events)

    def test_summary_is_reduced_by_default_reducer(self) -> None:
        # Slice 2D wired reduce.reduce_bundle as the default reducer, so the
        # happy path now writes a real reduced summary (energy numbers, phase
        # attribution) rather than the minimal-summary shape.
        bundle_path, summary = self.run_happy()
        data = self.assert_summary_round_trips(bundle_path)
        self.assertEqual(data["status"], "succeeded")
        self.assertIsNone(data["failure_reason"])
        quality = data["measurement_quality"]
        self.assertEqual(quality["requested_sampling_hz"], 2.0)
        self.assertEqual(quality["idle_power_w_stddev"], 0.0)
        self.assertEqual(quality["telemetry_source"], "mock")
        self.assertEqual(data["idle_baseline"]["power_w_mean"], 5.0)
        self.assertEqual(summary.idle_baseline.power_w_mean, 5.0)
        # Real reducer output: energy and per-phase attribution are populated.
        self.assertIsNotNone(summary.gross_energy_j)
        self.assertGreater(summary.gross_energy_j, 0.0)
        self.assertIsNotNone(summary.idle_subtracted_energy_j)
        self.assertEqual(set(summary.phase_energy_j), {"prefill", "decode"})
        self.assertIsNotNone(data["phase_energy_j"])

    def test_metadata_carries_model_block(self) -> None:
        # Contract: metadata.json enumerates model metadata (run_bundle_layout
        # docs). The model block is present and carries the configured name.
        bundle_path, _ = self.run_happy()
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertIsInstance(metadata["model"], dict)
        self.assertEqual(metadata["model"]["name"], "mock-model")
        self.assertEqual(metadata["quantization"]["name"], "none")

    def test_metadata_carries_collected_sections(self) -> None:
        bundle_path, _ = self.run_happy()
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertEqual(metadata["adapters"]["runtime"]["name"], "mock")
        self.assertEqual(metadata["adapters"]["telemetry"]["name"], "mock")
        self.assertEqual(metadata["connection"], {"transport": "local", "host": "localhost"})
        self.assertEqual(metadata["device"]["rail_manifest"], ["mock"])
        self.assertEqual(metadata["idle_baseline"]["telemetry_backend"], "mock")
        self.assertEqual(metadata["thermal_pre"]["temperature_c"], 42.0)
        self.assertEqual(metadata["thermal_post"]["temperature_c"], 42.0)
        self.assertEqual(
            metadata["workload_observed"],
            {"token_count": 40, "output_token_count": 8},
        )

    def test_injected_reducer_summary_is_written(self) -> None:
        # The 2D seam: swapping the reducer changes the written summary.
        sentinel = SummaryMetrics(status=RunStatus.SUCCEEDED, energy_request_j=12.5)
        seen: list[Path] = []

        def reducer(bundle_path: Path) -> SummaryMetrics:
            seen.append(bundle_path)
            return sentinel

        config = make_config("controller-reducer")
        bundle_path, summary = run_benchmark(
            config, self.runs_root, self.clock, reducer=reducer
        )
        self.assertEqual(seen, [bundle_path])
        self.assertIs(summary, sentinel)
        data = json.loads((bundle_path / "summary_metrics.json").read_text())
        self.assertEqual(data["energy_request_j"], 12.5)


class UnsupportedModelTests(ControllerTestCase):
    def run_unsupported(self) -> tuple[Path, SummaryMetrics]:
        config = make_config("controller-unsupported", model_name="mock-unsupported")
        return run_benchmark(config, self.runs_root, self.clock)

    def test_status_and_reason(self) -> None:
        _, summary = self.run_unsupported()
        self.assertEqual(summary.status, RunStatus.UNSUPPORTED)
        self.assertEqual(summary.failure_reason, FailureReason.DID_NOT_FIT)

    def test_bundle_complete_and_schema_valid(self) -> None:
        bundle_path, _ = self.run_unsupported()
        self.assert_complete_bundle(bundle_path)
        data = self.assert_summary_round_trips(bundle_path)
        self.assertEqual(data["status"], "unsupported")
        self.assertEqual(data["failure_reason"], "did_not_fit")
        # The failure preceded the measured window: no trace, no outputs.
        self.assertFalse((bundle_path / "power_trace.csv").exists())

    def test_failure_event_in_prepare_phase(self) -> None:
        bundle_path, _ = self.run_unsupported()
        events = self.read_events(bundle_path)
        failures = [event for event in events if event["event_type"] == "failure"]
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["phase"], "prepare")
        self.assertEqual(failures[0]["metadata"], {"failure_reason": "did_not_fit"})
        self.assert_run_finalized_last(events)
        self.assert_timestamps_non_decreasing(events)


class TelemetryDeniedTests(ControllerTestCase):
    def run_denied(self) -> tuple[Path, SummaryMetrics]:
        config = make_config("controller-denied", notes="telemetry-denied")
        return run_benchmark(config, self.runs_root, self.clock)

    def test_status_and_reason(self) -> None:
        _, summary = self.run_denied()
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.PERMISSION_DENIED)

    def test_bundle_complete_without_power_trace(self) -> None:
        bundle_path, _ = self.run_denied()
        self.assert_complete_bundle(bundle_path)
        self.assertFalse((bundle_path / "power_trace.csv").exists())
        data = self.assert_summary_round_trips(bundle_path)
        self.assertEqual(data["status"], "failed")
        self.assertEqual(data["failure_reason"], "permission_denied")
        # The idle baseline was collected before the denial and is preserved.
        self.assertEqual(data["idle_baseline"]["power_w_mean"], 5.0)

    def test_failure_event_in_measured_run_phase(self) -> None:
        bundle_path, _ = self.run_denied()
        events = self.read_events(bundle_path)
        failures = [event for event in events if event["event_type"] == "failure"]
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["phase"], "measured_run")
        self.assertEqual(
            failures[0]["metadata"], {"failure_reason": "permission_denied"}
        )
        self.assert_run_finalized_last(events)
        self.assert_timestamps_non_decreasing(events)


class UnexpectedExceptionTests(ControllerTestCase):
    def run_exploding(self) -> tuple[Path, SummaryMetrics]:
        config = make_config("controller-exploding")
        return run_benchmark(
            config, self.runs_root, self.clock, registry=ExplodingRegistry()
        )

    def test_status_and_reason(self) -> None:
        _, summary = self.run_exploding()
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("injected workload explosion", summary.failure_message)

    def test_traceback_written_to_controller_log(self) -> None:
        bundle_path, _ = self.run_exploding()
        log_text = (bundle_path / "logs" / "controller.log").read_text()
        self.assertIn("Traceback (most recent call last):", log_text)
        self.assertIn("RuntimeError: injected workload explosion", log_text)

    def test_bundle_complete_and_schema_valid(self) -> None:
        bundle_path, _ = self.run_exploding()
        self.assert_complete_bundle(bundle_path)
        data = self.assert_summary_round_trips(bundle_path)
        self.assertEqual(data["status"], "failed")
        self.assertEqual(data["failure_reason"], "unknown_error")
        events = self.read_events(bundle_path)
        failures = [event for event in events if event["event_type"] == "failure"]
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["phase"], "measured_run")
        self.assertEqual(failures[0]["metadata"], {"failure_reason": "unknown_error"})
        self.assert_run_finalized_last(events)
        self.assert_timestamps_non_decreasing(events)


class PoisonMetadataTests(ControllerTestCase):
    """A hostile adapter must not break the D-011 bundle-completion invariant.

    Non-JSON-serializable adapter device_metadata, encountered on the failure
    path (start_sampling fails), must NOT escape execute(): the bundle still
    finalizes with a schema-valid summary and a run_finalized terminal event.
    """

    def run_poison(self) -> tuple[Path, SummaryMetrics]:
        config = make_config("controller-poison")
        return run_benchmark(
            config, self.runs_root, self.clock, registry=PoisonRegistry()
        )

    def test_run_returns_normally_with_complete_bundle(self) -> None:
        # Must not raise (the json.dumps coercion preserves D-011).
        bundle_path, summary = self.run_poison()
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assert_complete_bundle(bundle_path)
        data = self.assert_summary_round_trips(bundle_path)
        self.assertEqual(data["status"], "failed")

    def test_events_end_with_run_finalized(self) -> None:
        bundle_path, _ = self.run_poison()
        events = self.read_events(bundle_path)
        self.assert_run_finalized_last(events)
        # The poison value was coerced to its str() rather than aborting.
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertIn("poison", metadata["device"])


class DeterministicRunIdTests(ControllerTestCase):
    """D-022: identical config + clock => byte-identical run artifacts.

    With run_id removed the generated suffix is derived from the config hash
    (not a random token), so two runs into separate dirs under a fresh
    FakeClock(0.0) each produce byte-identical events.jsonl and power_trace.csv.
    """

    def _config_without_run_id(self) -> BenchmarkConfig:
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data.pop("run_id", None)
        return BenchmarkConfig.from_mapping(data)

    def test_two_runs_are_byte_identical(self) -> None:
        config = self._config_without_run_id()
        first_root = self.runs_root / "a"
        second_root = self.runs_root / "b"
        first_path, _ = run_benchmark(config, first_root, FakeClock(start=0.0))
        second_path, _ = run_benchmark(config, second_root, FakeClock(start=0.0))

        # Same generated run_id (config-hash suffix, no random token).
        self.assertEqual(first_path.name, second_path.name)

        self.assertEqual(
            (first_path / "events.jsonl").read_bytes(),
            (second_path / "events.jsonl").read_bytes(),
        )
        self.assertEqual(
            (first_path / "power_trace.csv").read_bytes(),
            (second_path / "power_trace.csv").read_bytes(),
        )


class LatencyTelemetry:
    """Wraps the mock telemetry, simulating sampler spawn and wind-down latency
    on the injected clock (2N.2: FakeClock alone collapses these intervals)."""

    name = "latency"

    def __init__(self, inner: Any, clock: Clock, start_latency_s: float, stop_latency_s: float) -> None:
        self._inner = inner
        self._clock = clock
        self._start_latency_s = start_latency_s
        self._stop_latency_s = stop_latency_s

    def device_metadata(self, config: BenchmarkConfig, context=None) -> dict:
        return self._inner.device_metadata(config, context)

    def measure_idle(self, config: BenchmarkConfig, context=None):
        return self._inner.measure_idle(config, context)

    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        # Simulated spawn latency (sudo probe, process start, first sample)
        # BEFORE sampling is confirmed active.
        self._clock.sleep(self._start_latency_s)
        return self._inner.start_sampling(config, context)

    def stop_sampling(self, config: BenchmarkConfig, context=None):
        samples = self._inner.stop_sampling(config, context)
        # Simulated wind-down latency (process stop, plist parsing) AFTER the
        # samples were collected.
        self._clock.sleep(self._stop_latency_s)
        return samples

    def thermal_state(self, config: BenchmarkConfig, context=None):
        return self._inner.thermal_state(config, context)


class LatencyRegistry:
    """Real mock adapters, telemetry wrapped with simulated sampler latency."""

    def __init__(self, clock: Clock, start_latency_s: float, stop_latency_s: float) -> None:
        self._clock = clock
        self._start_latency_s = start_latency_s
        self._stop_latency_s = stop_latency_s

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        if telemetry is not None:
            telemetry = LatencyTelemetry(
                telemetry, self._clock, self._start_latency_s, self._stop_latency_s
            )
        return telemetry, failure

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class RunContextSeamTests(ControllerTestCase):
    """2N.1 (D-024/D-002): adapters can preserve raw evidence via the context."""

    def test_mock_run_preserves_raw_sampler_output(self) -> None:
        bundle_path, summary = run_benchmark(
            make_config("context-raw"), self.runs_root, self.clock
        )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        raw_path = bundle_path / "raw" / "mock_samples.json"
        self.assertTrue(raw_path.is_file())
        raw_samples = json.loads(raw_path.read_text())
        trace_lines = (bundle_path / "power_trace.csv").read_text().splitlines()
        # Raw evidence matches the trace: one raw record per trace row.
        self.assertEqual(len(raw_samples), len(trace_lines) - 1)
        self.assertTrue(all(sample["rail"] == "mock" for sample in raw_samples))

    def test_stop_sampling_without_context_writes_no_raw_output(self) -> None:
        # Out-of-run invocations (the cooldown gate, direct adapter use) pass
        # no context; the adapter must tolerate that with no raw output.
        telemetry, failure = adapters.resolve_telemetry(
            make_config("context-none"), self.clock
        )
        self.assertIsNone(failure)
        config = make_config("context-none")
        self.assertTrue(telemetry.start_sampling(config).ok)
        self.clock.sleep(1.0)
        samples = telemetry.stop_sampling(config)
        self.assertGreaterEqual(len(samples), 2)


class SamplingWindowTests(ControllerTestCase):
    """2N.2 (D-026): the measured window excludes sampler start/stop latency."""

    def run_with_latency(
        self, run_id: str, start_latency_s: float, stop_latency_s: float
    ) -> tuple[Path, SummaryMetrics]:
        clock = FakeClock(start=1_700_000_000.0)
        registry = LatencyRegistry(clock, start_latency_s, stop_latency_s)
        return run_benchmark(
            make_config(run_id), self.runs_root, clock, registry=registry
        )

    def test_marker_events_bracket_the_runtime_events(self) -> None:
        bundle_path, _ = run_benchmark(
            make_config("markers"), self.runs_root, self.clock
        )
        events = self.read_events(bundle_path)
        types = [event["event_type"] for event in events]
        self.assertIn("sampling_started", types)
        self.assertIn("sampling_stopped", types)
        started = types.index("sampling_started")
        stopped = types.index("sampling_stopped")
        first_token = types.index("token")
        last_token = len(types) - 1 - types[::-1].index("token")
        self.assertLess(started, first_token)
        self.assertGreater(stopped, last_token)
        self.assertEqual(events[started]["phase"], "measured_run")
        self.assertEqual(events[stopped]["phase"], "measured_run")

    def test_sampler_latency_does_not_change_measured_metrics(self) -> None:
        _, baseline_summary = self.run_with_latency("latency-zero", 0.0, 0.0)
        _, latency_summary = self.run_with_latency("latency-real", 3.0, 2.0)

        self.assertEqual(baseline_summary.status, RunStatus.SUCCEEDED)
        self.assertEqual(latency_summary.status, RunStatus.SUCCEEDED)
        for metric in (
            "gross_energy_j",
            "idle_subtracted_energy_j",
            "energy_request_j",
            "ttft_s",
            "decode_latency_s",
        ):
            self.assertAlmostEqual(
                getattr(baseline_summary, metric),
                getattr(latency_summary, metric),
                places=9,
                msg=metric,
            )

    def test_stage_window_still_contains_the_latency(self) -> None:
        # The stage boundaries DO include the simulated latency - proving the
        # markers (not the stage span) are what keep it out of the metrics.
        bundle_path, _ = self.run_with_latency("latency-stage", 3.0, 2.0)
        events = self.read_events(bundle_path)
        by_type = {
            event["event_type"]: event["timestamp_s"]
            for event in events
            if event["phase"] == "measured_run"
        }
        self.assertAlmostEqual(
            by_type["sampling_started"] - by_type["stage_started"], 3.0, places=9
        )
        self.assertGreaterEqual(
            by_type["stage_completed"] - by_type["sampling_stopped"], 2.0
        )


if __name__ == "__main__":
    unittest.main()
