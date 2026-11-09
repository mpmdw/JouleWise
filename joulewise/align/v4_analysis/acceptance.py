"""Registered U1-U6 and R14 battery arithmetic on materialized desk evidence.

No arm, no observation, no source discovery. Missing inputs stay inconclusive.
U3 is derived once per invocation from the frozen pre-series export, never from
the analyzed series. No decisions or refusals are cached.
"""
import math
from statistics import fmean, stdev

from joulewise.align.apple import thermal_desk as td
from joulewise.align.apple import v4_estimands as estimands
from . import exclusions as ex

# R25, RUN_STATE 239; e36b096fe:scripts/align_v4_u3_export.py:ROSTER.
# Budget every possible comparison, including reserves even when unarmed.
U3_SCOPES = {'W1': {'30B': 4, 'D': 1},
             **{f'C{i}': {'30B': 0, 'D': 1} for i in range(1, 15)},
             **{f'T{i}': {'30B': 0, 'D': 1} for i in range(1, 4)}}
U3_COMPARISONS = sum(sum(row.values()) for row in U3_SCOPES.values())


def _series_tail(q, n, tests):
    # w=sqrt(v) removes the chi-square density's origin singularity.
    hi, steps = math.sqrt(n+14*math.sqrt(2*n)+40), 4000
    h = hi/steps
    log_c = -(n/2)*math.log(2)-math.lgamma(n/2)
    total = 0.
    for i in range(1, steps+1):
        w = i*h
        tail = min(math.erfc(q*w/math.sqrt(n)/math.sqrt(2)), 1-1e-16)
        value = -math.expm1(tests*math.log1p(-tail))
        total += (1 if i == steps else 4 if i%2 else 2)*math.exp(
            log_c+math.log(2)+(n-1)*math.log(w)-w*w/2)*value
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
    heavy = any(abs(v) > 3*math.sqrt(math.fsum(x*x for j, x in enumerate(r) if j != i)/(len(r)-1))
                for i, v in enumerate(r))
    beta = .025 if heavy else .05
    lo, hi = 0., 200.
    for _ in range(64):
        mid = (lo+hi)/2
        lo, hi = (mid, hi) if _series_tail(mid, len(r), U3_COMPARISONS) > beta else (lo, mid)
    bar = hi*s0
    screen = evidence.get('r1_d_screen')
    screen_pass = bool(screen and screen.get('token_identical') is True
                       and screen.get('eligible') is True
                       and abs(screen['relative_difference']) <= 1.5*bar)
    return dict(status='available', n=len(r), rms_relative=s0, q=hi, beta=beta,
                comparisons=U3_COMPARISONS, checks_by_window={w: dict(r) for w, r in U3_SCOPES.items()},
                d_transfer_factor=1.5, heavy_tail_rule_applied=heavy,
                heavy_tail_rule='R21 A22: abs(r_i) > 3 * zero-centred leave-one-out RMS',
                relative_bar_30B=bar, relative_bar_D=1.5*bar,
                d_screen='not_refuted' if screen_pass else 'missing_or_refuted',
                qualified=evidence.get('frozen_before_W1') is True,
                limitation='zero-mean normal model; D transfer and dependence remain assumptions')


def u3_pair(a, b, derivation, population):
    if any('X5' in m.get('analysis_classes', []) for m in (a,b)):
        return dict(status='excluded', reason='X5', token_identical=False)
    if any(ex.classes(td.calibration_exclusions(m)) or m.get('status') != 'completed'
           or set((m.get('battery') or {}).get('flags', [])) &
              {'battery.member_span', 'battery.accumulator_excursion'} or m.get('analysis_ineligible', False) for m in (a, b)):
        return dict(status='inconclusive', reason='ineligible replay member')
    if not a.get('identity_sha256') or not b.get('identity_sha256'):
        return dict(status='inconclusive', reason='identity missing')
    if a['identity_sha256'] != b['identity_sha256']:
        return dict(status='excluded', reason='X5', token_identical=False)
    if a.get('turn_counts') is None or b.get('turn_counts') is None:
        return dict(status='inconclusive', reason='per-turn counts missing')
    if a['turn_counts'] != b['turn_counts']:
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


