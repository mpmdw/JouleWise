"""Real-process SIGKILL matrix for the D-117 writer/supervisor boundary."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest

from joulewise.calibration_ledger import (
    GENESIS_DIGEST,
    GOVERNED_ARTIFACTS,
    LEDGER_SCHEMA,
    T1_FIELDS,
    append_bracket_session_receipt,
    artifact_hashes,
    claim_bracket_session_slot,
    finalize_bracket_session_slot,
)
from scripts.validate_powermetrics_fiducial import WriterStage


REPO_ROOT = Path(__file__).resolve().parents[1]


def _fresh_env() -> dict[str, str]:
    """Deliberately exclude parent lifecycle, UUID, and shell-local state."""

    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }

_COMPLETE_OR_LATER = {
    WriterStage.ARTIFACTS_COMPLETE_BEFORE_FINALIZATION,
    WriterStage.FINALIZATION_INTENT_WRITE,
    WriterStage.FINALIZATION_INTENT_FSYNCED,
    WriterStage.FINALIZATION_TARGET_WRITE,
    WriterStage.FINALIZATION_TARGET_FSYNCED,
    WriterStage.FINALIZATION_RETURNED_BEFORE_CLOSED,
    WriterStage.AFTER_CLOSED_BEFORE_HANDLER_UNREGISTER,
    WriterStage.AFTER_PRE_FINALIZATION_BEFORE_SUPERVISOR_DISPATCH,
    WriterStage.BEFORE_POST_DISPATCH,
    WriterStage.AFTER_POST_FINALIZATION_BEFORE_TERMINAL_PIN,
    WriterStage.AFTER_TERMINAL_PIN_BEFORE_OUTPUT,
}
_ACTUAL_RESERVATION = {
    WriterStage.BEFORE_PRE_RESERVE_READINESS,
    WriterStage.AFTER_PRE_RESERVE_READINESS,
    WriterStage.RESERVATION_INTENT_WRITE,
    WriterStage.RESERVATION_INTENT_FSYNCED,
    WriterStage.RESERVATION_TARGET_WRITE,
    WriterStage.RESERVATION_TARGET_FSYNCED,
    WriterStage.RESERVATION_RETURNED,
}
_FINALIZED = {
    WriterStage.FINALIZATION_INTENT_WRITE,
    WriterStage.FINALIZATION_INTENT_FSYNCED,
    WriterStage.FINALIZATION_TARGET_WRITE,
    WriterStage.FINALIZATION_TARGET_FSYNCED,
    WriterStage.FINALIZATION_RETURNED_BEFORE_CLOSED,
    WriterStage.AFTER_CLOSED_BEFORE_HANDLER_UNREGISTER,
    WriterStage.AFTER_PRE_FINALIZATION_BEFORE_SUPERVISOR_DISPATCH,
    WriterStage.BEFORE_POST_DISPATCH,
    WriterStage.AFTER_POST_FINALIZATION_BEFORE_TERMINAL_PIN,
    WriterStage.AFTER_TERMINAL_PIN_BEFORE_OUTPUT,
}
_PARTIAL = {
    WriterStage.AFTER_CUSTODY_DIRECTORY_CREATION,
    WriterStage.AFTER_EVENT_STREAM_OPEN,
    WriterStage.AFTER_SAMPLER_SPAWN,
    WriterStage.AFTER_SAMPLER_READY,
    WriterStage.AFTER_ROLLOVER_READY,
    WriterStage.DURING_CAPTURE,
    WriterStage.AFTER_SAMPLER_TEARDOWN,
    WriterStage.DURING_RAW_EVENTS_ARTIFACT,
    WriterStage.DURING_TRACE_ARTIFACT,
    WriterStage.DURING_EVIDENCE_ARTIFACT,
    WriterStage.DURING_MANIFEST_ARTIFACT,
}
_ACTUAL_BEGIN = {
    WriterStage.BEFORE_WRITER_LEASE,
    WriterStage.AFTER_WRITER_LEASE,
    WriterStage.AFTER_REPAIR,
    WriterStage.AFTER_SLOT_VALIDATION,
    WriterStage.CLAIM_INTENT_WRITE,
    WriterStage.CLAIM_INTENT_FSYNCED,
    WriterStage.CLAIM_TARGET_WRITE,
    WriterStage.CLAIM_TARGET_FSYNCED,
    WriterStage.CLAIM_RETURNED_BEFORE_BEGUN,
    WriterStage.AFTER_BEGUN,
}
_ACTUAL_FINALIZE = {
    WriterStage.FINALIZATION_INTENT_WRITE,
    WriterStage.FINALIZATION_INTENT_FSYNCED,
    WriterStage.FINALIZATION_TARGET_WRITE,
    WriterStage.FINALIZATION_TARGET_FSYNCED,
    WriterStage.FINALIZATION_RETURNED_BEFORE_CLOSED,
    WriterStage.AFTER_CLOSED_BEFORE_HANDLER_UNREGISTER,
    WriterStage.AFTER_PRE_FINALIZATION_BEFORE_SUPERVISOR_DISPATCH,
    WriterStage.AFTER_POST_FINALIZATION_BEFORE_TERMINAL_PIN,
    WriterStage.AFTER_TERMINAL_PIN_BEFORE_OUTPUT,
}


class CalibrationWriterCrashMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.tmp.name).resolve() / "repo"
        shutil.copytree(REPO_ROOT / "joulewise", cls.repo / "joulewise")
        (cls.repo / "scripts").mkdir()
        for name in (
            "recover_calibration_ledger.py",
            "reserve_calibration_window_bracket.py",
            "validate_powermetrics_fiducial.py",
        ):
            shutil.copy2(REPO_ROOT / "scripts" / name, cls.repo / "scripts" / name)
        subprocess.run(["git", "init", "-q"], cwd=cls.repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "tests@joulewise.invalid"],
            cwd=cls.repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "JouleWise tests"],
            cwd=cls.repo,
            check=True,
        )
        subprocess.run(["git", "add", "."], cwd=cls.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "matrix runtime"], cwd=cls.repo, check=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.epoch = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        self.t1 = {field: f"value-{field}" for field in T1_FIELDS}
        self.t1.update(self.epoch)

    def _case(
        self,
        token: str,
        *,
        prefinalize: bool = False,
        reserved: bool = True,
    ):
        root = self.repo / "cases" / token
        root.mkdir(parents=True)
        ledger = root / "ledger.jsonl"
        pin = root / "head.json"
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
        subprocess.run(["git", "add", str(pin.relative_to(self.repo))], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", f"pin {token}"], cwd=self.repo, check=True)
        session_id = f"session-{token}"
        plan = root / "plan.json"
        plan.write_text(json.dumps({"plan_id": f"plan-{token}"}) + "\n", encoding="utf-8")
        runs_root = root / "runs"
        custody = {
            slot: runs_root / "instrument_validation" / f"{session_id}-{slot}"
            for slot in ("pre", "post")
        }
        if reserved:
            append_bracket_session_receipt(
                ledger,
                session_id=session_id,
                window_id=f"window-{token}",
                plan_id=f"plan-{token}",
                plan_sha256=hashlib.sha256(plan.read_bytes()).hexdigest(),
                evidence_root_id=f"evidence-{token}",
                runs_root=runs_root,
                slots={
                    slot: {
                        "attempt_id": f"{session_id}-{slot}",
                        "custody_locator": str(custody[slot]),
                        "identity_epoch": self.epoch,
                        "t1_bindings": self.t1,
                    }
                    for slot in ("pre", "post")
                },
                head_pin_path=pin,
                require_committed_pin=False,
                repo_root=self.repo,
            )
        if prefinalize:
            if not reserved:
                raise AssertionError("prefinalize requires a reservation")
            self._complete(custody["pre"], f"{session_id}-pre")
            claim_bracket_session_slot(
                ledger,
                session_id=session_id,
                slot="pre",
                attempt_id=f"{session_id}-pre",
            )
            finalize_bracket_session_slot(
                ledger,
                session_id=session_id,
                slot="pre",
                disposition="valid",
                custody_locator=str(custody["pre"]),
                artifact_sha256=artifact_hashes(custody["pre"]),
                identity_epoch=self.epoch,
                t1_bindings=self.t1,
                capture_wall_time_s="99.0",
                exact_bound_lexeme_s="0.025",
            )
        return root, ledger, pin, plan, session_id, custody

    def _complete(self, root: Path, attempt_id: str) -> None:
        (root / "raw").mkdir(parents=True)
        payloads = {
            "raw/powermetrics.plist": b"raw\n",
            "events.jsonl": b'{"event_type":"capture"}\n',
            "power_trace.csv": b"timestamp_s,power_w\n1,2\n",
        }
        for relative, raw in payloads.items():
            (root / relative).write_bytes(raw)
        evidence = {
            "validation_id": attempt_id,
            "status": "valid",
            "b_fiducial_s": 0.025,
            "capture_wall_time_s": 99.0,
            "bindings": self.t1,
            "artifact_sha256": {
                name: hashlib.sha256(raw).hexdigest()
                for name, raw in payloads.items()
            },
        }
        (root / "instrument_evidence.json").write_text(
            json.dumps(evidence, sort_keys=True) + "\n", encoding="utf-8"
        )
        manifest = {
            "validation_id": attempt_id,
            "artifacts": {
                name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                for name in GOVERNED_ARTIFACTS
                if name != "manifest.json"
            },
        }
        (root / "manifest.json").write_text(
            json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8"
        )

    def _cli(self, ledger: Path, pin: Path, *args: str):
        return subprocess.run(
            [
                sys.executable,
                str(self.repo / "scripts" / "recover_calibration_ledger.py"),
                "--ledger",
                str(ledger),
                "--head-pin",
                str(pin),
                *args,
            ],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_env(),
            check=False,
        )

    def _reserve_cli(
        self,
        *,
        ledger: Path,
        pin: Path,
        plan: Path,
        session_id: str,
        custody: dict[str, Path],
    ) -> subprocess.CompletedProcess[str]:
        epoch_path = plan.with_name(f"{session_id}-epoch.json")
        t1_path = plan.with_name(f"{session_id}-t1.json")
        epoch_path.write_text(json.dumps(self.epoch), encoding="utf-8")
        t1_path.write_text(json.dumps(self.t1), encoding="utf-8")
        token = session_id.removeprefix("session-")
        return subprocess.run(
            [
                sys.executable,
                str(self.repo / "scripts" / "reserve_calibration_window_bracket.py"),
                "--ledger",
                str(ledger),
                "--head-pin",
                str(pin),
                "--session-id",
                session_id,
                "--window-id",
                f"window-{session_id}",
                "--plan-id",
                f"plan-{token}",
                "--plan-sha256",
                hashlib.sha256(plan.read_bytes()).hexdigest(),
                "--plan",
                str(plan),
                "--evidence-root-id",
                f"evidence-{session_id}",
                "--runs-root",
                str(custody["pre"].parents[1]),
                "--pre-attempt-id",
                f"{session_id}-pre",
                "--post-attempt-id",
                f"{session_id}-post",
                "--pre-custody-locator",
                str(custody["pre"]),
                "--post-custody-locator",
                str(custody["post"]),
                "--identity-epoch-json",
                str(epoch_path),
                "--t1-bindings-json",
                str(t1_path),
                "--execute",
            ],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_env(),
            check=False,
        )

    def _kill_at_projection(
        self,
        *,
        ledger: Path,
        pin: Path,
        plan: Path,
        session_id: str,
        slot: str,
        custody: Path,
        stage: WriterStage,
        projection: str,
    ) -> subprocess.CompletedProcess[str]:
        if stage in _ACTUAL_RESERVATION:
            action = f"""writer._writer_stage(WriterStage.BEFORE_PRE_RESERVE_READINESS)
