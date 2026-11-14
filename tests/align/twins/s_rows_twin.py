"""Twin of the RL-148 reference-state row builder (``joulewise/align/apple/s_rows.py``).

Written from RL-148 sections 1-3 and the step-0/step-6 brief, with its own
arithmetic: energy through ``tests.align.twins.attribution_twin.trace_energy``
(the independent A4 twin), its own state scan (one merged, time-ordered stream
of readings per turn), its own snapping (bisect over stamps) and its own
least-squares (normal equations in exact ``fractions.Fraction`` arithmetic on
integer-scaled data, then a float score).

CAVEAT, stated plainly: this twin and the production module were written in one
session by one model (Opus). It catches slips of arithmetic and of reading, not
a shared misreading of the ruling. Family independence in the round-2 sense
(CLAIM-CONTRACT-B-ROUND2-SPEC, preamble) still needs the Sol engine family to
build its own rows from the RL-148 text.

READINGS (choices the ruling leaves open; production reads them the same way,
and each is listed for the research lead):

T1  State at a turn's start is the last reading at or before the start (the
    carry-in). Off at the start cuts at the start, so the turn gives no row.
T2  A powermetrics row is read at its end time (as ``rl145_prints``); Nominal,
    Unknown and missing never cut. An OS level that is not an int is missing.
T3  The trailing clock window must lie inside the turn: the clause is evaluated
    at each PM row end t with start + window <= t <= end (idle gate rows, low
    clock at low activity, would otherwise fire it at every turn start). No
    clock cut can therefore fall in a turn's first window (10 s).
T4  Snap: D' = number of stamps at or before (cut - guard); the row ends at stamp
    D'. A whole turn (no cut, no deadman) ends at the turn record's own end.
T5  A deadman-cut turn (finish reason ``episode.deadman``) ends at its last
    stamped token unless a state cut falls earlier.
T6  Edges: 'all_boundaries' counts both ends of every row (a row's start is no
    longer shared with an integrated neighbour); 'cut_only' counts cut ends.
T7  Member half-width: query bounds summed linearly, edges in quadrature
    (sqrt(Q^2 + n_edges * edge_j^2)).
"""
from __future__ import annotations

from bisect import bisect_right
from fractions import Fraction
import math

from tests.align.twins.attribution_twin import trace_energy as twin_trace_energy

NS = 1_000_000_000
OK_PM = {'Nominal', 'Unknown', None}


def _os_events(turn, os_readings):
    """Times at which the OS stream says 'off' for this turn (carry-in mapped to the start)."""
    out = []
    last_before = None
    for t, v in sorted(os_readings, key=lambda tv: tv[0]):
        if not isinstance(v, int) or isinstance(v, bool):
            continue
        if t <= turn.start_ns:
            last_before = v
        elif t <= turn.end_ns and v > 0:
            out.append(t)
    if last_before is not None and last_before > 0:
        out.append(turn.start_ns)
    return out


def _pm_events(turn, pm_rows):
    out = []
    last_before = 'none'
    for r in sorted(pm_rows, key=lambda r: r['end_ns']):
        if r['end_ns'] <= turn.start_ns:
            last_before = r.get('state')
        elif r['end_ns'] <= turn.end_ns and r.get('state') not in OK_PM:
            out.append(r['end_ns'])
    if last_before != 'none' and last_before not in OK_PM:
        out.append(turn.start_ns)
    return out


def _clock_events(turn, pm_rows, reference, ratio, window_s):
    if not reference:
        return []
    w = int(round(window_s * NS))
    rows = [r for r in pm_rows if r.get('clock_mhz') is not None and r['end_ns'] > r['start_ns']]
    hits = []
    for probe in sorted(r['end_ns'] for r in pm_rows):
        if probe - w < turn.start_ns or probe > turn.end_ns:
            continue
        a = probe - w
        weights = []
        for r in rows:
            ov = min(probe, r['end_ns']) - max(a, r['start_ns'])
            if ov > 0:
                weights.append((r.get('active_ns', 0) * ov / (r['end_ns'] - r['start_ns']), r['clock_mhz']))
        total = sum(x for x, _ in weights)
        if total > 0 and sum(x * c for x, c in weights) / total < ratio * reference:
            hits.append(probe)
            break
    return hits


def rows_for(episode, *, token_stamps, finish_reasons, os_readings, pm_rows, state, clock, guard_s,
             edge_j=1.0, edges='all_boundaries', source='powermetrics', channel='gpu_power'):
    """Twin output: {'rows': [dict], 'no_row': [dict], 'measured_j', 'half_width_j', 'n_edges'}.

    ``clock`` is None or a dict {reference, ratio, window_s, base_mhz}.
    """
    traces = [t for t in episode.power_traces if t.source == source and t.channel == channel]
    trace = traces[0] if len(traces) == 1 else None
    leg_max = max((r['max_state_mhz'] for r in pm_rows if r.get('max_state_mhz') is not None), default=None)
    guard = int(round(guard_s * NS))
    holds = [(i['start_ns'], i['end_ns'], i.get('turn')) for i in
             (episode.hardware.get('thermal') or {}).get('intervals', ()) if i.get('kind') == 'H']
    out_rows, no_row = [], []
    for turn in episode.turns:
        events = []
        if 'os_level' in state:
            events += [(t, 'os_first_nonzero') for t in _os_events(turn, os_readings)]
        if 'pm_state' in state:
            events += [(t, 'pm_first_off') for t in _pm_events(turn, pm_rows)]
        if clock is not None:
            ref = clock['base_mhz'] if clock['reference'] == 'registered_base' else leg_max
            name = 'clock_vs_base' if clock['reference'] == 'registered_base' else 'clock_vs_leg_max'
            events += [(t, name) for t in _clock_events(turn, pm_rows, ref, clock['ratio'], clock['window_s'])]
        first_off = min(events) if events else None
        stamps = token_stamps.get(turn.index)
        dead = finish_reasons.get(turn.index) == 'episode.deadman'
        if turn.decode_tokens == 0 or stamps == []:
            no_row.append({'turn': turn.index,
                           'reason': 'deadman_before_first_token' if dead else 'no_decode_token'})
            continue
        stamps = None if stamps is None else sorted(stamps)
        if stamps is not None and len(stamps) != turn.decode_tokens:
            no_row.append({'turn': turn.index, 'reason': 'token_stamps_count_mismatch'})
            continue
        cut_at = None if first_off is None else first_off[0] - guard
        cut_name = None if first_off is None else first_off[1]
        state_cut = cut_at is not None and cut_at < turn.end_ns
        if not state_cut and not dead:
            end, d, reason, is_cut = turn.end_ns, turn.decode_tokens, 'turn_end', False
        elif stamps is None:
            early = state_cut and turn.first_token_ns is not None and cut_at < turn.first_token_ns
            no_row.append({'turn': turn.index,
                           'reason': f'cut_before_first_token:{cut_name}' if early else 'token_stamps_unavailable'})
            continue
        else:
            if state_cut and cut_at < stamps[-1]:
                d = bisect_right(stamps, cut_at)
                reason = cut_name
            else:
                d = len(stamps)
                reason = 'deadman_last_token' if dead else cut_name
            if d == 0:
                no_row.append({'turn': turn.index, 'reason': f'cut_before_first_token:{cut_name}'})
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
    return {'rows': out_rows, 'no_row': no_row, 'measured_j': measured, 'half_width_j': half, 'n_edges': n_edges}


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
