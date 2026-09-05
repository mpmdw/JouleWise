```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: the focused landing tests fail on a current direct-init site, and the new enumeration guard ignores non-test_*.py support modules under tests/.",
  "workspace": {
    "base_requested": "git merge-base origin/main HEAD = 04cd6e52e9d6ed2da369398bb448c5454f1917b3",
    "base_mode": "exact",
    "head_start": "785ab754af47ac1ef02bb8db27d914790f85cc07",
    "head_end": "785ab754af47ac1ef02bb8db27d914790f85cc07",
    "upstream_end": "36e7d539c795cf8a60f2bace8d640ff81499c336",
    "branch": "feat/2026-09-04-fan-GIT-FIXTURE-MAINTENANCE-SWEEP-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/GIT-FIXTURE-MAINTENANCE-SWEEP-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "GF-01",
        "severity": "blocker",
        "location": "tests/test_git_fixture_maintenance.py:157; tests/test_d117_contrast_v5_pack.py:356",
        "text": "The landing's repository-wide guard is red at the reviewed head: it reports the current D117 v5 fixture's direct git init even though that local helper installs the exact four-key tuple. Therefore the claimed touched-module pass and three-consecutive-green acceptance cannot hold. Route that helper through init_git_fixture or explicitly recognize and exact-check this established local helper.",
        "counterfactual": "At the reviewed head, running tests.test_git_fixture_maintenance fails with violations == {'test_d117_contrast_v5_pack.py': (356,)}; removing or curing that direct site makes this specific failure disappear."
      },
      {
        "id": "GF-02",
        "severity": "blocker",
        "location": "tests/test_git_fixture_maintenance.py:160",
        "text": "The claimed repository-wide regrowth guard scans only TESTS_ROOT.glob('test_*.py'), so a fixture factory in any differently named Python support module below tests/ can initialize an unhygienic repository without detection. This contradicts the acceptance requirement covering every tests/ module and leaves the teardown race able to regrow.",
        "counterfactual": "In a temporary copy, a direct-init test_bundle.py is detected and fails; renaming the identical file to tests/fixture_factory.py makes the enumeration test pass unchanged (exit 0)."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_git_fixture_maintenance -v",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 3 tests in 3.866s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_arm_readiness_evidence tests.test_arm_readiness_evidence_author tests.test_arm_readiness_lifecycle tests.test_arm_readiness_pack_digest tests.test_bridge tests.test_bundle tests.test_calibration_bracketing tests.test_calibration_ledger tests.test_calibration_live_three_window tests.test_calibration_writer_crash_matrix tests.test_check_gate_ledger tests.test_d117_decode_contrast_plan tests.test_d117_floor_qwen25_1p5b_plan tests.test_d117_floor_qwen25_7b_plan tests.test_family_marker tests.test_git_fixture_maintenance tests.test_issue_dg071_dg075_statistics tests.test_launch_window tests.test_mint_floor_artifact_generalized tests.test_reauthor_clean tests.test_receipt_histsem tests.test_scheduler_gates tests.test_window_status_guard",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 797 tests in 3423.738s",
          "FAILED (failures=1, skipped=13)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK( \\(skipped=13\\))?"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --name-only \"$(git merge-base origin/main HEAD)\"..HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tests/test_receipt_histsem.py",
          "tests/test_scheduler_gates.py",
          "tests/test_window_status_guard.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^(tests/.*\\n)*tests/.*$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp/jw-git-fixture-audit.wXjMSY python3 -m unittest -v tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_shared_helper_installs_the_exact_four_key_tuple",
      "cwd": "/private/tmp/jw-git-fixture-audit.wXjMSY",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Ran 1 test in 0.084s",
          "FAILED (errors=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(errors=1\\)"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp/jw-git-fixture-audit.wXjMSY python3 -m unittest -v tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper",
      "cwd": "/private/tmp/jw-git-fixture-audit.wXjMSY",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "AssertionError: {'test_bundle.py': (204,)} != {}",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "test_bundle.py.*FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "mv /private/tmp/jw-git-fixture-audit.wXjMSY/tests/test_bundle.py /private/tmp/jw-git-fixture-audit.wXjMSY/tests/fixture_factory.py; PYTHONPATH=/private/tmp/jw-git-fixture-audit.wXjMSY python3 -m unittest -v tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper",
      "cwd": "/private/tmp/jw-git-fixture-audit.wXjMSY",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.000s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "fixture_factory.py.*FAILED"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The landing is uncorroborated and cannot satisfy its three-consecutive-green or hosted-green acceptance while its own focused guard is deterministically red.",
      "needs": "Cure GF-01 and GF-02, then rerun every touched module three consecutive times and obtain the required hosted run across both interpreters."
    }
  ]
}
```

## Findings

### GF-01 — blocker

The focused landing test and the complete touched-module command both fail on `tests/test_d117_contrast_v5_pack.py:356`. That existing fixture helper already applies the exact tuple, but the new guard neither routes nor recognizes it. The landing is red and cannot meet its bench acceptance.

### GF-02 — blocker

The guard's `TESTS_ROOT.glob("test_*.py")` is narrower than the governed `tests/**` population. A temporary-copy falsifier kept an unhygienic direct init byte-for-byte but renamed its module from `test_bundle.py` to `fixture_factory.py`; the guard changed from the expected failure to `OK`.

## Evidence

- Review range: `04cd6e52e9d6ed2da369398bb448c5454f1917b3..785ab754af47ac1ef02bb8db27d914790f85cc07`, obtained from `git merge-base origin/main HEAD` at the reviewed head. All 24 delta paths are within the declared `tests/**` scope. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta.
- Diff inspection found no assertion edits and no product-code edits. Every adopted call preserves its repository target and `git init` arguments. `tests/git_fixture.py` is a shared extraction whose only intended behavioral addition is installing the exact four local maintenance controls immediately after initialization. The former dated wrapper in `test_issue_dg071_dg075_statistics.py` used its pinned environment for commits; dropping it for `git init` does not change commit identities.
- Runtime counterfactual: in a temporary copy, skipping only `maintenance.auto` while leaving the declared tuple unchanged makes `test_shared_helper_installs_the_exact_four_key_tuple` error on the missing local key. Static counterfactual: reverting the adopted `test_bundle.py` call to direct `git init` makes the enumeration test fail at line 204. These kill the single intended behavior class and show the extraction is load-bearing.
- Previous-round status: no prior report exists in this mission directory, and the durable fan-out record names no mission-specific non-staleness blocker for this landing. There was therefore no prior mission blocker to re-test beyond the refreshed-head audit required here.
- No whole-suite command was run. Verification was limited to the modules changed by the landing, plus the new guard that inspects their fixture-init population, as required by the preflight rule.

## Residual risk

The required hosted run across both interpreters was not available in the supplied evidence. A green hosted result would not cure either deterministic local blocker.
