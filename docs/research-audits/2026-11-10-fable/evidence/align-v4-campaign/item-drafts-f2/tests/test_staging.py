"""Staging integration test: temporary local clone, env overrides only, no MBP.

Usage: python3 -B tests/test_staging.py /path/to/local/source-clone
Queue b is a SYNTHETIC test commit in the temporary clone, never published.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parents[1]
PIN='2d347f721552fe03bdd19f113e7bad7a7c24908e'
SRC='1f683fc634ed6b8722a3976af400920ee1f7dd7d'
tests=0
def run(args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, check=True, **kwargs).stdout.strip()

with tempfile.TemporaryDirectory(prefix='jw-f2-stage-') as tmp:
    root=Path(tmp); repo=root/'repo'
    run(['git','clone','--shared','--no-checkout',str(Path(sys.argv[1]).resolve()),str(repo)])
    run(['git','sparse-checkout','init','--cone'],cwd=repo)
    run(['git','sparse-checkout','set','scripts','joulewise','configs/align/v4','configs/campaigns/align_v4'],cwd=repo)
    # A synthetic, expressly PASSed hand-read only for this local test.
    q=json.loads(run(['git','show',f'{SRC}:docs/process/cadence/queues/f2-inst-01.v1.1.queue-a.json'],cwd=repo))
    q['queue_id']='cq-f2-inst-01-b'; q['spans']=[]
    for n in (2,3,4):
        q['spans'].append({'seq':n-1,'span_id':f'f2-inst-p{n}','block_id':'f2-inst',
                           'kit':{'path':'docs/process/cadence/kits/f2-inst-01.v1.1.json','sha256':'651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b'},
                           'legs':[f'L{i:03d}' for i in range(3*n-2,3*n+1)],'attempt':1,'not_before':'2026-11-17'})
    qb=root/'SYNTHETIC-queue-b.json'; qb.write_text(json.dumps(q,indent=1)+'\n')
    # Build the synthetic queue object/commit without checking out unrelated evidence.
    blob=run(['git','hash-object','-w',str(qb)],cwd=repo)
    tree=run(['git','mktree'],cwd=repo,input=f'100644 blob {blob}\tSYNTHETIC-queue-b.json\n')
    tree=run(['git','mktree'],cwd=repo,input=f'040000 tree {tree}\tsynthetic\n')
    env=dict(os.environ,GIT_AUTHOR_NAME='Synthetic fixture',GIT_AUTHOR_EMAIL='fixture@invalid',GIT_COMMITTER_NAME='Synthetic fixture',GIT_COMMITTER_EMAIL='fixture@invalid')
    commit=run(['git','commit-tree',tree,'-m','Synthetic queue b, test only'],cwd=repo,env=env)
    for shell in ('bash','zsh'):
        dest=root/shell; dest.mkdir(); (dest/'custody').mkdir()
        env=dict(os.environ,JW_REPO=str(repo),JW_WT_ROOT=str(dest/'wt'),JW_OUT_ROOT=str(dest/'out'),JW_CUSTODY=str(dest/'custody'),JW_NO_FETCH='1',JW_PGREP_PATTERN='^JW_F2_SYNTHETIC_NO_PROCESS$',
                 JW_F2_HAND_READ='PASS',JW_F2_QUEUE_COMMIT=commit,JW_F2_QUEUE_DIR='synthetic',JW_F2_QUEUE_FILE='SYNTHETIC-queue-b.json',JW_F2_QUEUE_SHA=hashlib.sha256(qb.read_bytes()).hexdigest())
        def stage(span, ok=True, dry=False, changes=None):
            global tests
            e={**env,**(changes or {})}
            r=subprocess.run([shell,str(HERE/'stage_mbp_span.sh')]+(['--dry-run'] if dry else [])+[span],text=True,capture_output=True,env=e)
            assert (r.returncode==0)==ok,(shell,span,r.stdout,r.stderr)
            tests+=1
        stage('f2-inst-p1',dry=True)
        assert not (dest/'out').exists()
        stage('f2-inst-p1'); stage('f2-inst-p1')
        kit=dest/'out/kits/f2-inst-01.v1.1-1f683fc63.json'
        assert hashlib.sha256(kit.read_bytes()).hexdigest()=='651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b'
        stage('f2-inst-p2',ok=False,changes={'JW_F2_HAND_READ':'FAIL'})
        stage('f2-inst-p2',ok=False,changes={'JW_F2_QUEUE_COMMIT':''})
        for n in (2,3,4):
            stage(f'f2-inst-p{n}')
            wp=dest/f'wt/cadence-f2-inst-p{n}'
            assert run(['git','rev-parse','HEAD'],cwd=wp)==PIN
            assert not run(['git','status','--porcelain'],cwd=wp)
        fence=dest/'custody/desk_fence.json'; fence.write_text('SYNTHETIC fence')
        stage('f2-inst-p1',ok=False); fence.unlink()
        dirty=dest/'wt/cadence-f2-inst-p1/SYNTHETIC-dirty'; dirty.write_text('fixture')
        stage('f2-inst-p1',ok=False); dirty.unlink()
        original=kit.read_bytes(); kit.write_text('wrong kit')
        stage('f2-inst-p1',ok=False); kit.write_bytes(original)
        print('PASS',shell,'local staging: dry, create, reuse, all pieces, hand/commit/fence/dirty/hash refusals')
print(tests,'local staging checks; no network or MBP')
