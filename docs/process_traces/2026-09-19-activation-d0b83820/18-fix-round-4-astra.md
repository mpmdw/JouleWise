```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented all ten 13a dispositions; both 44-test runs passed and all eleven mutations were detected, with CPU-ceiling variability and a sandbox-blocked census recorded.",
  "workspace": {
    "base_requested": "d74b1be5",
    "base_mode": "exact",
    "head_start": "d74b1be525aee141699573ae4361262973cbab00",
    "head_end": "d74b1be525aee141699573ae4361262973cbab00",
    "upstream_end": "d74b1be525aee141699573ae4361262973cbab00",
    "branch": "feat/2026-09-18-quiet-predicate-evidence-harness"
  },
  "pathspec": [
    "scripts/sample_quiet_predicate_evidence.py",
    "tests/test_sample_quiet_predicate_evidence.py"
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
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_sample_quiet_predicate_evidence",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 44 tests in 12.974s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 44 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_sample_quiet_predicate_evidence",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 44 tests in 13.229s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 44 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-fix4-232/bench.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tracked_files_checked 8053 byte_changed []",
          "status_identical True",
          "All 11 mutations killed; worktree byte-identical."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "All 11 mutations killed; worktree byte-identical."}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-fix4-232/verify_ast.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Baseline tests 45 current tests 44",
          "Removed ['test_exited_recorder_is_reaped_without_signal', 'test_term_then_kill_and_reap']",
          "Added ['test_native_qos_classes_read_back_in_subprocess']",
          "Real-load test AST unchanged"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Real-load test AST unchanged"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_sample_quiet_predicate_evidence.LoadTests.test_real_load_tracks_point_one_core_and_guards_worker_budget",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 4.009s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-fix4-232/control.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 1 test in 4.165s", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --check && git diff --stat && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " scripts/sample_quiet_predicate_evidence.py    |  74 +++++++-----",
          " tests/test_sample_quiet_predicate_evidence.py | 164 +++++++++++++++++++++++---",
          " 2 files changed, 189 insertions(+), 49 deletions(-)",
          "## feat/2026-09-18-quiet-predicate-evidence-harness...origin/feat/2026-09-18-quiet-predicate-evidence-harness",
          " M scripts/sample_quiet_predicate_evidence.py",
          " M tests/test_sample_quiet_predicate_evidence.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "2 files changed"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The unchanged real-load kernel ceiling also failed in the pool-across-boots and qos-swap mutation runs: 0.996578 s and 0.920590 s charged versus 0.920000 s allowed. Both full correct-code runs and the subsequent direct control passed.",
      "needs": "Lead should retain these observations when assessing the existing startup allowance; no threshold change was authorized or made."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The fixture orphan census could not execute ps under the sandbox; orphan count and rows are unavailable.",
      "needs": "Run the observational census from the lead bench."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical discovery was not run in this bounded fix round. Record 13a assigns full sharded replay after lead review and fresh delta re-audit.",
      "needs": "Complete the record-13a downstream verification sequence."
    }
  ]
}
```

## Change

All S1–S7 and N1–N3 dispositions are implemented. No ruling or scope expansion was needed; nothing was committed.

| Finding | Change and defect-shaped regression |
|---|---|
| S1 | `load()` cleanup now reports escalated PIDs and exit codes. A spawned child delivers its result, then sleeps past the grace: regression checks the named error and CLI exit 1. |
| S2 | First join grace is five seconds. The same regression checks a child needing one second after result delivery: no error, exit 0, child exit code 0. |
| S3 | `collect()` always records `error_rounds`. Three returned error rounds produce a session error and CLI exit 1; one error among three rounds preserves `error: null` and exit 0. Existing success status is `complete`; partial-only duration clipping remains unchanged. |
| S4 | `summarize()` removes reasons for resolved `reference` and `alignment_model` values. Probe-A-shaped regression checks returned and persisted summaries. |
| S5 | Summary means and reference deltas are separated by census condition, boot, and available row OS build. Probe-D-shaped regressions check two groups at 1 W and 9 W, emitted identities, matching-reference delta −1920 J, and null when that reference is absent. |
| S6 | New Darwin subprocess test reads back both native QoS classes through `pthread_get_qos_class_np`: background `0x09`, user-initiated `0x19`. |
| S7 | Removed `stop_process` and exactly its two tests. |
| N1 | Corrected the startup-plus-unreported CPU headroom comment. |
| N2 | `aggregate()` rejects foreign observations missing `busy_cores` with `ValueError`; both missing-metrics and empty-metrics inputs are covered. |
| N3 | `load()` closes both pipe ends when `Process.start()` raises. Regression uses a failing fake process and real connections, asserting both are closed. |

