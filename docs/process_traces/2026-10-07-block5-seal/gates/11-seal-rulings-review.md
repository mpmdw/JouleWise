# Independent review of lane/2026-10-07-seal-rulings (executing lens)

Reviewer: Opus 5.5, not the author. Written 2026-10-08.

**Verdict: PASS WITH NOTES.** No BLOCKER, no MAJOR. Four NOTES, all representation-only.

- Reviewed head: `a0920cb8cec18188cc34902273eb3d6de4e965b4`; base `9395cecfbc40fb93e87a7657ec0ba5da0ca9ef3a`
  (an ancestor of the head); the head is an ancestor of the merge `cc0b3446d`.
- The seven files of the lane are byte-identical between `a0920cb8c` and `cc0b3446d`, and the three
  configuration files are byte-identical at the integration head at the time of review (`4394ca891`)
  (`git diff --stat`, empty).
- Scratch clones: `/private/tmp/w1007-rulings-review` (tests and probes) and
  `/private/tmp/w1007-rulings-rv-mut` (mutations). Both are back at `a0920cb8c` with a clean tree. No
  leaked child process (`pgrep -fl w1007-rulings-rv`: none). Nothing was written in the int5 worktree.
- Interpreter `/opt/homebrew/bin/python3.13 -B`, `TMPDIR=/private/tmp/w1007-rulings-rv-tmp`.
- My probe scripts (written for this review, not the author's): `review_probe_p12.py` and
  `review_probe_p345.py` beside this file.

## 1. What the diff touches (EXECUTED)

`git diff --name-only 9395cecfb..a0920cb8c` lists exactly seven files:
`configs/campaigns/v5_claim_25g83/flag_catalog.json`, `configs/gates/hazard_refusals.json`,
`tests/fixtures/b5_harvest/README.md`, `tests/fixtures/b5_harvest/flag_catalog.json`,
`tests/flags/test_flags_catalog.py`, `tests/flags/test_flags_exclusions.py`, `tests/test_harvest_b5_window.py`.
Nothing under `joulewise/` or `scripts/`.

A key-by-key comparison of the parsed JSON (base against head) gives:

| File | Every difference |
|---|---|
| block-5 catalog | `/rules/cell_unit_minimum` 8 to 5. Nothing else. |
| allowlist | `window_exclusions/cell.below_minimum/protects` changed; `window_exclusions/neg8.midpoint_lost_primary/protects` changed; `window_exclusions/g3.recompute_failed` removed. Nothing else. The string `g3.recompute_failed` no longer occurs anywhere in the file. |
| test fixture catalog | `codes/g3.recompute_failed/effect` EXCLUDE_WINDOW to DISCLOSE; `rules/cell_unit_minimum` 8 to 5; the free-text `notes`. Nothing else. |

The two `protects` texts equal the judge's wording character for character (string equality in Python against
the text of K-1 and K-3 in `RULING_STAGE1.md`, with the ruling's line breaks joined by single spaces): both `True`.

## 2. The catalog's codes are unchanged (EXECUTED)

`base["codes"] == head["codes"]` is `True` for the block-5 catalog (192 codes on both sides), so every code's
effect, family, class, blinding and note is identical. The only differing key in the whole document is the rule.

## 3. The rule takes effect through the real code path (EXECUTED)

Inputs I built: the real rosters from `harvest.build_roster` and `harvest.l4_exclusion_inputs` for ALPHA
(`d117_floor_qwen3-1p7b_v5`), BETA (`d117_floor_qwen3-8b_v5`) and GAMMA
(`d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`); the lane's block-5 catalog read from its path; member flags of a
code the author's tests do not use (`thermal.powermetrics_pressure_elevated`, EXCLUDE_MEMBER), placed on one
randomly chosen member of each of N randomly chosen units (fixed seed), not the first N units. Each case was
run through the harvest's own call (`harvest._l4_exclusions`, which re-reads the catalog from its path) and
through `joulewise.flags.exclusions.compute` directly; the two results were asserted equal.

| Pack | Members (science) | Target cells and strata | Clean window |
|---|---|---|---|
| ALPHA | 126 (100) | decode and prefill-p2048, each `quad` and `repeat` | usable, no reason |
| BETA | 126 (100) | decode and prefill-p2048, each `quad` and `repeat` | usable, no reason |
| GAMMA | 108 (80) | the two contrast cells, `quad` only | usable, no reason |

For every stratum of every target cell of all three packs (10 cell-stratum pairs: 4 on ALPHA, 4 on BETA, 2 on
GAMMA; two cases each, 20 cases):

- 5 units lost, 5 kept: `minimum` reports 5 for every stratum, `claim_usable` true, `reasons` empty.
- 6 units lost, 4 kept: `claim_usable` false, `reasons` exactly `['cell.below_minimum']`.

Zero mismatches in 20 cases. The estimator boundary the ruling cites is real in this tree:
`small_sample_guard_factor(5)` returns 1.5 and `small_sample_guard_factor(4)` raises `ValueError`.

## 4. Does anything else decide by 8? (EXECUTED, with one part READ)

Search of `joulewise/` and `scripts/` for a hard-coded minimum finds two things, as the author reported:

1. `joulewise/flags/catalog.py` line 50, `DEFAULT_CELL_UNIT_MINIMUM = 8`, read at line 392 only when the
   catalog's `rules` has no `cell_unit_minimum` key, and used to build the in-code draft catalog (line 482).
2. `joulewise/b5/driver.py` line 154, `SCIENCE_MIN_NUMERATOR, SCIENCE_MIN_DENOMINATOR = 4, 5`: the driver's
   per-stage yield count. It produces `yield.stage_low` and the terminal record's `yield_low` notice. Those
   catalog codes are DISCLOSE (printed from the lane's catalog), and no claim-usability decision reads them
   (READ: the only consumers are the driver's own records and the notice text in `scripts/run_night.py`).

**The default is never consulted with the sealed catalog.** I set `catalog.DEFAULT_CELL_UNIT_MINIMUM = 999`
in the running process and repeated all 20 cases on the three real rosters: identical results, `minimum` 5
everywhere. Had the default been read on any path, every cell would have been below a minimum of 999.

**Paths by which a block-5 harvest could reach the default or lose the rule** (each driven):

| Condition | What happens | Direction |
|---|---|---|
| Catalog file absent, or path `None` | `_l4_exclusions` raises `HarvestFault("flag_catalog_absent")`; the caller (harvest.py 7403 to 7412) records the error and writes `claim_usable: false`, reason `exclusions.function_unavailable` (READ for the caller) | safe: nothing is kept wrongly; numbers and flags still emitted |
| Catalog not parseable | `Catalog.load` raises `JSONDecodeError` | not reachable with the sealed bytes |
| `cell_unit_minimum` of 0, 4.5, `"5"`, `true` or `null` | `load_catalog` raises `CatalogError`; same `exclusions.function_unavailable` route | safe |
| A readable catalog with no `rules` key, or `rules: {}` | `cell_unit_minimum` is 8 (the default) | stricter than the ruling (a window with 5 to 7 kept units would be removed), never looser |

So the only route to 8 is a catalog other than the sealed one: the harvest takes its catalog from the plan's
`catalog_path` / `flag_catalog` key if present, else from
`<measurement>/configs/campaigns/v5_claim_25g83/flag_catalog.json` (harvest.py 1521 to 1522). There is no
fallback catalog in code: the draft catalog (`draft_catalog()`, minimum 8) is called by no module under
`joulewise/` or `scripts/` outside `catalog.py` itself (grep). The catalog's path and SHA-256 are written into
the harvest summary, so a wrong catalog is visible in the record. The arm-time collector
(`scripts/collect_window_flags.py`) loads the catalog only to stamp its digest on flags; it decides nothing by
the rule.

## 5. `g3.recompute_failed` (EXECUTED)

- `tests.hazards.test_refusal_allowlist`: 23 tests, OK. In a plain clone one test skips (it needs the local
  branch `design/2026-10-05-v5-claim-block-draft`); with that branch created in the scratch clone (at
  `c7408819c`) all 23 run and pass.
- Effect through the lane's catalog: `load_catalog(...).effect("g3.recompute_failed")` is `DISCLOSE`.
- A window carrying only `g3.recompute_failed` (window level) on each of the real ALPHA, BETA and GAMMA
  rosters, through `_l4_exclusions`: `claim_usable` true, `reasons` empty. Adding `whole_window.not_passed`:
  still true. Positive control, adding `neg8.screen_failed`: false, `['neg8.screen_failed']`.

## 6. Mutation checks (EXECUTED in the second scratch clone; each restored with `git checkout -- .`)

| Mutation | Tests that fail |
|---|---|
| **A. block-5 catalog rule back to 8** | 7 failures: `CatalogTests.test_sealed_catalog_classifies_every_code_this_lane_emits`; `SealedCellMinimumTests` (3 tests, 4 failures counting sub-tests); `ExclusionSeamTests.test_the_block5_catalogs_cell_minimum_decides_on_the_real_alpha_roster`; `FixtureCatalogTests.test_the_fixture_agrees_with_the_block5_catalog_on_every_code_both_list` |
| **B. the allowlist's `g3.recompute_failed` line restored** | `RefusalAllowlistTests.test_every_window_exclusion_names_what_it_protects`: "window_exclusions lists g3.recompute_failed, which no catalog makes EXCLUDE_WINDOW" |
| C. fixture `g3.recompute_failed` back to EXCLUDE_WINDOW | `FixtureCatalogTests` agreement test, both allowlist exclusion tests, and `DeskAndG3Tests.test_g3_recompute_that_did_not_pass_is_never_silent` (5 sub-test failures on the new `assertNotIn`, rerun alone) |
| D. block-5 catalog `g3.recompute_failed` to EXCLUDE_WINDOW | `FixtureCatalogTests` agreement test and both allowlist exclusion tests |
| E. fixture rule back to 8 | 4 failures (`test_l4_compute_on_the_real_alpha_roster`, the agreement test, `test_catalog_and_codes_agree_with_l4`, `test_every_catalog_fixture_code_is_an_emitted_code`) |
| F. block-5 catalog rule to 6 | 6 failures |
| G. block-5 catalog rule to 4 | 6 failures |
| H. block-5 catalog `rules` key deleted (default 8 takes over) | 5 failures, 2 errors |

Every guard can fail on the defect it guards, in both directions around 5.

## 7. Modules run at `a0920cb8c` (EXECUTED)

| Module | Tests | Result |
|---|---|---|
| `tests.hazards.test_refusal_allowlist` | 23 | OK (1 skip without the design branch; 0 skips with it) |
| `tests.flags.test_flags_catalog` | 6 | OK |
| `tests.flags.test_flags_collect` | 58 | OK |
| `tests.flags.test_flags_core` | 20 | OK |
| `tests.flags.test_flags_exclusions` | 34 | OK |
| `tests.flags.test_flags_fx_regressions` | 6 | OK |
| `tests.flags.test_flags_identity_pins` | 6 | OK |
| `tests.flags.test_flags_import_graph` | 3 | OK |
| `tests.flags.test_flags_review_regressions` | 16 | OK |
| `tests.flags.test_flags_schema` | 10 | OK |
| `tests.flags.test_flags_sink` | 9 | OK |
| `tests.flags.test_number_coverage` | 6 | OK |
| `tests.test_harvest_b5_window` | 184 | OK (493 s) |
| `tests.test_b5_seal_landing` | 9 | OK |

Total 390 tests, 0 failures, 0 errors.

## Findings

All NOTE (representation only; none reaches a claim-usability decision). None needs a fix before the seal.

- **N1 (NOTE). Stale "8" in three code comments.** `joulewise/b5/driver.py` line 153 ("the analysis plan's
  8-of-10 cell minimum"), `joulewise/flags/exclusions.py` line 57 ("may only raise the catalog rule (8)") and
  the format example in `joulewise/flags/catalog.py` line 18. Probe: grep; the poisoned-default run of section
  4 shows none of them decides anything. Smallest fix: reword the three comments after the seal, in the desk
  checkout, if the files are ever opened for another reason. The lane was right not to touch `joulewise/`.
- **N2 (NOTE). The default of 8 remains in code.** A catalog without the rule key decides by 8, which is
  stricter than the ruling and never looser. Probe: section 4 table and mutation H. Smallest fix: none needed;
  the sealed catalog carries the key and mutation H shows the tests fail if the key is ever dropped.
- **N3 (NOTE). The driver's per-stage yield rule (4 of 5) is a separate, disclose-only count** and was sized
  against the old 8-of-10 minimum, so `yield.stage_low` and the `yield_low` notice will now fire for windows
  the cell rule keeps. Probe: catalog effects printed (`yield.stage_low`, `yield.stage_zero`: DISCLOSE); grep
  for consumers. Smallest fix: none for the seal; a notice-wording matter for the orchestrator.
- **N4 (NOTE, outside the lane). The int5 copy of the block-5 catalog and the design branch's copy
  (`c7408819c`) differ in bytes**: 42 codes' `note` texts and the top-level `notes` differ; family, class,
  effect and blinding of all 192 codes and the rule (5) are equal on both. Probe: scripted comparison.
  Smallest fix: the integrator copies the final design-branch catalog into int5 before the catalog's bytes
  are pinned (already the integrator's step; reported so it is not missed).
