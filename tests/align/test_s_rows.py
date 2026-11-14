"""RL-148 desk step 6: reference-state rows on synthetic members, production and twin.

Synthetic only: in-memory episodes, traces, OS readings and PM rows. No bundle,
no measurement, no model. The optional world test (JW_S_ROWS_WORLD=1) drives the
WP22 synthetic world through the controller to build failed-execution bundles.
"""
from __future__ import annotations

from dataclasses import replace
import math
import os
from pathlib import Path
import random
import tempfile
import unittest

from joulewise.align.apple import s_rows
from joulewise.align.apple.s_rows import ClockClause, RowConstants
from joulewise.align.attribution import trace_energy
from joulewise.align.records import Episode, PowerTrace, ToolCall, Turn
from tests.align.twins import s_rows_twin as twin

NS = 1_000_000_000
MS = 1_000_000
BOTH = frozenset({'os_level', 'pm_state'})


def watts_at(t, phases):
    for a, b, w in phases:
        if a <= t < b:
            return w
    return 2.0


def build(eid, spec, *, condition='benign', flags=(), start=10 * NS, os_level=None, pm_state=None,
          clock=None, max_state=None, deadman_turn=None, prefill_cut_turn=None, holds=(), pair='shade/x',
          watt_scale=1.0):
    """One synthetic member. ``spec``: per turn (context, prefill_tokens, prefill_s, decode_tokens, tok_s, tool_s).

    os_level / pm_state / clock / max_state: functions of absolute ns (None: level 0 / Nominal / 1400 MHz).
    deadman_turn: the last turn, cut mid-decode (its finish reason is episode.deadman).
    prefill_cut_turn: the last turn, cut inside prefill (full prompt count, zero decode, first_token_ns = cut).
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
    os_readings = [(x, os_fn(x)) for x in range(start - 5 * NS, end_ns, NS)]
    pm_rows = []
    for a in range(start - 5 * NS, end_ns, 250 * MS):
        b = a + 250 * MS
        busy = any(p <= a < q for p, q, _ in phases[:]) and watts_at(a, phases) > 10
        pm_rows.append({'start_ns': a, 'end_ns': b, 'state': (pm_state or (lambda x: 'Nominal'))(b),
                        'active_ns': (250 * MS) if busy else 10 * MS,
                        'clock_mhz': (clock or (lambda x: 1400.0))(b) if busy else 400.0,
                        'max_state_mhz': (max_state or (lambda x: 1400.0))(b)})
    return ep, stamps, finish, os_readings, pm_rows


SPEC3 = [(0, 3000, 6.0, 400, 0.08, 1.0), (3400, 120, 0.4, 300, 0.08, 1.0), (3820, 90, 0.3, 200, 0.08, 0.0)]


def run(member, constants):
    ep, stamps, finish, os_readings, pm_rows = member
    return s_rows.member_rows(ep, token_stamps=stamps, finish_reasons=finish, os_readings=os_readings,
                              pm_rows=pm_rows, constants=constants)


def run_twin(member, constants):
    ep, stamps, finish, os_readings, pm_rows = member
    clock = None if constants.clock is None else dict(reference=constants.clock.reference,
                                                     ratio=constants.clock.ratio,
                                                     window_s=constants.clock.window_s,
                                                     base_mhz=constants.clock.base_mhz)
    return twin.rows_for(ep, token_stamps=stamps, finish_reasons=finish, os_readings=os_readings,
                         pm_rows=pm_rows, state=constants.state, clock=clock, guard_s=constants.guard_s,
                         edge_j=constants.edge_j, edges=constants.edges)


C_BOTH = RowConstants(state=BOTH, clock=None, guard_s=2.0)


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

    def test_os_cut_snaps_to_the_last_stamp_before_the_guard(self):
        probe = build('a', SPEC3)
        t1 = probe[0].turns[1]
        m = build('a', SPEC3, os_level=lambda x: 1 if t1.first_token_ns + 15 * NS <= x <= t1.end_ns else 0)
        out = run(m, C_BOTH)
        row = next(r for r in out.rows if r.turn == 1)
        reading = min(x for x, v in m[3] if v == 1)
        limit = reading - 2 * NS
        stamps = m[1][1]
        self.assertEqual(row.decode_tokens, sum(1 for s in stamps if s <= limit))
        self.assertEqual(row.end_ns, stamps[row.decode_tokens - 1])
        self.assertEqual((row.reason, row.cut, row.logged_decode_tokens), ('os_first_nonzero', True, 300))
        self.assertAlmostEqual(row.energy_j, trace_energy(m[0].power_traces[0], t1.start_ns, row.end_ns).joules)

    def test_state_definition_is_an_input(self):
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        pm_hot = lambda x: 'Moderate' if t0.first_token_ns + 10 * NS <= x <= t0.end_ns else 'Nominal'
        m = build('a', SPEC3, pm_state=pm_hot)
        self.assertEqual(run(m, RowConstants(state={'pm_state'}, clock=None, guard_s=2)).rows[0].reason,
                         'pm_first_off')
        self.assertEqual(run(m, RowConstants(state={'os_level'}, clock=None, guard_s=2)).rows[0].reason,
                         'turn_end')
        unknown = build('a', SPEC3, pm_state=lambda x: 'Unknown' if x > t0.first_token_ns else None)
        self.assertEqual(run(unknown, C_BOTH).rows[0].reason, 'turn_end')

    def test_turn_starting_off_gives_no_row_and_the_next_turn_still_does(self):
        probe = build('a', SPEC3)
        t0, t1 = probe[0].turns[0], probe[0].turns[1]
        # Hot from late in turn 0 until 0.5 s after turn 1 started (the carry-in reading is hot).
        level = lambda x: 1 if t0.end_ns - 3 * NS <= x <= t1.start_ns + 500 * MS else 0
        m = build('a', SPEC3, os_level=level)
        out = run(m, C_BOTH)
        self.assertEqual([r.turn for r in out.rows], [0, 2])
        self.assertEqual(out.no_row, ({'turn': 1, 'reason': 'cut_before_first_token:os_first_nonzero'},))

    def test_cut_inside_prefill_gives_no_row(self):
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        m = build('a', SPEC3, os_level=lambda x: 1 if t0.start_ns + 3 * NS <= x <= t0.end_ns else 0)
        out = run(m, C_BOTH)
        self.assertEqual(out.no_row[0]['reason'], 'cut_before_first_token:os_first_nonzero')
        self.assertEqual([r.turn for r in out.rows], [1, 2])

    def test_clock_clause_base_and_leg_max_and_turn_start_clip(self):
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        drop = t0.first_token_ns + 12 * NS
        m = build('a', SPEC3, clock=lambda x: 1300.0 if drop <= x <= t0.end_ns else 1400.0,
                  max_state=lambda x: 1500.0)
        none = run(m, C_BOTH)
        self.assertEqual(none.rows[0].reason, 'turn_end')
        base = run(m, RowConstants(state=BOTH, clock=ClockClause('registered_base', base_mhz=1398.0), guard_s=2))
        self.assertEqual(base.rows[0].reason, 'clock_vs_base')
        self.assertLess(base.rows[0].decode_tokens, 400)
        # Against the leg's highest state (1500 MHz), 1400 MHz is already under 0.97: the clause fires
        # as soon as it is evaluated, one full window (10 s) into the turn.
        leg = run(m, RowConstants(state=BOTH, clock=ClockClause('leg_max_state'), guard_s=0))
        self.assertEqual(leg.rows[0].reason, 'clock_vs_leg_max')
        self.assertLessEqual(leg.rows[0].end_ns, t0.start_ns + 10 * NS)
        self.assertGreater(leg.rows[0].end_ns, t0.start_ns + 10 * NS - 300 * MS)
        # A steady clock at base never cuts, although idle gate rows before each turn read 400 MHz.
        steady = run(build('a', SPEC3), RowConstants(state=BOTH, clock=ClockClause('registered_base',
                                                                                    base_mhz=1398.0), guard_s=2))
        self.assertEqual([r.reason for r in steady.rows], ['turn_end'] * 3)
        rec = base.candidates[0]['candidates_ns']
        self.assertEqual(set(rec), set(s_rows.CANDIDATES))
        self.assertIsNotNone(rec['clock_vs_base'])
        self.assertIsNotNone(rec['after_base_two_row'])

    def test_larger_guard_never_scores_more_tokens(self):
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        m = build('a', SPEC3, os_level=lambda x: 1 if t0.first_token_ns + 20 * NS <= x <= t0.end_ns else 0)
        counts = [run(m, RowConstants(state=BOTH, clock=None, guard_s=g)).rows[0].decode_tokens for g in (0, 1, 2, 5)]
        self.assertEqual(counts, sorted(counts, reverse=True))
        self.assertGreater(counts[0], counts[-1])

    def test_deadman_mid_decode_keeps_the_cut_turn_to_its_last_stamp(self):
        m = build('a', SPEC3, deadman_turn=1, flags=('episode.deadman:1',))
        out = run(m, C_BOTH)
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
        out = run(m, C_BOTH)
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
        out = run(m, C_BOTH)
        self.assertEqual((out.rows, out.status, out.measured_j), ((), 's_score_undefined', None))
        self.assertIn('s_rows.no_row', out.flags)

    def test_edges_and_member_uncertainty(self):
        probe = build('a', SPEC3)
        t0 = probe[0].turns[0]
        m = build('a', SPEC3, os_level=lambda x: 1 if t0.first_token_ns + 20 * NS <= x <= t0.end_ns else 0)
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
        self.assertEqual(s_rows.scored_shares(cut)['decode_logged'], 900)

    def test_constants_are_validated(self):
        with self.assertRaises(ValueError):
            RowConstants(state={'temperature'}, clock=None, guard_s=2)
        with self.assertRaises(ValueError):
            ClockClause('registered_base')
        with self.assertRaises(ValueError):
            RowConstants(state=BOTH, clock=None, guard_s=-1)


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


def world(seed, *, n=8, hot=False, deadman=None):
    """A stratum of n members of one window and pair with varied lengths (deterministic)."""
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
        if deadman == k:
            kwargs.update(deadman_turn=len(spec) - 1, flags=(f'episode.deadman:{len(spec) - 1}',))
        members.append(build(f'w{seed}-m{k}', spec, start=10 * NS + k * 1000 * NS,
                             watt_scale=1 + rng.gauss(0, 0.02), **kwargs))
    return members


CONSTANT_GRID = [
    RowConstants(state=BOTH, clock=None, guard_s=2.0),
    RowConstants(state={'os_level'}, clock=None, guard_s=0.0, edges='cut_only'),
    RowConstants(state=BOTH, clock=ClockClause('registered_base', base_mhz=1398.0), guard_s=2.0, edge_j=0.5),
    RowConstants(state={'pm_state'}, clock=ClockClause('leg_max_state', ratio=0.95, window_s=5.0), guard_s=1.0),
]


class TwinAgreementTests(unittest.TestCase):
    def test_production_and_twin_agree_on_rows_and_scores(self):
        for seed, hot, deadman in ((1, False, None), (2, True, None), (3, True, 4), (4, False, 0)):
            members = world(seed, hot=hot, deadman=deadman)
            for constants in CONSTANT_GRID:
                prod = [run(m, constants) for m in members]
                twins = {m[0].episode_id: run_twin(m, constants) for m in members}
                for p in prod:
                    t = twins[p.episode_id]
                    self.assertEqual([(r.turn, r.decode_tokens, r.end_ns, r.reason, r.cut) for r in p.rows],
                                     [(r['turn'], r['decode_tokens'], r['end_ns'], r['reason'], r['cut'])
                                      for r in t['rows']], (seed, constants, p.episode_id))
                    self.assertEqual(list(p.no_row), t['no_row'])
                    self.assertEqual(p.n_edges, t['n_edges'])
                    for a, b in zip(p.rows, t['rows']):
                        self.assertAlmostEqual(a.energy_j, b['energy_j'], delta=1e-9 * max(1, abs(a.energy_j)))
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
