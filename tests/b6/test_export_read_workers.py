"""Exact parity with the pre-optimization exporter, on synthetic bytes only."""
import json
from contextlib import contextmanager
from pathlib import Path
import tempfile
import threading
import types
import unittest
from unittest.mock import patch

from joulewise import desk_compress, desk_restore
from joulewise.b6 import export_runs
from tests.b6.export_profile_support import fixture, serial_exporter
from tests.b6.test_export_runs import seal_reference_inputs

class ExportReadWorkersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        context = serial_exporter()
        cls.serial = context.__enter__()
        cls.addClassCleanup(context.__exit__, None, None, None)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bytes-read-workers-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def compare(self, compressed=False, interval_trace=False):
        archive, reg, plan, pack = fixture(self.root, references=3, blob_bytes=4096,
                                           samples=32, compressed=compressed, interval_trace=interval_trace)
        args = (archive, plan, reg, self.root / "packs", self.root / "out")
        source_bytes = {p: p.read_bytes() for p in archive.rglob("*") if p.is_file()}
        result = self.serial.export(*args, pack_registration=pack)
        side = json.loads(result.sidecar_path.read_bytes())
        paths = [result.csv_path, result.sidecar_path,
                 result.csv_path.parent / side["blinding"]["withheld"]["path"]]
        expected = [path.read_bytes() for path in paths]
        keys = {p: p.read_bytes() for p in (self.root / "packs/bytes").rglob("*") if p.is_file()}
        for workers in (1, 2, 4):
            with self.subTest(workers=workers):
                actual = export_runs.export(*args, pack_registration=pack, read_workers=workers)
                self.assertEqual(actual.structure(), result.structure())
                self.assertEqual([path.read_bytes() for path in paths], expected)
                self.assertEqual({p: p.read_bytes() for p in (self.root / "packs/bytes").rglob("*")
                                  if p.is_file()}, keys)
                self.assertEqual({p: p.read_bytes() for p in archive.rglob("*") if p.is_file()}, source_bytes)

    def test_plain_exports_equal_serial_bytes_and_preserve_keys(self):
        self.compare()

    def test_interval_exports_equal_serial_bytes(self):
        self.compare(interval_trace=True)

    def test_relative_archive_aliases_share_the_verified_read_cache(self):
        with tempfile.TemporaryDirectory(prefix=".export-relative-", dir=Path.cwd()) as temporary:
            root = Path(temporary)
            archive, _, _, _ = fixture(root, references=2, blob_bytes=0, samples=32)
            inputs = export_runs._ReferenceInputs(archive.relative_to(Path.cwd()))
            path = archive / "sources/claim-runs/ref/config.json"
            with patch.object(export_runs, "read_bytes", wraps=export_runs.read_bytes) as read:
                self.assertEqual(inputs.read(path, require_digest=True),
                                 inputs.read(path.relative_to(Path.cwd()), require_digest=True))
                self.assertEqual(read.call_count, 1)

    @unittest.skipUnless(Path(desk_compress.zstd_path()).is_file(), "zstd CLI required")
    def test_compressed_exports_equal_serial_bytes_and_preserve_keys(self):
        with patch("joulewise.desk_restore.shutil.disk_usage",
                   return_value=types.SimpleNamespace(free=100 * 1024**3)):
            self.compare(compressed=True)

    @unittest.skipUnless(Path(desk_compress.zstd_path()).is_file(), "zstd CLI required")
    def test_export_parses_the_shared_compression_journal_once(self):
        archive, reg, plan, pack = fixture(self.root, references=3, blob_bytes=4096,
                                           samples=32, compressed=True)
        with patch("joulewise.desk_restore.shutil.disk_usage",
                   return_value=types.SimpleNamespace(free=100 * 1024**3)), \
                patch.object(desk_restore, "_records", wraps=desk_restore._records) as records:
            export_runs.export(archive, plan, reg, self.root / "packs", self.root / "out",
                               pack_registration=pack, read_workers=4)
            self.assertEqual(records.call_count, 1)

    @unittest.skipUnless(Path(desk_compress.zstd_path()).is_file(), "zstd CLI required")
    def test_journal_cache_invalidates_and_never_hides_corruption_or_deletion(self):
        archive, _, _, _ = fixture(self.root, references=2, blob_bytes=64, samples=32, compressed=True)
        journal = Path(str(archive) + ".desk") / "compression.jsonl"
        original, cache = journal.read_bytes(), {}
        records = desk_restore._cached_records(journal, cache)
        self.assertIs(desk_restore._cached_records(journal, cache), records)
        journal.write_bytes(b"{bad journal}\n")
        with self.assertRaisesRegex(ValueError, "invalid compression journal"):
            desk_restore._cached_records(journal, cache)
        journal.write_bytes(original)
        self.assertEqual(desk_restore._cached_records(journal, cache), records)
        journal.unlink()
        with self.assertRaisesRegex(ValueError, "compressed run requires compression.jsonl"):
            desk_restore._cached_records(journal, cache)

    def test_large_inventory_inputs_are_streamed_and_verified_once(self):
        archive, _, _, _ = fixture(self.root, references=2, blob_bytes=2 * 1024**2, samples=32)
        inputs = export_runs._ReferenceInputs(archive, read_workers=2)
        raw = archive / "sources/claim-runs/ref/raw/synthetic.bin"
        original = export_runs.read_bytes
        open_original = export_runs.open_bytes
        reads = []
        def no_large_read(path):
            self.assertNotEqual(Path(path), raw, "opaque inventory bytes must be streamed")
            return original(path)
        @contextmanager
        def bounded_stream(path):
            with open_original(path) as stream:
                class Stream:
                    def read(inner, size=-1):
                        self.assertGreater(size, 0)
                        self.assertLessEqual(size, desk_compress.CHUNK_BYTES)
                        if Path(path) == raw:
                            reads.append(size)
                        return stream.read(size)
                yield Stream()
        with patch.object(export_runs, "read_bytes", side_effect=no_large_read), \
                patch.object(export_runs, "open_bytes", side_effect=bounded_stream):
            inputs.check_bundle(raw.parent.parent)
            count = len(reads)
            inputs.verify(raw, require_digest=True)
            self.assertEqual(len(reads), count)
            self.assertGreaterEqual(count, 3)  # Two chunks and EOF; no second decompression.
        self.assertIsNone(inputs.verified[raw][2])
        self.assertLessEqual(inputs.cached_bytes, 4 * 1024**2)

    def test_key_operations_and_publication_stay_on_the_calling_thread(self):
        archive, reg, plan, pack = fixture(self.root, references=2, blob_bytes=64, samples=32)
        caller = threading.current_thread()
        def serial_only(function):
            def check(*args, **kwargs):
                self.assertIs(threading.current_thread(), caller)
                return function(*args, **kwargs)
            return check
        with patch.object(export_runs.blinding, "factor", side_effect=serial_only(export_runs.blinding.factor)), \
                patch.object(export_runs.blinding, "bind_session_keys",
                             side_effect=serial_only(export_runs.blinding.bind_session_keys)), \
                patch.object(export_runs, "atomic_write", side_effect=serial_only(export_runs.atomic_write)):
            export_runs.export(archive, plan, reg, self.root / "packs", self.root / "out",
                               pack_registration=pack, read_workers=4)

    def test_workers_overlap_but_first_refusal_is_serial_order(self):
        archive, _, _, _ = fixture(self.root, references=2, blob_bytes=64, samples=32)
        inputs = export_runs._ReferenceInputs(archive, read_workers=2)
        bundle = archive / "sources/claim-runs/ref"
        first, second = threading.Event(), threading.Event()
        original = inputs.verify
        def verify(path, **kwargs):
            if path.name == "config.json":
                first.set()
                self.assertTrue(second.wait(5), "second read must overlap the first")
                raise export_runs.StorageStop("first serial refusal")
            if path.name == "events.jsonl":
                self.assertTrue(first.wait(5))
                second.set()
                raise export_runs.StorageStop("later serial refusal")
            return original(path, **kwargs)
        with patch.object(inputs, "verify", side_effect=verify), self.assertRaisesRegex(
                export_runs.StorageStop, "first serial refusal"):
            inputs.check_bundle(bundle)

    def test_invalid_workers_refuse_before_keys_or_outputs(self):
        archive, reg, plan, pack = fixture(self.root, references=2, blob_bytes=0, samples=32)
        for workers in (0, -1, 9, True, 1.5):
            with self.subTest(workers=workers), self.assertRaises(ValueError):
                export_runs.export(archive, plan, reg, self.root / "packs", self.root / "out",
                                   pack_registration=pack, read_workers=workers)
        self.assertFalse((self.root / "packs").exists())
        self.assertFalse((self.root / "out").exists())

    def test_faults_preserve_exact_serial_refusal_and_publish_nothing(self):
        mutations = {
            "missing-raw": lambda a: (a / "sources/claim-runs/corpus/raw/synthetic.bin").unlink(),
            "bad-trace": lambda a: (a / "sources/claim-runs/corpus/power_trace.csv").write_bytes(b"bad"),
            "missing-events": lambda a: (a / "sources/claim-runs/corpus/events.jsonl").unlink(),
            "bad-summary": lambda a: (a / "withheld/reductions/corpus.summary_metrics.rereduced.json").write_bytes(b"bad"),
            "unlisted": lambda a: (a / "sources/claim-runs/corpus/extra").write_bytes(b"extra"),
            "malformed-events": lambda a: (
                (a / "sources/claim-runs/corpus/events.jsonl").write_bytes(b"{bad"), seal_reference_inputs(a)),
        }
        for name, mutate in mutations.items():
            with self.subTest(fault=name):
                root = self.root / name
                root.mkdir()
                archive, reg, plan, pack = fixture(root, references=2, blob_bytes=64, samples=32)
                mutate(archive)
                args = (archive, plan, reg, root / "packs", root / "out")
                with self.assertRaises(export_runs.StorageStop) as serial:
                    self.serial.export(*args, pack_registration=pack)
                for workers in (1, 4):
                    with self.assertRaises(export_runs.StorageStop) as optimized:
                        export_runs.export(*args, pack_registration=pack, read_workers=workers)
                    self.assertEqual(str(optimized.exception), str(serial.exception))
                self.assertFalse((root / "out").exists())

    def test_cached_control_bytes_invalidate_on_rewrite_and_failed_auth_is_not_cached(self):
        archive, _, _, _ = fixture(self.root, references=2, blob_bytes=0, samples=32)
        inputs = export_runs._ReferenceInputs(archive)
        path = archive / "sources/claim-runs/ref/config.json"
        original = path.read_bytes()
        with patch.object(export_runs, "read_bytes", wraps=export_runs.read_bytes) as read:
            self.assertEqual(inputs.read(path, require_digest=True), original)
            self.assertEqual(inputs.read(path, require_digest=True), original)
            self.assertEqual(read.call_count, 1)
            path.write_bytes(b"x" * len(original))
            with self.assertRaisesRegex(export_runs.StorageStop, "digest mismatch"):
                inputs.read(path, require_digest=True)
            path.write_bytes(original)
            self.assertEqual(inputs.read(path, require_digest=True), original)
            self.assertEqual(read.call_count, 3)

    @unittest.skipUnless(Path(desk_compress.zstd_path()).is_file(), "zstd CLI required")
    def test_compressed_corruption_preserves_exact_serial_refusal(self):
        for fault in ("frame", "missing", "journal"):
            with self.subTest(fault=fault):
                root = self.root / fault
                root.mkdir()
                archive, reg, plan, pack = fixture(root, references=2, blob_bytes=4096,
                                                   samples=32, compressed=True)
                raw = archive / "sources/claim-runs/corpus/raw/synthetic.bin.zst"
                if fault == "frame":
                    raw.write_bytes(raw.read_bytes()[:-4])
                elif fault == "missing":
                    raw.unlink()
                else:
                    journal = Path(str(archive) + ".desk") / "compression.jsonl"
                    rows = [json.loads(line) for line in journal.read_text().splitlines()]
                    for row in rows:
                        row["sha256"] = "0" * 64
                    journal.write_text("".join(json.dumps(row) + "\n" for row in rows))
                args = (archive, plan, reg, root / "packs", root / "out")
                with patch("joulewise.desk_restore.shutil.disk_usage",
                           return_value=types.SimpleNamespace(free=100 * 1024**3)):
                    with self.assertRaises(export_runs.StorageStop) as serial:
                        self.serial.export(*args, pack_registration=pack)
                    for workers in (1, 4):
                        with self.assertRaises(export_runs.StorageStop) as optimized:
                            export_runs.export(*args, pack_registration=pack, read_workers=workers)
                        self.assertEqual(str(optimized.exception), str(serial.exception))
                self.assertFalse((root / "out").exists())


if __name__ == "__main__":
    unittest.main()
