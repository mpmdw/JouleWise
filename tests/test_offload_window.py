"""Synthetic records and an in-process fake transport for scripts/offload_window.py.

No network, no ssh, no hardware: the fake runner calls the Air gate directly.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("offload_window", ROOT / "scripts/offload_window.py")
ow = importlib.util.module_from_spec(SPEC)
sys.modules["offload_window"] = ow
SPEC.loader.exec_module(ow)


class Clock:
    def __init__(self, t=1_800_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


class FakeTransport:
    """Runs the Air gate in process. Hooks inject transit faults."""

    def __init__(self, air_root: Path, *, extract=True, clock=None):
        self.air_root, self.extract, self.clock = air_root, extract, clock
        self.calls, self.sent = [], 0
        self.corrupt_put = False
        self.cut_put_after = None  # bytes delivered before the connection drops
        self.advance_on = {}       # verb -> seconds to advance the fake clock

    def __call__(self, command, *, stdin_path=None, offset=0, timeout=None):
        self.calls.append(command)
        verb = command.split()[0]
        if self.clock is not None and verb in self.advance_on:
            self.clock.t += self.advance_on[verb]
        data = b""
        if stdin_path is not None:
            with open(stdin_path, "rb") as stream:
                stream.seek(offset)
                data = stream.read()
            if self.corrupt_put and data:
                data = bytes([data[0] ^ 0xFF]) + data[1:]
                self.corrupt_put = False
            if self.cut_put_after is not None and command.split()[2].startswith("part-"):
                data, self.cut_put_after = data[:self.cut_put_after], None
            self.sent += len(data)
        out = io.BytesIO()
        rc = ow.gate_main(self.air_root, self.extract, command, io.BytesIO(data), out)
        return rc, out.getvalue(), b""


class FakeCloud:
    def __init__(self):
        self.dataless, self.uploaded = set(), True

    def evict(self, path):
        if not self.uploaded:
            raise ow.subprocess.CalledProcessError(1, ["brctl", "evict"])
        self.dataless.add(str(path))

    def download(self, path):
        self.dataless.discard(str(path))

    def is_dataless(self, path):
        return str(path) in self.dataless

    def sleep(self, seconds):
        pass


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.record = self.tmp / "mbp/night-align/w1-test"
        self.state = self.tmp / "mbp/offload-state"
        self.air = self.tmp / "air/JW-AIR/offload"
        self.icloud = self.tmp / "air/icloud/JouleWise-offload"
        self.air.mkdir(parents=True)
        self.files = {
            "members/m01/raw/powermetrics.plist": b"<plist>" + os.urandom(3000) * 3 + b"</plist>\0",
            "members/m01/raw/powermetrics_idle.plist": b"<plist>idle</plist>\0" * 500,
            "members/m01/outputs/align_turns.jsonl": b'{"turn":0}\n' * 50,
            "members/m02/raw/powermetrics.plist": b"<plist>" + os.urandom(1_200_000) + b"</plist>\0",
            "custody/night/chain-stages.jsonl": b'{"stage_id":"s1"}\n',
            "empty.txt": b"",
        }
        for rel, raw in self.files.items():
            path = self.record / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        (self.record / "NOTE-unlisted.md").write_bytes(b"not in the record manifest\n")
        lines = "".join(f"{sha(raw)}  {rel}\n" for rel, raw in sorted(self.files.items()))
        self.manifest = self.tmp / "mbp/SHA256SUMS"
        self.manifest.write_text(lines)
        self.manifest_sha = sha(lines.encode())
        self.clock = Clock()
        self.transport = FakeTransport(self.air, clock=self.clock)
        self.probe_state = {"armed": [], "measuring": []}

    def args(self, **over):
        values = dict(state_root=self.state, window_id="w1-test", record_root=self.record,
                      record_manifest=self.manifest, record_manifest_sha256=self.manifest_sha,
                      duplicate_root=[], codec="auto", level=3, threads=2, part_mib=1, hash_on_mbp=False,
                      deadline_epoch=None, budget_s=600.0, safety=1.5, release_older=True,
                      min_free_gib=0.0, pressure_compressed_local=False)
        values.update(over)
        return SimpleNamespace(**values)

    def run_offload(self, **over):
        with open(os.devnull, "w") as sink, _redirect(sink):
            return ow.run_offload(self.args(**over), runner=self.transport,
                                  state_probe=lambda: self.probe_state, now=self.clock)

    def offload(self, window="w1-test"):
        return ow.Offload(self.state, window, runner=self.transport, now=self.clock,
                          state_probe=lambda: self.probe_state)

    def span(self, window="w1-test"):
        return json.loads((self.state / window / "timing/offload-span.json").read_text())

    def confirm_second_copy(self):
        return ow.second_copy(self.air, self.icloud, cloud=FakeCloud(), now=self.clock)


class _redirect:
    def __init__(self, sink):
        self.sink = sink

    def __enter__(self):
        self.old, sys.stdout = sys.stdout, self.sink

    def __exit__(self, *exc):
        sys.stdout = self.old


class HappyPath(Fixture):
    def test_round_trip_verify_second_copy_release(self):
        self.assertEqual(self.run_offload(), 0)
        span = self.span()
        self.assertEqual(span["outcome"], "verified_on_air")
        self.assertEqual(span["release_held"], "second_copy_not_confirmed")
        self.assertEqual(span["kind"], "backup")  # window_timing journal kind -> phase "offload"
        self.assertTrue(span["ended_before_deadline"])
        manifest = json.loads((self.state / "w1-test/offload-manifest.json").read_text())
        self.assertGreater(len(manifest["parts"]), 1)  # 1 MiB parts force a split
        self.assertEqual(manifest["unlisted_not_offloaded"], ["NOTE-unlisted.md"])
        for rel, raw in self.files.items():  # the Air holds byte-identical raw files
            self.assertEqual((self.air / "windows/w1-test/raw" / rel).read_bytes(), raw)
        receipt = json.loads((self.state / "w1-test/receipt-air.json").read_text())
        ow.check_sealed(receipt)
        self.assertEqual(receipt["files_verified"], len(self.files))
        self.assertTrue((self.record / "members/m01/raw/powermetrics.plist").exists())  # still kept

        self.assertEqual(self.confirm_second_copy(), ["w1-test"])
        result = self.offload().release()
        self.assertEqual(result["files_deleted"], len(self.files))
        for rel in self.files:
            self.assertFalse((self.record / rel).exists())
        self.assertTrue((self.record / "NOTE-unlisted.md").exists())  # never verified, never deleted
        self.assertFalse(any((self.state / "w1-test/parts").glob("part-*.tar.zst")))
        self.assertEqual(self.offload().release(), result)  # idempotent

    def test_next_run_releases_older_window(self):
        self.assertEqual(self.run_offload(), 0)
        self.confirm_second_copy()
        other = self.tmp / "mbp/night-align/w2"
        other.mkdir(parents=True)
        (other / "a.plist").write_bytes(b"x" * 100)
        manifest = self.tmp / "mbp/w2.SUMS"
        manifest.write_text(f"{sha(b'x' * 100)}  a.plist\n")
        rc = self.run_offload(window_id="w2", record_root=other, record_manifest=manifest,
                              record_manifest_sha256=sha(manifest.read_bytes()))
        self.assertEqual(rc, 0)
        self.assertEqual(self.span("w2")["older"][0]["rule"], "two_verified_copies")
        self.assertFalse((self.record / "members/m01/raw/powermetrics.plist").exists())

    def test_r1_harvest_manifest_and_gzip_fallback(self):
        doc = {"schema": ow.SCHEMA_R1, "root": str(self.record),
               "files": {rel: sha(raw) for rel, raw in self.files.items()}}
        raw = (json.dumps(doc, indent=2, sort_keys=True) + "\n").encode()
        self.manifest.write_bytes(raw)
        self.assertEqual(self.run_offload(record_manifest_sha256=sha(raw), codec="gzip"), 0)
        manifest = json.loads((self.state / "w1-test/offload-manifest.json").read_text())
        self.assertEqual(manifest["codec"]["name"], "gzip")
        self.assertTrue(all(p["name"].endswith(".tar.gz") for p in manifest["parts"]))

    def test_without_zstd_cli_falls_back_to_stdlib(self):
        saved = ow.zstd_cli
        ow.zstd_cli = lambda: None
        self.addCleanup(setattr, ow, "zstd_cli", saved)
        self.assertEqual(self.run_offload(), 0)
        codec = json.loads((self.state / "w1-test/offload-manifest.json").read_text())["codec"]
        self.assertEqual(codec["impl"], "zstd-stdlib" if ow.stdlib_zstd() else "gzip-stdlib")

    def test_r1_manifest_root_must_match(self):
        doc = {"schema": ow.SCHEMA_R1, "root": str(self.tmp), "files": {"empty.txt": sha(b"")}}
        raw = json.dumps(doc).encode()
        self.manifest.write_bytes(raw)
        self.assertEqual(self.run_offload(record_manifest_sha256=sha(raw)), 2)

    def test_duplicate_root(self):
        dup = self.tmp / "mbp/backup/w1-test"
        for rel, raw in self.files.items():
            (dup / rel).parent.mkdir(parents=True, exist_ok=True)
            (dup / rel).write_bytes(raw)
        (dup / "members/m01/outputs/align_turns.jsonl").write_bytes(b"a different backup\n")
        self.assertEqual(self.run_offload(duplicate_root=[dup]), 0)
        self.confirm_second_copy()
        result = self.offload().release()
        self.assertEqual(result["files_deleted"], 2 * len(self.files) - 1)
        self.assertEqual([s["path"] for s in result["skipped"]], ["members/m01/outputs/align_turns.jsonl"])
        self.assertTrue((dup / "members/m01/outputs/align_turns.jsonl").exists())
        self.assertFalse((dup / "members/m01/raw/powermetrics.plist").exists())

    def test_no_extract_mode_verifies_without_raw_tree(self):
        self.transport.extract = False
        self.assertEqual(self.run_offload(), 0)
        self.assertFalse((self.air / "windows/w1-test/raw").exists())


class Refusals(Fixture):
    def assert_nothing_deleted(self):
        for rel in self.files:
            self.assertTrue((self.record / rel).exists(), rel)

    def test_armed_refuses_before_any_work(self):
        self.probe_state = {"armed": ["com.joulewise.night.plist"], "measuring": []}
        self.assertEqual(self.run_offload(), 2)
        self.assertFalse((self.state / "w1-test/plan.json").exists())
        self.assertEqual(self.transport.calls, [])

    def test_measuring_refuses(self):
        self.probe_state = {"armed": [], "measuring": ["123 /usr/bin/powermetrics -i 100"]}
        self.assertEqual(self.run_offload(), 2)
        self.assertEqual(self.transport.calls, [])

    def test_default_probe_sees_armed_agent(self):
        agents = self.tmp / "LaunchAgents"
        agents.mkdir()
        (agents / "com.joulewise.magistrate.plist").write_text("")  # watchdog: not armed
        probe = ow.default_state_probe(agents)
        self.assertEqual(probe()["armed"], [])
        (agents / "com.joulewise.night.plist").write_text("")
        self.assertEqual(probe()["armed"], ["com.joulewise.night.plist"])
        self.assertTrue(ow.MEASURING.search("812 /usr/bin/python3 /x/scripts/run_night.py --arm"))
        self.assertTrue(ow.MEASURING.search("812 python3 -m mlx_lm.generate"))
        self.assertFalse(ow.MEASURING.search("812 python3 scripts/offload_window.py run"))

    def test_record_manifest_pin_mismatch(self):
        self.assertEqual(self.run_offload(record_manifest_sha256="0" * 64), 3)
        self.assertEqual(self.transport.calls, [])

    def test_raw_corruption_is_caught_on_the_air_end_to_end(self):
        path = self.record / "members/m02/raw/powermetrics.plist"
        raw = bytearray(path.read_bytes())
        raw[100] ^= 1  # same size: only the Air's digest check can see it
        stat = path.stat()
        path.write_bytes(bytes(raw))
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(self.run_offload(), 3)
        self.assertIn("raw_digest", self.span()["reason"])
        self.assertFalse((self.air / "windows/w1-test/air-receipt.json").exists())
        self.assertFalse((self.air / "windows/w1-test/raw").exists())
        self.assert_nothing_deleted()

    def test_hash_on_mbp_catches_corruption_before_sending(self):
        path = self.record / "members/m02/raw/powermetrics.plist"
        raw = bytearray(path.read_bytes())
        raw[10] ^= 1
        stat = path.stat()
        path.write_bytes(bytes(raw))
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(self.run_offload(hash_on_mbp=True), 3)
        self.assertIn("mbp_hash_mismatch", self.span()["reason"])
        self.assertFalse(any(c.startswith("put") for c in self.transport.calls))

    def test_transit_corruption_fails_closed_then_resends(self):
        self.transport.corrupt_put = True
        self.assertEqual(self.run_offload(), 3)
        self.assertIn("commit_digest_mismatch", self.span()["reason"])
        self.assertFalse(any((self.air / "inbox/w1-test").glob("*.partial")))  # restart from zero
        self.assertEqual(self.run_offload(), 0)

    def test_local_part_corruption_after_pack(self):
        off = self.offload()
        manifest = off.pack(self.record, self.manifest, self.manifest_sha, codec=ow.choose_codec("auto", 3, 2),
                            part_bytes=1 << 20)
        part = self.state / "w1-test/parts" / manifest["parts"][0]["name"]
        part.write_bytes(part.read_bytes()[:-1] + b"\0")
        self.assertEqual(self.run_offload(), 3)
        self.assert_nothing_deleted()

    def test_interrupted_push_resumes_from_offset(self):
        self.transport.cut_put_after = 700
        self.assertEqual(self.run_offload(), 5)
        self.assertEqual(self.span()["outcome"], "TransportError")
        first = self.transport.sent
        partials = list((self.air / "inbox/w1-test").glob("*.partial"))
        self.assertEqual([p.stat().st_size for p in partials], [700])
        self.transport.sent = 0
        self.assertEqual(self.run_offload(), 0)
        total = sum(p.stat().st_size for p in (self.air / "inbox/w1-test").iterdir())
        already = 700 + (self.air / "inbox/w1-test/record-manifest.bin").stat().st_size
        self.assertEqual(self.transport.sent + already, total)  # nothing re-sent
        self.assertGreater(first, 0)

    def test_partial_copy_never_verifies_or_releases(self):
        off = self.offload()
        manifest = off.pack(self.record, self.manifest, self.manifest_sha, codec=ow.choose_codec("auto", 3, 2),
                            part_bytes=1 << 20)
        first = manifest["parts"][0]["name"]
        out = io.BytesIO()
        data = (self.state / "w1-test/parts" / first).read_bytes()
        ow.gate_main(self.air, True, f"put w1-test {first} 0 {len(data)}", io.BytesIO(data), out)
        ow.gate_main(self.air, True, f"commit w1-test {first} {len(data)} {sha(data)}", io.BytesIO(), out)
        raw = (self.state / "w1-test/offload-manifest.json").read_bytes()
        ow.gate_main(self.air, True, f"put w1-test offload-manifest.json 0 {len(raw)}", io.BytesIO(raw), out)
        ow.gate_main(self.air, True, f"commit w1-test offload-manifest.json {len(raw)} {sha(raw)}",
                     io.BytesIO(), out)
        self.assertNotEqual(ow.gate_main(self.air, True, "verify w1-test", io.BytesIO(), io.BytesIO()), 0)
        with self.assertRaises(ow.Refusal) as caught:
            off.release()
        self.assertEqual(str(caught.exception), "no_air_receipt")
        self.assert_nothing_deleted()

    def test_duplicate_run_is_idempotent(self):
        self.assertEqual(self.run_offload(), 0)
        calls = len(self.transport.calls)
        self.assertEqual(self.run_offload(), 0)
        later = self.transport.calls[calls:]
        self.assertFalse(any(c.startswith(("put", "verify")) for c in later))

    def test_duplicate_window_id_with_different_content(self):
        self.assertEqual(self.run_offload(), 0)
        other = self.tmp / "mbp/w1-other.SUMS"
        other.write_text(f"{sha(b'')}  empty.txt\n")
        self.assertEqual(self.run_offload(record_manifest=other, record_manifest_sha256=sha(other.read_bytes())), 3)
        self.assertIn("duplicate_run_conflict", self.span()["reason"])

    def test_window_id_conflict_on_air(self):
        self.assertEqual(self.run_offload(), 0)
        other = self.tmp / "mbp/w1-other.SUMS"
        other.write_text(f"{sha(b'')}  empty.txt\n")
        rc = self.run_offload(state_root=self.tmp / "mbp/other-state", record_manifest=other,
                              record_manifest_sha256=sha(other.read_bytes()))
        self.assertEqual(rc, 3)
        span = json.loads((self.tmp / "mbp/other-state/w1-test/timing/offload-span.json").read_text())
        self.assertIn("window_id_conflict_on_air", span["reason"])

    def test_concurrent_run_refused(self):
        import fcntl
        self.state.mkdir(parents=True)
        fd = os.open(self.state / ".lock", os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            self.assertEqual(self.run_offload(), 2)
            report = ow.triage(self.state, "w1-test", self.clock.t + 3600, 120)
            self.assertIn("offload_running", report["reasons"])
        finally:
            os.close(fd)

    def test_symlinked_file_or_directory_refused(self):
        target = self.tmp / "elsewhere.plist"
        target.write_bytes(self.files["empty.txt"])
        (self.record / "empty.txt").unlink()
        (self.record / "empty.txt").symlink_to(target)
        self.assertEqual(self.run_offload(), 3)
        (self.record / "empty.txt").unlink()
        (self.record / "empty.txt").write_bytes(b"")
        moved = self.tmp / "m02"
        shutil.move(self.record / "members/m02", moved)
        (self.record / "members/m02").symlink_to(moved)
        self.assertEqual(self.run_offload(), 3)

    def test_gate_rejects_unlisted_verbs_and_names(self):
        for command in ("rm -rf /", "put w1-test ../../etc/passwd 0 1", "stat ../x", "verify", "put w1 x y z"):
            out = io.BytesIO()
            self.assertNotEqual(ow.gate_main(self.air, True, command, io.BytesIO(b"x"), out), 0, command)
        self.assertEqual(sorted(p.name for p in self.air.iterdir()), ["inbox", "locks", "queue", "windows"])


class Deadline(Fixture):
    def test_predicted_overrun_refuses_before_any_work(self):
        self.state.mkdir(parents=True)
        (self.state / "rates.json").write_text(json.dumps({"pack_raw_mb_s": 1e-4}))
        self.assertEqual(self.run_offload(budget_s=60), 4)
        self.assertEqual(self.span()["reason"], "deadline:predicted_overrun")
        self.assertFalse((self.state / "w1-test/plan.json").exists())
        self.assertEqual(self.transport.calls, [])

    def test_deadline_mid_run_stops_resumably_and_before_dwell(self):
        deadline = self.clock.t + 300
        self.transport.advance_on = {"put": 200}  # a slow network
        self.assertEqual(self.run_offload(deadline_epoch=deadline), 4)
        span = self.span()
        self.assertTrue(span["reason"].startswith("deadline"))
        self.assertFalse((self.air / "windows/w1-test/air-receipt.json").exists())
        dwell_start = deadline + 120
        self.assertLessEqual(span["ended_epoch_s"], self.clock.t)
        report = ow.triage(self.state, "w1-test", dwell_start, 120)
        self.assertEqual(report["quiet_start_state_ok"], span["ended_epoch_s"] <= dwell_start - 120)
        self.transport.advance_on = {}
        self.assertEqual(self.run_offload(deadline_epoch=self.clock.t + 600), 0)  # next turnaround resumes

    def test_triage_flags_dwell_overlap_and_crash(self):
        self.assertEqual(self.run_offload(), 0)
        end = self.span()["ended_epoch_s"]
        self.assertTrue(ow.triage(self.state, "w1-test", end + 121, 120)["quiet_start_state_ok"])
        self.assertIn("offload_ended_inside_dwell_margin",
                      ow.triage(self.state, "w1-test", end + 60, 120)["reasons"])
        start = self.state / "w1-test/timing/offload-start.json"
        doc = json.loads(start.read_text())
        doc["started_epoch_s"] = end + 10  # a newer run that never wrote its end receipt
        start.write_text(json.dumps(doc))
        self.assertIn("offload_started_without_end_receipt",
                      ow.triage(self.state, "w1-test", end + 1000, 120)["reasons"])


class TwoCopyRule(Fixture):
    """Delete only after a verified Air receipt AND a confirmed second copy."""

    def setUp(self):
        super().setUp()
        self.assertEqual(self.run_offload(), 0)

    def assert_kept(self):
        for rel in self.files:
            self.assertTrue((self.record / rel).exists(), rel)

    def test_air_receipt_only_is_not_enough(self):
        with self.assertRaises(ow.Refusal) as caught:
            self.offload().release()
        self.assertEqual(str(caught.exception), "second_copy_not_confirmed")
        self.assert_kept()

    def test_cloud_not_uploaded_keeps_queue_and_copy(self):
        cloud = FakeCloud()
        cloud.uploaded = False
        clock = Clock(self.clock.t)

        def tick():
            clock.t += 100
            return clock.t
        self.assertEqual(ow.second_copy(self.air, self.icloud, cloud=cloud, now=tick, wait_s=300), [])
        self.assertTrue((self.air / "queue/w1-test.json").exists())
        with self.assertRaises(ow.Refusal):
            self.offload().release()
        self.assert_kept()

    def test_forged_second_receipt_refused(self):
        self.confirm_second_copy()
        path = self.air / "windows/w1-test/second-copy-receipt.json"
        doc = json.loads(path.read_text())
        doc["confirmed_epoch_s"] += 1  # body no longer matches its receipt hash
        path.write_text(json.dumps(doc))
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        self.assert_kept()

    def test_second_receipt_for_other_bytes_refused(self):
        self.confirm_second_copy()
        path = self.air / "windows/w1-test/second-copy-receipt.json"
        body = ow.check_sealed(json.loads(path.read_text()))
        body["files"][0]["sha256"] = "f" * 64
        path.write_bytes(ow.canonical(ow.sealed(body)))
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        self.assert_kept()

    def test_tampered_air_receipt_refused(self):
        self.confirm_second_copy()
        path = self.air / "windows/w1-test/air-receipt.json"
        body = ow.check_sealed(json.loads(path.read_text()))
        body["files_verified"] -= 1
        path.write_bytes(ow.canonical(ow.sealed(body)))
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        self.assert_kept()

    def test_record_changed_after_offload_refuses_delete(self):
        self.confirm_second_copy()
        (self.record / "custody/night/chain-stages.jsonl").write_bytes(b"changed after offload\n")
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        for rel in self.files:  # checked before any unlink: nothing is half-released
            self.assertTrue((self.record / rel).exists(), rel)

    def test_both_receipts_delete_raw_and_parts(self):
        self.confirm_second_copy()
        result = self.offload().release()
        self.assertEqual(result["rule"], "two_verified_copies")
        for rel in self.files:
            self.assertFalse((self.record / rel).exists())

    def test_pressure_rule_keeps_two_verified_copies(self):
        result = self.offload().release(pressure_compressed_local=True)
        self.assertEqual(result["rule"], "pressure_compressed_local")
        for rel in self.files:
            self.assertFalse((self.record / rel).exists())
        parts = list((self.state / "w1-test/parts").glob("part-*.tar.zst"))
        self.assertTrue(parts)  # the MBP keeps the Air-verified compressed copy
        self.assertFalse((self.state / "w1-test/released.json").exists())
        self.confirm_second_copy()
        final = self.offload().release()
        self.assertEqual(final["rule"], "two_verified_copies")
        self.assertFalse(list((self.state / "w1-test/parts").glob("part-*.tar.zst")))

if __name__ == "__main__":
    unittest.main()
