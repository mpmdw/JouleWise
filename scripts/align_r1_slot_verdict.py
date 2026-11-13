#!/usr/bin/env python3
"""B4: section 3's decision table as code (spec /Volumes/JW-EXT/scratch/fable-r1-slot-desk-spec.md 2.4, 3; RL-135).

Usage:
  python3.13 -B -s -E scripts/align_r1_slot_verdict.py --record out/record.json --gate-desk out/gate_desk.json \
      --3a out/3a.json --kit-desk out/kit_desk.json --kit-desk-rc out/kit_desk.rc \
      --kit-desk-stderr out/kit_desk.stderr.txt --idle-parse-gap out/idle_parse_gap.txt \
      [--decide out/decide.json --decide-rc out/decide.rc] [--proofs out/proofs.json] \
      --json-out out/verdict.json > out/verdict.txt

Blind-safe: reads only the desk outputs. Every row of section 3 is printed with
``fired`` (true / false / null = not evaluated), its evidence and its route.
No judgment and no threshold lives here that section 3 does not state; the
one comparison that is not a row (C1's 30 s) is section 3's. A missing or
unparseable input is X2 (TO-LEAD-TOOL-DEFECT), never a pass. It also fills
RL-106's ``n_gate`` and applies T2's planning exclusion (RL-135 items 1, 4).

Overall route, in precedence: TO-RESEARCH-LEAD if any such row fired; else
TO-LEAD-TOOL-DEFECT; else SLOTS-PR-HOLD-SIGNING (S6c, S1); else
SLOTS-AND-SIGNING. Exit 0 whenever the verdict was written.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = 'joulewise.align_r1_slot_verdict.v1'
TRL, TOOL, HOLD, GO = 'TO-RESEARCH-LEAD', 'TO-LEAD-TOOL-DEFECT', 'SLOTS-PR-HOLD-SIGNING', 'SLOTS-AND-SIGNING'
PLANNING_SEGMENTS = tuple(f'planning_turn_R_plus_{n}C' for n in (0, 2, 4))
RL106_MEMBERS = frozenset(('step_30b', 'high_power_A1', 'high_power_B', 'high_power_A2',
                           'step_D_prefill_10k_decode_4096') + PLANNING_SEGMENTS)
G0_TIMEOUT_FLAG = 'r1.g0_timeout_run'
U5_INCONCLUSIVE = 'r1.u5_inconclusive'
CLASS_3A, CLASS_LEAD = 'planning-release-3a', 'to-research-lead'
S6_BAR_S = 90.0
CAPTURE_SPAN_BAR_S = 30.0
DECIDE_STEPS = ('CURRENT-RULE', 'R10-2(a)')
IDLE_GAP_COLUMN = 'plist_mtime->warmup_start s'
SUFFIX = re.compile(r'(\.(?:g0_timeout|g0_release|rejected)\d*)+$')
NOT_EVALUATED = 'not evaluated: input missing or unreadable (X2)'
S6B_TEXT = ('median G1 wait {n} s; not reachable by δ_slow (replay at 1.5 and 2.0 °C attached); δ_slow stays '
            '1.0 °C; implied energy band disclosed')
S6A_TEXT = 'median G1 wait {n} s; S6 rule not engaged; δ_slow 1.0 °C'


def base_name(segment):
    return SUFFIX.sub('', segment or '')


def is_planning(segment):
    return base_name(segment) in PLANNING_SEGMENTS


# ---------------------------------------------------------------- inputs
class Inputs:
    def __init__(self):
        self.problems = []      # X2 evidence: missing or unreadable inputs

    def json(self, label, path, required=True):
        if path is None:
            if required:
                self.problems.append(f'{label}: not given')
            return None
        try:
            return json.loads(Path(path).read_text())
        except (OSError, ValueError) as error:
            self.problems.append(f'{label}: {path}: {type(error).__name__}: {error}')
            return None

    def text(self, label, path, required=True):
        if path is None:
            if required:
                self.problems.append(f'{label}: not given')
            return None
        try:
            return Path(path).read_text()
        except OSError as error:
            self.problems.append(f'{label}: {path}: {error}')
            return None


def parse_rc(text):
    if text is None:
        return None
    match = re.search(r'-?\d+', text)
    return int(match.group()) if match else None


def parse_idle_gap(text):
    """E4's table: header line then `member | MB | plist_mtime->warmup s | ...` rows."""
    lines = [line for line in (text or '').splitlines() if line.strip()]
    if not lines:
        raise ValueError('empty')
    header = [h.strip() for h in lines[0].split('|')]
    if IDLE_GAP_COLUMN not in header:
        raise ValueError(f'no column {IDLE_GAP_COLUMN!r}')
    col = header.index(IDLE_GAP_COLUMN)
    rows = []
    for line in lines[1:]:
        cells = [c.strip() for c in line.split('|')]
        if len(cells) != len(header):
            raise ValueError(f'malformed row: {line!r}')
        rows.append({'member': cells[0], 'span_s': float(cells[col])})
    if not rows:
        raise ValueError('no member rows')
    return rows


