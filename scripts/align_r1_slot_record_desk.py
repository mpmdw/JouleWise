#!/usr/bin/env python3
"""B3: the slot-session record desk (spec /Volumes/JW-EXT/scratch/fable-r1-slot-desk-spec.md 2.3; RL-135).

Usage:
  python3.13 -B -s -E scripts/align_r1_slot_record_desk.py RUN_DIR --custody-root "$S" \
      --night-commit a6a09e6d7c3c756551c3e5c3546311c96fe8d3fe --packet-sha256 <PKT_SHA> \
      --json-out out/record.json > out/record.txt

Blind-safe: structure fields of the driver's own record only. Reads
``RUN_DIR/r1_result.json``; ``RUN_DIR/r1_slots.json`` (bytes, for its sha256);
``$S/result.json`` (chain outcome, exit code, fault, census hits); each
``RUN_DIR/<phase>/runtime_result.json`` (flags, g0_outcome, census process
names, admitted_turns, gate_waits_s, load-journal tick times); each bundle's
capture-reap record (the key only); the thermal journal's reading stamps
(tick count only). It copies two rehearsal-energy summary numbers the driver
already wrote (``u5`` / ``planning_temperature``) for the implied energy band
disclosure. No energy, power, meter, transcript or episode file is opened.

Exit 0 when the record was built (a row that fires is data, not an error);
exit 2 when an input is missing or unreadable, or a layout self-check fails.
Output is deterministic: sorted keys, no wall clock, every input with sha256.
"""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

SCHEMA = 'joulewise.align_r1_slot_record_desk.v1'

# ---------------------------------------------------------------- layout constants (confirm in step 0)
# UNCONFIRMED LAYOUT FACT (spec "Not checked", item 3): the file that carries
# device_metadata.capture_reaps. From the code at a6a09e6d7:
# joulewise/adapters/powermetrics_reap.py:226 appends to the adapter's
# _device_metadata["capture_reaps"]; the controller writes that dict as
# `device` in the bundle's metadata.json
# (docs/run_reports/2026-11-12-powermetrics-orphan-reap-review.md:55, 98, 105).
# The key is absent when no capture was reaped.
CAPTURE_REAPS_FILE = 'metadata.json'            # relative to each bundle <phase>/runs/<run>/
CAPTURE_REAPS_KEYPATH = ('device', 'capture_reaps')
# r1_runtime.py:59 RESULT_NAME, written at :2433 into the segment's --output dir
# (= RUN_DIR/<phase>, align_r1_rehearsal.py _invoke/_admission_unit).
RUNTIME_RESULT = 'runtime_result.json'
THERMAL_JOURNAL = 'outputs/align_thermal.jsonl'  # relative to each bundle
LAYOUT_NOTE = 'layout assumption not confirmed: confirm in step 0 on the 11-12 copy'

# ---------------------------------------------------------------- registered constants
# align_r1_rehearsal.py:53 DUTY_BAR (ruling 1(d)); a test asserts equality.
DUTY_MIN_TURNS = 3
DUTY_MAX_FRACTION = 0.40
GATED_D_RUNS = ('D_bank_benign_s1_gated_held', 'D_spam_benign_s1_gated_held_a',
                'D_spam_benign_s1_gated_held_b')      # r1_phase_table.GATED_D_RUNS
X_G = 'X_G_contrast'
PLANNING_SEGMENTS = tuple(f'planning_turn_R_plus_{n}C' for n in (0, 2, 4))
CONFIRMED_PAIR = ('TV0h', 'TVh0')                     # RL-122 item 7 rebind; RL-131 T4
T4_FLAGS = ('r1.sensor_inadmissible', 'r1.picks_aliased')
G0_TIMEOUT_FLAG = 'r1.g0_timeout_run'
SHORT_TICK_S = 0.5                                    # RL-91: tick under 0.5 s after the previous
SHORT_TICK_FRACTION = 0.01
NOT_ESTIMABLE = 'not estimable on this session: planning temperature inconclusive (RL-20)'
# Superseded-attempt and release suffixes (align_r1_rehearsal.py G0_TIMEOUT_SUFFIX, _fresh_name
# '.rejectedN', g0_wait_record '.g0_release'; scratch-copy '.g0_timeoutN'/'.g0_releaseN').
SUFFIX = re.compile(r'(\.(?:g0_timeout|g0_release|rejected)\d*)+$')


