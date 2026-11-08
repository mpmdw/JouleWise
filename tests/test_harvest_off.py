"""Synthetic harvest I/O and transport witnesses. Never open local study data."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.b5 import harvest as h


def manifest(root):
    return {str(p.relative_to(root)): ({'directory': True} if p.is_dir() else
            {'size': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
            for p in sorted(root.rglob('*'))}


class HarvestIOTests(unittest.TestCase):
    def test_parallel_inventory_preserves_order_links_and_copy_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/'raw'
            source.mkdir()
            for name in ('z', 'a', 'empty'):
                (source/name).write_bytes(name.encode()*10000 if name != 'empty' else b'')
            (source/'link').symlink_to('z')
            expected = h.tree_inventory(source)
            self.assertEqual(list(expected), list(h.tree_inventory(source, workers=2)))
            self.assertEqual(expected, h.tree_inventory(source, workers=2))
            h.archive_sources({'raw': source}, root/'serial')
            h.archive_sources({'raw': source}, root/'parallel', workers=2)
            self.assertEqual(h.tree_inventory(root/'serial'), h.tree_inventory(root/'parallel'))
            def corrupt(src, dst):
                shutil.copytree(src, dst, symlinks=True)
                (dst/'a').write_bytes(b'corrupt')
            with self.assertRaisesRegex(h.HarvestFault, 'archive_copy_mismatch'):
                h.archive_sources({'raw': source}, root/'corrupt', clone=corrupt, workers=2)

    def test_stage_profile_is_external_to_harvest_bytes(self):
        rows = []
        # Exercise the real wrapper without constructing a window or probing a host.
        run = object.__new__(h._Harvest)
        run.seams = h.Seams(stage_observer=rows.append)
        self.assertEqual(run.step('synthetic', lambda: 42), 42)
        self.assertEqual(rows[0]['stage'], 'synthetic')
        self.assertGreaterEqual(rows[0]['wall_s'], 0)
        self.assertFalse(rows[0]['failed'])

    def test_profile_reports_cli_exit_without_opening_measurements(self):
        from scripts import harvest_b6_session as cli
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp)/'profile.jsonl'
            argv = [arg for name in ('plan', 'archive-root', 'registration-dir',
                                    'pack-records-root', 'export-dir')
                    for arg in ('--'+name, str(Path(tmp)/name))]
            with patch.object(cli, '_run', return_value=3):
                self.assertEqual(cli.main(argv+['--profile', str(profile)]), 3)
            rows = [json.loads(line) for line in profile.read_text().splitlines()]
            self.assertIn({'stage': 'cli.result', 'exit_code': 3}, rows)
            self.assertEqual(rows[-1]['stage'], 'cli.total')

    @unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
    def test_complete_harvest_equal_on_verified_copy_in_canonical_namespace(self):
        from joulewise.harvest_transport import pack_raw, unpack_raw
        # This guard MUST precede importing the existing fixture module: its
        # optional native-test decorator otherwise stats a local archive.
        with patch.dict(os.environ, {'JW_B5_SYNTHETIC_ONLY': '1'}):
            from tests.test_harvest_b5_window import Window
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            window = Window(root/'canonical')
            original = manifest(window.root)
            rows = []
            def seams(workers):
                # The proposed immutable replay envelope fixes these values.
                # No assertion here implies default live clocks are portable.
                return h.Seams(group_alive=lambda _: False, now=lambda: 1794096000.0,
                    monotonic_ns=lambda: 100, boot_session_uuid=lambda: 'SYNTHETIC-BOOT',
                    harvest_checkout=lambda **_: {'schema': h.HARVEST_CHECKOUT_SCHEMA,
                        'head': 'a'*40, 'root': '/canonical/harvest-program',
                        'files': {}, 'errors': [], 'status_clean': True, 'status_lines': 0},
                    io_workers=workers, parse_cache_bytes=0 if workers == 1 else 128 << 20,
                    stage_observer=rows.append)
            record = window.harvest(seams=seams(1), prepare_desk=True, run_g3=False)
            self.assertEqual(record['verdict'], h.COLLECTED, record)
            reference = {str(p.relative_to(window.archive)): p.read_bytes()
                         for p in window.archive.rglob('*') if p.is_file()}
            shutil.rmtree(window.archive)  # synthetic output only
            self.assertEqual(manifest(window.root), original)
            pack_raw(window.root, root/'transport', original, workers=2)
            # Model the two hosts mounting exactly the SAME canonical paths.
            # Absolute locators in original bytes remain untouched. Compare
            # every file without scrubbing paths, clocks, digests or reports.
            window.root.rename(root/'original-kept')
            unpack_raw(root/'transport', window.root, original)
            replay = window.harvest(seams=seams(2), prepare_desk=True, run_g3=False)
            self.assertEqual(replay['verdict'], record['verdict'],
                (window.archive/'withheld/collector-errors.json').read_text())
            self.assertEqual(replay, record)
            observed = {str(p.relative_to(window.archive)): p.read_bytes()
                        for p in window.archive.rglob('*') if p.is_file()}
            self.assertEqual(observed, reference)
            self.assertIn('sources_unchanged', {r['stage'] for r in rows})
            if profile := os.environ.get('JW_HARVEST_OFF_PROFILE'):
                Path(profile).write_text(json.dumps({'files': len(reference), 'stages': rows,
                    'raw_bytes': sum(r.get('size', 0) for r in original.values())}, indent=2)+'\n')


@unittest.skipUnless(shutil.which('zstd'), 'zstd CLI required')
class RawTransportTests(unittest.TestCase):
    def test_deduplicated_compressed_copy_restores_exact_bytes(self):
        from joulewise.harvest_transport import pack_raw, unpack_raw
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/'raw'
            (source/'night').mkdir(parents=True)
            raw = b'<?xml version="1.0"?><plist><dict/></plist>\n'*100000
            (source/'powermetrics.plist').write_bytes(raw)
            (source/'duplicate.plist').write_bytes(raw)
            (source/'night/result.json').write_bytes(b'{"terminal":true}\n')
            expected = manifest(source)
            packed = pack_raw(source, root/'packed', expected, workers=2)
            self.assertEqual(packed['files'], 3)
            self.assertEqual(packed['payloads'], 2)
            unpack_raw(root/'packed', root/'air', expected)
            self.assertEqual(manifest(root/'air'), expected)
            self.assertEqual(manifest(source), expected)
            # Compression is canonical for a pinned zstd version/thread count.
            pack_raw(root/'air', root/'repacked', expected, workers=1)
            self.assertEqual(manifest(root/'packed'), manifest(root/'repacked'))

    def test_changed_missing_extra_escaping_and_symlink_inputs_refuse(self):
        from joulewise.harvest_transport import pack_raw
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/'raw'
            source.mkdir()
            (source/'one').write_bytes(b'original')
            expected = manifest(source)
            (source/'one').write_bytes(b'changed!')
            with self.assertRaisesRegex(ValueError, 'digest'):
                pack_raw(source, root/'bad', expected)
            self.assertFalse((root/'bad').exists())
            (source/'one').unlink()
            with self.assertRaises(ValueError):
                pack_raw(source, root/'bad', expected)
            (source/'one').symlink_to(root/'absent')
            with self.assertRaises(ValueError):
                pack_raw(source, root/'bad', expected)
            with self.assertRaises(ValueError):
                pack_raw(source, root/'bad', {'../escape': next(iter(expected.values()))})
            (source/'one').unlink()
            (source/'one').write_bytes(b'original')
            (source/'extra').write_bytes(b'extra')
            with self.assertRaises(ValueError):
                pack_raw(source, root/'bad', expected)

    def test_corrupt_payload_or_wrong_committed_manifest_never_publishes(self):
        from joulewise.harvest_transport import pack_raw, unpack_raw
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/'raw'
            source.mkdir()
            (source/'one').write_bytes(bytes(range(256))*10000)
            expected = manifest(source)
            pack_raw(source, root/'packed', expected)
            with self.assertRaises(ValueError):
                unpack_raw(root/'packed', root/'bad', {})
            payload = next((root/'packed/payloads').iterdir())
            payload.write_bytes(payload.read_bytes()[:10])
            with self.assertRaises((ValueError, subprocess.CalledProcessError)):
                unpack_raw(root/'packed', root/'bad', expected)
            self.assertFalse((root/'bad').exists())


if __name__ == '__main__':
    unittest.main()
