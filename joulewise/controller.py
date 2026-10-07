"""Single-run benchmark controller: lifecycle, status mapping, deferred logging.

Executes one measured run end-to-end (Slice 2C; repetitions and experiment
manifests arrive with the experiment runner in Slice 2F) and applies:

- D-002: raw evidence first - every run, including failed ones, leaves a
  complete bundle whose artifacts can be re-reduced without re-running
  hardware.
- D-003/D-019: measurement timestamps come from the injected
  :class:`joulewise.clock.Clock`. Battery observations and their span stamps
  use an independent clock so they cannot consume measurement timing inputs.
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
import math
import os
import stat
import sys
import threading
import traceback
from collections.abc import Callable
from copy import deepcopy
from dataclasses import asdict, dataclass, replace
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

import joulewise.adapters
from joulewise import battery_float
from joulewise.aggregate import aggregate_experiment
from joulewise import reduce as reduce_module
from joulewise.bundle import (
    BundleError,
    RunBundleWriter,
    _cli_config_source,
    _writer_launch_lineage,
    generate_run_id,
    sanitize_id_component,
    write_experiment_manifest,
    write_experiment_rejection_verdict,
)
from joulewise.clock import Clock, ClockStamp, FakeClock, SystemClock
from joulewise.cooldown_anchor import (
    COOLDOWN_ANCHOR_VERDICT_SCHEMA_VERSION,
    cooldown_anchor_eligibility,
    idle_baseline_from_anchor,
)
from joulewise.cooldown import cooldown_disposition_from_raw
from joulewise.environment import (
    collect_environment_guard_observation,
    collect_environment_snapshot,
    empty_environment_snapshot,
    evaluate_environment_policy,
)
from joulewise.environment_admission import environment_observation_failure
from joulewise.idle_admission import (
    CONDITION_CPU_SAMPLES_INSUFFICIENT,
    CONDITION_CPU_TELEMETRY_MALFORMED,
    CONDITION_CPU_TELEMETRY_MISSING,
    CONDITION_GPU_ADMISSION_UNKNOWN,
    evaluate_cpu_idle_admission,
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
    SchemaError,
    SummaryMetrics,
    SummaryMetricsV060,
    TelemetryBackend,
)
from joulewise.sampler_teardown import SamplerTeardown
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
    "record_cooldown_anchor_rejection",
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
DEFAULT_POWERMETRICS_POST_WINDOW_DWELL_S = 1.0
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
    FailureReason.MODEL_IDENTITY_MISMATCH: RunStatus.FAILED,
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
    instrument_calibration_dir: Path | None = None,
    instrument_power_policy: str | None = None,
    post_window_sampling_dwell_s: float | None = None,
    battery_runner: Callable | None = None,
    battery_clock: Clock | None = None,
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
    if registry is None:
        registry = joulewise.adapters
    # HAZARD_PACK dispatch (gate-prune core lane CTL): a context only when the
    # runs root carries the hazard lineage locator; None keeps the legacy path.
    from joulewise.flags import core as flags_core  # noqa: PLC0415

    hazard = flags_core.hazard_flag_context(runs_root, writer="core-controller")
    pre_resolved_telemetry: TelemetryAdapter | None = None
    runtime_powermetrics_sha256: str | None = None
    binary_identity_unmeasured: str | None = None
    if instrument_calibration_dir is not None:
        pre_resolved_telemetry, failure = registry.resolve_telemetry(config, clock)
        if pre_resolved_telemetry is None:
            detail = failure.message if failure is not None else "unknown resolution failure"
            raise ValueError(
                "instrument calibration attachment cannot observe the selected "
                f"telemetry executable: {detail}"
            )
        try:
            runtime_powermetrics_sha256 = _runtime_powermetrics_digest(
                pre_resolved_telemetry.device_metadata(config)
            )
        except ValueError as exc:
            if hazard is None:
                raise
            # The binary digest is observed per invocation: an unobserved
            # digest is this member's fact, flagged once its bundle exists.
            # A present digest that differs from the calibrated one still
            # refuses in the attachment.
            runtime_powermetrics_sha256 = None
            binary_identity_unmeasured = str(exc)[:300]
    if campaign_policy is None:
        (
            campaign_policy,
            campaign_policy_binding,
            campaign_environment_preflight,
        ) = _campaign_policy_from_environment()
    runtime_power_policy = _runtime_power_policy_observation(
        campaign_environment_preflight
    )
    attachment = _load_instrument_calibration_attachment(
        instrument_calibration_dir,
        power_policy=instrument_power_policy,
        runtime_powermetrics_sha256=runtime_powermetrics_sha256,
        runtime_power_policy=runtime_power_policy,
        runs_root=runs_root,
        config=config,
        g2a_context=(config, runs_root, Path(os.environ["JOULEWISE_G2A_PRE_BRACKET_PLAN"]))
        if "JOULEWISE_G2A_PRE_BRACKET_PLAN" in os.environ else None,
        hazard=hazard,
    )
    config, suite_preparation, suite_preparation_failure = (
        _prepare_suite_manifest_for_new_bundle(config)
    )
    if post_window_sampling_dwell_s is None:
        post_window_sampling_dwell_s = (
            campaign_policy.post_window_sampling_dwell_s
            if campaign_policy is not None
            and config.hardware_target.telemetry_backend
            == TelemetryBackend.POWERMETRICS
            else (
                DEFAULT_POWERMETRICS_POST_WINDOW_DWELL_S
                if config.hardware_target.telemetry_backend
                == TelemetryBackend.POWERMETRICS
                else 0.0
            )
        )
    if (
        isinstance(post_window_sampling_dwell_s, bool)
        or not isinstance(post_window_sampling_dwell_s, int | float)
        or not math.isfinite(float(post_window_sampling_dwell_s))
        or float(post_window_sampling_dwell_s) < (
            1.0
            if config.hardware_target.telemetry_backend
            == TelemetryBackend.POWERMETRICS
            else 0.0
        )
    ):
        raise ValueError(
            "post-window sampling dwell must be finite and at least 1.0 s "
            "for powermetrics collection"
        )
    writer = RunBundleWriter.create(runs_root, config, clock)

    def make_execution() -> _Execution:
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
            attachment.metadata if attachment is not None else None,
            pre_resolved_telemetry,
            float(post_window_sampling_dwell_s),
            battery_runner,
            battery_clock,
            hazard=hazard,
            calibration_physics_seed=(
                attachment.physics_seed if attachment is not None else None
            ),
        )

    if hazard is None:
        if attachment is not None:
            attachment.install(writer.path)
        return make_execution().execute()
    # HAZARD (review F3 of PLAN2 row 8): the bundle exists from here on, so an
    # interrupt (SIGTERM becomes SystemExit) during the flag records or the
    # attachment install is salvaged and finalized like one in the lifecycle.
    # The constructor only stores state; a custody ValueError from install
    # still propagates unchanged.
    execution = make_execution()
    try:
        if binary_identity_unmeasured is not None:
            flags_core.emit(
                hazard, "instrument.binary_identity_unmeasured", level="member",
                run_id=writer.run_id,
                observed={"runtime_powermetrics_sha256": None},
                detail=binary_identity_unmeasured,
                legacy_site="joulewise/controller.py:795@e6b6a0ce",
                legacy_code="runtime_powermetrics_digest_unavailable",
            )
        if attachment is not None and attachment.refit_cache_miss is not None:
            # M1: the member refit the calibration itself (no usable window
            # verdict).  A record of time spent, not of the bound: the refit
            # verified the physics exactly as before.
            flags_core.emit(
                hazard, "calibration.refit_cache_miss", level="member",
                run_id=writer.run_id, observed=attachment.refit_cache_miss,
                legacy_site="joulewise/controller.py:575@89571045b",
                legacy_code="verify_stored_evidence_physics",
            )
        if attachment is not None:
            attachment.install(writer.path)
    except (KeyboardInterrupt, SystemExit) as interrupt:
        execution._finalize_interrupted_run(interrupt)
        raise
    return execution.execute()


@dataclass(frozen=True)
class _InstrumentCalibrationAttachment:
    files: dict[str, bytes]
    metadata: dict[str, Any]
    # HAZARD only (PLAN2 P2-CTL; None on the legacy path).  ``sources`` maps
    # each installed relative path to the verified file it was read from, so
    # the install can clone it (t1-06); ``physics_seed`` is the reduce-cache
    # seed {evidence sha256: verified effective bound} (M2);
    # ``refit_cache_miss`` says why the window verdict (J1) was not used (M1).
    sources: dict[str, Path] | None = None
    physics_seed: dict[str, float] | None = None
    refit_cache_miss: dict[str, Any] | None = None

    def install(self, bundle_path: Path) -> None:
        root = bundle_path / "instrument_calibration"
        if self.sources is None:
            for relative, raw in sorted(self.files.items()):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb") as handle:
                    handle.write(raw)
            return
        # HAZARD (t1-06): clone each verified source file (APFS clonefile, no
        # data copy), else write the verified bytes.  Either way the installed
        # copy is re-hashed against the bytes this attachment verified; a
        # clone that does not match is replaced by the byte copy, and a byte
        # copy that does not match refuses (custody keeper).
        for relative, raw in sorted(self.files.items()):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            expected = hashlib.sha256(raw).hexdigest()
            source = self.sources.get(relative)
            if source is not None and _clone_file(source, path):
                if _installed_copy_sha256(path) == expected:
                    continue
                path.unlink(missing_ok=True)
            with path.open("xb") as handle:
                handle.write(raw)
            if _installed_copy_sha256(path) != expected:
                raise ValueError(
                    "instrument calibration installed copy does not match its "
                    f"verified bytes: {relative}"
                )


def _clone_file(source: Path, destination: Path) -> bool:
    """APFS ``clonefile(2)`` without following a symlink; False when unavailable.

    Never raises: any failure (another volume, another OS, a symlink or a
    non-regular source) leaves no file behind and the caller writes bytes.
    """

    if sys.platform != "darwin":
        return False
    try:
        import ctypes  # noqa: PLC0415

        libc = ctypes.CDLL(None, use_errno=True)
        clonefile = libc.clonefile
        clonefile.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32)
        clonefile.restype = ctypes.c_int
        clone_nofollow = 0x0001
        if clonefile(os.fsencode(source), os.fsencode(destination), clone_nofollow) != 0:
            return False
        if not stat.S_ISREG(os.lstat(destination).st_mode):
            destination.unlink(missing_ok=True)
            return False
        return True
    except Exception:  # noqa: BLE001 - the byte copy is the fallback
        try:
            if destination.is_symlink() or destination.exists():
                destination.unlink()
        except OSError:
            pass
        return False


def _installed_copy_sha256(path: Path) -> str | None:
    try:
        if not stat.S_ISREG(os.lstat(path).st_mode):
            return None
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
        return digest.hexdigest()
    except OSError:
        return None


# J1 (PLAN2 section 3.2): the window calibration verdict, written once by the
# chain (P2-CHAIN) right after the pre-slot screen, next to the pre-slot
# capture directory.  A member that matches every digest skips the refit;
# anything else is a cache miss: the member refits and flags, never refuses.
WINDOW_CALIBRATION_VERDICT_BASENAME = "window_calibration_verdict.json"
WINDOW_CALIBRATION_VERDICT_SCHEMA = "joulewise.window_calibration_verdict.v1"


def window_calibration_estimator_files_sha256() -> dict[str, str] | None:
    """The J1 ``estimator_files_sha256`` value: {repo path: sha256} of the
    estimator code that runs the refit (``ESTIMATOR_CODE_PATHS``), as this
    process loads it; None when a file is unreadable."""

    from joulewise.calibration_bracketing import (  # noqa: PLC0415
        _current_estimator_code_sha256,
    )

    return _current_estimator_code_sha256()


def _window_calibration_verdict_bound(
    capture_directory: Path,
    files: dict[str, bytes],
    *,
    stored_bound: float,
) -> tuple[float | None, dict[str, Any] | None]:
    """Read J1; return ``(effective bound, None)`` only on a full match.

    The digests compared are those of the bytes this attachment verified
    against the capture manifest and installs (evidence, plist, events,
    manifest), plus the estimator code now loaded.  Otherwise
    ``(None, miss)``, where ``miss`` names the reason.  Never raises.
    """

    path = capture_directory.parent / WINDOW_CALIBRATION_VERDICT_BASENAME
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return None, {"reason": "verdict_absent"}
    except OSError as exc:
        return None, {"reason": "verdict_unreadable", "error": type(exc).__name__}
    try:
        verdict = json.loads(raw)
    except (UnicodeDecodeError, ValueError):
        return None, {"reason": "verdict_malformed"}
    if not isinstance(verdict, dict) or not isinstance(verdict.get("flags"), list):
        return None, {"reason": "verdict_malformed"}
    if verdict.get("schema") != WINDOW_CALIBRATION_VERDICT_SCHEMA:
        return None, {"reason": "verdict_schema_mismatch"}
    try:
        expected = {
            "evidence_sha256": hashlib.sha256(files["instrument_evidence.json"]).hexdigest(),
            "manifest_sha256": hashlib.sha256(files["manifest.json"]).hexdigest(),
            "raw_plist_sha256": hashlib.sha256(files["raw/powermetrics.plist"]).hexdigest(),
            "events_sha256": hashlib.sha256(files["events.jsonl"]).hexdigest(),
        }
    except KeyError as exc:
        return None, {"reason": "capture_file_absent", "file": str(exc.args[0])}
    mismatched = sorted(name for name, digest in expected.items() if verdict.get(name) != digest)
    try:
        estimator = window_calibration_estimator_files_sha256()
    except Exception:  # noqa: BLE001 - an unreadable estimator is a miss
        estimator = None
    if estimator is None or verdict.get("estimator_files_sha256") != estimator:
        mismatched.append("estimator_files_sha256")
    if mismatched:
        return None, {"reason": "digest_mismatch", "fields": mismatched}
    bound = verdict.get("effective_b_fiducial_s")
    if isinstance(bound, bool) or not isinstance(bound, int | float):
        return None, {"reason": "verdict_bound_invalid"}
    try:
        value = float(bound)
    except OverflowError:  # review F6: an integer beyond float range
        return None, {"reason": "verdict_bound_invalid"}
    # widen-only, as verify_stored_evidence_physics returns it
    if not math.isfinite(value) or value < float(stored_bound):
        return None, {"reason": "verdict_bound_invalid"}
    return value, None


def _load_instrument_calibration_attachment(
    directory: Path | None,
    *,
    power_policy: str | None,
    runtime_powermetrics_sha256: str | None = None,
    runtime_power_policy: str | None = None,
    g2a_context: tuple[BenchmarkConfig, Path, Path] | None = None,
    runs_root: Path | None = None,
    config: BenchmarkConfig | None = None,
    hazard: Any = None,
) -> _InstrumentCalibrationAttachment | None:
    """Authenticate a validation directory before a bundle is created.

    ``hazard`` is the HAZARD_PACK flag context (``joulewise.flags.core``);
    ``None`` is the legacy path.  On HAZARD the power-policy label terms and
    an unobserved runtime binary digest become flags, while evidence status,
    the fiducial bound, a present-but-different binary digest and the raw
    physics reproduction stay refusals.
    """

    if directory is None:
        if power_policy is not None:
            raise ValueError("instrument power policy requires a calibration directory")
        return None
    if not isinstance(power_policy, str) or not power_policy.strip():
        raise ValueError(
            "instrument calibration attachment requires --instrument-power-policy"
        )
    root = Path(directory)
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"instrument calibration directory is unavailable: {exc}") from exc
    manifest_path = root / "manifest.json"
    try:
        manifest_raw = manifest_path.read_bytes()
        manifest = json.loads(manifest_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"instrument calibration manifest is unavailable: {exc}") from exc
    artifacts = manifest.get("artifacts") if isinstance(manifest, dict) else None
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version")
        != "joulewise.instrument_validation_manifest.v1"
        or not isinstance(artifacts, dict)
    ):
        raise ValueError("instrument calibration manifest schema is invalid")
    files: dict[str, bytes] = {"manifest.json": manifest_raw}
    for relative, expected_sha in artifacts.items():
        path_value = Path(relative) if isinstance(relative, str) else None
        if (
            path_value is None
            or path_value.is_absolute()
            or ".." in path_value.parts
            or not isinstance(expected_sha, str)
            or len(expected_sha) != 64
        ):
            raise ValueError("instrument calibration artifact descriptor is invalid")
        try:
            candidate = (resolved_root / path_value).resolve(strict=True)
            if resolved_root not in candidate.parents:
                raise ValueError(
                    f"instrument calibration artifact escapes directory: {relative}"
                )
            raw = candidate.read_bytes()
        except OSError as exc:
            raise ValueError(
                f"instrument calibration artifact is unavailable: {relative}"
            ) from exc
        if hashlib.sha256(raw).hexdigest() != expected_sha:
            raise ValueError(
                f"instrument calibration artifact hash mismatch: {relative}"
            )
        files[path_value.as_posix()] = raw
    evidence_raw = files.get("instrument_evidence.json")
    if evidence_raw is None:
        raise ValueError("instrument calibration manifest omits instrument_evidence.json")
    try:
        evidence = json.loads(evidence_raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("instrument calibration evidence is invalid JSON") from exc
    from joulewise.calibration_bracketing import REVISION_FIVE_EPOCH  # noqa: PLC0415

    from joulewise.arm_readiness import LAUNCH_LINEAGE_LOCATOR_BASENAME  # noqa: PLC0415

    bracket_provenance = None
    g2b_provenance = None
    auxiliary_errors: list[str] | None = [] if hazard is not None else None
    locator = Path(runs_root) / LAUNCH_LINEAGE_LOCATOR_BASENAME if runs_root is not None else None
    if locator is not None and (locator.exists() or locator.is_symlink()):
        g2b_provenance = _authenticate_g2b_pre_slot_attachment(
            resolved_root, files, evidence, Path(runs_root), config, hazard=hazard,
            **({"auxiliary_errors": auxiliary_errors} if auxiliary_errors is not None else {}),
        )
    elif g2a_context is not None:
        bracket_provenance = _authenticate_g2a_pre_bracket_attachment(
            resolved_root, files, evidence, *g2a_context
        )
    if isinstance(evidence, dict) and (
        "battery_float" in evidence
        or any(
            isinstance(epoch, dict)
            and all(epoch.get(field) == value for field, value in REVISION_FIVE_EPOCH.items())
            for epoch in (evidence.get("identity_epoch"), evidence.get("bindings"))
        )
    ) and bracket_provenance is None and g2b_provenance is None:
        if auxiliary_errors:
            # HAZARD (PLAN2 row 5): name the cause in the refusal itself.
            raise ValueError(
                "revision_five evidence cannot be attached as instrument calibration "
                f"(auxiliary member match raised {auxiliary_errors[0]})"
            )
        raise ValueError("revision_five evidence cannot be attached as instrument calibration")
    bindings = evidence.get("bindings") if isinstance(evidence, dict) else None
    bound = evidence.get("b_fiducial_s") if isinstance(evidence, dict) else None
    if (
        not isinstance(evidence, dict)
        or evidence.get("status") != "valid"
        or not isinstance(bindings, dict)
        # HAZARD: the label term is a flag below; the other terms are keepers.
        or (hazard is None and bindings.get("power_policy") != power_policy)
        or isinstance(bound, bool)
        or not isinstance(bound, int | float)
        or not math.isfinite(float(bound))
        or float(bound) < 0.0
    ):
        raise ValueError("instrument calibration evidence/power-policy binding is invalid")
    bound_powermetrics_sha256 = bindings.get("powermetrics_sha256")
    # HAZARD: an unobserved digest (None, flagged per member in run_benchmark)
    # skips the comparison; a present digest that differs still refuses.
    if not (hazard is not None and runtime_powermetrics_sha256 is None) and (
        not isinstance(runtime_powermetrics_sha256, str)
        or runtime_powermetrics_sha256 != bound_powermetrics_sha256
    ):
        raise ValueError(
            "instrument calibration powermetrics binding does not match the "
            "runtime-observed executable digest"
        )
    runtime_policy_unverified = (
        not isinstance(runtime_power_policy, str)
        or runtime_power_policy != power_policy
        or runtime_power_policy != bindings.get("power_policy")
    )
    if hazard is not None and (
        runtime_policy_unverified or bindings.get("power_policy") != power_policy
    ):
        from joulewise.flags import core as flags_core  # noqa: PLC0415

        # The reducer re-checks the recorded observation against the bindings
        # and leaves the member's clock anchor unresolved on a mismatch.
        flags_core.emit(
            hazard, "calibration.power_policy_unverified", level="window",
            observed={
                "cli_label": power_policy,
                "recorded_label": bindings.get("power_policy"),
                "runtime_observation": runtime_power_policy,
            },
            legacy_site="joulewise/controller.py:479-507@e6b6a0ce",
            legacy_code="instrument_calibration_power_policy_binding",
        )
    elif runtime_policy_unverified:
        raise ValueError(
            "instrument calibration power-policy binding does not match a "
            "runtime-observed power policy"
        )
    from joulewise.powermetrics_fiducial import (  # noqa: PLC0415
        verify_stored_evidence_physics,
    )

    effective_bound: float | None = None
    refit_cache_miss: dict[str, Any] | None = None
    if hazard is not None:
        # M1: the window verdict (J1) carries the refit of exactly these
        # bytes under exactly this estimator; any miss refits below.
        effective_bound, refit_cache_miss = _window_calibration_verdict_bound(
            resolved_root, files, stored_bound=float(bound)
        )
    if effective_bound is None:
        try:
            effective_bound = verify_stored_evidence_physics(
                evidence,
                files["raw/powermetrics.plist"],
                files["events.jsonl"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                "instrument calibration evidence does not reproduce the raw physics"
            ) from exc
    hazard_fields: dict[str, Any] = {}
    if hazard is not None:
        hazard_fields = {
            "sources": {relative: resolved_root / relative for relative in files},
            # M2: the child reduce reads this instead of a third refit.  The
            # reducer consults it only after its own manifest, evidence, plist
            # and events hash checks of the installed copy.
            "physics_seed": {hashlib.sha256(evidence_raw).hexdigest(): float(effective_bound)},
            "refit_cache_miss": refit_cache_miss,
        }
    return _InstrumentCalibrationAttachment(
        **hazard_fields,
        files=files,
        metadata={
            "artifact_path": "instrument_calibration/instrument_evidence.json",
            "artifact_sha256": hashlib.sha256(evidence_raw).hexdigest(),
            "validation_manifest_path": "instrument_calibration/manifest.json",
            "validation_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "b_fiducial_s": float(bound),
            "verified_effective_b_fiducial_s": effective_bound,
            "bindings": dict(bindings),
            "binding_observations": {
                "powermetrics_sha256": runtime_powermetrics_sha256,
                "power_policy": runtime_power_policy,
            },
            **({"g2a_pre_bracket": bracket_provenance} if bracket_provenance else {}),
            **({"g2b_pre_slot": g2b_provenance} if g2b_provenance else {}),
        },
    )


def _g2b_auxiliary_config_matches(
    config: BenchmarkConfig, context: dict[str, Any], tree: dict[str, Any], repo: Path,
    *, errors: list[str] | None = None,
) -> bool:
    """Match a pinned external campaign member and its stage's runs-root binding.

    GAMMA uses input IDs; ALPHA/BETA embed the manifest descriptor directly.
    Neither directory names nor external artifacts alone confer eligibility.
    The caller has already authenticated the launch and its committed pack.

    ``errors`` (HAZARD, PLAN2 row 5): when given, an exception that makes the
    match False is recorded there as ``"<type>: <text>"`` instead of vanishing.
    """
    from joulewise.arm_readiness import LaunchLineageError  # noqa: PLC0415

    try:
        source, raw = _cli_config_source(config)
        relative = source.relative_to(repo.resolve(strict=True)).as_posix()
    except (LaunchLineageError, OSError, ValueError) as exc:
        if errors is not None:
            errors.append(f"{type(exc).__name__}: {exc}"[:300])
        return False
    digest = hashlib.sha256(raw).hexdigest()
    inputs = tree.get("external_inputs", [])
    if isinstance(inputs, dict):
        inputs = inputs.get("manifests", [])
    if not isinstance(inputs, list) or not isinstance(tree.get("stage_graph"), list):
        return False
    for external in inputs:
        if not isinstance(external, dict) or not isinstance(external.get("members"), list):
            continue
        if not any(isinstance(member, dict) and member.get("path") == relative
                   and member.get("sha256") == digest for member in external["members"]):
            continue
        for stage in tree["stage_graph"]:
            if not isinstance(stage, dict) or stage.get("kind") != "campaign_collection":
                continue
            input_ref = stage.get("input_ref", {})
            if "input_id" in external:
                matches = input_ref == {"kind": "external_input", "input_id": external["input_id"]}
            else:
                matches = isinstance(external.get("manifest"), dict) and stage.get("input") == external["manifest"]
            if not matches:
                continue
            commands = stage.get("launch", {}).get("commands", [])
            for command in commands:
                if command.get("command_kind") != "campaign_collection":
                    continue
                arguments = command.get("argv_template", {}).get("arguments", [])
                for index, argument in enumerate(arguments[:-1]):
                    if (argument == {"kind": "literal", "value": "--runs-dir"}
                            and arguments[index + 1] == {"kind": "binding", "value": context["root_role"]}):
                        return True
    return False


def _authenticate_g2b_pre_slot_attachment(
    directory: Path, files: dict[str, bytes], evidence: Any, runs_root: Path,
    config: BenchmarkConfig | None, *, hazard: Any = None,
    auxiliary_errors: list[str] | None = None,
) -> dict[str, Any] | None:
    """Authenticate the launch lineage and its ordinary finalized pre slot.

    The root-local locator selects this route; it is never an authorization
    by itself. Both claim and bound members use the session named by the
    authenticated consumption/start/settle chain, with completion absent.

    HAZARD (``hazard`` not None): no Git per member (the repository is the
    pack's ``<repo>/configs/campaigns/<pack>`` ancestor, or for any other
    layout one git lookup plus a ``records.pin_ledger`` flag; the ledger pin
    is not compared with HEAD), the ledger's governed-extension shape and a
    non-passing pre-slot battery verdict become window flags.  Every
    session/slot/plan/custody/digest/T1 term stays a refusal, and a battery
    phase whose record names a raw digest must still carry those bytes.
    """
    from joulewise.arm_readiness import (  # noqa: PLC0415
        authenticate_campaign_launch_lineage, _plan_tree, _repo_for_pack,
    )
    from joulewise.calibration_ledger import (  # noqa: PLC0415
        SESSION_KIND_BRACKET, calibration_session_status,
        load_calibration_ledger_snapshot,
    )

    context = authenticate_campaign_launch_lineage(runs_root)
    # A root locator alone cannot authorize the running member. Reuse the
    # writer's marker, CLI-source equality and authenticated pack-inventory
    # checks, or authenticate an external auxiliary against the same plan.
    # Ineligible configs retain ordinary Revision-5 refusal, without G2-a fallback.
    if config is None:
        return None
    try:
        member_lineage = _writer_launch_lineage(runs_root, config)
    except BundleError:
        member_lineage = None
    lineage = context["launch_lineage"]
    pack_root = Path(context["pack_root"])
    if hazard is None:
        repo = _repo_for_pack(pack_root)
    elif (pack_root.parent.name == "campaigns"
            and pack_root.parent.parent.name == "configs"):
        repo = pack_root.parents[2]
    else:
        # Refusal census 2026-10-06: a pack outside <repo>/configs/campaigns
        # is a path-shape fact, not a physical hazard.  Find the repository
        # the legacy way (one git call) and record the layout; the
        # session/slot/plan/custody/digest keepers below still refuse a
        # repository whose ledger does not bind this member.
        from joulewise.flags import core as flags_core  # noqa: PLC0415

        repo = _repo_for_pack(pack_root)
        flags_core.emit(
            hazard, "records.pin_ledger", level="window",
            observed={"kind": "pack_root_layout", "pack_root": str(pack_root),
                      "repository": str(repo)},
            expected={"pack_root": "<repo>/configs/campaigns/<pack>"},
            detail="the pack root is not <repo>/configs/campaigns/<pack>; the repository "
                   "was found with git and the member was collected",
            legacy_site="joulewise/controller.py:923@ba0e0c72e",
            legacy_code="G2-b attachment pack root is not <repo>/configs/campaigns/<pack>",
        )
    tree, _ = _plan_tree(pack_root)
    if member_lineage is None and not _g2b_auxiliary_config_matches(
            config, context, tree, repo,
            **({"errors": auxiliary_errors} if auxiliary_errors is not None else {})):
        if hazard is not None and auxiliary_errors:
            from joulewise.flags import core as flags_core  # noqa: PLC0415

            # The refusal that follows stays; its cause is now on record.
            flags_core.emit(
                hazard, "records.auxiliary_match_raised", level="member",
                run_id=config.run_id, observed={"errors": list(auxiliary_errors)},
                legacy_site="joulewise/controller.py:618@89571045b",
                legacy_code="_g2b_auxiliary_config_matches",
            )
        return None
    plan = tree["plan"]
    plan_path = pack_root / plan["path"]
    ledger_path = repo / "runs/calibration_observation_ledger.jsonl"
    pin_path = repo / "configs/calibration/calibration_ledger_head.json"
    status = calibration_session_status(
        ledger_path, pin_path, session_id=lineage["bracket_session_id"],
        plan_path=plan_path, repo_root=repo, custody_mode="issuing",
        require_committed_pin=hazard is None,
    )
    pre_status = status["slots"].get("pre")
    if (status["session_id"] != lineage["bracket_session_id"]
            or status["plan_id"] != lineage["plan_id"]
            or plan["plan_id"] != lineage["plan_id"]
            or status["plan_sha256"] != plan["actual_sha256"]
            or status["session_kind"] != SESSION_KIND_BRACKET
            or status["session_state"] != "open"
            or not isinstance(pre_status, dict)
            or pre_status.get("finalized") is not True
            or pre_status.get("custody_state") != "complete"
            or Path(pre_status["custody_locator"]).resolve() != directory):
        raise ValueError("G2-b attachment requires its session's finalized pre slot")
    # Session status authenticates the durable reservation. Compare the byte
    # snapshot being installed with the finalization receipt as well: a valid
    # manifest alone cannot bind these bytes to this session.
    snapshot = load_calibration_ledger_snapshot(
        ledger_path, pin_path, repo_root=repo, verify_custody=False, mode="issuing",
        require_committed_pin=hazard is None,
    )
    session = snapshot.bracket_session_by_id[lineage["bracket_session_id"]]
    pre = session.finalized_slots.get("pre")
    governed_extension = snapshot.is_governed_open_bracket_extension
    if ((hazard is None and not governed_extension)
            or session.session_kind != SESSION_KIND_BRACKET or session.state != "open"
            or session.window_id != lineage["window_id"]
            or session.plan_id != status["plan_id"]
            or session.plan_sha256 != status["plan_sha256"]
            or pre is None or pre.disposition != "valid" or pre.is_historical_import
            or Path(pre.custody_locator).resolve() != directory
            or not isinstance(evidence, dict) or evidence.get("validation_id") != pre.attempt_id
            or any(hashlib.sha256(files.get(name, b"")).hexdigest() != digest
                   for name, digest in pre.artifact_sha256.items())
            or any(evidence.get("bindings", {}).get(key) != value
                   for key, value in pre.t1_bindings.items())):
        raise ValueError("G2-b attachment does not match the authenticated finalized pre slot")
    if hazard is not None and not governed_extension:
        from joulewise.flags import core as flags_core  # noqa: PLC0415

        # Ledger integrity is re-checked at harvest; the session/slot/digest
        # binding above stays a refusal.
        flags_core.emit(
            hazard, "records.pin_ledger", level="window",
            observed={"refusal_reasons": sorted(snapshot.refusal_reasons)},
            legacy_site="joulewise/controller.py:655@e6b6a0ce",
            legacy_code="is_governed_open_bracket_extension",
        )
    verdict = battery_float.authenticate_capture(directory, expected={
        "session_id": session.session_id, "slot": "pre", "attempt_id": pre.attempt_id,
    })
    if hazard is None:
        if verdict.status != "pass":
            raise ValueError(f"G2-b pre slot battery {verdict.status}: {'; '.join(verdict.reasons)}")
        # Live capture manifests predate battery artifact entries. Carry the raw
        # pair too, so the installed Revision-5 capture remains independently readable.
        for phase in ("pre", "post"):
            relative = f"raw/battery_float.{phase}.ioreg"
            raw = (directory / relative).read_bytes()
            if hashlib.sha256(raw).hexdigest() != evidence["battery_float"][phase]["raw_stdout_sha256"]:
                raise ValueError("G2-b pre slot battery custody changed during attachment")
            files[relative] = raw
    else:
        if verdict.status != "pass":
            from joulewise.flags import core as flags_core  # noqa: PLC0415

            # The harvest re-derives the pair from the same bytes (confounded:
            # calibration.capture_battery_pair_failed) and joins the continuous
            # battery journal over the capture span.  Members measure their own
            # battery float; this is a fact about the calibration capture.
            flags_core.emit(
                hazard, "calibration.capture_battery_pair_unverified", level="window",
                observed={"slot": "pre", "status": verdict.status,
                          "reasons": list(verdict.reasons[:8])},
                legacy_site="joulewise/controller.py:671-672@e6b6a0ce",
                legacy_code=f"G2-b pre slot battery {verdict.status}",
            )
        # Carry every phase whose record names a raw digest; its bytes must be
        # present and unchanged (custody keeper).  A phase with no record, or
        # a capture with no battery_float block, has nothing to carry.
        block = evidence.get("battery_float") if isinstance(evidence, dict) else None
        for phase in ("pre", "post"):
            record = block.get(phase) if isinstance(block, dict) else None
            expected_raw_sha256 = (
                record.get("raw_stdout_sha256") if isinstance(record, dict) else None
            )
            if not (
                isinstance(expected_raw_sha256, str)
                and len(expected_raw_sha256) == 64
                and all(character in "0123456789abcdef" for character in expected_raw_sha256)
            ):
                continue
            relative = f"raw/battery_float.{phase}.ioreg"
            raw = (directory / relative).read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected_raw_sha256:
                raise ValueError("G2-b pre slot battery custody changed during attachment")
            files[relative] = raw
    return {"session_id": session.session_id, "slot": "pre",
            "plan_id": session.plan_id, "plan_sha256": session.plan_sha256,
            "receipt_digest": pre.receipt_digest,
            "launch_lineage_locator_sha256": context["locator_sha256"]}


def _authenticate_g2a_pre_bracket_attachment(
    directory: Path, files: dict[str, bytes], evidence: Any,
    config: BenchmarkConfig, runs_root: Path, plan_path: Path,
) -> dict[str, Any]:
    """Admit only a registered diagnostic member's ordinary, ledger-bound pre slot.

    C-2's legacy readers remain closed. A derivation observation cannot use
    this path, even after its epoch has an issued acceptance (D-102 clause 2).
    This attachment supplies bindings and the recorded fiducial bound
    b_fiducial_s, which the reducer folds into the member's clock-anchor bound.
    The member's stored clock_anchor.status comes from its own telemetry,
    and harvest still judges the whole bracket.
    """
    from joulewise.calibration_ledger import (  # noqa: PLC0415
        SESSION_KIND_BRACKET, load_calibration_ledger_snapshot,
    )

    repo = Path(__file__).resolve().parents[1]
    raw = plan_path.read_bytes()
    plan = json.loads(raw)
    if (plan.get("schema_version") != "joulewise.g2a_probe_plan.v1"
            or plan.get("status", {}).get("diagnostic") is not True
            or plan.get("status", {}).get("claim_eligible") is not False
            or plan.get("window_id") != os.environ.get("JOULEWISE_NIGHT_PLAN_ID")
            or plan_path.resolve().parent.parent / "runs" != runs_root.resolve()):
        raise ValueError("G2-a pre attachment requires its frozen diagnostic window")
    members = [member for stage in plan["stages"] for member in stage["members"]
               if member["run_id"] == config.to_dict().get("run_id")]
    if len(members) != 1:
        raise ValueError("G2-a pre attachment requires a registered member")
    member = members[0]
    config_path = Path(plan["config_root"]) / member["config_path"]
    config_raw = config_path.read_bytes()
    if (hashlib.sha256(config_raw).hexdigest() != member["config_sha256"]
            or BenchmarkConfig.from_mapping(json.loads(config_raw)).to_dict() != config.to_dict()):
        raise ValueError("G2-a pre attachment member config mismatch")
    ledger_ref, pin_ref = plan["calibration_ledger"], plan["ledger_head_pin"]
    snapshot = load_calibration_ledger_snapshot(
        repo / ledger_ref["path"], repo / pin_ref["path"], repo_root=repo,
        baseline_sequence=ledger_ref["head_sequence"], baseline_digest=ledger_ref["head_digest"],
        require_committed_pin=True, verify_custody=True, mode="issuing",
    )
    session = snapshot.bracket_session_by_id.get(plan["session_id"])
    if (not snapshot.is_governed_open_bracket_extension or session is None
            or session.session_kind != SESSION_KIND_BRACKET or session.state != "open"
            or session.window_id != plan["window_id"] or session.plan_id != plan["plan_id"]
            or session.plan_sha256 != hashlib.sha256(raw).hexdigest()
            or session.evidence_root_id != plan["evidence_root_id"]
            or Path(session.runs_root).resolve() != runs_root.resolve()):
        raise ValueError("G2-a pre attachment requires an authenticated ordinary bracket session")
    pre = session.finalized_slots.get("pre")
    if (pre is None or pre.disposition != "valid" or pre.is_historical_import
            or Path(pre.custody_locator).resolve() != directory
            or not isinstance(evidence, dict) or evidence.get("validation_id") != pre.attempt_id
            or any(hashlib.sha256(files.get(name, b"")).hexdigest() != digest
                   for name, digest in pre.artifact_sha256.items())
            or any(evidence.get("bindings", {}).get(key) != value
                   for key, value in pre.t1_bindings.items())):
        raise ValueError("G2-a pre attachment does not match the finalized pre slot")
    return {"session_id": session.session_id, "slot": "pre",
            "plan_sha256": session.plan_sha256, "receipt_digest": pre.receipt_digest}


def _runtime_power_policy_observation(
    campaign_environment_preflight: object,
) -> str | None:
    """Classify the live campaign snapshot into a canonical power policy.

    A CLI/config label is not an observation.  Only the campaign environment
    snapshot can establish the currently supported ``ac_high_power`` policy;
    missing or contradictory fields leave the binding unverifiable.
    """

    snapshot = (
        campaign_environment_preflight.get("snapshot")
        if isinstance(campaign_environment_preflight, dict)
        else None
    )
    power = snapshot.get("power") if isinstance(snapshot, dict) else None
    if (
        isinstance(snapshot, dict)
        and snapshot.get("power_source") == "AC Power"
        and isinstance(power, dict)
        and power.get("external_connected") is True
        and snapshot.get("low_power_mode") is False
    ):
        return "ac_high_power"
    return None


def _runtime_powermetrics_digest(device_metadata: object) -> str:
    """Return the selected adapter's runtime-observed executable digest."""

    powermetrics = (
        device_metadata.get("powermetrics")
        if isinstance(device_metadata, dict)
        else None
    )
    digest = (
        powermetrics.get("executable_sha256")
        if isinstance(powermetrics, dict)
        else None
    )
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
    ):
        raise ValueError(
            "selected telemetry adapter did not expose a valid runtime-observed "
            "powermetrics executable digest"
        )
    return digest


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
        "calibration_bracketing": {
            "require_bracket": policy.calibration_bracketing.require_bracket,
            "calibration_bracket_max_drift_s": (
                policy.calibration_bracketing.calibration_bracket_max_drift_s
            ),
        },
    }
    if policy.idle_admission_extension is not None:
        extension = policy.idle_admission_extension
        binding["idle_admission_extension"] = {
            "schema_version": extension.schema_version,
            "policy_version": extension.policy_version,
            "claim_bearing": extension.claim_bearing,
            "sha256": extension.sha256(),
        }
    return policy, binding, preflight


