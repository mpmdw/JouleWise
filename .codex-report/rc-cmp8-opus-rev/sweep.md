# RC-CMP8-OPUS-REV sweep: every row constructor in scripts/compare_b5_recompute.py at 0d317afd4

Key source:
- **REG**: the key comes from the sealed config, the plan tree, the manifest, the registered packs, or a constant.
- **OUT**: the key exists only because L9 or the recompute printed the item. A key routed through the registry (G3)
  is still OUT when its *existence* comes from an output.

Probes:
- Base for every probe: `with_neg8 + with_references + with_sensitivity(widened)`, run both widened and unwidened.
- Probe sources: `probe_cmp8.py` (drop, ours, relabel, confirm, joint2, loo) and `probe_cmp7.py` (A*, K*).
- "L9 drop" removes the item from L9's output, and only from that output.
- "Joint" removes it from every L9 output and from the recompute.
- "Relabel" swaps the key for another registered value.

| # | Line | Constructor (scope) | Key source | L9 drop | Joint drop | Relabel |
|---|---|---|---|---|---|---|
| 1 | :891 | `exact run/{pack}/kept_units/exclusions_sha256` | REG (PACKS) | 1 | 1 | n/a |
| 2 | :895 | `pairs run/` | OUT: L9 kept-units universe and rereduced files ∪ recompute selected | A1 1 | **A4/A5 0** (declared; A5b 1 via exclusions_rederivation) | A8 1 |
| 3 | :993 | `exact {pack}/extraction/p42` | REG (alpha, beta) | n/a | n/a | n/a |
| 4 | :999 | `pairs floor/` (+ numeric rows) | OUT: extraction cells ∪ recompute floors | 2 | 2 (caught by the sensitivity rows) | none exit 0 |
| 5 | :1055 | `pairs aggregate/` | OUT | 2 | not run | none exit 0 |
| 6 | :1063/:1066 | `exact branch`, `dominance_sentence_licensed` | REG (constant) | 2 | n/a | n/a |
| 7 | :1072 | `pairs ratio/` (+ status) | OUT: ratio table ∪ recompute ratios | 2 | 1, only because the fixture has one ratio (`ratio/none` guard) | none exit 0 |
| 8 | :1138 | `pairs contrast/{cid}/arm/` | REG (ARMS) | 2 | n/a | n/a |
| 9 | :1147 | `pairs …/resolution/` | REG (ARMS) | 2 | n/a | n/a |
| 10 | :1156 | `pairs …/resolution/{i}/source/` | REG ({0: cell}) | 2 | n/a | n/a |
| 11 | :1172 | `pairs contrast/` (+ ~30 rows, :1175-:1231) | OUT: verdict contrasts ∪ recompute contrasts (ids registry-checked) | 2 | **0 (decode contrast gone everywhere)** | none exit 0 |
| 12 | :1215 | `exact {cid}/loo_status` | value from whether the recompute printed rows | n/a | **0 (joint: rows gone, `not_run`)** | n/a |
| 13 | :1237 | `pairs contrast/{cid}/loo/` | OUT: verdict loo rows ∪ recompute loo | 2 | **0** | 2 |
| 14 | :1255 | `pairs …/influence_triggers/` | recompute-derived (re-derived from its numbers) | RC-CMP-8 tests | n/a | n/a |
| 15 | :1258 | `exact holm_order` | REG (constant) | n/a | n/a | n/a |
| 16 | :1312 | `exact campaigns/{pack}/claim_usable` | REG (alpha, beta) | 2 | n/a | n/a |
| 17 | :1320-:1327 | bracket rows | REG (PACKS, constant) | 1 | n/a | n/a |
| 18 | :1353 | `pairs reported/{pack}/` | OUT: projection cells ∪ recompute reported_cells | 2 | **0 (reported cell gone everywhere)** | none exit 0 |
| 19 | :1379 | `exact {pack}/projection/p42` | OUT: exists only if L9 prints `refused_cells` | **0** (redundant with #3) | n/a | n/a |
| 20 | :1422-:1424 | sensitivity B_max rows | REG (constant) | 2 | n/a | n/a |
| 21 | :1427 | `pairs sensitivity/windows/` | OUT, but the gate requires every pack | 2 | n/a | n/a |
| 22 | :1437 | `pairs sensitivity/floor_cells/` | OUT | 2 | 2 | **0** (`floor_cell_ids`, #31) |
| 23 | :1453 | `pairs sensitivity/contrasts/` | OUT | 2 | 0 (with #11) | **0** (`floor_cell_ids`) |
| 24 | :1475 | `pairs sensitivity/reported_cells/` | OUT (+ REG p42 ids) | 2 | 0 (with #18) | none exit 0 |
| 25 | :1595 | `pairs disclosure/cells/` (cross_window, battery_assist_cell, reported_cell) | OUT | 1 | 0 (with #18) | none exit 0 |
| 26 | :1617/:1636 | `pairs …/assist_members/` | OUT | 2 (required key) | n/a | n/a |
| 27 | :1622 | `pairs disclosure/contrasts/` (battery_assist, magnitude_*, loo_*) | OUT | 1 | 0 (with #11) | none exit 0 |
| 28 | :1657 | `pairs loo_magnitude rows` | recompute-derived | not in base | n/a | n/a |
| 29 | :1664 | `pairs floor_composition/` | OUT | 1 | 2 | none exit 0 |
| 30 | :1676 | `pairs window_lines/{word}/` (below_screen_bound, neg8_screen) | **REG (PACKS)**, new this round | 1 | n/a | n/a |
| 31 | :1686/:1688 | `pairs window_lines/{pack}/` (NEG-8 lines) | OUT | 1 | not run | none exit 0 |
| 32 | :1787 | `pairs machine/{pack}/` | OUT | not in base (meter tests) | n/a | n/a |
| 33 | :1842 | `pairs machine_summary/{pack}/` | OUT | not in base | n/a | n/a |
| 34 | :1882 | `exact exclusions_rederivation` | REG (PACKS) | 1 | n/a | n/a |
| 35 | :2292 | `coverage()` leaf binding for the fill and the disclosure: every printed leaf must bind an AGREE row | **OUT: a check exists per printed leaf** | **0 for 22 named drops** (confirm.out) | n/a | **0**: fill `floor_source_cell_ids`, `floor/floor_row_ids` (IDENTITY :2182) |
| 36 | :745/:757/:732 | `gate_fill`, `gate_lines`, `gate_sensitivity` (`require`) | OUT per printed row; REG only for fill campaigns and sensitivity windows | see #35 | n/a | n/a |

Constant guard rows `contrasts`, `ratio/none`, `aggregate_floor`, `disclosure/record` and `sensitivity/record`
fire only when a whole output or section is empty on both sides.

Output-derived constructors whose drop or joint probe exits 0 with a missing claim:
- #2, declared and bound;
- #11, #12, #13, #18, #23 and #24, joint;
- #19, redundant;
- #35/#36, L9 alone (22 cases).

Relabels exiting 0: #35, plus the identity leaves (`kept-units` `pack` and unit `cell_id`, and an excluded block's
`block_id`). See `relabel_ids.out`.