class DeskInputError(RuntimeError):
    pass


def base_name(segment):
    return SUFFIX.sub('', segment or '')


def is_planning(segment):
    return base_name(segment) in PLANNING_SEGMENTS


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


class Reader:
    """Reads files, recording every one with its sha256 under a labelled root."""

    def __init__(self, roots):
        self.roots = roots          # label -> Path
        self.inputs = {}

    def _label(self, path):
        for label, root in self.roots.items():
            try:
                return f'{label}/{Path(path).relative_to(root).as_posix()}'
            except ValueError:
                continue
        return str(path)

    def raw(self, path):
        try:
            data = Path(path).read_bytes()
        except OSError as error:
            raise DeskInputError(f'cannot read {path}: {error}') from error
        self.inputs[self._label(path)] = sha256_bytes(data)
        return data

    def json(self, path):
        data = self.raw(path)
        try:
            return json.loads(data)
        except ValueError as error:
            raise DeskInputError(f'{path}: not JSON: {error}') from error


# ---------------------------------------------------------------- blocks
def identity_block(result, slots_sha, chain, night_commit, packet_sha):
    status = result.get('status')
    executed = result.get('executed_commit')
    registration = result.get('registration_sha256')
    packet = (result.get('prepare_packet') or {}).get('sha256') if isinstance(result.get('prepare_packet'), dict) \
        else None
    exit_code = chain.get('chain_exit_code')
    checks = {'status_complete': status == 'complete', 'chain_exit_0': exit_code == 0,
              'executed_commit_is_night_commit': executed == night_commit,
              'r1_slots_sha256_equals_registration_sha256': slots_sha is not None and slots_sha == registration,
              'packet_sha256_equals_expected': packet is not None and packet == packet_sha}
    return {'status': status, 'error': result.get('error'), 'executed_commit': executed,
            'night_commit': night_commit, 'registration_sha256': registration, 'r1_slots_sha256': slots_sha,
            'packet_sha256': packet, 'packet_sha256_source': 'r1_result.json prepare_packet.sha256',
            'packet_sha256_expected': packet_sha,
            'chain_outcome': chain.get('chain_outcome'), 'chain_exit_code': exit_code,
            'chain_fault': chain.get('fault'), 'chain_census_hits': chain.get('census_hits'),
            'checks': checks, 'ok': all(checks.values())}


def thermometry_block(result):
    thermo = result.get('thermometry') if isinstance(result.get('thermometry'), dict) else {}
    d = thermo.get('D') if isinstance(thermo.get('D'), dict) else {}
    conf = d.get('night_confirmation') if isinstance(d.get('night_confirmation'), dict) else None
    flags = sorted(set(list(thermo.get('flags') or []) + list(d.get('flags') or [])))
    pair = (conf.get('s_fast'), conf.get('s_slow')) if conf else (None, None)
    reasons = []
    if thermo.get('bar') != 'pass':
        reasons.append(f"thermometry.bar is {thermo.get('bar')!r}, not 'pass'")
    if conf is None or conf.get('ok') is not True:
        reasons.append('night_confirmation.ok is not True' if conf is not None else 'night_confirmation absent')
    if pair != CONFIRMED_PAIR:
        reasons.append(f'confirmed pair {list(pair)} is not {list(CONFIRMED_PAIR)}')
    for flag in T4_FLAGS:
        if flag in flags:
            reasons.append(f'flag {flag}')
    return {'bar': thermo.get('bar'), 'bar_reason': thermo.get('bar_reason'),
            'night_confirmation': None if conf is None else {
                k: conf.get(k) for k in ('ok', 'reasons', 's_fast', 's_slow', 'authority')},
            'sensor_pick_changed': d.get('sensor_pick_changed'), 's_fast': d.get('s_fast'), 's_slow': d.get('s_slow'),
            'flags': flags, 't4_fired': bool(reasons), 't4_reasons': reasons}


