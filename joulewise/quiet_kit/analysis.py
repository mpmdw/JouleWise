"""Pure calibration arithmetic. Missing observations produce undefined quantities.

These functions accept parsed observations and never access files, hardware,
calibration ledgers, block-5 outcomes, or registration policy.
"""
from __future__ import annotations

import math
import statistics
from functools import lru_cache


def undefined(reason, unit='', sources=()):
    return {'value': None, 'unit': unit, 'undefined': reason, 'sources': list(sources),
            'uncertainty': {'kind': 'standard error', 'value': None, 'n': 0, 'method': reason}}


def quantity(value, unit, uncertainty=None, sources=()):
    return {'value': value, 'unit': unit, 'uncertainty': uncertainty or
            {'kind': 'standard error', 'value': None, 'n': 0, 'method': 'not estimable'},
            'sources': list(sources)}


def _defined(q):
    value = q.get('value')
    return isinstance(value, (int, float)) and math.isfinite(value)


def mean(values, unit, sources=()):
    values = [float(v) for v in values if isinstance(v, (int, float)) and math.isfinite(v)]
    if not values:
        return undefined('empty segment', unit, sources)
    n = len(values)
    se = statistics.stdev(values)/math.sqrt(n) if n > 1 else None
    return quantity(statistics.mean(values), unit,
                    {'kind': 'standard error', 'value': se, 'n': n,
                     'undefined': 'one record; scatter cannot be estimated' if n == 1 else None,
                     'method': 'sample standard deviation / sqrt(n); record scatter, no independence claim'}, sources)


def sd(values, unit, sources=()):
    if len(values) < 2:
        return undefined('fewer than two observations', unit, sources)
    return quantity(statistics.stdev(values), unit,
                    {'kind': 'standard deviation', 'value': statistics.stdev(values),
                     'n': len(values), 'method': 'sample standard deviation'}, sources)


def percentile(values, q):
    vals = sorted(values)
    if not vals:
        return None
    pos = (len(vals)-1)*q
    low = int(pos)
    return vals[low] + (vals[min(low+1, len(vals)-1)]-vals[low])*(pos-low)


def linear(xs, ys):
    if len(xs) < 3 or len(xs) != len(ys):
        return {'undefined': 'line needs at least three paired points'}
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((x-mx)**2 for x in xs)
    if sxx <= 0:
        return {'undefined': 'zero x span'}
    b = sum((x-mx)*(y-my) for x, y in zip(xs, ys))/sxx
    a = my-b*mx
    residuals = [y-a-b*x for x, y in zip(xs, ys)]
    residual_sd = math.sqrt(sum(r*r for r in residuals)/(len(xs)-2))
    return {'intercept': a, 'slope': b, 'slope_se': residual_sd/math.sqrt(sxx),
            'residuals': residuals, 'residual_sd': residual_sd, 'n': len(xs)}


def _segment(segment, rail='total'):
    return [r.get(rail) for r in segment.get('records', []) if r.get(rail) is not None]


def _step(load, before, after, rail='total'):
    sources = [s.get('id') for s in (before, load, after)]
    quantities = [mean(_segment(s, rail), 'W') for s in (before, load, after)]
    if any(q['value'] is None for q in quantities):
        return undefined('empty bracketing segment', 'W', sources)
    b, l, a = quantities
    errors = [q['uncertainty']['value'] for q in quantities]
    se = math.sqrt(errors[1]**2 + (errors[0]**2 + errors[2]**2)/4) if all(
        e is not None for e in errors) else None
    return quantity(l['value']-(b['value']+a['value'])/2, 'W',
                    {'kind': 'standard error', 'value': se,
                     'n': [q['uncertainty']['n'] for q in quantities],
                     'method': 'SE(load)^2 + (SE(before)^2 + SE(after)^2)/4, square root'}, sources)


def _arms(segments):
    for i, s in enumerate(segments):
        if s.get('kind') not in ('idle', 'burst') and 0 < i < len(segments)-1:
            if segments[i-1].get('kind') == segments[i+1].get('kind') == 'idle':
                yield s, segments[i-1], segments[i+1]


def _binomial_cdf(k, n, p):
    return sum(math.comb(n, j)*p**j*(1-p)**(n-j) for j in range(k+1))


