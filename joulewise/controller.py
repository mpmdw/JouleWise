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
import os
import traceback
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
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
from joulewise.environment import (
    collect_environment_guard_observation,
    collect_environment_snapshot,
    empty_environment_snapshot,
    evaluate_environment_policy,
)
from joulewise.interfaces import (
    AttemptIdentity,
    AdapterFailure,
    AdapterResult,
    AxiRuntimeResult,
    BoundedTelemetryAdapter,
    EvidenceCustodyProvider,
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
from joulewise.analysis_engine.registry import render_dispatch_receipt
from joulewise.axi_decode_config import (
    AXI_CONFIG_EXTENSION,
    EVENT_SEMANTICS_VERSION,
    RequestRoster,
    canonical_json_bytes as axi_canonical_json_bytes,
    sha256_bytes as axi_sha256_bytes,
)
from joulewise.schemas import (
    AdmissionFailureAction,
    BenchmarkConfig,
    CampaignPolicy,
    CooldownPolicy,
    FailureReason,
    IdleBaseline,
    MeasurementQuality,
    RunStatus,
    SamplingConfig,
    SummaryMetrics,
    SummaryMetricsV060,
    TelemetryBackend,
)
from joulewise.suite import (
    SuiteManifest,
    canonical_effective_manifest,
    migrate_suite_manifest,
    order_seed,
    suite_manifest_sha256,
)

__all__ = [
    "STATUS_BY_REASON",
    "AdapterRegistry",
    "Reducer",
    "cooldown_gate",
    "finalize_dispatch_receipt",
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
CAMPAIGN_POLICY_PATH_ENV = "JOULEWISE_CAMPAIGN_POLICY_PATH"
CAMPAIGN_POLICY_SHA256_ENV = "JOULEWISE_CAMPAIGN_POLICY_SHA256"
CAMPAIGN_PREFLIGHT_JSON_ENV = "JOULEWISE_CAMPAIGN_PREFLIGHT_JSON"

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
    FailureReason.CLEANUP_FAILED: RunStatus.FAILED,
    FailureReason.UNKNOWN_ERROR: RunStatus.FAILED,
}

#: Post-hoc summary derivation over a bundle directory (Slice 2D).
Reducer = Callable[[Path], SummaryMetrics | SummaryMetricsV060]
_ENVIRONMENT_UNSET = object()


def finalize_dispatch_receipt(
    path: Path,
    identity: AttemptIdentity,
    *,
    dispatch_started: bool,
    transport_status: str,
    process_exit_code: int | None,
    admitted_request_count: int,
    finalized_run_id: str | None,
) -> Path:
    """Write one immutable, identity-bound receipt after dispatch handling."""

    payload = {
        "schema_version": "joulewise.dispatch_receipt.v1",
        "manifest_id": identity.manifest_id,
        "entry_id": identity.entry_id,
        "pair_id": identity.pair_id,
        "arm": identity.arm,
        "attempt_ordinal": identity.attempt_ordinal,
        "dispatch_started": dispatch_started,
        "transport_status": transport_status,
        "process_exit_code": process_exit_code,
        "admitted_request_count": admitted_request_count,
        "finalized_run_id": finalized_run_id,
    }
    rendered = render_dispatch_receipt(payload)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as handle:
        handle.write(rendered)
    return target


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
    campaign_policy: CampaignPolicy | None = None,
    campaign_policy_binding: dict[str, Any] | None = None,
    campaign_environment_preflight: dict[str, Any] | None = None,
) -> tuple[Path, SummaryMetrics | SummaryMetricsV060]:
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
    if campaign_policy is None:
        (
            campaign_policy,
            campaign_policy_binding,
            campaign_environment_preflight,
        ) = _campaign_policy_from_environment()
    config, suite_preparation, suite_preparation_failure = (
        _prepare_suite_manifest_for_new_bundle(config)
    )
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
        suite_preparation,
        suite_preparation_failure,
        campaign_policy,
        campaign_policy_binding,
        campaign_environment_preflight,
    ).execute()


def _campaign_policy_from_environment() -> tuple[
    CampaignPolicy | None,
    dict[str, Any] | None,
    dict[str, Any] | None,
]:
    """Load and authenticate the optional campaign-only process binding."""

    path_text = os.environ.get(CAMPAIGN_POLICY_PATH_ENV)
    expected_sha = os.environ.get(CAMPAIGN_POLICY_SHA256_ENV)
    preflight_text = os.environ.get(CAMPAIGN_PREFLIGHT_JSON_ENV)
    if path_text is None and expected_sha is None and preflight_text is None:
        return None, None, None
    if not path_text or not expected_sha:
        raise ValueError(
            "campaign policy environment binding requires both path and sha256"
        )
    raw = Path(path_text).read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    normalized_expected = expected_sha.removeprefix("sha256:")
    if normalized_expected != actual_sha:
        raise ValueError(
            "campaign policy hash mismatch: "
            f"expected {normalized_expected}, observed {actual_sha}"
        )
    payload = json.loads(raw)
    policy = CampaignPolicy.from_mapping(payload)
    preflight: dict[str, Any] | None = None
    if preflight_text is not None:
        parsed = json.loads(preflight_text)
        if not isinstance(parsed, dict):
            raise ValueError("campaign environment preflight must be a JSON object")
        preflight = parsed
        if preflight.get("policy_sha256") != actual_sha:
            raise ValueError("campaign preflight is not bound to the selected policy hash")
    binding = {
        "schema_version": policy.schema_version,
        "policy_id": policy.policy_id,
        "policy_version": policy.policy_version,
        "profile": policy.profile.value,
        "sha256": actual_sha,
        "source": path_text,
    }
    return policy, binding, preflight


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


@dataclass(frozen=True)
class _PreparedSuiteManifest:
    manifest: SuiteManifest
    effective_manifest: dict[str, Any]
    manifest_sha256: str
    source_file_sha256: str


