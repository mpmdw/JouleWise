"""Synthetic-only checks of per-run archive restoration and source immutability."""
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from joulewise import desk_restore as restore
from joulewise import desk_compress as desk


ZSTD = Path(desk.zstd_path()).is_file()


class RestoreRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.archive = self.root / "archive"
        self.run = self.archive / "sources" / "claim-runs" / "synthetic-run"
        (self.run / "raw").mkdir(parents=True)
        (self.run / "metadata.json").write_text('{"fixture":true}\n')
        (self.run / "raw" / "powermetrics.plist").write_bytes(b"synthetic plist bytes\n" * 123)
        (self.run / "power_trace.csv").write_bytes(b"fixture,only\n1,2\n")
        self.scratch = self.root / "scratch"
        self.record_dir = self.root / "archive.desk"
        self.records = self.record_dir / "compression.jsonl"
        self.custody = self.root / "custody"
        (self.custody / "night").mkdir(parents=True)
        (self.custody / "night" / "chain.exited").write_text('{}\n')
        (self.archive / "harvest.json").write_text('{"verdict":"COLLECTED"}\n')

    @staticmethod
    def snapshot(root):
        return {str(p.relative_to(root)): p.read_bytes()
                for p in root.rglob("*") if p.is_file()}

    def compress(self):
        rc, summary = desk.compress(archive=self.archive, custody=self.custody,
                                    record_dir=self.record_dir, min_bytes=0)
        # Three run files plus custody/night/chain.exited are eligible at
        # min_bytes=0; harvest.json remains protected by the real compressor.
        self.assertEqual((rc, summary["files"]), (0, 4))

    def change_raw_record(self, **changes):
        rows = [json.loads(line) for line in self.records.read_text().splitlines()]
        for row in rows:
            if row["path"] == str(self.run / "raw" / "powermetrics.plist"):
                row.update(changes)
        self.records.write_text("".join(json.dumps(row) + "\n" for row in rows))

    @contextmanager
    def restored(self, source=None, scratch=None, **kwargs):
        # Simulate free space exceeding the standing 40 GiB floor by exactly
        # the fixture bytes; CI can exercise the floor without a 40 GiB disk.
        size = sum(p.stat().st_size for p in self.run.rglob("*") if p.is_file())
        required = sum(row["size"] for row in desk.status(self.record_dir))
        with mock.patch.object(restore.shutil, "disk_usage", return_value=mock.Mock(
                free=restore.MIN_RESERVE_GIB * 1024**3 + size + required)):
            with restore.restored_run(source or self.run, scratch or self.scratch, **kwargs) as run:
                yield run

    def test_plain_archive_is_identical_and_cleaned_after_reader(self):
        expected = self.snapshot(self.run)
        with self.restored() as run:
            self.assertEqual(self.snapshot(run), expected)
            self.assertNotEqual(run, self.run)
            restored = run
        self.assertFalse(restored.exists())
        self.assertEqual(list(self.scratch.iterdir()), [])
        self.assertEqual(self.snapshot(self.run), expected)

    def test_plain_reader_keeps_original_path_without_scratch(self):
        # A stale compressed sibling must not override existing plain bytes.
        (self.run / "metadata.json.zst").write_bytes(b"invalid stale sibling")
        with mock.patch.object(restore, "restored_run", side_effect=AssertionError("unneeded restore")):
            with restore.readable_run(self.run) as run:
                self.assertEqual(run, self.run)

    @unittest.skipUnless(ZSTD, "zstd is optional")
    def test_tree_reader_preserves_root_manifests_and_partial_directories(self):
        source = self.run.parent
        manifest = source / "campaign_manifests/manifest.json"
        manifest.parent.mkdir()
        manifest.write_bytes(b'{"members":[]}\n')
        partial = source / "failed-partial/raw/capture.txt"
        partial.parent.mkdir(parents=True)
        partial.write_bytes(b"retained partial evidence\n")
        (source / "failed-empty").mkdir()
        expected = self.snapshot(source)
        rc, _ = desk.compress(archive=self.archive, custody=self.custody,
                              record_dir=self.record_dir, min_bytes=0)
        self.assertEqual(rc, 0)
        before, journal = self.snapshot(source), self.records.read_bytes()
        required = sum(row[4] for row in restore._inventory(source.resolve(), restore._records(self.records)))
        with mock.patch.object(restore.shutil, "disk_usage", return_value=mock.Mock(
                free=restore.MIN_RESERVE_GIB * 1024**3 + required)):
            # The per-run API keeps its bundle-shape requirement.
            with self.assertRaisesRegex(restore.RestoreRefused, "run-dir must name one bundle"):
                with restore.readable_run(source, compression_records=self.records):
                    self.fail("non-bundle reached the run reader")
            with restore.readable_tree(source, compression_records=self.records) as plain:
                self.assertEqual(self.snapshot(plain), expected)
                self.assertTrue((plain / "failed-empty").is_dir())
                restored = plain
        self.assertFalse(restored.exists())
        self.assertEqual(self.snapshot(source), before)
        self.assertEqual(self.records.read_bytes(), journal)

    @unittest.skipUnless(ZSTD, "zstd is optional")
    def test_reader_discovers_journal_and_cleans_scratch_on_success_and_error(self):
        expected = self.snapshot(self.run)
        self.compress()
        before, journal = self.snapshot(self.archive), self.records.read_bytes()
        with mock.patch.object(restore.shutil, "disk_usage", return_value=mock.Mock(
                free=restore.MIN_RESERVE_GIB * 1024**3 + sum(
                    row["size"] for row in desk.status(self.record_dir)))):
            for fail in (False, True):
                with self.subTest(fail=fail):
                    try:
                        with restore.readable_run(self.run) as run:
                            self.assertEqual(self.snapshot(run), expected)
                            scratch = run.parent.parent
                            self.assertNotIn(self.archive, scratch.parents)
                            if fail:
                                raise RuntimeError("reader failed")
                    except RuntimeError as error:
                        self.assertTrue(fail)
                        self.assertEqual(str(error), "reader failed")
                    self.assertFalse(scratch.exists())
        self.assertEqual(self.snapshot(self.archive), before)
        self.assertEqual(self.records.read_bytes(), journal)

    @unittest.skipUnless(ZSTD, "zstd is optional")
    def test_reader_requires_journal_and_accepts_explicit_nonstandard_location(self):
        expected = self.snapshot(self.run)
        self.compress()
        moved = self.root / "nonstandard"
        self.record_dir.rename(moved)
        with self.assertRaisesRegex(ValueError, "compressed run requires compression.jsonl"):
            with restore.readable_run(self.run):
                self.fail("reader reached")
        with mock.patch.object(restore.shutil, "disk_usage", return_value=mock.Mock(
                free=restore.MIN_RESERVE_GIB * 1024**3 + sum(row["size"] for row in desk.status(moved)))):
            with restore.readable_run(self.run, compression_records=moved / "compression.jsonl") as run:
                self.assertEqual(self.snapshot(run), expected)
        self.assertFalse(run.exists())

    @unittest.skipUnless(ZSTD, "zstd is optional")
    def test_compressed_and_plain_archives_give_identical_bytes(self):
        with self.restored() as run:
            plain = self.snapshot(run)
        self.compress()
        before = self.snapshot(self.root / "archive")
        journal_before = self.records.read_bytes()
        with self.restored(compression_records=self.records) as run:
            self.assertEqual(self.snapshot(run), plain)
        self.assertEqual(self.snapshot(self.root / "archive"), before)
        self.assertEqual(self.records.read_bytes(), journal_before)
        self.assertEqual(list(self.scratch.iterdir()), [])

    @unittest.skipUnless(ZSTD, "zstd is optional")
    def test_compressed_metadata_is_a_run_and_restores_identically(self):
        expected = self.snapshot(self.run)
        self.compress()
        before = self.snapshot(self.root / "archive")
        with self.restored(compression_records=self.records) as run:
            self.assertEqual(self.snapshot(run), expected)
        self.assertEqual(self.snapshot(self.root / "archive"), before)
        self.assertEqual(list(self.scratch.iterdir()), [])

    @unittest.skipUnless(ZSTD, "zstd is optional")
    def test_digest_mismatch_never_reaches_reader(self):
        self.compress()
        self.change_raw_record(sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            with self.restored(compression_records=self.records):
                self.fail("reader reached")
        self.assertEqual(list(self.scratch.iterdir()), [])

    @unittest.skipUnless(ZSTD, "zstd is optional")
    def test_bad_frame_and_wrong_size_are_rejected(self):
        self.compress()
        self.change_raw_record(size=1)
        with self.assertRaisesRegex(ValueError, "size mismatch"):
            with self.restored(compression_records=self.records):
                self.fail("reader reached")
        self.assertEqual(list(self.scratch.iterdir()), [])
        (self.run / "raw" / "powermetrics.plist.zst").write_bytes(b"invalid frame")
        with self.assertRaises(ValueError):
            with self.restored(compression_records=self.records):
                self.fail("reader reached")
        self.assertEqual(list(self.scratch.iterdir()), [])

    @unittest.skipUnless(ZSTD, "zstd is optional")
    def test_missing_record_and_ambiguous_siblings_are_rejected(self):
        self.compress()
        with self.assertRaisesRegex(ValueError, "no digest record"):
            with self.restored():
                self.fail("reader reached")
        (self.run / "raw" / "powermetrics.plist").write_bytes(b"plain sibling")
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            with self.restored(compression_records=self.records):
                self.fail("reader reached")

    def test_cleanup_on_reader_failure_and_sequential_runs(self):
        with self.assertRaisesRegex(RuntimeError, "fixture reader"):
            with self.restored() as first:
                raise RuntimeError("fixture reader")
        self.assertFalse(first.exists())
        second = self.run.with_name("second-run")
        shutil.copytree(self.run, second)
        with self.restored(source=second) as run:
            self.assertEqual(run.name, "second-run")
            self.assertEqual(len(list(self.scratch.iterdir())), 1)
        self.assertEqual(list(self.scratch.iterdir()), [])

    def test_refuses_session_roots_nested_scratch_and_symlinks(self):
        for source, scratch in ((self.run.parent, self.scratch), (self.run, self.run / "scratch"),
                                (self.run, self.archive / "scratch"),
                                (self.run, self.run.parent / "scratch")):
            with self.subTest(source=source, scratch=scratch), self.assertRaises(ValueError):
                with self.restored(source, scratch):
                    self.fail("reader reached")
        with self.assertRaisesRegex(ValueError, "outside the compression records"):
            with self.restored(scratch=self.record_dir / "scratch", compression_records=self.records):
                self.fail("reader reached")
        (self.run / "linked").symlink_to(self.root)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            with self.restored():
                self.fail("reader reached")
        self.assertFalse(self.scratch.exists())

    def test_space_refusal_happens_before_restoration(self):
        with mock.patch.object(restore.shutil, "disk_usage", return_value=mock.Mock(free=0)):
            with self.assertRaisesRegex(ValueError, "insufficient scratch space"):
                with restore.restored_run(self.run, self.scratch):
                    self.fail("reader reached")
        self.assertEqual(list(self.scratch.iterdir()), [])

    def test_space_gate_accounts_for_the_entire_restored_footprint(self):
        required = sum(p.stat().st_size for p in self.run.rglob("*") if p.is_file())
        # One byte below reserve + required would cross the standing floor.
        free = restore.MIN_RESERVE_GIB * 1024**3 + required - 1
        with mock.patch.object(restore.shutil, "disk_usage", return_value=mock.Mock(free=free)):
            with self.assertRaisesRegex(ValueError, "insufficient scratch space"):
                with restore.restored_run(self.run, self.scratch):
                    self.fail("reader reached")
        with mock.patch.object(restore.shutil, "disk_usage", return_value=mock.Mock(free=free + 1)):
            with restore.restored_run(self.run, self.scratch) as run:
                self.assertEqual(self.snapshot(run), self.snapshot(self.run))
        self.assertEqual(list(self.scratch.iterdir()), [])

    def test_unreadable_directory_is_not_silently_omitted(self):
        scandir = restore.os.scandir

        def denied(path):
            if Path(path) == self.run / "raw":
                raise PermissionError("fixture directory unreadable")
            return scandir(path)

        with mock.patch.object(restore.os, "scandir", side_effect=denied):
            with self.assertRaisesRegex(restore.RestoreRefused, "restore_refused:.*directory unreadable"):
                with self.restored():
                    self.fail("reader reached")
        self.assertFalse(self.scratch.exists())

    def test_default_reserve_and_invalid_reserves(self):
        # The 2026-10-12 eviction began near 29 GiB free; restore the earlier
        # 40 GiB margin above it. Exact integer GiB, not a measured comparison.
        self.assertEqual(restore.MIN_RESERVE_GIB, 40)
        # 39 GiB is one GiB below that reserve, even before fixture bytes.
        with mock.patch.object(restore.shutil, "disk_usage", return_value=mock.Mock(free=39 * 1024**3)):
            with self.assertRaisesRegex(ValueError, "insufficient scratch space"):
                with restore.restored_run(self.run, self.scratch):
                    self.fail("reader reached")
        for reserve in (-1, 0, 25, 29, 39, float("nan"), float("inf")):
            with self.subTest(reserve=reserve), self.assertRaisesRegex(ValueError, "finite and at least 40"):
                with restore.restored_run(self.run, self.scratch, reserve_gib=reserve):
                    self.fail("reader reached")

    def test_cli_passes_restored_path_and_reader_exit_status(self):
        # This subprocess exercises the real free-space gate. The extra
        # bytes are exactly the single synthetic run's restored footprint.
        required = sum(p.stat().st_size for p in self.run.rglob("*") if p.is_file())
        if shutil.disk_usage(self.root).free < restore.MIN_RESERVE_GIB * 1024**3 + required:
            self.skipTest("real CLI restore requires the project's 40 GiB free-disk floor")
        if ZSTD:
            self.compress()
        before = self.snapshot(self.archive)
        journal = self.records.read_bytes() if ZSTD else None
        seen = self.root / "seen-path.txt"
        code = ("from pathlib import Path; import sys; p=Path(sys.argv[1]); "
                "assert (p/'metadata.json').is_file(); Path(sys.argv[2]).write_text(str(p)); "
                "raise SystemExit(7)")
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve().parents[1] / "scripts/restore_run_to_scratch.py"),
                                 "--run-dir", str(self.run), "--scratch-dir", str(self.scratch),
                                 *(["--compression-records", str(self.records)] if ZSTD else []),
                                 "--", sys.executable, "-B", "-c", code, "{run}", str(seen)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertFalse(Path(seen.read_text()).exists())
        self.assertEqual(list(self.scratch.iterdir()), [])
        self.assertEqual(self.snapshot(self.archive), before)
        if ZSTD:
            self.assertEqual(self.records.read_bytes(), journal)

    @unittest.skipUnless(ZSTD, "zstd is optional")
    def test_real_bundle_readers_match_plain_after_cli_scratch_restore(self):
        seed = Path(__file__).resolve().parent / "fixtures/d117_v2_production/strict_seed_bundle"
        metadata = json.loads((seed / "metadata.json").read_bytes())
        shutil.rmtree(self.run)
        self.run = self.run.with_name(metadata["run_id"])
        shutil.copytree(seed, self.run)
        required = sum(p.stat().st_size for p in self.run.rglob("*") if p.is_file())
        if shutil.disk_usage(self.root).free < restore.MIN_RESERVE_GIB * 1024**3 + required:
            self.skipTest("real CLI restore requires the project's 40 GiB free-disk floor")
        reader = ("import json, sys; from pathlib import Path; "
                  "from joulewise.cli import validate_bundle; from joulewise.reduce import reduce_bundle; "
                  "p=Path(sys.argv[1]); stored=json.loads((p/'summary_metrics.json').read_bytes()); "
                  "v=stored['summary_provenance']['reducer_version']; "
                  "out={'problems':list(validate_bundle(p, strict=True)), "
                  "'summary':reduce_bundle(p, reducer_version=v).to_dict()}; "
                  "Path(sys.argv[2]).write_text(json.dumps(out,sort_keys=True))")
        expected = self.root / "expected.json"
        subprocess.run([sys.executable, "-B", "-c", reader, str(self.run), str(expected)], check=True)
        self.assertEqual(json.loads(expected.read_bytes())["problems"], [])
        rc, summary = desk.compress(archive=self.archive, custody=self.custody,
                                    record_dir=self.record_dir, min_bytes=0)
        self.assertEqual(rc, 0)
        self.assertGreater(summary["files"], 0)
        before = self.snapshot(self.archive)
        journal = self.records.read_bytes()
        observed = self.root / "observed.json"
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve().parents[1] / "scripts/restore_run_to_scratch.py"),
                                 "--run-dir", str(self.run), "--scratch-dir", str(self.scratch),
                                 "--compression-records", str(self.records), "--",
                                 sys.executable, "-B", "-c", reader, "{run}", str(observed)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        # Identical code on identical restored bytes: the full serialized
        # output (including every derived quantity) must match bit for bit.
        self.assertEqual(observed.read_bytes(), expected.read_bytes())
        self.assertEqual(self.snapshot(self.archive), before)
        self.assertEqual(self.records.read_bytes(), journal)
        self.assertEqual(list(self.scratch.iterdir()), [])

    @unittest.skipUnless(ZSTD, "zstd is optional")
    def test_latest_restore_event_and_damaged_journal_refuse_compressed_inputs(self):
        self.compress()
        with self.records.open("a") as stream:
            stream.write('{"event":"compress"')
        with self.assertRaisesRegex(ValueError, "invalid compression journal"):
            with self.restored(compression_records=self.records):
                self.fail("reader reached")
        rows = self.records.read_text().splitlines()[:-1]
        restored = next(json.loads(row) for row in rows
                        if json.loads(row)["path"] == str(self.run / "raw/powermetrics.plist"))
        restored["event"] = "restore"
        self.records.write_text("\n".join([*rows, json.dumps(restored)]) + "\n")
        with self.assertRaisesRegex(ValueError, "no digest record"):
            with self.restored(compression_records=self.records):
                self.fail("reader reached")


if __name__ == "__main__":
    unittest.main()
