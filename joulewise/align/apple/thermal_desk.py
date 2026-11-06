"""Synthetic-testable v4 thermal desk support (FINAL-DESIGN §§2.4–2.6).

Inputs are member records, observed journals and frozen-fit residuals, never
model/data paths. This does not refit or change the frozen v3 calibration.
All unavailable evidence produces inconclusive, independently of point values.
"""
from __future__ import annotations

from collections import defaultdict
import math
from statistics import fmean, stdev
import json
from pathlib import Path

from joulewise.align.attribution import attribute_episode
from joulewise.align.apple import thermal as temperature

NS = 1_000_000_000


def _beta_fraction(a, b, x):
    # Modified Lentz continued fraction for the regularized incomplete beta.
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1., 1 - qab * x / qap
    d = 1 / max(d, 1e-300)
    h = d
    for m in range(1, 401):
        for aa in (m * (b - m) * x / ((qam + 2*m) * (a + 2*m)),
                   -(a + m) * (qab + m) * x / ((a + 2*m) * (qap + 2*m))):
            d = 1 + aa * d
            if abs(d) < 1e-300:
                d = 1e-300
            c = 1 + aa / c
            if abs(c) < 1e-300:
                c = 1e-300
            d = 1 / d
            delta = d * c
            h *= delta
        if abs(delta - 1) < 3e-14:
            return h
    raise ArithmeticError('incomplete beta did not converge')


def _ibeta(a, b, x):
    if x <= 0:
        return 0.
    if x >= 1:
        return 1.
    term = math.exp(math.lgamma(a+b) - math.lgamma(a) - math.lgamma(b)
                    + a * math.log(x) + b * math.log1p(-x))
    if x < (a+1)/(a+b+2):
        return term * _beta_fraction(a, b, x) / a
    return 1 - term * _beta_fraction(b, a, 1-x) / b


def t90(df):
    """Two-sided 90% Student t critical value, including fractional Welch df."""
    if df <= 0:
        raise ValueError('positive degrees of freedom required')
    lo, hi = 0., 1.
    def tail(t):
        return .5 * _ibeta(df/2, .5, df/(df+t*t))
    while tail(hi) > .05:
        hi *= 2
    for _ in range(80):
        mid = (lo+hi)/2
        if tail(mid) > .05:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def interval(mean, se, df):
    half = t90(df) * se
    return [mean-half, mean+half]


def bounded(point, ci, margin):
    if point is None or ci is None:
        return 'inconclusive'
    if abs(point) > margin:
        return 'fail'
    return 'pass' if ci[0] >= -margin and ci[1] <= margin else 'inconclusive'


def combine(values):
    return 'fail' if 'fail' in values else 'inconclusive' if 'inconclusive' in values else 'pass'


def regression(x, y):
    """Small OLS with intercept, full-rank refusal, and covariance."""
    n, p = len(y), len(x[0]) if x else 0
    if n <= p or not p:
        return None
    a = [[sum(row[i]*row[j] for row in x) for j in range(p)]
         + [float(i == j) for j in range(p)] for i in range(p)]
    for i in range(p):
        pivot = max(range(i, p), key=lambda k: abs(a[k][i]))
        if abs(a[pivot][i]) < 1e-12:
            return None
        a[i], a[pivot] = a[pivot], a[i]
        scale = a[i][i]
        a[i] = [v/scale for v in a[i]]
        for k in range(p):
            if k != i:
                scale = a[k][i]
                a[k] = [u-scale*v for u, v in zip(a[k], a[i])]
    inv = [row[p:] for row in a]
    xy = [sum(row[i]*v for row, v in zip(x, y)) for i in range(p)]
    coef = [sum(v*u for v, u in zip(row, xy)) for row in inv]
    variance = sum((v-sum(b*t for b, t in zip(coef, row)))**2 for row, v in zip(x, y))/(n-p)
    return {'coef': coef, 'ci90': [interval(b, math.sqrt(max(0, variance*inv[i][i])), n-p)
                                 for i, b in enumerate(coef)], 'df': n-p}


def normalize_journal(rows):
    result = []
    for row in rows:
        if row.get('kind') == 'sample':
            result.append(row)
        elif row.get('module') == 'temperature' and row.get('kind') == 'reading':
            result.append({'kind': 'sample', 'monotonic_ns': row['started']['monotonic_ns'],
                           'finished': {'monotonic_after_ns': row['finished']['monotonic_ns']},
                           **row['values']})
    return sorted(result, key=lambda r: r['monotonic_ns'])


def _coverage(rows, a, b, keys):
    counter = temperature.Coverage(a, keys)
    for row in rows:
        # Preserve the collector's grid and its bracketing edge samples.
        counter.observe(row['monotonic_ns'], row['finished']['monotonic_after_ns'],
                        {'sensors': row['sensors'], 'errors': row.get('errors', {})})
    return counter.report(b)['all_keys']


