"""Twin of the reference-state row builder (``joulewise/align/apple/s_rows.py``).

Written from RL-149 section 1.3 (with RL-151 section 1.1), RL-152 section 1.6
and RL-153 section 2, with its own arithmetic: energy through
``tests.align.twins.attribution_twin.trace_energy`` (the independent A4 twin),
its own state scan (one time-ordered sweep over a merged stream of journal
readings, native powermetrics rows and hazard readings per turn), its own stamp
age (integer nanoseconds against +/-2 s, not ``rl145_prints``), its own snapping
(bisect over stamps) and its own least-squares (normal equations in exact
``fractions.Fraction`` arithmetic on integer-scaled data, then a float score).

CAVEAT, stated plainly: this twin and the production module were written in one
session by one model (Opus). It catches slips of arithmetic and of reading, not
a shared misreading of the ruling. Family independence (RL-149 section 1.3,
question 6) still needs the Sol engine family to build its own rows from
RL-149 section 1.3 and RL-153 section 2.

READINGS (choices the rulings leave open; production reads them the same way,
and each is listed for the research lead):

T1  Carry-in is the last member-journal reading at or before the turn's start
    (RL-149 T1). It must be fresh state, at most 2 s before the start, level 0
    and Nominal. A fresh reading whose state is missing (None) is unobserved,
    not out of state; ``Unknown`` is out of state (it is not Nominal).
T2  A powermetrics row is read at its end; it only cuts, inside the turn.
T3  The clock window lies inside the decode: it ends at a PM row end no later
    than the last stamped token and starts no earlier than first token + 10 s
    (the first stamped token; the turn record's first token without stamps).
T4  Snap: D' = number of stamps at or before the row end; the row ends at stamp
    D'. A whole turn (no cut, no deadman) ends at the turn record's own end.
T5  A deadman-cut turn ends at its last stamped token unless a cut falls earlier.
T6  Edges: 'all_boundaries' counts both ends of every row; 'cut_only' cut ends.
T7  Member half-width: sqrt(Q^2 + n_edges * edge_j^2).
T8  The in-turn search (off readings, gaps, clock windows) runs over
    (start, last stamped token], as the step-3 script does; without stamps, to
    the turn record's end.
T9  "Any cut fired" for ``after_hot_turn`` means any candidate row end found in
    the turn (state, ``state_unobserved`` or clock), or a start read out of state.
T10 The guard's second term is the last FRESH in-state reading before the first
    off reading (freshness is needed to claim the state); the turn's start when
    there is none. Ties between candidate row ends take the reason code that
    sorts first; simultaneous off kinds are joined with '+'.
T11 A hazard journal only adds cuts (level above 0 inside the turn). It is
    never the start's evidence.
"""
from __future__ import annotations

from bisect import bisect_right
from fractions import Fraction
import math

from tests.align.twins.attribution_twin import trace_energy as twin_trace_energy

NS = 1_000_000_000
TWO_S = 2 * NS
NOT_OFF = {'Nominal', 'Unknown', None}


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _reading(sample):
    """(t, level or None, state, fresh) from one normalized journal sample, ages in integer ns."""
    st = sample.get('status') or {}
    level = st.get('os_level') if _int(st.get('os_level')) else None
    pm_ns = st.get('pm_observed_ns')
    t = sample['monotonic_ns']
    stamp_ok = _int(pm_ns) and -TWO_S <= t - pm_ns <= TWO_S
    return t, level, st.get('pm_state'), bool(level is not None and stamp_ok)


