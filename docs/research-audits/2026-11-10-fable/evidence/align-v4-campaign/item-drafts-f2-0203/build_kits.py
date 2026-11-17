"""RL-174 B data-only kit builder. No host contact or measured-data reads.

Usage: python3 -B build_kits.py F2_PIN_WORKTREE HP_PIN_WORKTREE
STOP on any validate-kit/plan/mock refusal; never relax a validator or re-pin.
"""
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
F2_SOURCE = '1f683fc634ed6b8722a3976af400920ee1f7dd7d'
HP_SOURCE = 'bbd34dc87'
F2_PIN = '2d347f721552fe03bdd19f113e7bad7a7c24908e'
HP_PIN = 'dd206025abb30fd5c07515cd4b34b3e653174810'
ENV = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'JW_B5_SYNTHETIC_ONLY': '1'}

def git(*args):
    return subprocess.check_output(['git', *args], cwd=HERE, text=True)

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1) + '\n')

def cli(repo, script, *args):
    r = subprocess.run([sys.executable, '-B', 'scripts/' + script, *map(str, args)],
                       cwd=repo, env=ENV, text=True, capture_output=True)
    if r.returncode:
        raise SystemExit(f'STOP: pinned {script} refused {args}: rc {r.returncode}\n{r.stdout}{r.stderr}\n'
                         'Tell the research lead under RL-174 B; no re-pin or workaround.')
    return json.loads(r.stdout)

def differences(a, b, prefix=''):
    if type(a) is not type(b): return [{'path': prefix, 'before': a, 'after': b}]
    if isinstance(a, dict):
        assert a.keys() == b.keys()
        return [d for k in a for d in differences(a[k], b[k], prefix + '/' + k)]
    if isinstance(a, list):
        assert len(a) == len(b)
        return [d for i, (x,y) in enumerate(zip(a,b)) for d in differences(x,y,prefix+'/'+str(i))]
    return [] if a == b else [{'path': prefix, 'before': a, 'after': b}]

def main(f2repo, hprepo):
    for repo,pin in ((f2repo,F2_PIN),(hprepo,HP_PIN)):
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==pin
    stamp = subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'], text=True).strip()
    # Only kit DATA in this directory is inspected across refs; never evidence roots.
    refs = git('for-each-ref','--format=%(refname)').splitlines()
    blobs = set()
    for ref in refs:
        for line in git('ls-tree','-r',ref,'--','docs/process/cadence/kits').splitlines():
            meta, path = line.split('\t',1)
            if path.endswith('.json'): blobs.add(meta.split()[2])
    used = set()
    for blob in sorted(blobs):
        try: used.add(json.loads(git('cat-file','blob',blob))['seed_law']['master_seed'])
        except (KeyError, ValueError, TypeError): pass
    originals = {
        'f2': json.loads(git('show',F2_SOURCE+':docs/process/cadence/kits/f2-inst-01.v1.1.json')),
        'hp': json.loads(git('show',HP_SOURCE+':docs/process/cadence/kits/cl-hp-01.json'))}
    report = {'built_at_date': stamp, 'synthetic_only': True,
              'seed_scan': {'refs':len(refs),'unique_kit_blobs':len(blobs),'used_master_seeds':sorted(used)},
              'kits': []}
    for name, dose, repo, kind in [('f2-inst-02',128,f2repo,'f2'),('f2-inst-03',256,f2repo,'f2'),
                                   ('cl-hp-02',4096,hprepo,'hp')]:
        base = originals[kind]; kit = copy.deepcopy(base)
        kit['campaign_id'] = name
        # Keep all inherited prose verbatim, including historical doses/expiry.
        # The delta note and items explicitly supersede it under RL-174 B.
        kit['ruling']['id'] = 'RL-174'
        kit['leg_defaults']['decode_tokens'] = dose
        seed = 2026111441 if kind=='f2' else 2026111601
        rejected = []
        while True:
            if seed in used:
                rejected.append({'seed':seed,'reason':'used on a ref or earlier kit in this build'})
                seed += 1; continue
            args = ['gen-legs','--campaign-id',name,
                    '--master-seed',seed,'--n-legs',12,'--bands',','.join(kit['seed_law']['bands']),
                    '--decode-tokens',dose]
            if kind=='f2': args += ['--law',kit['seed_law']['method'],'--prompt-tokens','256,2000,19458','--g0-shapes','own']
            else: args += ['--prefill-tokens',19458]
            generated = cli(repo,'cadence_queue.py',*args)
            layout = [[x.get('prefill_tokens',19458) for x in generated['legs'][i:i+3]] for i in range(0,12,3)]
            if kind=='hp' or all({r.index(size) for r in layout}=={0,1,2} for size in (256,2000,19458)):
                break
            rejected.append({'seed':seed,'reason':'not every prompt size in every position'})
            seed += 1
        used.add(seed); kit['seed_law']=generated['seed_law']; kit['legs']=generated['legs']
        assert kit['frozen']==base['frozen']
        folder = HERE / ('hp-02' if kind=='hp' else name)
        path = folder / (name + ('.v1.1.json' if kind=='f2' else '.json'))
        write(path,kit)
        record = {'name':name,'path':str(path.relative_to(HERE)),'pin':kit['frozen']['commit'],
                  'source':F2_SOURCE if kind=='f2' else git('rev-parse',HP_SOURCE).strip(),
                  'source_sha256':hashlib.sha256(git('show',(F2_SOURCE if kind=='f2' else HP_SOURCE)+
                    ':docs/process/cadence/kits/'+('f2-inst-01.v1.1.json' if kind=='f2' else 'cl-hp-01.json')).encode()).hexdigest(),
                  'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'decode':dose,
                  'master_seed':seed,'rejected_seeds':rejected,'layout':layout,
                  'delta':differences(base,kit),'validate':[],'plans':[],'mocks':[]}
        for arg in ('02:00-02:35','13:14-13:15'):
            record['validate'].append(cli(repo,'cadence_queue.py','validate-kit',path,'--repo',repo,'--batch-window',arg))
        rosters = [list(range(i,i+3)) for i in (1,4,7,10)] if kind=='f2' else [list(range(1,4)),list(range(4,8)),list(range(8,13))]
        with tempfile.TemporaryDirectory(prefix='jw-rl174-synthetic-') as temp:
            for n, ids in enumerate(rosters,1):
                legs = ','.join(f'L{i:03d}' for i in ids)
                for hms,arg in [('00:30:00','13:14-13:15'),('13:15:00','02:00-02:35')]:
                    epoch=int(dt.datetime.fromisoformat('2026-11-19T'+hms).replace(tzinfo=ZoneInfo('America/Los_Angeles')).timestamp())
                    p=cli(repo,'cadence_legs_runner.py','plan','--kit',path,'--legs',legs,
                          '--t0',epoch,'--batch-window',arg)
                    assert p['blackout_clear'] is True
                    record['plans'].append({'piece':n,'roster':legs,'argument':arg,'plan':p})
                out=Path(temp)/f'{name}-{n}'
                m=cli(repo,'cadence_legs_runner.py','mock','--kit',path,'--legs',legs,
                      '--t0-local','2026-11-19T13:15:00','--batch-window','02:00-02:35','--output',out)
                assert m['rc']==0 and m['legs']==len(ids) and not m['stops'],m
                record['mocks'].append({'piece':n,'output':m,'qualification':'SYNTHETIC; streams not opened'})
        report['kits'].append(record)
        write(HERE/'evidence'/'kit-build.json',report)
        print(name,'seed',seed,'decode',dose,'validate/plan/mock PASS',record['sha256'])

if __name__=='__main__': main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
