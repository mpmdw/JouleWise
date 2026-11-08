"""Adversarial portable-record bindings, using synthetic finalized exports only."""
from contextlib import redirect_stdout
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple import desk_record as dr
from joulewise.align.apple.desk_execution import DeskExecution, host_desk_guard
from scripts import bytes_h_session as h
from tests.align.desk_record_fixture import passing_artifact, seal, successful_desk
from tests.align import test_desk_parallel as desk_fixture


class RecordBindings(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo, self.commit, self.inputs, self.layout = desk_fixture.CommittedRecordTests().record(self.root)
        self.output = self.root/'output'

    def replay(self, **kwargs):
        with redirect_stdout(io.StringIO()):
            return dr.replay(self.repo, self.commit, 'record.json', self.inputs, self.output, **kwargs)

    def reseal(self):
        self.commit = seal(self.repo, self.inputs, self.layout)

    def test_unpushed_commit_refuses(self):
        dr._git(self.repo, 'update-ref', '-d', self.layout['records_ref'])
        with self.assertRaises(subprocess.CalledProcessError):
            self.replay()
        self.assertFalse(self.output.exists())

    def test_unrelated_pushed_tip_refuses_even_with_a_local_descriptor_commit(self):
        # A sibling commit exists locally, but is not on the records ref.
        dr._git(self.repo, 'checkout', '--orphan', 'other')
        dr._git(self.repo, '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=Synthetic',
                '-c', 'user.email=synthetic@example.invalid', 'commit', '-qm', 'unrelated')
        dr._git(self.repo, 'update-ref', self.layout['records_ref'], 'HEAD')
        with self.assertRaises(subprocess.CalledProcessError):
            self.replay()

    def test_manifest_cannot_be_replaced_by_laptop_inventory(self):
        (self.inputs/'plan.json').write_text('{}')
        value = dr.describe(self.inputs, self.layout, repository=self.repo)
        h.write(self.repo/'record.json', value)
        dr._git(self.repo, 'add', 'record.json')
        dr._git(self.repo, '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=Synthetic',
                '-c', 'user.email=synthetic@example.invalid', 'commit', '-qm', 'forged descriptor')
        self.commit = dr._git(self.repo, 'rev-parse', 'HEAD').decode().strip()
        dr._git(self.repo, 'update-ref', self.layout['records_ref'], self.commit)
        with self.assertRaisesRegex(ValueError, 'finalize manifest'):
            self.replay()

    def test_failed_or_unrecorded_harvest_cannot_be_finalized(self):
        for status, code in (('program_fault', 1), ('not_run', None), ('ok', 1), ('members_excluded', 6)):
            with self.subTest(status=status, code=code):
                h.write(self.inputs/'session/desk.json', {'plan_id': 'synthetic',
                    'harvest_status': status, 'harvest_exit': code})
                with self.assertRaisesRegex(ValueError, 'harvest success'):
                    dr.finalize(self.inputs, self.layout)

    def test_archive_changes_and_forged_receipt_digests_refuse(self):
        path = self.inputs/'session/archive/derived/exclusions.json'
        path.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            self.replay()
        self.assertFalse(self.output.exists())

    def test_manifest_harvest_archive_digests_must_match_inventory(self):
        manifest = h.read(self.repo/'finalize.json')
        name = next(iter(manifest['harvest']['archive_files']))
        manifest['harvest']['archive_files'][name] = '0'*64
        h.write(self.repo/'finalize.json', manifest)
        h.write(self.repo/'record.json', dr.describe(self.inputs, self.layout, repository=self.repo))
        dr._git(self.repo, 'add', 'record.json', 'finalize.json')
        dr._git(self.repo, '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=Synthetic',
                '-c', 'user.email=synthetic@example.invalid', 'commit', '-qm', 'invalid manifest')
        self.commit = dr._git(self.repo, 'rev-parse', 'HEAD').decode().strip()
        dr._git(self.repo, 'update-ref', self.layout['records_ref'], self.commit)
        with self.assertRaisesRegex(ValueError, 'finalize/harvest binding'):
            self.replay()

    def test_pack_config_locators_cannot_escape_export(self):
        state = h.read(self.inputs/'session/session.json')
        state['inputs']['pack_root'] = '/unavailable/pack'
        h.write(self.inputs/'session/session.json', state)
        self.layout['pack_root'] = 'pack'
        h.write(self.inputs/'pack/extraction_spec.json', {'cells': []})
        for path in ('/unavailable/config.json', '../config.json', 'restricted/config.json'):
            h.write(self.inputs/'pack/plan_tree.json', {'science': [{'run_id': 'm000', 'config_path': path}]})
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'relative contained path'):
                dr.finalize(self.inputs, self.layout)

    def test_pack_without_target_definition_refuses_instead_of_using_fallback_targets(self):
        state = h.read(self.inputs/'session/session.json')
        state['inputs']['pack_root'] = '/unavailable/pack'
        h.write(self.inputs/'session/session.json', state)
        self.layout['pack_root'] = 'pack'
        h.write(self.inputs/'pack/plan_tree.json', {'science': []})
        with self.assertRaisesRegex(ValueError, 'pack/extraction_spec.json or pack/analysis_manifest_v3.json'):
            dr.finalize(self.inputs, self.layout)

    def test_missing_layout_files_are_named_even_when_inventory_omits_them(self):
        for relative in ('custody/collection/run_clock.jsonl', 'custody/hazards/monitor/thermal.jsonl',
                         'custody/hazards/meter/stream-0.jsonl', 'session/staging/harvest.stdout'):
            with self.subTest(path=relative):
                path = self.inputs/relative
                raw = path.read_bytes()
                path.unlink()
                with self.assertRaisesRegex(ValueError, relative):
                    dr.finalize(self.inputs, self.layout)
                path.write_bytes(raw)

    def test_session_and_plan_must_match_terminal_result(self):
        for target in ('plan.json', 'custody/night/result.json', 'session/session.json'):
            with self.subTest(target=target):
                path = self.inputs/target
                raw = path.read_bytes()
                value = json.loads(raw)
                value['session_id' if target.endswith('session.json') else 'plan_id'] = 'other-window'
                h.write(path, value)
                with self.assertRaisesRegex(ValueError, 'night/result.json'):
                    dr.finalize(self.inputs, self.layout)
                path.write_bytes(raw)

    def test_targets_are_recomputed_with_build_roster_and_mismatch_refuses(self):
        state = h.read(self.inputs/'session/session.json')
        state['inputs']['pack_root'] = '/unavailable/pack'
        h.write(self.inputs/'session/session.json', state)
        self.layout['pack_root'] = 'pack'
        rows = h.read(self.inputs/'measurement/configs/campaigns/align_v4/collection_plan.json')['members']
        h.write(self.inputs/'pack/plan_tree.json', {'science': [
            {'run_id': m['run_id'], 'stage_id': 's', 'role': 'absolute_repeat', 'config_path': 'config.json'}
            for m in rows]})
        h.write(self.inputs/'pack/config.json', {})
        h.write(self.inputs/'pack/extraction_spec.json', {'cells': [{'cell_id': 'c', 'kind': 'absolute',
            'target_precheck_path': ['gross_request'], 'members': [{'bundle_id': m['run_id']} for m in rows]}]})
        value = dr.describe(self.inputs, self.layout, repository=self.repo)
        targets = dr._targets(self.inputs, value)
        self.assertEqual(targets, {m['run_id']: [['gross_request']] for m in rows})
        self.layout['targets'] = {m['run_id']: [] for m in rows}
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            self.reseal()
        self.layout['targets'] = targets
        self.reseal()
        with patch('scripts.align_pilot_session._desk', successful_desk):
            self.assertEqual(self.replay()['harvest_status'], 'ok')

    def test_profile_failure_prevents_publication_and_preserves_original_error(self):
        profile = self.root/'profile.json'
        original = Path.open
        def broken(path, *args, **kwargs):
            if path == profile and args == ('x',):
                raise OSError('profile fault')
            return original(path, *args, **kwargs)
        with patch('scripts.align_pilot_session._desk', successful_desk), patch.object(Path, 'open', broken), \
                self.assertRaisesRegex(OSError, 'profile fault'):
            self.replay(profile=profile)
        self.assertFalse(self.output.exists())
        with self.assertRaisesRegex(ValueError, 'original'):
            with DeskExecution(1, profile):
                profile.write_text('racing writer')
                raise ValueError('original')

    def test_publication_does_not_replace_a_racing_empty_directory(self):
        staging = self.root/'staged'
        staging.mkdir()
        (staging/'PILOT.json').write_text('synthetic')
        self.output.mkdir()
        with self.assertRaises(FileExistsError):
            dr._publish(staging, self.output)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_cli_emits_gate_binding_only_for_a_successful_replay(self):
        from scripts.align_v4_record_desk import main
        evidence = self.root/'gate.json'
        with patch('scripts.align_pilot_session._desk', successful_desk), redirect_stdout(io.StringIO()):
            code = main(['--repository', str(self.repo), '--commit', self.commit, '--record', 'record.json',
                         '--inputs', str(self.inputs), '--output', str(self.output), '--gate-evidence', str(evidence)])
        self.assertEqual(code, 0)
        self.assertTrue(dr.validate_gate(h.read(evidence), 'synthetic'))


