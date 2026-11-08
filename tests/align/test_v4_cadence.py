"""R12 (RUN_STATE 214/215): next-arm triage list (B2) and the fixed-8 calibration predicate (B3).

Synthetic only. The stop tests check the predicate, not exchangeability.
"""
import itertools
from pathlib import Path
import unittest

from joulewise.align.apple import v4_cadence as cad

PAIRS = cad.CAL_PAIRS


def passing_packet(**overrides):
    """A complete passing packet for a calibration arm after window C2."""
    packet = {'schema': cad.TRIAGE_SCHEMA, 'previous_window': 'C2',
              'previous_window_is_w1': False, 'code_or_config_changed': False,
              'next_window_role': 'calibration',
              'calibration_windows': [window('C1', 7, 7), window('C2', 7, 7)],
              'checks': {row['id']: {'status': 'pass', 'basis': 'synthetic'}
                         for row in cad.NEXT_ARM_TRIAGE if row['source'] == cad.PACKET}}
    packet.update(overrides)
    return packet


def window(name, spam, bank, status='final', captured=18):
    return {'window': name, 'status': status, 'captured_members': captured,
            'eligible_benign': {'spam': spam, 'bank': bank}}


INTERNAL = {'series_powermode': True, 'external_volume': True, 'charging_battery': True}


class TriageListTests(unittest.TestCase):
    def test_every_listed_check_is_present_and_gating(self):
        # The frozen list enumerates the next-arm-dependent checks named by R12/R215.
        self.assertEqual(set(cad.TRIAGE_IDS), {
            'record_committed', 'terminal_completion', 'quiet_start_state', 'series_powermode',
            'external_volume', 'charging_battery', 'meter_samples_clock', 'capture_faults',
            'thermal_escalation', 'cohort_pool_rules', 'sentinel_roster', 'member_eligibility',
            'calibration_stop', 'full_desk_gate'})
        self.assertEqual(len(cad.TRIAGE_IDS), len(set(cad.TRIAGE_IDS)))
        ok = cad.next_arm_triage(passing_packet(), INTERNAL)
        self.assertTrue(ok['admitted'], ok['reasons'])
        self.assertEqual(set(ok['checks']), set(cad.TRIAGE_IDS))
        # Each check gates: failing, or removing, any one refuses the arm.
        for name in cad.TRIAGE_IDS:
            with self.subTest(failing=name):
                internal, packet = dict(INTERNAL), passing_packet()
                if name in internal:
                    internal[name] = False
                elif name == 'calibration_stop':
                    packet['next_window_role'] = 'test'      # still 'continue' after two windows
                else:
                    packet['checks'][name]['status'] = 'fail'
                self.assertFalse(cad.next_arm_triage(packet, internal)['admitted'])
            if name in passing_packet()['checks']:
                with self.subTest(missing=name):
                    packet = passing_packet()
                    del packet['checks'][name]
                    self.assertFalse(cad.next_arm_triage(packet, INTERNAL)['admitted'])
            if name in INTERNAL:
                with self.subTest(unevaluated=name):
                    internal = dict(INTERNAL)
                    del internal[name]
                    self.assertFalse(cad.next_arm_triage(passing_packet(), internal)['admitted'])

    def test_packet_cannot_supply_or_override_arm_computed_checks(self):
        packet = passing_packet()
        packet['checks']['series_powermode'] = {'status': 'pass', 'basis': 'forged'}
        self.assertFalse(cad.next_arm_triage(packet, {**INTERNAL, 'series_powermode': False})['admitted'])
        packet = passing_packet()
        packet['checks']['extra_check'] = {'status': 'pass', 'basis': 'unlisted'}
        self.assertFalse(cad.next_arm_triage(packet, INTERNAL)['admitted'])

    def test_malformed_packet_refuses(self):
        for packet in (None, {}, passing_packet(schema='x'), passing_packet(previous_window=''),
                       passing_packet(previous_window_is_w1=None), passing_packet(code_or_config_changed='no')):
            with self.subTest(packet=packet):
                self.assertFalse(cad.next_arm_triage(packet, INTERNAL)['admitted'])
        blank = passing_packet()
        blank['checks']['record_committed']['basis'] = ' '
        self.assertFalse(cad.next_arm_triage(blank, INTERNAL)['admitted'])

    def test_full_desk_gate_is_required_after_w1_and_after_code_or_config_change(self):
        for flags in ({'previous_window_is_w1': True}, {'code_or_config_changed': True}):
            packet = passing_packet(**flags)
            packet['checks']['full_desk_gate'] = {'status': 'deferred', 'basis': 'desk running off MBP'}
            with self.subTest(flags=flags):
                self.assertFalse(cad.next_arm_triage(packet, INTERNAL)['admitted'])
                packet['checks']['full_desk_gate'] = {'status': 'pass', 'basis': 'desk complete'}
                self.assertTrue(cad.next_arm_triage(packet, INTERNAL)['admitted'])
        # An unchanged later window need not wait for the desk's pass, but must report it.
        later = passing_packet()
        later['checks']['full_desk_gate'] = {'status': 'deferred', 'basis': 'running on laptop'}
        self.assertTrue(cad.next_arm_triage(later, INTERNAL)['admitted'])
        later['checks']['full_desk_gate'] = {'status': 'not_applicable', 'basis': 'running on laptop'}
        self.assertFalse(cad.next_arm_triage(later, INTERNAL)['admitted'])
        other = passing_packet()
        other['checks']['record_committed'] = {'status': 'deferred', 'basis': 'commit running'}
        self.assertFalse(cad.next_arm_triage(other, INTERNAL)['admitted'])

    def test_not_applicable_is_only_for_previous_window_checks_before_w1(self):
        first = passing_packet(previous_window='R1', calibration_windows=[], next_window_role=None)
        for name in ('thermal_escalation', 'cohort_pool_rules', 'sentinel_roster', 'member_eligibility'):
            first['checks'][name] = {'status': 'not_applicable', 'basis': 'previous window is R1'}
        self.assertTrue(cad.next_arm_triage(first, INTERNAL)['admitted'], cad.next_arm_triage(first, INTERNAL)['reasons'])
        first['checks']['record_committed'] = {'status': 'not_applicable', 'basis': 'skip'}
        self.assertFalse(cad.next_arm_triage(first, INTERNAL)['admitted'])
        later = passing_packet()
        later['checks']['thermal_escalation'] = {'status': 'not_applicable', 'basis': 'skip'}
        self.assertFalse(cad.next_arm_triage(later, INTERNAL)['admitted'])


