"""Independent delta review of 175f0c8b9..66b7da341; synthetic data only.

Passing ``test_witness_*`` cases demonstrate remaining defects, not safe behavior.
``test_control_*`` cases check preservation/refusal. Deterministic unlink hooks
stand in for a crash or another ordinary local producer at that scheduling point;
no receipt, digest, clock, or deletion journal is forged.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import unittest

from tests import test_offload_window as fixtures
from tests.test_offload_review_fixes import native_harvest

ow = fixtures.ow


class LegacyChecks(fixtures.Fixture):
    def verified(self, **kwargs):
        self.assertEqual(self.run_offload(**kwargs), 0)
        self.confirm_second_copy()

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
        self.assertEqual(len(deleted), count)
        return ow.read_json(self.state / "w1-test/deleting.json")

    def test_control_crash_after_unlink_resumes_with_fresh_receipts(self):
        self.verified()
        journal = self.crash_raw()
        self.assertEqual(journal["state"], "deleting")
        before = len([c for c in self.transport.calls if c.startswith("receipts ")])
        result = self.offload().release()
        self.assertTrue(result["resumed"])
        self.assertEqual(result["rule"], "two_verified_copies")
        after = len([c for c in self.transport.calls if c.startswith("receipts ")])
        self.assertEqual(after, before + 1)
        self.assertFalse(any((self.record / rel).exists() for rel in self.files))

    def test_control_real_unlink_resume_rehashes_same_metadata_duplicate(self):
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

    def test_control_air_decay_on_crash_resume_prevents_more_unlinks(self):
        self.verified()
        self.crash_raw()
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        part = self.store / "inbox/w1-test" / manifest["parts"][0]["name"]
        part.write_bytes(b"synthetic storage decay")
        before = sum((self.record / rel).exists() for rel in self.files)
        with self.assertRaisesRegex(ow.Mismatch, "air_part_decayed"):
            self.offload().release()
        self.assertEqual(sum((self.record / rel).exists() for rel in self.files), before)

    def test_control_partial_pack_cannot_authorize_raw_deletion(self):
        self.transport.cut_put_after = 100
        self.assertEqual(self.run_offload(), 5)
        self.assert_nothing_deleted()
        self.assertFalse((self.store / "windows/w1-test" / ow.AIR_RECEIPT).exists())
        with self.assertRaisesRegex(ow.Refusal, "no_air_receipt"):
            self.offload().release()
        self.assert_nothing_deleted()
        self.assertEqual(self.run_offload(), 0)
        self.confirm_second_copy()
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")

    def test_witness_repeated_root_needs_retry_after_file_not_found(self):
        self.verified(duplicate_root=[self.record, self.record])
        with self.assertRaises(FileNotFoundError):
            self.offload().release()
        self.assertFalse((self.state / "w1-test/released.json").exists())
        self.assertEqual(ow.read_json(self.state / "w1-test/deleting.json")["state"], "deleting")
        self.assertTrue(self.offload().release()["resumed"])

    def test_witness_raw_replacement_in_stat_unlink_gap_is_deleted(self):
        # Narrow race: no mtime preservation is needed AFTER the final stat.
        self.verified()
        off, changed = self.offload(), []
        relative = sorted(self.files)[0]
        target = self.record / relative
        unique = b"new bytes written after final stat, before unlink"

        def concurrent_writer(path, **kwargs):
            if not changed:
                self.assertEqual(path, target.name)
                target.write_bytes(unique)
                changed.append(True)
            os.unlink(path, **kwargs)
        off.unlink = concurrent_writer
        self.assertEqual(off.release()["rule"], "two_verified_copies")
        self.assertTrue(changed)
        self.assertFalse(target.exists())
        self.assertNotEqual((self.store / "windows/w1-test/raw" / relative).read_bytes(), unique)


@unittest.skipUnless(ow.zstd_cli(), "native harvest packs require zstd")
class NativeChecks(fixtures.Fixture):
    def pack_native(self, *, inputs=(), duplicate_roots=()):
        harvest = native_harvest()
        finalized = harvest.finalized_manifest(self.record, inputs=tuple(inputs))
        raw = json.dumps(finalized, sort_keys=True, separators=(",", ":")).encode()
        self.manifest.write_bytes(raw)
        self.manifest_sha = fixtures.sha(raw)
        pack_dir = self.tmp / "mbp/harvest-output/offload"
        harvest.pack(self.record, pack_dir, finalized=finalized, threads=1, external=tuple(inputs))
        self.assertEqual(self.run_offload(harvest_pack=pack_dir, pack=False,
                                          duplicate_root=list(duplicate_roots)), 0)
        self.confirm_second_copy()
        return harvest, finalized, pack_dir

    def test_witness_new_native_pack_at_validated_path_is_deleted(self):
        self.pack_reuse_witness(resumed=False)

    def test_witness_resumed_cleanup_deletes_new_native_pack(self):
        self.pack_reuse_witness(resumed=True)

    def pack_reuse_witness(self, *, resumed):
        harvest, _, pack_dir = self.pack_native()
        off = self.offload()
        if resumed:
            def crash_before_pack_unlink(path, **kwargs):
                if isinstance(path, Path):
                    raise OSError(5, "synthetic crash after pack journal, before pack unlink")
                os.unlink(path, **kwargs)
            off.unlink = crash_before_pack_unlink
            with self.assertRaises(OSError):
                off.release()
            self.assertEqual(ow.read_json(self.state / "w1-test/deleting-parts.json")["state"], "deleting")
            off = self.offload()

        next_root = self.tmp / "mbp/w2-record"
        next_root.mkdir()
        (next_root / "new.txt").write_bytes(b"window two's independently finalized, not-yet-offloaded bytes")
        next_finalized = harvest.finalized_manifest(next_root)
        replacements = {}
        retired = pack_dir.with_name("retired-w1-pack")

        def next_producer(path, **kwargs):
            if isinstance(path, Path) and not replacements:
                # Ordinary producer actions: move aside the old output, then
                # use the native packer's required NEW directory at that name.
                pack_dir.rename(retired)
                harvest.pack(next_root, pack_dir, finalized=next_finalized, threads=1)
                replacements.update({p.name: p.read_bytes() for p in pack_dir.iterdir()})
                # This producer never adopts w2: the claim is checked at adoption,
                # after production, and does not exclude these ordinary writes.
            os.unlink(path, **kwargs)
        off.unlink = next_producer
        self.assertEqual(off.release()["rule"], "two_verified_copies")
        self.assertEqual(set(replacements), {ow.HARVEST_PAYLOAD, ow.HARVEST_MANIFEST})
        self.assertFalse(pack_dir.exists())
        for name, raw in replacements.items():
            self.assertNotEqual((self.store / "inbox/w1-test" / name).read_bytes(), raw)
            self.assertNotEqual((self.icloud / "w1-test" / name).read_bytes(), raw)
            self.assertNotEqual((retired / name).read_bytes(), raw)
        self.assertTrue((next_root / "new.txt").exists())

    def test_witness_validated_duplicate_link_becomes_unbacked_regular_file(self):
        self.link_replacement_witness(resumed=False)

    def test_witness_resumed_unlinks_delete_materialized_duplicate_link(self):
        self.link_replacement_witness(resumed=True)

    def link_replacement_witness(self, *, resumed):
        (self.record / "view").symlink_to("members/m01/raw")
        duplicate = self.tmp / "mbp/synced-duplicate"
        shutil.copytree(self.record, duplicate, symlinks=True)
        self.pack_native(duplicate_roots=[duplicate])
        off = self.offload()
        if resumed:
            calls = []

            def crash_raw(path, **kwargs):
                if len(calls) == 2:
                    raise OSError(5, "synthetic crash during raw deletion")
                os.unlink(path, **kwargs)
                calls.append(path)
            off.unlink = crash_raw
            with self.assertRaises(OSError):
                off.release()
            off = self.offload()
        changed = []
        target = duplicate / "view"
        unique = b"a sync materialized a different file here after link verification"

        def sync_during_raw_unlinks(path, **kwargs):
            if not changed:
                target.unlink()  # materialize a file over a symlink, without metadata tricks
                target.write_bytes(unique)
                changed.append(True)
            os.unlink(path, **kwargs)
        off.unlink = sync_during_raw_unlinks
        self.assertEqual(off.release()["rule"], "two_verified_copies")
        self.assertFalse(target.exists())
        self.assertTrue(changed)
        for root in (self.store / "inbox/w1-test", self.icloud / "w1-test"):
            transport = ow.read_json(root / ow.HARVEST_MANIFEST)
            self.assertEqual(transport["entries"]["view"], {"link": "members/m01/raw"})
            self.assertNotIn(fixtures.sha(unique), {r.get("sha256") for r in transport["entries"].values()})

    def test_control_link_changed_before_release_is_preserved(self):
        (self.record / "view").symlink_to("members/m01/raw")
        self.pack_native()
        target = self.record / "view"
        target.unlink()
        target.write_bytes(b"different regular file")
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        self.assertEqual(target.read_bytes(), b"different regular file")
        self.assert_nothing_deleted()

    def test_witness_native_restore_with_carried_file_link_target_absent(self):
        self.restore_link_witness(directory=False)

    def test_witness_native_restore_with_carried_directory_target_absent(self):
        self.restore_link_witness(directory=True)

    def restore_link_witness(self, *, directory):
        outside = self.tmp / "mbp/linked-inputs"
        outside.mkdir()
        dependency = outside / "input.json"
        dependency.write_bytes(b'{"synthetic_dependency":true}\n')
        (self.record / "view").symlink_to(outside if directory else dependency)
        harvest, finalized, _ = self.pack_native(inputs=(dependency,))
        inbox = self.store / "inbox/w1-test"
        for name in (ow.HARVEST_PAYLOAD, ow.HARVEST_MANIFEST, ow.RECORD_MANIFEST_NAME, ow.MANIFEST_NAME):
            self.assertEqual((inbox / name).read_bytes(), (self.icloud / "w1-test" / name).read_bytes())
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        env = ow.parse_record_manifest(self.manifest.read_bytes(), self.record)
        self.assertEqual(ow.restore_gaps(env, manifest["externals"]), [])
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
        self.record.rmdir()
        # Model an unprovisioned Air solely by withholding synthetic MBP files.
        outside.rename(outside.with_name("withheld-mbp-inputs"))
        with self.assertRaisesRegex(harvest.OffloadRefused, "external link view resolves differently"):
            harvest.unpack(inbox, finalized=finalized, finalized_sha256=self.manifest_sha)
        self.assertFalse(self.record.exists())
        self.assertTrue((inbox / ow.HARVEST_PAYLOAD).is_file())

    def test_control_unlinked_carried_input_restores_when_mbp_input_absent(self):
        outside = self.tmp / "mbp/input.json"
        outside.write_bytes(b'{"synthetic_input":true}\n')
        harvest, finalized, _ = self.pack_native(inputs=(outside,))
        original = outside.read_bytes()
        self.offload().release()
        self.record.rmdir()
        outside.rename(outside.with_name("withheld-input.json"))
        harvest.unpack(self.store / "inbox/w1-test", finalized=finalized, finalized_sha256=self.manifest_sha)
        self.assertEqual(outside.read_bytes(), original)
        for rel, raw in self.files.items():
            self.assertEqual((self.record / rel).read_bytes(), raw)

    def test_control_reused_window_id_refuses_different_finalize(self):
        harvest, _, _ = self.pack_native()
        relative = "members/m01/outputs/align_turns.jsonl"
        new_bytes = b"a later window accidentally reused w1-test"
        (self.record / relative).write_bytes(new_bytes)
        finalized = harvest.finalized_manifest(self.record)
        raw = json.dumps(finalized, sort_keys=True, separators=(",", ":")).encode()
        self.manifest.write_bytes(raw)
        new_pack = self.tmp / "mbp/new-harvest-pack"
        harvest.pack(self.record, new_pack, finalized=finalized, threads=1)
        rc = self.run_offload(record_manifest_sha256=fixtures.sha(raw), harvest_pack=new_pack, pack=False)
        self.assertEqual(rc, 3)
        self.assertIn("duplicate_run_conflict", self.span()["reason"])
        self.assertEqual((self.record / relative).read_bytes(), new_bytes)
        self.assertTrue((new_pack / ow.HARVEST_PAYLOAD).exists())
        # With a new local state root, the Air independently rejects ID reuse.
        rc = self.run_offload(state_root=self.tmp / "mbp/other-state", record_manifest_sha256=fixtures.sha(raw),
                              harvest_pack=new_pack, pack=False)
        self.assertEqual(rc, 3)
        self.assertEqual((self.record / relative).read_bytes(), new_bytes)


if __name__ == "__main__":
    unittest.main()
