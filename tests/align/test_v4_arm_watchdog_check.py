"""W-1/W-2: synthetic plists and injected commands only; no host probes."""
from contextlib import ExitStack
import ast
import contextlib
import datetime as dt
import io
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from xml.sax.saxutils import escape

from joulewise.align.apple import powermode
from scripts import align_v4_session as session
from tests import test_magistrate_watchdog as watchdog_fixtures


def acceptance(*, phase, **_):
    """Explicit seam for older witnesses that isolate other arm gates."""
    return {'ok': True, 'state': 'ACTIVE' if phase == 'post_install' else 'LAUNCHING',
            'reason': 'synthetic watchdog', 'argv': ['synthetic-watchdog', '--dry-run'],
            'elapsed_s': 0.0, 'plan_read_proven': False}


class WeightDigestTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.weights = self.root / 'tiny-weights'
        self.weights.mkdir()
        (self.weights / 'model.safetensors').write_bytes(b'fixture')
        self.members = [{'model_id': 'tiny', 'run_id': 'one'}, {'model_id': 'tiny', 'run_id': 'two'}]
        self.observed = {'status': 'ok', 'kind': 'file_set', 'folded_sha256': 'a' * 64,
                         'files': {'model.safetensors': 'b' * 64},
                         'inventory': [{'path': 'model.safetensors', 'size_bytes': 7}]}
        self.inventory = {'artifacts': {session.pilot.h.align_unit_id(m['model_id'], m['run_id']):
            dict(self.observed, root=str(self.weights)) for m in self.members}}
        self.state = {'measurement_root': str(self.root), 'source_measurement_root': str(self.root),
                      'registration_dir': str(self.root / session.kit.KIT / 'registration'),
                      'preparation_status': 'STAGED'}
        self.write_inputs()

    def write_inputs(self):
        directory = Path(self.state['registration_dir'])
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'model_artifact_inventory.json').write_text(json.dumps(self.inventory))
        (directory.parent / 'collection_plan.json').write_text(json.dumps({'members': self.members}))

    def preflight(self, observed=None):
        self.identity = Mock(return_value=self.observed if observed is None else observed)
        return session.weight_digest_preflight(self.state, identity_fn=self.identity)

    def test_shared_root_hashed_once_and_unplanned_inventory_ignored(self):
        self.inventory['artifacts']['unplanned'] = {'root': '/synthetic/never-read'}
        self.write_inputs()
        row = self.preflight()
        self.assertTrue(row['ok'], row)
        self.identity.assert_called_once_with(str(self.weights))
        root = row['roots'][str(self.weights)]
        self.assertEqual(root['registered_folded_sha256'], 'a' * 64)
        self.assertEqual(root['observed_folded_sha256'], 'a' * 64)
        self.assertEqual((root['file_count'], root['total_bytes']), (1, 7))
        self.assertTrue(root['ok'])
        self.assertGreaterEqual(root['elapsed_s'], 0)
        self.assertIsInstance(row['prepared_at_epoch_s'], (float, int))

    def test_every_shared_unit_digest_is_compared(self):
        self.inventory['artifacts']['tiny-two']['folded_sha256'] = 'c' * 64
        self.write_inputs()
        row = self.preflight()
        self.assertFalse(row['ok'])
        self.assertIn('weight_digest_preflight: digest_mismatch: tiny-two tiny-weights', row['reasons'])
        self.identity.assert_called_once()

    def test_missing_inventory_row_refuses(self):
        del self.inventory['artifacts']['tiny-two']
        self.write_inputs()
        row = self.preflight()
        self.assertFalse(row['ok'])
        self.assertIn('weight_digest_preflight: no_inventory_row: tiny-two', row['reasons'])

    def test_changed_digest_refuses(self):
        row = self.preflight(dict(self.observed, folded_sha256='c' * 64))
        self.assertIn('weight_digest_preflight: digest_mismatch: tiny-one tiny-weights', row['reasons'])
        self.assertFalse(row['roots'][str(self.weights)]['ok'])

    def test_each_file_map_change_refuses_even_with_matching_fold(self):
        for files, added, missing, changed in (
                ({'model.safetensors': 'b' * 64, 'extra.bin': 'c' * 64}, ['extra.bin'], [], []),
                ({}, [], ['model.safetensors'], []),
                ({'renamed.safetensors': 'b' * 64}, ['renamed.safetensors'], ['model.safetensors'], []),
                ({'model.safetensors': 'c' * 64}, [], [], ['model.safetensors'])):
            with self.subTest(files=files):
                row = self.preflight(dict(self.observed, files=files))
                self.assertIn('weight_digest_preflight: file_set_differs: tiny-weights', row['reasons'])
                self.assertEqual(row['roots'][str(self.weights)]['file_set_diff'],
                                 {'added': added, 'missing': missing, 'changed': changed})
                self.assertFalse(row['ok'])

    def test_every_shared_unit_file_map_is_compared(self):
        self.inventory['artifacts']['tiny-two'] = dict(self.inventory['artifacts']['tiny-two'], files={})
        self.write_inputs()
        self.assertFalse(self.preflight()['ok'])

    def test_unavailable_reasons_and_wrong_kind_refuse(self):
        for reason in ('model weight file is unreadable', 'model inventory changed during read',
                       'cannot enumerate model directory'):
            with self.subTest(reason=reason):
                row = self.preflight({'status': 'unavailable', 'reason': reason})
                self.assertEqual(row['reasons'], [f'weight_digest_preflight: unavailable: tiny-weights: {reason}'])
        row = self.preflight(dict(self.observed, kind='single_file'))
        self.assertFalse(row['ok'])
        self.assertIn('weight_digest_preflight: unavailable: tiny-weights:', row['reasons'][0])

    def test_identity_exception_is_a_recorded_unavailable(self):
        with patch('joulewise.provenance.model_artifact_identity', side_effect=OSError('synthetic read failure')):
            row = session.weight_digest_preflight(self.state)
        self.assertIn('weight_digest_preflight: unavailable: tiny-weights: OSError: synthetic read failure',
                      row['reasons'])

    def test_member_and_inventory_order_independent(self):
        other = self.root / 'other-tiny-weights'
        other.mkdir()
        (other / 'model.safetensors').write_bytes(b'fixture')
        self.inventory['artifacts']['tiny-two'] = dict(self.inventory['artifacts']['tiny-two'], root=str(other))
        self.write_inputs()
        with patch.object(session.time, 'time', return_value=10), \
                patch.object(session.time, 'monotonic', return_value=20):
            first = self.preflight()
            self.members.reverse()
            self.inventory['artifacts'] = dict(reversed(list(self.inventory['artifacts'].items())))
            self.write_inputs()
            self.assertEqual(first, self.preflight())
            self.assertEqual(self.identity.call_count, 2)

    def test_real_identity_on_tiny_tree_and_extra_shard(self):
        from joulewise.provenance import model_artifact_identity
        (self.weights / 'model.safetensors').write_bytes(b'tiny synthetic weights')
        real = model_artifact_identity(str(self.weights))
        self.inventory['artifacts'] = {unit: real for unit in self.inventory['artifacts']}
        self.write_inputs()
        self.assertTrue(session.weight_digest_preflight(self.state)['ok'])
        (self.weights / 'extra.bin').write_bytes(b'extra synthetic shard')
        row = session.weight_digest_preflight(self.state)
        self.assertFalse(row['ok'])
        self.assertEqual(row['roots'][str(self.weights)]['file_set_diff']['added'], ['extra.bin'])

    def test_prepare_persists_refusal_and_never_enters_arm_dwell(self):
        with ExitStack() as stack:
            stack.enter_context(patch.object(powermode, 'host_lock_preflight', return_value={'ok': True}))
            stack.enter_context(patch.object(session, 'session_start_restore', return_value={'action': 'none'}))
            stack.enter_context(patch.object(session.kit, 'generate'))
            stack.enter_context(patch.object(session, 'series_ac_powermode', return_value=0))
            stack.enter_context(patch.object(session.pilot, 'prepare', return_value=self.state))
            arm = stack.enter_context(patch.object(session, 'arm_checks', side_effect=AssertionError('arm in prepare')))
            for mismatch in (True, False):
                identity = Mock(return_value=dict(self.observed, folded_sha256=('c' if mismatch else 'a') * 64))
                if mismatch:
                    with self.assertRaisesRegex(ValueError, 'weight_digest_preflight: digest_mismatch:'):
                        session.prepare(self.root, self.root / 'session', weight_identity_fn=identity,
                                        frequency_preflight=lambda *a, **k: {'ok': True})
                else:
                    session.prepare(self.root, self.root / 'session', weight_identity_fn=identity,
                                    frequency_preflight=lambda *a, **k: {'ok': True})
                stored = session.pilot.h.read(self.root / 'session/session.json')['weight_digest_preflight']
                self.assertEqual(stored['ok'], not mismatch)
                identity.assert_called_once()
            arm.assert_not_called()

    def test_early_model_presence_or_row_refusal_also_records_weight_evidence(self):
        for fault in ('missing_shard', 'renamed_shard', 'unreadable_shard', 'missing_row'):
            with self.subTest(fault=fault), ExitStack() as stack:
                self.write_inputs()
                observed = dict(self.observed, files={} if fault == 'missing_shard' else
                                {'renamed.safetensors': 'b' * 64})
                if fault == 'unreadable_shard':
                    observed = {'status': 'unavailable', 'reason': 'synthetic unreadable shard'}
                if fault == 'missing_row':
                    del self.inventory['artifacts']['tiny-two']
                    self.write_inputs()
                target = self.root / fault
                stack.enter_context(patch.object(powermode, 'host_lock_preflight', return_value={'ok': True}))
                stack.enter_context(patch.object(session, 'session_start_restore', return_value={'action': 'none'}))
                stack.enter_context(patch.object(session.kit, 'generate'))
                stack.enter_context(patch.object(session, 'series_ac_powermode', return_value=0))
                error = (KeyError('tiny-two') if fault == 'missing_row' else PermissionError('synthetic unreadable shard')
                         if fault == 'unreadable_shard' else session.pilot.h.PhysicalHazard('models missing: synthetic'))
                stack.enter_context(patch.object(session.pilot, 'prepare', side_effect=error))
                code = ('no_inventory_row' if fault == 'missing_row' else 'unavailable'
                        if fault == 'unreadable_shard' else 'file_set_differs')
                with self.assertRaisesRegex(ValueError, 'weight_digest_preflight: ' + code):
                    session.prepare(self.root, target, weight_identity_fn=lambda _: observed)
                stored = session.pilot.h.read(target / 'session.json')['weight_digest_preflight']
                self.assertFalse(stored['ok'])
                if fault in ('missing_shard', 'renamed_shard'):
                    self.assertIn('model.safetensors', stored['roots'][str(self.weights)]['file_set_diff']['missing'])
                preserved = target / 'preserved.txt'
                preserved.write_text('keep')
                before = (target / 'session.json').read_bytes()
                with self.assertRaises(type(error)):
                    session.prepare(self.root, target, weight_identity_fn=lambda _: observed)
                self.assertEqual(preserved.read_text(), 'keep')
                self.assertEqual((target / 'session.json').read_bytes(), before)


class RuntimeStackTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.versions = {'python': '3.13.1', 'packages': {'mlx': '0.31.2', 'numpy': '2.5.1'}}
        self.pins = self.root / session.kit.KIT / 'registration/identity_pins.json'
        self.pins.parent.mkdir(parents=True)
        self.pins.write_text(json.dumps({'runtime_versions': self.versions}))
        self.python = str(self.root / '.venv/bin/python')

    def check(self, observed=None, **kwargs):
        self.runner = Mock(return_value=self.versions if observed is None else observed)
        return session.runtime_stack_preflight(self.python, self.pins, runner=self.runner, **kwargs)

    def test_matching_uses_measurement_interpreter_and_reader(self):
        reader = Mock(return_value={'runtime_versions': self.versions})
        row = self.check(reader=reader)
        self.assertTrue(row['ok'], row)
        self.runner.assert_called_once_with(self.python)
        reader.assert_called_once_with(self.pins)
        self.assertEqual(row['registered'], self.versions)
        self.assertEqual(row['observed'], self.versions)
        self.assertGreaterEqual(row['elapsed_s'], 0)

    def test_python_each_package_missing_and_extra_are_compared(self):
        for observed, expected in (
                ({'python': '3.13.2', 'packages': {'mlx': 'changed', 'numpy': '2.5.1'}},
                 ['python: registered 3.13.1 installed 3.13.2', 'mlx: registered 0.31.2 installed changed']),
                ({'python': '3.13.1', 'packages': {'numpy': '2.5.1', 'extra': '1'}},
                 ['mlx: registered 0.31.2 installed <missing>', 'extra: registered <missing> installed 1'])):
            with self.subTest(observed=observed):
                row = self.check(observed)
                self.assertFalse(row['ok'])
                self.assertCountEqual(row['reasons'], ['runtime_stack_preflight: differs: ' + r for r in expected])

    def test_unreadable_versions_and_probe_or_reader_errors_refuse(self):
        for value in (None, '', 3, {}, []):
            row = self.check({'python': '3.13.1', 'packages': {'mlx': value, 'numpy': '2.5.1'}})
            self.assertFalse(row['ok'])
            self.assertTrue(any(': unreadable:' in r for r in row['reasons']), row)
        for runner, reader in ((Mock(side_effect=OSError('probe failed')), session.pilot.h.read),
                               (Mock(), Mock(side_effect=ValueError('pins failed')))):
            row = session.runtime_stack_preflight(self.python, self.pins, runner=runner, reader=reader)
            self.assertFalse(row['ok'])
            self.assertIn('runtime_stack_preflight: unreadable:', row['reasons'][0])

    def test_prepare_persists_stack_and_mismatch_hold_before_frequency_or_arm(self):
        from scripts import align_v4_next_arm_packet as builder
        from tests.align.test_v4_next_arm_packet import Scenario
        (self.root / 'ledger').mkdir()
        scenario = Scenario(self.root / 'ledger', 'R1')
        scenario.finish()
        state = {'measurement_root': str(self.root / 'ledger'), 'preparation_status': 'STAGED',
                 'registration_dir': str(self.pins.parent)}
        frequency = Mock(return_value={'ok': True})
        with ExitStack() as stack:
            stack.enter_context(patch.object(powermode, 'host_lock_preflight', return_value={'ok': True}))
            stack.enter_context(patch.object(session, 'session_start_restore', return_value={'action': 'none'}))
            stack.enter_context(patch.object(session.kit, 'generate'))
            stack.enter_context(patch.object(session, 'series_ac_powermode', return_value=0))
            stack.enter_context(patch.object(session.pilot, 'prepare', return_value=state))
            stack.enter_context(patch.object(session, 'weight_digest_preflight', return_value={'ok': True}))
            stack.enter_context(patch.object(session, 'arm_checks', side_effect=AssertionError('arm in prepare')))
            with self.assertRaisesRegex(ValueError, 'runtime_stack_preflight: differs:.*holds_previous_window: R1'):
                session.prepare(self.root / 'ledger', self.root / 'session', frequency_preflight=frequency,
                    runtime_runner=lambda python: dict(self.versions, python='changed'))
        stored = session.pilot.h.read(self.root / 'session/session.json')
        self.assertEqual(stored['holds_previous_window'], 'R1')
        self.assertFalse(stored['runtime_stack_preflight']['ok'])
        frequency.assert_not_called()

    def test_weight_function_accepts_explicit_inputs_without_session_state(self):
        reader = Mock(return_value={'artifacts': {'tiny-one': {'root': '/synthetic/weights',
            'folded_sha256': 'a' * 64, 'files': {'shard': 'b' * 64}}}})
        row = session.weight_digest_preflight(self.pins.parent, [{'model_id': 'tiny', 'run_id': 'one'}],
            reader=reader, identity_fn=lambda root: {'status': 'ok', 'kind': 'file_set',
                'folded_sha256': 'a' * 64, 'files': {'shard': 'b' * 64}})
        self.assertTrue(row['ok'], row)


class HeldWindowTests(unittest.TestCase):
    def setUp(self):
        from scripts import align_v4_next_arm_packet as builder
        from tests.align.test_v4_next_arm_packet import Scenario
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.builder = builder
        (self.root / 'repo').mkdir()
        self.scenario = Scenario(self.root / 'repo', 'W1')

    def packet(self):
        self.scenario.finish()
        return self.builder.build_packet(self.scenario.root, **self.scenario.identities(), now_epoch_s=111,
                                         current_artifact_set_sha256='a' * 64)

    def test_each_held_reason_refuses_and_nonheld_reason_does_not(self):
        for reason in ('records.source_changed_during_harvest', 'roster.no_science_bundles',
                       'precheck.certain_exclusion', 'cell.below_minimum'):
            with self.subTest(reason=reason):
                self.scenario.sources['exclusions'].update(reasons=[reason], claim_usable=False)
                row = session.held_window_check(self.scenario.root, self.packet())
                self.assertEqual(row['ok'], reason == 'cell.below_minimum', row)
                if not row['ok']:
                    self.assertEqual(row['reasons'], [f'held_window: W1: {reason}: no signed ruling'])

    def test_valid_signed_ruling_answers_hold_and_is_recorded_invalid_refuses(self):
        self.scenario.sources['exclusions'].update(reasons=['precheck.certain_exclusion'], claim_usable=False)
        text = self.scenario.write('rulings/held.txt', b'RL synthetic release after investigation')
        packet = self.packet()
        ruling = {'ruling_id': 'RL-synthetic', 'after_window': 'W1', 'resets': 'held_window_release',
                  'text': text, 'lead_signature': 'lead: synthetic 2026-11-11'}
        path = self.root / 'ruling.json'
        for signature, ok in (('unsigned', False), (ruling['lead_signature'], True)):
            path.write_text(json.dumps(dict(ruling, lead_signature=signature)))
            row = session.held_window_check(self.scenario.root, packet, ruling_path=path)
            self.assertEqual(row['ok'], ok, row)
            if ok:
                self.assertEqual(row['ruling']['lead_signature'], signature)
                self.assertEqual(row['ruling']['text_sha256'], text['sha256'])
        for mutation in ({'after_window': 'C1'}, {'resets': 'other'},
                         {'text': {'path': text['path'], 'sha256': 'f' * 64}}):
            path.write_text(json.dumps(dict(ruling, **mutation)))
            self.assertFalse(session.held_window_check(self.scenario.root, packet, ruling_path=path)['ok'])

    def test_previous_not_final_defers(self):
        from tests.align.test_v4_next_arm_packet import Scenario
        prior = Scenario(self.scenario.root, 'R1').finish()
        self.scenario = Scenario(self.scenario.root, 'W1', previous=prior)
        self.scenario.provisional = True
        row = session.held_window_check(self.scenario.root, self.packet())
        self.assertTrue(row['ok'], row)
        self.assertEqual(row['status'], 'previous window not final: hold check deferred to its finality')

    def test_changed_exclusions_blob_refuses_authentication(self):
        packet = self.packet()
        descriptor = self.scenario.record['sources']['exclusions']
        # Working-tree changes cannot replace committed evidence.
        (self.scenario.root / descriptor['path']).write_text('{"reasons": ["precheck.certain_exclusion"]}')
        self.assertTrue(session.held_window_check(self.scenario.root, packet)['ok'])
        packet['record_sha256'] = 'f' * 64
        self.assertFalse(session.held_window_check(self.scenario.root, packet)['ok'])


class WatchdogTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.plist = self.root / 'magistrate.plist'
        self.document = {'Label': 'com.joulewise.magistrate',
            'ProgramArguments': ['/usr/bin/env', 'python3', '/synthetic/installed/scripts/magistrate_watchdog.py'],
            'WorkingDirectory': '/synthetic/installed',
            'EnvironmentVariables': {'PATH': '/synthetic/bin',
                'MAGISTRATE_WATCHDOG_CUSTODY_ROOT': str(self.root / 'watchdog'),
                'MAGISTRATE_WATCHDOG_STATUS_HOST': 'synthetic'}}
        self.write_plist()
        self.plan = {'plan_id': 'synthetic-arm', 't0_epoch_s': session.time.time() + 3600,
                     'custody_root': str(self.root / 'custody')}
        item = {k: self.plan[k] for k in ('plan_id', 't0_epoch_s')}
        self.parser = dict(item, parse='ok', discovered_by_scan=False,
                           span_start_epoch_s=self.plan['t0_epoch_s'] - 180)
        self.discovery = {'plans': [dict(item, span_start_epoch_s=self.plan['t0_epoch_s'] - 180)],
                          'errors_count': 0, 'installed_source': 'not_distinguishable'}
        self.run = Mock(return_value=subprocess.CompletedProcess([], 0,
            'decision=LAUNCHING reason=all launch predicates clear\nWOULD_SPAWN none\n', ''))
        self.run.side_effect = lambda argv, **kw: (subprocess.CompletedProcess(argv, 0,
            json.dumps(self.parser if session.WATCHDOG_PLAN_FILE_PROGRAM in argv else self.discovery) + '\n', '')
            if '-c' in argv else self.run.return_value)

    def write_plist(self):
        self.plist.write_bytes(plistlib.dumps(self.document))

    def check(self, phase='pre_install'):
        return session.watchdog_acceptance(phase=phase, runner=self.run, plist_path=self.plist, plan=self.plan,
                                          plan_path=self.root / 'custody/night_plan.json')

    def test_span_boundary_requires_a_fence_in_both_phases(self):
        fences = {'FENCED', 'STANDDOWN_REQUEST', 'STANDDOWN_TERM', 'STANDDOWN_KILL'}
        for phase in ('pre_install', 'post_install'):
            for offset in (-181, -180, -179):
                for state in session.WATCHDOG_STATES:
                    with self.subTest(phase=phase, offset=offset, state=state):
                        self.run.return_value = subprocess.CompletedProcess([], 0, f'decision={state} reason=x\n', '')
                        row = session.watchdog_acceptance(phase=phase, runner=self.run, plist_path=self.plist,
                            plan=self.plan, plan_path=self.root / 'custody/night_plan.json',
                            now=lambda: self.plan['t0_epoch_s'] + offset)
                        admitted = session.WATCHDOG_ADMITTED if offset == -181 else fences
                        self.assertEqual(row['ok'], state in admitted)

    def test_discovery_uses_installed_interpreter_environment_and_identity(self):
        row = self.check('post_install')
        self.assertTrue(row['ok'], row)
        self.assertEqual(row['plan_identity'], {'source': 'installed_load_plans', 'found': True,
            'span_start_epoch_s': self.plan['t0_epoch_s'] - 180,
            'expected': self.plan['t0_epoch_s'] - 180, 'ok': True})
        first, second = self.run.call_args_list
        self.assertEqual(second.args[0], self.document['ProgramArguments'][:2] + [
            '-c', session.WATCHDOG_DISCOVERY_PROGRAM, self.document['ProgramArguments'][2],
            str(self.root / 'watchdog')])
        self.assertEqual(first.kwargs['env'], second.kwargs['env'])
        self.assertEqual(first.kwargs['cwd'], second.kwargs['cwd'])
        self.assertLessEqual(second.kwargs['timeout'], first.kwargs['timeout'])
        self.assertEqual(row['installed_source'], 'not_distinguishable')

    def test_discovery_faults_refuse_after_install(self):
        valid = json.dumps(self.discovery) + '\n'
        for phase in ('post_install',):
            for fault in ('missing', 'wrong_span', 'malformed', 'timeout', 'nonzero', 'errors', 'duplicate'):
                with self.subTest(phase=phase, fault=fault):
                    payload = json.loads(valid)
                    if fault == 'missing':
                        payload['plans'] = []
                    if fault == 'wrong_span':
                        payload['plans'][0]['span_start_epoch_s'] += 1
                    if fault == 'errors':
                        payload['errors_count'] = 1
                    if fault == 'duplicate':
                        payload['plans'] *= 2
                    def run(argv, **kw):
                        if '-c' not in argv:
                            return self.run.return_value
                        if fault == 'timeout':
                            raise subprocess.TimeoutExpired(argv, kw['timeout'])
                        return subprocess.CompletedProcess(argv, int(fault == 'nonzero'),
                            'not json\n' if fault == 'malformed' else json.dumps(payload) + '\n', '')
                    row = session.watchdog_acceptance(phase=phase, runner=run, plist_path=self.plist, plan=self.plan)
                    self.assertFalse(row['ok'], row)
                    self.assertFalse(row['plan_identity']['ok'])
                    self.assertIn(f'watchdog_acceptance: {phase}: plan_identity:', session._watchdog_refusal(phase, row))

    def test_dry_run_and_discovery_share_one_deadline(self):
        clock = [100_000_000_000]
        timeouts = []
        def run(argv, **kw):
            timeouts.append(kw['timeout'])
            clock[0] += (11 if '-c' in argv else 20) * 1_000_000_000
            return subprocess.CompletedProcess(argv, 0, json.dumps(self.discovery) if '-c' in argv
                else 'decision=LAUNCHING reason=x\n', '')
        with patch.object(session.time, 'monotonic_ns', side_effect=lambda: clock[0]):
            row = session.watchdog_acceptance(phase='post_install', runner=run, plist_path=self.plist, plan=self.plan)
        self.assertEqual(timeouts, [30, 10])
        self.assertFalse(row['ok'], row)
        self.assertIn('timeout', row['reason'].lower())

    def test_uses_only_installed_program_with_dry_run_and_bounded_environment(self):
        record = self.check()
        self.assertTrue(record['ok'], record)
        argv = self.run.call_args_list[0].args[0]
        self.assertEqual(argv, self.document['ProgramArguments'] + ['--dry-run', '--custody-root',
            self.document['EnvironmentVariables']['MAGISTRATE_WATCHDOG_CUSTODY_ROOT']])
        options = self.run.call_args_list[0].kwargs
        self.assertEqual(options['cwd'], self.document['WorkingDirectory'])
        self.assertEqual(options['env']['PATH'], '/synthetic/bin')
        self.assertGreater(options['timeout'], 0)
        self.assertLessEqual(options['timeout'], session.WATCHDOG_TIMEOUT_S)
        self.assertEqual(session.WATCHDOG_TIMEOUT_S, 3 * watchdog_fixtures.wd.SUPERVISOR_POLL_S)
        self.assertEqual(session.WATCHDOG_PLAN_LEAD_S, watchdog_fixtures.wd.PLAN_LEAD_S)
        self.assertEqual(record['argv'], argv)
        self.assertEqual(record['state'], 'LAUNCHING')
        self.assertGreaterEqual(record['elapsed_s'], 0)
        self.assertTrue(record['plan_read_proven'])

    def test_missing_unreadable_or_invalid_plist_refuses_without_running(self):
        for raw in (None, b'broken', plistlib.dumps({}), plistlib.dumps(dict(self.document, Program='/bin/sh')),
                plistlib.dumps(dict(self.document,
                ProgramArguments=self.document['ProgramArguments'] + ['handoff-daemons']))):
            with self.subTest(raw=raw):
                self.run.reset_mock()
                if raw is None:
                    self.plist.unlink()
                else:
                    self.plist.write_bytes(raw)
                self.assertFalse(self.check()['ok'])
                self.run.assert_not_called()
        self.write_plist()
        with patch.object(Path, 'read_bytes', side_effect=PermissionError('synthetic')):
            self.assertFalse(self.check()['ok'])

    def test_bad_decisions_exit_and_timeout_refuse(self):
        for output in ('', 'decision=ALIEN reason=unknown\n', ' decision=ACTIVE reason=bad\n',
                'decision=ACTIVE\n', 'decision=ACTIVE reason=\n',
                'decision=ACTIVE reason=ok\ndecision=ACTIVE reason=twice\n',
                'decision=ACTIVE reason=night_plan_unreadable x\n',
                'decision=ACTIVE reason=night_plan_malformed x\n',
                'decision=ACTIVE reason=installed_agent_fence: x\n'):
            with self.subTest(output=output):
                self.run.return_value = subprocess.CompletedProcess([], 0, output, '')
                self.assertFalse(self.check()['ok'])
                self.assertFalse(self.check('post_install')['ok'])
        self.run.return_value = subprocess.CompletedProcess([], 1, 'decision=ACTIVE reason=ok\n', '')
        self.assertFalse(self.check()['ok'])
        self.run.side_effect = subprocess.TimeoutExpired('synthetic', 30)
        self.assertFalse(self.check()['ok'])
        self.assertFalse(self.check('post_install')['ok'])

    def test_every_declared_state_is_classified_in_both_phases(self):
        wd = watchdog_fixtures.wd
        tree = ast.parse(Path(wd.__file__).read_text())
        # Literal Decision constructors, the reason-to-HOLD mapper, and the
        # two computed constructors; IDLE is emitted by the supervisor.
        declared = {node.args[0].value for node in ast.walk(tree)
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == 'Decision' and node.args
                    and isinstance(node.args[0], ast.Constant)}
        unsafe = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                      and node.name == '_unsafe_state')
        declared |= {node.value for node in ast.walk(unsafe)
                     if isinstance(node, ast.Constant) and isinstance(node.value, str)
                     and node.value.startswith('HOLD_')}
        declared |= {'STANDDOWN_REQUEST', 'STANDDOWN_TERM', 'STANDDOWN_KILL',
                     'BACKOFF', 'BACKOFF_USAGE', 'IDLE'}
        self.assertEqual(session.WATCHDOG_STATES, declared)
        admitted = {'ACTIVE', 'FENCED', 'STANDDOWN_REQUEST', 'STANDDOWN_TERM', 'STANDDOWN_KILL',
                    'LAUNCHING', 'IDLE', 'BACKOFF', 'BACKOFF_USAGE', 'STOPPED'}
        for phase in ('pre_install', 'post_install'):
            for state in sorted(declared):
                with self.subTest(phase=phase, state=state):
                    self.run.return_value = subprocess.CompletedProcess([], 0, f'decision={state} reason=x\n', '')
                    record = self.check(phase)
                    self.assertEqual(record['ok'], state in admitted)
                    self.assertEqual(record['stopped'], state == 'STOPPED')

    def test_unknown_words_refuse_and_pre_span_states_admit_after_install(self):
        for state in ('HOLD_PLAN_UNREADABLE', 'HOLD_CENSUS', 'STRANDED', 'CLOCK_UNCERTAIN',
                      'NETWORK_UNCERTAIN', 'HOLD_INVENTED', 'STANDDOWN_INVENTED'):
            with self.subTest(state=state):
                self.run.return_value = subprocess.CompletedProcess([], 0, f'decision={state} reason=x\n', '')
                self.assertFalse(self.check()['ok'])
        for state in ('FENCED', 'STANDDOWN_REQUEST', 'STANDDOWN_TERM', 'STANDDOWN_KILL', 'ACTIVE'):
            self.run.return_value = subprocess.CompletedProcess([], 0, f'decision={state} reason=x\n', '')
            self.assertTrue(self.check('post_install')['ok'], state)
        for state in ('LAUNCHING', 'IDLE', 'BACKOFF', 'BACKOFF_USAGE', 'STOPPED'):
            self.run.return_value = subprocess.CompletedProcess([], 0, f'decision={state} reason=x\n', '')
            self.assertTrue(self.check()['ok'], state)
            self.assertTrue(self.check('post_install')['ok'], state)

    def test_explicit_custody_argument_is_preserved_and_no_mutating_form_is_built(self):
        self.document['ProgramArguments'] += ['--custody-root', str(self.root / 'explicit')]
        self.write_plist()
        self.assertTrue(self.check()['ok'])
        argv = self.run.call_args_list[0].args[0]
        self.assertEqual(argv.count('--dry-run'), 1)
        self.assertEqual(argv.count('--custody-root'), 1)
        self.assertEqual(argv[-1], str(self.root / 'explicit'))

    def test_absolute_interpreter_and_plist_parse_failure_are_bounded_refusals(self):
        self.document['ProgramArguments'] = ['/synthetic/venv/bin/python3.13', '-B',
            '/synthetic/installed/scripts/magistrate_watchdog.py']
        self.write_plist()
        self.assertTrue(self.check()['ok'])
        self.assertEqual(self.run.call_args_list[0].args[0][:3], self.document['ProgramArguments'])
        self.run.reset_mock()
        with patch.object(session.plistlib, 'loads', side_effect=RuntimeError('bad XML date')):
            self.assertFalse(self.check()['ok'])
        self.run.assert_not_called()

    def test_stored_dry_run_streams_are_capped_in_utf8_bytes_without_hiding_decision(self):
        self.run.return_value = subprocess.CompletedProcess([], 0,
            '\N{SNOWMAN}' * 8192 + '\ndecision=LAUNCHING reason=x\n', '\N{SNOWMAN}' * 8192)
        row = self.check('post_install')
        self.assertTrue(row['ok'], row)
        for stream in ('stdout', 'stderr'):
            self.assertLessEqual(len(row[stream].encode()), 8192)
            self.assertTrue(row[stream + '_truncated'])
        self.run.return_value = subprocess.CompletedProcess([], 0, 'decision=LAUNCHING reason=x\n', '')
        row = self.check('post_install')
        self.assertFalse(row['stdout_truncated'])
        self.assertFalse(row['stderr_truncated'])