Regression comments name the production call sites. Existing tests were extended, leaving **44 tests** and the original real-load assertion set intact.

## Verification notes

The second module run took **13.792 s including interpreter startup**. Mutation substitutions and complete logs are retained in the [bench runner](/tmp/jw-fix4-232/bench.py) and [results](/tmp/jw-fix4-232/results.json). Every mutation exited 1 with assertion failures and no test errors.

| Mutation | Failure tail | Failing test names |
|---|---|---|
| `cores` | `FAILED (failures=1)` | `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `alignment` | `FAILED (failures=2)` | `test_absolute_anchor_endpoints_reject_known_arrival_offset`; `test_real_production_rate_anchor_and_clock_step_refusal` |
| `observer` | `FAILED (failures=1)` | `test_observer_cost_includes_known_reaped_child_delta` |
| `clock` | `FAILED (failures=1)` | `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `catchup-capped` | `FAILED (failures=3)` | `test_cpu_budget_overshoot_and_frozen_duty`; `test_late_initial_scheduling_never_catches_up`; `test_preempted_burn_exits_on_the_wall_deadline` |
| `burn-noop` | `FAILED (failures=1)` | `test_burn_profiles_advance_their_generator` |
| `window-skip` | `FAILED (failures=1)` | `test_load_worker_runs_its_window_after_the_rendezvous` |
| `cleanup-silent` | `FAILED (failures=1)` | `test_load_worker_runs_its_window_after_the_rendezvous` (`exit_delay=60`) |
| `pool-across-boots` | `FAILED (failures=2)` | `test_summary_never_pools_census_conditions_or_reference` (`boot_id`); incidental `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `qos-swap` | `FAILED (failures=2)` | `test_native_qos_classes_read_back_in_subprocess`; additional `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `all-error-exit-0` | `FAILED (failures=1)` | `test_one_recorder_for_all_rounds_and_cleanup_on_round_failure` (three errors) |

An isolated rerun of the summary test in the boot-pooling copy independently failed with `AssertionError: 1 != 2`; its detection does not depend on the incidental load failure.

Git status before and after mutations contained exactly the same two scoped modifications. Hash comparison covered **8,053 tracked files**, with no changes during mutations or subsequent checks.

The instrumented control V6 is **not an equivalent startup-cost control**: its script imports the test module during spawned-child bootstrap. It reported 1.133794 s charged, including 0.833645 s outside claimed periods. The subsequent direct unittest invocation V5 avoids that instrumentation and passed.

Every assertion in the unchanged real-load test is classified below:

| Test line | Assertion | Classification |
|---:|---|---|
| 727 | Worker share equals `.1` | Configuration invariant |
| 739 | `report["error"] is None` | Bounded protocol/lifecycle completion; deadline-sensitive |
| 748 | Claimed CPU fraction ≤ `.14` | Delivery ceiling; reduced delivery relaxes it |
| 750 | Period CPU ≤ budget + overshoot allowance | Per-period ceiling |
| 756 | Charged CPU ≥ claimed CPU − `.01` | Accounting consistency; lower claimed delivery relaxes RHS |
| 758 | Charged CPU ≤ `.14 × duration + STARTUP_CPU_S` | CPU ceiling with fixed startup headroom; observed variability noted above |
| 760 | Cleanup list is nonempty | Lifecycle structure |
| 762 | Child is not alive | Cleanup completion |
| 763 | Child exit code equals 0 | Clean exit; escalation/deadline-sensitive |
| 764 | PID probe raises `ProcessLookupError` | Process absence after reaping |

## Residual risk

**“real-load assertion fails on correct code under scheduler starvation”** remains possible literally when starvation exceeds readiness, result, or cleanup deadlines. The specific one-second post-result shutdown now passes. No controlled starvation experiment established the cause of the observed CPU-ceiling excursions.

**“assertion keyed to a quantity starvation destroys”** does not describe a surviving CPU-delivery minimum: none remains. Lifecycle completion still depends on finite deadlines, and the fixed startup allowance is empirically fallible.

Next exact step: lead diff review, fresh round-4 delta re-audit, then the full sharded replay specified by record 13a. The lead also needs to rerun the sandbox-blocked orphan census.