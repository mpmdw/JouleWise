"""Portable desk consumer chain: synthetic bytes only, including refusals."""
from contextlib import nullcontext, redirect_stdout
from dataclasses import replace
import hashlib
import io
import json
import math
import os
import random
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from scripts import align_pilot_session as pilot, align_v4_session as v4
from scripts import bytes_h_session as h
from tests.align.test_pilot4 import native


def setUpModule():
    # Synthetic exports never inspect or take the real machine's night lock.
    global host_guard
    host_guard = patch('joulewise.align.apple.desk_execution.host_desk_guard', side_effect=lambda _: nullcontext())
    host_guard.start()


def tearDownModule():
    host_guard.stop()


def work(item):
    delay, value = item
    time.sleep(delay)
    if isinstance(value, str):
        raise ValueError(value)
    return value, os.getpid()


def snapshot(root):
    return {p.relative_to(root).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file()}


def synthetic_record(root, count=6):
    """Captured fake endpoint bundles plus an already committed harvest record."""
    root = Path(root).resolve()
    bundle, status, _, _ = native(root/'generator')
    assert status.status.value == 'succeeded'
    rows = []
    for index in range(count):
        rid = f'm{index:03d}'
        shutil.copytree(bundle, root/'runs'/rid)
        episode_path = root/'runs'/rid/'outputs/align_episode.json'
        episode = json.loads(episode_path.read_bytes())
        episode['episode_id'] = rid
        episode_path.write_text(json.dumps(episode)+'\n')
        rows.append(dict(run_id=rid, task_pair='review', condition='benign', repeat=index+1,
                         ordinal=index+1, role='D', model_id='synthetic', ac_powermode=0))
    rows.append({**rows[0], 'run_id': 'missing', 'ordinal': count+1})
    bad = root/'runs/corrupt/outputs'
    bad.mkdir(parents=True)
    (bad/'align_episode.json').write_text('{bad json')
    rows.append({**rows[0], 'run_id': 'corrupt', 'ordinal': count+2})
    session = root/'session'
    registration = root/'measurement'/v4.kit.KIT/'registration'
    h.write(registration.parent/'collection_plan.json', {'members': rows})
    h.write(root/'plan.json', {'custody_root': str(root/'custody')})
    h.write(root/'custody/night/result.json', {'synthetic': True})
    h.write(session/'session.json', dict(session_id='synthetic', measurement_root=str(root/'measurement'),
        registration_dir=str(registration), plan_path=str(root/'plan.json'),
        inputs={'custody_root': str(root/'custody')}, runs_roots={'claim': str(root/'runs')}))
    h.write(session/'archive/derived/exclusions.json', {'members_excluded': [
        {'run_id': 'm001', 'codes': ['battery.member_span']},
        {'run_id': 'missing', 'codes': ['member.runtime_failure']}]})
    (session/'archive/derived/flags.jsonl').write_text(json.dumps(
        {'code': 'synthetic.flag', 'scope': {'run_id': 'm001'}})+'\n')
    h.write(session/'archive/withheld/battery-assist.json', {'members': {'m001': {'synthetic': True}}})
    # Current U3 intentionally refuses. Tests that exercise later rendering
    # isolate that gate with the same parent-only patch as test_thermal_desk.
    h.write(registration/'u3_bar.json', {})
    from joulewise.align.apple.v4_registration import wp19_identity
    fixture = {'turns': [{'turn': 0, 'prompt_token_ids': [1], 'output_token_ids': [2]}]}
    h.write(registration/'wp19_receipt.json', wp19_identity({'X': fixture, 'Y': fixture},
        {'X': [[1]], 'Y': [[1]]}, fixture['turns'], live_source_sha256='a'*64))
    h.write(registration/'inputs.json', {'R1': {'thermal_policy': {
        'sensors': {'s_fast': 'Tfst', 's_slow': 'Tslw'}, 'delta_slow_c': 2}}})
    from joulewise.align.apple.r1_runtime import SOAK_REFERENCE_SCHEMA
    h.write(registration/'r1_soak_reference.json', {
        'schema': SOAK_REFERENCE_SCHEMA, 'sensors_c': {'Tfst': 40., 'Tslw': 40.}})
    return session


