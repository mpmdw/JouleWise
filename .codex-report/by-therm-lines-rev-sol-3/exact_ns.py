"""A one-ns request boundary above float's exact-integer range, no tolerance."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import bytes_thermal_lines as t
from tests.test_bytes_thermal_lines import RecordedFaultTests
f=RecordedFaultTests();f.setUp()
try:
 n=2**60;NS=10**9
 rows=[json.loads(x) for x in f.journal.read_text().splitlines()]
 for row in rows:
  old=row['finished']['monotonic_ns']
  row['values']['level']=int(old==85*NS)
  for key in ('started','finished'):
   row[key]['monotonic_ns']+=n
  if old==85*NS:row['finished']['monotonic_ns']=n+80*NS+1;row['started']['monotonic_ns']=n+80*NS+1
 f.journal.write_text(''.join(json.dumps(r)+'\n' for r in rows))
 f.put('derived/window_flags.json',{'hazards':{'thermal':{'continuous':{'journal':{'sha256':hashlib.sha256(f.journal.read_bytes()).hexdigest()}}}}})
 f.put('derived/roster.json',{'members':[{'run_id':'a','kind':'science','units':[]}]})
 for delta in (0,1):
  f.put('withheld/spans.json',{'spans':{'a':{'member':[n+20*NS,n+100*NS],'request':[n+40*NS,n+80*NS+delta]}}})
  r=t.transform('request-end-p1',f.archive,f.root/str(delta))
  got=[c['action'] for c in r['changes']]
  assert got==(['removed'] if delta==0 else [])
  print('EXACT_LARGE_INTEGER_NS',delta,got,r['equals_registered_line'])
finally:f.doCleanups()
