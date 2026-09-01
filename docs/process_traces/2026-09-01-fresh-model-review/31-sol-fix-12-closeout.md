```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the independent D-165 census, adapter, output-safety, contract, and regression fixes; full lineage binding needs a ruling because finalized manifests do not record the required operands.",
  "workspace": {
    "base_requested": "baec098f67588ff40d3547f07f4018ee5e75565b",
    "base_mode": "exact",
    "head_start": "baec098f67588ff40d3547f07f4018ee5e75565b",
    "head_end": "baec098f67588ff40d3547f07f4018ee5e75565b",
    "upstream_end": null,
    "branch": "feat/d165-dominance-closeout-core"
  },
  "pathspec": [
    "docs/contracts/d165_dominance_closeout.md",
    "joulewise/dominance_closeout.py",
    "scripts/build_d165_dominance_closeout.py",
    "tests/test_d165_dominance_closeout.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_ratio_predicate_and_zero_denominator_refusal",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.005s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_d165_dominance_closeout tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "..................................",
          "----------------------------------------------------------------------",
          "Ran 34 tests in 2.881s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 34 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_ratio_predicate_and_zero_denominator_refusal",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.002s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'import hashlib; from configs.campaigns.d117_contrast_v5 import generate_configs as g; from joulewise.analysis_manifest_v3 import canonical_json_bytes; print(hashlib.sha256(canonical_json_bytes(g.dominance_criterion_registration())).hexdigest())'",
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
      "kind": "lint",
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: finalized manifest blocks record identity and member positions, but not per-block delta_j, replay width, or replay sign operands. L-F1 cannot be closed without choosing a new authority for those values.",
      "needs": "Rule whether to add a hash-bound replay-operand attachment, extend finalized blocks, or replace the required manifest-operand comparison with authenticated bundle re-derivation."
    }
  ]
}
```

## Change

A census here means the exact required set of record identities.

| Ruling | Cure | File:line | Regression |
|---|---|---|---|
| T-F1 / L-F2 | Requires exactly the eight floor-cell/component pairs and four floor-cell common-mode records. Unknown and missing identities are named errors; invalid records force neither-branch fields. | [dominance_closeout.py](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1001), [dominance_closeout.py](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1283) | [Terra forged IDs](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:272), [Luna forged cell](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:297) |
| L-F1 | Not completed: the required manifest operands do not exist. No partial lineage wire was invented. | [analysis_manifest_v3.py](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3167) | Forged-sidecar, wrong-manifest-hash, block-membership, and operand-mismatch regressions remain blocked. |
| T-F2 | Added the sole mint adapter from `block_ids`, `block_deltas_j`, and extraction-owned block inputs. The contract now states the `1e-12`-second tolerance and 16-block cap directly. | [dominance_closeout.py](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:295), [contract](/Users/edr/code/JouleWise-wt-closeout/docs/contracts/d165_dominance_closeout.md:47), [contract](/Users/edr/code/JouleWise-wt-closeout/docs/contracts/d165_dominance_closeout.md:147) | [adapter regression](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:820) |
| L-F3 | Output uses one atomic exclusive-open operation and refuses with `output_already_exists`. | [build script](/Users/edr/code/JouleWise-wt-closeout/scripts/build_d165_dominance_closeout.py:224) | [output-exists regression](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:748) |
| L-F4 / L-F5 | Tests now obtain a finalized manifest through the production finalizer, route replay blocks through the production adapter, and apply one-defect guard matrices. | [production fixture](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:88) | [sidecar matrix](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:406), [close-out matrix](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:547), [builder matrix](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:621) |
| L-F6 | Removed the trailing blank line; `git diff --check` passes. | [contract](/Users/edr/code/JouleWise-wt-closeout/docs/contracts/d165_dominance_closeout.md:252) | V5 |

## Lineage binding

Lineage binding means checking replayed data against the finalized record from which it came.

