#!/usr/bin/env python3
"""Round-5 D1: independent stdlib replay; one pinned RC file, no data writes.

Only --write appends the aggregate row to the repository ledger. Custody is
hashed before loading, authenticated again before parsing, and rehashed in
finally. Embedded paths are inert. --repo-only never opens custody.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from decimal import Decimal
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import statistics
import subprocess

HERE = Path(__file__).absolute().parent
REPO = HERE.parents[2]
BASE = 'ffe8137beef723e06c381c91267df099f9665261'
SOURCE = Path('/Users/edr/jw-b5-custody/release-check-final-20261108T0942Z/recompute.json')
PIN = 'c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc'
RESULTS_PIN = 'fb5f81e8741532d79b059b2ca7c44b1c479f0f983c28527ab6e2511d7dfb6f55'
CELL = 'Qwen3-1.7B-4bit/prefill'
KEY = f'RC.dominance.common_mode[{CELL}].R_cm'
PRINTED = '1.99975'
FORMULA = (
    f'RC.members.ALPHA[*].{{E_j,r_j}}.prefill; RC.floors[{CELL}/comparative].'
    '{kept_units,shared_j}; d=(B1+B2-A1-A2)/2; local=sum(r_j)/2; '
    'point=max(max|d|,|mean(d)|+2.365*sampleSD(d)*sqrt(1+1/n)), n=8 '
    '(analysis plan section 5, df=7); numerator=max(point, all shared-sign/local-sign '
    'corner point floors); R_cm=numerator/point; independently cross-check full '
    f'RC.dominance.common_mode[{CELL}].{{numerator_j,denominator_j,R_cm,n}}'
)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_source(record):
    # Inspect only the authorized root and exact file, never their parents.
    if SOURCE.parent.is_symlink() or SOURCE.is_symlink():
        raise ValueError('custody symlink refused')
    record.update(path=str(SOURCE), expected_sha256=PIN, sha256_before=digest(SOURCE))
    if record['sha256_before'] != PIN:
        raise ValueError('RC hash mismatch before loading')
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('RC loaded bytes differ from pin; refuse parsing')
    return json.loads(raw)


def point(values):
    # Registered t for df=7, not a new or estimated constant.
    if len(values) != 8:
        raise ValueError('D1 replay expects eight kept quads')
    return max(max(map(abs, values)), abs(statistics.fmean(values)) +
               2.365 * statistics.stdev(values) * math.sqrt(1 + 1/len(values)))


def rederive(rc):
    floor = rc['floors'][CELL+'/comparative']
    members = rc['members']['ALPHA']
    values, local = [], []
    for unit in floor['kept_units']:
        quad = []
        for position in ('a1', 'b1', 'b2', 'a2'):
            hits = [v for k, v in members.items()
                    if '-prefill-' in k and k.endswith('-'+unit[-3:]+'-'+position)]
            if len(hits) != 1:
                raise ValueError('missing or ambiguous kept quad member')
            quad.append(hits[0])
        energy = [v['E_j']['prefill'] for v in quad]
        values.append((energy[1]+energy[2]-energy[0]-energy[3])/2)
        local.append(math.fsum(v['r_j']['prefill'] for v in quad)/2)
    shared = floor['shared_j']
    if len(shared) != len(values) or len(floor['local_j']) != len(local):
        raise ValueError('width count mismatch')
    if not all(math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
               for a, b in zip(local, floor['local_j'])):
        raise ValueError('member-derived local widths disagree')
    denominator = point(values)
    if denominator <= 0:
        raise ValueError('nonpositive denominator')
    numerator = denominator
    for common in (-1, 1):
        for signs in itertools.product((-1, 1), repeat=len(values)):
            corner = [v + common*s + sign*l
                      for v, s, sign, l in zip(values, shared, signs, local)]
            numerator = max(numerator, point(corner))
    actual = numerator/denominator
    stored = rc['dominance']['common_mode'][CELL]
    terms = Decimal(str(stored['numerator_j']))/Decimal(str(stored['denominator_j']))
    for own, source in ((numerator, stored['numerator_j']),
                        (denominator, stored['denominator_j']),
                        (actual, stored['R_cm']), (actual, float(terms))):
        if not math.isclose(own, source, rel_tol=1e-11, abs_tol=1e-12):
            raise ValueError('D1 real mismatch; report, do not repair')
    if stored['n'] != len(values):
        raise ValueError('D1 n mismatch')
    return actual, stored['R_cm']


def make_row(actual, source, fields):
    if any(abs(value-float(PRINTED)) > 0.000005 for value in (actual, source)):
        raise ValueError('D1 real mismatch at ledger precision')
    row = dict.fromkeys(fields, '')
    row.update(printed_value=PRINTED, **{'key/leaf': KEY}, source='RC sha256='+PIN,
               rederived_value=f'{actual:.5f}', match='within-rounding',
               note='RL-55 round 5 D1; five-decimal row; prior rows remain immutable; '
                    'source difference='+format(source-float(PRINTED), '.2g'),
               source_value=f'{source:.5f}', source_match='within-rounding',
               difference=format(actual-float(PRINTED), '.2g'), hand_check=FORMULA, paper1='print')
    return row


def prefix_bytes():
    return subprocess.run(['git', 'show', BASE+':docs/analysis/b5/rederivation.tsv'],
                          cwd=REPO, check=True, capture_output=True).stdout


def repository_check(current, prefix):
    if not current.startswith(prefix):
        raise ValueError('prior 1844 rows differ')
    rows = list(csv.DictReader(io.StringIO(current.decode()), delimiter='\t'))
    row = rows[1844]
    expected = {'printed_value': PRINTED, 'rederived_value': PRINTED, 'key/leaf': KEY,
                'match': 'within-rounding', 'source': 'RC sha256='+PIN,
                'difference': '-1.7e-06', 'paper1': 'print', 'hand_check': FORMULA}
    if any(row[k] != v for k, v in expected.items()):
        raise ValueError('D1 row metadata differs')
    if hashlib.sha256((HERE/'RESULTS.md').read_bytes()).hexdigest() != RESULTS_PIN:
        raise ValueError('RESULTS bytes changed')
    print(json.dumps({'mode': 'repository-only; custody arithmetic not rerun',
                      'prior_rows_byte_identical': True, 'physical_row': 1846,
                      'counts': dict(Counter(r['match'] for r in rows)), 'opened_custody': []}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--repo-only', action='store_true')
    args = parser.parse_args()
    if args.repo_only and args.write:
        parser.error('--repo-only cannot be combined with --write')
    prefix = prefix_bytes()
    target = HERE/'rederivation.tsv'
    current = target.read_bytes()
    if not current.startswith(prefix):
        raise ValueError('prior 1844 rows differ; stop before custody')
    if args.repo_only:
        repository_check(current, prefix)
        return
    fields = next(csv.reader(io.StringIO(prefix.decode()), delimiter='\t'))
    opened = {}
    try:
        actual, source = rederive(read_source(opened))
        row = make_row(actual, source, fields)
    finally:
        if 'sha256_before' in opened:
            opened['sha256_after'] = digest(SOURCE)
            print(json.dumps({'opened_custody': {'RC': opened}}, sort_keys=True))
            if opened['sha256_after'] != opened['sha256_before']:
                raise ValueError('RC changed during read')
    buffer = io.StringIO(newline='')
    csv.DictWriter(buffer, fields, delimiter='\t', lineterminator='\n').writerow(row)
    expected = prefix+buffer.getvalue().encode()
    if args.write and current == prefix:
        target.write_bytes(expected)
    elif not current.startswith(expected):
        raise ValueError('D1 row absent or differs; --write only appends to frozen round 4')
    print(json.dumps({'physical_row': 1846, 'printed_value': row['printed_value'],
                      'difference': row['difference'], 'match': row['match'],
                      'prior_rows_byte_identical': True}, sort_keys=True))


if __name__ == '__main__':
    main()
