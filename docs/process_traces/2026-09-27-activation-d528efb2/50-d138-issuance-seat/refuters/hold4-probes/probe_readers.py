import safety
import json, sys, io, hashlib
from pathlib import Path
from types import SimpleNamespace as NS
from contextlib import redirect_stdout
from unittest.mock import patch
from joulewise import calibration_bracketing as b, whole_window as ww
from joulewise.analysis_engine import inputs as ai
from scripts import mint_floor_artifact as mint, mint_floor_artifact_generalized as gen, run_campaign as rc, issue_calibration_acceptance_generation as issuance, issue_epoch_continuation as continuation, reissue_calibration_acceptance as reissue, sim_acc_25g83_rev5 as sim, epoch_equivalence_check as equivalence, generate_g2a_probe_inputs as g2a, validate_powermetrics_fiducial as pf
held=b.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH
class ReaderReached(BaseException): pass
seen=[]
def probe(name,fn):
 def trace(frame,event,arg):
  if event=='return' and frame.f_code is b.load_calibration_acceptance_bound.__code__:
   caller=frame.f_back
   row={'case':name,'caller':str(Path(caller.f_code.co_filename).relative_to(safety.ROOT))+':'+str(caller.f_lineno),'function':caller.f_code.co_name,'path':str(frame.f_locals['path']),'returned':arg.get('acceptance_id') if isinstance(arg,dict) else arg}
   seen.append(row); print(json.dumps(row)); raise ReaderReached
  return trace
 sys.settrace(trace)
 try: fn()
 except ReaderReached: pass
 finally: sys.settrace(None)
 assert seen and seen[-1]['case']==name, name+' failed to exercise reader'
# Default readers: actual caller executes, tracing stops after real loader returns.
probe('analysis.bind',lambda:ai.bind_floor_artifact_evidence({},safety.SCRATCH/'floor',{},strict_validator=None))
probe('whole_window.constructor',lambda:ww.AuthenticatedConsumptionSession(safety.SCRATCH,set()))
probe('mint.component',lambda:mint._authenticate_component(None,expected_cell_id='',expected_basis_sha256='',strict_validator=None))
probe('mint.bind',lambda:mint.bind_floor_artifact_evidence({},safety.SCRATCH/'floor',{},strict_validator=None))
plan=safety.ROOT/'configs/campaigns/p2_015_floors/calibration_plan.json'
probe('mint.main',lambda:mint.mint_floor_artifact(artifact_id='probe',floor_path=safety.SCRATCH/'floor',statement_path=safety.SCRATCH/'statement',calibration_plan_path=plan,calibration_plan_relative_path=str(plan.relative_to(safety.ROOT)),absolute_paths=None,comparative_paths=None,project_commit='b953f4b0119f0e05bf02cb9ac206eaf4498b08e3',project_tree_state='clean',strict_validator=None))
probe('campaign.snapshot',lambda:rc._load_calibration_snapshot_for_evaluation())
probe('issuance.check',lambda:issuance.check(NS(acceptance=held)))
probe('issuance.predecessor',lambda:issuance._authenticated_predecessor(held))
probe('continuation.derive',lambda:continuation.derive_record(NS(acceptance=str(held))))
candidate=safety.SCRATCH/'continuation-check.json'; candidate.write_text(json.dumps({'acceptance_id':b.EPOCH_25G83_R1_ACCEPTANCE_ID}))
probe('continuation.check',lambda:continuation.check(NS(candidate=candidate)))
probe('reissue.main',lambda:reissue.main(['--predecessor',str(held),'--output',str(safety.SCRATCH/'not-written.json')]))
with patch.object(sys,'argv',['sim','--trials','1']): probe('simulation.main',sim.main)
probe('equivalence.reference',lambda:equivalence.reference_envelope(held))
# Generalized v2: real held JSON is parsed, real loader refuses; no corpus or digest is forged.
try:
 gen._authenticate_v2_inputs(pinset=NS(value={'producer_plans':[]}),pinset_path=safety.SCRATCH/'unused',pinset_sha256='a'*64,input_manifest_path=safety.SCRATCH/'unused',strict_validator=None,consumption_semantics_id=None,input_manifest={'producer_plans':[],'calibration_acceptance':str(held)})
except gen.MintError as e:
 assert 'not authenticated' in str(e); print('generalized.v2 REFUSED',str(e))
else: raise AssertionError('held v2 mint accepted')
# Generate a valid legacy analysis manifest and floor with test builder, no git or hardware.
from scripts import generate_matrix
from tests.test_detection_floor import make_artifact
out=safety.SCRATCH/'analysis-configs'
with redirect_stdout(io.StringIO()):
 generate_matrix.main(['--base',str(safety.ROOT/'configs/examples/mac_mlx_local.json'),'--model-tag','qwen25-1p5b','--out-dir',str(out)])
floor=safety.SCRATCH/'analysis-floor.json'; floor.write_text(json.dumps(make_artifact()))
probe('analysis.load',lambda:ai.load_analysis_inputs(out/'analysis_manifest.json',safety.SCRATCH/'analysis-runs',floor,strict_validator=None))
# Held-machine G2A stops at capture preflight before mlx, sampler binary or T1 probes.
identity=b.inspect_acceptance_without_claim_authority(held).artifact['identity_epoch']
with patch.object(pf,'_sysctl_identity',side_effect=lambda k: '25G83' if k=='kern.osversion' else identity['hardware_model']):
 try:g2a._derive_live_vectors(identity['power_policy'])
 except g2a.G2AProbeError as e:
  assert 'acceptance_artifact_epoch_mismatch' in str(e); print('G2A_LIVE_VECTORS REFUSED',str(e))
 else:raise AssertionError('G2A held-build vectors returned')
(safety.SCRATCH/'reader-edges.json').write_text(json.dumps(seen,indent=2)+'\n')
print('readers_probe: PASS; '+str(len(seen))+' real caller/loader edges; v2 and G2A refused')
