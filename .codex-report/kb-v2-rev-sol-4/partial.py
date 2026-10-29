import json,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;R=Path('/workspace/JouleWise')
d=json.loads((P/'compact.json').read_text());d['records'][2]={}
f=P/'lost_c3.json';f.write_text(json.dumps(d))
c=subprocess.run([sys.executable,'-B',str(R/'scripts/bytes_stream_test.py'),'read',str(f)],capture_output=True,text=True)
assert c.returncode==0,c.stderr
o=json.loads(c.stdout);v=o['boundaries']['rails'];arms=v['arms']
x1,x2,xs=(arms[a]['x'] for a in ('C1','C2','S'))
s=d['scan'];gc=(x2-x1)/(s['Bc2']-s['Bc1']);alpha=x1-gc*s['Bc1'];gd=(xs-alpha)/s['B']
print('lost C3 class',v['class'],'printed gamma_c',v.get('gamma_c'),'alpha',v.get('alpha'),'gamma_d',v.get('gamma_d'),'delta',v.get('delta'))
print('from retained complete arms: gamma_c',gc*1e9,'alpha',alpha,'gamma_d',gd*1e9,'delta',(gd-gc)*1e9)
