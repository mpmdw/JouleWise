import json, sys
sys.path.insert(0, sys.argv[1])
from joulewise.b5_analysis.steps import classify_step4_exit, step4_r3_reasons
t = json.load(open(sys.argv[1] + '/configs/analysis/b5/step4_reason_classes.json'))
codes = sorted(set(t['mask']) | set(t['tooling']) | set(t['r3']) | {'paired_block_incomplete','fixed_n_plan_incomplete','syn_unlisted'} | set(json.loads(sys.argv[2])))
SPEC = {'cells': [{'cell_id': 'syn-target', 'kind': 'absolute', 'condition_family_id': 'cell-target'},
    {'cell_id': 'syn-p42-abs', 'kind': 'absolute', 'condition_family_id': 'cell-p42'}]}
out = {}
for c in codes:
    for target, p42 in ((True, False), (False, True), (True, True)):
        rep = {'spec_membership_refusals': [], 'cells': [
            {'cell_id': 'syn-target', 'extractable': not target, 'refusal_reasons': [c] if target else []},
            {'cell_id': 'syn-p42-abs', 'extractable': not p42, 'refusal_reasons': [c] if p42 else []}]}
        out[f'{c}|t={int(target)}|p={int(p42)}'] = classify_step4_exit(1, rep, SPEC)
    # exit 0 / exit 2 with that reason
    rep = {'spec_membership_refusals': [], 'cells': [{'cell_id': 'syn-target', 'extractable': False, 'refusal_reasons': [c]},{'cell_id':'syn-p42-abs','extractable':True,'refusal_reasons':[]}]}
    out[f'{c}|exit0'] = classify_step4_exit(0, rep, SPEC)
    out[f'{c}|exit2'] = classify_step4_exit(2, rep, SPEC)
json.dump({'r3': sorted(step4_r3_reasons()), 'mask': t['mask'], 'tooling': t['tooling'], 'class': out}, sys.stdout, indent=0, sort_keys=True)