def duty_row(row, fallback_t_dead):
    phases = row.get('phases_s') or {}
    g0, g1, h = (phases.get(k) for k in ('G0', 'G1', 'H'))
    gate_hold = g0 + g1 + h if all(finite(v) for v in (g0, g1, h)) else None
    duty = row.get('duty_T_dead_s')
    if not finite(duty):
        duty = fallback_t_dead if finite(fallback_t_dead) else row.get('T_dead_s')
    cap = DUTY_MAX_FRACTION * duty if finite(duty) else None
    turns, x7 = row.get('admitted_turns'), row.get('x7')
    checks = {'no_x7': x7 is False if isinstance(x7, bool) else None,
              'admitted_turns_ge_3': turns >= DUTY_MIN_TURNS if type(turns) is int else None,
              'gate_hold_le_40pct_T_dead': gate_hold <= cap if gate_hold is not None and cap is not None else None}
    driver_bar = row.get('duty_bar') or {}
    if row.get('inconclusive_reason') is not None:
        recomputed = 'inconclusive'
    elif any(v is None for v in checks.values()):
        recomputed = None
    else:
        recomputed = 'pass' if all(checks.values()) else 'fail'
    return {'run': row.get('run'), 'admitted_turns': turns, 'x7': x7,
            'phases_s': {'G0': g0, 'G1': g1, 'H': h}, 'gate_hold_s': gate_hold,
            'driver_gate_hold_s': row.get('gate_hold_s'), 'duty_T_dead_s': duty, 'cap_0_40_T_dead_s': cap,
            'checks': checks, 'driver_checks': driver_bar.get('checks'),
            'inconclusive_reason': row.get('inconclusive_reason'), 'g0_outcome': row.get('g0_outcome'),
            'verdict': driver_bar.get('verdict'), 'recomputed_verdict': recomputed,
            'agrees': recomputed == driver_bar.get('verdict')}


def duty_block(result):
    bar = result.get('duty_bar') if isinstance(result.get('duty_bar'), dict) else {}
    rows = [duty_row(r, bar.get('duty_T_dead_s')) for r in (result.get('deadman_budget') or [])
            if isinstance(r, dict)]
    verdicts = [r['verdict'] for r in rows]
    recomputed = ('fail' if 'fail' in verdicts else 'inconclusive' if 'inconclusive' in verdicts else 'pass') \
        if rows else None
    mismatch = [r['run'] for r in rows if not r['agrees']]
    if rows and recomputed != bar.get('verdict'):
        mismatch.append('overall')
    return {'verdict': bar.get('verdict'), 'verdict_source': 'driver duty_bar.verdict (registered)',
            'duty_T_dead_s': bar.get('duty_T_dead_s'), 'inconclusive_runs': bar.get('inconclusive_runs'),
            'reason': bar.get('reason'), 'runs': rows, 'recomputed_overall': recomputed,
            'recompute_mismatch': mismatch}


def x_g_block(result, x_g_runtime):
    x_g = result.get('x_g') if isinstance(result.get('x_g'), dict) else {}
    rt = x_g_runtime or {}
    flags = rt.get('episode_flags')
    rt_x7 = any(str(f).startswith('episode.deadman:') for f in flags) if isinstance(flags, list) else None
    return {'status': x_g.get('status'), 'inconclusive_reason': x_g.get('inconclusive_reason'),
            'g0_outcome': x_g.get('g0_outcome'), 'x7': x_g.get('x7'),
            'admitted_turns': rt.get('admitted_turns', x_g.get('admitted_turns')),
            'runtime_x7': rt_x7, 'gate_waits_s': rt.get('gate_waits_s'),
            'runtime_result_present': x_g_runtime is not None}


