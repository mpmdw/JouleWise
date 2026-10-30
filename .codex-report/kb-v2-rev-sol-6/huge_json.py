"""Valid JSON numeric token exceeding CPython's default integer digit limit."""
import json,subprocess,sys
from pathlib import Path
D=Path(__file__).parent; root=D.parents[1]
d=json.loads((D/'fixture/input_A_knee_found.json').read_text())
d['records'][0]['harvest']['battery_edge_j'][0]='REVIEW_HUGE_INTEGER'
f=D/'huge-json-input.json'
f.write_text(json.dumps(d).replace('"REVIEW_HUGE_INTEGER"','1'+'0'*5000))
parsed=json.loads(f.read_text(),parse_int=str)
assert len(parsed['records'][0]['harvest']['battery_edge_j'][0])==5001
print('JSON grammar validated with parse_int=str')
r=subprocess.run([sys.executable,'-B',str(root/'scripts/bytes_stream_test.py'),'read',str(f)],capture_output=True,text=True)
print('valid JSON 5001-digit numeric battery_edge_j[0]; rc=',r.returncode,'stdout bytes=',len(r.stdout))
print('\n'.join(r.stderr.splitlines()[-9:]))
f.unlink()