def member_record(episode, journal, *, os_readings, pm_samples, pm_period_s,
                  turn_rows=(), source='powermetrics', channel='gpu_power', registered_os_readings=None,
                  gate_journal=None):
    """Derive checks from raw observations, not a stored pass bit.

    OS readings: [monotonic_ns, level]. PM samples: {start_ns,end_ns,state,
    active_ns,clock_mhz}. The v4 desk must anchor native PM supports to the
    episode clock before calling this function; missing clocks remain null.
    """
    thermal = episode.hardware.get('thermal')
    gated = thermal is not None
    thermal = thermal or {'policy': {}, 'intervals': []}
    rows = normalize_journal(journal)
    decision_rows = normalize_journal(gate_journal) if gate_journal is not None else rows
    policy = thermal['policy']
    keys = temperature.keys(policy['sensors']) if gated else ()
    intervals = thermal['intervals']
    spans = [(episode.start_ns, episode.end_ns)] + [(r['start_ns'], r['end_ns']) for r in intervals if r['kind'] == 'G0']
    coverage = [_coverage(rows, a, b, keys) for a, b in spans if a < b]
    g0 = next((r for r in intervals if r['kind'] == 'G0'), None)
    releases = []
    for gate in intervals:
        if gate['outcome'] != 'released':
            continue
        samples = [r for r in decision_rows if r['monotonic_ns'] == gate.get('exit_sample_ns')]
        release = None if len(samples) != 1 else {role: samples[0]['sensors'].get(policy['sensors'][sensor])
                                                 for role, sensor in (('fast_c', 's_fast'), ('slow_c', 's_slow'))}
        same = None if release is None else release == gate['release']
        if gate['kind'] != 'G0' and same is not None:
            # Trust neither a ratcheted gate reference nor a claimed release.
            ref = g0['release'] if g0 else None
            same = (same and ref is not None and gate['reference'] == ref
                    and all(release[k] is not None and release[k] <= ref[k] + policy[d]
                            for k, d in (('fast_c', 'delta_fast_c'), ('slow_c', 'delta_slow_c'))))
        nearest = min(rows, key=lambda r: abs(r['monotonic_ns']-gate['exit_sample_ns'])) if rows and gate.get('exit_sample_ns') is not None else None
        crosscheck = ({'sample_ns': nearest['monotonic_ns'], 'sensors': nearest['sensors']}
                      if nearest is not None and abs(nearest['monotonic_ns']-gate['exit_sample_ns']) <= 2*NS else None)
        releases.append({'kind': gate['kind'], 'journal_verified': same, 'release': release,
                         'temperature_crosscheck': crosscheck})
    custody_invalid = False
    try:
        attributed = attribute_episode(episode, source=source, channel=channel)
    except ValueError:
        # A corrupt custody interval excludes this member, not the whole desk.
        from dataclasses import replace
        custody_invalid = True
        attributed = attribute_episode(replace(
            episode, hardware={**episode.hardware, 'thermal': {**thermal, 'intervals': []}}
        ), source=source, channel=channel)
    owned = sum(s.energy.joules for s in attributed.segments if s.turn is not None)
    owned_half = sum(s.energy.half_width_j for s in attributed.segments if s.turn is not None)
    gross_half = attributed.total.half_width_j
    energy_flags = list(attributed.flags)
    if not all(math.isfinite(v) for v in (owned_half, gross_half)):
        energy_flags.append('energy.nonfinite_half_width')
    clocks, turn_observation = [], []
    all_clock_weights = []
    for turn in episode.turns:
        observation_end = max([turn.end_ns, *(c.end_ns for c in turn.tool_calls)])
        levels = [v for t, v in os_readings if turn.start_ns <= t <= observation_end]
        if not levels:
            before = [(t, v) for t, v in os_readings if t <= turn.start_ns]
            after = [(t, v) for t, v in os_readings if t >= observation_end]
            if before and after:
                levels = [max(before)[1], min(after)[1]]
        samples = [r for r in pm_samples if r['start_ns'] < observation_end and r['end_ns'] > turn.start_ns]
        supports = sorted((max(turn.start_ns, r['start_ns']), min(turn.end_ns, r['end_ns'])) for r in samples)
        cursor, gap = turn.start_ns, 0
        for a, b in supports:
            gap = max(gap, a-cursor)
            cursor = max(cursor, b)
        gap = max(gap, turn.end_ns-cursor)
        weights = []
        for r in samples:
            # Decode-owned clock excludes holds and prefill, weighted by activity.
            duration = sum(max(0, min(s.end_ns, r['end_ns']) - max(s.start_ns, r['start_ns']))
                           for s in attributed.segments if s.turn == turn.index and s.kind == 'decode')
            weight = r.get('active_ns', 0) * duration / (r['end_ns']-r['start_ns'])
            if r.get('clock_mhz') is not None:
                weights.append((weight, r['clock_mhz']))
        clocks.append(sum(w*c for w, c in weights)/sum(w for w, _ in weights) if sum(w for w, _ in weights) else None)
        all_clock_weights.extend(weights)
        os_nominal = (False if any(type(v) is int and v > 0 for v in levels) else
                      True if levels and all(type(v) is int and v == 0 for v in levels) else None)
        pm_nominal = (False if any(r.get('state') not in (None, 'Unknown', 'Nominal') for r in samples) else
                      True if samples and all(r.get('state') == 'Nominal' for r in samples) else None)
        turn_observation.append({'os_nominal': os_nominal, 'pm_nominal': pm_nominal,
                                 'pm_max_gap_s': gap/NS})
    token_ids = [{k: r.get('generation', {}).get(k) for k in ('prompt_token_ids', 'output_token_ids')} for r in turn_rows]
    exact_tokens = token_ids if len(token_ids) == len(episode.turns) and all(
        all(ids is not None for ids in row.values()) for row in token_ids) else None
    pm_gap = 0
    for a, b in spans:
        cursor = a
        for sample in sorted(pm_samples, key=lambda s: s['start_ns']):
            left, right = max(a, sample['start_ns']), min(b, sample['end_ns'])
            if left < right:
                pm_gap = max(pm_gap, left-cursor)
                cursor = max(cursor, right)
        pm_gap = max(pm_gap, b-cursor)
    traces = [t for t in episode.power_traces if t.source == source and t.channel == channel]
    trace_domain = traces[0].clock_domain if traces else None
    mappings = [m for m in episode.clock_mappings if m.trace_domain == trace_domain and m.episode_domain == episode.clock_domain]
    offset = 0 if trace_domain == episode.clock_domain else mappings[0].offset_ns if len(mappings) == 1 else None
    per_turn = []
    for turn, clock in zip(episode.turns, clocks):
        prior = [r for r in rows if 0 <= turn.start_ns-r['monotonic_ns'] <= 2*NS]
        per_turn.append({'turn': turn.index, 'decode_clock_mhz': clock,
                         'owned_j': sum(s.energy.joules for s in attributed.segments if s.turn == turn.index),
                         'slow_c': prior[-1]['sensors'].get(policy['sensors']['s_slow']) if prior and gated else None})
    return {'id': episode.episode_id, 'gated': gated, 'model': episode.agent_model,
            'pair': episode.task_pair, 'condition': episode.condition, 'start_ns': episode.start_ns,
            'flags': list(dict.fromkeys([*episode.flags, *thermal.get('flags', []),
                                        *(['thermal.custody_invalid'] if custody_invalid else [])])),
            'registered_os_nonzero': any(type(v) is int and v > 0 for _, v in (registered_os_readings or ())),
            'registered_os_observed': registered_os_readings is not None and any(type(v) is int and v >= 0 for _, v in registered_os_readings),
            'coverage': coverage, 'turn_observation': turn_observation, 'pm_period_s': pm_period_s,
            'pm_max_gap_s': pm_gap/NS,
            'turn_admissions': len(episode.turns) + sum(r['kind'] == 'G1' and r['outcome'] in ('timeout', 'deadman') for r in intervals),
            'intervals': intervals, 'releases': releases, 'g0_slow_c': g0['release']['slow_c'] if g0 else None,
            'tokens': exact_tokens, 'decode_clocks_mhz': clocks, 'turn_owned_j': owned,
            'turn_owned_half_width_j': owned_half if math.isfinite(owned_half) else None,
            'gross_episode_half_width_j': gross_half if math.isfinite(gross_half) else None,
            'per_turn': per_turn,
            'decode_clock_mhz': (sum(w*c for w, c in all_clock_weights)/sum(w for w, _ in all_clock_weights)
                                 if sum(w for w, _ in all_clock_weights) else None),
            'gross_episode_j': attributed.total.joules, 'gross_latency_s': (episode.end_ns-episode.start_ns)/NS,
            'exclusion_intervals': [{'kind': r['kind'], 'start_ns': r['start_ns'], 'end_ns': r['end_ns'],
                                     'entry_stamp': r['entry_stamp'], 'exit_stamp': r['exit_stamp']}
                                    | {'meter_clock_domain': trace_domain,
                                       'meter_start_ns': r['start_ns']-offset if offset is not None else None,
                                       'meter_end_ns': r['end_ns']-offset if offset is not None else None,
                                       'mapping_uncertainty_ns': mappings[0].uncertainty_ns if len(mappings) == 1 else 0 if offset == 0 else None}
                                    for r in intervals],
            'energy_flags': energy_flags}


