"""Opus A1 contract refuter: D1 reproduction with the REAL group census (pgrep).

Cases: (1) natural chain exit; (2) agent-census abort (driver SIGTERM/SIGKILL of
the chain's group); (3) recovery. Each chain spawns a harmless sleeper exactly as
joulewise/quiet_predicate_campaign.py:1610 launch() does (Popen with
start_new_session=True, then journal the pgid with append_event). Network-time
commands go through injected runners; no sudo/systemsetup/log/battery.
"""
import sys, os, pathlib, tempfile, json, functools, hashlib, signal, time
from unittest import mock
from contextlib import ExitStack
scratch = pathlib.Path('/tmp/opus-ntpA1-d528efb2'); root = scratch / 'cand'
sys.path.insert(0, str(root)); tempfile.tempdir = str(scratch / 'tmp'); (scratch / 'tmp').mkdir(exist_ok=True)
def guard(event, args):
    if event == 'subprocess.Popen':
        exe, argv, cwd, env = args
        if pathlib.Path(str(exe)).name in {'sudo', 'systemsetup', 'powermetrics', 'ioreg', 'pmset', 'log', 'sntp'}:
            raise AssertionError('FORBIDDEN ' + str(argv))
sys.addaudithook(guard)
from joulewise import network_time_window as nt
from joulewise import quiet_predicate_campaign as qpc
from tests.test_network_time_window import WindowTests, line, Runner
from tests.test_run_night import NightDriverTests, _probe
from joulewise import night_gate

LAUNCHER = """import subprocess, pathlib, sys, time, os
sys.path.insert(0, {root!r})
from joulewise.quiet_predicate_campaign import append_event
journal = pathlib.Path({journal!r})
p = subprocess.Popen(['/opt/homebrew/bin/python3', '-B', '-c', 'import time; time.sleep(45)'],
                     stdin=subprocess.DEVNULL, start_new_session=True)   # = qpc.py:1610
append_event(journal, {{'kind': 'collector', 'pgid': p.pid, 'epoch_s': time.time()}})  # = qpc.py:1612
pathlib.Path({pidfile!r}).write_text(str(p.pid))
time.sleep({linger})
"""

def classify(calls):
    return ['off' if x == nt.OFF_ARGV else 'on' if x == nt.ON_ARGV else 'query' if x[:1] == nt.LOG_PREFIX[:1] else 'boot' for x in calls if x != nt.BOOT_ARGV]

