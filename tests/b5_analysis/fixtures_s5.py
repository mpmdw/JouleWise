"""S5 synthetic fixtures. Arithmetic inputs and archive bases are module cached.

Arithmetic fixtures use hand-built KeptUnits and synthetic member values.
Pinned fixtures use S0's committed bytes from the real pinned writer/harvest;
S3B supplies authenticated structural counterfactuals and adapter projections.
"""
from __future__ import annotations
import atexit
import contextlib
import copy
from dataclasses import replace
from functools import lru_cache
import json
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise import analysis_engine as engine
from joulewise.analysis_engine.inputs import FloorResolution
from joulewise.b5_analysis.kept_units import Unit, DroppedUnit, CellKeptUnits, KeptUnits
from tests import test_analysis_integration as integration

ROOT = Path(__file__).resolve().parents[2]

@lru_cache(maxsize=1)
def arithmetic_base():
    def capture(*args, **kwargs):
        return engine.load_analysis_inputs(*args, **kwargs)
    with mock.patch.object(integration, 'analyze_claims', side_effect=capture):
        return integration._v3_fixture_artifact()


def arithmetic_inputs(values, second=None, *, removed=(4,), second_removed=None, mde=None, block5=True):
    base = copy.deepcopy(arithmetic_base())
    manifest = copy.deepcopy(base.manifest)
    first = manifest['contrasts'][0]
    first['mde'] = mde
    first['contrast_id'] = 'decode'
    first['metric']['metric_tag'] = 'decode-s5'
    evidence = copy.deepcopy(base.effective)
    second = list(values) if second is None else list(second)
    second_removed = removed if second_removed is None else second_removed
    old_entries = copy.deepcopy(manifest['entries'])
    old_blocks = copy.deepcopy(manifest['blocks'])
    c2 = copy.deepcopy(first)
    c2['contrast_id'] = 'prefill'
    c2['block_ids'] = ['prefill-' + block for block in first['block_ids']]
    c2['metric']['metric_tag'] = 'prefill-s5'
    for row in old_entries:
        old_id = row['entry_id']
        row['entry_id'] = 'prefill-' + old_id
        row['run_id'] = 'prefill-' + row['run_id']
        row['block_id'] = 'prefill-' + row['block_id']
        original = evidence[old_id]
        evidence[row['entry_id']] = replace(original, entry=row, bundle_id=row['run_id'],
            relative_path=row['run_id'], path=Path('runs') / row['run_id'], window_prechecks={})
    for block in old_blocks:
        block['block_id'] = 'prefill-' + block['block_id']
        block['position_entry_ids'] = {p: 'prefill-' + eid for p, eid in block['position_entry_ids'].items()}
    manifest['entries'].extend(old_entries)
    manifest['blocks'].extend(old_blocks)
    manifest['contrasts'].append(c2)
    family = manifest['families'][0]
    family['contrast_ids'] = ['decode', 'prefill']
    family['multiplicity']['m'] = 2
    family['multiplicity']['method'] = 'holm'
    cells = {}
    entries = {row['entry_id']: row for row in manifest['entries']}
    blocks = {row['block_id']: row for row in manifest['blocks']}
    for contrast, ds, dropped_numbers in ((first, values, removed), (c2, second, second_removed)):
        kept, dropped = [], []
        for i, bid in enumerate(contrast['block_ids'], 1):
            run_ids = tuple(entries[blocks[bid]['position_entry_ids'][p]]['run_id'] for p in ('A1','B1','B2','A2'))
            unit = Unit(contrast['contrast_id'], 'quad', bid, run_ids, tuple(range(4)), (None,) * 4)
            if i in dropped_numbers:
                dropped.append(DroppedUnit(**unit.__dict__, codes=('thermal.os_level_nonzero',), families=('thermal',)))
            else:
                kept.append(unit)
            for p, eid in blocks[bid]['position_entry_ids'].items():
                row = evidence[eid]
                row.summary = {**row.summary, 'test_value': 10.0 + (ds[i-1] if p.startswith('B') else 0.0)}
        cid = contrast['contrast_id']
        cells[cid] = CellKeptUnits(cid, True, {'quad': 10}, {'quad': 5}, {'quad': tuple(kept)}, tuple(dropped), 0, len(kept))
    units = KeptUnits(SimpleNamespace(pack='gamma'), '1'*64, '2'*64, '3'*64, cells, {}, {})
    return replace(base, manifest=manifest, effective=evidence, registered=evidence,
                   kept_quads=cells if block5 else None, kept_units=units if block5 else None)


