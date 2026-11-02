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
    assert all(m['summary']['window_evidence_precheck']['eligible'] is False for m in pilot['members'])
    assert all(m['summary']['thermal_pressure_seconds']['Heavy']>0 for m in pilot['members'])
    assert all(m['summary']['state_changing_calls']==2 for m in pilot['members'])
    assert pilot['status']=='instrument_incomplete'
    assert result['harvest_exit'] in (0,6), (case.session/'staging/harvest.stderr').read_text()
    # Save a durable scratch result before TemporaryDirectory is cleaned.
    target=Path(tempfile.mkdtemp(prefix='synthetic-session-',dir=scratch))
    shutil.copytree(case.session,target,dirs_exist_ok=True)
    print('SYNTHETIC_E2E members=12 chain_ineligible=12 state_changing_calls=2_per_member end_state=end_task harvest_exit='+str(result['harvest_exit']))
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
    # Only scratch is handed to desk. No harvest, model, sampler or server.
    result=session.desk(replay,harvest=False)
    pilot=h.read(replay/'PILOT.json')
    assert len(pilot['members'])==12
    assert all(m['summary']['state_changing_calls']==0 for m in pilot['members'])
    heavy=[]
    for m in pilot['members']:
        if m['ordinal'] in (1,5,9):
            summary=m['summary']
            assert summary['window_evidence_precheck']['eligible'] is False
            assert 'thermal_pressure_elevated_in_window' in summary['window_evidence_precheck']['reasons']
            heavy.append((m['ordinal'],summary['thermal_pressure_seconds']['Heavy']))
    print('PILOT1_REPLAY members=12 state_changing_calls=0_all heavy_seconds='+json.dumps(heavy))
    print('PILOT1_REPLAY end_states='+json.dumps([m['summary']['end_state'] for m in pilot['members']]))
    assert result['harvest_status']=='not_run'
    assert pilot['status']=='instrument_incomplete'


def parent(scratch):
    # Load parent implementations into their normal module names, then execute
    # current acceptance tests. No checkout, Git mutation or second worktree.
    import importlib.util
    import importlib
    modules=('joulewise.align.apple.endpoint','joulewise.align.apple.workload',
             'joulewise.align.apple.pilot','joulewise.align.apple.campaign','joulewise.align.shade.task',
             'scripts.align_pilot_kit','scripts.align_pilot_session')
    for name in modules:
        importlib.import_module(name)
        relative=name.replace('.','/')+'.py'
        raw=subprocess.check_output(['git','-C',str(ROOT),'show','cbfb9b0a5:'+relative])
        path=scratch/('parent-'+name.replace('.','_')+'.py');path.write_bytes(raw)
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module
        setattr(importlib.import_module(name.rsplit('.',1)[0]),name.rsplit('.',1)[1],module)
        # Keep repository-relative file lookup identical to the parent checkout.
        module.__file__=str(ROOT/relative)
        exec(compile(raw,str(ROOT/relative),'exec'),module.__dict__)
    from tests.align import test_pilot2
    from tests import test_align_pilot_session as pilot_tests
    KitTests=pilot_tests.KitTests
    # Overlay only artifact roots: parent has no v1 protocol. Config inputs
    # remain the untouched v0 kit selected by the parent implementation.
    assets=scratch/'parent-assets';assets.mkdir(exist_ok=True)
    if not (assets/'configs').exists():
        (assets/'configs').symlink_to(ROOT/'configs',target_is_directory=True)
    (assets/'docs/align').mkdir(parents=True,exist_ok=True)
    pilot_tests.ROOT=assets
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_pilot2)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(KitTests))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    assert not result.wasSuccessful(),'regressions did not detect parent'
    print(f'PARENT_REGRESSIONS tests={result.testsRun} failures={len(result.failures)} errors={len(result.errors)}')


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('synthetic','pilot1','parent'));p.add_argument('--scratch',type=Path,required=True)
    a=p.parse_args();a.scratch.mkdir(parents=True,exist_ok=True)
    os.environ.update(TMPDIR=str(a.scratch),JW_B5_SYNTHETIC_ONLY='1');tempfile.tempdir=str(a.scratch)
    globals()[a.mode](a.scratch)

if __name__=='__main__':main()
