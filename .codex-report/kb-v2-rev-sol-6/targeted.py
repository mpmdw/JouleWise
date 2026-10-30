import sys,json,subprocess,tempfile,math
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import bytes_stream_test as p
D=Path(__file__).parent
base=json.loads((D/'fixture/input_A_knee_found.json').read_text())
fmt=p.format_interval
seen=[]
def spy(v,w):
 assert math.isfinite(w) and w>0,(v,w)
 seen.append(w);return fmt(v,w)
def run(name,d):
 with patch.object(p,'format_interval',side_effect=spy): r=p.read_known_bytes(d['records'],d['scan'])
 assert len(r['calls'])==8
 print(name,{k:(v['class'],v.get('halfwidth'),v.get('reason')) for k,v in r['boundaries'].items()},flush=True)
 return r
# All-zero physical measurements and bounds; signed battery cancels meter exactly.
z=deepcopy(base)
for rec in z['records']:
 h=rec['harvest'];h['energy_j']={k:(-1 if k=='battery' else 1 if k=='meter' else 0) for k in p.NATIVE_INPUTS}
 h.update(anchor_shift_j=0,r_max_s=0,meter_edge_w=[0,0],battery_edge_j=[0,0])
 for span in ('pre','post'):
  for k,rows in h['idle'][span].items():
   for row in rows: row['power_w']=-1 if k=='battery' else 1 if k=='meter' else 0
r=run('zero_cancellation',z)
for k,v in r['boundaries'].items(): assert v['class']=='UNDETERMINED' and k in v['reason'] and 'halfwidth' in v['reason']
# Finite leaf-valid overflow of each class.
d=deepcopy(base)
for rec in d['records']: rec['harvest'].update(anchor_shift_j=1e308,meter_edge_w=[1e308,1e308])
r=run('nonfinite',d)
assert all(v['class']=='UNDETERMINED' and not isinstance(v['halfwidth'],(int,float)) for v in r['boundaries'].values())
# Descending cache sizes can produce negative computed halfwidths despite leaf-valid sizes.
d=deepcopy(base);d['scan']['Bc1'],d['scan']['Bc2']=d['scan']['Bc2'],d['scan']['Bc1']
for rec in d['records']:
 b=rec['receipt']['bytes_per_read']
 if b==base['scan']['Bc1']: rec['receipt']['bytes_per_read']=d['scan']['Bc1']
 elif b==base['scan']['Bc2']: rec['receipt']['bytes_per_read']=d['scan']['Bc2']
raw_reduce=p.reduce_boundary
raw_widths={}
def capture(c,s,b):
 v=raw_reduce(c,s,b);raw_widths[b]=v['halfwidth'];return v
with patch.object(p,'reduce_boundary',side_effect=capture):
 r=run('descending_cache',d)
assert all(type(w) in (int,float) and w<0 for w in raw_widths.values()),raw_widths
print('raw_negative_widths',raw_widths,flush=True)
# Valid zero individual measurements/bounds remain accepted.
for key in ('anchor_shift_j','r_max_s','meter_edge_w','battery_edge_j'):
 d=deepcopy(base)
 for rec in d['records']: rec['harvest'][key]=[0,0] if key.endswith('_w') or key=='battery_edge_j' else 0
 r=run('valid_zero_'+key,d);assert all(v['class']=='RESOLVED' for v in r['boundaries'].values())
assert fmt(0,0)=='0.00 ± 0.00'
for kind in ('rails','gpu'):
 for span in ('pre','post'):
  for mode in ('touching','overlap','duplicate'):
   d=deepcopy(base);rows=d['records'][1]['harvest']['idle'][span][kind]
   if mode=='overlap': rows[1]['start_ns']=rows[0]['end_ns']-1
   elif mode=='duplicate': rows[1]=deepcopy(rows[0])
   r=run(kind+'_'+span+'_'+mode,d)
   assert (r['boundaries'][kind]['class']=='RESOLVED')==(mode=='touching')
for status in ('knee found','knee not found','unknown'):
 d=deepcopy(base);d['scan']['status']=status;r=run('status_'+status,d)
 assert (r['boundaries']['rails']['class']=='RESOLVED')==(status=='knee found')
d=deepcopy(base)
for row in d['records'][0]['harvest']['idle']['pre']['gpu']: row['power_w']=0
r=run('valid_zero_gpu_measurement',d)
assert r['boundaries']['gpu']['class']=='RESOLVED'
print('PASS formatter calls all positive finite',len(seen),flush=True)
