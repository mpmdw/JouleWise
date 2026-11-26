"""Reference-state rows for the registered test S (RL-148 desk step 6; RL-149 section 1.3; RL-153 section 2;
RL-154; RL-160).

A row is the part of one turn's model call that ran in the reference state:
from the turn's start to the earliest cut, less the guard, snapped down to the
last decode token stamped at or before that time. It is ``(C, P, D')`` with
``C`` the cached context, ``P`` the prefill tokens and ``D'`` the decode tokens
stamped by the row's end, and its energy is the GPU-rail integral over exactly
that interval (``attribution.trace_energy``), with holds removed. Tool-call time
and unowned segments never enter a row.

THE STATE RULE (RL-149 section 1.3 as amended by RL-153 section 2 and RL-154;
constants confirmed by RL-151 section 1.1). A reading is in the reference state
when the OS level is 0 and the power-management state is Nominal.

- Fresh state (RL-154 section 3). A journal reading is fresh state when its OS
  level is an integer, ``rl145_prints.stamp_fresh`` accepts its stamp's age (the
  age ``rl145_prints._status_age_s`` computes at the reading's own stamp; RL-152
  section 1.6: within 2 s on either side; both imported, not copied), and its
  power-management state is present and not ``Unknown``. ``Unknown`` is the
  instrument saying it does not know: it and a missing state are one thing,
  unobserved, never out of state. The definition does not depend on the
  constants' state keys.
- At the turn's start, positive evidence: the last journal reading at or before
  the start is fresh state, at most 2 s before the start, and level 0 and
  Nominal. No reading, a reading with no level, a missing or ``Unknown`` state, a
  stale or absent stamp, or one more than 2 s before the start gives
  ``start_state_unobserved``. ``start_out_of_state`` means one thing: a fresh
  reading that reports a level above 0 or a named state other than Nominal.
- Inside the turn (the search runs over (start, last stamped token]; the turn
  record's end when no stamp exists), the state cut is the first of: a journal
  reading with level above 0 (``os_level_above_0``); a journal reading whose
  state is not Nominal, Unknown or missing (``journal_pm_state_off``); a native
  powermetrics row, read at its end, with such a state (``native_pm_state_off``);
  a hazard-journal OS reading above 0 (``hazard_os_level_above_0``). An off-state
  reading cuts whatever its stamp's age: freshness is needed to claim the state,
  never to leave it. Kinds that fire at the same instant are joined with ``+``.
- ``state_unobserved``: the start of the first stretch of more than 2 s with no
  fresh state. The first anchor is the carry-in when it is fresh state, and the
  turn's start when it is not or there is none (RL-154 finding 1: a turn nobody
  observed is cut at its start); after that each fresh reading is an anchor, and
  the stretch may run to the last stamped token. Readings with a missing or
  ``Unknown`` state do not count: one such reading costs nothing, more than 2 s of
  them is ``state_unobserved``. ``Unknown`` and missing never cut by themselves.
- Native powermetrics rows only cut. They carry no stamp-age rule and never
  supply in-state evidence (RL-153 section 2.2 item 4). The OS level has no stamp
  of its own: its bounds are those of the journal reading that carries it. A
  hazard journal only adds cuts; it is never the start's evidence (item 5).
- Guard. A state cut ends the row at the earlier of 2.0 s (``guard_s``) before
  the first off reading and the stamp of the last fresh in-state reading before
  it (the turn's start if there is none). ``state_unobserved`` ends the row at
  its reading. The clock clause ends it at the firing window's start.
- Clock clause (e20). The activity-weighted mean GPU clock over a trailing 10 s
  window is under 0.97 of the member's own top DVFM state with used time
  (``leg_max_state``). Windows end at powermetrics row ends, lie wholly inside the
  decode (end at or before the last stamped token) and start no earlier than the
  first token plus 10 s; the cut is the window's start (``clock_e20``). A window
  with no active time gives no value and no cut. "First token" is the first
  stamped decode token (RL-160 D1): ``Turn.first_token_ns`` is the end of
  prefill, not a token, and stands in only for a turn with no stamp list, where
  the clock search decides hot and nothing else.
- Clock reference (RL-154 finding 3). When the constants carry a clock clause and
  the member has no reference (no ``max_state_mhz`` on its PM rows, or no PM
  rows), the member gives no row: every turn's no-row reason is
  ``clock_reference_missing``, the status is ``s_score_undefined`` and the flag
  ``s_rows.clock_reference_missing``. The clause never switches itself off.
- The row ends at the earliest of these; ties take the first reason code in sort
  order, as the step-3 script does. A cut before the first stamped token gives no
  row (``cut_in_prefill``).
- A row needs at least one stamped decode token, cut or not (RL-160 D5). A turn
  with logged decode and no stamp list gives no row: ``cut_in_prefill`` when a
  cut lies before ``Turn.first_token_ns``, otherwise ``token_stamps_unavailable``
  (with or without a cut or the deadman). Its search still runs over (start, the
  turn record's end] with clock windows from ``first_token_ns`` + 10 s; that
  decides only whether the turn is hot.
- ``after_hot_turn`` (RL-154 section 2; T9 kept). A turn is hot when its start
  read out of state; an off reading fired in (start, last stamped token]; the
  clock clause fired; or more than 2 s of it went by with no fresh state, counted
  from the fresh carry-in or else from the start. No later turn of the member
  gives a row. Hot is decided whether or not the turn gave a row. A turn that is
  only ``start_state_unobserved`` (in-turn readings fresh and in state, no gap)
  is not hot: it loses its own row and nothing else. A fresh carry-in anchors the
  gap whatever its distance from the start (RL-160 #6): the 2 s distance belongs
  to the start verdict only, so a turn whose fresh carry-in lies more than 2 s
  before the start, with no fresh reading until more than 2 s after it, is hot.
- Member half-width (RL-149 T7 as RL-160 D4 confirms): sqrt(Q^2 + n_edges *
  edge_j^2), with Q the summed query half-widths of the rows (integration bounds
  add linearly) and the boundary timing noise of each edge in quadrature.

Truncated members (RL-148 section 2): a member ended by the deadman, a G1
timeout or the decode budget is kept on the rows it produced. A turn cut by the
deadman is scored up to its last stamped token; a turn with no stamped token
gives no row whatever its record says about prompt tokens. The member's scored
energy ends at its last scored boundary.

RL-148's record-only candidates (``turn_candidates``) still print for every
turn; they decide nothing.

Label blindness: no function here reads ``Episode.condition`` (the sharp-null
exactness of S rests on it; tests poison the field).
"""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
from typing import Any, Mapping