with CalibrationWriterLease(ledger):
    ready = calibration_readiness(ledger, Path({str(pin)!r}), phase='pre-reserve', enforcing_under_lease=False, require_committed_pin=False, repo_root=Path({str(self.repo)!r}))
    if ready.status != 'ready':
        raise CalibrationLedgerError(ready.refusal_code)
    writer._writer_stage(WriterStage.AFTER_PRE_RESERVE_READINESS)
    append_bracket_session_receipt(
        ledger,
        session_id={session_id!r},
        window_id={f'window-{session_id}'!r},
        plan_id={f'plan-{session_id.removeprefix("session-")}'!r},
        plan_sha256={hashlib.sha256(plan.read_bytes()).hexdigest()!r},
        evidence_root_id={f'evidence-{session_id}'!r},
        runs_root=Path({str(custody.parents[1])!r}),
        slots={{role: {{'attempt_id': f'{session_id}-{{role}}', 'custody_locator': str(Path({str(custody.parents[1])!r}) / 'instrument_validation' / f'{session_id}-{{role}}'), 'identity_epoch': {self.epoch!r}, 't1_bindings': {self.t1!r}}} for role in ('pre', 'post')}},
        head_pin_path=Path({str(pin)!r}),
        require_committed_pin=False,
        repo_root=Path({str(self.repo)!r}),
        _stage_boundary=lambda boundary: writer._writer_stage({{'intent-write': WriterStage.RESERVATION_INTENT_WRITE, 'intent-fsynced': WriterStage.RESERVATION_INTENT_FSYNCED, 'target-write': WriterStage.RESERVATION_TARGET_WRITE, 'target-fsynced': WriterStage.RESERVATION_TARGET_FSYNCED}}[boundary]),
    )
    writer._writer_stage(WriterStage.RESERVATION_RETURNED)"""
        elif stage in _ACTUAL_BEGIN:
            action = "lifecycle.begin()"
        elif stage in _ACTUAL_FINALIZE:
            supervisor = ""
            if stage == WriterStage.AFTER_PRE_FINALIZATION_BEFORE_SUPERVISOR_DISPATCH:
                supervisor = (
                    "\nwriter._writer_stage(WriterStage."
                    "AFTER_PRE_FINALIZATION_BEFORE_SUPERVISOR_DISPATCH)"
                )
            elif slot == "pre" and stage in {
                WriterStage.AFTER_POST_FINALIZATION_BEFORE_TERMINAL_PIN,
                WriterStage.AFTER_TERMINAL_PIN_BEFORE_OUTPUT,
            }:
                supervisor = f"\nwriter._writer_stage(WriterStage({stage.value!r}))"
            action = f"lifecycle.begin()\nmake_complete()\nlifecycle.capture_wall_time_s = '99.0'\nlifecycle.exact_bound_lexeme_s = '0.025'\nlifecycle.finalize('valid'){supervisor}"
        elif stage == WriterStage.BEFORE_POST_DISPATCH:
            action = "writer._writer_stage(WriterStage.BEFORE_POST_DISPATCH)"
        else:
            custody_setup = (
                "\nmake_partial()"
                if projection == "partial"
                else "\nmake_complete()"
                if projection == "complete"
                else ""
            )
            action = f"""lifecycle.begin(){custody_setup}
