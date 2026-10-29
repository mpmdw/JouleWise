# Row-constructor sweep of `scripts/compare_b5_recompute.py` at 0d317afd4

Key source classes: **R-const** (a constant key: `PACKS`, `ARMS`, `{0: cell}`, a fixed name); **R-reg** (the sealed
registry: manifest, plan trees, specs, `registry.blocks`); **R-rec** (the recompute's own derivation); **L9-key**
(the key comes from an L9 id looked up literally in the registry, G3); **L9-out** (the row, or the key set, exists
only because L9 printed something). A `c.pairs` row set is the union of its sides; the table names each side.
"Exists if" is the condition on L9's side for the row set to be built at all. Probe results are in `probes.out`
(S1) and `sweep.out` (every leaf deleted once).

| # | constructor (line) | rows | key source | exists if | one-sided drop | both-sided / L9-only omission |
|---|---|---|---|---|---|---|
| 1 | `compare_runs` `c.exact routing_id run/{pack}/kept_units/exclusions_sha256` (:879) | 3 | R-const | always | n/a | n/a |
| 2 | `compare_runs` `c.pairs("run/", rereduced, universe, selected)` (:884) | per run | L9-out (re-reduced names) ∪ L9-out (kept-units record, declared NEEDS_RULING) ∪ R-rec | always | DISAGREE (G7.a, G7.c, G7.f) | joint drop exit 0 (G7.b, declared residual; bound by `exclusions_rederivation`, G7.b3) |
| 3 | `compare_runs` `c.numeric run_phase_energy_j` ×3 (:888-:901) | per run | inherits 2 | 2 | DISAGREE | as 2 |
| 4 | `compare_brackets` `c.numeric b_op_s` ×2 per pack, `block/*` ×3 (:1321-:1330) | 9 | R-const | always | DISAGREE | n/a |
| 5 | `compare_floors` `c.exact p42_status {pack}/extraction/p42` (:993) | 2 | R-const | always | DISAGREE (None) | n/a |
| 6 | `compare_floors` `c.pairs("floor/", l9_cells, mine_cells)` (:975) + 13 numeric | per cell | L9-key ∪ R-rec | always | DISAGREE | joint drop exit 0; the registry's extraction table is not a side |
| 7 | `compare_aggregate` `c.pairs("aggregate/", …)` (:1024) + 3 numeric; `aggregate_floor` None row when the file is absent (:1029) | per cell | L9-key ∪ R-rec | always | DISAGREE | joint drop exit 0; `registry.tables["floor"]` not a side |
| 8 | `compare_aggregate` `c.exact dominance_branch branch`, `dominance_sentence_licensed` (:1032-:1036) | 2 | R-const | always | DISAGREE | n/a |
| 9 | `compare_aggregate` `c.pairs("ratio/", l9_rows, our_ratios)` (:1041) + 5 rows; `ratio/none` when both empty (:1039) | per ratio | L9-key (numerator field literal) ∪ R-rec | always | DISAGREE | joint drop exit 0 |
| 10 | `compare_arms` `if "arm_gates" in floor:` `c.pairs(contrast/{cid}/arm/, positions, ARMS)` + 3 rows (:1125-:1131) | 2 per contrast | positions ∪ R-const (ARMS) | **L9-out: the verdict prints `arm_gates`** | emptied list: DISAGREE (S1.i) | **key absent on both copies: exit 0, 0 rows (S1.a); absent on the fill only: exit 0 (S1.c)** |
| 11 | `compare_arms` `if "resolutions" in floor:` `c.pairs(contrast/{cid}/resolution/, …)` + 3 numeric + `transport_rule_id` + source pairs `{0: cell}` (:1133-:1148) | 2 per contrast | positions ∪ R-const | **L9-out: the verdict prints `resolutions`** | emptied: DISAGREE (S1.h) | **absent on both: exit 0, `transport_rule_id` row gone (S1.a); fill only: exit 0 (S1.c)** |
| 12 | `compare_contrasts` `c.pairs("contrast/", l9_rows, mine_all)` (:1159) + ~30 rows per contrast (:1161-:1222) | per contrast | L9-key ∪ R-rec | always | DISAGREE | joint drop exit 0; `registry.tables["contrast"]` (the manifest's contrast ids) not a side |
| 13 | `compare_contrasts` definition / estimator / floor-rule `routing_id` rows (:1212-:1222) | 9 per contrast | R-reg on the recompute side | 12 | DISAGREE (None vs registered) | n/a (the registry side is always present) |
| 14 | `compare_contrasts` `claim_ready`, `claim_role`, `hypothesized_direction`, `confirmatory_status`, `loo_status` (:1196-:1210) | 5 per contrast | R-rec / R-reg | 12 | DISAGREE | n/a |
| 15 | `compare_contrasts` `c.pairs(contrast/{cid}/loo/, loo_l9, loo_mine)` (:1226) + 11 rows | per block | L9-key (`registry.block`) ∪ R-rec | 12 | DISAGREE | joint drop exit 0; `registry.blocks[cid]` ∩ kept quads not a side |
| 16 | `compare_contrasts` `influence_triggers` whole list + `c.pairs(positions, positions)` (:1241-:1245) | per row | positions ∪ R-rec | 15 | DISAGREE | n/a (recompute derives the list) |
| 17 | `compare_contrasts` `c.exact holm_order raw_p_order` (:1246) | 1 | R-const | always | DISAGREE | n/a |
| 18 | `compare_campaigns` `c.exact campaigns/{pack}/claim_usable` (:1313) | 2 | R-const | fill present (else `step11_outputs_absent`) | DISAGREE | n/a |
| 19 | `compare_reported` `projection` None row when absent (:1349); `c.pairs(reported/{pack}/, l9_cells, mine_cells)` (:1355) + 20 rows | per cell | L9-key ∪ R-rec (filtered by `registry.families`) | always | DISAGREE | joint drop exit 0; `registry.families(pack, False)` not a side |
| 20 | `compare_reported` `if refused is not None: c.exact p42_status {pack}/projection/p42` (:1380) | ≤1 per pack | R-const | **L9-out: the projection lists a refused p42 cell** | S1.k DISAGREE | **`refused_cells` dropped, relabelled or an object: exit 0, no row (S1.l-n); the word is still compared at rows 5 and 24** |
| 21 | `compare_sensitivity` `labelled(…, "sensitivity")` route by L9's `label`; None row when absent (:1413) | 1 | L9-out (route), fail-closed | always | DISAGREE | n/a |
| 22 | `compare_sensitivity` `B_max_s`, `T`, `attained_by_sequence` (:1416-:1419) | 3 | R-const | record found | DISAGREE | n/a |
| 23 | `compare_sensitivity` `c.pairs(sensitivity/windows/, windows, by_pack(ours.windows))` + `widened` (:1421-:1428) | per pack | L9-out ∪ R-rec; `gate_sensitivity` requires every `PACKS` window on L9's side | record found | DISAGREE | L9 cannot omit (required key); recompute omission alone: DISAGREE |
| 24 | `compare_sensitivity` `c.pairs(sensitivity/floor_cells/…)`, `(…/contrasts/…)`, `(…/reported_cells/…)` + relation and p42 rows (:1432-:1484) | per cell / contrast | L9-key ∪ R-rec (+ recompute p42 cells) | record found | DISAGREE | joint drop exit 0; the registry tables not a side |
| 25 | `compare_disclosures` record None row (:1550); `c.pairs(disclosure/cells/, lines, our_cell_lines)` (:1557) | per (word, pack, cell) | L9-key ∪ R-rec (cross_window, battery_assist, **reported_cell since RC-CMP-8**) | record found | DISAGREE (drop `reported_cell`, `battery_assist_cell`: exit 1) | `attribution_floor`, `kept_units`: **not paired, whole-line drop exit 0** (values compared from the projection) |
| 26 | `compare_disclosures` `c.pairs(disclosure/contrasts/, contrasts, our_contrast_lines)` (:1586) | per (cid, word) | L9-key ∪ R-rec (battery_assist_contrast, magnitude_*, loo_*) | record found | DISAGREE (exit 1 for those four words) | `primary_contrast`, `contrast_interval`, `decision_floor`: **not paired, whole-line drop exit 0** (values compared from the verdicts) |
| 27 | `compare_disclosures` `c.pairs(disclosure/floors/floor_composition/, compositions, mine_floors)` + `source` (:1633-:1638) | per cell | L9-key ∪ R-rec | record found | DISAGREE (exit 1) | n/a |
| 28 | `compare_disclosures` `WINDOW_CLAIM_LINES` `c.pairs(…, printed, dict.fromkeys(PACKS))` (:1643-:1654) | 3 per word | L9-out ∪ **R-const (PACKS)** | record found | DISAGREE (F2.c, F2.d, F2.e: exit 1) | n/a (fixed by RC-CMP-8) |
| 29 | `compare_disclosures` `c.pairs(disclosure/window_lines/, window_line_names, our_neg8)` and the inner `c.pairs(rows, neg8s)` (:1656-:1659) | per pack, 3 words | L9-out ∪ R-rec (every pack with a NEG-8 result, all three words) | record found | DISAGREE (exit 1 for each word) | both sides lacking a window's NEG-8: exit 0 |
| 30 | block lines `dominance_branch`, `dominance_ratio`, `sensitivity_*` (no constructor; coverage binds their leaves to rows 8, 9, 22-24) | 0 | — | — | — | **whole-line drop exit 0** for all seven words (values compared from the closeout and the record) |
| 31 | `compare_machine` `meter_record` None row (:1778); `c.pairs(machine/{pack}/, disclosed[, harvested], mine)` + rows (:1781-:1815) | per member | L9-out ∪ harvest record ∪ R-rec | any side non-empty | DISAGREE | all three empty: skipped (no window has a meter line) |
| 32 | `compare_machine` `if available:` battery rows (:1801) | 2 | harvest record's word | the record says available | the `battery_term` exact row DISAGREEs when the sides differ | n/a |
| 33 | `compare_machine_summary` `c.pairs(machine_summary/{pack}/, summaries, groups)` + `if stat in line or stat in derived` + band rows (:1838-:1854) | per model | L9-out ∪ R-rec | 31 | DISAGREE (a statistic either side has) | both lacking a statistic: no row (the recompute derives every statistic from finite rho) |
| 34 | `compare_exclusions` `c.exact exclusions_rederivation {PACK}` (:1875) | 3 | R-const | always | DISAGREE | n/a |
| 35 | `coverage` (every printed step-11 leaf must bind an agreeing row) (:2259) | per leaf | L9-out by design | a leaf is printed | refuses `no_row` / `value_differs` / `row_disagrees` | **an unprinted leaf is not covered**: see `sweep.out` for every fill and disclosure leaf whose deletion exits 0 |

Output-derived existence (rows 10, 11, 20) and unpaired producer-unconditional lines (rows 25, 26, 30) are the
findings; rows 2, 6, 7, 9, 12, 15, 19, 24 are the union pattern (one-sided drop always DISAGREEs; a joint drop is
invisible because the registry's own table is not a side where one exists).
