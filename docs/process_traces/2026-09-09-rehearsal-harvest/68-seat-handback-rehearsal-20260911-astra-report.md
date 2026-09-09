```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Rewrote the handback for rehearsal-20260911 and added the source-checked arm runbook; requested checks pass.",
  "workspace": {
    "base_requested": "7ca2908f",
    "base_mode": "exact",
    "head_start": "7ca2908f66819d534ebc53e3786f32106f6de5ba",
    "head_end": "7ca2908f66819d534ebc53e3786f32106f6de5ba",
    "upstream_end": "7ca2908f66819d534ebc53e3786f32106f6de5ba",
    "branch": null
  },
  "pathspec": [
    "docs/process/NIGHT_HANDBACK.md",
    "docs/process_traces/2026-09-09-rehearsal-harvest/67-arm-runbook-rehearsal-20260911.md"
  ],
  "unowned_dirty": ["RUN_STATE.md"],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness > /private/tmp/joulewise-rehearsal-20260911-docs-freshness.log 2>&1\ncheck_rc=$?\ncat /private/tmp/joulewise-rehearsal-20260911-docs-freshness.log\nprint \"rc=$check_rc\"\nexit \"$check_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 0.926s", "OK", "rc=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK\\nrc=0"
      }
    },
    {
      "id": "V2",
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
      "level": "nonblocking",
      "text": "Future arming commands were syntax-checked, not executed. H, notice IDs and live results remain UNVERIFIED.",
      "needs": "Lead review and future arming activation."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Launchd stream paths are inside night/; literal no-write acceptance at the pre-night dead-man firing requires live inspection.",
      "needs": "Preserve the directory baseline and adjudicate any observed conflict with synthesis 65."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No runner baseline manifest/digest was supplied; formal bridge scope-check was not performed. Start/end status and unowned-file byte preservation were checked.",
      "needs": "Lead retains formal bridge provenance verification."
    }
  ]
}
```

## Change

Updated the three current handback sections. Retained the complete prior reconciliation as dated history; Standing rules are byte-identical.

Added the arm sequence, validation-twin explanation, exact commands, harvest criteria, source-line table and UNVERIFIED list. No commit or arming performed.

| Fact | Source lines |
|---|---|
| t0, window, deadline, exit boundary, belt | Synthesis 65:15–16 |
| H and roots | Synthesis 65:17–20 |
| Install window and first dead-man | Synthesis 65:21–26 |
| Power/timer observations and acceptance | Synthesis 65:27–32 |
| Notice ordering and successor activation | Synthesis 65:33–41 |
| Writer and validation twin | 21b:177–226 |
| Atomic move and install | 21b:293–301 |
| Exact dead-man message | `scripts/run_night.py:1740–1747` |

## Verification notes

All four shell blocks and embedded Python parse. Epoch arithmetic matches the pins. Untracked-file whitespace also passes; `RUN_STATE.md` remains byte-identical.

[Acceptance log, including rc](/private/tmp/joulewise-rehearsal-20260911-docs-freshness.log). Full suite omitted for this docs-only task.

## Residual risk

UNVERIFIED: future H/notice IDs, live arming outcomes, and launchd stream-file behavior. Sources 61/62/65 currently reside only in the lead worktree and need to accompany landing. The runbook preserves the existing acceptance wording without relaxing it.