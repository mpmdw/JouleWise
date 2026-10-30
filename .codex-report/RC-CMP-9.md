STATUS: DONE

# RC-CMP-9: the registry-driven expected-check table (the structural fallback FIX-BRIEF-3 pre-registered)

Seat RC-CMP-9, branch `lane/2026-10-27-recompute-comparator`, from `0d317afd4`. Synthetic data only: no real
block-5, block-6 or BYTES data was opened or searched for. `/usr/bin/python3.13`, `TMPDIR=/tmp/rccmp_nine_tmp`
(outside the checkout, no float-like token). Producers on `origin/main` were read as text only:
`analysis_engine/{__init__,artifact}.py`, `results_fill_adapter.py`, `scripts/build_results_fill_input.py`,
`b5_analysis/{disclosures,sensitivity,bracket,dry_run}.py`, `dominance_closeout.py`. The sealed manifest, the
consumer declaration, the extraction specs and the three plan trees were read as data (all pinned by digest in
`REGISTRY_PINS`, unchanged). `configs/analysis/b5/analysed_windows.json` exists only on `origin/main`; I looked at
its schema to name it, and the comparator does not read it (NEEDS_RULING 3). The script imports no `joulewise`
module (unchanged; `test_no_l9_import`).

Reviews read: `review/2026-10-29-rc-cmp8-opus-rev` (256b834d5) and `review/2026-10-29-rc-cmp8-fable-rev` (71b727c79).

## SUMMARY

- **The design rule is implemented.** Before any family compares, `compare_expected` builds one table with
  `expected_checks(registry)`. The table is a function of the registry alone. It has 256 entries in 29
  families, carrying 2406 required nested key paths.
- **Every entry must be found on both sides.** For each entry whose registered condition holds, the item must be
  present, with its required nested keys, in every L9 copy (fill, verdict, disclosure line, disclosure copy,
  block-line copy, standalone record, projection, extraction report, aggregate floor, ratio table, brackets,
  kept-units record) and in the recompute. Anything missing on either side is a DISAGREE row
  (`routing_id expected/<check>`, with the missing names listed in the restricted output). Nothing is skipped.
- **Output items outside the table can only DISAGREE.** An L9 item of a listed collection that no entry claims
  becomes `expected/unexpected/<doc>:<path>`, which is DISAGREE.
- **A compared leaf must sit inside a claimed item.** A compared step-11 leaf binds only inside an item the table
  claimed; otherwise it is `not_in_table` and refuses. The leaf coverage of RC-CMP-3 to RC-CMP-8 stays in place.
- **The registered sources are closed.** `REGISTERED_SOURCES` is a module constant with a comment saying the list
  is closed.
- **The producer key sets are literals.** They are copied as `ENGINE_KEYS`, `FILL_SHAPE`, `DISCLOSURE_SHAPE`,
  `WINDOW_LINES`, `TRIPWIRES`, `FIXED_SENTENCE_WORDS`, `SENSITIVITY_SHAPE`, `CLOSEOUT_RATIOS`, `BATTERY_CODES`,
  `CORPUS_DROPS` and `TRIGGER_KEYS`. Each one is pinned by a test that parses its `origin/main` producer.
- **Opus RC-CMP-8 REJECT is closed.**
  - All 22 single-output drops exit non-zero, on both the widened and the unwidened window.
  - The joint drops exit non-zero: the decode contrast, the ALPHA reported cell, the loo rows, the
    sensitivity floor cell, the extraction cell and the ratio row.
  - `loo_status` follows the kept `n`.
  - The floor cell ids are bound to the registered source cells.
  - Opus's relabel probe gives 4081 identity relabels tried and 0 exit 0. At `0d317afd4` it was 623 and 64.
