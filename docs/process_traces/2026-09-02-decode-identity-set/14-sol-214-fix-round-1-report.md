```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented and verified F-A–F-L and F-N–F-P; F-M requires two out-of-scope reason-census files.",
  "workspace": {
    "base_requested": "1a60808974dea46c54e11dc3fc6900ab6230644d",
    "base_mode": "exact",
    "head_start": "1a60808974dea46c54e11dc3fc6900ab6230644d",
    "head_end": "1a60808974dea46c54e11dc3fc6900ab6230644d",
    "upstream_end": "1a60808974dea46c54e11dc3fc6900ab6230644d",
    "branch": "fix/2026-09-02-decode-identity-set"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "docs/contracts/d165_dominance_closeout.md",
    "docs/contracts/identity_pin_projection.md",
    "docs/decision_log.md",
    "docs/phase_2/gamma_arm_readiness.md",
    "joulewise/analysis_engine/inputs.py",
    "joulewise/identity_pins.py",
    "tests/test_analysis_inputs.py",
    "tests/test_d117_contrast_v5_pack.py",
    "tests/test_identity_pins.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_identity_pins tests.test_analysis_inputs tests.test_analysis_engine tests.test_d165_dominance_closeout tests.test_night_gate tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 201 tests in 36.151s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 201 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_decode_declaration_is_rule_derived_not_folded_from_emission tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_v5_pack_refuses_extra_byte_identical_decode_member tests.test_identity_pins.SharedDerivationTests.test_declared_manifest_identity_cardinality_refuses_synthetic_mismatch tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_v5_pack_refuses_one_member_runtime_pin_drift tests.test_identity_pins.ProjectionLifecycleTests.test_verify_refuses_current_runtime_triple_mismatch tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_generated_pack_gate_and_caller_refuse_stale_receipt_bytes tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_multi_identity_transport_requires_declared_subset_and_skips_exact_cell tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_v5_pack_refuses_tampered_declared_manifest_bytes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 8 tests in 7.192s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "F-M needs the governed transport-reason census and its exact-census regression updated, but both files are outside WRITE_SCOPE.",
      "needs": "Expand WRITE_SCOPE with joulewise/detection_floor.py and tests/test_detection_floor.py."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/detection_floor.py",
      "tests/test_detection_floor.py"
    ],
    "reason": "Register floor_identity_set_unauthenticated in TRANSPORT_REASON_CODES and update test_reason_code_set_is_closed_v1_set.",
    "blocked_work": "F-M distinct authentication-failure reason and its analysis-engine regression.",
    "minimal_change": "Add one reason literal to the governed tuple and exact-census expectation, then plumb that reason through the already-authorized analysis files."
  }
}
```

## Change

Implemented the authenticated manifest-byte gate at freeze and verify, exact emitted census and independent identity-cardinality enforcement, runtime-pin/triple checks, pack-digest authentication before consumer-plan trust, unconditional same-condition refusal, strict lineage roots, in-hand identity hashing, exact GAMMA roster/rotation, and governing documentation corrections.

The generator now emits schema-canonical suite-manifest bytes matching their declared effective SHA-256. The dominance registration remained:

`1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`

Fresh TMPDIR generation produced:

- Freeze: `PASS`
- Verify: `PASS`
- Decode census: `4/4/2/2/2/2/2/2`
- Identity counts: decode 8 per arm; prefill 1 per arm

No committed receipt changed. Final diff: 10 files, 817 insertions, 51 deletions.

Same-signature disposition:

- luna 202: F-A killed by both manifest-tamper tests; F-J by the exact-roster test; F-K by the modulo-eight test; F-L/F-N corrected and checked by literal/first-use inspection plus docs freshness.
- Opus 204: F-B/F-D killed by generated-pack gate/caller tests; F-C by the same-condition multi-identity test; F-O/F-P by their lineage and no-recomputation assertions. F-M remains scope-blocked.
- terra 206: M1, M4, M6, M10, and M11 all killed by their named regressions.

All required temporary mutations were also killed and reverted:

