"""Disk-backed real read CLI variants on production-shaped, real stream receipts."""
from copy import deepcopy
from pathlib import Path
import json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts import bytes_stream_test as p
base=json.loads(Path(sys.argv[1]).read_text())
cases=[('baseline',deepcopy(base))]
def add(name,fn):
 d=deepcopy(base);fn(d);cases.append((name,d))
for field,value,gap in [('adapter_source','',True),('adapter_max_w',None,True),('battery_source',None,True),('r_max_s',None,False),('meter_edge_w',None,False),('battery_edge_j',None,False),('anchor_shift_j',None,False),('tau_s',None,False)]:
 def edit(d,field=field,value=value,gap=gap):
  d['records'][0]['harvest'][field]=value
  if gap:d['records'][0]['harvest']['meter_gaps']=[{'span':'stream','missing_samples':1}]
 add(field,edit)
for stream in ('rails','gpu','meter','battery'):
 add('integral_'+stream,lambda d,stream=stream:d['records'][0]['harvest']['energy_j'].pop(stream))
add('lost_call',lambda d:d['records'].pop())
add('duplicate',lambda d:d['records'][0]['harvest']['idle']['pre']['meter'][1].__setitem__('stamp_ns',d['records'][0]['harvest']['idle']['pre']['meter'][0]['stamp_ns']))
add('rails_boundary',lambda d:d['records'][0]['harvest']['capture_stack']['measurement_boundary_label'].__setitem__('rails',['cpu_power','gpu_power']))
for name,d in cases:
 with tempfile.TemporaryDirectory() as tmp:
  path=Path(tmp)/'input.json';path.write_text(json.dumps(d,allow_nan=False))
  proc=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/bytes_stream_test.py'),'read',str(path)],capture_output=True,text=True,check=True)
  r=json.loads(proc.stdout)
  print(name,{b:v['class'] for b,v in r['boundaries'].items()},r['reasons'],'contrasts',r['printed']['contrasts'])
  if name=='duplicate':print('duplicate stats', {k:r['calls'][0]['native_idle']['pre']['meter'][k] for k in ['sample_count','duplicate_stamp_count','native_interval_ns','variance_w2']})
print('zero width',p.format_interval(.1+.2,0))
v={'delta':0.,'halfwidth':.000996,**p.classify(0.,.000996,1/64)}
print('upper rounding',p.printed_record({'share':{'f':'unknown'},'stack_comparisons':[],'boundaries':{'rails':v}})['claim_lines']['rails'])
