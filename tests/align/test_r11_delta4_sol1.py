"""Delta4 Sol1: real arm rebuild over synthetic Git records, fake host probes only.

No native installer, measurement, model, network, or external custody path is used.
The committed-source fixtures are shared; admission calls use the product arm.
The battery clock-regression witness is intentionally red at 48a4d1d76; it
specifies the required refusal for the lead's product repair.
"""
from tests.align.test_v4_arm_watchdog_check import acceptance as _watchdog_acceptance
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_cadence as cadence
from joulewise.align.apple import v4_registration as registration
from joulewise.align.apple import v4_topup as topup
from scripts import align_v4_next_arm_packet as builder
from scripts import align_v4_session as session
from tests.align.test_v4_cadence import write_battery_log
from tests.align.test_v4_next_arm_packet import Base, NOW, Scenario

ROOT = Path(__file__).resolve().parents[2]
GOOD_BATTERY = dict(passed=True, probe_error=False, external_connected=True,
                    is_charging=False, current_capacity_pct=100,
                    instant_amperage_ma=0, update_age_s=1)


class ArmWitnesses(Base):
    def arm(self, scenario, packet, *, now=NOW, meter_live=True, battery=None, battery_rows=None):
        # Keep logs and host state outside the synthetic Git tree: the only
        # changes to that tree are the explicit committed-source mutations.
        temp = tempfile.TemporaryDirectory(prefix='jw-delta4-arm-')
        self.addCleanup(temp.cleanup)
        outside = Path(temp.name)
        log = write_battery_log(outside / 'battery.jsonl', now)
        if battery_rows is not None:
            log.write_text(''.join(json.dumps(row) + '\n' for row in battery_rows))
        supplied = outside / 'packet.json'
        supplied.write_text(json.dumps(packet))
        with patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(outside / 'host')}), \
             patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True}), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check',
                   return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe',
                   return_value=(dict(GOOD_BATTERY if battery is None else battery), b'synthetic ioreg')):
            return session.arm_checks(
                scenario.root, {}, next_arm_triage=supplied, now=lambda: now,
                obc_off_attested_by='synthetic-delta4', battery_log=log,
                watchdog_check=_watchdog_acceptance, runner=lambda argv: subprocess.CompletedProcess(argv, 0, 'synthetic pmset', ''),
                meter_probe=lambda root: {'live': meter_live, 'source': 'synthetic probe'})

    def test_exact_merged_entry_sources_and_strict_launch_inventory(self):
        scenario = self.scenario().finish()
        packet = scenario.build()
        self.assertEqual((len(cadence.TRIAGE_IDS), len(cadence.GATING_IDS)), (16, 15))
        self.assertEqual(set(packet['entry_sources']), set(cadence.TRIAGE_IDS))
        self.assertEqual(set(packet['arm_pending']),
                         {'series_powermode', 'external_volume', 'charging_battery', 'meter_reader_live'})
        self.assertEqual(packet['entry_sources']['battery_window'], cadence.PACKET)
        self.assertEqual(packet['entry_sources']['calibration_stop'], cadence.DERIVED)
        self.assertEqual(registration.AMENDMENT_ALLOWLIST, ())
        for path in ('scripts/align_v4_next_arm_packet.py',
                     'configs/launchd/com.joulewise.night.plist.template',
                     'configs/launchd/com.joulewise.night-probe.plist.template',
                     'configs/launchd/com.joulewise.magistrate.plist.template',
                     'configs/launchd/com.joulewise.b6loop.plist.template'):
            with self.subTest(path=path):
                self.assertIn(path, registration.ARTIFACTS)
                self.assertTrue(registration.is_strict(path))
        trace = json.loads((ROOT / 'docs/align/v4/dynamic_closure_trace.json').read_bytes())
        self.assertTrue(trace['scenarios']['night_driver_hazard_pack']['ok'])
        self.assertIn('scripts/run_night.py', trace['executed'])

    def test_r0_filled_config_and_templates_validate_without_a_native_backend(self):
        from joulewise.align.apple import r1_runtime as runtime
        config, _ = runtime.load_config(ROOT / 'configs/align/v4/r1_runtime.json')
        sensors = runtime.sensors_policy(config)
        # RL-145 (rebinding RL-122's TVh0 and RL-89's Th0C): the runtime pair is TV0h/TV1h;
        # RL-94: R0's registered picks stay TV0h/Tf08.
        self.assertEqual((config['r0_picks']['s_fast'], config['r0_picks']['s_slow']), ('TV0h', 'Tf08'))
        self.assertEqual((sensors['s_fast'], sensors['s_slow']), ('TV0h', 'TV1h'))
        self.assertEqual(sensors['fan_keys'], ['F0Ac', 'F1Ac'])
        for key in ('d_spam', 'd_bank'):
            _, spec = runtime.read_template(config['templates'][key])
            self.assertEqual(spec['chat_template_kwargs']['reasoning_effort'], 'medium')
            runtime.require_effort(spec, key)

    def test_added_removed_or_edited_packet_content_cannot_arm(self):
        scenario = self.scenario().finish()
        honest = scenario.build()
        self.assertTrue(self.arm(scenario, honest)['admitted'])
        edits = {
            'basis': lambda p: p['checks']['record_committed'].update(basis='edited basis'),
            'extra': lambda p: p.update(operator_override=True),
            'missing_battery': lambda p: p['checks'].pop('battery_window'),
            'arm_assertion': lambda p: p['checks'].update(meter_reader_live={'status': 'pass', 'basis': 'typed'}),
            'fake_counts': lambda p: p.update(calibration_windows=[{
                'window': f'C{i}', 'status': 'final', 'captured_members': 14,
                'eligible_benign': {'spam': 7, 'bank': 7}} for i in range(1, 9)], next_window_role='test'),
            'expiry': lambda p: p.update(valid_until_epoch_s=10**12),
        }
        for name, edit in edits.items():
            with self.subTest(edit=name):
                packet = copy.deepcopy(honest)
                edit(packet)
                result = self.arm(scenario, packet)
                self.assertFalse(result['admitted'], result)
                self.assertFalse(result['next_arm_triage']['supplied_packet_matches_rebuild'])
                self.assertIn('packet does not match', ' '.join(result['reasons']))

    def test_preflight_and_top_level_tip_are_ignored_but_never_authoritative(self):
        scenario = self.scenario().finish()
        packet = scenario.build()
        packet.update(pushed_tip='informational edit', packet_preflight={'ready': False, 'reasons': ['edited']})
        result = self.arm(scenario, packet)
        self.assertTrue(result['admitted'], result['reasons'])
        self.assertTrue(result['next_arm_triage']['supplied_packet_matches_rebuild'])
        self.assertNotIn('pushed_tip', result['next_arm_triage']['rebuilt_packet'])
        bad = self.scenario()
        bad.quiet['active_work'] = ['hashing']
        bad.finish()
        forged = bad.build()
        forged['packet_preflight'] = {'ready': True, 'reasons': []}
        refused = self.arm(bad, forged)
        self.assertFalse(refused['admitted'])
        self.assertIn('quiet_start_state', ' '.join(refused['reasons']))

    def test_arm_clock_dominates_entered_preparation_and_expiry(self):
        scenario = self.scenario()
        scenario.series['prepared_at_epoch_s'] = 111
        scenario.finish()
        packet = scenario.build()
        # A fresh rebuild is byte-identical while the committed quiet receipt
        # remains valid; the arm time itself is never serialized into the packet.
        self.assertEqual(builder.canonical(packet), builder.canonical(scenario.build(now=139)))
        self.assertTrue(self.arm(scenario, packet, now=139)['admitted'])
        self.assertFalse(self.arm(scenario, packet, now=141)['admitted'])
        for value in (None, True, 'forever', float('inf')):
            forged = copy.deepcopy(packet)
            forged['valid_until_epoch_s'] = value
            with self.subTest(expiry=value):
                self.assertFalse(self.arm(scenario, forged)['admitted'])
        packet.pop('valid_until_epoch_s')
        self.assertFalse(self.arm(scenario, packet)['admitted'])

    def test_live_meter_and_battery_overrule_a_ready_committed_packet(self):
        scenario = self.scenario().finish()
        packet = scenario.build()
        self.assertTrue(packet['packet_preflight']['ready'])
        meter = self.arm(scenario, packet, meter_live=False)
        self.assertFalse(meter['admitted'])
        self.assertEqual(meter['next_arm_triage']['checks']['meter_reader_live']['status'], 'fail')
        battery = self.arm(scenario, packet, battery={**GOOD_BATTERY, 'is_charging': True, 'passed': False})
        self.assertFalse(battery['admitted'])
        self.assertEqual(battery['next_arm_triage']['checks']['charging_battery']['status'], 'fail')

    def test_arm_does_not_sort_away_a_battery_source_clock_regression(self):
        scenario = self.scenario().finish()
        # One source, as written: floating, then charging at a regressed wall
        # time. There is no consecutive charging -> floating observation.
        rows = [{**GOOD_BATTERY, 'schema': topup.SCHEMA, 'wall_time_s': NOW - 50},
                {**GOOD_BATTERY, 'schema': topup.SCHEMA, 'wall_time_s': NOW - 100,
                 'is_charging': True, 'current_capacity_pct': 97}]
        self.assertFalse(topup.derive(rows, NOW)['admissible'])
        result = self.arm(scenario, scenario.build(), battery_rows=rows)
        self.assertFalse(result['admitted'],
                         'arm sorted a regressed source into a fabricated completed-charge event: '
                         + json.dumps(result['battery']['topup_evidence'], sort_keys=True))

    def test_latest_window_binding_rejects_old_packet_despite_valid_rebuild(self):
        old = self.scenario().finish()
        packet = old.build()
        self.assertTrue(self.arm(old, packet)['admitted'])
        old.write('docs/unrelated.json', {'note': 'no state change'})
        old.commit()
        self.assertTrue(self.arm(old, packet)['admitted'])
        newest = Scenario(old.root, 'C1', previous=old).finish()
        self.assertFalse(self.arm(old, packet)['admitted'])
        # Refresh the old record's packet against the now-advanced pushed ref,
        # so equality succeeds and G1 itself has to reject the old identity.
        result = self.arm(old, old.build())
        self.assertFalse(result['admitted'])
        self.assertTrue(result['next_arm_triage']['supplied_packet_matches_rebuild'])
        self.assertFalse(result['next_arm_triage']['derived']['record_bound'])
        self.assertTrue(self.arm(newest, newest.build())['admitted'])

    def test_remote_ref_advance_does_not_stale_a_packet(self):
        # Fixed (delta4 S1 L1 / S2 F3): the emitted pushed tip inside the record_committed check is the same
        # volatile pointer as the top-level one; advancing only the remote-tracking ref keeps equality.
        scenario = self.scenario().finish()
        before = scenario.build()
        scenario.write('docs/push-note.json', {'note': 'no window or code change'})
        tip = scenario.commit()
        scenario.git('update-ref', 'refs/remotes/synthetic/records', tip)
        after = scenario.build()
        self.assertNotEqual(before['checks']['record_committed']['pushed_tip'],
                            after['checks']['record_committed']['pushed_tip'])
        self.assertEqual(builder.canonical(before), builder.canonical(after))
        stale = self.arm(scenario, before)
        self.assertTrue(stale['next_arm_triage']['derived']['record_bound'])
        self.assertTrue(stale['next_arm_triage']['supplied_packet_matches_rebuild'])
        self.assertTrue(stale['admitted'], stale['reasons'])
        # every other nested field is still compared
        edited = copy.deepcopy(before)
        edited['checks']['record_committed']['basis'] += ' (edited)'
        self.assertFalse(self.arm(scenario, edited)['admitted'])

    def test_c3_attempt_ruling_is_bound_to_committed_text_and_preserves_counts(self):
        # R22-2: a zero-capture refusal beyond the retry is a structural bar that a replacement window absorbs;
        # escalation needs a seventh bar (R24: six replacements). The ruling's committed text digest, forgery and omission behaviour are
        # unchanged; the ruling resets the trailing count but cannot repair an unreachable eight.
        scenario = self.calibration_series([(f'C{n}#{k}', False, True) for n in range(1, 8) for k in (1, 2)])
        before = scenario.build()
        self.assertEqual(before['calibration_decision']['decision'], 'escalate_to_lead')
        self.assertFalse(self.arm(scenario, before)['admitted'])
        text = b'SYNTHETIC lead: seven zero-capture bars, counts frozen unchanged.\n'
        ref = scenario.write('rulings/c3.txt', text)
        scenario.series['lead_rulings'] = [{'ruling_id': 'C3-RESUME', 'after_window': 'C7#2',
            'text': ref, 'lead_signature': 'lead: synthetic 2026-11-08'}]
        scenario.write(scenario.series_path, scenario.series)
        scenario.series_commit = scenario.commit()
        ruled = scenario.build()
        self.assertEqual(ruled['lead_rulings'][0]['text_sha256'], hashlib.sha256(text).hexdigest())
        self.assertEqual(ruled['calibration_decision']['attempted'], 0)
        self.assertEqual(ruled['calibration_decision']['eligible_by_pair'],
                         before['calibration_decision']['eligible_by_pair'])
        self.assertEqual(ruled['calibration_decision']['decision'], 'insufficient_calibration')
        self.assertFalse(self.arm(scenario, ruled)['admitted'])
        forged = copy.deepcopy(ruled)
        forged['lead_rulings'][0]['text_sha256'] = 'a' * 64
        self.assertFalse(self.arm(scenario, forged)['admitted'])
        # Omitting the #1 attempt from the committed link must fail as well.
        scenario.record['previous_record'] = scenario.previous.previous.link
        scenario.finish()
        skipped = scenario.build()
        self.assertIn('out of order or omitted', skipped['calibration_error'])
        self.assertFalse(self.arm(scenario, skipped)['admitted'])

    def test_battery_ruling_is_required_after_second_failure_and_uses_committed_text(self):
        scenario = self.calibration_series([('C1', True, True, False)])
        first = self.arm(scenario, scenario.build())
        self.assertTrue(first['admitted'], first['reasons'])
        self.assertEqual(first['next_arm_triage']['checks']['battery_window']['status'], 'automatic_resume')
        second = Scenario(scenario.root, 'C2', previous=scenario, b_bar=False).finish()
        self.assertFalse(self.arm(second, second.build())['admitted'])
        text = b'SYNTHETIC battery disposition after C2.\n'
        ref = second.write('rulings/battery.txt', text)
        second.series['battery_rulings'] = [{'ruling_id': 'B-RESUME', 'after_window': 'C2',
            'text': ref, 'lead_signature': 'lead: synthetic 2026-11-08'}]
        second.write(second.series_path, second.series)
        second.series_commit = second.commit()
        packet = second.build()
        self.assertEqual(packet['battery_rulings'][0]['text_sha256'], hashlib.sha256(text).hexdigest())
        resumed = self.arm(second, packet)
        self.assertTrue(resumed['admitted'], resumed['reasons'])
        self.assertEqual(resumed['next_arm_triage']['checks']['battery_window']['status'], 'resumed_by_lead')
        self.assertFalse(self.arm(second, packet, meter_live=False)['admitted'])
        forged = copy.deepcopy(packet)
        forged['checks']['battery_window'].update(consecutive_non_pass=1)
        self.assertFalse(self.arm(second, forged)['admitted'])


if __name__ == '__main__':
    unittest.main()
