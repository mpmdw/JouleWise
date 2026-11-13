"""Cold-review regression witnesses. Synthetic hosts and local Git only."""
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import signal
import shlex
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise.align.apple import powermode, v4_registration
from joulewise.b5 import driver as hazard
from scripts import align_v4_session as session, km003c_monitor as monitor
from tests import test_w1_reliability as r1, test_w1_reliability_r2 as r2, test_w1_reliability_r3 as r3


class HostCloseTests(r2.DriverCase):
    def test_completed_restored_delivered_night_is_byte_stable_on_daily_fires(self):
        h, host = self.make()
        self.assertEqual(h.run(), 0)
        result = (h.night / 'result.json').read_bytes()
        sent = h.night / 'courier.sent'
        sent.write_bytes(b'delivered\n')
        identity = sent.stat()
        before = set(h.night.iterdir())
        host.calls.clear()
        h.driver.run_courier.reset_mock()
        with mock.patch.object(h.driver, '_completion_epoch_s', return_value=0):
            for _ in range(3):
                self.assertEqual(h.driver.dead_man(h.plan_path), 0)
                self.assertEqual(hashlib.sha256((h.night / 'result.json').read_bytes()).digest(),
                                 hashlib.sha256(result).digest())
                self.assertEqual((sent.stat().st_ino, sent.stat().st_mtime_ns),
                                 (identity.st_ino, identity.st_mtime_ns))
                self.assertEqual(sent.read_bytes(), b'delivered\n')
        self.assertEqual(set(h.night.iterdir()), before)
        self.assertEqual(host.calls, [])
        h.driver.run_courier.assert_not_called()

    def test_recovery_preserves_original_result_and_sent_even_when_redelivery_fails(self):
        h, host = self.make()
        h.night.mkdir(exist_ok=True)
        original = b'{"host_restoration":{"ok":false},"fault":true}\n'
        (h.night / 'result.json').write_bytes(original)
        (h.night / 'courier.sent').write_bytes(b'original delivery')
        self.marker(h)
        host.mode = 2
        h.driver.run_courier.return_value = dict(h.sent, sent=False)
        with mock.patch.object(h.driver, '_completion_epoch_s', return_value=0):
            self.assertEqual(h.driver.dead_man(h.plan_path), h.driver.EXIT_COURIER_FAILED)
        self.assertEqual((h.night / 'result.json').read_bytes(), original)
        self.assertEqual((h.night / 'courier.sent').read_bytes(), b'original delivery')
        paths = {x['path'] for x in h.driver._artifact_list(h.custody, h.night)}
        self.assertTrue(any(p.startswith('night/deadman_host_restoration-') for p in paths))

    def test_launch_abandoned_deadman_restores_power_and_preserves_directory(self):
        h, host = self.make()
        h.night.mkdir(exist_ok=True)
        (h.night / h.driver.LAUNCH_ABANDONED_MARKER).write_text('{}')
        self.marker(h, w1=True)
        host.mode = 2
        before = set(h.night.iterdir())
        with mock.patch.object(h.driver, '_completion_epoch_s', return_value=0):
            self.assertEqual(h.driver.dead_man(h.plan_path), 0)
        self.assertEqual(set(h.night.iterdir()), before)
        self.assertEqual(host.mode, 0)
        self.assertFalse(Path(powermode.host_marker_path()).exists())
        self.assertEqual(host.ntp, 'off')
        self.assertNotIn(h.driver.NETWORK_TIME_ON_ARGV, host.calls)
        self.assertIn('restore Automatic', (h.custody / 'night.log').read_text())
        h.driver.run_courier.assert_not_called()

    def test_hazard_unproven_chain_defers_both_settings_through_real_result_close(self):
        h, host = self.make()
        original = h.driver._run_chain_once
        children = []
        def popen(*args, **kwargs):
            process = subprocess.Popen(*args, **kwargs)
            children.append(process)
            return process
        h.driver._hazard_seams = lambda: dataclasses.replace(h.seams(), popen=popen)
        def cleanup():
            for child in children:
                if child.poll() is None:
                    child.terminate()
                child.wait(timeout=5)
        self.addCleanup(cleanup)
        def unproven(*args, **kwargs):
            code, abort, count, hits, _ = original(*args, **kwargs)
            host.mode = 2
            self.marker(h)
            return code, abort, count, hits, False
        h.driver._run_chain_once = unproven
        self.assertNotEqual(h.run(), 0)
        restoration = h.result()['host_restoration']
        self.assertFalse(restoration['ok'])
        self.assertEqual(restoration['chain_termination']['path'], 'hazard')
        self.assertEqual((host.mode, host.ntp), (2, 'off'))
        self.assertTrue(Path(powermode.host_marker_path()).exists())
        h.driver.run_courier.assert_not_called()
        hazard.reap_orphan_monitor(h.night, identity=h.driver.observe_identity)
        hazard.reap_orphan_monitor(h.night, identity=h.driver.observe_identity, journal=hazard.METER_JOURNAL)

    def test_pre_off_refusal_does_not_enable_network_time(self):
        h, host = self.make(arm=r2.FakeArm(verdicts={'clock': 'REFUSE'}))
        self.assertEqual(h.run(), h.driver.EXIT_REFUSED)
        record = h.result()['host_restoration']['network_time']
        self.assertEqual(record['action'], 'left_off')
        self.assertEqual(record['observed'], 'off')
        self.assertTrue(record['verified'])
        self.assertIn('next arm', record['reason'])
        self.assertNotIn('ok', record)
        self.assertNotIn(h.driver.NETWORK_TIME_ON_ARGV, host.calls)

    def test_exit_zero_off_permission_denial_does_not_create_an_on_obligation(self):
        h, host = self.make()
        self.owed(h)
        path = h.night / 'network_time_off.action.json'
        action = json.loads(path.read_bytes())
        action['stdout'] = 'You need administrator access\n'
        path.write_text(json.dumps(action))
        record = h.driver.restore_owed(h.plan, h.driver.make_probes(), {})
        self.assertEqual(record['network_time']['action'], 'left_off')
        self.assertNotIn(h.driver.NETWORK_TIME_ON_ARGV, host.calls)

    def test_rerun_with_old_off_action_does_not_enable_network_time(self):
        h, host = self.make()
        self.assertEqual(h.run(), 0)
        original = (h.night / 'result.json').read_bytes()
        host.ntp = 'off'
        host.calls.clear()
        self.assertEqual(h.run(), h.driver.EXIT_REFUSED)
        self.assertEqual(host.ntp, 'off')
        self.assertNotIn(h.driver.NETWORK_TIME_ON_ARGV, host.calls)
        self.assertEqual((h.night / 'result.json').read_bytes(), original)

    def test_deadman_without_off_action_requires_authenticated_job_absence_for_on(self):
        for absent in (True, False):
            with self.subTest(absent=absent):
                h, host = self.make()
                def run(argv):
                    response = host(argv)
                    if tuple(argv)[:2] == ('launchctl', 'print') and not absent:
                        return dataclasses.replace(response, exit_code=0, stderr='')
                    return response
                h.driver.make_probes = lambda: dataclasses.replace(h.census.probes(), run=run)
                with mock.patch.object(h.driver, '_completion_epoch_s', return_value=0):
                    self.assertEqual(h.driver.dead_man(h.plan_path), 0)
                self.assertEqual(host.ntp, 'on' if absent else 'off')

    def test_escaped_exception_publishes_immediately_after_result(self):
        h, host = self.make()
        def escape(*args, **kwargs):
            kwargs['stage'].update(plan=h.plan, probes=h.driver.make_probes())
            raise RuntimeError('synthetic escape')
        h.driver._run_night = escape
        def publish(*args):
            self.assertTrue((h.night / 'result.json').exists())
            self.assertIn('host_restoration', h.result())
        h.driver._durable_record.side_effect = publish
        with self.assertRaisesRegex(RuntimeError, 'synthetic escape'):
            h.run()
        h.driver._durable_record.assert_called_once()

    def test_term_after_host_close_interrupts_courier(self):
        h, host = self.make()
        write = h.driver._write_json
        def signalled_write(path, value):
            if path.name == 'result.json':
                os.kill(os.getpid(), signal.SIGTERM)  # shield through persistence
            return write(path, value)
        h.driver._write_json = signalled_write
        def interrupted(*args, **kwargs):
            os.kill(os.getpid(), signal.SIGTERM)
        h.driver.run_courier.side_effect = interrupted
        with self.assertRaises(KeyboardInterrupt):
            h.run()
        self.assertTrue(h.result()['host_restoration']['ok'])

    def test_first_meter_batch_required_before_chain_claim(self):
        h, host = self.make()
        h.meter_argv = lambda request: [sys.executable, '-c', 'import time; time.sleep(30)']
        with mock.patch.object(hazard, 'MONITOR_READY_TIMEOUT_S', .25):
            self.assertEqual(h.run(), h.driver.EXIT_REFUSED)
        self.assertFalse((h.night / 'chain.started').exists())
        self.assertIn('meter_not_sampling', h.result()['fault_reasons'])
        self.assertFalse(h.hazard()['meter_stream_readiness']['ready'])

    def test_meter_reenumeration_retries_an_absent_start_before_chain(self):
        h, _ = self.make()
        from tests.test_b5_driver import fake_dc_meter_argv
        attempts = []
        def command(request):
            attempts.append(request)
            if len(attempts) == 1:
                return [sys.executable, '-c', 'raise SystemExit(0)']
            return fake_dc_meter_argv(request)
        h.meter_argv = command
        with mock.patch.object(hazard, 'MONITOR_RESTART_INTERVAL_S', .01):
            self.assertEqual(h.run(), 0)
        self.assertGreaterEqual(len(attempts), 2)
        self.assertTrue(h.hazard()['meter_stream_readiness']['ready'])


