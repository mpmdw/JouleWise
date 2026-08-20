"""Cross-layer D-117 refusal inventory and public-exit witnesses."""

from __future__ import annotations

import ast
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
import errno
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

from joulewise.uncertainty_evidence import ACTIVE_CAPTURE_ANCHOR_METHOD
from joulewise.calibration_exits import (
    REFUSAL_BY_CODE,
    REFUSAL_INVENTORY,
    RefusalCode,
    TerminalResult,
    WitnessClass,
)
import joulewise.calibration_ledger as ledger_module
from scripts import validate_powermetrics_fiducial as validation_script
from joulewise.calibration_ledger import (
    GENESIS_DIGEST,
    GOVERNED_ARTIFACTS,
    LEDGER_SCHEMA,
    CalibrationLedgerError,
    append_bracket_session_receipt,
    canonical_json_bytes,
)
from tests.owned_process_runner import (
    AuthenticatedProgress,
    OwnedProcessResult,
    OwnedPublicProcessRunner,
    PublicExecutionEvidence,
    assert_no_owned_fake_sampler_survivors,
    assert_no_owned_process_group_survivors,
    assert_no_owned_writer_survivors,
    next_execution_order,
    owned_process_group_survivors,
    owned_thread_survivors,
)
from tests.receipt_corpus import ReceiptCorpus


REPO_ROOT = Path(__file__).resolve().parents[1]
RECOVERY_SCRIPT = REPO_ROOT / "scripts" / "recover_calibration_ledger.py"
FIXTURE_ROOT = REPO_ROOT / "tests" / "calibration_exits_fixtures"
GIT_MAINTENANCE_CONTROLS = (
    ("maintenance.auto", "false"),
    ("gc.auto", "0"),
    ("maintenance.autoDetach", "false"),
    ("gc.autoDetach", "false"),
)
_PACK_OBJECTS_ARGV = ("pack-objects", "--quiet", ".git/objects/pack/loose")
_PACK_TERMINAL_EVENTS = frozenset({"atexit", "exit", "signal"})
_RACE_EXERCISED = "RACE_EXERCISED"
_NO_RACE_PRE_WRITE = "NO_RACE_PRE_WRITE"
_TRACE_INCOMPLETE = "TRACE_INCOMPLETE"


@dataclass(frozen=True)
class PackTraceEvidence:
    """Complete child-owned Trace2 evidence for one loose-object packer."""

    events: tuple[dict[str, object], ...]
    child_sid: str | None
    terminal_event: dict[str, object] | None
    complete: bool


def _read_complete_trace_events(
    path: Path,
) -> tuple[tuple[dict[str, object], ...], bool]:
    """Read newline-terminated Trace2 records, retaining a partial tail.

    The file is reread on each poll, so bytes after the last newline remain
    available for the next attempt instead of being parsed or discarded.
    """

    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return (), False
    final_record_incomplete = bool(raw) and not raw.endswith(b"\n")
    complete_lines = raw.split(b"\n")
    if final_record_incomplete:
        complete_lines.pop()
    elif complete_lines and complete_lines[-1] == b"":
        complete_lines.pop()
    events: list[dict[str, object]] = []
    for line in complete_lines:
        if not line:
            continue
        event = json.loads(line)
        if not isinstance(event, dict):
            raise ValueError("Trace2 record is not a JSON object")
        events.append(event)
    return tuple(events), final_record_incomplete


def _is_pack_objects_start(event: dict[str, object]) -> bool:
    argv = event.get("argv")
    return (
        event.get("event") == "start"
        and isinstance(argv, list)
        and len(argv) == len(_PACK_OBJECTS_ARGV) + 1
        and isinstance(argv[0], str)
        and Path(argv[0]).name == "git"
        and tuple(argv[1:]) == _PACK_OBJECTS_ARGV
    )


def _pack_trace_evidence(
    events: tuple[dict[str, object], ...],
    *,
    final_record_incomplete: bool = False,
    timed_out: bool = False,
) -> PackTraceEvidence:
    child_sids = {
        event.get("sid")
        for event in events
        if _is_pack_objects_start(event) and isinstance(event.get("sid"), str)
    }
    child_sid = next(iter(child_sids)) if len(child_sids) == 1 else None
    terminal_events = tuple(
        event
        for event in events
        if child_sid is not None
        and event.get("sid") == child_sid
        and event.get("event") in _PACK_TERMINAL_EVENTS
    )
    terminal_event = terminal_events[-1] if terminal_events else None
    return PackTraceEvidence(
        events=events,
        child_sid=child_sid,
        terminal_event=terminal_event,
        complete=(
            child_sid is not None
            and terminal_event is not None
            and not final_record_incomplete
            and not timed_out
        ),
    )


def _wait_for_pack_terminal(
    path: Path,
    deadline_s: float = 2.0,
) -> PackTraceEvidence:
    """Poll until the exact pack-objects child emits its own terminal event."""

    deadline = time.monotonic() + deadline_s
    events: tuple[dict[str, object], ...] = ()
    final_record_incomplete = False
    while True:
        events, final_record_incomplete = _read_complete_trace_events(path)
        evidence = _pack_trace_evidence(
            events,
            final_record_incomplete=final_record_incomplete,
        )
        if evidence.complete:
            return evidence
        remaining_s = deadline - time.monotonic()
        if remaining_s <= 0:
            return _pack_trace_evidence(
                events,
                final_record_incomplete=final_record_incomplete,
                timed_out=True,
            )
        time.sleep(min(0.01, remaining_s))


def _event_timestamp(event: dict[str, object]) -> float | None:
    value = event.get("time")
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _classify_pack_cleanup(
    evidence: PackTraceEvidence,
    *,
    cleanup_started_s: float,
    cleanup_finished_s: float,
    raw_enotempty: bool,
) -> str:
    """Classify cleanup using only the pack child's own Trace2 region."""

    if not evidence.complete or evidence.child_sid is None:
        return _TRACE_INCOMPLETE
    if evidence.terminal_event is None:
        return _TRACE_INCOMPLETE
    terminal_time = _event_timestamp(evidence.terminal_event)
    if terminal_time is None:
        return _TRACE_INCOMPLETE
    if raw_enotempty:
        return _RACE_EXERCISED

    open_regions: list[float] = []
    intervals: list[tuple[float, float]] = []
    for event in evidence.events:
        if (
            event.get("sid") != evidence.child_sid
            or event.get("category") != "pack-objects"
            or event.get("label") != "write-pack-file"
        ):
            continue
        event_name = event.get("event")
        if event_name not in {"region_enter", "region_leave"}:
            continue
        event_time = _event_timestamp(event)
        if event_time is None:
            return _TRACE_INCOMPLETE
        if event_name == "region_enter":
            open_regions.append(event_time)
        elif not open_regions:
            return _TRACE_INCOMPLETE
        else:
            started_s = open_regions.pop()
            if event_time < started_s:
                return _TRACE_INCOMPLETE
            intervals.append((started_s, event_time))
    for started_s in open_regions:
        if terminal_time < started_s:
            return _TRACE_INCOMPLETE
        intervals.append((started_s, terminal_time))
    if any(
        started_s <= cleanup_finished_s and finished_s >= cleanup_started_s
        for started_s, finished_s in intervals
    ):
        return _RACE_EXERCISED
    return _NO_RACE_PRE_WRITE


def tearDownModule() -> None:
    assert_no_owned_writer_survivors()


@dataclass(frozen=True)
class WitnessCase:
    code: RefusalCode
    constructor: str
    observer: str


@dataclass(frozen=True)
class PreservationEvidence:
    code: RefusalCode
    before_fingerprint: dict[str, tuple[object, ...]]
    after_fingerprint: dict[str, tuple[object, ...]]
    before_order: int
    public_process_start_order: int
    public_process_end_order: int
    after_order: int
    observed_code: str


@dataclass(frozen=True)
class WitnessResult:
    """Immutable evidence cached only after the witness sandbox closes."""

    code: RefusalCode
    preservation: PreservationEvidence | None
    public_executions: tuple[PublicExecutionEvidence, ...]


_WITNESS_RESULTS: dict[RefusalCode, WitnessResult] = {}


@dataclass(frozen=True)
class CleanupDiagnostic:
    """One post-quiescence cleanup race, retained even after removal."""

    residual_path: str
    residual_snapshot: tuple[str, ...]
    writers: tuple[str, ...]


