"""Single-run benchmark controller: lifecycle, status mapping, deferred logging.

Executes one measured run end-to-end (Slice 2C; repetitions and experiment
manifests arrive with the experiment runner in Slice 2F) and applies:

- D-002: raw evidence first - every run, including failed ones, leaves a
  complete bundle whose artifacts can be re-reduced without re-running
  hardware.
- D-003/D-019: every timestamp comes from the injected
  :class:`joulewise.clock.Clock`; this module never reads the wall clock.
- D-011: ``summary_metrics.json`` is the completion marker. No code path
  between ``RunBundleWriter.create`` and ``finalize()`` exits without a
  finalized bundle except process death: stage failures, structured adapter
  failures, and controller bugs alike end in a schema-valid summary.
- D-012: the controller (never the adapters) maps ``FailureReason`` to
  ``RunStatus`` via the module-level :data:`STATUS_BY_REASON` table.
- D-013: controller-as-DUT mitigation - all events and log records buffer in
  memory and flush only after ``stop_sampling``; between ``start_sampling``
  and ``stop_sampling`` the controller does nothing but block on the runtime
  (no file writes, no disk event appends, no logging; the two in-memory
  ``sampling_started``/``sampling_stopped`` marker appends of D-026 are the
  sole - and negligible - buffer touches inside the window).
- D-026: the reducer's measured window is bounded by the
  ``sampling_started``/``sampling_stopped`` marker events (stage boundaries
  are the fallback for pre-2N bundles), so sampler spawn latency and stop-side
  parsing never land inside the integrated window.

Lifecycle stages, in order: ``validate``, ``prepare``, ``idle_baseline``,
``warmup``, ``measured_run``, ``cleanup``, ``reduce``. ``run_finalized``
(appended by the bundle writer) is the finalize marker; there are no stage
events for finalize itself.

The reducer seam: ``run_benchmark(..., reducer=None)`` defaults to
:func:`joulewise.reduce.reduce_bundle` (Slice 2D); an explicit ``reducer``
callable overrides it. The reducer runs inside the reduce stage's failure
wrapping, so a reducer crash becomes the ``unknown_error`` failure path with a
complete bundle. Failure paths never call the reducer - the controller builds
those summaries directly from the partial evidence it already holds.

Event-flush ordering (so the reducer reads a populated ``events.jsonl``):
buffered events are flushed to disk by :meth:`_Execution._flush_events`, which
the reduce stage calls *before* invoking the reducer (after metadata is
written) and which ``_finish`` calls again (idempotently) so failure paths -
which never reach the reduce stage - still flush exactly once before
``finalize()``. ``writer.finalize()`` then appends ``run_finalized`` and writes
``summary_metrics.json`` last (D-011). ``reduce_bundle`` is pure over the
on-disk artifacts (D-002): events are never handed to it in memory.
"""

from __future__ import annotations

import hashlib
import json
import traceback
from collections.abc import Callable
from dataclasses import asdict, replace
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

import joulewise.adapters
from joulewise import reduce as reduce_module
from joulewise.bundle import (
    RunBundleWriter,
    generate_run_id,
    sanitize_id_component,
    write_experiment_manifest,
)
from joulewise.clock import Clock
from joulewise.interfaces import (
    AdapterResult,
    PowerSample,
    RunContext,
    RuntimeAdapter,
    RuntimeEvent,
    RuntimeResult,
    TelemetryAdapter,
    ThermalState,
    TransportAdapter,
)
from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    IdleBaseline,
    MeasurementQuality,
    RunStatus,
    SamplingConfig,
    SummaryMetrics,
    TelemetryBackend,
)

__all__ = [
    "STATUS_BY_REASON",
    "AdapterRegistry",
    "Reducer",
    "cooldown_gate",
    "run_benchmark",
    "run_experiment",
]

#: D-014 cooldown gate constants (idle-power recovery between live reps).
#: A short idle sub-window is measured repeatedly; a rolling mean over the last
#: ``COOLDOWN_ROLLING_WINDOW_S`` of sub-window readings must come within
#: ``COOLDOWN_TOLERANCE`` of the previous rep's baseline, capped at
#: ``COOLDOWN_CAP_S`` from the injected clock.
COOLDOWN_SUBWINDOW_S = 5.0
COOLDOWN_ROLLING_WINDOW_S = 30.0
COOLDOWN_TOLERANCE = 0.10
COOLDOWN_CAP_S = 300.0

