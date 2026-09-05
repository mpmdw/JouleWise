```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Applied D-165 superseded banners; the census is RED only on the three paper-K/L draft lines.",
  "workspace": {
    "base_requested": "a9d03fdef7345d9da6f70f7978963c5687cf1dd7",
    "base_mode": "exact",
    "head_start": "a9d03fdef7345d9da6f70f7978963c5687cf1dd7",
    "head_end": "a9d03fdef7345d9da6f70f7978963c5687cf1dd7",
    "upstream_end": "a9d03fdef7345d9da6f70f7978963c5687cf1dd7",
    "branch": "feat/2026-09-05-d165-relabel"
  },
  "pathspec": [
    "docs/paper/round7/retensing-plan.md",
    "tests/fixtures/d165_rationale_allowlist.json",
    "docs/process_traces/2026-09-05-d165-relabel/12-fix-round-7-report.md"
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
      "cmd": "python3 -B -m unittest -v tests.test_d165_rationale_census",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "docs/paper/draft-v2-skeleton.md:29: moved together",
          "docs/paper/draft-v2-skeleton.md:1387: moved together",
          "docs/paper/draft-v2-skeleton.md:1738: timing error common to",
          "",
          "----------------------------------------------------------------------",
          "Ran 8 tests in 7.461s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "docs/paper/draft-v2-skeleton\\.md:29: moved together[\\s\\S]*docs/paper/draft-v2-skeleton\\.md:1738: timing error common to[\\s\\S]*FAILED \\(failures=1\\)"
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
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Per the magistrate ruling, draft-v2-skeleton.md:29, :1387, and :1738 remain untouched and are the only active census hits; Paper-K/L cures them after merge.",
      "needs": "Merge the assigned Paper-K/L cures, then rerun the census."
    }
  ]
}
```

## Change

Inserted the exact dated D-165 superseded banner before the historical H07 A paragraph and H22 A/B paragraphs, preserving all historical text. The old occurrence lines 143, 333, and 335 are now 145, 337, and 341; the inserted banners are at 143, 335, and 339. Updated existing exact custody locators 411→417, 559→565, and 563→569, and recorded the three newly bounded marked phrases with exact marker-ledger keys. No unbounded or path-wide exception was added. The draft was not touched.

## Verification notes

The sole allowed census invocation exited 1 exactly as ruled: seven tests passed, and the one census failure reports only the three draft lines.

Exact RED tail:

```text
docs/paper/draft-v2-skeleton.md:29: moved together
docs/paper/draft-v2-skeleton.md:1387: moved together
docs/paper/draft-v2-skeleton.md:1738: timing error common to

----------------------------------------------------------------------
Ran 8 tests in 7.461s

FAILED (failures=1)
```

No discovery suite, Claude/Codex launcher, commit, or out-of-scope write was performed.

## Residual risk

The three draft hits remain active until their assigned Paper-K/L changes merge; the lead must rerun the census after that merge.
