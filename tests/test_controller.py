"""Tests for the controller lifecycle (Slice 2C; D-011, D-012, D-013, D-019)."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest.mock import patch

import joulewise.adapters as adapters
from joulewise.clock import Clock, FakeClock
from joulewise.controller import (
    STATUS_BY_REASON,
    _suite_rep_index_from_run_id,
    run_benchmark,
    run_experiment,
)
from joulewise.interfaces import AdapterResult
from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    RunStatus,
    SummaryMetrics,
)
from joulewise.suite import order_seed, suite_manifest_sha256

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"
SUITE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_suite_local.json"
SUITE_MANIFEST_PATH = REPO_ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json"

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


def make_suite_config(run_id: str, *, repetitions: int = 1, sha: str | None = None) -> BenchmarkConfig:
    data = json.loads(SUITE_CONFIG_PATH.read_text())
    manifest = json.loads(SUITE_MANIFEST_PATH.read_text())
    data["run_id"] = run_id
    data["workload_profile"]["suite_manifest_ref"] = str(SUITE_MANIFEST_PATH)
    data["workload_profile"]["suite_manifest_sha256"] = sha or suite_manifest_sha256(manifest)
    data["workload_profile"]["repetitions"] = repetitions
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
        return AdapterResult(
            ok=True,
            metadata={"memory_snapshots": [{"label": "cleanup_start", "sentinel": True}]},
        )


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


class FailingIdleTelemetry:
    name = "failing-idle"

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def device_metadata(self, config: BenchmarkConfig, context=None) -> dict:
        return self._inner.device_metadata(config, context)

    def measure_idle(self, config: BenchmarkConfig, context=None):
        from joulewise.interfaces import AdapterFailure

        raise AdapterFailure(FailureReason.UNKNOWN_ERROR, "injected idle failure")

    def thermal_state(self, config: BenchmarkConfig, context=None):
        return self._inner.thermal_state(config, context)

    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return self._inner.start_sampling(config, context)

    def stop_sampling(self, config: BenchmarkConfig, context=None):
        return self._inner.stop_sampling(config, context)


class FailingIdleRegistry:
    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        if telemetry is not None:
            telemetry = FailingIdleTelemetry(telemetry)
        return telemetry, failure

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class SuspectIdleTelemetry:
    """Wraps mock telemetry and marks the idle baseline suspect."""

    name = "suspect-idle"

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def device_metadata(self, config: BenchmarkConfig, context=None) -> dict:
        return self._inner.device_metadata(config, context)

    def measure_idle(self, config: BenchmarkConfig, context=None):
        baseline = self._inner.measure_idle(config, context)
        return replace(
            baseline,
            gpu_idle_ratio_mean=0.4,
            gpu_idle_ratio_min=0.0,
            gpu_freq_hz_mean=338.0,
            idle_window_suspect=True,
        )

    def thermal_state(self, config: BenchmarkConfig, context=None):
        return self._inner.thermal_state(config, context)

    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return self._inner.start_sampling(config, context)

    def stop_sampling(self, config: BenchmarkConfig, context=None):
        return self._inner.stop_sampling(config, context)


class SuspectIdleRegistry:
    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        if telemetry is not None:
            telemetry = SuspectIdleTelemetry(telemetry)
        return telemetry, failure

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class MetadataRuntime:
    name = "metadata-runtime"

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def prepare(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return self._inner.prepare(config, context)

    def warmup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return self._inner.warmup(config, context)

    def run_workload(self, config: BenchmarkConfig, context=None) -> Any:
        result = self._inner.run_workload(config, context)
        return replace(
            result,
            metadata={
                "sentinel_runtime_metadata": "round-trip",
                "worker_metadata": {"node_utc_offset_s": -28800},
            },
        )

    def cleanup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return self._inner.cleanup(config, context)


class MetadataRuntimeRegistry:
    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        runtime, failure = adapters.resolve_runtime(config, clock)
        if runtime is not None:
            runtime = MetadataRuntime(runtime)
        return runtime, failure

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_telemetry(config, clock)

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class CollidingMetadataRuntime:
    name = "colliding-metadata-runtime"

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def prepare(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return self._inner.prepare(config, context)

    def warmup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return self._inner.warmup(config, context)

    def run_workload(self, config: BenchmarkConfig, context=None) -> Any:
        result = self._inner.run_workload(config, context)
        return replace(
            result,
            metadata={
                "metadata": "adapter-top-level-metadata",
                "name": "adapter-reported-name",
            },
        )

    def cleanup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        return self._inner.cleanup(config, context)


class CollidingMetadataRuntimeRegistry:
    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        runtime, failure = adapters.resolve_runtime(config, clock)
        if runtime is not None:
            runtime = CollidingMetadataRuntime(runtime)
        return runtime, failure

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_telemetry(config, clock)

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class DeterministicClock:
    """Non-Fake test clock that advances instantly without host time."""

    def __init__(self, start: float = 1_700_000_000.0) -> None:
        self._start = float(start)
        self._now = float(start)

    def now(self) -> float:
        return self._now

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("cannot sleep a negative duration")
        self._now += seconds

    def info(self) -> dict[str, Any]:
        return {"kind": "deterministic-test", "start_s": self._start}


def fake_environment_run(command, **kwargs):
    if tuple(command) == ("git", "rev-parse", "HEAD"):
        return subprocess.CompletedProcess(command, 0, "0" * 40 + "\n", "")
    outputs = {
        ("pmset", "-g", "batt"): "Now drawing from 'AC Power'\n -InternalBattery-0 100%; charged; 0:00 remaining\n",
        ("pmset", "-g"): " lowpowermode 0\n",
        ("pmset", "-g", "assertions"): "   PreventUserIdleDisplaySleep    0\n",
        ("memory_pressure", "-Q"): "System-wide memory free percentage: 42.0%\n",
        ("vm_stat",): (
            "Mach Virtual Memory Statistics: (page size of 4096 bytes)\n"
            "Pages free: 1000.\n"
            "Pageins: 2000.\n"
            "Pageouts: 30.\n"
            "Pages occupied by compressor: 400.\n"
            "Pages stored in compressor: 500.\n"
        ),
        ("sysctl", "vm.swapusage"): "vm.swapusage: total = 1.00G used = 0.00M free = 1.00G\n",
        ("system_profiler", "SPDisplaysDataType", "-json"): """{
          "SPDisplaysDataType": [
            {
              "_name": "Apple GPU",
              "spdisplays_ndrvs": [
                {
                  "_name": "Built-in Display",
                  "spdisplays_online": "spdisplays_yes",
                  "spdisplays_connection_type": "spdisplays_internal"
                }
              ]
            }
          ]
        }""",
        ("ioreg", "-r", "-c", "IOMobileFramebuffer"): (
            "+-o IOMobileFramebufferShim  <class IOMobileFramebufferShim, id 0x1, registered>\n"
            '  |   "IONameMatched" = "disp0,t603x"\n'
        ),
        ("ioreg", "-r", "-c", "AppleSmartBattery", "-d", "1"): (
            '"ExternalConnected" = Yes\n'
            '"IsCharging" = No\n'
            '"AdapterDetails" = {"Watts"=96,"Description"="USB-C"}\n'
        ),
        ("sysctl", "-n", "kern.boottime"): "{ sec = 1700000000, usec = 0 }\n",
        ("pgrep", "-x", "timed"): "123\n",
        ("uptime",): "12:00 up 1 day, load averages: 1.00 2.00 3.00\n",
        ("sw_vers",): "ProductName:\t\tmacOS\nProductVersion:\t\t14.0\nBuildVersion:\t\t23A344\n",
        (
            "sysctl",
            "-n",
            "hw.model",
            "hw.ncpu",
            "machdep.cpu.brand_string",
        ): "MacTest1,1\n8\nTest CPU\n",
    }
    key = tuple(command)
    if key not in outputs:
        return subprocess.CompletedProcess(command, 1, "", "unexpected command")
    return subprocess.CompletedProcess(command, 0, outputs[key], "")


def fake_git_only_run(command, **kwargs):
    if tuple(command) == ("git", "rev-parse", "HEAD"):
        return subprocess.CompletedProcess(command, 0, "0" * 40 + "\n", "")
    raise AssertionError(f"FakeClock must not probe host environment: {command}")


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

    def test_runtime_result_metadata_round_trips_under_adapter_namespace(self) -> None:
        config = make_config("controller-runtime-metadata")
        bundle_path, summary = run_benchmark(
            config,
            self.runs_root,
            self.clock,
            registry=MetadataRuntimeRegistry(),
        )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        runtime = metadata["adapters"]["runtime"]
        self.assertEqual(runtime["sentinel_runtime_metadata"], "round-trip")
        self.assertEqual(runtime["worker_metadata"]["node_utc_offset_s"], -28800)

    def test_runtime_result_metadata_collision_with_non_dict_metadata_slot(self) -> None:
        config = make_config("controller-colliding-adapter-metadata")
        bundle_path, summary = run_benchmark(
            config,
            self.runs_root,
            self.clock,
            registry=CollidingMetadataRuntimeRegistry(),
        )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        runtime = metadata["adapters"]["runtime"]
        self.assertEqual(runtime["name"], "colliding-metadata-runtime")
        self.assertEqual(
            runtime["metadata"],
            {
                "metadata": "adapter-top-level-metadata",
                "name": "adapter-reported-name",
            },
        )

    def test_single_run_captures_environment_snapshot(self) -> None:
        config = make_config("controller-environment")
        clock = DeterministicClock()
        with patch(
            "joulewise.environment.subprocess.run",
            side_effect=fake_environment_run,
        ) as run:
            bundle_path, _ = run_benchmark(config, self.runs_root, clock)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        environment = metadata["environment"]
        environment_calls = [
            call for call in run.call_args_list if call.args[0][0] != "git"
        ]
        self.assertEqual(len(environment_calls), 14)
        self.assertEqual(environment["power_source"], "AC Power")
        self.assertEqual(environment["memory_free_percent"], 42.0)
        self.assertEqual(environment["memory"]["pageins"], 2000)
        self.assertEqual(environment["memory"]["pages_occupied_by_compressor"], 400)
        self.assertEqual(environment["memory"]["pages_stored_in_compressor"], 500)
        self.assertEqual(environment["display"]["active_displays"], 1)
        self.assertEqual(environment["display"]["probe"], "system_profiler_spdisplays")
        self.assertEqual(environment["display"]["framebuffer_pipes_total"], 1)
        self.assertEqual(environment["power"]["adapter_watts"], 96)
        self.assertEqual(environment["clock_sync"]["status"], "limited_without_admin")
        self.assertIs(environment["clock_sync"]["timed_running"], True)
        self.assertFalse(environment["capture_skipped"])
        self.assertEqual(environment["capture_scope"], "run")
        self.assertIsNone(environment["captured_for_rep"])
        self.assertIsInstance(environment["captured_at_s"], (int, float))
        self.assertIsInstance(environment["env_capture_duration_s"], (int, float))
        self.assertEqual(environment["settle_s"], 2.0)

    def test_idle_baseline_failure_preserves_prepare_end_environment(self) -> None:
        config = make_config("controller-idle-failure-env")
        clock = DeterministicClock()
        with patch(
            "joulewise.environment.subprocess.run",
            side_effect=fake_environment_run,
        ):
            bundle_path, summary = run_benchmark(
                config,
                self.runs_root,
                clock,
                registry=FailingIdleRegistry(),
            )

        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertNotIn("idle_baseline", metadata)
        environment = metadata["environment"]
        self.assertEqual(environment["capture_scope"], "run")
        self.assertFalse(environment["capture_skipped"])
        self.assertEqual(environment["settle_s"], 2.0)
        self.assertEqual(environment["power_source"], "AC Power")

    def test_negative_preceding_gap_is_signed_and_flagged(self) -> None:
        config = make_config("controller-negative-gap")
        bundle_path, summary = run_benchmark(
            config,
            self.runs_root,
            FakeClock(start=0.0),
            extra_metadata={"preceding_member_end_s": 100.0},
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        extra = metadata["extra"]
        self.assertEqual(extra["idle_start_s"], 2.0)
        self.assertEqual(extra["preceding_gap_s"], -98.0)
        self.assertIs(extra["clock_step_suspect"], True)

    def test_fake_clock_skips_environment_subprocesses(self) -> None:
        with patch(
            "joulewise.environment.subprocess.run",
            side_effect=fake_git_only_run,
        ):
            bundle_path, _ = self.run_happy()
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        environment = metadata["environment"]
        self.assertTrue(environment["capture_skipped"])
        self.assertEqual(environment["skip_reason"], "fake_clock")
        self.assertEqual(environment["capture_scope"], "run")
        self.assertIsNone(environment["captured_at_s"])

    def test_suspect_idle_flag_does_not_fail_successful_run(self) -> None:
        config = make_config("controller-suspect-idle")
        bundle_path, summary = run_benchmark(
            config,
            self.runs_root,
            self.clock,
            registry=SuspectIdleRegistry(),
        )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIs(summary.measurement_quality.idle_window_suspect, True)
        self.assert_complete_bundle(bundle_path)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertIs(metadata["idle_baseline"]["idle_window_suspect"], True)
        written = json.loads((bundle_path / "summary_metrics.json").read_text())
        self.assertEqual(written["status"], "succeeded")
        self.assertIs(written["measurement_quality"]["idle_window_suspect"], True)

    def test_new_bundle_writes_summary_and_workload_provenance(self) -> None:
        bundle_path, summary = self.run_happy()
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        workload = metadata["workload_provenance"]
        self.assertEqual(workload["prompt"]["realized_token_count"], 32)
        self.assertEqual(
            workload["prompt"]["token_hash_domain"],
            "joulewise.prompt_token_ids.v1",
        )
        self.assertEqual(len(workload["prompt"]["token_ids_sha256"]), 64)
        self.assertEqual(workload["tokenizer"]["backend"], "mock")
        self.assertEqual(workload["generator"]["name"], "mock_runtime")
        self.assertEqual(workload["output_policy"]["name"], "fixed_budget_exact")
        self.assertEqual(workload["output_policy"]["requested_tokens"], 8)
        self.assertEqual(workload["output_policy"]["emitted_tokens"], 8)
        self.assertEqual(
            workload["output_policy"]["stop_condition"],
            "requested_tokens_emitted",
        )
        written = json.loads((bundle_path / "summary_metrics.json").read_text())
        self.assertEqual(
            sorted(written["summary_provenance"]),
            [
                "config_schema_version",
                "reducer_id",
                "reducer_version",
                "summary_schema_version",
            ],
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
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertEqual(metadata["environment"]["capture_scope"], "failure_fallback")
        self.assertTrue(metadata["environment"]["capture_skipped"])

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
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertEqual(
            metadata["adapters"]["runtime"]["cleanup_metadata"]["memory_snapshots"],
            [{"label": "cleanup_start", "sentinel": True}],
        )
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

    def test_node_role_context_passes_through_untouched(self) -> None:
        # 2N.9 (D-008/D-024 compatibility): a Phase 3 split-run context with a
        # node_role must flow through today's adapters with no code change -
        # mocks ignore fields they do not need (single lifecycle code path).
        from joulewise.interfaces import RunContext

        config = make_config("context-node-role")
        bundle_dir = self.runs_root / "synthetic-prefill-node"
        raw_dir = bundle_dir / "raw"
        raw_dir.mkdir(parents=True)
        context = RunContext(
            config=config,
            clock=self.clock,
            run_id="synthetic-prefill-node",
            bundle_path=bundle_dir,
            raw_dir=raw_dir,
            logs_dir=bundle_dir / "logs",
            outputs_dir=bundle_dir / "outputs",
            node_role="prefill",
        )
        self.assertEqual(context.node_role, "prefill")
        telemetry, failure = adapters.resolve_telemetry(config, self.clock)
        self.assertIsNone(failure)
        self.assertTrue(telemetry.start_sampling(config, context).ok)
        self.clock.sleep(1.0)
        samples = telemetry.stop_sampling(config, context)
        self.assertGreaterEqual(len(samples), 2)
        self.assertTrue((raw_dir / "mock_samples.json").is_file())

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


class SuiteControllerTests(ControllerTestCase):
    def test_suite_rep_index_parser_edges(self) -> None:
        cases = {
            "plain-run": 0,
            "exp__rX": 0,
            "exp__r0": 0,
            "exp__r007": 7,
            "outer__r2__r5": 5,
        }
        for run_id, expected in cases.items():
            with self.subTest(run_id=run_id):
                self.assertEqual(_suite_rep_index_from_run_id(run_id), expected)

    def test_suite_run_writes_manifest_metadata_and_bracketed_markers(self) -> None:
        bundle_path, summary = run_benchmark(
            make_suite_config("suite-happy"), self.runs_root, self.clock
        )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNotNone(summary.suite_metrics)
        self.assertTrue((bundle_path / "suite_manifest.json").is_file())
        self.assertTrue((bundle_path / "outputs" / "suite_items.jsonl").is_file())
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertEqual(metadata["suite"]["suite_id"], "mock_suite_smoke")
        events = self.read_events(bundle_path)
        types = [event["event_type"] for event in events]
        sampling_started = types.index("sampling_started")
        sampling_stopped = types.index("sampling_stopped")
        self.assertEqual(types.count("suite_start"), 1)
        self.assertEqual(types.count("suite_end"), 1)
        self.assertLess(sampling_started, types.index("suite_start"))
        self.assertLess(types.index("suite_end"), sampling_stopped)
        suite_indices = [
            index for index, event in enumerate(events) if event["phase"] == "suite"
        ]
        self.assertTrue(suite_indices)
        self.assertTrue(all(sampling_started < index < sampling_stopped for index in suite_indices))

    def test_suite_runtime_without_run_suite_is_unsupported_complete_bundle(self) -> None:
        bundle_path, summary = run_benchmark(
            make_suite_config("suite-unsupported"),
            self.runs_root,
            self.clock,
            registry=ExplodingRegistry(),
        )
        self.assertEqual(summary.status, RunStatus.UNSUPPORTED)
        self.assertEqual(summary.failure_reason, FailureReason.UNSUPPORTED_WORKLOAD)
        for artifact in COMPLETE_BUNDLE_ARTIFACTS:
            self.assertTrue((bundle_path / artifact).exists(), artifact)

    def test_suite_manifest_hash_mismatch_fails_closed_with_complete_bundle(self) -> None:
        bundle_path, summary = run_benchmark(
            make_suite_config("suite-bad-hash", sha="bad"),
            self.runs_root,
            self.clock,
        )
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("suite manifest hash mismatch", summary.failure_message)
        for artifact in COMPLETE_BUNDLE_ARTIFACTS:
            self.assertTrue((bundle_path / artifact).exists(), artifact)

    def test_run_experiment_suite_uses_repetition_order_seed(self) -> None:
        manifest_path, results = run_experiment(
            make_suite_config("suite-experiment", repetitions=2),
            self.runs_root,
            self.clock,
        )
        self.assertTrue(manifest_path.is_file())
        self.assertEqual(len(results), 2)
        for rep, (bundle_path, summary) in enumerate(results, start=1):
            self.assertEqual(summary.status, RunStatus.SUCCEEDED)
            self.assertTrue((bundle_path / "suite_manifest.json").is_file())
            metadata = json.loads((bundle_path / "metadata.json").read_text())
            self.assertEqual(
                metadata["suite"]["order_seed"],
                order_seed("mock-suite-seed", "manifest_order", rep),
            )


if __name__ == "__main__":
    unittest.main()
