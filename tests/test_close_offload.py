"""Synthetic byte trees only. No real iCloud, runner, or remote host."""
from __future__ import annotations

from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from joulewise import close_offload as co

try:
    from compression import zstd
except ImportError:
    zstd = None

REPO = Path(__file__).resolve().parents[1]


class OffloadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.cloud = self.root / "cloud"
        self.cloud.mkdir()
        self.control = self.root / "provider.json"
        self.control.write_text(json.dumps({"pending": 0, "evictions": []}))
        self.exe("pgrep", "import os,sys\nsys.exit(int(os.environ.get('FAKE_RUNNER_RC','1')))\n")
        self.exe("stat", """import json,os,sys
from pathlib import Path
p=Path(sys.argv[-1]); s=json.loads(Path(os.environ['FAKE_PROVIDER']).read_text())
if str(p) in s.get('evictions',[]): print('dataless')
else: print('-')
""")
        self.exe("brctl", """import json,os,sys,time
from pathlib import Path
state=Path(os.environ['FAKE_PROVIDER']); s=json.loads(state.read_text())
if sys.argv[1]=='download': sys.exit(0)
if sys.argv[1]=='status': print('needs-upload' if s.get('pending') else 'caught-up'); sys.exit(0)
if s.get('hang'): time.sleep(30)
if s.get('error'): print('NSFileProviderErrorDomain -9999',file=sys.stderr); sys.exit(1)
if s.get('pending'):
 s['pending']-=1; state.write_text(json.dumps(s))
 print('NSFileProviderErrorDomain -2008',file=sys.stderr); sys.exit(1)
if s.get('size_change'):
 p=Path(sys.argv[-1]); p.write_bytes(p.read_bytes()+b'x')
if not s.get('not_dataless') and sys.argv[-1] not in s['evictions']: s['evictions'].append(sys.argv[-1])
state.write_text(json.dumps(s))
""")
        env = {"PATH": str(self.bin) + os.pathsep + os.environ["PATH"], "FAKE_PROVIDER": str(self.control)}
        self.env = mock.patch.dict(os.environ, env)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.config = co.Config(deadline=time.time() + 30, campaign_root=self.root / "campaign",
                                work_root=self.root / "work", cloud_root=self.cloud,
                                state_root=self.root / "state", marker_root=self.root / "markers",
                                fence=self.root / "custody/desk_fence.json", air_root=self.root / "ssd",
                                poll_seconds=0.01)
        self.config.campaign_root.mkdir()
        self.config.work_root.mkdir()
        self.old = self.span("campaign", "cq-example-a1-20261116T010000Z", 100)
        self.new = self.span("campaign", "cq-example-a1-20261116T020000Z", 200)

    def exe(self, name, code):
        path = self.bin / name
        path.write_text("#!" + sys.executable + "\n" + code)
        path.chmod(0o755)

    def span(self, kind, name, stamp, kit="kit"):
        path = (self.config.campaign_root / kit / name if kind == "campaign"
                else self.config.work_root / kit / ".desk" / name)
        path.mkdir(parents=True)
        # Deliberately invalid JSON: the runner receipt and all journal files are opaque.
        (path / "runner_receipt.json").write_bytes(b'NOT JSON\xff\x00')
        (path / "nested").mkdir()
        (path / "nested/raw").write_bytes(b"SENSITIVE-DO-NOT-PRINT\x00\xff" * 5000)
        (path / "empty").mkdir()
        (path / "link").symlink_to("nested/raw")
        os.utime(path / "runner_receipt.json", (stamp, stamp))
        return path

    def provider(self, **kwargs):
        state = json.loads(self.control.read_text())
        state.update(kwargs)
        self.control.write_text(json.dumps(state))

    def pending_run(self):
        # Reach a real fake-provider poll, then advance the deadline deterministically.
        # Packing speed and host test contention cannot change which phase expires.
        with mock.patch.object(co.time, "sleep", side_effect=co.OutOfTime("DEADLINE")):
            return co.run(self.config)

    def record(self, path=None):
        return json.loads(co.record_path(self.config, path or self.old).read_text())

    def cli(self, deadline=5, *extra):
        args = [sys.executable, "-B", str(REPO / "scripts/close_offload.py"),
                "--deadline", str(time.time() + deadline)]
        for name in ("campaign_root", "work_root", "cloud_root", "state_root", "marker_root", "fence", "air_root"):
            args.extend(["--" + name.replace("_", "-"), str(getattr(self.config, name))])
        return subprocess.run([*args, "--poll-seconds", "0.01", *extra], capture_output=True, text=True, timeout=10)

    def test_newest_by_receipt_mtime_in_each_kind_and_ties_stay(self):
        older = self.span("partc", "r1-partc-f0-old", 250)
        latest = self.span("partc", "r1-partc-latest", 300)
        tied = self.span("partc", "r1-partc-tie", 300, kit="other-tree")
        selected = co.candidates(self.config, co.Guard(self.config))
        self.assertEqual({p for _, p, _ in selected}, {self.old, older})
        self.assertTrue(latest.exists() and tied.exists())

    def test_normal_rotates_previous_close_catch_up_includes_backlog(self):
        oldest = self.span("campaign", "cq-first-a1-20261115T010000Z", 50)
        guard = co.Guard(self.config)
        self.assertEqual([p for _, p, _ in co.candidates(self.config, guard)], [self.old])
        self.assertEqual([p for _, p, _ in co.candidates(replace(self.config, catch_up=True), guard)], [oldest, self.old])

    def test_no_marker_with_opt_out_preserves_original(self):
        code, result = co.run(replace(self.config, cloud_only_allowed=False))
        self.assertEqual(code, co.VERIFY_FAILED)
        self.assertEqual(result["status"], "AIR_COPY_REQUIRED")
        self.assertTrue(result["holds_next_arm"])
        self.assertTrue(self.old.exists())
        self.assertFalse(list(self.cloud.rglob("*.tar.zst")))

    def test_fence_even_dangling_symlink_stops_before_writes(self):
        self.config.fence.parent.mkdir()
        self.config.fence.symlink_to(self.root / "absent")
        code, result = co.run(self.config)
        self.assertEqual((code, result["status"]), (co.BUSY, "DESK_FENCE_PRESENT"))
        self.assertFalse(self.config.state_root.exists())

    def test_runner_and_census_error_hold(self):
        for rc in (0, 2):
            with self.subTest(rc=rc), mock.patch.dict(os.environ, {"FAKE_RUNNER_RC": str(rc)}):
                code, result = co.run(self.config)
                self.assertEqual(code, co.BUSY)
                self.assertTrue(result["holds_next_arm"])
        self.assertFalse(self.config.state_root.exists())

    def test_expired_and_nonfinite_deadline(self):
        self.assertEqual(co.run(replace(self.config, deadline=time.time() - 1))[0], co.DEADLINE)
        p = subprocess.run([sys.executable, str(REPO / "scripts/close_offload.py"), "--deadline", "nan"], capture_output=True)
        self.assertEqual(p.returncode, 2)

    def test_shared_launch_lock_refuses_another_close(self):
        self.config.fence.parent.mkdir()
        with (self.config.fence.parent / ".desk-fence.lock").open("w") as handle:
            co.fcntl.flock(handle, co.fcntl.LOCK_EX | co.fcntl.LOCK_NB)
            self.assertEqual(co.run(self.config)[0], co.BUSY)

    def test_missing_root_fail_closed(self):
        self.config.work_root.rmdir()
        self.assertEqual(co.run(self.config)[0], co.VERIFY_FAILED)

    def test_dataless_uses_flags_never_sparse_size(self):
        self.assertFalse(co.dataless(self.old / "runner_receipt.json", co.Guard(self.config)))

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_complete_bytes_roundtrip_provider_receipt_and_newest_kept(self):
        expected = co.manifest(self.old, co.Guard(self.config))
        latest_mtime = (self.new / "runner_receipt.json").stat().st_mtime_ns
        self.provider(pending=2)
        code, result = co.run(self.config)
        self.assertEqual((code, result["completed"]), (co.OK, 1), result)
        self.assertFalse(self.old.exists())
        self.assertEqual((self.new / "runner_receipt.json").stat().st_mtime_ns, latest_mtime)
        record = self.record()
        self.assertEqual(record["state"], "COMPLETE")
        self.assertEqual(record["copy_basis"], "cloud-only")
        self.assertEqual(record["manifest_sha256"], co.digest(expected))
        self.assertEqual(set(record["provider"]), {"archive", "receipt"})
        self.assertFalse((self.config.marker_root / "cq-example-a1.ok").exists())
        config = replace(self.config, air_pull="campaign/" + self.old.name, receipt_sha256=record["receipt_sha256"])
        code, result = co.run(config)
        self.assertEqual(code, co.OK, result)
        self.assertEqual(co.manifest(config.air_root / "campaign" / self.old.name, co.Guard(config)), expected)

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_air_marker_copy_basis_and_marker_preserved(self):
        self.config.marker_root.mkdir()
        marker = self.config.marker_root / "cq-example-a1.air.ok"
        marker.write_bytes(b"existing-Air-proof")
        normal = self.config.marker_root / "cq-example-a1.ok"
        normal.write_bytes(b"existing-proof")
        code, result = co.run(replace(self.config, cloud_only_allowed=False))
        self.assertEqual(code, co.OK, result)
        self.assertEqual(self.record()["copy_basis"], "prior-copy-marker-and-cloud")
        self.assertEqual(normal.read_bytes(), b"existing-proof")

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_upload_pending_distinct_nonholding_and_resumes(self):
        self.provider(pending=1000)
        code, result = self.pending_run()
        self.assertEqual(code, co.UPLOAD_PENDING, result)
        self.assertFalse(result["holds_next_arm"])
        self.assertTrue(self.old.exists())
        self.assertEqual(self.record()["state"], "UPLOAD_PENDING")
        self.assertTrue(Path(self.record()["archive"]).exists())
        self.assertFalse(self.config.marker_root.exists())
        self.provider(pending=0)
        self.assertEqual(co.run(self.config)[0], co.OK)
        self.assertFalse(self.old.exists())

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_provider_failure_or_wrong_size_preserves_source_and_holds_f0(self):
        for setting in ("error", "size_change"):
            with self.subTest(setting=setting):
                self.provider(**{setting: True})
                code, result = co.run(self.config)
                self.assertEqual(code, co.VERIFY_FAILED, result)
                self.assertTrue(result["holds_next_arm"])
                self.assertTrue(self.old.exists())
                self.provider(**{setting: False})

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_rc_zero_without_dataless_is_still_pending(self):
        self.provider(not_dataless=True)
        code, result = self.pending_run()
        self.assertEqual(code, co.UPLOAD_PENDING, result)
        self.assertTrue(self.old.exists())

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_archive_hash_mismatch_on_resume_holds_and_keeps_original(self):
        self.provider(pending=1000)
        self.assertEqual(self.pending_run()[0], co.UPLOAD_PENDING)
        archive = Path(self.record()["archive"])
        archive.write_bytes(b"corrupted")
        self.provider(pending=0)
        code, result = co.run(self.config)
        self.assertEqual((code, result["status"]), (co.VERIFY_FAILED, "CLOUD_HASH_MISMATCH"))
        self.assertTrue(self.old.exists())

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_stream_reread_detects_changed_bytes(self):
        guard = co.Guard(self.config)
        entries = co.manifest(self.old, guard)
        (self.old / "nested/raw").write_bytes(b"X" * entries["nested/raw"]["size"])
        with self.assertRaisesRegex(co.Refusal, "ARCHIVE_MANIFEST_MISMATCH"):
            co.pack(self.old, self.root / "test.tar.zst", entries, guard)
        self.assertTrue(self.old.exists())

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_source_mutation_after_upload_does_not_delete(self):
        real = co.provider_evict
        def mutate(path, size, guard):
            evidence = real(path, size, guard)
            (self.old / "late-journal").write_bytes(b"still-writing")
            return evidence
        with mock.patch.object(co, "provider_evict", side_effect=mutate):
            code, result = co.run(self.config)
        self.assertEqual((code, result["status"]), (co.VERIFY_FAILED, "SOURCE_CHANGED"))
        self.assertTrue(self.old.exists())

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_runner_appearing_before_delete_preserves_original(self):
        real = co.provider_evict
        def runner(path, size, guard):
            evidence = real(path, size, guard)
            os.environ["FAKE_RUNNER_RC"] = "0"
            return evidence
        with mock.patch.object(co, "provider_evict", side_effect=runner):
            code, result = co.run(self.config)
        os.environ.pop("FAKE_RUNNER_RC", None)
        self.assertEqual(code, co.BUSY, result)
        self.assertTrue(self.old.exists())

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_cli_no_content_leak_and_idempotent_second_run(self):
        first = self.cli()
        self.assertEqual(first.returncode, co.OK, first.stdout + first.stderr)
        self.assertNotIn("SENSITIVE", first.stdout + first.stderr)
        self.assertEqual(self.cli().returncode, co.OK)

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_hard_deadline_kills_hanging_provider_and_leaves_original(self):
        self.provider(hang=True)
        start = time.monotonic()
        result = self.cli(0.9)
        self.assertIn(result.returncode, (co.UPLOAD_PENDING, co.DEADLINE), result.stdout + result.stderr)
        self.assertLess(time.monotonic() - start, 2.5)
        self.assertTrue(self.old.exists())

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_interrupted_deletion_resumes_without_receipt(self):
        real = co.remove_original
        def interrupted(source, guard):
            (source / "runner_receipt.json").unlink()
            raise co.OutOfTime("DEADLINE")
        with mock.patch.object(co, "remove_original", side_effect=interrupted):
            self.assertEqual(co.run(self.config)[0], co.DEADLINE)
        self.assertEqual(self.record()["state"], "DELETING")
        self.assertEqual(co.run(self.config)[0], co.OK)
        self.assertFalse(self.old.exists())

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_interrupted_deletion_rejects_new_unverified_files(self):
        def interrupted(source, guard):
            (source / "runner_receipt.json").unlink()
            raise co.OutOfTime("DEADLINE")
        with mock.patch.object(co, "remove_original", side_effect=interrupted):
            self.assertEqual(co.run(self.config)[0], co.DEADLINE)
        (self.old / "new-evidence").write_bytes(b"preserve me")
        code, result = co.run(self.config)
        self.assertEqual((code, result["status"]), (co.VERIFY_FAILED, "SOURCE_CHANGED_DURING_DELETE"))
        self.assertTrue((self.old / "new-evidence").exists())

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_air_pull_requires_independent_receipt_digest(self):
        code, result = co.run(replace(self.config, air_pull="campaign/" + self.old.name))
        self.assertEqual((code, result["status"]), (co.VERIFY_FAILED, "AIR_PULL_REQUIRES_MARKER_RECEIPT_SHA256"))

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_cloud_only_completion_never_satisfies_air_opt_out_for_later_source(self):
        self.assertEqual(co.run(self.config)[0], co.OK)
        self.span("campaign", "cq-example-a1-20261116T030000Z", 300)
        code, result = co.run(replace(self.config, cloud_only_allowed=False))
        self.assertEqual((code, result["status"]), (co.VERIFY_FAILED, "AIR_COPY_REQUIRED"))
        self.assertTrue(self.new.exists())
        self.assertFalse(co.record_path(self.config, self.new).exists())

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_noncanonical_symlink_refuses_before_any_original_is_removed(self):
        (self.old / "link").unlink()
        (self.old / "link").symlink_to("nested/../nested/raw")
        code, result = co.run(self.config)
        self.assertEqual((code, result["status"]), (co.VERIFY_FAILED, "NONCANONICAL_SYMLINK"))
        self.assertTrue(self.old.exists())
        self.assertFalse(list(self.cloud.rglob("*.tar.zst")))

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_symlink_cycle_refuses_before_delete(self):
        (self.old / "a").symlink_to("b")
        (self.old / "b").symlink_to("a")
        code, result = co.run(self.config)
        self.assertEqual((code, result["status"]), (co.VERIFY_FAILED, "UNRESOLVED_SYMLINK"))
        self.assertTrue(self.old.exists())

    @unittest.skipUnless(zstd, "stdlib zstd needs Python 3.14")
    def test_deadline_cleans_provider_grandchild_after_normal_worker_exit(self):
        heartbeat = self.root / "heartbeat"
        pid_file = self.root / "provider-child.pid"
        child_code = ("import time; from pathlib import Path; p=Path(" + repr(str(heartbeat))
                      + ");\nwhile True: p.write_text(str(time.monotonic())); time.sleep(0.03)")
        self.exe("brctl", "import subprocess,sys,time; from pathlib import Path; "
                 + "child=subprocess.Popen([sys.executable,'-B','-c'," + repr(child_code) + "], "
                 + "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); "
                 + "Path(" + repr(str(pid_file)) + ").write_text(str(child.pid)); time.sleep(30)\n")
        try:
            result = self.cli(2.0)
            self.assertIn(result.returncode, (co.UPLOAD_PENDING, co.DEADLINE), result.stdout + result.stderr)
            self.assertTrue(pid_file.exists(), "probe must actually launch the grandchild")
            time.sleep(0.1)
            stopped = heartbeat.read_bytes()
            time.sleep(0.2)
            self.assertEqual(heartbeat.read_bytes(), stopped, "provider work survived CLI exit")
            self.assertTrue(self.old.exists())
        finally:
            if pid_file.exists():
                try:
                    os.kill(int(pid_file.read_text()), co.signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_special_and_escaping_links_refused(self):
        (self.old / "link").unlink()
        (self.old / "link").symlink_to("../outside")
        with self.assertRaises(co.Refusal):
            co.manifest(self.old, co.Guard(self.config))


if __name__ == "__main__":
    unittest.main()
