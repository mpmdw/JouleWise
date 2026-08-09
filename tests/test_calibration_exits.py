"""Cross-layer D-117 refusal inventory and public-exit witnesses."""

from __future__ import annotations

import ast
from dataclasses import dataclass, replace
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from joulewise.calibration_exits import (
    REFUSAL_BY_CODE,
    REFUSAL_INVENTORY,
    RefusalCode,
    TerminalResult,
    WitnessClass,
)
import joulewise.calibration_ledger as ledger_module
from joulewise.calibration_ledger import (
    GENESIS_DIGEST,
    GOVERNED_ARTIFACTS,
    LEDGER_SCHEMA,
    CalibrationLedgerError,
    append_bracket_session_receipt,
    canonical_json_bytes,
)
from tests.owned_process_runner import (
    OwnedProcessResult,
    OwnedPublicProcessRunner,
    PublicExecutionEvidence,
    assert_no_owned_process_group_survivors,
    next_execution_order,
)
from tests.receipt_corpus import ReceiptCorpus


REPO_ROOT = Path(__file__).resolve().parents[1]
RECOVERY_SCRIPT = REPO_ROOT / "scripts" / "recover_calibration_ledger.py"


def tearDownModule() -> None:
    assert_no_owned_process_group_survivors()


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


_PRESERVATION_EVIDENCE: dict[RefusalCode, PreservationEvidence] = {}
_PUBLIC_EXECUTION_EVIDENCE: dict[
    RefusalCode, list[PublicExecutionEvidence]
] = {}
_EXECUTED_DURABLE_WITNESS_CODES: set[RefusalCode] = set()


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
        _PRESERVATION_EVIDENCE[self.code] = evidence


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


def _install_fake_writer_dependencies(repo: Path) -> Path:
    """Install process-level external dependencies; production code stays real."""

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


class RefusalInventoryTests(unittest.TestCase):
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
            already_executed = expected & _EXECUTED_DURABLE_WITNESS_CODES
            executed = set(already_executed)
            executed.update(
                PublicGovernedExitWitnessTests.execute_cases(
                    code
                    for code in discovered
                    if REFUSAL_BY_CODE[code].witness_class is witness_class
                    and code not in already_executed
                )
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
        already_executed = expected & set(_PRESERVATION_EVIDENCE)
        executed = set(already_executed)
        executed.update(
            PublicGovernedExitWitnessTests.execute_cases(
                expected - already_executed
            )
        )
        self.assertEqual(executed, expected)
        self.assertEqual(set(_PRESERVATION_EVIDENCE), expected)
        for code, evidence in _PRESERVATION_EVIDENCE.items():
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
        _PUBLIC_EXECUTION_EVIDENCE.clear()
        executed = PublicGovernedExitWitnessTests.execute_cases(expected)
        self.assertEqual(executed, expected)
        self.assertEqual(set(_PUBLIC_EXECUTION_EVIDENCE), expected)
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
                evidence = _PUBLIC_EXECUTION_EVIDENCE[code]
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


class PublicGovernedExitWitnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name).resolve() / "repo"
        self.public_runner = OwnedPublicProcessRunner(Path(self.tmp.name))
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
        executed: set[RefusalCode] = set()
        for case in cases:
            witness = cls(methodName="runTest")
            witness.setUp()
            try:
                witness._execute_case(case)
                executed.add(case.code)
            finally:
                witness.tearDown()
        _EXECUTED_DURABLE_WITNESS_CODES.update(executed)
        return executed

    def tearDown(self) -> None:
        self.tmp.cleanup()

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
        )

    def _run_corrected_script(
        self,
        code: RefusalCode,
        script: Path,
        *args: str,
        env: dict[str, str] | None = None,
        durable_postcondition=None,
    ) -> OwnedProcessResult:
        record = REFUSAL_BY_CODE[code]
        completed = self._run_script(
            script,
            *args,
            env=env,
            refusal_code=code.value,
            registered_surface=record.correction_surface,
            durable_postcondition=durable_postcondition,
        )
        evidence = completed.public_evidence
        self.assertIsNotNone(evidence)
        assert evidence is not None
        _PUBLIC_EXECUTION_EVIDENCE.setdefault(code, []).append(evidence)
        return completed

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
        )
        self.assertEqual(
            completed.returncode,
            0,
            f"correction={code.value}\n{completed.stdout}{completed.stderr}",
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
        lines = [
            line
            for line in (completed.stdout + "\n" + completed.stderr).splitlines()
            if line.strip().startswith("{")
        ]
        self.assertTrue(lines, completed.stdout + completed.stderr)
        return json.loads(lines[-1])

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
            "JW_FAKE_SAMPLER_ELAPSED_NS": "200000",
            "JW_FAKE_TIME_SCALE": "0.025",
            "JW_FAKE_TIME_ORIGIN": str(time.time()),
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
            "anchor_method_version": (
                "powermetrics_native_second_censored_intersection_v1"
            ),
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
        holder = subprocess.Popen(
            [sys.executable, "-c", holder_code],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_cli_env(),
        )
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

    def _execute_case(self, case: WitnessCase) -> None:
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
                    writer_env = self._writer_env(state, mode="never")
                elif case.observer == "writer-rollover-failure":
                    writer_env = self._writer_env(state, mode="one")
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
                os.kill(holder.pid, signal.SIGKILL)
                holder.communicate(timeout=10)
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
            if holder is not None and holder.poll() is None:
                holder.kill()
                holder.communicate(timeout=10)
            if holder is not None:
                if holder.stdout is not None:
                    holder.stdout.close()
                if holder.stderr is not None:
                    holder.stderr.close()

    def test_parameterized_durable_public_cli_witnesses(self) -> None:
        expected = {case.code for case in WITNESS_CASES}
        executed = set(_EXECUTED_DURABLE_WITNESS_CODES)
        executed.update(self.execute_cases(expected - executed))
        self.assertEqual(executed, expected)

    def test_diagnostic_routes_never_emit_ready_to_arm_under_live_lease(self) -> None:
        holder_code = (
            "import time; from pathlib import Path; "
            "from joulewise.calibration_ledger import CalibrationWriterLease; "
            f"lease=CalibrationWriterLease(Path({str(self.ledger)!r})); "
            "lease.acquire(); print('LEASED', flush=True); time.sleep(60)"
        )
        holder = subprocess.Popen(
            [sys.executable, "-c", holder_code],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_cli_env(),
        )
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
            if holder.poll() is None:
                holder.kill()
            holder.communicate(timeout=10)

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


if __name__ == "__main__":
    unittest.main()
