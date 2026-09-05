```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "GF-02 is cured by exact repository-relative helper exemptions, with a red-then-green nested basename-collision regression.",
  "workspace": {
    "base_requested": "b3fb3ae388efa23a571a3d52f0af37574ddbfb1b",
    "base_mode": "exact",
    "head_start": "b3fb3ae388efa23a571a3d52f0af37574ddbfb1b",
    "head_end": "b3fb3ae388efa23a571a3d52f0af37574ddbfb1b",
    "upstream_end": "a6e9edde082f460fbe335d2eac8021f77258b8e6",
    "branch": "feat/2026-09-04-fan-GIT-FIXTURE-MAINTENANCE-SWEEP-01"
  },
  "pathspec": [
    "tests/test_git_fixture_maintenance.py",
    "docs/process_traces/2026-09-04-fanout/GIT-FIXTURE-MAINTENANCE-SWEEP-01/05-sol-fix-round-2-report.md"
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
      "cmd": "python3 -m unittest -v tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: {} != {'support/git_fixture.py': (4,)}",
          "Ran 5 tests in 3.703s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "AssertionError: \\{\\} != \\{'support/git_fixture.py': \\(4,\\)\\}.*FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 3.677s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests in [0-9.]+s\\n\\nOK"
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

`ESTABLISHED_LOCAL_HELPERS` now names exact repository-relative paths, so only `tests/git_fixture.py` receives the shared-helper exemption. The guard passes each recursively discovered module's repository-relative path into the exemption check. A nested `tests/support/git_fixture.py` regression proves that a basename collision is reported at line 4.

## Verification notes

The required red run, after adding only the regression:

```text
test_established_local_helpers_retain_the_exact_tuple (tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_established_local_helpers_retain_the_exact_tuple) ... ok
test_every_test_module_routes_git_initialization_through_shared_helper (tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper) ... ok
test_guard_flags_direct_init_in_nested_support_module (tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_guard_flags_direct_init_in_nested_support_module) ... ok
test_nested_git_fixture_does_not_inherit_top_level_exemption (tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_nested_git_fixture_does_not_inherit_top_level_exemption) ... FAIL
test_shared_helper_installs_the_exact_four_key_tuple (tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_shared_helper_installs_the_exact_four_key_tuple) ... ok

======================================================================
FAIL: test_nested_git_fixture_does_not_inherit_top_level_exemption (tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_nested_git_fixture_does_not_inherit_top_level_exemption)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-fan-GIT-FIXTURE-MAINTENANCE-SWEEP-01/tests/test_git_fixture_maintenance.py", line 200, in test_nested_git_fixture_does_not_inherit_top_level_exemption
    self.assertEqual(violations, {"support/git_fixture.py": (4,)})
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {} != {'support/git_fixture.py': (4,)}
- {}
+ {'support/git_fixture.py': (4,)}

----------------------------------------------------------------------
Ran 5 tests in 3.703s

FAILED (failures=1)
```

The green replay after the implementation:

```text
test_established_local_helpers_retain_the_exact_tuple (tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_established_local_helpers_retain_the_exact_tuple) ... ok
test_every_test_module_routes_git_initialization_through_shared_helper (tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper) ... ok
test_guard_flags_direct_init_in_nested_support_module (tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_guard_flags_direct_init_in_nested_support_module) ... ok
test_nested_git_fixture_does_not_inherit_top_level_exemption (tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_nested_git_fixture_does_not_inherit_top_level_exemption) ... ok
test_shared_helper_installs_the_exact_four_key_tuple (tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_shared_helper_installs_the_exact_four_key_tuple) ... ok

----------------------------------------------------------------------
Ran 5 tests in 3.677s

OK
```

The explicit preflight boundary was honored: no test module other than `tests.test_git_fixture_maintenance` was run.
