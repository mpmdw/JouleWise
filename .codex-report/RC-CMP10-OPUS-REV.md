VERDICT: ACCEPT_WITH_FIXES

# RC-CMP10-OPUS-REV: delta review of RC-CMP-10 (f9f86869e..1affc4208, excluding the merge ab4029f7b)

Seat RC-CMP10-OPUS-REV. Branch `review/2026-10-30-rc-cmp10-opus-rev`, from `1affc4208`. Synthetic data only: no
real block-5, block-6 or BYTES data was opened or searched for. `python3.13`, `TMPDIR=/tmp/rcopus_rev_tmp`
(outside the checkout, no float-like token). The probes and their outputs are in `.codex-report/rc-cmp10-opus-rev/`.

Suite: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
gives `Ran 393 tests in 577.525s`, `OK (skipped=18)`, exit 0 (`suite.out`).

The verdict is ACCEPT_WITH_FIXES because of F1. It is a real false pass. The fix is one line, and I tested it
(below). Every other RC-CMP-9 closure I re-probed holds.

## Findings (ranked)

**F1 (MEDIUM, required): FS3 lets a wrong relation word exit 0 when its values are exactly equal.**
- Where: `scripts/compare_b5_recompute.py:280` (`atom`: `within` is true whenever |number − threshold| ≤ bar),
  with `:239-268` (`word`) and `relation_words` at `:2984`.
- How it happens: when a value is unchanged, sensitivity − primary is exactly 0 on both sides, so the test is
  always "within". An undetermined row checks only the numbers, never the word.
- Why the word is still certain: the producer prints these words by exact equality.
  - `sensitivity.py:303`: `equals_primary = _same(before, after)`.
  - `:304`, `:321`, `:346`: `not_below_primary` is `>=`.
  - `:279`: `widened = b_sens > b_fiducial`.
  - Unwidened, `_at_primary_bound` (`:62`) raises unless the values are identical, so `equals_primary=False`
    cannot be printed there.
- Probe: `probe_cmp10.py eq` → `eq.out`. Each word is set wrong in every copy (L9's record, the disclosure copy and
  the block line):

  | Case | Exit at 1affc4208 |
  |---|---|
  | E1: floor `equals_primary` False, unwidened | **0** |
  | E2: every reported cell's `equals_primary` False | **0** |
  | E3: floor `not_below_primary` False (difference exactly 0) | **0** |
  | E4: contrast `not_below_primary` False (row `within_bar_undetermined`, AGREE) | **0** |
  | E6: window `widened` True with b_sens == b_op | **0** |
  | E7: `equals_primary: "banana"` (not a boolean) | **0** |
  | E8: widened window, unchanged beta cells' `equals_primary` False | **0** |
  | E5: `outcome_equals_primary` False (the outcome tests are decided) | 2 (caught) |
  | E9: control, a decided difference | 2 (caught) |

- Fix (answers focus 1): yes, "exact equality on both sides counts as decided" closes it. Change `:280` to:
  `within = known and (...) and not (same(l9, l9_threshold) and ours == threshold)`.
  - With that line patched in (mock in `eq.out`, real patch in a scratch worktree), E1-E4 and E6-E8 all exit 2.
  - The over-refusal stays closed: the full-size b10 ulp flip (U1/U2) and an exactly-0 L9 value against a ±1e-16
    recompute value (U3/U4) still exit 0 with `within_bar_undetermined`.
  - The reason: when exactly one side is exactly 0, the test stays undetermined, so an ulp difference never
    decides a word.
- Tests to update with the fix (real patch, `test_rc_cmp10`, `test_rc_cmp8` and `test_comparator`: 86 tests, 2
  failures, both expected):
  - `test_rc_cmp10.WithinBarTests.test_relation_words_inside_the_bar`: it asserts that some unwidened
    `equals_primary` row is undetermined. That row is now decided and AGREE.
  - `test_comparator.test_planted_contrast`: it expects `{"contrast_j": 3, "outcome_word": 1}`. It now gets
    `{"contrast_j": 3}`. The `not_below_primary` word is now decided and correct (True = True), and the moved D is
    still caught by the three `contrast_j` rows.
  - `test_rc_cmp8` passes unchanged.
- Edge case: `_same` is a canonical digest, so it tells −0.0 from 0.0 and 1 from 1.0. A printed −0.0 against 0.0
  would therefore be a decided True against L9's False, an over-refusal. That is only possible widened, and it
  fails on the safe side.