def _evaluate(turn, journal, pm_rows, hazard, state, guard, clock, leg_max, first_tok, hi):
    """(start verdict, [(row end, reason)]) for one turn by one sweep."""
    readings = sorted((_reading(s) for s in journal), key=lambda r: r[0])
    want_level, want_pm = 'os_level' in state, 'pm_state' in state

    def in_state(level, pm):
        return (not want_level or level == 0) and (not want_pm or pm == 'Nominal')

    carry = None
    for r in readings:
        if r[0] <= turn.start_ns:
            carry = r
    if carry is None or turn.start_ns - carry[0] > TWO_S or not carry[3] or (want_pm and carry[2] is None):
        verdict = 'start_state_unobserved'
    elif in_state(carry[1], carry[2]):
        verdict = 'ok'
    else:
        verdict = 'start_out_of_state'

    stream = []   # (t, order, kind, payload)
    for t, level, pm, fresh in readings:
        if turn.start_ns < t <= hi:
            stream.append((t, 0, 'journal', (level, pm, fresh)))
    for r in pm_rows:
        if turn.start_ns < r['end_ns'] <= hi:
            stream.append((r['end_ns'], 1, 'native', r.get('state')))
    for t, level in hazard:
        if turn.start_ns < t <= hi:
            stream.append((t, 2, 'hazard', level))
    stream.sort(key=lambda e: (e[0], e[1]))

    carry_fresh = carry is not None and carry[3]
    last_fresh = carry[0] if carry_fresh else None
    fresh_in = [carry[0]] if carry_fresh and in_state(carry[1], carry[2]) else []
    off_t, off_kinds, unobserved = None, set(), None
    for t, _, kind, payload in stream:
        kinds = []
        if kind == 'journal':
            level, pm, fresh = payload
            if want_level and level is not None and level > 0:
                kinds.append('os_level_above_0')
            if want_pm and pm not in NOT_OFF:
                kinds.append('journal_pm_state_off')
            if fresh:
                if unobserved is None and last_fresh is not None and t - last_fresh > TWO_S:
                    unobserved = last_fresh
                last_fresh = t
                if in_state(level, pm):
                    fresh_in.append(t)
        elif kind == 'native' and want_pm and payload not in NOT_OFF:
            kinds.append('native_pm_state_off')
        elif kind == 'hazard' and want_level and _int(payload) and payload > 0:
            kinds.append('hazard_os_level_above_0')
        if kinds and (off_t is None or t == off_t):
            off_t = t
            off_kinds.update(kinds)
    if unobserved is None and last_fresh is not None and hi - last_fresh > TWO_S:
        unobserved = last_fresh

    ends = []
    if off_t is not None:
        second = max((t for t in fresh_in if t < off_t), default=turn.start_ns)
        ends.append((min(off_t - guard, second), '+'.join(sorted(off_kinds))))
    if unobserved is not None:
        ends.append((unobserved, 'state_unobserved'))
    if clock is not None and first_tok is not None:
        ref = clock['base_mhz'] if clock['reference'] == 'registered_base' else leg_max
        name = 'clock_e20' if clock['reference'] == 'leg_max_state' else 'clock_base_e20'
        hit = _clock_window(pm_rows, ref, clock, first_tok, hi)
        if hit is not None:
            ends.append((hit, name))
    return verdict, ends


def _clock_window(pm_rows, reference, clock, first_tok, hi):
    if not reference:
        return None
    w = int(round(clock['window_s'] * NS))
    floor = first_tok + int(round(clock.get('start_after_first_token_s', 10.0) * NS))
    rows = [r for r in pm_rows if r.get('clock_mhz') is not None and r['end_ns'] > r['start_ns']]
    for probe in sorted(r['end_ns'] for r in pm_rows):
        a = probe - w
        if a < floor or probe > hi:
            continue
        weights = []
        for r in rows:
            ov = min(probe, r['end_ns']) - max(a, r['start_ns'])
            if ov > 0:
                weights.append((r.get('active_ns', 0) * ov / (r['end_ns'] - r['start_ns']), r['clock_mhz']))
        total = sum(x for x, _ in weights)
        if total > 0 and sum(x * c for x, c in weights) / total < clock['ratio'] * reference:
            return a
    return None


