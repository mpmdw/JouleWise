```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the ruled teardown exception catch; regression and mutation checks pass, but the full transaction module had two failures that passed on focused replay.",
  "workspace": {
    "base_requested": "4114349aed35a84e305dce7be636c5fde65b1e3b",
    "base_mode": "exact",
    "head_start": "4114349aed35a84e305dce7be636c5fde65b1e3b",
    "head_end": "4114349aed35a84e305dce7be636c5fde65b1e3b",
    "upstream_end": "4114349aed35a84e305dce7be636c5fde65b1e3b",
    "branch": "feat/2026-09-15-install-windows-transactional"
  },
  "pathspec": [
    "joulewise/night_agent_install.py",
    "tests/test_night_agent_install.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B /private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6c-mut/must_die.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RED rc=1",
          "RuntimeError: teardown witness",
          "Ran 1 test in 0.611s",
          "FAILED (errors=1)",
          "GREEN rc=0",
          "Ran 1 test in 0.612s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "RED rc=1[\\s\\S]*RuntimeError: teardown witness[\\s\\S]*FAILED \\(errors=1\\)[\\s\\S]*GREEN rc=0[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 'VERIFIED' != 'VALIDATED'",
          "- VERIFIED",
          "+ VALIDATED",
          "----------------------------------------------------------------------",
          "Ran 48 tests in 594.306s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 48 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 51 tests in 51.115s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 51 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install.TransactionTests.test_retention_product",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 185.393s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test[\\s\\S]*OK"
      }
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The full transaction module failed two test_retention_product subtests before VERIFIED. The entire affected test passed on focused replay without edits. A clean full-module result is not established; the original failures' cause remains unconfirmed.",
      "needs": "Lead rerun tests.test_night_agent_install; investigate admission-query failures if they recur before accepting verification."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The existing synthesis Q5 execution lens under both interpreters, fresh delta audit, and lead full-suite replay remain lead-owned gates.",
      "needs": "Complete the existing final verification gates and add the new warning to the runbook table."
    }
  ]
}
```

## Change

Hunks: installer lines 7–8 document the warning; lines 428–430 implement the prescribed catch. Regression at test line 1242 requires return 1, RETAINED state, preserved plists and sidecars after partial teardown, restored signal state, and no traceback.

Exact warning format: `teardown failed; retained: {}: {}`  
Regression output: `teardown failed; retained: RuntimeError: teardown witness`

`run()` and uninstall are unchanged. Baseline digest verified; final scope check returned `SCOPE_OK`. No commit made.

## Verification notes

Both modules ran sequentially in the foreground. Mutation ran only in the designated `cp -R` copy.

The two failing matrix cells were `commit_refusal`, respectively night/hang/no-priors and deadman/rc9/priors. Both stopped at `VALIDATED`. Their complete matrix passed on replay; subprocess timing is only a hypothesis.

Next exact step: lead replay of the transaction module, followed by the outstanding final verification gates.