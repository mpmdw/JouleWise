"""Synthetic W1 reliability ruling witnesses; no meter, sudo or custody data.

Real flock and signals are exercised only on temporary files/processes. Chain
termination proofs in driver witnesses are injected because this sandbox's
pgrep cannot census process groups (round-1 report).
"""
import contextlib
import dataclasses
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from joulewise.align.apple import powermode
from joulewise.b5 import driver as hazard
from scripts import align_v4_session as session
from tests.test_b5_driver import FakeArm, Harness
from tests import test_w1_reliability as round1


class Host:
    def __init__(self, h):
        self.h, self.mode, self.ntp, self.calls = h, 0, 'off', []
        self.fail_power, self.fail_ntp, self.bad_ntp_read = False, False, False

    def __call__(self, argv):
        argv = tuple(argv)
        self.calls.append(argv)
        code, out = 0, ''
        if argv == powermode.QUERY:
            out = f'AC Power:\n powermode {self.mode}\n'
        elif argv == powermode.RESTORE_AUTOMATIC:
            code = int(self.fail_power)
            if not code:
                self.mode = 0
        elif argv == self.h.driver.NETWORK_TIME_ON_ARGV:
            code = int(self.fail_ntp)
            if not code:
                self.ntp = 'on'
        elif argv == self.h.driver.NETWORK_TIME_QUERY_ARGV:
            out = 'Network Time: ' + ('Off' if self.bad_ntp_read else self.ntp.title()) + '\n'
        else:
            return self.h.census.run(argv)
        from joulewise.night_gate import ProbeResult
        return ProbeResult(argv, code, out, 'synthetic denial' if code else '', time.monotonic_ns())


class DriverCase(unittest.TestCase):
    def make(self, **kwargs):
        h = Harness(self, g10=False, **kwargs)
        h.replace_chain('#!/bin/zsh -f\nexit 0\n')
        env = mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(h.root / 'host-state')})
        env.start()
        self.addCleanup(env.stop)
        host = Host(h)
        h.driver.make_probes = lambda: dataclasses.replace(h.census.probes(), run=host)
        round1.OutcomeTests.chain_exit(self, h, 0)
        return h, host

    def marker(self, h, *, w1=False):
        path = Path(powermode.host_marker_path())
        powermode.write_host_marker(path, tag=powermode.W1_MARKER_TAG if w1 else powermode.R1_MARKER_TEXT,
                                    owner={'custody_root': h.custody, 'plan_path': h.plan_path})
        return path


class MeterGateTests(DriverCase):
    def test_absent_unreadable_or_unconfigured_reader_refuses_before_chain(self):
        for kind in ('absent', 'exception', 'no-command'):
            with self.subTest(kind=kind):
                h, host = self.make()
                if kind == 'exception':
                    h.meter_probe = mock.Mock(side_effect=OSError('USB unavailable'))
                else:
                    h.meter_probe = lambda root: {'live': kind == 'no-command', 'reason': kind}
                if kind == 'no-command':
                    h.meter_argv = None
                self.assertEqual(h.run(), h.driver.EXIT_REFUSED)
                self.assertFalse((h.night / 'chain.started').exists())
                self.assertIn('meter_not_sampling', h.result()['fault_reasons'])
                self.assertEqual(host.ntp, 'on')

    def test_driver_reuses_the_v4_probe_and_records_its_evidence(self):
        h, _ = self.make()
        h.meter_probe = None
        with mock.patch.object(session, '_probe_meter_live', return_value={'live': False, 'samples': 0}) as probe:
            self.assertEqual(h.run(), h.driver.EXIT_REFUSED)
        probe.assert_called_once_with(h.driver.REPO_ROOT)
        self.assertEqual(h.hazard()['meter_readiness'], {'live': False, 'samples': 0})

    def test_in_window_usb_loss_stops_and_faults_all_terminal_records(self):
        h, host = self.make()
        original = h.driver._run_chain_once

        def outage(*args, **kwargs):
            with mock.patch.object(hazard.MeterLiveness, 'check', return_value={
                    'silent_s': {'meter': 600.0}, 'outage_s': 600.0}):
                abort = kwargs['supervise']()
            code, _, count, hits, proven = original(*args, **kwargs)
            return code, abort, count, hits, proven
        h.driver._run_chain_once = outage
        self.assertEqual(h.run(), h.driver.EXIT_ABORTED)
        for row in (h.result(), h.driver.run_courier.call_args.kwargs['report']['facts']):
            self.assertIn('meter_liveness_outage', row['fault_reasons'])
        self.assertIn('meter_liveness_outage', h.hazard()['faults']['reasons'])
        self.assertEqual(host.ntp, 'on')


class MeterLivenessTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root, self.now = Path(tmp.name), 1000.0
        self.live = hazard.MeterLiveness(self.root, clock=lambda: self.now)
        self.path = self.root / 'stream-001.jsonl'

    def write(self, rows, *, path=None):
        with (path or self.path).open('a') as out:
            for row in rows:
                out.write(json.dumps(row) + '\n')

    def header(self):
        return {'k': 'h', 'status': 'streaming', 'start_raw_ns': 11_000_000_000,
                'start_mono_ns': 1_000_000_000_000}

    def batch(self, *, n=1, seen=None):
        # RAW/monotonic offset from header, with a 20-byte synthetic sample.
        return {'k': 'b', 'n': n, 'p': '00' * 20 * n,
                'rx': int((self.now if seen is None else seen) * 1e9) - 989_000_000_000}

    def test_valid_samples_refresh_but_empty_polls_usb_errors_and_bad_rows_do_not(self):
        self.write([self.header(), self.batch()])
        self.assertIsNone(self.live.check())
        self.now += 599
        self.write([self.batch(n=0), {'k': 'e', 'usb_error': 'unplug'},
                    {'k': 'b', 'n': 1, 'p': 'bad', 'rx': 0}])
        self.assertIsNone(self.live.check())
        self.now += 10
        self.assertEqual(self.live.check()['outage_s'], 600)

    def test_stream_restart_partial_line_and_old_backlog(self):
        self.now += 590
        self.write([self.header(), self.batch(seen=1000)])
        self.assertIsNone(self.live.check())
        self.now += 10
        self.assertIsNotNone(self.live.check())  # old bytes do not refresh the clock
        other = self.root / 'stream-002.jsonl'
        self.write([self.header()], path=other)
        row = json.dumps(self.batch())
        with other.open('a') as out:
            out.write(row)
        self.now += 10
        self.assertIsNotNone(self.live.check())  # partial batch does not count
        with other.open('a') as out:
            out.write('\n')
        self.now += 10
        self.assertIsNotNone(self.live.check())  # recovery cannot erase the already observed outage
        self.assertEqual(self.live.last_good['meter'], 1600.0)

    def test_gap_over_bound_is_not_hidden_by_a_recovered_batch_before_the_next_check(self):
        self.write([self.header(), self.batch()])
        self.live.check()
        self.now += 601
        self.write([self.batch()])
        self.assertTrue(self.live.check()['recovered'])

    def test_unreadable_absent_and_truncated_streams_reach_the_bound(self):
        for kind in ('unreadable', 'absent', 'truncated'):
            with self.subTest(kind=kind):
                self.now = 1000.0
                live = hazard.MeterLiveness(self.root, clock=lambda: self.now)
                self.path.write_text('')
                self.write([{'k': 'h', 'status': 'absent'}] if kind == 'absent'
                           else [self.header(), self.batch()])
                live.check()
                if kind == 'truncated':
                    self.path.write_text('{}\n')
                self.now += 600
                patch = mock.patch.object(Path, 'open', side_effect=PermissionError('synthetic'))
                with patch if kind == 'unreadable' else contextlib.nullcontext():
                    self.assertIsNotNone(live.check())


