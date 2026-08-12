```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "The hosted failure is probably a missed real-writer window plus an unsynchronized, parent-owned Git trace assertion—not event loss or a JouleWise production defect.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "60d9e42a8204c3a117a577ddb4680fcb30814a26",
    "head_end": "60d9e42a8204c3a117a577ddb4680fcb30814a26",
    "upstream_end": "7a76a295d8ff089820a12f6d917323416b475db5",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "probable",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_calibration_exits.CalibrationExitReliabilityTests.test_forced_auto_maintenance_mutation_reproduces_cleanup_race",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "for iteration in {1..30}; do python3 -m unittest tests.test_calibration_exits.CalibrationExitReliabilityTests.test_forced_auto_maintenance_mutation_reproduces_cleanup_race || exit $?; done",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["All 30 invocations passed", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\nimport io, os, shutil, time, unittest\nfrom unittest import mock\nfrom tests.test_calibration_exits import CalibrationExitReliabilityTests\nreal = shutil.rmtree\ntombs = []\ndef shortened(path, *args, **kwargs):\n    p = Path(path)\n    if p.name.startswith('joulewise-exit-witness-') and p.exists():\n        q = p.with_name(p.name + '-shortened-window')\n        os.rename(p, q)\n        tombs.append(q)\n        time.sleep(0.02)\n        return None\n    return real(path, *args, **kwargs)\nout = io.StringIO()\nsuite = unittest.TestSuite([CalibrationExitReliabilityTests('test_forced_auto_maintenance_mutation_reproduces_cleanup_race')])\ntry:\n    with mock.patch.object(shutil, 'rmtree', side_effect=shortened):\n        unittest.TextTestRunner(stream=out, verbosity=0).run(suite)\nfinally:\n    time.sleep(0.1)\n    for tomb in tombs:\n        real(tomb, ignore_errors=True)\nassert 'line 1470' in out.getvalue(), out.getvalue()\nprint('WRITER_EXIT_MISSING_REPRODUCED=1 DELAY_S=0.02')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["WRITER_EXIT_MISSING_REPRODUCED=1 DELAY_S=0.02"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "WRITER_EXIT_MISSING_REPRODUCED=1 DELAY_S=0\\.02"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The exact Ubuntu/Python 3.11/Git terminal interleaving was available only through the supplied hosted trace; the bench was macOS, Python 3.13.1, Apple Git 2.50.1.",
      "needs": "Confirm the proposed classifier on the exclusive Ubuntu 3.11 and 3.14 jobs after implementation."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced concurrently from 60d9e42a to 7a76a295 while the detached read-only worktree remained at its exact starting head.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The terminating design is proposed, not implemented; the current one-shot parent-child_exit assertion remains flaky.",
      "needs": "Land and host-verify the test-only repair."
    }
  ]
}
```

## Causal chain

Probable verdict: **(a), compounded by a test-side observation race**.

1. The test removes the local maintenance controls and triggers detached Git maintenance.
2. It immediately runs `shutil.rmtree`, then reads the shared `GIT_TRACE2_EVENT` file exactly once.
3. `object_writer_starts` uses the maintenance parent’s `child_start` record. That proves a launch attempt, not that `pack-objects` reached its object-writing phase while the repository still existed.
4. `writer_exits` then demands the parent’s later `child_exit` record. On the supplied hosted trace, the child instead emitted its own exit 128 after finding the repository gone, and the maintenance parent received SIGPIPE. That parent therefore could not emit the demanded `child_exit`.
5. Consequently, `writer_exits == []` does not show a JouleWise exit-path defect. The hosted mutation probably missed the actual write phase, while the assertion depended on an event whose producer died.

Bench evidence:

