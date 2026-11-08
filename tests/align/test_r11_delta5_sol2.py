"""Delta5 Sol2: synthetic committed records, frozen rosters and boundary mutations.

The contract assertions documenting findings are intentionally red on 03253edca.
No real measurements, native probes, weights, network or external user paths.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import thermal_desk, v4_cadence as cadence
from scripts import align_v4_kit as kit, align_v4_next_arm_packet as builder
from scripts import align_v4_series as series, align_v4_session as session
from tests.align import test_v4_next_arm_packet as fixtures
from tests.align.test_thermal_desk import member
from tests.align.test_v4_cadence import write_battery_log

ROOT = Path(__file__).resolve().parents[2]


class CommittedSeriesTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='jw-delta5-sol2-')
        self.addCleanup(temp.cleanup)
        self.scratch = Path(temp.name).resolve()
        self.repo = self.scratch / 'repo'
        self.repo.mkdir()
        host = patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(self.scratch / 'host')})
        host.start()
        self.addCleanup(host.stop)
        self.arms = 0

    def scenario(self, window='W1', *, previous=None, captured=True):
        s = fixtures.Scenario(self.repo, window, previous=previous, captured=captured)
        s.write(series.MANIFEST.as_posix(), series.raw_json(series.candidate()))
        if window.startswith('C'):
            s.sources['pilot']['extra_checks']['series_desk_row'] = {
                'window_id': window.split('#')[0], 'captured_members': 2 if captured else 0,
                'status': 'provisional', 'desk_eligible_benign': dict.fromkeys(cadence.CAL_PAIRS, int(captured)),
                'flags': []}
        return s

    def arm(self, scenario, packet, window):
        """Real rebuild, record binding, cadence and _arm_and_install series binding.

        Only host observations, the final disk check and installer are seams.
        No packet_builder, commit_check or record_check seam is supplied.
        """
        self.arms += 1
        target = self.scratch / f'arm-{self.arms}'
        target.mkdir()
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        log = write_battery_log(self.scratch / 'battery.jsonl', fixtures.NOW)
        state = {'v4_series': {'window_id': window}, 'source_measurement_root': str(self.repo)}
        with patch('joulewise.align.apple.powermode.admit_ac_powermode',
                   return_value={'admitted': True, 'observed': 0}), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check',
                   return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', return_value=(good, b'synthetic ioreg')), \
             patch.object(kit, 'arm_powermode_check'), \
             patch.object(session, 'w1_disk_check', return_value={'status': 'pass'}), \
             patch.object(session.pilot, 'install', return_value={'synthetic': True}) as install:
            try:
                session._arm_and_install(target, state, self.repo, scenario.next_plan, None,
                    runner=lambda argv: subprocess.CompletedProcess(argv, 0, '', ''),
                    volume_runner=None, now=lambda: fixtures.NOW, w1_disk_config=None, disk_gate=None,
                    battery_log=log, obc_off_attested_by='synthetic', next_arm_triage=packet,
                    meter_probe=lambda root: {'live': True})
                error = None
            except ValueError as exc:
                error = str(exc)
            record = json.loads((target / 'staging/v4-arm-001.json').read_bytes())
            return record, error, install.call_count

    def test_honest_r1_to_w1_and_w1_to_c1_reach_installer(self):
        for previous, window in (('R1', 'W1'), ('W1', 'C1')):
            with self.subTest(window=window):
                # Independent repositories: no attempt is silently overwritten.
                self.repo = self.scratch / ('repo-' + previous)
                self.repo.mkdir()
                s = self.scenario(previous)
                if previous == 'R1':
                    s.next_plan.update(window='W1', role='development')
                s.finish()
                record, error, calls = self.arm(s, s.build(), window)
                self.assertIsNone(error, record['reasons'])
                self.assertTrue(record['admitted'])
                self.assertEqual(calls, 1)
                self.assertTrue(record['quiet_dwell']['meter_probe_before_dwell'])

    def test_supplied_history_window_and_manifest_forgery_cannot_arm(self):
        s = self.scenario().finish()
        packet = s.build()
        for key, value in (
            ('next_window_id', 'C2'),
            ('series_manifest_sha256', '0' * 64),
            ('series_history', [{'window_id': 'C1', 'attempt_id': 'C1', 'status': 'final',
                                 'captured_members': 22, 'eligible_benign': {'spam': 7, 'bank': 7}}]),
        ):
            with self.subTest(key=key):
                changed = deepcopy(packet)
                changed[key] = value
                record, error, calls = self.arm(s, changed, 'C1')
                self.assertIsNotNone(error)
                self.assertFalse(record['next_arm_triage']['supplied_packet_matches_rebuild'])
                self.assertEqual(calls, 0)

    def test_committed_wrong_next_plan_still_cannot_skip_c1(self):
        s = self.scenario()
        s.next_plan['window'] = 'C2'
        s.finish()
        packet = s.build()
        self.assertEqual(packet['next_window_id'], 'C2')
        record, error, calls = self.arm(s, packet, 'C2')
        self.assertIn('next frozen window (C1)', error)
        self.assertFalse(record['admitted'])
        self.assertEqual(calls, 0)

    def test_canonical_c1_hash_one_zero_capture_retry_can_arm_c1(self):
        w1 = self.scenario().finish()
        zero = self.scenario('C1#1', previous=w1, captured=False)
        zero.next_plan['window'] = 'C1#2'
        zero.finish()
        packet = zero.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual(packet['series_history'][0]['attempt_id'], 'C1#1')
        record, error, calls = self.arm(zero, packet, 'C1')
        self.assertIsNone(error, record['series_binding'])
        self.assertEqual(calls, 1)

    def test_captured_c1_hash_two_retry_can_advance_to_c2(self):
        w1 = self.scenario().finish()
        zero = self.scenario('C1', previous=w1, captured=False).finish()
        retry = self.scenario('C1#2', previous=zero)
        retry.next_plan['window'] = 'C2'
        retry.finish()
        packet = retry.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        record, error, calls = self.arm(retry, packet, 'C2')
        self.assertIsNone(error, record['series_binding'])
        self.assertEqual(calls, 1)

    def supplemental_scenario(self, *, only_supplemental=False):
        w1 = self.scenario().finish()
        c1 = self.scenario('C1', previous=w1)
        for row in c1.members:
            row.update(pool_role='calibration', counts_toward='calibration')
        # Two ordinary calibrators plus the two R20 diagnostics. All four captures
        # must authenticate, but only two contribute to captured_members or m.
        for ordinal in (23, 24):
            row = dict(run_id=f'align-v4-c1-e{ordinal}', model_id='tiny', role='D', condition='benign',
                       task_pair='spam', pool_role='sentinel', counts_toward='none', supplemental=True)
            c1.members.append(row)
            thermal = deepcopy(c1.thermal['members'][0])
            thermal.update(id=row['run_id'], supplemental=True, pool_role='sentinel')
            c1.thermal['members'].append(thermal)
        if only_supplemental:
            ordinary = {m['run_id'] for m in c1.members if not m.get('supplemental')}
            c1.absent_captures = ordinary
            for row in c1.thermal['members']:
                if row['id'] in ordinary:
                    row.update(excluded=True, calibration_exclusions=['member.runtime_failure'])
            c1.sources['exclusions']['members_excluded'] = [
                {'run_id': rid, 'codes': ['member.runtime_failure']} for rid in sorted(ordinary)]
        c1.next_plan['window'] = 'C2'
        return c1.finish()

    def test_builder_excludes_supplemental_captures_from_counted_members(self):
        c1 = self.supplemental_scenario()
        packet = c1.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        record, error, calls = self.arm(c1, packet, 'C2')
        self.assertIsNone(error, record['reasons'])
        self.assertEqual(calls, 1)
        row = packet['series_history'][0]
        self.assertEqual((row['captured_members'], row['eligible_benign']),
                         (2, {'spam': 1, 'bank': 1}))

    def test_only_supplemental_captures_cannot_advance_the_slot(self):
        c1 = self.supplemental_scenario(only_supplemental=True)
        packet = c1.build()
        record, error, calls = self.arm(c1, packet, 'C2')
        self.assertFalse(record['admitted'], 'diagnostics alone consumed C1 and armed C2')
        self.assertIsNotNone(error)
        self.assertEqual(calls, 0)

    def test_frozen_roster_task_pair_names_are_accepted_by_final_eligibility(self):
        s = self.scenario()
        # Actual frozen W1 uses long SHADE task-pair ids, not cadence's aliases.
        frozen = json.loads((ROOT / kit.KIT / 'collection_plan.json').read_bytes())['members']
        self.assertEqual({m['task_pair'] for m in frozen if m['role'] == 'D'}, set(series.PAIRS))
        for row, pair in zip(s.members, series.PAIRS):
            row['task_pair'] = pair
        s.finish()
        record = builder.WindowRecord(builder.GitEvidence(self.repo), s.record_commit, s.record_path)
        self.assertEqual(record.eligibility()['captured_members'], 2)

    def test_final_counts_cannot_raise_committed_provisional_desk_counts(self):
        w1 = self.scenario().finish()
        c1 = self.scenario('C1', previous=w1)
        for row in c1.members:
            row.update(pool_role='calibration', counts_toward='calibration')
        c1.sources['pilot']['extra_checks']['series_desk_row'] = {
            'window_id': 'C1', 'captured_members': 2, 'status': 'provisional',
            'desk_eligible_benign': {'spam': 0, 'bank': 0}, 'flags': []}
        c1.next_plan['window'] = 'C2'
        c1.finish()
        packet = c1.build()
        record, error, calls = self.arm(c1, packet, 'C2')
        self.assertFalse(record['admitted'], 'final counts exceeded the committed desk upper bound')
        self.assertIsNotNone(error)
        self.assertEqual(calls, 0)


class FrozenSeriesTests(unittest.TestCase):
    def test_seed_checked_manifest_bytes_still_match(self):
        checked = subprocess.run(['git', 'show',
            '79777d261:docs/align/v4/seed-check/series_manifest.json'],
            cwd=ROOT, check=True, capture_output=True).stdout
        raw = (ROOT / series.MANIFEST).read_bytes()
        self.assertEqual(raw, checked)
        self.assertEqual(series.sha(raw), 'eba6fb0732ec26996a0c63bb679a899b71dc2009474502e59048dd67d764f0c7')

    def test_series_binding_refuses_a_23rd_counted_member(self):
        history = [{'window_id': 'C1', 'attempt_id': 'C1', 'status': 'final',
                    'captured_members': 23, 'eligible_benign': {'spam': 7, 'bank': 7}}]
        with self.assertRaisesRegex(ValueError, 'impossible captured/eligible counts'):
            series.calibration_rows(series.candidate(), history)

    def test_count_only_ceiling_refuses_a_23rd_counted_member(self):
        # R20 excludes ordinals 23/24 even from captured_members. The lower-level
        # count-only predicate still permits 24; bind_packet's 22 ceiling is intact.
        row = {'window': 'C1', 'status': 'final', 'captured_members': 23,
               'eligible_benign': {'spam': 7, 'bank': 7}}
        with self.assertRaises(ValueError):
            cadence.calibration_stop([row])

    def test_supplemental_diagnostics_do_not_change_u3_or_u4(self):
        rows = []
        for ordinal in (5, 22, 23, 24):
            r = member(str(ordinal))
            r.update(window='C1', role='D', u3_configuration_sha256='a' * 64)
            planned = {'ordinal': ordinal, 'run_id': str(ordinal), 'role': 'D'}
            if ordinal >= 22:
                planned['replay_of'] = '5'
            if ordinal >= 23:
                planned.update(supplemental=True, escalation_sentinel=ordinal - 22)
            session.assign_work_group(r, planned)
            rows.append(r)
        bar = {'d_abs_relative_bar': .2, '30b_abs_relative_bar': .1,
               'policy': {'checks_by_window': {'C1': {'D': 1}}}}
        cross = {'synthetic': {'sentinels': {'status': 'pass', 'W': 4, 'df': 3}}}
        # Isolate grouping from the separately tested signed-bar validator.
        with patch('joulewise.align.apple.v4_registration.u3_margin', return_value=200):
            ordinary = thermal_desk.window_report(rows[:2], v4=True, u3_bar=bar, cross_windows=cross)
            escalated = thermal_desk.window_report(rows, v4=True, u3_bar=bar, cross_windows=cross)
        self.assertEqual(ordinary['model_windows']['synthetic/C1']['U3']['status'], 'pass')
        for key in ('U3', 'U4'):
            self.assertEqual(ordinary['model_windows']['synthetic/C1'][key],
                             escalated['model_windows']['synthetic/C1'][key])


if __name__ == '__main__':
    unittest.main()
