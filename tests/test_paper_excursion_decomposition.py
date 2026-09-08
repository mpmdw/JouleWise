"""Scratch-only regressions for optional backup discovery."""
from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/paper_excursion_decomposition.py"


class BackupProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory(prefix="excursion-backups-")
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        override = mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": str(self.root)})
        override.start()
        self.addCleanup(override.stop)
        spec = importlib.util.spec_from_file_location("excursion_probe_test", SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_empty_override_disables_all_roots(self) -> None:
        with mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": ""}):
            self.assertEqual(self.module.backup_roots(), ())

    def test_override_splits_roots(self) -> None:
        second = self.root / "second"
        with mock.patch.dict(os.environ, {
            "JOULEWISE_BACKUP_ROOTS": os.pathsep.join((str(self.root), str(second)))
        }):
            self.assertEqual(self.module.backup_roots(), (self.root, second))

    def test_blocking_directory_check_is_unavailable_within_budget(self) -> None:
        self._assert_block_bounded("is_dir")

    def test_blocking_enumeration_is_unavailable_within_budget(self) -> None:
        self._assert_block_bounded("glob")

    def _assert_block_bounded(self, method: str) -> None:
        release = threading.Event()
        entered = threading.Event()
        workers = []

        def block(*args, **kwargs):
            workers.append(threading.current_thread())
            entered.set()
            release.wait(10)
            return False if method == "is_dir" else iter(())

        try:
            with mock.patch.object(Path, method, side_effect=block):
                with self.assertLogs(self.module.__name__, level="WARNING") as logs:
                    started = time.monotonic()
                    result = self.module.probe_backup_root(self.root, timeout_s=0.05)
                    elapsed = time.monotonic() - started
            self.assertTrue(entered.is_set())
            self.assertEqual(result, ())
            self.assertLess(elapsed, 0.5)
            self.assertTrue(workers[0].daemon)
            self.assertIn("backup_root_unavailable reason=timeout", logs.output[0])
        finally:
            release.set()
            for worker in workers:
                worker.join(1)

    def test_absent_and_io_error_roots_are_unavailable(self) -> None:
        self.assertEqual(self.module.probe_backup_root(self.root / "absent"), ())
        with mock.patch.object(Path, "is_dir", side_effect=OSError("offline")):
            with self.assertLogs(self.module.__name__, level="WARNING") as logs:
                self.assertEqual(self.module.probe_backup_root(self.root), ())
        self.assertIn("backup_root_unavailable reason=os_error", logs.output[0])

    def test_probe_retains_both_search_depths(self) -> None:
        paths = []
        for prefix in ("one", "two/nested"):
            path = self.root / prefix / "instrument_validation" / self.module.MEMBER_ID / "raw/powermetrics.plist"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"fixture")
            paths.append(path)
        self.assertEqual(self.module.probe_backup_root(self.root), tuple(paths))

    def test_unavailable_probe_preserves_absent_root_result(self) -> None:
        raw = b"fixture primary bytes"
        path = self.root / self.module.SOURCE_DIRECTORY / "raw/powermetrics.plist"
        path.parent.mkdir(parents=True)
        path.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        with mock.patch.dict(os.environ, {"JOULEWISE_BACKUP_ROOTS": ""}):
            absent = self.module.locate_raw_powermetrics(self.root, digest)
        with mock.patch.object(self.module, "probe_backup_root", return_value=()):
            unavailable = self.module.locate_raw_powermetrics(self.root, digest)
        self.assertEqual(absent, raw)
        self.assertEqual(unavailable, absent)


if __name__ == "__main__":
    unittest.main()
