"""Prospective R03 procedure; no installed alpha, transfer factor or energy floor.

See docs/align/v4/W1-BLOCKERS-sol.md. All numerical policy inputs require lead
adoption. A descriptive export without that policy remains PENDING.
"""
from functools import lru_cache
import json
import math
import random
import statistics

METHOD = 'session_student_t_predictive_v1'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


@lru_cache(maxsize=128)
def critical(alpha, df):
    """Two-sided Student-t quantile by incomplete-beta tail inversion."""
    from joulewise.align.apple.thermal_desk import _ibeta
    lo, hi = 0., 1.
    def tail(x):
        return _ibeta(df/2, .5, df/(df+x*x))
    while tail(hi) > alpha:
        hi *= 2
    for _ in range(80):
        mid = (lo+hi)/2
        if tail(mid) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def policy_checks(policy):
    from joulewise.align.apple.v4_registration import is_digest
    if (not isinstance(policy, dict) or policy.get('method') != METHOD
            or policy.get('selection') != 'one_prespecified_pair_per_session'
            or type(policy.get('series_alpha')) not in (int, float)
            or not 0 < policy['series_alpha'] <= .15
            or type(policy.get('d_transfer_factor')) not in (int, float)
            or not math.isfinite(policy['d_transfer_factor']) or policy['d_transfer_factor'] < 1
            or not is_digest(policy.get('d_configuration_sha256'))
            or not is_digest(policy.get('r1_configuration_sha256'))
            or not is_digest(policy.get('transfer_justification_sha256'))
            or policy.get('r1_D_qualification') != 'adjacent_matched_predecessor_screen_only'
            or type(policy.get('seed')) is not int
            or type(policy.get('simulations')) is not int or not 1000 <= policy['simulations'] <= 100000):
        raise ValueError('U3 requires explicit predictive/OC/transfer policy (series budget <=15%)')
    windows = policy.get('checks_by_window')
    if not isinstance(windows, dict) or not windows or 'W1' not in windows:
        raise ValueError('U3 requires the final prospective window/comparison roster')
    for name, counts in windows.items():
        if (not isinstance(name, str) or not name.strip() or not isinstance(counts, dict)
                or set(counts) != {'30B', 'D'}
                or any(type(n) is not int or n < 0 for n in counts.values())
                or sum(counts.values()) < 1):
            raise ValueError('U3 invalid window comparison counts')
    counts = {model: sum(w[model] for w in windows.values()) for model in ('30B', 'D')}
    if not all(counts.values()) or sum(counts.values()) > 10000:
        raise ValueError('U3 requires both populations and bounded comparison count')
    return counts


def relative_pairs(pairs):
    if not isinstance(pairs, list):
        raise ValueError('U3 replay pairs must be a list')
    relative, seen = [], set()
    for pair in pairs:
        if not isinstance(pair, dict):
            raise ValueError('U3 replay pair must be an object')
        ordinals, values = pair.get('ordinals', []), pair.get('energies_j', [])
        qualification = (pair.get('population') == 'D' and pair.get('phase') == 'R1'
                         and pair.get('qualification_only') is True)
        if (pair.get('token_identical') is not True or len(ordinals) != 2
                or any(type(v) is not int or v < 1 for v in ordinals)
                or ordinals[1]-ordinals[0] < (1 if qualification else 3) or len(values) != 2
                or any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in values)
                or not isinstance(pair.get('session'), str) or not pair['session'].strip()):
            raise ValueError('U3 requires separated-ordinal within-session token-identical positive-energy pairs')
        key = (pair['session'], *ordinals)
        if key in seen:
            raise ValueError('duplicate U3 replay pair')
        seen.add(key)
        relative.append((values[1]-values[0])/statistics.fmean(values))
    if len(relative) < 2:
        raise ValueError('U3 requires at least two eligible replay pairs')
    return relative


