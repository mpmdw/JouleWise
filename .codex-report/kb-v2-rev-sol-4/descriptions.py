"""Description-only inputs: recursive JSON, timing, and session metadata."""
import json,copy,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;R=Path('/workspace/JouleWise')
base=json.loads((P/'compact.json').read_text());n=0
for position in (0,7):
 for field in ('gpu_state','thermal_spans','operative_timing_bound_s','hour_as_run_s'):
  for mode in ('absent','null','nan'):
   d=copy.deepcopy(base)
   # hour_as_run_s is explicitly read from the first call only.
   pos=0 if field=='hour_as_run_s' else position
   h=d['records'][pos]['harvest']
   if mode=='absent':h.pop(field,None)
   elif mode=='null':h[field]=None
   elif field in ('gpu_state','thermal_spans'):
    h[field]={'outer':[{'inner':[1,float('nan')]}]}
   else:h[field]=float('nan')
   with tempfile.TemporaryDirectory() as td:
    f=Path(td)/'in.json';f.write_text(json.dumps(d));c=subprocess.run([sys.executable,'-B',str(R/'scripts/bytes_stream_test.py'),'read',str(f)],capture_output=True,text=True)
   assert c.returncode==0,c.stderr
   o=json.loads(c.stdout);assert len(o['calls'])==8
   if field=='gpu_state':text=o['calls'][pos]['gpu_state']
   elif field=='thermal_spans':text=o['calls'][pos]['thermal']['spans']
   elif field=='operative_timing_bound_s':text=o['calls'][pos]['timing'][field]
   else:text=o[field]
   assert text.startswith('not defined ('),(field,mode,text)
   if mode=='nan':assert field in text,(field,text)
   n+=1
print('description-only CLI faults',n,'PASS; nested JSON lists and first/final call metadata covered')
