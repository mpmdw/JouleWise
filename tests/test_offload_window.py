"""Synthetic records and an in-process fake transport for scripts/offload_window.py.

No network, no ssh, no hardware: the fake runner calls the Air gate directly, and a fake
volume probe stands in for diskutil. Temporary trees live under the real temp directory
(macOS: /private/tmp or /private/var, never through the /tmp or /var symlinks).
"""
from __future__ import annotations

import fcntl
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from contextlib import redirect_stderr as contextlib_redirect_stderr
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("offload_window", ROOT / "scripts/offload_window.py")
ow = importlib.util.module_from_spec(SPEC)
sys.modules["offload_window"] = ow
SPEC.loader.exec_module(ow)
TMP_BASE = Path(os.path.realpath(tempfile.gettempdir()))
TERMINAL = "custody/night/result.json"


class Clock:
    def __init__(self, t=1_800_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


class FakeProbe:
    """diskutil stand-in: per-mount identities, a switch for 'unmounted'."""

    def __init__(self):
        self.mounted_ok = True
        self.ids = {}
        self.default = {"volume_uuid": "UUID-PRIMARY", "volume_name": "JW-EXT", "internal": False,
                        "owners_enabled": True, "physical_stores": ["disk9s2"]}

    def mounted(self, path):
        return self.mounted_ok

    def identity(self, path):
        return dict(self.ids.get(str(path), self.default))


class FakeTransport:
    """Runs the Air gate in process. Hooks inject transit faults."""

    def __init__(self, binding: Path, probe, *, extract=True, clock=None):
        self.binding, self.probe, self.extract, self.clock = binding, probe, extract, clock
        self.calls, self.sent = [], 0
        self.corrupt_put = False
        self.cut_put_after = None  # bytes delivered before the connection drops
        self.advance_on = {}       # verb -> seconds to advance the fake clock
        self.before = None         # callable(command) run before each call
        self.replace_reply = None  # callable(command, reply_bytes) -> reply_bytes

    def __call__(self, command, *, stdin_path=None, offset=0, timeout=None):
        self.calls.append(command)
        verb = command.split()[0]
        if self.before is not None:
            self.before(command)
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
        rc = ow.gate_main(self.binding, self.extract, command, io.BytesIO(data), out, probe=self.probe)
        reply = out.getvalue()
        if self.replace_reply is not None:
            reply = self.replace_reply(command, reply)
        return rc, reply, b""


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


class _redirect:
    def __init__(self, sink):
        self.sink = sink

    def __enter__(self):
        self.old, sys.stdout = sys.stdout, self.sink

    def __exit__(self, *exc):
        sys.stdout = self.old


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(dir=TMP_BASE))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.record = self.tmp / "mbp/night-align/w1-test"
        self.state = self.tmp / "mbp/offload-state"
        self.vol = self.tmp / "air/JW-EXT"
        self.store = self.vol / "jw-offload"
        self.binding = self.tmp / "air/etc/store-binding.json"
        self.icloud = self.tmp / "air/icloud/JouleWise-offload"
        self.vol.mkdir(parents=True)
        self.binding.parent.mkdir(parents=True)
        self.probe = FakeProbe()
        ow.init_store(self.store, self.binding, probe=self.probe, mount_point=self.vol, min_free_gib=0)
        (self.store / "second").mkdir()
        self.files = {
            "members/m01/raw/powermetrics.plist": b"<plist>" + os.urandom(3000) * 3 + b"</plist>\0",
            "members/m01/raw/powermetrics_idle.plist": b"<plist>idle</plist>\0" * 500,
            "members/m01/outputs/align_turns.jsonl": b'{"turn":0}\n' * 50,
            "members/m02/raw/powermetrics.plist": b"<plist>" + os.urandom(1_200_000) + b"</plist>\0",
            "custody/night/chain-stages.jsonl": b'{"stage_id":"s1"}\n',
            TERMINAL: json.dumps({"plan_id": "plan-w1", "verdict": "GO", "ended_epoch_s": 1_799_999_000.0}).encode(),
            "custody/night/chain.started": b"{}",
            "custody/night/chain.exited": b'{"rc":0}',
            "custody/night/courier.sent": b"{}",
            "empty.txt": b"",
        }
        for rel, raw in self.files.items():
            path = self.record / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.manifest = self.tmp / "mbp/SHA256SUMS"
        self.write_manifest()
        self.clock = Clock()
        self.transport = FakeTransport(self.binding, self.probe, clock=self.clock)
        self.probe_state = {"armed": [], "measuring": []}

    def write_manifest(self, files=None):
        files = self.files if files is None else files
        lines = "".join(f"{sha(raw)}  {rel}\n" for rel, raw in sorted(files.items()))
        self.manifest.write_text(lines)
        self.manifest_sha = sha(lines.encode())

    def put_file(self, rel, raw, listed=True):
        path = self.record / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        if listed:
            self.files[rel] = raw
            self.write_manifest()

    def drop_file(self, rel):
        (self.record / rel).unlink()
        del self.files[rel]
        self.write_manifest()

    def args(self, **over):
        values = dict(state_root=self.state, window_id="w1-test", record_root=self.record,
                      record_manifest=self.manifest, record_manifest_sha256=self.manifest_sha, terminal=TERMINAL,
                      duplicate_root=[], codec="auto", level=3, threads=2, part_mib=1, hash_on_mbp=False,
                      deadline_epoch=None, budget_s=600.0, safety=1.5, release_older=True, rates_seed=None,
                      harvest_pack=None, pack=True,
                      min_free_gib=0.0)
        values.update(over)
        return SimpleNamespace(**values)

    def run_offload(self, lease=None, **over):
        with open(os.devnull, "w") as sink, _redirect(sink):
            return ow.run_offload(self.args(**over), runner=self.transport, state_probe=lambda: self.probe_state,
                                  now=self.clock, mono=self.clock, lease=lease)

    def offload(self, window="w1-test"):
        return ow.Offload(self.state, window, runner=self.transport, now=self.clock, mono=self.clock,
                          state_probe=lambda: self.probe_state)

    def span(self, window="w1-test", state=None):
        return json.loads(((state or self.state) / window / "timing/offload-span.json").read_text())

    def confirm_second_copy(self, cloud=None, internal_min_free_gib=0):
        return ow.second_copy_icloud(self.binding, self.icloud, cloud=cloud or FakeCloud(), probe=self.probe,
                                     now=self.clock, internal_min_free_gib=internal_min_free_gib)

    def assert_nothing_deleted(self):
        for rel in self.files:
            self.assertTrue((self.record / rel).exists(), rel)


