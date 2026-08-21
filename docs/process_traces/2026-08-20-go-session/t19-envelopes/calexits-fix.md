```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Confirmed Python 3.11 stale-descendant rmtree race; test now explicitly accepts only ENOTEMPTY or the equivalent Git-first ENOENT variant.",
  "workspace": {
    "base_requested": "3d0b48a1cec94a324e694e13c073b4b6785a553d",
    "base_mode": "exact",
    "head_start": "3d0b48a1cec94a324e694e13c073b4b6785a553d",
    "head_end": "3d0b48a1cec94a324e694e13c073b4b6785a553d",
    "upstream_end": "3d0b48a1cec94a324e694e13c073b4b6785a553d",
    "branch": "fix/calexits-311-errno"
  },
  "pathspec": ["tests/test_calibration_exits.py"],
  "unowned_dirty": [],
  "verdict": {
    "cause": "confirmed",
    "remediation": "fixed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3.11 -m unittest tests.test_calibration_exits.CalibrationExitReliabilityTests.test_forced_auto_maintenance_mutation_reproduces_cleanup_race > /tmp/calexits-forced-py311-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["RACE_EXERCISED=0 NO_RACE_PRE_WRITE=1 TRACE_INCOMPLETE=0", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3.11 -m unittest tests.test_calibration_exits > /tmp/calexits-module-py311-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 463.311s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 31 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3.13 -m unittest tests.test_calibration_exits.CalibrationExitReliabilityTests.test_forced_auto_maintenance_mutation_reproduces_cleanup_race > /tmp/calexits-forced-py313-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["RACE_EXERCISED=1 NO_RACE_PRE_WRITE=0 TRACE_INCOMPLETE=0", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test[\\s\\S]*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The causal rmtree interleaving is locally reproduced on Python 3.11; the exact hosted Git version/change was not supplied, so Git-version causation remains probable rather than confirmed.",
      "needs": "Record git --version and runner image on the next 3.11 CI run."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Python 3.14 was unavailable locally; Python 3.13 demonstrated the same lower-level ENOENT-ignore behavior.",
      "needs": "Confirm the existing 3.14 job remains green."
    }
  ]
}
```

## Causal chain

Confirmed causal class:

1. The mutation removes local maintenance disables, commits, and starts detached Git maintenance.
2. Immediate `shutil.rmtree()` enumerates an object-store child.
3. Detached Git maintenance removes that child first—after enumeration but before Python 3.11 stats/opens it.
4. Python 3.11 re-raises that stale descendant lookup as `ENOENT`; it is captured in `raw_enotempty`.
5. The test asserts only `ENOTEMPTY`, so it fails before classification. Thus the all-zero printed counters mean “assertion aborted before counters were updated,” not “no race occurred.”

I reproduced this exact ordering locally: deleting `objects/pack/loose` after enumeration yields `PY311_ERRNO=2 ... REMOVER_FIRST=1`; the same probe completes on Python 3.13, which ignores lower-level vanished-child errors.

Why CI flipped is probably timing/environment: Git can instead write into the directory before `rmtree` removes it, producing `ENOTEMPTY`; a faster/different maintenance path can remove a previously enumerated child first, producing `ENOENT`. The 3.11-versus-3.14 result is directly explained by Python’s changed `rmtree` behavior. A hosted Git-version change is not confirmed from the supplied evidence.

## Remediation

Changed only [tests/test_calibration_exits.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a96c43-ea39-4170-96e5-126b77b16301/scratchpad/wtCALEXITS/tests/test_calibration_exits.py:1792).

The raw teardown assertion now permits only:

- `ENOTEMPTY`: Git wrote a child before directory removal.
- `ENOENT`: Git removed an enumerated child first.

All other errors still fail. The output label is now `RAW_CLEANUP_ERRNO`, avoiding the false implication that errno 2 is `ENOTEMPTY`.

Discriminating power remains:

- Detached-maintenance launch and complete child-owned Trace2 evidence are still mandatory.
- Incomplete trace evidence still fails.
- The sibling deterministic cleanup guard still rejects the original bad ordering. An in-memory reversal of cleanup-before-writer-quiescence failed as expected: `rmtree began before the writer observed its stop request` (`/tmp/calexits-broken-cleanup-order.log`).

Exact test tails are in the JSON above; full logs are under `/tmp/calexits-*-final.log`.

## Disproved alternatives

- The all-zero classifier counters do not prove the forced race was absent; the assertion precedes classification.
- No current JouleWise production cleanup was implicated. This test exercises Git plus Python stdlib `rmtree` and the test sandbox cleanup helper.

## Residual risk

No full discovery run was performed; the requested affected module passed on Python 3.11 in 463.311s. No out-of-scope bookkeeping files were changed.

On the next CI run, the parent should check that Python 3.11 reaches a nonzero `RACE_EXERCISED` or `NO_RACE_PRE_WRITE` count with `TRACE_INCOMPLETE=0`, and capture `git --version` plus runner image metadata if `RAW_CLEANUP_ERRNO=2` recurs.