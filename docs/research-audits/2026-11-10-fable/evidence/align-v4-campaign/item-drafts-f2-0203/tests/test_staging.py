"""Stage in a disposable local sparse clone; no network or MBP access."""
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
    env={**os.environ,'GIT_AUTHOR_NAME':'Synthetic fixture','GIT_AUTHOR_EMAIL':'fixture@invalid',
         'GIT_COMMITTER_NAME':'Synthetic fixture','GIT_COMMITTER_EMAIL':'fixture@invalid'}
    commit=subprocess.check_output(['git','-C',str(repo),'commit-tree',tree_sha,'-m',
        'Synthetic staging fixture only\n\nCo-Authored-By: Sol 6.1 via codex <noreply@openai.com>'],env=env,text=True).strip()
    fence=root/'fence'; fence.mkdir()
    admission=root/'administrative-admission.json'
    def stage(span,record,want=True,extra=()):
        global checks
        admission.write_text(json.dumps(record))
        r=subprocess.run([sys.executable,'-B',str(HERE/'stage_mbp_span.py'),span,'--commit',commit,
            '--admission',str(admission),'--repo',str(repo),'--wt-root',str(root/'wt'),
            '--campaign-root',str(root/'campaign'),'--f2-root',str(root/'f2-out'),'--fence-root',str(fence),
            '--process-pattern','^JW_RL174_SYNTHETIC_ABSENT$',*extra],text=True,capture_output=True)
        assert (r.returncode==0)==want,(span,extra,r.stdout,r.stderr)
        checks+=1
    for kit in json.loads((HERE/'evidence/kit-build.json').read_text())['kits']:
        hp=kit['name']=='cl-hp-02'; folder='hp-02' if hp else kit['name']
        items=json.loads((HERE/folder/'items.json').read_text())
        record={'nothing_armed':True,'delta':'ADMIT','kit_issued_epoch':int(time.time())-60,
            'inst01_piece1_hand_read':'PASS','kit_sha256':kit['sha256'],'lm_hp_01_run':False,
            'lm_hp_01_record':'SYNTHETIC administrative no-run record','own_piece1_hand_read':'PASS'}
        first=items[0]['span']
        stage(first,record,extra=['--dry-run'])
        for bad in ({'delta':'PENDING'},{'nothing_armed':False},{'kit_sha256':'0'*64},
                    {'kit_issued_epoch':int(time.time())-604801}): stage(first,{**record,**bad},want=False)
        stage(first,{**record,**({'lm_hp_01_run':True} if hp else {'inst01_piece1_hand_read':'FAIL'})},want=False)
        stage(first,record); stage(first,record)
        for item in items[1:]:
            extra=[]
            if not hp:
                qp='synthetic/'+folder+'-queue-b.json'; qbytes=run(repo,'show',commit+':'+qp).encode()+b'\n'
                extra=['--queue-commit',commit,'--queue-path',qp,'--queue-sha',hashlib.sha256(qbytes).hexdigest()]
                stage(item['span'],{**record,'own_piece1_hand_read':'FAIL'},want=False,extra=extra)
                stage(item['span'],record,want=False)
            stage(item['span'],record,extra=extra)
        (fence/'desk_fence.json').write_text('SYNTHETIC fence, never opened')
        stage(first,record,want=False); (fence/'desk_fence.json').unlink()
        wt=root/'wt'/('cadence-'+first)
        dirty=wt/'SYNTHETIC-dirty'; dirty.write_text('fixture')
        stage(first,record,want=False); dirty.unlink()
        assert not run(wt,'status','--porcelain')
        print('PASS',folder,'local dry/stage/reuse/all spans/admission/hand/fence/dirty refusals')
print(checks,'local staging checks PASS; no network, measurement Mac or measured files')