writer._writer_stage(WriterStage({stage.value!r}))"""
        code = f"""
import hashlib, json, os, signal
from pathlib import Path
import scripts.validate_powermetrics_fiducial as writer
from scripts.validate_powermetrics_fiducial import WriterStage, _CaptureLedgerLifecycle
from joulewise.calibration_ledger import CalibrationLedgerError, CalibrationWriterLease, append_bracket_session_receipt, calibration_readiness
ledger = Path({str(ledger)!r})
target = WriterStage({stage.value!r})
def crash_at_stage(observed):
    if observed == target:
        os.kill(os.getpid(), signal.SIGKILL)
writer._writer_stage = crash_at_stage
custody = Path({str(custody)!r})
def make_partial():
    (custody / 'raw').mkdir(parents=True)
    (custody / 'raw' / 'powermetrics.plist').write_bytes(b'partial')
def make_complete():
    (custody / 'raw').mkdir(parents=True)
    payloads = {{
        'raw/powermetrics.plist': b'raw\\n',
        'events.jsonl': b'{{"event_type":"capture"}}\\n',
        'power_trace.csv': b'timestamp_s,power_w\\n1,2\\n',
    }}
    for relative, raw in payloads.items():
        (custody / relative).write_bytes(raw)
    evidence = {{
        'validation_id': {f'{session_id}-{slot}'!r},
        'status': 'valid',
        'b_fiducial_s': 0.025,
        'capture_wall_time_s': 99.0,
        'bindings': {self.t1!r},
        'artifact_sha256': {{name: hashlib.sha256(raw).hexdigest() for name, raw in payloads.items()}},
    }}
    (custody / 'instrument_evidence.json').write_text(json.dumps(evidence, sort_keys=True) + '\\n')
    names = ('raw/powermetrics.plist', 'events.jsonl', 'power_trace.csv', 'instrument_evidence.json')
    manifest = {{'validation_id': {f'{session_id}-{slot}'!r}, 'artifacts': {{name: hashlib.sha256((custody / name).read_bytes()).hexdigest() for name in names}}}}
    (custody / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True) + '\\n')
