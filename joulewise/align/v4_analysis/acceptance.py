"""Registered U1-U6 and R14 battery arithmetic on materialized desk evidence.

No arm, no observation, no source discovery. Missing inputs stay inconclusive.
U3 is derived once per invocation from the frozen pre-series export, never from
the analyzed series. No decisions or refusals are cached.
"""
import math
from statistics import fmean, stdev

from joulewise.align.apple import thermal_desk as td
from joulewise.align.apple import v4_estimands as estimands


def _series_tail(q, n, tests):
    hi, steps = n+14*math.sqrt(2*n)+40, 2000
    h = hi/steps
    log_c = -(n/2)*math.log(2)-math.lgamma(n/2)
    total = 0.
    for i in range(1, steps+1):
        x = i*h
        tail = min(math.erfc(q*math.sqrt(x/n)/math.sqrt(2)), 1-1e-16)
        value = -math.expm1(tests*math.log1p(-tail))
        total += (1 if i == steps else 4 if i%2 else 2)*math.exp(
            log_c+(n/2-1)*math.log(x)-x/2)*value
    return total*h/3


def u3_derivation(evidence):
    if not evidence:
        return {'status': 'inconclusive', 'reason': 'frozen U3 evidence missing'}
    pairs = evidence['pilot_pairs']
    sessions, r = set(), []
    for p in pairs:
        if (p['session'] in sessions or p.get('prespecified') is not True
                or p.get('token_identical') is not True or p['ordinals'][1]-p['ordinals'][0] < 3
                or len(p['energies_j']) != 2 or any(type(v) not in (int, float)
                    or not math.isfinite(v) or v <= 0 for v in p['energies_j'])):
            raise ValueError('U3 needs one prespecified separated identical pair per pilot session')
        sessions.add(p['session'])
        a, b = p['energies_j']
        r.append((b-a)/fmean([a, b]))
    if len(r) < 5:
        raise ValueError('U3 requires at least five pilot sessions')
    s0 = math.sqrt(math.fsum(v*v for v in r)/len(r))
    if s0 <= 0:
        return {'status': 'inconclusive', 'reason': 'U3 scale is zero'}
    heavy = any(abs(v)/s0 > 3 for v in r)
    beta = .025 if heavy else .05
    lo, hi = 0., 200.
    for _ in range(64):
        mid = (lo+hi)/2
        lo, hi = (mid, hi) if _series_tail(mid, len(r), 16) > beta else (lo, mid)
    bar = hi*s0
    screen = evidence.get('r1_d_screen')
    screen_pass = bool(screen and screen.get('token_identical') is True
                       and screen.get('eligible') is True
                       and abs(screen['relative_difference']) <= 1.5*bar)
    return dict(status='available', n=len(r), rms_relative=s0, q=hi, beta=beta,
                comparisons=16, d_transfer_factor=1.5, heavy_tail_rule_applied=heavy,
                heavy_tail_rule='RUN_STATE 226: abs(r)/s0 > 3',
                relative_bar_30B=bar, relative_bar_D=1.5*bar,
                d_screen='not_refuted' if screen_pass else 'missing_or_refuted',
                qualified=evidence.get('frozen_before_W1') is True,
                limitation='zero-mean normal model; D transfer and dependence remain assumptions')


def u3_pair(a, b, derivation, population):
    if any(td.calibration_exclusions(m) or m.get('status') != 'completed'
           or set((m.get('battery') or {}).get('flags', [])) &
              {'battery.member_span', 'battery.accumulator_excursion'} for m in (a, b)):
        return dict(status='inconclusive', reason='ineligible replay member')
    if a.get('tokens') is None or b.get('tokens') is None:
        return dict(status='inconclusive', reason='identity missing')
    if a['tokens'] != b['tokens']:
        return dict(status='excluded', reason='X5', token_identical=False)
    if a.get('identity_evidence') is None or b.get('identity_evidence') is None:
        return dict(status='inconclusive', reason='transcript/cache/seed identity unavailable')
    if a['identity_evidence'] != b['identity_evidence']:
        return dict(status='excluded', reason='X5', token_identical=False)
    values = [m.get('turn_owned_j') for m in (a, b)]
    if any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in values):
        return dict(status='inconclusive', reason='replay energy unavailable')
    if (derivation['status'] != 'available' or not derivation['qualified']
            or population == 'D' and derivation['d_screen'] != 'not_refuted'):
        return dict(status='inconclusive', reason='U3 frozen derivation or D screen unavailable')
    clocks = [m.get('decode_clock_mhz') for m in (a, b)]
    clock = (abs(clocks[1]-clocks[0])/fmean(clocks) if all(
        type(v) in (int, float) and math.isfinite(v) and v > 0 for v in clocks) else None)
    relative = (values[1]-values[0])/fmean(values)
    bar = derivation['relative_bar_'+population]
    status = 'fail' if abs(relative) > bar or clock is not None and clock > .005 else (
        'pass' if clock is not None else 'inconclusive')
    return dict(status=status, relative_difference=relative, margin_relative=bar,
                margin_j=bar*fmean(values), delta_j=values[1]-values[0],
                active_clock_difference_fraction=clock, token_identical=True)


