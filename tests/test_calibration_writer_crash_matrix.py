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
from unittest import mock

from joulewise.uncertainty_evidence import ACTIVE_CAPTURE_ANCHOR_METHOD
from joulewise.calibration_ledger import (
    BRACKET_SESSION_ABORT_EVENT,
    BRACKET_SESSION_FINALIZATION_EVENT,
    BRACKET_SESSION_SCHEMA,
    GENESIS_DIGEST,
    GOVERNED_ARTIFACTS,
    LEDGER_SCHEMA,
    T1_FIELDS,
    append_bracket_session_receipt,
    artifact_hashes,
    claim_bracket_session_slot,
    finalize_bracket_session_slot,
)
import scripts.validate_powermetrics_fiducial as fiducial_validator
from scripts.validate_powermetrics_fiducial import WriterStage
import tests.owned_process_runner as owned_process_runner
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


class LogicalPulseAcknowledgementDeadlineTests(unittest.TestCase):
    class _Clock:
        def __init__(self) -> None:
            self.now_s = 0.0
            self.sleep_calls: list[float] = []

        def monotonic(self) -> float:
            return self.now_s

        def sleep(self, seconds: float) -> None:
            self.sleep_calls.append(seconds)
            self.now_s += seconds

    class _RunningProcess:
        @staticmethod
        def poll() -> None:
            return None

    @staticmethod
    def _ack(sequence: int, event_type: str) -> bytes:
        return (
            json.dumps(
                {
                    "schema": fiducial_validator.TEST_LOGICAL_ACK_SCHEMA,
                    "sequence": sequence,
                    "event_type": event_type,
                },
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")

    def _driver(
        self,
        fake_clock: _Clock,
        reader,
        *,
        timeout_s: float = 0.004,
        hard_timeout_s: float = 0.020,
    ):
        return fiducial_validator._LogicalTestPulseDriver(
            fiducial_validator._LogicalTestClock(0.0),
            Path("unused-injected-acknowledgement-path"),
            timeout_s=timeout_s,
            hard_timeout_s=hard_timeout_s,
            monotonic=fake_clock.monotonic,
            sleep=fake_clock.sleep,
            acknowledgement_reader=reader,
        )

    def test_progress_extends_stall_deadline_past_nominal_timeout(self) -> None:
        fake_clock = self._Clock()
        first_progress = self._ack(7, "pulse_command_on")
        second_progress = self._ack(8, "pulse_command_off")
        target = self._ack(9, "pulse_command_on")

        def reader() -> bytes:
            if fake_clock.now_s >= 0.007:
                return first_progress + second_progress + target
            if fake_clock.now_s >= 0.006:
                return first_progress + second_progress
            if fake_clock.now_s >= 0.003:
                return first_progress
            return b""

        row = self._driver(fake_clock, reader).await_acknowledgement(
            self._RunningProcess(),
            sequence=9,
            event_type="pulse_command_on",
        )

        self.assertEqual(row["sequence"], 9)
        self.assertGreater(fake_clock.now_s, 0.004)
        self.assertTrue(fake_clock.sleep_calls)

    def test_true_stall_refuses_before_outer_hard_bound(self) -> None:
        fake_clock = self._Clock()
        stalled = self._ack(7, "pulse_command_on")
        driver = self._driver(fake_clock, lambda: stalled, hard_timeout_s=0.050)

        with self.assertRaisesRegex(
            RuntimeError,
            r"test sampler acknowledgement timeout: pulse_command_off:9",
        ):
            driver.await_acknowledgement(
                self._RunningProcess(),
                sequence=9,
                event_type="pulse_command_off",
            )

        self.assertGreaterEqual(fake_clock.now_s, 0.004)
        self.assertLess(fake_clock.now_s, 0.050)

    def test_outer_hard_bound_refuses_continuous_progress(self) -> None:
        fake_clock = self._Clock()

        def reader() -> bytes:
            event_count = int(fake_clock.now_s / 0.001) + 1
            return b"".join(
                self._ack(index, "pulse_command_on")
                for index in range(event_count)
            )

        driver = self._driver(fake_clock, reader, hard_timeout_s=0.009)

        with self.assertRaisesRegex(
            RuntimeError,
            r"test sampler acknowledgement timeout: pulse_command_off:99",
        ):
            driver.await_acknowledgement(
                self._RunningProcess(),
                sequence=99,
                event_type="pulse_command_off",
            )

        self.assertGreaterEqual(fake_clock.now_s, 0.009)
        self.assertLess(fake_clock.now_s, 0.013)


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
        shutil.copy2(
            REPO_ROOT / "configs" / "calibration" / "calibration_acceptance_d079_v2_n17_r6.json",
            cls.repo / "configs" / "calibration" / "calibration_acceptance_d079_v2_n17_r6.json",
        )
        # This private synthetic repository must authenticate the estimator
        # bytes it actually copied, which are this checkout's bytes rather than
        # the issued artifact's recorded ones; this fixture re-key is test
        # custody, never an issuance or live claim. It copies the LIVE issued
        # generation (the anchor-v3 science reissue) because that is what the
        # production loader resolves by default.
        acceptance_path = (
            cls.repo
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
            relative: hashlib.sha256((cls.repo / relative).read_bytes()).hexdigest()
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
        acceptance_path.write_text(
            json.dumps(acceptance, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        old_acceptance_sha256 = hashlib.sha256(
            (
                REPO_ROOT
                / "configs"
                / "calibration"
                / "calibration_acceptance_d079_v2_n17_r6.json"
            ).read_bytes()
        ).hexdigest()
        new_acceptance_sha256 = hashlib.sha256(
            acceptance_path.read_bytes()
        ).hexdigest()
        bracketing_path = cls.repo / "joulewise" / "calibration_bracketing.py"
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
        cls.fake_sampler = _install_fake_writer_dependencies(cls.repo)
        sampler_source = cls.fake_sampler.read_text(encoding="utf-8")
        sampler_anchor_expression = (
            "str(origin + ((time.time() - origin) / time_scale)),"
        )
        if sampler_source.count(sampler_anchor_expression) != 1:
            raise AssertionError("fake sampler anchor expression changed")
        cls.fake_sampler.write_text(
            sampler_source.replace(
                sampler_anchor_expression,
                (
                    "str(origin + ((time.time() - origin) / time_scale) + "
                    "float(os.environ.get('JW_FAKE_INITIAL_OFFSET_S', '0'))),"
                ),
                1,
            ),
            encoding="utf-8",
        )
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
        projection_cell_budget: int | None = None,
        sampler_initial_offset_s: float | None = None,
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
        if sampler_initial_offset_s is not None:
            environment["JW_FAKE_INITIAL_OFFSET_S"] = str(
                sampler_initial_offset_s
            )
        command = [
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
        ]
        if projection_cell_budget is not None:
            command.extend(
                [
                    "--projection-cell-budget-for-test",
                    str(projection_cell_budget),
                ]
            )
        return self.runner.run(
            command,
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

    def test_owned_runner_bounds_inherited_pipe_wait_and_reaps_group(self) -> None:
        runner = OwnedPublicProcessRunner(Path(self.tmp.name))
        runner.communicate_timeout_s = 0.25
        descendant_pid = Path(self.tmp.name) / "inherited-pipe-descendant.pid"
        child_code = "\n".join(
            (
                "import pathlib, subprocess, sys",
                "descendant = subprocess.Popen([sys.executable, '-c', 'while True: pass'])",
                f"pathlib.Path({str(descendant_pid)!r}).write_text(str(descendant.pid))",
            )
        )
        entry_point = Path(self.tmp.name) / "inherited_pipe_parent.py"
        entry_point.write_text(child_code, encoding="utf-8")
        started = time.monotonic()
        with self.assertRaises(subprocess.TimeoutExpired):
            runner.run(
                [sys.executable, str(entry_point)],
                cwd=self.repo,
                env=_fresh_env(),
                readiness_path=descendant_pid,
                readiness_timeout_s=2.0,
            )
        self.assertLess(time.monotonic() - started, 3.0)
        self.assertEqual(owned_process_group_survivors(), ())
        descendant = int(descendant_pid.read_text(encoding="utf-8"))
        with self.assertRaises(ProcessLookupError):
            os.kill(descendant, 0)

    def test_teardown_reaps_zombie_only_group_after_term_eperm(self) -> None:
        pgid = 91_001
        process = mock.Mock()
        owned_process_runner._OWNED_PROCESS_GROUPS[pgid] = (
            owned_process_runner._OwnedGroup(
                pgid=pgid,
                child_pid=pgid,
                label="simulated-zombie-only-group",
                process=process,
            )
        )

        def killpg_outcome(_pgid: int, sig: int) -> None:
            self.assertEqual(_pgid, pgid)
            if sig == signal.SIGTERM:
                raise PermissionError(1, "simulated Darwin zombie EPERM")
            if sig == 0:
                raise ProcessLookupError(3, "simulated group ESRCH after reap")
            self.fail(f"unexpected signal {sig}")

        try:
            with mock.patch.object(
                owned_process_runner.os, "killpg", side_effect=killpg_outcome
            ):
                owned_process_runner._teardown_group(pgid, grace_s=0)
            process.wait.assert_called_once_with(timeout=0)
            self.assertNotIn(pgid, owned_process_runner._OWNED_PROCESS_GROUPS)
        finally:
            owned_process_runner._OWNED_PROCESS_GROUPS.pop(pgid, None)

    def test_teardown_propagates_persistent_eperm_for_existing_group(self) -> None:
        pgid = 91_002
        process = mock.Mock()
        owned_process_runner._OWNED_PROCESS_GROUPS[pgid] = (
            owned_process_runner._OwnedGroup(
                pgid=pgid,
                child_pid=pgid,
                label="simulated-persistent-eperm-group",
                process=process,
            )
        )

        def killpg_outcome(_pgid: int, sig: int) -> None:
            self.assertEqual(_pgid, pgid)
            raise PermissionError(1, f"simulated persistent EPERM for signal {sig}")

        try:
            with mock.patch.object(
                owned_process_runner.os, "killpg", side_effect=killpg_outcome
            ):
                with self.assertRaises(PermissionError):
                    owned_process_runner._teardown_group(pgid, grace_s=0)
            process.wait.assert_called_once_with(timeout=0)
            self.assertIn(pgid, owned_process_runner._OWNED_PROCESS_GROUPS)
        finally:
            owned_process_runner._OWNED_PROCESS_GROUPS.pop(pgid, None)

    def test_teardown_propagates_persistent_eperm_after_sigkill(self) -> None:
        pgid = 91_003
        process = mock.Mock()
        owned_process_runner._OWNED_PROCESS_GROUPS[pgid] = (
            owned_process_runner._OwnedGroup(
                pgid=pgid,
                child_pid=pgid,
                label="simulated-sigkill-eperm-group",
                process=process,
            )
        )

        def killpg_outcome(_pgid: int, sig: int) -> None:
            self.assertEqual(_pgid, pgid)
            if sig == signal.SIGTERM:
                return
            if sig == signal.SIGKILL or sig == 0:
                raise PermissionError(1, "simulated persistent SIGKILL EPERM")
            self.fail(f"unexpected signal {sig}")

        try:
            with mock.patch.object(
                owned_process_runner.os, "killpg", side_effect=killpg_outcome
            ):
                with self.assertRaises(PermissionError):
                    owned_process_runner._teardown_group(pgid, grace_s=0)
            self.assertEqual(process.wait.call_count, 2)
            self.assertIn(pgid, owned_process_runner._OWNED_PROCESS_GROUPS)
        finally:
            owned_process_runner._OWNED_PROCESS_GROUPS.pop(pgid, None)

    def test_teardown_raises_when_group_survives_successful_sigkill(self) -> None:
        pgid = 91_004
        process = mock.Mock()
        owned_process_runner._OWNED_PROCESS_GROUPS[pgid] = (
            owned_process_runner._OwnedGroup(
                pgid=pgid,
                child_pid=pgid,
                label="simulated-sigkill-survivor",
                process=process,
            )
        )
        try:
            with mock.patch.object(owned_process_runner.os, "killpg", return_value=None):
                with self.assertRaisesRegex(RuntimeError, "survived SIGKILL"):
                    owned_process_runner._teardown_group(pgid, grace_s=0)
            self.assertEqual(process.wait.call_count, 2)
            self.assertIn(pgid, owned_process_runner._OWNED_PROCESS_GROUPS)
        finally:
            owned_process_runner._OWNED_PROCESS_GROUPS.pop(pgid, None)

    def test_invalid_crash_authorization_is_preserved_and_valid_one_is_consumed(
        self,
    ) -> None:
        malformed_identity = Path(self.tmp.name) / "malformed-identity.json"
        malformed_identity.write_text("{", encoding="utf-8")
        invalid_cases = {
            "fiducial": [
                sys.executable,
                str(self.repo / "scripts" / "validate_powermetrics_fiducial.py"),
            ],
            "reservation": [
                sys.executable,
                str(self.repo / "scripts" / "reserve_calibration_window_bracket.py"),
                "--session-id",
                "invalid-authorization-session",
                "--window-id",
                "invalid-authorization-window",
                "--plan-id",
                "invalid-authorization-plan",
                "--plan-sha256",
                "0" * 64,
                "--evidence-root-id",
                "invalid-authorization-evidence",
                "--runs-root",
                str(Path(self.tmp.name) / "invalid-authorization-runs"),
                "--pre-attempt-id",
                "invalid-authorization-pre",
                "--post-attempt-id",
                "invalid-authorization-post",
                "--pre-custody-locator",
                str(Path(self.tmp.name) / "invalid-authorization-pre"),
                "--post-custody-locator",
                str(Path(self.tmp.name) / "invalid-authorization-post"),
                "--identity-epoch-json",
                str(malformed_identity),
                "--t1-bindings-json",
                str(malformed_identity),
            ],
        }
        for label, command in invalid_cases.items():
            with self.subTest(entry_point=label):
                invalid = Path(self.tmp.name) / f"caller-owned-{label}.json"
                invalid.write_text('{"nonce":"wrong"}\n', encoding="utf-8")
                invalid.chmod(0o600)
                completed = subprocess.run(
                    [
                        *command,
                        "--test-writer-crash-authorization",
                        str(invalid),
                    ],
                    cwd=self.repo,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=_fresh_env(),
                    check=False,
                )
                self.assertEqual(
                    completed.returncode,
                    2,
                    completed.stdout + completed.stderr,
                )
                refusal = json.loads(completed.stderr)
                self.assertTrue(str(refusal["code"]).startswith("calibration_"))
                self.assertTrue(invalid.exists())

        _root, ledger, pin, plan, session_id, custody = self._case(
            "valid-capability-consumed",
            reserved=False,
        )
        killed = self._reserve_cli(
            ledger=ledger,
            pin=pin,
            plan=plan,
            session_id=session_id,
            custody=custody,
            crash_stage=WriterStage.BEFORE_PRE_RESERVE_READINESS,
        )
        self.assertEqual(killed.returncode, -signal.SIGKILL)
        capability = Path(
            killed.args[killed.args.index("--test-writer-crash-authorization") + 1]
        )
        self.assertFalse(capability.exists())

    def test_two_presenters_racing_one_capability_authorize_exactly_one(self) -> None:
        entry_point = self.repo / "scripts" / "validate_powermetrics_fiducial.py"
        stage = WriterStage.BEFORE_WRITER_LEASE.value
        capability, nonce = self.runner._crash_capability(
            stage=stage,
            entry_point=entry_point,
        )
        barrier_root = Path(self.tmp.name) / "capability-race-barrier"
        barrier_root.mkdir()
        code = "\n".join(
            (
                "import os, pathlib, sys, time",
                "import scripts.validate_powermetrics_fiducial as validator",
                "real_unlink = os.unlink",
                "ready = pathlib.Path(sys.argv[3]) / ('ready-' + sys.argv[4])",
                "def synchronized_unlink(basename, *, dir_fd):",
                "    ready.write_text('ready', encoding='utf-8')",
                "    deadline = time.monotonic() + 5.0",
                "    while len(list(ready.parent.glob('ready-*'))) < 2:",
                "        if time.monotonic() >= deadline: raise RuntimeError('barrier timeout')",
                "        time.sleep(0.01)",
                "    release = ready.parent / 'winner-released'",
                "    if sys.argv[4] != '0':",
                "        while not release.exists():",
                "            if time.monotonic() >= deadline: raise RuntimeError('release timeout')",
                "            time.sleep(0.01)",
                "    try:",
                "        real_unlink(basename, dir_fd=dir_fd)",
                "    except FileNotFoundError:",
                "        ready.with_name('outcome-' + sys.argv[4]).write_text('lost', encoding='utf-8')",
                "        raise",
                "    ready.with_name('outcome-' + sys.argv[4]).write_text('won', encoding='utf-8')",
                "    release.write_text('released', encoding='utf-8')",
                "validator.os.unlink = synchronized_unlink",
                "validator._configure_writer_crash_authorization(pathlib.Path(sys.argv[1]), entry_point=pathlib.Path(sys.argv[2]))",
                "print('1' if validator._AUTHORIZED_WRITER_CRASH_STAGE else '0')",
            )
        )
        env = _fresh_env()
        env.update(
            {
                "JOULEWISE_TEST_WRITER_CRASH_STAGE": stage,
                "JOULEWISE_TEST_WRITER_CRASH_TOKEN": nonce,
                "JOULEWISE_TEST_WRITER_CRASH_CAPABILITY_ROOT": str(
                    self.runner.capability_root
                ),
            }
        )
        presenters = [
            subprocess.Popen(
                [
                    sys.executable,
                    "-c",
                    code,
                    str(capability),
                    str(entry_point),
                    str(barrier_root),
                    str(index),
                ],
                cwd=self.repo,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            for index in range(2)
        ]
        outputs = []
        try:
            for presenter in presenters:
                stdout, stderr = presenter.communicate(timeout=10)
                self.assertEqual(presenter.returncode, 0, stderr)
                outputs.append(stdout.strip())
        finally:
            for presenter in presenters:
                if presenter.poll() is None:
                    presenter.kill()
                    presenter.communicate(timeout=10)
        outcomes = sorted(
            path.read_text(encoding="utf-8")
            for path in barrier_root.glob("outcome-*")
        )
        self.assertEqual(
            outcomes,
            ["lost", "won"],
            f"authorizations={outputs}",
        )
        self.assertEqual(sorted(outputs), ["0", "1"], f"unlink={outcomes}")
        self.assertFalse(capability.exists())

    def test_swapped_capability_pathname_fails_link_count_check_closed(self) -> None:
        entry_point = Path(fiducial_validator.__file__).resolve()
        stage = WriterStage.BEFORE_WRITER_LEASE.value
        capability, nonce = self.runner._crash_capability(
            stage=stage,
            entry_point=entry_point,
        )
        retained = capability.with_name(f"{capability.name}.retained")
        replacement = capability.with_name(f"{capability.name}.replacement")
        real_unlink = os.unlink

        def swap_then_unlink(basename: str, *, dir_fd: int) -> None:
            os.link(capability, retained)
            replacement.write_text("replacement\n", encoding="utf-8")
            replacement.chmod(0o600)
            os.replace(replacement, capability)
            real_unlink(basename, dir_fd=dir_fd)

        env = {
            "JOULEWISE_TEST_WRITER_CRASH_STAGE": stage,
            "JOULEWISE_TEST_WRITER_CRASH_TOKEN": nonce,
            "JOULEWISE_TEST_WRITER_CRASH_CAPABILITY_ROOT": str(
                self.runner.capability_root
            ),
        }
        with mock.patch.dict(os.environ, env, clear=False), mock.patch.object(
            fiducial_validator.os, "unlink", side_effect=swap_then_unlink
        ):
            fiducial_validator._configure_writer_crash_authorization(
                capability,
                entry_point=entry_point,
            )
        self.assertIsNone(fiducial_validator._AUTHORIZED_WRITER_CRASH_STAGE)
        self.assertTrue(retained.exists())

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

    def test_detection_budget_refuses_with_terminal_custody_and_released_lease(
        self,
    ) -> None:
        _root, ledger, pin, plan, session_id, custody = self._case(
            "detection-budget-terminal"
        )
        completed = self._writer_cli(
            ledger=ledger,
            pin=pin,
            session_id=session_id,
            slot="pre",
            custody=custody["pre"],
            crash_stage=WriterStage.BEFORE_WRITER_LEASE,
            authorize_crash=False,
            projection_cell_budget=1,
            sampler_initial_offset_s=0.4,
        )
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        output = self._payload(completed)
        self.assertEqual(
            output["invalid_evidence_disposition"],
            "detection_nonconvergent",
        )
        self.assertEqual(
            output["detection_projection"]["diagnostics"][
                "evaluated_cell_count"
            ],
            1,
        )
        self.assertEqual(
            output["detection_projection"]["cell_budget"],
            1,
        )
        self.assertEqual(
            output["detection_projection"]["diagnostics"],
            {
                "reproducible": True,
                "evaluated_cell_count": 1,
                "trigger": "evaluated_cell_budget",
            },
        )

        evidence_path = custody["pre"] / "instrument_evidence.json"
        self.assertTrue(evidence_path.is_file())
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["status"], "invalid")
        self.assertIn("detection_nonconvergent", evidence["reasons"])
        self.assertIsNone(evidence["b_fiducial_s"])
        self.assertEqual(evidence["pulses"], [])
        self.assertEqual(
            evidence["detection_projection"],
            output["detection_projection"],
        )

        receipts = [
            json.loads(line)
            for line in ledger.read_text(encoding="utf-8").splitlines()
        ]
        business = [
            receipt
            for receipt in receipts
            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
        ]
        finalizations = [
            receipt
            for receipt in business
            if receipt.get("event") == BRACKET_SESSION_FINALIZATION_EVENT
        ]
        aborts = [
            receipt
            for receipt in business
            if receipt.get("event") == BRACKET_SESSION_ABORT_EVENT
        ]
        self.assertEqual(len(finalizations), 1)
        self.assertEqual(finalizations[0]["disposition"], "ordinary-invalid")
        self.assertEqual(
            finalizations[0]["artifact_sha256"]["instrument_evidence.json"],
            hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(len(aborts), 1)
        self.assertEqual(aborts[0]["reason"], "detection_nonconvergent")
        self.assertEqual(business[-1], aborts[0])
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
        self.assertEqual(self._payload(status)["session_state"], "aborted")
        with fiducial_validator.CalibrationWriterLease(ledger):
            pass

    def test_post_detection_budget_has_terminal_custody_and_released_lease(
        self,
    ) -> None:
        _root, ledger, pin, plan, session_id, custody = self._case(
            "post-detection-budget-terminal",
            prefinalize=True,
        )
        completed = self._writer_cli(
            ledger=ledger,
            pin=pin,
            session_id=session_id,
            slot="post",
            custody=custody["post"],
            crash_stage=WriterStage.BEFORE_WRITER_LEASE,
            authorize_crash=False,
            projection_cell_budget=1,
            sampler_initial_offset_s=0.4,
        )
        self.assertEqual(
            completed.returncode,
            1,
            completed.stdout + completed.stderr,
        )
        output = self._payload(completed)
        self.assertEqual(
            output["invalid_evidence_disposition"],
            "detection_nonconvergent",
        )
        self.assertEqual(
            output["detection_projection"]["diagnostics"],
            {
                "reproducible": True,
                "evaluated_cell_count": 1,
                "trigger": "evaluated_cell_budget",
            },
        )
        self.assertEqual(output["detection_projection"]["cell_budget"], 1)

        evidence_path = custody["post"] / "instrument_evidence.json"
        self.assertTrue(evidence_path.is_file())
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["status"], "invalid")
        self.assertIsNone(evidence["b_fiducial_s"])
        self.assertEqual(evidence["pulses"], [])
        self.assertEqual(
            evidence["detection_projection"],
            output["detection_projection"],
        )

        receipts = [
            json.loads(line)
            for line in ledger.read_text(encoding="utf-8").splitlines()
        ]
        business = [
            receipt
            for receipt in receipts
            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
        ]
        post_finalizations = [
            receipt
            for receipt in business
            if receipt.get("event") == BRACKET_SESSION_FINALIZATION_EVENT
            and receipt.get("slot") == "post"
        ]
        self.assertEqual(len(post_finalizations), 1)
        terminal = post_finalizations[0]
        self.assertEqual(terminal["disposition"], "ordinary-invalid")
        self.assertEqual(
            terminal["artifact_sha256"]["instrument_evidence.json"],
            hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(business[-1], terminal)
        self.assertFalse(
            any(
                receipt.get("event") == BRACKET_SESSION_ABORT_EVENT
                for receipt in business
            )
        )
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
        self.assertEqual(self._payload(status)["session_state"], "finalized")
        with fiducial_validator.CalibrationWriterLease(ledger):
            pass

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
