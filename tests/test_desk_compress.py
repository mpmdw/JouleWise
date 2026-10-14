"""Synthetic round trips and failure paths; no collection or hardware timing."""
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise import desk_compress as desk
from joulewise.b5.harvest import tree_inventory

ZSTD = shutil.which("zstd") or "/opt/homebrew/bin/zstd"


@unittest.skipUnless(Path(ZSTD).is_file(), "zstd CLI required")
class DeskCompressTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.archive, self.custody, self.runs = [self.root / name for name in ("archive", "custody", "runs")]
        for path in (self.archive / "sources", self.custody / "night", self.runs):
            path.mkdir(parents=True)
        (self.custody / "night/chain.exited").write_text('{}')
        (self.archive / "harvest.json").write_text('{"verdict":"COLLECTED"}')
        self.records = Path(str(self.archive) + ".desk")

    def compress(self, **kwargs):
        return desk.compress(archive=self.archive, custody=self.custody, runs_roots=[self.runs], **kwargs)

    def put(self, path, data=b"a" * (1048576 + 1)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_round_trip_modes_times_reader_and_harvest_inventory(self):
        files = [self.put(self.runs / "random", random.Random(5).randbytes(1048576)),
                 self.put(self.runs / "repeat"), self.put(self.runs / "empty", b""),
                 self.put(self.archive / "sources/raw", b"b" * 1048576),
                 self.put(self.custody / "raw", b"c" * 1048576)]
        for path in files:
            path.chmod(0o640)
            os.utime(path, ns=(1234567890000000000, 1234567890123456789))
        before = [tree_inventory(path) for path in (self.runs, self.custody, self.archive)]
        stats = {path: (path.stat().st_mode, path.stat().st_mtime_ns) for path in files}
        expected = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
        self.assertEqual(desk.read_bytes(files[0]), files[0].read_bytes())
        rc, summary = self.compress()
        self.assertEqual(rc, 0)
        self.assertEqual(summary["files"], 4)
        self.assertTrue(files[2].exists())
        for path in files:
            self.assertEqual(hashlib.sha256(desk.read_bytes(path)).hexdigest(), expected[path])
        self.assertEqual(self.compress()[1]["files"], 0)
        self.assertEqual(desk.restore(record_dir=self.records, reserve_gib=0)[0], 0)
        self.assertEqual([tree_inventory(path) for path in (self.runs, self.custody, self.archive)], before)
        for path in files:
            self.assertEqual((path.stat().st_mode, path.stat().st_mtime_ns), stats[path])
        self.assertEqual(desk.status(self.records), [])

    def test_protected_realpaths_clones_and_symlinks(self):
        capture = self.runs / "odd_capture"
        protected = [capture / "raw", self.archive / "sources/claim-runs/instrument_validation/pre/raw",
                     self.archive / "sources/ledger/large", self.archive / "sources/inputs/large",
                     self.archive / "sources/repo/large", self.archive / "sources/SHA256SUMS",
                     self.runs / "derived/large", self.runs / "withheld/large",
                     self.runs / "calibration_ledger_head.json"]
        for path in protected:
            self.put(path)
        ledger = self.root / "ledger.jsonl"
        alias = self.root / "runs-link"
        alias.symlink_to(self.runs, target_is_directory=True)
        ledger.write_text(json.dumps({"custody_locator": str(alias / "odd_capture"), "runs_root": str(self.runs)}) + '\n')
        copy = self.archive / "sources/ledger/calibration_observation_ledger.jsonl"
        copy.write_bytes(ledger.read_bytes())
        raw = self.put(self.runs / "ordinary")
        link = self.runs / "symlink"
        link.symlink_to(raw)
        before = {path: path.read_bytes() for path in protected}
        rc, summary = self.compress(ledgers=[ledger])
        self.assertEqual(rc, 0)
        self.assertEqual(summary["files"], 1)
        self.assertGreaterEqual(summary["skipped_protected"], len(protected))
        self.assertEqual({path: path.read_bytes() for path in protected}, before)
        self.assertTrue(link.is_symlink())

    def test_unreadable_or_malformed_ledger_keeps_every_original(self):
        path = self.put(self.runs / "raw")
        bad = self.root / "bad-ledger"
        for text in (None, 'not-json', '[]', '{"custody_locator":3}'):
            with self.subTest(text=text):
                if text is not None:
                    bad.write_text(text)
                self.assertEqual(self.compress(ledgers=[bad])[0], 5)
                self.assertTrue(path.exists())
                self.assertFalse(Path(str(path) + '.zst').exists())
        self.assertIn('ledger_unreadable', (self.records / 'compression.jsonl').read_text())

    def test_ledger_session_rows_and_archive_copy_locators(self):
        capture = self.put(self.runs / 'capture/raw')
        ledger = self.archive / 'sources/ledger/calibration_observation_ledger.jsonl'
        self.put(ledger, (json.dumps({'runs_root': str(self.runs)}) + '\n'
                          + json.dumps({'runs_root': str(self.runs), 'custody_locator': 'capture'}) + '\n').encode())
        self.put(self.runs / 'ordinary')
        self.assertEqual(self.compress()[1]['files'], 1)
        self.assertTrue(capture.exists())

    def test_preconditions_write_nothing(self):
        path = self.put(self.runs / "raw")
        exited = self.custody / "night/chain.exited"
        exited.unlink()
        self.assertEqual(self.compress()[0], 4)
        exited.write_text('{}')
        (self.archive / "harvest.json").write_text('{"verdict":"HARVEST_FAULT"}')
        self.assertEqual(self.compress()[0], 4)
        (self.archive / "harvest.json").write_text('{"verdict":"COLLECTED"}')
        self.assertEqual(self.compress(after=[self.root / "missing"])[0], 4)
        self.assertTrue(path.exists())
        self.assertFalse(self.records.exists())

    def test_path_shim_verify_mismatch_keeps_original(self):
        raw = self.put(self.runs / "raw")
        shimdir = self.root / "bin"
        shimdir.mkdir()
        shim = shimdir / "zstd"
        shim.write_text(f"#!{sys.executable}\nimport os, sys\n"
                        "if '-c' in sys.argv:\n    os.write(1, b'corrupt')\n    sys.exit(0)\n"
                        f"os.execv({ZSTD!r}, [{ZSTD!r}] + sys.argv[1:])\n")
        shim.chmod(0o755)
        with patch.dict(os.environ, {"PATH": str(shimdir) + os.pathsep + os.environ.get("PATH", "")}):
            self.assertEqual(desk.zstd_path(), str(shim))
            rc, summary = self.compress()
        self.assertEqual((rc, summary['mismatches']), (2, 1))
        self.assertTrue(raw.exists())
        self.assertFalse(Path(str(raw) + '.zst.partial').exists())

    def test_crash_recovery_original_wins(self):
        raw = self.put(self.runs / "raw")
        compressed = self.put(Path(str(raw) + '.zst'), b'invalid-old-output')
        partial = self.put(self.runs / "orphan.partial", b'partial')
        self.assertEqual(self.compress()[0], 0)
        self.assertFalse(partial.exists())
        self.assertFalse(raw.exists())
        self.assertTrue(compressed.exists())
        self.assertEqual(desk.read_bytes(raw), b'a' * 1048577)
        self.assertEqual(desk.restore(record_dir=self.records, reserve_gib=0)[0], 0)

    def test_restore_space_is_checked_before_any_write(self):
        self.put(self.runs / 'raw')
        self.compress()
        before = tree_inventory(self.root)
        with patch.object(desk, 'statvfs', return_value=SimpleNamespace(f_bavail=0, f_frsize=4096)):
            rc, summary = desk.restore(record_dir=self.records, reserve_gib=0)
        self.assertEqual(rc, 3)
        self.assertEqual(summary['shortfall_bytes'], 1048577)
        self.assertEqual(tree_inventory(self.root), before)

    def test_restore_mismatch_keeps_compressed_file(self):
        raw = self.put(self.runs / 'raw')
        self.compress()
        manifest = self.records / 'compression.jsonl'
        rows = [json.loads(line) for line in manifest.read_text().splitlines()]
        rows[0]['sha256'] = '0' * 64
        manifest.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        self.assertEqual(desk.restore(record_dir=self.records, reserve_gib=0)[0], 2)
        self.assertFalse(raw.exists())
        self.assertTrue(Path(str(raw) + '.zst').exists())
        self.assertFalse(Path(str(raw) + '.partial').exists())

    def test_cli_compress_status_and_selected_restore(self):
        self.put(self.runs / 'raw')
        self.put(self.custody / 'raw')
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(desk.main(['compress', '--archive', str(self.archive), '--custody', str(self.custody),
                                        '--runs-root', str(self.runs)]), 0)
            self.assertEqual(desk.main(['status', '--record-dir', str(self.records)]), 0)
            self.assertEqual(desk.main(['restore', '--record-dir', str(self.records), '--root', 'runs', '--reserve-gib', '0']), 0)
        self.assertIn('compress files=2 before=', output.getvalue())
        self.assertEqual(len(desk.status(self.records)), 1)
        result = subprocess.run([sys.executable, 'scripts/desk_compress.py', 'status', '--record-dir', str(self.records)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('status files=1', result.stdout)
