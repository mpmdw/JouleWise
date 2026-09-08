```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "Static delta review and census checks pass; custody execution is blocked by the read-only sandbox.",
  "workspace": {
    "base_requested": "b598113e",
    "base_mode": "exact",
    "head_start": "07e6e4c1a6038d58df6c59feccf79f59e97ed650",
    "head_end": "07e6e4c1a6038d58df6c59feccf79f59e97ed650",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-custody-locator"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {"findings": []},
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_custody_mode_inventory.CustodyModeInventoryTests.test_line_shift_does_not_require_allowlist_edit tests.test_custody_mode_inventory.CustodyModeInventoryTests.test_second_call_requires_its_own_allowlist_row",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_custody_mode_inventory.CustodyModeInventoryTests.test_read_replay_inventory",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_custody_mode_inventory tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_campaign_core_callers_keep_replacement_custody_replay_only tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_campaign_core_mode_counterfactuals tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_direct_campaign_bracket_explicitly_replays_relocated_custody",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-fan-ICLOUD-LOCATOR']"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "Campaign tests fail during import because the sandbox disallows temporary-file creation; regression and live-AXI custody counterfactual remain unexecuted.",
      "needs": "Lead reruns with temporary-fixture write access and verifies the custody assertion fails under the live-AXI replay mutation."
    }
  ]
}
```

## Residual risk

No new production defect found in the five-file diff.

`_idle_admission_core_evaluation` defaults to issuing at `scripts/run_campaign.py:5000` and forwards `mode` at :5258. The compatibility wrapper (:5300) and live AXI caller (:7911) omit mode; only completed-window replay (:6284) explicitly selects `read_replay`.

The census keys by file, qualified function, and replay-call ordinal. `line` remains validated metadata but does not participate in equality. Both requested census counterfactuals passed.

The contract paragraph (:511) names all four ruled limits and the runtime invariant. Earlier replay-default language is explicitly superseded; no substantive contradiction found.

The changed `test_direct_campaign_bracket_explicitly_replays_relocated_custody` (`tests/test_run_campaign.py:7885`) directly exercises retained-custody replay and its issuing counterfactual, not a live campaign entry. Explicit opt-in is appropriate; it does not conceal an identified issuing regression.

However, the new built-in live-AXI mutation encounters `assertNotIn("mode", ...)` before the replacement-inspection assertion. Its generic “any assertion failed” check cannot establish the specifically requested absent-versus-replacement failure. That execution remains outstanding.