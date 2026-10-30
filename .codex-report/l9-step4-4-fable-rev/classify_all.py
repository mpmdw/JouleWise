"""Classify every blind-table code (plus extras) on a refused non-p42 target, under the checkout given as argv[1]."""
import json, sys
root = sys.argv[1]
sys.path.insert(0, root)
from joulewise.b5_analysis.steps import classify_step4_exit
table = json.load(open(root + '/configs/analysis/b5/step4_reason_classes.json'))
SPEC = {'cells': [
    {'cell_id': 'syn-target', 'kind': 'absolute', 'condition_family_id': 'cell-target'},
    {'cell_id': 'syn-cmp', 'kind': 'comparative', 'condition_family_id': 'cell-target'},
    {'cell_id': 'syn-p42-abs', 'kind': 'absolute', 'condition_family_id': 'cell-p42'},
    {'cell_id': 'syn-p42-cmp', 'kind': 'comparative', 'condition_family_id': 'cell-p42-x'}]}
def cell(cid, refused, reasons):
    return {'cell_id': cid, 'extractable': not refused, 'refusal_reasons': list(reasons) if refused else [], 'floor': None}
def report(refused, reasons):
    return {'spec_membership_refusals': [],
            'cells': [cell(c['cell_id'], c['cell_id'] in refused, reasons.get(c['cell_id'], ())) for c in SPEC['cells']]}
extras = ['fixed_n_plan_incomplete', 'syn_reason_in_neither_list', 'member_code_on_kept_unit', '']
codes = sorted(set(table['mask']) | set(table['tooling']) | set(table['r3']) | set(extras))
out = {}
for code in codes:
    target = classify_step4_exit(1, report(('syn-target',), {'syn-target': (code,)}), SPEC)
    p42 = classify_step4_exit(1, report(('syn-p42-abs',), {'syn-p42-abs': (code,)}), SPEC)
    both = classify_step4_exit(1, report(('syn-target', 'syn-p42-abs'), {'syn-target': ('marker_self_digest_mismatch',), 'syn-p42-abs': (code,)}), SPEC)
    exit0 = classify_step4_exit(0, report(('syn-target',), {'syn-target': (code,)}), SPEC)
    exit2 = classify_step4_exit(2, report(('syn-target',), {'syn-target': (code,)}), SPEC)
    out[code] = {'target': target, 'p42_only': p42, 'target_tooling_plus_p42': both, 'exit0': exit0, 'exit2': exit2}
json.dump(out, sys.stdout, indent=1, sort_keys=True)
print()
