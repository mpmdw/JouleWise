"""Independent data-driven walk; no builder schemas or builder walk imported.
Source: disk receipts made by real stream() in sol3/adapted/e2e.py.
Compact only native support (four 14.4 s intervals); all eight calls retained.
"""
import copy,json,sys,subprocess,concurrent.futures, tempfile
from pathlib import Path
ROOT=Path('/workspace/JouleWise'); OUT=Path(__file__).resolve().parent
base=json.loads((OUT/'e2e/input_A_knee_found.json').read_text())
for rec in base['records']:
 h=rec['harvest'];h['meter_gaps']=[{'span':'stream','missing_samples':1},{'span':'post','missing_samples':2}]
 for side in ('pre','post'):
  for stream,rows in h['idle'][side].items():
   mean=sum(r['power_w'] for r in rows)/len(rows);start=rec['receipt']['idle_'+side+'_start_ns']
   h['idle'][side][stream]=[dict({'stamp_ns':start+i*14_400_000_000} if stream in ('meter','battery') else {'start_ns':start+i*14_400_000_000,'end_ns':start+(i+1)*14_400_000_000},power_w=mean) for i in range(4)]
 h['battery_samples']=copy.deepcopy(h['idle']['pre']['battery']+h['idle']['post']['battery'])
# These are the input fields used by the reader, from direct code-path reading.
rkeys='start_ns end_ns idle_pre_start_ns idle_pre_end_ns idle_post_start_ns idle_post_end_ns bytes_per_read repeats settle_s stack'.split()
hkeys='capture_stack energy_j idle battery_samples meter_gaps adapter_max_w adapter_source battery_source tau_s r_max_s anchor_shift_j meter_edge_w battery_edge_j'.split()
stackkeys='os_version hardware_unit runtime_version kernel_library python packages'.split()
def walk(x,path):
 if isinstance(x,dict):
  for k,v in x.items(): yield from walk(v,path+(k,))
 elif isinstance(x,list):
  for i,v in enumerate(x): yield from walk(v,path+(i,))
 else: yield path,x
paths=[]
for i,rec in enumerate(base['records']):
 for k in rkeys:
  v=rec['receipt'][k]
  if k=='stack':v={s:v[s] for s in stackkeys}
  paths.extend(walk(v,('records',i,'receipt',k)))
 for k in hkeys:paths.extend(walk(rec['harvest'][k],('records',i,'harvest',k)))
for k in ('K','B','Bc1','Bc3','Bc2'):paths.append((('scan',k),base['scan'][k]))

def run(data):
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'in.json';p.write_text(json.dumps(data))
  cp=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/bytes_stream_test.py'),'read',str(p)],capture_output=True,text=True)
  if cp.returncode:return None,cp.stderr.strip().splitlines()[-1]
  return json.loads(cp.stdout),None
baseline,err=run(base);assert not err,err
(OUT/'compact.json').write_text(json.dumps(base))

def trial(item):
 path,value,mode=item;d=copy.deepcopy(base);p=d
 for k in path[:-1]:p=p[k]
 k=path[-1]
 if mode=='delete':del p[k]
 elif mode=='null':p[k]=None
 elif mode=='type':p[k]={}
 else:p[k]=float('nan')
 o,err=run(d)
 if err:return str(path),mode,err
 failures=[]
 if len(o['calls'])!=8:failures.append('lost record')
 # Deleting one rail label can leave a valid alternative rail set; comparison
 # still invalidates rails/rest. Other mutations must name the missing leaf.
 if not any(v['class']=='UNDETERMINED' for v in o['boundaries'].values()):failures.append('no UNDETERMINED')
 if mode!='delete' or not isinstance(k,int):
  leaf=next(str(k) for k in reversed(path) if isinstance(k,str))
  if not any(leaf in r for r in o['reasons']):failures.append('no leaf reason '+leaf)
 for b,v in o['boundaries'].items():
  w=v.get('halfwidth')
  if type(w) in (int,float) and w<baseline['boundaries'][b]['halfwidth']:failures.append('shrunk '+b)
 for a,b in zip(o['calls'],baseline['calls']):
  for beta,row in a['boundaries'].items():
   for key in ('bound_j','edge_bound_j','baseline_bound_j'):
    w=row.get(key)
    if type(w) in (int,float) and w<b['boundaries'][beta][key]:failures.append('shrunk call '+beta+'.'+key)
 return (str(path),mode,failures) if failures else None
jobs=[(p,v,m) for p,v in paths for m in (['delete','null','type','nan'] if type(v) in (int,float) else ['delete','null','type'])]
print('independent leaves',len(paths),'CLI faults',len(jobs),flush=True)
fails=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for n,res in enumerate(pool.map(trial,jobs),1):
  if res:fails.append(res);print('FAIL',res,flush=True)
  if n%400==0:print('completed',n,flush=True)
print('TOTAL',len(jobs),'FAILURES',len(fails),flush=True)
# Every lost position: dropped, empty object, null receipt, missing N.
for i in range(8):
 for mode in ('drop','empty','receipt','N'):
  d=copy.deepcopy(base)
  if mode=='drop':del d['records'][i]
  elif mode=='empty':d['records'][i]={}
  elif mode=='receipt':d['records'][i]['receipt']=None
  else:del d['records'][i]['receipt']['repeats']
  o,e=run(d);assert not e,(i,mode,e)
  lost=('S','C1','C3','C2','C2','C3','C1','S')[i]
  for beta,v in o['boundaries'].items():
   for arm,a in v['arms'].items():assert ('x' in a)==(arm!=lost),(i,mode,beta,arm)
print('lost call positions: 32 PASS')
