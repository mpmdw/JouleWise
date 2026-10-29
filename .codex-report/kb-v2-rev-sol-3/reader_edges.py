"""Additional F4 missing-input cases through the real disk-backed read CLI."""
import json,sys,subprocess,tempfile
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[2]
base=json.loads(Path(sys.argv[1]).read_text())
cases=[]
def case(name,change):
 data=deepcopy(base);change(data);cases.append((name,data))
case('meter edge missing reading',lambda d:d['records'][0]['harvest'].__setitem__('meter_edge_w',[None,86]))
case('battery edge missing reading',lambda d:d['records'][0]['harvest'].__setitem__('battery_edge_j',[0,None]))
case('meter edge readings empty',lambda d:d['records'][0]['harvest'].__setitem__('meter_edge_w',[]))
case('battery edge readings empty',lambda d:d['records'][0]['harvest'].__setitem__('battery_edge_j',[]))
case('idle pre object null',lambda d:d['records'][0]['harvest']['idle'].__setitem__('pre',None))
case('null receipt',lambda d:d['records'][0].__setitem__('receipt',None))
case('missing C1 receipt',lambda d:d['records'][1].pop('receipt'))
case('missing C1 repeat count',lambda d:d['records'][1]['receipt'].pop('repeats'))
for name,data in cases:
 with tempfile.TemporaryDirectory() as tmp:
  path=Path(tmp)/'input.json';path.write_text(json.dumps(data,allow_nan=False))
  r=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/bytes_stream_test.py'),'read',str(path)],capture_output=True,text=True)
 if r.returncode:print(name,'EXIT',r.returncode,'stdout_bytes',len(r.stdout),r.stderr.strip().splitlines()[-1])
 else:
  out=json.loads(r.stdout)
  print(name,'EXIT 0','dc',out['boundaries']['dc']['class'],'delta',out['boundaries']['dc'].get('delta'),
        'arms',list(out['boundaries']['dc'].get('arms',{})), 'first_dc_bound',out['calls'][0]['boundaries'].get('dc',{}).get('edge_bound_j'),
        'retained_other_calls',sum(bool(c['boundaries']) for c in out['calls']))
