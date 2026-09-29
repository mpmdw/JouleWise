# Cold gate A1 probe: D1 (separately grouped descendant) against the driver,
# the driver's kill path, and recovery. Real process-group census (pgrep).
# Network-time commands and the log query are injected; sleepers are killed here.
import sys, os, pathlib, tempfile, json, functools, subprocess, hashlib, signal, time
from unittest import mock
from contextlib import ExitStack

scratch = pathlib.Path('/tmp/cg-ntpfix2-d528efb2')
rev = sys.argv[1]
root = scratch / rev
sys.path.insert(0, str(root))
os.chdir(root)
tempfile.tempdir = str(scratch / 'tmp')
(scratch / 'tmp').mkdir(exist_ok=True)

FORBIDDEN = {'sudo', 'systemsetup', 'powermetrics', 'ioreg', 'pmset', 'log', 'sntp'}
def guard(event, args):
    if event == 'subprocess.Popen':
        exe, argv, cwd, env = args
        if pathlib.Path(str(exe)).name in FORBIDDEN:
            raise AssertionError('FORBIDDEN ' + str(argv))
sys.addaudithook(guard)

from joulewise import network_time_window as nt
from tests.test_network_time_window import line, Runner
from tests.test_run_night import NightDriverTests

PY = '/opt/homebrew/bin/python3'
SLEEPER = [PY, '-B', '-c', 'import time; time.sleep(45)']
spawned = []

def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False

def calls(runner):
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
    # The REAL production census: pgrep -lf -g <pgid> .
    real = lambda pgid, timeout_s=1: d._group_census(pgid, timeout_s)[0]
    stack.enter_context(mock.patch.object(d, '_probe_group_absent', side_effect=real))
    return real

def launcher_text(child_file, new_session, linger_s=0):
    # The Popen below copies the production call shape of
    # joulewise/quiet_predicate_campaign.py:1610.
    return ("import subprocess,pathlib,time\n"
            "p=subprocess.Popen(%r,stdin=subprocess.DEVNULL,start_new_session=%r)\n"
            "pathlib.Path(%r).write_text(str(p.pid))\n"
            "time.sleep(%r)\n" % (SLEEPER, new_session, str(child_file), linger_s))

def driver_case(label, new_session):
    t = NightDriverTests(); t.setUp(); d = t.driver
    runner = Runner(nt.HEADER + '\n' + line(9900)); marker = t.root / 'pending.json'
    child_file = t.root / 'child.pid'; launcher = t.root / 'launcher.py'
    launcher.write_text(launcher_text(child_file, new_session))
    t.chain.write_text('exec %s -B %s\n' % (PY, launcher))
    t.sidecar.write_text(hashlib.sha256(t.chain.read_bytes()).hexdigest() + '\n')
    child = None
    try:
        with ExitStack() as s:
            real = patched(s, d, runner, marker)
            code = d.run_night(t.plan_path)
            child = int(child_file.read_text()); spawned.append(child)
            pgid = json.loads((t.custody / 'night/chain.started').read_text())['pgid']
            print(label, json.dumps({
                'rev': rev, 'exit': code, 'chain_pgid': pgid,
                'chain_group_absent_by_real_pgrep': real(pgid),
                'descendant_pid': child, 'descendant_alive': alive(child),
                'descendant_pgid': os.getpgid(child) if alive(child) else None,
                'descendant_ppid': subprocess.run(['/bin/ps', '-o', 'ppid=', '-p', str(child)],
                                                  capture_output=True, text=True).stdout.strip(),
                'commands_run': calls(runner),
                'chain_exited_written': (t.custody / 'night/chain.exited').exists(),
                'marker_present': marker.exists()}), flush=True)
    finally:
        if child is None and child_file.exists():
            child = int(child_file.read_text())
        if child:
            try: os.kill(child, signal.SIGKILL)
            except ProcessLookupError: pass
        t.tearDown(); t.doCleanups()