@contextlib.contextmanager
def arithmetic_seams(inputs, *, floor=1.0):
    resolution = FloorResolution(status='exact', artifact_id='df-v3-test', artifact_sha256=inputs.floor_sha256,
        source_cell_ids=('floor-a',), transport_group_id=None, transport_rule_id=None,
        floor_abs_j=floor, floor_cmp_j=floor, floor_gate_j=floor, reason_codes=())
    with mock.patch.object(engine, 'metric_value', side_effect=lambda summary, metric: summary['test_value']), \
         mock.patch.object(engine, 'window_evidence_precheck', return_value={'reasons': ()}), \
         mock.patch.object(engine, 'governed_stochastic_variance', return_value=((), ())), \
         mock.patch.object(engine, 'deterministic_bounds', return_value=({'E_interpolation_joint_edge_bound_j': .025}, ())), \
         mock.patch.object(engine, '_resolve_contrast_floor', return_value=[resolution,resolution]), \
         mock.patch.object(engine, 'load_analysis_inputs', return_value=inputs), \
         mock.patch.object(engine, 'sibling_floor_pinset', return_value=None):
        yield


def prepared_pair(inputs):
    prepared = {row['contrast_id']: engine._prepare_contrast_v3(inputs, row, None, None, evidence_class='current')
                for row in inputs.manifest['contrasts']}
    _, adjusted = engine._family_adjustments(inputs.manifest, prepared)
    evaluated = {cid: engine._evaluation(p, p['estimate'], adjusted[cid], engine._base_reasons(p)) for cid, p in prepared.items()}
    loo = engine._loo_family(inputs, inputs.manifest['families'][0], prepared, adjusted, evaluated, None)
    return prepared, adjusted, evaluated, loo


@lru_cache(maxsize=None)
def pinned_window(name='GAMMA_STD'):
    from tests.b5_analysis import fixtures_s3
    return fixtures_s3.cached(name)


def pinned_handle(name='GAMMA_STD'):
    from tests.b5_analysis import fixtures_s3b
    return fixtures_s3b.original_handle(pinned_window(name))


