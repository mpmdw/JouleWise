# RC-CMP9-OPUS-REV sweep: row constructors and expected-check families at f9f86869e

Key source: **REG** = sealed config / plan tree / manifest / declaration / PACKS / pinned producer literal;
**OUT** = the item exists only because an output printed it. Since RC-CMP-9 an OUT `pairs` universe is
safe for a drop when a REG table entry requires the same item on both sides first (column "Table").
Probes: `probe_cmp8.py` (confirm, joint2, loo, relabel, drop, ours, joint), `probe_cmp9.py` (n2, extra, ratio),
Fable's `fable_probes.py` / `fable_sweep.py`; base `with_neg8 + with_references + with_sensitivity`,
widened and unwidened. Exit codes are from the `.out` files in this directory.

## Row constructors (`c.pairs`, scripts/compare_b5_recompute.py)

| Line | Constructor | Universe source | Table entry backing existence | L9 drop | Joint drop | Relabel |
|---|---|---|---|---|---|---|
| :1234 | `expected/` | REG (`expected_checks(registry)`) + `unexpected/` (closed lists) | itself | 1 (all 22 confirm drops non-zero) | 2 (joint2: all 10 non-zero) | 0 of 4081 exit 0 |
| :1603 | `run/` | OUT (kept-units ∪ rereduced ∪ recompute) | none (G7, declared) | 1 (G7.a) | **0** (G7.b, G7.b2; declared, bound by `exclusions_rederivation`, G7.b3 1) | 1 |
| :1710 | `floor/` | OUT | `extraction_cell`, `extraction_floor` (REG 12/8) | non-zero | 2 (joint2 extraction cell) | none exit 0 |
| :1766 | `aggregate/` | OUT | `aggregate_cell` (REG 4) | non-zero | non-zero | none |
| :1783 | `ratio/` | OUT | `ratio` (REG 12) | non-zero | 1 (joint2 ratio row) | R/R_cm text swap: 2 when values differ (`ratio`), 0 only when R = R_cm (no number changes) |
| :1850/:1858 | `arm/`, `resolution/` | REG (ARMS) | `contrast_floor_*` | 1 (S1.a-i) | n/a | 2 |
| :1870 | `resolution/{i}/source/` | REG | `contrast_floor_resolution` | non-zero | n/a | 2 |
| :1914 | `*_position/` floor ids | REG (declaration [A, B]) | `contrast` (`floor_row_ids/0,1`) | non-zero | n/a | 2 (confirm RELABEL) |
| :1928 | `contrast/` | OUT | `contrast` (REG 2) | 2 | 2 (joint2 decode contrast) | none |
| :1994/:1996 | kept/removed block-id positions | OUT both sides (L9 `included`, recompute `kept_quads`) | `contrast` (key only) + `kept_quads` exact row + `COPIED_LISTS` | 2 | n/a | none |
| :2019 | `contrast/{cid}/loo/` | OUT | `loo_row` (REG blocks) **only when a kept n ≥ 3** | 2 (loo.out) | 2 (loo.out joint) | 2 |
| :2019 at kept n 1-2 | same | OUT, recompute prints none | **none** | sound output 2 (31 fails); **rows dropped + `loo_counts` 0: exit 0** (`probe_cmp9 n2`) | n/a | n/a |
| :2037 | `influence_triggers/` | recompute-derived | `loo_row` key | non-zero | n/a | n/a |
| :2138 | `reported/` | OUT | `projection_cell` (REG 6) | non-zero | 2 (joint2 reported cell) | none |
| :2212 | `sensitivity/windows/` | OUT | `sensitivity_window` (REG 3) | non-zero | n/a | none |
| :2222/:2243/:2271 | sensitivity floor/contrast/reported | OUT | `sensitivity_floor`/`_contrast`/`_reported` (REG) | non-zero | 2 (joint2 floor cell) | none |
| :2395 | `disclosure/cells/` | OUT | `cell_line` (REG, condition computed / phase n ≥ 2) | 1 | non-zero | none |
| :2417/:2436 | `assist_members/` strata | OUT (Counter keys, producer prints only non-zero strata) | key `assist_members` only | 1 if recompute has the stratum | joint only if recompute also lacks it | n/a |
| :2422 | `disclosure/contrasts/` | OUT | `contrast_line` (REG) | 1 | non-zero | none |
| :2457 | `loo_magnitude` rows | recompute-derived selection | `contrast_line` key `rows` | 1 | n/a | n/a |
| :2464 | `floor_composition/` | OUT | `floor_line` (REG, condition computed) | 1 | 2 | none |
| :2476 | `window_lines/{word}/` | REG (PACKS) | `window_line` | 1 | n/a | n/a |
| :2486/:2488 | NEG-8 window lines | OUT | `window_line` (REG) | 1 | n/a | none |
| :2587 | `machine/{pack}/` | **OUT** (disclosure ∪ meter record ∪ recompute; skipped when all three empty) | none (`TABLE_CONDITIONAL_LINES`, declared NEEDS_RULING 2) | 1 if recompute or meter holds the member | **three-way omission passes** (declared) | n/a |
| :2642 | `machine_summary/{pack}/` | **OUT** | none (declared) | as above | as above | n/a |

