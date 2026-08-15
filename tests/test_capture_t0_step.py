from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from scripts import capture_t0_step as capture
from tests.test_arm_readiness_evidence_t0 import (
    SYNTHETIC_MONOTONIC_NS,
    SYNTHETIC_UTC_NOW,
    TEST_BOOT_SESSION_ID,
    author_arm_readiness_evidence_t0,
    author_environment,
    make_t0_fixture,
)
from joulewise import arm_readiness as readiness


class _Clock:
    def __init__(self, value: int) -> None:
        self.value = value

    def monotonic_ns(self) -> int:
        return self.value

    def advance(self, seconds: int) -> None:
        self.value += seconds * 1_000_000_000


class CaptureT0StepTests(unittest.TestCase):
    maxDiff = None

    def _producer_fixture(self):
        temporary, repository, pack, custody, context, input_root = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        session_receipt = json.loads(
            next(Path(temporary.name).glob("production-ledger.jsonl")).read_text(
                encoding="utf-8"
            )
        )
        shutil.rmtree(input_root)
        return (
            temporary,
            repository,
            pack,
            custody,
            context,
            input_root,
            session_receipt,
        )

    def test_produces_all_nine_inputs_then_author_reaches_normal_derivation(self) -> None:
        (
            _temporary,
            repository,
            pack,
            custody,
            _arm_context,
            input_root,
            session_receipt,
        ) = self._producer_fixture()
        tree, _raw = readiness._plan_tree(pack)
        plan_path, _relative, plan_id, plan_raw = readiness.resolve_frozen_plan(
            pack, tree
        )
        plan_sha = readiness.sha256_bytes(plan_raw)
        window_root = custody / "window-plan"
        clock = _Clock(SYNTHETIC_MONOTONIC_NS - 900 * 1_000_000_000)

        def execute(argv, *, cwd):
            command = tuple(argv)
            if "-getusingnetworktime" in command:
                stdout = b"Network Time: On\n"
                stderr = b""
            elif "-setusingnetworktime" in command:
                stdout = stderr = b""
            elif Path(command[1]).name == "quiet_mac_prep.sh":
                stdout = (
                    b"OK: passwordless powermetrics works.\n"
                    b"OK: display verification reports all online displays asleep.\n"
                    b"OK: post-arm evidence reports screensaver disengaged.\nREADY.\n"
                )
                stderr = b""
            elif Path(command[1]).name == "prewindow_check.sh":
                clock.advance(600)
                stdout = b"READY after 10 min.\n"
                stderr = b""
            elif Path(command[1]).name == "recover_calibration_ledger.py":
                stdout = json.dumps(
                    {
                        "status": "ready",
                        "early_warning_only": True,
                        "frozen_plan": {
                            "path": str(plan_path),
                            "plan_id": plan_id,
                            "sha256": plan_sha,
                        },
                    }
                ).encode("utf-8")
                stderr = b""
            elif Path(command[1]).name == "reserve_calibration_window_bracket.py":
                stdout = json.dumps(
                    {"status": "reserved", "receipt": session_receipt}
                ).encode("utf-8")
                stderr = b'{"event":"calibration_pre_reserve_authorized"}\n'
            else:
                raise AssertionError(command)
            clock.advance(1)
            return subprocess.CompletedProcess(command, 0, stdout, stderr)

        with (
            mock.patch.object(capture, "REPO_ROOT", repository),
            mock.patch.object(
                capture,
                "_current_boot_session_id",
                return_value=TEST_BOOT_SESSION_ID,
            ),
        ):
            for step_id in capture.STEP_ORDER:
                result = capture.capture_step(
                    step_id,
                    pack,
                    custody,
                    window_root,
                    prompt=lambda _message: "2026-08-13T20:30:01Z",
                    execute=execute,
                    monotonic_ns=clock.monotonic_ns,
                    utc_now=lambda: SYNTHETIC_UTC_NOW,
                )
                self.assertEqual(result["status"], "PASS")

        self.assertEqual(
            {path.name for path in input_root.iterdir()},
            {
                "arm-context.json",
                "clock-attestation.json",
                "clock-disable.json",
                "clock-prior-state.json",
                "launch-manifest.json",
                "ledger-readiness.json",
                "ledger-reservation.json",
                "prewindow-check.json",
                "quiet-mac-prep.json",
            },
        )
        for path in input_root.iterdir():
            raw = path.read_bytes()
            self.assertEqual(raw, readiness.render_json(json.loads(raw)))
        capture_value = json.loads(
            (input_root / "prewindow-check.json").read_text(encoding="utf-8")
        )
        self.assertGreaterEqual(
            capture_value["finished_monotonic_ns"]
            - capture_value["started_monotonic_ns"],
            600 * 1_000_000_000,
        )
        diagnostic = json.loads(
            json.loads(
                (input_root / "ledger-readiness.json").read_text(encoding="utf-8")
            )["stdout"]
        )
        self.assertEqual(
            diagnostic["frozen_plan"],
            {"path": str(plan_path), "plan_id": plan_id, "sha256": plan_sha},
        )
        prior = json.loads(
            (input_root / "clock-prior-state.json").read_text(encoding="utf-8")
        )
        disable = json.loads(
            (input_root / "clock-disable.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            prior["argv"],
            [
                "/usr/bin/sudo",
                "/usr/sbin/systemsetup",
                "-getusingnetworktime",
            ],
        )
        self.assertEqual(
            disable["argv"],
            [
                "/usr/bin/sudo",
                "-n",
                "/usr/sbin/systemsetup",
                "-setusingnetworktime",
                "off",
            ],
        )

        with author_environment(repository, now_monotonic_ns=clock.value + 1):
            authored = author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(authored["status"], "PASS")
        self.assertEqual(len(authored["authored_rows"]), 15)

    def test_refuses_out_of_order_step_without_executing(self) -> None:
        (
            _temporary,
            repository,
            pack,
            custody,
            _context,
            _input_root,
            _receipt,
        ) = self._producer_fixture()
        with (
            mock.patch.object(capture, "REPO_ROOT", repository),
            mock.patch.object(
                capture,
                "_current_boot_session_id",
                return_value=TEST_BOOT_SESSION_ID,
            ),
            self.assertRaises(capture.CaptureT0Error) as caught,
        ):
            capture.capture_step(
                "clock-disable",
                pack,
                custody,
                custody / "window-plan",
                execute=mock.Mock(side_effect=AssertionError("must not execute")),
            )
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_t0_capture_sequence_invalid",
        )

    def test_refuses_dollar_bearing_window_environment(self) -> None:
        (
            _temporary,
            repository,
            pack,
            custody,
            _context,
            _input_root,
            _receipt,
        ) = self._producer_fixture()
        env_path = custody / "window-plan/window.env"
        raw = env_path.read_text(encoding="utf-8")
        env_path.write_text(
            raw.replace(f"PACK_ROOT={pack}", "PACK_ROOT=$MEASUREMENT_REPO/pack"),
            encoding="utf-8",
        )
        with (
            mock.patch.object(capture, "REPO_ROOT", repository),
            mock.patch.object(
                capture,
                "_current_boot_session_id",
                return_value=TEST_BOOT_SESSION_ID,
            ),
            self.assertRaises(capture.CaptureT0Error) as caught,
        ):
            capture.capture_step(
                "clock-prior-state",
                pack,
                custody,
                custody / "window-plan",
                prompt=lambda _message: "2026-08-13T20:30:01Z",
                execute=mock.Mock(side_effect=AssertionError("must not execute")),
            )
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_t0_capture_environment_invalid",
        )

    def test_reason_code_registry_is_closed(self) -> None:
        self.assertEqual(len(capture.CAPTURE_REASON_CODES), 12)
        decision_log = (Path(__file__).resolve().parents[1] / "docs/decision_log.md").read_text(
            encoding="utf-8"
        )
        for reason_code in capture.CAPTURE_REASON_CODES:
            self.assertTrue(reason_code.startswith("evidence_author_t0_capture_"))
            self.assertEqual(decision_log.count(f"`{reason_code}`"), 1)

    def test_terminal_review_trailers_are_required_before_execution(self) -> None:
        with (
            mock.patch.object(
                readiness,
                "reviewed_main",
                return_value={"clean": True, "exact_match": True},
            ),
            mock.patch.object(
                capture,
                "_git_text",
                side_effect=["ordinary commit\n", "1" * 40],
            ),
            self.assertRaises(capture.CaptureT0Error) as caught,
        ):
            capture._verify_terminal_review(
                Path("."), Path("."), pack_sha256="2" * 64
            )
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_t0_capture_terminal_review_missing",
        )

    def test_prewindow_wait_requires_600_continuous_seconds(self) -> None:
        source = (
            Path(__file__).resolve().parents[1] / "scripts/prewindow_check.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("MIN_CLEAN_DWELL_S=600", source)
        self.assertIn('wait_started="$SECONDS"', source)
        self.assertIn('clean_since="$now"', source)
        self.assertIn('clean_elapsed=$((now - clean_since))', source)
        self.assertIn('clean_since=-1', source)
        self.assertNotIn("SETTLE_CHECKS", source)

    def test_cli_usage_error_is_a_registered_json_refusal(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/capture_t0_step.py", "not-a-step"],
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stderr, "")
        self.assertEqual(
            json.loads(completed.stdout)["reason_codes"],
            ["evidence_author_t0_capture_usage_invalid"],
        )


if __name__ == "__main__":
    unittest.main()
