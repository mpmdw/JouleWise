"""Synthetic review witnesses for Air offload at 175f0c8b9.

The ``test_witness_*`` cases characterize unsafe behavior in the reviewed tree;
passing them is evidence of the finding, not evidence that the behavior is safe.
After repairs, invert those assertions into safety regression checks. Everything
uses the existing temporary-directory fixture and in-process Air/volume/cloud
fakes. No setup script, SSH, network, live store, or study data is used.
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import unittest
from unittest.mock import patch

from tests import test_offload_window as fixture

ow = fixture.ow


class ReleaseWitnesses(fixture.Fixture):
    def test_witness_different_same_size_duplicate_is_deleted(self):
        duplicate = self.tmp / "mbp/operator-selected-duplicate"
        shutil.copytree(self.record, duplicate)
        rel = "custody/night/chain-stages.jsonl"
        original = self.files[rel]
        unique = b"!" * len(original)
        (duplicate / rel).write_bytes(unique)

        self.assertEqual(self.run_offload(duplicate_root=[duplicate]), 0)
        self.confirm_second_copy()
        copy = self.store / "windows/w1-test/raw" / rel
        self.assertEqual(copy.read_bytes(), original)
        self.assertNotEqual(copy.read_bytes(), unique)
        result = self.offload().release()

        # Only the original bytes were backed up; the unique duplicate is lost.
        self.assertEqual(result["rule"], "two_verified_copies")
        self.assertFalse((duplicate / rel).exists())
        self.assertEqual(result["skipped"], [])

    def test_witness_reused_pack_directory_new_payload_is_deleted(self):
        self.assertEqual(self.run_offload(), 0)
        self.confirm_second_copy()
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        # A later pack occupies the same local directory before this older
        # window's asynchronous second-copy receipt is collected.
        part = self.state / "w1-test/parts" / manifest["parts"][0]["name"]
        replacement = b"a different window's not-yet-backed-up compressed bytes"
        part.write_bytes(replacement)
        result = self.offload().release()
        self.assertTrue(result["parts_deleted"])
        self.assertFalse(part.exists())

    def test_witness_cli_release_is_invisible_to_triage(self):
        self.assertEqual(self.run_offload(), 0)
        self.confirm_second_copy()
        span_path = self.state / "w1-test/timing/offload-span.json"
        old_span = span_path.read_bytes()
        self.clock.t += 600  # the second copy landed well after the initial run
        dwell = self.clock.t + 60  # release is now inside the 120 s margin
        observed = []

        def before(command):
            if command.startswith("receipts "):
                observed.append(ow.triage(self.state, "w1-test", dwell, 120))

        self.transport.before = before
        # Invoke the actual public release command, replacing only host-facing
        # dependencies. In particular, do not call the real home-directory/ps probe.
        with patch.object(ow, "_transport", return_value=self.transport), \
                patch.object(ow, "default_state_probe", return_value=lambda: self.probe_state), \
                contextlib.redirect_stdout(io.StringIO()):
            rc = ow.main(["release", "--state-root", str(self.state), "--window-id", "w1-test"])

        self.assertEqual(rc, 0)
        self.assertEqual(len(observed), 1)
        self.assertTrue(observed[0]["quiet_start_state_ok"])  # even while release is active
        self.assertEqual(span_path.read_bytes(), old_span)
        self.assertTrue(ow.triage(self.state, "w1-test", dwell, 120)["quiet_start_state_ok"])
        self.assertFalse((self.record / fixture.TERMINAL).exists())

    def test_witness_arm_after_receipt_request_does_not_stop_deletion(self):
        self.assertEqual(self.run_offload(), 0)
        self.confirm_second_copy()

        def before(command):
            if command.startswith("receipts "):
                self.probe_state = {"armed": ["com.joulewise.align-next.plist"], "measuring": []}

        self.transport.before = before
        result = self.offload().release()
        self.assertEqual(result["rule"], "two_verified_copies")
        self.assertTrue(self.probe_state["armed"])
        self.assertFalse((self.record / fixture.TERMINAL).exists())


class SafetyControls(fixture.Fixture):
    def test_replayed_nonce_is_refused_before_deletion(self):
        self.assertEqual(self.run_offload(), 0)
        self.confirm_second_copy()
        _, prior, _ = self.transport(f"receipts w1-test {'a' * 32}")
        self.transport.replace_reply = lambda command, reply: prior if command.startswith("receipts ") else reply
        with self.assertRaisesRegex(ow.Mismatch, "fresh_receipt_does_not_match"):
            self.offload().release()
        self.assert_nothing_deleted()

    def test_volume_uuid_switch_at_release_is_refused(self):
        self.assertEqual(self.run_offload(), 0)
        self.confirm_second_copy()
        self.probe.default["volume_uuid"] = "REPLACEMENT-VOLUME"
        with self.assertRaisesRegex(ow.TransportError, "store_volume_uuid_mismatch"):
            self.offload().release()
        self.assert_nothing_deleted()


@unittest.skipUnless(ow.zstd_cli(), "synthetic harvest pack needs the zstd CLI")
class ConsumedPackWitnesses(fixture.Fixture):
    def packed(self):
        entries = {}
        for path in sorted(self.record.rglob("*")):
            rel = path.relative_to(self.record).as_posix()
            entries[rel] = {"directory": True} if path.is_dir() else {
                "sha256": fixture.sha(path.read_bytes()), "size": path.stat().st_size}
        doc = {"schema": ow.SCHEMA_FINALIZED_V2, "source_root": str(self.record), "entries": entries,
               "closure": {"links": {}, "ignored": {}, "mirror": None, "ignored_policy": {},
                           "inputs": {}, "files": {}}}
        raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
        finalized = self.tmp / "mbp/finalized_manifest.json"
        finalized.write_bytes(raw)
        self.pack_dir = self.tmp / "mbp/shared-harvest-output/offload"
        fixture.build_harvest_pack(self.record, self.pack_dir, fixture.sha(raw))
        return dict(record_manifest=finalized, record_manifest_sha256=fixture.sha(raw),
                    harvest_pack=self.pack_dir, pack=False)

    def test_witness_reused_harvest_pack_is_deleted_without_identity_check(self):
        args = self.packed()
        self.assertEqual(self.run_offload(**args), 0)
        self.confirm_second_copy()
        payload = self.pack_dir / ow.HARVEST_PAYLOAD
        transport_manifest = self.pack_dir / ow.HARVEST_MANIFEST
        payload.write_bytes(b"next window's sole compressed payload")
        transport_manifest.write_bytes(b"next window's sole transport manifest")
        result = self.offload().release()
        self.assertTrue(result["parts_deleted"])
        self.assertFalse(self.pack_dir.exists())

    def test_consumed_pack_is_byte_identical_and_never_repacked(self):
        args = self.packed()
        originals = {p.name: p.read_bytes() for p in self.pack_dir.iterdir()}
        with patch.object(ow.Offload, "pack", side_effect=AssertionError("unexpected repack")):
            self.assertEqual(self.run_offload(**args), 0)
        for name, raw in originals.items():
            self.assertEqual((self.store / "inbox/w1-test" / name).read_bytes(), raw)
        self.assertFalse(list((self.state / "w1-test/parts").iterdir()))

    def test_payload_corruption_is_refused_before_any_raw_deletion(self):
        args = self.packed()
        payload = self.pack_dir / ow.HARVEST_PAYLOAD
        raw = bytearray(payload.read_bytes())
        raw[-1] ^= 1
        payload.write_bytes(raw)
        self.assertEqual(self.run_offload(**args), 3)
        self.assertIn("commit_digest_mismatch:payload.tar.zst", self.span()["reason"])
        self.assert_nothing_deleted()


if __name__ == "__main__":
    unittest.main()
