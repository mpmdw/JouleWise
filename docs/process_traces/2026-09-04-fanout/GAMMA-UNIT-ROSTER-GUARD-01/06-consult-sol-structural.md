```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The repeated oracle finding is caused by putting pack-specific applicability inside a generic in-band validator; re-scope to the unconditional gamma generator fence and retire the runtime guard mission.",
  "workspace": {
    "base_requested": "323dd715",
    "base_mode": "exact",
    "head_start": "323dd71555ae91b6d9565fa63e0abe1de299fe0a",
    "head_end": "323dd71555ae91b6d9565fa63e0abe1de299fe0a",
    "upstream_end": "323dd71555ae91b6d9565fa63e0abe1de299fe0a",
    "branch": "feat/2026-09-04-fan-GAMMA-UNIT-ROSTER-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/GAMMA-UNIT-ROSTER-GUARD-01/06-consult-sol-structural.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "joulewise/identity_pins.py:527-589,592-657,2071-2096; joulewise/arm_readiness.py:5612-5652,5740-5788; configs/campaigns/d117_contrast_v5/generate_configs.py:2825-2859,3232",
        "text": "Pack-specific applicability is being inferred from the same in-band object the rule validates. The active gamma generator already owns an unconditional exact D-131 roster check, so the added generic runtime guard is both structurally unable to be an external oracle and unnecessary under D-161."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "test \"$(git rev-parse HEAD)\" = 323dd71555ae91b6d9565fa63e0abe1de299fe0a && rg -n 'def validate_gamma_identity_unit_roster|validate_gamma_identity_unit_roster\\(' configs/campaigns/d117_contrast_v5/generate_configs.py && rg -n 'test_gamma_identity_roster_is_exact_and_rejects_three_units' tests/test_d117_contrast_v5_pack.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "2825:def validate_gamma_identity_unit_roster(tree: Mapping[str, Any]) -> None:",
          "3232:    validate_gamma_identity_unit_roster(tree)",
          "1020:    def test_gamma_identity_roster_is_exact_and_rejects_three_units(self) -> None:"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1020:.*test_gamma_identity_roster_is_exact_and_rejects_three_units"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check -- docs/process_traces/2026-09-04-fanout/GAMMA-UNIT-ROSTER-GUARD-01/06-consult-sol-structural.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No test was run because this consult makes a structural claim from the inspected production and test boundaries; the requested proving mutation remains the resumed implementation's acceptance test.",
      "needs": "Run the single generator-boundary mutation test after the magistrate adopts the re-scope."
    }
  ]
}
```

## Findings

**Q1 — F1 (blocker).** The repeated signature is architectural: `validate_identity_pin_projection(value)` is a generic value validator with no trusted pack-role or policy input, yet it invokes a D-131 policy (`joulewise/identity_pins.py:592-657`). The helper must therefore discover applicability from the payload; round 0 used the payload's `plan_id`, and round 1 merely moved that choice to `identity_unit_id`, whose no-match return is explicit at `joulewise/identity_pins.py:534-541`. Freeze supplies only the attachment to that generic validator (`joulewise/identity_pins.py:2071-2096`), while both arm paths repeat the same in-band decision over pack/receipt bytes (`joulewise/arm_readiness.py:5612-5652,5740-5788`); changing the selector can never make it independent. The secondary producer-direction miss is the same abstraction leak: a legacy v3 literal is generalized into equality/distinctness at `joulewise/identity_pins.py:573-583`, discarding D-131's directional smaller/larger policy.

**Q2 — threat model.** Classify the *repeated applicability-oracle bypass* as operator-only and downgrade it under D-161, while preserving roster correctness itself as a pre-registration/evidence invariant. A missing unit can omit the identity evidence for a claim-bearing arm, so a gamma constructor must fail before mint; but defeating every in-pack selector coherently (IDs, producer references, receipt, sidecars, and reviewed bytes) is deliberate trusted-operator conduct, not an accidental or physical failure. The active `_v5` gamma generator already has the proper mistake fence: it constructs the four ordered units (`configs/campaigns/d117_contrast_v5/generate_configs.py:2586-2617`), compares them to the exact directional policy (`:2825-2859`), and calls that check unconditionally before publishing the tree (`:3232`), consistent with D-161's tamper-evident rather than tamper-proof model (`docs/decision_log.md:207`). The branch's generic freeze/arm anti-forgery machinery should therefore be removed, not given a third mutable applicability key; historical `_v3` bytes remain untouched.

**Q3 — cure and proof.** Re-scope to construction-time policy ownership, then retire this production-guard mission: the gamma-specific generator is the applicability boundary by construction, and the generic projection validator remains family-neutral. Make the gamma constructor's exact D-131 check the single source for ordered IDs and A→smaller/B→larger producer mapping; arm authenticates the frozen receipt against the reviewed pack, not independently against a duplicated roster constant. The one proving test should replace/intercept `build_tree` during `generate_pack` so it returns a coherently renamed `C/...`,`D/...` four-unit roster with the complete A/B producer pairs swapped, then assert `gamma_identity_unit_roster_invalid` occurs before `plan_tree.json` is published; that single boundary mutation proves both F1 and F2 without inventing an oracle.

**Q4 — magistrate row, verbatim.** “RE-SCOPE: D-131 roster completeness is a pre-registration/evidence invariant, but coherent trusted-operator rewrites are outside D-161. Remove the generic runtime D-131 dispatch and freeze/arm hooks; keep the active gamma generator's unconditional exact-roster check as the pre-mint mistake fence. Acceptance is one generator-boundary C/D-rename plus A/B-producer-swap mutation that must refuse before publishing `plan_tree.json`. On green, RETIRE GAMMA-UNIT-ROSTER-GUARD-01 as superseded by that generator-owned check.”

## Residual risk

The existing test mutates an already-generated tree and calls the validator directly (`tests/test_d117_contrast_v5_pack.py:1020-1042`); until the Q3 boundary mutation exists, it does not prove the generator cannot omit the unconditional call.
