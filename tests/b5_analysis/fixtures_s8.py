"""S8 cached synthetic windows and explicitly named authentication seams."""
from __future__ import annotations
import atexit
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest import mock
from joulewise import whole_window as ww
from joulewise import paper_reported_energy_issuer as issuer
from joulewise.b5_analysis.kept_units import KeptUnits
from tests.b5_analysis.test_reported_cell import case
from tests.test_paper_reported_energy import synthetic_input
from tests.test_whole_window import TwoScopeRefusalTests


@lru_cache(maxsize=1)
def synthetic_pack():
    tmp=tempfile.TemporaryDirectory(prefix='s8-pack-');atexit.register(tmp.cleanup)
    root=Path(tmp.name)
    spec=synthetic_input(prefill_length=2048)['spec']
    cells={}; summaries={}
    for i,c in enumerate(spec['reported_energy_cells']):
        _,rows,_,k=case((6,),(5,9))
        cid=f's8-{i}' if i!=1 else 's8-p42-cell'
        unit_cell=replace(k.cell,cell_id=cid,target=i!=1,
            kept={s:tuple(replace(u,cell_id=cid) for u in units) for s,units in k.cell.kept.items()},
            dropped=tuple(replace(u,cell_id=cid) for u in k.cell.dropped))
        # Long-prefill uses its own bundle ids; units must follow that census.
        all_units=[u for us in unit_cell.kept.values() for u in us]+list(unit_cell.dropped)
        def remap(u):
            return replace(u,run_ids=tuple(c['members'][n-1]['bundle_id'] for n in u.positions))
        unit_cell=replace(unit_cell,kept={s:tuple(remap(u) for u in us) for s,us in unit_cell.kept.items()},
                          dropped=tuple(remap(u) for u in unit_cell.dropped))
        cells[cid]=unit_cell
        spec['cells'][2*i]['condition_family_id']=cid
        spec['cells'][2*i+1]['condition_family_id']=cid
        for m in c['members']:
            bid=m['bundle_id'];path=root/bid;path.mkdir(exist_ok=True)
            summary=TwoScopeRefusalTests._summary(10+m['ordinal']/100,bound_s=.04,half_width_j=.2)
            summary['phase_energy_j']['prefill']=11+m['ordinal']/100
            summary['energy_anchor_shift_envelopes']['/phase_energy_j/prefill']=TwoScopeRefusalTests._envelope(11+m['ordinal']/100,.04,.2)
            summary['window_evidence_precheck']['phase']['prefill']=deepcopy(summary['window_evidence_precheck']['phase']['decode'])
            metadata={'uncertainty_evidence':{'schema_version':'joulewise.uncertainty_evidence.v3','clock_anchor':{'method':'powermetrics_native_second_rate_aware_set_membership_v1'}},'model':{'name':'Qwen3-1.7B-4bit'},'workload_observed':{'token_count':2560,'output_token_count':512},
                      'workload_provenance':{'prompt':{'realized_token_count':2048},'tokenizer':{'identifier':'synthetic'},
                        'output_policy':{'name':'fixed','requested_tokens':512},'sampler':{}}}
            for name,v in [('summary_metrics.json',summary),('metadata.json',metadata),('config.json',{})]:
                (path/name).write_text(json.dumps(v))
            (path/'events.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in [
                {'event_type':'phase_end','phase':'tokenize','message':'','timestamp_s':1.0,'metadata':{'prompt_tokens':2048}},
                {'event_type':'phase_start','phase':'prefill','message':'','timestamp_s':2.0,'metadata':{'prompt_tokens':2048}}]))
            summaries[bid]=summary
    window=SimpleNamespace(pack='alpha',plan_id='synthetic-plan',attempt=1,harvest_pin='a'*40)
    exclusions_raw=(json.dumps({'cells':{cid:{'kept_units':{s:[u.unit_id for u in us] for s,us in c.kept.items()},
        'removed_units':[u.unit_id for u in c.dropped]} for cid,c in cells.items()}},sort_keys=True)+'\n').encode()
    (root/'exclusions.json').write_bytes(exclusions_raw)
    kept=KeptUnits(window,hashlib.sha256(exclusions_raw).hexdigest(),'b'*64,'c'*64,cells,{}, {})
    session=SimpleNamespace(ready=True,refusal_reasons=(),summary_for=lambda bid:summaries.get(bid),
        provenance_for=lambda bid:{'operative_fiducial_bound_s':.04})
    context=ww.ArchiveContext(root,window_bracket={'b_fiducial_s':.04})
    return SimpleNamespace(root=root,spec=spec,kept=kept,session=session,context=context,summaries=summaries)