def clopper_pearson(k, n):
    if n == 0:
        return None
    def root(target, index):
        lo, hi = 0., 1.
        for _ in range(80):
            mid = (lo+hi)/2
            if _binomial_cdf(index, n, mid) > target:
                lo = mid
            else:
                hi = mid
        return (lo+hi)/2
    return [0. if k == 0 else root(.975, k-1),
            1. if k == n else root(.025, k)]


def m4(data):
    segments = data.get('segments', [])
    arms = []
    for s, before, after in _arms(segments):
        step = _step(s, before, after)
        rate = s.get('cpu_seconds', 0)/s.get('elapsed_s', 1) if s.get('elapsed_s', 0) > 0 else 0
        if rate <= 0 or step['value'] is None:
            w = undefined('no positive measured load CPU rate or power step', 'W / (CPU-s/s)')
        else:
            w = quantity(step['value']/rate, 'W / (CPU-s/s)',
                         {**step['uncertainty'], 'value': step['uncertainty']['value']/rate
                          if step['uncertainty']['value'] is not None else None,
                          'method': step['uncertainty']['method'] + '; true resource CPU time treated as observed'},
                         step['sources'])
        arms.append({'segment': s.get('id'), 'priority': s.get('priority'), 'duty': s.get('duty'),
                     'true_cpu_rate': quantity(rate, 'CPU-s/s'), 'power_step': step, 'watts_per_cpu_rate': w,
                     'inside_one_accounting_interval_energy': quantity(.5*w['value'], 'J',
                         {**w['uncertainty'], 'value': .5*w['uncertainty']['value'] if w['uncertainty']['value'] is not None else None})
                         if w['value'] is not None else undefined('watts per CPU rate undefined', 'J')})
    bursts = []
    for i, s in enumerate(segments):
        if s.get('kind') != 'burst':
            continue
        before = next((x for x in reversed(segments[:i]) if x.get('kind') == 'idle'), {})
        after = next((x for x in segments[i+1:] if x.get('kind') == 'idle'), {})
        bv, av = _segment(before), _segment(after)
        start, end = s.get('burst_on_s', 0)-.5, s.get('burst_off_s', 0)+1.
        records = [r for x in segments for r in x.get('records', [])]
        relevant = [r for r in records if min(r.get('end_s', 0), end) > max(r.get('start_s', 0), start)]
        if not bv or not av or not relevant:
            energy = undefined('missing burst or bracketing idle records', 'J')
        else:
            baseline = (statistics.mean(bv)+statistics.mean(av))/2
            energy_j = sum((r['total']-baseline)*max(0., min(r['end_s'], end)-max(r['start_s'], start))
                           for r in relevant)
            noise = statistics.stdev(bv+av) if len(bv+av) > 1 else None
            energy = quantity(energy_j, 'J', {'kind': 'standard deviation',
                       'value': noise*(end-start) if noise is not None else None, 'n': len(bv+av),
                       'method': 'bracketing idle scatter x integration window length'}, [s.get('id')])
        cpu = s.get('cpu_seconds')
        duration = s.get('burst_s', 0)
        placement = s.get('actual_placement_s', s.get('placement_s', 0))
        allowed = 0.
        for tick in range(math.floor(placement/10), math.floor((placement+duration)/10)+1):
            overlap = max(0., min(placement+duration, (tick+1)*10)-max(placement, tick*10))
            allowed += min(.5, overlap)
        possible = (quantity(energy['value']/cpu*allowed, 'J',
                    {**energy['uncertainty'], 'value': energy['uncertainty']['value']/cpu*allowed
                     if energy['uncertainty']['value'] is not None else None,
                     'method': 'measured burst J per true CPU-second x permitted CPU work; linear power inference'})
                    if cpu and energy['value'] is not None else undefined('burst CPU time or energy undefined', 'J'))
        bursts.append({'segment': s.get('id'), 'burst_s': s.get('burst_s'),
                       'placement_s': s.get('placement_s'), 'added_energy': energy,
                       'actual_placement_s': s.get('actual_placement_s'),
                       'permitted_cpu_seconds_inside_phase': allowed,
                       'phase_energy_below_census_limit': possible,
                       'accounting_intervals': s.get('accounting_intervals', [])})
    inference = [{'segment': s.get('id'), 'outside_cpu_rate': s.get('outside_cpu_rate'),
                  'rail_mean': mean(_segment(s), 'W', [s.get('id')]),
                  'simultaneous_ticks': s.get('ticks', [])}
                 for s in segments if s.get('kind') == 'idle']
    paired = [(tick.get('outside_cpu_rate'), tick.get('rail_power_w')) for s in segments
              if s.get('kind') == 'idle' for tick in s.get('ticks', [])
              if tick.get('outside_cpu_rate') is not None and tick.get('rail_power_w') is not None]
    fit = linear([p[0] for p in paired], [p[1] for p in paired])
    complete = (len(arms) == 6 and all(_defined(a['watts_per_cpu_rate']) for a in arms)
                and sum(_defined(b['added_energy']) for b in bursts) >= 16)
    return {'arms': arms, 'bursts': bursts, 'daemon_inference': inference,
            'incomplete_reason': None if complete else 'contention_quantities_undefined',
            'undefined': 'no complete bracketing load segments' if not arms else None,
            'daemon_watts_per_cpu_rate_fit': fit,
            'daemon_label': 'inference from simultaneous outside-process CPU time and rail readings',
            'single_process_phase_energy_formula': 'w * 0.05 CPU-s/s * 10 s = 0.5*w J; CPU time can concentrate inside a phase'}


