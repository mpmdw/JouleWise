from __future__ import annotations

import copy
import errno
import fcntl
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/reauthor_clean.py"
SPEC = importlib.util.spec_from_file_location("reauthor_clean", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
reauthor_clean = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reauthor_clean)

DARWIN_FLAGS = (
    sys.platform == "darwin"
    and hasattr(os.stat("."), "st_flags")
    and getattr(stat, "UF_IMMUTABLE", None) is not None
)


class SimulatedCrash(RuntimeError):
    pass


class ReauthorCleanTests(unittest.TestCase):
    maxDiff = None

    def _git(self, repository: Path, *args: str) -> None:
        subprocess.run(
            ("git", "-C", str(repository), *args),
            check=True,
            capture_output=True,
        )

    def _clear_flags(self, root: Path) -> None:
        if not hasattr(os, "chflags") or not root.exists():
            return
        paths: list[Path] = []
        for current, directories, files in os.walk(root, topdown=False):
            paths.extend(Path(current) / name for name in files)
            paths.extend(Path(current) / name for name in directories)
        paths.append(root)
        for path in paths:
            try:
                if not path.is_symlink():
                    os.chflags(path, 0, follow_symlinks=False)
            except (FileNotFoundError, OSError):
                pass

    def _delete_tree(self, root: Path) -> None:
        self._clear_flags(root)
        for current, directories, files in os.walk(root, topdown=False):
            current_path = Path(current)
            for name in files:
                (current_path / name).unlink()
            for name in directories:
                (current_path / name).rmdir()
        root.rmdir()

    def _fixture(self, *, frozen: bool = False):
        temporary = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        temporary_root = Path(temporary.name).resolve()

        def cleanup() -> None:
            self._clear_flags(temporary_root)
            temporary.cleanup()

        self.addCleanup(cleanup)
        repository = temporary_root / "repo"
        repository.mkdir()
        self._git(repository, "init", "-q")
        self._git(repository, "config", "user.email", "tests@example.invalid")
        self._git(repository, "config", "user.name", "JouleWise Tests")
        pack = repository / "configs/campaigns/test_campaign_v4"
        pack.mkdir(parents=True)
        tree = {
            "plan": {"plan_id": "plan-test-v4", "path": "calibration_plan.json"},
            "window_identity": {"window_id": "window-test-v4"},
            "arm_attachments": {"arm_readiness": {"freeze_receipt": None}},
        }
        plan_raw = (
            json.dumps(tree, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode()
        (pack / "plan_tree.json").write_bytes(plan_raw)
        (pack / "plan_tree.sha256").write_text(
            f"{hashlib.sha256(plan_raw).hexdigest()}  plan_tree.json\n",
            encoding="ascii",
        )
        if frozen:
            self._add_freeze(pack)
        self._git(repository, "add", ".")
        self._git(repository, "commit", "-qm", "fixture")

        custody_pack = temporary_root / "custody" / pack.name
        custody_pack.mkdir(parents=True)
        targets = []
        for index, name in enumerate(sorted(reauthor_clean.EXPECTED_NAMESPACES)):
            target = custody_pack / name
            (target / "nested").mkdir(parents=True)
            (target / "nested" / f"item-{index}.txt").write_text(
                f"evidence {index}\n", encoding="utf-8"
            )
            targets.append(target)
        untouched = custody_pack / "arm_readiness.freeze.receipts"
        untouched.mkdir()
        (untouched / "sentinel.txt").write_text("preserve\n", encoding="utf-8")
        outside = custody_pack.parent / "outside.txt"
        outside.write_text("preserve\n", encoding="utf-8")
        return repository, pack, custody_pack, targets, untouched, outside

    def _add_freeze(self, pack: Path) -> None:
        namespace = pack / "arm_readiness.freeze.receipts"
        namespace.mkdir(exist_ok=True)
        raw = b'{"receipt_id":"freeze-0004"}\n'
        (namespace / "freeze-0004.json").write_bytes(raw)
        (namespace / "freeze-0004.json.sha256").write_text(
            f"{hashlib.sha256(raw).hexdigest()}  freeze-0004.json\n",
            encoding="ascii",
        )

    def _assert_refusal(self, reason: str, pack: Path, targets: list[Path]) -> None:
        with self.assertRaises(reauthor_clean.ReauthorCleanError) as caught:
            reauthor_clean.clean(pack, targets)
        self.assertEqual(caught.exception.reason_code, reason)

    def _crash(self, pack: Path, targets: list[Path], point: str) -> None:
        hit = False

        def injector(observed: str) -> None:
            nonlocal hit
            if not hit and observed == point:
                hit = True
                raise SimulatedCrash(point)

        with mock.patch.object(reauthor_clean, "_FAULT_INJECTOR", injector):
            with self.assertRaisesRegex(SimulatedCrash, reauthor_clean.re.escape(point)):
                reauthor_clean.clean(pack, targets)
        self.assertTrue(hit, f"fault point was not reached: {point}")

    def _crash_after_manifest(self, pack: Path, targets: list[Path]) -> dict[str, object]:
        self._crash(pack, targets, "after_manifest_directory_fsync")
        operation_root = targets[0].parent / reauthor_clean.OPERATION_DIRECTORY
        paths = list(operation_root.glob("state-*.manifest.json"))
        self.assertEqual(len(paths), 1)
        return json.loads(paths[0].read_bytes())

    def _resume(self, pack: Path, targets: list[Path]):
        return reauthor_clean.clean(pack, targets, resume_removal=True)

    def _rewrite_artifact(self, path: Path, value: object) -> None:
        if hasattr(os, "chflags"):
            os.chflags(path, 0, follow_symlinks=False)
        path.write_bytes(reauthor_clean._render_json(value))

    def test_refuses_wrong_shape_non_pack_partial_set_and_symlink_ancestry(self) -> None:
        repository, pack, custody, targets, _untouched, _outside = self._fixture()
        targets[0].rename(targets[0].with_suffix(".saved"))
        targets[0].write_text("not a directory\n", encoding="utf-8")
        self._assert_refusal("reauthor_clean_namespace_shape_invalid", pack, targets)

        wrong = repository / "not-a-pack/test_campaign_v4"
        wrong.mkdir(parents=True)
        self._assert_refusal("reauthor_clean_pack_root_invalid", wrong, targets)
        self._assert_refusal("reauthor_clean_namespace_set_invalid", pack, targets[:-1])

        alias = repository.parent / "custody-alias"
        alias.symlink_to(custody.parent, target_is_directory=True)
        alias_targets = [alias / custody.name / target.name for target in targets]
        self._assert_refusal(
            "reauthor_clean_namespace_shape_invalid", pack, alias_targets
        )

    def test_frozen_pack_refuses_before_target_inspection(self) -> None:
        _repository, pack, _custody, targets, _untouched, _outside = self._fixture(
            frozen=True
        )
        targets[0].rename(targets[0].with_suffix(".missing"))
        self._assert_refusal("reauthor_clean_frozen_pack", pack, targets)

    def test_cli_usage_refusal_is_structured(self) -> None:
        completed = subprocess.run(
            (sys.executable, str(SCRIPT)), check=False, capture_output=True, text=True
        )
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(
            json.loads(completed.stdout)["reason_codes"],
            ["reauthor_clean_usage_invalid"],
        )
        self.assertEqual(completed.stderr, "")

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_capability_sentinel_proves_postunlink_and_cleans_up(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            reauthor_clean._capability_sentinel(root, "a" * 64)
            self.assertEqual(list(root.iterdir()), [])

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_success_is_manifested_fd_unlink_verified_and_idempotent(self) -> None:
        _repository, pack, custody, targets, untouched, outside = self._fixture()
        captured_final: dict[str, str] = {}
        original_payload = reauthor_clean._payload_record

        def capture(descriptor, relative, kind, **kwargs):
            payload = original_payload(descriptor, relative, kind, **kwargs)
            if kind == "file" and os.fstat(descriptor).st_nlink == 0:
                captured_final[relative] = reauthor_clean._sha256(
                    reauthor_clean._canonical_json(payload)
                )
            return payload

        with mock.patch.object(reauthor_clean, "_payload_record", side_effect=capture):
            outcome = reauthor_clean.clean(pack, reversed(targets))

        self.assertEqual(outcome["completion"], "COMPLETE")
        self.assertEqual(
            outcome["deletion_claim"], "VERIFIED LOGICAL NAMESPACE DELETION"
        )
        self.assertTrue(all(not target.exists() for target in targets))
        self.assertEqual((untouched / "sentinel.txt").read_text(), "preserve\n")
        self.assertEqual(outside.read_text(), "preserve\n")
        receipt_path = Path(outcome["receipt_path"])
        raw = receipt_path.read_bytes()
        receipt = json.loads(raw)
        self.assertEqual(receipt["schema_version"], reauthor_clean.RECEIPT_SCHEMA)
        self.assertEqual(receipt["status"], "COMPLETE_VERIFIED")
        self.assertEqual(
            receipt["deletion_semantics"],
            "logical_namespace_unlink_not_secure_erase",
        )
        self.assertEqual(
            receipt["truth_boundary"],
            "not secure erase and not hostile-process exclusion",
        )
        manifest_path = Path(receipt["state_manifest"]["path"])
        manifest_raw = manifest_path.read_bytes()
        manifest = json.loads(manifest_raw)
        self.assertEqual(manifest_raw, reauthor_clean._render_json(manifest))
        self.assertEqual(manifest["schema_version"], reauthor_clean.STATE_SCHEMA)
        self.assertEqual(manifest["protocol"], reauthor_clean.PROTOCOL)
        self.assertEqual(len(bytes.fromhex(manifest["nonce"])), 32)
        self.assertEqual(
            manifest["state_id"],
            reauthor_clean._derive_state_id(
                reauthor_clean._manifest_identity_core(manifest)
            ),
        )
        self.assertEqual(
            manifest_path.name, f"state-{manifest['state_id']}.manifest.json"
        )
        self.assertIn("pack_tree_git_oid", manifest["pack_identity"])
        self.assertEqual(len(manifest["sources"]), 3)
        self.assertTrue(
            all("st_gen" in item["root_anchor"] for item in manifest["sources"])
        )
        events = reauthor_clean._load_events(
            custody
            / reauthor_clean.OPERATION_DIRECTORY
            / f"state-{manifest['state_id']}.events",
            manifest["state_id"],
        )
        self.assertEqual(
            [event["sequence"] for event in events], list(range(1, len(events) + 1))
        )
        self.assertEqual(receipt["event_count"], len(events))
        self.assertEqual(
            receipt["event_chain_head_sha256"], events[-1]["event_sha256"]
        )
        file_rows = [
            row
            for row in receipt["destroyed_verified"]
            if row["path"] in captured_final
        ]
        self.assertEqual(len(file_rows), 3)
        for row in file_rows:
            self.assertEqual(
                row["final_held_fd_payload_sha256"], captured_final[row["path"]]
            )
            self.assertEqual(
                row["authorized_payload_sha256"], captured_final[row["path"]]
            )
        self.assertFalse(
            (custody / reauthor_clean.OPERATION_DIRECTORY / "operations.jsonl").exists()
        )
        self.assertNotIn("shutil", SCRIPT.read_text(encoding="utf-8"))

        repeated = reauthor_clean.clean(pack, targets)
        self.assertEqual(repeated["completion"], "ALREADY_COMPLETE")
        self.assertEqual(repeated["receipt_sha256"], outcome["receipt_sha256"])

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_terminal_replay_refuses_replaced_custody_root_binding(self) -> None:
        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        outcome = reauthor_clean.clean(pack, targets)
        self.assertEqual(outcome["completion"], "COMPLETE")

        original_anchor = reauthor_clean._anchor(custody.stat())
        operation_root = custody / reauthor_clean.OPERATION_DIRECTORY
        stashed_operation_root = custody.parent / "stashed-reauthor-clean-operations"
        operation_root.rename(stashed_operation_root)
        self._delete_tree(custody)
        custody.mkdir()
        self.assertNotEqual(reauthor_clean._anchor(custody.stat()), original_anchor)
        stashed_operation_root.rename(
            custody / reauthor_clean.OPERATION_DIRECTORY
        )

        recreated_targets = []
        for name in sorted(reauthor_clean.EXPECTED_NAMESPACES):
            target = custody / name
            target.mkdir()
            recreated_targets.append(target)

        with self.assertRaises(reauthor_clean.ReauthorCleanError) as caught:
            reauthor_clean.clean(pack, recreated_targets)
        self.assertEqual(
            caught.exception.reason_code,
            "reauthor_clean_state_binding_mismatch",
        )

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_same_timestamp_has_distinct_nonce_derived_state_ids(self) -> None:
        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        identity = reauthor_clean._authenticate_pack(pack)
        operation_root = custody / reauthor_clean.OPERATION_DIRECTORY
        operation_root.mkdir()
        instant = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)
        with mock.patch.object(reauthor_clean, "_utc_now", return_value=instant):
            first = reauthor_clean._build_manifest(
                identity, custody, operation_root, {item.name: item for item in targets}
            )
            second = reauthor_clean._build_manifest(
                identity, custody, operation_root, {item.name: item for item in targets}
            )
        self.assertNotEqual(first["nonce"], second["nonce"])
        self.assertNotEqual(first["state_id"], second["state_id"])

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_nonce_state_collision_refuses_before_rename(self) -> None:
        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        identity = reauthor_clean._authenticate_pack(pack)
        operation_root = custody / reauthor_clean.OPERATION_DIRECTORY
        operation_root.mkdir()
        target_map = {item.name: item for item in targets}
        with mock.patch.object(reauthor_clean.secrets, "token_bytes", return_value=b"x" * 32):
            manifest = reauthor_clean._build_manifest(
                identity, custody, operation_root, target_map
            )
            reauthor_clean._publish_no_clobber(
                reauthor_clean._manifest_path(operation_root, manifest["state_id"]),
                reauthor_clean._render_json(manifest),
            )
            with mock.patch.object(reauthor_clean, "_select_manifest", return_value=None), mock.patch.object(
                reauthor_clean.os, "rename", wraps=os.rename
            ) as rename:
                self._assert_refusal("reauthor_clean_output_collision", pack, targets)
        rename.assert_not_called()

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_platform_sentinel_failure_and_exdev_refuse_before_or_at_rename(self) -> None:
        _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
        with mock.patch.object(
            reauthor_clean,
            "_capability_sentinel",
            side_effect=reauthor_clean._refuse(
                "reauthor_clean_platform_capability_missing", "sentinel failed"
            ),
        ), mock.patch.object(reauthor_clean.os, "rename", wraps=os.rename) as rename:
            self._assert_refusal(
                "reauthor_clean_platform_capability_missing", pack, targets
            )
        rename.assert_not_called()
        self.assertTrue(all(target.exists() for target in targets))
        operation_root = targets[0].parent / reauthor_clean.OPERATION_DIRECTORY
        self.assertEqual(len(list(operation_root.glob("state-*.manifest.json"))), 1)

        _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
        with mock.patch.object(
            reauthor_clean.os, "rename", side_effect=OSError(errno.EXDEV, "cross-device")
        ):
            self._assert_refusal(
                "reauthor_clean_namespace_shape_invalid", pack, targets
            )
        self.assertTrue(all(target.exists() for target in targets))

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_complete_crash_matrix_and_each_persistence_boundary(self) -> None:
        names = sorted(reauthor_clean.EXPECTED_NAMESPACES)
        rename_points = [
            point
            for name in names
            for point in (
                f"before_rename_{name}",
                f"after_rename_{name}",
                f"before_source_parent_fsync_{name}",
                f"after_source_parent_fsync_{name}",
                f"before_quarantine_parent_fsync_{name}",
                f"after_quarantine_parent_fsync_{name}",
            )
        ]
        safe_resume_points = [
            "after_manifest_file_fsync",
            "before_manifest_directory_fsync",
            "after_manifest_directory_fsync",
            "before_event_prepared_create",
            "after_event_prepared_file_fsync",
            "before_event_prepared_directory_fsync",
            "after_event_prepared_directory_fsync",
            *rename_points,
            "after_event_rename_verified_file_fsync",
            "before_event_rename_verified_directory_fsync",
            "after_event_rename_verified_directory_fsync",
            "after_event_freeze_intent_file_fsync",
            "before_event_freeze_intent_directory_fsync",
            "after_event_freeze_intent_directory_fsync",
            "after_freeze_before_inventory",
            "after_inventory_file_fsync",
            "before_inventory_directory_fsync",
            "after_inventory_directory_fsync",
            "after_event_delete_authorized_file_fsync",
            "before_event_delete_authorized_directory_fsync",
            "after_event_delete_authorized_directory_fsync",
            "after_event_delete_intent_file_fsync",
            "before_event_delete_intent_directory_fsync",
            "after_event_delete_intent_directory_fsync",
        ]
        dynamic_safe_points = [
            "after_intent_before_thaw:",
            "after_thaw_before_unlink:",
            "before_unlink:",
        ]
        destroyed_unverified_points = [
            "after_unlink_before_parent_freeze:",
            "before_delete_parent_fsync:",
            "after_delete_parent_fsync:",
            "after_unlink_before_postunlink_freeze:",
            "after_postunlink_hash_before_event:",
            "before_event_delete_verified_create",
        ]
        verified_event_points = [
            "after_event_delete_verified_file_fsync",
            "before_event_delete_verified_directory_fsync",
            "after_event_delete_verified_directory_fsync",
        ]

        for point in ["before_manifest_create", *safe_resume_points]:
            with self.subTest(point=point):
                _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
                self._crash(pack, targets, point)
                outcome = (
                    reauthor_clean.clean(pack, targets)
                    if point == "before_manifest_create"
                    else self._resume(pack, targets)
                )
                self.assertEqual(outcome["completion"], "COMPLETE")

        for prefix in dynamic_safe_points:
            with self.subTest(point=prefix):
                _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
                observed: list[str] = []

                def crash_first(point: str) -> None:
                    if point.startswith(prefix) and not observed:
                        observed.append(point)
                        raise SimulatedCrash(point)

                with mock.patch.object(reauthor_clean, "_FAULT_INJECTOR", crash_first):
                    with self.assertRaises(SimulatedCrash):
                        reauthor_clean.clean(pack, targets)
                self.assertTrue(observed)
                self.assertEqual(self._resume(pack, targets)["completion"], "COMPLETE")

        for prefix in destroyed_unverified_points:
            with self.subTest(point=prefix):
                _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
                observed: list[str] = []

                def crash_first(point: str) -> None:
                    matches = point == prefix or point.startswith(prefix)
                    if matches and not observed:
                        observed.append(point)
                        raise SimulatedCrash(point)

                with mock.patch.object(reauthor_clean, "_FAULT_INJECTOR", crash_first):
                    with self.assertRaises(SimulatedCrash):
                        reauthor_clean.clean(pack, targets)
                with self.assertRaises(reauthor_clean.ReauthorCleanError) as caught:
                    self._resume(pack, targets)
                self.assertEqual(
                    caught.exception.reason_code,
                    "reauthor_clean_destroyed_unverified",
                )
                self.assertEqual(
                    caught.exception.outcome["completion"],
                    "INCOMPLETE_DESTROYED_UNVERIFIED",
                )
                first_hash = caught.exception.outcome["receipt_sha256"]
                with self.assertRaises(reauthor_clean.ReauthorCleanError) as repeated:
                    self._resume(pack, targets)
                self.assertEqual(repeated.exception.outcome["receipt_sha256"], first_hash)

        for point in verified_event_points:
            with self.subTest(point=point):
                _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
                self._crash(pack, targets, point)
                self.assertEqual(self._resume(pack, targets)["completion"], "COMPLETE")

        for point, expected in [
            ("before_terminal_receipt_create", "COMPLETE"),
            ("after_terminal_receipt_file_fsync", "ALREADY_COMPLETE"),
            ("before_terminal_receipt_directory_fsync", "ALREADY_COMPLETE"),
            ("after_terminal_receipt_directory_fsync", "ALREADY_COMPLETE"),
        ]:
            with self.subTest(point=point):
                _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
                self._crash(pack, targets, point)
                outcome = self._resume(pack, targets)
                self.assertEqual(outcome["completion"], expected)

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_post_freeze_and_thaw_mutation_attacks_fail_closed(self) -> None:
        _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
        victim = targets[0] / "nested" / "item-0.txt"

        def frozen_attack(point: str) -> None:
            if point == "after_freeze_before_inventory":
                with self.assertRaises(OSError):
                    victim.write_text("mutation\n", encoding="utf-8")

        with mock.patch.object(reauthor_clean, "_FAULT_INJECTOR", frozen_attack):
            self.assertEqual(reauthor_clean.clean(pack, targets)["completion"], "COMPLETE")

        _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
        writer = os.open(targets[0] / "nested" / "item-0.txt", os.O_WRONLY)
        self.addCleanup(os.close, writer)

        def thaw_attack(point: str) -> None:
            if point.startswith("after_thaw_before_unlink:"):
                os.pwrite(writer, b"MUTATION", 0)

        with mock.patch.object(reauthor_clean, "_FAULT_INJECTOR", thaw_attack):
            with self.assertRaises(reauthor_clean.ReauthorCleanError) as caught:
                reauthor_clean.clean(pack, targets)
        self.assertEqual(caught.exception.reason_code, "reauthor_clean_destroyed_mismatch")
        receipt = json.loads(Path(caught.exception.outcome["receipt_path"]).read_bytes())
        self.assertEqual(receipt["status"], "INCOMPLETE_DESTROYED_MISMATCH")
        self.assertNotEqual(
            receipt["destroyed_mismatch"][0]["authorized_payload_sha256"],
            receipt["destroyed_mismatch"][0]["observed_final_sha256"],
        )

        _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
        writer = os.open(targets[0] / "nested" / "item-0.txt", os.O_WRONLY)
        self.addCleanup(os.close, writer)

        def held_writer_attack(point: str) -> None:
            if point.startswith("after_unlink_before_postunlink_freeze:"):
                os.pwrite(writer, b"HELD-WRITER", 0)

        with mock.patch.object(reauthor_clean, "_FAULT_INJECTOR", held_writer_attack):
            with self.assertRaises(reauthor_clean.ReauthorCleanError) as held:
                reauthor_clean.clean(pack, targets)
        self.assertEqual(held.exception.reason_code, "reauthor_clean_destroyed_mismatch")

        _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
        writer = os.open(targets[0] / "nested" / "item-0.txt", os.O_WRONLY)
        self.addCleanup(os.close, writer)

        def post_authorization_attack(point: str) -> None:
            if point == "after_event_delete_authorized_directory_fsync":
                reauthor_clean._fchflags(writer, 0)
                os.pwrite(writer, b"POST-AUTH", 0)

        with mock.patch.object(
            reauthor_clean, "_FAULT_INJECTOR", post_authorization_attack
        ):
            with self.assertRaises(reauthor_clean.ReauthorCleanError) as post_auth:
                reauthor_clean.clean(pack, targets)
        self.assertIn(
            post_auth.exception.reason_code,
            {
                "reauthor_clean_concurrent_mutation",
                "reauthor_clean_state_inventory_mismatch",
            },
        )

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_recursive_freeze_precedes_authorization_inventory(self) -> None:
        _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
        original = reauthor_clean._inventory_tree
        observed: list[int] = []

        def inspect(active, manifest):
            observed.append(os.stat(active, follow_symlinks=False).st_flags)
            observed.extend(
                os.stat(path, follow_symlinks=False).st_flags
                for path in active.rglob("*")
            )
            return original(active, manifest)

        with mock.patch.object(reauthor_clean, "_inventory_tree", side_effect=inspect):
            self.assertEqual(reauthor_clean.clean(pack, targets)["completion"], "COMPLETE")
        self.assertTrue(observed)
        self.assertTrue(all(flags == reauthor_clean.UF_IMMUTABLE for flags in observed))

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_mismatch_event_crash_boundaries_replay_incident(self) -> None:
        for point in (
            "after_event_delete_mismatch_file_fsync",
            "before_event_delete_mismatch_directory_fsync",
            "after_event_delete_mismatch_directory_fsync",
        ):
            with self.subTest(point=point):
                _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
                writer = os.open(targets[0] / "nested" / "item-0.txt", os.O_WRONLY)
                self.addCleanup(os.close, writer)
                crashed = False

                def attack_and_crash(observed: str) -> None:
                    nonlocal crashed
                    if observed.startswith("after_unlink_before_postunlink_freeze:"):
                        os.pwrite(writer, b"MISMATCH", 0)
                    if observed == point and not crashed:
                        crashed = True
                        raise SimulatedCrash(point)

                with mock.patch.object(reauthor_clean, "_FAULT_INJECTOR", attack_and_crash):
                    with self.assertRaises(SimulatedCrash):
                        reauthor_clean.clean(pack, targets)
                with self.assertRaises(reauthor_clean.ReauthorCleanError) as incident:
                    self._resume(pack, targets)
                self.assertEqual(
                    incident.exception.reason_code,
                    "reauthor_clean_destroyed_mismatch",
                )
                self.assertEqual(
                    incident.exception.outcome["completion"],
                    "INCOMPLETE_DESTROYED_MISMATCH",
                )

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_target_replacement_and_unexpected_child_during_thaw_refuse(self) -> None:
        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        fired = False

        def replacement(point: str) -> None:
            nonlocal fired
            if point.startswith("after_thaw_before_unlink:") and not fired:
                fired = True
                relative = point.split(":", 1)[1]
                active = next((custody / reauthor_clean.QUARANTINE_DIRECTORY).iterdir())
                victim = active / relative
                saved = victim.with_name(victim.name + ".held")
                victim.rename(saved)
                victim.write_text("replacement\n", encoding="utf-8")

        with mock.patch.object(reauthor_clean, "_FAULT_INJECTOR", replacement):
            with self.assertRaises(reauthor_clean.ReauthorCleanError) as caught:
                reauthor_clean.clean(pack, targets)
        self.assertEqual(caught.exception.reason_code, "reauthor_clean_concurrent_mutation")

        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        fired = False

        def extra_child(point: str) -> None:
            nonlocal fired
            if point.startswith("after_thaw_before_unlink:") and not fired:
                fired = True
                relative = point.split(":", 1)[1]
                active = next((custody / reauthor_clean.QUARANTINE_DIRECTORY).iterdir())
                (active / relative).parent.joinpath("unexpected.txt").write_text("x")

        with mock.patch.object(reauthor_clean, "_FAULT_INJECTOR", extra_child):
            with self.assertRaises(reauthor_clean.ReauthorCleanError) as caught:
                reauthor_clean.clean(pack, targets)
        self.assertEqual(caught.exception.reason_code, "reauthor_clean_destroyed_unverified")

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_foreign_stale_pack_path_device_inode_generation_and_multiple_states(self) -> None:
        mutations = {
            "pack": lambda value: value["pack_identity"].update(
                {"pack_tree_git_oid": "0" * 40}
            ),
            "path": lambda value: value["request"]["entries"][0].update(
                {"canonical_path": "/foreign/path"}
            ),
            "device": lambda value: value["custody"]["root_anchor"].update(
                {"st_dev": value["custody"]["root_anchor"]["st_dev"] + 1}
            ),
            "inode": lambda value: value["sources"][0]["root_anchor"].update(
                {"st_ino": value["sources"][0]["root_anchor"]["st_ino"] + 1}
            ),
            "generation": lambda value: value["pack_identity"].update(
                {"generation": value["pack_identity"]["generation"] + 1}
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                _repository, pack, custody, targets, _untouched, _outside = self._fixture()
                original = self._crash_after_manifest(pack, targets)
                foreign = copy.deepcopy(original)
                mutate(foreign)
                foreign["state_id"] = reauthor_clean._derive_state_id(
                    reauthor_clean._manifest_identity_core(foreign)
                )
                foreign["expected_quarantine_path"] = str(
                    custody
                    / reauthor_clean.QUARANTINE_DIRECTORY
                    / foreign["state_id"]
                )
                path = reauthor_clean._manifest_path(
                    custody / reauthor_clean.OPERATION_DIRECTORY,
                    foreign["state_id"],
                )
                reauthor_clean._publish_no_clobber(
                    path, reauthor_clean._render_json(foreign)
                )
                with self.assertRaises(reauthor_clean.ReauthorCleanError) as caught:
                    self._resume(pack, targets)
                self.assertEqual(
                    caught.exception.reason_code,
                    "reauthor_clean_state_binding_mismatch",
                )

        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        first = self._crash_after_manifest(pack, targets)
        identity = reauthor_clean._authenticate_pack(pack)
        operation_root = custody / reauthor_clean.OPERATION_DIRECTORY
        second = reauthor_clean._build_manifest(
            identity, custody, operation_root, {item.name: item for item in targets}
        )
        reauthor_clean._publish_no_clobber(
            reauthor_clean._manifest_path(operation_root, second["state_id"]),
            reauthor_clean._render_json(second),
        )
        self.assertNotEqual(first["state_id"], second["state_id"])
        with self.assertRaises(reauthor_clean.ReauthorCleanError) as caught:
            self._resume(pack, targets)
        self.assertEqual(caught.exception.reason_code, "reauthor_clean_state_ambiguous")

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_pack_tree_head_and_generation_resume_rules(self) -> None:
        repository, pack, _custody, targets, _untouched, _outside = self._fixture()
        self._crash_after_manifest(pack, targets)
        (repository / "unrelated.txt").write_text("head moves\n")
        self._git(repository, "add", "unrelated.txt")
        self._git(repository, "commit", "-qm", "unrelated head movement")
        self.assertEqual(self._resume(pack, targets)["completion"], "COMPLETE")

        repository, pack, _custody, targets, _untouched, _outside = self._fixture()
        self._crash_after_manifest(pack, targets)
        (pack / "tree-change.txt").write_text("changes pack tree\n")
        self._git(repository, "add", ".")
        self._git(repository, "commit", "-qm", "pack tree movement")
        with self.assertRaises(reauthor_clean.ReauthorCleanError) as changed:
            self._resume(pack, targets)
        self.assertEqual(
            changed.exception.reason_code, "reauthor_clean_state_binding_mismatch"
        )

        repository, pack, _custody, targets, _untouched, _outside = self._fixture()
        self._crash_after_manifest(pack, targets)
        self._add_freeze(pack)
        self._git(repository, "add", ".")
        self._git(repository, "commit", "-qm", "freeze generation")
        with self.assertRaises(reauthor_clean.ReauthorCleanError) as frozen:
            self._resume(pack, targets)
        self.assertEqual(frozen.exception.reason_code, "reauthor_clean_frozen_pack")

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_split_rename_recreated_source_and_quarantine_anchor_refuse(self) -> None:
        first = sorted(reauthor_clean.EXPECTED_NAMESPACES)[0]
        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        self._crash(pack, targets, f"after_rename_{first}")
        (custody / first).mkdir()
        with self.assertRaises(reauthor_clean.ReauthorCleanError) as recreated:
            self._resume(pack, targets)
        self.assertEqual(
            recreated.exception.reason_code, "reauthor_clean_state_binding_mismatch"
        )

        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        self._crash(pack, targets, "after_event_prepared_directory_fsync")
        quarantine_root = custody / reauthor_clean.QUARANTINE_DIRECTORY
        active = next(quarantine_root.iterdir())
        moved = active.with_name(active.name + ".old")
        active.rename(moved)
        active.mkdir()
        with self.assertRaises(reauthor_clean.ReauthorCleanError) as rebound:
            self._resume(pack, targets)
        self.assertEqual(
            rebound.exception.reason_code, "reauthor_clean_state_binding_mismatch"
        )

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_remaining_projection_and_event_chain_tamper_refuse(self) -> None:
        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        self._crash(pack, targets, "after_event_delete_verified_directory_fsync")
        active = next((custody / reauthor_clean.QUARANTINE_DIRECTORY).iterdir())
        remaining_file = next(active.rglob("*.txt"))
        os.chflags(remaining_file, 0)
        remaining_file.write_text("stale receipt mutation\n")
        with self.assertRaises(reauthor_clean.ReauthorCleanError) as changed:
            self._resume(pack, targets)
        self.assertEqual(
            changed.exception.reason_code, "reauthor_clean_state_inventory_mismatch"
        )

        tamper_kinds = ("torn", "reordered", "duplicated", "hash-broken")
        for kind in tamper_kinds:
            with self.subTest(kind=kind):
                _repository, pack, custody, targets, _untouched, _outside = self._fixture()
                self._crash(pack, targets, "after_event_delete_authorized_directory_fsync")
                events_root = next(
                    (custody / reauthor_clean.OPERATION_DIRECTORY).glob("state-*.events")
                )
                files = sorted(events_root.iterdir())
                if kind == "torn":
                    os.chflags(files[-1], 0)
                    files[-1].write_bytes(b'{"torn":')
                elif kind == "reordered":
                    os.chflags(files[-1], 0)
                    files[-1].rename(events_root / "99999999.event.json")
                elif kind == "duplicated":
                    duplicate = events_root / f"{len(files) + 1:08d}.event.json"
                    duplicate.write_bytes(files[-1].read_bytes())
                else:
                    value = json.loads(files[-1].read_bytes())
                    value["prev_event_sha256"] = "f" * 64
                    self._rewrite_artifact(files[-1], value)
                with self.assertRaises(reauthor_clean.ReauthorCleanError) as caught:
                    self._resume(pack, targets)
                self.assertEqual(
                    caught.exception.reason_code,
                    "reauthor_clean_event_chain_invalid",
                )

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_unsupported_hardlink_symlink_special_nonutf8_xattr_and_flags(self) -> None:
        cases = []

        def hardlink(targets):
            source = targets[0] / "nested" / "item-0.txt"
            os.link(source, source.with_name("linked.txt"))

        cases.append(("hardlink", hardlink, "reauthor_clean_hardlink_unsupported", None))
        cases.append(
            (
                "symlink",
                lambda targets: (targets[0] / "link").symlink_to("nested"),
                "reauthor_clean_entry_type_unsupported",
                None,
            )
        )
        cases.append(
            (
                "special",
                lambda targets: os.mkfifo(targets[0] / "fifo"),
                "reauthor_clean_entry_type_unsupported",
                None,
            )
        )

        def flags(targets):
            os.chflags(
                targets[0] / "nested" / "item-0.txt",
                getattr(stat, "UF_APPEND", 0x4),
            )

        cases.append(
            (
                "flags",
                flags,
                "reauthor_clean_namespace_inventory_invalid",
                None,
            )
        )
        cases.append(
            (
                "xattr",
                lambda _targets: None,
                "reauthor_clean_extended_attribute_unreadable",
                mock.patch.object(
                    reauthor_clean,
                    "_xattrs",
                    side_effect=reauthor_clean._refuse(
                        "reauthor_clean_extended_attribute_unreadable", "denied"
                    ),
                ),
            )
        )
        for label, prepare, reason, patcher in cases:
            with self.subTest(label=label):
                _repository, pack, _custody, targets, _untouched, _outside = self._fixture()
                prepare(targets)
                context = patcher if patcher is not None else mock.patch.object(
                    reauthor_clean, "_FAULT_INJECTOR", None
                )
                with context:
                    self._assert_refusal(reason, pack, targets)

        with tempfile.TemporaryDirectory() as temporary:
            descriptor = os.open(temporary, os.O_RDONLY | os.O_DIRECTORY)
            self.addCleanup(os.close, descriptor)
            with mock.patch.object(
                reauthor_clean.os, "listdir", return_value=["bad-\udcff"]
            ):
                with self.assertRaises(reauthor_clean.ReauthorCleanError) as nonutf8:
                    reauthor_clean._scan_tree(
                        descriptor,
                        "",
                        lambda *_args: None,
                    )
            self.assertEqual(
                nonutf8.exception.reason_code,
                "reauthor_clean_entry_type_unsupported",
            )

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_concurrent_invocation_lock_refuses(self) -> None:
        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        operation_root = custody / reauthor_clean.OPERATION_DIRECTORY
        operation_root.mkdir()
        descriptor = os.open(operation_root / ".lock", os.O_RDWR | os.O_CREAT, 0o600)
        self.addCleanup(os.close, descriptor)
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self._assert_refusal("reauthor_clean_operation_lock_busy", pack, targets)
        self.assertTrue(all(target.exists() for target in targets))

    @unittest.skipUnless(DARWIN_FLAGS, "requires Darwin fchflags/st_flags")
    def test_legacy_v2_complete_refuses_and_partial_gets_deterministic_incident(self) -> None:
        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        operation_root = custody / reauthor_clean.OPERATION_DIRECTORY
        operation_root.mkdir()
        (operation_root / "reauthor-clean-20260820T120000000000Z.receipt.json").write_text(
            '{"schema_version":"joulewise.reauthor_clean_receipt.v2"}\n'
        )
        self._assert_refusal("reauthor_clean_legacy_state_unbound", pack, targets)

        _repository, pack, custody, targets, _untouched, _outside = self._fixture()
        operation_root = custody / reauthor_clean.OPERATION_DIRECTORY
        operation_root.mkdir()
        quarantine_root = custody / reauthor_clean.QUARANTINE_DIRECTORY
        active = quarantine_root / "20260820T120000000000Z"
        active.mkdir(parents=True)
        for target in targets:
            target.rename(active / target.name)
        missing = active / targets[0].name
        missing.rename(custody.parent / "legacy-missing-preserved")
        (operation_root / "reauthor-clean-20260820T120000000000Z.receipt.json").write_text(
            '{"schema_version":"joulewise.reauthor_clean_receipt.v2"}\n'
        )
        hashes = []
        for _attempt in range(2):
            with self.assertRaises(reauthor_clean.ReauthorCleanError) as incident:
                self._resume(pack, targets)
            self.assertEqual(
                incident.exception.reason_code, "reauthor_clean_destroyed_unverified"
            )
            hashes.append(incident.exception.outcome["receipt_sha256"])
            receipt = json.loads(
                Path(incident.exception.outcome["receipt_path"]).read_bytes()
            )
            self.assertEqual(
                receipt["destroyed_unverified"][0]["scope"],
                "subtree_delta_unknown",
            )
        self.assertEqual(hashes[0], hashes[1])


if __name__ == "__main__":
    unittest.main()
