```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "D-131's ordered four-unit gamma roster now governs freeze validation and arm-side receipt authentication without changing frozen pack bytes.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-GAMMA-UNIT-ROSTER-GUARD-01"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py",
    "docs/process_traces/2026-09-04-fanout/GAMMA-UNIT-ROSTER-GUARD-01/01-sol-report.md",
    "joulewise/arm_readiness.py",
    "joulewise/identity_pins.py",
    "tests/test_gamma_unit_roster_guard.py"
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
      "cmd": "python3 -m unittest tests.test_gamma_unit_roster_guard",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 0.309s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_identity_pins",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 35 tests in 17.098s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 35 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_integration",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 10 tests in 7.271s", "OK (skipped=5)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests in .*s\\n\\nOK \\(skipped=5\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_decode_contrast_plan",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 25 tests in 36.026s", "OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 25 tests in .*s\\n\\nOK \\(skipped=1\\)"
      }
    },
    {
      "id": "V5",
      "kind": "build",
      "cmd": "python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py --check",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["generation failed: the current frozen identity requires preserve mode"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "checked D-117 gamma"
      }
    },
    {
      "id": "V6",
      "kind": "build",
      "cmd": "python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py --check --preserve-current-frozen-bytes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["checked D-117 gamma d117_contrast_qwen25_1p5b_vs_7b_v3: decode_members=40 prefill_p256_members=40 plan_sha256=56ed0e534f102ad6e0a1da12a4e2f9856ce4fe17e9d8af546bf2323f9d70bcb5 tree_sha256=788f1a20bc5a22f073539e2d0b4df5ffd0b3e82d8b78015c7e668c0cbda8b5a7"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^checked D-117 gamma .*decode_members=40 prefill_p256_members=40.*$"
      }
    },
    {
      "id": "V7",
      "kind": "lint",
      "cmd": "git diff --check && python3 -m py_compile joulewise/identity_pins.py joulewise/arm_readiness.py configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py tests/test_gamma_unit_roster_guard.py",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The default gamma generator check refuses after authenticated readiness source changes make the frozen source census stale; the explicit frozen-byte preservation check passes and no frozen artifact was rewritten.",
      "needs": "At final-head verification, use the explicit --preserve-current-frozen-bytes check for this historical frozen pack."
    }
  ]
}
```

## Change

The freeze path now receives the pack's plan identity and checks the gamma projection against the D-131 roster held outside the pack: `A/decode`, `A/prefill_p256`, `B/decode`, and `B/prefill_p256`, with the A units pointing to the Qwen2.5 1.5B floor producer and the B units pointing to the Qwen2.5 7B floor producer. The same check is applied independently to authenticated freeze and arm receipts. A pack and receipt that agree on the same wrong list therefore no longer pass by self-consistency.

The guard is scoped to the ruled Qwen2.5 gamma plan identity. Other identity-projection families retain their existing schemas. Refusal uses the registered `readiness_identity_artifact_unreadable` reason and includes the observed roster. The freeze counterfactual tests also compare every pack byte before and after refusal, proving that the guard reports the defect without repairing a frozen pack.

| Finding | Decision | Result |
|---|---|---|
| The pack was its own roster oracle. | Put the D-131 roster in shared identity-validation code, keyed by the ruled plan identity. | Missing, reordered, extra, and wrong-producer units refuse before freeze work begins. |
| Arm compared receipt unit identifiers only with the pack's unit identifiers. | Check the authenticated receipt against D-131 before the pack-to-receipt equality comparison. | A self-consistent three-unit pack and receipt refuse. |
| Frozen bytes must not be repaired. | Add validation only; do not regenerate or edit the frozen plan, projection, or receipts. | The preservation check reports the same plan and tree digests as the tracked pack. |

## Clause map

| Ruling proposition | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| Gamma has exactly four ordered units. | `joulewise/identity_pins.py:43-65,503-534` | `tests/test_gamma_unit_roster_guard.py:60-96` | Remove one unit, swap the first two, or append `C/decode`; each mutation is refused. |
| A uses the 1.5B producer and B uses the 7B producer. | `joulewise/identity_pins.py:44-65,503-534` | `tests/test_gamma_unit_roster_guard.py:72-96` | Redirect the first unit to another producer plan; freeze refuses. |
| Freeze validates against the ruling, not only the pack. | `joulewise/identity_pins.py:1802-1806`; `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:1823-1835` | `tests/test_gamma_unit_roster_guard.py:60-96` | Remove the plan-aware roster call; all four structurally valid malformed projections reach the old freeze logic. |
| Arm authenticates the receipt roster against the ruling. | `joulewise/arm_readiness.py:5786-5798` | `tests/test_gamma_unit_roster_guard.py:98-162` | Replace the arm-side roster checker with a no-op; the test's mutually consistent malformed pack and receipt return `PASS`. |
| Existing gamma bytes and valid evidence remain accepted. | `joulewise/identity_pins.py:2202-2213`; `joulewise/arm_readiness.py:5612-5674` | `tests/test_gamma_unit_roster_guard.py:164-176` | Change any ruled roster field in the tracked evidence; validation no longer returns `PASS`. |

## Verification notes

The repository-wide test suite was not run, as required by the preflight rule. V5 records the expected frozen-source-census refusal from the default command. V6 uses the generator's explicit preservation mode and proves the current gamma science and configuration outputs remain byte-identical while leaving the frozen tree unchanged.

## Residual risk

No design ruling, hardware action, or scope expansion is needed for this row. After harvest, the magistrate should update `docs/process/state_kernel.json` to close the row, regenerate the owned `TASK_QUEUE.md` and `RUN_STATE.md` projections, and cite `tests/test_gamma_unit_roster_guard.py::GammaUnitRosterGuardTests.test_freeze_refuses_every_counterfactual_gamma_roster` as the producer regression. Those magistrate-owned files were intentionally not edited here.
