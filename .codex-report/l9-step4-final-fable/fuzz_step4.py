"""Independent randomized differential of classify_step4_exit + step_record at the head under review."""
import json, random, sys
sys.path.insert(0, '/home/user/JouleWise')
from joulewise.b5_analysis.steps import classify_step4_exit, step_record
from joulewise.b5_analysis import dry_run as d
T = json.load(open('/home/user/JouleWise/configs/analysis/b5/step4_reason_classes.json'))
C = d.refusal_classes()
r3, mask, tooling = set(T['r3']), [m for m in T['mask'] if m not in T['r3']], T['tooling'][:200]
pool = list(r3) + mask + tooling + ['syn_unlisted', '', 'KEPT_UNITS_BELOW_MINIMUM', 'kept_units_below_minimum ']
SPEC = {'cells': [
    {'cell_id': 't1', 'kind': 'absolute', 'condition_family_id': 'cell-target'},
    {'cell_id': 't2', 'kind': 'comparative', 'condition_family_id': 'cell-target'},
    {'cell_id': 'p1', 'kind': 'absolute', 'condition_family_id': 'cell-p42'},
    {'cell_id': 'p2', 'kind': 'comparative', 'condition_family_id': 'cell-p42-x'},
    {'cell_id': 'rp', 'kind': 'reported', 'condition_family_id': 'cell-p42'}]}
P42 = {'p1', 'p2'}
rng = random.Random(20261030)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
hist = {}
viol = 0
for i in range(N):
    cells = []
    for c in SPEC['cells']:
        refused = rng.random() < 0.4
        k = rng.choice([0, 0, 1, 1, 2, 3])
        reasons = [rng.choice(pool) for _ in range(k)]
        if rng.random() < 0.03: reasons = rng.choice([None, 'x', 5, [None], [1], {}])
        cell = {'cell_id': c['cell_id'], 'extractable': (not refused) if rng.random() > 0.02 else rng.choice([None, 0, 'false']),
                'refusal_reasons': reasons}
        if rng.random() < 0.02: del cell['refusal_reasons']
        cells.append(cell)
    report = {'cells': cells, 'spec_membership_refusals': [] if rng.random() > 0.05 else [{'bundle_id': 'b'}]}
    exit_status = rng.choice([0, 1, 1, 1, 1, 2])
    code = classify_step4_exit(exit_status, report, SPEC)
    registered = code if code == 'p42_floor_cells_only' else None
    if exit_status == 1:
        row = step_record('4', window='alpha', exit_status=1, classes=C, refusal_code=None if registered else (code if code != 'refused' else None), registered_exit=registered)
    else:
        row = step_record('4', window='alpha', exit_status=exit_status if exit_status else 0, classes=C,
                          refusal_code=None if exit_status == 0 else 'syn_x', registered_exit=None)
    hist[(exit_status, code, row.status)] = hist.get((exit_status, code, row.status), 0) + 1
    # Invariants
    refused_non_p42 = [c for c in cells if c['extractable'] is False and c['cell_id'] not in P42]
    omitted = bool(report['spec_membership_refusals'])
    bad = False
    if exit_status == 1:
        if code == 'refused' or code == 'ok': bad = True
        if code in C['outcome_class'] or row.status == 'outcome_class': bad = True
        if code == 'p42_floor_cells_only' and (refused_non_p42 or omitted): bad = True
        if row.status == 'ok' and code != 'p42_floor_cells_only': bad = True
        if code != 'p42_floor_cells_only' and row.status != 'tooling_refusal': bad = True
        if code == 'extraction_cell_r3_refusal' and not any(isinstance(c.get('refusal_reasons'), list) and any(r in r3 for r in c['refusal_reasons'] if isinstance(r, str)) for c in refused_non_p42): bad = True
        if code == 'extraction_cell_tooling_refusal' and any(isinstance(c.get('refusal_reasons'), list) and any(r in r3 for r in c['refusal_reasons'] if isinstance(r, str)) for c in refused_non_p42): bad = True
    if bad:
        viol += 1
        if viol <= 5: print('VIOLATION', exit_status, code, row.status, json.dumps(report)[:300])
print('N', N, 'violations', viol)
for k in sorted(hist, key=str): print(' ', k, hist[k])
