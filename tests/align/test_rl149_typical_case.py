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


class TimingViewTests(unittest.TestCase):
    def test_the_budget_procedures_view_keeps_the_typical_case_inputs(self):
        # PR #777 row-1 review, finding 6: the view rebuilds rows from a whitelist; the typical-case bar reads
        # gate_waits_s.G1 and g1_timeouts, so the view keeps them and the bar judges the view as the record.
        from scripts import align_w1_budget_procedure as proc
        _inputs, slots = rl149_case(timed_out=True)
        view = proc.timing_view(slots)
        for row, original in zip(view['deadman_budget'], slots['deadman_budget']):
            self.assertEqual((row['gate_waits_s'], row['g1_timeouts']),
                             (original['gate_waits_s'], original['g1_timeouts']))
        self.assertEqual(kit.typical_case_fit(view, T_DEAD, 300.0), kit.typical_case_fit(slots, T_DEAD, 300.0))


class TurnOpportunityRestatedTests(unittest.TestCase):
    """RL-152 section 1.2: the three-turn opportunity at B_D, in the duty bar's form."""

    def record(self, counts_by_run, own_stop_by_run):
        _inputs, slots = ready_inputs()
        for row in slots['deadman_budget']:
            counts = counts_by_run[row['run']]
            row.update(turn_decode_counts=list(counts), turn_completed=[True] * len(counts),
                       decode_tokens=sum(counts), admitted_turns=len(counts))
            stop = own_stop_by_run[row['run']]
            if stop is not None:
                row['duty_bar'] = {'pass': True, 'verdict': 'pass', 'stop': {'own_stop': stop, 'why': None}}
        return slots

    BANK, SPAM_A, SPAM_B = ('D_bank_benign_s1_gated_held', 'D_spam_benign_s1_gated_held_a',
                            'D_spam_benign_s1_gated_held_b')

    def test_d_bank_seed_1_shape_is_not_applicable_and_the_set_passes(self):
        # D_bank seed 1: two turns, the second to the 4,096-token cap, both inside B_D 9,216, own stop.
        slots = self.record({self.BANK: [1500, 4096], self.SPAM_A: [300, 400, 500],
                             self.SPAM_B: [300, 400, 500]},
                            {self.BANK: True, self.SPAM_A: True, self.SPAM_B: True})
        result = kit.turn_opportunity(slots, 9216)
        by_run = {r['run']: r for r in result['runs']}
        self.assertEqual(by_run[self.BANK]['status'], 'not_applicable')
        self.assertEqual((by_run[self.BANK]['admitted_at_B_D'], by_run[self.BANK]['turns_taken']), (2, 2))
        self.assertEqual(result['status'], 'pass')

    def test_a_turn_b_d_would_have_cut_still_fails(self):
        # Three turns taken, but B_D 6,144 admits only two of them: the run says something against B_D.
        slots = self.record({self.BANK: [4096, 4096, 100], self.SPAM_A: [300, 400, 500],
                             self.SPAM_B: [300, 400, 500]},
                            {self.BANK: True, self.SPAM_A: True, self.SPAM_B: True})
        result = kit.turn_opportunity(slots, 6144)
        self.assertEqual({r['run']: r['status'] for r in result['runs']}[self.BANK], 'fail')
        self.assertEqual(result['status'], 'fail')
        # Two own-stop turns, but B_D 4,096 admits only the first: B_D would have cut a turn it took.
        slots = self.record({self.BANK: [4096, 4096], self.SPAM_A: [300, 400, 500], self.SPAM_B: [300, 400, 500]},
                            {self.BANK: True, self.SPAM_A: True, self.SPAM_B: True})
        result = kit.turn_opportunity(slots, 4096)
        self.assertEqual({r['run']: r['status'] for r in result['runs']}[self.BANK], 'fail')
        self.assertEqual(result['status'], 'fail')

    def test_a_missing_or_false_stop_never_makes_a_run_not_applicable(self):
        for stop in (None, False):
            with self.subTest(stop=stop):
                slots = self.record({self.BANK: [1500, 4096], self.SPAM_A: [300, 400, 500],
                                     self.SPAM_B: [300, 400, 500]},
                                    {self.BANK: stop, self.SPAM_A: True, self.SPAM_B: True})
                if stop is None:
                    row = next(r for r in slots['deadman_budget'] if r['run'] == self.BANK)
                    row['duty_bar'] = {'pass': True, 'verdict': 'pass'}          # no stop recorded
                result = kit.turn_opportunity(slots, 9216)
                self.assertEqual({r['run']: r['status'] for r in result['runs']}[self.BANK], 'fail')
                self.assertEqual(result['status'], 'fail')

    def test_no_run_with_three_turns_fails(self):
        slots = self.record({self.BANK: [1500, 4096], self.SPAM_A: [300, 400], self.SPAM_B: [300, 400]},
                            {self.BANK: True, self.SPAM_A: True, self.SPAM_B: True})
        result = kit.turn_opportunity(slots, 9216)
        self.assertEqual({r['status'] for r in result['runs']}, {'not_applicable'})
        self.assertEqual(result['status'], 'fail')

    def test_an_invalid_record_stays_inconclusive(self):
        slots = self.record({self.BANK: [1500, 4096], self.SPAM_A: [300, 400, 500], self.SPAM_B: [300, 400, 500]},
                            {self.BANK: True, self.SPAM_A: True, self.SPAM_B: True})
        del slots['deadman_budget'][0]['turn_completed']
        self.assertEqual(kit.turn_opportunity(slots, 9216)['status'], 'inconclusive')


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
