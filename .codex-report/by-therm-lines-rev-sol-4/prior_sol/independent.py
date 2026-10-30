"""Independent synthetic fault matrix; prints codes/statuses only."""
import copy, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import bytes_thermal_lines as t
from tests.test_bytes_thermal_lines import RecordedFaultTests
from tests.b6.test_bytes_p2_thermal_window import thermal_journal
SCRIPT=Path(t.__file__).resolve()
def cli(*args,env=None):
 return subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],text=True,capture_output=True,env=env)
def result(p):
 lines=(p.stdout+p.stderr).strip().splitlines();return (p.returncode,lines[-1] if lines else '')
def fixture():
 f=RecordedFaultTests();f.setUp();return f

def main():
 for mode in t.LABELS:
  for fault in ('absent','member-missing','field-missing','null','journal-unavailable','wrong-pass'):
   f=fixture()
   try:
    good={'excluded':False,'journal_available':True}
    data={'members':{r:{t.FIELD:dict(good)} for r in ('a','b')}}
    if fault=='member-missing':data['members'].pop('b')
    if fault=='field-missing':data['members']['b'][t.FIELD].pop('excluded')
    if fault=='null':
     for r in data['members']:data['members'][r][t.FIELD]['excluded']=None
    if fault=='journal-unavailable':
     for r in data['members']:data['members'][r][t.FIELD]['journal_available']=False
    if fault!='absent':f.put('withheld/member-assessments.json',data)
    if mode=='request-end-p1':f.journal.unlink()
    f.put('sources/repo/plan_tree.json',{'bytes_pass':(1 if mode=='hull-p2' else 2) if fault=='wrong-pass' else (2 if mode=='hull-p2' else 1)})
    r=t.transform(mode,f.archive,f.root/'out')
    print('DIRECTION',mode,fault,[m['status'] for m in r['member_statuses']],r['equals_registered_line'])
   finally:f.doCleanups()
 for seal in ('missing','mismatch','matching'):
  f=fixture()
  try:
   thermal_journal(range(0,126,5),{60}).dump(f.journal)
   flags=f.archive/'derived/window_flags.json'
   if seal=='missing':flags.unlink()
   else:f.put('derived/window_flags.json',{'hazards':{'thermal':{'continuous':{'journal':{'sha256':hashlib.sha256(f.journal.read_bytes()).hexdigest() if seal=='matching' else '0'*64}}}}})
   # a already excluded, b clean: only a's equality is epistemically uncertain.
   if True:
    f.put('derived/roster.json',{'members':[{'run_id':'a','kind':'science','units':[]}]})
   r=t.transform('request-end-p1',f.archive,f.root/'out')
   print('NONZERO_UNTRUSTED',seal,[(m['run_id'],m['status']) for m in r['member_statuses']],r['equals_registered_line'],r['changes'])
  finally:f.doCleanups()
 for damage in ('source-null','source-list','notice-null','notice-empty','missing-binding'):
  f=fixture()
  try:
   o=f.root/'out';t.transform('request-end-p1',f.archive,o)
   p=o/'thermal_line.json';r=json.loads(p.read_bytes())
   if damage=='source-null':r['source_sha256']=None
   if damage=='source-list':r['source_sha256']=[]
   if damage=='notice-null':r['notices']=[None]
   if damage=='notice-empty':r['notices']=[{}]
   if damage=='missing-binding':r.pop('view_manifest_sha256')
   p.chmod(0o644);p.write_text(json.dumps(r));c=cli('verify',o)
   print('DAMAGED_RECORD',damage,result(c),'flag',json.loads(p.read_bytes())['records.thermal_view_changed'])
  finally:f.doCleanups()
 for value in (0,1):
  f=fixture()
  try:
   f.put('withheld/member-assessments.json',{'members':{r:{t.FIELD:{'excluded':value,'journal_available':True}} for r in ('a','b')}})
   r=t.transform('hull-p2',f.archive,f.root/'out')
   print('INTEGER_EXCLUDED',value,[m['status'] for m in r['member_statuses']],r['equals_registered_line'],r['changes'])
  finally:f.doCleanups()
 # Actual outside-git loading, with imports supplied from the reviewed checkout.
 f=fixture()
 try:
  code=f.root/'standalone/scripts/bytes_thermal_lines.py';code.parent.mkdir(parents=True);code.write_bytes(SCRIPT.read_bytes())
  p=subprocess.run([sys.executable,str(code),'request-end-p1',str(f.archive),str(f.root/'outside')],capture_output=True,text=True)
  r=json.loads((f.root/'outside/thermal_line.json').read_bytes());print('OUTSIDE_GIT',p.returncode,r['producing_commit'],r['producing_tree_dirty'])
 finally:f.doCleanups()
if __name__=='__main__':main()