def s6_block(result):
    s6 = result.get('s6_tuning') if isinstance(result.get('s6_tuning'), dict) else {}
    return {'G1_median_s': s6.get('G1_median_s'), 'H_median_s': s6.get('H_median_s'),
            'G1_waits': s6.get('G1_waits'), 'H_waits': s6.get('H_waits'), 'status': s6.get('status'),
            'S6_c': s6.get('S6_c')}


def planning_block(result):
    temp = result.get('planning_temperature') if isinstance(result.get('planning_temperature'), dict) else {}
    u5 = result.get('u5') if isinstance(result.get('u5'), dict) else {}
    return {'planning_temperature_status': temp.get('status'),
            'inconclusive_states': temp.get('inconclusive_states'),
            'u5_verdict': u5.get('verdict'), 'calibration_precools': result.get('calibration_precools')}


def aba_block(result):
    hp = result.get('high_power') if isinstance(result.get('high_power'), dict) else {}
    ac, slots_ac = result.get('ac_powermode'), result.get('slots_ac_powermode')
    return {'verdict': hp.get('verdict'), 'reason': hp.get('reason'), 't_decline_s': hp.get('t_decline_s'),
            'start_state_bars': hp.get('start_state_bars'), 'ac_powermode': ac, 'slots_ac_powermode': slots_ac,
            'ok': hp.get('verdict') == 'not_adopted' and ac == 0 and slots_ac == 0}


def flags_block(result):
    inadmissible = result.get('inadmissible_slots') if isinstance(result.get('inadmissible_slots'), dict) else {}
    return {'inconclusive_segments': result.get('inconclusive_segments') or {},
            'inadmissible_slots': {k: v for k, v in sorted(inadmissible.items()) if v},
            'skipped_segments': result.get('skipped_segments') or {},
            'g0_waits': result.get('g0_waits') or []}


def non_planning_g0_not_released(result):
    return [row for row in (result.get('g0_waits') or []) if isinstance(row, dict)
            and not is_planning(row.get('segment')) and row.get('g0_outcome') != 'released']


def _has_flag(value, flag):
    """True when ``flag`` appears in any list under a key ending in 'flags', at any depth."""
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).endswith('flags') and isinstance(child, list) and flag in child:
                return True
            if _has_flag(child, flag):
                return True
    elif isinstance(value, list):
        return any(_has_flag(child, flag) for child in value)
    return False


def rl106_block(runtime_results):
    members = sorted(name for name, rt in runtime_results.items() if _has_flag(rt, G0_TIMEOUT_FLAG))
    return {'flag': G0_TIMEOUT_FLAG, 'members': members, 'n_flag': len(members), 'n_gate': None,
            'N': len(members), 'definition': ('member sessions (runtime_result.json per phase dir, superseded '
                                              'attempts included) whose flags contain r1.g0_timeout_run; '
                                              'counted once per member (RL-135 item 4). n_gate is filled by B4.')}


def ticks(times_s):
    diffs = [b - a for a, b in zip(times_s, times_s[1:])]
    short = sum(1 for d in diffs if d < SHORT_TICK_S)
    n = len(times_s)
    return {'ticks': n, 'short': short, 'fraction': short / n if n else None,
            'over_1pct': bool(n) and short / n > SHORT_TICK_FRACTION}


