"""RL-148 section 2 ("What replaces the fit in the kit"), as RL-149 section 1.5 sets the numbers.

``require_ready`` no longer refuses on ruling 1(f)'s worst case for D. It asks that the typical case fits:
each of R1's three gated D runs, with its own prefill, tool and decode seconds, plus the G0 seconds and, for
each of its G1s, the largest G1 (the G_turn cap if any G1 timed out), ends inside T_dead. Synthetic R1
records only; the RL-149 table's seconds are protocol arithmetic on rehearsal timings, not study data.
"""
from copy import deepcopy
import unittest

from scripts import align_r1_rehearsal as r1
from scripts import align_v4_kit as kit
from tests.align.test_v4_kit import ready_inputs, set_decode_rate

# RL-149 section 1.5's table: T_dead 983.10 s, G0 110.78 s, largest D G1 99.82 s.
T_DEAD = 983.10
G0 = 110.78
G1 = 99.82


def rl149_case(*, timed_out=False):
    """Three gated runs shaped as RL-149's table: D_bank (459.00 s of prefill + decode, two turns, one G1) and
    D_spam a and b (185.9 and 185.4 s, three turns, two G1s); tool seconds 0."""
    inputs, slots = ready_inputs()
    inputs['R1']['T_dead'] = T_DEAD
    shapes = {'D_bank_benign_s1_gated_held': (459.00, [G1]),
              'D_spam_benign_s1_gated_held_a': (185.9, [60.0, G1]),
              'D_spam_benign_s1_gated_held_b': (185.4, [70.0, 50.0])}
    for row in slots['deadman_budget']:
        own, waits = shapes[row['run']]
        row['phases_s'].update(G0=G0 if row['run'].startswith('D_bank') else 90.0, G1=sum(waits), H=0.0,
                               prefill=own - 120.0, decode=120.0, tool=0.0)
        row['gate_waits_s'] = {'G1': list(waits)}
        row['g1_timeouts'] = 1 if timed_out and row['run'].endswith('_b') else 0
    set_decode_rate(slots, 12.0)
    slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
    inputs['R1']['thermal_policy']['g0_cap_s'] = slots['g0_cap_w1']['value_s']
    return inputs, slots


class TypicalCaseTests(unittest.TestCase):
    def test_rl149_table_values_and_the_g_turn_column(self):
        _inputs, slots = rl149_case()
        fit = kit.typical_case_fit(slots, T_DEAD, 300.0)
        self.assertTrue(fit['fits'])
        self.assertEqual((fit['G0_s'], fit['G1_max_s']), (G0, G1))
        runs = fit['runs']
        self.assertAlmostEqual(runs['D_bank_benign_s1_gated_held']['total_s'], 669.60, places=2)    # RL-149 table
        self.assertAlmostEqual(runs['D_spam_benign_s1_gated_held_a']['total_s'], 496.32, places=2)
        self.assertAlmostEqual(runs['D_spam_benign_s1_gated_held_b']['total_s'], 495.82, places=2)
        # A G1 timeout anywhere puts every G1 at the G_turn cap: RL-149's last column.
        _inputs, slots = rl149_case(timed_out=True)
        fit = kit.typical_case_fit(slots, T_DEAD, 300.0)
        self.assertEqual(fit['G1_max_s'], 300.0)
        self.assertAlmostEqual(fit['runs']['D_bank_benign_s1_gated_held']['total_s'], 869.78, places=2)
        self.assertAlmostEqual(fit['runs']['D_spam_benign_s1_gated_held_a']['total_s'], 896.68, places=2)
        self.assertAlmostEqual(min(r['margin_s'] for r in fit['runs'].values()), 86.42, places=2)  # "86 s"
        self.assertTrue(fit['fits'])

    def test_require_ready_refuses_only_when_the_typical_case_misses(self):
        inputs, slots = rl149_case()
        result = kit.check_r1_budget_and_policy(inputs['R1'], slots, x_max_turns=12)
        self.assertFalse(result['worst_case_refuses'])
        self.assertFalse(result['fits'])          # ruling 1(f)'s worst case is printed and no longer refuses
        self.assertTrue(result['typical_case']['fits'])
        late = deepcopy(slots)
        next(r for r in late['deadman_budget'] if r['run'].startswith('D_bank'))['phases_s']['prefill'] += 400.0
        with self.assertRaisesRegex(ValueError, 'RL-148 typical-case bar.*D_bank_benign_s1_gated_held'):
            kit.check_r1_budget_and_policy(inputs['R1'], late, x_max_turns=12)

    def test_an_r1_record_without_per_g1_waits_or_timeouts_is_refused(self):
        inputs, slots = rl149_case()
        for field, value, pattern in (('gate_waits_s', None, 'per-G1 waits'), ('gate_waits_s', {'G1': [-1.0]},
                                                                               'per-G1 waits'),
                                      ('g1_timeouts', None, 'g1_timeouts')):
            with self.subTest(field=field, value=value):
                bad = deepcopy(slots)
                bad['deadman_budget'][1][field] = value
                with self.assertRaisesRegex(ValueError, pattern):
                    kit.typical_case_fit(bad, T_DEAD, 300.0)

    def test_the_driver_records_the_fields_the_bar_reads(self):
        result = {'admitted_turns': 2, 'x7': False, 'episode_flags': ['thermal.gate_timeout:2'],
                  'gate_waits_s': {'G0': [110.0], 'G1': [99.5, 300.0], 'H': []},
                  'deadman': {'T_dead_s': T_DEAD, 'phases_s': {'G0': 110.0, 'G1': 399.5, 'H': 0.0, 'decode': 300.0,
                                                               'prefill': 60.0, 'tool': 0.0, 'tail': 5.0}}}
        row = r1.deadman_summary('D_bank_benign_s1_gated_held', result)
        self.assertEqual((row['gate_waits_s'], row['g1_timeouts']), ({'G1': [99.5, 300.0]}, 1))
        bare = r1.deadman_summary('d', {k: v for k, v in result.items() if k not in ('gate_waits_s', 'episode_flags')})
        self.assertEqual((bare['gate_waits_s'], bare['g1_timeouts']), ({'G1': None}, None))


class DutySetClauseInTheKitTests(unittest.TestCase):
    def test_the_kit_rederives_the_three_turn_set_clause(self):
        _inputs, slots = ready_inputs()
        for row in slots['deadman_budget']:
            row['admitted_turns'] = 2
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            kit.check_duty_bar_consistency(slots)
        slots['duty_bar'].update({'pass': False, 'verdict': 'fail'})
        kit.check_duty_bar_consistency(slots)
        slots['deadman_budget'][0]['admitted_turns'] = 3
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            kit.check_duty_bar_consistency(slots)


if __name__ == '__main__':
    unittest.main()
