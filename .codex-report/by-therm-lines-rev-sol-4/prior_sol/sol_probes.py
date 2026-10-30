"""Fast independent exclusion, boundary, refusal, opacity and linked-view probes."""
import sys, tempfile, json, csv, hashlib, io, contextlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import bytes_thermal_lines as t
from tests.b6.test_bytes_p2_thermal_window import thermal_journal, NS
from joulewise import bytes_analysis as ba
from unittest.mock import patch

def put(p,x):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x))
def codes(p): return json.loads((p/'derived/b6-acceptance.json').read_text())['excluding']
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def fixture(root, name, mode='request-end-p1', levels=(90,)):
 a=root/name; members=[{'run_id':r,'kind':k,'units':[]} for r,k in [('dup','science'),('other','science'),('ref','external_input'),('absent','science'),('equal','science'),('edge','science'),('nonnumeric','science')]]
 ex=[{'scope':'member','run_id':r,'code':t.CODE} for r in ['dup','dup','other','ref','absent','equal','edge','nonnumeric']]
 ex.append({'scope':'member','run_id':'other','code':'thermal.powermetrics_pressure_elevated'})
 put(a/'derived/b6-acceptance.json',{'session_id':'s','counting':True,'excluding':ex,'energy':987654321.123456})
 put(a/'derived/roster.json',{'members':members})
 spans={r['run_id']:{'member':[20*NS,100*NS],'request':[40*NS,80*NS]} for r in members}
 spans.pop('absent'); spans['equal']['request']=[20*NS,100*NS]; spans['edge']['request'][1]=90*NS
 put(a/'withheld/spans.json',{'spans':spans})
 put(a/'derived/harvest-thresholds.json',{'values':{'thermal_unmeasured_gap_s':6}})
 journal=a/'sources/night-custody/hazards/monitor/thermal.jsonl'; journal.parent.mkdir(parents=True)
 j=thermal_journal(range(0,126,5),levels); j.dump(journal)
 with journal.open('a') as s: s.write('malformed\n')
 put(a/'withheld/member-assessments.json',{'members':{m['run_id']:{t.FIELD:{'excluded':True,'journal_available':True}} for m in members}})
 return a

def run():
 with tempfile.TemporaryDirectory() as tmp:
  root=Path(tmp); a=fixture(root,'a'); out=root/'out'
  # Guard lexical JSON measurement skipping; journal values deliberately only thermal.
  loads=json.loads
  def guarded(raw,*args,**kw):
   assert '987654321.123456' not in (raw.decode() if isinstance(raw,bytes) else raw)
   return loads(raw,*args,**kw)
  stdout=io.StringIO()
  with patch.object(t.json,'loads',side_effect=guarded),contextlib.redirect_stdout(stdout): t.main(['request-end-p1',str(a),str(out)])
  assert '987654321.123456' not in stdout.getvalue()
  result=json.loads(stdout.getvalue()); print('EDGE_CHANGES',[(x['run_id'],x['action']) for x in result['changes']])
  print('EDGE_REMAINING',[(x['run_id'],x['code']) for x in codes(out)])
  print('MALFORMED_NOTICE',result['notices'])
  assert [r['run_id'] for r in result['changes']]==['dup','other','nonnumeric']
  # Numeric-level filters: an unknown level is skipped, so boundary search reaches the next numeric read.
  b=fixture(root,'numeric'); jp=b/'sources/night-custody/hazards/monitor/thermal.jsonl'
  rows=[json.loads(x) for x in jp.read_text().splitlines()[:-1]]
  next(x for x in rows if x['finished']['monotonic_ns']==80*NS)['values']['level']='not-a-number'
  next(x for x in rows if x['finished']['monotonic_ns']==85*NS)['values']['level']=1
  jp.write_text(''.join(json.dumps(x)+'\n' for x in rows))
  nr=t.transform('request-end-p1',b,root/'numeric-out'); print('NONNUMERIC_NEXT_BOUNDARY',nr['changes'])
  assert not nr['changes']
  # Missing journal refuses even when there are no OS exclusions to remove.
  c=fixture(root,'missing'); (c/'sources/night-custody/hazards/monitor/thermal.jsonl').unlink()
  ac=json.loads((c/'derived/b6-acceptance.json').read_text()); ac['excluding']=[]; put(c/'derived/b6-acceptance.json',ac)
  for label,src,exp in [('missing-journal',c,None)]:
   try: t.transform('request-end-p1',src,root/label,exp)
   except ValueError as exc: print('REFUSAL',label,str(exc))
  exp=root/'export'; exp.mkdir(); csvp=exp/'s.runs.csv'
  with csvp.open('w',newline='') as s:
   wr=csv.writer(s); wr.writerow(['run_id','exclusion_codes','phase_decode_j']); wr.writerow(['ref',t.CODE,'987654321.123456'])
  try: t.transform('request-end-p1',a,root/'hidden-out',exp)
  except ValueError as exc: print('REFUSAL hidden',exc)
  csvp.write_text('run_id,exclusion_codes\nref,\n')
  try: t.transform('request-end-p1',a,root/'mismatch-out',exp)
  except ValueError as exc: print('REFUSAL mismatch',exc)
  # Hash coverage: unread linked files can change without changing any recorded input digest.
  source=a/'withheld/reductions/run.summary_metrics.rereduced.json'; put(source,{'phase_energy_j':{'decode':1}})
  linked=root/'linked'; record=t.transform('request-end-p1',a,linked)
  before=digest(linked/source.relative_to(a)); put(source,{'phase_energy_j':{'decode':2}})
  print('LINK_MUTATION',before!=digest(linked/source.relative_to(a)), 'all_recorded_hashes_match',all(digest(Path(p))==v for p,v in record['source_sha256'].items()))
  assert all(digest(Path(p))==v for p,v in record['source_sha256'].items())
  hp=fixture(root,'hull-special'); ap=hp/'withheld/member-assessments.json'; data=json.loads(ap.read_text())
  data['members']['dup'][t.FIELD]['excluded']=None
  data['members']['other'][t.FIELD]['journal_available']=False
  put(ap,data)
  hh=t.transform('hull-p2',hp,root/'hull-special-out')
  assert not hh['changes']  # others already carry OS, references untouched
  assert codes(hp)==codes(root/'hull-special-out')
  print('HULL_NULL_UNAVAILABLE_REFERENCE_DUPLICATES_UNCHANGED',hh['notices'])
  print('PROBES_PASS')
if __name__=='__main__': run()