def energy_exclusions(member):
    reasons = [f for f in member.get('energy_flags', ()) if f.startswith((
        'trace.missing', 'trace.ambiguous', 'clock.', 'clock_anchor_unresolved',
        'duty.uncovered', 'energy.'))]
    for key in ('turn_owned_half_width_j', 'gross_episode_half_width_j'):
        value = member.get(key)
        if type(value) not in (int, float) or not math.isfinite(value):
            reasons.append('energy.uncertainty_unavailable')
    if type(member.get('turn_owned_j')) not in (int, float) or not math.isfinite(member['turn_owned_j']):
        reasons.append('energy.value_unavailable')
    return sorted(set(reasons))


def identical_pair(a, b):
    if any(energy_exclusions(r) for r in (a, b)):
        return {'status': 'inconclusive', 'reason': 'energy evidence unavailable'}
    if a.get('tokens') is None or b.get('tokens') is None:
        return {'status': 'inconclusive', 'token_identical': None, 'reason': 'token identity unavailable'}
    identity = a.get('tokens') is not None and a['tokens'] == b.get('tokens')
    if not identity:
        return {'status': 'excluded', 'exclusion': 'X5', 'token_identical': False}
    energy = (a['turn_owned_j'] + b['turn_owned_j'])/2
    delta = b['turn_owned_j']-a['turn_owned_j']
    ca, cb = a.get('decode_clocks_mhz', []), b.get('decode_clocks_mhz', [])
    differences = [abs(y-x)/((x+y)/2) for x, y in zip(ca, cb) if x is not None and y is not None and x+y > 0]
    ac, bc = a.get('decode_clock_mhz'), b.get('decode_clock_mhz')
    difference = abs(bc-ac)/((ac+bc)/2) if ac is not None and bc is not None and ac+bc > 0 else None
    clock_status = ('pass' if difference <= .005 else 'fail') if difference is not None else 'inconclusive'
    margin = 3*max(2.97, .0011*energy)
    return {'status': combine(['pass' if abs(delta) <= margin else 'fail', clock_status]),
            'token_identical': True, 'delta_j': delta, 'margin_j': margin,
            'decode_clock_difference_fraction': difference,
            'max_decode_clock_difference_fraction': max(differences) if differences else None}


