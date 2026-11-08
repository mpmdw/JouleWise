"""Closed synthetic files only; no machine probes, network or study data."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import file_hashes
from scripts import harvest_window
from scripts import run_night


class FinalizeHashesTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "night/evidence/nested").mkdir(parents=True)
        for name in ("night.log", "night/receipt.json", "night/chain.stdout.log",
                     "night/evidence/z", "night/evidence/nested/a"):
            (self.root / name).write_bytes((name.encode() + b"\0") * 100)

    @staticmethod
    def legacy_inventory(root):
        rows = {}
        for path in [root, *sorted(root.rglob("*"))]:
            st = path.lstat()
            row = dict(mode=st.st_mode, size=st.st_size, mtime_ns=st.st_mtime_ns)
            if path.is_symlink():
                row["link"] = os.readlink(path)
            elif path.is_file():
                row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            elif not path.is_dir():
                raise harvest_window.HarvestRefusal("unsupported evidence file type")
            rows[path.relative_to(root).as_posix()] = row
        return rows

    def test_manifest_bytes_equal_legacy_for_every_worker_count(self):
        (self.root / "literal-link").symlink_to("night/receipt.json")
        (self.root / "dangling-link").symlink_to("absent-synthetic-file")
        (self.root / "directory-link").symlink_to("night/evidence", target_is_directory=True)
        os.link(self.root / "night/receipt.json", self.root / "hard-link")
        expected = harvest_window.json_bytes(self.legacy_inventory(self.root))
        for workers in (1, 2, 4, 8):
            with self.subTest(workers=workers):
                self.assertEqual(expected, harvest_window.json_bytes(
                    harvest_window.inventory(self.root, workers=workers)))
                with file_hashes.hash_scope(workers):
                    actual = run_night._artifact_list(self.root, self.root / "night")
                for row in actual:
                    self.assertEqual(row["sha256"], hashlib.sha256(
                        (self.root / row["path"]).read_bytes()).hexdigest())
                if workers == 1:
                    reference = run_night._json_bytes(actual)
                else:
                    self.assertEqual(reference, run_night._json_bytes(actual))

    def test_incremental_hashes_once_and_invalidates_same_size_restored_mtime(self):
        path = self.root / "night/receipt.json"
        hashes = file_hashes.FileHashes(4)
        with mock.patch.object(file_hashes, "_stream_sha256", wraps=file_hashes._stream_sha256) as stream:
            first = harvest_window.inventory(self.root, hashes=hashes)
            count = stream.call_count
            self.assertEqual(first, harvest_window.inventory(self.root, hashes=hashes))
            self.assertEqual(count, stream.call_count)
            st = path.stat()
            path.write_bytes(b"!" * st.st_size)
            os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))
            changed = harvest_window.inventory(self.root, hashes=hashes)
            self.assertEqual(count + 1, stream.call_count)
            self.assertNotEqual(first["night/receipt.json"], changed["night/receipt.json"])
        # New operations must re-authenticate, even with identical metadata.
        with mock.patch.object(file_hashes, "_stream_sha256", wraps=file_hashes._stream_sha256) as stream:
            harvest_window.inventory(self.root)
            self.assertEqual(count, stream.call_count)

    def test_missing_and_corrupt_destination_never_use_source_cache(self):
        hashes = file_hashes.FileHashes(2)
        before = harvest_window.inventory(self.root, hashes=hashes)
        destination = self.root.parent / (self.root.name + "-copy")
        self.addCleanup(shutil.rmtree, destination, True)
        shutil.copytree(self.root, destination)
        self.assertTrue(harvest_window.copy_matches(before, harvest_window.inventory(destination)))
        path = destination / "night/receipt.json"
        st = path.stat()
        path.write_bytes(b"!" * st.st_size)
        os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))
        self.assertFalse(harvest_window.copy_matches(before, harvest_window.inventory(destination)))
        path.unlink()
        self.assertFalse(harvest_window.copy_matches(before, harvest_window.inventory(destination)))
        (self.root / "night/receipt.json").unlink()
        self.assertNotIn("night/receipt.json", harvest_window.inventory(self.root, hashes=hashes))

    def test_interrupted_hash_not_cached_or_published(self):
        hashes = file_hashes.FileHashes(4)
        with mock.patch.object(file_hashes, "_stream_sha256", side_effect=InterruptedError("synthetic")):
            with self.assertRaises(InterruptedError):
                harvest_window.inventory(self.root, hashes=hashes)
        self.assertEqual(self.legacy_inventory(self.root), harvest_window.inventory(self.root, hashes=hashes))
        self.assertFalse((self.root / "night/result.json").exists())

    def test_interruption_after_partial_stream_never_caches_digest(self):
        path = self.root / "partial.bin"
        path.write_bytes(b"s" * (file_hashes.CHUNK_BYTES * 2))
        hashes = file_hashes.FileHashes(1)
        opened = Path.open
        class InterruptedReader:
            def __init__(self, handle):
                self.handle, self.reads = handle, 0
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.handle.close()
            def fileno(self):
                return self.handle.fileno()
            def read(self, size):
                self.reads += 1
                if size != file_hashes.CHUNK_BYTES:
                    raise AssertionError("unbounded read")
                if self.reads == 2:
                    raise InterruptedError("synthetic partial read")
                return self.handle.read(size)
        with mock.patch.object(Path, "open", lambda p, *a, **kw: InterruptedReader(opened(p, *a, **kw))):
            with self.assertRaises(InterruptedError):
                hashes.sha256(path)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), hashes.sha256(path))

    def test_unsupported_files_refuse_in_sorted_order(self):
        os.mkfifo(self.root / "synthetic-fifo")
        for workers in (1, 2, 4, 8):
            with self.assertRaisesRegex(harvest_window.HarvestRefusal, "^unsupported evidence file type$"):
                harvest_window.inventory(self.root, workers=workers)

    def test_read_failure_entries_and_order_equal_across_workers(self):
        (self.root / "night/receipt.json").unlink()
        (self.root / "night/receipt.json").mkdir()
        for workers in (1, 2, 4, 8):
            with file_hashes.hash_scope(workers):
                actual = run_night._artifact_list(self.root, self.root / "night")
            receipt = next(row for row in actual if row["path"] == "night/receipt.json")
            self.assertEqual(receipt["error"], "IsADirectoryError")
            if workers == 1:
                reference = actual
            self.assertEqual(reference, actual)

    def test_mutation_or_replacement_during_hash_refuses_without_cache_entry(self):
        path = self.root / "night/receipt.json"
        original = file_hashes._stream_sha256
        hashes = file_hashes.FileHashes(2)
        def mutate(candidate, **kwargs):
            result = original(candidate, **kwargs)
            replacement = path.with_suffix(".new")
            replacement.write_bytes(path.read_bytes())
            replacement.replace(path)
            return result
        with mock.patch.object(file_hashes, "_stream_sha256", mutate):
            with self.assertRaises(OSError):
                hashes.sha256(path)
        self.assertEqual(original(path), hashes.sha256(path))

    def test_ordered_map_bounds_workers_and_reports_first_input_error(self):
        for workers in (1, 2, 4, 8):
            lock = threading.Lock()
            active = peak = 0
            def work(number):
                nonlocal active, peak
                with lock:
                    active += 1
                    peak = max(active, peak)
                try:
                    time.sleep(.002 if number else .01)
                    if number in (1, 2):
                        raise ValueError(str(number))
                    return number
                finally:
                    with lock:
                        active -= 1
            with self.assertRaisesRegex(ValueError, "^1$"):
                list(file_hashes.FileHashes(workers).map(work, range(100)))
            self.assertLessEqual(peak, workers)
            self.assertEqual(active, 0)

    def test_invalid_workers_refuse(self):
        for workers in (0, 3, 16, True):
            with self.assertRaises(ValueError):
                file_hashes.FileHashes(workers)

    def test_night_publish_reuses_closed_hashes_but_refreshes_courier_changes(self):
        plan = SimpleNamespace(plan_id="synthetic-close", receipt_class="DIAGNOSTIC_NO_PACK")
        calls, reads = [], []
        original = file_hashes._stream_sha256
        def stream(path, **kwargs):
            reads.append(path)
            return original(path, **kwargs)
        def git(argv, **kwargs):
            calls.append(argv)
            if argv[:4] == ["git", "clone", "--depth", "1"]:
                Path(argv[-1]).mkdir()
            return SimpleNamespace(stdout="synthetic-origin\n")
        with file_hashes.hash_scope(4), \
             mock.patch.object(file_hashes, "_stream_sha256", stream), \
             mock.patch.object(run_night.t0_rehearsal, "observed_run", git):
            before = run_night._artifact_list(self.root, self.root / "night")
            self.assertIsNone(run_night._durable_record(self.root, self.root / "night", plan))
            (self.root / "night/courier.sent").write_bytes(b"synthetic sent\n")
            self.assertIsNone(run_night._durable_record(self.root, self.root / "night", plan))
        evidence = self.root / "night/evidence/nested/a"
        self.assertEqual(reads.count(evidence), 1)
        self.assertEqual(reads.count(self.root / "night/receipt.json"), 1)
        self.assertEqual(reads.count(self.root / "night/courier.sent"), 1)
        destination = self.root / "results-clone/docs/process_traces/night-results/synthetic-close"
        self.assertEqual((destination / "evidence/nested/a").read_bytes(), evidence.read_bytes())
        self.assertEqual((destination / "courier.sent").read_bytes(), b"synthetic sent\n")
        self.assertFalse((destination / "chain.stdout.log").exists())
        self.assertEqual(sum("push" in call for call in calls), 2)
        self.assertEqual(before[0]["sha256"], hashlib.sha256((b"night.log\0") * 100).hexdigest())

    def test_gate_hash_reads_are_never_cached_by_terminal_scope(self):
        path = self.root / "night/receipt.json"
        with file_hashes.hash_scope(8), \
             mock.patch.object(run_night, "_stream_sha256", wraps=file_hashes._stream_sha256) as stream:
            self.assertEqual(run_night._sha256_path(path), run_night._sha256_path(path))
            self.assertEqual(stream.call_count, 2)

    def test_cli_scopes_cache_for_terminal_dispatch_and_releases_it(self):
        for command, callee in (("run", "run_night"), ("rehearse", "run_night"), ("dead-man", "dead_man")):
            for workers in (1, 2, 4, 8):
                def dispatch(*args, **kwargs):
                    self.assertEqual(file_hashes.current_hashes().workers, workers)
                    run_night._artifact_list(self.root, self.root / "night")
                    run_night._artifact_list(self.root, self.root / "night")
                    return 0
                with mock.patch.object(run_night, callee, dispatch), \
                     mock.patch.object(file_hashes, "_stream_sha256", wraps=file_hashes._stream_sha256) as stream:
                    self.assertEqual(run_night._main([command, "--plan", "synthetic.json",
                                                     "--hash-workers", str(workers)]), 0)
                    self.assertEqual(stream.call_count, 5)
                self.assertEqual(file_hashes.current_hashes()._cache, {})


if __name__ == "__main__":
    unittest.main()