def rl91_block(reaps, unreadable, runtime_results, thermal_ticks, metadata_files=0):
    records, not_ok = [], []
    for bundle, items in sorted(reaps.items()):
        for item in items:
            absent = item.get('absent') if isinstance(item, dict) else None
            records.append({'bundle': bundle, 'absent': absent,
                            'reason': item.get('reason') if isinstance(item, dict) else None})
            if absent is not True:
                not_ok.append(bundle)
    pm = []
    for name, rt in sorted(runtime_results.items()):
        for census in rt.get('census') or []:
            if any(Path(str(p.get('comm', ''))).name == 'powermetrics' for p in (census.get('processes') or [])
                   if isinstance(p, dict)):
                pm.append(name)
                break
    load = {}
    for name, rt in sorted(runtime_results.items()):
        t = rt.get('cpu_busy_t_s')
        if isinstance(t, list) and all(finite(v) for v in t):
            load[name] = ticks(t)
    total_load = {'ticks': sum(v['ticks'] for v in load.values()), 'short': sum(v['short'] for v in load.values())}
    total_thermal = {'ticks': sum(v['ticks'] for v in thermal_ticks.values()),
                     'short': sum(v['short'] for v in thermal_ticks.values())}
    # RL-138 item 9: an empty list is "none recorded", not "none happened"; the census arm is the check.
    summary = (f'no reap record in {metadata_files} {CAPTURE_REAPS_FILE} files' if not records else
               f'{len(records)} reap record(s) in {metadata_files} {CAPTURE_REAPS_FILE} files')
    return {'capture_reaps': records, 'capture_reaps_summary': summary, 'metadata_files_read': metadata_files,
            'capture_reaps_not_absent': sorted(set(not_ok)),
            'capture_reaps_unreadable': unreadable,
            'root_powermetrics_in_census': pm,
            'ticker': {'load_journal': {'source': 'runtime_result.json cpu_busy_t_s (r1_runtime ticker)',
                                        'members': load, 'total': total_load},
                       'thermal_journal': {'source': f'{THERMAL_JOURNAL} reading started.monotonic_ns',
                                           'members': thermal_ticks, 'total': total_thermal},
                       'over_1pct_members': sorted(set(
                           [k for k, v in load.items() if v['over_1pct']]
                           + [k for k, v in thermal_ticks.items() if v['over_1pct']])),
                       'note': ('a member over 1% short ticks also needs its load statistics printed '
                                'time-weighted (RL-91); owed only for over_1pct_members, and signing holds '
                                'until it is in the slots PR (RL-138 item 9; B4 row R1p)')},
            'ok': not not_ok and not pm}


def implied_energy_band(result):
    temp = result.get('planning_temperature') if isinstance(result.get('planning_temperature'), dict) else {}
    if temp.get('status') == 'inconclusive':
        return NOT_ESTIMABLE
    u5 = result.get('u5') if isinstance(result.get('u5'), dict) else {}
    beta, beta90, delta = temp.get('beta_T_j_per_c'), temp.get('abs_beta_T_90_j_per_c'), temp.get('delta_slow_c')
    if not all(finite(v) for v in (beta, beta90, delta)):
        return 'not estimable on this session: planning_temperature carries no beta_T / delta_slow_c'
    return {'point_j': abs(beta) * delta, 'bound90_j': beta90 * delta, 'delta_slow_c': delta,
            'beta_T_j_per_c': beta, 'abs_beta_T_90_j_per_c': beta90,
            'u5_state_shift_point_j': u5.get('state_shift_point_j'),
            'u5_state_shift_bound90_j': u5.get('state_shift_bound90_j'),
            'source': 'r1_result.json planning_temperature (u5 copies beside it)'}


def host_block(result):
    out = {'powermode': result.get('powermode')}
    for key in ('restore_deferred', 'restore_skipped'):
        if key in result:
            out[key] = result[key]
    return out