class ExecutionTests(unittest.TestCase):
    def test_pool_is_bounded_and_consumes_in_input_order(self):
        from joulewise.align.apple.desk_execution import DeskExecution
        with DeskExecution(2) as execution:
            result = execution.map('work', work, [(.08, 0), (0, 1), (0, 2), (0, 3)])
        self.assertEqual([v for v, _ in result], [0, 1, 2, 3])
        self.assertLessEqual(len({pid for _, pid in result}), 2)
        self.assertNotIn(os.getpid(), {pid for _, pid in result})

    def test_first_roster_error_wins_even_if_a_later_error_finishes_first(self):
        from joulewise.align.apple.desk_execution import DeskExecution
        for workers in (1, 2):
            with DeskExecution(workers) as execution, self.assertRaisesRegex(ValueError, '^first$'):
                execution.map('errors', work, [(.05, 'first'), (0, 'second')])

    def test_invalid_worker_counts_refuse_before_starting_a_pool(self):
        from joulewise.align.apple.desk_execution import DeskExecution
        for workers in (0, -1, 9, True, 1.5):
            with self.subTest(workers=workers), self.assertRaises(ValueError):
                DeskExecution(workers)

    def test_queued_reads_are_bounded_on_early_refusal(self):
        from joulewise.align.apple.desk_execution import DeskExecution
        consumed = []
        def tasks():
            for i in range(100):
                consumed.append(i)
                yield (0, 'first') if i == 0 else (.01, i)
        with DeskExecution(2) as execution, self.assertRaisesRegex(ValueError, '^first$'):
            execution.map('bounded', work, tasks())
        self.assertEqual(consumed, [0, 1, 2, 3])


