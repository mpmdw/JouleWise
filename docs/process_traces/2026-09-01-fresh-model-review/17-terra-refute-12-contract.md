```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "REFUTE: the close-out validator licenses a forged four-cell census whose slot identities bind to neither authenticated source.",
  "workspace": {
    "base_requested": "HEAD~",
    "base_mode": "exact",
    "head_start": "3935bf15b7e55fcf5b1e2e89bd9028ca8ab38181",
    "head_end": "baec098f67588ff40d3547f07f4018ee5e75565b",
    "upstream_end": null,
    "branch": "feat/d165-dominance-closeout-core"
  },
  "pathspec": [],
  "unowned_dirty": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "joulewise/floor_extraction.py",
    "joulewise/dominance_closeout.py",
    "scripts/build_d165_dominance_closeout.py",
    "tests/test_d165_dominance_closeout.py",
    "docs/contracts/d165_dominance_closeout.md"
  ],
  "verdict": {
    "decision": "REFUTE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "summary": "validate_d165_closeout accepts an all-passing close-out after every ratio slot is relabeled to invented cell IDs.",
        "location": "joulewise/dominance_closeout.py:1097-1163,1202-1232"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "summary": "The stage-2 interface is not callable from the described mint output and the contract omits required replay constants.",
        "location": "docs/contracts/d165_dominance_closeout.md:47-54,104-107,150-168"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_floor_extraction tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found",
          "['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-closeout']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_ratio_predicate_and_zero_denominator_refusal tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_census_is_eight_ordinary_plus_four_comparative_common_mode tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_ratio_equal_to_two_passes tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_zero_denominator_refuses_with_named_reason tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_missing_sidecar_cell_stops_with_neither_branch tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_source_hash_mutation_refuses_validation tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_validators_reject_missing_extra_and_nonfinite_fields tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_branch_a_and_branch_b_fixtures tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_generator_imports_shared_core_and_registration_bytes_are_unchanged tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_extraction_total_stays_bit_identical_after_split_exposure tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_measured_pair_reshaped_as_one_cell_sidecar_round_trips",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 11 tests in 0.033s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox has no writable temporary directory, so the complete requested pack and floor-extraction modules could not run.",
      "needs": "Re-run V1 in a clean runner with writable /tmp."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The initially dirty core was committed concurrently during review; no repository files were modified by this session.",
      "needs": ""
    }
  ]
}
```

## Findings

1. **F1 — BLOCKER** — `validate_d165_closeout` accepts a forged close-out whose twelve records use four invented `cell_id`s. The validator checks only internal eight/four counts and that the two output arrays use the same IDs, not that those IDs equal the authenticated floor/sidecar IDs (`joulewise/dominance_closeout.py:1097-1163`). Its floor and sidecar comparisons silently skip unknown IDs (`joulewise/dominance_closeout.py:1202-1232`). This violates the required matching-cell census and source-operand binding (`docs/contracts/d165_dominance_closeout.md:196-200,246-250`) and the ruling’s exact authenticated close-out requirement (`docs/process_traces/2026-09-01-fresh-model-review/06b-RULING-d165-artifact-ownership.md:27-34`).

   Concrete forged artifact: starting from the valid four-cell fixture, relabel every ordinary and R_cm record to `forged-a` through `forged-d`, leaving all source hashes untouched. `validate_d165_closeout(...)` returned `[]`; `branch` remained `A` and `dominance_sentence_licensed` remained `True`.

   Minimal fix: require the exact `(floor_cell_id, component)` set for ordinary records and exact floor-cell-ID set for R_cm records; reject unknown IDs before source-result comparisons. Add this forged-ID regression test.

2. **F2 — SHOULD-FIX** — The stage-2 interface is not reproducible from the described mint path. The contract says `blocks` are `_common_mode_block_inputs_from_evidence` outputs plus identities (`docs/contracts/d165_dominance_closeout.md:150-168`), but that output has neither `block_id` nor `delta_j` (`joulewise/floor_extraction.py:245-253,366-373`); deltas are separately carried into `_common_mode_floor_from_block_inputs` (`joulewise/floor_extraction.py:625-652`). Yet the sidecar requires both fields (`joulewise/dominance_closeout.py:80-90`). Separately, the text leaves the authenticated-bound tolerance and exact corner cap external (`docs/contracts/d165_dominance_closeout.md:47-54,104-107`), while production uses `1e-12` (`joulewise/dominance_closeout.py:320-325`) and the cap is 16 (`joulewise/detection_floor.py:110`).

   Minimal fix: specify an explicit mint adapter accepting `block_ids`, `block_deltas_j`, and `_CommonModeBlockInputs` (or a fully specified serialized record), and state the tolerance and cap in the contract.

## Mutation table

| Guard deleted/absent | Named test that still passes |
|---|---|
| Floor/sidecar cell-ID alignment (currently absent) | `test_census_is_eight_ordinary_plus_four_comparative_common_mode` passes after all IDs are forged. |
| Mint-shaped stage-2 adapter | `test_measured_pair_reshaped_as_one_cell_sidecar_round_trips` passes because it hand-reshapes fixture data rather than calling the mint interface. |

## Residual risk

Registration is clean: the HEAD~ and reviewed generator registrations serialized to identical 2,032-byte canonical JSON (SHA-256 `1c0a4a…783a2b`), and the focused golden-readback test passed. The extraction refactor preserves the prior `fsum` then four-step outward-rounding order (`joulewise/floor_extraction.py:470-481`); the focused bit-identity test passed.

Semantic one-character mutations of each finalized manifest, floor artifact, and sidecar were caught by source-hash validation (`joulewise/dominance_closeout.py:739-771`). A one-cell sidecar is accepted only as a standalone diagnostic; at close-out it produces `branch: null`, both licenses false, and a census refusal, matching the ruled stop behavior (`docs/contracts/d165_dominance_closeout.md:227-240`).

VERDICT: REFUTE