class DeletionDecisionCharacterization(unittest.TestCase):
    # Written and committed against b4a6c217f before the Q10 fixes. These are
    # release() decisions for fixed custody states, not retry-stage decisions.
    CASES = (
        ("air_missing", False, "no_air_receipt"),
        ("air_only", False, "second_copy_not_confirmed"),
        ("local_second_only", False, "second_copy_not_confirmed"),
        ("both_verified", True, None),
        ("air_seal_changed", False, "receipt_hash_mismatch"),
        ("second_seal_changed", False, "receipt_hash_mismatch"),
        ("second_wrong_manifest", False, "second_copy_receipt_does_not_match"),
        ("fresh_missing", False, "no_fresh_receipt"),
        ("fresh_replayed", False, "fresh_receipt_does_not_match"),
        ("air_part_changed", False, "air_part_decayed"),
        ("local_part_changed", False, "local_pack_changed"),
        ("local_raw_changed", False, "content_differs_from_bound_digest"),
        ("armed", False, "window_armed"),
        ("deleting_without_air", False, "no_air_receipt"),
        ("deleting_without_second", False, "second_copy_not_confirmed"),
        ("deleting_with_both", True, None),
        ("released_latch", False, None),
    )

    def test_base_deletion_decisions(self):
        for state, may_delete, reason in self.CASES:
            with self.subTest(state=state):
                f = Fixture()
                f.setUp()
                try:
                    self._check_state(f, state, may_delete, reason)
                finally:
                    f.doCleanups()

    def _check_state(self, f, state, may_delete, reason):
        self.assertEqual(f.run_offload(codec="gzip"), 0)
        off = f.offload()
        manifest = ow.read_json(off.dir / ow.MANIFEST_NAME)
        no_second = {"air_missing", "air_only", "deleting_without_air", "deleting_without_second"}
        if state not in no_second:
            f.confirm_second_copy()
        air_path = f.store / "windows/w1-test" / ow.AIR_RECEIPT
        second_path = f.store / "second/w1-test" / ow.SECOND_RECEIPT
        if state in {"air_missing", "deleting_without_air"}:
            air_path.unlink()  # the stale MBP receipt remains
        elif state == "local_second_only":
            shutil.copyfile(second_path, off.dir / "receipt-second.json")
            second_path.unlink()
        elif state in {"air_seal_changed", "second_seal_changed", "second_wrong_manifest"}:
            path = air_path if state == "air_seal_changed" else second_path
            receipt = ow.read_json(path)
            receipt["offload_manifest_sha256"] = "0" * 64
            if state == "second_wrong_manifest":
                receipt = ow.sealed(ow.check_sealed(ow.read_json(path)) | {"offload_manifest_sha256": "0" * 64})
            path.write_bytes(ow.canonical(receipt))
        elif state in {"fresh_missing", "fresh_replayed"}:
            def replace(command, raw):
                if not command.startswith("receipts "):
                    return raw
                reply = json.loads(raw)
                reply["fresh"] = (None if state == "fresh_missing" else
                                  ow.sealed(ow.check_sealed(reply["fresh"]) | {"nonce": "0" * 32}))
                return ow.canonical(reply)
            f.transport.replace_reply = replace
        elif state in {"air_part_changed", "local_part_changed", "local_raw_changed"}:
            path = (f.store / "inbox/w1-test" / manifest["parts"][0]["name"] if state == "air_part_changed" else
                    off.parts_dir / manifest["parts"][0]["name"] if state == "local_part_changed" else
                    f.record / "members/m01/raw/powermetrics.plist")
            info = path.stat()
            raw = path.read_bytes()
            path.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
            os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
        elif state == "armed":
            f.probe_state["armed"] = ["synthetic-night.plist"]
        if state.startswith("deleting_"):
            rows, skipped = off._inventory(manifest)
            (off.dir / "deleting.json").write_bytes(ow.canonical({
                "schema": ow.SCHEMA_DELETING, "window_id": "w1-test", "state": "deleting",
                "record_manifest_sha256": manifest["record_manifest_sha256"],
                "rule": "two_verified_copies", "inventory": rows, "skipped": skipped,
            }))
        if state == "released_latch":
            (off.dir / "released.json").write_bytes(ow.canonical({"already": "released"}))
        if reason is not None:
            with self.assertRaisesRegex(ow.Refusal, reason):
                off.release()
        else:
            off.release()
        self.assertEqual(not (f.record / "empty.txt").exists(), may_delete)
        if not may_delete:
            f.assert_nothing_deleted()


class HappyPath(Fixture):
    def test_round_trip_verify_second_copy_release(self):
        self.assertEqual(self.run_offload(), 0)
        span = self.span()
        self.assertEqual(span["outcome"], "verified_on_air")
        self.assertEqual(span["release_held"], "second_copy_not_confirmed")
        self.assertEqual(span["kind"], "backup")  # window_timing journal kind -> phase "offload"
        self.assertEqual(span["interlock"], {"mode": "probe_only"})
        self.assertEqual(span["terminal"]["verdict"], "GO")
        self.assertTrue(span["ended_before_deadline"])
        manifest = json.loads((self.state / "w1-test/offload-manifest.json").read_text())
        self.assertGreater(len(manifest["parts"]), 1)  # 1 MiB parts force a split
        self.assertEqual(manifest["record_format"], "sha256sums")
        for rel, raw in self.files.items():  # the Air holds byte-identical raw files
            self.assertEqual((self.store / "windows/w1-test/raw" / rel).read_bytes(), raw)
        receipt = json.loads((self.state / "w1-test/receipt-air.json").read_text())
        body = ow.check_sealed(receipt)
        self.assertEqual(body["files_verified"], len(self.files))
        self.assertEqual(body["store_volume_uuid"], "UUID-PRIMARY")
        self.assertTrue((self.record / "members/m01/raw/powermetrics.plist").exists())  # still kept

        self.assertEqual(self.confirm_second_copy(), ["w1-test"])
        self.assertTrue((self.store / "second/w1-test" / ow.SECOND_RECEIPT).exists())
        result = self.offload().release()
        self.assertEqual(result["files_deleted"], len(self.files))
        for rel in self.files:
            self.assertFalse((self.record / rel).exists())
        self.assertEqual(list(self.record.iterdir()), [])  # only empty directories were removed, root kept
        self.assertFalse(any((self.state / "w1-test/parts").glob("part-*.tar.zst")))
        fresh = ow.check_sealed(json.loads((self.state / "w1-test/receipt-fresh.json").read_text()))
        self.assertEqual(len(fresh["rechecked"]), len(manifest["parts"]) + 2)
        journal = json.loads((self.state / "w1-test/deleting.json").read_text())
        self.assertEqual(journal["state"], "deleted")
        self.assertEqual(self.offload().release(), result)  # idempotent

    def test_next_run_releases_older_window(self):
        self.assertEqual(self.run_offload(), 0)
        self.confirm_second_copy()
        other = self.tmp / "mbp/night-align/smoke-w2"
        other.mkdir(parents=True)
        (other / "a.plist").write_bytes(b"x" * 100)
        manifest = self.tmp / "mbp/w2.SUMS"
        manifest.write_text(f"{sha(b'x' * 100)}  a.plist\n")
        rc = self.run_offload(window_id="smoke-w2", record_root=other, record_manifest=manifest,
                              record_manifest_sha256=sha(manifest.read_bytes()), terminal=None)
        self.assertEqual(rc, 0)
        self.assertEqual(self.span("smoke-w2")["older"][0]["rule"], "two_verified_copies")
        self.assertFalse((self.record / "members/m01/raw/powermetrics.plist").exists())

    def test_r1_harvest_manifest_and_gzip_fallback(self):
        doc = {"schema": ow.SCHEMA_R1, "root": str(self.record),
               "files": {rel: sha(raw) for rel, raw in self.files.items()}}
        raw = (json.dumps(doc, indent=2, sort_keys=True) + "\n").encode()
        self.manifest.write_bytes(raw)
        self.assertEqual(self.run_offload(record_manifest_sha256=sha(raw), codec="gzip"), 0)
        manifest = json.loads((self.state / "w1-test/offload-manifest.json").read_text())
        self.assertEqual(manifest["codec"]["name"], "gzip")
        self.assertEqual(manifest["record_format"], "r1_harvest_manifest.v1")
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
        rel = "members/m01/outputs/align_turns.jsonl"
        (dup / rel).write_bytes(b"a different backup\n")
        self.assertEqual(self.run_offload(duplicate_root=[dup]), 0)
        self.confirm_second_copy()
        with self.assertRaises(ow.Mismatch) as caught:  # review F1: a differing duplicate refuses the release
            self.offload().release()
        self.assertIn("duplicate_differs", str(caught.exception))
        self.assert_nothing_deleted()
        self.assertEqual((dup / rel).read_bytes(), b"a different backup\n")
        (dup / rel).write_bytes(self.files[rel])  # the operator dispositions the duplicate
        result = self.offload().release()
        self.assertEqual(result["files_deleted"], 2 * len(self.files))
        self.assertFalse((dup / "members/m01/raw/powermetrics.plist").exists())

    def test_no_extract_mode_verifies_without_raw_tree(self):
        self.transport.extract = False
        self.assertEqual(self.run_offload(), 0)
        self.assertFalse((self.store / "windows/w1-test/raw").exists())

    def test_rates_seed_then_observed_rates(self):
        seed = self.tmp / "seed.json"
        seed.write_text(json.dumps({"rates": {"pack_raw_mb_s": 123.0, "recheck_mb_s": 77.0}, "evidence": "x"}))
        rates = ow.load_rates(self.state, seed)
        self.assertEqual((rates["pack_raw_mb_s"], rates["recheck_mb_s"]), (123.0, 77.0))
        self.assertEqual(self.run_offload(rates_seed=seed), 0)
        self.assertEqual(self.span()["rates_used"]["pack_raw_mb_s"], 123.0)
        self.assertTrue((self.state / "rates.json").exists())  # observed rates override the seed next time

    def test_committed_rates_seed_is_valid(self):
        doc = json.loads(ow.RATES_SEED.read_text())
        self.assertEqual(set(doc["rates"]), set(ow.DEFAULT_RATES))
        self.assertTrue(all(v > 0 for v in doc["rates"].values()))


