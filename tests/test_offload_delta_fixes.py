"""Required properties from the Sol delta re-review seats on 66b7da341 (both HOLD).

Seat 1: docs/ops/AIR-OFFLOAD-DELTA-sol1.md on ops/2026-11-08-offload-delta-sol1 (S1-D01..D03, LOW);
seat 2: docs/ops/AIR-OFFLOAD-DELTA-sol2.md on ops/2026-11-08-offload-delta-sol2 (D1..D3, LOW). Each of
their defect-reproducing witnesses is inverted into the safe behavior; their controls are kept. Hooks
schedule ordinary concurrent filesystem changes (a producer reusing a pack path, a sync materializing a
file, a crash); nothing forges a receipt, digest or journal. Everything is synthetic.
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
import unittest
from unittest import mock

from tests import test_offload_window as fixtures
from tests.test_offload_review_fixes import native_harvest

ow = fixtures.ow


class Base(fixtures.Fixture):
    def verified(self, **over):
        self.assertEqual(self.run_offload(**over), 0)
        self.assertEqual(self.confirm_second_copy(), ["w1-test"])

    def release_cli(self, *extra, runner=None):
        with mock.patch.object(ow, "_transport", return_value=runner or self.transport), \
                mock.patch.object(ow, "default_state_probe", return_value=lambda: self.probe_state), \
                mock.patch.object(ow.time, "time", self.clock), mock.patch.object(ow.time, "monotonic", self.clock), \
                contextlib.redirect_stdout(io.StringIO()):
            return ow.main(["release", "--state-root", str(self.state), "--window-id", "w1-test", *extra])

    def crash_raw(self, count=2):
        off, deleted = self.offload(), []

        def interrupted(path, **kwargs):
            if len(deleted) == count:
                raise OSError(5, "synthetic crash mid-unlink")
            os.unlink(path, **kwargs)
            deleted.append(str(path))
        off.unlink = interrupted
        with self.assertRaises(OSError):
            off.release()
        return ow.read_json(self.state / "w1-test/deleting.json")

    def payload_names(self, part_path, codec):
        with ow.decompressed(codec, part_path) as stream:
            with tarfile.open(fileobj=stream, mode="r|") as archive:
                return {m.name: archive.extractfile(m).read() for m in archive if m.isreg()}

    def native_pack(self, *, inputs=(), duplicate_roots=(), link=None):
        harvest = native_harvest()
        if link is not None:
            (self.record / "view").symlink_to(link)
        finalized = harvest.finalized_manifest(self.record, inputs=tuple(inputs))
        raw = json.dumps(finalized, sort_keys=True, separators=(",", ":")).encode()
        self.manifest.write_bytes(raw)
        self.manifest_sha = fixtures.sha(raw)
        self.pack_dir = self.tmp / "mbp/harvest-output/offload"
        harvest.pack(self.record, self.pack_dir, finalized=finalized, threads=1,
                     external=tuple(harvest.byte_bound_inputs(finalized)))
        return harvest, finalized, dict(harvest_pack=self.pack_dir, pack=False, duplicate_root=list(duplicate_roots))

    def next_pack(self, harvest, name="next"):
        source = self.tmp / f"mbp/{name}-window-source"
        source.mkdir()
        (source / "next.txt").write_bytes(b"a different window's synthetic, not-yet-offloaded contents\n")
        output = self.tmp / f"mbp/{name}-window-pack"
        harvest.pack(source, output, finalized=harvest.finalized_manifest(source), threads=1)
        return output


class Lifecycle(Base):
    """Seat 2 LegacyChecks and seat 1 ClosedFindingControls, kept."""

    def test_crash_after_detach_resumes_with_fresh_receipts(self):
        self.verified()
        self.assertEqual(self.crash_raw()["state"], "deleting")
        before = len([c for c in self.transport.calls if c.startswith("receipts ")])
        result = self.offload().release()
        self.assertTrue(result["resumed"])
        self.assertEqual(len([c for c in self.transport.calls if c.startswith("receipts ")]), before + 1)
        self.assertFalse(any((self.record / rel).exists() for rel in self.files))

    def test_resume_rehashes_a_same_metadata_duplicate(self):
        duplicate = self.tmp / "mbp/duplicate"
        shutil.copytree(self.record, duplicate)
        self.verified(duplicate_root=[duplicate])
        self.crash_raw()
        target = duplicate / "members/m01/outputs/align_turns.jsonl"
        info = target.stat()
        unique = b"X" * info.st_size
        target.write_bytes(unique)
        os.utime(target, ns=(info.st_atime_ns, info.st_mtime_ns))
        before = sum((self.record / rel).exists() for rel in self.files)
        with self.assertRaisesRegex(ow.Mismatch, "content_differs_from_bound_digest"):
            self.offload().release()
        self.assertEqual(target.read_bytes(), unique)
        self.assertEqual(sum((self.record / rel).exists() for rel in self.files), before)

    def test_air_decay_on_resume_prevents_more_unlinks(self):
        self.verified()
        self.crash_raw()
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        (self.store / "inbox/w1-test" / manifest["parts"][0]["name"]).write_bytes(b"synthetic storage decay")
        before = sum((self.record / rel).exists() for rel in self.files)
        with self.assertRaisesRegex(ow.Mismatch, "air_part_decayed"):
            self.offload().release()
        self.assertEqual(sum((self.record / rel).exists() for rel in self.files), before)

    def test_partial_pack_cannot_authorize_raw_deletion(self):
        self.transport.cut_put_after = 100
        self.assertEqual(self.run_offload(), 5)
        with self.assertRaisesRegex(ow.Refusal, "no_air_receipt"):
            self.offload().release()
        self.assert_nothing_deleted()
        self.assertEqual(self.run_offload(), 0)
        self.confirm_second_copy()
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")

    def test_cli_release_lock_timing_and_deadline(self):
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
        self.assertIn("offload_activity_inside_dwell_margin",
                      ow.triage(self.state, "next-window", self.clock() + 60, 120)["reasons"])
        self.assert_nothing_deleted()

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

    # LOW (both seats): a duplicate root that repeats or nests the record is refused up front.
    def test_duplicate_root_alias_is_refused_before_any_work(self):
        for roots in ([self.record], [self.record, self.record], [self.record / "members"]):
            with self.subTest(roots=roots):
                self.assertEqual(self.run_offload(duplicate_root=roots), 2)
                self.assertIn("duplicate_root_overlaps", self.span()["reason"])
                self.assert_nothing_deleted()

    # Lead ruling (b): the pressure route is gone; pressure never deletes.
    def test_pressure_never_deletes(self):
        self.assertEqual(self.run_offload(min_free_gib=1e9), 0)  # no second copy yet, under pressure
        self.assertTrue(self.span()["disk_pressure"])
        with self.assertRaises(TypeError):
            self.offload().release(pressure_compressed_local=True)
        with self.assertRaisesRegex(ow.Refusal, "second_copy_not_confirmed"):
            self.offload().release()
        self.assert_nothing_deleted()
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        for part in manifest["parts"]:
            self.assertTrue((self.state / "w1-test/parts" / part["name"]).exists())

    # LOW (both seats): a replacement published at the pathname right before the unlink is never deleted.
    def test_replacement_published_at_the_last_moment_is_preserved(self):
        self.verified(codec="gzip")
        target = self.record / "custody/night/chain-stages.jsonl"
        unique = b"new content from a concurrent atomic file publisher\n"
        off, changed = self.offload(), []

        def publish_before_unlink(path, *args, **kwargs):
            if not changed and Path(str(path)).name.endswith("chain-stages.jsonl"):
                tmp = target.with_name("atomic-output.tmp")
                tmp.write_bytes(unique)
                os.replace(tmp, target)
                changed.append(True)
            return os.unlink(path, *args, **kwargs)
        off.unlink = publish_before_unlink
        with contextlib.suppress(ow.Mismatch):
            off.release()
        self.assertTrue(changed)
        self.assertEqual(target.read_bytes(), unique)  # what the release removed was the detached old file


@unittest.skipUnless(ow.zstd_cli(), "native harvest packs require zstd")
class PackOwnership(Base):
    """D1 / S1-D01: pack cleanup removes only this window's sealed objects, detached and re-verified."""

    def test_new_native_pack_at_the_validated_path_is_kept(self):
        self.reuse(resumed=False)

    def test_resumed_cleanup_keeps_a_new_native_pack(self):
        self.reuse(resumed=True)

    def reuse(self, *, resumed):
        harvest, _, args = self.native_pack()
        self.verified(**args)
        off = self.offload()
        if resumed:
            def crash_before_pack_unlink(path, **kwargs):
                if isinstance(path, Path) and ".jw-offload-q-" in str(path) and "payload" in path.name:
                    raise OSError(5, "synthetic crash after pack journal, before pack unlink")
                os.unlink(path, **kwargs)
            off.unlink = crash_before_pack_unlink
            with self.assertRaises(OSError):
                off.release()
            self.assertEqual(ow.read_json(self.state / "w1-test/deleting-parts.json")["state"], "deleting")
            off = self.offload()
        next_pack = self.next_pack(harvest)
        retired = self.pack_dir.with_name("retired-w1-pack")
        replacements = {}

        def next_producer(path, **kwargs):
            if isinstance(path, Path) and not replacements and ".jw-offload-q-" in str(path):
                os.unlink(path, **kwargs)
                self.pack_dir.rename(retired)  # the producer moves the old output aside ...
                shutil.copytree(next_pack, self.pack_dir)  # ... and publishes the next pack at the same name
                replacements.update({p.name: p.read_bytes() for p in self.pack_dir.iterdir()})
                return
            os.unlink(path, **kwargs)
        off.unlink = next_producer
        with contextlib.suppress(ow.Mismatch):
            off.release()
        self.assertEqual(set(replacements), {ow.HARVEST_PAYLOAD, ow.HARVEST_MANIFEST})
        for name, raw in replacements.items():  # the next window's pack is intact at its path
            self.assertEqual((self.pack_dir / name).read_bytes(), raw)
        self.assertFalse((self.state / "w1-test/released.json").exists())

    def test_reused_pack_manifest_after_payload_removal_is_kept(self):
        harvest, _, args = self.native_pack()
        self.verified(**args)
        next_pack = self.next_pack(harvest)
        published = {}
        off = self.offload()

        def replace_after_payload_unlink(path, *a, **kw):
            os.unlink(path, *a, **kw)
            if isinstance(path, Path) and path.name.endswith(ow.HARVEST_PAYLOAD) and ".jw-offload-q-" in str(path):
                for name in (ow.HARVEST_PAYLOAD, ow.HARVEST_MANIFEST):
                    published[name] = (next_pack / name).read_bytes()
                    os.replace(next_pack / name, self.pack_dir / name)
        off.unlink = replace_after_payload_unlink
        with self.assertRaisesRegex(ow.Mismatch, "changed_during_deletion"):
            off.release()
        for name, raw in published.items():
            self.assertEqual((self.pack_dir / name).read_bytes(), raw)

    def test_crash_then_reused_manifest_is_preserved_on_resume(self):
        harvest, _, args = self.native_pack()
        self.verified(**args)
        off = self.offload()

        def crash_after_payload_unlink(path, *a, **kw):
            os.unlink(path, *a, **kw)
            if isinstance(path, Path) and path.name.endswith(ow.HARVEST_PAYLOAD):
                raise OSError(5, "synthetic crash during pack cleanup")
        off.unlink = crash_after_payload_unlink
        with self.assertRaises(OSError):
            off.release()
        next_pack = self.next_pack(harvest)
        unique = (next_pack / ow.HARVEST_MANIFEST).read_bytes()
        for name in (ow.HARVEST_PAYLOAD, ow.HARVEST_MANIFEST):
            os.replace(next_pack / name, self.pack_dir / name)
        with self.assertRaisesRegex(ow.Mismatch, "local_pack_changed"):
            self.offload().release()
        self.assertEqual((self.pack_dir / ow.HARVEST_MANIFEST).read_bytes(), unique)

    def test_resumed_hash_of_an_old_inode_never_deletes_the_replacement(self):
        harvest, _, args = self.native_pack()
        self.verified(**args)
        payload = self.pack_dir / ow.HARVEST_PAYLOAD
        off = self.offload()

        def crash_before_pack_unlink(path, *a, **kw):
            if isinstance(path, Path) and path.name.endswith(ow.HARVEST_PAYLOAD):
                raise OSError(5, "synthetic crash before the first pack unlink")
            return os.unlink(path, *a, **kw)
        off.unlink = crash_before_pack_unlink
        with self.assertRaises(OSError):
            off.release()
        # The crashed run left the detached payload in its quarantine; put it back to model a crash one step
        # earlier, so the resume re-hashes it at its path.
        journal = ow.read_json(self.state / "w1-test/deleting-parts.json")
        for qdir in journal["quarantine"].values():
            for entry in Path(qdir).iterdir():
                os.replace(entry, payload)
        next_pack = self.next_pack(harvest)
        unique = (next_pack / ow.HARVEST_PAYLOAD).read_bytes()
        real_open, replaced = os.open, []

        def open_old_then_publish(path, flags, *a, **kw):
            fd = real_open(path, flags, *a, **kw)
            if not replaced and str(path) == str(payload) and flags & os.O_ACCMODE == os.O_RDONLY:
                os.replace(next_pack / ow.HARVEST_PAYLOAD, payload)  # published while the hash owns the old fd
                replaced.append(True)
            return fd
        with mock.patch.object(ow.os, "open", side_effect=open_old_then_publish):
            # The old inode's fd shows nlink 0 once replaced, or the detached object fails its re-hash.
            with self.assertRaisesRegex(ow.Mismatch, "changed_during_deletion|local_pack_changed"):
                self.offload().release()
        self.assertTrue(replaced)
        self.assertEqual(payload.read_bytes(), unique)  # the replacement is never deleted

    def test_pressure_cannot_release_with_only_the_air_copy(self):
        harvest, _, args = self.native_pack()
        self.assertEqual(self.run_offload(min_free_gib=1e9, **args), 0)
        with self.assertRaises(TypeError):
            self.offload().release(pressure_compressed_local=True)
        with self.assertRaisesRegex(ow.Refusal, "second_copy_not_confirmed"):
            self.offload().release()
        self.assert_nothing_deleted()
        self.assertTrue((self.pack_dir / ow.HARVEST_PAYLOAD).exists())


