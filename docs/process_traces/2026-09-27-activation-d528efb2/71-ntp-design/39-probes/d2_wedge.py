import sys,pathlib,tempfile,json,functools
from contextlib import ExitStack
from unittest import mock
scratch=pathlib.Path('/tmp/opus-ntpA1-d528efb2');sys.path.insert(0,str(scratch/sys.argv[1]));tempfile.tempdir=str(scratch/"tmp")
from joulewise import network_time_window as nt
from tests.test_network_time_window import Runner
from tests.test_run_night import NightDriverTests
case=NightDriverTests();case.setUp();d=case.driver;r=Runner();r.off_output=b'wrong output\n';r.on_code=1;marker=case.root/'pending.json'
originals={name:getattr(nt,name) for name in ['set_network_time_off','set_network_time_on','run_window_query','recover_network_time']}
try:
    with ExitStack() as s:
        s.enter_context(mock.patch.object(nt,'RESTORE_PENDING_PATH',marker))
        s.enter_context(mock.patch.object(nt,'NETWORK_TIME_ENFORCED_KINDS',frozenset({'unknown'})))
        for name,fn in originals.items():s.enter_context(mock.patch.object(nt,name,functools.partial(fn,runner=r,boot_probe=lambda:'boot-1',clock=lambda:{'epoch_s':10000,'monotonic_s':10000})))
        with mock.patch.object(d.subprocess,'Popen',side_effect=AssertionError('NO CHAIN MAY SPAWN')):
            result=d.run_night(case.plan_path)
        night=case.custody/'night'
        print('OFF_FAILURE',result,'started_bytes',repr((night/'chain.started').read_bytes()),'launch_failed',json.loads((night/'chain.exited').read_text()).get('launch_failed'),'marker_present',marker.exists())
        assert marker.exists();r.on_code=0;r.calls.clear()
        result=nt.recover_network_time(marker_path=marker,process_group_absent=lambda pgid:False)
        print('RECOVERY_AFTER_OFF_FAILURE',result,'on_retried',nt.ON_ARGV in r.calls,'marker_present',marker.exists())
        refusals_before=sorted(x.name for x in night.glob('refusal*.json'))
        code2=d.run_night(case.plan_path)
        refusals_after=sorted(x.name for x in night.glob('refusal*.json'))
        newest=[json.loads((night/n).read_text()) for n in refusals_after if n not in refusals_before]
        print('NEXT_NIGHT_AFTER_D2',code2,'new_refusal_reasons',[x.get('refusal',{}).get('reason') for x in newest],'marker_present',marker.exists(),flush=True)
        assert result == 'restored', 'a known never-launched chain must permit the failed ON retry'
        assert nt.ON_ARGV in r.calls and not marker.exists()
finally:case.tearDown();case.doCleanups()
