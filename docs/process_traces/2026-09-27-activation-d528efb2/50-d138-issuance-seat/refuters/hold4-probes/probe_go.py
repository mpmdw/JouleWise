import safety
import hashlib, json, subprocess, unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
from joulewise import arm_readiness as arm
from tests import test_arm_readiness as fixtures
from tests.test_claim_hold_routes import ClaimHoldRouteTests
# Existing fixture otherwise initializes a git repository. Substitute only fixture Git writes
# and a deterministic fixture-pack hash. The hold, GO reader and policy checks remain real.
original_run=subprocess.run
intercepted=[]
def run(command,*a,**kw):
 if command[0]=='git' and any(x in command for x in ['add','commit']):
  intercepted.append(command);return subprocess.CompletedProcess(command,0,b'',b'')
 return original_run(command,*a,**kw)
def pack_hash(path):
 return hashlib.sha256(b''.join(p.read_bytes() for p in sorted(Path(path).glob('*')) if p.is_file())).hexdigest()
with patch.object(fixtures,'init_git_fixture',return_value=None),patch.object(subprocess,'run',side_effect=run),patch.object(arm,'committed_pack_tree_sha256',side_effect=pack_hash):
 test=ClaimHoldRouteTests('test_e7_go_receipt_refuses_claim_on_held_machine')
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([test]))
 assert result.wasSuccessful()
 print('S2_DIRECT: held/unreadable refuse; old build/nonclaim pass; replay does not read machine')
 case=fixtures.LaunchConsumptionV2Tests();case.setUp()
 try:
  inputs=case._consumer_inputs(); go=inputs['authenticated_go_receipt']
  def ref(p):return {'path':str(Path(p).resolve()),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
  authpath=Path(go['authorization']['path']);auth=arm.parse_json_bytes(authpath.read_bytes())
  auth.update(purpose='CAMPAIGN_TRANSACTION',claim_eligible=True,authority='V5-TRANSACTION-GO-01');authpath.write_bytes(arm.render_json(auth))
  planpath=inputs['night_plan'];plan=arm.parse_json_bytes(planpath.read_bytes());plan['pack_night']['authorization_record']=ref(authpath);planpath.write_bytes(arm.render_json(plan))
  go['authorization'].update(ref(authpath));go['authorization'].update(purpose='CAMPAIGN_TRANSACTION',claim_eligible=True);go['purpose']='CAMPAIGN_TRANSACTION';go['plan_sha256']=ref(planpath)['sha256']
  for cond in go['conditions']:
   for evidence in cond['evidence']:
    if evidence['path']=='night/authorization.json':evidence['sha256']=ref(authpath)['sha256']
  inputs['go_receipt'].write_bytes(arm.render_json(go));inputs['go_receipt_sha256']=ref(inputs['go_receipt'])['sha256']
  with patch.object(arm,'machine_os_build',return_value='25G83'):
   try:case._invoke_consumer(inputs)
   except arm.LaunchLineageError as e:
    assert 'claim_hold:' in str(e);print('S2_CONSUME_REFUSED',str(e))
   else:raise AssertionError('held claim consumed')
  with patch.object(arm,'machine_os_build',return_value='25F84'):
   consumed=case._invoke_consumer(inputs)
  path=Path(consumed['consumption_path']);value=arm.parse_json_bytes(path.read_bytes())
  with patch.object(arm,'machine_os_build',return_value='25G83'):
   try:arm._replay_consumed_go(value,case.arm,path,require_current_boot=True)
   except arm.LaunchLineageError as e:
    assert 'claim_hold:' in str(e);print('S2_REPLAY_REFUSED',str(e))
   else:raise AssertionError('held live replay accepted')
  with patch.object(arm,'machine_os_build',side_effect=AssertionError('historical machine read')):
   arm._replay_consumed_go(value,case.arm,path,require_current_boot=False)
  print('S2_HISTORICAL_REPLAY: accepted without live authority')
 finally:case.doCleanups()
print('go_probe: PASS; fixture Git calls suppressed; no git command wrote')
