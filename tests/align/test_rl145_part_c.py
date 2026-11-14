"""RL-145 addendum section 6 / row 7: Part C's evaluator, kit sequence and launcher wiring.

Synthetic facts and fake runtime invocations only; no host, journal or study data.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt
from scripts import align_r1_followup_kit as kit, align_r1_part_c as pc, launch_align_r0 as launcher
from scripts import run_align_r1_smoke as smoke


def status(level=0, state='Nominal', age=0.5):
    return {'os_level': level, 'pm_state': state, 'pm_age_s': age}


def turn(index, decode, **extra):
    return {'index': index, 'decode_tokens': decode, 'first_reading_after_start': status(), **extra}


def interval(kind, turn_index=0, *, duration=20.0, outcome='released', token_count=None, release_status='ok'):
    return {'kind': kind, 'turn': turn_index, 'token_count': token_count, 'outcome': outcome,
            'duration_s': duration, 'release_status': status() if release_status == 'ok' else release_status}


def bank(**override):
    """Three admitted turns, G0 and two G1 releases clean, no holds (N_chunk 4,096)."""
    value = {'turns': [turn(0, 1500), turn(1, 3000), turn(2, 4096)],
             'intervals': [interval('G0', 0, duration=100.0), interval('G1', 1, duration=90.0),
                           interval('G1', 2, duration=120.0)],
             't_dead_s': 1000.0, 'x7': False}
    value.update(override)
    return value


STEP = {'g0_outcome': 'released', 'g0_wait_s': 212.0, 'release': {'fast_c': 35.4, 'slow_c': 35.4},
        'reference': {'fast_c': 35.0, 'slow_c': 35.0}, 'slope_c_per_min': 0.05}
XG = {'x7': False, 'intervals': [interval('G0'), interval('G1', 1)]}


def run(step=STEP, d_bank=None, n_chunk=4096, x_g=XG, **kw):
    return pc.evaluate(step_d=step, d_bank=bank() if d_bank is None else d_bank, n_chunk=n_chunk, x_g=x_g, **kw)


class ExpectedHoldsTests(unittest.TestCase):
    def test_one_hold_at_each_multiple_the_turn_reaches_before_finishing_and_below_4096(self):
        self.assertEqual(pc.expected_hold_tokens(4096, 4096), [])
        self.assertEqual(pc.expected_hold_tokens(4096, 2048), [2048])
        self.assertEqual(pc.expected_hold_tokens(2048, 2048), [])         # finishes at the multiple: no hold
        self.assertEqual(pc.expected_hold_tokens(2049, 2048), [2048])
        self.assertEqual(pc.expected_hold_tokens(4096, 1024), [1024, 2048, 3072])
        self.assertEqual(pc.expected_hold_tokens(300, 256), [256])
        self.assertEqual(pc.expected_hold_tokens(255, 256), [])
        self.assertEqual(pc.expected_hold_tokens(9000, 1024), [1024, 2048, 3072])   # nothing at or above the cap
        with self.assertRaises(ValueError):
            pc.expected_hold_tokens(100, 0)


class EvaluatorPassTests(unittest.TestCase):
    def test_a_clean_run_passes_and_the_printed_rows_do_not_decide(self):
        result = run(printed=[{'turn': 0, 'first_off': {'s_after_first_token': 60.5}}])
        self.assertEqual((result['pass'], result['verdict']), (True, 'pass'))
        self.assertTrue(all(v is None or v['pass'] for v in result['lines'].values()))
        self.assertEqual(result['printed_not_judged']['turns'][0]['turn'], 0)
        self.assertIn('0.83 and 0.93', result['printed_not_judged']['predicted'])
        self.assertFalse(result['slots_entered'])
        both = run(printed={'turns': [{'turn': 0}], 'desk_verdict': {'member_excluded': True}, 'tv1h_trigger': {'fires': True}})
        self.assertTrue(both['pass'])      # the desk verdict is printed beside the result and never decides
        self.assertTrue(both['printed_not_judged']['desk_verdict']['member_excluded'])
        # A bad-looking print changes nothing.
        bad = run(printed=[{'turn': 0, 'first_off': {'s_after_first_token': 1.0}, 'clock_ratio_last_512': 0.1}])
        self.assertTrue(bad['pass'])
        json.dumps(result)

    def test_holds_match_the_configured_n_chunk_at_2048(self):
        holds = [interval('H', 1, token_count=2048, duration=20.0), interval('H', 2, token_count=2048, duration=20.0)]
        d = bank(intervals=bank()['intervals'] + holds)
        self.assertTrue(run(d_bank=d, n_chunk=2048)['pass'])
        # The same two H records at N_chunk 4,096 are a defect.
        self.assertEqual(run(d_bank=d, n_chunk=4096)['verdict'], 'other_failure')

    def test_x_g_not_run_is_logged_and_does_not_fail(self):
        result = run(x_g=None, x_g_not_run_reason='launcher cannot run it')
        self.assertTrue(result['pass'])
        self.assertIsNone(result['lines']['x_g'])
        self.assertEqual(result['log'], ['X_G was not run: launcher cannot run it'])


class EvaluatorFailureTests(unittest.TestCase):
    def check(self, result, line, key, verdict):
        self.assertFalse(result['pass'])
        self.assertEqual(result['verdict'], verdict)
        self.assertTrue(result['disposition'])
        node = result['lines'][line]
        if key:
            self.assertFalse(node['checks'][key]['pass'], node)

    def test_fewer_than_three_admitted_turns(self):
        d = bank(turns=[turn(0, 1500), turn(1, 3000)])
        self.check(run(d_bank=d), 'd_bank_mechanics', 'admitted_turns', 'other_failure')

    def test_gate_time_over_forty_percent_of_t_dead_is_the_gate_time_branch(self):
        d = bank()
        d['intervals'][0]['duration_s'] = 190.0          # 190 + 90 + 120 = 400 = 0.40 x 1000: at the limit holds (<=)
        self.assertTrue(run(d_bank=d)['pass'])
        d['intervals'][0]['duration_s'] = 190.001
        result = run(d_bank=d)
        self.check(result, 'd_bank_mechanics', 'gate_time', 'mechanics_gate_time_failed')
        self.assertNotIn('fallback of', result['disposition'].replace('withdrew the fallback', ''))
        self.assertIn('research lead', result['disposition'])
        # Holds count toward the same total.
        d = bank(intervals=bank()['intervals'] + [interval('H', 1, token_count=None, duration=300.0)])
        self.assertFalse(run(d_bank=d)['lines']['d_bank_mechanics']['checks']['gate_time']['pass'])

    def test_x7_and_g1_timeout(self):
        self.check(run(d_bank=bank(x7=True)), 'd_bank_mechanics', 'no_x7', 'other_failure')
        d = bank()
        d['intervals'][1]['outcome'] = 'timeout'
        self.check(run(d_bank=d), 'd_bank_mechanics', 'no_g1_timeout', 'other_failure')
        # A G0 timeout is not a G1 timeout; it still leaves no G0 release sample.
        d = bank()
        d['intervals'][0]['outcome'] = 'timeout'
        result = run(d_bank=d)
        self.assertTrue(result['lines']['d_bank_mechanics']['checks']['no_g1_timeout']['pass'])
        self.assertFalse(result['lines']['d_bank_start_state']['pass'])

    def test_an_h_record_the_configuration_does_not_imply_or_a_missing_one(self):
        d = bank(intervals=bank()['intervals'] + [interval('H', 1, token_count=2048)])
        self.check(run(d_bank=d, n_chunk=4096), 'd_bank_mechanics', 'h_records', 'other_failure')
        # A hold the configuration implies but that is absent (N_chunk 2048, turn 1 reaches 3,000 tokens).
        self.check(run(d_bank=bank(), n_chunk=2048), 'd_bank_mechanics', 'h_records', 'other_failure')
        # An H record on a turn that is not in the turn list.
        d = bank(intervals=bank()['intervals'] + [interval('H', 9, token_count=4096)])
        self.check(run(d_bank=d), 'd_bank_mechanics', 'h_records', 'other_failure')
        # Duplicate H at one multiple is not "exactly one".
        d = bank(intervals=bank()['intervals'] + [interval('H', 1, token_count=2048), interval('H', 1, token_count=2048)])
        self.check(run(d_bank=d, n_chunk=2048), 'd_bank_mechanics', 'h_records', 'other_failure')

    def test_start_state_branches_each_fail_alone(self):
        def broken(mutate):
            d = bank()
            mutate(d)
            return run(d_bank=d)
        cases = {
            'G0 release level 1': lambda d: d['intervals'][0].update(release_status=status(1)),
            'G1 release not Nominal': lambda d: d['intervals'][1].update(release_status=status(0, 'Fair')),
            'G1 release status missing': lambda d: d['intervals'][2].update(release_status=None),
            'turn start level 2': lambda d: d['turns'][1].update(first_reading_after_start=status(2)),
            'turn start not Nominal': lambda d: d['turns'][2].update(first_reading_after_start=status(0, 'Heavy')),
            'turn start unread': lambda d: d['turns'][0].update(first_reading_after_start=None),
            'G0 stamp 2.5 s old': lambda d: d['intervals'][0].update(release_status=status(age=2.5)),
            'G1 stamp age missing': lambda d: d['intervals'][1].update(release_status=status(age=None)),
            'turn start stamp old': lambda d: d['turns'][2].update(first_reading_after_start=status(age=9.0)),
        }
        for name, mutate in cases.items():
            with self.subTest(name):
                result = broken(mutate)
                self.assertEqual(result['verdict'], 'start_state_failed')
                self.assertFalse(result['lines']['d_bank_start_state']['pass'])
                self.assertIn('research lead', result['disposition'])
                self.assertIn('Nothing is re-run', result['disposition'])
        # The failing sample is named in the table.
        bad = [s for s in broken(cases['G1 release not Nominal'])['lines']['d_bank_start_state']['samples'] if not s['ok']]
        self.assertEqual([s['at'] for s in bad], ['G1 release (turn 1)'])

    def test_start_state_outranks_a_mechanics_failure(self):
        d = bank(x7=True)
        d['turns'][0]['first_reading_after_start'] = status(1)
        self.assertEqual(run(d_bank=d)['verdict'], 'start_state_failed')

    def test_step_d_lines(self):
        cases = {
            'G0 not released': {'g0_outcome': 'timeout'},
            'G0 after 1200 s': {'g0_wait_s': 1200.5},
            'fast 1.2 over': {'release': {'fast_c': 36.2, 'slow_c': 35.4}},
            'slow 1.2 over': {'release': {'fast_c': 35.4, 'slow_c': 36.2}},
            'slope +0.3': {'slope_c_per_min': 0.3},
            'slope -0.3': {'slope_c_per_min': -0.3},
            'slope missing': {'slope_c_per_min': None},
            'reference missing': {'reference': None},
        }
        for name, change in cases.items():
            with self.subTest(name):
                result = run(step={**STEP, **change})
                self.assertFalse(result['lines']['step_d']['pass'])
                self.assertEqual(result['verdict'], 'other_failure')
        for ok in ({'g0_wait_s': 1200.0}, {'slope_c_per_min': -0.2}, {'release': {'fast_c': 36.0, 'slow_c': 34.0}}):
            with self.subTest(ok=ok):
                self.assertTrue(run(step={**STEP, **ok})['pass'])

    def test_x_g_line(self):
        self.check_x(dict(XG, x7=True))
        self.check_x({'x7': False, 'intervals': [interval('G1', 3, outcome='timeout')]})

    def check_x(self, x_g):
        result = run(x_g=x_g)
        self.assertFalse(result['pass'])
        self.assertFalse(result['lines']['x_g']['pass'])
        self.assertEqual(result['verdict'], 'other_failure')

    def test_a_missing_d_bank_is_not_judged_as_a_pass(self):
        result = pc.evaluate(step_d=STEP, d_bank=None, n_chunk=4096, x_g=None)
        self.assertFalse(result['pass'])
        self.assertTrue(any('D_bank did not run' in line for line in result['log']))


class OwnStopTurnCheckTests(unittest.TestCase):
    """RL-149 sections 1.2 item 5 and 1.5: a member that returned by its own stop before a third admission is
    judged on its other checks; its turn check prints not_applicable. The R1 driver's own rule decides."""

    def two_turns(self, **override):
        d = bank(turns=[turn(0, 2200), turn(1, 4096)],
                 intervals=[interval('G0', 0, duration=110.0), interval('G1', 1, duration=99.8)],
                 episode_flags=['ended_in_unclosed_reasoning'])
        d.update(override)
        return d

    def test_an_own_stop_at_two_turns_is_not_applicable_and_the_run_passes(self):
        result = run(d_bank=self.two_turns())
        self.assertEqual((result['pass'], result['verdict']), (True, 'pass'))
        check = result['lines']['d_bank_mechanics']['checks']['admitted_turns']
        self.assertEqual(check['status'], 'not_applicable: episode returned at turn 1')
        self.assertIs(check['judged'], False)
        self.assertEqual(check['value'], 2)
        self.assertIn('RL-149', result['authority'])
        json.dumps(result)

    def test_a_cut_or_unreadable_stop_keeps_the_turn_check_judged(self):
        cases = {
            'deadman': self.two_turns(x7=True, episode_flags=['episode.deadman:1']),
            'G1 timeout in the flags': self.two_turns(episode_flags=['thermal.gate_timeout:1']),
            'decode budget': self.two_turns(episode_flags=['episode.decode_budget:2']),
            'flags not recorded': self.two_turns(episode_flags=None),
        }
        for name, d in cases.items():
            with self.subTest(name):
                result = run(d_bank=d)
                check = result['lines']['d_bank_mechanics']['checks']['admitted_turns']
                self.assertIs(check['pass'], False)
                self.assertFalse(result['pass'])
        # A G1 timeout that only the intervals show is still a gate timeout.
        d = self.two_turns()
        d['intervals'][1]['outcome'] = 'timeout'
        check = run(d_bank=d)['lines']['d_bank_mechanics']['checks']
        self.assertIs(check['admitted_turns']['pass'], False)
        self.assertFalse(check['no_g1_timeout']['pass'])

    def test_a_not_applicable_turn_check_does_not_hide_the_gate_time_branch(self):
        d = self.two_turns()
        d['intervals'][0]['duration_s'] = 500.0
        self.assertEqual(run(d_bank=d)['verdict'], 'mechanics_gate_time_failed')

    def test_three_turns_need_no_stop_reading(self):
        self.assertTrue(run(d_bank=bank(episode_flags=None))['pass'])


