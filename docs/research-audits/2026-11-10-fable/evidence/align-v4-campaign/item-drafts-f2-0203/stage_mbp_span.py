"""Stage exact committed kit/queue DATA between spans; never launch or use SSH.

The builder tests this only against a disposable local clone. The lead alone
runs it on the MBP after delta admission and a clean close. No measurement,
stream or custody file is opened (the shared fence is checked for existence).
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from prepare_hp_items import PIN as HP_PIN, Refusal, check_look, number, queue_entry

BASE='docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203'

def fail(s): raise SystemExit('STAGE STOP: '+s)
def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args])
def digest(b): return hashlib.sha256(b).hexdigest()
def write_once(path, data):
    if path.is_symlink(): fail('symlink destination: '+str(path))
    if path.exists():
        if path.read_bytes()!=data: fail('different existing bytes: '+str(path))
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f: f.write(data)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('span'); p.add_argument('--commit',required=True)
    p.add_argument('--admission',type=Path,required=True,help='lead administrative admission record, no measured data')
    p.add_argument('--repo',type=Path,default=Path('/Users/edr/code/JouleWise'))
    p.add_argument('--wt-root',type=Path,default=Path('/Users/edr/code/jw-wt'))
    p.add_argument('--campaign-root',type=Path,default=Path('/Users/edr/campaign-out'))
    p.add_argument('--f2-root',type=Path,default=Path('/Users/edr/f2-out'))
    p.add_argument('--fence-root',type=Path,default=Path('/Users/edr/night-custody/magistrate'))
    p.add_argument('--process-pattern',default='cadence_legs_runner|launch_cadence_span|align_r1_rehearsal|run_align_r1|launch_align_r0|km003c_monitor|hazard_monitor')
    p.add_argument('--queue-commit'); p.add_argument('--queue-path'); p.add_argument('--queue-sha')
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(); repo=a.repo.resolve()
    if os.path.lexists(a.fence_root/'desk_fence.json'): fail('shared fence exists; no staging while armed')
    live=subprocess.run(['pgrep','-f',a.process_pattern],capture_output=True)
    if live.returncode==0: fail('runner/monitor process exists')
    if live.returncode!=1: fail('process census failed')
    admission=json.loads(a.admission.read_text())
    if admission.get('nothing_armed') is not True or admission.get('delta')!='ADMIT': fail('clean interval / independent delta required')
    now=time.time(); issued=admission.get('kit_issued_epoch')
    commit=git(repo,'rev-parse',a.commit+'^{commit}').decode().strip()
    if a.span.startswith('f2-inst-02-p'): folder='f2-inst-02'; file=folder+'.v1.1.json'
    elif a.span.startswith('f2-inst-03-p'): folder='f2-inst-03'; file=folder+'.v1.1.json'
    elif a.span.startswith('hp-02-s'): folder='hp-02'; file='cl-hp-02.json'
    else: fail('unknown span')
    hp=folder=='hp-02'
    if not hp and (type(issued) is not int or not issued<=now<issued+604800): fail('lead kit issue / seven-day expiry')
    items=json.loads(git(repo,'show',commit+':'+BASE+'/'+folder+'/items.json'))
    matches=[x for x in items if x['span']==a.span]
    if len(matches)!=1: fail('unknown/ambiguous roster')
    item=matches[0]
    if folder!='hp-02' and admission.get('inst01_piece1_hand_read')!='PASS': fail('inst-01 piece-1 PASS required')
    if admission.get('kit_sha256')!=item['kit_sha']: fail('admission not bound to this kit')
    kp=BASE+'/'+folder+'/'+file
    kb=git(repo,'show',commit+':'+kp); kit=json.loads(kb)
    if digest(kb)!=item['kit_sha']: fail('kit hash')
    pin=kit['frozen']['commit']
    qcommit=commit; qpath=BASE+'/'+folder+'/queue-a.json'
    if hp:
        if pin!=item['pin'] or pin!=HP_PIN: fail('HP pin binding')
        if not all((a.queue_commit,a.queue_path,a.queue_sha)): fail('explicit HP queue commit/path/SHA required')
        qcommit=git(repo,'rev-parse',a.queue_commit+'^{commit}').decode().strip(); qpath=a.queue_path
        binding={'commit':qcommit,'path':qpath,'sha256':a.queue_sha}
        if binding!=item['queue'] or binding!=admission.get('queue'): fail('HP queue differs from admitted item')
        observed=admission.get('observed_epoch_s'); valid=admission.get('valid_through_epoch_s')
        if not number(observed) or not number(valid) or not observed<=now<=valid: fail('stale HP staging evidence')
        try:
            check_look(admission.get('look'),now,observed)
        except (Refusal, KeyError, TypeError) as error:
            fail(str(error))
    elif item['piece']>1:
        if admission.get('own_piece1_hand_read')!='PASS': fail('own piece-1 PASS required before queue b')
        if not all((a.queue_commit,a.queue_path,a.queue_sha)): fail('lead must commit queue b first')
        qcommit=git(repo,'rev-parse',a.queue_commit+'^{commit}').decode().strip(); qpath=a.queue_path
    qb=git(repo,'show',qcommit+':'+qpath); q=json.loads(qb)
    if a.queue_sha and digest(qb)!=a.queue_sha: fail('queue hash')
    expiry=__import__('datetime').datetime.fromisoformat(q['expires_at']).timestamp()
    qtime=int(git(repo,'show','-s','--format=%ct',qcommit).decode())
    if hp:
        if qtime>now: fail('HP queue commit is in the future')
        try:
            queue_entry(item,q,now)
        except (Refusal, KeyError, TypeError, ValueError) as error:
            fail(str(error))
    elif not qtime<=now<expiry or expiry>qtime+604800: fail('queue expired, future commit, or longer than seven days')
    entries=[s for s in q['spans'] if s['span_id']==a.span]
    if len(entries)!=1 or entries[0]['legs']!=item['legs'] or entries[0]['kit']['sha256']!=digest(kb): fail('queue/roster binding')
    wt=(a.wt_root/('cadence-'+a.span)).resolve()
    if wt==repo or repo in wt.parents: fail('worktree inside canonical repo')
    destkit=a.campaign_root/'kits'/(kit['campaign_id']+('-RL174B.json' if folder=='hp-02' else '.v1.1-RL174B.json'))
    destqueue=a.campaign_root/'queues'/Path(qpath).name
    # Per-kit queue names must not alias (all source folders use queue-a.json).
    destqueue=destqueue.with_name(folder+'-'+Path(qpath).name)
    if hp:
        destqueue=destqueue.with_name(f'{folder}-{Path(qpath).stem}-{digest(qb)}.json')
    for path in (destkit.resolve(),destqueue.resolve(),a.f2_root.resolve()):
        if path==repo or repo in path.parents or path==wt or wt in path.parents: fail('data destination inside checkout')
    if folder!='hp-02' and (a.f2_root.resolve()==a.campaign_root.resolve() or a.campaign_root.resolve() in a.f2_root.resolve().parents): fail('F2 root must be outside campaign root')
    if wt.exists():
        if git(wt,'rev-parse','HEAD').decode().strip()!=pin or git(wt,'status','--porcelain').strip(): fail('existing worktree wrong pin or dirty')
        if subprocess.run(['git','-C',str(wt),'symbolic-ref','-q','HEAD'],capture_output=True).returncode==0: fail('existing worktree not detached')
    if a.dry_run:
        print(json.dumps({'dry_run':True,'span':a.span,'pin':pin,'commit':commit,'kit_sha256':digest(kb),'queue_sha256':digest(qb),'worktree':str(wt),'kit':str(destkit),'queue':str(destqueue)}))
        return
    if hp and os.path.lexists(a.fence_root/'desk_fence.json'): fail('shared fence appeared during HP staging')
    if not wt.exists():
        wt.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['git','-C',str(repo),'worktree','add','--quiet','--detach',str(wt),pin],check=True)
    write_once(destkit,kb); write_once(destqueue,qb)
    # This empty root is required by the receipt census, including before its first F2 run.
    a.f2_root.mkdir(parents=True,exist_ok=True)
    stamp=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip()
    record={'span':a.span,'staged_at_date':stamp,'source_commit':commit,'pin':pin,
            'kit':str(destkit),'kit_sha256':digest(kb),'queue':str(destqueue),'queue_commit':qcommit,
            'queue_sha256':digest(qb),'worktree':str(wt),'measurement_started':False}
    rec=a.campaign_root/'staged'/(a.span+'.staged.json'); rec.parent.mkdir(parents=True,exist_ok=True)
    if hp:
        record.update(queue_path=qpath)
        rec=rec.with_name(f'{a.span}-{digest(qb)}.staged.json')
        if rec.is_file() and not rec.is_symlink():
            record['staged_at_date']=json.loads(rec.read_bytes())['staged_at_date']
        write_once(rec,(json.dumps(record,indent=2)+'\n').encode())
    else:
        rec.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))

if __name__=='__main__': main()
