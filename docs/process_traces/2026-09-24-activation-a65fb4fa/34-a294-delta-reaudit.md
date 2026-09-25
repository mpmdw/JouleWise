```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "P1–P9 are fixed; two nit-level regression-test gaps remain, with no new production defect found.",
  "workspace": {
    "base_requested": "5ef72338",
    "base_mode": "exact",
    "head_start": "2235eecb16145957206fd28051fe4c75b12cc7bb",
    "head_end": "2235eecb16145957206fd28051fe4c75b12cc7bb",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "nit",
        "file": "tests/test_night_gate.py",
        "line": 881,
        "summary": "The truncation test does not assert that the flag is absent at exactly 50 lines."
      },
      {
        "id": "F2",
        "severity": "nit",
        "file": "tests/test_night_gate.py",
        "line": 904,
        "summary": "The timeout test does not exercise invalid UTF-8, leaving errors='replace' unpinned."
      }
    ],
    "p1_p9": {
      "P1": "FIXED",
      "P2": "FIXED",
      "P3": "FIXED",
      "P4": "FIXED",
      "P5": "FIXED",
      "P6": "FIXED",
      "P7": "FIXED",
      "P8": "FIXED",
      "P9": "FIXED"
    },
    "same_signature": "YES for weak regression coverage (lens 21 NIT-2); NO for an actual recurrence of the probe, consumer, documentation, fixture, or receipt defects."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_gate tests.test_run_night tests.test_night_kinds tests.test_evidence_night tests.test_arm_retry tests.test_magistrate_watchdog tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 667 tests in 692.857s", "FAILED (failures=1, skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_gate.NightGateTests.test_real_git_status_disables_fsmonitor_hook tests.test_night_gate.NightGateTests.test_partial_output_timeout_keeps_status_refusal_evidence tests.test_arm_retry.ArmRetryTests.test_both_document_blocks_are_exact tests.test_arm_retry.ArmRetryTests.test_runbook_describes_t0_clone_status_and_recut_remedy",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 4 tests in 0.315s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 6.654s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "GIT_CONFIG_GLOBAL=/tmp/jw-a294-delta.OklvIW/hostile-gitconfig python3 -B -m unittest tests.test_night_kinds.NightKindTests.test_committed_window_mutant_refused_by_real_prepare",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 52.909s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check 5ef72338 HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The suite's sole failure was the eight-second journal_block watchdog test. It passed in isolation; lens 20 recorded the same suite failure at base and prior head.",
      "needs": "Assess watchdog-test stability separately."
    }
  ]
}
```

## Findings

- **F1 — NIT:** [test_night_gate.py:881](/Users/edr/code/wt-a65fb4fa-a294rev2/tests/test_night_gate.py:881) checks 51 porcelain lines but not the exact 50-line boundary. In a `/tmp` copy, changing the [gate’s `> 50` condition](/Users/edr/code/wt-a65fb4fa-a294rev2/joulewise/night_gate.py:1285) to `>= 50` survived the targeted tests. Direct execution confirmed the current implementation is correct: 49 and 50 lines have no flag; 51 has the flag. Add an absence assertion at 50.

- **F2 — NIT:** [test_night_gate.py:904](/Users/edr/code/wt-a65fb4fa-a294rev2/tests/test_night_gate.py:904) emits only valid UTF-8. Changing either [timeout decoder](/Users/edr/code/wt-a65fb4fa-a294rev2/scripts/run_night.py:360) from `errors="replace"` to strict decoding survived that test. A direct partial-output timeout containing `0xff` confirmed the current runner returns strings with replacement characters. Add invalid-byte stdout and stderr to the regression.

**P1–P9 audit**

| Item | Result | Executed evidence |
|---|---|---|
| P1 | FIXED | Clean, dirty, and failed status receipts each cited the probe in C5; removing the citation failed the clean-pass test. |
| P2 | FIXED | With a configured hook, the production runner created a marker without the override and did not create it with `core.fsmonitor=false`. Removing the override failed the real-Git test. |
| P3 | FIXED | The executed partial-output timeout retained string stdout and stderr through the gate’s `night_probe_error` evidence. Removing either decode failed the test. |
| P4 | FIXED | [arm_retry.py:42](/Users/edr/code/wt-a65fb4fa-a294rev2/joulewise/arm_retry.py:42) has the exact requested text. `render_policy()` generates both marked document blocks; their byte-for-byte sync test passed, and a mutated block failed it. |
| P5 | FIXED | The [runbook passage](/Users/edr/code/wt-a65fb4fa-a294rev2/docs/phase_2/derivation_night_runbook.md:770) matches the code’s HEAD-then-status order, untracked-file and fsmonitor settings, refusal codes, and re-cut remedy. Its focused test passed. |
| P6 | FIXED | Six-line test shows the first five in detail and excludes the sixth; removing that cap failed it. |
| P7 | FIXED | The fake returned a dirty table result for another root; broadening its matcher failed [the new test](/Users/edr/code/wt-a65fb4fa-a294rev2/tests/test_run_night.py:370). |
| P8 | FIXED | Removing either T6 commit override failed under hostile signing or hook configuration. The A295 committed-mutant test passed with that hostile global configuration. |
| P9 | FIXED | A failed status serialized the measured field as JSON `null` while retaining refusal evidence. Detail uses semicolons; direct 49/50/51-line checks confirmed the cap and flag behavior. The null, cap, flag, and detail mutations were caught except F1’s exact-boundary mutation. |

The fix-round diff showed no additional production behavior or refusal-text change outside P1–P9. **Same-signature result:** YES for weak test coverage, repeating lens 21’s NIT-2 class. NO for an actual repeat of lens 20’s missing citation, fsmonitor side effect, or lost timeout evidence, and NO for lens 21’s missed text consumer, stale runbook, broad fake, fixture, or receipt-shape classes.

## Residual risk

The named suite’s only failure was the `journal_block` external watchdog timeout; its isolated replay passed. Lens 20 had reproduced that failure at both base and prior head. Linux CI was not run. The repository remained clean.