from joulewise.align.apple.rl145_prints import _status_age_s, stamp_fresh

NS = 1_000_000_000
STATE_KEYS = frozenset({'os_level', 'pm_state'})
PM_REFERENCE_STATES = ('Nominal', 'Unknown', None)   # states that never cut
PM_UNOBSERVED_STATES = ('Unknown', None)            # states that never claim the state (RL-154 section 3)
CLOCK_REFERENCES = ('registered_base', 'leg_max_state')
# RL-149 section 1.3: the start's reading is at most 2 s before the start; more than 2 s with no fresh
# state is state_unobserved. (The stamp's own 2 s bound is rl145_prints.stamp_fresh, imported above.)
START_MAX_AGE_NS = 2 * NS
UNOBSERVED_GAP_NS = 2 * NS
# RL-148 section 3: the record-only candidate list and its fixed parameters.
RECORD_RATIO = 0.97
RECORD_WINDOW_S = 10.0
CANDIDATES = ('os_first_nonzero', 'pm_first_off', 'after_base_two_row', 'clock_vs_base', 'clock_vs_leg_max')
# RL-149 section 1.3's reason codes.
START_OUT_OF_STATE = 'start_out_of_state'
START_STATE_UNOBSERVED = 'start_state_unobserved'
STATE_UNOBSERVED = 'state_unobserved'
CUT_IN_PREFILL = 'cut_in_prefill'
CLOCK_REFERENCE_MISSING = 'clock_reference_missing'
TOKEN_STAMPS_UNAVAILABLE = 'token_stamps_unavailable'
AFTER_HOT_TURN = 'after_hot_turn'
OFF_KINDS = ('os_level_above_0', 'journal_pm_state_off', 'native_pm_state_off', 'hazard_os_level_above_0')
TRUNCATING_STOPS = (('episode.deadman:', 'deadman'), ('thermal.gate_timeout:', 'g1_timeout'),
                    ('episode.decode_budget:', 'decode_budget'))