def window_checks(members, derivation, *, window=None):
    # The registered roster leaves ordinals 1-4 unchanged/ungated. All
    # contrast, D and sentinel slots plan G0. Decide from planned slots BEFORE
    # filtering captures, never from the presence of a recorded G0 interval.
    g0_planned = {model: any(m['slot'].get('ordinal') not in (1, 2, 3, 4)
                            for m in members if m['slot']['model_id'] == model)
                  for model in {m['slot']['model_id'] for m in members}}
    members = [m for m in members if m.get('captured', m['thermal'].get('captured', True))]
    result = {}
    for model in sorted({m['slot']['model_id'] for m in members}):
        rows = [m['thermal'] for m in members if m['slot']['model_id'] == model]
        by_ordinal = {m['slot'].get('ordinal', m['thermal'].get('ordinal')): m['thermal']
                      for m in members if m['slot']['model_id'] == model}
        fixed = ([(5, 17)] if model == 'qwen3.8-27b' else [(6, 16), (9, 13), (7, 15), (10, 12)]) if window == 'W1' else (
            [(5, 22)] if model == 'qwen3.8-27b' else [])
        # Tags are a custody assertion, never a pair selector.
        groups = {}
        for ordinal, row in by_ordinal.items():
            if row.get('identical_work_group'):
                groups.setdefault(row['identical_work_group'], []).append(ordinal)
        observed_fixed = [[i for i in pair if i in by_ordinal] for pair in fixed]
        if groups and sorted(sorted(v) for v in groups.values()) != sorted(sorted(v) for v in observed_fixed if v):
            raise ValueError('desk replay tags differ from fixed ordinal pairs')
        pairs = []
        for a, b in fixed:
            p = (u3_pair(by_ordinal[a], by_ordinal[b], derivation,
                        'D' if model == 'qwen3.8-27b' else '30B') if a in by_ordinal and b in by_ordinal else
                 dict(status='inconclusive', reason='fixed replay missing'))
            pairs.append(dict(ordinals=[a, b], **p))
        # Anchors in C/T are bridge diagnostics, not extra U3 tests (R25 N=22).
        check = td.acceptance(rows, v4=True)
        if not g0_planned[model]:
            check['U2']['parts']['a'] = 'not_applicable'
            check['U2']['g0_slow_range_c'] = None
        else:
            # R23n: U2(b) runs only over members whose planned G0 is present.
            # A g0_missing member's G1/H releases have no planned-G0 reference.
            # With no planned G0 present, U2(b) is inconclusive, never fail.
            present = [r for o, r in by_ordinal.items() if o not in (1, 2, 3, 4)
                       and any(i.get('kind') == 'G0' for i in r.get('intervals', ()))]
            if not present:
                check['U2']['parts']['b'] = 'inconclusive'
            else:
                ids = {id(r) for r in present}
                releases = [v['journal_verified'] for r in rows if id(r) in ids and r.get('gated')
                            and not td.thermal_exclusions(r) for v in r['releases'] if v.get('kind') != 'G0']
                check['U2']['parts']['b'] = (td.combine(['inconclusive' if v is None else 'pass' if v else 'fail'
                                                         for v in releases]) if releases else 'not_applicable')
        applicable = [v for v in check['U2']['parts'].values() if v != 'not_applicable']
        check['U2']['status'] = td.combine(applicable) if applicable else 'not_applicable'
        check['U3'] = dict(status=td.combine([p['status'] for p in pairs if p['status'] != 'excluded'])
                          if any(p['status'] != 'excluded' for p in pairs) else 'inconclusive', pairs=pairs)
        result[model] = {k: check[k] for k in ('U1', 'U2', 'U3')}
    return result


