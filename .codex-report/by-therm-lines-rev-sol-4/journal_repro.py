"""Minimal matching-seal/unusable-journal reproduction; real CLI."""
import json,hashlib,sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tests.test_bytes_thermal_lines import RecordedFaultTests
from scripts import bytes_thermal_lines as t
for fault in ('valid','not-json','missing-level','wrong-level','empty'):
 f=RecordedFaultTests();f.setUp()
 try:
  f.put('derived/roster.json',{'members':[{'run_id':'a','kind':'science','units':[]}]})
  if fault=='not-json':f.journal.write_text('{bad\n')
  elif fault=='empty':f.journal.write_text('')
  elif fault!='valid':
   rows=[json.loads(x) for x in f.journal.read_text().splitlines()]
   for row in rows:
    if fault=='missing-level':row['values'].pop('level',None)
    else:row['values']['level']={}
   f.journal.write_text(''.join(json.dumps(x)+'\n' for x in rows))
  f.put('derived/window_flags.json',{'hazards':{'thermal':{'continuous':{'journal':{'sha256':hashlib.sha256(f.journal.read_bytes()).hexdigest()}}}}})
  o=f.root/'o';p=subprocess.run([sys.executable,t.__file__,'request-end-p1',str(f.archive),str(o)],capture_output=True,text=True)
  r=json.loads(p.stdout)
  print('SEALED_JOURNAL',fault,'exit',p.returncode,'status',r['member_statuses'][0]['status'],'restored',r['restored_members'],'codes',json.loads((o/'derived/b6-acceptance.json').read_text())['excluding'])
 finally:f.doCleanups()
