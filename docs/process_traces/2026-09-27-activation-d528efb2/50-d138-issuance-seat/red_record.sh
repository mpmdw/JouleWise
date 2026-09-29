#!/bin/zsh
set -eu
/opt/homebrew/bin/python3 -B - <<'PY'
from pathlib import Path
import os, shutil, subprocess, tempfile

FIX = Path('/Users/edr/code/JouleWise-wt-d138-impl-d528efb2')
OLD1 = Path('/Users/edr/code/JouleWise-wt-d138-final-d528efb2')
OLD2 = Path('/Users/edr/code/JouleWise-wt-d138-hold2-d528efb2')
print('RED_RECORD fix_base=5decbe6b old1=325d9f77 old2=8458f797', flush=True)

def run_case(root, file, cls, method, test_root=None):
    test_root = test_root or root
    source = test_root / file
    code = '''import importlib.util, unittest
source = %r
class_name = %r
method = %r
spec = importlib.util.spec_from_file_location("red_case", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cls = getattr(module, class_name)
if hasattr(cls, "setUpClass"):
    cls.setUpClass()
result = unittest.TestResult()
cls(method).run(result)
kind = "FAIL" if result.failures else "ERROR" if result.errors else "PASS"
message = (result.failures or result.errors)
print(kind + " " + str(result.testsRun) + " " + (message[0][1].splitlines()[-1][:120] if message else ""))
''' % (str(source), cls, method)
    env = dict(os.environ, PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE='1')
    completed = subprocess.run(['/opt/homebrew/bin/python3', '-B', '-c', code],
                               cwd=root, env=env, capture_output=True, text=True)
    line = completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else 'ERROR subprocess'
    if completed.returncode or not line.startswith(('PASS ', 'FAIL ', 'ERROR ')):
        line = 'ERROR subprocess ' + (completed.stderr.strip().splitlines()[-1][:120] if completed.stderr.strip() else '')
    return line

def require(label, observed, expected):
    print(label + ' ' + observed, flush=True)
    if not observed.startswith(expected + ' '):
        raise SystemExit('STOP non-assertion RED or non-GREEN: ' + label)

ROUTES = 'tests/test_claim_hold_routes.py'
RC = 'ClaimHoldRouteTests'
old = [
    (OLD1, 'E-1', 'test_hr1_r7_pack_capture_preflight_stays_at_r7'),
    (OLD1, 'E-2', 'test_e2_observed_build_gate_with_file_gate_switched_off'),
    (OLD1, 'E-3', 'test_hr3_manual_route_cannot_consume_held_file'),
    (OLD2, 'E-4', 'test_e4_nested_mixed_identifier_is_refused'),
    (OLD2, 'E-5', 'test_e5_flat_mixed_identifier_is_refused'),
    (OLD2, 'E-6', 'test_hr6_authenticator_refuses_held_bytes'),
    (OLD2, 'E-6b', 'test_e6b_loader_has_no_hold_bypass_keyword'),
    (OLD2, 'E-6c', 'test_e6c_identifier_operatives_are_held'),
    (OLD2, 'E-6d', 'test_e6d_later_registered_file_at_held_build_is_refused'),
    (OLD2, 'E-6e', 'test_e6e_continuation_into_held_build_is_refused'),
    (OLD2, 'E-9', 'test_e9_identity_override_requires_test_sampler'),
]
for root, label, method in old:
    commit = '325d9f77' if root == OLD1 else '8458f797'
    require(f'{label}@{commit}', run_case(root, ROUTES, RC, method, FIX), 'FAIL')
