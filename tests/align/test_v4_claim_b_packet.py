"""Agreement items 19-21: synthetic committed records, no hardware or data."""
from copy import deepcopy
import unittest

from scripts import align_v4_series as series
from tests.align.test_v4_next_arm_packet import Base, Scenario, evaluate

RESET = 'u1_u3_fail_escalation'


class ClaimBPacketTests(Base):
    def chain(self, specs, *, next_window=None, change_policy=False, pool=False):
        first = self.scenario().finish()
        previous = first
        for window, status in specs:
            s = Scenario(first.root, window, previous=previous)
            if window.startswith('T'):
                s.record['role'] = 'test'
            # Seven eligible benign members per pair make the T-prefix calibration real.
            originals = list(s.members)
            thermal = list(s.thermal['members'])
            for i in range(1, 7):
                for m, t in zip(originals, thermal):
                    rid = m['run_id'] + f'-{i}'
                    s.members.append({**m, 'run_id': rid})
                    s.thermal['members'].append({**deepcopy(t), 'id': rid})
            s.thermal['model_windows'][f'tiny/{window}']['U3']['status'] = status
            previous = s
            s.finish()
        if next_window is not None:
            s.next_plan.update(window=next_window, role='test' if next_window.startswith('T') else 'calibration')
        if change_policy:
            s.next_plan['thermal_policy']['idle_s'] = 450
            s.series['escalations'] = [{'window': s.window, 'ruling_id': 'SYNTHETIC-LADDER',
                                       'next_plan_sha256': s.write('next-plan.json', s.next_plan)['sha256']}]
        if pool:
            s.series['pool_members'] = [m['run_id'] for m in s.members]
        s.series['next_plan'] = s.write(f'{s.dir}/series/next_plan.json', s.next_plan)
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        return s

    def rule(self, s, after=None, *, signature='lead: synthetic-rl20 2026-11-10', reset=RESET):
        text = s.write(f'{s.dir}/ruling.txt', b'Synthetic structural ruling: continue unchanged.\n')
        s.series['lead_rulings'] = [{'ruling_id': 'SYNTHETIC-RL20', 'after_window': after or s.window,
                                    'resets': reset, 'text': text, 'lead_signature': signature}]
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()

    def assert_thermal(self, s, status, reason=None):
        packet = s.build()
        check = packet['checks']['thermal_escalation']
        self.assertEqual(check['status'], status, check)
        if reason:
            self.assertIn(reason, check['basis'])
        return packet

    def test_item19_c_inconclusive_enters_pool_without_ladder_or_bar_and_counts_slot(self):
        s = self.chain([('C1', 'inconclusive')], next_window='C2', pool=True)
        packet = self.assert_thermal(s, 'pass')
        self.assertEqual(packet['checks']['cohort_pool_rules']['status'], 'pass')
        self.assertNotIn('barred', packet['series_history'][0])
        self.assertEqual(packet['calibration_decision']['attempted'], 1)
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])

    def test_item19_t_and_reserve_inconclusive_use_slots_without_ladder_or_bar(self):
        specs = [(f'C{i}', 'pass') for i in range(1, 9)]
        specs += [('T1', 'fail'), ('T2', 'pass'), ('T3', 'pass'), ('T4', 'inconclusive')]
        s = self.chain(specs, next_window='T5', pool=True)
        packet = self.assert_thermal(s, 'pass')
        self.assertEqual(packet['checks']['cohort_pool_rules']['status'], 'pass')
        self.assertNotIn('barred', packet['series_history'][-1])
        self.assertIsNone(series.calibration_rows(series.candidate(), packet['series_history'])[1])

    def test_item20_c_fail_accepts_unchanged_plan_and_records_bar(self):
        s = self.chain([('C1', 'fail')], next_window='C2')
        packet = self.assert_thermal(s, 'pass')
        self.assertEqual(packet['series_history'][-1]['barred'], 'u1_u3_fail')
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])

    def test_item20_c_fail_refuses_ladder_even_when_escalation_recorded(self):
        s = self.chain([('C1', 'fail')], next_window='C2', change_policy=True)
        self.assert_thermal(s, 'fail', 'series_thermal_policy_changed')

    def test_item20_c_pass_and_inconclusive_also_refuse_policy_changes(self):
        for status in ('pass', 'inconclusive'):
            s = self.chain([('C1', status)], next_window='C2', change_policy=True)
            self.assert_thermal(s, 'fail', 'series_thermal_policy_changed')

    def test_item20_t_fail_and_reserve_accept_unchanged_plan_but_refuse_ladder(self):
        prefix = [(f'C{i}', 'pass') for i in range(1, 9)]
        prefix += [('T1', 'fail'), ('T2', 'pass'), ('T3', 'pass')]
        for suffix, next_window in (([], 'T4'), ([('T4', 'fail')], 'T5')):
            s = self.chain(prefix+suffix, next_window=next_window)
            self.assert_thermal(s, 'pass')
            s = self.chain(prefix+suffix, next_window=next_window, change_policy=True)
            self.assert_thermal(s, 'fail', 'series_thermal_policy_changed')

    def test_item21_two_consecutive_c_fail_bars_hold_until_signed_ruling(self):
        s = self.chain([('C1', 'fail'), ('C2', 'fail')], next_window='C3')
        self.assert_thermal(s, 'fail', RESET)
        self.rule(s)
        packet = self.assert_thermal(s, 'pass')
        self.assertEqual(packet['checks']['thermal_escalation']['rulings'][0]['resets'], RESET)
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertTrue(evaluate(s, packet)['admitted'])

    def test_item21_third_nonconsecutive_c_fail_bar_holds_until_ruling(self):
        s = self.chain([('C1', 'fail'), ('C2', 'pass'), ('C3', 'fail'),
                        ('C4', 'inconclusive'), ('C5', 'fail')], next_window='C6')
        self.assert_thermal(s, 'fail', RESET)
        self.rule(s)
        self.assert_thermal(s, 'pass')

    def test_item21_two_consecutive_t_and_reserve_fail_bars_hold_until_ruling(self):
        prefix = [(f'C{i}', 'pass') for i in range(1, 9)]
        prefix += [('T1', 'pass'), ('T2', 'pass'), ('T3', 'fail'), ('T4', 'fail')]
        s = self.chain(prefix, next_window='T5')
        self.assert_thermal(s, 'fail', RESET)
        self.rule(s)
        packet = self.assert_thermal(s, 'pass')
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertTrue(evaluate(s, packet)['admitted'])

    def test_item21_third_nonconsecutive_bar_counts_c_and_t_attempts_together(self):
        prefix = [(f'C{i}', 'fail' if i == 1 else 'pass') for i in range(1, 10)]
        prefix += [('T1', 'fail'), ('T2', 'pass'), ('T3', 'fail')]
        s = self.chain(prefix, next_window='T4')
        self.assert_thermal(s, 'fail', RESET)
        self.rule(s)
        self.assert_thermal(s, 'pass')

    def test_item21_bad_signature_wrong_window_and_wrong_reset_do_not_release(self):
        for changes in ({'signature': 'PENDING'}, {'after': 'C1'}, {'reset': 'zero_capture_escalation'}):
            s = self.chain([('C1', 'fail'), ('C2', 'fail')], next_window='C3')
            self.rule(s, **changes)
            self.assertFalse(s.build()['packet_preflight']['ready'])

    def test_item21_third_nonconsecutive_bar_in_test_reserve_requires_ruling(self):
        prefix = [(f'C{i}', 'fail' if i == 1 else 'pass') for i in range(1, 10)]
        prefix += [('T1', 'fail'), ('T2', 'pass'), ('T3', 'pass'), ('T4', 'fail')]
        s = self.chain(prefix, next_window='T5')
        self.assert_thermal(s, 'fail', RESET)
        self.rule(s)
        packet = self.assert_thermal(s, 'pass')
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])

    def test_item21_a_later_pass_does_not_erase_an_unruled_hold(self):
        s = self.chain([('C1', 'fail'), ('C2', 'fail'), ('C3', 'pass')], next_window='C4')
        self.assert_thermal(s, 'fail', RESET)


if __name__ == '__main__':
    unittest.main()
