import json,subprocess,sys
from pathlib import Path
D=Path(__file__).parent
base=json.loads((D/'fixture/input_A_knee_found.json').read_text())
base['records'][0]['harvest']['idle']['pre']['rails'][0]['power_w']=1e308
f=D/'label-overflow-input.json';f.write_text(json.dumps(base))
r=subprocess.run([sys.executable,'-B',str(D.parents[1]/'scripts/bytes_stream_test.py'),'read',str(f)],capture_output=True,text=True)
print('rc',r.returncode)
out=json.loads(r.stdout);print('calls',len(out['calls']),'input retained',out['input_records']==base['records'])
print('rails',out['boundaries']['rails']['class'],out['boundaries']['rails']['halfwidth'])
print('reasons',out['reasons'])
f.unlink()
