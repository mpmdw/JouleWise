```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Applied all P1-P9 and N1-N5 advisor-language and traceability fixes to PROJECT_STATUS.md.",
  "workspace": {
    "base_requested": "a915a9c7",
    "base_mode": "exact",
    "head_start": "a915a9c7c042e439522bd1bdaad8b9db672ccc18",
    "head_end": "a915a9c7c042e439522bd1bdaad8b9db672ccc18",
    "upstream_end": "a915a9c7c042e439522bd1bdaad8b9db672ccc18",
    "branch": "feat/2026-09-01-status-rewrite"
  },
  "pathspec": [
    "PROJECT_STATUS.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_terms_lint tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...........................................",
          "----------------------------------------------------------------------",
          "Ran 43 tests in 2.001s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 43 tests in [0-9.]+s\\n\\nOK$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; import re; t=Path(\"PROJECT_STATUS.md\").read_text(); ps={re.sub(r\":\\d+(?:-\\d+)?$\", \"\", x).rstrip(\"/\") for x in re.findall(r\"`([^`\\n]+)`\", t) if \"/\" in x and not x.startswith(\"github.com/\")}; print(\"missing:\", sorted(p for p in ps if not Path(p).exists()))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "missing: []"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^missing: \\[\\]$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "grep -n -i \"timing-bracket\\|estimator\\b\" PROJECT_STATUS.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "(no output)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "^\\(no output\\)$"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "(no output)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^\\(no output\\)$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M PROJECT_STATUS.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^ M PROJECT_STATUS\\.md$"
      }
    }
  ],
  "flags": []
}
```

## Change

| Item | Line(s) | What changed |
|---|---:|---|
| P1 | 106–116 | Replaced “timing-bracket corners” with the physical two-boundary/four-combination explanation; removed remaining corner coinage. |
| P2 | 32–35 | Replaced “estimator” in the cell definition with “which of the two formulas below produces the number.” |
| P3 | 148–150 | Explained five samples as three physically required samples plus a two-sample advance-declared safety factor. |
| P4 | 118–126 | Defined the headline comparison as boundary-placement error versus spread among unchanged repeated runs. |
| P5 | 173–178, 424–426, 569 | Standardized on “ten-block direction test,” physically defined it at first use, and reused it at both later sites. |
| P6 | 427–430 | Replaced the second meaning of “marginal” with the dictated one-model-interval wording. |
| P7 | 431–433 | Replaced “practical equivalence” with a plain-language advance-declared closeness threshold. |
| P8 | 82–90 | Renamed the text “frozen analysis semantics” and cited `generate_configs.py:2597-2603`. |
| P9 | 445–448 | Explained replacement as a recorded procedure that preserves the original run. |
| N1 | 188–194 | Attached measurement-soundness decision D-078, clause 11, to the attribution figures and approximately 5-joule disclosure. |
| N2 | 145–148 | Added generator and adapter pointers for the 100-millisecond interval. |
| N3 | 202–203 | Added `docs/council_log.md:1536` for the 222-bundle count. |
| N4 | 132–133 | Attached close-out decision D-168 directly to the eight-plus-four ratio requirement. |
| N5 | 415–420 | Attached D-078 clause 11 to the approximately 1-joule restatement. |

A scripted occurrence inventory followed by context review covered 38 repeated technical terms. Their first uses now define them, explain their physical meaning, or follow an earlier plain-language construction.

## Verification notes

The grep exit code of 1 is expected and means neither prohibited expression occurs. The worktree remains intentionally dirty with only `PROJECT_STATUS.md` modified.