def m5(data):
    segments = data.get('segments', [])
    idle_gpu = [v for s in segments if s.get('kind') == 'idle' for v in _segment(s, 'gpu_power')]
    levels = [{'segment': s.get('id'), 'kind': s.get('kind'), 'duty': s.get('duty'),
               'added_power': {rail: _step(s, b, a, rail) for rail in ('cpu_power', 'gpu_power', 'ane_power', 'total')},
               'contender_cpu_rate': quantity(s.get('cpu_seconds', 0)/s['elapsed_s'], 'CPU-s/s')
               if s.get('elapsed_s', 0) > 0 else undefined('no measured duration', 'CPU-s/s')}
              for s, b, a in _arms(segments)]
    idle_mean = mean(idle_gpu, 'W')
    complete = (_defined(idle_mean) and len(levels) == 6
                and all(_defined(l['added_power']['gpu_power']) for l in levels))
    return {'idle_gpu_mean': idle_mean, 'idle_gpu_sd': sd(idle_gpu, 'W'),
            'incomplete_reason': None if complete else 'graphics_rail_quantities_undefined',
            'idle_gpu_p95': quantity(percentile(idle_gpu, .95), 'W'), 'levels': levels,
            'excluding_power_formula': 'P_added * phase_duration_s >= F_min_J / 4',
            'non_claim_illustration': {'F_min_J': 2.1, 'phase_duration_s': .62,
                                     'power_W': 2.1/4/.62, 'label': 'threshold-note illustration; not a block-5 floor'}}


def m1(data):
    captures = data.get('captures', [])
    groups = {}
    for condition in ('quiet', 'load', 'utility'):
        rows = [c for c in captures if c.get('condition') == condition]
        vals = [c['bound_s']*1000 for c in rows if c.get('bound_s') is not None]
        groups[condition] = {'captures': rows, 'capture_count': len(rows), 'bounded_capture_count': len(vals),
                             'median': quantity(statistics.median(vals), 'ms') if vals and len(vals) == len(rows)
                             else undefined('one or more capture bounds undefined', 'ms'),
                             'maximum': quantity(max(vals), 'ms') if vals and len(vals) == len(rows)
                                 else undefined('one or more capture bounds undefined', 'ms')}
    quiet = [c for c in captures if c.get('condition') == 'quiet']
    disturbed = [c for c in captures if c.get('condition') != 'quiet']
    k, n = sum(c['bound_s'] > .03646 for c in quiet if c.get('bound_s') is not None), len(quiet)
    missing_quiet = sum(c.get('bound_s') is None for c in quiet)
    def pairs(left, right):
        return [{'opening': o.get('id'), 'closing': c.get('id'),
                 'operative_bound': quantity((max(o['bound_s'], c['bound_s'])+
                      max(abs(c['bound_s']-o['bound_s']), .014531))*1000, 'ms')
                      if o.get('bound_s') is not None and c.get('bound_s') is not None else
                      undefined('one capture bound undefined', 'ms', [o.get('id'), c.get('id')])}
                for o in left for c in right if o is not c]
    qp, dp = pairs(quiet, quiet), pairs(quiet, disturbed) + pairs(disturbed, quiet)
    qmax = (max(p['operative_bound']['value'] for p in qp) if qp and all(
        p['operative_bound']['value'] is not None for p in qp) else None)
    dmin = (min(p['operative_bound']['value'] for p in dp) if dp and all(
        p['operative_bound']['value'] is not None for p in dp) else None)
    complete = all(groups[c]['bounded_capture_count'] >= n for c, n in
                   (('quiet', 8), ('load', 3), ('utility', 3)))
    return {'conditions': groups, 'incomplete_reason': None if complete else 'captures_unbounded',
            'quiet_fraction_above_screen': quantity(k/n, 'fraction', {'kind': '95% interval',
               'value': clopper_pearson(k, n), 'n': n, 'method': 'exact Clopper-Pearson binomial interval'})
               if n and not missing_quiet else undefined('one or more quiet bounds undefined' if n else 'no quiet captures', 'fraction'),
            'quiet_ordered_pairs': qp, 'quiet_disturbed_ordered_pairs': dp,
            'separation': quantity(dmin-qmax, 'ms') if dmin is not None and qmax is not None else
               undefined('missing quiet or disturbed pair', 'ms'),
            'stop_line_range': {'lower_ms': qmax, 'upper_ms': dmin,
               'nonempty': qmax is not None and dmin is not None and dmin > qmax,
               'note': 'reports separation only; chooses no stop line'}}


