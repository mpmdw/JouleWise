from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from joulewise import arm_readiness
from joulewise.analysis_engine import inputs as analysis_inputs
from joulewise import floor_extraction, whole_window
from tests import test_arm_readiness as arm_readiness_tests


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "launch_window_script", ROOT / "scripts/launch_window.py"
)
assert SPEC is not None and SPEC.loader is not None
launch_window = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launch_window)

GENERATE_SPEC = importlib.util.spec_from_file_location(
    "generate_arm_readiness_script", ROOT / "scripts/generate_arm_readiness.py"
)
assert GENERATE_SPEC is not None and GENERATE_SPEC.loader is not None
generate_arm_readiness = importlib.util.module_from_spec(GENERATE_SPEC)
GENERATE_SPEC.loader.exec_module(generate_arm_readiness)

AUTHOR_SPEC = importlib.util.spec_from_file_location(
    "author_arm_readiness_evidence_script",
    ROOT / "scripts/author_arm_readiness_evidence.py",
)
assert AUTHOR_SPEC is not None and AUTHOR_SPEC.loader is not None
author_arm_readiness_evidence = importlib.util.module_from_spec(AUTHOR_SPEC)
AUTHOR_SPEC.loader.exec_module(author_arm_readiness_evidence)


class LaunchWindowEntrypointTests(unittest.TestCase):
    def _args(self, root: Path) -> argparse.Namespace:
        return argparse.Namespace(
            pack_root=root / "pack",
            arm_receipt=root / "arm-0001.json",
            arm_readiness_custody_root=root / "custody",
            launch_manifest=root / "launch-manifest.json",
            lifecycle_event=None,
            expected_confirmation_digest=None,
        )

    def _launch_inputs(
        self, args: argparse.Namespace, argv: list[str]
    ) -> dict[str, object]:
        return {
            "pack_root": args.pack_root,
            "arm_receipt": args.arm_receipt,
            "authenticated_arm_receipt": {"schema_version": "test"},
            "arm_receipt_sha256": "a" * 64,
            "window_custody_root": args.arm_readiness_custody_root,
            "launch_manifest": args.launch_manifest,
            "authenticated_launch_manifest": {"launch_command": argv},
            "launch_manifest_sha256": "b" * 64,
            "window_plan_root": Path(argv[-1]),
            "window_environment_sha256": "c" * 64,
            "window_chain_sha256": "d" * 64,
            "exec_argv": argv,
        }

    def test_eight_launchers_make_one_claim_and_one_execve(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self._args(Path(temporary))
            argv = [
                "/usr/bin/caffeinate",
                "-is",
                "/bin/zsh",
                "/tmp/window-chain.zsh",
                "/tmp/window-plan",
            ]
            barrier = threading.Barrier(8)
            lock = threading.Lock()
            claimed = False
            outcomes: list[str] = []

            def consume(*_args: object, **_kwargs: object) -> dict[str, str]:
                nonlocal claimed
                barrier.wait()
                with lock:
                    if claimed:
                        raise arm_readiness.ArmReadinessError(
                            "readiness_record_consumed", "already consumed"
                        )
                    claimed = True
                return {"consumption_path": "/tmp/consumed.json"}

            def run() -> None:
                try:
                    launch_window.launch(args)
                except arm_readiness.ArmReadinessError as exc:
                    outcome = exc.reason_code
                except arm_readiness.LaunchLineageError:
                    # A mocked execve returns; production execve cannot.
                    outcome = "execve_returned_under_mock"
                with lock:
                    outcomes.append(outcome)

            with mock.patch.object(
                launch_window,
                "_assemble_launch_inputs",
                return_value=self._launch_inputs(args, argv),
            ), mock.patch.object(
                launch_window, "_install_handoff"
            ), mock.patch.object(
                launch_window, "_consume_launch_capability", side_effect=consume
            ), mock.patch.object(
                launch_window,
                "verify_consumed_launch",
                return_value={"exec_argv": argv},
            ), mock.patch.object(launch_window.os, "execve") as execve:
                threads = [threading.Thread(target=run) for _ in range(8)]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(timeout=10)
            self.assertEqual(execve.call_count, 1)
            self.assertEqual(outcomes.count("readiness_record_consumed"), 7)
            self.assertEqual(outcomes.count("execve_returned_under_mock"), 1)

    def test_anonymous_fd_handoff_is_one_use(self) -> None:
        token = b"f" * launch_window.HANDOFF_TOKEN_BYTES
        launch_window._install_handoff(token)
        self.assertEqual(launch_window._read_one_use_handoff(), token)
        with self.assertRaises(arm_readiness.LaunchLineageError) as replay:
            launch_window._read_one_use_handoff()
        self.assertEqual(replay.exception.reason_code, "launch_handoff_invalid")

    def test_direct_chain_entry_without_inherited_fd_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self._args(Path(temporary))
            args.lifecycle_event = "start"
            args.expected_confirmation_digest = "e" * 64
            try:
                os.close(launch_window.HANDOFF_FD)
            except OSError:
                pass
            with mock.patch.object(
                launch_window, "_consumption_path", return_value=Path("/tmp/c.json")
            ), mock.patch.object(
                launch_window, "verify_consumed_launch", return_value={"status": "PASS"}
            ) as verify:
                with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
                    launch_window.lifecycle(args)
            self.assertEqual(caught.exception.reason_code, "launch_handoff_invalid")
            self.assertEqual(
                verify.call_args.kwargs["expected_confirmation_digest"],
                args.expected_confirmation_digest,
            )

    def test_execve_failure_is_one_burned_attempt_without_retry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self._args(Path(temporary))
            argv = [
                "/usr/bin/caffeinate",
                "-is",
                "/bin/zsh",
                "/tmp/window-chain.zsh",
                "/tmp/window-plan",
            ]
            with mock.patch.object(
                launch_window,
                "_assemble_launch_inputs",
                return_value=self._launch_inputs(args, argv),
            ), mock.patch.object(
                launch_window, "_install_handoff"
            ), mock.patch.object(
                launch_window,
                "_consume_launch_capability",
                return_value={"consumption_path": "/tmp/consumed.json"},
            ) as consume, mock.patch.object(
                launch_window,
                "verify_consumed_launch",
                return_value={"exec_argv": argv},
            ) as verify, mock.patch.object(
                launch_window.os,
                "execve",
                side_effect=OSError("injected exec failure"),
            ) as execve:
                with self.assertRaises(OSError):
                    launch_window.launch(args)
            consume.assert_called_once()
            verify.assert_called_once()
            execve.assert_called_once()

    def test_reviewed_launcher_enters_private_consumption_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self._args(Path(temporary))
            argv = [
                "/usr/bin/caffeinate",
                "-is",
                "/bin/zsh",
                "/tmp/window-chain.zsh",
                "/tmp/window-plan",
            ]
            with mock.patch.object(
                launch_window,
                "_assemble_launch_inputs",
                return_value=self._launch_inputs(args, argv),
            ), mock.patch.object(
                launch_window, "_install_handoff"
            ), mock.patch.object(
                launch_window,
                "_consume_launch_capability",
                return_value={"consumption_path": "/tmp/consumed.json"},
            ) as private_consume, mock.patch.object(
                launch_window,
                "verify_consumed_launch",
                return_value={"exec_argv": argv},
            ), mock.patch.object(launch_window.os, "execve"):
                with self.assertRaises(arm_readiness.LaunchLineageError):
                    launch_window.launch(args)
            private_consume.assert_called_once()
            self.assertEqual(
                set(private_consume.call_args.kwargs),
                {
                    "pack_root",
                    "arm_receipt",
                    "authenticated_arm_receipt",
                    "arm_receipt_sha256",
                    "window_custody_root",
                    "launch_manifest",
                    "authenticated_launch_manifest",
                    "launch_manifest_sha256",
                    "window_plan_root",
                    "window_environment_sha256",
                    "window_chain_sha256",
                    "exec_argv",
                    "handoff_token_sha256",
                    "expected_confirmation_digest",
                },
            )

    def test_launch_assembles_and_passes_reauthenticated_file_context(self) -> None:
        fixture = arm_readiness_tests.LaunchConsumptionV2Tests(
            methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
        )
        fixture.setUp()
        try:
            args = argparse.Namespace(
                pack_root=fixture.pack,
                arm_receipt=fixture.arm_path,
                arm_readiness_custody_root=fixture.custody,
                launch_manifest=fixture.manifest_path,
                lifecycle_event=None,
                expected_confirmation_digest="e" * 64,
            )
            arm_raw = fixture.arm_path.read_bytes()
            verified_arm = {
                "status": "PASS",
                "arm_disposition": "GO",
                "receipt_path": str(fixture.arm_path.resolve()),
                "receipt_sha256": arm_readiness.sha256_bytes(arm_raw),
                "pack_sha256": fixture.arm["pack"]["pack_sha256"],
            }
            with mock.patch.object(
                launch_window,
                "_verify_arm_receipt",
                return_value=verified_arm,
            ) as verify_arm, mock.patch.object(
                launch_window, "_install_handoff"
            ), mock.patch.object(
                launch_window,
                "_consume_launch_capability",
                return_value={"consumption_path": "/tmp/consumed.json"},
            ) as consume, mock.patch.object(
                launch_window,
                "verify_consumed_launch",
                return_value={"exec_argv": fixture.exec_argv},
            ), mock.patch.object(launch_window.os, "execve"):
                with self.assertRaises(arm_readiness.LaunchLineageError):
                    launch_window.launch(args)
            context = consume.call_args.kwargs
            self.assertEqual(
                context["authenticated_arm_receipt"], fixture.arm
            )
            self.assertEqual(
                context["authenticated_launch_manifest"]["launch_command"],
                fixture.exec_argv,
            )
            self.assertEqual(
                context["window_environment_sha256"],
                arm_readiness.sha256_bytes(
                    (fixture.window_root / "window.env").read_bytes()
                ),
            )
            self.assertEqual(
                context["window_chain_sha256"],
                arm_readiness.sha256_bytes(fixture.chain_path.read_bytes()),
            )
            self.assertEqual(
                verify_arm.call_args.kwargs["expected_confirmation_digest"],
                args.expected_confirmation_digest,
            )
        finally:
            fixture.doCleanups()

    def test_honest_launcher_consumes_verifies_and_reaches_execve(self) -> None:
        fixture = arm_readiness_tests.LaunchConsumptionV2Tests(
            methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
        )
        fixture.setUp()
        try:
            args = argparse.Namespace(
                pack_root=fixture.pack,
                arm_receipt=fixture.arm_path,
                arm_readiness_custody_root=fixture.custody,
                launch_manifest=fixture.manifest_path,
                lifecycle_event=None,
                expected_confirmation_digest=None,
            )
            arm_digest = hashlib.sha256(
                fixture.arm_path.read_bytes()
            ).hexdigest()
            verified_arm = {
                "status": "PASS",
                "arm_disposition": "GO",
                "receipt_path": str(fixture.arm_path.resolve()),
                "receipt_sha256": arm_digest,
                "pack_sha256": fixture.arm["pack"]["pack_sha256"],
            }
            with mock.patch.object(
                launch_window, "_verify_arm_receipt", return_value=verified_arm
            ), mock.patch.object(
                arm_readiness, "_verify_arm_receipt", return_value=verified_arm
            ), mock.patch.object(
                arm_readiness,
                "reviewed_main",
                return_value=fixture.arm["reviewed_main"],
            ), mock.patch.object(
                arm_readiness, "_root_policy_refusals", return_value=([], set())
            ), mock.patch.object(
                arm_readiness, "_pack_record", return_value=fixture.arm["pack"]
            ), mock.patch.object(
                arm_readiness,
                "_derive_arm_semantics_for_verification",
                return_value=(fixture.arm["rows"], fixture.arm["refusals"]),
            ), mock.patch.object(
                arm_readiness,
                "_current_boot_session_id",
                return_value=fixture.arm["boot_session_id"],
            ), mock.patch.object(
                launch_window, "_install_handoff"
            ), mock.patch.object(
                launch_window.os, "execve"
            ) as execve:
                with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
                    launch_window.launch(args)
            self.assertEqual(
                caught.exception.reason_code, "launch_consumption_invalid"
            )
            execve.assert_called_once_with(
                fixture.exec_argv[0],
                fixture.exec_argv,
                mock.ANY,
            )
            consumption_path = (
                fixture.custody
                / fixture.pack.name
                / "arm_readiness.consumptions"
                / "arm-0001.consumed.json"
            )
            self.assertTrue(consumption_path.is_file())
        finally:
            fixture.doCleanups()

    def test_standalone_consume_cli_is_retired_with_launcher_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack = root / "pack"
            pack.mkdir()
            (pack / "sentinel.txt").write_text("immutable\n")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/generate_arm_readiness.py"),
                    "consume",
                    "--pack-root",
                    str(pack),
                    "--arm-receipt",
                    str(root / "arm.json"),
                    "--window-custody-root",
                    str(root / "custody"),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 2)
        refusal = json.loads(completed.stdout)
        self.assertEqual(refusal["reason_codes"], ["readiness_usage_invalid"])
        self.assertIn("scripts/launch_window.py", refusal["detail"])


