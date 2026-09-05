```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "The D-131 gamma roster guard no longer trusts mutable plan_id dispatch, and the refuter's exact freeze and arm spoof now refuse.",
  "workspace": {
    "base_requested": "aa33b0a8a5e8db6c03351cd23f8e75a203f1dcde",
    "base_mode": "exact",
    "head_start": "aa33b0a8a5e8db6c03351cd23f8e75a203f1dcde",
    "head_end": "aa33b0a8a5e8db6c03351cd23f8e75a203f1dcde",
    "upstream_end": "aa33b0a8a5e8db6c03351cd23f8e75a203f1dcde",
    "branch": "feat/2026-09-04-fan-GAMMA-UNIT-ROSTER-GUARD-01"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py",
    "docs/process_traces/2026-09-04-fanout/GAMMA-UNIT-ROSTER-GUARD-01/03-sol-fix-round-1-report.md",
    "joulewise/arm_readiness.py",
    "joulewise/identity_pins.py",
    "tests/test_gamma_unit_roster_guard.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/GAMMA-UNIT-ROSTER-GUARD-01/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gamma_unit_roster_guard tests.test_identity_pins tests.test_arm_readiness_integration tests.test_d117_decode_contrast_plan tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 122 tests in 72.372s", "OK (skipped=6)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 122 tests in .*s\\n\\nOK \\(skipped=6\\)"
      }
    },
    {
      "id": "V2",
      "kind": "build",
      "cmd": "python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py --check --preserve-current-frozen-bytes && git diff --check && python3 -m py_compile joulewise/identity_pins.py joulewise/arm_readiness.py configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py tests/test_gamma_unit_roster_guard.py",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The real MLX-backed idempotent freeze/arm path was not rerun in this agent-loaded session; production loader/authenticator seams, all importing focused modules, and frozen-byte preservation were exercised instead.",
      "needs": "Lead final verification may run the real MLX-backed freeze/arm path from its controlled environment."
    }
  ]
}
```

## Change

The validator no longer accepts `plan_id` as an applicability switch. Any identity projection using the reserved gamma `A/...` or `B/...` unit namespace must have the D-131 order `A/decode`, `A/prefill_p<N>`, `B/decode`, `B/prefill_p<N>`, matching prefill lengths, one producer per arm, and distinct A/B producers. The v3 pack retains its exact ruled producer references; the parameterized v5 shape is covered without hard-coding `p256`.

| Finding | Cure | Production site | Biting regression and refuter counterfactual |
|---|---|---|---|
| F1: mutable `plan_id` disabled the roster guard at freeze and arm; v5 IDs also missed it. | Removed `plan_id` dispatch and made gamma namespace/shape validation intrinsic to projection validation and receipt authentication. | `joulewise/identity_pins.py:527-589,592-657`; `joulewise/arm_readiness.py:5623-5652,5782-5788` | `tests/test_gamma_unit_roster_guard.py:98-127` drops `B/prefill_p256` and changes plan/window IDs to `plan-not-d131-gamma`; `:129-198` applies the same plan/window/receipt spoof at arm; `:200-222` covers `prefill_p512`. |

The v3 generator now calls the plan-ID-independent projection validator. No frozen plan, projection, receipt, or sidecar bytes changed.

## Verification notes

Per the mission preflight rule, no repository-wide discovery run was performed. The focused run includes the touched guard plus identity-pin, arm-integration, v3 campaign, and v5 campaign modules. The magistrate ruling file contains no mission-specific row; its general instruction places this completed-row seat in the gauntlet and does not alter D-131.

## Residual risk

No scope expansion or new ruling is needed. The magistrate-owned state files remain untouched; the prior report's proposed closure action remains the exact next state update, so no new or amended row text is required from this fix round.
