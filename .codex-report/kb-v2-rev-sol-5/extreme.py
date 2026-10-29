"""Residual finite-arithmetic record loss, beyond the repaired 10**400 case."""
import sys,json,subprocess,math
from pathlib import Path
R=Path(__file__).resolve().parent;ROOT=R.parents[1];sys.path.insert(0,str(ROOT))
from scripts import bytes_stream_test as p
for value in (1e308,10**308):
 d=json.loads((R/'sol/compact.json').read_text());d['records'][0]['harvest']['tau_s']=value
 f=R/('finite-tau-'+type(value).__name__+'.json');f.write_text(json.dumps(d));pr=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/bytes_stream_test.py'),'read',str(f)],capture_output=True,text=True)
 print('tau_s',type(value).__name__,'finite',math.isfinite(float(value)),'accessor error',p.input_value(value,p.NONNEG,'tau_s')[1],'EXIT',pr.returncode)
 print('\n'.join(pr.stderr.splitlines()[-4:]))
