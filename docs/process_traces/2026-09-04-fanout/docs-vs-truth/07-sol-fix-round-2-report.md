```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "DVTR-R5 is cured with compact Markdown table parsing and discriminating literal-pipe regressions; the touched module is green.",
  "workspace": {
    "base_requested": "75bce710d11a9092d413f9e238cc382658c1747c",
    "base_mode": "exact",
    "head_start": "75bce710d11a9092d413f9e238cc382658c1747c",
    "head_end": "75bce710d11a9092d413f9e238cc382658c1747c",
    "upstream_end": "75bce710d11a9092d413f9e238cc382658c1747c",
    "branch": "feat/2026-09-04-fan-docs-vs-truth"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/docs-vs-truth/07-sol-fix-round-2-report.md",
    "scripts/build_site.py",
    "tests/test_build_site_parsers.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/docs-vs-truth/06-delta-reaudit-round-1.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "JOULEWISE_SITE_CONTENT_TESTS=1 python3 -m unittest tests.test_build_site_parsers.BuildSiteParserTests.test_parse_status_at_glance_accepts_compact_table_rows tests.test_build_site_parsers.BuildSiteParserTests.test_parse_completed_queue_keeps_escaped_and_inline_code_pipes_in_one_cell -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.000s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "JOULEWISE_SITE_CONTENT_TESTS=1 python3 -m unittest tests.test_build_site_parsers",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 30 tests in 20.432s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 30 tests.*OK \\(skipped=1\\)"
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The pinned Marked 18.0.6 integration case skipped because its local binary is unavailable; the offline production build and pack regression passed.",
      "needs": "The lead may rerun the connected case where the exact pinned binary is installed."
    }
  ]
}
```

## Change

| Finding | Cure | Evidence |
|---|---|---|
| DVTR-R5 | Replaced the whitespace-only tokenization rule with a scanner that accepts compact ordinary separators while retaining escaped pipes and pipes inside matching backtick spans. Callers with a known schema supply the expected column count; only when an all-pipe parse has excess cells and the legacy whitespace-boundary interpretation yields exactly that count does the compatibility path apply. This keeps the existing decision-index production source readable without changing its out-of-scope file. | `scripts/build_site.py:689`; `scripts/build_site.py:780`; `scripts/build_site.py:789`; `scripts/build_site.py:1065` |
| DVTR-R5 counterfactual | Added a full compact Status At A Glance table regression (`|Phase|Scope|Status|`) and changed the literal-pipe regression to compact row syntax containing both escaped mathematical pipes and a pipe-bearing code span. The compact status regression reproduced the refuter's pre-fix one-cell result and passes after the cure. | `tests/test_build_site_parsers.py:99`; `tests/test_build_site_parsers.py:287` |

## Verification notes

The required touched module passed. Its one skip is the pre-existing connected Marked 18.0.6 integration case; the same module's offline production build/pack path passed and exercised the live decision-index consumer.