#: FailureReason -> RunStatus mapping owned by the controller (D-012).
#: ``unsupported`` is a finding (structural incompatibility of the
#: hardware/runtime/model/workload combination); ``failed`` is an operational
#: problem a configuration or environment change should fix.
STATUS_BY_REASON: dict[FailureReason, RunStatus] = {
    FailureReason.DID_NOT_FIT: RunStatus.UNSUPPORTED,
    FailureReason.FORMAT_UNAVAILABLE: RunStatus.UNSUPPORTED,
    FailureReason.UNSUPPORTED_WORKLOAD: RunStatus.UNSUPPORTED,
    FailureReason.RUNTIME_UNAVAILABLE: RunStatus.UNSUPPORTED,
    FailureReason.TELEMETRY_UNAVAILABLE: RunStatus.UNSUPPORTED,
    FailureReason.PERMISSION_DENIED: RunStatus.FAILED,
    FailureReason.TRANSPORT_UNAVAILABLE: RunStatus.FAILED,
    FailureReason.UNKNOWN_ERROR: RunStatus.FAILED,
}

#: Post-hoc summary derivation over a bundle directory (Slice 2D).
Reducer = Callable[[Path], SummaryMetrics]


class AdapterRegistry(Protocol):
    """Resolution seam: backend enums -> adapters (``joulewise.adapters``)."""

    def resolve_runtime(
        self, config: BenchmarkConfig, clock: Clock
    ) -> tuple[RuntimeAdapter | None, AdapterResult | None]: ...

    def resolve_telemetry(
        self, config: BenchmarkConfig, clock: Clock
    ) -> tuple[TelemetryAdapter | None, AdapterResult | None]: ...

    def resolve_transport(
        self, config: BenchmarkConfig
    ) -> tuple[TransportAdapter | None, AdapterResult | None]: ...


def run_benchmark(
    config: BenchmarkConfig,
    runs_root: Path,
    clock: Clock,
    registry: AdapterRegistry | None = None,
    reducer: Reducer | None = None,
    extra_metadata: dict[str, Any] | None = None,
) -> tuple[Path, SummaryMetrics]:
    """Run one benchmark and return ``(bundle path, summary)``.

    A :class:`~joulewise.schemas.SchemaError` from ``config.validate()`` and a
    :class:`~joulewise.bundle.BundleError` from bundle creation both propagate
    with no bundle on disk (the CLI maps them to exit 2). After the bundle
    exists, every outcome - structured adapter failure, unsupported target,
    or controller bug - finalizes a complete bundle (D-011): unexpected
    exceptions map to ``unknown_error`` with the traceback in
    ``logs/controller.log``. Only a failure of the finalization machinery
    itself propagates.

    ``extra_metadata`` is merged into ``metadata.json`` under the ``extra``
    key. The experiment runner (Slice 2F) uses it to record a cooldown
    cap-hit against the FOLLOWING repetition (``{"cooldown_cap_hit": True}``),
    which the reducer copies into the run's ``measurement_quality``.
    """
    config.validate()
    if registry is None:
        registry = joulewise.adapters
    writer = RunBundleWriter.create(runs_root, config, clock)
    return _Execution(config, writer, clock, registry, reducer, extra_metadata).execute()


