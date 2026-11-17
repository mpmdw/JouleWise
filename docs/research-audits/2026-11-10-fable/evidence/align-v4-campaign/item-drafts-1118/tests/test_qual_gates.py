"""Exact embedded item gates in bash and zsh, using pinned mock predecessors.

All test roots, synthetic Git commits and altered mock receipts stay inside the
caller-created .synthetic directory in this folder. No production path is read.
"""
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zoneinfo import ZoneInfo
HERE=Path(__file__).resolve().parents[1]; META=json.loads((HERE/'items.json').read_text()); BASE=Path(sys.argv[1]).resolve(); TZ=ZoneInfo('America/Los_Angeles')
checks=failures=0

def quote(s): return "'"+str(s).replace("'","'\"'\"'")+"'"
def dump(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj))
def git(repo,*args,**kw): return subprocess.check_output(['git','-C',str(repo),*args],stderr=subprocess.DEVNULL,**kw).decode().strip()
def epoch(day): return int(dt.datetime.fromisoformat(day+'T12:00:00').replace(tzinfo=TZ).timestamp())

def run_item(item,shell):
    global checks,failures
    text=(HERE/f"ITEM-{item['item']}.md").read_text(); blocks=re.findall(r'```sh\n(.*?)```',text,re.S)
    config=re.search(r'SPAN=.*?\nQUAL_DATES=.*?\n',blocks[0],re.S).group()
    gates=blocks[0].split('# BEGIN TESTABLE GATES\n')[1].split('# END TESTABLE GATES')[0]
    assert sum(b.count('all_gates || exit 1') for b in blocks)==2
    assert '--batch-window' not in blocks[1] and 'launch_cadence_span.py launch' in blocks[1]
    src=(HERE/'gates.sh').read_text().split('# BEGIN TESTABLE GATES\n')[1].split('# END TESTABLE GATES')[0]
    assert gates==src  # Test exactly the final emitted functions.
    home=BASE/(item['item']+'-'+shell); home.mkdir(); root=home/'mock-root'; wt=home/'worktree-root'; markers=home/'markers'; auth=home/'auth'; auth.mkdir()
    git(auth,'init','-q'); (auth/'coefficients.json').write_text('{"SYNTHETIC":true,"coefficients":[1,2,3]}\n')
    coefsha=hashlib.sha256((auth/'coefficients.json').read_bytes()).hexdigest()
    for i in META['items']:
        p=auth/i['queue_path']; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes((HERE/i['queue_file']).read_bytes())
    git(auth,'add','.')
    env=dict(os.environ,GIT_AUTHOR_NAME='Synthetic fixture',GIT_AUTHOR_EMAIL='fixture@invalid',GIT_COMMITTER_NAME='Synthetic fixture',GIT_COMMITTER_EMAIL='fixture@invalid',GIT_AUTHOR_DATE='2026-11-16T12:00:00-08:00',GIT_COMMITTER_DATE='2026-11-16T12:00:00-08:00')
    git(auth,'commit','-q','-m','Synthetic coefficients and queues, never published',env=env)
    commit=git(auth,'rev-parse','HEAD')
    git(auth,'update-ref','refs/remotes/origin/audit/2026-11-10-fable',commit); git(auth,'update-ref','refs/remotes/origin/main',commit)
    empty=git(auth,'mktree',input=b''); orphan=git(auth,'commit-tree',empty,'-m','Synthetic unrelated history',env=env)
    now=epoch(item['date']); predout=root/item['predecessor_camp']/f"cq-{item['predecessor']}-a1-20261119T090000Z"
    latest=wt/'partc'/'.desk'/'f0-synthetic-20261119T100000Z'
    debt=home/'synthetic-debt.json'
    gates=gates.replace('/Users/edr/campaign-out',str(root)).replace('/Users/edr/code/jw-wt',str(wt)).replace('/Users/Shared/JouleWise/desk-copy',str(markers))
    defaults=dict(AUTH_REPO=str(auth),PIN=META['pin'],KIT_SHA=item['kit_sha'],QUEUE_PATH=item['queue_path'],QUEUE_SHA=item['queue_sha'],
        NONCAMPAIGN_COPY_OK='yes',NONCAMPAIGN_COPY_CLOSE_EPOCH=now-1200,NONCAMPAIGN_COPY_RECEIPT=str(latest/'runner_receipt.json'),NONCAMPAIGN_COPY_RECORD='synthetic latest Check/copy proof',PRIOR_CLOSE_EPOCH=now-4000,OTHER_CLOSE_EPOCH=0,HOST_RESTORE_OK=1,GROUPS_ABSENT=1,LAST_CLOSE_KIND='other',
        QUAL_COLD_SEAT='ADMIT',LINE2_EQUAL='yes',LINE2_PIN=META['pin'],LINE2_BASE=META['merged_w1'],COLD_SEAT_KIT_SHA=item['kit_sha'],FIRST_CAPTURE_CONFIRMED='yes',
        HOST_EVENT_DISPOSITION='done',CURRENT_HOST_STATE_ID='synthetic-host',FREEZE2_HOST_STATE_ID='synthetic-host',HOST_EVENT_BEFORE_FREEZE2='yes',QUAL_INCLUSION_UNCHANGED='yes',
        SESSION_READY='no',SESSION_RECORD='synthetic fresh READY census',STOPS_CLEAR='yes',VETO_CLEAR='yes',CHECKLIST_OK='yes',PILOT_PASSED='yes',SAMPLE_HAND_CLEAR='yes',COPY_KEY_SAFE='yes',OFFLOAD_CLEAR='yes',
        LINE6_RECORD='synthetic stops clear',CHECKLIST_RECORD='synthetic native checklist',VETO_RECORD='synthetic veto census',SAMPLE_HAND_RECORD='synthetic sampled hand pass',
        QUAL01_SOAK_HAND_READ='SAME',QUAL01_SOAK_RECORD='synthetic RL172a soak comparison',LINE9_RECORD=str(debt))
    fills=dict(ISSUED_EPOCH=now-100,WATCH_UNTIL_EPOCH=now+10000,FREEZE2_COMMIT=commit,FREEZE2_COEF_SHA256=coefsha,FREEZE2_COEF_PATH='coefficients.json',COLD_SEAT_RECORD='synthetic cold seat pointer',LINE2_RECORD='synthetic test-for-test red comparison',HOST_EVENT_RECORD='synthetic pre-freeze event/readback',HOST_STATE_ID='synthetic-host',INCLUSION_RECORD='synthetic research-lead unchanged inclusion ruling',QUEUE_COMMIT=commit)
    def fixture():
        for d in (root,wt,markers): shutil.rmtree(d,ignore_errors=True); d.mkdir()
        source=BASE/'mock'/item['predecessor']; shutil.copytree(source,predout)
        p=predout/'runner_receipt.json'; r=json.loads(p.read_text()); r['mock']=False; r['synthetic_fixture']=True; r['ended']={'epoch_s':now-4000}; dump(p,r); os.utime(p,(now-4000,now-4000))
        dump(latest/'runner_receipt.json',{'synthetic_fixture':True,'ended':{'epoch_s':now-1200}}); os.utime(latest/'runner_receipt.json',(now-1200,now-1200))
        (markers/'f0-synthetic.ok').write_text('SYNTHETIC verified hashes, size, provider upload completion\n')
        # Minimal but typed k+2 proof: prior two entries only stand for the full census in this test.
        dump(debt,{'next_span':item['span'],'authenticated_roster_identity_checks':'RL-172 (c)','machine_order':[
            {'span_id':'dev-05-s01' if item['span']=='qual-01-s01' else 'dev-05-s02' if item['span']=='qual-01-s02' else 'synthetic-k-minus-2','runner_kind':'cadence-legs-v1.1','desk_final_record':'synthetic authenticated FINAL','q1_complete_record':'synthetic typed Q1 completion'},
            {'span_id':item['predecessor'],'runner_kind':'cadence-legs-v1.1'}]})
    def close_stamp(path, epoch):
        r=json.loads(path.read_text()); r['ended']={'epoch_s':epoch}; dump(path,r)
    def mutate(**kw):
        p=predout/'runner_receipt.json'; r=json.loads(p.read_text()); r.update(kw); dump(p,r); os.utime(p,(now-4000,now-4000))
    def summary(leg,**kw):
        p=predout/'desk-bundle'/'legs'/leg/'leg_summary.json'; r=json.loads(p.read_text()); r.update(kw); dump(p,r)
    def debt_change(key,value):
        r=json.loads(debt.read_text()); r['machine_order'][0][key]=value; dump(debt,r)
    def run(name,setup=lambda:None,overrides=None,fill_changes=None,want=True,command='all_gates',stamp=None,contains=None):
        global checks,failures
        fixture(); setup(); vals={**defaults,**(overrides or {})}; ff={**fills,**(fill_changes or {})}; program=gates
        for key,value in ff.items():
            pattern=rf'^{key}="[^"]*"$'
            assert re.search(pattern,program,re.M),key
            if value is not None: program=re.sub(pattern,key+'='+quote(value),program,flags=re.M)
        assignments='\n'.join('unset '+key if value is None else key+'='+quote(value) for key,value in vals.items())
        script=f'PY={quote(sys.executable)}\n'+config+program+f'\ndate() {{ echo {now if stamp is None else stamp}; }}\n'+assignments+'\n'+command+'\n'
        result=subprocess.run([shell],input=script,text=True,capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(home)))
        out=result.stdout+result.stderr; passed=(result.returncode==0)==want and (contains is None or contains in out)
        checks+=1; failures+=not passed
        print(('PASS' if passed else 'FAIL'),item['span'],shell,name,'| rc',result.returncode,'|',out.strip().replace('\n',' / ')[-500:])
    run('clean full arm path')
    run('freeze2 unfilled WAIT',fill_changes={'FREEZE2_COMMIT':None},want=False,contains='HOLD_FOR_FIT_FREEZE')
    run('coefficient sha unfilled WAIT',fill_changes={'FREEZE2_COEF_SHA256':None},want=False,contains='HOLD_FOR_FIT_FREEZE')
    run('freeze2 wrong sha STOP',fill_changes={'FREEZE2_COEF_SHA256':'0'*64},want=False,contains='sha256 mismatch')
    run('freeze2 missing path STOP',fill_changes={'FREEZE2_COEF_PATH':'missing.json'},want=False,contains='unreadable')
    run('freeze2 nonancestor STOP',fill_changes={'FREEZE2_COMMIT':orphan},want=False,contains='not ancestor')
    run('freeze2 path escapes STOP',fill_changes={'FREEZE2_COEF_PATH':'../coefficients.json'},want=False,contains='path not permitted')
    for key in ('COLD_SEAT_RECORD','LINE2_RECORD'):
        run(key+' unfilled WAIT',fill_changes={key:None},want=False,contains='WAIT')
    for key,value in [('COLD_SEAT_KIT_SHA','0'*64),('QUAL_COLD_SEAT','UNKNOWN'),('LINE2_EQUAL','no'),('LINE2_PIN','bad'),('LINE2_BASE','bad'),('FIRST_CAPTURE_CONFIRMED','no')]:
        run('admission mismatch '+key,overrides={key:value},want=False,contains='STOP')
    run('host event unfilled WAIT',fill_changes={'HOST_EVENT_RECORD':None},want=False,contains='WAIT')
    run('host state unfilled WAIT',fill_changes={'HOST_STATE_ID':None},want=False,contains='WAIT')
    for key,value in [('CURRENT_HOST_STATE_ID','changed'),('FREEZE2_HOST_STATE_ID','changed')]:
        run('host mismatch '+key,overrides={key:value},want=False,contains='WAIT')
    for state in ('waived','deferred'): run('explicit host event '+state,overrides={'HOST_EVENT_DISPOSITION':state})
    assert 'INCLUSION_RECORD="RL-174 B.5 at ebff15ad27e831499dd65796b3727d8c5d451e21' in src
    run('maintenance record erased WAIT',fill_changes={'INCLUSION_RECORD':''},want=False,contains='WAIT')
    run('unplanned restart has no before-freeze gate',overrides={'HOST_EVENT_BEFORE_FREEZE2':'no'})
    run('maintenance inclusion changed WAIT',overrides={'QUAL_INCLUSION_UNCHANGED':'no'},want=False,contains='WAIT')
    run('READY v4 DO NOT ARM',overrides={'SESSION_READY':'yes'},want=False,contains='DO NOT ARM')
    run('unknown v4 STOP',overrides={'SESSION_READY':None},want=False,contains='STOP')
    run('v4 record unfilled WAIT',overrides={'SESSION_RECORD':''},want=False,contains='WAIT')
    for key in ('STOPS_CLEAR','VETO_CLEAR','CHECKLIST_OK','PILOT_PASSED','SAMPLE_HAND_CLEAR','COPY_KEY_SAFE','OFFLOAD_CLEAR'):
        run('native/admission '+key,overrides={key:'no'},want=False,contains='WAIT')
    run('soak handread absent',overrides={'QUAL01_SOAK_HAND_READ':'pending'},want=item['span']=='qual-01-s01',contains=None if item['span']=='qual-01-s01' else 'WAIT')
    run('queue commit unfilled WAIT',fill_changes={'QUEUE_COMMIT':None},want=False,contains='WAIT')
    run('queue wrong hash STOP',overrides={'QUEUE_SHA':'0'*64},want=False,contains='STOP')
    run('queue expired STOP',stamp=1795420800,command='queue_gate',want=False,contains='STOP')
    run('Q1 debt unpaid WAIT',setup=lambda:debt_change('q1_complete_record',''),want=False,contains='WAIT')
    run('desk debt unpaid WAIT',setup=lambda:debt_change('desk_final_record',''),want=False,contains='WAIT')
    run('Q1 debt unfilled WAIT',setup=lambda:debt_change('q1_complete_record','<LEAD FILLS: Q1>'),want=False,contains='WAIT')
    if item['span'].startswith('qual-01-'):
        run('named dev-05 debt omitted WAIT',setup=lambda:debt_change('span_id','unrelated-paid-span'),command='debt_gate',want=False,contains='WAIT')
    run('no predecessor WAIT',setup=lambda:shutil.rmtree(predout),want=False,contains='WAIT')
    run('pending predecessor WAIT',setup=lambda:(predout/'runner_receipt.json').unlink(),want=False,contains='WAIT')
    run('lookalike predecessor WAIT',setup=lambda:predout.rename(predout.with_name(predout.name.replace('-a1-','b-a1-'))),want=False,contains='WAIT')
    run('multiple attempts STOP',setup=lambda:shutil.copytree(predout,predout.with_name(predout.name.replace('-a1-','-a2-'))),want=False,contains='multiple')
    for key,value in [('rc',1),('mock',True),('error','refusal'),('legs_finished',5),('roster',[]),('runner_kind','cadence-legs-v1'),('kit',{}),('steps',[]),('feeds',{}),('meter',{}),('ended',{'epoch_s':float('nan')}),('span_result',{'fault':True})]:
        run('unclean predecessor '+key,setup=lambda k=key,v=value:mutate(**{k:v}),want=False,contains='VOID')
    run('two overtime STOP',setup=lambda:[summary(leg,wall_s=99999) for leg in item['predecessor_legs'][:2]],want=False,contains='LEG_OVERTIME')
    run('one overtime allowed',setup=lambda:summary(item['predecessor_legs'][0],wall_s=99999))
    run('three contaminated STOP',setup=lambda:summary(item['predecessor_legs'][0],contaminated_redos=3),want=False,contains='CONTAMINATED_REDOS')
    run('prior before predecessor STOP',overrides={'PRIOR_CLOSE_EPOCH':1},want=False,contains='STOP')
    run('issue unfilled WAIT',fill_changes={'ISSUED_EPOCH':None},want=False,contains='WAIT')
    run('issue future VOID',fill_changes={'ISSUED_EPOCH':now+1},want=False,contains='VOID')
    run('24h expired VOID',fill_changes={'ISSUED_EPOCH':now-86400},want=False,contains='VOID')
    run('24h minus second valid',fill_changes={'ISSUED_EPOCH':now-86399})
    run('watch unfilled WAIT',fill_changes={'WATCH_UNTIL_EPOCH':None},want=False,contains='WAIT')
    run('watch stale STOP',fill_changes={'WATCH_UNTIL_EPOCH':now},want=False,contains='STOP')
    run('watch future STOP',fill_changes={'WATCH_UNTIL_EPOCH':now+86401},want=False,contains='STOP')
    run('noncampaign copy missing WAIT',overrides={'NONCAMPAIGN_COPY_OK':'no'},want=False,contains='WAIT')
    run('stale noncampaign close copy proof WAIT',overrides={'NONCAMPAIGN_COPY_CLOSE_EPOCH':now-5000},want=False,contains='WAIT')
    run('other noncampaign receipt copy proof WAIT',overrides={'NONCAMPAIGN_COPY_RECEIPT':'old-F0-receipt'},want=False,contains='WAIT')
    run('missing receipt root STOP',setup=lambda:shutil.rmtree(wt),want=False,contains='missing receipt root')
    run('restore unproven STOP',overrides={'HOST_RESTORE_OK':0},want=False,contains='STOP')
    run('process group unproven STOP',overrides={'GROUPS_ABSENT':0},want=False,contains='STOP')
    run('F0/F2 gap 1199 WAIT',setup=lambda:close_stamp(latest/'runner_receipt.json',now-1199),overrides={'NONCAMPAIGN_COPY_CLOSE_EPOCH':now-1199},want=False,contains='interval 1200')
    run('fractional close rounded up',setup=lambda:close_stamp(latest/'runner_receipt.json',now-1199.9),overrides={'NONCAMPAIGN_COPY_CLOSE_EPOCH':now-1199},want=False,contains='interval 1200')
    def campaign_close(age):
        dest=root/'cl-hp-01'/'cq-hp-01-s03-a1-20261119T110000Z'; dest.parent.mkdir(parents=True); latest.rename(dest); close_stamp(dest/'runner_receipt.json',now-age)
        (markers/'cq-hp-01-s03-a1.ok').write_text('SYNTHETIC verified offload')
    def campaign_no_copy():
        campaign_close(300); (markers/'cq-hp-01-s03-a1.ok').unlink()
    def air_copy():
        campaign_close(300); (markers/'cq-hp-01-s03-a1.ok').rename(markers/'cq-hp-01-s03-a1.air.ok')
    run('campaign marker missing WAIT',setup=campaign_no_copy,overrides={'LAST_CLOSE_KIND':'campaign'},want=False,contains='WAIT')
    run('Air campaign marker accepted',setup=air_copy,overrides={'LAST_CLOSE_KIND':'campaign'})
    run('campaign exact 300 allowed',setup=lambda:campaign_close(300),overrides={'LAST_CLOSE_KIND':'campaign'})
    run('campaign 299 WAIT',setup=lambda:campaign_close(299),overrides={'LAST_CLOSE_KIND':'campaign'},want=False,contains='interval 300')
    def date_receipt(camp,date,n):
        out=root/camp/'cq-synthetic-date-a1-20261119T000000Z'
        dump(out/'runner_receipt.json',{'synthetic_fixture':True,'started':{'epoch_s':epoch(date)},'roster':[f'L{i:03d}' for i in range(1,n+1)]})
    run('development receipt on qual date REFUSE',setup=lambda:date_receipt('cl-dev-99',item['date'],1),command='day_gate',want=False,contains='development receipt')
    # Use current block for cap fixtures: not already a second/third block by metadata.
    run('25th leg on date REFUSE',setup=lambda:date_receipt(item['camp'],item['date'],19-(6 if item['predecessor_camp']==item['camp'] else 0)),command='day_gate',want=False,contains='25th leg')
    run('exact 24 leg cap; RL-174 printed',setup=lambda:date_receipt(item['camp'],item['date'],18-(6 if item['predecessor_camp']==item['camp'] else 0)),command='day_gate',contains='cap applies')
    other=next(k for k in META['dates'] if k!=item['block'] and 'cl-'+k!=item['predecessor_camp'])
    shared_dates=','.join(k+'='+(item['date'] if k==other else v) for k,v in META['dates'].items())
    run('shared-date slip plan REFUSE',overrides={'QUAL_DATES':shared_dates},command='day_gate',want=False,contains='three distinct dates')
    run('second unplanned block within 10h REFUSE',setup=lambda:date_receipt('cl-qual-extra',item['date'],1),command='day_gate',want=False,contains='10 h')
    def spaced_block():
        date_receipt('cl-qual-extra',item['date'],1)
        p=root/'cl-qual-extra'/'cq-synthetic-date-a1-20261119T000000Z'/'runner_receipt.json'
        r=json.loads(p.read_text()); r['started']['epoch_s']=now-36000; dump(p,r)
    run('10h cap is no slip remedy',setup=spaced_block,command='day_gate',want=False,contains='one qualification block')
    one=','.join(k+'='+item['date'] for k in META['dates'])
    run('all qual blocks same date REFUSE',overrides={'QUAL_DATES':one},command='day_gate',want=False,contains='three distinct dates')
    newdates=','.join(k+'='+('2026-11-18' if k==item['block'] else v) for k,v in META['dates'].items())
    run('known development date REFUSE',overrides={'T0_DATE':'2026-11-18','QUAL_DATES':newdates},stamp=epoch('2026-11-18'),command='day_gate',want=False,contains='development date')
    for t in (int(epoch(item['date'])-43200),int(epoch(item['date'])+43199)):
        run('date endpoint admitted',stamp=t,command='window_gate')
    run('one second before date REFUSE',stamp=epoch(item['date'])-43201,command='window_gate',want=False,contains='REFUSE')
    run('one second after date REFUSE',stamp=epoch(item['date'])+43200,command='window_gate',want=False,contains='REFUSE')

for shell in ('bash','zsh'):
    assert shutil.which(shell),shell
    for item in META['items']: run_item(item,shell)
print(checks,'synthetic gate checks;',failures,'failures; exact item functions under bash and zsh')
sys.exit(bool(failures))
