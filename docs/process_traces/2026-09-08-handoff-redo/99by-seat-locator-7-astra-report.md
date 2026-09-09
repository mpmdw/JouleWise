```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented all three ruled changes; 378 acceptance tests and the in-memory counterfactuals pass.",
  "workspace": {
    "base_requested": "b598113e",
    "base_mode": "exact",
    "head_start": "b598113e5c785b051738b52164b5328f90a0da27",
    "head_end": "b598113e5c785b051738b52164b5328f90a0da27",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-custody-locator"
  },
  "pathspec": [
    "docs/contracts/calibration_ledger_append.md",
    "scripts/run_campaign.py",
    "tests/fixtures/custody_read_replay_allowlist.json",
    "tests/test_custody_mode_inventory.py",
    "tests/test_run_campaign.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -u -B -m unittest tests.test_custody_mode_inventory tests.test_calibration_ledger_custody tests.test_run_campaign tests.test_whole_window > /private/tmp/icloud-locator-7-acceptance-final.log 2>&1\ncheck_rc=$?\ntail -n 5 /private/tmp/icloud-locator-7-acceptance-final.log\nexit \"$check_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 378 tests in 371.959s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 378 tests in .*\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_campaign_core_mode_counterfactuals > /private/tmp/icloud-locator-7-counterfactuals.log 2>&1\ncheck_rc=$?\ntail -n 5 /private/tmp/icloud-locator-7-counterfactuals.log\nexit \"$check_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check > /private/tmp/icloud-locator-7-diff-check.log 2>&1\ncheck_rc=$?\ncat /private/tmp/icloud-locator-7-diff-check.log\nexit \"$check_rc\"",
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
  "flags": []
}
```

## Change

1. [run_campaign.py:5000](/Users/edr/code/JouleWise-wt-fan-ICLOUD-LOCATOR/scripts/run_campaign.py:5000) defaults to issuing, forwards it at line 5258, and receives explicit replay only from the completed-window caller at line 6287. The [allowlist reason:98](/Users/edr/code/JouleWise-wt-fan-ICLOUD-LOCATOR/tests/fixtures/custody_read_replay_allowlist.json:98) names claim-readiness emission. [Regressions:7499](/Users/edr/code/JouleWise-wt-fan-ICLOUD-LOCATOR/tests/test_run_campaign.py:7499) verify all three callers and absent-original versus replacement discovery. Six in-memory mutations fail the assertions: either hard-coded bracket mode, replay default, omitted completed-window replay, and replay added to either other caller.

2. [Inventory:213](/Users/edr/code/JouleWise-wt-fan-ICLOUD-LOCATOR/tests/test_custody_mode_inventory.py:213) uses function-local replay-call ordinals; `line` remains informational. Counterfactuals at lines 330 and 337 confirm an inserted comment preserves inventory equality, while a second replay call requires ordinal 2.

3. [Contract:512](/Users/edr/code/JouleWise-wt-fan-ICLOUD-LOCATOR/docs/contracts/calibration_ledger_append.md:512) names all four census limits and the combined runtime invariant. No detection was added for those shapes.

No commit. Ready for the lead’s part-7 delta review.

## Verification notes

The first acceptance run exposed two assertions in an existing test that assumed implicit replay; that test now opts in explicitly. An initial counterfactual matcher was also narrowed to the intended call.

The call-edge regression uses real temporary filesystem probes with mocked candidate authentication and bracket scoring. No hardware measurement ran.