def driver_case(label, linger, census):
    t = NightDriverTests(); t.setUp(); d = t.driver
    runner = Runner(nt.HEADER + '\n' + line(9900)); marker = t.root / 'pending.json'
    night = t.custody / 'night'; journal = night / 'evidence_processes.jsonl'
    pidfile = t.root / 'child.pid'; launcher = t.root / 'launcher.py'
    launcher.write_text(LAUNCHER.format(root=str(root), journal=str(journal), pidfile=str(pidfile), linger=linger))
    t.chain.write_text('exec /opt/homebrew/bin/python3 -B ' + str(launcher) + '\n')
    t.sidecar.write_text(hashlib.sha256(t.chain.read_bytes()).hexdigest() + '\n')
    if census:
        t.source.census_responses = [_probe(night_gate.AGENT_CENSUS_ARGV, exit_code=1)] * 3 + [
            _probe(night_gate.AGENT_CENSUS_ARGV, stdout="agent\n")] * 5
    child = None
    real_absent = lambda pgid, timeout_s=1: d._group_census(pgid, timeout_s)[0]
    try:
        with ExitStack() as s:
            s.enter_context(mock.patch.object(nt, 'RESTORE_PENDING_PATH', marker))
            s.enter_context(mock.patch.object(nt, 'NETWORK_TIME_ENFORCED_KINDS', frozenset({'unknown'})))
            s.enter_context(mock.patch.object(d, 'CENSUS_INTERVAL_S', 1.0))
            for name in ['set_network_time_off', 'set_network_time_on', 'run_window_query', 'recover_network_time']:
                fn = getattr(nt, name)
                s.enter_context(mock.patch.object(nt, name, functools.partial(fn, runner=runner,
                    boot_probe=lambda: 'boot', clock=lambda: {'epoch_s': 10000, 'monotonic_s': 10000})))
            s.enter_context(mock.patch.object(d, '_probe_group_absent', side_effect=real_absent))
            code = d.run_night(t.plan_path)
        child = int(pidfile.read_text())
        os.kill(child, 0)  # raises if the descendant is gone
        started = json.loads((night / 'chain.started').read_text())
        registry = qpc.process_groups(journal) if journal.exists() else set()
        registry_absent = qpc.groups_absent(registry) if registry else {}
        print(label, json.dumps({
            'driver_exit': code, 'chain_pgid': started['pgid'],
            'chain_group_absent_by_real_pgrep': real_absent(started['pgid']),
            'descendant_pid': child, 'descendant_pgid': os.getpgid(child), 'descendant_sid': os.getsid(child),
            'descendant_ppid_now': int(os.popen(f'/bin/ps -o ppid= -p {child}').read().strip() or -1),
            'descendant_alive_after_driver': True,
            'network_time_calls': classify(runner.calls),
            'chain_exited_written': (night / 'chain.exited').exists(),
            'marker_present_after': marker.exists(),
            'journal_registry': sorted(registry),
            'form_a_registry_census_would_show_absent': registry_absent,
        }), flush=True)
    finally:
        if child is None and pidfile.exists():
            child = int(pidfile.read_text())
        if child:
            try: os.killpg(child, signal.SIGKILL)
            except ProcessLookupError: pass
        t.tearDown(); t.doCleanups()

def recovery_case():
    import subprocess
    case = WindowTests(); case.setUp(); child = None
    from importlib import util
    spec = util.spec_from_file_location('rn', str(root / 'scripts/run_night.py'))
    try:
        pfile = case.root / 'child.pid'
        cmd = ("import pathlib,subprocess;p=subprocess.Popen(['/opt/homebrew/bin/python3','-B','-c','import time;time.sleep(45)'],"
               "start_new_session=True);pathlib.Path(" + repr(str(pfile)) + ").write_text(str(p.pid))")
        parent = subprocess.Popen(['/opt/homebrew/bin/python3', '-B', '-c', cmd], start_new_session=True); parent.wait(timeout=10)
        child = int(pfile.read_text())
        sys.path.insert(0, str(root / 'scripts'))
        import importlib; rn = importlib.import_module('scripts.run_night')
        (case.root / 'night/chain.started').write_text(json.dumps({'pid': parent.pid, 'pgid': parent.pid}))
        (case.root / 'night/chain.exited').unlink()
        case.runner.log = nt.HEADER + '\n' + line(9900)
        result = nt.recover_network_time(marker_path=case.marker, runner=case.runner, boot_probe=lambda: 'boot-1',
            clock=lambda: {'epoch_s': 10620, 'monotonic_s': 10620}, process_group_absent=rn._probe_group_absent)
        os.kill(child, 0)
        print('RECOVERY_REAL_PGREP', json.dumps({'result': result, 'descendant_alive': True,
            'descendant_pgid': os.getpgid(child), 'chain_pgid': parent.pid,
            'network_time_calls': classify(case.runner.calls), 'marker_present': case.marker.exists()}), flush=True)
    finally:
        if child:
            try: os.killpg(child, signal.SIGKILL)
            except ProcessLookupError: pass
        case.doCleanups()

if __name__ == '__main__':
    driver_case('D1_NATURAL_EXIT', linger=0.5, census=False)
    driver_case('D1_CENSUS_ABORT', linger=40, census=True)
    recovery_case()
    print('PROBE_D1_COMPLETE')