- **Fable F1 to F5 are closed.**
  - F2: the arm gates and resolutions are built from `ARMS` whatever the floor prints.
  - F3: every one of the 13 line words is an entry.
  - F4: the projection's p42 row is unconditional.
  - F5: a conditional key is required whenever the status word that makes the producer print it is present.
  - Fable's whole-line drop leaves 2 words that still exit 0. Both are conditional and declared: `flag_count`
    and `machine_absent`.
- **The base fixture is producer-complete over the registry.** It now carries:
  - every registered reported cell, with p42 refused;
  - every extraction, aggregate and floor cell;
  - all 12 D-165 ratios;
  - nine kept blocks per contrast, each with its leave-one-out row;
  - every line the producer prints unconditionally.
- **No assertion was relaxed.** Fixtures that used to replace whole sections now edit them in place. Counts that
  grew because a planted fault is now also seen in a second copy were raised. Each test I changed is listed under
  FILES CHANGED with the reason.
- **Suite:** `Ran 362 tests`, `OK (skipped=18)`, exit 0. That is 330 at `0d317afd4` plus 32 in `test_rc_cmp9.py`.
  The run time went from about 178 s to about 470 s (OPEN ISSUES 5).

## A1-A7

Counterfactuals at `0d317afd4` come from two places:
- Opus's `confirm.out`, `joint.out`, `loo.out` and `relabel_ids.out`, and Fable's `probes.out` and `sweep.out`, as
  published on the review branches;
- reruns in a worktree at `0d317afd4`, which matched them:
  - `probe_cmp8.py confirm`: 50 cases exit 0, which is the 22 drops and 3 relabels on each window.
  - `probe_cmp8.py joint2`: the decode contrast and the reported cell exit 0.
  - `probe_cmp8.py loo`: the fill-row drop and the joint drop exit 0.
  - Fable's `probes.py` S1: `a`, `c`, `l`, `m` and `n` exit 0.

"In place" means a test in `test_rc_cmp9.py` switches the new check off (`no_table`, `rows_off`, …) and shows the
same case exiting 0.

