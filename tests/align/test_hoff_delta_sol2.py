"""Independent delta review of 6938c3733. Synthetic inputs only.

Assertions describe the required behavior; unresolved findings stay red.
No B5 fixture, model, native measurement, or external custody is imported.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from tests.align import synthetic_custody
from joulewise.align.apple import harvest_offload as off
from scripts import align_v4_harvest_off as runner
from scripts import align_v4_next_arm_packet as builder
from tests.align.test_v4_next_arm_packet import Scenario

setUpModule, tearDownModule = synthetic_custody.setUpModule, synthetic_custody.tearDownModule
REAL_TMP = os.path.realpath(tempfile.gettempdir())


class Scratch(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='hoff-delta-sol2-', dir=REAL_TMP)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def checkout(self):
        """Real Git identity; interpreter/package probe is a fixed synthetic seam."""
        checkout = self.root / 'checkout'
        checkout.mkdir()
        (checkout / '.gitignore').write_text('.venv/\nruns/\n')
        (checkout / 'a.json').write_text('{"input":1}')
        (checkout / 'b.json').write_text('{"input":2}')
        (checkout / '.venv/bin').mkdir(parents=True)
        (checkout / '.venv/bin/python').write_text('synthetic interpreter seam; never executed')
        for args in (('init', '-q'), ('add', '.'), ('commit', '-qm', 'synthetic checkout')):
            subprocess.run(['git', '-c', 'user.name=Synthetic', '-c',
                            'user.email=synthetic@example.invalid', '-C', str(checkout), *args],
                           check=True, capture_output=True)
        return checkout

    @staticmethod
    def identity(checkout):
        def run(argv, **kwargs):
            if argv[0] == 'git':
                return subprocess.run(argv, **kwargs)
            return subprocess.CompletedProcess(argv, 0, stdout='synthetic-python\nsynthetic-packages\n')
        return runner.checkout_identity(checkout, run=run)


class ClosureTests(Scratch):
    def session(self):
        source = self.root / 'session'
        source.mkdir()
        (source / 'raw.txt').write_bytes(b'synthetic raw\n')
        return source

    def test_finalize_must_refuse_a_link_whose_immediate_target_is_another_link(self):
        source = self.session()
        target = self.root / 'input.json'
        target.write_text('{}')
        alias = self.root / 'alias'
        alias.symlink_to(target)
        (source / 'input').symlink_to(alias)
        with self.assertRaisesRegex(off.OffloadRefused, 'link'):
            off.finalized_manifest(source)

    @unittest.skipUnless(shutil.which('zstd'), 'zstd required')
    def test_mirror_link_target_must_remain_the_same_within_the_checkout(self):
        source = self.session()
        checkout = self.checkout()
        alias = self.root / 'selected-input'
        alias.symlink_to(checkout / 'a.json')
        (source / 'input').symlink_to(alias)
        identity = self.identity(checkout)
        finalized = off.finalized_manifest(source, mirror={'root': str(checkout), 'identity': identity})
        off.pack(source, self.root / 'offload', finalized=finalized, mirror_identity=identity)
        source.rename(self.root / 'kept')
        alias.unlink()
        alias.symlink_to(checkout / 'b.json')
        self.assertEqual(self.identity(checkout), identity)
        self.assertEqual(finalized['closure']['links']['input']['target'], str(checkout / 'a.json'))
        with self.assertRaises(off.OffloadRefused, msg='same Git identity does not bind a different selected file'):
            off.unpack(self.root / 'offload', finalized=finalized,
                       finalized_sha256=off.manifest_sha256(finalized), mirror_identity=self.identity(checkout))

    @unittest.skipUnless(shutil.which('zstd'), 'zstd required')
    def test_ignored_checkout_input_must_be_bound_or_refused(self):
        source = self.session()
        checkout = self.checkout()
        (checkout / 'runs').mkdir()
        ignored = checkout / 'runs/input.json'
        ignored.write_text('{"synthetic_input":1}')
        (source / 'input').symlink_to(ignored)
        identity = self.identity(checkout)
        finalized = off.finalized_manifest(source, mirror={'root': str(checkout), 'identity': identity})
        self.assertEqual(finalized['closure']['files'], {})
        off.pack(source, self.root / 'offload', finalized=finalized, mirror_identity=identity)
        source.rename(self.root / 'kept')
        ignored.write_text('{"synthetic_input":2}')
        self.assertEqual(self.identity(checkout), identity)  # real Git status ignores runs/
        with self.assertRaises(off.OffloadRefused, msg='an ignored input is outside the Git mirror binding'):
            off.unpack(self.root / 'offload', finalized=finalized,
                       finalized_sha256=off.manifest_sha256(finalized), mirror_identity=self.identity(checkout))

    @unittest.skipUnless(shutil.which('zstd'), 'zstd required')
    def test_declared_external_parent_retarget_must_not_write_into_checkout_code(self):
        source = self.session()
        checkout = self.checkout()
        (checkout / 'runs').mkdir()
        code = checkout / 'a.json'
        original = code.read_bytes()
        (checkout / 'runs/a.json').write_bytes(original + b'\n{"ledger":1}\n')
        alias = self.root / 'ledger-directory'
        alias.symlink_to(checkout / 'runs', target_is_directory=True)
        ledger = alias / 'a.json'
        (source / 'measurement').symlink_to(checkout, target_is_directory=True)
        identity = self.identity(checkout)
        finalized = off.finalized_manifest(source, mirror={'root': str(checkout), 'identity': identity},
                                           inputs=(ledger,))
        off.pack(source, self.root / 'offload', finalized=finalized, external=(ledger,), mirror_identity=identity)
        source.rename(self.root / 'kept')
        alias.unlink()
        alias.symlink_to(checkout, target_is_directory=True)
        self.assertEqual(self.identity(checkout), identity)
        refused = False
        try:
            off.unpack(self.root / 'offload', finalized=finalized,
                       finalized_sha256=off.manifest_sha256(finalized), mirror_identity=self.identity(checkout))
        except off.OffloadRefused:
            refused = True
        self.assertEqual(code.read_bytes(), original, 'external placement wrote through a retargeted parent')
        self.assertTrue(refused, 'declared external destinations must have stable real parent directories')

    def test_external_directory_scan_errors_must_not_be_bound_as_empty(self):
        source = self.session()
        directory = self.root / 'external'
        directory.mkdir()
        (directory / 'input').write_bytes(b'input')
        (source / 'external').symlink_to(directory, target_is_directory=True)
        original = os.scandir

        def scandir(path):
            if Path(path) == directory:
                raise PermissionError('synthetic unreadable directory')
            return original(path)

        with mock.patch.object(os, 'scandir', side_effect=scandir):
            with self.assertRaises((off.OffloadRefused, PermissionError)):
                off.finalized_manifest(source)

    def test_all_three_byte_closure_limits_refuse_before_hashing_the_offending_file(self):
        source = self.session()
        directory = self.root / 'external'
        directory.mkdir()
        for name in ('a', 'b'):
            (directory / name).write_bytes(b'x' * 16)
        (source / 'external').symlink_to(directory, target_is_directory=True)
        for field, limit in (('CLOSURE_MAX_FILES', 1), ('CLOSURE_MAX_BYTES', 24),
                             ('CLOSURE_MAX_FILE_BYTES', 8)):
            with self.subTest(field=field), mock.patch.object(off, field, limit):
                with mock.patch.object(off, '_file_sha256', wraps=off._file_sha256) as hashing:
                    with self.assertRaises(off.OffloadRefused):
                        off.finalized_manifest(source)
                external_calls = [call for call in hashing.call_args_list if call.args[0].parent == directory]
                self.assertEqual(len(external_calls), 0 if field == 'CLOSURE_MAX_FILE_BYTES' else 1)

    def test_22_links_to_one_external_directory_hash_each_external_file_once(self):
        source = self.session()
        directory = self.root / 'external'
        directory.mkdir()
        target = directory / 'journal'
        target.write_bytes(b'synthetic\n' * 1024)
        for index in range(22):
            (source / f'member-{index:02d}').symlink_to(directory, target_is_directory=True)
        with mock.patch.object(off, '_file_sha256', wraps=off._file_sha256) as hashing, \
             mock.patch.object(off, '_directory_listing', wraps=off._directory_listing) as listing:
            finalized = off.finalized_manifest(source)
        self.assertEqual(sum(call.args[0] == target for call in hashing.call_args_list), 1)
        self.assertEqual(len(finalized['closure']['files']), 1)
        self.assertEqual(listing.call_count, 22)  # repeated scans remain even though file hashing deduplicates


class FinalityTests(Scratch):
    def test_only_supplemental_captures_still_need_a_completed_harvest(self):
        w1 = Scenario(self.root, 'W1').finish()
        c1 = Scenario(self.root, 'C1', previous=w1, captured=False)
        for index in range(2):
            planned = deepcopy(c1.members[0])
            planned.update(run_id=f'supplemental-{index}', supplemental=True, role='sentinel')
            thermal = deepcopy(c1.thermal['members'][0])
            thermal.update(id=planned['run_id'], role='sentinel', excluded=False, calibration_exclusions=[])
            c1.members.append(planned)
            c1.thermal['members'].append(thermal)
        c1.sources['desk']['harvest_status'] = 'not_run'
        c1.finish()
        record = builder.WindowRecord(builder.GitEvidence(self.root), c1.record_commit, c1.record_path)
        self.assertEqual(len(record.captures()), 2)
        self.assertEqual(record.counted_captures(), 0)
        self.assertFalse(record.is_final(), 'supplemental captures have raw bytes a harvest must adjudicate')

    def test_final_command_must_not_publish_a_non_adjudicated_pilot_as_final(self):
        session = self.root / 'session'
        session.mkdir()
        (session / 'PILOT.json').write_text(json.dumps({'plan_id': 'synthetic', 'status': 'running',
            'extra_checks': {'thermal': {'members': [], 'model_windows': {}}}}))
        (session / 'desk.json').write_text(json.dumps({'plan_id': 'synthetic', 'harvest_status': 'ok'}))
        args = SimpleNamespace(session_root=session, pilot=None, window_id='C1')
        with mock.patch.object(runner, '_session', return_value=(session, {'session_id': 'synthetic'}, {})), \
             mock.patch.object(runner, '_plan_rows', return_value=[]), \
             mock.patch.object(runner, '_runs_root', return_value=session / 'runs'):
            with self.assertRaises(ValueError, msg='cmd_final should enforce the same PILOT finality as the record'):
                runner.cmd_final(args)


class SweepTests(Scratch):
    def receipt(self, code):
        path = self.root / 'SWEEP.json'
        path.write_text(json.dumps({'schema': runner.SWEEP_SCHEMA, 'largest_plist_bytes': 100,
            'code': code, 'runs': [{'workers': 2, 'exit': 0, 'peak_child_rss_bytes': 200}]}))
        return path

    def test_sweep_from_a_dirty_checkout_must_not_bind_to_unchanged_head(self):
        identity = {'head': 'a' * 40, 'python': ['synthetic-python', 'packages'], 'tracked_clean': False}
        state = {'measurement_root': str(self.root)}
        with mock.patch.object(runner, '_session', return_value=(self.root, state, {})), \
             mock.patch.object(runner, 'checkout_identity', return_value=identity), \
             mock.patch.object(runner, 'largest_plist_bytes', return_value=100):
            code = runner.sweep_code_identity(self.root)
            peak, basis = runner.sweep_basis(self.receipt(code), self.root)
        self.assertIsNone(peak, f'dirty code was accepted as a bound peak: {basis}')

    def test_unidentified_interpreter_must_not_bind_a_sweep(self):
        code = {'head': 'a' * 40, 'python': None}
        with mock.patch.object(runner, 'sweep_code_identity', return_value=code), \
             mock.patch.object(runner, 'largest_plist_bytes', return_value=100):
            peak, basis = runner.sweep_basis(self.receipt(code), self.root)
        self.assertIsNone(peak, f'missing interpreter identity was accepted: {basis}')


class FenceTests(unittest.TestCase):
    def test_fence_survives_a_fresh_python_process_for_non_backup_custody(self):
        # Path TEXT only. The child invokes the pure resolver; it performs no stat/open of this locator.
        locator = str(synthetic_custody.HOME / 'night-custody/synthetic-never-probed')
        code = ("import json; from pathlib import Path; "
                "from joulewise.calibration_ledger import _custody_probe_paths; "
                "print(json.dumps([str(p) for p in _custody_probe_paths("
                f"Path({locator!r}), mode='read_replay')]))")
        with synthetic_custody.fence():
            child = subprocess.run([sys.executable, '-B', '-c', code], check=True,
                                   capture_output=True, text=True)
        self.assertEqual(json.loads(child.stdout), [], 'environment shortcut fences only BACKUP_ROOTS in a child')

    def test_audit_must_report_filesystem_bytes_paths(self):
        # Invoke the audit hook with a synthetic event; never make the filesystem operation.
        before = len(synthetic_custody.OPENED)
        locator = os.fsencode(synthetic_custody.HOME / 'night-custody/synthetic-never-opened')
        with mock.patch.object(synthetic_custody, '_AUDITING', [True]):
            synthetic_custody._audit('open', (locator, 'r', 0))
        observed = synthetic_custody.OPENED[before:]
        del synthetic_custody.OPENED[before:]
        self.assertTrue(observed, 'bytes path opens evade the advertised audit counter')


if __name__ == '__main__':
    unittest.main()