class GateBindings(unittest.TestCase):
    def test_gate_checks_report_bytes_record_identity_and_harvest(self):
        with tempfile.TemporaryDirectory() as td:
            artifact = passing_artifact(Path(td))
            self.assertTrue(dr.validate_gate(artifact, 'synthetic'))
            for field, value in (('record_commit', '0'*40), ('harvest_status', 'not_run'),
                                 ('records_ref', 'refs/remotes/origin/records/other')):
                with self.subTest(field=field), self.assertRaises((ValueError, subprocess.SubprocessError)):
                    dr.validate_gate({**artifact, field: value}, 'synthetic')
            with self.assertRaisesRegex(ValueError, 'previous window'):
                dr.validate_gate(artifact, 'different')
            path = Path(artifact['reports']['PILOT.json']['path'])
            path.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'digest mismatch'):
                dr.validate_gate(artifact, 'synthetic')

    def test_rehashed_replay_cannot_claim_a_failed_or_unrecorded_harvest(self):
        with tempfile.TemporaryDirectory() as td:
            artifact = passing_artifact(Path(td))
            path = Path(artifact['reports']['REPLAY.json']['path'])
            original = path.read_bytes()
            for fault in ('not_run', 'program_fault', 'wrong_archive'):
                receipt = json.loads(original)
                if fault == 'wrong_archive':
                    name = next(iter(receipt['harvest']['archive_files']))
                    receipt['harvest']['archive_files'][name] = '0'*64
                else:
                    receipt['harvest_status'] = fault
                h.write(path, receipt)
                changed = copy.deepcopy(artifact)
                changed['reports']['REPLAY.json']['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                with self.subTest(fault=fault), self.assertRaisesRegex(ValueError, 'successful harvest'):
                    dr.validate_gate(changed, 'synthetic')


class HostGuardTests(unittest.TestCase):
    def test_live_lock_loaded_job_and_unknown_job_refuse_before_work(self):
        absent = f'Could not find service "com.joulewise.night" in domain for user gui: {os.getuid()}'
        for held, code, stderr in ((False, 113, absent), (True, 0, ''), (True, 113, 'unexpected'),
                                   (True, 1, 'unavailable')):
            with self.subTest(lock=held, code=code, stderr=stderr), \
                    patch('joulewise.align.apple.desk_execution.sys.platform', 'darwin'), \
                    patch('joulewise.align.apple.powermode.HostLock') as lock, \
                    patch('joulewise.align.apple.desk_execution.subprocess.run', return_value=SimpleNamespace(
                        returncode=code, stderr=stderr)):
                lock.return_value.acquire.return_value = held
                with self.assertRaisesRegex(ValueError, 'parallel desk refused'):
                    with host_desk_guard(2):
                        self.fail('live window entered desk')
                lock.return_value.release.assert_called_once()

    def test_lock_is_held_until_desk_finishes(self):
        with patch('joulewise.align.apple.desk_execution.sys.platform', 'darwin'), \
                patch('joulewise.align.apple.powermode.HostLock') as lock, \
                patch('joulewise.align.apple.desk_execution.subprocess.run', return_value=SimpleNamespace(
                    returncode=113, stderr=f'Could not find service "com.joulewise.night" in domain for user gui: {os.getuid()}')):
            with host_desk_guard(2):
                lock.return_value.release.assert_not_called()
            lock.return_value.release.assert_called_once()

    def test_v4_entry_guard_refuses_before_pilot_reads(self):
        from scripts import align_v4_session as v4
        with patch('joulewise.align.apple.desk_execution.host_desk_guard', side_effect=ValueError('armed')), \
                patch('scripts.align_pilot_session.desk') as pilot, self.assertRaisesRegex(ValueError, 'armed'):
            v4.desk('/unavailable/session', workers=2)
        pilot.assert_not_called()


if __name__ == '__main__':
    unittest.main()
