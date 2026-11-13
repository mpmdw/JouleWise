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
* ``to-research-lead``: anything else, with the reasons.

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
# The night's planning members, plus the scratch-copy suffixes custody adds.
PLANNING = re.compile(r'^planning_turn_R_plus_(\d+)C(?:\.g0_(?:timeout|release)\d+)?$')
PLANNING_OFFSETS = (0, 2, 4)
TEMP_KEY = re.compile(r'^T[0-9A-Za-z]{3}$')
CLASS_RELEASED, CLASS_3A, CLASS_LEAD = 'released', 'planning-release-3a', 'to-research-lead'


class DeskError(RuntimeError):
    pass


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def valid_temp(value):
    return finite(value) and -40 <= value <= 150


def r6(value):
    return None if value is None else round(float(value), 6)


def turn_label(phase):
    match = PLANNING.match(phase)
    if match and int(match.group(1)) in PLANNING_OFFSETS:
        return f'planning R+{int(match.group(1))}', True
    return phase, False


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
    """(monotonic_ns, value or None, os_level, pm_state) per reading; time is the read start."""
    out = []
    for row in readings:
        values = row.get('values') or {}
        value = (values.get('sensors') or {}).get(key)
        if key in (values.get('errors') or {}) or not valid_temp(value):
            value = None
        status = values.get('status') if isinstance(values.get('status'), dict) else {}
        out.append((row['started']['monotonic_ns'], value, status.get('os_level'), status.get('pm_state')))
    out.sort(key=lambda p: p[0])
    return out


def member_delta_slow(bundle, phase_fields, override):
    """delta_slow_c the member armed: its own config policy, then r1_result, then the override."""
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
        return float(override), '--delta-slow-c'
    return None, None


def analyse_gate(phase, gate, start, readings, delta_slow, delta_source):
    label, planning = turn_label(phase)
    heater = start.get('s_slow')
    s_ns, e_ns = gate.get('start_ns'), gate.get('end_ns')
    reference = gate.get('reference') or {}
    target = reference.get('slow_c')
    duration = gate.get('duration_s')
    row = {'phase': phase, 'turn': gate.get('turn'), 'turn_label': label, 'planning_turn': planning,
           'outcome': gate.get('outcome'), 'duration_s': r6(duration), 'heater_key': heater,
           'target_c': r6(target), 'delta_slow_c': delta_slow, 'delta_slow_source': delta_source}
    edge = target + delta_slow if finite(target) and delta_slow is not None else None
    row['band_edge_c'] = r6(edge)
    row['threshold_c'] = r6(edge - EDGE_C) if edge is not None else None
    points = [p for p in sample_points(readings, heater)
              if finite(s_ns) and finite(e_ns) and s_ns <= p[0] <= e_ns]
    values = [(t, v) for t, v, _, _ in points if v is not None]
    last = [v for t, v in values if t >= e_ns - WINDOW_S * NS] if finite(e_ns) else []
    row['samples'] = len(points)
    row['samples_last_300s'] = len(last)
    row['short_interval'] = bool(finite(duration) and duration < WINDOW_S)
    peak = max(last) if last else None
    row[PEAK_FIELD] = r6(peak)
    row['margin_to_threshold_c'] = (r6(round(peak - edge + EDGE_C, 9))
                                    if peak is not None and edge is not None else None)
    row['whole_g0_max_c'] = r6(max((v for _, v in values), default=None))
    levels = sorted({p[2] for p in points if p[2] is not None})
    states = sorted({p[3] for p in points if isinstance(p[3], str)})
    row['os_level_max'] = max(levels) if levels else None
    row['os_levels'] = levels
    row['pm_states'] = states
    row['status_unobserved_samples'] = sum(1 for p in points if p[2] is None or p[3] is None)
    row['nominal_throughout'] = bool(points) and states == ['Nominal'] and row['status_unobserved_samples'] == 0
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
    if row['short_interval']:
        reasons.append('interval shorter than 300 s: the last-300-s measure is not defined')
    elif row[PEAK_FIELD] is None:
        reasons.append('no valid heater-key sample in the last 300 s')
    elif row['margin_to_threshold_c'] is not None and row['margin_to_threshold_c'] < 0:
        reasons.append('heater key not at the band edge: last-300-s peak %.3f C is %.3f C below band edge - 0.3'
                       % (row[PEAK_FIELD], -row['margin_to_threshold_c']))
    return (CLASS_LEAD, reasons) if reasons else (CLASS_3A, [])