def rows_for(episode, *, token_stamps, finish_reasons, journal, pm_rows, state, clock, guard_s,
             hazard_os=(), edge_j=1.0, edges='all_boundaries', source='powermetrics', channel='gpu_power'):
    """Twin output: {'rows': [dict], 'no_row': [dict], 'measured_j', 'half_width_j', 'n_edges', 'turns'}.

    ``journal``: normalized samples (``monotonic_ns``, ``status``). ``clock`` is None or a dict
    {reference, ratio, window_s, base_mhz, start_after_first_token_s}.
    """
    traces = [t for t in episode.power_traces if t.source == source and t.channel == channel]
    trace = traces[0] if len(traces) == 1 else None
    leg_max = max((r['max_state_mhz'] for r in pm_rows if r.get('max_state_mhz') is not None), default=None)
    guard = int(round(guard_s * NS))
    holds = [(i['start_ns'], i['end_ns'], i.get('turn')) for i in
             (episode.hardware.get('thermal') or {}).get('intervals', ()) if i.get('kind') == 'H']
    out_rows, no_row, turns = [], [], []
    seen_hot = False
    for turn in episode.turns:
        stamps = token_stamps.get(turn.index)
        stamps = None if stamps is None else sorted(stamps)
        hi = stamps[-1] if stamps else turn.end_ns
        first_tok = stamps[0] if stamps else turn.first_token_ns
        verdict, ends = _evaluate(turn, journal, pm_rows, hazard_os, state, guard, clock, leg_max, first_tok, hi)
        cut_at, cut_name = min(ends) if ends else (None, None)
        was_hot = seen_hot
        seen_hot = seen_hot or verdict == 'start_out_of_state' or bool(ends)
        turns.append({'turn': turn.index, 'start_state': verdict, 'cut': (cut_at, cut_name)})
        dead = finish_reasons.get(turn.index) == 'episode.deadman'
        if was_hot:
            no_row.append({'turn': turn.index, 'reason': 'after_hot_turn'})
            continue
        if turn.decode_tokens == 0 or stamps == []:
            no_row.append({'turn': turn.index,
                           'reason': 'deadman_before_first_token' if dead else 'no_decode_token'})
            continue
        if stamps is not None and len(stamps) != turn.decode_tokens:
            no_row.append({'turn': turn.index, 'reason': 'token_stamps_count_mismatch'})
            continue
        if verdict != 'ok':
            no_row.append({'turn': turn.index, 'reason': verdict})
            continue
        if cut_at is None and not dead:
            end, d, reason, is_cut = turn.end_ns, turn.decode_tokens, 'turn_end', False
        elif stamps is None:
            early = cut_at is not None and turn.first_token_ns is not None and cut_at < turn.first_token_ns
            no_row.append({'turn': turn.index, 'reason': 'cut_in_prefill' if early else 'token_stamps_unavailable'})
            continue
        else:
            if cut_at is not None:
                d, reason = bisect_right(stamps, cut_at), cut_name
            else:
                d, reason = len(stamps), 'deadman_last_token'
            if d == 0:
                no_row.append({'turn': turn.index, 'reason': 'cut_in_prefill'})
                continue
            end, is_cut = stamps[d - 1], True
        # Owned pieces: [start, end] minus this turn's holds.
        pieces, cursor = [], turn.start_ns
        for a, b, t in sorted(holds):
            if t != turn.index or b <= cursor or a >= end:
                continue
            if a > cursor:
                pieces.append((cursor, a))
            cursor = max(cursor, b)
        if cursor < end:
            pieces.append((cursor, end))
        if trace is None:
            joules, bound = math.nan, math.inf
        else:
            parts = [twin_trace_energy(trace, a, b, mapping=None) for a, b in pieces]
            joules = math.fsum(p.joules for p in parts)
            bound = math.fsum(p.half_width_j for p in parts)
        out_rows.append({'turn': turn.index, 'context_tokens': turn.context_tokens,
                         'prefill_tokens': turn.prefill_tokens, 'decode_tokens': d,
                         'start_ns': turn.start_ns, 'end_ns': end, 'reason': reason, 'cut': is_cut,
                         'energy_j': joules, 'query_half_width_j': bound})
    n_edges = 2 * len(out_rows) if edges == 'all_boundaries' else sum(r['cut'] for r in out_rows)
    if out_rows:
        q = math.fsum(r['query_half_width_j'] for r in out_rows)
        measured = math.fsum(r['energy_j'] for r in out_rows)
        half = math.hypot(q, math.sqrt(n_edges) * edge_j)
    else:
        measured = half = None
    return {'rows': out_rows, 'no_row': no_row, 'measured_j': measured, 'half_width_j': half,
            'n_edges': n_edges, 'turns': turns}


def _design(c, p, d):
    # Twice the protocol design, kept integer: [2, 2P, 2D, 2(C+P)D + D^2, 2CP + P^2].
    return [2, 2 * p, 2 * d, 2 * (c + p) * d + d * d, 2 * c * p + p * p]


def _solve_exact(a, b):
    n = len(b)
    m = [[Fraction(x) for x in row] + [Fraction(v)] for row, v in zip(a, b)]
    for i in range(n):
        piv = next((k for k in range(i, n) if m[k][i] != 0), None)
        if piv is None:
            return None
        m[i], m[piv] = m[piv], m[i]
        for k in range(n):
            if k != i and m[k][i] != 0:
                f = m[k][i] / m[i][i]
                m[k] = [x - f * y for x, y in zip(m[k], m[i])]
    return [m[i][n] / m[i][i] for i in range(n)]


def loso_scores(members):
    """{id: score | None}; ``members``: {id: twin output}. Same h = 0 model, exact normal equations."""
    out = {}
    for j, mine in members.items():
        train = [r for k, m in members.items() if k != j and m['rows'] and m['measured_j'] is not None
                 for r in m['rows']]
        if not mine['rows'] or len(train) < 6:
            out[j] = None
            continue
        x = [_design(r['context_tokens'], r['prefill_tokens'], r['decode_tokens']) for r in train]
        y = [Fraction(r['energy_j']) for r in train]
        p = 5
        xtx = [[sum(Fraction(row[a] * row[b]) for row in x) for b in range(p)] for a in range(p)]
        xty = [sum(row[a] * v for row, v in zip(x, y)) for a in range(p)]
        beta = _solve_exact(xtx, xty)
        if beta is None or len(train) <= p:
            out[j] = None
            continue
        resid = [v - sum(b * c for b, c in zip(beta, row)) for row, v in zip(x, y)]
        sigma2 = sum(r * r for r in resid) / (len(train) - p)
        if sigma2 == 0:
            out[j] = None
            continue
        s = [sum(_design(r['context_tokens'], r['prefill_tokens'], r['decode_tokens'])[k] for r in mine['rows'])
             for k in range(p)]
        w = _solve_exact(xtx, s)
        quad = sigma2 * sum(a * b for a, b in zip(s, w))
        pred = sum(b * c for b, c in zip(beta, s))
        var = float(quad) + len(mine['rows']) * float(sigma2) + mine['half_width_j'] ** 2
        out[j] = (mine['measured_j'] - float(pred)) / math.sqrt(var)
    return out