SCHEMA = 'joulewise.align.s_rows.v2'


@dataclass(frozen=True)
class ClockClause:
    """First window (trailing, inside the decode, from first token + ``start_after_first_token_s``) whose
    activity-weighted mean clock is under ratio x reference; the cut is the window's start."""
    reference: str
    ratio: float = RECORD_RATIO
    window_s: float = RECORD_WINDOW_S
    base_mhz: float | None = None
    start_after_first_token_s: float = 10.0

    def __post_init__(self):
        if self.reference not in CLOCK_REFERENCES:
            raise ValueError(f'clock reference must be one of {CLOCK_REFERENCES}')
        if not (0 < self.ratio <= 1) or not self.window_s > 0:
            raise ValueError('clock clause needs 0 < ratio <= 1 and a positive window')
        if not (self.start_after_first_token_s >= 0 and math.isfinite(self.start_after_first_token_s)):
            raise ValueError('start_after_first_token_s must be finite and nonnegative')
        if self.reference == 'registered_base' and not (self.base_mhz and self.base_mhz > 0):
            raise ValueError('registered_base clock clause needs base_mhz')

    @property
    def reason(self):
        return 'clock_e20' if self.reference == 'leg_max_state' else 'clock_base_e20'


@dataclass(frozen=True)
class RowConstants:
    """The row's constants. ``REGISTERED`` below holds RL-149 section 1.3's values."""
    state: frozenset
    clock: ClockClause | None
    guard_s: float
    # Uncertainty of the summed member term (RL-148 correction 1; RL-149 section 1.3, T7: edge_j = 1.0 J).
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


# RL-149 section 1.3 (RL-151 section 1.1: unchanged): both state keys, e20 against the member's own
# top state, a 2.0 s guard, edges at every row boundary at 1.0 J.
REGISTERED = RowConstants(state=STATE_KEYS, clock=ClockClause('leg_max_state'), guard_s=2.0)


@dataclass(frozen=True)
class JournalReading:
    """One member-journal reading on the episode clock, as S reads it.

    ``t_ns`` is the reading's own stamp (the sample's start, as ``thermal_desk.normalize_journal``),
    ``level`` the OS level when it is an int (else None), ``pm_state`` the journal's state as read
    (None when missing), ``stamp_ok`` whether ``stamp_fresh`` accepts the power-management stamp's
    age at ``t_ns``."""
    t_ns: int
    level: int | None
    pm_state: Any
    stamp_ok: bool

    @property
    def fresh(self):
        """Fresh state (RL-153 section 2.2 item 1 as RL-154 section 3 amends it): an integer level, an
        accepted stamp, and a power-management state that is present and not ``Unknown``."""
        return self.level is not None and self.stamp_ok and self.pm_state not in PM_UNOBSERVED_STATES

    def in_state(self, keys):
        return (('os_level' not in keys or self.level == 0)
                and ('pm_state' not in keys or self.pm_state == 'Nominal'))

    def off_kinds(self, keys):
        kinds = []
        if 'os_level' in keys and self.level is not None and self.level > 0:
            kinds.append('os_level_above_0')
        if 'pm_state' in keys and self.pm_state not in PM_REFERENCE_STATES:
            kinds.append('journal_pm_state_off')
        return kinds


def journal_readings(samples):
    """``JournalReading`` per normalized journal sample (``thermal_desk.normalize_journal`` rows)."""
    out = []
    for sample in samples:
        status = sample.get('status') or {}
        level = status.get('os_level')
        out.append(JournalReading(t_ns=int(sample['monotonic_ns']), level=level if type(level) is int else None,
                                  pm_state=status.get('pm_state'), stamp_ok=stamp_fresh(_status_age_s(sample))))
    return sorted(out, key=lambda r: r.t_ns)


def _as_readings(journal):
    journal = list(journal)
    if all(isinstance(r, JournalReading) for r in journal):
        return sorted(journal, key=lambda r: r.t_ns)
    return journal_readings(journal)


