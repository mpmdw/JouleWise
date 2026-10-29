import copy,json,sys,subprocess
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent;R=Path('/workspace/JouleWise');sys.path.insert(0,str(R))
from scripts import bytes_stream_test as p
base=json.loads((P/'compact.json').read_text())
ref,ver=p.registered_stack()
for side in ('registered','harvested'):
 d=copy.deepcopy(base);r=copy.deepcopy(ref)
 if side=='registered':r['measurement_boundary_label']['rails']=['cpu_power','ane_power']
 else:d['records'][6]['harvest']['capture_stack']['measurement_boundary_label']['rails']=['cpu_power','ane_power']
 with patch.object(p,'registered_stack',return_value=(r,ver)):
  o=p.read_known_bytes(d['records'],d['scan'])
 assert o['boundaries']['gpu']['class']=='UNDETERMINED'
 assert 'gpu_power missing' in o['boundaries']['gpu']['reason']
 assert o['boundaries']['dc']['class']=='RESOLVED'
 print('GPU source absent on',side,'PASS')
# Native clock branch needs no Mac numerator or denominator.
scan=json.loads((P/'opus-run/scan_worked5_floor/scan.json').read_text())
for c in scan:
 c['clock_tick_source']='not applicable (non-macOS clock_getres)';c['clock_tick_num_ns']=None;c['clock_tick_den']=None
assert p.knee_scan(scan)['K']==2**26
print('non-Mac clock branch PASS')
# Semantic registry diff, all metadata/targets unchanged.
a=json.loads(subprocess.check_output(['git','show','977a5d2df:configs/pins/registry.json']))
b=json.loads((R/'configs/pins/registry.json').read_text())
changes=[]
for x,y in zip(a['files'],b['files']):
 assert x['path']==y['path']
 for u,v in zip(x['rows'],y['rows']):
  if u!=v:changes.append((x['path'],u[0],b['targets'][v[2]]))
assert len(changes)==4
for x in changes:print('registry row',x)
for x,y in zip(a['files'],b['files']):
 for u,v in zip(x['rows'],y['rows']):
  if u!=v:u[:]=v
assert a==b
print('registry exactly four rows; all other content bit-identical PASS')
