"""Apply the shipped R0 patch to Git code, then test pure synthetic seams."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
BASE = '49e78e1784b6b498ace68895d8fbdd2443214e9d'


class R0PatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name).resolve()
        text = (ROOT / 'docs/align/r0_disk_gate_patch.md').read_text()
        patches = re.findall(r'```diff\n(.*?)```', text, re.S)
        if not patches:
            raise AssertionError('no reviewable patch')
        cls.files = set(re.findall(r'^--- a/(.+)$', '\n'.join(patches), re.M))
        for name in cls.files:
            data = subprocess.check_output(['git', '-C', str(ROOT), 'show', BASE + ':' + name])
            target = cls.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        for patch in patches:
            subprocess.run(['git', 'apply', '--check', '-'], input=patch, text=True,
                           check=True, cwd=cls.root, capture_output=True)
            subprocess.run(['git', 'apply', '-'], input=patch, text=True,
                           check=True, cwd=cls.root, capture_output=True)
        cls.host_text = (cls.root / 'joulewise/align/r0_host.py').read_text()
        cls.runner_text = (cls.root / 'joulewise/align/r0_runner.py').read_text()
        cls.ns = dict(os=os, Path=Path, hashlib=hashlib, shutil=shutil, re=re, stat=stat)
        parsed = ast.parse(cls.host_text)
        selected = [n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name in
                    ('inventory', 'required_free_bytes', 'disk_census') or
                    isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in
                    ('DISK_FLOOR_BYTES', 'AMENDMENT_PATH') for t in n.targets)]
        exec(compile(ast.Module(body=selected, type_ignores=[]), '<patched R0 pure seams>', 'exec'), cls.ns)

    def budget(self, value=7_000_000_000):
        return dict(window1_bytes_per_copy=value, copies=2,
                    authority='a' * 40 + ':' + self.ns['AMENDMENT_PATH'])

    def test_required_free_two_copies_plus_floor_exact_boundary(self):
        config = dict(disk_budget=self.budget(), disk_path='/synthetic', models={},
                      offloads=[dict(label=label, inventory=str(self.root / (label + '.json')),
                                     destination='/synthetic/' + label) for label in ('pilot8', 'pilot9')])
        rows = [{'path': 'blob', 'bytes': 1, 'sha256': 'b' * 64}]
        for item in config['offloads']:
            Path(item['inventory']).write_text(json.dumps(rows))
        required = 44_000_000_000  # synthetic 7 GB * 2 + 30 GB
        self.assertEqual(self.ns['required_free_bytes'](config), required)
        with mock.patch.dict(self.ns, inventory=mock.Mock(return_value=rows)), \
             mock.patch.object(shutil, 'disk_usage') as disk:
            for free, status in ((required - 1, 'fail'), (required, 'pass'), (required + 1, 'pass')):
                disk.return_value.free = free
                result = self.ns['disk_census'](config, {})
                self.assertEqual(result['status'], status)
                self.assertEqual(result['required_free_bytes_after_weights'], required)
                self.assertEqual(result['design']['authority'], config['disk_budget']['authority'])
        self.assertNotIn('80_000_000_000', self.host_text)

    def test_missing_bad_or_unreviewed_budget_refuses(self):
        for budget in ({}, self.budget(None), self.budget(True), self.budget(-1),
                       {**self.budget(), 'copies': 1}, {**self.budget(), 'copies': True},
                       {**self.budget(), 'authority': 'main:unreviewed'}):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                self.ns['required_free_bytes']({'disk_budget': budget})
        example = json.loads((self.root / 'docs/align/r0_desk.example.json').read_text())
        with self.assertRaises(ValueError):
            self.ns['required_free_bytes'](example)
        self.assertIn('required_free_bytes(config)', self.runner_text)

    def test_pilot_view_and_dangling_links_record_target_text_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / 'runs').mkdir()
            (root / 'runs' / 'opaque').write_bytes(b'synthetic')
            target = '/never-follow/restricted/measurement'
            (root / 'measurement').symlink_to(target, target_is_directory=True)
            (root / 'dangling').symlink_to('/never-follow/missing')
            opened = []
            real_open = os.open
            def open_local(path, flags, *args, **kwargs):
                self.assertEqual(Path(path), root / 'runs' / 'opaque')
                self.assertTrue(flags & os.O_NOFOLLOW)
                opened.append(str(path))
                return real_open(path, flags, *args, **kwargs)
            with mock.patch.object(os, 'open', side_effect=open_local):
                rows = self.ns['inventory'](root, record_symlinks=True)
            self.assertEqual([r for r in rows if r.get('type') == 'symlink'], [
                {'path': 'dangling', 'type': 'symlink', 'target': '/never-follow/missing'},
                {'path': 'measurement', 'type': 'symlink', 'target': target}])
            self.assertEqual(len(opened), 1)
            self.assertEqual(rows[-1]['bytes'], 9)
            self.assertIn('guard.check, record_symlinks=True', self.runner_text)
            with self.assertRaisesRegex(ValueError, 'materialized'):
                self.ns['inventory'](root)

    def test_real_synthetic_restricted_directory_still_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / 'restricted').mkdir()
            with self.assertRaisesRegex(ValueError, 'blinded'):
                self.ns['inventory'](root, record_symlinks=True)


if __name__ == '__main__':
    unittest.main()
