"""Reference-state rows (RL-148 desk step 6; RL-149 section 1.3; RL-153 section 2; RL-154): production and twin.

Synthetic only: in-memory episodes, traces, member journals, OS readings and PM
rows. No bundle, no measurement, no model. The optional world test
(JW_S_ROWS_WORLD=1) drives the WP22 synthetic world through the controller to
build failed-execution bundles.
"""
from __future__ import annotations

from dataclasses import replace
import math
import os
from pathlib import Path
import random
import tempfile
import unittest
from unittest import mock

from joulewise.align.apple import rl145_prints, s_rows
from joulewise.align.apple.s_rows import ClockClause, RowConstants
from joulewise.align.attribution import trace_energy
from joulewise.align.records import Episode, PowerTrace, ToolCall, Turn
from tests.align.twins import s_rows_twin as twin

NS = 1_000_000_000
MS = 1_000_000
BOTH = frozenset({'os_level', 'pm_state'})
REASONS = {'turn_end', 'deadman_last_token', 'os_level_above_0', 'journal_pm_state_off', 'native_pm_state_off',
           'hazard_os_level_above_0', 'state_unobserved', 'clock_e20', 'clock_base_e20'}
NO_ROW = {'start_out_of_state', 'start_state_unobserved', 'cut_in_prefill', 'after_hot_turn',
          'deadman_before_first_token', 'no_decode_token', 'token_stamps_count_mismatch',
          'token_stamps_unavailable', 'clock_reference_missing'}


def watts_at(t, phases):
    for a, b, w in phases:
        if a <= t < b:
            return w
    return 2.0