class CalibrationStopTests(unittest.TestCase):
    def test_constants_are_the_ruled_fixed_8_and_39_per_pair(self):
        self.assertEqual((cad.CAL_WINDOWS, cad.CAL_TARGET_PER_PAIR), (8, 39))
        for gone in ('CAL_MIN_WINDOWS', 'CAL_CAP_WINDOWS'):
            self.assertFalse(hasattr(cad, gone))        # no minimum, no early stop (RUN_STATE 217)

    def test_no_early_stop_even_when_six_or_seven_windows_already_meet_the_target(self):
        for n in (6, 7):
            rows = [window(f'C{i}', 7, 7) for i in range(1, n+1)]       # 42/42 or 49/49 >= 39
            result = cad.calibration_stop(rows)
            self.assertEqual((result['decision'], result['attempted']), ('continue', n))
        self.assertEqual(cad.calibration_stop([])['decision'], 'continue')
        rows = [window(f'C{i}', 7, 7, 'provisional') for i in range(1, 8)]
        self.assertEqual(cad.calibration_stop(rows)['decision'], 'continue')     # provisional is fine before 8

    def test_exactly_eight_final_windows_decide(self):
        done = [window(f'C{i}', 7, 7) for i in range(1, 9)]
        self.assertEqual(cad.calibration_stop(done)['decision'], 'calibration_complete')
        pending = done[:7] + [window('C8', 7, 7, 'provisional')]
        self.assertEqual(cad.calibration_stop(pending)['decision'], 'pending_final_eligibility')
        with self.assertRaises(ValueError):
            cad.calibration_stop(done + [window('C9', 7, 7)])             # no ninth counted window

    def test_both_pairs_must_reach_39_after_eight(self):
        rows = [window(f'C{i}', 7, 4) for i in range(1, 9)]               # spam 56, bank 32
        result = cad.calibration_stop(rows)
        self.assertEqual((result['decision'], result['eligible_by_pair']['bank']), ('insufficient_calibration', 32))
        edge = [window(f'C{i}', 7, 5) for i in range(1, 8)] + [window('C8', 7, 4)]        # bank 39 exactly
        self.assertEqual(cad.calibration_stop(edge)['decision'], 'calibration_complete')
        short = [window(f'C{i}', 7, 5) for i in range(1, 8)] + [window('C8', 7, 3)]       # bank 38
        self.assertEqual(cad.calibration_stop(short)['decision'], 'insufficient_calibration')

    def test_lost_whole_window_still_counts_and_can_leave_the_target_unmet(self):
        # One whole-window loss: 7 x 7 = 49 >= 39 still completes; losing 2 of 8 leaves 42 and completes;
        # five losses leave 21 and fail closed.
        lost = lambda n: [window(f'C{i}', 7, 7) for i in range(1, 9-n)] + [window(f'L{i}', 0, 0) for i in range(n)]
        self.assertEqual(cad.calibration_stop(lost(1))['decision'], 'calibration_complete')
        self.assertEqual(cad.calibration_stop(lost(2))['decision'], 'calibration_complete')
        self.assertEqual(cad.calibration_stop(lost(5))['decision'], 'insufficient_calibration')

    def test_zero_capture_windows_do_not_count_and_two_in_a_row_escalate(self):
        refused = lambda name: window(name, 0, 0, captured=0)
        rows = [window('C1', 7, 7), refused('C2-refusal-1'), window('C2', 7, 7)]
        result = cad.calibration_stop(rows)
        self.assertEqual((result['decision'], result['attempted'], result['zero_capture_refusals']),
                         ('continue', 2, 1))
        self.assertEqual(cad.calibration_stop([window('C1', 0, 0, captured=1)])['attempted'], 1)   # one member counts
        eight = [window(f'C{i}', 7, 7) for i in range(1, 9)]
        self.assertEqual(cad.calibration_stop(eight + [refused('R1')])['decision'], 'calibration_complete')
        with self.assertRaises(ValueError):
            cad.calibration_stop(eight + [window('C9', 7, 7)])
        two = [window('C1', 7, 7), refused('R1'), refused('R2')]
        self.assertEqual(cad.calibration_stop(two)['decision'], 'escalate_to_lead')
        self.assertEqual(cad.calibration_stop([refused('R1'), window('C1', 7, 7), refused('R2')])['decision'], 'continue')
        for role in ('calibration', 'test'):
            self.assertFalse(cad.next_arm_triage(passing_packet(calibration_windows=two, next_window_role=role),
                                                 INTERNAL)['admitted'])
        with self.assertRaises(ValueError):
            cad.calibration_stop([window('C1', 3, 0, captured=0)])         # zero-capture cannot carry eligible members
        with self.assertRaises(ValueError):
            cad.calibration_stop([{'window': 'C1', 'status': 'final', 'eligible_benign': {'spam': 0, 'bank': 0}}])

    def test_decision_uses_only_counts_and_status(self):
        rows = [dict(window('C1', 7, 7), score=9.9, alarm=True)] + [window(f'C{i}', 7, 7) for i in range(2, 9)]
        self.assertEqual(cad.calibration_stop(rows), cad.calibration_stop([window(f'C{i}', 7, 7) for i in range(1, 9)]))

    def test_invalid_rows_are_refused(self):
        good = [window(f'C{i}', 7, 7) for i in range(1, 8)]
        for bad in (good + [window('C8', 8, 7)], good + [window('C8', -1, 7)], good + [window('C8', True, 7)],
                    good + [window('C1', 7, 7)], good + [window('C8', 7, 7, 'done')], good + [{'window': 'C8'}]):
            with self.subTest(bad=bad[-1]), self.assertRaises(ValueError):
                cad.calibration_stop(bad)

    def test_triage_role_follows_the_fixed_8_decision(self):
        done = [window(f'C{i}', 7, 7) for i in range(1, 9)]
        self.assertFalse(cad.next_arm_triage(passing_packet(calibration_windows=done), INTERNAL)['admitted'])
        test = cad.next_arm_triage(passing_packet(calibration_windows=done, next_window_role='test'), INTERNAL)
        self.assertTrue(test['admitted'], test['reasons'])
        # Seven windows: a test arm is refused (no early stop), a calibration arm is allowed.
        seven = done[:7]
        self.assertTrue(cad.next_arm_triage(passing_packet(calibration_windows=seven), INTERNAL)['admitted'])
        self.assertFalse(cad.next_arm_triage(passing_packet(calibration_windows=seven, next_window_role='test'),
                                             INTERNAL)['admitted'])
        failed = [window(f'C{i}', 0, 0) for i in range(1, 9)]
        for role in ('calibration', 'test'):
            self.assertFalse(cad.next_arm_triage(passing_packet(calibration_windows=failed,
                                                                next_window_role=role), INTERNAL)['admitted'])


class RegistrationTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        text = (root / 'docs/align/pilot_protocol_v4.md').read_text()
        start = text.index('## R12 window cadence')
        cls.section = ' '.join(text[start:text.index('\n## ', start+10)].split())
        cls.r1 = (root / 'docs/align/r1_runtime_contract.md').read_text()

    def test_protocol_states_b1_b2_b3_and_lists_every_triage_check(self):
        for name in cad.TRIAGE_IDS:
            self.assertIn(f'`{name}`', self.section)
        for phrase in ('ceiling, not a reservation', 'authenticated terminal completion', 'RUN_STATE 217',
                       'insufficient_calibration', 'calibration_complete', 'fixed 8', 'not satisfied by counts alone',
                       'Open statistics item', 'minimum of 7', '0.5 s_r', 'zero-capture', 'escalate to the lead', '67,371 s', '96,427 s', '--next-arm-triage'):
            self.assertIn(phrase, self.section)

    def test_stale_r1_sizing_is_marked_and_corrected(self):
        self.assertIn('STALE', self.r1)
        self.assertIn('67,371 s', self.r1)
        self.assertIn('96,427 s', self.r1)
        self.assertNotIn('window_max_s` is set from this table', self.r1)


if __name__ == '__main__':
    unittest.main()
