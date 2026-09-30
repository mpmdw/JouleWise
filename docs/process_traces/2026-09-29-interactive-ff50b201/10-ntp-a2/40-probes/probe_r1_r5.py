"""Cold-gate A2 probes: R1..R5, NIT-2, NIT-1, on the scratch archive of 36e8ba6e.
No sudo, no systemsetup, no sntp, no powermetrics, no /usr/bin/log. pgrep/ps only list.
"""
import sys, json, os, subprocess, tempfile, time
import os as _os
CAND = _os.environ['CAND']
sys.path.insert(0, CAND)
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from scripts import run_night as d
from joulewise import network_time_window as nt
from joulewise import quiet_predicate_campaign as q
from tests.test_network_time_window import Runner

SCR = Path('/private/tmp/claude-501/-Users-edr-code-JouleWise/ff50b201-b458-48cc-8d86-bb1b4bb19e19/scratchpad/n1delta3/tmp')
print('CAND_HEAD_FILE', (Path(CAND)/'scripts/run_night.py').stat().st_size)

# ---------- R1: never-launched claim with MISSING keys ----------
print('\n== R1 ==')
with tempfile.TemporaryDirectory(dir=SCR) as td:
    root = Path(td); night = root/'night'; night.mkdir()
    for label, claim in [('missing_both', {'popen_attempted': False}),
                         ('missing_pid', {'pgid': None, 'launch_error': 'failed'}),
                         ('complete_nulls', {'pid': None, 'pgid': None, 'popen_attempted': False}),
                         ('pid_present_int', {'pid': 123, 'pgid': None, 'popen_attempted': False})]:
        marker = root/'pending.json'
        runner = Runner()
        nt.set_network_time_off(root, label, runner=runner, boot_probe=lambda: 'boot', marker_path=marker)
        (night/'chain.started').write_text(json.dumps(claim))
        (night/'chain.exited').write_text('{"launch_failed": true}')
        driver_accepts = d._chain_never_launched(night)
        proof_calls = []
        def proof(marker_, pgid):
            proof_calls.append(pgid); return (False, {'check': 'P3'})
        result = nt.recover_network_time(marker_path=marker, runner=runner, boot_probe=lambda: 'boot',
                                         capture_proof=proof)
        print(f'R1 {label:16s} driver_accepts={driver_accepts!s:5s} recovery={result:14s} '
              f'ON_ran={nt.ON_ARGV in runner.calls!s:5s} proof_called={bool(proof_calls)}')
        for p in (night/'network_time').iterdir(): p.unlink()
        marker.unlink(missing_ok=True)
    # dead-man's own launch_failed predicate (third site), by text of the condition:
    rec = {'launch_error': 'x'}
    print('R1 deadman_predicate_missing_keys_accepts=',
          (isinstance(rec, dict) and rec.get('pid') is None and rec.get('pgid') is None
           and isinstance(rec.get('launch_error'), str) and bool(rec['launch_error'])))

# ---------- R2: batch census, exit 0 with empty output ----------
print('\n== R2 ==')
def snapshot_self_only(_timeout):
    return 0, f'{os.getpid()} 1 python\n888888 {os.getpid()} /bin/ps\n', '', 888888
def listing_exit0_empty(argv, **kw):
    return subprocess.CompletedProcess(argv, 0, '', '')
def listing_exit1_empty(argv, **kw):
    return subprocess.CompletedProcess(argv, 1, '', '')
with mock.patch.object(d.subprocess, 'run', side_effect=listing_exit1_empty), \
     mock.patch.object(d, '_process_snapshot', side_effect=snapshot_self_only):
    print('R2 single_group(pgrep exit1 empty) ->', d._capture_proof_pass({}, 12345, {111}, 1))
def mixed(argv, **kw):
    # P1 single-group census answers exit 1 (empty); the 2-group batch answers exit 0, empty.
    if argv[0].endswith('pgrep') and ',' not in argv[3]:
        return subprocess.CompletedProcess(argv, 1, '', '')
    return subprocess.CompletedProcess(argv, 0, '', '')
