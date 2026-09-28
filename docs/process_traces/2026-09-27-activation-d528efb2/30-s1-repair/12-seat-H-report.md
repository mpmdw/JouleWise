```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Added digest-bound non-mock bundle pair writers, config rebinding, capture evidence, and an injected battery runner with counterfactual tests.",
  "workspace": {
    "base_requested": "c7593edb",
    "base_mode": "exact",
    "head_start": "c7593edbcaacdd2c7bbf0175ad315fdbafe5e275",
    "head_end": "c7593edbcaacdd2c7bbf0175ad315fdbafe5e275",
    "upstream_end": null,
    "branch": "fix/2026-09-27-s1-regress-H"
  },
  "pathspec": [
    "tests/bfgs_fixtures.py",
    "tests/test_bfgs_fixtures.py"
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
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_bfgs_fixtures",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 8 tests in 1.461s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests.*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -l '(^|[[:space:]])(from tests\\.bfgs_fixtures import|import tests\\.bfgs_fixtures)' tests --glob '*.py'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["tests/test_bfgs_fixtures.py"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^tests/test_bfgs_fixtures.py$"
      }
    }
  ],
  "flags": []
}
```

## Change

- `rebind_config(bundle, *, telemetry_backend="powermetrics")`: rewrites the config, its metadata digest, and existing metadata and summary backend labels.
- `write_passing_pair(bundle)` and `write_charging_pair(bundle)`: write authenticated bundle evidence; both refuse a mock-bound bundle or a stale config digest before writing.
- `injected_battery_runner(*, charging=False)`: answers only the expected battery probe from fixed fixture bytes.
- `write_capture_evidence(capture_dir, *, validation_id, session_id=None, slot=None, charging=False, evidence=None)`: writes a capture pair and parseable evidence, then returns the evidence digest.

## Verification notes

The eight tests cover gate pass, raw-byte custody failure, charging refusal, changed-config refusal, both mock-config writer refusals, rebind-before-pair behavior, capture authentication, and runner determinism. The importer search found only the new test module; there were no other importing modules to run. The whole suite was not run, as instructed. No NEEDS_RULING arose.