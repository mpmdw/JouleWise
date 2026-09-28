import safety
import json, hashlib
from unittest.mock import patch
from joulewise import calibration_bracketing as b, calibration_epoch_continuation as c, claim_hold
from joulewise.calibration_ledger import LEDGER_SCHEMA, content_id_from_artifact_hashes
r7=b.load_calibration_acceptance_bound(); rule=c.continuation_rule(r7)
slots=[]
for i in range(12):
 hashes={'manifest.json':hashlib.sha256(('manifest-'+str(i)).encode()).hexdigest(),'instrument_evidence.json':hashlib.sha256(('instrument-'+str(i)).encode()).hexdigest()}
 slots.append({'slot':f'd{i+1:02}','attempt_id':f'd{i+1:02}','content_id':content_id_from_artifact_hashes(hashes),'manifest_sha256':hashes['manifest.json'],'instrument_evidence_sha256':hashes['instrument_evidence.json'],'disposition':'valid','anchor_v3_resolved':True,'anchor_v3_detail':None,'b_fiducial_s':'0.025'})
stats=c.equivalence_statistics(['0.025']*12,rule)
evidence={'session_id':'probe-derivation','ledger':{'ledger_schema':LEDGER_SCHEMA,'head_sequence':1,'head_digest':'a'*64},'session_kind':'derivation','session_state':'finalized','declared_slots':[s['slot'] for s in slots],'slots':slots,'acknowledged_attempt_ids':[s['attempt_id'] for s in slots],**{k:v for k,v in stats.items() if k!='verdict'}}
value={'continuation_id':'probe-held-build','schema_version':c.CONTINUATION_SCHEMA,'decision_ids':['D-102'],'acceptance_id':r7['acceptance_id'],'acceptance_file_sha256':b._acceptance_artifact_sha256(r7),'acceptance_derivation_sha256':r7['derivation_sha256'],'verdict':'pass','continued_identity_epoch':{**r7['identity_epoch'],'os_build':'25G83'},'ruling':{'channel':'directive issue 316','authority':'owner','d102_addendum_date':'2026-09-10'},'rule':rule,'evidence':evidence}
value['derivation_sha256']=b._canonical_sha256(value)
raw=json.dumps(value).encode(); path=safety.SCRATCH/'registered-continuation.json';path.write_bytes(raw)
registry={value['continuation_id']:{'path':path,'relative_path':path.name,'file_sha256':hashlib.sha256(raw).hexdigest()}}
try:c.authenticate_epoch_continuation(path,r7,None,registry=registry)
except c.ContinuationRefusal as e:
 assert str(e)=='continued_identity_epoch_claim_held'; print('G2_HELD',str(e))
else:raise AssertionError('continued held build')
with patch.dict(claim_hold.CLAIM_HELD_OS_BUILDS,{},clear=True):
 result=c.authenticate_epoch_continuation(path,r7,None,registry=registry)
 assert result.continued_identity_epoch['os_build']=='25G83'
 print('G2_CONTROL',result.verdict,result.ledger_cross_check)
refusals=[]
epochs=c.acceptance_judged_epochs(r7,None,registry=registry,refusal_details=refusals)
assert [e['os_build'] for e in epochs]==['25F84']
print('G2_JUDGED_EPOCHS',[e['os_build'] for e in epochs],refusals)
print('continuation_probe: PASS')
