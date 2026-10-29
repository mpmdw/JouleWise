VERDICT: REJECT

# RC-CMP8-OPUS-REV: delta review of RC-CMP-8 (c372211bf..0d317afd4)

This is one of two parallel blocking delta reviews (gate policy rule 3).
- Branch: `review/2026-10-29-rc-cmp8-opus-rev`, cut from `0d317afd4`.
- Data: synthetic fixtures only. No real block-5, block-6 or BYTES data was opened or searched for.
- Environment: `python3.13`, with `TMPDIR=/tmp/rcopus_eight_tmp`, which is outside the checkout and has no float-like
  token.
- Producers on `origin/main` were read as text only: `b5_analysis/disclosures.py` and `sensitivity.py`.
- Evidence: everything is under `rc-cmp8-opus-rev/`. The sweep table is `sweep.md`.

**Why REJECT.**
- Every per-finding closure RC-CMP-8 claims reproduces at this head (answer 2).
- The new required keys do not over-refuse (answer 3).
- But the defect class this round was meant to close is still open. The fill and disclosure checks exist only per
  item L9 printed. The required-key gate only checks the keys of items that are present.
- As a result, 22 single-output drops of claim lines or claim rows, each of which the producer prints
  unconditionally, exit 0. Two joint drops of a registered contrast and of a registered reported cell exit 0 too.
- The fix is to key these families on registered universes. That is a structural change across about 10 families,
  so it needs a new round and a new review, not a local patch.

## Suite

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
gives `Ran 330 tests in 165.663s` / `OK (skipped=18)` / exit 0 (`suite.out`).

## Findings, ranked

1. **BLOCKING: a claim line or claim row that L9 omits is never checked, although the producer always prints it**
   (`confirm.out`, `drop_triage.out`).
   - The base is producer-shaped (`with_neg8 + with_references + with_sensitivity`). Each case below exits
     `0 ''` with 0 failing rows, on both the widened and the unwidened window.
   - **Fill** (`gate_fill`, `scripts/compare_b5_recompute.py:745`). These iterate only the rows present, and
     `FILL_KEYS` (:708) lists claim words only.
     - Removed whole: the decode contrast row, all of `gamma/contrasts`, and `gamma` itself.
     - Removed from a present contrast: its `estimate`, `decision_interval`, `floor`,
       `floor/claim_floor_rule` and `conditions/difference_orientation`. The last two are words this round says
       it compares.
     - The fill's leave-one-out row removed while the verdict keeps it (`loo.out`). That drops the influence
       triggers this round compares.
   - **Disclosure: lines that nothing pairs.** `CELL_LINES`/`CONTRAST_LINES` (:1530) leave these out, and
     `REQUIRED_KEYS` (:690) applies only to lines that are present. Each line below exits 0 when removed:
     - `primary_contrast`, `contrast_interval` and `decision_floor`. The producer prints each one per verdict
       contrast (`disclosures.py:482,537,546`).
     - `attribution_floor`, printed per projection cell (:429).
     - `dominance_branch` (:1159) and `dominance_ratio` (:1157).
     - `sensitivity_bmax`, and `sensitivity_window` for each pack (:1244-1251).
     - `sensitivity_reported`, `sensitivity_floor` and `sensitivity_contrast`, printed per record row (:1266).
     - The whole `sensitivity` copy (:1303, unconditional), or just its `contrasts`.
     - All of `block_lines`.
   - **Disclosure: a key missing inside a present line.** Removing `primary_contrast`'s `estimator/estimate` also
     exits 0. Only the top-level keys are required.
   - Some of these hide real claims. On a widened window, dropping the `sensitivity_window` line removes "values
     differ from primary". Flipping the same line's `widened` word exits 2, so the comparator checks the word only
     when the line exists.
   - **Joint drops** (`joint.out`, `joint2`). Each item below was removed from every L9 output and from the
     recompute. Each exits 0:
     - the registered primary decode contrast (verdict, fill, disclosure lines, sensitivity rows, recompute);
     - the registered ALPHA decode reported cell;
     - the leave-one-out row, with both sides then printing `not_run`.
   - These pass because:
     - `c.pairs("contrast/", l9_rows, mine_all)` (:1172) and `c.pairs("reported/…", l9_cells, mine_cells)` (:1353)
       take their universe from the two outputs;
     - `loo_status` (:1269) reads the word from whether the recompute printed rows.
   - Controls exit non-zero: `reported_cell` line removed (exit 1), `magnitude_per_token` removed (1), `neg8_screen`
     removed (1).
   - Fix:
     - Give each family a registered universe, and pair against it:
       - registered contrasts (`registry.blocks`/manifest);
       - registered reported cells (`registry.families`);
       - PACKS for `sensitivity_window`;
       - one `sensitivity_bmax`, one `dominance_branch` and one `sensitivity` record;
       - the sensitivity record's rows for the block-line copies.
     - Require the fill's contrast set to equal the registered set, and its loo rows to equal the verdict's.
     - Extend the required keys to the nested unconditional keys: `estimator/*` and `decision_interval/*`, and the
       fill's numeric and definition keys.
     - Derive `loo_status`'s `not_run` from the registered and kept `n`, not from the recompute's row count.

