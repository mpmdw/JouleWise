"""Tests for the controller lifecycle (Slice 2C; D-011, D-012, D-013, D-019)."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest.mock import patch

import joulewise.adapters as adapters
from joulewise.adapters.powermetrics import (
    RICH_IDLE_NAME,
    PowermetricsTelemetryAdapter,
    rich_telemetry_jsonl_from_records,
)
from joulewise.clock import Clock, FakeClock, SystemClock
from joulewise.controller import (
    CAMPAIGN_POLICY_PATH_ENV,
    CAMPAIGN_POLICY_SHA256_ENV,
    CAMPAIGN_PREFLIGHT_JSON_ENV,
    STATUS_BY_REASON,
    _suite_rep_index_from_run_id,
    run_benchmark,
    run_experiment,
)
from joulewise.interfaces import AdapterResult
from joulewise.environment import evaluate_environment_policy
from joulewise.schemas import (
    BenchmarkConfig,
    CampaignPolicy,
    FailureReason,
    RunStatus,
    SummaryMetrics,
)
from joulewise.sampler_teardown import SamplerTeardown
from joulewise.suite import (
    SUITE_SCHEMA_VERSION,
    migrate_suite_manifest,
    order_seed,
    suite_manifest_sha256,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"
SUITE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_suite_local.json"
SUITE_MANIFEST_PATH = REPO_ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json"
PRODUCTION_POLICY_PATH = (
    REPO_ROOT / "configs" / "campaign_policies" / "quiet_mac_p2_production.json"
)
EXPLORATORY_POLICY_PATH = (
    REPO_ROOT / "configs" / "campaign_policies" / "quiet_mac_exploratory.json"
)

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


def campaign_policy_fixture(*, exploratory: bool) -> tuple[
    CampaignPolicy, dict[str, Any], dict[str, Any], dict[str, Any]
]:
    path = EXPLORATORY_POLICY_PATH if exploratory else PRODUCTION_POLICY_PATH
    policy = CampaignPolicy.from_mapping(json.loads(path.read_text()))
    snapshot = {
        "power_source": "AC Power",
        "power": {"external_connected": True},
        "low_power_mode": False,
        "display_power_state": "all_asleep",
        "screensaver_engaged": False,
        "screensaver_module": "Ventura",
        "screensaver_delay_s": 1200,
        "hid_idle_s": 5.0,
        "thermal_pressure": "nominal",
        "load_average_1m": 99.0,
        "capture_scope": "provided_test_fixture",
    }
    evaluation = evaluate_environment_policy(snapshot, policy.environment_guard)
    policy_sha = "a" * 64
    binding = {
        "schema_version": policy.schema_version,
        "policy_id": policy.policy_id,
        "policy_version": policy.policy_version,
        "profile": policy.profile.value,
        "sha256": policy_sha,
        "source": str(path),
    }
    preflight = {
        "schema_version": "joulewise.campaign_environment_preflight.v1",
        "policy_sha256": policy_sha,
        "snapshot": snapshot,
        "evaluation": evaluation,
        "override": None,
        "admitted": True,
    }
    return policy, binding, preflight, snapshot


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


class InterruptingCleanupRuntime:
    name = "interrupting-cleanup"

    def __init__(self, primary: BaseException, cleanup_error: BaseException) -> None:
        self.primary = primary
        self.cleanup_error = cleanup_error
        self.cleanup_calls = 0

    def prepare(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        raise self.primary

    def warmup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        raise AssertionError("warmup must not run after interrupted prepare")

    def run_workload(self, config: BenchmarkConfig, context=None) -> Any:
        raise AssertionError("workload must not run after interrupted prepare")

    def cleanup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        self.cleanup_calls += 1
        raise self.cleanup_error


class InterruptingCleanupRegistry:
    def __init__(self, runtime: InterruptingCleanupRuntime) -> None:
        self.runtime = runtime

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return self.runtime, None

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_telemetry(config, clock)

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class InterruptDuringStartTelemetry:
    """Sampler becomes live, then start is interrupted before confirmation."""

    name = "interrupt-during-start"

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.live = False
        self.stop_calls = 0

    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        result = self._inner.start_sampling(config, context)
        if not result.ok:
            return result
        self.live = True
        raise KeyboardInterrupt("injected after sampler start")

    def stop_sampling(self, config: BenchmarkConfig, context=None):
        self.stop_calls += 1
        samples = self._inner.stop_sampling(config, context)
        self.live = False
        return samples

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class InterruptDuringStartRegistry:
    def __init__(self) -> None:
        self.telemetry: InterruptDuringStartTelemetry | None = None

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        if telemetry is not None:
            self.telemetry = InterruptDuringStartTelemetry(telemetry)
            telemetry = self.telemetry
        return telemetry, failure

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class InterruptAfterStartTransitionTelemetry:
    """Interrupt alignment work after start returned with a live capture."""

    name = "interrupt-after-start-transition"

    def __init__(self, inner: Any, capture_path: Path) -> None:
        self._inner = inner
        self.capture_path = capture_path
        self.live = False
        self.stop_calls = 0
        self.salvage_calls = 0
        self._interrupt_alignment = False

    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        result = self._inner.start_sampling(config, context)
        if result.ok:
            self.capture_path.write_bytes(b"native capture survives\n")
            self.live = True
            self._interrupt_alignment = True
        return result

    def clock_alignments(self) -> list[dict[str, Any]]:
        if self._interrupt_alignment:
            self._interrupt_alignment = False
            raise KeyboardInterrupt("injected during post-start alignment")
        return []

    def stop_sampling(self, config: BenchmarkConfig, context=None):
        self.stop_calls += 1
        samples = self._inner.stop_sampling(config, context)
        self.live = False
        return samples

    def salvage_custody(self, context) -> list[dict[str, Any]]:
        self.salvage_calls += 1
        if self.live:
            self.capture_path.unlink(missing_ok=True)
        return []

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class InterruptAfterStartTransitionRegistry:
    def __init__(self, capture_path: Path) -> None:
        self.capture_path = capture_path
        self.telemetry: InterruptAfterStartTransitionTelemetry | None = None

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        if telemetry is not None:
            self.telemetry = InterruptAfterStartTransitionTelemetry(
                telemetry,
                self.capture_path,
            )
            telemetry = self.telemetry
        return telemetry, failure

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class InterruptAfterStopTelemetry:
    """Interrupt post-stop alignment after recording one successful stop."""

    name = "interrupt-after-stop"

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.stop_calls = 0
        self.stop_records: list[int] = []
        self._interrupt_alignment = False

    def stop_sampling(self, config: BenchmarkConfig, context=None):
        self.stop_calls += 1
        if self.stop_calls > 1:
            raise AssertionError("stop_sampling must not be called twice")
        samples = self._inner.stop_sampling(config, context)
        self.stop_records.append(len(samples))
        self._interrupt_alignment = True
        return samples

    def clock_alignments(self) -> list[dict[str, Any]]:
        if self._interrupt_alignment:
            self._interrupt_alignment = False
            raise KeyboardInterrupt("injected after successful stop")
        return []

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class InterruptAfterStopRegistry:
    def __init__(self) -> None:
        self.telemetry: InterruptAfterStopTelemetry | None = None

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        if telemetry is not None:
            self.telemetry = InterruptAfterStopTelemetry(telemetry)
            telemetry = self.telemetry
        return telemetry, failure

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class PoisonTelemetry:
    """Wraps the real mock telemetry but returns non-JSON-serializable device
    metadata AND fails start_sampling (to drive the structured failure path)."""

    name = "poison-telemetry"

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def device_metadata(self, config: BenchmarkConfig, context=None) -> dict:
        cycle: dict[str, Any] = {}
        cycle["self"] = cycle
        # Every malformed category must reach the bundle writer's single
        # quarantine pass without aborting failure-path finalization (D-011).
        return {
            "poison": object(),
            "cycle": cycle,
            "not_finite": float("inf"),
            7: "non-string-key value",
        }

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
            gpu_freq_mhz_mean=338.0,
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


class AdmissionIdleTelemetry(SuspectIdleTelemetry):
    """Return a pinned suspect sequence while preserving mock lifecycle calls."""

    name = "admission-idle"

    def __init__(
        self,
        inner: Any,
        suspect_sequence: list[bool],
        cpu_busy_sequence: list[float] | None = None,
        combined_power_sequence: list[float] | None = None,
    ) -> None:
        super().__init__(inner)
        self._suspect_sequence = list(suspect_sequence)
        self._cpu_busy_sequence = list(cpu_busy_sequence or [0.1])
        self._combined_power_sequence = list(combined_power_sequence or [0.1])
        self._attempt = 0

    def measure_idle(self, config: BenchmarkConfig, context=None):
        baseline = self._inner.measure_idle(config, context)
        index = min(self._attempt, len(self._suspect_sequence) - 1)
        self._attempt += 1
        suspect = self._suspect_sequence[index]
        return replace(
            baseline,
            gpu_idle_ratio_mean=0.4 if suspect else 0.99,
            gpu_idle_ratio_min=0.0 if suspect else 0.95,
            gpu_freq_mhz_mean=900.0 if suspect else 300.0,
            gpu_freq_hz_mean=900.0 if suspect else 300.0,
            idle_window_suspect=suspect,
        )

    def idle_admission_records(self, *, run_id: str, attempt: int):
        index = min(attempt - 1, len(self._cpu_busy_sequence) - 1)
        power_index = min(attempt - 1, len(self._combined_power_sequence) - 1)
        busy = self._cpu_busy_sequence[index]
        power_w = self._combined_power_sequence[power_index]
        return [
            {
                "processor_combined_power_w": power_w,
                "clusters": [
                    {
                        "cpus": [
                            {"idle_ratio": 1.0 - busy, "down_ratio": 0.0},
                            {"idle_ratio": 0.0, "down_ratio": 1.0},
                        ]
                    }
                ],
            }
            for _ in range(30)
        ]


class AdmissionIdleRegistry:
    def __init__(
        self,
        suspect_sequence: list[bool],
        *,
        cpu_busy_sequence: list[float] | None = None,
        combined_power_sequence: list[float] | None = None,
    ) -> None:
        self._suspect_sequence = suspect_sequence
        self._cpu_busy_sequence = cpu_busy_sequence
        self._combined_power_sequence = combined_power_sequence

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        if telemetry is not None:
            telemetry = AdmissionIdleTelemetry(
                telemetry,
                self._suspect_sequence,
                self._cpu_busy_sequence,
                self._combined_power_sequence,
            )
        return telemetry, failure

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class FakeProcessPowermetricsRegistry:
    """Production adapter wired to the process-level synthetic sampler."""

    adapter_type = PowermetricsTelemetryAdapter

    def __init__(self) -> None:
        self.adapter: PowermetricsTelemetryAdapter | None = None

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        self.adapter = self.adapter_type(
            clock,
            executable=str(
                REPO_ROOT / "tests" / "fixtures" / "fake_powermetrics_process.py"
            ),
            privilege_prefix=(sys.executable,),
        )
        return self.adapter, None

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class NonEngagedPowermetricsRegistry:
    """Use the mock telemetry lifecycle under the powermetrics controller seam."""

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        if telemetry is not None:
            telemetry.name = "powermetrics"
        return telemetry, failure

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


class RetryAdmissionPowermetricsAdapter(PowermetricsTelemetryAdapter):
    """Process-backed sampler with deterministic retry CPU conditions."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.concurrent_bounded_capture = False
        self.idle_slice_count = 0

    def _run_bounded_capture(self, *args, **kwargs):
        if self._process is not None:
            self.concurrent_bounded_capture = True
        return super()._run_bounded_capture(*args, **kwargs)

    def _capture_idle_slice(self, *args, **kwargs):
        self.idle_slice_count += 1
        return super()._capture_idle_slice(*args, **kwargs)

    @staticmethod
    def _admission_records(
        records: list[dict[str, Any]], attempt: int
    ) -> list[dict[str, Any]]:
        adjusted = json.loads(json.dumps(records))
        busy_ratio = 0.9 if attempt == 1 else 0.1
        combined_power_w = 2.0 if attempt == 1 else 0.1
        for record in adjusted:
            record["processor_combined_power_w"] = combined_power_w
            for cluster in record.get("clusters", []):
                for cpu in cluster.get("cpus", []):
                    cpu["idle_ratio"] = 1.0 - busy_ratio
                    cpu["down_ratio"] = 0.0
        return adjusted

    def idle_admission_records(self, *, run_id: str, attempt: int):
        records = super().idle_admission_records(run_id=run_id, attempt=attempt)
        if records is None:
            return None
        return self._admission_records(records, attempt)

    def _write_rich_artifact(self, *, context, name, data, error_key) -> None:
        attempt: int | None = None
        if name == RICH_IDLE_NAME:
            attempt = 1
        elif name.startswith("rich_telemetry_idle_attempt_"):
            attempt = int(name.removesuffix(".jsonl").rsplit("_", 1)[-1])
        if attempt is not None:
            records = [json.loads(line) for line in data.splitlines() if line]
            data = rich_telemetry_jsonl_from_records(
                self._admission_records(records, attempt)
            )
        super()._write_rich_artifact(
            context=context,
            name=name,
            data=data,
            error_key=error_key,
        )


