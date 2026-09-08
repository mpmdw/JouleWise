```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "All requested fixes implemented; eight approved line pins refreshed and four-module acceptance passes.",
  "workspace": {
    "base_requested": "42b0d235",
    "base_mode": "exact",
    "head_start": "42b0d2356b494a22f567f840fb192d4686eab0f8",
    "head_end": "42b0d2356b494a22f567f840fb192d4686eab0f8",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-custody-locator"
  },
  "pathspec": [
    "joulewise/calibration_ledger.py",
    "tests/test_calibration_ledger_custody.py",
    "tests/test_authentication_io.py",
    "docs/contracts/calibration_ledger_append.md",
    "docs/paper/round7/fill-checklist.md",
    "docs/guides/tutorial-replicate-the-calibration-bound.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "JOULEWISE_BACKUP_ROOTS='' python3 -B -m unittest tests.test_calibration_ledger_custody tests.test_calibration_bracketing tests.test_calibration_ledger tests.test_authentication_io > /tmp/icloud-custody-fix-acceptance-resumed.log 2>&1; rc=$?; echo rc=$rc >> /tmp/icloud-custody-fix-acceptance-resumed.log; tail -7 /tmp/icloud-custody-fix-acceptance-resumed.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 159 tests in 6.779s",
          "OK (skipped=2)",
          "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer",
          "rc=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=2\\)"
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
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff -- tests/test_authentication_io.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "-    \"joulewise/calibration_ledger.py:abandon_calibration_ledger_tail:3963:os.fdopen\",",
          "+    \"joulewise/calibration_ledger.py:abandon_calibration_ledger_tail:3983:os.fdopen\","
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "abandon_calibration_ledger_tail:3983:os.fdopen"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Applied the approved refresh of exactly eight ledger line-number classifications. Classified operations remain unchanged. Opus N-1 was wrong: the line-pinned sentinel exists; restoring wrapper adjacency therefore requires a pin refresh.",
      "needs": ""
    }
  ]
}
```

## Change

- **SF-1:** Timeout and exception probes emit distinguishable stderr diagnostics while preserving absent-equivalent decisions and receipt fields. No existing structured log required extension.
- **SF-2:** The docstring explicitly covers complete but responsive-slow trees exceeding two seconds.
- **SF-3:** Added the dated contract addendum and both requested documentation lines.
- **SF-4:** Non-empty overrides refuse issuance before hashing with `custody_locator_override_mint_forbidden`. This prevents original-locator receipts from binding replacement-root bytes; empty-override behavior remains unchanged.
- **N-1/N-2/N-4:** Restored wrapper adjacency, exported `probe_custody`, and replaced the constant-only test with behavioral coverage. Refreshed only the eight approved line pins.

Counterfactual: without the fixes, unreachable custody lacks diagnostics and issuance can authenticate relocated bytes under an original locator.

## Verification notes

Fail-before regression tail: `FAILED (failures=4)`, `rc=1`. Before the approved pin refresh, acceptance reported `FAILED (failures=1, skipped=2)`. Pass-after results are recorded in the envelope and `/tmp/icloud-custody-fix-acceptance-resumed.log`.

Opus N-1’s sentinel premise was incorrect: restoring adjacency trades wrapper-placement churn for a required pin refresh. Classified operations were preserved exactly.

No real iCloud access, repository-wide suite, or commit was performed.

## Residual risk

Authenticated reads remain unbounded after a successful probe.