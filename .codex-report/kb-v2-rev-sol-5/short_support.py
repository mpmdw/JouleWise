"""A short C3 idle collection is an invalid support prerequisite, not valid new data."""
import sys,json,subprocess,importlib.util
from pathlib import Path
from copy import deepcopy
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
sys.argv=['leafwalk',str(ROOT),str(R/'e2e-positive'),str(R/'unused.json')]
s=importlib.util.spec_from_file_location('lw',R/'opus/leafwalk.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def cli(d,label):
 f=R/(label+'.json');f.write_text(json.dumps(d));c=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/bytes_stream_test.py'),'read',str(f)],capture_output=True,text=True)
 assert c.returncode==0,c.stderr
 o=json.loads(c.stdout);(R/(label+'-output.json')).write_text(c.stdout);return o
for full in (False,True,'jitter'):
 d=json.loads((R/'e2e-positive/input_A_knee_found.json').read_text()) if full else deepcopy(m.BASE)
 label='jitter' if full=='jitter' else 'full' if full else 'thin'
 if full=='jitter':d['records'][2]['harvest']['energy_j']['rails']-=12  # ordinary synthetic C3 energy variation, not an acceptance bar
 base=cli(d,'short-base-'+label)
 assert all(v['class']=='RESOLVED' for v in base['boundaries'].values())
 for span in ('pre','post'):
  bad=deepcopy(d);rows=bad['records'][2]['harvest']['idle'][span]['rails'];bad['records'][2]['harvest']['idle'][span]['rails']=rows[1:2] if full else rows[:1]
  out=cli(bad,'short-'+label+'-'+span);b,v=base['boundaries']['rest'],out['boundaries']['rest']
  print(label,span,'calls',len(out['calls']),'class',v['class'],'rest halfwidth',b['halfwidth'],'->',v['halfwidth'],flush=True)
  print('  C3 dx',v['arms']['C3']['dx'],'reason',v.get('reason'),'native',out['calls'][2]['native_idle'][span]['rails'].get('reason'),flush=True)
  print('  printed',base['printed']['contrasts']['rest'],'->',out['printed']['contrasts']['rest'],flush=True)