class TerminalRestoreTests(DriverCase):
    def test_a_signal_during_terminal_restore_cannot_interrupt_network_time_restoration(self):
        h, host = self.make()

        def signalled(argv):
            result = host(argv)
            if tuple(argv) == powermode.RESTORE_AUTOMATIC:
                os.kill(os.getpid(), signal.SIGTERM)
            return result
        h.driver.make_probes = lambda: dataclasses.replace(h.census.probes(), run=signalled)
        self.assertEqual(h.run(), 0)
        self.assertTrue(h.result()['host_restoration']['ok'])
        self.assertEqual(host.ntp, 'on')

    def test_normal_mode_zero_r1_chain_restores_both_before_delivery(self):
        h, host = self.make()
        original = h.driver._run_chain_once
        markers = []

        def chain(*a, **kw):
            host.mode = 2  # R1 changes mode inside a declared-mode-0 chain
            markers.append(self.marker(h))
            local = h.measurement / powermode.R1_HIGH_POWER_MARKER
            local.write_text(powermode.R1_MARKER_TEXT)
            markers.append(local)
            return original(*a, **kw)
        h.driver._run_chain_once = chain

        def deliver(*args, **kwargs):
            self.assertEqual((host.mode, host.ntp), (0, 'on'))
            self.assertTrue(h.result()['host_restoration']['ok'])
            self.assertTrue(kwargs['report']['facts']['host_restoration']['ok'])
            return h.sent
        h.driver.run_courier.side_effect = deliver
        self.assertEqual(h.run(), 0)
        self.assertTrue(all(not p.exists() for p in markers))
        self.assertEqual(host.calls.count(powermode.RESTORE_AUTOMATIC), 1)

    def test_refusal_and_failed_readbacks_are_recorded_and_keep_owed_marker(self):
        for failure in ('none', 'power', 'ntp', 'ntp-read'):
            with self.subTest(failure=failure):
                h, host = self.make(arm=FakeArm(verdicts={'clock': 'REFUSE'}))
                marker = self.marker(h)
                host.fail_power = failure == 'power'
                host.fail_ntp = failure == 'ntp'
                host.bad_ntp_read = failure == 'ntp-read'
                self.assertEqual(h.run(), h.driver.EXIT_REFUSED)
                record = h.result()['host_restoration']
                self.assertEqual(record['ok'], failure == 'none')
                self.assertEqual(marker.exists(), failure == 'power')
                self.assertIn(h.driver.NETWORK_TIME_QUERY_ARGV, host.calls)
                if failure != 'none':
                    self.assertIn('host_restoration_incomplete', h.result()['fault_reasons'])

    def test_unproven_chain_lock_holder_and_other_w1_owner_defer_both_settings(self):
        for reason in ('unproven', 'lock', 'owner'):
            with self.subTest(reason=reason):
                h, host = self.make()
                host.mode = 2
                marker = self.marker(h, w1=reason == 'owner')
                holder = None
                if reason == 'unproven':
                    h.driver._CHAIN_TERMINATION_UNPROVEN = {'path': 'interrupt'}
                elif reason == 'lock':
                    holder = powermode.HostLock()
                    self.assertTrue(holder.acquire())
                else:
                    powermode.write_host_marker(marker, tag=powermode.W1_MARKER_TAG,
                                                owner={'custody_root': h.root / 'other'})
                try:
                    record = h.driver._close_ac_powermode(h.plan, h.driver.make_probes(), {})
                finally:
                    if holder:
                        holder.release()
                    h.driver._CHAIN_TERMINATION_UNPROVEN = None
                self.assertFalse(record['ok'])
                self.assertEqual((host.mode, host.ntp), (2, 'off'))
                self.assertTrue(marker.exists())
                self.assertNotIn(powermode.RESTORE_AUTOMATIC, host.calls)

    def test_signal_and_exception_paths_leave_a_result_with_restore_evidence(self):
        for kind in ('TERM', 'HUP', 'exception'):
            with self.subTest(kind=kind):
                h, host = self.make()
                def interrupted(*a, **kw):
                    kw['stage'].update(plan=h.plan, probes=h.driver.make_probes())
                    host.mode = 2
                    self.marker(h)
                    if kind == 'exception':
                        raise RuntimeError('synthetic early exception')
                    os.kill(os.getpid(), signal.SIGTERM if kind == 'TERM' else signal.SIGHUP)
                h.driver._run_night = interrupted
                with self.assertRaises(RuntimeError if kind == 'exception' else KeyboardInterrupt):
                    h.run()
                self.assertEqual((host.mode, host.ntp), (0, 'on'))
                self.assertTrue(h.result()['host_restoration']['ok'])

    def test_deadman_restores_r1_and_w1_even_with_prior_courier_sent(self):
        for w1 in (False, True):
            with self.subTest(w1=w1):
                h, host = self.make()
                host.mode = 2
                marker = self.marker(h, w1=w1)
                h.night.mkdir(exist_ok=True)
                (h.night / 'chain.started').write_text('{"pgid": 123456789}')
                (h.night / 'courier.sent').write_text('old delivery')
                with mock.patch.object(h.driver, '_completion_epoch_s', return_value=0), \
                        mock.patch.object(h.driver.os, 'killpg', side_effect=ProcessLookupError), \
                        mock.patch.object(hazard, 'reap_orphan_monitor', return_value=None):
                    self.assertEqual(h.driver.dead_man(h.plan_path), 0)
                self.assertEqual((host.mode, host.ntp), (0, 'on'))
                self.assertFalse(marker.exists())
                self.assertTrue(h.result()['dead_man_host_restoration']['ok'])
                self.assertTrue(h.driver.run_courier.called)

    def test_deadman_refuses_live_chain_and_records_why_without_claiming_its_result_slot(self):
        h, host = self.make()
        marker = self.marker(h)
        host.mode = 2
        h.night.mkdir(exist_ok=True)
        (h.night / 'chain.started').write_text('{"pgid": 42}')
        with mock.patch.object(h.driver, '_completion_epoch_s', return_value=0), \
                mock.patch.object(h.driver.os, 'killpg', return_value=None):
            self.assertEqual(h.driver.dead_man(h.plan_path), h.driver.EXIT_REFUSED)
        self.assertEqual((host.mode, host.ntp), (2, 'off'))
        self.assertTrue(marker.exists())
        self.assertFalse((h.night / 'result.json').exists())
        records = list(h.night.glob('deadman_host_restoration-*.json'))
        self.assertIn('deferred', json.loads(records[0].read_bytes()))

    def test_sigkill_leaves_obligation_and_deadman_takes_the_released_real_flock(self):
        h, host = self.make()
        marker = Path(powermode.host_marker_path())
        code = '''
import sys, time
from joulewise.align.apple import powermode
lock = powermode.HostLock(role='synthetic-killed-driver')
assert lock.acquire()
powermode.write_host_marker(powermode.host_marker_path(), tag=powermode.R1_MARKER_TEXT)
print('armed', flush=True)
time.sleep(30)
'''
        process = subprocess.Popen([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE, text=True)
        try:
            import select
            self.assertTrue(select.select([process.stdout], [], [], 5)[0])
            self.assertEqual(process.stdout.readline().strip(), 'armed')
            host.mode = 2
            process.kill()
            process.wait(timeout=5)
            self.assertTrue(marker.exists())
            self.assertEqual((host.mode, host.ntp), (2, 'off'))
            with mock.patch.object(h.driver, '_completion_epoch_s', return_value=0), \
                    mock.patch.object(hazard, 'reap_orphan_monitor', return_value=None):
                self.assertEqual(h.driver.dead_man(h.plan_path), 0)
            self.assertTrue(h.result()['dead_man_host_restoration']['ok'])
            self.assertFalse(marker.exists())
            self.assertEqual((host.mode, host.ntp), (0, 'on'))
        finally:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
            process.stdout.close()


class ProductionPreflightTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for patch in (mock.patch.object(powermode, 'HOST_STATE_DEFAULT', str(self.root / 'production')),
                      mock.patch.object(powermode, '_PRODUCTION_ENTRY', None),
                      mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: ''})):
            patch.start()
            self.addCleanup(patch.stop)
        powermode.mark_production_entry('w1-r2-synthetic-production')

    def test_prepare_acquires_and_releases_the_fixed_path_even_without_a_marker(self):
        with mock.patch.object(session, 'session_start_restore', return_value={'action': 'none'}), \
                mock.patch.object(session.kit, 'generate'), \
                mock.patch.object(session, 'series_ac_powermode', return_value=0), \
                mock.patch.object(session.pilot, 'prepare', return_value={}), \
                mock.patch.object(session.pilot.h, 'write'):
            state = session.prepare(self.root / 'measurement', self.root / 'session')
        record = state['host_state_preflight']
        self.assertEqual(record['host_state_dir'], str(self.root / 'production'))
        self.assertTrue(record['acquired'] and record['released'])
        lock = powermode.HostLock()
        self.assertTrue(lock.acquire())
        lock.release()

    def test_root_owned_directory_failure_or_override_refuses_before_any_prepare_work(self):
        with mock.patch.object(session.kit, 'generate') as generate, \
                mock.patch.object(session.pilot, 'prepare') as prepare:
            with mock.patch.object(powermode.HostLock, 'acquire', side_effect=PermissionError('root-owned')):
                with self.assertRaisesRegex(ValueError, 'preflight refused.*root-owned'):
                    session.prepare(self.root, self.root / 'session')
            with mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(self.root / 'seam')}):
                with self.assertRaises(powermode.HostStateOverrideRefused):
                    session.prepare(self.root, self.root / 'session')
            generate.assert_not_called()
            prepare.assert_not_called()

    def test_busy_production_lock_refuses(self):
        lock = powermode.HostLock()
        self.assertTrue(lock.acquire())
        try:
            with self.assertRaisesRegex(ValueError, 'another night'):
                powermode.host_lock_preflight(role='synthetic')
        finally:
            lock.release()


if __name__ == '__main__':
    unittest.main()