def prediction(pairs, policy):
    from joulewise.align.apple.v4_registration import is_digest
    counts = policy_checks(policy)
    rel = relative_pairs(pairs)
    pilot, d, sessions = [], [], set()
    for pair, value in zip(pairs, rel):
        clock = pair.get('clock_difference_fraction')
        if (pair.get('eligible') is not True or type(clock) not in (int, float)
                or not math.isfinite(clock) or not 0 <= clock <= .005
                or not is_digest(pair.get('source_sha256'))
                or not is_digest(pair.get('configuration_sha256'))):
            raise ValueError('U3 requires eligible identity/clock/configuration/source evidence')
        if pair.get('population') == '30B' and pair.get('phase') == 'pilot':
            if pair['session'] in sessions:
                raise ValueError('U3 needs one prespecified pair per independent pilot session')
            sessions.add(pair['session'])
            pilot.append(value)
        elif pair.get('population') == 'D' and pair.get('phase') == 'R1':
            if pair.get('qualification_only') is not True:
                raise ValueError('U3 R1 D pair is a transfer screen, never a separated-session scale estimate')
            if pair['configuration_sha256'] != policy['r1_configuration_sha256']:
                raise ValueError('U3 R1 D configuration differs from the signed transfer source')
            d.append(value)
        else:
            raise ValueError('U3 training permits only 30B pilots and R1 D qualification; never W1')
    if len(pilot) < 3 or len(d) != 1:
        raise ValueError('U3 requires >=3 independent pilot sessions and exactly one R1 D replay pair')
    sd, mean = statistics.stdev(pilot), statistics.fmean(pilot)
    if sd <= 0:
        raise ValueError('U3 zero observed scale cannot qualify a finite predictive bar')
    alpha = policy['series_alpha']/sum(counts.values())
    t = critical(alpha, len(pilot)-1)
    width = t*sd*math.sqrt(1+1/len(pilot))
    bar = abs(mean)+width
    return dict(n=len(pilot), df=len(pilot)-1, mean_rel=mean, s_rel_sample=sd,
                series_comparisons=sum(counts.values()), pair_alpha=alpha,
                t_critical=t, predictive_half_width=width,
                predictive_interval=[mean-width, mean+width], relative_bar_30B=bar,
                relative_bar_D=bar*policy['d_transfer_factor'],
                d_qualification_relative=d[0],
                d_qualification_pass=abs(d[0]) <= bar*policy['d_transfer_factor'])


def operating_characteristics(policy, pred):
    """Regenerate calibration in each replicate; reuse it over the whole series.

    Standardized generators examine model misspecification, correlation and
    D scale transfer. Rates are diagnostics, never a simulated admission bit.
    """
    policy_checks(policy)
    return json.loads(_oc_cached(canonical(policy), pred['n'], pred['t_critical']))


