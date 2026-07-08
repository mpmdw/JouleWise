"""Adapter registry: backend enum -> adapter factory (decisions D-009, D-019).

The controller resolves adapters exclusively through this registry. Each
resolver returns a ``(adapter, failure)`` pair in which exactly one element
is non-None: a backend with a registered implementation yields the adapter;
any other backend yields a structured ``AdapterResult`` failure naming the
backend - the registry never raises. Unavailable backends map to
``runtime_unavailable`` / ``telemetry_unavailable`` / ``transport_unavailable``
so the controller's status mapping (D-012) applies uniformly. Real backends
land here in later slices (2G, 2H, 2K, 2L) behind lazy imports per the
stdlib-core/extras policy (D-009).

Implemented backends in this slice: runtime ``mock``, ``mlx``, and remote
``vllm``; telemetry ``mock``, ``powermetrics``, and remote ``nvidia_smi``;
transport ``local`` and ``ssh``. Clock-driven adapters receive the injected
:class:`joulewise.clock.Clock` (D-019).
"""

from __future__ import annotations

import importlib

from joulewise.adapters.local_transport import LocalTransport
from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.adapters.mock_telemetry import MockTelemetryAdapter
from joulewise.clock import Clock, SystemClock
from joulewise.interfaces import (
    AdapterResult,
    RuntimeAdapter,
    TelemetryAdapter,
    TransportAdapter,
)
from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    RuntimeBackend,
    TelemetryBackend,
    TransportKind,
)

__all__ = [
    "LocalTransport",
    "MlxRuntimeAdapter",
    "MockRuntimeAdapter",
    "MockTelemetryAdapter",
    "NvidiaSmiTelemetryAdapter",
    "PowermetricsTelemetryAdapter",
    "SshTransport",
    "VllmRuntimeAdapter",
    "resolve_runtime",
    "resolve_telemetry",
    "resolve_transport",
]


def __getattr__(name: str) -> object:
    if name == "MlxRuntimeAdapter":
        module = importlib.import_module("joulewise.adapters.mlx_runtime")
        return module.MlxRuntimeAdapter
    if name == "PowermetricsTelemetryAdapter":
        module = importlib.import_module("joulewise.adapters.powermetrics")
        return module.PowermetricsTelemetryAdapter
    if name == "SshTransport":
        module = importlib.import_module("joulewise.adapters.ssh_transport")
        return module.SshTransport
    if name == "VllmRuntimeAdapter":
        module = importlib.import_module("joulewise.adapters.vllm_runtime")
        return module.VllmRuntimeAdapter
    if name == "NvidiaSmiTelemetryAdapter":
        module = importlib.import_module("joulewise.adapters.nvidia_smi")
        return module.NvidiaSmiTelemetryAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _backend_name(backend: object) -> str:
    return str(getattr(backend, "value", backend))


def _failure(reason: FailureReason, message: str) -> tuple[None, AdapterResult]:
    return None, AdapterResult(ok=False, failure_reason=reason, message=message)


def _remote_node_client(config: BenchmarkConfig, clock: Clock):
    target = config.hardware_target
    if target.transport != TransportKind.SSH:
        return _failure(
            FailureReason.TRANSPORT_UNAVAILABLE,
            "remote node adapters require transport 'ssh'",
        )
    if not target.host:
        return _failure(
            FailureReason.TRANSPORT_UNAVAILABLE,
            "remote node adapters require hardware_target.host for ssh transport",
        )
    try:
        transport_module = importlib.import_module("joulewise.adapters.ssh_transport")
        client_module = importlib.import_module("joulewise.adapters.node_client")
    except ImportError as exc:
        return _failure(
            FailureReason.TRANSPORT_UNAVAILABLE,
            f"remote node transport/client could not import: {exc}",
        )
    try:
        transport = transport_module.SshTransport(clock, target.host)
        client = client_module.NodeWorkerClient(
            transport,
            clock,
        )
    except Exception as exc:  # noqa: BLE001 - registry resolution stays structured
        return _failure(
            FailureReason.TRANSPORT_UNAVAILABLE,
            f"remote node client could not be constructed: {exc}",
        )
    return client, None