@unittest.skipUnless(ow.zstd_cli(), "native harvest packs require zstd")
class LinkTypes(Base):
    """D2 / S1-D02: a bound link must still be a link with its text; a type change is kept and refuses."""

    def test_link_materialized_in_a_duplicate_is_kept(self):
        self.materialized(resumed=False)

    def test_link_materialized_after_a_resumed_crash_is_kept(self):
        self.materialized(resumed=True)

    def materialized(self, *, resumed):
        (self.record / "view").symlink_to("members/m01/raw")
        duplicate = self.tmp / "mbp/synced-duplicate"
        shutil.copytree(self.record, duplicate, symlinks=True)
        (self.record / "view").unlink()
        _, _, args = self.native_pack(duplicate_roots=[duplicate], link="members/m01/raw")
        self.verified(**args)
        if resumed:
            self.crash_raw()
        target, unique, changed = duplicate / "view", b"a sync materialized a different file here\n", []
        off = self.offload()

        def sync_during_raw_unlinks(path, **kwargs):
            if not changed:
                target.unlink()
                target.write_bytes(unique)
                changed.append(True)
            os.unlink(path, **kwargs)
        off.unlink = sync_during_raw_unlinks
        # Caught on the detached object, or (after a resume, whose first unlink drains the quarantine
        # before pass 1) by pass 1 itself: either way the new file is kept and the release refuses.
        with self.assertRaisesRegex(ow.Mismatch, "changed_during_deletion|type_or_link_changed"):
            off.release()
        self.assertTrue(changed)
        self.assertEqual(target.read_bytes(), unique)
        self.assertFalse((self.state / "w1-test/released.json").exists())

    def test_link_materialized_in_the_record_is_kept(self):
        _, _, args = self.native_pack(link="members/m01/outputs/align_turns.jsonl")
        self.verified(**args)
        target, unique, changed = self.record / "view", b"a copied regular file over a listed symlink\n", []
        off = self.offload()

        def materialize_after_first_unlink(path, *a, **kw):
            os.unlink(path, *a, **kw)
            if not changed:
                target.unlink()
                target.write_bytes(unique)
                changed.append(True)
        off.unlink = materialize_after_first_unlink
        with self.assertRaisesRegex(ow.Mismatch, "changed_during_deletion"):
            off.release()
        self.assertEqual(target.read_bytes(), unique)

    def test_link_changed_before_release_is_preserved(self):
        _, _, args = self.native_pack(link="members/m01/raw")
        self.verified(**args)
        target = self.record / "view"
        target.unlink()
        target.write_bytes(b"different regular file")
        with self.assertRaisesRegex(ow.Mismatch, "record_changed_since_offload|type_or_link_changed"):
            self.offload().release()
        self.assertEqual(target.read_bytes(), b"different regular file")
        self.assert_nothing_deleted()