# ---------------------------------------------------------------- the table
def row(rid, fired, route, packet, evidence=None, status=None):
    return {'row': rid, 'fired': fired, 'route': route if fired else None, 'route_if_fired': route,
            'packet': packet, 'evidence': evidence if evidence is not None else {},
            'status': status or ('fired' if fired else 'not fired' if fired is False else NOT_EVALUATED)}


def gate_rows(gate):
    return [g for g in (gate or {}).get('gates') or [] if isinstance(g, dict)]


def p3_set(three_a):
    """Planning segments whose every timed-out G0 row (final) is planning-release-3a (P3)."""
    rows = (three_a or {}).get('g0_intervals') or []
    timed = [r for r in rows if r.get('planning_turn') and r.get('outcome') != 'released' and not r.get('superseded')]
    return sorted({r['phase'] for r in timed if r.get('classification') == CLASS_3A}), timed


def evaluate(record, gate, three_a, kit, kit_rc, kit_stderr, idle_text, decide, decide_rc, proofs, problems,
             decide_given, proofs_given):
    rows = []
    rec_ok, gate_ok, three_ok = record is not None, gate is not None, three_a is not None
    x2 = list(problems)

    # ---- derived quantities
    gates = gate_rows(gate)
    n_gate = (sum(1 for g in gates if g.get('kind') == 'G0' and g.get('outcome') == 'timeout'
                  and g.get('attempt') in ('final', 'superseded') and g.get('member_base') in RL106_MEMBERS)
              if gate_ok else None)
    rl106 = dict((record or {}).get('rl106_n') or {})
    rl106['n_gate'] = n_gate
    released_3a, planning_timed = p3_set(three_a) if three_ok else ([], [])
    class_3a = {(r.get('phase')) for r in ((three_a or {}).get('g0_intervals') or [])
                if r.get('classification') == CLASS_3A}

    # ---- X1
    if rec_ok:
        ident = record.get('identity') or {}
        fired = ident.get('ok') is not True
        hard = ident.get('status') in ('refused', 'aborted') or ident.get('chain_exit_code') != 0
        route = TRL if hard else TOOL
        rows.append(row('X1', fired, route, ['record.json', "the magistrate's report"],
                        {'identity': ident, 'note': None if hard or not fired else
                         'hash or commit mismatch: TO-LEAD-TOOL-DEFECT only if the lead traces it to a copy error; '
                         'otherwise TO-RESEARCH-LEAD'}))
    else:
        rows.append(row('X1', None, TRL, ['record.json']))

    # ---- X2 (tool integrity)
    if gate_ok:
        if (gate.get('validation') or {}).get('all_agree') is not True:
            x2.append('B1 validation not all-agree')
        checks = gate.get('tool_checks') or {}
        if checks.get('slope_recompute_mismatch'):
            x2.append(f"slope_recompute_mismatch: {checks['slope_recompute_mismatch']}")
        if checks.get('s6_median_agrees') is not True:
            x2.append(f"s6_median_agrees is {checks.get('s6_median_agrees')!r}")
        kit_ran = kit_rc == 0
        if checks.get('tf08_excess_agrees') is False or (kit_ran and checks.get('tf08_excess_agrees') is not True):
            x2.append(f"tf08_excess_agrees is {checks.get('tf08_excess_agrees')!r} with the kit desk rc {kit_rc}")
        trig = gate.get('triggers') or {}
        for t in ('T1', 'T3'):
            if (trig.get(t) or {}).get('fired') is None:
                x2.append(f'gate_desk triggers.{t}.fired is None (not computable: tool or layout defect)')
    if three_ok:
        if (three_a.get('reconciliation') or {}).get('mismatches'):
            x2.append(f"3(a) rc 2: {three_a['reconciliation']['mismatches']}")
        if (three_a.get('rule') or {}).get('precool_fast') is None or \
                'rl131' not in json.dumps((three_a.get('rule') or {}).get('precool_fast')):
            x2.append('3(a) desk not run with --precool-fast-rule rl131')
    if rec_ok:
        tc = record.get('tool_checks') or {}
        if tc.get('duty_recompute_mismatch'):
            x2.append(f"record duty recompute disagrees with the driver: {tc['duty_recompute_mismatch']}")
        if tc.get('capture_reaps_unreadable'):
            x2.append(f"capture_reaps unreadable in: {tc['capture_reaps_unreadable']}")
        if gate_ok and rl106.get('n_flag') != n_gate:
            x2.append(f"RL-106 n_flag {rl106.get('n_flag')} != n_gate {n_gate}")
    kit_refused_rl78 = kit_rc not in (None, 0) and 'RL-78' in (kit_stderr or '')
    if kit_rc is None:
        x2.append('kit desk rc unavailable')
    elif kit_rc != 0 and not kit_refused_rl78:
        x2.append(f'kit desk rc {kit_rc} without an RL-78 refusal')
    elif kit_rc == 0 and kit is None:
        x2.append('kit desk rc 0 but out/kit_desk.json unreadable')
    idle_rows = None
    if idle_text is not None:
        try:
            idle_rows = parse_idle_gap(idle_text)
        except ValueError as error:
            x2.append(f'idle_parse_gap.txt unparseable: {error}')
    rows.append(row('X2', bool(x2), TOOL, ['the failing rows'], {'reasons': x2},
                    status=None))
    rows[-1]['note'] = 'TO-LEAD-TOOL-DEFECT; if it survives one fix: TO-RESEARCH-LEAD ("the desk cannot reproduce the session")'

    # ---- D1
    if rec_ok and kit_rc is not None:
        t4 = (record.get('thermometry') or {}).get('t4_fired') is True
        rows.append(row('D1', t4 or kit_refused_rl78, TRL,
                        ['record.thermometry', "the night's classification row for TV0h and TVh0", 'floor census'],
                        {'t4_fired': t4, 't4_reasons': (record.get('thermometry') or {}).get('t4_reasons'),
                         'kit_desk_rc': kit_rc, 'kit_desk_refused_rl78': kit_refused_rl78}))
    else:
        rows.append(row('D1', None, TRL, ['record.thermometry']))

    # ---- D2 / D2i / G1H / XG
    d2_packet = ["RL-122 item 6's table from gate_desk.gates (per judged run each G0, G1, H duration, clause_last, "
                 "d_tv0h_minus_tvh0_at_exit_c, Tf08 at entry and exit)",
                 'S6 replays at 1.5 and 2.0 °C (run B1 with --force-s6-replay if the median is <= 90 s)']
    duty = (record or {}).get('duty') or {}
    rows.append(row('D2', duty.get('verdict') == 'fail' if rec_ok else None, TRL, d2_packet,
                    {'verdict': duty.get('verdict')}))
    rows.append(row('D2i', duty.get('verdict') == 'inconclusive' if rec_ok else None, TRL, d2_packet,
                    {'verdict': duty.get('verdict')}))
    if gate_ok:
        bad = [g for g in gates if g.get('kind') in ('G1', 'H') and g.get('attempt') == 'final'
               and (g.get('gated_d') or g.get('x_g')) and g.get('outcome') != 'released']
        rows.append(row('G1H', bool(bad), TRL, d2_packet + ['the rows'], {'rows': bad}))
    else:
        rows.append(row('G1H', None, TRL, d2_packet))
    if rec_ok:
        xg = record.get('x_g') or {}
        rows.append(row('XG', xg.get('status') != 'measured' or xg.get('x7') is True, TRL,
                        ['record.x_g', "X_G's gate rows"], {'x_g': xg}))
    else:
        rows.append(row('XG', None, TRL, ['record.x_g']))

    # ---- P1 / P2 / P3
    if three_ok and rec_ok:
        timed_any = [r for r in (three_a.get('g0_intervals') or [])
                     if r.get('planning_turn') and r.get('outcome') != 'released']
        rows.append(row('P1', False, None, [], {'planning_g0_timeouts': len(timed_any)},
                        status='applies: no planning G0 timed out; no planning-release record' if not timed_any
                        else 'does not apply'))
        lead_rows = [{'phase': r.get('phase'), 'superseded': r.get('superseded'), 'reasons': r.get('reasons')}
                     for r in (three_a.get('g0_intervals') or []) if r.get('classification') == CLASS_LEAD]
        inc = (record.get('flags') or {}).get('inconclusive_segments') or {}
        other = {k: v for k, v in inc.items() if is_planning(k) and v != G0_TIMEOUT_FLAG}
        rows.append(row('P2', bool(lead_rows or other), TRL, ['3a.txt', 'the planning rows of gate_desk.gates'],
                        {'3a_rows_to_research_lead': lead_rows, 'planning_inconclusive_other_reason': other}))
        p3 = bool(planning_timed) and all(r.get('classification') == CLASS_3A for r in planning_timed) \
            and not lead_rows
        rows.append(row('P3', False, None, [], {'segments': released_3a},
                        status=('applies: step 7 writes the planning-release record; U5 and the planning '
                                'temperature print inconclusive') if p3 else 'does not apply'))
    else:
        p3 = False
        for rid in ('P1', 'P2', 'P3'):
            rows.append(row(rid, None, TRL if rid == 'P2' else None, []))
    released_p3 = set(released_3a) if p3 else set()

    # ---- G0x
    if rec_ok and gate_ok:
        npg = record.get('non_planning_g0_not_released') or []
        aux = [g for g in gates if g.get('attempt') == 'auxiliary' and g.get('kind') == 'G0'
               and g.get('outcome') != 'released']
        rows.append(row('G0x', bool(npg or aux), TRL, ['the rows, with clause_last'],
                        {'non_planning_g0_not_released': npg,
                         'auxiliary_g0_not_released': [{k: g.get(k) for k in ('member', 'outcome', 'clause_last',
                                                                               'duration_s')} for g in aux]}))
    else:
        rows.append(row('G0x', None, TRL, ['the rows']))

    # ---- A1
    rows.append(row('A1', (record.get('aba') or {}).get('ok') is not True if rec_ok else None, TRL,
                    ['record.aba', '11-12 values 98.665 / 98.845 / 98.856 s beside it'],
                    {'aba': (record or {}).get('aba')}))

    # ---- T1 / T2 / T3
    trig = (gate or {}).get('triggers') or {}
    t1 = (trig.get('T1') or {}).get('fired')
    rows.append(row('T1', t1 if gate_ok and t1 is not None else None, TRL,
                    ['floor census', 'the offending rows with their neighbours'],
                    {'T1': trig.get('T1')}))
    if gate_ok and three_ok:
        cands = (trig.get('T2') or {}).get('gates') or []
        kept = [c for c in cands if not (c.get('kind') == 'G0' and c.get('planning_turn')
                                         and c.get('member') in class_3a)]
        excluded = [c for c in cands if c not in kept]
        rows.append(row('T2', bool(kept), TRL, ['the gate rows', 't2_samples', "the member's duty block"],
                        {'candidates': len(cands), 'after_planning_exclusion': kept, 'excluded_3a': excluded}))
    else:
        rows.append(row('T2', None, TRL, ['the gate rows']))
    t3 = (trig.get('T3') or {}).get('fired')
    rows.append(row('T3', t3 if gate_ok and t3 is not None else None, TRL, ['u2 block'], {'T3': trig.get('T3')}))

    # ---- F1
    if rec_ok and three_ok:
        flags = record.get('flags') or {}
        inc = flags.get('inconclusive_segments') or {}
        other_keys = sorted(k for k, v in inc.items() if not (k in released_p3 and v == G0_TIMEOUT_FLAG))
        allowed = {'planning_temperature': {G0_TIMEOUT_FLAG}, 'U5': {G0_TIMEOUT_FLAG, U5_INCONCLUSIVE}}
        bad_slots = {k: v for k, v in (flags.get('inadmissible_slots') or {}).items()
                     if v and not (p3 and k in allowed and set(v) <= allowed[k])}
        rows.append(row('F1', bool(other_keys or bad_slots), TRL, ['record.flags'],
                        {'inconclusive_segments_other': {k: inc[k] for k in other_keys},
                         'inadmissible_slots_other': bad_slots}))
    else:
        rows.append(row('F1', None, TRL, ['record.flags']))

    # ---- C1
    if idle_rows is not None:
        over = [r for r in idle_rows if r['span_s'] >= CAPTURE_SPAN_BAR_S]
        rows.append(row('C1', bool(over), TRL, ['idle_parse_gap.txt'],
                        {'members_ge_30s': over, 'max_span_s': max(r['span_s'] for r in idle_rows)}))
        rows[-1]['note'] = 'TO-RESEARCH-LEAD before signing; the slots PR may be opened'
    else:
        rows.append(row('C1', None, TRL, ['idle_parse_gap.txt']))

    # ---- R1
    rows.append(row('R1', (record.get('rl91') or {}).get('ok') is not True if rec_ok else None, TRL,
                    ['record.rl91'], {'rl91_ok': (record or {}).get('rl91', {}).get('ok')}))

    # ---- S6a / S6b / S6c
    s6 = (gate or {}).get('s6') or {}
    med, reach = s6.get('g1_median_s'), s6.get('s6_reachable_step_c')
    if gate_ok and isinstance(med, (int, float)):
        band = (record or {}).get('implied_energy_band')
        if med <= S6_BAR_S:
            text = S6A_TEXT.format(n=med)
        elif reach is None:
            text = S6B_TEXT.format(n=med)
        else:
            text = None
        rows.append(row('S6a', False, None, [], {'g1_median_s': med},
                        status=f'applies: record "{text}"' if med <= S6_BAR_S else 'does not apply'))
        rows.append(row('S6b', False, None, [], {'g1_median_s': med, 'implied_energy_band': band},
                        status=(f'applies: record in the slots PR verbatim "{text}", followed by '
                                'record.implied_energy_band') if med > S6_BAR_S and reach is None else 'does not apply'))
        rows.append(row('S6c', med > S6_BAR_S and reach in (1.5, 2.0), HOLD, ['gate_desk.s6'],
                        {'g1_median_s': med, 's6_reachable_step_c': reach}))
    else:
        if gate_ok:
            x2_row = next(r for r in rows if r['row'] == 'X2')
            x2_row['evidence']['reasons'].append(f's6.g1_median_s not numeric: {med!r}')
            x2_row.update(fired=True, route=TOOL, status='fired')
        for rid in ('S6a', 'S6b'):
            rows.append(row(rid, None, None, []))
        rows.append(row('S6c', None, HOLD, ['gate_desk.s6']))

    # ---- B1x
    if decide_given:
        step = (decide or {}).get('step') if isinstance(decide, dict) else None
        fired = decide is None or (decide_rc not in (None, 0)) or step not in DECIDE_STEPS
        rows.append(row('B1x', fired, TRL, ['the decide output or the refusal text'],
                        {'step': step, 'rc': decide_rc}))
    else:
        rows.append(row('B1x', None, TRL, ['the decide output'], status='not evaluated (step 8)'))

    # ---- S1
    if proofs_given:
        bad = [] if isinstance(proofs, dict) else ['proofs.json unreadable']
        if isinstance(proofs, dict):
            bad += [p.get('id') for p in proofs.get('proofs') or [] if p.get('ok') is not True]
            bad += [t.get('path') for t in proofs.get('ten_paths') or [] if t.get('equals_night') is not True]
            if not proofs.get('proofs') or len(proofs.get('ten_paths') or []) != 10:
                bad.append('proofs.json incomplete (no proofs or not ten paths)')
        rows.append(row('S1', bool(bad), HOLD, ['proofs.json'], {'failing': bad}))
        rows[-1]['note'] = ('no signing. The lead fixes the head if the cause is a stray edit; a needed change to '
                            'one of the ten paths goes to the research lead first (RL-107 item 3)')
    else:
        rows.append(row('S1', None, HOLD, ['proofs.json'], status='not evaluated (step 10)'))

    return rows, rl106


