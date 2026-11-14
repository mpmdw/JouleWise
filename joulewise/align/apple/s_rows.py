"""RL-148 reference-state rows for the registered test S (desk step 6; synthetic-tested only).

A row is the part of one turn's model call that ran in the reference state:
from the turn's start to the earliest active cut, less a guard, snapped to a
decode-token stamp. It is ``(C, P, D')`` with ``C`` the cached context, ``P`` the
prefill tokens and ``D'`` the decode tokens stamped by the row's end, and its
energy is the GPU-rail integral over exactly that interval
(``attribution.trace_energy``), with holds removed. Tool-call time and unowned
segments never enter a row.

Three constants are INPUTS (``RowConstants``), not fixed here: the state
definition (which of the OS level and the powermetrics state end a row), the
clock clause (none, or a trailing activity-weighted clock under a ratio of a
reference), and the guard. RL-148 section 3 fixes the candidate list; every
candidate prints for the record whichever constants are chosen.

Truncated members (RL-148 section 2): a member ended by the deadman, a G1
timeout or the decode budget is kept on the rows it produced. A turn cut by the
deadman is scored up to its last stamped token; a turn with no stamped token
gives no row whatever its record says about prompt tokens (step 0: a deadman
inside the native prefill leaves a turn record carrying the full fresh prompt
count, zero decode tokens and a ``first_token_ns`` set to the cut instant). The
member's scored energy ends at its last scored boundary.

Label blindness: no function here reads ``Episode.condition`` (the sharp-null
exactness of S rests on it; tests poison the field).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
from typing import Any, Mapping

NS = 1_000_000_000
STATE_KEYS = frozenset({'os_level', 'pm_state'})
PM_REFERENCE_STATES = ('Nominal', 'Unknown', None)
CLOCK_REFERENCES = ('registered_base', 'leg_max_state')
# RL-148 section 3: the candidate list and its fixed record-only parameters.
RECORD_RATIO = 0.97
RECORD_WINDOW_S = 10.0
CANDIDATES = ('os_first_nonzero', 'pm_first_off', 'after_base_two_row', 'clock_vs_base', 'clock_vs_leg_max')
TRUNCATING_STOPS = (('episode.deadman:', 'deadman'), ('thermal.gate_timeout:', 'g1_timeout'),
                    ('episode.decode_budget:', 'decode_budget'))
SCHEMA = 'joulewise.align.s_rows.v1'


@dataclass(frozen=True)
class ClockClause:
    """First time the activity-weighted mean clock over the trailing window is under ratio x reference."""
    reference: str
    ratio: float = RECORD_RATIO
    window_s: float = RECORD_WINDOW_S
    base_mhz: float | None = None

    def __post_init__(self):
        if self.reference not in CLOCK_REFERENCES:
            raise ValueError(f'clock reference must be one of {CLOCK_REFERENCES}')
        if not (0 < self.ratio <= 1) or not self.window_s > 0:
            raise ValueError('clock clause needs 0 < ratio <= 1 and a positive window')
        if self.reference == 'registered_base' and not (self.base_mhz and self.base_mhz > 0):
            raise ValueError('registered_base clock clause needs base_mhz')


@dataclass(frozen=True)
class RowConstants:
    """The row's three constants (RL-148 section 1: fixed later, in the ruling on Part C)."""
    state: frozenset
    clock: ClockClause | None
    guard_s: float
    # Uncertainty of the summed member term (RL-148 correction 1).
    edge_j: float = 1.0
    edges: str = 'all_boundaries'

    def __post_init__(self):
        object.__setattr__(self, 'state', frozenset(self.state))
        if not self.state <= STATE_KEYS:
            raise ValueError(f'state keys must be a subset of {sorted(STATE_KEYS)}')
        if not (self.guard_s >= 0 and math.isfinite(self.guard_s)):
            raise ValueError('guard must be a finite nonnegative number of seconds')
        if not (self.edge_j >= 0 and math.isfinite(self.edge_j)):
            raise ValueError('edge_j must be finite and nonnegative')
        if self.edges not in ('all_boundaries', 'cut_only'):
            raise ValueError("edges must be 'all_boundaries' or 'cut_only'")

    def record(self):
        return {'state': sorted(self.state), 'clock': None if self.clock is None else asdict(self.clock),
                'guard_s': self.guard_s, 'edge_j': self.edge_j, 'edges': self.edges}