- M1 → `test_decode_declaration_is_rule_derived_not_folded_from_emission`
- M4 → `test_generated_v5_pack_refuses_extra_byte_identical_decode_member`
- M6 → `test_declared_manifest_identity_cardinality_refuses_synthetic_mismatch`
- M10 → `test_generated_v5_pack_refuses_one_member_runtime_pin_drift`
- M11 → `test_verify_refuses_current_runtime_triple_mismatch`
- M-gate → `test_generated_pack_gate_and_caller_refuse_stale_receipt_bytes`
- M-guard → `test_multi_identity_transport_requires_declared_subset_and_skips_exact_cell`
- M-manifest → `test_generated_v5_pack_refuses_tampered_declared_manifest_bytes`

## Clause map

| Closure | Production site | Biting test | Counterfactual |
|---|---|---|---|
| F-A | `joulewise/identity_pins.py:1610` | `tests/test_d117_contrast_v5_pack.py:1074,1105` | Skip declared-manifest byte hashing. |
| F-B | `joulewise/analysis_engine/inputs.py:3898` | `tests/test_analysis_inputs.py:547` | Remove committed-pack digest comparison. |
| F-C | `joulewise/analysis_engine/inputs.py:4107,4148` | `tests/test_analysis_inputs.py:595,697` | Re-nest same-condition refusal under single identity. |
| F-D | `joulewise/analysis_engine/inputs.py:3898,4012,4065` | `tests/test_analysis_inputs.py:547,564,584` | Replace consumer gate with `return frozenset()`. |
| F-E | `configs/campaigns/d117_contrast_v5/generate_configs.py:1479` | `tests/test_d117_contrast_v5_pack.py:1007` | Fold declaration from staged emitted configs. |
| F-F | `joulewise/identity_pins.py:1681` | `tests/test_d117_contrast_v5_pack.py:1159` | Accept emitted counts greater than declared. |
| F-G | `joulewise/identity_pins.py:1571,1701` | `tests/test_identity_pins.py:407` | Make cardinality helper always return `None`. |
| F-H | `joulewise/identity_pins.py:1845` | `tests/test_d117_contrast_v5_pack.py:1191` | Remove member runtime-pin/stack equality. |
| F-I | `joulewise/identity_pins.py:2453` | `tests/test_identity_pins.py:702,730` | Remove frozen/current runtime-triple comparison. |
| F-J | `configs/campaigns/d117_contrast_v5/generate_configs.py:2826,3233` | `tests/test_d117_contrast_v5_pack.py:983` | Permit three units or omit roster validation. |
| F-K | `configs/campaigns/d117_contrast_v5/generate_configs.py:1381` | `tests/test_d117_contrast_v5_pack.py:972` | Change prompt count or rotation mapping. |
| F-L | `docs/phase_2/gamma_arm_readiness.md:11`; `docs/contracts/d165_dominance_closeout.md:61`; `docs/decision_log.md:8438` | NOT PINNED: prose-only correction; literal scan and docs-freshness suite performed. | Restore `_v3` `prefill_p256` wording. |
| F-M | `joulewise/analysis_engine/__init__.py:422` | NOT PINNED: blocked on out-of-scope governed census at `tests/test_detection_floor.py:3695`. | Continue collapsing authentication refusal into ordinary unavailable resolution. |
| F-N | `docs/contracts/identity_pin_projection.md:563` | NOT PINNED: prose-ordering requirement verified by first-use inspection. | Move definitions after analysis consumption. |
| F-O | `joulewise/analysis_engine/inputs.py:3880` | `tests/test_analysis_inputs.py:534` | Filter out missing roots while forming the set. |
| F-P | `joulewise/analysis_engine/inputs.py:4079` | `tests/test_analysis_inputs.py:664` | Recompute the identity hash from raw config. |

## Residual risk

F-M cannot be completed soundly inside the current allowlist. The governed census is `TRANSPORT_REASON_CODES` at `joulewise/detection_floor.py:293`, with its exact test at `tests/test_detection_floor.py:3695`.