class SidecarJournalTests(unittest.TestCase):
    """RL-149 section 1.2 items 1 to 4: the evaluator reads a journal written by the runtime's own Sidecar
    writer (``reading`` rows, stamps nested in ``started``/``finished``, the status in ``values.status`` and
    read about 15 ms after the SMC read bracket starts). Synthetic sensors and clocks; no study data."""

    def setUp(self):
        from joulewise.align.apple import thermal
        from joulewise.hazards import base
        from tests.hazards.fakes import FakeClocks
        from tests.hazards.test_temperature import FakeSensors, POLICY
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.bundle = Path(self.temp.name) / 'bundle'
        self.clocks = FakeClocks(read_cost_ns=0)
        self.state = {'os_level': 0, 'pm_state': 'Nominal', 'age_s': 0.0}

        def status_reader():
            self.clocks.advance(0.015)                       # parsed just after the SMC read bracket
            now = self.clocks.monotonic_ns()
            return {'monotonic_ns': now, 'os_level': self.state['os_level'], 'pm_state': self.state['pm_state'],
                    'pm_observed_ns': now - round(self.state['age_s'] * 1e9)}
        self.sidecar = thermal.Sidecar(self.bundle / 'outputs', POLICY, reader=FakeSensors(),
                                       ctx=base.Context(clocks=self.clocks), status_reader=status_reader)
        self.sidecar.start(background=False)
        self.stamps = []

    def tick(self, n=1):
        for _ in range(n):
            self.clocks.advance(1.0)
            self.stamps.append(self.sidecar.tick()['started']['monotonic_ns'])
        return self.stamps[-1]

    def facts(self, *, release_ns=None, flags=('ended_in_unclosed_reasoning',)):
        """Two gates and two turns placed on the journal's own stamps (G0 release at tick 2, turn 0 after it;
        G1 release at tick 6, turn 1 after it), then ``facts_from_bundle`` on the written bundle."""
        g0 = self.tick(2)
        t0 = self.clocks.monotonic_ns() + 100_000_000
        self.tick(3)
        g1 = self.tick()
        t1 = self.clocks.monotonic_ns() + 100_000_000
        self.tick(3)
        self.sidecar.event('align_thermal_gate', {'gate_kind': 'G1', 'state': 'release', 'turn': 1})
        self.sidecar.stop()
        intervals = [{'kind': 'G0', 'turn': 0, 'outcome': 'released', 'duration_s': 110.0,
                      'exit_sample_ns': g0 if release_ns is None else release_ns},
                     {'kind': 'G1', 'turn': 1, 'outcome': 'released', 'duration_s': 99.8, 'exit_sample_ns': g1}]
        turns = [SimpleNamespace(index=0, start_ns=t0, end_ns=t0 + 2, decode_tokens=2200, prefill_tokens=11211),
                 SimpleNamespace(index=1, start_ns=t1, end_ns=t1 + 2, decode_tokens=4096, prefill_tokens=40)]
        ep = SimpleNamespace(hardware={'thermal': {'intervals': intervals}, 'token_budget': {'deadman_s': 983.1}},
                             turns=turns, flags=list(flags))
        with patch('joulewise.align.apple.workload.read_episode_bundle', return_value=ep):
            return pc.facts_from_bundle(self.bundle, role='d-bank')

    def test_the_sidecar_journal_is_read_and_a_fresh_in_state_member_passes(self):
        facts = self.facts()
        raw = [json.loads(x) for x in (self.bundle / 'outputs/align_thermal.jsonl').read_text().splitlines()]
        self.assertEqual({r['kind'] for r in raw}, {'session_start', 'reading', 'align_thermal_gate', 'session_end'})
        self.assertNotIn('sample', {r['kind'] for r in raw})
        self.assertEqual(len(pc._journal(self.bundle)), len(self.stamps))   # the legacy reader found 0 rows
        line = pc.d_bank_start_state(facts)
        self.assertTrue(line['pass'], line)
        self.assertEqual(line['reasons'], [])
        self.assertEqual(len(line['samples']), 4)
        for sample in line['samples']:
            self.assertEqual((sample['os_level'], sample['pm_state'], sample['stamp_fresh']), (0, 'Nominal', True))
            self.assertLess(sample['pm_age_s'], 0)           # the stamp follows the sample's own stamp
            self.assertGreater(sample['pm_age_s'], -0.1)
        result = pc.evaluate(step_d=STEP, d_bank=facts, n_chunk=4096, x_g=None, x_g_not_run_reason='not in this test')
        self.assertEqual((result['pass'], result['verdict']), (True, 'pass'), result['lines'])
        self.assertEqual(result['lines']['d_bank_mechanics']['checks']['admitted_turns']['status'],
                         'not_applicable: episode returned at turn 1')

    def test_a_sample_with_no_journal_row_is_a_reason_never_a_silent_null(self):
        line = pc.d_bank_start_state(self.facts(release_ns=123))
        self.assertFalse(line['pass'])
        self.assertIn('G0 release: no journal row for sample', line['reasons'])
        self.assertEqual(len(line['reasons']), 1)

    def test_a_stamp_over_two_seconds_old_is_not_recorded(self):
        self.state['age_s'] = 2.1
        line = pc.d_bank_start_state(self.facts())
        self.assertFalse(line['pass'])
        self.assertEqual(len(line['reasons']), 4)
        self.assertTrue(all('not recorded' in r for r in line['reasons']))
        self.assertTrue(pc.stamp_fresh(2.0) and pc.stamp_fresh(-0.02))
        self.assertFalse(pc.stamp_fresh(2.0001) or pc.stamp_fresh(None) or pc.stamp_fresh(True))

    def test_an_off_state_reading_fails_with_its_values(self):
        self.state.update(os_level=1, pm_state='Moderate')
        line = pc.d_bank_start_state(self.facts())
        self.assertFalse(line['pass'])
        self.assertIn("level 1, state 'Moderate'", line['reasons'][0])