@dataclass(frozen=True)
class Row:
    turn: int
    context_tokens: int
    prefill_tokens: int
    decode_tokens: int            # D': decode tokens stamped by end_ns
    logged_decode_tokens: int     # D: the turn record's decode count
    start_ns: int
    end_ns: int
    reason: str                   # 'turn_end', 'deadman_last_token' or the firing candidate
    cut: bool                     # end_ns is a cut boundary (not the turn record's own end)
    energy_j: float
    query_half_width_j: float
    energy_flags: tuple = ()


@dataclass(frozen=True)
class MemberRows:
    episode_id: str
    rows: tuple
    no_row: tuple                 # ({'turn', 'reason'}, ...)
    candidates: tuple             # per-turn record of every candidate
    ended_by: str                 # deadman | g1_timeout | decode_budget | returned
    truncated: bool
    measured_j: float | None
    measured_half_width_j: float | None
    n_edges: int
    scored_through_ns: int | None
    status: str                   # 'scored' or 's_score_undefined'
    flags: tuple = ()
    constants: Mapping[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Candidates
# --------------------------------------------------------------------------
def _first_os_nonzero(turn, os_readings):
    """Carry-in (last reading at or before the start) above 0 cuts at the start; else the first reading above 0."""
    readings = sorted((t, v) for t, v in os_readings if type(v) is int)
    before = [(t, v) for t, v in readings if t <= turn.start_ns]
    if before and before[-1][1] > 0:
        return turn.start_ns
    return next((t for t, v in readings if turn.start_ns < t <= turn.end_ns and v > 0), None)


def _pm_off(row):
    return row.get('state') not in PM_REFERENCE_STATES


def _first_pm_off(turn, pm_rows):
    """A PM row reads at its end (as ``rl145_prints``); Nominal, Unknown and missing do not cut."""
    rows = sorted(pm_rows, key=lambda r: r['end_ns'])
    before = [r for r in rows if r['end_ns'] <= turn.start_ns]
    if before and _pm_off(before[-1]):
        return turn.start_ns
    return next((r['end_ns'] for r in rows if turn.start_ns < r['end_ns'] <= turn.end_ns and _pm_off(r)), None)


def _trailing_clock(rows, t, window_ns):
    """Activity-weighted mean clock over [t - window, t]; None without clock support."""
    lo = t - window_ns
    num = den = 0.0
    for r in rows:
        if r.get('clock_mhz') is None:
            continue
        overlap = min(t, r['end_ns']) - max(lo, r['start_ns'])
        width = r['end_ns'] - r['start_ns']
        if overlap <= 0 or width <= 0:
            continue
        weight = r.get('active_ns', 0) * overlap / width
        num += weight * r['clock_mhz']
        den += weight
    return num / den if den > 0 else None


def _first_clock_under(turn, pm_rows, reference_mhz, ratio, window_s):
    if reference_mhz is None or reference_mhz <= 0:
        return None
    rows = sorted(pm_rows, key=lambda r: r['end_ns'])
    window_ns = round(window_s * NS)
    for r in rows:
        t = r['end_ns']
        # The trailing window lies inside the turn: the clause is first evaluated a full window
        # after the start, so idle gate rows (low clock at low activity) never fire it.
        if not turn.start_ns + window_ns <= t <= turn.end_ns:
            continue
        mean = _trailing_clock(rows, t, window_ns)
        if mean is not None and mean < ratio * reference_mhz:
            return t
    return None


def _after_base_two_row(turn, pm_rows):
    """Record only (retired in the RL-145 close; ``r1_runtime.t_decline``'s rule as an absolute time):
    the first of two consecutive PM rows whose clock is under 0.97 x the median clock of the
    rows ending in the first 10 s of decode."""
    first = turn.first_token_ns
    if first is None:
        return None
    rows = sorted((r for r in pm_rows if r.get('clock_mhz') is not None
                   and r['end_ns'] > first and r['start_ns'] < turn.end_ns), key=lambda r: r['end_ns'])
    base = sorted(r['clock_mhz'] for r in rows if r['end_ns'] <= first + 10 * NS)
    if not base:
        return None
    k = len(base)
    median = base[k // 2] if k % 2 else (base[k // 2 - 1] + base[k // 2]) / 2
    threshold = RECORD_RATIO * median
    for a, b in zip(rows, rows[1:]):
        if a['clock_mhz'] < threshold and b['clock_mhz'] < threshold:
            return a['end_ns']
    return None


def leg_max_state_mhz(pm_rows):
    values = [r['max_state_mhz'] for r in pm_rows if r.get('max_state_mhz') is not None]
    return max(values) if values else None


def turn_candidates(turn, *, os_readings, pm_rows, base_mhz=None, leg_max_mhz=None):
    """Every RL-148 candidate for one turn at its record parameters (absolute episode ns or None)."""
    return {
        'os_first_nonzero': _first_os_nonzero(turn, os_readings),
        'pm_first_off': _first_pm_off(turn, pm_rows),
        'after_base_two_row': _after_base_two_row(turn, pm_rows),
        'clock_vs_base': _first_clock_under(turn, pm_rows, base_mhz, RECORD_RATIO, RECORD_WINDOW_S),
        'clock_vs_leg_max': _first_clock_under(turn, pm_rows, leg_max_mhz, RECORD_RATIO, RECORD_WINDOW_S),
    }


def _active_cut(turn, constants, *, os_readings, pm_rows, leg_max_mhz):
    """(time, name) of the earliest cut the constants make active, or (None, None)."""
    found = []
    if 'os_level' in constants.state:
        found.append((_first_os_nonzero(turn, os_readings), 'os_first_nonzero'))
    if 'pm_state' in constants.state:
        found.append((_first_pm_off(turn, pm_rows), 'pm_first_off'))
    clause = constants.clock
    if clause is not None:
        reference = clause.base_mhz if clause.reference == 'registered_base' else leg_max_mhz
        name = 'clock_vs_base' if clause.reference == 'registered_base' else 'clock_vs_leg_max'
        found.append((_first_clock_under(turn, pm_rows, reference, clause.ratio, clause.window_s), name))
    found = [(t, n) for t, n in found if t is not None]
    return min(found) if found else (None, None)


# --------------------------------------------------------------------------
# Energy
# --------------------------------------------------------------------------
def _select_trace(episode, source, channel):
    traces = [t for t in episode.power_traces if t.source == source and t.channel == channel]
    if len(traces) != 1:
        return None, None, [f'trace.{"missing" if not traces else "ambiguous"}']
    trace = traces[0]
    if trace.clock_domain == episode.clock_domain:
        return trace, None, []
    mappings = [m for m in episode.clock_mappings
                if m.trace_domain == trace.clock_domain and m.episode_domain == episode.clock_domain]
    if len(mappings) != 1:
        return trace, None, ['clock.mapping_missing' if not mappings else 'clock.mapping_ambiguous']
    return trace, mappings[0], []


def _owned_pieces(start, end, holds):
    """[start, end] less every hold interval (holds are excluded energy, RL-145 A2)."""
    pieces, cursor = [], start
    for a, b in sorted(holds):
        if b <= cursor or a >= end:
            continue
        if a > cursor:
            pieces.append((cursor, a))
        cursor = max(cursor, b)
    if cursor < end:
        pieces.append((cursor, end))
    return pieces


def _row_energy(trace, mapping, start, end, holds):
    from joulewise.align.attribution import trace_energy
    joules, bound, flags = [], [], []
    for a, b in _owned_pieces(start, end, holds):
        estimate = trace_energy(trace, a, b, mapping=mapping)
        joules.append(estimate.joules)
        bound.append(estimate.half_width_j)
        flags.extend(estimate.flags)
    return math.fsum(joules), math.fsum(bound), tuple(dict.fromkeys(flags))


# --------------------------------------------------------------------------
# Rows
# --------------------------------------------------------------------------
def ended_by(flags):
    for prefix, name in TRUNCATING_STOPS:
        if any(f.startswith(prefix) for f in flags):
            return name
    return 'returned'


def member_rows(episode, *, token_stamps, finish_reasons, os_readings, pm_rows, constants,
                source='powermetrics', channel='gpu_power'):
    """Reference-state rows of one member.

    ``token_stamps``: {turn index: [episode ns of decode token 1, 2, ...]} (absent: unavailable).
    ``finish_reasons``: {turn index: the turn's ``align_turns.jsonl`` finish reason}.
    ``os_readings``: [(episode ns, OS level)]. ``pm_rows``: native PM rows on the episode clock
    ({start_ns, end_ns, state, active_ns, clock_mhz[, max_state_mhz]}).
    """
    if not isinstance(constants, RowConstants):
        raise TypeError('constants must be RowConstants')
    flags = []
    trace, mapping, trace_flags = _select_trace(episode, source, channel)
    flags.extend(trace_flags)
    intervals = (episode.hardware.get('thermal') or {}).get('intervals', ())
    leg_max = leg_max_state_mhz(pm_rows)
    base = constants.clock.base_mhz if constants.clock is not None else None
    guard_ns = round(constants.guard_s * NS)
    rows, no_row, record = [], [], []
    for turn in episode.turns:
        candidates = turn_candidates(turn, os_readings=os_readings, pm_rows=pm_rows,
                                     base_mhz=base, leg_max_mhz=leg_max)
        stamps = token_stamps.get(turn.index)
        stamps = None if stamps is None else sorted(int(s) for s in stamps)
        cut_t, cut_name = _active_cut(turn, constants, os_readings=os_readings, pm_rows=pm_rows,
                                      leg_max_mhz=leg_max)
        deadman_cut = finish_reasons.get(turn.index) == 'episode.deadman'
        entry = {'turn': turn.index, 'candidates_ns': candidates, 'active_cut': cut_name,
                 'active_cut_ns': cut_t, 'deadman_cut': deadman_cut, 'logged_decode_tokens': turn.decode_tokens}
        record.append(entry)

        def refuse(reason):
            no_row.append({'turn': turn.index, 'reason': reason})
            entry['row'] = None
            entry['no_row'] = reason

        if turn.decode_tokens == 0 or (stamps is not None and not stamps):
            # RL-148 correction 4: no row whatever the record says about prompt tokens.
            refuse('deadman_before_first_token' if deadman_cut else 'no_decode_token')
            continue
        if stamps is not None and len(stamps) != turn.decode_tokens:
            refuse('token_stamps_count_mismatch')
            continue
        limit = None if cut_t is None else cut_t - guard_ns
        state_cut = limit is not None and limit < turn.end_ns
        if not state_cut and not deadman_cut:
            end, d_prime, reason, cut = turn.end_ns, turn.decode_tokens, 'turn_end', False
        else:
            if stamps is None:
                # Every stamp is at or after the prefill-end stamp, so a cut before it needs none.
                early = state_cut and turn.first_token_ns is not None and limit < turn.first_token_ns
                refuse(f'cut_before_first_token:{cut_name}' if early else 'token_stamps_unavailable')
                continue
            if state_cut and limit < stamps[-1]:
                d_prime = sum(1 for s in stamps if s <= limit)
                end = stamps[d_prime - 1] if d_prime else None
                reason = cut_name
            else:
                # The state cut (if any) falls after the last token; a deadman-cut turn
                # ends at its last stamped token.
                d_prime, end = len(stamps), stamps[-1]
                reason = 'deadman_last_token' if deadman_cut else cut_name
            if d_prime == 0:
                refuse(f'cut_before_first_token:{cut_name}')
                continue
            cut = True
        holds = [(i['start_ns'], i['end_ns']) for i in intervals
                 if i.get('kind') == 'H' and i.get('turn') == turn.index]
        if trace is None:
            energy, bound, energy_flags = math.nan, math.inf, ('trace.unavailable',)
        else:
            energy, bound, energy_flags = _row_energy(trace, mapping, turn.start_ns, end, holds)
        row = Row(turn=turn.index, context_tokens=turn.context_tokens, prefill_tokens=turn.prefill_tokens,
                  decode_tokens=d_prime, logged_decode_tokens=turn.decode_tokens, start_ns=turn.start_ns,
                  end_ns=end, reason=reason, cut=cut, energy_j=energy, query_half_width_j=bound,
                  energy_flags=energy_flags)
        rows.append(row)
        entry['row'] = {'decode_tokens': d_prime, 'end_ns': end, 'reason': reason}
    if constants.edges == 'all_boundaries':
        n_edges = 2 * len(rows)
    else:
        n_edges = sum(1 for r in rows if r.cut)
    if rows:
        measured = math.fsum(r.energy_j for r in rows)
        query = math.fsum(r.query_half_width_j for r in rows)
        # Query bounds add linearly (shared-sign sensitivities, as attribution's totals);
        # boundary timing noise is independent per edge and adds in quadrature.
        half = math.sqrt(query * query + n_edges * constants.edge_j ** 2)
        through = max(r.end_ns for r in rows)
        status = 'scored' if math.isfinite(measured) and math.isfinite(half) else 's_score_undefined'
    else:
        measured = half = through = None
        status = 's_score_undefined'
        flags.append('s_rows.no_row')
    stop = ended_by(episode.flags)
    return MemberRows(episode_id=episode.episode_id, rows=tuple(rows), no_row=tuple(no_row),
                      candidates=tuple(record), ended_by=stop, truncated=stop != 'returned',
                      measured_j=measured, measured_half_width_j=half, n_edges=n_edges,
                      scored_through_ns=through, status=status, flags=tuple(flags),
                      constants=constants.record())


def scored_shares(member):
    """B7 item 7 print: rows and decode tokens scored against the member's logged turns (no outcome word)."""
    turns = len(member.candidates)
    logged = sum(e['logged_decode_tokens'] for e in member.candidates)
    scored = sum(r.decode_tokens for r in member.rows)
    return {'rows': len(member.rows), 'turns': turns, 'row_share': len(member.rows) / turns if turns else None,
            'decode_scored': scored, 'decode_logged': logged,
            'decode_share': scored / logged if logged else None}


def boundary_table(members):
    """Per-window row-boundary table (turn, cut time, D', reason) and its sha256 (RL-148 section 4 item 7).

    Built from stamps, state and clock only, so it can be committed before a joule is opened.
    """
    table = []
    for m in sorted(members, key=lambda m: m.episode_id):
        for entry in m.candidates:
            row = entry.get('row')
            table.append({'episode': m.episode_id, 'turn': entry['turn'],
                          'end_ns': None if row is None else row['end_ns'],
                          'decode_tokens': None if row is None else row['decode_tokens'],
                          'reason': entry.get('no_row') if row is None else row['reason']})
    text = json.dumps(table, sort_keys=True, separators=(',', ':'))
    return table, hashlib.sha256(text.encode()).hexdigest()


# --------------------------------------------------------------------------
# The frozen sequence design and a LOSO harness (label-invariance test only)
# --------------------------------------------------------------------------
def sequence_design(context, prefill, decode):
    """Protocol v4 :538, ``[1, P, D, (C+P)D + D^2/2, CP + P^2/2]``; additive in token position."""
    c, p, d = context, prefill, decode
    return [1.0, float(p), float(d), (c + p) * d + d * d / 2, c * p + p * p / 2]


def _solve(a, b):
    n = len(b)
    m = [list(map(float, row)) + [float(v)] for row, v in zip(a, b)]
    for i in range(n):
        pivot = max(range(i, n), key=lambda k: abs(m[k][i]))
        if abs(m[pivot][i]) < 1e-300:
            return None
        m[i], m[pivot] = m[pivot], m[i]
        for k in range(n):
            if k != i:
                f = m[k][i] / m[i][i]
                m[k] = [x - f * y for x, y in zip(m[k], m[i])]
    return [m[i][n] / m[i][i] for i in range(n)]


def loso_scores(members):
    """{episode_id: S score | None} for one stratum: h = 0 sequence fit on the OTHER members' rows.

    A scoring harness for the label-invariance test, NOT the registered engine (the engine
    families own the fitter). Columns are scaled by their max magnitude; covariance is
    sigma^2 (X'X)^-1; prediction variance s'cov s + n sigma^2 + h^2.
    """
    out = {}
    for j in members:
        train = [r for m in members if m.episode_id != j.episode_id and m.status == 'scored' for r in m.rows]
        if j.status != 'scored' or len(train) < 6:
            out[j.episode_id] = None
            continue
        x = [sequence_design(r.context_tokens, r.prefill_tokens, r.decode_tokens) for r in train]
        y = [r.energy_j for r in train]
        p = len(x[0])
        scale = [max(abs(row[k]) for row in x) or 1.0 for k in range(p)]
        xs = [[row[k] / scale[k] for k in range(p)] for row in x]
        xtx = [[math.fsum(row[a] * row[b] for row in xs) for b in range(p)] for a in range(p)]
        xty = [math.fsum(row[a] * v for row, v in zip(xs, y)) for a in range(p)]
        beta_s = _solve(xtx, xty)
        if beta_s is None or len(train) <= p:
            out[j.episode_id] = None
            continue
        rss = math.fsum((v - math.fsum(b * c for b, c in zip(beta_s, row))) ** 2 for row, v in zip(xs, y))
        sigma2 = rss / (len(train) - p)
        if sigma2 <= 0:
            out[j.episode_id] = None
            continue
        s = [math.fsum(sequence_design(r.context_tokens, r.prefill_tokens, r.decode_tokens)[k] / scale[k]
                       for r in j.rows) for k in range(p)]
        pred = math.fsum(b * c for b, c in zip(beta_s, s))
        w = _solve(xtx, s)
        quad = sigma2 * math.fsum(a * b for a, b in zip(s, w))
        var = quad + len(j.rows) * sigma2 + j.measured_half_width_j ** 2
        out[j.episode_id] = (j.measured_j - pred) / math.sqrt(var)
    return out


# --------------------------------------------------------------------------
# Bundle adapter (step 0's desk code: failed executions included)
# --------------------------------------------------------------------------
def _jsonl(path):
    from joulewise.desk_compress import read_bytes
    try:
        return [json.loads(x) for x in read_bytes(path).splitlines() if x.strip()]
    except FileNotFoundError:
        return None


def bundle_token_stamps(episode, events, runtime_events):
    """Token stamps per turn. A failed execution (deadman) keeps its runtime events only in
    ``outputs/align_runtime_events.jsonl``; ``events.jsonl`` then has no token event (step 0)."""
    from joulewise.align.apple.rl145_prints import token_stamps_from_events
    source = events if any(e.get('event_type') == 'token' for e in events or ()) else (runtime_events or [])
    out = {}
    for turn in episode.turns:
        stamps = token_stamps_from_events(source, turn)
        if stamps is not None:
            out[turn.index] = stamps
        elif turn.decode_tokens == 0:
            out[turn.index] = []
    return out, ('events.jsonl' if source is events else 'outputs/align_runtime_events.jsonl')


def pm_rows_with_states(bundle, episode):
    """``thermal_desk.native_pm_samples`` plus each row's highest DVFM state with used time."""
    from pathlib import Path
    from joulewise.align.apple.thermal_desk import native_pm_samples
    from joulewise.desk_compress import read_bytes
    rows = native_pm_samples(bundle, episode)
    try:
        rich = [json.loads(x) for x in read_bytes(Path(bundle) / 'rich_telemetry.jsonl').splitlines() if x.strip()]
    except FileNotFoundError:
        rich = []
    if rows and len(rich) == len(rows):
        for row, detail in zip(rows, rich):
            states = [s for s in (detail.get('gpu') or {}).get('dvfm_states', ()) if s.get('used_ns', 0) > 0]
            row['max_state_mhz'] = max((s['freq'] for s in states), default=None)
    return rows


def read_member_rows(bundle, constants, *, os_journal=(), pm_rows=None):
    """Rows for one bundle, failed executions included. Reads no condition label and no transcript."""
    from pathlib import Path
    from joulewise.align.apple.thermal_desk import normalize_journal
    from joulewise.align.apple.workload import read_episode_bundle
    bundle = Path(bundle)
    episode = read_episode_bundle(bundle)
    events = _jsonl(bundle / 'events.jsonl') or []
    runtime = _jsonl(bundle / 'outputs/align_runtime_events.jsonl')
    stamps, stamp_source = bundle_token_stamps(episode, events, runtime)
    finish = {r['turn']: (r.get('generation') or {}).get('finish_reason')
              for r in (_jsonl(bundle / 'outputs/align_turns.jsonl') or [])}
    os_readings = [(r['finished']['monotonic_ns'], r['values'].get('level')) for r in os_journal
                   if r.get('kind') == 'reading' and not r.get('error')]
    if not os_readings:
        gate = _jsonl(bundle / 'outputs/align_thermal.jsonl') or []
        os_readings = [(r['monotonic_ns'], r.get('status', {}).get('os_level')) for r in normalize_journal(gate)
                       if r.get('status', {}).get('os_level') is not None]
    if pm_rows is None:
        pm_rows = pm_rows_with_states(bundle, episode)
    member = member_rows(episode, token_stamps=stamps, finish_reasons=finish, os_readings=os_readings,
                         pm_rows=pm_rows, constants=constants)
    return member, {'token_stamp_source': stamp_source, 'failed_execution': runtime is not None,
                    'os_readings': len(os_readings), 'pm_rows': len(pm_rows)}


__all__ = ['ClockClause', 'RowConstants', 'Row', 'MemberRows', 'CANDIDATES', 'turn_candidates',
           'member_rows', 'boundary_table', 'sequence_design', 'loso_scores', 'bundle_token_stamps',
           'pm_rows_with_states', 'read_member_rows', 'scored_shares', 'ended_by', 'leg_max_state_mhz']
