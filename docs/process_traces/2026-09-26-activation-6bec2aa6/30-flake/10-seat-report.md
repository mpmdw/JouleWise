```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Extended the test child's post-TERM wait while preserving the SIGTERM exit-code and escalation-report assertions.",
  "workspace": {
    "base_requested": "64e39bb937e79c710886acf13fbfab295526aa18",
    "base_mode": "exact",
    "head_start": "64e39bb937e79c710886acf13fbfab295526aa18",
    "head_end": "64e39bb937e79c710886acf13fbfab295526aa18",
    "upstream_end": "64e39bb937e79c710886acf13fbfab295526aa18",
    "branch": "test/2026-09-26-load-join-ladder-flake"
  },
  "pathspec": ["tests/test_sample_quiet_predicate_evidence.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_sample_quiet_predicate_evidence > /private/tmp/jw-load-join-module.log 2>&1; result=$?; tail -n 5 /private/tmp/jw-load-join-module.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["", "----------------------------------------------------------------------", "Ran 79 tests in 35.742s", "", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 79 tests.*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nimport subprocess, sys, time\ncmd=[sys.executable, '-m', 'unittest', 'tests.test_sample_quiet_predicate_evidence.LoadTests.test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child']\nloads=[]; failures=[]; started=time.monotonic()\ntry:\n    loads=[subprocess.Popen(['yes'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for _ in range(12)]\n    for i in range(1,21):\n        run=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=15)\n        if run.returncode: failures.append((i,run.stdout))\n        print(f'ITERATION {i}: {\"PASS\" if run.returncode == 0 else \"RED\"}',flush=True)\nfinally:\n    for p in loads: p.terminate()\n    for p in loads:\n        try: p.wait(timeout=3)\n        except subprocess.TimeoutExpired: p.kill(); p.wait()\n    print('LOAD_PROCESSES_CLEANED='+str(all(p.poll() is not None for p in loads)),flush=True)\nprint(f'Ran 20 iterations under 12 yes processes in {time.monotonic()-started:.1f}s',flush=True)\nprint(f'Failures: {len(failures)}',flush=True)\nfor i,output in failures: print(f'RED {i}: '+ ' | '.join(output.splitlines()[-12:]),flush=True)\nprint('OK' if not failures else 'FAILED',flush=True)\nsys.exit(bool(failures))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ITERATION 20: PASS", "LOAD_PROCESSES_CLEANED=True", "Ran 20 iterations under 12 yes processes in 37.6s", "Failures: 0", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Failures: 0\\nOK$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_git_fixture_maintenance > /private/tmp/jw-load-join-maintenance.log 2>&1; result=$?; tail -n 5 /private/tmp/jw-load-join-maintenance.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".....", "----------------------------------------------------------------------", "Ran 5 tests in 9.316s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 5 tests.*\\n\\nOK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The original failure did not reproduce locally: RED 0/8 with 12 yes processes and RED 0/24 with 24 yes processes. Every load process was reaped.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "The full test module failed in an unrelated collect test; that test also failed when run alone, with its collect subprocess returning 1 and no stderr.",
      "needs": "Lead reruns the full test module in its verification environment."
    }
  ]
}
```

## Change

The worker sends its result and then sleeps for 60 seconds ([test worker](</Users/edr/code/JouleWise-wt-flake-6bec2aa6/tests/test_sample_quiet_predicate_evidence.py:135>)). For that subtest, `join_grace_s=0.2` is the wait **before** TERM. After TERM, `load()` waits **1 second**, then sends KILL if the child is still alive ([join ladder](</Users/edr/code/JouleWise-wt-flake-6bec2aa6/scripts/sample_quiet_predicate_evidence.py:1398>)). Thus the suggested “0.2 seconds after TERM” explanation is incorrect. Scheduling delay during the one-second post-TERM wait can produce `-SIGKILL`; the code does not establish a signal-disposition race.

The diff adds a real spawn-process subclass whose post-TERM `join(1)` waits up to three seconds, and uses it only in this test ([diff location](</Users/edr/code/JouleWise-wt-flake-6bec2aa6/tests/test_sample_quiet_predicate_evidence.py:144>)). `load()` still sends TERM and retains its conditional KILL step. The test still requires `-SIGTERM` and the report’s `worker cleanup escalated` entry ([assertions](</Users/edr/code/JouleWise-wt-flake-6bec2aa6/tests/test_sample_quiet_predicate_evidence.py:859>)).

## Verification notes

The full-module failure was `CollectionTests.test_real_collect_no_power_reaps_all_recorded_workers` at line 498; it also failed alone. The loaded pre-edit replay did not produce a RED, so the reported flake could not be reproduced literally here. No full suite was run.