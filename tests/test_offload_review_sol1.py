"""Independent review witnesses for Air offload at 175f0c8b9.

All paths and data are synthetic. The existing fixture supplies only a temporary
store, fake volume probe, fake cloud and in-process gate transport. Tests named
``witness`` deliberately assert the reviewed defect, so a passing witness means
the defect reproduced; these are not assertions that the behavior is safe.
No real process census, setup script, network or measurement input is used.
"""
from __future__ import annotations

import contextlib
import fcntl
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import types
from unittest import mock
import unittest

from tests import test_offload_window as fixtures

ow = fixtures.ow


class ReviewWitnesses(fixtures.Fixture):
    def verified(self, **kwargs):
        self.assertEqual(self.run_offload(codec="gzip", **kwargs), 0)
        self.confirm_second_copy()

    def release_cli(self):
        # Patch the CLI boundary, not release(), triage(), or the locking code.
        with mock.patch.object(ow, "_transport", return_value=self.transport), \
                mock.patch.object(ow, "default_state_probe", return_value=lambda: self.probe_state), \
                contextlib.redirect_stdout(io.StringIO()):
            return ow.main(["release", "--state-root", str(self.state), "--window-id", "w1-test"])

    def test_witness_same_size_nonduplicate_is_deleted(self):
        duplicate = self.tmp / "mbp/backup/w1-test"
        duplicate.mkdir(parents=True)
        # Use a nonempty member to distinguish equal length from equal content.
        rel = "members/m01/outputs/align_turns.jsonl"
        original = self.files[rel]
        different = b"X" * len(original)
        target = duplicate / rel
        target.parent.mkdir(parents=True)
        target.write_bytes(different)
        self.assertNotEqual(ow.hash_file(target)[0], fixtures.sha(original))
        self.verified(duplicate_root=[duplicate])
        result = self.offload().release()
        self.assertFalse(target.exists())  # Unbacked bytes have been unlinked.
        self.assertEqual(result["skipped"], [])
        self.assertEqual((self.store / "windows/w1-test/raw" / rel).read_bytes(), original)
        # Both confirmed custody copies contain the original digest, not the lost one.
        self.assertEqual((self.store / "inbox/w1-test" / ow.MANIFEST_NAME).read_bytes(),
                         (self.icloud / "w1-test" / ow.MANIFEST_NAME).read_bytes())
        self.assertNotIn(fixtures.sha(different),
                         (self.store / "inbox/w1-test" / ow.MANIFEST_NAME).read_text())

    def test_different_size_duplicate_is_preserved_control(self):
        duplicate = self.tmp / "mbp/backup/w1-test"
        duplicate.mkdir(parents=True)
        target = duplicate / "empty.txt"
        target.write_bytes(b"not empty")
        self.verified(duplicate_root=[duplicate])
        result = self.offload().release()
        self.assertEqual(target.read_bytes(), b"not empty")
        self.assertEqual(result["skipped"][0]["reason"], "duplicate_differs")

    def test_witness_standalone_release_ignores_active_offload_lock(self):
        self.verified()
        fd = os.open(self.state / ".lock", os.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(self.release_cli(), 0)
            self.assertTrue((self.state / "w1-test/released.json").is_file())
            self.assertFalse((self.record / "empty.txt").exists())
        finally:
            os.close(fd)

    def test_witness_standalone_release_is_invisible_to_triage_and_unbounded(self):
        self.verified()
        old_span = (self.state / "w1-test/timing/offload-span.json").read_bytes()
        observations = []
        runner = self.transport

        def observing_runner(command, **kwargs):
            if command.startswith("receipts "):
                observations.append((kwargs["timeout"], ow.triage(
                    self.state, "w1-test", self.clock.t + 121, 120)))
                # A slow release crosses the entire pre-dwell margin. No real wait.
                self.clock.t += 200
            return runner(command, **kwargs)

        with mock.patch.object(ow, "_transport", return_value=observing_runner), \
                mock.patch.object(ow, "default_state_probe", return_value=lambda: self.probe_state), \
                contextlib.redirect_stdout(io.StringIO()):
            rc = ow.main(["release", "--state-root", str(self.state), "--window-id", "w1-test"])
        self.assertEqual(rc, 0)
        self.assertEqual(len(observations), 1)
        timeout, during_release = observations[0]
        self.assertIsNone(timeout)
        self.assertTrue(during_release["quiet_start_state_ok"])
        self.assertEqual((self.state / "w1-test/timing/offload-span.json").read_bytes(), old_span)
        self.assertTrue(ow.triage(self.state, "w1-test",
                                  during_release["dwell_start_epoch_s"], 120)["quiet_start_state_ok"])

    def test_witness_failed_ps_census_reports_quiet(self):
        agents = self.tmp / "empty-launch-agents"
        agents.mkdir()
        failed = subprocess.CompletedProcess(["/bin/ps"], 1, stdout="", stderr="census unavailable")
        with mock.patch.object(ow.subprocess, "run", return_value=failed):
            state = ow.default_state_probe(launch_agents=agents)()
        self.assertEqual(state, {"armed": [], "measuring": []})
        # This is the same probe result accepted at the admission boundary.
        off = self.offload()
        off.state_probe = lambda: state
        off.check_quiet_allowed()

    def test_nonce_replay_is_rejected_control(self):
        self.verified()
        replay = self.transport("receipts w1-test " + "0" * 32)[1]
        self.transport.replace_reply = lambda command, raw: replay if command.startswith("receipts ") else raw
        with self.assertRaisesRegex(ow.Mismatch, "fresh_receipt_does_not_match"):
            self.offload().release()
        self.assert_nothing_deleted()

    def test_live_volume_uuid_change_is_rejected_control(self):
        self.verified()
        self.probe.default["volume_uuid"] = "REPLACEMENT-VOLUME"
        with self.assertRaisesRegex(ow.TransportError, "store_volume_uuid_mismatch"):
            self.offload().release()
        self.assert_nothing_deleted()

    def test_decayed_air_part_is_rejected_control(self):
        self.verified()
        part = next((self.store / "inbox/w1-test").glob("part-*.tar.gz"))
        raw = bytearray(part.read_bytes())
        raw[len(raw) // 2] ^= 1
        part.write_bytes(raw)
        with self.assertRaisesRegex(ow.Mismatch, "air_part_decayed"):
            self.offload().release()
        self.assert_nothing_deleted()


@unittest.skipUnless(ow.zstd_cli(), "consumed harvest packs require zstd")
class ConsumedPackWitnesses(fixtures.Fixture):
    def terminal_outside_pack(self):
        night = self.tmp / "mbp/external-terminal"
        night.mkdir(parents=True)
        for rel in list(self.files):
            if rel.startswith("custody/night/"):
                (night / Path(rel).name).write_bytes(self.files.pop(rel))
                (self.record / rel).unlink()
        entries = {}
        for rel, (kind, _) in ow.scan_tree(self.record).items():
            entries[rel] = ({"directory": True} if kind == "dir" else
                            {"sha256": ow.hash_file(self.record / rel)[0],
                             "size": (self.record / rel).stat().st_size})
        inputs = sorted(night.iterdir())
        finalized = {"schema": ow.SCHEMA_FINALIZED_V2, "source_root": str(self.record), "entries": entries,
                     "closure": {"links": {}, "files": {
                         str(p): {"sha256": ow.hash_file(p)[0], "size": p.stat().st_size} for p in inputs},
                         "ignored": {}, "inputs": {str(p): {"real": str(p)} for p in inputs},
                         "mirror": None, "ignored_policy": {}}}
        raw = json.dumps(finalized, sort_keys=True, separators=(",", ":")).encode()
        self.manifest.write_bytes(raw)
        self.manifest_sha = fixtures.sha(raw)
        pack_dir = self.tmp / "mbp/harvest-pack"
        # Ordinary producer omission: finalize declares inputs but pack was called
        # without --external for the external terminal files.
        fixtures.build_harvest_pack(self.record, pack_dir, self.manifest_sha, externals=())
        return night, pack_dir

    def test_witness_bound_external_terminal_is_absent_from_both_copies(self):
        night, pack_dir = self.terminal_outside_pack()
        before = (pack_dir / ow.HARVEST_PAYLOAD).read_bytes()
        self.assertEqual(self.run_offload(harvest_pack=pack_dir, pack=False,
                                          terminal=str(night / "result.json")), 0)
        inbox = self.store / "inbox/w1-test"
        self.assertEqual((inbox / ow.HARVEST_PAYLOAD).read_bytes(), before)
        self.assertFalse(any((self.state / "w1-test/parts").iterdir()))
        manifest = ow.read_json(self.state / "w1-test" / ow.MANIFEST_NAME)
        self.assertEqual(manifest["externals"], [])
        self.assertGreater(manifest["closure_external_not_offloaded"], 0)
        self.confirm_second_copy()
        self.offload().release()
        # The MBP retains these external files; the tool has NOT backed them up.
        self.assertTrue((night / "result.json").is_file())
        for copy in (inbox, self.icloud / "w1-test"):
            with ow.decompressed({"name": "zstd"}, copy / ow.HARVEST_PAYLOAD) as stream:
                with tarfile.open(fileobj=stream, mode="r|") as archive:
                    self.assertFalse(any(m.name.startswith(".external/") or m.name.endswith("result.json")
                                         for m in archive))
        receipt = ow.check_sealed(ow.read_json(self.store / "windows/w1-test" / ow.AIR_RECEIPT))
        self.assertEqual(receipt["externals_verified"], 0)

    def test_wrong_finalized_pin_is_rejected_control(self):
        night, pack_dir = self.terminal_outside_pack()
        hpath = pack_dir / ow.HARVEST_MANIFEST
        hdoc = ow.read_json(hpath)
        hdoc["finalized_manifest_sha256"] = "f" * 64
        hpath.write_bytes(ow.canonical(hdoc))
        self.assertEqual(self.run_offload(harvest_pack=pack_dir, pack=False,
                                          terminal=str(night / "result.json")), 3)
        self.assertEqual(self.transport.calls, [])
        self.assert_nothing_deleted()

    def test_witness_native_restore_requires_omitted_external_terminal(self):
        # The producer is on a sibling lane, not in this checkout. Pin its code
        # object so this integration witness needs neither a network nor a path
        # into another worktree. Ordinary shallow CI clones may lack the object.
        blob = "d279ab46f8cb3eae288545c8265948e325b24eba"
        result = subprocess.run(["git", "cat-file", "blob", blob], cwd=fixtures.ROOT,
                                capture_output=True)
        if result.returncode:
            self.skipTest("pinned harvest-off code object is unavailable")
        self.assertEqual(fixtures.sha(result.stdout),
                         "1ba0cc107aaa8c0b63b598ed46e0b89b97d04a314d513f54f40d7b9964e28293")
        harvest = types.ModuleType("review_sol1_native_harvest")
        exec(compile(result.stdout, "git-blob:" + blob, "exec"), harvest.__dict__)
        night, pack_dir = self.terminal_outside_pack()
        finalized = harvest.finalized_manifest(self.record, inputs=tuple(sorted(night.iterdir())))
        raw = json.dumps(finalized, sort_keys=True, separators=(",", ":")).encode()
        self.manifest.write_bytes(raw)
        self.manifest_sha = fixtures.sha(raw)
        fixtures.shutil.rmtree(pack_dir)
        harvest.pack(self.record, pack_dir, finalized=finalized, threads=1, external=())
        self.assertEqual(self.run_offload(harvest_pack=pack_dir, pack=False,
                                          terminal=str(night / "result.json")), 0)
        self.confirm_second_copy()
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")
        self.record.rmdir()  # unpack requires an absent destination; release leaves the empty root.
        night.rename(night.with_name("withheld-terminal-inputs"))  # the Air lacks these MBP files.
        with self.assertRaisesRegex(harvest.OffloadRefused, "external closure input differs"):
            harvest.unpack(self.store / "inbox/w1-test", finalized=finalized,
                           finalized_sha256=self.manifest_sha)


if __name__ == "__main__":
    unittest.main()
