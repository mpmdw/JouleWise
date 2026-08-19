#!/usr/bin/env python3
"""Lead-owned [QUIET-MAC] pulse-fiducial calibration run (D-078).

The current claim-bearing protocol is frozen in
configs/calibration/powermetrics_fiducial/protocol_v3.json and documented in
docs/contracts/powermetrics_fiducial.md. Historical protocol files remain
byte-frozen validation identities.

- preallocated 4096x4096 FP16 MLX matmuls, mx.eval GPU fencing;
- 3 warmup pulses, then k=59 pulses of 1.0 s each;
- deterministic low-discrepancy spacing 1.5 + vanDerCorput_2(j) s
  (avoids 10 Hz phase lock);
- >= 5 s baseline before and after the pulse train;
- events pulse_command_on/off carry full paired ClockStamps;
- primary rail gpu_power; CPU+GPU combined is corroboration only;
- gates: plateau >= 10 W over baseline, robust SNR >= 10, all pulses
  detected, no spurious plateaus - otherwise the artifact is invalid.

NEVER run this while another agent session is active on the machine
([QUIET-MAC] discipline); the run is refused without --allow-live.

Full lifecycle ownership of a privileged sampler is UNSUPPORTED pending
WO-SAMPLER-SUPERVISOR: a privileged supervisor, kernel no-fork confinement,
sudoers migration, and a live admission gate. The post-run process census in
this module is detect-and-report only; it neither proves ownership nor changes
run behavior.
"""

from __future__ import annotations

import argparse
import atexit
from contextlib import contextmanager
import hmac
import hashlib
import json
import math
import os
import signal
import stat
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, replace
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_exits import RefusalCode, emit_refusal  # noqa: E402
from joulewise import arm_readiness as arm_readiness_module  # noqa: E402
from joulewise.adapters.powermetrics import (  # noqa: E402
    POWER_METRICS,
    SAMPLERS,
    anchor_records_from_powermetrics,
    parse_powermetrics_records,
    samples_from_records,
)
from joulewise.clock import ClockStamp, SystemClock  # noqa: E402
from joulewise.calibration_bracketing import (  # noqa: E402
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    _current_estimator_code_sha256,
    load_calibration_acceptance_bound,
)
from joulewise.calibration_ledger import (  # noqa: E402
    BRACKET_SESSION_OPEN_EVENT,
    BRACKET_SESSION_SCHEMA,
    BRACKET_SESSION_SLOTS,
    DEFAULT_LEDGER_PATH,
    DEFAULT_HEAD_PIN_PATH,
    CalibrationLedgerError,
    CalibrationWriterLease,
    calibration_readiness,
    abort_bracket_session,
    append_pending_receipt,
    artifact_hashes as ledger_artifact_hashes,
    claim_bracket_session_slot,
    finalize_attempt_receipt,
    finalize_bracket_session_slot,
    head_pin_for_receipt,
    load_calibration_ledger_snapshot,
    normalize_calibration_custody_path,
    repair_calibration_ledger,
    stable_bracket_claim_id,
    terminal_head_pin_for_session,
)
from joulewise.powermetrics_fiducial import (  # noqa: E402
    BASELINE_S,
    CLOCK_ANCHOR_UNRESOLVED,
    DETECTION_NONCONVERGENT,
    DETECTION_PROJECTION_CELL_BUDGET,
    LEGACY_PROTOCOL_ID,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    PROTOCOL_V2_PULSE_COUNT,
    RESIDUAL_REGION_METHOD,
    PULSE_COUNT,
    PULSE_DURATION_S,
    SAMPLING_INTERVAL_MS,
    CommandedPulse,
    TraceInterval,
    WARMUP_PULSE_COUNT,
    allocate_matmul_buffers,
    capture_wall_time_from_events,
    clock_stamp_half_width_s,
    detect_pulses,
    instrument_evidence,
    protocol_definition_matches,
    protocol_sha256,
    pulse_schedule,
    run_matmul_pulse,
    trim_trace_after_pulses,
    rederive_detection_from_artifacts,
)
from joulewise.uncertainty_evidence import (  # noqa: E402
    ACTIVE_CAPTURE_ANCHOR_METHOD,
    resolve_clock_evidence_deriver,
)

PROTOCOL_PATH = (
    REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v3.json"
)
PROTOCOL_V2_PATH = (
    REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v2.json"
)
ROLLOVER_GATE_TIMEOUT_REASON = "pulse_calibration_rollover_gate_timeout"
SAMPLER_TERMINATE_TIMEOUT_S = 10.0
SAMPLER_CENSUS_DIAGNOSTIC = "powermetrics_post_teardown_census"
TEST_WRITER_CRASH_AUTHORIZATION_SCHEMA = (
    "joulewise.test_writer_crash_authorization.v1"
)
TEST_WRITER_CRASH_CAPABILITY_ROOT_ENV = (
    "JOULEWISE_TEST_WRITER_CRASH_CAPABILITY_ROOT"
)
TEST_LOGICAL_SAMPLER_ACK_ENV = "JW_FAKE_SAMPLER_ACK_PATH"
TEST_LOGICAL_CLOCK_ORIGIN_ENV = "JW_FAKE_LOGICAL_CLOCK_ORIGIN"
TEST_LOGICAL_ACK_SCHEMA = "joulewise.test_sampler_ack.v1"
TEST_LOGICAL_READY_EVENT = "sampler_ready"
TEST_LOGICAL_READY_SEQUENCE = 0
TEST_LOGICAL_PROTOCOL_EVENTS = frozenset(
    {
        "sampling_started",
        "warmup_command_on",
        "warmup_command_off",
        "pulse_command_on",
        "pulse_command_off",
        "sampling_stopped",
    }
)
_AUTHORIZED_WRITER_CRASH_STAGE: str | None = None
_CRASH_HOOK_DIAGNOSTIC_EMITTED = False
_LAUNCH_LINEAGE_LOCATOR_BASENAME = ".joulewise-launch-lineage.json"
_CALIBRATION_OUTPUT_ROOT_BASENAME = "instrument_validation"
_CALIBRATION_LAUNCH_REASON_CODES = frozenset(
    {
        "launch_consumption_missing",
        "launch_consumption_invalid",
        "launch_binding_mismatch",
        "launch_lineage_conflict",
        "launch_lifecycle_incomplete",
        "launch_handoff_invalid",
    }
)


class _CalibrationLaunchLineageError(ValueError):
    """Fallback D-078 refusal while the staged branch awaits stage-1 sync."""

    def __init__(self, reason_code: str, message: str) -> None:
        if reason_code not in _CALIBRATION_LAUNCH_REASON_CODES:
            raise ValueError(f"unregistered calibration launch code {reason_code!r}")
        super().__init__(message)
        self.reason_code = reason_code


class _LogicalTestClock:
    """Test-only clock advanced solely by synthetic protocol transitions."""

    def __init__(self, epoch_origin_s: float) -> None:
        if not math.isfinite(epoch_origin_s):
            raise ValueError("test logical clock origin must be finite")
        self._now_s = float(epoch_origin_s)

    def now(self) -> float:
        return self._now_s

    def stamp(self) -> ClockStamp:
        return ClockStamp(
            epoch_s=self._now_s,
            monotonic_before_s=self._now_s,
            monotonic_after_s=self._now_s,
            wall_resolution_s=0.0,
            monotonic_resolution_s=0.0,
        )

    def advance(self, seconds: float) -> None:
        if not math.isfinite(seconds) or seconds < 0.0:
            raise ValueError("test logical clock advance must be finite and nonnegative")
        self._now_s += seconds

    def advance_to(self, epoch_s: float) -> None:
        if not math.isfinite(epoch_s) or epoch_s < self._now_s:
            raise ValueError("test logical clock cannot move backward")
        self._now_s = float(epoch_s)


class _LogicalTestPulseDriver:
    """Synchronize each test command transition with a durable sampler ack."""

    def __init__(
        self,
        clock: _LogicalTestClock,
        acknowledgement_path: Path,
        *,
        timeout_s: float,
    ) -> None:
        self.clock = clock
        self.acknowledgement_path = acknowledgement_path
        self.timeout_s = timeout_s
        self._next_sequence = TEST_LOGICAL_READY_SEQUENCE + 1

    def next_sequence(self, event_type: str) -> int:
        if event_type not in TEST_LOGICAL_PROTOCOL_EVENTS:
            raise ValueError("test logical pulse event is not registered")
        sequence = self._next_sequence
        self._next_sequence += 1
        return sequence

    def await_acknowledgement(
        self,
        process: subprocess.Popen,
        *,
        sequence: int,
        event_type: str,
    ) -> dict[str, Any]:
        deadline = time.monotonic() + self.timeout_s
        while time.monotonic() < deadline:
            try:
                lines = self.acknowledgement_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            except (OSError, UnicodeDecodeError):
                lines = []
            for line in lines:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if (
                    isinstance(row, Mapping)
                    and row.get("schema") == TEST_LOGICAL_ACK_SCHEMA
                    and row.get("sequence") == sequence
                ):
                    if row.get("event_type") != event_type:
                        raise RuntimeError("test sampler acknowledgement event mismatch")
                    return dict(row)
            if process.poll() is not None:
                raise RuntimeError("test sampler exited before acknowledgement")
            time.sleep(min(0.001, self.timeout_s / 4))
        raise RuntimeError(
            f"test sampler acknowledgement timeout: {event_type}:{sequence}"
        )

    def await_ready(self, process: subprocess.Popen) -> None:
        row = self.await_acknowledgement(
            process,
            sequence=TEST_LOGICAL_READY_SEQUENCE,
            event_type=TEST_LOGICAL_READY_EVENT,
        )
        ready_epoch_s = row.get("logical_epoch_s")
        if isinstance(ready_epoch_s, bool) or not isinstance(
            ready_epoch_s, int | float
        ):
            raise RuntimeError("test sampler ready acknowledgement lacks logical time")
        self.clock.advance_to(float(ready_epoch_s))

    def drive_fenced_pulse(self, buffers: Any) -> int:
        """Issue fixed logical work; pulse duration advances only by protocol."""

        import mlx.core as mx  # noqa: PLC0415 - synthetic writer dependency

        left, right = buffers
        product = mx.matmul(left, right)
        mx.eval(product)
        return 1


