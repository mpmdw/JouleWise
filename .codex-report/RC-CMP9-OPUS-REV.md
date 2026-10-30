VERDICT: ACCEPT_WITH_FIXES

# RC-CMP9-OPUS-REV: blocking delta review of RC-CMP-9 (0d317afd4..f9f86869e)

Branch `review/2026-10-30-rc-cmp9-opus-rev` from `f9f86869e`. Synthetic fixtures only; no block-5/6/BYTES data
opened or searched for. Producers read as text from `origin/main` (2bc739d2e). `python3.13`,
`TMPDIR=/tmp/rcnine_opus_tmp`. Evidence in `.codex-report/rc-cmp9-opus-rev/` (`*.out`, `sweep.md`, `probe_cmp9.py`).

The structure holds. The table is a function of the pinned registry alone, every registered item is required on
both sides before any family compares, and no output path reaches the table. Every probe the RC-CMP-8 REJECT rested
on now exits non-zero. One undeclared instance of the class remains: leave-one-out rows at a kept n of 1 or 2 (F1).
It is a small fix plus the ruling the report already asks for (NEEDS_RULING 5).

## Findings (ranked)

**F1 (blocking fix; class instance) — leave-one-out rows at a kept n of 1 or 2: sound output refuses, the
rows-dropped output exits 0.**
- The engine prints one row per kept block from n ≥ 1, with at most 10 registered blocks
  (`origin/main joulewise/analysis_engine/__init__.py:1443` `_loo_family`). The table expects rows only from
  n ≥ `LOO_MIN` = 3 (`scripts/compare_b5_recompute.py:1160`). The row counts are checked only from 3 (`:1978`).
- `loo_counts/count` is compared with `len(ours.contrasts[cid].loo)` (`:2450-2452`). That reference is what the
  recompute printed, not the registered rule. Below 3 the recompute prints no rows, so a count of 0 agrees.
- `probe_cmp9.py n2` (`cmp9_n2.out`; decode contrast kept n = 2; every copy of n, kept ids, kept_units edited consistently):
  ```
  N2 sound (engine rows printed, recompute none) widened=True: exit=2 err='refused=step11_unmapped_fill' fails=31
  N2 both L9 rows dropped, loo_counts 0, status complete widened=True: exit=0 err='' fails=0
  N2 both L9 rows dropped, loo_counts left 2 widened=True: exit=2 ... fails=1 [('count', '.../loo_counts/count')]
  ```
  The unwidened window gives the same three results.
- So `loo/status = complete` with zero rows and "leave-one-out rows 0" passes. OPEN ISSUES 3 and NEEDS_RULING 5
  describe only the over-refusal, not this exit-0 path.
- Fix (small, no ruling needed):
  - For 1 ≤ n ≤ `LOO_REQUIRED_MAX` registered blocks, bind the L9 row count (`loo/l9_rows`) and `loo_counts/count`
    to the kept n (`:1978`, `:2452`), not to the recompute's printed rows.
  - Make `loo_block_kept` require the rows from n ≥ 1 on L9's side.
  - After this both cases refuse: the over-refusal stays, and the safe side is the one that holds. Whether the
    recompute should compute rows at n of 1 or 2 is Ed's ruling (NEEDS_RULING 5).

**F2 (low; report accuracy, not a claim value)** — producer-unconditional nested keys are missing from the table,
and a drop of each exits 0 (`drop.out`, 718 of 4075 exit 0).
- The keys:
  - `bundle_blocks/included_bundle_ids`;
  - each block's `bundle_a_id`, `bundle_b_id` and `reason_codes`, and `included` on a removed block;
  - `randomization_check/{status,reason,n_blocks,exact_two_sided_p,rejects}`;
  - `estimator/repeat_point_CI95/{lower,upper}`;
  - `estimator/variance_contributions/*`.
- `artifact.py` validates each of them (origin/main `:1858`, `:2134`, `:2172`).
- They are all declared value exemptions. A kept block's `included` is bound (`kept_quads`; `cmp9_extra.out`:
  exit 2).
- But the report's residue calls `repeat_point_CI95` and `variance_contributions` "verdict-only … not in any step-11
  output". They are also printed in the disclosure's `primary_contrast/estimator` copy, and a drop there exits 0
  too (`drop.out`).
- Either require these nested keys, or correct the residue text and A1's "every literal key … required".

**F3 (declared; for Ed)** — the remaining output-keyed universes, unchanged and correctly declared:
- the whole-machine `machine_member` and `machine_summary` lines (`:2587`, `:2642`, `TABLE_CONDITIONAL_LINES`
  `:1047`), which pass only on a three-way omission (NEEDS_RULING 2);