@unittest.skipUnless(ow.zstd_cli(), "native harvest packs require zstd")
class FreshAirRestore(Base):
    """D3: with the harvest-off lane's pack (every byte_bound_inputs() entry carried) and its unpack (placed
    at the finalized real paths), the Air copy restores with every MBP-side external file deleted."""

    def restore_with_externals_deleted(self, *, link_to_directory):
        outside = self.tmp / "mbp/linked-inputs"
        outside.mkdir()
        dependency = outside / "input.json"
        dependency.write_bytes(b'{"synthetic_dependency":true}\n')
        harvest, finalized, args = self.native_pack(inputs=(dependency,),
                                                    link=str(outside if link_to_directory else dependency))
        self.verified(**args)
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        carried = {row["path"] for row in manifest["externals"]}
        self.assertEqual(carried, set(harvest.byte_bound_inputs(finalized)))
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
        expected = dependency.read_bytes()
        shutil.rmtree(outside)  # every MBP-side external file is gone
        self.record.rmdir()
        for source in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            with self.subTest(source=source.name):
                harvest.unpack(source, finalized=finalized, finalized_sha256=self.manifest_sha)
                self.assertEqual(dependency.read_bytes(), expected)
                via = (self.record / "view" / "input.json") if link_to_directory else (self.record / "view")
                self.assertEqual(via.read_bytes(), expected)  # the bound link resolves on the fresh Air
                for rel, raw in self.files.items():
                    self.assertEqual((self.record / rel).read_bytes(), raw)
                shutil.rmtree(self.record)
                shutil.rmtree(outside)

    def test_link_to_a_carried_file_restores(self):
        self.restore_with_externals_deleted(link_to_directory=False)

    def test_link_to_a_carried_directory_restores(self):
        self.restore_with_externals_deleted(link_to_directory=True)

    def test_external_terminal_evidence_restores_from_each_copy(self):
        night = self.tmp / "mbp/external-terminal"
        night.mkdir(parents=True)
        external = {}
        for rel in tuple(self.files):
            if rel.startswith("custody/night/"):
                path = night / Path(rel).name
                external[path] = self.files.pop(rel)
                (self.record / rel).rename(path)
        harvest, finalized, args = self.native_pack(inputs=tuple(sorted(external)))
        self.verified(terminal=str(night / "result.json"), **args)
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
        for source in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            shutil.rmtree(self.record)
            for path in external:
                path.unlink()
            harvest.unpack(source, finalized=finalized, finalized_sha256=self.manifest_sha)
            for path, raw in external.items():
                self.assertEqual(path.read_bytes(), raw)
            for rel, raw in self.files.items():
                self.assertEqual((self.record / rel).read_bytes(), raw)

    def test_a_pack_missing_a_byte_bound_input_is_refused(self):
        outside = self.tmp / "mbp/input.json"
        outside.write_bytes(b'{"synthetic_input":true}\n')
        harvest = native_harvest()
        (self.record / "view").symlink_to(outside)
        finalized = harvest.finalized_manifest(self.record)  # the link target is byte-bound, not declared
        raw = json.dumps(finalized, sort_keys=True, separators=(",", ":")).encode()
        self.manifest.write_bytes(raw)
        self.manifest_sha = fixtures.sha(raw)
        pack_dir = self.tmp / "mbp/incomplete-pack"
        harvest.pack(self.record, pack_dir, finalized=finalized, threads=1, external=())
        self.assertEqual(self.run_offload(harvest_pack=pack_dir, pack=False), 2)
        self.assertIn("harvest_pack_not_restorable", self.span()["reason"])
        self.assertEqual(self.transport.calls, [])

    def test_reused_window_id_refuses_a_different_finalize(self):
        harvest, _, args = self.native_pack()
        self.verified(**args)
        relative = "members/m01/outputs/align_turns.jsonl"
        new_bytes = b"a later window accidentally reused w1-test"
        (self.record / relative).write_bytes(new_bytes)
        finalized = harvest.finalized_manifest(self.record)
        raw = json.dumps(finalized, sort_keys=True, separators=(",", ":")).encode()
        self.manifest.write_bytes(raw)
        new_pack = self.tmp / "mbp/new-harvest-pack"
        harvest.pack(self.record, new_pack, finalized=finalized, threads=1)
        self.assertEqual(self.run_offload(record_manifest_sha256=fixtures.sha(raw), harvest_pack=new_pack,
                                          pack=False), 3)
        self.assertEqual((self.record / relative).read_bytes(), new_bytes)
        self.assertTrue((new_pack / ow.HARVEST_PAYLOAD).exists())


if __name__ == "__main__":
    unittest.main()
