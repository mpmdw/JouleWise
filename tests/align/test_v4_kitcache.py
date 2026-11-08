"""Content-cache regressions using synthetic files and Git repositories only."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import align_v4_kit as kit
from joulewise.align.apple import v4_registration as reg


def git(root, *args):
    return subprocess.run(['git', *args], cwd=root, check=True,
                          capture_output=True).stdout.decode().strip()


def receipt_fixture(root):
    """The complete artifact roster contains synthetic text, never study data."""
    paths = [*reg.ARTIFACTS, 'docs/align/v4/gate-A.md', 'docs/align/v4/gate-B.md']
    for path in paths:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('synthetic input: ' + path + '\n')
    git(root, 'init', '-q')
    git(root, 'add', '.')
    git(root, '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
        'commit', '-qm', 'Synthetic registration')
    hashes = {p: reg.digest((root / p).read_bytes()) for p in paths}
    return dict(schema=reg.RECEIPT_SCHEMA, status='registered', commit=git(root, 'rev-parse', 'HEAD'),
                artifacts={p: hashes[p] for p in reg.ARTIFACTS},
                rulings={str(n): 'installed' for n in reg.RULINGS},
                gates={s: dict(verdict='ADMIT', path=f'docs/align/v4/gate-{s}.md',
                               sha256=hashes[f'docs/align/v4/gate-{s}.md']) for s in ('A', 'B')},
                lead_signature='lead: synthetic-test 2026-11-08')


def generation_fixture(root):
    """Synthetic filled R1/W1 inputs; historical configs are Git code objects."""
    from tests.align.test_v4_kit import ready_inputs, filled_w1_plan
    inputs, slots = ready_inputs()
    for path, value in ((kit.INPUTS, inputs), (kit.R1_SLOTS, slots)):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(kit.raw_json(value))
    git(root, 'init', '-q')
    # This clone's code objects only. Git may use its allowed shared alternate.
    (root / '.git/objects/info/alternates').write_text(str(kit.ROOT / '.git/objects') + '\n')
    files = kit.build_files(root)
    plan = filled_w1_plan(inputs, slots,
                          collection_plan=json.loads(files[kit.KIT / 'collection_plan.json']))
    (root / kit.W1_PLAN).write_bytes(kit.raw_json(plan))


class GenerationCacheTests(unittest.TestCase):
    def test_warm_generate_skips_builder_but_check_always_rebuilds_and_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = kit.generate(root)
            with patch.object(kit, 'build_files', side_effect=AssertionError('cache missed')):
                self.assertEqual(kit.generate(root), first)
            with patch.object(kit, 'build_files', wraps=kit.build_files) as build:
                for _ in range(2):
                    with self.assertRaisesRegex(ValueError, 'BLOCKED'):
                        kit.generate(root, check=True)
                self.assertEqual(build.call_count, 2)

    def test_warm_generate_repairs_output_and_skips_unchanged_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = kit.generate(root)
            path = root / kit.KIT / 'collection_plan.json'
            stamp = path.stat().st_mtime_ns
            kit.generate(root)
            self.assertEqual(path.stat().st_mtime_ns, stamp)
            path.write_bytes(b'drift')
            self.assertEqual(kit.generate(root), files)
            self.assertEqual(path.read_bytes(), files[kit.KIT / 'collection_plan.json'])

    def test_check_shares_git_snapshot_with_its_fresh_readiness_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit.generate(tmp)
            def ready(root):
                kit.d_turn_cap_tokens(root)
                raise ValueError('synthetic readiness refused')
            run = subprocess.run
            with patch.object(kit, 'require_w1_ready', side_effect=ready), \
                 patch.object(subprocess, 'run', wraps=run) as calls:
                with self.assertRaisesRegex(ValueError, 'synthetic readiness refused'):
                    kit.generate(tmp, check=True)
                self.assertEqual(len(calls.call_args_list), 1)

    def test_input_digests_include_optional_absence_and_bytes_without_mtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in (kit.INPUTS, kit.R1_SLOTS):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((kit.ROOT / path).read_bytes())
            before = kit.generation_input_digests(root)
            target = root / kit.INPUTS
            stamp = target.stat()
            target.write_bytes(target.read_bytes() + b' ')
            os.utime(target, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
            self.assertNotEqual(kit.generation_input_digests(root), before)
            absent = kit.generation_input_digests(root)
            (root / kit.W1_PLAN).write_text('{}')
            self.assertNotEqual(kit.generation_input_digests(root), absent)

    def test_code_changes_and_new_python_modules_change_the_content_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in (kit.INPUTS, kit.R1_SLOTS):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((kit.ROOT / path).read_bytes())
            code = root / 'scripts/new_lazy_dependency.py'
            code.parent.mkdir()
            (root / 'joulewise').mkdir()
            with patch.object(kit, 'ROOT', root):
                absent = kit.generation_input_digests(root)
                code.write_text('VALUE = 1\n')
                before = kit.generation_input_digests(root)
                self.assertNotEqual(before, absent)
                code.write_text('VALUE = 2\n')
                self.assertNotEqual(kit.generation_input_digests(root), before)

    def test_changed_input_rebuilds_and_invalid_optional_plan_is_never_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in (kit.INPUTS, kit.R1_SLOTS):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((kit.ROOT / path).read_bytes())
            sources = kit._read_frozen_sources(kit.ROOT)
            with patch.object(kit, '_read_frozen_sources', return_value=sources):
                before = kit.generate(root, source_root=root)
                target = root / kit.INPUTS
                stamp = target.stat()
                value = json.loads(target.read_bytes())
                value['WP15']['runtime_entrypoint'] = 'synthetic changed entrypoint'
                target.write_text(json.dumps(value))
                os.utime(target, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
                with patch.object(kit, 'build_files', wraps=kit.build_files) as build:
                    after = kit.generate(root, source_root=root)
                    build.assert_called_once()
                self.assertNotEqual(before[kit.KIT / 'collection_plan.json'],
                                    after[kit.KIT / 'collection_plan.json'])
                (root / kit.W1_PLAN).write_text('{}')
                with patch.object(kit, 'build_files', wraps=kit.build_files) as build:
                    for _ in range(2):
                        with self.assertRaises(ValueError):
                            kit.generate(root, source_root=root)
                    self.assertEqual(build.call_count, 2)

    def test_build_batches_historical_objects_and_is_byte_identical(self):
        # Independent legacy reader: a fresh git show for every request.
        legacy = lambda root, commit, path: subprocess.run(
            ['git', 'show', f'{commit}:{path}'], cwd=root,
            check=True, capture_output=True).stdout
        with patch.object(kit, 'frozen', side_effect=legacy):
            expected = kit.build_files()
        with patch.object(reg, '_git_blobs', wraps=reg._git_blobs) as batch:
            self.assertEqual(kit.build_files(), expected)
            self.assertEqual(batch.call_count, 1)

    def test_filled_synthetic_plan_and_sizing_are_byte_identical_when_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generation_fixture(root)
            legacy = lambda root, commit, path: subprocess.run(
                ['git', 'show', f'{commit}:{path}'], cwd=root,
                check=True, capture_output=True).stdout
            with patch.object(kit, 'frozen', side_effect=legacy):
                expected = kit.build_files(root)
            self.assertIn(kit.SIZING, expected)
            self.assertEqual(kit.generate(root, source_root=root), expected)
            with patch.object(kit, 'build_files', side_effect=AssertionError('cache missed')):
                self.assertEqual(kit.generate(root, source_root=root), expected)
            # Also prove the forced byte comparison succeeds before its fresh
            # readiness gate. A cached positive cannot suppress a later refusal.
            with patch.object(kit, 'require_w1_ready', side_effect=ValueError('synthetic live gate')) as ready:
                with self.assertRaisesRegex(ValueError, 'synthetic live gate'):
                    kit.generate(root, source_root=root, check=True)
                ready.assert_called_once_with(root)

    def test_corrupt_or_unwritable_cache_falls_back_to_regeneration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = kit.generate(root)
            for path in (root / 'build/align-v4-cache/generation').glob('*.json'):
                path.write_text('{broken')
            with patch.object(kit, 'build_files', wraps=kit.build_files) as build:
                self.assertEqual(kit.generate(root), expected)
                build.assert_called_once()
            for path in (root / 'build/align-v4-cache/generation').glob('*.json'):
                path.unlink()
            with patch.object(reg, '_cache_store', side_effect=OSError('read only')) as store:
                self.assertEqual(kit.generate(root), expected)
                store.assert_called_once()


class ReceiptCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.receipt = receipt_fixture(self.root)

    def test_only_success_is_cached_and_warm_hit_checks_current_bytes(self):
        with patch.object(reg, '_committed_bytes', wraps=reg._committed_bytes) as blobs:
            self.assertIs(reg.validate_receipt(self.receipt, self.root), self.receipt)
            self.assertIs(reg.validate_receipt(self.receipt, self.root), self.receipt)
            self.assertEqual(blobs.call_count, 1)
            path = self.root / reg.ARTIFACTS[-1]
            old, stamp = path.read_bytes(), path.stat()
            path.write_bytes(b'x' * len(old))
            os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
            for _ in range(2):
                with self.assertRaisesRegex(ValueError, 'digest drift'):
                    reg.validate_receipt(self.receipt, self.root)
            path.write_bytes(old)
            self.assertIs(reg.validate_receipt(self.receipt, self.root), self.receipt)

    def test_warm_hit_never_bypasses_signature_gate_commit_or_path_refusals(self):
        reg.validate_receipt(self.receipt, self.root)
        for change in ('signature', 'gate', 'commit', 'symlink', 'missing'):
            bad = deepcopy(self.receipt)
            target = self.root / reg.ARTIFACTS[0]
            old = target.read_bytes()
            if change == 'signature': bad['lead_signature'] = kit.UNSIGNED
            if change == 'gate': bad['gates']['A']['verdict'] = 'REFUSE'
            if change == 'commit': bad['commit'] = '0' * 40
            if change == 'missing': target.unlink()
            if change == 'symlink':
                target.unlink()
                target.symlink_to(self.root / reg.ARTIFACTS[1])
            with self.subTest(change=change), self.assertRaises(ValueError):
                reg.validate_receipt(bad, self.root)
            if change in ('symlink', 'missing'):
                if target.is_symlink(): target.unlink()
                target.write_bytes(old)

    def test_local_and_committed_drift_never_becomes_a_success(self):
        path = reg.ARTIFACTS[0]
        old = (self.root / path).read_bytes()
        (self.root / path).write_bytes(old + b'changed')
        bad = deepcopy(self.receipt)
        bad['artifacts'][path] = reg.digest((self.root / path).read_bytes())
        for _ in range(2):
            with self.assertRaisesRegex(ValueError, 'digest drift'):
                reg.validate_receipt(bad, self.root)
        (self.root / path).write_bytes(old)
        self.assertEqual(reg.validate_receipt(self.receipt, self.root), self.receipt)

    def test_blob_replacement_cannot_reuse_a_warm_success(self):
        reg.validate_receipt(self.receipt, self.root)
        path = reg.ARTIFACTS[0]
        original = git(self.root, 'rev-parse', f'{self.receipt["commit"]}:{path}')
        raw = (self.root / path).read_bytes()
        replacement = subprocess.run(['git', 'hash-object', '-w', '--stdin'], cwd=self.root,
                                     input=b'x' * len(raw), check=True, capture_output=True).stdout.decode().strip()
        git(self.root, 'replace', original, replacement)
        with self.assertRaisesRegex(ValueError, 'digest drift'):
            reg.validate_receipt(self.receipt, self.root)

    def test_force_bypasses_cache_and_unavailable_git_still_refuses(self):
        reg.validate_receipt(self.receipt, self.root)
        with patch.object(reg, '_committed_bytes', wraps=reg._committed_bytes) as blobs:
            reg.validate_receipt(self.receipt, self.root, cache=False)
            blobs.assert_called_once()
        with patch.object(reg, '_committed_oids', side_effect=ValueError('commit unreadable')):
            with self.assertRaisesRegex(ValueError, 'commit unreadable'):
                reg.validate_receipt(self.receipt, self.root)

    def test_refusal_is_not_persisted_and_corruption_is_a_miss(self):
        bad = deepcopy(self.receipt)
        bad['gates']['A']['verdict'] = 'REFUSE'
        with patch.object(reg, '_cache_store', wraps=reg._cache_store) as store:
            for _ in range(2):
                with self.assertRaises(ValueError):
                    reg.validate_receipt(bad, self.root)
            store.assert_not_called()
        reg.validate_receipt(self.receipt, self.root)
        for path in (self.root / 'build/align-v4-cache/receipt').glob('*.json'):
            path.write_text('{}')
        with patch.object(reg, '_committed_bytes', wraps=reg._committed_bytes) as blobs:
            reg.validate_receipt(self.receipt, self.root)
            blobs.assert_called_once()


class GitBatchTests(unittest.TestCase):
    def test_binary_empty_and_missing_blobs_preserve_framing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'binary').write_bytes(b'\x00\n\xffheader-looking blob 22\n')
            (root / 'empty').write_bytes(b'')
            git(root, 'init', '-q')
            git(root, 'add', '.')
            git(root, '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                'commit', '-qm', 'Binary fixture')
            commit = git(root, 'rev-parse', 'HEAD')
            self.assertEqual(reg._committed_bytes(root, commit, ['binary', 'empty', 'missing']),
                             {'binary': (root / 'binary').read_bytes(), 'empty': b'', 'missing': None})

    def test_truncated_or_unexpected_git_output_refuses(self):
        for raw in (b'', b'123 blob 100\nshort\n', b'123 tree 0\n\n'):
            with self.subTest(raw=raw), patch.object(reg.subprocess, 'run', return_value=
                    subprocess.CompletedProcess([], 0, stdout=raw, stderr=b'')):
                with self.assertRaisesRegex(ValueError, 'commit unreadable'):
                    reg._git_blobs('.', ['HEAD:synthetic'])


if __name__ == '__main__':
    unittest.main()