class _StageFailure(Exception):
    """Internal control flow: a lifecycle stage failed with a structured reason."""

    def __init__(
        self,
        stage: str,
        reason: FailureReason,
        message: str,
        traceback_text: str | None = None,
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.reason = reason
        self.message = message
        self.traceback_text = traceback_text


def _jsonable(value: Any) -> Any:
    """Recursively convert enums to their values for JSON metadata."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _jsonable(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_jsonable(inner) for inner in value]
    return value


class _Execution:
    """One run's lifecycle state: buffered events/logs and collected evidence."""

    def __init__(
        self,
        config: BenchmarkConfig,
        writer: RunBundleWriter,
        clock: Clock,
        registry: AdapterRegistry,
        reducer: Reducer | None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> None:
        self._config = config
        self._writer = writer
        self._clock = clock
        self._registry = registry
        self._reducer = reducer
        self._extra_metadata = dict(extra_metadata) if extra_metadata else {}
        # D-024: one immutable context, constructed after bundle creation,
        # passed to every adapter lifecycle call. Context is data (paths and
        # identity), never the writer.
        self._context = RunContext(
            config=config,
            clock=clock,
            run_id=writer.run_id,
            bundle_path=writer.path,
            raw_dir=writer.path / "raw",
            logs_dir=writer.path / "logs",
            outputs_dir=writer.path / "outputs",
        )
        # Deferred buffers (D-013): nothing below touches disk until _finish
        # or the explicitly post-window artifact writes.
        self._events: list[RuntimeEvent] = []
        self._controller_log: list[str] = []
        self._runtime_log: list[str] = []
        self._telemetry_log: list[str] = []
        self._current_stage = "run"
        # Collected evidence, populated as stages progress.
        self._transport: TransportAdapter | None = None
        self._runtime: RuntimeAdapter | None = None
        self._telemetry: TelemetryAdapter | None = None
        self._connection_metadata: dict[str, Any] | None = None
        self._device_metadata: dict[str, Any] | None = None
        self._prepare_metadata: dict[str, Any] | None = None
        self._baseline: IdleBaseline | None = None
        self._thermal_pre: ThermalState | None = None
        self._thermal_post: ThermalState | None = None
        self._runtime_result: RuntimeResult | None = None
        self._samples: list[PowerSample] = []
        self._sampling_active = False
        # Idempotence flags so the failure path writes only what is missing.
        self._outputs_written = False
        self._trace_written = False
        self._metadata_written = False
        self._events_flushed = False
        self._events_flushed_count = 0

    # ------------------------------------------------------------------
    # Top level

    def execute(self) -> tuple[Path, SummaryMetrics]:
        try:
            summary = self._run_lifecycle()
        except _StageFailure as failure:
            summary = self._handle_failure(failure)
        except Exception as exc:  # noqa: BLE001 - D-011: a controller bug must still finalize
            summary = self._handle_failure(
                _StageFailure(
                    stage=self._current_stage,
                    reason=FailureReason.UNKNOWN_ERROR,
                    message=f"unexpected {type(exc).__name__}: {exc}",
                    traceback_text=traceback.format_exc(),
                )
            )
        self._finish()
        return self._writer.path, summary

    def _run_lifecycle(self) -> SummaryMetrics:
        self._buffer_event(
            "run_started",
            "run",
            f"run {self._writer.run_id} started",
            {"run_id": self._writer.run_id},
        )
        self._log(self._controller_log, f"run {self._writer.run_id} started")
        self._stage_validate()
        self._stage_prepare()
        self._stage_idle_baseline()
        self._stage_warmup()
        self._stage_measured_run()
        self._stage_cleanup()
        return self._stage_reduce()

    # ------------------------------------------------------------------
    # Stages

    def _stage_validate(self) -> None:
        self._begin_stage("validate")
        transport, failure = self._registry.resolve_transport(self._config)
        if transport is None:
            raise self._resolution_failure("validate", "transport", failure)
        self._transport = transport
        runtime, failure = self._registry.resolve_runtime(self._config, self._clock)
        if runtime is None:
            raise self._resolution_failure("validate", "runtime", failure)
        self._runtime = runtime
        self._log(self._runtime_log, f"resolved runtime adapter '{runtime.name}'")
        telemetry, failure = self._registry.resolve_telemetry(self._config, self._clock)
        if telemetry is None:
            raise self._resolution_failure("validate", "telemetry", failure)
        self._telemetry = telemetry
        self._log(self._telemetry_log, f"resolved telemetry adapter '{telemetry.name}'")
        self._complete_stage(
            "validate",
            {
                "transport": transport.name,
                "runtime": runtime.name,
                "telemetry": telemetry.name,
            },
        )

    def _stage_prepare(self) -> None:
        self._begin_stage("prepare")
        assert self._transport is not None and self._runtime is not None
        assert self._telemetry is not None
        self._connection_metadata = self._transport.connection_metadata(
            self._config, self._context
        )
        self._device_metadata = self._telemetry.device_metadata(self._config, self._context)
        result = self._runtime.prepare(self._config, self._context)
        self._check(result, "prepare", "runtime prepare failed")
        self._prepare_metadata = dict(result.metadata)
        self._log(self._runtime_log, "runtime prepare succeeded")
        self._complete_stage("prepare")

    def _stage_idle_baseline(self) -> None:
        self._begin_stage("idle_baseline")
        assert self._telemetry is not None
        self._baseline = self._telemetry.measure_idle(self._config, self._context)
        self._log(
            self._telemetry_log,
            f"idle baseline: mean {self._baseline.power_w_mean} W over "
            f"{self._baseline.duration_s} s ({self._baseline.sample_count} samples)",
        )
        self._complete_stage(
            "idle_baseline",
            {
                "power_w_mean": self._baseline.power_w_mean,
                "duration_s": self._baseline.duration_s,
            },
        )

    def _stage_warmup(self) -> None:
        self._begin_stage("warmup")
        assert self._runtime is not None
        warmup_runs = self._config.workload_profile.warmup_runs
        for index in range(warmup_runs):
            result = self._runtime.warmup(self._config, self._context)
            self._check(result, "warmup", f"runtime warmup run {index} failed")
        self._log(self._runtime_log, f"completed {warmup_runs} warmup run(s)")
        self._complete_stage("warmup", {"warmup_runs": warmup_runs})

    def _stage_measured_run(self) -> None:
        self._begin_stage("measured_run")
        assert self._runtime is not None and self._telemetry is not None
        self._thermal_pre = self._telemetry.thermal_state(self._config, self._context)
        start_result = self._telemetry.start_sampling(self._config, self._context)
        self._check(start_result, "measured_run", "telemetry start_sampling failed")
        self._sampling_active = True
        # D-026: the measured window the reducer integrates is bounded by the
        # sampling_started/sampling_stopped marker events, not the stage
        # boundaries, so sampler spawn latency (sudo probe, process start,
        # first sample) and stop-side parsing stay outside the window. The
        # start marker is stamped only after start_sampling confirms; the stop
        # marker is stamped before stop_sampling is asked to wind down.
        self._buffer_event(
            "sampling_started", "measured_run", "telemetry sampling confirmed active"
        )
        # D-013 quiescent window: between start_sampling and stop_sampling the
        # controller only blocks on the runtime - no file writes, no disk event
        # appends, no logging (buffers flush after the window).
        runtime_result = self._runtime.run_workload(self._config, self._context)
        # The stop marker's timestamp is captured before stop_sampling so the
        # sampler's wind-down (process stop, plist parsing) stays outside the
        # window; the event itself is appended after the runtime events so the
        # stable flush-sort keeps it bracketing them.
        sampling_stopped_s = self._clock.now()
        self._samples = self._telemetry.stop_sampling(self._config, self._context)
        self._sampling_active = False
        self._runtime_result = runtime_result
        self._thermal_post = self._telemetry.thermal_state(self._config, self._context)
        self._events.extend(runtime_result.events)
        self._events.append(
            RuntimeEvent(
                timestamp_s=sampling_stopped_s,
                event_type="sampling_stopped",
                phase="measured_run",
                message="telemetry sampling stopped",
                metadata={},
            )
        )
        self._write_outputs()
        self._write_trace()
        self._log(
            self._telemetry_log,
            f"measured window captured {len(self._samples)} power sample(s)",
        )
        self._complete_stage(
            "measured_run",
            {
                "sample_count": len(self._samples),
                "runtime_event_count": len(runtime_result.events),
            },
        )

    def _stage_cleanup(self) -> None:
        # Best-effort by design: a cleanup failure on an otherwise-successful
        # run is recorded in the controller log and the stage_completed event
        # metadata but does not change run status.
        self._begin_stage("cleanup")
        assert self._runtime is not None
        metadata: dict[str, Any] = {"cleanup_ok": True}
        try:
            result = self._runtime.cleanup(self._config, self._context)
        except Exception as exc:  # noqa: BLE001 - best-effort cleanup
            metadata = {
                "cleanup_ok": False,
                "message": f"runtime cleanup raised {type(exc).__name__}: {exc}",
            }
            self._log(
                self._controller_log,
                "runtime cleanup raised; run status unchanged (best-effort cleanup)",
            )
            self._log(self._controller_log, traceback.format_exc())
        else:
            if not result.ok:
                metadata = {
                    "cleanup_ok": False,
                    "failure_reason": (
                        result.failure_reason.value if result.failure_reason else None
                    ),
                    "message": result.message,
                }
                self._log(
                    self._controller_log,
                    f"runtime cleanup failed ({result.message}); "
                    "run status unchanged (best-effort cleanup)",
                )
        self._complete_stage("cleanup", metadata)

    def _stage_reduce(self) -> SummaryMetrics:
        self._begin_stage("reduce")
        self._write_metadata()
        # The reducer is a pure function over on-disk artifacts (D-002), so
        # events.jsonl must hold every measurement event (the measured_run
        # window and the token events) BEFORE it runs. _flush_events writes
        # them now; only run_finalized is still appended later by finalize().
        self._flush_events()
        reducer = self._reducer if self._reducer is not None else reduce_module.reduce_bundle
        summary = reducer(self._writer.path)
        self._writer.write_summary(summary)
        self._log(self._controller_log, f"run {self._writer.run_id} succeeded")
        self._complete_stage("reduce")
        return summary

    # ------------------------------------------------------------------
    # Failure path

    def _handle_failure(self, failure: _StageFailure) -> SummaryMetrics:
        self._buffer_event(
            "failure",
            failure.stage,
            failure.message,
            {"failure_reason": failure.reason.value},
        )
        self._log(
            self._controller_log,
            f"failure in stage {failure.stage}: {failure.reason.value}: {failure.message}",
        )
        if failure.traceback_text:
            self._log(self._controller_log, failure.traceback_text)
        self._stop_sampling_best_effort()
        self._cleanup_best_effort()
        # Preserve whatever partial evidence exists (D-002).
        self._write_outputs()
        self._write_trace()
        self._write_metadata()
        summary = SummaryMetrics(
            status=STATUS_BY_REASON[failure.reason],
            failure_reason=failure.reason,
            failure_message=failure.message,
            idle_baseline=self._baseline,
            measurement_quality=self._minimal_quality(),
        )
        self._writer.write_summary(summary)
        return summary

    def _stop_sampling_best_effort(self) -> None:
        if not self._sampling_active or self._telemetry is None:
            return
        self._sampling_active = False
        # D-026: even on the failure path the sampling window gets its closing
        # marker, stamped before the stop call, so post-hoc re-reduction sees
        # the same window semantics as a successful run.
        self._buffer_event(
            "sampling_stopped", "measured_run", "telemetry sampling stopping (failure path)"
        )
        try:
            self._samples = self._telemetry.stop_sampling(self._config, self._context)
        except Exception:  # noqa: BLE001 - evidence salvage must not mask the failure
            self._log(
                self._controller_log,
                "best-effort stop_sampling raised after failure:",
            )
            self._log(self._controller_log, traceback.format_exc())

    def _cleanup_best_effort(self) -> None:
        if self._runtime is None:
            return
        try:
            result = self._runtime.cleanup(self._config, self._context)
        except Exception:  # noqa: BLE001 - best-effort cleanup must not mask the failure
            self._log(
                self._controller_log,
                "best-effort runtime cleanup raised after failure:",
            )
            self._log(self._controller_log, traceback.format_exc())
        else:
            if not result.ok:
                self._log(
                    self._controller_log,
                    f"best-effort runtime cleanup failed after failure: {result.message}",
                )

    # ------------------------------------------------------------------
    # Artifact writes (idempotent so the failure path writes only the missing)

    def _write_outputs(self) -> None:
        if self._outputs_written or self._runtime_result is None:
            return
        for name, text in self._runtime_result.output_artifacts.items():
            self._writer.write_output(name, text)
        self._outputs_written = True

    def _write_trace(self) -> None:
        # Skip entirely when no samples were collected: a failure before the
        # measured window leaves no power_trace.csv.
        if self._trace_written or not self._samples:
            return
        self._writer.write_power_trace(self._samples)
        self._trace_written = True

    def _write_metadata(self) -> None:
        if self._metadata_written:
            return
        extra: dict[str, Any] = {}
        extra["model"] = _jsonable(asdict(self._config.model))
        extra["quantization"] = _jsonable(asdict(self._config.quantization))
        if self._device_metadata is not None:
            extra["device"] = _jsonable(self._device_metadata)
        if self._connection_metadata is not None:
            extra["connection"] = _jsonable(self._connection_metadata)
        adapters: dict[str, Any] = {}
        if self._runtime is not None:
            adapters["runtime"] = {
                "name": self._runtime.name,
                "prepare_metadata": self._prepare_metadata or {},
            }
        if self._telemetry is not None:
            adapters["telemetry"] = {"name": self._telemetry.name}
        extra["adapters"] = adapters
        if self._baseline is not None:
            extra["idle_baseline"] = _jsonable(asdict(self._baseline))
        if self._thermal_pre is not None:
            extra["thermal_pre"] = _jsonable(asdict(self._thermal_pre))
        if self._thermal_post is not None:
            extra["thermal_post"] = _jsonable(asdict(self._thermal_post))
        if self._runtime_result is not None:
            extra["workload_observed"] = {
                "token_count": self._runtime_result.token_count,
                "output_token_count": self._runtime_result.output_token_count,
            }
        # Caller-supplied metadata (Slice 2F: the experiment runner records a
        # cooldown cap-hit against the following rep here). Lands under the
        # dedicated "extra" key so it never collides with controller fields and
        # the reducer reads it from one known place.
        if self._extra_metadata:
            extra["extra"] = _jsonable(self._extra_metadata)
        self._writer.write_metadata(extra)
        self._metadata_written = True

    # ------------------------------------------------------------------
    # Summaries

    def _minimal_quality(self) -> MeasurementQuality:
        return MeasurementQuality(
            requested_sampling_hz=self._config.sampling.power_hz,
            idle_power_w_stddev=(
                self._baseline.power_w_stddev if self._baseline is not None else None
            ),
            telemetry_source=self._telemetry.name if self._telemetry is not None else None,
        )

    # ------------------------------------------------------------------
    # Buffers and flush

    def _buffer_event(
        self,
        event_type: str,
        phase: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._events.append(
            RuntimeEvent(
                timestamp_s=self._clock.now(),
                event_type=event_type,
                phase=phase,
                message=message,
                metadata=metadata or {},
            )
        )

    def _begin_stage(self, name: str) -> None:
        self._current_stage = name
        self._buffer_event("stage_started", name, f"stage {name} started")

    def _complete_stage(self, name: str, metadata: dict[str, Any] | None = None) -> None:
        self._buffer_event("stage_completed", name, f"stage {name} completed", metadata)

    def _log(self, buffer: list[str], message: str) -> None:
        buffer.append(f"{self._clock.now():.6f} {message}")

    def _check(self, result: AdapterResult, stage: str, default_message: str) -> None:
        if result.ok:
            return
        reason = result.failure_reason or FailureReason.UNKNOWN_ERROR
        raise _StageFailure(stage, reason, result.message or default_message)

    @staticmethod
    def _resolution_failure(
        stage: str, kind: str, failure: AdapterResult | None
    ) -> _StageFailure:
        if failure is not None and failure.failure_reason is not None:
            return _StageFailure(
                stage,
                failure.failure_reason,
                failure.message or f"could not resolve {kind} adapter",
            )
        return _StageFailure(
            stage,
            FailureReason.UNKNOWN_ERROR,
            f"registry returned no {kind} adapter and no structured failure",
        )

    def _flush_events(self) -> None:
        """Append every buffered event to ``events.jsonl`` exactly once.

        Called by ``_stage_reduce`` before the reducer runs (so the reducer
        reads a populated log, D-002) and again by ``_finish`` so the failure
        paths - which never reach ``_stage_reduce`` - flush before finalize. A
        repeat call appends only events buffered since the previous flush (e.g.
        the reduce ``stage_completed`` event, buffered after the in-reduce
        flush), so no event is written twice. Within each flushed batch a
        stable sort by timestamp keeps controller stage boundaries bracketing
        the runtime events they enclose; the trailing batch's events are
        strictly later than the first batch's, so global order is preserved.
        """
        pending = self._events[self._events_flushed_count :]
        for event in sorted(pending, key=lambda event: event.timestamp_s):
            self._writer.append_event(event)
        self._events_flushed_count = len(self._events)
        self._events_flushed = True

    def _finish(self) -> None:
        """Flush buffered logs and events, then finalize (D-011, D-013)."""
        self._flush_log("controller.log", self._controller_log)
        self._flush_log("runtime.log", self._runtime_log)
        self._flush_log("telemetry.log", self._telemetry_log)
        self._flush_events()
        self._writer.finalize()

    def _flush_log(self, name: str, records: list[str]) -> None:
        path = self._writer.log_path(name)
        if records:
            path.write_text("".join(record + "\n" for record in records))
        else:
            path.write_text("no records\n")


# ---------------------------------------------------------------------------
# Cooldown gate (D-014: idle-power recovery between live repetitions)


def cooldown_gate(
    telemetry: TelemetryAdapter,
    reference_baseline: IdleBaseline,
    config: BenchmarkConfig,
    clock: Clock,
) -> dict[str, Any]:
    """Hold until idle power recovers to within 10% of ``reference_baseline``.

    D-014's idle-power recovery gate: repeatedly measure short (~5 s) idle
    sub-windows via ``telemetry.measure_idle`` on a sampling config trimmed to
    ``COOLDOWN_SUBWINDOW_S``, keep a rolling mean over the last 30 s of
    sub-window readings, and return once that rolling mean is within 10% of the
    reference baseline's mean. A 300 s cap from the injected ``clock`` bounds
    the wait. Returns ``{"result": "recovered" | "cap_hit", "waited_s": float}``
    (the caller adds ``after_member``). On ``cap_hit`` the caller records
    ``cooldown_cap_hit=True`` against the NEXT rep's ``run_benchmark``.

    All blocking is via ``telemetry.measure_idle`` (which sleeps on the clock),
    so a ``FakeClock`` makes the gate instant and exact in tests.
    """
    reference = reference_baseline.power_w_mean
    sub_config = replace(
        config,
        sampling=replace(config.sampling, idle_seconds=COOLDOWN_SUBWINDOW_S),
    )
    start_s = clock.now()
    # Each reading carries (timestamp_s, mean) so the rolling mean spans only
    # the most recent COOLDOWN_ROLLING_WINDOW_S of readings.
    readings: list[tuple[float, float]] = []
    while True:
        baseline = telemetry.measure_idle(sub_config)
        now_s = clock.now()
        readings.append((now_s, baseline.power_w_mean))
        cutoff = now_s - COOLDOWN_ROLLING_WINDOW_S
        readings = [reading for reading in readings if reading[0] >= cutoff]
        rolling_mean = sum(value for _, value in readings) / len(readings)
        waited_s = now_s - start_s
        if _within_tolerance(rolling_mean, reference, COOLDOWN_TOLERANCE):
            return {"result": "recovered", "waited_s": waited_s}
        if waited_s >= COOLDOWN_CAP_S:
            return {"result": "cap_hit", "waited_s": waited_s}


def _within_tolerance(value: float, reference: float, tolerance: float) -> bool:
    """True when ``value`` is within ``tolerance`` (fraction) of ``reference``.

    When the reference is exactly zero the tolerance band collapses to an exact
    match (a degenerate baseline that cannot meaningfully define a 10% band).
    """
    return abs(value - reference) <= tolerance * abs(reference)


# ---------------------------------------------------------------------------
# Experiment runner (D-005: one bundle per rep + experiment manifest;
# D-014: cooldown gate between live reps)


def run_experiment(
    config: BenchmarkConfig,
    runs_root: Path,
    clock: Clock,
    registry: AdapterRegistry | None = None,
) -> tuple[Path, list[tuple[Path, SummaryMetrics]]]:
    """Run ``repetitions`` measured runs and group them by an experiment manifest.

    Returns ``(manifest path, [(bundle path, summary), ...])`` in executed
    order. Each member is one ``run_benchmark`` call on a config whose ``run_id``
    is ``<experiment_id>__rN`` (D-010); ``run_benchmark`` already runs exactly
    one measured run per call (it ignores ``repetitions``).

    The manifest is rewritten after EVERY completed rep (D-005), so a killed
    experiment leaves a valid manifest of exactly the members that finished.
    Between live reps the D-014 cooldown gate runs (skipped for mock telemetry,
    which has no thermal reality to wait for); a cap hit is recorded against the
    following rep's ``measurement_quality``.
    """
    if registry is None:
        registry = joulewise.adapters

    experiment_id = (
        sanitize_id_component(config.run_id)
        if config.run_id is not None
        else generate_run_id(config, clock)
    )
    # The config hash identifies the experiment's shared configuration as given
    # (including its run_id) - BEFORE per-member run_id replacement - matching
    # the bundle writer's D-001 hash over sorted-key, 2-space-indented JSON.
    config_sha256 = _config_sha256(config)
    created_at_s = clock.now()
    condition_name = config.workload_profile.name
    repetitions = config.workload_profile.repetitions

    manifest: dict[str, Any] = {
        "experiment_id": experiment_id,
        "config_sha256": config_sha256,
        "created_at_s": created_at_s,
        "members": [],
        "condition_order": [],
        "cooldown": [],
    }

    results: list[tuple[Path, SummaryMetrics]] = []
    manifest_path: Path | None = None
    # Pending cap-hit recorded against the NEXT rep's run_benchmark.
    next_extra_metadata: dict[str, Any] | None = None

    for rep in range(1, repetitions + 1):
        member_config = replace(config, run_id=f"{experiment_id}__r{rep}")
        bundle_path, summary = run_benchmark(
            member_config,
            runs_root,
            clock,
            registry=registry,
            extra_metadata=next_extra_metadata,
        )
        next_extra_metadata = None
        results.append((bundle_path, summary))
        manifest["members"].append(bundle_path.name)
        manifest["condition_order"].append(condition_name)
        # Incremental write: a kill before the next rep leaves a valid manifest
        # listing exactly the members that completed (D-005 acceptance).
        manifest_path = write_experiment_manifest(runs_root, manifest)

        if rep < repetitions:
            note, cap_hit = _cooldown_between_reps(
                config, bundle_path.name, summary, registry, clock
            )
            manifest["cooldown"].append(note)
            manifest_path = write_experiment_manifest(runs_root, manifest)
            if cap_hit:
                next_extra_metadata = {"cooldown_cap_hit": True}

    assert manifest_path is not None  # repetitions >= 1 by schema
    return manifest_path, results


def _cooldown_between_reps(
    config: BenchmarkConfig,
    after_member: str,
    summary: SummaryMetrics,
    registry: AdapterRegistry,
    clock: Clock,
) -> tuple[dict[str, Any], bool]:
    """Run the D-014 gate after a completed rep; return ``(note, cap_hit)``.

    Mock telemetry: skipped (no thermal reality). Otherwise the gate uses the
    previous rep's measured ``idle_baseline`` as the reference; an absent
    baseline (a failed rep) skips with a recorded reason rather than guessing.
    """
    note: dict[str, Any] = {"after_member": after_member}
    if config.hardware_target.telemetry_backend == TelemetryBackend.MOCK:
        note.update({"result": "skipped", "reason": "mock telemetry"})
        return note, False
    if summary.idle_baseline is None:
        note.update({"result": "skipped", "reason": "no idle baseline from previous rep"})
        return note, False

    telemetry, failure = registry.resolve_telemetry(config, clock)
    if telemetry is None:
        reason = failure.message if failure is not None else "telemetry adapter unavailable"
        note.update({"result": "skipped", "reason": reason})
        return note, False

    gate = cooldown_gate(telemetry, summary.idle_baseline, config, clock)
    note.update(gate)
    return note, gate["result"] == "cap_hit"


def _config_sha256(config: BenchmarkConfig) -> str:
    """SHA-256 over the sorted-key, 2-space-indented JSON of ``config.to_dict()``.

    Matches the bundle writer's D-001 config hash (``bundle.RunBundleWriter``)
    so an experiment's ``config_sha256`` is the hash of the shared, as-given
    config - including its ``run_id`` - before per-member run_id replacement.
    """
    config_bytes = (
        json.dumps(config.to_dict(), indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return hashlib.sha256(config_bytes).hexdigest()
