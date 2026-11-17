"""Span cloud offload (RL-173 A). Synthetic spans only; real openssl; local and fake-rclone backends."""
from __future__ import annotations

import contextlib
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import threading
import time
import unittest
from unittest import mock

from joulewise import span_offload as so
from scripts import span_offload as cli
from tests.git_fixture import init_git_fixture

OPENSSL = shutil.which("openssl")
PLAN = "cq-syn-01-s01-a1"
SPAN = "cq-syn-01-s01-a1-20990101T000000Z"

FAKE_RCLONE = textwrap.dedent('''\
    import hashlib, json, os, shutil, sys, time
    args = sys.argv[1:]
    log = os.environ.get("FAKE_RCLONE_LOG")
    if log:
        with open(log, "a") as handle:
            handle.write(json.dumps(args) + "\\n")
    root = os.environ["FAKE_RCLONE_ROOT"]
    if os.environ.get("FAKE_RCLONE_PIDFILE"):
        with open(os.environ["FAKE_RCLONE_PIDFILE"], "a") as handle:
            handle.write(str(os.getpid()) + "\\n")
    flags_with_value = {"--config", "--retries", "--low-level-retries", "--contimeout", "--timeout", "--stats",
                        "--hash-type"}
    positional, opts, i = [], {}, 0
    while i < len(args):
        if args[i] in flags_with_value:
            opts[args[i]] = args[i + 1]; i += 2
        elif args[i].startswith("-"):
            opts[args[i]] = True; i += 1
        else:
            positional.append(args[i]); i += 1
    def local(path):
        if path.startswith("fake:"):
            return os.path.join(root, path[len("fake:"):].lstrip("/"))
        return path
    def dbx(data):
        blocks = b"".join(hashlib.sha256(data[i:i + 4194304]).digest() for i in range(0, len(data), 4194304))
        return hashlib.sha256(blocks).hexdigest()
    cmd = positional[0]
    if os.environ.get("FAKE_RCLONE_FAIL") == cmd:
        sys.exit(1)
    if os.environ.get("FAKE_RCLONE_SLEEP") and cmd == "copyto":
        time.sleep(float(os.environ["FAKE_RCLONE_SLEEP"]))
    if cmd == "copyto":
        src, dst = local(positional[1]), local(positional[2])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst) and "--immutable" in opts:
            if open(dst, "rb").read() != open(src, "rb").read():
                sys.exit(7)
        else:
            shutil.copyfile(src, dst)
        corrupt = os.environ.get("FAKE_RCLONE_CORRUPT")
        if corrupt and positional[2].endswith(corrupt):
            data = bytearray(open(dst, "rb").read()); data[-1] ^= 1; open(dst, "wb").write(bytes(data))
    elif cmd == "lsjson":
        path = local(positional[1])
        rows = []
        for name in sorted(os.listdir(path)):
            data = open(os.path.join(path, name), "rb").read()
            row = {"Path": name, "Name": name, "Size": len(data), "IsDir": False}
            if "--hash" in opts and not os.environ.get("FAKE_RCLONE_NOHASH"):
                t = opts["--hash-type"]
                row["Hashes"] = {t: dbx(data) if t == "dropbox" else hashlib.new(t, data).hexdigest()}
            rows.append(row)
        print(json.dumps(rows))
    elif cmd == "hashsum":
        data = open(positional[2], "rb").read()
        print(dbx(data) + "  " + os.path.basename(positional[2]))
    else:
        sys.exit(2)
''')


FAKE_BRCTL = textwrap.dedent('''\
    import json, os, pathlib, shutil, sys, time
    args = sys.argv[1:]
    state = pathlib.Path(os.environ["FAKE_BRCTL_STATE"])
    with (state / "calls").open("a") as log:
        log.write(json.dumps(args) + "\\n")
    cmd = args[0]
    if os.environ.get("FAKE_BRCTL_SLEEP") == cmd:
        time.sleep(30)
    if os.environ.get("FAKE_BRCTL_FAIL") == cmd or (cmd == "evict" and
            os.environ.get("FAKE_BRCTL_FAIL_SUFFIX") and args[1].endswith(os.environ["FAKE_BRCTL_FAIL_SUFFIX"])):
        sys.exit(1)
    if cmd == "status":
        assert args == ["status", "com.apple.CloudDocs"]
        counter = state / "counter"
        i = int(counter.read_text()) if counter.exists() else 0
        counter.write_text(str(i + 1))
        statuses = json.loads(os.environ.get("FAKE_BRCTL_STATUSES", '["com.apple.CloudDocs client:idle caught-up"]'))
        print(statuses[min(i, len(statuses) - 1)])
    elif cmd in ("evict", "download"):
        path = pathlib.Path(args[1])
        assert not path.is_symlink()
        remote = state / path.name
        if cmd == "evict":
            if not os.environ.get("FAKE_BRCTL_NO_EVICTION"):
                shutil.copyfile(path, remote)
                path.write_bytes(b"")  # synthetic placeholder, observed ONLY by a test mock
        elif remote.exists():
            shutil.copyfile(remote, path)
            if os.environ.get("FAKE_BRCTL_CORRUPT") == path.suffix:
                data = bytearray(path.read_bytes()); data[-1] ^= 1; path.write_bytes(data)
    else:
        sys.exit(2)
''')


