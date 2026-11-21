"""Recheck the published data at its original pins; inspect no measured files."""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from build_kits import differences
from draft_queue_b import make_queue
report=json.loads((HERE/'evidence/kit-build.json').read_text())
repos={'f2':Path(sys.argv[1]).resolve(),'hp':Path(sys.argv[2]).resolve()}
checks=[]
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','JW_B5_SYNTHETIC_ONLY':'1'}

def cli(repo,script,*args,want=0):
    r=subprocess.run([sys.executable,'-B','scripts/'+script,*map(str,args)],cwd=repo,env=env,text=True,capture_output=True)
    assert r.returncode==want,(args,r.returncode,r.stdout,r.stderr)
    return json.loads(r.stdout)

for kitrec in report['kits']:
    hp=kitrec['name']=='cl-hp-02'; repo=repos['hp' if hp else 'f2']; path=HERE/kitrec['path']
    kit=json.loads(path.read_text()); folder=path.parent
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==kitrec['pin']
    sourcepath='docs/process/cadence/kits/'+('cl-hp-01.json' if hp else 'f2-inst-01.v1.1.json')
    base=json.loads(subprocess.check_output(['git','show',kitrec['source']+':'+sourcepath],cwd=repo))
    diff=differences(base,kit)
    assert diff==kitrec['delta'] and kit['frozen']==base['frozen']
    assert kit['title']==base['title'] and kit['inclusion_rules']==base['inclusion_rules'] and kit['stop_rules']==base['stop_rules']
    allowed=r'/(campaign_id|ruling/id|seed_law/master_seed|leg_defaults/decode_tokens|legs/\d+/(seed|prefill_tokens|decode_tokens))'
    assert all(re.fullmatch(allowed,x['path']) for x in diff),diff
    if hp: assert not any('decode_tokens' in x['path'] or 'prefill_tokens' in x['path'] for x in diff)
    for arg in ('02:00-02:35','13:14-13:15'):
        result=cli(repo,'cadence_queue.py','validate-kit',path,'--repo',repo,'--batch-window',arg)
        assert result['frozen_paths_verified'] and result['kit_sha256']==kitrec['sha256']
        checks.append([kitrec['name'],'validate-kit',arg,'PASS'])
    args=['gen-legs','--campaign-id',kit['campaign_id'],'--master-seed',kit['seed_law']['master_seed'],
          '--n-legs',12,'--bands','q0' if hp else 'q600','--decode-tokens',kitrec['decode']]
    args+=['--prefill-tokens',19458] if hp else ['--law','sha256-cells-v1','--prompt-tokens','256,2000,19458','--g0-shapes','own']
    generated=cli(repo,'cadence_queue.py',*args)
    assert generated['legs']==kit['legs'] and generated['seed_law']==kit['seed_law']
    checks.append([kitrec['name'],'gen-legs / exact allowed delta','PASS'])
    qa=cli(repo,'cadence_queue.py','validate-queue',folder/'queue-a.json','--kits-root',HERE)
    assert qa['spans']==(3 if hp else 1)
    checks.append([kitrec['name'],'queue a','PASS'])
    with tempfile.TemporaryDirectory(prefix='jw-rl174-verify-') as tmp:
        tmp=Path(tmp)
        if hp:
            assert cli(repo,'cadence_queue.py','validate-queue',folder/'queue-b.json','--kits-root',HERE)['spans']==3
            checks.append([kitrec['name'],'finite successor queue b','PASS'])
        else:
            qb=tmp/'SYNTHETIC-unpublished-b.json'; qb.write_text(json.dumps(make_queue(kitrec['name'])))
            assert cli(repo,'cadence_queue.py','validate-queue',qb,'--kits-root',HERE)['spans']==3
            checks.append([kitrec['name'],'queue b TEMPORARY ONLY','PASS'])
        first=json.loads((folder/'items.json').read_text())[0]
        legs=','.join(first['legs'])
        scenarios=[('contaminated',['--contaminate',first['legs'][0]],0),
                   ('G0-timeout',['--g0-timeout',first['legs'][0]],0)]
        if hp: scenarios.append(('failing-restore',['--fail-close-restore'],2))
        for label,flags,want in scenarios:
            out=tmp/label
            r=cli(repo,'cadence_legs_runner.py','mock','--kit',path,'--legs',legs,'--output',out,
                  '--t0-local','2026-11-19T13:15:00','--batch-window','02:00-02:35',*flags,want=want)
            assert r['rc']==want and r['legs']==3
            if label=='failing-restore': assert any(x['code']=='RESTORE_UNPROVEN' for x in r['stops'])
            else: assert not r['stops'],r
            checks.append([kitrec['name'],'SYNTHETIC '+label,r])
            # Exercise the item's actual operational Check on this disposable
            # fixture. Relabel mock only in the fixture, with synthetic_fixture
            # retained; never promote this to live admission evidence.
            receipt_path=out/'runner_receipt.json'
            receipt=json.loads(receipt_path.read_text()); receipt['mock']=False; receipt['synthetic_fixture']=True
            receipt_path.write_text(json.dumps(receipt))
            text=(folder/('ITEM-'+first['item']+'.md')).read_text().split('**Check.**')[1]
            program=re.search(r"<<'PY'\n(.*?)\nPY",text,re.S).group(1)
            checked=subprocess.run([sys.executable,'-I','-B','-',str(out),legs,'02:00-02:35'],input=program,text=True,capture_output=True,env=env)
            assert (checked.returncode==0)==(want==0),(kitrec['name'],label,checked.stdout,checked.stderr)
            checks.append([kitrec['name'],'embedded Check / SYNTHETIC '+label,'PASS'])
# Exercise the real leg-runtime orchestration with its synthetic adapter world,
# so these doses are checked beyond the runner's fake leg implementation.
os.environ.update(JW_B5_SYNTHETIC_ONLY='1',PYTHONDONTWRITEBYTECODE='1')
sys.path.insert(0,str(repos['f2']))
from tests.cadence.test_legs_runner import LegRuntimeTests
T=LegRuntimeTests; T.setUpClass()
try:
    t=T()
    for dose in (128,256):
        out=t.root/('rl174-dose-'+str(dose))
        rc,result=t.call(out,t.spec('L002',band='q600',prefill_tokens=256,prefill_chars=526,decode_tokens=dose))
        assert rc==0 and result['leg_status']=='complete' and result['decode_tokens']==dose and result['decode_cap_reached']
        assert result['quiet_spans_ns'][0][1]-result['quiet_spans_ns'][0][0]>=600*10**9
        checks.append(['q600 real orchestration / synthetic runtime',dose,'PASS'])
finally:
    T.tearDownClass()
out={'synthetic_only':True,'checks':checks,'count':len(checks),'measurement_streams_opened':False}
evidence = Path(os.environ.get('JW_DRAFT_EVIDENCE_DIR', HERE/'evidence'))
evidence.mkdir(parents=True, exist_ok=True)
(evidence/'pinned-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(len(checks),'pinned kit/law/delta/queue/fault-injection checks PASS; no measured input or stream opened')