for label, method in [('E-1','test_hr1_r7_pack_capture_preflight_stays_at_r7'),
                      ('E-2','test_e2_observed_build_gate_with_file_gate_switched_off'),
                      ('E-3','test_hr3_manual_route_cannot_consume_held_file'),
                      ('E-4','test_e4_nested_mixed_identifier_is_refused'),
                      ('E-5','test_e5_flat_mixed_identifier_is_refused'),
                      ('E-5c','test_e5c_all_nine_committed_packs_stay_admitted'),
                      ('E-6','test_hr6_authenticator_refuses_held_bytes'),
                      ('E-6b','test_e6b_loader_has_no_hold_bypass_keyword'),
                      ('E-6c','test_e6c_identifier_operatives_are_held'),
                      ('E-6d','test_e6d_later_registered_file_at_held_build_is_refused'),
                      ('E-6e','test_e6e_continuation_into_held_build_is_refused'),
                      ('E-7','test_e7_go_receipt_refuses_claim_on_held_machine'),
                      ('E-8','test_e8_manual_campaign_refuses_before_runner'),
                      ('E-9','test_e9_identity_override_requires_test_sampler'),
                      ('E-10','test_e10_inspection_and_derivation_provenance'),
                      ('E-11','test_e11_default_path_and_identifier_must_agree')]:
    require(label+'@fix', run_case(FIX, ROUTES, RC, method), 'PASS')
PROMO='tests/test_promote_calibration_candidate.py'
require('P8@8458f797', run_case(OLD2,PROMO,'PromotionTests','test_p8_citations_and_all_four_holds_are_complete',FIX),'FAIL')
require('P8@fix', run_case(FIX,PROMO,'PromotionTests','test_p8_citations_and_all_four_holds_are_complete'),'PASS')