@dataclass(frozen=True)
class Row:
    turn: int
    context_tokens: int
    prefill_tokens: int
    decode_tokens: int            # D': decode tokens stamped by end_ns
    logged_decode_tokens: int     # D: the turn record's decode count
    start_ns: int
    end_ns: int
    reason: str                   # 'turn_end', 'deadman_last_token' or the cut's reason code
    cut: bool                     # end_ns is a cut boundary (not the turn record's own end)
    energy_j: float
    query_half_width_j: float
    energy_flags: tuple = ()


@dataclass(frozen=True)
class MemberRows:
    episode_id: str
    rows: tuple
    no_row: tuple                 # ({'turn', 'reason'}, ...)
    candidates: tuple             # per-turn record: the state rule's pieces and RL-148's record candidates
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
# The state rule (RL-149 section 1.3, RL-153 section 2, RL-154)
# --------------------------------------------------------------------------
def start_state(turn, readings, keys):
    """'ok', 'start_out_of_state' or 'start_state_unobserved' from the last reading at or before the start.

    A carry-in that is not fresh state (a missing or ``Unknown`` state included, RL-154 section 3) or more
    than 2 s before the start is unobserved; fresh state level 0 and Nominal is 'ok'; any other fresh state
    is out of state."""
    before = [r for r in readings if r.t_ns <= turn.start_ns]
    if not before:
        return START_STATE_UNOBSERVED
    carry = before[-1]
    if turn.start_ns - carry.t_ns > START_MAX_AGE_NS or not carry.fresh:
        return START_STATE_UNOBSERVED
    return 'ok' if carry.in_state(keys) else START_OUT_OF_STATE


def state_cut(turn, readings, pm_rows, keys, *, guard_ns, search_end_ns, hazard_os=()):
    """The state's candidate row ends inside (start, search_end]: a list of (end_ns, reason), plus the
    first off reading's time and kind and the state_unobserved reading (for the record)."""
    lo, hi = turn.start_ns, search_end_ns
    first = {}
    for r in readings:
        if lo < r.t_ns <= hi:
            for kind in r.off_kinds(keys):
                first.setdefault(kind, r.t_ns)
    if 'pm_state' in keys:
        for row in sorted(pm_rows, key=lambda x: x['end_ns']):
            if lo < row['end_ns'] <= hi and row.get('state') not in PM_REFERENCE_STATES:
                first.setdefault('native_pm_state_off', row['end_ns'])
                break
    if 'os_level' in keys:
        for t, level in sorted(hazard_os, key=lambda x: x[0]):
            if lo < t <= hi and type(level) is int and level > 0:
                first.setdefault('hazard_os_level_above_0', t)
                break
    candidates = []
    first_off = min(first.values()) if first else None
    why = None
    if first_off is not None:
        why = '+'.join(sorted(k for k, t in first.items() if t == first_off))
        last_in = max((r.t_ns for r in readings if r.t_ns < first_off and r.fresh and r.in_state(keys)),
                      default=lo)
        candidates.append((min(first_off - guard_ns, last_in), why))
    before = [r for r in readings if r.t_ns <= lo]
    # RL-154 finding 1: the first anchor is the carry-in when it is fresh state, else the turn's start.
    fresh_t = [before[-1].t_ns if before and before[-1].fresh else lo]
    fresh_t += [r.t_ns for r in readings if lo < r.t_ns <= hi and r.fresh]
    unobserved = None
    for a, b in zip(fresh_t, fresh_t[1:] + [hi]):
        if b - a > UNOBSERVED_GAP_NS:
            unobserved = a
            break
    if unobserved is not None:
        candidates.append((unobserved, STATE_UNOBSERVED))
    return candidates, first_off, why, unobserved


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


def clock_cut(pm_rows, clause, reference_mhz, *, first_token_ns, decode_end_ns):
    """(window start, window end) of the first e20 window that fires, or None."""
    if clause is None or not reference_mhz or reference_mhz <= 0 or first_token_ns is None:
        return None
    window_ns = round(clause.window_s * NS)
    earliest = first_token_ns + round(clause.start_after_first_token_s * NS)
    rows = sorted(pm_rows, key=lambda r: r['end_ns'])
    for r in rows:
        end = r['end_ns']
        if end - window_ns < earliest or end > decode_end_ns:
            continue
        mean = _trailing_clock(rows, end, window_ns)
        if mean is not None and mean < clause.ratio * reference_mhz:
            return end - window_ns, end
    return None


