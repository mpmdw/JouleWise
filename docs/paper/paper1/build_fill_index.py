"""Builds fill_index.md: every {{FILL: id | what}} placeholder in Paper 1 and its variants.

Run from the repository root: python3 docs/paper/paper1/build_fill_index.py
"""
import re, pathlib, collections

ROOT = pathlib.Path('docs/paper/paper1')
FILES = [ROOT / 'paper1.md'] + sorted((ROOT / 'variants').glob('tier*.md'))
REGISTRY = pathlib.Path('docs/paper/results-fill-registry.md').read_text()
PAT = re.compile(r'\{\{FILL:\s*([^|\\}]+?)\s*(?:\\\||\|)\s*(.*?)\}\}', re.S)

registry_tokens = set(re.findall(r'`\[([A-Za-z0-9_]+)\]`', REGISTRY))
registry_rows = set(re.findall(r'^\| ((?:DG|DX|SYN|S)-?\d+)\b', REGISTRY, re.M))

PA = 'configs/campaigns/v5_claim_25g83/analysis_plan_block5.md'
B6 = 'docs/registrations/block6_replication_DRAFT.md'
BY = 'docs/registrations/bytes_pack_v1.md (branch work/2026-10-23-by-slots-draft)'
BYX = 'docs/registrations/bytes_extension_models_2026-10-27.md'

def source(fid):
    """Supplying artifact and field for an id (who issues the value)."""
    if re.match(r'E_(1p7B|8B)_', fid):
        f = {'J_per_request': 'mean_j', 'lower_J': 'lower_j', 'upper_J': 'upper_j', 'J_per_token': 'per_token.j_per_token'}
        fld = next(v for k, v in f.items() if fid.endswith(k))
        return f'`joulewise.paper_reported_energy_projection.v1` cell `{fld}` ({PA} §4, §9)'
    if re.match(r'E_(decode|prefill_p2048)_contrast_signed', fid):
        return f'`joulewise.claim_verdicts.v1` contrast `estimator.estimate` (8B minus 1.7B) ({PA} §7, §9)'
    if re.match(r'E_(decode|prefill_p2048)_contrast_(lower|upper)', fid):
        return f'`joulewise.claim_verdicts.v1` `deterministic_bounds.decision_interval.lower/upper` ({PA} §7.1)'
    if fid.startswith('F_claim_'):
        return f'claim gate `floor_gate_j` = max of the two sides\' operative floors ({PA} §5, §7)'
    if re.match(r'F_(1p7B|8B)_.*_(abs|cmp)_J', fid):
        return f'`joulewise.detection_floor_artifact.v2` cell `floor_abs_j` / `floor_cmp_j`, guarded ({PA} §5)'
    if re.match(r'F_(1p7B|8B)_.*operative', fid):
        return 'DERIVE max(abs, cmp); must equal the artifact\'s `floor_gate_j`'
    if fid.startswith(('R_', 'TERM_')):
        return f'`joulewise.d165_dominance_closeout.v1` (R, R_cm, point and corner unguarded floors) ({PA} §6)'
    if fid.startswith('CP-X'):
        return 'placement site of docs/contracts/paper_comparison_placements.md; text rendered from the outcome fields named in the description'
    if fid.startswith(('DG-', 'DX-')):
        return 'existing results-fill-registry row (historical diagnostic, already issued)'
    if fid.startswith('P1-B5-'):
        return f'primary-block analysis outputs and disclosure producer ({PA} §4-§8; registration §1)'
    if fid.startswith('P1-B6-'):
        return f'replication-block analysis per counting session, between-session summary and labelled lines ({B6} §6, §9-§11)'
    if fid.startswith('P1-BYX-'):
        return f'BYTES extension records, own family ({BYX})'
    if fid.startswith(('P1-BYB-', 'P1-BYD-')):
        return f'BYTES harvest structure and stage records ({BY} §5, §11, §15)'
    if fid.startswith('P1-BY-'):
        return f'BYTES stage-2 records of `scripts/bytes_analyze.py` and the twin comparer ({BY} §7-§15)'
    if fid.startswith('P1-AUTO-'):
        return 'process record: docs/process/gate_policy.md, docs/process_traces/2026-10-27-pipeline-audit/ (SYNTHESIS, CRITIQUE, outcomes ledger), RUN_STATE'
    if fid.startswith('P1-ID-') or fid == 'CP-X01-identity':
        return 'identity pins (`identity_pins.json`) and per-session stack records'
    if fid.startswith('P1-M-'):
        return 'registered instrument constants: block-5 registration §0.2, §0.11; replication §3.3 (acceptance files)'
    if fid in ('P1-RELEASE', 'P1-DEV-LIST'):
        return 'seal record (block 5) "Release event" section, replication §17 change log, BYTES addenda and release records'
    if fid.startswith('P1-RECOMPUTE'):
        return f'independent recomputation comparison table; tolerance from {B6} §12.3'
    if fid.startswith('P1-E-'):
        return 'structure-only harvest records; merged methods draft §4 rows'
    if fid in ('P1-LEDGER',):
        return 'harvest verdicts and attempt histories of every pack (primary, replication, BYTES)'
    if fid.startswith('P1-ABS-'):
        return 'assembled from the outcome ids listed in its description; no new value'
    if fid == 'P1-AVAIL':
        return 'release manifest (not yet issued)'
    return 'NEW — supplier to be named'