def battery(members):
    members = [m for m in members if m['captured']]
    charge = missing = assist = 0
    for m in members:
        b = m['thermal'].get('battery') or {}
        flags = set(b.get('flags', [])) | set(m['thermal'].get('flags', []))
        charge += bool(flags & {'battery.member_span', 'battery.accumulator_excursion'})
        missing += b.get('status') != 'observed'
        assist += 'battery.assist' in flags
    return dict(status='fail' if charge else 'unavailable' if missing or not members else 'pass',
                charging_members=charge, unobserved_members=missing, assist_members=assist,
                next_action='fresh_topup_and_obc' if charge else 'none', assist='disclosure_only',
                members=[dict(run_id=m['slot']['run_id'],
                    soc_pct=(m['thermal'].get('battery') or {}).get('soc_pct'),
                    charger_w=(m['thermal'].get('battery') or {}).get('charger_w'),
                    flags=(m['thermal'].get('battery') or {}).get('flags', [])) for m in members])


def anchor_diagnostic(windows, selection=None):
    sessions = {}
    w1_block = 'unavailable:W1 window unavailable'
    # W1 arrives only from its window, after the engine's full member screen.
    if selection is not None:
        anchors = [r for r in selection['members'] if r.get('ordinal') in (1, 2, 3, 4)]
        if len(anchors) != 4 or {r['ordinal'] for r in anchors} != {1, 2, 3, 4}:
            w1_block = 'unavailable:four W1 anchors required'
        else:
            reasons = set()
            for r in anchors:
                if not r.get('captured', True):
                    reasons.add('not_captured')
                    continue
                reasons.update(ex.classes([*td.calibration_exclusions(r),
                    *r.get('calibration_exclusions', []), *r.get('analysis_classes', [])]))
                if r.get('status') != 'completed':
                    reasons.add('incomplete')
                if r.get('anchor_eligible') is not True and not reasons:
                    reasons.add('anchor_ineligible')
            if reasons:
                w1_block = 'excluded:'+','.join(sorted(reasons))
            elif any(type(r.get('turn_owned_j')) not in (int, float)
                     or not math.isfinite(r['turn_owned_j']) for r in anchors):
                w1_block = 'unavailable:W1 anchor energy unavailable'
            else:
                sessions['W1'] = {str(r['ordinal']): r['turn_owned_j'] for r in anchors}
                w1_block = 'included'
    for w in windows:
        anchors = [m for m in w['members'] if m['slot']['series_role'] == 'anchor']
        if len(anchors) == 4 and all(m['captured'] and m['eligible'] for m in anchors):
            sessions[w['window']] = {str(m['slot']['ordinal']): m['thermal']['turn_owned_j'] for m in anchors}
    result = dict(K=len(sessions), anchor_sigma_j=None, ms_window_j2=None, ms_error_j2=None,
                  sigma_w2_raw_j2=None, sigma_w2_reported_j2=None,
                  method='balanced crossed-anchor moment')
    result.update(td._anchor_moments(sessions))
    if result['ms_window_j2'] is not None:
        raw = (result['ms_window_j2']-result['ms_error_j2'])/4
        result.update(sigma_w2_raw_j2=raw, sigma_w2_reported_j2=max(0., raw))
    # The historical helper has a 6J veto; v4 expressly demotes it to print-only.
    result.pop('status')
    return dict(status='print_only', W1_anchor_block=w1_block, **result)


def u4(reference, windows):
    if (not reference or reference.get('qualified') is not True
            or len(reference.get('r1_replay_j', [])) != 2
            or set(reference.get('w1_sentinel_j', {})) != {'5', '17'}):
        return dict(status='inconclusive', reason='qualified R1 pair and W1 5/17 required')
    ref = fmean([*reference['r1_replay_j'], *reference['w1_sentinel_j'].values()])
    if not ref > 0:
        return dict(status='inconclusive', reason='positive E_ref required')
    values = {'W1': list(reference['w1_sentinel_j'].values())}
    per_window = {'W1': dict(status='unevaluable', window_count=1, skipped=False)}
    for window in windows:
        name = window['window']
        sentinels = [m for m in window['members'] if m['captured'] and m['slot']['ordinal'] in (5, 22)]
        reason = None
        if len(sentinels) != 2 or any(not m['eligible'] or not m['thermal'].get('identity_sha256')
               or len((m.get('summary') or {}).get('residual_rows', {}).get('True', [])) < 3 for m in sentinels):
            reason = 'sentinel incomplete or ineligible'
        elif (len({m['thermal']['identity_sha256'] for m in sentinels}) != 1 or
              sentinels[0]['thermal'].get('turn_counts') != sentinels[1]['thermal'].get('turn_counts')):
            reason = 'sentinel identity unavailable/divergent'
        if reason:
            per_window[name] = dict(status='inconclusive', skipped=True, reason=reason, window_count=len(values))
            continue
        values[name] = [m['thermal']['turn_owned_j'] for m in sentinels]
        result = td._sentinel_equivalence(values, ref) if len(values) >= 3 else dict(status='unevaluable')
        per_window[name] = {**result, 'window_count': len(values), 'skipped': False}
    evaluated = [r for r in per_window.values() if not r['skipped']]
    result = evaluated[-1]
    return {**result, 'E_ref_j': ref, 'window_count': len(values),
            'per_window': per_window, 'R20_trigger': result['status'] in ('fail', 'inconclusive'),
            'sigma_w_30b': {'status': 'print_only', 'reason': 'requires balanced crossed anchors'}}