## Expected-check families (expected_checks, :726-:1001): every key is registered

| Family | Entries | Key source | Condition (read on either side) |
|---|---|---|---|
| fill_document, verdicts_document, disclosure_document | 1 each | constant | — |
| fill_campaign | 2 | REG (alpha, beta) | — |
| kept_units_record, disclosure_window, bracket | 3/3/4 | PACKS | — |
| window_line | 69 | PACKS × `WINDOW_LINES` (21) + `TRIPWIRES` (2), pinned | — |
| block_line | 5 | PACKS (attempt_count) + constants | — |
| fixed_sentence | 13 | `FIXED_SENTENCE_WORDS` (pinned) + 2 | — |
| sensitivity_record/bmax/window | 1/1/3 | constant / PACKS | — |
| sensitivity_reported | 10 | manifest reported cells (6; p42 refused) + refused variants | computed / not |
| projection_cell | 6 | REG | — |
| cell_line | 20 | REG reported cells × 5 words | computed; cross_window also phase n ≥ 2 |
| sensitivity_floor, aggregate_cell | 4/4 | declaration floor cells | — |
| ratio | 12 | floor cells × `CLOSEOUT_RATIOS` (pinned) | — |
| dominance_branch | 1 | constant | — |
| extraction_cell / extraction_floor / floor_line | 12 / 8 / 20 | extraction specs | floor computed |
| contrast, contrast_floor_arm_gate, contrast_floor_resolution | 2/4/4 | manifest × ARMS | — |
| loo_row | 20 | manifest block ids | block kept and **kept n ≥ 3** |
| contrast_line | 20 | manifest × 9 words (+ ratio estimates) | ratio computable |
| sensitivity_contrast | 2 | manifest | — |

Count at this head: 256 entries, 29 families (TableTests pass). The table is built from `custody.registry`, which reads
only the pinned configs under `configs/campaigns` (`Registry.__init__`, `REGISTRY_PINS`); no output reaches it.
Outputs reach only the conditions, and only to add expectations (either side switches an item on).

## Output-derived existence that remains (no registered entry)

1. Leave-one-out rows at a kept n of 1 or 2 (:2019; `condition_holds` `loo_block_kept` uses `LOO_MIN` = 3). The engine
   prints a row per kept block from n ≥ 1 (`analysis_engine/__init__.py` `_loo_family`); the comparator expects none.
   Sound output refuses; dropping the rows exits 0. **Not declared as an exit-0 path** (OPEN ISSUES 3 states only the
   over-refusal).
2. Whole-machine member and summary lines (:2587, :2642, `TABLE_CONDITIONAL_LINES`): declared NEEDS_RULING 2.
3. `battery_temperature_sentence`, `flag_count`, `machine_absent`, history lines, attempt `causes`: declared
   (NEEDS_RULING 2-4); none carries a claim number or claim word (the sentence's `neg8` word is bound to `neg8_screen`, F2.f).
4. The G7 run universe (:1603): declared since RC-CMP-7, bound by `exclusions_rederivation`.