# ---------------------------------------------------------------- collection
def read_reaps(reader, run_dir):
    bundles = sorted(p for p in run_dir.glob('*/runs/*') if p.is_dir())
    reaps, unreadable, found = {}, [], 0
    for bundle in bundles:
        name = bundle.relative_to(run_dir).as_posix()
        path = bundle / CAPTURE_REAPS_FILE
        if not path.is_file():
            unreadable.append(name)
            continue
        try:
            meta = reader.json(path)
        except DeskInputError:
            unreadable.append(name)
            continue
        node = meta
        for key in CAPTURE_REAPS_KEYPATH[:-1]:
            node = node.get(key) if isinstance(node, dict) else None
        if not isinstance(node, dict):
            unreadable.append(name)
            continue
        found += 1
        items = node.get(CAPTURE_REAPS_KEYPATH[-1], [])
        if items:
            reaps[name] = items if isinstance(items, list) else [items]
    if bundles and not found:
        raise DeskInputError(
            f'CAPTURE_REAPS_FILE={CAPTURE_REAPS_FILE!r} keypath {".".join(CAPTURE_REAPS_KEYPATH[:-1])!r}: no '
            f'bundle under {run_dir}/*/runs/* has it; {LAYOUT_NOTE}')
    return reaps, unreadable, found


def read_thermal_ticks(reader, run_dir):
    out = {}
    for path in sorted(run_dir.glob(f'*/runs/*/{THERMAL_JOURNAL}')):
        stamps = []
        for line in reader.raw(path).splitlines():
            if b'"reading"' not in line:
                continue
            row = json.loads(line)
            if row.get('kind') == 'reading':
                stamps.append(row['started']['monotonic_ns'] / 1e9)
        stamps.sort()
        out[path.relative_to(run_dir).parts[0]] = ticks(stamps)
    return out


def build(run_dir, custody_root, night_commit, packet_sha):
    run_dir, custody_root = Path(run_dir), Path(custody_root)
    reader = Reader({'RUN_DIR': run_dir, 'CUSTODY': custody_root})
    result = reader.json(run_dir / 'r1_result.json')
    if not isinstance(result, dict):
        raise DeskInputError('r1_result.json is not an object')
    slots_path = run_dir / 'r1_slots.json'
    slots_sha = sha256_bytes(reader.raw(slots_path)) if slots_path.is_file() else None
    chain = reader.json(custody_root / 'result.json')
    runtime_results = {}
    for path in sorted(run_dir.glob(f'*/{RUNTIME_RESULT}')):
        value = reader.json(path)
        runtime_results[path.parent.name] = value if isinstance(value, dict) else {}
    if not runtime_results and result.get('status') == 'complete':
        raise DeskInputError(f'RUNTIME_RESULT={RUNTIME_RESULT!r}: no {run_dir}/<phase>/{RUNTIME_RESULT}; '
                             f'{LAYOUT_NOTE}')
    reaps, unreadable, metadata_files = read_reaps(reader, run_dir)
    thermal_ticks = read_thermal_ticks(reader, run_dir)
    record = {
        'schema': SCHEMA, 'night': run_dir.name,
        'layout': {'capture_reaps_file': CAPTURE_REAPS_FILE, 'capture_reaps_keypath': list(CAPTURE_REAPS_KEYPATH),
                   'runtime_result': RUNTIME_RESULT, 'thermal_journal': THERMAL_JOURNAL, 'confirm': LAYOUT_NOTE},
        'identity': identity_block(result, slots_sha, chain, night_commit, packet_sha),
        'thermometry': thermometry_block(result),
        'duty': duty_block(result),
        'x_g': x_g_block(result, runtime_results.get(X_G)),
        's6': s6_block(result),
        'planning': planning_block(result),
        'aba': aba_block(result),
        'flags': flags_block(result),
        'non_planning_g0_not_released': non_planning_g0_not_released(result),
        'rl106_n': rl106_block(runtime_results),
        'rl91': rl91_block(reaps, unreadable, runtime_results, thermal_ticks, metadata_files),
        'implied_energy_band': implied_energy_band(result),
        'host': host_block(result),
        'runtime_g0_outcomes': {k: v.get('g0_outcome') for k, v in sorted(runtime_results.items())
                                if 'g0_outcome' in v},
    }
    record['tool_checks'] = {'duty_recompute_mismatch': record['duty']['recompute_mismatch'],
                             'capture_reaps_unreadable': unreadable}
    record['inputs'] = [{'path': p, 'sha256': d} for p, d in sorted(reader.inputs.items())]
    return record


