"""Read-only pinned kit/queue/plan checks and synthetic runner characterization.

Writes only compact evidence in this draft folder and disposable synthetic files.
Queue b is validated in a temporary directory, never committed or authorized.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parents[1]
REPO=Path(sys.argv[1]).resolve()
PIN='2d347f721552fe03bdd19f113e7bad7a7c24908e'
SOURCE='1f683fc634ed6b8722a3976af400920ee1f7dd7d'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()==PIN
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','JW_B5_SYNTHETIC_ONLY':'1'}
kitpath=HERE/'f2-inst-01.v1.1.json'; kit=json.loads(kitpath.read_text())
report={'pin':PIN,'kit_source':SOURCE,'kit_sha256':hashlib.sha256(kitpath.read_bytes()).hexdigest(),
        'synthetic_only':True,'checks':[],'mock_spans':[]}
def call(*args):
    r=subprocess.run([sys.executable,'-B',*args],cwd=REPO,env=env,text=True,capture_output=True)
    assert r.returncode==0,(args,r.stdout,r.stderr)
    return json.loads(r.stdout)
for arg in ('02:00-02:35','13:14-13:15'):
    r=call('scripts/cadence_queue.py','validate-kit',str(kitpath),'--repo',str(REPO),'--batch-window',arg)
    report['checks'].append({'validate-kit':arg,'output':r})
generated=call('scripts/cadence_queue.py','gen-legs','--law','sha256-cells-v1','--campaign-id','f2-inst-01',
               '--master-seed','2026111443','--n-legs','12','--bands','q600','--prompt-tokens','256,2000,19458',
               '--g0-shapes','own','--decode-tokens','512')
assert generated['legs']==kit['legs'] and generated['seed_law']==kit['seed_law'], generated
layout=[[x['prefill_tokens'] for x in kit['legs'][i:i+3]] for i in range(0,12,3)]
for size in (256,2000,19458): assert {row.index(size) for row in layout}=={0,1,2}
report['checks'].append({'gen-legs':'exact equality','layout':layout,'every_size_every_position':True})
items=json.loads((HERE/'items.json').read_text())
with tempfile.TemporaryDirectory(prefix='jw-f2-kit-') as temp:
    root=Path(temp); kp=root/'docs/process/cadence/kits/f2-inst-01.v1.1.json'; kp.parent.mkdir(parents=True); kp.write_bytes(kitpath.read_bytes())
    qa=json.loads((HERE/'queue-a.json').read_text())
    report['checks'].append({'validate-queue-a':call('scripts/cadence_queue.py','validate-queue',str(HERE/'queue-a.json'),'--kits-root',str(root))})
    qb={**qa,'queue_id':'cq-f2-inst-01-b','spans':[]}
    for item in items[1:]:
        qb['spans'].append({**qa['spans'][0],'seq':item['piece']-1,'span_id':item['span'],
                            'legs':item['legs'],'not_before':item['date']})
    bp=root/'SYNTHETIC-queue-b.json'; bp.write_text(json.dumps(qb))
    report['checks'].append({'validate-queue-b-SYNTHETIC-NOT-COMMITTED':call('scripts/cadence_queue.py','validate-queue',str(bp),'--kits-root',str(root))})
    for item in items:
        for hour,arg in (('00:30:00','13:14-13:15'),('13:15:00','02:00-02:35')):
            out=root/f"{item['item']}-{hour[:2]}"
            r=call('scripts/cadence_legs_runner.py','mock','--kit',str(kitpath),'--output',str(out),
                   '--legs',','.join(item['legs']),'--t0-local',item['date']+'T'+hour,'--batch-window',arg)
            assert r['rc']==0 and r['legs']==3 and not r['stops']
            receipt=json.loads((out/'runner_receipt.json').read_text())
            assert receipt['mock'] is True
            # Execute the item's operational Check on synthetic bytes only. As in
            # the predecessor-gate test, clear mock solely in this disposable fixture.
            # This never constitutes a live Check or custody/admission evidence.
            check_text=(HERE/f"ITEM-{item['item']}.md").read_text().split('**Check.**')[1]
            check_program=re.search(r"<<'PY'\n(.*?)\nPY",check_text,re.S).group(1)
            receipt['mock']=False; receipt['synthetic_fixture']=True
            (out/'runner_receipt.json').write_text(json.dumps(receipt))
            checked=subprocess.run([sys.executable,'-I','-B','-',str(out),','.join(item['legs'])],input=check_program,
                                   text=True,capture_output=True,env=env)
            assert checked.returncode==0,(checked.stdout,checked.stderr)
            report['mock_spans'].append({'item':item['item'],'t0_local':item['date']+'T'+hour,'argument':arg,
                                         'rc':r['rc'],'legs':r['legs'],'stops':r['stops'],
                                         'item_check_on_synthetic_fixture_rc':checked.returncode,
                                         'restore_rc':[s['rc'] for s in receipt['steps'] if s['name']=='restore'],
                                         'feeds_proven_stopped':all(f['stop']['proven_stopped'] for f in receipt['feeds'].values())})

# Required RL-169a §1 builder observation, using the real orchestration and fake world.
# Read only the generated configuration and operational event/log stamps; no stream/member energy.
os.environ.update(JW_B5_SYNTHETIC_ONLY='1',PYTHONDONTWRITEBYTECODE='1')
sys.path.insert(0,str(REPO))
from tests.cadence.test_legs_runner import LegRuntimeTests
T=LegRuntimeTests; T.setUpClass()
try:
    t=T(); out=t.root/'f2-q600-proof'
    rc,r=t.call(out,t.spec('L002',band='q600',prefill_tokens=256,prefill_chars=526,decode_tokens=512))
    assert rc==0 and r['leg_status']=='complete' and r['decode_tokens']==512
    assert r['quiet_spans_ns'] and r['quiet_spans_ns'][0][1]-r['quiet_spans_ns'][0][0]>=600*10**9
    bundle=out/r['bundle']; cfg=json.loads((bundle/'config.json').read_text())
    task=json.loads(cfg['workload_profile']['prompt_text'])
    assert task['task_kwargs']=={'prefill_chars':526}
    events=[json.loads(line) for line in (bundle/'events.jsonl').read_text().splitlines()]
    stamps=[{k:e.get(k) for k in ('event_type','phase','timestamp_s','metadata')} for e in events
            if e.get('event_type')=='sampling_started' or e.get('phase')=='warmup']
    # Log metadata is operational; these files are generated by this synthetic call only.
    warm_logs=[]
    for p in (bundle/'logs').glob('*.log'):
        for line in p.read_text().splitlines():
            if 'warmup run(s)' in line or 'post-warmup settling' in line: warm_logs.append(line)
    report['warmup_observation']={'nominal_leg_prompt_tokens':256,'task_prefill_chars':526,
                                  'warmup_runs':cfg['workload_profile']['warmup_runs'],
                                  'post_warmup_settling_s':cfg['sampling']['warmup_seconds'],
                                  'events':stamps,'operational_log_lines':warm_logs,
                                  'g0_release_ns':r['quiet_spans_ns'][0][0],
                                  'quiet_spans_ns':r['quiet_spans_ns'],'decode_tokens':r['decode_tokens'],
                                  'qualification':'SYNTHETIC; stage_completed warmup includes post-warmup settling; do not label it the inference-end stamp'}
finally:
    T.tearDownClass()
(HERE/'evidence/kit-recheck.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS pinned kit, generated layout, queue a, temporary queue b, eight mock spans, q600 synthetic runtime')