class RemoteProbeTests(watchdog_fixtures.WatchdogTestCase):
    def test_direct_parser_rejects_installed_deadman_epoch_error(self):
        module = self.temp / 'deadman-watchdog.py'
        module.write_text('''import json, time
from pathlib import Path
from types import SimpleNamespace
PLAN_LEAD_S = 180
class PlanError(ValueError): pass
class Storage:
    def __init__(self, root, dry_run): pass
    def read_text(self, path): return path.read_text()
def is_retired_v1_plan(raw): return False
class NightPlan:
    @staticmethod
    def from_mapping(raw): return SimpleNamespace(**raw)
def deadman_epoch(plan): raise PlanError("synthetic invalid deadman")
def load_plans(storage, now_epoch_s): return SimpleNamespace(plans=[])
''')
        plan = self.temp / 'deadman-plan.json'
        plan.write_text(json.dumps({'plan_id': 'synthetic', 'authored_epoch_s': 1, 't0_epoch_s': 2}))
        out = subprocess.run([sys.executable, '-B', '-c', session.WATCHDOG_PLAN_FILE_PROGRAM,
            str(module), str(self.temp), str(plan)], capture_output=True, text=True, check=True, timeout=30)
        self.assertEqual(json.loads(out.stdout), {'parse': 'malformed', 'exception': 'PlanError',
                                                 'discovered_by_scan': False})

    def parser_run(self, argv, **kwargs):
        # Only the fixed file-reader program runs for real. Host/remote dry-run
        # probes remain behind the injected runner, as required by RL-53.
        if '-c' in argv:
            return subprocess.run(argv, **kwargs)
        return subprocess.CompletedProcess(argv, 0, 'decision=LAUNCHING reason=synthetic\n', '')

    def installed_plist(self, home, watchdog_root):
        # Match install_magistrate_watchdog.sh:225-246, including XML escaping
        # and replacement of the env/python pair by the selected interpreter.
        text = (session.ROOT / 'configs/launchd/com.joulewise.magistrate.plist.template').read_text()
        for key, value in {'REPO': str(session.ROOT), 'PATH': os.environ['PATH'],
                'SESSION_BIN': str(self.temp / 'unused-session'), 'CUSTODY_ROOT': str(watchdog_root),
                'STATUS_HOST': 'synthetic'}.items():
            text = text.replace('@@' + key + '@@', escape(value))
        text = text.replace('    <string>/usr/bin/env</string>\n    <string>python3</string>',
                            f'    <string>{escape(sys.executable)}</string>')
        self.assertNotIn('@@', text)
        path = home / 'Library/LaunchAgents/com.joulewise.magistrate.plist'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_real_installed_parser_accepts_both_layouts_and_post_install_needs_discovery(self):
        from joulewise.night_agent_install import LABELS, Prepared
        wd = watchdog_fixtures.wd
        for scanned in (True, False):
            with self.subTest(discovered_by_scan=scanned):
                base = self.temp / str(scanned)
                home = base / 'home'
                watchdog_root = base / 'night-custody/watchdog'
                custody = (base / 'night-custody/arm' if scanned else
                           base / 'night-align/session/custody')
                plan = self.make_plan(name=str(custody), t0=session.time.time() + 3600)
                plan_path = custody / 'night_plan.json'
                raw = json.loads(plan_path.read_text())
                plist = self.installed_plist(home, watchdog_root)
                def check(phase):
                    with patch.dict(os.environ, HOME=str(home)):
                        return session.watchdog_acceptance(phase=phase, runner=self.parser_run,
                            plist_path=plist, plan=raw, plan_path=plan_path)
                pre = check('pre_install')
                self.assertTrue(pre['ok'], pre)
                self.assertEqual(pre['plan_identity'], {'source': 'installed_parser_on_plan_file',
                    'found': True, 'discovered_by_scan': scanned,
                    'span_start_epoch_s': plan.t0_epoch_s - wd.PLAN_LEAD_S,
                    'expected': plan.t0_epoch_s - session.WATCHDOG_PLAN_LEAD_S, 'ok': True})
                self.assertEqual(json.loads(subprocess.run([sys.executable, '-B', '-c',
                    session.WATCHDOG_PLAN_FILE_PROGRAM, str(Path(wd.__file__).resolve()),
                    str(watchdog_root), str(plan_path)], cwd=session.ROOT,
                    env=dict(os.environ, HOME=str(home), PYTHONDONTWRITEBYTECODE='1'),
                    capture_output=True, text=True, check=True, timeout=30).stdout)['parse'], 'ok')
                if not scanned:
                    post = check('post_install')
                    self.assertFalse(post['ok'], post)
                    self.assertIn('arm plan missing', post['reason'])
                    calls = []
                    def run(argv, **kwargs):
                        calls.append(argv)
                        if '--uninstall' in argv:
                            return subprocess.CompletedProcess(argv, 0, '', '')
                        if argv[:2] == ['launchctl', 'print']:
                            label = argv[-1].rsplit('/', 1)[-1]
                            return subprocess.CompletedProcess(argv, 113, '',
                                f'Could not find service "{label}" in domain for user gui: {os.getuid()}')
                        return self.parser_run(argv, **kwargs)
                    dwell = {'quiet_dwell': {}}
                    with patch.dict(os.environ, HOME=str(home)), self.assertRaisesRegex(
                            ValueError, 'arm plan missing.*install undone'):
                        session._watchdog_post_install({'plan_path': str(plan_path),
                            'measurement_root': str(session.ROOT)}, dwell, runner=run, plist_path=plist)
                    self.assertTrue(any('--uninstall' in call for call in calls))
                    self.assertEqual(dwell['quiet_dwell']['watchdog_post_install']['install_undo']['remaining_labels'], [])
                # Render the real production night template through its helper;
                # no installer invocation or launchctl is needed to publish temp plists.
                prepared = Prepared(plan, plan_path, session.ROOT, sys.executable,
                    (session.ROOT / 'configs/launchd/com.joulewise.night.plist.template').read_text(),
                    str(self.temp / 'unused-courier'), os.environ['PATH'],
                    {'night_calendar': {'Month': 11, 'Day': 11, 'Hour': 23, 'Minute': 0},
                     'deadman_calendar': {'Month': 11, 'Day': 12, 'Hour': 1, 'Minute': 0}}, None)
                for label, payload in prepared.render(LABELS):
                    (plist.parent / f'{label}.plist').write_bytes(payload)
                post = check('post_install')
                self.assertTrue(post['ok'], post)
                self.assertEqual(post['plan_identity']['source'], 'installed_load_plans')
                self.assertTrue(post['plan_read_proven'])

    def test_version_skewed_installed_parser_refuses_pre_install_without_fake_runner(self):
        home = self.temp / 'skew-home'
        plist = self.installed_plist(home, self.temp / 'night-custody/watchdog')
        module = self.temp / 'installed/magistrate_watchdog.py'
        module.parent.mkdir()
        module.write_text('''import json, time
from pathlib import Path
from types import SimpleNamespace
PLAN_LEAD_S = 180
class PlanError(ValueError): pass
class Storage:
    def __init__(self, root, dry_run=False):
        self.root, self.dry_run, self.would_write = root, dry_run, []
    def read_text(self, path): return path.read_text()
    def glob_plans(self): return []
class NightPlan:
    @classmethod
    def from_mapping(cls, raw):
        if 'ac_powermode' in raw: raise PlanError('SECRET unknown key ac_powermode')
        return SimpleNamespace(**raw)
def is_retired_v1_plan(raw): return False
def deadman_epoch(plan): return plan.t0_epoch_s + 600
def load_plans(storage, **kwargs): return SimpleNamespace(plans=(), errors=())
if __name__ == '__main__': print('decision=LAUNCHING reason=synthetic')
''')
        doc = plistlib.loads(plist.read_bytes())
        doc['ProgramArguments'] = [sys.executable, '-B', str(module)]
        plist.write_bytes(plistlib.dumps(doc))
        custody = self.temp / 'night-align/session/custody'
        custody.mkdir(parents=True)
        plan = {'plan_id': 'skew-arm', 't0_epoch_s': session.time.time() + 3600,
                'authored_epoch_s': session.time.time() - 60, 'custody_root': str(custody), 'ac_powermode': 2}
        (custody / 'night_plan.json').write_text(json.dumps(plan))
        with patch.dict(os.environ, HOME=str(home)):
            row = session.watchdog_acceptance(phase='pre_install', plist_path=plist, plan=plan,
                                             plan_path=custody / 'night_plan.json')
        self.assertFalse(row['ok'], row)
        self.assertEqual(session._watchdog_refusal('pre_install', row),
            'watchdog_acceptance: pre_install: plan_identity: malformed')
        self.assertNotIn('SECRET', json.dumps(row))
        self.assertNotIn('ac_powermode', json.dumps(row))

    def test_real_magistrate_template_is_accepted_by_installed_plist_whitelist(self):
        plan = self.make_plan(t0=session.time.time() + 3600)
        home = self.temp / 'template-home'
        plist = self.installed_plist(home, self.harness.storage.root)
        run = Mock(side_effect=self.parser_run)
        with patch.dict(os.environ, HOME=str(home)):
            row = session.watchdog_acceptance(phase='pre_install', runner=run, plist_path=plist,
                plan=json.loads((Path(plan.custody_root) / 'night_plan.json').read_text()),
                plan_path=Path(plan.custody_root) / 'night_plan.json')
        self.assertTrue(row['ok'], row)
        self.assertEqual(run.call_args_list[0].args[0][:2],
            [sys.executable, str(session.ROOT / 'scripts/magistrate_watchdog.py')])
        self.assertEqual(run.call_args_list[0].kwargs['env']['MAGISTRATE_SESSION_BIN'],
                         str(self.temp / 'unused-session'))

    def test_direct_parser_uses_scanned_plan_rejection_steps_and_emits_no_content(self):
        plan = self.make_plan(t0=session.time.time() + 3600)
        path = Path(plan.custody_root) / 'night_plan.json'
        original = path.read_text()
        home = self.temp / 'parser-home'
        home.mkdir()
        cases = [(None, 'unreadable', 'FileNotFoundError'), ('SECRET not json', 'unreadable', 'JSONDecodeError'),
                 ((session.ROOT / 'tests/fixtures/night_plan_v1_retired.json').read_text(), 'retired_v1', None)]
        future = json.loads(original)
        future['authored_epoch_s'] = future['t0_epoch_s']
        cases.append((json.dumps(future), 'malformed', 'PlanError'))
        malformed = json.loads(original)
        malformed['SECRET_UNKNOWN_KEY'] = 'SECRET content'
        cases.append((json.dumps(malformed), 'malformed', 'PlanError'))
        for content, status, exception in cases:
            with self.subTest(status=status, exception=exception):
                if content is None:
                    path.unlink()
                else:
                    path.write_text(content)
                before = sorted(str(p) for p in self.temp.rglob('*'))
                out = subprocess.run([sys.executable, '-B', '-c', session.WATCHDOG_PLAN_FILE_PROGRAM,
                    str(Path(watchdog_fixtures.wd.__file__).resolve()), str(self.harness.storage.root), str(path)],
                    cwd=session.ROOT, env=dict(os.environ, HOME=str(home), PYTHONDONTWRITEBYTECODE='1'),
                    check=True, capture_output=True, text=True, timeout=30)
                self.assertEqual(len(out.stdout.splitlines()), 1)
                expected = {'parse': status, 'discovered_by_scan': False}
                if exception:
                    expected['exception'] = exception
                self.assertEqual(json.loads(out.stdout), expected)
                self.assertEqual(out.stderr, '')
                self.assertNotIn('SECRET', out.stdout)
                self.assertEqual(before, sorted(str(p) for p in self.temp.rglob('*')))

    def test_constant_discovery_program_runs_against_real_module_without_host_access(self):
        plan = self.make_plan()
        home = self.temp / 'isolated-home'
        (home / 'Library/LaunchAgents').mkdir(parents=True)
        before = sorted(str(p.relative_to(self.temp)) for p in self.temp.rglob('*'))
        out = subprocess.run([sys.executable, '-B', '-c', session.WATCHDOG_DISCOVERY_PROGRAM,
            str(Path(watchdog_fixtures.wd.__file__).resolve()), str(self.harness.storage.root)],
            cwd=session.ROOT, env=dict(os.environ, HOME=str(home), PYTHONDONTWRITEBYTECODE='1'),
            check=False, capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(len(out.stdout.splitlines()), 1)
        self.assertEqual(json.loads(out.stdout), {'plans': [{'plan_id': plan.plan_id,
            't0_epoch_s': plan.t0_epoch_s, 'span_start_epoch_s': plan.t0_epoch_s - watchdog_fixtures.wd.PLAN_LEAD_S}],
            'errors_count': 0, 'installed_source': 'not_distinguishable'})
        self.assertEqual(before, sorted(str(p.relative_to(self.temp)) for p in self.temp.rglob('*')))

    def test_helper_argv_and_environment_cannot_enable_in_span_probe(self):
        wd = watchdog_fixtures.wd
        plan = self.make_plan()
        agents = self.temp / 'home/Library/LaunchAgents'
        agents.mkdir(parents=True)
        for label in ('com.joulewise.night', 'com.joulewise.night.deadman'):
            (agents / f'{label}.plist').write_bytes(plistlib.dumps({
                'ProgramArguments': ['/synthetic/run_night.py', '--plan',
                                     str(Path(plan.custody_root) / 'night_plan.json')]}))
        plist = agents / 'com.joulewise.magistrate.plist'
        environment = {'MAGISTRATE_WATCHDOG_CUSTODY_ROOT': str(self.harness.storage.root),
                       'MAGISTRATE_WATCHDOG_STATUS_HOST': 'synthetic', 'GIT_TERMINAL_PROMPT': '1'}
        plist.write_bytes(plistlib.dumps({'Label': 'com.joulewise.magistrate',
            'ProgramArguments': ['/synthetic/python3', '/synthetic/magistrate_watchdog.py'],
            'WorkingDirectory': str(self.temp), 'EnvironmentVariables': environment}))
        self.harness.deps.git_probe = wd.remote_stop_probe

        def runner(argv, **kwargs):
            if '-c' in argv:
                return subprocess.CompletedProcess(argv, 0, json.dumps({'plans': [{'plan_id': plan.plan_id,
                    't0_epoch_s': plan.t0_epoch_s, 'span_start_epoch_s': plan.t0_epoch_s - wd.PLAN_LEAD_S}],
                    'errors_count': 0, 'installed_source': 'not_distinguishable'}), '')
            self.assertEqual(argv[2:], ['--dry-run', '--custody-root', str(self.harness.storage.root)])
            out = io.StringIO()
            with patch.dict(os.environ, kwargs['env'], clear=True), contextlib.redirect_stdout(out):
                rc = wd.main(argv[2:])
            return subprocess.CompletedProcess(argv, rc, out.getvalue(), '')

        with ExitStack() as stack:
            # The installed plists alone supply the plan (no custody glob).
            stack.enter_context(patch.object(wd.Storage, 'glob_plans', return_value=[]))
            stack.enter_context(patch.object(wd, 'real_dependencies', return_value=self.harness.deps))
            stack.enter_context(patch.object(wd, 'current_boot_id', return_value='synthetic-boot'))
            network = stack.enter_context(patch.object(wd.subprocess, 'run',
                return_value=subprocess.CompletedProcess([], 0, 'synthetic stop', '')))
            transport = stack.enter_context(patch.object(wd.subprocess, 'Popen',
                side_effect=AssertionError('status transport forbidden')))
            fork = stack.enter_context(patch.object(wd.os, 'fork', side_effect=AssertionError('fork forbidden')))
            for offset in (-wd.PLAN_LEAD_S, -1, 0, 1):
                with self.subTest(offset=offset):
                    self.harness.clock.wall = dt.datetime.fromtimestamp(plan.t0_epoch_s + offset,
                                                                        tz=self.local_tz)
                    storage = wd.Storage(self.harness.storage.root, dry_run=True)
                    state = wd.initial_state()
                    self.assertFalse(wd._remote_probe_allowed(storage, self.harness.deps, state))
                    self.assertEqual(wd._probe_remote_stop(storage, self.harness.deps, state).state, 'NOT_PROBED')
                    record = session.watchdog_acceptance(phase='post_install', runner=runner, plist_path=plist,
                        plan={'plan_id': plan.plan_id, 't0_epoch_s': plan.t0_epoch_s},
                        now=lambda: self.harness.clock.wall.timestamp())
                    self.assertTrue(record['ok'], record)
                    self.assertEqual(record['state'], 'FENCED')
                    network.assert_not_called()
                    transport.assert_not_called()
                    fork.assert_not_called()
            # The same installed plan before t0-180 DOES permit remote Git.
            self.harness.clock.wall = dt.datetime.fromtimestamp(plan.t0_epoch_s - wd.PLAN_LEAD_S - 1,
                                                                tz=self.local_tz)
            self.assertTrue(wd._remote_probe_allowed(storage, self.harness.deps, wd.initial_state()))
            record = session.watchdog_acceptance(phase='post_install', runner=runner, plist_path=plist,
                plan={'plan_id': plan.plan_id, 't0_epoch_s': plan.t0_epoch_s},
                now=lambda: self.harness.clock.wall.timestamp())
            self.assertTrue(record['ok'], record)
            self.assertEqual(record['state'], 'STOPPED')
            self.assertEqual(network.call_count, 2)
            self.assertTrue(all('ls-remote' in call.args[0] for call in network.call_args_list))
            fork.assert_not_called()
            transport.assert_not_called()
        self.assertFalse((self.harness.storage.root / 'state.json').exists())


class PrivilegeTests(unittest.TestCase):
    def test_stored_sudo_listing_streams_are_capped_with_individual_flags(self):
        def run(argv):
            return subprocess.CompletedProcess(argv, 0,
                '\N{SNOWMAN}' * 8192 if '-l' in argv else 'Network Time: On\n', 'x' * 8193)
        row = session.host_privilege_preflight(runner=run)
        self.assertTrue(row['ok'], row)
        for rule in row['rules'].values():
            for stream in ('stdout', 'stderr'):
                self.assertLessEqual(len(rule[stream].encode()), 8192)
                self.assertTrue(rule[stream + '_truncated'])
        row, _ = self.run_preflight()
        for rule in row['rules'].values():
            self.assertFalse(rule['stdout_truncated'])
            self.assertFalse(rule['stderr_truncated'])

    def run_preflight(self, *, missing=None, network='Network Time: On\n', query_exit=0):
        calls = []

        def run(argv):
            calls.append(tuple(argv))
            self.assertEqual(argv[:2], ('/usr/bin/sudo', '-n'))
            if '-l' in argv:
                self.assertEqual(argv[2], '-l')
                return subprocess.CompletedProcess(argv, int(tuple(argv[3:]) == missing), '', '')
            self.assertIn('-getusingnetworktime', argv)
            self.assertFalse(any(arg.startswith('-set') for arg in argv))
            return subprocess.CompletedProcess(argv, query_exit, network, '')

        return session.host_privilege_preflight(runner=run), calls

    def test_each_rule_missing_refuses_and_names_it(self):
        rules = session.host_privilege_rules()
        self.assertEqual(len(rules), 6)
        for name, argv in rules:
            with self.subTest(rule=name):
                record, _ = self.run_preflight(missing=tuple(argv[2:]))
                self.assertFalse(record['ok'])
                self.assertIn(f'host_privilege_preflight: sudo_rule_missing: {name}', record['reasons'])

    def test_all_rules_are_listed_never_executed_and_on_or_off_both_admit(self):
        for state in ('On', 'Off'):
            record, calls = self.run_preflight(network=f'Network Time: {state}\n')
            self.assertTrue(record['ok'], record)
            self.assertEqual(record['network_time']['observed'], state.lower())
            self.assertEqual(len(calls), 7)
            self.assertTrue(all('-l' in argv for argv in calls[:-1]))

    def test_network_read_failure_refuses(self):
        for output, code in (('', 0), ('permission denied', 0), ('Network Time: On\n', 1)):
            record, _ = self.run_preflight(network=output, query_exit=code)
            self.assertFalse(record['ok'])
            self.assertIn('host_privilege_preflight: network_time_unreadable', record['reasons'])

    def test_rule_timeout_is_a_named_refusal_and_query_is_not_a_setter(self):
        def timeout(argv):
            raise subprocess.TimeoutExpired(argv, 10)
        record = session.host_privilege_preflight(runner=timeout)
        self.assertFalse(record['ok'])
        self.assertEqual(sum('sudo_rule_missing' in reason for reason in record['reasons']), 6)
        self.assertIsNone(record['network_time'])

    def test_prepare_records_failure_and_keeps_old_host_lock_refusal(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            stack.enter_context(patch.object(powermode, 'host_state_override', return_value=None))
            stack.enter_context(patch.object(powermode, 'HostLock'))
            lock = stack.enter_context(patch.object(powermode, 'host_lock_preflight', return_value={'acquired': True}))
            stack.enter_context(patch.object(session, 'session_start_restore', return_value={'action': 'none'}))
            stack.enter_context(patch.object(session.kit, 'generate'))
            stack.enter_context(patch.object(session, 'series_ac_powermode', return_value=0))
            stack.enter_context(patch.object(session.pilot, 'prepare', return_value={'preparation_status': 'STAGED'}))
            frequency = Mock(return_value={'ok': True})
            run = lambda argv: subprocess.CompletedProcess(argv, 1, '', '')
            with self.assertRaisesRegex(ValueError, 'host_privilege_preflight: sudo_rule_missing'):
                session.prepare(tmp, tmp, power_runner=run, frequency_preflight=frequency)
            state = json.loads((Path(tmp) / 'session.json').read_bytes())
            self.assertFalse(state['host_privilege_preflight']['ok'])
            self.assertEqual(state['host_state_preflight'], {'acquired': True})
            frequency.assert_not_called()
            lock.side_effect = ValueError('host-state preflight refused: synthetic')
            with self.assertRaisesRegex(ValueError, 'host-state preflight refused'):
                session.prepare(tmp, tmp, power_runner=run)

    def test_prepare_admits_readable_on_and_retains_the_frequency_gate(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            stack.enter_context(patch.object(session, 'weight_digest_preflight', return_value={'ok': True, 'synthetic': True}))
            stack.enter_context(patch.object(powermode, 'host_state_override', return_value=None))
            stack.enter_context(patch.object(powermode, 'HostLock'))
            stack.enter_context(patch.object(powermode, 'host_lock_preflight', return_value={'acquired': True}))
            stack.enter_context(patch.object(session, 'session_start_restore', return_value={'action': 'none'}))
            stack.enter_context(patch.object(session.kit, 'generate'))
            stack.enter_context(patch.object(session, 'series_ac_powermode', return_value=0))
            stack.enter_context(patch.object(session.pilot, 'prepare', return_value={'preparation_status': 'STAGED'}))
            frequency = Mock(return_value={'ok': True})
            run = lambda argv: subprocess.CompletedProcess(argv, 0, 'Network Time: On\n', '')
            state = session.prepare(tmp, tmp, power_runner=run, frequency_preflight=frequency)
            self.assertTrue(state['host_privilege_preflight']['ok'])
            self.assertEqual(state['host_privilege_preflight']['network_time']['observed'], 'on')
            frequency.assert_called_once()
            frequency.return_value = {'ok': False, 'cause': 'clock.frequency_word_nonzero', 'reason': 'synthetic'}
            with self.assertRaisesRegex(ValueError, 'clock.frequency_word_nonzero'):
                session.prepare(tmp, tmp, power_runner=run, frequency_preflight=frequency)


class PreInstallTests(unittest.TestCase):
    def test_watchdog_refusal_is_recorded_before_meter_and_stamp(self):
        events = []
        from joulewise.align.apple import external_volume, v4_registration
        from joulewise import battery_float
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            stack.enter_context(patch.object(powermode, 'admit_ac_powermode',
                                            return_value={'admitted': False, 'reason': 'old refusal'}))
            stack.enter_context(patch.object(external_volume, 'census', return_value={}))
            stack.enter_context(patch.object(external_volume, 'arm_check', return_value={'verdict': 'PASS', 'reasons': []}))
            stack.enter_context(patch.object(battery_float, 'observe', return_value=({}, b'synthetic')))
            stack.enter_context(patch.object(v4_registration, 'battery_arm', return_value={'admitted': False, 'reasons': []}))
            stack.enter_context(patch.object(v4_registration, 'artifact_set_digest', return_value='a' * 64))
            held = stack.enter_context(patch.object(session, 'held_window_check', create=True,
                side_effect=lambda *a, **k: events.append('held') or
                {'ok': False, 'reasons': ['held_window: W1: precheck.certain_exclusion: no signed ruling']}))

            def check(**kwargs):
                events.append('watchdog')
                return dict(acceptance(**kwargs), ok=False, state='HOLD_PLAN_MALFORMED', reason='synthetic')

            record = session.arm_checks(tmp, {}, runner=lambda argv: subprocess.CompletedProcess(argv, 0, '', ''),
                watchdog_check=check, meter_probe=lambda root: events.append('meter') or {'live': True},
                pre_dwell=lambda record: events.append('write'),
                dwell_start=lambda: events.append('stamp') or session.time.monotonic_ns())
            self.assertEqual(events, ['held', 'watchdog', 'meter', 'write', 'stamp'])
            held.assert_called_once()
            self.assertFalse(record['held_window_check']['ok'])
            self.assertIn('watchdog_acceptance: pre_install: HOLD_PLAN_MALFORMED: synthetic', record['reasons'])
            self.assertIn('ac_powermode: old refusal', record['reasons'])
            self.assertFalse(record['watchdog_acceptance']['ok'])


class ArmIntegrationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.session = self.root / 'session'
        self.session.mkdir()
        self.events = []
        self.state = {'measurement_root': str(self.root), 'plan_path': str(self.root / 'night_plan.json'),
                      'inputs': {'custody_root': str(self.root / 'custody')}}
        self.t0 = session.time.time() + 3600
        Path(self.state['plan_path']).write_text(json.dumps({'plan_id': 'synthetic-arm', 't0_epoch_s': self.t0}))
        self.plan = {'runtime_requirements': {'ac_powermode': 0}}
        session.pilot.h.write(self.session / 'session.json', self.state)
        self.run = Mock(side_effect=self.command)
        self.check = Mock(side_effect=self.watchdog)
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(session.kit, 'generate'))
        stack.enter_context(patch.object(session.kit, 'arm_powermode_check'))
        stack.enter_context(patch.object(session, 'session_start_restore', return_value={'action': 'none'}))
        stack.enter_context(patch.object(session, 'w1_disk_check', return_value={'status': 'pass'}))
        stack.enter_context(patch.object(session, 'arm_checks', side_effect=self.arm))
        self.installer = stack.enter_context(patch.object(session.pilot, 'install', side_effect=self.installed))
        self.restore = stack.enter_context(patch.object(powermode, 'restore_automatic', return_value={'ok': True}))
        stack.enter_context(patch.object(powermode, 'enter_high_power', return_value={'ok': True}))
        stack.enter_context(patch.object(powermode, 'HostLock'))

    def command(self, argv, **_):
        self.events.append(tuple(argv))
        if '--uninstall' in argv:
            return subprocess.CompletedProcess(argv, 0, '', '')
        label = argv[-1].rsplit('/', 1)[-1]
        return subprocess.CompletedProcess(argv, 113, '',
            f'Could not find service "{label}" in domain for user gui: {os.getuid()}')

    def watchdog(self, **kwargs):
        self.events.append(kwargs['phase'])
        return acceptance(**kwargs)

    def installed(self, *_, **__):
        self.events.append('install')
        return {'exit_code': 0}

    def arm(self, *_, pre_dwell, **kwargs):
        # The real arm ordering is checked separately; retain its pre-dwell write seam here.
        record = {'admitted': True, 'reasons': [], 'series_binding': [],
                  'ac_powermode': {'observed': 0}, 'quiet_dwell': {}}
        pre_dwell(record)
        self.events.append('stamp')
        record['quiet_dwell'] = {'start_ns': session.time.monotonic_ns()}
        return record

    def install(self, *, high=False, now=None, **kwargs):
        if high:
            self.plan['runtime_requirements']['ac_powermode'] = 2
        path = self.root / session.kit.KIT / 'collection_plan.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.plan))
        return session.install(self.session, runner=self.run, watchdog_check=self.check, now=now,
            frequency_preflight=lambda *a, **k: {'ok': True},
            frequency_pre_t0=lambda *a, **k: {'ok': True}, **kwargs)

    def test_weight_digests_from_prepare_are_carried_verbatim_without_hashing(self):
        block = {'source': 'prepare', 'prepared_at_epoch_s': 1234, 'ok': True,
                 'roots': {'/synthetic/model': {'registered_folded_sha256': 'a' * 64,
                     'observed_folded_sha256': 'a' * 64, 'ok': True}}}
        self.state['weight_digest_preflight'] = block
        session.pilot.h.write(self.session / 'session.json', self.state)
        with patch('joulewise.provenance.model_artifact_identity', side_effect=AssertionError('arm rehashed')) as identity:
            self.install()
        identity.assert_not_called()
        arm = session.pilot.h.read(self.session / 'staging/v4-arm-001.json')
        self.assertEqual(arm['weight_digests'], block)

    def test_runtime_stack_prepare_legacy_and_attestation_sources(self):
        versions = {'python': '3.13.1', 'packages': {'mlx': '0.31.2'}}
        pins = self.root / session.kit.KIT / 'registration/identity_pins.json'
        pins.parent.mkdir(parents=True, exist_ok=True)
        pins.write_text(json.dumps({'runtime_versions': versions}))
        path = self.root / 'stack.json'
        for source in ('prepare', 'not_recorded_by_prepare', 'attested'):
            with self.subTest(source=source):
                state = session.pilot.h.read(self.session / 'session.json')
                block = {'source': 'prepare', 'ok': True, 'registered': versions, 'observed': versions,
                         'elapsed_s': 12.5}
                state.pop('runtime_stack_preflight', None)
                if source == 'prepare':
                    state['runtime_stack_preflight'] = block
                session.pilot.h.write(self.session / 'session.json', state)
                path.write_text(json.dumps({'attested_by': 'Synthetic operator', 'registered': versions,
                                           'observed': versions}))
                with patch('joulewise.flags.collect.runtime_versions', side_effect=AssertionError('probe at arm')):
                    self.install(**({'runtime_stack_attested': path} if source == 'attested' else {}))
                arm = json.loads(sorted((self.session / 'staging').glob('v4-arm-???.json'))[-1].read_text())
                self.assertEqual(arm['runtime_stack']['source'], source)
                if source == 'prepare':
                    self.assertEqual(arm['runtime_stack'], block)
        path.write_text(json.dumps({'attested_by': 'Synthetic operator', 'registered': versions,
                                   'observed': dict(versions, python='changed')}))
        self.installer.reset_mock()
        with self.assertRaisesRegex(ValueError, 'runtime_stack_preflight: differs:'):
            self.install(runtime_stack_attested=path)
        self.installer.assert_not_called()
        arm = json.loads(sorted((self.session / 'staging').glob('v4-arm-???.json'))[-1].read_text())
        self.assertFalse(arm['runtime_stack']['ok'])

    def test_runtime_and_held_cli_options_are_forwarded(self):
        with patch.object(session, 'install', return_value={}) as install:
            session.main(['install', '--session-root', str(self.session), '--w1-disk-config', 'synthetic',
                '--obc-off-attested-by', 'synthetic', '--battery-log', 'synthetic', '--next-arm-triage', 'synthetic',
                '--runtime-stack-attested', 'stack.json', '--held-window-ruling', 'ruling.json'])
        self.assertEqual(install.call_args.kwargs['runtime_stack_attested'], Path('stack.json'))
        self.assertEqual(install.call_args.kwargs['held_window_ruling'], Path('ruling.json'))

    def test_legacy_prepare_records_not_recorded_without_refusal_or_hashing(self):
        with patch('joulewise.provenance.model_artifact_identity', side_effect=AssertionError('arm rehashed')):
            self.install()
        arm = session.pilot.h.read(self.session / 'staging/v4-arm-001.json')
        self.assertTrue(arm['admitted'])
        self.assertEqual(arm['weight_digests'], {'source': 'not_recorded_by_prepare'})

    def attestation(self, **changes):
        root = str(self.root / 'tiny-weights')
        self.plan['members'] = [{'model_id': 'tiny', 'run_id': 'one'}, {'model_id': 'tiny', 'run_id': 'two'}]
        directory = self.root / session.kit.KIT / 'registration'
        directory.mkdir(parents=True, exist_ok=True)
        session.pilot.h.write(directory / 'model_artifact_inventory.json', {'artifacts': {
            'tiny-one': {'root': root, 'folded_sha256': 'a' * 64},
            'tiny-two': {'root': root, 'folded_sha256': 'a' * 64}}})
        doc = {'attested_by': 'Synthetic operator', 'attested_at_epoch_s': 1234,
               'roots': {root: {'registered_folded_sha256': 'a' * 64, 'observed_folded_sha256': 'a' * 64}}}
        doc.update(changes)
        path = self.root / 'attestation.json'
        session.pilot.h.write(path, doc)
        return path

    def test_attested_weight_digests_are_validated_and_carried_without_hashing(self):
        path = self.attestation()
        with patch('joulewise.provenance.model_artifact_identity', side_effect=AssertionError('arm rehashed')):
            self.install(weight_digests_attested=path)
        arm = session.pilot.h.read(self.session / 'staging/v4-arm-001.json')
        self.assertEqual(arm['weight_digests']['source'], 'attested')
        self.assertEqual(arm['weight_digests']['attested_by'], 'Synthetic operator')
        self.assertEqual(arm['weight_digests']['attested_at_epoch_s'], 1234)
        self.assertEqual(arm['weight_digests']['roots'], session.pilot.h.read(path)['roots'])

    def test_bad_weight_attestations_refuse_in_persisted_arm_before_install(self):
        for fault in ('observed', 'registered', 'missing_root', 'blank_name', 'missing_unit', 'other_unit'):
            with self.subTest(fault=fault):
                path = self.attestation()
                doc = session.pilot.h.read(path)
                root = next(iter(doc['roots']))
                if fault in ('observed', 'registered'):
                    doc['roots'][root][fault + '_folded_sha256'] = 'c' * 64
                elif fault == 'missing_root':
                    doc['roots'] = {}
                elif fault == 'blank_name':
                    doc['attested_by'] = ' '
                else:
                    inventory_path = self.root / session.kit.KIT / 'registration/model_artifact_inventory.json'
                    inventory = session.pilot.h.read(inventory_path)
                    if fault == 'missing_unit':
                        del inventory['artifacts']['tiny-two']
                    else:
                        inventory['artifacts']['tiny-two']['folded_sha256'] = 'd' * 64
                    session.pilot.h.write(inventory_path, inventory)
                session.pilot.h.write(path, doc)
                self.installer.reset_mock()
                with patch('joulewise.provenance.model_artifact_identity', side_effect=AssertionError('arm rehashed')):
                    with self.assertRaisesRegex(ValueError, 'weight_digest_preflight:'):
                        self.install(weight_digests_attested=path)
                self.installer.assert_not_called()
                records = sorted((self.session / 'staging').glob('v4-arm-[0-9][0-9][0-9].json'))
                arm = session.pilot.h.read(records[-1])
                self.assertFalse(arm['admitted'])
                self.assertEqual(arm['weight_digests']['source'], 'attested')
                self.assertTrue(any(r.startswith('weight_digest_preflight:') for r in arm['reasons']))

    def test_weight_attestation_cli_option_is_forwarded(self):
        path = self.attestation()
        with patch.object(session, 'install') as install:
            rc = session.main(['install', '--session-root', str(self.session), '--w1-disk-config', 'synthetic',
                '--obc-off-attested-by', 'synthetic', '--battery-log', 'synthetic',
                '--next-arm-triage', 'synthetic', '--weight-digests-attested', str(path)])
        self.assertEqual(rc, 0)
        self.assertEqual(install.call_args.kwargs['weight_digests_attested'], path)

    def dwell(self):
        return json.loads((self.session / 'staging/v4-arm-001.dwell.json').read_bytes())['quiet_dwell']

    def assert_stamps(self):
        dwell = self.dwell()
        self.assertLessEqual(dwell['start_ns'], dwell['installer_end_ns'])
        self.assertLessEqual(dwell['installer_end_ns'], dwell['watchdog_post_install_start_ns'])
        self.assertLessEqual(dwell['watchdog_post_install_start_ns'], dwell['watchdog_post_install_end_ns'])
        self.check.assert_called_once()

    def test_post_install_check_has_both_monotonic_stamps(self):
        self.install()
        self.assertIn('post_install', self.events)
        self.assertLess(self.events.index('stamp'), self.events.index('install'))
        self.assertLess(self.events.index('install'), self.events.index('post_install'))
        dwell = self.dwell()
        self.assertLessEqual(dwell['installer_end_ns'], dwell['watchdog_post_install_end_ns'])
        self.assertTrue(dwell['watchdog_post_install']['ok'])
        self.assert_stamps()
        self.assertEqual(dwell['watchdog_post_install']['evidence_class'], 'installed_plan_parsed_no_fence_yet')
        self.assertAlmostEqual(dwell['watchdog_post_install']['seconds_until_span_begins'], 3420, delta=2)

    def test_fence_evidence_is_distinct_from_pre_span_evidence(self):
        self.check.side_effect = lambda **kw: dict(acceptance(**kw), state='STANDDOWN_REQUEST')
        self.install()
        self.assertEqual(self.dwell()['watchdog_post_install']['evidence_class'], 'fence_observed')
        self.assert_stamps()

    def test_nonfence_at_span_start_undoes_and_restores(self):
        with self.assertRaisesRegex(ValueError, 'watchdog_acceptance: post_install: ACTIVE:.*install undone'):
            self.install(high=True, now=lambda: self.t0 - 180)
        self.restore.assert_called_once()
        self.assert_stamps()

    def test_failed_discovery_undoes_and_restores_with_identity_reason(self):
        plist = self.root / 'magistrate.plist'
        plist.write_bytes(plistlib.dumps({'Label': 'com.joulewise.magistrate',
            'ProgramArguments': ['/synthetic/python3', '/synthetic/magistrate_watchdog.py'],
            'WorkingDirectory': str(self.root),
            'EnvironmentVariables': {'MAGISTRATE_WATCHDOG_CUSTODY_ROOT': str(self.root / 'watchdog')}}))
        self.check.side_effect = lambda **kw: session.watchdog_acceptance(**dict(kw, plist_path=plist))
        def command(argv, **kw):
            if '--dry-run' in argv:
                return subprocess.CompletedProcess(argv, 0, 'decision=ACTIVE reason=x\n', '')
            if '-c' in argv:
                return subprocess.CompletedProcess(argv, 0, json.dumps({'plans': [], 'errors_count': 0,
                    'installed_source': 'not_distinguishable'}), '')
            return self.command(argv, **kw)
        self.run.side_effect = command
        with self.assertRaisesRegex(ValueError, 'watchdog_acceptance: post_install: plan_identity:.*install undone'):
            self.install(high=True)
        self.restore.assert_called_once()
        self.assertEqual(self.dwell()['watchdog_post_install']['install_undo']['remaining_labels'], [])
        self.assert_stamps()

    def test_timeout_is_bounded_refusal_with_undo_and_both_stamps(self):
        plist = self.root / 'magistrate.plist'
        plist.write_bytes(plistlib.dumps({'Label': 'com.joulewise.magistrate',
            'ProgramArguments': ['/synthetic/python3', '/synthetic/magistrate_watchdog.py'],
            'WorkingDirectory': str(self.root),
            'EnvironmentVariables': {'MAGISTRATE_WATCHDOG_CUSTODY_ROOT': str(self.root / 'watchdog')}}))

        def check(**kwargs):
            return session.watchdog_acceptance(**dict(kwargs, plist_path=plist))

        def command(argv, **kwargs):
            if '--dry-run' in argv:
                self.assertLessEqual(kwargs['timeout'], session.WATCHDOG_TIMEOUT_S)
                raise subprocess.TimeoutExpired(argv, kwargs['timeout'])
            return self.command(argv, **kwargs)

        self.check.side_effect = check
        self.run.side_effect = command
        with self.assertRaisesRegex(ValueError, 'TimeoutExpired:.*install undone'):
            self.install(high=True)
        self.assertTrue(any('--uninstall' in event for event in self.events))
        self.restore.assert_called_once()
        self.assert_stamps()

    def test_post_check_signal_still_records_both_stamps_and_undoes(self):
        self.check.side_effect = KeyboardInterrupt('synthetic signal')
        with self.assertRaisesRegex(ValueError, 'KeyboardInterrupt:.*install undone'):
            self.install()
        self.assertTrue(any('--uninstall' in event for event in self.events))
        self.assert_stamps()

    def test_post_install_refusal_uninstalls_both_labels_and_restores(self):
        self.check.side_effect = lambda **kw: dict(acceptance(**kw), ok=False,
            state='HOLD_PLAN_MALFORMED', reason='night_plan_malformed: synthetic')
        with self.assertRaisesRegex(ValueError, 'watchdog_acceptance: post_install: HOLD_PLAN_MALFORMED:.*install undone'):
            self.install(high=True)
        self.assertTrue(any('--uninstall' in event for event in self.events))
        for label in ('com.joulewise.night', 'com.joulewise.night.deadman'):
            self.assertTrue(any(isinstance(event, tuple) and event[-1].endswith('/' + label)
                                for event in self.events))
        self.restore.assert_called_once()
        self.assertFalse(self.dwell()['watchdog_post_install']['ok'])
        self.assert_stamps()

    def test_failed_undo_names_remaining_job_and_still_restores(self):
        self.check.side_effect = lambda **kw: dict(acceptance(**kw), ok=False,
            state='NETWORK_UNCERTAIN', reason='synthetic')
        original = self.command

        def command(argv, **kwargs):
            if argv[-1].endswith('/com.joulewise.night.deadman'):
                return subprocess.CompletedProcess(argv, 0, 'loaded', '')
            return original(argv, **kwargs)

        self.run.side_effect = command
        with self.assertRaisesRegex(ValueError, 'install_undo_failed.*com.joulewise.night.deadman'):
            self.install(high=True)
        self.restore.assert_called_once()
        self.assert_stamps()

    def test_post_check_exception_still_undoes_the_install(self):
        self.check.side_effect = OSError('synthetic watchdog failed')
        with self.assertRaisesRegex(ValueError, 'watchdog_acceptance: post_install: UNAVAILABLE:.*install undone'):
            self.install()
        self.assertTrue(any('--uninstall' in event for event in self.events))
        self.assertFalse(self.dwell()['watchdog_post_install']['ok'])
        self.assert_stamps()

    def test_uninstaller_failure_is_loud_even_if_labels_are_absent(self):
        self.check.side_effect = lambda **kw: dict(acceptance(**kw), ok=False)
        original = self.command

        def command(argv, **kwargs):
            if '--uninstall' in argv:
                return subprocess.CompletedProcess(argv, 4, '', 'synthetic retained plists')
            return original(argv, **kwargs)

        self.run.side_effect = command
        with self.assertRaisesRegex(ValueError, 'install_undo_failed.*com.joulewise.night.deadman'):
            self.install()
        self.assert_stamps()

    def test_failed_host_restore_is_reported_loudly(self):
        self.check.side_effect = lambda **kw: dict(acceptance(**kw), ok=False)
        self.restore.return_value = {'ok': False, 'reason': 'synthetic restore failed'}
        with self.assertRaisesRegex(ValueError, 'install_undo_failed: host Automatic restore failed'):
            self.install(high=True)


if __name__ == '__main__':
    unittest.main()
