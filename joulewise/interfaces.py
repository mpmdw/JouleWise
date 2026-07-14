"""Adapter protocol contracts for JouleWise."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Protocol, runtime_checkable

from joulewise.clock import Clock, ClockStamp
from joulewise.schemas import BenchmarkConfig, FailureReason, IdleBaseline

if TYPE_CHECKING:
    from joulewise.suite import SuiteManifest


@dataclass(frozen=True)
class DurableCustodyAcknowledgement:
    """On-disk proof that opaque-token evidence reached bundle custody.

    The token is intentionally transport- and protocol-agnostic.  WO-010 can
    therefore use its per-dispatch correlation token without changing this
    acknowledgement seam.
    """

    token: str
    acknowledgement_path: Path
    artifact_paths: tuple[Path, ...]


def acknowledge_durable_custody(
    bundle_path: Path,
    token: str,
    artifact_paths: Iterable[Path],
) -> DurableCustodyAcknowledgement:
    """Atomically persist bundle-local custody proof for ``token``.

    Merely holding artifact bytes or a temporary collection directory does
    not satisfy this contract.  Every named artifact must already exist under
    the bundle, and the acknowledgement itself is flushed and atomically
    replaced before it is returned to a cleanup caller.
    """

    if not isinstance(token, str) or not token:
        raise ValueError("custody token must be a non-empty string")
    bundle = Path(bundle_path).resolve()
    artifacts: list[Path] = []
    for candidate in artifact_paths:
        path = Path(candidate).resolve()
        try:
            path.relative_to(bundle)
        except ValueError as exc:
            raise ValueError("custody artifact must be inside the run bundle") from exc
        if not path.exists():
            raise FileNotFoundError(path)
        if path.is_dir() and not any(candidate.is_file() for candidate in path.rglob("*")):
            raise ValueError("custody artifact directory contains no evidence files")
        artifacts.append(path)
    if not artifacts:
        raise ValueError("custody acknowledgement requires at least one artifact")

    for artifact in artifacts:
        candidates = (
            [path for path in artifact.rglob("*") if path.is_file()]
            if artifact.is_dir()
            else [artifact]
        )
        for candidate in candidates:
            file_descriptor = os.open(candidate, os.O_RDONLY)
            try:
                os.fsync(file_descriptor)
            finally:
                os.close(file_descriptor)

    ack_dir = bundle / "logs" / "custody"
    ack_dir.mkdir(parents=True, exist_ok=True)
    safe_token = "".join(character for character in token if character.isalnum() or character in "-_")
    if not safe_token or safe_token != token:
        raise ValueError("custody token is not a safe acknowledgement filename")
    ack_path = ack_dir / (safe_token + ".json")
    payload = {
        "schema_version": 1,
        "custody_token": token,
        "artifacts": sorted(str(path.relative_to(bundle)) for path in artifacts),
    }
    handle = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        prefix=".custody-",
        suffix=".tmp",
        dir=ack_dir,
        delete=False,
    )
    temporary_path = Path(handle.name)
    try:
        with handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, ack_path)
        directory_fd = os.open(ack_dir, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary_path.unlink(missing_ok=True)
    return DurableCustodyAcknowledgement(token, ack_path, tuple(artifacts))


@dataclass(frozen=True)
class RunContext:
    """Immutable per-run context passed to adapter lifecycle methods (D-024).

    Context carries only narrowly bounded bundle capabilities: adapters never
    receive the bundle writer, so its write-order invariants stay with the
    controller and :class:`joulewise.bundle.RunBundleWriter`; they may persist
    raw artifacts and an opaque durable-custody acknowledgement. ``raw_dir`` is
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

    def acknowledge_custody(
        self,
        token: str,
        artifact_paths: Iterable[Path],
    ) -> DurableCustodyAcknowledgement:
        """Return durable bundle-local proof suitable for destructive cleanup."""

        return acknowledge_durable_custody(self.bundle_path, token, artifact_paths)


@dataclass(frozen=True)
class AdapterResult:
    ok: bool
    metadata: dict[str, Any] = field(default_factory=dict)
    failure_reason: FailureReason | None = None
    message: str | None = None


class AdapterFailure(Exception):
    """Structured adapter failure for lifecycle methods without AdapterResult.

    Most lifecycle methods report operational failures through
    :class:`AdapterResult`. A few legacy-shaped methods return data directly
    (for example ``TelemetryAdapter.measure_idle``), so they use this exception
    to preserve the same stable ``FailureReason`` without smuggling sentinel
    values into measurement objects.
    """

    def __init__(
        self,
        failure_reason: FailureReason,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.failure_reason = failure_reason
        self.message = message
        self.metadata = dict(metadata) if metadata else {}


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
    workload_provenance: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PowerSample:
    timestamp_s: float
    power_w: float
    source: str
    rail: str | None = None


@dataclass(frozen=True)
class TelemetryStopResult:
    """Measured samples plus adapter-derived uncertainty provenance."""

    samples: list[PowerSample]
    uncertainty_evidence: dict[str, Any]


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
class SuiteRuntimeAdapter(RuntimeAdapter, Protocol):
    """Runtime adapter that can execute a materialized suite manifest."""

    def run_suite(
        self,
        config: BenchmarkConfig,
        manifest: "SuiteManifest",
        context: RunContext | None = None,
        *,
        order_seed: str,
        order_row: int | None = None,
    ) -> RuntimeResult:
        """Run every suite item inside one measured adapter call."""


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
class BoundedTelemetryAdapter(Protocol):
    """Optional telemetry extension for per-run clock/phase evidence."""

    def stop_sampling_with_evidence(
        self,
        config: BenchmarkConfig,
        context: RunContext | None,
        *,
        sampling_started: ClockStamp,
        sampling_stopped: ClockStamp,
    ) -> TelemetryStopResult:
        """Stop sampling and return evidence tied to controller markers."""


@runtime_checkable
class IdleDriftEvidenceProvider(Protocol):
    """Optional post-window sentinel extension for empirical idle drift."""

    def measure_post_run_idle(
        self,
        config: BenchmarkConfig,
        baseline: IdleBaseline,
        context: RunContext | None,
    ) -> dict[str, Any]:
        """Collect the post-run sentinel and return its derivation record."""


@runtime_checkable
class EvidenceCustodyProvider(Protocol):
    """Optional adapter extension for retrying native evidence preservation."""

    def salvage_custody(self, context: RunContext) -> list[dict[str, Any]]:
        """Retry pending bundle writes without deleting unacknowledged source."""


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