class Envelope(Fixture):
    """Agreement item 3: the record is exactly the manifest's closed envelope."""

    def test_unlisted_file_refuses_before_any_work(self):
        self.put_file("NOTE-unlisted.md", b"not in the record manifest\n", listed=False)
        self.assertEqual(self.run_offload(), 2)
        self.assertIn("envelope_unlisted_file:NOTE-unlisted.md", self.span()["reason"])
        self.assertEqual(self.transport.calls, [])
        self.assertFalse((self.state / "w1-test/plan.json").exists())

    def test_hard_link_refuses(self):
        os.link(self.record / "empty.txt", self.tmp / "outside-link")
        self.assertEqual(self.run_offload(), 2)
        self.assertIn("envelope_hard_link:empty.txt", self.span()["reason"])

    def test_git_and_restricted_members_refuse_without_entering(self):
        (self.record / ".git").mkdir()
        self.assertEqual(self.run_offload(), 2)
        self.assertIn("envelope_sealed_member:.git", self.span()["reason"])
        (self.record / ".git").rmdir()
        sealed = self.record / "members/restricted"
        sealed.mkdir()
        (sealed / "x").write_bytes(b"")
        sealed.chmod(0)  # an attempt to list it would raise PermissionError (exit 6), not a refusal
        self.addCleanup(sealed.chmod, 0o755)
        self.assertEqual(self.run_offload(), 2)
        self.assertIn("envelope_sealed_member:members/restricted", self.span()["reason"])

    def test_special_file_refuses(self):
        os.mkfifo(self.record / "fifo")
        self.assertEqual(self.run_offload(), 2)
        self.assertIn("envelope_special_file:fifo", self.span()["reason"])

    def test_unlisted_symlink_refuses(self):
        (self.record / "link").symlink_to("empty.txt")
        self.assertEqual(self.run_offload(), 2)
        self.assertIn("envelope_unlisted_symlink:link", self.span()["reason"])

    def test_symlinked_listed_file_or_directory_is_a_mismatch(self):
        target = self.tmp / "elsewhere.plist"
        target.write_bytes(b"")
        (self.record / "empty.txt").unlink()
        (self.record / "empty.txt").symlink_to(target)
        self.assertEqual(self.run_offload(), 3)
        (self.record / "empty.txt").unlink()
        (self.record / "empty.txt").write_bytes(b"")
        moved = self.tmp / "m02"
        shutil.move(self.record / "members/m02", moved)
        (self.record / "members/m02").symlink_to(moved)
        self.assertEqual(self.run_offload(), 3)

    def test_symlinked_record_root_refused(self):
        alias = self.tmp / "mbp/alias"
        alias.symlink_to(self.record)
        self.assertEqual(self.run_offload(record_root=alias), 3)

    def test_closed_record_size_mismatch(self):
        doc = {"schema": ow.SCHEMA_CLOSED, "closed": True,
               "files": {rel: {"sha256": sha(raw), "size": len(raw)} for rel, raw in self.files.items()}}
        doc["files"]["empty.txt"]["size"] = 1
        raw = json.dumps(doc).encode()
        self.manifest.write_bytes(raw)
        self.assertEqual(self.run_offload(record_manifest_sha256=sha(raw)), 3)
        self.assertIn("size_mismatch:empty.txt", self.span()["reason"])

    def test_ssd_closed_record_inside_the_record_travels_and_is_released(self):
        doc = {"schema": ow.SCHEMA_SSD, "state": "closed", "window_id": "w1-test",
               "files": {rel: sha(raw) for rel, raw in self.files.items()}}
        raw = (json.dumps(doc, sort_keys=True, indent=2) + "\n").encode()
        (self.record / "ssd-closed.json").write_bytes(raw)
        rc = self.run_offload(record_manifest=self.record / "ssd-closed.json", record_manifest_sha256=sha(raw))
        self.assertEqual(rc, 0)
        self.assertEqual((self.store / "windows/w1-test/raw/ssd-closed.json").read_bytes(), raw)
        self.confirm_second_copy()
        self.offload().release()
        self.assertFalse((self.record / "ssd-closed.json").exists())

    def test_unsupported_or_schemaless_manifest_refuses(self):
        for doc in ({"files": {"empty.txt": sha(b"")}}, {"schema": "joulewise.other.v9", "files": {}}):
            raw = json.dumps(doc).encode()
            self.manifest.write_bytes(raw)
            self.assertEqual(self.run_offload(record_manifest_sha256=sha(raw)), 2)

    def test_harvest_window_inventory(self):
        inv = {"custody-root": {".": {"mode": 0o40755}}}
        for rel, raw in self.files.items():
            inv["custody-root"][rel] = {"mode": 0o100644, "sha256": sha(raw), "size": len(raw)}
        doc = {"schema": ow.SCHEMA_HARVEST, "custody_root": "/absolute/never/opened", "inventory": inv}
        env = ow.parse_record_manifest(json.dumps(doc).encode(), self.tmp)
        self.assertEqual(env.fmt, "harvest_window.v1")
        self.assertEqual(set(env.files), {f"custody-root/{rel}" for rel in self.files})
        doc["inventory"]["custody-root"]["l"] = {"mode": 0o120777}
        with self.assertRaises(ow.Refusal):
            ow.parse_record_manifest(json.dumps(doc).encode(), self.tmp)