@contextlib.contextmanager
def loader_case(*, removed=(4,), reasons=()):
    """Hand-built loader boundary: genuine member loop, named downstream doubles."""
    import hashlib
    import tempfile
    from joulewise.analysis_engine import inputs as im
    from joulewise.whole_window import ArchiveContext
    from joulewise.analysis_engine.inputs import AuthenticatedFloorArtifact, FloorEvidenceBinding
    with tempfile.TemporaryDirectory(prefix='s5-loader-') as temporary:
        root=Path(temporary);runs=root/'runs';runs.mkdir()
        (runs/'.joulewise-launch-lineage.json').write_text(json.dumps({'schema_version':'joulewise.hazard_window_lineage_locator.v1'}))
        loaded=arithmetic_inputs([3.1,2.9,3.3,3.,2.8,3.2,3.1,2.9,3.,2.7],removed=removed)
        manifest_path=root/'manifest.json';manifest_path.write_text(json.dumps(loaded.manifest))
        floor_path=root/'floor.json';floor_path.write_bytes(loaded.floor_artifact_bytes)
        for row in loaded.effective.values():
            row.path=runs/row.bundle_id;row.path.mkdir()
            (row.path/'summary_metrics.json').write_text('{"synthetic_extreme": 1e99}')
        archive_root=root/'archive';archive_root.mkdir()
        window=SimpleNamespace(pack='gamma',archive_root=archive_root,harvest_pin='4'*40,
            harvest_record_sha256='5'*64,claim_runs_root=runs)
        units=replace(loaded.kept_units,window=window)
        context=ArchiveContext(archive_root,window_bracket={'status':'passed','b_fiducial_s':.04},
            removed_bundle_ids=units.removed_run_ids())
        archive=SimpleNamespace(window=window,output_bytes=lambda name: b'' if name.endswith('.jsonl') else b'{}')
        session=SimpleNamespace(ready=True,summary_for=lambda bid: next(row.summary for row in loaded.effective.values() if row.bundle_id==bid),
            provenance_for=lambda bid: {'operative_fiducial_bound_s':.04})
        floor=AuthenticatedFloorArtifact(loaded.floor_artifact,loaded.floor_artifact_bytes,loaded.floor_sha256,frozenset())
        reader_calls=[]
        def read(entry,path,*args,**kwargs):
            reader_calls.append(entry['run_id'])
            if entry['run_id'] in units.removed_run_ids():raise AssertionError('removed bundle opened')
            row=loaded.effective[entry['entry_id']]
            if not path.is_dir():return replace(row,inclusion_status='excluded',summary=None,base_reason_codes=('bundle_missing',))
            if path.name != row.bundle_id:
                return replace(row, bundle_id=path.name, relative_path=path.name, path=path,
                               raw_config=json.loads((path / 'config.json').read_bytes()))
            return row
        def load_object(path, label):
            if path == manifest_path:
                return loaded.manifest, b'{}'
            for row in loaded.registered.values():
                if path.as_posix().endswith(row.entry['config']):
                    return row.raw_config, b'{}'
            return {}, b'{}'
        case=SimpleNamespace(root=root,runs=runs,manifest_path=manifest_path,floor_path=floor_path,loaded=loaded,
            units=units,context=context,archive=archive,reader_calls=reader_calls,session=session)
        case.call=lambda **kwargs: im.load_analysis_inputs(manifest_path,runs,floor_path,
            **{'strict_validator':lambda *_:[],'kept_units':units,'archive_contexts':{str(runs.resolve()):context},
               'gamma_archive':archive,**kwargs})
        with mock.patch.object(im,'is_hazard_runs_root',side_effect=lambda path:Path(path).resolve()==runs.resolve()), \
             mock.patch.object(im,'load_manifest',return_value=(loaded.manifest,'b'*64)), \
             mock.patch.object(im,'load_floor_artifact',return_value=floor), \
             mock.patch.object(im,'bind_floor_artifact_evidence',return_value=FloorEvidenceBinding(frozenset(),{},{},frozenset(),{},())), \
             mock.patch.object(im,'_load_json_object',side_effect=load_object), \
             mock.patch.object(im,'supersession_visibility_scan',return_value={'status':'clean'}), \
             mock.patch.object(im,'_campaign_claim_records',return_value={}), \
             mock.patch.object(im,'_campaign_cooldown_evidence',return_value={}), \
             mock.patch.object(im,'_enforce_registered_realized_identity',return_value={}), \
             mock.patch.object(im,'_read_bundle',side_effect=read), \
             mock.patch.object(im,'AuthenticatedConsumptionSession',autospec=True,return_value=session), \
             mock.patch.object(im,'whole_window_refusal_reasons',return_value=reasons), \
             mock.patch.object(im,'whole_window_drift_allowances',return_value=SimpleNamespace(status='allowances',allowances={})):
            yield case


@lru_cache(maxsize=1)
def finalization_base():
    import tempfile
    from tests.test_analysis_finalizer import install_synthetic_finalization_fixture
    tmp=tempfile.TemporaryDirectory(prefix='s5-finalize-base-');atexit.register(tmp.cleanup)
    return install_synthetic_finalization_fixture(Path(tmp.name),shared_family=True)


