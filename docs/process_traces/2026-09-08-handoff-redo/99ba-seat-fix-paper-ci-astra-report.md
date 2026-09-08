```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Restored the verbatim standing-sentence block and corrected the rationale allowlist; all 116 acceptance tests pass.",
  "workspace": {
    "base_requested": "83f61672",
    "base_mode": "exact",
    "head_start": "83f6167236cbcedbee3f1e4c5e6bddd3045acf76",
    "head_end": "83f6167236cbcedbee3f1e4c5e6bddd3045acf76",
    "upstream_end": "83f6167236cbcedbee3f1e4c5e6bddd3045acf76",
    "branch": "int/2026-09-08-paper-s1-s6-s7"
  },
  "pathspec": [
    "docs/paper/round7/fill-checklist.md",
    "tests/fixtures/d165_rationale_allowlist.json"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_paper_round7_artifacts tests.test_d165_rationale_census tests.test_paper_successor_migration tests.test_docs_freshness > /private/tmp/pr301-fix-acceptance-final.log 2>&1\nacceptance_rc=$?\ntail -n 15 /private/tmp/pr301-fix-acceptance-final.log\nexit \"$acceptance_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 116 tests in 647.305s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 116 tests in [0-9.]+s\\n\\nOK"
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
  "flags": []
}
```

## Change

- Restored `main` checklist lines **35–43** verbatim at **59–67**, preserving exact indentation, curly quotes, and S7 guidance.
- Updated registry `common-time` keys: **264→270, 273→279, 281→287, 289→295, 297→303**. Original reasons retained.
- Deleted removed checklist keys: `common-time` at **63, 207, 215, 223, 231**, and the v1 rule token at **143**. No replacement occurrences.
- Added two exact entries for the inventory’s existing denial at **66→66**: `common-time` and `physical common-time`.

No commit made. Ready for lead review.

## Verification notes

The initial acceptance run exposed the two missing inventory exemptions; both were corrected before the successful full rerun. An optional process-status inspection was denied by the sandbox.