def discover(root):
    found = []
    for journal in sorted(root.glob(f'*/runs/*/outputs/{JOURNAL}')):
        found.append((journal.relative_to(root).parts[0], journal))
    if not found:
        raise DeskError(f'{root}: no <phase>/runs/<run>/outputs/{JOURNAL} found')
    return found


def desk(night_dir, delta_slow_override=None):
    root = Path(night_dir)
    result = {}
    if (root / 'r1_result.json').is_file():
        result = json.loads((root / 'r1_result.json').read_text())
    fields = {p.get('name'): p.get('result') or {} for p in result.get('phases', []) if isinstance(p, dict)}
    rows = []
    for phase, journal in discover(root):
        start, gates, readings = read_journal(journal)
        delta, source = member_delta_slow(journal.parent.parent, fields.get(phase, {}), delta_slow_override)
        for gate in gates:
            row = analyse_gate(phase, gate, start, readings, delta, source)
            row['journal'] = str(journal.relative_to(root))
            rows.append(row)
    rows.sort(key=lambda r: (r['phase'], r['turn'] if finite(r['turn']) else -1))
    segments = {r['phase']: {'band_edge_c': r['band_edge_c'], 'heater_key': r['heater_key'],
                             PEAK_FIELD: r[PEAK_FIELD], 'os_levels': r['os_levels'], 'pm_states': r['pm_states']}
                for r in rows if r['classification'] == CLASS_3A
                and r['phase'] in {f'planning_turn_R_plus_{n}C' for n in PLANNING_OFFSETS}}
    counts = {}
    for r in rows:
        counts[r['classification']] = counts.get(r['classification'], 0) + 1
    return {'schema': SCHEMA, 'night': root.name, 'rule': {
                'authority': 'RL-122 item 3(a), RL-122 amendment 2026-11-13',
                'measure': f'heater key peak over the last {WINDOW_S} s of the G0 interval >= band edge - {EDGE_C} C',
                'band_edge': 'reference.slow_c (target) + delta_slow_c', 'heater_key': 'session s_slow'},
            'g0_intervals': rows, 'counts': dict(sorted(counts.items())),
            'kit_record_segments': dict(sorted(segments.items()))}


def _f(value, fmt='{:.3f}'):
    return '-' if value is None else fmt.format(value)


def render(report):
    head = ('turn', 'outcome', 'dur_s', 'key', 'target', 'edge', 'last300', 'margin', 'whole', 'os', 'nom', 'class')
    lines = [f"RL-122 3(a) desk: night {report['night']}", '  '.join(head)]
    for r in report['g0_intervals']:
        lines.append('  '.join((
            r['turn_label'] + (f" [{r['phase']}]" if r['planning_turn'] else ''), r['outcome'], _f(r['duration_s'], '{:.1f}'), str(r['heater_key']),
            _f(r['target_c']), _f(r['band_edge_c']), _f(r[PEAK_FIELD]),
            _f(r['margin_to_threshold_c'], '{:+.3f}'), _f(r['whole_g0_max_c']) + '*',
            '-' if r['os_level_max'] is None else str(r['os_level_max']),
            'yes' if r['nominal_throughout'] else 'NO', r['classification'])))
        for reason in r['reasons']:
            lines.append(f'    -> {reason}')
    lines.append('margin = last-300-s peak - (band edge - 0.3); >= 0 meets the pattern. '
                 '* whole-G0 peak: disclosure only.')
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('night_dir', type=Path)
    parser.add_argument('--delta-slow-c', type=float, default=None,
                        help='used only when neither the member config nor r1_result carries delta_slow_c')
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
    return 0


if __name__ == '__main__':
    sys.exit(main())
