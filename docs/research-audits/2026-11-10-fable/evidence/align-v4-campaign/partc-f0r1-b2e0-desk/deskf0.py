#!/usr/bin/env python3.13
"""Desk table for STANDING-F0 run 1 (Part C only) at b2e01464d (RUN_STATE 346/351/352), THERMAL VALUES ONLY. The second Part C's deskpc2.py (partc2-c3f4-desk, c9fc0339d) with only BUILD/BUILD_HEAD changed (thermal_gates.py and thermal_desk.py: git diff c3f4bacd8 b2e01464d empty; thermal_gates sha256 asserted as before).
Earlier header (second Part C): desk319.py with only BUILD/BUILD_HEAD changed (thermal_gates.py and thermal_desk.py are byte-identical at f30a97d00 and c3f4bacd8).

Adapted from the item-316 desk (/Volumes/JW-EXT/scratch/partc-desk/scripts/desk_table.py) with every
powermetrics-derived clock row and every events.jsonl read removed (events.jsonl carries a power key).
Opens only: the members' outputs/align_thermal.jsonl, outputs/align_turns.jsonl (turn stamps, clock-mapping
offset, prefill_tokens, stop condition, flags, and the LENGTH of output_token_ids; no id is read or printed),
step-D's outputs/align_window_reference.json, recovery/align_thermal.jsonl and inventory/r1_classification.json,
soak/soak_reference.json and the soak sensors journal.
Code: thermal_gates/thermal_desk from the clean worktree at c3f4bacd8; the B1 slot desk tool at 04059c26e
via git show, executed in memory (as the 316 desk did).
Usage: python3.13 -B desk319.py OUT_COPY OUT_JSON
"""
import bisect, hashlib, json, subprocess, sys, types
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
NS = 10**9
BUILD = Path('/Volumes/JW-EXT/jw-wt/partc-b2e0')
BUILD_HEAD = 'b2e01464d6d4fbf2901ff4d4154df9455104a12a'
TG_SHA = 'c72937bd8bf7b5553c1ffd70e76018ffbf25f32578533c8749aa88419837918d'
B1_COMMIT, B1_PATH = '04059c26e', 'scripts/align_r1_slot_gate_desk.py'
OUT = Path(sys.argv[1]); OUT_JSON = Path(sys.argv[2])
MEMBERS = {'step_D': 'part-c/step_D_prefill_10k_decode_4096/runs/align-v4-r1-step-d',
           'D_bank': 'part-c/D_bank_benign_s1_gated_held/runs/align-v4-r1-d-bank-benign-s1',
           'X_G': 'part-c/X_G_contrast/runs/align-v4-r1-x-g'}
RECOVERY = 'part-c/step_D_prefill_10k_decode_4096/recovery/align_thermal.jsonl'
CLASSIF = 'part-c/step_D_prefill_10k_decode_4096/inventory/r1_classification.json'


def sha(b): return hashlib.sha256(b).hexdigest()
def jl(p): return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]


head = subprocess.check_output(['git', '-C', str(BUILD), 'rev-parse', 'HEAD'], text=True).strip()
assert head == BUILD_HEAD, head
assert not subprocess.check_output(['git', '-C', str(BUILD), 'status', '--porcelain', '--untracked-files=no'], text=True).strip()
sys.path.insert(0, str(BUILD))
from joulewise.align.apple import thermal_gates as tg  # noqa: E402
from joulewise.align.apple.thermal_desk import thermal_exclusions  # noqa: E402
assert sha(Path(tg.__file__).read_bytes()) == TG_SHA
src = subprocess.run(['git', '-C', str(BUILD), 'show', f'{B1_COMMIT}:{B1_PATH}'], check=True, capture_output=True).stdout
b1 = types.ModuleType('b1'); b1.__file__ = f'{B1_COMMIT}:{B1_PATH}'
exec(compile(src, b1.__file__, 'exec'), b1.__dict__)
out = {'code': {'build_head': head, 'thermal_gates_sha256': TG_SHA, 'b1_blob_sha256': sha(src)}, 'inputs': {}}


def fresh(t, pm): return type(pm) is int and t - pm <= 2 * NS
def age(t, pm): return None if type(pm) is not int else (t - pm) / NS
def ok_state(st): return st.get('os_level') == 0 and st.get('pm_state') == 'Nominal'