class ChainTests(unittest.TestCase):
    def run_chain(self, root, session, workers, output):
        stream = io.StringIO()
        with redirect_stdout(stream):
            v4.desk(session, harvest=False, output=output, workers=workers,
                    profile=root/f'profile-{workers}.json')
        return {p.name: p.read_bytes() for p in output.iterdir()}, stream.getvalue()

    def test_full_consumer_chain_is_byte_equal_and_custody_is_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            session = synthetic_record(root/'record')
            before = snapshot(root/'record')
            output = root/'output'
            serial = self.run_chain(root, session, 1, output)
            shutil.rmtree(output)
            parallel = self.run_chain(root, session, 2, output)
            self.assertEqual(serial, parallel)
            self.assertEqual(snapshot(root/'record'), before)
            report = json.loads(parallel[0]['PILOT.json'])
            self.assertEqual([m['run_id'] for m in report['members']],
                             [f'm{i:03d}' for i in range(6)]+['missing', 'corrupt'])
            self.assertIsNone(report['members'][-1]['summary'])
            self.assertTrue(report['members'][1]['excluded'])
            self.assertIn('U3 PENDING', report['extra_checks']['registration_error'])
            profile = json.loads((root/'profile-2.json').read_text())
            self.assertIn('pilot.members', [s['name'] for s in profile['stages']])
            self.assertNotIn('stages', report)

    def test_full_thermal_rendering_after_isolated_pending_gate_is_byte_equal(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            session = synthetic_record(root/'record')
            output = root/'output'
            with patch('joulewise.align.apple.v4_registration.validate_u3'):
                serial = self.run_chain(root, session, 1, output)
                shutil.rmtree(output)
                parallel = self.run_chain(root, session, 2, output)
            self.assertEqual(serial, parallel)
            self.assertIn('thermal', json.loads(parallel[0]['PILOT.json'])['extra_checks'])

    def test_manifest_entry_point_is_byte_equal_including_missing_members_and_refusals(self):
        from scripts.align_v4_thermal_desk import main
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            synthetic_record(root/'record', 3)
            record = root/'record'
            manifest = record/'manifest.json'
            items = [{'bundle': f'runs/m{i:03d}', 'window': 'W1'} for i in range(3)]
            items.append({'bundle': 'runs/missing', 'id': 'missing', 'model': 'synthetic', 'window': 'W1'})
            manifest.write_text(json.dumps({'members': items}))
            reg = record/'measurement'/v4.kit.KIT/'registration'
            results = []
            with patch('joulewise.align.apple.v4_registration.validate_u3'):
                for workers in (1, 2):
                    output = root/f'desk-{workers}'
                    self.assertEqual(main(['--manifest', str(manifest), '--output', str(output),
                        '--registration-dir', str(reg), '--workers', str(workers)]), 0)
                    results.append({p.name: p.read_bytes() for p in output.iterdir()})
                self.assertEqual(results[0], results[1])
                for workers in (1, 2):
                    manifest.write_text(json.dumps({'members': [
                        {**items[0], 'compare_reference_id': 'unresolved'}]}))
                    with self.assertRaisesRegex(ValueError, '^unresolved compare_reference_id: unresolved$'):
                        main(['--manifest', str(manifest), '--output', str(root/f'bad-{workers}'),
                              '--registration-dir', str(reg), '--workers', str(workers)])

    def test_parallel_independent_reductions_keep_identified_fit_and_loo_bytes(self):
        from joulewise.align import energy_residual as er
        from joulewise.align.apple.desk_execution import DeskExecution
        from tests.align.test_pilot4 import coefficient_bundle
        with tempfile.TemporaryDirectory() as td:
            rng, members = random.Random(512), []
            beta = [2, .05, .2, .00003, .000002]
            for pair in ('spam', 'bank'):
                for condition in ('benign', 'sabotage'):
                    for seed in range(1, 5):
                        rid = f'{pair}-{condition}-{seed}'
                        rows = []
                        for _ in range(8):
                            row = er.TurnRow(rid, pair, rng.randrange(100, 10000), rng.randrange(10, 2000),
                                             rng.randrange(100, 1000), 1, 0, 1, 'additive_bound')
                            rows.append(replace(row, energy_j=math.fsum(x*b for x,b in zip(er.design_row(row), beta))))
                        summary = coefficient_bundle(Path(td)/rid, rid, pair, condition, seed, rows)
                        members.append(dict(run_id=rid, block='A', task_pair=pair, condition=condition, summary=summary))
            members.append({**members[0], 'run_id': 'replay'})
            outputs = []
            for workers in (1, 2):
                with DeskExecution(workers) as execution:
                    outputs.append(execution.map('analysis', pilot._desk_analysis,
                        ((name, members) for name in ('instrument', 'sampling', 'residuals'))))
            self.assertEqual(json.dumps(outputs[0], sort_keys=True), json.dumps(outputs[1], sort_keys=True))
            fit = outputs[1][2][0]['scopes']['registered']['counts_logged_headline']
            self.assertEqual(fit['distinct_trajectories'], 16)
            self.assertEqual(fit['benign_distinct_trajectories'], 8)
            self.assertFalse(any(f.startswith('unidentified_column:') for f in fit['flags']))
            for row in fit['residuals']:
                self.assertNotIn('replay', row['training_trajectories'])


class CommittedRecordTests(unittest.TestCase):
    def record(self, root):
        from joulewise.align.apple.desk_record import describe, finalize
        inputs, repository = root/'inputs', root/'repository'
        session = synthetic_record(inputs, 3)
        # These are inert locator strings. A laptop must never follow them.
        state = h.read(session/'session.json')
        state.update(measurement_root='/unavailable/measurement', plan_path='/unavailable/plan.json',
                     registration_dir='/unavailable/registration', runs_roots={'claim': '/unavailable/runs'})
        state['inputs'] = {'custody_root': '/unavailable/custody'}
        h.write(session/'session.json', state)
        h.write(inputs/'plan.json', {'plan_id': 'synthetic', 'custody_root': '/unavailable/custody'})
        h.write(inputs/'custody/night/result.json', {'plan_id': 'synthetic'})
        for path in ('collection/run_clock.jsonl', 'hazards/monitor/thermal.jsonl', 'hazards/meter/stream-0.jsonl'):
            target = inputs/'custody'/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('')
        h.write(inputs/'custody/night/hazard_result.json', {'meter': {'streams': [
            {'path': 'hazards/meter/stream-0.jsonl', 'sha256': hashlib.sha256(b'').hexdigest()}]}})
        h.write(session/'desk.json', {'plan_id': 'synthetic', 'harvest_status': 'ok', 'harvest_exit': 0})
        for name in ('harvest.stdout', 'harvest.stderr'):
            path = session/'staging'/name
            path.parent.mkdir(exist_ok=True)
            path.write_text('synthetic harvest log\n')
        layout = dict(session='session', measurement_root='measurement',
                         registration_dir='measurement/configs/campaigns/align_v4/registration', runs_root='runs',
                         custody_root='custody', plan='plan.json')
        repository.mkdir()
        h.write(repository/'finalize.json', finalize(inputs, layout))
        layout.update(finalize_manifest='finalize.json', records_ref='refs/remotes/origin/records/synthetic')
        value = describe(inputs, layout, repository=repository)
        env = dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')
        def git(*args):
            return subprocess.run(['git', '-C', str(repository), '-c', 'core.hooksPath=/dev/null',
                '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid', *args],
                check=True, capture_output=True, text=True, env=env).stdout.strip()
        git('init', '-q')
        h.write(repository/'record.json', value)
        git('add', 'record.json', 'finalize.json')
        git('commit', '-qm', 'Synthetic desk record descriptor')
        git('update-ref', layout['records_ref'], 'HEAD')
        return repository, git('rev-parse', 'HEAD'), inputs, value

    def test_committed_record_relocates_all_host_paths_and_is_byte_equal(self):
        from joulewise.align.apple.desk_record import replay
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repository, commit, inputs, _ = self.record(root)
            before = snapshot(inputs)
            output = root/'output'
            results = []
            for workers in (1, 2):
                stream = io.StringIO()
                with redirect_stdout(stream), patch('joulewise.align.apple.v4_registration.validate_u3'):
                    replay(repository, commit, 'record.json', inputs, output, workers=workers)
                self.assertIn('thermal', h.read(output/'PILOT.json')['extra_checks'])
                results.append((snapshot(output), stream.getvalue(),
                                {p.name: p.read_bytes() for p in output.iterdir()}))
                shutil.rmtree(output)
            self.assertEqual(results[0][1:], results[1][1:])
            self.assertEqual(snapshot(inputs), before)

    def test_corruption_unlisted_file_and_missing_terminal_refuse_without_publication(self):
        from joulewise.align.apple.desk_record import replay
        for fault in ('corrupt', 'extra', 'missing', 'symlink'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                repository, commit, inputs, _ = self.record(root)
                if fault == 'corrupt':
                    (inputs/'plan.json').write_text('{}')
                elif fault == 'extra':
                    (inputs/'unexpected.json').write_text('{}')
                elif fault == 'missing':
                    (inputs/'custody/night/result.json').unlink()
                else:
                    (inputs/'link').symlink_to(inputs/'plan.json')
                with self.assertRaises(ValueError):
                    replay(repository, commit, 'record.json', inputs, root/'output', workers=2)
                self.assertFalse((root/'output').exists())

    def test_change_during_replay_refuses_before_atomic_publication(self):
        from joulewise.align.apple.desk_record import replay
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repository, commit, inputs, _ = self.record(root)
            original = pilot._desk
            def changed(*args, **kwargs):
                status = original(*args, **kwargs)
                (inputs/'plan.json').write_text('{}')
                return status
            with patch.object(pilot, '_desk', changed), self.assertRaisesRegex(ValueError, 'digest mismatch'):
                replay(repository, commit, 'record.json', inputs, root/'output')
            self.assertFalse((root/'output').exists())

    def test_descriptor_paths_are_contained(self):
        from joulewise.align.apple.desk_record import relative_path
        for path in ('/absolute', '../escape', 'a/../b', 'a//b', 'a/restricted/b', 'a\\b'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                relative_path(path)

    def test_descriptor_and_replay_cli_preserve_inputs_and_pending_exit_status(self):
        from scripts.align_v4_record_desk import main
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repository, commit, inputs, descriptor = self.record(root)
            layout = root/'layout.json'
            h.write(layout, descriptor)
            before = snapshot(inputs)
            self.assertEqual(main(['--repository', str(repository), '--describe', str(layout), '--inputs', str(inputs),
                                   '--output', str(root/'described.json')]), 0)
            self.assertEqual(h.read(root/'described.json'), descriptor)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(['--repository', str(repository), '--commit', commit,
                    '--record', 'record.json', '--inputs', str(inputs), '--output', str(root/'output')]), 2)
            self.assertEqual(snapshot(inputs), before)


if __name__ == '__main__':
    unittest.main()