with mock.patch.object(d.subprocess, 'run', side_effect=mixed), \
     mock.patch.object(d, '_process_snapshot', side_effect=snapshot_self_only):
    print('R2 two_groups(batch pgrep exit0 EMPTY) ->', d._capture_proof_pass({}, 12345, {111, 222}, 1))
with mock.patch.object(d.subprocess, 'run', side_effect=listing_exit0_empty):  # DELTA3: leak fixed (judge's §0 item 8)
    print('R2 _census_chunk(exit0 empty) direct ->', d._census_chunk([111, 222], 1))
real = subprocess.run(['/usr/bin/pgrep', '-lf', '-g', '999998,999999', '.'], capture_output=True, text=True)
print('R2 real pgrep on two absent groups: exit=', real.returncode, 'stdout_bytes=', len(real.stdout))

# ---------- R3: [K]'s early refusal vs the chain-alive cause ----------
print('\n== R3 ==')
def r3_case(label, pre_write):
    with tempfile.TemporaryDirectory(dir=SCR) as td:
        root = Path(td); night = root/'night'; night.mkdir()
        plan = SimpleNamespace(plan_id='cg-a2-r3', receipt_class='DIAGNOSTIC_NO_PACK', quiet_admission=None)
        (night/'chain.started').write_text('{"pid": 4242, "pgid": 4242}')
        (night/'evidence_processes.jsonl').write_text('')
        (night/'receipt.json').write_text(json.dumps({'plan_id': plan.plan_id, 'conditions': [
            {'condition_id': 'C5', 'status': 'PASS', 'measured': {'payload_kind': 'quiet_predicate_evidence'}}]}))
        pre_write(night, plan)
        # [K] as the driver calls it at :3347 (cleanup_record stubbed: no signals sent here)
        with mock.patch.object(d.night_gate, 'validate_receipt', return_value=[]), \
             mock.patch.object(q, 'cleanup_record', return_value={'cleanup_proven': True}):
            import inspect as _i  # DELTA3: call [K] exactly as this head's driver does
            if 'cleanup_only' in _i.signature(d._evidence_cleanup_error).parameters:
                k = d._evidence_cleanup_error(plan, night, cleanup_only=True); kmode='cleanup_only=True'
            else:
                k = d._evidence_cleanup_error(plan, night); kmode='full'
            print('R3 K call mode:', kmode)
        after_k = [(p.name, json.loads(p.read_text())['refusal']['reason']) for p in d._refusal_paths(night)]
        # the proof fails (P3 match) -> the abort helper, prior=None (chain ended on its own)
        proof = {'check': 'P3', 'matches': [{'pid': 999999, 'command': str(root/'collector.py')}]}
        abort = d._capture_unproved_abort(night, plan, root, None, 'capture process absence could not be proved', proof)
        # the result step as at :3417
        if 'document' not in abort:
            d._write_driver_refusal(night/'refusal.json', plan, abort['reason'], abort['detail'], abort['evidence'])
        result = d._write_result(root, night, plan, 'REFUSED', 1, abort['reason'], 0, 0, None, 0)
        docs = [(p.name, json.loads(p.read_text())['refusal']['reason']) for p in d._refusal_paths(night)]
        for p in d._refusal_paths(night):
            r=json.loads(p.read_text())['refusal']; print('   ', p.name, 'reason=',r['reason'], 'prior_documents=', (r.get('evidence') or {}).get('prior_documents'), 'keys=', sorted(r))
        print(f'R3 {label}: K_returned={k!r}; after_K={after_k}; final docs={docs}; '
              f'result.aborted_reason={result["aborted_reason"]}; refusal_documents={result["refusal_documents"]}')
r3_case('A_chain_left_no_outcome', lambda night, plan: None)
def chain_wrote_own(night, plan):
    q.write_refusal(night, plan, 'probe failed inside the chain')  # the chain's own document (:1602 path)
r3_case('B_chain_wrote_own_refusal', chain_wrote_own)
def outcome_complete(night, plan):
    (night/'evidence_outcome.json').write_text('{"outcome": "complete"}')
r3_case('C_outcome_complete_control', outcome_complete)

