"""Synthetic witnesses for the 2026-11-10 measurement-system audit fixes."""
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest import mock

from tests.test_b5_driver import Harness, FakeArm, load_driver
from tests.git_fixture import init_git_fixture


class OutcomeTests(unittest.TestCase):
    def chain_exit(self, h, code):
        # The sandbox cannot census real process groups reliably. Exercise
        # the production terminal/reporting path with a synthetic proven exit.
        def exited(chain, plan, probes, night, claim, **kwargs):
            os.close(claim)
            (night / 'chain.started').write_text('{"pgid": 1}')
            (night / 'chain.exited').write_text(json.dumps({'exit_code': code}))
            return code, None, 0, [], True
        h.driver._run_chain_once = exited

    def test_nonzero_chain_exit_faults_result_hazard_and_courier_without_changing_go(self):
        h = Harness(self, g10=False)
        h.replace_chain("#!/bin/zsh -f\nexit 3\n")
        self.chain_exit(h, 3)
        self.assertEqual(h.driver.EXIT_CHAIN_FAILED, h.run())
        for record in (h.result(), h.hazard(), h.driver.run_courier.call_args.kwargs['report']['facts']):
            self.assertEqual('GO', record['verdict'])
            self.assertEqual('CHAIN_FAILED', record['chain_outcome'])
            reasons = record.get('fault_reasons', record.get('faults', {}).get('reasons'))
            self.assertIn('chain_exit_nonzero:3', reasons)
        self.assertTrue(h.result()['fault'])

    def test_prechain_refusal_faults_without_claiming_chain_started(self):
        h = Harness(self, arm=FakeArm(verdicts={'clock': 'REFUSE'}))
        self.assertEqual(h.driver.EXIT_REFUSED, h.run())
        result = h.result()
        self.assertEqual('REFUSED', result['verdict'])
        self.assertEqual('REFUSED_PRE_CHAIN', result['chain_outcome'])
        self.assertTrue(result['fault'])
        self.assertFalse((h.night / 'chain.started').exists())
        self.assertTrue(h.driver.run_courier.call_args.kwargs['report']['facts']['fault'])

    def test_r1_status_absent_unreadable_or_incomplete_is_a_fault_even_at_exit_zero(self):
        rt = load_driver()
        with tempfile.TemporaryDirectory() as tmp:
            night = Path(tmp)
            (night / 'chain.started').touch()
            payload = night / 'align-r1/r1_result.json'
            payload.parent.mkdir()
            plan = types.SimpleNamespace(plan_id='align-r1-synthetic')
            for status in ('absent', 'unreadable', 'refused', 'aborted', 'running', 'invalid', 'complete'):
                with self.subTest(status=status):
                    payload.unlink(missing_ok=True)
                    if status != 'absent':
                        payload.write_text('{' if status == 'unreadable' else json.dumps({'status': status}))
                    outcome = rt._chain_outcome(plan, night, 'GO', 0)
                    self.assertEqual(status, outcome['measurement_outcome'])
                    self.assertEqual(status != 'complete', outcome['fault'])
                    self.assertEqual('COMPLETE' if status == 'complete' else 'CHAIN_FAILED', outcome['chain_outcome'])

    def test_success_has_no_new_fault_and_non_r1_needs_no_r1_payload(self):
        h = Harness(self, g10=False)
        h.replace_chain("#!/bin/zsh -f\nexit 0\n")
        self.chain_exit(h, 0)
        self.assertEqual(h.driver.EXIT_GO, h.run())
        self.assertEqual('GO', h.result()['verdict'])
        self.assertEqual('COMPLETE', h.result()['chain_outcome'])
        self.assertFalse(h.result()['fault'])
        self.assertIsNone(h.result()['measurement_outcome'])

    def test_r1_refused_payload_faults_all_terminal_records_even_at_chain_exit_zero(self):
        h = Harness(self, g10=False)
        h.replace_chain("#!/bin/zsh -f\nexit 0\n")
        self.chain_exit(h, 0)
        exited = h.driver._run_chain_once
        def with_payload(*args, **kwargs):
            result = exited(*args, **kwargs)
            payload = h.night / 'align-r1/r1_result.json'
            payload.parent.mkdir()
            payload.write_text('{"status":"refused"}')
            return result
        h.driver._run_chain_once = with_payload
        self.assertEqual(h.driver.EXIT_GO, h.run())  # registered exit/verdict policy is unchanged
        for record in (h.result(), h.hazard(), h.driver.run_courier.call_args.kwargs['report']['facts']):
            self.assertEqual('GO', record['verdict'])
            self.assertEqual('refused', record['measurement_outcome'])
            self.assertEqual('CHAIN_FAILED', record['chain_outcome'])
        self.assertIn('r1_status:refused', h.result()['fault_reasons'])


class TerminalDeliveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='w1-delivery-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo, self.remote = self.root / 'source', self.root / 'remote.git'
        self.repo.mkdir()
        init_git_fixture(self.repo, '-q')
        self.git('init', '--bare', '-q', str(self.remote))
        self.git('-C', str(self.repo), 'remote', 'add', 'origin', str(self.remote))
        self.custody = self.root / 'custody'
        self.night = self.custody / 'night'
        self.night.mkdir(parents=True)
        self.result = b'{"verdict":"REFUSED","chain_outcome":"REFUSED_PRE_CHAIN","fault":true}\n'
        (self.night / 'result.json').write_bytes(self.result)
        (self.night / 'refusal.json').write_text('{"reason":"synthetic_clock_refusal"}')
        (self.night / 'chain.stdout.log').write_text('DO NOT EXPORT RAW LOGS')
        self.rt = load_driver()
        patcher = mock.patch.object(self.rt, 'REPO_ROOT', self.repo)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.plan_id = 'align-w1-synthetic'
        self.ref = 'refs/heads/night-results/' + self.plan_id

    def git(self, *args):
        return subprocess.check_output(['git', *args], stderr=subprocess.PIPE)

    def test_prechain_refusal_delivers_within_minute_and_only_then_acknowledges(self):
        started = time.monotonic()
        self.assertEqual(0, self.rt._program_courier_delivery(self.custody, self.plan_id))
        self.assertLess(time.monotonic() - started, 60)
        prefix = 'docs/process_traces/night-results/' + self.plan_id + '/'
        raw = self.git('--git-dir=' + str(self.remote), 'show', self.ref + ':' + prefix + 'result.json')
        self.assertEqual(self.result, raw)
        names = self.git('--git-dir=' + str(self.remote), 'ls-tree', '-r', '--name-only', self.ref).decode()
        self.assertIn('refusal.json', names)
        self.assertNotIn('chain.stdout.log', names)
        self.assertFalse((self.night / 'chain.started').exists())
        self.assertTrue((self.night / 'courier.sent').exists())
        receipt = json.loads((self.night / 'courier.delivery.json').read_text())
        self.assertEqual('git-push', receipt['transport'])
        self.assertEqual(self.ref, receipt['ref'])
        self.assertEqual(self.git('--git-dir=' + str(self.remote), 'rev-parse', self.ref).decode().strip(), receipt['commit'])

    def test_repeat_snapshot_fast_forwards_and_preserves_byte_identical_result(self):
        self.assertIsNone(self.rt._publish_terminal_result(self.custody, self.night, self.plan_id))
        before = self.git('--git-dir=' + str(self.remote), 'rev-parse', self.ref).decode().strip()
        (self.night / 'courier.sent').touch()
        self.assertIsNone(self.rt._publish_terminal_result(self.custody, self.night, self.plan_id))
        parent = self.git('--git-dir=' + str(self.remote), 'rev-parse', self.ref + '^').decode().strip()
        self.assertEqual(before, parent)
        self.assertEqual(self.result, (self.night / 'result.json').read_bytes())

    def test_failed_push_is_filed_and_never_sent(self):
        real = self.rt.t0_rehearsal.observed_run
        budgets = []
        def fail_push(args, **kwargs):
            budgets.append(kwargs['timeout'])
            if 'push' in args:
                raise subprocess.TimeoutExpired(args, kwargs['timeout'])
            return real(args, **kwargs)
        with mock.patch.object(self.rt.t0_rehearsal, 'observed_run', side_effect=fail_push):
            self.assertEqual(1, self.rt._program_courier_delivery(self.custody, self.plan_id))
        self.assertTrue((self.night / 'courier.filed').exists())
        self.assertFalse((self.night / 'courier.sent').exists())
        self.assertFalse((self.night / 'courier.delivery.json').exists())
        self.assertTrue(all(0 < budget <= 50 for budget in budgets))
        self.assertEqual(budgets, sorted(budgets, reverse=True))

    def test_align_finish_reporting_routes_prechain_refusal_to_fast_publisher(self):
        plan = types.SimpleNamespace(plan_id=self.plan_id)
        with mock.patch.object(self.rt, '_publish_terminal_result', return_value=None) as publish:
            self.rt._finish_reporting(self.custody, self.night, plan, self.rt.EXIT_REFUSED, None,
                                      allow_courier=False)
        self.assertGreaterEqual(publish.call_count, 1)
        self.assertEqual(self.plan_id, publish.call_args.args[2])

    def test_changed_result_cannot_reuse_old_delivery_receipt(self):
        self.assertIsNone(self.rt._publish_terminal_result(self.custody, self.night, self.plan_id))
        (self.night / 'result.json').write_text('{"verdict":"REFUSED","revision":2}')
        with mock.patch.object(self.rt, '_publish_terminal_result', return_value='delivery failed') as publish:
            self.assertEqual(1, self.rt._program_courier_delivery(self.custody, self.plan_id))
        publish.assert_called_once()
        self.assertFalse((self.night / 'courier.sent').exists())

    def test_actual_program_courier_parses_prompt_and_pushes_to_local_remote(self):
        # Copy only repo code into an isolated measurement checkout. The sole
        # shell substitution is the interpreter path, for Linux/3.11 CI too.
        scripts = self.repo / 'scripts'
        scripts.mkdir()
        (scripts / '__init__.py').touch()
        source = Path(self.rt.__file__)
        shutil.copyfile(source, scripts / 'run_night.py')
        shell = (source.parent / 'b6_courier.sh').read_text()
        shell = shell.replace('exec /opt/homebrew/bin/python3.13', 'exec ' + shlex.quote(sys.executable))
        courier = scripts / 'b6_courier.sh'
        courier.write_text(shell)
        env = dict(os.environ, PYTHONPATH=str(source.parent.parent))
        result = subprocess.run(['/bin/sh', str(courier), '-p',
                                 f'Custody root: {self.custody}; plan: {self.plan_id}.'],
                                input=b'', cwd=self.repo, env=env, capture_output=True, timeout=20)
        self.assertEqual(0, result.returncode, result.stderr.decode())
        self.assertTrue((self.night / 'courier.sent').exists())
        self.assertEqual(self.ref, json.loads((self.night / 'courier.delivery.json').read_text())['ref'])
        self.git('--git-dir=' + str(self.remote), 'rev-parse', '--verify', self.ref)


if __name__ == '__main__':
    unittest.main()
