from __future__ import annotations

import argparse
import importlib.util
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
from tests.test_arm_readiness import LaunchConsumptionV2Tests


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "launch_window_script", ROOT / "scripts/launch_window.py"
)
assert SPEC is not None and SPEC.loader is not None
launch_window = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launch_window)


class LaunchWindowEntrypointTests(unittest.TestCase):
    def _args(self, root: Path) -> argparse.Namespace:
        return argparse.Namespace(
            pack_root=root / "pack",
            arm_receipt=root / "arm-0001.json",
            arm_readiness_custody_root=root / "custody",
            launch_manifest=root / "launch-manifest.json",
            lifecycle_event=None,
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
            try:
                os.close(launch_window.HANDOFF_FD)
            except OSError:
                pass
            with mock.patch.object(
                launch_window, "_consumption_path", return_value=Path("/tmp/c.json")
            ), mock.patch.object(
                launch_window, "verify_consumed_launch", return_value={"status": "PASS"}
            ):
                with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
                    launch_window.lifecycle(args)
            self.assertEqual(caught.exception.reason_code, "launch_handoff_invalid")

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
                },
            )

    def test_launch_assembles_and_passes_reauthenticated_file_context(self) -> None:
        fixture = LaunchConsumptionV2Tests(
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
            ), mock.patch.object(
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
