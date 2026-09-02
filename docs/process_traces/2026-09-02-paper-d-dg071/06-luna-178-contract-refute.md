```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Statistics reproduce exactly, but artifact custody and guard coverage need fixes.",
  "workspace": {
    "base_requested": "/Users/edr/code/JouleWise-wt-paper-d",
    "base_mode": "exact",
    "head_start": "a63d45bd",
    "head_end": "1baf8c4c5f1c1e671cfd4b10fdd76452b1fdc8c5",
    "upstream_end": "a63d45bd",
    "branch": "feat/2026-09-02-paper-d"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "SF-1",
        "severity": "should_fix",
        "title": "Absolute input locator",
        "evidence": "Artifact JSON line 5 records /Users/edr/code/JouleWise/... rather than a repo-relative locator.",
        "recommendation": "Record the canonical repo-relative bundle path, optionally retaining the absolute path only as local provenance."
      },
      {
        "id": "SF-2",
        "severity": "should_fix",
        "title": "Artifact commit is stale relative to reviewed head",
        "evidence": "Artifact records 3fca7d6b, while head is 1baf8c4c. Re-running at head changes JSON/MD only in git_commit and produces a different artifact hash.",
        "recommendation": "Re-issue at 1baf8c4c and update the registered artifact SHA."
      },
      {
        "id": "SF-3",
        "severity": "should_fix",
        "title": "Several refusal guards lack biting tests",
        "evidence": "The blank required-field branch at script lines 165-168 is not exercised; the missing-header test exercises schema mismatch instead. Invalid-value, extra-field, non-positive interval, empty-set, insufficient-unique-timestamp, output-extension, and commit-error guards are also untested.",
        "recommendation": "Add focused refusal tests, including a row with an empty interval_end_s."
      },
      {
        "id": "NIT-1",
        "severity": "nit",
        "title": "Markdown is not exhaustive",
        "evidence": "Rendered numbers agree, but q1_ms and q3_ms JSON fields are omitted from the Markdown companion.",
        "recommendation": "Either render those fields or state that Markdown renders only median/IQR milliseconds."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 7 tests in 0.031s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 7 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python scripts/issue_dg071_dg075_statistics.py --out <scratchpad>/codex-review-d/dg071-dg075-statistics.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DG-071 median_ms=120.918512 iqr_ms=5.975008",
          "DG-075 median_ms=120.922327 iqr_ms=5.894899"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DG-071 median_ms=120\\.918512 iqr_ms=5\\.975008\\nDG-075 median_ms=120\\.922327 iqr_ms=5\\.894899"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "independent CSV recomputation over pinned power_trace.csv",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "sha256 6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9",
          "DG-071 0.12091851234436035 0.005975008010864258",
          "DG-075 0.12092232704162598 0.005894899368286133"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DG-071 0\\.12091851234436035 0\\.005975008010864258"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Named focused suite passes, but multiple refusal branches are not directly tested.",
      "needs": "Add guard-coverage tests."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The committed artifact was produced at 3fca7d6b; current-head replay records 1baf8c4c and changes the artifact hash.",
      "needs": "Re-issue at reviewed head or explicitly ratify production-commit provenance."
    }
  ]
}
```

## Findings

No blocker: the ratification is implemented correctly. It defines DG-071 as median/IQR of `interval_end_s − interval_start_s` over every retained record (ratification lines 7–10), and DG-075 as median/IQR of differences between consecutive unique `timestamp_s` values (lines 13–16). Registry rows 643 and 647 state the same formulas.

The implementation includes every row (`scripts/issue_dg071_dg075_statistics.py:152-202`), collapses sorted distinct timestamps before differencing (`257-266`), and reports 1218 records, 406 timestamps, 812 duplicates, and 405 spacings. R-167-1 is followed at lines 117–130: `statistics.median`, copied `_quantile` (`95-108`), IQR subtraction, unrounded seconds, and six-decimal millisecond renderings.

Independent recomputation agrees to the last digit:

- DG-071: `0.12091851234436035 s`, IQR `0.005975008010864258 s`.
- DG-075: `0.12092232704162598 s`, IQR `0.005894899368286133 s`.

The committed script SHA is correct: `048d8bb2…31ce2`, and `git diff 3fca7d6b 1baf8c4c -- scripts/` is empty. The artifact’s `git_commit` correctly identifies its production commit, but not the reviewed head; current-head replay differs only in that field.

The Markdown’s shared values are numerically faithful. It omits JSON `q1_ms` and `q3_ms`, hence NIT-1.

Guard assertions: wrong SHA is tested at test lines 105–109; schema mismatch at 119–122; non-monotone timestamps at 127–130; path mismatch at 132–144; generic CLI nonzero refusal at 146–156. The actual missing-value branch (`record_field_missing`) is not tested.

The excursion artifact uses `capture_relative_path`; the anchor artifact uses absolute raw paths. For this registry supplier, use the requested repo-relative locator.

Replacement rows:

```markdown
| DG-071 — Section 6 sampling-record interval width, line 256 | 120.918512 ms (IQR 5.975008 ms) | `docs/paper/round7/dg071-dg075-statistics.json#statistics.DG-071.median_s` and `#statistics.DG-071.iqr_s`; artifact SHA-256 `5cc81fd74b39383d14aa5cc2df6ba13dc1fdb309ddecd0ff6d4ec0ab333e8c7a`; render seconds ×1000 to 6 decimals, retaining unrounded `*_s` | historical a10 diagnostic / resolvability example | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, DF, PROJ, SYN |
| DG-075 — Section 6 record spacing, line 256 | 120.922327 ms (IQR 5.894899 ms) | `docs/paper/round7/dg071-dg075-statistics.json#statistics.DG-075.median_s` and `#statistics.DG-075.iqr_s`; artifact SHA-256 `5cc81fd74b39383d14aa5cc2df6ba13dc1fdb309ddecd0ff6d4ec0ab333e8c7a`; render seconds ×1000 to 6 decimals, retaining unrounded `*_s` | historical a10 diagnostic / resolvability example | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, DF, PROJ, SYN |
```

A sibling R7F should pin the artifact SHA, input bundle SHA/path, schema version, registry IDs, producer script blob SHA, and commit identity; independently recompute both statistics; compare every JSON/Markdown rendered value; and require stable exit-0 success plus named exit-2 refusal for path, hash, schema, missing-field, and timestamp-order failures.

## Residual risk

The producer has no dedicated replay fence or artifact self-hash verification; registry acceptance should therefore require the sibling fence before publication.