lifecycle = _CaptureLedgerLifecycle(
    ledger_path=ledger,
    head_pin_path=Path({str(pin)!r}),
    attempt_id={f'{session_id}-{slot}'!r},
    custody_locator={str(custody)!r},
    identity_epoch={self.epoch!r},
    t1_bindings={self.t1!r},
    session_id={session_id!r},
    slot={slot!r},
    require_committed_pin=False,
)
{action}
raise SystemExit('stage hook was not reached')
"""
        return subprocess.run(
            [sys.executable, "-c", code],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_env(),
            check=False,
        )

    def _kill_during_append(
        self,
        *,
        operation: str,
        crash_point: str,
        ledger: Path,
        pin: Path,
        plan: Path,
        session_id: str,
        custody: Path,
        slot: str,
    ) -> subprocess.CompletedProcess[str]:
        runs_root = custody.parents[1]
        reservation = f"""
ledger.append_bracket_session_receipt(
    ledger_path,
    session_id={session_id!r},
    window_id={f'window-{session_id}'!r},
    plan_id={f'plan-{session_id.removeprefix("session-")}'!r},
    plan_sha256={hashlib.sha256(plan.read_bytes()).hexdigest()!r},
    evidence_root_id={f'evidence-{session_id}'!r},
    runs_root=Path({str(runs_root)!r}),
    slots={{
        role: {{
            'attempt_id': f'{session_id}-{{role}}',
            'custody_locator': str(Path({str(runs_root)!r}) / 'instrument_validation' / f'{session_id}-{{role}}'),
            'identity_epoch': {self.epoch!r},
            't1_bindings': {self.t1!r},
        }}
        for role in ('pre', 'post')
    }},
    head_pin_path=Path({str(pin)!r}),
    require_committed_pin=False,
    repo_root=Path({str(self.repo)!r}),
)
"""
        claim = f"""
