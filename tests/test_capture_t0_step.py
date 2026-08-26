from __future__ import annotations

import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
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

    @staticmethod
    def _terminal_review_message(tree_oid: str, packs: tuple[str, ...]) -> str:
        return "\n".join(
            (
                "terminal review",
                "",
                "JouleWise-Terminal-Review: PASS",
                f"JouleWise-Terminal-Review-Tree-Oid: {tree_oid}",
                *(
                    f"JouleWise-Terminal-Review-Pack-Sha256: {pack}"
                    for pack in packs
                ),
            )
        )

    def _verify_terminal_review_for(
        self, message: str, *, pack_sha256: str
    ) -> None:
        with (
            mock.patch.object(
                readiness,
                "reviewed_main",
                return_value={"clean": True, "exact_match": True},
            ),
            mock.patch.object(
                capture,
                "_git_text",
                side_effect=[message, "1" * 40],
            ),
        ):
            capture._verify_terminal_review(
                Path("."), Path("."), pack_sha256=pack_sha256
            )

    def _assert_terminal_review_refuses(
        self, message: str, *, pack_sha256: str
    ) -> None:
        with self.assertRaises(capture.CaptureT0Error) as caught:
            self._verify_terminal_review_for(message, pack_sha256=pack_sha256)
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_t0_capture_terminal_review_missing",
        )

    def test_terminal_review_three_pack_message_accepts_each_pack(self) -> None:
        tree_oid = "1" * 40
        packs = ("a" * 64, "b" * 64, "c" * 64)
        message = self._terminal_review_message(tree_oid, packs)
        for pack_sha256 in packs:
            with self.subTest(pack_sha256=pack_sha256):
                self._verify_terminal_review_for(
                    message, pack_sha256=pack_sha256
                )

    def test_terminal_review_foreign_pack_list_refuses(self) -> None:
        message = self._terminal_review_message(
            "1" * 40, ("b" * 64, "c" * 64)
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_duplicate_pack_line_refuses(self) -> None:
        message = self._terminal_review_message(
            "1" * 40, ("a" * 64, "a" * 64)
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_single_pack_message_still_passes(self) -> None:
        message = self._terminal_review_message("1" * 40, ("a" * 64,))
        self._verify_terminal_review_for(message, pack_sha256="a" * 64)

    def test_terminal_review_pack_line_with_trailing_token_refuses(self) -> None:
        message = self._terminal_review_message("1" * 40, ()).replace(
            "JouleWise-Terminal-Review-Tree-Oid: " + "1" * 40,
            "JouleWise-Terminal-Review-Tree-Oid: "
            + "1" * 40
            + "\nJouleWise-Terminal-Review-Pack-Sha256: "
            + "a" * 64
            + " trailing",
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_malformed_pack_digest_refuses(self) -> None:
        message = self._terminal_review_message(
            "1" * 40, ("a" * 64, "not-a-sha256")
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_duplicate_pass_line_refuses(self) -> None:
        message = (
            self._terminal_review_message("1" * 40, ("a" * 64,))
            + "\nJouleWise-Terminal-Review: PASS"
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_duplicate_tree_oid_line_refuses(self) -> None:
        message = (
            self._terminal_review_message("1" * 40, ("a" * 64,))
            + "\nJouleWise-Terminal-Review-Tree-Oid: "
            + "1" * 40
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_empty_pack_list_refuses(self) -> None:
        message = self._terminal_review_message("1" * 40, ())
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

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

        def prompt(message: str) -> str:
            if "trusted-clock" in message:
                return "2026-08-13T20:30:01Z"
            if "prior network-time" in message:
                return "Network Time: On"
            raise AssertionError(message)

        def execute(argv, *, cwd):
            command = tuple(argv)
            if "-setusingnetworktime" in command:
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
                result = capture._capture_step_for_test(
                    step_id,
                    pack,
                    custody,
                    window_root,
                    prompt=prompt,
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
                "operator-interactive",
                "network-time-prior-state",
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
            capture._capture_step_for_test(
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

    def test_invalid_e8_capture_does_not_unlock_e9_reservation(self) -> None:
        (
            _temporary,
            repository,
            pack,
            custody,
            _context,
            input_root,
            _receipt,
        ) = self._producer_fixture()
        with (
            mock.patch.object(capture, "REPO_ROOT", repository),
            mock.patch.object(
                capture,
                "_current_boot_session_id",
                return_value=TEST_BOOT_SESSION_ID,
            ),
        ):
            context = capture._load_context(pack, custody, custody / "window-plan")
        input_root.mkdir(parents=True)
        outputs = {
            "clock-prior-state": ("Network Time: On\n", "", 10, 20),
            "clock-disable": ("", "", 30, 40),
            "quiet-mac-prep": (
                "OK: passwordless powermetrics works.\n"
                "OK: display verification reports all online displays asleep.\n"
                "OK: post-arm evidence reports screensaver disengaged.\n",
                "",
                50,
                60,
            ),
            "prewindow-check": (
                "READY after 10 min.\n",
                "",
                100,
                100 + 600 * 1_000_000_000,
            ),
        }
        for prior, (stdout, stderr, started, finished) in outputs.items():
            value = {
                "schema_version": capture.COMMAND_CAPTURE_SCHEMA,
                "step_id": prior,
                "argv": list(capture._command_for_step(context, prior)),
                "cwd": str(repository),
                "exit_code": 0,
                "stdout": stdout,
                "stderr": stderr,
                "started_monotonic_ns": started,
                "finished_monotonic_ns": finished,
                "boot_session_id": TEST_BOOT_SESSION_ID,
            }
            (input_root / capture.STEP_FILENAMES[prior]).write_bytes(
                readiness.render_json(value)
            )
        invalid_diagnostic = subprocess.CompletedProcess(
            (), 0, b'{"status":"not-ready"}\n', b""
        )
        with (
            mock.patch.object(capture, "REPO_ROOT", repository),
            mock.patch.object(
                capture,
                "_current_boot_session_id",
                return_value=TEST_BOOT_SESSION_ID,
            ),
            self.assertRaises(capture.CaptureT0Error) as invalid,
        ):
            capture._capture_step_for_test(
                "ledger-readiness",
                pack,
                custody,
                custody / "window-plan",
                execute=mock.Mock(return_value=invalid_diagnostic),
            )
        self.assertEqual(
            invalid.exception.reason_code,
            "evidence_author_t0_capture_result_invalid",
        )

        reservation_execute = mock.Mock(
            side_effect=AssertionError("invalid E-8 must gate E-9 execution")
        )
        with (
            mock.patch.object(capture, "REPO_ROOT", repository),
            mock.patch.object(
                capture,
                "_current_boot_session_id",
                return_value=TEST_BOOT_SESSION_ID,
            ),
            self.assertRaises(capture.CaptureT0Error) as sequence,
        ):
            capture._capture_step_for_test(
                "ledger-reservation",
                pack,
                custody,
                custody / "window-plan",
                execute=reservation_execute,
            )
        self.assertEqual(
            sequence.exception.reason_code,
            "evidence_author_t0_capture_sequence_invalid",
        )
        reservation_execute.assert_not_called()
        self.assertFalse(
            (input_root / capture.STEP_FILENAMES["ledger-readiness"]).exists()
        )

    def test_sequence_refuses_malformed_predecessor_capture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / capture.STEP_FILENAMES["clock-prior-state"]).write_text(
                "invalid", encoding="utf-8"
            )
            with self.assertRaises(capture.CaptureT0Error) as caught:
                capture._require_sequence(
                    SimpleNamespace(input_root=root), "clock-disable"
                )
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_t0_capture_sequence_invalid",
        )

    def test_clock_prior_state_is_interactive_and_never_executes_privileged_get(
        self,
    ) -> None:
        (
            _temporary,
            repository,
            pack,
            custody,
            _context,
            input_root,
            _receipt,
        ) = self._producer_fixture()

        def prompt(message: str) -> str:
            if "trusted-clock" in message:
                return "2026-08-13T20:30:01Z"
            if "prior network-time" in message:
                return "Network Time: On"
            raise AssertionError(message)

        execute = mock.Mock(side_effect=AssertionError("must not execute E-4 get"))
        with (
            mock.patch.object(capture, "REPO_ROOT", repository),
            mock.patch.object(
                capture,
                "_current_boot_session_id",
                return_value=TEST_BOOT_SESSION_ID,
            ),
        ):
            result = capture._capture_step_for_test(
                "clock-prior-state",
                pack,
                custody,
                custody / "window-plan",
                prompt=prompt,
                execute=execute,
                monotonic_ns=lambda: SYNTHETIC_MONOTONIC_NS,
                utc_now=lambda: SYNTHETIC_UTC_NOW,
            )
        execute.assert_not_called()
        self.assertEqual(result["status"], "PASS")
        prior = json.loads(
            (input_root / "clock-prior-state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            prior["argv"],
            ["operator-interactive", "network-time-prior-state"],
        )
        self.assertEqual(prior["stdout"], "Network Time: On\n")

    def test_capture_paths_contain_no_privileged_network_time_get(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for relative in (
            "scripts/capture_t0_step.py",
            "scripts/prewindow_check.sh",
            "joulewise/arm_readiness_evidence_t0.py",
        ):
            with self.subTest(path=relative):
                source = (root / relative).read_text(encoding="utf-8")
                self.assertNotIn("-getusingnetworktime", source)

    def test_execute_uses_governed_environment_allowlist(self) -> None:
        completed = subprocess.CompletedProcess((), 0, b"", b"")
        with (
            mock.patch.dict(
                os.environ,
                {
                    "CPU_LIMIT": "999",
                    "LOAD_LIMIT": "999",
                    "PYTHONPATH": "/operator/injected",
                },
            ),
            mock.patch.object(
                capture.subprocess, "run", return_value=completed
            ) as run,
        ):
            self.assertIs(capture._execute(("/usr/bin/true",), cwd=Path(".")), completed)
        environment = run.call_args.kwargs["env"]
        self.assertEqual(
            environment,
            {
                "LANG": "C",
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
            },
        )

    def test_inherited_high_cpu_limit_does_not_make_loaded_sample_ready(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            fake_bin = Path(directory)
            commands = {
                "ps": "printf '%s\\n' 'edr 123 50.0 0.0 0 0 ?? R 0:00 0:00 /usr/libexec/XProtectRemediator'\n",
                "uptime": "printf '%s\\n' '12:00  up 1 day, load averages: 0.10 0.20 0.30'\n",
                "pmset": "printf \"%s\\n\" \"Now drawing from 'AC Power'\"\n",
                "df": "printf '%s\\n' 'Filesystem blocks Used Available Capacity Mounted' '/dev/disk 1 1 100 1% /'\n",
            }
            for name, body in commands.items():
                path = fake_bin / name
                path.write_text(f"#!/bin/sh\n{body}", encoding="utf-8")
                path.chmod(0o755)
            environment = {
                **os.environ,
                "CPU_LIMIT": "999",
                "LOAD_LIMIT": "999",
                "PATH": f"{fake_bin}:/usr/bin:/bin:/usr/sbin:/sbin",
            }
            completed = subprocess.run(
                ["/bin/bash", "scripts/prewindow_check.sh"],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        self.assertIn("background daemon active", completed.stdout)
        self.assertNotIn("999", completed.stdout)
        self.assertIn("NOT READY.", completed.stdout)

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
            capture._capture_step_for_test(
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

    def test_public_capture_surface_has_no_dependency_injection(self) -> None:
        self.assertEqual(
            tuple(inspect.signature(capture.capture_step).parameters),
            ("step_id", "pack_root", "custody_root", "window_plan_root"),
        )
        parser_destinations = {
            action.dest for action in capture._parser()._actions
        }
        for name in ("prompt", "execute", "monotonic_ns", "utc_now"):
            with self.subTest(name=name):
                self.assertNotIn(name, parser_destinations)
                with self.assertRaises(TypeError):
                    capture.capture_step(
                        "unused",
                        Path("unused"),
                        Path("unused"),
                        Path("unused"),
                        **{name: object()},
                    )

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

    def test_prewindow_runs_prefixes_name_the_successor_family(self) -> None:
        """D-138: the operator gate must name the governed generation.

        The runs-root prefix is ``runs_<pack_id>``.  It cannot be derived from
        ``_PROFILE_BY_PACK`` — that map is immutable HISTORY (generation 1) —
        so the prefixes are pinned against the three D-139-approved successor
        name shapes instead: each window must name a later-generation pack ID
        of its own profile, which is exactly what a registry install can admit.
        """

        source = (
            Path(__file__).resolve().parents[1] / "scripts/prewindow_check.sh"
        ).read_text(encoding="utf-8")
        observed = dict(
            re.findall(
                r"^\s*(alpha|beta|gamma)\) WINDOW_RUNS_PREFIX=(\S+) ;;$",
                source,
                re.MULTILINE,
            )
        )
        self.assertEqual(set(observed), {"alpha", "beta", "gamma"})
        for window, prefix in sorted(observed.items()):
            with self.subTest(window=window):
                self.assertTrue(prefix.startswith("runs_"))
                pack_id = prefix.removeprefix("runs_")
                pattern = readiness._SUCCESSOR_PROFILE_PATTERNS[window.upper()]
                self.assertIsNotNone(pattern.fullmatch(pack_id))
                self.assertNotIn(pack_id, readiness._PROFILE_BY_PACK)

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