class RetryAdmissionPowermetricsRegistry(FakeProcessPowermetricsRegistry):
    adapter_type = RetryAdmissionPowermetricsAdapter


class CleanAdmissionPowermetricsAdapter(RetryAdmissionPowermetricsAdapter):
    @staticmethod
    def _admission_records(
        records: list[dict[str, Any]], attempt: int
    ) -> list[dict[str, Any]]:
        return RetryAdmissionPowermetricsAdapter._admission_records(records, 2)


class CleanAdmissionPowermetricsRegistry(FakeProcessPowermetricsRegistry):
    adapter_type = CleanAdmissionPowermetricsAdapter


def powermetrics_frames(data: bytes) -> list[bytes]:
    return [frame for frame in data.split(b"\0") if frame.strip()]


def assert_contiguous_frame_subsequence(
    testcase: unittest.TestCase,
    stream: bytes,
    logical_slice: bytes,
) -> None:
    stream_frames = powermetrics_frames(stream)
    slice_frames = powermetrics_frames(logical_slice)
    testcase.assertTrue(slice_frames)
    testcase.assertTrue(
        any(
            stream_frames[index : index + len(slice_frames)] == slice_frames
            for index in range(len(stream_frames) - len(slice_frames) + 1)
        ),
        "idle artifact frames must be a contiguous byte-exact stream slice",
    )


def _produce_admission_powermetrics_bundle(
    runs_root: Path,
    run_id: str,
    registry: Any,
) -> tuple[Path, SummaryMetrics]:
    """Produce one strict-valid bundle through the process harness."""

    config_payload = json.loads(EXAMPLE_CONFIG_PATH.read_text())
    config_payload["run_id"] = run_id
    config_payload["hardware_target"].update(
        {"id": "synthetic_mac", "telemetry_backend": "powermetrics"}
    )
    config_payload["sampling"].update(
        {"power_hz": 20.0, "idle_seconds": 1.5}
    )
    config = BenchmarkConfig.from_mapping(config_payload)

    policy_bytes = PRODUCTION_POLICY_PATH.read_bytes()
    policy = CampaignPolicy.from_mapping(json.loads(policy_bytes))
    policy_sha256 = hashlib.sha256(policy_bytes).hexdigest()
    snapshot = {
        "power_source": "AC Power",
        "power": {"external_connected": True},
        "low_power_mode": False,
        "display_power_state": "all_asleep",
        "screensaver_engaged": False,
        "thermal_pressure": "nominal",
    }
    preflight = {
        "schema_version": "joulewise.campaign_environment_preflight.v1",
        "policy_sha256": policy_sha256,
        "snapshot": snapshot,
        "evaluation": evaluate_environment_policy(
            snapshot, policy.environment_guard
        ),
        "override": None,
        "admitted": True,
    }
    binding = {
        "schema_version": policy.schema_version,
        "policy_id": policy.policy_id,
        "policy_version": policy.policy_version,
        "profile": policy.profile.value,
        "sha256": policy_sha256,
        "source": str(PRODUCTION_POLICY_PATH),
    }
    clean_observation = {
        "power_source": "AC Power",
        "display_power_state": "all_asleep",
        "screensaver_engaged": False,
        "power": {
            "adapter_watts": 140.0,
            "adapter_description": "synthetic adapter",
        },
        "errors": {},
    }
    with patch(
        "joulewise.controller.collect_environment_guard_observation",
        side_effect=lambda **_kwargs: json.loads(json.dumps(clean_observation)),
    ):
        return run_benchmark(
            config,
            runs_root,
            SystemClock(),
            registry=registry,
            environment_snapshot=snapshot,
            campaign_policy=policy,
            campaign_policy_binding=binding,
            campaign_environment_preflight=preflight,
            post_window_sampling_dwell_s=1.0,
        )


