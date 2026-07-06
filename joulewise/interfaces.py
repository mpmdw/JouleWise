"""Adapter protocol contracts for JouleWise."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from joulewise.clock import Clock
from joulewise.schemas import BenchmarkConfig, FailureReason, IdleBaseline


@dataclass(frozen=True)
class RunContext:
    """Immutable per-run context passed to adapter lifecycle methods (D-024).

    Context is data, not capability: adapters receive paths and identity, never
    the bundle writer, so write-order and immutability invariants stay with the
    controller and :class:`joulewise.bundle.RunBundleWriter`. ``raw_dir`` is
    where a real telemetry adapter preserves its native sampler output verbatim
    (D-002; e.g. the powermetrics plist). ``node_role`` is ``None`` for
    single-node runs and is reserved for Phase 3 split orchestration (D-008);
    it rides along now so the v0.2 compatibility check can exercise it without
    a schema change (R-015).

    Placement (D-024 amendment, pinned during 2N.1): every lifecycle method
    takes a trailing ``context: RunContext | None = None`` parameter. The
    controller always passes the context; out-of-run invocations - the D-014
    cooldown gate's ``measure_idle`` between repetitions, direct adapter tests -
    pass ``None``, which adapters must tolerate by producing no raw output.
    """

    config: BenchmarkConfig
    clock: Clock
    run_id: str
    bundle_path: Path
    raw_dir: Path
    logs_dir: Path
    outputs_dir: Path
    node_role: str | None = None


@dataclass(frozen=True)
class AdapterResult:
    ok: bool
    metadata: dict[str, Any] = field(default_factory=dict)
    failure_reason: FailureReason | None = None
    message: str | None = None


@dataclass(frozen=True)
class RuntimeEvent:
    timestamp_s: float
    event_type: str
    phase: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeResult:
    events: list[RuntimeEvent]
    output_artifacts: dict[str, str] = field(default_factory=dict)
    token_count: int | None = None
    output_token_count: int | None = None


@dataclass(frozen=True)
class PowerSample:
    timestamp_s: float
    power_w: float
    source: str
    rail: str | None = None


@dataclass(frozen=True)
class ThermalState:
    timestamp_s: float
    temperature_c: float | None = None
    thermal_pressure: str | None = None
    fan_state: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class RuntimeAdapter(Protocol):
    """Executes model workloads and emits phase events."""

    name: str

    def prepare(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        """Prepare runtime dependencies and model state."""

    def warmup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        """Run warmup work outside the measured interval."""

    def run_workload(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> RuntimeResult:
        """Run the configured workload and return output/event artifacts."""

    def cleanup(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        """Release runtime resources."""


@runtime_checkable
class TelemetryAdapter(Protocol):
    """Measures power and thermal state for a target."""

    name: str

    def device_metadata(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> dict[str, Any]:
        """Return device and telemetry metadata."""

    def measure_idle(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> IdleBaseline:
        """Measure idle power before a benchmark run."""

    def start_sampling(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        """Start power sampling for the measured interval."""

    def stop_sampling(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> list[PowerSample]:
        """Stop sampling and return raw power samples; preserve native raw
        output verbatim under ``context.raw_dir`` when a context is given
        (D-002)."""

    def thermal_state(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> ThermalState:
        """Return current thermal state when available."""


@runtime_checkable
class TransportAdapter(Protocol):
    """Executes commands and moves artifacts for local or remote targets."""

    name: str

    def connection_metadata(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> dict[str, Any]:
        """Return connection metadata for the target."""

    def run_command(
        self,
        config: BenchmarkConfig,
        command: list[str],
        context: RunContext | None = None,
    ) -> AdapterResult:
        """Run a command on the target transport."""

    def collect_artifact(
        self,
        config: BenchmarkConfig,
        source: str,
        destination: str,
        context: RunContext | None = None,
    ) -> AdapterResult:
        """Collect an artifact into the controller run bundle."""
