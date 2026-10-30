"""Check whether an exact integer level can escape the source validator."""
import hashlib, json, os, subprocess, sys, tempfile, types
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import bytes_thermal_lines as t
from tests.test_bytes_thermal_lines import TrustArchive
with tempfile.TemporaryDirectory() as tmp:
    a=TrustArchive(Path(tmp),'request-end-p1',True,False)
    rows=a.journal_rows()
    for row in rows:
        if row['values']['level']:
            row['values']['level']=10**1000
    a.write_journal(rows)
    for name, module in [('head',t)]:
        out=a.root/name
        result=subprocess.run([sys.executable,t.__file__,'request-end-p1',str(a.a),str(out)],capture_output=True,text=True)
        print(name,'exit',result.returncode,'record_exists',(out/'thermal_line.json').exists())
        print('\n'.join(result.stderr.splitlines()[-9:]))
    src=subprocess.check_output(['git','show','9615ea4a1:scripts/bytes_thermal_lines.py'],text=True)
    baseline=types.ModuleType('baseline'); baseline.__file__=t.__file__
    exec(compile(src,t.__file__,'exec'),baseline.__dict__)
    try: baseline.transform('request-end-p1',a.a,a.root/'baseline')
    except Exception as exc: print('baseline',type(exc).__name__,str(exc))
