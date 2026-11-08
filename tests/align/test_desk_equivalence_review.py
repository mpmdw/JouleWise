"""Cold-review equality witnesses for the stage-parallel v4 desk (eng-desk).

Stronger than test_desk_parallel in four ways:

* the reference is the WHOLE base tree (git archive of the eng-desk merge base,
  run in its own interpreter), not current-serial and not a two-module splice;
* members are heterogeneous: distinct seeds, conditions, pairs, a sampled replay,
  and member-specific GPU-labelled power, so residual fits, LOO, thresholds and
  energy spreads are live and a member/summary swap or a reordered float sum
  changes bytes;
* the compared artifact is the full set of files (path + SHA-256) in the record
  tree after the run, plus stdout and any raised refusal (type, message), across
  workers 1/2/4/8, harvest and --no-harvest, the pending-U3 refusal, the
  isolated-U3 thermal rendering, and an uncaught-member-error refusal;
* worker death and the __main__ spawn path are exercised.

Synthetic fake-native bundles only; nothing measured is read.
"""
from contextlib import nullcontext, redirect_stderr, redirect_stdout
import csv
import io
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import align_pilot_session as pilot
from scripts import bytes_h_session as h


def setUpModule():
    global host_guard
    host_guard = patch('joulewise.align.apple.desk_execution.host_desk_guard', side_effect=lambda _: nullcontext())
    host_guard.start()


def tearDownModule():
    host_guard.stop()

ROOT = Path(__file__).resolve().parents[2]
BASE = '50c99e4f83b9e4d1442745fbe4492e0a1cc6446c'   # merge base of perf/2026-11-08-eng-desk
CASES = ((1, 'benign', 'a', 'spam_filter_update'), (2, 'benign', 'b', 'spam_filter_update'),
         (1, 'sabotage', 'c', 'spam_filter_update'), (2, 'sabotage', 'd', 'spam_filter_update'),
         (1, 'benign', 'replay-a', 'spam_filter_update'), (3, 'benign', 'e', 'spam_filter_update'),
         (1, 'benign', 'bank-a', 'bank_transfer_2'), (2, 'benign', 'bank-b', 'bank_transfer_2'),
         (3, 'benign', 'bank-e', 'bank_transfer_2'), (1, 'sabotage', 'bank-c', 'bank_transfer_2'))

DRIVER = r'''
import hashlib, io, json, shutil, sys
from contextlib import nullcontext, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
tree, template, work, out, workers, harvest, isolate, fault = sys.argv[1:]
work = Path(work)
shutil.rmtree(work, ignore_errors=True)
shutil.copytree(template, work)
if fault == 'member_keyerror':
    path = work/'runs/c/config.json'
    value = json.loads(path.read_bytes()); value.pop('workload_profile'); path.write_text(json.dumps(value))
from scripts import align_v4_session as v4
assert Path(v4.__file__).resolve().is_relative_to(Path(tree).resolve()), v4.__file__
kwargs = dict(harvest=harvest == '1',
              run=lambda argv, **k: SimpleNamespace(returncode=6, stdout='inert receipt\n', stderr=''))
if workers != 'base':
    kwargs['workers'] = int(workers)
stream, error = io.StringIO(), None
with (patch('joulewise.align.apple.v4_registration.validate_u3') if isolate == '1' else nullcontext()), \
        (patch('joulewise.align.apple.desk_execution.host_desk_guard', side_effect=lambda _: nullcontext())
         if workers != 'base' else nullcontext()):
    with redirect_stdout(stream):
        try:
            v4.desk(work/'session', **kwargs)
        except Exception as exc:
            error = [type(exc).__name__, str(exc)]
text = stream.getvalue()
inspection = sorted((work/'session/inspection').iterdir()) if (work/'session/inspection').is_dir() else []
assert len(inspection) <= 1
names = [(p.name.encode(), b'INSPECTION') for p in inspection]
def norm(data):
    for a, b in names:
        data = data.replace(a, b)
    return data
files = {norm(p.relative_to(work).as_posix().encode()).decode(): hashlib.sha256(norm(p.read_bytes())).hexdigest()
         for p in sorted(work.rglob('*')) if p.is_file()}
Path(out).write_text(json.dumps({'stdout': norm(text.encode()).decode(), 'error': error, 'files': files},
                                sort_keys=True))
'''


def crash_member(task):
    """Simulated worker death (OOM kill, segfault) on the third roster member."""
    if task[0]['ordinal'] == 3:
        os._exit(17)
    return pilot._desk_member(task)


def die(item):
    if item == 2:
        os._exit(9)
    return item


