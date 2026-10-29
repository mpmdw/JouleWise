VERDICT: ACCEPT_WITH_FIXES

# RC-CMP8-FABLE-REV: delta review of RC-CMP-8 (`c372211bf..0d317afd4`)

Seat RC-CMP8-FABLE-REV, Fable 5.1, cloud, synthetic only; no real block-5/6/BYTES data opened or searched for.
Branch `review/2026-10-29-rc-cmp8-fable-rev` at `0d317afd4`. `/usr/bin/python3.13`, `TMPDIR=/tmp/claude-0/rcfable8/tmp`
(outside the checkout, no float-like token). Evidence in `.codex-report/rc-cmp8-fable-rev/`. Producers on
`origin/main` (`b5_analysis/{disclosures,sensitivity}.py`, `analysis_engine/artifact.py`, `results_fill_adapter.py`)
read as text only.

**Summary.** Every claim RC-CMP-8 makes holds under re-execution: my RC-CMP-7 probes F2.c, F2.d, F2.e exit 1 and
F2.g exits 2 at this head, G7.0-G7.g are unchanged, the gate-passing relabel sweep (70 tried, 40 exit 0) moves no
keyed word, the producer-shaped sensitivity fixture exits 0 widened and unwidened with all 19 relation rows AGREE,
and the suite is `Ran 330 tests` / `OK (skipped=18)` (`suite.out`). The design is not closed against the class.
The required-key gate is one level deep and names claim words only, so a claim *number*, a nested object or a
whole line or section the producer writes unconditionally is required only when L9 prints it: of 1933 single-leaf
deletions across every L9 input and the recompute, 831 exit 0, and about 290 of those remove a producer-unconditional
claim value, object or line (`sweep.out`, `classify.out`). The fill with its `gamma` object deleted exits 0. Two
row constructors still exist only because L9 printed a key (F2, F4). No over-refusal found.

## Findings (ranked)

**F1 (HIGH, fix next round). Claim numbers, nested objects and whole sections are required only when printed; the
fill and the disclosure can omit them with exit 0.** `require` (`:717`) checks key presence one level deep;
`FILL_KEYS` (`:709`) names 7 of the adapter's 24 unconditional contrast keys (`results_fill_adapter.py:163-180`);
`gate_fill` iterates `get(fill, "gamma", "contrasts", default=[])` (`:749`), so no contrast row is required;
`gate_sensitivity` returns when the disclosure's `sensitivity` is absent (`:735`) although `disclosures.py:1303`
always writes it; `coverage` (`:2292`) walks printed leaves only. `sweep.out` (base: `with_sensitivity` widened,
exit 0; each deletion alone):
- fill: `gamma` → exit 0; `gamma/contrasts` → 0; `gamma/contrasts/0` → 0; per contrast `estimate`, `interval`,
  `interval/lower`, `decision_interval`, `deterministic_widening_total`, `n`, `df`, `t_critical_95`, `floor`,
  `floor/active_floor_j`, `floor/floor_abs_j`, `metric`, `conditions`, `floor/arm_gates`, `floor/resolutions` → 0
  (100 producer-unconditional fill leaves, `classify.out`). The engine's `_ESTIMATOR_KEYS`, `_FLOOR_KEYS`,
  `_V3_FLOOR_KEYS`, `_ARM_GATE_KEYS` and `_FLOOR_RESOLUTION_KEYS` are exact key sets (`artifact.py:210-258`,
  `:2233-2240`) and the adapter copies `row["floor"]` whole.
- disclosure: `sensitivity` → 0, `sensitivity/reported_cells` → 0, `sensitivity/contrasts/0` → 0, `block_lines` → 0,
  `fixed_sentences` → 0; `contrasts/*/estimator/estimate` (primary_contrast) → 0 (the line keeps `estimator: {}`),
  `estimator/{s_d,SE_total,n,df,t_critical_95,metrology_aware_CI95/*}` → 0, `decision_interval/lower|upper` on
  `primary_contrast` and `decision_floor` → 0, `block_lines/*/record/{primary,sensitivity}/*` and
  `sensitivity/*/{primary,sensitivity}/*` → 0, `cells/*/primary/{mean_j,h_j,B_j,lower_j,upper_j}` → 0
  (158 leaves). `disclosures.py:482` prints `_plain(verdict["estimator"])`, `sensitivity.py:302,320,344` print
  both value objects whole.
- sensitivity record (`outputs/*.json`, read by `compare_sensitivity`): `floor_cells/*/primary`, `contrasts/0/primary`,
  `reported_cells/2/primary` and their members → 0 (26 leaves): the record's primary values are read only through the
  disclosure copy's coverage, and that copy is optional.
