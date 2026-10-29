import json,copy,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=Path('/workspace/JouleWise')
base=json.loads((Path(sys.argv[1]) if len(sys.argv)>1 else P/'compact.json').read_text())
def run(name,d):
 f=P/(name+'.json');f.write_text(json.dumps(d))
 c=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/bytes_stream_test.py'),'read',str(f)],capture_output=True,text=True)
 if c.returncode:print(name,'EXIT',c.returncode,c.stderr.strip().splitlines()[-1],flush=True);return
 o=json.loads(c.stdout);print(name,'EXIT 0', {k:(v['class'],v.get('halfwidth')) for k,v in o['boundaries'].items()},o['reasons'][:2],flush=True)
for name,change in [
 ('reversed_idle',lambda d:d['records'][0]['harvest']['idle']['pre']['rails'][1].__setitem__('end_ns',d['records'][0]['harvest']['idle']['pre']['rails'][1]['start_ns']-1)),
 ('huge_integer',lambda d:d['records'][7]['receipt'].__setitem__('repeats',10**400)),
 ('huge_finite',lambda d:d['records'][7]['harvest'].__setitem__('r_max_s',1e308)),
 ('fractional_stamp',lambda d:d['records'][7]['receipt'].__setitem__('start_ns',d['records'][7]['receipt']['start_ns']+.5)),
 ('bad_clock',lambda d:d['records'][7]['receipt'].__setitem__('clock_resolution_s',None)),
 ('bad_scan_status',lambda d:d['scan'].__setitem__('status',None)),
 ]:
 if len(sys.argv)>2 and name!=sys.argv[2]:continue
 d=copy.deepcopy(base);change(d);run(name,d)