# --------------------------------------------------------------------------
# RL-148's record-only candidates (they print; they decide nothing)
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


def _first_clock_under(turn, pm_rows, reference_mhz, ratio, window_s):
    if reference_mhz is None or reference_mhz <= 0:
        return None
    rows = sorted(pm_rows, key=lambda r: r['end_ns'])
    window_ns = round(window_s * NS)
    for r in rows:
        t = r['end_ns']
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


def member_rows(episode, *, token_stamps, finish_reasons, journal, pm_rows, constants, hazard_os=(),
                source='powermetrics', channel='gpu_power'):
    """Reference-state rows of one member.

    ``token_stamps``: {turn index: [episode ns of decode token 1, 2, ...]} (absent: unavailable).
    ``finish_reasons``: {turn index: the turn's ``align_turns.jsonl`` finish reason}.
    ``journal``: the member journal on the episode clock, as normalized samples
    (``thermal_desk.normalize_journal``: ``monotonic_ns`` and ``status`` with ``os_level``, ``pm_state``,
    ``pm_observed_ns``) or as ``JournalReading``. ``pm_rows``: native PM rows on the episode clock
    ({start_ns, end_ns, state, active_ns, clock_mhz[, max_state_mhz]}). ``hazard_os``: [(episode ns,
    OS level)] from a hazard journal; it only adds cuts.
    """
    if not isinstance(constants, RowConstants):
        raise TypeError('constants must be RowConstants')
    readings = _as_readings(journal)
    keys = constants.state
    flags = []
    trace, mapping, trace_flags = _select_trace(episode, source, channel)
    flags.extend(trace_flags)
    intervals = (episode.hardware.get('thermal') or {}).get('intervals', ())
    leg_max = leg_max_state_mhz(pm_rows)
    clause = constants.clock
    base = clause.base_mhz if clause is not None else None
    reference = None if clause is None else (clause.base_mhz if clause.reference == 'registered_base' else leg_max)
    # RL-154 finding 3: a clock clause with no reference gives no row (the clause never switches itself off).
    reference_missing = clause is not None and not (reference is not None and reference > 0)
    if reference_missing:
        flags.append('s_rows.' + CLOCK_REFERENCE_MISSING)
    guard_ns = round(constants.guard_s * NS)
    record_os = sorted([(r.t_ns, r.level) for r in readings] + list(hazard_os), key=lambda x: x[0])
    rows, no_row, record = [], [], []
    hot_before = False
    for turn in episode.turns:
        stamps = token_stamps.get(turn.index)
        stamps = None if stamps is None else sorted(int(s) for s in stamps)
        first_token = stamps[0] if stamps else turn.first_token_ns
        search_end = stamps[-1] if stamps else turn.end_ns
        start = start_state(turn, readings, keys)
        candidates, first_off, off_kind, unobserved = state_cut(
            turn, readings, pm_rows, keys, guard_ns=guard_ns, search_end_ns=search_end, hazard_os=hazard_os)
        window = clock_cut(pm_rows, clause, reference, first_token_ns=first_token, decode_end_ns=search_end)
        if window is not None:
            candidates.append((window[0], clause.reason))
        cut_t, cut_name = min(candidates) if candidates else (None, None)
        hot = start == START_OUT_OF_STATE or cut_t is not None
        deadman_cut = finish_reasons.get(turn.index) == 'episode.deadman'
        entry = {'turn': turn.index, 'start_state': start, 'first_off_ns': first_off, 'off_kind': off_kind,
                 'state_unobserved_ns': unobserved, 'clock_window_ns': window, 'clock_reference_mhz': reference,
                 'active_cut': cut_name, 'active_cut_ns': cut_t, 'hot': hot, 'after_hot': hot_before,
                 'deadman_cut': deadman_cut, 'logged_decode_tokens': turn.decode_tokens,
                 'candidates_ns': turn_candidates(turn, os_readings=record_os, pm_rows=pm_rows,
                                                  base_mhz=base, leg_max_mhz=leg_max)}
        record.append(entry)
        after_hot = hot_before
        hot_before = hot_before or hot

        def refuse(reason):
            no_row.append({'turn': turn.index, 'reason': reason})
            entry['row'] = None
            entry['no_row'] = reason

        if reference_missing:
            refuse(CLOCK_REFERENCE_MISSING)
            continue
        if after_hot:
            refuse(AFTER_HOT_TURN)
            continue
        if turn.decode_tokens == 0 or (stamps is not None and not stamps):
            # RL-148 correction 4: no row whatever the record says about prompt tokens.
            refuse('deadman_before_first_token' if deadman_cut else 'no_decode_token')
            continue
        if stamps is not None and len(stamps) != turn.decode_tokens:
            refuse('token_stamps_count_mismatch')
            continue
        if start != 'ok':
            refuse(start)
            continue
        if stamps is None:
            # RL-160 D5: a row needs at least one stamped decode token, cut or not. Every stamp is at or
            # after the prefill-end stamp, so a cut before it needs none. The search to the record's end
            # above decides hot only.
            early = cut_t is not None and turn.first_token_ns is not None and cut_t < turn.first_token_ns
            refuse(CUT_IN_PREFILL if early else TOKEN_STAMPS_UNAVAILABLE)
            continue
        if cut_t is None and not deadman_cut:
            end, d_prime, reason, cut = turn.end_ns, turn.decode_tokens, 'turn_end', False
        else:
            if cut_t is not None:
                # The search ends at the last stamp and every candidate lies before it.
                d_prime, reason = bisect_right(stamps, cut_t), cut_name
            else:
                d_prime, reason = len(stamps), 'deadman_last_token'
            if d_prime == 0:
                refuse(CUT_IN_PREFILL)
                continue
            end, cut = stamps[d_prime - 1], True
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
    """B7 item 7 print: rows and decode tokens scored against the member's logged turns, and the turns
    lost to ``after_hot_turn`` (no outcome word)."""
    turns = len(member.candidates)
    logged = sum(e['logged_decode_tokens'] for e in member.candidates)
    scored = sum(r.decode_tokens for r in member.rows)
    return {'rows': len(member.rows), 'turns': turns, 'row_share': len(member.rows) / turns if turns else None,
            'decode_scored': scored, 'decode_logged': logged,
            'decode_share': scored / logged if logged else None,
            'after_hot_turn': sum(1 for x in member.no_row if x['reason'] == AFTER_HOT_TURN)}


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


