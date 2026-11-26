"""Completed-top-up evidence derived from a logged battery record (Opus cold MED-3, delta2).

The 1800 s bound of AGREEMENT-FINAL R02 / protocol section 4 stays. What counts as
evidence is defined here, and is derived from a log of ``battery_float.observe``
records, never from a hand-entered time. The log is read **in its raw order**: a row
that is invalid (probe error), untimed, off AC or out of order is never filtered away;
it breaks whatever interval it falls in.

A *completed charge* is a pair of **consecutive** valid timed rows, a charging one then
a not-charging one at or above ``FLOAT_MIN_PCT`` on AC, no more than ``max_gap_s``
apart; the completion time is the second row's. The last such pair is the event.

(a) ``completed_charge``: the arm is within 1800 s of the event, no valid row after it
    is charging, and the latest valid row is fresh and floating. Nothing else is required
    (no continuity rule): the live arm predicate re-checks AC, SoC, charging and current.
(b) ``continuous_float``: older than 1800 s, every row after the event is valid, timed,
    on AC, not charging and at or above ``FLOAT_MIN_PCT``, with no gap above
    ``max_gap_s`` through the latest row, which must be fresh. The evidence time is the
    latest qualifying observation.

Operating procedure (lead ruling: no sampler during a window). Between windows
``scripts/align_v4_battery_log.py sample --loop`` runs from terminal completion until just
before the arm dwell (start and stop are part of the magistrate sequence). Across a window,
float evidence comes from the window's own 1 Hz hazard battery journal (SMC ``B0AC`` lines
plus the ioreg lines that carry AC, charging and SoC), converted by ``window_records`` into
the same observation shape and merged in time order with the between-window log(s). A gap at
a window boundary above ``max_gap_s``, or a missing window journal, breaks continuity as
before: it costs only basis (b) until the next completed charge. ``FLOAT_MIN_PCT`` is the arm
bar (99 %). Optimized Battery Charging has no mechanical read here, so the operator attestation
(``--obc-off-attested-by``) stays an arm requirement. Pure stdlib; reads only the log.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

SCHEMA = 'joulewise.battery_float.v1'
TOPUP_WINDOW_S = 30*60
FLOAT_MIN_PCT = 99
MAX_GAP_S = 300.0
JOURNAL_SCHEMA = 'joulewise.hazard_journal.v1'
SMC_CHARGING_MA = 200      # joulewise.hazards.battery limit: B0AC above +200 mA is charging


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def load_log(path):
    """(records, sha256 of the file bytes). Unparseable lines make the log inadmissible."""
    raw = Path(path).read_bytes()
    records = []
    for number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            raise ValueError(f'battery log line {number} is not JSON') from exc
        if not isinstance(row, dict):
            raise ValueError(f'battery log line {number} is not an object')
        records.append(row)
    return records, hashlib.sha256(raw).hexdigest()


def _valid(row):
    """A usable timed observation (not whether it floats)."""
    return (isinstance(row, dict) and row.get('schema') == SCHEMA and row.get('probe_error') is False
            and _finite(row.get('wall_time_s')) and row.get('external_connected') is True
            and type(row.get('is_charging')) is bool and _finite(row.get('current_capacity_pct')))


def _floating(row):
    return _valid(row) and row['is_charging'] is False and row['current_capacity_pct'] >= FLOAT_MIN_PCT


def derive(records, now_epoch_s, *, log_sha256=None, max_gap_s=MAX_GAP_S):
    """Evidence for the arm at ``now_epoch_s`` (a clock reading the arm took itself)."""
    base = {'admissible': False, 'basis': None, 'completed_at_epoch_s': None, 'source': None,
            'log_sha256': log_sha256, 'observations': len(records), 'topup_window_s': TOPUP_WINDOW_S,
            'float_min_pct': FLOAT_MIN_PCT, 'max_gap_s': max_gap_s, 'reasons': []}

    def refuse(reason):
        return {**base, 'reasons': [reason]}

    if not _finite(now_epoch_s):
        return refuse('arm time unavailable')
    timed = [r['wall_time_s'] for r in records if isinstance(r, dict) and _finite(r.get('wall_time_s'))]
    if any(b <= a for a, b in zip(timed, timed[1:])):
        return refuse('battery log observations are not strictly increasing in time')
    if timed and timed[-1] > now_epoch_s:
        return refuse('battery log has an observation after the arm time')
    # Completed-charge events: consecutive raw rows, both valid; nothing between them can vanish.
    events = [i for i in range(1, len(records))
              if _valid(records[i-1]) and records[i-1]['is_charging'] is True and _floating(records[i])
              and records[i]['wall_time_s']-records[i-1]['wall_time_s'] <= max_gap_s]
    if not events:
        return refuse('no completed charge (consecutive charging then floating observations) in the battery log')
    last = events[-1]
    completed = records[last]['wall_time_s']
    after = records[last+1:]
    valid_after = [r for r in after if _valid(r)]
    latest = valid_after[-1] if valid_after else records[last]
    if now_epoch_s-latest['wall_time_s'] > max_gap_s:
        return refuse('the latest valid battery observation is stale at the arm time')
    if any(r['is_charging'] is True for r in valid_after):
        return refuse('the battery is charging again after the last completed charge')
    if not _floating(latest):
        return refuse('the latest battery observation is not floating')
    common = {'completed_charge_epoch_s': completed, 'latest_observation_epoch_s': latest['wall_time_s']}
    if now_epoch_s-completed <= TOPUP_WINDOW_S:
        stamp, basis = completed, 'completed_charge'
    else:
        chain = records[last:]
        if not all(_floating(r) for r in chain):
            return refuse('a probe error, untimed, off-AC or non-floating row since the last completed charge')
        if any(b['wall_time_s']-a['wall_time_s'] > max_gap_s for a, b in zip(chain, chain[1:])):
            return refuse(f'gap above {max_gap_s:g} s since the last completed charge')
        stamp, basis = latest['wall_time_s'], 'continuous_float'
    return {**base, 'admissible': True, 'basis': basis, 'completed_at_epoch_s': stamp,
            'source': f'battery_log:{basis}:{(log_sha256 or "unhashed")[:16]}', **common}


def _nonbool_int(value):
    return type(value) is int


def window_records(rows):
    """battery_float-shaped observations from one window's hazard battery journal.

    ``rows`` are the journal's JSON rows (``module`` ``battery``, ``kind`` ``reading``). An ioreg
    line gives AC, charging and SoC (and becomes the carried state); an SMC-only line
    (``values.source`` ``smc``, 1 Hz) gives B0AC and takes AC and SoC from the latest ioreg line, so
    ``is_charging`` is B0AC above 200 mA. The monitor writes an ioreg line whenever a polled field
    changes, so the carried state is current. A line that cannot be used (error, missing B0AC,
    no state yet, malformed stamp) becomes an invalid row, never a deleted one.
    """
    out, state = [], None
    for row in rows:
        if (not isinstance(row, dict) or row.get('schema') != JOURNAL_SCHEMA or row.get('module') != 'battery'
                or row.get('kind') != 'reading'):
            if isinstance(row, dict) and row.get('module') == 'battery' and row.get('kind') in ('session_start', 'session_end'):
                continue
            out.append({'schema': SCHEMA, 'probe_error': True, 'wall_time_s': None, 'source': 'window_journal'})
            continue
        stamp = (row.get('finished') or {}).get('wall_ns')
        wall = stamp / 1e9 if _nonbool_int(stamp) else None
        values = row.get('values') if isinstance(row.get('values'), dict) else {}
        invalid = {'schema': SCHEMA, 'probe_error': True, 'wall_time_s': wall, 'source': 'window_journal'}
        if values.get('source') == 'smc':
            sample = values.get('smc') if isinstance(values.get('smc'), dict) else {}
            current = (sample.get('values') or {}).get('B0AC')
            if (row.get('error') or (sample.get('errors') or {}).get('B0AC') or not _nonbool_int(current)
                    or state is None or wall is None):
                out.append(invalid)
                continue
            out.append({'schema': SCHEMA, 'probe_error': False, 'wall_time_s': wall, 'source': 'window_journal',
                        'external_connected': state['external_connected'], 'is_charging': current > SMC_CHARGING_MA,
                        'current_capacity_pct': state['current_capacity_pct'], 'instant_amperage_ma': current})
            continue
        needed = ('external_connected', 'is_charging', 'current_capacity_pct')
        if row.get('error') or wall is None or any(k not in values for k in needed):
            out.append(invalid)
            continue
        state = {'external_connected': values['external_connected'], 'current_capacity_pct': values['current_capacity_pct']}
        out.append({'schema': SCHEMA, 'probe_error': False, 'wall_time_s': wall, 'source': 'window_journal',
                    'external_connected': values['external_connected'], 'is_charging': values['is_charging'],
                    'current_capacity_pct': values['current_capacity_pct'],
                    'instant_amperage_ma': values.get('instant_amperage_ma')})
    return out


def merge_in_time_order(*sources):
    """Merge record lists by ``wall_time_s``. An untimed row stays right after its predecessor in its own source."""
    keyed = []
    for index, records in enumerate(sources):
        last = -math.inf
        for position, row in enumerate(records):
            when = row.get('wall_time_s') if isinstance(row, dict) else None
            if _finite(when):
                last = when
            keyed.append((last, index, position, row))
    keyed.sort(key=lambda item: item[:3])
    return [item[3] for item in keyed]


def derive_from_sources(logs, journals, now_epoch_s, **kwargs):
    """Evidence from the between-window log file(s) merged with the window hazard battery journal(s)."""
    sources, digests = [], []
    try:
        for path in logs or ():
            records, digest = load_log(path)
            sources.append(records)
            digests.append(digest)
        for path in journals or ():
            records, digest = load_log(path)
            sources.append(window_records(records))
            digests.append(digest)
    except (OSError, ValueError) as exc:
        return {'admissible': False, 'basis': None, 'completed_at_epoch_s': None, 'source': None,
                'log_sha256': None, 'reasons': [f'battery evidence unreadable: {exc}']}
    # Raw order per source first (delta4 S1 F1): a source whose clock goes backwards or repeats is refused
    # BEFORE merging, so sorting can never repair a regression into a completed-charge transition.
    for index, records in enumerate(sources):
        timed = [r['wall_time_s'] for r in records if isinstance(r, dict) and _finite(r.get('wall_time_s'))]
        if any(b <= a for a, b in zip(timed, timed[1:])):
            kind = 'between-window log' if index < len(logs or ()) else 'window journal'
            return {'admissible': False, 'basis': None, 'completed_at_epoch_s': None, 'source': None,
                    'log_sha256': None, 'observations': sum(len(r) for r in sources),
                    'reasons': [f'battery {kind} {index} observations are not strictly increasing in time '
                                '(raw order, before merging)'],
                    'sources': {'between_window_logs': len(logs or ()), 'window_journals': len(journals or ()),
                                'source_sha256': digests}}
    combined = hashlib.sha256(''.join(digests).encode()).hexdigest() if len(digests) != 1 else digests[0]
    result = derive(merge_in_time_order(*sources), now_epoch_s, log_sha256=combined, **kwargs)
    result['sources'] = {'between_window_logs': len(logs or ()), 'window_journals': len(journals or ()),
                         'source_sha256': digests}
    return result


def derive_from_file(path, now_epoch_s, **kwargs):
    try:
        records, digest = load_log(path)
    except (OSError, ValueError) as exc:
        return {'admissible': False, 'basis': None, 'completed_at_epoch_s': None, 'source': None,
                'log_sha256': None, 'reasons': [f'battery log unreadable: {exc}']}
    return derive(records, now_epoch_s, log_sha256=digest, **kwargs)