def route_of(rows):
    fired = [r for r in rows if r['fired']]
    routes = {r['route'] for r in fired}
    if TRL in routes:
        return TRL
    if TOOL in routes:
        return TOOL
    if HOLD in routes:
        return HOLD
    return GO


def run(args):
    ins = Inputs()
    record = ins.json('record.json', args.record)
    gate = ins.json('gate_desk.json', args.gate_desk)
    three_a = ins.json('3a.json', args.three_a)
    kit_rc_text = ins.text('kit_desk.rc', args.kit_desk_rc)
    kit_rc = parse_rc(kit_rc_text)
    if kit_rc_text is not None and kit_rc is None:
        ins.problems.append(f'kit_desk.rc unparseable: {kit_rc_text!r}')
    kit_stderr = ins.text('kit_desk.stderr', args.kit_desk_stderr, required=False)
    # The kit desk's JSON is read only when it ran (rc 0); a refusal leaves no JSON (step 4).
    kit = ins.json('kit_desk.json', args.kit_desk) if kit_rc == 0 else None
    idle = ins.text('idle_parse_gap.txt', args.idle_parse_gap)
    decide = decide_rc = proofs = None
    if args.decide is not None:
        try:
            decide = json.loads(Path(args.decide).read_text())
        except (OSError, ValueError):
            decide = None
        decide_rc = parse_rc(Path(args.decide_rc).read_text()) if args.decide_rc and Path(args.decide_rc).is_file() \
            else None
    if args.proofs is not None:
        try:
            proofs = json.loads(Path(args.proofs).read_text())
        except (OSError, ValueError):
            proofs = None
    rows, rl106 = evaluate(record, gate, three_a, kit, kit_rc, kit_stderr, idle, decide, decide_rc, proofs,
                           ins.problems, args.decide is not None, args.proofs is not None)
    route = route_of(rows)
    fired = [r for r in rows if r['fired']]
    out = {'schema': SCHEMA, 'route': route, 'fired_rows': [r['row'] for r in fired],
           'packets': {r['row']: r['packet'] for r in fired if r['route'] == TRL},
           'rows': rows, 'rl106_n': rl106,
           'note': ('X2 also fired: the TO-RESEARCH-LEAD rows were read from a desk with an open tool defect'
                    if route == TRL and any(r['row'] == 'X2' and r['fired'] for r in rows) else None),
           'inputs': {k: str(v) if v is not None else None for k, v in sorted(vars(args).items())
                      if k != 'json_out'}}
    return out