| Item | Evidence at this head | At `0d317afd4` |
|---|---|---|
| A1 table | `TableTests`: the table is a function of `registry` alone (`expected_checks(registry)`; equal for two independently loaded registries). It lists each registered item at its multiplicity (family counts asserted). `test_unconditional_producer_line_kinds_are_in_the_table` analyses `produce_disclosures` on origin/main (AST: every `_item` printed on every path, per registered loop), and every such (section, word) has an entry. `test_unconditional_keys_of_each_line_are_required`: every literal key each `_item` call writes is required or names the line. `ProducerPinTests` (6 tests) pin every literal key set to `artifact.py`, `results_fill_adapter.py`, `build_results_fill_input.py`, `disclosures.py`, `sensitivity.py`, `bracket.py` and `dominance_closeout.py`. The restricted output carries `expected_checks` (sources, families, each check's name, documents and condition kind; no value; `test_structure_is_printed_without_values`). | no table |
| A2 Opus's 22 drops | `OpusDropTests.test_each_single_output_drop_exits_non_zero`: all 22, widened and unwidened, exit non-zero. `probe_cmp8.py confirm` at this head: none exit 0. | all 22 exit 0 on both windows (confirm.out); in place (`no_table`): ≥14 of 22 pass again (`test_without_the_table_the_drops_pass`; the rest also meet another new check, e.g. the sensitivity record's primary values read directly) |
| A2 joint drops | `test_joint_drops_exit_non_zero` (decode contrast, ALPHA decode reported cell, decode loo rows; both windows). `probe_cmp8.py joint2`: all 10 cases non-zero. `loo`: all 5 drop cases non-zero. | decode contrast and reported cell exit 0 (joint.out); loo joint and fill-row drop exit 0 (loo.out); in place: `test_joint_drops_passed_before_the_table` (no table, 0d317afd4's rows-based loo word): all three exit 0 |
| A2 loo word | `loo_status(n, blocks)`: `complete` iff the kept `n` ≥ 1 (engine `_loo_family` with block 5's kept quads), `not_run` iff 0, `None` above `LOO_REQUIRED_MAX` registered blocks or without `n`. Two row counts: each side's rows number the kept `n` when `n` ≥ `LOO_MIN` (3). `test_loo_status_follows_the_kept_n`: the joint drop reads `not_run` against `complete`. | the word came from whether the recompute printed rows |
| A3 floor ids | `compare_floor_ids` compares `floor_row_ids` (verdict), the fill's `floor_source_cell_ids` and `floor/floor_row_ids`, and the sensitivity record's and its copies' `floor_cell_ids`, by position, against the registered cells [A, B] of the contrast's phase. The coverage rules bind these leaves to those rows (no longer IDENTITY). `test_floor_cell_ids_bind_to_the_registered_source_cells`; `test_list_positions_and_terms_are_required` covers shortened lists. | Opus's 64 exit-0 relabels |
| A3/A4 Opus relabels | `probe_cmp8.py relabel`: 4081 tried, **0 exit 0**. `test_opus_identity_relabels_refuse_or_disagree`, each with an in-place counterfactual: floors `kept_units` cell id, kept-units `pack` (bound to the file name's window: `run/<pack>/kept_units/pack`), kept unit `cell_id` (refuses `kept_units_identity_mismatch:<pack>`: a unit names the cell that keeps it), excluded block id and planned ids (bound to the manifest's `block_ids`), transport group (bound to the manifest's group per arm). Identity carried by a file name and left so: the window of `brackets/<sha>-<pack>.json`, `outputs/<sha>-projection-<pack>.json`, `mint/<sha>-extraction-<pack>.json` and `kept-units/<sha>-<pack>.json` (none prints a window field except the kept-units record, now bound), and the run id of `rereduced/<pack>/<run>.rereduced.json` (G7 universe). | 623 tried, 64 exit 0 (relabel_ids.out) |
| A4 p42 row | `compare_reported` builds `<pack>/projection/p42` for every floor window; absent, relabelled or object-shaped `refused_cells` reads `None` (DISAGREE). The table also expects each p42 cell in `refused_cells`. `test_projection_p42_row_is_unconditional`. Fable's S1.l, S1.m and S1.n exit 1. | S1.l, S1.m, S1.n exit 0 |
| A4b F1 | Fable's `sweep.py` at this head: 4982 deletions over every L9 input and the recompute (base: with_sensitivity widened, exit 0), 735 exit 0. Classified with Fable's `classify.py`: 724 declared exemption, identity or text, **11 classified producer-unconditional, each a declared exemption listed below** (0 undeclared). Each remaining one is listed in **Sweep residue** below. | 1933 deletions; 831 exit 0; 297 classified producer-unconditional |
| A4b F2 | S1.a, S1.c (`arm_gates`, `resolutions`): exit 1. `FableFindingTests.test_f2_arm_gates_and_resolutions_dropped`. | S1.a, S1.c exit 0 |
| A4b F3 | All 13 words dropped: non-zero (`test_f3_each_line_word_dropped`; Fable's whole-line sweep: only `flag_count` and `machine_absent` exit 0). | 13 words exit 0 |
| A4b F4, F5 | F4 as A4. F5: `STATUS_KEYS` (a complete `dominance_ratio` requires `ratio`, `numerator_j`, `denominator_j`; a computed `battery_assist_contrast` its six estimates, a one-quad one its mean) and the trigger object's keys when it is an object. `test_f5_conditional_keys_follow_the_status_word` (with controls: a refused ratio and a not-computable assist contrast pass the gate). | `block_lines/8/ratio` and the like exit 0 (sweep.out) |
| A5 | `GenericDeletionTests` (6 tests). For every entry active on the producer-shaped base, its item is deleted from L9's side (every copy, and each copy alone), from the recompute's side alone, and from both: never exit 0. `test_every_kind_is_exercised` covers all 29 families. `test_every_compared_leaf_lies_inside_an_expected_check`: the base has no unbound leaf, and without claims every compared leaf refuses `not_in_table`. | — |
| A6 | `OverRefusalTests.test_producer_shaped_windows_pass`: with_neg8 + with_references + with_sensitivity, widened and unwidened, exit 0 with every row AGREE. Fable's S3.a: exit 0 on both windows. `test_rc_cmp7...test_rc_cmp4_window_passes_and_lists_each_reference_member` passes. `test_conditional_items_follow_their_condition`: on the base, exactly the not-kept block 1 rows and the refused variants of computed cells are not expected. | — |
| A7 | Every RC-CMP-6/7/8 test passes (362 OK). `probe_cmp7.py all`: A0-A14, C1-C6 and K1-K12 give the same exits as Opus's `cmp7_*.out` at `0d317afd4` (A4, A5, C5, K10 still exit 0 as declared). Its relabel sweep: 14940 relabels tried, 6 exit 0, all `machine_absent` (a bare conditional sentence) relabelled into `catalog_path` or `lost_midpoint` (at `0d317afd4`: 4067 tried, 13 exit 0, bare sentences). Its words probe: 295 exit-0 single-leaf mutations (141 at `0d317afd4` on a smaller fixture), all in RC-CMP-8's declared classes: `restricted`; ids, digests, plan ids, schema versions; harvest words (`stored_status`, tripwire and parity `result`, `causes`); `reason_codes`; floor-resolution and arm-gate `status`/`transport_verdict` (NEEDS_RULING RC-CMP-8 2); `without/status`; `attained_by`; `metric/unit`, `cell_a_id`/`cell_b_id`; variance-contribution names; limitation notes; `evidence_class`; `characterization`. The fill's block-id copies, which it found exiting 0 earlier this round, are now bound (A4). Fable's probes S2 (G7.0-G7.g, F2.a-F2.g) give the same exits, except F2.c, which now fails 5 routing rows instead of 1. `probe_cmp8.py` at this head: confirm 0 exit-0, joint2 all non-zero, loo only the control exits 0, relabel 0 exit-0. | — |

### Sweep residue (Fable's `sweep.py` at this head)

The 11 classified producer-unconditional, all declared:
- `window_lines/<pack>/1` ×3, the `flag_count` line. It follows the flag catalog, which is not a registered source
  (NEEDS_RULING 4).
- `window_lines/<pack>/23` ×3, the `machine_absent` line. It is conditional on the meter-absent flag
  (NEEDS_RULING 4).
- `block_lines/18-20/causes/0`, the attempt causes. These come from the window index, which this branch does not
  read (NEEDS_RULING 3).
- `recompute:disclosures/battery_assist/<ctr>/status` ×2. This is the recompute's own word, which the comparator
  does not read; the producer's word is re-derived from `n` (`paired_status`).

The remaining 724 exit-0 deletions fall in Fable's declared classes:
- text, label and `restricted` leaves (650);
- verdict-only engine internals that are not in any step-11 output:
  - `included_bundle_ids`;
  - `bundle_blocks/blocks/*/{bundle_a_id,bundle_b_id,reason_codes,included}`;
  - `randomization_check`;
  - `variance_contributions`;
  - `repeat_point_CI95`;
  - the verdict's own `sampling/removed_block_ids` (the fill's copy is bound);
- the disclosure's estimator internals (`ESTIMATOR_INTERNALS`);
- limitation notes and `reason_codes`;
- kept-units identity and harvest fields;
- the recompute's unread fields: `program_sha256`, the unselected corpus member, GAMMA's `claim_usable`, assist
  strata and `direction`.

## The expected-check table's families

Multiplicity comes from the registry: PACKS (3), the floor windows (2), the reported cells (6, of which 2 are p42),
the extraction cells (12, of which 4 are p42), the aggregate floor cells (4), the contrasts (2), the registered
blocks (10 per contrast), the arms (2) and the D-165 ratio census (12).

| Family | Entries | L9 copies (documents) | Recompute item | Condition |
|---|---|---|---|---|
| `fill_document` | 1 | fill: top, gamma (incl. extended), characterization, floor_artifact keys | `contrasts`, `inputs` | — |
| `fill_campaign` | 2 | fill `campaigns/<pack>` (5 keys) | `inputs.<PACK>` | — |
| `verdicts_document` | 1 | verdicts `contrasts` | `contrasts` | — |
| `kept_units_record` | 3 | kept-units record (pack, exclusions hash, cells) | `inputs.<PACK>` | — |
| `disclosure_document` | 1 | disclosure: 9 sections | `disclosures` | — |
| `disclosure_window` | 3 | `windows/<pack>` (4 keys), `window_lines/<pack>` | `windows.<PACK>` | — |
| `window_line` | 69 | per pack: the 21 unconditional window lines + 2 tripwire lines, each with its keys (NEG-8 terms; battery codes; corpus drops; reference slots) | the window's b_op / NEG-8 terms / window anchor | — |
| `block_line` | 5 | `harvest_once`, `sensitivity_boundary`, `attempt_count` per pack | disclosures / window anchor | — |
| `fixed_sentence` | 13 | 11 unconditional sentences, `floor_drift_ownership`, `gross_energy` | `disclosures` | — |
| `sensitivity_record` | 1 | the record and the disclosure copy (top keys, `b_max` keys) | `sensitivity_bound` | — |
| `sensitivity_bmax` | 1 | record, copy, `sensitivity_bmax` line | B_max, T, sequence | — |
| `sensitivity_window` | 3 | record, copy, block line | b_op, b_sens | — |
| `sensitivity_reported` | 10 | record, copy, block line, per reported cell (refused keys for p42; values and relation words when computed; a refused variant) | `p42.<fam>` / `sensitivity_bound.reported_cells` / `reported_cells` | computed (either side) or not |
| `projection_cell` | 6 | projection `cells` (18 keys) or `refused_cells` (p42: refused only) | `reported_cells.<fam>` / `p42.<fam>` | — |
| `cell_line` | 20 | `reported_cell`, `battery_assist_cell`, `attribution_floor`, `kept_units`, `cross_window` per non-p42 reported cell | reported cell / assist / cross window | computed; `cross_window` also phase n ≥ 2 |
| `sensitivity_floor` | 4 | record, copy, block line (values, relation words) | `sensitivity_bound.floor_cells` | — |
| `aggregate_cell` | 4 | aggregate floor (3 values) | `floor_cells` | — |
| `ratio` | 12 | ratio table row (by cell, component, numerator field) and its `dominance_ratio` line | `dominance.ratios` / `common_mode` | — (values: F5 gate) |
| `dominance_branch` | 1 | closeout and its line | `dominance.branch` | — |
| `extraction_cell` | 12 | extraction report cell (kind, extractable) | `floors.<key>` / `p42.<fam>` | — |
| `extraction_floor` | 8 | the cell's floor (16 values) | `floors.<key>` | computed (either side) |
| `floor_line` | 20 | `kept_units` per extraction cell; `floor_composition` per non-p42 cell | floors / NEG-8 source | composition: computed |
| `bracket` | 4 | each window's bracket; the block bracket | b_op, b_sens / B_max | — |
| `contrast` | 2 | verdict (19 keys and nested engine keys, floor ids [A, B]) and fill copy (24 keys and nested, interval, floor, floor ids) | `contrasts.<cid>` (16 keys) | — |
| `contrast_floor_arm_gate` | 4 | verdict and fill `floor/arm_gates/<i>` | `floor_cells` arm cell | — |
| `contrast_floor_resolution` | 4 | verdict and fill `floor/resolutions/<i>` (8 keys, source cell) | `floor_cells` arm cell | — |
| `loo_row` | 20 | verdict and fill row by registered block id (11 keys, both intervals) | recompute row by block position | block kept (either side) and kept n ≥ 3 |
| `contrast_line` | 20 | `primary_contrast`, `battery_assist_contrast`, `magnitude_ratio` (+ estimates), `magnitude_per_token`, `contrast_interval`, `decision_floor`, `loo_counts`, `loo_magnitude`, `kept_units` | contrast / assist / descriptive | ratio estimates: computable (either side) |
| `sensitivity_contrast` | 2 | record, copy, block line (values, floor cell ids [A, B], relation words) | `sensitivity_bound.contrasts` | — |

Items the brief lists, and where they are:
- fill contrast rows and campaigns: `contrast`, `fill_campaign`;
- verdict contrasts and loo rows: `contrast`, `loo_row`;
- the disclosure lines: `contrast_line`, `cell_line`, `ratio`, `dominance_branch`, `sensitivity_*` and
  `window_line`;
- the block-line copies: `sensitivity_*`;
- the sensitivity record: `sensitivity_record` with its windows, floor cells, contrasts and reported cells;
- reported cells: `projection_cell`;
- floor cells and floor composition: `aggregate_cell`, `extraction_*` and `floor_line`;
- ratio and aggregate rows: `ratio`, `aggregate_cell`;
- extraction p42 per pack: the p42 `extraction_cell` entries, beside the existing `<pack>/extraction/p42` row.

Items the producer prints that the brief's list misses, all added:
- the unconditional structure window lines;
- the tripwire lines;
- `kept_units` lines (cells, floors, contrasts);
- `cross_window`;
- `battery_assist_*`;
- `magnitude_*`;
- `loo_counts` and `loo_magnitude`;
- the fixed sentences;
- `harvest_once`;
- `attempt_count`;
- the brackets;
- the kept-units records;
- the deterministic bound terms (their sum against D);
- the fill's kept and removed block ids.

## FILES CHANGED

- `scripts/compare_b5_recompute.py`
  - `REGISTERED_SOURCES`; the literal key sets listed in SUMMARY.
  - `expected_checks` (the table), `expected_items` (the walk), `compare_expected` (one routing row per check,
    run first in `run`), `condition_holds`, `resolve` and `matches` (identity selectors), `CLOSED` and
    `closed_items` (unexpected items), `table_structure` (restricted output), and `TABLE_CONDITIONAL_LINES`.
  - The registry records each contrast's transport groups and floor cells [A, B].
  - Row and binding changes:
    - `compare_arms` is unconditional;
    - `compare_floor_ids`;
    - `planned_block_ids` and `bundle_block_ids` rows;
    - the fill's kept and removed block-id positions (`verdict_block_ids`, `registered_block_ids`);
    - `transport_group_id` rows;
    - `D_terms_j` (`terms_total`);
    - `loo_status(n, …)` and the loo row counts;
    - the projection p42 row is unconditional;
    - the sensitivity record's primary values are read directly (`sensitivity/primary/…`);
    - the kept-units `pack` row and the kept unit's cell identity.
  - Gate: `STATUS_KEYS` (F5) and the trigger object's keys.
  - Coverage:
    - new binding rules for the floor ids, transport groups and block ids;
    - `POSITIONS` gains five list positions;
    - the trigger object null rule;
    - `not_in_table`;
    - `COPIED_LISTS` (`copy_shortened`);
    - `leaves` carries each leaf's concrete path (`@@at`).
  - Module docstring.
- `tests/independent_recompute/test_rc_cmp9.py` (new, 32 tests): A1-A7 as above.
- `tests/independent_recompute/test_comparator.py`
  - The base fixture is producer-complete over the registry. New helpers: `BLOCKS`, `KEPT`, `TRANSPORT_GROUPS`,
    `loo_row`, `recompute_loo_row`, `structure_lines`, `reported_cells`, `extraction_cells`, `sensitivity_rows`,
    `ratio_rows`, `aggregate_key` and `no_table`.
  - Raised counts:
    - `test_planted_contrast`: 3 rows. The record's primary D and the term sum see D too.
    - `test_planted_p42_status`: p42 3. The projection row now exists.
    - `test_missing_or_null…`: the recompute side adds 2 expected rows, and its counterfactual also switches the
      table off.
  - `test_planted_outcome_word` plants the sensitivity outcome. The full outcome now feeds nine trigger lists.
  - `test_planted_kept_units` also expects the block-id and loo rows the kept set fixes, with a counterfactual for
    each.
- `test_rc_cmp7.py`
  - `with_loo` edits block 3's row in place.
  - `find(…, keep)` and `p42_line`: the p42 line is no longer the first `sensitivity_reported` line.
  - `test_neg8_line_dropped…` counts the table's routing row.
  - Counterfactuals add `no_table`. The G7.2 counterfactual record carries `pack`.
- `test_rc_cmp8.py`
  - `with_sensitivity` sets the widened values in place on the complete base. Unwidened, every sensitivity value
    equals its primary value.
  - `RELATION_WORDS` index 0.
  - `with_loo` and `with_assist_contrast` edit in place; `loo_b03`.
  - The loo word tests use the kept-n rule (base: `complete`).
  - The assist counterfactual drops the status row (as the RC-CMP-8 report states).
  - The F2.c count is 5 routing rows. The BETA source set includes the prefill floor lines.
  - Counterfactuals add `no_table` and `COPIED_LISTS`.
- `test_structural_rules.py`
  - `v3_floor` edits the base's whole v3 floor in place, with every copy of the 8B gate.
  - `ratio_line` edits one line in place.
  - The resolution-copy case counts the transport-group row.
  - The fill-only gate refuses `value_differs`: the row now exists.
  - The unregistered-contrast refusal may name the fill.
- `test_input_gate.py`: `without_gate` also switches the table off.
- `test_review_fixes.py`: the bool/int case sets the leave-one-out replay's rejection; the denominator test uses
  the base's PREFILL line.
- `.codex-report/RC-CMP-9.md` (this report).

## DECISIONS I MADE

1. **The table's rows are `routing_id` rows `expected/<check>`.** They are built through `Comparison.pairs` over
   (expected, L9-present, recompute-present). I did not add a new family: the S3 structure tests require family
   functions to iterate only through the union helper.
2. **An L9 item outside the table is DISAGREE, not a refusal.** It becomes `expected/unexpected/…`. The brief allows
   either.
3. **Conditions read the status or kept word on either side (the F5 pattern).** A word on one side requires the item
   on both. The conditions are:
   - a reported cell is computed;
   - an extraction floor is computed;
   - a block is kept and the kept n is at least 3;
   - the phase's kept n is at least 2 (`cross_window`);
   - the magnitude ratio is computable;
   - the refused variant of a reported cell.
4. **Lines with no recompute value use the recompute's registered window or section as their recompute side.** This
   covers structure lines, fixed sentences, `harvest_once`, `attempt_count` and `sensitivity_boundary`. The anchor
   is `windows.<PACK>`, `disclosures` or `sensitivity_bound`. Without it the A5 recompute-side deletion would have
   nothing to delete.
5. **`dominance_branch` is unconditional.** `branch` is an exact key of the D-165 closeout (`_CLOSEOUT_TOP_KEYS`,
   pinned).
6. **`kept_n` and `removed_block_ids` are required.** Block 5 always passes kept quads
   (`build_results_fill_input`).
7. **The v3 floor keys are required.** The manifest is v3 with a `claim_floor_rule`, and the engine refuses a v3
   contrast without them.
8. **Block identity:**
   - a verdict's planned and bundle block ids must equal the manifest's `block_ids`;
   - the fill's kept and removed ids are compared by position with the registered blocks, in registered order,
     that the recompute keeps or leaves out;
   - `COPIED_LISTS` refuses a fill list shorter than the verdict list it copies.
9. **The transport group of each arm is bound to the manifest's group for that arm's condition family.** The brief
   did not name it; the manifest registers it.
10. **The deterministic bound terms are checked through their sum.** The terms appear only in the verdict. Each term
    must have exactly the engine's keys, and the terms must sum to the recompute's D.
11. **The table requires only that nested keys be present.** A null is allowed. Values stay with the family rows.
12. **`kept_units_identity_mismatch` refuses.** A kept unit that names a cell other than the cell holding it refuses
    the run.

## OPEN ISSUES

1. **A non-p42 reported cell that is refused (below the registered minimum) on both sides still over-refuses.** The
   table expects its refused variant. But `compare_sensitivity` has no registered mapping from the recompute's
   `below_minimum` / `below_registered_minimum` to the record's `refused` / `paper_reported_energy_kept_units_below_minimum`,
   so the record row pairs with nothing. This predates RC-CMP-9 and is not exercised end to end.
2. **Carried from RC-CMP-8:** the value rows of a refused dominance ratio and of a not-computable assist contrast
   still over-refuse (`None` against `None`). These are Fable's S3.b (exit 2) and S3.c (exit 1). The table and the
   gate pass them.
3. **Leave-one-out with kept n of 1 or 2.** The engine prints rows there; the recompute computes rows only from 3
   (`LOO_MIN`). The table does not expect rows there. The row pairs still DISAGREE, as before.
4. **`Custody.step_ok` has no caller** (Fable F6, carried).
5. **The suite takes about 470 s instead of 178 s.** The base fixture is larger, and the A5 deletion test runs about
   900 comparisons.
6. **Unchanged and declared:** the G7 joint drop (A4/A5 of probe_cmp7) is bound by `exclusions_rederivation` (A5b).
   C5 (`reason_codes`) and K10 also stay as declared.
7. **The producer pins and the A1 producer analysis skip if a clone lacks `origin/main`.**

## NEEDS_RULING

1. **Does `consumer_family_declaration.json` count as a registered source?** It is in `REGISTERED_SOURCES`, but the
   brief's exhaustive list does not name it.
   - It supplies the floor cells [A, B]: the A3 relations and the floor table.
   - The gamma plan tree binds it by digest, and the registry has read it since RC-CMP-6.
   - The stricter reading I applied keeps it as a source and names it.
2. **Some compared lines remain outside the table.** These are the whole-machine `machine_member` and
   `machine_summary` lines and the `battery_temperature_sentence` (`TABLE_CONDITIONAL_LINES`).
   - The machine lines print only when a meter record exists, one per member of that record.
   - Their members are paired over three sides: L9's disclosure, the harvest meter record and the recompute
     (RC-CMP-3 X3). A drop from any one or two of those sides is DISAGREE; only a three-way omission passes.
   - This is the one output-keyed universe besides G7's run family. Registering it would need the plan trees'
     metered members per window.
   - I recommend this goes to Ed as the design question the brief anticipates.
3. **The window index is not on this branch.** `analysed_windows.json` exists only on `origin/main`, so it is named
   and not read.
   - The history lines (`attempt_history`, `g10`, `superseded_history`, `reharvest_account`) are not entries.
   - `attempt_count` (superseded False) is expected once per registered pack.
   - Its `causes` list elements are not checked (sweep residue).
4. **`flag_count` and `machine_absent` are not entries.**
   - `flag_count` lines follow the flag catalog, which is not a registered source.
   - `machine_absent` follows the `meter.absent` flag.
   - Dropping either still exits 0. Both are listed as declared exemptions.
5. **The leave-one-out minimum.** The table uses the recompute's 3 (`LOO_MIN`), not the engine's 1 (OPEN ISSUES 3).
