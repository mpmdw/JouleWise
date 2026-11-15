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
import stat
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import unittest
from unittest import mock

from joulewise import span_offload as so
from scripts import span_offload as cli

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
        return hashlib.sha256(b"dbx" + data).hexdigest()
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

    def marker(self, plan=PLAN, confirmed=False):
        return so.marker_path(self.tmp / "markers", plan, confirmed)

    def pull(self, expect=None, kit="cl-syn-01", config=None):
        if expect is None:
            expect = so.expectations(json.loads(self.marker().read_bytes()))
        return so.pull(config or self.air, PLAN, kit, self.tmp / "desk", expect, allow_local=True)

    # --- offload ------------------------------------------------------------------------------

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
        link = self.tmp / "campaign-out" / (SPAN + "-link")
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
        self.assertEqual(os.listdir(self.tmp / "stage"), [])

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

    def test_retry_reuses_a_complete_stage_and_sets_aside_a_partial_one(self):
        with mock.patch.object(so.LocalBackend, "put", side_effect=so.unverified("UPLOAD_TIMEOUT", "x")):
            with self.assertRaises(so.OffloadError) as caught:
                self.offload()
        self.assertEqual(caught.exception.exit_kind, "unverified")
        self.assertEqual(os.listdir(self.tmp / "markers"), [])
        staged = so.sha256_file(self.tmp / "stage" / PLAN / f"{PLAN}.tgz.enc")
        record = self.offload()
        self.assertTrue(record["stage_reused"])
        self.assertEqual(record["ciphertext"]["sha256"], staged)
        # A partial stage (no descriptor) is renamed aside, never reused.
        other = PLAN.replace("s01", "s02")
        (self.tmp / "stage" / other).mkdir()
        (self.tmp / "stage" / other / f"{other}.tgz.enc").write_bytes(b"half")
        record = so.offload(self.config, other, self.span, allow_local=True)
        self.assertFalse(record["stage_reused"])
        self.assertTrue(any(n.startswith(other + ".partial-") for n in os.listdir(self.tmp / "stage")))

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

    def fake_rclone(self, hash_type="sha256", **env):
        script = self.tmp / "fake-rclone.py"
        script.write_text(FAKE_RCLONE)
        wrapper = self.tmp / "rclone"
        wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {script} \"$@\"\n")
        wrapper.chmod(0o755)
        (self.tmp / "rclone-root").mkdir(exist_ok=True)
        backend = {"kind": "rclone", "rclone": str(wrapper), "rclone_config": str(self.tmp / "rclone.conf"),
                   "remote": "fake:JouleWise-offload", "hash_type": hash_type, "timeout_s": 60,
                   "readback_tries": 2, "readback_wait_s": 0}
        values = {"FAKE_RCLONE_ROOT": str(self.tmp / "rclone-root"), "FAKE_RCLONE_LOG": str(self.tmp / "rclone.log")}
        values.update(env)
        patcher = mock.patch.dict(os.environ, values)
        patcher.start()
        self.addCleanup(patcher.stop)
        return backend

    def test_rclone_backend_confirms_each_hash_type(self):
        for hash_type in ("sha256", "md5", "dropbox", "size"):
            with self.subTest(hash_type=hash_type):
                plan = f"{PLAN}-{hash_type}"
                config = dict(self.config, backend=self.fake_rclone(hash_type))
                record = so.offload(config, plan, self.span)
                self.assertTrue(record["provider_confirmed"])
                for row in record["provider_confirmation"]:
                    self.assertEqual(row["provider_size"], row["size"])
                    self.assertEqual(row["provider_hash_type"], hash_type)
                    if hash_type == "sha256":
                        self.assertEqual(row["provider_hash"], row["sha256"])
                    elif hash_type == "size":
                        self.assertIsNone(row["provider_hash"])
                air = dict(self.air, backend=config["backend"])
                marker = json.loads(self.marker(plan, True).read_bytes())
                so.pull(air, plan, "cl-" + hash_type, self.tmp / "desk", so.expectations(marker))
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
                    so.offload(config, plan, self.span)
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
            self.assertEqual(cli.main(argv + ["--allow-local-backend"]), 0)
            self.assertEqual(cli.main(argv + ["--allow-local-backend"]), so.EXIT["marker_exists"])
        self.assertIn("LOCAL_BACKEND_NOT_ALLOWED", err.getvalue())
        self.assertRegex(out.getvalue(), r"^OFFLOAD_OK plan=cq-syn-01-s01-a1 backend=local provider_confirmed=false ")
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
                   'tmp / files["descriptor"]')
        for line in loads:
            self.assertTrue(any(token in line for token in allowed), line)


if __name__ == "__main__":
    unittest.main()
