"""PR #777 row-2 attack (Mythos 5.2, /Volumes/JW-EXT/scratch/mythos-777-attack/REPORT.md): tests built from the
seat's reproductions, one class per finding the lead's dispositions fix on PR #783. Each repro fails at 2646197e3
(PR #783 before these fixes) and passes with the fix.
Finding 6 was fixed by RL-153 section 1.2 finding 1 (tests/align/test_w1_3a_desk.py). Synthetic records and
journals only; no host, journal or study data.
"""
import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import align_r1_part_c as pc
from scripts import align_r1_rehearsal as r1
from scripts import align_v4_kit as kit
from scripts import align_w1_3a_desk as desk
from scripts import align_w1_budget_procedure as proc
from scripts import run_align_r1_smoke as smoke
from tests.align.test_v4_kit import ready_inputs, set_decode_rate
from tests.align.test_w1_rl122_kit import planning_slots, release_for

NS = 1_000_000_000
BANK, SPAM_A, SPAM_B = ('D_bank_benign_s1_gated_held', 'D_spam_benign_s1_gated_held_a',
                        'D_spam_benign_s1_gated_held_b')


class Finding1PartCBlackoutTests(unittest.TestCase):
    """MED: Part C's soak child checks the whole Part C span, not the soak alone, against 02:00-02:35."""

    def run_child(self, parts, hour, minute):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / 'soak'
            moment = r1.datetime(2026, 11, 15, hour, minute, tzinfo=r1.LOCAL_ZONE)
            with patch.object(smoke.reg, 'verify_r1_executed_sources'), \
                    patch.object(smoke.r1, 'executed_commit', return_value='0' * 40), \
                    patch.object(smoke.r1, '_now_local', lambda: moment), \
                    patch.object(smoke.r1, 'runtime_argv_from_inputs', return_value=['runtime']), \
                    patch.object(smoke.r1, '_invoke', side_effect=RuntimeError('reached the soak')), \
                    patch.object(smoke.r1, '_run', side_effect=RuntimeError('reached the soak')):
                smoke.soak_child(out, Path(directory) / 'inputs.json', parts=parts)

    def test_a_0129_start_refuses_for_part_c_and_not_for_the_soak_alone(self):
        # The soak alone ends at 01:59, before the window: it starts (and reaches the runtime here).
        with self.assertRaisesRegex(RuntimeError, 'reached the soak'):
            self.run_child('AB', 1, 29)
        # Part C's span (soak + r1_part_c_cap_s) runs through 02:00-02:35: refused before the soak.
        with self.assertRaisesRegex(ValueError, 'OS batch window'):
            self.run_child('C', 1, 29)
        # Far from the window, Part C starts.
        with self.assertRaisesRegex(RuntimeError, 'reached the soak'):
            self.run_child('C', 12, 0)

    def test_the_runner_passes_the_parts_to_the_soak_child(self):
        argv = smoke.part_argv(SimpleNamespace(output=Path('/out'), parts='C'), 'soak')
        self.assertEqual(argv[argv.index('--parts') + 1], 'C')


class Finding2DeskStaleStampTests(unittest.TestCase):
    """MED: a stale-stamped Nominal is not "Nominal throughout" (RL-149 section 1.6 item 1)."""

    def test_a_state_read_30_s_after_its_sample_is_unobserved_and_goes_to_the_lead(self):
        start = {'s_fast': 'TV0h', 's_slow': 'TV1h'}
        gate = {'kind': 'G0', 'turn': 0, 'outcome': 'timeout', 'start_ns': 0, 'end_ns': 1200 * NS,
                'duration_s': 1200, 'reference': {'slow_c': 60.0}}
        readings = [{'kind': 'reading', 'started': {'monotonic_ns': t * NS},
                     'values': {'sensors': {'TV0h': 60.9, 'TV1h': 60.9}, 'errors': {},
                                'status': {'os_level': 0, 'pm_state': 'Nominal',
                                           'pm_observed_ns': t * NS - 30 * NS}}} for t in range(0, 1201)]
        precool = {'phase': 'planning_turn_R_plus_2C.precool', 'released': True, 'last_curve_c': 59.0}
        with contextlib.redirect_stderr(io.StringIO()):
            row = desk.analyse_gate('planning_turn_R_plus_2C', gate, start, readings, 1.0, 'test', precool)
        self.assertEqual(row['stale_power_state_samples'], row['samples'])
        self.assertEqual(row['status_unobserved_samples'], row['samples'])
        self.assertFalse(row['nominal_throughout'])
        self.assertEqual(row['classification'], 'to-research-lead')