def _prepare_suite_manifest_for_new_bundle(
    config: BenchmarkConfig,
) -> tuple[
    BenchmarkConfig,
    _PreparedSuiteManifest | None,
    _StageFailure | None,
]:
    """Authenticate a source manifest and normalize new-bundle identity to v2.

    Legacy v1 source pins remain accepted as source authentication and remain
    unchanged in ``config.json`` so campaign registration identity is stable.
    The bundle metadata, marker events, and embedded ``suite_manifest.json``
    all use the canonical v2 digest; the reader verifies the deterministic
    source-pin-to-artifact migration.
    """

    profile = config.workload_profile
    if profile.suite_manifest_ref is None:
        return config, None, None
    ref_path = Path(profile.suite_manifest_ref)
    try:
        source_bytes = ref_path.read_bytes()
        raw_manifest = json.loads(source_bytes)
        source_effective = canonical_effective_manifest(raw_manifest)
        source_hash = suite_manifest_sha256(source_effective)
        effective = migrate_suite_manifest(raw_manifest)
        manifest = SuiteManifest.from_mapping(effective)
        manifest_hash = suite_manifest_sha256(effective)
    except Exception as exc:  # noqa: BLE001 - becomes a complete failure bundle
        return config, None, _StageFailure(
            "validate",
            FailureReason.UNKNOWN_ERROR,
            f"suite manifest cannot be loaded from {profile.suite_manifest_ref!r}: "
            f"{type(exc).__name__}: {exc}",
        )
    if profile.suite_manifest_sha256 not in {source_hash, manifest_hash}:
        return config, None, _StageFailure(
            "validate",
            FailureReason.UNKNOWN_ERROR,
            "suite manifest hash mismatch: "
            f"config has {profile.suite_manifest_sha256!r}, "
            f"{profile.suite_manifest_ref!r} hashes to {source_hash!r}",
        )
    return (
        config,
        _PreparedSuiteManifest(
            manifest=manifest,
            effective_manifest=effective,
            manifest_sha256=manifest_hash,
            source_file_sha256=hashlib.sha256(source_bytes).hexdigest(),
        ),
        None,
    )


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
        suite_preparation: _PreparedSuiteManifest | None = None,
        suite_preparation_failure: _StageFailure | None = None,
        campaign_policy: CampaignPolicy | None = None,
        campaign_policy_binding: dict[str, Any] | None = None,
        campaign_environment_preflight: dict[str, Any] | None = None,
    ) -> None:
        self._config = config
        self._writer = writer
        self._clock = clock
        self._registry = registry
        self._reducer = reducer
        self._extra_metadata = dict(extra_metadata) if extra_metadata else {}
        self._environment_snapshot = environment_snapshot
        self._suite_preparation = suite_preparation
        self._suite_preparation_failure = suite_preparation_failure
        self._campaign_policy = campaign_policy
        self._campaign_policy_binding = (
            dict(campaign_policy_binding) if campaign_policy_binding else None
        )
        self._campaign_environment_preflight = (
            dict(campaign_environment_preflight)
            if campaign_environment_preflight
            else None
        )
        self._environment_admission: dict[str, Any] | None = None
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
        self._sampling_start_in_progress = False
        self._sampling_stop_claimed = False
        # Idempotence flags so the failure path writes only what is missing.
        self._outputs_written = False
        self._trace_written = False
        self._metadata_written = False
        self._events_flushed_count = 0

    # ------------------------------------------------------------------
    # Top level

    def execute(self) -> tuple[Path, SummaryMetrics]:
        try:
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
            except Exception as exc:  # noqa: BLE001 - D-011 finalizes controller bugs
                summary = self._handle_failure(
                    _StageFailure(
                        stage=self._current_stage,
                        reason=FailureReason.UNKNOWN_ERROR,
                        message=f"unexpected {type(exc).__name__}: {exc}",
                        traceback_text=traceback.format_exc(),
                    )
                )
            self._finish()
        except (KeyboardInterrupt, SystemExit) as interrupt:
            self._finalize_interrupted_run(interrupt)
            raise
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
        admission = (
            self._campaign_policy.idle_admission
            if self._campaign_policy is not None
            else None
        )
        attempts: list[dict[str, Any]] = []
        if admission is not None and admission.enabled:
            per_run_evaluation = evaluate_environment_policy(
                self._environment if isinstance(self._environment, dict) else {},
                self._campaign_policy.environment_guard,
            )
            preflight_evaluation = (
                self._campaign_environment_preflight.get("evaluation")
                if isinstance(self._campaign_environment_preflight, dict)
                else None
            )
            override = (
                self._campaign_environment_preflight.get("override")
                if isinstance(self._campaign_environment_preflight, dict)
                else None
            )
            critical_environment_passed = bool(
                per_run_evaluation.get("eligible") is True
                and isinstance(preflight_evaluation, dict)
                and preflight_evaluation.get("eligible") is True
                and override is None
            )
            self._environment_admission = {
                "schema_version": "joulewise.environment_admission.v1",
                "policy_version": self._campaign_policy.policy_version,
                "on_fail": admission.on_fail.value,
                "attempts": attempts,
                "per_run_environment_evaluation": per_run_evaluation,
                "critical_environment_passed": critical_environment_passed,
                "reference_provenance_present": bool(
                    self._campaign_policy_binding
                    and per_run_evaluation.get("snapshot_sha256")
                    and isinstance(preflight_evaluation, dict)
                    and preflight_evaluation.get("snapshot_sha256")
                ),
                "decision": None,
                "claim_reason": None,
            }
            observation = self._admission_guard_observation("before_attempt_1")
            environment_reason = self._admission_environment_failure(observation)
            if environment_reason is not None:
                self._environment_admission.update(
                    {"decision": "abort", "failure": environment_reason}
                )
                raise _StageFailure(
                    "idle_baseline", FailureReason.UNKNOWN_ERROR, environment_reason
                )
            if per_run_evaluation.get("eligible") is not True and override is None:
                reason = "critical per-run environment policy did not pass"
                self._environment_admission.update(
                    {"decision": "abort", "failure": reason}
                )
                raise _StageFailure(
                    "idle_baseline", FailureReason.UNKNOWN_ERROR, reason
                )

        self._baseline = self._measure_idle_admission_attempt(1, attempts)
        if admission is not None and admission.enabled:
            self._enforce_post_capture_admission_guard(1)
            if self._baseline.idle_window_suspect is not False:
                observation = self._admission_guard_observation("before_attempt_2")
                environment_reason = self._admission_environment_failure(observation)
                if environment_reason is not None:
                    assert self._environment_admission is not None
                    self._environment_admission.update(
                        {"decision": "abort", "failure": environment_reason}
                    )
                    raise _StageFailure(
                        "idle_baseline",
                        FailureReason.UNKNOWN_ERROR,
                        environment_reason,
                    )
                self._baseline = self._measure_idle_admission_attempt(2, attempts)
                self._enforce_post_capture_admission_guard(2)
            assert self._environment_admission is not None
            if self._baseline.idle_window_suspect is False:
                self._environment_admission["decision"] = "admitted"
            elif admission.on_fail == AdmissionFailureAction.ABORT:
                reason = "idle environment admission failed after one retry"
                self._environment_admission.update(
                    {
                        "decision": "abort",
                        "failure": reason,
                        "claim_reason": "environment_admission_failed",
                    }
                )
                raise _StageFailure(
                    "idle_baseline", FailureReason.UNKNOWN_ERROR, reason
                )
            else:
                self._environment_admission.update(
                    {
                        "decision": "flagged",
                        "claim_reason": "environment_admission_failed",
                    }
                )
            if self._extra_metadata.get("environment_admission_failed") is True:
                self._environment_admission.update(
                    {
                        "decision": "flagged",
                        "failure": (
                            "cooldown reference admission failed before this repetition"
                        ),
                        "claim_reason": "environment_admission_failed",
                    }
                )
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
                "admission_attempts": len(attempts) if attempts else None,
                "admission_decision": (
                    self._environment_admission.get("decision")
                    if self._environment_admission is not None
                    else None
                ),
            },
        )

    def _measure_idle_admission_attempt(
        self, attempt: int, attempts: list[dict[str, Any]]
    ) -> IdleBaseline:
        assert self._telemetry is not None
        baseline = self._telemetry.measure_idle(self._config, self._context)
        self._capture_adapter_alignments()
        self._capture_adapter_metadata()
        if self._campaign_policy is not None:
            attempts.append(
                {
                    "attempt": attempt,
                    "baseline": _jsonable(asdict(baseline)),
                    "admitted": baseline.idle_window_suspect is False,
                }
            )
        return baseline

    def _admission_guard_observation(self, phase: str) -> dict[str, Any]:
        if isinstance(self._clock, FakeClock):
            source = self._environment if isinstance(self._environment, dict) else {}
            observation = {
                "display_power_state": source.get("display_power_state"),
                "screensaver_engaged": source.get("screensaver_engaged"),
                "screensaver_module": source.get("screensaver_module"),
                "screensaver_delay_s": source.get("screensaver_delay_s"),
                "hid_idle_s": source.get("hid_idle_s"),
                "errors": {},
                "capture_skipped": True,
                "skip_reason": "fake_clock",
            }
        else:
            observation = collect_environment_guard_observation()
            observation["capture_skipped"] = False
        observation["phase"] = phase
        if self._environment_admission is not None:
            self._environment_admission.setdefault("guard_observations", []).append(
                observation
            )
        return observation

    def _enforce_post_capture_admission_guard(self, attempt: int) -> None:
        observation = self._admission_guard_observation(f"after_attempt_{attempt}")
        environment_reason = self._admission_environment_failure(observation)
        if environment_reason is None:
            return
        assert self._environment_admission is not None
        self._environment_admission.update(
            {"decision": "abort", "failure": environment_reason}
        )
        raise _StageFailure(
            "idle_baseline", FailureReason.UNKNOWN_ERROR, environment_reason
        )

    @staticmethod
    def _admission_environment_failure(
        observation: dict[str, Any],
    ) -> str | None:
        display_state = observation.get("display_power_state")
        screensaver = observation.get("screensaver_engaged")
        if display_state == "any_awake":
            return "display became or remained awake during idle admission"
        if screensaver is True:
            return "screensaver became or remained engaged during idle admission"
        if display_state not in {"all_asleep"}:
            return "display power state is unknown during idle admission"
        if screensaver is not False:
            return "screensaver engagement state is unknown during idle admission"
        return None

    def _stage_warmup(self) -> None:
        self._begin_stage("warmup")
        assert self._runtime is not None
        warmup_runs = self._config.workload_profile.warmup_runs
        for index in range(warmup_runs):
            result = self._runtime.warmup(self._config, self._context)
            self._check(result, "warmup", f"runtime warmup run {index} failed")
            self._capture_adapter_alignments()
        self._log(self._runtime_log, f"completed {warmup_runs} warmup run(s)")
        warmup_seconds = self._config.sampling.warmup_seconds
        if warmup_seconds > 0.0:
            self._log(
                self._runtime_log,
                f"post-warmup settling for {warmup_seconds} s before sampling",
            )
            self._clock.sleep(warmup_seconds)
        self._complete_stage(
            "warmup",
            {"warmup_runs": warmup_runs, "warmup_seconds": warmup_seconds},
        )

    def _stage_measured_run(self) -> None:
        self._begin_stage("measured_run")
        assert self._runtime is not None and self._telemetry is not None
        self._thermal_pre = self._telemetry.thermal_state(self._config, self._context)
        self._sampling_start_in_progress = True
        try:
            start_result = self._telemetry.start_sampling(self._config, self._context)
        except BaseException:
            # Finalization must treat the sampler as potentially live if start
            # was interrupted after it created native capture state.
            raise
        else:
            # Keep liveness continuous across the successful-start transition:
            # an interrupt between these assignments still leaves at least one
            # flag set, so finalization stops the sampler before custody salvage.
            self._sampling_active = True
            self._sampling_start_in_progress = False
        self._telemetry_metadata = dict(start_result.metadata)
        self._check(start_result, "measured_run", "telemetry start_sampling failed")
        self._capture_adapter_alignments()
        self._capture_adapter_metadata()
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
        self._stop_sampling_once(sampling_stopped_stamp)
        self._capture_adapter_alignments()
        self._capture_adapter_metadata()
        self._sampling_active = False
        self._runtime_result = runtime_result
        self._thermal_post = self._telemetry.thermal_state(self._config, self._context)
        if self._is_axi_run():
            if runtime_result.axi_result is None:
                raise _StageFailure(
                    "measured_run",
                    FailureReason.UNKNOWN_ERROR,
                    "AXI config requires request-scoped runtime result evidence",
                )
            self._events.extend(self._axi_request_events(runtime_result.axi_result))
        else:
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
        if self._is_axi_run() and runtime_result.axi_result is not None:
            unsuccessful = [
                request
                for request in runtime_result.axi_result.requests
                if request.admitted_at_s is not None
                and request.terminal_status != "succeeded"
            ]
            if unsuccessful:
                raise _StageFailure(
                    "measured_run",
                    FailureReason.UNKNOWN_ERROR,
                    "request-scoped runtime result contains non-succeeded terminal",
                )
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
                self._uncertainty_evidence[key] = result[key]
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
        self._salvage_adapter_custody()
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
                if result.failure_reason == FailureReason.CLEANUP_FAILED:
                    raise _StageFailure(
                        "cleanup",
                        FailureReason.CLEANUP_FAILED,
                        result.message or "worker-started runtime process survived cleanup",
                    )
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
        self._capture_post_run_environment_observation()
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
        # Every salvage action is independent: one broken writer or adapter
        # cannot prevent later evidence and cleanup attempts.
        self._attempt_salvage_step("stop_sampling", self._stop_sampling_best_effort)
        self._attempt_salvage_step("adapter_custody", self._salvage_adapter_custody)
        self._attempt_salvage_step("runtime_cleanup", self._cleanup_best_effort)
        self._attempt_salvage_step(
            "failure_environment", self._capture_failure_fallback_environment
        )
        self._attempt_salvage_step("outputs", self._write_outputs)
        self._attempt_salvage_step("power_trace", self._write_trace)
        self._attempt_salvage_step("metadata", self._write_metadata)
        summary = self._failure_summary(
            status=STATUS_BY_REASON[failure.reason],
            failure_reason=failure.reason,
            failure_message=failure.message,
            idle_baseline=self._baseline,
            measurement_quality=self._minimal_quality(),
        )
        self._writer.write_summary(summary)
        return summary

    def _attempt_salvage_step(self, name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except Exception:  # noqa: BLE001 - later salvage steps must still run
            self._log(
                self._controller_log,
                "independent salvage step %s raised:" % name,
            )
            self._log(self._controller_log, traceback.format_exc())

    def _finalize_interrupted_run(
        self,
        interrupt: KeyboardInterrupt | SystemExit,
    ) -> None:
        """Salvage and finalize without ever replacing the original interrupt."""

        self._buffer_event(
            "failure",
            self._current_stage,
            "%s: %s" % (type(interrupt).__name__, interrupt),
            {"failure_reason": FailureReason.UNKNOWN_ERROR.value},
        )
        self._log(
            self._controller_log,
            "interrupt in stage %s: %s: %s"
            % (self._current_stage, type(interrupt).__name__, interrupt),
        )
        actions: list[tuple[str, Callable[[], Any]]] = [
            ("stop_sampling", self._stop_sampling_best_effort),
            ("adapter_custody", self._salvage_adapter_custody),
            ("runtime_cleanup", self._cleanup_best_effort),
            ("failure_environment", self._capture_failure_fallback_environment),
            ("outputs", self._write_outputs),
            ("power_trace", self._write_trace),
            ("metadata", self._write_metadata),
        ]
        for name, action in actions:
            try:
                action()
            except BaseException as cleanup_error:  # preserve the first interrupt
                self._log(
                    self._controller_log,
                    "interrupt salvage step %s raised %s: %s"
                    % (name, type(cleanup_error).__name__, cleanup_error),
                )
        summary = self._failure_summary(
            status=RunStatus.FAILED,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            failure_message="%s: %s" % (type(interrupt).__name__, interrupt),
            idle_baseline=self._baseline,
            measurement_quality=self._minimal_quality(),
        )
        try:
            self._writer.write_summary(summary)
        except BaseException as cleanup_error:
            self._log(
                self._controller_log,
                "interrupt summary staging raised %s: %s"
                % (type(cleanup_error).__name__, cleanup_error),
            )
        try:
            self._finish()
        except BaseException:
            # The caller's KeyboardInterrupt/SystemExit remains authoritative;
            # retention manifests and native pending paths preserve retry data.
            pass

    def _failure_summary(
        self,
        *,
        status: RunStatus,
        failure_reason: FailureReason,
        failure_message: str,
        idle_baseline: IdleBaseline | None,
        measurement_quality: MeasurementQuality,
    ) -> SummaryMetrics | SummaryMetricsV060:
        summary_type = SummaryMetricsV060 if self._is_axi_run() else SummaryMetrics
        return summary_type(
            status=status,
            failure_reason=failure_reason,
            failure_message=failure_message,
            idle_baseline=idle_baseline,
            measurement_quality=measurement_quality,
        )

    def _stop_sampling_best_effort(self) -> None:
        if (
            not self._sampling_active
            and not self._sampling_start_in_progress
        ) or self._telemetry is None or self._sampling_stop_claimed:
            return
        # D-026: even on the failure path the sampling window gets its closing
        # marker, stamped before the stop call, so post-hoc re-reduction sees
        # the same window semantics as a successful run.
        sampling_stopped_stamp = _clock_stamp(self._clock)
        if self._sampling_active:
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
            self._stop_sampling_once(sampling_stopped_stamp)
            self._capture_adapter_alignments()
            self._sampling_active = False
            self._sampling_start_in_progress = False
        except Exception:  # noqa: BLE001 - evidence salvage must not mask the failure
            self._log(
                self._controller_log,
                "best-effort stop_sampling raised after failure:",
            )
            self._log(self._controller_log, traceback.format_exc())

    def _stop_sampling_once(self, sampling_stopped_stamp: ClockStamp) -> bool:
        """Claim and execute the sampler stop at most once per lifecycle."""

        if self._sampling_stop_claimed or self._telemetry is None:
            return False
        self._sampling_stop_claimed = True
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
        except Exception:
            # Ordinary failures remain retryable by the failure-salvage path.
            self._sampling_stop_claimed = False
            raise
        return True

    def _salvage_adapter_custody(self) -> None:
        for adapter in (self._telemetry, self._runtime):
            if not isinstance(adapter, EvidenceCustodyProvider):
                continue
            report = adapter.salvage_custody(self._context)
            for item in report:
                if item.get("acknowledged") is not True:
                    self._log(
                        self._controller_log,
                        "adapter custody remains retained: %s" % item,
                    )

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

    def _is_axi_run(self) -> bool:
        return self._config.schema_extensions == [AXI_CONFIG_EXTENSION]

    def _axi_roster(self) -> tuple[RequestRoster, bytes]:
        policy = self._config.batch_policy
        if policy is None:
            raise ValueError("AXI batch policy is unavailable")
        source = Path(policy.request_roster_ref)
        raw = source.read_bytes()
        if axi_sha256_bytes(raw) != policy.request_roster_sha256:
            raise ValueError("configured request roster byte hash mismatch")
        roster = RequestRoster.from_mapping(json.loads(raw))
        normalized = roster.to_bytes()
        if normalized != raw:
            raise ValueError("configured request roster is not normalized bytes")
        return roster, normalized

    def _axi_common_event_metadata(
        self,
        result: AxiRuntimeResult,
        request: Any,
        *,
        scheduler_step_id: str | int | None,
    ) -> dict[str, Any]:
        policy = self._config.batch_policy
        assert policy is not None
        return {
            "request_id": request.request_id,
            "request_ordinal": request.request_ordinal,
            "request_input_id": request.request_input_id,
            "request_roster_sha256": policy.request_roster_sha256,
            "source_identity": result.primary_source_identity,
            "batch_group_id": result.batch.batch_group_id,
            "scheduler_step_id": scheduler_step_id,
        }

    def _axi_request_events(self, result: AxiRuntimeResult) -> list[RuntimeEvent]:
        events: list[RuntimeEvent] = []
        for request in result.requests:
            common = self._axi_common_event_metadata(
                result, request, scheduler_step_id=None
            )
            local: list[RuntimeEvent] = [
                RuntimeEvent(
                    request.submitted_at_s,
                    "request_submitted",
                    "request",
                    "request submitted",
                    dict(common),
                )
            ]
            if request.admitted_at_s is not None:
                metadata = dict(common)
                metadata["admitted_at_s"] = request.admitted_at_s
                local.append(
                    RuntimeEvent(
                        request.admitted_at_s,
                        "request_admitted",
                        "request",
                        "request admitted",
                        metadata,
                    )
                )
            for phase in request.phase_windows:
                phase_common = self._axi_common_event_metadata(
                    result,
                    request,
                    scheduler_step_id=phase.scheduler_step_id,
                )
                start_metadata = dict(phase_common)
                start_metadata["request_phase_ordinal"] = phase.request_phase_ordinal
                end_metadata = dict(start_metadata)
                local.extend(
                    [
                        RuntimeEvent(
                            phase.start_s,
                            "phase_start",
                            phase.phase,
                            f"{phase.phase} started",
                            start_metadata,
                        ),
                        RuntimeEvent(
                            phase.end_s,
                            "phase_end",
                            phase.phase,
                            f"{phase.phase} ended",
                            end_metadata,
                        ),
                    ]
                )
            scheduler_by_step = {
                emission.decode_step_ordinal: emission.scheduler_step_id
                for emission in request.emissions
            }
            for emission in request.emissions:
                metadata = self._axi_common_event_metadata(
                    result,
                    request,
                    scheduler_step_id=emission.scheduler_step_id,
                )
                token_ids = (
                    list(emission.emitted_token_ids)
                    if emission.emitted_token_ids is not None
                    else None
                )
                metadata.update(
                    decode_step_ordinal=emission.decode_step_ordinal,
                    output_token_start_ordinal=emission.output_token_start_ordinal,
                    emitted_count=emission.emitted_count,
                    tokens_proposed=emission.tokens_proposed,
                    tokens_accepted=emission.tokens_accepted,
                    target_emitted_count=emission.target_emitted_count,
                    emitted_token_ids=token_ids,
                    emitted_token_ids_sha256=(
                        axi_sha256_bytes(
                            b"joulewise.request_output_token_ids_slice.v1\n"
                            + axi_canonical_json_bytes(token_ids)
                        )
                        if token_ids is not None
                        else None
                    ),
                )
                local.append(
                    RuntimeEvent(
                        emission.timestamp_s,
                        "decode_emission",
                        "decode",
                        "decode emission",
                        metadata,
                    )
                )
            for token in request.tokens:
                if token.timestamp_s is None:
                    continue
                metadata = self._axi_common_event_metadata(
                    result,
                    request,
                    scheduler_step_id=scheduler_by_step.get(
                        token.decode_step_ordinal
                    ),
                )
                metadata.update(
                    decode_step_ordinal=token.decode_step_ordinal,
                    output_token_ordinal=token.output_token_ordinal,
                    token_id=token.token_id,
                    timestamp_provenance=token.timestamp_provenance,
                )
                local.append(
                    RuntimeEvent(
                        token.timestamp_s,
                        "token",
                        "decode",
                        "token callback",
                        metadata,
                    )
                )
            if request.terminal_at_s is not None:
                metadata = dict(common)
                metadata.update(
                    terminal_status=request.terminal_status,
                    stop_reason=request.stop_reason,
                    failure_reason=request.failure_reason,
                    failure_message=request.failure_message,
                    realized_output_token_count=len(request.tokens),
                    cancelled_proposal_counters=(
                        asdict(request.cancelled_proposal_counters)
                        if request.cancelled_proposal_counters is not None
                        else None
                    ),
                )
                local.append(
                    RuntimeEvent(
                        request.terminal_at_s,
                        "request_terminal",
                        "request",
                        "request terminal",
                        metadata,
                    )
                )
            # Stable timestamp ordering preserves the runtime/result sequence
            # at equal boundaries: phase end precedes the next phase start,
            # an emission precedes its singleton token callbacks, and terminal
            # evidence remains last.  Ordinals are request-local; the writer's
            # stable global timestamp sort then interleaves multiple requests.
            ordered = sorted(local, key=lambda event: event.timestamp_s)
            for ordinal, event in enumerate(ordered):
                metadata = dict(event.metadata)
                metadata["request_event_ordinal"] = ordinal
                events.append(replace(event, metadata=metadata))
        return events

    def _axi_output_artifacts(self, result: AxiRuntimeResult) -> dict[str, str]:
        roster, roster_bytes = self._axi_roster()
        roster_by_ordinal = {
            descriptor.request_ordinal: descriptor
            for descriptor in roster.requests
        }
        request_rows: list[dict[str, Any]] = []
        token_rows: list[dict[str, Any]] = []
        policy = self._config.batch_policy
        assert policy is not None
        for request in sorted(result.requests, key=lambda row: row.request_ordinal):
            if request.admitted_at_s is None:
                continue
            descriptor = roster_by_ordinal.get(request.request_ordinal)
            if descriptor is None or descriptor.request_input_id != request.request_input_id:
                raise ValueError("runtime request identity does not match roster")
            emitted_count = sum(item.emitted_count for item in request.emissions)
            proposed = (
                sum(int(item.tokens_proposed) for item in request.emissions)
                if self._config.speculation is not None
                and self._config.speculation.mode != "off"
                else None
            )
            accepted = (
                sum(int(item.tokens_accepted) for item in request.emissions)
                if proposed is not None
                else None
            )
            target = sum(item.target_emitted_count for item in request.emissions)
            if request.cancelled_proposal_counters is not None:
                counters = request.cancelled_proposal_counters
                if proposed is not None:
                    proposed += counters.tokens_proposed
                    accepted += counters.tokens_accepted
                target += counters.target_emitted_count
                emitted_count += counters.emitted_count
            token_ids = [item.token_id for item in request.tokens]
            complete_ids = all(
                isinstance(token_id, int) and not isinstance(token_id, bool)
                for token_id in token_ids
            )
            response_hash = (
                axi_sha256_bytes(request.response_text.encode("utf-8"))
                if request.response_text is not None
                else None
            )
            request_rows.append(
                {
                    "request_id": request.request_id,
                    "request_ordinal": request.request_ordinal,
                    "request_input_id": request.request_input_id,
                    "prompt_sha256": descriptor.prompt_sha256,
                    "request_roster_sha256": policy.request_roster_sha256,
                    "batch_group_id": result.batch.batch_group_id,
                    "terminal_status": request.terminal_status,
                    "output_policy_name": descriptor.output_policy_name,
                    "requested_output_tokens": descriptor.requested_output_tokens,
                    "output_token_count": emitted_count,
                    "stop_reason": request.stop_reason,
                    "failure_reason": request.failure_reason,
                    "response_text": request.response_text,
                    "response_text_sha256": response_hash,
                    "emitted_token_ids_sha256": (
                        axi_sha256_bytes(
                            b"joulewise.request_output_token_ids.v1\n"
                            + axi_canonical_json_bytes(token_ids)
                        )
                        if complete_ids
                        else None
                    ),
                    "tokens_proposed": proposed,
                    "tokens_accepted": accepted,
                    "target_emitted_count": target,
                    "acceptance_rate": (
                        accepted / proposed
                        if proposed is not None and proposed
                        else None
                    ),
                }
            )
            token_rows.extend(
                {
                    "request_id": request.request_id,
                    "request_ordinal": request.request_ordinal,
                    "request_input_id": request.request_input_id,
                    "output_token_ordinal": token.output_token_ordinal,
                    "decode_step_ordinal": token.decode_step_ordinal,
                    "token_id": token.token_id,
                    "timestamp_s": token.timestamp_s,
                    "timestamp_provenance": token.timestamp_provenance,
                }
                for token in request.tokens
            )
        root_path = self._writer.path / "request_roster.json"
        with root_path.open("xb") as handle:
            handle.write(roster_bytes)
        return {
            "requests.jsonl": "".join(
                axi_canonical_json_bytes(row).decode("utf-8") + "\n"
                for row in request_rows
            ),
            "request_tokens.jsonl": "".join(
                axi_canonical_json_bytes(row).decode("utf-8") + "\n"
                for row in token_rows
            ),
        }

    def _write_outputs(self) -> None:
        if self._outputs_written or self._runtime_result is None:
            return
        if self._is_axi_run():
            if self._runtime_result.axi_result is None:
                raise ValueError("AXI runtime result is unavailable")
            for name, text in self._axi_output_artifacts(
                self._runtime_result.axi_result
            ).items():
                self._writer.write_output(name, text)
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
        if self._is_axi_run():
            policy = self._config.batch_policy
            speculation = self._config.speculation
            assert policy is not None and speculation is not None
            extra["event_semantics_version"] = EVENT_SEMANTICS_VERSION
            extra["speculation"] = speculation.to_dict()
            axi = (
                self._runtime_result.axi_result
                if self._runtime_result is not None
                else None
            )
            if axi is None:
                extra["batch"] = {
                    "policy_schema_version": AXI_CONFIG_EXTENSION,
                    "configured_batch_size": policy.requested_batch_size,
                    "realized_batch_size": 0,
                    "submitted_request_count": 0,
                    "admitted_request_count": 0,
                    "terminal_request_count": 0,
                    "batch_group_id": None,
                    "request_roster_sha256": policy.request_roster_sha256,
                }
            else:
                extra["batch"] = {
                    "policy_schema_version": AXI_CONFIG_EXTENSION,
                    "configured_batch_size": policy.requested_batch_size,
                    "realized_batch_size": axi.batch.realized_batch_size,
                    "submitted_request_count": axi.batch.submitted_request_count,
                    "admitted_request_count": axi.batch.admitted_request_count,
                    "terminal_request_count": axi.batch.terminal_request_count,
                    "batch_group_id": axi.batch.batch_group_id,
                    "request_roster_sha256": policy.request_roster_sha256,
                }
                extra["runtime"] = {
                    "primary_source_identity": axi.primary_source_identity,
                    "target_model_artifact_sha256": axi.target_model_artifact_sha256,
                    "target_tokenizer_identity": axi.target_tokenizer_identity.to_dict(),
                    "target_tokenizer_artifact_files": dict(
                        axi.target_tokenizer_artifact_files
                    ),
                }
        extra["config_warnings"] = [dict(item) for item in self._config.config_warnings]
        extra["model"] = asdict(self._config.model)
        extra["quantization"] = asdict(self._config.quantization)
        if self._device_metadata is not None:
            # Preserve adapter values verbatim for the bundle writer's single
            # path-aware quarantine pass (including exact cycle locations).
            extra["device"] = self._device_metadata
        if self._connection_metadata is not None:
            extra["connection"] = self._connection_metadata
        if self._environment is not None:
            extra["environment"] = self._environment
        if self._campaign_policy_binding is not None:
            extra["campaign_policy"] = self._campaign_policy_binding
        if self._campaign_environment_preflight is not None:
            extra["campaign_environment_preflight"] = (
                self._campaign_environment_preflight
            )
        if self._environment_admission is not None:
            extra["environment_admission"] = self._environment_admission
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
                adapters["runtime"]["cleanup_metadata"] = self._runtime_cleanup_metadata
            if self._runtime_alignments:
                adapters["runtime"]["clock_alignments"] = self._runtime_alignments
        if self._telemetry is not None:
            adapters["telemetry"] = {"name": self._telemetry.name}
            if self._telemetry_metadata:
                _merge_adapter_metadata(adapters["telemetry"], self._telemetry_metadata)
            if self._telemetry_alignments:
                adapters["telemetry"]["clock_alignments"] = self._telemetry_alignments
        extra["adapters"] = adapters
        if self._baseline is not None:
            extra["idle_baseline"] = asdict(self._baseline)
        if self._thermal_pre is not None:
            extra["thermal_pre"] = asdict(self._thermal_pre)
        if self._thermal_post is not None:
            extra["thermal_post"] = asdict(self._thermal_post)
        if self._uncertainty_evidence is not None:
            evidence = dict(self._uncertainty_evidence)
            idle_bound_w = evidence.pop("idle_drift_bound_w", None)
            extra["uncertainty_evidence"] = evidence
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
            token_count_source = self._runtime_result.metadata.get(
                "token_count_source"
            )
            if token_count_source in {
                "server_usage",
                "stream_chunk_fallback",
            }:
                extra["workload_observed"]["token_count_source"] = (
                    token_count_source
                )
            if self._runtime_result.workload_provenance is not None:
                extra["workload_provenance"] = self._runtime_result.workload_provenance
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
        node_cleanup = [
            *_adapter_cleanup_report(self._runtime),
            *_adapter_cleanup_report(self._telemetry),
        ]
        # Caller-supplied metadata (Slice 2F: the experiment runner records a
        # cooldown cap-hit against the following rep here). Lands under the
        # dedicated "extra" key so it never collides with controller fields and
        # the reducer reads it from one known place.
        controller_extra = dict(self._extra_metadata)
        if node_cleanup:
            controller_extra["node_cleanup"] = node_cleanup
        if controller_extra:
            extra["extra"] = controller_extra
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

    def _capture_post_run_environment_observation(self) -> None:
        if not isinstance(self._environment, dict):
            return
        if isinstance(self._clock, FakeClock):
            self._environment["post_run_observation"] = {
                "capture_skipped": True,
                "skip_reason": "fake_clock",
                "captured_at_s": None,
            }
            return
        started_at_s = self._clock.now()
        observation = collect_environment_guard_observation()
        captured_at_s = self._clock.now()
        observation.update(
            {
                "capture_skipped": False,
                "captured_at_s": captured_at_s,
                "capture_duration_s": captured_at_s - started_at_s,
            }
        )
        self._environment["post_run_observation"] = observation

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
        cleanup_failed = sorted(
            {
                str(item["path"])
                for item in (
                    _adapter_cleanup_report(self._runtime)
                    + _adapter_cleanup_report(self._telemetry)
                )
                if item.get("removed") is False
                and item.get("eventually_removed") is not True
                and isinstance(item.get("path"), str)
            }
        )
        return MeasurementQuality(
            requested_sampling_hz=self._config.sampling.power_hz,
            idle_power_w_stddev=(
                self._baseline.power_w_stddev if self._baseline is not None else None
            ),
            telemetry_source=self._telemetry.name if self._telemetry is not None else None,
            idle_window_suspect=(
                self._baseline.idle_window_suspect if self._baseline is not None else None
            ),
            remote_cleanup_failed=cleanup_failed or None,
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
        if self._suite_preparation_failure is not None:
            raise self._suite_preparation_failure
        preparation = self._suite_preparation
        if preparation is None:  # defensive: suite refs always preflight above
            raise _StageFailure(
                "validate",
                FailureReason.UNKNOWN_ERROR,
                "suite manifest preparation is missing",
            )
        manifest = preparation.manifest
        rep_index = _suite_rep_index_from_run_id(self._config.run_id)
        self._suite_manifest = manifest
        self._suite_effective_manifest = preparation.effective_manifest
        self._suite_manifest_sha256 = preparation.manifest_sha256
        self._suite_source_file_sha256 = preparation.source_file_sha256
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
    policy: CooldownPolicy | None = None,
) -> dict[str, Any]:
    """Hold for a complete sustained cooldown-v2 recovery window.

    Sub-window means are weighted by their evidenced durations over the most
    recent complete sustained window.  Release requires both a complete
    wall-clock span and the policy's minimum evidence coverage, so small probe
    gaps neither prevent recovery nor masquerade as a complete window.
    Recovery is one-sided: values below the reference count as recovered.
    Thermal pressure must be nominal at release, and an optional calibrated
    absolute ceiling is an additional upper cap, never an alternative escape.

    All blocking is via ``telemetry.measure_idle`` (which sleeps on the clock),
    so a ``FakeClock`` makes the gate instant and exact in tests.

    ``run_id`` (NV-2/ARC-7): the gate calls ``measure_idle`` out-of-run with
    no ``RunContext``, so adapters that need a run id for node-side isolation
    fall back to ``config.run_id`` - which is ``None`` for generated-id
    experiments. When given, ``run_id`` is stamped onto the sub-window config
    so those adapters see a cooldown-scoped id instead of failing.
    """
    selected = policy if policy is not None else CooldownPolicy()
    reference = reference_baseline.power_w_mean
    sub_config = replace(
        config,
        run_id=run_id if run_id is not None else config.run_id,
        sampling=replace(config.sampling, idle_seconds=selected.subwindow_s),
    )
    start_s = clock.now()
    readings: list[tuple[float, float, float, float]] = []
    trace: list[dict[str, Any]] = []
    while True:
        subwindow_start_s = clock.now()
        baseline = telemetry.measure_idle(sub_config)
        now_s = clock.now()
        duration_s = baseline.duration_s
        if not isinstance(duration_s, int | float) or duration_s <= 0.0:
            duration_s = max(0.0, now_s - subwindow_start_s)
        evidence_start_s = now_s - float(duration_s)
        # Do not let a backend-reported duration reach backward across the
        # actual start of this bounded capture.
        evidence_start_s = max(evidence_start_s, subwindow_start_s)
        readings.append(
            (subwindow_start_s, evidence_start_s, now_s, baseline.power_w_mean)
        )
        cutoff = now_s - selected.sustained_window_s
        readings = [reading for reading in readings if reading[2] > cutoff]
        weighted_sum = 0.0
        coverage_s = 0.0
        retained_start_s: float | None = None
        for capture_start, evidence_start, evidence_end, value in readings:
            clipped_start = max(evidence_start, cutoff)
            overlap_s = max(0.0, evidence_end - clipped_start)
            weighted_sum += overlap_s * value
            coverage_s += overlap_s
            if overlap_s > 0.0:
                retained_capture_start = max(capture_start, cutoff)
                retained_start_s = (
                    retained_capture_start
                    if retained_start_s is None
                    else min(retained_start_s, retained_capture_start)
                )
        rolling_mean = weighted_sum / coverage_s if coverage_s > 0.0 else None
        window_span_s = (
            max(0.0, now_s - retained_start_s)
            if retained_start_s is not None
            else 0.0
        )
        waited_s = now_s - start_s
        try:
            thermal = telemetry.thermal_state(sub_config)
            thermal_pressure = thermal.thermal_pressure
        except Exception:  # noqa: BLE001 - unknown thermal fails the conjunctive gate
            thermal_pressure = None
        thermal_nominal = (
            isinstance(thermal_pressure, str)
            and thermal_pressure.lower() in {"nominal", "normal"}
        )
        reference_upper_w = reference * (1.0 + selected.tolerance_fraction)
        effective_upper_w = reference_upper_w
        if selected.absolute_ceiling_w is not None:
            effective_upper_w = min(effective_upper_w, selected.absolute_ceiling_w)
        required_coverage_s = (
            selected.coverage_fraction * selected.sustained_window_s
        )
        span_complete = window_span_s + 1e-9 >= selected.sustained_window_s
        coverage_complete = coverage_s + 1e-9 >= required_coverage_s
        window_complete = span_complete and coverage_complete
        power_recovered = (
            rolling_mean is not None and rolling_mean <= effective_upper_w
        )
        release = bool(
            window_complete
            and power_recovered
            and (thermal_nominal or not selected.require_thermal_nominal)
        )
        trace.append(
            {
                "timestamp_s": now_s,
                "waited_s": waited_s,
                "rolling_mean_power_w": rolling_mean,
                "window_span_s": window_span_s,
                "window_coverage_s": coverage_s,
                "required_coverage_s": required_coverage_s,
                "span_complete": span_complete,
                "coverage_complete": coverage_complete,
                "window_complete": window_complete,
                "reference_upper_w": reference_upper_w,
                "absolute_ceiling_w": selected.absolute_ceiling_w,
                "effective_upper_w": effective_upper_w,
                "thermal_pressure": thermal_pressure,
                "thermal_nominal": thermal_nominal,
                "release": release,
                "baseline": _jsonable(asdict(baseline)),
            }
        )
        common = {
            "policy_version": selected.policy_version,
            "thresholds": {
                "subwindow_s": selected.subwindow_s,
                "sustained_window_s": selected.sustained_window_s,
                "coverage_fraction": selected.coverage_fraction,
                "tolerance_fraction": selected.tolerance_fraction,
                "cap_s": selected.cap_s,
                "absolute_ceiling_w": selected.absolute_ceiling_w,
                "require_thermal_nominal": selected.require_thermal_nominal,
            },
            "waited_s": waited_s,
            "reference_power_w": reference,
            "tolerance_fraction": selected.tolerance_fraction,
            "absolute_ceiling_w": selected.absolute_ceiling_w,
            "reference_upper_w": reference_upper_w,
            "effective_upper_w": effective_upper_w,
            "decision_rolling_mean_power_w": rolling_mean,
            "window_required_s": selected.sustained_window_s,
            "window_span_s": window_span_s,
            "window_coverage_s": coverage_s,
            "required_coverage_s": required_coverage_s,
            "span_complete": span_complete,
            "coverage_complete": coverage_complete,
            "window_complete": window_complete,
            "thermal_pressure": thermal_pressure,
            "thermal_nominal": thermal_nominal,
            "release_criterion": {
                "power": "duration_weighted_rolling_mean <= effective_upper_w",
                "reference_bound": "reference_power_w * (1 + tolerance_fraction)",
                "absolute_ceiling_role": "additional_upper_cap",
                "window": "complete_sustained_span_and_minimum_coverage",
                "coverage": "window_coverage_s >= coverage_fraction * sustained_window_s",
                "thermal": (
                    "nominal_required"
                    if selected.require_thermal_nominal
                    else "not_required"
                ),
            },
        }
        if release:
            return {
                "result": "recovered",
                **common,
                "_trace": trace,
            }
        if waited_s >= selected.cap_s:
            return {
                "result": "cap_hit",
                **common,
                "_trace": trace,
            }


def _within_tolerance(value: float, reference: float, tolerance: float) -> bool:
    """Compatibility helper for cooldown-v2's one-sided recovery bound."""
    return value <= reference * (1.0 + tolerance)


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


def _adapter_cleanup_report(adapter: Any) -> list[dict[str, Any]]:
    if adapter is None:
        return []
    getter = getattr(adapter, "cleanup_report", None)
    if not callable(getter):
        return []
    try:
        report = getter()
    except Exception:  # noqa: BLE001 - cleanup evidence must not disturb lifecycle.
        return []
    if not isinstance(report, list):
        return []
    return [dict(item) for item in report if isinstance(item, dict)]


def _merge_adapter_metadata(target: dict[str, Any], metadata: dict[str, Any]) -> None:
    # Do not recursively normalize here: RunBundleWriter owns the one
    # deterministic quarantine pass and its path-addressed diagnostics.
    for key, value in metadata.items():
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
    campaign_policy, policy_binding, preflight = _campaign_policy_from_environment()

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
    environment_snapshot = (
        _environment_for_experiment(clock) if campaign_policy is None else None
    )

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
    frozen_cooldown_anchor: dict[str, Any] | None = None

    for rep in range(1, repetitions + 1):
        member_config = replace(config, run_id=f"{experiment_id}__r{rep}")
        member_extra_metadata = dict(next_extra_metadata or {})
        member_extra_metadata["preceding_member_end_s"] = previous_member_end_s
        member_environment = environment_snapshot
        if campaign_policy is not None:
            member_environment = _capture_environment(
                clock,
                capture_scope="run",
                captured_for_rep=rep,
                settle_s=PRE_IDLE_SETTLE_S,
            )
        bundle_path, summary = run_benchmark(
            member_config,
            runs_root,
            clock,
            registry=registry,
            extra_metadata=member_extra_metadata,
            environment_snapshot=member_environment,
            campaign_policy=campaign_policy,
            campaign_policy_binding=policy_binding,
            campaign_environment_preflight=preflight,
        )
        previous_member_end_s = clock.now()
        next_extra_metadata = None
        results.append((bundle_path, summary))
        manifest["members"].append(bundle_path.name)
        manifest["member_gaps"].append(_member_gap_note(bundle_path))
        manifest["condition_order"].append(condition_name)
        # Commit member custody before the reconstructable aggregate derivation.
        # Removing the prior aggregate prevents an interrupt from leaving a
        # newly extended member list beside a stale aggregate.
        manifest.pop("aggregate", None)
        manifest_path = write_experiment_manifest(runs_root, manifest)
        try:
            manifest["aggregate"] = aggregate_experiment(runs_root, manifest)
        except Exception as exc:
            manifest["aggregate_error"] = {
                "error_type": type(exc).__name__,
                "message": str(exc),
                "retryable": True,
            }
            write_experiment_manifest(runs_root, manifest)
            raise
        manifest.pop("aggregate_error", None)
        manifest_path = write_experiment_manifest(runs_root, manifest)

        reference_eligibility = _experiment_cooldown_reference_eligibility(
            bundle_path, summary
        )
        if frozen_cooldown_anchor is None and reference_eligibility["eligible"]:
            frozen_cooldown_anchor = _experiment_cooldown_anchor(
                bundle_path, summary, reference_eligibility
            )
            manifest["cooldown_anchor"] = frozen_cooldown_anchor
            manifest_path = write_experiment_manifest(runs_root, manifest)

        if rep < repetitions:
            note, cap_hit = _cooldown_between_reps(
                config,
                runs_root,
                experiment_id,
                bundle_path.name,
                summary,
                registry,
                clock,
                campaign_policy=campaign_policy,
                frozen_anchor=frozen_cooldown_anchor,
            )
            manifest["cooldown"].append(note)
            manifest_path = write_experiment_manifest(runs_root, manifest)
            if cap_hit:
                next_extra_metadata = {"cooldown_cap_hit": True}
            if note.get("fail_closed_action") == "flag":
                next_extra_metadata = dict(next_extra_metadata or {})
                next_extra_metadata["environment_admission_failed"] = True
            elif note.get("fail_closed_action") == "abort":
                raise RuntimeError(
                    "cooldown v2 failed closed: "
                    + str(note.get("reason", "eligible reference unavailable"))
                )

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
    campaign_policy: CampaignPolicy | None = None,
    frozen_anchor: dict[str, Any] | None = None,
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
    reference_baseline = summary.idle_baseline
    if campaign_policy is not None and campaign_policy.idle_admission.enabled:
        bundle_path = Path(runs_root) / after_member
        eligibility = _experiment_cooldown_reference_eligibility(
            bundle_path, summary
        )
        note["reference_eligibility"] = eligibility
        note["anchor_provenance"] = frozen_anchor
        if eligibility["eligible"]:
            note["reference_selection"] = "preceding_eligible_baseline"
        else:
            anchor_baseline = _idle_baseline_from_anchor(frozen_anchor)
            if anchor_baseline is not None:
                reference_baseline = anchor_baseline
                note["reference_selection"] = "frozen_clean_anchor"
            else:
                action = campaign_policy.idle_admission.on_fail
                note.update(
                    {
                        "result": "unknown",
                        "reason": (
                            "preceding baseline is ineligible and no frozen clean "
                            "cooldown anchor is available"
                        ),
                        "reference_selection": "none",
                        "fail_closed_action": action.value,
                    }
                )
                return note, False
    elif reference_baseline is None:
        note.update({"result": "skipped", "reason": "no idle baseline from previous rep"})
        return note, False

    if reference_baseline is None:
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
            telemetry,
            reference_baseline,
            config,
            clock,
            run_id=cooldown_run_id,
            policy=(campaign_policy.cooldown if campaign_policy is not None else None),
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


def _experiment_cooldown_reference_eligibility(
    bundle_path: Path,
    summary: SummaryMetrics | SummaryMetricsV060,
) -> dict[str, Any]:
    """Fail closed when an experiment repetition is proposed as a reference."""

    reasons: list[str] = []
    baseline = summary.idle_baseline
    if baseline is None:
        reasons.append("idle_baseline_unavailable")
    elif baseline.idle_window_suspect is not False:
        reasons.append("idle_window_not_clean")
    try:
        metadata = json.loads((bundle_path / "metadata.json").read_text())
    except (OSError, json.JSONDecodeError):
        metadata = None
    admission = (
        metadata.get("environment_admission") if isinstance(metadata, dict) else None
    )
    policy_binding = (
        metadata.get("campaign_policy") if isinstance(metadata, dict) else None
    )
    if not isinstance(admission, dict):
        reasons.append("environment_admission_provenance_missing")
    else:
        if admission.get("critical_environment_passed") is not True:
            reasons.append("critical_environment_not_passed")
        if admission.get("decision") != "admitted":
            reasons.append("idle_admission_not_passed")
        if admission.get("reference_provenance_present") is not True:
            reasons.append("reference_provenance_incomplete")
    if (
        not isinstance(policy_binding, dict)
        or not isinstance(policy_binding.get("sha256"), str)
        or not policy_binding.get("sha256")
    ):
        reasons.append("campaign_policy_provenance_missing")
    return {
        "bundle_id": bundle_path.name,
        "eligible": baseline is not None and not reasons,
        "reasons": sorted(reasons),
        "idle_window_suspect": (
            baseline.idle_window_suspect if baseline is not None else None
        ),
        "critical_environment_passed": (
            admission.get("critical_environment_passed")
            if isinstance(admission, dict)
            else None
        ),
        "provenance_present": bool(
            isinstance(admission, dict)
            and admission.get("reference_provenance_present") is True
            and isinstance(policy_binding, dict)
            and policy_binding.get("sha256")
        ),
    }


def _experiment_cooldown_anchor(
    bundle_path: Path,
    summary: SummaryMetrics | SummaryMetricsV060,
    eligibility: dict[str, Any],
) -> dict[str, Any]:
    baseline = summary.idle_baseline
    assert baseline is not None
    try:
        metadata = json.loads((bundle_path / "metadata.json").read_text())
    except (OSError, json.JSONDecodeError):
        metadata = {}
    admission = metadata.get("environment_admission", {})
    per_run = (
        admission.get("per_run_environment_evaluation", {})
        if isinstance(admission, dict)
        else {}
    )
    return {
        "schema_version": "joulewise.cooldown_anchor.v1",
        "source_kind": "first_admission_passing_baseline",
        "bundle_id": bundle_path.name,
        "baseline": _jsonable(asdict(baseline)),
        "eligibility": eligibility,
        "environment_snapshot_sha256": (
            per_run.get("snapshot_sha256") if isinstance(per_run, dict) else None
        ),
        "immutable_after_freeze": True,
    }


def _idle_baseline_from_anchor(
    anchor: dict[str, Any] | None,
) -> IdleBaseline | None:
    if not isinstance(anchor, dict) or anchor.get("immutable_after_freeze") is not True:
        return None
    raw = anchor.get("baseline")
    if not isinstance(raw, dict):
        return None
    try:
        return IdleBaseline(
            power_w_mean=float(raw["power_w_mean"]),
            power_w_stddev=float(raw["power_w_stddev"]),
            duration_s=float(raw["duration_s"]),
            sample_count=int(raw["sample_count"]),
            telemetry_backend=TelemetryBackend(raw["telemetry_backend"]),
            gpu_idle_ratio_mean=raw.get("gpu_idle_ratio_mean"),
            gpu_idle_ratio_min=raw.get("gpu_idle_ratio_min"),
            gpu_freq_mhz_mean=raw.get("gpu_freq_mhz_mean"),
            gpu_freq_hz_mean=raw.get("gpu_freq_hz_mean"),
            idle_window_suspect=raw.get("idle_window_suspect"),
        )
    except (KeyError, TypeError, ValueError):
        return None


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
