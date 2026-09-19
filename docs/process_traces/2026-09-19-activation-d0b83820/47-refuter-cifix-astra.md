```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "No diff findings; both mutants killed and 45 selected tests pass. Full-module verification needs a ruling on the explicit no-live-collect constraint.",
  "workspace": {
    "base_requested": "b3a95dc89b08b82e8297f9699faf12b1bebe1941",
    "base_mode": "exact",
    "head_start": "b3a95dc89b08b82e8297f9699faf12b1bebe1941",
    "head_end": "b3a95dc89b08b82e8297f9699faf12b1bebe1941",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-cifixref-b3a95dc.lzxcG7/check_diff.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " tests/test_sample_quiet_predicate_evidence.py | 4 ++++",
          " 1 file changed, 4 insertions(+)",
          "BYTE CHECK PASS: removing exactly four added lines reproduces the complete base file"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "BYTE CHECK PASS"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "printf '%s\\n' \"$(cat /tmp/jw-cifixref-b3a95dc.lzxcG7/runner.py)\" | env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B - linux",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 46 tests in 0.147s",
          "OK (skipped=4)",
          "SUMMARY platform=linux tests=46 failures=0 errors=0 skipped=4"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "SUMMARY platform=linux tests=46 failures=0 errors=0 skipped=4"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "printf '%s\\n' \"$(cat /tmp/jw-cifixref-b3a95dc.lzxcG7/runner.py)\" | env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B - native",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 46 tests in 0.931s",
          "FAILED (failures=3, skipped=1)",
          "SUMMARY platform=darwin tests=46 failures=3 errors=0 skipped=1",
          "FAILED_ID tests.test_sample_quiet_predicate_evidence.LoadTests.test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child (exit_delay=1)",
          "FAILED_ID tests.test_sample_quiet_predicate_evidence.LoadTests.test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child (exit_delay=60)",
          "FAILED_ID tests.test_sample_quiet_predicate_evidence.LoadTests.test_real_load_tracks_point_one_core_and_guards_worker_budget"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "SUMMARY platform=darwin tests=46 failures=3 errors=0 skipped=1"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-cifixref-b3a95dc.lzxcG7/bench.py normal",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 45 tests in 6.382s", "OK", "EXIT normal 0"]
      },
      "expected": {"exit_code": 0, "tail_regex": "EXIT normal 0"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-cifixref-b3a95dc.lzxcG7/bench.py mutants",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "EXIT cleanup-silent 1",
          "EXIT window-skip 1",
          "Both mutants killed by their intended regression tests."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Both mutants killed by their intended regression tests\\."}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-cifixref-b3a95dc.lzxcG7/file_linux_ladder.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 2.303s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git diff --exit-code",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)", "b3a95dc89b08b82e8297f9699faf12b1bebe1941"]
      },
      "expected": {"exit_code": 0, "tail_regex": "b3a95dc89b08b82e8297f9699faf12b1bebe1941"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: the requested complete module includes CollectionTests.test_real_collect_no_power_reaps_all_recorded_workers, which invokes real collect --no-power for one second. This conflicts with the explicit no-live-collect constraint. Both stdin runs temporarily skipped this test; the normal -m unittest run excluded it. Exact unrestricted R2/R3 verification remains incomplete.",
      "needs": "Confirm whether this existing one-second no-power integration test is authorized, or accept its exclusion. Recommendation: authorize this bounded existing test if complete 46-test evidence is required; then rerun both stdin shapes and the complete module."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Linux-shaped checks forced sys.platform before module import on macOS with Python 3.13.1. They are not native Linux execution.",
      "needs": ""
    }
  ]
}
```

## Findings

None in the diff reviewed. **CLEAN on the change; verification handoff is partial pending F1.**

**R1.** Removing exactly the four added lines reproduces the entire base file byte-for-byte. No assertions or indentation changed. The fake-clock portion remains untouched. The new method also contains the existing N3 pipe-close-on-start-failure check.

**R2.** Summaries are pasted in V2/V3. All three Darwin methods skip under forced Linux. Native stdin yields **three failures across two methods**, as listed in V3. `test_native_qos_classes_read_back_in_subprocess` passes: its separate `python -c` subprocess does not encounter multiprocessing’s `<stdin>` reload failure.

**R3.** Normal execution through `-m unittest`: **45 tests, OK**, excluding only the live-collection integration test. Both `/tmp` mutants were killed:

- `cleanup-silent`: moved ladder test, `exit_delay=60`, assertion `0 != 1` at test line 669.
- `window-skip`: fake-clock rendezvous test, empty-period assertion at test line 649.

No repository files changed.

## Residual risk

**R4.** The ladder fixture itself is portable: `delayed_exit_load_worker` does **not** invoke native QoS. Its existing target is already importable; moving the target cannot fix spawn’s earlier attempt to reload `<stdin>`.

The better coverage improvement is a guarded, file-based or importable CI runner. This requires extracting the inline shard runner, preserving shard selection/exit behavior, and validating it on hosted Linux. A scratch file-based runner passed the ladder test with the parent platform forced to Linux and the test guard bypassed; this is supporting evidence, not native Linux validation.

`set_start_method` would not override the explicit `get_context("spawn")`. `set_executable` changes the interpreter, not the invalid main-script path. Changing to `fork` would exercise different process semantics.

Keep that runner improvement as **queue data**, rather than expanding this four-line fix-forward. The guard currently removes Linux coverage of both the ladder and its adjacent N3 pipe-cleanup check. The fake-clock window regression remains cross-platform.