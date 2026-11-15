"""Delta4 Sol2 review witnesses: synthetic Git records and arithmetic only.

The retry-scope, validation-cache and pushed-tip witnesses are intentionally red on
48a4d1d76. Product fixes and authority decisions belong to the lead.
No real capture, hardware probe, model, network or external user path is used.
"""
from tests.align.test_v4_arm_watchdog_check import acceptance as _watchdog_acceptance
import copy
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import thermal_desk, v4_cadence as cadence
from joulewise.align.apple import v4_registration as registration, v4_u3
from scripts import align_v4_session as session
from tests.align import test_v4_next_arm_packet as packet_fixtures
from tests.align.test_thermal_desk import member
from tests.align.test_v4_cadence import write_battery_log
from tests.align.v4_registration_fixtures import signed_bar


class PacketBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='jw-delta4-sol2-')
        self.addCleanup(self.temp.cleanup)
        self.scratch = Path(self.temp.name).resolve()
        self.host = patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(self.scratch / 'host')})
        self.host.start()
        self.addCleanup(self.host.stop)

    def scenario(self, **kwargs):
        root = self.scratch / str(len(list(self.scratch.iterdir())))
        root.mkdir()
        return packet_fixtures.Scenario(root, **kwargs).finish()

    def arm(self, scenario, packet, *, now=packet_fixtures.NOW, meter_live=True):
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        log = write_battery_log(self.scratch / 'battery.jsonl', now)
        with patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True}), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check', return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', return_value=(good, b'synthetic ioreg')):
            # Real rebuild, digest, record/ledger binding and top-up derivation;
            # only hardware observations and the clock are test seams.
            return session.arm_checks(scenario.root, scenario.next_plan,
                next_arm_triage=packet, now=lambda: now, battery_log=log,
                obc_off_attested_by='synthetic-review',
                watchdog_check=_watchdog_acceptance, runner=lambda argv: subprocess.CompletedProcess(argv, 0, '', ''),
                meter_probe=lambda root: {'live': meter_live})

    def test_actual_arm_admits_honest_packet_and_only_ignores_the_two_named_fields(self):
        s = self.scenario()
        packet = s.build()
        self.assertTrue(self.arm(s, packet)['admitted'])
        ignored = copy.deepcopy(packet)
        ignored.update(pushed_tip='ignored', packet_preflight={'ready': False, 'reasons': ['ignored']})
        record = self.arm(s, ignored)
        self.assertTrue(record['admitted'], record['reasons'])
        self.assertTrue(record['next_arm_triage']['supplied_packet_matches_rebuild'])
        for key, value in (('unexpected', True), ('prepared_at_epoch_s', 1e30),
                           ('calibration_windows', [{'window': 'C8', 'captured_members': 14}]),
                           ('last_desk_passed_artifact_set_sha256', 'f' * 64)):
            with self.subTest(key=key):
                record = self.arm(s, {**packet, key: value})
                self.assertFalse(record['admitted'])
                self.assertFalse(record['next_arm_triage']['supplied_packet_matches_rebuild'])

    def test_status_basis_source_digest_and_expiry_edits_refuse_at_actual_arm(self):
        s = self.scenario()
        packet = s.build()
        variants = []
        for field, value in (('status', 'not_applicable'), ('basis', 'invented basis'), ('sources', [])):
            changed = copy.deepcopy(packet)
            changed['checks']['record_committed'][field] = value
            variants.append(changed)
        no_expiry = copy.deepcopy(packet)
        no_expiry.pop('valid_until_epoch_s')
        variants.extend((no_expiry, {**packet, 'record_sha256': '0' * 64},
                         {**packet, 'series_sha256': '0' * 64}))
        for changed in variants:
            with self.subTest(changed=changed != packet):
                record = self.arm(s, changed)
                self.assertFalse(record['admitted'])
                self.assertFalse(record['next_arm_triage']['supplied_packet_matches_rebuild'])

    def test_current_clock_and_meter_cannot_be_overridden_by_packet_preflight(self):
        s = self.scenario()
        packet = s.build()
        self.assertFalse(self.arm(s, packet, meter_live=False)['admitted'])
        self.assertFalse(self.arm(s, packet, now=141.)['admitted'])
        # A forged current-meter check cannot replace the ARM source.
        packet['checks']['meter_reader_live'] = {'status': 'pass', 'basis': 'invented'}
        self.assertFalse(self.arm(s, packet, meter_live=False)['admitted'])

    def test_latest_ledger_binding_survives_unrelated_commits_and_refuses_old_window(self):
        s = self.scenario()
        packet = s.build()
        self.assertTrue(self.arm(s, packet)['admitted'])
        s.write('docs/unrelated.txt', b'unrelated\n')
        s.commit()
        self.assertTrue(self.arm(s, packet)['admitted'])
        packet_fixtures.Scenario(s.root, 'C1', previous=s).finish()
        record = self.arm(s, packet)
        self.assertFalse(record['admitted'])
        self.assertIn('triage record_committed failed', ' '.join(record['reasons']))

    def test_pushed_tip_only_advance_does_not_stale_the_committed_sources(self):
        s = self.scenario()
        packet = s.build()
        s.write('docs/pushed-note.txt', b'unrelated pushed note\n')
        tip = s.commit()
        s.git('update-ref', packet['pushed_ref'], tip)
        self.assertTrue(session._record_bound(s.root, packet))
        record = self.arm(s, packet)
        self.assertTrue(record['admitted'], record['reasons'])

    def test_missing_or_broken_history_cannot_be_hidden_by_ignored_preflight(self):
        first = self.scenario()
        next_s = packet_fixtures.Scenario(first.root, 'C1', previous=first)
        next_s.record['previous_record']['sha256'] = '0' * 64
        next_s.finish()
        packet = next_s.build()
        self.assertIn('series history link digest mismatch', packet['calibration_error'])
        packet['packet_preflight'] = {'ready': True, 'reasons': []}
        self.assertFalse(self.arm(next_s, packet)['admitted'])

    def test_second_battery_failure_needs_a_ruling_bound_to_committed_text(self):
        first = self.scenario(b_bar=False)
        record = self.arm(first, first.build())
        self.assertTrue(record['admitted'], record['reasons'])
        self.assertEqual(record['next_arm_triage']['checks']['battery_window']['status'], 'automatic_resume')
        second = packet_fixtures.Scenario(first.root, 'C1', previous=first, b_bar=False).finish()
        self.assertFalse(self.arm(second, second.build())['admitted'])
        text = second.write('rulings/battery.txt', b'Synthetic prospective disposition after C1.\n')
        second.series['battery_rulings'] = [{'ruling_id': 'synthetic-battery', 'after_window': 'C1',
            'text': text, 'lead_signature': 'lead: synthetic-review 2026-11-08'}]
        second.write(second.series_path, second.series)
        second.series_commit = second.commit()
        packet = second.build()
        self.assertEqual(packet['battery_rulings'][0]['text_sha256'], text['sha256'])
        record = self.arm(second, packet)
        self.assertTrue(record['admitted'], record['reasons'])
        packet['battery_rulings'][0]['text_sha256'] = '0' * 64
        self.assertFalse(self.arm(second, packet)['admitted'])

    def test_empty_allowlist_builder_and_all_launch_templates_are_strict(self):
        self.assertEqual(registration.AMENDMENT_ALLOWLIST, ())
        for path in ('scripts/align_v4_next_arm_packet.py',
                     'configs/launchd/com.joulewise.night.plist.template',
                     'configs/launchd/com.joulewise.night-probe.plist.template',
                     'configs/launchd/com.joulewise.magistrate.plist.template',
                     'configs/launchd/com.joulewise.b6loop.plist.template'):
            with self.subTest(path=path):
                self.assertIn(path, registration.ARTIFACTS)
                self.assertTrue(registration.is_strict(path))
        self.assertEqual((len(cadence.TRIAGE_IDS), len(cadence.GATING_IDS)), (16, 15))