def resolve_runtime(
    config: BenchmarkConfig, clock: Clock
) -> tuple[RuntimeAdapter | None, AdapterResult | None]:
    """Resolve the configured runtime backend to an adapter or a failure."""
    backend = config.hardware_target.runtime_backend
    if backend == RuntimeBackend.MOCK:
        return MockRuntimeAdapter(clock), None
    if backend == RuntimeBackend.MLX:
        try:
            module = importlib.import_module("joulewise.adapters.mlx_runtime")
        except ImportError as exc:
            return _failure(
                FailureReason.RUNTIME_UNAVAILABLE,
                "runtime backend 'mlx' could not import its adapter; the MLX "
                "runtime requires the [mac] extra "
                f"(pip install 'joulewise[mac]'; D-009): {exc}",
            )
        return module.MlxRuntimeAdapter(clock), None
    if backend == RuntimeBackend.VLLM:
        client, failure = _remote_node_client(config, clock)
        if client is None:
            return None, failure
        try:
            module = importlib.import_module("joulewise.adapters.vllm_runtime")
        except ImportError as exc:
            return _failure(
                FailureReason.RUNTIME_UNAVAILABLE,
                f"runtime backend 'vllm' could not import its adapter: {exc}",
            )
        return module.VllmRuntimeAdapter(clock, client), None
    return _failure(
        FailureReason.RUNTIME_UNAVAILABLE,
        f"runtime backend '{_backend_name(backend)}' has no registered adapter",
    )


def resolve_telemetry(
    config: BenchmarkConfig, clock: Clock
) -> tuple[TelemetryAdapter | None, AdapterResult | None]:
    """Resolve the configured telemetry backend to an adapter or a failure."""
    backend = config.hardware_target.telemetry_backend
    if backend == TelemetryBackend.MOCK:
        return MockTelemetryAdapter(clock), None
    if backend == TelemetryBackend.POWERMETRICS:
        try:
            module = importlib.import_module("joulewise.adapters.powermetrics")
        except ImportError as exc:
            return _failure(
                FailureReason.TELEMETRY_UNAVAILABLE,
                "telemetry backend 'powermetrics' could not import its adapter: "
                f"{exc}",
            )
        return module.PowermetricsTelemetryAdapter(clock), None
    if backend == TelemetryBackend.NVIDIA_SMI:
        client, failure = _remote_node_client(config, clock)
        if client is None:
            return None, failure
        try:
            module = importlib.import_module("joulewise.adapters.nvidia_smi")
        except ImportError as exc:
            return _failure(
                FailureReason.TELEMETRY_UNAVAILABLE,
                f"telemetry backend 'nvidia_smi' could not import its adapter: {exc}",
            )
        return module.NvidiaSmiTelemetryAdapter(clock, client), None
    return _failure(
        FailureReason.TELEMETRY_UNAVAILABLE,
        f"telemetry backend '{_backend_name(backend)}' has no registered adapter",
    )


def resolve_transport(
    config: BenchmarkConfig,
) -> tuple[TransportAdapter | None, AdapterResult | None]:
    """Resolve the configured transport kind to an adapter or a failure."""
    transport = config.hardware_target.transport
    if transport == TransportKind.LOCAL:
        return LocalTransport(), None
    if transport == TransportKind.SSH:
        if not config.hardware_target.host:
            return _failure(
                FailureReason.TRANSPORT_UNAVAILABLE,
                "transport 'ssh' requires hardware_target.host",
            )
        try:
            module = importlib.import_module("joulewise.adapters.ssh_transport")
            return module.SshTransport(SystemClock(), config.hardware_target.host), None
        except ImportError as exc:
            return _failure(
                FailureReason.TRANSPORT_UNAVAILABLE,
                f"transport 'ssh' could not import its adapter: {exc}",
            )
        except Exception as exc:  # noqa: BLE001 - registry resolution stays structured
            return _failure(
                FailureReason.TRANSPORT_UNAVAILABLE,
                f"transport 'ssh' could not be constructed: {exc}",
            )
    return _failure(
        FailureReason.TRANSPORT_UNAVAILABLE,
        f"transport '{_backend_name(transport)}' has no registered adapter",
    )