def m2(data, arm='L'):
    runs = data.get('runs', [])
    phases = sorted({'prefill', 'decode'} | {phase for r in runs for phase in r.get('phase_energy_j', {})})
    measured = {}
    for phase in phases:
        quads, ordinary = [], []
        for q in range(5):
            rows = [r for r in runs if r.get('quad') == q and not r.get('failure_reasons')
                    and r.get('returncode') in (0, None)]
            ns = [r['phase_energy_j'][phase] for r in rows if r.get('arm') == 'N' and phase in r.get('phase_energy_j', {})]
            ls = [r['phase_energy_j'][phase] for r in rows if r.get('arm') == arm and phase in r.get('phase_energy_j', {})]
            if len(ns) == len(ls) == 2 and all(_defined({'value': v}) for v in ns+ls):
                quads.append((sum(ls)-sum(ns))/2)
                ordinary.extend(ns)
        available_mean = mean(quads, 'J', [r.get('id') for r in runs])
        qmean = available_mean if len(quads) == 5 else undefined('five complete quads required', 'J',
                                                                               [r.get('id') for r in runs])
        se = qmean['uncertainty']['value']
        if len(quads) == 5 and se is not None:
            lo, hi = qmean['value']-2.776*se, qmean['value']+2.776*se
            qmean['uncertainty'] = {'kind': '95% interval', 'value': [lo, hi], 'n': 5,
                                    'method': 'paired quad means; t(0.975,4)=2.776', 'standard_error': se}
        else:
            qmean['interval_undefined'] = 'five complete quads required for specified t interval'
        base = statistics.mean(ordinary) if ordinary else 0
        percent = (quantity(100*qmean['value']/base, '%',
                          {'kind': '95% interval', 'value': [100*x/base for x in qmean['uncertainty']['value']],
                           'n': 5, 'method': 'joule interval divided by observed ordinary mean'}) if base and len(quads) == 5 else
                  undefined('five complete quads and positive ordinary mean required', '%'))
        measured[phase] = {'quad_differences_j': quads, 'complete_quad_count': len(quads),
                          'available_quad_mean_diagnostic': available_mean if len(quads) != 5 else None,
                          'short_minus_ordinary' if arm == 'S' else 'long_minus_ordinary': qmean, 'percent': percent}
    complete = all(p['complete_quad_count'] == 5 for p in measured.values())
    return {'phases': measured, 'run_table': runs, 'long_waits': data.get('long_waits', []),
            'incomplete_reason': None if complete else 'five_complete_quads_required',
            'undefined': 'no measured phase energies' if not any(r.get('phase_energy_j') for r in runs) else None}


def m2b(data):
    result = m2(data, arm='S')
    failures = [{'run': r.get('id'), 'returncode': r.get('returncode'),
                 'reasons': r.get('failure_reasons') or [{'reason': 'nonzero_exit'}]}
                for r in data.get('runs', []) if r.get('arm') == 'S' and
                (r.get('failure_reasons') or r.get('returncode') not in (0, None))]
    result['short_baseline_refusals'] = failures
    if failures:
        result['incomplete_reason'] = 'short_baseline_refused_by_run_path'
    elif len(data.get('runs', [])) != 20 or any(r.get('failure_reasons') for r in data.get('runs', [])):
        result['incomplete_reason'] = 'short_baseline_run_table_incomplete'
    elif result['incomplete_reason']:
        result['incomplete_reason'] = 'short_baseline_run_table_incomplete'
    return result


