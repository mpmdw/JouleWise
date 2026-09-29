# Cold gate A1 probe: what each candidate proof can and cannot see.
import sys, os, pathlib, tempfile, json, subprocess, signal, time, shutil
scratch = pathlib.Path('/tmp/cg-ntpfix2-d528efb2')
root = scratch / 'new'
sys.path.insert(0, str(root)); os.chdir(root)
work = pathlib.Path(tempfile.mkdtemp(dir=scratch / 'tmp'))
from joulewise import quiet_predicate_campaign as qpc
from joulewise import network_time_window as nt
from tests.test_network_time_window import WindowTests, line

PY = '/opt/homebrew/bin/python3'
spawned = []
def alive(pid):
    try: os.kill(pid, 0); return True
    except ProcessLookupError: return False

# A sleeper script with a neutral, recognisable name stands in for a capture program.
signature = 'cgprobe_capture_standin.py'
standin = work / signature
standin.write_text('import time\ntime.sleep(45)\n')

def orphan(journal=None):
    """Parent starts the stand-in in its own session (production call shape),
    optionally journals it the way production does, then exits."""
    pid_file = work / ('child-%d.pid' % len(spawned))
    code = ("import subprocess,pathlib,sys,time\n"
            "sys.path.insert(0,%r)\n"
            "from joulewise.quiet_predicate_campaign import append_event\n"
            "p=subprocess.Popen([%r,'-B',%r],stdin=subprocess.DEVNULL,start_new_session=True)\n"
            "j=%r\n"
            "if j: append_event(pathlib.Path(j),{'kind':'collector','pgid':p.pid,'epoch_s':time.time()})\n"
            "pathlib.Path(%r).write_text(str(p.pid))\n"
            % (str(root), PY, str(standin), str(journal) if journal else '', str(pid_file)))
    parent = subprocess.Popen([PY, '-B', '-c', code], stdin=subprocess.DEVNULL, start_new_session=True)
    parent.wait(timeout=15)
    child = int(pid_file.read_text()); spawned.append(child)
    return parent.pid, child

try:
    # --- Form (a): the registry production already writes -------------------
    journal = work / 'evidence_processes.jsonl'; journal.touch()
    chain_pid, child = orphan(journal)
    groups = qpc.process_groups(journal)
    print('FORM_A_JOURNALED', json.dumps({
        'journal_rows': [json.loads(x) for x in journal.read_text().splitlines()],
        'groups_from_journal': sorted(groups), 'child_pgid': os.getpgid(child),
        'groups_absent': {str(k): v for k, v in qpc.groups_absent(groups).items()},
        'chain_group_absent': qpc.group_absent(chain_pid)}), flush=True)
    # The gap: killed between Popen (line 1610) and the journal append (1612).
    journal2 = work / 'evidence_processes_gap.jsonl'; journal2.touch()
    chain_pid2, child2 = orphan(None)
    groups2 = qpc.process_groups(journal2)
    print('FORM_A_UNJOURNALED_GAP', json.dumps({
        'groups_from_journal': sorted(groups2), 'child_alive': alive(child2),
        'registry_would_say_all_absent': all(qpc.groups_absent(groups2).values())}), flush=True)

    # --- Form (c): one process-table snapshot -------------------------------
    snap = subprocess.run(['/bin/ps', '-axo', 'pid=,ppid=,pgid=,sess=,command='],
                          capture_output=True, text=True, timeout=5)
    rows = []
    for text in snap.stdout.splitlines():
        f = text.split(None, 4)
        if len(f) == 5 and f[0].isdigit():
            rows.append({'pid': int(f[0]), 'ppid': int(f[1]), 'pgid': int(f[2]), 'sess': f[3], 'command': f[4]})
    by_pid = {r['pid']: r for r in rows}
    def ancestry(pid):
        seen = []
        while pid in by_pid and pid not in seen and pid > 1:
            seen.append(pid); pid = by_pid[pid]['ppid']
        return seen
    mine = by_pid.get(child2)
    print('FORM_C_SNAPSHOT', json.dumps({
        'ps_exit': snap.returncode, 'rows': len(rows),
        'distinct_sess_values': sorted({r['sess'] for r in rows})[:5],
        'orphan_row': mine,
        'orphan_ancestry_reaches_chain': chain_pid2 in ancestry(child2),
        'found_by_group_of_chain': [r['pid'] for r in rows if r['pgid'] == chain_pid2],
        'found_by_command_signature': [r['pid'] for r in rows if signature in r['command']],
        'both_orphans_found_by_signature': {child, child2} <= {r['pid'] for r in rows if signature in r['command']},
    }), flush=True)
    began = time.monotonic()
    subprocess.run(['/bin/ps', '-axo', 'pid=,ppid=,pgid=,command='], capture_output=True, timeout=5)
    print('FORM_C_COST_S', round(time.monotonic() - began, 3), flush=True)
finally:
    for pid in spawned:
        try: os.kill(pid, signal.SIGKILL)
        except ProcessLookupError: pass
    time.sleep(0.2)
    print('SLEEPERS_LEFT', [pid for pid in spawned if alive(pid)])

# --- What the verdict function does with a capture the query overlapped -----
t = WindowTests(); t.setUp()
try:
    t.query(line(9900))                       # a valid run that started at 10620
    t.first = {'epoch_s': 10600, 'monotonic_before_s': 10600}
    t.last = {'epoch_s': 10610, 'monotonic_before_s': 10610}
    ended_before = nt.capture_verdict(t.window, t.first, t.last)
    t.last = {'epoch_s': 10650, 'monotonic_before_s': 10650}   # still recording at the query
    still_running = nt.capture_verdict(t.window, t.first, t.last)
    t.last = {'epoch_s': 10619.5, 'monotonic_before_s': 10619.5}  # ended 0.5 s before the query
    half_second = nt.capture_verdict(t.window, t.first, t.last)
    print('VERDICT_BOUND', json.dumps({'capture_ended_10_s_before_query': ended_before,
                                       'capture_still_running_at_query': still_running,
                                       'capture_ended_half_second_before_query': half_second}))
finally:
    t.doCleanups()
shutil.rmtree(work, ignore_errors=True)
print('PROBE_FORMS_COMPLETE')
