"""RL-145 addendum section 6 / row 7: Part C's evaluator, kit sequence and launcher wiring.

The W1 wiring and direct checks use synthetic facts and fake runtime invocations.
RL-215's frozen v4 suite supplies the complete native and archived controls and
the case matrix. The historical fixture remains at the suite's pinned commit.
"""
import contextlib
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple import r1_runtime as rt
from scripts import align_r1_followup_kit as kit, align_r1_part_c as pc, launch_align_r0 as launcher
from scripts import run_align_r1_smoke as smoke
from tests.test_part_c_evidence_ledger import MARKER, SoakAttempt, hashed, json_bytes
from tests.test_part_c_gate_evidence import (
    evaluation_inputs, member_record, oracle_that_passed, step_record, synthetic_episode,
    write_predecessor, write_receipt,
)


def status(level=0, state='Nominal', age=0.5):
    return {'os_level': level, 'pm_state': state, 'pm_age_s': age}


def turn(index, decode, **extra):
    return {'index': index, 'decode_tokens': decode, 'first_reading_after_start': status(), **extra}


def interval(kind, turn_index=0, *, duration=20.0, outcome='released', token_count=None, release_status='ok'):
    return {'kind': kind, 'turn': turn_index, 'token_count': token_count, 'outcome': outcome,
            'duration_s': duration, 'start_ns': 0, 'end_ns': round(duration * 1e9),
            'release_status': status() if release_status == 'ok' else release_status}


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
XG = {'x7': False, 'turns': [turn(0, 1500), turn(1, 3000)],
      'intervals': [interval('G0'), interval('G1', 1)]}


def run(step=STEP, d_bank=None, n_chunk=4096, x_g=XG, **kw):
    with tempfile.TemporaryDirectory() as tmp:
        inputs = evaluation_inputs(Path(tmp), step_d=step, d_bank=bank() if d_bank is None else d_bank,
                                   n_chunk=n_chunk, x_g=x_g)
        return pc._judge_observations(**inputs, **kw)


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
        result = run(x_g=None, x_g_not_run_reason=pc.RuntimeAdmissionRefusal('x-g', 'native exit 2'))
        self.assertTrue(result['pass'])
        self.assertIsNone(result['lines']['x_g'])
        self.assertEqual(result['log'], ['three-turn clause not evaluated: one D run',     # RL-152 section 1.4
                                         'X_G was not run: runtime.x-g: native exit 2'])