class _AcceptancePreflightError(ValueError):
    """Named fail-closed reason for acceptance-artifact preflight."""

    def __init__(self, reason: str, **context: Any) -> None:
        super().__init__(reason)
        self.reason = reason
        self.context = context


def _derive_preflight_systematic_screen_s(
    identity_epoch: Mapping[str, Any] | None = None,
    *,
    acceptance_path: Path | None = None,
) -> Decimal:
    """Authenticate the active acceptance and derive its level comparator."""

    path = (
        DEFAULT_ACCEPTANCE_BOUND_PATH
        if acceptance_path is None
        else Path(acceptance_path)
    )
    if not path.exists():
        raise _AcceptancePreflightError("acceptance_artifact_missing")
    artifact = load_calibration_acceptance_bound(path)
    if artifact is None:
        raise _AcceptancePreflightError("acceptance_artifact_unauthenticated")
    if artifact.get("artifact_role") != "issued":
        raise _AcceptancePreflightError("acceptance_artifact_not_issued")

    prospective = artifact.get("prospective_rederivation")
    if not isinstance(prospective, Mapping):
        raise _AcceptancePreflightError("acceptance_artifact_derivation_invalid")
    if (
        protocol_sha256(PROTOCOL_ID) != prospective.get("protocol_sha256")
        or _current_estimator_code_sha256()
        != prospective.get("estimator_code_sha256")
    ):
        raise _AcceptancePreflightError("acceptance_artifact_stale")

    expected_epoch = artifact.get("identity_epoch")
    if not isinstance(expected_epoch, Mapping):
        raise _AcceptancePreflightError("acceptance_artifact_derivation_invalid")
    if identity_epoch is not None:
        stale_fields = sorted(
            field
            for field, expected in expected_epoch.items()
            if identity_epoch.get(field) != expected
        )
        if stale_fields:
            raise _AcceptancePreflightError(
                "acceptance_artifact_epoch_mismatch",
                stale_fields=stale_fields,
            )

    try:
        derivation = artifact["decimal_derivation"]
        source_statistics = derivation["source_statistics"]
        rounding = derivation["rounding"]["preflight_level_screen"]
        if (
            rounding["source"]
            != "decimal_derivation.source_statistics.maximum_s"
            or derivation["rounding"]["mode"] != "ROUND_HALF_EVEN"
            or rounding["numeric_role"] != "operative_comparator"
        ):
            raise KeyError("unrecognized preflight derivation rule")
        comparator = Decimal(source_statistics["maximum_s"]).quantize(
            Decimal(rounding["quantum_s"]),
            rounding=ROUND_HALF_EVEN,
        )
        recorded = Decimal(rounding["value_s"])
        ratified = Decimal(
            derivation["ratified_operatives"]["preflight_level_screen_s"]
        )
    except (InvalidOperation, KeyError, TypeError, ValueError):
        raise _AcceptancePreflightError(
            "acceptance_artifact_derivation_invalid"
        ) from None
    if not comparator.is_finite() or comparator != recorded or comparator != ratified:
        raise _AcceptancePreflightError("acceptance_artifact_derivation_invalid")
    return comparator


# Recovery's resume-finalize path imports this historical public symbol.  It
# remains available as an authenticated derivation, never as a copied scalar;
# the live writer below independently derives and epoch-checks its local value.
try:
    PREFLIGHT_SYSTEMATIC_SCREEN_S = _derive_preflight_systematic_screen_s()
except _AcceptancePreflightError:
    PREFLIGHT_SYSTEMATIC_SCREEN_S = None


class WriterStage(str, Enum):
    BEFORE_PRE_RESERVE_READINESS = "before-pre-reserve-readiness"
    AFTER_PRE_RESERVE_READINESS = "after-pre-reserve-readiness"
    RESERVATION_INTENT_WRITE = "reservation-intent-write"
    RESERVATION_INTENT_FSYNCED = "reservation-intent-fsynced"
    RESERVATION_TARGET_WRITE = "reservation-target-write"
    RESERVATION_TARGET_FSYNCED = "reservation-target-fsynced"
    RESERVATION_RETURNED = "reservation-returned"
    BEFORE_WRITER_LEASE = "before-writer-lease"
    AFTER_WRITER_LEASE = "after-writer-lease"
    AFTER_REPAIR = "after-repair"
    AFTER_SLOT_VALIDATION = "after-slot-validation"
    CLAIM_INTENT_WRITE = "claim-intent-write"
    CLAIM_INTENT_FSYNCED = "claim-intent-fsynced"
    CLAIM_TARGET_WRITE = "claim-target-write"
    CLAIM_TARGET_FSYNCED = "claim-target-fsynced"
    CLAIM_RETURNED_BEFORE_BEGUN = "claim-returned-before-begun"
    AFTER_BEGUN = "after-begun"
    BEFORE_EXIT_HANDLER_REGISTRATION = "before-exit-handler-registration"
    AFTER_EXIT_HANDLER_REGISTRATION = "after-exit-handler-registration"
    AFTER_CUSTODY_DIRECTORY_CREATION = "after-custody-directory-creation"
    AFTER_EVENT_STREAM_OPEN = "after-event-stream-open"
    AFTER_SAMPLER_SPAWN = "after-sampler-spawn"
    AFTER_SAMPLER_READY = "after-sampler-ready"
    AFTER_ROLLOVER_READY = "after-rollover-ready"
    DURING_CAPTURE = "during-capture"
    AFTER_SAMPLER_TEARDOWN = "after-sampler-teardown"
    DURING_RAW_EVENTS_ARTIFACT = "during-raw-events-artifact"
    DURING_TRACE_ARTIFACT = "during-trace-artifact"
    DURING_EVIDENCE_ARTIFACT = "during-evidence-artifact"
    DURING_MANIFEST_ARTIFACT = "during-manifest-artifact"
    ARTIFACTS_COMPLETE_BEFORE_FINALIZATION = "artifacts-complete-before-finalization"
    FINALIZATION_INTENT_WRITE = "finalization-intent-write"
    FINALIZATION_INTENT_FSYNCED = "finalization-intent-fsynced"
    FINALIZATION_TARGET_WRITE = "finalization-target-write"
    FINALIZATION_TARGET_FSYNCED = "finalization-target-fsynced"
    FINALIZATION_RETURNED_BEFORE_CLOSED = "finalization-returned-before-closed"
    AFTER_CLOSED_BEFORE_HANDLER_UNREGISTER = "after-closed-before-handler-unregister"
    AFTER_PRE_FINALIZATION_BEFORE_SUPERVISOR_DISPATCH = (
        "after-pre-finalization-before-supervisor-dispatch"
    )
    BEFORE_POST_DISPATCH = "before-post-dispatch"
    AFTER_POST_FINALIZATION_BEFORE_TERMINAL_PIN = (
        "after-post-finalization-before-terminal-pin"
    )
    AFTER_TERMINAL_PIN_BEFORE_OUTPUT = "after-terminal-pin-before-output"


def _emit_inert_crash_hook_diagnostic(requested_stage: str) -> None:
    global _CRASH_HOOK_DIAGNOSTIC_EMITTED
    if _CRASH_HOOK_DIAGNOSTIC_EMITTED:
        return
    print(
        json.dumps(
            {
                "event": "joulewise_test_writer_crash_hook_inert",
                "reason": "missing_or_invalid_harness_authorization",
                "requested_stage": requested_stage,
            },
            separators=(",", ":"),
        ),
        file=sys.stderr,
        flush=True,
    )
    _CRASH_HOOK_DIAGNOSTIC_EMITTED = True


