"""F14: syscall ordering and failed-barrier retention on synthetic evidence."""

from __future__ import annotations

import fcntl
import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
from joulewise.bundle import write_raw_artifact
from joulewise.clock import FakeClock
from joulewise.interfaces import RunContext, acknowledge_durable_custody


class CustodyDurabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        bundle = self.root / "bundle"
        (bundle / "raw").mkdir(parents=True)
        self.context = RunContext(
            config=None,
            clock=FakeClock(start=100.0),
            run_id="synthetic-custody",
            bundle_path=bundle,
            raw_dir=bundle / "raw",
            logs_dir=bundle / "logs",
            outputs_dir=bundle / "outputs",
        )

    def _relative(self, path) -> str:
        return str(Path(path).relative_to(self.root))

    def _fd_path(self, fd: int) -> str:
        opened = os.fstat(fd)
        for path in [self.root, *self.root.rglob("*")]:
            candidate = path.stat()
            if (candidate.st_dev, candidate.st_ino) == (opened.st_dev, opened.st_ino):
                return self._relative(path)
        self.fail("sync descriptor has no synthetic fixture path")

    @contextmanager
    def _trace_syncs(self, *, platform="darwin"):
        events = []
        real_fsync, real_replace = os.fsync, os.replace

        def synced(fd):
            events.append(("fsync", self._fd_path(fd)))
            return real_fsync(fd)

        def replaced(source, destination):
            events.append(("replace", self._relative(source), self._relative(destination)))
            return real_replace(source, destination)

        def full_synced(fd, command):
            self.assertEqual(command, fcntl.F_FULLFSYNC)
            events.append(("fullfsync", self._fd_path(fd)))

        with (
            patch("joulewise.interfaces.sys.platform", platform),
            # Darwin's kernel command is 51; provide it on Linux test hosts.
            patch.object(fcntl, "F_FULLFSYNC", 51, create=True),
            patch("joulewise.interfaces.fcntl.fcntl", side_effect=full_synced),
            patch("os.fsync", side_effect=synced),
            patch("os.replace", side_effect=replaced),
        ):
            yield events

    def test_raw_and_receipt_syncs_precede_one_final_drive_cache_barrier(self):
        with self._trace_syncs() as events:
            artifact = write_raw_artifact(self.context, "native.plist", b"synthetic raw")
            acknowledgement = self.context.acknowledge_custody("capture", [artifact])

        raw_rename = next(
            i for i, e in enumerate(events)
            if e[-1] == "bundle/raw/native.plist" and e[0] == "replace"
        )
        receipt_rename = next(
            i for i, e in enumerate(events)
            if e[-1] == "bundle/logs/custody/capture.json" and e[0] == "replace"
        )
        self.assertEqual(events[raw_rename - 1], ("fsync", events[raw_rename][1]))
        self.assertEqual(events[raw_rename + 1], ("fsync", "bundle/raw"))
        self.assertEqual(events[receipt_rename - 1], ("fsync", events[receipt_rename][1]))
        self.assertIn(("fsync", "bundle/raw/native.plist"), events[raw_rename + 1:receipt_rename])
        after_receipt = events[receipt_rename + 1:]
        for directory in ("bundle/raw", "bundle/logs/custody", "bundle/logs", "bundle", "."):
            self.assertIn(("fsync", directory), after_receipt)
        self.assertLess(
            after_receipt.index(("fsync", "bundle/logs/custody")),
            after_receipt.index(("fsync", "bundle/logs")),
        )
        self.assertLess(
            after_receipt.index(("fsync", "bundle")),
            after_receipt.index(("fsync", ".")),
        )
        self.assertEqual(
            [e for e in events if e[0] == "fullfsync"],
            [("fullfsync", "bundle/logs/custody/capture.json")],
        )
        self.assertEqual(events[-1][0], "fullfsync")
        self.assertEqual(
            json.loads(acknowledgement.acknowledgement_path.read_text())["artifacts"],
            ["raw/native.plist"],
        )
        self.assertEqual(artifact.read_bytes(), b"synthetic raw")

    def test_directory_artifact_syncs_nested_evidence_and_ancestor_entries(self):
        collection = self.context.bundle_path / "raw" / "collection"
        nested = collection / "nested" / "evidence.bin"
        nested.parent.mkdir(parents=True)
        nested.write_bytes(b"synthetic remote evidence")
        with self._trace_syncs() as events:
            acknowledge_durable_custody(self.context.bundle_path, "remote", [collection])
        for path in (nested, nested.parent, collection, collection.parent):
            self.assertIn(("fsync", self._relative(path)), events)
        self.assertEqual(events[-1], ("fullfsync", "bundle/logs/custody/remote.json"))

    def test_non_macos_receipt_uses_file_and_directory_fsync(self):
        artifact = write_raw_artifact(self.context, "native.bin", b"synthetic raw")
        with self._trace_syncs(platform="linux") as events:
            acknowledge_durable_custody(self.context.bundle_path, "portable", [artifact])
        self.assertFalse(any(e[0] == "fullfsync" for e in events))
        self.assertEqual(events[-1], ("fsync", "."))

    def test_failed_temp_file_sync_does_not_publish_raw_artifact(self):
        with patch("os.fsync", side_effect=OSError("temp file sync failed")):
            with self.assertRaisesRegex(OSError, "temp file sync failed"):
                write_raw_artifact(self.context, "native.bin", b"synthetic raw")
        self.assertFalse(list(self.context.raw_dir.iterdir()))

    def test_failed_sync_retains_native_capture_until_salvage_succeeds(self):
        for failure in ("raw_directory", "receipt_directory", "drive_cache"):
            with self.subTest(failure=failure):
                name = failure + ".plist"
                source = self.root / name
                source.write_bytes(b"synthetic retained capture")
                adapter = PowermetricsTelemetryAdapter(self.context.clock)
                adapter._pending_captures[name] = source
                real_fsync = os.fsync
                failed_directory = (
                    "bundle/raw" if failure == "raw_directory"
                    else "bundle/logs/custody"
                )

                def failing_sync(fd):
                    if self._fd_path(fd) == failed_directory:
                        raise OSError("directory sync failed")
                    return real_fsync(fd)

                with (
                    patch("joulewise.interfaces.sys.platform", "darwin"),
                    patch.object(fcntl, "F_FULLFSYNC", 51, create=True),
                    patch(
                        "os.fsync",
                        side_effect=failing_sync if failure != "drive_cache" else real_fsync,
                    ),
                    patch(
                        "joulewise.interfaces.fcntl.fcntl",
                        side_effect=OSError("drive cache sync failed"),
                    ),
                ):
                    failed = adapter.salvage_custody(self.context)
                self.assertFalse(failed[0]["acknowledged"])
                self.assertTrue(source.is_file())
                self.assertEqual(adapter._pending_captures[name], source)
                self.assertEqual((self.context.raw_dir / name).read_bytes(), source.read_bytes())
                with self._trace_syncs():
                    retried = adapter.salvage_custody(self.context)
                self.assertTrue(retried[0]["acknowledged"])
                self.assertFalse(source.exists())
                self.assertNotIn(name, adapter._pending_captures)


if __name__ == "__main__":
    unittest.main()