# ---------- R4: first pass longer than the window, still proved ----------
print('\n== R4 ==')
with tempfile.TemporaryDirectory(dir=SCR) as td:
    night = Path(td)
    for n in (2, 300, 769):
        groups = set(range(1000, 1000+n))
        (night/'evidence_processes.jsonl').write_text(''.join(json.dumps({'pgid': g})+'\n' for g in groups))
        clock = [0.0]
        def slow_clear(argv, **kw):
            clock[0] += 0.9
            return subprocess.CompletedProcess(argv, 1, '', '')
        def slow_snapshot(t):
            clock[0] += 0.9
            return snapshot_self_only(t)
        with mock.patch.object(d.time, 'monotonic', side_effect=lambda: clock[0]), \
             mock.patch.object(d.time, 'sleep', side_effect=lambda s: None), \
             mock.patch.object(d.subprocess, 'run', side_effect=slow_clear), \
             mock.patch.object(d, '_process_snapshot', side_effect=slow_snapshot):
            out = d._prove_capture_absent({}, 12345, night)
        print(f'R4 groups={n:4d} calls_budget={d._capture_pass_calls(groups)} -> {out} virtual_elapsed={clock[0]:.1f}s window={d.GROUP_CENSUS_WINDOW_S}')

# ---------- R5: the C7 (termination unproved) return path ----------
print('\n== R5 ==')
with tempfile.TemporaryDirectory(dir=SCR) as td:
    root = Path(td); night = root/'night'; night.mkdir()
    plan = SimpleNamespace(plan_id='cg-a2-r5', receipt_class='DIAGNOSTIC_NO_PACK', quiet_admission=None)
    with mock.patch.object(d, '_durable_record'), mock.patch.object(d, '_write_courier_outcome'):
        code = d._finish_reporting(root, night, plan, d.EXIT_REFUSED, None, allow_courier=False,
                                   courier_error='chain termination was not proven')
    print('R5 C7 path exit =', code, '(EXIT_REFUSED=%d, EXIT_COURIER_FAILED=%d)' % (d.EXIT_REFUSED, d.EXIT_COURIER_FAILED))

# ---------- NIT-2: prefix match ----------
print('\n== NIT-2 ==')
paths = {'/Users/edr/code/JouleWise'}
for cmd in ['/bin/zsh /Users/edr/code/JouleWise-wt-other/run.sh', '/bin/zsh /Users/edr/code/JouleWise/run.sh',
            'python3 -B /Users/edr/code/JouleWiseX/x.py', 'vim /Users/edr/code/JouleWise']:
    print(f'NIT2 {d._capture_signature(cmd, paths)!s:5s} <- {cmd}')

# ---------- NIT-1: real proof, real census+sweep, a path-signature sleeper ending on its own ----------
print('\n== NIT-1 ==')
with tempfile.TemporaryDirectory(dir=SCR) as td:
    root = Path(td); mroot = root/'mroot'; mroot.mkdir(); night = root/'night'; night.mkdir()
    sleeper = mroot/'cg_sleeper.py'
    for life, n_groups in ((2.0, 2), (2.0, 0), (0.5, 2)):
        sleeper.write_text(f'import time\ntime.sleep({life})\n')
        # registry of dead groups (pids that cannot exist)
        (night/'evidence_processes.jsonl').write_text(''.join(json.dumps({'pgid': g})+'\n' for g in range(999000, 999000+n_groups)))
        marker = {'measurement_root': str(mroot), 'custody_root': str(root), 'chain_path': str(root/'chain.zsh'),
                  'measurement_root_resolved': str(mroot.resolve()), 'custody_root_resolved': str(root.resolve()),
                  'chain_path_resolved': str((root/'chain.zsh').resolve())}
        child = subprocess.Popen([sys.executable, '-B', str(sleeper)], start_new_session=True,
                                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.monotonic()
        proved, ev = d._prove_capture_absent(marker, 999999, night)  # pgid 999999: an empty group (P1 passes)
        dt = time.monotonic() - t0
        alive = child.poll() is None
        print(f'NIT1 life={life}s groups={n_groups} -> proved={proved} check={ev.get("check")} passes={ev.get("passes")} took={dt:.2f}s child_alive_at_return={alive}')
        try: child.kill()
        except ProcessLookupError: pass
        child.wait()
print('\nPROBES_COMPLETE')
