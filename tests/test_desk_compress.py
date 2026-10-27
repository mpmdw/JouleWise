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
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import warnings

from joulewise import desk_compress as desk
from joulewise.b5.harvest import tree_inventory

ZSTD = shutil.which("zstd") or "/opt/homebrew/bin/zstd"


class DeskCompressFixture(unittest.TestCase):
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


@unittest.skipUnless(Path(ZSTD).is_file(), "zstd CLI required")
class DeskCompressTests(DeskCompressFixture):
    def test_open_bytes_consumer_closes(self):
        path = self.put(self.runs / "consumer-closes")
        for compressed in (False, True):
            with self.subTest(compressed=compressed):
                if compressed:
                    self.assertEqual(self.compress()[0], 0)
                with desk.open_bytes(path) as stream:
                    observed = stream.read(10)
                    stream.close()
                self.assertEqual(observed, b"a" * 10)

    def test_open_bytes_textiowrapper_dropped(self):
        path = self.put(self.runs / "wrapper-dropped")
        for compressed in (False, True):
            with self.subTest(compressed=compressed):
                if compressed:
                    self.assertEqual(self.compress()[0], 0)
                with desk.open_bytes(path) as stream:
                    wrapper = io.TextIOWrapper(stream, encoding="latin-1")
                    observed = wrapper.read(5)
                    # Dropping an unclosed wrapper intentionally emits this
                    # warning; its close of the underlying stream is the case.
                    with warnings.catch_warnings(action="ignore", category=ResourceWarning):
                        del wrapper
                    self.assertTrue(stream.closed)
                self.assertEqual(observed, "a" * 5)

    def damaged_frame(self, name):
        path = self.put(self.runs / name, random.Random(573).randbytes(1048576))
        self.assertEqual(self.compress()[0], 0)
        compressed = Path(str(path) + ".zst")
        frame = compressed.read_bytes()
        compressed.write_bytes(frame[:len(frame) // 2])
        return path, compressed, frame

    def test_open_bytes_read_to_eof_then_close_checks_damaged_frame_status(self):
        path, compressed, frame = self.damaged_frame("eof-then-close")

        def consume(size=-1):
            with desk.open_bytes(path) as stream:
                self.assertTrue(stream.read(size))
                stream.close()

        for size in (-1, None, len(frame) * 2):
            with self.subTest(size=size), self.assertRaisesRegex(OSError, "decompression_failed"):
                consume(size)
        compressed.write_bytes(frame)
        consume()  # A closed full reader of a healthy frame remains valid.

    def test_open_bytes_textiowrapper_eof_then_dropped_checks_damaged_frame_status(self):
        path, compressed, frame = self.damaged_frame("wrapper-eof-then-dropped")

        def consume():
            with desk.open_bytes(path) as stream:
                wrapper = io.TextIOWrapper(stream, encoding="latin-1")
                self.assertTrue(wrapper.read())
                with warnings.catch_warnings(action="ignore", category=ResourceWarning):
                    del wrapper
                self.assertTrue(stream.closed)

        with self.assertRaisesRegex(OSError, "decompression_failed"):
            consume()
        compressed.write_bytes(frame)
        consume()

    def test_open_bytes_empty_read_before_close_preserves_eof_status_check(self):
        path, _, _ = self.damaged_frame("empty-read-then-close")
        for method in ("read", "read1", "readinto", "readinto1", "readline", "iteration"):
            with self.subTest(method=method), self.assertRaisesRegex(OSError, "decompression_failed"):
                with desk.open_bytes(path) as stream:
                    if method == "iteration":
                        for _ in stream:
                            pass
                    elif method.startswith("readinto"):
                        buffer = bytearray(io.DEFAULT_BUFFER_SIZE)
                        while getattr(stream, method)(buffer):
                            pass
                    else:
                        while getattr(stream, method)(io.DEFAULT_BUFFER_SIZE):
                            pass
                    stream.close()

    def test_open_bytes_zero_length_read_then_close_is_partial(self):
        path, _, _ = self.damaged_frame("zero-read-then-close")
        for method in ("read", "read1", "readinto", "readinto1", "readline"):
            with self.subTest(method=method), desk.open_bytes(path) as stream:
                argument = bytearray() if method.startswith("readinto") else 0
                self.assertFalse(getattr(stream, method)(argument))
                stream.close()

    def test_partial_compressed_read_exits_within_plain_path_budget(self):
        payload = random.Random(573).randbytes(4 * 1024 * 1024)
        path = self.put(self.runs / "partial-read", payload)
        probe = ("import sys\nfrom pathlib import Path\n"
                 "from joulewise.desk_compress import open_bytes\n"
                 "with open_bytes(Path(sys.argv[1])) as stream:\n"
                 "    assert stream.read(10).hex() == sys.argv[2]\n")
        argv = [sys.executable, "-B", "-c", probe, str(path), payload[:10].hex()]
        started = time.monotonic()
        # Five seconds bounds even the plain-path child on a busy test runner.
        plain = subprocess.run(argv, capture_output=True, text=True, timeout=5)
        plain_seconds = time.monotonic() - started
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertEqual(self.compress()[0], 0)
        self.assertFalse(path.exists())
        # Operational hang detector: give decompression 100x the measured plain
        # subprocess time, with a 5 s startup/scheduling floor. No energy bar.
        result = subprocess.run(argv, capture_output=True, text=True,
                                timeout=max(5, 100 * plain_seconds))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_full_read_still_rejects_a_damaged_compressed_frame(self):
        path = self.put(self.runs / "damaged", random.Random(573).randbytes(1048576))
        self.assertEqual(self.compress()[0], 0)
        compressed = Path(str(path) + ".zst")
        frame = compressed.read_bytes()
        compressed.write_bytes(frame[:len(frame) // 2])
        with self.assertRaisesRegex(OSError, "decompression_failed"):
            desk.read_bytes(path)

    def test_git_hazards_and_campaign_logs_stay_plain_in_every_root(self):
        protected = []
        raw = []
        for root in (self.runs, self.custody, self.archive / "sources"):
            for relative in ("clone/.git/objects/pack/pack-fixture.pack", "worktree/.git",
                             "nested/hazards/monitor/battery.jsonl",
                             "hazards/meter/stream-001.jsonl", "nested/campaign_log.jsonl"):
                protected.append(self.put(root / relative))
            raw.append(self.put(root / "run/raw/powermetrics.plist"))
        before = {path: path.read_bytes() for path in protected + raw}
        rc, summary = self.compress()
        self.assertEqual((rc, summary["files"]), (0, len(raw)))
        self.assertGreaterEqual(summary["skipped_protected"], len(protected))
        for path in protected:
            self.assertEqual(path.read_bytes(), before[path])
            self.assertFalse(Path(str(path) + ".zst").exists())
        for path in raw:
            self.assertFalse(path.exists())
            self.assertEqual(desk.read_bytes(path), before[path])
        # Protected files are counted in the summary, omitted from the journal:
        # only successful transformations need a restorable custody record.
        self.assertEqual({row["path"] for row in desk.status(self.records)}, {str(path) for path in raw})

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
        for text in (None, 'not-json\n{}\n', '[]', '{"custody_locator":3}'):
            with self.subTest(text=text):
                if text is not None:
                    bad.write_text(text)
                self.assertEqual(self.compress(ledgers=[bad])[0], 5)
                self.assertTrue(path.exists())
                self.assertFalse(Path(str(path) + '.zst').exists())
        self.assertIn('ledger_unreadable', (self.records / 'compression.jsonl').read_text())

    def test_review_d1_torn_last_ledger_line_is_recorded_and_compressed(self):
        raw = self.put(self.runs / 'r1/raw/powermetrics.plist', b'A' * (2 * 1048576))
        protected = self.put(self.runs / 'instrument_validation/opening/raw')
        ledger = self.root / 'ledger.jsonl'
        ledger.write_text(json.dumps({'custody_locator': str(self.root / 'elsewhere')}) + '\n{"custody_loc')
        rc, summary = self.compress(ledgers=[ledger])
        self.assertEqual((rc, summary['files'], summary['ledger_lines_skipped']), (0, 1, 1))
        self.assertFalse(raw.exists())
        self.assertTrue(Path(str(raw) + '.zst').exists())
        self.assertTrue(protected.exists())
        rows = [json.loads(line) for line in (self.records / 'compression.jsonl').read_text().splitlines()]
        self.assertEqual((rows[0]['event'], rows[0]['line']), ('ledger_line_skipped', 2))
        self.assertEqual(desk.restore(record_dir=self.records, reserve_gib=0)[0], 0)
        ledger.write_text('{}\n{"custody_loc\n{}\n')
        self.assertEqual(self.compress(ledgers=[ledger])[0], 5)
        self.assertTrue(raw.exists())

    def test_review_d2_status_restore_skip_torn_manifest_line(self):
        raw = self.put(self.runs / 'raw')
        expected = raw.read_bytes()
        self.assertEqual(self.compress()[0], 0)
        manifest = self.records / 'compression.jsonl'
        with manifest.open('a') as stream:
            stream.write('{"event": "compre')
        summary = {}
        self.assertEqual(len(desk.status(self.records, summary=summary)), 1)
        self.assertEqual(summary['manifest_lines_skipped'], 1)
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(desk.main(['status', '--record-dir', str(self.records)]), 0)
        self.assertIn('manifest_lines_skipped=1', out.getvalue())
        rc, summary = desk.restore(record_dir=self.records, reserve_gib=0)
        self.assertEqual((rc, summary['files'], summary['manifest_lines_skipped']), (0, 1, 1))
        self.assertEqual(raw.read_bytes(), expected)
        self.assertEqual(json.loads(manifest.read_text().splitlines()[-1])['event'], 'restore')

    def test_review_d2b_new_compress_row_is_parseable_and_restorable(self):
        first = self.put(self.runs / 'r1/raw/powermetrics.plist')
        self.assertEqual(self.compress()[0], 0)
        manifest = self.records / 'compression.jsonl'
        with manifest.open('a') as stream:
            stream.write('{"event": "compre')
        second = self.put(self.runs / 'r2/raw/powermetrics.plist', b'B' * (2 * 1048576))
        self.assertEqual(self.compress()[0], 0)
        last = json.loads(manifest.read_text().splitlines()[-1])
        self.assertEqual((last['event'], last['path']), ('compress', str(second)))
        self.assertEqual(len(desk.status(self.records)), 2)
        rc, summary = desk.restore(record_dir=self.records, reserve_gib=0)
        self.assertEqual((rc, summary['files'], summary['manifest_lines_skipped']), (0, 2, 1))
        self.assertEqual(second.read_bytes(), b'B' * (2 * 1048576))
        self.assertTrue(first.exists())

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
        partials = [self.put(self.runs / name, b'partial')
                    for name in ('raw.partial', 'raw.zst.partial', 'orphan.zst.partial')]
        ordinary = self.put(self.runs / 'orphan.partial', b'ordinary data')
        self.assertEqual(self.compress()[0], 0)
        for partial in partials:
            self.assertFalse(partial.exists())
        self.assertEqual(ordinary.read_bytes(), b'ordinary data')
        self.assertFalse(raw.exists())
        self.assertTrue(compressed.exists())
        self.assertEqual(desk.read_bytes(raw), b'a' * 1048577)
        self.assertEqual(desk.restore(record_dir=self.records, reserve_gib=0)[0], 0)

    def test_ordinary_partial_data_round_trips_in_every_root(self):
        data = random.Random(7).randbytes(2 * 1048576)
        expected = hashlib.sha256(data).hexdigest()
        paths = [self.put(root / 'foo.partial', data)
                 for root in (self.runs, self.custody, self.archive / 'sources')]
        # Creating foo.zst during this pass must not turn foo.partial into a leftover.
        siblings = [self.put(path.with_suffix(''), b'other data' * 200000) for path in paths]
        self.assertEqual(self.compress()[0], 0)
        for path in paths:
            self.assertEqual(hashlib.sha256(desk.read_bytes(path)).hexdigest(), expected)
            self.assertTrue(Path(str(path) + '.zst').exists())
        self.assertEqual(desk.restore(record_dir=self.records, reserve_gib=0)[0], 0)
        for path in paths:
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
        for sibling in siblings:
            self.assertEqual(sibling.read_bytes(), b'other data' * 200000)

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


class DeskUnavailableTests(DeskCompressFixture):
    def unavailable_paths(self):
        empty = self.root / 'empty-bin'
        empty.mkdir()
        broken = self.root / 'broken-zstd'
        broken.write_text(f'#!{sys.executable}\nimport sys\nsys.exit(1)\n')
        broken.chmod(0o755)
        nonexecutable = self.put(self.root / 'nonexecutable-zstd', b'not executable')
        nonexecutable.chmod(0o644)
        return empty, (self.root / 'missing-zstd', broken, nonexecutable)

    def test_compress_unavailable_exit_four_preserves_all_bytes(self):
        for root in (self.runs, self.custody, self.archive / 'sources'):
            self.put(root / 'raw')
            self.put(root / 'raw.zst.partial', b'crashed compress')
            self.put(root / 'raw.partial', b'crashed restore')
            self.put(root / 'raw.zst', b'compressed sibling')
        empty, fallbacks = self.unavailable_paths()
        before = tree_inventory(self.root)
        for fallback in fallbacks:
            with self.subTest(fallback=fallback.name), patch.dict(os.environ, {'PATH': str(empty)}), \
                    patch.object(desk, 'ZSTD_FALLBACK', str(fallback)):
                self.assertEqual(self.compress(), (4, {'reason': 'zstd_unavailable'}))
                output = io.StringIO()
                with redirect_stdout(output):
                    rc = desk.main(['compress', '--archive', str(self.archive), '--custody', str(self.custody),
                                    '--runs-root', str(self.runs)])
                self.assertEqual(rc, 4)
                self.assertIn('reason=zstd_unavailable', output.getvalue())
                self.assertEqual(tree_inventory(self.root), before)
                self.assertFalse(self.records.exists())

    def test_restore_unavailable_exit_four_preserves_all_bytes(self):
        raw = self.runs / 'raw'
        self.put(Path(str(raw) + '.zst'), b'synthetic compressed bytes')
        self.put(Path(str(raw) + '.partial'), b'crashed restore')
        self.put(self.records / 'compression.jsonl', (json.dumps({
            'event': 'compress', 'path': str(raw), 'root': 'runs', 'size': 1048576,
            'sha256': '0' * 64}) + '\n').encode())
        empty, fallbacks = self.unavailable_paths()
        before = tree_inventory(self.root)
        for fallback in fallbacks:
            with self.subTest(fallback=fallback.name), patch.dict(os.environ, {'PATH': str(empty)}), \
                    patch.object(desk, 'ZSTD_FALLBACK', str(fallback)):
                self.assertEqual(desk.restore(record_dir=self.records, reserve_gib=0),
                                 (4, {'reason': 'zstd_unavailable'}))
                output = io.StringIO()
                with redirect_stdout(output):
                    rc = desk.main(['restore', '--record-dir', str(self.records), '--reserve-gib', '0'])
                self.assertEqual(rc, 4)
                self.assertIn('reason=zstd_unavailable', output.getvalue())
                self.assertEqual(tree_inventory(self.root), before)

    def test_reader_errors_name_data_path_without_process_argv(self):
        raw = self.runs / 'raw'
        compressed = self.put(Path(str(raw) + '.zst'), b'synthetic compressed bytes')
        empty, fallbacks = self.unavailable_paths()
        for fallback in fallbacks:
            with self.subTest(fallback=fallback.name), patch.dict(os.environ, {'PATH': str(empty)}), \
                    patch.object(desk, 'ZSTD_FALLBACK', str(fallback)):
                with self.assertRaises(OSError) as caught:
                    desk.read_bytes(raw)
                self.assertEqual(caught.exception.filename, str(compressed))
                self.assertNotIsInstance(caught.exception, subprocess.CalledProcessError)
                self.assertNotIn(str(fallback), str(caught.exception))
                plain = self.put(self.runs / 'plain', b'plain data')
                self.assertEqual(desk.read_bytes(plain), b'plain data')
        with self.assertRaises(FileNotFoundError) as caught:
            desk.read_bytes(self.runs / 'missing')
        self.assertEqual(caught.exception.filename, str(self.runs / 'missing.zst'))
