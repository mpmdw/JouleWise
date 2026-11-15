"""Delta5 Sol1: synthetic committed-record/series integration witnesses.

No hardware, weights, network, measurement data or external custody is read.
The unmarked failing tests specify required fixes on 03253edca; product and
coordination-state changes belong to the lead. Short task-pair spellings in
counting-isolation tests are explicit; the exact generated spelling has its
own witness. Host observations and the final installer alone are replaced.
"""
from tests.align.test_v4_arm_watchdog_check import acceptance as _watchdog_acceptance
from tests.align.v4_registration_fixtures import session_plan
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_cadence as cadence, v4_registration
from scripts import align_v4_kit as kit, align_v4_next_arm_packet as builder
from scripts import align_v4_series as series, align_v4_session as session
from tests.align.test_v4_cadence import write_battery_log
from tests.align.test_v4_next_arm_packet import NOW, Scenario

ROOT = Path(__file__).resolve().parents[2]


class Delta5Witnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = series.load(ROOT)
        cls.plans = {}
        for extras in (0, 2):
            files = series.build_files(ROOT, cls.manifest, 'C1', extra_sentinels=extras)
            cls.plans[extras] = json.loads(files[series.kit_path('C1') / 'collection_plan.json'])

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='jw-r11-delta5-')
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name).resolve()

    def scenario(self, window='W1', *, previous=None, captured=True, next_window='C1'):
        root = previous.root if previous else self.tmp / 'repo'
        root.mkdir(exist_ok=True)
        s = Scenario(root, window, previous=previous, captured=captured)
        s.write(series.MANIFEST.as_posix(), series.raw_json(self.manifest))
        s.next_plan['window'] = next_window
        if next_window == 'W1':
            s.next_plan['role'] = 'development'
        return s

    def generated_roster(self, s, *, extras=0, exact_pair_names=False, excluded=(), only_supplemental=False):
        plan = deepcopy(self.plans[extras])
        if not exact_pair_names:
            for m in plan['members']:
                m['task_pair'] = series.PAIR_KEYS[m['task_pair']]
        prototype = deepcopy(s.thermal['members'][0])
        s.members = plan['members']
        s.sources['collection_plan'] = dict(plan, thermal_policy=dict(s.policy))
        s.thermal['members'] = []
        s.sources['exclusions']['members_excluded'] = []
        s.absent_captures = set()
        for planned in s.members:
            missing = only_supplemental and not planned.get('supplemental')
            barred = missing or planned['ordinal'] in excluded
            member = dict(deepcopy(prototype), id=planned['run_id'], role=planned['role'],
                          excluded=barred, calibration_exclusions=['member.runtime_failure'] if barred else [])
            session.assign_work_group(member, planned)
            s.thermal['members'].append(member)
            if barred:
                s.sources['exclusions']['members_excluded'].append(
                    dict(run_id=member['id'], codes=['member.runtime_failure']))
            if missing:
                s.absent_captures.add(member['id'])
        s.sources['pilot']['extra_checks']['km003c']['members'] = {
            m['run_id']: {'status': 'available', 'flags': []} for m in s.members}
        if only_supplemental:
            s.thermal['model_windows'][f'tiny/{s.window}']['U1']['status'] = 'fail'
        return s

    def eligibility(self, s):
        return builder.WindowRecord(builder.GitEvidence(s.root), s.record_commit, s.record_path).eligibility()

    def arm(self, s, packet, *, window):
        """Real rebuild, equality, record binding, triage and series binding; fake host/install."""
        scratch = self.tmp / ('arm-' + str(len(list(self.tmp.iterdir()))))
        scratch.mkdir()
        log = write_battery_log(scratch / 'battery.jsonl', NOW)
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        host = lambda argv: subprocess.CompletedProcess(argv, 0, 'synthetic host', '')
        state = session_plan(scratch, {'source_measurement_root': str(s.root),
                                      'v4_series': {'window_id': window}}, now=NOW)
        with patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(scratch / 'host')}), \
             patch('joulewise.align.apple.powermode.admit_ac_powermode',
                   return_value={'admitted': True, 'observed': 0}), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check',
                   return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', return_value=(good, b'synthetic ioreg')), \
             patch.object(session, 'w1_disk_check', return_value={'status': 'pass'}), \
             patch.object(session.pilot, 'install', return_value={'exit_code': 0}) as installer:
            try:
                session._arm_and_install(scratch, state, s.root, {'runtime_requirements': {'ac_powermode': 0}},
                    None, watchdog_check=_watchdog_acceptance, runner=host, volume_runner=host, now=lambda: NOW, w1_disk_config=None, disk_gate=None,
                    obc_off_attested_by='synthetic-review', battery_log=log, next_arm_triage=packet,
                    meter_probe=lambda root: {'live': True})
                error = None
            except ValueError as exc:
                error = str(exc)
            record = json.loads((scratch / 'staging/v4-arm-001.json').read_bytes())
            return record, error, installer.call_count

    def test_seed_checked_manifest_bytes_and_dynamic_closure_are_preserved(self):
        # R22-2 changed the manifest bytes by design (reserve windows appended at seeds 100-131): every R15
        # seed-checked window (W1, C1-C8, T1-T3) must be preserved exactly; the paired seed check of the new
        # bytes follows. The committed file is still exactly the generator's output.
        # RUN_STATE 252 option B (adapted by name): the seeded sabotage placement moves which fresh ordinal of
        # each pair is sabotage-instructed, so the checked windows keep every seed field, not every byte.
        from tests.align.v4_option_b import assert_seed_preserved
        result = subprocess.run(['git', 'show', '79777d261:' + series.MANIFEST.as_posix()],
                                cwd=ROOT, capture_output=True, check=True)
        checked = json.loads(result.stdout)
        current = json.loads((ROOT / series.MANIFEST).read_bytes())
        self.assertEqual((ROOT / series.MANIFEST).read_bytes(), series.raw_json(self.manifest))
        by_id = {w['id']: w for w in current['windows']}
        for window in checked['windows']:                  # W1, C1-C8 AND T1-T3: every seed as seed-checked (R15)
            assert_seed_preserved(self, window, by_id[window['id']])
        trace = json.loads((ROOT / 'docs/align/v4/dynamic_closure_trace.json').read_bytes())
        # the committed trace grows with each merged module (timing_receipts joined at integration item 6)
        self.assertGreaterEqual(len(trace['executed']), 180)
        self.assertIn('joulewise/timing_receipts.py', trace['executed'])
        self.assertTrue(trace['scenarios']['dct_series_window']['ok'])
        for path in ('scripts/align_v4_series.py', series.MANIFEST.as_posix()):
            self.assertIn(path, v4_registration.ARTIFACTS)
            self.assertTrue(v4_registration.is_strict(path))

    def test_w1_and_c1_bind_the_real_rebuild_and_edited_history_or_target_refuses(self):
        for previous, target in (('R1', 'W1'), ('W1', 'C1')):
            # Each independent synthetic repository has its own committed ref.
            if (self.tmp / 'repo').exists():
                self.tmp = self.tmp / 'independent'
                self.tmp.mkdir()
            s = self.scenario(previous, next_window=target).finish()
            honest = s.build()
            record, error, calls = self.arm(s, honest, window=target)
            self.assertIsNone(error, record['reasons'])
            self.assertEqual((record['admitted'], calls, record['series_binding']), (True, 1, []))
            variants = [dict(honest, next_window_id='C8'),
                        dict(honest, series_manifest_sha256='0' * 64),
                        dict(honest, series_history=[dict(window_id='C1', attempt_id='C1',
                            captured_members=22, status='final', eligible_benign={'spam': 7, 'bank': 7})])]
            for packet in variants:
                with self.subTest(previous=previous, changed=[k for k in packet if packet[k] != honest[k]]):
                    record, error, calls = self.arm(s, packet, window=target)
                    self.assertIsNotNone(error)
                    self.assertFalse(record['admitted'])
                    self.assertEqual(calls, 0)
                    self.assertFalse(record['next_arm_triage']['supplied_packet_matches_rebuild'])
                    self.assertEqual(record['series_packet']['next_window_id'], target)
            record, error, calls = self.arm(s, honest, window='C8')
            self.assertIsNotNone(error)
            self.assertFalse(record['admitted'])
            self.assertEqual(calls, 0)
            self.assertTrue(record['series_binding'])

    def test_committed_23_captures_cannot_pass_the_frozen_22_member_binding(self):
        first = self.scenario().finish()
        s = self.generated_roster(self.scenario('C1', previous=first, next_window='C2'), extras=2,
                                  excluded=(5, 22, 23, 24))
        # An illegal ordinary 23-member roster: no supplemental marker can
        # justify the extra member. This stays an overflow after R20 is fixed.
        dropped = s.members.pop()['run_id']
        s.sources['collection_plan'].pop('extra_sentinels', None)
        for m in s.members:
            m.pop('supplemental', None)
            m.pop('escalation_sentinel', None)
        s.thermal['members'] = [m for m in s.thermal['members'] if m['id'] != dropped]
        for m in s.thermal['members']:
            m.pop('supplemental', None)
            m.pop('escalation_sentinel', None)
        s.sources['exclusions']['members_excluded'] = [
            m for m in s.sources['exclusions']['members_excluded'] if m['run_id'] != dropped]
        s.sources['pilot']['extra_checks']['km003c']['members'].pop(dropped)
        s.finish()
        packet = s.build()
        # delta5 S2 F5: the count-only predicate now refuses 23 itself (ceiling 22), so the history is
        # refused when the packet is built; the frozen-series binding remains a second, independent guard.
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertIn('captured_members in 0..22', packet['calibration_error'])
        record, error, calls = self.arm(s, packet, window='C2')
        self.assertIsNotNone(error)
        self.assertFalse(record['admitted'])
        self.assertEqual(calls, 0)

    def test_generated_pair_names_are_accepted_by_production_eligibility(self):
        first = self.scenario().finish()
        s = self.generated_roster(self.scenario('C1', previous=first, next_window='C2'),
                                  exact_pair_names=True, excluded=(5, 22)).finish()
        self.assertEqual(self.eligibility(s)['eligible_benign'], {'spam': 7, 'bank': 7})

    def test_sentinel_pool_members_do_not_inflate_m_in_an_admitted_rebuilt_packet(self):
        first = self.scenario().finish()
        # Two genuine spam calibrators and the ordinary sentinels are excluded.
        # The two SUPPLEMENTAL sentinels must not replace the calibrators in m.
        # Two missing anchors keep the erroneous raw capture total within 22,
        # proving that the separate 22-member check does not catch this case.
        spam = [m['ordinal'] for m in self.plans[0]['members']
                if m['pool_role'] == 'calibration' and m['task_pair'] == series.PAIRS[0]]
        s = self.generated_roster(self.scenario('C1', previous=first, next_window='C2'),
                                  extras=2, excluded=spam[:2] + [1, 2, 5, 22])
        s.absent_captures.update(m['run_id'] for m in s.members[:2])
        s.finish()
        packet = s.build()
        record, error, calls = self.arm(s, packet, window='C2')
        self.assertIsNone(error, record['reasons'])
        self.assertEqual((record['admitted'], calls), (True, 1))
        self.assertEqual(packet['calibration_windows'][0]['eligible_benign'], {'spam': 5, 'bank': 7})

    def test_supplemental_only_captures_do_not_advance_a_counted_calibration_window(self):
        first = self.scenario().finish()
        s = self.generated_roster(self.scenario('C1', previous=first, next_window='C2'), extras=2,
                                  only_supplemental=True).finish()
        row = self.eligibility(s)
        self.assertEqual(row['eligible_benign'], {'spam': 0, 'bank': 0})
        decision = cadence.calibration_stop([row])
        self.assertEqual((row['captured_members'], decision['attempted']), (0, 0),
                         'only supplemental diagnostics were captured')

    def test_captured_retry_can_bind_the_next_slot_without_losing_the_attempt_suffix(self):
        first = self.scenario().finish()
        zero = self.scenario('C1', previous=first, captured=False, next_window='C1').finish()
        s = self.scenario('C1#2', previous=zero, next_window='C2').finish()
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight']['reasons'])
        self.assertEqual([a['attempt_id'] for a in packet['series_history']], ['C1', 'C1#2'])
        record, error, calls = self.arm(s, packet, window='C2')
        self.assertIsNone(error, record['series_binding'])
        self.assertEqual((record['admitted'], calls), (True, 1))

    def test_supplemental_records_change_neither_u3_group_pairs_nor_u4_windows(self):
        from joulewise.align.apple import thermal_desk
        from tests.align.test_thermal_desk import member
        base = []
        for ordinal in (5, 22, 23, 24):
            row = dict(self.plans[2]['members'][ordinal - 1])
            record = member(row['run_id'])
            record.update(window='C1', role='D')
            session.assign_work_group(record, row)
            base.append(record)
        reports = []
        cross = {'synthetic': {'sentinels': {'status': 'pass', 'W': 8, 'df': 7}}}
        for records in (base[:2], base):
            report = thermal_desk.window_report(records, v4=True, cross_windows=cross)
            reports.append(next(iter(report['model_windows'].values())))
        self.assertEqual(len(reports[0]['U3']['pairs']), 1)
        self.assertEqual(reports[0]['U3'], reports[1]['U3'])
        self.assertEqual(reports[0]['U4'], reports[1]['U4'])
        self.assertTrue(all('identical_work_group' not in r for r in base[2:]))


if __name__ == '__main__':
    unittest.main()