def build_harvest_pack(root: Path, out: Path, finalized_sha: str, externals=(), external_directories=()) -> dict:
    """The harvest-off lane's pack format (harvest_offload._pack): payload.tar.zst + MANIFEST.json.
    Mirrors its walk, rows and manifest keys; the end-to-end run checks against the real module."""
    out.mkdir(parents=True)
    rows, outside = {}, {}
    payload = out / "payload.tar.zst"
    with payload.open("wb") as sink:
        proc = subprocess.Popen([ow.zstd_cli(), "-q", "-3", "-T4", "-c"], stdin=subprocess.PIPE, stdout=sink)
        with ow.tarfile.open(fileobj=proc.stdin, mode="w|", format=ow.tarfile.PAX_FORMAT) as tar:
            for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
                rel = path.relative_to(root).as_posix()
                info = os.lstat(path)
                ti = ow.tarfile.TarInfo(rel)
                ti.mode, ti.mtime = ow.stat.S_IMODE(info.st_mode), int(info.st_mtime)
                if path.is_symlink():
                    ti.type, ti.linkname = ow.tarfile.SYMTYPE, os.readlink(path)
                    tar.addfile(ti)
                    rows[rel] = {"link": ti.linkname}
                elif path.is_dir():
                    ti.type = ow.tarfile.DIRTYPE
                    tar.addfile(ti)
                    rows[rel] = {"dir": True, "mode": ti.mode}
                else:
                    raw = path.read_bytes()
                    ti.size = len(raw)
                    tar.addfile(ti, io.BytesIO(raw))
                    rows[rel] = {"sha256": sha(raw), "size": len(raw), "mode": ti.mode}
            for index, path in enumerate(externals):
                raw = Path(path).read_bytes()
                ti = ow.tarfile.TarInfo(f".external/{index:04d}")
                ti.size, ti.mode = len(raw), 0o644
                tar.addfile(ti, io.BytesIO(raw))
                outside[ti.name] = {"path": str(path), "sha256": sha(raw), "size": len(raw), "mode": 0o644}
        proc.stdin.close()
        assert proc.wait() == 0
    manifest = {"schema": ow.SCHEMA_HARVEST_PACK, "source_root": str(root), "entries": rows, "external": outside,
                "files": sum("sha256" in r for r in rows.values()), "bytes": sum(r.get("size", 0) for r in rows.values()),
                "payload": {"name": "payload.tar.zst", "sha256": sha(payload.read_bytes()), "size": payload.stat().st_size},
                "zstd_level": 3, "finalized_manifest_sha256": finalized_sha,
                "external_directories": list(external_directories)}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


