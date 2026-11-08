"""Lead ruling R22-3 (RUN_STATE 234): printed balance check by condition.

Exclusions and flags per member-second are compared benign against sabotage, and per task pair,
against the exposure-adjusted expectation. The result is PRINTED and DISCLOSED; it gates nothing and
selects nothing (``status: print_only``). Pure functions over desk records.

Events of a member = its distinct flags + its calibration exclusions (contention codes included as
disclosed events: R22-1 makes them disclosure-only, not absent). Exposure = the member's span in
seconds (the R22-1 contention span, else the episode's gross latency).
"""
from __future__ import annotations

import math


def _exposure_s(record):
    span = (record.get('contention') or {}).get('span_s')
    if type(span) in (int, float) and math.isfinite(span) and span > 0:
        return float(span)
    latency = record.get('gross_latency_s')
    if type(latency) in (int, float) and math.isfinite(latency) and latency > 0:
        return float(latency)
    return None


def _events(record):
    return len(set(record.get('flags') or ())) + len(set(record.get('calibration_exclusions') or ()))


def _two_sided_binomial_p(k, n, p):
    """Exact two-sided p-value (sum of outcomes no more probable than the observed one)."""
    if n == 0 or not 0 < p < 1:
        return None
    pmf = [math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(n + 1)]
    return min(1.0, sum(x for x in pmf if x <= pmf[k] * (1 + 1e-9)))


def _group(records):
    exposure = sum(r['_exposure'] for r in records)
    events = sum(r['_events'] for r in records)
    return {'members': len(records), 'exposure_s': exposure, 'events': events,
            'rate_per_member_hour': (events / exposure * 3600) if exposure > 0 else None}


def balance_check(records):
    """The by-condition and by-pair balance of exclusions + flags per member-second (print only)."""
    rows, missing = [], []
    for record in records:
        exposure = _exposure_s(record)
        if exposure is None or record.get('condition') not in ('benign', 'sabotage'):
            missing.append(record.get('id'))
            continue
        rows.append({**record, '_exposure': exposure, '_events': _events(record)})
    total = _group(rows)
    pooled = (total['events'] / total['exposure_s']) if total['exposure_s'] else None

    def describe(subset):
        group = _group(subset)
        expected = None if pooled is None else pooled * group['exposure_s']
        group['expected_events'] = expected
        group['observed_over_expected'] = (group['events'] / expected) if expected else None
        return group

    by_condition = {c: describe([r for r in rows if r['condition'] == c]) for c in ('benign', 'sabotage')}
    by_pair = {}
    for pair in sorted({r.get('task_pair') for r in rows if r.get('task_pair')}):
        by_pair[pair] = {c: describe([r for r in rows if r.get('task_pair') == pair and r['condition'] == c])
                         for c in ('benign', 'sabotage')}
    benign, sabotage = by_condition['benign'], by_condition['sabotage']
    p_value = None
    if benign['exposure_s'] > 0 and sabotage['exposure_s'] > 0 and total['events'] > 0:
        # conditional on the total, the benign share of events is Binomial(N, benign exposure share)
        p_value = _two_sided_binomial_p(benign['events'], total['events'],
                                        benign['exposure_s'] / total['exposure_s'])
    return {'status': 'print_only', 'authority': 'RUN_STATE 234 R22-3', 'disclosed': True,
            'basis': 'exclusions + flags per member-second against the exposure-adjusted pooled expectation',
            'total': {**total, 'expected_rate_per_member_hour': None if pooled is None else pooled * 3600},
            'by_condition': by_condition, 'by_pair': by_pair,
            'benign_vs_sabotage': {'exact_binomial_p': p_value,
                                   'rate_ratio_sabotage_over_benign': (
                                       (sabotage['rate_per_member_hour'] / benign['rate_per_member_hour'])
                                       if benign['rate_per_member_hour'] and sabotage['rate_per_member_hour'] is not None
                                       else None)},
            'members_without_exposure_or_condition': missing}


def lines(report):
    """The printed rows of the balance check."""
    out = []
    for name, group in report['by_condition'].items():
        out.append(f"balance {name}: members={group['members']} exposure_s={group['exposure_s']:.0f} "
                   f"events={group['events']} expected={group['expected_events'] if group['expected_events'] is None else round(group['expected_events'], 3)}")
    for pair, groups in report['by_pair'].items():
        for name, group in groups.items():
            out.append(f"balance {pair}/{name}: members={group['members']} events={group['events']} "
                       f"exposure_s={group['exposure_s']:.0f}")
    out.append('balance benign-vs-sabotage: ' + str(report['benign_vs_sabotage']) + ' (print only)')
    return out