def m3(data):
    groups, current = [], []
    for row in data.get('clock', []):
        if row.get('anchor') is None:
            if current:
                groups.append(current)
                current = []
            continue
        if current and (row.get('boot_session_uuid') != current[-1].get('boot_session_uuid') or
                        row['anchor']['monotonic_raw_ns']-current[-1]['anchor']['monotonic_raw_ns'] > 60e9):
            groups.append(current)
            current = []
        current.append(row)
    if current:
        groups.append(current)
    segments = []
    longest = data.get('longest_sampler_s', 0)
    for group in groups:
        anchors = [r['anchor'] for r in group]
        origin = anchors[0]['monotonic_raw_ns']
        yorigin = anchors[0]['realtime_ns']-origin
        xs = [(a['monotonic_raw_ns']-origin)/1e9 for a in anchors]
        ys = [(a['realtime_ns']-a['monotonic_raw_ns']-yorigin)/1e9 for a in anchors]
        fit = linear(xs, ys)
        if 'undefined' in fit:
            segments.append({'rate': undefined(fit['undefined'], 'ppm')})
            continue
        rate = fit['slope']*1e6
        budgets = []
        for length, source in ((longest, 'longest kit stream; waiting-proper length comes from fault rehearsal'),
                               (1835., 'draft illustrative waiting stream')):
            budget = .010/length*1e6 if length > 0 else None
            budgets.append({'L_s': length, 'source': source, 'budget': quantity(budget, 'ppm'),
                            'margin': quantity(budget-abs(rate), 'ppm') if budget is not None else
                                undefined('no sampler stream observed', 'ppm')})
        residuals = fit['residuals']
        stored = [(r.get('frequency') or {}).get('frequency_ppm') for r in group]
        segments.append({'boot_session_uuid': group[0].get('boot_session_uuid'), 'duration_s': xs[-1],
             'source_attempts': sorted({r['source_attempt'] for r in group if 'source_attempt' in r}),
             'rate': quantity(rate, 'ppm', {'kind': 'standard error', 'value': fit['slope_se']*1e6,
                     'n': len(group), 'method': 'centered OLS slope; residual variance/(n-2)'}),
             'residual_max': quantity(max(abs(r) for r in residuals)*1000, 'ms'),
             'residual_step_max': quantity(max((abs(b-a) for a, b in zip(residuals, residuals[1:])), default=0)*1000, 'ms'),
             'stored_correction': mean([v for v in stored if v is not None], 'ppm'), 'budgets': budgets})
    span = max((s.get('duration_s', 0) for s in segments), default=0)
    minimum = data.get('minimum_clock_span_s', 10800)
    return {'segments': segments, 'minimum_span_s': minimum,
            'incomplete_reason': None if span >= minimum else 'clock_span_under_3h',
            'undefined': 'no continuous usable clock series' if not segments else None,
            'span_s': span}


def _gamma_p(a, x):
    if x <= 0:
        return 0.
    if x < a+1:
        term = total = 1/a
        for k in range(1, 1000):
            term *= x/(a+k)
            total += term
            if abs(term) < abs(total)*1e-15:
                break
        return total*math.exp(-x+a*math.log(x)-math.lgamma(a))
    b = x+1-a
    c, d = 1e300, 1/b
    h = d
    for i in range(1, 1000):
        an = -i*(i-a)
        b += 2
        d = an*d+b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b+an/c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1/d
        delta = d*c
        h *= delta
        if abs(delta-1) < 1e-15:
            break
    return 1-math.exp(-x+a*math.log(x)-math.lgamma(a))*h


