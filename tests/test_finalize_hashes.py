"""Closed synthetic files only; no machine probes, network or study data."""
from __future__ import annotations

import hashlib
import ctypes
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

    @mock.patch.object(file_hashes.FileHashes, "_can_reuse", return_value=True)
    def test_incremental_hashes_once_and_invalidates_same_size_restored_mtime(self, _reuse):
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
        with mock.patch.object(file_hashes, "_stream_sha256", side_effect=mutate) as stream, \
             mock.patch.object(file_hashes.time, "sleep") as sleep:
            with self.assertRaisesRegex(OSError, f"file changed while hashing: {path}"):
                hashes.sha256(path)
        self.assertEqual(stream.call_count, 4)
        self.assertEqual(sleep.call_args_list, [mock.call(.01), mock.call(.02), mock.call(.03)])
        self.assertNotIn(path, hashes._cache)
        self.assertEqual(original(path), hashes.sha256(path))

    def test_transient_changes_retry_with_fresh_identity_and_digest(self):
        path = self.root / "night/receipt.json"
        original = file_hashes._stream_sha256
        for changes in (1, 2, 3):
            with self.subTest(changes=changes):
                hashes = file_hashes.FileHashes()
                reads = 0
                def mutate(candidate, **kwargs):
                    nonlocal reads
                    digest = original(candidate, **kwargs)
                    reads += 1
                    if reads <= changes:
                        candidate.write_bytes(bytes([reads]) * candidate.stat().st_size)
                    return digest
                with mock.patch.object(file_hashes, "_stream_sha256", side_effect=mutate), \
                     mock.patch.object(file_hashes.time, "sleep") as sleep:
                    digest = hashes.sha256(path)
                self.assertEqual(reads, changes + 1)
                self.assertEqual(sleep.call_count, changes)
                self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_open_and_postread_identity_changes_retry_for_uncached_gate(self):
        path = self.root / "night/receipt.json"
        original = file_hashes._read_sha256
        for phase in ("before_open", "after_read"):
            with self.subTest(phase=phase):
                reads = 0
                def mutate(candidate, **kwargs):
                    nonlocal reads
                    reads += 1
                    if phase == "before_open" and reads == 1:
                        candidate.write_bytes(b"open race")
                    digest = original(candidate, **kwargs)
                    if phase == "after_read" and reads == 1:
                        candidate.write_bytes(b"post read race")
                    return digest
                with mock.patch.object(file_hashes, "_read_sha256", side_effect=mutate), \
                     mock.patch.object(file_hashes.time, "sleep") as sleep:
                    digest = run_night._sha256_path(path)
                self.assertEqual(reads, 2)
                self.assertEqual(sleep.call_count, 1)
                self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_read_errors_and_interrupts_never_retry(self):
        path = self.root / "night/receipt.json"
        for error in (PermissionError("synthetic"), FileNotFoundError("synthetic"),
                      InterruptedError("synthetic"), KeyboardInterrupt()):
            with self.subTest(error=type(error).__name__), \
                 mock.patch.object(file_hashes, "_read_sha256", side_effect=error) as stream, \
                 mock.patch.object(file_hashes.time, "sleep") as sleep:
                hashes = file_hashes.FileHashes()
                with self.assertRaises(type(error)):
                    hashes.sha256(path)
                self.assertEqual(stream.call_count, 1)
                sleep.assert_not_called()
                self.assertNotIn(path, hashes._cache)

    def test_unstable_artifact_names_file_and_omits_digest(self):
        path = self.root / "night/receipt.json"
        error = file_hashes._FileChanged(f"file changed while hashing: {path}")
        with mock.patch.object(file_hashes, "_read_sha256", side_effect=error), \
             mock.patch.object(file_hashes.time, "sleep"):
            row = run_night._artifact_entry(self.root, path)
        self.assertEqual(row["path"], "night/receipt.json")
        self.assertIsNone(row["sha256"])
        self.assertEqual(row["error"], "OSError")

    def test_fstat_change_during_read_is_retried(self):
        path = self.root / "night/receipt.json"
        fstat = os.fstat
        calls = 0
        def mutate(descriptor):
            nonlocal calls
            calls += 1
            if calls == 2:
                path.write_bytes(b"changed during read")
            return fstat(descriptor)
        with mock.patch.object(file_hashes.os, "fstat", side_effect=mutate), \
             mock.patch.object(file_hashes.time, "sleep") as sleep:
            digest = file_hashes.FileHashes().sha256(path)
        self.assertEqual(calls, 4)
        sleep.assert_called_once_with(.01)
        self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_filesystem_detection_is_apfs_only_and_fails_closed(self):
        path = self.root / "night/receipt.json"
        for filesystem in (b"apfs", b"hfs", b"exfat", b"nfs", b"", b"\xff"):
            def statfs(raw_path, info):
                self.assertEqual(raw_path, os.fsencode(path))
                info._obj.fstypename = filesystem
                return 0
            with self.subTest(filesystem=filesystem), \
                 mock.patch.object(file_hashes.sys, "platform", "darwin"), \
                 mock.patch.object(ctypes, "CDLL") as library:
                library.return_value.statfs.side_effect = statfs
                expected = filesystem.decode("ascii") if filesystem != b"\xff" else None
                self.assertEqual(file_hashes._filesystem_type(path), expected)
        for failure in ("statfs_error", "load_error", "missing_symbol", "non_darwin"):
            with self.subTest(failure=failure), \
                 mock.patch.object(file_hashes.sys, "platform", "linux" if failure == "non_darwin" else "darwin"), \
                 mock.patch.object(ctypes, "CDLL") as library:
                library.return_value.statfs.return_value = -1
                if failure == "load_error":
                    library.side_effect = OSError("synthetic")
                elif failure == "missing_symbol":
                    del library.return_value.statfs
                self.assertIsNone(file_hashes._filesystem_type(path))
                if failure == "non_darwin":
                    library.assert_not_called()

    def test_non_apfs_and_coarse_apfs_never_reuse_same_identity_rewrite(self):
        path = self.root / "night/receipt.json"
        identity = file_hashes._identity
        def coarse(st):
            values = identity(st)
            return (*values[:-2], 1_000_000_000, 1_000_000_000)
        for filesystem in ("apfs", "hfs", "exfat", "nfs", None):
            with self.subTest(filesystem=filesystem), \
                 mock.patch.object(file_hashes, "_filesystem_type", return_value=filesystem), \
                 mock.patch.object(file_hashes, "_identity", side_effect=coarse), \
                 mock.patch.object(file_hashes, "_stream_sha256", wraps=file_hashes._stream_sha256) as stream:
                hashes = file_hashes.FileHashes()
                path.write_bytes(b"first")
                before = file_hashes._fingerprint(path)
                first = hashes.sha256(path)
                path.write_bytes(b"other")
                self.assertEqual(before, file_hashes._fingerprint(path))
                second = hashes.sha256(path)
                self.assertNotEqual(first, second)
                self.assertEqual(stream.call_count, 2)
                self.assertEqual(hashes._cache, {})

    def test_fine_timestamps_on_non_apfs_still_never_reuse(self):
        path = self.root / "night/receipt.json"
        for filesystem in ("hfs", "exfat", "nfs", None):
            with self.subTest(filesystem=filesystem), \
                 mock.patch.object(file_hashes, "_filesystem_type", return_value=filesystem), \
                 mock.patch.object(file_hashes, "_stream_sha256", wraps=file_hashes._stream_sha256) as stream:
                hashes = file_hashes.FileHashes()
                self.assertEqual(hashes.sha256(path), hashes.sha256(path))
                self.assertEqual(stream.call_count, 2)
                self.assertEqual(hashes._cache, {})

    def test_apfs_reuse_rejects_each_coarse_timestamp_and_checks_link_volume(self):
        path = self.root / "night/receipt.json"
        # Artificial fine timestamps avoid relying on the host's precision.
        identity = (*file_hashes._identity(path.stat())[:-2], 1_001, 2_001)
        with mock.patch.object(file_hashes, "_filesystem_type", return_value="apfs"):
            self.assertTrue(file_hashes.FileHashes()._can_reuse(path, (identity, identity)))
        for stamp in (1_000_000_000, 1_000_000, 1_000):
            for index in (-2, -1):
                with self.subTest(stamp=stamp, index=index), \
                     mock.patch.object(file_hashes, "_filesystem_type", return_value="apfs"):
                    coarse = list(identity)
                    coarse[index] = stamp
                    for fingerprint in ((tuple(coarse), identity), (identity, tuple(coarse))):
                        self.assertFalse(file_hashes.FileHashes()._can_reuse(path, fingerprint))
        target = (identity[0] + 1, *identity[1:])
        for filesystems in (("hfs", "apfs"), ("apfs", "exfat")):
            with self.subTest(filesystems=filesystems), \
                 mock.patch.object(file_hashes, "_filesystem_type", side_effect=filesystems) as detect:
                self.assertFalse(file_hashes.FileHashes()._can_reuse(path, (identity, target)))
                self.assertEqual(detect.call_args_list[0], mock.call(path.parent))
                if filesystems[0] == "apfs":
                    self.assertEqual(detect.call_args_list[1], mock.call(path))

    def test_thread_context_does_not_share_terminal_cache(self):
        seen = []
        with file_hashes.hash_scope(4) as parent:
            thread = threading.Thread(target=lambda: seen.append(file_hashes.current_hashes()))
            thread.start()
            thread.join()
            self.assertIs(file_hashes.current_hashes(), parent)
        self.assertIsNot(seen[0], parent)
        self.assertEqual(seen[0].workers, 1)
        self.assertEqual(seen[0]._cache, {})

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

    @mock.patch.object(file_hashes.FileHashes, "_can_reuse", return_value=True)
    def test_night_publish_reuses_closed_hashes_but_refreshes_courier_changes(self, _reuse):
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

    @mock.patch.object(file_hashes.FileHashes, "_can_reuse", return_value=True)
    def test_cli_scopes_cache_for_terminal_dispatch_and_releases_it(self, _reuse):
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
