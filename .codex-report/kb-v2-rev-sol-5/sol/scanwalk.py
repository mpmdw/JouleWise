import copy,json,sys,subprocess,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;R=Path('/workspace/JouleWise');sys.path.insert(0,str(R))
from scripts import bytes_stream_test as p
base=json.loads((P/'opus-run/scan_worked5_floor/scan.json').read_text())
keys='bytes_per_read repeats start_ns end_ns clock clock_resolution_s clock_tick_num_ns clock_tick_den clock_tick_source'.split()
fails=[];n=0
for i in range(len(base)):
 for key in keys:
  for mode in ('delete','null','type','nan'):
   d=copy.deepcopy(base)
   if mode=='delete':del d[i][key]
   else:d[i][key]={'null':None,'type':{},'nan':float('nan')}[mode]
   try:
    o=p.knee_scan(d)
    assert o['status']=='knee not found' and len(o['receipts'])==66
    # A tick-source field corruption must refuse rather than pick an arm.
    assert key in o['reason'],o['reason']
   except Exception as e:fails.append((i,key,mode,str(e)))
   n+=1
# All 66 call positions independently through the real CLI, plus non-Mac
# timebase branch: its tick numerator/denominator are intentionally unused.
for i in range(66):
 d=copy.deepcopy(base);d[i]['clock_tick_den']=None
 with tempfile.TemporaryDirectory() as td:
  f=Path(td)/'scan.json';f.write_text(json.dumps(d))
  c=subprocess.run([sys.executable,'-B',str(R/'scripts/bytes_stream_test.py'),'scan',str(f)],capture_output=True,text=True)
 assert c.returncode==0,c.stderr
 o=json.loads(c.stdout);assert len(o['receipts'])==66 and 'clock_tick_den' in o['reason']
print('scan leaf faults',n,'failures',fails,'real scan CLI positions 66 PASS')
