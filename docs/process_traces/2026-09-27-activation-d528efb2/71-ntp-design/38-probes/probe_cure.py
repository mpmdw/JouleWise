# Cold gate A1 probe: the D1 cure prototype (scratch copy "cure") against every
# failing case, the clean path, and liveness after the survivor ends.
import sys, os, pathlib, tempfile, json, functools, subprocess, hashlib, signal, time
from unittest import mock
from contextlib import ExitStack

scratch = pathlib.Path('/tmp/cg-ntpfix2-d528efb2'); rev = sys.argv[1]
root = scratch / rev
sys.path.insert(0, str(root)); os.chdir(root)
(scratch / 'tmp').mkdir(exist_ok=True); tempfile.tempdir = str(scratch / 'tmp')
outside = scratch / 'standins'; outside.mkdir(exist_ok=True)

FORBIDDEN = {'sudo', 'systemsetup', 'powermetrics', 'ioreg', 'pmset', 'log', 'sntp'}
def guard(event, args):
    if event == 'subprocess.Popen' and pathlib.Path(str(args[0])).name in FORBIDDEN:
        raise AssertionError('FORBIDDEN ' + str(args[1]))
sys.addaudithook(guard)

from joulewise import network_time_window as nt
from tests.test_network_time_window import line, Runner
from tests.test_run_night import NightDriverTests

PY = '/opt/homebrew/bin/python3'
SAMPLER_NAME = 'cgprobe-sampler'          # neutral stand-in for the sampler's executable name
spawned = []

def alive(pid):
    try: os.kill(pid, 0); return True
    except ProcessLookupError: return False

def names(runner):
    return ['off' if x == nt.OFF_ARGV else 'on' if x == nt.ON_ARGV else 'query'
            for x in runner.calls if x != nt.BOOT_ARGV]

def patched(stack, d, runner, marker):
    stack.enter_context(mock.patch.object(nt, 'RESTORE_PENDING_PATH', marker))
    stack.enter_context(mock.patch.object(nt, 'NETWORK_TIME_ENFORCED_KINDS', frozenset({'unknown'})))
    for name in ['set_network_time_off', 'set_network_time_on', 'run_window_query', 'recover_network_time']:
        fn = getattr(nt, name)
        stack.enter_context(mock.patch.object(nt, name, functools.partial(
            fn, runner=runner, boot_probe=lambda: 'boot',
            clock=lambda: {'epoch_s': 10000, 'monotonic_s': 10000})))
    stack.enter_context(mock.patch.object(
        d, '_probe_group_absent', side_effect=lambda pgid, timeout_s=1: d._group_census(pgid, timeout_s)[0]))
    if hasattr(d, 'CAPTURE_SAMPLER_BASENAMES'):
        stack.enter_context(mock.patch.object(d, 'CAPTURE_SAMPLER_BASENAMES', ('powermetrics', SAMPLER_NAME)))

def case(label, kind, journaled, then_recover=False):
    """kind: none | collector (script under the measurement root) |
    sampler (executable-name signature, outside every night path) | plain (no signature)."""
    t = NightDriverTests(); t.setUp(); d = t.driver
    runner = Runner(nt.HEADER + '\n' + line(9900)); marker = t.root / 'pending.json'
    child_file = t.root / 'child.pid'; launcher = t.root / 'launcher.py'
    night = t.custody / 'night'
    if kind == 'collector':
        script = t.root / 'scripts'; script.mkdir(exist_ok=True); script = script / 'standin_collector.py'
        script.write_text('import time\ntime.sleep(45)\n'); argv = [PY, '-B', str(script), 'collect']
    elif kind == 'sampler':
        script = outside / SAMPLER_NAME
        script.write_text('import time\ntime.sleep(45)\n'); argv = [PY, '-B', str(script)]
    elif kind == 'plain':
        argv = [PY, '-B', '-c', 'import time; time.sleep(45)']
    else:
        argv = None
    if argv is None:
        launcher.write_text('print("chain with no children")\n')
    else:
        launcher.write_text(
            "import subprocess,pathlib,sys,time,os\n"
            "sys.path.insert(0,%r)\n"
            "p=subprocess.Popen(%r,stdin=subprocess.DEVNULL,start_new_session=True)\n"
            "if %r:\n"
            "    from joulewise.quiet_predicate_campaign import append_event\n"
            "    append_event(pathlib.Path(os.environ['NIGHT_DIR'])/'evidence_processes.jsonl',"
            "{'kind':'collector','pgid':p.pid,'epoch_s':time.time()})\n"
            "pathlib.Path(%r).write_text(str(p.pid))\n" % (str(root), argv, journaled, str(child_file)))
    t.chain.write_text('exec %s -B %s\n' % (PY, launcher))
    t.sidecar.write_text(hashlib.sha256(t.chain.read_bytes()).hexdigest() + '\n')
    child = None
    try:
        with ExitStack() as s:
            patched(s, d, runner, marker)
            code = d.run_night(t.plan_path)
            if argv is not None:
                child = int(child_file.read_text()); spawned.append(child)
            out = {'rev': rev, 'exit': code, 'descendant_alive': bool(child and alive(child)),
                   'journal_exists': (night / 'evidence_processes.jsonl').exists(),
                   'commands_run': names(runner),
                   'chain_exited_written': (night / 'chain.exited').exists(),
                   'marker_present': marker.exists()}
            if then_recover:
                runner.calls.clear()
                out['recovery_while_alive'] = {'result': d.network_time_window.recover_network_time(
                    marker_path=marker, process_group_absent=d._probe_group_absent,
                    **({'capture_absent': lambda n, p, sig: d._capture_absence_proof(n, p, sig)[0]}
                       if hasattr(d, '_capture_absence_proof') else {})),
                    'commands_run': names(runner), 'marker_present': marker.exists()}
                os.kill(child, signal.SIGKILL); time.sleep(0.3)
                runner.calls.clear()
                out['recovery_after_survivor_ended'] = {'result': d.network_time_window.recover_network_time(
                    marker_path=marker, process_group_absent=d._probe_group_absent,
                    **({'capture_absent': lambda n, p, sig: d._capture_absence_proof(n, p, sig)[0]}
                       if hasattr(d, '_capture_absence_proof') else {})),
                    'commands_run': names(runner), 'marker_present': marker.exists(),
                    'on_receipts': sorted(x.name for x in (night / 'network_time').glob('h5-on*'))}
            print(label, json.dumps(out), flush=True)
    finally:
        if child is None and child_file.exists() and child_file.read_text():
            child = int(child_file.read_text())
        if child:
            try: os.kill(child, signal.SIGKILL)
            except ProcessLookupError: pass
        t.tearDown(); t.doCleanups()

try:
    case('G_CLEAN_CHAIN_NO_CHILDREN', 'none', False)
    case('B_COLLECTOR_JOURNALED', 'collector', True)
    case('C_COLLECTOR_UNJOURNALED', 'collector', False)
    case('D_SAMPLER_NAME_UNJOURNALED_OUTSIDE_NIGHT_PATHS', 'sampler', False)
    case('F_H_RECOVERY_THEN_LIVENESS', 'collector', False, then_recover=True)
    case('I_PLAIN_SLEEPER_NO_SIGNATURE', 'plain', False)
finally:
    for pid in spawned:
        try: os.kill(pid, signal.SIGKILL)
        except ProcessLookupError: pass
    time.sleep(0.2)
    print('SLEEPERS_LEFT', [pid for pid in spawned if alive(pid)])
print('PROBE_CURE_COMPLETE')
