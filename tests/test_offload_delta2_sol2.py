"""Independent final deletion review, seat 2, against ed3b375b7.

Synthetic trees only. Passing tests named ``witness`` reproduce an outstanding
limitation; they are not safety passes. Volumes, transport and iCloud are fakes.
The native restore implementation is the digest-pinned local Git blob used by
the builder's regression suite. No production data or home-directory probe.
"""
from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest import mock

from tests.test_offload_delta_fixes import Base
from tests import test_offload_window as fixtures

ow = fixtures.ow


class QuarantineRecovery(Base):
    def interrupt_first_unlink(self):
        off = self.offload()
        detached = []

        def crash(path, **kwargs):
            detached.append(Path(path))
            raise OSError(errno.EIO, "synthetic crash after detach")

        off.unlink = crash
        with self.assertRaises(OSError):
            off.release()
        self.assertEqual(len(detached), 1)
        self.assertTrue(detached[0].is_file())
        return detached[0]

    def test_crash_after_quarantine_journal_before_mkdir_resumes(self):
        self.verified(codec="gzip")
        original = ow.write_atomic

        def crash_after_journal(path, raw):
            original(path, raw)
            if Path(path).name == "deleting.json" and "quarantine" in json.loads(raw):
                raise OSError(errno.EIO, "synthetic crash before quarantine mkdir")

        with mock.patch.object(ow, "write_atomic", side_effect=crash_after_journal):
            with self.assertRaises(OSError):
                self.offload().release()
        self.assert_nothing_deleted()
        journal = ow.read_json(self.offload().dir / "deleting.json")
        self.assertTrue(journal["quarantine"])
        self.assertTrue(all(not Path(q).exists() for q in journal["quarantine"].values()))
        self.assertTrue(self.offload().release()["resumed"])
        self.assertFalse(any((self.record / rel).exists() for rel in self.files))

    def test_detached_object_is_rehashed_on_resume(self):
        self.verified(codec="gzip")
        detached = self.interrupt_first_unlink()
        original = detached.read_bytes()
        unique = b"!" * len(original)
        info = detached.stat()
        detached.write_bytes(unique)
        os.utime(detached, ns=(info.st_atime_ns, info.st_mtime_ns))
        with self.assertRaisesRegex(ow.Mismatch, "quarantine_holds_unbound_object"):
            self.offload().release()
        journal = ow.read_json(self.offload().dir / "deleting.json")
        row = journal["inventory"][0]
        home = Path(row["root"]) / row["path"]
        self.assertEqual(home.read_bytes(), unique)
        self.assertFalse((self.offload().dir / "released.json").exists())

    def test_resume_without_second_receipt_does_not_drain_detached_object(self):
        self.verified(codec="gzip")
        detached = self.interrupt_first_unlink()
        original = detached.read_bytes()
        (self.store / "second/w1-test" / ow.SECOND_RECEIPT).unlink()
        with self.assertRaisesRegex(ow.Refusal, "second_copy_not_confirmed"):
            self.offload().release()
        self.assertEqual(detached.read_bytes(), original)

    def test_resume_after_air_decay_does_not_drain_detached_object(self):
        self.verified(codec="gzip")
        detached = self.interrupt_first_unlink()
        original = detached.read_bytes()
        manifest = ow.read_json(self.offload().dir / ow.MANIFEST_NAME)
        (self.store / "inbox/w1-test" / manifest["parts"][0]["name"]).write_bytes(b"decay")
        with self.assertRaisesRegex(ow.Mismatch, "air_part_decayed"):
            self.offload().release()
        self.assertEqual(detached.read_bytes(), original)

    def test_existing_quarantine_name_with_unbound_contents_refuses(self):
        self.verified(codec="gzip")
        collision = self.record.parent / ".jw-offload-q-w1-test-cccccccc"
        collision.mkdir(mode=0o700)
        unique = collision / "operator-file"
        unique.write_bytes(b"unbacked synthetic collision contents")
        with mock.patch.object(ow.secrets, "token_hex", side_effect=lambda n: "cc" * n):
            with self.assertRaisesRegex(ow.Mismatch, "quarantine_holds_unbound_object"):
                self.offload().release()
        self.assertEqual(unique.read_bytes(), b"unbacked synthetic collision contents")
        self.assert_nothing_deleted()

    def test_cross_device_rename_error_keeps_source_and_resumes(self):
        self.verified(codec="gzip")
        original = os.rename

        def exdev(source, destination, *args, **kwargs):
            if "src_dir_fd" in kwargs:
                raise OSError(errno.EXDEV, "synthetic mount boundary")
            return original(source, destination, *args, **kwargs)

        with mock.patch.object(ow.os, "rename", side_effect=exdev):
            with self.assertRaises(OSError) as caught:
                self.offload().release()
        self.assertEqual(caught.exception.errno, errno.EXDEV)
        self.assert_nothing_deleted()
        self.assertTrue(self.offload().release()["resumed"])

    def test_quarantine_on_other_device_refuses_before_detach(self):
        self.verified(codec="gzip")
        original = os.lstat

        def other_device(path, *args, **kwargs):
            info = original(path, *args, **kwargs)
            if Path(path) == self.record:
                values = list(info)
                values[2] += 1  # st_dev only; mount layout is simulated, never mounted.
                return os.stat_result(values)
            return info

        with mock.patch.object(ow.os, "lstat", side_effect=other_device):
            with self.assertRaisesRegex(ow.Refusal, "quarantine_cross_device"):
                self.offload().release()
        self.assert_nothing_deleted()

    def test_corrupt_json_journal_fails_closed(self):
        self.verified(codec="gzip")
        detached = self.interrupt_first_unlink()
        original = detached.read_bytes()
        (self.offload().dir / "deleting.json").write_bytes(b'{"state":')
        with self.assertRaises(json.JSONDecodeError):
            self.offload().release()
        self.assertEqual(detached.read_bytes(), original)
        self.assertFalse((self.offload().dir / "released.json").exists())

    def test_wrong_record_pin_in_journal_refuses(self):
        self.verified(codec="gzip")
        detached = self.interrupt_first_unlink()
        original = detached.read_bytes()
        path = self.offload().dir / "deleting.json"
        journal = ow.read_json(path)
        journal["record_manifest_sha256"] = "0" * 64
        ow.write_atomic(path, ow.canonical(journal))
        with self.assertRaisesRegex(ow.Mismatch, "deletion_journal_mismatch"):
            self.offload().release()
        self.assertEqual(detached.read_bytes(), original)

    def test_changed_digest_in_journal_preserves_remaining_source(self):
        self.verified(codec="gzip")
        detached = self.interrupt_first_unlink()
        path = self.offload().dir / "deleting.json"
        journal = ow.read_json(path)
        row = journal["inventory"][-1]
        row["sha256"] = "0" * 64
        source = Path(row["root"]) / row["path"]
        original = source.read_bytes()
        ow.write_atomic(path, ow.canonical(journal))
        with self.assertRaisesRegex(ow.Mismatch, "content_differs_from_bound_digest"):
            self.offload().release()
        self.assertEqual(source.read_bytes(), original)
        self.assertFalse(detached.exists())  # only a separately reverified, bound object was drained.

    def test_reused_window_id_with_fresh_state_is_refused_by_air(self):
        self.verified(codec="gzip")
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
        for rel, raw in self.files.items():
            path = self.record / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        unique = b"new synthetic generation under reused window id"
        self.put_file("members/m01/outputs/align_turns.jsonl", unique)
        new_state = self.tmp / "mbp/fresh-state"
        self.assertEqual(self.run_offload(state_root=new_state, codec="gzip"), 3)
        self.assertEqual((self.record / "members/m01/outputs/align_turns.jsonl").read_bytes(), unique)
        self.assertEqual(self.span(state=new_state)["reason"], "window_id_conflict_on_air")


