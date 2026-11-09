"""Independent final deletion review of 66b7da341..ed3b375b7.

Synthetic only: real hashes, rename/unlink and the local gate; fake volume/cloud.
Inverted by the builder: the former ``witness`` tests now assert the required safe behavior.
Native harvest code comes from the already pinned, digest-checked Git blob.
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

from tests import test_offload_delta_fixes as delta

ow = delta.ow


class Recovery(delta.Base):
    def test_detached_raw_object_is_rehashed_and_preserved_after_crash(self):
        self.verified(codec="gzip")
        journal = self.crash_raw(count=0)
        root, qdir = next(iter(journal["quarantine"].items()))
        detached, = Path(qdir).iterdir()
        index = int(detached.name.split("-", 1)[0])
        home = Path(root) / journal["inventory"][index]["path"]
        unique = b"recovery wrote a different, unbacked object\n"
        detached.write_bytes(unique)
        with self.assertRaisesRegex(ow.Mismatch, "quarantine_holds_unbound_object"):
            self.offload().release()
        self.assertEqual(home.read_bytes(), unique)
        self.assertFalse(detached.exists())
        self.assertFalse((self.state / "w1-test/released.json").exists())

    def test_resume_preserves_both_a_quarantined_mismatch_and_new_home(self):
        self.verified(codec="gzip")
        journal = self.crash_raw(count=0)
        root, qdir = next(iter(journal["quarantine"].items()))
        detached, = Path(qdir).iterdir()
        index = int(detached.name.split("-", 1)[0])
        home = Path(root) / journal["inventory"][index]["path"]
        detached.write_bytes(b"unbacked quarantine recovery")
        home.write_bytes(b"unbacked newly published home")
        with self.assertRaisesRegex(ow.Mismatch, "quarantine_holds_unbound_object"):
            self.offload().release()
        self.assertEqual(detached.read_bytes(), b"unbacked quarantine recovery")
        self.assertEqual(home.read_bytes(), b"unbacked newly published home")

    def test_preexisting_quarantine_name_collision_preserves_unbound_content(self):
        self.verified(codec="gzip")
        qdir = self.record.parent / ".jw-offload-q-w1-test-c0111de0"
        qdir.mkdir()
        unique = b"unbacked file already at the proposed quarantine name"
        other = qdir / "unrelated-recovery.bin"
        other.write_bytes(unique)
        off = self.offload()
        real_quarantines = off._quarantines

        def collide(journal, path, roots):
            # Same journal that production writes before creating the directory; no row/digest forgery.
            with mock.patch.object(ow.secrets, "token_hex", return_value="c0111de0"):
                return real_quarantines(journal, path, roots)

        off._quarantines = collide
        with self.assertRaisesRegex(ow.Mismatch, "quarantine_holds_unbound_object"):
            off.release()
        self.assertEqual(other.read_bytes(), unique)
        self.assert_nothing_deleted()

    def test_cross_device_rename_refuses_without_copy_or_unlink(self):
        self.verified(codec="gzip")
        real_rename = os.rename
        attempted = []

        def exdev(source, destination, *args, **kwargs):
            if "src_dir_fd" in kwargs:
                attempted.append(str(source))
                raise OSError(errno.EXDEV, "synthetic mount boundary")
            return real_rename(source, destination, *args, **kwargs)

        off = self.offload()
        with mock.patch.object(ow.os, "rename", side_effect=exdev), \
                mock.patch.object(off, "unlink", wraps=off.unlink) as unlink:
            with self.assertRaises(OSError) as caught:
                off.release()
            self.assertEqual(caught.exception.errno, errno.EXDEV)
            unlink.assert_not_called()
        self.assertEqual(len(attempted), 1)
        self.assert_nothing_deleted()
        self.assertTrue(self.offload().release()["resumed"])

    def test_changed_device_is_refused_before_any_detach(self):
        self.verified(codec="gzip")
        real_lstat = os.lstat

        def different_device(path, *args, **kwargs):
            info = real_lstat(path, *args, **kwargs)
            if ".jw-offload-q-" in str(path):
                values = list(info)
                values[2] = info.st_dev + 1
                return os.stat_result(values)
            return info

        with mock.patch.object(ow.os, "lstat", side_effect=different_device):
            with self.assertRaisesRegex(ow.Refusal, "quarantine_cross_device"):
                self.offload().release()
        self.assert_nothing_deleted()

    def test_truncated_raw_and_pack_journals_preserve_pending_objects(self):
        self.verified(codec="gzip")
        off = self.offload()
        original = off.unlink

        def crash_pack(path, *args, **kwargs):
            if Path(path).name.endswith(".tar.gz"):
                raise OSError(errno.EIO, "synthetic crash after pack detach")
            return original(path, *args, **kwargs)

        off.unlink = crash_pack
        with self.assertRaises(OSError):
            off.release()
        raw_path, pack_path = off.dir / "deleting.json", off.dir / "deleting-parts.json"
        raw_bytes, pack_bytes = raw_path.read_bytes(), pack_path.read_bytes()
        pack_journal = json.loads(pack_bytes)
        detached = [p for qdir in pack_journal["quarantine"].values() for p in Path(qdir).iterdir()]
        self.assertEqual(len(detached), 1)
        kept = detached[0].read_bytes()
        for broken in (raw_path, pack_path):
            with self.subTest(journal=broken.name):
                broken.write_bytes(b'{"window_id":"w1-test",')
                with self.assertRaises(json.JSONDecodeError):
                    self.offload().release()
                self.assertEqual(detached[0].read_bytes(), kept)
                raw_path.write_bytes(raw_bytes)
                pack_path.write_bytes(pack_bytes)
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")

    def test_wrong_window_raw_journal_is_refused_before_quarantine_drain(self):
        self.verified(codec="gzip")
        journal = self.crash_raw(count=0)
        qdir = Path(next(iter(journal["quarantine"].values())))
        detached, = qdir.iterdir()
        raw = detached.read_bytes()
        journal["window_id"] = "other-window"
        (self.state / "w1-test/deleting.json").write_bytes(ow.canonical(journal))
        with self.assertRaisesRegex(ow.Mismatch, "deletion_journal_mismatch"):
            self.offload().release()
        self.assertEqual(detached.read_bytes(), raw)

    def test_reused_released_window_id_does_not_delete_new_objects(self):
        self.verified(codec="gzip")
        old_result = self.offload().release()
        target = self.record / "new-window.txt"
        target.write_bytes(b"new unbacked record at a completed window's root")
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        part = self.state / "w1-test/parts" / manifest["parts"][0]["name"]
        part.write_bytes(b"new unbacked pack at the old pack path")
        self.assertEqual(self.offload().release(), old_result)
        self.assertEqual(target.read_bytes(), b"new unbacked record at a completed window's root")
        self.assertEqual(part.read_bytes(), b"new unbacked pack at the old pack path")
        # A new run with a changed finalize pin must refuse rather than replace the old state.
        self.manifest.write_text(f"{ow.sha_bytes(target.read_bytes())}  new-window.txt\n")
        self.assertEqual(self.run_offload(record_manifest_sha256=ow.sha_bytes(self.manifest.read_bytes())), 3)


class Locking(delta.Base):
    def test_nested_same_process_lock_still_excludes_a_fresh_process(self):
        script = (
            "import pathlib, sys\n"
            "from tests.test_offload_window import ow\n"
            "try:\n"
            "    with ow.state_lock(pathlib.Path(sys.argv[1])): pass\n"
            "except ow.Refusal as exc:\n"
            "    print(str(exc)); sys.exit(0)\n"
            "sys.exit(10)\n"
        )
        with ow.state_lock(self.state):
            with ow.state_lock(self.state):
                result = subprocess.run([sys.executable, "-B", "-c", script, str(self.state)],
                                        cwd=delta.fixtures.ROOT, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "offload_already_running")
            self.assertIn("offload_running", ow.triage(self.state, "next-window", self.clock() + 600, 120)["reasons"])
        with ow.state_lock(self.state):
            pass

    @unittest.skipUnless(hasattr(os, "fork"), "POSIX fork required")
    def test_fork_child_does_not_inherit_lock_ownership(self):
        # S1-L01 inverted: the re-entrant registry is per owning pid, so a forked child takes its own flock.
        with ow.state_lock(self.state):
            pid = os.fork()
            if pid == 0:
                try:
                    with ow.state_lock(self.state):
                        os._exit(0)  # bypassed process exclusion
                except ow.Refusal:
                    os._exit(10)
                except BaseException:
                    os._exit(11)
            _, status = os.waitpid(pid, 0)
            self.assertTrue(os.WIFEXITED(status))
            self.assertEqual(os.WEXITSTATUS(status), 10)  # the child is refused while the parent holds it


@unittest.skipUnless(ow.zstd_cli(), "native harvest packs require zstd")
class RestoreClosure(delta.Base):
    """S1-F01 inverted (harvest-off @ d5dc1198c): an empty external directory target travels as a bound
    directory entry (`external_directories`) and the native restore recreates it on a fresh host."""

    def test_empty_external_directory_restores_from_each_copy(self):
        self.empty_directory_restore(with_ledger=False)

    def test_complete_carried_inputs_restore_an_empty_link_target(self):
        self.empty_directory_restore(with_ledger=True)

    def empty_directory_restore(self, *, with_ledger):
        outside = self.tmp / "mbp/empty-external-inputs"
        outside.mkdir()
        ledger = self.tmp / "mbp/synthetic-ledger.json"
        if with_ledger:
            ledger.write_bytes(b'{"synthetic_ledger":true}\n')
        harvest, finalized, args = self.native_pack(link=str(outside), inputs=(ledger,) if with_ledger else ())
        closure_link = finalized["closure"]["links"]["view"]
        self.assertEqual((closure_link["class"], closure_link["kind"], closure_link["files"]), ("bytes", "directory", []))
        self.assertEqual(harvest.byte_bound_inputs(finalized), [str(ledger)] if with_ledger else [])
        self.assertEqual(harvest.bound_directories(finalized), [str(outside)])
        self.assertEqual(ow.bound_directories(finalized), harvest.bound_directories(finalized))
        self.verified(**args)
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        self.assertEqual(manifest["external_directories"], [str(outside)])
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
        self.record.rmdir()
        for source in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            with self.subTest(copy=source):
                outside.rmdir()  # a fresh restore host has none of the MBP's external paths
                if with_ledger:
                    ledger.unlink()
                harvest.unpack(source, finalized=finalized, finalized_sha256=self.manifest_sha)
                self.assertTrue(outside.is_dir() and not any(outside.iterdir()))
                self.assertEqual(os.readlink(self.record / "view"), str(outside))
                if with_ledger:
                    self.assertEqual(ledger.read_bytes(), b'{"synthetic_ledger":true}\n')
                for rel, raw in self.files.items():
                    self.assertEqual((self.record / rel).read_bytes(), raw)
                shutil.rmtree(self.record)

    def test_pack_without_the_bound_directory_list_is_refused(self):
        outside = self.tmp / "mbp/empty-external-inputs"
        outside.mkdir()
        _, _, args = self.native_pack(link=str(outside))
        path = self.pack_dir / ow.HARVEST_MANIFEST
        doc = json.loads(path.read_text())
        doc["external_directories"] = []  # an older pack that cannot recreate the empty target
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
        self.assertEqual(self.run_offload(**args), 2)
        self.assertIn("harvest_pack_not_restorable:external_directories", self.span()["reason"])
        self.assertEqual(self.transport.calls, [])
        self.assert_nothing_deleted()


class DeclaredResidual(delta.Base):
    def test_same_inode_write_without_mtime_reset_is_rehashed_and_preserved(self):
        self.verified(codec="gzip")
        target = self.record / "custody/night/chain-stages.jsonl"
        before = target.stat()
        descriptor = os.open(target, os.O_RDWR)
        self.addCleanup(os.close, descriptor)
        replacement = b"!" * before.st_size
        real_rename, changed = os.rename, []

        def write_after_last_stat(source, destination, *args, **kwargs):
            if source == target.name and "src_dir_fd" in kwargs and not changed:
                os.pwrite(descriptor, replacement, 0)
                self.assertNotEqual(os.fstat(descriptor).st_mtime_ns, before.st_mtime_ns)
                changed.append(True)
            return real_rename(source, destination, *args, **kwargs)

        with mock.patch.object(ow.os, "rename", side_effect=write_after_last_stat):
            with self.assertRaisesRegex(ow.Mismatch, "changed_during_deletion"):
                self.offload().release()
        self.assertTrue(changed)
        self.assertEqual(target.read_bytes(), replacement)

    def test_accepted_residual_same_inode_write_and_mtime_reset_after_last_stat(self):
        """The LOW residual both delta2 seats accepted (runbook §1c): an in-place writer that already holds an
        fd and resets mtime in the instant before the detach is not detected. This documents it."""
        self.verified(codec="gzip")
        target = self.record / "custody/night/chain-stages.jsonl"
        before = target.stat()
        descriptor = os.open(target, os.O_RDWR)
        self.addCleanup(os.close, descriptor)
        replacement = b"!" * before.st_size
        real_rename, changed = os.rename, []

        def write_after_last_stat(source, destination, *args, **kwargs):
            if source == target.name and "src_dir_fd" in kwargs and not changed:
                # Only real writes through a pre-opened fd; no hash, receipt or stat result is forged.
                os.pwrite(descriptor, replacement, 0)
                os.utime(descriptor, ns=(before.st_atime_ns, before.st_mtime_ns))
                changed.append(True)
            return real_rename(source, destination, *args, **kwargs)

        with mock.patch.object(ow.os, "rename", side_effect=write_after_last_stat):
            self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
        self.assertTrue(changed)
        self.assertFalse(target.exists())
        self.assertEqual(os.fstat(descriptor).st_nlink, 0)
        self.assertEqual(os.pread(descriptor, before.st_size, 0), replacement)
        # Both real payloads contain only the finalized bytes at that path.
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        relative = target.relative_to(self.record).as_posix()
        part_name = next(row["part"] for row in manifest["files"] if row["path"] == relative)
        for copy in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            entries = self.payload_names(copy / part_name, manifest["codec"])
            self.assertEqual(entries[relative], self.files[relative])


if __name__ == "__main__":
    unittest.main()
