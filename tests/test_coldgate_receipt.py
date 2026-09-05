from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock

from joulewise import coldgate_receipt
from joulewise.coldgate_receipt import (
    ReceiptDirectoryChanged,
    ReceiptDurabilityUncertain,
    ReceiptPublicationCollision,
    ReceiptPublicationError,
    persist_validator_receipt,
)


class ValidatorReceiptPublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.receipts = self.root / "receipts"
        self.receipts.mkdir()
        self.payload = b'{"result":"PASS","schema":"coldgate-validator-receipt/v2"}\n'

    def test_success_is_byte_exact_atomic_and_fsync_complete(self) -> None:
        real_fsync = os.fsync
        sync_kinds: list[str] = []

        def record_sync(descriptor: int) -> None:
            mode = os.fstat(descriptor).st_mode
            sync_kinds.append("directory" if stat.S_ISDIR(mode) else "file")
            real_fsync(descriptor)

        with mock.patch.object(coldgate_receipt.os, "fsync", side_effect=record_sync):
            result = persist_validator_receipt(
                self.receipts, "validation.json", self.payload
            )

        published = self.receipts / "validation.json"
        self.assertEqual(result.path, published)
        self.assertEqual(published.read_bytes(), self.payload)
        self.assertEqual(result.sha256, hashlib.sha256(self.payload).hexdigest())
        self.assertEqual(result.size_bytes, len(self.payload))
        self.assertEqual(sync_kinds, ["file", "directory"])
        self.assertEqual(stat.S_IMODE(published.stat().st_mode), 0o600)
        self.assertEqual(published.stat().st_nlink, 1)
        self.assertEqual(list(self.receipts.iterdir()), [published])

    def test_directory_path_replacement_refuses_without_writing_either_tree(self) -> None:
        anchored = self.root / "opened-receipts"

        def replace_directory(_descriptor: int) -> None:
            self.receipts.rename(anchored)
            self.receipts.mkdir()

        with mock.patch.object(
            coldgate_receipt,
            "_after_directory_open",
            side_effect=replace_directory,
        ):
            with self.assertRaisesRegex(
                ReceiptDirectoryChanged, "changed after it was opened"
            ):
                persist_validator_receipt(
                    self.receipts, "validation.json", self.payload
                )

        self.assertEqual(list(anchored.iterdir()), [])
        self.assertEqual(list(self.receipts.iterdir()), [])

    def test_directory_fsync_failure_is_reported_as_durability_uncertain(self) -> None:
        real_fsync = os.fsync

        def fail_directory_sync(descriptor: int) -> None:
            if stat.S_ISDIR(os.fstat(descriptor).st_mode):
                raise OSError("injected directory fsync failure")
            real_fsync(descriptor)

        with mock.patch.object(
            coldgate_receipt.os, "fsync", side_effect=fail_directory_sync
        ):
            with self.assertRaises(ReceiptDurabilityUncertain) as caught:
                persist_validator_receipt(
                    self.receipts, "validation.json", self.payload
                )

        published = self.receipts / "validation.json"
        self.assertEqual(caught.exception.path, published)
        self.assertEqual(published.read_bytes(), self.payload)

    def test_file_fsync_failure_leaves_no_published_receipt(self) -> None:
        with mock.patch.object(
            coldgate_receipt.os,
            "fsync",
            side_effect=OSError("injected file fsync failure"),
        ):
            with self.assertRaises(ReceiptPublicationError):
                persist_validator_receipt(
                    self.receipts, "validation.json", self.payload
                )

        self.assertEqual(list(self.receipts.iterdir()), [])

    def test_existing_file_or_symlink_is_never_overwritten_or_followed(self) -> None:
        outside = self.root / "outside.json"
        outside.write_bytes(b"outside\n")
        target = self.receipts / "validation.json"

        for existing in ("file", "symlink"):
            with self.subTest(existing=existing):
                target.unlink(missing_ok=True)
                if existing == "file":
                    target.write_bytes(b"existing\n")
                else:
                    target.symlink_to(outside)
                with self.assertRaises(ReceiptPublicationCollision):
                    persist_validator_receipt(
                        self.receipts, target.name, self.payload
                    )
                expected = b"existing\n" if existing == "file" else b"outside\n"
                self.assertEqual(target.read_bytes(), expected)
                self.assertEqual(outside.read_bytes(), b"outside\n")

    def test_final_name_is_absent_while_receipt_bytes_are_being_written(self) -> None:
        target = self.receipts / "validation.json"
        real_write = os.write
        observations: list[bool] = []

        def write_one_byte(descriptor: int, payload: bytes) -> int:
            written = real_write(descriptor, bytes(payload[:1]))
            observations.append(target.exists())
            return written

        with mock.patch.object(
            coldgate_receipt.os, "write", side_effect=write_one_byte
        ):
            persist_validator_receipt(self.receipts, target.name, self.payload)

        self.assertGreater(len(observations), 1)
        self.assertFalse(any(observations))
        self.assertEqual(target.read_bytes(), self.payload)

    def test_receipt_name_is_one_directory_entry(self) -> None:
        for name in ("", ".", "..", "nested/receipt.json", "bad\x00name"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    persist_validator_receipt(self.receipts, name, self.payload)


if __name__ == "__main__":
    unittest.main()