class FrequencyTests(r3.FrequencyPreflightTests):
    def test_plan_stream_span_overrides_a_stale_clock_threshold_span(self):
        plan = json.loads(self.path.read_bytes())
        plan['hazard_window']['thresholds']['clock']['t_stream_max_s'] = 1
        self.path.write_text(json.dumps(plan))
        self.state['plan_sha256'] = session.pilot.h.locator(self.path)['sha256']
        record = self.check(r3.Host(0))
        self.assertTrue(record['ok'], record)
        self.assertEqual(record['after_gate']['bound_ms'], 1.441)

    def test_missing_real_budget_has_its_own_cause_and_no_host_calls(self):
        self.path.write_text(json.dumps({'t0_epoch_s': time.time() + 3600}))
        self.state['plan_sha256'] = session.pilot.h.locator(self.path)['sha256']
        host = r3.Host(0)
        record = self.check(host)
        self.assertEqual(record['cause'], 'clock.frequency_plan_invalid')
        self.assertEqual(host.calls, [])

    def test_passing_word_with_network_time_on_turns_it_off_and_authenticates(self):
        host = r3.Host(0)
        on = [True]
        def run(argv):
            if tuple(argv) == r3.QUERY and on[0]:
                return SimpleNamespace(returncode=0, stdout='Network Time: On\n', stderr='')
            if tuple(argv) == r3.network_time_off.OFF_ARGV:
                on[0] = False
            return host(argv)
        record = session.frequency_word_preflight(self.state, reader=host.read, runner=run)
        self.assertTrue(record['ok'], record)
        self.assertFalse(on[0])
        self.assertNotIn(session.ZERO_FREQUENCY_ARGV, host.calls)
        self.assertEqual(record['network_time'], {'observed': 'off', 'verified': True})

    def test_zero_helper_binary_digest_and_source_binding(self):
        helper = self.root / 'zero-helper'
        helper.write_bytes(b'synthetic fixed helper')
        with mock.patch.object(session, 'ZERO_FREQUENCY_ARGV', ('sudo', '-n', str(helper))):
            record = self.check(r3.Host())
        self.assertTrue(record['ok'], record)
        self.assertEqual(record['zero_helper']['sha256'], hashlib.sha256(helper.read_bytes()).hexdigest())
        self.assertIn('scripts/zero_ntp_frequency.c', v4_registration.ARTIFACTS)