class Finding3TurnOpportunityCrossCheckTests(unittest.TestCase):
    """LOW: RL-152 section 1.2's fourth condition (RL-156 section 1): not_applicable also needs the row to show no
    cut, i.e. x7 False, g1_timeouts the integer 0 and g0_outcome released; otherwise the run fails."""

    def record(self, **bank):
        _inputs, slots = ready_inputs()
        slots['budget_fit_inputs']['turn_cap_tokens'] = 4096
        for row in slots['deadman_budget']:
            if row['run'] == BANK:
                row.update(turn_decode_counts=[3000, 4096], turn_completed=[True, False], decode_tokens=7096,
                           admitted_turns=2, turn_counts_source_sha256='c' * 64, g1_timeouts=0, x7=False,
                           g0_outcome='released',
                           duty_bar={'pass': True, 'verdict': 'pass', 'stop': {'own_stop': True}})
                row.update(bank)
            else:
                row.update(turn_decode_counts=[100, 100, 100], turn_completed=[True] * 3, decode_tokens=300,
                           admitted_turns=3, turn_counts_source_sha256='c' * 64)
        return slots

    def test_a_cut_flag_on_the_row_fails_the_run(self):
        self.assertEqual(kit.turn_opportunity(self.record(), 6144)['status'], 'pass')
        for name, change in (('g1 timeout', {'g1_timeouts': 1}), ('x7', {'x7': True}),
                             ('g0 not released', {'g0_outcome': 'timeout'}), ('g1_timeouts missing', {'g1_timeouts': None})):
            with self.subTest(name):
                result = kit.turn_opportunity(self.record(**change), 6144)
                self.assertEqual({r['run']: r['status'] for r in result['runs']}[BANK], 'fail')
                self.assertEqual(result['status'], 'fail')


class Finding4AliasPairByNameTests(unittest.TestCase):
    """LOW: the ruled alias pair is (TV0h, TV1h) by name, in the driver and in the kit's copy; RL-145 section 3's
    lexical clause is not a condition of the bar (RL-156 section 2)."""

    @staticmethod
    def classification(fast, slow, groups):
        return {'s_fast': fast, 's_slow': slow, 'alias_groups': groups,
                'night_confirmation': {'ok': True, 'second_key_rule': 'RL-145', 's_fast': fast, 's_slow': slow}}

    def test_another_rule_shaped_pair_and_the_swapped_pair_are_refused(self):
        self.assertFalse(r1.ruled_alias_pair(self.classification('Tp01', 'Tp05', [['Tp01', 'Tp05']])))
        self.assertFalse(r1.ruled_alias_pair(self.classification('TV1h', 'TV0h', [['TV0h', 'TV1h']])))
        self.assertTrue(r1.ruled_alias_pair(self.classification('TV0h', 'TV1h', [['TV0h', 'TV1h']])))

    def test_a_third_alias_sorting_between_does_not_refuse_the_ruled_pair(self):
        # The seat's second case. RL-156 section 2: the lexical clause leaves the bar; the pair by name stays.
        self.assertTrue(r1.ruled_alias_pair(self.classification('TV0h', 'TV1h', [['TV0h', 'TV0x', 'TV1h']])))
        self.assertTrue(r1.ruled_alias_pair(self.classification('TV0h', 'TV1h', [['TV0h', 'TV1h', 'TVh0']])))

    def test_the_kit_copy_names_the_same_pair(self):
        self.assertEqual(kit.RULED_ALIAS_PAIR, r1.RULED_ALIAS_PAIR)
        self.assertEqual(r1.RULED_ALIAS_PAIR, ('TV0h', 'TV1h'))
        for fast, slow, groups, expected in (('Tp01', 'Tp05', [['Tp01', 'Tp05']], False),
                                             ('TV1h', 'TV0h', [['TV0h', 'TV1h']], False),
                                             ('TV0h', 'TV1h', [['TV0h', 'TV0x', 'TV1h']], True),
                                             ('TV0h', 'TV1h', [['TV0h', 'TV1h']], True)):
            with self.subTest(pair=(fast, slow), groups=groups):
                c = self.classification(fast, slow, groups)
                self.assertIs(kit.ruled_alias_pair({'s_fast': fast, 's_slow': slow}, groups,
                                                   c['night_confirmation']), expected)


