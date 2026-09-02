```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented D-165 close-out round 3 with byte-only source authority, manifest-sealed floor authentication, named malformed-input refusals, complete regressions, and replication-grade contract prose.",
  "workspace": {
    "base_requested": "057660e1",
    "base_mode": "exact",
    "head_start": "057660e1c172b7b21af59fde758baf6f466258bd",
    "head_end": "057660e1c172b7b21af59fde758baf6f466258bd",
    "upstream_end": null,
    "branch": "feat/d165-dominance-closeout-core"
  },
  "pathspec": [
    "joulewise/dominance_closeout.py",
    "scripts/build_d165_dominance_closeout.py",
    "tests/test_d165_dominance_closeout.py",
    "docs/contracts/d165_dominance_closeout.md"
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
      "cmd": "python3 -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 26 tests in 13.891s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 26 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_analysis_manifest_v3 tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 36 tests in 2.978s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 36 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4428 tests in 4088.902s",
          "",
          "OK (skipped=128)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4428 tests in .*s\\n\\nOK \\(skipped=128\\)"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c \"import hashlib,json,sys; sys.path.insert(0,'.'); from configs.campaigns.d117_contrast_v5.generate_configs import dominance_criterion_registration as r; print(hashlib.sha256(json.dumps(r(),sort_keys=True,separators=(',',':')).encode()).hexdigest())\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b$"
      }
    },
    {
      "id": "V5",
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
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/contracts/d165_dominance_closeout.md",
          " M joulewise/dominance_closeout.py",
          " M scripts/build_d165_dominance_closeout.py",
          " M tests/test_d165_dominance_closeout.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^( M (docs/contracts/d165_dominance_closeout.md|joulewise/dominance_closeout.py|scripts/build_d165_dominance_closeout.py|tests/test_d165_dominance_closeout.py)\\n?){4}$"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --quiet -- joulewise/analysis_manifest_v3.py joulewise/floor_extraction.py configs/campaigns/d117_contrast_v5/generate_configs.py",
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
      "id": "G1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The cited 48d-COLD-GATE-2-verdict-40b-45b.md is absent from this checkout and HEAD; implementation used the reproduced Packet 1 requirements in the prompt and the binding cold-gate amendment in 40b.",
      "needs": "Lead may compare the resulting diff with the external 48d artifact."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Producer-to-finalizer sidecar custody remains unproven until D165-SIDECAR-EMIT-01 lands.",
      "needs": "Do not cite a close-out in the paper before D165-SIDECAR-EMIT-01 closes."
    }
  ]
}
```

## Change

| Item | Change | Regression | Observed tail |
|---|---|---|---|
| F1 | Byte decoder and sealed-floor guard at `joulewise/dominance_closeout.py:203,1205,1385`; byte-only builder and single-read CLI at `scripts/build_d165_dominance_closeout.py:54,198,218` | `test_forged_sidecar_bytes_cannot_pair_with_closeout_built_from_other_bytes`, `test_floor_bytes_must_match_the_artifact_digest_sealed_by_manifest`, `test_public_closeout_apis_expose_only_source_byte_channels` | `Ran 26 tests … OK` |
| F2 | Entry-boundary catches at `scripts/build_d165_dominance_closeout.py:153` and `joulewise/dominance_closeout.py:366,1623` | `test_build_catches_unhashable_source_membership_as_named_neither`, `test_validate_catches_unhashable_closeout_census_as_named_neither`, adapter unhashable case | Exact named reasons; focused suite `OK` |
| F3 | Exact manifest/sidecar byte-hash, attachment presence/identity, and membership guards at `joulewise/dominance_closeout.py:1181-1286,1417-1423` | Isolated replay hash, all four partial keys, schema identity mismatch, forged pair | All deletion mutations failed their named tests |
| F4 | First-use glossary, forcing-problem examples, byte-only API, exact CLI, exclusive-output semantics, floor-digest problem, and custody limitation at `docs/contracts/d165_dominance_closeout.md:14-58,221-289` | `tests.test_paper_terms_lint` | `Ran 36 tests … OK` |

Public signatures changed from:

- `build(finalized_manifest, floor_artifact, replay_sidecar, *, finalized_manifest_bytes, replay_sidecar_bytes)`
- `validate(value, *, finalized_manifest=None, floor_artifact=None, replay_sidecar=None, finalized_manifest_bytes=None, replay_sidecar_bytes=None)`

to:

- `build(finalized_manifest_bytes, floor_artifact_bytes, replay_sidecar_bytes)`
- `validate(value, *, finalized_manifest_bytes, floor_artifact_bytes, replay_sidecar_bytes)`

Mutation audit:

| Deleted guard | Test that failed | Observed result |
|---|---|---|
| Finalized-manifest raw-byte digest | `test_source_hash_mutation_refuses_validation` | `FAILED (failures=1)` |
| Replay-sidecar raw-byte digest | `test_replay_sidecar_source_byte_hash_guard_is_isolated` | `FAILED (failures=1)` |
| Manifest-sealed floor digest | `test_floor_bytes_must_match_the_artifact_digest_sealed_by_manifest` | `FAILED (failures=1)` |
| Bytes-only public surface | `test_public_closeout_apis_expose_only_source_byte_channels` | `FAILED (failures=1)` |
| Absent attachment guard | builder guard matrix, `manifest attachment` | `FAILED (failures=1)` |
| Partial attachment key census | `test_each_partial_replay_attachment_refuses_as_manifest_lacks_sidecar` | `FAILED (errors=4)` |
| Attachment sidecar-byte digest | builder guard matrix, `sidecar digest` | `FAILED (failures=1)` |
| Attachment schema identity | `test_sidecar_attachment_schema_mismatch_has_identity_reason` | `FAILED (failures=1)` |
| Manifest block membership | builder guard matrix, `manifest block membership` | `FAILED (failures=1)` |
| Builder malformed-source catch | `test_build_catches_unhashable_source_membership_as_named_neither` | `FAILED (errors=1)` |
| Validator malformed-census catch | `test_validate_catches_unhashable_closeout_census_as_named_neither` | `FAILED (errors=1)` |
| Mint-adapter malformed-ID catch | adapter unhashable case | `FAILED (errors=1)` |

## Verification notes

The requested `48d-COLD-GATE-2-verdict-40b-45b.md` source was unavailable in the worktree and repository tree. No scope expansion was needed, and all temporary mutation-audit deletions were restored before final verification.

## Residual risk

`D165-SIDECAR-EMIT-01` remains the external custody gate. The contract now explicitly forbids citing the close-out before that producer-to-finalizer path lands.