def kill_path_case():
    # The driver's own stop (deadline or agent-census abort) ends in
    # _terminate_process_group. Call that production function on a real chain
    # stand-in that holds a separately grouped child and would run on.
    t = NightDriverTests(); t.setUp(); d = t.driver
    child_file = t.root / 'child.pid'; launcher = t.root / 'launcher.py'
    launcher.write_text(launcher_text(child_file, True, linger_s=60))
    night = t.custody / 'night'; night.mkdir(parents=True, exist_ok=True)
    child = None
    try:
        with mock.patch.object(d, '_probe_group_absent',
                               side_effect=lambda pgid, timeout_s=1: d._group_census(pgid, timeout_s)[0]):
            process = subprocess.Popen(['/bin/zsh', '-c', 'exec %s -B %s' % (PY, launcher)],
                                       stdin=subprocess.DEVNULL, start_new_session=True)
            deadline = time.monotonic() + 10
            while not child_file.exists() or not child_file.read_text():
                if time.monotonic() > deadline: raise SystemExit('launcher did not start')
                time.sleep(0.05)
            child = int(child_file.read_text()); spawned.append(child)
            began = time.monotonic()
            proven = d._terminate_process_group(process, night, pgid=process.pid)
            print('KILL_PATH', json.dumps({
                'rev': rev, 'termination_proven': proven, 'seconds': round(time.monotonic() - began, 2),
                'chain_exit': process.poll(), 'descendant_alive': alive(child),
                'descendant_pgid': os.getpgid(child) if alive(child) else None,
                'chain_exited_written': (night / 'chain.exited').exists()}), flush=True)
    finally:
        if child:
            try: os.kill(child, signal.SIGKILL)
            except ProcessLookupError: pass
        t.tearDown(); t.doCleanups()

def recovery_case():
    t = NightDriverTests(); t.setUp(); d = t.driver
    runner = Runner(nt.HEADER + '\n' + line(9900)); marker = t.root / 'pending.json'
    child_file = t.root / 'child.pid'; launcher = t.root / 'launcher.py'
    launcher.write_text(launcher_text(child_file, True))
    night = t.custody / 'night'; night.mkdir(parents=True, exist_ok=True)
    child = None
    try:
        parent = subprocess.Popen([PY, '-B', str(launcher)], stdin=subprocess.DEVNULL, start_new_session=True)
        parent.wait(timeout=10)
        child = int(child_file.read_text()); spawned.append(child)
        real = lambda pgid, timeout_s=1: d._group_census(pgid, timeout_s)[0]
        # The state a killed driver leaves: OFF receipt and marker exist, the
        # chain's identity is published, no chain.exited.
        nt.set_network_time_off(t.custody, 'night-plan', runner=runner, boot_probe=lambda: 'boot',
                                clock=lambda: {'epoch_s': 10000, 'monotonic_s': 10000}, marker_path=marker)
        (night / 'chain.started').write_text(json.dumps({'pid': parent.pid, 'pgid': parent.pid}))
        runner.calls.clear()
        result = nt.recover_network_time(marker_path=marker, runner=runner, boot_probe=lambda: 'boot',
                                         clock=lambda: {'epoch_s': 10620, 'monotonic_s': 10620},
                                         process_group_absent=real)
        print('RECOVERY', json.dumps({
            'rev': rev, 'result': result, 'chain_group_absent_by_real_pgrep': real(parent.pid),
            'descendant_alive': alive(child), 'commands_run': calls(runner),
            'marker_present': marker.exists()}), flush=True)
    finally:
        if child:
            try: os.kill(child, signal.SIGKILL)
            except ProcessLookupError: pass
        t.tearDown(); t.doCleanups()

try:
    driver_case('DRIVER_SAME_GROUP_CONTROL', False)
    driver_case('DRIVER_SEPARATE_GROUP', True)
    kill_path_case()
    recovery_case()
finally:
    for pid in spawned:
        try: os.kill(pid, signal.SIGKILL)
        except ProcessLookupError: pass
    print('SLEEPERS_LEFT', [pid for pid in spawned if alive(pid)])
print('PROBE_D1_COMPLETE')
