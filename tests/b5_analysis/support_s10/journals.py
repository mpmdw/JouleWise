"""Synthetic primary monitor/cooldown observations; the production joins run."""
import json
from pathlib import Path
from unittest import mock
from tests.b5_analysis.support_s10.member import EPOCH_ORIGIN


def write_cooldown(root,run_id,session):
    import hashlib
    path=Path(root)/'campaign_manifests/cooldown_raw'/f'{run_id}.jsonl'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({'release':True,'release_criteria_met_late':False,
        'power_w':.7331,'elapsed_s':7.331})+'\n')
    return {'result':'recovered','session_id':session,'following_run_id':run_id,
        'raw_artifact':{'path':path.relative_to(path.parent.parent).as_posix(),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'records':1}}


def write_monitor_journals(directory,start_s,end_s,*,charge_intervals=()):
    from tests import test_harvest_b5_window as hb
    from joulewise.hazards import battery
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    offset=round((EPOCH_ORIGIN-100.)*1e9)
    lo=round((start_s-EPOCH_ORIGIN+100.)*1e9)
    hi=round((end_s-EPOCH_ORIGIN+100.)*1e9)
    with mock.patch.object(hb,'WALL_OFFSET_NS',offset):
        journals={name:hb.L1Journal(name) for name in ('battery','thermal','contention','clock','disk')}
        for journal in journals.values():journal.write('session_start',lo-10**9,values={'pid':4242,'argv':['synthetic']})
        for n,poll in enumerate(range(lo,hi,10**9)):
            if n%60==0:
                journals['battery'].write('reading',poll,poll+1000000,
                    values=hb.battery_values(round((poll+offset)/1e9),power_telemetry=hb.STEADY_TELEMETRY))
                journals['disk'].write('reading',poll,poll+1000000,values=hb.disk_values(200*hb.GIB))
            epoch=(poll+offset)/1e9
            current=447. if any(lo<=epoch<=hi for lo,hi in charge_intervals) else 0.
            sample=battery.smc_sample(lambda:{'values':{'B0AC':current,'B0AV':12733.,'PDTR':.7331,
                'PSTR':.7331,'PPBR':0.},'errors':{}})
            journals['battery'].write('reading',poll-400000,poll,values={'source':'smc','smc':sample})
            if n%5==0:journals['thermal'].write('reading',poll-3000000,poll,values={'level':0,'source':'notifyutil'})
            if n%10==0:journals['contention'].write('interval',poll-1000000,poll+10**10+1000000,
                values=hb.contention_values(poll,poll+10**10))
            journals['clock'].write('reading',poll-600,poll,
                values=hb.clock_values(poll+hb.RAW_OFFSET_NS,offset-hb.RAW_OFFSET_NS,n%5==0))
        for name,journal in journals.items():
            journal.write('session_end',hi+10**9,values={'reason':'synthetic complete'})
            journal.dump(directory/(name+'.jsonl'))