class KitSequenceTests(unittest.TestCase):
    """smoke --part C: the runtime kinds in order, no slots entered, a failure raises after the table."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tmp = Path(self.temp.name)
        self.calls = []
        self.x_g_fails = False

    def invoke(self, runtime, kind, output, **kw):
        self.calls.append(kind)
        if kind == 'x-g' and self.x_g_fails:
            raise kit.r1.Refusal('runtime.x-g: exit 2: synthetic')
        base = {'bundle': kind + '-bundle'}
        if kind == 'step-d':
            return {**base, 'g0_outcome': 'released', 'g0_wait_s': 212.0,
                    'slots': {'N_chunk': 4096, 'B_D': 6144}, 'slot_detail': {'N_chunk_formula': 1280}}
        if kind == 'd-bank-benign-s1':
            return {**base, 'x7': False, 'deadman': {'T_dead_s': 1000.0}}
        if kind == 'x-g':
            return {**base, 'episode_flags': []}
        return base

    def facts(self, bundle, *, role):
        return {'d-bank': bank(), 'x-g': deepcopy(XG)}[role]

    def run_c(self, *, bank_facts=None, step_facts=None):
        facts = (lambda bundle, *, role: bank_facts if role == 'd-bank' and bank_facts else self.facts(bundle, role=role))
        config = SimpleNamespace()
        return kit.smoke_part_c(self.tmp / 'c', ['runtime'], config, soak_reference='soak.json', invoke=self.invoke,
                                facts=facts, step_facts=lambda *_: dict(step_facts or STEP),
                                prints=lambda bundle: {'turns': [{'turn': 0, 'token_basis': 'uniform_estimate'}],
                                                     'desk_verdict': {'exclusion_reasons': ['r']}})

    def test_order_and_a_passing_table(self):
        result = self.run_c()
        self.assertEqual(self.calls, ['capture-predecessor-30b', 'step-d', 'd-bank-benign-s1', 'x-g'])
        table = json.loads((self.tmp / 'c' / 'smoke_part_c.json').read_text())
        self.assertEqual(table, json.loads((self.tmp / 'c' / 'smoke.json').read_text()))
        self.assertTrue(table['evaluation']['pass'])
        self.assertIs(table['slots_entered'], False)
        self.assertEqual(table['n_chunk_formula_recorded'], 1280)
        self.assertEqual(table['evaluation']['n_chunk_configured'], 4096)
        self.assertEqual(table['evaluation']['printed_not_judged']['turns'][0]['token_basis'], 'uniform_estimate')
        self.assertEqual(table['evaluation']['printed_not_judged']['desk_verdict']['exclusion_reasons'], ['r'])
        self.assertFalse((self.tmp / 'c' / 'r1_slots.json').exists())
        self.assertIs(result['evaluation']['pass'], True)

    def test_x_g_that_cannot_run_is_left_out_with_a_log_line(self):
        self.x_g_fails = True
        result = self.run_c()
        evaluation = result['evaluation']
        self.assertTrue(evaluation['pass'])
        self.assertTrue(any(line.startswith('X_G was not run: Refusal') for line in evaluation['log']))

    def test_a_failed_test_writes_the_table_then_raises(self):
        bad = bank()
        bad['turns'][1]['first_reading_after_start'] = status(1)
        with self.assertRaisesRegex(ValueError, 'start_state_failed'):
            self.run_c(bank_facts=bad)
        table = json.loads((self.tmp / 'c' / 'smoke_part_c.json').read_text())
        self.assertEqual(table['evaluation']['verdict'], 'start_state_failed')

    def test_no_step_d_slots_stops_before_the_gated_member(self):
        original = self.invoke
        self.invoke = lambda runtime, kind, output, **kw: ({'bundle': 'b', 'g0_outcome': 'timeout'}
                                                           if kind == 'step-d' else original(runtime, kind, output, **kw))
        with self.assertRaisesRegex(ValueError, 'no slots'):
            self.run_c()
        self.assertNotIn('d-bank-benign-s1', self.calls)
        self.assertIn('error', json.loads((self.tmp / 'c' / 'smoke_part_c.json').read_text()))

    def test_smoke_dispatches_part_c_after_the_bound_checks(self):
        with patch.object(kit, 'smoke_part_c', return_value={'ok': True}) as part_c, \
                patch.object(kit.reg, 'verify_r1_executed_sources'), \
                patch.object(kit.r1, 'executed_commit', return_value='x'), \
                patch.object(kit.r1, 'runtime_config_path', return_value=kit.ROOT / kit.r1.DEFAULT_RUNTIME_CONFIG):
            self.assertEqual(kit.smoke(self.tmp / 'd', 'C', ['runtime'], soak_reference='s'), {'ok': True})
        part_c.assert_called_once()
        self.assertEqual(kit.main.__module__, 'scripts.align_r1_followup_kit')


class LauncherWiringTests(unittest.TestCase):
    def test_part_c_cap_and_minimum_follow_the_part_b_span_and_member_caps(self):
        caps = launcher.r1_part_caps()
        self.assertEqual(launcher.r1_part_c_cap_s(), caps['B'] + 2 * (rt.MEMBER_CAP_S + 120))
        self.assertEqual(launcher.r1_part_caps(), {'A': 3120, 'B': 5720})      # A and B are unchanged
        minimum = launcher.r1_minimum_seconds('C', True)
        self.assertEqual(minimum, launcher.r1_part_c_cap_s() + launcher.r1_soak_cap_s()
                         + launcher.DISPLAY_SLEEP_DWELL_S + 2 * launcher.R1_CLEANUP_GRACE_S + 10)
        self.assertEqual(launcher.r1_minimum_seconds('AB', False),
                         caps['A'] + caps['B'] + launcher.DISPLAY_SLEEP_DWELL_S + 2 * launcher.R1_CLEANUP_GRACE_S + 10)

    def test_part_c_needs_a_fresh_soak(self):
        args = SimpleNamespace(parts='C', fresh_soak=False, runner_kind='r1-smoke', soak_reference=None,
                               deadline=time.time() + 20000, magistrate_pid=os.getpid(), output=Path('/nonexistent/x'),
                               checks=None)
        with self.assertRaisesRegex(ValueError, 'fresh soak'):
            launcher.launch(args)

    def test_runner_argv_and_cap_for_part_c(self):
        args = SimpleNamespace(output=Path('/out'), soak_reference=Path('/s.json'))
        argv = smoke.part_argv(args, 'C')
        self.assertEqual(argv[2:6], [str(smoke.ROOT / 'scripts/align_r1_followup_kit.py'), 'smoke', '--part', 'C'])
        with self.assertRaises(SystemExit):
            smoke.main(['--output', '/tmp/rl145-never', '--parts', 'C', '--soak-reference', '/s.json', '--deadline', '1e12'])


class RunnerPartCTests(unittest.TestCase):
    def test_runner_runs_only_part_c_and_records_it(self):
        from tests.align.test_r1_smoke_launcher import RunnerTests
        case = RunnerTests('test_order_and_receipt')
        case.setUp()
        self.addCleanup(case.doCleanups)
        case.args.parts = 'C'
        self.assertEqual(case.run_runner(), 0)
        self.assertEqual([e for e in case.events if e.startswith('part-')], ['part-C'])
        receipt = case.receipt()
        self.assertEqual((receipt['parts'], receipt['parts_requested'], receipt['rc']), ({'C': True}, 'C', 0))
        self.assertFalse(case.live)


if __name__ == '__main__':
    unittest.main()