- The unmodified test passed 30/30.
- Instrumented normal teardown showed the child’s own `pack-objects` lifetime overlapping `rmtree` in 10/10 trials.
- Shortening only the observation window reproduced line 1470 deterministically: 3/3 at 20 ms and 3/3 at 50 ms lacked `child_exit`; waiting 100 ms passed 3/3.
- That shortened-window probe does not reproduce Linux repository deletion—it proves only that the current one-shot trace snapshot is causally sufficient to produce the signature. The child-exit-128/SIGPIPE terminal variant remains hosted-runner evidence.

The faulty assertion is in [tests/test_calibration_exits.py](</private/tmp/claude-501/-Users-edr-code-JouleWise/7c344e29-f3e2-455c-9384-1902c950c106/scratchpad/wtH-consult/tests/test_calibration_exits.py:1470>).

## Remediation

Use child-owned trace evidence and make the real-Git leg an honest classifier:

- Add `_read_complete_trace_events(path)`. Parse only newline-terminated JSON records; retain and retry an incomplete final record rather than discarding or failing it.
- Add `_wait_for_pack_terminal(path, deadline_s=2.0)`, polling by monotonic deadline. Locate the child’s own `start` event by exact `pack-objects` argv and correlate its own SID—not a PID used for signalling.
- Classify the write-phase interval from the child’s own `region_enter`/`region_leave` events for `category == "pack-objects"` and `label == "write-pack-file"`.
- Treat the child’s own `atexit`, `exit`, or terminal `signal` as completion evidence. Do not require the maintenance parent’s `child_exit`.
- Remove `writer_exits`, `live_object_writer_pid`, the `os.kill(pid, 0)` loop, and the emergency PID kill from `test_forced_auto_maintenance_mutation_reproduces_cleanup_race`.

The exact outcome assertion should become:

- `RACE_EXERCISED` when raw `ENOTEMPTY` occurred, or the child-owned `write-pack-file` interval overlapped `rmtree`.
- `NO_RACE_PRE_WRITE` when the child terminated without such overlap.
- Failure for incomplete/unclassifiable trace evidence.
- Assert exactly one classification and always print counts, for example `RACE_EXERCISED=0 NO_RACE_PRE_WRITE=1 TRACE_INCOMPLETE=0`.

To keep FIND-1 non-vacuous, make the companion owned-writer regression the authoritative deterministic closure:

- Replace the timing delays in `test_delayed_object_writers_never_escape_bounded_cleanup` with `ready`, `stop_observed`, and `final_write_complete` events.
- Have the writer register, wait for the stop request, perform one already-scheduled final object write, set `final_write_complete`, and exit.
- In patched `rmtree`, assert `stop_observed`, `final_write_complete`, and `not writer.is_alive()` before delegating to real `rmtree`.
- This deterministically kills the broken ordering where `_cleanup_root()` runs before `runner.close()` joins writers.

Add two pure classifier regressions:

- Child exit 128 plus parent SIGPIPE and no `child_exit`, with no write-phase overlap → `NO_RACE_PRE_WRITE`.
- The same missing parent `child_exit`, but with a child-owned `write-pack-file` overlap → `RACE_EXERCISED`.

This preserves the real Git census, avoids prohibited identity machinery, and guarantees the governed cleanup property is exercised independently of hosted scheduling.

## Disproved alternatives

- **(b), generic event-channel loss:** unsupported. The hosted channel captured the child’s exit and the parent’s SIGPIPE. The demanded event was either read too early or never produced by its signalled parent; it was not silently dropped after emission.
- **(c), JouleWise production writer-exit failure:** unsupported. This assertion observes Git’s internal parent/child trace lifecycle; it does not traverse the production validator’s writer-exit machinery.

## Residual risk

For PRs #135–#137, this exact signature is **non-blocking evidence for branch correctness**: the failing module content came from main and was identical across those PRs, while the same content also passed elsewhere. Record an explicit baseline-flake disposition; do not describe the required check as green or waive it silently.

The defect remains blocking for the shared test baseline until repaired. Any different signature—or any PR touching this test, cleanup ownership, Git configuration, or the exclusive-job environment—must still block and be investigated independently.