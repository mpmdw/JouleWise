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

Implemented backends in this slice: runtime ``mock`` and ``mlx``, telemetry
``mock`` and ``powermetrics``, transport ``local``. Clock-driven adapters receive the injected
:class:`joulewise.clock.Clock` (D-019).
"""

from __future__ import annotations

import importlib

from joulewise.adapters.local_transport import LocalTransport
from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.adapters.mock_telemetry import MockTelemetryAdapter
from joulewise.clock import Clock
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
    "PowermetricsTelemetryAdapter",
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
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _backend_name(backend: object) -> str:
    return str(getattr(backend, "value", backend))


def _failure(reason: FailureReason, message: str) -> tuple[None, AdapterResult]:
    return None, AdapterResult(ok=False, failure_reason=reason, message=message)


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
    return _failure(
        FailureReason.TRANSPORT_UNAVAILABLE,
        f"transport '{_backend_name(transport)}' has no registered adapter",
    )
