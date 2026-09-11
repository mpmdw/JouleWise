```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT-CLOSED: the owned runner deadlocks before teardown when a terminated direct child leaves a descendant holding its captured pipes.",
  "workspace": {
    "base_requested": "bc01908",
    "base_mode": "exact",
    "head_start": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "head_end": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "upstream_end": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "branch": "impl/d117-ledger-recovery"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "NOT-CLOSED",
    "findings": [
      {
        "id": "G4-1",
        "severity": "blocker",
        "title": "OwnedPublicProcessRunner can block forever before descendant teardown",
        "site": "tests/owned_process_runner.py:308",
        "scenario": "In a temporary repository copy, OwnedPublicProcessRunner launched a direct Python child that spawned a forever-spinning descendant inheriting stdout/stderr and then exited. process.communicate(timeout=15) raised TimeoutExpired because the descendant retained the pipe descriptors; with the runner's default timeout=None, normal teardown at lines 319-321 is never reached."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_survivor_guard_detects_spinning_descendant tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_ambient_writer_crash_stage_is_inert_without_capability",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 1.212s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_calibration_writer_crash_matrix.CalibrationWriterCrashMatrixTests.test_every_exact_stage_pre_and_post_sigkill_reaches_fresh_governed_exit",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 95.973s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_calibration_writer_crash_matrix",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 147.404s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_calibration_exits.RefusalInventoryTests.test_public_witness_ast_requires_owned_registered_executions",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.562s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test .*\\n\\nOK"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "temporary-copy Python probe under $TMPDIR: copy repository, run OwnedPublicProcessRunner against timeit.py spawning an inherited-pipe `while True: pass` descendant, timeout=15",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "tests/owned_process_runner.py, line 308, in run",
          "subprocess.TimeoutExpired: Command [...] timed out after 15 seconds"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "manual_leak_probe=pass.*group_esrch=True"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "temporary-copy Python capability probe under $TMPDIR covering reuse, symlink, wrong nonce, and wrong stage",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "capability_reuse=refused first_rc=2 second_rc=2 inert_events=1",
          "capability_symlink=refused rc=2 inert_events=1",
          "capability_wrong_nonce=refused rc=2 inert_events=1",
          "capability_wrong_stage=refused rc=2 inert_events=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "capability_reuse=refused.*capability_symlink=refused.*capability_wrong_nonce=refused.*capability_wrong_stage=refused"
      }
    }
  ],
  "flags": []
}
```

## Findings

### G4-1 — Owned runner can deadlock before teardown

Verdict: **NOT-CLOSED**.

At `tests/owned_process_runner.py:308`, the runner calls `process.communicate()` before initiating group teardown. A descendant inheriting the direct child’s captured stdout/stderr keeps those pipes open after the direct child exits.

The temporary-copy probe spawned exactly that shape: the direct child exited, while its spinning descendant retained the pipes. `communicate(timeout=15)` raised `TimeoutExpired`. With the normal default `timeout=None`, the call has no completion trigger, so teardown at lines 319–321 is never reached and the process group survives indefinitely until external interruption.

The committed survivor regression at `tests/test_calibration_writer_crash_matrix.py:746` does not discriminate this defect because it registers the synthetic group directly and never routes it through `OwnedPublicProcessRunner`.

The landed real sampler path redirects its own streams to `DEVNULL`, so the current authorized matrices passed and left no reported survivors. That does not satisfy the shared runner’s dictated descendant-ownership contract.

Checks performed: named survivor and ambient-inertness tests; exhaustive authorized real-site SIGKILL matrix; complete five-test crash module; owned-launch AST gate; temporary-copy inherited-pipe leak probe; temporary-copy capability reuse/symlink/wrong-nonce/wrong-stage probes.

## Residual risk

The capability misuse checks passed but exist only as grader probes, not committed regressions.