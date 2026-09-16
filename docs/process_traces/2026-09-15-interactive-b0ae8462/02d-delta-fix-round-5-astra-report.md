```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FINDINGS: early refusal can restore a stale signal mask; both reversions and the trap are pinned, all six module runs pass, and both ruled predicates return NO.",
  "workspace": {"base_requested":"ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a","base_mode":"exact","head_start":"ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a","head_end":"ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a","upstream_end":null,"branch":null},
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FINDINGS",
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "location": "joulewise/night_agent_install.py:334,418,429-432",
        "title": "Early refusal restores a stale construction-time signal mask",
        "evidence": "Construct Transaction with an empty mask, block SIGUSR1 before run(), and supply an existing .plist.prior. run() exits 3 before installing handlers, but leaves an empty mask instead of the run-entry {SIGUSR1}. All three dispositions remain correct.",
        "recommendation": "Capture the run-entry mask before validation can refuse, and add a regression for changing the mask between construction and an early refusal. Immediate construction/run cases pass."
      }
    ],
    "reversions": "F1 deletion RED/GREEN; F3 production-only reversion RED/GREEN; naive unwind old_mask trap RED/GREEN. The existing F3 regression kills the trap at its entry-mask assertion.",
    "mask_hygiene": {
      "entry_masks": [[],["SIGHUP","SIGUSR1"]],
      "passed_for_each_mask": {"committed":0,"signal_rollback":143,"refusal_before_handlers":3,"uninstall":0,"uninstall_retained":4,"uninstall_repeated_signals":0,"uninstall_ioerror":1},
      "assertions": "All 14 cases preserve the entry mask and INT/TERM/HUP dispositions. The additional changed-since-construction refusal fails mask equality only (R1)."
    },
    "module_modes": "Serial foreground with default dispositions; serial inherited SIG_IGN on SIGINT and SIGQUIT, matching background-shell inheritance.",
    "class_1": "NO",
    "class_2": "NO",
    "executed_predicate_cases": {
      "count": 32,
      "clock_cases": "Open commit; selected-close-first and install-close-first at 160, 161, and 221 against minimum close 160: all six boundary cases exit 2. Cleanup control commits at engine clock read 100 < 160, then advances the observer clock to 9999 and exits 0.",
      "liveness_cases": "Both labels: failed bootstrap with and without load effect; INT/TERM/HUP after bootstrap effect. Verification UNKNOWN. Retained rollback for 9/64/112/wrong-label-113/timeout. Bootout rc0 that remains loaded exits 4 during rollback and uninstall. Successful and UNKNOWN uninstall. Untouched pre-existing loaded/missing-plist states in admission, prior refusal, render, and unsuccessful uninstall.",
      "instrumentation": "Records the value returned to the actual engine _commit clock call, launchd attempts, and actual label/plist mutations. Successful installation has no launchd mutation after that clock read."
    },
    "census": {
      "iw_initial_count": 9,
      "iw_final_count": 50,
      "observed_working_directories": ["/Users/edr/code/JouleWise-wt-iw-txn"],
      "scratch_owned_iw_found": [],
      "process_verification": "Unavailable: ps denied; concurrent temporary-directory activity prevents global attribution."
    },
    "workspace_check": "Original worktree remains clean at the requested HEAD. Canonical baseline digest verified. Scratch production restored byte-for-byte. No full suite, real launchctl bootstrap/bootout, or additional worktree."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B delta5-audit/reversions.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta5-copy",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "F1-red: exit=1",
          "AssertionError: 3 != 0 : ",
          "Ran 1 test in 1.510s",
          "FAILED (failures=1)",
          "F1-green: exit=0",
          "Ran 1 test in 0.965s",
          "OK",
          "F3-red: exit=1",
          " : handler must block all transaction signals before unwinding",
          "Ran 1 test in 0.708s",
          "FAILED (failures=1)",
          "F3-green: exit=0",
          "Ran 1 test in 0.739s",
          "OK",
          "trap-red: exit=1",
          "AssertionError: Items in the second set but not the first:",
          "<Signals.SIGHUP: 1>",
          "<Signals.SIGINT: 2>",
          "<Signals.SIGTERM: 15>",
          "Ran 1 test in 0.891s",
          "FAILED (failures=1)",
          "trap-green: exit=0",
          "Ran 1 test in 0.671s",
          "OK",
          "production restored sha256=9697d7264175b3a806c870185b9e4d36d300e5962b03e7eefb35a286d7244226"
        ]
      },
      "expected": {"exit_code":0,"tail_regex":"production restored sha256="}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B delta5-audit/modules.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta5-copy",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "END foreground tests.test_night_agent_install rc=0",
          "Ran 37 tests in 622.407s",
          "OK",
          "END foreground tests.test_install_night_agent rc=0",
          "Ran 47 tests in 59.178s",
          "OK",
          "END foreground tests.test_run_night rc=0",
          "Ran 101 tests in 20.699s",
          "OK",
          "END inherited_SIG_IGN tests.test_night_agent_install rc=0",
          "Ran 37 tests in 624.807s",
          "OK",
          "END inherited_SIG_IGN tests.test_install_night_agent rc=0",
          "Ran 47 tests in 54.002s",
          "OK",
          "END inherited_SIG_IGN tests.test_run_night rc=0",
          "Ran 101 tests in 20.079s",
          "OK"
        ]
      },
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B delta5-audit/probes.py hygiene",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta5-copy",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "HYGIENE {\"case\": \"refusal_changed_since_construction\", \"entry_mask\": [\"SIGUSR1\"], \"exit_mask\": [], \"rc\": 3, \"dispositions_restored\": true, \"ok\": false}",
          "ASSERTION_FAILED AssertionError(('mask differs', ['SIGUSR1'], []))",
          "HYGIENE_SUMMARY passed=14 failed=1"
        ]
      },
      "expected": {"exit_code":0,"tail_regex":"HYGIENE_SUMMARY passed=15 failed=0"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B delta5-audit/probes.py predicates",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/delta5-copy",
      "observed": {"result":"pass","exit_code":0,"tail":["EXECUTED_CASES 32","class_1: NO","class_2: NO"]},
      "expected": {"exit_code":0,"tail_regex":"class_2: NO"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "GIT_OPTIONAL_LOCKS=0 git status --short --branch; GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD; GIT_OPTIONAL_LOCKS=0 git diff --exit-code",
      "cwd": "/Users/edr/code/JouleWise-wt-delta4-txn",
      "observed": {"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a"]},
      "expected": {"exit_code":0,"tail_regex":"ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "ps was denied. The fallback ls /private/tmp | grep iw- census changed concurrently: nine initial entries disappeared; a new capability entry disappeared; later 50 iw entries were present. Inspected published plists identify JouleWise-wt-iw-txn, with no scratch-copy-owned entry found. Other non-iw additions are unattributed. Process leak freedom cannot be certified.",
      "needs": "Lead-controlled process census if required; preserve foreign temporary entries."
    }
  ]
}
```

## Findings

- **R1 — should_fix:** Capture the mask at `run()` entry before an early refusal can occur, and add the changed-mask refusal regression.

## Residual risk

Concurrent `/tmp` activity and denied process listing prevent a definitive process-leak census.