scratch = Path(tempfile.mkdtemp(prefix='d138-red-scratch-', dir='/tmp'))
try:
    for directory in ('joulewise','scripts','configs','tests'):
        shutil.copytree(FIX/directory, scratch/directory, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    (scratch/'docs').symlink_to(FIX/'docs', target_is_directory=True)
    def mutation(label, path, before, after, file, cls, method):
        target=scratch/path
        original=target.read_text()
        if original.count(before)!=1:
            raise SystemExit('STOP mutation anchor '+label+' count='+str(original.count(before)))
        target.write_text(original.replace(before,after,1))
        try:
            require('M-'+label,run_case(scratch,file,cls,method),'FAIL')
        finally:
            target.write_text(original)
    cb='joulewise/calibration_bracketing.py'
    mutation('G1',cb,'''    artifact = _authenticate_acceptance_bytes(raw)
    if (artifact is not None and
            claim_hold_for_os_build(artifact["identity_epoch"]["os_build"]) is not None):
        return None
    return artifact
''','''    return _authenticate_acceptance_bytes(raw)
''',ROUTES,RC,'test_hr6_authenticator_refuses_held_bytes')
    mutation('G2','joulewise/calibration_epoch_continuation.py','''    _require(claim_hold_for_os_build(epoch.get("os_build")) is None,
             "continued_identity_epoch_claim_held")
''','',ROUTES,RC,'test_e6e_continuation_into_held_build_is_refused')
    mutation('S1',cb,'''    if (observed_hold := claim_hold_for_os_build(observed_identity.get("os_build"))) is not None:
        result["acceptance"]["artifact"]["claim_eligible"] = False
        result["acceptance"]["freshness"] = {
            "status": "stale", "reason": "observed_epoch_claim_held", "hold": observed_hold,
        }
        return result, ("calibration_acceptance_bound_stale",)
''','',ROUTES,RC,'test_e2_observed_build_gate_with_file_gate_switched_off')
    mutation('single-id','joulewise/arm_readiness.py','''    return (len(declared) == 1 and next(iter(declared)) in _ISSUED_D079_IDS
            and claim_hold_for_acceptance_id(next(iter(declared))) is None)
''','''    return any(identifier in _ISSUED_D079_IDS and claim_hold_for_acceptance_id(identifier) is None
               for identifier in declared)
''',ROUTES,RC,'test_e4_nested_mixed_identifier_is_refused')
    mutation('operatives',cb,'''    if claim_hold_for_acceptance_id(acceptance_id) is not None:
        return None
    return _registered_operatives_unchecked(acceptance_id, acceptance=acceptance)
''','''    return _registered_operatives_unchecked(acceptance_id, acceptance=acceptance)
''',ROUTES,RC,'test_e6c_identifier_operatives_are_held')
    mutation('S2','joulewise/arm_readiness.py','''        if authorization["claim_eligible"] and require_current_boot:
            hold = claim_hold_for_os_build(machine_os_build())
            if hold is not None:
                raise _go_invalid("claim_hold: " + hold)
''','',ROUTES,RC,'test_e7_go_receipt_refuses_claim_on_held_machine')
    mutation('S3','scripts/run_campaign.py','''        if not args.dry_run:
            from joulewise.claim_hold import claim_hold_for_os_build, machine_os_build
            policy = load_campaign_policy(args.campaign_policy)
            if (policy.idle_admission_extension is not None
                    and policy.idle_admission_extension.claim_bearing):
                hold = claim_hold_for_os_build(machine_os_build())
                if hold is not None:
                    print(hold, file=sys.stderr)
                    return 2
''','',ROUTES,RC,'test_e8_manual_campaign_refuses_before_runner')
    mutation('build-entry',cb,'    EPOCH_25G83_R1_ACCEPTANCE_ID: "25G83",\n','',
             'tests/test_claim_hold_census.py','ClaimHoldCensusTests','test_c7_registered_builds_and_held_routes')
    mutation('R7-predecessor','scripts/issue_calibration_acceptance_generation.py',
             'if predecessor["acceptance_id"] != ANCHOR_V3_R7_ACCEPTANCE_ID:',
             'if predecessor["acceptance_id"] != ACTIVE_ACCEPTANCE_ID:',
             'tests/test_acc_25g83_rev5.py','RevisionFiveTests',
             'test_issuer_refuses_unsealed_launch_context_and_disposes_exact_ids')
    mutation('R7-prepare-default','scripts/issue_calibration_acceptance_generation.py',
             '"--predecessor-acceptance", type=Path, default=ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH,',
             '"--predecessor-acceptance", type=Path, default=DEFAULT_ACCEPTANCE_BOUND_PATH,',
             'tests/test_acc_25g83_rev5.py','RevisionFiveTests',
             'test_revision_five_predecessor_default_and_simulation_are_frozen_to_r7')
    mutation('R7-epoch-default','scripts/epoch_equivalence_check.py',
             '"--acceptance", type=Path, default=ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH,',
             '"--acceptance", type=Path, default=DEFAULT_ACCEPTANCE_BOUND_PATH,',
             'tests/test_epoch_equivalence_check.py','EpochEquivalenceCheckTest',
             'test_cli_default_is_frozen_to_r7')
    mutation('R7-simulation','scripts/sim_acc_25g83_rev5.py',
             'reference = load_calibration_acceptance_bound(ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH)',
             'reference = load_calibration_acceptance_bound(DEFAULT_ACCEPTANCE_BOUND_PATH)',
             'tests/test_acc_25g83_rev5.py','RevisionFiveTests',
             'test_revision_five_predecessor_default_and_simulation_are_frozen_to_r7')
    census='tests/test_claim_hold_census.py'; cc='ClaimHoldCensusTests'
    planted=[
        ('new-reader','scripts/planted_calibration_reader.py',None,'import json\nfrom pathlib import Path\njson.loads((Path(__file__).resolve().parents[1] / "configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json").read_text())\n','test_c5_calibration_readers_are_reviewed'),
        ('unchecked-alias','joulewise/arm_readiness_evidence.py','append','\nfrom joulewise.calibration_bracketing import _authenticate_acceptance_bytes as planted_unchecked\n','test_c1_unchecked_authenticator_stays_local'),
        ('second-pass','joulewise/calibration_bracketing.py','append','\ndef planted_pass():\n    result = {}\n    result["status"] = "passed"\n','test_c6_only_pass_site_has_top_level_build_guard'),
        ('inspection-alias','joulewise/whole_window.py','append','\nfrom joulewise.calibration_bracketing import inspect_acceptance_without_claim_authority as planted_inspection\n','test_c2_inspection_and_unchecked_operatives_stay_local'),
    ]
    for label,path,mode,addition,method in planted:
        target=scratch/path
        original=target.read_text() if mode else None
        target.write_text((original or '')+addition)
        try:
            require('C-plant-'+label,run_case(scratch,census,cc,method),'FAIL')
        finally:
            if original is None: target.unlink()
            else: target.write_text(original)
    print('RED_RECORD_COMPLETE scratch_removed=true',flush=True)
finally:
    shutil.rmtree(scratch)
PY