@contextmanager
def pack_seams(fixture, *, p42=True):
    real=issuer.inputs.window_evidence_precheck
    def precheck(evidence,metric):
        value=real(evidence,metric)
        if p42 and 'prefill-p42-' in metric['metric_tag']:
            value={**value,'eligible':False,'reasons':['window_evidence_precheck_missing']}
        return value
    with mock.patch.object(issuer,'AuthenticatedConsumptionSession',return_value=fixture.session), \
         mock.patch.object(issuer,'whole_window_drift_allowances',return_value=ww.WholeWindowDriftAllowanceResult('allowances',{'gross_energy':{'allowance_j':.1}})), \
         mock.patch.object(issuer.inputs,'campaign_cooldown_evidence',return_value={bid:{'verified':True,'result':'recovered'} for bid in fixture.summaries}), \
         mock.patch.object(issuer.inputs,'realized_scientific_identity',side_effect=lambda config,metadata:{'model':metadata['model']}), \
         mock.patch.object(issuer.inputs,'window_evidence_precheck',side_effect=precheck):
        yield


def project(fixture,**kwargs):
    return issuer.project_pack(fixture.spec,fixture.kept,context=fixture.context,runs_root=fixture.root,
        evaluation_basis_sha256='c'*64,selection_sha256='a'*64,prompt_pin_sha256='b'*64,
        strict_validator=lambda path,strict:(),**kwargs)


@lru_cache(maxsize=1)
def production_member():
    from tests.test_whole_window_selection import MaxBracketConsumptionTests
    from tests.test_whole_window import _fixture_snapshot
    from joulewise.powermetrics_fiducial import PROTOCOL_ID
    from joulewise.reduce import _rederive_summary_for_authenticated_fiducial_bound
    tmp=tempfile.TemporaryDirectory(prefix='s8-production-');atexit.register(tmp.cleanup)
    root=Path(tmp.name)
    helper=MaxBracketConsumptionTests
    bundle,stored,pre,operative=helper._build_v052_bundle(root,protocol_id=PROTOCOL_ID,v3_measurement=True)
    independent=_rederive_summary_for_authenticated_fiducial_bound(bundle,authenticated_fiducial_bound_s=operative,
        _instrument_calibration_physics_cache=helper._physics_cache)
    snapshot,_=_fixture_snapshot([])
    context=ww.ArchiveContext(root,window_bracket=TwoScopeRefusalTests._bracket(operative))
    session=ww.AuthenticatedConsumptionSession(bundle.parent,{bundle.name},calibration_ledger_snapshot=snapshot,archive_context=context)
    # Bracket/strict/calibration authentication are explicit seams; production
    # reducer dispatch and the session's dominated-member reduction are real.
    with mock.patch.object(ww,'calibration_bracket_for_bundles',return_value=(TwoScopeRefusalTests._bracket(operative),())), \
         mock.patch.object(ww,'_current_strict_summary',return_value=True), \
         mock.patch.object(ww,'_verify_instrument_calibration',return_value=(pre,None)):
        session._prepare(bundle_paths={bundle.name:bundle},policy=SimpleNamespace(calibration_bracketing=object()))
    cell,rows,binding,k=case()
    cell=deepcopy(cell);cell['members'][0]['bundle_id']=bundle.name
    k=replace(k,kept_repeat_ordinals=(1,),removed_repeat_ordinals=tuple(range(2,11)),
              kept_quad_ordinals=(),removed_quad_ordinals=tuple(tuple(range(i,i+4)) for i in range(11,51,4)))
    return SimpleNamespace(root=root,bundle=bundle,stored=stored,independent=independent,pre=pre,operative=operative,
        session=session,context=context,cell=cell,kept=k,binding=binding)