def window_checks(members, derivation):
    result = {}
    for model in sorted({m['slot']['model_id'] for m in members}):
        rows = [m['thermal'] for m in members if m['slot']['model_id'] == model]
        # Replays are explicitly tagged; no search for an outcome-favorable pair.
        groups = {}
        for m in rows:
            if m.get('identical_work_group'):
                groups.setdefault(m['identical_work_group'], []).append(m)
        pairs = [u3_pair(v[0], v[1], derivation, 'D' if model == 'qwen3.8-27b' else '30B')
                 if len(v) == 2 else dict(status='inconclusive', reason='replay cardinality')
                 for v in groups.values()]
        # Anchors in C/T are bridge diagnostics, not extra U3 tests (N=16).
        check = td.acceptance(rows, v4=True)
        check['U3'] = dict(status=td.combine([p['status'] for p in pairs if p['status'] != 'excluded'])
                          if any(p['status'] != 'excluded' for p in pairs) else 'inconclusive', pairs=pairs)
        result[model] = {k: check[k] for k in ('U1', 'U2', 'U3')}
    return result


def battery(members):
    charge = missing = assist = 0
    for m in members:
        b = m['thermal'].get('battery') or {}
        flags = set(b.get('flags', [])) | set(m['thermal'].get('flags', []))
        charge += bool(flags & {'battery.member_span', 'battery.accumulator_excursion'})
        missing += b.get('status') != 'observed'
        assist += 'battery.assist' in flags
    return dict(status='fail' if charge else 'inconclusive' if missing else 'pass',
                charging_members=charge, unobserved_members=missing, assist_members=assist,
                next_action='fresh_topup_and_obc' if charge else 'none', assist='disclosure_only',
                members=[dict(run_id=m['slot']['run_id'],
                    soc_pct=(m['thermal'].get('battery') or {}).get('soc_pct'),
                    charger_w=(m['thermal'].get('battery') or {}).get('charger_w'),
                    flags=(m['thermal'].get('battery') or {}).get('flags', [])) for m in members])


def anchor_diagnostic(windows):
    sessions = {}
    for w in windows:
        anchors = [m for m in w['members'] if m['slot']['series_role'] == 'anchor']
        if len(anchors) == 4 and all(m['eligible'] for m in anchors):
            sessions[w['window']] = {str(m['slot']['ordinal']): m['thermal']['turn_owned_j'] for m in anchors}
    result = td._anchor_moments(sessions)
    # The historical helper has a 6J veto; v4 expressly demotes it to print-only.
    result.pop('status')
    return dict(status='print_only', **result)


def u4(reference, windows):
    if (not reference or reference.get('qualified') is not True
            or len(reference.get('r1_replay_j', [])) != 2
            or set(reference.get('w1_sentinel_j', {})) != {'5', '17'}):
        return dict(status='inconclusive', reason='qualified R1 pair and W1 5/17 required')
    ref = fmean([*reference['r1_replay_j'], *reference['w1_sentinel_j'].values()])
    if not ref > 0:
        return dict(status='inconclusive', reason='positive E_ref required')
    values = {'W1': list(reference['w1_sentinel_j'].values())}
    for window in windows:
        sentinels = [m for m in window['members'] if m['slot']['series_role'] == 'sentinel']
        if any(not m['eligible'] or m['thermal'].get('tokens') is None
               or len(m.get('summary', {}).get('residual_rows', {}).get('True', [])) < 3 for m in sentinels):
            return dict(status='inconclusive', reason='sentinel incomplete or ineligible')
        if len(sentinels) < 2 or any(m['thermal']['tokens'] != sentinels[0]['thermal']['tokens'] for m in sentinels):
            return dict(status='inconclusive', reason='sentinel identity unavailable/divergent')
        values[window['window']] = [m['thermal']['turn_owned_j'] for m in sentinels]
    result = td._sentinel_equivalence(values, ref)
    return {**result, 'E_ref_j': ref, 'window_count': len(values),
            'sigma_w_30b': {'status': 'print_only', 'reason': 'requires balanced crossed anchors'}}


