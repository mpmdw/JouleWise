```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Closed F5 by resolving both the reported and expected missing-corpus paths before comparison, making the regression independent of macOS TMPDIR spelling.",
  "workspace": {
    "base_requested": "b2e107a5",
    "base_mode": "exact",
    "head_start": "b2e107a5f64efe1fc17efaf5a5d23274be232cb0",
    "head_end": "b2e107a5f64efe1fc17efaf5a5d23274be232cb0",
    "upstream_end": "b2e107a5f64efe1fc17efaf5a5d23274be232cb0",
    "branch": "int/2026-09-04-fan-wave-1"
  },
  "pathspec": [
    "tests/test_paper_round7_artifacts.py",
    "docs/process_traces/2026-09-04-fanout/wave-1/06-sol-fix-f5-tmpdir.md"
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
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.161s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in [0-9.]+s[\\s\\S]*OK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.160s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in [0-9.]+s[\\s\\S]*OK$"
      }
    }
  ],
  "flags": []
}
```

## Change

The absent-corpus regression now parses the path from the diagnostic, resolves it, resolves the expected path independently, and compares the canonical `Path` objects. The diagnostic prefix remains asserted separately.

## Verification notes

Per the preflight restriction, only the touched `InvocationTests` class ran. It passed with the ambient macOS temporary-directory environment and with `TMPDIR=/private/tmp`.