def chi2_quantile(p, df):
    lo, hi = 0., float(max(df, 1))
    while _gamma_p(df/2, hi/2) < p:
        hi *= 2
    for _ in range(100):
        mid = (lo+hi)/2
        if _gamma_p(df/2, mid/2) < p:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def m9(data):
    servers = {}
    for name in ('time.apple.com', 'time.cloudflare.com'):
        rows = [r for r in data.get('queries', []) if r.get('server') == name and r.get('offset_s') is not None]
        fit = linear([r['time_s'] for r in rows], [r['offset_s']*1000 for r in rows])
        if 'undefined' in fit:
            scatter = undefined(fit['undefined'], 'ms')
        else:
            df = len(rows)-2
            scatter = quantity(fit['residual_sd'], 'ms', {'kind': '95% interval',
               'value': [math.sqrt(df*fit['residual_sd']**2/chi2_quantile(.975, df)),
                         math.sqrt(df*fit['residual_sd']**2/chi2_quantile(.025, df))],
               'n': len(rows), 'method': 'detrended normal residual scatter; chi-square with n-2 degrees of freedom'})
        servers[name] = {'offsets': rows, 'line': fit, 'one_query_scatter': scatter}
    paired = {}
    for r in data.get('queries', []):
        if r.get('offset_s') is not None:
            paired.setdefault(r.get('query'), {})[r['server']] = r['offset_s']
    differences = [(r['time.apple.com']-r['time.cloudflare.com'])*1000 for r in paired.values()
                   if 'time.apple.com' in r and 'time.cloudflare.com' in r]
    return {'servers': servers, 'apple_minus_cloudflare': mean(differences, 'ms'),
            'incomplete_reason': None if all(len(s['offsets']) >= 8 for s in servers.values())
                else 'time_server_offsets_insufficient'}


def m14(data):
    levels = []
    for s, b, a in _arms(data.get('segments', [])):
        meter, rails = _step(s, b, a, 'meter'), _step(s, b, a)
        ratio = rails['value']/meter['value'] if meter['value'] and rails['value'] is not None else None
        sr, sm = rails['uncertainty']['value'], meter['uncertainty']['value']
        ratio_se = (math.sqrt(sr*sr/meter['value']**2+rails['value']**2*sm*sm/meter['value']**4)
                    if ratio is not None and sr is not None and sm is not None else None)
        levels.append({'segment': s.get('id'), 'kind': s.get('kind'), 'duty': s.get('duty'),
                       'meter_step': meter, 'rail_step': rails, 'rails_over_meter': quantity(ratio, 'ratio',
                           {'kind': 'standard error', 'value': ratio_se,
                            'n': [rails['uncertainty']['n'], meter['uncertainty']['n']],
                            'method': 'delta method, rail and meter step errors treated independently; covariance unmeasured'}),
                       'battery_current_ma': s.get('battery_current_ma', []),
                       'battery_flag': any(abs(v) > 200 for v in s.get('battery_current_ma', []))})
    idles = [{'segment': s.get('id'), 'noise': sd(_segment(s, 'meter'), 'W')}
             for s in data.get('segments', []) if s.get('kind') == 'idle']
    complete = len(levels) == 8 and all(_defined(l['meter_step']) and _defined(l['rail_step']) for l in levels)
    return {'levels': levels, 'idle_noise': idles,
            'incomplete_reason': 'meter_absent' if data.get('meter_present') is not True else
                None if complete else 'meter_or_rail_steps_undefined',
            'undefined': 'no meter segments' if not levels and not idles else None,
            'interpretation': 'idle sample scatter, not a certified detection limit'}


def _student_cdf(x, df):
    # Integrate the smooth t density by Simpson's rule; enough accuracy for
    # calibration reporting, independent reference quantiles tested below.
    if x < 0:
        return 1-_student_cdf(-x, df)
    n = 2048
    dx = x/n
    factor = math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2))/math.sqrt(df*math.pi)
    def density(t):
        return factor*(1+t*t/df)**(-(df+1)/2)
    return .5+dx/3*(density(0)+density(x)+sum((4 if i%2 else 2)*density(i*dx) for i in range(1, n)))


