"""Generated mutation corpus for the D-188 result-equivalence comparator.

Nothing here is copied from a run: every custody tree is built from the small
synthetic model in ``base_model()``. The layout mirrors a block-5 blind dry run
(record outside ``restricted/``, content-addressed result files inside it, runner
stderr logs, optional ``restricted/decisions/step-codes.jsonl``).

A mutation edits the MODEL and the tree is rebuilt, so every digest reference to
the changed file is re-derived and the record re-commits every output: the change
is a single, clean change. ``break_reference`` is the exception: it edits one built
file in place and re-commits only that file, leaving stale references behind.

Each case in ``CASES`` names the expected blinded result: the verdict and, for each
failing tier, the exact set of printed ``field`` names.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path

CORPUS_INDEX_SHA256 = hashlib.sha256(b'joulewise.b5_equivalence.synthetic_corpus.v1').hexdigest()
UNLISTED_INDEX_SHA256 = hashlib.sha256(b'joulewise.b5_equivalence.synthetic_corpus.unlisted').hexdigest()
COMMIT = 'c0ffee0000000000000000000000000000000001'
OTHER_COMMIT = 'c0ffee0000000000000000000000000000000002'
RECORD = 'B5-BLIND-DRY-RUN-RECORD.json'

# Sentinels the blinded output must never reveal.
SENTINEL_MEAN = '31415.926535'
SENTINEL_MEAN_MUTANT = '27182.818284'
SENTINEL_BUNDLE = 'bundle-sentinel-qx'
SENTINEL_CODE = 'claim_family_underpowered'
SENTINEL_CODE_MUTANT = 'claim_family_unbalanced'
SENTINEL_PLAN = 'v5-b5-alpha-a1-s10-synthetic'


class Num(str):
    """A JSON number written with exactly this source text."""


def _h(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def dumps(value, *, indent=None, sort_keys=False) -> str:
    def enc(v, level):
        pad = '' if indent is None else '\n' + ' ' * (indent * (level + 1))
        end = '' if indent is None else '\n' + ' ' * (indent * level)
        sep = ', ' if indent is None else ','
        if isinstance(v, Num):
            return str(v)
        if v is True:
            return 'true'
        if v is False:
            return 'false'
        if v is None:
            return 'null'
        if isinstance(v, str):
            return json.dumps(v)
        if isinstance(v, int):
            return str(v)
        if isinstance(v, dict):
            items = sorted(v.items()) if sort_keys else list(v.items())
            if not items:
                return '{}'
            return '{' + sep.join(pad + json.dumps(k) + ': ' + enc(x, level + 1) for k, x in items) + end + '}'
        if isinstance(v, list):
            if not v:
                return '[]'
            return '[' + sep.join(pad + enc(x, level + 1) for x in v) + end + ']'
        raise TypeError(type(v))
    return enc(value, 0)


STEPS = [('0', None), ('1', None), ('2', None), ('3', None), ('3b', None), ('4', 'alpha'), ('5', None),
         ('8', None), ('6', None), ('9', None), ('9b', None), ('10', 'alpha'), ('11', None)]
POS = {s if w is None else f'{s}:{w}': i for i, (s, w) in enumerate(STEPS)}


def base_model() -> dict:
    census = [
        {'check': 'harvest_outputs', 'path': 'derived/bracket-binding.json', 'sha256': _h('binding'), 'window': 'alpha'},
        {'check': 'plan_tree_binding:sealed', 'path': 'binding/plan_tree', 'sha256': _h('plan-tree'), 'window': 'alpha'},
        {'check': 'bundle', 'path': f'runs/{SENTINEL_BUNDLE}/manifest.json', 'sha256': _h('bundle'), 'window': 'alpha'},
    ]
    steps = []
    for step, window in STEPS:
        row = {'step': step, 'window': window, 'status': 'ok', 'exit_status': 0, 'registered_exit': None,
               'schema_valid': True, 'refusal': None, 'flags': []}
        if step == '4':
            row.update(exit_status=1, registered_exit='p42_floor_cells_only')
        if step == '1':
            row['schema_valid'] = None
        if step == '11':
            row['flags'] = ['results_rendering_not_run_no_block5_template']
        steps.append(row)
    files = [
        F('0', 'supply-census/{H}-alpha.json', {'schema_version': 'joulewise.supply_census.v1',
                                                'rows': [{'path': 'runs/x', 'sha256': _h('x')}]}),
        F('0', 'attempts/{H}-' + SENTINEL_PLAN + '.json', {
            'attempt': 1, 'claim_usable': True, 'flag_total': 0, 'pack': 'alpha', 'plan_id': SENTINEL_PLAN,
            'verdict': 'COLLECTED', 'window_reasons': []}),
        F('2', 'rereduced/alpha/' + SENTINEL_BUNDLE + '.rereduced.json', {
            'status': 'ok', 'energy_token_j': Num('0.0123456'), 'gross_energy_j': Num('812.5'),
            'summary_provenance': {'bundle_sha256': _h('bundle')}}),
        F('3', 'kept-units/{H}-alpha.json', {
            'attempt': 1, 'pack': 'alpha', 'plan_id': SENTINEL_PLAN, 'schema_version': 'joulewise.kept_units.v1',
            'catalog_sha256': _h('catalog'),
            'cells': {'df-ph-decode-qwen3-1p7b': {'kept': [{'unit_id': 'q01', 'run_ids': ['r1', 'r2']}],
                                                  'dropped': [{'code': 'neg8', 'family': 'NEG8'}]}}}),
        F('3b', 'brackets/{H}-alpha.json', {
            'b_sens': Num('0.0371'),
            'evaluation': {'status': 'accepted', 'b_fiducial_s': Num('0.0238'),
                           'acceptance': {'drift_status': 'within', 'artifact_sha256': _h('acc')}}}),
        F('3b', 'brackets/{H}-block.json', {'T': 3, 'attained_by_sequence': 2, 'value_s': Num('0.0412')}),
        F('4', 'mint/{H}-extraction-alpha.json', {
            'all_cells_extractable': False, 'schema_version': 'joulewise.extraction.v1',
            'manifest_id': 'am-' + _h('manifest')[:16], 'runs_root': '/synthetic/runs',
            'cells': [{'cell_id': 'c-decode', 'extractable': True, 'refusal_reasons': [], 'n_admitted': 9,
                       'members': [{'member': SENTINEL_BUNDLE, 'excluded': False, 'reasons': []}]},
                      {'cell_id': 'c-p42', 'extractable': False, 'refusal_reasons': ['p42_floor'], 'n_admitted': 0,
                       'members': []}],
            'consumption_provenance': {SENTINEL_BUNDLE: {'reduced': '<<sha:rereduced/alpha/' + SENTINEL_BUNDLE
                                                         + '.rereduced.json>>'}},
            'idle_admission_refusals': [], 'spec_membership_refusals': []}, window='alpha'),
        F('5', 'mint/alpha/calibration_plan.json', {'schema_version': 'joulewise.calibration_plan.v1',
                                                    'fixed_n': 24, 'floor_cells': ['c-decode']}),
        F('5', 'mint/floor-mint-inputs.json', {'schema_version': 'joulewise.floor_mint_inputs.v1',
                                               'producer_plans': [{'extraction': '<<name:mint/{H}-extraction-alpha.json>>',
                                                                   'sha256': '<<sha:mint/{H}-extraction-alpha.json>>',
                                                                   'ref': '<<sha:mint/{H}-extraction-alpha.json>>'}]}),
        F('5', 'mint/{H}-aggregate-floor.json', {
            'schema_version': 'joulewise.aggregate_floor.v1', 'method': {'rule': 'max-envelope'},
            'cells': [{'cell_id': 'c-decode', 'floor_abs_j': Num('0.0'), 'floor_cmp_j': Num('1.25'),
                       'eligibility': 'eligible'}],
            'transport_groups': [{'composed_floor_j': Num('2.5')}],
            'provenance': {'implementation': {'project_commit': '<<commit>>'}}}),
        F('5', 'mint/{H}-single-count.md', 'single count: 9 members\n'),
        F('8', 'finalized/inputs/gamma-pack/plan_tree.json', {'plan': 'gamma', 'rows': [1, 2, 3]}),
        F('8', 'finalized/analysed-attempt-exclusions-{H}.json', {
            'attempt': 1, 'cells': [], 'members_excluded': [{'member': 'm9', 'code': 'span'}], 'release_blocked': False}),
        F('6', 'finalized/outputs/closeout.json', {
            'schema_version': 'joulewise.closeout.v1', 'branch': 'dominance', 'all_independent_pass': True,
            'subtitle_licensed': True, 'refusal_reason': None,
            'independent_ratios': [{'ratio': Num('1.731'), 'passes': True, 'status': 'ok', 'refusal_reason': None}],
            'finalized_manifest_sha256': _h('fm')}),
        F('6', 'finalized/outputs/closeout.ratio-table.json', {
            'schema_version': 'joulewise.ratio_table.v1', 'closeout_sha256': '<<sha:finalized/outputs/closeout.json>>',
            'ratios': [{'ratio': Num('100000.0')}]}),
        F('9', 'outputs/{H}-claim-verdicts.json', {
            'schema_version': 'joulewise.claim_verdicts.v1', 'claim_verdicts_id': 'cv-' + _h('cv')[:12],
            'contrasts': [{'contrast_id': 'ctr-decode', 'estimator': {'difference_j': Num('4.25')},
                           'claim_evaluation': {'verdict': 'supported'}}],
            'families': [{'family_id': 'fam-decode', 'structural_status': 'complete'}],
            'bundle_audit': [{'bundle': SENTINEL_BUNDLE, 'inclusion_status': 'included', 'path': '/synthetic/a'}],
            'sampling_audit': {'top_up_detected': False}}),
        F('9b', 'custody/{H}.json', {'schema_version': 'joulewise.paper_custody_receipt.v1', 'family': 'claim_evidence',
                                     'inputs': [{'path': 'outputs/<<name:outputs/{H}-claim-verdicts.json>>',
                                                 'sha256': '<<sha:outputs/{H}-claim-verdicts.json>>'}],
                                     'status': 'verified', 'validator_source_sha256': _h('validator-r1')}),
        F('9b', 'custody/{H}.json#bound', {'schema_version': 'joulewise.claim_side_bound.v2',
                                           'claim_verdicts_sha256': '<<sha:outputs/{H}-claim-verdicts.json>>',
                                           'contrasts': [{'contrast_id': 'ctr-decode', 'bound_j': Num('0.75')}]}),
        F('10', 'outputs/{H}-projection-alpha.json', {
            'schema_version': 'joulewise.projection.v1', 'mode': 'blind-dry-run', 'b_override_s': None,
            'cells': [{'cell_id': 'c-decode', 'mean_j': Num(SENTINEL_MEAN), 'lower_j': Num('2.0'),
                       'upper_j': Num('5.5'), 'n_bundles': 9}],
            'refused_cells': [{'cell_id': 'c-p42', 'reason': 'p42_floor'}],
            'window': {'pack': 'alpha', 'plan_id': SENTINEL_PLAN}}, window='alpha'),
        F('10', 'custody/{H}.json#energy', {'schema_version': 'joulewise.paper_custody_receipt.v1',
                                            'family': 'reported_energy_parents', 'status': 'verified',
                                            'inputs': [{'path': '<<name:mint/{H}-extraction-alpha.json>>',
                                                        'sha256': '<<sha:mint/{H}-extraction-alpha.json>>'}],
                                            'validator_source_sha256': _h('validator-r1')}, window='alpha'),
        F('11', 'outputs/{H}.json#sensitivity', {'schema_version': 'joulewise.sensitivity.v1', 'b_max': Num('0.05'),
                                                 'contrasts': [], 'floor_cells': [], 'reported_cells': [],
                                                 'label': 'sensitivity', 'windows': ['alpha']}),
        F('11', 'disclosures/{H}.released.txt', 'alpha decode: 99.03180 J; h = 4.90347 J\n'),
        F('11', 'outputs/{H}.json#index', {
            'projection_alpha': {'path': '<<name:outputs/{H}-projection-alpha.json>>',
                                 'sha256': '<<sha:outputs/{H}-projection-alpha.json>>'},
            'extraction_alpha': {'path': '<<name:mint/{H}-extraction-alpha.json>>',
                                 'sha256': '<<sha:mint/{H}-extraction-alpha.json>>'}}),
    ]
    logs = {}
    for i, (step, window) in enumerate(STEPS):
        logs[f'{i + 1:04d}-{step}-{window or "block"}.stderr.log'] = f'step {step} progress line\n'
    return {
        'record': {
            'schema_version': 'joulewise.b5_blind_dry_run.v1', 'mode': 'blind-dry-run', 'analysis_commit': COMMIT,
            'window_index_sha256': CORPUS_INDEX_SHA256,
            'sealed': {'analysis_plan_sha256': _h('plan'), 'registration_sha256': _h('registration')},
            'attempts': [{'analysed': True, 'attempt': 1, 'pack': 'alpha', 'plan_id': SENTINEL_PLAN,
                          'verdict': 'COLLECTED'}],
            'windows': [{'harvest_pin': 'a' * 40, 'harvest_record_sha256': _h('harvest'), 'pack': 'alpha',
                         'plan_id': SENTINEL_PLAN, 'kept_counts': {'df-ph-decode-qwen3-1p7b': {'n_b': 9, 'n_r': 9}}}],
            'input_census': census,
            'steps': steps,
        },
        'files': files,
        'logs': logs,
        'step_codes': None,     # None: no step-codes.jsonl; otherwise {'raw_code': ..., 'exception_class': ...}
        'refused_at': None,     # serial position of an outcome-class refusal, if any
        'refusal_code': SENTINEL_CODE,
        'refusal_status': 'outcome_class',   # or 'tooling_refusal' (code then public in the record)
        'indent': None,
    }


def F(step, template, body, window=None):
    key = step if window is None else f'{step}:{window}'
    return {'pos': POS[key], 'template': template, 'body': body}


def _resolve(value, names, shas, commit):
    if isinstance(value, Num):
        return value
    if isinstance(value, str):
        out = value.replace('<<commit>>', commit)
        while '<<' in out:
            start = out.index('<<')
            stop = out.index('>>', start)
            kind, _, template = out[start + 2:stop].partition(':')
            table = names if kind == 'name' else shas
            if template not in table:
                raise KeyError(f'forward or unknown reference {template}')
            out = out[:start] + table[template] + out[stop + 2:]
        return out
    if isinstance(value, dict):
        return {_resolve(k, names, shas, commit): _resolve(v, names, shas, commit) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve(v, names, shas, commit) for v in value]
    return value


def build(model: dict, root: Path) -> Path:
    """Write <root>/dry-run/{RECORD, restricted/...}; return root."""
    model = copy.deepcopy(model)
    record = model['record']
    run = root / 'dry-run'
    restricted = run / 'restricted'
    restricted.mkdir(parents=True)
    commit = record['analysis_commit']
    names, shas = {}, {}
    refused = model['refused_at']
    steps = record['steps']
    if refused is not None:
        row = steps[refused]
        if model['refusal_status'] == 'tooling_refusal':
            row.update(status='tooling_refusal', exit_status=2, registered_exit=None, refusal=model['refusal_code'])
        else:
            row.update(status='outcome_class', exit_status=2, registered_exit=None,
                       refusal=f'outcome-class refusal at step {row["step"]}')
        for later in steps[refused + 1:]:
            later.update(status='not_run', exit_status=None, registered_exit=None, schema_valid=None,
                         refusal=None, flags=[])
    for row in steps:
        row['outputs'] = []
    for f in model['files']:
        if refused is not None and f['pos'] > refused:
            continue
        body = _resolve(f['body'], names, shas, commit)
        template = f['template'].split('#', 1)[0]
        # Input copies are byte copies of sealed inputs: serialization never varies.
        indent = None if template.startswith('finalized/inputs/') else model['indent']
        data = (body if isinstance(body, str) else dumps(body, indent=indent)).encode()
        digest = hashlib.sha256(data).hexdigest()
        name = template.replace('{H}', digest)
        path = restricted / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        names[f['template']] = name
        shas[f['template']] = digest
        steps[f['pos']]['outputs'].append({'name': name, 'sha256': digest})
    logs = restricted / 'logs'
    logs.mkdir()
    for name, text in model['logs'].items():
        (logs / name).write_text(text)
    if refused is not None:
        step, window = STEPS[refused]
        (logs / f'{refused + 1:04d}-{step}-{window or "block"}.stderr.log').write_text(
            f'step {step} progress line\nerror: {model["refusal_code"]}\n')
    if model['step_codes'] is not None:
        rows = []
        for i, row in enumerate(steps):
            code = None
            exc = None
            if row['status'] == 'tooling_refusal':
                code = row['refusal']
            elif row['status'] in ('outcome_class', 'unclassified_refusal'):
                code, exc = model['step_codes']['raw_code'], model['step_codes']['exception_class']
            elif row['exit_status'] not in (None, 0):
                code = row['registered_exit']
            rows.append({'pos': i, 'step': row['step'], 'window': row['window'], 'raw_code': code,
                         'exit_status': row['exit_status'], 'exception_class': exc})
        (restricted / 'decisions').mkdir()
        (restricted / 'decisions' / 'step-codes.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    record['completed_without_tooling_refusal'] = not any(
        r['status'] in ('tooling_refusal', 'unclassified_refusal') for r in steps)
    (run / RECORD).write_bytes(json.dumps(record, sort_keys=True, separators=(',', ':')).encode())
    return root


def file_body(model: dict, template: str):
    for f in model['files']:
        if f['template'] == template:
            return f['body']
    raise KeyError(template)


def recommit(root: Path, name: str, data: bytes) -> str:
    """Replace one built output in place and re-commit only it (no reference cascade)."""
    run = root / 'dry-run'
    record = json.loads((run / RECORD).read_bytes())
    restricted = run / 'restricted'
    for row in record['steps']:
        for out in row['outputs']:
            if out['name'] == name:
                digest = hashlib.sha256(data).hexdigest()
                new = name.replace(out['sha256'], digest)
                os.unlink(restricted / name)
                (restricted / new).write_bytes(data)
                out['name'], out['sha256'] = new, digest
                (run / RECORD).write_bytes(json.dumps(record, sort_keys=True, separators=(',', ':')).encode())
                return new
    raise KeyError(name)


def output_name(root: Path, prefix: str) -> str:
    record = json.loads((root / 'dry-run' / RECORD).read_bytes())
    hits = [o['name'] for row in record['steps'] for o in row['outputs'] if o['name'].startswith(prefix)]
    if len(hits) != 1:
        raise KeyError(prefix)
    return hits[0]


# ---------------------------------------------------------------------------
# Mutations: each returns nothing and edits the model in place.
# ---------------------------------------------------------------------------

def _set(template, path, value):
    def apply(model):
        node = file_body(model, template)
        for p in path[:-1]:
            node = node[p]
        node[path[-1]] = value
    return apply


def _record(path, value):
    def apply(model):
        node = model['record']
        for p in path[:-1]:
            node = node[p]
        node[path[-1]] = value
    return apply


def _text(template, old, new):
    def apply(model):
        for f in model['files']:
            if f['template'] == template:
                assert old in f['body']
                f['body'] = f['body'].replace(old, new)
                return
        raise KeyError(template)
    return apply


def _add_file(step, template, body):
    def apply(model):
        model['files'].append(F(step, template, body))
        model['files'].sort(key=lambda f: f['pos'])
    return apply


def _top_key(template, key, value):
    def apply(model):
        file_body(model, template)[key] = value
    return apply


def _census_extra(model):
    model['record']['input_census'].append({'check': 'extra_read', 'path': 'runs/extra.json', 'sha256': _h('extra'),
                                            'window': 'alpha'})


def _census_sha(model):
    model['record']['input_census'][0]['sha256'] = _h('binding-changed')


def _commit(model):
    model['record']['analysis_commit'] = OTHER_COMMIT


def _reformat(model):
    model['indent'] = 2


def _logs_noise(model):
    for name in model['logs']:
        model['logs'][name] += 'timing: 12 s\n'


def _refused(pos, code=SENTINEL_CODE, status='outcome_class'):
    def apply(model):
        model['refused_at'] = pos
        model['refusal_code'] = code
        model['refusal_status'] = status
    return apply


def _step_codes(raw_code=SENTINEL_CODE, exception_class='AnalysisRefusal'):
    def apply(model):
        model['step_codes'] = {'raw_code': raw_code, 'exception_class': exception_class}
    return apply


def _chain(*fns):
    def apply(model):
        for fn in fns:
            fn(model)
    return apply


P_ONLY = {'decisions': 'NOT_COMPARED', 'registered': 'NOT_COMPARED', 'intermediate': 'NOT_COMPARED'}
REFUSED_POS = POS['9']

# name -> (reference mutation or None, candidate mutation, expected)
# expected: {'verdict', tier -> set of field names | 'MATCH' | 'NOT_COMPARED', optional 'audit'}
CASES = {
    # --- registered numbers -------------------------------------------------
    'registered_projection_mean': (None, _set('outputs/{H}-projection-alpha.json', ['cells', 0, 'mean_j'],
                                              Num(SENTINEL_MEAN_MUTANT)),
                                   {'registered': {'outputs/projection-alpha.json:cells'}}),
    'registered_token_one_point_zero_vs_one': (None, _set('outputs/{H}-projection-alpha.json', ['cells', 0, 'lower_j'],
                                                          Num('2')),
                                               {'registered': {'outputs/projection-alpha.json:cells'}}),
    'registered_negative_zero': (None, _set('mint/{H}-aggregate-floor.json', ['cells', 0, 'floor_abs_j'], Num('-0.0')),
                                 {'registered': {'mint/aggregate-floor.json:cells'}}),
    'registered_exponent_form': (None, _set('finalized/outputs/closeout.ratio-table.json', ['ratios', 0, 'ratio'],
                                            Num('1e5')),
                                 {'registered': {'finalized/outputs/closeout.ratio-table.json:ratios'}}),
    'registered_composed_floor': (None, _set('mint/{H}-aggregate-floor.json', ['transport_groups', 0, 'composed_floor_j'],
                                             Num('2.50')),
                                  {'registered': {'mint/aggregate-floor.json:transport_groups'}}),
    'registered_disclosure_text': (None, _text('disclosures/{H}.released.txt', '99.03180', '99.03181'),
                                   {'registered': {'disclosures/artifact.released.txt:text'}}),
    'registered_sensitivity_b_max': (None, _set('outputs/{H}.json#sensitivity', ['b_max'], Num('0.06')),
                                     {'registered': {'step-eleven/sensitivity:b_max'}}),
    'registered_claim_estimator': (None, _set('outputs/{H}-claim-verdicts.json',
                                              ['contrasts', 0, 'estimator', 'difference_j'], Num('4.26')),
                                   {'registered': {'outputs/claim-verdicts.json:contrasts'}}),
    'registered_closeout_ratio': (None, _set('finalized/outputs/closeout.json', ['independent_ratios', 0, 'ratio'],
                                             Num('1.732')),
                                  {'registered': {'finalized/outputs/closeout.json:independent_ratios'}}),
    'registered_block_bracket': (None, _set('brackets/{H}-block.json', ['value_s'], Num('0.0413')),
                                 {'registered': {'brackets/block.json:value_s'}}),
    # --- decisions ------------------------------------------------------------
    'decision_extractable': (None, _set('mint/{H}-extraction-alpha.json', ['cells', 1, 'extractable'], True),
                             {'decisions': {'mint/extraction-alpha.json:cells'}}),
    'decision_kept_unit': (None, _set('kept-units/{H}-alpha.json',
                                      ['cells', 'df-ph-decode-qwen3-1p7b', 'kept', 0, 'unit_id'], 'q02'),
                           {'decisions': {'kept-units/alpha.json:cells'}}),
    'decision_bracket_status': (None, _set('brackets/{H}-alpha.json', ['evaluation', 'status'], 'refused'),
                                {'decisions': {'brackets/alpha.json:evaluation'}}),
    'decision_closeout_branch': (None, _set('finalized/outputs/closeout.json', ['branch'], 'no_dominance'),
                                 {'decisions': {'finalized/outputs/closeout.json:branch'}}),
    'decision_claim_evaluation': (None, _set('outputs/{H}-claim-verdicts.json',
                                             ['contrasts', 0, 'claim_evaluation', 'verdict'], 'not_supported'),
                                  {'decisions': {'outputs/claim-verdicts.json:contrasts'}}),
    'decision_refused_cells': (None, _set('outputs/{H}-projection-alpha.json', ['refused_cells', 0, 'reason'],
                                          'p42_other'),
                               {'decisions': {'outputs/projection-alpha.json:refused_cells'}}),
    'decision_attempt_verdict': (None, _set('attempts/{H}-' + SENTINEL_PLAN + '.json', ['verdict'], 'ABANDONED'),
                                 {'decisions': {'attempts/alpha:verdict'}}),
    'decision_record_kept_counts': (None, _record(['windows', 0, 'kept_counts', 'df-ph-decode-qwen3-1p7b', 'n_b'], 8),
                                    {'decisions': {'record:windows'}}),
    'decision_exclusions': (None, _set('finalized/analysed-attempt-exclusions-{H}.json',
                                       ['members_excluded', 0, 'code'], 'neg8'),
                            {'decisions': {'finalized/analysed-attempt-exclusions.json:members_excluded'}}),
    'decision_step_flags': (None, _record(['steps', POS['11'], 'flags'], []),
                            {'decisions': {'record:steps'}}),
    # --- refusal identity and position -----------------------------------------
    'refusal_code_from_logs': (_refused(REFUSED_POS), _refused(REFUSED_POS, SENTINEL_CODE_MUTANT),
                               {'decisions': {'decisions:first_refusal'}}),
    'refusal_code_from_step_codes': (_chain(_refused(REFUSED_POS), _step_codes()),
                                     _chain(_refused(REFUSED_POS), _step_codes(raw_code=SENTINEL_CODE_MUTANT)),
                                     {'decisions': {'decisions:step_codes'}}),
    'refusal_position': (_refused(REFUSED_POS), _refused(POS['6']),
                         {'decisions': {'record:steps', 'decisions:first_refusal', 'decisions:step_outputs',
                                        'outputs/claim-verdicts.json:presence'}, 'audit': 'DIFFER'}),
    'refusal_appears': (None, _refused(REFUSED_POS),
                        {'decisions': {'record:steps', 'decisions:first_refusal', 'decisions:step_outputs',
                                       'custody/claim_side_bound:presence', 'outputs/projection-alpha.json:presence',
                                       'step-eleven/sensitivity:presence', 'disclosures/artifact.released.txt:presence'},
                         'audit': 'DIFFER'}),
    # --- intermediate ------------------------------------------------------------
    'intermediate_calibration_plan': (None, _set('mint/alpha/calibration_plan.json', ['fixed_n'], 25),
                                      {'intermediate': {'mint/alpha/calibration_plan.json:fixed_n'}}),
    'intermediate_rereduced': (None, _set('rereduced/alpha/' + SENTINEL_BUNDLE + '.rereduced.json', ['energy_token_j'],
                                          Num('0.0123457')),
                               {'intermediate': {'rereduced/alpha:energy_token_j'}}),
    'intermediate_unknown_key_fails': (None, _top_key('outputs/{H}-projection-alpha.json', 'novel_field', 1),
                                       {'intermediate': {'outputs:<unlisted>'}}),
    'intermediate_side_bound': (None, _set('custody/{H}.json#bound', ['contrasts', 0, 'bound_j'], Num('0.76')),
                                {'intermediate': {'custody/claim_side_bound:contrasts'}}),
    'unknown_artifact_fails': (None, _add_file('5', 'mint/{H}-novel.json', {'value': 1}),
                               {'decisions': {'mint:<unlisted>', 'decisions:step_outputs'}, 'audit': 'DIFFER'}),
    # --- input preconditions -------------------------------------------------------
    'input_sealed_pin': (None, _record(['sealed', 'registration_sha256'], _h('registration-2')),
                         {'inputs': {'record:sealed'}, **P_ONLY}),
    'input_census_sha': (None, _census_sha, {'inputs': {'record:input_census'}, **P_ONLY}),
    'input_copy_bytes': (None, _set('finalized/inputs/gamma-pack/plan_tree.json', ['rows', 2], 4),
                         {'inputs': {'finalized/inputs:bytes'}, **P_ONLY}),
    'input_harvest_pin': (None, _record(['windows', 0, 'harvest_pin'], 'b' * 40),
                          {'inputs': {'record:windows'}, **P_ONLY}),
    # --- audit-only changes: must be ignored ----------------------------------------------
    'audit_validator_source': (None, _set('custody/{H}.json', ['validator_source_sha256'], _h('validator-r2')),
                               {'audit': 'DIFFER'}),
    'audit_claim_verdicts_id': (None, _set('outputs/{H}-claim-verdicts.json', ['claim_verdicts_id'], 'cv-other'),
                                {'audit': 'DIFFER'}),
    'audit_identity_hash_key': (None, _set('brackets/{H}-alpha.json', ['evaluation', 'acceptance', 'artifact_sha256'],
                                           _h('acc-2')),
                                {'audit': 'DIFFER'}),
    'audit_path_key': (None, _set('outputs/{H}-claim-verdicts.json', ['bundle_audit', 0, 'path'], '/elsewhere/a'),
                       {'audit': 'DIFFER'}),
    'audit_census_membership': (None, _census_extra, {'audit': 'DIFFER'}),
    'audit_analysis_commit': (None, _commit, {'audit': 'DIFFER'}),
    'audit_serialization_only': (None, _reformat, {'audit': 'MATCH'}),
    'audit_log_noise': (None, _logs_noise, {'audit': 'MATCH'}),
    'audit_supply_census': (None, _set('supply-census/{H}-alpha.json', ['rows', 0, 'path'], 'runs/y'),
                            {'audit': 'DIFFER'}),
    'audit_exception_class': (_chain(_refused(REFUSED_POS), _step_codes()),
                              _chain(_refused(REFUSED_POS), _step_codes(exception_class='PaperCustodyRefusal')),
                              {'audit': 'DIFFER'}),
    'audit_step_codes_one_side_only': (_refused(REFUSED_POS), _chain(_refused(REFUSED_POS), _step_codes()),
                                       {'audit': 'MATCH'}),
}


def build_case(name: str, parent: Path):
    ref_mut, cand_mut, expected = CASES[name]
    ref_model, cand_model = base_model(), base_model()
    if ref_mut is not None:
        ref_mut(ref_model)
    cand_mut(cand_model)
    ref = build(ref_model, parent / f'{name}-ref')
    cand = build(cand_model, parent / f'{name}-cand')
    return ref, cand, expected
