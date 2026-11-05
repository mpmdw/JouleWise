import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location('keep', Path(__file__).resolve().parents[1] / 'scripts/align_offload_model_keep.py')
k = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(k)


class ModelKeepTests(unittest.TestCase):
    def test_sources_are_text_not_followed_and_include_blobs(self):
        data = {'unit': {'model_source': '/not-mounted/Qwen-ref'},
                'models': {'N': {'source': '/not-mounted/Qwen-next'}},
                'model_artifact_inventory': {'a': {'root': '/not-mounted/snapshot',
                    'files': [{'resolved_path': '/not-mounted/blob'}]}}}
        self.assertEqual(k.sources(data), {'/not-mounted/Qwen-ref', '/not-mounted/Qwen-next',
                                          '/not-mounted/snapshot', '/not-mounted/blob'})
        with self.assertRaises(ValueError):
            k.sources({'model_source': '/bad/../model'})

    def test_derivation_covers_all_configs_rosters_and_r0(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            files = {
                'configs/campaigns/bytes_v1/roster.json': {'models': [{'model': {'source': '/text/bytes'}}]},
                'configs/b6/registration/identity_pins.json': {'unit': {'model_source': '/text/b6'}},
                'configs/bytes/identity_pins.json': {'unit': {'model_source': '/text/extension'}},
                'configs/campaigns/align_pilot_v3/registration/identity_pins.json': {'unit': {'model_source': '/text/neg8'}},
                'configs/other/model.json': {'model': {'source': '/text/other'}},
            }
            for name, data in files.items():
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps(data))
            r0 = root / 'r0.json'
            r0.write_text(json.dumps({'models': {'N': {'source': '/text/r0'}}}))
            with mock.patch.object(k.subprocess, 'check_output', return_value='\0'.join(files) + '\0'):
                paths, receipts = k.derive(root, r0)
                self.assertEqual(paths, ['/text/b6', '/text/bytes', '/text/extension', '/text/neg8', '/text/other', '/text/r0'])
                self.assertEqual(len(receipts), 6)
                (root / next(iter(files))).unlink()
                (root / next(iter(files))).symlink_to('/must-not-follow')
                with self.assertRaisesRegex(ValueError, 'symlink'):
                    k.derive(root, r0)
            with mock.patch.object(k.subprocess, 'check_output', return_value=''):
                with self.assertRaisesRegex(ValueError, 'missing'):
                    k.derive(root, r0)