2. **LOW: the contrast-to-floor-cell relation is exempt as identity although the registry fixes it**
   (`relabel_ids.out`). Each relabel below exits 0:
   - the fill's `floor_source_cell_ids/*` and `floor/floor_row_ids/*`, and the verdict's `floor/floor_row_ids/*`,
     swapped from decode floors to prefill floors (IDENTITY rule, :2182-2183);
   - the sensitivity record's and the disclosure copy's `contrasts/*/floor_cell_ids`, reversed (:2187-2188).

   Only `resolutions/*/source_cell_ids` is bound (:1156). These leaves print which floor gates which contrast, and
   the manifest's `floor_selector` determines that. Fix: compare them against the registered source cells, as
   :1156 already does.

3. **LOW, informational:**
   - The p42 row at `:1379` exists only if L9 prints `refused_cells`. Dropping `refused_cells` exits 0, but :993
     compares the same status.
   - The kept-units record's own `pack`, a kept unit's `cell_id`, and an excluded block's `block_id` can be relabelled
     with exit 0. These are identity fields, and the file name and the kept set carry them.

## Answers

**(1) Sweep.**
- `sweep.md` lists all 36 constructor sites with their key source and probe exit codes.
- Registered: 13 sites. The new per-pack window claim lines (:1676) are registered, and they are the only
  per-registered-key pairing this round added.
- Output-derived, but a drop on either side is caught by the other side: most `c.pairs` sites (L9 drop exits 1 or
  2).
- Output-derived where an exit-0 drop leaves a claim missing:
  - `run/` (A4/A5: declared, and bound by A5b);
  - `contrast/`, `loo/`, `loo_status`, `reported/` and the sensitivity contrast/reported pairs (joint);
  - the p42 row at :1379 (redundant);
  - `coverage()`'s per-leaf binding and the `require` gates. These are the 22 L9-only drops in finding 1.
- Relabels: 623 identity relabels were tried and 64 exit 0. All 64 are finding 2 or finding 3.

**(2) `probe_cmp7.py` at this head** (`cmp7_*.out`).

| Case | Result | RC-CMP-8 claim holds? |
|---|---|---|
| C1 | exit 2 | yes |
| C3 | exit 2 | yes |
| C3b | exit 2 | yes |
| C4 | exit 2 | yes |
| C6 | exit 2 | yes |
| C5 (`reason_codes` emptied) | exit 0 | yes, declared |
| K5, K6, K7, K8 | exit 2 `required_key_absent:…` | yes |
| K9 | exit 1 | yes |
| K1-K4, K11, K12 | exit 2 | yes |
| K10 | exit 0 | no-op: both windows carry an identical line (`b_op_s 0.0375`, `below False`) |
| G7 A0-A14 | as at c372211bf | yes |
| A4, A5 | exit 0 | yes, declared residual |
| A5b | exit 1 | yes |
| Relabel sweep | 4067 tried, 13 exit 0, all keyless bare sentences (`order`→fixed sentence, `sensitivity_boundary`→`superseded_history`) | yes |
| Words | 141 exit-0 mutations, the classes RC-CMP-8 lists | yes |

**(3) Over-refusal.**
- Each `REQUIRED_KEYS` / `SENSITIVITY_KEYS` / `FILL_KEYS` entry was checked against the producer:
  - `disclosures.py`: `_cell_values`, `_paired_values`, `_item` calls at :386-546, :657, :689, :952-1022, :1068,
    :1100, :1157-1162, :1245-1266;
  - `sensitivity.py:275-346`.
- Every listed key is written unconditionally. The ones held out as conditional (dominance_ratio values,
  battery_assist_contrast estimates, magnitude_ratio values, machine_summary statistics) are exactly the conditional
  ones.
- The manifest words resolve from the sealed manifest: both contrasts are primary, positive, confirmatory, with the
  `abba_block_arm_mean_difference_t_v1` estimator. Each registration has 10 blocks, so `loo_status` never gives
  `None` there.
- The widened and unwidened F4 fixtures exit `0 ''`. So do the conditional-key-absent lines
  (`test_producer_lines_with_conditional_keys_absent_pass_the_gate`). The NEG-8 `source` rows agree on the fixture.
- One structural note: `gate_sensitivity` runs on the disclosure's copy only (:782). L9's standalone sensitivity
  record is not key-gated. Its compared leaves still turn a missing value into DISAGREE.

**(4) Still exempt but determinable:**
- the floor-cell relation in finding 2;
- the `characterization/funded` and `characterization/run` constants (:2016; always `False`; any boolean passes);
- the NEEDS_RULING 2 and 3 words (floor-resolution statuses, flag family and blinding), which the lead must rule on.
  Their stated reasons hold.

`reason_codes`, harvest and history words, and `restricted` stay as declared.
