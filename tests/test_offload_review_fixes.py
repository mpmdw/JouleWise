"""Required properties from the Sol review seats on 175f0c8b9 (both HOLD).

Seat 1: docs/ops/AIR-OFFLOAD-REVIEW-sol1.md on ops/2026-11-08-offload-review-sol1 (S1-01..S1-04);
seat 2: docs/ops/AIR-OFFLOAD-REVIEW-sol2.md on ops/2026-11-08-offload-review-sol2 (F1..F3). Each of their
defect-reproducing witnesses is inverted here into the safe behavior; their controls are kept.
Everything is synthetic: temporary trees, the in-process gate, the fake volume probe and cloud.
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
# harvest_offload.py at origin/align/2026-11-08-harvest-off-fix @ 4c292637d: its pack carries every
# byte_bound_inputs() entry and its unpack places them append-only at their finalized real paths.
HARVEST_BLOB = "aaf28b28761aea5201f7b15d0997cd06b064f3d1"
HARVEST_SHA256 = "a767a4642f559d755b2b212fbcfc91eb0b13e7fc8f8d8d1cdff6c6549806f5c4"


def native_harvest():
    result = subprocess.run(["git", "cat-file", "blob", HARVEST_BLOB], cwd=fixtures.ROOT, capture_output=True)
    if result.returncode or fixtures.sha(result.stdout) != HARVEST_SHA256:
        raise unittest.SkipTest("pinned harvest-off code object is unavailable")
    module = types.ModuleType("native_harvest_offload")
    exec(compile(result.stdout, "git-blob:" + HARVEST_BLOB, "exec"), module.__dict__)
    return module


class Release(fixtures.Fixture):
    def verified(self, **kwargs):
        self.assertEqual(self.run_offload(**kwargs), 0)
        self.confirm_second_copy()

    def release_cli(self, *extra, runner=None):
        with mock.patch.object(ow, "_transport", return_value=runner or self.transport), \
                mock.patch.object(ow, "default_state_probe", return_value=lambda: self.probe_state), \
                mock.patch.object(ow.time, "time", self.clock), mock.patch.object(ow.time, "monotonic", self.clock), \
                contextlib.redirect_stdout(io.StringIO()):
            return ow.main(["release", "--state-root", str(self.state), "--window-id", "w1-test", *extra])

    # F1 / S1-01: content, not size, authorizes a deletion.
    def test_same_size_different_duplicate_is_kept_and_release_refused(self):
        duplicate = self.tmp / "mbp/operator-selected-duplicate"
        shutil.copytree(self.record, duplicate)
        rel = "custody/night/chain-stages.jsonl"
        unique = b"!" * len(self.files[rel])
        (duplicate / rel).write_bytes(unique)
        self.verified(duplicate_root=[duplicate])
        for _ in range(2):  # first release, then the journaled resume: both refuse
            with self.assertRaises(ow.Mismatch) as caught:
                self.offload().release()
            self.assertIn("content_differs_from_bound_digest", str(caught.exception))
        self.assertEqual((duplicate / rel).read_bytes(), unique)
        for root in (self.record, duplicate):
            for name in self.files:
                self.assertTrue((root / name).exists(), (root, name))

    def test_nonempty_same_size_nonduplicate_is_kept(self):
        duplicate = self.tmp / "mbp/backup/w1-test"
        rel = "members/m01/outputs/align_turns.jsonl"
        target = duplicate / rel
        target.parent.mkdir(parents=True)
        different = b"X" * len(self.files[rel])
        target.write_bytes(different)
        self.verified(duplicate_root=[duplicate])
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        self.assertEqual(target.read_bytes(), different)
        self.assert_nothing_deleted()

    def test_different_size_duplicate_refuses_and_is_kept(self):
        # Seat 1's control kept the file and released the rest; the lead's rule is to refuse on any mismatch.
        duplicate = self.tmp / "mbp/backup/w1-test"
        duplicate.mkdir(parents=True)
        (duplicate / "empty.txt").write_bytes(b"not empty")
        self.verified(duplicate_root=[duplicate])
        with self.assertRaises(ow.Mismatch) as caught:
            self.offload().release()
        self.assertIn("duplicate_differs", str(caught.exception))
        self.assertEqual((duplicate / "empty.txt").read_bytes(), b"not empty")
        self.assert_nothing_deleted()

    def test_record_file_with_kept_size_and_mtime_but_new_content_is_kept(self):
        self.verified()
        path = self.record / "members/m02/raw/powermetrics.plist"
        raw, info = bytearray(path.read_bytes()), path.stat()
        raw[100] ^= 1
        path.write_bytes(bytes(raw))
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
        with self.assertRaises(ow.Mismatch) as caught:
            self.offload().release()
        self.assertIn("content_differs_from_bound_digest", str(caught.exception))
        self.assert_nothing_deleted()

    # F2: a reused local pack location never loses another window's bytes.
    def test_replaced_local_part_is_never_deleted(self):
        self.verified()
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        part = self.state / "w1-test/parts" / manifest["parts"][0]["name"]
        replacement = b"a different window's not-yet-backed-up compressed bytes"
        part.write_bytes(replacement)
        with self.assertRaises(ow.Mismatch) as caught:
            self.offload().release()
        self.assertIn("local_pack_changed", str(caught.exception))
        self.assertEqual(part.read_bytes(), replacement)
        self.assert_nothing_deleted()  # checked before the first deletion

    def test_interrupted_parts_deletion_resumes_and_rechecks(self):
        self.verified()
        off = self.offload()
        calls = {"n": 0}

        def flaky(path, *a, **kw):
            if isinstance(path, Path) and "part-" in path.name:
                calls["n"] += 1
                if calls["n"] == 1:  # the first part is detached, its unlink is lost
                    raise OSError(5, "simulated power loss")
            return os.unlink(path, *a, **kw)
        off.unlink = flaky
        with self.assertRaises(OSError):
            off.release()
        survivors = sorted((self.state / "w1-test/parts").glob("part-*.tar.zst"))
        self.assertTrue(survivors)
        survivors[0].write_bytes(b"replaced while the deletion was interrupted")
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        self.assertTrue(survivors[0].exists())

    # F3 / S1-02: a standalone release is supervised exactly like run.
    def test_cli_release_holds_the_lock_and_is_visible_to_triage(self):
        self.verified()
        old_span = (self.state / "w1-test/timing/offload-span.json").read_bytes()
        self.clock.t += 600
        dwell = self.clock.t + 60
        observed = []

        def before(command):
            if command.startswith("receipts "):
                observed.append(ow.triage(self.state, "w1-test", dwell, 120))
        self.transport.before = before
        self.assertEqual(self.release_cli(), 0)
        self.assertFalse(observed[0]["quiet_start_state_ok"])
        self.assertIn("offload_running", observed[0]["reasons"])
        after = ow.triage(self.state, "w1-test", dwell, 120)
        self.assertFalse(after["quiet_start_state_ok"])
        self.assertIn("offload_activity_inside_dwell_margin", after["reasons"])
        span = json.loads((self.state / "w1-test/timing/release-span.json").read_text())
        self.assertEqual((span["activity"], span["rc"]), ("release", 0))
        self.assertEqual((self.state / "w1-test/timing/offload-span.json").read_bytes(), old_span)
        self.assertTrue(ow.triage(self.state, "w1-test", span["ended_epoch_s"] + 121, 120)["quiet_start_state_ok"])

    def test_cli_release_refuses_while_an_offload_holds_the_lock(self):
        self.verified()
        fd = os.open(self.state / ".lock", os.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(self.release_cli(), 2)
        finally:
            os.close(fd)
        self.assertFalse((self.state / "w1-test/released.json").exists())
        self.assert_nothing_deleted()

    def test_cli_release_is_bounded_and_stops_before_the_dwell(self):
        self.verified()
        timeouts = []
        runner = self.transport

        def slow(command, **kwargs):
            if command.startswith("receipts "):
                timeouts.append(kwargs["timeout"])
                self.clock.t += 200  # a slow Air: crosses the deadline
            return runner(command, **kwargs)
        rc = self.release_cli("--deadline-epoch", str(self.clock.t + 150), runner=slow)
        self.assertEqual(rc, 4)
        self.assertIsNotNone(timeouts[0])
        self.assertLessEqual(timeouts[0], 150)
        self.assert_nothing_deleted()
        rc = self.release_cli("--deadline-epoch", str(self.clock.t + 3), runner=slow)  # admission refuses
        self.assertEqual(rc, 4)

    def test_arm_during_the_receipt_round_trip_stops_the_deletion(self):
        self.verified()

        def before(command):
            if command.startswith("receipts "):
                self.probe_state = {"armed": ["com.joulewise.align-next.plist"], "measuring": []}
        self.transport.before = before
        with self.assertRaises(ow.Refusal) as caught:
            self.offload().release()
        self.assertIn("window_armed", str(caught.exception))
        self.assert_nothing_deleted()

    # Controls kept from both seats.
    def test_replayed_nonce_is_refused_before_deletion(self):
        self.verified()
        _, prior, _ = self.transport(f"receipts w1-test {'a' * 32}")
        self.transport.replace_reply = lambda command, reply: prior if command.startswith("receipts ") else reply
        with self.assertRaisesRegex(ow.Mismatch, "fresh_receipt_does_not_match"):
            self.offload().release()
        self.assert_nothing_deleted()

    def test_volume_uuid_switch_at_release_is_refused(self):
        self.verified()
        self.probe.default["volume_uuid"] = "REPLACEMENT-VOLUME"
        with self.assertRaisesRegex(ow.TransportError, "store_volume_uuid_mismatch"):
            self.offload().release()
        self.assert_nothing_deleted()


class Census(unittest.TestCase):
    """S1-03: any failure of the process census counts as NOT quiet."""

    def probe(self, result):
        agents = Path(fixtures.TMP_BASE) / "nonexistent-launch-agents-dir"
        with mock.patch.object(ow.subprocess, "run", **result):
            return ow.default_state_probe(launch_agents=agents)()

    def assert_not_quiet(self, state):
        self.assertTrue(state["measuring"] and state["measuring"][0].startswith("process_census_failed"), state)
        off = ow.Offload(fixtures.TMP_BASE / "census-state", "w1-test", state_probe=lambda: state)
        with self.assertRaises(ow.Refusal):
            off.check_quiet_allowed()

    def test_failed_census_variants_refuse(self):
        me = os.getpid()
        for result in (
                {"return_value": subprocess.CompletedProcess(["/bin/ps"], 1, stdout="", stderr="unavailable")},
                {"return_value": subprocess.CompletedProcess(["/bin/ps"], 0, stdout="", stderr="")},
                {"return_value": subprocess.CompletedProcess(["/bin/ps"], 0, stdout="garbage line\n", stderr="")},
                {"return_value": subprocess.CompletedProcess(["/bin/ps"], 0, stdout="1 /sbin/launchd\n", stderr="")},
                {"side_effect": PermissionError(1, "Operation not permitted")},
                {"side_effect": subprocess.TimeoutExpired(["/bin/ps"], 30)}):
            with self.subTest(result=result):
                self.assert_not_quiet(self.probe(result))
        ok = self.probe({"return_value": subprocess.CompletedProcess(
            ["/bin/ps"], 0, stdout=f"1 /sbin/launchd\n{me} python3 offload_window.py\n", stderr="")})
        self.assertEqual(ok, {"armed": [], "measuring": []})


@unittest.skipUnless(ow.zstd_cli(), "consumed harvest packs require zstd")
class ConsumedPack(fixtures.Fixture):
    def finalized(self, night=None, inputs=()):
        entries = {}
        for rel, (kind, value) in ow.scan_tree(self.record).items():
            entries[rel] = ({"directory": True} if kind == "dir" else {"link": value} if kind == "link" else
                            {"sha256": ow.hash_file(self.record / rel)[0], "size": (self.record / rel).stat().st_size})
        doc = {"schema": ow.SCHEMA_FINALIZED_V2, "source_root": str(self.record), "entries": entries,
               "closure": {"links": {}, "ignored": {}, "mirror": None, "ignored_policy": {},
                           "files": {str(p): {"sha256": ow.hash_file(p)[0], "size": p.stat().st_size} for p in inputs},
                           "inputs": {str(p): {"real": str(p)} for p in inputs}}}
        raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
        self.manifest.write_bytes(raw)
        self.manifest_sha = fixtures.sha(raw)
        return doc

    def terminal_outside(self):
        night = self.tmp / "mbp/external-terminal"
        night.mkdir(parents=True)
        for rel in list(self.files):
            if rel.startswith("custody/night/"):
                (night / Path(rel).name).write_bytes(self.files.pop(rel))
                (self.record / rel).unlink()
        return night

    def run_pack(self, pack_dir, night, **over):
        return self.run_offload(harvest_pack=pack_dir, pack=False, terminal=str(night / "result.json"), **over)

    # S1-04: the Air copy must be restorable on its own before anything is deleted.
    def test_pack_omitting_bound_terminal_inputs_is_refused(self):
        night = self.terminal_outside()
        self.finalized(inputs=sorted(night.iterdir()))
        pack_dir = self.tmp / "mbp/harvest-pack"
        fixtures.build_harvest_pack(self.record, pack_dir, self.manifest_sha, externals=())
        self.assertEqual(self.run_pack(pack_dir, night), 2)
        self.assertIn("harvest_pack_not_restorable", self.span()["reason"])
        self.assertEqual(self.transport.calls, [])

    def test_release_refuses_a_copy_that_is_not_restorable(self):
        night = self.terminal_outside()
        self.finalized(inputs=sorted(night.iterdir()))
        pack_dir = self.tmp / "mbp/harvest-pack"
        fixtures.build_harvest_pack(self.record, pack_dir, self.manifest_sha, externals=sorted(night.iterdir()))
        self.assertEqual(self.run_pack(pack_dir, night), 0)
        self.confirm_second_copy()
        path = self.state / "w1-test" / ow.MANIFEST_NAME
        manifest = ow.read_json(path)
        manifest["externals"] = manifest["externals"][1:]  # as if one bound input had not travelled
        path.write_bytes(ow.canonical(manifest))
        with self.assertRaises(ow.Refusal) as caught:
            self.offload().release()
        self.assertIn("not_restorable_from_the_copy", str(caught.exception))
        self.assert_nothing_deleted()

    def test_native_restore_from_the_air_copy_with_external_terminal_evidence(self):
        harvest = native_harvest()
        night = self.terminal_outside()
        inputs = tuple(sorted(night.iterdir()))
        finalized = harvest.finalized_manifest(self.record, inputs=inputs)
        raw = json.dumps(finalized, sort_keys=True, separators=(",", ":")).encode()
        self.manifest.write_bytes(raw)
        self.manifest_sha = fixtures.sha(raw)
        pack_dir = self.tmp / "mbp/harvest-pack"
        harvest.pack(self.record, pack_dir, finalized=finalized, threads=1, external=inputs)
        self.assertEqual(self.run_pack(pack_dir, night), 0)
        inbox = self.store / "inbox/w1-test"
        with ow.decompressed({"name": "zstd"}, inbox / ow.HARVEST_PAYLOAD) as stream:
            with tarfile.open(fileobj=stream, mode="r|") as archive:
                carried = sorted(m.name for m in archive if m.name.startswith(".external/"))
        self.assertEqual(len(carried), len(inputs))  # every bound terminal input travels in the copy
        receipt = ow.check_sealed(ow.read_json(self.store / "windows/w1-test" / ow.AIR_RECEIPT))
        self.assertEqual(receipt["externals_verified"], len(inputs))
        self.confirm_second_copy()
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
        self.assertFalse(pack_dir.exists())
        self.record.rmdir()  # unpack requires an absent destination; release leaves the empty root
        harvest.unpack(inbox, finalized=finalized, finalized_sha256=self.manifest_sha)
        for rel, row in finalized["entries"].items():
            if "sha256" in row:
                self.assertEqual(ow.hash_file(self.record / rel), (row["sha256"], row["size"]), rel)

    # F2: a pack directory serves one window at a time.
    def test_reused_harvest_pack_directory_is_refused_and_kept(self):
        self.finalized()
        pack_dir = self.tmp / "mbp/shared-harvest-output/offload"
        fixtures.build_harvest_pack(self.record, pack_dir, self.manifest_sha)
        args = dict(harvest_pack=pack_dir, pack=False)
        self.assertEqual(self.run_offload(**args), 0)
        self.confirm_second_copy()
        payload, transport_manifest = pack_dir / ow.HARVEST_PAYLOAD, pack_dir / ow.HARVEST_MANIFEST
        payload.write_bytes(b"next window's sole compressed payload")
        transport_manifest.write_bytes(b"next window's sole transport manifest")
        with self.assertRaises(ow.Mismatch) as caught:
            self.offload().release()
        self.assertIn("local_pack_changed", str(caught.exception))
        self.assertEqual(payload.read_bytes(), b"next window's sole compressed payload")
        self.assertEqual(transport_manifest.read_bytes(), b"next window's sole transport manifest")
        self.assert_nothing_deleted()

    def test_second_window_cannot_claim_an_unreleased_pack_path(self):
        self.finalized()
        pack_dir = self.tmp / "mbp/shared-harvest-output/offload"
        fixtures.build_harvest_pack(self.record, pack_dir, self.manifest_sha)
        self.assertEqual(self.run_offload(harvest_pack=pack_dir, pack=False), 0)
        # A second window's session and finalize, packed into the same (recreated) directory.
        other = self.tmp / "mbp/night-align/w2-test"
        shutil.copytree(self.record, other)
        doc = json.loads(self.manifest.read_bytes())
        doc["source_root"] = str(other)
        raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
        manifest2 = self.tmp / "mbp/w2-finalized.json"
        manifest2.write_bytes(raw)
        moved = self.tmp / "mbp/w1-pack-moved-aside"
        pack_dir.rename(moved)
        fixtures.build_harvest_pack(other, pack_dir, fixtures.sha(raw))
        rc = self.run_offload(window_id="w2-test", record_root=other, record_manifest=manifest2,
                              record_manifest_sha256=fixtures.sha(raw), harvest_pack=pack_dir, pack=False)
        self.assertEqual(rc, 3)
        self.assertIn("harvest_pack_path_held_by:w1-test", self.span("w2-test")["reason"])

    def test_consumed_pack_is_byte_identical_and_never_repacked(self):
        self.finalized()
        pack_dir = self.tmp / "mbp/harvest-pack"
        fixtures.build_harvest_pack(self.record, pack_dir, self.manifest_sha)
        originals = {p.name: p.read_bytes() for p in pack_dir.iterdir()}
        with mock.patch.object(ow.Offload, "pack", side_effect=AssertionError("unexpected repack")):
            self.assertEqual(self.run_offload(harvest_pack=pack_dir, pack=False), 0)
        for name, raw in originals.items():
            self.assertEqual((self.store / "inbox/w1-test" / name).read_bytes(), raw)
        self.assertFalse(list((self.state / "w1-test/parts").iterdir()))

    def test_wrong_finalized_pin_is_rejected(self):
        self.finalized()
        pack_dir = self.tmp / "mbp/harvest-pack"
        fixtures.build_harvest_pack(self.record, pack_dir, "f" * 64)
        self.assertEqual(self.run_offload(harvest_pack=pack_dir, pack=False), 3)
        self.assertEqual(self.transport.calls, [])
        self.assert_nothing_deleted()


if __name__ == "__main__":
    unittest.main()
