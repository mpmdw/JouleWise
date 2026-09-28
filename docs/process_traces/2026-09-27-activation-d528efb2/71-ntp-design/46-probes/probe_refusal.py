import sys
sys.path.insert(0, '/Users/edr/code/JouleWise-wt-ntp-n1delta2-d528efb2')
import json,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from scripts import run_night as d
from joulewise import quiet_predicate_campaign as q

with tempfile.TemporaryDirectory(dir='/tmp/ntp-n1delta2-astra') as td:
    root=Path(td); night=root/'night'; night.mkdir()
    plan=SimpleNamespace(plan_id='proof-refusal-probe', receipt_class='DIAGNOSTIC_NO_PACK',quiet_admission=None)
    (night/'chain.started').write_text('{}')
    (night/'evidence_processes.jsonl').write_text('')
    (night/'receipt.json').write_text(json.dumps({'plan_id':plan.plan_id,'conditions':[{'condition_id':'C5','status':'PASS','measured':{'payload_kind':'quiet_predicate_evidence'}}]}))
    with mock.patch.object(d.night_gate,'validate_receipt',return_value=[]),mock.patch.object(q,'cleanup_record',return_value={'cleanup_proven':True}):
        print('K_RESULT',d._evidence_cleanup_error(plan,night))
    proof={'check':'P3','matches':[{'pid':999999,'command':str(root/'collector.py')}]}
    abort=d._capture_unproved_abort(night,plan,root,None,'capture process absence could not be proved',proof)
    if 'document' not in abort:
        d._write_driver_refusal(night/'refusal.json',plan,abort['reason'],abort['detail'],abort['evidence'])
    result=d._write_result(root,night,plan,'REFUSED',1,abort['reason'],0,0,None,0)
    for p in d._refusal_paths(night):print('REFUSAL',p.name,json.loads(p.read_text())['refusal']['reason'])
    print('RESULT',result['verdict'],result['aborted_reason'],result['refusal_documents'])
    with mock.patch.object(d,'_durable_record'),mock.patch.object(d,'_write_courier_outcome'):
        print('C7_EXIT',d._finish_reporting(root,night,plan,d.EXIT_REFUSED,None,allow_courier=False,courier_error='chain termination was not proven'))
print('PURE_REFUSAL_PROBE_COMPLETE')