def deciding_experiment(runs):
    """Exactly 2 runs/template/arm; OLS template + arm S + start-hour drift."""
    result = {'verdict': 'INCONCLUSIVE', 'branch': 'G1 stays for every cell',
              'rule': ('FINAL-DESIGN §2.5: T CONFIRMED iff |d_X| and |d_Y| >= 10 J, same sign, '
                       'and the 90% t CI of delta excludes 0 (df=4). T REJECTED iff both '
                       '|d| <= 6 J and that CI is contained in [-6,+6] J. Otherwise INCONCLUSIVE, '
                       'including fewer than 2 eligible token-identical runs per template/arm. '
                       'Heavy cells always keep G1 and holds')}
    cells = {(t, a): [r for r in runs if r.get('template') == t and r.get('arm') == a
                     and r.get('pilot7_token_identical') is True and not r.get('excluded', False)
                     and not calibration_exclusions(r)]
             for t in ('X', 'Y') for a in ('S', 'G')}
    if any(len(c) != 2 for c in cells.values()):
        return {**result, 'reason': 'requires 2 token-identical eligible runs in each template/arm'}
    selected = [r for cell in cells.values() for r in cell]
    if len({r['id'] for r in selected}) != 8:
        return {**result, 'reason': 'duplicate contrast members'}
    for template in ('X', 'Y'):
        trajectory = cells[template, 'G'][0].get('tokens')
        if trajectory is None or any(r.get('tokens') != trajectory for arm in ('G', 'S') for r in cells[template, arm]):
            return {**result, 'reason': 'within-template token identity unavailable or divergent'}
    t0 = min(r['start_ns'] for r in selected)
    x = [[1., float(r['template'] == 'Y'), float(r['arm'] == 'S'), (r['start_ns']-t0)/(3600*NS)] for r in selected]
    fit = regression(x, [r['turn_owned_j'] for r in selected])
    d = {t: fmean(r['turn_owned_j'] for r in cells[t, 'S'])-fmean(r['turn_owned_j'] for r in cells[t, 'G']) for t in ('X', 'Y')}
    if fit is None:
        return {**result, 'd_template_j': d, 'reason': 'singular contrast design'}
    delta, ci = fit['coef'][2], fit['ci90'][2]
    if all(abs(v) >= 10 for v in d.values()) and d['X']*d['Y'] > 0 and (ci[0] > 0 or ci[1] < 0):
        result['verdict'] = 'T CONFIRMED'
    elif all(abs(v) <= 6 for v in d.values()) and ci[0] >= -6 and ci[1] <= 6:
        result.update(verdict='T REJECTED', branch='light cells use G0 only; heavy cells keep G1 and holds')
    result.update(d_template_j=d, arm_effect_j=delta, ci90_j=ci, df=fit['df'],
                  same_arm_pairs={f'{t}-{a}': identical_pair(*cell) for (t, a), cell in cells.items()})
    # Token-level identity is a required input from --compare-session. Optional
    # turn tables retain clock and temperature deltas without deciding on them.
    result['turn_tables'] = []
    for template in ('X', 'Y'):
        count = max((len(r.get('per_turn', [])) for arm in ('S', 'G') for r in cells[template, arm]), default=0)
        for turn in range(count):
            row = {'template': template, 'turn': turn}
            for field in ('owned_j', 'decode_clock_mhz', 'slow_c'):
                values = {arm: [r.get('per_turn', [])[turn].get(field) if turn < len(r.get('per_turn', [])) else None
                                for r in cells[template, arm]] for arm in ('S', 'G')}
                row['delta_'+field] = (fmean(values['S'])-fmean(values['G'])
                                       if all(v is not None for group in values.values() for v in group) else None)
            result['turn_tables'].append(row)
    return result


def _anchor_moments(anchor_sessions):
    if anchor_sessions is None:
        return {'status': 'inconclusive', 'reason': 'requires K >= 3 anchor sessions'}
    if len(anchor_sessions) < 3 or any(len(r) != 4 for r in anchor_sessions.values()):
        return {'status': 'inconclusive', 'reason': 'requires K >= 3 anchor sessions'}
    cells = list(next(iter(anchor_sessions.values())))
    if any(set(r) != set(cells) for r in anchor_sessions.values()):
        return {'status': 'inconclusive', 'reason': 'requires same four anchors in every session'}
    matrix = [[r[c] for c in cells] for r in anchor_sessions.values()]
    means = [fmean(row) for row in matrix]
    cell_means = [fmean(col) for col in zip(*matrix)]
    grand = fmean(means)
    k, j = len(matrix), len(cells)
    ms_window = j*sum((v-grand)**2 for v in means)/(k-1)
    ms_error = sum((v-means[w]-cell_means[c]+grand)**2 for w, row in enumerate(matrix)
                   for c, v in enumerate(row))/((k-1)*(j-1))
    sigma = math.sqrt(max(0, (ms_window-ms_error)/j))
    return {'status': 'pass' if sigma <= 6 else 'fail', 'anchor_sigma_j': sigma, 'K': k,
            'ms_window_j2': ms_window, 'ms_error_j2': ms_error, 'method': 'balanced crossed-anchor moment'}


def _sentinel_equivalence(windows, reference_j):
    if len(windows) < 3 or not reference_j or any(not runs for runs in windows.values()):
        return {'status': 'inconclusive', 'reason': 'requires >= 3 windows and W1 sentinel reference'}
    means = [fmean((v-reference_j)/reference_j for v in runs) for runs in windows.values()]
    mean = fmean(means)
    ci = interval(mean, stdev(means)/math.sqrt(len(means)), len(means)-1)
    return {'status': 'fail' if abs(mean) > .0025 else bounded(mean, ci, .005),
            'mean_fraction': mean, 'ci90_fraction': ci, 'df': len(means)-1, 'window_means': means}


def _combined_u4(value):
    if not value or not all(isinstance(value.get(k), dict) and value[k].get('status') in
                            ('pass', 'fail', 'inconclusive') for k in ('anchors', 'sentinels')):
        return {'status': 'inconclusive', 'reason': 'U4 requires both sentinel equivalence and anchor moments'}
    return {**value, 'status': combine([value[k]['status'] for k in ('anchors', 'sentinels')])}


def cross_window(windows, reference_j, *, anchor_sessions=None):
    """U4 is conjunctive: sentinel equivalence AND the 30B anchor moment bar."""
    return _combined_u4({'anchors': _anchor_moments(anchor_sessions),
                         'sentinels': _sentinel_equivalence(windows, reference_j)})


