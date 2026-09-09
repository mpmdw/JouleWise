```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Fixed both regression classes; all 228 requested acceptance tests passed with 3 existing skips.",
  "workspace": {
    "base_requested": "6d35e8af",
    "base_mode": "exact",
    "head_start": "6d35e8afab2227ca93b9eebde5a318574cef653c",
    "head_end": "6d35e8afab2227ca93b9eebde5a318574cef653c",
    "upstream_end": "6d35e8afab2227ca93b9eebde5a318574cef653c",
    "branch": "fix/2026-09-08-icloud-custody-locator"
  },
  "pathspec": [
    "configs/paper_supply/supply_map.json",
    "tests/test_bracket_binding_cli.py",
    "tests/test_calibration_live_three_window.py"
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
      "cmd": "python3 -m unittest tests.test_calibration_live_three_window tests.test_bracket_binding_cli tests.test_launch_window tests.test_arm_readiness_evidence_author tests.test_arm_readiness_dry_run tests.test_paper_custody tests.test_paper_rendering tests.test_custody_mode_inventory tests.test_calibration_ledger_custody tests.test_whole_window > /private/tmp/icloud-locator-part8-acceptance.log 2>&1\npart8_rc=$?\nprintf '\\nACCEPTANCE_RC=%s\\n' \"$part8_rc\" >> /private/tmp/icloud-locator-part8-acceptance.log\ntail -n 15 /private/tmp/icloud-locator-part8-acceptance.log\nexit \"$part8_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 228 tests in 694.366s",
          "OK (skipped=3)",
          "KILLED 109 owner-source mutations and 5 grant-policy mutations: stale receipts refused",
          "PENDING production Git-blob role: fixture coverage is not production coverage",
          "KILLED 4 refusal AST mutations: dead literal, undeclared call, variable argument, declared-only code",
          "ACCEPTANCE_RC=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=3\\)[\\s\\S]*ACCEPTANCE_RC=0"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check > /private/tmp/icloud-locator-part8-diff-check.log 2>&1\npart8_rc=$?\nprintf 'DIFF_CHECK_RC=%s\\n' \"$part8_rc\" >> /private/tmp/icloud-locator-part8-diff-check.log\ncat /private/tmp/icloud-locator-part8-diff-check.log\nexit \"$part8_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["DIFF_CHECK_RC=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^DIFF_CHECK_RC=0$"
      }
    }
  ],
  "flags": []
}
```

## Change

- **Class A:** The shared candidate fake accepts `mode`; patch mocks record it. Assertions at [test_calibration_live_three_window.py:814](/Users/edr/code/JouleWise-wt-fan-ICLOUD-LOCATOR/tests/test_calibration_live_three_window.py:814) verify discovery and candidate forwarding for default `issuing` and explicit `read_replay`. Assertions at [test_bracket_binding_cli.py:598](/Users/edr/code/JouleWise-wt-fan-ICLOUD-LOCATOR/tests/test_bracket_binding_cli.py:598) verify six replay calls and six default issuing calls through production evaluation. Existing assertions and test counts are preserved.
- **Class B:** [supply_map.json:47](/Users/edr/code/JouleWise-wt-fan-ICLOUD-LOCATOR/configs/paper_supply/supply_map.json:47) has eight hash-only changes: receipt and inventory pins for claim evidence, D165 closeout, reported-energy parents, and whole-window verdict. Structural comparison asserted that **no role, grant, or production digest was added or changed**. The census fixture reads inventory pins from this map; `tests/test_paper_custody.py` needed no edit.

## Verification notes

Launch/readiness cascades passed unchanged; no genuine mismatch remained. Three skips are existing U2 successor-engine cases.

Verification used the requested acceptance set for these test/fixture-only changes. No commit. Next: lead diff review and repository-wide replay.