# A18 (HAZARD only): idle-admission conditions that say evidence is missing,
# as opposed to the threshold conditions that measure a busy host.
_IDLE_ADMISSION_EVIDENCE_CONDITIONS = frozenset({
    CONDITION_CPU_TELEMETRY_MISSING,
    CONDITION_CPU_TELEMETRY_MALFORMED,
    CONDITION_CPU_SAMPLES_INSUFFICIENT,
    CONDITION_GPU_ADMISSION_UNKNOWN,
})
# A11 (HAZARD only): per-run policy findings that measure the quiet state
# itself.  Every other failed or unknown finding is a guard flag: the battery
# and thermal hazard journals measure power source and thermal directly.
_QUIET_STATE_FINDING_CODES = frozenset({
    "display_not_all_asleep",
    "screensaver_engaged",
    "low_power_mode_enabled",
})


# HAZARD (s2-02): the doctrine's contending-process threshold, used only to
# label an earlier member's live sampler survivor in this member's record.
SURVIVOR_CONTENTION_CPU_PERCENT = 5.0
_SURVIVOR_PS_TIMEOUT_S = 5.0


def _survivor_pids(group_survivors: Any, escaped_candidates: Any) -> list[dict[str, Any]]:
    """Pids (and exact argv where the census recorded one) of census survivors."""

    rows: dict[int, dict[str, Any]] = {}
    for source in (group_survivors, escaped_candidates):
        for entry in source if isinstance(source, list) else []:
            pid = entry.get("pid") if isinstance(entry, dict) else None
            if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 1:
                continue
            row: dict[str, Any] = {"pid": pid}
            argv = entry.get("argv")
            if isinstance(argv, list) and argv and all(isinstance(part, str) for part in argv):
                row["argv"] = [part[:200] for part in argv[:16]]
            rows.setdefault(pid, {}).update(row)
    return [rows[pid] for pid in sorted(rows)][:32]


