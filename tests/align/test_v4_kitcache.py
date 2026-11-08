"""Fresh kit/receipt validation and batched reads on synthetic Git fixtures."""
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
    common = Path(git(kit.ROOT, 'rev-parse', '--path-format=absolute', '--git-common-dir'))
    (root / '.git/objects/info/alternates').write_text(str(common / 'objects') + '\n')
    files = kit.build_files(root)
    plan = filled_w1_plan(inputs, slots,
                          collection_plan=json.loads(files[kit.KIT / 'collection_plan.json']))
    (root / kit.W1_PLAN).write_bytes(kit.raw_json(plan))


class GenerationTests(unittest.TestCase):
    def test_repeated_generate_and_check_always_run_builder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = kit.generate(root)
            with patch.object(kit, 'build_files', wraps=kit.build_files) as build:
                self.assertEqual(kit.generate(root), first)
                build.assert_called_once_with(kit.ROOT)
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

    def test_changed_input_rebuilds_and_invalid_optional_plan_always_refuses(self):
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

    def test_filled_synthetic_plan_and_sizing_are_byte_identical_on_rebuild(self):
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
            with patch.object(kit, 'build_files', wraps=kit.build_files) as build:
                self.assertEqual(kit.generate(root, source_root=root), expected)
                build.assert_called_once_with(root)
            # Byte comparison succeeds before the fresh readiness gate, whose
            # refusal must still execute on a previously generated output root.
            with patch.object(kit, 'require_w1_ready', side_effect=ValueError('synthetic live gate')) as ready:
                with self.assertRaisesRegex(ValueError, 'synthetic live gate'):
                    kit.generate(root, source_root=root, check=True)
                ready.assert_called_once_with(root)

    def test_generation_fixture_resolves_common_objects_from_a_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, worktree, target = (root / name for name in ('source', 'worktree', 'target'))
            source.mkdir()
            target.mkdir()
            generation_fixture(source)
            git(source, 'add', '.')
            git(source, '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                'commit', '-qm', 'Synthetic worktree source')
            git(source, 'worktree', 'add', '-q', '--detach', str(worktree))
            self.assertTrue((worktree / '.git').is_file())
            with patch.object(kit, 'ROOT', worktree):
                generation_fixture(target)
            self.assertIn(kit.SIZING, kit.build_files(target))
            alternate = (target / '.git/objects/info/alternates').read_text().strip()
            self.assertEqual(Path(alternate), source / '.git/objects')

    def test_output_symlink_components_preserve_legacy_generation_and_check(self):
        # Both ends are synthetic directories under this test's temporary root.
        with tempfile.TemporaryDirectory() as tmp:
            root, destination = Path(tmp) / 'output', Path(tmp) / 'destination'
            root.mkdir()
            destination.mkdir()
            (root / 'configs').symlink_to(destination, target_is_directory=True)
            files = kit.generate(root)
            self.assertTrue(all((root / p).read_bytes() == raw for p, raw in files.items()))
            with self.assertRaisesRegex(ValueError, 'BLOCKED'):
                kit.generate(root, check=True)

    def test_invocation_snapshot_resets_after_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(kit, 'check_window_reference_roles', side_effect=ValueError('synthetic refusal')):
                with self.assertRaisesRegex(ValueError, 'synthetic refusal'):
                    kit.generate(root)
            with patch.object(kit, '_read_frozen_sources', wraps=kit._read_frozen_sources) as read:
                kit.generate(root)
                read.assert_called_once_with(kit.ROOT)


class ReceiptValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.receipt = receipt_fixture(self.root)

    def test_every_validation_rechecks_committed_and_working_bytes(self):
        with patch.object(reg, '_committed_bytes', wraps=reg._committed_bytes) as blobs:
            self.assertIs(reg.validate_receipt(self.receipt, self.root), self.receipt)
            self.assertIs(reg.validate_receipt(self.receipt, self.root), self.receipt)
            self.assertEqual(blobs.call_count, 2)
            path = self.root / reg.ARTIFACTS[-1]
            old, stamp = path.read_bytes(), path.stat()
            path.write_bytes(b'x' * len(old))
            os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
            for _ in range(2):
                with self.assertRaisesRegex(ValueError, 'digest drift'):
                    reg.validate_receipt(self.receipt, self.root)
            path.write_bytes(old)
            self.assertIs(reg.validate_receipt(self.receipt, self.root), self.receipt)

    def test_repeated_validation_never_bypasses_signature_gate_commit_or_path_refusals(self):
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

    def test_blob_replacement_after_success_still_refuses(self):
        reg.validate_receipt(self.receipt, self.root)
        path = reg.ARTIFACTS[0]
        original = git(self.root, 'rev-parse', f'{self.receipt["commit"]}:{path}')
        raw = (self.root / path).read_bytes()
        replacement = subprocess.run(['git', 'hash-object', '-w', '--stdin'], cwd=self.root,
                                     input=b'x' * len(raw), check=True, capture_output=True).stdout.decode().strip()
        git(self.root, 'replace', original, replacement)
        with self.assertRaisesRegex(ValueError, 'digest drift'):
            reg.validate_receipt(self.receipt, self.root)

    def test_working_drift_refuses_before_git_and_unavailable_git_refuses(self):
        reg.validate_receipt(self.receipt, self.root)
        target = self.root / reg.ARTIFACTS[-1]
        raw = target.read_bytes()
        target.write_bytes(raw + b'drift')
        with patch.object(reg, '_committed_bytes', wraps=reg._committed_bytes) as blobs:
            with self.assertRaisesRegex(ValueError, 'digest drift'):
                reg.validate_receipt(self.receipt, self.root)
            blobs.assert_not_called()
        target.write_bytes(raw)
        with patch.object(reg.subprocess, 'run', side_effect=OSError('synthetic Git unavailable')):
            with self.assertRaisesRegex(ValueError, 'commit unreadable'):
                reg.validate_receipt(self.receipt, self.root)


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
