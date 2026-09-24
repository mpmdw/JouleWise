```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Installed TIER-01 in the six authorized files and drafted the required full-tier PR body.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "exact",
    "head_start": "bce0d7dfd38ca1ff160ae9b29a685f6c3a61d9b1",
    "head_end": "bce0d7dfd38ca1ff160ae9b29a685f6c3a61d9b1",
    "upstream_end": "bce0d7dfd38ca1ff160ae9b29a685f6c3a61d9b1",
    "branch": "feat/2026-09-24-tier01-install"
  },
  "pathspec": [
    "docs/orchestration.md",
    ".github/pull_request_template.md",
    "scripts/check_gate_ledger.py",
    "tests/test_check_gate_ledger.py",
    ".github/workflows/gate-ledger.yml",
    "docs/process/tier01_defect_log.md"
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
      "cmd": "TMPDIR=/tmp/278ebc9e python3 -B -m unittest tests.test_check_gate_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 38 tests in 4.554s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 38 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -B scripts/check_gate_ledger.py --body-file /tmp/278ebc9e/tier01-pr-body.md --head-sha bce0d7dfd38ca1ff160ae9b29a685f6c3a61d9b1 --repo-root .",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["gate-ledger: item 12: evidence must be RUN <path-or-sha>"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "gate-ledger: item 12: evidence must be RUN <path-or-sha>"
      }
    },
    {
      "id": "V3",
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
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "mkdir -p /tmp/278ebc9e && TMPDIR=/tmp/278ebc9e python3 -B -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The extra repository-wide suite was interrupted after several minutes without a reported test failure; it has no final result.",
      "needs": "Magistrate runs the required unpiped full-suite replay on the integration tree and fills ledger row 9."
    }
  ]
}
```

## Change

Installed all six COUNCIL-407-01 §G5 clauses verbatim in [orchestration.md](/Users/edr/code/wt-278ebc9e-tier01/docs/orchestration.md), added the tier fields and checker behavior, and opened the [TIER-01 defect log](/Users/edr/code/wt-278ebc9e-tier01/docs/process/tier01_defect_log.md) with the suspension rule and 2026-10-24 review. The required-check wording matches the September 24 branch-protection record. All six files remain uncommitted as instructed.

**Draft full-tier PR body** (also saved at `/tmp/278ebc9e/tier01-pr-body.md`):

```markdown
Tier: full

Impact statement (TIER-01):
(i) Raw-bundle byte or recorded timestamp: No.
(ii) Reduced energy, time, token count or correctness score: No.
(iii) Admit, refuse, select or exclude decision over bundles, nights, blocks, envelopes or items: No.
(iv) Unit or uncertainty: No.
(v) Registration, prospective manifest, analysis plan or estimator constant: No.
(vi) Published number or sentence in the paper, README claims or claim renderers: No.

## Gate ledger (D-118 / D-121)

| # | Gate item | Evidence |
| --- | --- | --- |
| 1 | Independent audit by a fresh non-author reviewer | TODO (magistrate: reviewer evidence) |
| 2 | Paired distinct lenses: contract + execution (physics if measurement-adjacent) | TODO (magistrate: lens evidence) |
| 3 | Lead-written FIX contract with dictated closure shapes; findings triaged and dispositioned, never silently applied | TODO (magistrate: FIX and disposition evidence) |
| 4 | Delta re-audit of every fix round | TODO (magistrate: re-audit evidence) |
| 5 | Same-signature statement from every delta; a surviving class escalates to a consult, not round three | TODO (magistrate: signature evidence) |
| 6 | Opus counter-review on the near-final head | TODO (magistrate: Opus evidence) |
| 7 | Apex Fable code-reading diff gate answering design-level questions; never skipped or downgraded | TODO (magistrate: Fable evidence) |
| 8 | Overbuild / merge-ability prune | TODO (magistrate: prune evidence) |
| 9 | Lead unpiped full-suite replay on the integration tree (not the stale branch), exact tail recorded | TODO (magistrate: integration-tree replay) |
| 10 | Final-head fresh-eyes review after every post-review commit | TODO (magistrate: final-head review) |
| 11 | CI green on final head + post-merge cross-unit integration review | TODO (magistrate: CI and integration evidence) |
| 12 | Magistrate terminal review, full session context, of the exact merge candidate (final head sha); not delegable | TODO (magistrate: RUN final-head-sha) |

## Summary

Install Rule TIER-01 from cold gate COUNCIL-407-01 §G5 as one full-tier change. Document the required main-branch gate-ledger check, add tier and six impact lines to the PR template, enforce light-tier ledger rows in the checker, add branch tests, and open the 30-day defect log. Ed was informed with veto by Gmail 1a0d364481dec249. Day-30 review: 2026-10-24.

## Verification

- `python3 -B -m unittest tests.test_check_gate_ledger`: 38 tests, OK.
- Full-suite integration-tree replay: TODO (magistrate gate-ledger row 9).
- `git diff --check`: passed.
```

## Verification notes

The checker rejected the draft on all twelve TODO rows, as intended. The focused suite and diff check passed. The repository-wide suite was started but interrupted before completion; its final verdict remains open.