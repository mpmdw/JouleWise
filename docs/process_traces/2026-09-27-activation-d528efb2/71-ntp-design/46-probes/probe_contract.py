import sys
sys.path.insert(0, '/Users/edr/code/JouleWise-wt-ntp-n1delta2-d528efb2')
import json, os, tempfile, subprocess
from pathlib import Path
from unittest import mock
from scripts import run_night as d
from joulewise import network_time_window as nt
from tests.test_network_time_window import Runner

def snapshot(_timeout):
    return 0, f'{os.getpid()} 1 python\n888888 {os.getpid()} /bin/ps\n', '', 888888

with tempfile.TemporaryDirectory(dir='/tmp/ntp-n1delta2-astra') as td:
    root=Path(td); night=root/'night'; night.mkdir()
    # A0: missing keys are not JSON null fields; only a complete claim qualifies.
    for label,claim in [('missing_both',{'popen_attempted':False}), ('missing_pid',{'pgid':None,'launch_error':'failed'}), ('complete',{'pid':None,'pgid':None,'popen_attempted':False})]:
        marker=root/'pending.json'
        runner=Runner()
        nt.set_network_time_off(root,label,runner=runner,boot_probe=lambda:'boot',marker_path=marker)
        (night/'chain.started').write_text(json.dumps(claim))
        (night/'chain.exited').write_text('{"launch_failed":true}')
        driver_accepts=d._chain_never_launched(night)
        result=nt.recover_network_time(marker_path=marker,runner=runner,boot_probe=lambda:'boot')
        print('CLAIM',label,'driver_accepts=',driver_accepts,'recovery=',result,'ON=',nt.ON_ARGV in runner.calls)
        for p in (night/'network_time').iterdir(): p.unlink()
    # A1: zero exit with zero rows is not the ruled empty-group answer.
    def malformed_listing(argv,**kw):
        if argv[0].endswith('pgrep') and ',' not in argv[3]:
            return subprocess.CompletedProcess(argv,1,'','')
        return subprocess.CompletedProcess(argv,0,'','')
    with mock.patch.object(d.subprocess,'run',side_effect=malformed_listing), mock.patch.object(d,'_process_snapshot',side_effect=snapshot):
        print('P2_EMPTY_SUCCESS',d._capture_proof_pass({},12345,{111,222},1))
    # A2: a wholly successful first pass can exceed the 5-second bound.
    groups=set(range(1000,1769))
    (night/'evidence_processes.jsonl').write_text(''.join(json.dumps({'pgid':g})+'\n' for g in groups))
    clock=[0.0]
    def slow_clear(argv,**kw):
        clock[0]+=0.9
        return subprocess.CompletedProcess(argv,1,'','')
    def slow_snapshot(timeout):
        clock[0]+=0.9
        return snapshot(timeout)
    with mock.patch.object(d.time,'monotonic',side_effect=lambda:clock[0]), mock.patch.object(d.subprocess,'run',side_effect=slow_clear), mock.patch.object(d,'_process_snapshot',side_effect=slow_snapshot):
        print('FIRST_PASS_BOUND',d._prove_capture_absent({},12345,night),'elapsed=',round(clock[0],1),'window=',d.GROUP_CENSUS_WINDOW_S)
print('PURE_CONTRACT_PROBES_COMPLETE')
