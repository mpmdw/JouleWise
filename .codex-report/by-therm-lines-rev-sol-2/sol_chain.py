"""Independent synthetic executing review; run with Python 3.13 from repository root."""
import sys, os, json, tempfile, copy, hashlib, csv, contextlib, io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ['JW_B5_SYNTHETIC_ONLY']='1'
from unittest.mock import patch
from tests.b6 import test_bytes_p2_thermal_window as f
from tests import test_harvest_b5_window as w
from tests.b6.support import registration_dir
from joulewise.b6.session import accept_archive
from joulewise.b6.export_runs import export
from scripts import bytes_thermal_lines as t
from joulewise import bytes_analysis as ba
from joulewise.b5 import harvest as h

def put(p,v): p.write_text(json.dumps(v))
def get(p): return json.loads(p.read_bytes())
def small(root, pass_id, case='tail'):
    b=f.HarvestEntryTests(); b.root=root
    factory=w.Window
    with patch.object(w,'Window',side_effect=lambda *a,**kw: factory(*a,catalog_overrides=w.WindowTestCase.ISOLATE,**kw)):
        win=b.window(pass_id,name='small'+str(pass_id)+case)
    if case=='clean':
        jp=win.custody/'hazards/monitor/thermal.jsonl'
        rows=[json.loads(x) for x in jp.read_text().splitlines()]
        for row in rows: row['values']['level']=0
        jp.write_text(''.join(json.dumps(x)+'\n' for x in rows))
    b.harvest(win)
    # Verify the sealed stamps and thresholds equal the real harvest inputs.
    inputs=h.resolve_inputs(win.plan_path)
    assert get(win.archive/'derived/harvest-thresholds.json')['values']['thermal_unmeasured_gap_s']==inputs.thresholds['thermal_unmeasured_gap_s']
    spans=get(win.archive/'withheld/spans.json')['spans']; assessments=get(win.archive/'withheld/member-assessments.json')['members']
    assert all(spans[r]==m['spans'] for r,m in assessments.items())
    print('SEALED_INPUTS_EXACT',pass_id,case,flush=True)
    reg=registration_dir(root)
    result,evidence=accept_archive(win.archive,get(win.plan_path),reg)
    print('REAL_ACCEPTANCE',pass_id,result.verdict,result.counting,result.record['excluding'])
    out=root/('small-line'+str(pass_id)+case)
    r=t.transform('hull-p2' if pass_id==2 else 'request-end-p1',win.archive,out)
    print('REAL_CHAIN_CHANGES',pass_id,r['changes'])
    plan=get(win.plan_path)
    exported=export(win.archive,plan,reg,root/'keys',root/('export-'+str(pass_id)+case),non_claim=True,evidence=evidence,acceptance_record=result.record,pack_registration={'pack_id':w.PACK_ID})
    csv_out=root/('csv-line'+str(pass_id)+case)
    rr=t.transform('hull-p2' if pass_id==2 else 'request-end-p1',win.archive,csv_out,exported.csv_path.parent)
    assert rr['changes']==r['changes']
    rows=list(csv.DictReader(exported.csv_path.open()))
    model={'model':'mock-model','cell_ids':['b5t-abs','b5t-cmp'],'role':'fit','config_key':next(x['config_key'] for x in rows if x['role']=='science')}
    manifest={'synthetic':True,'models':[model],'sessions':[{'session_id':result.record['session_id'],'pass_id':pass_id}]}
    for stage,source in [('all',win.archive),('all',out),('blinded',exported.csv_path.parent),('blinded',csv_out/'export')]:
        try:
            records=ba.load_records(source,manifest,stage=stage)
            reductions=ba.reduce_models(records,manifest,boundaries=('rails',))
            print('REAL_ANALYSIS',pass_id,case,stage,source.name,[(x['status'],x.get('reason')) for x in reductions],flush=True)
        except (ValueError,KeyError) as exc: print('REAL_ANALYSIS',pass_id,case,stage,source.name,'not defined',str(exc),flush=True)
    repeated=t.transform('hull-p2' if pass_id==2 else 'request-end-p1',out,root/('again'+str(pass_id)+case))
    assert repeated['changes']==[]
    try: t.transform('hull-p2' if pass_id==2 else 'request-end-p1',win.archive,win.archive/'invalid')
    except ValueError as exc: assert 'overlaps' in str(exc)
    else: raise AssertionError('source overlap allowed')
    return win

if __name__=='__main__':
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        for pass_id,case in ((1,'tail'),(2,'tail'),(1,'clean')): small(root,pass_id,case)