- Fix: a producer-shaped required-path table per document (the adapter's and engine's key sets for the fill, nested;
  `_cell_values`, `_ESTIMATOR_KEYS`, `decision_interval` lower/upper, the sensitivity value sets for the disclosure;
  `sensitivity`, `block_lines`, `windows` required at the top), walked from the registry (every registered contrast
  id must have a fill row and the verdict's rows: the adapter's own `results_fill_contrast_census_mismatch` enforces
  that census on the producer side). That is answer 4's structure.

**F2 (MEDIUM). Arm-gate and resolution rows exist only if the verdict prints the key.** `compare_arms` `:1137`
`if "arm_gates" in floor:` and `:1146` `if "resolutions" in floor:`. The engine requires both for every v3 contrast
(`artifact.py:233-242`, `:2233-2240`, exactly two gates `:2420`), so a verdict and fill without them are a wrong
producer, not a sound one. `probes.out` S1: `arm_gates` dropped from both copies `exit=0`, 0 `arm/` rows;
`resolutions` dropped from both `exit=0`, the `transport_rule_id` row gone (the only comparison of that registered
word); dropped from the fill alone `exit=0` (S1.c); dropped from the verdict alone `exit=2 no_row` (S1.b);
relabelled `exit=2` (S1.d, S1.e); emptied lists `exit=1` (S1.h, S1.i); wrong words with both present `exit=2`
(S1.f, S1.g). Fix: build both row sets unconditionally (ARMS is the key universe already) and require the keys
in the fill (F1).

**F3 (MEDIUM). Producer-unconditional disclosure lines are not paired with any recompute item, so a whole line
drops with exit 0.** RC-CMP-8 paired `reported_cell` (`our_cell_lines` `:1534`) and the two window claim lines;
`our_contrast_lines` (`:1547`) pairs four contrast words. `probes.out` S1 (every line of a word removed): exit 0 for
`primary_contrast`, `contrast_interval`, `decision_floor` (`disclosures.py:482,537,546`, per contrast),
`attribution_floor` (`:429`, per cell), `floors/kept_units` (`:721`), `dominance_branch`, `dominance_ratio`
(`:1157-1159`), `sensitivity_bmax`, `sensitivity_window`, `sensitivity_reported`, `sensitivity_floor`,
`sensitivity_contrast`, `sensitivity_boundary` (`:1245-1267`); exit 1 for `reported_cell`, `battery_assist_cell`,
`floor_composition`, `magnitude_ratio`, `magnitude_per_token`, `loo_counts`, `loo_magnitude`, `below_screen_bound`,
`neg8_screen`, `neg8_allowance`, `reference_counts`, `corpus_counts`. The values of the exit-0 words are compared
from their source artifacts (verdicts, projection, closeout, record), so nothing wrong passes; the disclosure the
reader sees is silent. Fix: add the 13 words to `our_cell_lines` / `our_contrast_lines` and a block-line map keyed
on the recompute's items (contrasts, reported cells, dominance ratios, sensitivity rows, `PACKS` for the windows).

**F4 (LOW). The projection's refused-p42 row exists only if L9 prints a refused p42 cell.** `:1378`
`if refused is not None:`. S1.l `refused_cells` key dropped `exit=0`, S1.m relabelled to the decode cell id
`exit=0`, S1.n an object `exit=0` (row absent each time); S1.k a wrong word `exit=2`. The p42 word is also compared
from the extraction report (`:993`) and the sensitivity record (`:1483`), so the status cannot be wrong unseen.
Fix: `c.exact` unconditionally with `refused_p42` None on absence.

**F5 (LOW). A conditional key is never required, even when the status word the producer keys it on is printed.**
`CONDITIONAL_KEYS` (`:679`) is subtracted from `REQUIRED_KEYS` regardless of the line's status. `sweep.out`:
`block_lines/8/ratio`, `numerator_j`, `denominator_j` deleted from a `complete` dominance ratio line `exit=0`
(`disclosures.py:1148-1154` prints them iff `complete`). Fix: key the set on the status word as `sensitivity_row`
does (`:724`).

**F6 (LOW, carried).** `Custody.step_ok` (`:338`) still has no caller.

## Answers

**1. Sweep.** `rc-cmp8-fable-rev/row_constructors.md` lists all 35 constructors (every `c.pairs`, `c.exact`,
`c.numeric` site) with the key source of each side. Registered or recompute-derived: 25. Output-derived existence:
rows 10, 11 (F2) and 20 (F4); each probed by drop and relabel above. Union pairs whose sides are L9-keyed ∪
recompute (rows 2, 6, 7, 9, 12, 15, 19, 24): a one-sided drop is DISAGREE in every case executed, a joint drop is
invisible, and for contrasts, reported cells, floor cells and loo blocks the registry holds a table that is not a
side. Coverage (row 35) is output-derived by design and is F1.

