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
from joulewise import arm_readiness_evidence_t0 as t0_evidence
from joulewise import clock_reference
from joulewise.analysis_engine import inputs as analysis_inputs
from joulewise import floor_extraction, whole_window
from tests import test_arm_readiness as arm_readiness_tests
from tests.git_fixture import init_git_fixture


REAL_GO_T0_AUTHENTICATOR = arm_readiness._authenticate_go_t0_evidence

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
            go_inputs = fixture._consumer_inputs()
            for key in ("night_plan", "go_receipt", "step6_confirmation_table", "expected_confirmation_digest"):
                if getattr(args, key, None) is None:
                    setattr(args, key, go_inputs[key])
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
            go_inputs = fixture._consumer_inputs()
            for key in ("night_plan", "go_receipt", "step6_confirmation_table", "expected_confirmation_digest"):
                if getattr(args, key, None) is None:
                    setattr(args, key, go_inputs[key])
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
    # Inspect authored clock evidence with fixed readers, then stop before ARM
    # samples live subprocess clocks. This isolates clock-family arithmetic
    # from the independent live drift and sampling-skew gates.
    def test_mint_keeps_raw_anchors_separate_from_sequence_clock(self) -> None:
        from tests import test_arm_readiness_evidence_t0 as fixtures

        class AuthoringChecked(Exception):
            pass

        make_fixture = fixtures.make_t0_fixture
        author = fixtures.author_arm_readiness_evidence_t0
        two_hours = 7_200_000_000_000
        cases = (
            (10_000_000_000_000, -two_hours),
            (10_000_000_000_000, 0),
            (10_000_000_000_000, two_hours),
            (60_000_000_000, -two_hours),  # Exercise the capture floor.
        )

        for raw_now, offset in cases:
            with self.subTest(raw_now=raw_now, ordinary_minus_raw_ns=offset):
                ordinary = raw_now + offset
                sequence_now = (
                    max(ordinary, 0) + t0_evidence._MIN_IDLE_NS + 1_000
                )
                anchor = clock_reference.ClockAnchor(
                    realtime_ns=1_700_000_000_000_000_000 + raw_now,
                    monotonic_raw_ns=raw_now,
                    read_skew_ns=1_000,
                )
                inputs = []

                def tracked_fixture(**kwargs):
                    result = make_fixture(**kwargs)
                    self.addCleanup(result[0].cleanup)
                    inputs.append(result[-1])
                    return result

                def check_author(*args, **kwargs):
                    result = author(*args, **kwargs)
                    self.assertEqual(result["status"], "PASS", result)
                    self.assertEqual(len(result["authored_rows"]), 15)
                    receipts = [
                        json.loads(Path(p).read_text())
                        for p in result["receipt_paths"]
                    ]
                    receipt = next(
                        r for r in receipts if r["kind"] == "CLOCK_ATTESTATION"
                    )
                    value = receipt["facts"][0]["value"]
                    capture = json.loads(
                        (inputs[0] / "clock-reference.json").read_text()
                    )
                    self.assertEqual(
                        capture["started_monotonic_ns"], max(ordinary, 0) + 10
                    )
                    expected = {
                        "r0_anchor_monotonic_raw_ns":
                            raw_now - t0_evidence._MIN_IDLE_NS - 980,
                        "anchor_monotonic_raw_ns": raw_now,
                        "anchor_realtime_ns": anchor.realtime_ns,
                        "t0_span_ns": t0_evidence._MIN_IDLE_NS + 980,
                        "anchor_delta_ns": 0,
                        "r1_batch_started_monotonic_raw_ns": raw_now,
                        "r1_batch_finished_monotonic_raw_ns": raw_now,
                        "r1_batch_duration_ns": 0,
                        "r1_batch_finished_monotonic_ns": sequence_now,
                    }
                    for field, expected_value in expected.items():
                        self.assertEqual(value[field], expected_value, field)
                    self.assertEqual(
                        receipt["valid_until_monotonic_ns"],
                        sequence_now + 21_600_000_000_000,
                    )
                    raise AuthoringChecked

                with (
                    mock.patch.object(
                        time, "monotonic_ns", return_value=ordinary
                    ),
                    mock.patch.object(
                        clock_reference, "sample_anchor", return_value=anchor
                    ),
                    mock.patch.object(
                        fixtures, "make_t0_fixture", side_effect=tracked_fixture
                    ),
                    mock.patch.object(
                        fixtures,
                        "author_arm_readiness_evidence_t0",
                        side_effect=check_author,
                    ),
                    self.assertRaises(AuthoringChecked),
                ):
                    self._mint_v4_arm()

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
            "ALPHA": "d117_floor_qwen3-1p7b_v5",
            "BETA": "d117_floor_qwen3-8b_v5",
            "GAMMA": "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5",
        }
        live_fixture_now = time.monotonic_ns()
        # Give the synthetic command-capture timeline a complete positive
        # ten-minute history even when a Linux runner booted only seconds ago.
        # The subprocess clock remains live: this offset is confined to the
        # in-process T-0 author and cannot mint the arm capability deadline.
        # The clock-separation regression can deliberately put ordinary time
        # below zero on a freshly booted host. Only the capture timeline needs
        # this floor; keep the live RAW/REALTIME anchors intact for ARM replay.
        fixture_now = max(live_fixture_now, 0) + t0_evidence._MIN_IDLE_NS + 1_000
        temporary, repository, pack, custody, context, input_root = (
            make_t0_fixture(
                now_monotonic_ns=fixture_now,
                synthetic_clock=False,
                # This test is the only one that reaches the real `os.execve`,
                # so its frozen argv must name a program that exists on the CI
                # runner as well as on Darwin.
                portable_launch_program=True,
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
            # This relocation fixture isolates ARM replay. The new GO binder
            # remains real, including the integrated v3 plan parser. The T0
            # inventory has a separate synthetic evidence boundary here.
            + "arm_readiness._authenticate_go_t0_evidence = lambda *args: None\n"
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
                # D-154 R-3 (MINT-CHECKOUT-DECLARATION-01): the mint requires an
                # explicit operator declaration; the fixture's own repository is
                # this mint's declared measurement checkout.
                measurement_checkout=repository,
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
        # Main now derives the attestation from this captured R0 reference.
        # Keep capture ordering on the synthetic ordinary-monotonic timeline
        # and R0/author duration on RAW, as in make_t0_fixture. Give R0 the ambient
        # REALTIME-minus-MONOTONIC_RAW relation that the real ARM subprocess
        # independently resamples and checks within the production 5 ms gate.
        # Sample here, immediately before authoring and ARM, so Linux clock
        # discipline cannot accumulate avoidable RAW/realtime drift during the
        # comparatively expensive synthetic mint setup above.
        live_clock_anchor = clock_reference.sample_anchor()
        live_clock_offset_ns = (
            live_clock_anchor.realtime_ns - live_clock_anchor.monotonic_raw_ns
        )
        clock_capture_path = input_root / "clock-reference.json"
        clock_capture = json.loads(clock_capture_path.read_text())
        r0_reference = json.loads(clock_capture["stdout"])
        r0_reference["anchor_realtime_ns"] = (
            live_clock_offset_ns + r0_reference["anchor_monotonic_raw_ns"]
        )
        clock_capture["stdout"] = arm_readiness.render_json(r0_reference).decode(
            "utf-8"
        )
        clock_capture_path.write_bytes(arm_readiness.render_json(clock_capture))
        with author_environment(
            repository,
            now_monotonic_ns=fixture_now,
            sample_anchor=lambda: live_clock_anchor,
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

    def _install_launch_inputs(self, repository, pack, arm_path, manifest_path, custody):
        # Author in the checkout that will execute the launcher. Import only
        # the fixture helpers from the test runner; joulewise stays imported
        # from repository, so both real launcher-identity checks remain live.
        installed = subprocess.run(
            [
                sys.executable, "-c",
                "import json, sys\n"
                "from pathlib import Path\n"
                "from joulewise import arm_readiness\n"
                "assert Path(arm_readiness.__file__).resolve().parents[1] == Path.cwd().resolve()\n"
                "sys.path.insert(0, sys.argv[1])\n"
                "from tests.test_arm_readiness import install_pack_night_launch_inputs\n"
                "inputs = install_pack_night_launch_inputs(*(Path(value) for value in sys.argv[2:]))\n"
                "print(json.dumps(inputs, default=str))\n",
                str(ROOT), str(pack), str(arm_path), str(manifest_path), str(custody),
            ],
            cwd=repository,
            env={**os.environ, "PYTHONPATH": str(repository), "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(installed.returncode, 0, f"{installed.stdout}{installed.stderr}")
        inputs = json.loads(installed.stdout)
        plan = json.loads(Path(inputs["night_plan"]).read_bytes())
        self.assertEqual(plan["measurement_root"], str(repository.resolve()))
        return inputs

    def _run_launch(
        self,
        repository: Path,
        pack: Path,
        arm_path: Path,
        custody: Path,
        manifest_path: Path,
        go_inputs=None,
    ) -> subprocess.CompletedProcess[str]:
        if go_inputs is None:
            go_inputs = self._install_launch_inputs(
                repository, pack, arm_path, manifest_path, custody)
        return subprocess.run(
            [
                sys.executable,
                str(repository / "scripts/launch_window.py"),
                "--night-plan", str(go_inputs["night_plan"]),
                "--go-receipt", str(go_inputs["go_receipt"]),
                "--step6-confirmation-table", str(go_inputs["step6_confirmation_table"]),
                "--expected-confirmation-digest", go_inputs["expected_confirmation_digest"],
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

    def test_real_minted_v4_go_binds_root_and_refuses_content_change(
        self,
    ) -> None:
        temporary, repository, pack, custody, arm_path, manifest_path = (
            self._mint_v4_arm()
        )
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        pack_relative = pack.relative_to(repository)
        go_inputs = self._install_launch_inputs(
            repository, pack, arm_path, manifest_path, custody)

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
            go_inputs,
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
        relocated = self._run_launch(
            relocated_repository,
            relocated_pack,
            arm_path,
            custody,
            manifest_path,
            go_inputs,
        )
        self.assertEqual(relocated.returncode, 2, relocated.stderr)
        refusal = json.loads(relocated.stdout)
        self.assertEqual(refusal["reason_codes"], ["launch_go_receipt_invalid"])
        self.assertIn("pack_root", refusal["detail"])
        # D-176 binds an absolute pack locator. Restore the original locator
        # without changing the ARM or GO bytes; its real launch still succeeds.
        pack.unlink()
        shutil.copytree(relocated_pack, pack)
        accepted = self._run_launch(repository, pack, arm_path, custody, manifest_path, go_inputs)
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
        init_git_fixture(repository, "-q")
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
        go_inputs = arm_readiness_tests.install_pack_night_launch_inputs(
            launch_fixture.pack, launch_fixture.arm_path, launch_fixture.manifest_path,
            launch_fixture.custody, table_path, hashlib.sha256(table_raw).hexdigest())
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
                "--night-plan", str(go_inputs["night_plan"]),
                "--go-receipt", str(go_inputs["go_receipt"]),
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
            # D-154 R-3: the mint requires an explicit operator declaration;
            # this fixture's own repository is its declared measurement checkout.
            minted = arm_readiness.generate_freeze_receipt(
                pack, measurement_checkout=repository
            )
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
        go_inputs = arm_readiness_tests.install_pack_night_launch_inputs(
            pack, arm_path, manifest_path, custody, table_path, hashlib.sha256(table_raw).hexdigest())
        return argparse.Namespace(
            arm_path=arm_path,
            boot_session_id=TEST_BOOT_SESSION_ID,
            custody=custody,
            table_digest=hashlib.sha256(table_raw).hexdigest(),
            table_path=table_path,
            argv=[
                "--night-plan", str(go_inputs["night_plan"]),
                "--go-receipt", str(go_inputs["go_receipt"]),
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
        missing_pair = not all(flag in extra_argv for flag in (
            "--step6-confirmation-table", "--expected-confirmation-digest"))
        self.assertEqual(refusal["reason_codes"],
                         ["confirmation_missing" if missing_pair else supply.changed_set_code])
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
            ("digest absent", ["--step6-confirmation-table", str(supply.table_path)]),
            (
                "digest wrong",
                ["--step6-confirmation-table", str(supply.table_path), "--expected-confirmation-digest", "0" * 64],
            ),
        ):
            with self.subTest(case=label):
                self._run_confirmation_refusal(supply, extra_argv)

        correct_argv = supply.argv + [
            "--step6-confirmation-table", str(supply.table_path),
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

    def test_launch_cli_leg_b_refuses_correct_digest_without_table_path(self) -> None:
        supply = self._confirmation_supply_fixture(table_at_default=False)
        refusal, verify_arm = self._run_confirmation_refusal(
            supply, ["--expected-confirmation-digest", supply.table_digest])
        self.assertEqual(refusal["reason_codes"], ["confirmation_missing"])
        verify_arm.assert_not_called()

    def test_launch_cli_leg_c_refuses_table_path_without_digest(self) -> None:
        supply = self._confirmation_supply_fixture(table_at_default=False)
        refusal, verify_arm = self._run_confirmation_refusal(
            supply, ["--step6-confirmation-table", str(supply.table_path)])
        self.assertEqual(refusal["reason_codes"], ["confirmation_missing"])
        verify_arm.assert_not_called()

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
        self.assertEqual(refusal["reason_codes"], ["confirmation_missing"])
        verify_arm.assert_not_called()


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


class PackNightGoRefusalHandlerTests(unittest.TestCase):
    # Python 3.14 argparse must not probe the mocked stdout for color support.
    @mock.patch.dict(os.environ, {"PYTHON_COLORS": "0", "NO_COLOR": "1"})
    def test_cli_uses_one_json_handler_for_both_exception_families(self) -> None:
        argv = ["--pack-root", "/pack", "--arm-receipt", "/arm.json",
                "--arm-readiness-custody-root", "/custody",
                "--launch-manifest", "/manifest.json"]
        for error in (
            arm_readiness.ArmReadinessError("readiness_usage_invalid", "missing keyword"),
            arm_readiness.LaunchLineageError("launch_go_receipt_missing", "missing GO"),
            arm_readiness.LaunchLineageError("launch_go_receipt_invalid", "sha256"),
        ):
            with self.subTest(code=error.reason_code):
                output = io.BytesIO()
                stdout = mock.Mock(buffer=output)
                with mock.patch.object(launch_window, "launch", side_effect=error), \
                     mock.patch.object(launch_window.sys, "stdout", stdout):
                    self.assertEqual(launch_window.main(argv), 2)
                self.assertEqual(json.loads(output.getvalue()), {
                    "status": "REFUSE", "reason_codes": [error.reason_code],
                    "detail": str(error),
                })


class PackNightLaunchBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.case = arm_readiness_tests.PackNightConsumerTests()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.fixture = self.case.fixture
        inputs = self.case.inputs
        self.base_argv = ["--pack-root", str(self.fixture.pack), "--arm-receipt", str(self.fixture.arm_path),
            "--arm-readiness-custody-root", str(self.fixture.custody),
            "--launch-manifest", str(self.fixture.manifest_path)]
        self.argv = self.base_argv + ["--night-plan", str(inputs["night_plan"]),
            "--go-receipt", str(inputs["go_receipt"]),
            "--step6-confirmation-table", str(inputs["step6_confirmation_table"]),
            "--expected-confirmation-digest", inputs["expected_confirmation_digest"]]

    def arm_patches(self):
        from contextlib import ExitStack
        stack = ExitStack()
        verified = {"status": "PASS", "arm_disposition": "GO", "receipt_path": str(self.fixture.arm_path.resolve()),
                    "receipt_sha256": self.case.inputs["arm_receipt_sha256"],
                    "pack_sha256": self.fixture.arm["pack"]["pack_sha256"]}
        for owner, name, value in (
            (launch_window, "_verify_arm_receipt", verified),
            (arm_readiness, "_verify_arm_receipt", verified),
            (arm_readiness, "reviewed_main", self.fixture.arm["reviewed_main"]),
            (arm_readiness, "_root_policy_refusals", ([], set())),
            (arm_readiness, "_derive_arm_semantics_for_verification", (self.fixture.arm["rows"], self.fixture.arm["refusals"])),
        ):
            stack.enter_context(mock.patch.object(owner, name, return_value=value))
        return stack

    def test_integrated_driver_arm_go_launcher_consumption_and_replay(self):
        """Real driver/parser/GO/consumer/replay; synthetic ARM and machine probes."""
        from dataclasses import replace
        from datetime import datetime
        from joulewise import night_gate
        from joulewise.measurement_liveness import Identity
        from tests.test_run_night import _load_driver, ProbeSource, FakeProcess, _probe
        from tests.test_arm_readiness_schemas import sample_evidence

        driver = _load_driver()
        fixture = self.fixture
        events = []
        custody_pack = fixture.custody / fixture.pack.name
        input_root = custody_pack / t0_evidence._INPUT_DIRECTORY
        fixture.arm["arm_context"]["custody_root"] = str(fixture.custody)
        (input_root / "arm-context.json").write_bytes(arm_readiness.render_json(fixture.arm["arm_context"]))
        plan_path = self.case.inputs["night_plan"]
        plan = json.loads(plan_path.read_bytes())
        plan["t0_epoch_s"] = datetime(2026, 9, 2, 1, 0).timestamp()
        plan["authored_epoch_s"] = plan["t0_epoch_s"] - 1
        plan_path.write_bytes(arm_readiness.render_json(plan))
        for name in ("go_receipt.json", "go-census.json"):
            (fixture.custody / "night" / name).unlink()
        fixture.arm_path.unlink()
        fixture.arm_path.with_name(fixture.arm_path.name + ".sha256").unlink()

        def author(pack, custody):
            events.append("T0")
            now = time.monotonic_ns()
            captures = []
            for index, (step, name) in enumerate(t0_evidence._CAPTURE_FILES.items()):
                path = input_root / name
                path.write_bytes(arm_readiness.render_json({
                    "schema_version": t0_evidence._COMMAND_SCHEMA, "step_id": step,
                    "argv": ["/fixture/probe"], "cwd": str(custody), "exit_code": 0,
                    "stdout": "", "stderr": "", "started_monotonic_ns": now - 100 + index * 2,
                    "finished_monotonic_ns": now - 99 + index * 2,
                    "boot_session_id": fixture.arm["boot_session_id"]}))
                captures.append(fixture._artifact(path))
            recipe_path = custody_pack / fixture.arm["evidence"][0]["path"]
            recipe = json.loads(recipe_path.read_bytes())
            source_path = custody_pack / recipe["facts"][0]["source_path"]
            source = json.loads(source_path.read_bytes())
            source["input_artifacts"].extend(captures)
            source_path.write_bytes(arm_readiness.render_json(source))
            source_digest = fixture._artifact(source_path)["sha256"]
            paths = []
            fixture.arm["evidence"] = []
            for row in t0_evidence._EXPECTED_ROWS:
                value = copy.deepcopy(recipe) if row == "t0.single_launch_capability" else sample_evidence()
                value.update(evidence_id=t0_evidence._evidence_id(row), kind=t0_evidence._ROW_KIND[row],
                             pack_sha256=fixture.arm["pack"]["pack_sha256"],
                             head_commit=fixture.arm["reviewed_main"]["head_commit"],
                             valid_until_monotonic_ns=fixture.arm["valid_until_monotonic_ns"])
                for fact in value["facts"]:
                    fact.update(source_kind="PROBE", source_path=str(source_path.relative_to(custody_pack)),
                                source_sha256=source_digest)
                path = custody_pack / t0_evidence._EVIDENCE_DIRECTORY / t0_evidence._receipt_name(row)
                path.write_bytes(arm_readiness.render_json(value))
                digest = fixture._artifact(path)["sha256"]
                path.with_name(path.name + ".sha256").write_bytes(arm_readiness.gnu_sidecar(digest, path.name))
                fixture.arm["evidence"].append({"evidence_id": value["evidence_id"],
                    "receipt_kind": value["kind"], "namespace": "WINDOW_CUSTODY",
                    "path": str(path.relative_to(custody_pack)), "sha256": digest,
                    "schema_version": value["schema_version"], "status": "PASS"})
                paths.append(str(path))
            return {"status": "PASS", "receipt_paths": paths}

        def mint_arm(*args, **kwargs):
            events.append("ARM")
            fixture._rewrite_arm()
            return verified()

        def verified(*args, **kwargs):
            return {"status": "PASS", "arm_disposition": "GO", "receipt_path": str(fixture.arm_path),
                    "receipt_sha256": fixture._artifact(fixture.arm_path)["sha256"],
                    "pack_sha256": fixture.arm["pack"]["pack_sha256"]}

        source = ProbeSource(plan["t0_epoch_s"] + 1)
        source.results[night_gate.BOOT_SESSION_ARGV] = _probe(night_gate.BOOT_SESSION_ARGV,
            stdout=fixture.arm["boot_session_id"] + "\n")
        probes = replace(source.probes(), checkout_head=lambda: plan["repo_head"],
                         measurement_head=lambda root: plan["measurement_head"])
        real_prepare = driver._prepare_pack_night
        def prepare(*args):
            events.append("PREPARE")
            return real_prepare(*args)

        def execute(*args):
            events.append("CONSUMED")
            raise SystemExit(0)

        real_popen = subprocess.Popen
        def spawn(command, **kwargs):
            if not any(str(arg).endswith("scripts/launch_window.py") for arg in command):
                return real_popen(command, **kwargs)
            events.append("GO_ARGV")
            self.assertIs(kwargs["stdin"], subprocess.DEVNULL)
            self.assertEqual(len(command[2:]), 16)
            self.assertTrue((fixture.custody / "night/go_receipt.json").is_file())
            with mock.patch.object(launch_window.os, "execve", side_effect=execute):
                with self.assertRaises(SystemExit) as caught:
                    launch_window.main(command[2:])
            self.assertEqual(caught.exception.code, 0)
            replay = arm_readiness.verify_consumed_launch(fixture.pack, self.case.consumption)
            self.assertEqual(replay["status"], "PASS")
            events.append("REPLAY")
            return FakeProcess(command)

        with mock.patch.object(driver, "make_probes", return_value=probes), \
             mock.patch.object(driver, "_prepare_pack_night", side_effect=prepare), \
             mock.patch.object(driver, "_resolve_courier_bin", return_value=(Path("/fixture/courier"), None, None)), \
             mock.patch.object(driver, "_finish_reporting", side_effect=lambda c, n, p, code, *a, **k: code), \
             mock.patch.object(driver, "observe_identity", return_value=Identity("LIVE", "fixture-start")), \
             mock.patch.object(driver.subprocess, "Popen", side_effect=spawn), \
             mock.patch.object(t0_evidence, "author_arm_readiness_evidence_t0", side_effect=author), \
             mock.patch.object(arm_readiness, "generate_arm_receipt", side_effect=mint_arm), \
             mock.patch.object(arm_readiness, "_verify_arm_receipt", side_effect=verified), \
             mock.patch.object(launch_window, "_verify_arm_receipt", side_effect=verified), \
             mock.patch.object(arm_readiness, "_authenticate_go_t0_evidence", REAL_GO_T0_AUTHENTICATOR), \
             mock.patch.object(arm_readiness, "reviewed_main", return_value=fixture.arm["reviewed_main"]), \
             mock.patch.object(arm_readiness, "_root_policy_refusals", return_value=([], set())), \
             mock.patch.object(arm_readiness, "_derive_arm_semantics_for_verification", return_value=(fixture.arm["rows"], fixture.arm["refusals"])):
            result = driver.run_night(plan_path)
            self.assertEqual(result, driver.EXIT_GO, (fixture.custody / "night/receipt.json").read_text() if result else events)
        self.assertEqual(events, ["PREPARE", "T0", "ARM", "PREPARE", "GO_ARGV", "CONSUMED", "REPLAY"])
        consumption = json.loads(self.case.consumption.read_bytes())
        go_path = fixture.custody / "night/go_receipt.json"
        go = json.loads(go_path.read_bytes())
        import uuid
        self.assertEqual(uuid.UUID(go["receipt_id"]).version, 4)
        self.assertEqual(str(uuid.UUID(go["receipt_id"])), go["receipt_id"])
        self.assertEqual(len(go["t0_evidence"]), 21)
        self.assertEqual(consumption["go_receipt"]["sha256"], fixture._artifact(go_path)["sha256"])
        self.assertEqual(consumption["night_plan"]["sha256"], fixture._artifact(plan_path)["sha256"])

    @mock.patch.dict(os.environ, {"PYTHON_COLORS": "0", "NO_COLOR": "1"})
    def test_each_required_cli_flag_omission_refuses_before_consumption(self):
        for flag in ("--night-plan", "--go-receipt", "--step6-confirmation-table", "--expected-confirmation-digest"):
            with self.subTest(flag=flag):
                argv = list(self.argv)
                index = argv.index(flag)
                del argv[index:index + 2]
                output = io.BytesIO()
                with mock.patch.object(launch_window.sys, "stdout", mock.Mock(buffer=output)), \
                     mock.patch.object(launch_window, "_consume_launch_capability") as consume, \
                     mock.patch.object(launch_window.os, "execve") as execute:
                    self.assertEqual(launch_window.main(argv), 2)
                expected = "readiness_usage_invalid" if flag in ("--night-plan", "--go-receipt") else "confirmation_missing"
                self.assertEqual(json.loads(output.getvalue())["reason_codes"], [expected])
                consume.assert_not_called()
                execute.assert_not_called()
                self.assertFalse(self.case.consumption.exists())

    @mock.patch.dict(os.environ, {"PYTHON_COLORS": "0", "NO_COLOR": "1"})
    def test_cli_then_callee_go_mutation_is_detected_by_the_real_callee(self):
        real_consume = arm_readiness._consume_launch_capability
        def mutate_then_consume(**inputs):
            path = Path(inputs["go_receipt"])
            path.write_bytes(path.read_bytes() + b" ")
            return real_consume(**inputs)
        output = io.BytesIO()
        with self.arm_patches(), mock.patch.object(launch_window, "_install_handoff"), \
             mock.patch.object(launch_window, "_consume_launch_capability", side_effect=mutate_then_consume), \
             mock.patch.object(launch_window.os, "execve") as execute, \
             mock.patch.object(launch_window.sys, "stdout", mock.Mock(buffer=output)):
            self.assertEqual(launch_window.main(self.argv), 2)
        self.assertEqual(json.loads(output.getvalue())["reason_codes"], ["launch_go_receipt_invalid"])
        self.assertIn("sha256", json.loads(output.getvalue())["detail"])
        execute.assert_not_called()
        self.assertFalse(self.case.consumption.exists())

    def test_child_start_uses_persisted_confirmation_and_plan_without_environment_transport(self):
        digest = self.case.inputs["expected_confirmation_digest"]
        child_output = io.BytesIO()
        def execute(_program, _argv, environment):
            self.assertNotIn(digest, environment)
            self.assertNotIn(digest, environment.values())
            self.assertNotIn(str(self.case.inputs["step6_confirmation_table"]), environment.values())
            args = launch_window._parser().parse_args(self.base_argv + ["--lifecycle-event", "start"])
            self.assertIsNone(args.night_plan)
            self.assertIsNone(args.go_receipt)
            self.assertIsNone(args.step6_confirmation_table)
            self.assertIsNone(args.expected_confirmation_digest)
            with mock.patch.object(launch_window.sys, "stdout", mock.Mock(buffer=child_output)):
                self.assertEqual(launch_window.lifecycle(args), 0)
            raise SystemExit(0)
        with self.arm_patches(), mock.patch.object(launch_window.os, "execve", side_effect=execute):
            with self.assertRaises(SystemExit) as caught:
                launch_window.main(self.argv)
        self.assertEqual(caught.exception.code, 0)
        self.assertTrue(arm_readiness._lifecycle_receipt_path(self.case.consumption, "start").is_file())
        value = json.loads(self.case.consumption.read_bytes())
        self.assertEqual(value["step6_confirmation"]["table_sha256"], digest)
        self.assertEqual(value["night_plan"]["path"], str(self.case.inputs["night_plan"]))

    def test_child_refuses_substituted_pair_changed_plan_and_missing_go(self):
        self.case.consume()
        with self.assertRaisesRegex(arm_readiness.LaunchLineageError, "table_sha256"):
            self.case.verify(expected_confirmation_digest="f" * 64)
        path = self.case.inputs["night_plan"]
        raw = path.read_bytes()
        path.write_bytes(raw + b" ")
        with self.assertRaisesRegex(arm_readiness.LaunchLineageError, "plan_sha256"):
            self.case.verify()
        path.write_bytes(raw)
        self.case.inputs["go_receipt"].unlink()
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            self.case.verify()
        self.assertEqual(caught.exception.reason_code, "launch_go_receipt_missing")
        self.assertFalse(arm_readiness._lifecycle_receipt_path(self.case.consumption, "start").exists())

    def test_g7_control_refuses_both_presentations_before_missing_arm(self):
        self._g7_control_case()

    def test_g7_control_refuses_symlinked_night_without_changing_completed_rehearsal(self):
        self._g7_control_case(symlink="night")

    def test_g7_control_refuses_symlinked_control_before_writes(self):
        self._g7_control_case(symlink="control")

    def test_g7_non_pack_plan_refusal_artifact_fails_bytes_only_acceptance(self):
        self._g7_control_case(non_pack=True)

    @mock.patch.dict(os.environ, {"PYTHON_COLORS": "0", "NO_COLOR": "1"})
    def _g7_control_case(self, *, symlink=None, non_pack=False):
        """§10.5 admission regression: the control deliberately has no ARM.

        This pins the required production-entry behavior, not a substitute
        validator. The consumer admission must run before the absent ARM is accessed.
        """
        from joulewise import t0_rehearsal

        window_id = t0_rehearsal.REHEARSAL_WINDOW_PREFIX + "g7-fixture"
        parent = Path(self.fixture.temporary.name).resolve() / "home/night-custody"
        rehearsal_root = parent / window_id
        control = parent / (window_id + "-g7-control")
        rehearsal_root.mkdir(parents=True)
        control.mkdir()
        # Preserve completed-night evidence while presenting from its sibling.
        consumed = rehearsal_root / "arm-0001.consumed.json"
        started = rehearsal_root / "chain.started"
        consumed.write_bytes(b"completed rehearsal consumption fixture\n")
        started.write_bytes(b"completed rehearsal capture fixture\n")
        preserved = {path: path.read_bytes() for path in (consumed, started)}
        plan = json.loads(self.case.inputs["night_plan"].read_bytes())
        plan["custody_root"] = str(control)
        authorization = json.loads(Path(plan["pack_night"]["authorization_record"]["path"]).read_bytes())
        authorization.update(purpose="CAMPAIGN_TRANSACTION", authority="V5-TRANSACTION-GO-01")
        auth_path = control / "authorization.json"
        auth_path.write_bytes(arm_readiness.render_json(authorization))
        plan["pack_night"]["authorization_record"] = {
            "path": str(auth_path), "sha256": hashlib.sha256(auth_path.read_bytes()).hexdigest()}
        confirmation_path = control / "confirmation.json"
        confirmation_path.write_bytes(Path(plan["pack_night"]["confirmation_record"]["path"]).read_bytes())
        plan["pack_night"]["confirmation_record"] = {
            "path": str(confirmation_path), "sha256": hashlib.sha256(confirmation_path.read_bytes()).hexdigest()}
        plan_path = control / "night_plan.json"
        plan_path.write_bytes(arm_readiness.render_json(plan))
        go = copy.deepcopy(self.case.inputs["authenticated_go_receipt"])
        go["purpose"] = "T0_REHEARSAL"
        go["authorization"]["purpose"] = "T0_REHEARSAL"
        source_go = rehearsal_root / "night/go_receipt.json"
        source_go.parent.mkdir()
        source_go.write_bytes(arm_readiness.render_json(go))
        preserved[source_go] = source_go.read_bytes()
        six_key = {
            "schema_version": t0_rehearsal.REHEARSAL_RECEIPT_SCHEMA,
            "receipt_class": t0_rehearsal.REHEARSAL_RECEIPT_CLASS,
            "claim_eligible": False, "window_id": window_id,
            "custody_root": str(rehearsal_root), "acceptance_target": "T0-UNATTENDED-01",
        }
        from tests.test_run_night import _load_driver
        driver = _load_driver()
        source_receipt = rehearsal_root / "rehearsal-receipt.json"
        source_receipt.write_bytes(arm_readiness.render_json(six_key))
        preserved[source_receipt] = source_receipt.read_bytes()
        if symlink:
            if symlink == "night":
                (control / "night").symlink_to(source_go.parent, target_is_directory=True)
            else:
                actual = control.with_name(control.name + "-actual")
                control.rename(actual)
                control.symlink_to(actual, target_is_directory=True)
            before = {str(path.relative_to(rehearsal_root)): path.read_bytes()
                      for path in rehearsal_root.rglob("*") if path.is_file()}
            with mock.patch.object(Path, "home", return_value=parent.parent), \
                 mock.patch.object(driver.subprocess, "run") as launch:
                with self.assertRaisesRegex(driver.PackNightRefusal, "non-symlink"):
                    driver.produce_g7_control(plan_path, source_receipt, source_go)
            launch.assert_not_called()
            after = {str(path.relative_to(rehearsal_root)): path.read_bytes()
                     for path in rehearsal_root.rglob("*") if path.is_file()}
            self.assertEqual(before, after)  # No new files, and every original byte retained.
            return
        if non_pack:
            # Exercise real admission against a valid non-pack plan. The producer's
            # own guard also refuses it, but bytes-only acceptance must stand alone.
            other_plan = {**plan, "schema": "joulewise.night_plan.v2", "schema_version": 2,
                          "receipt_class": "DIAGNOSTIC_NO_PACK",
                          "registration_path": "configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json"}
            del other_plan["pack_night"]
            non_pack_path = parent / "non-pack-plan.json"
            non_pack_path.write_bytes(arm_readiness.render_json(other_plan))
            with mock.patch.object(Path, "home", return_value=parent.parent):
                original = plan_path.read_bytes()
                plan_path.write_bytes(non_pack_path.read_bytes())
                try:
                    with self.assertRaisesRegex(driver.PackNightRefusal, "G7 production plan"):
                        driver.produce_g7_control(plan_path, source_receipt, source_go)
                finally:
                    plan_path.write_bytes(original)
        calls = []
        def invoke(argv, **kwargs):
            self.assertEqual(len(argv[2:]), 16)
            if non_pack:
                argv = list(argv)
                argv[argv.index("--night-plan") + 1] = str(non_pack_path)
            self.assertIs(kwargs["stdin"], subprocess.DEVNULL)
            calls.append(argv)
            output = io.BytesIO()
            with mock.patch.object(launch_window.sys, "stdout", mock.Mock(buffer=output)):
                rc = launch_window.main(argv[2:])
            return subprocess.CompletedProcess(argv, rc, output.getvalue(), b"")
        with mock.patch.object(Path, "home", return_value=parent.parent), \
             mock.patch.object(driver.subprocess, "run", side_effect=invoke), \
             mock.patch.object(launch_window, "_verify_arm_receipt") as verify, \
             mock.patch.object(arm_readiness, "_verify_arm_receipt") as consumer_verify, \
             mock.patch.object(launch_window, "_consume_launch_capability") as consume, \
             mock.patch.object(launch_window.os, "execve") as execute:
            locator = driver.produce_g7_control(plan_path, source_receipt, source_go)
            with self.assertRaises((driver.PackNightRefusal, FileExistsError)):
                driver.produce_g7_control(plan_path, source_receipt, source_go)
        verify.assert_not_called()
        consumer_verify.assert_not_called()
        consume.assert_not_called()
        execute.assert_not_called()
        self.assertEqual(len(calls), 2)
        path = Path(locator["path"])
        artifact = json.loads(path.read_bytes())
        self.assertEqual(locator["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        if non_pack:
            self.assertEqual(artifact["verdict"], "FAIL")
            self.assertEqual([item["refusal"]["detail"] for item in artifact["presented"]],
                             ["go_receipt.receipt_class", "night_plan.receipt_class"])
            artifact["verdict"] = "PASS"  # Even a relabeled artifact cannot pass.
            with self.assertRaisesRegex(ValueError, "class/purpose"):
                t0_rehearsal.validate_g7_control(json.loads(arm_readiness.render_json(artifact)))
            return
        self.assertEqual(artifact["verdict"], "PASS")
        self.assertEqual(artifact["control_plan_sha256"], hashlib.sha256(plan_path.read_bytes()).hexdigest())
        t0_rehearsal.validate_g7_control(artifact)
        self.assertEqual((control / "night/presented_go_receipt.json").read_bytes(), source_go.read_bytes())
        self.assertEqual(list(control.rglob("*.consumed.json")), [])
        self.assertEqual(list(control.rglob("chain.started")), [])
        for path, original in preserved.items():
            self.assertEqual(path.read_bytes(), original)

    @mock.patch.dict(os.environ, {"PYTHON_COLORS": "0", "NO_COLOR": "1"})
    def test_valid_rehearsal_class_refused_by_production_entry_and_consumer(self):
        """B4: real six-key rehearsal authority, never a malformed GO surrogate."""
        from joulewise import t0_rehearsal
        from tests.test_t0_rehearsal import FixtureBuilder, fixture_bundle

        with tempfile.TemporaryDirectory() as temporary:
            rehearsal_root = FixtureBuilder(Path(temporary)).build()
            rehearsal_consumptions = {
                path: path.read_bytes() for path in rehearsal_root.rglob("*.consumed.json")
            }
            self.assertEqual(len(rehearsal_consumptions), 1)
            bundle = fixture_bundle(rehearsal_root)
            self.assertEqual(t0_rehearsal.evaluate_g6(bundle).status,
                             t0_rehearsal.GateStatus.PASS)
            presented = bundle.record("rehearsal_receipt")
            self.assertEqual(set(presented.value), t0_rehearsal._REHEARSAL_RECEIPT_KEYS)
            go_path = self.case.inputs["go_receipt"]
            go_path.write_bytes(presented.raw)
            self.case.inputs.update(authenticated_go_receipt=presented.value,
                                    go_receipt_sha256=presented.sha256)
            detail = "go_receipt.receipt_class"
            output = io.BytesIO()
            with mock.patch.object(launch_window.os, "execve") as execute, \
                 mock.patch.object(launch_window.sys, "stdout", mock.Mock(buffer=output)):
                self.assertEqual(launch_window.main(self.argv), 2)
            self.assertEqual(json.loads(output.getvalue()), {
                "status": "REFUSE", "reason_codes": ["launch_go_receipt_invalid"],
                "detail": detail,
            })
            execute.assert_not_called()
            # The launcher checks schema during assembly; independently prove
            # that bypassing that assembly cannot bypass the callee's check.
            with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
                self.case.consume()
            self.assertEqual(caught.exception.reason_code, "launch_go_receipt_invalid")
            self.assertEqual(str(caught.exception), detail)
            # Bytes/digest authentication must still precede the class check.
            self.case.inputs["go_receipt_sha256"] = "0" * 64
            with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
                self.case.consume()
            self.assertEqual(caught.exception.reason_code, "launch_go_receipt_invalid")
            self.assertIn("sha256", str(caught.exception))
            self.assertNotIn("class=", str(caught.exception))
            self.assertEqual(list(self.fixture.custody.rglob("*.consumed.json")), [])
            self.assertEqual(
                {path: path.read_bytes() for path in rehearsal_root.rglob("*.consumed.json")},
                rehearsal_consumptions,
            )
            for custody in (self.fixture.custody, rehearsal_root):
                self.assertEqual(list(custody.rglob("chain.started")), [])


if __name__ == "__main__":
    unittest.main()
