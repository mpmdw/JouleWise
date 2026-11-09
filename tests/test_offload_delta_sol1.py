"""Independent delta review of 175f0c8b9..66b7da341; synthetic objects only.

Passing ``test_witness_*`` tests demonstrate unsafe behavior in the candidate,
not safe-behavior regressions. Hooks schedule ordinary filesystem changes at
specific boundaries; they do not forge receipts, digests, or guard results.
No network, SSH, real volumes, measurement data, or model weights are used.
"""
from __future__ import annotations

import contextlib
import fcntl
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import types
import unittest
from unittest import mock

from tests import test_offload_window as fixtures

ow = fixtures.ow
HARVEST_BLOB = "d279ab46f8cb3eae288545c8265948e325b24eba"
HARVEST_SHA256 = "1ba0cc107aaa8c0b63b598ed46e0b89b97d04a314d513f54f40d7b9964e28293"


def native_harvest():
    result = subprocess.run(["git", "cat-file", "blob", HARVEST_BLOB],
                            cwd=fixtures.ROOT, capture_output=True, check=False)
    if result.returncode or fixtures.sha(result.stdout) != HARVEST_SHA256:
        raise unittest.SkipTest("pinned harvest-off code object unavailable")
    module = types.ModuleType("delta_sol1_native_harvest")
    exec(compile(result.stdout, "git-blob:" + HARVEST_BLOB, "exec"), module.__dict__)
    return module


class ReviewFixture(fixtures.Fixture):
    def verified(self, **over):
        self.assertEqual(self.run_offload(**over), 0)
        self.assertEqual(self.confirm_second_copy(), ["w1-test"])

    def release_cli(self, *extra, runner=None):
        with mock.patch.object(ow, "_transport", return_value=runner or self.transport), \
                mock.patch.object(ow, "default_state_probe", return_value=lambda: self.probe_state), \
                mock.patch.object(ow.time, "time", self.clock), \
                mock.patch.object(ow.time, "monotonic", self.clock), \
                contextlib.redirect_stdout(io.StringIO()):
            return ow.main(["release", "--state-root", str(self.state), "--window-id", "w1-test", *extra])

    def interrupt_raw_after_one_unlink(self):
        off = self.offload()
        count = 0

        def crash(path, *args, **kwargs):
            nonlocal count
            if count == 1:
                raise OSError(5, "synthetic crash after first raw unlink")
            os.unlink(path, *args, **kwargs)
            count += 1

        off.unlink = crash
        with self.assertRaises(OSError):
            off.release()
        journal = ow.read_json(off.dir / "deleting.json")
        self.assertEqual(journal["state"], "deleting")
        self.assertEqual(count, 1)
        return journal

    def part_bytes(self, part_path):
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        with ow.decompressed(manifest["codec"], part_path) as stream:
            with tarfile.open(fileobj=stream, mode="r|") as archive:
                return {m.name: archive.extractfile(m).read() for m in archive if m.isreg()}


