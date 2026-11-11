"""W-1/W-2: synthetic plists and injected commands only; no host probes."""
from contextlib import ExitStack
import json
import os
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from joulewise.align.apple import powermode
from scripts import align_v4_session as session


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
        self.run = Mock(return_value=subprocess.CompletedProcess([], 0,
            'decision=LAUNCHING reason=all launch predicates clear\nWOULD_SPAWN none\n', ''))

    def write_plist(self):
        self.plist.write_bytes(plistlib.dumps(self.document))

    def check(self, phase='pre_install'):
        return session.watchdog_acceptance(phase=phase, runner=self.run, plist_path=self.plist)

    def test_uses_only_installed_program_with_dry_run_and_bounded_environment(self):
        record = self.check()
        self.assertTrue(record['ok'], record)
        argv = self.run.call_args.args[0]
        self.assertEqual(argv, self.document['ProgramArguments'] + ['--dry-run', '--custody-root',
            self.document['EnvironmentVariables']['MAGISTRATE_WATCHDOG_CUSTODY_ROOT']])
        options = self.run.call_args.kwargs
        self.assertEqual(options['cwd'], self.document['WorkingDirectory'])
        self.assertEqual(options['env']['PATH'], '/synthetic/bin')
        self.assertGreater(options['timeout'], 0)
        self.assertLessEqual(options['timeout'], 60)
        self.assertEqual(record['argv'], argv)
        self.assertEqual(record['state'], 'LAUNCHING')
        self.assertGreaterEqual(record['elapsed_s'], 0)
        self.assertFalse(record['plan_read_proven'])

    def test_missing_unreadable_or_invalid_plist_refuses_without_running(self):
        for raw in (None, b'broken', plistlib.dumps({}), plistlib.dumps(dict(self.document,
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
        self.run.return_value = subprocess.CompletedProcess([], 1, 'decision=ACTIVE reason=ok\n', '')
        self.assertFalse(self.check()['ok'])
        self.run.side_effect = subprocess.TimeoutExpired('synthetic', 30)
        self.assertFalse(self.check()['ok'])

    def test_state_policy_is_closed_and_post_install_requires_fence_or_owned_active(self):
        for state in ('HOLD_PLAN_UNREADABLE', 'HOLD_CENSUS', 'STRANDED', 'CLOCK_UNCERTAIN',
                      'NETWORK_UNCERTAIN', 'HOLD_INVENTED', 'STANDDOWN_INVENTED'):
            with self.subTest(state=state):
                self.run.return_value = subprocess.CompletedProcess([], 0, f'decision={state} reason=x\n', '')
                self.assertFalse(self.check()['ok'])
        for state in ('FENCED', 'STANDDOWN_REQUEST', 'STANDDOWN_TERM', 'STANDDOWN_KILL', 'ACTIVE'):
            self.run.return_value = subprocess.CompletedProcess([], 0, f'decision={state} reason=x\n', '')
            self.assertTrue(self.check('post_install')['ok'], state)
        for state in ('LAUNCHING', 'BACKOFF', 'BACKOFF_USAGE', 'STOPPED'):
            self.run.return_value = subprocess.CompletedProcess([], 0, f'decision={state} reason=x\n', '')
            self.assertTrue(self.check()['ok'], state)
            self.assertFalse(self.check('post_install')['ok'], state)

    def test_explicit_custody_argument_is_preserved_and_no_mutating_form_is_built(self):
        self.document['ProgramArguments'] += ['--custody-root', str(self.root / 'explicit')]
        self.write_plist()
        self.assertTrue(self.check()['ok'])
        argv = self.run.call_args.args[0]
        self.assertEqual(argv.count('--dry-run'), 1)
        self.assertEqual(argv.count('--custody-root'), 1)
        self.assertEqual(argv[-1], str(self.root / 'explicit'))


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

    def test_prepare_records_failure_and_keeps_old_host_lock_refusal(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            stack.enter_context(patch.object(powermode, 'host_state_override', return_value=None))
            stack.enter_context(patch.object(powermode, 'HostLock'))
            lock = stack.enter_context(patch.object(powermode, 'host_lock_preflight', return_value={'acquired': True}))
            stack.enter_context(patch.object(session, 'session_start_restore', return_value={'action': 'none'}))
            stack.enter_context(patch.object(session.kit, 'generate'))
            stack.enter_context(patch.object(session, 'series_ac_powermode', return_value=0))
            stack.enter_context(patch.object(session.pilot, 'prepare', return_value={'preparation_status': 'STAGED'}))
            frequency = Mock()
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


if __name__ == '__main__':
    unittest.main()