class Finding5TypicalCaseChecksTests(unittest.TestCase):
    """LOW: refuse H > 0; reconcile the G1 waits with phases_s.G1; the timed-out term is max(cap, largest)."""

    def record(self):
        from tests.align.test_rl149_typical_case import rl149_case
        return rl149_case()

    def test_hold_seconds_are_refused(self):
        _inputs, slots = self.record()
        slots['deadman_budget'][0]['phases_s']['H'] = 80.0
        with self.assertRaisesRegex(ValueError, 'hold'):
            kit.typical_case_fit(slots, 983.10, 300.0)

    def test_g1_waits_must_add_up_to_the_g1_phase(self):
        _inputs, slots = self.record()
        for row in slots['deadman_budget']:
            row['gate_waits_s'] = {'G1': [10.0, 10.0]}
            row['phases_s']['G1'] = 500.0
        with self.assertRaisesRegex(ValueError, 'G1 waits'):
            kit.typical_case_fit(slots, 983.10, 300.0)

    def test_a_timed_out_g1_term_is_at_least_the_largest_recorded_wait(self):
        _inputs, slots = self.record()
        row = next(r for r in slots['deadman_budget'] if r['run'] == SPAM_B)
        row['gate_waits_s'] = {'G1': [70.0, 300.8]}
        row['phases_s']['G1'] = 370.8
        row['g1_timeouts'] = 1
        fit = kit.typical_case_fit(slots, 983.10, 300.0)
        self.assertEqual(fit['G1_max_s'], 300.8)


class Finding7PartCXgFlagsTests(unittest.TestCase):
    """LOW: X_G's X7 comes from the runtime's flags only when they are a list."""

    def test_missing_flags_keep_the_bundle_x7(self):
        from scripts import align_r1_followup_kit as fkit
        from tests.align.test_rl145_part_c import STEP, bank

        def invoke(runtime, kind, output, **kw):
            base = {'bundle': kind + '-bundle'}
            if kind == 'step-d':
                return {**base, 'g0_outcome': 'released', 'g0_wait_s': 212.0,
                        'slots': {'N_chunk': 4096, 'B_D': 6144}, 'slot_detail': {}}
            if kind == 'd-bank-benign-s1':
                return {**base, 'x7': False, 'deadman': {'T_dead_s': 1000.0}}
            return base                              # x-g: no episode_flags

        def facts(bundle, *, role):
            return bank() if role == 'd-bank' else {'x7': True, 'intervals': []}
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(ValueError, 'Part C failed'):
                fkit.smoke_part_c(Path(tmp) / 'c', ['runtime'], SimpleNamespace(), soak_reference='s',
                                  invoke=invoke, facts=facts, step_facts=lambda *_: dict(STEP),
                                  prints=lambda bundle: {'turns': []})
            table = json.loads((Path(tmp) / 'c' / 'smoke_part_c.json').read_text())
        self.assertIs(table['evaluation']['lines']['x_g']['x7'], True)
        self.assertFalse(table['evaluation']['lines']['x_g']['pass'])


