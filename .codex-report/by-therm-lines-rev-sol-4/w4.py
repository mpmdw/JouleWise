"""W4 named faults in both directions, including invariant original-code states."""
import hashlib,json,sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts import bytes_thermal_lines as t
from tests.test_bytes_thermal_lines import RecordedFaultTests
for mode in t.LABELS:
 for fault in ('excluding-null','missing-code','missing-run','nonutf8','missing-session'):
  f=RecordedFaultTests();f.setUp()
  try:
   f.put('sources/repo/plan_tree.json',{'bytes_pass':2 if mode=='hull-p2' else 1})
   f.put('withheld/member-assessments.json',{'members':{r:{t.FIELD:{'excluded':False,'journal_available':True}} for r in ('a','b')}})
   if fault=='excluding-null':f.put('derived/b6-acceptance.json',{'session_id':'s','excluding':None})
   elif fault=='missing-code':f.put('derived/b6-acceptance.json',{'session_id':'s','excluding':[{'scope':'member','run_id':'a'}]})
   elif fault=='missing-run':f.put('derived/roster.json',{'members':[{'kind':'science','units':[]},{'run_id':'b','kind':'science','units':[]}]})
   elif fault=='missing-session':f.put('derived/b6-acceptance.json',{'excluding':[{'scope':'member','run_id':'a','code':t.CODE}]})
   e=f.root/'e';e.mkdir();(e/'s.runs.csv').write_bytes(b'run_id,exclusion_codes\na,\xff\n' if fault=='nonutf8' else ('run_id,exclusion_codes\na,'+t.CODE+'\nb,\n').encode())
   def snapshot():return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in f.archive.rglob('*') if p.is_file()}
   before=snapshot();o=f.root/'o';args=[sys.executable,t.__file__,mode,str(f.archive),str(o)]
   if fault in ('nonutf8','missing-session'):args+=['--export',str(e)]
   p=subprocess.run(args,capture_output=True,text=True);assert p.returncode==0,p.stderr
   r=json.loads(p.stdout);statuses={x['run_id']:x['status'] for x in r['member_statuses']}
   for run,status in statuses.items():assert status.startswith('not defined (') if fault!='missing-code' or run=='a' else status in ('evaluated','equals registered line'),statuses
   assert not r['equals_registered_line'];assert before==snapshot()
   print('W4',mode,fault,p.returncode,statuses,'SOURCE_UNCHANGED',True,flush=True)
  finally:f.doCleanups()