@lru_cache(maxsize=64)
def t975(df):
    lo, hi = 0., 100.
    for _ in range(50):
        mid = (lo+hi)/2
        if _student_cdf(mid, df) < .975:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def m10(data):
    rows = []
    for s in data.get('segments', []):
        meter, rails = mean(_segment(s, 'meter'), 'W'), mean(_segment(s), 'W')
        battery = s.get('battery_current_ma', [])
        rows.append({'segment': s.get('id'), 'level': s.get('kind'), 'repeat': s.get('repeat'),
                     'meter': meter, 'rails': rails,
                     'battery_current_ma': battery, 'thermal_levels': s.get('thermal_levels', []),
                     'charger_supplied': bool(battery) and all(abs(v) <= 200 for v in battery)})
    def fit_rows(rows):
        good = [r for r in rows if r['meter']['value'] is not None and r['rails']['value'] is not None]
        fit = linear([r['rails']['value'] for r in good], [r['meter']['value'] for r in good])
        if 'undefined' in fit:
            return {'slope': undefined(fit['undefined'], 'W/W'), 'intercept': undefined(fit['undefined'], 'W')}
        error = t975(len(good)-2)*fit['slope_se']
        return {'slope': quantity(fit['slope'], 'W/W', {'kind': '95% interval',
                   'value': [fit['slope']-error, fit['slope']+error], 'n': len(good),
                   'method': 'OLS slope, t interval with n-2 degrees of freedom'}),
                'intercept': quantity(fit['intercept'], 'W'), 'residuals_W': fit['residuals'],
                'sources': [r.get('segments', r.get('segment')) for r in good]}
    level_means = []
    for repeat in sorted({r['repeat'] for r in rows if r['repeat'] is not None}):
        for level in ('idle', 'cpu', 'gpu', 'mixed'):
            members = [r for r in rows if r['repeat'] == repeat and r['level'] == level]
            expected = 7 if level == 'idle' else 2
            sources = [r['segment'] for r in members]
            def average(field):
                if len(members) != expected or any(r[field]['value'] is None for r in members):
                    return undefined('incomplete palindrome level; all scheduled segments required', 'W', sources)
                return mean([r[field]['value'] for r in members], 'W', sources)
            level_means.append({'repeat': repeat, 'level': level, 'segments': sources,
                'segment_count': len(members), 'expected_segment_count': expected,
                'meter': average('meter'), 'rails': average('rails'),
                'battery_current_ma': [v for r in members for v in r['battery_current_ma']],
                'thermal_levels': [v for r in members for v in r['thermal_levels']],
                'charger_supplied': len(members) == expected and all(r['charger_supplied'] for r in members)})
    repeat_fits = []
    for repeat in sorted({r['repeat'] for r in level_means}):
        levels = [r for r in level_means if r['repeat'] == repeat]
        repeat_fits.append({'repeat': repeat,
            'charger_supplied_fit': fit_rows([r for r in levels if r['charger_supplied']]),
            'all_levels_fit': fit_rows(levels)})
    charger_fit = fit_rows([r for r in level_means if r['charger_supplied']])
    all_fit = fit_rows(level_means)
    return {'levels': rows, 'charger_supplied_fit': fit_rows([r for r in rows if r['charger_supplied']]),
            'incomplete_reason': None if _defined(charger_fit['slope']) or _defined(all_fit['slope'])
                else 'palindrome_level_mean_fit_undefined',
            'all_levels_fit': fit_rows(rows), 'all_levels_label': 'includes battery assist/charging and missing battery reads',
            'palindrome_level_means': level_means,
            'palindrome_charger_supplied_fit': charger_fit,
            'palindrome_all_levels_fit': all_fit, 'palindrome_repeat_fits': repeat_fits,
            'palindrome_method': 'equal mean of the two segments per load level and repeat; '
                                 'idle uses all seven symmetrically placed segments per repeat'}


def m13(data):
    meter_lags, sampler_lags = [], []
    for edge in data.get('edges', []):
        if edge.get('meter_s') is not None:
            meter_lags.append((edge['meter_s']-edge['command_s'])*1000)
        if edge.get('sampler_s') is not None:
            sampler_lags.append((edge['sampler_s']-edge['command_s'])*1000)
    precision = statistics.stdev(meter_lags)/math.sqrt(len(meter_lags)) if len(meter_lags) > 1 else None
    sampler_captures = {e['capture'] for e in data.get('edges', [])
                        if e.get('capture') is not None and e.get('sampler_s') is not None}
    meter_mean, sampler_mean = mean(meter_lags, 'ms'), mean(sampler_lags, 'ms')
    complete = (len(meter_lags) >= 100 and _defined(meter_mean)
                and len(sampler_captures) >= 2 and _defined(sampler_mean))
    return {'meter_clock_fits': data.get('meter_fits', []), 'edge_table': data.get('edges', []),
            'incomplete_reason': None if complete else 'meter_or_sampler_edges_insufficient',
            'meter_edge_count': len(meter_lags), 'sampler_capture_count': len(sampler_captures),
            'meter_lag_mean': meter_mean, 'meter_lag_sd': sd(meter_lags, 'ms'),
            'sampler_lag_mean': sampler_mean, 'sampler_lag_sd': sd(sampler_lags, 'ms'),
            'meter_alignment_precision': quantity(precision, 'ms', {'kind': 'standard error', 'value': precision,
                  'n': len(meter_lags), 'method': 'edge lag standard deviation / sqrt(edge count)'}),
            'typical_sampler_bound': quantity(30., 'ms'),
            'precision_below_typical_bound': precision < 30 if precision is not None else None,
            'interpretation': 'precision comparison; power-path lag is retained, not subtracted as clock error'}


