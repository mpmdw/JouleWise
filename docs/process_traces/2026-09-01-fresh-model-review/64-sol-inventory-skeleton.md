```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Reshaped the first-use ledger into a 152-row closed inventory and added a mechanical drift guard.",
  "workspace": {
    "base_requested": "d462512893d616244f3f61a3e1dfe1cec09093b7",
    "base_mode": "exact",
    "head_start": "d462512893d616244f3f61a3e1dfe1cec09093b7",
    "head_end": "d462512893d616244f3f61a3e1dfe1cec09093b7",
    "upstream_end": "d462512893d616244f3f61a3e1dfe1cec09093b7",
    "branch": "feat/2026-09-01-skeleton"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md",
    "tests/test_paper_first_use_ledger.py"
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
      "cmd": "python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 1.001s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "probe_dir=$(mktemp -d /tmp/joulewise-first-use-probe.XXXXXX); cp docs/paper/draft-v2-skeleton.md \"$probe_dir/probe.md\"; perl -0pi -e 's/\\| warm-up pulses \\| Bracketed pulse-train algorithm \\|/| warm-up pulses | One diagnostic reconstruction |/' \"$probe_dir/probe.md\"; PAPER_FIRST_USE_DRAFT=\"$probe_dir/probe.md\" python3 -m unittest tests.test_paper_first_use_ledger >\"$probe_dir/probe.log\" 2>&1; probe_rc=$?; tail -n 14 \"$probe_dir/probe.log\"; echo \"MIS_HOME_PROBE_EXIT=$probe_rc\"; test \"$probe_rc\" -ne 0",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "AssertionError: 'Bracketed pulse-train algorithm' != 'One diagnostic reconstruction'",
          ": 'warm-up pulses' first occurs on line 122 in 'Bracketed pulse-train algorithm', not 'One diagnostic reconstruction'",
          "FAILED (failures=1)",
          "MIS_HOME_PROBE_EXIT=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)warm-up pulses.*first occurs on line 122.*FAILED \\(failures=1\\).*MIS_HOME_PROBE_EXIT=1"
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
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/paper/draft-v2-skeleton.md",
          "?? tests/test_paper_first_use_ledger.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "docs/paper/draft-v2-skeleton.md.*tests/test_paper_first_use_ledger.py"
      }
    }
  ],
  "flags": []
}
```

## Change

The ledger now contains 152 unique rows:

- `glossed-at-first-use`: 127
- `audience-vocabulary`: 13
- `built-before`: 11
- `forward-pointer-next-paragraph`: 1
- `FAILS`: 0

The test enforces the closed statuses, row/count agreement, unique terms and alternatives, exact first-occurrence homes, comment stripping, and closure for bold phrases containing at least two lexical words.

FAILS rows: none.

## Verification notes

The deliberate scratch-copy mis-home produced:

```text
AssertionError: 'Bracketed pulse-train algorithm' != 'One diagnostic reconstruction'
: 'warm-up pulses' first occurs on line 122 in 'Bracketed pulse-train algorithm', not 'One diagnostic reconstruction'
FAILED (failures=1)
MIS_HOME_PROBE_EXIT=1
```

Only the two authorized paths are dirty. `git diff --check` is clean. The requested targeted suites were run; the repository-wide suite was not needed for this ledger-and-test-only change.