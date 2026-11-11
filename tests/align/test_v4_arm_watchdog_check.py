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

from joulewise.align.apple import powermode
from scripts import align_v4_session as session
from tests import test_magistrate_watchdog as watchdog_fixtures


def acceptance(*, phase, **_):
    """Explicit seam for older witnesses that isolate other arm gates."""
    return {'ok': True, 'state': 'ACTIVE' if phase == 'post_install' else 'LAUNCHING',
            'reason': 'synthetic watchdog', 'argv': ['synthetic-watchdog', '--dry-run'],
            'elapsed_s': 0.0, 'plan_read_proven': False}


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
        self.plan = {'plan_id': 'synthetic-arm', 't0_epoch_s': session.time.time() + 3600}
        self.discovery = {'plans': [dict(self.plan, span_start_epoch_s=self.plan['t0_epoch_s'] - 180)],
                          'errors_count': 0, 'installed_source': 'not_distinguishable'}
        self.run = Mock(return_value=subprocess.CompletedProcess([], 0,
            'decision=LAUNCHING reason=all launch predicates clear\nWOULD_SPAWN none\n', ''))
        self.run.side_effect = lambda argv, **kw: (subprocess.CompletedProcess(argv, 0,
            json.dumps(self.discovery) + '\n', '') if '-c' in argv else self.run.return_value)

    def write_plist(self):
        self.plist.write_bytes(plistlib.dumps(self.document))

    def check(self, phase='pre_install'):
        return session.watchdog_acceptance(phase=phase, runner=self.run, plist_path=self.plist, plan=self.plan)

    def test_span_boundary_requires_a_fence_in_both_phases(self):
        fences = {'FENCED', 'STANDDOWN_REQUEST', 'STANDDOWN_TERM', 'STANDDOWN_KILL'}
        for phase in ('pre_install', 'post_install'):
            for offset in (-181, -180, -179):
                for state in session.WATCHDOG_STATES:
                    with self.subTest(phase=phase, offset=offset, state=state):
                        self.run.return_value = subprocess.CompletedProcess([], 0, f'decision={state} reason=x\n', '')
                        row = session.watchdog_acceptance(phase=phase, runner=self.run, plist_path=self.plist,
                            plan=self.plan, now=lambda: self.plan['t0_epoch_s'] + offset)
                        admitted = session.WATCHDOG_ADMITTED if offset == -181 else fences
                        self.assertEqual(row['ok'], state in admitted)

    def test_discovery_uses_installed_interpreter_environment_and_identity(self):
        row = self.check('post_install')
        self.assertTrue(row['ok'], row)
        self.assertEqual(row['plan_identity'], {'found': True,
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

    def test_discovery_faults_refuse_in_both_phases(self):
        valid = json.dumps(self.discovery) + '\n'
        for phase in ('pre_install', 'post_install'):
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


class RemoteProbeTests(watchdog_fixtures.WatchdogTestCase):
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

            def check(**kwargs):
                events.append('watchdog')
                return dict(acceptance(**kwargs), ok=False, state='HOLD_PLAN_MALFORMED', reason='synthetic')

            record = session.arm_checks(tmp, {}, runner=lambda argv: subprocess.CompletedProcess(argv, 0, '', ''),
                watchdog_check=check, meter_probe=lambda root: events.append('meter') or {'live': True},
                pre_dwell=lambda record: events.append('write'),
                dwell_start=lambda: events.append('stamp') or session.time.monotonic_ns())
            self.assertEqual(events, ['watchdog', 'meter', 'write', 'stamp'])
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

    def install(self, *, high=False, now=None):
        if high:
            self.plan['runtime_requirements']['ac_powermode'] = 2
        path = self.root / session.kit.KIT / 'collection_plan.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.plan))
        return session.install(self.session, runner=self.run, watchdog_check=self.check, now=now,
            frequency_preflight=lambda *a, **k: {'ok': True},
            frequency_pre_t0=lambda *a, **k: {'ok': True})

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
