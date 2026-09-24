```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the t0 clean-tree guard; full acceptance needs an out-of-scope driver test fixture update.",
  "workspace": {
    "base_requested": "bd80d169",
    "base_mode": "exact",
    "head_start": "bd80d16905757ab03f7e166e42d93a0d6ac888bb",
    "head_end": "bd80d16905757ab03f7e166e42d93a0d6ac888bb",
    "upstream_end": "bd80d16905757ab03f7e166e42d93a0d6ac888bb",
    "branch": "feat/2026-09-24-a294-t0-clean-tree"
  },
  "pathspec": ["joulewise/night_gate.py", "tests/test_night_gate.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_gate tests.test_evidence_night tests.test_night_kinds tests.test_run_night tests.test_arm_retry tests.test_magistrate_watchdog tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 659 tests in 391.592s", "FAILED (failures=44, errors=7, skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 93 tests in 0.826s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_gate.NightGateTests.test_dirty_unmanifested_tracked_file_refuses_at_t0 tests.test_night_gate.NightGateTests.test_untracked_shadowing_module_refuses_at_t0 tests.test_night_gate.NightGateTests.test_real_git_checkout_status_uses_production_runner",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 3 tests in 0.146s", "FAILED (errors=3)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(errors=3\\)"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "All 51 acceptance failures and errors are in tests.test_run_night. Its fake probe source raises KeyError for the new status argv, causing downstream driver assertions to fail.",
      "needs": "Authorize tests/test_run_night.py for a clean response to the status argv, then rerun named acceptance."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_run_night.py"],
    "reason": "The new production probe reaches driver test fakes whose run method has no response for its argv.",
    "blocked_work": "Passing the named acceptance suite.",
    "minimal_change": "Have ProbeSource.run return an exit-0, empty-stdout ProbeResult for the checkout status argv."
  }
}
```

## Change

C1–C3: After a matching HEAD, C5 runs `/usr/bin/git status` through `probes.run`, records the result and porcelain lines, refuses a dirty tree as `night_plan_stale`, and routes an uncheckable tree through `night_probe_error` ([night_gate.py](/Users/edr/code/wt-a65fb4fa-a294/joulewise/night_gate.py:1256), [night_gate.py](/Users/edr/code/wt-a65fb4fa-a294/joulewise/night_gate.py:1269)). The path matches the existing Git probe convention. C4: no manifest, arm check, or `Probes` fields changed. C5: the gate test fakes provide a clean result while preserving existing assertions ([test_night_gate.py](/Users/edr/code/wt-a65fb4fa-a294/tests/test_night_gate.py:40)).

T1–T6 are `test_dirty_unmanifested_tracked_file_refuses_at_t0`, `test_untracked_shadowing_module_refuses_at_t0`, `test_clean_measurement_checkout_proceeds_with_porcelain_evidence`, `test_measurement_checkout_status_exit_128_is_probe_error`, `test_measurement_head_mismatch_skips_checkout_status`, and `test_real_git_checkout_status_uses_production_runner` ([test_night_gate.py](/Users/edr/code/wt-a65fb4fa-a294/tests/test_night_gate.py:833)). T6 uses `init_git_fixture` and the production `make_probes` runner.

## Verification notes

The named acceptance command ran and ended with **659 tests; 44 failures, 7 errors, 9 skipped**. Every failure or error was in `tests.test_run_night`; these were fixture `KeyError` failures for the new argv and their downstream effects, not process-list sandbox failures. `tests.test_night_gate` passes after the refusal was restored.

For the guard-deletion check, I removed the new dirty-tree refusal block. T1, T2, and T6 each failed because the dirty checkout was no longer refused. I restored the block and reran `tests.test_night_gate` successfully. `git diff bd80d169 --stat` lists only the two allowed paths.

## Residual risk

**NEEDS_SCOPE:** the exhaustive `WRITE_SCOPE` excludes [test_run_night.py](/Users/edr/code/wt-a65fb4fa-a294/tests/test_run_night.py:232). The magistrate should double-check its fake status response, then rerun the exact named acceptance command.