def _configure_writer_crash_authorization(
    authorization_path: Path | None,
    *,
    entry_point: Path,
) -> None:
    """Consume and validate one explicit harness capability, if supplied."""

    global _AUTHORIZED_WRITER_CRASH_STAGE
    _AUTHORIZED_WRITER_CRASH_STAGE = None
    requested_stage = os.environ.get("JOULEWISE_TEST_WRITER_CRASH_STAGE")
    token = os.environ.get("JOULEWISE_TEST_WRITER_CRASH_TOKEN")
    valid_stage: str | None = None
    descriptor = -1
    root_descriptor = -1
    authorization_basename: str | None = None
    path = Path(authorization_path) if authorization_path is not None else None
    try:
        if path is None:
            raise ValueError("missing explicit crash authorization path")
        root_raw = os.environ.get(TEST_WRITER_CRASH_CAPABILITY_ROOT_ENV)
        if root_raw is None:
            raise ValueError("missing harness crash capability root")
        resolved_root = Path(root_raw).resolve(strict=True)
        resolved_path = path.resolve(strict=True)
        if resolved_path.parent != resolved_root:
            raise ValueError("crash authorization is outside harness capability root")
        authorization_basename = resolved_path.name
        root_descriptor = os.open(
            resolved_root,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        root_status = os.fstat(root_descriptor)
        if (
            not stat.S_ISDIR(root_status.st_mode)
            or root_status.st_uid != os.getuid()
            or stat.S_IMODE(root_status.st_mode) != 0o700
        ):
            raise ValueError("unsafe harness crash capability root")
        descriptor = os.open(
            resolved_path.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=root_descriptor,
        )
        status = os.fstat(descriptor)
        if (
            not stat.S_ISREG(status.st_mode)
            or status.st_uid != os.getuid()
            or stat.S_IMODE(status.st_mode) != 0o600
            or status.st_nlink != 1
        ):
            raise ValueError("unsafe crash authorization inode")
        raw = os.read(descriptor, 65537)
        if len(raw) > 65536:
            raise ValueError("oversized crash authorization")
        payload = json.loads(raw)
        resolved_entry = Path(entry_point).resolve(strict=True)
        if (
            not isinstance(payload, Mapping)
            or payload.get("schema_version")
            != TEST_WRITER_CRASH_AUTHORIZATION_SCHEMA
            or payload.get("stage") != requested_stage
            or payload.get("stage") not in {stage.value for stage in WriterStage}
            or payload.get("entry_point") != str(resolved_entry)
            or payload.get("entry_point_sha256")
            != hashlib.sha256(resolved_entry.read_bytes()).hexdigest()
            or not isinstance(payload.get("nonce"), str)
            or not isinstance(token, str)
            or not hmac.compare_digest(payload["nonce"], token)
        ):
            raise ValueError("crash authorization fields do not match")
        candidate_stage = str(payload["stage"])
        assert authorization_basename is not None
        os.unlink(authorization_basename, dir_fd=root_descriptor)
        if os.fstat(descriptor).st_nlink != 0:
            raise ValueError("crash authorization unlink did not consume inode")
        valid_stage = candidate_stage
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        valid_stage = None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if root_descriptor >= 0:
            os.close(root_descriptor)
    if valid_stage is not None:
        _AUTHORIZED_WRITER_CRASH_STAGE = valid_stage
    elif requested_stage is not None:
        _emit_inert_crash_hook_diagnostic(requested_stage)


def _writer_stage(stage: WriterStage) -> None:
    """Real production boundary armed only by two matching logical keys."""

    if (
        os.environ.get("JOULEWISE_TEST_WRITER_CRASH_STAGE") == stage.value
        and _AUTHORIZED_WRITER_CRASH_STAGE == stage.value
    ):
        os.kill(os.getpid(), signal.SIGKILL)


def _write_text_artifact(path: Path, payload: str, stage: WriterStage) -> None:
    """Write one artifact with the stage boundary inside the durable write."""

    raw = payload.encode("utf-8")
    split = max(1, len(raw) // 2)
    with path.open("xb") as handle:
        handle.write(raw[:split])
        handle.flush()
        os.fsync(handle.fileno())
        _writer_stage(stage)
        handle.write(raw[split:])
        handle.flush()
        os.fsync(handle.fileno())


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _derive_active_capture_clock_evidence(*, stamps, records):
    """Derive calibration clock evidence under the active registered method."""

    deriver = resolve_clock_evidence_deriver(ACTIVE_CAPTURE_ANCHOR_METHOD)
    return deriver(stamps=stamps, records=records)


def _label_active_capture_detection(detection, evidence: Mapping[str, Any]):
    """Carry the active clock method into the authored instrument evidence."""

    clock_anchor = evidence.get("clock_anchor")
    if not isinstance(clock_anchor, Mapping):
        raise ValueError("active capture clock anchor is missing")
    method = clock_anchor.get("method")
    if method != ACTIVE_CAPTURE_ANCHOR_METHOD:
        raise ValueError("active capture clock anchor method drifted")
    return replace(
        detection,
        anchor_method=method,
        derivation_role="prospective",
    )


def _planned_t1_bindings(
    *, planned_epoch: Mapping[str, Any], sampler_binary: Path, mlx_version: object
) -> dict[str, Any]:
    """Project the capture-time T1 bindings from the active method identity."""

    return {
        **planned_epoch,
        "powermetrics_sha256": sha256_path(sampler_binary),
        "anchor_method_version": ACTIVE_CAPTURE_ANCHOR_METHOD,
        "mlx_version": mlx_version,
        "protocol_sha256": sha256_path(PROTOCOL_PATH),
    }


def _raise_calibration_launch_lineage(
    reason_code: str, detail: str
) -> None:
    error_type = getattr(
        arm_readiness_module,
        "LaunchLineageError",
        _CalibrationLaunchLineageError,
    )
    raise error_type(reason_code, detail)


def _calibration_launch_reason_code(exc: BaseException) -> str | None:
    reason_code = getattr(exc, "reason_code", None)
    return (
        reason_code
        if isinstance(reason_code, str)
        and reason_code in _CALIBRATION_LAUNCH_REASON_CODES
        else None
    )


def _emit_calibration_launch_refusal(exc: BaseException) -> int:
    reason_code = _calibration_launch_reason_code(exc)
    if reason_code is None:
        raise exc
    print(f"error: {reason_code}: {exc}", file=sys.stderr)
    return 2


def _launch_lineage_required(config: object) -> bool:
    predicate = getattr(arm_readiness_module, "launch_lineage_required", None)
    if callable(predicate):
        return bool(predicate(config))
    if not isinstance(config, Mapping):
        return False
    metadata = config.get("run_metadata")
    tags = metadata.get("tags") if isinstance(metadata, Mapping) else None
    return isinstance(tags, list) and "launch_lineage_required" in tags


def _load_calibration_source_config(
    config_path: Path,
) -> tuple[Mapping[str, Any] | None, bytes | None, Path | None]:
    """Read the existing acceptance input without perturbing legacy failures."""

    try:
        if config_path.is_symlink():
            return None, None, None
        resolved = config_path.resolve(strict=True)
        raw = resolved.read_bytes()
        parsed = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None, None, None
    return (
        (parsed if isinstance(parsed, Mapping) else None),
        raw,
        resolved,
    )


def _authenticate_calibration_source_config(
    authentication: Mapping[str, Any],
    *,
    config_path: Path,
    config_raw: bytes,
) -> None:
    """Bind the acceptance input as a pack member or pack-pinned artifact."""

    try:
        pack_root = Path(str(authentication["pack_root"])).resolve(strict=True)
        config_resolved = config_path.resolve(strict=True)
    except (KeyError, OSError) as exc:
        _raise_calibration_launch_lineage(
            "launch_binding_mismatch",
            f"authenticated calibration config root is unavailable: {exc}",
        )
    config_sha256 = hashlib.sha256(config_raw).hexdigest()
    try:
        relative = config_resolved.relative_to(pack_root).as_posix()
    except ValueError:
        relative = None
    inventory = authentication.get("config_inventory")
    if (
        relative is not None
        and isinstance(inventory, Mapping)
        and inventory.get(relative) == config_sha256
    ):
        return

    try:
        plan = json.loads((pack_root / "plan_tree.json").read_bytes())
        policy = plan["acceptance_policy"]
        reference = policy["issued_acceptance"]
        reference_path = reference["path"]
        reference_sha256 = reference["artifact_sha256"]
        if not isinstance(reference_path, str) or not reference_path:
            raise ValueError("issued acceptance path is invalid")
        expected_path = Path(reference_path)
        if not expected_path.is_absolute():
            expected_path = REPO_ROOT / expected_path
        expected_path = expected_path.resolve(strict=True)
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        _raise_calibration_launch_lineage(
            "launch_binding_mismatch",
            f"authenticated pack omits the selected calibration config: {exc}",
        )
    if expected_path != config_resolved or reference_sha256 != config_sha256:
        _raise_calibration_launch_lineage(
            "launch_binding_mismatch",
            "selected calibration config is not bound by authenticated pack bytes",
        )


def authenticate_calibration_writer_launch_lineage(
    output_root: Path,
    *,
    session_id: str | None,
    slot: str | None,
    attempt_id: str | None,
    source_config_path: Path | None = None,
) -> dict[str, Any] | None:
    """Authenticate the fixed calibration locator before any custody claim."""

    selected_config_path = (
        DEFAULT_ACCEPTANCE_BOUND_PATH
        if source_config_path is None
        else Path(source_config_path)
    )
    config, config_raw, config_resolved = _load_calibration_source_config(
        selected_config_path
    )
    if not _launch_lineage_required(config):
        return None
    if Path(output_root).name != _CALIBRATION_OUTPUT_ROOT_BASENAME:
        _raise_calibration_launch_lineage(
            "launch_binding_mismatch",
            "calibration --output-root must end in instrument_validation",
        )
    if session_id is None or slot not in BRACKET_SESSION_SLOTS or attempt_id is None:
        _raise_calibration_launch_lineage(
            "launch_binding_mismatch",
            "marker-bearing calibration requires an exact bracket session and slot",
        )
    assert config_raw is not None and config_resolved is not None
    try:
        resolved_output_root = Path(output_root).resolve(strict=False)
        selected_root = resolved_output_root.parent.resolve(strict=True)
    except OSError as exc:
        _raise_calibration_launch_lineage(
            "launch_binding_mismatch",
            f"calibration output parent is unavailable: {exc}",
        )
    locator_basename = getattr(
        arm_readiness_module,
        "LAUNCH_LINEAGE_LOCATOR_BASENAME",
        _LAUNCH_LINEAGE_LOCATOR_BASENAME,
    )
    locator_path = selected_root / locator_basename
    if not locator_path.exists() or not locator_path.with_name(
        f"{locator_path.name}.sha256"
    ).exists():
        _raise_calibration_launch_lineage(
            "launch_consumption_missing",
            "marker-bearing calibration launch-lineage locator is absent",
        )
    authenticate_campaign = getattr(
        arm_readiness_module,
        "authenticate_campaign_launch_lineage",
        None,
    )
    authenticate_lineage = getattr(
        arm_readiness_module,
        "authenticate_launch_lineage",
        None,
    )
    if not callable(authenticate_campaign) or not callable(authenticate_lineage):
        _raise_calibration_launch_lineage(
            "launch_consumption_invalid",
            "launch-lineage authenticator is unavailable in this checkout",
        )
    authentication = authenticate_campaign(selected_root)
    _authenticate_calibration_source_config(
        authentication,
        config_path=config_resolved,
        config_raw=config_raw,
    )
    direct = authenticate_lineage(
        authentication["launch_lineage"],
        require_completion=False,
        expected_pack_root=authentication["pack_root"],
        require_current_boot=True,
        require_completion_absent=True,
    )
    arm_context = direct.get("arm_context")
    attempt_key = f"{slot}_attempt_id"
    if (
        not isinstance(arm_context, Mapping)
        or arm_context.get("bracket_session_id") != session_id
        or arm_context.get(attempt_key) != attempt_id
    ):
        _raise_calibration_launch_lineage(
            "launch_binding_mismatch",
            "calibration bracket session/attempt differs from authenticated arm context",
        )
    return {
        "launch_lineage": authentication["launch_lineage"],
        "locator_sha256": authentication["locator_sha256"],
        "selected_config_path": str(config_resolved),
        "selected_config_sha256": hashlib.sha256(config_raw).hexdigest(),
    }


def reconcile_calibration_writer_launch_lineage(
    outer: Mapping[str, Any],
    output_root: Path,
    *,
    session_id: str | None,
    slot: str | None,
    attempt_id: str | None,
    source_config_path: Path | None = None,
) -> dict[str, Any]:
    """Reopen writer inputs and reject any outer/inner lineage swap."""

    inner = authenticate_calibration_writer_launch_lineage(
        output_root,
        session_id=session_id,
        slot=slot,
        attempt_id=attempt_id,
        source_config_path=source_config_path,
    )
    compared_fields = (
        "launch_lineage",
        "locator_sha256",
        "selected_config_path",
        "selected_config_sha256",
    )
    if inner is None or any(inner.get(name) != outer.get(name) for name in compared_fields):
        _raise_calibration_launch_lineage(
            "launch_lineage_conflict",
            "calibration launch lineage/config changed during writer execution",
        )
    return inner


def _sysctl_identity(name: str) -> str:
    """Read a reservation-time macOS identity before capture begins."""

    value = subprocess.run(
        ["/usr/sbin/sysctl", "-n", name],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    if not value:
        raise RuntimeError(f"empty reservation identity: {name}")
    return value


def verify_frozen_protocol(path: Path = PROTOCOL_PATH) -> bool:
    """Load and field-bind the frozen JSON to executable module constants."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    return protocol_definition_matches(payload)


def _terminate_powermetrics(process: subprocess.Popen) -> None:
    """Best-effort bounded termination and reaping of the direct child."""

    poll = getattr(process, "poll", None)  # small unit-test fakes lack poll
    if callable(poll) and poll() is not None:
        process.communicate(timeout=SAMPLER_TERMINATE_TIMEOUT_S)
        return
    process.terminate()
    try:
        process.communicate(timeout=SAMPLER_TERMINATE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate(timeout=SAMPLER_TERMINATE_TIMEOUT_S)


def _powermetrics_process_census() -> list[dict[str, object]]:
    """Best-effort snapshot of processes whose command names powermetrics."""

    try:
        completed = subprocess.run(
            ["ps", "-axo", "pid=,comm=,args="],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2.0,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if completed.returncode != 0:
        return []
    findings: list[dict[str, object]] = []
    for line in completed.stdout.splitlines():
        fields = line.strip().split(maxsplit=2)
        if len(fields) < 2 or not fields[0].isdigit():
            continue
        pid = int(fields[0])
        command = " ".join(fields[1:])
        if pid != os.getpid() and "powermetrics" in command.casefold():
            findings.append({"pid": pid, "command": command})
    return findings


def _report_powermetrics_census(event_reporter=None) -> None:
    """Loudly report census findings without asserting or changing behavior."""

    try:
        findings = _powermetrics_process_census()
    except Exception:  # noqa: BLE001 - census is detect-and-report only
        return
    if not findings:
        return
    metadata = {
        "findings": findings,
        "scope": "detect_and_report_only",
        "lifecycle_ownership": "unsupported_pending_WO-SAMPLER-SUPERVISOR",
    }
    try:
        print(
            json.dumps(
                {"event": SAMPLER_CENSUS_DIAGNOSTIC, **metadata}, sort_keys=True
            ),
            file=sys.stderr,
            flush=True,
        )
    except Exception:  # noqa: BLE001 - census reporting cannot alter run behavior
        pass
    if event_reporter is not None:
        try:
            event_reporter(SAMPLER_CENSUS_DIAGNOSTIC, metadata)
        except Exception:  # noqa: BLE001 - census reporting cannot alter run behavior
            pass


@contextmanager
def _sampler_lifetime(
    command: list[str],
    *,
    event_reporter=None,
    environment: Mapping[str, str] | None = None,
):
    """Join the direct sampler child on every exit path, then census."""

    if environment is None:
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=environment,
        )
    try:
        yield process
    finally:
        try:
            _terminate_powermetrics(process)
        finally:
            _report_powermetrics_census(event_reporter)


def wait_for_preworkload_rollover(
    capture_path: Path,
    process: subprocess.Popen,
    *,
    timeout_s: float = 15.0,
    poll_s: float = 0.05,
) -> None:
    """Require an advancing native plist timestamp before any workload.

    Timeout is a governed refusal, not permission to fall through. The
    sampler is terminated here so callers cannot accidentally continue with
    baseline, warmup, or pulse work after the gate fails.
    """

    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            records = parse_powermetrics_records(capture_path.read_bytes())
        except (OSError, ValueError):
            records = []
        stamps = [
            float(record.metadata["plist_timestamp_s"])
            for record in records
        ]
        if any(later > earlier for earlier, later in zip(stamps, stamps[1:])):
            return
        time.sleep(poll_s)
    _terminate_powermetrics(process)
    raise RuntimeError(ROLLOVER_GATE_TIMEOUT_REASON)


def trim_trace_after_warmups(
    intervals: list[TraceInterval], warmups: list[CommandedPulse]
) -> list[TraceInterval]:
    """Remove captured warmup plateaus before measured-pulse detection.

    Warmups are deliberately inside the raw capture but are not protocol
    pulses.  Leaving them in the detector's ``outside`` baseline launders no
    evidence: they are classified as spurious plateaus and make every clean
    live validation invalid.  Trim only through the final commanded warmup
    edge; the second BASELINE_S pause remains available to fit the first
    measured edge, and any genuinely uncommanded plateau after that edge is
    still detected.
    """

    return trim_trace_after_pulses(intervals, warmups)


def rederive_artifact(source_dir: Path, output: Path) -> dict[str, object]:
    """Re-emit v2 validation evidence from compatible 40-pulse primary bytes."""

    source_dir = Path(source_dir)
    manifest_path = source_dir / "manifest.json"
    evidence_path = source_dir / "instrument_evidence.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        stored = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("source calibration metadata is unreadable") from exc
    artifacts = manifest.get("artifacts") if isinstance(manifest, dict) else None
    if not isinstance(artifacts, dict) or not isinstance(stored, dict):
        raise ValueError("source calibration metadata is malformed")
    if (
        stored.get("protocol_id") not in {LEGACY_PROTOCOL_ID, PROTOCOL_V2_ID}
        or stored.get("pulse_count") != PROTOCOL_V2_PULSE_COUNT
    ):
        raise ValueError("re-derivation requires compatible 40-pulse v1/v2 evidence")
    raw_by_name: dict[str, bytes] = {}
    for relative in (
        "raw/powermetrics.plist",
        "events.jsonl",
        "instrument_evidence.json",
    ):
        expected = artifacts.get(relative)
        candidate = source_dir / relative
        try:
            raw = candidate.read_bytes()
        except OSError as exc:
            raise ValueError(f"source artifact missing: {relative}") from exc
        if (
            not isinstance(expected, str)
            or hashlib.sha256(raw).hexdigest() != expected
        ):
            raise ValueError(f"source artifact hash mismatch: {relative}")
        raw_by_name[relative] = raw
    stored_hashes = stored.get("artifact_sha256")
    if not isinstance(stored_hashes, dict):
        raise ValueError("source evidence omits primary artifact hashes")
    for relative in ("raw/powermetrics.plist", "events.jsonl"):
        if hashlib.sha256(raw_by_name[relative]).hexdigest() != stored_hashes.get(
            relative
        ):
            raise ValueError(f"source evidence hash mismatch: {relative}")
    fresh = rederive_detection_from_artifacts(
        raw_by_name["raw/powermetrics.plist"],
        raw_by_name["events.jsonl"],
        stored.get("clock_anchor"),
        protocol_id=str(stored.get("protocol_id")),
    )
    stored_bound = stored.get("b_fiducial_s")
    if (
        isinstance(stored_bound, bool)
        or not isinstance(stored_bound, int | float)
        or fresh.b_fiducial_s is None
    ):
        raise ValueError("source calibration bound is malformed")
    fresh = replace(
        fresh,
        b_fiducial_s=max(float(stored_bound), float(fresh.b_fiducial_s)),
    )
    bindings = dict(stored.get("bindings", {}))
    bindings.update(
        {
            "pulse_protocol_id": PROTOCOL_V2_ID,
            "estimator_revision": RESIDUAL_REGION_METHOD,
            "protocol_sha256": sha256_path(PROTOCOL_V2_PATH),
        }
    )
    validation_id = str(stored.get("validation_id") or source_dir.name) + "-v2"
    payload = instrument_evidence(
        fresh,
        bindings=bindings,
        validation_id=validation_id,
        artifact_sha256={
            relative: hashlib.sha256(raw_by_name[relative]).hexdigest()
            for relative in ("raw/powermetrics.plist", "events.jsonl")
        },
        capture_wall_time_s=capture_wall_time_from_events(
            raw_by_name["events.jsonl"]
        ),
        protocol_id=PROTOCOL_V2_ID,
        protocol_pulse_count=PROTOCOL_V2_PULSE_COUNT,
    )
    payload["clock_anchor"] = stored.get("clock_anchor")
    payload["clock_anchor_resolved"] = True
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create: re-derivation must never clobber an existing evidence
    # artifact (same rule as the extraction and campaign-log outputs).
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def _validate_reserved_bracket_slot(
    ledger_path: Path,
    head_pin_path: Path,
    *,
    session_id: str,
    slot: str,
    attempt_id: str,
    custody_locator: str,
    identity_epoch: Mapping[str, Any],
    t1_bindings: Mapping[str, Any],
    require_committed_pin: bool = True,
) -> None:
    """Authenticate the exact predeclared slot before capture state exists."""

    snapshot = load_calibration_ledger_snapshot(
        ledger_path,
        head_pin_path,
        require_committed_pin=require_committed_pin,
        verify_custody=True,
    )
    session = snapshot.bracket_session_by_id.get(session_id)
    finalized_slots = set(session.finalized_slots) if session is not None else set()
    expected_slot = (
        "pre"
        if not finalized_slots
        else "post"
        if finalized_slots == {"pre"}
        else None
    )
    open_receipt = next(
        (
            receipt
            for receipt in snapshot.receipts
            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
            and receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
            and receipt.get("session_id") == session_id
        ),
        None,
    )
    reserved = (
        open_receipt.get("slots", {}).get(slot)
        if isinstance(open_receipt, Mapping)
        and isinstance(open_receipt.get("slots"), Mapping)
        else None
    )
    if (
        not snapshot.is_governed_open_bracket_extension
        or session is None
        or session.state != "open"
        or slot not in BRACKET_SESSION_SLOTS
        or slot != expected_slot
        or session.slot_attempt_ids.get(slot) != attempt_id
        or not isinstance(reserved, Mapping)
        or reserved.get("attempt_id") != attempt_id
        or reserved.get("custody_locator") != custody_locator
        or dict(reserved.get("identity_epoch", {})) != dict(identity_epoch)
        or dict(reserved.get("t1_bindings", {})) != dict(t1_bindings)
    ):
        raise CalibrationLedgerError(RefusalCode.RESERVED_SLOT_MISMATCH)


class _CaptureLedgerLifecycle:
    """Route one writer attempt through ordinary or bracket-session APIs."""

    def __init__(
        self,
        *,
        ledger_path: Path,
        head_pin_path: Path,
        attempt_id: str,
        custody_locator: str,
        identity_epoch: Mapping[str, Any],
        t1_bindings: Mapping[str, Any],
        session_id: str | None = None,
        slot: str | None = None,
        require_committed_pin: bool = True,
    ) -> None:
        if (session_id is None) != (slot is None):
            raise CalibrationLedgerError(RefusalCode.WRITER_BRACKET_ARGUMENTS)
        self.ledger_path = Path(ledger_path)
        self.head_pin_path = Path(head_pin_path)
        self.attempt_id = attempt_id
        self.custody_locator = normalize_calibration_custody_path(
            custody_locator
        )
        self.identity_epoch: Mapping[str, Any] = identity_epoch
        self.t1_bindings: Mapping[str, Any] = t1_bindings
        self.capture_wall_time_s: str | None = None
        self.exact_bound_lexeme_s: str | None = None
        self.session_id = session_id
        self.slot = slot
        self.require_committed_pin = require_committed_pin
        self.claim_id = (
            stable_bracket_claim_id(
                session_id=session_id,
                slot=slot,
                attempt_id=attempt_id,
            )
            if session_id is not None and slot is not None
            else None
        )
        self.writer_lease = CalibrationWriterLease(self.ledger_path)
        self.begun = False
        self.closed = False

    @property
    def is_bracket_session(self) -> bool:
        return self.session_id is not None

    def begin(self) -> None:
        """Reserve ordinarily, or authenticate a previously reserved slot."""

        if self.begun:
            raise CalibrationLedgerError(
                RefusalCode.PRE_SLOT_NOT_READY,
                context={"reason": "lifecycle_already_began"},
            )
        # Early warning only. The same binding is checked again after the
        # nonblocking lease is held; only that second check can authorize ARM.
        if self.is_bracket_session:
            self._validate_slot()
        try:
            _writer_stage(WriterStage.BEFORE_WRITER_LEASE)
            self.writer_lease.acquire()
            _writer_stage(WriterStage.AFTER_WRITER_LEASE)
            repair_calibration_ledger(
                self.ledger_path,
                engine_identity="validate_powermetrics_fiducial",
                attestation_reason="automatic pre-capture ledger recovery",
            )
            _writer_stage(WriterStage.AFTER_REPAIR)
            self._begin_once()
            _writer_stage(WriterStage.CLAIM_RETURNED_BEFORE_BEGUN)
            self.begun = True
            _writer_stage(WriterStage.AFTER_BEGUN)
        except Exception:
            self.writer_lease.release()
            raise

    def _validate_slot(self) -> None:
        assert self.session_id is not None and self.slot is not None
        _validate_reserved_bracket_slot(
            self.ledger_path,
            self.head_pin_path,
            session_id=self.session_id,
            slot=self.slot,
            attempt_id=self.attempt_id,
            custody_locator=self.custody_locator,
            identity_epoch=self.identity_epoch,
            t1_bindings=self.t1_bindings,
            require_committed_pin=self.require_committed_pin,
        )

    def _begin_once(self) -> None:
        """Perform one stable-identity reservation or slot-claim attempt."""

        if self.is_bracket_session:
            assert self.session_id is not None and self.slot is not None
            readiness = calibration_readiness(
                self.ledger_path,
                self.head_pin_path,
                phase="pre-slot",
                session_id=self.session_id,
                slot=self.slot,
                attempt_id=self.attempt_id,
                enforcing_under_lease=True,
                require_committed_pin=self.require_committed_pin,
            )
            if readiness.status != "ready":
                assert readiness.refusal_code is not None
                raise CalibrationLedgerError(readiness.refusal_code)
            self._validate_slot()
            print(
                json.dumps(
                    {
                        "event": "calibration_writer_arm_authorized",
                        "session_id": self.session_id,
                        "slot": self.slot,
                        "attempt_id": self.attempt_id,
                    },
                    sort_keys=True,
                ),
                file=sys.stderr,
                flush=True,
            )
            _writer_stage(WriterStage.AFTER_SLOT_VALIDATION)
            claim_bracket_session_slot(
                self.ledger_path,
                session_id=self.session_id,
                slot=self.slot,
                attempt_id=self.attempt_id,
                claim_id=self.claim_id,
                _stage_boundary=lambda boundary: _writer_stage(
                    {
                        "intent-write": WriterStage.CLAIM_INTENT_WRITE,
                        "intent-fsynced": WriterStage.CLAIM_INTENT_FSYNCED,
                        "target-write": WriterStage.CLAIM_TARGET_WRITE,
                        "target-fsynced": WriterStage.CLAIM_TARGET_FSYNCED,
                    }[boundary]
                ),
            )
        else:
            append_pending_receipt(
                self.ledger_path,
                attempt_id=self.attempt_id,
                custody_locator=self.custody_locator,
                identity_epoch=self.identity_epoch,
                t1_bindings=self.t1_bindings,
                head_pin_path=self.head_pin_path,
                require_committed_pin=self.require_committed_pin,
            )

    def abandon(self, reason: str) -> Mapping[str, Any] | None:
        """Best-effort governed closure for an interrupted writer."""

        if not self.begun or self.closed:
            return None
        try:
            if self.is_bracket_session:
                assert self.session_id is not None
                receipt = abort_bracket_session(
                    self.ledger_path,
                    session_id=self.session_id,
                    reason=reason,
                )
            else:
                receipt = finalize_attempt_receipt(
                    self.ledger_path,
                    attempt_id=self.attempt_id,
                    disposition="abandoned",
                    custody_locator=self.custody_locator,
                    artifact_sha256=ledger_artifact_hashes(
                        Path(self.custody_locator)
                    ),
                    identity_epoch=self.identity_epoch,
                    t1_bindings=self.t1_bindings,
                    capture_wall_time_s=self.capture_wall_time_s,
                    exact_bound_lexeme_s=self.exact_bound_lexeme_s,
                )
            self.closed = True
            return receipt
        finally:
            self.writer_lease.release()

    def finalize(
        self,
        disposition: str,
        *,
        invalid_evidence_disposition: str | None = None,
    ) -> tuple[Mapping[str, Any], dict[str, Any] | None]:
        """Finalize the exact attempt and return any terminal head candidate."""

        if not self.begun or self.closed:
            raise CalibrationLedgerError(RefusalCode.SESSION_NOT_OPEN)
        if invalid_evidence_disposition not in (
            None,
            CLOCK_ANCHOR_UNRESOLVED,
            DETECTION_NONCONVERGENT,
        ):
            raise ValueError("invalid evidence disposition is not registered")
        try:
            artifacts = ledger_artifact_hashes(Path(self.custody_locator))
            if self.is_bracket_session:
                assert self.session_id is not None and self.slot is not None
                receipt = finalize_bracket_session_slot(
                    self.ledger_path,
                    session_id=self.session_id,
                    slot=self.slot,
                    disposition=disposition,
                    custody_locator=self.custody_locator,
                    artifact_sha256=artifacts,
                    identity_epoch=self.identity_epoch,
                    t1_bindings=self.t1_bindings,
                    capture_wall_time_s=self.capture_wall_time_s,
                    exact_bound_lexeme_s=self.exact_bound_lexeme_s,
                    _stage_boundary=lambda boundary: _writer_stage(
                        {
                            "intent-write": WriterStage.FINALIZATION_INTENT_WRITE,
                            "intent-fsynced": WriterStage.FINALIZATION_INTENT_FSYNCED,
                            "target-write": WriterStage.FINALIZATION_TARGET_WRITE,
                            "target-fsynced": WriterStage.FINALIZATION_TARGET_FSYNCED,
                        }[boundary]
                    ),
                )
                _writer_stage(WriterStage.FINALIZATION_RETURNED_BEFORE_CLOSED)
                if self.slot == "pre" and disposition != "valid":
                    receipt = abort_bracket_session(
                        self.ledger_path,
                        session_id=self.session_id,
                        reason=(
                            invalid_evidence_disposition
                            or f"pre_capture_{disposition}"
                        ),
                    )
                self.closed = True
                _writer_stage(WriterStage.AFTER_CLOSED_BEFORE_HANDLER_UNREGISTER)
                if self.slot == "post":
                    _writer_stage(
                        WriterStage.AFTER_POST_FINALIZATION_BEFORE_TERMINAL_PIN
                    )
                head_pin = (
                    None
                    if self.slot == "pre" and disposition == "valid"
                    else terminal_head_pin_for_session(
                        self.ledger_path, session_id=self.session_id
                    )
                )
                if self.slot == "post":
                    _writer_stage(WriterStage.AFTER_TERMINAL_PIN_BEFORE_OUTPUT)
                return receipt, head_pin
            receipt = finalize_attempt_receipt(
                self.ledger_path,
                attempt_id=self.attempt_id,
                disposition=disposition,
                custody_locator=self.custody_locator,
                artifact_sha256=artifacts,
                identity_epoch=self.identity_epoch,
                t1_bindings=self.t1_bindings,
                capture_wall_time_s=self.capture_wall_time_s,
                exact_bound_lexeme_s=self.exact_bound_lexeme_s,
            )
            _writer_stage(WriterStage.FINALIZATION_RETURNED_BEFORE_CLOSED)
            self.closed = True
            _writer_stage(WriterStage.AFTER_CLOSED_BEFORE_HANDLER_UNREGISTER)
            return receipt, head_pin_for_receipt(receipt)
        finally:
            self.writer_lease.release()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-live",
        action="store_true",
        help="explicitly confirm a lead-owned quiet-machine live run",
    )
    parser.add_argument(
        "--arm-countdown-s",
        type=float,
        default=0.0,
        help="count down only after the enforcing pre-slot gate owns the writer lease",
    )
    parser.add_argument(
        "--sleep-display-before-capture",
        action="store_true",
        help="run pmset displaysleepnow under the held writer lease after countdown",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "runs" / "instrument_validation",
    )
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH)
    parser.add_argument(
        "--sampler-binary",
        type=Path,
        default=Path(POWER_METRICS),
        help="powermetrics-compatible sampler executable",
    )
    parser.add_argument(
        "--sampler-ready-timeout-s", type=float, default=15.0
    )
    parser.add_argument("--rollover-timeout-s", type=float, default=15.0)
    parser.add_argument(
        "--display-arm-binary", type=Path, default=Path("/usr/bin/pmset")
    )
    parser.add_argument(
        "--sampler-direct-for-test", action="store_true", help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--time-scale-for-test", type=float, default=1.0, help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--projection-cell-budget-for-test",
        type=int,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--identity-epoch-json-for-test",
        type=Path,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--test-writer-crash-authorization",
        type=Path,
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--rederive-from", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pulse-count", type=int, default=PULSE_COUNT)
    parser.add_argument(
        "--session-id",
        help="predeclared two-slot bracket session id (requires --slot and --attempt-id)",
    )
    parser.add_argument(
        "--slot",
        choices=BRACKET_SESSION_SLOTS,
        help="exact predeclared bracket slot to capture",
    )
    parser.add_argument(
        "--attempt-id",
        help="exact attempt id already reserved for the bracket slot",
    )
    parser.add_argument(
        "--power-policy",
        default=None,
        help="operator-recorded power policy identity (e.g. 'ac_high_power'); required",
    )
    args = parser.parse_args(argv)
    _configure_writer_crash_authorization(
        args.test_writer_crash_authorization,
        entry_point=Path(__file__),
    )
    bracket_values = (args.session_id, args.slot, args.attempt_id)
    bracket_mode = all(value is not None and value != "" for value in bracket_values)
    if any(value is not None for value in bracket_values) and not bracket_mode:
        return emit_refusal(
            RefusalCode.WRITER_BRACKET_ARGUMENTS,
            stream=sys.stderr,
        )
    if bracket_mode and (args.rederive_from is not None or args.output is not None):
        return emit_refusal(
            RefusalCode.WRITER_BRACKET_REDERIVE_CONFLICT,
            stream=sys.stderr,
        )
    if not verify_frozen_protocol():
        return emit_refusal(
            RefusalCode.FROZEN_PROTOCOL_INVALID,
            stream=sys.stderr,
        )
    if args.rederive_from is not None:
        if args.output is None:
            return emit_refusal(
                RefusalCode.REDERIVE_OUTPUT_REQUIRED,
                stream=sys.stderr,
            )
        try:
            payload = rederive_artifact(args.rederive_from, args.output)
        except ValueError as exc:
            return emit_refusal(
                RefusalCode.REDERIVE_FAILED,
                context={"detail": str(exc)},
                stream=sys.stderr,
            )
        print(json.dumps({"status": payload["status"], "output": str(args.output)}))
        return 0 if payload["status"] == "valid" else 1
    if args.output is not None:
        return emit_refusal(
            RefusalCode.OUTPUT_REQUIRES_REDERIVE,
            stream=sys.stderr,
        )
    try:
        launch_authentication = authenticate_calibration_writer_launch_lineage(
            args.output_root,
            session_id=args.session_id,
            slot=args.slot,
            attempt_id=args.attempt_id,
        )
    except ValueError as exc:
        if _calibration_launch_reason_code(exc) is None:
            raise
        return _emit_calibration_launch_refusal(exc)
    if not args.allow_live:
        return emit_refusal(
            RefusalCode.QUIET_MAC_AUTH_REQUIRED,
            stream=sys.stderr,
        )
    if not args.power_policy:
        return emit_refusal(
            RefusalCode.POWER_POLICY_REQUIRED,
            stream=sys.stderr,
        )
    if args.time_scale_for_test <= 0 or args.time_scale_for_test > 1:
        return emit_refusal(
            RefusalCode.WRITER_BRACKET_ARGUMENTS,
            context={"detail": "test time scale must be in (0, 1]"},
            stream=sys.stderr,
        )
    if args.projection_cell_budget_for_test is not None and (
        not args.sampler_direct_for_test
        or args.time_scale_for_test == 1
        or args.identity_epoch_json_for_test is None
        or args.projection_cell_budget_for_test <= 0
        or args.projection_cell_budget_for_test
        > DETECTION_PROJECTION_CELL_BUDGET
    ):
        # Tests may only tighten the production budget inside the existing
        # accelerated synthetic seam. There is no live operator override that
        # can raise, disable, or recover from the frozen fail-closed bound.
        return emit_refusal(
            RefusalCode.WRITER_BRACKET_ARGUMENTS,
            context={"detail": "invalid test-only projection budget"},
            stream=sys.stderr,
        )

    identity_fixture: Mapping[str, Any] = {}
    if args.identity_epoch_json_for_test is not None:
        try:
            loaded_identity = json.loads(
                args.identity_epoch_json_for_test.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("test identity fixture is unreadable") from exc
        if not isinstance(loaded_identity, Mapping):
            raise ValueError("test identity fixture is malformed")
        identity_fixture = loaded_identity
    planned_epoch = {
        "os_build": identity_fixture.get("os_build")
        or _sysctl_identity("kern.osversion"),
        "hardware_model": identity_fixture.get("hardware_model")
        or _sysctl_identity("hw.model"),
        "power_policy": args.power_policy,
        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
        "estimator_revision": RESIDUAL_REGION_METHOD,
        "pulse_protocol_id": PROTOCOL_ID,
    }
    try:
        preflight_systematic_screen_s = _derive_preflight_systematic_screen_s(
            planned_epoch
        )
    except _AcceptancePreflightError as exc:
        return emit_refusal(
            RefusalCode.FROZEN_PROTOCOL_INVALID,
            context={"reason": exc.reason, **exc.context},
            stream=sys.stderr,
        )

    import mlx.core as mx  # noqa: PLC0415

    logical_test_clock = (
        None
        if args.time_scale_for_test == 1
        else _LogicalTestClock(
            float(os.environ.get("JW_FAKE_TIME_ORIGIN", time.time()))
        )
    )
    clock = SystemClock() if logical_test_clock is None else logical_test_clock
    validation_id = (
        args.attempt_id
        if bracket_mode
        else time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    )
    out_dir = args.output_root / validation_id
    custody_locator = normalize_calibration_custody_path(out_dir)
    planned_t1 = _planned_t1_bindings(
        planned_epoch=planned_epoch,
        sampler_binary=args.sampler_binary,
        mlx_version=getattr(mx, "__version__", None),
    )
    # D-109 reservation-first: ordinary captures append here; D-117 bracket
    # captures authenticate the exact slot that the bookend tool already
    # reserved. Both paths run before directory creation, sampler launch, and
    # all hardware capture.
    ledger_lifecycle = _CaptureLedgerLifecycle(
        ledger_path=args.ledger,
        head_pin_path=args.head_pin,
        attempt_id=validation_id,
        custody_locator=custody_locator,
        identity_epoch=planned_epoch,
        t1_bindings=planned_t1,
        session_id=args.session_id if bracket_mode else None,
        slot=args.slot if bracket_mode else None,
    )
    try:
        if bracket_mode and args.slot == "post":
            _writer_stage(WriterStage.BEFORE_POST_DISPATCH)
        ledger_lifecycle.begin()
    except CalibrationLedgerError as exc:
        return emit_refusal(
            exc.code or RefusalCode.LEDGER_MALFORMED,
            context=dict(exc.context) | {"detail": str(exc)},
            stream=sys.stderr,
        )
    try:
        if args.arm_countdown_s < 0:
            raise ValueError("arm countdown must be nonnegative")
        if args.arm_countdown_s or args.sleep_display_before_capture:
            print(
                json.dumps(
                    {
                        "event": "calibration_display_arm_countdown",
                        "seconds": args.arm_countdown_s,
                    }
                ),
                file=sys.stderr,
                flush=True,
            )
            time.sleep(args.arm_countdown_s)
        if args.sleep_display_before_capture:
            subprocess.run(
                [str(args.display_arm_binary), "displaysleepnow"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            time.sleep(5 * args.time_scale_for_test)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        ledger_lifecycle.abandon("display_arm_failed")
        return emit_refusal(
            RefusalCode.DISPLAY_ARM_FAILED,
            context={"detail": str(exc)},
            stream=sys.stderr,
        )

    def finalize_abandoned(
        reason: str = "writer_exit_before_slot_finalization",
    ) -> None:
        """Best effort; a failed closure leaves a fail-closed pending/open state."""

        try:
            ledger_lifecycle.abandon(reason)
        except Exception:  # noqa: BLE001 - pending/open is mandatory fail-closed state
            return

    # An actual interpreter-level uncaught exception/interrupt finalizes when
    # possible. A hard crash between these two appends intentionally leaves
    # ``pending``, which every downstream snapshot refuses.
    _writer_stage(WriterStage.BEFORE_EXIT_HANDLER_REGISTRATION)
    atexit.register(finalize_abandoned)
    _writer_stage(WriterStage.AFTER_EXIT_HANDLER_REGISTRATION)
    (out_dir / "raw").mkdir(parents=True, exist_ok=False)
    _writer_stage(WriterStage.AFTER_CUSTODY_DIRECTORY_CREATION)
    capture_path = out_dir / "raw" / "powermetrics.plist"
    events_path = out_dir / "events.jsonl"
    events = events_path.open("w", encoding="utf-8")
    _writer_stage(WriterStage.AFTER_EVENT_STREAM_OPEN)
    logical_driver = (
        None
        if logical_test_clock is None
        else _LogicalTestPulseDriver(
            logical_test_clock,
            out_dir / ".test-sampler-acks.jsonl",
            timeout_s=args.sampler_ready_timeout_s,
        )
    )
    active_sampler: subprocess.Popen | None = None

    def emit(event_type: str, metadata: dict) -> None:
        sequence = (
            logical_driver.next_sequence(event_type)
            if logical_driver is not None
            and event_type in TEST_LOGICAL_PROTOCOL_EVENTS
            else None
        )
        row = {
            "timestamp_s": clock.now(),
            "event_type": event_type,
            "phase": "instrument_validation",
            "message": event_type,
            "metadata": metadata,
        }
        if sequence is not None:
            row["test_protocol_sequence"] = sequence
        events.write(
            json.dumps(row, sort_keys=True) + "\n"
        )
        events.flush()
        if sequence is not None:
            os.fsync(events.fileno())
            if active_sampler is None:
                raise RuntimeError("test sampler is unavailable for acknowledgement")
            logical_driver.await_acknowledgement(
                active_sampler,
                sequence=sequence,
                event_type=event_type,
            )

    buffers = allocate_matmul_buffers()
    command = ([] if args.sampler_direct_for_test else ["sudo", "-n"]) + [
        str(args.sampler_binary),
        "-b",
        "0",
        "-i",
        str(SAMPLING_INTERVAL_MS),
        "--samplers",
        SAMPLERS,
        "--format",
        "plist",
        "-o",
        str(capture_path),
    ]
    sampler_environment = None
    if logical_driver is not None:
        sampler_environment = os.environ.copy()
        sampler_environment[TEST_LOGICAL_SAMPLER_ACK_ENV] = str(
            logical_driver.acknowledgement_path
        )
        sampler_environment[TEST_LOGICAL_CLOCK_ORIGIN_ENV] = repr(clock.now())
    pre_spawn = clock.stamp()
    with _sampler_lifetime(
        command,
        event_reporter=emit,
        environment=sampler_environment,
    ) as process:
        active_sampler = process
        _writer_stage(WriterStage.AFTER_SAMPLER_SPAWN)
        first_parse = None
        deadline = time.monotonic() + args.sampler_ready_timeout_s
        while time.monotonic() < deadline:
            if capture_path.exists() and capture_path.stat().st_size > 0:
                first_frame = capture_path.read_bytes().split(b"\0", 1)[0]
                if first_frame.strip():
                    try:
                        parse_powermetrics_records(first_frame)
                    except ValueError:
                        pass
                    else:
                        if logical_driver is not None:
                            logical_driver.await_ready(process)
                        first_parse = clock.stamp()
                        break
            time.sleep(
                min(
                    0.05 * args.time_scale_for_test,
                    args.sampler_ready_timeout_s / 4,
                )
            )
        if first_parse is None:
            finalize_abandoned("powermetrics_never_ready")
            return emit_refusal(
                RefusalCode.SAMPLER_NEVER_READY,
                stream=sys.stderr,
            )
        _writer_stage(WriterStage.AFTER_SAMPLER_READY)
        # D-078: wait for a native whole-second rollover before any workload.
        try:
            wait_for_preworkload_rollover(
                capture_path,
                process,
                timeout_s=args.rollover_timeout_s,
                poll_s=min(
                    0.05 * args.time_scale_for_test,
                    args.rollover_timeout_s / 4,
                ),
            )
        except RuntimeError as exc:
            finalize_abandoned(str(exc))
            return emit_refusal(
                RefusalCode.ROLLOVER_GATE_TIMEOUT,
                stream=sys.stderr,
            )
        _writer_stage(WriterStage.AFTER_ROLLOVER_READY)
        sampling_started = clock.stamp()
        emit("sampling_started", {})

        if logical_driver is None:
            time.sleep(BASELINE_S * args.time_scale_for_test)
        else:
            logical_test_clock.advance(BASELINE_S)
        warmups: list[CommandedPulse] = []
        for warmup_index in range(WARMUP_PULSE_COUNT):
            on_stamp = clock.stamp()
            emit(
                "warmup_command_on",
                {"warmup_index": warmup_index, "clock_stamp": asdict(on_stamp)},
            )
            if logical_driver is None:
                run_matmul_pulse(
                    PULSE_DURATION_S * args.time_scale_for_test,
                    buffers,
                )
            else:
                logical_driver.drive_fenced_pulse(buffers)
                logical_test_clock.advance(PULSE_DURATION_S)
            off_stamp = clock.stamp()
            emit(
                "warmup_command_off",
                {"warmup_index": warmup_index, "clock_stamp": asdict(off_stamp)},
            )
            warmups.append(
                CommandedPulse(
                    on_s=on_stamp.epoch_s,
                    off_s=off_stamp.epoch_s,
                    on_uncertainty_s=clock_stamp_half_width_s(on_stamp),
                    off_uncertainty_s=clock_stamp_half_width_s(off_stamp),
                )
            )
            if logical_driver is None:
                time.sleep(1.5 * args.time_scale_for_test)
            else:
                logical_test_clock.advance(1.5)
        if logical_driver is None:
            time.sleep(BASELINE_S * args.time_scale_for_test)
        else:
            logical_test_clock.advance(BASELINE_S)

        # Van der Corput spacing is schedule-relative (offsets start at 0 for the
        # first pulse), so the loop cursor MUST be measured from the pulse-loop
        # start, not from sampling-start (which precedes it by the baseline +
        # warmup + baseline preamble). Measuring elapsed against sampling_started
        # made every gap negative and collapsed the pulses back-to-back.
        pulse_loop_mono0 = (
            time.monotonic() if logical_driver is None else None
        )
        pulse_loop_epoch0 = clock.now() if logical_driver is not None else None
        pulses: list[CommandedPulse] = []
        for raw_on_offset_s, raw_off_offset_s in pulse_schedule(args.pulse_count):
            if logical_driver is None:
                on_offset_s = raw_on_offset_s * args.time_scale_for_test
                off_offset_s = raw_off_offset_s * args.time_scale_for_test
            else:
                on_offset_s = raw_on_offset_s
                off_offset_s = raw_off_offset_s
            _writer_stage(WriterStage.DURING_CAPTURE)
            if logical_driver is not None:
                assert pulse_loop_epoch0 is not None
                logical_test_clock.advance_to(pulse_loop_epoch0 + on_offset_s)
            elif pulses:
                assert pulse_loop_mono0 is not None
                elapsed_s = time.monotonic() - pulse_loop_mono0
                time.sleep(max(0.0, on_offset_s - elapsed_s))
            on_stamp = clock.stamp()
            emit(
                "pulse_command_on",
                {"clock_stamp": asdict(on_stamp), "planned_on_offset_s": on_offset_s},
            )
            if logical_driver is None:
                run_matmul_pulse(
                    PULSE_DURATION_S * args.time_scale_for_test,
                    buffers,
                )
            else:
                logical_driver.drive_fenced_pulse(buffers)
                logical_test_clock.advance_to(pulse_loop_epoch0 + off_offset_s)
            off_stamp = clock.stamp()
            emit(
                "pulse_command_off",
                {"clock_stamp": asdict(off_stamp), "planned_off_offset_s": off_offset_s},
            )
            pulses.append(
                CommandedPulse(
                    on_s=on_stamp.epoch_s,
                    off_s=off_stamp.epoch_s,
                    on_uncertainty_s=clock_stamp_half_width_s(on_stamp),
                    off_uncertainty_s=clock_stamp_half_width_s(off_stamp),
                )
            )
        if logical_driver is None:
            time.sleep(BASELINE_S * args.time_scale_for_test)
        else:
            logical_test_clock.advance(BASELINE_S)
        sampling_stopped = clock.stamp()
        emit("sampling_stopped", {})
        _terminate_powermetrics(process)
        _writer_stage(WriterStage.AFTER_SAMPLER_TEARDOWN)
        post_parse = clock.stamp()
        active_sampler = None

    if logical_driver is not None:
        logical_driver.acknowledgement_path.unlink(missing_ok=True)

    data = capture_path.read_bytes()
    _writer_stage(WriterStage.DURING_RAW_EVENTS_ARTIFACT)
    native_records = parse_powermetrics_records(data)
    evidence, point_anchor_s = _derive_active_capture_clock_evidence(
        stamps={
            "pre_spawn": pre_spawn,
            "first_parse": first_parse,
            "sampling_started": sampling_started,
            "sampling_stopped": sampling_stopped,
            "post_parse": post_parse,
        },
        records=anchor_records_from_powermetrics(native_records),
    )
    anchor_resolved = point_anchor_s is not None
    if not anchor_resolved:
        print(
            "clock_anchor_unresolved: calibration capture cannot be anchored",
            file=sys.stderr,
        )
        # Fail closed: an unanchored capture can never be valid. Native records
        # remain in custody, but the expensive full-resolution projection is
        # skipped and the explicit causal linkage is serialized below.
        anchored = native_records
    else:
        anchored = parse_powermetrics_records(
            data, first_record_endpoint_s=point_anchor_s
        )
    samples = samples_from_records(anchored)
    trace_path = out_dir / "power_trace.csv"
    trace_payload = (
        "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
        + "".join(
            f"{sample.timestamp_s!r},{sample.power_w!r},{sample.source},"
            f"{sample.rail},{sample.interval_start_s!r},{sample.interval_end_s!r}\n"
            for sample in samples
        )
    )
    _write_text_artifact(trace_path, trace_payload, WriterStage.DURING_TRACE_ARTIFACT)

    intervals = [
        TraceInterval(
            start_s=record.timestamp_s - record.elapsed_ns / 1e9,
            end_s=record.timestamp_s,
            power_w=record.rail_power_w["gpu_power"],
        )
        for record in anchored
    ]
    detection = detect_pulses(
        trim_trace_after_warmups(intervals, warmups),
        pulses,
        trace_anchor_bound_s=(
            float(evidence["clock_anchor"]["effective_clock_anchor_bound_s"])
            if anchor_resolved
            else 0.0
        ),
        projection_cell_budget=(
            args.projection_cell_budget_for_test
            if args.projection_cell_budget_for_test is not None
            else DETECTION_PROJECTION_CELL_BUDGET
        ),
        projection_bypass_reason=(
            None if anchor_resolved else CLOCK_ANCHOR_UNRESOLVED
        ),
    )
    detection = _label_active_capture_detection(detection, evidence)
    events.close()

    if launch_authentication is not None:
        try:
            launch_authentication = reconcile_calibration_writer_launch_lineage(
                launch_authentication,
                args.output_root,
                session_id=args.session_id,
                slot=args.slot,
                attempt_id=args.attempt_id,
            )
        except ValueError as exc:
            if _calibration_launch_reason_code(exc) is None:
                raise
            finalize_abandoned(_calibration_launch_reason_code(exc) or "")
            atexit.unregister(finalize_abandoned)
            return _emit_calibration_launch_refusal(exc)

    device_meta = native_records[0].metadata if native_records else {}
    bindings = {
        "hardware_model": device_meta.get("hw_model"),
        "os_build": device_meta.get("kern_osversion"),
        "powermetrics_sha256": sha256_path(args.sampler_binary),
        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
        "anchor_method_version": evidence["clock_anchor"].get("method"),
        "mlx_version": getattr(mx, "__version__", None),
        "pulse_protocol_id": PROTOCOL_ID,
        "power_policy": args.power_policy,
        "estimator_revision": RESIDUAL_REGION_METHOD,
        "protocol_sha256": sha256_path(PROTOCOL_PATH),
    }
    ledger_lifecycle.identity_epoch = {
        field: bindings.get(field)
        for field in (
            "os_build",
            "hardware_model",
            "power_policy",
            "sampling_interval_ms",
            "estimator_revision",
            "pulse_protocol_id",
        )
    }
    ledger_lifecycle.t1_bindings = bindings
    ledger_lifecycle.capture_wall_time_s = str(sampling_started.epoch_s)
    evidence_payload = instrument_evidence(
        detection,
        bindings=bindings,
        validation_id=validation_id,
        artifact_sha256={
            "raw/powermetrics.plist": sha256_path(capture_path),
            "events.jsonl": sha256_path(events_path),
            "power_trace.csv": sha256_path(trace_path),
        },
        capture_wall_time_s=sampling_started.epoch_s,
        launch_lineage=(
            launch_authentication["launch_lineage"]
            if launch_authentication is not None
            else None
        ),
    )
    evidence_payload["clock_anchor"] = evidence["clock_anchor"]
    evidence_payload["clock_anchor_resolved"] = anchor_resolved
    if not anchor_resolved:
        evidence_payload["status"] = "invalid"
        evidence_payload["reasons"] = sorted(
            set(evidence_payload.get("reasons", [])) | {"clock_anchor_unresolved"}
        )
    _write_text_artifact(
        out_dir / "instrument_evidence.json",
        json.dumps(evidence_payload, indent=2, sort_keys=True) + "\n",
        WriterStage.DURING_EVIDENCE_ARTIFACT,
    )
    manifest = {
        "schema_version": "joulewise.instrument_validation_manifest.v1",
        "validation_id": validation_id,
        "protocol_id": PROTOCOL_ID,
        "pulse_count": args.pulse_count,
        "artifacts": {
            name: sha256_path(out_dir / name)
            for name in (
                "events.jsonl",
                "power_trace.csv",
                "instrument_evidence.json",
            )
        }
        | {"raw/powermetrics.plist": sha256_path(capture_path)},
    }
    _write_text_artifact(
        out_dir / "manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        WriterStage.DURING_MANIFEST_ARTIFACT,
    )
    _writer_stage(WriterStage.ARTIFACTS_COMPLETE_BEFORE_FINALIZATION)
    serialized_evidence = json.loads(
        json.dumps(evidence_payload, sort_keys=True),
        parse_float=str,
        parse_int=str,
    )
    bound_lexeme = serialized_evidence.get("b_fiducial_s")
    ledger_lifecycle.exact_bound_lexeme_s = (
        bound_lexeme if isinstance(bound_lexeme, str) else None
    )
    disposition = "ordinary-invalid"
    if evidence_payload["status"] == "valid":
        disposition = (
            "systematic-invalid"
            if isinstance(bound_lexeme, str)
            and Decimal(bound_lexeme) > preflight_systematic_screen_s
            else "valid"
        )
    try:
        _final_receipt, head_pin_candidate = ledger_lifecycle.finalize(
            disposition,
            invalid_evidence_disposition=detection.projection_disposition,
        )
    except CalibrationLedgerError as exc:
        if exc.code == RefusalCode.FINALIZATION_BINDING_CONFLICT:
            # Binding conflict is corruption evidence.  Do not let the generic
            # atexit abort mutate the open session underneath it. Other writer
            # failures retain their automatic governed-abort handler.
            atexit.unregister(finalize_abandoned)
        return emit_refusal(
            exc.code or RefusalCode.LEDGER_MALFORMED,
            context=dict(exc.context) | {"detail": str(exc)},
            stream=sys.stderr,
        )
    atexit.unregister(finalize_abandoned)
    output = {
        "validation_id": validation_id,
        "status": evidence_payload["status"],
        "b_fiducial_s": evidence_payload["b_fiducial_s"],
        "output": str(out_dir),
        "ledger_head_pin_candidate": head_pin_candidate,
        "claim_evaluation_blocked_until_pin_commit": True,
    }
    if bracket_mode:
        output["bracket_session"] = {
            "session_id": args.session_id,
            "slot": args.slot,
            "attempt_id": args.attempt_id,
        }
    if detection.projection_disposition is not None:
        output["invalid_evidence_disposition"] = (
            detection.projection_disposition
        )
        output["detection_projection"] = evidence_payload[
            "detection_projection"
        ]
    if bracket_mode and args.slot == "pre":
        _writer_stage(WriterStage.AFTER_PRE_FINALIZATION_BEFORE_SUPERVISOR_DISPATCH)
    print(json.dumps(output, indent=2))
    return 0 if disposition == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