@lru_cache(maxsize=16)
def _oc_cached(serialized_policy, n, k):
    policy = json.loads(serialized_policy)
    reps = policy['simulations']
    factor = policy['d_transfer_factor']
    scenarios = []
    # Each scenario is a fully specified part of this versioned procedure.
    for name, law, rho, d_scale, shift in (
            ('normal_iid', 'normal', 0., 1., 0.),
            ('normal_window_rho_0.5', 'normal', .5, 1., 0.),
            ('normal_series_rho_0.9', 'normal', .9, 1., 0.),
            ('normal_correlated_training_rho_0.5', 'normal', 0., 1., 0.),
            ('student_t3_unit_variance', 't3', 0., 1., 0.),
            ('centered_exponential', 'skew', 0., 1., 0.),
            ('D_scale_at_assumed_factor', 'normal', 0., factor, 0.),
            ('D_scale_twice_assumed_factor', 'normal', 0., 2*factor, 0.),
            ('D_drift_two_pilot_sd', 'normal', 0., 1., 2.),
            ('D_drift_eight_pilot_sd', 'normal', 0., 1., 8.)):
        rng = random.Random(policy['seed'])
        failures = {w: 0 for w in policy['checks_by_window']}
        pair_fail = total = series_fail = 0
        population_fail = {'30B': 0, 'D': 0}
        def draw():
            if law == 't3':
                return rng.gauss(0, 1)/math.sqrt(sum(rng.gauss(0, 1)**2 for _ in range(3)))
            return rng.expovariate(1)-1 if law == 'skew' else rng.gauss(0, 1)
        for _ in range(reps):
            training_common = draw()
            sample = [(training_common+draw())/math.sqrt(2) if name == 'normal_correlated_training_rho_0.5'
                      else draw() for _ in range(n)]
            bound = abs(statistics.fmean(sample))+k*statistics.stdev(sample)*math.sqrt(1+1/n)
            common = draw()
            any_fail = False
            for window, roster in policy['checks_by_window'].items():
                window_common = common if rho == .9 else draw()
                lost = False
                for model, count in roster.items():
                    for _ in range(count):
                        value = math.sqrt(rho)*window_common+math.sqrt(1-rho)*draw()
                        limit = bound
                        if model == 'D':
                            value, limit = value*d_scale+shift, bound*factor
                        bad = abs(value) > limit
                        pair_fail += bad
                        population_fail[model] += bad
                        total += 1
                        lost |= bad
                failures[window] += lost
                any_fail |= lost
            series_fail += any_fail
        rate = series_fail/reps
        scenarios.append(dict(name=name, series_failures=series_fail,
                              series_failure_rate=rate,
                              monte_carlo_se=math.sqrt(rate*(1-rate)/reps),
                              pair_failure_rate=pair_fail/total,
                              population_pair_failure_rates={model: population_fail[model]/(reps*count)
                                  for model, count in policy_checks(policy).items()},
                              window_failure_rates={w: f/reps for w, f in failures.items()}))
    return canonical(dict(simulations=reps, seed=policy['seed'], scenarios=scenarios,
                limitation='Model sensitivity only; no hardware validation or D transfer guarantee. '
                            'Conditional rates for the realized small-sample scale can exceed marginal rates.'))


def derive(pairs, source_sha256, policy):
    from joulewise.align.apple.v4_registration import digest
    pred = prediction(pairs, policy)
    payload = dict(schema='joulewise.align_v4.u3_bar.v2', pairs=pairs,
                   source_sha256=source_sha256, policy=policy, prediction=pred,
                   oc=operating_characteristics(policy, pred))
    return {**payload, 'derivation_sha256': digest(canonical(payload).encode()),
            'status': 'PENDING', 'lead_signature': None, 'independent_gate': None}


@lru_cache(maxsize=16)
def validate_cached(serialized):
    from scripts.align_v4_kit import valid_lead_signature
    from joulewise.align.apple.v4_registration import is_digest
    bar = json.loads(serialized)
    if (bar.get('schema') != 'joulewise.align_v4.u3_bar.v2' or bar.get('status') != 'registered'
            or not valid_lead_signature(bar.get('lead_signature'))):
        raise ValueError('U3 PENDING predictive derivation or lead signature')
    if bar.get('policy', {}).get('transfer_justification_sha256') not in bar.get('source_sha256', {}).values():
        raise ValueError('U3 transfer justification source missing')
    expected = derive(bar['pairs'], bar['source_sha256'], bar['policy'])
    for key in ('prediction', 'oc', 'derivation_sha256'):
        if bar.get(key) != expected[key]:
            raise ValueError('U3 derived arithmetic/OC/digest drift')
    gate = bar.get('independent_gate') or {}
    if (not isinstance(gate, dict) or gate.get('verdict') != 'ADMIT' or not is_digest(gate.get('sha256'))
            or not isinstance(gate.get('path'), str) or not gate['path'].startswith('docs/align/v4/')
            or gate.get('derivation_sha256') != bar['derivation_sha256']):
        raise ValueError('U3 requires independent ADMIT bound to the exact derivation')
    if not bar['prediction']['d_qualification_pass']:
        raise ValueError('U3 R1 D transfer qualification failed; no W1 admission')
    return True