def status(fid):
    if fid in registry_tokens:
        return 'registry row (exists; status RETIRED_FALLBACK — needs reactivation by placement ruling)'
    if fid.replace('_prefill_p2048_', '_prefill_p[PREFILL_LENGTH]_') in registry_tokens:
        return 'registry row with [PREFILL_LENGTH] = 2048 (registry token family; reactivation needed)'
    if fid.startswith(('DG-', 'DX-')):
        return 'registry row (issued)'
    if fid.startswith('CP-X'):
        return 'existing placement id (PROPOSED_STOP_FILL)'
    return 'NEW id (this draft)'

occ = collections.OrderedDict()
for f in FILES:
    text = f.read_text()
    for m in PAT.finditer(text):
            i = text.count('\n', 0, m.start()) + 1
            fid, what = m.group(1).strip(), ' '.join(m.group(2).split())
            if fid.startswith('<'):
                continue
            e = occ.setdefault(fid, {'what': what, 'where': []})
            if len(what) > len(e['what']):
                e['what'] = what
            e['where'].append(f'{f.relative_to(ROOT)}:{i}')

total = sum(len(v['where']) for v in occ.values())
main_total = sum(1 for v in occ.values() for w in v['where'] if w.startswith('paper1.md'))
new_ids = [k for k in occ if status(k).startswith('NEW')]
out = ['# Paper 1 FILL index', '',
       'Generated by `build_fill_index.py` from every `{{FILL: id | what}}` in `paper1.md` and `variants/`.',
       'Do not edit by hand; edit the placeholders and re-run.', '',
       f'- Placeholder occurrences: **{total}** ({main_total} in paper1.md, {total - main_total} in variants).',
       f'- Distinct ids: **{len(occ)}**, of which **{len(new_ids)}** are new ids introduced by this draft.', '',
       '**Fill rule.** A value is filled only from the issued artifact and field named in "Source", after the',
       'release event of the block concerned, never from prose or recomputed by hand. Ids that name an outcome',
       'word also select the branch of the text to keep. Registry rows marked RETIRED_FALLBACK must be',
       'reactivated by the placement ruling (block-5 registration §14 Q4) before any fill.', '',
       '| Id | What it is | Status | Source (artifact, field) | Where |', '|---|---|---|---|---|']
for fid, e in occ.items():
    where = ', '.join(e['where'][:6]) + (f' (+{len(e["where"]) - 6})' if len(e['where']) > 6 else '')
    out.append(f'| `{fid}` | {e["what"].replace("|", "/")} | {status(fid)} | {source(fid)} | {where} |')
out += ['', '## New ids introduced by this draft', '', ', '.join(f'`{k}`' for k in new_ids), '']
(ROOT / 'fill_index.md').write_text('\n'.join(out))
print(total, main_total, len(occ), len(new_ids))