class FinalizedManifestV2(Fixture):
    """Lead ruling 2026-11-08, one pack per window: a finalized_manifest.v2 record is packed once by the
    harvest-off lane, and the offload consumes that pack (verify, transport, second copy, release)."""

    def setUp(self):
        super().setUp()
        (self.record / "view").symlink_to("/Users/edr/measurement-checkout/configs")  # literal, never followed
        (self.record / "members/m01/latest").symlink_to("raw")
        (self.record / "members/m03/empty").mkdir(parents=True)
        self.ledger = self.tmp / "mbp/checkout/runs/calibration-ledger.jsonl"
        self.ledger.parent.mkdir(parents=True)
        self.ledger.write_bytes(b'{"cal":1}\n')
        self.pack_dir = self.tmp / "mbp/jw-wt/offload/w1-test/offload"

    def v2(self, inputs=()):
        entries = {}
        for path in sorted(self.record.rglob("*")):
            rel = path.relative_to(self.record).as_posix()
            if path.is_symlink():
                entries[rel] = {"link": os.readlink(path)}
            elif path.is_dir():
                entries[rel] = {"directory": True}
            else:
                raw = path.read_bytes()
                entries[rel] = {"sha256": sha(raw), "size": len(raw)}
        bound = [self.ledger, *inputs]
        doc = {"schema": ow.SCHEMA_FINALIZED_V2, "source_root": str(self.record), "entries": entries,
               "closure": {"links": {}, "ignored": {}, "mirror": None, "ignored_policy": {},
                           "inputs": {str(p): {"real": str(p)} for p in bound},
                           "files": {str(p): {"sha256": sha(p.read_bytes()), "size": p.stat().st_size} for p in bound}}}
        raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()  # canonical bytes, as finalize writes
        out = self.tmp / "mbp/finalized_manifest.json"
        out.write_bytes(raw)
        self.v2_path, self.v2_sha = out, sha(raw)
        return out, sha(raw)

    def packed(self, inputs=(), **over):
        self.v2(inputs)
        self.hmanifest = build_harvest_pack(self.record, self.pack_dir, over.pop("bound_to", self.v2_sha),
                                            externals=over.pop("externals", [self.ledger, *inputs]))
        return dict(record_manifest=self.v2_path, record_manifest_sha256=self.v2_sha, harvest_pack=self.pack_dir,
                    pack=False, **over)

    def test_consumes_the_harvest_pack_without_repacking(self):
        self.assertEqual(self.run_offload(**self.packed()), 0)
        span = self.span()
        self.assertEqual([s["name"] for s in span["stages"]], ["release_older", "adopt_harvest_pack", "push",
                                                                "verify"])  # release held: no second copy yet
        self.assertEqual(span["pack_format"], ow.SCHEMA_HARVEST_PACK)
        self.assertFalse(any((self.state / "w1-test/parts").iterdir()))  # nothing packed on this side
        inbox = self.store / "inbox/w1-test"
        self.assertEqual((inbox / "payload.tar.zst").read_bytes(), (self.pack_dir / "payload.tar.zst").read_bytes())
        self.assertEqual((inbox / "MANIFEST.json").read_bytes(), (self.pack_dir / "MANIFEST.json").read_bytes())
        self.assertEqual((inbox / "record-manifest.bin").read_bytes(), self.v2_path.read_bytes())
        body = ow.check_sealed(json.loads((self.store / "windows/w1-test/air-receipt.json").read_text()))
        self.assertEqual((body["links_verified"], body["dirs_verified"], body["externals_verified"]), (2, 10, 1))
        self.assertFalse(body["extracted"])  # the harvest restore is the raw tree for v4 sessions
        self.assertFalse((self.store / "windows/w1-test/raw").exists())
        manifest = json.loads((self.state / "w1-test/offload-manifest.json").read_text())
        self.assertEqual(manifest["closure_external_not_offloaded"], 0)
        self.confirm_second_copy()
        names = {r["name"] for r in ow.check_sealed(json.loads(
            (self.store / "second/w1-test" / ow.SECOND_RECEIPT).read_text()))["files"]}
        self.assertEqual(names, {"payload.tar.zst", "MANIFEST.json", ow.MANIFEST_NAME, ow.RECORD_MANIFEST_NAME})
        result = self.offload().release()
        self.assertEqual((result["files_deleted"], result["links_deleted"]), (len(self.files), 2))
        self.assertEqual(list(self.record.iterdir()), [])
        self.assertFalse(self.pack_dir.exists())  # payload and MANIFEST.json gone; the empty directory too
        self.assertTrue(self.ledger.exists())     # a closure input is never deleted

    def test_pack_mode_refuses_a_v2_record(self):
        path, digest = self.v2()
        self.assertEqual(self.run_offload(record_manifest=path, record_manifest_sha256=digest), 2)
        self.assertIn("finalized_manifest_v2_is_packed_once_by_harvest_off", self.span()["reason"])

    def test_pack_bound_to_another_finalize_is_a_mismatch(self):
        self.assertEqual(self.run_offload(**self.packed(bound_to="e" * 64)), 3)
        self.assertIn("harvest_pack_bound_to_another_finalize", self.span()["reason"])
        self.assertEqual(self.transport.calls, [])

    def test_pack_entries_must_equal_the_finalize(self):
        args = self.packed()
        doc = json.loads((self.pack_dir / "MANIFEST.json").read_text())
        doc["entries"]["empty.txt"]["sha256"] = "f" * 64
        (self.pack_dir / "MANIFEST.json").write_text(json.dumps(doc))
        self.assertEqual(self.run_offload(**args), 3)
        self.assertIn("harvest_pack_entries_differ_from_finalize", self.span()["reason"])

    def test_unbound_external_is_a_mismatch(self):
        args = self.packed()
        doc = json.loads((self.pack_dir / "MANIFEST.json").read_text())
        doc["external"][".external/0000"]["path"] = "/elsewhere/ledger.jsonl"
        (self.pack_dir / "MANIFEST.json").write_text(json.dumps(doc))
        self.assertEqual(self.run_offload(**args), 3)
        self.assertIn("harvest_pack_external_not_bound", self.span()["reason"])

    def test_corrupt_payload_is_caught_by_the_air(self):
        args = self.packed()
        payload = self.pack_dir / "payload.tar.zst"
        raw = bytearray(payload.read_bytes())
        raw[len(raw) // 2] ^= 1  # same size: only the Air's digest check can see it
        payload.write_bytes(bytes(raw))
        self.assertEqual(self.run_offload(**args), 3)
        self.assertIn("commit_digest_mismatch:payload.tar.zst", self.span()["reason"])
        self.assertFalse((self.store / "windows/w1-test/air-receipt.json").exists())
        self.assert_nothing_deleted()

    def test_member_outside_the_finalize_is_caught_by_the_air(self):
        args = self.packed()
        # A self-consistent pack (payload digest and MANIFEST agree) whose payload holds an extra member.
        (self.record / "smuggled.bin").write_bytes(b"x")
        shutil.rmtree(self.pack_dir)
        hm = build_harvest_pack(self.record, self.pack_dir, self.v2_sha, externals=[self.ledger])
        (self.record / "smuggled.bin").unlink()
        hm["entries"].pop("smuggled.bin")
        (self.pack_dir / "MANIFEST.json").write_text(json.dumps(hm, indent=2, sort_keys=True) + "\n")
        self.assertEqual(self.run_offload(**args), 3)
        self.assertIn("unexpected_member:smuggled.bin", self.span()["reason"])

    def test_unlisted_directory_refuses(self):
        args = self.packed()
        (self.record / "late-dir").mkdir()
        self.assertEqual(self.run_offload(**args), 2)
        self.assertIn("envelope_unlisted_dir:late-dir", self.span()["reason"])

    def test_link_target_changed_is_a_mismatch(self):
        args = self.packed()
        (self.record / "view").unlink()
        (self.record / "view").symlink_to("/somewhere/else")
        self.assertEqual(self.run_offload(**args), 3)

    def test_source_root_must_be_the_record_root(self):
        args = self.packed()
        other = self.tmp / "mbp/elsewhere"
        shutil.copytree(self.record, other, symlinks=True)
        self.assertEqual(self.run_offload(record_root=other, **args), 2)

    # Lead ruling 2026-11-08: terminal evidence outside the session root is a bound closure input.
    def move_terminal_outside(self):
        night = self.tmp / "mbp/custody/night"
        night.mkdir(parents=True)
        for rel in [r for r in self.files if r.startswith("custody/night/")]:
            (night / Path(rel).name).write_bytes(self.files.pop(rel))
            (self.record / rel).unlink()
        (self.record / "custody/night").rmdir()
        (self.record / "custody").rmdir()
        return night

    def test_terminal_evidence_as_closure_inputs(self):
        night = self.move_terminal_outside()
        args = self.packed(inputs=sorted(night.iterdir()), terminal=str(night / "result.json"))
        self.assertEqual(self.run_offload(**args), 0)
        self.assertEqual(self.span()["terminal"]["terminal"], str(night / "result.json"))

    def test_terminal_marker_present_but_unbound_refuses(self):
        night = self.move_terminal_outside()
        bound = sorted(night.iterdir())
        (night / "chain.unkilled").write_text("{}")
        args = self.packed(inputs=bound, terminal=str(night / "result.json"))
        self.assertEqual(self.run_offload(**args), 2)
        self.assertIn("terminal_marker_not_in_closure", self.span()["reason"])

    def test_terminal_marker_bound_but_absent_or_changed(self):
        night = self.move_terminal_outside()
        args = self.packed(inputs=sorted(night.iterdir()), terminal=str(night / "result.json"))
        (night / "courier.sent").unlink()
        self.assertEqual(self.run_offload(**args), 3)
        self.assertIn("terminal_marker_bound_but_absent", self.span()["reason"])
        (night / "courier.sent").write_text("{x}")  # back, other bytes
        self.assertEqual(self.run_offload(**args), 3)
        self.assertIn("terminal_digest_mismatch", self.span()["reason"])

    def test_terminal_outside_must_be_bound(self):
        night = self.move_terminal_outside()
        args = self.packed(terminal=str(night / "result.json"))  # not declared as inputs
        self.assertEqual(self.run_offload(**args), 2)
        self.assertIn("terminal_not_in_closure", self.span()["reason"])


class Terminal(Fixture):
    """Agreement item 2: the record is terminal before anything is packed."""

    def expect(self, rc, reason, **over):
        self.assertEqual(self.run_offload(**over), rc)
        self.assertIn(reason, self.span()["reason"])
        self.assertEqual(self.transport.calls, [])

    def result(self, **fields):
        doc = {"plan_id": "plan-w1", "verdict": "GO", "ended_epoch_s": 1_799_999_000.0, **fields}
        self.put_file(TERMINAL, json.dumps(doc).encode())

    def test_courier_not_sent(self):
        self.drop_file("custody/night/courier.sent")
        self.expect(2, "terminal_courier_not_sent")

    def test_unkilled_chain(self):
        self.put_file("custody/night/chain.unkilled", b"{}")
        self.expect(2, "terminal_chain_unkilled")

    def test_open_chain(self):
        self.drop_file("custody/night/chain.exited")
        self.expect(2, "terminal_chain_open_or_ambiguous")

    def test_unknown_verdict_or_future_end(self):
        self.result(verdict="RUNNING")
        self.expect(2, "record_is_not_terminal")
        self.result(ended_epoch_s=self.clock.t + 60)
        self.expect(2, "record_is_not_terminal")

    def test_zero_capture_refused_window_without_chain_markers(self):
        self.drop_file("custody/night/chain.started")
        self.drop_file("custody/night/chain.exited")
        self.result(verdict="REFUSED")
        self.assertEqual(self.run_offload(), 0)

    def test_result_bytes_must_match_the_manifest(self):
        path = self.record / TERMINAL
        path.write_bytes(path.read_bytes().replace(b"GO", b"OK"))  # same size, SHA256SUMS has no sizes
        self.expect(3, "terminal_digest_mismatch")

    def test_terminal_must_be_listed(self):
        self.expect(2, "terminal_not_in_manifest", terminal="custody/night/other.json")

    def test_skipping_the_check_is_for_synthetic_windows_only(self):
        self.expect(2, "terminal_evidence_required", terminal=None)
        self.assertEqual(self.run_offload(terminal=None, window_id="smoke-20261108"), 0)


class Refusals(Fixture):
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
        info = path.stat()
        path.write_bytes(bytes(raw))
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
        self.assertEqual(self.run_offload(), 3)
        self.assertIn("raw_digest", self.span()["reason"])
        self.assertFalse((self.store / "windows/w1-test/air-receipt.json").exists())
        self.assertFalse((self.store / "windows/w1-test/raw").exists())
        self.assert_nothing_deleted()

    def test_hash_on_mbp_catches_corruption_before_sending(self):
        path = self.record / "members/m02/raw/powermetrics.plist"
        raw = bytearray(path.read_bytes())
        raw[10] ^= 1
        info = path.stat()
        path.write_bytes(bytes(raw))
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
        self.assertEqual(self.run_offload(hash_on_mbp=True), 3)
        self.assertIn("mbp_hash_mismatch", self.span()["reason"])
        self.assertFalse(any(c.startswith("put") for c in self.transport.calls))

    def test_transit_corruption_fails_closed_then_resends(self):
        self.transport.corrupt_put = True
        self.assertEqual(self.run_offload(), 3)
        self.assertIn("commit_digest_mismatch", self.span()["reason"])
        self.assertFalse(any((self.store / "inbox/w1-test").glob("*.partial")))  # restart from zero
        self.assertEqual(self.run_offload(), 0)

    def test_local_part_corruption_after_pack(self):
        off = self.offload()
        manifest = off.pack(self.record, self.manifest, self.manifest_sha, codec=ow.choose_codec("auto", 3, 2),
                            part_bytes=1 << 20, terminal=TERMINAL)
        part = self.state / "w1-test/parts" / manifest["parts"][0]["name"]
        part.write_bytes(part.read_bytes()[:-1] + b"\0")
        self.assertEqual(self.run_offload(), 3)
        self.assert_nothing_deleted()

    def test_interrupted_push_resumes_from_offset(self):
        self.transport.cut_put_after = 700
        self.assertEqual(self.run_offload(), 5)
        self.assertEqual(self.span()["outcome"], "TransportError")
        first = self.transport.sent
        partials = list((self.store / "inbox/w1-test").glob("*.partial"))
        self.assertEqual([p.stat().st_size for p in partials], [700])
        self.transport.sent = 0
        self.assertEqual(self.run_offload(), 0)
        total = sum(p.stat().st_size for p in (self.store / "inbox/w1-test").iterdir())
        already = 700 + (self.store / "inbox/w1-test/record-manifest.bin").stat().st_size
        self.assertEqual(self.transport.sent + already, total)  # nothing re-sent
        self.assertGreater(first, 0)

    def test_partial_copy_never_verifies_or_releases(self):
        off = self.offload()
        manifest = off.pack(self.record, self.manifest, self.manifest_sha, codec=ow.choose_codec("auto", 3, 2),
                            part_bytes=1 << 20, terminal=TERMINAL)
        first = manifest["parts"][0]["name"]

        def gate(command, data=b""):
            return ow.gate_main(self.binding, True, command, io.BytesIO(data), io.BytesIO(), probe=self.probe)
        data = (self.state / "w1-test/parts" / first).read_bytes()
        gate(f"put w1-test {first} 0 {len(data)}", data)
        gate(f"commit w1-test {first} {len(data)} {sha(data)}")
        raw = (self.state / "w1-test/offload-manifest.json").read_bytes()
        gate(f"put w1-test offload-manifest.json 0 {len(raw)}", raw)
        gate(f"commit w1-test offload-manifest.json {len(raw)} {sha(raw)}")
        self.assertNotEqual(gate("verify w1-test"), 0)
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
        files = {rel: raw for rel, raw in self.files.items() if rel != "empty.txt"}
        (self.record / "empty.txt").unlink()
        self.write_manifest(files)
        rc = self.run_offload(state_root=self.tmp / "mbp/other-state", record_manifest_sha256=self.manifest_sha)
        self.assertEqual(rc, 3)
        self.assertIn("window_id_conflict_on_air", self.span(state=self.tmp / "mbp/other-state")["reason"])

    def test_concurrent_run_refused(self):
        self.state.mkdir(parents=True)
        fd = os.open(self.state / ".lock", os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            self.assertEqual(self.run_offload(), 2)
            report = ow.triage(self.state, "w1-test", self.clock.t + 3600, 120)
            self.assertIn("offload_running", report["reasons"])
        finally:
            os.close(fd)

    def test_gate_rejects_unlisted_verbs_and_names(self):
        for command in ("rm -rf /", "put w1-test ../../etc/passwd 0 1", "stat ../x", "verify", "put w1 x y z",
                        "receipts w1-test notanonce", "hello extra", "stat 'unterminated"):
            out = io.BytesIO()
            rc = ow.gate_main(self.binding, True, command, io.BytesIO(b"x"), out, probe=self.probe)
            self.assertNotEqual(rc, 0, command)
        self.assertEqual(sorted(p.name for p in self.store.iterdir()),
                         [ow.MARKER_NAME, "inbox", "locks", "queue", "second", "windows"])


class Interlock(Fixture):
    """Agreement item 1: the magistrate lease and loop lock, used when the magistrate passes them."""

    def setUp(self):
        super().setUp()
        ops = self.tmp / "mbp/ops"
        ops.mkdir(parents=True)
        self.lease_path, self.watch, self.loop = ops / "offload-gate.json", ops / "watchdog.json", ops / "loop.lock"
        self.loop.write_text("")
        self.watch.write_text(json.dumps({"fenced_checkouts": []}))
        self.write_lease()

    def write_lease(self, **over):
        doc = {"schema": ow.SCHEMA_LEASE, "generation": "cooldown-w1-1", "phase": "cooldown", "armed": False,
               "measuring": False, "record_manifest_sha256": self.manifest_sha, "record_committed": True,
               "record_pushed": True, "quiet_dwell_epoch_s": self.clock.t + 900, "expires_epoch_s": self.clock.t + 900}
        doc.update(over)
        self.lease_path.write_text(json.dumps(doc))

    def lease(self):
        return ow.Lease(self.lease_path, self.watch, self.loop, self.manifest_sha, now=self.clock)

    def test_lease_path_and_deadline(self):
        self.assertEqual(self.run_offload(lease=self.lease(), budget_s=3600), 0)
        span = self.span()
        self.assertEqual(span["interlock"], {"mode": "lease+loop_lock+probe", "generation": "cooldown-w1-1"})
        self.assertEqual(span["deadline_epoch_s"], self.clock.t + 900 - 120)

    def test_lease_refusals_before_any_work(self):
        for over in ({"armed": True}, {"measuring": True}, {"phase": "dwell"}, {"record_pushed": False},
                     {"record_manifest_sha256": "0" * 64}, {"schema": "other"}, {"generation": ""}):
            self.write_lease(**over)
            self.assertEqual(self.run_offload(lease=self.lease()), 2, over)
        self.write_lease()
        self.watch.write_text(json.dumps({"fenced_checkouts": ["plan-x"]}))
        self.assertEqual(self.run_offload(lease=self.lease()), 2)
        self.assertEqual(self.transport.calls, [])

    def test_generation_change_mid_run_refuses(self):
        def flip(command):
            if command.startswith("put"):
                self.write_lease(generation="arming-w2")
        self.transport.before = flip
        self.assertEqual(self.run_offload(lease=self.lease()), 2)
        self.assertIn("lease_generation_changed", self.span()["reason"])
        self.assertFalse((self.store / "windows/w1-test/air-receipt.json").exists())
        self.assert_nothing_deleted()

    def test_loop_lock_held_by_the_magistrate(self):
        fd = os.open(self.loop, os.O_RDWR)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            self.assertEqual(self.run_offload(lease=self.lease()), 2)
        finally:
            os.close(fd)
        self.assertEqual(self.transport.calls, [])

    def test_loop_lock_is_never_created(self):
        self.loop.unlink()
        self.assertEqual(self.run_offload(lease=self.lease()), 2)
        self.assertFalse(self.loop.exists())

    def test_lease_end_bounds_the_deadline(self):
        self.write_lease(quiet_dwell_epoch_s=self.clock.t + 130)  # 10 s left after the 120 s margin
        self.assertEqual(self.run_offload(lease=self.lease()), 4)
        self.write_lease(expires_epoch_s=self.clock.t + 60)
        self.assertEqual(self.run_offload(lease=self.lease()), 4)
        self.assertEqual(self.transport.calls, [])

    def test_probe_still_runs_with_the_lease(self):
        self.probe_state = {"armed": ["com.joulewise.align-w2.plist"], "measuring": []}
        self.assertEqual(self.run_offload(lease=self.lease()), 2)


class StoreBinding(Fixture):
    """The landing store refuses an unmounted, different or full volume."""

    def test_unmounted_volume_is_resumable_and_writes_nothing(self):
        self.probe.mounted_ok = False
        self.assertEqual(self.run_offload(), 5)
        self.assertIn("store_not_mounted", self.span()["reason"])
        self.assertFalse((self.store / "inbox").exists())

    def test_other_volume_uuid_refused(self):
        self.probe.default["volume_uuid"] = "UUID-OTHER"
        self.assertEqual(self.run_offload(), 5)
        self.assertIn("store_volume_uuid_mismatch", self.span()["reason"])

    def test_marker_missing_refused(self):
        (self.store / ow.MARKER_NAME).unlink()
        self.assertEqual(self.run_offload(), 5)
        self.assertIn("store_marker_missing", self.span()["reason"])

    def test_ownership_ignored_refused_unless_allowed(self):
        self.probe.default["owners_enabled"] = False
        self.assertEqual(self.run_offload(), 5)
        self.assertIn("store_volume_ignores_ownership", self.span()["reason"])

    def test_free_floor_refused(self):
        ow.init_store(self.store, self.binding, probe=self.probe, mount_point=self.vol, min_free_gib=1e9)
        self.assertEqual(self.run_offload(), 5)
        self.assertIn("air_ssd_space", self.span()["reason"])
        out = io.BytesIO()
        self.assertNotEqual(ow.gate_main(self.binding, True, "put w1-test part-0000.tar.zst 0 1", io.BytesIO(b"x"),
                                         out, probe=self.probe), 0)
        self.assertIn(b"store_below_free_floor", out.getvalue())

    def test_init_store_is_idempotent_and_binds_once(self):
        doc = json.loads(self.binding.read_text())
        again = ow.init_store(self.store, self.binding, probe=self.probe, mount_point=self.vol, min_free_gib=0)
        self.assertEqual(again["store_id"], doc["store_id"])
        self.probe.default["volume_uuid"] = "UUID-OTHER"
        with self.assertRaises(ow.Mismatch):
            ow.init_store(self.store, self.binding, probe=self.probe, mount_point=self.vol)

    def test_init_store_refuses_internal_boot_and_noowners(self):
        self.probe.default["internal"] = True
        with self.assertRaises(ow.Refusal):
            ow.init_store(self.vol / "s2", self.tmp / "b2.json", probe=self.probe, mount_point=self.vol)
        self.probe.default["internal"] = False
        with self.assertRaises(ow.Refusal):
            ow.init_store(self.tmp / "s3", self.tmp / "b3.json", probe=self.probe, mount_point=Path("/"))
        self.probe.default["owners_enabled"] = False
        with self.assertRaises(ow.Refusal):
            ow.init_store(self.vol / "s4", self.tmp / "b4.json", probe=self.probe, mount_point=self.vol)
        ow.init_store(self.vol / "s4", self.tmp / "b4.json", probe=self.probe, mount_point=self.vol,
                      allow_noowners=True)


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
        self.assertFalse((self.store / "windows/w1-test/air-receipt.json").exists())
        dwell_start = deadline + 120
        report = ow.triage(self.state, "w1-test", dwell_start, 120)
        self.assertEqual(report["quiet_start_state_ok"], span["ended_epoch_s"] <= dwell_start - 120)
        self.transport.advance_on = {}
        self.assertEqual(self.run_offload(deadline_epoch=self.clock.t + 600), 0)  # next turnaround resumes

    def test_deadline_is_monotonic(self):
        wall, mono = Clock(), Clock(100.0)
        off = ow.Offload(self.state, "w1-test", now=wall, mono=mono, deadline_epoch=wall.t + 60)
        wall.t -= 3600  # the wall clock steps back an hour: no extra budget
        mono.t += 61
        with self.assertRaises(ow.DeadlineStop):
            off.check_deadline(0, "x")

    def test_alarm_backstop_interrupts_blocking_io(self):
        start = time.monotonic()
        with self.assertRaises(ow.DeadlineStop):
            with ow.alarm_guard(0.2):
                time.sleep(5)
        self.assertLess(time.monotonic() - start, 2)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL), (0.0, 0.0))
        with self.assertRaises(ow.Interrupted):
            with ow.alarm_guard(30):
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(1)

    def test_process_group_kill_reaps_grandchildren(self):
        pidfile = self.tmp / "pid"
        with self.assertRaises(subprocess.TimeoutExpired):
            ow.run_process_group(["/bin/sh", "-c", f"sleep 30 & echo $! > {pidfile}; wait"], timeout=0.5)
        pid = int(pidfile.read_text())
        for _ in range(50):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            self.fail("grandchild survived the deadline")

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
    """Delete only after a FRESH verified Air receipt AND a confirmed second copy."""

    def setUp(self):
        super().setUp()
        self.assertEqual(self.run_offload(), 0)

    def test_air_receipt_only_is_not_enough(self):
        with self.assertRaises(ow.Refusal) as caught:
            self.offload().release()
        self.assertEqual(str(caught.exception), "second_copy_not_confirmed")
        self.assert_nothing_deleted()

    def test_cloud_not_uploaded_keeps_queue_and_copy(self):
        cloud = FakeCloud()
        cloud.uploaded = False
        clock = Clock(self.clock.t)

        def tick():
            clock.t += 100
            return clock.t
        self.assertEqual(ow.second_copy_icloud(self.binding, self.icloud, cloud=cloud, probe=self.probe, now=tick,
                                               wait_s=300, internal_min_free_gib=0), [])
        self.assertTrue((self.store / "queue/w1-test.json").exists())
        self.assertIn("cloud_evict_timeout", (self.store / "second/errors.jsonl").read_text())
        with self.assertRaises(ow.Refusal):
            self.offload().release()
        self.assert_nothing_deleted()

    def test_internal_disk_floor_holds_the_icloud_copy(self):
        self.assertEqual(self.confirm_second_copy(internal_min_free_gib=1e9), [])
        self.assertIn("internal_disk_floor", (self.store / "second/errors.jsonl").read_text())
        self.assertFalse(self.icloud.joinpath("w1-test", ow.MANIFEST_NAME).exists())

    def test_forged_second_receipt_refused(self):
        self.confirm_second_copy()
        path = self.store / "second/w1-test" / ow.SECOND_RECEIPT
        doc = json.loads(path.read_text())
        doc["confirmed_epoch_s"] += 1  # body no longer matches its receipt hash
        path.write_text(json.dumps(doc))
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        self.assert_nothing_deleted()

    def test_second_receipt_for_other_bytes_refused(self):
        self.confirm_second_copy()
        path = self.store / "second/w1-test" / ow.SECOND_RECEIPT
        body = ow.check_sealed(json.loads(path.read_text()))
        body["files"][0]["sha256"] = "f" * 64
        path.write_bytes(ow.canonical(ow.sealed(body)))
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        self.assert_nothing_deleted()

    def test_tampered_air_receipt_refused(self):
        self.confirm_second_copy()
        path = self.store / "windows/w1-test/air-receipt.json"
        body = ow.check_sealed(json.loads(path.read_text()))
        body["files_verified"] -= 1
        path.write_bytes(ow.canonical(ow.sealed(body)))
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        self.assert_nothing_deleted()

    def test_part_decayed_on_the_air_after_verify_refuses(self):
        self.confirm_second_copy()
        part = sorted((self.store / "inbox/w1-test").glob("part-*"))[0]
        raw = bytearray(part.read_bytes())
        raw[-1] ^= 1
        part.write_bytes(bytes(raw))
        with self.assertRaises(ow.Mismatch) as caught:
            self.offload().release()
        self.assertIn("air_part_decayed", str(caught.exception))
        self.assert_nothing_deleted()

    def test_replayed_fresh_receipt_refused(self):
        self.confirm_second_copy()
        _, old, _ = self.transport(f"receipts w1-test {'a' * 32}")  # an answer to an earlier nonce
        self.transport.replace_reply = lambda command, reply: old if command.startswith("receipts") else reply
        with self.assertRaises(ow.Mismatch) as caught:
            self.offload().release()
        self.assertIn("fresh_receipt_does_not_match", str(caught.exception))
        self.assert_nothing_deleted()

    def test_record_changed_after_offload_refuses_delete(self):
        self.confirm_second_copy()
        (self.record / "custody/night/chain-stages.jsonl").write_bytes(b"changed after offload\n")
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        self.assert_nothing_deleted()  # checked before any unlink: nothing is half-released
        self.assertFalse((self.state / "w1-test/deleting.json").exists())

    def test_both_receipts_delete_raw_and_parts(self):
        self.confirm_second_copy()
        result = self.offload().release()
        self.assertEqual(result["rule"], "two_verified_copies")
        for rel in self.files:
            self.assertFalse((self.record / rel).exists())

    def test_disk_pressure_never_deletes(self):
        # Lead ruling 2026-11-08: the pressure-release route is gone; under pressure the policy is HOLD.
        self.assertEqual(self.run_offload(min_free_gib=1e9), 0)
        span = self.span()
        self.assertTrue(span["disk_pressure"])
        self.assertEqual(span["release_held"], "second_copy_not_confirmed")
        self.assert_nothing_deleted()
        with self.assertRaises(TypeError):
            self.offload().release(pressure_compressed_local=True)
        with self.assertRaises(SystemExit), open(os.devnull, "w") as sink, _redirect(sink), \
                contextlib_redirect_stderr(sink):
            ow.main(["run", "--state-root", str(self.state), "--window-id", "w1-test", "--record-root",
                     str(self.record), "--record-manifest", str(self.manifest), "--record-manifest-sha256",
                     self.manifest_sha, "--terminal", TERMINAL, "--pack", "--pressure-compressed-local"])
        self.assertFalse(any(p.name == "raw-released.json" for p in (self.state / "w1-test").iterdir()))
        parts = list((self.state / "w1-test/parts").glob("part-*.tar.zst"))
        self.assertTrue(parts)
        self.assert_nothing_deleted()


