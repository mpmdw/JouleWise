# Red-by-deletion (A1 §7.3 row 3) in the scratch worktree JouleWise-wt-ntp-n1d2x-del (head 36e8ba6e).
# Each case edits one production file, runs its named tests, then restores the file with git.
import subprocess, sys, pathlib, json
W = pathlib.Path('/private/tmp/claude-501/-Users-edr-code-JouleWise/ff50b201-b458-48cc-8d86-bb1b4bb19e19/scratchpad/n1delta3/mut')
RN, NT = 'scripts/run_night.py', 'joulewise/network_time_window.py'
T = 'tests.test_run_night.NightDriverTests.'; W_ = 'tests.test_network_time_window.WindowTests.'
CASES = [
 ('P1_in_proof', [(RN, "    if not p1:\n        return False, {\"check\": \"P1\", \"pgid\": pgid, \"census\": p1_lines}\n", "")],
  [T+'test_live_chain_group_cannot_prove_p1', T+'test_recovery_withholds_on_while_same_group_child_without_signature_lives',
   T+'test_same_group_live_child_without_signature_blocks_query_and_on', T+'test_same_group_live_child_blocks_query_and_on']),
 ('P1_in_proof_and_post_exit_census', [(RN, "    if not p1:\n        return False, {\"check\": \"P1\", \"pgid\": pgid, \"census\": p1_lines}\n", ""),
                                       (RN, "        exit_code = process.wait()\n        if not _probe_group_absent(pgid):", "        exit_code = process.wait()\n        if False:")],
  [T+'test_same_group_live_child_without_signature_blocks_query_and_on', T+'test_same_group_live_child_blocks_query_and_on']),
 ('P2', [(RN, "    unproved = {group: lines for group, (absent, lines) in census.items() if not absent}\n",
          "    unproved = {}\n")],
  [T+'test_journaled_detached_capture_without_path_signature_blocks_by_registry', T+'test_journaled_detached_capture_blocks_query_and_on']),
 ('P3', [(RN, "    return not matches, {\"check\": \"P3\", \"matches\": matches}\n", "    return True, {\"check\": \"P3\", \"matches\": []}\n")],
  [T+'test_unjournaled_detached_capture_blocks_query_and_on', T+'test_sampler_named_detached_capture_outside_night_blocks_query_and_on']),
 ('C5', [(NT, "            else:\n                if capture_proof is None:\n                    return \"chain_unproved\"\n                try:\n                    proved, _evidence = capture_proof(marker, pgid)\n                except Exception:\n                    return \"chain_unproved\"\n                if not proved:\n                    return \"chain_unproved\"\n", ""),
         (NT, "        if isinstance(pgid, int) and pgid > 0:\n            try:\n                proved, _evidence = capture_proof(marker, pgid)\n            except Exception:\n                return \"chain_unproved\"\n            if not proved:\n                return \"chain_unproved\"\n", "")],
  [T+'test_recovery_from_run_night_waits_for_detached_child_then_restores', T+'test_dead_man_both_recovery_calls_withhold_on_while_child_lives']),
 ('never_launched_claim', [(RN, "        _write_all(descriptor, _json_bytes({\n            \"pid\": None, \"pgid\": None, \"epoch_s\": time.time(),\n            \"popen_attempted\": False,\n            \"launch_error\": \"never_launched: network_time_off_unproved\",\n        }))\n", "        pass\n")],
  [T+'test_wrong_off_and_failed_immediate_on_recover_from_never_launched_claim', T+'test_unsavable_off_and_failed_immediate_on_recover_from_never_launched_claim']),
 ('E2_replace', [(RN, "        os.replace(temporary, path)\n", "")],
  [T+'test_deadline_stop_with_detached_child_blocks_query_and_on', T+'test_census_stop_with_detached_child_blocks_query_and_on']),
]

import re
only = sys.argv[1:]
for name, edits, tests in CASES:
    if only and name not in only: continue
    originals = {}
    for f, old, new in edits:
        p = W / f; s = p.read_text(); originals.setdefault(f, s)
        assert s.count(old) == 1, (name, f, s.count(old))
        p.write_text(s.replace(old, new))
    r = subprocess.run(['/opt/homebrew/bin/python3', '-B', '-m', 'unittest', '-v', *tests], cwd=W, capture_output=True, text=True)
    for f, s in originals.items(): (W / f).write_text(s)
    lines = r.stderr.splitlines()
    verdicts = [l for l in lines if re.search(r' \.\.\. (ok|FAIL|ERROR|skipped.*)$', l)]
    errs = [l for l in lines if l.startswith(('AssertionError', 'FileNotFoundError', 'Traceback')) or re.match(r'^[A-Za-z]+Error:', l)]
    print(f'== DELETION {name}: exit={r.returncode} {lines[-1] if lines else ""}')
    for v in verdicts: print('   ', v[-160:])
    for e in errs: print('   !', e[:200])
