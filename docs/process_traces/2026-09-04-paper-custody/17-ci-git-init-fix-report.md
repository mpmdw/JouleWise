```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Routed the paper-custody fixture's Git initialization through the shared helper while preserving identity and commit behavior.",
  "workspace": {
    "base_requested": "f6363d67",
    "base_mode": "exact",
    "head_start": "f6363d67d8a61bebe2fd653ec1b8c3e6ad94b01c",
    "head_end": "f6363d67d8a61bebe2fd653ec1b8c3e6ad94b01c",
    "upstream_end": "f6363d67d8a61bebe2fd653ec1b8c3e6ad94b01c",
    "branch": "feat/2026-09-04-paper-custody-seam"
  },
  "pathspec": [
    "tests/test_paper_custody.py",
    "docs/process_traces/2026-09-04-paper-custody/17-ci-git-init-fix-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 3.890s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 29 tests in 39.488s",
          "",
          "OK",
          "KILLED 109 owner-source mutations and 5 grant-policy mutations: stale receipts refused",
          "PENDING production Git-blob role: fixture coverage is not production coverage",
          "KILLED 4 refusal AST mutations: dead literal, undeclared call, variable argument, declared-only code"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 29 tests in [0-9.]+s\\n\\nOK\\nKILLED 109 owner-source mutations and 5 grant-policy mutations: stale receipts refused\\nPENDING production Git-blob role: fixture coverage is not production coverage\\nKILLED 4 refusal AST mutations: dead literal, undeclared call, variable argument, declared-only code"
      }
    },
    {
      "id": "V3",
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
  "flags": []
}
```

## Change

Imported `init_git_fixture` from `tests.git_fixture` and replaced the direct
`git init -q` call. The helper now supplies the shared maintenance controls;
the fixture's existing directory, user identity, add/commit sequence, and
recorded HEAD remain unchanged. No commit was created.