class DeliveryTests(r1.TerminalDeliveryTests):
    def test_actual_program_courier_parses_prompt_and_pushes_to_local_remote(self):
        # Execute the real shell body and import the production runner in the
        # child. Only the interpreter and origin checkout are synthetic.
        root = Path(__file__).resolve().parents[1]
        shell = (root / 'scripts/b6_courier.sh').read_text()
        shell = shell.replace('exec /opt/homebrew/bin/python3.13', 'exec ' + shlex.quote(sys.executable))
        self.assertIn('from scripts import run_night\n', shell)
        shell = shell.replace('from scripts import run_night\n',
                              'from scripts import run_night\nrun_night.REPO_ROOT = Path('
                              + json.dumps(str(self.repo)) + ')\n')
        courier = self.repo / 'courier.sh'
        courier.write_text(shell)
        env = dict(os.environ, GIT_ALLOW_PROTOCOL='file',
                   PYTHONPATH=os.pathsep.join(filter(None, [str(root), os.environ.get('PYTHONPATH')])) )
        done = subprocess.run(['/bin/sh', str(courier), '-p',
                               f'Custody root: {self.custody}; plan: {self.plan_id}.'],
                              input=b'', cwd=self.repo, env=env, capture_output=True, timeout=20)
        self.assertEqual(done.returncode, 0, done.stderr.decode())
        receipt = json.loads((self.night / 'courier.delivery.json').read_bytes())
        self.assertEqual(receipt['result_sha256'], hashlib.sha256(self.result).hexdigest())
        self.assertEqual(receipt['ref'], self.ref)
        self.assertTrue((self.night / 'courier.sent').exists())

    def test_unreadable_secondary_artifact_is_named_and_omitted_while_result_delivers(self):
        original = self.rt._artifact_entry
        def unreadable(root, path):
            if path.name == 'refusal.json':
                return {'path': 'night/refusal.json', 'sha256': None, 'error': 'PermissionError'}
            return original(root, path)
        with mock.patch.object(self.rt, '_artifact_entry', side_effect=unreadable):
            self.assertEqual(self.rt._program_courier_delivery(self.custody, self.plan_id), 0)
        prefix = 'docs/process_traces/night-results/' + self.plan_id + '/'
        omissions = json.loads(self.git('--git-dir=' + str(self.remote), 'show',
                                      self.ref + ':' + prefix + 'delivery_omissions.json'))
        self.assertEqual(omissions['omitted_unreadable_artifacts'][0]['path'], 'night/refusal.json')
        self.assertIn('PermissionError', (self.custody / 'night.log').read_text())
        self.assertEqual(self.git('--git-dir=' + str(self.remote), 'show', self.ref + ':' + prefix + 'result.json'),
                         self.result)

    def test_failed_result_read_is_not_delivered(self):
        (self.night / 'result.json').unlink()
        self.assertEqual(self.rt._program_courier_delivery(self.custody, self.plan_id), 1)
        self.assertFalse((self.night / 'courier.sent').exists())

    def test_stderr_tail_and_filed_cleanup_after_retry(self):
        real = self.rt.t0_rehearsal.observed_run
        def failed(argv, **kwargs):
            if 'push' in argv:
                raise subprocess.CalledProcessError(128, argv, stderr='x' * 5000 + 'AUTH DENIED')
            return real(argv, **kwargs)
        with mock.patch.object(self.rt.t0_rehearsal, 'observed_run', side_effect=failed):
            self.assertEqual(self.rt._program_courier_delivery(self.custody, self.plan_id), 1)
        diagnostic = (self.night / 'courier.filed').read_text()
        self.assertIn('AUTH DENIED', diagnostic)
        self.assertLess(len(diagnostic), 3300)
        self.assertEqual(self.rt._program_courier_delivery(self.custody, self.plan_id), 0)
        self.assertFalse((self.night / 'courier.filed').exists())

    def test_failed_courier_process_does_not_consume_wait_budget(self):
        process = mock.Mock()
        process.poll.return_value = 1
        with mock.patch.object(self.rt.time, 'sleep') as sleep:
            self.assertEqual(self.rt._wait_for_courier(self.night / 'heartbeat', self.night / 'sent',
                                                     process=process), (False, False))
        sleep.assert_not_called()


