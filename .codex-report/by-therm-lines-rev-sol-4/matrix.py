"""Independent CLI trust matrix; no production monkeypatches. Synthetic only."""
import hashlib,itertools,json,os,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts import bytes_thermal_lines as t
from tests.b6.test_bytes_p2_thermal_window import thermal_journal,NS

def put(a,p,v):
 q=a/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(v));return q

def cli(*args):return subprocess.run([sys.executable,t.__file__,*map(str,args)],capture_output=True,text=True)

COMMON=['trusted','missing-plan','missing-pass','pass-bool','pass-string','pass-bad-json','wrong-pass','roster-gap']
HULL=['absent','bad-json','missing-member','missing-field','excluded-int','excluded-list','excluded-null','available-missing','available-int','journal-unavailable','members-list']
REQUEST=['absent','bad-json','missing-member','missing-field','request-dict','span-float','span-bool','spans-list','journal-absent','journal-mismatch','seal-absent','seal-bad-json','seal-missing-field','seal-wrong-type','journal-bad-json','journal-missing-level','journal-wrong-level','journal-empty']
FAIL=[];COUNT=0
with tempfile.TemporaryDirectory() as tmp:
 for mode,present,agrees in itertools.product(t.LABELS,[False,True],[False,True]):
  for fault in [v for f in COMMON+(HULL if mode=='hull-p2' else REQUEST) for v in (f,'trusted')]:
   COUNT+=1;a=Path(tmp)/str(COUNT)/'a';o=a.parent/'o'
   want=present if agrees else not present
   put(a,'derived/roster.json',{'members':[{'run_id':'a','kind':'science','units':[]}]})
   ex=[{'scope':'member','run_id':'a','code':t.CODE}] if present else []
   put(a,'derived/b6-acceptance.json',{'session_id':'s','excluding':ex})
   plan=put(a,'sources/repo/plan_tree.json',{'bytes_pass':2 if mode=='hull-p2' else 1})
   ev=put(a,'withheld/member-assessments.json',{'members':{'a':{t.FIELD:{'excluded':want,'journal_available':True}}}}) if mode=='hull-p2' else put(a,'withheld/spans.json',{'spans':{'a':{'member':[20*NS,100*NS],'request':[40*NS,80*NS]}}})
   j=a/'sources/night-custody/hazards/monitor/thermal.jsonl';j.parent.mkdir(parents=True)
   thermal_journal(range(0,126,5),{60 if want else 90}).dump(j)
   def seal():return put(a,'derived/window_flags.json',{'hazards':{'thermal':{'continuous':{'journal':{'sha256':hashlib.sha256(j.read_bytes()).hexdigest()}}}}})
   s=seal()
   if fault=='missing-plan':plan.unlink()
   elif fault=='missing-pass':plan.write_text('{}')
   elif fault=='pass-bool':plan.write_text('{"bytes_pass":true}')
   elif fault=='pass-string':plan.write_text('{"bytes_pass":"2"}')
   elif fault=='pass-bad-json':plan.write_text('{bad')
   elif fault=='wrong-pass':plan.write_text(json.dumps({'bytes_pass':1 if mode=='hull-p2' else 2}))
   elif fault=='roster-gap':ev.write_text('{"members":{}}' if mode=='hull-p2' else '{"spans":{}}')
   elif fault=='absent':ev.unlink()
   elif fault=='bad-json':ev.write_text('{bad')
   elif fault=='missing-member':ev.write_text('{"members":{}}' if mode=='hull-p2' else '{"spans":{}}')
   elif mode=='hull-p2' and fault!='trusted' and fault in HULL:
    r={'excluded':want,'journal_available':True}
    if fault=='missing-field':r.pop('excluded')
    elif fault=='excluded-int':r['excluded']=int(want)
    elif fault=='excluded-list':r['excluded']=[]
    elif fault=='excluded-null':r['excluded']=None
    elif fault=='available-missing':r.pop('journal_available')
    elif fault=='available-int':r['journal_available']=1
    elif fault=='journal-unavailable':r['journal_available']=False
    ev.write_text(json.dumps({'members':[] if fault=='members-list' else {'a':{t.FIELD:r}}}))
   elif mode=='request-end-p1' and fault in REQUEST:
    spans={'a':{'member':[20*NS,100*NS],'request':[40*NS,80*NS]}}
    if fault=='missing-field':spans['a'].pop('request')
    elif fault=='request-dict':spans['a']['request']={}
    elif fault=='span-float':spans['a']['request'][1]=80.0*NS
    elif fault=='span-bool':spans['a']['request'][1]=True
    elif fault=='spans-list':spans=[]
    elif fault=='journal-absent':j.unlink()
    elif fault=='journal-mismatch':s.write_text(s.read_text().replace(hashlib.sha256(j.read_bytes()).hexdigest(),'0'*64))
    elif fault=='seal-absent':s.unlink()
    elif fault=='seal-bad-json':s.write_text('{bad')
    elif fault=='seal-missing-field':s.write_text('{}')
    elif fault=='seal-wrong-type':s.write_text(s.read_text().replace('"'+hashlib.sha256(j.read_bytes()).hexdigest()+'"','[]'))
    elif fault.startswith('journal-'):
     if fault=='journal-bad-json':j.write_text('{bad\n')
     elif fault=='journal-empty':j.write_text('')
     else:
      rows=[json.loads(x) for x in j.read_text().splitlines()]
      for row in rows:
       if fault=='journal-missing-level':row['values'].pop('level',None)
       else:row['values']['level']={}
      j.write_text(''.join(json.dumps(x)+'\n' for x in rows))
     seal() # digest alone must not turn unusable evidence into trusted evidence
    ev.write_text(json.dumps({'spans':spans}))
   p=cli(mode,a,o)
   if fault=='trusted' and mode=='request-end-p1' and want and not present:
    ok=p.returncode==2 and not o.exists();print('CONTROL_STOP',ok);continue
   mutable=present if mode=='request-end-p1' else not present
   undefined=fault!='trusted' and mutable
   changed=fault=='trusted' and mutable and not agrees
   try:
    r=json.loads(p.stdout);st=r['member_statuses'][0]['status'];codes=json.loads((o/'derived/b6-acceptance.json').read_text())['excluding']
    expected='evaluated' if changed else 'equals registered line'
    expected_codes={t.CODE} if (want if changed else present) else set()
    actual_codes={x['code'] for x in codes}
    ok=(p.returncode==0 and (st.startswith('not defined (') if undefined else st==expected)
        and r['equals_registered_line']==(not undefined and not changed)
        and actual_codes==expected_codes
        and r['dropped_members']==([{'run_id':'a','codes':[t.CODE]}] if expected_codes else []))
    result=(p.returncode,st,r['equals_registered_line'],[x['code'] for x in codes])
   except Exception:ok=False;result=(p.returncode,(p.stdout+p.stderr)[-240:])
   print('CELL',mode,present,agrees,fault,'PASS' if ok else 'FAIL',result,flush=True)
   if not ok:FAIL.append((mode,present,agrees,fault,result))
print('SUMMARY',COUNT,'cells',len(FAIL),'failures')
for f in FAIL:print('FAILURE',f)
