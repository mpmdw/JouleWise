"""Keep the entire export-path probe inside a temporary synthetic directory."""
import json, subprocess, sys, tempfile, types
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts import bytes_thermal_lines as t
from tests.test_bytes_thermal_lines import TrustArchive, ACC
with tempfile.TemporaryDirectory(prefix='sol5-path-') as tmp:
    root=Path(tmp)
    a=TrustArchive(root/'case/deep1/deep2','hull-p2',False,True)
    session='../../../escape'
    acc=json.loads(a.text(ACC)); acc['session_id']=session; a.put(ACC,acc)
    exp=a.root/'export'; exp.mkdir()
    (exp/(session+'.runs.csv')).resolve().write_text('run_id,exclusion_codes,excluded\nr,,False\n')
    store=a.a/'withheld/store.csv'; store.write_text('run_id,exclusion_codes,excluded\na,,False\n')
    (exp/(session+'.session.json')).resolve().write_text(json.dumps({'blinding':{'withheld':{'path':str(store)}}}))
    out=a.root/'out'
    escaped=(out/'export/withheld'/(session+'.withheld.csv')).resolve()
    assert escaped.is_relative_to(root) and not escaped.is_relative_to(out)
    escaped.write_text('SENTINEL: preserve this sibling file\n')
    try:
        record=t.transform('hull-p2',a.a,out,exp)
        print('transform returned',record['status'])
    except Exception as exc:
        print('transform raised',type(exc).__name__,str(exc))
    print('destination outside output',not escaped.is_relative_to(out))
    print('sibling sentinel preserved',escaped.read_text()=='SENTINEL: preserve this sibling file\n')
    print('sibling content',repr(escaped.read_text()))

    escaped.chmod(0o644)
    escaped.write_text('SENTINEL: preserve this sibling file\n')
    src=subprocess.check_output(['git','show','9615ea4a1:scripts/bytes_thermal_lines.py'],text=True)
    baseline=types.ModuleType('baseline'); baseline.__file__=t.__file__
    exec(compile(src,t.__file__,'exec'),baseline.__dict__)
    baseline.transform('hull-p2',a.a,a.root/'baseline-out',exp)
    print('baseline sibling sentinel preserved',escaped.read_text()=='SENTINEL: preserve this sibling file\n')
