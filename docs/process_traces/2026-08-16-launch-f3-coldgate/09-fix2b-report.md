```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Migrated lifecycle tests from the deleted public consumer to launcher/private-context paths; all requested tests pass.",
  "workspace": {
    "base_requested": "impl/wo-launch-binding",
    "base_mode": "exact",
    "head_start": "72cd69842434962d95176c9a625d256bc55f4fe5",
    "head_end": "72cd69842434962d95176c9a625d256bc55f4fe5",
    "upstream_end": "72cd69842434962d95176c9a625d256bc55f4fe5",
    "branch": "impl/wo-launch-binding"
  },
  "pathspec": [
    "tests/test_arm_readiness_lifecycle.py"
  ],
  "unowned_dirty": [
    "docs/decision_log.md",
    "joulewise/arm_readiness.py",
    "scripts/launch_window.py",
    "scripts/run_campaign.py",
    "tests/test_arm_readiness.py",
    "tests/test_launch_window.py",
    "tests/test_run_campaign.py",
    ".consult-f3-report.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_lifecycle",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 12 tests in 9.255s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 12 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness tests.test_launch_window tests.test_run_campaign tests.test_bundle tests.test_arm_readiness_dry_run tests.test_arm_readiness_integration tests.test_arm_readiness_schemas tests.test_arm_readiness_registry tests.test_arm_readiness_pack_digest",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 406 tests in 191.707s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 406 tests in [0-9.]+s\\s+OK"
      }
    }
  ],
  "flags": []
}
```

## Change

Removed the stale public-symbol import and obsolete direct-call checks. Lifecycle scenarios now use the launcher, with the collision test supplying complete authenticated private-consumer context. The public API check now asserts that `consume_launch_capability` is absent.

The authorized change remains uncommitted; no other files were touched.