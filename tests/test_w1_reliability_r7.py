"""RL-26 arm evidence: synthetic helper bytes, timex probes and installer only."""
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

from joulewise.align.apple import powermode, v4_registration
from scripts import align_v4_session as session
from tests.test_kernel_clock import frequency_probe
from tests.test_w1_reliability_r3 import Host, LIMITS, WORD


SOURCE = 'scripts/zero_ntp_frequency.c'


class ArmEvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.measurement = self.root / 'measurement'
        source = self.measurement / SOURCE
        source.parent.mkdir(parents=True)
        source.write_bytes((session.ROOT / SOURCE).read_bytes())
        self.source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
        receipt = self.measurement / v4_registration.REGISTRATION / 'registration_receipt.json'
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({'artifacts': {SOURCE: self.source_digest}}))
        (self.measurement / session.kit.KIT / 'collection_plan.json').write_text(json.dumps(
            {'runtime_requirements': {'ac_powermode': 0}}))
        self.helper = self.root / 'installed-helper'
        self.helper.write_bytes(b'synthetic installed native binary')
        self.target = self.root / 'session'
        self.target.mkdir()
        self.plan = self.root / 'plan.json'
        self.plan.write_text(json.dumps({'t0_epoch_s': time.time() + 3600,
            'hazard_window': {'thresholds': {'clock': LIMITS}, 'T_stream_max_s': 5764}}))
        self.state = dict(measurement_root=str(self.measurement),
            source_measurement_root=str(self.measurement), plan_path=str(self.plan),
            plan_sha256=session.pilot.h.locator(self.plan)['sha256'],
            inputs={'custody_root': str(self.target / 'custody')})
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(mock.patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(self.root / 'host')}))
        stack.enter_context(mock.patch.object(session, 'ZERO_FREQUENCY_ARGV', ('sudo', '-n', str(self.helper))))

    def preflight(self, host):
        return session.frequency_word_preflight(self.state, reader=host.read, runner=host)

    def arm(self, host, *, after_checks=None, install_effect=None):
        session.pilot.h.write(self.target / 'session.json', self.state)

        def checks(*args, pre_dwell, **kwargs):
            if after_checks is not None:
                after_checks()
            record = {'admitted': True, 'reasons': [], 'ac_powermode': {'observed': 0},
                      'series_binding': [], 'quiet_dwell': {}}
            pre_dwell(record)
            return record

        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(session, 'arm_checks', side_effect=checks))
            stack.enter_context(mock.patch.object(session.kit, 'generate'))
            stack.enter_context(mock.patch.object(session.kit, 'arm_powermode_check'))
            stack.enter_context(mock.patch.object(session, 'session_start_restore', return_value={'action': 'none'}))
            stack.enter_context(mock.patch.object(session, 'w1_disk_check', return_value={}))
            self.installer = stack.enter_context(mock.patch.object(session.pilot, 'install',
                return_value={'exit_code': 0}, side_effect=install_effect))
            return session.install(self.target, runner=host, volume_runner=host, frequency_reader=lambda: host.read())

    def saved(self):
        return json.loads((self.target / 'staging/v4-arm-001.json').read_bytes())

    def test_installed_binary_and_receipt_bound_source_are_paired_in_arm(self):
        host = Host()
        self.arm(host)
        helper = self.saved()['clock_frequency_preflight']['zero_helper']
        self.assertEqual(helper['path'], str(self.helper))
        self.assertEqual(helper['sha256'], hashlib.sha256(self.helper.read_bytes()).hexdigest())
        self.assertEqual(helper['source'], {'path': SOURCE, 'sha256': self.source_digest})
        self.installer.assert_called_once()

    def test_no_op_also_records_the_installed_binary_without_running_it(self):
        host = Host(1)
        record = self.preflight(host)
        self.assertTrue(record['ok'], record)
        self.assertEqual(record['zero_helper']['sha256'], hashlib.sha256(self.helper.read_bytes()).hexdigest())
        self.assertNotIn(session.ZERO_FREQUENCY_ARGV, host.calls)

    def test_missing_needed_binary_is_a_named_refusal_before_helper_or_install(self):
        self.helper.unlink()
        host = Host()
        with self.assertRaisesRegex(ValueError, 'clock.frequency_helper_unreadable'):
            self.arm(host)
        self.installer.assert_not_called()
        self.assertNotIn(session.ZERO_FREQUENCY_ARGV, host.calls)
        record = self.saved()['clock_frequency_preflight']
        self.assertFalse(self.saved()['admitted'])
        self.assertIsNone(record['zero_helper']['sha256'])
        self.assertIn('FileNotFoundError', record['zero_helper']['error'])
        self.assertEqual(record['zero_helper']['source']['sha256'], self.source_digest)

    def test_unreadable_needed_binary_is_a_named_refusal_before_helper_or_install(self):
        original = Path.read_bytes

        def read(path):
            if path == self.helper:
                raise PermissionError('synthetic helper read denied')
            return original(path)

        host = Host()
        with mock.patch.object(Path, 'read_bytes', read), \
                self.assertRaisesRegex(ValueError, 'clock.frequency_helper_unreadable'):
            self.arm(host)
        self.installer.assert_not_called()
        self.assertNotIn(session.ZERO_FREQUENCY_ARGV, host.calls)
        self.assertIn('PermissionError', self.saved()['clock_frequency_preflight']['zero_helper']['error'])

    def test_missing_unused_binary_does_not_add_a_zero_word_requirement(self):
        self.helper.unlink()
        host = Host(1)
        self.arm(host)
        record = self.saved()['clock_frequency_preflight']
        self.assertTrue(record['ok'], record)
        self.assertIsNone(record['zero_helper']['sha256'])
        self.assertNotIn(session.ZERO_FREQUENCY_ARGV, host.calls)

    def test_source_drift_cannot_be_reported_as_the_bound_source(self):
        (self.measurement / SOURCE).write_bytes(b'changed source')
        host = Host()
        with self.assertRaisesRegex(ValueError, 'clock.frequency_helper_source_unbound'):
            self.arm(host)
        self.installer.assert_not_called()
        self.assertNotIn(session.ZERO_FREQUENCY_ARGV, host.calls)

    def test_last_pre_t0_probe_is_after_arm_checks_and_is_durable_before_install(self):
        prepare_host = Host(0)
        self.state['clock_frequency_preflight'] = self.preflight(prepare_host)
        host = Host(1)

        def installed(*args, **kwargs):
            final = self.saved()['clock_frequency_pre_t0']
            self.assertEqual(final['probe'], frequency_probe(2, call_status=5))
            self.assertLess(final['read_finished_epoch_s'], final['t0_epoch_s'])
            self.assertLessEqual(final['read_started_epoch_s'], final['read_finished_epoch_s'])
            self.assertEqual(host.events[-1], ('read', 2))
            return {'exit_code': 0}

        self.arm(host, after_checks=lambda: setattr(host, 'word', 2), install_effect=installed)
        record = self.saved()
        self.assertEqual(record['clock_frequency_preflight']['after']['raw_word'], 1)
        self.assertEqual(record['clock_frequency_pre_t0']['probe']['raw_word'], 2)

    def test_final_probe_failure_refuses_with_evidence_before_install(self):
        host = Host(0)

        def failed_read():
            host.read = mock.Mock(side_effect=OSError('synthetic final probe unavailable'))

        with self.assertRaisesRegex(ValueError, 'clock.frequency_pre_t0_unreadable'):
            self.arm(host, after_checks=failed_read)
        self.installer.assert_not_called()
        self.assertFalse(self.saved()['clock_frequency_pre_t0']['ok'])

    def test_no_post_t0_probe_is_labelled_pre_t0(self):
        host = Host(0)

        def expired():
            clock = mock.patch.object(session.time, 'time', return_value=time.time() + 7200)
            clock.start()
            self.addCleanup(clock.stop)

        with self.assertRaisesRegex(ValueError, 'clock.frequency_pre_t0_unavailable'):
            self.arm(host, after_checks=expired)
        self.installer.assert_not_called()
        self.assertIsNone(self.saved()['clock_frequency_pre_t0']['probe'])

    def test_read_crossing_t0_is_retained_but_cannot_admit_install(self):
        host = Host(0)

        def slow_read():
            original = host.read

            def read():
                probe = original()
                clock = mock.patch.object(session.time, 'time', return_value=time.time() + 7200)
                clock.start()
                self.addCleanup(clock.stop)
                return probe

            host.read = read

        with self.assertRaisesRegex(ValueError, 'clock.frequency_pre_t0_unavailable'):
            self.arm(host, after_checks=slow_read)
        self.installer.assert_not_called()
        final = self.saved()['clock_frequency_pre_t0']
        self.assertFalse(final['ok'])
        self.assertEqual(final['probe']['raw_word'], 0)
        self.assertLess(final['read_started_epoch_s'], final['t0_epoch_s'])
        self.assertGreaterEqual(final['read_finished_epoch_s'], final['t0_epoch_s'])


if __name__ == '__main__':
    unittest.main()
