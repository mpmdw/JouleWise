#!/usr/bin/env python3
"""Stdlib-only R24 synthetic artifact audit and pair-mean table builder.

Reads only named local synthetic files. No product/runtime/data imports.
"""
import csv
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'r24-c14-confirm'
KEYS = ('mechanism', 'bar_p', 'member_p', 'tau', 'trend')
DESIGNS = ('oracle8', 'C10', 'C11', 'C12', 'C13', 'C14')
RULES = ('maximum', 'rank05', 'literal38')
HORIZONS = ('fixed_after_C14', 'after_stop')
SUFFIXES = ('estimate', 'lo', 'hi')


def read(name):
    with (HERE/name).open(newline='') as stream:
        return list(csv.DictReader(stream))


def write(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def key(row):
    return tuple(row[k] for k in KEYS)


def binomial_tail(n, p, minimum):
    return math.fsum(math.comb(n, k)*p**k*(1-p)**(n-k) for k in range(minimum, n+1))


def audit():
    metadata = json.loads((HERE/f'{PREFIX}-metadata-sol1.json').read_text())
    for hashes in ('source_sha256', 'input_sha256', 'output_sha256'):
        for name, digest in metadata[hashes].items():
            assert '/' not in name and name not in ('.', '..')
            assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == digest, name
    assert metadata['seed'] == 202611082201 and metadata['batch'] == 2000
    assert metadata['suffix_seed_sequence'] == [202611082201, 11, 12]
    assert metadata['extension_seed_sequence'] == [202611082201, 13, 14]
    assert metadata['trials_per_setting'] == 100_000 and len(metadata['settings']) == 72
    assert metadata['caps'] == [10, 11, 12, 13, 14]
    assert metadata['designs'] == list(DESIGNS) and metadata['rules'] == list(RULES)
    assert set(metadata['horizons']) == set(HORIZONS)
    replay = metadata['prior_replay']
    assert replay['equal_rows'] == dict(counts=288, scores=5184)
    assert replay['new_serialized_sha256'] == replay['prior_serialized_sha256']
    counts = read(f'{PREFIX}-counts-sol1.csv')
    scores = read(f'{PREFIX}-scores-sol1.csv')
    assert len(counts) == 432 and len(scores) == 7776
    count_lookup = {(key(r), r['design']): r for r in counts}
    score_lookup = {(key(r), r['horizon'], r['design'], r['rule'], r['pair']): r for r in scores}
    assert len(count_lookup) == len(counts) and len(score_lookup) == len(scores)
    grid = {tuple(str(v) for v in setting) for setting in metadata['settings']}
    assert {key(r) for r in counts} == grid
    assert {key(r) for r in scores} == grid
    ci_count = 0
    for row in counts + scores:
        for field, value in row.items():
            if field.endswith('_estimate'):
                prefix = field[:-9]
                estimate, lo, hi = map(float, (value, row[prefix+'_lo'], row[prefix+'_hi']))
                assert all(map(math.isfinite, (estimate, lo, hi)))
                assert lo <= estimate+1e-14 <= hi+1e-14, (field, row)
                ci_count += 1
        for field in ('fpr_estimate', 'future_pass_fpr_estimate', 'success_estimate', 'exact_success'):
            if field in row:
                assert 0 <= float(row[field]) <= 1
    exact_stops = {}
    for row in counts:
        q, e = float(row['bar_p']), float(row['member_p'])
        members = binomial_tail(56, 1-e, 39)**2
        cap = 8 if row['design'] == 'oracle8' else int(row['design'][1:])
        expected = members if cap == 8 else members*binomial_tail(cap, 1-q, 8)
        reserves = 0. if cap == 8 else math.fsum(1-binomial_tail(n, 1-q, 8) for n in range(8, cap))
        assert abs(float(row['exact_success'])-expected) < 2e-14
        assert abs(float(row['exact_reserves_attempted'])-reserves) < 2e-14
        assert abs(float(row['attempted_estimate'])-8-float(row['reserves_attempted_estimate'])) < 2e-14
        assert 0 <= float(row['reserves_attempted_estimate']) <= max(0, cap-8)
        assert 8 <= float(row['qualified_stop_estimate']) <= cap
        # Independent negative-binomial calculation for the stop, conditional
        # on structural completion. Member qualification is independent of L.
        stop_weights = [(8, 1.)] if cap == 8 else [
            (n, math.comb(n-1, 7)*(1-q)**8*q**(n-8)) for n in range(8, cap+1)]
        exact_stop = math.fsum(n*w for n, w in stop_weights)/math.fsum(w for _, w in stop_weights)
        exact_stops[key(row), row['design']] = exact_stop
        half = float(row['qualified_stop_hi'])-float(row['qualified_stop_estimate'])
        assert abs(float(row['qualified_stop_estimate'])-exact_stop) < 7*half/1.959963984540054+7/100_000
        assert int(row['trials']) == 100_000
        tolerance = 7*math.sqrt(expected*(1-expected)/100_000)+7/100_000
        assert abs(float(row['success_estimate'])-expected) < tolerance
        if 10 <= cap < 14:
            nxt = count_lookup[key(row), f'C{cap+1}']
            assert int(nxt['qualified']) >= int(row['qualified'])
            assert float(nxt['reserves_attempted_estimate']) >= float(row['reserves_attempted_estimate'])
    for row in scores:
        assert row['design'] in DESIGNS and row['rule'] in RULES and row['horizon'] in HORIZONS
        assert row['pair'] in ('spam_filter_update', 'bank_transfer_2', 'pair_mean')
        other_horizon = HORIZONS[1-HORIZONS.index(row['horizon'])]
        other = score_lookup[key(row), other_horizon, row['design'], row['rule'], row['pair']]
        for field in ('threshold', 'delta_threshold_oracle', 'delta_threshold_C10', 'iid_reference'):
            for suffix in SUFFIXES:
                assert row[field+'_'+suffix] == other[field+'_'+suffix]
        if float(row['trend']) == 0:
            for field in row:
                if field != 'horizon':
                    assert row[field] == other[field], (field, row)
        elif row['horizon'] == 'fixed_after_C14':
            assert float(row['fpr_estimate']) > float(other['fpr_estimate'])
            assert float(row['future_pass_fpr_estimate']) > float(other['future_pass_fpr_estimate'])
        if row['pair'] == 'pair_mean':
            pairs = [score_lookup[key(row), row['horizon'], row['design'], row['rule'], p]
                     for p in ('spam_filter_update', 'bank_transfer_2')]
            for field in ('fpr', 'future_pass_fpr', 'threshold', 'delta_threshold_oracle',
                          'delta_future_pass_oracle', 'population_delta_future_pass_C10'):
                assert abs(float(row[field+'_estimate'])
                           - math.fsum(float(p[field+'_estimate']) for p in pairs)/2) < 2e-14
        if row['mechanism'] != 'hot_correlated' or float(row['tau']) == 0:
            for suffix in SUFFIXES:
                if row['mechanism'] != 'hot_correlated':
                    assert row['fpr_'+suffix] == row['future_pass_fpr_'+suffix]
                else:
                    assert abs(float(row['fpr_'+suffix])-float(row['future_pass_fpr_'+suffix])) < 2e-14
        if row['design'] != 'oracle8':
            c10_count = count_lookup[key(row), 'C10']
            assert int(row['common_with_C10']) == int(c10_count['qualified'])
            for field in ('delta_threshold_C10', 'delta_future_pass_C10'):
                assert all(float(row[field+'_'+s]) == 0 for s in SUFFIXES)
        oracle = score_lookup[key(row), row['horizon'], 'oracle8', row['rule'], row['pair']]
        c10 = score_lookup[key(row), row['horizon'], 'C10', row['rule'], row['pair']]
        for field, reference in (('population_delta_future_pass_oracle', oracle),
                                 ('population_delta_future_pass_C10', c10)):
            a, b = float(row['future_pass_fpr_estimate']), float(reference['future_pass_fpr_estimate'])
            half = float(row['future_pass_fpr_hi'])-a + float(reference['future_pass_fpr_hi'])-b
            for suffix, expected in zip(SUFFIXES, (a-b, a-b-half, a-b+half)):
                assert abs(float(row[field+'_'+suffix])-expected) < 2e-14
    table = []
    for row in scores:
        if row['pair'] != 'pair_mean':
            continue
        count = count_lookup[key(row), row['design']]
        joined = {k: v for k, v in row.items() if k != 'pair'}
        joined.update({k: v for k, v in count.items() if k not in KEYS + ('design',)})
        stop = exact_stops[key(row), row['design']]
        cap = 8 if row['design'] == 'oracle8' else int(row['design'][1:])
        joined.update(exact_qualified_stop=stop,
                      exact_T1_mean=15 if row['horizon'] == 'fixed_after_C14' else stop+1,
                      T1_min=15 if row['horizon'] == 'fixed_after_C14' else 9,
                      T1_max=15 if row['horizon'] == 'fixed_after_C14' else cap+1)
        table.append(joined)
    assert len(table) == 2592
    table_path = HERE/f'{PREFIX}-table-sol1.csv'
    write(table_path, table)
    comparisons = []
    for horizon in HORIZONS:
        for trend in ('0.0', '0.05'):
            for rule in RULES:
                for cap in ('C13', 'C14'):
                    subset = [r for r in table if (r['horizon'], r['trend'], r['rule'], r['design'])
                              == (horizon, trend, rule, cap)]
                    assert len(subset) == 36
                    field = 'population_delta_future_pass_C10'
                    delta = [float(r[field+'_estimate']) for r in subset]
                    comparisons.append(dict(horizon=horizon, trend=float(trend), rule=rule, design=cap,
                        settings=len(subset), min_delta=min(delta), max_delta=max(delta),
                        positive_points=sum(d > 0 for d in delta),
                        positive_intervals=sum(float(r[field+'_lo']) > 0 for r in subset),
                        negative_intervals=sum(float(r[field+'_hi']) < 0 for r in subset)))
    receipt = dict(count_rows=len(counts), score_rows=len(scores), joined_rows=len(table),
        checked_intervals=ci_count, prior_replay=replay, comparisons=comparisons,
        scope='Synthetic-only artifact validation; both pairs, both calendars, all 72 settings. No hardware validation.',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        derived_sha256={table_path.name: hashlib.sha256(table_path.read_bytes()).hexdigest()})
    (HERE/f'{PREFIX}-audit-sol1.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))
    return receipt


if __name__ == '__main__':
    audit()