def heterogeneous_record(work):
    """Distinct native bundles, member-specific power, refusals; built at ``work``."""
    from tests.align.test_desk_parallel import synthetic_record
    from tests.align.test_pilot4 import native
    work = Path(work).resolve()
    session = synthetic_record(work, 1)     # registration, custody, plan, session scaffold
    shutil.rmtree(work/'runs/m000')
    generated = work.parent/(work.name+'-generated')
    rows = []
    for ordinal, (seed, condition, label, pair) in enumerate(CASES, 1):
        bundle, status, _, _ = native(generated/label, seed=seed, condition=condition, pair=pair)
        assert status.status.value == 'succeeded'
        target = work/'runs'/label
        shutil.copytree(bundle, target)
        episode_path = target/'outputs/align_episode.json'
        episode = json.loads(episode_path.read_bytes())
        episode['episode_id'] = label
        episode_path.write_text(json.dumps(episode)+'\n')
        trace = target/'power_trace.csv'
        with trace.open() as stream:
            reader = csv.DictReader(stream)
            fields, samples = reader.fieldnames, list(reader)
        rng = random.Random(label)
        level = 6 + 4*rng.random()
        for sample in samples:
            sample.update(source='powermetrics', rail='gpu_power',
                          power_w=repr(level + rng.gauss(0, .7) + 1e-9*rng.random()))
        with trace.open('w') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(samples)
        expected = pilot.episode_summary(target)['sampler_seed_inputs']['episode_seed']
        rows.append(dict(run_id=label, task_pair=pair, condition=condition, repeat=1, ordinal=ordinal,
                         block='A', role='D', model_id='synthetic', ac_powermode=0,
                         expected_episode_seed=expected))
    rows.append({**rows[0], 'run_id': 'missing', 'ordinal': len(rows)+1})
    rows.append({**rows[0], 'run_id': 'corrupt', 'ordinal': len(rows)+1})
    shutil.rmtree(generated)
    registration = Path(h.read(session/'session.json')['registration_dir'])
    h.write(registration.parent/'collection_plan.json', {'members': rows})
    h.write(session/'archive/derived/exclusions.json', {'members_excluded': [
        {'run_id': 'b', 'codes': ['battery.member_span']},
        {'run_id': 'missing', 'codes': ['member.runtime_failure']}]})
    (session/'archive/derived/flags.jsonl').write_text(
        json.dumps({'code': 'synthetic.flag', 'scope': {'run_id': 'bank-b'}})+'\n'
        + json.dumps({'code': 'synthetic.session_flag', 'scope': {}})+'\n')
    h.write(session/'archive/withheld/battery-assist.json', {'members': {'b': {'synthetic': True}}})
    (session/'staging').mkdir(exist_ok=True)
    return session


class WholeTreeEquivalenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        probe = subprocess.run(['git', '-C', str(ROOT), 'cat-file', '-e', BASE+'^{commit}'], capture_output=True)
        if probe.returncode:
            raise unittest.SkipTest('base commit object unavailable')
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name).resolve()
        cls.base_tree = cls.root/'base-tree'
        cls.base_tree.mkdir()
        archive = subprocess.run(['git', '-C', str(ROOT), 'archive', BASE, 'scripts', 'joulewise', 'configs'],
                                 check=True, capture_output=True).stdout
        subprocess.run(['tar', '-x', '-C', str(cls.base_tree)], input=archive, check=True)
        cls.work = cls.root/'work'
        heterogeneous_record(cls.work)
        cls.template = cls.root/'template'
        shutil.copytree(cls.work, cls.template)
        cls.template_files = {p.relative_to(cls.template).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in cls.template.rglob('*') if p.is_file()}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_tree(self, tree, workers, harvest, isolate, fault='none'):
        out = self.root/f'result-{tree.name}-{workers}-{harvest}-{isolate}-{fault}.json'
        env = dict(os.environ, PYTHONPATH=str(tree), PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run([sys.executable, '-B', '-c', DRIVER, str(tree), str(self.template), str(self.work),
                                 str(out), workers, harvest, isolate, fault],
                                cwd=tree, env=env, capture_output=True, text=True, timeout=900)
        self.assertEqual(result.returncode, 0, result.stderr[-4000:])
        return json.loads(out.read_text())

    def assert_equivalent(self, harvest, isolate, fault='none', workers=('1', '2', '4', '8')):
        reference = self.run_tree(self.base_tree, 'base', harvest, isolate, fault)
        # Evidence bytes are never altered by the reference itself.
        for path, digest in self.template_files.items():
            if fault == 'none' or path != 'runs/c/config.json':
                self.assertEqual(reference['files'].get(path), digest, path)
        for count in workers:
            with self.subTest(workers=count):
                current = self.run_tree(ROOT, count, harvest, isolate, fault)
                self.assertEqual(current['error'], reference['error'])
                self.assertEqual(current['stdout'], reference['stdout'])
                self.assertEqual(sorted(current['files']), sorted(reference['files']))   # set of files written
                self.assertEqual(current['files'], reference['files'])                   # and their bytes
        return reference

    def test_pending_u3_refusal_with_harvest_matches_whole_base_tree(self):
        reference = self.assert_equivalent('1', '0')
        self.assertIsNone(reference['error'])
        self.assertIn('pilot_status: instrument_incomplete', reference['stdout'])
        self.assertIn('v4_registration_evidence: fail', reference['stdout'])

    def test_isolated_u3_thermal_and_residual_rendering_matches_whole_base_tree(self):
        reference = self.assert_equivalent('1', '1')
        self.assertIsNone(reference['error'])
        # The residual fit, LOO and thresholds are live, not vacuous.
        self.assertIn('leave_one_trajectory_out', reference['stdout'])
        self.assertIn('v4_D_cohort', reference['stdout'])

    def test_no_harvest_inspection_path_matches_whole_base_tree(self):
        reference = self.assert_equivalent('0', '1', workers=('1', '3'))
        self.assertTrue(any(p.startswith('session/inspection/INSPECTION/') for p in reference['files']))

    def test_uncaught_member_error_refuses_identically_across_processes(self):
        reference = self.assert_equivalent('1', '1', 'member_keyerror', workers=('1', '2', '8'))
        self.assertIsNotNone(reference['error'])   # read_bundle_record wraps it (BundleReadError)
        self.assertNotIn('session/PILOT.json', reference['files'])
        self.assertNotIn('session/desk.json', reference['files'])


class WorkerDeathTests(unittest.TestCase):
    def test_worker_death_is_a_refusal_never_a_partial_result(self):
        from concurrent.futures.process import BrokenProcessPool
        from joulewise.align.apple.desk_execution import DeskExecution
        values = []
        with DeskExecution(2) as execution, self.assertRaises(BrokenProcessPool):
            values = execution.map('die', die, [0, 1, 2, 3, 4])
        self.assertEqual(values, [])

    def test_worker_death_mid_desk_publishes_nothing_and_cli_does_not_pass(self):
        from tests.align.test_desk_parallel import synthetic_record
        from scripts import align_v4_session as v4
        from concurrent.futures.process import BrokenProcessPool
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            session = synthetic_record(root/'record', 4)
            output = root/'output'
            with patch.object(pilot, '_desk_member', crash_member), self.assertRaises(BrokenProcessPool):
                v4.desk(session, harvest=False, output=output, workers=2)
            self.assertFalse((output/'PILOT.json').exists())
            self.assertFalse(output.exists())   # L1: even an empty report dir is no longer published
            stderr = io.StringIO()
            with patch.object(pilot, '_desk_member', crash_member), redirect_stderr(stderr):
                code = v4.main(['desk', '--session-root', str(session), '--no-harvest', '--output', str(output),
                                '--workers', '2'])
            self.assertEqual(code, 1)          # BrokenProcessPool is a RuntimeError: refusal, never 0
            self.assertIn('align_pilot_session:', stderr.getvalue())
            self.assertFalse((output/'PILOT.json').exists())
            self.assertFalse((output/'desk.json').exists())
            self.assertFalse((session/'PILOT.json').exists())


class MainModuleSpawnTests(unittest.TestCase):
    """Production runs the desk as ``python scripts/align_v4_session.py desk``:
    the thermal member reader then lives in ``__main__`` and is pickled by
    reference into spawned workers. Exercise exactly that path, with the
    pending U3 gate isolated in the parent so the thermal stage runs."""

    WRAPPER = r'''
import runpy, sys
from contextlib import nullcontext
from unittest.mock import patch
script, *argv = sys.argv[1:]
sys.argv = [script, *argv]
with patch('joulewise.align.apple.v4_registration.validate_u3'), \
        patch('joulewise.align.apple.desk_execution.host_desk_guard', side_effect=lambda _: nullcontext()):
    try:
        runpy.run_path(script, run_name='__main__')
    except SystemExit as exc:
        print('EXIT', exc.code)
'''

    def test_script_entry_with_workers_matches_serial_bytes(self):
        from tests.align.test_desk_parallel import synthetic_record
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            session = synthetic_record(root/'record', 4)
            outputs = []
            for workers in ('1', '2'):
                output = root/f'out-{workers}'
                result = subprocess.run([sys.executable, '-B', '-c', self.WRAPPER, str(ROOT/'scripts/align_v4_session.py'),
                                         'desk', '--session-root', str(session), '--no-harvest', '--output', str(output),
                                         '--workers', workers, '--profile', str(root/f'profile-{workers}.json')],
                                        cwd=root, capture_output=True, text=True, timeout=600,
                                        env=dict(os.environ, PYTHONPATH=str(ROOT)))
                self.assertEqual(result.returncode, 0, result.stderr[-4000:])
                self.assertIn('EXIT 2', result.stdout)
                stages = [s['name'] for s in json.loads((root/f'profile-{workers}.json').read_text())['stages']]
                self.assertIn('v4.thermal_members', stages)
                outputs.append(({p.name: p.read_bytes().replace(str(output).encode(), b'OUT')
                                 for p in output.iterdir()},
                                result.stdout.replace(str(output), 'OUT')))
            self.assertEqual(outputs[0], outputs[1])


class ReplayTargetBindingWitness(unittest.TestCase):
    """HIGH witness (failing first on 2fd82914c). On the MBP a session with a
    pack root derives each member's target-precheck paths from the pack roster
    (``harvest.build_roster``). The laptop replay instead takes them verbatim
    from the operator-authored layout/descriptor and only checks that every
    run_id has *some* list. ``evidence_precheck(bundle, [])`` is eligible
    whenever any precheck row exists, so a descriptor that says ``[]`` turns a
    pack-derived ineligible member into a chain-eligible one: a refusal the
    MBP desk makes is not made by the laptop desk."""

    def test_replay_precheck_matches_pack_derived_mbp_desk(self):
        from joulewise.align.apple.desk_record import describe, replay
        from tests.align.test_desk_parallel import synthetic_record
        from scripts import align_v4_session as v4
        roster = {'members': [{'run_id': f'm{i:03d}', 'cells': [{'target_precheck_path': ['gross_request']}]}
                              for i in range(3)]}
        with tempfile.TemporaryDirectory() as td, \
                patch('joulewise.b5.harvest.build_roster', return_value=roster), \
                redirect_stdout(io.StringIO()):
            root = Path(td).resolve()
            # MBP semantics: in-place desk, targets derived from the pack roster.
            mbp = synthetic_record(root/'mbp', 3)
            state = h.read(mbp/'session.json')
            state['inputs']['pack_root'] = str(root/'mbp/pack')
            h.write(mbp/'session.json', state)
            v4.desk(mbp, harvest=False, output=root/'mbp-out')
            reference = h.read(root/'mbp-out/PILOT.json')
            # Laptop semantics: the same evidence, exported, with a descriptor
            # whose target lists are explicit but not the pack's.
            inputs = root/'inputs'
            session = synthetic_record(inputs, 3)
            state = h.read(session/'session.json')
            state.update(measurement_root='/unavailable/measurement', plan_path='/unavailable/plan.json',
                         registration_dir='/unavailable/registration', runs_roots={'claim': '/unavailable/runs'})
            state['inputs'] = {'custody_root': '/unavailable/custody', 'pack_root': '/unavailable/pack'}
            h.write(session/'session.json', state)
            h.write(inputs/'plan.json', {'custody_root': '/unavailable/custody'})
            value = describe(inputs, dict(session='session', measurement_root='measurement',
                registration_dir='measurement/configs/campaigns/align_v4/registration', runs_root='runs',
                custody_root='custody', plan='plan.json',
                targets={m['run_id']: [] for m in h.read(inputs/'measurement/configs/campaigns/align_v4/collection_plan.json')['members']}))
            repository = root/'repository'
            repository.mkdir()
            env = dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')
            def git(*args):
                return subprocess.run(['git', '-C', str(repository), '-c', 'core.hooksPath=/dev/null',
                    '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid', *args],
                    check=True, capture_output=True, text=True, env=env).stdout.strip()
            git('init', '-q')
            h.write(repository/'record.json', value)
            git('add', 'record.json')
            git('commit', '-qm', 'descriptor')
            try:
                replay(repository, git('rev-parse', 'HEAD'), 'record.json', inputs, root/'laptop-out')
            except ValueError:
                return      # a replay that refuses unverifiable targets also satisfies this witness
            laptop = h.read(root/'laptop-out/PILOT.json')
        def eligibility(report):
            return {m['run_id']: (m['summary'] or {}).get('chain_eligible') for m in report['members']}
        self.assertEqual(eligibility(laptop), eligibility(reference))
        self.assertEqual(laptop['checks']['chain_eligibility'], reference['checks']['chain_eligibility'])


if __name__ == '__main__':
    unittest.main()