class ClosedFindingControls(ReviewFixture):
    def test_different_same_size_duplicate_refuses_on_first_attempt_and_resume(self):
        duplicate = self.tmp / "mbp/duplicate"
        shutil.copytree(self.record, duplicate)
        rel = "custody/night/chain-stages.jsonl"
        unique = b"!" * len(self.files[rel])
        (duplicate / rel).write_bytes(unique)
        self.verified(duplicate_root=[duplicate])
        for _ in range(2):
            with self.assertRaisesRegex(ow.Mismatch, "content_differs_from_bound_digest"):
                self.offload().release()
        self.assertEqual((duplicate / rel).read_bytes(), unique)
        self.assert_nothing_deleted()

    def test_crash_mid_unlink_then_changed_duplicate_is_preserved(self):
        duplicate = self.tmp / "mbp/duplicate"
        shutil.copytree(self.record, duplicate)
        self.verified(duplicate_root=[duplicate])
        self.interrupt_raw_after_one_unlink()
        rel = "members/m02/raw/powermetrics.plist"
        path = duplicate / rel
        info = path.stat()
        unique = b"!" * info.st_size
        path.write_bytes(unique)
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
        remaining = {p for root in (self.record, duplicate) for p in root.rglob("*") if p.is_file()}
        with self.assertRaisesRegex(ow.Mismatch, "content_differs_from_bound_digest"):
            self.offload().release()
        self.assertEqual(path.read_bytes(), unique)
        self.assertTrue(all(p.exists() for p in remaining))

    def test_crash_mid_unlink_resumes_without_changes(self):
        self.verified()
        self.interrupt_raw_after_one_unlink()
        self.assertTrue(self.offload().release()["resumed"])
        self.assertFalse(any((self.record / rel).exists() for rel in self.files))

    def test_reused_legacy_pack_is_checked_before_any_raw_deletion(self):
        self.verified(codec="gzip")
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        path = self.state / "w1-test/parts" / manifest["parts"][0]["name"]
        unique = b"next window's sole pack bytes"
        path.write_bytes(unique)
        with self.assertRaisesRegex(ow.Mismatch, "local_pack_changed"):
            self.offload().release()
        self.assertEqual(path.read_bytes(), unique)
        self.assert_nothing_deleted()

    def test_cli_release_lock_timing_and_deadline_are_installed(self):
        self.verified()
        fd = os.open(self.state / ".lock", os.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(self.release_cli(), 2)
        finally:
            os.close(fd)
        observed = []

        def slow(command, **kwargs):
            if command.startswith("receipts "):
                self.assertIsNotNone(kwargs["timeout"])
                observed.append(ow.triage(self.state, "next-window", self.clock() + 60, 120))
                self.clock.t += 200
            return self.transport(command, **kwargs)

        self.assertEqual(self.release_cli("--deadline-epoch", str(self.clock() + 150), runner=slow), 4)
        self.assertIn("offload_running", observed[0]["reasons"])
        after = ow.triage(self.state, "next-window", self.clock() + 60, 120)
        self.assertIn("offload_activity_inside_dwell_margin", after["reasons"])
        self.assertEqual(ow.read_json(self.state / "w1-test/timing/release-span.json")["rc"], 4)
        self.assert_nothing_deleted()

    def test_failed_ps_result_cannot_admit_release(self):
        agents = self.tmp / "synthetic-launch-agents"
        agents.mkdir()
        with mock.patch.object(ow.subprocess, "run", return_value=subprocess.CompletedProcess(
                ["/bin/ps"], 1, stdout="", stderr="synthetic census failure")):
            state = ow.default_state_probe(launch_agents=agents)()
        off = self.offload()
        off.state_probe = lambda: state
        with self.assertRaisesRegex(ow.Refusal, "process_census_failed"):
            off.check_quiet_allowed()

    def test_reused_window_id_cannot_replace_the_manifest_or_release_new_content(self):
        self.verified()
        off = self.offload()
        sealed_manifest = (off.dir / ow.MANIFEST_NAME).read_bytes()
        rel = "custody/night/chain-stages.jsonl"
        self.put_file(rel, b"a new revision in a reused window namespace\n")
        self.assertEqual(self.run_offload(), 3)
        self.assertEqual((off.dir / ow.MANIFEST_NAME).read_bytes(), sealed_manifest)
        with self.assertRaises(ow.Mismatch):
            off.release()
        self.assertEqual((self.record / rel).read_bytes(), self.files[rel])

    def test_partial_upload_has_no_receipt_and_cannot_release(self):
        self.transport.cut_put_after = 200
        self.assertEqual(self.run_offload(), 5)
        with self.assertRaises(ow.Refusal):
            self.offload().release()
        self.assert_nothing_deleted()
        self.assertFalse((self.store / "windows/w1-test" / ow.AIR_RECEIPT).exists())
        self.assertEqual(self.run_offload(), 0)

    def test_pressure_release_refuses_a_missing_retained_part(self):
        self.assertEqual(self.run_offload(), 0)
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        (self.state / "w1-test/parts" / manifest["parts"][0]["name"]).unlink()
        with self.assertRaisesRegex(ow.Mismatch, "local_part_missing"):
            self.offload().release(pressure_compressed_local=True)
        self.assert_nothing_deleted()

    def test_witness_duplicate_root_alias_causes_partial_failure_but_resumes(self):
        self.verified(duplicate_root=[self.record])
        with self.assertRaises(FileNotFoundError):
            self.offload().release()
        self.assertEqual(ow.read_json(self.state / "w1-test/deleting.json")["state"], "deleting")
        self.assertTrue(self.offload().release()["resumed"])

    def test_witness_raw_replacement_after_last_stat_is_unlinked(self):
        self.verified(codec="gzip")
        target = self.record / "custody/night/chain-stages.jsonl"
        unique = b"new content from a concurrent atomic file publisher\n"
        changed = False
        off = self.offload()

        def publish_before_unlink(leaf, *args, **kwargs):
            nonlocal changed
            if not changed and leaf == target.name:
                replacement = target.with_name("atomic-output.tmp")
                replacement.write_bytes(unique)
                os.replace(replacement, target)
                changed = True
            return os.unlink(leaf, *args, **kwargs)

        off.unlink = publish_before_unlink
        result = off.release()
        self.assertTrue(changed)
        self.assertEqual(result["rule"], "two_verified_copies")
        self.assertFalse(target.exists())
        for root in (self.store / "windows/w1-test/raw",):
            self.assertNotEqual((root / target.relative_to(self.record)).read_bytes(), unique)
        manifest = ow.read_json(off.dir / ow.MANIFEST_NAME)
        for row in manifest["parts"]:
            for root in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
                self.assertNotIn(unique, self.part_bytes(root / row["name"]).values())


@unittest.skipUnless(ow.zstd_cli(), "consumed harvest packs require zstd")
class HarvestBoundaryWitnesses(ReviewFixture):
    def next_pack(self):
        """A real tiny native pack, published later into the caller's reused directory."""
        harvest = native_harvest()
        source = self.tmp / "mbp/next-window-source"
        source.mkdir()
        (source / "next.txt").write_bytes(b"a different window's synthetic contents\n")
        finalized = harvest.finalized_manifest(source)
        output = self.tmp / "mbp/next-window-pack"
        harvest.pack(source, output, finalized=finalized, threads=1)
        return output

    def packed(self, *, link=False):
        harvest = native_harvest()
        if link:
            (self.record / "view").symlink_to("members/m01/outputs/align_turns.jsonl")
        finalized = harvest.finalized_manifest(self.record)
        raw = json.dumps(finalized, sort_keys=True, separators=(",", ":")).encode()
        self.manifest.write_bytes(raw)
        self.manifest_sha = fixtures.sha(raw)
        self.pack_dir = self.tmp / "mbp/shared-harvest-output/offload"
        harvest.pack(self.record, self.pack_dir, finalized=finalized, threads=1)
        return dict(harvest_pack=self.pack_dir, pack=False)

    def test_witness_materialized_link_is_deleted_without_size_or_digest_check(self):
        self.verified(**self.packed(link=True))
        target = self.record / "view"
        unique = b"a copied regular file replacing a formerly listed symlink\n"
        off = self.offload()
        changed = False

        def materialize_after_first_unlink(leaf, *args, **kwargs):
            nonlocal changed
            os.unlink(leaf, *args, **kwargs)
            if not changed:
                target.unlink()
                target.write_bytes(unique)
                changed = True

        off.unlink = materialize_after_first_unlink
        result = off.release()
        self.assertTrue(changed)
        self.assertEqual(result["links_deleted"], 1)
        self.assertFalse(target.exists())
        for root in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            self.assertNotIn(unique, self.part_bytes(root / ow.HARVEST_PAYLOAD).values())

    def test_witness_reused_pack_manifest_after_payload_unlink_is_deleted(self):
        self.verified(**self.packed())
        target = self.pack_dir / ow.HARVEST_MANIFEST
        next_pack = self.next_pack()
        unique = (next_pack / ow.HARVEST_MANIFEST).read_bytes()
        changed = False
        off = self.offload()

        def replace_after_payload_unlink(path, *args, **kwargs):
            nonlocal changed
            os.unlink(path, *args, **kwargs)
            if isinstance(path, Path) and path == self.pack_dir / ow.HARVEST_PAYLOAD:
                for name in (ow.HARVEST_PAYLOAD, ow.HARVEST_MANIFEST):
                    os.replace(next_pack / name, self.pack_dir / name)
                changed = True

        off.unlink = replace_after_payload_unlink
        self.assertEqual(off.release()["rule"], "two_verified_copies")
        self.assertTrue(changed)
        self.assertFalse(target.exists())
        self.assertTrue((self.pack_dir / ow.HARVEST_PAYLOAD).exists())
        self.assertFalse((next_pack / ow.HARVEST_MANIFEST).exists())
        for root in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            self.assertNotEqual((root / ow.HARVEST_MANIFEST).read_bytes(), unique)

    def test_crash_after_payload_unlink_then_reused_manifest_is_preserved_on_resume(self):
        self.verified(**self.packed())
        off = self.offload()

        def crash_after_payload_unlink(path, *args, **kwargs):
            os.unlink(path, *args, **kwargs)
            if isinstance(path, Path) and path == self.pack_dir / ow.HARVEST_PAYLOAD:
                raise OSError(5, "synthetic crash during pack cleanup")

        off.unlink = crash_after_payload_unlink
        with self.assertRaises(OSError):
            off.release()
        self.assertEqual(ow.read_json(off.dir / "deleting-parts.json")["state"], "deleting")
        next_pack = self.next_pack()
        unique = (next_pack / ow.HARVEST_MANIFEST).read_bytes()
        for name in (ow.HARVEST_PAYLOAD, ow.HARVEST_MANIFEST):
            os.replace(next_pack / name, self.pack_dir / name)
        with self.assertRaisesRegex(ow.Mismatch, "local_pack_changed"):
            self.offload().release()
        self.assertEqual((self.pack_dir / ow.HARVEST_MANIFEST).read_bytes(), unique)

    def test_witness_resumed_pack_hashes_open_old_inode_but_unlinks_replacement(self):
        self.verified(**self.packed())
        payload = self.pack_dir / ow.HARVEST_PAYLOAD
        off = self.offload()

        def crash_before_pack_unlink(path, *args, **kwargs):
            if isinstance(path, Path) and path == payload:
                raise OSError(5, "synthetic crash before first pack unlink")
            return os.unlink(path, *args, **kwargs)

        off.unlink = crash_before_pack_unlink
        with self.assertRaises(OSError):
            off.release()
        self.assertEqual(ow.read_json(off.dir / "deleting-parts.json")["state"], "deleting")
        original = payload.read_bytes()
        next_pack = self.next_pack()
        unique = (next_pack / ow.HARVEST_PAYLOAD).read_bytes()
        self.assertNotEqual(unique, original)
        real_open = os.open
        replaced = False

        def open_old_then_publish(path, flags, *args, **kwargs):
            nonlocal replaced
            fd = real_open(path, flags, *args, **kwargs)
            if not replaced and Path(path) == payload and flags & os.O_ACCMODE == os.O_RDONLY:
                # A copier publishes the next payload while the re-hash owns an
                # FD of the old inode. Actual hashing still reads the old bytes.
                os.replace(next_pack / ow.HARVEST_PAYLOAD, payload)
                replaced = True
            return fd

        with mock.patch.object(ow.os, "open", side_effect=open_old_then_publish):
            result = self.offload().release()
        self.assertTrue(replaced)
        self.assertEqual(result["rule"], "two_verified_copies")
        self.assertFalse(payload.exists())
        self.assertFalse((next_pack / ow.HARVEST_PAYLOAD).exists())
        for root in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            self.assertEqual((root / ow.HARVEST_PAYLOAD).read_bytes(), original)
            self.assertNotEqual((root / ow.HARVEST_PAYLOAD).read_bytes(), unique)

    def test_witness_pressure_release_loses_its_retained_copy_during_raw_deletion(self):
        self.assertEqual(self.run_offload(**self.packed()), 0)
        payload = self.pack_dir / ow.HARVEST_PAYLOAD
        original = payload.read_bytes()
        next_pack = self.next_pack()
        off = self.offload()
        changed = False

        def reuse_after_first_raw_unlink(leaf, *args, **kwargs):
            nonlocal changed
            os.unlink(leaf, *args, **kwargs)
            if not changed:
                for name in (ow.HARVEST_PAYLOAD, ow.HARVEST_MANIFEST):
                    os.replace(next_pack / name, self.pack_dir / name)
                changed = True

        off.unlink = reuse_after_first_raw_unlink
        result = off.release(pressure_compressed_local=True)
        self.assertEqual(result["rule"], "pressure_compressed_local")
        self.assertTrue(changed)
        self.assertFalse(any((self.record / rel).exists() for rel in self.files))
        self.assertNotEqual(payload.read_bytes(), original)
        self.assertEqual((self.store / "inbox/w1-test" / ow.HARVEST_PAYLOAD).read_bytes(), original)
        self.assertFalse((self.store / "second/w1-test" / ow.SECOND_RECEIPT).exists())
        self.assertFalse((self.icloud / "w1-test").exists())

    def test_native_restore_recreates_all_external_terminal_bytes_from_each_copy(self):
        harvest = native_harvest()
        night = self.tmp / "mbp/external-terminal"
        night.mkdir(parents=True)
        external_bytes = {}
        for rel in tuple(self.files):
            if rel.startswith("custody/night/"):
                path = night / Path(rel).name
                external_bytes[path] = self.files.pop(rel)
                (self.record / rel).rename(path)
        inputs = tuple(sorted(external_bytes))
        finalized = harvest.finalized_manifest(self.record, inputs=inputs)
        raw = json.dumps(finalized, sort_keys=True, separators=(",", ":")).encode()
        self.manifest.write_bytes(raw)
        self.manifest_sha = fixtures.sha(raw)
        pack_dir = self.tmp / "mbp/native-pack"
        harvest.pack(self.record, pack_dir, finalized=finalized, external=inputs, threads=1)
        args = dict(harvest_pack=pack_dir, pack=False, terminal=str(night / "result.json"))
        self.verified(**args)
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
        for source in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            shutil.rmtree(self.record)
            for path in external_bytes:
                path.unlink()
            harvest.unpack(source, finalized=finalized, finalized_sha256=self.manifest_sha)
            for path, expected in external_bytes.items():
                self.assertEqual(path.read_bytes(), expected)
            for rel, expected in self.files.items():
                self.assertEqual((self.record / rel).read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()