def session_desk_evidence(pilot_paths, *, adapter=None):
    """Read desk-only U4--U6 evidence from K ``PILOT.json`` files.

    ``adapter`` is the deliberately narrow seam for the off-repository
    ``k_sessions.py`` reader.  It receives the decoded PILOT objects and must
    return the same mapping as the portable ``v4_desk_evidence`` object used
    by fixtures: ``anchors``, ``sentinels``, ``u5`` and ``u6``.  No path from
    a PILOT file is followed here.
    """
    paths = [Path(p) for p in pilot_paths]
    pilots = [json.loads(p.read_text()) for p in paths]
    if adapter is not None:
        evidence = adapter(pilots)
    else:
        parts = [p.get('v4_desk_evidence') for p in pilots]
        if not parts or any(not isinstance(p, dict) for p in parts):
            return {'status': 'inconclusive', 'reason':
                    'PILOT lacks v4_desk_evidence; connect off-repo k_sessions.py at adapter'}
        anchors, sentinels = {}, {}
        u5, u6, u5_inputs, u6_inputs = {}, {}, {}, {}
        reference = None
        for i, part in enumerate(parts):
            session = str(part.get('session_id', pilots[i].get('session_id', paths[i].stem)))
            if isinstance(part.get('anchors'), dict):
                anchors[session] = part['anchors']
            if isinstance(part.get('sentinel_energies_j'), dict):
                for model, values in part['sentinel_energies_j'].items():
                    sentinels.setdefault(model, {})[session] = values
            reference = part.get('sentinel_reference_j', reference)
            if isinstance(part.get('u5'), dict):
                u5.update(part['u5'])
            if isinstance(part.get('u6'), dict):
                u6.update(part['u6'])
            if isinstance(part.get('u5_inputs'), dict):
                u5_inputs.update(part['u5_inputs'])
            if isinstance(part.get('u6_inputs'), dict):
                for model, raw in part['u6_inputs'].items():
                    target = u6_inputs.setdefault(model, {k: v for k, v in raw.items() if k != 'benign'})
                    target.setdefault('benign', []).extend(raw.get('benign', []))
        for model, raw in u5_inputs.items():
            u5[model] = state_sensitivity(**raw)
        for model, raw in u6_inputs.items():
            u6[model] = monitoring_stability(**raw)
        evidence = {'anchors': anchors, 'sentinels': sentinels,
                    'sentinel_reference_j': reference, 'u5': u5, 'u6': u6}
    if not isinstance(evidence, dict):
        return {'status': 'inconclusive', 'reason': 'K-session adapter returned no evidence'}
    anchors = evidence.get('anchors')
    models = set(evidence.get('sentinels', {})) | set(evidence.get('u5', {})) | set(evidence.get('u6', {}))
    cross = {model: cross_window(evidence.get('sentinels', {}).get(model, {}),
                                 evidence.get('sentinel_reference_j'), anchor_sessions=anchors)
             for model in models}
    return {'status': 'pass', 'K': len(pilots), 'cross_windows': cross,
            'sensitivity': evidence.get('u5', {}), 'monitoring': evidence.get('u6', {}),
            'adapter': 'external' if adapter is not None else 'portable-v4_desk_evidence'}


def state_sensitivity(*, heavy, smaller_pair_sr_j, mean_energy_j, mean_30b_energy_j=None,
                      contrast=None, pairs=(), release_range_c=None):
    margin = .1 * smaller_pair_sr_j if smaller_pair_sr_j is not None else None
    point = upper = None
    details = {}
    if not heavy and contrast and contrast.get('ci90_j') is not None and mean_30b_energy_j:
        ratio = mean_energy_j/mean_30b_energy_j
        point = abs(contrast['arm_effect_j'])*ratio
        upper = max(abs(v) for v in contrast['ci90_j'])*ratio
        details = {'source': 'scaled W1 contrast', 'energy_ratio': ratio}
    elif heavy and release_range_c is not None:
        observed = [(b['g0_slow_c']-a['g0_slow_c'], b['turn_owned_j']-a['turn_owned_j']) for a, b in pairs
                    if a.get('g0_slow_c') is not None and b.get('g0_slow_c') is not None
                    and not calibration_exclusions(a) and not calibration_exclusions(b)
                    and a.get('tokens') is not None and a['tokens'] == b.get('tokens')]
        fit = regression([[dt] for dt, _ in observed], [de for _, de in observed])
        if fit is not None:
            beta, ci = fit['coef'][0], fit['ci90'][0]
            point, upper = abs(beta)*release_range_c, max(abs(v) for v in ci)*release_range_c
            details = {'source': 'model identical-work pair differences through origin', 'beta_j_per_c': beta,
                       'beta_ci90': ci, 'n_pairs': len(observed), 'release_range_c': release_range_c}
    status = ('inconclusive' if point is None or margin is None else 'fail' if point > margin else
              'pass' if upper <= margin else 'inconclusive')
    return {'status': status, 'point_shift_j': point, 'upper90_shift_j': upper, 'margin_j': margin, **details}


def _correlation(x, y):
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 2:
        return None
    xm, ym = (fmean(c) for c in zip(*pairs))
    xx = sum((a-xm)**2 for a, _ in pairs)
    yy = sum((b-ym)**2 for _, b in pairs)
    return sum((a-xm)*(b-ym) for a, b in pairs)/math.sqrt(xx*yy) if xx*yy else None


