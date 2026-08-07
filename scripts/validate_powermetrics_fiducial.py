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
"""

from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import math
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, replace
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.adapters.powermetrics import (  # noqa: E402
    POWER_METRICS,
    SAMPLERS,
    anchor_records_from_powermetrics,
    parse_powermetrics_records,
    samples_from_records,
)
from joulewise.clock import SystemClock  # noqa: E402
from joulewise.calibration_ledger import (  # noqa: E402
    BRACKET_SESSION_OPEN_EVENT,
    BRACKET_SESSION_SCHEMA,
    BRACKET_SESSION_SLOTS,
    DEFAULT_LEDGER_PATH,
    DEFAULT_HEAD_PIN_PATH,
    CalibrationLedgerError,
    abort_bracket_session,
    append_pending_receipt,
    artifact_hashes as ledger_artifact_hashes,
    claim_bracket_session_slot,
    finalize_attempt_receipt,
    finalize_bracket_session_slot,
    head_pin_for_receipt,
    load_calibration_ledger_snapshot,
    terminal_head_pin_for_session,
)
from joulewise.powermetrics_fiducial import (  # noqa: E402
    BASELINE_S,
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
    pulse_schedule,
    run_matmul_pulse,
    trim_trace_after_pulses,
    rederive_detection_from_artifacts,
)
from joulewise.uncertainty_evidence import (  # noqa: E402
    CLOCK_METHOD_V2,
    derive_powermetrics_clock_evidence_v2,
)

PROTOCOL_PATH = (
    REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v3.json"
)
PROTOCOL_V2_PATH = (
    REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v2.json"
)
ROLLOVER_GATE_TIMEOUT_REASON = "pulse_calibration_rollover_gate_timeout"
PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.033558756679900")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    """Best-effort bounded termination for a calibration sampler."""

    process.terminate()
    try:
        process.communicate(timeout=10.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()


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
        raise CalibrationLedgerError(
            "capture does not match the exact reserved bracket session slot"
        )


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
            raise CalibrationLedgerError(
                "bracket session id and slot must be supplied together"
            )
        self.ledger_path = Path(ledger_path)
        self.head_pin_path = Path(head_pin_path)
        self.attempt_id = attempt_id
        self.custody_locator = custody_locator
        self.identity_epoch: Mapping[str, Any] = identity_epoch
        self.t1_bindings: Mapping[str, Any] = t1_bindings
        self.capture_wall_time_s: str | None = None
        self.exact_bound_lexeme_s: str | None = None
        self.session_id = session_id
        self.slot = slot
        self.require_committed_pin = require_committed_pin
        self.claim_id = uuid.uuid4().hex
        self.begun = False
        self.closed = False

    @property
    def is_bracket_session(self) -> bool:
        return self.session_id is not None

    def begin(self) -> None:
        """Reserve ordinarily, or authenticate a previously reserved slot."""

        if self.begun:
            raise CalibrationLedgerError("capture ledger lifecycle already began")
        if self.is_bracket_session:
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
            claim_bracket_session_slot(
                self.ledger_path,
                session_id=self.session_id,
                slot=self.slot,
                attempt_id=self.attempt_id,
                claim_id=self.claim_id,
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
        self.begun = True

    def abandon(self, reason: str) -> Mapping[str, Any] | None:
        """Best-effort governed closure for an interrupted writer."""

        if not self.begun or self.closed:
            return None
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

    def finalize(
        self, disposition: str
    ) -> tuple[Mapping[str, Any], dict[str, Any] | None]:
        """Finalize the exact attempt and return any terminal head candidate."""

        if not self.begun or self.closed:
            raise CalibrationLedgerError("capture ledger lifecycle is not open")
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
            )
            if self.slot == "pre" and disposition != "valid":
                receipt = abort_bracket_session(
                    self.ledger_path,
                    session_id=self.session_id,
                    reason=f"pre_capture_{disposition}",
                )
            self.closed = True
            head_pin = (
                None
                if self.slot == "pre" and disposition == "valid"
                else terminal_head_pin_for_session(
                    self.ledger_path, session_id=self.session_id
                )
            )
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
        self.closed = True
        return receipt, head_pin_for_receipt(receipt)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-live",
        action="store_true",
        help="explicitly confirm a lead-owned quiet-machine live run",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "runs" / "instrument_validation",
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
    bracket_values = (args.session_id, args.slot, args.attempt_id)
    bracket_mode = all(value is not None and value != "" for value in bracket_values)
    if any(value is not None for value in bracket_values) and not bracket_mode:
        print(
            "refusing: --session-id, --slot, and --attempt-id must be supplied together",
            file=sys.stderr,
        )
        return 2
    if bracket_mode and (args.rederive_from is not None or args.output is not None):
        print(
            "refusing: bracket session parameters apply only to live capture",
            file=sys.stderr,
        )
        return 2
    if not verify_frozen_protocol():
        print(
            "refusing: frozen powermetrics fiducial protocol is missing, "
            "incomplete, or disagrees with executable constants",
            file=sys.stderr,
        )
        return 2
    if args.rederive_from is not None:
        if args.output is None:
            print("refusing: --rederive-from requires --output", file=sys.stderr)
            return 2
        try:
            payload = rederive_artifact(args.rederive_from, args.output)
        except ValueError as exc:
            print(f"refusing: {exc}", file=sys.stderr)
            return 2
        print(json.dumps({"status": payload["status"], "output": str(args.output)}))
        return 0 if payload["status"] == "valid" else 1
    if args.output is not None:
        print("refusing: --output requires --rederive-from", file=sys.stderr)
        return 2
    if not args.allow_live:
        print(
            "refusing: live [QUIET-MAC] calibration is lead-owned; "
            "pass --allow-live on a quiet machine",
            file=sys.stderr,
        )
        return 77
    if not args.power_policy:
        print("refusing: --power-policy is a binding field", file=sys.stderr)
        return 2

    import mlx.core as mx  # noqa: PLC0415

    clock = SystemClock()
    validation_id = (
        args.attempt_id
        if bracket_mode
        else time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    )
    out_dir = args.output_root / validation_id
    custody_locator = str(out_dir.resolve())
    planned_epoch = {
        "os_build": _sysctl_identity("kern.osversion"),
        "hardware_model": _sysctl_identity("hw.model"),
        "power_policy": args.power_policy,
        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
        "estimator_revision": RESIDUAL_REGION_METHOD,
        "pulse_protocol_id": PROTOCOL_ID,
    }
    planned_t1 = {
        **planned_epoch,
        "powermetrics_sha256": sha256_path(Path(POWER_METRICS)),
        "anchor_method_version": CLOCK_METHOD_V2,
        "mlx_version": getattr(mx, "__version__", None),
        "protocol_sha256": sha256_path(PROTOCOL_PATH),
    }
    # D-109 reservation-first: ordinary captures append here; D-117 bracket
    # captures authenticate the exact slot that the bookend tool already
    # reserved. Both paths run before directory creation, sampler launch, and
    # all hardware capture.
    ledger_lifecycle = _CaptureLedgerLifecycle(
        ledger_path=DEFAULT_LEDGER_PATH,
        head_pin_path=DEFAULT_HEAD_PIN_PATH,
        attempt_id=validation_id,
        custody_locator=custody_locator,
        identity_epoch=planned_epoch,
        t1_bindings=planned_t1,
        session_id=args.session_id if bracket_mode else None,
        slot=args.slot if bracket_mode else None,
    )
    try:
        ledger_lifecycle.begin()
    except CalibrationLedgerError as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2

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
    atexit.register(finalize_abandoned)
    (out_dir / "raw").mkdir(parents=True, exist_ok=False)
    capture_path = out_dir / "raw" / "powermetrics.plist"
    events_path = out_dir / "events.jsonl"
    events = events_path.open("w", encoding="utf-8")

    def emit(event_type: str, metadata: dict) -> None:
        events.write(
            json.dumps(
                {
                    "timestamp_s": clock.now(),
                    "event_type": event_type,
                    "phase": "instrument_validation",
                    "message": event_type,
                    "metadata": metadata,
                },
                sort_keys=True,
            )
            + "\n"
        )
        events.flush()

    buffers = allocate_matmul_buffers()
    command = [
        "sudo",
        "-n",
        POWER_METRICS,
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
    pre_spawn = clock.stamp()
    process = subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    first_parse = None
    deadline = time.monotonic() + 15.0
    while time.monotonic() < deadline:
        if capture_path.exists() and capture_path.stat().st_size > 0:
            first_frame = capture_path.read_bytes().split(b"\0", 1)[0]
            if first_frame.strip():
                try:
                    parse_powermetrics_records(first_frame)
                except ValueError:
                    pass
                else:
                    first_parse = clock.stamp()
                    break
        time.sleep(0.05)
    if first_parse is None:
        process.terminate()
        finalize_abandoned("powermetrics_never_ready")
        print("powermetrics never became ready", file=sys.stderr)
        return 1
    # D-078: wait for a native whole-second rollover before any workload.
    try:
        wait_for_preworkload_rollover(capture_path, process)
    except RuntimeError as exc:
        events.close()
        finalize_abandoned(str(exc))
        print(f"refusing: {exc}", file=sys.stderr)
        return 1
    sampling_started = clock.stamp()
    emit("sampling_started", {})

    time.sleep(BASELINE_S)
    warmups: list[CommandedPulse] = []
    for warmup_index in range(WARMUP_PULSE_COUNT):
        on_stamp = clock.stamp()
        emit(
            "warmup_command_on",
            {"warmup_index": warmup_index, "clock_stamp": asdict(on_stamp)},
        )
        run_matmul_pulse(PULSE_DURATION_S, buffers)
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
        time.sleep(1.5)
    time.sleep(BASELINE_S)

    # Van der Corput spacing is schedule-relative (offsets start at 0 for the
    # first pulse), so the loop cursor MUST be measured from the pulse-loop
    # start, not from sampling-start (which precedes it by the baseline +
    # warmup + baseline preamble). Measuring elapsed against sampling_started
    # made every gap negative and collapsed the pulses back-to-back.
    pulse_loop_mono0 = time.monotonic()
    pulses: list[CommandedPulse] = []
    for on_offset_s, off_offset_s in pulse_schedule(args.pulse_count):
        if pulses:
            elapsed_s = time.monotonic() - pulse_loop_mono0
            time.sleep(max(0.0, on_offset_s - elapsed_s))
        on_stamp = clock.stamp()
        emit(
            "pulse_command_on",
            {"clock_stamp": asdict(on_stamp), "planned_on_offset_s": on_offset_s},
        )
        run_matmul_pulse(PULSE_DURATION_S, buffers)
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
    time.sleep(BASELINE_S)
    sampling_stopped = clock.stamp()
    emit("sampling_stopped", {})
    _terminate_powermetrics(process)
    post_parse = clock.stamp()

    data = capture_path.read_bytes()
    native_records = parse_powermetrics_records(data)
    evidence, point_anchor_s = derive_powermetrics_clock_evidence_v2(
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
        # Fail closed: an unanchored capture can never be a valid calibration.
        # Detection still runs against the 1 s-quantized native stamps so the
        # diagnostic artifact records why, but the evidence is forced invalid
        # and the script exits nonzero below.
        anchored = native_records
    else:
        anchored = parse_powermetrics_records(
            data, first_record_endpoint_s=point_anchor_s
        )
    samples = samples_from_records(anchored)
    trace_path = out_dir / "power_trace.csv"
    with trace_path.open("w", encoding="utf-8") as handle:
        handle.write(
            "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
        )
        for sample in samples:
            handle.write(
                f"{sample.timestamp_s!r},{sample.power_w!r},{sample.source},"
                f"{sample.rail},{sample.interval_start_s!r},{sample.interval_end_s!r}\n"
            )

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
    )
    events.close()

    device_meta = native_records[0].metadata if native_records else {}
    bindings = {
        "hardware_model": device_meta.get("hw_model"),
        "os_build": device_meta.get("kern_osversion"),
        "powermetrics_sha256": sha256_path(Path(POWER_METRICS)),
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
    )
    evidence_payload["clock_anchor"] = evidence["clock_anchor"]
    evidence_payload["clock_anchor_resolved"] = anchor_resolved
    if not anchor_resolved:
        evidence_payload["status"] = "invalid"
        evidence_payload["reasons"] = sorted(
            set(evidence_payload.get("reasons", [])) | {"clock_anchor_unresolved"}
        )
    (out_dir / "instrument_evidence.json").write_text(
        json.dumps(evidence_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
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
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
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
            and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
            else "valid"
        )
    _final_receipt, head_pin_candidate = ledger_lifecycle.finalize(disposition)
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
    print(json.dumps(output, indent=2))
    return 0 if disposition == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
