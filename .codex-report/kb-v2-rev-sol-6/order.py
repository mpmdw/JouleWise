import sys,json,math,io,contextlib
from pathlib import Path
from copy import deepcopy
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import bytes_stream_test as p
D=Path(__file__).parent
base=json.loads((D/'fixture/input_A_knee_found.json').read_text())
for rec in base['records']:
 for span in ('pre','post'):
  start=rec['receipt']['idle_'+span+'_start_ns']; step=14_400_000_000
  for kind,rows in rec['harvest']['idle'][span].items():
   mean=math.fsum(r['power_w'] for r in rows)/len(rows)
   rec['harvest']['idle'][span][kind]=[dict({'stamp_ns':start+i*step} if kind in ('battery','meter') else {'start_ns':start+i*step,'end_ns':start+(i+1)*step},power_w=mean) for i in range(4)]
 rec['harvest']['battery_samples']=deepcopy(rec['harvest']['idle']['pre']['battery']+rec['harvest']['idle']['post']['battery'])
b=p.read_known_bytes(base['records'],base['scan']); n=0
file=D/'order-input.json'
def check(d,leaf,valid=False):
 global n
 file.write_text(json.dumps(d));out=io.StringIO()
 with contextlib.redirect_stdout(out): rc=p.main(['read',str(file)])
 assert rc in (0,None);r=json.loads(out.getvalue());assert len(r['calls'])==8
 assert r['input_records']==d['records']
 if not valid:
  assert leaf in json.dumps(r['reasons']),(leaf,r['reasons'])
  assert any(v['class']=='UNDETERMINED' for v in r['boundaries'].values())
  for k,v in r['boundaries'].items():
   if type(v.get('halfwidth')) in (int,float): assert v['halfwidth']>=b['boundaries'][k]['halfwidth']
 n+=1
keys=('idle_pre_start_ns','idle_pre_end_ns','start_ns','end_ns','idle_post_start_ns','idle_post_end_ns')
for i in range(8):
 for a,c in zip(keys,keys[1:]):
  for offset in (-1,0):
   d=deepcopy(base);d['records'][i]['receipt'][c]=d['records'][i]['receipt'][a]+offset
   check(d,c,valid=offset==0 and a!='start_ns')
 rows=base['records'][i]['harvest']['battery_samples']
 for j in range(1,len(rows)):
  d=deepcopy(base);d['records'][i]['harvest']['battery_samples'][j]['stamp_ns']=rows[j-1]['stamp_ns']-1
  check(d,'stamp_ns')
print('PASS receipt endpoint and battery poll ordering',n,'CLI main exit0 complete records no invalid shrink')
file.unlink()