def render(out):
    lines = [f"R1 slot verdict: route {out['route']}; fired {out['fired_rows'] or 'none'}"]
    if out['note']:
        lines.append(f"  note: {out['note']}")
    for r in out['rows']:
        mark = {True: 'FIRED', False: 'clear', None: 'n/e'}[r['fired']]
        lines.append(f"{r['row']:5} {mark:6} {r['route_if_fired'] or '-':24} {r['status']}")
        if r['fired']:
            lines.append(f"      evidence: {json.dumps(r['evidence'], sort_keys=True)}")
            if r['packet']:
                lines.append(f"      packet: {'; '.join(r['packet'])}")
    n = out['rl106_n']
    lines.append(f"RL-106 N: n_flag {n.get('n_flag')} n_gate {n.get('n_gate')}")
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--record', type=Path)
    parser.add_argument('--gate-desk', type=Path)
    parser.add_argument('--3a', dest='three_a', type=Path)
    parser.add_argument('--kit-desk', type=Path)
    parser.add_argument('--kit-desk-rc', type=Path)
    parser.add_argument('--kit-desk-stderr', type=Path)
    parser.add_argument('--idle-parse-gap', type=Path)
    parser.add_argument('--decide', type=Path)
    parser.add_argument('--decide-rc', type=Path)
    parser.add_argument('--proofs', type=Path)
    parser.add_argument('--json-out', type=Path, required=True)
    args = parser.parse_args(argv)
    out = run(args)
    try:
        args.json_out.write_text(json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False) + '\n')
    except OSError as error:
        print(f'verdict: cannot write {args.json_out}: {error}', file=sys.stderr)
        return 2
    print(render(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
