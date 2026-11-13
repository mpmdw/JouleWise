"""Independent delta3 witnesses at 8ebc175c3; synthetic paths and hosts only.

Assertions state the required safety property. Open findings fail visibly, with
no expectedFailure or skip hiding them. The only real children are tiny Python
processes owned and killed by these tests; launchd and real plists are untouched.
Run this module alone: python3.13 -B -m unittest tests.align.test_smoke_delta3_sol1
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import signal
import subprocess
import sys
import time
import unittest
from unittest import mock

from joulewise.align import w1_prequal as wp, w1_smoke as smoke
from tests.align import test_smoke_delta_sol1 as previous
from tests.align import test_w1_prequal as pq_fixtures
from tests.align import test_w1_smoke as fixtures


class WriteSafety(previous.DeltaFixture):
    def test_safe_write_refuses_leaf_parent_symlinks_and_hardlinks(self):
        runner = self.runner()
        runner.dir.mkdir()
        victim = self.production / 'victim'
        victim.write_bytes(b'preserve me')
        leaf = runner.dir / 'leaf'
        leaf.symlink_to(victim)
        parent = runner.dir / 'parent'
        parent.symlink_to(self.production, target_is_directory=True)
        linked = runner.dir / 'hardlink'
        os.link(victim, linked)
        for target in (leaf, parent / 'victim', linked):
            with self.subTest(target=target):
                with self.assertRaises(smoke.IsolationAbort):
                    smoke.safe_write(runner.dir, target, b'overwrite')
                self.assertEqual(victim.read_bytes(), b'preserve me')
        ordinary = runner.dir / 'ordinary'
        smoke.safe_write(runner.dir, ordinary, 'first')
        smoke.safe_write(runner.dir, ordinary, '+second', append=True)
        self.assertEqual(ordinary.read_bytes(), b'first+second')

    def test_finalize_does_not_follow_a_planted_symlink(self):
        runner = self.runner()
        runner.dir.mkdir()
        custody = runner.dir / 'custody'
        custody.mkdir()
        (custody / 'synthetic-evidence').write_bytes(b'evidence')
        victim = self.production / 'finalize-victim'
        victim.write_bytes(b'preserve me')
        (runner.dir / 'finalize.json').symlink_to(victim)
        try:
            runner.finalize({'inputs': {'custody_root': str(custody)}})
        except smoke.IsolationAbort:
            pass
        self.assertEqual(victim.read_bytes(), b'preserve me')

    def test_teardown_recovery_record_does_not_follow_a_planted_symlink(self):
        runner = self.runner()
        runner.dir.mkdir()
        victim = self.production / 'recovery-victim'
        victim.write_bytes(b'preserve me')
        (runner.dir / 'teardown-unproven.json').symlink_to(victim)
        runner.installed = {'plan_path': str(runner.dir / 'own-plan')}
        with mock.patch.object(runner, 'published_plan_owner', return_value='other:synthetic-plan'):
            try:
                runner.teardown_owned()
            except smoke.IsolationAbort:
                pass
        self.assertEqual(victim.read_bytes(), b'preserve me')

    def test_detached_cli_does_not_append_to_a_hardlinked_production_log(self):
        from scripts import align_v4_w1_smoke as cli
        runner = self.runner()
        victim = self.production / 'log-victim'
        victim.write_text('preserve me')
        os.link(victim, runner.dir.with_name(runner.dir.name + '.out'))
        argv = ['run', '--measurement-root', str(self.production), '--smoke-dir', str(runner.dir),
                '--prequal-report', str(self.prequal), '--next-arm-triage', str(self.tmp / 'packet'),
                '--w1-disk-config', str(self.tmp / 'disk'), '--obc-off-attested-by', 'synthetic',
                '--battery-log', str(self.tmp / 'battery'), '--detach']

        def child(_argv, **kwargs):
            kwargs['stdout'].write('synthetic child output')
            kwargs['stdout'].flush()
            return mock.Mock(pid=123)

        # The CLI and detach perform their real file operations; no process is launched.
        with mock.patch.object(smoke.subprocess, 'Popen', side_effect=child), \
                contextlib.redirect_stdout(io.StringIO()):
            cli.main(argv)
        self.assertEqual(victim.read_text(), 'preserve me')

    def test_fault_session_preserves_the_original_smoke_write_anchor(self):
        runner = self.runner()
        runner.dir.mkdir()
        fixtures.fake_prepare(runner.dir / 'measurement', runner.dir / 'main', self.config['keep'])
        victim = self.production / 'fault-victim'
        victim.mkdir()
        root = runner.dir / 'faults'
        real_mkdir = os.mkdir

        def replace_new_fault_root(path, *args, **kwargs):
            result = real_mkdir(path, *args, **kwargs)
            if Path(path) == root:
                root.rmdir()
                root.symlink_to(victim, target_is_directory=True)
            return result

        # Swap only a runner-owned directory, before fault_session's own writes.
        # Production prepare and the installer are never invoked in this witness.
        with mock.patch.object(smoke.os, 'mkdir', side_effect=replace_new_fault_root):
            try:
                runner.arm_fault(smoke.ARM_FAULTS[0], runner.dir / 'main')
            except smoke.IsolationAbort:
                pass
        self.assertEqual(list(victim.iterdir()), [], 'fault_session replaced the supplied smoke anchor')

    def test_safe_write_refuses_fifo_without_blocking(self):
        runner = self.runner()
        runner.dir.mkdir()
        fifo = runner.dir / 'fifo'
        os.mkfifo(fifo)
        script = ('from joulewise.align import w1_smoke as s\n'
                  'try: s.safe_write(' + repr(str(runner.dir)) + ', ' + repr(str(fifo)) + ', b"x")\n'
                  'except s.IsolationAbort: pass\n'
                  'else: raise SystemExit("FIFO accepted")\n')
        # subprocess.run kills/reaps this single child if open(O_WRONLY) blocks.
        try:
            done = subprocess.run([sys.executable, '-B', '-c', script], capture_output=True, text=True, timeout=1)
        except subprocess.TimeoutExpired:
            self.fail('safe_write blocked opening a FIFO before its regular-file check')
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_safe_write_finishes_a_short_write(self):
        runner = self.runner()
        runner.dir.mkdir()
        path = runner.dir / 'record'
        real_write = os.write
        with mock.patch.object(smoke.os, 'write', side_effect=lambda fd, raw: real_write(fd, raw[:3])):
            smoke.safe_write(runner.dir, path, b'complete record')
        self.assertEqual(path.read_bytes(), b'complete record')


class Lifecycle(previous.DeltaFixture):
    def test_publication_before_install_record_is_adopted_and_cleaned(self):
        class PublishesThenTimesOut(fixtures.FakeMBP):
            def install(host, argv):
                session = Path(argv[argv.index('--session-root') + 1])
                state = json.loads((session / 'session.json').read_bytes())
                host.main_state, host.job_loaded = state, True
                plist = Path.home() / 'Library/LaunchAgents/com.joulewise.night.plist'
                plist.write_bytes(plistlib.dumps({'ProgramArguments': [
                    '/synthetic/python', 'run_night.py', 'run', '--plan', state['plan_path']]}))
                # h.install writes state['install'] ONLY AFTER its installer subprocess returns.
                return subprocess.CompletedProcess(argv, 124, '', 'synthetic timeout after publication')

        self.mbp = PublishesThenTimesOut(self, self.clock)
        runner = self.runner()
        with mock.patch.object(smoke, 'ARM_FAULTS', []):
            runner.run()
        self.assertIsNotNone(self.mbp.main_state)
        self.assertNotIn('install', self.mbp.main_state)
        self.assertFalse(self.mbp.job_loaded, 'published own job was never adopted for teardown')

    def test_cleanup_leaves_a_different_published_plan_untouched(self):
        runner = self.runner()
        runner.dir.mkdir()
        state = fixtures.fake_prepare(runner.dir / 'measurement', runner.dir / 'main', self.config['keep'])
        state['install'] = {'argv': ['installer', '--plan', state['plan_path']], 'exit_code': 124}
        (runner.dir / 'main/session.json').write_text(json.dumps(state))
        runner.pending_install = runner.dir / 'main'
        plist = Path.home() / 'Library/LaunchAgents/com.joulewise.night.plist'
        raw = plistlib.dumps({'ProgramArguments': ['python', 'run_night.py', '--plan', '/synthetic/other-plan']})
        plist.write_bytes(raw)
        runner.reconcile_pending_install()
        self.assertFalse(runner.teardown_owned())
        self.assertEqual(plist.read_bytes(), raw)
        self.assertFalse(any('--uninstall' in argv for argv in self.mbp.calls))

    def test_isolation_timeout_kills_its_descendants(self):
        runner = self.runner(clock=time.monotonic)
        runner.dir.mkdir()
        runner.make_tmp()
        runner.deadline = time.monotonic() + 2
        identity = runner.dir / 'child.json'
        script = ('import json,os,signal,time\n'
                  'child=os.fork()\n'
                  'if child == 0:\n'
                  ' signal.signal(signal.SIGTERM,signal.SIG_IGN)\n'
                  ' open(' + repr(str(identity)) + ',"w").write(json.dumps({"pgid":os.getpgrp()}))\n'
                  ' os.close(1); os.close(2)\n'
                  ' time.sleep(30)\n'
                  'else: time.sleep(30)\n')
        try:
            with self.assertRaises(subprocess.TimeoutExpired):
                runner.isolate_run([sys.executable, '-B', '-c', script])
            self.assertTrue(identity.is_file(), 'child must reach the deliberately surviving state')
            pgid = json.loads(identity.read_bytes())['pgid']
            with self.assertRaises(ProcessLookupError, msg='isolate_run killed only the group leader'):
                os.killpg(pgid, 0)
        finally:
            if identity.is_file():
                pgid = json.loads(identity.read_bytes())['pgid']
                try:
                    os.killpg(pgid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                for _ in range(100):
                    if not smoke._group_alive(pgid):
                        break
                    time.sleep(0.01)
                self.assertFalse(smoke._group_alive(pgid), 'fixture cleanup must prove its group gone')

    def test_default_budget_ignores_wall_clock_jumps(self):
        monotonic, wall = [100.0], [1_800_000_000.0]
        with mock.patch.object(smoke.time, 'monotonic', side_effect=lambda: monotonic[0]):
            runner = self.runner(clock=None, wall=lambda: wall[0])
            runner.deadline = 150.0
            for jump in (-1_000_000.0, 2_000_000.0):
                wall[0] += jump
                self.assertEqual(runner.remaining(), 50.0)
            monotonic[0] += 51
            with self.assertRaises(smoke.BudgetExpired):
                runner.require_budget(1, 'synthetic command')


class DeadlineBundle(previous.DeltaFixture):
    def bundle(self, name):
        return pq_fixtures.PortedSolTests.bundle(self, name)

    def probe(self, name):
        return wp.probe('deadline', wp.Context(self.tmp / 'proj', self.tmp / 'work', 'w1',
                                              commit='a' * 40, deadline_projection=name))

    def test_real_plan_bundle_control_and_mismatched_hash(self):
        name, _ = self.bundle('control')
        self.assertEqual(self.probe(name)['status'], wp.PASS)
        path = self.tmp / 'proj' / name / 'session.json'
        session = json.loads(path.read_bytes())
        session['plan_sha256'] = '0' * 64
        path.write_text(json.dumps(session))
        self.assertEqual(self.probe(name)['status'], wp.FAIL)

    def test_only_the_actual_plan_flag_can_bind_the_bundle(self):
        for member in ('plist', 'installer'):
            with self.subTest(member=member):
                name, _ = self.bundle(member)
                directory = self.tmp / 'proj' / name
                session = json.loads((directory / 'session.json').read_bytes())
                # A copied argv can mention the right path but execute a different --plan.
                args = ['program', '--plan', '/synthetic/different/night_plan.json',
                        '--courier-bin', session['plan_path']]
                if member == 'plist':
                    (directory / 'com.joulewise.night.plist').write_bytes(
                        plistlib.dumps({'ProgramArguments': args}))
                else:
                    session['install']['argv'] = args
                    (directory / 'session.json').write_text(json.dumps(session))
                row = self.probe(name)
                self.assertEqual(row['status'], wp.FAIL, row)

    def test_authoritative_hazard_span_controls_sizing(self):
        name, plan = self.bundle('long-span')
        directory = self.tmp / 'proj' / name
        plan['hazard_window']['programmed_span_s'] = 100_000
        raw = json.dumps(plan).encode()
        (directory / 'night_plan.json').write_bytes(raw)
        session = json.loads((directory / 'session.json').read_bytes())
        session['plan_sha256'] = hashlib.sha256(raw).hexdigest()
        (directory / 'session.json').write_text(json.dumps(session))
        row = self.probe(name)
        self.assertEqual(row['status'], wp.FAIL, row)
        self.assertIn('required', row['detail'])


class PacketCoverage(previous.DeltaFixture):
    def test_every_nested_chain_leaf_is_changed_and_removed(self):
        packet = {'checks': {'record_committed': {'status': 'pass', 'pushed_tip': 'ignored',
                   'nested': {'sha256': 'a' * 64, 'items': [1, {'path': 'record.json'}]}}},
                  'window_chain': [{'window': 'C3', 'nested': {'previous_sha256': 'b' * 64, 'empty': []}}],
                  'calibration_windows': [{'window': 'C3', 'captured_members': 0, 'nested': {'status': 'final'}}]}
        mutations = {json.dumps(value, sort_keys=True) for _, value in wp._mutations(packet)}

        # Independent walk and mutation oracle, including nested lists and empty containers.
        def paths(value, path):
            if isinstance(value, dict) and value:
                for key, item in value.items():
                    yield from paths(item, path + (key,))
            elif isinstance(value, list) and value:
                for i, item in enumerate(value):
                    yield from paths(item, path + (i,))
            else:
                yield path

        roots = [('checks', 'record_committed'), ('window_chain', 0), ('calibration_windows', 0)]
        for root in roots:
            node = packet[root[0]][root[1]]
            for path in paths(node, root):
                if path == ('checks', 'record_committed', 'pushed_tip'):
                    continue
                for action in ('changed', 'removed'):
                    edited = copy.deepcopy(packet)
                    parent = edited
                    for step in path[:-1]:
                        parent = parent[step]
                    if action == 'removed':
                        parent.pop(path[-1])
                    else:
                        old = parent[path[-1]]
                        parent[path[-1]] = (old + 1 if isinstance(old, int) else
                            'fail' if old == 'pass' else 'finalx' if old == 'final' else
                            'f' + old[1:] if isinstance(old, str) and len(old) == 64 else
                            old + 'x' if isinstance(old, str) else
                            [{'injected': True}] if old == [] else None)
                    with self.subTest(path=path, action=action):
                        self.assertIn(json.dumps(edited, sort_keys=True), mutations)

    def test_production_packet_has_488_mutations_and_an_admitted_control(self):      # 358 before R22-2 .. R25; 362 before R17 harvest-off (final_record etc.); 440 before claim contract B items 19-21 (cc67ac11e)
        ctx = wp.Context(previous.ROOT, self.tmp / 'packet-work', 'w1')
        ctx.work.mkdir()
        _root, _scenario, _now, _pointer, arm, packet = wp._rebuild(ctx, 'coverage')
        self.assertTrue(wp._triage_ok(arm), arm.get('reasons'))
        self.assertIsNotNone(packet)
        mutations = list(wp._mutations(packet))
        attempt = wp._zero_capture_attempt(packet)
        _holed, removed = wp._omit_attempt(packet, attempt)
        self.assertEqual(attempt, 'C3')
        self.assertGreater(removed, 0)
        self.assertEqual(len(mutations) + 1, 488)  # the omission is the final probe (358 before the R24/R25 packet fields, 362 before the R17 harvest-off fields, 440 before the frozen thermal series fields of claim contract B items 19-21, cc67ac11e, admitted in RL-28)


if __name__ == '__main__':
    unittest.main()