def hazard_os_readings(hazard_journal):
    """[(episode ns, level)] from a hazard journal's readings; they only add cuts (RL-153 section 2.2 item 5)."""
    return [(r['finished']['monotonic_ns'], r['values'].get('level')) for r in hazard_journal
            if r.get('kind') == 'reading' and not r.get('error')]


def read_member_rows(bundle, constants, *, hazard_journal=(), pm_rows=None):
    """Rows for one bundle, failed executions included. Reads no condition label and no transcript.

    The start's evidence and the gap rule come from the member journal (``outputs/align_thermal.jsonl``)
    only; a hazard journal adds cuts."""
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
    readings = journal_readings(normalize_journal(_jsonl(bundle / 'outputs/align_thermal.jsonl') or []))
    hazard = hazard_os_readings(hazard_journal)
    if pm_rows is None:
        pm_rows = pm_rows_with_states(bundle, episode)
    member = member_rows(episode, token_stamps=stamps, finish_reasons=finish, journal=readings,
                         pm_rows=pm_rows, constants=constants, hazard_os=hazard)
    return member, {'token_stamp_source': stamp_source, 'failed_execution': runtime is not None,
                    'journal_readings': len(readings), 'fresh_readings': sum(r.fresh for r in readings),
                    'hazard_os_readings': len(hazard), 'pm_rows': len(pm_rows)}


__all__ = ['ClockClause', 'RowConstants', 'REGISTERED', 'JournalReading', 'journal_readings', 'Row',
           'MemberRows', 'CANDIDATES', 'OFF_KINDS', 'start_state', 'state_cut', 'clock_cut', 'turn_candidates',
           'member_rows', 'boundary_table', 'sequence_design', 'loso_scores', 'bundle_token_stamps',
           'pm_rows_with_states', 'hazard_os_readings', 'read_member_rows', 'scored_shares', 'ended_by',
           'leg_max_state_mhz']
