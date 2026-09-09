```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_SCOPE: custody probes and overrides implemented; regression exposes an authentication-session lock retained by timed-out reads.",
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
    "joulewise/calibration_bracketing.py",
    "tests/test_calibration_ledger_custody.py",
    "tests/test_calibration_bracketing.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' python3 -m unittest tests.test_calibration_ledger_custody tests.test_calibration_ledger tests.test_calibration_bracketing > /private/tmp/ICLOUD-CUSTODY-LOCATOR-01-expanded-final.log 2>&1\ncustody_test_rc=$?\nprintf '\\nrc=%s\\n' \"$custody_test_rc\" >> /private/tmp/ICLOUD-CUSTODY-LOCATOR-01-expanded-final.log\ntail -17 /private/tmp/ICLOUD-CUSTODY-LOCATOR-01-expanded-final.log\nexit \"$custody_test_rc\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=1, skipped=2)",
          "",
          "rc=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=2\\)\\s+rc=0"
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
      "text": "NEEDS_SCOPE: V2AuthenticationReadSession.read and read_nofollow hold their shared RLock during filesystem reads. A timed-out custody worker retains that lock, potentially blocking subsequent authentication work. The new non-hanging regression demonstrates this. No out-of-scope paths were modified.",
      "needs": "Authorize the requested authentication I/O paths, repair lock ownership around blocking reads, and rerun focused acceptance."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/authentication_io.py",
      "tests/test_authentication_io.py"
    ],
    "reason": "Blocking filesystem reads occur while holding the shared authentication-session lock outside the current allowlist.",
    "blocked_work": "Ensure a timed-out custody probe cannot leave subsequent authentication work blocked; obtain green acceptance.",
    "minimal_change": "Move blocking filesystem I/O outside the session registry lock while preserving strict parsing and atomic first-digest enforcement; add concurrency regressions."
  }
}
```

## Change

Added shared two-second budgets for artifact hashing, observation verification, governed reads, historical reauthentication, finalization rereads, and candidate authentication. Nested reads share one worker.

Timeout preserves each existing absent outcome: `"absent"`, `{}`, `calibration_ledger_custody_invalid`, the missing-custody error, or `None`, respectively. Empty backup overrides skip probing; nonempty overrides preserve the relative suffix beneath replacement roots.

## Verification notes

The [final log](/private/tmp/ICLOUD-CUSTODY-LOCATOR-01-expanded-final.log) records 132 tests with one failure and two skips. The sole failure is the new `test_timed_out_authenticated_read_does_not_pin_session_lock`; all other tests passed.

CloudDocs appears in `tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl`. Its referencing modules include `test_d117_fixture_transport`, `test_floor_extraction`, `test_partial_record_enclosure`, `test_mint_floor_artifact_generalized`, and `test_p2038_production_path`. None were touched. Existing custody tests remain unchanged.

No real iCloud access, repository-wide suite, or commit occurred.

## Residual risk

Do not merge yet: the demonstrated shared-lock blockage requires the additional scope above.