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
    staged=home/'staged'; staged.mkdir()
    gates=gates.replace('/Users/edr/campaign-out',str(root)).replace('/Users/edr/code/jw-wt',str(wt)).replace('/Users/Shared/JouleWise/desk-copy',str(markers))
    defaults=dict(AUTH_REPO=str(auth),PIN=META['pin'],KIT_SHA=item['kit_sha'],QUEUE_PATH=item['queue_path'],QUEUE_SHA=item['queue_sha'],
        NONCAMPAIGN_COPY_OK='yes',NONCAMPAIGN_COPY_CLOSE_EPOCH=now-1200,NONCAMPAIGN_COPY_RECEIPT=str(latest/'runner_receipt.json'),NONCAMPAIGN_COPY_RECORD='synthetic latest Check/copy proof',PRIOR_CLOSE_EPOCH=now-4000,OTHER_CLOSE_EPOCH=0,HOST_RESTORE_OK=1,GROUPS_ABSENT=1,LAST_CLOSE_KIND='other',
        FEEDS_STOPPED=1,FOREIGN_PROCESSES_ABSENT=1,CLOSE_PROOF_RECEIPT=str(latest/'runner_receipt.json'),
        QUEUE_COMMIT_EPOCH=now-300,PRED_CLOSE_EPOCH=now-4000,EFF_EPOCH=now-1200,ARM_NOT_BEFORE_EPOCH=now-1200,
        QUAL_COLD_SEAT='ADMIT',LINE2_EQUAL='yes',LINE2_PIN=META['pin'],LINE2_BASE=META['merged_w1'],COLD_SEAT_KIT_SHA=item['kit_sha'],FIRST_CAPTURE_CONFIRMED='yes',
        HOST_EVENT_DISPOSITION='done',CURRENT_HOST_STATE_ID='synthetic-host',FREEZE2_HOST_STATE_ID='synthetic-host',HOST_EVENT_BEFORE_FREEZE2='yes',QUAL_INCLUSION_UNCHANGED='yes',
        S02_ISSUED_EPOCH='unissued',SESSION_READY='no',SESSION_RECORD='synthetic fresh READY census',STOPS_CLEAR='yes',VETO_CLEAR='yes',CHECKLIST_OK='yes',PILOT_PASSED='yes',SAMPLE_HAND_CLEAR='yes',COPY_KEY_SAFE='yes',OFFLOAD_CLEAR='yes',
        LINE6_RECORD='synthetic stops clear',CHECKLIST_RECORD='synthetic native checklist',VETO_RECORD='synthetic veto census',SAMPLE_HAND_RECORD='synthetic sampled hand pass',
        QUAL01_SOAK_HAND_READ='SAME',QUAL01_SOAK_RECORD='synthetic RL172a soak comparison',LINE9_RECORD=str(debt))
    fills=dict(ISSUED_EPOCH=now-100,WATCH_UNTIL_EPOCH=now+10000,FREEZE2_COMMIT=commit,FREEZE2_COEF_SHA256=coefsha,FREEZE2_COEF_PATH='coefficients.json',COLD_SEAT_RECORD='synthetic cold seat pointer',LINE2_RECORD='synthetic test-for-test red comparison',HOST_EVENT_RECORD='synthetic pre-freeze event/readback',HOST_STATE_ID='synthetic-host',INCLUSION_RECORD='synthetic research-lead unchanged inclusion ruling',QUEUE_COMMIT=commit)
    def fixture():
        for d in (root,wt,markers): shutil.rmtree(d,ignore_errors=True); d.mkdir()
        source=BASE/'mock'/item['predecessor']
        relative=['runner_receipt.json',*(f'desk-bundle/legs/{leg}/leg_summary.json' for leg in item['predecessor_legs'])]
        for name in relative:
            target=predout/name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source/name,target)
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
    def run(name,setup=lambda:None,overrides=None,fill_changes=None,want=True,command='all_gates',stamp=None,contains=None,full_start=False,run_boot=None,run_anchor=None):
        global checks,failures
        fixture(); setup(); vals={**defaults,**(overrides or {})}; ff={**fills,**(fill_changes or {})}; program=gates
        for key,value in ff.items():
            pattern=rf'^{key}="[^"]*"$'
            assert re.search(pattern,program,re.M),key
            if value is not None: program=re.sub(pattern,key+'='+quote(value),program,flags=re.M)
        assignments='\n'.join('unset '+key if value is None else key+'='+quote(value) for key,value in vals.items())
        default_boot=quote(f'{{ sec = {now-21600}, usec = 0 }}')
        clock=f'''date() {{ echo {now if stamp is None else stamp}; }}
synthetic_t0_clock_anchor() {{ printf '%s000000000:1000000000000:1000000000000\n' "${{SYNTHETIC_ANCHOR_EPOCH:-{now if stamp is None else stamp}}}"; }}
t0_clock_anchor() {{ synthetic_t0_clock_anchor; }}
BATCH_DEFAULT_BOOT={default_boot}
sysctl() {{
  test "$*" = '-n kern.boottime' && test "${{BATCH_SYSCTL_RC:-0}}" = 0 || return 1
  printf '%s\n' "${{BATCH_SYSCTL:-$BATCH_DEFAULT_BOOT}}"
}}
'''
        if full_start:
            start=blocks[0].replace(blocks[0].split('# BEGIN TESTABLE GATES\n')[1].split('# END TESTABLE GATES')[0], program)
            # Redirect every native path and stub every native command. The two
            # authenticated Git gates still use the real, disposable Git repo.
            paths={
                '/Users/edr/code/jw-wt/cadence-'+item['span']: str(staged),
                '/Users/edr/code/JouleWise': str(auth),
                '/Users/edr/campaign-out/kits/'+item['camp']+'.v1.1-'+META['pin'][:9]+'.json': str(HERE/item['kit_file']),
                '/Users/edr/campaign-out/queues/'+item['camp']+'.queue.json': str(HERE/item['queue_file']),
                '/Users/edr/campaign-out': str(root),
                '/Users/edr/night-custody/magistrate': str(home/'synthetic-fence'),
                '/Users/Shared/JouleWise': str(home/'synthetic-host'),
            }
            for old,new in paths.items(): start=start.replace(old,new)
            overrides_sh=f'''synthetic_python() {{
  case "$*" in
    "-B scripts/launch_align_r0.py preflight "*) echo MOCK_NATIVE_PREFLIGHT;;
    "-B scripts/cadence_queue.py validate-kit "*) echo MOCK_VALIDATE_KIT;;
    "-B scripts/cadence_queue.py checklist "*) echo MOCK_NATIVE_CHECKLIST; test "$NATIVE_RC" = 0;;
    "-B scripts/cadence_legs_runner.py plan "*) echo MOCK_PLAN;;
    "-B scripts/launch_cadence_span.py launch "*) echo MOCK_LAUNCH "$@";;
    "-I -B "*"/scripts/cadence_legs_runner.py t0-anchor") synthetic_t0_clock_anchor;;
    *) {quote(sys.executable)} "$@";;
  esac
}}
git() {{
  case "$*" in
    "rev-parse HEAD") echo {META['pin']};;
    "symbolic-ref -q HEAD") return 1;;
    "status --porcelain"|"-C "*fetch*) :;;
    *) echo "unexpected Git command" >&2; return 2;;
  esac
}}
sudo() {{ echo 'network time: Off'; }}
pmset() {{ echo 'powermode 0'; }}
lsof() {{ return 1; }}
pgrep() {{ return 1; }}
launchctl() {{ :; }}
zsh() {{ :; }}
PY=synthetic_python
MAGISTRATE_PID=100
CHECKLIST_OBSERVATIONS=synthetic
unset MAGISTRATE_WATCHDOG_CUSTODY_ROOT
'''
            script=assignments+'\n'+clock+overrides_sh+start
            if run_boot is not None:
                script+='\nBATCH_SYSCTL='+quote(run_boot)+'\n'
                if run_anchor is not None:
                    script+='SYNTHETIC_ANCHOR_EPOCH='+quote(run_anchor)+'\n'
                script+=blocks[1]
        else:
            script=f'PY={quote(sys.executable)}\n'+config+program+clock+assignments+'\n'+command+'\n'
        result=subprocess.run([shell],input=script,text=True,capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(home)))
        out=result.stdout+result.stderr; passed=(result.returncode==0)==want and (contains is None or contains in out)
        checks+=1; failures+=not passed
        print(('PASS' if passed else 'FAIL'),item['span'],shell,name,'| rc',result.returncode,'|',out.strip().replace('\n',' / ')[-500:])
    run('clean full arm path')
    run('WS 2 full Start with checklist initially unset', overrides={'CHECKLIST_OK':None,'NATIVE_RC':0},
        full_start=True, contains='MOCK_PLAN')
    run('WS 2 native checklist failure clears prefilled yes', overrides={'CHECKLIST_OK':'yes','NATIVE_RC':1},
        full_start=True, want=False, contains='MOCK_NATIVE_CHECKLIST')
    def boot_at(batch):
        return f'{{ sec = {batch-43248}, usec = 0 }} Mon synthetic'
    run('C.4 Start refuses predicted overlap', overrides={'NATIVE_RC':0,'BATCH_SYSCTL':boot_at(now+3600)},
        full_start=True, want=False, contains='RL-175 C.4 predicted OS batch')
    run('C.4 Run refreshes boot after a clear Start',overrides={'NATIVE_RC':0,'BATCH_SYSCTL':boot_at(now+21648-86400)},full_start=True,
        run_boot=boot_at(now+3600),want=False,contains='RL-175 C.4 predicted OS batch')
    expected=item['expected_s']
    run('C.4 Run sends tightened cutoff to child',overrides={'NATIVE_RC':0},full_start=True,
        run_boot=boot_at(now+expected+1),contains=f'--t0-before {now+1}')
    cutoff=min(now+10000,int(re.search(r'WINDOW_END=(\d+)',config)[1])+1)
    run('C.4 Run forwards 27-minute release and clock anchor',overrides={'NATIVE_RC':0},full_start=True,
        run_boot=boot_at(now-1620),
        contains=f'--t0-not-before {now} --t0-before {cutoff} --t0-anchor {now}000000000:1000000000000:1000000000000')
    run('Watch expiry one second away bounds the Run handoff',overrides={'NATIVE_RC':0},full_start=True,
        run_boot=boot_at(now+expected+60),fill_changes={'WATCH_UNTIL_EPOCH':now+1},
        contains=f'--t0-before {now+1} --t0-anchor')
    run('Watch cutoff is exclusive even after watch_gate has passed',
        stamp=now+1,fill_changes={'WATCH_UNTIL_EPOCH':now+1},
        command=f'EXPIRES_EPOCH={now+86400}; QUEUE_EXPIRES_EPOCH={now+86400}; arm_bound_gate',
        want=False,contains=f'effective t0 cutoff {now+1}')
    proven_now={'NATIVE_RC':0,'NONCAMPAIGN_COPY_CLOSE_EPOCH':now}
    issue_now={'ISSUED_EPOCH':now,'WATCH_UNTIL_EPOCH':now+86400}
    run('Delta audit: rollback after Run gates refuses before issue, watch and proven close',
        setup=lambda:close_stamp(latest/'runner_receipt.json',now),overrides=proven_now,fill_changes=issue_now,
        full_start=True,run_boot=boot_at(now+expected+60),run_anchor=now-2,
        want=False,contains=f'arm clock before earliest authorized t0 {now}')
    run('Run forwards the exact latest close, issue and observation bound',
        setup=lambda:close_stamp(latest/'runner_receipt.json',now),overrides=proven_now,fill_changes=issue_now,
        full_start=True,run_boot=boot_at(now+expected+60),contains=f'--t0-not-before {now}')
    for lower in ('ISSUED_EPOCH','WATCH_UNTIL_EPOCH','QUEUE_COMMIT_EPOCH','PRED_CLOSE_EPOCH','PRIOR_CLOSE_EPOCH','EFF_EPOCH'):
        opening=now+86400 if lower=='WATCH_UNTIL_EPOCH' else now
        run('inclusive start from '+lower,command=f'EXPIRES_EPOCH={now+86400}; QUEUE_EXPIRES_EPOCH={now+86400}; '
            f'{lower}={opening}; arm_bound_gate && echo "LOWER $ARM_NOT_BEFORE_EPOCH"',contains=f'LOWER {now}')
    batch_only=f'ARM_BEFORE_EPOCH={now+86400}; batch_gate && echo "FINAL CUTOFF $ARM_BEFORE_EPOCH"'
    for label, batch, allow in (
        ('expected close one second before batch',now+expected+1,True),
        ('batch starts exactly at expected close',now+expected,False),
        ('batch starts exactly at soak end',now+1950,False),
        ('batch during soak',now+1200,False),
        ('batch starts at arm',now,False),
        ('one second before 27-minute release',now-1619,False),
        ('exact 27-minute release',now-1620,True),
    ):
        note='FINAL CUTOFF '+str(now+1) if batch==now+expected+1 else (
            'FINAL CUTOFF' if allow else f'arm at or after {batch+1620}')
        run('C.4 '+label,overrides={'BATCH_SYSCTL':boot_at(batch)},command=batch_only,want=allow,contains=note)
    run('C.4 missing boot STOP',overrides={'BATCH_SYSCTL_RC':1},command=batch_only,want=False,contains='boot time unavailable')
    run('C.4 malformed boot STOP',overrides={'BATCH_SYSCTL':'invalid'},command=batch_only,want=False,contains='unreadable boot time')
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
    run('C.3 queue date binding STOP',overrides={'T0_DATE':'2026-11-22'},command='queue_gate',want=False,contains='span date')
    run('C.3 queue kit binding STOP',overrides={'KIT_SHA':'0'*64},command='queue_gate',want=False,contains='kit')
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
    run('feed stop unproven STOP',overrides={'FEEDS_STOPPED':0},want=False,contains='feed stop')
    run('process group unproven STOP',overrides={'GROUPS_ABSENT':0},want=False,contains='STOP')
    run('foreign process alive STOP',overrides={'FOREIGN_PROCESSES_ABSENT':0},want=False,contains='absence unproven')
    run('stale restore receipt identity STOP',overrides={'CLOSE_PROOF_RECEIPT':str(predout/'runner_receipt.json')},
        want=False,contains='proof must bind the latest close receipt')
    run('RL-179 noncampaign close proof permits start immediately',
        setup=lambda:close_stamp(latest/'runner_receipt.json',now),
        overrides={'NONCAMPAIGN_COPY_CLOSE_EPOCH':now},contains=f'CLOSE PROVEN latest {now}')
    run('fractional close rounded up to the next whole second',
        setup=lambda:close_stamp(latest/'runner_receipt.json',now-0.1),
        overrides={'NONCAMPAIGN_COPY_CLOSE_EPOCH':now},contains=f'CLOSE PROVEN latest {now}')
    run('future close refused even with matching proof',
        setup=lambda:close_stamp(latest/'runner_receipt.json',now+0.1),
        overrides={'NONCAMPAIGN_COPY_CLOSE_EPOCH':now+1},want=False,contains='close stamp is in the future')
    outside=home/'external-runner_receipt.json'
    run('declared external close without a receipt STOP',
        overrides={'OTHER_CLOSE_EPOCH':now,'OTHER_CLOSE_RECEIPT':str(outside)},
        want=False,contains='unreadable receipt close stamp')
    run('proven external close can be the latest receipt',
        setup=lambda:dump(outside,{'synthetic_fixture':True,'ended':{'epoch_s':now}}),
        overrides={'OTHER_CLOSE_EPOCH':now,'OTHER_CLOSE_RECEIPT':str(outside),'CLOSE_PROOF_RECEIPT':str(outside),
                   'NONCAMPAIGN_COPY_RECEIPT':str(outside),'NONCAMPAIGN_COPY_CLOSE_EPOCH':now},
        contains=f'CLOSE PROVEN latest {now}')
    campaign_receipt=root/'cl-hp-01'/'cq-hp-01-s03-a1-20261119T110000Z'/'runner_receipt.json'
    campaign_proof={'LAST_CLOSE_KIND':'campaign','CLOSE_PROOF_RECEIPT':str(campaign_receipt)}
    def campaign_close(age):
        dest=campaign_receipt.parent; dest.parent.mkdir(parents=True); latest.rename(dest); close_stamp(campaign_receipt,now-age)
        (markers/'cq-hp-01-s03-a1.ok').write_text('SYNTHETIC verified offload')
    def campaign_no_copy():
        campaign_close(300); (markers/'cq-hp-01-s03-a1.ok').unlink()
    def air_copy():
        campaign_close(300); (markers/'cq-hp-01-s03-a1.ok').rename(markers/'cq-hp-01-s03-a1.air.ok')
    run('campaign marker missing WAIT',setup=campaign_no_copy,overrides=campaign_proof,want=False,contains='WAIT')
    run('Air campaign marker accepted',setup=air_copy,overrides=campaign_proof)
    run('RL-179 campaign close proof permits start immediately',
        setup=lambda:campaign_close(0),overrides=campaign_proof,contains=f'CLOSE PROVEN latest {now}')
    def date_receipt(camp,span,day,roster,attempt=1):
        out=root/camp/f'cq-{span}-a{attempt}-20261119T000000Z'
        dump(out/'runner_receipt.json',{'synthetic_fixture':True,'started':{'epoch_s':epoch(day)},'roster':roster})
    run('development receipt on qual date REFUSE',
        setup=lambda:date_receipt('cl-dev-99','dev-99-s01',item['date'],['L001']),
        command='day_gate',want=False,contains='development receipt')
    run('one block with declared cap applies',command='day_gate',contains='cap applies')
    plan=META['dates']
    def dates_arg(dates):
        return ','.join(k+'='+v for k,v in dates.items())
    other=next(i['span'] for i in META['items'] if i['block']!=item['block'])
    run('C.3 shared date between blocks REFUSE',overrides={'QUAL_DATES':dates_arg({**plan,other:item['date']})},
        command='day_gate',want=False,contains='one qualification block')
    run('C.3 duplicate plan key REFUSE',overrides={'QUAL_DATES':dates_arg(plan)+','+item['span']+'='+item['date']},
        command='day_gate',want=False,contains='six unique span dates')
    run('known development date REFUSE',overrides={'T0_DATE':'2026-11-18','QUAL_DATES':dates_arg({**plan,item['span']:'2026-11-18'})},
        stamp=epoch('2026-11-18'),command='day_gate',want=False,contains='development date')
    run('C.3 qualifying span with existing t0 cannot re-arm',
        setup=lambda:date_receipt(item['camp'],item['span'],item['date'],item['legs']),
        command='day_gate',want=False,contains='already has a recorded t0')
    shift=lambda date: (dt.date.fromisoformat(date)+dt.timedelta(days=1)).isoformat()
    revised={span:shift(day) if span>=item['block']+'-s02' else day for span,day in plan.items()}
    if item['span'].endswith('s02'):
        later=shift(item['date'])
        midnight=epoch(later)-43200
        run('C.3 legacy submicrosecond receipt remains on the prior local date',
            setup=lambda:mutate(started={'epoch_s':midnight-0.0000002}),
            command='day_gate',contains='DAY OK')
        run('C.3 exact receipt nanoseconds remain on the prior local date',
            setup=lambda:mutate(started={'epoch_ns':midnight*1_000_000_000-1,'epoch_s':midnight}),
            command='day_gate',contains='DAY OK')
        run('C.3 missing s02 cannot use old-date item',stamp=epoch(later),
            command='day_gate',want=False,contains='outside this item t0-date')
        recovery={'T0_DATE':later,'QUAL_DATES':dates_arg(revised)}
        run('C.3 missing s02 can use later unused date; s01 date retained',stamp=epoch(later),
            overrides=recovery,command='day_gate',contains='DAY OK')
        run('C.3 recovery without recorded s01 REFUSE',setup=lambda:shutil.rmtree(predout),
            stamp=epoch(later),overrides=recovery,command='day_gate',want=False,contains='must move whole')
        run('C.3 re-dating recorded s01 REFUSE',stamp=epoch(later),
            overrides={**recovery,'QUAL_DATES':dates_arg({**revised,item['predecessor']:later})},
            command='day_gate',want=False,contains='receipt disagrees with its span plan')
        run('C.3 second receipt for recorded s01 REFUSE',stamp=epoch(later),overrides=recovery,
            setup=lambda:date_receipt(item['camp'],item['predecessor'],item['date'],item['predecessor_legs'],2),
            command='day_gate',want=False,contains='multiple receipts')
        queue_path=auth/item['queue_path']
        queue=json.loads(queue_path.read_bytes())
        next(entry for entry in queue['spans'] if entry['span_id']==item['span'])['not_before']=later
        dump(queue_path,queue)
        git(auth,'add',item['queue_path'])
        git(auth,'commit','-q','-m','Synthetic half-run queue',env=env)
        recovery_commit=git(auth,'rev-parse','HEAD')
        git(auth,'update-ref','refs/remotes/origin/audit/2026-11-10-fable',recovery_commit)
        later_noon=epoch(later)
        run('C.3 full recovery with authenticated later queue and original s01',stamp=later_noon,
            overrides={**recovery,'QUEUE_SHA':hashlib.sha256(queue_path.read_bytes()).hexdigest(),
                       'WINDOW_START':later_noon-43200,'WINDOW_END':later_noon+43199,
                       'WATCH_UNTIL_EPOCH':later_noon+10000},
            fill_changes={'QUEUE_COMMIT':recovery_commit,'ISSUED_EPOCH':later_noon-100},
            contains='BATCH OK')
    else:
        run('C.3 split plan for an untouched block REFUSE',overrides={'QUAL_DATES':dates_arg(revised)},
            command='day_gate',want=False,contains='must move whole')
    if item['span'].endswith('s01'):
        pair_budget=int(item['launch_minimum_s'])
        # If s02's item expires at exactly the backed-out handoff, s01 is too late.
        run('WS 4 s02 item expiry binds s01', overrides={'S02_ISSUED_EPOCH': now+pair_budget-86400},
            want=False, contains='effective t0 cutoff')
        run('WS 4 s02 cutoff exact last second', overrides={'S02_ISSUED_EPOCH': now+pair_budget+1-86400})
        run('WS 4 s02 queue expiry binds s01',
            command=f'EXPIRES_EPOCH={now+86400}; QUEUE_EXPIRES_EPOCH={now+pair_budget}; arm_bound_gate',
            want=False, contains='effective t0 cutoff')
    day_start=epoch(item['date'])-43200
    limit=day_start+(16*3600+32*60 if item['span'].endswith('s01') else 86399)
    for t in (day_start,limit):
        run('date endpoint admitted',stamp=t,command='window_gate')
    run('one second before date REFUSE',stamp=epoch(item['date'])-43201,command='window_gate',want=False,contains='REFUSE')
    run('D8/window one second past LIMIT REFUSE',stamp=limit+1,command='window_gate',want=False,contains='REFUSE')

for shell in ('bash','zsh'):
    assert shutil.which(shell),shell
    for item in META['items']: run_item(item,shell)
print(checks,'synthetic gate checks;',failures,'failures; exact item functions under bash and zsh')
sys.exit(bool(failures))
