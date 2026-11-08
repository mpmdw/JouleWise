"""Synthetic harvest I/O witnesses (Sol build, ported for R17). Never open local study data.

Sol's raw transport was folded into joulewise.align.apple.harvest_offload (it refused
symlinks, which every ALIGN session's measurement view uses); its record-bound finalized
manifest is kept there and exercised here.
"""
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
        from joulewise.align.apple import harvest_offload as off
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
                    io_workers=workers,
                    stage_observer=rows.append)
            record = window.harvest(seams=seams(1), prepare_desk=True, run_g3=False)
            self.assertEqual(record['verdict'], h.COLLECTED, record)
            reference = {str(p.relative_to(window.archive)): p.read_bytes()
                         for p in window.archive.rglob('*') if p.is_file()}
            shutil.rmtree(window.archive)  # synthetic output only
            self.assertEqual(manifest(window.root), original)
            finalized = off.finalized_manifest(window.root)        # MBP, at finalize (record-bound)
            off.pack(window.root, root/'transport', finalized=finalized)
            # Model the two hosts mounting exactly the SAME canonical paths.
            # Absolute locators in original bytes remain untouched. Compare
            # every file without scrubbing paths, clocks, digests or reports.
            window.root.rename(root/'original-kept')
            off.unpack(root/'transport', window.root, finalized=finalized,
                       finalized_sha256=off.manifest_sha256(finalized))
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


if __name__ == '__main__':
    unittest.main()
