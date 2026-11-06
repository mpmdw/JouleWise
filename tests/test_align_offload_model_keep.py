"""Synthetic Git histories only; no model paths are opened."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tests.git_fixture import init_git_fixture

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

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        init_git_fixture(self.root, '-q')
        self.git('config', 'user.email', 'synthetic@example.invalid')
        self.git('config', 'user.name', 'Synthetic')
        self.refs = {}
        self.r0 = 'docs/align/r0_v4.json'
        files = {
            'main': 'configs/campaigns/main/registration/identity_pins.json',
            'bytes': 'configs/campaigns/bytes_v1/roster.json',
            'b6': 'configs/b6/registration/identity_pins.json',
            'align-v4': k.ALIGN + 'registration/identity_pins.json',
            'amendment-1': k.AMENDMENT,
            'r0-v4': self.r0,
        }
        # Independent commits: none contains an ad-hoc merge of the lanes.
        for role, name in files.items():
            self.git('checkout', '--orphan', role)
            for p in list(self.root.glob('configs/**/*.json')) + list(self.root.glob('docs/**/*')):
                if p.is_file() or p.is_symlink():
                    p.unlink()
            self.git('rm', '-rf', '--ignore-unmatch', 'configs', 'docs')
            self.write(name, ('Qwen3.8-27B Qwen3-30B Qwen2.5-1.5B\n' if name.endswith('.md')
                             else json.dumps({'model': {'source': '/text/' + role}})))
            if role == 'bytes':
                self.write('configs/bytes/identity_pins.json', json.dumps({'model_source': '/text/extension'}))
            if role == 'b6':
                self.write(k.B6_ROSTER, 'Qwen3-8B\n')
            self.git('add', '.')
            self.git('commit', '-qm', role)
            self.refs[role] = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True,
                                       stderr=subprocess.DEVNULL)

    def write(self, name, data):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data)

    def test_several_refs_without_checkout_or_merge_and_full_provenance(self):
        # Working copy poison and symlinks must never be consulted.
        self.write(self.r0, 'not json')
        result = k.derive(self.root, self.refs, self.r0)
        self.assertEqual(result['paths'], ['/text/align-v4', '/text/b6', '/text/bytes',
                                          '/text/extension', '/text/main', '/text/r0-v4'])
        self.assertEqual(result['reviewed_refs'], self.refs)
        self.assertIn('Qwen3.8-27B', result['model_ids'])
        self.assertEqual({r['role'] for r in result['inputs']}, set(k.ROLES))
        for row in result['inputs']:
            self.assertEqual(row['commit'], self.refs[row['role']])
            self.assertEqual(len(row['sha256']), 64)
        (self.root / self.r0).unlink()
        (self.root / self.r0).symlink_to('/must-not-follow')
        self.assertEqual(k.derive(self.root, self.refs, self.r0), result)

    def test_missing_role_or_stale_kit_ref_refuses(self):
        with self.assertRaisesRegex(ValueError, 'six'):
            k.derive(self.root, {'main': self.refs['main']}, self.r0)
        refs = {**self.refs, 'align-v4': self.refs['main']}
        with self.assertRaisesRegex(ValueError, 'missing.*align-v4'):
            k.derive(self.root, refs, self.r0)

    def test_symlink_git_blob_and_blinded_input_refuse(self):
        self.git('checkout', '-f', 'r0-v4')
        path = self.root / self.r0
        path.unlink()
        path.symlink_to('/must-not-follow')
        self.git('add', '.')
        self.git('commit', '-qm', 'synthetic symlink')
        refs = {**self.refs, 'r0-v4': self.git('rev-parse', 'HEAD').strip()}
        with self.assertRaisesRegex(ValueError, 'symlink'):
            k.derive(self.root, refs, self.r0)
        for name in ('docs/restricted/model.json', 'docs/withheld/model.json', '../escape', '/absolute'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'unsafe'):
                k.derive(self.root, self.refs, name)


if __name__ == '__main__':
    unittest.main()
