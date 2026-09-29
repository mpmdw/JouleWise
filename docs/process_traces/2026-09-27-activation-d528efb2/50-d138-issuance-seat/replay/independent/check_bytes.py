import ast, difflib, hashlib, json, subprocess, sys
from pathlib import Path
R=Path.cwd(); O=Path('/tmp/d138-replay-d528efb2/independent'); sys.path.insert(0,str(R))
C=R/'docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json'
I=R/'configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json'
from joulewise.calibration_bracketing import ISSUED_ACCEPTANCE_REGISTRY
craw=C.read_text(); iraw=I.read_text(); c=json.loads(craw); i=json.loads(iraw)
sha=lambda b:hashlib.sha256(b).hexdigest()
for p in [C,I]:
 assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(R))])
 print(p.name,sha(p.read_bytes()))
assert sha(I.read_bytes())==ISSUED_ACCEPTANCE_REGISTRY[i['acceptance_id']]['file_sha256']
print('i committed bytes and registry pin PASS')
# Independently parse source spans, retaining whitespace and numeric spellings.
def spans(s):
 d=json.JSONDecoder(); out={}
 def ws(pos):
  while pos<len(s) and s[pos].isspace(): pos+=1
  return pos
 def walk(pos,path):
  pos=ws(pos); start=pos
  if s[pos]=='{':
   pos=ws(pos+1)
   while s[pos]!='}':
    key,end=d.raw_decode(s,pos); pos=ws(end); assert s[pos]==':'
    pos=walk(pos+1,path+(key,)); pos=ws(pos)
    if s[pos]==',':pos=ws(pos+1)
    else:break
   assert s[pos]=='}'; pos+=1
  elif s[pos]=='[':
   pos=ws(pos+1); n=0
   while s[pos]!=']':
    pos=walk(pos,path+(n,)); n+=1; pos=ws(pos)
    if s[pos]==',':pos=ws(pos+1)
    else:break
   assert s[pos]==']';pos+=1
  else: _,pos=d.raw_decode(s,pos)
  out[path]=(start,pos);return pos
 assert ws(walk(0,()))==len(s)
 return out
cs=spans(craw); iss=spans(iraw)
protected=[(k,) for k in ('schema_version','acceptance_id','decision_ids','ledger_cutoff','identity_epoch','prospective_rederivation','derivation_corpus','prior_observation_set','decimal_derivation','registered_generation_row','derivation_input_sha256')]+[('backfill_candidate','candidate_inventory')]+[('derivation_notes',k) for k in c['derivation_notes']]
def value(a,path):
 for k in path:a=a[k]
 return a
for p in protected:
 assert value(c,p)==value(i,p),p
 assert craw[slice(*cs[p])]==iraw[slice(*iss[p])],p
 print('protected','.'.join(p),'parsed and source text IDENTICAL')
assert list(i['derivation_notes'])==list(c['derivation_notes'])+['network_time_provenance','issuance_record']
assert list(i)==[k for k in c if k!='candidate_not_issued']
common=[('artifact_role',),('issuance',),('derivation_sha256',)]+[('backfill_candidate',k) for k in ('status','production_issuance_blocked','required_verification')]
def allowed(s,sp,paths,last):
 lines=set()
 for p in paths:
  a,b=sp[p];lines.update(range(s.count('\n',0,a),s.count('\n',0,b-1)+1))
 lines.add(s.count('\n',0,sp[last][1]-1))
 return lines
last=('derivation_notes',next(reversed(c['derivation_notes'])))
ca=allowed(craw,cs,common+[('candidate_not_issued',)],last)
ia=allowed(iraw,iss,common+[('derivation_notes','network_time_provenance'),('derivation_notes','issuance_record')],last)
cl=craw.splitlines(True); il=iraw.splitlines(True); changed=[]
for op,a,b,x,y in difflib.SequenceMatcher(None,cl,il,autojunk=False).get_opcodes():
 if op=='equal':continue
 assert set(range(a,b))<=ca,(op,'candidate',a,b)
 assert set(range(x,y))<=ia,(op,'issued',x,y)
 changed.append([op,a+1,b,x+1,y])
(O/'candidate-issued.diff').write_text(''.join(difflib.unified_diff(cl,il,fromfile=str(C),tofile=str(I))))
print('ii PASS protected_paths=',len(protected),'diff_operations=',json.dumps(changed))
# Full seal and input seal, independently constructing the published recipes.
for name,a in [('candidate',c),('issued',i)]:
 full=sha(json.dumps({k:v for k,v in a.items() if k!='derivation_sha256'},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
 assert full==a['derivation_sha256']
 d=a['decimal_derivation'];row=a['registered_generation_row']
 inp={k:a[k] for k in ('acceptance_id','identity_epoch')}
 inp['ledger_cutoff']={k:a['ledger_cutoff'][k] for k in ('sequence','head_digest','ledger_schema')}
 inp['corpus_member_values']=[[m['member_id'],m['b_fiducial_s']] for m in a['derivation_corpus']['members']]
 inp.update({k:d[k] for k in ('source_statistics','rounding','two_draw_prediction_derivation','quantile_proof','ratified_operatives')})
 inp.update({k:row[k] for k in ('screen_rule','predecessor_acceptance_id','predecessor_ceiling_s','d125_ruling')})
 dig=sha(json.dumps(inp,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode())
 assert dig==a['derivation_input_sha256'];print(name,'whole seal',full,'input seal',dig)
expected_prefixes=['386e8254','b583f35a','70f47086','7b9c0d28']; seen=[]
for p,want in c['prospective_rederivation']['estimator_code_sha256'].items():
 got=sha((R/p).read_bytes());assert got==want;assert got[:8] in expected_prefixes;seen.append(got[:8]);print('estimator',p,got)
assert sorted(seen)==sorted(expected_prefixes)
capfile=R/'joulewise/powermetrics_fiducial.py'
cap=[n.value.value for n in ast.walk(ast.parse(capfile.read_text())) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DETECTION_PROJECTION_CELL_BUDGET' for t in n.targets)]
assert cap==[165000];print('DETECTION_PROJECTION_CELL_BUDGET',cap[0])
for commit in ['bda7ffe0','aeea07b6','ea10e3c8','5135c1d2']:
 rc=subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD']).returncode;assert rc==1;print('not_ancestor',commit,'exit',rc)
changed=subprocess.check_output(['git','diff','--name-only','e7c8bcc6...HEAD'],text=True).splitlines()
assert not set(changed)&set(c['prospective_rederivation']['estimator_code_sha256']);print('estimator diff intersection=[]')
print('BYTE AND BINDING CHECKS PASS')