**2. RC-CMP-7 probes.** `probes.out` S2: G7.0-G7.g identical to `c372211bf` (G7.a, c, d, e, f exit 1; G7.b, b2
exit 0, the declared joint-drop residual; G7.b3 exit 1; G7.g 281 routing DISAGREEs, 280 both None). F2.a exit 0;
F2.b exit 2; **F2.c exit 1, F2.d exit 1, F2.e exit 1** (RC-CMP-7 F1 closed); F2.f exit 2, F2.f2 exit 0;
**F2.g exit 2 for both words** (RC-CMP-7 F2 closed). Relabel sweep: 70 gate-passing relabels, 40 exit 0, all bare
sentences (`order`, `sensitivity_boundary` into other bare words); the three `stored_status` → `reported_cell`
exits are gone. RC-CMP-8's table is confirmed.

**3. Over-refusal.** None found. `probes.out` S3: `with_sensitivity(widened=True)` and `(False)` exit 0, 19 sensitivity
relation rows, 0 non-AGREE. `RequiredKeyTests` 6 OK (conditional keys absent pass the gate). S3.b (refused dominance
ratios without ratio keys) and S3.c (`battery_assist_contrast` n=0 without estimates) pass the gate; their exits
(2 and 1) are RC-CMP-8 OPEN ISSUE 2's declared value-row over-refusals (`None` against `None`), not the gate.
`census.out`: each of the 25 `REQUIRED_KEYS` entries is a subset of the producer's unconditional `_item` keys
(literal kwargs plus the resolved `**` builders, lines cited); no required key is conditional in the producer.
`SENSITIVITY_KEYS` match `sensitivity.py:276-279,292,302,320,344`; `FILL_KEYS` match `_EVALUATION_KEYS`,
`_MULTIPLICITY_EVIDENCE_KEYS`, `_CONTRAST_SAMPLING_KEYS`, `_LOO_KEYS`, `_LOO_ROW_KEYS` (`artifact.py:209,279,287-305`)
and `dry_run.py:615,1173` for `claim_usable`. DECISION 2 (`confirmatory`) and DECISION 3 (`loo_status`: `complete`
iff rows, `not_run` otherwise, `__init__.py:1707-1709`) read correctly.

**4. Closed?** No. The current structure is "walk what L9 printed; each printed leaf must bind an agreeing row;
each printed line must carry its top-level keys". RC-CMP-8 closed every *printed* word (answer 2) and three line
kinds by pairing. What remains open is exactly omission: F1 (numbers and objects one level down, whole sections),
F2 and F4 (row sets gated on a printed key), F3 (lines not paired). Each fix above is the same move, a required
path or key set taken from the producer and walked from a registered or recompute key, so the needed structure
is the recompute-driven walk: for each registered contrast (`registry.tables["contrast"]`), each recompute
computed cell and ratio, and each `PACKS` window, require the producer's unconditional paths in the fill, the
verdicts, the disclosure and the record, then bind them. The per-leaf coverage stays as the second direction
(nothing printed may be uncovered). Evidence that the gap is material: `sweep.out` fill `gamma` → exit 0.

## Evidence (`.codex-report/rc-cmp8-fable-rev/`)

- `suite.out`: the brief's command at `0d317afd4`, `Ran 330 tests` / `OK (skipped=18)` / exit 0.
- `probes.py`, `probes.out`: S1 (F2, F4 drop and relabel; whole-line drops), S2 (RC-CMP-7 probes), S3 (over-refusal).
- `sweep.py`, `sweep.out`: 1933 single deletions over every L9 input and the recompute; `classify.py`, `classify.out`:
  the 831 exit-0 deletions split into declared exemptions (534) and producer-unconditional claim values (297, a few
  identity fields misfiled among them).
- `census.py`, `census.out`: `REQUIRED_KEYS` against the producer's `_item` calls (AST, `origin/main`).
- `row_constructors.md`: answer 1's table.

## Pruning tally (gate policy rule 9)

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| suite at `0d317afd4` | yes | no | no | `suite.out`, 330 OK |
| RC-CMP-7 probes re-run (G7, F2, relabel sweep) | yes | no | no (all RC-CMP-8 claims confirmed) | `probes.out` S2 |
| output-derived constructors (drop, relabel) | yes | no | yes (F2, F4: exit 0 with a row missing) | `probes.out` S1 |
| whole-line drop per word | yes | no | yes (F3: 13 words exit 0) | `probes.out` S1 |
| single-leaf deletion sweep | yes | yes (fill `estimate`, disclosure `estimator/estimate` absent, exit 0: F1) | yes | `sweep.out`, `classify.out` |
| producer-shaped over-refusal (sensitivity fixture, conditional keys, census) | yes | no | no | `probes.out` S3, `census.out` |
