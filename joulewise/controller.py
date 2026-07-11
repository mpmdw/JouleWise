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
  memory and flush only after ``stop_sampling``; inside the MARKER-bounded
  measured window (``sampling_started`` stamp to ``sampling_stopped`` stamp)
  the controller does nothing but block on the runtime; alignment capture and
  ``stop_sampling`` wind-down happen after the stop stamp, outside the window
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
from joulewise.aggregate import aggregate_experiment
from joulewise import reduce as reduce_module
from joulewise.bundle import (
    RunBundleWriter,
    generate_run_id,
    sanitize_id_component,
    write_experiment_manifest,
)
from joulewise.clock import Clock, ClockStamp, FakeClock
from joulewise.environment import collect_environment_snapshot, empty_environment_snapshot
from joulewise.interfaces import (
    AdapterFailure,
    AdapterResult,
    BoundedTelemetryAdapter,
    IdleDriftEvidenceProvider,
    PowerSample,
    RunContext,
    RuntimeAdapter,
    RuntimeEvent,
    RuntimeResult,
    SuiteRuntimeAdapter,
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
from joulewise.suite import (
    SuiteManifest,
    canonical_effective_manifest,
    load_suite_manifest,
    order_seed,
    suite_manifest_sha256,
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
PRE_IDLE_SETTLE_S = 2.0

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
_ENVIRONMENT_UNSET = object()


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
    environment_snapshot: dict[str, Any] | None | object = _ENVIRONMENT_UNSET,
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
    return _Execution(
        config,
        writer,
        clock,
        registry,
        reducer,
        extra_metadata,
        environment_snapshot,
    ).execute()


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


def _clock_stamp(clock: Clock) -> ClockStamp:
    """Use the paired API, with an exact synthetic bracket for old test clocks."""

    stamp = getattr(clock, "stamp", None)
    if callable(stamp):
        return stamp()
    epoch_s = clock.now()
    return ClockStamp(epoch_s, epoch_s, epoch_s, 0.0, 0.0)


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
        environment_snapshot: dict[str, Any] | None | object = _ENVIRONMENT_UNSET,
    ) -> None:
        self._config = config
        self._writer = writer
        self._clock = clock
        self._registry = registry
        self._reducer = reducer
        self._extra_metadata = dict(extra_metadata) if extra_metadata else {}
        self._environment_snapshot = environment_snapshot
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
        if environment_snapshot is not _ENVIRONMENT_UNSET:
            self._environment = (
                dict(environment_snapshot) if environment_snapshot is not None else None
            )
        else:
            self._environment = None
        self._device_metadata: dict[str, Any] | None = None
        self._prepare_metadata: dict[str, Any] | None = None
        self._runtime_cleanup_metadata: dict[str, Any] | None = None
        self._telemetry_metadata: dict[str, Any] | None = None
        self._runtime_alignments: list[dict[str, Any]] = []
        self._telemetry_alignments: list[dict[str, Any]] = []
        self._baseline: IdleBaseline | None = None
        self._thermal_pre: ThermalState | None = None
        self._thermal_post: ThermalState | None = None
        self._runtime_result: RuntimeResult | None = None
        self._suite_manifest: SuiteManifest | None = None
        self._suite_effective_manifest: dict[str, Any] | None = None
        self._suite_manifest_sha256: str | None = None
        self._suite_source_file_sha256: str | None = None
        self._suite_order_seed: str | None = None
        self._suite_order_row: int | None = None
        self._samples: list[PowerSample] = []
        self._uncertainty_evidence: dict[str, Any] | None = None
        self._sampling_started_stamp: ClockStamp | None = None
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
        except AdapterFailure as failure:
            summary = self._handle_failure(
                _StageFailure(
                    stage=self._current_stage,
                    reason=failure.failure_reason,
                    message=failure.message,
                )
            )
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
        self._stage_idle_drift_sentinel()
        self._stage_cleanup()
        return self._stage_reduce()

    # ------------------------------------------------------------------
    # Stages

    def _stage_validate(self) -> None:
        """Resolve adapters and validate suite manifests before any sampling.

        When ``workload_profile.suite_manifest_ref`` is set, the manifest path
        is used as given if absolute, otherwise resolved by ``Path(ref)`` from
        the process current working directory. The raw source bytes are hashed
        for audit metadata, while run identity and bundle evidence use the
        canonical effective manifest hash (D-044).
        """
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
        self._validate_suite_manifest_if_present(runtime)
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
        if self._suite_effective_manifest is not None:
            self._writer.write_suite_manifest(self._suite_effective_manifest)
        self._connection_metadata = self._transport.connection_metadata(
            self._config, self._context
        )
        self._device_metadata = self._telemetry.device_metadata(self._config, self._context)
        result = self._runtime.prepare(self._config, self._context)
        self._check(result, "prepare", "runtime prepare failed")
        self._prepare_metadata = dict(result.metadata)
        self._capture_adapter_alignments()
        self._capture_prepare_end_environment()
        self._log(self._runtime_log, "runtime prepare succeeded")
        self._complete_stage("prepare")

    def _stage_idle_baseline(self) -> None:
        self._begin_stage("idle_baseline")
        assert self._telemetry is not None
        self._settle_before_idle()
        idle_start_s = self._clock.now()
        self._stamp_preceding_gap(idle_start_s)
        self._baseline = self._telemetry.measure_idle(self._config, self._context)
        self._capture_adapter_alignments()
        self._capture_adapter_metadata()
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
            self._capture_adapter_alignments()
        self._log(self._runtime_log, f"completed {warmup_runs} warmup run(s)")
        self._complete_stage("warmup", {"warmup_runs": warmup_runs})

    def _stage_measured_run(self) -> None:
        self._begin_stage("measured_run")
        assert self._runtime is not None and self._telemetry is not None
        self._thermal_pre = self._telemetry.thermal_state(self._config, self._context)
        start_result = self._telemetry.start_sampling(self._config, self._context)
        self._telemetry_metadata = dict(start_result.metadata)
        self._check(start_result, "measured_run", "telemetry start_sampling failed")
        self._capture_adapter_alignments()
        self._capture_adapter_metadata()
        self._sampling_active = True
        # D-026: the measured window the reducer integrates is bounded by the
        # sampling_started/sampling_stopped marker events, not the stage
        # boundaries, so sampler spawn latency (sudo probe, process start,
        # first sample) and stop-side parsing stay outside the window. The
        # start marker is stamped only after start_sampling confirms; the stop
        # marker is stamped before stop_sampling is asked to wind down.
        sampling_started_stamp = _clock_stamp(self._clock)
        self._sampling_started_stamp = sampling_started_stamp
        self._events.append(
            RuntimeEvent(
                timestamp_s=sampling_started_stamp.epoch_s,
                event_type="sampling_started",
                phase="measured_run",
                message="telemetry sampling confirmed active",
                metadata={},
            )
        )
        # D-013 quiescent window: between the sampling_started stamp and the
        # sampling_stopped stamp the controller only blocks on the runtime -
        # no file writes, no disk event appends, no logging (buffers flush
        # after the window; alignment capture runs after the stop stamp).
        if self._suite_manifest is not None:
            assert self._suite_order_seed is not None
            runtime_result = self._runtime.run_suite(  # type: ignore[attr-defined]
                self._config,
                self._suite_manifest,
                self._context,
                order_seed=self._suite_order_seed,
                order_row=self._suite_order_row,
            )
        else:
            runtime_result = self._runtime.run_workload(self._config, self._context)
        # The stop marker's timestamp is captured as soon as the runtime
        # returns - before alignment capture and stop_sampling - so adapter
        # clock_alignments() getters (D-013 quiescent window) and the
        # sampler's wind-down (process stop, plist parsing) stay outside the
        # window; the event itself is appended after the runtime events so
        # the stable flush-sort keeps it bracketing them.
        sampling_stopped_stamp = _clock_stamp(self._clock)
        self._capture_adapter_alignments()
        if isinstance(self._telemetry, BoundedTelemetryAdapter):
            stop_result = self._telemetry.stop_sampling_with_evidence(
                self._config,
                self._context,
                sampling_started=sampling_started_stamp,
                sampling_stopped=sampling_stopped_stamp,
            )
            self._samples = stop_result.samples
            self._uncertainty_evidence = dict(stop_result.uncertainty_evidence)
        else:
            self._samples = self._telemetry.stop_sampling(self._config, self._context)
        self._capture_adapter_alignments()
        self._capture_adapter_metadata()
        self._sampling_active = False
        self._runtime_result = runtime_result
        self._thermal_post = self._telemetry.thermal_state(self._config, self._context)
        self._events.extend(runtime_result.events)
        self._events.append(
            RuntimeEvent(
                timestamp_s=sampling_stopped_stamp.epoch_s,
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

    def _stage_idle_drift_sentinel(self) -> None:
        """Collect the short post-run idle sentinel outside the measured window."""

        if not isinstance(self._telemetry, IdleDriftEvidenceProvider):
            return
        self._begin_stage("idle_drift_sentinel")
        assert self._baseline is not None
        try:
            result = self._telemetry.measure_post_run_idle(
                self._config, self._baseline, self._context
            )
        except Exception as exc:  # noqa: BLE001 - unknown drift preserves L0/L1
            result = {
                "idle_drift": {
                    "status": "unknown",
                    "reason": "post_idle_unavailable",
                }
            }
            self._log(
                self._telemetry_log,
                f"post-run idle sentinel unavailable: {type(exc).__name__}: {exc}",
            )
        if self._uncertainty_evidence is None:
            self._uncertainty_evidence = {
                "schema_version": "p2-038.1",
                "telemetry_backend": self._telemetry.name,
            }
        for key in ("idle_drift", "idle_drift_guard"):
            if key in result:
                self._uncertainty_evidence[key] = _jsonable(result[key])
        if "idle_drift_bound_w" in result:
            self._uncertainty_evidence["idle_drift_bound_w"] = result[
                "idle_drift_bound_w"
            ]
        self._capture_adapter_metadata()
        self._complete_stage(
            "idle_drift_sentinel",
            {
                "status": self._uncertainty_evidence.get("idle_drift", {}).get(
                    "status"
                ),
                "duration_requested_s": result.get("post_idle_duration_requested_s"),
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
            self._capture_adapter_alignments()
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
            if result.metadata:
                self._runtime_cleanup_metadata = dict(result.metadata)
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
            elif result.metadata:
                metadata.update(_jsonable(result.metadata))
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
        self._capture_failure_fallback_environment()
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
        sampling_stopped_stamp = _clock_stamp(self._clock)
        self._events.append(
            RuntimeEvent(
                timestamp_s=sampling_stopped_stamp.epoch_s,
                event_type="sampling_stopped",
                phase="measured_run",
                message="telemetry sampling stopping (failure path)",
                metadata={},
            )
        )
        try:
            if (
                isinstance(self._telemetry, BoundedTelemetryAdapter)
                and self._sampling_started_stamp is not None
            ):
                result = self._telemetry.stop_sampling_with_evidence(
                    self._config,
                    self._context,
                    sampling_started=self._sampling_started_stamp,
                    sampling_stopped=sampling_stopped_stamp,
                )
                self._samples = result.samples
                self._uncertainty_evidence = dict(result.uncertainty_evidence)
            else:
                self._samples = self._telemetry.stop_sampling(
                    self._config, self._context
                )
            self._capture_adapter_alignments()
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
            self._capture_adapter_alignments()
        except Exception:  # noqa: BLE001 - best-effort cleanup must not mask the failure
            self._log(
                self._controller_log,
                "best-effort runtime cleanup raised after failure:",
            )
            self._log(self._controller_log, traceback.format_exc())
        else:
            if result.metadata:
                self._runtime_cleanup_metadata = dict(result.metadata)
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
        if self._environment is not None:
            extra["environment"] = _jsonable(self._environment)
        adapters: dict[str, Any] = {}
        if self._runtime is not None:
            adapters["runtime"] = {
                "name": self._runtime.name,
                "prepare_metadata": self._prepare_metadata or {},
            }
            if self._runtime_result is not None and self._runtime_result.metadata:
                _merge_adapter_metadata(
                    adapters["runtime"], self._runtime_result.metadata
                )
            if self._runtime_cleanup_metadata is not None:
                adapters["runtime"]["cleanup_metadata"] = _jsonable(
                    self._runtime_cleanup_metadata
                )
            if self._runtime_alignments:
                adapters["runtime"]["clock_alignments"] = _jsonable(self._runtime_alignments)
        if self._telemetry is not None:
            adapters["telemetry"] = {"name": self._telemetry.name}
            if self._telemetry_metadata:
                _merge_adapter_metadata(adapters["telemetry"], self._telemetry_metadata)
            if self._telemetry_alignments:
                adapters["telemetry"]["clock_alignments"] = _jsonable(self._telemetry_alignments)
        extra["adapters"] = adapters
        if self._baseline is not None:
            extra["idle_baseline"] = _jsonable(asdict(self._baseline))
        if self._thermal_pre is not None:
            extra["thermal_pre"] = _jsonable(asdict(self._thermal_pre))
        if self._thermal_post is not None:
            extra["thermal_post"] = _jsonable(asdict(self._thermal_post))
        if self._uncertainty_evidence is not None:
            evidence = dict(self._uncertainty_evidence)
            idle_bound_w = evidence.pop("idle_drift_bound_w", None)
            extra["uncertainty_evidence"] = _jsonable(evidence)
            clock_anchor = evidence.get("clock_anchor")
            if isinstance(clock_anchor, dict) and clock_anchor.get("status") == "bounded":
                extra["clock_anchor_bound_s"] = clock_anchor.get(
                    "effective_clock_anchor_bound_s"
                )
            sample_phase = evidence.get("sample_phase")
            if isinstance(sample_phase, dict) and sample_phase.get("status") == "bounded":
                extra["marker_to_first_sample_phase_bound_s"] = sample_phase.get(
                    "marker_to_first_sample_phase_bound_s"
                )
                extra["marker_to_last_sample_phase_bound_s"] = sample_phase.get(
                    "marker_to_last_sample_phase_bound_s"
                )
            if idle_bound_w is not None:
                extra["idle_drift_bound_w"] = idle_bound_w
        if self._runtime_result is not None:
            extra["workload_observed"] = {
                "token_count": self._runtime_result.token_count,
                "output_token_count": self._runtime_result.output_token_count,
            }
            if self._runtime_result.workload_provenance is not None:
                extra["workload_provenance"] = _jsonable(
                    self._runtime_result.workload_provenance
                )
        if self._suite_manifest is not None:
            extra["suite"] = {
                "suite_id": self._suite_manifest.suite_id,
                "suite_profile": self._suite_manifest.suite_profile,
                "suite_revision": self._suite_manifest.suite_revision,
                "manifest_sha256": self._suite_manifest_sha256,
                "source_file_sha256": self._suite_source_file_sha256,
                "item_count": len(self._suite_manifest.items),
                "order_policy": self._suite_manifest.execution_policy.order_policy,
                "order_seed": self._suite_order_seed,
                "order_row": self._suite_order_row,
            }
        # Caller-supplied metadata (Slice 2F: the experiment runner records a
        # cooldown cap-hit against the following rep here). Lands under the
        # dedicated "extra" key so it never collides with controller fields and
        # the reducer reads it from one known place.
        if self._extra_metadata:
            extra["extra"] = _jsonable(self._extra_metadata)
        self._writer.write_metadata(extra)
        self._metadata_written = True

    def _capture_adapter_alignments(self) -> None:
        self._runtime_alignments = _adapter_clock_alignments(self._runtime)
        self._telemetry_alignments = _adapter_clock_alignments(self._telemetry)

    def _capture_adapter_metadata(self) -> None:
        telemetry_metadata = _adapter_metadata(self._telemetry)
        if telemetry_metadata:
            self._telemetry_metadata = telemetry_metadata

    def _capture_prepare_end_environment(self) -> None:
        if not self._should_capture_run_environment():
            return
        self._environment = _capture_environment(
            self._clock,
            capture_scope="run",
            captured_for_rep=None,
            settle_s=PRE_IDLE_SETTLE_S,
        )

    def _should_capture_run_environment(self) -> bool:
        if self._environment_snapshot is _ENVIRONMENT_UNSET:
            return True
        if not isinstance(self._environment_snapshot, dict):
            return False
        return self._environment_snapshot.get("capture_scope") == "experiment"

    def _capture_failure_fallback_environment(self) -> None:
        if self._environment is not None:
            return
        if self._environment_snapshot is not _ENVIRONMENT_UNSET:
            return
        self._environment = _capture_environment(
            self._clock,
            capture_scope="failure_fallback",
            captured_for_rep=None,
            settle_s=None,
        )

    def _settle_before_idle(self) -> None:
        if not isinstance(self._environment, dict):
            return
        settle_s = self._environment.get("settle_s")
        if isinstance(settle_s, int | float) and settle_s > 0:
            self._clock.sleep(float(settle_s))

    def _stamp_preceding_gap(self, idle_start_s: float) -> None:
        if "preceding_member_end_s" not in self._extra_metadata:
            return
        preceding_end_s = self._extra_metadata.get("preceding_member_end_s")
        self._extra_metadata["idle_start_s"] = idle_start_s
        if isinstance(preceding_end_s, int | float):
            gap_s = idle_start_s - float(preceding_end_s)
            self._extra_metadata["preceding_gap_s"] = gap_s
            if gap_s < 0.0:
                self._extra_metadata["clock_step_suspect"] = True
        else:
            self._extra_metadata["preceding_gap_s"] = None

    # ------------------------------------------------------------------
    # Summaries

    def _minimal_quality(self) -> MeasurementQuality:
        return MeasurementQuality(
            requested_sampling_hz=self._config.sampling.power_hz,
            idle_power_w_stddev=(
                self._baseline.power_w_stddev if self._baseline is not None else None
            ),
            telemetry_source=self._telemetry.name if self._telemetry is not None else None,
            idle_window_suspect=(
                self._baseline.idle_window_suspect if self._baseline is not None else None
            ),
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

    def _validate_suite_manifest_if_present(self, runtime: RuntimeAdapter) -> None:
        profile = self._config.workload_profile
        if profile.suite_manifest_ref is None:
            return
        if not isinstance(runtime, SuiteRuntimeAdapter) or not callable(
            getattr(runtime, "run_suite", None)
        ):
            raise _StageFailure(
                "validate",
                FailureReason.UNSUPPORTED_WORKLOAD,
                "runtime adapter does not support suite workloads",
            )
        ref_path = Path(profile.suite_manifest_ref)
        try:
            source_bytes = ref_path.read_bytes()
            manifest = load_suite_manifest(ref_path)
            effective = canonical_effective_manifest(json.loads(source_bytes))
        except Exception as exc:  # noqa: BLE001 - fail closed into a complete bundle
            raise _StageFailure(
                "validate",
                FailureReason.UNKNOWN_ERROR,
                f"suite manifest cannot be loaded from {profile.suite_manifest_ref!r}: "
                f"{type(exc).__name__}: {exc}",
            ) from exc
        actual_hash = suite_manifest_sha256(effective)
        if actual_hash != profile.suite_manifest_sha256:
            raise _StageFailure(
                "validate",
                FailureReason.UNKNOWN_ERROR,
                "suite manifest hash mismatch: "
                f"config has {profile.suite_manifest_sha256!r}, "
                f"{profile.suite_manifest_ref!r} hashes to {actual_hash!r}",
            )
        rep_index = _suite_rep_index_from_run_id(self._config.run_id)
        self._suite_manifest = manifest
        self._suite_effective_manifest = effective
        self._suite_manifest_sha256 = actual_hash
        self._suite_source_file_sha256 = hashlib.sha256(source_bytes).hexdigest()
        self._suite_order_seed = order_seed(
            manifest.suite_seed,
            manifest.execution_policy.order_policy,
            rep_index,
        )
        self._suite_order_row = rep_index

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
    run_id: str | None = None,
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

    ``run_id`` (NV-2/ARC-7): the gate calls ``measure_idle`` out-of-run with
    no ``RunContext``, so adapters that need a run id for node-side isolation
    fall back to ``config.run_id`` - which is ``None`` for generated-id
    experiments. When given, ``run_id`` is stamped onto the sub-window config
    so those adapters see a cooldown-scoped id instead of failing.
    """
    reference = reference_baseline.power_w_mean
    sub_config = replace(
        config,
        run_id=run_id if run_id is not None else config.run_id,
        sampling=replace(config.sampling, idle_seconds=COOLDOWN_SUBWINDOW_S),
    )
    start_s = clock.now()
    # Each reading carries (timestamp_s, mean) so the rolling mean spans only
    # the most recent COOLDOWN_ROLLING_WINDOW_S of readings.
    readings: list[tuple[float, float]] = []
    trace: list[dict[str, Any]] = []
    while True:
        baseline = telemetry.measure_idle(sub_config)
        now_s = clock.now()
        readings.append((now_s, baseline.power_w_mean))
        cutoff = now_s - COOLDOWN_ROLLING_WINDOW_S
        readings = [reading for reading in readings if reading[0] >= cutoff]
        rolling_mean = sum(value for _, value in readings) / len(readings)
        waited_s = now_s - start_s
        trace.append(
            {
                "timestamp_s": now_s,
                "waited_s": waited_s,
                "rolling_mean_power_w": rolling_mean,
                "baseline": _jsonable(asdict(baseline)),
            }
        )
        if _within_tolerance(rolling_mean, reference, COOLDOWN_TOLERANCE):
            return {
                "result": "recovered",
                "waited_s": waited_s,
                "reference_power_w": reference,
                "tolerance_fraction": COOLDOWN_TOLERANCE,
                "decision_rolling_mean_power_w": rolling_mean,
                "_trace": trace,
            }
        if waited_s >= COOLDOWN_CAP_S:
            return {
                "result": "cap_hit",
                "waited_s": waited_s,
                "reference_power_w": reference,
                "tolerance_fraction": COOLDOWN_TOLERANCE,
                "decision_rolling_mean_power_w": rolling_mean,
                "_trace": trace,
            }


def _within_tolerance(value: float, reference: float, tolerance: float) -> bool:
    """True when ``value`` is within ``tolerance`` (fraction) of ``reference``.

    When the reference is exactly zero the tolerance band collapses to an exact
    match (a degenerate baseline that cannot meaningfully define a 10% band).
    """
    return abs(value - reference) <= tolerance * abs(reference)


def _adapter_clock_alignments(adapter: Any) -> list[dict[str, Any]]:
    if adapter is None:
        return []
    getter = getattr(adapter, "clock_alignments", None)
    if not callable(getter):
        return []
    try:
        alignments = getter()
    except Exception:  # noqa: BLE001 - metadata capture must not disturb lifecycle.
        return []
    if not isinstance(alignments, list):
        return []
    return [dict(item) for item in alignments if isinstance(item, dict)]


def _adapter_metadata(adapter: Any) -> dict[str, Any]:
    if adapter is None:
        return {}
    getter = getattr(adapter, "metadata", None)
    if not callable(getter):
        return {}
    try:
        metadata = getter()
    except Exception:  # noqa: BLE001 - metadata capture must not disturb lifecycle.
        return {}
    if not isinstance(metadata, dict):
        return {}
    return dict(metadata)


def _merge_adapter_metadata(target: dict[str, Any], metadata: dict[str, Any]) -> None:
    for key, value in _jsonable(metadata).items():
        if key in target:
            collision_metadata = target.get("metadata")
            if not isinstance(collision_metadata, dict):
                collision_metadata = {}
                if "metadata" in target:
                    collision_metadata["metadata"] = target["metadata"]
                target["metadata"] = collision_metadata
            collision_metadata[key] = value
        else:
            target[key] = value


# ---------------------------------------------------------------------------
# Environment snapshot policy (INT-002)


def _environment_for_run(
    clock: Clock,
    *,
    provided: dict[str, Any] | None | object = _ENVIRONMENT_UNSET,
) -> dict[str, Any] | None:
    if provided is not _ENVIRONMENT_UNSET:
        return dict(provided) if provided is not None else None
    return _capture_environment(
        clock,
        capture_scope="run",
        captured_for_rep=None,
        settle_s=PRE_IDLE_SETTLE_S,
    )


def _environment_for_experiment(clock: Clock) -> dict[str, Any]:
    return _capture_environment(
        clock,
        capture_scope="experiment",
        captured_for_rep=1,
        settle_s=None,
    )


def _capture_environment(
    clock: Clock,
    *,
    capture_scope: str,
    captured_for_rep: int | None,
    settle_s: float | None,
) -> dict[str, Any]:
    started_at_s = clock.now()
    if isinstance(clock, FakeClock):
        snapshot = empty_environment_snapshot()
        snapshot.update(
            {
                "capture_skipped": True,
                "skip_reason": "fake_clock",
                "capture_scope": capture_scope,
                "captured_for_rep": captured_for_rep,
                "captured_at_s": None,
                "env_capture_duration_s": 0.0,
                "settle_s": settle_s,
            }
        )
        return snapshot
    snapshot = collect_environment_snapshot()
    captured_at_s = clock.now()
    snapshot.update(
        {
            "capture_skipped": False,
            "capture_scope": capture_scope,
            "captured_for_rep": captured_for_rep,
            "captured_at_s": captured_at_s,
            "env_capture_duration_s": captured_at_s - started_at_s,
            "settle_s": settle_s,
        }
    )
    return snapshot


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
    environment_snapshot = _environment_for_experiment(clock)

    manifest: dict[str, Any] = {
        "experiment_id": experiment_id,
        "config_sha256": config_sha256,
        "created_at_s": created_at_s,
        "members": [],
        "member_gaps": [],
        "condition_order": [],
        "cooldown": [],
    }

    results: list[tuple[Path, SummaryMetrics]] = []
    manifest_path: Path | None = None
    # Pending cap-hit recorded against the NEXT rep's run_benchmark.
    next_extra_metadata: dict[str, Any] | None = None
    previous_member_end_s: float | None = None

    for rep in range(1, repetitions + 1):
        member_config = replace(config, run_id=f"{experiment_id}__r{rep}")
        member_extra_metadata = dict(next_extra_metadata or {})
        member_extra_metadata["preceding_member_end_s"] = previous_member_end_s
        bundle_path, summary = run_benchmark(
            member_config,
            runs_root,
            clock,
            registry=registry,
            extra_metadata=member_extra_metadata,
            environment_snapshot=environment_snapshot,
        )
        previous_member_end_s = clock.now()
        next_extra_metadata = None
        results.append((bundle_path, summary))
        manifest["members"].append(bundle_path.name)
        manifest["member_gaps"].append(_member_gap_note(bundle_path))
        manifest["condition_order"].append(condition_name)
        manifest["aggregate"] = aggregate_experiment(runs_root, manifest)
        # Incremental write: a kill before the next rep leaves a valid manifest
        # listing exactly the members that completed (D-005 acceptance).
        manifest_path = write_experiment_manifest(runs_root, manifest)

        if rep < repetitions:
            note, cap_hit = _cooldown_between_reps(
                config, runs_root, experiment_id, bundle_path.name, summary, registry, clock
            )
            manifest["cooldown"].append(note)
            manifest_path = write_experiment_manifest(runs_root, manifest)
            if cap_hit:
                next_extra_metadata = {"cooldown_cap_hit": True}

    assert manifest_path is not None  # repetitions >= 1 by schema
    return manifest_path, results


def _cooldown_between_reps(
    config: BenchmarkConfig,
    runs_root: Path,
    experiment_id: str,
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

    # NV-2 (ARC-7): generated-id experiments have config.run_id == None, and
    # the gate's out-of-run measure_idle passes no RunContext, so adapters
    # that require a run id for node-side task isolation (nvidia_smi) would
    # fail and silently downgrade every cooldown to "skipped". Thread a
    # cooldown-scoped run id, unique per gate invocation, and record it so
    # the manifest is auditable against node-side artifacts.
    cooldown_run_id = f"{experiment_id}-cooldown-{after_member}"
    note["cooldown_run_id"] = cooldown_run_id
    try:
        gate = cooldown_gate(
            telemetry, summary.idle_baseline, config, clock, run_id=cooldown_run_id
        )
    except AdapterFailure as failure:
        note.update(
            {
                "result": "skipped",
                "reason": failure.message,
                "failure_reason": failure.failure_reason.value,
            }
        )
        return note, False
    trace = gate.pop("_trace", [])
    note.update(gate)
    if trace:
        artifact, error = _write_cooldown_trace(
            runs_root, experiment_id, after_member, trace
        )
        if artifact is not None:
            note["raw_artifact"] = artifact
        if error is not None:
            note["raw_artifact_error"] = error
    return note, gate["result"] == "cap_hit"


def _member_gap_note(bundle_path: Path) -> dict[str, Any]:
    note: dict[str, Any] = {"member": bundle_path.name, "preceding_gap_s": None}
    try:
        metadata = json.loads((bundle_path / "metadata.json").read_text())
    except Exception:  # noqa: BLE001 - manifest update must stay fail-soft.
        note["error"] = "metadata_unavailable"
        return note
    extra = metadata.get("extra")
    if isinstance(extra, dict):
        note["preceding_gap_s"] = extra.get("preceding_gap_s")
    return note


def _write_cooldown_trace(
    runs_root: Path,
    experiment_id: str,
    after_member: str,
    trace: list[dict[str, Any]],
) -> tuple[str | None, str | None]:
    try:
        raw_dir = Path(runs_root) / "experiments" / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        filename = (
            f"{sanitize_id_component(experiment_id)}__cooldown_after_"
            f"{sanitize_id_component(after_member)}.jsonl"
        )
        path = raw_dir / filename
        text = "".join(json.dumps(record, sort_keys=True) + "\n" for record in trace)
        with path.open("x") as handle:
            handle.write(text)
        return f"raw/{filename}", None
    except Exception as exc:  # noqa: BLE001 - cooldown evidence is fail-soft.
        return None, f"{type(exc).__name__}: {exc}"


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


def _suite_rep_index_from_run_id(run_id: str | None) -> int:
    """Suite order-seed repetition index from the existing D-010 ``__rN`` suffix.

    Single runs and custom run IDs without that suffix use index 0. Experiment
    members are created by ``run_experiment`` as ``<experiment_id>__rN`` and use
    the one-based ``N`` already present in the run id. The ``__rN`` segment is
    the D-022-reserved experiment-member suffix, so any run id carrying it gets
    that repetition index deliberately; malformed or zero values fall back to 0.
    """
    if run_id is None:
        return 0
    marker = "__r"
    if marker not in run_id:
        return 0
    suffix = run_id.rsplit(marker, 1)[1]
    if not suffix.isdigit():
        return 0
    return int(suffix)