The finalized manifest currently records:

- `blocks[].block_id`, `block_number`, and `position_entry_ids` at [analysis_manifest_v3.py](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3167).
- Contrast-level block identities and difference orientation at [analysis_manifest_v3.py](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3696).
- Only a path, digest, schema, and identity for the aggregate floor artifact at [analysis_manifest_v3.py](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3649).

It does not record per-block `delta_j`, shared/local replay width, or a per-block replay-sign operand. Those values exist transiently around [floor_extraction.py](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_extraction.py:2755), while `_CommonModeBlockInputs` itself contains only sweeps, the zero point, residual widths, windows, and the envelope sum at [floor_extraction.py](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_extraction.py:244).

NEEDS_RULING:

- Question: Which authenticated artifact should own the absent per-block operands?
- Options considered:
  1. Extend finalized `blocks[]`.
  2. Add a separately hashed replay-operand attachment referenced by the finalized manifest.
  3. Amend the comparison rule to rederive operands from manifest-indexed authenticated bundles.
- Recommendation: option 2, preserving the finalized manifest’s outcome-blind design while binding complete operand bytes.
- Blocked work: L-F1, `finalized_manifest_sha256`, operand lineage validation, and its four named regressions.

## Guard table

A guard is a validation check that stops malformed or forged input.

| Guard | Test |
|---|---|
| Exact ordinary and common-mode cell census | `test_terra_relabel_all_cells_to_forged_ids_refuses_neither_branch`; `test_luna_replace_first_cell_id_with_forged_cell_refuses` |
| Sidecar schema and identity | `test_replay_sidecar_guard_matrix_trips_one_named_guard_per_case` |
| Sidecar cell and block uniqueness | Same matrix: `cell census`, `block census` |
| Absolute common-mode cancellation license | Same matrix: `absolute cancellation license` |
| Bracket digest and operative bound | Same matrix: `bracket authentication`, `operative bound authentication` |
| Exact-corner cap | Same matrix: `exact corner cap` |
| Ordinary ratio, split, and replay arithmetic | Same matrix: `ordinary arithmetic`, `split arithmetic`, `replay arithmetic` |
| Close-out schema and source digest | `test_closeout_guard_matrix_trips_one_named_guard_per_case` |
| Floor operands and sidecar results | Same matrix: `source operand arithmetic`, `source result arithmetic` |
| Branch licensing | Same matrix: `branch license` |
| Builder floor/component/operand/schema gates | `test_builder_guard_matrix_refuses_named_invalid_sources` |
| Zero denominator | `test_zero_denominator_refuses_with_named_reason` |
| Missing sidecar cell | `test_missing_sidecar_cell_stops_with_neither_branch` |
| Existing output | `test_cli_refuses_to_overwrite_an_existing_output` |
| Mint adapter alignment | `test_mint_adapter_rejects_misaligned_inputs_with_named_reason` |
| Manifest hash, manifest block membership, manifest operand equality | Blocked by NEEDS_RULING |

## Verification notes

Exact targeted command and tail:

```text
python3 -m unittest tests.test_d165_dominance_closeout tests.test_d117_contrast_v5_pack
..................................
----------------------------------------------------------------------
Ran 34 tests in 2.881s

OK
```

Golden readback passed before and after. The canonical registration digest remains exactly:

```text
1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b
```

`git diff --stat`:

```text
 docs/contracts/d165_dominance_closeout.md |  45 +--
 joulewise/dominance_closeout.py           | 150 ++++++++-
 scripts/build_d165_dominance_closeout.py  |  10 +-
 tests/test_d165_dominance_closeout.py     | 500 +++++++++++++++++++++++++++---
 4 files changed, 630 insertions(+), 75 deletions(-)
```

## Residual risk

L-F1 remains a blocker: until operand authority is ruled and implemented, a self-consistent forged replay sidecar can still satisfy the existing arithmetic-only validation.