"""Synthetic totality probe for classify_step4_exit (L9-STEP4-OPUS-REV).

Random structured inputs; asserts every call returns exactly one registered
name and never raises. Synthetic data only.
"""
import itertools, json, random, sys
from collections import Counter
from pathlib import Path
from joulewise.b5_analysis.steps import classify_step4_exit

ROOT = Path(__file__).resolve().parents[2]
table = json.loads((ROOT/'configs/analysis/b5/dry_run_refusal_classes.json').read_text())
TOOL, OUT = set(table['tooling_refusal']), set(table['outcome_class'])
ALLOWED = {'ok', 'p42_floor_cells_only', 'refused'} | TOOL | OUT
rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
JUNK = [None, 0, 1, True, False, '', 'x', [], {}, 1.5, ['a'], {'a': 1}]
IDS = ['c-t', 'c-c', 'c-p42a', 'c-p42b', 'c-ref']
SPEC_CELLS = [{'cell_id': 'c-t', 'kind': 'absolute', 'condition_family_id': 'cell-target'},
              {'cell_id': 'c-c', 'kind': 'comparative', 'condition_family_id': 'cell-target'},
              {'cell_id': 'c-p42a', 'kind': 'absolute', 'condition_family_id': 'cell-p42'},
              {'cell_id': 'c-p42b', 'kind': 'comparative', 'condition_family_id': 'p42-x'},
              {'cell_id': 'c-ref', 'kind': 'reference', 'condition_family_id': 'ref-p42'}]
P42 = {'c-p42a', 'c-p42b'}

def maybe(v):
    return rng.choice(JUNK) if rng.random() < 0.05 else v

def spec():
    if rng.random() < 0.05: return rng.choice(JUNK)
    cells = [dict(c) for c in rng.sample(SPEC_CELLS, rng.randint(0, 5))]
    for c in cells:
        for k in list(c):
            c[k] = maybe(c[k])
        if rng.random() < 0.03: c.pop(rng.choice(list(c)))
    if cells and rng.random() < 0.05: cells.append(dict(cells[0]))
    return {'cells': maybe(cells)}

def report(sp):
    if rng.random() < 0.05: return rng.choice(JUNK)
    ids = [c.get('cell_id') for c in sp.get('cells', [])] if isinstance(sp, dict) and isinstance(sp.get('cells'), list) and all(isinstance(c, dict) for c in sp['cells']) else IDS
    if rng.random() < 0.1: ids = rng.sample(IDS, rng.randint(0, 5))
    cells = [{'cell_id': maybe(i), 'extractable': maybe(rng.random() < 0.7)} for i in ids]
    if cells and rng.random() < 0.05: cells.append(dict(cells[0]))
    r = {'spec_membership_refusals': maybe([] if rng.random() < 0.9 else [{'bundle_id': 'b'}]), 'cells': maybe(cells)}
    if rng.random() < 0.03: r.pop(rng.choice(list(r)))
    return r

def oracle(es, rep, sp):
    """Independent restatement of the ruling, for well-formed inputs only."""
    refused = {c['cell_id'] for c in rep['cells'] if c['extractable'] is False}
    p42 = {c['cell_id'] for c in sp['cells'] if c['kind'] in ('absolute', 'comparative') and 'p42' in c['condition_family_id'].split('-')}
    if not refused: return 'extraction_exit_without_refused_cell'
    return 'p42_floor_cells_only' if refused <= p42 else 'floor_cell_not_extractable'

counts, bad, checked = Counter(), [], 0
for n in range(200000):
    es = rng.choice([0, 1, 1, 1, 1, 2, 3, -1, True, None, '1', 1.0])
    sp = spec(); rep = report(sp)
    try:
        got = classify_step4_exit(es, rep, sp)
    except Exception as exc:  # totality failure
        bad.append(('raised', repr(exc), es)); continue
    counts[got] += 1
    if got not in ALLOWED: bad.append(('unregistered', got))
    if got == 'refused' and type(es) is int and es in (0, 1): bad.append(('refused_for_0_or_1', es))
    if type(es) is int and es == 1 and got not in ('refused', 'ok') and got not in ('p42_floor_cells_only',) and got not in TOOL | OUT:
        bad.append(('class', got))
    # Oracle comparison on well-formed, consistent, membership-clean inputs.
    if (type(es) is int and es == 1 and isinstance(rep, dict) and isinstance(sp, dict)
            and rep.get('spec_membership_refusals') == [] and isinstance(rep.get('cells'), list)
            and isinstance(sp.get('cells'), list)
            and all(isinstance(c, dict) and type(c.get('cell_id')) is str and c['cell_id'] and type(c.get('extractable')) is bool for c in rep['cells'])
            and all(isinstance(c, dict) and type(c.get('cell_id')) is str and c['cell_id'] and type(c.get('kind')) is str and type(c.get('condition_family_id')) is str for c in sp['cells'])):
        ids = [c['cell_id'] for c in rep['cells']]; sids = [c['cell_id'] for c in sp['cells']]
        if len(ids) == len(set(ids)) and len(sids) == len(set(sids)) and set(ids) == set(sids):
            checked += 1
            if got != oracle(es, rep, sp): bad.append(('oracle', got, oracle(es, rep, sp)))
print('codes:', dict(sorted(counts.items())))
print('oracle-checked well-formed cases:', checked)
print('tooling codes returned:', sorted(set(counts) & TOOL))
print('outcome codes returned:', sorted(set(counts) & OUT))
print('failures:', len(bad), bad[:5])
sys.exit(1 if bad else 0)
