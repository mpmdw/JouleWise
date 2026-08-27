from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
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
            step6_confirmation_table=None,
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
            args.step6_confirmation_table = Path("/tmp/operator-confirmation.json")
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
                verify.call_args.kwargs["step6_confirmation_table"],
                args.step6_confirmation_table,
            )
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
                    "step6_confirmation_table",
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
                step6_confirmation_table=fixture.custody
                / "operator-confirmation.json",
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
                verify_arm.call_args.kwargs["step6_confirmation_table"],
                args.step6_confirmation_table,
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
                step6_confirmation_table=None,
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


class ProductionArmRelocationLaunchTests(unittest.TestCase):
    def _mint_v4_arm(
        self,
    ) -> tuple[tempfile.TemporaryDirectory[str], Path, Path, Path, Path, Path]:
        from joulewise import arm_readiness_evidence as generic_evidence
        from tests.test_arm_readiness_evidence_author import make_author_fixture
        from tests.test_arm_readiness_evidence_t0 import (
            _install_synthetic_identity_inputs,
            _valid_session_receipt,
            author_arm_readiness_evidence_t0,
            author_environment,
            make_t0_fixture,
        )
        from tests.test_arm_readiness_integration import (
            PACKS,
            install_passing_dry_run,
        )
        from tests.test_arm_readiness_lifecycle import (
            git,
            predecessor_pack_root,
        )
        from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID

        family = {
            "ALPHA": "d117_floor_qwen25_1p5b_v4",
            "BETA": "d117_floor_qwen25_7b_v4",
            "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v4",
        }
        fixture_now = time.monotonic_ns()
        temporary, repository, pack, custody, context, input_root = (
            make_t0_fixture(
                now_monotonic_ns=fixture_now,
                synthetic_clock=False,
            )
        )
        template_temporary, template_repository, template_pack, _unused, _arm = (
            make_author_fixture(pack.name)
        )
        try:
            original_tree = json.loads((pack / "plan_tree.json").read_text())
            shutil.copytree(
                template_repository,
                repository,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(".git"),
            )
            tree = json.loads((template_pack / "plan_tree.json").read_text())
        finally:
            template_temporary.cleanup()

        tree["external_inputs"] = original_tree["external_inputs"]
        tree["stage_graph"] = [
            *original_tree["stage_graph"],
            *tree["stage_graph"],
        ]
        tree["arm_attachments"]["arm_readiness"]["freeze_receipt"] = None
        # The sandbox denies the production kern.bootsessionuuid sysctl.  The
        # open v4 transaction also has no three-pack publication marker yet,
        # so a temporary one-pack arm cannot cross that independent gate.  The
        # copied module replaces those two prerequisites only; clocks, pack
        # authentication, arm derivation, consumption, and consumed-arm replay
        # all remain production paths.
        _install_synthetic_identity_inputs(
            repository,
            pack,
            tree,
            boot_session_override=TEST_BOOT_SESSION_ID,
            clock_override=None,
        )
        sitecustomize_path = repository / "sitecustomize.py"
        sitecustomize_path.write_text(
            sitecustomize_path.read_text()
            + "from joulewise import arm_readiness_evidence\n"
            + f"arm_readiness_evidence._PACKS_BY_PROFILE = {family!r}\n"
            + "arm_readiness._gate_family_publication = lambda *args, **kwargs: None\n"
        )
        producer_path = pack / "producer_contract.json"
        producer_raw = arm_readiness.render_json(
            {
                "schema_version": "synthetic-producer.v1",
                "identity_pin_projection": copy.deepcopy(
                    tree["arm_attachments"]["identity_pin_projection"]
                ),
            }
        )
        producer_path.write_bytes(producer_raw)
        tree["downstream_contract"]["producer_contract"]["sha256"] = (
            hashlib.sha256(producer_raw).hexdigest()
        )
        tree_raw = arm_readiness.render_json(tree)
        (pack / "plan_tree.json").write_bytes(tree_raw)
        (pack / "plan_tree.sha256").write_bytes(
            arm_readiness.gnu_sidecar(
                hashlib.sha256(tree_raw).hexdigest(),
                "plan_tree.json",
            )
        )
        for name in (
            generic_evidence._EVIDENCE_DIRECTORY,
            generic_evidence._SOURCE_DIRECTORY,
            "arm_readiness.freeze.receipts",
            "identity_pin_projection.receipts",
        ):
            shutil.rmtree(pack / name, ignore_errors=True)
        self.assertFalse((pack / "arm_readiness.freeze.receipts").exists())
        git(repository, "add", ".")
        git(repository, "commit", "-qm", "complete unprojected author pack")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")

        environment = {
            **os.environ,
            "PYTHONPATH": str(repository),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        projected = subprocess.run(
            [
                sys.executable,
                "scripts/project_identity_pins.py",
                "freeze",
                str(pack),
            ],
            cwd=repository,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            projected.returncode,
            0,
            f"{projected.stdout}{projected.stderr}",
        )
        projected_unit = json.loads((pack / "plan_tree.json").read_text())[
            "arm_attachments"
        ]["identity_pin_projection"]["identity_units"][0]
        beta_tree_path = (
            repository
            / "configs/campaigns"
            / PACKS["BETA"]
            / "plan_tree.json"
        )
        beta_unit = json.loads(beta_tree_path.read_text())["arm_attachments"][
            "identity_pin_projection"
        ]["identity_units"][0]
        gamma_tree_path = (
            repository
            / "configs/campaigns"
            / PACKS["GAMMA"]
            / "plan_tree.json"
        )
        gamma_tree = json.loads(gamma_tree_path.read_text())
        gamma_tree["arm_attachments"]["identity_pin_projection"][
            "identity_units"
        ] = [copy.deepcopy(projected_unit), copy.deepcopy(beta_unit)]
        gamma_tree_path.write_bytes(arm_readiness.render_json(gamma_tree))
        git(repository, "add", ".")
        git(repository, "commit", "-qm", "project identity")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        self.assertFalse((pack / "arm_readiness.freeze.receipts").exists())

        with (
            mock.patch.dict(generic_evidence._PACKS_BY_PROFILE, family),
            mock.patch.object(
                arm_readiness,
                "_current_boot_session_id",
                return_value=TEST_BOOT_SESSION_ID,
            ),
        ):
            authored = generic_evidence.author_arm_readiness_evidence(pack)
        self.assertEqual(authored["status"], "PASS", authored)
        pack_relative = pack.relative_to(repository).as_posix()
        git(
            repository,
            "add",
            "--",
            f"{pack_relative}/{generic_evidence._SOURCE_DIRECTORY}",
            f"{pack_relative}/{generic_evidence._EVIDENCE_DIRECTORY}",
        )
        git(repository, "commit", "-qm", "author freeze evidence")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        self.assertFalse((pack / "arm_readiness.freeze.receipts").exists())

        with (
            mock.patch.dict(generic_evidence._PACKS_BY_PROFILE, family),
            mock.patch.object(
                arm_readiness,
                "_current_boot_session_id",
                return_value=TEST_BOOT_SESSION_ID,
            ),
        ):
            frozen = arm_readiness.generate_freeze_receipt(
                pack,
                predecessor_pack_root=predecessor_pack_root(
                    repository,
                    pack.name,
                ),
            )
        if frozen["receipt_path"] is not None:
            frozen["refusals"] = json.loads(
                Path(frozen["receipt_path"]).read_text()
            )["refusals"]
        self.assertEqual(frozen["status"], "PASS", frozen)
        git(repository, "add", "--", pack_relative)
        git(repository, "commit", "-qm", "mint freeze")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")

        pack_sha256 = arm_readiness.committed_pack_tree_sha256(pack)
        tree_oid = subprocess.run(
            ["git", "rev-parse", "HEAD^{tree}"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        terminal_review = "\n".join(
            (
                "terminal review",
                "",
                "JouleWise-Terminal-Review: PASS",
                f"JouleWise-Terminal-Review-Tree-Oid: {tree_oid}",
                "JouleWise-Terminal-Review-Pack-Sha256: "
                f"{pack_sha256}",
            )
        )
        git(
            repository,
            "commit",
            "--allow-empty",
            "-qm",
            terminal_review,
        )
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        install_passing_dry_run(pack, custody)

        tree, _tree_raw = arm_readiness._plan_tree(pack)
        plan_sha256 = arm_readiness._pack_identity(pack, tree)["plan_sha256"]
        session = _valid_session_receipt(context, plan_sha256, tree)
        temporary_root = Path(temporary.name)
        (temporary_root / "identity-epoch.json").write_bytes(
            arm_readiness.render_json(
                session["slots"]["pre"]["identity_epoch"]
            )
        )
        (temporary_root / "t1-bindings.json").write_bytes(
            arm_readiness.render_json(
                session["slots"]["pre"]["t1_bindings"]
            )
        )
        (temporary_root / "production-ledger.jsonl").write_text(
            json.dumps(session, sort_keys=True, separators=(",", ":")) + "\n"
        )
        readiness_capture_path = input_root / "ledger-readiness.json"
        readiness_capture = json.loads(readiness_capture_path.read_text())
        readiness_capture["stdout"] = json.dumps(
            {
                "status": "ready",
                "early_warning_only": True,
                "frozen_plan": {
                    "path": str(pack / "calibration_plan.json"),
                    "plan_id": tree["plan"]["plan_id"],
                    "sha256": plan_sha256,
                },
            }
        )
        readiness_capture_path.write_bytes(
            arm_readiness.render_json(readiness_capture)
        )
        reservation_capture_path = input_root / "ledger-reservation.json"
        reservation_capture = json.loads(reservation_capture_path.read_text())
        plan_index = reservation_capture["argv"].index("--plan-sha256") + 1
        reservation_capture["argv"][plan_index] = plan_sha256
        reservation_capture["stdout"] = json.dumps(
            {"status": "reserved", "receipt": session}
        )
        reservation_capture_path.write_bytes(
            arm_readiness.render_json(reservation_capture)
        )
        with author_environment(
            repository,
            now_monotonic_ns=fixture_now,
        ):
            authored_t0 = author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(authored_t0["status"], "PASS", authored_t0)
        self.assertEqual(
            len(authored_t0["authored_rows"]),
            15,
            authored_t0,
        )

        armed = subprocess.run(
            [
                sys.executable,
                str(repository / "scripts/generate_arm_readiness.py"),
                "arm",
                "--pack-root",
                str(pack),
                "--arm-context",
                json.dumps(context, sort_keys=True, separators=(",", ":")),
                "--window-custody-root",
                str(custody),
            ],
            cwd=repository,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(armed.returncode, 0, f"{armed.stdout}{armed.stderr}")
        arm_result = json.loads(armed.stdout)
        self.assertEqual(arm_result["status"], "PASS", arm_result)
        arm_path = Path(arm_result["receipt_path"])
        manifest_path = input_root / "launch-manifest.json"
        return temporary, repository, pack, custody, arm_path, manifest_path

    def _clone_repository(self, source: Path, destination: Path) -> None:
        from tests.test_arm_readiness_lifecycle import git

        git(
            destination.parent,
            "clone",
            "-q",
            "--no-local",
            str(source),
            str(destination),
        )
        git(destination, "config", "user.email", "tests@joulewise.invalid")
        git(destination, "config", "user.name", "JouleWise tests")
        git(destination, "config", "gc.auto", "0")
        git(destination, "config", "maintenance.auto", "false")

    def _run_launch(
        self,
        repository: Path,
        pack: Path,
        arm_path: Path,
        custody: Path,
        manifest_path: Path,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(repository / "scripts/launch_window.py"),
                "--pack-root",
                str(pack),
                "--arm-receipt",
                str(arm_path),
                "--arm-readiness-custody-root",
                str(custody),
                "--launch-manifest",
                str(manifest_path),
            ],
            cwd=repository,
            env={
                **os.environ,
                "PYTHONPATH": str(repository),
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            check=False,
            capture_output=True,
            text=True,
        )

    def test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change(
        self,
    ) -> None:
        temporary, repository, pack, custody, arm_path, manifest_path = (
            self._mint_v4_arm()
        )
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        pack_relative = pack.relative_to(repository)

        content_repository = root / "content-different-repository"
        self._clone_repository(repository, content_repository)
        content_pack = content_repository / pack_relative
        content_path = content_pack / "config.json"
        content_path.write_bytes(b'{"run_id":"genuine-content-difference"}\n')
        subprocess.run(
            ["git", "add", pack_relative.as_posix()],
            cwd=content_repository,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-qm", "genuine pack content difference"],
            cwd=content_repository,
            check=True,
        )
        refused = self._run_launch(
            content_repository,
            content_pack,
            arm_path,
            custody,
            manifest_path,
        )
        self.assertEqual(refused.returncode, 2, refused.stderr)
        refusal = json.loads(refused.stdout)
        self.assertEqual(
            refusal["reason_codes"],
            ["readiness_pack_digest_mismatch"],
        )
        self.assertEqual(
            refusal["detail"],
            "arm receipt pack binding differs from committed pack bytes",
        )

        relocated_repository = root / "relocated-repository"
        self._clone_repository(repository, relocated_repository)
        relocated_pack = relocated_repository / pack_relative
        shutil.rmtree(pack)
        pack.symlink_to(relocated_pack, target_is_directory=True)
        accepted = self._run_launch(
            relocated_repository,
            relocated_pack,
            arm_path,
            custody,
            manifest_path,
        )
        self.assertEqual(
            accepted.returncode,
            0,
            f"{accepted.stdout}{accepted.stderr}",
        )
        self.assertEqual(accepted.stdout, "")
        consumption_path = (
            custody
            / relocated_pack.name
            / "arm_readiness.consumptions"
            / f"{arm_path.stem}.consumed.json"
        )
        self.assertTrue(consumption_path.is_file())
        consumption = arm_readiness.validate_consumption_receipt(
            arm_readiness.parse_json_bytes(
                consumption_path.read_bytes(),
                require_canonical=True,
            )
        )
        self.assertEqual(
            consumption["schema_version"],
            arm_readiness.CONSUMPTION_RECEIPT_SCHEMA,
        )


class OperatorConfirmationDigestCliTests(unittest.TestCase):
    DIGEST = "Operator-Custody-Digest-Passed-Unchanged"

    @staticmethod
    def _captured_stdout(module: object) -> tuple[io.BytesIO, object]:
        # A real text stream, not a Mock: Python 3.14's argparse probes
        # sys.stdout.fileno() for colorization at parser construction, and
        # os.isatty(Mock) is a TypeError. TextIOWrapper.fileno() raises
        # io.UnsupportedOperation, which _colorize handles by disabling
        # color — the supported non-tty path on every version we test.
        sink = io.BytesIO()
        stream = io.TextIOWrapper(sink, encoding="utf-8", write_through=True)
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
                        "--measurement-checkout",
                        str(root),
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
                    if argv[0] == "freeze":
                        self.assertEqual(
                            consumer.call_args.kwargs["measurement_checkout"],
                            root,
                        )

    def test_evidence_author_cli_keeps_digest_out_but_emits_checkout(self) -> None:
        # Delta re-audit S1D-1: the digest is a CONSUMPTION-side attestation;
        # the authoring CLI carried an inert digest flag (no table path, no
        # effect) and it was removed to restore the ruled --pack-root-only
        # surface. The checkout declaration is instead an operative mint gate.
        # This test pins both facts: the digest still refuses, while the
        # explicitly supplied checkout appears literally in the freeze command.
        pack = ROOT / "tests"
        with self.assertRaises(SystemExit) as caught:
            author_arm_readiness_evidence.main(
                [
                    "--pack-root",
                    str(pack),
                    "--measurement-checkout",
                    str(ROOT),
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
                    [
                        "--pack-root",
                        str(pack),
                        "--measurement-checkout",
                        str(ROOT),
                    ]
                )
        self.assertEqual(code, 0)
        result = json.loads(sink.getvalue())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(
            result["post_authoring"]["sequence"][3],
            "python3 scripts/generate_arm_readiness.py freeze "
            "--pack-root tests "
            f"--measurement-checkout {ROOT}",
        )
        self.assertEqual(consumer.call_args.args, (ROOT / "tests",))
        self.assertEqual(consumer.call_args.kwargs, {})

    def _confirmation_supply_fixture(
        self, *, table_at_default: bool
    ) -> argparse.Namespace:
        from tests.test_family_marker import confirmation

        launch_fixture = arm_readiness_tests.LaunchConsumptionV2Tests(
            methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
        )
        launch_fixture.setUp()
        self.addCleanup(launch_fixture.doCleanups)
        root = Path(launch_fixture.temporary.name)
        repository = root / "repository"
        repository.mkdir()
        subprocess.run(("git", "-C", str(repository), "init", "-q"), check=True)
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
        subprocess.run(("git", "-C", str(repository), "add", "."), check=True)
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

        default_table_path = (
            launch_fixture.custody
            / "family_publication"
            / arm_readiness.STEP6_CONFIRMATION_TABLE_NAME
        )
        table_path = (
            default_table_path
            if table_at_default
            else root
            / "operator-confirmations"
            / arm_readiness.STEP6_CONFIRMATION_TABLE_NAME
        )
        table_path.parent.mkdir(parents=True)
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
        arm_raw = launch_fixture.arm_path.read_bytes()
        return argparse.Namespace(
            repository=repository,
            head=head,
            successor_relative=successor_relative,
            lifecycle_registry=lifecycle_registry,
            changed_set_code=changed_set_code,
            table_path=table_path,
            default_table_path=default_table_path,
            table_digest=hashlib.sha256(table_raw).hexdigest(),
            launch_fixture=launch_fixture,
            verified_arm={
                "status": "PASS",
                "arm_disposition": "GO",
                "receipt_path": str(launch_fixture.arm_path.resolve()),
                "receipt_sha256": hashlib.sha256(arm_raw).hexdigest(),
                "pack_sha256": launch_fixture.arm["pack"]["pack_sha256"],
            },
            argv=[
                "--pack-root",
                str(launch_fixture.pack),
                "--arm-receipt",
                str(launch_fixture.arm_path),
                "--arm-readiness-custody-root",
                str(launch_fixture.custody),
                "--launch-manifest",
                str(launch_fixture.manifest_path),
            ],
            gate_discharged=False,
        )

    def _real_confirmation_reach_fixture(self) -> argparse.Namespace:
        """Build a committed pack whose real replay reaches the C-to-S gate."""

        from tests import test_arm_readiness_lifecycle as lifecycle_tests
        from tests.test_arm_readiness_evidence import content_source_and_receipt
        from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID, sample_arm
        from tests.test_family_marker import confirmation

        temporary, repository, pack, custody, arm_path = (
            lifecycle_tests.make_go_fixture(
                lifecycle_tests.HISTORICAL_PACK_NAME
            )
        )
        self.addCleanup(temporary.cleanup)

        # These two setup-only seams are the same ones the lifecycle fixture
        # uses to mint synthetic evidence. Both patches end before main() runs;
        # the launcher-to-authenticator receiving chain below remains real.
        with mock.patch.object(
            arm_readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID
        ), mock.patch.object(
            arm_readiness, "_gate_receipt_histsem", return_value=None
        ), mock.patch(
            "joulewise.arm_readiness_evidence._r1_rederive_at_arm",
            return_value=None,
        ):
            (repository / "dependency.txt").write_text("stable\n")
            lifecycle_tests.git(repository, "add", "dependency.txt")
            lifecycle_tests.git(
                repository, "commit", "-qm", "dependency baseline"
            )
            derivation = lifecycle_tests.git_text(
                repository, "rev-parse", "HEAD"
            ).strip()
            source, receipt = content_source_and_receipt(
                repository, derivation
            )
            registry = json.loads(
                (
                    repository / arm_readiness.ROW_REGISTRY_RELATIVE_PATH
                ).read_bytes()
            )
            policy = next(
                item
                for item in registry["freeze_evidence_lifecycle"][
                    "evidence_policies"
                ]
                if item["kind"] == "DOCTRINE_PIN"
            )
            source["freshness_policy_id"] = policy["freshness_policy_id"]
            receipt["freshness_policy_id"] = policy["freshness_policy_id"]
            source_raw = arm_readiness.render_json(source)
            source_digest = hashlib.sha256(source_raw).hexdigest()
            receipt["dependency_manifest_sha256"] = source_digest
            receipt["facts"][0]["source_sha256"] = source_digest

            source_path = pack / "arm_readiness.sources/doctrine-pin.json"
            source_path.parent.mkdir()
            source_path.write_bytes(source_raw)
            receipt_path = (
                pack / "arm_readiness.evidence/evidence-doctrine-pin.json"
            )
            receipt_path.parent.mkdir()
            receipt_raw = arm_readiness.render_json(receipt)
            receipt_path.write_bytes(receipt_raw)
            receipt_path.with_name(f"{receipt_path.name}.sha256").write_bytes(
                arm_readiness.gnu_sidecar(
                    hashlib.sha256(receipt_raw).hexdigest(), receipt_path.name
                )
            )
            lifecycle_tests.git(repository, "add", ".")
            lifecycle_tests.git(
                repository, "commit", "-qm", "install synthetic R1 evidence"
            )
            minted = arm_readiness.generate_freeze_receipt(pack)
            self.assertTrue(minted["mutated"])
            lifecycle_tests.git(repository, "add", ".")
            lifecycle_tests.git(
                repository, "commit", "-qm", "mint freeze receipt"
            )

        successor_relative = arm_readiness.RECEIPT_HISTSEM_PINSET_RELATIVE_PATH[1]
        successor_path = repository / successor_relative
        successor_path.parent.mkdir(parents=True, exist_ok=True)
        successor_raw = b'{"packs": []}\n'
        successor_path.write_bytes(successor_raw)
        lifecycle_tests.git(repository, "add", successor_relative.as_posix())
        lifecycle_tests.git(
            repository, "commit", "-qm", "mint successor pinset"
        )
        lifecycle_tests.git(
            repository, "update-ref", "refs/remotes/origin/main", "HEAD"
        )

        table_path = (
            Path(temporary.name)
            / "operator-confirmations"
            / arm_readiness.STEP6_CONFIRMATION_TABLE_NAME
        )
        table_path.parent.mkdir()
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

        arm = sample_arm(Path(temporary.name) / "context")
        arm["pack"] = arm_readiness._pack_record(pack)
        arm["reviewed_main"] = arm_readiness.reviewed_main(pack)
        tree, _tree_raw = arm_readiness._plan_tree(pack)
        attachment = tree["arm_attachments"]["arm_readiness"]
        freeze_reference = attachment["freeze_receipt"]
        arm["freeze_receipt"] = {
            "receipt_id": Path(freeze_reference["path"]).stem,
            "path": freeze_reference["path"],
            "sha256": freeze_reference["sha256"],
        }
        arm["row_registry"] = attachment["row_registry"]
        arm_raw = arm_readiness.render_json(arm)
        arm_path.write_bytes(arm_raw)
        arm_path.with_name(f"{arm_path.name}.sha256").write_bytes(
            arm_readiness.gnu_sidecar(
                hashlib.sha256(arm_raw).hexdigest(), arm_path.name
            )
        )

        window_root = custody / "window-plan"
        window_root.mkdir()
        (window_root / "window.env").write_text(f"PACK_ROOT={pack}\n")
        chain_path = window_root / "window-chain.zsh"
        chain_path.write_text("#!/bin/zsh\nexit 0\n")
        exec_argv = [
            "/usr/bin/caffeinate",
            "-is",
            "/bin/zsh",
            str(chain_path),
            str(window_root),
        ]
        manifest_path = (
            custody
            / pack.name
            / "arm_readiness.t0.inputs"
            / "launch-manifest.json"
        )
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(
            arm_readiness.render_json(
                {
                    "schema_version": arm_readiness.LAUNCH_MANIFEST_SCHEMA,
                    "boot_session_id": TEST_BOOT_SESSION_ID,
                    "window_plan_root": str(window_root),
                    "prewindow_command": ["/bin/true"],
                    "launch_command": exec_argv,
                }
            )
        )
        return argparse.Namespace(
            arm_path=arm_path,
            boot_session_id=TEST_BOOT_SESSION_ID,
            custody=custody,
            table_digest=hashlib.sha256(table_raw).hexdigest(),
            table_path=table_path,
            argv=[
                "--pack-root",
                str(pack),
                "--arm-receipt",
                str(arm_path),
                "--arm-readiness-custody-root",
                str(custody),
                "--launch-manifest",
                str(manifest_path),
            ],
        )

    def _run_real_confirmation_reach(
        self, supply: argparse.Namespace, extra_argv: list[str]
    ) -> tuple[Path, str]:
        reached: list[tuple[Path | None, str | None]] = []

        def stop_at_authenticator(
            confirmation_path: Path | str | None,
            expected_confirmation_digest: str | None,
        ) -> None:
            reached.append(
                (
                    Path(confirmation_path)
                    if confirmation_path is not None
                    else None,
                    expected_confirmation_digest,
                )
            )
            raise arm_readiness.FamilyPublicationError(
                "confirmation_mismatch", "confirmation reach sentinel"
            )

        sink, stdout_patch = self._captured_stdout(launch_window)
        with stdout_patch, mock.patch.object(
            arm_readiness,
            "_current_boot_session_id",
            return_value=supply.boot_session_id,
        ), mock.patch.object(
            arm_readiness,
            "_authenticate_confirmation_table",
            side_effect=stop_at_authenticator,
        ) as authenticator, mock.patch.object(
            launch_window, "_consume_launch_capability"
        ) as consume, mock.patch.object(
            launch_window, "verify_consumed_launch"
        ) as verify_consumed, mock.patch.object(
            launch_window.os, "execve"
        ) as execve:
            code = launch_window.main(supply.argv + extra_argv)
        refusal = json.loads(sink.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(refusal["status"], "REFUSE")
        self.assertIn("confirmation reach sentinel", refusal["detail"])
        authenticator.assert_called_once()
        consume.assert_not_called()
        verify_consumed.assert_not_called()
        execve.assert_not_called()
        self.assertEqual(len(reached), 1)
        observed_path, observed_digest = reached[0]
        self.assertIsNotNone(observed_path)
        self.assertIsNotNone(observed_digest)
        return observed_path, observed_digest

    def test_launch_cli_real_chain_reaches_confirmation_authenticator(
        self,
    ) -> None:
        supply = self._real_confirmation_reach_fixture()
        cases = (
            (
                "explicit operator path",
                [
                    "--step6-confirmation-table",
                    str(supply.table_path),
                    "--expected-confirmation-digest",
                    supply.table_digest,
                ],
                supply.table_path,
            ),
            (
                "auto-resolved custody path",
                [
                    "--expected-confirmation-digest",
                    supply.table_digest,
                ],
                supply.arm_path.resolve().parent.parent.parent
                / "family_publication"
                / arm_readiness.STEP6_CONFIRMATION_TABLE_NAME,
            ),
        )
        for label, extra_argv, expected_path in cases:
            with self.subTest(case=label):
                observed_path, observed_digest = (
                    self._run_real_confirmation_reach(supply, extra_argv)
                )
                # The explicit expectation stays unresolved to pin the exact
                # argv Path. The default starts from the resolved arm receipt,
                # just as _verify_arm_receipt does, then compares the derived
                # lexical Path without a final resolve() that could hide a
                # substitution.
                if observed_path != expected_path:
                    self.fail(
                        "confirmation authenticator path mismatch: "
                        f"spy recorded {observed_path}; expected {expected_path}"
                    )
                self.assertEqual(observed_digest, supply.table_digest)

    @staticmethod
    def _confirmation_verifier(supply: argparse.Namespace) -> object:
        def verify_arm(
            _pack_root: Path,
            _arm_receipt: Path,
            *,
            require_unconsumed: bool,
            step6_confirmation_table: Path | None = None,
            expected_confirmation_digest: str | None = None,
        ) -> dict[str, object]:
            if require_unconsumed:
                raise AssertionError("launcher must replay the arm as consumed")
            confirmation_path = (
                step6_confirmation_table
                if step6_confirmation_table is not None
                else supply.default_table_path
            )
            try:
                arm_readiness._require_confirmed_conditional_path(
                    supply.repository,
                    supply.head,
                    supply.successor_relative,
                    supply.lifecycle_registry,
                    confirmation_path,
                    expected_confirmation_digest=expected_confirmation_digest,
                    evidence_id="freeze-doctrine-pin-v1",
                )
            except arm_readiness.EvidenceLifecycleError as exc:
                raise arm_readiness.ArmReadinessError(
                    exc.reason_code, str(exc)
                ) from exc
            supply.gate_discharged = True
            return supply.verified_arm

        return verify_arm

    def _run_confirmation_refusal(
        self, supply: argparse.Namespace, extra_argv: list[str]
    ) -> tuple[dict[str, object], mock.Mock]:
        sink, stdout_patch = self._captured_stdout(launch_window)
        supply.gate_discharged = False
        with stdout_patch, mock.patch.object(
            launch_window,
            "_verify_arm_receipt",
            side_effect=self._confirmation_verifier(supply),
        ) as verify_arm, mock.patch.object(
            launch_window, "_consume_launch_capability"
        ) as consume, mock.patch.object(
            launch_window, "verify_consumed_launch"
        ) as verify_consumed, mock.patch.object(
            launch_window.os, "execve"
        ) as execve:
            code = launch_window.main(supply.argv + extra_argv)
        refusal = json.loads(sink.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(refusal["status"], "REFUSE")
        self.assertEqual(refusal["reason_codes"], [supply.changed_set_code])
        self.assertFalse(supply.gate_discharged)
        consume.assert_not_called()
        verify_consumed.assert_not_called()
        execve.assert_not_called()
        return refusal, verify_arm

    def test_evidence_author_cli_requires_absolute_existing_checkout(self) -> None:
        pack = ROOT / "tests"
        with self.assertRaises(SystemExit) as caught:
            author_arm_readiness_evidence.main(["--pack-root", str(pack)])
        self.assertEqual(caught.exception.code, 2)

        declarations = (
            "relative-measurement-checkout",
            str(ROOT / ".definitely-absent-measurement-checkout"),
        )
        for declaration in declarations:
            with self.subTest(declaration=declaration):
                sink, stdout_patch = self._captured_stdout(
                    author_arm_readiness_evidence
                )
                with stdout_patch:
                    code = author_arm_readiness_evidence.main(
                        [
                            "--pack-root",
                            str(pack),
                            "--measurement-checkout",
                            declaration,
                        ]
                    )
                self.assertEqual(code, 2)
                refusal = json.loads(sink.getvalue())
                self.assertEqual(
                    refusal["reason_codes"],
                    ["readiness_r1_measurement_checkout"],
                )

    def test_launch_cli_refuses_unconfirmed_table_and_accepts_operator_digest(
        self,
    ) -> None:
        supply = self._confirmation_supply_fixture(table_at_default=True)
        for label, extra_argv in (
            ("digest absent", []),
            (
                "digest wrong",
                ["--expected-confirmation-digest", "0" * 64],
            ),
        ):
            with self.subTest(case=label):
                self._run_confirmation_refusal(supply, extra_argv)

        correct_argv = supply.argv + [
            "--expected-confirmation-digest",
            supply.table_digest,
        ]
        supply.gate_discharged = False
        with mock.patch.object(
            launch_window,
            "_verify_arm_receipt",
            side_effect=self._confirmation_verifier(supply),
        ), mock.patch.object(
            launch_window, "_install_handoff"
        ), mock.patch.object(
            launch_window,
            "_consume_launch_capability",
            return_value={"consumption_path": "/tmp/consumed.json"},
        ) as consume, mock.patch.object(
            launch_window,
            "verify_consumed_launch",
            return_value={"exec_argv": supply.launch_fixture.exec_argv},
        ) as verify, mock.patch.object(
            launch_window.os, "execve", side_effect=SystemExit(0)
        ) as execve:
            with self.assertRaises(SystemExit) as exited:
                launch_window.main(correct_argv)
        self.assertEqual(exited.exception.code, 0)
        self.assertTrue(supply.gate_discharged)
        consume.assert_called_once()
        verify.assert_called_once()
        execve.assert_called_once()
        self.assertEqual(
            consume.call_args.kwargs["expected_confirmation_digest"],
            supply.table_digest,
        )
        self.assertEqual(
            verify.call_args.kwargs["expected_confirmation_digest"],
            supply.table_digest,
        )

    def test_launch_cli_leg_a_accepts_valid_pair_at_nondefault_table_path(
        self,
    ) -> None:
        supply = self._confirmation_supply_fixture(table_at_default=False)
        self.assertNotEqual(supply.table_path, supply.default_table_path)
        self.assertFalse(supply.default_table_path.exists())
        argv = supply.argv + [
            "--step6-confirmation-table",
            str(supply.table_path),
            "--expected-confirmation-digest",
            supply.table_digest,
        ]
        with mock.patch.object(
            launch_window,
            "_verify_arm_receipt",
            side_effect=self._confirmation_verifier(supply),
        ) as verify_arm, mock.patch.object(
            launch_window, "_install_handoff"
        ), mock.patch.object(
            launch_window,
            "_consume_launch_capability",
            return_value={"consumption_path": "/tmp/consumed.json"},
        ) as consume, mock.patch.object(
            launch_window,
            "verify_consumed_launch",
            return_value={"exec_argv": supply.launch_fixture.exec_argv},
        ) as verify_consumed, mock.patch.object(
            launch_window.os, "execve", side_effect=SystemExit(0)
        ) as execve:
            with self.assertRaises(SystemExit) as exited:
                launch_window.main(argv)
        self.assertEqual(exited.exception.code, 0)
        self.assertTrue(supply.gate_discharged)
        execve.assert_called_once()
        for consumer in (verify_arm, consume, verify_consumed):
            self.assertEqual(
                consumer.call_args.kwargs["step6_confirmation_table"],
                supply.table_path,
            )
            self.assertEqual(
                consumer.call_args.kwargs["expected_confirmation_digest"],
                supply.table_digest,
            )

    def test_launch_cli_leg_b_refuses_correct_digest_without_table_path(
        self,
    ) -> None:
        supply = self._confirmation_supply_fixture(table_at_default=False)
        refusal, verify_arm = self._run_confirmation_refusal(
            supply,
            ["--expected-confirmation-digest", supply.table_digest],
        )
        self.assertIn("custody artifact is absent", refusal["detail"])
        self.assertIn(str(supply.default_table_path), refusal["detail"])
        self.assertNotIn(
            "table bytes differ from the expected confirmation digest",
            refusal["detail"],
        )
        self.assertIsNone(
            verify_arm.call_args.kwargs["step6_confirmation_table"]
        )

    def test_launch_cli_leg_c_refuses_table_path_without_digest(self) -> None:
        supply = self._confirmation_supply_fixture(table_at_default=False)
        refusal, verify_arm = self._run_confirmation_refusal(
            supply,
            ["--step6-confirmation-table", str(supply.table_path)],
        )
        self.assertIn(
            "no expected confirmation digest supplied", refusal["detail"]
        )
        self.assertEqual(
            verify_arm.call_args.kwargs["step6_confirmation_table"],
            supply.table_path,
        )

    def test_launch_cli_leg_d_refuses_malformed_digest(self) -> None:
        supply = self._confirmation_supply_fixture(table_at_default=False)
        refusal, _verify_arm = self._run_confirmation_refusal(
            supply,
            [
                "--step6-confirmation-table",
                str(supply.table_path),
                "--expected-confirmation-digest",
                "A" * 64,
            ],
        )
        self.assertIn(
            "supplied expected confirmation digest is malformed",
            refusal["detail"],
        )

    def test_launch_cli_leg_e_refuses_mismatched_table_bytes(self) -> None:
        supply = self._confirmation_supply_fixture(table_at_default=False)
        refusal, _verify_arm = self._run_confirmation_refusal(
            supply,
            [
                "--step6-confirmation-table",
                str(supply.table_path),
                "--expected-confirmation-digest",
                "0" * 64,
            ],
        )
        self.assertIn(
            "table bytes differ from the expected confirmation digest",
            refusal["detail"],
        )
        self.assertNotIn(
            "no expected confirmation digest supplied", refusal["detail"]
        )
        self.assertNotIn(
            "no step-6 confirmation table supplied", refusal["detail"]
        )

    def test_launch_cli_leg_f_refuses_when_nothing_is_supplied(self) -> None:
        supply = self._confirmation_supply_fixture(table_at_default=False)
        refusal, verify_arm = self._run_confirmation_refusal(supply, [])
        self.assertIn(
            "no expected confirmation digest supplied", refusal["detail"]
        )
        self.assertIsNone(
            verify_arm.call_args.kwargs["step6_confirmation_table"]
        )
        self.assertIsNone(
            verify_arm.call_args.kwargs["expected_confirmation_digest"]
        )


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
