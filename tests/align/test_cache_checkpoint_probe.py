"""Offline config/probe contract; no native backend or measurement reads."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from scripts.align_cache_checkpoint_native import payload_projection, tiny_config


class CheckpointProbeTests(unittest.TestCase):
    def test_optional_source_test_import_does_not_stat_external_home(self):
        source = '''
from pathlib import Path
from unittest.mock import patch
root = Path.cwd()
original = Path.is_dir
def guarded(path):
    if str(path).startswith('/Users/edr/') and not path.is_relative_to(root):
        raise AssertionError('external home stat: ' + str(path))
    return original(path)
with patch.object(Path, 'is_dir', guarded):
    import tests.align.test_pilot4
'''
        root = Path(__file__).resolve().parents[2]
        env = dict(os.environ, PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE='1')
        env.pop('JW_ALIGN_REAL_SHADE_TEST', None)
        result = subprocess.run([sys.executable, '-B', '-c', source], cwd=root,
                                env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_real_configs_select_the_tested_native_families(self):
        root = Path(__file__).with_name('fixtures')
        for family, fixture, expected_text_type in (
            ('qwen3_next', 'qwen3_next_config.json', 'qwen3_next'),
            ('qwen3_5', 'qwen38_config.json', 'qwen3_5_text'),
        ):
            with self.subTest(family=family):
                real = json.loads((root / fixture).read_text())
                tiny = tiny_config(family)
                self.assertEqual(real['model_type'], family)
                self.assertEqual(tiny['model_type'], family)
                self.assertEqual(real.get('text_config', real)['model_type'], expected_text_type)
                text = tiny.get('text_config', tiny)
                self.assertEqual(text['model_type'], expected_text_type)
                self.assertEqual(text['num_hidden_layers'], 4)
                self.assertEqual(text['full_attention_interval'], 4)

    def test_planning_payload_excludes_unmeasured_timing(self):
        for family, two_snapshots, replacement, plus_active in (
            ('qwen3_next', 154534080, 231800832, 309067776),
            ('qwen3_5', 307888384, 461832192, 615776256),
        ):
            with self.subTest(family=family):
                row = payload_projection(family, 'bfloat16')
                self.assertIsNone(row['byte_proportional_timing_ms'])
                self.assertEqual(row['two_retained_payload_bytes'], two_snapshots)
                self.assertEqual(row['replacement_snapshot_array_bytes'], replacement)
                self.assertEqual(row['replacement_plus_active_recurrent_array_bytes'], plus_active)

    def test_native_timings_are_never_scaled_by_retained_array_bytes(self):
        timings = {'checkpoint': {'median_ms': .125}, 'restore': {'median_ms': .25}}
        for family in ('qwen3_next', 'qwen3_5'):
            with self.subTest(family=family):
                row = payload_projection(family, 'bfloat16', timings)
                self.assertIsNone(row['byte_proportional_timing_ms'])
                self.assertEqual(row['snapshot_storage'], 'immutable_array_reference_retention')

    def test_estimate_cli_never_imports_native_backend(self):
        # Guard imports even when MLX is installed. This checks data-free
        # estimation, not a mocked numerical result.
        source = '''
import importlib.abc, runpy, sys
class BlockNative(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('mlx', 'mlx_lm'):
            raise AssertionError('estimate-only imported ' + fullname)
sys.meta_path.insert(0, BlockNative())
sys.argv = ['scripts/align_cache_checkpoint_native.py', '--estimate-only']
runpy.run_path(sys.argv[0], run_name='__main__')
'''
        root = Path(__file__).resolve().parents[2]
        env = dict(os.environ, PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run([sys.executable, '-B', '-c', source], cwd=root,
                                env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(line)['projection'] for line in result.stdout.splitlines()]
        self.assertEqual(len(rows), 4)
        self.assertEqual({(r['family'], r['dtype']) for r in rows}, {
            ('qwen3_next', 'float32'), ('qwen3_next', 'bfloat16'),
            ('qwen3_5', 'float32'), ('qwen3_5', 'bfloat16'),
        })
        self.assertTrue(all(r['byte_proportional_timing_ms'] is None for r in rows))


if __name__ == '__main__':
    unittest.main()