class DeletionJournal(Fixture):
    """Agreement item 7: `deleting` then `deleted`, the inventory outside the record; resume re-checks."""

    def setUp(self):
        super().setUp()
        self.assertEqual(self.run_offload(), 0)
        self.confirm_second_copy()

    def interrupted(self, after=3):
        off = self.offload()
        calls = {"n": 0}

        def flaky(*a, **kw):
            if calls["n"] == after:
                raise OSError(5, "simulated power loss")
            calls["n"] += 1
            return os.unlink(*a, **kw)
        off.unlink = flaky
        with self.assertRaises(OSError):
            off.release()
        journal = json.loads((self.state / "w1-test/deleting.json").read_text())
        self.assertEqual(journal["state"], "deleting")
        # `after` objects removed, one more detached into the private quarantine when the crash hit.
        self.assertEqual(sum(1 for rel in self.files if not (self.record / rel).exists()), after + 1)
        held = [p for q in journal["quarantine"].values() if Path(q).is_dir() for p in Path(q).iterdir()]
        self.assertEqual(len(held), 1)

    def test_resume_completes_from_the_journal(self):
        self.interrupted()
        result = self.offload().release()
        self.assertTrue(result["resumed"])
        self.assertEqual(result["files_deleted"], len(self.files))
        for rel in self.files:
            self.assertFalse((self.record / rel).exists())
        self.assertEqual(json.loads((self.state / "w1-test/deleting.json").read_text())["state"], "deleted")

    def test_resume_refuses_a_changed_remaining_file(self):
        self.interrupted()
        survivor = next(self.record / rel for rel in sorted(self.files) if (self.record / rel).exists())
        info = survivor.stat()
        os.utime(survivor, ns=(info.st_atime_ns, info.st_mtime_ns + 1000))
        left = sum(1 for rel in self.files if (self.record / rel).exists())
        with self.assertRaises(ow.Mismatch):
            self.offload().release()
        self.assertEqual(sum(1 for rel in self.files if (self.record / rel).exists()), left)

    def test_new_file_during_deletion_refuses(self):
        self.interrupted()
        (self.record / "custody/night").mkdir(parents=True, exist_ok=True)
        (self.record / "custody/night/late.log").write_bytes(b"appeared after the offload\n")
        with self.assertRaises(ow.Mismatch) as caught:
            self.offload().release()
        self.assertIn("new:custody/night/late.log", str(caught.exception))


