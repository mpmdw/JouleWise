"""Independent delta-3 review: synthetic files, fake host, fixture-owned children.

Assertions state required properties; outstanding findings fail visibly. No
launchd calls, real plists, measurements, model loads, or network are used.

Kit-owner adaptation (lead ruling 2026-11-08, delta4): F6's in-process budget
patch is deleted; the production prepare runs in a dedicated child process whose
hard wall timeout is the remaining budget. The capacity witness drove the deleted
in-process path, so it now drives a REAL prepare child that calls the production
``important_capacity`` (its own 30 s timeout, an intercepted 30 s command): the
child is launched with at most the remaining budget and killed whole at it.
Run this module alone, with Python 3.11/3.13 and -B.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import plistlib
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from joulewise.align import w1_prequal as wp, w1_smoke as smoke
from tests.align import test_w1_prequal as prequal_fixtures
from tests.align import test_w1_smoke as fixtures

ROOT = Path(__file__).resolve().parents[2]


class Fixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='smoke-delta3-sol2-')
        self.addCleanup(temporary.cleanup)
        self.tmp = Path(temporary.name).resolve()
        self.home = self.tmp / 'account'
        (self.home / 'Library/LaunchAgents').mkdir(parents=True)
        patch = mock.patch.object(Path, 'home', return_value=self.home)
        patch.start()
        self.addCleanup(patch.stop)
        patch = mock.patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(self.tmp / 'host')})
        patch.start()
        self.addCleanup(patch.stop)
        (self.tmp / 'host').mkdir()
        self.config = smoke.load_config(ROOT)
        # The configured home paths are text only: never resolve their metadata.
        self.config['production_roots'] = [str(self.tmp / 'synthetic-custody')]
        self.production = self.tmp / 'production'
        self.production.mkdir()
        path = self.production / smoke.CONFIG
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(self.config))
        self.prequal = self.tmp / 'prequal.json'
        self.prequal.write_text(json.dumps({'status': 'PASS', 'commit': 'a' * 40,
                                           'next': 'w1', 'checkout_dirty': False}))
        self.clock = fixtures.Clock()
        self.host = fixtures.FakeMBP(self, self.clock)

    def runner(self, **kwargs):
        options = dict(packet={}, battery_log=self.tmp / 'battery', obc_off_attested_by='synthetic',
                       w1_disk_config=self.tmp / 'disk', prequal_report=self.prequal,
                       config=copy.deepcopy(self.config), python=sys.executable, run=self.host,
                       popen=mock.Mock(return_value=fixtures.FakeProcess()),
                       clock=self.clock, sleep=self.clock.sleep,
                       prepare=fixtures.fake_prepare, isolate_fn=fixtures.fake_isolate)
        options.update(kwargs)
        return smoke.SmokeRunner(self.production, self.tmp / 'smoke', **options)

    def staged(self):
        runner = self.runner()
        runner.dir.mkdir()
        runner.make_tmp()
        runner.started = self.clock()
        runner.deadline = runner.started + self.config['budget_s']
        runner.clone = runner.dir / 'measurement'
        state = fixtures.fake_prepare(runner.clone, runner.dir / 'main', self.config['keep'])
        return runner, state

    def publish(self, plan):
        path = self.home / f'Library/LaunchAgents/{smoke.NIGHT_LABEL}.plist'
        path.write_bytes(plistlib.dumps({'ProgramArguments': [sys.executable,
            'scripts/run_night.py', 'run', '--plan', str(plan)]}))
        return path


class WriteWitnesses(Fixture):
    def test_no_follow_and_single_link_controls(self):
        base = self.tmp / 'base'
        base.mkdir()
        victim = self.production / 'victim'
        victim.write_bytes(b'preserve')
        leaf = base / 'leaf'
        leaf.symlink_to(victim)
        directory = base / 'directory'
        directory.symlink_to(self.production, target_is_directory=True)
        hard = base / 'hard'
        os.link(victim, hard)
        for path in (leaf, directory / 'victim', hard):
            with self.subTest(path=path):
                with self.assertRaises(smoke.IsolationAbort):
                    smoke.safe_write(base, path, b'changed')
                self.assertEqual(victim.read_bytes(), b'preserve')
        smoke.safe_write(base, base / 'ordinary', b'one')
        smoke.safe_write(base, base / 'ordinary', b'two', append=True)
        self.assertEqual((base / 'ordinary').read_bytes(), b'onetwo')

    def test_finalize_cannot_follow_an_output_symlink(self):
        runner, state = self.staged()
        victim = self.production / 'finalize-victim'
        victim.write_bytes(b'preserve')
        (runner.dir / 'finalize.json').symlink_to(victim)
        try:
            runner.finalize(state)
        except smoke.IsolationAbort:
            pass
        self.assertEqual(victim.read_bytes(), b'preserve', 'finalize bypassed safe_write')

    def test_unproven_teardown_cannot_follow_an_output_symlink(self):
        runner, state = self.staged()
        runner.installed = state
        self.publish(self.production / 'another/night_plan.json')
        victim = self.production / 'teardown-victim'
        victim.write_bytes(b'preserve')
        (runner.dir / 'teardown-unproven.json').symlink_to(victim)
        try:
            self.assertFalse(runner.teardown_owned())
        except smoke.IsolationAbort:
            pass
        self.assertEqual(victim.read_bytes(), b'preserve', 'recovery receipt bypassed safe_write')
        self.assertFalse(any('--uninstall' in argv for argv in self.host.calls))

    def test_base_ancestor_replacement_cannot_redirect_safe_write(self):
        # This is the runner's write, outside the accepted prepare/installer residual.
        parent = self.tmp / 'parent'
        base = parent / 'smoke'
        base.mkdir(parents=True)
        protected = self.production / 'smoke'
        protected.mkdir()
        parent.rename(self.tmp / 'parent.saved')
        parent.symlink_to(self.production, target_is_directory=True)
        try:
            smoke.safe_write(base, base / 'escape', b'changed')
        except (smoke.IsolationAbort, OSError):
            pass
        self.assertFalse((protected / 'escape').exists(), 'base ancestors were followed by os.open(base)')

    def test_short_write_does_not_silently_truncate_evidence(self):
        base = self.tmp / 'base'
        base.mkdir()
        original = os.write
        # POSIX permits a positive short write. Use a real regular file, limiting
        # each syscall to two bytes; successful safe_write must finish its buffer.
        with mock.patch.object(os, 'write', side_effect=lambda fd, raw: original(fd, raw[:2])):
            smoke.safe_write(base, base / 'evidence', b'complete evidence\n')
        self.assertEqual((base / 'evidence').read_bytes(), b'complete evidence\n')

    def test_fifo_is_refused_without_blocking_before_fstat(self):
        base = self.tmp / 'base'
        base.mkdir()
        fifo = base / 'fifo'
        os.mkfifo(fifo)
        script = ('from joulewise.align import w1_smoke as s\n'
                  'import sys\n'
                  'try: s.safe_write(sys.argv[1],sys.argv[2],b"x")\n'
                  'except (s.IsolationAbort,OSError): sys.exit(0)\n'
                  'sys.exit(2)\n')
        result = smoke.bounded_run([sys.executable, '-B', '-c', script, str(base), str(fifo)], timeout=1)
        self.assertFalse(result.group_survived)
        self.assertEqual(result.returncode, 0, 'opening the FIFO blocked before the regular-file check')


class LifecycleWitnesses(Fixture):
    def test_published_own_plan_without_session_install_record_is_cleaned(self):
        # h.install saves state['install'] only after its installer command
        # returns: interrupt precisely between publication and that save.
        fixture = self

        class PublishedThenInterrupted(fixtures.FakeMBP):
            def install(host, argv):
                session = Path(argv[argv.index('--session-root') + 1])
                state = json.loads((session / 'session.json').read_bytes())
                fixture.publish(state['plan_path'])
                host.job_loaded = True
                result = subprocess.CompletedProcess(argv, 124, '', 'synthetic installer timeout')
                result.group_survived = True
                return result

        self.host = PublishedThenInterrupted(self, self.clock)
        runner = self.runner()
        with mock.patch.object(smoke, 'ARM_FAULTS', []):
            self.assertNotEqual(runner.run(), 0)
        self.assertFalse(self.host.job_loaded, 'published smoke job was not adopted without install state')
        self.assertTrue(any('--uninstall' in argv for argv in self.host.calls))

    def test_a_different_published_plan_is_never_uninstalled_control(self):
        runner, state = self.staged()
        state['install'] = {'exit_code': 0, 'argv': ['installer', '--plan', state['plan_path']]}
        (runner.dir / 'main/session.json').write_text(json.dumps(state))
        other = self.publish(self.production / 'other/night_plan.json')
        before = other.read_bytes()
        runner.pending_install = runner.dir / 'main'
        runner.reconcile_pending_install()
        self.assertFalse(runner.teardown_owned())
        self.assertFalse(any('--uninstall' in argv for argv in self.host.calls))
        self.assertEqual(other.read_bytes(), before)

    def test_budget_uses_monotonic_and_wall_is_separate_control(self):
        runner = self.runner(clock=None)
        self.assertIs(runner.clock, time.monotonic)
        self.assertIs(runner.wall, time.time)
        wall = fixtures.Clock()
        runner = self.runner(wall=wall)
        runner.deadline = self.clock() + 90
        wall.now -= 1_000_000
        self.clock.sleep(10)
        self.assertEqual(runner.remaining(), 80)
        self.clock.sleep(81)
        with self.assertRaises(smoke.BudgetExpired):
            runner.cmd(['synthetic-command'])
        self.assertEqual(self.host.calls, [])

    def test_production_prepare_capacity_probe_uses_remaining_budget(self):
        # Adapted (delta4 ruling): the prepare child is bounded, not patched in-process.
        runner = self.runner(prepare=None)
        runner.config['prepare_reserve_s'] = 1
        runner.dir.mkdir()
        runner.make_tmp()
        runner.clone = runner.dir / 'measurement'
        runner.clone.mkdir()
        runner.deadline = self.clock() + 1.5      # what is left after synthetic preparation work
        marker = self.tmp / 'capacity.json'
        source = (
            'import json, os, subprocess, sys\n'
            'sys.path.insert(0, sys.argv[2])\n'
            'from scripts import bytes_h_session as h\n'
            'def probe(argv, **kw):\n'
            '    json.dump({"pgid": os.getpgrp(), "timeout": kw["timeout"]}, open(sys.argv[1], "w"))\n'
            '    return subprocess.run(["/bin/sleep", "30"], timeout=kw["timeout"])\n'
            'h.important_capacity(sys.argv[1], run=probe)\n')
        runner.prepare_child_argv = lambda session, result, fd: [sys.executable, '-B', '-c', source,
                                                                 str(marker), str(ROOT)]
        observed = []
        real = smoke.grouped_run

        def launch(argv, **kwargs):
            observed.append(kwargs['timeout'])
            return real(argv, **kwargs)

        started = time.monotonic()
        try:
            with mock.patch.object(smoke, 'grouped_run', side_effect=launch):
                with self.assertRaises(smoke.BudgetExpired):
                    runner.prepare_main()
            self.assertEqual(len(observed), 1)
            self.assertLessEqual(observed[0], 5, 'the prepare child outlives the remaining budget')
            self.assertLess(time.monotonic() - started, 6, 'the capacity probe ran to its own 30 s timeout')
            self.assertTrue(marker.is_file(), 'the production capacity probe must have started')
            self.assertEqual(json.loads(marker.read_bytes())['timeout'], 30)
            self.assertFalse(smoke._group_alive(json.loads(marker.read_bytes())['pgid']))
        finally:
            if marker.is_file():
                try:
                    os.killpg(json.loads(marker.read_bytes())['pgid'], signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_isolate_timeout_kills_its_descendant(self):
        runner = self.runner()
        runner.dir.mkdir()
        runner.make_tmp()
        runner.deadline = self.clock() + 1.25
        marker = self.tmp / 'child.json'
        heartbeat = self.tmp / 'heartbeat'
        script = ('import json,os,signal,sys,time\n'
                  'child=os.fork()\n'
                  'if child == 0:\n'
                  ' signal.signal(signal.SIGTERM,signal.SIG_IGN)\n'
                  ' os.close(1); os.close(2)\n'
                  ' with open(sys.argv[1],"w") as f: json.dump({"pgid":os.getpgrp()},f)\n'
                  ' for _ in range(1500):\n'
                  '  with open(sys.argv[2],"a") as f: f.write("x")\n'
                  '  time.sleep(.02)\n'
                  'else: time.sleep(60)\n')
        try:
            try:
                runner.isolate_run([sys.executable, '-B', '-c', script, str(marker), str(heartbeat)])
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass
            self.assertTrue(marker.is_file(), 'descendant did not start; witness invalid')
            before = heartbeat.stat().st_size
            time.sleep(.15)
            self.assertEqual(heartbeat.stat().st_size, before, 'isolate_run killed only the command leader')
        finally:
            if marker.is_file():
                pgid = json.loads(marker.read_bytes())['pgid']
                try:
                    os.killpg(pgid, signal.SIGKILL)  # only the process group created by this test
                except ProcessLookupError:
                    pass


class AdmissionWitnesses(Fixture):
    def bundle(self, name):
        return prequal_fixtures.PortedSolTests.bundle(self, name)

    def context(self, projection=None):
        work = self.tmp / 'work'
        work.mkdir(exist_ok=True)
        return wp.Context(self.tmp / 'proj', work, 'w1', commit='a' * 40, deadline_projection=projection)

    def test_deadline_bundle_controls(self):
        name, plan = self.bundle('controls')
        ctx = self.context(name)
        row = wp.probe('deadline', ctx)
        self.assertEqual(row['status'], wp.PASS, row)
        directory = ctx.repo / name
        session_path = directory / 'session.json'
        state = json.loads(session_path.read_bytes())
        state['plan_sha256'] = '0' * 64
        session_path.write_text(json.dumps(state))
        self.assertEqual(wp.probe('deadline', ctx)['status'], wp.FAIL)
        state['plan_sha256'] = hashlib.sha256((directory / 'night_plan.json').read_bytes()).hexdigest()
        session_path.write_text(json.dumps(state))
        plan['programmed_span_s'] = 0  # a top-level decoy is not a production NightPlan
        (directory / 'night_plan.json').write_text(json.dumps(plan))
        state['plan_sha256'] = hashlib.sha256((directory / 'night_plan.json').read_bytes()).hexdigest()
        session_path.write_text(json.dumps(state))
        self.assertEqual(wp.probe('deadline', ctx)['status'], wp.FAIL)

    def test_deadline_binds_the_plan_option_not_arbitrary_argument_membership(self):
        name, _ = self.bundle('option')
        ctx = self.context(name)
        self.assertEqual(wp.probe('deadline', ctx)['status'], wp.PASS)
        directory = ctx.repo / name
        plist_path = directory / 'com.joulewise.night.plist'
        plist = plistlib.loads(plist_path.read_bytes())
        copied_plan = plist['ProgramArguments'][-1]
        # A stale --plan value, with the copied path in another legal option.
        plist['ProgramArguments'][-1] = str(self.production / 'different/night_plan.json')
        plist['ProgramArguments'] += ['--courier-bin', copied_plan]
        plist_path.write_bytes(plistlib.dumps(plist))
        self.assertEqual(wp.probe('deadline', ctx)['status'], wp.FAIL,
                         'plist --plan differs while plan_path is merely another argv value')

    def test_deadline_binds_the_installer_plan_option(self):
        name, _ = self.bundle('installer-option')
        ctx = self.context(name)
        self.assertEqual(wp.probe('deadline', ctx)['status'], wp.PASS)
        path = ctx.repo / name / 'session.json'
        state = json.loads(path.read_bytes())
        state['install']['argv'] = ['install_night_agent.sh', '--plan',
            str(self.production / 'different/night_plan.json'), '--courier-bin', state['plan_path']]
        path.write_text(json.dumps(state))
        self.assertEqual(wp.probe('deadline', ctx)['status'], wp.FAIL,
                         'installer --plan differs while plan_path is merely another argv value')

    def test_packet_probe_checks_all_362_mutations_on_the_production_arm(self):      # 358 before R22-2 .. R25 grew the packet
        ctx = self.context()
        captured = []
        original = wp._mutations

        def inspect(packet):
            rows = list(original(packet))
            captured.append((copy.deepcopy(packet), rows))
            yield from rows

        with mock.patch.object(wp, '_mutations', inspect):
            row = wp.probe('packet-tamper', ctx)
        self.assertEqual(row['status'], wp.PASS, row)
        self.assertEqual(row['evidence']['mutations_tried'], 362, row)      # 358 before the R24/R25 packet fields
        self.assertEqual(row['evidence']['admitted_mutations'], [])
        self.assertEqual(row['evidence']['zero_capture_attempt'], 'C3')
        packet, rows = captured[0]
        labels = {label for label, _ in rows}

        # Independent walk, including list leaves; do not use the implementation's
        # _leaves to decide what its coverage should contain.
        def leaves(value, path=()):
            if isinstance(value, dict) and value:
                for key, child in value.items():
                    yield from leaves(child, path + (key,))
            elif isinstance(value, list) and value:
                for i, child in enumerate(value):
                    yield from leaves(child, path + (i,))
            else:
                yield path

        for name, entry in packet['checks'].items():
            for path in leaves(entry):
                if path == ('status',):
                    self.assertIn(f'checks.{name}: status flipped', labels)
                    self.assertIn(f'checks.{name}: status removed', labels)
                elif (name,) + path != ('record_committed', 'pushed_tip'):
                    for action in ('changed', 'removed'):
                        self.assertIn(f'checks.{name}.' + '.'.join(map(str, path)) + ' ' + action, labels)
        for key in ('window_chain', 'calibration_windows'):
            for i, entry in enumerate(packet[key]):
                for path in leaves(entry):
                    for action in ('changed', 'removed'):
                        self.assertIn(f'{key}[{i}].' + '.'.join(map(str, path)) + ' ' + action, labels)
        self.assertFalse(any('checks.record_committed.pushed_tip ' in label for label in labels))


if __name__ == '__main__':
    unittest.main()
