```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented S1–S5 and all requested nits; both modules pass and all six S2 guard mutants are killed.",
  "workspace": {
    "base_requested": "2daf2b0b8892a9ad898a4fd87b7164963adee691",
    "base_mode": "exact",
    "head_start": "2daf2b0b8892a9ad898a4fd87b7164963adee691",
    "head_end": "2daf2b0b8892a9ad898a4fd87b7164963adee691",
    "upstream_end": "2daf2b0b8892a9ad898a4fd87b7164963adee691",
    "branch": "feat/2026-09-15-arm-retry-class"
  },
  "pathspec": [
    "joulewise/arm_retry.py",
    "tests/test_arm_retry.py",
    "docs/phase_2/derivation_night_runbook.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_arm_retry",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 27 tests in 1.985s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 27 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 59 tests in 3.575s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 59 tests[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "/usr/bin/python3 -B -c 'from joulewise import arm_retry; print(\"arm_retry import OK\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["arm_retry import OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "arm_retry import OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B /private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a172-fix3-mut/probe_s2.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "green_restored exit=0",
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.083s",
          "",
          "OK",
          "S2: 6/6 guard mutants killed; restored test GREEN"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "S2: 6/6 guard mutants killed; restored test GREEN"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Change

Hunks implemented:

- Module `@@ -21,7 +21,7 @@`: watchdog description references `UNCERTAIN_STATES`; rendered bytes unchanged.
- Tests `@@ -162,11 +162,6 @@`: deleted the foreign `INSTALL_SPANS` pin.
- Tests `@@ -185,6 +180,31 @@`: added one S2 cell covering three invalid histories and each candidate-head field.
- Runbook `@@ -1490,6 +1490,8 @@`: added the exact first-arm sentence.
- Runbook `@@ -1616,11 +1618,16 @@`: supplied `cp -n` then `cmp`; named the repeated §0.x checks.
- Runbook `@@ -1665,7 +1672,8 @@`: added the exact outcome/history sentence.
- Runbook `@@ -1907,8 +1915,8 @@`: replaced the obsolete span requirement with the checks actually applied.

Both marked blocks remain byte-identical to `render_policy()`; NIGHT_HANDBACK needed no edit. Baseline digest verified. No commit made.

## Verification notes

Mutation probes ran exclusively in the designated `cp -R` scratch copy. Each runs the new S2 cell:

| Dropped guard | Exit | RED tail |
|---|---:|---|
| Abort before start | 1 | `FAILED (failures=1)` |
| Abort in future | 1 | `FAILED (failures=1)` |
| Attempt overlap | 1 | `FAILED (failures=1)` |
| Candidate repo head | 1 | `FAILED (failures=1)` |
| Candidate measurement head | 1 | `FAILED (failures=1)` |
| Entire candidate-head guard | 1 | `FAILED (failures=2)` |

Before mutation and after restoration: exit 0, `OK`. Probe script and individual logs remain in the scratch copy.

Verification stayed within the two authorized modules. Next step: lead final diff review and verification.