@contextmanager
def replay_math_seams(loaded):
    from joulewise import analysis_engine as engine
    from joulewise.analysis_engine.inputs import FloorResolution
    from tests.b5_analysis import fixtures_s5 as s5
    def resolve(inputs_,contrast,*args,**kwargs):
        cid='floor-a' if contrast['contrast_id']=='decode' else 'floor-b'
        resolution=FloorResolution(status='exact',artifact_id=loaded.floor_artifact['artifact_id'],
            artifact_sha256=loaded.floor_sha256,source_cell_ids=(cid,),transport_group_id=None,
            transport_rule_id=None,floor_abs_j=1.,floor_cmp_j=1.,floor_gate_j=1.,reason_codes=())
        return [resolution,resolution]
    with s5.arithmetic_seams(loaded),mock.patch.object(engine,'_resolve_contrast_floor',side_effect=resolve), \
         mock.patch.object(engine,'deterministic_bounds',return_value=({'E_clock_anchor_shift_bound_j':.01,'E_interpolation_joint_edge_bound_j':.025},())):
        yield


@lru_cache(maxsize=1)
def fill_fixture():
    """Copy-boundary fixture: real engine arithmetic, nine kept quads each."""
    from joulewise import analysis_engine as engine
    from joulewise.analysis_engine.artifact import render_claim_verdicts
    from tests.b5_analysis import fixtures_s5 as s5
    from tests.test_detection_floor import make_artifact, make_cell
    tmp=tempfile.TemporaryDirectory(prefix='s8-fill-');atexit.register(tmp.cleanup)
    root=Path(tmp.name)
    loaded=s5.arithmetic_inputs([2+.01*i for i in range(10)])
    floor=make_artifact([make_cell(cell_id='floor-a'),make_cell(cell_id='floor-b',condition='cf-2')])
    floor_raw=(json.dumps(floor,indent=2)+'\n').encode()
    manifest=deepcopy(loaded.manifest)
    manifest['evidence']={'analysed_attempt_exclusions':{'sha256':loaded.kept_units.exclusions_sha256},
        'aggregate_floor_artifact':{'path':'floor.json','sha256':hashlib.sha256(floor_raw).hexdigest()}}
    manifest_raw=(json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n').encode()
    loaded=replace(loaded,manifest=manifest,manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
        floor_artifact=floor,floor_artifact_bytes=floor_raw,floor_sha256=hashlib.sha256(floor_raw).hexdigest())
    with replay_math_seams(loaded):
        artifact=engine.analyze_claims(root/'manifest.json',Path('runs'),root/'floor.json',strict_validator=lambda *a:())
    raw=render_claim_verdicts(artifact)
    for name,value in [('manifest.json',manifest_raw),('floor.json',floor_raw),('verdicts.json',raw)]:
        (root/name).write_bytes(value)
    return SimpleNamespace(root=root,loaded=loaded,artifact=artifact,raw=raw,manifest=manifest,
        manifest_raw=manifest_raw,floor_raw=floor_raw,kept={cid:loaded.kept_units.for_contrast(cid) for cid in ('decode','prefill')},
        exclusions_sha256=loaded.kept_units.exclusions_sha256)


@lru_cache(maxsize=1)
def replay_fixture():
    """Nearest S5 indexed/real-engine fixture; loader physics remains a seam."""
    import subprocess
    from joulewise import paper_custody as custody, analysis_engine as engine
    from joulewise.analysis_engine.artifact import render_claim_verdicts, validate_claim_verdicts
    from joulewise.analysis_engine.claim_side_bound import produce_claim_side_bound
    from tests.b5_analysis import fixtures_s5 as s5
    from tests.git_fixture import init_git_fixture
    tmp=tempfile.TemporaryDirectory(prefix='s8-replay-');atexit.register(tmp.cleanup)
    root=Path(tmp.name);repo=root/'repo';repo.mkdir()
    indexed=s5.indexed_gamma_case()
    # S5's indexed GAMMA is floor-shaped and deliberately refuses. Its
    # positive structural finalization fixture supplies the builder seam.
    built=s5._finalization_case()['block5_inputs']
    index_path=repo/custody._B5_WINDOW_INDEX_PATH;index_path.parent.mkdir(parents=True)
    index_path.write_bytes(indexed.index.read_bytes())
    init_git_fixture(repo)
    subprocess.run(['git','-C',str(repo),'add','.'],check=True,capture_output=True)
    subprocess.run(['git','-C',str(repo),'-c','user.name=Synthetic','-c','user.email=synthetic@example.invalid','commit','-m','synthetic index'],check=True,capture_output=True)
    head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    loaded=s5.arithmetic_inputs([2+.01*i for i in range(10)])
    from tests.test_detection_floor import make_artifact, make_cell
    floor=make_artifact([make_cell(cell_id='floor-a'),make_cell(cell_id='floor-b',condition='cf-2')])
    floor_raw=(json.dumps(floor,indent=2)+'\n').encode()
    loaded=replace(loaded,floor_artifact=floor,floor_artifact_bytes=floor_raw,
                   floor_sha256=hashlib.sha256(floor_raw).hexdigest())
    manifest=deepcopy(loaded.manifest)
    manifest['evidence']={'analysed_attempt_exclusions':{'sha256':loaded.kept_units.exclusions_sha256}}
    manifest_raw=(json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n').encode()
    loaded=replace(loaded,manifest=manifest,manifest_sha256=hashlib.sha256(manifest_raw).hexdigest())
    path=root/'manifest.json';path.write_bytes(manifest_raw)
    floor_path=root/'floor.json';floor_path.write_bytes(loaded.floor_artifact_bytes)
    with replay_math_seams(loaded):
        artifact=engine.analyze_claims(path,indexed.gamma.claim,floor_path,strict_validator=lambda *a:(),
            output_path=None,kept_units=built['kept_units'],archive_contexts=built['archive_contexts'],
            gamma_archive=built['gamma_archive'],neg8_harvest_archive=built['gamma_archive'].window.archive_root,
            legacy_l1_mechanics=False)
    assert validate_claim_verdicts(artifact,frozen_manifest=manifest)==[]
    raw=render_claim_verdicts(artifact);(root/'verdicts.json').write_bytes(raw)
    sources=tuple(custody._BoundFile('runs_root',Path(name),hashlib.sha256(value).hexdigest(),role,'generated')
        for name,value,role in [('manifest.json',manifest_raw,custody.InputRole.FINALIZED_MANIFEST),
        ('floor.json',loaded.floor_artifact_bytes,custody.InputRole.FLOOR_ARTIFACT)])
    raws={custody.InputRole.FINALIZED_MANIFEST:manifest_raw,custody.InputRole.FLOOR_ARTIFACT:loaded.floor_artifact_bytes,
          custody.InputRole.CLAIM_VERDICTS:raw}
    raws[custody.InputRole.CLAIM_SIDE_BOUND]=produce_claim_side_bound(raw,finalized_manifest=manifest,floor_artifact=loaded.floor_artifact)
    roots={'a10':'alpha','window_c':'beta'}
    request=custody.claim_replay_request(claim_verdicts_sha256=hashlib.sha256(raw).hexdigest(),
        analysis_manifest_sha256=loaded.manifest_sha256,floor_artifact_sha256=loaded.floor_sha256,
        window_index_sha256=hashlib.sha256(index_path.read_bytes()).hexdigest(),evidence_roots=roots)
    raws[custody.InputRole.CLAIM_REPLAY_REQUEST]=request
    ctx=custody._GateContext('claim_evidence','synthetic.claim','production','claim-evidence.v1',
        tuple(c['contrast_id'] for c in artifact['contrasts']),repo,root,head,sources,(),raws,None)
    return SimpleNamespace(root=root,repo=repo,indexed=indexed,built=built,loaded=loaded,artifact=artifact,raw=raw,
        manifest=manifest,manifest_raw=manifest_raw,ctx=ctx,request=request,index_path=index_path)


@contextmanager
def replay_seams(fixture):
    """Real engine + index selection; S5 loader/physics and input builder seams."""
    from joulewise.b5_analysis import windows, archive
    from joulewise.analysis_engine import inputs
    from tests.b5_analysis import fixtures_s5 as s5
    real_index,real_record=windows.load_window_index,archive.open_attempt_record
    def index(path,**kw):return real_index(path,**kw,pack_table=fixture.indexed.pack_table)
    def record(entry,**kw):return real_record(entry,**kw,pack_table=fixture.indexed.pack_table)
    with mock.patch.object(windows,'load_window_index',side_effect=index), \
         mock.patch.object(archive,'open_attempt_record',side_effect=record), \
         mock.patch.object(inputs,'block5_claim_gate_inputs',return_value=fixture.built), \
         replay_math_seams(fixture.loaded):
        yield


@lru_cache(maxsize=1)
def indexed_reported_fixture():
    """Full indexed S8 composition; only the synthetic spec registration differs."""
    import shutil
    from tests.b5_analysis import fixtures as s0, fixtures_s2 as s2
    from tests.b5_analysis.test_floor_kept_units import indexed_fixture, family
    from tests.test_paper_reported_energy import synthetic_spec
    from joulewise.b5 import harvest
    from joulewise.flags.catalog import load_catalog
    from joulewise.flags.exclusions import compute
    tmp=tempfile.TemporaryDirectory(prefix='s8-indexed-gate-');atexit.register(tmp.cleanup)
    root=Path(tmp.name);base=indexed_fixture();window=s2.fork(base.window,root/'beta')
    pack=window.archive/'sources/repo/configs/campaigns'/window.entry.pack_id
    spec=deepcopy(base.spec)
    third=deepcopy(spec['cells'][:2])
    for i,cell in enumerate(third):
     cell['cell_id']='s8-long-'+cell['cell_id'];cell['metric']='phase_energy_j.prefill';cell['target_precheck_path']=['phase','prefill'];family(cell,'df-s8-long')
    spec['cells'].extend(third)
    reported=synthetic_spec('qwen3-8b',2048)
    spec['reported_energy_registration']=reported['reported_energy_registration']
    spec['reported_energy_cells']=reported['reported_energy_cells']
    for i,cell in enumerate(spec['reported_energy_cells']):
     absolute,comparative=spec['cells'][2*i:2*i+2]
     bids=[r['bundle_id'] for r in absolute['members']]+[b['members'][p] for b in comparative['blocks'] for p in ('A1','B1','B2','A2')]
     cell['members']=[{'ordinal':n,'bundle_id':bid,'config_sha256':hashlib.sha256((window.claim/bid/'config.json').read_bytes()).hexdigest()} for n,bid in enumerate(bids,1)]
    s0.put(pack/'extraction_spec.json',spec)
    tree_path=pack/'plan_tree.json';tree=json.loads(tree_path.read_bytes());tree['downstream_contract']['extraction_spec']['sha256']=s0.sha(pack/'extraction_spec.json');s0.put(tree_path,tree)
    for name in ('selection.json','prefill_prompt_pin.json'):s0.put(pack/'prefill_pin'/name,{})
    rebuilt=harvest.build_roster(pack,window.archive/'sources/repo')
    projection,_=harvest.l4_exclusion_inputs(rebuilt,{},plan_id=window.entry.plan_id,attempt=window.entry.attempt)
    projection.pop('bundles',None);projection.pop('chain_started_monotonic_ns',None)
    s0.put(window.archive/'derived/roster.json',projection)
    flags=[json.loads(line) for line in (window.archive/'derived/flags.jsonl').read_bytes().splitlines() if line.strip()]
    exclusions=compute(flags,projection,{},load_catalog(s0.ROOT/'configs/campaigns/v5_claim_25g83/flag_catalog.json'))
    record=json.loads((window.archive/'harvest.json').read_bytes());exclusions['harvest_checkout']=record['harvest_checkout'];s0.put(window.archive/'derived/exclusions.json',exclusions)
    wf_path=window.archive/'derived/window_flags.json';wf=json.loads(wf_path.read_bytes());wf['exclusions']={key:exclusions[key] for key in ('claim_usable','release_blocked','reasons','unclassified')};s0.put(wf_path,wf)
    s2.refresh(window)
    index=json.loads(base.index.read_bytes())
    index['attempts']=[window.entry_data if entry['pack']=='beta' and entry['entry_kind']!='no_archive' else entry for entry in index['attempts']]
    index_path=root/'index.json';s0.put(index_path,index)
    repo=root/'repo';local_pack=repo/'configs/campaigns'/window.entry.pack_id;shutil.copytree(pack,local_pack)
    return SimpleNamespace(root=root,window=window,index=index_path,repo=repo,spec=spec,
        spec_raw=(local_pack/'extraction_spec.json').read_bytes(),
        selection_raw=(local_pack/'prefill_pin/selection.json').read_bytes(),
        prompt_raw=(local_pack/'prefill_pin/prefill_prompt_pin.json').read_bytes(),row=base.row)


@contextmanager
def indexed_reported_seams(fixture):
    """Real issue_pack/project_pack; synthetic summaries, identity and prechecks."""
    from tests.b5_analysis import fixtures_s2 as s2
    from joulewise import paper_reported_energy as energy
    summary=next(iter(synthetic_pack().summaries.values()))
    def session(root,ids,**kwargs):
        context=kwargs['archive_context']
        return SimpleNamespace(ready=True,refusal_reasons=(),summary_for=lambda bid:summary,
            provenance_for=lambda bid:{'operative_fiducial_bound_s':context.window_bracket['b_fiducial_s']})
    real_precheck=issuer.inputs.window_evidence_precheck
    def precheck(evidence,metric):
        return {**real_precheck(evidence,metric),'eligible':'prefill-p42-' not in metric['metric_tag'],
            'reasons':['window_evidence_precheck_missing'] if 'prefill-p42-' in metric['metric_tag'] else []}
    with s2.capture_adapter(),mock.patch.object(energy,'_validate_registered_spec'), \
         mock.patch.object(issuer,'AuthenticatedConsumptionSession',side_effect=session), \
         mock.patch.object(issuer,'whole_window_drift_allowances',return_value=ww.WholeWindowDriftAllowanceResult(
             'allowances',{'gross_energy':{'allowance_j':.1}})), \
         mock.patch.object(issuer.inputs,'realized_scientific_identity',return_value={'model':{'name':'Qwen3-8B-4bit'}}), \
         mock.patch.object(issuer.inputs,'campaign_cooldown_evidence',return_value={}), \
         mock.patch.object(issuer.inputs,'window_evidence_precheck',side_effect=precheck):
        yield


def issue_indexed_reported(fixture,index=None,pack='beta',**kwargs):
    from tests.b5_analysis import fixtures as s0
    from joulewise.b5_analysis.windows import SealPins
    # Explicit S0 synthetic pack bindings; production defaults remain untouched.
    kwargs.pop('repo_root',None)
    return issuer.issue_pack(index or fixture.index,pack,repo_root=fixture.repo,seal_pins=SealPins.load(),
        pack_table=s0.PACK_TABLE,test_only_allow_synthetic_binding=True,strict_validator=lambda *a:())
