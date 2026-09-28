# Cold gate A1 probe: D2 (OFF refused, immediate ON fails, later recovery).
import sys, os, pathlib, tempfile, json, functools
from contextlib import ExitStack
from unittest import mock
scratch = pathlib.Path('/tmp/cg-ntpfix2-d528efb2'); rev = sys.argv[1]
sys.path.insert(0, str(scratch / rev)); os.chdir(scratch / rev)
(scratch / 'tmp').mkdir(exist_ok=True); tempfile.tempdir = str(scratch / 'tmp')
from joulewise import network_time_window as nt
from tests.test_network_time_window import Runner
from tests.test_run_night import NightDriverTests

def names(runner):
    return ['off' if x == nt.OFF_ARGV else 'on' if x == nt.ON_ARGV else 'query'
            for x in runner.calls if x != nt.BOOT_ARGV]

def case(label, off_output, off_raises):
    t = NightDriverTests(); t.setUp(); d = t.driver
    r = Runner(); r.off_output = off_output; r.on_code = 1
    marker = t.root / 'pending.json'
    originals = {n: getattr(nt, n) for n in
                 ['set_network_time_off', 'set_network_time_on', 'run_window_query', 'recover_network_time']}
    try:
        with ExitStack() as s:
            s.enter_context(mock.patch.object(nt, 'RESTORE_PENDING_PATH', marker))
            s.enter_context(mock.patch.object(nt, 'NETWORK_TIME_ENFORCED_KINDS', frozenset({'unknown'})))
            for n, fn in originals.items():
                s.enter_context(mock.patch.object(nt, n, functools.partial(
                    fn, runner=r, boot_probe=lambda: 'boot-1',
                    clock=lambda: {'epoch_s': 10000, 'monotonic_s': 10000})))
            if off_raises:
                # The OFF receipt cannot be saved: the second OFF-failure branch.
                real_off = nt.set_network_time_off
                def off(*a, **k):
                    nt.create_restore_marker(a[0], a[1], marker_path=k['marker_path'])
                    raise OSError('receipt directory not writable')
                s.enter_context(mock.patch.object(nt, 'set_network_time_off', side_effect=off))
            with mock.patch.object(d.subprocess, 'Popen', side_effect=AssertionError('NO CHAIN MAY SPAWN')):
                code = d.run_night(t.plan_path)
            night = t.custody / 'night'
            first = {'exit': code, 'commands_run': names(r),
                     'chain_started_bytes': (night / 'chain.started').read_bytes().decode(),
                     'chain_exited': json.loads((night / 'chain.exited').read_text()),
                     'refusal': json.loads((night / 'refusal.json').read_text())['refusal']['reason']
                                if (night / 'refusal.json').exists() else None,
                     'marker_present': marker.exists()}
            r.on_code = 0; r.calls.clear()
            result = nt.recover_network_time(marker_path=marker, process_group_absent=lambda pgid: False)
            print(label, json.dumps({'rev': rev, 'driver_run': first,
                                     'recovery': {'result': result, 'commands_run': names(r),
                                                  'marker_present': marker.exists()}}), flush=True)
    finally:
        t.tearDown(); t.doCleanups()

def f2_retained():
    # An EMPTY start claim with no exit record: Popen may have run. Must stay unproved.
    from tests.test_network_time_window import WindowTests
    w = WindowTests(); w.setUp()
    try:
        (w.root / 'night/chain.started').write_bytes(b'')
        (w.root / 'night/chain.exited').unlink()
        w.runner.calls.clear()
        result = nt.recover_network_time(marker_path=w.marker, runner=w.runner, boot_probe=lambda: 'boot-1',
                                         clock=lambda: {'epoch_s': 10620, 'monotonic_s': 10620},
                                         process_group_absent=lambda pgid: True)
        print('F2_EMPTY_CLAIM_NO_EXIT', json.dumps({'rev': rev, 'result': result,
              'commands_run': names(w.runner), 'marker_present': w.marker.exists()}), flush=True)
        # An empty claim WITH a launch_failed exit record but no statement in the claim itself.
        (w.root / 'night/chain.exited').write_text(json.dumps({'launch_failed': True}))
        result = nt.recover_network_time(marker_path=w.marker, runner=w.runner, boot_probe=lambda: 'boot-1',
                                         clock=lambda: {'epoch_s': 10620, 'monotonic_s': 10620},
                                         process_group_absent=lambda pgid: True)
        print('EMPTY_CLAIM_WITH_EXIT_RECORD', json.dumps({'rev': rev, 'result': result,
              'commands_run': names(w.runner), 'marker_present': w.marker.exists()}), flush=True)
    finally:
        w.doCleanups()

case('OFF_WRONG_OUTPUT', b'wrong output\n', False)
case('OFF_RECEIPT_RAISES', b'setUsingNetworkTime: Off\n', True)
f2_retained()
print('PROBE_D2_COMPLETE')