class SecondDisk(Fixture):
    """Agreement item 9: the alternative proof of the second copy on a physically independent disk."""

    def setUp(self):
        super().setUp()
        self.vol2 = self.tmp / "air/JW-SECOND"
        self.vol2.mkdir()
        self.binding2 = self.tmp / "air/etc/second-binding.json"
        self.probe.ids[str(self.vol2)] = {**self.probe.default, "volume_uuid": "UUID-SECOND",
                                          "physical_stores": ["disk12s2"]}
        ow.init_store(self.vol2 / "jw-offload-second", self.binding2, role="second", probe=self.probe,
                      mount_point=self.vol2, min_free_gib=0)
        self.assertEqual(self.run_offload(), 0)

    def test_independent_disk_copy_releases(self):
        self.assertEqual(ow.second_copy_disk(self.binding, self.binding2, probe=self.probe, now=self.clock),
                         ["w1-test"])
        body = ow.check_sealed(json.loads((self.store / "second/w1-test" / ow.SECOND_RECEIPT).read_text()))
        self.assertEqual(body["method"], "second_disk_verified_copy")
        copied = self.vol2 / "jw-offload-second/windows/w1-test"
        self.assertEqual(sorted(p.name for p in copied.iterdir()), sorted(r["name"] for r in body["files"]))
        self.assertEqual(self.offload().release()["rule"], "two_verified_copies")

    def test_same_physical_disk_refused(self):
        self.probe.ids[str(self.vol2)]["physical_stores"] = ["disk9s2"]  # another volume, same SSD
        with self.assertRaises(ow.Refusal) as caught:
            ow.second_copy_disk(self.binding, self.binding2, probe=self.probe, now=self.clock)
        self.assertIn("second_disk_not_physically_independent", str(caught.exception))
        with self.assertRaises(ow.Refusal):
            self.offload().release()
        self.assert_nothing_deleted()

    def test_primary_store_cannot_serve_as_second(self):
        with self.assertRaises(ow.Refusal):
            ow.second_copy_disk(self.binding, self.binding, probe=self.probe, now=self.clock)


class LocalTransport(Fixture):
    """The gate CLI as a real subprocess (same stdin/stdout protocol as the ssh forced command)."""

    def test_cli_gate_refuses_an_unbound_volume(self):
        rc, out, _ = ow.local_gate_runner(self.binding)("hello")
        self.assertEqual(rc, 2)  # the real probe: a temp dir is not a mounted volume
        self.assertIn(b"store_not_mounted", out)


class OperatorScripts(unittest.TestCase):
    def test_setup_scripts_parse_and_call_this_cli(self):
        for name in ("offload_setup_air.sh", "offload_setup_mbp.sh"):
            subprocess.run(["/bin/bash", "-n", str(ROOT / "scripts" / name)], check=True)
        text = (ROOT / "scripts/offload_setup_air.sh").read_text()
        self.assertIn("air-gate --binding", text)
        self.assertIn("init-store", text)
        with self.assertRaises(SystemExit) as caught, open(os.devnull, "w") as sink, _redirect(sink):
            ow.main(["air-gate", "--help"])
        self.assertEqual(caught.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