def _measure_survivor_processes(pids: list[int]) -> dict[int, dict[str, Any]]:
    """Live pids among ``pids`` with their CPU percent and command (``ps``).

    A pid that ``ps`` does not list is gone.  When ``ps`` itself cannot run,
    every pid is reported live with unknown CPU, which records a flag and
    does not refuse.
    """

    import subprocess  # noqa: PLC0415

    try:
        completed = subprocess.run(
            ["/bin/ps", "-o", "pid=,%cpu=,command=", "-p", ",".join(str(pid) for pid in pids)],
            check=False, capture_output=True, text=True, timeout=_SURVIVOR_PS_TIMEOUT_S,
        )
    except (OSError, subprocess.SubprocessError):
        return {pid: {"cpu_percent": None, "command": None} for pid in pids}
    if completed.returncode not in (0, 1):
        return {pid: {"cpu_percent": None, "command": None} for pid in pids}
    live: dict[int, dict[str, Any]] = {}
    for line in completed.stdout.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) < 2:
            continue
        try:
            pid = int(parts[0])
            cpu = float(parts[1])
        except ValueError:
            continue
        if pid in pids:
            live[pid] = {
                "cpu_percent": cpu if math.isfinite(cpu) else None,
                "command": parts[2] if len(parts) > 2 else None,
            }
    return live


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


