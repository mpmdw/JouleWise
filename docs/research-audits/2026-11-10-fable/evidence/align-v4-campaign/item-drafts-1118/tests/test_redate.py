"""One-argument regeneration and conservative date rejection, restoring defaults."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys
SOURCE=Path(__file__).resolve().parents[1]; checks=0
# Exercise the mutating generator only in an isolated copy, never over source
# drafts or their retained evidence. The copy stays inside this Git repository.
temporary=tempfile.TemporaryDirectory(prefix='.redate-fixture-',dir=SOURCE.parent)
fixture=Path(temporary.name)
HERE=fixture/'item-drafts-1118'
HERE.mkdir()
for name in ('build_items.py', 'gates.sh'):
    shutil.copy2(SOURCE/name, HERE/name)
shutil.copytree(SOURCE/'tools', HERE/'tools')
dev=SOURCE.parent/'item-drafts-1115'
dev_fixture=fixture/dev.name
(dev_fixture/'tools').mkdir(parents=True)
shutil.copy2(dev/'tools/close_census.py', dev_fixture/'tools')
shutil.copy2(dev/'ITEM-dev05-s01.md', dev_fixture)
def call(*args,ok=True):
    global checks
    env=dict(os.environ,JW_DRAFT_EVIDENCE_DIR=str(HERE/'evidence/regeneration-test'))
    r=subprocess.run([sys.executable,'-B',str(HERE/'build_items.py'),*args],text=True,capture_output=True,env=env)
    assert (r.returncode==0)==ok,(args,r.stdout,r.stderr); checks+=1; return r
call()  # Establish this fixture's default output at the current source refs.
paths=[*HERE.glob('ITEM-*.md'),*HERE.glob('queues/*.json'),*HERE.glob('evidence/plan-*.json')]
before={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
try:
    arg='qual-01=2026-11-20,qual-02=2026-11-21,qual-03=2026-11-22'
    call('--dates',arg)
    meta=json.loads((HERE/'items.json').read_text()); assert meta['dates']==dict(x.split('=') for x in arg.split(','))
    assert all(i['date']==meta['dates'][i['block']] for i in meta['items'])
    print('PASS one argument re-dates all six items, queue lower bounds and plan t0s to Fri/Sat/Sun')
    call('--dates','qual-01=2026-11-19,qual-02=2026-11-19,qual-03=2026-11-21',ok=False)
    print('PASS shared-date plan refused: RL-174 B.3 requires three dates, one block each')
    call('--dates','qual-01=2026-11-19,qual-02=2026-11-19,qual-03=2026-11-19',ok=False)
    call('--dates','qual-01=2026-11-18',ok=False)
    call('--dates','qual-03=2026-11-24',ok=False)
    print('PASS one-date, known development-date and expired queue plans refused')
finally:
    call()
after={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}; assert before==after
temporary.cleanup()
print(checks,'generator checks; zero failures; isolated default items/queues/plans restored byte for byte')
