```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Installed §10.5 and preserved B4; the new G7 regression proves that missing ARM wins before either required refusal.",
  "workspace": {
    "base_requested": "4d72e524",
    "base_mode": "informational",
    "head_start": "4d72e5248953c178cbaa2fa2125bcbc034685e66",
    "head_end": "4d72e5248953c178cbaa2fa2125bcbc034685e66",
    "upstream_end": null,
    "branch": "feat/2026-09-08-d176-seat4-rehearsal"
  },
  "pathspec": [
    "docs/contracts/pack_night_go_receipt.md",
    "tests/test_launch_window.py"
  ],
  "unowned_dirty": [
    "docs/contracts/pack_night_go_receipt.md",
    "tests/test_launch_window.py"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_night tests.test_t0_rehearsal tests.test_launch_window tests.test_night_gate tests.test_docs_freshness > /private/tmp/d176-seat4-g7-acceptance.log 2>&1\nseat4_test_rc=$?\ntail -70 /private/tmp/d176-seat4-g7-acceptance.log\nprintf '\\nACCEPTANCE_EXIT_CODE=%s\\n' \"$seat4_test_rc\"\nexit \"$seat4_test_rc\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=2)",
          "",
          "ACCEPTANCE_EXIT_CODE=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK[\\s\\S]*ACCEPTANCE_EXIT_CODE=0"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check > /private/tmp/d176-seat4-g7-diff-check.log 2>&1\nseat4_diff_rc=$?\ncat /private/tmp/d176-seat4-g7-diff-check.log\nprintf 'DIFF_CHECK_EXIT_CODE=%s\\n' \"$seat4_diff_rc\"\nexit \"$seat4_diff_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DIFF_CHECK_EXIT_CODE=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^DIFF_CHECK_EXIT_CODE=0\\n$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: no out-of-scope writes occurred. The launcher reads ARM before GO, and the consumer authenticates the 26-key GO purpose after ARM verification. The ruled control cannot reach the required refusal through the current production entry.",
      "needs": "Have the launcher/consumer owner implement §10.5 pre-ARM admission, or prospectively expand scope."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: §6 specifies eight exact keys for one presentation; §10.5 requires two presentations and first-refusal evidence without specifying replacement keys/version. The bundle loader also has a closed record-name set with no G7 locator slot.",
      "needs": "Rule the exact aggregate JSON schema and bundle locator slot. A versioned aggregate with two presentation records is recommended over silently extending the exact eight-key form."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Named acceptance ran 213 tests in 434.084 seconds. Only the new G7 regression's two presentation subtests failed: both returned launch_consumption_missing for absent-arm.json instead of launch_go_receipt_invalid with class/purpose detail.",
      "needs": "Resolve F1/F2, finish runtime implementation, and replay the same named acceptance."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "scripts/launch_window.py",
      "joulewise/arm_readiness.py",
      "scripts/rehearse_t0_unattended.py",
      "tests/test_rehearse_t0_unattended.py"
    ],
    "reason": "Required pre-ARM production-entry behavior and bundle locator admission reside outside the exhaustive allowlist.",
    "blocked_work": "Executable two-presentation G7 producer and authenticated bundle acceptance.",
    "minimal_change": "Install digest-authenticated control refusal before ARM reads/verification through the owning launcher/consumer seat, then admit and test the lead-ruled G7 locator transport."
  }
}
```

## Change

Installed the five ruling items verbatim as §10.5, preserved the intake B4 regression, and updated §7.1/§9 with the demonstrated blocker. No runtime files changed; no commit.

| Clause | Disposition |
|---|---|
| §10.5 item 1 | Control custody rule installed; sibling control represented in regression. |
| Items 2–3 | Both presentations tested through the real eight-flag CLI with absent ARM; both expose incorrect refusal ordering. |
| Item 4 | Blocked on aggregate schema and bundle locator transport. |
| Item 5 | Regression asserts completed-night fixture bytes remain unchanged. |
| B4 | Existing digest-before-class regression preserved; new pre-ARM regression added. |
| G5 | D-149 retirement and C1–C5 recomputation remain unimplemented. |
| S1/S4/N1 | Remaining purpose/root regressions and final clause pins remain incomplete. |

**G7 artifact’s exact JSON shape:** none produced. The ruling does not specify the replacement exact keys/version needed to represent two refusals; no shape was invented.

## Verification notes

The [acceptance log](/private/tmp/d176-seat4-g7-acceptance.log) records only the two new G7 subtest failures. Both return missing-ARM refusal before examining the presented receipt. Diff whitespace checks passed.

## Residual risk

The new regression isolates admission ordering; it is not authenticated completed-rehearsal evidence. Lead action is required to route the launcher/consumer fix and rule the aggregate schema and locator slot before resuming seat 4.