def monitoring_stability(benign, *, mean_turn_j, mean_30b_turn_j, mean_episode_j, split_rule=None):
    """Frozen-fit residual records; no temperature/clock term is fitted.

    Each record has pair, start_ns, residual_j (per-turn list), and optionally
    release_slow_c/mean_clock_mhz. Early/late means halves of chronological
    benign episodes within each pair; pair contrasts are pooled equally.
    Protocol v4 must freeze that split/unit convention before any desk is read.
    """
    if split_rule != 'within_pair_episode_order':
        return {'status': 'inconclusive', 'reason': 'protocol v4 must freeze the early/late split convention'}
    groups = defaultdict(list)
    for r in benign:
        groups[r['pair']].append(r)
    if len(groups) != 2 or any(len(g) < 6 for g in groups.values()):
        return {'status': 'inconclusive', 'reason': 'requires m >= 6 benign per model x pair'}
    x, y = [], []
    for r in benign:
        for k, residual in enumerate(r['residual_j']):
            x.append([1., k])
            y.append(residual)
    fit = regression(x, y)
    changes, variances, dfs = [], [], []
    for group in groups.values():
        ordered = sorted(group, key=lambda r: r['start_ns'])
        middle = len(ordered)//2
        early = [sum(r['residual_j']) for r in ordered[:middle]]
        late = [sum(r['residual_j']) for r in ordered[middle:]]
        v1, v2 = stdev(early)**2/len(early), stdev(late)**2/len(late)
        changes.append(fmean(late)-fmean(early))
        variances.append(v1+v2)
        dfs.append((v1+v2)**2/(v1*v1/(len(early)-1)+v2*v2/(len(late)-1)) if v1+v2 else len(group)-2)
    change = fmean(changes)
    variance = sum(variances)/len(groups)**2
    df = sum(variances)**2/sum(v*v/d for v, d in zip(variances, dfs)) if sum(variances) else sum(dfs)
    ci = interval(change, math.sqrt(variance), df)
    slope_status = bounded(fit['coef'][1], fit['ci90'][1], mean_turn_j/mean_30b_turn_j) if fit else 'inconclusive'
    return {'status': combine([slope_status, bounded(change, ci, .0037*mean_episode_j)]),
            'slope_j_per_turn': fit['coef'][1] if fit else None, 'slope_ci90': fit['ci90'][1] if fit else None,
            'slope_margin_j_per_turn': mean_turn_j/mean_30b_turn_j,
            'early_late_change_j': change, 'early_late_ci90': ci, 'early_late_margin_j': .0037*mean_episode_j,
            'corr_residual_release_slow': _correlation([sum(r['residual_j']) for r in benign], [r.get('release_slow_c') for r in benign]),
            'corr_residual_clock': _correlation([sum(r['residual_j']) for r in benign], [r.get('mean_clock_mhz') for r in benign])}


def collector_lost(member):
    """The 1 Hz sidecar died (WP8 F2 fail-fast): X4, state unobserved."""
    return any('thermal.collector_thread_dead' in f or 'thermal.collector_failed' in f
               or f.startswith('collector_error:') for f in member.get('flags', ()))


def state_unobserved(member):
    return 'thermal.state_unobserved' in member.get('flags', ()) or collector_lost(member)


def thermal_exclusions(member):
    """X1–X4 only: value checks omit these; U1(b/d) still count them."""
    reasons = [f for f in member.get('flags', ()) if f.startswith((
        'thermal.os_level_nonzero', 'thermal.powermetrics_non_nominal',
        'thermal.start_gate_timeout', 'thermal.gate_timeout:',
        'thermal.hold_timeout:', 'thermal.state_unobserved'))]
    if collector_lost(member):
        # A member failed fast on a dead collector is X4 for U1(b), as in
        # calibration_exclusions.
        reasons.append('thermal.state_unobserved')
    if member.get('registered_os_nonzero') or any(t.get('os_nominal') is False for t in member.get('turn_observation', ())):
        reasons.append('thermal.os_level_nonzero')
    if any(t.get('pm_nominal') is False for t in member.get('turn_observation', ())):
        reasons.append('thermal.powermetrics_non_nominal')
    return sorted(set(reasons))


def acceptance(members, *, pairs=(), u4=None, u5=None, u6=None):
    """One model/window; only included members supply U1(a)/U2 values."""
    model_ids = {r.get('model') for r in members if r.get('gated')}
    if len(model_ids) > 1:
        raise ValueError('acceptance is per model per window')
    gated = [r for r in members if r.get('gated')]
    observed = [r for r in gated if not state_unobserved(r)]
    included = [r for r in gated if not thermal_exclusions(r)]
    excluded = len(gated) - len(included)
    turns = [t for r in included for t in r['turn_observation']]
    checks = []
    checks.append('pass' if excluded <= 1 else 'fail')
    checks.append('pass' if included and all(r.get('registered_os_observed') is True for r in included) else 'inconclusive')
    checks.extend('inconclusive' if t[k] is None else 'pass' if t[k] else 'fail'
                  for t in turns for k in ('os_nominal', 'pm_nominal'))
    checks.extend('pass' if c['sample_fraction'] is not None and c['sample_fraction'] >= .99
                  and c.get('max_interval_ns') is not None and c['max_interval_ns'] <= 2*NS else 'fail'
                  for r in observed for c in r['coverage'])
    checks.extend('pass' if t['pm_max_gap_s'] <= max(1, 5*r['pm_period_s']) else 'fail'
                  for r in observed for t in r['turn_observation'])
    checks.extend('pass' if r.get('pm_max_gap_s', 0) <= max(1, 5*r['pm_period_s']) else 'fail' for r in observed)
    admissions = sum(r['turn_admissions'] for r in observed)
    timeouts = sum(i['kind'] in ('G1', 'H') and i['outcome'] == 'timeout' for r in observed for i in r['intervals'])
    g0_timeouts = sum(i['kind'] == 'G0' and i['outcome'] == 'timeout' for r in observed for i in r['intervals'])
    checks.append('pass' if g0_timeouts <= 1 else 'fail')
    checks.append('pass' if admissions and timeouts/admissions <= .02 else 'fail' if admissions else 'inconclusive')
    if not turns or not observed:
        checks.append('inconclusive')
    slow = [r['g0_slow_c'] for r in included if r.get('g0_slow_c') is not None]
    range_c = max(slow)-min(slow) if slow else None
    release_checks = [v['journal_verified'] for r in included for v in r['releases']]
    u2 = combine(['pass' if range_c is not None and range_c <= 3 else 'fail' if range_c is not None else 'inconclusive',
                  combine(['inconclusive' if v is None else 'pass' if v else 'fail' for v in release_checks])
                  if release_checks else 'inconclusive'])
    pair_results = [identical_pair(a, b) for a, b in pairs
                    if not state_unobserved(a) and not state_unobserved(b)]
    eligible_pairs = [p['status'] for p in pair_results if p['status'] != 'excluded']
    results = {'U1': {'status': combine(checks), 'thermal_excluded_members': excluded,
                      'turn_admissions': admissions, 'g1_h_timeouts': timeouts, 'g0_timeouts': g0_timeouts},
               'U2': {'status': u2, 'g0_slow_range_c': range_c},
               'U3': {'status': combine(eligible_pairs) if eligible_pairs else 'inconclusive', 'pairs': pair_results},
               'U4': _combined_u4(u4),
               'U5': u5 or {'status': 'inconclusive', 'reason': 'requires pair s_r and state sensitivity evidence'},
               'U6': u6 or {'status': 'inconclusive', 'reason': 'requires frozen-fit benign residuals'}}
    hardware = combine([results[f'U{k}']['status'] for k in range(1, 6)])
    results['hardware_control'] = hardware
    results['monitoring_calibration'] = results['U6']['status']
    results['consequence'] = ('thermal protocol not met' if any(results[f'U{k}']['status'] == 'fail' for k in (1, 2, 3)) else
                             'state not controlled; calibration unresolved' if any(results[f'U{k}']['status'] == 'fail' for k in (4, 5)) else
                             'calibration unresolved' if results['U6']['status'] == 'fail' else
                             'add 2 sentinels per remaining window' if any(results[f'U{k}']['status'] == 'inconclusive' for k in (4, 5)) else
                             'under control' if hardware == 'pass' else 'inconclusive')
    return results


