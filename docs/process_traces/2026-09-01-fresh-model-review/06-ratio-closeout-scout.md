```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Ordinary R operands are already present or derivable in floor artifacts, but no issued artifact preserves the authenticated per-block split needed for R_cm, and the frozen 109-key renderer cannot fill the 126-key _v5 registry.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "head_end": "1d4b4ba47b98cca1782990fa7843a62948a4ed59",
    "upstream_end": "1d4b4ba47b98cca1782990fa7843a62948a4ed59",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-09-01-fresh-model-review/"
  ],
  "verdict": {
    "rows": [
      {
        "row": "D165-ARTIFACT-OWNERSHIP",
        "action": "needs_ruling",
        "reason": "The magistrate must choose whether replay evidence extends the aggregate floor artifact or is emitted as a separately hash-bound sidecar."
      },
      {
        "row": "D165-RATIO-CLOSEOUT",
        "action": "wait_for",
        "reason": "Implementation depends on the artifact-ownership ruling."
      },
      {
        "row": "RENDERER-V5-SUCCESSOR-01",
        "action": "wait_for",
        "reason": "The successor needs the close-out artifact contract and the G2-a prefill selection."
      },
      {
        "row": "FROZEN-DRAFT-AND-RETAINED-CORPORA",
        "action": "do_not_start",
        "reason": "The draft and runs corpora remain immutable."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_render_results_fills",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 43 tests in 1.089s",
          "",
          "FAILED (errors=21)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 43 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_ratio_predicate_and_zero_denominator_refusal tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_common_mode_replay_matches_independent_retained_fixture_calculation tests.test_render_results_fills.InterimVocabularyContractTests.test_renderer_vocabulary_is_frozen_pre_v5 tests.test_render_results_fills.InterimVocabularyContractTests.test_v5_registry_rows_are_unknown_to_frozen_renderer",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "....",
          "----------------------------------------------------------------------",
          "Ran 4 tests in 0.029s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "rg -n 'RENDERER-V5-SUCCESSOR-01' TASK_QUEUE.md docs/process/state_kernel.json docs/process_traces/2026-08-27-t26/WAVE-ROWS.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/process_traces/2026-08-27-t26/WAVE-ROWS.md:68:- RENDERER-V5-SUCCESSOR-01 (row owed): regenerate `scripts/render_results_fills.py` for the `_v5` registry (parser must handle nested `[PREFILL_LENGTH]` keys; template home moves OUT of the frozen 2026-08-07 trace; restore the vocabulary-sync tests the interim contract pinned frozen). Lead-owned, post-G2-a (41 keys unresolved until the selection record). Authority: fill-checklist header ruling + the interim-contract suite note."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "WAVE-ROWS.md:68:.*RENDERER-V5-SUCCESSOR-01"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Artifact ownership for the authenticated R_cm replay is not settled.",
      "needs": "Choose the recommended separate replay sidecar or authorize a new aggregate-floor schema."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full targeted modules require temporary directories, but this runner is read-only; all 21 errors were temporary-directory creation failures.",
      "needs": "Replay V1 in a writable test runner."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "RENDERER-V5-SUCCESSOR-01 is described as a row owed, but its identifier is absent from TASK_QUEUE.md and docs/process/state_kernel.json.",
      "needs": "Lead should register or explicitly retire the successor row."
    },
    {
      "id": "F4",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The workspace advanced concurrently from 3b3839c to 1d4b4ba; none of the cited files changed and this session wrote nothing.",
      "needs": ""
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Artifact ownership | needs_ruling | Magistrate chooses floor-schema extension or separate sidecar | Aggregate floor schema, final-manifest binding |
| Ratio and shared-error close-out | wait_for | Artifact-ownership ruling | Mint estimator, replay arithmetic, close-out schema |
| `_v5` renderer successor | wait_for | Close-out schema and G2-a prefill choice | Renderer, template vocabulary, 126-key registry |
| Frozen draft and retained corpora | do_not_start | Never | `docs/paper/draft-v1.md`, `runs*/` |

## Critical path

A **cell** is one model and one phase, such as 1.7B decode. Each cell has two **components**: absolute, meaning repeated-run scatter within that condition; and comparative, meaning differences from four-run A/B/B/A blocks arranged to cancel slow drift. A **corner** chooses an allowed low or high endpoint for every uncertain input. An **artifact** is a JSON record whose identifiers and hashes bind it to its evidence. A **mint** is the authenticated step that issues the aggregate floor artifact.

### 1. Ordinary ratio operands

The aggregate `joulewise.detection_floor_artifact.v2` is already the nearest complete carrier. For every cell, both `cells[].absolute` and `cells[].comparative` contain:

- `corner_widened_unguarded_floor_j`, the numerator.
- `prediction_component_j`.
- `max_abs_residual_j` for absolute or `max_abs_delta_j` for comparative.

Thus the denominator is always reconstructible as:

```text
absolute point floor    = max(max_abs_residual_j, prediction_component_j)
comparative point floor = max(max_abs_delta_j, prediction_component_j)
```

The point formula is implemented in [joulewise/detection_floor.py:787](/Users/edr/code/JouleWise/joulewise/detection_floor.py:787), while the component records are built at [joulewise/detection_floor.py:1440](/Users/edr/code/JouleWise/joulewise/detection_floor.py:1440) and joined into one cell at [joulewise/detection_floor.py:1579](/Users/edr/code/JouleWise/joulewise/detection_floor.py:1579). The generalized mint constructs those two records at [scripts/mint_floor_artifact_generalized.py:2427](/Users/edr/code/JouleWise/scripts/mint_floor_artifact_generalized.py:2427) and [scripts/mint_floor_artifact_generalized.py:2750](/Users/edr/code/JouleWise/scripts/mint_floor_artifact_generalized.py:2750).

There is no unconditional field literally named `point_unguarded_floor_j`. Some artifacts carry the equivalent nested `point_floor_diagnostic.unguarded_floor_j`, but extraction only emits that diagnostic under the older coded-label condition at [joulewise/floor_extraction.py:1440](/Users/edr/code/JouleWise/joulewise/floor_extraction.py:1440). The unconditional parents above are therefore the dependable denominator source. Extraction rows expose the numerator, parents, widths, and conditional diagnostic at [joulewise/floor_extraction.py:1356](/Users/edr/code/JouleWise/joulewise/floor_extraction.py:1356).

A real, older minted example shows the shape: absolute numerator and point parents at [df-ph-decode-floor-mint1.json:83](/Users/edr/code/JouleWise/df-ph-decode-floor-mint1.json:83), and comparative values at [df-ph-decode-floor-mint1.json:660](/Users/edr/code/JouleWise/df-ph-decode-floor-mint1.json:660). It is diagnostic-era evidence, not a `_v5` supplier.

The `_v5` registry already states these exact derivations and the zero-denominator refusal at [docs/paper/results-fill-registry.md:210](/Users/edr/code/JouleWise/docs/paper/results-fill-registry.md:210). What is missing is not ordinary-R arithmetic; it is an issued `_v5` artifact and a governed close-out record that stores each result and the all-cells decision.

### 2. Shared-error ratio inputs

No artifact today carries the complete `R_cm` input set.

“Common-mode” means one timing-edge error with the same sign across every comparative block. Each block also has a **local width**, the uncertainty unique to that block. The registered replay keeps the shared sign common while enumerating every combination of local signs.

During extraction, `_CommonModeBlockInputs` temporarily holds onset and offset sweeps, the zero-point contrast, four bundle-local residual widths, member window bounds, and the envelope integral at [joulewise/floor_extraction.py:243](/Users/edr/code/JouleWise/joulewise/floor_extraction.py:243). `_common_mode_block_half_width` then calculates:

```text
shared width + local width
```

and returns only that sum at [joulewise/floor_extraction.py:460](/Users/edr/code/JouleWise/joulewise/floor_extraction.py:460). The separate values cease to exist after [joulewise/floor_extraction.py:497](/Users/edr/code/JouleWise/joulewise/floor_extraction.py:497).

The raw values remain reconstructible from the retained bundle ensemble:

- Power curves are read from `power_trace.csv` at [joulewise/bundle_read.py:323](/Users/edr/code/JouleWise/joulewise/bundle_read.py:323).
- Phase windows come from `events.jsonl` at [joulewise/bundle_read.py:566](/Users/edr/code/JouleWise/joulewise/bundle_read.py:566).
- Extraction reconstructs residuals, sweeps, windows, and envelope totals at [joulewise/floor_extraction.py:2382](/Users/edr/code/JouleWise/joulewise/floor_extraction.py:2382).
- The authenticated shared-edge bound is re-derived from the calibration bracket at [joulewise/detection_floor.py:575](/Users/edr/code/JouleWise/joulewise/detection_floor.py:575); an evaluation basis can carry it as `calibration_bracket_set.operative_b_fiducial_s` at [joulewise/whole_window.py:2124](/Users/edr/code/JouleWise/joulewise/whole_window.py:2124).

The current mint recomputes those private records and then discards them at [joulewise/floor_mint_estimator.py:465](/Users/edr/code/JouleWise/joulewise/floor_mint_estimator.py:465). The aggregate artifact retains only `comparative.admissible_half_widths_j`, the already-summed widths. Its own module states that the registration is intentionally not projected into the artifact at [joulewise/floor_mint_estimator.py:1](/Users/edr/code/JouleWise/joulewise/floor_mint_estimator.py:1).

Therefore the exact missing artifact content is:

- The authenticated shared-edge bound.
- Each block’s raw replay inputs.
- Each derived `shared_width_j` and `local_width_j`.
- The replayed point floor, common-mode corner floor, ratio, and pass/fail result.

The fixture at [tests/fixtures/fcm_r4_real_blocks/measured_pair.json](/Users/edr/code/JouleWise/tests/fixtures/fcm_r4_real_blocks/measured_pair.json) has the needed replay shape, but it is test data, not campaign evidence.

### 3. Minimal artifact chain

The registered predicate already exists: `dominance_ratio` performs finite-value checks, refuses a zero denominator, divides, and tests `R >= 2` at [configs/campaigns/d117_contrast_v5/generate_configs.py:591](/Users/edr/code/JouleWise/configs/campaigns/d117_contrast_v5/generate_configs.py:591). `replay_common_mode_dominance` authenticates the shared bound, reconstructs each split, enumerates one shared sign and all local signs, and computes `R_cm` at [configs/campaigns/d117_contrast_v5/generate_configs.py:683](/Users/edr/code/JouleWise/configs/campaigns/d117_contrast_v5/generate_configs.py:683).

The smallest complete production chain is:

| Artifact in | Function | Artifact out |
|---|---|---|
| Real bundles, uncertainty evidence, calibration bracket | Existing `extract_cells` and `_common_mode_block_inputs_from_evidence` | Existing `joulewise.detection_floor_extraction.v1` |
| Extraction reports plus authenticated raw evidence | Existing mint recomputation plus new `build_d165_replay_record` | Existing floor artifact plus proposed `joulewise.d165_dominance_replay.v1` sidecar |
| Finalized manifest, floor artifact, replay sidecar | New `build_d165_dominance_closeout` | Proposed `joulewise.d165_dominance_closeout.v1` |
| Close-out artifact plus 126-key registry | New `derive_d165_ratio_fills` and `_d165_branch_text` | Renderer fill map and selected prose branch |

The replay sidecar should contain:

```text
cells[].absolute.independent.{point_unguarded_floor_j,
  corner_widened_unguarded_floor_j, ratio, passes}
