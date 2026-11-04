"""Commit-derived reference corpus for the D-188 comparator (REFERENCE SITES in compare_b5_results.py).

The base corpus (corpus.py) carries no field that digests another artifact's content,
so an analysis-commit change there only touches the commit itself. Real block-5 trees
do: the commit is in the floor artifacts' provenance, and the floor-mint pinset, the
finalized manifest, the closeout and the claim verdicts carry canonical-JSON digests,
content-derived ids, a hex-named path, an embedded copy and digests of per-producer
component floor artifacts that custody never stores. ``derived_model()`` adds that
structure to the base model, every derived field computed from the bytes actually
written, by the producers' rules (restated stdlib-only; tests check them against the
producers: analysis_manifest_v3.calculate_manifest_id, dominance_closeout.canonical_json_sha256,
mint._artifact_sha256 and the mint's own component check _validate_v2_artifact_binding).

A model edit therefore hides behind recomputed digests: every reference to the edited
content is re-derived. ``spec['forge']`` is the exception: it overwrites one reference
site after derivation (everything downstream is still derived from the forged bytes),
which the comparator must refuse as self-inconsistent.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _corpus():
    name = 'jw_b5_equivalence_corpus'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, _HERE / 'corpus.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


corpus = _corpus()
Num, F, _h = corpus.Num, corpus.F, corpus._h

PROSPECTIVE_ID = _h('prospective-manifest')
FM = f'finalized/am-{PROSPECTIVE_ID}.finalized.json'
AGG, AGG_FINAL = 'mint/{H}-aggregate-floor.json', 'finalized/mint/{H}-aggregate-floor.json'
PINSET, PINSET_FINAL = 'mint/floor-mint-pinset.json', 'finalized/mint/floor-mint-pinset.json'
REPLAY, REPLAY_FINAL = 'mint/{H}-dominance-replay.json', 'finalized/mint/{H}-dominance-replay.json'
CLOSEOUT, VERDICTS = 'finalized/outputs/closeout.json', 'outputs/{H}-claim-verdicts.json'
EXTRACTION = 'mint/{H}-extraction-alpha.json'
# scripts/mint_floor_artifact_generalized.py V2_MINT_TOOL_VERSION / V2_ASSURANCE_PROFILE (a test pins them).
MINT_TOOL_VERSION = 'joulewise.floor_mint.generalized.v2'
ASSURANCE = {
    'profile_id': 'single_authority_hash_bound_replay.v1', 'independent_attestation': False,
    'establishes': ['exact-byte consistency with disclosed commitments',
                    'ledger and verdict consistency under the recorded code',
                    'deterministic rederivability of mint inputs'],
    'does_not_establish': ['honesty of the trusted operator', 'independent witness of physical collection',
                           'resistance to coordinated prepublication rewrite'],
}
CONTAINMENT = ('mint_commit_contained_in_origin_main', 'head_pin_commit_contained_in_origin_main')

_ROOT: list = [None]


def canonical_sha256(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                                     allow_nan=False).encode('utf-8')).hexdigest()


def manifest_id(value) -> str:
    body = dict(value)
    body.pop('manifest_id', None)
    return 'am-' + canonical_sha256(body)


def artifact_sha256(value) -> str:
    return hashlib.sha256((json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()).hexdigest()


def config_set_sha256(hashes) -> str:
    return hashlib.sha256(json.dumps(sorted(set(hashes)), separators=(',', ':')).encode()).hexdigest()


def plain(value):
    """The JSON value a reader of the written bytes sees (Num text -> float/int)."""
    return json.loads(corpus.dumps(value))


def _written(names, template) -> bytes:
    return (_ROOT[0] / 'dry-run' / 'restricted' / names[template]).read_bytes()


def _forge(spec, kind, body):
    for path, value in spec.get('forge', {}).get(kind, []):
        node = body
        for p in path[:-1]:
            node = node[p]
        node[path[-1]] = value
    return body


class Derived:
    """A file body computed at build time from the model spec and the outputs written before it."""

    def __init__(self, kind: str, spec: dict):
        self.kind, self.spec = kind, spec

    def __call__(self, names, shas, commit):
        spec = corpus._resolve(copy.deepcopy({k: v for k, v in self.spec.items() if k != 'forge'}), names, shas, commit)
        spec['forge'] = self.spec.get('forge', {})
        return _forge(spec, self.kind, BUILDERS[self.kind](spec, names, shas))


# ---------------------------------------------------------------------------
# The two-producer aggregate mint (scripts/emit_floor_mint_pinset.py, mint _build_v2_artifacts)
# ---------------------------------------------------------------------------

def _aggregate_core(spec):
    floor = spec['floor']
    return {
        'schema_version': 'joulewise.detection_floor_artifact.v2', 'artifact_id': floor['artifact_id'],
        'calibration_scope': 'production_window', 'source_class': 'prospective', 'method': floor['method'],
        'idle_drift_guard': floor['idle_drift_guard'], 'cells': floor['cells'],
        'transport_groups': floor['transport_groups'],
        'provenance': {
            'calibration_plan': {'plan_id': floor['plan_set_id'], 'declared_calibration_scope': 'production_window',
                                 'relative_path': 'floor-mint-pinset.json', 'sha256': None},
            'producer_calibration_plans': [{k: p['plan'][k] for k in ('plan_id', 'declared_calibration_scope',
                                                                       'relative_path', 'sha256')}
                                           for p in spec['producers']],
            'mint_tool_version': MINT_TOOL_VERSION, 'assurance': ASSURANCE,
            'implementation': floor['implementation'],
            'producer_config_sets': [_config_set(p) for p in spec['producers']],
            'producer_launch_lineages': [{'plan_id': p['plan']['plan_id'], 'launch_lineage': p['launch_lineage']}
                                         for p in spec['producers']],
        },
    }


def _config_set(producer):
    return {'plan_id': producer['plan']['plan_id'], 'config_set_sha256': producer['model_runtime_config']['config_set_sha256'],
            'cells': [{'cell_id': c['cell_id'], 'scientific_config_identity_sha256': c['scientific_config_identity_sha256']}
                      for c in producer['cells']]}


def component(aggregate, producer, artifact_id, variant):
    """Component floor artifact of one producer: the aggregate restricted to it (mint _build_v2_artifacts)."""
    out = copy.deepcopy(aggregate)
    out['artifact_id'] = artifact_id
    prov = aggregate['provenance']
    out['provenance'] = {
        'calibration_plan': {k: producer['plan'][k] for k in ('plan_id', 'declared_calibration_scope', 'relative_path',
                                                              'sha256')},
        'mint_tool_version': prov['mint_tool_version'], 'assurance': copy.deepcopy(prov['assurance']),
        'implementation': dict(prov['implementation'], **dict(zip(CONTAINMENT, variant))),
        'producer_config_sets': [_config_set(producer)], 'launch_lineage': copy.deepcopy(producer['launch_lineage'])}
    cells = {c['cell_id']: c for c in aggregate['cells']}
    groups = {g['transport_group_id']: g for g in aggregate['transport_groups']}
    out['cells'] = [copy.deepcopy(cells[c['cell_id']]) for c in producer['cells']]
    out['transport_groups'] = [copy.deepcopy(groups[c['transport_group_id']]) for c in producer['cells']]
    return out


def floor_pair(spec):
    """(aggregate floor, pinset) as plain-able bodies; digests computed over the plain values."""
    aggregate = _aggregate_core(spec)
    agg_plain = plain(aggregate)
    producers = []
    for p in spec['producers']:
        row = {k: copy.deepcopy(v) for k, v in p.items() if k not in ('launch_lineage', 'variant')}
        row['component_artifact'] = {'artifact_id': p['component_artifact_id'],
                                     'sha256': artifact_sha256(component(agg_plain, plain(p), p['component_artifact_id'],
                                                                         p['variant']))}
        row.pop('component_artifact_id')
        producers.append(row)
    pinset = {
        'schema_version': 'joulewise.floor_mint_pinset.v2', 'mint_tool_version': MINT_TOOL_VERSION,
        'producer_plans': producers,
        'aggregate': {
            'artifact_id': spec['floor']['artifact_id'], 'plan_set_id': spec['floor']['plan_set_id'],
            'producer_set_sha256': canonical_sha256(plain(producers)),
            'calibration_scope': 'production_window', 'source_class': 'prospective',
            'cell_composition_rule': 'componentwise_max_never_sum.v1', 'consumer_floor_rule': 'cross_stack_armwise_max.v1',
            'component_artifacts': [{'plan_id': p['plan']['plan_id'], **p['component_artifact'],
                                     'producer_pin_sha256': canonical_sha256(plain(p))} for p in producers],
            'cell_ids': [c['cell_id'] for p in producers for c in p['cells']],
            'transport_allowlists': [{'transport_group_id': c['transport_group_id'], 'cell_ids': [c['cell_id']],
                                      'allowed_consumer_condition_families': c['allowed_consumer_condition_families']}
                                     for p in producers for c in p['cells']],
        },
    }
    aggregate['provenance']['calibration_plan']['sha256'] = pinset['aggregate']['producer_set_sha256']
    return aggregate, pinset


def _b_aggregate(spec, names, shas):
    return floor_pair(spec)[0]


def _b_pinset(spec, names, shas):
    return floor_pair(spec)[1]


def _b_manifest(spec, names, shas):
    body = copy.deepcopy(spec['manifest'])
    floor_name = names[AGG_FINAL]
    replay_name = names[REPLAY_FINAL]
    body['evidence'] = {
        'aggregate_floor_artifact': {'path': floor_name.removeprefix('finalized/'), 'sha256': shas[AGG_FINAL],
                                     'schema_version': 'joulewise.detection_floor_artifact.v2',
                                     'artifact_id': spec['floor']['artifact_id']},
        'dominance_replay_sidecar': {'path': replay_name.removeprefix('finalized/'), 'sha256': shas[REPLAY_FINAL],
                                     'schema_version': 'joulewise.d165_dominance_replay.v1',
                                     'sidecar_id': spec['replay']['sidecar_id']}}
    body = _forge(spec, 'manifest-evidence', body)
    body['manifest_id'] = manifest_id(plain(body))
    return body


def _b_closeout(spec, names, shas):
    body = copy.deepcopy(spec['closeout'])
    fm = json.loads(_written(names, FM))
    floor = json.loads(_written(names, AGG_FINAL))
    replay = json.loads(_written(names, REPLAY_FINAL))
    body['finalized_manifest_sha256'] = shas[FM]
    body['replay_sidecar_sha256'] = shas[REPLAY_FINAL]
    body['sources'] = {
        'finalized_manifest': {'canonical_json_sha256': canonical_sha256(fm), 'identity': fm['manifest_id'],
                               'schema_version': 'joulewise.analysis_manifest.v3.finalized'},
        'floor_artifact': {'canonical_json_sha256': canonical_sha256(floor), 'identity': floor['artifact_id'],
                           'schema_version': 'joulewise.detection_floor_artifact.v2'},
        'replay_sidecar': {'canonical_json_sha256': canonical_sha256(replay), 'identity': replay['sidecar_id'],
                           'schema_version': 'joulewise.d165_dominance_replay.v1'}}
    return body


def _b_verdicts(spec, names, shas):
    body = copy.deepcopy(spec['verdicts'])
    fm_raw, floor_raw = _written(names, FM), _written(names, AGG_FINAL)
    body['inputs'] = {
        'analysis_manifest': {'manifest_id': json.loads(fm_raw)['manifest_id'], 'file_sha256': shas[FM]},
        'floor_artifact': {'artifact_id': json.loads(floor_raw)['artifact_id'], 'file_sha256': shas[AGG_FINAL],
                           'embedded_bytes_base64': base64.b64encode(floor_raw).decode('ascii')},
        'runs_root_label': 'runs_claim', 'evidence_class': 'current', 'limitations': []}
    return body


BUILDERS = {'aggregate': _b_aggregate, 'pinset': _b_pinset, 'manifest': _b_manifest, 'closeout': _b_closeout,
            'verdicts': _b_verdicts}


def _cell(cell_id, group, gate):
    return {'cell_id': cell_id, 'transport_group_id': group, 'floor_abs_j': Num('0.5'), 'floor_cmp_j': Num(gate),
            'floor_gate_j': Num(gate), 'eligibility': {'status': 'claim_ready', 'minimum_claim_n': 9},
            'key': {'metric': 'phase_energy_j.decode', 'window_class': 'phase'}}


def _producer(n, cells):
    plan_id = f'plan-syn-floor-producer-{n}'
    config = [_h(f'config-{n}-{c}') for c, _g in cells]
    return {
        'plan': {'plan_id': plan_id, 'sha256': _h(f'plan-{n}'), 'declared_sha256': _h(f'plan-{n}'),
                 'sidecar_sha256': _h(f'plan-sidecar-{n}'), 'relative_path': f'p{n}/calibration_plan.json',
                 'declared_calibration_scope': 'production_window', 'artifact_calibration_scope': 'production_window'},
        'evidence_root_id': f'evidence-syn-{n}', 'component_artifact_id': f'syn-floor-component-{n}',
        'model_runtime_config': {'config_set_sha256': config_set_sha256(config), 'runtime_identity_sha256': _h(f'rt-{n}')},
        'extraction_spec': {'sha256': '<<sha:' + EXTRACTION + '>>', 'member_count': 100},
        'calibration_acceptance': {'acceptance_id': 'syn-acceptance-v2', 'artifact_sha256': _h('acceptance'),
                                   'derivation_sha256': _h('derivation'), 'derivation_rule_id': 'syn.bound.v2'},
        'cells': [{'role': role, 'cell_id': cell, 'transport_group_id': group, 'scientific_config_identity_sha256': cfg,
                   'metric': 'phase_energy_j.decode', 'window_class': 'phase',
                   'condition_family_id': f'fam-{cell}', 'condition_family_sha256': _h(f'fam-{cell}'),
                   'allowed_consumer_condition_families': [{'condition_family_id': f'fam-{cell}',
                                                            'condition_family_sha256': _h(f'fam-{cell}')}],
                   'absolute': {'drift_allowance_j': Num('1.0440031334189257'), 'expected_n': 9,
                                'extraction_spec_sha256': '<<sha:' + EXTRACTION + '>>'},
                   'postcollection': {'absolute_floor_full_precision': '0.5', 'comparative_floor_full_precision': '1.25',
                                      'operative_floor_full_precision': '1.25'}}
                  for role, (cell, group), cfg in zip(('decode', 'prefill'), cells, config)],
        'launch_lineage': {'launch_id': f'syn-launch-{n}', 'marker_sha256': _h(f'marker-{n}')},
        'variant': [False, None],
    }


def derived_spec() -> dict:
    cells = [('syn-cell-a-decode', 'tg-a-decode'), ('syn-cell-a-prefill', 'tg-a-prefill'),
             ('syn-cell-b-decode', 'tg-b-decode'), ('syn-cell-b-prefill', 'tg-b-prefill')]
    return {
        'floor': {
            'artifact_id': 'syn-floor-set-v5', 'plan_set_id': 'plan-set-syn-floor-v5', 'method': {'rule': 'max-envelope'},
            'idle_drift_guard': {'status': 'within', 'bound_j': Num('0.25')},
            'cells': [_cell(c, g, gate) for (c, g), gate in zip(cells, ('1.25', '1.5', '2.25', '2.5'))],
            'transport_groups': [{'transport_group_id': g, 'source_cell_ids': [c], 'composed_floor_gate_j': Num(gate)}
                                 for (c, g), gate in zip(cells, ('1.25', '1.5', '2.25', '2.5'))],
            'implementation': {'project_commit': '<<commit>>', 'project_tree_state': 'clean',
                               'mint_commit_contained_in_origin_main': True,
                               'head_pin_commit_contained_in_origin_main': None, 'python_package': 'joulewise'},
        },
        'producers': [_producer(1, cells[:2]), _producer(2, cells[2:])],
        'replay': {'schema_version': 'joulewise.d165_dominance_replay.v1', 'sidecar_id': 'syn-floor-set-v5::d165-replay',
                   'rule_id': 'syn.replay.v1', 'cells': [{'cell_id': 'syn-cell-a-decode', 'ratio': Num('1.731')}]},
        'manifest': {'schema_version': 'joulewise.analysis_manifest.v3.finalized', 'manifest_id': '',
                     'freeze_status': 'finalized',
                     'lineage': {'prospective_manifest_id': f'am-{PROSPECTIVE_ID}'},
                     'contrasts': [{'contrast_id': 'ctr-decode', 'estimand': 'difference_j'}],
                     'design': {'blocks': 5}},
        'closeout': corpus.file_body(corpus.base_model(), CLOSEOUT),
        'verdicts': corpus.file_body(corpus.base_model(), VERDICTS),
    }


def derived_model() -> dict:
    model = corpus.base_model()
    spec = derived_spec()
    model['derived'] = spec
    replaced = {AGG: 'aggregate', CLOSEOUT: 'closeout', VERDICTS: 'verdicts'}
    files = [dict(f, body=Derived(replaced[f['template']], spec)) if f['template'] in replaced else f
             for f in model['files']]
    files += [F('5', PINSET, Derived('pinset', spec)), F('5', REPLAY, spec['replay']),
              F('8', AGG_FINAL, Derived('aggregate', spec)), F('8', PINSET_FINAL, Derived('pinset', spec)),
              F('8', REPLAY_FINAL, spec['replay']), F('8', FM, Derived('manifest', spec))]
    files.sort(key=lambda f: f['pos'])     # stable: referents precede their references
    model['files'] = files
    return model


def build(model: dict, root: Path) -> Path:
    _ROOT[0] = root
    try:
        return corpus.build(model, root)
    finally:
        _ROOT[0] = None


# ---------------------------------------------------------------------------
# Mutations of the spec (model['derived']); each is hidden behind recomputed digests.
# ---------------------------------------------------------------------------

def _spec(*path, value):
    def apply(model):
        node = model['derived']
        for p in path[:-1]:
            node = node[p]
        node[path[-1]] = value
    return apply


def _forged(kind, path, value):
    def apply(model):
        model['derived'].setdefault('forge', {}).setdefault(kind, []).append((path, value))
    return apply


def _commit(model):
    model['record']['analysis_commit'] = corpus.OTHER_COMMIT


def _variant(model):
    for p in model['derived']['producers']:
        p['variant'] = [True, None]


def _extraction_cell(model):
    corpus.file_body(model, EXTRACTION)['cells'][0]['n_admitted'] = 8


PINSETS = {'mint/floor-mint-pinset.json:{}', 'finalized/mint/floor-mint-pinset.json:{}'}
AGGREGATES = {'mint/aggregate-floor.json:{}', 'finalized/mint/aggregate-floor.json:{}'}


def _both(names, section):
    return {n.format(section) for n in names}


# name -> (reference mutation, candidate mutation, expected blinded result, the reference rule the change hides behind)
CASES = {
    # The real E-vs-candidate pattern: only the analysis commit differs.
    'commit_only': (None, _commit, {'audit': 'DIFFER'}, 'all'),
    'hidden_replay_value': (None, _spec('replay', 'cells', 0, 'ratio', value=Num('1.732')),
                            {'intermediate': {'mint/dominance-replay.json:cells',
                                              'finalized/mint/dominance-replay.json:cells'}}, 'canonical'),
    'hidden_floor_identity': (None, _spec('floor', 'artifact_id', value='syn-floor-set-v6'),
                              {'intermediate': _both(AGGREGATES, 'artifact_id') | _both(PINSETS, 'aggregate')
                               | {'finalized/am.finalized.json:evidence'}}, 'identity'),
    'hidden_manifest_field': (None, _spec('manifest', 'contrasts', 0, 'estimand', value='ratio_j'),
                              {'intermediate': {'finalized/am.finalized.json:contrasts'}}, 'manifest-id'),
    'hidden_floor_guard': (None, _spec('floor', 'idle_drift_guard', 'bound_j', value=Num('0.26')),
                           {'intermediate': _both(AGGREGATES, 'idle_drift_guard') | _both(PINSETS, 'aggregate')},
                           'file'),
    'hidden_floor_value': (None, _spec('floor', 'cells', 0, 'floor_gate_j', value=Num('1.26')),
                           {'registered': _both(AGGREGATES, 'cells') | _both(PINSETS, 'aggregate')}, 'embedded'),
    'hidden_floor_method': (None, _spec('floor', 'method', 'rule', value='sum-envelope'),
                            {'registered': _both(AGGREGATES, 'method') | _both(PINSETS, 'aggregate')}, 'path'),
    'hidden_transport_floor': (None, _spec('floor', 'transport_groups', 3, 'composed_floor_gate_j', value=Num('2.6')),
                               {'registered': _both(AGGREGATES, 'transport_groups') | _both(PINSETS, 'aggregate')},
                               'component'),
    'hidden_component_only': (None, _variant, {'intermediate': _both(PINSETS, 'aggregate')}, 'component'),
    'hidden_producer_extraction_pin': (None, _spec('producers', 0, 'cells', 0, 'absolute', 'drift_allowance_j',
                                                   value=Num('1.0440031334189258')),
                                       {'intermediate': _both(PINSETS, 'producer_plans')}, 'producer-pin'),
    'hidden_producer_acceptance': (None, _spec('producers', 1, 'calibration_acceptance', 'acceptance_id',
                                               value='syn-acceptance-v3'),
                                   {'intermediate': _both(PINSETS, 'producer_plans')}, 'producer-set'),
    'hidden_extraction_cell': (None, _extraction_cell, {'decisions': {'mint/extraction-alpha.json:cells'}},
                               'producer-pin'),
}

FORGED = '0' * 63 + 'f'
# name -> (candidate forgery, the site path the comparator must name)
FORGERIES = {
    'forged_closeout_canonical': (_forged('closeout', ('sources', 'finalized_manifest', 'canonical_json_sha256'),
                                          FORGED), '$.sources.finalized_manifest.canonical_json_sha256'),
    'forged_closeout_identity': (_forged('closeout', ('sources', 'finalized_manifest', 'identity'), 'am-' + FORGED),
                                 '$.sources.finalized_manifest.identity'),
    'forged_replay_canonical': (_forged('closeout', ('sources', 'replay_sidecar', 'canonical_json_sha256'), FORGED),
                                '$.sources.replay_sidecar.canonical_json_sha256'),
    'forged_verdicts_manifest_id': (_forged('verdicts', ('inputs', 'analysis_manifest', 'manifest_id'), 'am-' + FORGED),
                                    '$.inputs.analysis_manifest.manifest_id'),
    'forged_verdicts_file': (_forged('verdicts', ('inputs', 'floor_artifact', 'file_sha256'), FORGED),
                             '$.inputs.floor_artifact.file_sha256'),
    'forged_embedded_copy': (_forged('verdicts', ('inputs', 'floor_artifact', 'embedded_bytes_base64'),
                                     base64.b64encode(b'{"artifact_id": "syn-floor-set-v5", "cells": []}').decode()),
                             '$.inputs.floor_artifact.embedded_bytes_base64'),
    'forged_manifest_id': (_forged('manifest', ('manifest_id',), 'am-' + FORGED), '$.manifest_id'),
    'forged_manifest_path': (_forged('manifest-evidence', ('evidence', 'aggregate_floor_artifact', 'path'),
                                     f'mint/{FORGED}-aggregate-floor.json'), '$.evidence.aggregate_floor_artifact.path'),
    'forged_component_digest': (_forged('pinset', ('aggregate', 'component_artifacts', 1, 'sha256'), FORGED),
                                '$.aggregate.component_artifacts[1].sha256'),
    'forged_producer_pin': (_forged('pinset', ('aggregate', 'component_artifacts', 0, 'producer_pin_sha256'), FORGED),
                            '$.aggregate.component_artifacts[0].producer_pin_sha256'),
    'forged_producer_set': (_forged('pinset', ('aggregate', 'producer_set_sha256'), FORGED),
                            '$.aggregate.producer_set_sha256'),
    'forged_plan_set_pin': (_forged('aggregate', ('provenance', 'calibration_plan', 'sha256'), FORGED),
                            '$.provenance.calibration_plan.sha256'),
}


def build_pair(ref_mut, cand_mut, parent: Path, name: str):
    ref_model, cand_model = derived_model(), derived_model()
    if ref_mut is not None:
        ref_mut(ref_model)
    if cand_mut is not None:
        cand_mut(cand_model)
    return build(ref_model, parent / f'{name}-ref'), build(cand_model, parent / f'{name}-cand')
