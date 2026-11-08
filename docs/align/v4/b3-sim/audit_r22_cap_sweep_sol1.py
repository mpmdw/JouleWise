#!/usr/bin/env python3
"""Stdlib-only audit and compact joined tables for the synthetic cap sweep.

Run with supported Python 3.13; no NumPy, product runtime, measurement inputs
or coordination-state access. Reads only the explicitly named local synthetic
artifacts and source files bound by the simulation metadata.
"""
import csv
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = 'r22-cap-sweep'
KEYS = ('mechanism', 'bar_p', 'member_p', 'tau', 'trend')
DESIGNS = ('oracle8', 'C10', 'C11', 'C12')
RULES = ('maximum', 'rank05', 'literal38')


def read(name):
    with (HERE/name).open(newline='') as stream:
        return list(csv.DictReader(stream))


def key(row):
    return tuple(row[k] for k in KEYS)


def binomial_tail(n, p, minimum):
    return math.fsum(math.comb(n, k)*p**k*(1-p)**(n-k) for k in range(minimum, n+1))


def audit():
    metadata = json.loads((HERE/f'{PREFIX}-metadata-sol1.json').read_text())
    for hashes in ('source_sha256', 'output_sha256'):
        for name, digest in metadata[hashes].items():
            assert '/' not in name and name not in ('.', '..')
            assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == digest, name
    assert metadata['seed'] == 202611082201 and metadata['batch'] == 2000
    assert metadata['trials_per_setting'] == 100_000
    assert len(metadata['settings']) == 72
    replay = metadata['original_replay']
    assert replay['equal_numeric_fields'] == 17_568, replay
    assert replay['new_serialized_sha256'] == replay['original_serialized_sha256']
    counts = read(f'{PREFIX}-counts-sol1.csv')
    scores = read(f'{PREFIX}-scores-sol1.csv')
    assert len(counts) == 288 and len(scores) == 5184
    count_lookup = {(key(r), r['design']): r for r in counts}
    score_lookup = {(key(r), r['horizon'], r['design'], r['rule'], r['pair']): r for r in scores}
    assert len(count_lookup) == len(counts) and len(score_lookup) == len(scores)
    ci_count = 0
    for row in counts + scores:
        for field, value in row.items():
            if field.endswith('_estimate'):
                prefix = field[:-9]
                estimate, lo, hi = map(float, (value, row[prefix+'_lo'], row[prefix+'_hi']))
                assert all(map(math.isfinite, (estimate, lo, hi))), (field, row)
                assert lo <= estimate+1e-14 <= hi+1e-14, (field, row)
                ci_count += 1
        for field in ('fpr_estimate', 'future_pass_fpr_estimate', 'success_estimate', 'exact_success'):
            if field in row:
                assert 0 <= float(row[field]) <= 1
    for r in counts:
        q, e = float(r['bar_p']), float(r['member_p'])
        members = binomial_tail(56, 1-e, 39)**2
        cap = 8 if r['design'] == 'oracle8' else int(r['design'][1:])
        expected = members if cap == 8 else members*binomial_tail(cap, 1-q, 8)
        reserves = 0. if cap == 8 else math.fsum(1-binomial_tail(n, 1-q, 8) for n in range(8, cap))
        assert abs(float(r['exact_success'])-expected) < 2e-14
        assert abs(float(r['exact_reserves_attempted'])-reserves) < 2e-14
        assert abs(float(r['attempted_estimate'])-8-float(r['reserves_attempted_estimate'])) < 2e-14
        assert 0 <= float(r['reserves_attempted_estimate']) <= max(0, cap-8)
        tolerance = 7*math.sqrt(expected*(1-expected)/100_000)+7/100_000
        assert abs(float(r['success_estimate'])-expected) < tolerance
        if cap in (10, 11):
            nxt = count_lookup[key(r), f'C{cap+1}']
            assert int(nxt['qualified']) >= int(r['qualified'])
            assert float(nxt['reserves_attempted_estimate']) >= float(r['reserves_attempted_estimate'])
    for r in scores:
        if r['pair'] == 'pair_mean':
            for field in ('fpr_estimate', 'future_pass_fpr_estimate', 'threshold_estimate',
                          'delta_threshold_oracle_estimate', 'delta_future_pass_oracle_estimate'):
                pairs = [score_lookup[key(r), r['horizon'], r['design'], r['rule'], p]
                         for p in ('spam_filter_update', 'bank_transfer_2')]
                assert abs(float(r[field])-math.fsum(float(p[field]) for p in pairs)/2) < 2e-14
        if r['mechanism'] != 'hot_correlated' or float(r['tau']) == 0:
            for suffix in ('estimate', 'lo', 'hi'):
                # At tau=0, differing mixture weights are algebraically
                # irrelevant but can round by an ulp. Independent mechanisms
                # use exactly the same arithmetic in the two populations.
                if r['mechanism'] != 'hot_correlated':
                    assert r['fpr_'+suffix] == r['future_pass_fpr_'+suffix]
                else:
                    assert abs(float(r['fpr_'+suffix])-float(r['future_pass_fpr_'+suffix])) < 2e-14
        if r['design'] in ('C10', 'C11', 'C12'):
            # Every study qualifying by C10 has already stopped permanently.
            for prefix in ('delta_threshold_C10', 'delta_future_pass_C10'):
                assert all(float(r[prefix+'_'+s]) == 0 for s in ('estimate', 'lo', 'hi'))
        if r['horizon'] == 'after_C12':
            old = score_lookup[key(r), 'legacy_C10', r['design'], r['rule'], r['pair']]
            if float(r['trend']) == 0:
                for field in r:
                    if field != 'horizon':
                        assert r[field] == old[field]
            else:
                for field in ('fpr_estimate', 'future_pass_fpr_estimate'):
                    assert float(r[field]) > float(old[field])
    table = []
    for r in scores:
        if r['horizon'] != 'after_C12' or r['pair'] != 'pair_mean':
            continue
        c = count_lookup[key(r), r['design']]
        oracle = score_lookup[key(r), 'after_C12', 'oracle8', r['rule'], 'pair_mean']
        c10 = score_lookup[key(r), 'after_C12', 'C10', r['rule'], 'pair_mean']
        row = {k: r[k] for k in KEYS}
        row.update(design=r['design'], rule=r['rule'], trials=c['trials'], qualified=c['qualified'])
        for field in ('success_estimate', 'success_lo', 'success_hi', 'exact_success',
                      'reserves_attempted_estimate', 'reserves_attempted_lo', 'reserves_attempted_hi',
                      'exact_reserves_attempted'):
            row[field] = c[field]
        for prefix in ('fpr', 'future_pass_fpr', 'delta_threshold_oracle', 'delta_future_pass_oracle',
                       'population_delta_future_pass_oracle'):
            for suffix in ('estimate', 'lo', 'hi'):
                row[prefix+'_'+suffix] = r[prefix+'_'+suffix]
        row.update(oracle_fpr_estimate=oracle['fpr_estimate'],
                   oracle_future_pass_fpr_estimate=oracle['future_pass_fpr_estimate'])
        # Cauchy difference interval over each cap's own qualification sample.
        a, b = float(r['future_pass_fpr_estimate']), float(c10['future_pass_fpr_estimate'])
        half = float(r['future_pass_fpr_hi'])-a + float(c10['future_pass_fpr_hi'])-b
        row.update(population_delta_future_pass_C10_estimate=a-b,
                   population_delta_future_pass_C10_lo=a-b-half,
                   population_delta_future_pass_C10_hi=a-b+half)
        table.append(row)
    table_path = HERE/f'{PREFIX}-table-sol1.csv'
    with table_path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(table)
    assert len(table) == 864
    availability = []
    for q in (.125, .25):
        for e in (.1, .2):
            members = binomial_tail(56, 1-e, 39)**2
            for cap in range(8, 15):
                availability.append(dict(bar_p=q, member_p=e, cap=cap,
                    exact_success=members*binomial_tail(cap, 1-q, 8),
                    exact_reserves_attempted=math.fsum(1-binomial_tail(n, 1-q, 8) for n in range(8, cap))))
    path = HERE/f'{PREFIX}-availability-sol1.csv'
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(availability[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(availability)
    receipt = dict(count_rows=len(counts), score_rows=len(scores), joined_rows=len(table),
        checked_intervals=ci_count, original_replay=replay,
        scope='Synthetic artifact validation only; all 72 settings and both pairs; no hardware validation.',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        derived_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (table_path, path)})
    (HERE/f'{PREFIX}-audit-sol1.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    audit()
