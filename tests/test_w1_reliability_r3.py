"""Synthetic frequency-word preflight; no sudo, clock changes or study inputs."""
from tests.align.test_v4_arm_watchdog_check import acceptance as _watchdog_acceptance
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import network_time_off
from joulewise.align.apple import powermode, v4_registration
from scripts import align_v4_session as session
from tests.test_kernel_clock import frequency_probe


LIMITS = dict(t_stream_max_s=5764, h_ms=0, frequency_margin_ppm=.25, limit_ms=5)
WORD = -648908
QUERY = ('/usr/bin/sudo', '-n', '/usr/sbin/systemsetup', '-getusingnetworktime')


class Host:
    def __init__(self, word=WORD, *, available=True, zeroes=True, off=True, job_absent=True):
        self.word, self.available, self.zeroes = word, available, zeroes
        self.off, self.job_absent = off, job_absent
        self.calls, self.events = [], []

    def read(self):
        self.events.append(('read', self.word))
        return frequency_probe(self.word, call_status=5)

    def __call__(self, argv):
        argv = tuple(argv)
        self.calls.append(argv)
        self.events.append(('command', argv))
        code, stdout, stderr = 0, '', ''
        if argv[:2] == ('launchctl', 'print'):
            code = 113 if self.job_absent else 0
            stderr = f'Could not find service "com.joulewise.night" in domain for user gui: {os.getuid()}'
        elif argv == network_time_off.OFF_ARGV:
            stdout = 'setUsingNetworkTime: Off\n' if self.off else 'You need administrator access\n'
        elif argv == QUERY:
            stdout = 'Network Time: Off\n' if self.off else 'Network Time: On\n'
        elif argv == session.ZERO_FREQUENCY_ARGV:
            code = 0 if self.available else 1
            if self.available and self.zeroes:
                self.word = 0
            if code:
                stderr = 'sudo: a password is required'
        else:
            raise AssertionError(argv)
        return SimpleNamespace(returncode=code, stdout=stdout, stderr=stderr)


class FrequencyPreflightTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / 'night_plan.json'
        self.path.write_text(json.dumps({'hazard_window': {'thresholds': {'clock': LIMITS}, 'T_stream_max_s': LIMITS['t_stream_max_s']}, 't0_epoch_s': time.time() + 3600}))
        self.state = {'plan_path': str(self.path), 'plan_sha256': session.pilot.h.locator(self.path)['sha256']}
        # RL-26: synthetic installed bytes and the receipt-bound source pair.
        source = self.root / 'scripts/zero_ntp_frequency.c'
        source.parent.mkdir()
        source.write_bytes((session.ROOT / 'scripts/zero_ntp_frequency.c').read_bytes())
        receipt = self.root / v4_registration.REGISTRATION / 'registration_receipt.json'
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({'artifacts': {
            'scripts/zero_ntp_frequency.c': hashlib.sha256(source.read_bytes()).hexdigest()}}))
        self.state['source_measurement_root'] = str(self.root)
        helper = self.root / 'synthetic-helper'
        helper.write_bytes(b'synthetic installed helper')
        binary = mock.patch.object(session, 'ZERO_FREQUENCY_ARGV', ('sudo', '-n', str(helper)))
        binary.start()
        self.addCleanup(binary.stop)
        env = mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(self.root / 'host')})
        env.start()
        self.addCleanup(env.stop)

    def check(self, host):
        return session.frequency_word_preflight(self.state, reader=host.read, runner=host)

    def test_nonzero_word_zeroes_after_off_and_rereads_the_same_hazard_reader(self):
        host = Host()
        # Omit the reader seam: prove the production path uses clock.read_frequency.
        with mock.patch('joulewise.hazards.clock.read_frequency', side_effect=host.read) as reader:
            record = session.frequency_word_preflight(self.state, runner=host)
        self.assertEqual(reader.call_count, 2)
        self.assertTrue(record['ok'])
        self.assertEqual(record['action'], 'zeroed')
        self.assertEqual((record['before']['raw_word'], record['after']['raw_word']), (WORD, 0))
        self.assertAlmostEqual(record['before_gate']['bound_ms'], 58.513535888671875)
        self.assertAlmostEqual(record['after_gate']['bound_ms'], 1.441)
        self.assertEqual(host.calls[1:], [network_time_off.OFF_ARGV, QUERY, session.ZERO_FREQUENCY_ARGV])
        self.assertEqual(host.events[-1], ('read', 0))

    def test_unavailable_helper_refuses_and_retains_before_after_and_denial(self):
        host = Host(available=False)
        record = self.check(host)
        self.assertFalse(record['ok'])
        self.assertEqual(record['cause'], 'clock.frequency_word_nonzero')
        self.assertEqual(record['after']['raw_word'], WORD)
        self.assertIn('password is required', record['commands'][-1]['stderr'])
        self.assertIn('unavailable', record['reason'])

    def test_zero_word_checks_network_time_without_zeroing(self):
        host = Host(0)
        record = self.check(host)
        self.assertTrue(record['ok'])
        self.assertEqual(record['action'], 'no_op')
        self.assertEqual(host.calls[-1], QUERY)
        self.assertNotIn(session.ZERO_FREQUENCY_ARGV, host.calls)
        self.assertEqual(record['before']['raw_word'], record['after']['raw_word'])

    def test_a_passing_nonzero_word_does_not_introduce_a_new_zero_threshold(self):
        host = Host(1)
        self.assertTrue(self.check(host)['ok'])
        self.assertEqual(host.calls[-1], QUERY)
        self.assertNotIn(session.ZERO_FREQUENCY_ARGV, host.calls)

    def test_helper_success_requires_actual_zero_readback(self):
        record = self.check(Host(zeroes=False))
        self.assertFalse(record['ok'])
        self.assertIn('read-back', record['reason'])
        self.assertEqual(record['after']['raw_word'], WORD)

    def test_off_denial_and_a_loaded_night_never_invoke_the_zero_helper(self):
        for host in (Host(off=False), Host(job_absent=False)):
            with self.subTest(host=host):
                record = self.check(host)
                self.assertFalse(record['ok'])
                self.assertNotIn(session.ZERO_FREQUENCY_ARGV, host.calls)
                self.assertEqual(record['after']['raw_word'], WORD)

    def test_probe_failure_and_plan_tampering_refuse_without_commands(self):
        host = Host()
        with mock.patch.object(host, 'read', side_effect=OSError('probe denied')):
            record = self.check(host)
        self.assertFalse(record['ok'])
        self.assertIn('probe denied', record['reason'])
        self.path.write_text('{}')
        record = self.check(host)
        self.assertFalse(record['ok'])
        self.assertIn('plan bytes changed', record['reason'])
        self.assertEqual(host.calls, [])

    def test_a_fresh_install_cannot_reuse_a_passing_prepare_record(self):
        host = Host(0)
        self.state['clock_frequency_preflight'] = self.check(host)
        host.word, host.available = WORD, False
        record = self.check(host)
        self.assertFalse(record['ok'])
        self.assertEqual(record['before']['raw_word'], WORD)

    def test_a_past_t0_refuses_before_any_clock_read_or_change(self):
        plan = json.loads(self.path.read_text())
        plan['t0_epoch_s'] = time.time() - 1
        self.path.write_text(json.dumps(plan))
        self.state['plan_sha256'] = session.pilot.h.locator(self.path)['sha256']
        host = Host()
        record = self.check(host)
        self.assertFalse(record['ok'])
        self.assertIn('t0 has passed', record['reason'])
        self.assertEqual(host.events, [])

    def test_off_query_failure_and_helper_timeout_refuse_without_a_success_claim(self):
        for fails_at in (QUERY, session.ZERO_FREQUENCY_ARGV):
            host = Host()
            def run(argv):
                if tuple(argv) == fails_at:
                    if fails_at == QUERY:
                        return SimpleNamespace(returncode=0, stdout='Network Time: On\n', stderr='')
                    raise subprocess.TimeoutExpired(argv, 10)
                return host(argv)
            record = session.frequency_word_preflight(self.state, reader=host.read, runner=run)
            self.assertFalse(record['ok'])
            self.assertEqual(record['cause'], 'clock.frequency_word_nonzero')
            self.assertEqual(record['after']['raw_word'], WORD)
            if fails_at == QUERY:
                self.assertNotIn(session.ZERO_FREQUENCY_ARGV, host.calls)
            else:
                self.assertIn('TimeoutExpired', record['commands'][-1]['error'])

    def test_terminal_restore_still_sets_on_and_records_next_arm_zeroing(self):
        from tests.test_run_night import _load_driver
        driver = _load_driver(module_name='run_night_frequency_r3')
        calls = []
        def run(argv):
            calls.append(tuple(argv))
            return SimpleNamespace(exit_code=0, stdout='Network Time: On\n', stderr='')
        record = driver._restore_network_time(SimpleNamespace(run=run))
        self.assertTrue(record['ok'])
        self.assertEqual(calls, [driver.NETWORK_TIME_ON_ARGV, driver.NETWORK_TIME_QUERY_ARGV])
        self.assertTrue(record['next_arm_owns_zeroing'])
        self.assertEqual(record['next_arm_preflight'], 'clock.frequency_word_nonzero')

    def test_prepare_persists_success_or_named_refusal_before_any_install(self):
        self.state.update(preparation_status='STAGED')
        for available in (True, False):
            host = Host(available=available)
            target = self.root / str(available)
            with self.subTest(available=available), \
                    mock.patch.object(session.kit, 'generate'), \
                    mock.patch.object(session, 'session_start_restore', return_value={'action': 'none'}), \
                    mock.patch.object(session, 'series_ac_powermode', return_value=0), \
                    mock.patch.object(session.pilot, 'prepare', return_value=dict(self.state)), \
                    mock.patch.object(session, 'weight_digest_preflight', return_value={'ok': True, 'synthetic': True}), \
                    mock.patch.object(session.pilot, 'install') as install:
                if available:
                    session.prepare(self.root, target, frequency_reader=host.read, frequency_runner=host)
                else:
                    with self.assertRaisesRegex(ValueError, 'clock.frequency_word_nonzero'):
                        session.prepare(self.root, target, frequency_reader=host.read, frequency_runner=host)
                record = session.pilot.h.read(target / 'session.json')['clock_frequency_preflight']
                self.assertEqual(record['ok'], available)
                self.assertEqual(record['before']['raw_word'], WORD)
                install.assert_not_called()

    def test_arm_record_before_after_and_refusal_precede_shared_install(self):
        measurement = self.root / 'measurement'
        (measurement / session.kit.KIT).mkdir(parents=True)
        (measurement / session.kit.KIT / 'collection_plan.json').write_text(json.dumps(
            {'runtime_requirements': {'ac_powermode': 0}}))
        for word, available, succeeds in ((WORD, True, True), (WORD, False, False), (0, False, True)):
            host = Host(word, available=available)
            target = self.root / f'arm-{word}-{available}'
            target.mkdir()
            state = dict(self.state)
            state.update(measurement_root=str(measurement), inputs={'custody_root': str(target / 'custody')})
            state['clock_frequency_preflight'] = {'ok': True, 'action': 'stale_prepare'}
            session.pilot.h.write(target / 'session.json', state)
            record = {'admitted': True, 'reasons': [], 'ac_powermode': {'observed': 0},
                      'series_binding': [], 'quiet_dwell': {}}

            def checks(*args, pre_dwell, **kwargs):
                pre_dwell(record)
                return record

            with mock.patch.object(session, 'arm_checks', side_effect=checks), \
                    mock.patch.object(session.kit, 'generate'), \
                    mock.patch.object(session.kit, 'arm_powermode_check'), \
                    mock.patch.object(session, 'session_start_restore', return_value={'action': 'none'}), \
                    mock.patch.object(session, 'w1_disk_check', return_value={}), \
                    mock.patch.object(session.pilot, 'install', return_value={'exit_code': 0}) as install:
                def arm():
                    return session.install(target, watchdog_check=_watchdog_acceptance, runner=host, volume_runner=host, frequency_reader=host.read)
                if succeeds:
                    arm()
                else:
                    with self.assertRaisesRegex(ValueError, 'clock.frequency_word_nonzero'):
                        arm()
                self.assertEqual(install.called, succeeds)
            saved = json.loads((target / 'staging/v4-arm-001.json').read_text())
            self.assertEqual(saved['admitted'], succeeds)
            frequency = saved['clock_frequency_preflight']
            self.assertEqual(frequency['before']['raw_word'], word)
            self.assertEqual(frequency['after']['raw_word'], 0 if succeeds else word)


