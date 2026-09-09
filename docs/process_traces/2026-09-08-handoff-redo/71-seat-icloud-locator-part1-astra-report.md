```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_SCOPE: bounded _custody_state and disabled-backup handling implemented; broader custody probes remain.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "head_end": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-custody-locator"
  },
  "pathspec": [
    "joulewise/calibration_ledger.py",
    "tests/test_calibration_ledger_custody.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' python3 -m unittest tests.test_calibration_ledger_custody tests.test_calibration_ledger > /private/tmp/ICLOUD-CUSTODY-LOCATOR-01-tests-rerun.log 2>&1\ncustody_test_rc=$?\nprintf '\\nrc=%s\\n' \"$custody_test_rc\" >> /private/tmp/ICLOUD-CUSTODY-LOCATOR-01-tests-rerun.log\ntail -8 /private/tmp/ICLOUD-CUSTODY-LOCATOR-01-tests-rerun.log\nexit \"$custody_test_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=1)", "", "rc=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)\\s+rc=0"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: calibration_bracketing._candidate_from_observation passes custody_locator to load_calibration_candidate, which performs unbounded resolve and authentication reads outside the allowlist. No out-of-scope files were modified.",
      "needs": "Expand scope to the requested paths and resume complete probe coverage."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Acceptance remains incomplete: nonempty backup-root overrides and other custody reads, including artifact_hashes, _custody_reasons, historical reauthentication, and finalization rereads, remain unbounded.",
      "needs": "Complete integrated custody-read handling and regressions after scope expansion."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/calibration_bracketing.py",
      "tests/test_calibration_bracketing.py"
    ],
    "reason": "Custody-locator filesystem access also occurs in candidate authentication outside calibration_ledger.py.",
    "blocked_work": "Complete every-probe timeout and backup-root override coverage.",
    "minimal_change": "Bound candidate authentication with its existing absent-equivalent result and add focused regressions."
  }
}
```

## Change

`_custody_state()` now has a two-second daemon-thread budget covering checks and artifact reads. Timeout returns exactly `"absent"`. An empty `JOULEWISE_BACKUP_ROOTS` skips default-backup locators without probing. Caller authentication context and existing exceptions are preserved.

## Verification notes

Both named modules ran: 77 tests, one skipped. Initial new-test setup errors were corrected before the successful [logged rerun](/private/tmp/ICLOUD-CUSTODY-LOCATOR-01-tests-rerun.log).

The CloudDocs fixture is `tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl`. Referencing test modules include `test_p2038_production_path`, `test_d117_fixture_transport`, `test_mint_floor_artifact_generalized`, `test_floor_extraction`, and `test_partial_record_enclosure`. None were modified; existing `test_calibration_ledger.py` also remains unchanged.

No real iCloud access, repository-wide suite, or commit was performed.

## Residual risk

This is a partial patch, pending the scope expansion above. Timed-out daemon workers can remain blocked; remaining custody-read paths still need protection.