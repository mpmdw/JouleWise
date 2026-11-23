"""Stage in a disposable local sparse clone; no network or MBP access."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from draft_queue_b import make_queue
BASE='docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203'
checks=0
STAGE_TIME = int(datetime.fromisoformat("2026-11-21T12:00:00-08:00").timestamp())
FIXTURE_COMMIT = "2026-11-20T00:00:00-08:00"
TIME_WRAPPER = """
import runpy, sys, time
clock = float(sys.argv[1])
sys.argv = sys.argv[2:]
sys.path.insert(0, str(__import__('pathlib').Path(sys.argv[0]).parent))
time.time = lambda: clock
runpy.run_path(sys.argv[0], run_name='__main__')
"""

def run(repo,*args,input=None):
    return subprocess.check_output(['git','-C',str(repo),*args],input=input).decode().strip()

with tempfile.TemporaryDirectory(prefix='jw-rl174-stage-') as tmp:
    root=Path(tmp); repo=root/'repo'
    subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(Path(sys.argv[1]).resolve()),str(repo)],check=True)
    run(repo,'sparse-checkout','init','--cone')
    run(repo,'sparse-checkout','set','scripts','joulewise','configs/align/v4','configs/campaigns/align_v4')
    tree={}
    def add(path,data):
        d=tree
        parts=path.split('/')
        for part in parts[:-1]: d=d.setdefault(part,{})
        d[parts[-1]]=run(repo,'hash-object','-w','--stdin',input=data)
    for file in HERE.rglob('*'):
        if file.is_file() and '__pycache__' not in str(file): add(BASE+'/'+str(file.relative_to(HERE)),file.read_bytes())
    for name in ('f2-inst-02','f2-inst-03'):
        add('synthetic/'+name+'-queue-b.json',(json.dumps(make_queue(name),indent=1)+'\n').encode())
    def mktree(d):
        lines=[]
        for name,value in sorted(d.items()):
            lines.append(('040000 tree '+mktree(value) if isinstance(value,dict) else '100644 blob '+value)+'\t'+name+'\n')
        return run(repo,'mktree',input=''.join(lines).encode())
    tree_sha=mktree(tree)
    env={**os.environ,'GIT_AUTHOR_DATE':FIXTURE_COMMIT,'GIT_COMMITTER_DATE':FIXTURE_COMMIT,
         'GIT_AUTHOR_NAME':'Synthetic fixture','GIT_AUTHOR_EMAIL':'fixture@invalid',
         'GIT_COMMITTER_NAME':'Synthetic fixture','GIT_COMMITTER_EMAIL':'fixture@invalid'}
    commit=subprocess.check_output(['git','-C',str(repo),'commit-tree',tree_sha,'-m',
        'Synthetic staging fixture only\n\nCo-Authored-By: Sol 6.1 via codex <noreply@openai.com>'],env=env,text=True).strip()
    fence=root/'fence'; fence.mkdir()
    admission=root/'administrative-admission.json'
    def stage(span,record,want=True,extra=(),clock=STAGE_TIME):
        global checks
        admission.write_text(json.dumps(record))
        r=subprocess.run([sys.executable,'-B','-c',TIME_WRAPPER,str(clock),str(HERE/'stage_mbp_span.py'),span,'--commit',commit,
            '--admission',str(admission),'--repo',str(repo),'--wt-root',str(root/'wt'),
            '--campaign-root',str(root/'campaign'),'--f2-root',str(root/'f2-out'),'--fence-root',str(fence),
            '--process-pattern','^JW_RL174_SYNTHETIC_ABSENT$',*extra],text=True,capture_output=True)
        assert (r.returncode==0)==want,(span,extra,r.stdout,r.stderr)
        checks+=1
    for kit in json.loads((HERE/'evidence/kit-build.json').read_text())['kits']:
        hp=kit['name']=='cl-hp-02'; folder='hp-02' if hp else kit['name']
        items=json.loads((HERE/folder/'items.json').read_text())
        record={'nothing_armed':True,'delta':'ADMIT','kit_issued_epoch':STAGE_TIME-60,
            'inst01_piece1_hand_read':'PASS','kit_sha256':kit['sha256'],'lm_hp_01_run':False,
            'lm_hp_01_record':'SYNTHETIC administrative no-run record','own_piece1_hand_read':'PASS'}
        first=items[0]['span']
        starter=[]
        if hp:
            binding=items[0]['queue']
            record.update(queue=binding, observed_epoch_s=STAGE_TIME-1, valid_through_epoch_s=STAGE_TIME,
                          look={'record':'synthetic HP look register','by':'synthetic desk','scope':'lm-hp-01',
                                'kit_sha256':kit['sha256'],'checked_through':STAGE_TIME-1,
                                'execution_register_checked':True,'both_custody_roots_checked':True,
                                'all_execution_routes_covered':True,'status':'not_run','pending_conflict':False})
            starter=['--queue-commit',binding['commit'],'--queue-path',binding['path'],'--queue-sha',binding['sha256']]
            stage(first,record,want=False)
            stage(first,{**record,'queue':{**binding,'sha256':'0'*64}},want=False,extra=starter)
            stage(first,{**record,'valid_through_epoch_s':STAGE_TIME-1},want=False,extra=starter)
            expiry=int(datetime.fromisoformat(items[0]['expires_at']).timestamp())
            for clock,want in ((expiry-1,True),(expiry,False)):
                stage(first,{**record,'observed_epoch_s':clock,'valid_through_epoch_s':clock,
                             'look':{**record['look'],'checked_through':clock}},want=want,
                      extra=[*starter,'--dry-run'],clock=clock)
        stage(first,record,extra=[*starter,'--dry-run'])
        for bad in ({'delta':'PENDING'},{'nothing_armed':False},{'kit_sha256':'0'*64}):
            stage(first,{**record,**bad},want=False,extra=starter)
        stage(first,{**record,'kit_issued_epoch':STAGE_TIME-604801},want=hp,extra=[*starter,'--dry-run'])
        bad={'look':{**record['look'],'status':'ran'}} if hp else {'inst01_piece1_hand_read':'FAIL'}
        stage(first,{**record,**bad},want=False,extra=starter)
        stage(first,record,extra=starter); stage(first,record,extra=starter)
        for item in items[1:]:
            extra=starter
            if not hp:
                qp='synthetic/'+folder+'-queue-b.json'; qbytes=run(repo,'show',commit+':'+qp).encode()+b'\n'
                extra=['--queue-commit',commit,'--queue-path',qp,'--queue-sha',hashlib.sha256(qbytes).hexdigest()]
                stage(item['span'],{**record,'own_piece1_hand_read':'FAIL'},want=False,extra=extra)
                stage(item['span'],record,want=False)
            stage(item['span'],record,extra=extra)
        (fence/'desk_fence.json').write_text('SYNTHETIC fence, never opened')
        stage(first,record,want=False,extra=starter); (fence/'desk_fence.json').unlink()
        wt=root/'wt'/('cadence-'+first)
        dirty=wt/'SYNTHETIC-dirty'; dirty.write_text('fixture')
        stage(first,record,want=False,extra=starter); dirty.unlink()
        assert not run(wt,'status','--porcelain')
        print('PASS',folder,'local dry/stage/reuse/all spans/admission/hand/fence/dirty refusals')
print(checks,'local staging checks PASS; no network, measurement Mac or measured files')
