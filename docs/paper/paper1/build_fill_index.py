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
DEV = 'docs/analysis/b5/DEVIATION-LOG.md'
BARS = 'configs/analysis/b5/recompute_bars.json'
L9 = 'docs/process_traces/2026-10-block5/l9-rulings/'
SEAL = 'docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md'
# FACT H23: RL-5; R2P P1/P7/P9/P12. Source metadata only; no data is read.

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
        return f'claim gate `floor_gate_j` = max over both sides and forms of (guarded operative floor + that floor session\'s whole gross drift allowance); {L9}RULING.md J5 corrects {PA} §5, §7'
    if re.match(r'F_(1p7B|8B)_.*_(abs|cmp)_J', fid):
        return f'`joulewise.detection_floor_artifact.v2` cell `floor_abs_j` / `floor_cmp_j` = form `drift_widened_guarded_floor_j` (guarded operative + whole gross drift allowance); disclose both terms and allowance source ({L9}RULING.md J5)'
    if re.match(r'F_(1p7B|8B)_.*operative', fid):
        return 'DERIVE max(drift-widened abs, drift-widened cmp); must equal the artifact\'s `floor_gate_j`; each form already includes its floor session\'s whole gross drift allowance'
    if fid.startswith(('R_', 'TERM_')):
        return f'`joulewise.d165_dominance_closeout.v1` (R, R_cm, point and corner unguarded floors) ({PA} §6)'
    if fid.startswith('CP-X'):
        return 'placement site of docs/contracts/paper_comparison_placements.md; text rendered from the outcome fields named in the description'
    if fid.startswith(('DG-', 'DX-')):
        return 'existing results-fill-registry row (historical diagnostic, already issued)'
    if fid == 'P1-B5-B-SHARE':
        return 'EXPLORATORY, unregistered: DERIVE B / (h + B) from the same reported-cell record; no registered verdict uses it (RL-5 item 6; analysis plan §12 (lines 771-772))'
    if fid.startswith('P1-B5-'):
        return f'primary-block analysis outputs and disclosure producer ({PA} §4-§8; registration §1)'
    if fid.startswith('P1-B6-'):
        return f'replication-block analysis per counting session, between-session summary and labelled lines ({B6} §6, §9-§11)'
    if fid.startswith('P1-BYX-'):
        return 'structural drop-decision identifiers only: RUN_STATE.md:902 (Qwen3.8-27B), paper-audit.md §4.2/F-18 at origin/audit/2026-11-10-fable (Nemotron: no loadable build); RL-5 item 5; no extension results'
    if fid.startswith(('P1-BYB-', 'P1-BYD-')):
        return f'BYTES harvest structure and stage records ({BY} §5, §11, §15)'
    if fid.startswith('P1-BY-'):
        return f'BYTES stage-2 records of `scripts/bytes_analyze.py` and the twin comparer ({BY} §7-§15)'
    # FACT S9-12 (RL-24 seat 9): per-id sources for the Section 7 automation fills, through 10 November 2026.
    if fid == 'P1-AUTO-MODELS':
        return 'session headers in RUN_STATE.md (each item names its session, model and role: lead, magistrate activation, loop wake); docs/process/gate_policy.md rule 3 (review seats); docs/process/model_allocation_ledger.md; RUN_STATE items 252 and 257 (research lead from 2026-11-10); E3 of item 256b (the AI-use statement names the families)'
    if fid == 'P1-AUTO-LOST':
        return 'census refusal, stop and pause records outside custody, structure only: primary-block arm and window records (docs/process_traces/2026-10-block5/), RUN_STATE items 16 and 31 (primary), 44-59 (replication), 70-78, 85 and 151 (BYTES), harvest verdict codes `night_refused_agent_present` / `night_aborted_agent_present`; no custody path is opened'
    if fid == 'P1-AUTO-CATCHES':
        return 'docs/process_traces/2026-10-27-pipeline-audit/segments.json and SYNTHESIS.md (through 2026-10-27, historical evidence only); docs/process/gate_policy.md rule 9 pruning tallies in session records after 2026-10-27 (RUN_STATE magistrate RECORD.md files and docs/run_reports/)'
    if fid == 'P1-AUTO-REPLAY':
        return f'replay counts, structure only, from {B6}: the drift bar in §9.5 item 7 (lines 1046-1054) and the outside-processor exclusion, S-8 (lines 765-774; RUN_STATE item 42); both on the 77 rehearsal runs named in the revision of 2026-10-15 (lines 32-43)'
    if fid == 'P1-AUTO-BLINDCHECK':
        return 'made 2026-11-11: `docs/process_traces/2026-11-11-bytes-blindcheck/BLINDCHECK.md` on the BYTES lineage; research lead RL-44 and RL-45; registration deviation BY-BLIND-1'
    if fid.startswith('P1-AUTO-'):
        return 'process evidence through November: docs/process/gate_policy.md; docs/process_traces/2026-10-27-pipeline-audit/ (historical evidence only); RUN_STATE items 108 and 181; docs/analysis/b5/DEVIATION-LOG.md; RL-5 items 3-4 and RL-24 seat 9 at origin/audit/2026-11-10-fable (full rewrite and evidence adjudication pending; BLINDCHECK requires its own recorded check)'
    if fid.startswith('P1-ID-') or fid == 'CP-X01-identity':
        return 'identity pins (`identity_pins.json`) and per-session stack records'
    if fid.startswith('P1-M-'):
        return 'registered instrument constants: block-5 registration §0.2, §0.11; replication §3.3 (acceptance files)'
    if fid == 'P1-RELEASE':
        return f'{SEAL} "Release event" and custody locators; record digest, released bundle SHA256SUMS and release-event bindings; replication and BYTES release records only after their gates'
    if fid == 'P1-DEV-LIST':
        return f'{SEAL} (two seals, three prospective errata); {L9}RULING.md J1-J8 (J5 floor-drift correction, 2026-10-12), ERRATUM-RULING.md and ROSTER-RULING.md; docs/process_traces/2026-10-20-magistrate-6cff3515/L9-RULING-ADDENDUM.md; {DEV} DLE-0 through DLE-10; docs/decision_log.md D-188 through D-190; replication §17 and BYTES addenda'
    if fid.startswith('P1-RECOMPUTE'):
        return f'per-family independent comparison and uncovered-quantity reader checks: Block 5 bars from {BARS}, fixed blind under RUN_STATE item 83 ruling 1 and {DEV} DLE-0; coverage limits in docs/analysis/b5/LEAN-COVERAGE-AUDIT.md §§2-4 and pre-print check in DLE-6; Block 6 separately uses {B6} §12.3 (S-13); no agreement/completion inferred from a source pointer'
    if fid.startswith('P1-E-'):
        return 'structure-only harvest records; merged methods draft §4 rows'
    if fid in ('P1-LEDGER',):
        return 'harvest verdicts and attempt histories of every pack (primary, replication, BYTES)'
    if fid.startswith('P1-ABS-'):
        return 'assembled from the outcome ids listed in its description; no new value'
    if fid == 'P1-AVAIL':
        return f'authorized public release manifest and {SEAL} release-event bindings: custody locator, dry-run record digest and released bundle SHA256SUMS; R2P P12; publication scope and actual locators remain unfilled'
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