def u5(evidence):
    if not evidence:
        return dict(status='inconclusive', reason='R1 three designed start states missing', triggers_R20=False)
    states = evidence.get('states', [])
    if len(states) != 3 or any(p.get('token_identical') is not True or
        any(type(p.get(k)) not in (int,float) or not math.isfinite(p[k]) for k in ('g0_slow_c','turn_owned_j')) for p in states):
        return dict(status='inconclusive', reason='three identical-work designed-state members required', triggers_R20=False)
    fit = td.regression([[1., p['g0_slow_c']] for p in states], [p['turn_owned_j'] for p in states])
    if fit is None:
        return dict(status='inconclusive', reason='state sensitivity rank deficient', triggers_R20=False)
    sigma = max(stdev(evidence['r1_replay_j']), 2.97)
    delta = evidence['delta_slow_c']
    point = abs(fit['coef'][1])*delta
    upper = max(map(abs, fit['ci90'][1]))*delta
    return dict(status='fail' if point > sigma else 'pass' if upper <= sigma else 'inconclusive',
                beta_T_j_per_c=fit['coef'][1], beta_T_ci90=fit['ci90'][1], c=1.,
                intercept_j=fit['coef'][0], df=fit['df'], designed_states=states, triggers_R20=False,
                sigma_pair_j=sigma, delta_slow_c=delta, point_shift_j=point, upper90_shift_j=upper)


def u6(records, split_rule, *, pooled_rss=None, pooled_df=None):
    if split_rule != 'within_pair_episode_order':
        return dict(status='inconclusive', reason='frozen U6 split/unit missing', imprecise=None)  # R27(d): no interval
    if len(records) < 2:
        return dict(status='inconclusive', reason='insufficient trajectories', imprecise=None)
    turns = [v for r in records for v in r['residual_j']]
    # The owning contract must explicitly adopt this per-turn s_r definition.
    if len(turns) < 2 or pooled_df is None or pooled_df <= 0 or pooled_rss is None or pooled_rss < 0:
        return dict(status='inconclusive', reason='no residual degrees of freedom', imprecise=None)  # R27(d): no interval
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
        return dict(status='inconclusive', reason='empty chronological half', imprecise=None)  # R27(d): no interval
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
    sr = math.sqrt(pooled_rss/pooled_df)
    effect, margin = means[1]-means[0], .5*sr
    ci = [effect-1.645*se, effect+1.645*se]
    status = 'fail' if abs(effect) > margin else 'pass' if ci[0] >= -margin and ci[1] <= margin else 'inconclusive'
    return dict(status=status, effect_j=effect, ci90_j=ci, margin_j=margin,
                trajectory_clustered_se_j=se, se_kind='trajectory_clustered',
                imprecise=status == 'inconclusive',
                turn_position_residual_means=estimands.d_turn_position_means(positions),
                s_r_unit='per_turn_J', s_r_definition='sqrt(sum C-window full-fit RSS / sum full-fit df)',
                pooled_rss=pooled_rss, pooled_df=pooled_df, s_r_j=sr, split_rule=split_rule)