class _GuardProbe:
    """One guard observation collected on a helper thread (M4, HAZARD only).

    The probe is pure collection (subprocesses and their parsing); the
    observation is recorded on the controller thread after :meth:`join`, so
    the admission record keeps one writer and its phase order.  The sampler
    spawn seam adopts only the thread that entered it
    (``SamplerTeardown.intercept_popen``), so a probe subprocess can never be
    taken for the sampler.
    """

    def __init__(self, collect: Callable[[], dict[str, Any]]) -> None:
        self._result: dict[str, Any] | None = None
        self._error: BaseException | None = None
        self._thread = threading.Thread(
            target=self._run, args=(collect,), name="joulewise-guard-probe", daemon=True
        )
        self._thread.start()

    def _run(self, collect: Callable[[], dict[str, Any]]) -> None:
        try:
            self._result = collect()
        except BaseException as exc:  # noqa: BLE001 - re-raised on the controller thread
            self._error = exc

    def join(self) -> dict[str, Any] | None:
        self._thread.join()
        return self._result

    def raise_error(self) -> None:
        if self._error is not None:
            raise self._error


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
        instrument_calibration: dict[str, Any] | None = None,
        pre_resolved_telemetry: TelemetryAdapter | None = None,
        post_window_sampling_dwell_s: float = 0.0,
        battery_runner: Callable | None = None,
        battery_clock: Clock | None = None,
        *,
        hazard: Any = None,
        calibration_physics_seed: dict[str, float] | None = None,
    ) -> None:
        self._config = config
        # HAZARD_PACK flag context (joulewise.flags.core); None = legacy path.
        self._hazard = hazard
        # M2 (HAZARD only): the attachment's verified calibration bound,
        # seeded into the default reducer's physics cache.
        self._calibration_physics_seed = (
            dict(calibration_physics_seed) if calibration_physics_seed else None
        )
        # A11: environment-guard reasons that no longer stop a HAZARD member,
        # by flag code; emitted once per code at the end of the lifecycle.
        self._hazard_environment: dict[str, list[dict[str, Any]]] = {}
        # The true sampling_stopped stamp once its event is recorded.
        self._sampling_stopped_stamp: ClockStamp | None = None
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
        self._instrument_calibration = (
            dict(instrument_calibration) if instrument_calibration else None
        )
        self._pre_resolved_telemetry = pre_resolved_telemetry
        self._post_window_sampling_dwell_s = post_window_sampling_dwell_s
        self._battery_runner = battery_runner
        self._battery_clock = battery_clock
        self._battery_float: dict[str, Any] = {"pre": None, "post": None}
        self._trace_window_margins: dict[str, float] | None = None
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
        self._sampler_teardown = SamplerTeardown()
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
            if self._hazard is not None:
                self._emit_hazard_environment_flags()
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
        self._observe_battery_float("pre")
        self._stage_idle_baseline()
        self._stage_warmup()
        self._stage_measured_run()
        self._stage_idle_drift_sentinel()
        self._observe_battery_float("post")
        self._stage_cleanup()
        # Current claim reduction consumes the post-run environment/admission
        # record.  Capture it at the lifecycle boundary immediately before
        # metadata is persisted and the pure reducer reads that metadata.
        self._capture_post_run_environment_observation()
        return self._stage_reduce()

    def _observe_battery_float(self, phase: str) -> None:
        if self._config.hardware_target.telemetry_backend == TelemetryBackend.MOCK:
            return
        name = f"battery_float.{phase}.ioreg"
        try:
            stamp = self._battery_stamp()
            probe_kwargs = {
                "runner": (battery_float.run_bundle_probe
                           if self._battery_runner is None else self._battery_runner),
                "wall_time_s": stamp.epoch_s,
                "monotonic_ns": self._battery_monotonic_ns,
                "raw_path": f"raw/{name}", "session_id": self._writer.run_id,
            }
            if phase == "pre":
                record, raw = battery_float.observe(phase="bundle_pre", **probe_kwargs)
            else:
                record, raw = battery_float.observe(phase="bundle_post", **probe_kwargs)
        except Exception as exc:
            self._record_battery_observation_failure(phase, exc)
            return
        self._battery_float[phase] = record
        try:
            self._writer.write_raw(name, raw)
        except Exception as exc:  # observation custody failure cannot abort a member
            record["probe_error"] = True
            record["passed"] = False
            record["reasons"].append(f"battery raw write failed: {type(exc).__name__}: {exc}")
            self._controller_log.append(record["reasons"][-1])

    def _battery_stamp(self) -> ClockStamp:
        if self._battery_clock is None:
            self._battery_clock = SystemClock()
        return _clock_stamp(self._battery_clock)

    def _battery_monotonic_ns(self) -> int:
        return battery_float.monotonic_ns_from_s(self._battery_stamp().monotonic_after_s)

    def _record_battery_observation_failure(self, phase: str, exc: Exception) -> None:
        reason = f"battery {phase} not observed: {type(exc).__name__}: {exc}"
        self._battery_float.setdefault("not_observed", {})[phase] = reason
        # Battery diagnostics must not read the measurement clock, including
        # on the error/logging path.
        self._controller_log.append(reason)

    def _salvage_battery_float_post(self) -> None:
        if self._battery_float["pre"] is not None and self._battery_float["post"] is None:
            # Do not launch a probe if teardown failed and the sampler is live.
            if self._sampling_active or self._sampling_start_in_progress:
                reason = "battery post not observed: sampler teardown incomplete"
                self._battery_float.setdefault("not_observed", {})["post"] = reason
                self._controller_log.append(reason)
                return
            self._observe_battery_float("post")

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
        if self._pre_resolved_telemetry is not None:
            telemetry, failure = self._pre_resolved_telemetry, None
        else:
            telemetry, failure = self._registry.resolve_telemetry(
                self._config, self._clock
            )
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
        if self._hazard is not None:
            # s2-02: earlier members' sampler survivors, measured before the
            # settle so the ps probe never overlaps an idle capture.
            self._check_carried_sampler_survivors()
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
            # Preserve the exact snapshot that licensed admission.  The live
            # environment object later gains post-run observations, so its
            # eventual metadata representation is not the immutable input to
            # this decision.  Current strict consumers recompute both the
            # snapshot digest and the policy result from this embedded copy.
            per_run_evaluation["snapshot"] = _jsonable(
                self._environment if isinstance(self._environment, dict) else {}
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
            reference_provenance_present = bool(
                self._campaign_policy_binding
                and per_run_evaluation.get("snapshot_sha256")
                and isinstance(preflight_evaluation, dict)
                and preflight_evaluation.get("snapshot_sha256")
            )
            if self._hazard is not None:
                # HAZARD (PLAN2 s2-01): one stage-start reading must not decide
                # every member.  The member's own per-run evaluation (same
                # evaluator and guard policy, taken just before its idle
                # admission) decides.  The stage preflight stays recorded as
                # data in metadata.extra.campaign_environment_preflight.
                critical_environment_passed = per_run_evaluation.get("eligible") is True
                reference_provenance_present = bool(
                    self._campaign_policy_binding
                    and per_run_evaluation.get("snapshot_sha256")
                )
            self._environment_admission = {
                "schema_version": "joulewise.environment_admission.v1",
                "policy_version": self._campaign_policy.policy_version,
                "on_fail": admission.on_fail.value,
                "attempts": attempts,
                "per_run_environment_evaluation": per_run_evaluation,
                "critical_environment_passed": critical_environment_passed,
                "reference_provenance_present": reference_provenance_present,
                "decision": None,
                "claim_reason": None,
            }
            extension = self._campaign_policy.idle_admission_extension
            if extension is not None:
                self._environment_admission["idle_admission_extension"] = {
                    "schema_version": extension.schema_version,
                    "policy_version": extension.policy_version,
                    "claim_bearing": extension.claim_bearing,
                    "sha256": extension.sha256(),
                }
            # M4 (HAZARD, PLAN2 t1-07 safe variant): when the admission sampler
            # is started below, the before_attempt_1 guard probes run during
            # its start instead of before it.  The idle slice begins only at
            # the first frame completed after measure_idle is called, so the
            # probes still never overlap an idle capture.  On the legacy path
            # (and without an admission sampler) they run here, as before.
            probe_during_sampler_start = (
                self._hazard is not None
                and callable(
                    getattr(self._telemetry, "begin_admission_window_sampling", None)
                )
            )
            if not probe_during_sampler_start:
                observation = self._admission_guard_observation("before_attempt_1")
                environment_reason = self._admission_environment_failure(observation)
                if environment_reason is not None:
                    if self._hazard is not None:
                        self._record_hazard_guard_observation(
                            observation, environment_reason
                        )
                    else:
                        self._environment_admission.update(
                            {"decision": "abort", "failure": environment_reason}
                        )
                        raise _StageFailure(
                            "idle_baseline",
                            FailureReason.UNKNOWN_ERROR,
                            environment_reason,
                        )
            if per_run_evaluation.get("eligible") is not True and override is None:
                reason = "critical per-run environment policy did not pass"
                if self._hazard is not None:
                    self._record_hazard_environment_evaluation(per_run_evaluation, reason)
                else:
                    self._environment_admission.update(
                        {"decision": "abort", "failure": reason}
                    )
                    raise _StageFailure(
                        "idle_baseline", FailureReason.UNKNOWN_ERROR, reason
                    )

        if admission is not None and admission.enabled:
            begin_sampling = getattr(
                self._telemetry, "begin_admission_window_sampling", None
            )
            if callable(begin_sampling):
                probe = (
                    _GuardProbe(self._guard_observation_payload)
                    if self._hazard is not None
                    else None
                )
                self._sampling_start_in_progress = True
                try:
                    result = self._start_telemetry_with_parent_adoption(begin_sampling)
                except BaseException:
                    # Review F2: the probe's own work (subprocesses with
                    # command timeouts, then parsing) must end before this
                    # member's failure path returns, so it can never run on
                    # into a later capture.  Its observation is not recorded;
                    # the start's exception stays authoritative.
                    if probe is not None:
                        probe.join()
                    raise
                if probe is not None:
                    observation = probe.join()
                    probe.raise_error()
                    observation = self._admission_guard_observation(
                        "before_attempt_1", collected=observation
                    )
                    environment_reason = self._admission_environment_failure(observation)
                    if environment_reason is not None:
                        self._record_hazard_guard_observation(
                            observation, environment_reason
                        )
                self._check(
                    result,
                    "idle_baseline",
                    "telemetry admission-window sampling failed",
                )

        self._baseline = self._measure_idle_admission_attempt(1, attempts)
        if admission is not None and admission.enabled:
            self._enforce_post_capture_admission_guard(1)
            if not attempts[-1]["admitted"]:
                if admission.retry_backoff_s > 0:
                    assert self._environment_admission is not None
                    backoff_start_s = self._clock.now()
                    self._clock.sleep(admission.retry_backoff_s)
                    self._environment_admission["retry_backoff"] = {
                        "requested_s": admission.retry_backoff_s,
                        "start_s": backoff_start_s,
                        "end_s": self._clock.now(),
                    }
                observation = self._admission_guard_observation("before_attempt_2")
                environment_reason = self._admission_environment_failure(observation)
                if environment_reason is not None and self._hazard is not None:
                    self._record_hazard_guard_observation(observation, environment_reason)
                elif environment_reason is not None:
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
            if attempts[-1]["admitted"]:
                final_attempt = attempts[-1].get("attempt")
                promote_attempt = getattr(
                    self._telemetry, "promote_idle_admission_attempt", None
                )
                if (
                    isinstance(final_attempt, int)
                    and final_attempt > 1
                    and callable(promote_attempt)
                ):
                    promote_attempt(
                        run_id=self._context.run_id,
                        attempt=final_attempt,
                        context=self._context,
                    )
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
        attempt_start_s = self._clock.now()
        baseline = self._telemetry.measure_idle(self._config, self._context)
        attempt_end_s = self._clock.now()
        self._capture_adapter_alignments()
        self._capture_adapter_metadata()
        if self._campaign_policy is not None:
            gpu_admitted: bool | None = baseline.idle_window_suspect is False
            if (
                self._hazard is not None
                and self._environment_admission is not None
                and baseline.idle_window_suspect is None
            ):
                # HAZARD keeps GPU admission tri-state: an unknown GPU idle
                # window is missing evidence, not the threshold condition.
                gpu_admitted = None
            row: dict[str, Any] = {
                "attempt": attempt,
                "start_s": attempt_start_s,
                "end_s": attempt_end_s,
                "baseline": _jsonable(asdict(baseline)),
                "admitted": gpu_admitted is True,
            }
            extension = self._campaign_policy.idle_admission_extension
            if extension is not None:
                records = _adapter_idle_admission_records(
                    self._telemetry,
                    run_id=self._context.run_id,
                    attempt=attempt,
                )
                cpu_admission = evaluate_cpu_idle_admission(
                    records,
                    extension.cpu_criteria,
                    gpu_admitted=gpu_admitted,
                )
                cpu_enforced = records is not None or not isinstance(
                    self._clock, FakeClock
                )
                row.update(
                    {
                        "gpu_admitted": gpu_admitted,
                        "cpu_admission": cpu_admission,
                        "cpu_admission_enforced": cpu_enforced,
                        "admitted": (
                            cpu_admission["admitted"]
                            if cpu_enforced
                            else gpu_admitted is True
                        ),
                    }
                )
                if (
                    self._hazard is not None
                    and self._environment_admission is not None
                    and cpu_enforced
                ):
                    self._hazard_admit_on_missing_evidence(row, cpu_admission)
            attempts.append(row)
        return baseline

    def _hazard_admit_on_missing_evidence(
        self, row: dict[str, Any], cpu_admission: dict[str, Any]
    ) -> None:
        """A18: admit when only evidence conditions failed; flag the member.

        The recorded ``cpu_admission`` stays the evaluator's own output (it
        says the admission did not pass); only the controller's decision to
        proceed changes.  Any threshold condition keeps the row not admitted,
        so retry and abort stay.  A baseline whose CPU quietness is
        unmeasured never serves as a cooldown reference: its
        ``reference_provenance_present`` is recorded false, which every
        reference-eligibility reader already refuses.
        """

        conditions = cpu_admission.get("conditions")
        if (
            row.get("admitted") is True
            or not isinstance(conditions, list)
            or not conditions
            or not set(conditions) <= _IDLE_ADMISSION_EVIDENCE_CONDITIONS
        ):
            return
        row["admitted"] = True
        if self._environment_admission is not None:
            self._environment_admission["reference_provenance_present"] = False
        from joulewise.flags import core as flags_core  # noqa: PLC0415

        flags_core.emit(
            self._hazard, "member.idle_admission_telemetry_missing", level="member",
            run_id=self._writer.run_id,
            observed={
                "attempt": row.get("attempt"),
                "conditions": sorted(str(condition) for condition in conditions),
                "sample_count": cpu_admission.get("sample_count"),
            },
            legacy_site="joulewise/controller.py:1381-1392@e6b6a0ce",
            legacy_code="idle environment admission failed after one retry",
        )

    def _admission_guard_observation(
        self, phase: str, *, collected: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        observation = (
            collected if collected is not None else self._guard_observation_payload()
        )
        observation["phase"] = phase
        if self._environment_admission is not None:
            self._environment_admission.setdefault("guard_observations", []).append(
                observation
            )
        return observation

    def _guard_observation_payload(self) -> dict[str, Any]:
        """Collect one guard observation; no state is touched (thread-safe)."""

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
            observation = collect_environment_guard_observation(
                include_adapter_power=True
            )
            observation["capture_skipped"] = False
        return observation

    def _enforce_post_capture_admission_guard(self, attempt: int) -> None:
        observation = self._admission_guard_observation(f"after_attempt_{attempt}")
        environment_reason = self._admission_environment_failure(observation)
        if environment_reason is None:
            return
        if self._hazard is not None:
            self._record_hazard_guard_observation(observation, environment_reason)
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
        return environment_observation_failure(observation)

    # A11 (HAZARD only): an environment-guard reason is recorded, not a stop.
    # The admission record and its guard observations are written as on the
    # legacy path; the reducer's claim barrier still reads them.  ``decision``
    # keeps its meaning (admitted iff the final attempt was admitted).  A
    # measured quiet-state violation also records
    # ``critical_environment_passed`` false, so that baseline never becomes a
    # cooldown reference; an unknown guard state alone does not (PLAN2 s2-01:
    # one DISCLOSE guard flag must not exclude the next member).

    def _record_hazard_quiet_state_violation(self) -> None:
        if self._environment_admission is not None:
            self._environment_admission["critical_environment_passed"] = False

    def _record_hazard_guard_observation(
        self, observation: Any, reason: str
    ) -> None:
        source = observation if isinstance(observation, dict) else {}
        phase = source.get("phase")
        display = source.get("display_power_state")
        screensaver = source.get("screensaver_engaged")
        errors = source.get("errors")
        error_fields = sorted(str(key) for key in errors) if isinstance(errors, dict) else []
        quiet: list[dict[str, Any]] = []
        guard: list[dict[str, Any]] = []
        if display == "any_awake":
            quiet.append({"phase": phase, "field": "display_power_state", "value": display})
        elif display != "all_asleep":
            guard.append({"phase": phase, "field": "display_power_state", "status": "unknown"})
        if screensaver is True:
            quiet.append({"phase": phase, "field": "screensaver_engaged", "value": True})
        elif screensaver is not False:
            guard.append({"phase": phase, "field": "screensaver_engaged", "status": "unknown"})
        if not isinstance(observation, dict):
            guard.append({"phase": phase, "field": "observation", "status": "missing"})
        if error_fields:
            guard.append({"phase": phase, "field": "errors", "keys": error_fields})
        if not quiet and not guard:
            guard.append({"phase": phase, "field": "observation", "reason": reason[:200]})
        if quiet:
            self._record_hazard_quiet_state_violation()
            self._hazard_environment.setdefault(
                "env.member_quiet_state_violated", []).extend(quiet)
        if guard:
            self._hazard_environment.setdefault(
                "env.member_guard_flagged", []).extend(guard)

    def _record_hazard_environment_evaluation(
        self, evaluation: Any, reason: str
    ) -> None:
        findings = evaluation.get("findings") if isinstance(evaluation, dict) else None
        quiet: list[dict[str, Any]] = []
        guard: list[dict[str, Any]] = []
        for finding in findings if isinstance(findings, list) else []:
            if not isinstance(finding, dict):
                continue
            status = finding.get("status")
            if status not in {"fail", "unknown"}:
                continue
            entry = {"phase": "per_run_evaluation", "field": finding.get("field"),
                     "code": finding.get("code"), "status": status}
            if status == "fail" and finding.get("code") in _QUIET_STATE_FINDING_CODES:
                quiet.append(entry)
            else:
                guard.append(entry)
        if not quiet and not guard:
            guard.append({"phase": "per_run_evaluation", "field": None,
                          "reason": reason[:200]})
        if quiet:
            self._record_hazard_quiet_state_violation()
            self._hazard_environment.setdefault(
                "env.member_quiet_state_violated", []).extend(quiet)
        if guard:
            self._hazard_environment.setdefault(
                "env.member_guard_flagged", []).extend(guard)

    def _emit_hazard_environment_flags(self) -> None:
        if not self._hazard_environment:
            return
        from joulewise.flags import core as flags_core  # noqa: PLC0415

        for code in sorted(self._hazard_environment):
            flags_core.emit(
                self._hazard, code, level="member", run_id=self._writer.run_id,
                observed={"findings": self._hazard_environment[code]},
                legacy_site="joulewise/controller.py:1306-1322,1350-1361,1502-1513@e6b6a0ce",
                legacy_code="environment_admission_abort",
            )
        self._hazard_environment = {}

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
            start_result = self._start_telemetry_with_parent_adoption(
                self._telemetry.start_sampling
            )
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
        if self._post_window_sampling_dwell_s > 0.0:
            self._clock.sleep(self._post_window_sampling_dwell_s)
        if self._hazard is not None:
            # HAZARD (PLAN2 s2-02): after the dwell and before the stop, keep
            # the completed run's result and record its events and the true
            # stop marker, so a raising stop or census cannot lose the token
            # timeline, the outputs or the window bound.  The window and its
            # post-window tail are untouched; the stable flush-sort still
            # brackets the runtime events.
            self._runtime_result = runtime_result
            try:
                if not self._is_axi_run():
                    self._events.extend(runtime_result.events)
                elif runtime_result.axi_result is not None:
                    self._events.extend(
                        self._axi_request_events(runtime_result.axi_result)
                    )
            finally:
                # Even if the request events cannot be built, the failure
                # path then stops the sampler with this true stamp.
                self._append_sampling_stopped(sampling_stopped_stamp)
        self._capture_adapter_alignments()
        self._stop_sampling_once(sampling_stopped_stamp)
        if self._hazard is not None:
            # The stop returned: it stays claimed whatever the census said.
            self._sampling_active = False
        self._record_trace_window_margins(
            sampling_started_stamp, sampling_stopped_stamp
        )
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
            if self._hazard is None:
                self._events.extend(self._axi_request_events(runtime_result.axi_result))
        elif self._hazard is None:
            self._events.extend(runtime_result.events)
        if self._hazard is None:
            self._append_sampling_stopped(sampling_stopped_stamp)
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

    def _append_sampling_stopped(self, stamp: ClockStamp) -> None:
        self._events.append(
            RuntimeEvent(
                timestamp_s=stamp.epoch_s,
                event_type="sampling_stopped",
                phase="measured_run",
                message="measured window stopped; telemetry tail retained outside window",
                metadata={},
            )
        )
        # HAZARD: the true stop marker is recorded; no second one is written.
        self._sampling_stopped_stamp = stamp

    def _stage_idle_drift_sentinel(self) -> None:
        """Collect the short post-run idle sentinel outside the measured window."""

        if not isinstance(self._telemetry, IdleDriftEvidenceProvider):
            if self._config.hardware_target.telemetry_backend != TelemetryBackend.MOCK:
                self._begin_stage("idle_drift_sentinel")
                self._complete_stage("idle_drift_sentinel", {"status": "unavailable"})
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
                "telemetry_backend": self._telemetry.name,
                "capture_pipeline_absent": True,
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
                    if self._hazard is None:
                        raise _StageFailure(
                            "cleanup",
                            FailureReason.CLEANUP_FAILED,
                            result.message or "worker-started runtime process survived cleanup",
                        )
                    # A17 (HAZARD): the measured window is complete.  Record
                    # it; no extra signals (the adapter owns its process
                    # identity check).  The next member's contention is
                    # measured by the monitor journal and its idle admission.
                    self._emit_hazard_teardown_survivors(
                        kind="runtime", status="cleanup_failed",
                        group_survivors=None, escaped_candidates=None,
                        message=result.message,
                        legacy_site="joulewise/controller.py:1734-1740@e6b6a0ce",
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
        self._complete_stage("cleanup", metadata)

    def _stage_reduce(self) -> SummaryMetrics:
        self._begin_stage("reduce")
        self._write_metadata()
        # The reducer is a pure function over on-disk artifacts (D-002), so
        # events.jsonl must hold every measurement event (the measured_run
        # window and the token events) BEFORE it runs. _flush_events writes
        # them now; only run_finalized is still appended later by finalize().
        self._flush_events()
        if self._reducer is None and self._calibration_physics_seed:
            # M2: the reducer runs every hash check of the installed copy, then
            # takes the bound this member already verified instead of a refit.
            summary = reduce_module.reduce_bundle(
                self._writer.path,
                _instrument_calibration_physics_cache=dict(
                    self._calibration_physics_seed
                ),
            )
        else:
            reducer = (
                self._reducer if self._reducer is not None
                else reduce_module.reduce_bundle
            )
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
        self._attempt_salvage_step("battery_float_post", self._salvage_battery_float_post)
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
            ("battery_float_post", self._salvage_battery_float_post),
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
        if self._hazard is not None:
            self._emit_hazard_environment_flags()  # never raises (flags.core.emit)
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
        if self._hazard is not None and self._sampling_stopped_stamp is not None:
            # HAZARD (s2-02): the true marker is already recorded; retry the
            # stop with that stamp and write no second sampling_stopped.
            try:
                self._stop_sampling_once(self._sampling_stopped_stamp)
                self._capture_adapter_alignments()
                self._sampling_active = False
                self._sampling_start_in_progress = False
            except Exception:  # noqa: BLE001 - evidence salvage must not mask the failure
                self._log(
                    self._controller_log,
                    "best-effort stop_sampling raised after failure:",
                )
                self._log(self._controller_log, traceback.format_exc())
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
                    required_post_window_tail_s=self._post_window_sampling_dwell_s,
                )
                if self._hazard is not None and self._hazard_keeps_stop_evidence():
                    pass
                else:
                    self._samples = result.samples
                    self._uncertainty_evidence = dict(result.uncertainty_evidence)
            else:
                samples = self._telemetry.stop_sampling(self._config, self._context)
                if self._hazard is None or not self._hazard_keeps_stop_evidence():
                    self._samples = samples
        except BaseException:
            self._attach_sampler_teardown_custody()
            # Ordinary failures remain retryable by the failure-salvage path.
            self._sampling_stop_claimed = False
            raise
        if self._telemetry.name == "powermetrics":
            self._attach_sampler_teardown_custody()
            teardown = self._sampler_teardown.report
            if self._sampler_teardown.spawned and (
                not isinstance(teardown, dict) or teardown.get("status") != "clean"
            ):
                if self._hazard is not None:
                    # A17 (HAZARD): custody is attached above; the window is
                    # complete.  No further signals: the teardown already
                    # escalated while the leader was unreaped and refuses group
                    # signals after reaping.
                    # The survivor pids ride in the flag, so the next member's
                    # contention check can measure them (s2-02).
                    report = teardown if isinstance(teardown, dict) else {}
                    survivors = report.get("group_survivors")
                    escaped = report.get("escaped_candidates")
                    self._emit_hazard_teardown_survivors(
                        kind="sampler",
                        status=report.get("status") if report else "report_missing",
                        group_survivors=len(survivors) if isinstance(survivors, list) else None,
                        escaped_candidates=len(escaped) if isinstance(escaped, list) else None,
                        message=None,
                        legacy_site="joulewise/controller.py:1957-1968@e6b6a0ce",
                        pids=_survivor_pids(survivors, escaped),
                    )
                    return True
                self._sampling_stop_claimed = False
                raise _StageFailure(
                    "measured_run",
                    FailureReason.UNKNOWN_ERROR,
                    "powermetrics process-group teardown census reported contamination",
                )
        return True

    def _start_telemetry_with_parent_adoption(
        self,
        start: Callable[[BenchmarkConfig, RunContext | None], AdapterResult],
    ) -> AdapterResult:
        """Run the existing adapter start under the parent-owned spawn seam."""

        assert self._telemetry is not None
        if self._telemetry.name != "powermetrics":
            return start(self._config, self._context)
        if self._hazard is None:
            with self._sampler_teardown.intercept_popen():
                return start(self._config, self._context)
        # HAZARD (M4): the guard probe may spawn concurrently on its helper
        # thread; only this (the start call's) thread can be adopted.
        with self._sampler_teardown.intercept_popen(owner_thread_only=True):
            return start(self._config, self._context)

    def _emit_hazard_teardown_survivors(
        self,
        *,
        kind: str,
        status: Any,
        group_survivors: int | None,
        escaped_candidates: int | None,
        message: str | None,
        legacy_site: str,
        pids: list[dict[str, Any]] | None = None,
    ) -> None:
        from joulewise.flags import core as flags_core  # noqa: PLC0415

        observed: dict[str, Any] = {
            "kind": kind,
            "status": status,
            "group_survivors": group_survivors,
            "escaped_candidates": escaped_candidates,
        }
        if pids:
            observed["pids"] = pids
        if message:
            observed["message"] = str(message)[:200]
        flags_core.emit(
            self._hazard, "teardown.survivors", level="member",
            run_id=self._writer.run_id, observed=observed,
            legacy_site=legacy_site,
            legacy_code=(
                "powermetrics process-group teardown census reported contamination"
                if kind == "sampler" else FailureReason.CLEANUP_FAILED.value
            ),
        )

    def _hazard_keeps_stop_evidence(self) -> bool:
        """HAZARD (s2-02): a later stop never overwrites recorded evidence.

        True when samples or a clock-anchor derivation are already held,
        whatever the new result holds; the first recorded stop evidence is
        then kept whole and the new result is discarded.
        """

        held_anchor = (
            isinstance(self._uncertainty_evidence, dict)
            and bool(self._uncertainty_evidence.get("clock_anchor"))
        )
        if not self._samples and not held_anchor:
            return False
        self._log(
            self._controller_log,
            "repeated stop result discarded; recorded samples and anchor evidence kept",
        )
        return True

    def _check_carried_sampler_survivors(self) -> None:
        """HAZARD (s2-02): measure earlier members' sampler survivors; record only.

        Earlier members of this window record census survivors in their
        ``teardown.survivors`` flags.  Before this member's settle and idle
        admission, each carried pid is measured with ``ps``.  A survivor that
        is still alive (same pid and, when recorded, the same command) is
        recorded on this member as ``teardown.survivors`` (kind
        ``carried_over``) with its CPU percent, ``contending`` above the
        doctrine's 5 % threshold.  It never refuses and sends no signal: the
        monitor's contention journal (``contention.request_overlap``,
        EXCLUDE_MEMBER) and this member's idle admission measure the
        contention itself.  Never raises.
        """

        try:
            self._measure_carried_sampler_survivors()
        except Exception:  # noqa: BLE001 - a diagnostic never stops collection
            self._log(self._controller_log, "carried sampler survivor check raised:")
            self._log(self._controller_log, traceback.format_exc())

    def _measure_carried_sampler_survivors(self) -> None:
        path = getattr(self._hazard, "path", None)
        carried: dict[int, dict[str, Any]] = {}
        try:
            lines = path.read_bytes().splitlines() if path is not None else []
        except OSError:
            lines = []
        for line in lines:
            try:
                flag = json.loads(line)
            except ValueError:
                continue
            if not isinstance(flag, dict) or flag.get("code") != "teardown.survivors":
                continue
            scope = flag.get("scope")
            if isinstance(scope, dict) and scope.get("run_id") == self._writer.run_id:
                continue
            observed = flag.get("observed")
            value = observed.get("value", observed) if isinstance(observed, dict) else None
            for entry in value.get("pids", []) if isinstance(value, dict) else []:
                pid = entry.get("pid") if isinstance(entry, dict) else None
                if isinstance(pid, int) and not isinstance(pid, bool) and pid > 1:
                    carried[pid] = entry
        if not carried:
            return
        live = _measure_survivor_processes(sorted(carried))
        alive: list[dict[str, Any]] = []
        contending: list[dict[str, Any]] = []
        for pid, row in sorted(live.items()):
            argv = carried[pid].get("argv")
            if isinstance(argv, list) and argv and row.get("command") is not None:
                if not str(row["command"]).startswith(str(argv[0])):
                    continue  # the pid now names another process
            entry = {"pid": pid, "cpu_percent": row.get("cpu_percent")}
            alive.append(entry)
            cpu = row.get("cpu_percent")
            if isinstance(cpu, float) and cpu > SURVIVOR_CONTENTION_CPU_PERCENT:
                contending.append(entry)
        if alive:
            self._emit_hazard_teardown_survivors(
                kind="carried_over", status="alive" if not contending else "contending",
                group_survivors=None, escaped_candidates=None, message=None,
                legacy_site="joulewise/controller.py:1957-1968@e6b6a0ce",
                pids=alive,
            )

    def _attach_sampler_teardown_custody(self) -> None:
        """Persist sampler custody evidence for every powermetrics-shaped run.

        A mock pipeline may legitimately avoid a sampler spawn, while this
        controller cannot distinguish that case from a silently unmatched real
        spawn.  Real-window enforcement that custody is engaged *and* clean
        therefore belongs to the scheduler-gate layer and its activation-gates
        register; non-engagement remains explicit here rather than masquerading
        as a clean census.
        """

        if self._telemetry is None or self._telemetry.name != "powermetrics":
            return
        teardown = self._sampler_teardown.report
        if teardown is None:
            teardown = self._sampler_teardown.teardown()
        if self._uncertainty_evidence is None:
            self._uncertainty_evidence = {}
        self._uncertainty_evidence["process_group_teardown"] = dict(teardown)

    def _record_trace_window_margins(
        self,
        sampling_started_stamp: ClockStamp,
        sampling_stopped_stamp: ClockStamp,
    ) -> None:
        """Record achieved trace support outside the measured window."""

        if not self._samples:
            return
        support_starts = [
            sample.interval_start_s
            if sample.interval_start_s is not None
            else sample.timestamp_s
            for sample in self._samples
        ]
        support_ends = [
            sample.interval_end_s
            if sample.interval_end_s is not None
            else sample.timestamp_s
            for sample in self._samples
        ]
        self._trace_window_margins = {
            "requested_post_window_dwell_s": self._post_window_sampling_dwell_s,
            "achieved_pre_window_margin_s": (
                sampling_started_stamp.epoch_s - min(support_starts)
            ),
            "achieved_post_window_margin_s": (
                max(support_ends) - sampling_stopped_stamp.epoch_s
            ),
        }

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
        if self._config.hardware_target.telemetry_backend == TelemetryBackend.MOCK:
            extra["battery_float"] = {"pre": None, "post": None, "not_applicable": "mock"}
        elif self._battery_float["pre"] is None and "not_observed" not in self._battery_float:
            extra["battery_float"] = {"pre": None, "post": None, "not_reached": self._current_stage}
        else:
            extra["battery_float"] = dict(self._battery_float)
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
        # The canonical serializer omits the identity pins when both are
        # null; metadata must match it byte-for-byte or the analysis loader's
        # realized-identity equality refuses every unpinned bundle.
        extra["model"] = dict(self._config.to_dict()["model"])
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
        if self._instrument_calibration is not None:
            extra["instrument_calibration"] = self._instrument_calibration
        if self._trace_window_margins is not None:
            extra["trace_window_margins"] = self._trace_window_margins
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
        # Adapter continuity must bracket the workload.  In particular, a
        # renegotiation during the final member is invisible without this
        # post-workload power observation.
        observation = collect_environment_guard_observation(
            include_adapter_power=True
        )
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
        metadata = None
        if name == "idle_baseline" and self._config.hardware_target.telemetry_backend != TelemetryBackend.MOCK:
            metadata = self._battery_span_metadata(name)
        self._buffer_event("stage_started", name, f"stage {name} started", metadata)

    def _complete_stage(self, name: str, metadata: dict[str, Any] | None = None) -> None:
        if name == "idle_drift_sentinel" and self._config.hardware_target.telemetry_backend != TelemetryBackend.MOCK:
            metadata = dict(metadata or {})
            metadata.update(self._battery_span_metadata(name))
        self._buffer_event("stage_completed", name, f"stage {name} completed", metadata)

    def _battery_span_metadata(self, stage: str) -> dict[str, Any]:
        try:
            return {"monotonic_ns": self._battery_monotonic_ns()}
        except Exception as exc:
            self._record_battery_observation_failure(stage, exc)
            return {"monotonic_ns": None}

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
        coverage_rounding_s = 0.0
        retained_start_s: float | None = None
        for capture_start, evidence_start, evidence_end, value in readings:
            clipped_start = max(evidence_start, cutoff)
            overlap_s = max(0.0, evidence_end - clipped_start)
            weighted_sum += overlap_s * value
            coverage_s += overlap_s
            if overlap_s > 0.0:
                coverage_rounding_s += (
                    math.ulp(evidence_end) + math.ulp(clipped_start)
                )
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
        span_complete = window_span_s + 1e-6 >= selected.sustained_window_s
        coverage_slack_s = max(
            1e-6, coverage_rounding_s + math.ulp(coverage_s)
        )
        coverage_complete = coverage_s + coverage_slack_s >= required_coverage_s
        window_complete = span_complete and coverage_complete
        power_recovered = (
            rolling_mean is not None and rolling_mean <= effective_upper_w
        )
        release_criteria_met = bool(
            window_complete
            and power_recovered
            and (thermal_nominal or not selected.require_thermal_nominal)
        )
        cap_hit = waited_s >= selected.cap_s
        release_criteria_met_late = cap_hit and release_criteria_met
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
                "release": release_criteria_met and not cap_hit,
                "release_criteria_met_late": release_criteria_met_late,
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
        if cap_hit or release_criteria_met:
            disposition = cooldown_disposition_from_raw(trace)
            if disposition == "cap_hit":
                return {
                    "result": "cap_hit",
                    **common,
                    "_trace": trace,
                }
            if disposition == "recovered":
                return {
                    "result": "recovered",
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


def _adapter_idle_admission_records(
    adapter: Any,
    *,
    run_id: str,
    attempt: int,
) -> list[dict[str, Any]] | None:
    """Read the just-captured rich idle rows through an optional adapter seam.

    Admission runs before workload invocation, so the controller must consume
    in-memory evidence rather than re-opening the derived bundle artifact.
    Adapters without the seam yield missing telemetry, which the production
    extension fails closed and the exploratory extension labels/flags.
    """

    if adapter is None:
        return None
    getter = getattr(adapter, "idle_admission_records", None)
    if not callable(getter):
        return None
    try:
        records = getter(run_id=run_id, attempt=attempt)
    except Exception:  # noqa: BLE001 - policy evaluator owns fail-closed mapping.
        return None
    if not isinstance(records, list):
        return None
    return [dict(record) if isinstance(record, dict) else record for record in records]


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
    frozen_cooldown_anchor: dict[str, Any] | None = None,
    instrument_calibration_dir: Path | None = None,
    instrument_power_policy: str | None = None,
    post_window_sampling_dwell_s: float | None = None,
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
    following rep's ``measurement_quality``. A campaign-owned clean anchor may
    be supplied explicitly; the experiment takes an immutable child copy and
    never replaces it from repetition outcomes.
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
    frozen_anchor = deepcopy(frozen_cooldown_anchor)
    if frozen_anchor is not None:
        expected_policy_sha256 = None
        if campaign_policy is not None:
            expected_policy_sha256 = (
                policy_binding.get("sha256")
                if isinstance(policy_binding, dict)
                and isinstance(policy_binding.get("sha256"), str)
                else ""
            )
        anchor_eligibility = cooldown_anchor_eligibility(
            frozen_anchor,
            expected_policy_sha256,
        )
        if not anchor_eligibility["eligible"]:
            verdict_path = _write_cooldown_anchor_rejection(
                runs_root,
                manifest,
                frozen_anchor,
                anchor_eligibility,
                boundary="controller_policy_binding",
                policy_sha256=expected_policy_sha256,
                observed_at_s=clock.now(),
            )
            raise SchemaError(
                "frozen cooldown anchor rejected fail-closed: "
                + ", ".join(anchor_eligibility["reasons"])
                + f"; verdict={verdict_path}"
            )
        manifest["cooldown_anchor"] = frozen_anchor

    results: list[tuple[Path, SummaryMetrics]] = []
    manifest_path: Path | None = None
    # Pending cap-hit recorded against the NEXT rep's run_benchmark.
    next_extra_metadata: dict[str, Any] | None = None
    previous_member_end_s: float | None = None

    for rep in range(1, repetitions + 1):
        member_config = replace(config, run_id=f"{experiment_id}__r{rep}")
        member_extra_metadata = dict(next_extra_metadata or {})
        member_extra_metadata["preceding_member_end_s"] = previous_member_end_s
        # Governed admission owns the prepare-end capture. Passing the unset
        # sentinel lets _stage_prepare recapture after runtime.prepare(), so a
        # critical transition during preparation cannot be admitted from stale
        # pre-prepare evidence.
        member_environment = (
            environment_snapshot
            if campaign_policy is None
            else _ENVIRONMENT_UNSET
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
            instrument_calibration_dir=instrument_calibration_dir,
            instrument_power_policy=instrument_power_policy,
            post_window_sampling_dwell_s=post_window_sampling_dwell_s,
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
        if frozen_anchor is None and reference_eligibility["eligible"]:
            candidate_anchor = _experiment_cooldown_anchor(
                bundle_path,
                summary,
                reference_eligibility,
                policy_sha256=(
                    policy_binding.get("sha256")
                    if isinstance(policy_binding, dict)
                    else None
                ),
            )
            candidate_eligibility = cooldown_anchor_eligibility(
                candidate_anchor,
                (
                    policy_binding.get("sha256")
                    if isinstance(policy_binding, dict)
                    else None
                ),
            )
            if candidate_eligibility["eligible"]:
                frozen_anchor = candidate_anchor
                manifest["cooldown_anchor"] = frozen_anchor
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
                frozen_anchor=frozen_anchor,
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
    *,
    policy_sha256: str | None,
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
        "policy_sha256": policy_sha256,
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
    return idle_baseline_from_anchor(anchor)


def _write_cooldown_anchor_rejection(
    runs_root: Path,
    manifest: dict[str, Any],
    anchor: Any,
    eligibility: dict[str, Any],
    *,
    boundary: str,
    policy_sha256: str | None,
    observed_at_s: float,
) -> Path:
    """Persist the terminal D-077 verdict before rejecting child execution."""

    manifest["terminal_verdict"] = {
        "schema_version": COOLDOWN_ANCHOR_VERDICT_SCHEMA_VERSION,
        "record_type": "cooldown_anchor_verdict",
        "status": "rejected",
        "decision": "fail_closed",
        "reason": "invalid_frozen_cooldown_anchor",
        "boundary": boundary,
        "observed_at_s": observed_at_s,
        "policy_sha256": policy_sha256,
        "anchor_eligibility": eligibility,
        "rejected_anchor": deepcopy(anchor),
    }
    return write_experiment_rejection_verdict(runs_root, manifest)


def record_cooldown_anchor_rejection(
    config: BenchmarkConfig,
    runs_root: Path,
    clock: Clock,
    anchor: Any,
    eligibility: dict[str, Any],
    *,
    boundary: str,
) -> Path:
    """Record a CLI-boundary anchor rejection without starting a member."""

    experiment_id = (
        sanitize_id_component(config.run_id)
        if config.run_id is not None
        else generate_run_id(config, clock)
    )
    manifest: dict[str, Any] = {
        "experiment_id": experiment_id,
        "config_sha256": _config_sha256(config),
        "created_at_s": clock.now(),
        "members": [],
        "member_gaps": [],
        "condition_order": [],
        "cooldown": [],
    }
    return _write_cooldown_anchor_rejection(
        runs_root,
        manifest,
        anchor,
        eligibility,
        boundary=boundary,
        policy_sha256=None,
        observed_at_s=clock.now(),
    )


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
