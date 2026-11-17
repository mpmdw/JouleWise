"""Synthetic verification only. Run from repository root; never launches or stages.
The original lint/test bytes are copied unchanged. Runtime time placeholders are
substituted by test_rl173_gates.py for each case, as designed by that test.
"""
from pathlib import Path
import os,re,sys,subprocess,shutil,time,json
REPO=Path.cwd().resolve()
BASE=REPO/'docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign'
OUT=BASE/'issue-dev05-1117'; DRAFT=BASE/'item-drafts-1115'
SCRATCH=REPO/'.desk-scratch/issue-dev05-1117'; TMP=REPO/'.desk-scratch/tmp'
PIN=Path('/Users/edr/code/jw-wt/desk-pin-2d347f721')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=PIN,text=True).strip()=='2d347f721552fe03bdd19f113e7bad7a7c24908e'
TMP.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,JW_B5_SYNTHETIC_ONLY='1',PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(TMP))
PY=sys.executable
results=[]
def run(argv,cwd,log):
 r=subprocess.run(list(map(str,argv)),cwd=cwd,env=env,text=True,capture_output=True)
 text='$ '+ ' '.join(map(str,argv))+'\nCWD '+str(cwd)+'\nJW_B5_SYNTHETIC_ONLY=1 TMPDIR='+str(TMP)+'\n'+r.stdout+r.stderr+'\nEXIT_CODE '+str(r.returncode)+'\n'
 (OUT/log).write_text(text)
 results.append(dict(log=log,exit_code=r.returncode,tail=r.stdout.splitlines()[-1:]));print(log,r.returncode,r.stdout.splitlines()[-1:] or r.stderr[-200:])
 return r
for sub in ('lint/tools','gates','fixtures','fully-filled'):(SCRATCH/sub).mkdir(parents=True,exist_ok=True)
shutil.copyfile(DRAFT/'tools/lint.py',SCRATCH/'lint/tools/lint.py')
shutil.copyfile(DRAFT/'tests/test_rl173_gates.py',SCRATCH/'gates/test_rl173_gates.py')
# All non-time issue placeholders are substituted before running the test.
# Its two literal time templates must be left for the unmodified test to vary.
now=int(time.time())
for f in sorted(OUT.glob('ITEM-*.md')):
 t=f.read_text()
 def fill(m):
  s=m.group()
  if s=="<LEAD FILLS: the issue time as an epoch, from `date +%s` at issue>": return str(now-100)
  if s=="<LEAD FILLS: line 7's watcher observation stamp + 86,400 s, as an epoch>": return str(now+3600)
  if 'YYYY-MM-DD' in s: return '2026-11-17 09:00:00 PST (SYNTHETIC TEST VALUE)'
  if 'heartbeat' in s: return 'SYNTHETIC TEST WATCHER stamp 0 pid 0 commit 000000000'
  return '999' # synthetic RUN_STATE numbers; never written to delivered items
 full=re.sub(r'<LEAD FILLS:[^>]*>',fill,t)
 assert '<LEAD FILLS:' not in full
 (SCRATCH/'lint'/f.name).write_text(full)
 (SCRATCH/'fully-filled'/f.name).write_text(full)
 gate=full.replace(f'ISSUED_EPOCH={now-100}',"ISSUED_EPOCH=<LEAD FILLS: the issue time as an epoch, from `date +%s` at issue>")
 if '.lineflag.' not in f.name:
  gate=gate.replace(f'WATCH_UNTIL_EPOCH={now+3600}',"WATCH_UNTIL_EPOCH=<LEAD FILLS: line 7's watcher observation stamp + 86,400 s, as an epoch>")
 (SCRATCH/'gates'/f.name).write_text(gate)
run([PY,'-B',SCRATCH/'lint/tools/lint.py'],REPO,'lint.log')
for n,camp,pred,roster in [('01','cl-dev-04','dev-04-s02','L007,L008,L009,L010,L011,L012'),('02','cl-dev-05','dev-05-s01','L001,L002,L003,L004,L005,L006')]:
 kit=SCRATCH/'fixtures'/f'{camp}.v1.1.json'
 kit.write_bytes(subprocess.check_output(['git','show',f'fecaf73f3:docs/process/cadence/kits/{kit.name}'],cwd=REPO))
 mock=SCRATCH/'fixtures'/f'mock-for-dev05-s{n}'
 if not mock.exists():
  r=run([PY,'-B','scripts/cadence_legs_runner.py','mock','--kit',kit,'--output',mock,'--legs',roster,'--t0-local','2026-11-16T00:30:00','--batch-window','13:14-13:15'],PIN,f'mock-dev05-s{n}.log')
  if r.returncode: raise SystemExit(r.returncode)
 for variant,suffix in [('A',''),('B','.lineflag')]:
  name=f'ITEM-dev05-s{n}{suffix}.md'
  run([PY,'-B',SCRATCH/'gates/test_rl173_gates.py',SCRATCH/'gates'/name,mock,camp,pred,roster],REPO,f'gates-harness-{variant}-dev05-s{n}.log')
  # Also honor the literal fully-prefilled-input request. This exposes the
  # original test's string-substitution coupling; preserve failures as evidence.
  run([PY,'-B',SCRATCH/'gates/test_rl173_gates.py',SCRATCH/'fully-filled'/name,mock,camp,pred,roster],REPO,f'gates-{variant}-dev05-s{n}.log')
(OUT/'verification-results.json').write_text(json.dumps(results,indent=2)+'\n')
# Return nonzero for any failed check, including the intentionally retained B
# stale-watcher incompatibility and fully-prefilled harness coupling.
raise SystemExit(1 if any(r['exit_code'] for r in results) else 0)
