import errno
import hashlib
import os
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from joulewise import durable


class Interrupted(BaseException):
    pass


class DurableTests(unittest.TestCase):
    def setUp(self):
        root = tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        self.root = Path(root.name)
        self.path = self.root / "artifact"

    def temps(self):
        return sorted(self.root.glob(".jw-publish-*.tmp"))

    def interrupt(self, operation, point, data=b"new"):
        def checkpoint(name):
            if name == point:
                raise Interrupted

        with patch.object(durable, "checkpoint", checkpoint):
            with self.assertRaises(Interrupted):
                operation(self.path, data)

    def test_create_once_and_collision_preserve_bytes_and_permissions(self):
        durable.publish_once(self.path, b"original")
        inode = self.path.stat().st_ino
        with self.assertRaises(FileExistsError):
            durable.publish_once(self.path, b"different")
        self.assertEqual(durable.read_published(self.path, 8), b"original")
        self.assertEqual(self.path.stat().st_ino, inode)
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
        self.assertEqual(self.temps(), [])

    def test_replace_create_and_replace(self):
        durable.replace(self.path, b"old")
        with self.path.open("rb") as old:
            durable.replace(self.path, b"new\x00")
            self.assertEqual(old.read(), b"old")
        self.assertEqual(durable.read_published(self.path, 4), b"new\x00")
        self.assertEqual(self.temps(), [])

    def test_read_absence_empty_size_and_unsafe_types(self):
        with self.assertRaises(durable.Absent):
            durable.read_published(self.path, 0)
        with self.assertRaises(ValueError):
            durable.read_published(self.path, -1)
        durable.publish_once(self.path, b"")
        self.assertEqual(durable.read_published(self.path, 0), b"")
        durable.replace(self.path, b"longer")
        with self.assertRaises(durable.Unsafe):
            durable.read_published(self.path, 5)
        self.path.unlink()
        for create in (self.path.mkdir, lambda: os.mkfifo(self.path),
                       lambda: self.path.symlink_to(self.root / "missing")):
            with self.subTest(create=create):
                create()
                with self.assertRaises(durable.Unsafe):
                    durable.read_published(self.path, 100)
                with self.assertRaises(durable.Unsafe):
                    durable.finish_publication(self.path)
                if self.path.is_dir():
                    self.path.rmdir()
                else:
                    self.path.unlink()

    def test_publisher_keeps_target_on_dangling_symlink_collision(self):
        missing = self.root / "missing"
        self.path.symlink_to(missing)
        with self.assertRaises(FileExistsError):
            durable.publish_once(self.path, b"new")
        self.assertTrue(self.path.is_symlink())
        self.assertFalse(missing.exists())
        self.assertEqual(self.temps(), [])

    def test_each_create_once_crash_point(self):
        points = {
            "temp_created": "absent", "temp_written": "absent", "file_synced": "absent",
            "linked": "busy", "link_synced": "busy", "temp_unlinked": "visible",
            "directory_synced": "visible",
        }
        for point, status in points.items():
            with self.subTest(point=point):
                self.interrupt(durable.publish_once, f"durable.{point}")
                before = set(self.root.iterdir())
                if status == "busy":
                    with self.assertRaises(durable.Busy):
                        durable.read_published(self.path, 3)
                elif status == "absent":
                    with self.assertRaises(durable.Absent):
                        durable.read_published(self.path, 3)
                else:
                    self.assertEqual(durable.read_published(self.path, 3), b"new")
                self.assertEqual(set(self.root.iterdir()), before)
                durable.finish_publication(self.path)
                durable.finish_publication(self.path)
                self.assertEqual(self.temps(), [])
                if status == "absent":
                    self.assertFalse(self.path.exists())
                    durable.publish_once(self.path, b"new")
                self.assertEqual(durable.read_published(self.path, 3), b"new")
                self.path.unlink()

    def test_each_replace_crash_point(self):
        for point, expected in (("temp_created", b"old"), ("temp_written", b"old"),
                                ("file_synced", b"old"), ("replaced", b"new"),
                                ("directory_synced", b"new")):
            with self.subTest(point=point):
                durable.replace(self.path, b"old")
                self.interrupt(durable.replace, f"durable.{point}")
                self.assertEqual(durable.read_published(self.path, 3), expected)
                durable.finish_publication(self.path)
                self.assertEqual(durable.read_published(self.path, 3), expected)
                self.assertEqual(self.temps(), [])

    def test_abrupt_process_exit_with_link_is_reconciled(self):
        program = """
import os
import sys
from pathlib import Path

from joulewise import durable

def crash(name):
    if name == "durable.linked":
        os._exit(77)

durable.checkpoint = crash
durable.publish_once(Path(sys.argv[1]), b"child")
"""
        result = subprocess.run([sys.executable, "-B", "-c", program, str(self.path)],
                                check=False, capture_output=True)
        self.assertEqual(result.returncode, 77, result.stderr)
        with self.assertRaises(durable.Busy):
            durable.read_published(self.path, 5)
        durable.finish_publication(self.path)
        self.assertEqual(durable.read_published(self.path, 5), b"child")

    def test_recovery_discards_only_this_artifacts_torn_and_duplicate_temps(self):
        neighbor = self.root / "other"
        self.interrupt(durable.publish_once, "durable.temp_created")
        self.interrupt(durable.publish_once, "durable.temp_written")
        self.interrupt(durable.publish_once, "durable.linked")
        linked, = [temp for temp in self.temps() if temp.samefile(self.path)]
        duplicate = linked.with_name(linked.name[:-36] + "1" * 32 + ".tmp")
        os.link(linked, duplicate)
        self.interrupt(lambda _, data: durable.publish_once(neighbor, data),
                       "durable.temp_written")
        stray = self.root / ".jw-publish-unrelated.tmp"
        stray.write_bytes(b"keep")
        with self.assertRaises(durable.Busy):
            durable.read_published(self.path, 3)
        durable.finish_publication(self.path)
        self.assertEqual(durable.read_published(self.path, 3), b"new")
        self.assertFalse(neighbor.exists())
        self.assertEqual(len(self.temps()), 2)
        durable.finish_publication(neighbor)
        self.assertEqual(self.temps(), [stray])

    def test_foreign_hardlink_is_unsafe_and_recovery_changes_nothing(self):
        durable.publish_once(self.path, b"old")
        other = self.root / "foreign"
        os.link(self.path, other)
        with self.assertRaises(durable.Unsafe):
            durable.read_published(self.path, 3)
        with self.assertRaises(durable.Unsafe):
            durable.finish_publication(self.path)
        self.assertTrue(other.samefile(self.path))

    def test_unsafe_temp_is_not_followed_or_removed(self):
        self.interrupt(durable.publish_once, "durable.temp_created")
        temp, = self.temps()
        temp.unlink()
        temp.symlink_to(self.root / "missing")
        with self.assertRaises(durable.Unsafe):
            durable.finish_publication(self.path)
        self.assertTrue(temp.is_symlink())
        self.assertFalse(self.path.exists())

    def test_concurrent_create_once_has_one_winner(self):
        start = threading.Barrier(4)
        def writer(index):
            data = str(index).encode()
            start.wait()
            try:
                durable.publish_once(self.path, data)
            except FileExistsError:
                return None
            return data

        with ThreadPoolExecutor(4) as pool:
            winner, = [data for data in pool.map(writer, range(4)) if data is not None]
        self.assertEqual(durable.read_published(self.path, 1), winner)
        self.assertEqual(self.temps(), [])

    def test_linked_publication_reconciles_through_filesystem_alias(self):
        for name, alternate in (("Record.ok", "record.ok"), ("café", "cafe\u0301")):
            with self.subTest(name=name):
                self.path = self.root / name
                alias = self.root / alternate
                self.path.write_bytes(b"probe")
                equivalent = alias.exists() and alias.samefile(self.path)
                self.path.unlink()
                if not equivalent:
                    self.skipTest("the fixture filesystem distinguishes these spellings")
                neighbor = self.root / "unrelated"
                self.interrupt(lambda _, data: durable.publish_once(neighbor, data),
                               "durable.temp_written")
                neighbor_temps = self.temps()
                self.interrupt(durable.publish_once, "durable.link_synced")
                with self.assertRaises(durable.Busy):
                    durable.read_published(alias, 3)
                durable.finish_publication(alias)
                self.assertEqual(durable.read_published(self.path, 3), b"new")
                self.assertEqual(durable.read_published(alias, 3), b"new")
                self.assertEqual(self.temps(), neighbor_temps)
                durable.finish_publication(neighbor)
                self.path.unlink()

    def test_sync_order_and_enospc_eio_at_each_sync(self):
        fsync = os.fsync
        for operation, order in ((durable.publish_once, ["file", "dir", "dir"]),
                                 (durable.replace, ["file", "dir"])):
            for error in (None, errno.ENOSPC, errno.EIO):
                positions = [None] if error is None else range(len(order))
                for position in positions:
                    with self.subTest(operation=operation.__name__, error=error, position=position):
                        seen = []
                        def sync(fd):
                            seen.append("dir" if stat.S_ISDIR(os.fstat(fd).st_mode) else "file")
                            if len(seen) - 1 == position:
                                raise OSError(error, os.strerror(error))
                            fsync(fd)
                        if operation == durable.replace:
                            durable.replace(self.path, b"old")
                        with patch.object(durable.os, "fsync", sync):
                            if error is None:
                                operation(self.path, b"new")
                            else:
                                expected_error = durable.VisibleNotDurable if position else OSError
                                with self.assertRaises(expected_error) as raised:
                                    operation(self.path, b"new")
                                self.assertEqual(raised.exception.errno, error)
                                if position:
                                    self.assertEqual(raised.exception.digest, hashlib.sha256(b"new").hexdigest())
                                    self.assertIsInstance(raised.exception.__cause__, OSError)
                                else:
                                    self.assertNotIsInstance(raised.exception, durable.VisibleNotDurable)
                        self.assertEqual(seen, order if position is None else order[:position + 1])
                        if position == 1 and operation == durable.publish_once:
                            with self.assertRaises(durable.Busy):
                                durable.read_published(self.path, 3)
                        durable.finish_publication(self.path)
                        if position == 0 and operation == durable.publish_once:
                            self.assertFalse(self.path.exists())
                        else:
                            expected = b"old" if position == 0 else b"new"
                            self.assertEqual(durable.read_published(self.path, 3), expected)
                        self.assertEqual(self.temps(), [])
                        self.path.unlink(missing_ok=True)

    def test_publish_once_late_retry_resyncs_identical_bytes(self):
        native_sync = os.fsync
        for point in ("durable.linked", "durable.temp_unlinked"):
            with self.subTest(point=point):
                failure = OSError(errno.EIO, "synthetic sync failure")

                def fail_after_visibility(name):
                    if name == point:
                        raise failure

                with patch.object(durable, "checkpoint", fail_after_visibility):
                    with self.assertRaises(durable.VisibleNotDurable) as caught:
                        durable.publish_once(self.path, b"original")
                self.assertEqual(caught.exception.digest, hashlib.sha256(b"original").hexdigest())
                with self.assertRaises(FileExistsError):
                    durable.publish_once(self.path, b"different")
                with patch.object(durable.os, "fsync", side_effect=native_sync) as sync:
                    durable.publish_once(self.path, b"original")
                self.assertGreaterEqual(sync.call_count, 2)
                self.assertEqual(durable.read_published(self.path, 8), b"original")
                self.assertEqual(self.temps(), [])
                self.path.unlink()

    def test_enospc_on_create_write_and_link(self):
        failure = OSError(errno.ENOSPC, "synthetic disk full")
        with patch.object(durable.os, "open", side_effect=[os.open(self.root, os.O_RDONLY), failure]):
            with self.assertRaises(OSError) as raised:
                durable.publish_once(self.path, b"new")
        self.assertEqual(raised.exception.errno, errno.ENOSPC)
        for member in ("fdopen", "link"):
            with self.subTest(member=member):
                if member == "fdopen":
                    fdopen = os.fdopen
                    def short_write(fd, mode):
                        handle = fdopen(fd, mode)
                        class Stream:
                            def __enter__(self):
                                return self
                            def __exit__(self, *_):
                                handle.close()
                            def write(self, _):
                                handle.write(b"n")
                                raise failure
                        return Stream()
                    effect = short_write
                else:
                    effect = failure
                with patch.object(durable.os, member, side_effect=effect):
                    with self.assertRaises(OSError) as raised:
                        durable.publish_once(self.path, b"new")
                self.assertEqual(raised.exception.errno, errno.ENOSPC)
                with self.assertRaises(durable.Absent):
                    durable.read_published(self.path, 3)
                durable.finish_publication(self.path)
        durable.publish_once(self.path, b"new")
        self.assertEqual(durable.read_published(self.path, 3), b"new")

    def test_recovery_sync_failure_keeps_busy_link(self):
        self.interrupt(durable.publish_once, "durable.linked")
        with patch.object(durable.os, "fsync", side_effect=OSError(errno.EIO, "synthetic")):
            with self.assertRaises(OSError) as raised:
                durable.finish_publication(self.path)
        self.assertEqual(raised.exception.errno, errno.EIO)
        with self.assertRaises(durable.Busy):
            durable.read_published(self.path, 3)
        durable.finish_publication(self.path)
        self.assertEqual(durable.read_published(self.path, 3), b"new")
