```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "none",
  "summary": "NEEDS_RULING: round-1 F1 repeats the pack-is-its-own-applicability-oracle signature, so the mandated last-round stop prevents another local cure.",
  "workspace": {
    "base_requested": "ee940013abd1f1f3f78b44ba17ebf5346edb36d3",
    "base_mode": "exact",
    "head_start": "ee940013abd1f1f3f78b44ba17ebf5346edb36d3",
    "head_end": "ee940013abd1f1f3f78b44ba17ebf5346edb36d3",
    "upstream_end": "ee940013abd1f1f3f78b44ba17ebf5346edb36d3",
    "branch": "feat/2026-09-04-fan-GAMMA-UNIT-ROSTER-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/GAMMA-UNIT-ROSTER-GUARD-01/05-sol-fix-round-2-report.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/GAMMA-UNIT-ROSTER-GUARD-01/04-delta-reaudit-round-1.md"
  ],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ee940013abd1f1f3f78b44ba17ebf5346edb36d3",
          "feat/2026-09-04-fan-GAMMA-UNIT-ROSTER-GUARD-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ee940013abd1f1f3f78b44ba17ebf5346edb36d3\\nfeat/2026-09-04-fan-GAMMA-UNIT-ROSTER-GUARD-01"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The round-1 re-audit explicitly classifies F1 as the same trust-boundary signature: applicability still comes from mutable bytes inside the roster being policed.",
      "needs": "Rule the external authority that selects the D-131 gamma roster policy and binds A to the small producer and B to the large producer."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No test module was run because the mandatory same-signature early return prohibited a second implementation attempt and this landing touches only this report.",
      "needs": "After the ruling and resumed implementation, run tests.test_gamma_unit_roster_guard with both named counterfactuals."
    }
  ]
}
```

## Change

NEEDS_RULING. No production or test file was changed. Round-1 F1 is expressly the same defect signature as the original refuter finding: the pack still chooses whether D-131 applies, now through `identity_unit_id` rather than `plan_id`. The prompt requires stopping instead of attempting another formulation.

Question: Which caller-owned authority must select the D-131 gamma policy at freeze and arm?

Options considered:

1. Resolve a roster policy from canonical repository-relative `pack_root` (or a reviewed-HEAD successor registry) before reading the projection, then pass that policy explicitly through freeze, frozen-receipt, and arm validation. This removes applicability from the bytes being checked and supports v3/v5 families.
2. Apply the four-unit D-131 rule to every identity projection. This is fail-closed but incorrectly constrains non-gamma families.
3. Detect gamma through another projection field. This repeats the prohibited signature and is rejected.

Recommendation: choose option 1. The external policy should carry the ordered unit IDs (including the ruled `prefill_p<N>` parameter) and exact directional producer mapping, A to the small/1.5B producer and B to the large/7B producer. Generic projection validation should not infer applicability from projection contents. `freeze_projection(pack_root)` and both arm paths already possess `pack_root`; they can select policy before validating any pack or receipt bytes.

Blocked work: production changes and regressions for both re-audit findings await that authority ruling.

| Finding | Structural cure awaiting ruling | Target file:line | Required biting counterfactual |
|---|---|---|---|
| F1, NOT CURED | Remove namespace autodispatch; select an explicit required roster policy from caller-owned pack context and apply it independently to projection and receipt. | `joulewise/identity_pins.py:527-657`; `joulewise/arm_readiness.py:5612-5652,5740-5788` | Rename all A/B IDs to C/D in a self-consistent pack and receipt; freeze and arm must still refuse. Disabling caller policy selection must make the regression fail. |
| F2, NEW | Put exact A→small and B→large producer references in that external policy rather than accepting merely same-within-arm/different-between-arm. | `joulewise/identity_pins.py:544-588`; `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:1760-1829` | Swap the complete A/B producer-reference pairs; validation must refuse. Replacing the directional policy with equality/distinctness-only logic must make the regression fail. |

## Verification notes

No test module was run: the mandated same-signature stop occurred before implementation, and the only session-owned landing is this report.

## Residual risk

F1 and F2 remain open in production until the lead selects the external policy authority and resumes the seat.
