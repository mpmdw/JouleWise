from __future__ import annotations

import copy
import hashlib
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

    def _consume(self, token: bytes = b"t" * 32) -> dict[str, object]:
        with mock.patch.object(
            readiness,
            "verify_arm_receipt",
            return_value={"pack_sha256": self.arm["pack"]["pack_sha256"]},
        ), mock.patch.object(
            readiness, "reviewed_main", return_value=self.arm["reviewed_main"]
        ), mock.patch.object(
            readiness, "_root_policy_refusals", return_value=([], set())
        ):
            return readiness.consume_launch_capability(
                self.pack,
                self.arm_path,
                self.custody,
                launch_manifest=self.manifest_path,
                exec_argv=self.exec_argv,
                handoff_token_sha256=hashlib.sha256(token).hexdigest(),
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


if __name__ == "__main__":
    unittest.main()