@unittest.skipUnless(OPENSSL, "openssl is not installed")
class SpanOffloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys = tempfile.TemporaryDirectory(prefix="offload-keys-")
        cls.fingerprint = so.keygen(OPENSSL, cls.keys.name, bits=3072)
        cls.public = Path(cls.keys.name) / "span-offload.pub.pem"
        cls.private = Path(cls.keys.name) / "span-offload.key.pem"

    @classmethod
    def tearDownClass(cls):
        cls.keys.cleanup()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="offload-test-"))
        self.addCleanup(self._cleanup)
        # Disk state and mail are synthetic too: runner capacity must never trigger real mail.
        self.enterContext(mock.patch.object(so.shutil, "disk_usage", return_value=(1_000_000_000_000, 0, 900_000_000_000)))
        self.span = self.tmp / "campaign-out" / SPAN
        self.make_span(self.span)
        for name in ("stage", "markers", "cloud", "desk", "work"):
            (self.tmp / name).mkdir()
        self.config = {"schema": so.MBP_CONFIG_SCHEMA, "recipient_public_key": str(self.public),
                       "recipient_sha256": self.fingerprint, "stage_root": str(self.tmp / "stage"),
                       "marker_dir": str(self.tmp / "markers"), "openssl": OPENSSL,
                       "backend": {"kind": "local", "root": str(self.tmp / "cloud")}}
        self.air = {"schema": so.AIR_CONFIG_SCHEMA, "identity": str(self.private),
                    "recipient_sha256": self.fingerprint, "work_root": str(self.tmp / "work"), "openssl": OPENSSL,
                    "backend": {"kind": "local", "root": str(self.tmp / "cloud")}}

    def _cleanup(self):
        for root, dirs, files in os.walk(self.tmp):
            for name in dirs:
                os.chmod(os.path.join(root, name), 0o755)
        shutil.rmtree(self.tmp)

    @staticmethod
    def make_span(span):
        """Synthetic bytes: not JSON, not journals. The tool must never need to parse them."""
        (span / "desk-bundle" / "legs" / "L001").mkdir(parents=True)
        (span / "runtime" / "empty-dir").mkdir(parents=True)
        (span / "runner_receipt.json").write_bytes(b"synthetic receipt bytes {not json")
        (span / "chain-stages.jsonl").write_bytes(b"\x00\x01binary\xff" * 1000)
        (span / "desk-bundle" / "legs" / "L001" / "leg_summary.json").write_bytes(b"synthetic")
        (span / "runtime" / "big.bin").write_bytes(os.urandom(300_000))
        (span / "empty.txt").write_bytes(b"")
        (span / "Zeta upper.txt").write_bytes(b"case and space")

    def offload(self, **kwargs):
        return so.offload(self.config, PLAN, self.span, allow_local=True, **kwargs)

    def span_for(self, plan):
        span = self.tmp / "campaign-out" / f"{plan}-20990101T000000Z"
        if not span.exists():
            self.make_span(span)
        return span

    def marker(self, plan=PLAN, confirmed=False):
        return so.marker_path(self.tmp / "markers", plan, confirmed)

    def pull(self, expect=None, kit="cl-syn-01", config=None):
        if expect is None:
            expect = so.expectations(json.loads(self.marker().read_bytes()))
        return so.pull(config or self.air, PLAN, kit, self.tmp / "desk", expect, allow_local=True)

    # --- offload ------------------------------------------------------------------------------

    def test_source_membership_and_cross_file_races_never_certify(self):
        real = so._add_file
        for change in ("add", "mixed", "restore-mtime", "empty-dir", "replace"):
            with self.subTest(change=change):
                plan = PLAN + "-race-" + change
                span = self.span_for(plan)
                fired = []

                def race(tar, path, arcname):
                    result = real(tar, path, arcname)
                    if not fired:
                        fired.append(True)
                        if change == "add":
                            (span / "late.bin").write_bytes(b"late")
                        elif change == "empty-dir":
                            (span / "late-dir").mkdir()
                        elif change == "replace":
                            data = path.read_bytes()
                            path.unlink()
                            path.write_bytes(data)
                        else:
                            stamp = path.stat()
                            path.write_bytes(b"changed after its read")
                            (span / "runner_receipt.json").write_bytes(b"changed before its read")
                            if change == "restore-mtime":
                                os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
                    return result

                with mock.patch.object(so, "_add_file", race), self.assertRaises(so.OffloadError) as caught:
                    so.offload(self.config, plan, span, allow_local=True)
                self.assertEqual(caught.exception.code, "SPAN_CHANGED")
                self.assertFalse(self.marker(plan).exists())
                self.assertFalse((self.tmp / "cloud" / plan).exists())

    def test_source_change_during_cloud_readback_prevents_marker(self):
        backend = self.fake_brctl()
        real = so.ICloudBackend.put

        def race(instance, *args, **kwargs):
            row = real(instance, *args, **kwargs)
            (self.span / "late.bin").write_bytes(b"late")
            return row

        with mock.patch.object(so.ICloudBackend, "put", race), self.assertRaises(so.OffloadError) as caught:
            so.offload(dict(self.config, backend=backend), PLAN, self.span)
        self.assertEqual(caught.exception.code, "SPAN_CHANGED")
        self.assertEqual(list((self.tmp / "markers").iterdir()), [])

    def test_keygen_creates_a_private_missing_output_directory(self):
        root = self.tmp / "new-private-keys"
        fingerprint = so.keygen(OPENSSL, root, 3072)
        self.assertRegex(fingerprint, r"^[0-9a-f]{64}$")
        self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((root / "span-offload.key.pem").stat().st_mode), 0o600)

    def test_retry_of_failed_placeholder_download_remains_exit_8(self):
        backend = self.fake_brctl(FAKE_BRCTL_FAIL="download")
        conf = self.tmp / "icloud.json"
        conf.write_text(json.dumps(dict(self.config, backend=backend)))
        argv = ["offload", "--config", str(conf), "--plan", PLAN, "--span-dir", str(self.span)]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(argv), 8)
            original = self.marker().read_bytes()
            self.assertEqual(cli.main(argv), 8)
        self.assertEqual(self.marker().read_bytes(), original)
        self.assertFalse(self.marker(confirmed=True).exists())

    def test_pending_transfer_read_is_fail_closed_and_does_not_mutate_cloud(self):
        backend = self.fake_brctl()
        config = dict(self.config, backend=backend)
        result = so.pending_transfers(config)
        self.assertTrue(result["clear"])
        for status in ("", "unknown", "com.apple.CloudDocs client:idle caught-up needs-upload",
                       "com.apple.CloudDocs client:idle caught-up downloading"):
            with mock.patch.dict(os.environ, {"FAKE_BRCTL_STATUSES": json.dumps([status])}):
                self.assertFalse(so.pending_transfers(config)["clear"])
        calls = [json.loads(line) for line in (self.tmp / "brctl-state" / "calls").read_text().splitlines()]
        self.assertTrue(all(call == ["status", "com.apple.CloudDocs"] for call in calls))
        with mock.patch.dict(os.environ, {"FAKE_BRCTL_FAIL": "status"}), self.assertRaises(so.OffloadError):
            so.pending_transfers(config)

    def test_pack_readback_checks_per_file_manifest_before_any_deletion(self):
        real = so.encrypt_span

        def wrong_manifest(*args, **kwargs):
            manifest, digest, size, count = real(*args, **kwargs)
            return b"0" * 64 + manifest[64:], digest, size, count

        with mock.patch.object(so, "encrypt_span", wrong_manifest), self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "PACK_MANIFEST_MISMATCH")
        self.assertTrue(self.span.exists())
        self.assertEqual(list((self.tmp / "cloud").iterdir()), [])

    def test_close_cloud_only_deletes_raw_but_keeps_materialised_pack(self):
        backend = self.fake_brctl()
        config = dict(self.config, backend=backend, lead_email="lead@example.test")
        before = so.hash_tree(self.span)
        result = so.close_offload(config, PLAN, self.span)
        self.assertTrue(result["original_deleted"])
        self.assertFalse(result["archive_evicted"])
        self.assertFalse(self.span.exists())
        archive = self.tmp / "stage" / PLAN / (PLAN + ".tgz.enc")
        self.assertGreater(archive.stat().st_size, 0)
        self.assertEqual(so.sha256_file(archive), result["ciphertext"]["sha256"])
        self.pull(so.expectations(result), config=dict(self.air, backend=backend))
        self.assertEqual(so.hash_tree(self.tmp / "desk" / "cl-syn-01" / SPAN), before)
        # Retrying a completed close rechecks its cloud hashes and returns 0, including with no OUT.
        self.assertTrue(so.close_offload(config, PLAN, self.span)["original_deleted"])

    def test_close_unconfirmed_never_deletes_and_ssd_mismatch_never_evicts(self):
        backend = self.fake_brctl(FAKE_BRCTL_NO_EVICTION="1")
        config = dict(self.config, backend=backend, lead_email="lead@example.test")
        with self.assertRaises(so.OffloadError):
            so.close_offload(config, PLAN, self.span)
        self.assertTrue(self.span.exists())
        os.environ.pop("FAKE_BRCTL_NO_EVICTION")
        record = so.offload(config, PLAN, self.span)
        receipt = self.tmp / "ssd.json"
        receipt.write_bytes(so.canonical({"schema": so.SSD_SCHEMA, "plan": PLAN, "files": {}}))
        with self.assertRaises(so.OffloadError):
            so.close_offload(config, PLAN, self.span, ssd_receipt=receipt)
        self.assertTrue((self.tmp / "stage" / PLAN / (PLAN + ".tgz.enc")).exists())
        self.assertTrue(record["provider_confirmed"])

    def test_close_evicts_only_after_ssd_copy_readback_matches_receipt(self):
        backend = self.fake_brctl()
        config = dict(self.config, backend=backend, lead_email="lead@example.test")
        record = so.offload(config, PLAN, self.span)
        ssd = self.tmp / "ssd"
        ssd.mkdir()
        with mock.patch.object(so, "require_ssd_mount"):
            receipt = so.ssd_copy(dict(self.air, backend=backend), PLAN, record, ssd)
        self.assertEqual(so.sha256_file(Path(receipt).parent / (PLAN + ".tgz.enc")), record["ciphertext"]["sha256"])
        result = so.close_offload(config, PLAN, self.span, ssd_receipt=receipt)
        self.assertTrue(result["archive_evicted"])
        self.assertFalse(self.span.exists())
        self.assertFalse((self.tmp / "stage" / PLAN / (PLAN + ".tgz.enc")).exists())
        self.assertEqual((self.tmp / "cloud" / PLAN / (PLAN + ".tgz.enc")).stat().st_size, 0)

    def test_low_space_mails_at_sixty_decimal_gb_and_never_forces_eviction(self):
        for free, expected in ((60_000_000_001, False), (60_000_000_000, True), (39_000_000_000, True)):
            with self.subTest(free=free), mock.patch.object(so.shutil, "disk_usage", return_value=(100, 0, free)), \
                    mock.patch.object(so.subprocess, "run") as mail:
                mail.return_value.returncode = 0
                self.assertEqual(so.storage_alarm(self.config | {"lead_email": "lead@example.test"}, PLAN), expected)
                self.assertEqual(mail.called, expected)
                if expected:
                    self.assertEqual(mail.call_args.args[0][-1], "lead@example.test")

    def test_typed_marker_retry_rechecks_cloud_hashes_and_never_rewrites_marker(self):
        backend = self.fake_brctl()
        config = dict(self.config, backend=backend)
        original = so.offload(config, PLAN, self.span)
        marker = self.marker(confirmed=True).read_bytes()
        self.assertEqual(so.offload(config, PLAN, self.span), original)
        path = self.tmp / "brctl-state" / (PLAN + ".key.enc")
        path.write_bytes(b"bad")
        with self.assertRaises(so.OffloadError):
            so.offload(config, PLAN, self.span)
        self.assertEqual(self.marker(confirmed=True).read_bytes(), marker)

    def test_typed_marker_retry_rechecks_source_after_final_pending_wait(self):
        backend = self.fake_brctl()
        config = dict(self.config, backend=backend)
        so.offload(config, PLAN, self.span)
        original = self.marker(confirmed=True).read_bytes()
        real = so.ICloudBackend._wait_uploaded

        def changed(instance, deadline):
            result = real(instance, deadline)
            (self.span / "late.bin").write_bytes(b"late in final pending wait")
            return result

        with mock.patch.object(so.ICloudBackend, "_wait_uploaded", changed), self.assertRaises(so.OffloadError) as caught:
            so.offload(config, PLAN, self.span)
        self.assertEqual(caught.exception.code, "SPAN_CHANGED")
        self.assertEqual(self.marker(confirmed=True).read_bytes(), original)

    def test_pending_cli_holds_on_unknown_or_pending_state(self):
        backend = self.fake_brctl()
        conf = self.tmp / "mbp.json"
        conf.write_text(json.dumps(dict(self.config, backend=backend)))
        argv = ["pending", "--config", str(conf)]
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(argv), 0)
            with mock.patch.dict(os.environ, {"FAKE_BRCTL_STATUSES": '["unknown"]'}):
                self.assertEqual(cli.main(argv), 5)
        self.assertIn("ICLOUD_CLEAR", out.getvalue())

    def test_close_refuses_missing_or_corrupt_local_pack_before_raw_deletion(self):
        backend = self.fake_brctl()
        config = dict(self.config, backend=backend)
        so.offload(config, PLAN, self.span)
        archive = self.tmp / "stage" / PLAN / (PLAN + ".tgz.enc")
        data = archive.read_bytes()
        archive.chmod(0o600)
        archive.write_bytes(b"bad")
        with self.assertRaises(so.OffloadError):
            so.close_offload(config, PLAN, self.span)
        self.assertTrue(self.span.exists())
        archive.write_bytes(data)
        shutil.rmtree(self.span)
        archive.unlink()
        with self.assertRaises(so.OffloadError):
            so.close_offload(config, PLAN, self.span)

    def test_ssd_copy_refuses_system_disk_and_wrong_cloud_bytes(self):
        backend = self.fake_brctl()
        record = so.offload(dict(self.config, backend=backend), PLAN, self.span)
        ssd = self.tmp / "ssd"
        ssd.mkdir()
        with self.assertRaises(so.OffloadError) as caught:
            so.ssd_copy(dict(self.air, backend=backend), PLAN, record, ssd)
        self.assertEqual(caught.exception.code, "SSD_MOUNT")
        (self.tmp / "brctl-state" / (PLAN + ".tgz.enc")).write_bytes(b"bad")
        with mock.patch.object(so, "require_ssd_mount"), self.assertRaises(so.OffloadError):
            so.ssd_copy(dict(self.air, backend=backend), PLAN, record, ssd)
        self.assertFalse((ssd / "span-archives" / PLAN).exists())

    def test_existing_ssd_copy_requires_a_complete_valid_receipt(self):
        backend = self.fake_brctl()
        record = so.offload(dict(self.config, backend=backend), PLAN, self.span)
        ssd = self.tmp / "ssd"
        ssd.mkdir()
        with mock.patch.object(so, "require_ssd_mount"):
            path = Path(so.ssd_copy(dict(self.air, backend=backend), PLAN, record, ssd))
            original = so.read_record(path)
            for key, bad in (("schema", "wrong"), ("plan", "other"), ("descriptor_sha256", "0" * 64),
                             ("verified_epoch_s", None)):
                with self.subTest(key=key):
                    path.write_bytes(so.canonical(dict(original, **{key: bad})))
                    with self.assertRaises(so.OffloadError) as caught:
                        so.ssd_copy(dict(self.air, backend=backend), PLAN, record, ssd)
                    self.assertEqual(caught.exception.code, "SSD_RECEIPT_INVALID")
            path.write_bytes(so.canonical(original))
            self.assertEqual(so.ssd_copy(dict(self.air, backend=backend), PLAN, record, ssd), str(path))

    def test_incomplete_readback_evidence_cannot_publish_ok(self):
        backend = self.fake_brctl()
        real = so.ICloudBackend.put

        def missing_observation(instance, *args, **kwargs):
            row = real(instance, *args, **kwargs)
            row.pop("evicted_epoch_s")
            return row

        with mock.patch.object(so.ICloudBackend, "put", missing_observation), self.assertRaises(so.OffloadError):
            so.offload(dict(self.config, backend=backend), PLAN, self.span)
        self.assertFalse(self.marker(confirmed=True).exists())

    def test_round_trip_marker_and_read_only_pull(self):
        before = so.hash_tree(self.span)
        record = self.offload(require_files=["runner_receipt.json"])
        marker = self.marker()
        self.assertEqual(json.loads(marker.read_bytes()), record)
        # The local backend cannot see a provider: never the copy gate's <plan>.ok (A.7).
        self.assertEqual(os.listdir(self.tmp / "markers"), [f"{PLAN}.ok.unconfirmed"])
        self.assertEqual(record["schema"], so.MARKER_SCHEMA)
        self.assertEqual(record["manifest_sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(record["manifest_files"], 6)
        cloud = self.tmp / "cloud" / PLAN
        self.assertEqual(record["ciphertext"]["sha256"], so.sha256_file(cloud / f"{PLAN}.tgz.enc"))
        self.assertEqual(record["ciphertext"]["size"], (cloud / f"{PLAN}.tgz.enc").stat().st_size)
        self.assertEqual([c["name"] for c in record["provider_confirmation"]],
                         [f"{PLAN}{s}" for s in (".tgz.enc", ".key.enc", ".SHA256SUMS", ".offload.json")])
        self.assertFalse(record["provider_confirmed"])  # the local backend cannot see a provider
        self.assertEqual(so.hash_tree(self.span), before)  # originals untouched (A.5)
        # The manifest is shasum-compatible.
        sums = (cloud / f"{PLAN}.SHA256SUMS").read_bytes()
        self.assertEqual(sums, before)
        self.assertIn(b"  ./runtime/big.bin\n", sums)
        # No plaintext of the span appears in the cloud folder.
        blob = (cloud / f"{PLAN}.tgz.enc").read_bytes()
        self.assertNotIn(b"synthetic receipt bytes", blob)
        self.assertTrue(blob.startswith(b"Salted__"))
        result = self.pull()
        dest = self.tmp / "desk" / "cl-syn-01" / SPAN
        self.assertEqual(result["dest"], str(dest))
        self.assertEqual(so.hash_tree(dest), before)
        self.assertTrue((dest / "runtime" / "empty-dir").is_dir())
        for root, dirs, files in os.walk(dest):
            self.assertEqual(stat.S_IMODE(os.stat(root).st_mode), 0o555)
            for name in files:
                self.assertEqual(stat.S_IMODE(os.stat(os.path.join(root, name)).st_mode), 0o444)
        kit_dir = self.tmp / "desk" / "cl-syn-01"
        self.assertEqual((kit_dir / f"{SPAN}.mbp.SHA256SUMS").read_bytes(), before)
        self.assertEqual((kit_dir / f"{SPAN}.air.SHA256SUMS").read_bytes(), before)
        self.assertEqual(sorted(os.listdir(self.tmp / "work")), [])  # no plaintext archive left behind

    def test_bytes_only_contents_do_not_matter(self):
        """A.4: changing a file's bytes changes only that file's hash line; nothing is parsed."""
        self.offload()
        first = (self.tmp / "cloud" / PLAN / f"{PLAN}.SHA256SUMS").read_bytes().splitlines()
        other = self.tmp / "other" / SPAN
        self.make_span(other)
        (other / "runner_receipt.json").write_bytes(b"\xff\xfe totally different")
        lines = so.hash_tree(other).splitlines()
        changed = [i for i, (a, b) in enumerate(zip(first, lines)) if a != b]
        names = [first[i].split(b"  ", 1)[1] for i in changed]
        self.assertIn(b"./runner_receipt.json", names)
        self.assertNotIn(b"./chain-stages.jsonl", names)

    def test_marker_exists_does_nothing(self):
        marker = self.tmp / "markers" / f"{PLAN}.ok"
        marker.write_text("written by the Air\n")
        with self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual((caught.exception.code, caught.exception.exit_kind), ("MARKER_EXISTS", "marker_exists"))
        self.assertEqual(os.listdir(self.tmp / "stage"), [])
        self.assertEqual(os.listdir(self.tmp / "cloud"), [])
        self.assertEqual(marker.read_text(), "written by the Air\n")

    def test_marker_race_keeps_the_first_writer(self):
        marker = self.marker()
        real = so.write_marker

        def racing(path, record):
            Path(path).write_text("first\n")
            return real(path, record)

        with mock.patch.object(so, "write_marker", racing), self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "MARKER_EXISTS")
        self.assertEqual(marker.read_text(), "first\n")
        self.assertEqual(os.listdir(self.tmp / "markers"), [marker.name])

    def test_refuses_symlink_special_and_bad_names(self):
        cases = {
            "SPAN_SYMLINK": lambda s: os.symlink("/etc/hosts", s / "link"),
            "BAD_NAME": lambda s: (s / "new\nline").write_bytes(b"x"),
            "SPAN_SPECIAL_FILE": lambda s: os.mkfifo(s / "fifo"),
        }
        for code, plant in cases.items():
            with self.subTest(code=code):
                span = self.tmp / code / SPAN
                self.make_span(span)
                plant(span)
                with self.assertRaises(so.OffloadError) as caught:
                    so.offload(self.config, PLAN, span, allow_local=True)
                self.assertEqual((caught.exception.code, caught.exception.exit_kind), (code, "refused"))
                self.assertEqual(os.listdir(self.tmp / "markers"), [])
                self.assertEqual(os.listdir(self.tmp / "cloud"), [])

    def test_refuses_unclosed_span_and_symlinked_span_dir(self):
        with self.assertRaises(so.OffloadError) as caught:
            self.offload(require_files=["no_receipt_here.json"])
        self.assertEqual(caught.exception.code, "SPAN_NOT_CLOSED")
        (self.tmp / "links").mkdir()
        link = self.tmp / "links" / SPAN
        os.symlink(self.span, link)
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(self.config, PLAN, link, allow_local=True)
        self.assertEqual(caught.exception.code, "SPAN_NOT_DIR")

    def test_recipient_pin_and_local_backend_gate(self):
        bad = dict(self.config, recipient_sha256="0" * 64)
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(bad, PLAN, self.span, allow_local=True)
        self.assertEqual(caught.exception.code, "RECIPIENT_MISMATCH")
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(self.config, PLAN, self.span)
        self.assertEqual(caught.exception.code, "LOCAL_BACKEND_NOT_ALLOWED")
        self.assertEqual([n for n in os.listdir(self.tmp / "stage") if not n.startswith(".")], [])

    def test_mbp_config_cannot_hold_the_private_key(self):
        path = self.tmp / "mbp.json"
        path.write_text(json.dumps(dict(self.config, identity=str(self.private))))
        with self.assertRaises(so.OffloadError) as caught:
            so.load_mbp_config(path)
        self.assertEqual(caught.exception.code, "CONFIG")
        self.assertIn("identity", caught.exception.detail)
        path.write_text(json.dumps(dict(self.config, stage_root="relative/stage")))
        with self.assertRaises(so.OffloadError):
            so.load_mbp_config(path)

    def test_span_changing_while_archived_refuses(self):
        real = so._HashingReader.read

        grown = []

        def growing(reader, size=-1):
            data = real(reader, size)
            if data and not grown and os.fstat(reader.handle.fileno()).st_size == 300_000:
                grown.append(True)
                with open(self.span / "runtime" / "big.bin", "ab") as handle:
                    handle.write(b"late")
            return data

        with mock.patch.object(so._HashingReader, "read", growing), self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "SPAN_CHANGED")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])
        self.assertEqual(os.listdir(self.tmp / "cloud"), [])

    def test_retry_reuses_a_complete_stage_and_never_moves_a_foreign_one(self):
        with mock.patch.object(so.LocalBackend, "put", side_effect=so.unverified("UPLOAD_TIMEOUT", "x")):
            with self.assertRaises(so.OffloadError) as caught:
                self.offload()
        self.assertEqual(caught.exception.exit_kind, "unverified")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])
        staged = so.sha256_file(self.tmp / "stage" / PLAN / f"{PLAN}.tgz.enc")
        record = self.offload()
        self.assertTrue(record["stage_reused"])
        self.assertEqual(record["ciphertext"]["sha256"], staged)
        # A directory the tool did not complete (item 347's stage, say) is never moved or reused.
        other = PLAN.replace("s01", "s02")
        (self.tmp / "stage" / other).mkdir()
        (self.tmp / "stage" / other / f"{other}.tgz.enc").write_bytes(b"half")
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(self.config, other, self.span_for(other), allow_local=True)
        self.assertEqual(caught.exception.code, "STAGE_CONFLICT")
        self.assertEqual((self.tmp / "stage" / other / f"{other}.tgz.enc").read_bytes(), b"half")
        # A failed build leaves nothing behind.
        third = PLAN.replace("s01", "s03")
        with mock.patch.object(so, "wrap_passphrase", side_effect=so.refused("OPENSSL_FAILED", "x")):
            with self.assertRaises(so.OffloadError):
                so.offload(self.config, third, self.span_for(third), allow_local=True)
        self.assertEqual([n for n in os.listdir(self.tmp / "stage") if third in n and not n.endswith(".lock")], [])

    def test_deadline(self):
        with self.assertRaises(so.OffloadError) as caught:
            self.offload(deadline_epoch=1.0)
        self.assertEqual((caught.exception.code, caught.exception.exit_kind), ("DEADLINE", "unverified"))
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    # --- pull ---------------------------------------------------------------------------------

    def test_pull_refuses_tampering(self):
        self.offload()
        cloud = self.tmp / "cloud" / PLAN
        pristine = {p.name: p.read_bytes() for p in cloud.iterdir()}
        for name in pristine:
            with self.subTest(name=name):
                data = bytearray(pristine[name]); data[len(data) // 2] ^= 0x40
                (cloud / name).write_bytes(bytes(data))
                with self.assertRaises(so.OffloadError) as caught:
                    self.pull()
                self.assertEqual(caught.exception.exit_kind, "integrity")
                self.assertFalse((self.tmp / "desk" / "cl-syn-01" / SPAN).exists())
                (cloud / name).write_bytes(pristine[name])
        # Only the two A.2 hashes, given by hand: tampering the descriptor's archive hash is still caught
        # because the decrypted bytes must match the anchored manifest.
        record = json.loads(self.marker().read_bytes())
        expect = so.expectations(None, record["manifest_sha256"], record["ciphertext"]["sha256"])
        self.pull(expect)
        self.assertTrue((self.tmp / "desk" / "cl-syn-01" / SPAN).is_dir())
        with self.assertRaises(so.OffloadError) as caught:
            self.pull(expect)
        self.assertEqual(caught.exception.exit_kind, "dest_exists")

    def test_pull_with_wrong_identity_fails_closed(self):
        self.offload()
        other = Path(tempfile.mkdtemp(prefix="offload-other-key-"))
        self.addCleanup(shutil.rmtree, other)
        so.keygen(OPENSSL, other, bits=3072)
        air = dict(self.air, identity=str(other / "span-offload.key.pem"))
        with self.assertRaises(so.OffloadError) as caught:
            self.pull(config=air)
        self.assertEqual(caught.exception.exit_kind, "integrity")
        self.assertFalse((self.tmp / "desk" / "cl-syn-01").exists())

    def test_pull_refuses_an_archive_escaping_its_top(self):
        """A hostile archive encrypted to the right key, with a matching (hostile) manifest and descriptor."""
        cloud = self.tmp / "cloud" / PLAN
        cloud.mkdir()
        raw = io.BytesIO()
        with gzip.GzipFile(fileobj=raw, mode="wb") as gz, tarfile.open(fileobj=gz, mode="w|") as tar:
            for name in (SPAN, f"{SPAN}/../escape.txt"):
                info = tarfile.TarInfo(name)
                if name == SPAN:
                    info.type = tarfile.DIRTYPE
                    tar.addfile(info)
                else:
                    info.size = 3
                    tar.addfile(info, io.BytesIO(b"bad"))
        archive = raw.getvalue()
        passphrase = b"ab" * 32
        plain = self.tmp / "hostile.tgz"
        plain.write_bytes(archive)
        names = so.names(PLAN)
        read_end, write_end = os.pipe()
        os.write(write_end, passphrase + b"\n"); os.close(write_end)
        subprocess.run([OPENSSL, *so._enc_args(False, read_end), "-in", str(plain), "-out",
                        str(cloud / names["ciphertext"])], check=True, pass_fds=(read_end,))
        os.close(read_end)
        so.wrap_passphrase(OPENSSL, self.public, passphrase, cloud / names["wrapped_key"])
        (cloud / names["manifest"]).write_bytes(b"")
        descriptor = {"schema": so.DESCRIPTOR_SCHEMA, "plan": PLAN, "span_name": SPAN,
                      "scheme": {"recipient_sha256": self.fingerprint},
                      "archive": {"sha256": hashlib.sha256(archive).hexdigest(), "size": len(archive)},
                      "files": {k: {"name": names[k], "sha256": so.sha256_file(cloud / names[k]),
                                    "size": (cloud / names[k]).stat().st_size}
                                for k in ("ciphertext", "wrapped_key", "manifest")}}
        (cloud / names["descriptor"]).write_bytes(so.canonical(descriptor))
        expect = so.expectations(None, so.sha256_file(cloud / names["manifest"]),
                                 so.sha256_file(cloud / names["ciphertext"]))
        with self.assertRaises(so.OffloadError) as caught:
            self.pull(expect)
        self.assertEqual(caught.exception.code, "ARCHIVE_PATH")
        self.assertFalse((self.tmp / "escape.txt").exists())
        self.assertFalse((self.tmp / "desk" / "escape.txt").exists())

    def test_expectations_need_the_two_a2_hashes(self):
        with self.assertRaises(so.OffloadError):
            so.expectations(None, "a" * 64, None)
        with self.assertRaises(so.OffloadError):
            so.expectations({"schema": so.MARKER_SCHEMA, "manifest_sha256": "a" * 64,
                             "ciphertext": {"sha256": "b" * 64}}, "c" * 64, None)

    # --- rclone backend (fake binary) ---------------------------------------------------------

    def fake_brctl(self, observe=True, **env):
        """Fake executable on PATH; no real CloudDocs or file flags are touched, on any platform."""
        bindir = self.tmp / "bin"
        bindir.mkdir(exist_ok=True)
        script = bindir / "brctl"
        script.write_text(f"#!{sys.executable}\n" + FAKE_BRCTL)
        script.chmod(0o755)
        state = self.tmp / "brctl-state"
        state.mkdir(exist_ok=True)
        values = {"PATH": str(bindir) + os.pathsep + os.environ.get("PATH", ""), "FAKE_BRCTL_STATE": str(state)}
        values.update(env)
        patcher = mock.patch.dict(os.environ, values)
        patcher.start(); self.addCleanup(patcher.stop)
        if observe:
            # The fake evicts by truncating a NONEMPTY synthetic artifact and downloads by restoring it.
            # This is explicitly not hardware evidence: production observes Apple's SF_DATALESS instead.
            flags = mock.patch.object(so, "_is_dataless", side_effect=lambda info: info.st_size == 0)
            flags.start(); self.addCleanup(flags.stop)
        return {"kind": "icloud", "root": str(self.tmp / "cloud"), "timeout_s": 10,
                "poll_interval_s": 0.01, "evict_timeout_s": 0.3, "download_timeout_s": 1}

    def test_icloud_default_and_observed_provider_round_trip(self):
        backend = self.fake_brctl(FAKE_BRCTL_STATUSES=json.dumps([
            "com.apple.CloudDocs client:needs-sync-up needs-upload", "com.apple.CloudDocs client:idle caught-up"]))
        before = so.hash_tree(self.span)
        config = dict(self.config, backend=backend)
        record = so.offload(config, PLAN, self.span)
        self.assertEqual(json.loads(self.marker(confirmed=True).read_bytes()), record)
        self.assertTrue(record["provider_confirmed"])
        self.assertFalse(self.marker().exists())
        self.assertEqual(record["ciphertext"]["sha256"], so.sha256_file(self.tmp / "brctl-state" / f"{PLAN}.tgz.enc"))
        self.assertEqual(record["manifest_sha256"], hashlib.sha256(before).hexdigest())
        for row in record["provider_confirmation"]:
            self.assertEqual(row["kind"], "icloud evict+redownload sha256 match")
            self.assertEqual((row["provider_hash"], row["provider_size"]), (row["sha256"], row["size"]))
            self.assertLessEqual(row["uploaded_epoch_s"], row["evicted_epoch_s"])
            self.assertLessEqual(row["evicted_epoch_s"], row["verified_epoch_s"])
        air = dict(self.air, backend=backend)
        self.pull(so.expectations(record), config=air)
        self.assertEqual(so.hash_tree(self.tmp / "desk" / "cl-syn-01" / SPAN), before)
        self.assertEqual(so.hash_tree(self.span), before)
        calls = [json.loads(line) for line in (self.tmp / "brctl-state" / "calls").read_text().splitlines()]
        self.assertEqual(sum(c[0] == "evict" for c in calls), 4)
        self.assertEqual(sum(c[0] == "download" for c in calls), 8)  # readback + later Air pull
        self.assertEqual(calls[:2], [["status", "com.apple.CloudDocs"]] * 2)
        self.assertIsInstance(so.make_backend({"root": str(self.tmp / "cloud")}), so.ICloudBackend)
        self.assertEqual(so.make_backend({}).root, Path(so.ICLOUD_ROOT).expanduser())

    def test_icloud_status_parser_requires_positive_evidence_and_no_pending_items(self):
        good = b"<com.apple.CloudDocs[1] client:idle caught-up last-sync 2026-11-15 13:13:40>"
        self.assertTrue(so.ICloudBackend._uploaded(good))
        for text in (b"", b"unknown format", b"client:idle caught-up", b"com.apple.CloudDocs client:idle",
                     good + b"\nneeds-upload file", good + b"\nuploading", good + b"\nerror: failed",
                     b"com.apple.CloudDocs client:idle not-caught-up", good + b"\nneeds-sync-up",
                     good + b"\npending transfers: 1", good + b"\ntransfer-pending"):
            with self.subTest(text=text):
                self.assertFalse(so.ICloudBackend._uploaded(text))

    def test_icloud_status_failure_timeout_and_hash_mismatch_write_no_marker(self):
        cases = [({"FAKE_BRCTL_FAIL": "status"}, {}, "BRCTL_FAILED"),
                 ({"FAKE_BRCTL_SLEEP": "status"}, {"timeout_s": 0.2}, "BRCTL_TIMEOUT"),
                 ({"FAKE_BRCTL_STATUSES": '["com.apple.CloudDocs client:idle caught-up needs-upload"]'},
                  {"timeout_s": 0.2}, "DEADLINE"),
                 ({"FAKE_BRCTL_STATUSES": '["unrecognized"]'}, {"timeout_s": 0.2}, "DEADLINE"),
                 ({"FAKE_BRCTL_CORRUPT": ".enc"}, {}, "READBACK_HASH")]
        for i, (env, overrides, code) in enumerate(cases):
            with self.subTest(code=code):
                backend = dict(self.fake_brctl(**env), **overrides)
                plan = f"{PLAN}-bad{i}"
                with self.assertRaises(so.OffloadError) as caught:
                    so.offload(dict(self.config, backend=backend), plan, self.span_for(plan))
                # A status process can start just before the same absolute deadline expires.
                self.assertIn(caught.exception.code, ("DEADLINE", "BRCTL_TIMEOUT") if code == "DEADLINE" else (code,))
                self.assertEqual(caught.exception.exit_kind, "unverified")
                self.assertEqual(os.listdir(self.tmp / "markers"), [])
                for key in env:
                    os.environ.pop(key)
        self.assertEqual(so._CHILDREN, set())

    def test_icloud_failed_or_unobserved_eviction_and_failed_download_are_unconfirmed(self):
        for i, env in enumerate(({"FAKE_BRCTL_FAIL": "evict"}, {"FAKE_BRCTL_FAIL": "download"},
                                 {"FAKE_BRCTL_NO_EVICTION": "1"}, {"FAKE_BRCTL_SLEEP": "evict"})):
            with self.subTest(env=env):
                backend = self.fake_brctl(**env)
                plan = f"{PLAN}-unconfirmed{i}"
                record = so.offload(dict(self.config, backend=backend), plan, self.span_for(plan))
                self.assertFalse(record["provider_confirmed"])
                self.assertTrue(self.marker(plan).exists())
                self.assertFalse(self.marker(plan, True).exists())
                self.assertTrue(all(r["kind"] == "icloud-unconfirmed" for r in record["provider_confirmation"]))
                self.assertTrue(all(r["provider_hash"] is None for r in record["provider_confirmation"]))
                for key in env:
                    os.environ.pop(key)
        self.assertEqual(so._CHILDREN, set())

    def test_icloud_cli_returns_8_without_observed_eviction_and_5_on_upload_timeout(self):
        backend = self.fake_brctl(FAKE_BRCTL_NO_EVICTION="1")
        conf = self.tmp / "icloud.json"
        conf.write_text(json.dumps(dict(self.config, backend=backend)))
        argv = ["offload", "--config", str(conf), "--plan", PLAN, "--span-dir", str(self.span)]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(cli.main(argv), 8)
        self.assertIn("OFFLOAD_OK_UNCONFIRMED", out.getvalue())
        self.assertFalse(self.marker(confirmed=True).exists())
        os.environ.pop("FAKE_BRCTL_NO_EVICTION")
        # The same immutable stage can be verified later, upgrading to .ok without overwriting it.
        record = so.offload(dict(self.config, backend=backend), PLAN, self.span)
        self.assertTrue(record["provider_confirmed"])
        self.assertTrue(record["stage_reused"])
        marker_before = self.marker(confirmed=True).read_bytes()
        self.assertEqual(so.offload(dict(self.config, backend=backend), PLAN, self.span), record)
        self.assertEqual(self.marker(confirmed=True).read_bytes(), marker_before)
        plan = PLAN + "-timeout"
        conf.write_text(json.dumps(dict(self.config, backend=dict(backend, timeout_s=0.2))))
        with mock.patch.dict(os.environ, {"FAKE_BRCTL_STATUSES": '["com.apple.CloudDocs needs-upload"]'}), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            self.assertEqual(cli.main(["offload", "--config", str(conf), "--plan", plan,
                                       "--span-dir", str(self.span_for(plan))]), 5)
        self.assertIn("OFFLOAD_UNVERIFIED", err.getvalue())
        self.assertFalse(self.marker(plan).exists())
        self.assertFalse(self.marker(plan, True).exists())

    def test_icloud_one_unconfirmed_artifact_prevents_the_copy_gate_and_can_retry(self):
        backend = self.fake_brctl(FAKE_BRCTL_FAIL_SUFFIX=".offload.json")
        record = so.offload(dict(self.config, backend=backend), PLAN, self.span)
        self.assertEqual([r["provider_confirmed"] for r in record["provider_confirmation"]], [True, True, True, False])
        self.assertFalse(record["provider_confirmed"])
        self.assertFalse(self.marker(confirmed=True).exists())
        os.environ.pop("FAKE_BRCTL_FAIL_SUFFIX")
        record = so.offload(dict(self.config, backend=backend), PLAN, self.span)
        self.assertTrue(record["provider_confirmed"])

    def test_icloud_repeated_unconfirmed_cli_exit_is_8_and_preserves_the_record(self):
        backend = self.fake_brctl(FAKE_BRCTL_NO_EVICTION="1")
        conf = self.tmp / "icloud.json"
        conf.write_text(json.dumps(dict(self.config, backend=backend)))
        argv = ["offload", "--config", str(conf), "--plan", PLAN, "--span-dir", str(self.span)]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(cli.main(argv), 8)
            original = self.marker().read_bytes()
            self.assertEqual(cli.main(argv), 8)
        self.assertIn("OFFLOAD_UNCONFIRMED ICLOUD_UNCONFIRMED", err.getvalue())
        self.assertEqual(self.marker().read_bytes(), original)
        self.assertFalse(self.marker(confirmed=True).exists())

    def test_icloud_no_flag_support_cannot_confirm_and_deadline_overrides_fallback(self):
        backend = self.fake_brctl()
        with mock.patch.object(so, "_is_dataless", return_value=None):
            record = so.offload(dict(self.config, backend=backend), PLAN, self.span)
        self.assertFalse(record["provider_confirmed"])
        self.assertFalse(self.marker(confirmed=True).exists())
        plan = PLAN + "-deadline"
        backend = self.fake_brctl(FAKE_BRCTL_SLEEP="evict")
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(dict(self.config, backend=backend), plan, self.span_for(plan), deadline_epoch=time.time() + 0.3)
        self.assertEqual(caught.exception.exit_kind, "unverified")
        self.assertFalse(self.marker(plan).exists())
        self.assertFalse(self.marker(plan, True).exists())

    def test_icloud_never_follows_backend_links_or_hardlinks_or_writes_into_a_repository(self):
        backend = self.fake_brctl()
        path = self.tmp / "cloud" / PLAN
        before = so.hash_tree(self.span)
        path.symlink_to(self.span, target_is_directory=True)
        with self.assertRaises(so.OffloadError):
            so.offload(dict(self.config, backend=backend), PLAN, self.span)
        path.unlink(); path.mkdir()
        target = path / f"{PLAN}.tgz.enc"
        for hard in (False, True):
            (os.link if hard else os.symlink)(self.span / "runner_receipt.json", target)
            with self.subTest(hard=hard), self.assertRaises(so.OffloadError):
                so.offload(dict(self.config, backend=backend), PLAN, self.span)
            target.unlink()
        os.mkfifo(target)
        with self.assertRaises(so.OffloadError):
            so.offload(dict(self.config, backend=backend), PLAN, self.span)
        target.unlink()
        alias = self.tmp / "alias"
        alias.symlink_to(self.tmp / "cloud", target_is_directory=True)
        with self.assertRaises(so.OffloadError):
            so.offload(dict(self.config, backend=dict(backend, root=str(alias))), PLAN, self.span)
        init_git_fixture(path, "-q")
        with self.assertRaises(so.OffloadError):
            so.offload(dict(self.config, backend=backend), PLAN, self.span)
        self.assertEqual(sorted(p.name for p in path.iterdir()), [".git"])
        self.assertEqual(so.hash_tree(self.span), before)
        self.assertFalse((self.tmp / "brctl-state" / "calls").exists())
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    def test_icloud_atomic_copy_conflicts_and_partial_copy_cleanup(self):
        backend = so.make_backend(self.fake_brctl())
        source = self.tmp / "artifact"
        source.write_bytes(b"synthetic artifact")
        name = so.names(PLAN)["ciphertext"]
        real_run = backend._run

        def inspect(args, deadline):
            self.assertEqual((self.tmp / "cloud" / PLAN / name).read_bytes(), source.read_bytes())
            self.assertEqual(os.listdir(self.tmp / "cloud" / PLAN), [name])
            if args[0] == "evict":
                raise so.unverified("BRCTL_FAILED")
            return real_run(args, deadline)

        with mock.patch.object(backend, "_run", side_effect=inspect):
            backend.put(source, PLAN, name)
        source.write_bytes(b"different")
        with self.assertRaises(so.OffloadError) as caught:
            backend.put(source, PLAN, name)
        self.assertEqual(caught.exception.code, "REMOTE_CONFLICT")
        plan = PLAN + "-partial"
        with mock.patch.object(so.os, "rename", side_effect=OSError("synthetic interruption")), \
                self.assertRaises(so.OffloadError):
            backend.put(source, plan, so.names(plan)["ciphertext"])
        self.assertEqual(os.listdir(self.tmp / "cloud" / plan), [])

    # --- rclone backend (fake binary) ---------------------------------------------------------

    def fake_rclone(self, hash_type="sha256", **env):
        script = self.tmp / "fake-rclone.py"
        script.write_text(FAKE_RCLONE)
        wrapper = self.tmp / "rclone"
        wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {script} \"$@\"\n")
        wrapper.chmod(0o755)
        (self.tmp / "rclone-root").mkdir(exist_ok=True)
        conf = self.tmp / "rclone.conf"
        if not conf.exists():
            conf.write_text("[fake]\ntype = local\n")
        backend = {"kind": "rclone", "rclone": str(wrapper), "rclone_config": str(self.tmp / "rclone.conf"),
                   "remote": "fake:JouleWise-offload", "hash_type": hash_type, "timeout_s": 60,
                   "readback_tries": 2, "readback_wait_s": 0}
        values = {"FAKE_RCLONE_ROOT": str(self.tmp / "rclone-root"), "FAKE_RCLONE_LOG": str(self.tmp / "rclone.log")}
        values.update(env)
        patcher = mock.patch.dict(os.environ, values)
        patcher.start()
        self.addCleanup(patcher.stop)
        return backend

    def test_rclone_checks_each_hash_type_but_never_satisfies_rl174_copy_gate(self):
        for hash_type in ("sha256", "md5", "dropbox", "size"):
            with self.subTest(hash_type=hash_type):
                plan = f"{PLAN}-{hash_type}"
                config = dict(self.config, backend=self.fake_rclone(hash_type))
                record = so.offload(config, plan, self.span_for(plan))
                self.assertFalse(record["provider_confirmed"])
                self.assertFalse(self.marker(plan, True).exists())
                for row in record["provider_confirmation"]:
                    self.assertEqual(row["provider_size"], row["size"])
                    self.assertEqual(row["provider_hash_type"], hash_type)
                    if hash_type == "sha256":
                        self.assertEqual(row["provider_hash"], row["sha256"])
                    elif hash_type == "size":
                        self.assertIsNone(row["provider_hash"])
                air = dict(self.air, backend=config["backend"])
                marker = json.loads(self.marker(plan).read_bytes())
                so.pull(air, plan, "cl-" + hash_type, self.tmp / "desk", so.expectations(marker))
                # Historical typed rclone markers are retained, but cannot satisfy today's gate.
                self.marker(plan, True).write_bytes(so.canonical(dict(record, provider_confirmed=True)))
                with self.assertRaises(so.OffloadError) as caught:
                    so.offload(config, plan, self.span_for(plan))
                self.assertEqual(caught.exception.code, "MARKER_INVALID")
        calls = [json.loads(line) for line in (self.tmp / "rclone.log").read_text().splitlines()]
        copies = [c for c in calls if "copyto" in c and c[c.index("copyto") + 1] == "--immutable"]
        self.assertEqual(len(copies), 4 * 4)
        self.assertTrue(all("--config" in c and c[-1].startswith("fake:JouleWise-offload/") for c in copies))
        downloads = [c for c in calls if "copyto" in c and c not in copies]
        self.assertTrue(downloads and all("--immutable" not in c for c in downloads))

    def test_rclone_failures_write_no_marker(self):
        cases = [("READBACK_HASH", {"FAKE_RCLONE_CORRUPT": ".tgz.enc"}),
                 ("READBACK_NO_HASH", {"FAKE_RCLONE_NOHASH": "1"}),
                 ("RCLONE_FAILED", {"FAKE_RCLONE_FAIL": "copyto"}),
                 ("RCLONE_FAILED", {"FAKE_RCLONE_FAIL": "lsjson"})]
        for index, (code, env) in enumerate(cases):
            with self.subTest(code=code, env=env):
                plan = f"{PLAN}-f{index}"
                config = dict(self.config, backend=self.fake_rclone(**env))
                with self.assertRaises(so.OffloadError) as caught:
                    so.offload(config, plan, self.span_for(plan))
                self.assertEqual((caught.exception.code, caught.exception.exit_kind), (code, "unverified"))
                self.assertEqual(os.listdir(self.tmp / "markers"), [])
                for key in env:
                    os.environ.pop(key)

    def test_rclone_timeout(self):
        backend = self.fake_rclone(FAKE_RCLONE_SLEEP="5")
        backend["timeout_s"] = 1
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(dict(self.config, backend=backend), PLAN, self.span)
        self.assertEqual((caught.exception.code, caught.exception.exit_kind), ("UPLOAD_TIMEOUT", "unverified"))
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    # --- round-1 regressions (Sol r1 findings 1-8, 10) ---------------------------------------

    def test_stage_reuse_is_bound_to_the_same_unchanged_source(self):
        with mock.patch.object(so.LocalBackend, "put", side_effect=so.unverified("UPLOAD_TIMEOUT", "x")):
            with self.assertRaises(so.OffloadError):
                self.offload()
        receipt = self.span / "runner_receipt.json"
        original, stamp = receipt.read_bytes(), os.stat(receipt)
        receipt.write_bytes(b"changed after the first attempt")
        with self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "STAGE_CONFLICT")
        receipt.write_bytes(original)
        os.utime(receipt, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        other = self.tmp / "elsewhere" / SPAN  # same basename, another source
        self.make_span(other)
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(self.config, PLAN, other, allow_local=True)
        self.assertEqual(caught.exception.code, "STAGE_CONFLICT")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])
        self.assertTrue(self.offload()["stage_reused"])  # the original source, unchanged: reused

    def test_one_offload_per_plan_at_a_time(self):
        with so.plan_lock(self.tmp / "stage", PLAN):
            with self.assertRaises(so.OffloadError) as caught:
                self.offload()
        self.assertEqual(caught.exception.code, "BUSY")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    def test_a_stage_that_changes_before_or_during_upload_writes_no_marker(self):
        real_build, real_put = so.build_stage, so.LocalBackend.put

        def tamper_after_build(*args, **kwargs):
            stage, descriptor, reused, digest = real_build(*args, **kwargs)
            path = stage / f"{PLAN}.tgz.enc"
            os.chmod(path, 0o600)
            data = bytearray(path.read_bytes()); data[-1] ^= 1; path.write_bytes(bytes(data))
            return stage, descriptor, reused, digest

        with mock.patch.object(so, "build_stage", tamper_after_build), self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "STAGE_CHANGED")
        shutil.rmtree(self.tmp / "stage" / PLAN)
        shutil.rmtree(self.tmp / "cloud" / PLAN, ignore_errors=True)

        def swap_during_upload(backend, local, plan, name, deadline=None):
            row = real_put(backend, local, plan, name, deadline)
            return dict(row, sha256="0" * 64) if name.endswith(".SHA256SUMS") else row

        with mock.patch.object(so.LocalBackend, "put", swap_during_upload), self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "STAGE_CHANGED")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    def test_output_paths_outside_the_span_and_any_repository(self):
        before = so.hash_tree(self.span)
        for key in ("stage_root", "marker_dir"):
            with self.subTest(key=key):
                with self.assertRaises(so.OffloadError) as caught:
                    so.offload(dict(self.config, **{key: str(self.span)}), PLAN, self.span, allow_local=True)
                self.assertEqual(caught.exception.code, "PATH_OVERLAPS_SPAN")
        backend = {"kind": "local", "root": str(self.span / "runtime")}
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(dict(self.config, backend=backend), PLAN, self.span, allow_local=True)
        self.assertEqual(caught.exception.code, "PATH_OVERLAPS_SPAN")
        repo = self.tmp / "repo"
        (repo / "markers").mkdir(parents=True)
        init_git_fixture(repo, "-q")
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(dict(self.config, marker_dir=str(repo / "markers")), PLAN, self.span, allow_local=True)
        self.assertEqual(caught.exception.code, "PATH_IN_REPOSITORY")
        self.assertEqual(so.hash_tree(self.span), before)
        self.assertEqual([n for n in os.listdir(self.tmp / "stage") if not n.startswith(".")], [])

    def test_a_stalled_encryptor_is_killed_at_the_deadline(self):
        stall = self.tmp / "openssl-stall"
        stall.write_text(f'#!/bin/sh\ncase "$1" in enc) exec sleep 60 ;; esac\nexec {OPENSSL} "$@"\n')
        stall.chmod(0o755)
        (self.span / "runtime" / "incompressible.bin").write_bytes(os.urandom(4_000_000))
        start = time.monotonic()
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(dict(self.config, openssl=str(stall)), PLAN, self.span, allow_local=True,
                       deadline_epoch=time.time() + 2)
        self.assertEqual((caught.exception.code, caught.exception.exit_kind), ("DEADLINE", "unverified"))
        self.assertLess(time.monotonic() - start, 30)
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    def test_the_recipient_key_is_read_once(self):
        other = Path(tempfile.mkdtemp(prefix="offload-swap-key-"))
        self.addCleanup(shutil.rmtree, other)
        so.keygen(OPENSSL, other, bits=3072)
        public = self.tmp / "recipient.pub.pem"
        shutil.copyfile(self.public, public)
        config = dict(self.config, recipient_public_key=str(public))
        real = so.check_recipient

        def swap_after_check(*args, **kwargs):
            result = real(*args, **kwargs)
            shutil.copyfile(other / "span-offload.pub.pem", public)  # the file changes after the pin check
            return result

        with mock.patch.object(so, "check_recipient", swap_after_check):
            so.offload(config, PLAN, self.span, allow_local=True)
        self.pull()  # still decrypts with the pinned key's private half
        self.assertTrue((self.tmp / "desk" / "cl-syn-01" / SPAN).is_dir())

    def test_pull_refuses_a_symlinked_kit_dir(self):
        self.offload()
        outside = self.tmp / "outside"
        outside.mkdir()
        os.symlink(outside, self.tmp / "desk" / "cl-syn-01")
        with self.assertRaises(so.OffloadError) as caught:
            self.pull()
        self.assertEqual(caught.exception.code, "DEST_SYMLINK")
        self.assertEqual(os.listdir(outside), [])

    def test_an_interrupted_landing_is_refused_not_trusted(self):
        self.offload()
        real_chmod = os.chmod
        final = self.tmp / "desk" / "cl-syn-01" / SPAN

        def interrupt(path, mode, *args, **kwargs):
            if Path(path) == final:
                raise KeyboardInterrupt
            return real_chmod(path, mode, *args, **kwargs)

        with mock.patch.object(so.os, "chmod", interrupt), self.assertRaises(KeyboardInterrupt):
            self.pull()
        self.assertTrue(final.is_dir())
        self.assertFalse((final.parent / f"{SPAN}.pull.ok").exists())
        with self.assertRaises(so.OffloadError) as caught:
            self.pull()
        self.assertEqual((caught.exception.code, caught.exception.exit_kind), ("INCOMPLETE_LANDING", "dest_exists"))
        final.rename(self.tmp / "aside")  # the lead moves it aside; the next pull lands it completely
        self.pull()
        done = json.loads((final.parent / f"{SPAN}.pull.ok").read_bytes())
        self.assertEqual(done["plan"], PLAN)
        self.assertEqual(stat.S_IMODE(os.stat(final).st_mode), 0o555)

    def test_pull_refuses_duplicate_members(self):
        cloud = self.tmp / "cloud" / PLAN
        cloud.mkdir()
        raw = io.BytesIO()
        with gzip.GzipFile(fileobj=raw, mode="wb") as gz, tarfile.open(fileobj=gz, mode="w|") as tar:
            top = tarfile.TarInfo(SPAN); top.type = tarfile.DIRTYPE; tar.addfile(top)
            for payload in (b"one", b"two"):
                info = tarfile.TarInfo(f"{SPAN}/a.txt"); info.size = 3
                tar.addfile(info, io.BytesIO(payload))
        expect = self.plant_hostile(cloud, raw.getvalue(), b"%s  ./a.txt\n" % hashlib.sha256(b"two").hexdigest().encode())
        with self.assertRaises(so.OffloadError) as caught:
            self.pull(expect)
        self.assertEqual(caught.exception.code, "ARCHIVE_DUPLICATE")

    def plant_hostile(self, cloud, archive, manifest):
        passphrase = b"cd" * 32
        plain = self.tmp / "hostile2.tgz"
        plain.write_bytes(archive)
        names = so.names(PLAN)
        read_end, write_end = os.pipe()
        os.write(write_end, passphrase + b"\n"); os.close(write_end)
        subprocess.run([OPENSSL, *so._enc_args(False, read_end), "-in", str(plain), "-out",
                        str(cloud / names["ciphertext"])], check=True, pass_fds=(read_end,))
        os.close(read_end)
        so.wrap_passphrase(OPENSSL, self.public, passphrase, cloud / names["wrapped_key"])
        (cloud / names["manifest"]).write_bytes(manifest)
        descriptor = {"schema": so.DESCRIPTOR_SCHEMA, "plan": PLAN, "span_name": SPAN,
                      "scheme": {"recipient_sha256": self.fingerprint},
                      "archive": {"sha256": hashlib.sha256(archive).hexdigest(), "size": len(archive)},
                      "files": {k: {"name": names[k], "sha256": so.sha256_file(cloud / names[k]),
                                    "size": (cloud / names[k]).stat().st_size}
                                for k in ("ciphertext", "wrapped_key", "manifest")}}
        (cloud / names["descriptor"]).write_bytes(so.canonical(descriptor))
        return so.expectations(None, so.sha256_file(cloud / names["manifest"]), so.sha256_file(cloud / names["ciphertext"]))

    # --- round-1 regressions (Mythos r1 F1-F10, N1, N4) ---------------------------------------

    def test_two_offloads_of_one_plan_never_mix(self):
        real = so.encrypt_span
        started = threading.Event()

        def slow(*args, **kwargs):
            started.set()
            time.sleep(1.0)
            return real(*args, **kwargs)

        results = {}

        def first():
            try:
                results["a"] = self.offload()
            except so.OffloadError as error:
                results["a"] = error

        with mock.patch.object(so, "encrypt_span", slow):
            worker = threading.Thread(target=first)
            worker.start()
            started.wait(10)
            with self.assertRaises(so.OffloadError) as caught:
                self.offload()
            worker.join(30)
        self.assertEqual(caught.exception.code, "BUSY")
        self.assertIsInstance(results["a"], dict)
        self.pull()  # the one marker written decrypts and matches
        self.assertEqual(so.hash_tree(self.tmp / "desk" / "cl-syn-01" / SPAN), so.hash_tree(self.span))

    def test_span_identity_emptiness_and_fence(self):
        cases = [("PLAN_SPAN_MISMATCH", lambda: so.offload(self.config, "cq-syn-01-s02-a1", self.span, allow_local=True)),
                 ("SPAN_EMPTY", lambda: so.offload(self.config, PLAN, self.empty_span(receipt=False),
                                                   require_files=(), allow_local=True))]
        fence = self.tmp / "desk_fence.json"
        fence.write_text("{}")
        cases.append(("FORBIDDEN_PATH_PRESENT", lambda: so.offload(dict(self.config, forbid_paths=[str(fence)]), PLAN,
                                                                   self.span, allow_local=True)))
        for code, call in cases:
            with self.subTest(code=code):
                with self.assertRaises(so.OffloadError) as caught:
                    call()
                self.assertEqual(caught.exception.code, code)
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    def empty_span(self, receipt):
        span = self.tmp / "empty" / f"{PLAN}-20990101T000001Z"
        span.mkdir(parents=True, exist_ok=True)
        if receipt:
            (span / "runner_receipt.json").write_bytes(b"x")
        return span

    def test_a_ciphertext_that_does_not_decrypt_writes_no_marker(self):
        liar = self.tmp / "openssl-liar"
        liar.write_text(f'#!/bin/sh\nif [ "$1" = enc ] && [ "$2" = -e ]; then cat >/dev/null; exit 0; fi\n'
                        f'exec {OPENSSL} "$@"\n')
        liar.chmod(0o755)
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(dict(self.config, openssl=str(liar)), PLAN, self.span, allow_local=True)
        self.assertEqual(caught.exception.code, "CIPHERTEXT_UNVERIFIED")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])
        self.assertEqual([n for n in os.listdir(self.tmp / "stage") if not n.startswith(".")], [])

    def test_no_time_left_does_nothing(self):
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(self.config, PLAN, self.span, allow_local=True, deadline_epoch=time.time() - 1)
        self.assertEqual(caught.exception.code, "DEADLINE")
        for bad in (-1, 0, float("nan"), "90"):
            with self.assertRaises(so.OffloadError) as caught:
                so.offload(dict(self.config, default_budget_s=bad), PLAN, self.span, allow_local=True)
            self.assertEqual(caught.exception.code, "CONFIG")
        self.assertEqual([n for n in os.listdir(self.tmp / "stage") if not n.startswith(".")], [])

    def test_remote_must_be_a_named_rclone_remote(self):
        for remote in (":local:/x", "/path/with:colon", "--flag:x", "noremote"):
            with self.subTest(remote=remote):
                with self.assertRaises(so.OffloadError):
                    so.RcloneBackend({"remote": remote, "rclone_config": "/nonexistent/rclone.conf"})
        so.RcloneBackend({"remote": "jwoffload:JouleWise-offload", "rclone_config": "/x/rclone.conf"})

    def test_dropbox_digest_is_the_content_hash_of_one_read(self):
        blob = self.tmp / "blob"
        data = os.urandom(9 * 1024 * 1024 + 5)
        blob.write_bytes(data)
        blocks = b"".join(hashlib.sha256(data[i:i + 4194304]).digest() for i in range(0, len(data), 4194304))
        snap = so.snapshot_digests(blob, ("dropbox", "md5"))
        self.assertEqual(snap["dropbox"], hashlib.sha256(blocks).hexdigest())
        self.assertEqual(snap["md5"], hashlib.md5(data).hexdigest())
        self.assertEqual((snap["sha256"], snap["size"]), (hashlib.sha256(data).hexdigest(), len(data)))

    def test_sigterm_kills_the_upload_and_exits_5(self):
        backend = self.fake_rclone(FAKE_RCLONE_SLEEP="30", FAKE_RCLONE_PIDFILE=str(self.tmp / "rclone.pids"))
        config = self.tmp / "mbp.json"
        config.write_text(json.dumps(dict(self.config, backend=backend)))
        root = Path(__file__).resolve().parents[1]
        proc = subprocess.Popen([sys.executable, str(root / "scripts" / "span_offload.py"), "offload", "--config",
                                 str(config), "--plan", PLAN, "--span-dir", str(self.span)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.time() + 30
        while not (self.tmp / "rclone.pids").exists() and time.time() < deadline:
            time.sleep(0.1)
        time.sleep(0.3)
        proc.send_signal(signal.SIGTERM)
        out, err = proc.communicate(timeout=30)
        self.assertEqual(proc.returncode, so.EXIT["unverified"])
        self.assertIn(b"TERMINATED", err)
        self.assertEqual(len(err.strip().splitlines()), 1)
        time.sleep(0.3)
        for pid in (self.tmp / "rclone.pids").read_text().split():
            with self.assertRaises(ProcessLookupError):
                os.kill(int(pid), 0)
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    # --- round-2 regressions (Sol r2 findings 1-7) -----------------------------------------------

    def test_staged_bytes_changing_at_the_upload_are_refused(self):
        backend = self.fake_rclone()
        real_run = so.RcloneBackend._run

        def mutate_before_copy(rclone, args, deadline, cap=None):
            if args[:2] == ["copyto", "--immutable"] and args[2].endswith(".tgz.enc"):
                os.chmod(args[2], 0o600)
                data = bytearray(Path(args[2]).read_bytes()); data[-1] ^= 1; Path(args[2]).write_bytes(bytes(data))
            return real_run(rclone, args, deadline, cap)

        with mock.patch.object(so.RcloneBackend, "_run", mutate_before_copy), \
                self.assertRaises(so.OffloadError) as caught:
            so.offload(dict(self.config, backend=backend), PLAN, self.span)
        self.assertEqual(caught.exception.code, "STAGE_CHANGED")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    def test_control_paths_inside_out_or_behind_links_are_never_read(self):
        inside = self.span / "mbp.json"
        inside.write_text(json.dumps(self.config))
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["offload", "--config", str(inside), "--plan", PLAN, "--span-dir",
                                       str(self.span), "--allow-local-backend"]), so.EXIT["refused"])
        self.assertIn("PATH_OVERLAPS_SPAN", err.getvalue())
        inside.unlink()
        os.symlink(self.span / "desk-bundle", self.tmp / "stage" / PLAN)
        with mock.patch.object(so.json, "loads", wraps=json.loads) as loads, \
                self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "STAGE_CONFLICT")
        self.assertEqual(loads.call_count, 0)

    def test_destinations_behind_links_or_in_repositories_are_refused(self):
        os.symlink(self.span, self.tmp / "cloud" / PLAN)
        before = so.hash_tree(self.span)
        with self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "BACKEND_PATH")
        self.assertEqual(so.hash_tree(self.span), before)
        os.unlink(self.tmp / "cloud" / PLAN)
        self.offload()
        kit = self.tmp / "desk" / "cl-syn-01"
        kit.mkdir()
        init_git_fixture(kit, "-q")
        with self.assertRaises(so.OffloadError) as caught:
            self.pull()
        self.assertEqual(caught.exception.code, "PATH_IN_REPOSITORY")
        with self.assertRaises(so.OffloadError) as caught:
            so.keygen(OPENSSL, kit, bits=3072)
        self.assertEqual(caught.exception.code, "PATH_IN_REPOSITORY")

    def test_a_fifo_as_the_recipient_key_does_not_hang(self):
        fifo = self.tmp / "key.fifo"
        os.mkfifo(fifo)
        start = time.monotonic()
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(dict(self.config, recipient_public_key=str(fifo)), PLAN, self.span, allow_local=True)
        self.assertEqual(caught.exception.code, "RECIPIENT_UNREADABLE")
        self.assertLess(time.monotonic() - start, 5)

    def test_sigterm_during_a_stalled_encryption_exits_promptly(self):
        stall = self.tmp / "openssl-stall"
        stall.write_text(f'#!/bin/sh\ncase "$1" in enc) exec sleep 60 ;; esac\nexec {OPENSSL} "$@"\n')
        stall.chmod(0o755)
        (self.span / "runtime" / "incompressible.bin").write_bytes(os.urandom(4_000_000))
        config = self.tmp / "mbp.json"
        config.write_text(json.dumps(dict(self.config, openssl=str(stall))))
        root = Path(__file__).resolve().parents[1]
        proc = subprocess.Popen([sys.executable, str(root / "scripts" / "span_offload.py"), "offload", "--config",
                                 str(config), "--plan", PLAN, "--span-dir", str(self.span), "--allow-local-backend"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2.0)
        proc.send_signal(signal.SIGTERM)
        out, err = proc.communicate(timeout=15)
        self.assertEqual(proc.returncode, so.EXIT["unverified"])
        self.assertEqual(len(err.strip().splitlines()), 1)
        self.assertIn(b"TERMINATED", err)

    def test_an_empty_completion_record_is_an_incomplete_landing(self):
        self.offload()
        real = so.write_marker

        def crash(path, record):
            Path(path).write_bytes(b"")
            raise KeyboardInterrupt

        with mock.patch.object(so, "write_marker", crash), self.assertRaises(KeyboardInterrupt):
            self.pull()
        with self.assertRaises(so.OffloadError) as caught:
            self.pull()
        self.assertEqual(caught.exception.code, "INCOMPLETE_LANDING")
        self.assertIs(so.write_marker, real)

    def test_odd_provider_listings_and_member_names_are_classified(self):
        backend = so.RcloneBackend({"remote": "x:y", "hash_type": "size", "rclone_config": "/x/rclone.conf"})
        with mock.patch.object(backend, "_run", return_value=b"null"), self.assertRaises(so.OffloadError) as caught:
            backend._readback("p", "n", 1, "a" * 64, None, None)
        self.assertEqual((caught.exception.code, caught.exception.exit_kind), ("READBACK_UNPARSEABLE", "unverified"))
        cloud = self.tmp / "cloud" / PLAN
        cloud.mkdir()
        raw = io.BytesIO()
        with gzip.GzipFile(fileobj=raw, mode="wb") as gz, tarfile.open(fileobj=gz, mode="w|") as tar:
            top = tarfile.TarInfo(SPAN); top.type = tarfile.DIRTYPE; tar.addfile(top)
            info = tarfile.TarInfo(f"{SPAN}/bad\nname"); info.size = 1
            tar.addfile(info, io.BytesIO(b"x"))
        expect = self.plant_hostile(cloud, raw.getvalue(), b"")
        with self.assertRaises(so.OffloadError) as caught:
            self.pull(expect)
        self.assertEqual((caught.exception.code, caught.exception.exit_kind), ("ARCHIVE_PATH", "integrity"))

    # --- Mythos round-2 notes (R2-5, R2-7 to R2-11) -----------------------------------------------

    def test_names_deadlines_and_paths_from_mythos_round_2(self):
        for plan in ("cq-syn-01", "cq"):  # a bare prefix of the plan is not this span's plan
            with self.assertRaises(so.OffloadError) as caught:
                so.offload(self.config, plan, self.span, allow_local=True)
            self.assertEqual(caught.exception.code, "PLAN_SPAN_MISMATCH")
        for bad in (float("inf"), time.time() * 1000):
            with self.assertRaises(so.OffloadError) as caught:
                self.offload(deadline_epoch=bad)
            self.assertEqual(caught.exception.code, "BAD_DEADLINE")
        backend = {"kind": "rclone", "remote": "x:y", "rclone_config": str(self.span / "rclone.conf")}
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(dict(self.config, backend=backend), PLAN, self.span)
        self.assertEqual(caught.exception.code, "PATH_OVERLAPS_SPAN")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    def test_directories_the_tool_did_not_make_are_never_removed(self):
        foreign = self.tmp / "stage" / f".{PLAN}.building-foreign"
        foreign.mkdir()
        init_git_fixture(foreign, "-q")
        (foreign / "PRESERVE.txt").write_bytes(b"x")
        self.offload()
        self.assertTrue((foreign / "PRESERVE.txt").exists() and (foreign / ".git").is_dir())

    def test_hard_linked_control_files_are_refused(self):
        inside = self.span / "config-alias.json"
        inside.write_text(json.dumps(self.config))
        outside = self.tmp / "mbp-linked.json"
        os.link(inside, outside)
        with self.assertRaises(so.OffloadError) as caught:
            so.load_mbp_config(outside)
        self.assertEqual(caught.exception.code, "CONFIG")
        inside.unlink(); outside.unlink()
        with mock.patch.object(so.LocalBackend, "put", side_effect=so.unverified("UPLOAD_TIMEOUT", "x")):
            with self.assertRaises(so.OffloadError):
                self.offload()
        source = self.tmp / "stage" / PLAN / so.SOURCE_RECORD
        alias = self.tmp / "alias-of-source"
        os.link(source, alias)  # a second name for a stage record
        with self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "STAGE_CONFLICT")
        conf = self.span / "rclone.conf"
        conf.write_text("[x]\n")
        linked = self.tmp / "rclone-linked.conf"
        os.link(conf, linked)
        backend = {"kind": "rclone", "remote": "x:y", "rclone_config": str(linked)}
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(dict(self.config, backend=backend), "cq-syn-01-s05-a1", self.span_for("cq-syn-01-s05-a1"))
        self.assertEqual(caught.exception.code, "HARD_LINKED")

    def test_a_descriptor_changed_after_validation_writes_no_marker(self):
        real_build = so.build_stage

        def rewrite_descriptor(*args, **kwargs):
            stage, descriptor, reused, digest = real_build(*args, **kwargs)
            path = stage / f"{PLAN}.offload.json"
            os.chmod(path, 0o600)
            doc = json.loads(path.read_bytes()); doc["archive"]["sha256"] = "0" * 64
            path.write_bytes(so.canonical(doc)); os.chmod(path, 0o400)
            return stage, descriptor, reused, digest

        with mock.patch.object(so, "build_stage", rewrite_descriptor), self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "STAGE_CHANGED")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    def test_a_stage_file_swapped_for_a_fifo_after_validation_does_not_block(self):
        real_build = so.build_stage

        def fifo_after(*args, **kwargs):
            stage, descriptor, reused, digest = real_build(*args, **kwargs)
            path = stage / f"{PLAN}.tgz.enc"
            os.unlink(path); os.mkfifo(path)
            return stage, descriptor, reused, digest

        start = time.monotonic()
        with mock.patch.object(so, "build_stage", fifo_after), self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "NOT_A_REGULAR_FILE")
        self.assertLess(time.monotonic() - start, 10)

    def test_an_empty_wrapped_key_is_refused(self):
        original = so._openssl_run

        def fake(openssl, args, **kwargs):
            return b"" if args[:2] == ["pkeyutl", "-encrypt"] else original(openssl, args, **kwargs)

        with mock.patch.object(so, "_openssl_run", fake), self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "WRAP_INVALID")

    def test_pull_folds_duplicate_names_and_ties_the_span_to_the_plan(self):
        cloud = self.tmp / "cloud" / PLAN
        cloud.mkdir()
        for index, names in enumerate(([f"{SPAN}/a.txt", f"{SPAN}/./a.txt"], [f"{SPAN}/A.txt", f"{SPAN}/a.txt"])):
            raw = io.BytesIO()
            with gzip.GzipFile(fileobj=raw, mode="wb") as gz, tarfile.open(fileobj=gz, mode="w|") as tar:
                top = tarfile.TarInfo(SPAN); top.type = tarfile.DIRTYPE; tar.addfile(top)
                for name in names:
                    info = tarfile.TarInfo(name); info.size = 1
                    tar.addfile(info, io.BytesIO(b"x"))
            for f in cloud.iterdir():
                f.unlink()
            expect = self.plant_hostile(cloud, raw.getvalue(), b"")
            with self.subTest(index=index), self.assertRaises(so.OffloadError) as caught:
                self.pull(expect)
            self.assertIn(caught.exception.code, ("ARCHIVE_PATH", "ARCHIVE_DUPLICATE"))
            self.assertEqual(caught.exception.exit_kind, "integrity")

    # --- Sol round-3 regressions (findings 1-5) ------------------------------------------------

    def test_an_edit_restored_after_the_upload_is_caught_in_every_hash_mode(self):
        for mode in ("md5", "sha1", "dropbox", "sha256"):
            with self.subTest(mode=mode):
                plan = f"cq-syn-0{('md5', 'sha1', 'dropbox', 'sha256').index(mode) + 2}-s01-a1"
                backend = self.fake_rclone(mode)
                real_run = so.RcloneBackend._run
                saved = {}

                def edit_then_restore(rclone, args, deadline, cap=None):
                    if args[:2] == ["copyto", "--immutable"] and args[2].endswith(".tgz.enc"):
                        path = Path(args[2])
                        os.chmod(path, 0o600)
                        saved["bytes"] = path.read_bytes()
                        path.write_bytes(saved["bytes"][:-1] + bytes([saved["bytes"][-1] ^ 1]))
                        try:
                            return real_run(rclone, args, deadline, cap)
                        finally:
                            path.write_bytes(saved["bytes"])  # restored before the post-upload check
                    return real_run(rclone, args, deadline, cap)

                with mock.patch.object(so.RcloneBackend, "_run", edit_then_restore), \
                        self.assertRaises(so.OffloadError) as caught:
                    so.offload(dict(self.config, backend=backend), plan, self.span_for(plan))
                self.assertEqual(caught.exception.code, "READBACK_HASH")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    def test_the_local_backend_never_follows_a_planted_temp_name_or_writes_into_a_repository(self):
        before = so.hash_tree(self.span)
        plan_dir = self.tmp / "cloud" / PLAN
        plan_dir.mkdir()
        for pid in range(os.getpid() - 2, os.getpid() + 3):
            os.symlink(self.span / "runner_receipt.json", plan_dir / f".{PLAN}.tgz.enc.part-{pid}")
        self.offload()
        self.assertEqual(so.hash_tree(self.span), before)
        self.assertFalse(os.path.islink(plan_dir / f"{PLAN}.tgz.enc"))
        other = "cq-syn-01-s02-a1"
        nested = self.tmp / "cloud" / other
        nested.mkdir()
        init_git_fixture(nested, "-q")
        with self.assertRaises(so.OffloadError) as caught:
            so.offload(self.config, other, self.span_for(other), allow_local=True)
        self.assertEqual(caught.exception.code, "BACKEND_PATH")
        self.assertEqual(sorted(os.listdir(nested)), [".git"])

    def test_control_files_that_are_fifos_never_block(self):
        fifo = self.tmp / "config.fifo"
        os.mkfifo(fifo)
        start = time.monotonic()
        with self.assertRaises(so.OffloadError) as caught:
            so.load_mbp_config(fifo)
        self.assertEqual(caught.exception.code, "CONFIG")
        with mock.patch.object(so.LocalBackend, "put", side_effect=so.unverified("UPLOAD_TIMEOUT", "x")):
            with self.assertRaises(so.OffloadError):
                self.offload()
        source = self.tmp / "stage" / PLAN / so.SOURCE_RECORD
        os.chmod(source.parent, 0o700)
        source.unlink()
        os.mkfifo(source)
        with self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "STAGE_CONFLICT")
        self.assertLess(time.monotonic() - start, 10)

    def test_malformed_provider_hashes_are_unverified(self):
        backend = so.RcloneBackend({"remote": "x:y", "hash_type": "md5", "rclone_config": "/x/rclone.conf"})
        for hashes in (1, "wrong", {"md5": 5}):
            listing = json.dumps([{"Name": "n", "Size": 1, "Hashes": hashes}]).encode()
            with self.subTest(hashes=hashes), mock.patch.object(backend, "_run", return_value=listing), \
                    self.assertRaises(so.OffloadError) as caught:
                backend._readback("p", "n", 1, "a" * 64, "b" * 32, None)
            self.assertEqual((caught.exception.code, caught.exception.exit_kind), ("READBACK_UNPARSEABLE", "unverified"))

    def test_pull_refuses_a_key_in_a_repository_and_a_bad_deadline(self):
        self.offload()
        repo = self.tmp / "keyrepo"
        repo.mkdir()
        init_git_fixture(repo, "-q")
        shutil.copyfile(self.private, repo / "k.pem")
        with self.assertRaises(so.OffloadError) as caught:
            self.pull(config=dict(self.air, identity=str(repo / "k.pem")))
        self.assertEqual(caught.exception.code, "PATH_IN_REPOSITORY")
        expect = so.expectations(json.loads(self.marker().read_bytes()))
        for bad in (float("nan"), float("inf"), time.time() * 1000):
            with self.assertRaises(so.OffloadError) as caught:
                so.pull(self.air, PLAN, "cl-syn-01", self.tmp / "desk", expect, allow_local=True, deadline_epoch=bad)
            self.assertEqual(caught.exception.code, "BAD_DEADLINE")

    def test_round_5_rclone_config_and_reused_descriptor(self):
        with self.assertRaises(so.OffloadError) as caught:
            so.RcloneBackend({"remote": "x:y"})  # rclone's own config discovery is never used
        self.assertEqual(caught.exception.code, "CONFIG")
        with mock.patch.object(so.LocalBackend, "put", side_effect=so.unverified("UPLOAD_TIMEOUT", "x")):
            with self.assertRaises(so.OffloadError):
                self.offload()
        path = self.tmp / "stage" / PLAN / f"{PLAN}.offload.json"
        os.chmod(path, 0o600)
        doc = json.loads(path.read_bytes()); doc["archive"]["sha256"] = "0" * 64
        path.write_bytes(so.canonical(doc)); os.chmod(path, 0o400)
        with self.assertRaises(so.OffloadError) as caught:
            self.offload()
        self.assertEqual(caught.exception.code, "STAGE_CONFLICT")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])

    def test_the_pull_checks_its_rclone_config(self):
        self.offload()
        repo = self.tmp / "conf-repo"
        repo.mkdir()
        init_git_fixture(repo, "-q")
        (repo / "rclone.conf").write_text("[x]\n")
        air = dict(self.air, backend={"kind": "rclone", "remote": "x:y", "rclone_config": str(repo / "rclone.conf")})
        with self.assertRaises(so.OffloadError) as caught:
            self.pull(config=air)
        self.assertEqual(caught.exception.code, "PATH_IN_REPOSITORY")

    def test_openssl_reads_no_configuration_from_the_environment(self):
        (self.span / "runner_receipt.json").write_bytes(b"this is not = an [openssl config\nmissing equal sign\n")
        with mock.patch.dict(os.environ, {"OPENSSL_CONF": str(self.span / "runner_receipt.json")}):
            record = self.offload()  # a parsed OPENSSL_CONF here would fail with "missing equal sign"
        self.assertEqual(record["schema"], so.MARKER_SCHEMA)
        env = so.openssl_env()
        self.assertEqual(env["OPENSSL_CONF"], os.devnull)

    # --- CLI ----------------------------------------------------------------------------------

    def test_cli_exit_codes_and_one_line_output(self):
        mbp = self.tmp / "mbp.json"
        mbp.write_text(json.dumps(self.config))
        air = self.tmp / "air.json"
        air.write_text(json.dumps(self.air))
        argv = ["offload", "--config", str(mbp), "--plan", PLAN, "--span-dir", str(self.span),
                "--require-file", "runner_receipt.json"]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(cli.main(argv), so.EXIT["refused"])  # local backend not allowed by default
            self.assertEqual(cli.main(argv + ["--allow-local-backend"]), so.EXIT["unconfirmed"])
            self.assertEqual(cli.main(argv + ["--allow-local-backend"]), so.EXIT["marker_exists"])
        self.assertIn("LOCAL_BACKEND_NOT_ALLOWED", err.getvalue())
        self.assertRegex(out.getvalue(), r"^OFFLOAD_OK_UNCONFIRMED plan=cq-syn-01-s01-a1 backend=local provider_confirmed=false .* "
                                       r"marker=\S+/cq-syn-01-s01-a1\.ok\.unconfirmed\n")
        pull = ["pull", "--config", str(air), "--plan", PLAN, "--kit", "cl-syn-01", "--dest-root",
                str(self.tmp / "desk"), "--marker", str(self.marker()), "--allow-local-backend"]
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(cli.main(pull), 0)
            self.assertEqual(cli.main(pull), so.EXIT["dest_exists"])
        self.assertTrue(out.getvalue().startswith("PULL_OK plan=cq-syn-01-s01-a1 kit=cl-syn-01 files=6 "))
        self.assertNotIn("synthetic", out.getvalue() + err.getvalue())


class SpanOffloadStaticTests(unittest.TestCase):
    def test_tool_never_parses_span_files_and_has_no_git_step(self):
        """A.4 and A.6, read as source: the only json.loads calls are on the tool's own records."""
        source = Path(so.__file__).read_text()
        self.assertNotRegex(source, r"\[\s*['\"]git['\"]")
        loads = [line.strip() for line in source.splitlines() if "json.loads(" in line]
        allowed = ("descriptor_path.read_bytes()", "listing", "Path(path).read_text()",
                   'tmp / files["descriptor"]', "_read_in(dfd", "descriptor_bytes", "handle.read(65536)", "handle.read(1 << 20)")
        for line in loads:
            self.assertTrue(any(token in line for token in allowed), line)


if __name__ == "__main__":
    unittest.main()