# ---------------------------------------------------------------- render
def render(rec):
    i, t, d = rec['identity'], rec['thermometry'], rec['duty']
    lines = [f"R1 slot record desk: {rec['night']}",
             f"identity ok={i['ok']} status={i['status']} chain={i['chain_outcome']} exit={i['chain_exit_code']} "
             f"commit={i['executed_commit']} slots_sha={i['r1_slots_sha256']} registration={i['registration_sha256']} "
             f"packet={i['packet_sha256']}"]
    lines += [f'    !! {k}' for k, v in i['checks'].items() if not v]
    lines.append(f"thermometry bar={t['bar']} t4_fired={t['t4_fired']} confirmation={t['night_confirmation']}")
    lines += [f'    -> {r}' for r in t['t4_reasons']]
    lines.append(f"duty verdict={d['verdict']} (recomputed {d['recomputed_overall']}) T_dead={d['duty_T_dead_s']}")
    for r in d['runs']:
        lines.append(f"    {r['run']}: turns={r['admitted_turns']} x7={r['x7']} G0/G1/H={r['phases_s']} "
                     f"hold={r['gate_hold_s']} cap={r['cap_0_40_T_dead_s']} checks={r['checks']} "
                     f"verdict={r['verdict']} recomputed={r['recomputed_verdict']}")
    x = rec['x_g']
    lines.append(f"x_g status={x['status']} g0={x['g0_outcome']} x7={x['x7']} turns={x['admitted_turns']} "
                 f"gate_waits_s={x['gate_waits_s']}")
    lines.append(f"s6 {rec['s6']}")
    lines.append(f"planning {rec['planning']}")
    a = rec['aba']
    lines.append(f"aba ok={a['ok']} verdict={a['verdict']} t_decline={a['t_decline_s']} ac={a['ac_powermode']} "
                 f"slots_ac={a['slots_ac_powermode']} reason={a['reason']}")
    f = rec['flags']
    lines.append(f"inconclusive_segments {f['inconclusive_segments']}")
    lines.append(f"inadmissible_slots {f['inadmissible_slots']}")
    lines.append(f"skipped_segments {f['skipped_segments']}")
    lines.append(f"non_planning_g0_not_released {rec['non_planning_g0_not_released']}")
    n = rec['rl106_n']
    lines.append(f"RL-106 n_flag={n['n_flag']} members={n['members']}")
    r = rec['rl91']
    lt, tt = r['ticker']['load_journal']['total'], r['ticker']['thermal_journal']['total']
    lines.append(f"RL-91 capture_reaps: {r['capture_reaps_summary']}")
    lines.append(f"RL-91 ok={r['ok']} reaps={r['capture_reaps']} not_absent={r['capture_reaps_not_absent']} "
                 f"unreadable={r['capture_reaps_unreadable']} powermetrics_in_census={r['root_powermetrics_in_census']}")
    lines.append(f"    ticker load: {lt['short']} short in {lt['ticks']}; thermal: {tt['short']} short in {tt['ticks']}; "
                 f"over 1%: {r['ticker']['over_1pct_members']}")
    lines.append(f"implied_energy_band {rec['implied_energy_band']}")
    lines.append(f"host {rec['host']}")
    lines.append(f"tool_checks {rec['tool_checks']}")
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('--custody-root', type=Path, required=True)
    parser.add_argument('--night-commit', required=True)
    parser.add_argument('--packet-sha256', required=True)
    parser.add_argument('--json-out', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        record = build(args.run_dir, args.custody_root, args.night_commit, args.packet_sha256)
    except DeskInputError as error:
        print(f'record desk: {error}', file=sys.stderr)
        return 2
    args.json_out.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(render(record))
    return 0


if __name__ == '__main__':
    sys.exit(main())
