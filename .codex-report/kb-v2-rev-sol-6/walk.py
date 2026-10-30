"""Independent exhaustive compact numeric walk; run from review root with python3.13 -B."""
import sys,json,math,io,contextlib,traceback
from pathlib import Path
from copy import deepcopy
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import bytes_stream_test as p
D=Path(__file__).parent
base=json.loads((D/'fixture/input_A_knee_found.json').read_text())
for rec in base['records']:
 r,h=rec['receipt'],rec['harvest']
 for span in ('pre','post'):
  for kind,rows in h['idle'][span].items():
   mean=math.fsum(x['power_w'] for x in rows)/len(rows); start=r['idle_'+span+'_start_ns']; step=14_400_000_000
   h['idle'][span][kind]=[dict({'stamp_ns':start+i*step} if kind in ('meter','battery') else {'start_ns':start+i*step,'end_ns':start+(i+1)*step},power_w=mean) for i in range(4)]
 h['battery_samples']=deepcopy(h['idle']['pre']['battery']+h['idle']['post']['battery'])
 h['meter_gaps']=[{'span':'stream','missing_samples':1},{'span':'pre','missing_samples':1}]
def leaves(v,path=()):
 if isinstance(v,dict):
  for k,x in v.items(): yield from leaves(x,path+(k,))
 elif isinstance(v,list):
  for i,x in enumerate(v): yield from leaves(x,path+(i,))
 elif type(v) in (int,float): yield path,v
# Every numeric leaf, including informational/ignored fields and scan evidence.
paths=list(leaves(base)); baseline=p.read_known_bytes(base['records'],base['scan']); issues=[]; counts=Counter()
file=D/'walk-input.json'
def check(data,path,mode):
 leaf=next(str(k) for k in reversed(path) if isinstance(k,str))
 try:
  # Execute the real CLI entry point on serialized evidence; SystemExit is its status.
  file.write_text(json.dumps(data)); out=io.StringIO()
  with contextlib.redirect_stdout(out):
   rc=p.main(['read',str(file)])
  assert rc in (None,0),rc
  result=json.loads(out.getvalue()); assert len(result['calls'])==8
  assert result['input_records']==p.json_evidence(data['records'])
  counts['exit0_complete']+=1
  reasons=json.dumps(result['reasons'])
  widths={k:v.get('halfwidth') for k,v in result['boundaries'].items()}
  shrunk=[k for k,w in widths.items() if type(w) in (int,float) and w<baseline['boundaries'][k]['halfwidth']]
  if shrunk or (leaf not in reasons):
   issues.append({'path':path,'mode':mode,'shrunk':shrunk,'named':leaf in reasons,'classes':{k:v['class'] for k,v in result['boundaries'].items()},'reasons':result['reasons']})
 except Exception:
  issues.append({'path':path,'mode':mode,'crash':traceback.format_exc()}); counts['crash']+=1
 counts[mode]+=1
for path,v in paths:
 parent=base
 for k in path[:-1]: parent=parent[k]
 key=path[-1]
 for mode,value in [('deleted',None),('null',None),('wrong_type',{}),('non_finite',float('nan')),('wrong_length',[]),('huge_int',10**400),('huge_float',1e308),('negative',-abs(v)-1),('zero',0),('nan_string','NaN'),('inf',float('inf')),('minus_inf',float('-inf')),('bool',True)]:
  if mode=='deleted': del parent[key]
  else: parent[key]=value
  check(base,path,mode)
  if mode=='deleted' and isinstance(parent,list): parent.insert(key,v)
  else: parent[key]=v
 if counts['exit0_complete']%1000<13: print('progress',counts['exit0_complete'],flush=True)
# All interval and poll-order violations in every row, span and call.
for i,rec in enumerate(base['records']):
 for span in ('pre','post'):
  for kind,rows in rec['harvest']['idle'][span].items():
   for j,row in enumerate(rows):
    if 'end_ns' in row:
     for key,value,mode in [('end_ns',row['start_ns'],'empty_interval'),('end_ns',row['start_ns']-1,'reversed_interval')]+([('start_ns',rows[j-1]['end_ns']-1,'overlap'),('start_ns',rows[j-1]['start_ns'],'duplicate_start')] if j else []):
      old=row[key];row[key]=value;check(base,('records',i,'harvest','idle',span,kind,j,key),mode);row[key]=old
    elif j:
     old=row['stamp_ns'];row['stamp_ns']=rows[j-1]['stamp_ns']-1;check(base,('records',i,'harvest','idle',span,kind,j,'stamp_ns'),'poll_order');row['stamp_ns']=old
(D/'walk-issues.json').write_text(json.dumps(issues,indent=1))
print('NUMERIC_LEAVES',len(paths),'COUNTS',dict(counts),'ISSUES',len(issues),flush=True)
file.unlink()
