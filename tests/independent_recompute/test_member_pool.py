"""--workers: the member pool's output bytes equal the serial run's (synthetic windows only).

The always-on tests build three small synthetic windows (support.full_pack) with planted member faults, so
flags are raised inside members and must replay in the serial order. The full-size class runs on the committed
S10 synthetic window (fullsize_window), which extracts about 1.2 GB; it runs only when
JW_B5_FULLSIZE_RECOMPUTE=1 (JW_B5_FULLSIZE_DIR names a reusable extraction folder).
"""
import contextlib
import io
import json
import multiprocessing
import multiprocessing.connection
import os
from pathlib import Path
import subprocess
import signal
import sys
import tempfile
import threading
import unittest
from unittest import mock

from . import fullsize_window
from .support import ROOT, SCRIPT, bundle, full_pack, recompute, remove_member


def run_subprocess(args, out, workers):
    command = [sys.executable, "-B", str(SCRIPT), *args, "--out", str(out)]
    if workers is not None:
        command += ["--workers", str(workers)]
    result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
    return result.returncode, out.read_bytes() if out.exists() else None, result.stdout, result.stderr


def build_windows(parent):
    archives = {pack: full_pack(parent, pack) for pack in ("ALPHA", "BETA", "GAMMA")}
    claim = {pack: archive / "sources/claim-runs" for pack, archive in archives.items()}
    # Planted member faults: each raises its flag inside Member.__init__ (in a worker under the pool).
    (claim["ALPHA"] / "fixture-decode-r03/raw/powermetrics.plist").unlink()                    # trace_plist_missing
    (claim["ALPHA"] / "fixture-decode-b02-b1/raw/powermetrics.plist").write_bytes(b"<plist")   # trace_plist_unreadable
    summary = claim["BETA"] / "fixture-prefill-p2048-r04/summary_metrics.json"
    data = json.loads(summary.read_text())
    data["phase_energy_j"]["prefill"] += 1.0                                                    # stored_energy_mismatch
    summary.write_text(json.dumps(data))
    (claim["GAMMA"] / "fixture-decode-b05-a2/power_trace.csv").write_text("bad\n")            # archive_file_missing
    remove_member(archives["BETA"], "fixture-decode-b03-a2")
    return [arg for pack, archive in archives.items() for arg in ("--" + pack.lower(), str(archive))]


class MemberPoolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.args = build_windows(cls.root) + ["--member-detail"]
        cls.serial = run_subprocess(cls.args, cls.root / "serial.json", 1)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_serial_run_raises_the_planted_flags(self):
        code, data, _, _ = self.serial
        self.assertEqual(code, 0)
        flags = {f["code"] for f in json.loads(data)["flags"]}
        for planted in ("trace_plist_missing", "trace_plist_unreadable", "stored_energy_mismatch", "archive_file_missing"):
            self.assertIn(planted, flags)

    def test_bytes_and_public_line_identical_across_worker_counts_1_3_10(self):
        code, data, stdout, stderr = self.serial
        for workers in (3, 10):
            with self.subTest(workers=workers):
                result = run_subprocess(self.args, self.root / f"w{workers}.json", workers)
                self.assertEqual(result, (code, data, stdout, stderr))

    def test_default_is_ten_workers_and_identical(self):
        self.assertEqual(run_subprocess(self.args, self.root / "default.json", None), self.serial)

    def test_pool_runs_when_the_script_is_loaded_by_file_path(self):
        # support loads the script with spec_from_file_location (no importable module name): the fork pool
        # pickles no code, so it still runs, and the bytes equal the serial subprocess's.
        out = self.root / "in-process.json"
        with contextlib.redirect_stdout(io.StringIO()) as stdout, \
                mock.patch.object(recompute.MemberPool, "_start", autospec=True,
                                  side_effect=recompute.MemberPool._start) as started:
            code = recompute.main([*self.args, "--workers", "3", "--out", str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(started.call_count, 1)
        self.assertEqual(out.read_bytes(), self.serial[1])
        self.assertEqual(stdout.getvalue(), self.serial[2])

    def test_every_member_comes_from_the_pool(self):
        built = []
        original = recompute.Member.__init__

        def counting(member, *args, **kwargs):
            built.append(args[0])
            return original(member, *args, **kwargs)
        out = self.root / "counted.json"
        with mock.patch.object(recompute.Member, "__init__", counting), contextlib.redirect_stdout(io.StringIO()):
            # The workers are forked after the patch, so their builds are not counted here: only in-process
            # fallbacks are. Every member the run uses was prefetched under the key it is asked for.
            self.assertEqual(recompute.main([*self.args, "--workers", "3", "--out", str(out)]), 0)
        self.assertEqual(built, [])
        self.assertEqual(out.read_bytes(), self.serial[1])

    def test_a_member_error_surfaces_as_in_the_serial_run(self):
        original = recompute.Member.__init__

        def failing(member, path, run_id, *args, **kwargs):
            if run_id == "fixture-prefill-p2048-b04-a1":
                raise ZeroDivisionError("planted")
            return original(member, path, run_id, *args, **kwargs)
        results = []
        for workers in ("1", "3"):
            stderr = io.StringIO()
            with mock.patch.object(recompute.Member, "__init__", failing), contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(stderr):
                code = recompute.guarded_main([*self.args, "--workers", workers, "--out", str(self.root / "x.json")])
            results.append((code, stderr.getvalue()))
        self.assertEqual(results[0], (2, "error: internal ZeroDivisionError\n"))
        self.assertEqual(results[1], results[0])

    def test_take_without_prefetch_builds_in_process(self):
        pool = recompute.MemberPool(2)
        self.addCleanup(pool.close)
        self.assertIsNone(pool.take("ALPHA", self.root, "x", .045, "science"))
        self.assertIsNone(pool.procs)

    def test_worker_killed_during_a_large_reply_refuses_instead_of_hanging(self):
        claim = self.root / "dead-worker"
        path = bundle(claim, "big-r01")
        metadata = json.loads((path / "metadata.json").read_text())
        metadata["padding"] = "x" * (8 << 20)   # unused by the recompute; makes the reply far larger than a pipe
        (path / "metadata.json").write_text(json.dumps(metadata))
        pool = recompute.MemberPool(2)
        self.addCleanup(pool.close)
        previous = signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("pool hung")))
        self.addCleanup(signal.signal, signal.SIGALRM, previous)
        signal.alarm(120)
        self.addCleanup(signal.alarm, 0)
        pool.prefetch("ALPHA", claim, "big-r01", .045, "science")
        busy = pool.result_readers[pool.busy.index(next(k for k in pool.busy if k is not None))]
        self.assertTrue(multiprocessing.connection.wait([busy], 100))   # the reply has started to arrive
        for process in pool.procs:
            os.kill(process.pid, signal.SIGKILL)
            process.join()
        with self.assertRaisesRegex(RuntimeError, "member pool worker exited"):
            pool.take("ALPHA", claim, "big-r01", .045, "science")

    def test_close_leaves_no_thread_or_child_with_a_backlog(self):
        threads = threading.active_count()
        for _ in range(3):
            pool = recompute.MemberPool(3)
            for i in range(200):
                pool.prefetch("ALPHA", self.root / "nowhere", f"missing-r{i:03}", .045, "science")
            pool.close()
            self.assertEqual(multiprocessing.active_children(), [])
            self.assertEqual(threading.active_count(), threads)

    def test_workers_leave_the_parents_atexit_held_temporary_directories_alone(self):
        # CI shard 11 on PR #688: a TemporaryDirectory kept alive only by atexit (tests/b5_analysis/fixtures_s8)
        # was freed in each forked worker, whose finalizer then deleted the parent's live tree.
        import atexit
        import gc
        held = tempfile.TemporaryDirectory(prefix="pool-atexit-held-", dir=self.root)
        atexit.register(held.cleanup)
        (Path(held.name) / "live.txt").write_text("kept")
        name = held.name
        del held
        gc.collect()
        pool = recompute.MemberPool(3)
        try:
            for i in range(6):
                pool.prefetch("ALPHA", self.root / "nowhere", f"missing-r{i:03}", .045, "science")
            for i in range(6):
                pool.take("ALPHA", self.root / "nowhere", f"missing-r{i:03}", .045, "science")
        finally:
            pool.close()
        self.assertTrue((Path(name) / "live.txt").is_file())

    def test_workers_must_be_positive(self):
        for value in ("0", "-1", "x"):
            with self.subTest(value=value), contextlib.redirect_stderr(io.StringIO()), \
                    self.assertRaises(SystemExit):
                recompute.main([*self.args, "--workers", value, "--out", str(self.root / "bad.json")])


@unittest.skipUnless(os.environ.get("JW_B5_FULLSIZE_RECOMPUTE") == "1" and fullsize_window.available(),
                     "full-size synthetic window: set JW_B5_FULLSIZE_RECOMPUTE=1 (extracts about 1.2 GB)")
class FullSizeMemberPoolTests(unittest.TestCase):
    """The committed S10 synthetic window (316 compared runs): serial, 3 and 10 workers give the same bytes."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        folder = os.environ.get("JW_B5_FULLSIZE_DIR") or str(cls.root / "window")
        cls.args = fullsize_window.extract(folder) + ["--member-detail"]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_full_size_bytes_identical_across_worker_counts_1_3_10(self):
        results = {w: run_subprocess(self.args, self.root / f"w{w}.json", w) for w in (1, 3, 10)}
        code, data, stdout, _ = results[1]
        self.assertEqual(code, 0)
        self.assertGreater(len(json.loads(data)["members"]["ALPHA"]), 100)
        for workers in (3, 10):
            with self.subTest(workers=workers):
                self.assertEqual(results[workers][:3], (code, data, stdout))


if __name__ == "__main__":
    unittest.main()
