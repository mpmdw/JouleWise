import hashlib,json,sys
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R))
from joulewise.calibration_bracketing import load_calibration_acceptance_bound,evaluate_calibration_bracket,ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
from joulewise.schemas import CalibrationBracketingPolicy
ledger=Path('/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/runs/calibration_observation_ledger.jsonl')
before=hashlib.sha256(ledger.read_bytes()).hexdigest()
for epoch,path in [('25G83',None),('25F84',ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH)]:
 a=load_calibration_acceptance_bound() if path is None else load_calibration_acceptance_bound(path)
 assert a is not None
 cutoff=a['ledger_cutoff']
 s=load_calibration_ledger_snapshot(ledger,R/'configs/calibration/calibration_ledger_head.json',baseline_sequence=cutoff['sequence'],baseline_digest=cutoff['head_digest'],require_committed_pin=True,verify_custody=False,repo_root=R,mode='read_replay')
 print('snapshot',epoch,'valid=',s.valid,'sequence=',s.head_sequence,'head=',s.head_digest,'baseline=',s.baseline_sequence,'refusals=',s.refusal_reasons)
 assert s.valid
 bindings=dict(a['identity_epoch']);assert bindings['os_build']==epoch
 kwargs={} if path is None else {'acceptance_bound':a}
 result,refusals=evaluate_calibration_bracket([],window_start_s=0,window_end_s=1,bindings=bindings,policy=CalibrationBracketingPolicy(True,0.0),ledger_snapshot=s,**kwargs)
 f=result['acceptance']['freshness'];print('acceptance',a['acceptance_id'],'path=',str(path),'freshness=',json.dumps(f,sort_keys=True),'evaluation_refusals=',refusals)
 assert f['status']=='fresh' and f['stale_fields']==[]
 assert 'calibration_acceptance_bound_stale' not in refusals
assert hashlib.sha256(ledger.read_bytes()).hexdigest()==before
print('real ledger SHA256',before,'unchanged=True')
print('vi FRESHNESS PASS default 25G83=fresh explicit R7 25F84=fresh')