def m15(data):
    runs = data.get('runs', [])
    phases = sorted({'prefill', 'decode'} | {p for r in runs for p in r.get('phase_energy_j', {})})
    drifts, contrasts, ratios, duration_ratios = {}, {}, {}, {}
    for phase in phases:
        drifts[phase], contrasts[phase], ratios[phase], duration_ratios[phase] = {}, {}, {}, {}
        for w in ('R', 'A', 'B'):
            blocks = [[r['phase_energy_j'][phase] for r in runs if r.get('workload') == w and
                       r.get('block') == b and phase in r.get('phase_energy_j', {})] for b in ('start', 'end')]
            start, end = [mean(vals, 'J') for vals in blocks]
            if start['value'] is None or end['value'] is None:
                drift = undefined('missing start/end block', 'J')
            else:
                es = [q['uncertainty']['value'] for q in (start, end)]
                drift = quantity(end['value']-start['value'], 'J', {'kind': 'standard error',
                  'value': math.hypot(*es) if all(e is not None for e in es) else None,
                  'n': [len(v) for v in blocks], 'method': 'quadrature of start/end block mean standard errors'})
            drifts[phase][w] = drift
        for left, right in (('B', 'R'), ('A', 'R'), ('B', 'A')):
            a, b = drifts[phase][left], drifts[phase][right]
            es = [q['uncertainty']['value'] for q in (a, b)]
            contrasts[phase][f'{left}-{right}'] = (quantity(a['value']-b['value'], 'J',
                {'kind': 'standard error', 'value': math.hypot(*es) if all(e is not None for e in es) else None,
                 'n': [a['uncertainty']['n'], b['uncertainty']['n']], 'method': 'quadrature of workload drift standard errors'})
                if a['value'] is not None and b['value'] is not None else undefined('missing workload drift', 'J'))
        for w in ('R', 'A', 'B'):
            vals = [r['phase_energy_j'][phase] for r in runs if r.get('workload') == w and
                    r.get('block') in ('start', 'end') and phase in r.get('phase_energy_j', {})]
            ref = [r['phase_energy_j'][phase] for r in runs if r.get('workload') == 'R' and
                   r.get('block') in ('start', 'end') and phase in r.get('phase_energy_j', {})]
            ratios[phase][w] = (quantity(statistics.mean(vals)/statistics.mean(ref), 'ratio') if vals and ref and
                statistics.mean(ref) != 0 else undefined('missing or zero reference energy', 'ratio'))
            durations = [r.get('phase_duration_s', {}).get(phase) for r in runs if r.get('workload') == w
                         and r.get('block') in ('start', 'end')]
            ref_durations = [r.get('phase_duration_s', {}).get(phase) for r in runs if r.get('workload') == 'R'
                             and r.get('block') in ('start', 'end')]
            durations = [v for v in durations if v is not None]
            ref_durations = [v for v in ref_durations if v is not None]
            duration_ratios[phase][w] = (quantity(statistics.mean(durations)/statistics.mean(ref_durations), 'ratio')
                if durations and ref_durations and statistics.mean(ref_durations)>0
                else undefined('missing or zero reference phase duration', 'ratio'))
    complete = all(_defined(d) for workloads in drifts.values() for d in workloads.values())
    return {'drift_by_phase': drifts, 'drift_differences': contrasts, 'energy_ratios': ratios,
            'incomplete_reason': None if complete else 'workload_drift_undefined',
            'duration_ratios': duration_ratios,
            'undefined': 'no measured workload phase energies' if not any(r.get('phase_energy_j') for r in runs) else None,
            'run_table': runs, 'scaling_formula': 'max(1, E/E_ref, T/T_ref) until transfer passes for regime'}


FUNCTIONS = {'m1-capture-stop-line': m1, 'm2-long-wait': m2, 'm2b-short-baseline': m2b, 'm3-clock-rate': m3,
             'm4-contention-watts': m4, 'm5-gpu-rail': m5, 'm9-time-server': m9,
             'm10-rails-vs-wall': m10, 'm13-meter-edges': m13,
             'm14-meter-idle-power': m14, 'm15-drift-transfer': m15}
