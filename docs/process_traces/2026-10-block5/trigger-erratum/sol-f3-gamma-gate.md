```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Route 2 F3 gate passed; the stale state adds only whole_window.not_passed (DISCLOSE).",
  "workspace": {
    "base_requested": "e4b4145a071871c8a3cca85c976433b89b15befd",
    "base_mode": "exact",
    "head_start": "e4b4145a071871c8a3cca85c976433b89b15befd",
    "head_end": "e4b4145a071871c8a3cca85c976433b89b15befd",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": ["tests/test_harvest_b5_trigger_scope_gamma_gate.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "B5_GAMMA_STALE_GATE=1 TMPDIR=\"$PWD/.scratch-fix\" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope_gamma_gate > .scratch-fix/f3-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["sealed_program_identity PASS writer checker"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "sealed_program_identity PASS writer checker"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/.scratch-fix\" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope_gamma_gate > .scratch-fix/f3-opt-out.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=4)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=4\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=\"$PWD/.scratch-fix\" PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope.SealedIdentityTests > .scratch-fix/f3-sealed-identity.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["?? tests/test_harvest_b5_trigger_scope_gamma_gate.py"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^\\?\\? tests/test_harvest_b5_trigger_scope_gamma_gate\\.py$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Route 2 is synthetic; the fresh control also fails fixture provenance checks. Real-model rehearsal execution remains unperformed.",
      "needs": ""
    }
  ]
}
```

## Change

Completed **route 2** with four opt-in tests. No production file changed; no commit was made.

The census found GAMMA-shaped rehearsal windows in `gamma-1` and `gamma-2`. Both lack the desk bracket binding and stored verdict, and their private programs differ from the lane’s programs. Route 1 stopped after this inspection.

Executed real paths:

- Verdict lock, membership resolution, core evaluation, row and basis construction, campaign-log append, and verdict publication.
- Ledger writers, snapshot integrity loader, bracket-binding builder, and bracket evaluator.
- The checker subprocess through the harvest’s unchanged argv construction and default `subprocess.run`.
- Full harvest and the real L4 exclusion function.

Synthetic inputs remain: member evaluations, idle telemetry, reference identity authentication, calibration candidate discovery, capture contents, and fresh launch lineage. Snapshot loading used `verify_custody=False`. Writer/checker source identity against the current-program rehearsal passed.

## Verification notes

Both harvest arms produced exactly these window-removing codes:

| Code | Catalog effect | Control payloads | Stale payloads |
|---|---|---:|---|
| `calibration.capture_battery_unmeasured` | `EXCLUDE_WINDOW` | 2 | Identical |
| `neg8.bound_not_derived` | `EXCLUDE_WINDOW` | 1 | Identical |

The stale state added only `whole_window.not_passed` (`DISCLOSE`). Its conditions contain `calibration_acceptance_bound_stale`. No other flag payload changed.

Both writer rows contain `member_failures: []`. The stale basis has null calibration endpoints and no `launch_lineage`.

| Executed path | Exit | Status | Actual last line |
|---|---:|---|---|
| Writer, control | 0 | passed | `decision: passed` |
| Writer, stale | 1 | failed | `condition: calibration_acceptance_bound_stale` |
| Checker, both arms | 1 | report present; F5-2 FAIL | `SUMMARY pass=5 skip=1 fail=4` |

Checker assertions were identical in both arms:

- **PASS:** NR14-LAYOUT, S11-A1, S11-A2, F5-3, F5-4.
- **FAIL:** S11-A3, S11-A5, F5-1, F5-2.
- **SKIP:** S11-A4.

The handler mapping was executed through **66 injected outcome cases**, plus **3 precondition cases**. Injection was confined to the separate mapping test.

| Outcome | Harvest codes |
|---|---|
| Usable report, F5-2 only PASS, exit 0 or 1 | None |
| Usable report, F5-2 PASS, exit outside `{0,1}` | `g3.recompute_failed` |
| F5-2 FAIL, SKIP, absent, or conflicting statuses | `g3.recompute_failed` |
| Any other FAIL assertion | Adds `g3.assertion_failed` |
| Report absent, malformed, non-object, or assertions unusable | `g3.recompute_failed`; other FAIL stdout rows additionally produce `g3.assertion_failed` |
| Usable report with contradictory stdout | Report controls the result |
| Spawn failure or timeout | `g3.recompute_failed`, `records.collector_failed` |
| G3 skipped or required desk outputs absent | `g3.recompute_failed` |
| Pack lacks analysis manifest | `g3.not_applicable` |

Every code in this mapping has catalog effect **`DISCLOSE`**.

The exact test commands and captured last lines are in the header. Replay requires `mkdir -p .scratch-fix` first. The final opt-in run passed four tests; opt-out skipped all four; sealed-scope identity passed.

Scratch remained below 3 GiB and was deleted. `git diff --name-only` was empty. Final `git status --short`:

```text
?? tests/test_harvest_b5_trigger_scope_gamma_gate.py
```

## Residual risk

This closes the authorized synthetic gate. The checker’s control is not a clean provenance pass; real-model rehearsal execution remains unperformed. The lead’s next step is to review and rerun the opt-in module before recording the gate closure.

F3: CLOSED (no window-removing code arises from the stale state)