**F2 (LOW-MEDIUM; for Ed's ruling on NEEDS_RULING 1): any closed-set p42 code passes when printed identically
everywhere.**
- Where: `:2953` (`refused_code`), with the set at `:2911`.
- Probe: `probe_cmp10.py p42` → `p42.out`. Swapping the issuer's `paper_reported_energy_record_invalid` for each of
  the other 32 closed codes in every copy exits 0 for all 32.
- Some of those codes are contradicted by what the comparator already knows:
  - `paper_reported_energy_kept_units_below_minimum`: the recompute's own word for that cell is `p42`, not
    `below_minimum`, and the comparator maps that code elsewhere.
  - `paper_reported_energy_whole_window_allowance_unrecorded`: `paper_reported_energy_issuer.py:162` raises it for
    every cell of a pack when `context` is absent, and the other cells of this pack are computed.
- Minimum fix: exclude the codes these facts contradict for a p42 cell. The stricter option is to pin the code
  `producer_fixtures.p42_refusal_code()` derives.

**F3 (LOW): two by-construction literals are unpinned.**
- `bound_independent_values_equal_primary` against `True` (`:2829`) and `mean_and_half_width_equal_primary` against
  `True` (`:2889`).
- The producer prints both as literal `True` (`sensitivity.py:302`, `:344`).
- No `LiteralPinTests` or `ProducerPinTests` test names them. (grep of `test_rc_cmp8/9/10`: they appear only as
  flipped fixture words.)

**F4 (LOW): a falsy direction counts as `"none"`.**
- Where: `:2237`. `evaluation.get("direction") or "none"` maps `False`, `""`, `0` and `[]` to `"none"`. `l9_raw` is
  recorded but not compared.
- Probe: `probe_cmp10.py direction` → `direction.out`. D1-D4 all exit 0. The producer prints `None`
  (`claims.py:414`).
- Fix: compare `"none"` only when the printed value is `None`.

**F5 (LOW): an undetermined trigger list accepts a duplicate.**
- Probe: `probe_cmp10.py garbage` → `garbage.out`. Inside the b10 bar, L9 printing
  `["estimate_sign","estimate_sign"]` exits 0. A non-word (`banana`) or a decided word (`outcome`) is still caught by
  the positional rows (exit 2).
- The F1 fix does not touch this. A cheap fix: an undetermined row also requires L9's word to be a member of its
  producer vocabulary, with no repeats.

## Answers

**1. Within-bar rule.** Yes: see F1, with the probe outputs and the validated one-line fix. The fix does not bring
back the ulp over-refusal: U1-U4 exit 0 with the fix applied.

**2. Class sweep.**
- New table entries and row constructors: I agree with the report's key-source list. There is no new existence
  derived from the recompute's output.
- History entries: probe `probe_cmp10.py hist` → `hist.out`, on the producer's lines for the 6-attempt `HISTORY`
  index. Every line is dropped, every key deleted, and every scalar relabelled: 356 mutations, exits
  `{1: 73, 0: 128, 2: 155}`.
  - Every line drop and every key deletion except `restricted`, `label` and `text` is non-zero.
  - The relabels of `pack`, `plan_id`, `attempt`, `verdict`, `cause_key`, `superseded`, `causes/*`, `count` and
    `redraw_cycles` are all non-zero.
  - The exit-0 cases fall in the declared classes only: `text`, `label` and `restricted`, plus
    `attempt_history/{collected,planned}` (STRUCTURE_NUMBER, `:3748`) and `catalog_path` (HARVEST_WORDS,
    `:3753`).
- Index binding: the index is bound by digest to L9's record (`test_the_index_is_bound_to_the_record` passes).
- `g10` without a request and `reharvest_account` stay conditional on L9's own line (NEEDS_RULING 3). They are
  declared and carry no compared claim; I accept that.
- FS2 p42 rule: yes, it is a false-pass route for a wrong code (F2).
- Fable's `sweep.py` + `classify.py` rerun at this head:
  - `deletions tried: 5035; exits: {1: 1673, 2: 2719, 0: 643}`, **0 UNDECLARED**
    (`fable_sweep.out`, `fable_classify.out`).
  - This matches the report.

**3. Pinned literals.** I listed every `c.exact` and `c.word` call that has a literal on the expected side (AST
scan). All of them are pinned or declared in the report, except the two `True` literals in F3. `"none"` and
`"extractable"` are declared unpinned with a reason; F4 shows that `"none"` needs a tighter raw check.

**4. RC-CMP-9 closures (re-probed at this head):**

| Finding | Probe at this head | Result |
|---|---|---|
| Opus F1 (loo rows at a kept n of 1 or 2) | `probe_cmp9.py n2` (`cmp9_n2.out`), both windows | Rows dropped with count 0: exit 2 (was 0). Rows dropped with count 2: exit 1. Sound: exit 2, the declared over-refusal (NEEDS_RULING 2) |
| Opus F2 (required nested keys) | `probe_cmp9.py extra` (`cmp9_extra.out`) | `included_bundle_ids`, `randomization_check`, `repeat_point_CI95` and each block's `included` dropped: exit 1 or 2 (were 0). The only exit-0 cases are the declared `machine_absent` and `flag_count` drops and the R/R_cm text swap |
| Fable F1 (conditional families) | `probes_extra.py` (`fable_probes.out`) | P1, P3, P4, X1, X3, X4, X5 and P13: exit 0. P2.a/b, P3.a/b, P4.a/b: non-zero |
| Fable F2 (verdict sampling words) | same | P6.a 2, P6.b 2, P7.a 1, P7.b 1 |
| Fable F3 (fill precondition) | `LiteralPinTests.test_extended_fill_precondition` | passes in the suite |
| Fable F4 (finalized manifest) | same | P8 exit 2 |

All four Fable findings are confirmed closed. P9.b (`LOAD_LINE`) exits 0 and is declared.