def calibration_exclusions(member):
    reasons = [f for f in member.get('flags', ()) if f.startswith((
        'thermal.start_gate_timeout', 'thermal.gate_timeout:', 'thermal.hold_timeout:',
        'thermal.state_unobserved', 'thermal.custody_invalid', 'episode.deadman:',
        'episode.malformed_tool_call:'))]
    if member.get('registered_os_nonzero'):
        reasons.append('thermal.os_level_nonzero')
    if any(t.get('pm_nominal') is False for t in member.get('turn_observation', ())):
        reasons.append('thermal.powermetrics_non_nominal')
    if any(f.startswith(('endpoint_error:', 'episode_error:')) for f in member.get('flags', ())):
        reasons.append('member.runtime_failure')
    if collector_lost(member):
        # Collector loss is the protocol's X4 state-observation exclusion even
        # when the runtime also (correctly) fails the member.
        reasons.append('thermal.state_unobserved')
    reasons.extend(energy_exclusions(member))
    return sorted(set(reasons))


def read_bundle_record(bundle, *, os_journal=(), temperature_journal=None, registered_span_ns=None):
    """Read existing immutable bundle artifacts and anchored native PM records.

    Accept hazard-journal rows from the desk caller, or use the member-local
    sidecar. No config model/cache/data path is followed and no bundle is written.
    """
    import json
    from pathlib import Path
    from joulewise.align.apple.workload import read_episode_bundle
    from joulewise.align.apple.sampler import seconds_ns
    from joulewise.adapters.powermetrics import parse_powermetrics_records
    from joulewise.desk_compress import read_bytes
    bundle = Path(bundle)
    ep = read_episode_bundle(bundle)
    def jsonl(path):
        try:
            return [json.loads(line) for line in read_bytes(path).splitlines() if line.strip()]
        except FileNotFoundError:
            return []
    gate_journal = jsonl(bundle/'outputs/align_thermal.jsonl')
    journal = temperature_journal if temperature_journal is not None else gate_journal
    rich = jsonl(bundle/'rich_telemetry.jsonl')
    pm = []
    trace = next((t for t in ep.power_traces if t.source == 'powermetrics' and t.channel == 'gpu_power'), None)
    mapping = next((m for m in ep.clock_mappings if trace is not None and m.trace_domain == trace.clock_domain
                    and m.episode_domain == ep.clock_domain), None)
    if rich and mapping is not None:
        raw = parse_powermetrics_records(read_bytes(bundle/'raw/powermetrics.plist'), first_record_endpoint_s=rich[0]['timestamp_s'])
        if len(raw) != len(rich):
            raise ValueError('PM native/rich record count mismatch')
        for native, detail in zip(raw, rich):
            end = seconds_ns(detail['timestamp_s']) + mapping.offset_ns
            states = (detail.get('gpu') or {}).get('dvfm_states', ())
            active = sum(s.get('used_ns', 0) for s in states)
            clock = sum(s['freq']*s.get('used_ns', 0) for s in states)/active if active else None
            pm.append({'start_ns': end-native.elapsed_ns, 'end_ns': end, 'state': native.thermal_pressure,
                       'active_ns': active, 'clock_mhz': clock})
    os_readings = [(r['finished']['monotonic_ns'], r['values'].get('level')) for r in os_journal
                   if r.get('kind') == 'reading' and not r.get('error')]
    if not os_readings:
        os_readings = [(r['monotonic_ns'], r.get('status', {}).get('os_level'))
                       for r in normalize_journal(gate_journal)
                       if r.get('status', {}).get('os_level') is not None]
    config = json.loads(read_bytes(bundle/'config.json'))
    registered = ([(t, v) for t, v in os_readings if registered_span_ns[0] <= t <= registered_span_ns[1]]
                  if registered_span_ns is not None else None)
    record = member_record(ep, journal, os_readings=os_readings, pm_samples=pm,
                           gate_journal=gate_journal,
                           pm_period_s=1/config['sampling']['power_hz'],
                           registered_os_readings=registered,
                           turn_rows=jsonl(bundle/'outputs/align_turns.jsonl'))
    record['registered_span_ns'] = registered_span_ns
    record['calibration_exclusions'] = calibration_exclusions(record)
    return record


