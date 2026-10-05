```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Genesis fixtures now supply pinned acceptance; all six requested modules pass, with one existing skip.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "f8ad1651423752d3290024532e5f11dcae43e1a4",
    "head_end": "f8ad1651423752d3290024532e5f11dcae43e1a4",
    "upstream_end": null,
    "branch": "feat/2026-10-05-v5-qual-x2"
  },
  "pathspec": [
    "tests/test_pipeline_smoke_tail.py",
    "tests/test_d165_dominance_closeout.py",
    "tests/test_analysis_integration.py"
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
      "cmd": "TMPDIR=/tmp/dd5-x2f PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_pipeline_smoke_tail tests.test_d165_dominance_closeout tests.test_analysis_integration tests.test_v5_block4_x2 tests.test_analysis_finalizer tests.test_check_window_provenance > /tmp/dd5-x2f/requested-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-x2f/inspect_scope.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scope satisfied; all assertions and existing skip markers unchanged; production files unchanged"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "scope satisfied; all assertions and existing skip markers unchanged; production files unchanged"
      }
    }
  ],
  "flags": []
}
```

## Change

Direct finalizer calls receive the fixture’s acceptance path. CLI and downstream consumers use the real byte-authenticating loader within fixture contexts. Changes remain uncommitted; nothing was pushed.

## Verification notes

Ran 248 tests. The existing smoke-tail DATA-only ruling skip remains unchanged. Verification covered the six requested modules; the full canonical suite was not run.