class MeterTests(unittest.TestCase):
    def test_real_monitor_exits_nonzero_after_consecutive_usb_errors_and_resets_counter(self):
        for sequence, expected in (([True] * 5, 5), ([True] * 4 + [False] + [True] * 5, 9)):
            with self.subTest(sequence=sequence), tempfile.TemporaryDirectory() as tmp:
                meter = mock.Mock()
                meter.poll_request.return_value = b'poll'
                meter.usb.read.side_effect = [monitor.usb.UsbError('read', -4) if error else b'empty'
                                             for error in sequence]
                meter.stop_graph.side_effect = monitor.usb.UsbError('cleanup', -4)
                reader = mock.Mock()
                reader.read.return_value = {'values': {k: None for k in monitor.smc.KEYS}, 'errors': {}}
                path = Path(tmp) / 'stream.jsonl'
                with mock.patch.object(monitor, 'init_meter', return_value=(meter, {})), \
                        mock.patch.object(monitor.smc, 'Reader', return_value=reader), \
                        mock.patch.object(monitor.usb, 'parse_put_data', return_value=(b'', 0, True)), \
                        mock.patch.object(monitor.signal, 'signal'), mock.patch.object(monitor.time, 'sleep'):
                    self.assertEqual(monitor.main(['--out', str(path)]), 1)
                rows = [json.loads(line) for line in path.read_text().splitlines()]
                self.assertEqual(rows[-1]['usb_errors'], expected)
                self.assertEqual(rows[-1]['stop_reason'], 'consecutive USB errors')
                meter.usb.close.assert_called_once()

    def test_latest_batch_only_and_sleep_aware_raw_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            now, raw = [1000.], [11_000_000_000]
            path = Path(tmp) / 'stream-001.jsonl'
            header = {'k': 'h', 'status': 'streaming', 'start_raw_ns': raw[0],
                      'start_mono_ns': int(now[0] * 1e9)}
            batch = lambda: {'k': 'b', 'n': 1, 'p': '00' * 20, 'rx': raw[0]}
            path.write_text(json.dumps(header) + '\n' + (json.dumps(batch()) + '\n') * 500)
            live = hazard.MeterLiveness(Path(tmp), clock=lambda: now[0], raw_clock=lambda: raw[0])
            real = hazard.json.loads
            with mock.patch.object(hazard.json, 'loads', wraps=real) as loads:
                self.assertIsNone(live.check())
                self.assertEqual(loads.call_count, 2)  # header + last batch
            now[0] += 10
            raw[0] += 110_000_000_000  # 100 s asleep, monotonic paused
            with path.open('a') as out:
                out.write(json.dumps(batch()) + '\n')
            self.assertIsNone(live.check())
            self.assertEqual(live.last_good['meter'], now[0])

    def test_real_probe_child_is_observed_with_forced_absent_library(self):
        # Real monitor script and child; nonexistent libusb prevents device access.
        real = session.subprocess.run
        from joulewise import t0_rehearsal
        def absent(argv, **kwargs):
            return real([*argv, '--libusb', '/NONEXISTENT-SYNTHETIC-LIBUSB'], **kwargs)
        with mock.patch.object(t0_rehearsal, 'observed_run', side_effect=absent) as observed:
            record = session._probe_meter_live(Path(__file__).resolve().parents[1], seconds=.01)
        self.assertFalse(record['live'])
        self.assertEqual(observed.call_count, 1)
        self.assertIn('scripts/km003c_monitor.py', observed.call_args.args[0][2])


if __name__ == '__main__':
    unittest.main()
