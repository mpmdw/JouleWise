import safety
import copy, hashlib, io, json, sys
from contextlib import redirect_stderr
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
from joulewise import calibration_bracketing as b, claim_hold, arm_readiness as arm, arm_readiness_evidence as ae
from joulewise.calibration_ledger import CalibrationLedgerSnapshot, CalibrationBracketSession, LedgerObservation
from scripts import validate_powermetrics_fiducial as pf, calibration_ledger_bootstrap as boot, write_derivation_night_inputs as ni
from tests.test_claim_hold_routes import synthetic_bracket
held_path=b.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH
raw=held_path.read_bytes(); held=json.loads(raw); identity=held['identity_epoch']; hid=held['acceptance_id']
assert identity['os_build']=='25G83'
assert hashlib.sha256(raw).hexdigest()==b.ISSUED_ACCEPTANCE_REGISTRY[hid]['file_sha256']
print('AUTHENTIC_BYTES',hashlib.sha256(raw).hexdigest())
assert b._authenticate_acceptance_bytes(raw)==held
print('OPEN_UNCHECKED_AUTH',hid,'build=25G83')
ops=dict(b._registered_operatives_unchecked(hid)); assert ops['bracket_screen_s']=='0.013701'
print('OPEN_UNCHECKED_OPERATIVES',json.dumps(ops,sort_keys=True))
assert b.load_calibration_acceptance_bound(held_path) is None
assert b._acceptance_bound_from_authenticated_bytes(raw) is None
assert b.acceptance_generation_operatives(hid) is None
assert b._valid_acceptance_bound(held) is True
ins=b.inspect_acceptance_without_claim_authority(held_path)
assert ins.artifact==held and ins.claim_hold
assert b._authenticated_explicit_acceptance_bound(ins.artifact) is None
assert b.issued_calibration_allowance_projection(ins.artifact,pre_exact_bound_lexeme_s='0.030',post_exact_bound_lexeme_s='0.036') is None
print('G1_VALIDATOR_INSPECTION: guarded callers refuse; validator returns boolean; inspector labeled')
ctx=NS(repository=safety.ROOT)
assert ae._recorded_acceptance_authentication(ctx,raw,kind='ACCEPTANCE_OWNER') is None
for shape in ('nested','flat'):
 policy={'selection':'issued_d116_artifact_only','issued':b.ANCHOR_V3_R7_ACCEPTANCE_ID}
 if shape=='nested': policy['issued_acceptance']={'acceptance_id':hid,'path':b.ISSUED_ACCEPTANCE_REGISTRY[hid]['relative_path'],'sha256':hashlib.sha256(raw).hexdigest()}
 else: policy.update(issued_artifact_id=hid,issued_artifact_sha256=hashlib.sha256(raw).hexdigest())
 ctx.tree={'acceptance_policy':policy}
 assert not arm._issued_d079(ctx.tree)
 try: ae._derive_acceptance_owner(ctx)
 except ae.EvidenceAuthoringError as e:
  assert 'production authenticator' in str(e); print('ARM_'+shape,str(e))
 else: raise AssertionError('certified held file')
for with_bytes in (True,False):
 try: boot._issued_acceptance_artifact(None,held,**({'source_artifact_raw':raw} if with_bytes else {}))
 except ValueError as e: assert 'byte pin' in str(e); print('BOOTSTRAP',with_bytes,str(e))
 else: raise AssertionError('bootstrap held')
for aid,row in b.ISSUED_ACCEPTANCE_REGISTRY.items():
 try: pf._derive_preflight_systematic_screen_s(identity,acceptance_path=row['path'])
 except pf._AcceptancePreflightError as e: print('CAPTURE_PREFLIGHT',aid,e.reason,e.context.get('stale_fields'))
 else: raise AssertionError('ordinary capture admitted')
 inspected=b.inspect_acceptance_without_claim_authority(row['path']).artifact
 result,reasons=synthetic_bracket(inspected,identity,2,explicit=True)
 assert result['status']!='passed'
 print('BRACKET',aid,result['status'],reasons,result['acceptance']['freshness'].get('reason'))
# No test-only sampler or identity argv. Stop at ordinary preflight before MLX, battery or ledger writes.
err=io.StringIO()
with patch.object(pf,'_sysctl_identity',side_effect=lambda k:'25G83' if k=='kern.osversion' else identity['hardware_model']), redirect_stderr(err):
 rc=pf.main(['--allow-live','--power-policy',identity['power_policy'],'--output-root',str(safety.SCRATCH/'capture-unused')])
print('ORDINARY_WRITER_MAIN',rc,err.getvalue().strip())
assert rc!=0 and 'acceptance_artifact_epoch_mismatch' in err.getvalue()
assert not (safety.SCRATCH/'capture-unused').exists()
print('ORDINARY_WRITER: refused before ledger write, sampler, MLX and battery')
# Real discovery on synthetic derivation and unresolved session rows; no capture reads allowed.
row=LedgerObservation(sequence=1,receipt_digest='a'*64,attempt_id='d01',content_id='b'*64,artifact_sha256={},identity_epoch=identity,t1_bindings={'anchor_method_version':b.ACTIVE_CAPTURE_ANCHOR_METHOD},capture_wall_time_s='100',exact_bound_lexeme_s='0.025',disposition='valid',custody_locator=str(safety.SCRATCH/'absent'),observation_kind='live-capture',bracket_session_id='derivation')
session=CalibrationBracketSession(session_id='derivation',window_id='w',plan_id='p',plan_sha256='a'*64,evidence_root_id='e',runs_root=str(safety.SCRATCH),capability_receipt_digest='b'*64,capability_sequence=1,slot_attempt_ids={'d01':'d01'},state='finalized',finalized_slots={'d01':row},session_kind='derivation')
for sessions in [(session,),()]:
 snap=CalibrationLedgerSnapshot(ledger_schema='joulewise.calibration_ledger.v1',ledger_path=safety.SCRATCH/'absent-ledger',head_sequence=1,head_digest='a'*64,receipts=(),observations=(row,),refusal_reasons=(),bracket_sessions=sessions)
 assert snap.valid
 with patch.object(b,'_candidate_from_observation',side_effect=AssertionError('endpoint read')):
  result=b.discover_calibration_candidates(snap)
 assert result==()
 print('DERIVATION_ENDPOINT',b._observation_session_kind(row,snap),'excluded')
print('DERIVATION_BASIS',pf._derivation_only_screen_basis()[1]['acceptance_id'])
print('INPUT_WRITER_STALE',ni._stale_identity_fields(b.load_calibration_acceptance_bound(),identity))
print('core_probe: PASS')