class WitnessSandbox:
    """Sole owner of one witness root and every writer created in it."""

    _CLEANUP_BACKOFF_S = (0.01, 0.05, 0.25, 1.0)

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="joulewise-exit-witness-")).resolve()
        self.repo = self.root / "repo"
        self.runner = OwnedPublicProcessRunner(self.root)
        self.cleanup_diagnostics: list[CleanupDiagnostic] = []
        self.closed = False

    def start_owned_writer_thread(
        self,
        target: Callable[[threading.Event], None],
        *,
        label: str,
    ) -> threading.Thread:
        """Start a thread whose stop/join lifecycle precedes root cleanup."""

        return self.runner.start_owned_thread(target, label=label)

    def _residual_snapshot(self) -> tuple[str, ...]:
        if not self.root.exists():
            return ()
        residual: list[str] = []
        try:
            for path in self.root.rglob("*"):
                try:
                    residual.append(str(path.relative_to(self.root)))
                except ValueError:
                    residual.append(str(path))
                if len(residual) >= 64:
                    residual.append("<snapshot-truncated>")
                    break
        except OSError as exc:
            residual.append(f"<snapshot-error:{type(exc).__name__}:{exc}>")
        return tuple(sorted(residual))

    def _residual_writers(self, failed_path: Path) -> tuple[str, ...]:
        """Best-effort PID/command attribution for a residual path."""

        lsof = shutil.which("lsof")
        if lsof is None:
            return ()
        try:
            completed = subprocess.run(
                [lsof, "-F", "pc", "+D", str(failed_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=1.0,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ()
        writers: list[str] = []
        pid: str | None = None
        for line in completed.stdout.splitlines():
            if line.startswith("p") and line[1:].isdigit():
                pid = line[1:]
            elif line.startswith("c") and pid is not None:
                writers.append(f"pid={pid} command={line[1:] or '<unknown>'}")
        return tuple(writers)

    def _cleanup_root(self) -> None:
        first_error: OSError | None = None
        for attempt in range(len(self._CLEANUP_BACKOFF_S) + 1):
            try:
                shutil.rmtree(self.root)
                break
            except FileNotFoundError:
                break
            except OSError as exc:
                if exc.errno != errno.ENOTEMPTY or exc.filename is None:
                    raise
                reported_path = Path(exc.filename)
                failed_path = (
                    reported_path.resolve(strict=False)
                    if reported_path.is_absolute()
                    else (self.root / reported_path).resolve(strict=False)
                )
                try:
                    failed_path.relative_to(self.root)
                except ValueError:
                    raise exc
                if first_error is None:
                    first_error = exc
                self.cleanup_diagnostics.append(
                    CleanupDiagnostic(
                        residual_path=str(failed_path),
                        residual_snapshot=self._residual_snapshot(),
                        writers=self._residual_writers(failed_path),
                    )
                )
                if attempt >= len(self._CLEANUP_BACKOFF_S):
                    break
                time.sleep(self._CLEANUP_BACKOFF_S[attempt])
        if self.cleanup_diagnostics:
            diagnostic = self.cleanup_diagnostics[0]
            writer = ", ".join(diagnostic.writers) or "undetermined"
            removed = not self.root.exists()
            raise AssertionError(
                "diagnostic-fatal post-quiescence ENOTEMPTY; "
                f"residual_path={diagnostic.residual_path}; writer={writer}; "
                f"best_effort_removed={removed}; snapshots="
                f"{[item.residual_snapshot for item in self.cleanup_diagnostics]!r}"
            ) from first_error

    def close(self) -> None:
        if self.closed:
            return
        # Complete writer quiescence is proved before the only permitted retry class.
        self.runner.close()
        assert_no_owned_fake_sampler_survivors()
        try:
            self._cleanup_root()
        finally:
            self.closed = not self.root.exists()


class PreservationGuard:
    """One universal pre-handler preservation span for a hard-stop witness."""

    def __init__(
        self,
        witness: "PublicGovernedExitWitnessTests",
        code: RefusalCode,
    ) -> None:
        self.witness = witness
        self.code = code
        self.before_fingerprint: dict[str, tuple[object, ...]] | None = None
        self.before_order: int | None = None

    def begin(self) -> None:
        self.before_fingerprint = self.witness._durable_fingerprint()
        self.before_order = next_execution_order()

    def finish(self, completed: OwnedProcessResult) -> None:
        after_fingerprint = self.witness._durable_fingerprint()
        after_order = next_execution_order()
        if self.before_fingerprint is None or self.before_order is None:
            raise AssertionError("preservation baseline was not captured")
        payload = self.witness._json_payload(completed)
        evidence = PreservationEvidence(
            code=self.code,
            before_fingerprint=self.before_fingerprint,
            after_fingerprint=after_fingerprint,
            before_order=self.before_order,
            public_process_start_order=completed.start_order,
            public_process_end_order=completed.end_order,
            after_order=after_order,
            observed_code=str(payload.get("code")),
        )
        self.witness.assertLess(evidence.before_order, evidence.public_process_start_order)
        self.witness.assertLess(
            evidence.public_process_start_order,
            evidence.public_process_end_order,
        )
        self.witness.assertLess(evidence.public_process_end_order, evidence.after_order)
        self.witness.assertEqual(
            evidence.before_fingerprint,
            evidence.after_fingerprint,
            f"{self.code.value} changed durable fingerprint inside refusal handler",
        )
        self.witness.assertEqual(evidence.observed_code, self.code.value)
        self.witness.preservation_evidence = evidence


INTERNAL_UNIT_CODES = frozenset(
    {
        RefusalCode.LEDGER_OFF_LEDGER_ARTIFACT,
        RefusalCode.LEDGER_BRACKET_SLOT_CLAIMED,
        RefusalCode.LEDGER_SNAPSHOT_REQUIRED,
    }
)


WITNESS_CASES = (
    WitnessCase(RefusalCode.LEDGER_MISSING, "_corrupt_missing", "audit"),
    WitnessCase(RefusalCode.LEDGER_MALFORMED, "_corrupt_malformed", "audit"),
    WitnessCase(RefusalCode.LEDGER_CHAIN_CONFLICT, "_corrupt_chain", "audit"),
    WitnessCase(RefusalCode.LEDGER_ATTEMPT_CONFLICT, "_corrupt_attempts", "audit"),
    WitnessCase(RefusalCode.LEDGER_BRACKET_SESSION_CONFLICT, "_corrupt_sessions", "audit"),
    WitnessCase(RefusalCode.LEDGER_CONTENT_CONFLICT, "_corrupt_content", "audit"),
    WitnessCase(RefusalCode.LEDGER_ROLLBACK, "_corrupt_rollback", "audit"),
    WitnessCase(RefusalCode.LEDGER_OPERATION_CONFLICT, "_corrupt_operation", "audit"),
    WitnessCase(RefusalCode.LEDGER_UNGOVERNED_BUSINESS, "_corrupt_ungoverned", "audit"),
    WitnessCase(RefusalCode.LEDGER_CUSTODY_INVALID, "_corrupt_custody", "audit"),
    WitnessCase(RefusalCode.UNSAFE_LOCK_INODE, "_corrupt_lock", "repair"),
    WitnessCase(RefusalCode.PHYSICAL_LEDGER_UNREADABLE, "_corrupt_unreadable_ledger", "inspect"),
    WitnessCase(RefusalCode.LEGACY_JOURNAL_UNREADABLE, "_corrupt_unreadable_journal", "repair"),
    WitnessCase(RefusalCode.LEGACY_JOURNAL_ARCHIVE_CONFLICT, "_corrupt_archive_conflict", "repair"),
    WitnessCase(RefusalCode.LEGACY_JOURNAL_ARCHIVE_FAILED, "_corrupt_archive_failure", "repair"),
    WitnessCase(RefusalCode.INTENT_TARGET_MALFORMED, "_corrupt_intent", "repair"),
    WitnessCase(RefusalCode.RECOVERY_NONCONVERGENT, "_corrupt_nonconvergent", "repair"),
    WitnessCase(RefusalCode.ABANDON_NOT_CLEAN, "_corrupt_abandon_io", "abandon"),
    WitnessCase(RefusalCode.ABANDON_PIN_MISMATCH, "_corrupt_abandon_pin", "abandon"),
    WitnessCase(RefusalCode.HEAD_PIN_UNREADABLE, "_corrupt_unreadable_pin", "abandon"),
    WitnessCase(RefusalCode.HEAD_PIN_MALFORMED, "_corrupt_malformed_pin", "abandon"),
    WitnessCase(RefusalCode.CUSTODY_UNREADABLE, "_corrupt_session_custody", "readiness-pre-slot"),
    WitnessCase(RefusalCode.TAIL_REQUIRES_ABANDON, "_state_tail", "repair"),
    WitnessCase(RefusalCode.CUSTODY_COMPLETE_USE_RESUME, "_state_complete_custody", "readiness-pre-slot"),
    WitnessCase(RefusalCode.CUSTODY_PARTIAL, "_state_partial_custody", "readiness-pre-slot"),
    WitnessCase(RefusalCode.LIVE_WRITER_CONTENTION, "_state_live_writer", "resume-live"),
    WitnessCase(RefusalCode.LEDGER_BRACKET_SESSION_OPEN, "_state_open_for_abort", "audit"),
    WitnessCase(RefusalCode.LEDGER_PENDING, "_state_pending", "audit"),
    WitnessCase(RefusalCode.LEDGER_HEAD_UNCOMMITTED, "_state_head_uncommitted", "audit"),
    WitnessCase(RefusalCode.LEDGER_HEAD_MISMATCH, "_state_head_mismatch", "audit"),
    WitnessCase(RefusalCode.LEDGER_RECOVERY_REQUIRED, "_state_recovery_required", "audit"),
    WitnessCase(RefusalCode.LEDGER_BASELINE_MISSING, "_state_clean", "audit-baseline"),
    WitnessCase(RefusalCode.OBSERVATION_UNCLASSIFIABLE, "_state_unclassifiable", "audit-observations"),
    WitnessCase(RefusalCode.RECOVERY_CREDENTIALS_INVALID, "_state_clean", "repair-credentials"),
    WitnessCase(RefusalCode.ABANDON_CREDENTIALS_INVALID, "_state_tail", "abandon-credentials"),
    WitnessCase(RefusalCode.ABANDON_ACTIVE_INTENT, "_state_recovery_required", "abandon"),
    WitnessCase(RefusalCode.HEAD_PIN_NOT_COMMITTED, "_state_pin_not_committed", "abandon"),
    WitnessCase(RefusalCode.RESERVATION_INPUT_INVALID, "_state_reservation_inputs", "reserve-input"),
    WitnessCase(RefusalCode.RESERVATION_HEAD_MISMATCH, "_state_head_mismatch", "reserve-execute"),
    WitnessCase(RefusalCode.RESERVATION_IDENTITY_CONFLICT, "_state_reservation_conflict", "reserve-execute"),
    WitnessCase(RefusalCode.SESSION_NOT_FOUND, "_state_missing_session", "session-status"),
    WitnessCase(RefusalCode.SESSION_NOT_OPEN, "_state_closed_session", "resume-pre"),
    WitnessCase(RefusalCode.SLOT_ORDER_CONFLICT, "_state_open_for_abort", "resume-post"),
    WitnessCase(RefusalCode.CLAIM_ID_INVALID, "_state_hostile_claim_id", "readiness-pre-slot"),
    WitnessCase(RefusalCode.FINALIZATION_BINDING_CONFLICT, "_state_writer_binding_conflict", "writer-binding-conflict"),
    WitnessCase(RefusalCode.SESSION_NOT_TERMINAL, "_state_open_for_abort", "terminal-pin"),
    WitnessCase(RefusalCode.SESSION_TERMINAL_NOT_HEAD, "_state_terminal_not_head", "terminal-pin"),
    WitnessCase(RefusalCode.PLAN_UNREADABLE, "_state_reservation_inputs", "reserve-plan-unreadable"),
    WitnessCase(RefusalCode.PLAN_HASH_MISMATCH, "_state_reservation_inputs", "reserve-plan-mismatch"),
    WitnessCase(RefusalCode.PRE_RESERVE_NOT_READY, "_state_reservation_conflict", "reserve-execute-new"),
    WitnessCase(RefusalCode.PRE_SLOT_NOT_READY, "_state_pre_slot_not_ready", "readiness-wrong-slot"),
    WitnessCase(RefusalCode.TERMINAL_NOT_READY, "_state_missing_session", "readiness-terminal"),
    WitnessCase(RefusalCode.PIN_ADVANCEMENT_NOT_NEEDED, "_state_clean", "advance-exact"),
    WitnessCase(RefusalCode.PIN_ADVANCEMENT_UNSAFE, "_state_open_for_abort", "advance-current"),
    WitnessCase(RefusalCode.PIN_CANDIDATE_MISMATCH, "_state_closed_session", "advance-wrong"),
    WitnessCase(RefusalCode.RESERVATION_JSON_INVALID, "_state_reservation_inputs", "reserve-json"),
    WitnessCase(RefusalCode.WRITER_BRACKET_ARGUMENTS, "_state_writer_protocol", "writer-bracket-args"),
    WitnessCase(RefusalCode.WRITER_BRACKET_REDERIVE_CONFLICT, "_state_writer_protocol", "writer-rederive-conflict"),
    WitnessCase(RefusalCode.FROZEN_PROTOCOL_INVALID, "_state_writer_protocol_invalid", "writer-quiet"),
    WitnessCase(RefusalCode.REDERIVE_OUTPUT_REQUIRED, "_state_writer_protocol", "writer-rederive-output"),
    WitnessCase(RefusalCode.REDERIVE_FAILED, "_state_writer_protocol", "writer-rederive-failed"),
    WitnessCase(RefusalCode.OUTPUT_REQUIRES_REDERIVE, "_state_writer_protocol", "writer-output"),
    WitnessCase(RefusalCode.QUIET_MAC_AUTH_REQUIRED, "_state_writer_protocol", "writer-quiet"),
    WitnessCase(RefusalCode.POWER_POLICY_REQUIRED, "_state_writer_protocol", "writer-power"),
    WitnessCase(RefusalCode.RESERVED_SLOT_MISMATCH, "_state_reserved_mismatch", "validate-slot"),
    WitnessCase(RefusalCode.DISPLAY_ARM_FAILED, "_state_display_abort", "writer-display-failure"),
    WitnessCase(RefusalCode.SAMPLER_NEVER_READY, "_state_sampler_abort", "writer-sampler-failure"),
    WitnessCase(RefusalCode.ROLLOVER_GATE_TIMEOUT, "_state_rollover_abort", "writer-rollover-failure"),
)


def _fresh_cli_env() -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def _install_wall_derived_sampler_mutation(repo: Path) -> Path:
    """Install the rejected elapsed-wall fixture for the P3 mutation check."""

    mlx = repo / "mlx"
    mlx.mkdir(exist_ok=True)
    (mlx / "__init__.py").write_text("", encoding="utf-8")
    (mlx / "core.py").write_text(
        """__version__ = 'test-mlx-1'\n
class _Array:\n
    def astype(self, _dtype):\n
        return self\n
class _Random:\n
    def normal(self, _shape):\n
        return _Array()\n
random = _Random()\n
float16 = object()\n
def matmul(_left, _right):\n
    return _Array()\n
def eval(*_values):\n
    return None\n
""",
        encoding="utf-8",
    )
    fixture_root = repo / "writer-fixtures"
    fixture_root.mkdir(exist_ok=True)
    shutil.copy2(
        REPO_ROOT / "tests" / "fixtures" / "powermetrics_sample.plist",
        fixture_root / "powermetrics_sample.plist",
    )
    sampler = fixture_root / "fake_sampler.py"
    sampler.write_text(
        """#!/usr/bin/env python3
import argparse
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import plistlib
import signal
import time
from xml.sax.saxutils import escape

running = True
stop_real_time = None
def stop(_signum, _frame):
    global running, stop_real_time
    stop_real_time = time.time()
    running = False

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-o', required=True)
args, _unknown = parser.parse_known_args()
signal.signal(signal.SIGTERM, stop)
mode = os.environ.get('JW_FAKE_SAMPLER_MODE', 'normal')
output = Path(args.o)
if mode == 'never':
    while running:
        time.sleep(0.001)
    raise SystemExit(0)
frames = [
    plistlib.loads(raw)
    for raw in Path(__file__).with_name('powermetrics_sample.plist').read_bytes().split(b'\\0')
    if raw.strip()
]
base = frames[0]
target_interval_s = int(os.environ.get('JW_FAKE_SAMPLER_ELAPSED_NS', '100000000')) / 1_000_000_000
time_scale = float(os.environ.get('JW_FAKE_TIME_SCALE', '1'))
real_epoch_origin = float(os.environ.get('JW_FAKE_TIME_ORIGIN', str(time.time())))
virtual_interval_s = float(
    os.environ.get(
        'JW_FAKE_VIRTUAL_INTERVAL_S',
        str(max(target_interval_s / time_scale, 1 / 64)),
    )
)

def virtual_now():
    observed_real_time = time.time() if stop_real_time is None else stop_real_time
    return real_epoch_origin + ((observed_real_time - real_epoch_origin) / time_scale)

def event_rows():
    events_path = output.parent.parent / 'events.jsonl'
    try:
        event_lines = events_path.read_text().splitlines()
    except OSError:
        return []
    rows = []
    for event_line in event_lines:
        try:
            row = json.loads(event_line)
            rows.append((float(row['timestamp_s']), row.get('event_type')))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
    return rows

def pulse_is_active_at(endpoint, rows):
    active = False
    for timestamp_s, event_type in rows:
        if timestamp_s > endpoint:
            continue
        if event_type in {'pulse_command_on', 'warmup_command_on'}:
            active = True
        elif event_type in {'pulse_command_off', 'warmup_command_off'}:
            active = False
    return active

def document_bytes_at(endpoint, rows):
    pulse_active = pulse_is_active_at(endpoint, rows)
    gpu_power = 30000 if pulse_active else 10000
    elapsed_ns = round(virtual_interval_s * 1_000_000_000)
    timestamp = datetime.fromtimestamp(endpoint, UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>is_delta</key><true/>
<key>kern_bootargs</key><string>{escape(str(base.get('kern_bootargs', '')))}</string>
<key>kern_boottime</key><integer>{int(base.get('kern_boottime', 0))}</integer>
<key>thermal_pressure</key><string>Nominal</string>
<key>hw_model</key><string>{escape(os.environ['JW_FAKE_HW_MODEL'])}</string>
<key>kern_osversion</key><string>{escape(os.environ['JW_FAKE_OS_BUILD'])}</string>
<key>timestamp</key><date>{timestamp}</date>
<key>elapsed_ns</key><integer>{elapsed_ns}</integer>
<key>processor</key><dict>
<key>cpu_power</key><integer>10000</integer>
<key>gpu_power</key><integer>{gpu_power}</integer>
<key>ane_power</key><integer>0</integer>
<key>cpu_energy</key><real>{10000 * virtual_interval_s:.12g}</real>
<key>gpu_energy</key><real>{gpu_power * virtual_interval_s:.12g}</real>
<key>ane_energy</key><real>0.0</real>
</dict></dict></plist>'''.encode()

virtual_endpoint = virtual_now()
capture_start_endpoint = virtual_endpoint

def rewrite_complete_capture(handle):
    rows = event_rows()
    final_endpoint = virtual_now()
    handle.seek(0)
    handle.truncate()
    endpoint = capture_start_endpoint
    rewritten = 0
    while endpoint <= final_endpoint:
        if rewritten:
            handle.write(b'\\0')
        handle.write(document_bytes_at(endpoint, rows))
        rewritten += 1
        endpoint += virtual_interval_s

with output.open('wb', buffering=0) as handle:
    index = 0
    while True:
        endpoints = []
        if index == 0:
            endpoints.append(virtual_endpoint)
        else:
            target_endpoint = virtual_now()
            while (
                virtual_endpoint + virtual_interval_s <= target_endpoint
                and len(endpoints) < 2
            ):
                virtual_endpoint += virtual_interval_s
                endpoints.append(virtual_endpoint)
        rows = event_rows()
        for endpoint in endpoints:
            if index:
                handle.write(b'\\0')
            handle.write(document_bytes_at(endpoint, rows))
            index += 1
        if mode == 'one':
            while running:
                time.sleep(0.001)
            break
        if not running:
            rewrite_complete_capture(handle)
            break
        if virtual_endpoint + virtual_interval_s > virtual_now():
            time.sleep(target_interval_s)
""",
        encoding="utf-8",
    )
    sampler.chmod(0o755)
    return sampler


def _install_fake_writer_dependencies(repo: Path) -> Path:
    """Install bounded process fixtures while keeping the production CLI real."""

    mlx = repo / "mlx"
    mlx.mkdir(exist_ok=True)
    (mlx / "__init__.py").write_text("", encoding="utf-8")
    shutil.copy2(FIXTURE_ROOT / "fake_mlx_core.py", mlx / "core.py")
    fixture_root = repo / "writer-fixtures"
    fixture_root.mkdir(exist_ok=True)
    sampler = fixture_root / "fake_sampler.py"
    shutil.copy2(FIXTURE_ROOT / "fake_sampler.py", sampler)
    sampler.chmod(0o755)
    return sampler


def _rekey_private_writer_acceptance(repo: Path) -> None:
    """Authenticate copied estimator bytes inside a private synthetic repo."""

    acceptance_path = (
        repo
        / "configs"
        / "calibration"
        / "calibration_acceptance_d079_v2_n17_r6.json"
    )
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    estimator_paths = tuple(
        acceptance["prospective_rederivation"][
            "estimator_code_sha256"
        ]
    )
    acceptance["prospective_rederivation"]["estimator_code_sha256"] = {
        relative: hashlib.sha256((repo / relative).read_bytes()).hexdigest()
        for relative in estimator_paths
    }
    acceptance_core = {
        key: value
        for key, value in acceptance.items()
        if key != "derivation_sha256"
    }
    acceptance["derivation_sha256"] = hashlib.sha256(
        json.dumps(
            acceptance_core,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    old_acceptance_sha256 = hashlib.sha256(acceptance_path.read_bytes()).hexdigest()
    acceptance_path.write_text(
        json.dumps(acceptance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    new_acceptance_sha256 = hashlib.sha256(acceptance_path.read_bytes()).hexdigest()
    bracketing_path = repo / "joulewise" / "calibration_bracketing.py"
    bracketing_source = bracketing_path.read_text(encoding="utf-8")
    if bracketing_source.count(old_acceptance_sha256) != 1:
        raise AssertionError("issued acceptance digest pin shape changed")
    bracketing_path.write_text(
        bracketing_source.replace(
            old_acceptance_sha256,
            new_acceptance_sha256,
            1,
        ),
        encoding="utf-8",
    )


class RefusalInventoryTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        assert_no_owned_fake_sampler_survivors()

    def test_generated_contract_projection_and_runbook_anchors_are_fresh(self) -> None:
        contract = (
            REPO_ROOT / "docs" / "contracts" / "calibration_ledger_append.md"
        ).read_text(encoding="utf-8")
        begin = "<!-- BEGIN GENERATED: calibration-refusal-registry -->\n"
        end = "\n<!-- END GENERATED: calibration-refusal-registry -->"
        actual = contract.split(begin, 1)[1].split(end, 1)[0]
        rows = [
            "| Code | Witness class | Component | Phase | Exit ID | Terminal result | Night loss | Witness | Correction surface | Corrected success |",
            "|---|---|---|---|---|---|---:|---|---|---|",
            *[
                "| `{}` | `{}` | {} | {} | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                    record.code.value,
                    record.witness_class.value,
                    record.component,
                    record.phase,
                    record.exit_id,
                    record.terminal_result.value,
                    str(record.night_loss).lower(),
                    record.witness_id,
                    record.correction_surface,
                    record.corrected_success,
                )
                for record in REFUSAL_INVENTORY
            ],
        ]
        self.assertEqual(actual, "\n".join(rows))
        runbook = (REPO_ROOT / "docs" / "phase_2" / "window_runbook.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("D-117 §5 amendment", runbook)
        self.assertIn("D-117 §6 amendment", runbook)
        self.assertIn("D-117 §10 amendment", runbook)
        section_13 = runbook.split("## 13.", 1)[1] if "## 13." in runbook else ""
        self.assertNotIn("D-117 §", section_13)
        for record in REFUSAL_INVENTORY:
            if record.witness_class is WitnessClass.INTERNAL_INVARIANT:
                self.assertEqual(record.runbook_anchor, "")
                self.assertNotIn(record.code.value, runbook.split("## 10.", 1)[1].split("## 11.", 1)[0])
            else:
                self.assertEqual(
                    record.runbook_anchor,
                    "d-117-10-calibration-ledger-refusals-and-governed-exits",
                )

    def test_enum_inventory_and_discovered_executed_witnesses_are_exact_sets_per_class(self) -> None:
        enum_codes = set(RefusalCode)
        inventory_codes = {record.code for record in REFUSAL_INVENTORY}
        self.assertEqual(enum_codes, inventory_codes)
        self.assertEqual(enum_codes, set(REFUSAL_BY_CODE))
        self.assertEqual(len(REFUSAL_INVENTORY), len(enum_codes))
        discovered = {case.code for case in WITNESS_CASES}
        self.assertEqual(len(discovered), len(WITNESS_CASES))
        for witness_class in (
            WitnessClass.OPERATIONAL,
            WitnessClass.CORRUPTION_BACKSTOP,
        ):
            expected = {
                record.code
                for record in REFUSAL_INVENTORY
                if record.witness_class is witness_class
            }
            executed = PublicGovernedExitWitnessTests.execute_cases(
                code
                for code in discovered
                if REFUSAL_BY_CODE[code].witness_class is witness_class
            )
            with self.subTest(witness_class=witness_class.value):
                self.assertEqual(expected, executed)
        internal = {
            record.code
            for record in REFUSAL_INVENTORY
            if record.witness_class is WitnessClass.INTERNAL_INVARIANT
        }
        self.assertEqual(internal, INTERNAL_UNIT_CODES)

    def test_registry_policy_is_complete_and_prior_crash_never_generic_stops(self) -> None:
        terminal_values = {result.value for result in TerminalResult}
        for record in REFUSAL_INVENTORY:
            with self.subTest(code=record.code.value):
                self.assertTrue(record.component)
                self.assertTrue(record.phase)
                self.assertTrue(record.retry_class)
                self.assertTrue(record.exit_id)
                self.assertTrue(record.witness_note)
                if record.exit_id == "correct-preflight":
                    self.assertTrue(record.correction_surface)
                    self.assertTrue(record.corrected_success)
                else:
                    self.assertEqual(record.correction_surface, "")
                    self.assertEqual(record.corrected_success, "")
                if record.witness_class is not WitnessClass.INTERNAL_INVARIANT:
                    self.assertTrue(record.command)
                    self.assertTrue(record.runbook_anchor)
                self.assertIn(record.terminal_result.value, terminal_values)
                if record.prior_crash_reachable:
                    self.assertNotEqual(record.exit_kind, "stop-preserved")

    def test_every_hard_stop_has_pre_handler_preservation_evidence(self) -> None:
        expected = {
            record.code
            for record in REFUSAL_INVENTORY
            if record.witness_class is not WitnessClass.INTERNAL_INVARIANT
            and record.terminal_result is TerminalResult.NIGHT_STOPPED_PRESERVED
        }
        executed = PublicGovernedExitWitnessTests.execute_cases(expected)
        self.assertEqual(executed, expected)
        preserved = {
            code: result.preservation
            for code, result in _WITNESS_RESULTS.items()
            if result.preservation is not None
        }
        self.assertEqual(set(preserved), expected)
        for code, evidence in preserved.items():
            assert evidence is not None
            with self.subTest(code=code.value):
                self.assertEqual(evidence.observed_code, code.value)
                self.assertLess(evidence.before_order, evidence.public_process_start_order)
                self.assertLess(
                    evidence.public_process_start_order,
                    evidence.public_process_end_order,
                )
                self.assertLess(evidence.public_process_end_order, evidence.after_order)
                self.assertEqual(
                    evidence.before_fingerprint,
                    evidence.after_fingerprint,
                )

    def test_correct_preflight_registry_executes_every_correction_surface(self) -> None:
        expected = {
            record.code
            for record in REFUSAL_INVENTORY
            if record.exit_id == "correct-preflight"
        }
        executed = PublicGovernedExitWitnessTests.execute_cases(expected)
        self.assertEqual(executed, expected)
        public_results = {
            code: _WITNESS_RESULTS[code].public_executions for code in expected
        }
        self.assertEqual(set(public_results), expected)
        rederive_codes = {
            RefusalCode.WRITER_BRACKET_REDERIVE_CONFLICT,
            RefusalCode.FROZEN_PROTOCOL_INVALID,
            RefusalCode.REDERIVE_OUTPUT_REQUIRED,
            RefusalCode.REDERIVE_FAILED,
            RefusalCode.OUTPUT_REQUIRES_REDERIVE,
        }
        for code in expected:
            with self.subTest(code=code.value):
                record = REFUSAL_BY_CODE[code]
                self.assertTrue(record.correction_surface)
                self.assertTrue(record.corrected_success)
                evidence = public_results[code]
                expected_count = 2 if code in rederive_codes else 1
                self.assertEqual(
                    len(evidence),
                    expected_count,
                    f"{code.value} missing registered writer execution",
                )
                for item in evidence:
                    self.assertEqual(item.refusal_code, code.value)
                    self.assertEqual(item.registered_surface, record.correction_surface)
                    self.assertEqual(
                        Path(item.resolved_entry_point),
                        (Path(item.cwd) / record.correction_surface).resolve(),
                    )
                    self.assertEqual(item.returncode, 0)
                    self.assertLess(item.start_order, item.end_order)
                if record.corrected_success == "reservation_execute_reserved":
                    item = evidence[-1]
                    self.assertIn("--execute", item.argv)
                    self.assertEqual(item.durable_postcondition["status"], "reserved")
                    self.assertTrue(
                        any(
                            event.get("event")
                            == "calibration_pre_reserve_authorized"
                            for event in item.structured_events
                        )
                    )
                elif record.corrected_success == "terminal_head_pin_emitted":
                    self.assertIn(
                        "terminal_head_pin",
                        evidence[-1].durable_postcondition,
                    )
                else:
                    writer = evidence[-1]
                    self.assertIn("--allow-live", writer.argv)
                    self.assertTrue(writer.durable_postcondition["slot_finalized"])
                    self.assertTrue(
                        any(
                            event.get("event")
                            == "calibration_writer_arm_authorized"
                            for event in writer.structured_events
                        )
                    )
                    if code in rederive_codes:
                        self.assertIn("--rederive-from", evidence[0].argv)
                        self.assertEqual(
                            evidence[0].durable_postcondition["status"],
                            "valid",
                        )

    def test_public_witness_ast_requires_owned_registered_executions(self) -> None:
        public_sources = (
            REPO_ROOT / "tests" / "test_calibration_exits.py",
            REPO_ROOT / "tests" / "test_calibration_writer_crash_matrix.py",
        )
        raw_public_launches: list[str] = []
        for source_path in public_sources:
            tree = ast.parse(source_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                rendered = ast.unparse(node)
                if not (
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "subprocess"
                    and node.func.attr in {"run", "Popen"}
                ):
                    continue
                if any(
                    marker in rendered
                    for marker in (
                        "writer_script",
                        "reserve_script",
                        "validate_powermetrics_fiducial.py",
                        "reserve_calibration_window_bracket.py",
                    )
                ):
                    raw_public_launches.append(
                        f"{source_path.name}:{node.lineno}:{rendered}"
                    )
        self.assertEqual(raw_public_launches, [])

        direct_evidence_construction: list[str] = []
        for source_path in (REPO_ROOT / "tests").glob("*.py"):
            if source_path.name == "owned_process_runner.py":
                continue
            tree = ast.parse(source_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "PublicExecutionEvidence"
                ):
                    direct_evidence_construction.append(
                        f"{source_path.name}:{node.lineno}"
                    )
        self.assertEqual(direct_evidence_construction, [])

        witness_tree = ast.parse(
            (REPO_ROOT / "tests" / "test_calibration_exits.py").read_text(
                encoding="utf-8"
            )
        )
        executor = next(
            node
            for node in ast.walk(witness_tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_execute_case"
        )
        forbidden_shortcuts = [
            f"{node.lineno}:{ast.unparse(node)}"
            for node in ast.walk(executor)
            if isinstance(node, ast.Call)
            and (
                (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "_enforcing_readiness"
                )
                or (
                    isinstance(node.func, ast.Name)
                    and node.func.id == "calibration_readiness"
                )
            )
        ]
        self.assertEqual(forbidden_shortcuts, [])

    def test_public_explain_cli_projects_every_operator_facing_record(self) -> None:
        observed: set[RefusalCode] = set()
        for record in REFUSAL_INVENTORY:
            if record.witness_class is WitnessClass.INTERNAL_INVARIANT:
                continue
            code = record.code
            result = subprocess.run(
                [sys.executable, str(RECOVERY_SCRIPT), "explain", code.value],
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=_fresh_cli_env(),
                check=False,
            )
            with self.subTest(code=code.value):
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(
                    set(payload), {"code", "exit_id", "arm_blocked", "next_command"}
                )
                self.assertEqual(payload["code"], code.value)
                observed.add(RefusalCode(payload["code"]))
        self.assertEqual(
            observed,
            {
                record.code
                for record in REFUSAL_INVENTORY
                if record.witness_class is not WitnessClass.INTERNAL_INVARIANT
            },
        )

    def test_internal_snapshot_argument_guard_raise_path(self) -> None:
        from joulewise.calibration_bracketing import (
            evaluate_calibration_bracket as evaluate,
        )
        from joulewise.schemas import CalibrationBracketingPolicy
        from tests.test_calibration_bracketing import _synthetic_issued_artifact

        artifact = _synthetic_issued_artifact()
        policy = CalibrationBracketingPolicy(
            require_bracket=True,
            calibration_bracket_max_drift_s=0.010,
        )
        with mock.patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            _result, reasons = evaluate(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=policy,
                ledger_snapshot=None,
            )
        self.assertEqual(reasons, (RefusalCode.LEDGER_SNAPSHOT_REQUIRED.value,))

    def test_internal_off_ledger_candidate_guard_raise_path(self) -> None:
        from joulewise.schemas import CalibrationBracketingPolicy
        from tests.test_calibration_bracketing import (
            CalibrationBracketingTests,
            _evaluate_with_unissued_acceptance,
            _fixture_snapshot,
        )

        fixture = CalibrationBracketingTests(methodName="runTest")
        fixture.setUp()
        registered_input = [
            fixture.candidate("pre", 99.0, "0.025"),
            fixture.candidate("post", 111.0, "0.026"),
        ]
        snapshot, registered = _fixture_snapshot(registered_input)
        hostile = replace(
            fixture.candidate("hostile", 105.0, "0.0255"),
            attempt_id="off-ledger",
            content_id="f" * 64,
            ledger_receipt_digest="e" * 64,
        )
        _result, reasons = _evaluate_with_unissued_acceptance(
            [*registered, hostile],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=fixture.bindings,
            policy=CalibrationBracketingPolicy(
                require_bracket=True,
                calibration_bracket_max_drift_s=0.010,
            ),
            ledger_snapshot=snapshot,
            _allow_unissued_fixture=True,
        )
        self.assertEqual(
            reasons, (RefusalCode.LEDGER_OFF_LEDGER_ARTIFACT.value,)
        )

    def test_internal_duplicate_claim_guard_raise_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "ledger.jsonl"
            pin = root / "pin.json"
            pin.write_text(
                json.dumps(
                    {
                        "sequence": 0,
                        "head_digest": GENESIS_DIGEST,
                        "ledger_schema": LEDGER_SCHEMA,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            epoch = {
                "os_build": "25F84",
                "hardware_model": "Mac15,9",
                "power_policy": "ac_high_power",
                "sampling_interval_ms": 100,
                "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
                "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
            }
            t1 = {field: f"value-{field}" for field in ledger_module.T1_FIELDS}
            t1.update(epoch)
            slots = {
                role: {
                    "attempt_id": f"attempt-{role}",
                    "custody_locator": str(
                        root / "instrument_validation" / f"attempt-{role}"
                    ),
                    "identity_epoch": epoch,
                    "t1_bindings": t1,
                }
                for role in ("pre", "post")
            }
            ledger_module.append_bracket_session_receipt(
                ledger,
                session_id="session",
                window_id="window",
                plan_id="plan",
                plan_sha256="a" * 64,
                evidence_root_id="evidence",
                runs_root=root,
                slots=slots,
                head_pin_path=pin,
                require_committed_pin=False,
                repo_root=root,
            )
            ledger_module.claim_bracket_session_slot(
                ledger,
                session_id="session",
                slot="pre",
                attempt_id="attempt-pre",
            )
            receipts = ledger_module._scan_physical_ledger(ledger.read_bytes()).receipts

            def force_inner_guard(_path, build, **_kwargs):
                return build(receipts)

            with mock.patch.object(
                ledger_module, "_locked_append", side_effect=force_inner_guard
            ):
                with self.assertRaises(CalibrationLedgerError) as raised:
                    ledger_module.claim_bracket_session_slot(
                        ledger,
                        session_id="session",
                        slot="pre",
                        attempt_id="attempt-pre",
                    )
            self.assertEqual(
                raised.exception.code, RefusalCode.LEDGER_BRACKET_SLOT_CLAIMED
            )

    def test_low_level_claim_id_argument_guard_supplements_public_witness(self) -> None:
        witness = PublicGovernedExitWitnessTests(methodName="runTest")
        witness.setUp()
        try:
            witness._open_session("session-claim-guard")
            with self.assertRaises(CalibrationLedgerError) as raised:
                ledger_module.claim_bracket_session_slot(
                    witness.ledger,
                    session_id="session-claim-guard",
                    slot="pre",
                    attempt_id="session-claim-guard-pre",
                    claim_id="caller-supplied-invalid-id",
                )
            self.assertEqual(raised.exception.code, RefusalCode.CLAIM_ID_INVALID)
        finally:
            witness.tearDown()

    def test_low_level_finalization_binding_guard_supplements_writer_witness(self) -> None:
        witness = PublicGovernedExitWitnessTests(methodName="runTest")
        witness.setUp()
        try:
            witness._open_session("session-finalization-guard")
            ledger_module.claim_bracket_session_slot(
                witness.ledger,
                session_id="session-finalization-guard",
                slot="pre",
                attempt_id="session-finalization-guard-pre",
            )
            with self.assertRaises(CalibrationLedgerError) as raised:
                ledger_module.finalize_bracket_session_slot(
                    witness.ledger,
                    session_id="session-finalization-guard",
                    slot="pre",
                    disposition="abandoned",
                    custody_locator=str(witness.repo / "wrong-custody"),
                    artifact_sha256={},
                    identity_epoch=witness.epoch,
                    t1_bindings=witness.t1,
                )
            self.assertEqual(
                raised.exception.code, RefusalCode.FINALIZATION_BINDING_CONFLICT
            )
        finally:
            witness.tearDown()

    def test_operational_ast_has_no_free_form_ledger_refusals_or_substring_policy(self) -> None:
        paths = (
            REPO_ROOT / "joulewise" / "calibration_ledger.py",
            REPO_ROOT / "scripts" / "validate_powermetrics_fiducial.py",
            REPO_ROOT / "scripts" / "recover_calibration_ledger.py",
            REPO_ROOT / "scripts" / "reserve_calibration_window_bracket.py",
        )
        operational_functions = {
            "_open_ledger_lock",
            "_repair_locked",
            "inspect_calibration_ledger",
            "repair_calibration_ledger",
            "abandon_calibration_ledger_tail",
            "_locked_append",
            "_authenticated_head_pin",
            "validate_bracket_session_reservation_inputs",
            "append_bracket_session_receipt",
            "claim_bracket_session_slot",
            "finalize_bracket_session_slot",
            "abort_bracket_session",
            "terminal_head_pin_for_session",
            "calibration_session_status",
            "calibration_readiness",
            "advance_calibration_head_pin",
            "resume_finalize_bracket_session",
            "abort_calibration_session",
            "append_pending_receipt",
            "finalize_attempt_receipt",
            "_head_pin_for_valid_receipt",
            "head_pin_for_receipt",
        }
        violations: list[str] = []
        for path in paths:
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("exclusive writer " + "claim", source)
            self.assertNotIn("operation key " + "conflicts", source)
            self.assertNotIn("marker in " + "str(exc)", source)
            self.assertNotIn('print("refusing:', source)
            tree = ast.parse(source)
            parents: dict[ast.AST, ast.AST] = {}
            for parent in ast.walk(tree):
                for child in ast.iter_child_nodes(parent):
                    parents[child] = parent
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                function = node.func
                if not isinstance(function, ast.Name) or function.id != "CalibrationLedgerError":
                    continue
                owner = node
                while owner in parents and not isinstance(
                    owner, (ast.FunctionDef, ast.AsyncFunctionDef)
                ):
                    owner = parents[owner]
                if (
                    path.name == "calibration_ledger.py"
                    and isinstance(owner, ast.FunctionDef)
                    and owner.name not in operational_functions
                ):
                    continue
                if node.args and isinstance(node.args[0], (ast.Constant, ast.JoinedStr)):
                    violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
        self.assertEqual(violations, [])

    def test_calibration_tests_pass_receipt_provenance_gate(self) -> None:
        from tests.receipt_provenance_analyzer import analyze_paths

        paths = sorted((REPO_ROOT / "tests").glob("test_calibration*.py"))
        paths.append(REPO_ROOT / "tests" / "test_powermetrics_fiducial.py")
        self.assertEqual(analyze_paths(paths), [])


class CalibrationExitReliabilityTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str, env=None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def _configure_fixture_repo(self, sandbox: WitnessSandbox) -> None:
        sandbox.repo.mkdir()
        self._git(sandbox.repo, "init", "-q")
        self._git(sandbox.repo, "config", "user.email", "tests@joulewise.invalid")
        self._git(sandbox.repo, "config", "user.name", "JouleWise tests")
        for key, value in GIT_MAINTENANCE_CONTROLS:
            self._git(sandbox.repo, "config", "--local", key, value)

    def test_minimal_git_create_commit_cleanup_cycles_are_bounded(self) -> None:
        cycles = int(os.environ.get("JW_CALEXITS_GIT_CYCLES", "4"))
        self.assertGreater(cycles, 0)
        retries = 0
        longest_cleanup_s = 0.0
        for index in range(cycles):
            sandbox = WitnessSandbox()
            try:
                self._configure_fixture_repo(sandbox)
                global_config = sandbox.root / "aggressive-global.gitconfig"
                for key, value in (
                    ("maintenance.auto", "true"),
                    ("maintenance.autoDetach", "true"),
                    ("maintenance.strategy", "incremental"),
                    ("maintenance.loose-objects.auto", "1"),
                    ("gc.auto", "1"),
                    ("gc.autoDetach", "true"),
                ):
                    subprocess.run(
                        ["git", "config", "-f", str(global_config), key, value],
                        check=True,
                    )
                aggressive_env = dict(os.environ) | {
                    "GIT_CONFIG_GLOBAL": str(global_config)
                }
                (sandbox.repo / "payload").write_text(str(index), encoding="utf-8")
                self._git(sandbox.repo, "add", ".", env=aggressive_env)
                self._git(
                    sandbox.repo,
                    "commit",
                    "-qm",
                    f"cycle-{index}",
                    env=aggressive_env,
                )
            finally:
                started = time.monotonic()
                sandbox.close()
                longest_cleanup_s = max(
                    longest_cleanup_s, time.monotonic() - started
                )
                retries += len(sandbox.cleanup_diagnostics)
        self.assertEqual(retries, 0)
        self.assertLess(longest_cleanup_s, 2.0)
        print(
            f"P1_CYCLES={cycles} RAW_ENOTEMPTY=0 RETRY_EXHAUSTION=0 "
            f"MAX_CLEANUP_S={longest_cleanup_s:.6f}",
            flush=True,
        )

    def test_delayed_object_writers_never_escape_bounded_cleanup(self) -> None:
        sandbox = WitnessSandbox()
        objects = sandbox.repo / ".git" / "objects"
        leaf = objects / "aa"
        leaf.mkdir(parents=True)
        ready = threading.Event()
        stop_observed = threading.Event()
        final_write_complete = threading.Event()

        def inject_writer(stop_requested: threading.Event) -> None:
            # Register the already-scheduled final write before cleanup asks
            # the writer to stop, then finish that write before returning.
            ready.set()
            stop_requested.wait()
            stop_observed.set()
            leaf.mkdir(exist_ok=True)
            (leaf / "already-scheduled-final-write").write_bytes(b"object")
            final_write_complete.set()

        writer = sandbox.start_owned_writer_thread(
            inject_writer,
            label="delayed-git-object-writer",
        )
        self.assertTrue(ready.wait(timeout=5.0))
        self.assertIn("delayed-git-object-writer", owned_thread_survivors())
        real_rmtree = shutil.rmtree

        def rmtree_after_quiescence(path):
            self.assertTrue(
                stop_observed.is_set(),
                "rmtree began before the writer observed its stop request",
            )
            self.assertTrue(
                final_write_complete.is_set(),
                "rmtree began before the already-scheduled final write completed",
            )
            self.assertFalse(
                writer.is_alive(),
                "rmtree began before the owned delayed writer joined",
            )
            return real_rmtree(path)

        started = time.monotonic()
        with mock.patch.object(
            shutil,
            "rmtree",
            side_effect=rmtree_after_quiescence,
        ):
            sandbox.close()
        self.assertTrue(stop_observed.is_set())
        self.assertTrue(final_write_complete.is_set())
        self.assertFalse(writer.is_alive())
        self.assertEqual(owned_thread_survivors(), ())
        self.assertFalse(sandbox.root.exists())
        self.assertLess(time.monotonic() - started, 2.0)
        self.assertEqual(sandbox.cleanup_diagnostics, [])
        print(
            "P1_DELAYED_WRITERS=1 EVENT_GATED_FINAL_WRITES=1 "
            "BOUNDED_RETRIES=0 THREAD_REGISTRY_EMPTY=1 ESCAPED=0",
            flush=True,
        )

    def test_pack_classifier_accepts_child_exit_without_parent_child_exit(
        self,
    ) -> None:
        parent_sid = "parent"
        child_sid = "parent/pack-child"
        events = (
            {
                "event": "start",
                "sid": child_sid,
                "time": "2026-08-11T12:00:00.100000Z",
                "argv": ["/usr/bin/git", *_PACK_OBJECTS_ARGV],
            },
            {
                "event": "exit",
                "sid": child_sid,
                "time": "2026-08-11T12:00:00.200000Z",
                "code": 128,
            },
            {
                "event": "signal",
                "sid": parent_sid,
                "time": "2026-08-11T12:00:00.210000Z",
                "signal": signal.SIGPIPE,
            },
        )
        evidence = _pack_trace_evidence(events)
        self.assertFalse(any(event.get("event") == "child_exit" for event in events))
        self.assertEqual(
            _classify_pack_cleanup(
                evidence,
                cleanup_started_s=datetime.fromisoformat(
                    "2026-08-11T12:00:00.120000+00:00"
                ).timestamp(),
                cleanup_finished_s=datetime.fromisoformat(
                    "2026-08-11T12:00:00.180000+00:00"
                ).timestamp(),
                raw_enotempty=False,
            ),
            _NO_RACE_PRE_WRITE,
        )

    def test_trace_reader_retries_incomplete_final_record(self) -> None:
        with tempfile.TemporaryDirectory(prefix="joulewise-trace-reader-") as root:
            trace = Path(root) / "trace.jsonl"
            first = {"event": "version", "sid": "parent"}
            second = {"event": "start", "sid": "parent/child"}
            first_record = json.dumps(first, separators=(",", ":")).encode("utf-8")
            second_record = json.dumps(second, separators=(",", ":")).encode("utf-8")
            split_at = len(second_record) // 2
            trace.write_bytes(first_record + b"\n" + second_record[:split_at])

            events, incomplete = _read_complete_trace_events(trace)
            self.assertEqual(events, (first,))
            self.assertTrue(incomplete)

            with trace.open("ab") as stream:
                stream.write(second_record[split_at:] + b"\n")
            events, incomplete = _read_complete_trace_events(trace)
            self.assertEqual(events, (first, second))
            self.assertFalse(incomplete)

    def test_pack_classifier_finds_child_write_overlap_without_parent_child_exit(
        self,
    ) -> None:
        parent_sid = "parent"
        child_sid = "parent/pack-child"
        events = (
            {
                "event": "start",
                "sid": child_sid,
                "time": "2026-08-11T12:00:00.100000Z",
                "argv": ["/usr/bin/git", *_PACK_OBJECTS_ARGV],
            },
            {
                "event": "region_enter",
                "sid": child_sid,
                "time": "2026-08-11T12:00:00.130000Z",
                "category": "pack-objects",
                "label": "write-pack-file",
            },
            {
                "event": "region_leave",
                "sid": child_sid,
                "time": "2026-08-11T12:00:00.170000Z",
                "category": "pack-objects",
                "label": "write-pack-file",
            },
            {
                "event": "exit",
                "sid": child_sid,
                "time": "2026-08-11T12:00:00.200000Z",
                "code": 128,
            },
            {
                "event": "signal",
                "sid": parent_sid,
                "time": "2026-08-11T12:00:00.210000Z",
                "signal": signal.SIGPIPE,
            },
        )
        evidence = _pack_trace_evidence(events)
        self.assertFalse(any(event.get("event") == "child_exit" for event in events))
        self.assertEqual(
            _classify_pack_cleanup(
                evidence,
                cleanup_started_s=datetime.fromisoformat(
                    "2026-08-11T12:00:00.140000+00:00"
                ).timestamp(),
                cleanup_finished_s=datetime.fromisoformat(
                    "2026-08-11T12:00:00.160000+00:00"
                ).timestamp(),
                raw_enotempty=False,
            ),
            _RACE_EXERCISED,
        )

    def test_cleanup_retry_is_diagnostic_fatal_after_best_effort_removal(self) -> None:
        sandbox = WitnessSandbox()
        sandbox.repo.mkdir()
        residual = sandbox.repo / ".git" / "objects" / "aa"
        residual.mkdir(parents=True)
        (residual / "object").write_bytes(b"race")
        real_rmtree = shutil.rmtree
        attempts = 0

        def injected_rmtree(path):
            nonlocal attempts
            attempts += 1
            if attempts <= len(WitnessSandbox._CLEANUP_BACKOFF_S):
                raise OSError(errno.ENOTEMPTY, "Directory not empty", residual)
            return real_rmtree(path)

        started = time.monotonic()
        with (
            mock.patch.object(shutil, "rmtree", side_effect=injected_rmtree),
            mock.patch.object(
                sandbox,
                "_residual_writers",
                return_value=("pid=4242 command=git",),
            ),
            self.assertRaisesRegex(
                AssertionError,
                r"diagnostic-fatal.*residual_path=.*objects/aa; "
                r"writer=pid=4242 command=git; best_effort_removed=True",
            ),
        ):
            sandbox.close()
        elapsed = time.monotonic() - started
        self.assertEqual(attempts, 5)
        self.assertEqual(len(sandbox.cleanup_diagnostics), 4)
        self.assertTrue(
            all(
                "repo/.git/objects/aa/object" in diagnostic.residual_snapshot
                for diagnostic in sandbox.cleanup_diagnostics
            )
        )
        self.assertFalse(sandbox.root.exists())
        self.assertTrue(sandbox.closed)
        self.assertLess(elapsed, 2.0)

        outside = WitnessSandbox()
        outside.repo.mkdir()
        with mock.patch.object(
            shutil,
            "rmtree",
            side_effect=OSError(errno.ENOTEMPTY, "Directory not empty", "/tmp/not-owned"),
        ) as refused_retry:
            with self.assertRaises(OSError):
                outside.close()
        refused_retry.assert_called_once()
        real_rmtree(outside.root)

    def test_forced_auto_maintenance_mutation_reproduces_cleanup_race(self) -> None:
        sandbox = WitnessSandbox()
        raw_enotempty: OSError | None = None
        cleanup_diagnostic: AssertionError | None = None
        classifications = {
            _RACE_EXERCISED: 0,
            _NO_RACE_PRE_WRITE: 0,
            _TRACE_INCOMPLETE: 0,
        }

        def report_classifications() -> None:
            print(
                f"RACE_EXERCISED={classifications[_RACE_EXERCISED]} "
                f"NO_RACE_PRE_WRITE={classifications[_NO_RACE_PRE_WRITE]} "
                f"TRACE_INCOMPLETE={classifications[_TRACE_INCOMPLETE]}",
                flush=True,
            )

        self.addCleanup(report_classifications)
        try:
            self._configure_fixture_repo(sandbox)
            global_config = sandbox.root / "aggressive-global.gitconfig"
            for key, value in (
                ("maintenance.auto", "true"),
                ("maintenance.autoDetach", "true"),
                ("maintenance.strategy", "incremental"),
                ("maintenance.gc.enabled", "false"),
                ("maintenance.loose-objects.enabled", "true"),
                ("maintenance.incremental-repack.enabled", "true"),
                ("maintenance.loose-objects.auto", "1"),
                ("gc.auto", "1"),
                ("gc.autoDetach", "true"),
            ):
                subprocess.run(
                    ["git", "config", "-f", str(global_config), key, value],
                    check=True,
                )
            execution_env = dict(os.environ)
            execution_env["GIT_CONFIG_GLOBAL"] = str(global_config)

            for index in range(1500):
                (sandbox.repo / f"controlled-{index}").write_text(
                    str(index), encoding="utf-8"
                )
            controlled_trace = sandbox.root / "controlled-trace.jsonl"
            controlled_env = execution_env | {"GIT_TRACE2_EVENT": str(controlled_trace)}
            self._git(sandbox.repo, "add", ".", env=controlled_env)
            self._git(
                sandbox.repo,
                "commit",
                "-qm",
                "maintenance-controlled",
                env=controlled_env,
            )
            controlled_events = [
                json.loads(line)
                for line in controlled_trace.read_text(encoding="utf-8").splitlines()
            ]
            self.assertFalse(
                any(
                    event.get("event") == "child_start"
                    and "maintenance" in event.get("argv", ())
                    for event in controlled_events
                )
            )

            # Required mutation: remove exactly the local controls.  The same
            # aggressive global settings must now launch detached maintenance.
            for key, _value in GIT_MAINTENANCE_CONTROLS:
                self._git(sandbox.repo, "config", "--local", "--unset-all", key)
            (sandbox.repo / "mutation").write_text("race", encoding="utf-8")
            with tempfile.TemporaryDirectory(
                prefix="joulewise-maintenance-trace-"
            ) as trace_tmp:
                mutation_trace = Path(trace_tmp) / "mutation-trace.jsonl"
                mutation_env = execution_env | {
                    "GIT_TRACE2_EVENT": str(mutation_trace)
                }
                self._git(sandbox.repo, "add", ".", env=mutation_env)
                self._git(
                    sandbox.repo,
                    "commit",
                    "-qm",
                    "maintenance-control-removal-mutation",
                    env=mutation_env,
                )
                # The target mutation is the immediate raw teardown attempted
                # as soon as the commit returns, before trace parsing adds
                # enough delay for the detached object writer to disappear.
                cleanup_started_s = time.time()
                try:
                    shutil.rmtree(sandbox.root)
                except OSError as exc:
                    raw_enotempty = exc
                cleanup_finished_s = time.time()
                pack_evidence = _wait_for_pack_terminal(mutation_trace)
                mutation_events = pack_evidence.events
            detached_starts = [
                event
                for event in mutation_events
                if event.get("event") == "child_start"
                and event.get("argv", ())[:2] == ["git", "maintenance"]
                and "--detach" in event.get("argv", ())
            ]
            self.assertTrue(detached_starts, mutation_events[-20:])
        finally:
            if sandbox.root.exists():
                try:
                    sandbox.close()
                except AssertionError as exc:
                    cleanup_diagnostic = exc
                    if sandbox.root.exists():
                        raise
            else:
                sandbox.closed = True
        if raw_enotempty is not None:
            self.assertEqual(raw_enotempty.errno, errno.ENOTEMPTY)
        classification = _classify_pack_cleanup(
            pack_evidence,
            cleanup_started_s=cleanup_started_s,
            cleanup_finished_s=cleanup_finished_s,
            raw_enotempty=raw_enotempty is not None,
        )
        classifications[classification] += 1
        self.assertEqual(sum(classifications.values()), 1)
        self.assertEqual(
            classifications[_TRACE_INCOMPLETE],
            0,
            mutation_events[-20:],
        )
        self.assertEqual(
            classifications[_RACE_EXERCISED]
            + classifications[_NO_RACE_PRE_WRITE],
            1,
        )
        self.assertFalse(sandbox.root.exists())
        print(
            f"RAW_ENOTEMPTY={getattr(raw_enotempty, 'errno', 0)} "
            f"FATAL_RETRY_DIAGNOSTIC={int(cleanup_diagnostic is not None)} "
            f"CONTROLS_MUTATION={classification}",
            flush=True,
        )

    def test_process_ownership_cycles_reach_esrch_and_empty_registry(self) -> None:
        cycles = int(os.environ.get("JW_CALEXITS_OWNERSHIP_CYCLES", "4"))
        self.assertGreater(cycles, 0)
        timeout_cycles = 0
        exception_cycles = 0
        for index in range(cycles):
            sandbox = WitnessSandbox()
            sandbox.repo.mkdir()
            ready = sandbox.root / "ready.json"
            entry_point = sandbox.repo / "ownership_cycle.py"
            entry_point.write_text(
                "\n".join(
                    (
                        "import json, os, signal, subprocess, sys, time",
                        "child = subprocess.Popen([sys.executable, '-c', "
                        "'import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(60)'])",
                        f"open({str(ready)!r}, 'w').write(json.dumps({{'parent': os.getpid(), 'child': child.pid}}))",
                        "print('READY', flush=True)",
                        "time.sleep(60)",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            if index % 2 == 0:
                with self.assertRaises(subprocess.TimeoutExpired):
                    sandbox.runner.run(
                        [sys.executable, entry_point],
                        cwd=sandbox.repo,
                        env=_fresh_cli_env(),
                        timeout=0.05,
                        readiness_path=ready,
                        readiness_timeout_s=2.0,
                    )
                timeout_cycles += 1
                identities = json.loads(ready.read_text(encoding="utf-8"))
                for pid in identities.values():
                    with self.assertRaises(ProcessLookupError):
                        os.kill(int(pid), 0)
            else:
                process = sandbox.runner.start_owned(
                    [sys.executable, entry_point],
                    cwd=sandbox.repo,
                    env=_fresh_cli_env(),
                    label=f"exception-holder-cycle-{index}",
                )
                assert process.stdout is not None
                self.assertEqual(process.stdout.readline().strip(), "READY")
                try:
                    raise RuntimeError("injected owner exception")
                except RuntimeError:
                    exception_cycles += 1
                finally:
                    sandbox.close()
                with self.assertRaises(ProcessLookupError):
                    os.killpg(process.pid, 0)
            sandbox.close()
        self.assertEqual(owned_process_group_survivors(), ())
        print(
            f"P2_OWNERSHIP_CYCLES={cycles} TIMEOUTS={timeout_cycles} "
            f"EXCEPTIONS={exception_cycles} ESRCH={cycles} REGISTRY_EMPTY=1"
        )

    def _run_event_fixture(self, stop_s: float) -> dict:
        sandbox = WitnessSandbox()
        try:
            custody = sandbox.root / "capture"
            (custody / "raw").mkdir(parents=True)
            origin = 1700000000.0
            events = (
                (origin + 2.0, "sampling_started"),
                (origin + 3.0, "pulse_command_on"),
                (origin + 4.0, "pulse_command_off"),
                (origin + 5.5, "pulse_command_on"),
                (origin + 6.5, "pulse_command_off"),
                (origin + 8.0, "sampling_stopped"),
            )
            (custody / "events.jsonl").write_text(
                "".join(
                    json.dumps(
                        {
                            "timestamp_s": timestamp,
                            "event_type": event_type,
                        },
                        sort_keys=True,
                    )
                    + "\n"
                    for timestamp, event_type in events
                ),
                encoding="utf-8",
            )
            capture = custody / "raw" / "powermetrics.plist"
            result_path = sandbox.root / "result.json"
            env = _fresh_cli_env() | {
                "JW_FAKE_SAMPLER_MODE": "normal",
                "JW_FAKE_HW_MODEL": "Mac15,9",
                "JW_FAKE_OS_BUILD": "25F84",
                "JW_FAKE_TIME_ORIGIN": str(origin),
                "JW_FAKE_TIME_SCALE": "1",
                "JW_FAKE_INITIAL_ENDPOINT": str(origin),
                "JW_FAKE_SAMPLER_RESULT_PATH": str(result_path),
            }
            process = sandbox.runner.start_owned(
                [sys.executable, FIXTURE_ROOT / "fake_sampler.py", "-o", capture],
                cwd=sandbox.root,
                env=env,
                label=f"event-fixture-stop-{stop_s}",
            )
            deadline = time.monotonic() + 2.0
            while not capture.exists():
                if time.monotonic() >= deadline:
                    self.fail("event fixture did not become ready")
                time.sleep(0.001)
            if stop_s:
                os.killpg(process.pid, signal.SIGSTOP)
                time.sleep(stop_s)
                os.killpg(process.pid, signal.SIGCONT)
            time.sleep(0.05)
            os.killpg(process.pid, signal.SIGTERM)
            process.communicate(timeout=2.0)
            # The process exited normally; runner close drops its ESRCH entry.
            sandbox.runner.close()
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertLessEqual(payload["record_count"], 2 + 96 * 4)
            self.assertLess(payload["capture_bytes"], 5_000_000)
            return payload
        finally:
            sandbox.close()

    def test_event_fixture_is_sigstop_invariant_and_wall_mutation_fails(self) -> None:
        durations = tuple(
            float(value)
            for value in os.environ.get(
                "JW_CALEXITS_SIGSTOP_SECONDS", "0,0.01,0.03"
            ).split(",")
        )
        results = [self._run_event_fixture(duration) for duration in durations]
        identities = {
            (
                result["record_count"],
                result["capture_sha256"],
                result["capture_bytes"],
                result["result"],
            )
            for result in results
        }
        self.assertEqual(len(identities), 1)

        # The rejected wall-derived generator is retained only as a mutation:
        # suspension changes its horizon, so the identity predicate fails.
        mutation_payloads = []
        for suspension in (0.0, 0.05):
            sandbox = WitnessSandbox()
            try:
                sandbox.repo.mkdir()
                sampler = _install_wall_derived_sampler_mutation(sandbox.repo)
                custody = sandbox.repo / "mutation" / "attempt"
                (custody / "raw").mkdir(parents=True)
                (custody / "events.jsonl").write_text("", encoding="utf-8")
                capture = custody / "raw" / "powermetrics.plist"
                env = _fresh_cli_env() | {
                    "JW_FAKE_SAMPLER_MODE": "normal",
                    "JW_FAKE_HW_MODEL": "Mac15,9",
                    "JW_FAKE_OS_BUILD": "25F84",
                    "JW_FAKE_TIME_ORIGIN": str(1700000000.0),
                    "JW_FAKE_TIME_SCALE": "0.025",
                    "JW_FAKE_SAMPLER_ELAPSED_NS": "200000",
                }
                process = sandbox.runner.start_owned(
                    [sampler, "-o", capture],
                    cwd=sandbox.repo,
                    env=env,
                    label="wall-derived-mutation",
                )
                deadline = time.monotonic() + 2.0
                while not capture.exists() or capture.stat().st_size == 0:
                    if time.monotonic() >= deadline:
                        self.fail("wall mutation did not become ready")
                    time.sleep(0.001)
                if suspension:
                    os.killpg(process.pid, signal.SIGSTOP)
                    time.sleep(suspension)
                    os.killpg(process.pid, signal.SIGCONT)
                time.sleep(0.02)
                os.killpg(process.pid, signal.SIGTERM)
                process.communicate(timeout=5.0)
                raw = capture.read_bytes()
                mutation_payloads.append(
                    (len(raw.split(b"\0")), hashlib.sha256(raw).hexdigest())
                )
            finally:
                sandbox.close()
        self.assertNotEqual(mutation_payloads[0], mutation_payloads[1])
        print(
            f"P3_SIGSTOP_RUNS={len(durations)} IDENTITY=PASS "
            "WALL_MUTATION=FAILS_IDENTITY",
            flush=True,
        )


class SamplerLifecycleHardeningTests(unittest.TestCase):
    def _deterministic_success_capture(self, *, hardened: bool) -> bytes:
        with tempfile.TemporaryDirectory() as tmp:
            custody = Path(tmp) / "attempt"
            (custody / "raw").mkdir(parents=True)
            origin = 1700000000.0
            rows = (
                (origin + 2.0, "sampling_started"),
                (origin + 3.0, "pulse_command_on"),
                (origin + 4.0, "pulse_command_off"),
                (origin + 5.5, "pulse_command_on"),
                (origin + 6.5, "pulse_command_off"),
                (origin + 8.0, "sampling_stopped"),
            )
            (custody / "events.jsonl").write_text(
                "".join(
                    json.dumps({"timestamp_s": stamp, "event_type": event}, sort_keys=True)
                    + "\n"
                    for stamp, event in rows
                ),
                encoding="utf-8",
            )
            capture = custody / "raw" / "powermetrics.plist"
            command = [sys.executable, str(FIXTURE_ROOT / "fake_sampler.py"), "-o", str(capture)]
            env = _fresh_cli_env() | {
                "JW_FAKE_SAMPLER_MODE": "normal",
                "JW_FAKE_HW_MODEL": "Mac15,9",
                "JW_FAKE_OS_BUILD": "25F84",
                "JW_FAKE_TIME_ORIGIN": str(origin),
                "JW_FAKE_TIME_SCALE": "1",
                "JW_FAKE_INITIAL_ENDPOINT": str(origin),
            }

            def wait_for_complete_capture() -> None:
                deadline = time.monotonic() + 2.0
                while True:
                    try:
                        records = len(capture.read_bytes().split(b"\0"))
                    except OSError:
                        records = 0
                    if records >= 258:
                        return
                    if time.monotonic() >= deadline:
                        self.fail(f"deterministic capture stalled at {records} records")
                    time.sleep(0.001)

            if hardened:
                with mock.patch.dict(os.environ, env, clear=True):
                    with validation_script._sampler_lifetime(command) as process:
                        wait_for_complete_capture()
                        validation_script._terminate_powermetrics(process)
            else:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=env,
                )
                wait_for_complete_capture()
                process.terminate()
                process.communicate(timeout=2.0)
            return capture.read_bytes()

    def test_success_capture_is_byte_identical_to_legacy_termination(self) -> None:
        legacy = self._deterministic_success_capture(hardened=False)
        hardened = self._deterministic_success_capture(hardened=True)
        self.assertEqual(hardened, legacy)
        print(
            f"F4_SUCCESS_CAPTURE_BYTES={len(hardened)} "
            f"SHA256={hashlib.sha256(hardened).hexdigest()} BYTE_IDENTICAL=1",
            flush=True,
        )

    def test_stubborn_direct_child_is_killed_and_reaped_on_every_exit_path(self) -> None:
        exit_paths = ("normal", "return", "exception")
        for exit_path in exit_paths:
            with self.subTest(exit_path=exit_path):
                with tempfile.TemporaryDirectory() as tmp:
                    ready_path = Path(tmp) / "ready"
                    command = [
                        sys.executable,
                        "-c",
                        (
                            "import signal,sys,time; "
                            "signal.signal(signal.SIGTERM,signal.SIG_IGN); "
                            "open(sys.argv[1],'w').write('ready'); "
                            "time.sleep(60)"
                        ),
                        str(ready_path),
                    ]
                    process = None
                    raised = False

                    def exercise_exit_path() -> subprocess.Popen:
                        nonlocal process
                        with validation_script._sampler_lifetime(command) as process:
                            deadline = time.monotonic() + 2.0
                            while not ready_path.exists():
                                if time.monotonic() >= deadline:
                                    self.fail("stubborn direct child did not start")
                                time.sleep(0.001)
                            if exit_path == "return":
                                return process
                            if exit_path == "exception":
                                raise RuntimeError("injected after sampler Popen")
                        return process

                    try:
                        with mock.patch.object(
                            validation_script,
                            "SAMPLER_TERMINATE_TIMEOUT_S",
                            0.05,
                        ):
                            process = exercise_exit_path()
                    except RuntimeError as exc:
                        if str(exc) != "injected after sampler Popen":
                            raise
                        raised = True
                    self.assertEqual(raised, exit_path == "exception")
                    assert process is not None
                    self.assertEqual(process.returncode, -signal.SIGKILL)
                    with self.assertRaises(ProcessLookupError):
                        os.kill(process.pid, 0)
        print(
            "F4_STUBBORN_EXIT_PATHS=3 DIRECT_SIGKILL=3 DIRECT_REAPED=3",
            flush=True,
        )

    def test_detached_grandchild_is_reported_by_post_teardown_census(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sampler_pid_path = root / "sampler.pid"
            detached_sampler = root / "powermetrics_detached_sampler.py"
            detached_sampler.write_text(
                "import signal,time\n"
                "signal.signal(signal.SIGTERM,signal.SIG_IGN)\n"
                "time.sleep(60)\n",
                encoding="utf-8",
            )
            command = [
                sys.executable,
                "-c",
                (
                    "import signal,subprocess,sys,time; "
                    "signal.signal(signal.SIGTERM,signal.SIG_IGN); "
                    "child=subprocess.Popen([sys.executable,sys.argv[1]],"
                    "start_new_session=True); "
                    "open(sys.argv[2],'w').write(str(child.pid)); "
                    "time.sleep(60)"
                ),
                str(detached_sampler),
                str(sampler_pid_path),
            ]
            process = None
            detached_pid: int | None = None
            reported_events: list[tuple[str, dict]] = []
            stderr = io.StringIO()
            try:
                with mock.patch.object(
                    validation_script,
                    "SAMPLER_TERMINATE_TIMEOUT_S",
                    0.05,
                ), mock.patch.object(
                    validation_script.subprocess,
                    "run",
                    side_effect=lambda args, **_kwargs: subprocess.CompletedProcess(
                        args,
                        0,
                        stdout=(
                            f"{detached_pid} Python {sys.executable} "
                            f"{detached_sampler}\n"
                        ),
                    ),
                ), mock.patch.object(validation_script.sys, "stderr", stderr):
                    with validation_script._sampler_lifetime(
                        command,
                        event_reporter=lambda event, metadata: reported_events.append(
                            (event, metadata)
                        ),
                    ) as process:
                        deadline = time.monotonic() + 2.0
                        while not sampler_pid_path.exists():
                            if time.monotonic() >= deadline:
                                self.fail("detached sampler did not start")
                            time.sleep(0.001)
                        detached_pid = int(sampler_pid_path.read_text())
                assert process is not None
                self.assertEqual(process.returncode, -signal.SIGKILL)
                self.assertEqual(
                    [event for event, _metadata in reported_events],
                    [validation_script.SAMPLER_CENSUS_DIAGNOSTIC],
                )
                findings = reported_events[0][1]["findings"]
                self.assertIn(detached_pid, [finding["pid"] for finding in findings])
                self.assertIn(
                    validation_script.SAMPLER_CENSUS_DIAGNOSTIC,
                    stderr.getvalue(),
                )
            finally:
                if detached_pid is not None:
                    try:
                        os.kill(detached_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
        print(
            "F3_DETACHED_TOPOLOGY DIRECT_CHILD_REAPED=1 "
            "DETACHED_GRANDCHILD_CENSUS_REPORTED=1",
            flush=True,
        )


class PublicGovernedExitWitnessTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        assert_no_owned_fake_sampler_survivors()

    def setUp(self) -> None:
        self.sandbox = WitnessSandbox()
        self.addCleanup(self.sandbox.close)
        self.repo = self.sandbox.repo
        self.public_runner = self.sandbox.runner
        self.preservation_evidence: PreservationEvidence | None = None
        self.public_execution_evidence: list[PublicExecutionEvidence] = []
        self.writer_env_overrides: dict[str, str] = {}
        shutil.copytree(REPO_ROOT / "joulewise", self.repo / "joulewise")
        (self.repo / "scripts").mkdir()
        for name in (
            "recover_calibration_ledger.py",
            "validate_powermetrics_fiducial.py",
            "reserve_calibration_window_bracket.py",
        ):
            shutil.copy2(REPO_ROOT / "scripts" / name, self.repo / "scripts" / name)
        protocol = (
            self.repo
            / "configs"
            / "calibration"
            / "powermetrics_fiducial"
            / "protocol_v3.json"
        )
        protocol.parent.mkdir(parents=True)
        for protocol_name in ("protocol_v2.json", "protocol_v3.json"):
            shutil.copy2(
                REPO_ROOT
                / "configs"
                / "calibration"
                / "powermetrics_fiducial"
                / protocol_name,
                protocol.with_name(protocol_name),
            )
        shutil.copy2(
            REPO_ROOT
            / "configs"
            / "calibration"
            / "calibration_acceptance_d079_v2_n17_r6.json",
            self.repo
            / "configs"
            / "calibration"
            / "calibration_acceptance_d079_v2_n17_r6.json",
        )
        _rekey_private_writer_acceptance(self.repo)
        self.pin = self.repo / "configs" / "calibration" / "calibration_ledger_head.json"
        self.pin.parent.mkdir(parents=True, exist_ok=True)
        self.pin.write_text(
            json.dumps(
                {
                    "sequence": 0,
                    "head_digest": GENESIS_DIGEST,
                    "ledger_schema": LEDGER_SCHEMA,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.ledger = self.repo / "runs" / "calibration_observation_ledger.jsonl"
        self.ledger.parent.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "tests@joulewise.invalid"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "JouleWise tests"],
            cwd=self.repo,
            check=True,
        )
        for key, value in GIT_MAINTENANCE_CONTROLS:
            subprocess.run(
                ["git", "config", "--local", key, value],
                cwd=self.repo,
                check=True,
            )
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=self.repo, check=True)
        self.script = self.repo / "scripts" / "recover_calibration_ledger.py"
        self.reserve_script = (
            self.repo / "scripts" / "reserve_calibration_window_bracket.py"
        )
        self.writer_script = (
            self.repo / "scripts" / "validate_powermetrics_fiducial.py"
        )
        self.fake_sampler = _install_fake_writer_dependencies(self.repo)
        self.epoch = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        from joulewise.calibration_ledger import T1_FIELDS

        self.t1 = {field: f"value-{field}" for field in T1_FIELDS}
        self.t1.update(self.epoch)

    @classmethod
    def execute_cases(cls, codes) -> set[RefusalCode]:
        selected = set(codes)
        cases = [case for case in WITNESS_CASES if case.code in selected]
        for case in cases:
            if case.code in _WITNESS_RESULTS:
                print(f"CASE CACHED {case.code.value}", flush=True)
                continue
            print(f"CASE START {case.code.value}", flush=True)
            witness = cls(methodName="runTest")
            setup_complete = False
            try:
                witness.setUp()
                setup_complete = True
                witness._execute_case(case)
            finally:
                if setup_complete:
                    witness.tearDown()
                witness.doCleanups()
            _WITNESS_RESULTS[case.code] = WitnessResult(
                code=case.code,
                preservation=witness.preservation_evidence,
                public_executions=tuple(witness.public_execution_evidence),
            )
            print(f"CASE PASS {case.code.value}", flush=True)
        return selected & set(_WITNESS_RESULTS)

    def tearDown(self) -> None:
        self.sandbox.close()

    def _start_holder(self, holder_code: str) -> subprocess.Popen[str]:
        return self.public_runner.start_owned(
            [sys.executable, "-c", holder_code],
            cwd=self.repo,
            env=_fresh_cli_env(),
            label="calibration-writer-holder",
        )

    def _terminate_and_reap_holder(
        self,
        holder: subprocess.Popen[str],
        *,
        timeout_s: float = 10.0,
    ) -> None:
        self.public_runner.terminate_owned(holder, timeout_s=timeout_s)
        self.assertIsNotNone(holder.poll())

    def _run(self, *args: str) -> OwnedProcessResult:
        return self.public_runner.run(
            [
                sys.executable,
                str(self.script),
                "--ledger",
                str(self.ledger),
                "--head-pin",
                str(self.pin),
                *args,
            ],
            cwd=self.repo,
            env=_fresh_cli_env(),
        )

    def _run_script(
        self,
        script: Path,
        *args: str,
        env: dict[str, str] | None = None,
        crash_stage: str | None = None,
        authorize_crash: bool = False,
        refusal_code: str | None = None,
        registered_surface: str | None = None,
        durable_postcondition=None,
        progress_probe=None,
        progress_reporter=None,
    ) -> OwnedProcessResult:
        return self.public_runner.run(
            [sys.executable, str(script), *args],
            cwd=self.repo,
            env=env or _fresh_cli_env(),
            crash_stage=crash_stage,
            authorize_crash=authorize_crash,
            refusal_code=refusal_code,
            registered_surface=registered_surface,
            durable_postcondition=durable_postcondition,
            progress_probe=progress_probe,
            progress_reporter=progress_reporter,
        )

    def _run_corrected_script(
        self,
        code: RefusalCode,
        script: Path,
        *args: str,
        env: dict[str, str] | None = None,
        durable_postcondition=None,
        progress_probe=None,
        progress_reporter=None,
    ) -> OwnedProcessResult:
        record = REFUSAL_BY_CODE[code]
        completed = self._run_script(
            script,
            *args,
            env=env,
            refusal_code=code.value,
            registered_surface=record.correction_surface,
            durable_postcondition=durable_postcondition,
            progress_probe=progress_probe,
            progress_reporter=progress_reporter,
        )
        evidence = completed.public_evidence
        self.assertIsNotNone(evidence)
        assert evidence is not None
        self.public_execution_evidence.append(evidence)
        return completed

    def _writer_progress_probe(self, state: dict):
        custody = Path(state["custody_locator"])
        known_events = {
            "sampling_started",
            "warmup_command_on",
            "warmup_command_off",
            "pulse_command_on",
            "pulse_command_off",
            "sampling_stopped",
        }

        def probe() -> AuthenticatedProgress:
            ordinal = 0
            stage = "writer-launched"
            if custody.is_dir():
                ordinal = 1
                stage = "custody-created"
            capture = custody / "raw" / "powermetrics.plist"
            try:
                capture_ready = capture.stat().st_size > 0
            except OSError:
                capture_ready = False
            if capture_ready:
                ordinal = 2
                stage = "sampler-ready"
            events_path = custody / "events.jsonl"
            authenticated_events: list[str] = []
            try:
                for line in events_path.read_text(encoding="utf-8").splitlines():
                    row = json.loads(line)
                    event_type = row.get("event_type")
                    if (
                        event_type in known_events
                        and row.get("phase") == "instrument_validation"
                        and row.get("message") == event_type
                        and isinstance(row.get("timestamp_s"), int | float)
                    ):
                        authenticated_events.append(str(event_type))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                pass
            if authenticated_events:
                ordinal = 100 + len(authenticated_events)
                stage = f"event-{authenticated_events[-1]}-{len(authenticated_events)}"
            if (custody / "instrument_evidence.json").is_file():
                ordinal = 1000
                stage = "instrument-evidence-written"
            if (custody / "manifest.json").is_file():
                ordinal = 1001
                stage = "manifest-written"
            return AuthenticatedProgress(ordinal=ordinal, stage=stage)

        return probe

    def _session_status_postcondition(self, state: dict) -> dict[str, object]:
        completed = self._run(
            "session-status",
            "--session-id",
            state["session_id"],
            "--plan",
            str(state["plan"]),
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        slot = state["slot"]
        return {
            "status_surface": "session-status",
            "session_state": payload["session_state"],
            "abort_reason": payload["abort_reason"],
            "slot": slot,
            "slot_finalized": payload["slots"][slot]["finalized"],
        }

    def _reservation_postcondition(self, state: dict) -> dict[str, object]:
        payload = ledger_module.calibration_session_status(
            self.ledger,
            self.pin,
            session_id=state["session_id"],
            plan_path=state["plan"],
            require_committed_pin=True,
            repo_root=self.repo,
        )
        self.assertEqual(payload["session_state"], "open")
        self.assertFalse(payload["slots"]["pre"]["finalized"])
        return {
            "status": "reserved",
            "session_state": payload["session_state"],
            "pre_finalized": payload["slots"]["pre"]["finalized"],
        }

    def _writer_detector_diagnostic(self, state: dict) -> dict[str, object]:
        evidence_path = Path(state["custody_locator"]) / "instrument_evidence.json"
        try:
            payload = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return {"instrument_evidence": "unavailable"}
        pulses = payload.get("pulses")
        undetected = []
        if isinstance(pulses, list):
            undetected = [
                {
                    "pulse_index": pulse.get("pulse_index"),
                    "reasons": pulse.get("reasons"),
                }
                for pulse in pulses
                if isinstance(pulse, dict) and pulse.get("detected") is not True
            ]
        anchor = payload.get("clock_anchor")
        return {
            "status": payload.get("status"),
            "b_fiducial_s": payload.get("b_fiducial_s"),
            "reasons": payload.get("reasons"),
            "clock_anchor_status": (
                anchor.get("status") if isinstance(anchor, dict) else None
            ),
            "undetected_pulses": undetected,
        }

    def _execute_valid_writer(
        self,
        code: RefusalCode,
        state: dict,
    ) -> OwnedProcessResult:
        completed = self._run_corrected_script(
            code,
            self.writer_script,
            *self._writer_capture_args(state),
            env=self._writer_env(state, mode="normal"),
            durable_postcondition=lambda: self._session_status_postcondition(state),
            progress_probe=self._writer_progress_probe(state),
            progress_reporter=lambda update: print(
                f"CASE STAGE {code.value} {update.ordinal} {update.stage}",
                flush=True,
            ),
        )
        self.assertEqual(
            completed.returncode,
            0,
            f"correction={code.value}\n{completed.stdout}{completed.stderr}\n"
            f"detector={json.dumps(self._writer_detector_diagnostic(state), sort_keys=True)}",
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        evidence = completed.public_evidence
        assert evidence is not None
        self.assertEqual(
            evidence.durable_postcondition["session_state"],
            "open",
            evidence.durable_postcondition,
        )
        self.assertTrue(
            any(
                event.get("event") == "calibration_writer_arm_authorized"
                for event in evidence.structured_events
            )
        )
        self.assertTrue(evidence.durable_postcondition["slot_finalized"])
        return completed

    def _json_payload(
        self, completed: subprocess.CompletedProcess[str] | OwnedProcessResult
    ) -> dict:
        objects = [
            json.loads(line)
            for line in (completed.stdout + "\n" + completed.stderr).splitlines()
            if line.strip().startswith("{")
        ]
        payloads = [
            value
            for value in objects
            if isinstance(value, dict) and ("status" in value or "code" in value)
        ]
        self.assertEqual(
            len(payloads),
            1,
            "expected one refusal/authorization payload; "
            f"found {len(payloads)} in {objects!r}",
        )
        return payloads[0]

    def _ensure_preservation_lock(self) -> Path:
        lock = ledger_module._ledger_lock_path(self.ledger)
        try:
            lock.lstat()
        except FileNotFoundError:
            descriptor = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
            os.close(descriptor)
        return lock

    def _durable_fingerprint(self) -> dict[str, tuple[object, ...]]:
        lock = self._ensure_preservation_lock()
        legacy = self.ledger.with_name(f"{self.ledger.name}.append-journal")
        candidates = {
            self.ledger,
            self.pin,
            lock,
            legacy,
            self.ledger.parent,
            self.pin.parent,
            self.repo / "runs",
            self.repo / "custody",
        }
        candidates.update(self.ledger.parent.glob(f"{self.ledger.name}.append-journal*"))
        for root in (self.repo / "runs", self.repo / "custody"):
            if root.exists():
                candidates.update(root.rglob("*"))
        fingerprints: dict[str, tuple[object, ...]] = {}
        for path in sorted(candidates, key=lambda item: str(item)):
            try:
                status = path.lstat()
            except FileNotFoundError:
                fingerprint: tuple[object, ...] = ("absent",)
            else:
                if path.is_symlink():
                    content_digest = hashlib.sha256(
                        os.readlink(path).encode()
                    ).hexdigest()
                elif path.is_file():
                    try:
                        content_digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    except OSError:
                        content_digest = "unreadable"
                elif path.is_dir():
                    try:
                        entries = "\0".join(sorted(entry.name for entry in path.iterdir()))
                        content_digest = hashlib.sha256(entries.encode()).hexdigest()
                    except OSError:
                        content_digest = "unreadable"
                else:
                    content_digest = "special"
                fingerprint = (
                    "present",
                    stat.S_IFMT(status.st_mode),
                    status.st_dev,
                    status.st_ino,
                    status.st_nlink,
                    status.st_size,
                    content_digest,
                )
            try:
                label = str(path.relative_to(self.repo))
            except ValueError:
                label = str(path)
            fingerprints[label] = fingerprint
        return fingerprints

    def _writer_env(self, state: dict, *, mode: str) -> dict[str, str]:
        return {
            **_fresh_cli_env(),
            "JW_FAKE_SAMPLER_MODE": mode,
            "JW_FAKE_HW_MODEL": state["epoch"]["hardware_model"],
            "JW_FAKE_OS_BUILD": state["epoch"]["os_build"],
            "JW_FAKE_TIME_SCALE": "0.025",
            "JW_FAKE_TIME_ORIGIN": str(time.time()),
            **self.writer_env_overrides,
        }

    def _write_valid_rederive_source(self, source: Path) -> None:
        from tests.test_reduce import self_consistent_calibration

        if source.exists():
            shutil.rmtree(source)
        (source / "raw").mkdir(parents=True)
        evidence, raw, events = self_consistent_calibration()
        stored_only = max(
            abs(float(pulse[field]))
            for pulse in evidence["pulses"]
            for field in (
                "onset_residual_lower_s",
                "onset_residual_upper_s",
                "offset_residual_lower_s",
                "offset_residual_upper_s",
            )
        )
        evidence["b_fiducial_s"] = stored_only
        (source / "raw" / "powermetrics.plist").write_bytes(raw)
        (source / "events.jsonl").write_bytes(events)
        evidence_raw = json.dumps(evidence, indent=2, sort_keys=True).encode() + b"\n"
        (source / "instrument_evidence.json").write_bytes(evidence_raw)
        (source / "manifest.json").write_text(
            json.dumps(
                {
                    "artifacts": {
                        "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
                        "events.jsonl": hashlib.sha256(events).hexdigest(),
                        "instrument_evidence.json": hashlib.sha256(
                            evidence_raw
                        ).hexdigest(),
                    }
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def _commit_fixture(self, message: str) -> None:
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", message], cwd=self.repo, check=True
        )

    def _write_pin_for_receipts(
        self, receipts: list[dict], *, commit: bool = True
    ) -> None:
        self.pin.write_text(
            json.dumps(
                {
                    "sequence": len(receipts),
                    "head_digest": (
                        next(
                            row
                            for row in receipts
                            if row.get("sequence") == len(receipts)
                        )["receipt_digest"]
                        if receipts
                        else GENESIS_DIGEST
                    ),
                    "ledger_schema": LEDGER_SCHEMA,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        if commit:
            self._commit_fixture("durable witness state")

    def _write_receipts(self, receipts: list[dict], *, pin: bool = True) -> None:
        self.ledger.write_bytes(
            b"".join(canonical_json_bytes(receipt) + b"\n" for receipt in receipts)
        )
        if pin:
            self._write_pin_for_receipts(receipts)

    def _ordinary(
        self,
        receipts: list[dict],
        *,
        event: str,
        attempt_id: str,
        disposition: str,
        artifacts: dict[str, str] | None = None,
        epoch: dict | None = None,
    ) -> dict:
        artifacts = artifacts or {}
        content_id = (
            None
            if event == "reservation"
            else ledger_module.content_id_from_artifact_hashes(artifacts)
        )
        return ledger_module._new_receipt(
            sequence=len(receipts) + 1,
            predecessor_digest=(
                next(reversed(receipts))["receipt_digest"] if receipts else GENESIS_DIGEST
            ),
            event=event,
            attempt_id=attempt_id,
            content_id=content_id,
            artifacts=artifacts,
            identity_epoch=epoch or self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s=("1.0" if disposition == "valid" else None),
            exact_bound_lexeme_s=("0.01" if disposition == "valid" else None),
            disposition=disposition,
            custody_locator=str(self.repo / "custody" / attempt_id),
        )

    def _session_record(
        self, receipts: list[dict], *, session_id: str = "session-corrupt"
    ) -> dict:
        identity = {
            "session_id": session_id,
            "window_id": "window-corrupt",
            "plan_id": "plan-corrupt",
            "plan_sha256": "a" * 64,
            "evidence_root_id": "evidence-corrupt",
            "runs_root": str(self.repo / "runs"),
        }
        slots = {
            role: {
                "attempt_id": f"{session_id}-{role}",
                "custody_locator": str(self.repo / "custody" / f"{session_id}-{role}"),
                "identity_epoch": self.epoch,
                "t1_bindings": self.t1,
                "expected_time_role": role,
            }
            for role in ("pre", "post")
        }
        return ledger_module._new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=(
                next(reversed(receipts))["receipt_digest"] if receipts else GENESIS_DIGEST
            ),
            event=ledger_module.BRACKET_SESSION_OPEN_EVENT,
            session_identity=identity,
            fields={"slots": slots},
        )

    def _state_clean(self) -> dict:
        return {}

    def _complete_ordinary_attempt(self, attempt_id: str = "ordinary") -> None:
        custody = str(self.repo / "custody" / attempt_id)
        ledger_module.append_pending_receipt(
            self.ledger,
            attempt_id=attempt_id,
            custody_locator=custody,
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            head_pin_path=self.pin,
            require_committed_pin=False,
            repo_root=self.repo,
        )
        ledger_module.finalize_attempt_receipt(
            self.ledger,
            attempt_id=attempt_id,
            disposition="abandoned",
            custody_locator=custody,
            artifact_sha256={},
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
        )

    def _state_open_for_abort(self) -> dict:
        plan = self._open_session("session-open")
        return {
            "plan": plan,
            "session_id": "session-open",
            "slot": "pre",
            "attempt_id": "session-open-pre",
        }

    def _state_pending(self) -> dict:
        ledger_module.append_pending_receipt(
            self.ledger,
            attempt_id="pending",
            custody_locator=str(self.repo / "custody" / "pending"),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            head_pin_path=self.pin,
            require_committed_pin=False,
            repo_root=self.repo,
        )
        return {}

    def _state_unclassifiable(self) -> dict:
        self._complete_ordinary_attempt("unclassifiable")
        receipts = ReceiptCorpus(
            ledger_module._scan_physical_ledger(self.ledger.read_bytes()).receipts
        )
        self._write_pin_for_receipts(receipts)
        return {"baseline_sequence": 0, "baseline_digest": GENESIS_DIGEST}

    def _state_head_mismatch(self) -> dict:
        self._complete_ordinary_attempt("ahead")
        return self._state_reservation_inputs()

    def _state_head_uncommitted(self) -> dict:
        self._complete_ordinary_attempt("uncommitted")
        receipts = ReceiptCorpus(
            ledger_module._scan_physical_ledger(self.ledger.read_bytes()).receipts
        )
        self._write_pin_for_receipts(receipts, commit=False)
        return {}

    def _state_recovery_required(self) -> dict:
        # Exercise a real kernel-enforced writer crash: the append intent fits
        # beneath RLIMIT_FSIZE, while its target crosses the limit. No function
        # or process hook is patched.
        child = "\n".join(
            (
                "import resource",
                "from pathlib import Path",
                "from joulewise.calibration_ledger import append_pending_receipt",
                "resource.setrlimit(resource.RLIMIT_FSIZE, (2500, 2500))",
                "append_pending_receipt(",
                f"    Path({str(self.ledger)!r}),",
                "    attempt_id='crashed',",
                f"    custody_locator={str(self.repo / 'custody' / 'crashed')!r},",
                f"    identity_epoch={self.epoch!r},",
                f"    t1_bindings={self.t1!r},",
                f"    head_pin_path=Path({str(self.pin)!r}),",
                "    require_committed_pin=False,",
                f"    repo_root=Path({str(self.repo)!r}),",
                ")",
            )
        )
        crashed = subprocess.run(
            [sys.executable, "-c", child],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_cli_env(),
            check=False,
        )
        self.assertNotEqual(crashed.returncode, 0, crashed.stdout + crashed.stderr)
        inspection = ledger_module.inspect_calibration_ledger(self.ledger)
        self.assertIsNotNone(inspection.active_operation_id)
        return {}

    def _state_pin_not_committed(self) -> dict:
        self.pin.write_text(
            json.dumps(
                {
                    "sequence": 0,
                    "head_digest": GENESIS_DIGEST,
                    "ledger_schema": LEDGER_SCHEMA,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return {}

    def _state_closed_session(self) -> dict:
        state = self._state_open_for_abort()
        ledger_module.abort_bracket_session(
            self.ledger, session_id=state["session_id"], reason="witness closure"
        )
        return state

    def _state_terminal_not_head(self) -> dict:
        state = self._state_closed_session()
        receipts = ReceiptCorpus(
            ledger_module._scan_physical_ledger(self.ledger.read_bytes()).receipts
        )
        self._write_pin_for_receipts(receipts, commit=False)
        self._complete_ordinary_attempt("after-terminal")
        return state

    def _state_missing_session(self) -> dict:
        plan = self.repo / "plans" / "missing.json"
        plan.parent.mkdir(parents=True)
        plan.write_text(
            json.dumps({"plan_id": "plan-missing", "session_id": "missing"}) + "\n",
            encoding="utf-8",
        )
        return {"plan": plan, "session_id": "missing"}

    def _state_reservation_inputs(self) -> dict:
        root = self.repo / "reservation-inputs"
        root.mkdir(exist_ok=True)
        plan = root / "plan.json"
        plan.write_text(
            json.dumps({"plan_id": "plan-new", "session_id": "session-new"}) + "\n",
            encoding="utf-8",
        )
        epoch = root / "epoch.json"
        epoch.write_text(json.dumps(self.epoch) + "\n", encoding="utf-8")
        t1 = root / "t1.json"
        t1.write_text(json.dumps(self.t1) + "\n", encoding="utf-8")
        return {
            "plan": plan,
            "plan_sha": hashlib.sha256(plan.read_bytes()).hexdigest(),
            "epoch_path": epoch,
            "t1_path": t1,
            "session_id": "session-new",
            "slot": "pre",
            "attempt_id": "session-new-pre",
        }

    def _state_reservation_conflict(self) -> dict:
        open_state = self._state_open_for_abort()
        reserve = self._state_reservation_inputs()
        return {**reserve, "open_state": open_state}

    def _state_writer_protocol(self) -> dict:
        source = self.repo / "rederive-source"
        source.mkdir()
        state = self._state_real_writer("session-writer-correction")
        return state | {
            "source": source,
            "output": self.repo / "rederived.json",
        }

    def _state_writer_protocol_invalid(self) -> dict:
        state = self._state_writer_protocol()
        (
            self.repo
            / "configs"
            / "calibration"
            / "powermetrics_fiducial"
            / "protocol_v3.json"
        ).write_bytes(b"{}\n")
        return state

    def _state_reserved_mismatch(self) -> dict:
        state = self._state_open_for_abort()
        root = self.repo / "slot-validation-inputs"
        root.mkdir()
        state["epoch_path"] = root / "epoch.json"
        state["t1_path"] = root / "t1.json"
        state["epoch_path"].write_text(json.dumps(self.epoch) + "\n", encoding="utf-8")
        state["t1_path"].write_text(json.dumps(self.t1) + "\n", encoding="utf-8")
        state["custody_locator"] = str(self.repo / "wrong-custody-location")
        return state

    def _actual_writer_bindings(self) -> tuple[dict, dict]:
        epoch = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        t1 = {
            **epoch,
            "powermetrics_sha256": hashlib.sha256(
                self.fake_sampler.read_bytes()
            ).hexdigest(),
            "anchor_method_version": ACTIVE_CAPTURE_ANCHOR_METHOD,
            "mlx_version": "test-mlx-1",
            "protocol_sha256": hashlib.sha256(
                (
                    self.repo
                    / "configs"
                    / "calibration"
                    / "powermetrics_fiducial"
                    / "protocol_v3.json"
                ).read_bytes()
            ).hexdigest(),
        }
        return epoch, t1

    def _state_real_writer(self, session_id: str) -> dict:
        epoch, t1 = self._actual_writer_bindings()
        plan = self._open_session(session_id, epoch=epoch, t1=t1)
        custody = (
            self.repo
            / "runs"
            / session_id
            / "instrument_validation"
            / f"{session_id}-pre"
        )
        identity_path = self.repo / "writer-fixtures" / f"{session_id}-identity.json"
        identity_path.write_text(json.dumps(epoch) + "\n", encoding="utf-8")
        return {
            "plan": plan,
            "session_id": session_id,
            "slot": "pre",
            "attempt_id": f"{session_id}-pre",
            "custody_locator": str(custody),
            "output_root": custody.parent,
            "epoch": epoch,
            "t1": t1,
            "identity_path": identity_path,
        }

    def _writer_capture_args(self, state: dict) -> list[str]:
        return [
            "--allow-live",
            "--power-policy",
            "ac_high_power",
            "--ledger",
            str(self.ledger),
            "--head-pin",
            str(self.pin),
            "--session-id",
            state["session_id"],
            "--slot",
            state["slot"],
            "--attempt-id",
            state["attempt_id"],
            "--output-root",
            str(state["output_root"]),
            "--sampler-binary",
            str(self.fake_sampler),
            "--sampler-direct-for-test",
            "--time-scale-for-test",
            "0.025",
            "--identity-epoch-json-for-test",
            str(state["identity_path"]),
            "--sampler-ready-timeout-s",
            "1.0",
            "--rollover-timeout-s",
            "1.5",
        ]

    def _state_hostile_claim_id(self) -> dict:
        state = self._state_open_for_abort()
        receipts = ReceiptCorpus(
            ledger_module._scan_physical_ledger(self.ledger.read_bytes()).receipts
        )
        open_receipt = receipts.one(
            event=ledger_module.BRACKET_SESSION_OPEN_EVENT
        )
        hostile = ledger_module._new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=receipts.one(sequence=len(receipts))[
                "receipt_digest"
            ],
            event=ledger_module.BRACKET_SESSION_SLOT_CLAIM_EVENT,
            session_identity={
                field: open_receipt[field]
                for field in ledger_module._SESSION_IDENTITY_KEYS
            },
            fields={
                "slot": "pre",
                "attempt_id": state["attempt_id"],
                "claim_id": "authenticated-but-not-the-policy-claim-id",
            },
        )
        intent = ledger_module._new_append_intent(
            receipts=tuple(receipts),
            byte_offset=len(self.ledger.read_bytes()),
            target_core=ledger_module._target_core(hostile),
            operation_key=ledger_module._operation_key_for_core(
                ledger_module._target_core(hostile)
            ),
        )
        target = ledger_module._intent_target_receipt(
            intent,
            sequence=len(receipts) + 2,
            predecessor_digest=intent["receipt_digest"],
        )
        with self.ledger.open("ab") as handle:
            handle.write(canonical_json_bytes(intent) + b"\n")
            handle.write(canonical_json_bytes(target) + b"\n")
        return state

    def _state_writer_binding_conflict(self) -> dict:
        return self._state_real_writer("session-binding-conflict")

    def _state_display_abort(self) -> dict:
        return self._state_real_writer("session-display-abort")

    def _state_sampler_abort(self) -> dict:
        return self._state_real_writer("session-sampler-abort")

    def _state_rollover_abort(self) -> dict:
        return self._state_real_writer("session-rollover-abort")

    def _state_pre_slot_not_ready(self) -> dict:
        return self._state_real_writer("session-pre-slot-not-ready")

    def _reservation_args(
        self, state: dict, *, session_id: str | None = None, execute: bool = False
    ) -> list[str]:
        session = session_id or state["session_id"]
        args = [
            "--ledger",
            str(self.ledger),
            "--head-pin",
            str(self.pin),
            "--session-id",
            session,
            "--window-id",
            f"window-{session}",
            "--plan-id",
            "plan-new",
            "--plan-sha256",
            state["plan_sha"],
            "--plan",
            str(state["plan"]),
            "--evidence-root-id",
            f"evidence-{session}",
            "--runs-root",
            str(self.repo / "runs" / session),
            "--pre-attempt-id",
            f"{session}-pre",
            "--post-attempt-id",
            f"{session}-post",
            "--pre-custody-locator",
            str(self.repo / "runs" / session / "instrument_validation" / f"{session}-pre"),
            "--post-custody-locator",
            str(self.repo / "runs" / session / "instrument_validation" / f"{session}-post"),
            "--identity-epoch-json",
            str(state["epoch_path"]),
            "--t1-bindings-json",
            str(state["t1_path"]),
        ]
        if execute:
            args.append("--execute")
        return args

    def _corrupt_missing(self) -> dict:
        self.pin.write_text(
            json.dumps(
                {
                    "sequence": 1,
                    "head_digest": "a" * 64,
                    "ledger_schema": LEDGER_SCHEMA,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self._commit_fixture("missing ledger witness")
        return {}

    def _corrupt_malformed(self) -> dict:
        self.ledger.write_bytes(b"{malformed}\n")
        self._commit_fixture("malformed ledger witness")
        return {}

    def _corrupt_chain(self) -> dict:
        receipt = ledger_module._new_receipt(
            sequence=1,
            predecessor_digest="f" * 64,
            event="reservation",
            attempt_id="chain",
            content_id=None,
            artifacts={},
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s=None,
            exact_bound_lexeme_s=None,
            disposition="pending",
            custody_locator=str(self.repo / "custody" / "chain"),
        )
        self.ledger.write_bytes(canonical_json_bytes(receipt) + b"\n")
        self._commit_fixture("chain witness")
        return {}

    def _corrupt_attempts(self) -> dict:
        receipts: list[dict] = []
        receipts.append(
            self._ordinary(
                receipts, event="reservation", attempt_id="duplicate", disposition="pending"
            )
        )
        receipts.append(
            self._ordinary(
                receipts, event="reservation", attempt_id="duplicate", disposition="pending"
            )
        )
        self._write_receipts(receipts)
        return {}

    def _corrupt_sessions(self) -> dict:
        receipts: list[dict] = []
        receipts.append(self._session_record(receipts))
        receipts.append(self._session_record(receipts))
        self._write_receipts(receipts)
        return {}

    def _corrupt_content(self) -> dict:
        artifacts = {
            name: hashlib.sha256(f"same:{name}".encode()).hexdigest()
            for name in GOVERNED_ARTIFACTS
        }
        receipts: list[dict] = []
        for attempt, disposition in (("a", "valid"), ("b", "abandoned")):
            receipts.append(
                self._ordinary(
                    receipts,
                    event="reservation",
                    attempt_id=attempt,
                    disposition="pending",
                )
            )
            receipts.append(
                self._ordinary(
                    receipts,
                    event="finalization",
                    attempt_id=attempt,
                    disposition=disposition,
                    artifacts=artifacts,
                )
            )
            custody = self.repo / "custody" / attempt
            for name in GOVERNED_ARTIFACTS:
                path = custody / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"same:{name}".encode())
        self._write_receipts(receipts)
        return {}

    def _corrupt_rollback(self) -> dict:
        ledger_module.append_pending_receipt(
            self.ledger,
            attempt_id="rollback",
            custody_locator=str(self.repo / "custody" / "rollback"),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            head_pin_path=self.pin,
            require_committed_pin=False,
            repo_root=self.repo,
        )
        receipts = ReceiptCorpus(
            ledger_module._scan_physical_ledger(self.ledger.read_bytes()).receipts
        )
        self._write_pin_for_receipts(receipts)
        self.ledger.write_bytes(b"")
        return {}

    def _intent_for_core(self, target_core: dict) -> dict:
        return ledger_module._new_append_intent(
            receipts=[],
            byte_offset=0,
            target_core=target_core,
            operation_key=ledger_module._operation_key_for_core(target_core),
        )

    def _corrupt_operation(self) -> dict:
        target_a = self._ordinary(
            [], event="reservation", attempt_id="expected", disposition="pending"
        )
        intent = self._intent_for_core(ledger_module._target_core(target_a))
        target_b = ledger_module._new_receipt(
            sequence=2,
            predecessor_digest=intent["receipt_digest"],
            event="reservation",
            attempt_id="foreign",
            content_id=None,
            artifacts={},
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s=None,
            exact_bound_lexeme_s=None,
            disposition="pending",
            custody_locator=str(self.repo / "custody" / "foreign"),
        )
        self.ledger.write_bytes(
            canonical_json_bytes(intent)
            + b"\n"
            + canonical_json_bytes(target_b)
            + b"\n"
        )
        self._commit_fixture("operation conflict witness")
        return {}

    def _corrupt_ungoverned(self) -> dict:
        target = self._ordinary(
            [], event="reservation", attempt_id="governed", disposition="pending"
        )
        intent = self._intent_for_core(ledger_module._target_core(target))
        committed = ledger_module._intent_target_receipt(
            intent, sequence=2, predecessor_digest=intent["receipt_digest"]
        )
        bare = ledger_module._new_receipt(
            sequence=3,
            predecessor_digest=committed["receipt_digest"],
            event="reservation",
            attempt_id="bare",
            content_id=None,
            artifacts={},
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s=None,
            exact_bound_lexeme_s=None,
            disposition="pending",
            custody_locator=str(self.repo / "custody" / "bare"),
        )
        self.ledger.write_bytes(
            b"".join(
                canonical_json_bytes(row) + b"\n"
                for row in (intent, committed, bare)
            )
        )
        self._commit_fixture("ungoverned witness")
        return {}

    def _corrupt_custody(self) -> dict:
        artifacts = {
            name: hashlib.sha256(f"absent:{name}".encode()).hexdigest()
            for name in GOVERNED_ARTIFACTS
        }
        receipts: list[dict] = []
        receipts.append(
            self._ordinary(
                receipts, event="reservation", attempt_id="custody", disposition="pending"
            )
        )
        receipts.append(
            self._ordinary(
                receipts,
                event="finalization",
                attempt_id="custody",
                disposition="valid",
                artifacts=artifacts,
            )
        )
        self._write_receipts(receipts)
        return {}

    def _corrupt_lock(self) -> dict:
        target = self.repo / "foreign-lock"
        target.write_text("foreign", encoding="utf-8")
        ledger_module._ledger_lock_path(self.ledger).symlink_to(target)
        return {}

    def _corrupt_unreadable_ledger(self) -> dict:
        self.ledger.write_text("", encoding="utf-8")
        self.ledger.chmod(0)
        return {"restore": lambda: self.ledger.chmod(0o600)}

    def _journal(self) -> Path:
        if not self.ledger.exists():
            self.ledger.write_bytes(b"")
        journal = ledger_module._legacy_append_journal_path(self.ledger)
        journal.write_bytes(b"legacy journal bytes")
        return journal

    def _corrupt_unreadable_journal(self) -> dict:
        journal = self._journal()
        journal.chmod(0)
        return {"restore": lambda: journal.chmod(0o600)}

    def _corrupt_archive_conflict(self) -> dict:
        journal = self._journal()
        digest = hashlib.sha256(journal.read_bytes()).hexdigest()
        journal.with_name(f"{journal.name}.archived-{digest[:16]}").write_bytes(b"conflict")
        return {}

    def _corrupt_archive_failure(self) -> dict:
        self.ledger.write_bytes(b"")
        ledger_module._ledger_lock_path(self.ledger).write_bytes(b"")
        self._journal()
        self.ledger.parent.chmod(0o555)
        return {"restore": lambda: self.ledger.parent.chmod(0o755)}

    def _corrupt_intent(self) -> dict:
        intent = self._intent_for_core(
            {"schema_version": "hostile.invalid.v1", "event": "invalid", "attempt_id": "x"}
        )
        self.ledger.write_bytes(canonical_json_bytes(intent) + b"\n")
        return {}

    def _corrupt_nonconvergent(self) -> dict:
        intent = self._intent_for_core(
            {
                "schema_version": ledger_module.CONTROL_SCHEMA,
                "event": ledger_module.APPEND_INTENT_EVENT,
                "attempt_id": "nested",
            }
        )
        self.ledger.write_bytes(canonical_json_bytes(intent) + b"\n")
        return {}

    def _corrupt_abandon_io(self) -> dict:
        self.ledger.write_bytes(b"operator residue\n")
        self.ledger.chmod(0o400)
        return {"restore": lambda: self.ledger.chmod(0o600)}

    def _corrupt_abandon_pin(self) -> dict:
        pinned = self._ordinary(
            [], event="reservation", attempt_id="pinned", disposition="pending"
        )
        sibling = self._ordinary(
            [], event="reservation", attempt_id="sibling", disposition="pending"
        )
        self.ledger.write_bytes(canonical_json_bytes(sibling) + b"\nresidue")
        self.pin.write_text(
            json.dumps(
                {
                    "sequence": 1,
                    "head_digest": pinned["receipt_digest"],
                    "ledger_schema": LEDGER_SCHEMA,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self._commit_fixture("abandon pin mismatch witness")
        return {}

    def _corrupt_unreadable_pin(self) -> dict:
        self.pin.chmod(0)
        return {"restore": lambda: self.pin.chmod(0o600)}

    def _corrupt_malformed_pin(self) -> dict:
        self.pin.write_bytes(b"{}\n")
        return {}

    def _corrupt_session_custody(self) -> dict:
        plan = self._open_session("session-unreadable")
        custody = (
            self.repo
            / "runs"
            / "session-unreadable"
            / "instrument_validation"
            / "session-unreadable-pre"
        )
        custody.parent.mkdir(parents=True, exist_ok=True)
        custody.write_bytes(b"not a directory")
        return {
            "plan": plan,
            "session_id": "session-unreadable",
            "slot": "pre",
            "attempt_id": "session-unreadable-pre",
        }

    def _state_tail(self) -> dict:
        self.ledger.write_bytes(b'{"orphan":true}\n')
        return {}

    def _state_complete_custody(self) -> dict:
        plan = self._open_session("session-resume")
        self._complete_custody("session-resume", "pre")
        return {
            "plan": plan,
            "session_id": "session-resume",
            "slot": "pre",
            "attempt_id": "session-resume-pre",
        }

    def _state_partial_custody(self) -> dict:
        plan = self._open_session("session-partial")
        partial = (
            self.repo
            / "runs"
            / "session-partial"
            / "instrument_validation"
            / "session-partial-pre"
        )
        (partial / "raw").mkdir(parents=True)
        (partial / "raw" / "powermetrics.plist").write_bytes(b"partial")
        return {
            "plan": plan,
            "session_id": "session-partial",
            "slot": "pre",
            "attempt_id": "session-partial-pre",
        }

    def _state_live_writer(self) -> dict:
        state = self._state_complete_custody()
        holder_code = (
            "import time; from pathlib import Path; "
            "from joulewise.calibration_ledger import CalibrationWriterLease, claim_bracket_session_slot; "
            f"lease=CalibrationWriterLease(Path({str(self.ledger)!r})); lease.acquire(); "
            f"claim_bracket_session_slot(Path({str(self.ledger)!r}), session_id='session-resume', slot='pre', attempt_id='session-resume-pre'); "
            "print('LEASED', flush=True); time.sleep(60)"
        )
        holder = self._start_holder(holder_code)
        assert holder.stdout is not None
        self.assertEqual(holder.stdout.readline().strip(), "LEASED")
        state["holder"] = holder
        return state

    def _open_session(
        self,
        session_id: str = "session-witness",
        *,
        epoch: dict | None = None,
        t1: dict | None = None,
    ) -> Path:
        epoch = epoch or self.epoch
        t1 = t1 or self.t1
        plan = self.repo / "plans" / f"{session_id}.json"
        plan.parent.mkdir(exist_ok=True)
        plan.write_text(
            json.dumps({"plan_id": f"plan-{session_id}", "session_id": session_id})
            + "\n",
            encoding="utf-8",
        )
        plan_sha = hashlib.sha256(plan.read_bytes()).hexdigest()
        runs_root = self.repo / "runs" / session_id
        append_bracket_session_receipt(
            self.ledger,
            session_id=session_id,
            window_id=f"window-{session_id}",
            plan_id=f"plan-{session_id}",
            plan_sha256=plan_sha,
            evidence_root_id=f"evidence-{session_id}",
            runs_root=runs_root,
            slots={
                slot: {
                    "attempt_id": f"{session_id}-{slot}",
                    "custody_locator": str(
                        runs_root / "instrument_validation" / f"{session_id}-{slot}"
                    ),
                    "identity_epoch": epoch,
                    "t1_bindings": t1,
                }
                for slot in ("pre", "post")
            },
            head_pin_path=self.pin,
            require_committed_pin=False,
            repo_root=self.repo,
        )
        return plan

    def _complete_custody(self, session_id: str, slot: str) -> Path:
        root = (
            self.repo
            / "runs"
            / session_id
            / "instrument_validation"
            / f"{session_id}-{slot}"
        )
        (root / "raw").mkdir(parents=True)
        payloads = {
            "raw/powermetrics.plist": b"synthetic raw\n",
            "events.jsonl": b'{"event_type":"synthetic"}\n',
            "power_trace.csv": b"timestamp_s,power_w\n1,2\n",
        }
        for relative, raw in payloads.items():
            (root / relative).write_bytes(raw)
        evidence = {
            "validation_id": f"{session_id}-{slot}",
            "status": "valid",
            "b_fiducial_s": 0.025,
            "capture_wall_time_s": 99.0,
            "bindings": self.t1,
            "artifact_sha256": {
                name: hashlib.sha256(raw).hexdigest()
                for name, raw in payloads.items()
            },
        }
        evidence_raw = json.dumps(evidence, sort_keys=True).encode() + b"\n"
        (root / "instrument_evidence.json").write_bytes(evidence_raw)
        manifest_artifacts = {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in GOVERNED_ARTIFACTS
            if name != "manifest.json"
        }
        (root / "manifest.json").write_text(
            json.dumps(
                {
                    "validation_id": f"{session_id}-{slot}",
                    "artifacts": manifest_artifacts,
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return root

    def _execute_case(self, case: WitnessCase) -> OwnedProcessResult:
        state = getattr(self, case.constructor)()
        holder = state.get("holder")
        record = REFUSAL_BY_CODE[case.code]
        if case.code is RefusalCode.FINALIZATION_BINDING_CONFLICT:
            construction_env = self._writer_env(state, mode="normal")
            construction_env["JW_FAKE_HW_MODEL"] = "corrupted-device-metadata"
            construction = self._run_script(
                self.writer_script,
                *self._writer_capture_args(state),
                env=construction_env,
                crash_stage="artifacts-complete-before-finalization",
                authorize_crash=True,
            )
            self.assertEqual(
                construction.returncode,
                -signal.SIGKILL,
                construction.stdout + construction.stderr,
            )
            self.assertNotIn(case.code.value, construction.stdout + construction.stderr)
        preservation_guard = (
            PreservationGuard(self, case.code)
            if record.terminal_result is TerminalResult.NIGHT_STOPPED_PRESERVED
            else None
        )
        if preservation_guard is not None:
            preservation_guard.begin()
        try:
            if case.observer in {"audit", "inspect", "repair"}:
                refused = self._run(case.observer)
            elif case.observer == "audit-baseline":
                refused = self._run(
                    "audit",
                    "--baseline-sequence",
                    "1",
                    "--baseline-digest",
                    "a" * 64,
                )
            elif case.observer == "audit-observations":
                refused = self._run(
                    "audit-observations",
                    "--baseline-sequence",
                    str(state["baseline_sequence"]),
                    "--baseline-digest",
                    state["baseline_digest"],
                )
            elif case.observer == "repair-credentials":
                refused = self._run("repair", "--engine-identity", "")
            elif case.observer == "abandon":
                refused = self._run(
                    "abandon-tail",
                    "--operator-identity",
                    "witness-operator",
                    "--attestation-reason",
                    "executed durable witness",
                )
            elif case.observer == "abandon-credentials":
                refused = self._run(
                    "abandon-tail",
                    "--operator-identity",
                    "",
                    "--attestation-reason",
                    "witness",
                )
            elif case.observer == "readiness-pre-slot":
                refused = self._run(
                    "readiness",
                    "--phase",
                    "pre-slot",
                    "--session-id",
                    state["session_id"],
                    "--slot",
                    state["slot"],
                    "--attempt-id",
                    state["attempt_id"],
                    "--plan",
                    str(state["plan"]),
                )
            elif case.observer == "resume-live":
                refused = self._run(
                    "resume-finalize",
                    "--session-id",
                    state["session_id"],
                    "--slot",
                    state["slot"],
                    "--plan",
                    str(state["plan"]),
                )
            elif case.observer.startswith("reserve-"):
                args = self._reservation_args(
                    state,
                    session_id=(
                        "session-open"
                        if case.observer == "reserve-execute"
                        and case.code is RefusalCode.RESERVATION_IDENTITY_CONFLICT
                        else None
                    ),
                    execute=case.observer in {
                        "reserve-execute",
                        "reserve-execute-new",
                    },
                )
                if case.code is RefusalCode.RESERVATION_IDENTITY_CONFLICT:
                    open_plan = state["open_state"]["plan"]
                    args[args.index("--plan-id") + 1] = "plan-session-open"
                    args[args.index("--plan-sha256") + 1] = hashlib.sha256(
                        open_plan.read_bytes()
                    ).hexdigest()
                    args[args.index("--plan") + 1] = str(open_plan)
                    args[args.index("--window-id") + 1] = "conflicting-window"
                if case.observer == "reserve-input":
                    plan_index = args.index("--plan")
                    del args[plan_index : plan_index + 2]
                    sha_index = args.index("--plan-sha256") + 1
                    args[sha_index] = "not-a-sha"
                elif case.observer == "reserve-json":
                    state["epoch_path"].write_bytes(b"not-json\n")
                elif case.observer == "reserve-plan-unreadable":
                    plan_index = args.index("--plan") + 1
                    args[plan_index] = str(self.repo / "missing-plan.json")
                elif case.observer == "reserve-plan-mismatch":
                    sha_index = args.index("--plan-sha256") + 1
                    args[sha_index] = "f" * 64
                refused = self._run_script(self.reserve_script, *args)
            elif case.observer == "session-status":
                refused = self._run(
                    "session-status",
                    "--session-id",
                    state["session_id"],
                    "--plan",
                    str(state["plan"]),
                )
            elif case.observer == "session-refusal":
                refused = self._run(
                    "session-refusal",
                    "--session-id",
                    state["session_id"],
                    "--plan",
                    str(state["plan"]),
                )
            elif case.observer == "validate-slot":
                refused = self._run(
                    "validate-slot",
                    "--session-id",
                    state["session_id"],
                    "--slot",
                    state["slot"],
                    "--attempt-id",
                    state["attempt_id"],
                    "--custody-locator",
                    state["custody_locator"],
                    "--identity-epoch-json",
                    str(state["epoch_path"]),
                    "--t1-bindings-json",
                    str(state["t1_path"]),
                )
            elif case.observer == "abort-session":
                refused = self._run(
                    "abort-session",
                    "--session-id",
                    state["session_id"],
                    "--plan",
                    str(state["plan"]),
                    "--reason",
                    "second abort witness",
                )
            elif case.observer in {"resume-post", "resume-pre"}:
                refused = self._run(
                    "resume-finalize",
                    "--session-id",
                    state["session_id"],
                    "--slot",
                    "post" if case.observer == "resume-post" else "pre",
                    "--plan",
                    str(state["plan"]),
                )
            elif case.observer == "terminal-pin":
                refused = self._run(
                    "terminal-pin", "--session-id", state["session_id"]
                )
            elif case.observer == "readiness-wrong-slot":
                refused = self._run(
                    "readiness",
                    "--phase",
                    "pre-slot",
                    "--session-id",
                    state["session_id"],
                    "--slot",
                    "post",
                    "--attempt-id",
                    f"{state['session_id']}-post",
                    "--plan",
                    str(state["plan"]),
                )
            elif case.observer == "readiness-terminal":
                refused = self._run(
                    "readiness",
                    "--phase",
                    "terminal",
                    "--session-id",
                    state["session_id"],
                )
            elif case.observer.startswith("advance-"):
                inspection = ledger_module.inspect_calibration_ledger(self.ledger)
                expected_sequence = inspection.head_sequence
                expected_digest = inspection.head_digest
                if case.observer == "advance-wrong":
                    expected_digest = "f" * 64
                advance_args = [
                    "advance-head-pin",
                    "--expected-sequence",
                    str(expected_sequence),
                    "--expected-digest",
                    expected_digest,
                    "--operator-identity",
                    "witness-operator",
                    "--attestation-reason",
                    "executed pin witness",
                    "--execute",
                ]
                if case.observer == "advance-wrong":
                    advance_args[1:1] = ["--session-id", state["session_id"]]
                refused = self._run(*advance_args)
            elif case.observer == "writer-binding-conflict":
                refused = self._run(
                    "resume-finalize",
                    "--session-id",
                    state["session_id"],
                    "--slot",
                    state["slot"],
                    "--plan",
                    str(state["plan"]),
                )
            elif case.observer.startswith("writer-"):
                writer_args: list[str]
                if case.observer == "writer-bracket-args":
                    writer_args = ["--session-id", "session"]
                elif case.observer == "writer-rederive-conflict":
                    writer_args = [
                        "--session-id",
                        "session",
                        "--slot",
                        "pre",
                        "--attempt-id",
                        "attempt",
                        "--output",
                        str(state["output"]),
                    ]
                elif case.observer == "writer-rederive-output":
                    writer_args = ["--rederive-from", str(state["source"])]
                elif case.observer == "writer-rederive-failed":
                    writer_args = [
                        "--rederive-from",
                        str(state["source"]),
                        "--output",
                        str(state["output"]),
                    ]
                elif case.observer == "writer-output":
                    writer_args = ["--output", str(state["output"])]
                elif case.observer == "writer-power":
                    writer_args = ["--allow-live"]
                elif case.observer == "writer-display-failure":
                    writer_args = [
                        *self._writer_capture_args(state),
                        "--sleep-display-before-capture",
                        "--display-arm-binary",
                        str(self.repo / "missing-display-arm-command"),
                    ]
                elif case.observer == "writer-sampler-failure":
                    writer_args = self._writer_capture_args(state)
                elif case.observer == "writer-rollover-failure":
                    writer_args = [
                        *self._writer_capture_args(state),
                        "--sampler-ready-timeout-s",
                        "1.0",
                    ]
                else:
                    writer_args = []
                if case.observer == "writer-display-failure":
                    writer_env = self._writer_env(state, mode="normal")
                elif case.observer == "writer-sampler-failure":
                    writer_env = self._writer_env(state, mode="never-stubborn")
                elif case.observer == "writer-rollover-failure":
                    writer_env = self._writer_env(state, mode="one-stubborn")
                else:
                    writer_env = state.get("env")
                refused = self._run_script(
                    self.writer_script,
                    *writer_args,
                    env=writer_env,
                )
            else:  # pragma: no cover - the table is closed by the exact-set gate
                raise AssertionError(f"unknown observer {case.observer}")
            if preservation_guard is not None:
                preservation_guard.finish(refused)
            self.assertEqual(
                refused.returncode,
                REFUSAL_BY_CODE[case.code].process_exit,
                refused.stdout + refused.stderr,
            )
            payload = self._json_payload(refused)
            self.assertEqual(payload["code"], case.code.value)
            if record.terminal_result is not TerminalResult.NIGHT_STOPPED_PRESERVED:
                self.assertNotIn(
                    "terminal_result",
                    payload,
                    f"{case.code.value} projected an unexecuted terminal result",
                )

            # The observation subprocess is gone here. Invoke the registered
            # public exit from a fresh process and assert its terminal state.
            if record.terminal_result is TerminalResult.NIGHT_STOPPED_PRESERVED:
                exited = refused
                exit_payload = payload
                self.assertEqual(exit_payload["exit_id"], record.exit_id)
                self.assertEqual(
                    exit_payload["terminal_result"],
                    TerminalResult.NIGHT_STOPPED_PRESERVED.value,
                )
                terminal = exit_payload["terminal_result"]
            elif case.code in {
                RefusalCode.TAIL_REQUIRES_ABANDON,
                RefusalCode.INTENT_TARGET_MALFORMED,
            }:
                if case.code is RefusalCode.INTENT_TARGET_MALFORMED:
                    quarantined = ledger_module.inspect_calibration_ledger(
                        self.ledger
                    )
                    self.assertEqual(quarantined.state, "intent")
                    before_rows = ReceiptCorpus(
                        ledger_module._scan_physical_ledger(
                            self.ledger.read_bytes()
                        ).receipts
                    )
                    self.assertEqual(
                        before_rows.one(event=ledger_module.APPEND_INTENT_EVENT)[
                            "event"
                        ],
                        ledger_module.APPEND_INTENT_EVENT,
                    )
                exited = self._run(
                    "abandon-tail",
                    "--operator-identity",
                    "witness-operator",
                    "--attestation-reason",
                    "executed orphaned-tail exit",
                )
                self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
                self.assertEqual(json.loads(exited.stdout)["inspection"]["state"], "clean")
                repaired = self._run("repair")
                self.assertEqual(
                    repaired.returncode, 0, repaired.stdout + repaired.stderr
                )
                repaired_payload = json.loads(repaired.stdout)
                self.assertEqual(repaired_payload["inspection"]["state"], "clean")
                if case.code is RefusalCode.INTENT_TARGET_MALFORMED:
                    after_rows = ReceiptCorpus(
                        ledger_module._scan_physical_ledger(
                            self.ledger.read_bytes()
                        ).receipts
                    )
                    self.assertEqual(
                        after_rows.one(event=ledger_module.ABANDONMENT_EVENT)[
                            "event"
                        ],
                        ledger_module.ABANDONMENT_EVENT,
                    )
                    self.assertFalse(
                        any(
                            row.get("schema_version") == "hostile.invalid.v1"
                            for row in after_rows
                        )
                    )
                terminal = repaired_payload["terminal_result"]
            elif case.code is RefusalCode.CUSTODY_COMPLETE_USE_RESUME:
                exited = self._run(
                    "resume-finalize",
                    "--session-id",
                    state["session_id"],
                    "--slot",
                    state["slot"],
                    "--plan",
                    str(state["plan"]),
                )
                self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
                terminal = json.loads(exited.stdout)["terminal_result"]
            elif case.code is RefusalCode.CUSTODY_PARTIAL:
                exited = self._run(
                    "abort-session",
                    "--session-id",
                    state["session_id"],
                    "--plan",
                    str(state["plan"]),
                    "--reason",
                    "executed partial-custody exit",
                )
                self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
                terminal = json.loads(exited.stdout)["terminal_result"]
            elif case.code is RefusalCode.LIVE_WRITER_CONTENTION:
                assert holder is not None
                self._terminate_and_reap_holder(holder)
                exited = self._run(
                    "resume-finalize",
                    "--session-id",
                    state["session_id"],
                    "--slot",
                    state["slot"],
                    "--plan",
                    str(state["plan"]),
                )
                self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
                terminal = json.loads(exited.stdout)["terminal_result"]
            elif case.code is RefusalCode.LEDGER_RECOVERY_REQUIRED:
                exited = self._run("repair")
                self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
                terminal = json.loads(exited.stdout)["terminal_result"]
            elif record.terminal_result is TerminalResult.SESSION_ABORTED:
                if case.code in {
                    RefusalCode.DISPLAY_ARM_FAILED,
                    RefusalCode.SAMPLER_NEVER_READY,
                    RefusalCode.ROLLOVER_GATE_TIMEOUT,
                }:
                    status = self._run(
                        "session-status",
                        "--session-id",
                        state["session_id"],
                        "--plan",
                        str(state["plan"]),
                    )
                    self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
                    durable = json.loads(status.stdout)
                    self.assertEqual(durable["session_state"], "aborted")
                    self.assertEqual(
                        durable["abort_reason"],
                        {
                            RefusalCode.DISPLAY_ARM_FAILED: "display_arm_failed",
                            RefusalCode.SAMPLER_NEVER_READY: "powermetrics_never_ready",
                            RefusalCode.ROLLOVER_GATE_TIMEOUT: (
                                "pulse_calibration_rollover_gate_timeout"
                            ),
                        }[case.code],
                    )
                    fresh = self._run(
                        "session-refusal",
                        "--session-id",
                        state["session_id"],
                        "--plan",
                        str(state["plan"]),
                    )
                    self.assertEqual(fresh.returncode, record.process_exit)
                    terminal = self._json_payload(fresh)["terminal_result"]
                else:
                    exit_state = state.get("open_state", state)
                    exited = self._run(
                        "abort-session",
                        "--session-id",
                        exit_state["session_id"],
                        "--plan",
                        str(exit_state["plan"]),
                        "--reason",
                        f"executed {case.code.value} exit",
                    )
                    self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
                    terminal = json.loads(exited.stdout)["terminal_result"]
            elif record.terminal_result is TerminalResult.READY_TO_ARM:
                reservation_corrections = {
                    RefusalCode.RESERVATION_INPUT_INVALID,
                    RefusalCode.RESERVATION_JSON_INVALID,
                    RefusalCode.PLAN_UNREADABLE,
                    RefusalCode.PLAN_HASH_MISMATCH,
                }
                rederive_corrections = {
                    RefusalCode.WRITER_BRACKET_REDERIVE_CONFLICT,
                    RefusalCode.FROZEN_PROTOCOL_INVALID,
                    RefusalCode.REDERIVE_OUTPUT_REQUIRED,
                    RefusalCode.REDERIVE_FAILED,
                    RefusalCode.OUTPUT_REQUIRES_REDERIVE,
                }
                if case.code in reservation_corrections:
                    if case.code is RefusalCode.RESERVATION_JSON_INVALID:
                        state["epoch_path"].write_text(
                            json.dumps(self.epoch) + "\n", encoding="utf-8"
                        )
                    corrected = self._run_corrected_script(
                        case.code,
                        self.reserve_script,
                        *self._reservation_args(state, execute=True),
                        durable_postcondition=lambda: self._reservation_postcondition(
                            state
                        ),
                    )
                    self.assertEqual(
                        corrected.returncode,
                        0,
                        corrected.stdout + corrected.stderr,
                    )
                    self.assertEqual(
                        json.loads(corrected.stdout)["status"],
                        "reserved",
                    )
                    evidence = corrected.public_evidence
                    assert evidence is not None
                    self.assertTrue(
                        any(
                            event.get("event")
                            == "calibration_pre_reserve_authorized"
                            for event in evidence.structured_events
                        )
                    )
                    terminal = TerminalResult.READY_TO_ARM.value
                elif case.code is RefusalCode.PRE_SLOT_NOT_READY:
                    self._execute_valid_writer(case.code, state)
                    terminal = TerminalResult.READY_TO_ARM.value
                elif case.code is RefusalCode.PRE_RESERVE_NOT_READY:
                    open_state = state["open_state"]
                    aborted = self._run(
                        "abort-session",
                        "--session-id",
                        open_state["session_id"],
                        "--plan",
                        str(open_state["plan"]),
                        "--reason",
                        "correct pre-reserve state",
                    )
                    self.assertEqual(aborted.returncode, 0, aborted.stdout + aborted.stderr)
                    inspection = ledger_module.inspect_calibration_ledger(self.ledger)
                    advanced = self._run(
                        "advance-head-pin",
                        "--session-id",
                        open_state["session_id"],
                        "--expected-sequence",
                        str(inspection.head_sequence),
                        "--expected-digest",
                        inspection.head_digest,
                        "--operator-identity",
                        "witness-operator",
                        "--attestation-reason",
                        "correct pre-reserve state",
                        "--execute",
                    )
                    self.assertEqual(advanced.returncode, 0, advanced.stdout + advanced.stderr)
                    self._commit_fixture("commit corrected head pin")
                    corrected = self._run_corrected_script(
                        case.code,
                        self.reserve_script,
                        *self._reservation_args(state, execute=True),
                        durable_postcondition=lambda: self._reservation_postcondition(
                            state
                        ),
                    )
                    self.assertEqual(
                        corrected.returncode,
                        0,
                        corrected.stdout + corrected.stderr,
                    )
                    self.assertEqual(json.loads(corrected.stdout)["status"], "reserved")
                    evidence = corrected.public_evidence
                    assert evidence is not None
                    self.assertTrue(
                        any(
                            event.get("event")
                            == "calibration_pre_reserve_authorized"
                            for event in evidence.structured_events
                        )
                    )
                    terminal = TerminalResult.READY_TO_ARM.value
                elif case.code is RefusalCode.TERMINAL_NOT_READY:
                    corrected_plan = self._open_session("session-terminal-corrected")
                    aborted = self._run(
                        "abort-session",
                        "--session-id",
                        "session-terminal-corrected",
                        "--plan",
                        str(corrected_plan),
                        "--reason",
                        "restore terminal state",
                    )
                    self.assertEqual(aborted.returncode, 0, aborted.stdout + aborted.stderr)
                    self.assertTrue(corrected_plan.is_file())
                    corrected = self._run_corrected_script(
                        case.code,
                        self.script,
                        "--ledger",
                        str(self.ledger),
                        "--head-pin",
                        str(self.pin),
                        "terminal-pin",
                        "--session-id",
                        "session-terminal-corrected",
                        durable_postcondition=lambda: {
                            "terminal_head_pin": dict(
                                ledger_module.terminal_head_pin_for_session(
                                    self.ledger,
                                    session_id="session-terminal-corrected",
                                )
                            )
                        },
                    )
                    self.assertEqual(
                        corrected.returncode,
                        0,
                        corrected.stdout + corrected.stderr,
                    )
                    terminal_pin = json.loads(corrected.stdout)
                    self.assertEqual(
                        terminal_pin,
                        dict(
                            corrected.public_evidence.durable_postcondition[
                                "terminal_head_pin"
                            ]
                        ),
                    )
                    terminal = TerminalResult.READY_TO_ARM.value
                elif case.code in rederive_corrections:
                    if case.code is RefusalCode.FROZEN_PROTOCOL_INVALID:
                        shutil.copy2(
                            REPO_ROOT
                            / "configs"
                            / "calibration"
                            / "powermetrics_fiducial"
                            / "protocol_v3.json",
                            self.repo
                            / "configs"
                            / "calibration"
                            / "powermetrics_fiducial"
                            / "protocol_v3.json",
                        )
                    self._write_valid_rederive_source(state["source"])
                    corrected = self._run_corrected_script(
                        case.code,
                        self.writer_script,
                        "--rederive-from",
                        str(state["source"]),
                        "--output",
                        str(state["output"]),
                        durable_postcondition=lambda: {
                            "status": "valid",
                            "output_sha256": hashlib.sha256(
                                state["output"].read_bytes()
                            ).hexdigest(),
                        },
                    )
                    self.assertEqual(
                        corrected.returncode,
                        0,
                        corrected.stdout + corrected.stderr,
                    )
                    self.assertTrue(state["output"].is_file())
                    self.assertEqual(json.loads(corrected.stdout)["status"], "valid")
                    self._execute_valid_writer(case.code, state)
                    terminal = TerminalResult.READY_TO_ARM.value
                else:
                    # Correct the writer tuple, lead authorization, or power
                    # policy named by the registry row, then run the exact
                    # under-lease gate that the live writer consumes.
                    self.assertIn(
                        case.code,
                        {
                            RefusalCode.WRITER_BRACKET_ARGUMENTS,
                            RefusalCode.QUIET_MAC_AUTH_REQUIRED,
                            RefusalCode.POWER_POLICY_REQUIRED,
                        },
                    )
                    self._execute_valid_writer(case.code, state)
                    terminal = TerminalResult.READY_TO_ARM.value
            else:  # pragma: no cover - every non-hard-stop row is explicit
                raise AssertionError(f"no terminal exit for {case.code.value}")
            self.assertEqual(terminal, record.terminal_result.value)
        finally:
            restore = state.get("restore")
            if restore is not None:
                restore()
            if holder is not None:
                self._terminate_and_reap_holder(holder)
        return refused

    def test_parameterized_durable_public_cli_witnesses(self) -> None:
        expected = {case.code for case in WITNESS_CASES}
        executed = self.execute_cases(expected)
        self.assertEqual(executed, expected)
        self.assertEqual(set(_WITNESS_RESULTS), expected)
        self.assertTrue(
            all(result.code is code for code, result in _WITNESS_RESULTS.items())
        )

    def test_logical_producer_delay_preserves_exact_evidence_bytes(self) -> None:
        origin = time.time()

        def capture(delay_s: float | None) -> tuple[bytes, bytes, bytes, bytes]:
            witness = type(self)(methodName="runTest")
            setup_complete = False
            try:
                witness.setUp()
                setup_complete = True
                marker = witness.repo / "writer-fixtures" / "producer-delay.json"
                witness.writer_env_overrides = {
                    "JW_FAKE_TIME_ORIGIN": repr(origin),
                }
                if delay_s is not None:
                    witness.writer_env_overrides.update(
                        {
                            "JW_FAKE_MLX_DELAY_ON_FENCE": "4",
                            "JW_FAKE_MLX_DELAY_S": repr(delay_s),
                            "JW_FAKE_MLX_DELAY_RESULT_PATH": str(marker),
                        }
                    )
                state = witness._state_real_writer(
                    "logical-producer-delay-immunity"
                )
                witness._execute_valid_writer(
                    RefusalCode.QUIET_MAC_AUTH_REQUIRED,
                    state,
                )
                custody = Path(state["custody_locator"])
                if delay_s is None:
                    self.assertFalse(marker.exists())
                else:
                    self.assertEqual(
                        json.loads(marker.read_text(encoding="utf-8")),
                        {"delay_s": delay_s, "fence": 4},
                    )
                self.assertFalse((custody / ".test-sampler-acks.jsonl").exists())
                return (
                    (custody / "instrument_evidence.json").read_bytes(),
                    (custody / "events.jsonl").read_bytes(),
                    (custody / "raw" / "powermetrics.plist").read_bytes(),
                    (custody / "power_trace.csv").read_bytes(),
                )
            finally:
                if setup_complete:
                    witness.tearDown()
                witness.doCleanups()

        baseline = capture(None)
        delayed = capture(0.12)
        self.assertEqual(delayed, baseline)

    def test_abort_witness_payload_survives_nonowned_sampler_census_decoy(self) -> None:
        decoy_capture = self.repo / "powermetrics-decoy.plist"
        decoy = subprocess.Popen(
            [sys.executable, str(self.fake_sampler), "-o", str(decoy_capture)],
            cwd=self.repo,
            env=_fresh_cli_env() | {"JW_FAKE_SAMPLER_MODE": "never"},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        fake_bin = self.repo / "fake-bin"
        fake_bin.mkdir()
        fake_ps = fake_bin / "ps"
        fake_ps.write_text(
            "#!/usr/bin/env python3\n"
            "import os\n"
            "print(os.environ['JW_FAKE_PS_OUTPUT'])\n",
            encoding="utf-8",
        )
        fake_ps.chmod(0o755)
        self.writer_env_overrides = {
            "PATH": os.pathsep.join((str(fake_bin), _fresh_cli_env()["PATH"])),
            "JW_FAKE_PS_OUTPUT": (
                f"{decoy.pid} Python {sys.executable} {self.fake_sampler} "
                f"-o {decoy_capture}"
            ),
        }
        try:
            case = next(
                item
                for item in WITNESS_CASES
                if item.code is RefusalCode.SAMPLER_NEVER_READY
            )
            refused = self._execute_case(case)
            payload = self._json_payload(refused)
            self.assertEqual(payload["code"], RefusalCode.SAMPLER_NEVER_READY.value)
            self.assertTrue(self.public_runner.observed_fake_sampler_pids)
            self.assertNotIn(decoy.pid, self.public_runner.observed_fake_sampler_pids)
            assert_no_owned_fake_sampler_survivors()
            census_events = [
                json.loads(line)
                for line in refused.stderr.splitlines()
                if line.startswith("{")
                and json.loads(line).get("event")
                == validation_script.SAMPLER_CENSUS_DIAGNOSTIC
            ]
            self.assertEqual(len(census_events), 1, refused.stderr)
            self.assertIn(
                decoy.pid,
                [finding["pid"] for finding in census_events[0]["findings"]],
            )
        finally:
            decoy.terminate()
            try:
                decoy.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                decoy.kill()
                decoy.wait(timeout=2.0)

    def test_diagnostic_routes_never_emit_ready_to_arm_under_live_lease(self) -> None:
        holder_code = (
            "import time; from pathlib import Path; "
            "from joulewise.calibration_ledger import CalibrationWriterLease; "
            f"lease=CalibrationWriterLease(Path({str(self.ledger)!r})); "
            "lease.acquire(); print('LEASED', flush=True); time.sleep(60)"
        )
        holder = self._start_holder(holder_code)
        try:
            assert holder.stdout is not None
            self.assertEqual(holder.stdout.readline().strip(), "LEASED")
            audit = self._run("audit")
            observations = self._run(
                "audit-observations",
                "--baseline-sequence",
                "0",
                "--baseline-digest",
                GENESIS_DIGEST,
            )
            for completed, expected_status in (
                (audit, "audit_clean"),
                (observations, "observations_classified"),
            ):
                self.assertEqual(
                    completed.returncode, 0, completed.stdout + completed.stderr
                )
                payload = json.loads(completed.stdout)
                self.assertEqual(payload["status"], expected_status)
                self.assertNotIn("terminal_result", payload)
                self.assertNotIn("ready_to_arm", completed.stdout)
        finally:
            self._terminate_and_reap_holder(holder)

        state = self._state_reserved_mismatch()
        state["custody_locator"] = str(
            self.repo
            / "runs"
            / state["session_id"]
            / "instrument_validation"
            / state["attempt_id"]
        )
        validated = self._run(
            "validate-slot",
            "--session-id",
            state["session_id"],
            "--slot",
            state["slot"],
            "--attempt-id",
            state["attempt_id"],
            "--custody-locator",
            state["custody_locator"],
            "--identity-epoch-json",
            str(state["epoch_path"]),
            "--t1-bindings-json",
            str(state["t1_path"]),
        )
        self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
        self.assertEqual(json.loads(validated.stdout)["status"], "slot_validated")
        self.assertNotIn("terminal_result", json.loads(validated.stdout))
        self.assertNotIn("ready_to_arm", validated.stdout)


def run_valid_writer_load_proof(cycles: int) -> None:
    """Run representative public writers under CPU and filesystem contention."""

    if cycles < 1:
        raise ValueError("cycles must be positive")
    load = WitnessSandbox()
    load.repo.mkdir()
    worker_count = (os.cpu_count() or 2) + 1
    churn_path = load.root / "filesystem-churn"
    load_code = (
        "import os,subprocess,sys; from pathlib import Path; "
        f"workers={worker_count}; root=Path({str(churn_path)!r}); root.mkdir(); "
        "[subprocess.Popen([sys.executable,'-c','while True: pass']) for _ in range(workers)]; "
        "print('LOAD_READY',flush=True); i=0; "
        "exec(\"while True:\\n p=root/f'{i%8}'\\n p.write_text(str(i))\\n i+=1\")"
    )
    load_process = load.runner.start_owned(
        [sys.executable, "-c", load_code],
        cwd=load.repo,
        env=_fresh_cli_env(),
        label="cpu-filesystem-oversubscription",
    )
    assert load_process.stdout is not None
    if load_process.stdout.readline().strip() != "LOAD_READY":
        raise AssertionError("load injector did not become ready")
    retries = 0
    started = time.monotonic()
    try:
        for index in range(cycles):
            witness = PublicGovernedExitWitnessTests(methodName="runTest")
            setup_complete = False
            try:
                witness.setUp()
                setup_complete = True
                state = witness._state_real_writer(f"load-proof-{index}")
                completed = witness._execute_valid_writer(
                    RefusalCode.QUIET_MAC_AUTH_REQUIRED,
                    state,
                )
                if completed.returncode != 0:
                    raise AssertionError(completed.stdout + completed.stderr)
            finally:
                if setup_complete:
                    witness.tearDown()
                    retries += len(witness.sandbox.cleanup_diagnostics)
                witness.doCleanups()
    finally:
        load.runner.terminate_owned(load_process)
        load.close()
    elapsed = time.monotonic() - started
    if owned_process_group_survivors():
        raise AssertionError(owned_process_group_survivors())
    print(
        f"P4_VALID_WRITER_LOOPS={cycles} CPU_WORKERS={worker_count} "
        f"TIMEOUTS=0 SURVIVORS=0 TEARDOWN_RETRIES={retries} "
        f"ELAPSED_S={elapsed:.3f}",
        flush=True,
    )


def run_hung_stage_watchdog_proof() -> None:
    """Prove a silent authenticated stage is killed within watchdog + 5 s."""

    sandbox = WitnessSandbox()
    sandbox.repo.mkdir()
    script = sandbox.repo / "hung_writer_stage.py"
    script.write_text("import time\ntime.sleep(600)\n", encoding="utf-8")
    started = time.monotonic()
    try:
        try:
            sandbox.runner.run(
                [sys.executable, script],
                cwd=sandbox.repo,
                env=_fresh_cli_env(),
                timeout=600.0,
                progress_probe=lambda: AuthenticatedProgress(0, "injected-hung-stage"),
                stage_idle_timeout_s=120.0,
            )
        except subprocess.TimeoutExpired:
            pass
        else:
            raise AssertionError("hung writer stage unexpectedly completed")
        elapsed = time.monotonic() - started
        if elapsed > 125.0:
            raise AssertionError(f"watchdog exceeded +5 s bound: {elapsed:.3f}")
    finally:
        sandbox.close()
    print(
        f"P4_HUNG_WATCHDOG_S=120.0 KILLED_S={elapsed:.3f} "
        "SURVIVORS=0 REGISTRY_EMPTY=1",
        flush=True,
    )


class ResumeFinalizeAcceptanceUnderivableTests(unittest.TestCase):
    """CH-1 hardening: a None acceptance comparator refuses by name.

    When the authenticated acceptance artifact is missing or unauthenticatable
    at import time, ``PREFLIGHT_SYSTEMATIC_SCREEN_S`` is ``None``; the
    resume-finalize command must refuse with a named reason before touching
    any ledger path, never reach the comparison site and crash with a
    ``TypeError``.
    """

    def test_resume_finalize_refuses_when_comparator_underivable(self):
        import contextlib

        import scripts.recover_calibration_ledger as recover_mod
        import scripts.validate_powermetrics_fiducial as writer_mod

        stdout = io.StringIO()
        with mock.patch.object(
            writer_mod, "PREFLIGHT_SYSTEMATIC_SCREEN_S", None
        ):
            with contextlib.redirect_stdout(stdout):
                rc = recover_mod.main(
                    [
                        "--ledger",
                        "/nonexistent/joulewise-test/ledger.jsonl",
                        "--head-pin",
                        "/nonexistent/joulewise-test/head-pin.json",
                        "resume-finalize",
                        "--session-id",
                        "never-used",
                        "--slot",
                        "post",
                        "--plan",
                        "/nonexistent/joulewise-test/plan.json",
                    ]
                )
        self.assertNotEqual(rc, 0)
        payload = json.loads(stdout.getvalue().strip().splitlines()[-1])
        self.assertEqual(payload["status"], "refused")
        self.assertEqual(
            payload["code"], "calibration_frozen_protocol_invalid"
        )
        self.assertEqual(
            payload["context"]["reason"], "acceptance_artifact_underivable"
        )


if __name__ == "__main__":
    unittest.main()
