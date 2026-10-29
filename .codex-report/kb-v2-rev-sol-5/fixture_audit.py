import sys,types,subprocess,math,json
from pathlib import Path
R=Path(__file__).resolve().parent; ROOT=R.parents[1];sys.path.insert(0,str(ROOT))
from scripts import bytes_stream_test as new
from tests import test_bytes_stream_test as nt

def load(name,src,file):
 m=types.ModuleType(name);m.__file__=str(file);sys.modules[name]=m;exec(compile(src,str(file),'exec'),m.__dict__);return m
old=load('oldreader',subprocess.check_output(['git','show','6847502b8:scripts/bytes_stream_test.py'],text=True),ROOT/'scripts/bytes_stream_test.py')
ot=load('oldtests',subprocess.check_output(['git','show','6847502b8:tests/test_bytes_stream_test.py'],text=True),ROOT/'tests/test_bytes_stream_test.py');ot.probe=old
ot.ReaderTests.setUpClass();nt.ReaderTests.setUpClass()
a,b=ot.ReaderTests,nt.ReaderTests
print('old worked',a.result['printed']['contrasts'],a.result['printed']['share'],flush=True)
print('new worked',b.result['printed']['contrasts'],b.result['printed']['share'],flush=True)
assert a.result['printed']['contrasts']==b.result['printed']['contrasts'];assert a.result['printed']['share']==b.result['printed']['share']
maxmean=maxvar=0
for ar,br in zip(a.records,b.records):
 for span in ('pre','post'):
  for k in ('rails','gpu','meter','battery'):
   x,y=ar['harvest']['idle'][span][k],br['harvest']['idle'][span][k]
   rs=ar['receipt'];st,en=(rs['idle_'+span+'_start_ns'],rs['idle_'+span+'_end_ns'])
   u,v=old.idle_statistics(x,st,en,k),new.idle_statistics(y,st,en,k)
   maxmean=max(maxmean,abs(u['mean_w']-v['mean_w']));maxvar=max(maxvar,abs(u['variance_w2']-v['variance_w2']))
   if k=='rails':assert min(r['power_w'] for r in y)>=0
print('fixture max mean/variance discrepancy',maxmean,maxvar,flush=True)
for beta in ('rails','dc','rest'):
 u,v=a.result['boundaries'][beta],b.result['boundaries'][beta]
 diff=max(abs(u[k]-v[k]) for k in ('delta','halfwidth'))
 print(beta,'max delta/width change',diff,flush=True);assert diff<=5.7e-6
# Four and six constant supports have same means, zero governed SE and bounds;
# lag-count changes are disclosed, so retain separate 8-row and full-cadence walks.
results=[]
for n in (6,4):
 d=json.loads(json.dumps(b.records));step=57_600_000_000//n
 for rec in d:
  r,h=rec['receipt'],rec['harvest']
  for sp in ('pre','post'):
   st=r['idle_'+sp+'_start_ns']
   for k,rows in h['idle'][sp].items():
    mean=sum(x['power_w'] for x in rows)/len(rows)
    h['idle'][sp][k]=[dict({'stamp_ns':st+i*step} if k in ('meter','battery') else {'start_ns':st+i*step,'end_ns':st+(i+1)*step},power_w=mean) for i in range(n)]
  h['battery_samples']=h['idle']['pre']['battery']+h['idle']['post']['battery']
 results.append(new.read_known_bytes(d,b.scan))
for beta in ('rails','dc','rest'):
 u,v=(x['boundaries'][beta] for x in results)
 print('6->4',beta,'delta difference',v['delta']-u['delta'],'width difference',v['halfwidth']-u['halfwidth'],flush=True)
 assert abs(v['delta']-u['delta'])<=5.7e-6;assert abs(v['halfwidth']-u['halfwidth'])<=5.7e-6
print('fixture audit PASS',flush=True)