def u5(evidence):
    if not evidence:
        return dict(status='inconclusive', reason='R1 three designed start states missing')
    pairs = evidence['pairs']
    if len(pairs) < 3 or any(p.get('token_identical') is not True for p in pairs):
        return dict(status='inconclusive', reason='three identical-work state pairs required')
    fit = td.regression([[p['delta_slow_c']] for p in pairs], [p['delta_j'] for p in pairs])
    if fit is None:
        return dict(status='inconclusive', reason='state sensitivity rank deficient')
    sigma = max(stdev(evidence['r1_replay_j']), 2.97)
    delta = evidence['delta_slow_c']
    point = abs(fit['coef'][0])*delta
    upper = max(map(abs, fit['ci90'][0]))*delta
    return dict(status='fail' if point > sigma else 'pass' if upper <= sigma else 'inconclusive',
                beta_T_j_per_c=fit['coef'][0], beta_T_ci90=fit['ci90'][0], c=1.,
                sigma_pair_j=sigma, delta_slow_c=delta, point_shift_j=point, upper90_shift_j=upper)


def u6(records, split_rule):
    if split_rule != 'within_pair_episode_order' or len(records) < 2:
        return dict(status='inconclusive', reason='frozen U6 split/unit missing')
    turns = [v for r in records for v in r['residual_j']]
    # The owning contract must explicitly adopt this per-turn s_r definition.
    if len(turns) < 2:
        return dict(status='inconclusive', reason='no residual degrees of freedom')
    ordered = sorted(records, key=lambda r: (r['start_ns'], r['trajectory']))
    middle = len(ordered)//2
    rows, positions = [], []
    for i, record in enumerate(ordered):
        for k, value in enumerate(record['residual_j']):
            rows.append((record['trajectory'], int(i >= middle), value))
            positions.append(dict(trajectory=record['trajectory'], turn_position=k, residual_j=value))
    early = [v for _, late, v in rows if not late]
    late = [v for _, is_late, v in rows if is_late]
    if not early or not late:
        return dict(status='inconclusive', reason='empty chronological half')
    means = fmean(early), fmean(late)
    # Identical uncorrected cluster sandwich and 1.645 bar as the v4 helper,
    # but ordered clusters make independent-process output byte deterministic.
    n0, n1 = len(early), len(late)
    inv = [[1/n0, -1/n0], [-1/n0, 1/n0+1/n1]]
    meat = [[0., 0.], [0., 0.]]
    for cluster in sorted({c for c, _, _ in rows}):
        score = [0., 0.]
        for c, is_late, value in rows:
            if c == cluster:
                error = value-means[is_late]
                score[0] += error
                score[1] += error*is_late
        for i in range(2):
            for j in range(2):
                meat[i][j] += score[i]*score[j]
    variance = sum(inv[1][i]*meat[i][j]*inv[j][1] for i in range(2) for j in range(2))
    se = math.sqrt(max(0., variance))
    effect, margin = means[1]-means[0], .5*stdev(turns)
    ci = [effect-1.645*se, effect+1.645*se]
    status = 'fail' if abs(effect) > margin else 'pass' if ci[0] >= -margin and ci[1] <= margin else 'inconclusive'
    return dict(status=status, effect_j=effect, ci90_j=ci, margin_j=margin,
                trajectory_clustered_se_j=se, se_kind='trajectory_clustered',
                imprecise=status == 'inconclusive',
                turn_position_residual_means=estimands.d_turn_position_means(positions),
                s_r_unit='per_turn_J', s_r_definition='sample SD of frozen-fit benign turn residuals',
                s_r_j=stdev(turns), split_rule=split_rule)