class EvaluatorFailureTests(unittest.TestCase):
    def check(self, result, line, key, verdict):
        self.assertFalse(result['pass'])
        self.assertEqual(result['verdict'], verdict)
        self.assertTrue(result['disposition'])
        node = result['lines'][line]
        if key:
            self.assertFalse(node['checks'][key]['pass'], node)

    def test_admitted_turns_cannot_pass_with_missing_duplicate_or_unreleased_g1(self):
        g0, g1, g2 = bank()['intervals']
        for intervals in ([g0], [g0, g1, g1, g2], [g0, g1, {**g2, 'turn': 8}],
                          [g0, g1, {**g2, 'outcome': 'unobserved'}]):
            with self.subTest(intervals=intervals):
                self.check(run(d_bank=bank(intervals=intervals)), 'd_bank_mechanics',
                           'g1_records', 'other_failure')

    def test_g1_wait_cannot_be_understated_in_the_duty_budget(self):
        d = bank()
        d['intervals'][1].update(duration_s=0, start_ns=0, end_ns=90_000_000_000)
        result = run(d_bank=d)
        self.check(result, 'd_bank_mechanics', 'gate_durations', 'other_failure')
        self.assertIsNone(result['lines']['d_bank_mechanics']['checks']['gate_time']['gates_plus_holds_s'])

    def test_fewer_than_three_admitted_turns(self):
        d = bank(turns=[turn(0, 1500), turn(1, 3000)], episode_flags=['episode.time_guard:2'])
        self.check(run(d_bank=d), 'd_bank_mechanics', 'admitted_turns', 'other_failure')

    def test_gate_time_over_forty_percent_of_t_dead_is_the_gate_time_branch(self):
        d = bank()
        d['intervals'][0].update(duration_s=190.0, end_ns=190_000_000_000)          # 190 + 90 + 120 = 400 = 0.40 x 1000: at the limit holds (<=)
        self.assertTrue(run(d_bank=d)['pass'])
        d['intervals'][0].update(duration_s=190.001, end_ns=190_001_000_000)
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

    def test_x_g_checks_g1_completeness_and_timing_when_run(self):
        d = {'x7': False, 'turns': [turn(0, 1500), turn(1, 3000)],
             'intervals': [interval('G0'), interval('G1', 1, outcome='unobserved')]}
        self.assertTrue(run(x_g=d)['pass'])   # The contrast has no released-sample requirement.
        for intervals in ([d['intervals'][0]], [{**d['intervals'][1], 'duration_s': 0}]):
            with self.subTest(intervals=intervals):
                result = run(x_g={**d, 'intervals': intervals})
                self.assertFalse(result['pass'])
                self.assertFalse(result['lines']['x_g']['pass'])

    def test_x_g_line(self):
        self.check_x(dict(XG, x7=True))
        self.check_x({'x7': False, 'intervals': [interval('G1', 3, outcome='timeout')]})

    def check_x(self, x_g):
        result = run(x_g=x_g)
        self.assertFalse(result['pass'])
        self.assertFalse(result['lines']['x_g']['pass'])
        self.assertEqual(result['verdict'], 'other_failure')

    def test_a_missing_d_bank_is_not_judged_as_a_pass(self):
        result = pc._judge_observations(step_d=STEP, d_bank=None, n_chunk=4096, x_g=None)
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
        d['intervals'][0].update(duration_s=500.0, end_ns=500_000_000_000)
        self.assertEqual(run(d_bank=d)['verdict'], 'mechanics_gate_time_failed')

    def test_three_turns_need_readable_stop_evidence(self):
        result = run(d_bank=bank(episode_flags=None))
        self.assertEqual(result['verdict'], 'other_failure')
        self.assertIn('flags', result['evidence_failures']['d_bank'])


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
        (self.bundle / 'outputs/align_episode.json').write_text(json.dumps(synthetic_episode('d-bank')))
        self.stamps = []

    def tick(self, n=1):
        for _ in range(n):
            self.clocks.advance(1.0)
            self.stamps.append(self.sidecar.tick()['started']['monotonic_ns'])
        return self.stamps[-1]

    def facts(self, *, release_ns=None, flags=('ended_in_unclosed_reasoning',)):
        """Two gates and two turns placed on the journal's own stamps (G0 release at tick 2, turn 0 after it;
        G1 release at tick 6, turn 1 after it), then ``facts_from_bundle`` on the written bundle."""
        g0_start = self.clocks.monotonic_ns()
        g0 = self.tick(2)
        t0 = self.clocks.monotonic_ns() + 100_000_000
        self.tick(3)
        g1 = self.tick()
        t1 = self.clocks.monotonic_ns() + 100_000_000
        self.tick(3)
        t0_end = t0 + 2_000_000_000
        intervals = [{'kind': 'G0', 'turn': 0, 'outcome': 'released', 'duration_s': (g0 - g0_start) / 1e9,
                      'start_ns': g0_start, 'end_ns': g0,
                      'exit_sample_ns': g0 if release_ns is None else release_ns},
                     {'kind': 'G1', 'turn': 1, 'outcome': 'released', 'duration_s': (g1 - t0_end) / 1e9,
                      'start_ns': t0_end, 'end_ns': g1, 'exit_sample_ns': g1}]
        from joulewise.align.apple.thermal_gates import ThermalSession
        for row in intervals:
            row.update(token_count=None, reference=STEP['reference'], release={'fast_c': 50.0, 'slow_c': 34.0},
                       slope_c_per_min=STEP['slope_c_per_min'], entry_stamp={'monotonic_ns': row['start_ns']})
            self.sidecar.event('align_thermal_gate', {'gate_kind': row['kind'], 'state': 'begin',
                                                     'turn': row['turn'], 'token_count': None,
                                                     'entry_stamp': row['entry_stamp']})
            ThermalSession.persist_interval(SimpleNamespace(sidecar=self.sidecar), row)
        self.sidecar.stop()
        turns = [SimpleNamespace(index=0, start_ns=t0, end_ns=t0_end, decode_tokens=2200, prefill_tokens=11211),
                 SimpleNamespace(index=1, start_ns=t1, end_ns=t1 + 2_000_000_000, decode_tokens=4096,
                                 prefill_tokens=40)]
        ep = SimpleNamespace(hardware={'thermal': {'intervals': intervals, 'flags': []},
                                       'token_budget': {'deadman_s': 983.1}},
                             turns=turns, flags=list(flags))
        self.fixture_episode = ep
        with patch('joulewise.align.apple.workload.read_episode_bundle', return_value=ep):
            return pc.facts_from_bundle(self.bundle, role='d-bank')

    def test_the_sidecar_journal_is_read_and_a_fresh_in_state_member_passes(self):
        facts = self.facts()
        raw = [json.loads(x) for x in (self.bundle / 'outputs/align_thermal.jsonl').read_text().splitlines()]
        self.assertEqual({r['kind'] for r in raw}, {'session_start', 'reading', 'align_thermal_gate', 'session_end'})
        self.assertNotIn('sample', {r['kind'] for r in raw})
        samples, _, _ = pc._journal(self.bundle)
        self.assertEqual(len(samples), len(self.stamps))
        line = pc.d_bank_start_state(facts)
        self.assertTrue(line['pass'], line)
        self.assertEqual(line['reasons'], [])
        self.assertEqual(len(line['samples']), 4)
        for sample in line['samples']:
            self.assertEqual((sample['os_level'], sample['pm_state'], sample['stamp_fresh']), (0, 'Nominal', True))
            self.assertLess(sample['pm_age_s'], 0)           # the stamp follows the sample's own stamp
            self.assertGreater(sample['pm_age_s'], -0.1)
        facts.pop('bundle_path')
        result = run(d_bank=facts, x_g=None, x_g_not_run_reason=pc.RuntimeAdmissionRefusal('x-g', 'native exit 2'))
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
        self.assertTrue(all('not recorded: not within 2 s of the sample, or absent' in r for r in line['reasons']))
        self.assertTrue(pc.stamp_fresh(2.0) and pc.stamp_fresh(-0.02))
        self.assertFalse(pc.stamp_fresh(2.0001) or pc.stamp_fresh(None) or pc.stamp_fresh(True))
        import contextlib
        import io
        with contextlib.redirect_stderr(io.StringIO()):         # RL-152 section 1.6: 2 s on either side
            self.assertFalse(pc.stamp_fresh(-2.01) or pc.stamp_fresh(float('nan')))
        self.assertTrue(pc.stamp_fresh(-2.0))

    def test_an_off_state_reading_fails_with_its_values(self):
        self.state.update(os_level=1, pm_state='Moderate')
        line = pc.d_bank_start_state(self.facts())
        self.assertFalse(line['pass'])
        self.assertIn("level 1, state 'Moderate'", line['reasons'][0])

    def test_failed_first_reading_cannot_be_replaced_by_a_later_nominal_reading(self):
        journal = self.bundle / 'outputs/align_thermal.jsonl'
        facts = self.facts()
        rows = [json.loads(line) for line in journal.read_text().splitlines()]
        after_start = next(r for r in rows if r['kind'] == 'reading'
                           and r['started']['monotonic_ns'] > facts['turns'][0]['start_ns'])
        after_start['values']['status'] = {'error': 'OSError: synthetic'}
        journal.write_text(''.join(json.dumps(r) + '\n' for r in rows))
        ep = SimpleNamespace(flags=[], turns=[SimpleNamespace(**t) for t in facts['turns']],
                             hardware={'thermal': {'intervals': [], 'flags': []}})
        with patch('joulewise.align.apple.workload.read_episode_bundle', return_value=ep):
            selected = pc.facts_from_bundle(self.bundle, role='d-bank')['turns'][0]['first_reading_after_start']
        self.assertEqual(selected.get('error'), 'OSError: synthetic')
        facts['turns'][0]['first_reading_after_start'] = selected
        self.assertEqual(run(d_bank=facts)['verdict'], 'start_state_failed')

    def test_reversed_bracket_cannot_move_a_hot_reading_out_of_the_start_window(self):
        facts = self.facts()
        journal = self.bundle / 'outputs/align_thermal.jsonl'
        rows = [json.loads(line) for line in journal.read_text().splitlines()]
        first = next(row for row in rows if row["kind"] == "reading"
                     and row["started"]["monotonic_ns"] > facts["turns"][0]["start_ns"])
        first["values"]["status"]["os_level"] = 2
        with patch('joulewise.align.apple.workload.read_episode_bundle', return_value=self.fixture_episode):
            journal.write_text(''.join(json.dumps(row) + '\n' for row in rows))
            hot = pc.facts_from_bundle(self.bundle, role='d-bank')
            self.assertEqual(run(d_bank=hot)['verdict'], 'start_state_failed')
            first["started"]["monotonic_ns"] = first["finished"]["monotonic_ns"] + 10_000_000_000
            journal.write_text(''.join(json.dumps(row) + '\n' for row in rows))
            rejected = pc.facts_from_bundle(self.bundle, role='d-bank')
            self.assertIn('reading_clock', rejected['evidence_error'])
            self.assertEqual(run(d_bank=rejected)['verdict'], 'other_failure')

    def test_every_native_journal_row_is_required(self):
        control = self.facts()
        control.pop('bundle_path')
        self.assertTrue(run(d_bank=control)['pass'])
        journal = self.bundle / 'outputs/align_thermal.jsonl'
        original = journal.read_text().splitlines(keepends=True)
        mutations = 0
        for i, line in enumerate(original):
            row = json.loads(line)
            for damage in ([], ['{\n'], [json.dumps({**row, 'seq': row['seq'] + 1}) + '\n']):
                journal.write_text(''.join(original[:i] + damage + original[i+1:]))
                with self.subTest(row=i, damage=damage):
                    with patch('joulewise.align.apple.workload.read_episode_bundle', return_value=self.fixture_episode):
                        evidence = pc.facts_from_bundle(self.bundle, role='d-bank')
                    self.assertIn('evidence_error', evidence)
                    self.assertFalse(run(d_bank=evidence)['pass'])
                    mutations += 1
        for gate in control['intervals']:
            i, sample = next((i, row) for i, line in enumerate(original)
                             if (row := json.loads(line))['kind'] == 'reading'
                             and row['started']['monotonic_ns'] == gate['exit_sample_ns'])
            for sensor_key in ('TG0D', 'TH0P'):
                changed = deepcopy(sample)
                changed['values']['sensors'][sensor_key] += 1
                journal.write_text(''.join(original[:i] + [json.dumps(changed) + '\n'] + original[i+1:]))
                with self.subTest(gate=gate['kind'], sensor=sensor_key):
                    with patch('joulewise.align.apple.workload.read_episode_bundle', return_value=self.fixture_episode):
                        evidence = pc.facts_from_bundle(self.bundle, role='d-bank')
                    self.assertIn('differs from its thermal reading', evidence['evidence_error'])
                    self.assertFalse(run(d_bank=evidence)['pass'])
                    mutations += 1
        print(f'Part C native journal mutations rejected: {mutations}')

    def test_episode_flags_must_be_present_and_unique_before_native_decoding(self):
        from joulewise.align.apple import workload
        from joulewise.align.records import Episode, Turn, to_jsonable

        self.facts()
        fixture = self.fixture_episode
        hardware = {**fixture.hardware, 'paired_clock_stamps_ns': [dict(
            epoch_ns=1, monotonic_before_ns=1, monotonic_after_ns=1,
            wall_resolution_ns=1, monotonic_resolution_ns=1)]}
        episode = Episode(episode_id='synthetic', task_pair='shade/bank_transfer_2', condition='benign',
                          agent_model='Qwen3.8-27B-8bit', endpoint='test', seed=1, clock_domain='synthetic', start_ns=0,
                          end_ns=fixture.turns[-1].end_ns, hardware=hardware, flags=tuple(fixture.flags),
                          turns=tuple(Turn(context_tokens=0, **vars(turn)) for turn in fixture.turns))
        payload = to_jsonable(episode)
        raw = json.dumps(payload)
        path = self.bundle / 'outputs/align_episode.json'
        auxiliary = SimpleNamespace(metadata=lambda: {}, trace_rows=lambda: [],
                                    config=lambda: SimpleNamespace(sampling=SimpleNamespace(power_hz=1)))
        with patch.object(workload, 'BundleReader', return_value=auxiliary):
            path.write_text(raw)
            clean = pc.facts_from_bundle(self.bundle, role='d-bank')
            clean.pop('bundle_path')
            self.assertTrue(run(d_bank=clean)['pass'])
            for damaged, reason in (
                ('{"flags":["episode.deadman:2"],' + raw[1:], 'duplicate JSON field'),
                (json.dumps({k: v for k, v in payload.items() if k != 'flags'}), 'explicitly record its flags'),
            ):
                with self.subTest(reason=reason):
                    path.write_text(damaged)
                    facts = pc.facts_from_bundle(self.bundle, role='d-bank')
                    self.assertIn(reason, facts.get('evidence_error', ''))
                    self.assertFalse(run(d_bank=facts)['pass'])

    def test_finalized_journal_failure_disagrees_with_bundle_for_both_roles(self):
        from joulewise.align.apple.thermal_gates import ThermalSession

        self.sidecar.stop()
        sidecar = SimpleNamespace(event=lambda kind, values: rows.append(
            {'module': 'temperature', 'kind': kind, 'values': values}))
        for journal_turn in (2, 3):
            rows = [{'kind': 'session_start', 'module': 'temperature', 'values': {}}]
            ThermalSession.persist_interval(SimpleNamespace(sidecar=sidecar),
                                            interval('G1', journal_turn, outcome='timeout'))
            rows.append({'kind': 'session_end', 'module': 'temperature', 'values': {}})
            ep = SimpleNamespace(flags=[], turns=[], hardware={'thermal': {'intervals': bank()['intervals'],
                                                                           'flags': []}})
            encoded = '\n'.join(map(json.dumps, rows)).encode()
            with self.subTest(journal_turn=journal_turn), \
                    patch('joulewise.align.apple.workload.read_episode_bundle', return_value=ep), \
                    patch('joulewise.desk_compress.read_bytes', return_value=encoded):
                extracted = pc.facts_from_bundle(self.bundle, role='d-bank')
                self.assertEqual(extracted['journal_intervals'][0]['outcome'], 'timeout')
                for role in ('d_bank', 'x_g'):
                    facts = {**bank(), **extracted, 'turns': bank()['turns'], 't_dead_s': 1000.0}
                    facts.pop('reading_stamps')
                    for row in facts['intervals']:
                        row['release_status'] = status()
                    result = run(**{role: facts})
                    self.assertEqual(result['verdict'], 'other_failure')
                    timeout = (result['lines']['x_g'] if role == 'x_g' else
                               result['lines']['d_bank_mechanics']['checks']['no_g1_timeout'])
                    self.assertIn(journal_turn, timeout['g1_timeout_turns'])