def produce_retry_powermetrics_bundle(
    runs_root: Path,
    run_id: str,
) -> tuple[Path, SummaryMetrics]:
    return _produce_admission_powermetrics_bundle(
        runs_root,
        run_id,
        RetryAdmissionPowermetricsRegistry(),
    )


def produce_clean_powermetrics_bundle(
    runs_root: Path,
    run_id: str,
) -> tuple[Path, SummaryMetrics]:
    return _produce_admission_powermetrics_bundle(
        runs_root,
        run_id,
        CleanAdmissionPowermetricsRegistry(),
    )


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


class CleanupOutcomeRuntime:
    """Wrap the production-shaped mock runtime with one cleanup mutation."""

    def __init__(self, delegate: Any, *, raises: bool) -> None:
        self._delegate = delegate
        self._raises = raises
        self.name = delegate.name

    def __getattr__(self, name: str) -> Any:
        return getattr(self._delegate, name)

    def cleanup(self, config: BenchmarkConfig, context=None) -> AdapterResult:
        if self._raises:
            raise RuntimeError("injected local cleanup exception")
        return AdapterResult(
            ok=False,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            message="injected local cleanup failure",
        )


class CleanupOutcomeRegistry:
    def __init__(self, *, raises: bool) -> None:
        self._raises = raises

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        runtime, failure = adapters.resolve_runtime(config, clock)
        if runtime is not None:
            runtime = CleanupOutcomeRuntime(runtime, raises=self._raises)
        return runtime, failure

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_telemetry(config, clock)

    def resolve_transport(self, config: BenchmarkConfig):
        return adapters.resolve_transport(config)


