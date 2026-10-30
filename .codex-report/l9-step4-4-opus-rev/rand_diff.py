import json, random, sys, importlib
def load(root):
    for m in [k for k in sys.modules if k.startswith('joulewise')]: del sys.modules[m]
    sys.path.insert(0, root)
    steps = importlib.import_module('joulewise.b5_analysis.steps')
    dr = importlib.import_module('joulewise.b5_analysis.dry_run')
    sys.path.pop(0)
    return steps, dr
t = json.load(open(sys.argv[2] + '/configs/analysis/b5/step4_reason_classes.json'))
pool = t['mask'] + t['tooling'] + ['syn_unlisted', 'fixed_n_plan_incomplete']
ADDED = {'window_evidence_precheck_missing', 'campaign_cooldown_evidence_missing', 'idle_window_suspect'}
pool += list(ADDED) * 200 + t['r3'] * 50
SPEC = {'cells': [{'cell_id': 'a', 'kind': 'absolute', 'condition_family_id': 'cell-x'},
                  {'cell_id': 'b', 'kind': 'comparative', 'condition_family_id': 'cell-y'},
                  {'cell_id': 'p', 'kind': 'absolute', 'condition_family_id': 'cell-p42'},
                  {'cell_id': 'q', 'kind': 'comparative', 'condition_family_id': 'z-p42-w'}]}
rng = random.Random(20261030)
cases = []
for _ in range(200000):
    cells = []
    for c in SPEC['cells']:
        refused = rng.random() < 0.5
        cells.append({'cell_id': c['cell_id'], 'extractable': not refused,
                      'refusal_reasons': [rng.choice(pool) for _ in range(rng.randint(0, 3))] if refused else []})
    cases.append((rng.choice([0, 1, 1, 1, 2]), {'spec_membership_refusals': [], 'cells': cells}))
res = {}
for label, root in (('before', sys.argv[1]), ('after', sys.argv[2])):
    steps, dr = load(root)
    assert root in steps.__file__, steps.__file__
    out = []
    for ex, rep in cases:
        c = steps.classify_step4_exit(ex, rep, SPEC)
        reg = c if (ex == 1 and c == 'p42_floor_cells_only') else None
        code = None if (reg or c == 'ok' or (c == 'refused')) else c
        rec = steps.step_record('4', window='alpha', exit_status=ex, classes=dr.refusal_classes(),
                                refusal_code=code, registered_exit=reg)
        out.append((c, rec.status))
    res[label] = out
from collections import Counter
diff = Counter(); bad = 0
for (ex, rep), b, a in zip(cases, res['before'], res['after']):
    if b != a:
        diff[(ex, b, a)] += 1
        tgt = [r for cell in rep['cells'] if not cell['extractable'] and 'p42' not in {'p': 'p42', 'q': 'p42'}.get(cell['cell_id'], '') for r in cell['refusal_reasons']]
        if not (ex == 1 and b[0] == 'extraction_cell_tooling_refusal' and a[0] == 'extraction_cell_r3_refusal' and set(tgt) & ADDED):
            bad += 1
print('changed', dict(diff)); print('unexpected changes', bad)
print('after exit1 classes', Counter(a for (ex, _), a in zip(cases, res['after']) if ex == 1))
print('after statuses for exit1 ok/outcome', sum(1 for (ex,_),a in zip(cases,res['after']) if ex==1 and (a[0]=='ok' or a[1]=='outcome_class')))
