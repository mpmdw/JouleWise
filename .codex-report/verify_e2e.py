#!/usr/bin/env python3
"""Repeatable offline verification. All generated sessions live under --scratch."""
import argparse
from contextlib import redirect_stdout
from dataclasses import replace
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import align_pilot_kit as kit, align_pilot_session as session, bytes_h_session as h


def synthetic(scratch):
    from tests.test_align_pilot_session import SessionPrepareTests, SyntheticDeskTests, fixture_spec
    from tests.align.test_shade import fixture_source
    kit.generate(scratch/'generated')
    case=SessionPrepareTests('test_prepare_stages_the_align_kit_without_install_or_loop_registration')
    case.setUp()
    # Feed the freshly generated kit into prepare, then substitute only local
    # file inventories with the test's explicit synthetic model payload.
    kit.generate(case.measurement,source_root=ROOT)
    reg=case.measurement/kit.KIT/'registration'
    pins=h.read(reg/'identity_pins.json');inventory=h.read(reg/'model_artifact_inventory.json')
    for name,unit in pins['units'].items():
        unit['model_source']=str(case.root/'models')
        inventory['artifacts'][name]['inventory']=[{'path':'weight','size_bytes':9}]
    h.write(reg/'identity_pins.json',pins);h.write(reg/'model_artifact_inventory.json',inventory)
    state=case.prepared()
    root=case.root
    with fixture_source() as source:
        bundle=SyntheticDeskTests.run_member(case,root/'seed',fixture_spec(source,'sabotage',1),'seed')
    episode=h.read(bundle/'outputs/align_episode.json')
    stamps=episode['hardware']['paired_clock_stamps_ns']
    start,end=[r['epoch_ns']/1e9 for r in stamps]
    # Production requested cadence is 10 Hz: interval=1/10 second. Include
    # one sample on each side, then clip supports in the real desk reader.
    rich=[];raw=[]
    index=0
    while start+index/10 <= end+.1:
        stamp=start+index/10
        pressure='Heavy' if stamp>(start+end)/2 else 'Nominal'
        active=100_000_000
        rich.append({'timestamp_s':stamp,'elapsed_ns':100_000_000,
            'gpu':{'dvfm_states':[{'freq':1380 if pressure=='Nominal' else 690,'used_ns':active}]}})
        raw.append(plistlib.dumps({'timestamp':dt.datetime(2026,11,2),'elapsed_ns':100_000_000,
            'thermal_pressure':pressure,'processor':{'cpu_power':1000,'gpu_power':1000,'ane_power':0,
            'cpu_energy':100,'gpu_energy':100,'ane_energy':0}}))
        index+=1
    (bundle/'rich_telemetry.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rich))
    (bundle/'raw/powermetrics.plist').write_bytes(b'\0'.join(raw))
    metrics=h.read(bundle/'summary_metrics.json')
    metrics['window_evidence_precheck']={'gross_request':{'eligible':False,'reasons':['thermal_pressure_elevated_in_window']}}
    h.write(bundle/'summary_metrics.json',metrics)
    case.seed_collection(state,bundle)
    result=session.desk(case.session)
    pilot=h.read(case.session/'PILOT.json')
    assert len(pilot['members'])==12
    assert all(m['summary']['chain_eligible'] is False for m in pilot['members'])
    assert all(m['summary']['thermal_pressure_seconds']['Heavy']>0 for m in pilot['members'])
    assert all(m['summary']['state_changing_calls']==0 for m in pilot['members'])
    assert pilot['status']=='instrument_incomplete'
    assert result['harvest_exit'] in (0,6), (case.session/'staging/harvest.stderr').read_text()
    # Save a durable scratch result before TemporaryDirectory is cleaned.
    target=Path(tempfile.mkdtemp(prefix='synthetic-session-',dir=scratch))
    shutil.copytree(case.session,target,dirs_exist_ok=True)
    print('SYNTHETIC_E2E members=12 chain_ineligible=12 state_changing_calls=0_per_member end_state=episode.end_task:1 harvest_exit='+str(result['harvest_exit']))
    print('SYNTHETIC_SESSION '+str(target))
    case.doCleanups()


def pilot1(scratch):
    original=Path('/Users/edr/night-align/pilot-v0-20261102T110643Z')
    replay=scratch/'pilot1-replay'
    replay.mkdir(exist_ok=True)
    for name in ('runs-parent','custody'):
        if not (replay/name).exists():
            subprocess.run(['/bin/cp','-cR',str(original/name),str(replay/name)],check=True)
    state=h.read(original/'session.json')
    measurement=replay/'measurement'
    old_kit=Path('configs/campaigns/align_pilot_v0')
    h.write(measurement/old_kit/'collection_plan.json',h.read(Path(state['measurement_root'])/old_kit/'collection_plan.json'))
    state.update(session_root=str(replay),measurement_root=str(measurement),
        registration_dir=str(measurement/old_kit/'registration'),plan_path=str(replay/'custody/night_plan.json'),
        runs_roots={k:str(replay/'runs-parent'/Path(v).name) for k,v in state['runs_roots'].items()})
    plan=h.read(original/'custody/night_plan.json');plan['custody_root']=str(replay/'custody')
    h.write(replay/'custody/night_plan.json',plan)
    h.write(replay/'session.json',state)
    (replay/'staging').mkdir(exist_ok=True)
    h.write(replay/'archive/derived/exclusions.json',h.read(original/'archive/derived/exclusions.json'))
    # Only scratch is handed to desk. No harvest, model, sampler or server.
    result=session.desk(replay,harvest=False)
    pilot=h.read(replay/'PILOT.json')
    assert len(pilot['members'])==12
    assert all(m['summary']['state_changing_calls']==0 for m in pilot['members'])
    heavy=[]
    for m in pilot['members']:
        if m['ordinal'] in (1,5,9):
            summary=m['summary']
            assert summary['chain_eligible'] is False
            assert summary['exclusion_codes']==['thermal.os_level_nonzero']
            heavy.append((m['ordinal'],summary['thermal_pressure_seconds']['Heavy']))
    assert [m['ordinal'] for m in pilot['members'] if m['excluded']]==[1,5,9,12]
    assert sum(m['summary']['chain_eligible'] for m in pilot['members'])==8
    assert all(m['summary']['classification']=='name_rule_v0' for m in pilot['members'])
    assert any(level==1 for _,level in pilot['members'][-1]['summary']['os_thermal']['readings_monotonic_ns_level'])
    replay_hidden_tokens(original)
    print('PILOT1_REPLAY excluded=e01,e05,e09,e12:thermal.os_level_nonzero eligible=8')
    print('PILOT1_REPLAY members=12 state_changing_calls=0_all heavy_seconds='+json.dumps(heavy))
    print('PILOT1_REPLAY end_states='+json.dumps([m['summary']['end_state'] for m in pilot['members']]))
    assert result['harvest_status']=='not_run'
    assert pilot['status']=='instrument_incomplete'


def replay_hidden_tokens(original):
    from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
    from joulewise.align.apple.endpoint import MlxEndpoint
    from joulewise.align.apple.workload import EpisodeRuntimeAdapter, EpisodeSpec
    from joulewise.align.interfaces import ChatMessage
    from joulewise.clock import FakeClock
    from joulewise.schemas import BenchmarkConfig
    from transformers import AutoTokenizer
    from types import SimpleNamespace
    runs=original/'runs-parent/runs_align_pilot_v0'
    bundle=runs/'align-pilot-v0-episodes-a-e01'
    config=BenchmarkConfig.from_mapping(h.read(bundle/'config.json'))
    tokenizer=AutoTokenizer.from_pretrained(config.model.source,local_files_only=True)
    cases=[('a',1,6,658),('a',2,0,1535),('a',3,1,1535),('b',12,1,1535),('a',1,0,864)]
    results=[]
    for stage,member,turn,want in cases:
        rows=[json.loads(line) for line in (runs/f'align-pilot-v0-episodes-{stage}-e{member:02}'/'outputs/align_turns.jsonl').read_text().splitlines()]
        generation=rows[turn]['generation']; ids=generation['output_token_ids']
        clock=FakeClock(); runtime=MlxRuntimeAdapter(clock)
        runtime._model=object();runtime._tokenizer=tokenizer
        def stream_generate(*args,**kwargs):
            for index,token in enumerate(ids):
                clock.sleep(.010)  # D-019 synthetic decode time, no native compute.
                text=tokenizer.decode([token],skip_special_tokens=False)
                if token == tokenizer.eos_token_id: text=''
                yield SimpleNamespace(token=token,text=text,finish_reason=generation.get('finish_reason') if index==len(ids)-1 else None)
        runtime._mlx_lm=SimpleNamespace(stream_generate=stream_generate,make_sampler=lambda temp:object())
        endpoint=MlxEndpoint(runtime,config,clock,episode_domain='replay')
        result=endpoint.chat([ChatMessage('user','offline replay')],max_tokens=1536,temperature=0.,seed=1)
        assert result.reasoning_tokens==want,(member,turn,result.reasoning_tokens,want)
        results.append(f'e{member:02} t{turn}={result.reasoning_tokens}')
    print('PILOT1_HIDDEN '+', '.join(results))
    # The projection bytes and legacy prompt text must also be unchanged.
    spec=EpisodeSpec.from_text(config.workload_profile.prompt_text)
    assert spec.to_text()==config.workload_profile.prompt_text
    from joulewise.adapters.mock_runtime import MockRuntimeAdapter
    adapter=EpisodeRuntimeAdapter(MockRuntimeAdapter(FakeClock()),FakeClock())
    projection=adapter.identity_projection_metadata(config)
    digest=hashlib.sha256(json.dumps(projection,sort_keys=True,default=str).encode()).hexdigest()
    assert digest.startswith('e5da7d088ab0d3db'),digest
    print('PILOT1_IDENTITY projection_sha256='+digest+' prompt_text_roundtrip=true')


def parent(scratch):
    # Current regressions over the exact requested baseline implementations.
    import importlib.util
    import importlib
    modules=('joulewise.align.records','joulewise.align.shade.task','joulewise.align.runner',
             'joulewise.align.apple.endpoint','joulewise.align.apple.workload',
             'joulewise.align.apple.diagnostics','scripts.align_pilot_kit','scripts.align_pilot_session')
    for name in modules:
        importlib.import_module(name)
        relative=name.replace('.','/')+'.py'
        raw=subprocess.check_output(['git','-C',str(ROOT),'show','aac67a575:'+relative])
        path=scratch/('parent-'+name.replace('.','_')+'.py');path.write_bytes(raw)
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module
        setattr(importlib.import_module(name.rsplit('.',1)[0]),name.rsplit('.',1)[1],module)
        module.__file__=str(ROOT/relative)
        exec(compile(raw,str(ROOT/relative),'exec'),module.__dict__)
    assets=scratch/'parent-assets';assets.mkdir(exist_ok=True)
    archive=subprocess.check_output(['git','-C',str(ROOT),'archive','aac67a575','configs/campaigns/align_pilot_v1'])
    import tarfile
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        bundle.extractall(assets,filter='data')
    from tests.align import test_pilot2_round1
    test_pilot2_round1.ROOT=assets
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_pilot2_round1)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    assert not result.wasSuccessful(),'regressions did not detect baseline'
    print(f'PARENT_REGRESSIONS base=aac67a575 tests={result.testsRun} failures={len(result.failures)} errors={len(result.errors)}')


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('synthetic','pilot1','parent'));p.add_argument('--scratch',type=Path,required=True)
    a=p.parse_args();a.scratch.mkdir(parents=True,exist_ok=True)
    os.environ.update(TMPDIR=str(a.scratch),JW_B5_SYNTHETIC_ONLY='1');tempfile.tempdir=str(a.scratch)
    globals()[a.mode](a.scratch)

if __name__=='__main__':main()
