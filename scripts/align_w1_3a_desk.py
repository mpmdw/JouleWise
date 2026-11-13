#!/usr/bin/env python3
"""RL-122 item 3(a) planning-release desk (desk print for the lead's record).

Input: a closed R1 night's output dir (the dir holding ``<phase>/runs/<run>/
outputs/align_thermal.jsonl``; ``r1_result.json`` is optional). Read-only:
only temperature journals, the member ``config.json`` thermal policy and the
``r1_result.json`` band field are opened; no energy, power or episode file.

For every G0 interval it prints the turn label, outcome and duration, the
heater key (the session's ``s_slow``: the planning heater regulates it,
r1_runtime.py planning_hook), the target (the gate's ``reference.slow_c``;
for a planning turn that is the soak reference + R+n offset, r1_runtime.py
k_planning/planning_hook), the band edge (target + ``delta_slow_c``, the
release clause in thermal_gates.py ``_wait``), the heater key's peak over the
last 300 s of the interval and its margin to (band edge - 0.3), the whole-G0
peak (disclosure only, not the 3(a) pattern), the OS thermal level maximum and
whether the state was Nominal throughout.

Classification of each G0 timeout (RL-122 item 3(a) and its 2026-11-13
amendment):

* ``planning-release-3a``: planning turn R+0, R+2 or R+4, OS level 0 and
  Nominal throughout, and the heater key's last-300-s peak >= band edge - 0.3.
* ``to-research-lead``: anything else, with the reasons. This includes: the
  preceding idle-until-soak phase (``cooldown_after_D`` for R+4, ``<turn>.precool``
  for R+2/R+0) not reporting ``released: true`` in ``r1_result.json`` or the file
  being absent (RL-124 5(a)); fewer than 270 valid heater-key samples in the last
  300 s; a band from ``--delta-slow-c`` (display only); unobserved/deadman exits;
  duplicate rows under one kit segment name. Superseded attempts (``.rejectedN``,
  ``.g0_timeoutN``) are classified by the same rule, labelled, never emitted.

A released G0 is classified ``released`` (nothing to rule). The output is
deterministic: no wall clock, sorted keys. ``kit_record_segments`` carries the
rows the W1 kit's ``r1_planning_release.json`` expects for the 3(a) segments
(align_v4_kit.py ``planning_released_segments``); the lead signs and cites
this desk print's sha256 in the record. This tool never writes the record.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

NS = 1_000_000_000
WINDOW_S = 300            # RL-122 amendment: last 300 s of the G0 interval
EDGE_C = 0.3              # RL-122 3(a): within 0.3 C under the band edge, or crossing it
PEAK_FIELD = 'heater_key_max_last_300s_c'   # align_v4_kit.PLANNING_RELEASE_PEAK_FIELD
SCHEMA = 'joulewise.align_w1_3a_desk.v1'
JOURNAL = 'align_thermal.jsonl'
# The night's planning members, plus the scratch-copy suffixes custody adds and
# the driver's superseded-attempt rename (<name>.rejectedN, r1_rehearsal.py).
PLANNING = re.compile(r'^planning_turn_R_plus_(\d+)C(?P<suffix>\.g0_(?:timeout|release)\d+|\.rejected\d+)?$')
PLANNING_OFFSETS = (0, 2, 4)
MIN_LAST_SAMPLES = 270    # RL-124 item 2: the gate's own 0.9 coverage of 300 s
FRESH_NS = 2 * NS         # thermal_gates.py: pm observation <= 2 s old
CLASS_RELEASED, CLASS_3A, CLASS_LEAD = 'released', 'planning-release-3a', 'to-research-lead'
KIT_SEGMENTS = tuple(f'planning_turn_R_plus_{n}C' for n in PLANNING_OFFSETS)
OVERRIDE_SOURCE = '--delta-slow-c'


class DeskError(RuntimeError):
    pass


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def valid_temp(value):
    return finite(value) and -40 <= value <= 150


def r6(value):
    return None if value is None else round(float(value), 6)


def median(values):
    ordered = sorted(values)
    n = len(ordered)
    if not n:
        return None
    return ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def sha256_file(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def turn_info(phase):
    """(label, planning turn?, superseded?, base phase name)."""
    match = PLANNING.match(phase)
    if match and int(match.group(1)) in PLANNING_OFFSETS:
        base = phase[:match.start('suffix')] if match.group('suffix') else phase
        return f'planning R+{int(match.group(1))}', True, bool(match.group('suffix')), base
    return phase, False, False, phase


def precool_phase(base):
    """The idle-until-soak phase just before a planning turn (r1_phase_table.phase_plan)."""
    return 'cooldown_after_D' if base == 'planning_turn_R_plus_4C' else base + '.precool'


def read_journal(path):
    """Project one thermal journal: session keys, G0 end rows, reading rows."""
    start, gates, readings = None, [], []
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        kind, values = row.get('kind'), row.get('values') or {}
        if kind == 'session_start':
            start = values.get('thermal') or {}
        elif kind == 'align_thermal_gate' and values.get('state') == 'end':
            gate = values.get('gate') or {}
            if gate.get('kind') == 'G0':
                gates.append(gate)
        elif kind == 'reading':
            readings.append(row)
    if start is None:
        raise DeskError(f'{path}: no session_start row')
    return start, gates, readings


def sample_points(readings, key):
    """(monotonic_ns, value or None, os_level, pm_state, pm_observed_ns) per reading; time is the read start."""
    out = []
    for row in readings:
        values = row.get('values') or {}
        value = (values.get('sensors') or {}).get(key)
        if key in (values.get('errors') or {}) or not valid_temp(value):
            value = None
        status = values.get('status') if isinstance(values.get('status'), dict) else {}
        out.append((row['started']['monotonic_ns'], value, status.get('os_level'), status.get('pm_state'),
                    status.get('pm_observed_ns')))
    out.sort(key=lambda p: p[0])
    return out


def member_delta_slow(bundle, phase_fields, override):
    """delta_slow_c the member armed: its own config policy, then r1_result. The override is display only."""
    config = bundle / 'config.json'
    if config.is_file():
        try:
            spec = json.loads(json.loads(config.read_text())['workload_profile']['prompt_text'])
            value = (spec.get('thermal') or {}).get('delta_slow_c')
            if finite(value):
                return float(value), 'member config.json thermal.delta_slow_c'
        except (KeyError, TypeError, ValueError):
            pass
    for value in ((phase_fields.get('bands_c') or {}).get('delta_slow_c'), phase_fields.get('delta_slow_c')):
        if finite(value):
            return float(value), 'r1_result.json phase result'
    if override is not None:
        return float(override), OVERRIDE_SOURCE
    return None, None


def precool_record(fields, base):
    """The preceding idle-until-soak result: released flag and last recovery-curve value, or Nones."""
    if fields is None:
        return {'phase': precool_phase(base), 'released': None, 'last_curve_c': None}
    result = fields.get(precool_phase(base))
    if result is None:
        return {'phase': precool_phase(base), 'released': None, 'last_curve_c': None}
    curve = result.get('recovery_curve') or []
    last = curve[-1][1] if curve and isinstance(curve[-1], (list, tuple)) and len(curve[-1]) == 2 else None
    released = result.get('released')
    return {'phase': precool_phase(base), 'released': released if type(released) is bool else None,
            'last_curve_c': r6(last) if finite(last) else None}


def analyse_gate(phase, gate, start, readings, delta_slow, delta_source, precool=None):
    label, planning, superseded, base = turn_info(phase)
    heater = start.get('s_slow')
    s_ns, e_ns = gate.get('start_ns'), gate.get('end_ns')
    reference = gate.get('reference') or {}
    target = reference.get('slow_c')
    duration = gate.get('duration_s')
    row = {'phase': phase, 'turn': gate.get('turn'), 'turn_label': label, 'planning_turn': planning,
           'superseded': superseded, 'outcome': gate.get('outcome'), 'duration_s': r6(duration),
           'heater_key': heater, 'target_c': r6(target), 'delta_slow_c': delta_slow,
           'delta_slow_source': delta_source}
    edge = target + delta_slow if finite(target) and delta_slow is not None else None
    row['band_edge_c'] = r6(edge)
    row['threshold_c'] = r6(edge - EDGE_C) if edge is not None else None
    points = [p for p in sample_points(readings, heater)
              if finite(s_ns) and finite(e_ns) and s_ns <= p[0] <= e_ns]
    values = [(t, v) for t, v, *_ in points if v is not None]
    last = [v for t, v in values if t >= e_ns - WINDOW_S * NS] if finite(e_ns) else []
    row['samples'] = len(points)
    row['samples_last_300s'] = len(last)
    row['short_interval'] = bool(finite(duration) and duration < WINDOW_S)
    peak = max(last) if last else None
    row[PEAK_FIELD] = r6(peak)
    row['margin_to_threshold_c'] = (r6(round(peak - edge + EDGE_C, 9))
                                    if peak is not None and edge is not None else None)
    row['whole_g0_max_c'] = r6(max((v for _, v in values), default=None))
    # Disclosure only (RL-124 item 1, review F7): no effect on the class.
    row['last_300s_median_c'] = r6(median(last))
    row['last_300s_count_ge_threshold'] = (sum(1 for v in last if round(v - edge + EDGE_C, 9) >= 0)
                                           if edge is not None else None)
    row['exit_slope_c_per_min'] = r6(gate.get('slope_c_per_min')) if finite(gate.get('slope_c_per_min')) else None
    row['stale_power_state_samples'] = sum(1 for t, _, _, _, pm in points
                                           if type(pm) is not int or t - pm > FRESH_NS)
    levels = sorted({p[2] for p in points if p[2] is not None})
    states = sorted({p[3] for p in points if isinstance(p[3], str)})
    row['os_level_max'] = max(levels) if levels else None
    row['os_levels'] = levels
    row['pm_states'] = states
    row['status_unobserved_samples'] = sum(1 for p in points if p[2] is None or p[3] is None)
    row['nominal_throughout'] = bool(points) and states == ['Nominal'] and row['status_unobserved_samples'] == 0
    if planning:
        row['precool'] = precool or precool_record(None, base)
    row['classification'], row['reasons'] = classify(row)
    return row


def classify(row):
    if row['outcome'] == 'released':
        return CLASS_RELEASED, []
    reasons = []
    if row['outcome'] != 'timeout':
        reasons.append(f"G0 outcome {row['outcome']!r} is not a timeout")
    if not row['planning_turn']:
        reasons.append('G0 timeout outside the planning turns (R+0, R+2, R+4)')
    if row['os_level_max'] is None:
        reasons.append('OS level unobserved in the interval')
    elif row['os_level_max'] > 0:
        reasons.append(f"OS level above 0 (max {row['os_level_max']})")
    if not row['nominal_throughout']:
        reasons.append('not Nominal throughout (states %s; %d sample(s) without status)'
                       % (row['pm_states'], row['status_unobserved_samples']))
    if row['band_edge_c'] is None:
        reasons.append('target or delta_slow_c unavailable: band edge undefined')
    elif row['delta_slow_source'] == OVERRIDE_SOURCE:
        reasons.append('band from --delta-slow-c override, not from the member\'s armed policy (display only)')
    if row['short_interval']:
        reasons.append('interval shorter than 300 s: the last-300-s measure is not defined')
    elif row['samples_last_300s'] < MIN_LAST_SAMPLES:
        reasons.append('only %d valid heater-key sample(s) in the last 300 s (< %d)'
                       % (row['samples_last_300s'], MIN_LAST_SAMPLES))
    elif row['margin_to_threshold_c'] is not None and row['margin_to_threshold_c'] < 0:
        reasons.append('heater key not at the band edge: last-300-s peak %.3f C is %.3f C below band edge - 0.3'
                       % (row[PEAK_FIELD], -row['margin_to_threshold_c']))
    if row['planning_turn']:
        released = (row.get('precool') or {}).get('released')
        if released is not True:
            reasons.append('precool %s did not report released: true (%s); RL-124 5(a)'
                           % ((row.get('precool') or {}).get('phase'),
                              'not available' if released is None else 'released false'))
    return (CLASS_LEAD, reasons) if reasons else (CLASS_3A, [])


def discover(root):
    found = []
    for journal in sorted(root.glob(f'*/runs/*/outputs/{JOURNAL}')):
        found.append((journal.relative_to(root).parts[0], journal))
    if not found:
        raise DeskError(f'{root}: no <phase>/runs/<run>/outputs/{JOURNAL} found')
    return found


def reconcile(phases, rows):
    """Every r1_result phase carrying g0_outcome has exactly one desk row with that outcome, and back."""
    if phases is None:
        return {'status': 'not reconciled (no r1_result.json)', 'mismatches': []}
    expected = {name: res['g0_outcome'] for name, res in phases.items() if 'g0_outcome' in res}
    by_phase = {}
    for r in rows:
        if not r['superseded']:
            by_phase.setdefault(r['phase'], []).append(r)
    mismatches = []
    for name, outcome in sorted(expected.items()):
        got = by_phase.get(name, [])
        if len(got) != 1:
            mismatches.append(f'{name}: r1_result has a G0 ({outcome!r}); desk found {len(got)} row(s)')
        elif got[0]['outcome'] != outcome:
            mismatches.append(f"{name}: r1_result g0_outcome {outcome!r} != journal {got[0]['outcome']!r}")
    for name in sorted(set(by_phase) - set(expected)):
        mismatches.append(f'{name}: desk row has no r1_result phase carrying g0_outcome')
    rows_n = sum(len(v) for v in by_phase.values())
    return {'status': ('reconciled: %d r1_result phase(s) with g0_outcome, %d desk row(s)' % (len(expected), rows_n)
                       if not mismatches else 'MISMATCH'),
            'phases_with_g0_outcome': len(expected), 'desk_rows': rows_n, 'mismatches': mismatches}


def desk(night_dir, delta_slow_override=None):
    root = Path(night_dir)
    phases = None
    if (root / 'r1_result.json').is_file():
        result = json.loads((root / 'r1_result.json').read_text())
        phases = {p.get('name'): p.get('result') or {} for p in result.get('phases', []) if isinstance(p, dict)}
    rows = []
    for phase, journal in discover(root):
        start, gates, readings = read_journal(journal)
        delta, source = member_delta_slow(journal.parent.parent, (phases or {}).get(turn_info(phase)[3], {}),
                                          delta_slow_override)
        digest = sha256_file(journal)
        for gate in gates:
            base = turn_info(phase)[3]
            row = analyse_gate(phase, gate, start, readings, delta, source,
                               precool_record(phases, base) if turn_info(phase)[1] else None)
            row['journal'] = str(journal.relative_to(root))
            row['journal_sha256'] = digest
            rows.append(row)
    rows.sort(key=lambda r: (r['phase'], r['turn'] if finite(r['turn']) else -1))
    # More than one G0 row under one kit segment name: none is released (RL-124 item 5(c)).
    for name in KIT_SEGMENTS:
        dup = [r for r in rows if r['phase'] == name]
        if len(dup) > 1:
            for r in dup:
                r['classification'] = CLASS_LEAD
                r['reasons'].append(f'{len(dup)} G0 rows under one segment name; none is released')
    segments = {r['phase']: {'band_edge_c': r['band_edge_c'], 'heater_key': r['heater_key'],
                             PEAK_FIELD: r[PEAK_FIELD], 'os_levels': r['os_levels'], 'pm_states': r['pm_states']}
                for r in rows if r['classification'] == CLASS_3A and not r['superseded']
                and r['phase'] in KIT_SEGMENTS}
    counts = {}
    for r in rows:
        counts[r['classification']] = counts.get(r['classification'], 0) + 1
    return {'schema': SCHEMA, 'night': root.name, 'rule': {
                'authority': 'RL-122 item 3(a), RL-122 amendment 2026-11-13, RL-124',
                'measure': f'heater key peak over the last {WINDOW_S} s of the G0 interval >= band edge - {EDGE_C} C',
                'band_edge': 'reference.slow_c (target) + delta_slow_c', 'heater_key': 'session s_slow',
                'precool': 'preceding idle-until-soak phase must report released: true (RL-124 5(a))'},
            'reconciliation': reconcile(phases, rows),
            'g0_intervals': rows, 'counts': dict(sorted(counts.items())),
            'kit_record_segments': dict(sorted(segments.items()))}


def _f(value, fmt='{:.3f}'):
    return '-' if value is None else fmt.format(value)


def render(report):
    head = ('turn', 'outcome', 'dur_s', 'key', 'target', 'edge', 'last300', 'margin', 'whole', 'os', 'nom',
            'median300', 'n>=thr', 'slope', 'stale_pm', 'precool', 'class')
    lines = [f"RL-122 3(a) desk: night {report['night']}", '  '.join(head)]
    for r in report['g0_intervals']:
        pre = r.get('precool')
        pre_text = '-' if pre is None else ('released' if pre['released'] is True else
                                            'NOT-released' if pre['released'] is False else 'n/a')
        label = r['turn_label'] + (f" [{r['phase']}]" if r['planning_turn'] else '')
        label += ' (superseded)' if r['superseded'] else ''
        lines.append('  '.join((
            label, r['outcome'], _f(r['duration_s'], '{:.1f}'), str(r['heater_key']),
            _f(r['target_c']), _f(r['band_edge_c']), _f(r[PEAK_FIELD]),
            _f(r['margin_to_threshold_c'], '{:+.3f}'), _f(r['whole_g0_max_c']) + '*',
            '-' if r['os_level_max'] is None else str(r['os_level_max']),
            'yes' if r['nominal_throughout'] else 'NO',
            _f(r['last_300s_median_c']) + '+', _f(r['last_300s_count_ge_threshold'], '{}') + '+',
            _f(r['exit_slope_c_per_min'], '{:+.3f}') + '+', str(r['stale_power_state_samples']) + '+',
            pre_text, r['classification'])))
        if pre is not None:
            lines.append(f"    precool {pre['phase']}: released {pre['released']}, last curve value "
                         f"{_f(pre['last_curve_c'])}")
        for reason in r['reasons']:
            lines.append(f'    -> {reason}')
    rec = report['reconciliation']
    lines.append(f"reconciliation: {rec['status']}")
    lines.extend(f'    !! {m}' for m in rec['mismatches'])
    lines.append('margin = last-300-s peak - (band edge - 0.3); >= 0 meets the pattern. '
                 '* whole-G0 peak and + columns: disclosure only.')
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('night_dir', type=Path)
    parser.add_argument('--delta-slow-c', type=float, default=None,
                        help='DISPLAY ONLY: a row whose band comes from this value is never planning-release-3a')
    parser.add_argument('--format', choices=('text', 'json', 'both'), default='both')
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        report = desk(args.night_dir, args.delta_slow_c)
    except (DeskError, OSError, ValueError) as error:
        print(f'3a desk: {error}', file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.json_out:
        args.json_out.write_text(text)
    if args.format in ('text', 'both'):
        print(render(report))
    if args.format in ('json', 'both'):
        print(text, end='')
    return 2 if report['reconciliation']['mismatches'] else 0


if __name__ == '__main__':
    sys.exit(main())