- `flag_count` and `machine_absent` (Fable's whole-line drops: exit 0 only for these two);
- `battery_temperature_sentence`;
- the history lines and `causes`;
- the G7 run universe (`probe_cmp8` / Fable S2 G7.b and G7.b2 exit 0; G7.b3 exit 1).

None of them carries a claim number or claim word, except the machine rho, which is a descriptive cross-check.

## Answers

**(1) Sweep.**
- `rc-cmp9-opus-rev/sweep.md` lists the 30 `c.pairs` constructors and the 29 table families with their key sources.
- Each output-derived universe is now backed by a registered entry, with three exceptions: loo rows at kept n of
  1 or 2 (F1), the machine lines (F3) and G7 (F3).
- Drop probes:
  - `confirm.out`: 58 cases, 0 exit 0.
  - `joint2.out`: 10 of 10 non-zero.
  - `loo.out`: only the control exits 0.
- Relabels:
  - `relabel_ids.out`: `identity relabels tried: 4081; exit 0: 0`.
  - A text-routed R/R_cm swap gives exit 2 once the R and R_cm values differ (`cmp9_ratio.out`). In the base the
    two values are equal, so the swap changes no number.

**(2) Completeness.** I derived this from `produce_disclosures`, `_energy_lines`, `_kept_lines`, `_monitor_lines`,
`_reference_lines`, `_ruling_lines`, `_closeout_lines`, `sensitivity_pass`, `adapt_claim_verdicts`, the
`artifact.py` key sets and `_loo_family`.
- Every unconditional line kind is an entry (each drop exits non-zero: Fable whole-line, `cmp9_extra.out`):
  - the 21 window lines plus the 2 tripwires, per pack; `machine_boundary` prints on both meter branches;
  - the 13 fixed sentences;
  - `harvest_once`, `sensitivity_*` and `dominance_*`;
  - per reported cell: `reported_cell`, `battery_assist_cell`, `attribution_floor`, `kept_units`;
  - `kept_units` per extraction cell, including p42, and per contrast;
  - the 8 per-contrast lines.
- Conditional lines match the producer's conditions:
  - `cross_window`: target cell and one phase contrast with n ≥ 2;
  - `floor_composition`: guarded floor not None;
  - `floor_drift_ownership`: floors exist;
  - magnitude estimates: computable.
- The nested keys of the fill (24), the verdict, the sensitivity record and the line keys match the pinned
  literals. ProducerPinTests ran: 6 ok, none skipped.
- Missing: the loo rows at n of 1 or 2 (F1), the nested engine keys in F2, and `flag_count` (it follows the flag
  catalog's RESTRICTED codes unconditionally; the catalog is not a registered source, NEEDS_RULING 4).

**(3) Numbers.** The report's numbers reproduce at this head.
- `probe_cmp8.py`:
  - confirm: 0 exit 0;
  - joint2: all non-zero;
  - loo: only the control exits 0;
  - relabel: 4081 tried, 0 exit 0;
  - drop: 4075 tried, 718 exit 0, all text/label/restricted, declared engine internals (F2), kept-units identity
    and harvest fields, `causes`, `flag_count` and `machine_absent`;
  - ours: 1308 tried, 420 exit 0, all unselected reference and corpus members, assist strata, `direction`,
    GAMMA `claim_usable` and `program_sha256`;
  - joint: 14 same-key joint drops (L9 and recompute), 0 exit 0 (`joint.out`; the probe's path split was fixed for recompute keys containing `/`).
- Fable's `sweep.py`: `deletions tried: 4982; exits: {1: 1606, 2: 2641, 0: 735}`. `classify.py`: 724 declared and
  11 producer-unconditional, the same 11 the report lists.
- Fable's `probes.py`:
  - S1.a, S1.c, S1.l, S1.m and S1.n exit 1;
  - the whole-line drop exits 0 only for `flag_count` and `machine_absent`;
  - S2 F2.c gives 5 routing rows;
  - S3.a exits 0 on both windows; S3.b exits 2 and S3.c exits 1 (OPEN ISSUES 2).

**(4) Over-refusal.**
- The sound producer-complete window passes, widened and unwidened, with every row AGREE (`fable_probes.out`
  S3.a; suite `OverRefusalTests`).
- Condition-false items pass: the not-kept block 1 loo rows and the refused variants (`test_conditional_items_…`).
- Known over-refusals, all on the safe side:
  - a refused non-p42 cell (OPEN ISSUES 1);
  - a refused ratio and a not-computable assist contrast (OPEN ISSUES 2, S3.b and S3.c);
  - kept n of 1 or 2 (F1).
- `REGISTERED_SOURCES` is closed:
  - `expected_checks` reads only `registry.tables` and `registry.blocks`;
  - `Registry` reads only pinned files under `configs/campaigns` (`REGISTRY_PINS`, `:395`);
  - outputs enter only `condition_holds` (`:1123`), and only to add an expectation, because either side's word
    switches an item on.

**(5) Other exit-0-with-wrong-claim paths.** None found beyond F1.
- Text-routed ratio identity is safe when the values differ.
- Dropping `included` from a kept block exits 2.
- `resolve` treats a duplicated selector as absent.
- Unclosed line words (`removed_unit`, `load_correlated_*`, history) are not compared claims.

**Suite:** `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
gives `Ran 362 tests in 433.294s`, `OK (skipped=18)`, exit 0 (`suite.out`).

**Defect class:** one undeclared instance remains: leave-one-out rows, and the `loo_counts` reference, at a kept n
of 1 or 2 (F1). The others are the declared machine-line, flag-catalog and G7 universes, which go to Ed.