def fake_environment_run(command, **kwargs):
    if tuple(command) == ("git", "rev-parse", "HEAD"):
        return subprocess.CompletedProcess(command, 0, "0" * 40 + "\n", "")
    outputs = {
        ("pmset", "-g", "batt"): "Now drawing from 'AC Power'\n -InternalBattery-0 100%; charged; 0:00 remaining\n",
        ("pmset", "-g"): " lowpowermode 0\n",
        ("pmset", "-g", "assertions"): "   PreventUserIdleDisplaySleep    0\n",
        ("pmset", "-g", "systemstate"): "Current System Capabilities: Audio Network\n",
        ("pmset", "-g", "therm"): "No thermal warning level has been recorded\n",
        ("defaults", "-currentHost", "read", "com.apple.screensaver"): (
            "{ moduleDict = { moduleName = Ventura; }; idleTime = 1200; }\n"
        ),
        ("ioreg", "-c", "IOHIDSystem"): '"HIDIdleTime" = 5000000000\n',
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
            energy_request_j=data["energy_request_j"],
            gross_energy_j=data["gross_energy_j"],
            window_evidence_precheck=data.get("window_evidence_precheck"),
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
                FailureReason.MODEL_IDENTITY_MISMATCH: RunStatus.FAILED,
                FailureReason.PERMISSION_DENIED: RunStatus.FAILED,
                FailureReason.TRANSPORT_UNAVAILABLE: RunStatus.FAILED,
                FailureReason.CLEANUP_FAILED: RunStatus.FAILED,
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
        self.assertIs(quality["runtime_cleanup_ok"], True)
        self.assertIs(summary.measurement_quality.runtime_cleanup_ok, True)
        self.assertEqual(data["idle_baseline"]["power_w_mean"], 5.0)
        self.assertEqual(summary.idle_baseline.power_w_mean, 5.0)
        # Real reducer output: energy and per-phase attribution are populated.
        self.assertIsNotNone(summary.gross_energy_j)
        self.assertGreater(summary.gross_energy_j, 0.0)
        self.assertIsNotNone(summary.idle_subtracted_energy_j)
        self.assertEqual(set(summary.phase_energy_j), {"prefill", "decode"})
        self.assertIsNotNone(data["phase_energy_j"])

    def test_warmup_seconds_advances_injected_clock_before_sampling(self) -> None:
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data["run_id"] = "controller-warmup-settle"
        data["sampling"]["warmup_seconds"] = 7.25
        bundle_path, summary = run_benchmark(
            BenchmarkConfig.from_mapping(data), self.runs_root, self.clock
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        events = self.read_events(bundle_path)
        warmup_started = next(
            event
            for event in events
            if event["event_type"] == "stage_started" and event["phase"] == "warmup"
        )
        warmup_completed = next(
            event
            for event in events
            if event["event_type"] == "stage_completed" and event["phase"] == "warmup"
        )
        measured_started = next(
            event
            for event in events
            if event["event_type"] == "stage_started"
            and event["phase"] == "measured_run"
        )
        sampling_started = next(
            event for event in events if event["event_type"] == "sampling_started"
        )
        self.assertAlmostEqual(
            warmup_completed["timestamp_s"] - warmup_started["timestamp_s"],
            7.30,
            places=6,
        )
        self.assertEqual(
            warmup_completed["metadata"],
            {"warmup_runs": 1, "warmup_seconds": 7.25},
        )
        self.assertEqual(
            measured_started["timestamp_s"], warmup_completed["timestamp_s"]
        )
        self.assertEqual(
            sampling_started["timestamp_s"], measured_started["timestamp_s"]
        )
        runtime_log = (bundle_path / "logs/runtime.log").read_text()
        self.assertIn("post-warmup settling for 7.25 s", runtime_log)
        runtime_lines = runtime_log.splitlines()
        active_warmup_done_s = float(
            next(line for line in runtime_lines if "completed 1 warmup run(s)" in line)
            .split(maxsplit=1)[0]
        )
        settle_started_s = float(
            next(line for line in runtime_lines if "post-warmup settling" in line)
            .split(maxsplit=1)[0]
        )
        self.assertAlmostEqual(
            active_warmup_done_s - warmup_started["timestamp_s"], 0.05, places=6
        )
        self.assertEqual(settle_started_s, active_warmup_done_s)
        self.assertAlmostEqual(
            measured_started["timestamp_s"] - settle_started_s, 7.25, places=6
        )

    def test_zero_warmup_seconds_is_a_timing_noop(self) -> None:
        bundle_path, _ = self.run_happy()
        events = self.read_events(bundle_path)
        start_s = next(
            event["timestamp_s"]
            for event in events
            if event["event_type"] == "stage_started" and event["phase"] == "warmup"
        )
        completed = next(
            event
            for event in events
            if event["event_type"] == "stage_completed" and event["phase"] == "warmup"
        )
        self.assertAlmostEqual(completed["timestamp_s"] - start_s, 0.05, places=6)
        self.assertEqual(
            completed["metadata"],
            {"warmup_runs": 1, "warmup_seconds": 0.0},
        )

    def test_config_warnings_are_recorded_in_bundle_metadata(self) -> None:
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data["run_id"] = "controller-config-warning"
        data["sampling"]["power_hzz"] = 99
        with self.assertWarnsRegex(UserWarning, "sampling.power_hzz"):
            config = BenchmarkConfig.from_mapping(data)

        bundle_path, _ = run_benchmark(config, self.runs_root, self.clock)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertEqual(
            metadata["config_warnings"],
            [
                {
                    "code": "unknown_config_key",
                    "message": (
                        "unknown config key 'sampling.power_hzz' ignored by schema 0.1"
                    ),
                    "path": "sampling.power_hzz",
                }
            ],
        )
        normalized = json.loads((bundle_path / "config.json").read_text())
        self.assertNotIn("power_hzz", normalized["sampling"])

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
        # 23 = full snapshot probes + the post-workload guard's display
        # inventory and adapter-power probe.  F6 requires the latter so a
        # final-member renegotiation cannot disappear after the workload.
        self.assertEqual(len(environment_calls), 23)
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
        self.assertEqual(environment["display_power_state"], "all_asleep")
        self.assertIs(environment["screensaver_engaged"], False)
        self.assertEqual(environment["post_run_observation"]["display_power_state"], "all_asleep")
        self.assertEqual(
            environment["post_run_observation"]["power"]["adapter_watts"], 96
        )

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

    def test_production_admission_retry_then_abort_is_fully_evidenced(self) -> None:
        policy, binding, preflight, snapshot = campaign_policy_fixture(
            exploratory=False
        )
        bundle_path, summary = run_benchmark(
            make_config("controller-admission-abort"),
            self.runs_root,
            self.clock,
            registry=AdmissionIdleRegistry([True, True]),
            environment_snapshot=snapshot,
            campaign_policy=policy,
            campaign_policy_binding=binding,
            campaign_environment_preflight=preflight,
        )

        self.assertEqual(summary.status, RunStatus.FAILED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        admission = metadata["environment_admission"]
        self.assertEqual(admission["decision"], "abort")
        self.assertEqual(len(admission["attempts"]), 2)
        self.assertEqual(
            [row["admitted"] for row in admission["attempts"]], [False, False]
        )
        self.assertEqual(
            admission["claim_reason"], "environment_admission_failed"
        )

    def test_exploratory_admission_flag_is_universal_claim_barrier(self) -> None:
        policy, binding, preflight, snapshot = campaign_policy_fixture(
            exploratory=True
        )
        bundle_path, summary = run_benchmark(
            make_config("controller-admission-flag"),
            self.runs_root,
            self.clock,
            registry=AdmissionIdleRegistry([True, True]),
            environment_snapshot=snapshot,
            campaign_policy=policy,
            campaign_policy_binding=binding,
            campaign_environment_preflight=preflight,
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertEqual(metadata["environment_admission"]["decision"], "flagged")
        gates = summary.window_evidence_precheck
        for key in ("gross_request", "idle_subtracted_request", "throughput"):
            self.assertFalse(gates[key]["eligible"])
            self.assertIn(
                "environment_admission_failed", gates[key]["reasons"]
            )
        # Load average is preflight evidence only and does not block admission.
        self.assertEqual(
            preflight["evaluation"]["load_average_evidence"]["load_average_1m"],
            99.0,
        )

    def test_admission_retry_can_recover_on_second_fully_evidenced_window(self) -> None:
        policy, binding, preflight, snapshot = campaign_policy_fixture(
            exploratory=False
        )
        bundle_path, summary = run_benchmark(
            make_config("controller-admission-retry-pass"),
            self.runs_root,
            self.clock,
            registry=AdmissionIdleRegistry([True, False]),
            environment_snapshot=snapshot,
            campaign_policy=policy,
            campaign_policy_binding=binding,
            campaign_environment_preflight=preflight,
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        admission = metadata["environment_admission"]
        self.assertEqual(admission["decision"], "admitted")
        self.assertEqual(len(admission["attempts"]), 2)
        self.assertIs(admission["critical_environment_passed"], True)
        self.assertIs(admission["reference_provenance_present"], True)

    def test_production_cpu_busy_retry_then_abort_is_enforced_pre_invoke(self) -> None:
        policy, binding, preflight, snapshot = campaign_policy_fixture(
            exploratory=False
        )
        bundle_path, summary = run_benchmark(
            make_config("controller-cpu-admission-abort"),
            self.runs_root,
            self.clock,
            registry=AdmissionIdleRegistry(
                [False, False], cpu_busy_sequence=[0.9, 0.8]
            ),
            environment_snapshot=snapshot,
            campaign_policy=policy,
            campaign_policy_binding=binding,
            campaign_environment_preflight=preflight,
        )

        self.assertEqual(summary.status, RunStatus.FAILED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        admission = metadata["environment_admission"]
        self.assertEqual(admission["decision"], "abort")
        self.assertEqual(len(admission["attempts"]), 2)
        self.assertEqual(
            [row["cpu_admission"]["decision"] for row in admission["attempts"]],
            ["failed", "failed"],
        )
        self.assertTrue(
            all(row["gpu_admitted"] for row in admission["attempts"])
        )
        events = self.read_events(bundle_path)
        self.assertNotIn("sampling_started", [event["event_type"] for event in events])

    def test_cpu_retry_ledger_pairs_final_attempt_before_admitting(self) -> None:
        policy, binding, preflight, snapshot = campaign_policy_fixture(
            exploratory=False
        )
        bundle_path, summary = run_benchmark(
            make_config("controller-cpu-admission-retry-pass"),
            self.runs_root,
            self.clock,
            registry=AdmissionIdleRegistry(
                [False, False], cpu_busy_sequence=[0.9, 0.1]
            ),
            environment_snapshot=snapshot,
            campaign_policy=policy,
            campaign_policy_binding=binding,
            campaign_environment_preflight=preflight,
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        admission = json.loads((bundle_path / "metadata.json").read_text())[
            "environment_admission"
        ]
        self.assertEqual(admission["decision"], "admitted")
        self.assertEqual(
            [row["attempt"] for row in admission["attempts"]], [1, 2]
        )
        self.assertEqual(
            [row["admitted"] for row in admission["attempts"]], [False, True]
        )
        self.assertGreater(
            admission["attempts"][0]["cpu_admission"]["cpu_busy_ratio_p95"],
            admission["attempts"][1]["cpu_admission"]["cpu_busy_ratio_p95"],
        )

    def test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce(
        self,
    ) -> None:
        from joulewise.cli import validate_bundle
        from joulewise.reduce import reduce_bundle

        registry = RetryAdmissionPowermetricsRegistry()
        bundle_path, summary = _produce_admission_powermetrics_bundle(
            self.runs_root,
            "controller-powermetrics-retry-pass",
            registry,
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        attempts = metadata["environment_admission"]["attempts"]
        self.assertEqual(
            [row["cpu_admission"]["decision"] for row in attempts],
            ["failed", "admitted"],
        )
        self.assertEqual([row["admitted"] for row in attempts], [False, True])

        canonical = bundle_path / "raw" / "powermetrics_idle.plist"
        attempt_one = bundle_path / "raw" / "powermetrics_idle_attempt_1.plist"
        attempt_two = bundle_path / "raw" / "powermetrics_idle_attempt_2.plist"
        stream = (bundle_path / "raw" / "powermetrics.plist").read_bytes()
        self.assertEqual(canonical.read_bytes(), attempt_two.read_bytes())
        self.assertNotEqual(attempt_one.read_bytes(), attempt_two.read_bytes())
        assert_contiguous_frame_subsequence(self, stream, attempt_one.read_bytes())
        assert_contiguous_frame_subsequence(self, stream, attempt_two.read_bytes())
        self.assertIsInstance(registry.adapter, RetryAdmissionPowermetricsAdapter)
        assert isinstance(registry.adapter, RetryAdmissionPowermetricsAdapter)
        self.assertEqual(registry.adapter.idle_slice_count, 2)
        self.assertFalse(registry.adapter.concurrent_bounded_capture)
        self.assertIsNone(registry.adapter._process)
        self.assertFalse(registry.adapter._admission_sampling_start_requested)
        self.assertFalse(registry.adapter._admission_sampling_handoff_pending)
        teardown = metadata["uncertainty_evidence"]["process_group_teardown"]
        self.assertEqual(
            set(teardown),
            {
                "status",
                "spawn_observed",
                "isolation_mode",
                "direct_child_pid",
                "process_group_id",
                "spawn_argv",
                "sampler_argv",
                "termination_signal",
                "termination_grace_s",
                "kill_escalated",
                "census_method",
                "census_timeout_s",
                "census_completed",
                "survivors_detected",
                "group_survivors",
                "escaped_candidates",
                "signal_attempts",
                "leader_reaped",
                "exception_class",
                "errors",
            },
        )
        self.assertEqual(teardown["status"], "clean")
        self.assertTrue(teardown["spawn_observed"])
        self.assertIn(
            teardown["isolation_mode"], {"isolated_group", "none_direct_child"}
        )
        self.assertFalse(teardown["survivors_detected"])
        self.assertEqual(teardown["termination_grace_s"], 10.0)
        command = metadata["adapters"]["telemetry"]["command"]
        self.assertNotIn("-n", command)
        self.assertEqual(
            command[command.index("--samplers") + 1],
            "cpu_power,gpu_power,ane_power,thermal",
        )
        self.assertEqual(validate_bundle(bundle_path, strict=True), [])
        fresh = reduce_bundle(bundle_path)
        self.assertEqual(fresh.status, RunStatus.SUCCEEDED)
        self.assertEqual(
            fresh.idle_mean_uncertainty["source_artifact"],
            "raw/powermetrics_idle.plist",
        )
        self.assertEqual(
            fresh.idle_mean_uncertainty["source_sha256"],
            hashlib.sha256(attempt_two.read_bytes()).hexdigest(),
        )

    def test_powermetrics_without_custodied_spawn_succeeds_not_engaged(
        self,
    ) -> None:
        bundle_path, summary = run_benchmark(
            make_config("controller-powermetrics-not-engaged"),
            self.runs_root,
            self.clock,
            registry=NonEngagedPowermetricsRegistry(),
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        teardown = metadata["uncertainty_evidence"]["process_group_teardown"]
        self.assertEqual(teardown["status"], "not_engaged")
        self.assertFalse(teardown["spawn_observed"])
        self.assertEqual(teardown["isolation_mode"], "not_spawned")
        self.assertFalse(teardown["census_completed"])

    def test_powermetrics_contaminated_teardown_census_fails_run_closed(
        self,
    ) -> None:
        escaped = {"pid": 999999, "argv": ["injected", "escaped", "sampler"]}
        with patch.object(
            SamplerTeardown, "_wide_argv_census", return_value=[escaped]
        ):
            bundle_path, summary = _produce_admission_powermetrics_bundle(
                self.runs_root,
                "controller-powermetrics-contaminated-teardown",
                RetryAdmissionPowermetricsRegistry(),
            )

        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertIn("teardown census reported contamination", summary.failure_message)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        teardown = metadata["uncertainty_evidence"]["process_group_teardown"]
        self.assertEqual(teardown["status"], "contaminated")
        self.assertTrue(teardown["spawn_observed"])
        self.assertTrue(teardown["survivors_detected"])
        self.assertEqual(teardown["escaped_candidates"], [escaped])

    def test_powermetrics_teardown_exception_persists_unknown_custody(
        self,
    ) -> None:
        with patch.object(
            SamplerTeardown,
            "_wide_argv_census",
            side_effect=OSError("injected mid-teardown census failure"),
        ):
            bundle_path, summary = _produce_admission_powermetrics_bundle(
                self.runs_root,
                "controller-powermetrics-exceptional-teardown",
                RetryAdmissionPowermetricsRegistry(),
            )

        self.assertEqual(summary.status, RunStatus.FAILED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        teardown = metadata["uncertainty_evidence"]["process_group_teardown"]
        self.assertEqual(teardown["status"], "contamination_unknown")
        self.assertNotEqual(teardown["status"], "clean")
        self.assertEqual(teardown["exception_class"], "OSError")
        self.assertFalse(teardown["census_completed"])
        self.assertTrue(
            any(
                "injected mid-teardown census failure" in error
                for error in teardown["errors"]
            )
        )

    def test_powermetrics_thermal_coverage_is_continuous_across_admission_handoff(
        self,
    ) -> None:
        from joulewise.environment_admission import (
            _window_thermal_pressure_refusals,
        )
        from joulewise.bundle_read import BundleReader
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V3

        config_payload = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        config_payload["run_id"] = "controller-thermal-admission-handoff"
        config_payload["hardware_target"].update(
            {
                "id": "synthetic_mac",
                "telemetry_backend": "powermetrics",
            }
        )
        config_payload["sampling"].update(
            {"power_hz": 20.0, "idle_seconds": 0.2}
        )
        config = BenchmarkConfig.from_mapping(config_payload)

        policy_payload = json.loads(PRODUCTION_POLICY_PATH.read_text())
        criteria = policy_payload["idle_admission_extension"]["cpu_criteria"]
        criteria.update(
            {
                "cpu_busy_ratio_p95_max": 0.6,
                "processor_combined_power_w_p95_max": 2.0,
                "min_samples": 3,
            }
        )
        policy = CampaignPolicy.from_mapping(policy_payload)
        snapshot = {
            "power_source": "AC Power",
            "power": {"external_connected": True},
            "low_power_mode": False,
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "thermal_pressure": "nominal",
        }
        evaluation = evaluate_environment_policy(snapshot, policy.environment_guard)
        binding = {
            "schema_version": policy.schema_version,
            "policy_id": policy.policy_id,
            "policy_version": policy.policy_version,
            "profile": policy.profile.value,
            "sha256": "a" * 64,
            "source": str(PRODUCTION_POLICY_PATH),
        }
        preflight = {
            "schema_version": "joulewise.campaign_environment_preflight.v1",
            "policy_sha256": binding["sha256"],
            "snapshot": snapshot,
            "evaluation": evaluation,
            "override": None,
            "admitted": True,
        }
        clean_observation = {
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "power": {
                "adapter_watts": 140.0,
                "adapter_description": "synthetic adapter",
            },
            "errors": {},
        }
        registry = FakeProcessPowermetricsRegistry()
        with patch(
            "joulewise.controller.collect_environment_guard_observation",
            side_effect=lambda **_kwargs: json.loads(json.dumps(clean_observation)),
        ):
            bundle_path, summary = run_benchmark(
                config,
                self.runs_root,
                SystemClock(),
                registry=registry,
                environment_snapshot=snapshot,
                campaign_policy=policy,
                campaign_policy_binding=binding,
                campaign_environment_preflight=preflight,
                post_window_sampling_dwell_s=1.0,
            )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNotNone(registry.adapter)
        assert registry.adapter is not None
        self.assertIsNone(registry.adapter._process)
        self.assertFalse(registry.adapter._admission_sampling_handoff_pending)
        assert_contiguous_frame_subsequence(
            self,
            (bundle_path / "raw" / "powermetrics.plist").read_bytes(),
            (bundle_path / "raw" / "powermetrics_idle.plist").read_bytes(),
        )
        self.assertFalse(
            (bundle_path / "raw" / "powermetrics_idle_attempt_1.plist").exists()
        )
        reader = BundleReader(bundle_path)
        window = reader.measured_window()
        self.assertIsNotNone(window)
        assert window is not None
        metadata = reader.metadata()
        anchor = metadata["uncertainty_evidence"]["clock_anchor"]
        # This process fixture has only a few seconds of native capture, so
        # current v3 correctly refuses its 60-second rate-fit requirement.
        # The handoff assertion must instead isolate the coverage consumer's
        # use of the controller-persisted v3 identity.  A v2/absent controller
        # presentation makes the dispatch assertion below fail (A9 kill).
        self.assertEqual(anchor["method"], CLOCK_METHOD_V3)

        def bounded_v3_reconstruction(*, records, **_kwargs):
            return {
                "status": "bounded",
                "first_sample_end_point_epoch_s": records[0].native_timestamp_s,
            }

        with patch(
            "joulewise.uncertainty_evidence.resolve_anchor_reconstructor",
            return_value=bounded_v3_reconstruction,
        ) as resolver:
            self.assertEqual(
                _window_thermal_pressure_refusals(
                    metadata,
                    bundle_path=bundle_path,
                    measured_window_start_s=window.start_s,
                    measured_window_end_s=window.end_s,
                ),
                (),
            )
        resolver.assert_called_once_with(CLOCK_METHOD_V3)

    def test_powermetrics_abort_before_admission_capture_clears_handoff_state(
        self,
    ) -> None:
        adapter = PowermetricsTelemetryAdapter(FakeClock())
        adapter._capability = AdapterResult(ok=True)
        config = make_config("controller-powermetrics-abort-latch")

        class InterruptedProcess:
            def __init__(self) -> None:
                self.returncode = None
                self.terminated = False

            def poll(self):
                return self.returncode

            def terminate(self):
                self.terminated = True
                self.returncode = 0

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        process = InterruptedProcess()

        def interrupted_start(*_args, **_kwargs):
            adapter._process = process
            raise KeyboardInterrupt

        with (
            patch.object(adapter, "start_sampling", side_effect=interrupted_start),
            self.assertRaises(KeyboardInterrupt),
        ):
            adapter.begin_admission_window_sampling(config)

        self.assertFalse(adapter._admission_sampling_start_requested)
        self.assertIs(adapter._process, process)
        self.assertEqual(adapter.stop_sampling(config), [])
        self.assertTrue(process.terminated)
        self.assertFalse(adapter._admission_sampling_handoff_pending)
        self.assertIsNone(adapter._admission_sampling_metadata)
        self.assertIsNone(adapter._process)

        admitted_process = InterruptedProcess()

        def successful_start(*_args, **_kwargs):
            metadata = {"command": ["powermetrics", "--samplers", "thermal"]}
            adapter._process = admitted_process
            adapter._admission_sampling_metadata = dict(metadata)
            return AdapterResult(ok=True, metadata=metadata)

        with patch.object(adapter, "start_sampling", side_effect=successful_start):
            result = adapter.begin_admission_window_sampling(config)
        self.assertTrue(result.ok)
        self.assertTrue(adapter._admission_sampling_handoff_pending)
        self.assertEqual(adapter.stop_sampling(config), [])
        self.assertTrue(admitted_process.terminated)
        self.assertFalse(adapter._admission_sampling_start_requested)
        self.assertFalse(adapter._admission_sampling_handoff_pending)
        self.assertIsNone(adapter._admission_sampling_metadata)
        self.assertIsNone(adapter._process)

        def failed_rollover(*_args, **_kwargs):
            adapter._admission_sampling_metadata = {"stale": True}
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.UNKNOWN_ERROR,
                message="rollover failed",
            )

        with patch.object(adapter, "start_sampling", side_effect=failed_rollover):
            result = adapter.begin_admission_window_sampling(config)
        self.assertFalse(result.ok)
        self.assertFalse(adapter._admission_sampling_start_requested)
        self.assertFalse(adapter._admission_sampling_handoff_pending)
        self.assertIsNone(adapter._admission_sampling_metadata)

    def test_exploratory_cpu_failure_is_lenient_but_claim_flagged(self) -> None:
        policy, binding, preflight, snapshot = campaign_policy_fixture(
            exploratory=True
        )
        bundle_path, summary = run_benchmark(
            make_config("controller-cpu-admission-exploratory"),
            self.runs_root,
            self.clock,
            registry=AdmissionIdleRegistry(
                [False, False], combined_power_sequence=[2.0, 2.0]
            ),
            environment_snapshot=snapshot,
            campaign_policy=policy,
            campaign_policy_binding=binding,
            campaign_environment_preflight=preflight,
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        admission = json.loads((bundle_path / "metadata.json").read_text())[
            "environment_admission"
        ]
        self.assertEqual(admission["decision"], "flagged")
        self.assertFalse(
            admission["idle_admission_extension"]["claim_bearing"]
        )
        self.assertIn(
            "processor_combined_power_w_p95_exceeded",
            admission["attempts"][-1]["cpu_admission"]["conditions"],
        )
        self.assertIn(
            "environment_admission_failed",
            summary.window_evidence_precheck["gross_request"]["reasons"],
        )

    def test_production_missing_cpu_telemetry_fails_closed_on_live_clock(self) -> None:
        policy, binding, preflight, snapshot = campaign_policy_fixture(
            exploratory=False
        )
        clean_guard = {
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "screensaver_module": "Ventura",
            "screensaver_delay_s": 1200,
            "hid_idle_s": 5.0,
            "power": {
                "adapter_watts": 140.0,
                "adapter_description": "140W USB-C Power Adapter",
            },
            "errors": {},
        }
        with patch(
            "joulewise.controller.collect_environment_guard_observation",
            return_value=clean_guard,
        ):
            bundle_path, summary = run_benchmark(
                make_config("controller-cpu-admission-missing-live"),
                self.runs_root,
                DeterministicClock(),
                environment_snapshot=snapshot,
                campaign_policy=policy,
                campaign_policy_binding=binding,
                campaign_environment_preflight=preflight,
            )

        self.assertEqual(summary.status, RunStatus.FAILED)
        admission = json.loads((bundle_path / "metadata.json").read_text())[
            "environment_admission"
        ]
        self.assertEqual(admission["decision"], "abort")
        self.assertEqual(len(admission["attempts"]), 2)
        self.assertTrue(admission["attempts"][-1]["cpu_admission_enforced"])
        self.assertIn(
            "cpu_baseline_telemetry_missing",
            admission["attempts"][-1]["cpu_admission"]["conditions"],
        )

    def test_extension_sidecar_reparses_in_child_environment_path(self) -> None:
        policy, _binding, preflight, snapshot = campaign_policy_fixture(
            exploratory=False
        )
        raw = PRODUCTION_POLICY_PATH.read_bytes()
        policy_sha = hashlib.sha256(raw).hexdigest()
        preflight["policy_sha256"] = policy_sha
        with patch.dict(
            os.environ,
            {
                CAMPAIGN_POLICY_PATH_ENV: str(PRODUCTION_POLICY_PATH),
                CAMPAIGN_POLICY_SHA256_ENV: policy_sha,
                CAMPAIGN_PREFLIGHT_JSON_ENV: json.dumps(preflight),
            },
            clear=False,
        ):
            bundle_path, summary = run_benchmark(
                make_config("controller-child-extension-sidecar"),
                self.runs_root,
                self.clock,
                registry=AdmissionIdleRegistry([False]),
                environment_snapshot=snapshot,
            )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertEqual(
            metadata["campaign_policy"]["idle_admission_extension"][
                "schema_version"
            ],
            policy.idle_admission_extension.schema_version,
        )

    def test_post_capture_guard_observation_aborts_awake_display(self) -> None:
        policy, binding, preflight, snapshot = campaign_policy_fixture(
            exploratory=False
        )
        clean = {
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "screensaver_module": "Ventura",
            "screensaver_delay_s": 1200,
            "hid_idle_s": 5.0,
            "errors": {},
        }
        awake = {**clean, "display_power_state": "any_awake"}
        with patch(
            "joulewise.controller.collect_environment_guard_observation",
            side_effect=[clean, awake],
        ) as collect_guard:
            bundle_path, summary = run_benchmark(
                make_config("controller-post-capture-awake"),
                self.runs_root,
                DeterministicClock(),
                registry=AdmissionIdleRegistry([False]),
                environment_snapshot=snapshot,
                campaign_policy=policy,
                campaign_policy_binding=binding,
                campaign_environment_preflight=preflight,
            )

        self.assertEqual(summary.status, RunStatus.FAILED)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        admission = metadata["environment_admission"]
        self.assertEqual(admission["decision"], "abort")
        self.assertIn("display became or remained awake", admission["failure"])
        self.assertEqual(
            [row["phase"] for row in admission["guard_observations"]],
            ["before_attempt_1", "after_attempt_1"],
        )
        self.assertTrue(
            all(
                call.kwargs == {"include_adapter_power": True}
                for call in collect_guard.call_args_list
            )
        )

    def test_environment_override_makes_member_universally_claim_ineligible(self) -> None:
        policy, binding, preflight, snapshot = campaign_policy_fixture(
            exploratory=False
        )
        preflight["override"] = {
            "schema_version": "joulewise.environment_override.v1",
            "snapshot_sha256": preflight["evaluation"]["snapshot_sha256"],
            "findings_sha256": preflight["evaluation"]["findings_sha256"],
            "reason": "operator accepted exact preflight for exploratory collection",
            "approver": "fixture-owner",
            "timestamp": "2026-07-17T00:00:00Z",
            "classification": "override",
            "claim_eligible": False,
        }
        bundle_path, summary = run_benchmark(
            make_config("controller-environment-override"),
            self.runs_root,
            self.clock,
            registry=AdmissionIdleRegistry([False]),
            environment_snapshot=snapshot,
            campaign_policy=policy,
            campaign_policy_binding=binding,
            campaign_environment_preflight=preflight,
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        for key in ("gross_request", "idle_subtracted_request", "throughput"):
            self.assertIn(
                "environment_override",
                summary.window_evidence_precheck[key]["reasons"],
            )
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertEqual(
            metadata["campaign_environment_preflight"]["override"][
                "classification"
            ],
            "override",
        )

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
            metadata["workload_observed"]["output_token_count"],
            workload["output_policy"]["emitted_tokens"],
        )
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
        sentinel = SummaryMetrics(
            status=RunStatus.SUCCEEDED,
            energy_request_j=12.5,
            gross_energy_j=14.0,
        )
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


class CleanupQualityTests(ControllerTestCase):
    def _run_cleanup_mutation(self, *, raises: bool) -> tuple[Path, SummaryMetrics]:
        return run_benchmark(
            make_config(f"cleanup-quality-{'raise' if raises else 'false'}"),
            self.runs_root,
            self.clock,
            registry=CleanupOutcomeRegistry(raises=raises),
        )

    def _assert_cleanup_quality_false(
        self, bundle_path: Path, summary: SummaryMetrics
    ) -> None:
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNone(summary.failure_reason)
        self.assertIs(summary.measurement_quality.runtime_cleanup_ok, False)
        stored = json.loads((bundle_path / "summary_metrics.json").read_text())
        self.assertEqual(stored["status"], "succeeded")
        self.assertIsNone(stored["failure_reason"])
        self.assertIs(stored["measurement_quality"]["runtime_cleanup_ok"], False)
        cleanup = next(
            event
            for event in self.read_events(bundle_path)
            if event["event_type"] == "stage_completed" and event["phase"] == "cleanup"
        )
        self.assertIs(cleanup["metadata"]["cleanup_ok"], False)

    def test_cleanup_adapter_failure_surfaces_without_retroactive_run_failure(self) -> None:
        self._assert_cleanup_quality_false(*self._run_cleanup_mutation(raises=False))

    def test_cleanup_exception_surfaces_without_retroactive_run_failure(self) -> None:
        self._assert_cleanup_quality_false(*self._run_cleanup_mutation(raises=True))


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
        self.assertIsNone(summary.measurement_quality.runtime_cleanup_ok)

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
        self.assertIsNone(data["measurement_quality"]["runtime_cleanup_ok"])
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


class InterruptFinalizationTests(ControllerTestCase):
    def test_interrupt_during_sampler_start_stops_potentially_live_sampler(self) -> None:
        registry = InterruptDuringStartRegistry()
        config = make_config("controller-interrupt-during-sampler-start")

        with self.assertRaisesRegex(KeyboardInterrupt, "after sampler start"):
            run_benchmark(
                config,
                self.runs_root,
                self.clock,
                registry=registry,
            )

        assert registry.telemetry is not None
        self.assertEqual(registry.telemetry.stop_calls, 1)
        self.assertFalse(registry.telemetry.live)
        bundle_path = self.runs_root / config.run_id
        self.assert_complete_bundle(bundle_path)
        events = self.read_events(bundle_path)
        self.assertNotIn("sampling_started", [event["event_type"] for event in events])

    def test_interrupt_after_start_transition_stops_before_custody_salvage(self) -> None:
        capture_path = self.runs_root / "native-transition-capture"
        registry = InterruptAfterStartTransitionRegistry(capture_path)
        config = make_config("controller-interrupt-after-start-transition")

        with self.assertRaisesRegex(KeyboardInterrupt, "post-start alignment"):
            run_benchmark(
                config,
                self.runs_root,
                self.clock,
                registry=registry,
            )

        assert registry.telemetry is not None
        self.assertEqual(registry.telemetry.stop_calls, 1)
        self.assertFalse(registry.telemetry.live)
        self.assertEqual(registry.telemetry.salvage_calls, 1)
        self.assertEqual(capture_path.read_bytes(), b"native capture survives\n")

    def test_interrupt_after_successful_stop_does_not_double_stop(self) -> None:
        registry = InterruptAfterStopRegistry()
        config = make_config("controller-interrupt-after-successful-stop")

        with self.assertRaisesRegex(KeyboardInterrupt, "after successful stop"):
            run_benchmark(
                config,
                self.runs_root,
                self.clock,
                registry=registry,
            )

        assert registry.telemetry is not None
        self.assertEqual(registry.telemetry.stop_calls, 1)
        self.assertEqual(len(registry.telemetry.stop_records), 1)
        self.assert_complete_bundle(self.runs_root / config.run_id)

    def test_keyboardinterrupt_and_systemexit_survive_cleanup_failures(self) -> None:
        cases = [
            (
                "keyboard",
                KeyboardInterrupt("primary keyboard interrupt"),
                SystemExit("cleanup system exit"),
            ),
            (
                "system-exit",
                SystemExit("primary system exit"),
                KeyboardInterrupt("cleanup keyboard interrupt"),
            ),
        ]
        for suffix, primary, cleanup_error in cases:
            with self.subTest(primary=type(primary).__name__):
                runtime = InterruptingCleanupRuntime(primary, cleanup_error)
                registry = InterruptingCleanupRegistry(runtime)
                config = make_config("controller-interrupt-" + suffix)

                with self.assertRaises(type(primary)) as caught:
                    run_benchmark(
                        config,
                        self.runs_root,
                        self.clock,
                        registry=registry,
                    )

                self.assertEqual(str(caught.exception), str(primary))
                self.assertEqual(runtime.cleanup_calls, 1)
                bundle_path = self.runs_root / config.run_id
                self.assert_complete_bundle(bundle_path)
                stored = self.assert_summary_round_trips(bundle_path)
                self.assertIn(type(primary).__name__, stored["failure_message"])
                controller_log = (bundle_path / "logs" / "controller.log").read_text()
                self.assertIn(type(cleanup_error).__name__, controller_log)
                self.assertIn(str(cleanup_error), controller_log)


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
        # Must not raise: structured quarantine preserves D-011.
        bundle_path, summary = self.run_poison()
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assert_complete_bundle(bundle_path)
        data = self.assert_summary_round_trips(bundle_path)
        self.assertEqual(data["status"], "failed")

    def test_events_end_with_run_finalized(self) -> None:
        bundle_path, _ = self.run_poison()
        events = self.read_events(bundle_path)
        self.assert_run_finalized_last(events)
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertIsNone(metadata["device"]["poison"])
        self.assertEqual(metadata["device"]["cycle"], {"self": None})
        self.assertIsNone(metadata["device"]["not_finite"])
        self.assertNotIn("7", metadata["device"])
        diagnostics = metadata["serialization_quarantine"]
        self.assertEqual(
            [(item["path"], item["reason"]) for item in diagnostics],
            [
                ("/device", "non_string_key"),
                ("/device/cycle/self", "cycle"),
                ("/device/not_finite", "non_finite_number"),
                ("/device/poison", "unsupported_type"),
            ],
        )


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


class AlignmentCostTelemetry:
    """Wraps the mock telemetry with a ``clock_alignments()`` getter whose
    call costs simulated time - the controller captures alignments after the
    runtime returns, and that work must stay outside the measured window
    (D-013 quiescent window, D-026 markers)."""

    def __init__(self, inner: Any, clock: Clock, cost_s: float) -> None:
        self._inner = inner
        self._clock = clock
        self._cost_s = cost_s

    def clock_alignments(self) -> list[dict[str, Any]]:
        self._clock.sleep(self._cost_s)
        return []

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class AlignmentCostRegistry:
    """Real mock adapters, telemetry wrapped with costly alignment capture."""

    def __init__(self, clock: Clock, cost_s: float) -> None:
        self._clock = clock
        self._cost_s = cost_s

    def resolve_runtime(self, config: BenchmarkConfig, clock: Clock):
        return adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config: BenchmarkConfig, clock: Clock):
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        if telemetry is not None:
            telemetry = AlignmentCostTelemetry(telemetry, self._clock, self._cost_s)
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
    def test_non_campaign_powermetrics_dwell_default_is_one_second(self) -> None:
        from joulewise.controller import DEFAULT_POWERMETRICS_POST_WINDOW_DWELL_S

        self.assertEqual(DEFAULT_POWERMETRICS_POST_WINDOW_DWELL_S, 1.0)

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

    def run_with_alignment_cost(
        self, run_id: str, cost_s: float
    ) -> tuple[Path, SummaryMetrics]:
        # The mock workload lasts ~0.1 s; sample fast enough that regular
        # 1/power_hz-spaced samples land inside the measured window even when
        # alignment-capture cost inflates the sampler's active span.
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data["run_id"] = run_id
        data["sampling"]["power_hz"] = 100.0
        config = BenchmarkConfig.from_mapping(data)
        clock = FakeClock(start=1_700_000_000.0)
        registry = AlignmentCostRegistry(clock, cost_s)
        return run_benchmark(config, self.runs_root, clock, registry=registry)

    def test_alignment_capture_cost_does_not_change_measured_metrics(self) -> None:
        # Adapter clock_alignments() capture after the runtime returns must
        # not be integrated into the measured window (D-013).
        _, baseline_summary = self.run_with_alignment_cost("alignment-zero", 0.0)
        _, costly_summary = self.run_with_alignment_cost("alignment-cost", 5.0)

        self.assertEqual(baseline_summary.status, RunStatus.SUCCEEDED)
        self.assertEqual(costly_summary.status, RunStatus.SUCCEEDED)
        for metric in (
            "gross_energy_j",
            "idle_subtracted_energy_j",
            "energy_request_j",
            "ttft_s",
            "decode_latency_s",
        ):
            self.assertAlmostEqual(
                getattr(baseline_summary, metric),
                getattr(costly_summary, metric),
                places=9,
                msg=metric,
            )

    def test_stop_marker_is_stamped_before_alignment_capture(self) -> None:
        # The sampling_stopped timestamp is taken as soon as the runtime
        # returns; a costly post-run alignment capture must not push it later.
        bundle_path, _ = self.run_with_alignment_cost("alignment-marker", 5.0)
        events = self.read_events(bundle_path)
        stopped_s = next(
            event["timestamp_s"]
            for event in events
            if event["event_type"] == "sampling_stopped"
        )
        last_runtime_s = max(
            event["timestamp_s"]
            for event in events
            if event["event_type"] == "phase_end"
        )
        self.assertAlmostEqual(stopped_s - last_runtime_s, 0.0, places=9)

    def test_post_window_dwell_changes_tail_support_without_moving_marker(self) -> None:
        # T1 defect shape: immediate sampler stop leaves the last sample before
        # the stop marker; an injected dwell retains post-window support while
        # the measured marker (and therefore energy window) stays unchanged.
        zero_bundle, _ = run_benchmark(
            make_config("tail-zero"),
            self.runs_root,
            FakeClock(start=1_700_000_000.0),
            post_window_sampling_dwell_s=0.0,
        )
        dwell_bundle, _ = run_benchmark(
            make_config("tail-dwell"),
            self.runs_root,
            FakeClock(start=1_700_000_000.0),
            post_window_sampling_dwell_s=0.75,
        )
        zero_metadata = json.loads((zero_bundle / "metadata.json").read_text())
        dwell_metadata = json.loads((dwell_bundle / "metadata.json").read_text())
        zero_margins = zero_metadata["trace_window_margins"]
        dwell_margins = dwell_metadata["trace_window_margins"]

        self.assertLess(zero_margins["achieved_post_window_margin_s"], 0.0)
        self.assertGreaterEqual(
            dwell_margins["achieved_post_window_margin_s"], 0.60
        )
        self.assertEqual(dwell_margins["requested_post_window_dwell_s"], 0.75)
        zero_stopped = next(
            event["timestamp_s"]
            for event in self.read_events(zero_bundle)
            if event["event_type"] == "sampling_stopped"
        )
        dwell_stopped = next(
            event["timestamp_s"]
            for event in self.read_events(dwell_bundle)
            if event["event_type"] == "sampling_stopped"
        )
        self.assertEqual(zero_stopped, dwell_stopped)

    def test_powermetrics_rejects_subsecond_post_window_dwell_before_collection(self) -> None:
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data["run_id"] = "tail-subsecond-refusal"
        data["hardware_target"]["telemetry_backend"] = "powermetrics"
        config = BenchmarkConfig.from_mapping(data)

        with self.assertRaisesRegex(ValueError, "at least 1.0 s"):
            run_benchmark(
                config,
                self.runs_root,
                FakeClock(start=1_700_000_000.0),
                post_window_sampling_dwell_s=0.999,
            )
        self.assertFalse((self.runs_root / "tail-subsecond-refusal").exists())

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
        persisted_manifest = json.loads(
            (bundle_path / "suite_manifest.json").read_text()
        )
        self.assertEqual(persisted_manifest["schema_version"], SUITE_SCHEMA_VERSION)
        self.assertEqual(
            persisted_manifest["execution_policy"]["cache_policy_verification"],
            "declared_not_verified",
        )
        self.assertNotIn(
            "cache_policy", persisted_manifest["execution_policy"]
        )
        self.assertTrue(
            all("status_policy" not in item for item in persisted_manifest["items"])
        )
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertEqual(metadata["suite"]["suite_id"], "mock_suite_smoke")
        persisted_hash = suite_manifest_sha256(persisted_manifest)
        self.assertEqual(metadata["suite"]["manifest_sha256"], persisted_hash)
        persisted_config = json.loads((bundle_path / "config.json").read_text())
        source_manifest = json.loads(SUITE_MANIFEST_PATH.read_text())
        self.assertEqual(
            persisted_config["workload_profile"]["suite_manifest_sha256"],
            suite_manifest_sha256(source_manifest),
        )
        self.assertNotEqual(
            persisted_config["workload_profile"]["suite_manifest_sha256"],
            persisted_hash,
        )
        self.assertEqual(
            persisted_manifest, migrate_suite_manifest(source_manifest)
        )
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

    def test_suite_controller_passes_controller_derived_order_seed_to_runtime(self) -> None:
        config = make_suite_config("suite-seed__r3")
        bundle_path, summary = run_benchmark(config, self.runs_root, self.clock)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        manifest = json.loads(SUITE_MANIFEST_PATH.read_text())
        expected = order_seed(
            manifest["suite_seed"],
            manifest["execution_policy"]["order_policy"],
            3,
        )
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        events = self.read_events(bundle_path)
        suite_start = next(event for event in events if event["event_type"] == "suite_start")
        self.assertEqual(metadata["suite"]["order_seed"], expected)
        self.assertEqual(suite_start["metadata"]["order_seed"], expected)
        self.assertEqual(
            metadata["workload_provenance"]["suite"]["order_seed"],
            expected,
        )

    def test_suite_manifest_ref_relative_to_cwd_from_repo_root(self) -> None:
        data = json.loads(SUITE_CONFIG_PATH.read_text())
        manifest = json.loads(SUITE_MANIFEST_PATH.read_text())
        data["run_id"] = "suite-relative-ref"
        data["workload_profile"]["suite_manifest_ref"] = (
            "configs/suite_manifests/mock_suite_manifest.json"
        )
        data["workload_profile"]["suite_manifest_sha256"] = suite_manifest_sha256(manifest)
        old_cwd = Path.cwd()
        try:
            os.chdir(REPO_ROOT)
            bundle_path, summary = run_benchmark(
                BenchmarkConfig.from_mapping(data), self.runs_root, self.clock
            )
        finally:
            os.chdir(old_cwd)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertTrue((bundle_path / "suite_manifest.json").is_file())

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
            self.assertEqual(metadata["suite"]["order_row"], rep)


if __name__ == "__main__":
    unittest.main()
