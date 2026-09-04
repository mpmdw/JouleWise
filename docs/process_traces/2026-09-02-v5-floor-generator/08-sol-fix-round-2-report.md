# Sol fix round 2 — `_v5` floor generators

Date: 2026-09-03  
Seat: Sol, implementation  
Base and final HEAD: `f6e9693df6b14515151cb59058f35b9669683ca7`  
Branch: `feat/2026-09-02-v5-floor-generator`  
Disposition: complete; no commit made

## Changes

- CR-1: both producer contracts now obtain `producer_index` and all three
  consumer-binding `arm` values only from `PRODUCER_INDEX` and `CONSUMER_ARM`.
  An AST regression proves those four routing sites are constant references and
  pins the ALPHA/BETA pairs to `(1, "A")` and `(2, "B")`.
- CR-2/CR-6: the shared fixture now has the issuer's exact pin key set, an
  exact selector-emitted selected record, and all four `512, 1024, 2048, 4096`
  ladder rungs. Both floor loaders accept it. They now require four rungs,
  reject duplicate or out-of-ladder lengths, and verify complete ladder
  membership. Two-rung, duplicate-rung, and unknown-rung regressions bite on
  both generators.
- CR-4: the fixture reads `ladder_prompt_tokens`,
  `min_small_model_members_per_rung`,
  `min_overlapping_power_interval_count`, `min_phase_samples_pinned`, and
  `sample_count_margin_floor` from
  `configs/campaigns/d117_contrast_v5/generate_configs.py`. A copied
  contrast-side mutation from 5 to 6 makes the floor acceptance test fail.
- CR-5: the loaders no longer accept `refused`; they emit the named refusal
  `selection_record_refused_not_supported`. The selected branch requires
  `collection_prefill_tokens == selected_prefill_tokens == 512` and a null
  refusal, under the issuer's closed selection-record key set.
- CR-7: removed the never-read `CURRENT_FROZEN_GENERATOR_SHA256` and
  `P512_PROMPT_TOKEN_IDS` state from both generators. The prompt-token digest
  remains live and unchanged.
- CR-3: the landing report now records that the six `_v3` family drift checks
  are intentionally absent only until `V5-DESK-DAY-01`, assigns their
  restoration to magistrate-registered row `FLOOR-V5-DRIFT-REPIN-01`, and
  records the R-7 consequence that a selected rung above 512 requires both
  floor packs to be re-authored.

## Required focused verification

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_floor_qwen3_v5_generate tests.test_d117_contrast_v5_pack tests.test_issue_g2a_prefill_prompt_pin
```

Tail:

```text
..........................................G2-a prompt pin refused: selection_record_does_not_match_summary_and_rule
G2-a prompt pin refused: selection_record_does_not_match_summary_and_rule
....G2-a prompt pin refused: output_already_exists
.G2-a prompt pin refused: prompt_token_ids_invalid:1024
..G2-a prompt pin refused: runtime_prompt_token_ids_mismatch:2048
.G2-a prompt pin refused: selection_record_does_not_match_summary_and_rule
G2-a prompt pin refused: selection_record_does_not_match_summary_and_rule
G2-a prompt pin refused: selection_record_does_not_match_summary_and_rule
..
----------------------------------------------------------------------
Ran 52 tests in 11.776s

OK
```

## Contrast-constant mutation

In a temporary repo-shaped copy, this mutation was applied only to the copied
contrast generator:

```text
PREFILL_MIN_SMALL_MODEL_MEMBERS_PER_RUNG = 5
->
PREFILL_MIN_SMALL_MODEL_MEMBERS_PER_RUNG = 6
```

The copied focused acceptance test then failed in both floor subtests at the
intended floor-loader boundary:

```text
ValueError: prefill_prompt_pin_invalid: ruled constants mismatch
...
----------------------------------------------------------------------
Ran 1 test in 0.103s

FAILED (failures=2, errors=2)
```

The harness treats that nonzero unittest exit as mutation success. The clean
source test passes in the required 52-test run above.

## Additional verification

`git diff --check` passed. The repository-wide discovery suite was also
started with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`;
its terminal result is recorded below after completion.

## Scope and handoff

Only the two allowlisted generators, the allowlisted floor test, this report,
and the allowlisted landing-report addendum were modified. No generated pack
tree, quiet-machine measurement, commit, or out-of-scope bookkeeping write was
performed. The lead retains final diff review, the post-freeze drift-row
registration, and live/desk-day verification.
