import safety
import json, shutil, tempfile, subprocess
from pathlib import Path
from unittest.mock import patch
from scripts import run_campaign as rc
from joulewise import claim_hold, measurement_liveness as ml
class ChildReached(BaseException): pass
base = Path(tempfile.mkdtemp(prefix='campaign-', dir=safety.SCRATCH))
configs = base/'configs'; configs.mkdir()
source = safety.ROOT/'configs/campaigns/p2_015_floors/11_neg8_end/p2015-neg8-reference-end.json'
shutil.copyfile(source, configs/source.name)
policy = safety.ROOT/'configs/campaign_policies/quiet_mac_p2_production.json'
argv = [str(configs),'--runs-dir',str(base/'runs'),'--campaign-policy',str(policy)]
assert rc.load_campaign_policy(str(policy)).idle_admission_extension.claim_bearing is True
snapshot = {'power_source':'AC Power','power':{'external_connected':True},'low_power_mode':False,'display_power_state':'all_asleep','screensaver_engaged':False,'thermal_pressure':'nominal','os_build':'25G83'}
original_run = subprocess.run
calls=[]
def sentinel(command, *args, **kwargs):
    if '-m' in command and 'joulewise' in command:
        calls.append(list(command)); raise ChildReached()
    return original_run(command,*args,**kwargs)
with patch.object(rc,'observe_identity',return_value=ml.Identity('LIVE','Mon Sep 28 10:00:00 2026')), patch.object(ml,'observe_identity',return_value=ml.Identity('LIVE','Mon Sep 28 10:00:00 2026')), patch.object(claim_hold,'machine_os_build',return_value='25G83') as build, patch.object(rc,'collect_environment_snapshot',return_value=snapshot), patch.object(subprocess,'run',side_effect=sentinel):
    args=rc.parse_args(argv)
    try:
        result=rc.run_campaign(args)
        print('DIRECT_RETURN',result)
    except ChildReached:
        print('DIRECT_CHILD_REACHED',json.dumps(calls[-1]))
    print('DIRECT_BUILD_READS',build.call_count)
    assert len(calls)==1, 'runner did not reach child'
    assert build.call_count==0
    calls.clear(); build.reset_mock()
    result=rc.main(argv)
    print('MAIN_RETURN',result,'CHILD_CALLS',len(calls),'BUILD_READS',build.call_count)
    assert result==2 and calls==[] and build.call_count==1
print('campaign_probe: PASS; direct runner reaches subprocess.run; main refuses; no child launched')
