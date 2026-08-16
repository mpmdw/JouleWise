from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import joulewise.arm_readiness as readiness
from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID, sample_arm


class LaunchConsumptionV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.pack = root / "pack-v2"
        self.pack.mkdir()
        self.custody = root / "arm-custody"
        self.arm = sample_arm(root / "context")
        self.arm["boot_session_id"] = TEST_BOOT_SESSION_ID
        self.arm["pack"]["pack_root"] = str(self.pack)
        pack_record_patch = mock.patch.object(
            readiness, "_pack_record", return_value=self.arm["pack"]
        )
        pack_record_patch.start()
        self.addCleanup(pack_record_patch.stop)
        for name in (
            "claim_runs_root",
            "bound_runs_root",
            "custody_root",
            "quarantine_root",
            "claim_backup_destination",
            "bound_backup_destination",
        ):
            Path(self.arm["arm_context"][name]).mkdir(parents=True)
        Path(self.arm["arm_context"]["waiver_path"]).write_bytes(
            readiness.render_json([])
        )
        namespace = self.custody / self.pack.name / "arm_readiness.receipts"
        namespace.mkdir(parents=True)
        self.arm_path = namespace / "arm-0001.json"
        arm_raw = readiness.render_json(self.arm)
        self.arm_path.write_bytes(arm_raw)
        self.arm_path.with_name(f"{self.arm_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(arm_raw).hexdigest(), self.arm_path.name
            )
        )
        self.window_root = root / "window-plan"
        self.window_root.mkdir()
        (self.window_root / "window.env").write_text("PACK_ROOT=/tmp/pack\n")
        self.chain_path = self.window_root / "window-chain.zsh"
        self.chain_path.write_text("#!/bin/zsh\nexit 0\n")
        self.exec_argv = [
            "/usr/bin/caffeinate",
            "-is",
            "/bin/zsh",
            str(self.chain_path),
            str(self.window_root),
        ]
        self.manifest_path = root / "launch-manifest.json"
        self.manifest_path.write_bytes(
            readiness.render_json(
                {
                    "schema_version": readiness.LAUNCH_MANIFEST_SCHEMA,
                    "boot_session_id": TEST_BOOT_SESSION_ID,
                    "window_plan_root": str(self.window_root),
                    "prewindow_command": ["/bin/true"],
                    "launch_command": self.exec_argv,
                }
            )
        )

    def _consumer_inputs(self, token: bytes = b"t" * 32) -> dict[str, object]:
        arm_raw = self.arm_path.read_bytes()
        manifest_raw = self.manifest_path.read_bytes()
        return {
            "pack_root": self.pack,
            "arm_receipt": self.arm_path,
            "authenticated_arm_receipt": copy.deepcopy(self.arm),
            "arm_receipt_sha256": hashlib.sha256(arm_raw).hexdigest(),
            "window_custody_root": self.custody,
            "launch_manifest": self.manifest_path,
            "authenticated_launch_manifest": readiness.parse_json_bytes(
                manifest_raw, require_canonical=True
            ),
            "launch_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "window_plan_root": self.window_root,
            "window_environment_sha256": hashlib.sha256(
                (self.window_root / "window.env").read_bytes()
            ).hexdigest(),
            "window_chain_sha256": hashlib.sha256(
                self.chain_path.read_bytes()
            ).hexdigest(),
            "exec_argv": self.exec_argv,
            "handoff_token_sha256": hashlib.sha256(token).hexdigest(),
        }

    def _consume(
        self, token: bytes = b"t" * 32, **overrides: object
    ) -> dict[str, object]:
        inputs = self._consumer_inputs(token)
        inputs.update(overrides)
        arm_digest = hashlib.sha256(self.arm_path.read_bytes()).hexdigest()
        with mock.patch.object(
            readiness,
            "_verify_arm_receipt",
            return_value={
                "status": "PASS",
                "arm_disposition": "GO",
                "receipt_path": str(self.arm_path.resolve()),
                "receipt_sha256": arm_digest,
                "pack_sha256": self.arm["pack"]["pack_sha256"],
            },
        ), mock.patch.object(
            readiness, "reviewed_main", return_value=self.arm["reviewed_main"]
        ), mock.patch.object(
            readiness, "_root_policy_refusals", return_value=([], set())
        ):
            return readiness._consume_launch_capability(**inputs)

    def _settle(self, token: bytes = b"l" * 32) -> tuple[Path, dict[str, object]]:
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            settled = readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "settle"
            )
        return consumption_path, settled

    def _authenticate_campaign(
        self, runs_root: Path, *, config_paths: tuple[Path, ...] = ()
    ) -> dict[str, object]:
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ), mock.patch.object(
            readiness,
            "_git_text",
            return_value=self.arm["reviewed_main"]["head_commit"],
        ), mock.patch.object(
            readiness,
            "_authenticated_pack_config_inventory",
            return_value={
                path.resolve().relative_to(self.pack.resolve()).as_posix():
                hashlib.sha256(path.read_bytes()).hexdigest()
                for path in config_paths
                if path.resolve().is_relative_to(self.pack.resolve())
            },
        ):
            return readiness.authenticate_campaign_launch_lineage(
                runs_root, config_paths=config_paths
            )

    def test_v2_claim_is_fsynced_and_replays_from_consumption(self) -> None:
        with mock.patch.object(
            readiness, "_fsync_directory", wraps=readiness._fsync_directory
        ) as fsync_directory:
            result = self._consume()
        self.assertEqual(fsync_directory.call_count, 3)
        consumption_path = Path(str(result["consumption_path"]))
        consumption = readiness.validate_consumption_receipt(
            readiness.parse_json_bytes(
                consumption_path.read_bytes(), require_canonical=True
            )
        )
        self.assertEqual(
            consumption["schema_version"], readiness.CONSUMPTION_RECEIPT_SCHEMA
        )
        self.assertEqual(consumption["exec_argv"], self.exec_argv)
        self.assertEqual(
            consumption["arm_context_sha256"],
            hashlib.sha256(
                readiness.render_json(self.arm["arm_context"])
            ).hexdigest(),
        )
        with mock.patch.object(
            readiness, "_pack_record", return_value=self.arm["pack"]
        ), mock.patch.object(
            readiness,
            "_derive_arm_semantics_for_verification",
            return_value=(self.arm["rows"], self.arm["refusals"]),
        ), mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            verified = readiness.verify_consumed_launch(
                self.pack,
                consumption_path,
                launch_manifest=self.manifest_path,
                expected_exec_argv=self.exec_argv,
            )
        self.assertEqual(verified["status"], "PASS")
        self.assertEqual(verified["consumption_sha256"], result["consumption_sha256"])

    def test_start_settle_completion_form_one_authenticated_lineage(self) -> None:
        token = b"h" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "settle"
            )
            completed = readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "completion"
            )
        lineage = readiness.authenticate_launch_lineage(
            completed["launch_lineage"], require_completion=True
        )
        self.assertEqual(lineage["consumption_sha256"], result["consumption_sha256"])
        self.assertIsNotNone(lineage["completion_sha256"])

    def test_settle_publishes_both_canonical_no_clobber_locators(self) -> None:
        with mock.patch.object(
            readiness, "_fsync_directory", wraps=readiness._fsync_directory
        ) as fsync_directory:
            _consumption_path, settled = self._settle()
        for role in ("claim_runs_root", "bound_runs_root"):
            root = Path(self.arm["arm_context"][role])
            locator_path = root / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
            raw = locator_path.read_bytes()
            locator = readiness.parse_json_bytes(raw, require_canonical=True)
            self.assertEqual(
                set(locator), readiness.LAUNCH_LINEAGE_LOCATOR_KEYS
            )
            self.assertEqual(
                locator["schema_version"],
                readiness.LAUNCH_LINEAGE_LOCATOR_SCHEMA,
            )
            self.assertEqual(locator["root_role"], role)
            self.assertEqual(locator["root_path"], str(root.resolve()))
            self.assertEqual(locator["launch_lineage"], settled["launch_lineage"])
            self.assertIsNone(locator["launch_lineage"]["completion"])
            self.assertEqual(
                locator_path.with_name(f"{locator_path.name}.sha256").read_bytes(),
                readiness.gnu_sidecar(
                    hashlib.sha256(raw).hexdigest(), locator_path.name
                ),
            )
            self.assertEqual(
                sum(
                    Path(call.args[0]).resolve() == root.resolve()
                    for call in fsync_directory.call_args_list
                ),
                2,
            )
        authenticated = self._authenticate_campaign(
            Path(self.arm["arm_context"]["claim_runs_root"])
        )
        self.assertEqual(
            readiness.render_json(authenticated["launch_lineage"]),
            readiness.render_json(settled["launch_lineage"]),
        )
        selected_locator = (
            Path(self.arm["arm_context"]["claim_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        self.assertEqual(
            authenticated["locator_sha256"],
            hashlib.sha256(selected_locator.read_bytes()).hexdigest(),
        )

    def test_lineage_replay_derives_pack_root_and_rejects_caller_mismatch(self) -> None:
        _consumption_path, settled = self._settle()
        replay = readiness.authenticate_launch_lineage(
            settled["launch_lineage"], require_completion=False
        )
        self.assertEqual(replay["pack_root"], str(self.pack.resolve()))
        other = Path(self.temporary.name) / "other-pack"
        other.mkdir()
        with self.assertRaises(readiness.LaunchLineageError) as caught:
            readiness.authenticate_launch_lineage(
                settled["launch_lineage"],
                require_completion=False,
                expected_pack_root=other,
            )
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    def test_partial_locator_publication_burns_and_cannot_be_repaired(self) -> None:
        token = b"p" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        bound_locator = (
            Path(self.arm["arm_context"]["bound_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        real_write = readiness._exclusive_write

        def fail_bound_primary(path: Path, raw: bytes) -> None:
            if path.resolve(strict=False) == bound_locator.resolve(strict=False):
                raise readiness.ArmReadinessError(
                    "readiness_io_error", "injected bound-locator crash"
                )
            real_write(path, raw)

        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            with mock.patch.object(
                readiness, "_exclusive_write", side_effect=fail_bound_primary
            ):
                with self.assertRaises(readiness.LaunchLineageError) as caught:
                    readiness.record_launch_lifecycle_event(
                        self.pack, consumption_path, "settle"
                    )
            self.assertEqual(
                caught.exception.reason_code, "launch_consumption_invalid"
            )
            claim_locator = (
                Path(self.arm["arm_context"]["claim_runs_root"])
                / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
            )
            self.assertTrue(claim_locator.is_file())
            self.assertTrue(
                claim_locator.with_name(f"{claim_locator.name}.sha256").is_file()
            )
            self.assertFalse(bound_locator.exists())
            with self.assertRaises(readiness.LaunchLineageError) as replay:
                readiness.record_launch_lifecycle_event(
                    self.pack, consumption_path, "settle"
                )
        self.assertEqual(
            replay.exception.reason_code, "launch_consumption_invalid"
        )

    def test_precreated_locator_burns_settle_without_publishing_sibling(self) -> None:
        token = b"o" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        claim_locator = (
            Path(self.arm["arm_context"]["claim_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        claim_locator.write_text("precreated\n")
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            with self.assertRaises(readiness.LaunchLineageError) as caught:
                readiness.record_launch_lifecycle_event(
                    self.pack, consumption_path, "settle"
                )
        self.assertEqual(caught.exception.reason_code, "launch_consumption_invalid")
        bound_locator = (
            Path(self.arm["arm_context"]["bound_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        self.assertFalse(bound_locator.exists())
        claim_locator.unlink()
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            with self.assertRaises(readiness.LaunchLineageError) as replay:
                readiness.record_launch_lifecycle_event(
                    self.pack, consumption_path, "settle"
                )
        self.assertEqual(
            replay.exception.reason_code, "launch_consumption_invalid"
        )
        self.assertFalse(bound_locator.exists())

    def test_locator_missing_corrupt_root_swap_and_mixed_are_discriminated(self) -> None:
        self._settle()
        claim = (
            Path(self.arm["arm_context"]["claim_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        bound = (
            Path(self.arm["arm_context"]["bound_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        paths = (
            claim,
            claim.with_name(f"{claim.name}.sha256"),
            bound,
            bound.with_name(f"{bound.name}.sha256"),
        )
        original = {path: path.read_bytes() for path in paths}

        claim.with_name(f"{claim.name}.sha256").unlink()
        with self.assertRaises(readiness.LaunchLineageError) as missing:
            self._authenticate_campaign(claim.parent)
        self.assertEqual(missing.exception.reason_code, "launch_consumption_missing")
        for path, raw in original.items():
            path.write_bytes(raw)

        claim.write_bytes(original[claim] + b" ")
        with self.assertRaises(readiness.LaunchLineageError) as corrupt_primary:
            self._authenticate_campaign(claim.parent)
        self.assertEqual(
            corrupt_primary.exception.reason_code, "launch_consumption_invalid"
        )
        for path, raw in original.items():
            path.write_bytes(raw)

        claim.with_name(f"{claim.name}.sha256").write_text("corrupt\n")
        with self.assertRaises(readiness.LaunchLineageError) as corrupt_sidecar:
            self._authenticate_campaign(claim.parent)
        self.assertEqual(
            corrupt_sidecar.exception.reason_code, "launch_consumption_invalid"
        )
        for path, raw in original.items():
            path.write_bytes(raw)

        claim.write_bytes(original[bound])
        claim.with_name(f"{claim.name}.sha256").write_bytes(
            original[bound.with_name(f"{bound.name}.sha256")]
        )
        bound.write_bytes(original[claim])
        bound.with_name(f"{bound.name}.sha256").write_bytes(
            original[claim.with_name(f"{claim.name}.sha256")]
        )
        with self.assertRaises(readiness.LaunchLineageError) as swapped:
            self._authenticate_campaign(claim.parent)
        self.assertEqual(swapped.exception.reason_code, "launch_binding_mismatch")
        for path, raw in original.items():
            path.write_bytes(raw)

        second = LaunchConsumptionV2Tests(
            methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
        )
        second.setUp()
        try:
            second._settle()
            second_bound_path = (
                Path(second.arm["arm_context"]["bound_runs_root"])
                / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
            )
            second_locator = readiness.parse_json_bytes(
                second_bound_path.read_bytes(), require_canonical=True
            )
        finally:
            second.doCleanups()
        mixed = json.loads(original[bound])
        mixed["launch_lineage"] = second_locator["launch_lineage"]
        mixed_raw = readiness.render_json(mixed)
        bound.write_bytes(mixed_raw)
        bound.with_name(f"{bound.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(mixed_raw).hexdigest(), bound.name
            )
        )
        with self.assertRaises(readiness.LaunchLineageError) as conflict:
            self._authenticate_campaign(claim.parent)
        self.assertEqual(conflict.exception.reason_code, "launch_lineage_conflict")

    def test_public_consumption_name_is_absent(self) -> None:
        self.assertNotIn("consume_launch_capability", readiness.__all__)
        with self.assertRaises(AttributeError):
            getattr(readiness, "consume_launch_capability")
        with self.assertRaises(ImportError):
            exec(
                "from joulewise.arm_readiness import consume_launch_capability",
                {},
            )

    def test_private_complete_context_consumes_once_at_atomic_primary(self) -> None:
        self._consume()
        with mock.patch.object(
            readiness, "_exclusive_write", wraps=readiness._exclusive_write
        ) as exclusive_write:
            with self.assertRaises(readiness.ArmReadinessError) as replay:
                self._consume()
        self.assertEqual(
            replay.exception.reason_code, "readiness_record_consumed"
        )
        exclusive_write.assert_called_once()

    def test_private_consumer_requires_complete_matching_context_before_write(
        self,
    ) -> None:
        other_window_root = Path(self.temporary.name) / "other-window"
        other_window_root.mkdir()
        cases = {
            "missing_arm": {"authenticated_arm_receipt": None},
            "missing_manifest": {"authenticated_launch_manifest": None},
            "missing_window_root": {"window_plan_root": None},
            "arm_digest": {"arm_receipt_sha256": "0" * 64},
            "manifest_digest": {"launch_manifest_sha256": "0" * 64},
            "window_root": {"window_plan_root": other_window_root},
            "environment_digest": {"window_environment_sha256": "0" * 64},
            "chain_digest": {"window_chain_sha256": "0" * 64},
            "exec_argv": {"exec_argv": ["/bin/false"]},
        }
        consumption_dir = (
            self.custody / self.pack.name / "arm_readiness.consumptions"
        )
        for name, overrides in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(readiness.ArmReadinessError) as caught:
                    self._consume(**overrides)
                self.assertIn(
                    caught.exception.reason_code, readiness.READINESS_REASON_CODES
                )
                self.assertFalse(consumption_dir.exists())

        with self.assertRaises(TypeError):
            readiness._consume_launch_capability(
                self.pack,
                self.arm_path,
                self.custody,
            )
        self.assertFalse(consumption_dir.exists())

    def test_campaign_config_membership_and_completion_absence_are_enforced(self) -> None:
        consumption_path, _settled = self._settle()
        config_path = self.pack / "member.json"
        config_path.write_text('{"run_id":"member"}\n')
        authenticated = self._authenticate_campaign(
            Path(self.arm["arm_context"]["claim_runs_root"]),
            config_paths=(config_path,),
        )
        self.assertEqual(authenticated["pack_root"], str(self.pack.resolve()))
        copied = Path(self.temporary.name) / "copied-member.json"
        copied.write_bytes(config_path.read_bytes())
        with self.assertRaises(readiness.LaunchLineageError) as outside:
            self._authenticate_campaign(
                Path(self.arm["arm_context"]["claim_runs_root"]),
                config_paths=(copied,),
            )
        self.assertEqual(outside.exception.reason_code, "launch_binding_mismatch")
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "completion"
            )
        with self.assertRaises(readiness.LaunchLineageError) as completed:
            self._authenticate_campaign(
                Path(self.arm["arm_context"]["claim_runs_root"]),
                config_paths=(config_path,),
            )
        self.assertEqual(completed.exception.reason_code, "launch_binding_mismatch")

    def test_writer_auth_does_not_reapply_short_arm_expiration(self) -> None:
        self.arm["valid_until_monotonic_ns"] = 200
        arm_raw = readiness.render_json(self.arm)
        self.arm_path.write_bytes(arm_raw)
        self.arm_path.with_name(f"{self.arm_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(arm_raw).hexdigest(), self.arm_path.name
            )
        )
        token = b"e" * 32
        with mock.patch.object(readiness.time, "monotonic_ns", return_value=100):
            result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ), mock.patch.object(
            readiness.time, "monotonic_ns", side_effect=(110, 120)
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "settle"
            )
        with mock.patch.object(readiness.time, "monotonic_ns", return_value=10_000):
            authenticated = self._authenticate_campaign(
                Path(self.arm["arm_context"]["claim_runs_root"])
            )
        self.assertEqual(authenticated["authentication"]["consumption_sha256"], result["consumption_sha256"])

    def test_missing_consumption_sidecar_is_machine_refusal(self) -> None:
        result = self._consume()
        consumption_path = Path(str(result["consumption_path"]))
        consumption_path.with_name(f"{consumption_path.name}.sha256").unlink()
        with self.assertRaises(readiness.LaunchLineageError) as caught:
            readiness.authenticate_launch_lineage(
                {
                    "schema_version": readiness.LAUNCH_LINEAGE_SCHEMA,
                    "collection_boot_session_id": TEST_BOOT_SESSION_ID,
                    "pack_id": self.arm["pack"]["pack_id"],
                    "plan_id": self.arm["pack"]["plan_id"],
                    "window_id": self.arm["pack"]["window_id"],
                    "bracket_session_id": self.arm["arm_context"]["bracket_session_id"],
                    "consumption": {
                        "path": str(consumption_path),
                        "sha256": str(result["consumption_sha256"]),
                    },
                    "start": None,
                    "settle": None,
                    "completion": None,
                },
                require_completion=False,
            )
        self.assertEqual(caught.exception.reason_code, "launch_consumption_missing")

    def test_primary_remains_burned_when_post_claim_directory_fsync_fails(self) -> None:
        failure = arm_readiness_error = readiness.ArmReadinessError(
            "readiness_io_error", "injected post-claim fsync failure"
        )
        with mock.patch.object(
            readiness,
            "_fsync_directory",
            side_effect=[None, failure],
        ):
            with self.assertRaises(readiness.ArmReadinessError) as caught:
                self._consume()
        self.assertIs(caught.exception, arm_readiness_error)
        consumption_path = (
            self.custody
            / self.pack.name
            / "arm_readiness.consumptions"
            / "arm-0001.consumed.json"
        )
        self.assertTrue(consumption_path.is_file())
        self.assertFalse(
            consumption_path.with_name(f"{consumption_path.name}.sha256").exists()
        )
        with self.assertRaises(readiness.ArmReadinessError) as replay:
            self._consume()
        self.assertEqual(replay.exception.reason_code, "readiness_record_consumed")

    def test_primary_remains_burned_when_sidecar_publication_fails(self) -> None:
        real_write = readiness._exclusive_write
        calls = 0

        def injected(path: Path, raw: bytes) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise readiness.ArmReadinessError(
                    "readiness_io_error", "injected sidecar failure"
                )
            real_write(path, raw)

        with mock.patch.object(readiness, "_exclusive_write", side_effect=injected):
            with self.assertRaises(readiness.ArmReadinessError):
                self._consume()
        consumption_path = (
            self.custody
            / self.pack.name
            / "arm_readiness.consumptions"
            / "arm-0001.consumed.json"
        )
        self.assertTrue(consumption_path.is_file())
        with self.assertRaises(readiness.ArmReadinessError) as replay:
            self._consume()
        self.assertEqual(replay.exception.reason_code, "readiness_record_consumed")

    def test_completed_sidecar_remains_burned_when_final_fsync_fails(self) -> None:
        failure = readiness.ArmReadinessError(
            "readiness_io_error", "injected final directory fsync failure"
        )
        with mock.patch.object(
            readiness,
            "_fsync_directory",
            side_effect=[None, None, failure],
        ):
            with self.assertRaises(readiness.ArmReadinessError) as caught:
                self._consume()
        self.assertIs(caught.exception, failure)
        consumption_path = (
            self.custody
            / self.pack.name
            / "arm_readiness.consumptions"
            / "arm-0001.consumed.json"
        )
        self.assertTrue(consumption_path.is_file())
        self.assertTrue(
            consumption_path.with_name(f"{consumption_path.name}.sha256").is_file()
        )
        with self.assertRaises(readiness.ArmReadinessError) as replay:
            self._consume()
        self.assertEqual(replay.exception.reason_code, "readiness_record_consumed")

    def test_chain_death_after_start_is_lifecycle_incomplete(self) -> None:
        token = b"d" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            started = readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
        with self.assertRaises(readiness.LaunchLineageError) as incomplete:
            readiness.authenticate_launch_lineage(
                started["launch_lineage"], require_completion=False
            )
        self.assertEqual(
            incomplete.exception.reason_code, "launch_lifecycle_incomplete"
        )

    def test_missing_completion_and_identity_mismatch_are_discriminated(self) -> None:
        token = b"q" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            settled = readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "settle"
            )
        with self.assertRaises(readiness.LaunchLineageError) as incomplete:
            readiness.authenticate_launch_lineage(
                settled["launch_lineage"], require_completion=True
            )
        self.assertEqual(
            incomplete.exception.reason_code, "launch_lifecycle_incomplete"
        )
        mismatched = dict(settled["launch_lineage"])
        mismatched["pack_id"] = "another-pack"
        with self.assertRaises(readiness.LaunchLineageError) as mismatch:
            readiness.authenticate_launch_lineage(
                mismatched, require_completion=False
            )
        self.assertEqual(mismatch.exception.reason_code, "launch_binding_mismatch")

    def test_later_arm_successor_does_not_destroy_historical_lineage(self) -> None:
        token = b"s" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "settle"
            )
            completed = readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "completion"
            )

        original_raw = self.arm_path.read_bytes()
        successor = copy.deepcopy(self.arm)
        successor["receipt_id"] = "arm-0002"
        successor["supersedes"] = {
            "receipt_id": self.arm["receipt_id"],
            "receipt_path": f"arm_readiness.receipts/{self.arm_path.name}",
            "receipt_sha256": hashlib.sha256(original_raw).hexdigest(),
            "pack_id": self.arm["pack"]["pack_id"],
            "pack_sha256": self.arm["pack"]["pack_sha256"],
        }
        successor_path = self.arm_path.with_name("arm-0002.json")
        successor_raw = readiness.render_json(successor)
        successor_path.write_bytes(successor_raw)
        successor_path.with_name(f"{successor_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(successor_raw).hexdigest(), successor_path.name
            )
        )

        historical = readiness.authenticate_launch_lineage(
            completed["launch_lineage"], require_completion=True
        )
        self.assertEqual(
            historical["consumption_sha256"], result["consumption_sha256"]
        )
        with mock.patch.object(
            readiness, "_pack_record", return_value=self.arm["pack"]
        ), mock.patch.object(
            readiness,
            "_derive_arm_semantics_for_verification",
            return_value=(self.arm["rows"], self.arm["refusals"]),
        ), mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            with self.assertRaises(readiness.LaunchLineageError) as launch_entry:
                readiness.verify_consumed_launch(self.pack, consumption_path)
        self.assertEqual(
            launch_entry.exception.reason_code, "launch_binding_mismatch"
        )


class LaunchPackConfigInventoryTests(unittest.TestCase):
    def test_real_pack_inventory_authenticates_exact_member_bytes(self) -> None:
        pack = (
            Path(__file__).resolve().parents[1]
            / "configs/campaigns/d117_floor_qwen25_1p5b_v1"
        )
        inventory = readiness._authenticated_pack_config_inventory(pack)
        relative = "01_phase_decode_absolute/d117f15-df-ph-decode-abs-r01.json"
        self.assertEqual(
            inventory[relative],
            hashlib.sha256((pack / relative).read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
