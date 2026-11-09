"""Lead ruling R22-1 (RUN_STATE 234): in-window contention in v4 is DISCLOSURE-ONLY.

Block 5's rule (0.05 CPU-s/s per 10 s, applied as an exclusion) is never used: at v4's roughly
830 s active episodes it would flag more than 99.7 % of members. Instead:

* every member records its outside-tree CPU-seconds over its member span (from the monitor's
  contention journal, kernel_task excluded as the monitor already does);
* a ``contention.unmeasured`` gap in that journal coverage is bounded: a gap over 30 s is flagged and
  disclosed, never excluded;
* no ``contention.*`` code can exclude a member: :func:`split_codes` moves them out of every
  exclusion list before eligibility is derived (desk and committed-record reader alike).

Pure functions over explicit journal lines; no clock, process or hardware access.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

PREFIX = 'contention.'
GAP_DISCLOSE_S = 30.0
UNMEASURED = 'contention.unmeasured'
NS = 1_000_000_000


def is_disclosure_only(code):
    return isinstance(code, str) and code.startswith(PREFIX)


def split_codes(codes):
    """(exclusion codes, disclosed contention codes): contention can never exclude a member."""
    codes = list(codes or ())
    return ([c for c in codes if not is_disclosure_only(c)], [c for c in codes if is_disclosure_only(c)])


def exclusion_map(entries):
    """run id -> sorted distinct codes, or None when the entries are not a well-formed list."""
    if not isinstance(entries, list):
        return None
    out = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get('run_id'), str) or not isinstance(entry.get('codes'), list):
            return None
        out[entry['run_id']] = sorted(set(out.get(entry['run_id'], [])) | {str(c) for c in entry['codes']})
    return out


def recorded_exclusion_map(record):
    """A desk's or PILOT.json's own record of exclusions, disclosure-aware (R22-1), or None if malformed.

    ``members_excluded`` plus the common desk's ``members_disclosure_only`` ({run id: contention codes}),
    merged per member. The ONE definition shared by the packet builder's ``effective_desk`` and by R17
    finality (``light_triage.final_adjudication_error``): contention is recorded as disclosure, never as an
    exclusion, so the record must be read together with its disclosure map before it is compared with the
    committed harvest exclusions. A missing ``members_excluded`` reads as no exclusions.
    """
    own = exclusion_map(record.get('members_excluded') if 'members_excluded' in record else [])
    disclosed = record.get('members_disclosure_only')
    if own is not None and isinstance(disclosed, dict):
        for run_id, codes in disclosed.items():
            own[run_id] = sorted(set(own.get(run_id, [])) | {str(c) for c in (codes if isinstance(codes, list) else [])})
    return own


def records_agree_with_harvest(record, harvest_entries):
    """Whether the record's exclusions (disclosure included) equal the harvest's: same members, same codes."""
    harvest = exclusion_map(harvest_entries)
    own = recorded_exclusion_map(record)
    return harvest is not None and own is not None and own == harvest


def load_journal(path):
    """Explicit closed contention journal: (interval values, sha256, malformed-line count)."""
    from joulewise.desk_compress import read_bytes
    from joulewise.hazards.monitor import contention_intervals
    import hashlib
    try:
        raw = read_bytes(Path(path))
    except (OSError, ValueError, TypeError):
        return [], None, 1
    lines, malformed = [], 0
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            malformed += 1
            continue
        if isinstance(row, dict) and row.get('module', 'contention') == 'contention':
            lines.append(row)
    try:
        intervals = contention_intervals(lines)
    except (KeyError, TypeError, ValueError):
        return [], hashlib.sha256(raw).hexdigest(), malformed + 1
    return intervals, hashlib.sha256(raw).hexdigest(), malformed


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def disclose(intervals, span_ns, *, gap_disclose_s=GAP_DISCLOSE_S):
    """Outside-tree CPU-seconds and unmeasured coverage gaps over one member span.

    ``intervals``: contention journal interval values (``interval.monotonic_ns`` [a, b],
    ``outside_total_cpu_s_per_s``, ``error``); ``span_ns``: ``[start, stop]`` in the same domain.
    Always ``excludes: False``.
    """
    start, stop = span_ns
    cpu_s, covered = 0.0, []
    for item in intervals:
        a, b = item['interval']['monotonic_ns']
        lo, hi = max(a, start), min(b, stop)
        if hi <= lo:
            continue
        rate = item.get('outside_total_cpu_s_per_s')
        if item.get('error') or not _finite(rate):
            continue                                   # missing evidence leaves coverage open
        cpu_s += rate * (hi - lo) / NS
        covered.append((lo, hi))
    gaps, cursor = [], start
    for lo, hi in sorted(covered):
        if lo > cursor:
            gaps.append([cursor, lo])
        cursor = max(cursor, hi)
    if cursor < stop:
        gaps.append([cursor, stop])
    longest = max(((b - a) / NS for a, b in gaps), default=0.0)
    flagged = longest > gap_disclose_s
    return {'rule': 'R22-1 disclosure only', 'excludes': False,
            'outside_cpu_s': cpu_s, 'span_s': (stop - start) / NS,
            'unmeasured_gaps': gaps, 'max_unmeasured_gap_s': longest,
            'flags': [UNMEASURED] if flagged else []}


def bundle_disclosure(bundle, journal):
    """The R22-1 record of one bundle: its member span (controller clock) against the journal."""
    from joulewise.b5.harvest import member_spans
    from joulewise.desk_compress import read_bytes
    intervals, source, malformed = journal
    result = {'rule': 'R22-1 disclosure only', 'excludes': False, 'status': 'unavailable',
              'source_sha256': source, 'outside_cpu_s': None, 'flags': []}
    try:
        spans = member_spans(json.loads(read_bytes(Path(bundle) / 'metadata.json')),
                             [json.loads(line) for line in read_bytes(Path(bundle) / 'events.jsonl').splitlines()
                              if line.strip()])
        if spans['member'] is None or source is None:
            result['reason'] = 'missing journal or controller span'
            return result
        result.update(disclose(intervals, spans['member']), status='observed', source_sha256=source,
                      malformed_lines=malformed)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result['reason'] = type(exc).__name__ + ': ' + str(exc)
    return result


def attach(record, bundle, journal):
    """Record the member's contention disclosure; strip contention from every exclusion list.

    Contention flags (the shared catalog's ``contention.request_overlap`` / ``contention.unmeasured``
    are EXCLUDE_MEMBER there) are moved to ``record['contention']['disclosed_codes']``; the member's
    ``calibration_exclusions`` keep only non-contention codes and ``excluded`` is recomputed.
    """
    evidence = bundle_disclosure(bundle, journal)
    kept, disclosed = split_codes(record.get('calibration_exclusions'))
    evidence['disclosed_codes'] = sorted(set(disclosed) | set(evidence.get('flags', ())))
    record['contention'] = evidence
    record['calibration_exclusions'] = kept
    record['excluded'] = bool(kept)
    return record
