"""Adapter protocol contracts for JouleWise."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from joulewise.schemas import BenchmarkConfig, FailureReason, IdleBaseline


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

    def prepare(self, config: BenchmarkConfig) -> AdapterResult:
        """Prepare runtime dependencies and model state."""

    def warmup(self, config: BenchmarkConfig) -> AdapterResult:
        """Run warmup work outside the measured interval."""

    def run_workload(self, config: BenchmarkConfig) -> RuntimeResult:
        """Run the configured workload and return output/event artifacts."""

    def cleanup(self, config: BenchmarkConfig) -> AdapterResult:
        """Release runtime resources."""


@runtime_checkable
class TelemetryAdapter(Protocol):
    """Measures power and thermal state for a target."""

    name: str

    def device_metadata(self, config: BenchmarkConfig) -> dict[str, Any]:
        """Return device and telemetry metadata."""

    def measure_idle(self, config: BenchmarkConfig) -> IdleBaseline:
        """Measure idle power before a benchmark run."""

    def start_sampling(self, config: BenchmarkConfig) -> AdapterResult:
        """Start power sampling for the measured interval."""

    def stop_sampling(self, config: BenchmarkConfig) -> list[PowerSample]:
        """Stop sampling and return raw power samples."""

    def thermal_state(self, config: BenchmarkConfig) -> ThermalState:
        """Return current thermal state when available."""


@runtime_checkable
class TransportAdapter(Protocol):
    """Executes commands and moves artifacts for local or remote targets."""

    name: str

    def connection_metadata(self, config: BenchmarkConfig) -> dict[str, Any]:
        """Return connection metadata for the target."""

    def run_command(self, config: BenchmarkConfig, command: list[str]) -> AdapterResult:
        """Run a command on the target transport."""

    def collect_artifact(self, config: BenchmarkConfig, source: str, destination: str) -> AdapterResult:
        """Collect an artifact into the controller run bundle."""