def synthetic_smoke_part_c(output, runtime, _config, *, soak_reference, facts, step_facts, invoke=None, prints=None):
    invoke = invoke or pc.judged_invoke
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    result = {"part": "C", "authority": "RL-145 step 3; RL-145 addendum section 6", "slots_entered": False, "members": {}}

    def finish(verdict_doc=None, error=None):
        if verdict_doc is not None:
            result["evaluation"] = verdict_doc
        if error is not None:
            result["error"] = error
        result["elapsed_s"] = time.monotonic() - started
        (output / "smoke_part_c.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        (output / "smoke.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        # RL-153 section 1.2 note 6, RL-156 section 3.2: the verdict and the evaluation's log (RL-152 section
        # 1.4's line among them) go to the terminal as well as the record; the record is unchanged.
        if verdict_doc is not None:
            print(f"Part C verdict: {verdict_doc.get('verdict')} (pass: {verdict_doc.get('pass')})")
            for line in verdict_doc.get("log") or ():
                print(f"Part C log: {line}")
    def run_member(kind, directory):
        return invoke(runtime, kind, directory, soak_reference=soak_reference)

    try:
        predecessor = run_member("capture-predecessor-30b", output / "capture_predecessor_30b")
        result["members"]["predecessor"] = predecessor
        step_dir = output / rt.STEP_D_SEGMENT
        step = run_member("step-d", step_dir)
        result["members"]["step_d"] = step
        slots = step.get("slots")
        n_chunk = (slots or {}).get("N_chunk")
        step_line = (step_facts(pc.bundle_directory(step_dir, step["bundle"]), step)
                     if step.get("bundle") else {"g0_outcome": step.get("g0_outcome")})
        if not isinstance(slots, dict) or not isinstance(n_chunk, int):
            doc = pc._judge_observations(predecessor=predecessor, step_d=step_line,
                                  n_chunk=n_chunk if isinstance(n_chunk, int) else 1)
            finish(doc, "step-D produced no slots: the gated members cannot run")
            raise ValueError("Part C: step-D produced no slots; see smoke_part_c.json")
        bank_dir = output / kit.PART_C_GATED_D
        bank = run_member("d-bank-benign-s1", bank_dir)
        result["members"]["d_bank"] = bank
        bank_bundle = pc.bundle_directory(bank_dir, bank["bundle"])
        bank_facts = {**facts(bank_bundle, role="d-bank"), "runtime": bank}
        printed = prints(bank_bundle) if prints is not None and "evidence_error" not in bank_facts else None
        x_g_facts, why = None, None
        x_g_dir = output / kit.PART_C_X_G
        try:
            x_g = run_member("x-g", x_g_dir)
        except pc.RuntimeEvidenceError as exc:
            if exc.receipt is not None:
                result["members"]["x_g"] = exc.receipt
            x_g_facts = {"evidence_error": str(exc)}
        except (subprocess.TimeoutExpired, UnicodeError, OSError) as exc:
            x_g_facts = {"evidence_error": f"{type(exc).__name__}: {exc}"}
        except pc.RuntimeAdmissionRefusal as exc:
            why = exc
        else:
            result["members"]["x_g"] = x_g
            try:
                bundle = pc.bundle_directory(x_g_dir, x_g["bundle"])
                x_g_facts = {**facts(bundle, role="x-g"), "runtime": x_g}
            except Exception as exc:
                # Once the runtime returns, any failure to read its evidence is judged.
                x_g_facts = {"evidence_error": f"{type(exc).__name__}: {exc}"}
        doc = pc._judge_observations(predecessor=predecessor, step_d=step_line, d_bank=bank_facts, n_chunk=n_chunk, x_g=x_g_facts,
                              x_g_not_run_reason=why, printed=printed,
                              oracle=oracle_that_passed(x_g_facts is not None))
        result["n_chunk_formula_recorded"] = (step.get("slot_detail") or {}).get("N_chunk_formula")
        finish(doc)
    except (pc.RuntimeEvidenceError, pc.RuntimeAdmissionRefusal) as exc:
        finish(pc._judge_observations(runtime_error=str(exc)), error=str(exc))
        raise ValueError("Part C: runtime receipt is invalid; see smoke_part_c.json") from exc
    except BaseException as exc:
        if "evaluation" not in result and "error" not in result:
            finish(error=f"{type(exc).__name__}: {exc}")
        raise
    if not doc["pass"]:
        raise ValueError(f"Part C failed ({doc['verdict']}): {doc['disposition']}")
    return result


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
            raise pc.RuntimeAdmissionRefusal('x-g', 'native exit 2')
        if kind == 'step-d':
            fields = {'slots': {'N_chunk': 4096, 'B_D': 6144, 'T_dead': 1000.0},
                      'slot_detail': {'N_chunk_formula': 1280}}
            return step_record(output.parent, STEP, 4096, receipt=fields)['member']['runtime']
        if kind == 'd-bank-benign-s1':
            return member_record(output.parent, 'd-bank', bank())['runtime']
        if kind == 'x-g':
            return member_record(output.parent, 'x-g', XG)['runtime']
        return write_predecessor(output)

    def facts(self, bundle, *, role):
        return {'d-bank': bank(), 'x-g': deepcopy(XG)}[role]

    def run_c(self, *, bank_facts=None, step_facts=None):
        root = self.tmp / 'c'

        def facts(bundle, *, role):
            payload = bank_facts if role == 'd-bank' and bank_facts else self.facts(bundle, role=role)
            return member_record(root, role, payload, save=False)

        def step_inputs(bundle, fields):
            return step_record(root, step_facts or STEP, 4096, receipt=fields, save=False)

        config = SimpleNamespace()
        return synthetic_smoke_part_c(root, ['runtime'], config, soak_reference='soak.json', invoke=self.invoke,
                                facts=facts, step_facts=step_inputs,
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

    def test_native_entry_refuses_before_any_launch_without_authorized_evidence(self):
        with patch.object(kit.r1, '_run') as run:
            with self.assertRaisesRegex(ValueError, 'evidence_unverifiable'):
                runtime = ['synthetic-runtime', '--config', str(kit.ROOT / kit.r1.DEFAULT_RUNTIME_CONFIG)]
                kit.smoke_part_c(self.tmp / 'c', runtime, SimpleNamespace(), soak_reference='synthetic')
        run.assert_not_called()
        record = json.loads((self.tmp / 'c/smoke_part_c.json').read_text())
        self.assertEqual(record['evaluation']['verdict'], 'other_failure')
        self.assertEqual(record, json.loads((self.tmp / 'c/smoke.json').read_text()))

    def test_the_verdict_and_the_log_are_printed_to_the_terminal(self):
        # RL-153 section 1.2 note 6, RL-156 section 3.2: finish prints the evaluation's log, RL-152 section
        # 1.4's line among them, as well as writing the record.
        with contextlib.redirect_stdout(io.StringIO()) as out:
            result = self.run_c()
        printed = out.getvalue()
        self.assertIn('Part C verdict: pass', printed)
        self.assertIn('three-turn clause not evaluated: one D run', printed)
        for line in result['evaluation']['log']:
            self.assertIn(line, printed)

    def test_x_g_that_cannot_run_is_left_out_with_a_log_line(self):
        self.x_g_fails = True
        result = self.run_c()
        evaluation = result['evaluation']
        self.assertTrue(evaluation['pass'])
        self.assertTrue(any(line.startswith('X_G was not run: runtime.x-g') for line in evaluation['log']))

    def test_native_predecessor_receipts_are_reconciled(self):
        from joulewise.align.apple.workload import EpisodeRuntimeAdapter

        original = self.invoke
        for mismatch in (False, True):
            with self.subTest(mismatch=mismatch), tempfile.TemporaryDirectory() as tmp:
                self.tmp = Path(tmp)

                def invoke(runtime, kind, output, **kwargs):
                    if kind != 'capture-predecessor-30b':
                        return original(runtime, kind, output, **kwargs)
                    template = self.tmp / 'synthetic-template.json'
                    template.write_text('{}')
                    mode = EpisodeRuntimeAdapter._observe_ac_powermode(SimpleNamespace(powermode_reader=lambda: 0))
                    member = SimpleNamespace(status='succeeded', bundle=output / 'runs/member',
                                             ep=SimpleNamespace(turns=[object()], hardware={'ac_powermode': mode}))
                    segment = SimpleNamespace(out=output, config={'templates': {'model_30b': str(template)}},
                                              run_member=lambda template, hook: member,
                                              template=lambda key: ({'run_metadata': {'tags': []}}, {}))
                    fields = rt.Segment.k_capture_predecessor_30b(segment)
                    write_predecessor(output, fields)
                    if mismatch:
                        write_receipt(output, {**fields, 'ac_powermode': 'Automatic'})
                    return fields

                self.invoke = invoke
                if mismatch:
                    with self.assertRaisesRegex(ValueError, 'other_failure'):
                        self.run_c()
                    result = json.loads((self.tmp / 'c/smoke_part_c.json').read_text())['evaluation']
                    self.assertIn('differs from runtime stdout', result['evidence_failures']['predecessor_receipt'])
                else:
                    self.assertTrue(self.run_c()['evaluation']['pass'])

    def test_duplicate_stdout_field_fails_before_the_last_value_can_win(self):
        original = self.invoke

        def invoke(runtime, kind, output, **kwargs):
            fields = original(runtime, kind, output, **kwargs)
            if kind != 'd-bank-benign-s1':
                return fields
            fields.update(energy_j=1, battery_drain_pct_per_h=0,
                          deadman={'T_dead_s': 1000.0, 'phases_s': {phase: 0 for phase in rt.contract.DEADMAN_PHASES}},
                          reference_source='step-d', inter_member_idle_s=300)
            write_receipt(output, fields)
            raw = '{"episode_flags":["episode.deadman:2"],' + json.dumps(fields)[1:]
            with patch.object(kit.r1, '_run', return_value=SimpleNamespace(returncode=0, stdout=raw + '\n', stderr='')):
                return pc.judged_invoke(runtime, kind, output, **kwargs)

        self.invoke = invoke
        with self.assertRaisesRegex(ValueError, 'invalid'):
            self.run_c()
        result = json.loads((self.tmp / 'c/smoke_part_c.json').read_text())['evaluation']
        self.assertEqual(result['verdict'], 'other_failure')
        self.assertIn('stdout_receipt: invalid', result['evidence_failures']['runtime_receipt'])

    def test_exit_two_cannot_hide_an_x_g_bundle_without_a_receipt(self):
        original = self.invoke

        def invoke(runtime, kind, output, **kwargs):
            if kind != 'x-g':
                return original(runtime, kind, output, **kwargs)
            bundle = output / 'runs/synthetic/outputs'
            bundle.mkdir(parents=True)
            (bundle / 'align_episode.json').write_text('{"turns":[{},{}],"flags":[]}')
            (bundle / 'align_thermal.jsonl').write_text('{}\n')
            with patch.object(kit.r1, '_run', return_value=SimpleNamespace(returncode=2, stdout='', stderr='refused')):
                return pc.judged_invoke(runtime, kind, output, **kwargs)

        self.invoke = invoke
        with self.assertRaisesRegex(ValueError, 'other_failure'):
            self.run_c()
        result = json.loads((self.tmp / 'c/smoke_part_c.json').read_text())['evaluation']
        self.assertIn('conflicts with output', result['evidence_failures']['x_g_launch'])
        self.assertFalse(any(line.startswith('X_G was not run:') for line in result['log']))

    def test_x_g_oserror_and_exit_two_with_completion_stdout_fail(self):
        original = self.invoke
        for error, response, reason in (
            (OSError('synthetic'), None, 'process_exit'),
            (None, SimpleNamespace(returncode=2, stdout='{"member_status":"succeeded","admitted_turns":2}',
                                   stderr='refused'), 'x_g_launch_conflict'),
            (None, SimpleNamespace(returncode=2, stdout=None, stderr='refused'), 'x_g_launch_conflict'),
        ):
            with self.subTest(reason=reason, response=response), tempfile.TemporaryDirectory() as tmp:
                self.tmp = Path(tmp)

                def invoke(runtime, kind, output, **kwargs):
                    if kind != 'x-g':
                        return original(runtime, kind, output, **kwargs)
                    with patch.object(kit.r1, '_run', side_effect=error, return_value=response):
                        return pc.judged_invoke(runtime, kind, output, **kwargs)

                self.invoke = invoke
                with self.assertRaisesRegex(ValueError, 'other_failure'):
                    self.run_c()
                evaluated = json.loads((self.tmp / 'c/smoke_part_c.json').read_text())['evaluation']
                self.assertIn(reason, evaluated['lines']['x_g']['evidence_error'])
                self.assertFalse(any(line.startswith('X_G was not run:') for line in evaluated['log']))

    def test_completed_x_g_with_missing_or_unreadable_evidence_fails(self):
        original = self.facts
        for failure in (FileNotFoundError('synthetic missing episode'), ValueError('synthetic unreadable episode')):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                self.tmp = Path(tmp)
                def facts(bundle, *, role):
                    if role == 'x-g':
                        raise failure
                    return original(bundle, role=role)
                self.facts = facts
                with self.assertRaisesRegex(ValueError, 'other_failure'):
                    self.run_c()
                table = json.loads((self.tmp / 'c' / 'smoke_part_c.json').read_text())
                self.assertIn('x_g', table['members'])
                self.assertFalse(table['evaluation']['lines']['x_g']['pass'])

    def test_zero_exit_x_g_missing_contract_fields_fails(self):
        original = self.invoke

        def invoke(runtime, kind, output, **kwargs):
            if kind != 'x-g':
                return original(runtime, kind, output, **kwargs)
            receipt = {'bundle': 'synthetic', 'admitted_turns': 2, 'episode_flags': []}
            process = SimpleNamespace(returncode=0, stdout=json.dumps(receipt) + '\n', stderr='')
            with patch.object(kit.r1, '_run', return_value=process):
                return pc.judged_invoke(runtime, kind, output, **kwargs)

        self.invoke = invoke
        with self.assertRaisesRegex(ValueError, 'other_failure'):
            self.run_c()
        table = json.loads((self.tmp / 'c' / 'smoke_part_c.json').read_text())
        self.assertEqual(table['members']['x_g']['admitted_turns'], 2)
        self.assertTrue(any('contract fields missing' in line for line in table['evaluation']['log']))
        self.assertFalse(table['evaluation']['lines']['x_g']['pass'])

    def test_a_failed_test_writes_the_table_then_raises(self):
        bad = bank()
        bad['turns'][1]['first_reading_after_start'] = status(1)
        with self.assertRaisesRegex(ValueError, 'start_state_failed'):
            self.run_c(bank_facts=bad)
        table = json.loads((self.tmp / 'c' / 'smoke_part_c.json').read_text())
        self.assertEqual(table['evaluation']['verdict'], 'start_state_failed')

    def test_no_step_d_slots_stops_before_the_gated_member(self):
        original = self.invoke
        self.invoke = lambda runtime, kind, output, **kw: ({'g0_outcome': 'timeout'}
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


class FrozenBoundaryTests(unittest.TestCase):
    def test_all_ten_r1_sources_are_exactly_the_issued_bytes(self):
        from joulewise.align.apple.v4_registration import R1_EXECUTED_SOURCES

        self.assertEqual(len(set(R1_EXECUTED_SOURCES)), 10)
        for path in R1_EXECUTED_SOURCES:
            with self.subTest(path=path):
                issued = subprocess.check_output(['git', 'show', f'b2e01464d:{path}'], cwd=kit.ROOT)
                self.assertEqual((kit.ROOT / path).read_bytes(), issued)

    def test_writer_control_passes_natively_and_in_archive(self):
        suite = (kit.ROOT / "tests/frozen/partc-v4/suite-v4/tests/align/test_partc_writer_v4.py")
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, "-IB", str(suite)], cwd=tmp, capture_output=True, text=True,
                env={**os.environ, "JW_PARTC_REPO": str(kit.ROOT), "JW_V4_PROOF": "1", "TMPDIR": tmp},
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PROOF frozen_checks, frozen driver, issued verdict, four bindings, native and archive: pass",
                      result.stdout.splitlines())

    def test_judged_invoker_uses_the_frozen_argv_with_and_without_lock(self):
        r1 = kit.r1
        for kind in ('capture-predecessor-30b', 'step-d', 'd-bank-benign-s1', 'x-g'):
            fields = {}
            for field in r1.contract.required_fields(kind, quiet=False):
                *parents, key = field.split('.')
                node = fields
                for parent in parents:
                    node = node.setdefault(parent, {})
                node.setdefault(key, {})
            process = SimpleNamespace(returncode=0, stdout=json.dumps(fields) + '\n', stderr='')
            for held in (False, True):
                lock = SimpleNamespace(held=held, pass_fds=lambda: (17,))
                with self.subTest(kind=kind, held=held), patch.object(r1, '_CHILD_HOST_LOCK', lock), \
                        patch.object(r1, '_run', return_value=process) as transport:
                    args = (['runtime', '--config', 'synthetic.json'], kind, Path('member'))
                    r1._invoke(*args, soak_reference=Path('soak.json'))
                    pc.judged_invoke(*args, soak_reference=Path('soak.json'))
                    self.assertEqual(transport.call_args_list[0], transport.call_args_list[1])

    def test_episode_replacement_during_frozen_read_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            path = bundle / 'outputs/align_episode.json'
            path.parent.mkdir()
            path.write_text(json.dumps(synthetic_episode('d-bank')))

            def replace(_):
                path.write_text('{"flags":["different"]}')

            with patch('joulewise.align.apple.workload.read_episode_bundle', side_effect=replace):
                evidence = pc.facts_from_bundle(bundle, role='d-bank')
            self.assertIn('source changed', evidence['evidence_error'])


class RunnerPartCTests(unittest.TestCase):
    def test_runner_c_requires_a_fresh_soak_even_through_python(self):
        from tests.align.test_r1_smoke_launcher import RunnerTests
        case = RunnerTests('test_order_and_receipt')
        case.setUp()
        self.addCleanup(case.doCleanups)
        case.args.parts = 'C'
        self.assertEqual(case.run_runner(), 2)
        self.assertEqual([e for e in case.events if e.startswith('part-')], [])
        receipt = case.receipt()
        self.assertEqual((receipt['parts'], receipt['parts_requested'], receipt['rc']), ({'C': False}, 'C', 2))
        self.assertFalse(case.live)


class SoakLauncherBindingTests(unittest.TestCase):
    """W1 handoff and direct checks alongside RL-215's writer-produced admission suite."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.attempt = SoakAttempt(Path(temp.name))
        self.attempt.config = kit.ROOT / kit.r1.DEFAULT_RUNTIME_CONFIG
        self.attempt.config_sha = hashed(self.attempt.config.read_bytes())
        self.attempt.revision = kit.r1.executed_commit(kit.ROOT)
        self.runtime = ["synthetic-runtime", "--config", str(self.attempt.config)]

    @staticmethod
    def journal(sensors, events, *, start=0, finish=None):
        """Serialize native sidecar rows and the frozen Coverage report."""
        from joulewise.align.apple.thermal import Coverage, keys
        selected = keys(sensors)
        coverage = Coverage(start, selected)

        def sample(fast, slow, ns):
            temps = {key: 34.0 if key.startswith("T") else 1200 for key in selected}
            temps.update({sensors["s_fast"]: fast, sensors["s_slow"]: slow})
            return {"source": "smc", "sensors": temps, "errors": {},
                    "units": {key: "degC" if key.startswith("T") else "rpm" for key in selected},
                    "readings": {key: {"value": value, "error": None} for key, value in temps.items()},
                    "status": {"os_level": 0, "pm_state": "Nominal",
                               "pm_observed_ns": ns, "monotonic_ns": ns}}

        def record(kind, index, ns, values):
            stamp = {"wall_ns": ns, "monotonic_ns": ns, "monotonic_raw_ns": ns}
            return {"kind": kind, "schema": "joulewise.align_thermal.v1", "module": "temperature",
                    "session": "synthetic-thermal", "seq": index, "started": stamp, "finished": stamp,
                    "values": values, "raw": [], "error": None}

        rows = [record("session_start", 1, start, {"thermal": sensors})]
        for kind, ns, data in events:
            values = sample(*data, ns) if kind == "reading" else data
            if kind == "reading":
                coverage.observe(ns, ns, values)
            rows.append(record(kind, len(rows) + 1, ns, values))
        end = events[-1][1] if finish is None else finish
        rows.append(record("session_end", len(rows) + 1, end,
                           {"collector_error": None, "coverage": coverage.report(end)}))
        return rows

    def make_idle(self):
        n = 1800
        times = [float(i) for i in range(n + 1)]
        sensors = rt.sensors_policy(rt.load_config(self.attempt.config)[0])
        fast, slow = sensors["s_fast"], sensors["s_slow"]
        degrees = float(f"35.{MARKER}")
        readings = {fast: degrees, slow: degrees}
        load = {
            "cpu_busy_cores": [0.1] * (n + 1), "cpu_busy_t_s": times,
            "census": [{"label": "start", "t_s": 0.0,
                        "processes": [{"pid": MARKER, "ppid": 0, "pcpu": 0.1, "comm": "synthetic"}]}],
        }
        observation = "Now drawing from 'AC Power'\n -InternalBattery-0 80%; charged;"
        battery_rows = [{"epoch_s": value, "raw": observation, **rt.parse_pmset_batt(observation)}
                        for value in (0.0, 120.0)]
        receipt = self.attempt.receipt(
            duration_s=float(n), sensor_roles=sensors, sensor_series_c={key: [value] * (n + 1)
                                                                         for key, value in readings.items()},
            sensor_series_t_s={key: times for key in readings}, sensor_series_end_t_s=float(n),
            sensor_series_failed_reads={key: 0 for key in readings}, load_journal_errors=[],
            sensor_series_note=("valid 1 Hz reads in order with their times (s from the first journal "
                                "row); a failed read is dropped, never interpolated"),
            battery=rt.battery_summary(battery_rows), **load)
        readings = [("reading", i * 1_000_000_000, (degrees, degrees)) for i in range(n + 1)]
        rows = self.journal(sensors, readings)
        return self.attempt.produce(receipt, **{
            "sensors/align_thermal.jsonl": b"".join(map(json_bytes, rows)),
            "battery.jsonl": b"".join(map(json_bytes, battery_rows)),
            "load_journal.json": json_bytes({"exclude_roots": [MARKER], "errors": [], **load}),
        })

    def run_launcher(self, *, idle_error=None, before_kit=None):
        def transport(argv):
            kind = argv[argv.index("--r1-kind") + 1]
            output = Path(argv[argv.index("--output") + 1])
            if kind == "idle" and idle_error is not None:
                raise idle_error
            if kind == "idle":
                return self.make_idle()
            self.fail(f"the handoff must stop before dispatching {kind}")

        real_popen = subprocess.Popen

        def child(argv, *args, stdout=None, stderr=None, **kwargs):
            command = Path(argv[2]).name if len(argv) > 2 else ""
            if command not in ("run_align_r1_smoke.py", "align_r1_followup_kit.py"):
                return real_popen(argv, *args, stdout=stdout, stderr=stderr, **kwargs)
            if command == "align_r1_followup_kit.py" and before_kit is not None:
                before_kit()
            with contextlib.redirect_stdout(io.TextIOWrapper(stdout, write_through=True)) as pipe, \
                    contextlib.redirect_stderr(io.TextIOWrapper(stderr, write_through=True)) as errors:
                try:
                    rc = (smoke.main if command == "run_align_r1_smoke.py" else kit.main)(argv[3:])
                except ValueError:
                    rc = 2
                finally:
                    pipe.detach()
                    errors.detach()
            return SimpleNamespace(pid=90001, poll=lambda: rc, wait=lambda: rc)

        with contextlib.ExitStack() as stack:
            for name in ("night_agents", "ac_power", "condition13", "read_power", "display", "dwell", "restore_power"):
                stack.enter_context(patch.object(smoke, name, return_value={"rc": 0}))
            stack.enter_context(patch.object(smoke, "SIGNALS", ()))
            stack.enter_context(patch.object(smoke.subprocess, "Popen", side_effect=child))
            stack.enter_context(patch.object(smoke, "PartDeadline", return_value=SimpleNamespace(
                start=lambda: None, cancel=lambda: None, expired=lambda: False)))
            stack.enter_context(patch.object(smoke.night, "_terminate_process_group", return_value=True))
            stack.enter_context(patch.object(kit.r1, "executed_commit", return_value=self.attempt.revision))
            stack.enter_context(patch.object(kit.reg, "verify_r1_executed_sources"))
            stack.enter_context(patch.object(kit.r1, "runtime_argv_from_inputs", return_value=self.runtime))
            stack.enter_context(patch.object(kit.r1, "_run", side_effect=transport))
            stack.enter_context(patch.object(kit.r1, "wait_outside_os_batch"))
            args = SimpleNamespace(output=self.attempt.root, soak_reference=None, fresh_soak=True, parts="C",
                                   pmset_bin="synthetic", deadline=time.time() + 90_000)
            return smoke.run(args, feeds=[])

    def check_writer_handoff(self, *fault):
        probe = Path(__file__).with_name("rl145_w1_handoff.py").resolve()
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, "-IB", str(probe), str(kit.ROOT), str(Path(smoke.__file__).resolve()), *fault],
                cwd=tmp, capture_output=True, text=True,
                env={**os.environ, "JW_PARTC_REPO": str(kit.ROOT), "TMPDIR": tmp},
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_current_w1_launcher_passes_the_bound_soak_handoff(self):
        self.check_writer_handoff()

    def test_current_w1_launcher_rejects_wrong_forwarded_hashes(self):
        for fault in ("handoff-ledger", "publication-ledger", "publication-reference"):
            with self.subTest(fault=fault):
                self.check_writer_handoff(fault)

    def test_idle_argv_matches_frozen_invoker_with_and_without_the_host_lock(self):
        for held in (False, True):
            with self.subTest(held=held), tempfile.TemporaryDirectory() as tmp:
                attempt = SoakAttempt(Path(tmp))
                attempt.directory.mkdir(parents=True)
                writer = pc.EvidenceLedger(attempt.directory, attempt.revision, attempt.config, mode="soak")
                rt_receipt = attempt.receipt(cpu_busy_cores=[], cpu_busy_t_s=[], census=[], sensor_series_c={},
                                             sensor_series_t_s={}, sensor_series_end_t_s=0)
                process = attempt.produce(rt_receipt)
                lock = SimpleNamespace(held=held, pass_fds=lambda: (16,))
                with patch.object(kit.r1, "_CHILD_HOST_LOCK", lock), patch.object(
                        kit.r1, "_run", return_value=process) as call:
                    arguments = (["runtime"], "idle", attempt.segment, 1800.0)
                    kwargs = {"quiet": True, "contract_key": "idle_soak"}
                    kit.r1._invoke(*arguments, **kwargs)
                    pc.judged_invoke(*arguments, **kwargs, ledger=writer)
                    self.assertEqual(call.call_args_list[0], call.call_args_list[1])

    def test_real_child_stdout_matches_the_frozen_soak_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            attempt = SoakAttempt(Path(tmp))
            issued = attempt.produce(attempt.receipt())
            command = [sys.executable, "-c", f"import sys; sys.stdout.write({issued.stdout!r})"]
            with patch.object(kit.r1, "_terminate", side_effect=AssertionError("no signals")):
                actual = kit.r1._run(command)
            self.assertEqual(actual.returncode, 0)
            path_sha = attempt.close(process=actual)
            self.assertEqual(attempt.binding(path_sha).row["result"], attempt.receipt())

    def test_changed_ledger_after_handoff_refuses_before_kit_row_zero(self):
        def edit():
            raw = self.attempt.ledger.read_bytes()
            self.attempt.ledger.write_bytes(b" " + raw[1:])

        self.assertEqual(self.run_launcher(before_kit=edit), 2)
        self.assertFalse((self.attempt.output / "evidence_ledger.jsonl").exists())
        record = json.loads((self.attempt.output / "smoke.json").read_bytes())
        self.assertIs(record["evaluation"]["pass"], False)
        self.assertEqual(record["evaluation"]["evidence_failures"], {"source_integrity": "source_integrity"})

    def test_failed_soak_closes_its_ledger_and_starts_no_kit(self):
        self.assertEqual(self.run_launcher(idle_error=OSError(str(MARKER))), 2)
        rows = [json.loads(line) for line in self.attempt.ledger.read_bytes().splitlines()]
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]["exception"], "OSError")
        self.assertEqual(rows[2]["outcome"], "refused")
        self.assertEqual(rows[2]["soak_reference_sha256"], "absent")
        self.assertFalse(self.attempt.output.exists())
        self.assertNotIn(str(MARKER), (self.attempt.root / "part-soak.stdout.log").read_text())
        self.assertNotIn(str(MARKER), (self.attempt.root / "part-soak.stderr.log").read_text())

    def test_archive_cli_accepts_idle_custody_without_a_soak_ledger(self):
        self.attempt.close()
        self.attempt.ledger.unlink()
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(kit.main(["replay-archived", "--output", str(self.attempt.output),
                                       "--runtime-config", str(self.attempt.config), "--kind", "idle"]), 0)
        self.assertEqual(json.loads(out.getvalue()), {"binding": "archived_custody"})
        self.assertFalse(self.attempt.output.exists())

    def rl186_gate(self, *, missing=()):
        from joulewise.align.apple import thermal_gates as gates

        ns = pc.NS
        configured = rt.load_config(self.attempt.config)[0]
        sensors = rt.sensors_policy(configured)
        start, end = 60 * ns, 69 * ns
        journal = self.journal(sensors, [("reading", t * ns, (35.0, 35.0)) for t in range(400)
                                         if t not in missing])
        samples = gates.sample_rows(journal)
        interval = {
            "kind": "G0", "outcome": "released", "start_ns": start, "end_ns": end,
            "exit_sample_ns": end, "release": dict(fast_c=35.0, slow_c=35.0),
            "reference": dict(fast_c=35.0, slow_c=35.0),
            "entry_sensors": samples[next(i for i, row in enumerate(samples) if row["monotonic_ns"] == start)][
                "sensors"],
            "entry_slope_c_per_min": 0.0, "slope_c_per_min": 0.0,
        }
        policy = {"sensors": sensors, "delta_fast_c": 1.0, "delta_slow_c": 1.0,
                  "g0_cap_s": 1200, "turn_cap_s": 30}
        return journal, interval, policy

    @staticmethod
    def rl186_findings(journal, interval, policy, deadline=None):
        return {(row.field, row.reason) for row in pc._gate_findings(
            "d-bank-benign-s1", journal, [interval], (interval["reference"], interval["reference"]),
            policy, deadline)}

    def test_rl186_gate_word_counterexample_and_coverage_monotonicity(self):
        ns = pc.NS
        journal, interval, policy = self.rl186_gate(missing=range(7, 13))
        findings = self.rl186_findings(journal, interval, policy)
        self.assertIn(("U1", "evidence_unverifiable"), findings)
        good, _, _ = self.rl186_gate(missing=range(7, 11))
        self.assertFalse(self.rl186_findings(good, interval, policy))
        damaged, _, _ = self.rl186_gate(missing=range(7, 14))
        self.assertIn(("U1", "release_conditions"), self.rl186_findings(damaged, interval, policy))
        from joulewise.align.apple.thermal_gates import _window_coverage, sample_rows

        keys = tuple(policy["sensors"][role] for role in ("s_fast", "s_slow"))
        for source in (journal, good, damaged):
            reads = sample_rows(source)
            for instant in (60 * ns, 60 * ns + 200_000_000, 69 * ns):
                visible = [row for row in reads if row["monotonic_ns"] <= instant]
                full = _window_coverage(visible, instant, keys)["sample_fraction"]
                for index in range(len(visible)):
                    fewer = visible[:index] + visible[index + 1:]
                    self.assertLessEqual(_window_coverage(fewer, instant, keys)["sample_fraction"], full)

    def test_rl186_release_witness_mutations(self):
        ns = pc.NS
        journal, interval, policy = self.rl186_gate()
        deadline = 100 * ns
        self.assertFalse(self.rl186_findings(journal, interval, policy, deadline))

        def change_status(rows, begin, end, edit):
            for row in rows:
                instant = row["started"]["monotonic_ns"]
                if row["kind"] == "reading" and begin * ns <= instant <= end * ns:
                    edit(row["values"]["status"])

        operations = (
            ("U2", "evidence_unverifiable",
             lambda j, i, p: change_status(j, 50, 59, lambda status: status.clear()), deadline),
            ("U3", "evidence_unverifiable", lambda j, i, p: p.update(g0_cap_s=10), deadline),
            ("U4", "evidence_unverifiable", lambda j, i, p: None, 65 * ns),
            ("N1", "release_sample", lambda j, i, p: i["release"].update(fast_c=MARKER), deadline),
            ("N2", "evidence_unverifiable", lambda j, i, p: i.update(exit_sample_ns=67 * ns), deadline),
            ("N3", "release_conditions",
             lambda j, i, p: change_status(j, 64, 64, lambda status: status.update(os_level=MARKER)), deadline),
            ("N4", "evidence_unverifiable",
             lambda j, i, p: change_status(j, 64, 64, lambda status: status.update(pm_observed_ns=61 * ns)), deadline),
            ("N5.exit_slope", "evidence_unverifiable",
             lambda j, i, p: i.update(slope_c_per_min=MARKER), deadline),
            ("N5.entry", "evidence_unverifiable",
             lambda j, i, p: i.update(entry_slope_c_per_min=MARKER), deadline),
            ("N5.entry", "evidence_unverifiable",
             lambda j, i, p: i.update(entry_sensors={}), deadline),
        )
        for clause, reason, mutate, due in operations:
            with self.subTest(clause=clause):
                changed_journal, changed_interval, changed_policy = deepcopy((journal, interval, policy))
                mutate(changed_journal, changed_interval, changed_policy)
                findings = pc._gate_findings(
                    "d-bank-benign-s1", changed_journal, [changed_interval],
                    (interval["reference"], interval["reference"]), changed_policy, due)
                self.assertIn((clause, reason), {(e.field, e.reason) for e in findings})
                self.assertNotIn(str(MARKER), json.dumps([e.finding() for e in findings]))
        change_status(journal, 64, 64, lambda status: status.update(pm_observed_ns=62 * ns))
        self.assertFalse(self.rl186_findings(journal, interval, policy, deadline))

    def test_rl186_other_gate_words_and_clock_brackets(self):
        ns = pc.NS
        journal, interval, policy = self.rl186_gate()
        bad = {**interval, "outcome": "unobserved", "end_ns": 360 * ns, "exit_sample_ns": 360 * ns}
        self.assertIn(("unobserved", "evidence_unverifiable"), self.rl186_findings(journal, bad, policy))
        missing, _, _ = self.rl186_gate(missing=range(7, 14))
        bad["entry_slope_c_per_min"] = None
        self.assertFalse(self.rl186_findings(missing, bad, policy))
        self.assertIn(("unobserved_cap", "gate_outcome"),
                      self.rl186_findings(missing, {**bad, "end_ns": 359 * ns}, policy))
        shortened = {**policy, "g0_cap_s": 9.0}
        timeout = {**interval, "outcome": "timeout"}
        self.assertIn(("timeout", "gate_outcome"), self.rl186_findings(journal, timeout, shortened))
        hot = deepcopy(journal)
        sensor = policy["sensors"]["s_fast"]
        for row in hot:
            if row["kind"] == "reading":
                row["values"]["sensors"][sensor] = 42.0
        timed_out = {**timeout, "entry_sensors": hot[61]["values"]["sensors"],
                     "release": {"fast_c": 42.0, "slow_c": 35.0}}
        self.assertFalse(self.rl186_findings(hot, timed_out, shortened))
        deadman = {**interval, "outcome": "deadman"}
        self.assertFalse(self.rl186_findings(journal, deadman, policy, 65 * ns))
        self.assertIn(("deadline", "gate_outcome"), self.rl186_findings(journal, deadman, policy, 70 * ns))
        for start, end, expired, verdict in (
            (1, 9, False, None), (1, 10, False, "evidence_unverifiable"),
            (10, 11, False, "admission_recompute"), (1, 10, True, None), (1, 9, True, "admission_recompute"),
        ):
            with self.subTest(start=start, end=end, expired=expired):
                if verdict:
                    with self.assertRaisesRegex(pc.EvidenceFailure, verdict):
                        pc._check_clock_decision("step-d", start, end, 10, "deadman", expired=expired)
                else:
                    pc._check_clock_decision("step-d", start, end, 10, "deadman", expired=expired)

    def test_every_phase_rejects_absence_wrong_type_and_a_one_unit_difference(self):
        for kind, role in (("d-bank-benign-s1", "d-bank"), ("x-g", "x-g")):
            with self.subTest(member=kind):
                ns = pc.NS
                budget = {"deadline_ns": 12 * ns}
                episode = json_bytes(synthetic_episode(
                    role, episode_id="synthetic", endpoint="synthetic", clock_domain="synthetic",
                    start_ns=0, end_ns=13 * ns,
                    turns=[{"index": 0, "start_ns": 2 * ns, "first_token_ns": 5 * ns, "end_ns": 10 * ns,
                            "context_tokens": 0, "prefill_tokens": 1, "decode_tokens": 1}],
                    hardware={"token_budget": budget, "thermal": {"intervals": [
                        {"kind": "G0", "duration_s": 2.0},
                    ]}},
                ))
                trusted = {"G0": 2.0, "G1": 0.0, "H": 0.0, "decode": 5.0, "prefill": 3.0,
                           "tool": 0.0, "tail": 1.0}
                holder = {"deadline_ns": budget["deadline_ns"], "phases_s": trusted}
                receipt = {"deadman": holder} if kind == "d-bank-benign-s1" else holder
                pc._check_phase_accounting(kind, receipt, episode, budget)
                for phase, seconds in trusted.items():
                    for operation, value in (("delete", None), ("null", None), ("bool", True),
                                             ("plus", seconds + 1), ("minus", seconds - 1)):
                        with self.subTest(phase=phase, operation=operation):
                            mutant = {**trusted, phase: value}
                            if operation == "delete":
                                del mutant[phase]
                            holder["phases_s"] = mutant
                            with self.assertRaisesRegex(pc.EvidenceFailure, "phase_accounting"):
                                pc._check_phase_accounting(kind, receipt, episode, budget)
