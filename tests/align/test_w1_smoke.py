"""Native W1 smoke (Opus build): runner, fault catalogue and parser on a fake MBP.

Every host command (launchctl, pgrep, git, hdiutil, mount, pkill, the production
install CLI) goes to FakeMBP; the clock and sleep are fake; nothing real runs
except the production measurement view and the reducer on a temp directory.
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from joulewise.align import w1_smoke as smoke
from joulewise.align import w1_prequal as wp

ROOT = Path(__file__).resolve().parents[2]
TARGET, CLEAN = 'align-pilot-v3-episodes-a-e01', 'neg8-window-start-r1'
KEPT = {'align-v4-reference-start': [CLEAN], 'align-v4-episodes-a': [TARGET]}


class Clock:
    def __init__(self):
        self.now = 1_800_000_000.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class FakeProcess:
    pid = 4242

    def terminate(self):
        pass

    def wait(self, timeout=None):
        return 0

    def kill(self):
        pass


class FakeMBP:
    """The MBP as the smoke sees it. ``faults`` maps a fault id to (rc, stderr, arm-or-None)."""

    def __init__(self, test, clock, *, job_loaded=False, still_mounted=False, faults=None, main_rc=0,
                 window_s=1500, meter_restarts=1):
        self.test, self.clock, self.calls = test, clock, []
        self.job_loaded, self.still_mounted = job_loaded, still_mounted
        self.faults = faults or {}
        self.main_rc, self.window_s, self.meter_restarts = main_rc, window_s, meter_restarts
        self.main_state = None

    def __call__(self, argv, timeout=None, **kw):
        argv = [str(a) for a in argv]
        self.calls.append(argv)
        done = lambda rc=0, out='', err='': subprocess.CompletedProcess(argv, rc, out, err)
        if argv[:2] == ['launchctl', 'print']:
            return done(0, 'loaded') if self.job_loaded else done(113, '', 'Could not find service "x"')
        if argv[0] == '/usr/bin/pgrep':
            return done(1)
        if argv[0] == 'git' and 'rev-parse' in argv:
            return done(0, 'a' * 40 + '\n')
        if argv[0] == 'git' and 'status' in argv:
            return done(0, '')
        if argv[0] == 'git' and 'clone' in argv:
            from joulewise.align.apple import v4_registration as reg
            clone = Path(argv[-1])
            for path in reg.ARTIFACTS:
                if path.endswith('.md'):
                    (clone / path).parent.mkdir(parents=True, exist_ok=True)
                    (clone / path).write_text('synthetic\n')
            return done(0)
        if argv[0] == 'git':
            return done(0)
        if argv[0] == '/usr/bin/hdiutil':
            return done(0)
        if argv[0] == '/sbin/mount':
            return done(0, '/dev/disk9s1 on /Volumes/JWSMOKE (hfs)\n' if self.still_mounted else '')
        if argv[0] == '/bin/rm':
            shutil.rmtree(argv[-1], ignore_errors=True)
            return done(0)
        if argv[0] == '/usr/bin/pkill':
            return done(0)
        if argv[-1:] and 'align_v4_w1_prequal.py' in ' '.join(argv):
            return done(0, json.dumps({'check': 'r1-w1-chain', 'status': 'PASS', 'detail': 'synthetic'}) + '\n')
        if 'align_v4_session.py' in ' '.join(argv) and 'install' in argv:
            return self.install(argv)
        raise AssertionError(f'FakeMBP: unexpected {argv}')

    def install(self, argv):
        session = Path(argv[argv.index('--session-root') + 1])
        state = json.loads((session / 'session.json').read_text())
        name = state.get('smoke_fault')
        done = lambda rc, err='': subprocess.CompletedProcess(argv, rc, '', err)
        if name is None:                                        # the real arm
            if self.main_rc:
                return done(self.main_rc, 'v4 arm refused: synthetic')
            state['install'] = {'exit_code': 0, 'argv': ['install_night_agent.sh']}
            (session / 'session.json').write_text(json.dumps(state))
            self.main_state = state
            self.build_window(state)
            return done(0)
        rc, err, arm = self.faults.get(name, default_fault(name))
        if arm is not None:
            (session / 'staging').mkdir(exist_ok=True)
            (session / 'staging/v4-arm-001.json').write_text(json.dumps(arm))
        return done(rc, err)

    def build_window(self, state):
        custody = Path(state['inputs']['custody_root'])
        runs = Path(state['inputs']['runs_parent']) / 'claim'
        for run_id in (CLEAN, TARGET):
            (runs / run_id).mkdir(parents=True)
        streams = []
        for index in range(1, 2 + self.meter_restarts):
            path = custody / f'hazards/meter/stream-{index:03d}.jsonl'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'{{"k": "h", "n": {index}}}\n')
            streams.append({'path': path.relative_to(custody).as_posix(),
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        (custody / 'night').mkdir(parents=True, exist_ok=True)
        (custody / 'night/hazard_result.json').write_text(json.dumps({'meter': {
            'starts': 1 + self.meter_restarts, 'restarts': self.meter_restarts, 'streams': streams,
            'stop': {'proven_stopped': True}}}))
        self.clock.now += self.window_s
        (custody / 'night/result.json').write_text(json.dumps({'verdict': 'GO'}))


def default_fault(name):
    fault = next(f for f in smoke.ARM_FAULTS if f['id'] == name)
    if fault['expect'] == 'admit':
        return 1, 'align_pilot_session: plan t0 has passed; prepare again', {'admitted': True, 'reasons': []}
    if fault['expect'] == 'refuse_before_arm':
        return 1, 'align_pilot_session: registration_receipt digest drift: docs/x.md', None
    if fault['expect'] == 'usage':
        return 2, 'error: the following arguments are required: --topup-completed-at', None
    return 1, 'v4 arm refused', {'admitted': False, 'reasons': ['next_arm_triage: ' + fault['needle']]}


def fake_prepare(measurement_root, session_root, keep, **kwargs):
    session = Path(session_root)
    (session / 'staging').mkdir(parents=True)
    custody = session / 'custody'
    custody.mkdir()
    plan = custody / 'night_plan.json'
    plan.write_text(json.dumps({'plan_id': 'align-v4-smoke-20261108T0000Z', 't0_epoch_s': 1_800_000_420}))
    reduction = {'keep': keep, 'kept_runs': KEPT, 'stages': [], 'removed': []}
    (session / 'staging/smoke-reduction.json').write_text(json.dumps(reduction))
    state = {'session_id': 'align-v4-smoke-20261108T0000Z', 'preparation_status': 'STAGED',
             'plan_path': str(plan), 'plan_sha256': hashlib.sha256(plan.read_bytes()).hexdigest(),
             'measurement_root': str(session / 'measurement'), 'source_measurement_root': str(ROOT),
             'inputs': {'custody_root': str(custody), 'runs_parent': str(session / 'runs-parent')},
             't0_epoch_s': 1_800_000_420, 'window_max_s': 44640, 'smoke_reduction': reduction}
    (session / 'session.json').write_text(json.dumps(state))
    return state


def member_reader(state, killed, others):
    rows = {killed: {'dc_status': 'missing', 'dc_flags': ['meter.clock_unresolved'], 'findings': []}}
    rows.update({r: {'dc_status': 'available', 'dc_flags': [], 'findings': ['contention.request_overlap']}
                 for r in others})
    return rows


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='w1smoke-test-'))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        env = mock.patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(self.tmp / 'host-state')})
        env.start()
        self.addCleanup(env.stop)
        (self.tmp / 'host-state').mkdir()
        self.clock = Clock()
        self.prequal = self.tmp / 'prequal-w1.json'
        self.prequal.write_text(json.dumps({'status': 'PASS', 'commit': 'a' * 40, 'next': 'w1',
                                            'checkout_dirty': False}))
        self.popen = mock.Mock(return_value=FakeProcess())

    def runner(self, mbp, **kw):
        return smoke.SmokeRunner(ROOT, self.tmp / 'smoke', packet=wp.triage_packet(), topup_completed_at='1',
                                 topup_source='synthetic', obc_off_attested_by='synthetic',
                                 w1_disk_config=self.tmp / 'disk.json', prequal_report=self.prequal,
                                 python='/fake/python', run=mbp, popen=self.popen, sleep=self.clock.sleep,
                                 clock=self.clock, prepare=fake_prepare, **kw)

    def parse(self):
        return smoke.parse(self.tmp / 'smoke', member_reader=member_reader)

    def test_a_clean_smoke_passes_every_row(self):
        mbp = FakeMBP(self, self.clock)
        self.assertEqual(self.runner(mbp).run(), 0)
        report = self.parse()
        self.assertEqual(report['status'], 'PASS', smoke.render(report))
        names = [r['check'] for r in report['checks']]
        for fault in smoke.ARM_FAULTS:
            self.assertIn('arm-fault:' + fault['id'], names)
        # The contender ran out of tree and was stopped; the meter kill was sent once.
        self.popen.assert_called_once()
        self.assertEqual(self.popen.call_args.args[0], ['/usr/bin/yes'])
        self.assertTrue(self.popen.call_args.kwargs['start_new_session'])
        self.assertIn(['/usr/bin/pkill', '-KILL', '-f', 'scripts/km003c_monitor.py'], mbp.calls)
        steps = [json.loads(l)['step'] for l in (self.tmp / 'smoke' / smoke.LOG).read_text().splitlines()]
        self.assertLess(steps.index('meter-kill'), steps.index('cpu-contender'))     # kill in the first member
        # Every fault attempt used a past-t0 plan copy and its own custody.
        for fault in smoke.ARM_FAULTS:
            state = json.loads((self.tmp / 'smoke/faults' / fault['id'] / 'session/session.json').read_text())
            plan = json.loads(Path(state['plan_path']).read_text())
            self.assertLess(plan['t0_epoch_s'], self.clock.now)
            self.assertNotIn('install', state)
        dmg = [c for c in mbp.calls if c[0] == '/usr/bin/hdiutil']
        self.assertEqual([c[1] for c in dmg], ['create', 'attach', 'detach'])

    def test_guards_abort_during_a_window(self):
        mbp = FakeMBP(self, self.clock, job_loaded=True)
        self.assertEqual(self.runner(mbp).run(), 2)
        self.assertFalse(any('install' in c for c in mbp.calls))
        report = self.parse()
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual({r['check']: r['status'] for r in report['checks']}['gap-guards'], 'FAIL')

    def test_a_stale_or_mismatched_prequal_aborts(self):
        self.prequal.write_text(json.dumps({'status': 'PASS', 'commit': 'b' * 40, 'next': 'w1',
                                            'checkout_dirty': False}))
        self.assertEqual(self.runner(FakeMBP(self, self.clock)).run(), 2)

    def test_a_fault_without_its_documented_refusal_fails_its_row(self):
        mbp = FakeMBP(self, self.clock, faults={
            'triage-edited': (0, '', {'admitted': True, 'reasons': []}),
            'topup-missing': (1, 'v4 arm refused', {'admitted': False, 'reasons': ['something else']})})
        self.runner(mbp).run()
        rows = {r['check']: r['status'] for r in self.parse()['checks']}
        self.assertEqual(rows['arm-fault:triage-edited'], 'FAIL')
        self.assertEqual(rows['arm-fault:topup-missing'], 'FAIL')
        self.assertEqual(rows['arm-fault:triage-stale'], 'PASS')

    def test_a_disk_image_left_mounted_fails(self):
        self.runner(FakeMBP(self, self.clock, still_mounted=True)).run()
        rows = {r['check']: r for r in self.parse()['checks']}
        self.assertEqual(rows['arm-fault:disk-image-mounted']['status'], 'FAIL')
        self.assertIn('STILL MOUNTED', rows['arm-fault:disk-image-mounted']['detail'])

    def test_over_budget_and_unrestarted_meter_fail(self):
        self.runner(FakeMBP(self, self.clock, window_s=3000, meter_restarts=0)).run()
        rows = {r['check']: r['status'] for r in self.parse()['checks']}
        self.assertEqual(rows['wall-time'], 'FAIL')
        self.assertEqual(rows['km003c-reader'], 'FAIL')

    def test_a_refused_main_arm_fails_the_window_rows(self):
        self.runner(FakeMBP(self, self.clock, main_rc=1)).run()
        rows = {r['check']: r['status'] for r in self.parse()['checks']}
        for name in ('arm-main', 'km003c-reader', 'cpu-contender-flagged', 'terminal-marker'):
            self.assertEqual(rows[name], 'FAIL', name)

    def test_member_flags_are_required(self):
        self.runner(FakeMBP(self, self.clock)).run()
        quiet = lambda state, killed, others: {killed: {'dc_status': 'available', 'dc_flags': [], 'findings': []},
                                               **{r: {'dc_status': 'missing', 'findings': []} for r in others}}
        rows = {r['check']: r['status'] for r in smoke.parse(self.tmp / 'smoke', member_reader=quiet)['checks']}
        self.assertEqual(rows['meter-kill-flags-member'], 'FAIL')
        self.assertEqual(rows['cpu-contender-flagged'], 'FAIL')
        self.assertEqual(rows['w1-member-dc-available'], 'FAIL')

    def test_t0_consumed_by_the_faults_restages_the_main_session(self):
        mbp = FakeMBP(self, self.clock)
        runner = self.runner(mbp)
        real = runner.arm_fault

        def slow(fault, session):
            self.clock.now += 40      # 7 attempts eat 280 s of a 420 s lead
            return real(fault, session)
        runner.arm_fault = slow
        runner.run()
        steps = [json.loads(l)['step'] for l in (self.tmp / 'smoke' / smoke.LOG).read_text().splitlines()]
        self.assertIn('prepare-again', steps)
        self.assertTrue((self.tmp / 'smoke/main.superseded').is_dir())
        self.assertEqual(self.parse()['status'], 'PASS')


class PieceTests(unittest.TestCase):
    def test_config_is_labelled_non_registrable(self):
        config = smoke.load_config(ROOT)
        self.assertEqual((config['label'], config['registrable'], config['pooled']), ('smoke', False, False))
        self.assertLessEqual(config['budget_s'], 2700)
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / smoke.CONFIG
            bad.parent.mkdir(parents=True)
            bad.write_text(json.dumps({**config, 'registrable': True}))
            with self.assertRaises(ValueError):
                smoke.load_config(tmp)

    def test_judge_arm_fault_outcomes(self):
        fault = {'expect': 'refuse', 'needle': 'triage x failed'}
        refused = {'admitted': False, 'reasons': ['next_arm_triage: triage x failed']}
        self.assertEqual(smoke.judge_arm_fault(fault, 1, '', refused, {})['outcome'], 'pass')
        self.assertEqual(smoke.judge_arm_fault(fault, 1, '', refused, {'install': {'argv': ['x']}})['outcome'], 'fail')
        self.assertEqual(smoke.judge_arm_fault(fault, 1, '', {'admitted': False, 'reasons': []}, {})['outcome'], 'fail')
        control = {'expect': 'admit', 'needle': 'plan t0 has passed'}
        self.assertEqual(smoke.judge_arm_fault(control, 1, 'plan t0 has passed', {'admitted': True}, {})['outcome'],
                         'pass')
        self.assertEqual(smoke.judge_arm_fault(control, 0, '', {'admitted': True}, {})['outcome'], 'fail')
        self.assertEqual(smoke.judge_arm_fault({'expect': '?', 'needle': ''}, 1, '', None, {})['outcome'], 'fail')

    def test_reduce_view_on_the_production_measurement_view(self):
        from scripts import align_v4_kit as kit, bytes_h_session as h
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp) / 'session'
            session.mkdir()
            with contextlib.redirect_stdout(io.StringIO()):
                view, pack = h.measurement_view(ROOT, session, kit=kit.KIT, pack_id=kit.PACK_ID)
            source_tree = (ROOT / kit.KIT / 'plan_tree.json').read_bytes()
            record = smoke.reduce_view(view, pack, smoke.load_config(ROOT)['keep'])
            self.assertEqual(record['kept_runs'], KEPT)
            self.assertEqual((ROOT / kit.KIT / 'plan_tree.json').read_bytes(), source_tree)   # kit untouched
            tree = json.loads((pack / 'plan_tree.json').read_text())
            self.assertEqual(tree['smoke_label']['registrable'], False)
            self.assertNotIn('align-v4-episodes-b', [s['stage_id'] for s in tree['stage_graph']])
            ids = {m['external_input_id'] for m in tree['external_inputs']['manifests']}
            self.assertTrue(all(m['expected_count'] == len(m['members']) for m in tree['external_inputs']['manifests']),
                            ids)
            with self.assertRaises(ValueError):
                smoke.reduce_view(view, pack, {'align-v4-episodes-a': 99})

    def test_fault_session_is_disposable_and_cannot_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = fake_prepare(ROOT, Path(tmp) / 'main', {})
            state['install'] = {'exit_code': 0}
            (Path(tmp) / 'main/session.json').write_text(json.dumps(state))
            session = smoke.fault_session(Path(tmp) / 'main', 'x', Path(tmp) / 'faults', now=1_900_000_000)
            copied = json.loads((session / 'session.json').read_text())
            self.assertNotIn('install', copied)
            self.assertNotEqual(copied['inputs']['custody_root'], state['inputs']['custody_root'])
            self.assertLess(json.loads(Path(copied['plan_path']).read_text())['t0_epoch_s'], 1_900_000_000)
            self.assertEqual(copied['plan_sha256'], hashlib.sha256(Path(copied['plan_path']).read_bytes()).hexdigest())

    def test_prepare_smoke_requires_the_view_seam(self):
        with self.assertRaisesRegex(ValueError, 'nothing was reduced'):
            smoke.prepare_smoke(ROOT, '/nonexistent', {}, prepare_fn=lambda *a, **k: {})

    def test_cli_faults_and_parse_exit_codes(self):
        from scripts import align_v4_w1_smoke as cli
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(cli.main(['faults']), 0)
        self.assertIn('receipt-digest-mismatch', out.getvalue())
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / smoke.LOG).write_text(json.dumps({'step': 'start', 'outcome': 'info', 'label': 'smoke',
                                                           'registrable': False, 'budget_s': 2700}) + '\n')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(['parse', tmp]), 1)


if __name__ == '__main__':
    unittest.main()


class ProductionReaderTests(unittest.TestCase):
    def test_member_reader_uses_the_production_dc_and_contention_joins(self):
        from tests.align.test_km003c import fake_stream
        NS = 1_000_000_000
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            custody, runs = root / 'custody', root / 'runs-parent/claim'
            stream = custody / 'hazards/meter/stream-001.jsonl'
            stream.parent.mkdir(parents=True)
            fake_stream(stream)
            (custody / 'night').mkdir()
            (custody / 'night/hazard_result.json').write_text(json.dumps({'meter': {'streams': [
                {'path': 'hazards/meter/stream-001.jsonl', 'sha256': hashlib.sha256(stream.read_bytes()).hexdigest()}]}}))
            wp._synthetic_member(runs, 'clean', (NS, 4 * NS), (NS, 2 * NS))
            wp._synthetic_member(runs, 'target', (NS, 6 * NS), (NS, 2 * NS))      # runs past the stream's end
            journal = custody / 'hazards/monitor/contention.jsonl'
            journal.parent.mkdir(parents=True)
            line = {'kind': 'interval', 'started': {'monotonic_ns': int(2.5 * NS)},
                    'finished': {'monotonic_ns': 3 * NS},
                    'values': {'outside_over_limit': [{'cpu_s_per_s': 0.9, 'command': 'yes', 'pid': 1}]}}
            journal.write_text(json.dumps(line) + '\n')
            state = {'inputs': {'custody_root': str(custody), 'runs_parent': str(root / 'runs-parent')}}
            rows = smoke.member_dc_and_contention(state, 'target', ['clean'])
        self.assertEqual(rows['clean']['dc_status'], 'available')
        self.assertIn('contention.request_overlap', rows['clean']['findings'])
        self.assertEqual(rows['target']['dc_status'], 'missing')
        self.assertTrue(any(f.startswith('meter.') for f in rows['target']['dc_flags']))
