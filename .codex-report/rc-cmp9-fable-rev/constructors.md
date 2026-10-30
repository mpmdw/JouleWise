# Constructor sweep of `scripts/compare_b5_recompute.py` at f9f86869e (answer 2)

Key source classes as in `review/2026-10-29-rc-cmp8-fable-rev/row_constructors.md`: **R-reg** (the sealed registry:
manifest, plan trees, specs, declaration, `registry.blocks`), **R-const** (`PACKS`, `ARMS`, `MODELS`, a literal key
set), **R-rec** (the recompute's own derivation), **L9-key** (an L9 id looked up literally in the registry, G3),
**L9-out** (the check exists, or its key set exists, only because L9 printed something). A condition column names the
registered condition read on *both* sides (`condition_holds`, :1123); "—" is unconditional. Probe ids refer to
`probes.out`, `probes_extra.out`, `probes_prior.out` (my RC-CMP-8 probes re-run) and `opus_probe.out`.

## The expected-check table (`expected_checks`, :726-1001): 29 families, 256 entries

| family | entries | L9 locator keyed by | recompute item keyed by | condition | drop / relabel evidence |
|---|---|---|---|---|---|
| `fill_document` | 1 | R-const (`FILL_SHAPE` top, gamma, characterization, floor_artifact) | R-const | — | Opus confirm: `gamma` removed exit 2 |
| `fill_campaign` | 2 | R-const (alpha, beta; `FILL_SHAPE["campaign"]`) | `inputs.<PACK>` R-const | — | sweep: every key non-zero |
| `verdicts_document` | 1 | R-const | R-const | — | sweep |
| `kept_units_record` | 3 | R-const (PACKS; file name pattern) | `inputs.<PACK>` | — | sweep: `pack`, `exclusions_sha256`, `cells` non-zero |
| `disclosure_document` | 1 | R-const (`DISCLOSURE_SHAPE["top"]`) | `disclosures` | — | Opus confirm: `block_lines` removed exit 1 |
| `disclosure_window` | 3 | R-const (PACKS, `DISCLOSURE_SHAPE["window"]`) | `windows.<PACK>` | — | sweep |
| `window_line` | 69 | R-const (PACKS × `WINDOW_LINES` + `TRIPWIRES`); selector `{line: word}` / `{line: tripwire, tripwire: key}` | `windows.<PACK>` (+ neg8 fields) | — | P10.a duplicate refused; probes_prior F2.c-e exit 1; sweep |
| `block_line` | 5 | R-const (`attempt_count` × PACKS with `superseded: False`; `harvest_once`; `sensitivity_boundary`) | `windows.<PACK>` / `disclosures` / `sensitivity_bound` | — | sweep (whole line non-zero); `causes/*` declared NR-3 |
| `fixed_sentence` | 13 | R-const (`FIXED_SENTENCE_WORDS` + 2) | `disclosures` | — | sweep: each `text` non-zero |
| `sensitivity_record` | 1 | R-const (`SENSITIVITY_SHAPE`), 2 copies | `sensitivity_bound` | — | Opus confirm: copy removed exit 1 |
| `sensitivity_bmax` | 1 | R-const, 3 copies | `sensitivity_bound` | — | Opus confirm |
| `sensitivity_window` | 3 | R-const (PACKS), 3 copies | `windows.<PACK>`, `sensitivity_bound.windows` | — | Opus confirm |
| `sensitivity_reported` | 10 | R-reg (`tables["reported"]`, selector `{cell_id}` / `{record.cell_id}`), 3 copies; p42 refused keys | `p42.<fam>` / `sensitivity_bound.reported_cells.<fam>` / `reported_cells.<fam>` | p42 —; computed: `reported_computed`; refused variant: `not reported_computed` | P1/P2, X1, X5; Opus joint2 |
| `projection_cell` | 6 | R-reg; `any` of `cells` (18 keys) or `refused_cells` (code); p42 refused only | `reported_cells.<fam>` / `p42.<fam>` | — | P10.b duplicate refused; probes_prior S1.l-n exit 1; P2 |
| `cell_line` | 20 | R-reg × `CELL_WORDS` (selector `{pack, cell_id, line}`) | `reported_cells.<fam>` / `battery_assist.<fam>` / `cross_window.<model/phase>` | `reported_computed`; `cross_window` also phase n ≥ 2 | P2.a/b (6 and 4 table rows) |
| `sensitivity_floor` | 4 | R-reg (`tables["floor"]`), 3 copies | `sensitivity_bound.floor_cells.<key>` | — | Opus joint2 |
| `aggregate_cell` | 4 | R-reg | `floor_cells.<key>` | — | Opus confirm |
| `ratio` | 12 | R-reg × `CLOSEOUT_RATIOS`; ratio table `{cell_id, component, numerator_field}`; line `{cell_id, component, @ratio}` | `dominance.ratios.<key/comp>` / `dominance.common_mode.<key>` | — (values: F5 gate) | P5.a/b: the text selector fails closed (MISSING + unexpected); Opus joint2 ratio row exit 1 |
| `dominance_branch` | 1 | R-const (closeout + line) | `dominance.branch` | — | Opus confirm |
| `extraction_cell` | 12 | R-reg (`tables["extraction"]`) | `floors.<key>` / `p42.<fam>` | — | Opus joint2 extraction cell exit 2 |
| `extraction_floor` | 8 | R-reg (16 floor values) | `floors.<key>` | `floor_computed` | P3, P3.a/b, X3 |
| `floor_line` | 20 | R-reg × (`kept_units`; `floor_composition` non-p42) | `floors.<key>` (+ neg8 `source`) | composition: `floor_computed` | P3.a/b |
| `bracket` | 4 | R-const (PACKS + block) | `windows.<PACK>.b_op_s`, `sensitivity_bound` | — | sweep |
| `contrast` | 2 | R-reg (`tables["contrast"]`, selector `{contrast_id}`): verdict (ENGINE_KEYS nested) + fill (FILL_SHAPE nested) | `contrasts.<cid>` (16 keys) | — | Opus confirm (row, section, document removed) and joint2 |
| `contrast_floor_arm_gate` | 4 | R-reg × `ARMS` (positions 0, 1) | `floor_cells.<arm>` | — | probes_prior S1.a/c exit 1 (F2 closed) |
| `contrast_floor_resolution` | 4 | R-reg × `ARMS` | `floor_cells.<arm>` | — | probes_prior S1.a/c exit 1 |
| `loo_row` | 20 | R-reg (`registry.blocks[cid]`, selector `{omitted_block_id}`), 2 copies | `contrasts.<cid>.loo` `{block_number: position}` | `loo_block_kept` (kept on either side, n ≥ 3 on either side) | P11.a joint drop exit 2; Opus loo all non-zero |
| `contrast_line` | 20 | R-reg × `CONTRAST_WORDS` (selector `{contrast_id, line}`; `kept_units` by `{pack: gamma, cell_id}`) | `contrasts.<cid>` / `battery_assist.<cid>` / `descriptive.<cid>` | `magnitude_ratio` estimates: `ratio_computable` | P4, P4.a/b, X4; Opus confirm (6 lines) |
| `sensitivity_contrast` | 2 | R-reg, 3 copies | `sensitivity_bound.contrasts.<cid>` | — | Opus confirm |

Every locator is keyed by the registry or a literal constant; no entry's existence, key or route is read from either
output. The three `condition_holds` kinds that read outputs (`reported_computed`, `floor_computed`, `ratio_computable`;
`loo_block_kept` and `cross_window` read kept words and n) read **both** sides and switch a check on, never off, when
either side says computed (P2, P3.a/b, P4.a/b non-zero). The one selector read from printed text (`@ratio`, :1060)
fails closed (P5). Closed lists (`CLOSED`, :1026): an unclaimed item is `unexpected/` DISAGREE (P5), an unregistered id
refuses (P12.a/b), a duplicate refuses (P10.a/b), an invented word refuses `line_word_unregistered` (P9.a).

## Row constructors outside the table (every `c.pairs`, `c.exact`, `c.numeric` site)

| # | constructor (line) | key source | exists if | change since 0d317afd4 |
|---|---|---|---|---|
| 1 | `compare_expected` `c.pairs("expected/", …)` (:1234) | the table (R-reg / R-const) ∪ both sides' presence | always (first in `run`) | new |
| 2 | `compare_runs` `kept_units/exclusions_sha256`, `kept_units/pack` (:1598-1601) | R-const | always | `pack` row new (A4) |
| 3 | `compare_runs` `c.pairs("run/", rereduced, universe, selected)` (:1603) | L9-out ∪ L9-out (kept-units) ∪ R-rec | always | unchanged: G7.b/b2 joint drop exit 0, bound by `exclusions_rederivation` (G7.b3 exit 1), declared |
| 4 | `step_2_universe` `kept_units_identity_mismatch` (:1633) | L9 record vs its own cell key | always | new refusal (A4) |
| 5 | `compare_floors` p42 row (:1705); `c.pairs("floor/", l9_cells, mine_cells)` + 13 numeric (:1710-1722) | L9-key ∪ R-rec | always | **F1: rows exist whatever `floor_computed` says; both sides refusing → 15 None/None rows (P3, X3)** |
| 6 | `compare_aggregate` `c.pairs("aggregate/", …)`, branch rows, `c.pairs("ratio/", …)` (:1766-1792) | L9-key ∪ R-rec; R-const | always | unchanged; joint drops now caught by the table (Opus joint2) |
| 7 | `compare_arms` `c.pairs(arm/, positions, ARMS)`, `c.pairs(resolution/, …)` + `transport_group_id` + source pairs (:1850-1874) | positions ∪ **R-const (ARMS)** | registry entry | F2 closed: unconditional (was `if "arm_gates" in floor`) |
| 8 | `compare_floor_ids` `c.pairs(scope_position/, positions, registered [A, B])` (:1914) | positions ∪ R-reg (declaration) | always (3 call sites) | new (A3) |
| 9 | `compare_contrasts` `c.pairs("contrast/", l9_rows, mine_all)` + ~35 rows (:1928-2010), incl. `D_terms_j`, `loo/l9_rows`, `loo/recompute_rows` (if recompute n ≥ 3), `planned_block_ids`, `bundle_block_ids`, kept/removed positions | L9-key ∪ R-rec; R-reg for ids | always | new rows; `loo_status(n, …)` from the kept n (:2051) |
| 10 | `compare_contrasts` `c.pairs(loo/, loo_l9, loo_mine)` + rows, `influence_triggers` (:2019-2037) | L9-key (`registry.block`) ∪ R-rec | row 9 | joint drop now caught by the table (P11.a) |
| 11 | `compare_campaigns`, `compare_brackets` (:2089-2113) | R-const | fill present | unchanged |
| 12 | `compare_reported` `c.pairs(reported/{pack}/, …)` + rows (:2138); `{pack}/projection/p42` (:2164) | L9-key ∪ R-rec; R-const | always | F4 closed: p42 row unconditional |
| 13 | `compare_sensitivity` windows, floor cells, contrasts, reported pairs + relation rows + `primary/*` rows + `compare_floor_ids` (:2212-2300) | L9-key ∪ R-rec | record found | new primary rows; **OPEN ISSUE 1 confirmed: both sides refusing a reported cell → 17 None/None rows (P1, X1, X5)** |
| 14 | `compare_disclosures` cells / contrasts / floor_composition / window lines pairs (:2395-2499) | L9-key ∪ R-rec; R-const (PACKS) | record found | **F1: `magnitude_ratio` value rows (:2439-2443) exist whatever `ratio_computable` says → 3 None/None rows (P4, X4)** |
| 15 | `compare_machine`, `compare_machine_summary` (:2564-2660) | L9-out ∪ harvest record ∪ R-rec | any side non-empty | unchanged: the output-keyed universe the report names (NEEDS_RULING 2) |
| 16 | `compare_exclusions` (:2679) | R-const | always | unchanged |
| 17 | `coverage` (:3112): every printed step-11 leaf binds an agreeing row **inside a claimed item** (`not_in_table`, :3161), `COPIED_LISTS` (:3105) | L9-out by design, now bounded by the table's claims | a leaf is printed | new bound |

Rows 3 and 15 are the two output-keyed universes left, both declared by RC-CMP-9 (G7 joint drop bound by
`exclusions_rederivation`; machine lines NEEDS_RULING 2). Rows 5, 13, 14 are value rows built outside their registered
condition: fail-closed over-refusals, not the class.
