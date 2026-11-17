"""After-Check regressions on opaque synthetic spans and a fake iCloud provider."""
from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from joulewise import close_offload as co
from joulewise import span_offload as so
from tests.test_span_offload import FAKE_BRCTL, OPENSSL

CLI = Path(__file__).resolve().parents[1] / "scripts/close_offload.py"


@unittest.skipUnless(OPENSSL, "openssl is not installed")
class CloseOffloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        keys = cls.enterClassContext(tempfile.TemporaryDirectory(prefix="close-offload-keys-"))
        cls.fingerprint = so.keygen(OPENSSL, keys, bits=3072)
        cls.public = Path(keys) / "span-offload.pub.pem"

    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="close-offload-"))).resolve()
        for name in ("campaign", "worktrees", "stage", "markers", "cloud", "provider", "bin", "magistrate"):
            (self.root / name).mkdir()
        self.config_path = self.root / "config.json"
        self.config = {
            "schema": so.MBP_CONFIG_SCHEMA, "recipient_public_key": str(self.public),
            "recipient_sha256": self.fingerprint, "stage_root": str(self.root / "stage"),
            "marker_dir": str(self.root / "markers"), "openssl": OPENSSL, "lead_email": "lead@example.test",
            "backend": {"kind": "icloud", "root": str(self.root / "cloud"),
                        "brctl": str(self.root / "bin/brctl"), "timeout_s": 0.7,
                        "evict_timeout_s": 0.25, "poll_interval_s": 0.01},
        }
        self.config_path.write_bytes(so.canonical(self.config))
        self.fence = self.root / "magistrate/desk_fence.json"
        self.exe("pgrep", "raise SystemExit(int(os.environ.get('FAKE_PGREP_RC', '1')))\n", "import os\n")
        self.exe("brctl", FAKE_BRCTL)
        # The supervisor launches a new interpreter. Keep actual disk space and
        # the production mail command out of its fixtures too.
        (self.root / "bin/sitecustomize.py").write_text(
            "import shutil\nshutil.disk_usage = lambda path: (10**12, 0, 10**12)\n"
        )
        self.enterContext(mock.patch.dict(os.environ, {"PATH": str(self.root / "bin") + os.pathsep + os.environ["PATH"],
                                                       "FAKE_BRCTL_STATE": str(self.root / "provider"),
                                                       "PYTHONPATH": str(self.root / "bin")}))
        self.enterContext(mock.patch.object(so, "_is_dataless", side_effect=lambda info: info.st_size == 0))
        self.enterContext(mock.patch.object(so.shutil, "disk_usage",
                                          return_value=(10**12, 0, 10**12)))

    def exe(self, name, body, imports=""):
        path = self.root / "bin" / name
        path.write_text(f"#!{sys.executable}\n" + imports + body)
        path.chmod(0o700)

    def span(self, plan, stamp, *, kind="campaign", tree="kit"):
        if kind == "campaign":
            out = self.root / "campaign" / tree / f"{plan}-20990101T000000Z"
        else:
            out = self.root / "worktrees" / tree / ".desk" / plan
        out.mkdir(parents=True)
        if kind == "partc":
            # A linked worktree has .git metadata above .desk. The backend must
            # accept only the output path and keep the rest of the worktree.
            (out.parents[1] / ".git").touch()
        receipt = out / "runner_receipt.json"
        receipt.write_bytes(b"opaque synthetic receipt {\x00\xff")
        os.utime(receipt, (stamp, stamp))
        (out / "opaque.bin").write_bytes(b"SYNTHETIC-PAYLOAD-DO-NOT-PRINT\x00\xff" * 100)
        (out / "empty").mkdir()
        return out

    def argv(self, out, *extra, command="after-check", seconds=20):
        return [command, "--config", str(self.config_path), "--deadline-epoch", str(time.time() + seconds),
                "--campaign-root", str(self.root / "campaign"), "--work-root", str(self.root / "worktrees"),
                "--fence", str(self.fence), "--span-dir", str(out), *extra]

    def verify(self, out, *extra, **kwargs):
        return co.run(co.parser().parse_args(self.argv(out, *extra, **kwargs)))

    def cli(self, out, *extra, **kwargs):
        return subprocess.run([sys.executable, "-B", str(CLI), *self.argv(out, *extra, **kwargs)],
                              capture_output=True, text=True, timeout=10)

    def marker(self, plan, confirmed=True):
        return so.marker_path(self.config["marker_dir"], plan, confirmed)

    def archive(self, plan):
        return self.root / "stage" / plan / so.names(plan)["ciphertext"]

    def calls(self):
        return [json.loads(line) for line in (self.root / "provider/calls").read_text().splitlines()]

    def test_first_check_copies_exact_out_but_keeps_the_newest_receipt(self):
        out = self.span("cq-first", 100)
        before = (out / "runner_receipt.json").stat()
        result = self.verify(out)
        self.assertEqual(result["status"], "CLOSE_OK")
        self.assertTrue(result["pending"]["clear"])
        self.assertFalse(result["spans"][0]["original_deleted"])
        self.assertEqual((out / "runner_receipt.json").stat().st_mtime_ns, before.st_mtime_ns)
        record = so.read_record(self.marker("cq-first"))
        files = so.marker_files(record, "cq-first", icloud=True)
        self.assertEqual(so.sha256_file(self.archive("cq-first")), files["ciphertext"]["sha256"])
        self.assertEqual(sum(cmd[0] == "evict" for cmd in self.calls()), 4)
        self.assertEqual(sum(cmd[0] == "download" for cmd in self.calls()), 4)

    def test_pack_manifest_mismatch_holds_and_keeps_raw(self):
        out = self.span("cq-old", 100)
        current = self.span("cq-current", 200)
        encrypt = so.encrypt_span

        def divergent_manifest(*args, **kwargs):
            manifest, digest, size, count = encrypt(*args, **kwargs)
            if args[1] == out:
                manifest = (b"0" if manifest[:1] != b"0" else b"1") + manifest[1:]
            return manifest, digest, size, count

        with mock.patch.object(so, "encrypt_span", divergent_manifest), self.assertRaisesRegex(
            so.OffloadError, "PACK_MANIFEST_MISMATCH"
        ):
            self.verify(current)
        self.assertTrue(out.is_dir())
        self.assertFalse(self.marker("cq-old").exists())

    def test_air_absent_cloud_only_arms_with_materialised_archive_and_no_ssd_probe(self):
        old = self.span("cq-old", 100)
        current = self.span("cq-current", 200)
        with mock.patch.object(so, "require_ssd_receipt") as receipt:
            result = self.verify(current)
        receipt.assert_not_called()
        self.assertIn("AIR FALLBACK (item 388)", result["air_fallback"])
        self.assertFalse(result["holds_next_arm"])
        self.assertFalse(old.exists())
        self.assertTrue(current.is_dir())
        retired = next(row for row in result["spans"] if row["plan"] == "cq-old")
        self.assertTrue(retired["original_deleted"])
        self.assertFalse(retired["archive_evicted"])
        self.assertEqual(so.sha256_file(self.archive("cq-old")), retired["ciphertext_sha256"])
        self.assertGreater((self.root / "cloud/cq-old" / so.names("cq-old")["ciphertext"]).stat().st_size, 0)

    def test_ssd_copy_and_reclaim_are_later_and_require_all_hashes(self):
        old = self.span("cq-old", 100)
        current = self.span("cq-current", 200)
        self.verify(current)
        ssd = self.root / "external-ssd"
        ssd.mkdir()
        record = so.read_record(self.marker("cq-old"))
        with mock.patch.object(so, "require_ssd_mount"):
            receipt = Path(so.ssd_copy({"backend": self.config["backend"]}, "cq-old", record, ssd))
        counterfeit = self.root / "bad.json"
        wrong = so.read_record(receipt)
        wrong["files"]["ciphertext"]["sha256"] = "0" * 64
        counterfeit.write_bytes(so.canonical(wrong))
        with self.assertRaises(so.OffloadError):
            self.verify(old, "--ssd-receipt", str(counterfeit), command="reclaim")
        self.assertTrue(self.archive("cq-old").is_file())
        result = self.verify(old, "--ssd-receipt", str(receipt), command="reclaim")
        self.assertTrue(result["spans"][0]["archive_evicted"])
        self.assertFalse(self.archive("cq-old").exists())
        self.assertEqual(so.sha256_file(receipt.with_name(so.names("cq-old")["ciphertext"])),
                         record["ciphertext"]["sha256"])

    def test_low_disk_mails_lead_without_evicting_the_only_local_archive(self):
        old = self.span("cq-old", 100)
        current = self.span("cq-current", 200)
        real = subprocess.run

        def fake_mail(argv, **kwargs):
            if argv[0] == "/usr/bin/mail":
                self.assertEqual(argv[-1], "lead@example.test")
                self.assertIn(b"free_bytes=60000000000", kwargs["input"])
                return subprocess.CompletedProcess(argv, 0)
            return real(argv, **kwargs)

        with mock.patch.object(so.shutil, "disk_usage", return_value=(10**12, 0, 60_000_000_000)), \
                mock.patch.object(so.subprocess, "run", side_effect=fake_mail) as ran:
            result = self.verify(current)
        self.assertTrue(any(call.args[0][0] == "/usr/bin/mail" for call in ran.call_args_list))
        self.assertTrue(all(row["storage_mail_sent"] for row in result["spans"]))
        self.assertFalse(old.exists())
        self.assertTrue(self.archive("cq-old").is_file())

    def test_f0_uses_same_gate_and_keeps_all_tied_newest_by_kind(self):
        campaign = self.span("cq-current", 100)
        older = self.span("r1-partc-f0-old", 100, kind="partc")
        tied = self.span("r1-partc-f0-tie", 200, kind="partc", tree="another")
        f0 = self.span("r1-partc-f0-checked", 200, kind="partc")
        result = self.verify(f0)
        self.assertEqual([row["plan"] for row in result["spans"]], ["r1-partc-f0-checked", "r1-partc-f0-old"])
        self.assertTrue(all(path.is_dir() for path in (campaign, f0, tied)))
        self.assertFalse(older.exists())
        self.assertTrue((older.parents[1] / ".git").is_file())
        self.assertTrue(self.marker("r1-partc-f0-checked").is_file())

    def test_pending_or_unknown_at_final_read_holds_even_after_good_markers(self):
        out = self.span("r1-partc-f0-check", 200, kind="partc")
        with mock.patch.object(so, "pending_transfers", return_value={"clear": False}), \
                self.assertRaisesRegex(so.OffloadError, "ICLOUD_PENDING"):
            self.verify(out)
        self.assertTrue(self.marker(out.name).is_file())
        self.assertTrue(out.is_dir())

    def test_unobserved_eviction_in_f0_holds_and_does_not_publish_ok(self):
        out = self.span("r1-partc-f0-check", 200, kind="partc")
        with mock.patch.dict(os.environ, {"FAKE_BRCTL_FAIL": "evict"}), self.assertRaises(so.OffloadError) as caught:
            self.verify(out)
        self.assertEqual(caught.exception.exit_kind, "unconfirmed")
        self.assertFalse(self.marker(out.name).exists())
        self.assertTrue(self.marker(out.name, False).is_file())
        self.assertTrue(out.is_dir())

    def test_census_and_lock_holds_are_before_provider_work(self):
        out = self.span("cq-current", 200)
        # Only path presence matters. Deliberately keep the fence opaque.
        self.fence.touch()
        response = self.cli(out)
        self.assertEqual(response.returncode, so.EXIT["refused"])
        self.assertEqual(json.loads(response.stdout)["status"], "DESK_FENCE_PRESENT")
        self.fence.unlink()
        for code, status in ((0, "RUNNER_PRESENT"), (2, "RUNNER_CENSUS_FAILED")):
            with mock.patch.dict(os.environ, {"FAKE_PGREP_RC": str(code)}):
                response = self.cli(out)
            self.assertEqual(response.returncode, so.EXIT["refused"])
            self.assertEqual(json.loads(response.stdout)["status"], status)
        with (self.fence.parent / ".desk-fence.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            response = self.cli(out)
        self.assertEqual(json.loads(response.stdout)["status"], "DESK_LOCK_BUSY")
        self.assertFalse((self.root / "provider/calls").exists())

    def test_deadline_reaps_provider_group_and_holds_with_no_marker(self):
        out = self.span("cq-current", 200)
        heartbeat = self.root / "heartbeat"
        pidfile = self.root / "provider.pid"
        child = (f"import time; from pathlib import Path; p=Path({str(heartbeat)!r});\n"
                 "while True: p.write_text(str(time.monotonic())); time.sleep(0.03)")
        self.exe("brctl", "import subprocess, sys, time\nfrom pathlib import Path\n"
                 f"p = subprocess.Popen([sys.executable, '-B', '-c', {child!r}, "
                 "'jw-close-offload-fixture-provider-child-v1'], stdin=subprocess.DEVNULL, "
                 "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
                 f"Path({str(pidfile)!r}).write_text(str(p.pid))\ntime.sleep(30)\n")
        try:
            response = self.cli(out, seconds=4)
            self.assertEqual(response.returncode, so.EXIT["unverified"], response.stdout + response.stderr)
            self.assertTrue(json.loads(response.stdout)["holds_next_arm"])
            self.assertTrue(pidfile.is_file(), "fake provider must actually have started a grandchild")
            time.sleep(0.1)
            stopped = heartbeat.read_bytes()
            time.sleep(0.2)
            self.assertEqual(heartbeat.read_bytes(), stopped)
            self.assertFalse(self.marker("cq-current").exists())
            self.assertTrue(out.is_dir())
        finally:
            if pidfile.exists():
                try:
                    os.kill(int(pidfile.read_text()), signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def interrupt_retirement(self, current, old):
        retiring = so.retirement_path(old)
        remove = shutil.rmtree

        def partial(path, *args, **kwargs):
            if path == retiring:
                (retiring / "runner_receipt.json").unlink()
                raise so.unverified("DEADLINE", "synthetic interruption")
            return remove(path, *args, **kwargs)

        with mock.patch.object(so.shutil, "rmtree", side_effect=partial), self.assertRaisesRegex(
            so.OffloadError, "DEADLINE"
        ):
            self.verify(current)
        self.assertFalse(old.exists())
        self.assertTrue(retiring.is_dir())
        self.assertTrue(self.archive("cq-old").is_file())
        return retiring

    def test_interrupted_retirement_resumes_after_receipt_is_gone(self):
        current, old = self.span("cq-current", 200), self.span("cq-old", 100)
        retiring = self.interrupt_retirement(current, old)
        self.assertEqual(self.verify(current)["status"], "CLOSE_OK")
        self.assertFalse(retiring.exists())

    def test_interrupted_retirement_preserves_unexpected_files(self):
        current, old = self.span("cq-current", 200), self.span("cq-old", 100)
        retiring = self.interrupt_retirement(current, old)
        unexpected = retiring / "unexpected"
        unexpected.write_bytes(b"new fixture bytes")
        with self.assertRaisesRegex(so.OffloadError, "RETIREMENT_CONFLICT"):
            self.verify(current)
        self.assertTrue(unexpected.is_file())

    def test_invalid_source_control_and_plan_collision_fail_closed(self):
        out = self.span("cq-current", 200)
        args = co.parser().parse_args(self.argv(out))
        args.config = out / "runner_receipt.json"
        with mock.patch.object(so, "load_mbp_config") as load, self.assertRaisesRegex(
            so.OffloadError, "PATH_OVERLAPS_SPAN"
        ):
            co.run(args)
        load.assert_not_called()
        self.span("cq-current", 100, tree="other")
        with self.assertRaisesRegex(so.OffloadError, "PLAN_COLLISION"):
            self.verify(out)
        self.assertFalse((self.root / "provider/calls").exists())

    def test_linked_partc_desk_is_not_followed(self):
        old = self.span("r1-partc-f0", 100, kind="partc")
        real_desk = old.parent
        saved = real_desk.with_name("saved")
        real_desk.rename(saved)
        real_desk.symlink_to(saved)
        with self.assertRaisesRegex(so.OffloadError, "CHECK_OUT_REQUIRED"):
            self.verify(old)
        self.assertTrue((saved / old.name / "runner_receipt.json").is_file())