cells[].absolute.common_mode.{status, reason}

cells[].comparative.independent.{point_unguarded_floor_j,
  corner_widened_unguarded_floor_j, ratio, passes}

cells[].comparative.common_mode_replay.inputs.{
  calibration_bracket_sha256, shared_edge_bound_s, blocks[]}
blocks[].{delta_j, onset_sweep_j, offset_sweep_j,
  zero_point_contrast_j, bundle_residual_half_widths_j,
  member_window_bounds_s, member_envelope_integral_sum_j}
blocks[].derived_split.{shared_width_j, local_width_j}
cells[].comparative.common_mode_replay.result.{
  point_unguarded_floor_j,
  common_mode_corner_widened_unguarded_floor_j,
  ratio, passes}
```

The close-out artifact should count exactly eight ordinary ratios—two components across four model/phase cells—and four mandatory comparative `R_cm` values. Its global fields should be:

```text
all_independent_pass
all_required_common_mode_pass
branch
dominance_sentence_licensed
subtitle_licensed
refusal_reason
```

Branch A means all eight ordinary ratios pass and all four comparative `R_cm` values are at least 2. Branch B means a completed ratio is below 2, so the dominance sentence and subtitle are withdrawn. A missing, unauthenticated, or zero-denominator result selects neither branch; it stops filling.

Finalization currently binds only the floor artifact’s path, hash, schema, and identifier at [joulewise/analysis_manifest_v3.py:3624](/Users/edr/code/JouleWise/joulewise/analysis_manifest_v3.py:3624). It does not read outcomes or calculate ratios. Under the recommended sidecar design, that outcome-blind behavior can remain unchanged: the close-out artifact binds hashes of the finalized manifest, floor artifact, and replay sidecar.

### 4. Renderer answer

The successor renderer is required first.

Although the current script can load the live registry at [scripts/render_results_fills.py:100](/Users/edr/code/JouleWise/scripts/render_results_fills.py:100), its state holds only the old Boolean `dominance` label at [scripts/render_results_fills.py:370](/Users/edr/code/JouleWise/scripts/render_results_fills.py:370). `derive_numeric` has no ordinary-R or `R_cm` rule at [scripts/render_results_fills.py:512](/Users/edr/code/JouleWise/scripts/render_results_fills.py:512), and `_branch_text` understands only the old T/N/L/U branches at [scripts/render_results_fills.py:842](/Users/edr/code/JouleWise/scripts/render_results_fills.py:842).

The test contract explicitly freezes 109 historical keys and proves that `_v5` keys are unknown at [tests/test_render_results_fills.py:227](/Users/edr/code/JouleWise/tests/test_render_results_fills.py:227). The regenerated registry has 126 keys—109 renamed or retained keys plus 17 new `_v5` keys—and says the present renderer must fail closed at [docs/paper/results-fill-registry.md:868](/Users/edr/code/JouleWise/docs/paper/results-fill-registry.md:868).

There is also a queue-state mismatch: `RENDERER-V5-SUCCESSOR-01` appears only as “row owed” at [docs/process_traces/2026-08-27-t26/WAVE-ROWS.md:68](/Users/edr/code/JouleWise/docs/process_traces/2026-08-27-t26/WAVE-ROWS.md:68), not in `TASK_QUEUE.md` or `docs/process/state_kernel.json`.

### 5. Smallest implementation plan and ruling

One **Sol-day** means one focused implementation day by Codex Sol.

| Work | Files and functions | Tests | Estimate |
|---|---|---|---:|
| Production ratio core | New `joulewise/dominance_closeout.py`: `dominance_ratio`, `split_common_mode_block_width`, `replay_common_mode_dominance`; generator imports the shared functions | Preserve `tests/test_d117_contrast_v5_pack.py`; new `tests/test_d165_dominance_closeout.py` | 0.75 day |
| Authenticated replay emission | `joulewise/floor_mint_estimator.py`, `scripts/mint_floor_artifact_generalized.py`: `build_d165_replay_record` | `tests/test_floor_mint_estimator.py`, `tests/test_mint_floor_artifact_generalized.py` | 1.25 days |
| Global close-out | New `scripts/build_d165_dominance_closeout.py`; `build_d165_dominance_closeout` and source-hash validation | Eight-R/four-`R_cm` census, equality, zero refusal, missing input, source mutation, branches A/B | 1.0 day |
| Successor renderer | Regenerate `scripts/render_results_fills.py`; new current template, proposed `docs/paper/results-prose-template-v5.md`; `derive_d165_ratio_fills`, `_d165_branch_text` | Vocabulary sync at 126 keys, nested `[PREFILL_LENGTH]`, ratio formatting, not-applicable absolute `R_cm`, branch licensing | 1.25 days |
| End-to-end close-out | Same files; fixture-backed collection-to-fill replay | Clone proof and fail-closed mutations | 0.75 day |

Estimated total: **4–5 Sol-days**, centered near **5 days**.

The one required magistrate decision is artifact ownership:

- **Recommended:** keep `joulewise.detection_floor_artifact.v2` unchanged and emit a separately hash-bound `joulewise.d165_dominance_replay.v1` sidecar during mint.
- Alternative: introduce a new aggregate-floor schema containing the replay inputs and outcomes.

The sidecar is smaller in collision surface, preserves the floor artifact’s present meaning, and lets finalization remain outcome-blind. Implementation should not begin until that choice is issued.

### Worked pilot arithmetic

The frozen draft reports point floors of 0.2888, 0.4934, and 0.3113 J, paired with corner-widened floors of 3.153, 2.922, and 2.184 J at [docs/paper/draft-v1.md:103](/Users/edr/code/JouleWise/docs/paper/draft-v1.md:103). The arithmetic is:

```text
3.153 / 0.2888 = 10.9176 → 10.92
2.922 / 0.4934 =  5.9222 →  5.92
2.184 / 0.3113 =  7.0157 →  7.02
```

All three exceed 2. They still cannot close the prospective headline: `_v5` requires eight ordinary ratios and four comparative shared-error ratios from the issued campaign identities. The pilot has only three diagnostic-era pairs and supplies no authenticated `R_cm` replay.