class Finding8PartCLateFirstReadingTests(unittest.TestCase):
    """LOW: a first reading more than 2 s after the turn start is 'no journal row for sample'."""

    def test_a_reading_60_s_late_is_not_the_start_state(self):
        rows = [{'schema': 'joulewise.align_thermal.v1', 'module': 'temperature', 'kind': 'reading',
                 'started': {'monotonic_ns': t, 'monotonic_raw_ns': t, 'wall_ns': t},
                 'finished': {'monotonic_ns': t + 1, 'monotonic_raw_ns': t + 1, 'wall_ns': t + 1},
                 'values': {'sensors': {'TV0h': 35.0, 'TV1h': 35.0}, 'errors': {},
                            'status': {'monotonic_ns': t, 'os_level': 0, 'pm_state': 'Nominal',
                                       'pm_observed_ns': t}}}
                for t in (10 * NS, 11 * NS, 12 * NS, 80 * NS)]   # a journal gap from 12 s to 80 s
        turns = [SimpleNamespace(index=0, start_ns=13 * NS, end_ns=90 * NS, decode_tokens=10, prefill_tokens=5)]
        ep = SimpleNamespace(hardware={'thermal': {'intervals': []}, 'token_budget': {'deadman_s': 983.1}},
                             turns=turns, flags=[])
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'outputs').mkdir()
            (Path(tmp) / 'outputs/align_thermal.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
            with patch('joulewise.align.apple.workload.read_episode_bundle', return_value=ep):
                facts = pc.facts_from_bundle(tmp, role='d-bank')
        self.assertIsNone(facts['turns'][0]['first_reading_after_start'])
        line = pc.d_bank_start_state({**facts, 'intervals': []})
        self.assertIn('first reading after turn 0 start: no journal row for sample', line['reasons'])


class Finding9BudgetProcedureTests(unittest.TestCase):
    """LOW: decide() follows RL-148 section 2: the typical case, no R10-2 receipt route and no 4-bit route."""

    def test_a_record_the_worst_case_cannot_fit_takes_the_typical_case_route(self):
        from tests.align.test_rl149_typical_case import rl149_case
        _inputs, slots = rl149_case()
        slots['slots']['I_D'] = 400.0
        slots['max_r1_tail_s'] = 20.0
        for row in slots['deadman_budget']:
            row['phases_s']['tail'] = 20.0
        self.assertIsNone(kit.max_fitting_b_d(slots, kit.l1_t_dead(400.0, 20.0)))      # 1(f) fits nowhere
        decision = proc.decide(slots, 12)
        self.assertNotIn('R10-2', decision['step'])
        self.assertEqual(decision['step'], 'TYPICAL-CASE')
        self.assertNotIn('receipt_draft', decision)              # RL-156 section 3.1: decide drafts nothing
        self.assertTrue(decision['typical_case']['fits'])
        self.assertEqual(decision['set_inputs']['R1.B_D'], slots['slots']['B_D'])


class Finding10LooseComparisonTests(unittest.TestCase):
    """INFO: os_levels [False] is not [0]; admitted_turns 2.0 is not an int."""

    def test_os_levels_false_is_refused(self):
        names = ['planning_turn_R_plus_4C']
        _inputs, slots = planning_slots(names)
        with self.assertRaisesRegex(ValueError, 'OS level above 0'):
            kit.planning_released_segments(slots, release_for(slots, names, os_levels=[False]))

    def test_admitted_turns_must_be_an_int(self):
        _inputs, slots = ready_inputs()
        row = slots['deadman_budget'][0]
        row['admitted_turns'] = float(row['admitted_turns'])
        self.assertEqual(kit.turn_opportunity(slots, slots['slots']['B_D'])['status'], 'inconclusive')


if __name__ == '__main__':
    unittest.main()
