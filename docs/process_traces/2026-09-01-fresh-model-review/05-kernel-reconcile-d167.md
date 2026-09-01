```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "D-167 and the live _v5 kernel chain are implemented; NEEDS_SCOPE for tests/test_gen_state.py to replace retired-state test oracles.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "head_end": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "upstream_end": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "branch": "feat/2026-09-01-kernel"
  },
  "pathspec": [
    "RUN_STATE.md",
    "TASK_QUEUE.md",
    "docs/decision_log.md",
    "docs/process/instrument-readiness-audit-charter.md",
    "docs/process/state_kernel.json"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "python3 scripts/gen_state.py --check",
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
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 0.048s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 40 tests in 1.102s",
          "FAILED (failures=7, errors=3)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 40 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gen_state.TestKernelValidity.test_kernel_validates tests.test_gen_state.TestKernelValidity.test_kernel_bytes_are_canonical",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.013s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The kernel-importing test module still hard-codes D117-W-ALPHA, the three retired Qwen2.5 rows, the retired sitting rows, WINDOW-COUNCIL-GATE, the old live-row count, and old lane-head fixtures.",
      "needs": "Expand WRITE_SCOPE to tests/test_gen_state.py and resume so its state oracles can be reconciled to D-167."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/test_gen_state.py"
    ],
    "reason": "The required kernel-importing test module asserts the exact state D-167 retires.",
    "blocked_work": "Updating the exact-ID set, row count, cycle fixture, lane-head adapters, gate assertions, and selection scenarios, then rerunning the module green.",
    "minimal_change": "Replace only retired-state expectations with the D-167 live IDs, empty active-gate state, and V5-G2A-PREFILL-PROBE-01 lane head."
  }
}
```

## Change

Installed D-167 verbatim in the decision index and body, added its actual kernel-change inventory, retired the obsolete gate and six named rows, and added the dependency-linked `_v5`/`_v6` work.

The transfer fiducial now follows the final `_v5` G3 check, retains its diagnostic fences, and records that PR #239 remains held. The charter has only the permitted two-line supersession banner. Generated regions were regenerated without hand-editing surrounding text.

## Verification notes

The generator, freshness test, canonical kernel validation, scope audit, and dependency-chain inspection pass.

`tests.test_gen_state` fails because its hard-coded expectations still require the state D-167 explicitly retires. No out-of-scope test edit was made.