class IntegrationWitnesses(unittest.TestCase):
    def test_zero_capture_retry_keeps_the_registered_u3_scope_of_its_counted_slot(self):
        bar = signed_bar()
        a, b = member('a', energy=30000), member('b', energy=30000)
        for row in (a, b):
            row.update(role='D', window='C1', identical_work_group='replay',
                       u3_configuration_sha256='b' * 64)
        ordinary = thermal_desk.window_report([a, b], v4=True, u3_bar=bar)
        self.assertEqual(ordinary['model_windows']['synthetic/C1']['U3']['status'], 'pass')
        for row in (a, b):
            row['window'] = 'C1#2'
        retry = thermal_desk.window_report([a, b], v4=True, u3_bar=bar)
        self.assertEqual(retry['model_windows']['synthetic/C1#2']['U3']['status'], 'pass',
                         'a zero-capture retry still occupies counted slot C1, within its one D comparison')

    def test_u3_admission_recomputes_validation_instead_of_caching_a_decision(self):
        bar = signed_bar()
        # Give this witness a unique wire key so another test's cache cannot
        # conceal even its first call. The current validator permits metadata.
        bar['review_witness'] = 'delta4-sol2-no-decision-cache'
        with patch.object(v4_u3, 'derive', wraps=v4_u3.derive) as derive:
            registration.validate_u3(bar)
            registration.validate_u3(bar)
        self.assertEqual(derive.call_count, 2, 'standing SPEED-TOOLBOX rule: never cache decisions')


if __name__ == '__main__':
    unittest.main()