def load(name):
    base = OUT / MEMBERS[name]
    raw = (base / 'outputs/align_thermal.jsonl').read_bytes()
    out['inputs'][MEMBERS[name] + '/outputs/align_thermal.jsonl'] = sha(raw)
    rows, gates, begins, off, start = b1.project_journal(tg, raw)
    raw_rows = [json.loads(x) for x in raw.decode().splitlines() if x.strip()]
    tp = base / 'outputs/align_turns.jsonl'
    out['inputs'][MEMBERS[name] + '/outputs/align_turns.jsonl'] = sha(tp.read_bytes())
    turns = []
    offs = []
    for t in jl(tp):
        o = t['clock_mapping']['offset_ns']; offs.append(o)
        g = t['generation']
        turns.append({'index': t['turn'], 'start_ns': round(t['start_stamp']['epoch_s'] * NS) + o,
                      'end_ns': round(t['end_stamp']['epoch_s'] * NS) + o, 'decode_tokens': len(g['output_token_ids']),
                      'prefill_tokens': g['prefill_tokens'], 'stop': g['runtime_stop_condition'],
                      'flags': t['flags']})
    j = types.SimpleNamespace(seg=name, base=name, kind='member', rows=rows, gates=gates, off=off, session=start,
                              raw_rows=raw_rows, thermal={'sensors': {'s_fast': start['s_fast'], 's_slow': start['s_slow']},
                                                          'delta_fast_c': 1.0, 'delta_slow_c': 1.0, 'turn_cap_s': 300.0},
                              policy_source='registered floor 1.0/1.0', stages={}, wref=None, condition=None,
                              fin=[r['finished']['monotonic_after_ns'] for r in rows],
                              times=[r['monotonic_ns'] for r in rows], turns=turns,
                              clock_check_us=(off + sorted(offs)[len(offs) // 2]) / 1e3)
    return j


J = {n: load(n) for n in MEMBERS}
out['clock_check_us'] = {n: j.clock_check_us for n, j in J.items()}


def rd(j):
    o = []
    for r in j.rows:
        s = r.get('status') or {}
        o.append((r['monotonic_ns'], r['sensors'].get('TV0h'), r['sensors'].get('TV1h'), s.get('os_level'),
                  s.get('pm_state'), s.get('pm_observed_ns')))
    return o


# ---------------- gates: replay, clause last out, release sample under the 2 s rule
val, fails = b1.validate(tg, list(J.values()))
vrows = iter(val['rows'])
gate_rows = []
for n, j in J.items():
    for g in j.gates:
        if g['kind'] not in ('G0', 'G1', 'H'):
            continue
        v = next(vrows)
        last, _, final = b1.last_violations(tg, j, g, b1.gate_rows(j, g), delta_fast=1.0, delta_slow=1.0)
        clause, ties = b1.clause_last_of(g, last, final)
        x = g['exit_sample_ns']
        ex = b1.row_at(j, x) if x is not None else None
        st = (ex or {}).get('status') or {}
        gate_rows.append({'member': n, 'gate': g['kind'], 'turn': g['turn'], 'outcome': g['outcome'],
                          'duration_s': g['duration_s'], 'replay_agrees': v['agree'], 'replayed_s': v['replayed'][1],
                          'clause_last': clause, 'ties': ties,
                          'last_fail_s': {c: last.get(c) for c in ('valid', 'band_fast', 'band_slow', 'slope_slow', 'status')},
                          'entry_TV0h': g['entry_sensors'].get('TV0h'), 'entry_slope': g.get('entry_slope_c_per_min'),
                          'ref_fast_c': g['reference']['fast_c'], 'release_fast_c': g['release']['fast_c'],
                          'release_slow_c': g['release']['slow_c'], 'slope_at_release': g.get('slope_c_per_min'),
                          'exit_level': st.get('os_level'), 'exit_state': st.get('pm_state'),
                          'exit_age_s': age(x, st.get('pm_observed_ns')) if x is not None else None,
                          'exit_ok_2s': (ok_state(st) and fresh(x, st.get('pm_observed_ns'))) if x is not None else None,
                          'start_ns': g['start_ns'], 'end_ns': g['end_ns']})
out['replay'] = {'all_agree': val['all_agree'], 'counts': val['counts'], 'fails': fails}
out['gates'] = gate_rows


def five_after(r_, t0, need_fresh=True, n=5):
    run, prev = [], None
    for r in r_:
        if r[0] <= t0:
            continue
        if prev is not None and r[0] - prev > 2 * NS:
            run = []
        prev = r[0]
        good = r[3] == 0 and r[4] == 'Nominal' and (not need_fresh or fresh(r[0], r[5]))
        run = run + [r] if good else []
        if len(run) >= n:
            return (run[0][0] - t0) / NS, run[0][1]
    return None


# ---------------- per turn (row 6 thermal part; section 2; G1 after a hot turn)
row6 = {}
for n, j in J.items():
    r_ = rd(j)
    per = []
    for t in j.turns:
        inturn = [r for r in r_ if t['start_ns'] <= r[0] <= t['end_ns']]
        lv = [r[3] for r in inturn]; ss = [r[4] for r in inturn]
        os_nom = False if any(type(v) is int and v > 0 for v in lv) else (True if lv and all(v == 0 for v in lv) else None)
        pm_nom = False if any(s not in (None, 'Unknown', 'Nominal') for s in ss) else (True if ss and all(s == 'Nominal' for s in ss) else None)
        fo = next((r for r in inturn if (type(r[3]) is int and r[3] > 0) or r[4] not in (None, 'Unknown', 'Nominal')), None)
        l1 = next((r for r in inturn if r[3] == 1), None); l2 = next((r for r in inturn if r[3] == 2), None)
        t93 = next((r for r in inturn if r[1] is not None and r[1] >= 93.0), None)
        first = inturn[0] if inturn else None
        after = [r for r in r_ if r[0] > t['end_ns']]
        lvl0 = next((r for r in after if r[3] == 0), None)
        nomf = next((r for r in after if r[4] == 'Nominal' and fresh(r[0], r[5])), None)
        lastfresh = next((r for r in reversed(after) if fresh(r[0], r[5])), None)
        stale = [r for r in after if r[5] is not None and not fresh(r[0], r[5])]
        s_ = lambda r: None if r is None else round((r[0] - t['start_ns']) / NS, 2)
        e_ = lambda r: None if r is None else round((r[0] - t['end_ns']) / NS, 2)
        per.append({'turn': t['index'], 'prefill_tokens': t['prefill_tokens'], 'decode_tokens': t['decode_tokens'],
                    'turn_s': round((t['end_ns'] - t['start_ns']) / NS, 2), 'stop': t['stop'],
                    'readings': len(inturn), 'os_nominal_1Hz': os_nom, 'pm_nominal_1Hz': pm_nom,
                    'first_reading_after_start': None if first is None else
                    {'s': s_(first), 'level': first[3], 'state': first[4], 'age_s': age(first[0], first[5]),
                     'ok_2s': ok_state({'os_level': first[3], 'pm_state': first[4]}) and fresh(first[0], first[5])},
                    'first_off': None if fo is None else {'s_from_start': s_(fo), 'level': fo[3], 'state': fo[4], 'TV0h': fo[1]},
                    'first_level1_s': s_(l1), 'first_level2_s': s_(l2), 'first_TV0h_ge_93_s': s_(t93),
                    'max_TV0h': max((r[1] for r in inturn if r[1] is not None), default=None),
                    'level_counts': dict(Counter(str(v) for v in lv)), 'state_counts': dict(Counter(str(v) for v in ss)),
                    'journal_after_end_s': None if not after else round((after[-1][0] - t['end_ns']) / NS, 2),
                    'level0_after_end_s': e_(lvl0), 'nominal_fresh_after_end_s': e_(nomf),
                    'five_L0_Nominal_fresh': five_after(r_, t['end_ns']),
                    'five_L0_Nominal_any_stamp': five_after(r_, t['end_ns'], need_fresh=False),
                    'last_fresh_state_after_end': None if lastfresh is None else
                    {'s': e_(lastfresh), 'level': lastfresh[3], 'state': lastfresh[4], 'age_s': age(lastfresh[0], lastfresh[5])},
                    'stale_after_end': None if not stale else {'n': len(stale), 'from_s': e_(stale[0]), 'to_s': e_(stale[-1]),
                                                               'value': Counter(str(r[4]) for r in stale).most_common(2),
                                                               'max_age_s': max(age(r[0], r[5]) for r in stale)}})
    obs = [{'os_nominal': p['os_nominal_1Hz'], 'pm_nominal': p['pm_nominal_1Hz']} for p in per]
    try:
        excl = thermal_exclusions({'flags': [], 'turn_observation': obs})
    except Exception as e:
        excl = f'error: {type(e).__name__}: {e}'
    # G1 after a hot turn: a G1 whose previous turn left level 0 or Nominal
    hot_g1 = []
    for g in j.gates:
        if g['kind'] == 'G1':
            prev = next((p for p in per if p['turn'] == g['turn'] - 1), None)
            if prev and (prev['os_nominal_1Hz'] is False or prev['pm_nominal_1Hz'] is False):
                hot_g1.append({'turn': g['turn'], 'duration_s': g['duration_s'], 'outcome': g['outcome']})
    row6[n] = {'turns': per, 'exclusion_reasons_1Hz': excl, 'g1_after_hot_turn': hot_g1}
out['row6'] = row6


# ---------------- TV1h != TV0h trigger (close section 5)
def hexrows(j):
    for r in j.raw_rows:
        if r.get('kind') == 'reading':
            yield r


trig = {}
diffrows = []
for n, j in J.items():
    win = []
    for g in j.gates:
        rows = [r for r in j.rows if g['start_ns'] <= r['monotonic_ns'] <= g['end_ns']]
        lb = [r for r in j.rows if g['start_ns'] - 61 * NS <= r['monotonic_ns'] <= g['end_ns']]
        win.append((g['kind'], g['turn'], len(rows), sum(1 for r in rows if r['sensors'].get('TV0h') != r['sensors'].get('TV1h')),
                    sum(1 for r in lb if r['sensors'].get('TV0h') != r['sensors'].get('TV1h'))))
    hx = list(hexrows(j))
    ne = [r for r in hx if (r['values'].get('readings', {}).get('TV0h') or {}).get('raw_hex') !=
          (r['values'].get('readings', {}).get('TV1h') or {}).get('raw_hex')]
    trig[n] = {'rows': len(hx), 'raw_hex_unequal': len(ne),
               'gate_windows (kind, turn, rows, unequal, unequal incl. 61 s look-back)': win}
    for r in ne:
        t = r['started']['monotonic_ns']
        x = r['values']['readings']
        tr = next((tt for tt in j.turns if tt['start_ns'] <= t <= tt['end_ns']), None)
        near = min(j.gates, key=lambda g: abs(t - g['start_ns'])) if j.gates else None
        diffrows.append({'member': n, 'seq': r['seq'], 'TV0h': x['TV0h']['value'], 'TV1h': x['TV1h']['value'],
                         'TV1h_hex': x['TV1h']['raw_hex'],
                         'inside_gate_window': [f"{g['kind']} t{g['turn']}" for g in j.gates if g['start_ns'] <= t <= g['end_ns']],
                         'in_lookback_of': [f"{g['kind']} t{g['turn']}" for g in j.gates if g['start_ns'] - 61 * NS <= t < g['start_ns']],
                         'turn': None if tr is None else tr['index'],
                         's_after_turn_start': None if tr is None else round((t - tr['start_ns']) / NS, 2),
                         'nearest_gate': None if near is None else f"{near['kind']} t{near['turn']}",
                         's_from_nearest_gate_entry': None if near is None else round((t - near['start_ns']) / NS, 2)})
rec_raw = (OUT / RECOVERY).read_bytes(); out['inputs'][RECOVERY] = sha(rec_raw)
rec = [json.loads(x) for x in rec_raw.decode().splitlines() if x.strip()]
recr = [r for r in rec if r.get('kind') == 'reading']
trig['step_D_recovery'] = {'rows': len(recr), 'unequal': sum(1 for r in recr if r['values'].get('sensors', {}).get('TV0h') != r['values'].get('sensors', {}).get('TV1h'))}
soak_p = OUT / 'soak/idle_soak/sensors/align_thermal.jsonl'
soakr = [r for r in jl(soak_p) if r.get('kind') == 'reading']
out['inputs']['soak/idle_soak/sensors/align_thermal.jsonl'] = sha(soak_p.read_bytes())
trig['soak'] = {'rows': len(soakr), 'unequal': sum(1 for r in soakr if r['values'].get('sensors', {}).get('TV0h') != r['values'].get('sensors', {}).get('TV1h'))}
out['tv_trigger'] = trig
out['tv_trigger_rows'] = diffrows

# ---------------- step-D: G0, P4, P2/P6 thermal marks, P7
sd = J['step_D']; t = sd.turns[0]
cls_raw = (OUT / CLASSIF).read_bytes(); out['inputs'][CLASSIF] = sha(cls_raw)
cls = json.loads(cls_raw); c = cls['classification']
p4 = []
for key in ('TV0h', 'TV1h', 'TVh0'):
    r = next((x for x in c['ranking'] if x.get('key') == key), None)
    if r is None:
        p4.append({'key': key, 'absent': True}); continue
    rise = r.get('observed_rise') or r.get('amplitude')
    p4.append({'key': key, 'class': r['class'], 'eligible': r['eligible'], 'clamped': r['clamped'], 'resolving': r.get('resolving'),
               'baseline_c': r['baseline'], 'idle_mode_fraction': r['idle_mode_fraction'],
               'idle_distinct': r['idle_distinct_values'], 'max_1s_change_c': r['max_one_second_change'], 'rise_c': rise,
               'half_rise_minus_max_change_c': None if rise is None else rise / 2 - r['max_one_second_change'], 'reason': r['reason']})
p4_meta = {'s_fast': c.get('s_fast'), 's_slow': c.get('s_slow'), 'TV0h_alias_groups': [g for g in c['alias_groups'] if 'TV0h' in g],
           'selected_key_aliases': c.get('selected_key_aliases'), 'status': c.get('status'), 'night_confirmation': cls.get('night_confirmation')}
r_ = rd(sd)
rec_rd = []
for r in recr:
    if not r.get('error'):
        v = r['values']; s = v.get('status') or {}
        rec_rd.append((r['started']['monotonic_ns'], v['sensors'].get('TV0h'), v['sensors'].get('TV1h'), s.get('os_level'),
                       s.get('pm_state'), s.get('pm_observed_ns')))
lt = t['end_ns']
allrd = sorted(set(r_) | set(rec_rd))
post = [r for r in allrd if r[0] > lt]


def settle(rows, pred, n=5):
    run = 0
    for i, r in enumerate(rows):
        run = run + 1 if pred(r) else 0
        if run >= n:
            return round((rows[i - n + 1][0] - lt) / NS, 2)
    return None


g0 = next(g for g in sd.gates if g['kind'] == 'G0')
rel = g0['release']['fast_c']
first_band = next((r for r in post if r[1] is not None and abs(r[1] - rel) <= 1.0), None)
gaps, prev = [], None
for r in post:
    if prev is not None and r[0] - prev > 2 * NS:
        gaps.append((round((prev - lt) / NS, 2), round((r[0] - lt) / NS, 2)))
    prev = r[0]
at_end = min(r_, key=lambda r: abs(r[0] - lt))
p7 = {'basis': 'from the turn end stamp (align_turns end_stamp); no token stream read',
      'at_turn_end': {'level': at_end[3], 'state': at_end[4], 'age_s': age(at_end[0], at_end[5])},
      'in_run_journal_after_end_s': round((r_[-1][0] - lt) / NS, 2),
      'recovery_journal_s': None if not rec_rd else [round((rec_rd[0][0] - lt) / NS, 2), round((rec_rd[-1][0] - lt) / NS, 2)],
      'recovery_rows': len(rec_rd), 'recovery_rows_with_status': sum(1 for r in rec_rd if r[3] is not None or r[4] is not None),
      'level0_x5_s': settle(post, lambda r: r[3] == 0),
      'level0_nominal_x5_s': settle(post, lambda r: r[3] == 0 and r[4] == 'Nominal'),
      'level0_nominal_fresh_x5_s': settle(post, lambda r: r[3] == 0 and r[4] == 'Nominal' and fresh(r[0], r[5])),
      'last_fresh_state': next(({'s': round((r[0] - lt) / NS, 2), 'level': r[3], 'state': r[4], 'age_s': age(r[0], r[5])}
                                for r in reversed(r_) if r[0] > lt and fresh(r[0], r[5])), None),
      'gaps_over_2s': gaps, 'g0_release_TV0h': rel,
      'first_in_band_1C': None if first_band is None else {'s': round((first_band[0] - lt) / NS, 2), 'TV0h': first_band[1],
                                                             'level': first_band[3], 'state': first_band[4]},
      'band_1C_x5_s': settle([r for r in post if r[1] is not None], lambda r: abs(r[1] - rel) <= 1.0)}
wref = json.loads((OUT / MEMBERS['step_D'] / 'outputs/align_window_reference.json').read_text())
out['inputs'][MEMBERS['step_D'] + '/outputs/align_window_reference.json'] = sha((OUT / MEMBERS['step_D'] / 'outputs/align_window_reference.json').read_bytes())
soak_ref = json.loads((OUT / 'soak/soak_reference.json').read_text())
out['inputs']['soak/soak_reference.json'] = sha((OUT / 'soak/soak_reference.json').read_bytes())
out['soak'] = {'sensors_c': soak_ref.get('sensors_c'), 'detrended': soak_ref.get('detrended')}
out['step_D'] = {'g0': next(g for g in gate_rows if g['member'] == 'step_D'), 'p4': p4, 'p4_meta': p4_meta,
                 'turn': row6['step_D']['turns'][0], 'window_reference': {k: wref.get(k) for k in ('status', 'fast_c', 'slow_c')},
                 'p7': p7}
OUT_JSON.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + '\n')
print(json.dumps({'replay': out['replay'], 'clock_check_us': out['clock_check_us']}, default=str))