ledger.claim_bracket_session_slot(
    ledger_path,
    session_id={session_id!r},
    slot={slot!r},
    attempt_id={f'{session_id}-{slot}'!r},
)
"""
        finalization = f"""
ledger.finalize_bracket_session_slot(
    ledger_path,
    session_id={session_id!r},
    slot={slot!r},
    disposition='valid',
    custody_locator={str(custody)!r},
    artifact_sha256=ledger.artifact_hashes(Path({str(custody)!r})),
    identity_epoch={self.epoch!r},
    t1_bindings={self.t1!r},
    capture_wall_time_s='99.0',
    exact_bound_lexeme_s='0.025',
)
"""
        action = {
            "reservation": reservation,
            "claim": claim,
            "finalization": finalization,
        }[operation]
        code = f"""
import os, signal
from pathlib import Path
import joulewise.calibration_ledger as ledger

ledger_path = Path({str(ledger)!r})
crash_point = {crash_point!r}
write_calls = [0]
real_write = ledger._write_ledger_append_payload

def crash_write(handle, payload):
    write_calls[0] += 1
    crash_call = 1 if crash_point == 'during-intent' else 2
    if crash_point.startswith('during-') and write_calls[0] == crash_call:
        handle.write(payload[:max(1, len(payload) // 3)])
        handle.flush()
        os.fsync(handle.fileno())
        os.kill(os.getpid(), signal.SIGKILL)
    return real_write(handle, payload)

def crash_after(stage):
    expected = {{
        'after-intent-fsync': 'intent',
        'after-target-fsync': 'target',
    }}.get(crash_point)
    if stage == expected:
        os.kill(os.getpid(), signal.SIGKILL)

ledger._write_ledger_append_payload = crash_write
ledger._after_ledger_fsync = crash_after
with ledger.CalibrationWriterLease(ledger_path):
{''.join('    ' + line + '\n' for line in action.splitlines())}
raise SystemExit('crash hook was not reached')
"""
        return subprocess.run(
            [sys.executable, "-c", code],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_env(),
            check=False,
        )

    def test_torn_and_fsynced_append_boundaries_resume_from_fresh_processes(self) -> None:
        crash_points = (
            "during-intent",
            "after-intent-fsync",
            "during-target",
            "after-target-fsync",
        )
        witnessed: set[tuple[str, str, str]] = set()
        for operation in ("reservation", "claim", "finalization"):
            slots = ("pre",) if operation == "reservation" else ("pre", "post")
            for slot in slots:
                for crash_point in crash_points:
                    token = f"append-{operation}-{slot}-{crash_point}"
                    _root, ledger, pin, plan, session_id, custody = self._case(
                        token,
                        prefinalize=slot == "post",
                        reserved=operation != "reservation",
                    )
                    if operation == "finalization":
                        self._complete(custody[slot], f"{session_id}-{slot}")
                        claim_bracket_session_slot(
                            ledger,
                            session_id=session_id,
                            slot=slot,
                            attempt_id=f"{session_id}-{slot}",
                        )
                    killed = self._kill_during_append(
                        operation=operation,
                        crash_point=crash_point,
                        ledger=ledger,
                        pin=pin,
                        plan=plan,
                        session_id=session_id,
                        custody=custody[slot],
                        slot=slot,
                    )
                    self.assertEqual(killed.returncode, -signal.SIGKILL, killed.stderr)
                    witnessed.add((operation, slot, crash_point))
                    repaired = self._cli(ledger, pin, "repair")
                    self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)
                    self.assertEqual(
                        json.loads(repaired.stdout)["terminal_result"],
                        "operation_completed",
                    )
                    if operation == "reservation":
                        continue
                    status = self._cli(
                        ledger,
                        pin,
                        "session-status",
                        "--session-id",
                        session_id,
                        "--plan",
                        str(plan),
                    )
                    self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
                    durable = json.loads(status.stdout)
                    if operation == "claim":
                        exited = self._cli(
                            ledger,
                            pin,
                            "abort-session",
                            "--session-id",
                            session_id,
                            "--plan",
                            str(plan),
                            "--reason",
                            f"append-crash-{crash_point}",
                        )
                        self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
                        self.assertEqual(json.loads(exited.stdout)["terminal_result"], "session_aborted")
                    elif durable["slots"][slot]["finalized"]:
                        self.assertIn(durable["session_state"], {"open", "finalized"})
                    else:
                        exited = self._cli(
                            ledger,
                            pin,
                            "resume-finalize",
                            "--session-id",
                            session_id,
                            "--slot",
                            slot,
                            "--plan",
                            str(plan),
                        )
                        self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
                        self.assertEqual(json.loads(exited.stdout)["terminal_result"], "operation_completed")
        expected = {
            (operation, slot, crash_point)
            for operation in ("reservation", "claim", "finalization")
            for slot in (("pre",) if operation == "reservation" else ("pre", "post"))
            for crash_point in crash_points
        }
        self.assertEqual(witnessed, expected)

    def test_two_process_lease_contention_then_fresh_resume(self) -> None:
        _root, ledger, pin, plan, session_id, custody = self._case("lease-contention")
        self._complete(custody["pre"], f"{session_id}-pre")
        holder_code = f"""
import time
from pathlib import Path
from joulewise.calibration_ledger import CalibrationWriterLease, claim_bracket_session_slot
ledger = Path({str(ledger)!r})
with CalibrationWriterLease(ledger):
    claim_bracket_session_slot(ledger, session_id={session_id!r}, slot='pre', attempt_id={f'{session_id}-pre'!r})
    print('LEASED', flush=True)
    time.sleep(60)
"""
        holder = subprocess.Popen(
            [sys.executable, "-c", holder_code],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_env(),
        )
        try:
            assert holder.stdout is not None
            self.assertEqual(holder.stdout.readline().strip(), "LEASED")
            contender = self._cli(
                ledger,
                pin,
                "resume-finalize",
                "--session-id",
                session_id,
                "--slot",
                "pre",
                "--plan",
                str(plan),
            )
            self.assertEqual(contender.returncode, 2)
            self.assertEqual(
                json.loads(contender.stdout)["code"],
                "calibration_live_writer_contention",
            )
            os.kill(holder.pid, signal.SIGKILL)
            holder.communicate(timeout=10)
            resumed = self._cli(
                ledger,
                pin,
                "resume-finalize",
                "--session-id",
                session_id,
                "--slot",
                "pre",
                "--plan",
                str(plan),
            )
            self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
            self.assertEqual(json.loads(resumed.stdout)["terminal_result"], "operation_completed")
        finally:
            if holder.poll() is None:
                os.kill(holder.pid, signal.SIGKILL)
                holder.communicate(timeout=10)

    def test_every_exact_stage_pre_and_post_sigkill_reaches_fresh_governed_exit(self) -> None:
        self.assertEqual(len({stage.value for stage in WriterStage}), len(WriterStage))
        in_capture_shapes: dict[str, set[tuple[object, ...]]] = {}
        witnessed: set[tuple[WriterStage, str]] = set()
        for stage in WriterStage:
            for slot in ("pre", "post"):
                token = f"{stage.name.lower()}-{slot}"
                root, ledger, pin, plan, session_id, custody = self._case(
                    token,
                    prefinalize=(
                        stage == WriterStage.BEFORE_POST_DISPATCH
                        or slot == "post" and stage not in _ACTUAL_RESERVATION
                    ),
                    reserved=stage not in _ACTUAL_RESERVATION,
                )
                del root
                projection = (
                    "finalized"
                    if stage in _FINALIZED
                    else "complete"
                    if stage in _COMPLETE_OR_LATER
                    else "partial"
                    if stage in _PARTIAL
                    else "early"
                )
                killed = self._kill_at_projection(
                    ledger=ledger,
                    pin=pin,
                    plan=plan,
                    session_id=session_id,
                    slot=slot,
                    custody=custody[slot],
                    stage=stage,
                    projection=projection,
                )
                self.assertEqual(
                    killed.returncode,
                    -signal.SIGKILL,
                    f"{stage.value}/{slot}: {killed.stderr}",
                )
                witnessed.add((stage, slot))
                if stage in _ACTUAL_RESERVATION:
                    repaired = self._cli(ledger, pin, "repair")
                    self.assertEqual(
                        repaired.returncode, 0, repaired.stdout + repaired.stderr
                    )
                    physical = json.loads(repaired.stdout)["inspection"]
                    status = self._cli(
                        ledger,
                        pin,
                        "session-status",
                        "--session-id",
                        session_id,
                        "--plan",
                        str(plan),
                    )
                    if status.returncode != 0:
                        self.assertEqual(
                            json.loads(status.stdout)["code"],
                            "calibration_session_not_found",
                        )
                        if physical["needs_pin_commit"]:
                            candidate = physical["head_pin_candidate"]
                            advanced = self._cli(
                                ledger,
                                pin,
                                "advance-head-pin",
                                "--expected-sequence",
                                str(candidate["sequence"]),
                                "--expected-digest",
                                candidate["head_digest"],
                                "--operator-identity",
                                "matrix-desk-operator",
                                "--attestation-reason",
                                "reviewed crash recovery control head",
                                "--execute",
                            )
                            self.assertEqual(
                                advanced.returncode,
                                0,
                                advanced.stdout + advanced.stderr,
                            )
                            subprocess.run(
                                ["git", "add", str(pin.relative_to(self.repo))],
                                cwd=self.repo,
                                check=True,
                            )
                            subprocess.run(
                                ["git", "commit", "-qm", f"advance {token}"],
                                cwd=self.repo,
                                check=True,
                            )
                        reserved = self._reserve_cli(
                            ledger=ledger,
                            pin=pin,
                            plan=plan,
                            session_id=session_id,
                            custody=custody,
                        )
                        self.assertEqual(
                            reserved.returncode,
                            0,
                            reserved.stdout + reserved.stderr,
                        )
                        self.assertEqual(
                            json.loads(reserved.stdout)["terminal_result"],
                            "operation_completed",
                        )
                    exited = self._cli(
                        ledger,
                        pin,
                        "abort-session",
                        "--session-id",
                        session_id,
                        "--plan",
                        str(plan),
                        "--reason",
                        f"reservation-sigkill-{stage.value}",
                    )
                    self.assertEqual(
                        exited.returncode, 0, exited.stdout + exited.stderr
                    )
                    self.assertEqual(
                        json.loads(exited.stdout)["terminal_result"],
                        "session_aborted",
                    )
                    continue
                status = self._cli(
                    ledger,
                    pin,
                    "session-status",
                    "--session-id",
                    session_id,
                    "--plan",
                    str(plan),
                )
                self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
                durable = json.loads(status.stdout)
                shape = (
                    durable["session_state"],
                    durable["next_slot"],
                    durable["slots"][slot]["custody_state"],
                    durable["inspection_state"],
                )
                if stage in _PARTIAL:
                    in_capture_shapes.setdefault(slot, set()).add(shape)
                if projection == "finalized":
                    terminal_result = (
                        "operation_completed"
                        if durable["session_state"] == "finalized"
                        else "ready_to_arm"
                    )
                    self.assertIn(terminal_result, {"operation_completed", "ready_to_arm"})
                elif projection == "complete":
                    exited = self._cli(
                        ledger,
                        pin,
                        "resume-finalize",
                        "--session-id",
                        session_id,
                        "--slot",
                        slot,
                        "--plan",
                        str(plan),
                    )
                    self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
                    self.assertEqual(json.loads(exited.stdout)["terminal_result"], "operation_completed")
                else:
                    exited = self._cli(
                        ledger,
                        pin,
                        "abort-session",
                        "--session-id",
                        session_id,
                        "--plan",
                        str(plan),
                        "--reason",
                        f"sigkill-{stage.value}",
                    )
                    self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
                    self.assertEqual(json.loads(exited.stdout)["terminal_result"], "session_aborted")
        self.assertEqual(
            witnessed,
            {(stage, slot) for stage in WriterStage for slot in ("pre", "post")},
        )
        self.assertTrue(
            all(len(observed) == 1 for observed in in_capture_shapes.values()),
            in_capture_shapes,
        )


if __name__ == "__main__":
    unittest.main()