@lru_cache(maxsize=None)
def _finalization_case(*, removed=(4,)):
    """Finalization harness + real exclusions function and real KeptUnits reader.

    This is a structural archive, not a real pinned-harvest integration fixture.
    """
    import hashlib
    import shutil
    import tempfile
    from joulewise.analysis_engine.inputs import planned_contrast_units
    from joulewise.b5_analysis.archive import ArchiveHandle
    from joulewise.b5_analysis.kept_units import load_kept_units
    from joulewise.b5_analysis.bracket import WindowBracket
    from joulewise.flags.catalog import load_catalog
    from joulewise.flags.exclusions import compute
    from joulewise.whole_window import ArchiveContext
    from joulewise.calibration_ledger import canonical_json_bytes
    from tests.test_analysis_finalizer import _write_json
    tmp=tempfile.TemporaryDirectory(prefix='s5-finalize-');atexit.register(tmp.cleanup)
    root=Path(tmp.name)
    from tests.test_analysis_finalizer import install_synthetic_finalization_fixture
    fixture=install_synthetic_finalization_fixture(root,shared_family=True)
    (fixture['runs_root']/'.joulewise-launch-lineage.json').write_text(json.dumps({'schema_version':'joulewise.hazard_window_lineage_locator.v1'}))
    prospective=fixture['prospective'];planned=planned_contrast_units(prospective)
    roster={'schema':'joulewise.b5_harvest_roster.v1','pack_id':'s5-gamma','plan_id':prospective['plan']['plan_id'],
        'attempt':1,'cells':[],'members':[]}
    flags=[]
    for contrast in prospective['contrasts']:
        cid=contrast['contrast_id'];roster['cells'].append({'cell_id':cid,'target':True,'strata':['quad']})
        for member in contrast['members']:
            roster['members'].append({'run_id':member['run_id'],'stage_id':'synthetic',
                'units':[{'cell_id':cid,'stratum':'quad','unit_id':member['block_id']}]})
            if member['block_number'] in removed and member['position']=='A1':
                flags.append({'flag_id':'drop-'+member['run_id'],'code':'thermal.os_level_nonzero',
                    'scope':{'level':'member','plan_id':roster['plan_id'],'attempt':1,'run_id':member['run_id'],
                             'bundle_id':None,'stage_id':None},'interval':{'monotonic_ns':None}})
    catalog=load_catalog(ROOT/'configs/campaigns/v5_claim_25g83/flag_catalog.json')
    exclusions=compute(flags,roster,{},catalog)
    archive_root=root/'archive';archive_root.mkdir(exist_ok=True)
    outputs={};sources={}
    def output(name,value,raw=None):
        raw=json.dumps(value).encode() if raw is None else raw
        path=archive_root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        outputs[name]=hashlib.sha256(raw).hexdigest()
    output('derived/exclusions.json',exclusions);output('derived/roster.json',roster)
    output('derived/flags.jsonl',None,b''.join(json.dumps(flag).encode()+b'\n' for flag in flags))
    bracket=json.loads(fixture['bracket_path'].read_bytes())
    output('derived/bracket-binding.json',bracket,fixture['bracket_path'].read_bytes())
    output('derived/terminal-pin.json',bracket['terminal_head'])
    for name,path in (('sources/ledger/calibration_observation_ledger.jsonl',fixture['ledger_path']),
                      ('sources/inputs/acceptance.json',fixture['acceptance_path'])):
        dest=archive_root/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
        sources[name.removeprefix('sources/')]=hashlib.sha256(dest.read_bytes()).hexdigest()
    (archive_root/'sources/SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name,digest in sources.items()))
    harvest={'attempt':1,'plan_id':roster['plan_id'],'outputs':outputs}
    _write_json(archive_root/'harvest.json',harvest)
    window=SimpleNamespace(pack='gamma',pack_id='s5-gamma',claim_runs_root=fixture['runs_root'],archive_root=archive_root,
        harvest_record_sha256=hashlib.sha256((archive_root/'harvest.json').read_bytes()).hexdigest(),harvest_pin='4'*40,
        governed_e3=False,record=SimpleNamespace(record_shape='pin2'))
    archive=ArchiveHandle(window,harvest,{})
    units=load_kept_units(archive,sealed_catalog_sha256=catalog.sha256,planned_units=planned)
    verdict=json.loads(fixture['verdict_path'].read_bytes())
    assessment=verdict['idle_admission_core']['instrument_calibration_bracket']
    context=ArchiveContext(archive_root,window_bracket=assessment,removed_bundle_ids=units.removed_run_ids())
    wb=WindowBracket(window,'sealed',assessment,assessment['b_fiducial_s'],bracket['terminal_head']['sequence'],
        hashlib.sha256(fixture['ledger_path'].read_bytes()).hexdigest(),'no_harvest_digest',
        hashlib.sha256((archive_root/'sources/SHA256SUMS').read_bytes()).hexdigest())
    fixture['block5_inputs']={'gamma_archive':archive,'kept_units':units,
        'archive_contexts':{str(fixture['runs_root'].resolve()):context},'brackets':{'gamma':wb}}
    fixture['archive']=archive;fixture['units']=units
    return fixture


@contextlib.contextmanager
def finalization_case(*, removed=(4,)):
    fixture=_finalization_case(removed=tuple(removed))
    paths=[fixture['verdict_path'],fixture['ledger_path'],fixture['bracket_path'],fixture['floor_path'],
           fixture['runs_root']/'campaign_log.jsonl']
    originals={path:path.read_bytes() for path in paths}
    try:
        yield fixture
    finally:
        for path,raw in originals.items():path.write_bytes(raw)


@lru_cache(maxsize=1)
def indexed_gamma_case():
    """S0 pinned GAMMA_STD with S2's consistent synthetic capture adapter inputs.

    Selection requires one usable second-seal entry for each pack. ALPHA/BETA
    entries authenticate index history; only the GAMMA archive is consumed.
    """
    import tempfile
    from tests.b5_analysis import fixtures as s0, fixtures_s2 as s2
    gamma = s2.build_named('GAMMA_STD')
    others = [pinned_window('ALPHA_STD'), pinned_window('BETA_STD')]
    tmp = tempfile.TemporaryDirectory(prefix='s5-real-builder-'); atexit.register(tmp.cleanup)
    root = Path(tmp.name)
    index = root / 'window-index.json'
    attempts = [window.entry_data for window in (*others, gamma)]
    # A complete history: S0's BETA window is attempt 6, so attempts 1 to 5 are
    # entered as no-archive attempts (as tests.b5_analysis.test_windows does).
    beta = next(row for row in attempts if row['pack'] == 'beta')
    attempts = [{**beta, 'attempt': n, 'verdict': 'NO_COLLECTION', 'entry_kind': 'no_archive',
                 'archive_root': None, 'harvest_record_sha256': None, 'claim_usable': False,
                 'record_citation': f'synthetic.md:{n}'} for n in range(1, beta['attempt'])] + attempts
    index.write_text(json.dumps({'schema': 'joulewise.b5_window_index.v1', 'attempts': attempts}))
    roster = json.loads((gamma.archive / 'derived/roster.json').read_bytes())
    quads = {}
    for member in roster['members']:
        for unit in member.get('units', []):
            if unit['stratum'] == 'quad':
                quads.setdefault(unit['cell_id'], {}).setdefault(unit['unit_id'], []).append(member['run_id'])
    manifest = {'contrasts': [{'contrast_id': cid, 'block_ids': list(blocks),
        'members': [{'block_id': bid, 'run_id': run, 'order_index': i}
                    for bid, runs in blocks.items() for i, run in enumerate(runs)]}
        for cid, blocks in quads.items()]}
    path = root / 'manifest.json'; path.write_text(json.dumps(manifest))
    tree = gamma.archive / f'sources/repo/configs/campaigns/{gamma.entry.pack_id}/plan_tree.json'
    return SimpleNamespace(gamma=gamma, index=index, manifest_path=path, manifest=manifest,
        pack_table=s0.PACK_TABLE, tree_sha256=s0.sha(tree), root=root)


def real_indexed_gamma_inputs():
    from joulewise.analysis_engine.inputs import block5_claim_gate_inputs
    from tests.b5_analysis import fixtures_s2 as s2
    case = indexed_gamma_case()
    # S2's cached claim root is shared with other modules of this package: the
    # locator that makes it a block-5 root exists only for the builder call.
    locator = case.gamma.claim / '.joulewise-launch-lineage.json'
    locator.write_text(json.dumps({'schema_version': 'joulewise.hazard_window_lineage_locator.v1'}))
    try:
        with s2.capture_adapter():
            return block5_claim_gate_inputs(case.index, case.manifest_path, case.gamma.claim,
                _test_pack_table=case.pack_table, _test_synthetic_plan_tree_sha256=case.tree_sha256)
    finally:
        locator.unlink()


@contextlib.contextmanager
def floor_dispatch_case(*, removed=False):
    """Hand-built floor-binding boundary: real dispatch, synthetic reader/session projections."""
    import tempfile
    from joulewise.analysis_engine import inputs as im
    from joulewise.whole_window import ArchiveContext
    with tempfile.TemporaryDirectory(prefix='s5-floor-dispatch-') as temporary:
        root = Path(temporary)
        roots = {rid: root / rid for rid in ('first', 'second')}
        for path in roots.values(): path.mkdir()
        contexts = {str(path.resolve()): ArchiveContext(root / ('archive-' + rid),
            window_bracket={'status': 'passed', 'b_fiducial_s': .02 if rid == 'first' else .06},
            removed_bundle_ids=frozenset({'member-' + rid}) if removed else frozenset())
            for rid, path in roots.items()}
        artifact = {'provenance': {'calibration_plan': {'sha256': '3' * 64}}, 'cells': []}
        stack_hash = im.canonical_domain_sha256(im.STACK_IDENTITY_DOMAIN, {})
        for rid in roots:
            artifact['cells'].append({'cell_id': rid, 'key': {'metric': 'synthetic', 'window_class': 'whole_request'},
                'source_regime': {'stack_identity_sha256': stack_hash},
                'absolute': {'bundle_observations': [{'bundle_id': 'member-' + rid,
                    'bundle_sha256': '1' * 64, 'config_sha256': '2' * 64,
                    'metric_value_j': 42. if rid == 'first' else 99.}]},
                'provenance': {'absolute': {'evidence_root_id': rid}}})
        floor = root / 'floor.json'; floor.write_text(json.dumps(artifact))
        cap = im.AuthenticatedFloorArtifact(artifact, floor.read_bytes(), 'a' * 64, frozenset(roots))
        sessions = {}
        def session(path, members, **kwargs):
            value = 42. if Path(path).name == 'first' else 99.
            bound = contexts[str(Path(path).resolve())].window_bracket['b_fiducial_s']
            result = SimpleNamespace(ready=True, summary_for=lambda bid: {'status': 'succeeded', 'value': value},
                provenance_for=lambda bid: {'operative_fiducial_bound_s': bound})
            sessions[Path(path).name] = (result, members, kwargs)
            return result
        reader = SimpleNamespace(raw_summary=lambda: {'status': 'succeeded', 'value': 1.},
                                 raw_metadata=lambda: {}, raw_config=lambda: {})
        seen = []
        def metric(summary, name):
            seen.append(summary['value']); return summary['value']
        with mock.patch.object(im, 'is_hazard_runs_root', return_value=True), \
             mock.patch.object(im, 'AuthenticatedConsumptionSession', side_effect=session), \
             mock.patch.object(im, 'whole_window_refusal_reasons', return_value=()), \
             mock.patch.object(im, '_campaign_order_binding_problems', return_value=()), \
             mock.patch.object(im, 'BundleReader', return_value=reader) as readers, \
             mock.patch.object(im, '_source_provenance_admission_problems', return_value=[]), \
             mock.patch.object(im, 'custody_telemetry_identity', return_value=SimpleNamespace(custody_bound_config=False, mock_config=False)), \
             mock.patch.object(im, 'anchor_fallback_member_unusable', return_value=False), \
             mock.patch.object(im, 'complete_bundle_sha256', return_value='1' * 64), \
             mock.patch.object(im, '_sha256_file', return_value='2' * 64), \
             mock.patch.object(im, '_floor_metric_value', side_effect=metric), \
             mock.patch.object(im, 'scientific_config_identity', return_value={'synthetic': True}), \
             mock.patch.object(im, 'floor_stack_identity', return_value={}), \
             mock.patch.object(im, '_calibration_order_tags', return_value={'plan_sha256': '3' * 64}):
            yield SimpleNamespace(artifact=artifact, floor=floor, roots=roots, contexts=contexts,
                cap=cap, sessions=sessions, seen=seen, readers=readers,
                call=lambda: im.bind_floor_artifact_evidence(artifact, floor, roots,
                    strict_validator=lambda *_: [], _authenticated_floor=cap, archive_contexts=contexts))