class OperatorConfirmationDigestCliTests(unittest.TestCase):
    DIGEST = "Operator-Custody-Digest-Passed-Unchanged"

    @staticmethod
    def _captured_stdout(module: object) -> tuple[io.BytesIO, object]:
        sink = io.BytesIO()
        stream = mock.Mock(buffer=sink)
        return sink, mock.patch.object(module.sys, "stdout", stream)

    def test_generate_cli_threads_digest_to_freeze_arm_and_verify(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack = root / "pack"
            pack.mkdir()
            (pack / "sentinel.txt").write_text("immutable\n")
            common_result = {"status": "PASS"}
            commands = (
                (
                    [
                        "freeze",
                        "--pack-root",
                        str(pack),
                        "--expected-confirmation-digest",
                        self.DIGEST,
                    ],
                    "generate_freeze_receipt",
                ),
                (
                    [
                        "arm",
                        "--pack-root",
                        str(pack),
                        "--arm-context",
                        "{}",
                        "--window-custody-root",
                        str(root / "custody"),
                        "--expected-confirmation-digest",
                        self.DIGEST,
                    ],
                    "generate_arm_receipt",
                ),
                (
                    [
                        "verify",
                        "--pack-root",
                        str(pack),
                        "--arm-receipt",
                        str(root / "arm.json"),
                        "--expected-confirmation-digest",
                        self.DIGEST,
                    ],
                    "verify_arm_receipt",
                ),
            )
            for argv, consumer_name in commands:
                with self.subTest(command=argv[0]), mock.patch.object(
                    generate_arm_readiness,
                    consumer_name,
                    return_value=common_result,
                ) as consumer:
                    sink, stdout_patch = self._captured_stdout(
                        generate_arm_readiness
                    )
                    with stdout_patch:
                        code = generate_arm_readiness.main(argv)
                    self.assertEqual(code, 0)
                    self.assertEqual(json.loads(sink.getvalue()), common_result)
                    self.assertEqual(
                        consumer.call_args.kwargs["expected_confirmation_digest"],
                        self.DIGEST,
                    )

    def test_evidence_author_cli_keeps_the_ruled_pack_root_only_surface(self) -> None:
        # Delta re-audit S1D-1: the digest is a CONSUMPTION-side attestation;
        # the authoring CLI carried an inert digest flag (no table path, no
        # effect) and it was removed to restore the ruled --pack-root-only
        # surface. This test pins the removal: the flag refuses, and a plain
        # authoring invocation passes no confirmation kwargs at all.
        pack = ROOT / "tests"
        with self.assertRaises(SystemExit) as caught:
            author_arm_readiness_evidence.main(
                [
                    "--pack-root",
                    str(pack),
                    "--expected-confirmation-digest",
                    self.DIGEST,
                ]
            )
        self.assertEqual(caught.exception.code, 2)
        with mock.patch.object(
            author_arm_readiness_evidence.readiness,
            "_repo_for_pack",
            return_value=ROOT,
        ), mock.patch.object(
            author_arm_readiness_evidence,
            "author_arm_readiness_evidence",
            return_value={"status": "PASS"},
        ) as consumer:
            sink, stdout_patch = self._captured_stdout(
                author_arm_readiness_evidence
            )
            with stdout_patch:
                code = author_arm_readiness_evidence.main(
                    ["--pack-root", str(pack)]
                )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(sink.getvalue())["status"], "PASS")
        self.assertEqual(consumer.call_args.args, (ROOT / "tests",))
        self.assertEqual(consumer.call_args.kwargs, {})

    def test_launch_cli_refuses_unconfirmed_table_and_accepts_operator_digest(
        self,
    ) -> None:
        from tests.test_family_marker import confirmation

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "repository"
            repository.mkdir()
            subprocess.run(
                ("git", "-C", str(repository), "init", "-q"), check=True
            )
            subprocess.run(
                (
                    "git",
                    "-C",
                    str(repository),
                    "config",
                    "user.email",
                    "test@example.invalid",
                ),
                check=True,
            )
            subprocess.run(
                (
                    "git",
                    "-C",
                    str(repository),
                    "config",
                    "user.name",
                    "Launch CLI Digest Test",
                ),
                check=True,
            )
            self.assertEqual(
                len(arm_readiness.R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS), 1
            )
            successor_relative = next(
                iter(arm_readiness.R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS)
            )
            successor_path = repository / successor_relative
            successor_path.parent.mkdir(parents=True)
            successor_raw = b'{"schema_version":"test-successor-pinset"}\n'
            successor_path.write_bytes(successor_raw)
            subprocess.run(
                ("git", "-C", str(repository), "add", "."), check=True
            )
            subprocess.run(
                ("git", "-C", str(repository), "commit", "-qm", "pinset"),
                check=True,
            )
            head = subprocess.run(
                ("git", "-C", str(repository), "rev-parse", "HEAD"),
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            custody = root / "custody"
            publication = custody / "family_publication"
            publication.mkdir(parents=True)
            table_path = publication / arm_readiness.STEP6_CONFIRMATION_TABLE_NAME
            table = confirmation()
            table["successor_pinset"]["sha256"] = hashlib.sha256(
                successor_raw
            ).hexdigest()
            table_raw = arm_readiness.render_json(table)
            table_path.write_bytes(table_raw)
            table_path.with_name(f"{table_path.name}.sha256").write_bytes(
                arm_readiness.gnu_sidecar(
                    hashlib.sha256(table_raw).hexdigest(), table_path.name
                )
            )
            self.assertEqual(table["confirmation"]["authority"], "ED")
            self.assertEqual(table["confirmation"]["decision"], "YES")

            lifecycle_registry = json.loads(
                (ROOT / arm_readiness.ROW_REGISTRY_RELATIVE_PATH).read_text()
            )["freeze_evidence_lifecycle"]
            changed_set_code = next(
                item["code"]
                for item in lifecycle_registry["refusal_vocabulary"]
                if item["role"] == "DEPENDENCY_CHANGED_SET"
            )
            table_digest = hashlib.sha256(table_raw).hexdigest()
            args = self._launch_argv(root, custody)
            launch_args = launch_window._parser().parse_args(args)
            exec_argv = [
                "/usr/bin/caffeinate",
                "-is",
                "/bin/zsh",
                "/tmp/window-chain.zsh",
                "/tmp/window-plan",
            ]
            launch_inputs = LaunchWindowEntrypointTests()._launch_inputs(
                launch_args, exec_argv
            )
            subtracted = False

            def assemble(parsed: argparse.Namespace) -> dict[str, object]:
                nonlocal subtracted
                try:
                    arm_readiness._require_confirmed_conditional_path(
                        repository,
                        head,
                        successor_relative,
                        lifecycle_registry,
                        Path(parsed.arm_readiness_custody_root)
                        / "family_publication"
                        / arm_readiness.STEP6_CONFIRMATION_TABLE_NAME,
                        expected_confirmation_digest=(
                            parsed.expected_confirmation_digest
                        ),
                        evidence_id="freeze-doctrine-pin-v1",
                    )
                except arm_readiness.EvidenceLifecycleError as exc:
                    raise arm_readiness.ArmReadinessError(
                        exc.reason_code, str(exc)
                    ) from exc
                subtracted = True
                return launch_inputs

            for label, supplied in (
                ("digest absent", None),
                ("digest wrong", "0" * 64),
            ):
                with self.subTest(case=label):
                    subtracted = False
                    argv = list(args)
                    if supplied is not None:
                        argv.extend(
                            ["--expected-confirmation-digest", supplied]
                        )
                    sink, stdout_patch = self._captured_stdout(launch_window)
                    with stdout_patch, mock.patch.object(
                        launch_window,
                        "_assemble_launch_inputs",
                        side_effect=assemble,
                    ), mock.patch.object(
                        launch_window, "_consume_launch_capability"
                    ) as consume, mock.patch.object(
                        launch_window.os, "execve"
                    ) as execve:
                        code = launch_window.main(argv)
                    self.assertEqual(code, 2)
                    self.assertEqual(
                        json.loads(sink.getvalue())["reason_codes"],
                        [changed_set_code],
                    )
                    self.assertFalse(subtracted)
                    consume.assert_not_called()
                    execve.assert_not_called()

            subtracted = False
            correct_argv = args + [
                "--expected-confirmation-digest",
                table_digest,
            ]
            with mock.patch.object(
                launch_window,
                "_assemble_launch_inputs",
                side_effect=assemble,
            ), mock.patch.object(
                launch_window, "_install_handoff"
            ), mock.patch.object(
                launch_window,
                "_consume_launch_capability",
                return_value={"consumption_path": "/tmp/consumed.json"},
            ) as consume, mock.patch.object(
                launch_window,
                "verify_consumed_launch",
                return_value={"exec_argv": exec_argv},
            ) as verify, mock.patch.object(
                launch_window.os, "execve", side_effect=SystemExit(0)
            ) as execve:
                with self.assertRaises(SystemExit) as exited:
                    launch_window.main(correct_argv)
            self.assertEqual(exited.exception.code, 0)
            self.assertTrue(subtracted)
            consume.assert_called_once()
            verify.assert_called_once()
            execve.assert_called_once()
            self.assertEqual(
                consume.call_args.kwargs["expected_confirmation_digest"],
                table_digest,
            )
            self.assertEqual(
                verify.call_args.kwargs["expected_confirmation_digest"],
                table_digest,
            )

    @staticmethod
    def _launch_argv(root: Path, custody: Path) -> list[str]:
        return [
            "--pack-root",
            str(root / "pack"),
            "--arm-receipt",
            str(root / "arm.json"),
            "--arm-readiness-custody-root",
            str(custody),
            "--launch-manifest",
            str(root / "launch-manifest.json"),
        ]


class CeremonySkipConsumerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.runs_root = Path(self.temporary.name) / "runs"
        self.bundle = self.runs_root / "ceremony-skipped"
        self.bundle.mkdir(parents=True)
        self.config = {
            "run_id": self.bundle.name,
            "run_metadata": {
                "project": "joulewise",
                "tags": ["production-window", "launch_lineage_required"],
            },
        }
        (self.bundle / "config.json").write_text(
            json.dumps(self.config, sort_keys=True, separators=(",", ":")) + "\n"
        )
        (self.bundle / "metadata.json").write_text(
            '{"extra":{}}\n'
        )
        (self.bundle / "summary_metrics.json").write_text(
            '{"status":"succeeded"}\n'
        )

    def test_analysis_input_refuses_missing_launch_consumption(self) -> None:
        with self.assertRaises(analysis_inputs.AnalysisInputError) as caught:
            analysis_inputs._read_bundle(
                {"entry_id": "e1"},
                self.bundle,
                self.runs_root,
                self.config,
                lambda _path, _strict: [],
            )
        self.assertIn("launch_consumption_missing", str(caught.exception))

    def test_whole_window_refuses_missing_launch_consumption(self) -> None:
        reasons = whole_window.launch_lineage_refusal_reasons(
            self.runs_root,
            {self.bundle.name},
            require_completion=True,
        )
        self.assertEqual(reasons, ("launch_consumption_missing",))

    def test_floor_extraction_refuses_missing_launch_consumption(self) -> None:
        report = floor_extraction._evaluate_member(
            slot="r1",
            bundle_id=self.bundle.name,
            block_id=None,
            position=None,
            runs_root=self.runs_root,
            metric="energy_request_j",
            window_class="request",
            cooldowns={},
            hash_bundles=False,
            strict_validator=lambda _path, _strict: [],
        )
        self.assertIn("launch_consumption_missing", report.reasons)

    def test_malformed_and_mismatched_lineage_codes_reach_every_consumer(self) -> None:
        for code in ("launch_consumption_invalid", "launch_binding_mismatch"):
            error = arm_readiness.LaunchLineageError(code, "injected lineage defect")
            with self.subTest(code=code, consumer="analysis"), mock.patch.object(
                analysis_inputs,
                "authenticate_bundle_launch_lineage",
                side_effect=error,
            ):
                with self.assertRaises(analysis_inputs.AnalysisInputError) as caught:
                    analysis_inputs._read_bundle(
                        {"entry_id": "e1"},
                        self.bundle,
                        self.runs_root,
                        self.config,
                        lambda _path, _strict: [],
                    )
                self.assertIn(code, str(caught.exception))
            with self.subTest(code=code, consumer="whole-window"), mock.patch.object(
                whole_window,
                "authenticate_bundle_launch_lineage",
                side_effect=error,
            ):
                self.assertEqual(
                    whole_window.launch_lineage_refusal_reasons(
                        self.runs_root,
                        {self.bundle.name},
                        require_completion=True,
                    ),
                    (code,),
                )
            with self.subTest(code=code, consumer="floor-extraction"), mock.patch.object(
                floor_extraction,
                "authenticate_bundle_launch_lineage",
                side_effect=error,
            ):
                report = floor_extraction._evaluate_member(
                    slot="r1",
                    bundle_id=self.bundle.name,
                    block_id=None,
                    position=None,
                    runs_root=self.runs_root,
                    metric="energy_request_j",
                    window_class="request",
                    cooldowns={},
                    hash_bundles=False,
                    strict_validator=lambda _path, _strict: [],
                )
                self.assertIn(code, report.reasons)

    def test_mixed_valid_consumptions_refuse_at_aggregate_boundary(self) -> None:
        second = self.runs_root / "ceremony-skipped-2"
        second.mkdir()
        (second / "config.json").write_text(
            json.dumps(
                {**self.config, "run_id": second.name},
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )
        (second / "metadata.json").write_text('{"extra":{}}\n')
        (second / "summary_metrics.json").write_text(
            '{"status":"succeeded"}\n'
        )

        def lineage(path: Path, **_kwargs: object) -> dict[str, str]:
            suffix = "1" if path.name == self.bundle.name else "2"
            return {
                "consumption_sha256": suffix * 64,
                "pack_sha256": "a" * 64,
                "boot_session_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            }

        with mock.patch.object(
            whole_window,
            "authenticate_bundle_launch_lineage",
            side_effect=lineage,
        ):
            reasons = whole_window.launch_lineage_refusal_reasons(
                self.runs_root,
                {self.bundle.name, second.name},
                require_completion=True,
            )
        self.assertEqual(reasons, ("launch_lineage_conflict",))


if __name__ == "__main__":
    unittest.main()
