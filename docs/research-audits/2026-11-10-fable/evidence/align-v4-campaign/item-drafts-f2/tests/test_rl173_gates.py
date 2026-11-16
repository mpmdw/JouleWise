"""Execute each draft's exact gates in bash/zsh on temporary synthetic spans.

Adapted from item-drafts-1115/tests/test_rl173_gates.py. No local campaign,
measurement or custody roots are accessed. Fixed clock tests include expiry,
argument changes and boundary seconds. No mocks of the gate functions themselves.
"""
import ast
import copy
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parents[1]
ITEMS = json.loads((HERE/'items.json').read_text())
ISSUE = 'ISSUED_EPOCH=<LEAD FILLS: the issue time as an epoch, from `date +%s` at issue>'
WATCH = "WATCH_UNTIL_EPOCH=<LEAD FILLS: line 7's watcher observation stamp + 86,400 s, as an epoch>"
TZ = ZoneInfo('America/Los_Angeles')
checks = failures = 0

def quote(s): return "'" + str(s).replace("'", "'\"'\"'") + "'"
def dump(p, obj):
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj))

def run_item(item, shell):
    global checks, failures
    text = (HERE/f"ITEM-{item['item']}.md").read_text()
    blocks = re.findall(r'```sh\n(.*?)```',text,re.S)
    cfg = re.search(r'PIECE=.+\n',blocks[0]).group()
    pick = re.search(r'pick_arg\(\) \{.*?\n\}',blocks[0],re.S).group()
    gates = blocks[0].split('# BEGIN TESTABLE GATES\n')[1].split('# END TESTABLE GATES')[0]
    assert gates.count(ISSUE) == gates.count(WATCH) == 1
    # The gates tested must also be the gates used twice by the runnable item.
    assert sum(b.count('all_gates || exit 1') for b in blocks) == 2
    assert '--legs '+','.join(item['legs']) in blocks[1]
    syntax='\n'.join(blocks).replace(ISSUE,'ISSUED_EPOCH=1').replace(WATCH,'WATCH_UNTIL_EPOCH=2')
    parsed=subprocess.run([shell,'-n'],input=syntax,text=True,capture_output=True)
    assert parsed.returncode==0,(shell,item['item'],parsed.stderr)
    for program in re.findall(r"<<'PY'\n(.*?)\nPY",syntax,re.S): ast.parse(program)
    with tempfile.TemporaryDirectory(prefix='jw-f2-gates-') as tmp:
        base = Path(tmp); root=base/'campaign-out'; wt=base/'jw-wt'; markers=base/'markers'
        now = item['forecast_epoch']
        predout = root/item['predecessor_camp']/f"cq-{item['predecessor']}-a1-20261116T080000Z"
        current = root/'f2-inst-01'/'cq-synthetic-latest-a1-20261116T090000Z'
        latest_id = current.name[:-17]
        gates = gates.replace('/Users/edr/campaign-out',str(root)).replace('/Users/edr/code/jw-wt',str(wt)).replace('/Users/Shared/JouleWise/desk-copy',str(markers))
        # close_gate's path discriminator must follow the same temp root substitution.
        def fixture():
            for d in (root,wt,markers): shutil.rmtree(d,ignore_errors=True); d.mkdir()
            receipt = {'synthetic_fixture':True, 'rc':0,'error':None,'mock':False,
                       'roster':item['predecessor_legs'],'legs_planned':len(item['predecessor_legs']),
                       'legs_finished':len(item['predecessor_legs']),
                       'span_result':{'outcome':'MEASURED_OK','chain_outcome':'COMPLETE','fault':False},
                       'runner_kind':'cadence-legs-v1.1',
                       'kit':{'campaign_id':item['predecessor_camp'],'frozen_commit':'2d347f721552fe03bdd19f113e7bad7a7c24908e',
                              'sha256':'0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b' if item['piece']==1 else '651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b'},
                       'steps':[{'name':x,'rc':0} for x in ('restore','stop-agents','stop-meter','stop-volumes')],
                       'feeds':{x:{'stop':{'proven_stopped':True}} for x in ('agents','meter','volumes')},
                       'meter':{'present':True,'proven_stopped':True,'bad_polls':0,'usb_errors':0},
                       'ended':{'epoch_s':now-4000}}
            dump(predout/'runner_receipt.json',receipt)
            os.utime(predout/'runner_receipt.json',(now-4000,now-4000))
            for leg in item['predecessor_legs']:
                dump(predout/'desk-bundle'/'legs'/leg/'leg_summary.json',{'wall_s':1361,'budget_s':1361,'contaminated_redos':0})
            dump(current/'runner_receipt.json',{'synthetic_fixture':True})
            os.utime(current/'runner_receipt.json',(now-1200,now-1200))
            (markers/f'{latest_id}.ok').write_text('SYNTHETIC verified plaintext/ciphertext hashes, size, provider confirmation\n')
        def mutate_receipt(**kwargs):
            p=predout/'runner_receipt.json'; r=json.loads(p.read_text()); r.update(kwargs); dump(p,r)
            os.utime(p,(now-4000,now-4000))
        def summary(leg, **kwargs):
            p=predout/'desk-bundle'/'legs'/leg/'leg_summary.json'; s=json.loads(p.read_text()); s.update(kwargs); dump(p,s)
        defaults = dict(PRIOR_CLOSE_EPOCH=now-4000, OTHER_CLOSE_EPOCH=0, HOST_RESTORE_OK=1, GROUPS_ABSENT=1,
                        LAST_CLOSE_KIND='other', SESSION_READY='no',HP_READY='no',P_READY='no',
                        F0_ELIGIBLE='no', F0_REASON='daily_cap',OUTSTANDING_REFUSAL='none', F2_STOPS_CLEAR='yes',
                        RESTART_PENDING='no',NEXT_COUNTED_EPOCH=now+13010,PRIORITY_EVIDENCE='synthetic fresh staged/READY census',
                        F2_RECHECK_OK='yes',DEV03_SMOKE_CLOSED='yes',LINE2_OK='yes',LINE9_OK='yes',CHECKLIST_OK='yes',
                        QUEUE_AUTHORIZED='yes',COPY_KEY_SAFE='yes',F2_HAND_READ='PASS',QUEUE_B_COMMITTED='yes')
        def check(name, setup=lambda:None, overrides=None, want=True, command='all_gates', stamp=None, issued=None, watch=None, contains=None):
            global checks, failures
            fixture(); setup(); env=copy.copy(defaults); env.update(overrides or {})
            stamp=now if stamp is None else stamp
            f=gates.replace(ISSUE,f'ISSUED_EPOCH={now-100 if issued is None else issued}').replace(WATCH,f'WATCH_UNTIL_EPOCH={now+10000 if watch is None else watch}')
            args = [f'{k}={quote(v)}' if v is not None else f'unset {k}' for k,v in env.items()]
            script=f'PY={quote(sys.executable)}\n'+cfg+pick+'\n'+f+f'\ndate() {{ echo {stamp}; }}\n'+'\n'.join(args)+f'\nARG="$(pick_arg {stamp})"\n{command}\n'
            result=subprocess.run([shell],input=script,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            passed=(result.returncode==0)==want and (contains is None or contains in result.stdout+result.stderr)
            checks+=1
            if not passed:
                failures+=1; print('FAIL',item['item'],shell,name,result.returncode,(result.stdout+result.stderr)[-800:])
        check('clean complete path')
        check('no predecessor dir WAIT',lambda:shutil.rmtree(predout),want=False,contains='WAIT')
        check('receipt pending WAIT',lambda:(predout/'runner_receipt.json').unlink(),want=False,contains='WAIT')
        check('lookalike ignored',lambda:predout.rename(predout.with_name(predout.name.replace('-a1-','b-a1-'))),want=False)
        check('two predecessor attempts STOP',lambda:shutil.copytree(predout,predout.with_name(predout.name.replace('-a1-','-a2-'))),want=False,contains='multiple')
        for key,val in [('rc',1),('error','refusal'),('mock',True),('roster',[]),('legs_finished',0),('legs_planned',99),('span_result',{'fault':True}),('steps',[]),('ended',{'epoch_s':float('nan')}),('feeds',{}),('meter',{}),('kit',{}),('runner_kind','cadence-legs-v1')]:
            check('bad predecessor '+key,lambda k=key,v=val:mutate_receipt(**{k:v}),want=False,contains='VOID')
        check('bad restore',lambda:mutate_receipt(steps=[{'name':'restore','rc':1}]),want=False)
        check('feed stop missing',lambda:mutate_receipt(feeds={'meter':{'stop':{'proven_stopped':False}}}),want=False)
        check('bad receipt json',lambda:(predout/'runner_receipt.json').write_text('{'),want=False)
        check('no summary',lambda:(predout/'desk-bundle'/'legs'/item['predecessor_legs'][0]/'leg_summary.json').unlink(),want=False)
        check('negative budget',lambda:summary(item['predecessor_legs'][0],budget_s=-1),want=False)
        check('nonfinite wall',lambda:summary(item['predecessor_legs'][0],wall_s=float('inf')),want=False)
        check('two overtime',lambda:[summary(x,wall_s=9999) for x in item['predecessor_legs'][:2]],want=False,contains='LEG_OVERTIME')
        check('one overtime allowed',lambda:summary(item['predecessor_legs'][0],wall_s=9999))
        check('two loaded allowed',lambda:summary(item['predecessor_legs'][0],contaminated_redos=2))
        check('three loaded stop',lambda:summary(item['predecessor_legs'][0],contaminated_redos=3),want=False,contains='CONTAMINATED_REDOS')
        check('prior older than pred',overrides={'PRIOR_CLOSE_EPOCH':1},want=False)
        check('prior unset',overrides={'PRIOR_CLOSE_EPOCH':None},want=False)
        check('expiry exact 24h',issued=now-86400,want=False,contains='VOID')
        check('expiry second before',issued=now-86399)
        check('issue in future',issued=now+1,want=False)
        check('watch exactly 24h',watch=now,want=False)
        check('watch second before',watch=now+1)
        check('watch future observation',watch=now+86401,want=False)
        check('kit void',stamp=1795325340,issued=1795325300,watch=1795325400,want=False,command='expiry_gate')
        check('missing root',lambda:shutil.rmtree(wt),want=False,contains='missing receipt root')
        check('empty census',lambda:[p.unlink() for p in root.rglob('runner_receipt.json')],want=False,command='effective_close',contains='empty receipt census')
        check('ambiguous newest receipt',lambda:os.utime(predout/'runner_receipt.json',(now-1200,now-1200)),want=False,command='effective_close',contains='ambiguous newest')
        check('round fractional close up',lambda:os.utime(current/'runner_receipt.json',(now-1199.9,now-1199.9)),want=False,contains='interval 1200')
        check('F2 gap exactly 1200')
        check('F2 gap 1199',lambda:os.utime(current/'runner_receipt.json',(now-1199,now-1199)),want=False)
        check('restore unproven',overrides={'HOST_RESTORE_OK':0},want=False)
        check('group absence unproven',overrides={'GROUPS_ABSENT':0},want=False)
        check('kind contradiction',overrides={'LAST_CLOSE_KIND':'campaign'},want=False)
        check('OTHER unset',overrides={'OTHER_CLOSE_EPOCH':None},want=False)
        check('OTHER newer without copy',overrides={'OTHER_CLOSE_EPOCH':now-1200},
              setup=lambda:os.utime(current/'runner_receipt.json',(now-1300,now-1300)),want=False)
        def other_copy():
            os.utime(current/'runner_receipt.json',(now-1300,now-1300))
            (markers/'slot-synthetic.ok').write_text('SYNTHETIC verified offload')
        check('OTHER newer with copy',overrides={'OTHER_CLOSE_EPOCH':now-1200,'OTHER_COPY_PLAN_ID':'slot-synthetic'},setup=other_copy)
        def campaign_close(age):
            dest=root/'cl-dev-04'/'cq-dev-04-s02-a1-20261117T090000Z'; dest.parent.mkdir(parents=True)
            current.rename(dest)
            os.utime(dest/'runner_receipt.json',(now-age,now-age))
            (markers/f'{latest_id}.ok').rename(markers/'cq-dev-04-s02-a1.ok')
        check('campaign gap exactly 300',lambda:campaign_close(300),overrides={'LAST_CLOSE_KIND':'campaign'})
        check('campaign gap 299',lambda:campaign_close(299),overrides={'LAST_CLOSE_KIND':'campaign'},want=False,contains='interval 300')
        check('no copy marker',lambda:shutil.rmtree(markers),want=False,contains='WAIT')
        check('empty copy marker',lambda:(markers/f'{latest_id}.ok').write_text(''),want=False)
        check('Air marker accepted',lambda:(markers/f'{latest_id}.ok').rename(markers/f'{latest_id}.air.ok'))
        for key in ('SESSION_READY','HP_READY','P_READY'):
            check(key+' takes precedence',overrides={key:'yes'},want=False,contains='CEDE')
            check(key+' unknown stops',overrides={key:None},want=False)
        check('F0 eligible cedes',overrides={'F0_ELIGIBLE':'yes'},want=False,contains='CEDE')
        for reason in ('spacing','daily_cap','launch_window'): check('F0 reason '+reason,overrides={'F0_REASON':reason})
        check('unsafe F0 refusal',overrides={'F0_REASON':'restore_failed'},want=False)
        check('outstanding refusal',overrides={'OUTSTANDING_REFUSAL':'dev-04-s01'},want=False)
        check('F2 open stop',overrides={'F2_STOPS_CLEAR':'no'},want=False)
        check('host event pending',overrides={'RESTART_PENDING':'yes'},want=False)
        check('counted launch now',overrides={'NEXT_COUNTED_EPOCH':now},want=False,contains='CEDE')
        check('counted horizon minus second',overrides={'NEXT_COUNTED_EPOCH':now+13009},want=False)
        check('counted horizon exact',overrides={'NEXT_COUNTED_EPOCH':now+13010})
        check('counted explicit empty',overrides={'NEXT_COUNTED_EPOCH':0})
        check('counted unknown',overrides={'NEXT_COUNTED_EPOCH':None},want=False)
        check('priority evidence absent',overrides={'PRIORITY_EVIDENCE':''},want=False)
        for key in ('F2_RECHECK_OK','DEV03_SMOKE_CLOSED','LINE2_OK','LINE9_OK','CHECKLIST_OK','QUEUE_AUTHORIZED','COPY_KEY_SAFE'):
            check('admission '+key,overrides={key:'no'},want=False)
        for key in ('F2_HAND_READ','QUEUE_B_COMMITTED'):
            check('hand gate '+key,overrides={key:'no'},want=item['piece']==1)
        for lo,hi,arg in item['bands']:
            for t in (lo,hi):
                check('band endpoint',stamp=t,command=f'ARG={quote(arg)}; window_gate')
                check('wrong argument',stamp=t,command=f'ARG={quote("13:14-13:15" if arg=="02:00-02:35" else "02:00-02:35")}; window_gate',want=False)
        a=item['bands'][0][0]; z=item['bands'][-1][1]
        for t in (a-1,z+1,a+39001,a+47699): check('outside date/dead band',stamp=t,command='window_gate',want=False)
        print('PASS',item['item'],shell,'gate cases complete')

for shell in ('bash','zsh'):
    if not shutil.which(shell): raise SystemExit(f'Required shell missing: {shell}')
    for item in ITEMS: run_item(item,shell)
print(f'{checks} synthetic gate checks; {failures} failures; both bash and zsh; no MBP/custody')
sys.exit(bool(failures))
