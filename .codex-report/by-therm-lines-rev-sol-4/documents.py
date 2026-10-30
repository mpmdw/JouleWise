"""CLI cross product for unparsable documents whose selected field is intact."""
import itertools,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts import bytes_thermal_lines as t
from tests.test_bytes_thermal_lines import RecordedFaultTests
from tests.b6.test_bytes_p2_thermal_window import thermal_journal,NS
fails=[];count=0
for mode,present,agrees,fault in itertools.product(t.LABELS,(False,True),(False,True),('trailing-junk','truncated-root','invalid-sibling','plan-trailing-junk','plan-truncated-root')):
 for trusted in (False,True):
  count+=1;f=RecordedFaultTests();f.setUp()
  try:
   want=present if agrees else not present
   f.put('sources/repo/plan_tree.json',{'bytes_pass':2 if mode=='hull-p2' else 1})
   f.put('derived/roster.json',{'members':[{'run_id':'a','kind':'science','units':[]}]})
   f.put('derived/b6-acceptance.json',{'session_id':'s','excluding':[{'scope':'member','run_id':'a','code':t.CODE}] if present else []})
   f.put('withheld/member-assessments.json',{'members':{'a':{t.FIELD:{'excluded':want,'journal_available':True}}}})
   thermal_journal(range(0,126,5),{60 if want else 90}).dump(f.journal)
   import hashlib
   f.put('derived/window_flags.json',{'hazards':{'thermal':{'continuous':{'journal':{'sha256':hashlib.sha256(f.journal.read_bytes()).hexdigest()}}}}})
   path=f.archive/('sources/repo/plan_tree.json' if fault.startswith('plan-') else 'withheld/member-assessments.json' if mode=='hull-p2' else 'withheld/spans.json')
   raw=path.read_text()
   if not trusted:
    if 'trailing-junk' in fault:raw+='BROKEN'
    elif 'truncated-root' in fault:raw=raw[:-1]
    else:raw=raw[:-1]+',"extra": BROKEN}'
    path.write_text(raw)
    try:json.loads(raw)
    except ValueError:pass
    else:raise AssertionError('fault is not unparsable')
   o=f.root/'o';p=subprocess.run([sys.executable,t.__file__,mode,str(f.archive),str(o)],capture_output=True,text=True)
   if trusted and mode=='request-end-p1' and want and not present:
    assert p.returncode==2 and not o.exists();print('DOCUMENT_CONTROL_STOP',fault,True);continue
   if p.returncode!=0:
    row=(mode,present,agrees,fault,'trusted' if trusted else 'untrusted',p.returncode,p.stderr.strip())
    print('DOCUMENT FAIL',row,flush=True);fails.append(row);continue
   mutable=present if mode=='request-end-p1' else not present
   undef=not trusted and mutable;changed=trusted and mutable and not agrees
   r=json.loads(p.stdout);status=r['member_statuses'][0]['status'];codes={x['code'] for x in json.loads((o/'derived/b6-acceptance.json').read_text())['excluding']}
   expected_codes={t.CODE} if (want if changed else present) else set()
   ok=(p.returncode==0 and (status.startswith('not defined (') if undef else status==('evaluated' if changed else 'equals registered line')) and codes==expected_codes and r['equals_registered_line']==(not undef and not changed))
   row=(mode,present,agrees,fault,'trusted' if trusted else 'untrusted',p.returncode,status,r['equals_registered_line'],sorted(codes))
   print('DOCUMENT','PASS' if ok else 'FAIL',row,flush=True)
   if not ok:fails.append(row)
  finally:f.doCleanups()
print('SUMMARY_DOCUMENTS',count,'cells',len(fails),'failures')
