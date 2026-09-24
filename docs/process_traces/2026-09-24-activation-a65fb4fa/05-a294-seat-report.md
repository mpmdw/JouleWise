```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Added the t0 clean-tree guard, updated authorized test fakes, and passed named acceptance.",
  "workspace": {
    "base_requested": "bd80d169",
    "base_mode": "exact",
    "head_start": "bd80d16905757ab03f7e166e42d93a0d6ac888bb",
    "head_end": "bd80d16905757ab03f7e166e42d93a0d6ac888bb",
    "upstream_end": "bd80d16905757ab03f7e166e42d93a0d6ac888bb",
    "branch": "feat/2026-09-24-a294-t0-clean-tree"
  },
  "pathspec": [
    "joulewise/night_gate.py",
    "tests/test_night_gate.py",
    "tests/test_run_night.py"
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
      "cmd": "python3 -B -m unittest tests.test_night_gate tests.test_evidence_night tests.test_night_kinds tests.test_run_night tests.test_arm_retry tests.test_magistrate_watchdog tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 659 tests in 401.266s", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=9\\)"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 93 tests in 0.826s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": []
}
```

## Change

- **C1–C3:** After a matching HEAD, C5 runs the exact status argv using the existing `/usr/bin/git` convention. It records the probe and porcelain lines, refuses a dirty tree as `night_plan_stale` with at most five lines in the detail, and sends probe failures through `night_probe_error` ([night_gate.py](/Users/edr/code/wt-a65fb4fa-a294/joulewise/night_gate.py:1256), [night_gate.py](/Users/edr/code/wt-a65fb4fa-a294/joulewise/night_gate.py:1269)).
- **C4–C5:** No manifest, arm check, or `Probes` fields changed. The gate and driver test fakes now answer the status argv with a clean result; existing assertions remain unchanged ([test_night_gate.py](/Users/edr/code/wt-a65fb4fa-a294/tests/test_night_gate.py:40), [test_run_night.py](/Users/edr/code/wt-a65fb4fa-a294/tests/test_run_night.py:232)).

T1–T6 map respectively to `test_dirty_unmanifested_tracked_file_refuses_at_t0`, `test_untracked_shadowing_module_refuses_at_t0`, `test_clean_measurement_checkout_proceeds_with_porcelain_evidence`, `test_measurement_checkout_status_exit_128_is_probe_error`, `test_measurement_head_mismatch_skips_checkout_status`, and `test_real_git_checkout_status_uses_production_runner` ([test_night_gate.py](/Users/edr/code/wt-a65fb4fa-a294/tests/test_night_gate.py:833)). T6 uses `init_git_fixture` and the production probe runner.

## Verification notes

I deleted the new dirty-tree refusal block temporarily: T1, T2, and T6 failed. I restored it; `tests.test_night_gate` and the full named acceptance suite then passed.

Acceptance command: `python3 -B -m unittest tests.test_night_gate tests.test_evidence_night tests.test_night_kinds tests.test_run_night tests.test_arm_retry tests.test_magistrate_watchdog tests.test_git_fixture_maintenance`  
Result tail: `Ran 659 tests in 401.266s` / `OK (skipped=9)`. `git diff bd80d169 --stat` lists only the three authorized paths.

The magistrate should double-check the exact status argv, the five-line refusal detail, and the driver fake’s clean response for varying measurement roots.