class LockBoundaries(Base):
    def exec_contender(self):
        code = """
import importlib.util
from pathlib import Path
import sys
spec = importlib.util.spec_from_file_location('offload_lock_check', sys.argv[1])
ow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ow)
try:
    with ow.state_lock(Path(sys.argv[2])):
        print('entered')
except ow.Refusal as exc:
    print(str(exc))
"""
        result = subprocess.run([sys.executable, "-B", "-c", code,
                                 str(fixtures.ROOT / "scripts/offload_window.py"), str(self.state)],
                                capture_output=True, text=True, timeout=10, cwd=fixtures.ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_independent_process_refuses_during_nested_lock_then_enters(self):
        with ow.state_lock(self.state):
            with ow.state_lock(self.state):
                self.assertEqual(self.exec_contender(), "offload_already_running")
            self.assertEqual(self.exec_contender(), "offload_already_running")
        self.assertEqual(self.exec_contender(), "entered")

    @unittest.skipUnless(hasattr(os, "fork"), "fork inheritance requires POSIX")
    def test_witness_fork_child_inherits_reentrant_lock_registry(self):
        # A latent library-use limitation: the shipped CLI never forks Python
        # workers while holding this lock. Exec-created processes refuse above.
        read_fd, write_fd = os.pipe()
        try:
            with ow.state_lock(self.state):
                child = os.fork()
                if child == 0:
                    try:
                        os.close(read_fd)
                        with ow.state_lock(self.state):
                            os.write(write_fd, b"entered")
                    except ow.Refusal:
                        os.write(write_fd, b"refused")
                    finally:
                        os._exit(0)
                os.close(write_fd)
                write_fd = -1
                self.assertEqual(os.read(read_fd, 32), b"entered")
                _, status = os.waitpid(child, 0)
                self.assertEqual(os.waitstatus_to_exitcode(status), 0)
                self.assertEqual(self.exec_contender(), "offload_already_running")
        finally:
            os.close(read_fd)
            if write_fd != -1:
                os.close(write_fd)


class OpenWriterResidual(Base):
    def during_detach(self, *, reset_mtime):
        self.verified(codec="gzip")
        target = self.record / "custody/night/chain-stages.jsonl"
        before = target.stat()
        unique = b"!" * before.st_size
        writer = os.open(target, os.O_RDWR)
        self.addCleanup(os.close, writer)
        original = os.rename
        changed = []

        def write_after_last_stat(source, destination, *args, **kwargs):
            if source == target.name and "src_dir_fd" in kwargs and not changed:
                os.write(writer, unique)
                os.fsync(writer)
                mtime = before.st_mtime_ns if reset_mtime else before.st_mtime_ns + 1_000_000
                os.utime(writer, ns=(before.st_atime_ns, mtime))
                changed.append(True)
            return original(source, destination, *args, **kwargs)

        with mock.patch.object(ow.os, "rename", side_effect=write_after_last_stat):
            if reset_mtime:
                self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
            else:
                with self.assertRaisesRegex(ow.Mismatch, "changed_during_deletion"):
                    self.offload().release()
        self.assertEqual(changed, [True])
        return target, writer, unique

    def test_in_place_writer_with_changed_mtime_is_preserved(self):
        target, _, unique = self.during_detach(reset_mtime=False)
        self.assertEqual(target.read_bytes(), unique)

    def test_witness_same_inode_writer_resetting_mtime_can_lose_new_bytes(self):
        target, writer, unique = self.during_detach(reset_mtime=True)
        self.assertFalse(target.exists())
        self.assertEqual(os.fstat(writer).st_nlink, 0)
        self.assertEqual(os.pread(writer, len(unique), 0), unique)
        manifest = ow.read_json(self.offload().dir / ow.MANIFEST_NAME)
        relative = target.relative_to(self.record).as_posix()
        part = next(row["part"] for row in manifest["files"] if row["path"] == relative)
        for source in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            members = self.payload_names(source / part, manifest["codec"])
            self.assertEqual(members[relative], self.files[relative])
            self.assertNotEqual(members[relative], unique)


@unittest.skipUnless(ow.zstd_cli(), "native harvest packs require zstd")
class NativeRestoreBoundaries(Base):
    def test_witness_empty_external_directory_is_accepted_but_not_restorable(self):
        external = self.tmp / "mbp/empty-external-target"
        external.mkdir()
        harvest, finalized, args = self.native_pack(link=str(external))
        self.assertEqual(harvest.byte_bound_inputs(finalized), [])
        self.assertEqual(finalized["closure"]["links"]["view"]["kind"], "directory")
        self.verified(**args)
        manifest = ow.read_json(self.offload().dir / ow.MANIFEST_NAME)
        self.assertEqual(ow.restore_gaps(ow.parse_record_manifest(
            self.manifest.read_bytes(), self.record), manifest["externals"]), [])
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
        self.assertFalse(any((self.record / rel).exists() for rel in self.files))
        self.record.rmdir()
        external.rmdir()  # a fresh restore host lacks this MBP-only empty directory.
        for source in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            with self.subTest(source=str(source)):
                with self.assertRaisesRegex(harvest.OffloadRefused, "external link view resolves differently"):
                    harvest.unpack(source, finalized=finalized, finalized_sha256=self.manifest_sha)
                self.assertFalse(self.record.exists())
                self.assertFalse(external.exists())
                # Control: this single missing topology prerequisite explains
                # the failure; the same verified archive restores all bytes.
                external.mkdir()
                harvest.unpack(source, finalized=finalized, finalized_sha256=self.manifest_sha)
                for rel, raw in self.files.items():
                    self.assertEqual((self.record / rel).read_bytes(), raw)
                self.assertEqual(os.readlink(self.record / "view"), str(external))
                shutil.rmtree(self.record)
                external.rmdir()

    def test_witness_session_external_subtree_is_accepted_but_native_restore_refuses(self):
        relative = ".external/operator-notes.txt"
        self.put_file(relative, b"ordinary session bytes under the transport's hidden prefix")
        harvest, finalized, args = self.native_pack()
        self.assertEqual(harvest.byte_bound_inputs(finalized), [])
        self.assertIn(relative, finalized["entries"])
        self.verified(**args)
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
        self.assertFalse((self.record / relative).exists())
        self.record.rmdir()
        for source in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            with self.subTest(source=str(source)):
                with self.assertRaisesRegex(harvest.OffloadRefused, "external payload entry not in the manifest"):
                    harvest.unpack(source, finalized=finalized, finalized_sha256=self.manifest_sha)
                self.assertFalse(self.record.exists())


if __name__ == "__main__":
    unittest.main()
