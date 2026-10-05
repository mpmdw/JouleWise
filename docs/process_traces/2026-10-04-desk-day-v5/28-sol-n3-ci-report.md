```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Fixed N3's CI error with a custody-input skip and diagnostic assertion; focused verification passed.",
  "workspace": {
    "base_requested": "7f7cbec6",
    "base_mode": "exact",
    "head_start": "7f7cbec652a1ed20a7235cbaf5b1ea63ce1fff82",
    "head_end": "7f7cbec652a1ed20a7235cbaf5b1ea63ce1fff82",
    "upstream_end": "7f7cbec652a1ed20a7235cbaf5b1ea63ce1fff82",
    "branch": "tests/2026-10-03-g2a-attach-guard-tests"
  },
  "pathspec": ["tests/test_harvest_g2a_window.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-n3ci PYTHONDONTWRITEBYTECODE=1 AUDIT_LABEL=local python3.13 -S /tmp/dd5-n3ci/audit_inputs.py > /tmp/dd5-n3ci/local-test.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK", "INPUT_AUDIT /tmp/dd5-n3ci/inputs-local.json paths 918"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-n3ci PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3.13 -S -m unittest -v tests.test_harvest_g2a_window.G2aHarvestTests.test_real_passed_bracket_after_nonzero_acceptance_cutoff_selects",
      "cwd": "/tmp/dd5-n3ci/repo",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-n3ci PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3.13 -S -m unittest -v tests.test_harvest_g2a_window > /tmp/dd5-n3ci/archive-module.log 2>&1",
      "cwd": "/tmp/dd5-n3ci/repo",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 63 tests[\\s\\S]*OK \\(skipped=1\\)"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-n3ci PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= python3.13 -S -m unittest -v tests.test_harvest_g2a_window > /tmp/dd5-n3ci/worktree-module.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 63 tests[\\s\\S]*OK \\(skipped=1\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-n3ci PYTHONDONTWRITEBYTECODE=1 MISSING_AT_HARVEST=1 AUDIT_LABEL=refusal python3.13 -S /tmp/dd5-n3ci/audit_inputs.py",
      "cwd": "/tmp/dd5-n3ci/repo",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "harvest verdict=REFUSED fault={'type': 'HarvestRefusal', 'detail': 'ledger_authentication_failed'} cause_codes=['ledger_authentication_failed']"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "harvest verdict=REFUSED.*ledger_authentication_failed"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-n3ci PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests > /tmp/dd5-n3ci/full-suite.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical suite was started but deliberately interrupted before completion. Hosted Linux CI was not executed.",
      "needs": "Lead rerun the canonical suite and verify PR #469 CI."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Git staging failed because the sandbox cannot create the linked worktree's index.lock. Changes remain uncommitted; nothing was pushed.",
      "needs": "Commit the test change from a session with writable Git metadata."
    }
  ]
}
```

## Change

The tracked historical ledger references **190 external custody artifacts** under Ed’s absolute iCloud backup path. They exist locally but are absent on hosted CI. Missing custody produces `calibration_ledger_custody_invalid`, which harvest reports as `ledger_authentication_failed`.

Added `skipUnless` with reason `lead-reviewed D-079 import custody inputs are unavailable`. Its condition evaluates true locally and false with backup access disabled. The test now asserts the verdict and prints fault/cause diagnostics before reading `bracket.json`.

The [complete input inventory](/tmp/dd5-n3ci/input-inventory.md) lists 115 tracked source/data files and all 190 external artifacts. The [918-path audit](/tmp/dd5-n3ci/inputs-local.json) records each individual `git ls-files --error-unmatch` result.

## Verification notes

The missing-custody reproduction intentionally fails with the informative assertion. An initial override applied to the entire test hit the issuance guard; restricting it to harvest reproduced the reported failure.

The archive contained tracked HEAD bytes plus the patched test. A scratch Git repository satisfied the existing fixture’s `rev-parse` call.

## Residual risk

The canonical suite remains incomplete. Next step: lead runs `python3 -m unittest discover -s tests`, commits the change, and verifies PR #469 CI.