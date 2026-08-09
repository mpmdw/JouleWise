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
import time
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
from tests.owned_process_runner import (
    OwnedProcessResult,
    OwnedPublicProcessRunner,
    assert_no_owned_process_group_survivors,
    owned_process_group_survivors,
    spawn_spinning_descendant_for_guard_test,
)
from tests.test_calibration_exits import _install_fake_writer_dependencies


REPO_ROOT = Path(__file__).resolve().parents[1]


def tearDownModule() -> None:
    assert_no_owned_process_group_survivors()


def _fresh_env() -> dict[str, str]:
    """Deliberately exclude parent lifecycle, UUID, and shell-local state."""

    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONDONTWRITEBYTECODE": "1",
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
_PRE_ONLY = {WriterStage.AFTER_PRE_FINALIZATION_BEFORE_SUPERVISOR_DISPATCH}
_POST_ONLY = {
    WriterStage.BEFORE_POST_DISPATCH,
    WriterStage.AFTER_POST_FINALIZATION_BEFORE_TERMINAL_PIN,
    WriterStage.AFTER_TERMINAL_PIN_BEFORE_OUTPUT,
}


def _applicable_slots(stage: WriterStage) -> tuple[str, ...]:
    if stage in _ACTUAL_RESERVATION:
        return ("reservation",)
    if stage in _PRE_ONLY:
        return ("pre",)
    if stage in _POST_ONLY:
        return ("post",)
    return ("pre", "post")


class CalibrationWriterCrashMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.tmp.name).resolve() / "repo"
        cls.runner = OwnedPublicProcessRunner(Path(cls.tmp.name))
        shutil.copytree(REPO_ROOT / "joulewise", cls.repo / "joulewise")
        (cls.repo / "scripts").mkdir()
        for name in (
            "recover_calibration_ledger.py",
            "reserve_calibration_window_bracket.py",
            "validate_powermetrics_fiducial.py",
        ):
            shutil.copy2(REPO_ROOT / "scripts" / name, cls.repo / "scripts" / name)
        shutil.copytree(
            REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial",
            cls.repo / "configs" / "calibration" / "powermetrics_fiducial",
        )
        cls.fake_sampler = _install_fake_writer_dependencies(cls.repo)
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
        self.t1.update(
            {
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
        )

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
        crash_stage: WriterStage | None = None,
    ) -> OwnedProcessResult:
        epoch_path = plan.with_name(f"{session_id}-epoch.json")
        t1_path = plan.with_name(f"{session_id}-t1.json")
        epoch_path.write_text(json.dumps(self.epoch), encoding="utf-8")
        t1_path.write_text(json.dumps(self.t1), encoding="utf-8")
        token = session_id.removeprefix("session-")
        environment = _fresh_env()
        return self.runner.run(
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
            env=environment,
            crash_stage=crash_stage.value if crash_stage is not None else None,
            authorize_crash=crash_stage is not None,
        )

    def _writer_cli(
        self,
        *,
        ledger: Path,
        pin: Path,
        session_id: str,
        slot: str,
        custody: Path,
        crash_stage: WriterStage,
        sampler_mode: str = "normal",
        authorize_crash: bool = True,
    ) -> OwnedProcessResult:
        identity = custody.parent / f"{session_id}-identity.json"
        identity.parent.mkdir(parents=True, exist_ok=True)
        identity.write_text(json.dumps(self.epoch) + "\n", encoding="utf-8")
        environment = {
            **_fresh_env(),
            "JW_FAKE_SAMPLER_MODE": sampler_mode,
            "JW_FAKE_HW_MODEL": self.epoch["hardware_model"],
            "JW_FAKE_OS_BUILD": self.epoch["os_build"],
            "JW_FAKE_SAMPLER_ELAPSED_NS": "200000",
            "JW_FAKE_TIME_SCALE": "0.001",
            "JW_FAKE_TIME_ORIGIN": str(time.time()),
        }
        return self.runner.run(
            [
                sys.executable,
                str(self.repo / "scripts" / "validate_powermetrics_fiducial.py"),
                "--allow-live",
                "--power-policy",
                "ac_high_power",
                "--ledger",
                str(ledger),
                "--head-pin",
                str(pin),
                "--session-id",
                session_id,
                "--slot",
                slot,
                "--attempt-id",
                f"{session_id}-{slot}",
                "--output-root",
                str(custody.parent),
                "--sampler-binary",
                str(self.fake_sampler),
                "--sampler-direct-for-test",
                "--time-scale-for-test",
                "0.001",
                "--sampler-ready-timeout-s",
                "1.0",
                "--rollover-timeout-s",
                "1.0",
                "--identity-epoch-json-for-test",
                str(identity),
            ],
            cwd=self.repo,
            env=environment,
            crash_stage=crash_stage.value,
            authorize_crash=authorize_crash,
        )

    def _enforcing_readiness(
        self,
        *,
        ledger: Path,
        pin: Path,
        session_id: str,
        slot: str,
    ) -> dict[str, object]:
        code = f"""
import json
from pathlib import Path
from joulewise.calibration_ledger import CalibrationWriterLease, calibration_readiness
ledger = Path({str(ledger)!r})
with CalibrationWriterLease(ledger):
    output = calibration_readiness(
        ledger,
        Path({str(pin)!r}),
        phase='pre-slot',
        session_id={session_id!r},
        slot={slot!r},
        attempt_id={f'{session_id}-{slot}'!r},
        enforcing_under_lease=True,
        require_committed_pin=True,
        repo_root=Path({str(self.repo)!r}),
    ).as_dict()
print(json.dumps(output, sort_keys=True))
"""
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_env(),
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        output = json.loads(completed.stdout)
        self.assertEqual(output["terminal_result"], "ready_to_arm")
        self.assertTrue(output["authorizes_arm"])
        return output

    def _kill_at_production_stage(
        self,
        *,
        ledger: Path,
        pin: Path,
        plan: Path,
        session_id: str,
        slot: str,
        custody: dict[str, Path],
        stage: WriterStage,
    ) -> OwnedProcessResult:
        if stage in _ACTUAL_RESERVATION:
            return self._reserve_cli(
                ledger=ledger,
                pin=pin,
                plan=plan,
                session_id=session_id,
                custody=custody,
                crash_stage=stage,
            )
        return self._writer_cli(
            ledger=ledger,
            pin=pin,
            session_id=session_id,
            slot=slot,
            custody=custody[slot],
            crash_stage=stage,
        )

    def _payload(self, completed: subprocess.CompletedProcess[str] | OwnedProcessResult) -> dict[str, object]:
        for stream in (completed.stdout, completed.stderr):
            try:
                value = json.loads(stream)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
        self.fail(f"no JSON payload in stdout={completed.stdout!r} stderr={completed.stderr!r}")

    def _durable_fingerprint(
        self, ledger: Path, pin: Path, custody: Path
    ) -> tuple[dict[str, str], tuple[int, int]]:
        paths = [ledger, pin]
        if custody.exists():
            paths.extend(path for path in custody.rglob("*") if path.is_file())
        fingerprint = {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
        }
        lock = ledger.with_name(f"{ledger.name}.lock")
        lock_stat = lock.stat()
        return fingerprint, (lock_stat.st_dev, lock_stat.st_ino)

    def _recover_after_crash(
        self,
        *,
        stage: WriterStage,
        ledger: Path,
        pin: Path,
        plan: Path,
        session_id: str,
        slot: str,
        custody: dict[str, Path],
    ) -> str:
        repaired = self._cli(ledger, pin, "repair")
        self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)
        repaired_payload = self._payload(repaired)
        self.assertEqual(repaired_payload["terminal_result"], "operation_completed")
        if stage in _ACTUAL_RESERVATION:
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
                self.assertEqual(self._payload(status)["code"], "calibration_session_not_found")
                inspection = repaired_payload["inspection"]
                assert isinstance(inspection, dict)
                if inspection["needs_pin_commit"]:
                    candidate = inspection["head_pin_candidate"]
                    assert isinstance(candidate, dict)
                    advanced = self._cli(
                        ledger,
                        pin,
                        "advance-head-pin",
                        "--expected-sequence",
                        str(candidate["sequence"]),
                        "--expected-digest",
                        str(candidate["head_digest"]),
                        "--operator-identity",
                        "matrix-desk-operator",
                        "--attestation-reason",
                        "reviewed reservation crash recovery control head",
                        "--execute",
                    )
                    self.assertEqual(
                        advanced.returncode, 0, advanced.stdout + advanced.stderr
                    )
                    subprocess.run(
                        ["git", "add", str(pin.relative_to(self.repo))],
                        cwd=self.repo,
                        check=True,
                    )
                    subprocess.run(
                        ["git", "commit", "-qm", f"advance {session_id}"],
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
                self.assertEqual(reserved.returncode, 0, reserved.stdout + reserved.stderr)
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
            self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
            self.assertEqual(self._payload(exited)["terminal_result"], "session_aborted")
            return "session_aborted"

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
        durable = self._payload(status)
        slot_status = durable["slots"][slot]
        assert isinstance(slot_status, dict)
        if slot_status["custody_state"] == "unreadable":
            before, lock_before = self._durable_fingerprint(
                ledger, pin, custody[slot]
            )
            resumed = self._cli(
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
            self.assertNotEqual(resumed.returncode, 0)
            refusal = self._payload(resumed)
            self.assertEqual(refusal["code"], "calibration_custody_unreadable")
            self.assertEqual(refusal["terminal_result"], "night_stopped_preserved")
            after, lock_after = self._durable_fingerprint(
                ledger, pin, custody[slot]
            )
            self.assertEqual(after, before)
            self.assertEqual(lock_after, lock_before)
            return "night_stopped_preserved"
        if durable["session_state"] == "aborted":
            return "session_aborted"
        if durable["session_state"] == "finalized":
            terminal = self._cli(
                ledger,
                pin,
                "terminal-pin",
                "--session-id",
                session_id,
            )
            self.assertEqual(terminal.returncode, 0, terminal.stdout + terminal.stderr)
            self.assertIn("sequence", self._payload(terminal))
            return "operation_completed"
        if slot_status["finalized"]:
            self.assertEqual(slot, "pre")
            self.assertEqual(durable["next_slot"], "post")
            self._enforcing_readiness(
                ledger=ledger,
                pin=pin,
                session_id=session_id,
                slot="post",
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
                f"post-ready-after-{stage.value}",
            )
            self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
            return "ready_to_arm"
        if slot_status["custody_state"] == "complete":
            resumed = self._cli(
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
            self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
            terminal_result = str(self._payload(resumed)["terminal_result"])
            self.assertIn(
                terminal_result, {"operation_completed", "session_aborted"}
            )
            return terminal_result
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
        self.assertEqual(self._payload(exited)["terminal_result"], "session_aborted")
        return "session_aborted"

    def test_torn_and_fsynced_append_boundaries_resume_from_fresh_processes(self) -> None:
        operation_stages = {
            "reservation": (
                WriterStage.RESERVATION_INTENT_WRITE,
                WriterStage.RESERVATION_INTENT_FSYNCED,
                WriterStage.RESERVATION_TARGET_WRITE,
                WriterStage.RESERVATION_TARGET_FSYNCED,
            ),
            "claim": (
                WriterStage.CLAIM_INTENT_WRITE,
                WriterStage.CLAIM_INTENT_FSYNCED,
                WriterStage.CLAIM_TARGET_WRITE,
                WriterStage.CLAIM_TARGET_FSYNCED,
            ),
            "finalization": (
                WriterStage.FINALIZATION_INTENT_WRITE,
                WriterStage.FINALIZATION_INTENT_FSYNCED,
                WriterStage.FINALIZATION_TARGET_WRITE,
                WriterStage.FINALIZATION_TARGET_FSYNCED,
            ),
        }
        witnessed: set[tuple[str, str, str]] = set()
        for operation, stages in operation_stages.items():
            slots = ("reservation",) if operation == "reservation" else ("pre", "post")
            for slot in slots:
                for stage in stages:
                    token = f"append-{operation}-{slot}-{stage.value}"
                    _root, ledger, pin, plan, session_id, custody = self._case(
                        token,
                        prefinalize=slot == "post",
                        reserved=operation != "reservation",
                    )
                    killed = self._kill_at_production_stage(
                        ledger=ledger,
                        pin=pin,
                        plan=plan,
                        session_id=session_id,
                        slot=slot,
                        custody=custody,
                        stage=stage,
                    )
                    self.assertEqual(
                        killed.returncode,
                        -signal.SIGKILL,
                        f"{token}: {killed.stderr}",
                    )
                    witnessed.add((operation, slot, stage.value))
                    self._recover_after_crash(
                        stage=stage,
                        ledger=ledger,
                        pin=pin,
                        plan=plan,
                        session_id=session_id,
                        slot="pre" if slot == "reservation" else slot,
                        custody=custody,
                    )
        expected = {
            (operation, slot, stage.value)
            for operation, stages in operation_stages.items()
            for slot in (("reservation",) if operation == "reservation" else ("pre", "post"))
            for stage in stages
        }
        self.assertEqual(witnessed, expected)

    def test_survivor_guard_detects_spinning_descendant(self) -> None:
        process = spawn_spinning_descendant_for_guard_test()
        try:
            assert process.stdout is not None
            self.assertEqual(process.stdout.readline().strip(), "SPINNING")
            self.assertTrue(owned_process_group_survivors())
            with self.assertRaisesRegex(
                AssertionError, "owned process-group survivors"
            ):
                assert_no_owned_process_group_survivors()
            process.communicate(timeout=10)
            self.assertEqual(owned_process_group_survivors(), ())
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate(timeout=10)

    def test_ambient_writer_crash_stage_is_inert_without_capability(self) -> None:
        _root, ledger, pin, _plan, session_id, custody = self._case(
            "ambient-stage-inert"
        )
        completed = self._writer_cli(
            ledger=ledger,
            pin=pin,
            session_id=session_id,
            slot="pre",
            custody=custody["pre"],
            crash_stage=WriterStage.BEFORE_WRITER_LEASE,
            authorize_crash=False,
        )
        self.assertNotEqual(completed.returncode, -signal.SIGKILL)
        self.assertIn(completed.returncode, {0, 1}, completed.stdout + completed.stderr)
        inert = [
            json.loads(line)
            for line in completed.stderr.splitlines()
            if line.startswith("{")
            and json.loads(line).get("event")
            == "joulewise_test_writer_crash_hook_inert"
        ]
        self.assertEqual(
            inert,
            [
                {
                    "event": "joulewise_test_writer_crash_hook_inert",
                    "reason": "missing_or_invalid_harness_authorization",
                    "requested_stage": "before-writer-lease",
                }
            ],
        )

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
        expected = {
            (stage, slot)
            for stage in WriterStage
            for slot in _applicable_slots(stage)
        }
        witnessed: set[tuple[WriterStage, str]] = set()
        outcomes: dict[tuple[WriterStage, str], str] = {}
        for stage in WriterStage:
            for slot in _applicable_slots(stage):
                token = f"{stage.name.lower()}-{slot}"
                _root, ledger, pin, plan, session_id, custody = self._case(
                    token,
                    prefinalize=slot == "post",
                    reserved=stage not in _ACTUAL_RESERVATION,
                )
                killed = self._kill_at_production_stage(
                    ledger=ledger,
                    pin=pin,
                    plan=plan,
                    session_id=session_id,
                    slot=slot,
                    custody=custody,
                    stage=stage,
                )
                self.assertEqual(
                    killed.returncode,
                    -signal.SIGKILL,
                    f"{stage.value}/{slot}: {killed.stderr}",
                )
                witnessed.add((stage, slot))
                outcomes[(stage, slot)] = self._recover_after_crash(
                    stage=stage,
                    ledger=ledger,
                    pin=pin,
                    plan=plan,
                    session_id=session_id,
                    slot="pre" if slot == "reservation" else slot,
                    custody=custody,
                )
        self.assertEqual(witnessed, expected)
        self.assertEqual(
            outcomes[(WriterStage.DURING_MANIFEST_ARTIFACT, "pre")],
            "night_stopped_preserved",
        )


if __name__ == "__main__":
    unittest.main()