def build(eid, spec, *, condition='benign', flags=(), start=10 * NS, os_level=None, pm_state=None,
          journal_pm=None, age=None, keep=None, clock=None, max_state=None, deadman_turn=None,
          prefill_cut_turn=None, holds=(), pair='shade/x', watt_scale=1.0):
    """One synthetic member. ``spec``: per turn (context, prefill_tokens, prefill_s, decode_tokens, tok_s, tool_s).

    Functions of absolute ns: ``os_level`` (default 0), ``pm_state`` (native PM rows; default Nominal),
    ``journal_pm`` (the journal's state; default ``pm_state``), ``age`` (the journal stamp's age in s at the
    reading, None for no stamp; default -0.015), ``keep`` (whether a journal reading exists; default all),
    ``clock`` (default 1400 MHz) and ``max_state`` (default 1400 MHz). The journal reads every 1 s.
    deadman_turn: the last turn, cut mid-decode (its finish reason is episode.deadman).
    prefill_cut_turn: the last turn, cut inside prefill (full prompt count, zero decode, first_token_ns = cut).
    Returns (episode, stamps, finish reasons, journal samples, PM rows).
    """
    t = start
    turns, stamps, finish, phases = [], {}, {}, []
    for index, (context, prefill, prefill_s, decode, tok_s, tool_s) in enumerate(spec):
        t0 = t
        first = t0 + round(prefill_s * NS)
        phases.append((t0, first, 30.0 * watt_scale))
        if index == prefill_cut_turn:
            turns.append(Turn(index=index, start_ns=t0, end_ns=first + MS, context_tokens=context,
                              prefill_tokens=prefill, decode_tokens=0, first_token_ns=first))
            finish[index] = 'episode.deadman'
            stamps[index] = []
            t = first + MS
            break
        dt = round(tok_s * NS)
        own = [first + dt * (i + 1) for i in range(decode)]
        end = own[-1] + 50 * MS
        phases.append((first, end, (25.0 + 0.001 * index) * watt_scale))
        calls = ()
        finish[index] = 'episode.deadman' if index == deadman_turn else 'stop'
        stamps[index] = own
        if tool_s and index != deadman_turn:
            calls = (ToolCall('act', end + 10 * MS, end + 10 * MS + round(tool_s * NS), 3, 5),)
            phases.append((end + 10 * MS, end + 10 * MS + round(tool_s * NS), 8.0))
            t = calls[0].end_ns + 2 * NS
        else:
            t = end + 2 * NS
        turns.append(Turn(index=index, start_ns=t0, end_ns=end, context_tokens=context, prefill_tokens=prefill,
                          decode_tokens=decode, first_token_ns=first, tool_calls=calls))
        if index == deadman_turn:
            break
    end_ns = turns[-1].end_ns + 500 * MS
    grid = range(start - NS, end_ns + 2 * NS, 100 * MS)
    trace = PowerTrace(source='powermetrics', channel='gpu_power', clock_domain=f'ep:{eid}',
                       t_ns=tuple(grid), values=tuple(watts_at(x, phases) for x in grid), unit='W',
                       nominal_interval_ns=100 * MS)
    hardware = {'thermal': {'intervals': [dict(kind='H', turn=k, start_ns=a, end_ns=b) for a, b, k in holds]}}
    ep = Episode(episode_id=eid, task_pair=pair, condition=condition, agent_model='syn', endpoint='syn', seed=0,
                 clock_domain=f'ep:{eid}', start_ns=start, end_ns=end_ns, turns=tuple(turns),
                 power_traces=(trace,), hardware=hardware, flags=tuple(flags))
    os_fn = os_level or (lambda x: 0)
    pm_fn = pm_state or (lambda x: 'Nominal')
    jpm_fn = journal_pm or pm_fn
    age_fn = age or (lambda x: -0.015)
    keep_fn = keep or (lambda x: True)
    journal = []
    for x in range(((start - 5 * NS) // NS) * NS, end_ns, NS):
        if not keep_fn(x):
            continue
        a = age_fn(x)
        journal.append({'kind': 'sample', 'monotonic_ns': x,
                        'status': {'os_level': os_fn(x), 'pm_state': jpm_fn(x),
                                   'pm_observed_ns': None if a is None else x - round(a * NS)}})
    pm_rows = []
    for a in range(start - 5 * NS, end_ns, 250 * MS):
        b = a + 250 * MS
        busy = any(p <= a < q for p, q, _ in phases[:]) and watts_at(a, phases) > 10
        pm_rows.append({'start_ns': a, 'end_ns': b, 'state': pm_fn(b),
                        'active_ns': (250 * MS) if busy else 10 * MS,
                        'clock_mhz': (clock or (lambda x: 1400.0))(b) if busy else 400.0,
                        'max_state_mhz': (max_state or (lambda x: 1400.0))(b)})
    return ep, stamps, finish, journal, pm_rows


SPEC3 = [(0, 3000, 6.0, 400, 0.08, 1.0), (3400, 120, 0.4, 300, 0.08, 1.0), (3820, 90, 0.3, 200, 0.08, 0.0)]
SPEC1 = [(0, 3000, 6.0, 400, 0.08, 0.0)]


def run(member, constants, hazard_os=()):
    ep, stamps, finish, journal, pm_rows = member
    return s_rows.member_rows(ep, token_stamps=stamps, finish_reasons=finish, journal=journal,
                              pm_rows=pm_rows, constants=constants, hazard_os=hazard_os)


def run_twin(member, constants, hazard_os=()):
    ep, stamps, finish, journal, pm_rows = member
    clock = None if constants.clock is None else dict(
        reference=constants.clock.reference, ratio=constants.clock.ratio, window_s=constants.clock.window_s,
        base_mhz=constants.clock.base_mhz, start_after_first_token_s=constants.clock.start_after_first_token_s)
    return twin.rows_for(ep, token_stamps=stamps, finish_reasons=finish, journal=journal,
                         pm_rows=pm_rows, state=constants.state, clock=clock, guard_s=constants.guard_s,
                         hazard_os=hazard_os, edge_j=constants.edge_j, edges=constants.edges)


def outcome(member, constants, hazard_os=()):
    """(rows, no_row) of production, asserted equal to the twin's."""
    p = run(member, constants, hazard_os)
    t = run_twin(member, constants, hazard_os)
    prod = ([(r.turn, r.decode_tokens, r.end_ns, r.reason) for r in p.rows], list(p.no_row))
    tw = ([(r['turn'], r['decode_tokens'], r['end_ns'], r['reason']) for r in t['rows']], t['no_row'])
    assert prod == tw, (prod, tw)
    return p


C_BOTH = RowConstants(state=BOTH, clock=None, guard_s=2.0)
REG = s_rows.REGISTERED


class RowTests(unittest.TestCase):
    def test_whole_turns_score_model_call_energy_only(self):
        m = build('a', SPEC3)
        out = run(m, C_BOTH)
        ep = m[0]
        self.assertEqual([(r.turn, r.decode_tokens, r.reason, r.cut) for r in out.rows],
                         [(0, 400, 'turn_end', False), (1, 300, 'turn_end', False), (2, 200, 'turn_end', False)])
        expected = math.fsum(trace_energy(ep.power_traces[0], t.start_ns, t.end_ns).joules for t in ep.turns)
        self.assertAlmostEqual(out.measured_j, expected, places=9)
        whole = trace_energy(ep.power_traces[0], ep.start_ns, ep.end_ns).joules
        self.assertGreater(whole - out.measured_j, 8.0 * 2 - 1)   # tool calls and gaps are not scored
        self.assertEqual((out.status, out.ended_by, out.truncated, out.n_edges), ('scored', 'returned', False, 6))
        self.assertEqual(out.scored_through_ns, ep.turns[-1].end_ns)
        self.assertEqual([e['start_state'] for e in out.candidates], ['ok'] * 3)

    def test_os_cut_snaps_to_the_last_stamp_before_the_guard(self):
        probe = build('a', SPEC3)
        t1 = probe[0].turns[1]
        m = build('a', SPEC3, os_level=lambda x: 1 if t1.first_token_ns + 15 * NS <= x <= t1.end_ns else 0)
        out = outcome(m, C_BOTH)
        row = next(r for r in out.rows if r.turn == 1)
        reading = min(s['monotonic_ns'] for s in m[3] if s['status']['os_level'] == 1)
        limit = reading - 2 * NS
        stamps = m[1][1]
        self.assertEqual(row.decode_tokens, sum(1 for s in stamps if s <= limit))
        self.assertEqual(row.end_ns, stamps[row.decode_tokens - 1])
        self.assertEqual((row.reason, row.cut, row.logged_decode_tokens), ('os_level_above_0', True, 300))
        self.assertAlmostEqual(row.energy_j, trace_energy(m[0].power_traces[0], t1.start_ns, row.end_ns).joules)
        self.assertEqual(out.no_row, ({'turn': 2, 'reason': 'after_hot_turn'},))

    def test_state_definition_is_an_input(self):
        probe = build('a', SPEC1)
        t0 = probe[0].turns[0]
        pm_hot = lambda x: 'Moderate' if t0.first_token_ns + 10 * NS <= x <= t0.end_ns else 'Nominal'
        m = build('a', SPEC1, pm_state=pm_hot)
        self.assertIn('pm_state_off', outcome(m, RowConstants(state={'pm_state'}, clock=None, guard_s=2))
                      .rows[0].reason)
        self.assertEqual(outcome(m, RowConstants(state={'os_level'}, clock=None, guard_s=2)).rows[0].reason,
                         'turn_end')
        # Native Unknown and missing states never cut. RL-154 finding 5: the journal has its own state
        # (Nominal), so this checks the native rows only; a journal reading Unknown or missing is unobserved
        # (RL154UnknownIsUnobservedTests).
        unknown = build('a', SPEC1, pm_state=lambda x: 'Unknown' if x > t0.first_token_ns else None,
                        journal_pm=lambda x: 'Nominal')
        self.assertEqual(outcome(unknown, C_BOTH).rows[0].reason, 'turn_end')

    def test_journal_pm_state_cuts_without_a_native_row(self):
        probe = build('a', SPEC1)
        t0 = probe[0].turns[0]
        m = build('a', SPEC1, journal_pm=lambda x: 'Heavy' if x >= t0.first_token_ns + 12 * NS else 'Nominal')
        row = outcome(m, C_BOTH).rows[0]
        off = min(s['monotonic_ns'] for s in m[3] if s['status']['pm_state'] == 'Heavy')
        self.assertEqual(row.reason, 'journal_pm_state_off')
        self.assertEqual(row.decode_tokens, sum(1 for s in m[1][0] if s <= off - 2 * NS))

    def test_hot_turn_ends_the_member_and_a_later_turn_gives_after_hot_turn(self):
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        # Hot late in turn 0: turn 0 is cut; turns 1 and 2 give no row whatever their start reads.
        m = build('a', SPEC3, os_level=lambda x: 1 if t0.end_ns - 6 * NS <= x <= t0.end_ns else 0)
        out = outcome(m, C_BOTH)
        self.assertEqual([(r.turn, r.reason) for r in out.rows], [(0, 'os_level_above_0')])
        self.assertEqual(out.no_row, ({'turn': 1, 'reason': 'after_hot_turn'},
                                      {'turn': 2, 'reason': 'after_hot_turn'}))
        self.assertEqual(s_rows.scored_shares(out)['after_hot_turn'], 2)
        self.assertEqual([e['start_state'] for e in out.candidates], ['ok'] * 3)

    def test_turn_starting_out_of_state_gives_no_row_and_ends_the_member(self):
        probe = build('a', SPEC3)
        t0, t1 = probe[0].turns[0], probe[0].turns[1]
        # Hot only between turns 0 and 1 (after turn 0's last token): turn 0 is whole, turn 1 starts out of
        # state, turn 2 follows a hot turn.
        m = build('a', SPEC3, os_level=lambda x: 1 if t0.end_ns <= x <= t1.start_ns + 500 * MS else 0)
        out = outcome(m, C_BOTH)
        self.assertEqual([(r.turn, r.reason) for r in out.rows], [(0, 'turn_end')])
        self.assertEqual(out.no_row, ({'turn': 1, 'reason': 'start_out_of_state'},
                                      {'turn': 2, 'reason': 'after_hot_turn'}))

    def test_cut_inside_prefill_gives_cut_in_prefill(self):
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        m = build('a', SPEC3, os_level=lambda x: 1 if t0.start_ns + 3 * NS <= x <= t0.end_ns else 0)
        out = outcome(m, C_BOTH)
        self.assertEqual(out.rows, ())
        self.assertEqual([x['reason'] for x in out.no_row], ['cut_in_prefill', 'after_hot_turn', 'after_hot_turn'])

    def test_search_ends_at_the_last_stamped_token(self):
        # A reading after the last stamped token (here a hazard reading 20 ms later, before the turn
        # record's end) is outside the turn's search: the turn is whole and not hot.
        m = build('a', SPEC3)
        t0 = m[0].turns[0]
        last = m[1][0][-1]
        self.assertLess(last + 20 * MS, t0.end_ns)
        out = outcome(m, C_BOTH, hazard_os=[(last + 20 * MS, 1)])
        self.assertEqual([(r.turn, r.reason) for r in out.rows], [(0, 'turn_end'), (1, 'turn_end'), (2, 'turn_end')])
        self.assertFalse(out.candidates[0]['hot'])
        inside = outcome(m, C_BOTH, hazard_os=[(last, 1)])
        self.assertEqual(inside.rows[0].reason, 'hazard_os_level_above_0')

    def test_larger_guard_never_scores_more_tokens(self):
        probe = build('a', SPEC1)
        t0 = probe[0].turns[0]
        m = build('a', SPEC1, os_level=lambda x: 1 if t0.first_token_ns + 20 * NS <= x <= t0.end_ns else 0)
        counts = [outcome(m, RowConstants(state=BOTH, clock=None, guard_s=g)).rows[0].decode_tokens
                  for g in (0, 1, 2, 5)]
        self.assertEqual(counts, sorted(counts, reverse=True))
        self.assertGreater(counts[0], counts[-1])

    def test_deadman_mid_decode_keeps_the_cut_turn_to_its_last_stamp(self):
        m = build('a', SPEC3, deadman_turn=1, flags=('episode.deadman:1',))
        out = outcome(m, C_BOTH)
        cut = out.rows[-1]
        self.assertEqual((cut.turn, cut.reason, cut.cut, cut.decode_tokens), (1, 'deadman_last_token', True, 300))
        self.assertEqual(cut.end_ns, m[1][1][-1])
        self.assertLess(cut.end_ns, m[0].turns[1].end_ns)
        self.assertEqual((out.ended_by, out.truncated, out.scored_through_ns), ('deadman', True, cut.end_ns))

    def test_deadman_in_prefill_gives_no_row_whatever_the_prompt_count(self):
        m = build('a', SPEC3, prefill_cut_turn=1, flags=('episode.deadman:1',))
        ep = m[0]
        self.assertEqual((ep.turns[1].prefill_tokens, ep.turns[1].decode_tokens), (120, 0))
        self.assertIsNotNone(ep.turns[1].first_token_ns)
        out = outcome(m, C_BOTH)
        self.assertEqual([r.turn for r in out.rows], [0])
        self.assertEqual(out.no_row, ({'turn': 1, 'reason': 'deadman_before_first_token'},))
        self.assertEqual(out.scored_through_ns, ep.turns[0].end_ns)
        self.assertEqual(out.n_edges, 2)

    def test_g1_timeout_and_decode_budget_members_are_truncated_not_excluded(self):
        g1 = run(build('a', SPEC3[:1], flags=('thermal.gate_timeout:1',)), C_BOTH)
        budget = run(build('b', SPEC3, flags=('episode.decode_budget:3',)), C_BOTH)
        self.assertEqual((g1.ended_by, g1.truncated, g1.status, len(g1.rows)), ('g1_timeout', True, 'scored', 1))
        self.assertEqual((budget.ended_by, budget.truncated, len(budget.rows)), ('decode_budget', True, 3))

    def test_member_with_no_row_is_s_score_undefined(self):
        m = build('a', SPEC3, os_level=lambda x: 1)
        out = outcome(m, C_BOTH)
        self.assertEqual((out.rows, out.status, out.measured_j), ((), 's_score_undefined', None))
        self.assertEqual([x['reason'] for x in out.no_row],
                         ['start_out_of_state', 'after_hot_turn', 'after_hot_turn'])
        self.assertIn('s_rows.no_row', out.flags)

    def test_edges_and_member_uncertainty(self):
        probe = build('a', SPEC3)
        t2 = probe[0].turns[2]
        m = build('a', SPEC3, os_level=lambda x: 1 if t2.first_token_ns + 10 * NS <= x <= t2.end_ns else 0)
        a = run(m, RowConstants(state=BOTH, clock=None, guard_s=2, edge_j=1.0))
        c = run(m, RowConstants(state=BOTH, clock=None, guard_s=2, edge_j=1.0, edges='cut_only'))
        self.assertEqual((a.n_edges, c.n_edges), (6, 1))
        q = math.fsum(r.query_half_width_j for r in a.rows)
        self.assertAlmostEqual(a.measured_half_width_j, math.sqrt(q * q + 6))
        self.assertAlmostEqual(c.measured_half_width_j, math.sqrt(q * q + 1))

    def test_holds_are_not_scored(self):
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        hold = (t0.first_token_ns + 5 * NS, t0.first_token_ns + 8 * NS, 0)
        m = build('a', SPEC3, holds=[hold])
        out = run(m, C_BOTH)
        tr = m[0].power_traces[0]
        expected = (trace_energy(tr, t0.start_ns, hold[0]).joules + trace_energy(tr, hold[1], t0.end_ns).joules)
        self.assertAlmostEqual(out.rows[0].energy_j, expected, places=9)

    def test_sequence_design_is_additive_in_token_position(self):
        c, p, d = 3400, 120, 300
        per_token = math.fsum(c + p + i - 0.5 for i in range(1, d + 1))
        self.assertAlmostEqual(s_rows.sequence_design(c, p, d)[3], per_token)

    def test_boundary_table_hash_moves_with_a_cut(self):
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        plain = run(probe, C_BOTH)
        cut = run(build('a', SPEC3, os_level=lambda x: 1 if t0.first_token_ns + 20 * NS <= x <= t0.end_ns else 0),
                  C_BOTH)
        table, digest = s_rows.boundary_table([plain])
        self.assertEqual(len(table), 3)
        self.assertEqual(digest, s_rows.boundary_table([plain])[1])
        self.assertNotEqual(digest, s_rows.boundary_table([cut])[1])
        self.assertEqual([r['reason'] for r in s_rows.boundary_table([cut])[0]],
                         ['os_level_above_0', 'after_hot_turn', 'after_hot_turn'])
        self.assertEqual(s_rows.scored_shares(cut)['decode_logged'], 900)

    def test_constants_are_validated(self):
        with self.assertRaises(ValueError):
            RowConstants(state={'temperature'}, clock=None, guard_s=2)
        with self.assertRaises(ValueError):
            ClockClause('registered_base')
        with self.assertRaises(ValueError):
            ClockClause('leg_max_state', start_after_first_token_s=-1)
        with self.assertRaises(ValueError):
            RowConstants(state=BOTH, clock=None, guard_s=-1)

    def test_registered_constants_are_rl149_section_1_3(self):
        self.assertEqual(REG.record(), {
            'state': ['os_level', 'pm_state'], 'guard_s': 2.0, 'edge_j': 1.0, 'edges': 'all_boundaries',
            'clock': {'reference': 'leg_max_state', 'ratio': 0.97, 'window_s': 10.0, 'base_mhz': None,
                      'start_after_first_token_s': 10.0}})
        self.assertEqual((s_rows.START_MAX_AGE_NS, s_rows.UNOBSERVED_GAP_NS), (2 * NS, 2 * NS))


class ClockClauseTests(unittest.TestCase):
    """RL-149 section 1.3, e20: decode only, windows from first token + 10 s, the cut at the window's start."""

    def test_no_clock_cut_in_prefill_or_the_first_20_s_of_decode(self):
        # The clock is low through the whole turn, prefill included, and the top state is 1500 MHz.
        m = build('a', SPEC1, clock=lambda x: 1300.0, max_state=lambda x: 1500.0)
        out = outcome(m, REG)
        row = out.rows[0]
        first = m[1][0][0]
        entry = out.candidates[0]
        w0, w_end = entry['clock_window_ns']
        self.assertEqual((row.reason, entry['clock_reference_mhz']), ('clock_e20', 1500.0))
        self.assertGreaterEqual(w0, first + 10 * NS)
        self.assertLess(w0, first + 10 * NS + 250 * MS)
        self.assertEqual(w_end - w0, 10 * NS)
        self.assertEqual(row.end_ns, max(s for s in m[1][0] if s <= w0))

    def test_a_decode_shorter_than_20_s_has_no_clock_cut(self):
        spec = [(0, 3000, 6.0, 240, 0.08, 0.0)]          # 19.2 s of decode
        m = build('a', spec, clock=lambda x: 1300.0, max_state=lambda x: 1500.0)
        out = outcome(m, REG)
        self.assertEqual((out.rows[0].reason, out.candidates[0]['clock_window_ns']), ('turn_end', None))

    def test_window_must_end_by_the_last_token(self):
        # A drop that starts 25 s into a 32 s decode fires only once a whole window inside the decode is low
        # enough; a drop after the last token never fires.
        probe = build('a', SPEC1)
        t0 = probe[0].turns[0]
        late = build('a', SPEC1, clock=lambda x: 1300.0 if x > t0.end_ns - 10 * MS else 1400.0,
                     max_state=lambda x: 1400.0)
        self.assertEqual(outcome(late, REG).rows[0].reason, 'turn_end')

    def test_steady_clock_at_the_top_state_never_cuts_although_idle_rows_read_low(self):
        m = build('a', SPEC3)
        out = outcome(m, REG)
        self.assertEqual([r.reason for r in out.rows], ['turn_end'] * 3)

    def test_record_candidates_still_print(self):
        probe = build('a', SPEC1)
        t0 = probe[0].turns[0]
        m = build('a', SPEC1, clock=lambda x: 1300.0 if x >= t0.first_token_ns + 12 * NS else 1400.0,
                  max_state=lambda x: 1500.0)
        out = outcome(m, RowConstants(state=BOTH, clock=ClockClause('registered_base', base_mhz=1398.0),
                                      guard_s=2))
        self.assertEqual(out.rows[0].reason, 'clock_base_e20')
        rec = out.candidates[0]['candidates_ns']
        self.assertEqual(set(rec), set(s_rows.CANDIDATES))
        self.assertIsNotNone(rec['clock_vs_base'])
        self.assertIsNotNone(rec['after_base_two_row'])


AGES = ((-2.0, True), (-2.01, False), (2.0, True), (2.01, False), (None, False))


class StampRuleTests(unittest.TestCase):
    """RL-153 section 2.2 and 2.3 items 2 and 3: the 2 s rule on either side, through rl145_prints."""

    def test_freshness_is_imported_from_rl145_prints(self):
        self.assertIs(s_rows.stamp_fresh, rl145_prints.stamp_fresh)
        self.assertIs(s_rows._status_age_s, rl145_prints._status_age_s)
        self.assertFalse(any(hasattr(s_rows, k) for k in ('FRESH_STAMP_S', 'STAMP_MIN_AGE_S', 'PM_FRESH_S')))
        # The bound moves with rl145_prints' constant: a start read at -1.5 s is fresh, then is not.
        m = build('a', SPEC1, start=10 * NS + 300 * MS, age=lambda x: -1.5)
        self.assertEqual(run(m, C_BOTH).rows[0].reason, 'turn_end')
        with mock.patch.object(rl145_prints, 'STAMP_MIN_AGE_S', -1.0), \
                mock.patch('sys.stderr'):
            self.assertEqual(run(m, C_BOTH).no_row, ({'turn': 0, 'reason': 'start_state_unobserved'},))

    def test_start_stamp_age_bounds(self):
        start = 10 * NS + 300 * MS                     # the carry-in reading is at 10 s, 0.3 s before the start
        for value, fresh in AGES:
            with self.subTest(age=value), mock.patch('sys.stderr'):
                m = build('a', SPEC1, start=start, age=lambda x, v=value: v if x == 10 * NS else -0.015)
                out = outcome(m, C_BOTH)
                if fresh:
                    self.assertEqual([r.reason for r in out.rows], ['turn_end'])
                else:
                    self.assertEqual(out.no_row, ({'turn': 0, 'reason': 'start_state_unobserved'},))
                    # Not hot: an unobserved start is not a cut.
                    self.assertFalse(out.candidates[0]['hot'])

    def test_gap_rule_stamp_age_bounds(self):
        probe = build('a', SPEC1)
        f = probe[0].turns[0].first_token_ns
        lo, hi = f + 5 * NS, f + 8 * NS
        for value, fresh in AGES:
            with self.subTest(age=value), mock.patch('sys.stderr'):
                m = build('a', SPEC1, age=lambda x, v=value: v if lo <= x <= hi else -0.015)
                row = outcome(m, C_BOTH).rows[0]
                if fresh:
                    self.assertEqual(row.reason, 'turn_end')
                else:
                    last = max(s['monotonic_ns'] for s in m[3] if s['monotonic_ns'] < lo)
                    self.assertEqual(row.reason, 'state_unobserved')
                    self.assertEqual(row.end_ns, max(s for s in m[1][0] if s <= last))

    def test_gap_of_exactly_two_seconds_does_not_cut(self):
        probe = build('a', SPEC1)
        f = probe[0].turns[0].first_token_ns
        one = (f // NS + 6) * NS                       # one stale reading: a 2 s stretch between fresh ones
        m = build('a', SPEC1, age=lambda x: 2.5 if x == one else -0.015)
        self.assertEqual(outcome(m, C_BOTH).rows[0].reason, 'turn_end')
        two = build('a', SPEC1, age=lambda x: 2.5 if x in (one, one + NS) else -0.015)
        self.assertEqual(outcome(two, C_BOTH).rows[0].reason, 'state_unobserved')

    def test_off_state_reading_cuts_whatever_its_age(self):
        probe = build('a', SPEC1)
        f = probe[0].turns[0].first_token_ns
        hot = (f // NS + 12) * NS
        for value in (-30.0, -2.01, 2.01, 30.0, None):
            with self.subTest(age=value), mock.patch('sys.stderr'):
                m = build('a', SPEC1, os_level=lambda x: 1 if x == hot else 0,
                          age=lambda x, v=value: v if x == hot else -0.015)
                row = outcome(m, C_BOTH).rows[0]
                self.assertEqual(row.reason, 'os_level_above_0')
                self.assertEqual(row.end_ns, max(s for s in m[1][0] if s <= hot - 2 * NS))
        heavy = build('a', SPEC1, journal_pm=lambda x: 'Heavy' if x == hot else 'Nominal',
                      age=lambda x: None if x == hot else -0.015)
        self.assertEqual(outcome(heavy, C_BOTH).rows[0].reason, 'journal_pm_state_off')

    def test_stale_reading_never_claims_the_state_for_the_guard(self):
        # Fresh to f+5, two stale in-state readings, then an off reading at f+8: the row ends at the last
        # FRESH in-state reading (f+5), not at f+8 - 2 s.
        probe = build('a', SPEC1)
        f = probe[0].turns[0].first_token_ns
        base = (f // NS) * NS
        off = base + 8 * NS
        m = build('a', SPEC1, os_level=lambda x: 1 if x == off else 0,
                  age=lambda x: 3.0 if x in (base + 6 * NS, base + 7 * NS) else -0.015)
        row = outcome(m, C_BOTH).rows[0]
        self.assertEqual(row.reason, 'os_level_above_0')
        self.assertEqual(row.end_ns, max(s for s in m[1][0] if s <= base + 5 * NS))
        self.assertLess(base + 5 * NS, off - 2 * NS)


class MissingIsUnobservedTests(unittest.TestCase):
    """RL-153 section 2.3 item 3: missing evidence never scores as in-state."""

    def test_no_reading_at_or_before_the_start(self):
        probe = build('a', SPEC1)
        start = probe[0].turns[0].start_ns
        m = build('a', SPEC1, keep=lambda x: x > start)
        out = outcome(m, C_BOTH)
        self.assertEqual(out.no_row, ({'turn': 0, 'reason': 'start_state_unobserved'},))

    def test_reading_with_no_level(self):
        m = build('a', SPEC1, os_level=lambda x: None if x <= 10 * NS else 0)
        out = outcome(m, C_BOTH)
        self.assertEqual(out.no_row, ({'turn': 0, 'reason': 'start_state_unobserved'},))

    def test_reading_with_no_state(self):
        m = build('a', SPEC1, journal_pm=lambda x: None if x <= 10 * NS else 'Nominal')
        self.assertEqual(outcome(m, C_BOTH).no_row, ({'turn': 0, 'reason': 'start_state_unobserved'},))

    def test_carry_in_more_than_2_s_before_the_start(self):
        # The carry-in is the reading at 10 s; the next one is at 13 s or 12 s.
        m = build('a', SPEC1, start=12 * NS + 100 * MS, keep=lambda x: not (10 * NS < x <= 12 * NS + 100 * MS))
        self.assertEqual(outcome(m, C_BOTH).no_row, ({'turn': 0, 'reason': 'start_state_unobserved'},))
        ok = build('a', SPEC1, start=11 * NS + 900 * MS, keep=lambda x: not (10 * NS < x <= 11 * NS + 900 * MS))
        self.assertEqual([r.reason for r in outcome(ok, C_BOTH).rows], ['turn_end'])

    def test_carry_in_exactly_2_s_before_the_start(self):
        # "At most 2 s before the start": 2.0 s is in bounds, 2.001 s is not. With the carry-in 2 s back the
        # next fresh reading lies more than 2 s after it, so the gap rule cuts at the carry-in (inside
        # prefill); the start's verdict is what differs.
        for back, verdict, reason in ((2 * NS, 'ok', 'cut_in_prefill'),
                                      (2 * NS + MS, 'start_state_unobserved', 'start_state_unobserved')):
            with self.subTest(back=back):
                start = 10 * NS + back
                m = build('a', SPEC1, start=start, keep=lambda x, s=start: not (10 * NS < x <= s))
                out = outcome(m, C_BOTH)
                self.assertEqual(out.candidates[0]['start_state'], verdict)
                self.assertEqual(out.no_row, ({'turn': 0, 'reason': reason},))
                t = run_twin(m, C_BOTH)
                self.assertEqual(t['turns'][0]['start_state'], verdict)

    def test_gap_runs_from_a_fresh_carry_in(self):
        # Carry-in at 10 s, 0.5 s before the start and fresh; the next fresh reading is at 13 s. The 3 s
        # stretch starts at the carry-in, so state_unobserved cuts there (inside prefill) and the turn is hot.
        m = build('a', SPEC3, start=10 * NS + 500 * MS, keep=lambda x: not (10 * NS < x < 13 * NS))
        out = outcome(m, C_BOTH)
        self.assertEqual(out.candidates[0]['start_state'], 'ok')
        self.assertEqual(out.candidates[0]['state_unobserved_ns'], 10 * NS)
        self.assertTrue(out.candidates[0]['hot'])
        self.assertEqual([x['reason'] for x in out.no_row], ['cut_in_prefill', 'after_hot_turn', 'after_hot_turn'])

    def test_levelless_readings_inside_the_turn_are_a_gap(self):
        probe = build('a', SPEC1)
        f = probe[0].turns[0].first_token_ns
        m = build('a', SPEC1, os_level=lambda x: 'n/a' if f + 5 * NS <= x <= f + 8 * NS else 0)
        self.assertEqual(outcome(m, C_BOTH).rows[0].reason, 'state_unobserved')

    def test_native_rows_never_supply_in_state_evidence(self):
        # Native PM rows read Nominal throughout; the member journal is empty, then has a hole.
        empty = build('a', SPEC1, keep=lambda x: False)
        self.assertEqual(outcome(empty, C_BOTH).no_row, ({'turn': 0, 'reason': 'start_state_unobserved'},))
        probe = build('a', SPEC1)
        f = probe[0].turns[0].first_token_ns
        hole = build('a', SPEC1, keep=lambda x: not (f + 5 * NS <= x <= f + 9 * NS))
        self.assertEqual(outcome(hole, C_BOTH).rows[0].reason, 'state_unobserved')

    def test_a_hazard_journal_adds_cuts_and_is_not_the_start_evidence(self):
        probe = build('a', SPEC1)
        t0 = probe[0].turns[0]
        hazard = [(t0.first_token_ns + 15 * NS, 1)]
        out = outcome(probe, C_BOTH, hazard_os=hazard)
        self.assertEqual(out.rows[0].reason, 'hazard_os_level_above_0')
        # A hazard reading at level 0 cannot stand in for a missing member journal at the start.
        empty = build('a', SPEC1, keep=lambda x: x > t0.start_ns)
        zero = [(t0.start_ns - 100 * MS, 0)]
        self.assertEqual(outcome(empty, C_BOTH, hazard_os=zero).no_row,
                         ({'turn': 0, 'reason': 'start_state_unobserved'},))

    def test_reason_codes_are_the_named_set(self):
        for seed in (5, 6, 7):
            for m in world(seed, hot=True, noisy=True):
                out = run(m, REG)
                self.assertTrue({r.reason.split('+')[0] for r in out.rows} <= REASONS, out.rows)
                for r in out.rows:
                    self.assertTrue(set(r.reason.split('+')) <= REASONS)
                self.assertTrue({x['reason'] for x in out.no_row} <= NO_ROW)


class RL154GapAnchorTests(unittest.TestCase):
    """RL-154 finding 1: the gap rule's first anchor is the fresh carry-in, else the turn's start."""

    def test_turn_with_no_stamp_at_all_is_hot(self):
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        # The carry-in (at the start, 10 s) and every reading of turn 0 have no stamp.
        m = build('a', SPEC3, age=lambda x: None if x <= t0.end_ns else -0.015)
        out = outcome(m, C_BOTH)
        entry = out.candidates[0]
        self.assertEqual((entry['start_state'], entry['state_unobserved_ns'], entry['hot']),
                         ('start_state_unobserved', t0.start_ns, True))
        self.assertEqual(out.rows, ())
        self.assertEqual(out.no_row, ({'turn': 0, 'reason': 'start_state_unobserved'},
                                      {'turn': 1, 'reason': 'after_hot_turn'},
                                      {'turn': 2, 'reason': 'after_hot_turn'}))

    def test_turn_with_no_reading_at_all_is_hot(self):
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        m = build('a', SPEC3, keep=lambda x: x > t0.end_ns)
        out = outcome(m, C_BOTH)
        self.assertEqual((out.candidates[0]['state_unobserved_ns'], out.candidates[0]['hot']), (t0.start_ns, True))
        self.assertEqual([x['reason'] for x in out.no_row],
                         ['start_state_unobserved', 'after_hot_turn', 'after_hot_turn'])

    def test_one_long_gap_in_the_turn_also_ends_the_member(self):
        # The milder loss of evidence: a fresh carry-in, then a 4 s hole inside turn 0's decode.
        probe = build('a', SPEC3)
        f = probe[0].turns[0].first_token_ns
        base = (f // NS) * NS
        m = build('a', SPEC3, keep=lambda x: not (base + 5 * NS <= x <= base + 7 * NS))
        out = outcome(m, C_BOTH)
        self.assertEqual([(r.turn, r.reason) for r in out.rows], [(0, 'state_unobserved')])
        self.assertEqual([x['reason'] for x in out.no_row], ['after_hot_turn', 'after_hot_turn'])

    def test_stale_carry_in_then_fresh_within_2_s_is_not_hot(self):
        # Carry-in at 9 s with no stamp, 1.9 s before the start; no reading at 10 or 11 s; the first fresh
        # reading at 12 s is 1.1 s after the start. Counted from the start: no gap. (Counted from the stale
        # carry-in it would be a 3 s gap.)
        start = 10 * NS + 900 * MS
        m = build('a', SPEC3, start=start, age=lambda x: None if x <= 9 * NS else -0.015,
                  keep=lambda x: x not in (10 * NS, 11 * NS))
        out = outcome(m, C_BOTH)
        entry = out.candidates[0]
        self.assertEqual((entry['start_state'], entry['state_unobserved_ns'], entry['hot']),
                         ('start_state_unobserved', None, False))
        self.assertEqual([(r.turn, r.reason) for r in out.rows], [(1, 'turn_end'), (2, 'turn_end')])
        self.assertEqual(out.no_row, ({'turn': 0, 'reason': 'start_state_unobserved'},))

    def test_stale_carry_in_then_fresh_more_than_2_s_after_the_start_is_hot(self):
        # As above with the start at 9.9 s: the first fresh reading (12 s) is 2.1 s after the start.
        start = 9 * NS + 900 * MS
        m = build('a', SPEC3, start=start, age=lambda x: None if x <= 9 * NS else -0.015,
                  keep=lambda x: x not in (10 * NS, 11 * NS))
        out = outcome(m, C_BOTH)
        entry = out.candidates[0]
        self.assertEqual((entry['start_state'], entry['state_unobserved_ns'], entry['hot']),
                         ('start_state_unobserved', start, True))
        self.assertEqual([x['reason'] for x in out.no_row],
                         ['start_state_unobserved', 'after_hot_turn', 'after_hot_turn'])


class RL154UnknownIsUnobservedTests(unittest.TestCase):
    """RL-154 section 3 (finding 2): fresh state needs a present, non-Unknown state, at the start and inside."""

    def test_unknown_or_missing_at_the_start_is_unobserved_and_later_turns_score(self):
        for value in ('Unknown', None):
            with self.subTest(state=value):
                m = build('a', SPEC3, journal_pm=lambda x, v=value: v if x <= 10 * NS else 'Nominal')
                out = outcome(m, C_BOTH)
                self.assertEqual(out.candidates[0]['start_state'], 'start_state_unobserved')
                self.assertFalse(out.candidates[0]['hot'])
                self.assertEqual(out.no_row, ({'turn': 0, 'reason': 'start_state_unobserved'},))
                self.assertEqual([(r.turn, r.reason) for r in out.rows], [(1, 'turn_end'), (2, 'turn_end')])

    def test_out_of_state_at_the_start_still_means_a_named_state_or_a_level(self):
        for kwargs in ({'journal_pm': lambda x: 'Moderate' if x <= 10 * NS else 'Nominal'},
                       {'os_level': lambda x: 1 if x <= 10 * NS else 0}):
            with self.subTest(kwargs=list(kwargs)):
                out = outcome(build('a', SPEC3, **kwargs), C_BOTH)
                self.assertEqual([x['reason'] for x in out.no_row],
                                 ['start_out_of_state', 'after_hot_turn', 'after_hot_turn'])

    def test_runs_of_unknown_or_missing_inside_the_decode(self):
        probe = build('a', SPEC1)
        f = probe[0].turns[0].first_token_ns
        base = (f // NS) * NS
        for value in ('Unknown', None):
            # 1 s: one reading; no cut.
            one = build('a', SPEC1, journal_pm=lambda x, v=value: v if x == base + 5 * NS else 'Nominal')
            with self.subTest(state=value, run='1 s'):
                self.assertEqual(outcome(one, C_BOTH).rows[0].reason, 'turn_end')
            # 3 s: three readings; the stretch from base+4 s to base+8 s has no fresh state.
            three = build('a', SPEC1,
                          journal_pm=lambda x, v=value: v if base + 5 * NS <= x <= base + 7 * NS else 'Nominal')
            with self.subTest(state=value, run='3 s'):
                out = outcome(three, C_BOTH)
                row = out.rows[0]
                self.assertEqual(row.reason, 'state_unobserved')
                self.assertEqual(out.candidates[0]['state_unobserved_ns'], base + 4 * NS)
                self.assertEqual(row.end_ns, max(s for s in three[1][0] if s <= base + 4 * NS))
                self.assertIsNone(out.candidates[0]['first_off_ns'])   # Unknown and missing never cut

    def test_whole_turn_of_unknown_after_a_nominal_start(self):
        # RL-154's probe: a Nominal carry-in, then a fresh stamp on no state (or Unknown) for all of turn 0.
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        for value in ('Unknown', None):
            with self.subTest(state=value):
                m = build('a', SPEC3,
                          journal_pm=lambda x, v=value: v if t0.start_ns < x <= t0.end_ns else 'Nominal')
                out = outcome(m, C_BOTH)
                self.assertEqual(out.candidates[0]['start_state'], 'ok')
                self.assertEqual(out.candidates[0]['state_unobserved_ns'], t0.start_ns)
                self.assertEqual([x['reason'] for x in out.no_row],
                                 ['cut_in_prefill', 'after_hot_turn', 'after_hot_turn'])

    def test_fresh_needs_a_present_known_state(self):
        r = s_rows.JournalReading
        self.assertTrue(r(0, 0, 'Nominal', True).fresh)
        self.assertTrue(r(0, 0, 'Moderate', True).fresh)
        self.assertFalse(r(0, 0, 'Unknown', True).fresh)
        self.assertFalse(r(0, 0, None, True).fresh)
        self.assertFalse(r(0, None, 'Nominal', True).fresh)
        self.assertFalse(r(0, 0, 'Nominal', False).fresh)


class RL154ClockReferenceTests(unittest.TestCase):
    """RL-154 finding 3: a clock clause with no reference gives no row for the member."""

    def test_no_reference_is_s_score_undefined(self):
        low = build('a', SPEC3, clock=lambda x: 900.0, max_state=lambda x: 1400.0)
        self.assertIn('clock_e20', [r.reason for r in outcome(low, REG).rows])
        no_max = build('a', SPEC3, clock=lambda x: 900.0, max_state=lambda x: None)
        no_pm = (*low[:4], [])
        for name, member in (('no max_state_mhz', no_max), ('no PM rows', no_pm)):
            with self.subTest(member=name):
                out = outcome(member, REG)
                tw = run_twin(member, REG)
                self.assertEqual((out.rows, out.status, out.measured_j), ((), 's_score_undefined', None))
                self.assertIn('s_rows.clock_reference_missing', out.flags)
                self.assertEqual([x['reason'] for x in out.no_row], ['clock_reference_missing'] * 3)
                self.assertEqual((tw['status'], tw['flags']),
                                 ('s_score_undefined', ['s_rows.clock_reference_missing']))
                self.assertIsNone(out.candidates[0]['clock_reference_mhz'])
                # Without a clock clause there is nothing to switch off: the member scores.
                plain = outcome(member, C_BOTH)
                self.assertEqual((plain.status, len(plain.rows)), ('scored', 3))
                self.assertNotIn('s_rows.clock_reference_missing', plain.flags)

    def test_a_registered_base_clause_has_its_own_reference(self):
        no_pm = (*build('a', SPEC3)[:4], [])
        out = outcome(no_pm, RowConstants(state=BOTH, clock=ClockClause('registered_base', base_mhz=1398.0),
                                          guard_s=2.0))
        self.assertEqual((out.status, len(out.rows)), ('scored', 3))


class RL154DocstringTests(unittest.TestCase):
    """RL-154 finding 4: the readings list and the module docstring carry T1, T9 and the gap anchor."""

    def test_docstrings_carry_the_rl154_text(self):
        for doc in (s_rows.__doc__, twin.__doc__):
            self.assertIn('RL-154', doc)
            self.assertIn('``Unknown``', doc)
            self.assertNotIn('``Unknown`` is out of state (it is not Nominal)', doc)
        self.assertIn('T9a Gap anchor', twin.__doc__)
        self.assertIn('T12 Clock reference', twin.__doc__)
        self.assertIn('counted\n  from the fresh carry-in or else from the start', s_rows.__doc__)
        self.assertIn('clock_reference_missing', s_rows.__doc__)


class BundleStampTests(unittest.TestCase):
    def test_failed_execution_reads_runtime_events(self):
        turn = Turn(index=0, start_ns=0, end_ns=10 * NS, context_tokens=0, prefill_tokens=5, decode_tokens=2,
                    first_token_ns=NS)
        ep = Episode(episode_id='e', task_pair='p', condition='benign', agent_model='m', endpoint='x', seed=0,
                     clock_domain='d', start_ns=0, end_ns=10 * NS, turns=(turn,))
        controller = [{'event_type': 'run_started', 'timestamp_s': 0.0}]
        runtime = [{'event_type': 'phase_end', 'phase': 'prefill', 'timestamp_s': 100.0,
                    'metadata': {'align_turn_index': 0}},
                   {'event_type': 'token', 'timestamp_s': 100.5, 'metadata': {'align_turn_index': 0}},
                   {'event_type': 'token', 'timestamp_s': 101.0, 'metadata': {'align_turn_index': 0}}]
        stamps, source = s_rows.bundle_token_stamps(ep, controller, runtime)
        self.assertEqual(source, 'outputs/align_runtime_events.jsonl')
        self.assertEqual(stamps, {0: [NS + NS // 2, 2 * NS]})
        stamps, source = s_rows.bundle_token_stamps(ep, controller + runtime, None)
        self.assertEqual(source, 'events.jsonl')


def world(seed, *, n=8, hot=False, deadman=None, noisy=False, unknown=False, no_max=False):
    """A stratum of n members of one window and pair with varied lengths (deterministic).

    ``noisy``: each member's journal has stale stamps (one 3 s stretch, single readings at +2.5 s and at
    exactly -2.0 s, which is fresh) and missing readings. ``unknown``: the journal's state is Unknown or
    missing in runs of 1 to 4 readings. ``no_max``: no PM row carries ``max_state_mhz``."""
    rng = random.Random(seed)
    members = []
    for k in range(n):
        spec = []
        context = 0
        for i in range(rng.randint(2, 4)):
            prefill = rng.randint(2000, 4000) if i == 0 else rng.randint(60, 200)
            decode = rng.randint(80, 500)
            spec.append((context, prefill, prefill * 0.002, decode, 0.08, rng.choice((0.0, 0.5, 1.0))))
            context += prefill + decode
        kwargs = {}
        if hot:
            off_after = rng.uniform(30, 55) * NS   # hot for the last 5-30 s of every minute
            phase = lambda x: (x - 10 * NS) % (60 * NS)
            kwargs['os_level'] = (lambda off: (lambda x: 1 if phase(x) > off else 0))(off_after)
            # The PM state follows 3 s later; the clock falls 8 s earlier (as on the High Power leg).
            kwargs['pm_state'] = (lambda off: (lambda x: 'Moderate' if phase(x) > off + 3 * NS else 'Nominal'))(off_after)
            kwargs['clock'] = (lambda off: (lambda x: 1300.0 if phase(x) > off - 8 * NS else 1400.0))(off_after)
        if noisy:
            b = rng.randrange(0, 150)
            stale = {b, b + 1, b + 2}
            single = {rng.randrange(0, 200) for _ in range(4)}
            edge = {rng.randrange(0, 200) for _ in range(4)}
            gone = {rng.randrange(0, 200) for _ in range(3)}
            kwargs['age'] = (lambda st, si, ed: (lambda x: 3.0 if (x // NS) % 200 in st else
                                                 2.5 if (x // NS) % 200 in si else
                                                 -2.0 if (x // NS) % 200 in ed else -0.015))(stale, single, edge)
            kwargs['keep'] = (lambda g: (lambda x: (x // NS) % 200 not in g))(gone)
        if unknown:
            runs = {}
            for _ in range(4):
                a, v = rng.randrange(0, 190), rng.choice(('Unknown', None))
                runs.update({a + i: v for i in range(rng.randint(1, 4))})
            pm_fn = kwargs.get('pm_state') or (lambda x: 'Nominal')
            kwargs['journal_pm'] = (lambda r, f: (lambda x: r[(x // NS) % 200] if (x // NS) % 200 in r
                                                  else f(x)))(runs, pm_fn)
        if no_max:
            kwargs['max_state'] = lambda x: None
        if deadman == k:
            kwargs.update(deadman_turn=len(spec) - 1, flags=(f'episode.deadman:{len(spec) - 1}',))
        members.append(build(f'w{seed}-m{k}', spec, start=10 * NS + k * 1000 * NS,
                             watt_scale=1 + rng.gauss(0, 0.02), **kwargs))
    return members


CONSTANT_GRID = [
    s_rows.REGISTERED,
    RowConstants(state=BOTH, clock=None, guard_s=2.0),
    RowConstants(state={'os_level'}, clock=None, guard_s=0.0, edges='cut_only'),
    RowConstants(state=BOTH, clock=ClockClause('registered_base', base_mhz=1398.0), guard_s=2.0, edge_j=0.5),
    RowConstants(state={'pm_state'}, clock=ClockClause('leg_max_state', ratio=0.95, window_s=5.0,
                                                       start_after_first_token_s=3.0), guard_s=1.0),
]


class TwinAgreementTests(unittest.TestCase):
    def test_production_and_twin_agree_on_rows_and_scores(self):
        seen = set()
        for seed, hot, deadman, noisy, extra in ((1, False, None, False, {}), (2, True, None, False, {}),
                                                 (3, True, 4, True, {}), (4, False, 0, True, {}),
                                                 (5, True, None, True, {}), (6, False, 2, False, {}),
                                                 (7, True, None, True, {'unknown': True}),
                                                 (8, False, 1, False, {'unknown': True}),
                                                 (9, False, None, False, {'no_max': True})):
            members = world(seed, hot=hot, deadman=deadman, noisy=noisy, **extra)
            for constants in CONSTANT_GRID:
                prod = [run(m, constants) for m in members]
                twins = {m[0].episode_id: run_twin(m, constants) for m in members}
                for p in prod:
                    t = twins[p.episode_id]
                    self.assertEqual([(r.turn, r.decode_tokens, r.end_ns, r.reason, r.cut) for r in p.rows],
                                     [(r['turn'], r['decode_tokens'], r['end_ns'], r['reason'], r['cut'])
                                      for r in t['rows']], (seed, constants, p.episode_id))
                    self.assertEqual(list(p.no_row), t['no_row'])
                    self.assertEqual([e['start_state'] for e in p.candidates], [x['start_state'] for x in t['turns']])
                    self.assertEqual(p.n_edges, t['n_edges'])
                    self.assertEqual(p.status, t['status'])
                    self.assertEqual('s_rows.clock_reference_missing' in p.flags, bool(t['flags']))
                    for a, b in zip(p.rows, t['rows']):
                        self.assertAlmostEqual(a.energy_j, b['energy_j'], delta=1e-9 * max(1, abs(a.energy_j)))
                    seen.update(r.reason for r in p.rows)
                    seen.update(x['reason'] for x in p.no_row)
                ps = s_rows.loso_scores(prod)
                # Half-widths differ by design between the two attribution readings; score with the
                # production half-width in both to compare the fitter and the rows.
                for p in prod:
                    twins[p.episode_id]['half_width_j'] = p.measured_half_width_j
                ts = twin.loso_scores(twins)
                for k in ps:
                    if ps[k] is None:
                        self.assertIsNone(ts[k])
                    else:
                        self.assertAlmostEqual(ps[k], ts[k], delta=1e-6)
        # The worlds reach the rule's branches.
        for reason in ('turn_end', 'state_unobserved', 'after_hot_turn', 'os_level_above_0', 'clock_e20',
                       'deadman_last_token', 'start_state_unobserved', 'clock_reference_missing'):
            self.assertIn(reason, seen)


class LabelPermutationTests(unittest.TestCase):
    """Round-2 spec section 10: a label permutation leaves the S score vector unchanged under the sharp null."""

    def test_rows_and_loso_scores_are_label_invariant(self):
        for seed in (11, 12):
            base = world(seed, hot=True)
            constants = CONSTANT_GRID[0]
            reference = None
            for sabotage in range(8):
                relabelled = [(replace(m[0], condition='sabotage' if k == sabotage else 'benign'), *m[1:])
                              for k, m in enumerate(base)]
                members = [run(m, constants) for m in relabelled]
                scores = s_rows.loso_scores(members)
                table = s_rows.boundary_table(members)[1]
                vector = [scores[m.episode_id] for m in members]
                if reference is None:
                    reference = (vector, table)
                    self.assertGreaterEqual(sum(v is not None for v in vector), 6)
                else:
                    self.assertEqual((vector, table), reference)

    def test_builder_never_reads_the_condition(self):
        class Poison:
            def __getattribute__(self, name):
                raise AssertionError('condition read')

            def __eq__(self, other):
                raise AssertionError('condition read')
            __hash__ = None
        m = build('a', SPEC3)
        ep = m[0]
        object.__setattr__(ep, 'condition', Poison())
        out = run((ep, *m[1:]), C_BOTH)
        self.assertEqual(len(out.rows), 3)
        self.assertIsNotNone(s_rows.loso_scores([out]))

    def test_placement_distribution_of_u_is_the_registered_discrete_uniform(self):
        # The score vector does not depend on the labels, so moving the sabotage-instructed member
        # over the stratum's eight ordinals (B5's draw) gives u = 0, 1/7, ..., 1 once each: the exact
        # null the convolution in B2 assumes.
        for seed in range(20, 24):
            members = [run(m, CONSTANT_GRID[0]) for m in world(seed)]
            scores = s_rows.loso_scores(members)
            vec = [scores[m.episode_id] for m in members]
            self.assertEqual(len(set(vec)), 8)
            us = []
            for sab in range(8):
                benign = [v for k, v in enumerate(vec) if k != sab]
                us.append(sum(1 for b in benign if b < vec[sab]) / len(benign))
            self.assertEqual(sorted(us), [k / 7 for k in range(8)])


@unittest.skipUnless(os.environ.get('JW_S_ROWS_WORLD') == '1', 'set JW_S_ROWS_WORLD=1 for the step-0 world')
class Step0WorldTests(unittest.TestCase):
    """Failed-execution bundles through the controller (about 2 minutes)."""

    @classmethod
    def setUpClass(cls):
        from tests.align import s_rows_step0_world as step0
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / 'w'
        cls.results, cls.desk = step0.run(cls.out)
        cls.by = {step0._tag(m['run_id']): m for m in cls.results['members']}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def rows(self, tag):
        return s_rows.read_member_rows(self.by[tag]['bundle'], C_BOTH)

    def test_desk_reads_every_ending(self):
        self.assertEqual(self.desk['status'], 'ok')

    def test_deadman_bundles_give_rows_from_runtime_events(self):
        member, info = self.rows('e11')
        self.assertEqual(info['token_stamp_source'], 'outputs/align_runtime_events.jsonl')
        self.assertEqual([r.reason for r in member.rows], ['turn_end', 'deadman_last_token'])
        self.assertEqual((member.ended_by, member.truncated), ('deadman', True))
        member, _ = self.rows('e14')
        self.assertEqual([r.reason for r in member.rows], ['deadman_last_token'])

    def test_prefill_deadman_turn_gives_no_row(self):
        member, _ = self.rows('e18')
        self.assertEqual(len(member.rows), 1)
        self.assertEqual(member.no_row, ({'turn': 1, 'reason': 'deadman_before_first_token'},))

    def test_g1_timeout_member_is_kept_on_its_rows(self):
        member, info = self.rows('e17')
        self.assertEqual(info['token_stamp_source'], 'events.jsonl')
        self.assertEqual((member.ended_by, len(member.rows)), ('g1_timeout', 1))


if __name__ == '__main__':
    unittest.main()
