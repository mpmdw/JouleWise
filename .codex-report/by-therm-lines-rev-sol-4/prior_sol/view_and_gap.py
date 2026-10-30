"""Exact gap-invariance and view-drift checks; optional real archive argument."""
import sys,json,tempfile,hashlib,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import bytes_thermal_lines as t
from joulewise.b5 import harvest as h
from tests.b6.test_bytes_p2_thermal_window import thermal_journal,NS
from tests.test_bytes_thermal_lines import RecordedFaultTests
with tempfile.TemporaryDirectory() as d:
 for nz in ((),(70,),(110,)):
  p=Path(d)/'thermal.jsonl'; thermal_journal([0,20,70,85,110,125],nz).dump(p)
  readings,_=h.read_monitor_journal(p,'thermal')
  projections=[]; holes=[]
  for gap in (0,6,1000):
   flags=h.thermal_member_flags([20*NS,80*NS],readings,{'thermal_unmeasured_gap_s':gap})
   projections.append([row for row in flags if row[0]==t.CODE])
   holes.append(any(row[0]=='thermal.unmeasured' for row in flags))
  assert projections[0]==projections[1]==projections[2]
  assert holes==[True,True,False]
 print('REAL_GAPS_OS_PROJECTION_EXACT 3 variants x 3 gap thresholds OK')
f=RecordedFaultTests();f.setUp()
try:
 out=f.root/'view';t.transform('request-end-p1',f.archive,out)
 assert t.verify(out)==[]
 (out/'added.txt').write_text('opaque')
 (out/'withheld/spans.json').unlink()
 result=subprocess.run([sys.executable,'scripts/bytes_thermal_lines.py','verify',str(out)],capture_output=True,text=True)
 assert result.returncode==0
 assert result.stdout.splitlines()==['added.txt','withheld/spans.json']
 assert json.loads((out/'thermal_line.json').read_bytes())['records.thermal_view_changed'] is True
 print('ADDED_DELETED exit',result.returncode,'paths',result.stdout.splitlines(),'flag True')
finally:f.doCleanups()
if len(sys.argv)>1:
 from joulewise.b6.session import accept_archive
 root=Path(sys.argv[1]); source=next((root/'p1').rglob('derived/b6-acceptance.json')).parent.parent
 planpath=next((root/'p1').rglob('plan_tree.json'))
 # Normalize acceptance to this exact plan/registration invocation first.
 accept_archive(source,json.loads(planpath.read_bytes()),Path.cwd()/'configs/b6/registration',plan_path=planpath,replace_existing=True)
 with tempfile.TemporaryDirectory() as d:
  out=Path(d)/'view';t.transform('request-end-p1',source,out)
  before={r['path']:r for r in t.view_files(out)}
  accept_archive(source,json.loads(planpath.read_bytes()),Path.cwd()/'configs/b6/registration',plan_path=planpath,replace_existing=True)
  after={r['path']:r for r in t.view_files(out)}
  changed=t.verify(out)
  identical=[p for p in changed if before[p]['sha256']==after[p]['sha256'] and before[p]['size']==after[p]['size']]
  assert identical,changed
  assert all(before[p]['mtime_ns']!=after[p]['mtime_ns'] or before[p]['inode']!=after[p]['inode'] for p in identical)
  print('REAL_REACCEPT_BYTE_IDENTICAL_DETECTED',identical)