@unittest.skipUnless(sys.platform == 'darwin' and shutil.which('cc'), 'Darwin SDK and C compiler required')
class NativeHelperContractTests(unittest.TestCase):
    """Compile the real C helper with fake syscalls; NEVER adjust the clock."""
    def test_fixed_zero_operation_root_arguments_errors_and_readback(self):
        source = Path(__file__).resolve().parents[1] / 'scripts/zero_ntp_frequency.c'
        harness = r'''
#include <assert.h>
#include <sys/timex.h>
#include <unistd.h>
static int calls, root = 1, failure = 0, bad_readback = 0;
static uid_t fake_geteuid(void) { return root ? 0 : 501; }
static int fake_ntp_adjtime(struct timex *value) {
    ++calls;
    if (calls == 1) {
        assert(value->modes == (MOD_OFFSET | MOD_FREQUENCY));
        assert(value->offset == 0 && value->freq == 0);
    } else {
        assert(calls == 2 && value->modes == 0);
        value->freq = bad_readback ? -648908 : 0;
    }
    return failure ? -1 : 5;
}
#define geteuid fake_geteuid
#define ntp_adjtime fake_ntp_adjtime
#define main helper_main
#include SOURCE
#undef main
int main(void) {
    assert(helper_main(2, 0) == 2 && calls == 0);
    root = 0;
    assert(helper_main(1, 0) == 2 && calls == 0);
    root = 1;
    assert(helper_main(1, 0) == 0 && calls == 2);
    calls = 0; failure = 1;
    assert(helper_main(1, 0) == 1 && calls == 1);
    calls = 0; failure = 0; bad_readback = 1;
    assert(helper_main(1, 0) == 1 && calls == 2);
    return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'test.c').write_text(harness)
            build = subprocess.run(['cc', '-Wall', '-Wextra', '-Werror', '-DSOURCE=' + json.dumps(str(source)),
                                    str(root / 'test.c'), '-o', str(root / 'test')], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(root / 'test')], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == '__main__':
    unittest.main()