def window_report(members, *, cross_windows=None, sensitivity=None, monitoring=None):
    """Additive PILOT.json thermal section; keep v3 desk bytes unchanged.

    Group metadata comes from the sealed v4 roster: window, identical_work_group,
    template/arm and compare_reference_id. Every repeated group yields all pairs.
    Missing comparison members remain inconclusive; no replacement/top-up occurs.
    """
    by_id = {m['id']: m for m in members}
    if len(by_id) != len(members):
        raise ValueError('duplicate member ids')
    reports = {}
    models = sorted({m.get('model') for m in members if m.get('gated')})
    for model in models:
        windows = sorted({m.get('window', 'current') for m in members if m.get('model') == model})
        for window in windows:
            selected = [m for m in members if m.get('model') == model and m.get('window', 'current') == window]
            groups = defaultdict(list)
            for m in selected:
                if m.get('identical_work_group'):
                    groups[m['identical_work_group']].append(m)
            pairs = [(a, b) for group in groups.values() for i, a in enumerate(group) for b in group[i+1:]]
            missing_pair = any(len(g) < 2 for g in groups.values())
            for m in selected:
                ref = m.get('compare_reference_id')
                if ref:
                    if ref in by_id:
                        pairs.append((by_id[ref], m))
                    else:
                        missing_pair = True
            result = acceptance(selected, pairs=pairs, u4=(cross_windows or {}).get(model),
                                u5=(sensitivity or {}).get(model), u6=(monitoring or {}).get(model))
            if window == 'W1':
                for k in (4, 5, 6):
                    result[f'U{k}'] = {'status': 'inconclusive', 'reason': 'not evaluable in W1 (FINAL-DESIGN §2.3)'}
                result['hardware_control'] = combine([result[f'U{k}']['status'] for k in range(1, 6)])
                result['monitoring_calibration'] = 'inconclusive'
            if missing_pair and result['U3']['status'] != 'fail':
                result['U3']['status'] = 'inconclusive'
                result['U3']['reason'] = 'required identical-work comparison member missing'
                result['hardware_control'] = combine([result[f'U{k}']['status'] for k in range(1, 6)])
            if result['hardware_control'] != 'pass' and result['consequence'] == 'under control':
                result['consequence'] = 'inconclusive'
            if window == 'W1' and all(result[f'U{k}']['status'] != 'fail' for k in (1, 2, 3)):
                result['consequence'] = 'U4-U6 not evaluable in W1; no control verdict'
            reports[f'{model}/{window}'] = result
    contrast_runs = [m for m in members if m.get('template') in ('X', 'Y') and m.get('arm') in ('S', 'G')]
    return {'schema': 'joulewise.align.thermal_desk.v1', 'model_windows': reports,
            'deciding_experiment': deciding_experiment(contrast_runs), 'members': members}


def markdown_report(report):
    rows = ['# ALIGN v4 thermal desk', '', '| Model/window | U1 | U2 | U3 | U4 | U5 | U6 |',
            '|---|---|---|---|---|---|---|']
    for key, result in report['model_windows'].items():
        rows.append('| '+key+' | '+' | '.join(result[f'U{k}']['status'] for k in range(1, 7))+' |')
    contrast = report['deciding_experiment']
    rows.extend(['', '| Contrast | d_X (J) | d_Y (J) | Arm effect S−G (J) | 90% interval (J) | df |',
                 '|---|---|---|---|---|---|',
                 '| '+str(contrast['verdict'])+' | '+str(contrast.get('d_template_j', {}).get('X'))+' | '+
                 str(contrast.get('d_template_j', {}).get('Y'))+' | '+str(contrast.get('arm_effect_j'))+' | '+
                 str(contrast.get('ci90_j'))+' | '+str(contrast.get('df'))+' |', '',
                 contrast['rule']+'. '+contrast['branch']+'.', '',
                 '| Member | Turn-owned GPU J | Gross episode GPU J | Gross latency s | Exclusions |',
                 '|---|---|---|---|---|'])
    for m in report['members']:
        rows.append('| '+m['id']+' | '+str(m.get('turn_owned_j'))+' | '+str(m.get('gross_episode_j'))+' | '+
                    str(m.get('gross_latency_s'))+' | '+', '.join(calibration_exclusions(m))+' |')
    rows.extend(['', '| Member | Gate | Turn | Tokens | Duration s | Release slow °C | Slope °C/min | Outcome |',
                 '|---|---|---|---|---|---|---|---|'])
    for member in report['members']:
        for gate in member.get('intervals', []):
            rows.append('| '+' | '.join(str(v) for v in (member['id'], gate['kind'], gate.get('turn'),
                gate.get('token_count'), gate.get('duration_s'), gate.get('release', {}).get('slow_c'),
                gate.get('slope_c_per_min'), gate['outcome']))+' |')
    rows.extend(['', '| Contrast template | Turn | d energy J | Δdecode MHz | Δslow °C |',
                 '|---|---|---|---|---|'])
    for turn in contrast.get('turn_tables', []):
        rows.append('| '+' | '.join(str(turn.get(k)) for k in ('template', 'turn', 'delta_owned_j',
                                                               'delta_decode_clock_mhz', 'delta_slow_c'))+' |')
    rows.extend(['', 'Exact exclusion intervals and paired clock stamps are in PILOT.json.', ''])
    return '\n'.join(rows)
