"""Completed-top-up evidence derived from a logged battery record (Opus cold MED-3).

The 1800 s bound of AGREEMENT-FINAL R02 / protocol section 4 stays. What counts as
evidence is defined here, and is derived from a log of ``battery_float.observe``
records, never from a hand-entered time:

(a) ``completed_charge``: the log shows a completed charge, a charging observation
    followed by a not-charging observation at or above ``FLOAT_MIN_PCT`` on AC, and
    the arm is within 1800 s of that completion;
(b) ``continuous_float``: since the last completed charge every observation is on AC,
    not charging, at or above ``FLOAT_MIN_PCT`` with no gap above ``max_gap_s``, and the
    latest observation is fresh. The evidence time is the latest qualifying observation.

``FLOAT_MIN_PCT`` is the arm bar (99 %) so the log and the live arm predicate agree.
Optimized Battery Charging has no mechanical read here, so the operator attestation
(``--obc-off-attested-by``) stays an arm requirement for basis (b) as for (a). Pure
stdlib; reads only the supplied log file.
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


def _qualifying(row):
    return (row.get('schema') == SCHEMA and row.get('probe_error') is False and _finite(row.get('wall_time_s'))
            and row.get('external_connected') is True and type(row.get('is_charging')) is bool
            and _finite(row.get('current_capacity_pct')))


def _floating(row):
    return row['is_charging'] is False and row['current_capacity_pct'] >= FLOAT_MIN_PCT


def derive(records, now_epoch_s, *, log_sha256=None, max_gap_s=MAX_GAP_S):
    """Evidence for the arm at ``now_epoch_s`` (a clock reading the arm took itself)."""
    base = {'admissible': False, 'basis': None, 'completed_at_epoch_s': None, 'source': None,
            'log_sha256': log_sha256, 'observations': len(records), 'topup_window_s': TOPUP_WINDOW_S,
            'float_min_pct': FLOAT_MIN_PCT, 'max_gap_s': max_gap_s, 'reasons': []}
    if not _finite(now_epoch_s):
        return {**base, 'reasons': ['arm time unavailable']}
    good = [r for r in records if _qualifying(r)]
    times = [r['wall_time_s'] for r in good]
    if not good:
        return {**base, 'reasons': ['no usable on-AC observation in the battery log']}
    if any(b <= a for a, b in zip(times, times[1:])):
        return {**base, 'reasons': ['battery log observations are not strictly increasing in time']}
    if times[-1] > now_epoch_s:
        return {**base, 'reasons': ['battery log has an observation after the arm time']}
    events = [i for i in range(1, len(good))
              if good[i-1]['is_charging'] is True and _floating(good[i])]
    if not events:
        return {**base, 'reasons': ['no completed charge (charging then floating) in the battery log']}
    last = events[-1]
    run = good[last:]
    since = good[last]['wall_time_s']
    if any(not _qualifying(r) for r in records if _finite(r.get('wall_time_s')) and r['wall_time_s'] > since):
        return {**base, 'reasons': ['a probe error or off-AC observation since the last completed charge']}
    if not all(_floating(r) for r in run):
        return {**base, 'reasons': ['the battery is not floating after the last completed charge']}
    if any(b['wall_time_s']-a['wall_time_s'] > max_gap_s for a, b in zip(good[last-1:], good[last:])):
        return {**base, 'reasons': [f'gap above {max_gap_s:g} s since the last completed charge']}
    if now_epoch_s-times[-1] > max_gap_s:
        return {**base, 'reasons': ['the latest battery observation is stale at the arm time']}
    completed = good[last]['wall_time_s']
    if now_epoch_s-completed <= TOPUP_WINDOW_S:
        basis, stamp = 'completed_charge', completed
    else:
        basis, stamp = 'continuous_float', times[-1]
    return {**base, 'admissible': True, 'basis': basis, 'completed_at_epoch_s': stamp,
            'source': f'battery_log:{basis}:{(log_sha256 or "unhashed")[:16]}',
            'completed_charge_epoch_s': completed, 'latest_observation_epoch_s': times[-1]}


def derive_from_file(path, now_epoch_s, **kwargs):
    try:
        records, digest = load_log(path)
    except (OSError, ValueError) as exc:
        return {'admissible': False, 'basis': None, 'completed_at_epoch_s': None, 'source': None,
                'log_sha256': None, 'reasons': [f'battery log unreadable: {exc}']}
    return derive(records, now_epoch_s, log_sha256=digest, **kwargs)
