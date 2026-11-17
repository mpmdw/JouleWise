"""Pinned validation, law regeneration, roster attacks, plans and synthetic spans only."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from pinned import HERE, ROOT, PIN, SOURCE, git, pinned, call
meta=json.loads((HERE/'items.json').read_text()); output=Path(sys.argv[1]).resolve(); output.mkdir(exist_ok=True)
checks=0
report={'qualification':'SYNTHETIC ONLY; no hardware or real measurement/custody read','pin':PIN,'source':SOURCE,'checks':[],'mock_spans':[]}
def record(name,result):
    global checks
    checks+=1; report['checks'].append({'name':name,'result':result}); print('PASS',name)
with pinned() as repo:
    for n in range(1,4):
        items=[i for i in meta['items'] if i['block']==f'qual-{n:02d}']; item=items[0]
        kp=HERE/item['kit_file']; kit=json.loads(kp.read_text()); dest=repo/item['kit_path']; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(kp.read_bytes())
        r=call(repo,'scripts/cadence_queue.py','validate-kit',kp,'--repo',ROOT)
        record('validate-kit '+item['block']+' frozen paths',json.loads(r.stdout))
        law=kit['seed_law']
        r=call(repo,'scripts/cadence_queue.py','gen-legs','--law',law['method'],'--campaign-id',kit['campaign_id'],'--master-seed',law['master_seed'],'--n-legs',12,'--bands','q0','--spans',2,'--span-a-tokens','2000,10000,19458,19458','--pairs','19458:3724:4096,19458:3151:4096','--g0-shapes','own,span','--decode-tokens',4096)
        generated=json.loads(r.stdout); assert generated['legs']==kit['legs'] and generated['seed_law']==law
        record('gen-legs exact '+item['block'],generated)
        qp=HERE/item['queue_file']; r=call(repo,'scripts/cadence_queue.py','validate-queue',qp,'--kits-root',repo)
        record('validate-queue '+item['block'],json.loads(r.stdout))
        queue=json.loads(qp.read_text())
        for name,roster in [('cross-law-span',['L006','L007']),('split-pair',[items[0]['short_leg']['leg_id']]),('starts-on-pair',[x['leg_id'] for x in kit['legs'] if x.get('pair')==items[0]['short_leg']['pair']])]:
            attack=json.loads(json.dumps(queue)); attack['spans']=attack['spans'][:1]; attack['spans'][0]['legs']=roster
            ap=repo/'attack-queue.json'; ap.write_text(json.dumps(attack))
            r=call(repo,'scripts/cadence_queue.py','validate-queue',ap,'--kits-root',repo,ok=False); assert r.returncode!=0
            record('validate-queue refuses '+item['block']+' '+name,r.stdout.strip())
        for item in items:
            legs=','.join(item['legs'])
            # Every formerly troublesome time and its adjacent second, including no-window midday/night.
            for hh in ('00:00:00','02:00:00','02:34:59','02:35:00','10:50:00','10:50:01','13:14:59','13:15:00','22:40:01','23:59:59'):
                from datetime import datetime
                from zoneinfo import ZoneInfo
                t=datetime.fromisoformat(item['date']+'T'+hh).replace(tzinfo=ZoneInfo('America/Los_Angeles')).timestamp()
                r=call(repo,'scripts/cadence_legs_runner.py','plan','--kit',kp,'--legs',legs,'--t0',t); p=json.loads(r.stdout)
                assert p['batch_windows']==[] and p['expected_s']==item['expected_s'] and p['worst_case_s']==24750
                # Also exercise the actual pinned launcher's read-only plan adapter, never launch.
                code='import sys,json; from pathlib import Path; sys.path.insert(0,"."); from scripts.launch_cadence_span import cadence_plan,cadence_minimum_seconds; p=cadence_plan(Path(sys.argv[1]),sys.argv[2],None,float(sys.argv[3])); print(json.dumps({"windows":p["batch_windows"],"minimum":cadence_minimum_seconds(p)}))'
                launched=json.loads(call(repo,'-c',code,kp,legs,t).stdout)
                assert launched=={'windows':[],'minimum':27260}
                record('plan/launcher-plan '+item['span']+' '+hh,{'plan_expected_s':p['expected_s'],'work_worst_case_s':p['worst_case_s'],'launcher':launched})
            out=output/item['span']; r=call(repo,'scripts/cadence_legs_runner.py','mock','--kit',kp,'--legs',legs,'--t0-local',item['date']+'T12:00:00','--output',out)
            m=json.loads(r.stdout); assert m['rc']==0 and m['legs']==6 and m['stops']==[]
            receipt=json.loads((out/'runner_receipt.json').read_text()); assert receipt['mock'] is True and receipt['batch_windows']==[]
            assert [l['summary']['g0_role'] for l in receipt['legs']]==['capture']+['consume']*5
            # Exact operational Check on synthetic bytes only. Clear mock in this labeled disposable fixture.
            receipt['mock']=False; receipt['synthetic_fixture']=True; (out/'runner_receipt.json').write_text(json.dumps(receipt))
            text=(HERE/f"ITEM-{item['item']}.md").read_text().split('The Check proper')[1]
            program=re.search(r"<<'PY'\n(.*?)\nPY",text,re.S).group(1)
            import subprocess
            checked=subprocess.run([sys.executable,'-I','-B','-',str(out),legs],input=program,text=True,capture_output=True)
            assert checked.returncode==0,(checked.stdout,checked.stderr)
            report['mock_spans'].append({'span':item['span'],'mock':m,'g0_roles':[l['summary']['g0_role'] for l in receipt['legs']],'item_operational_check_rc':checked.returncode,'qualification':'synthetic fixture, never live evidence'})
            record('mock and exact operational Check '+item['span'],{'rc':m['rc'],'legs':6,'five_consumers':True})
        # One retry allowed; two refusals stop before any leg. No new mock reading grants live admission.
        for refusals,rc in ((1,0),(2,1)):
            out=repo/f'soak-{n}-{refusals}'
            r=call(repo,'scripts/cadence_legs_runner.py','mock','--kit',kp,'--legs',','.join(items[0]['legs']),'--t0-local',items[0]['date']+'T12:00:00','--soak-refusals',refusals,'--output',out,ok=False)
            m=json.loads(r.stdout); assert (m['rc']==0)==(rc==0)
            receipt=json.loads((out/'runner_receipt.json').read_text()); assert len(receipt['soak_attempts'])==2
            record('soak retry '+item['block']+' refusals '+str(refusals),{'rc':m['rc'],'attempts':receipt['soak_attempts']})
    first=meta['items'][0]; kp=repo/'dev05-data-kit.json'; kp.write_bytes(git('show','fecaf73f3579756c6e735f6a9cc74aab011d293a:docs/process/cadence/kits/cl-dev-05.v1.1.json'))
    r=call(repo,'scripts/cadence_legs_runner.py','mock','--kit',kp,'--legs',','.join(first['predecessor_legs']),'--t0-local','2026-11-18T03:00:00','--output',output/'dev-05-s02'); assert json.loads(r.stdout)['rc']==0
    record('synthetic predecessor dev-05-s02',json.loads(r.stdout))
report['total_checks']=checks
(HERE/'evidence/kit-recheck.json').write_text(json.dumps(report,indent=2)+'\n')
print(checks,'pinned checks; zero failures; source/config plus synthetic files only')
