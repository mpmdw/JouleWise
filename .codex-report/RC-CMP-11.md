STATUS: DONE

# RC-CMP-11: fix round inside the RC-CMP-10 design (both reviews' F1-F5)

Seat RC-CMP-11, branch `lane/2026-10-27-recompute-comparator`, from `1affc4208`; code commit `d97e55d1f`.
Synthetic data only: no real block-5, block-6 or BYTES data was opened or searched for. `python3.13`,
`TMPDIR=/tmp/rccmpeleven_tmp` (outside the checkout, no float-like token). The script still imports no
repository code (`test_no_l9_import` passes). Producers were read as text from `origin/main` (`d77ae428a`, fetched
at the start of the run). Reviews read: `review/2026-10-30-rc-cmp10-opus-rev` (`RC-CMP10-OPUS-REV.md`,
`probe_cmp10.py` and its `.out` files) and `review/2026-10-30-rc-cmp10-fable-rev` (`RC-CMP10-FABLE-REV.md`,
`fs3.py`, `fs3b.py`, `sweep.py`, `classify.py`).

## SUMMARY

- **F1.** `Comparison.atom`: a test whose number and threshold are bit-identical on both sides
  (`l9 == ours and l9_threshold == threshold`) is decided, never `within_bar_undetermined`. The word is then
  compared exactly against the recompute's word, whose tests are the exact relations (`NE`, `GE`, `GT`, `LT`, ...):
  strict words (`widened` as `b_sens != b_op` / `>`, `below` as `<`, `positive`, `exceeds`) are False at equality,
  equality and non-strict words (`equals_primary`, `not_below_primary` as `>=`) are True. Every wrong relation word
  on unchanged values now exits non-zero; the ulp cases (full-size b10 flip, one exactly-0 side) stay undetermined
  and exit 0.
- **F2.** The registered p42 cell's code must be the producer's own, `P42_REFUSAL_CODE =
  "paper_reported_energy_record_invalid"`, pinned to the kernel line that raises it, the issuer lines that set
  `strict_valid` from the p42 precheck, and the issuer's own output (`producer_fixtures.p42_refusal_code()`).
  All 32 other closed codes now exit non-zero.
- **F3.** `mean_and_half_width_equal_primary` and `bound_independent_values_equal_primary` (expected `True`) are
  pinned to the producer's literal `True` (`sensitivity.py:302` and `:344` respectively; the brief had the two line
  numbers swapped) and to the comparator's `True` literal.
- **F4.** L9's direction is `"none"` only when it prints `None`; any other value (False, "", 0, [], a foreign word)
  is compared as printed, and an undetermined direction row also requires a producer direction word
  (`DIRECTION_WORDS`).
- **F5.** Each printed trigger's position row requires a member of the engine's trigger vocabulary
  (`INFLUENCE_TRIGGERS`, pinned) printed once, whether decided or undetermined.
- Suite (the whole directory): `Ran 406 tests`, `OK (skipped=18)`, exit 0 (13 new tests in `test_rc_cmp11.py`).

## Per-finding table

Evidence at the head and the counterfactual at `1affc4208`. "exit" is the comparator's exit (2 = DISAGREE rows /
refusal).

| Finding | Change | Evidence at head | Counterfactual at 1affc4208 |
|---|---|---|---|
| F1 wrong words on identical values | `atom` (`:289`) | Opus `eq` E1-E4, E6-E8: exit 2 each (E5, E9 controls 2); `ExactEqualityTests.test_wrong_words_on_identical_values_refuse` | Opus `eq.out` at 1affc4208: E1-E4, E6-E8 exit 0; in-test mock `atom_before` (the old `within`): each case exits 0 |
| F1 Fable fs3 B (20 negations, 8 wrong) | same | `fs3.out` B: 0 wrong words exit 0 at head (all 20 exit 2) | Fable `fs3.out` at 1affc4208: 8 exit 0 |
| F1 Fable fs3 C (b10 identical, trigger mismatch) | same | `fs3.out` C head: exit 2; `test_identical_b10_trigger_mismatch_refuses` | mock `atom_before`: exit 0 (Fable: exit 0 at 1affc4208) |
| F1 strict claim at equality | same | `test_strict_claim_over_equal_values_fails`: b_op == screen bound, L9 `below=True`: non-zero; `below=False`: 0. E6 (`widened` True at b_sens == b_op): exit 2 | mock `atom_before`: `below=True` exits 0 |
| F1 over-refusal stays closed | same | Opus U1-U4 exit 0, row `within_bar_undetermined`; Fable `fs3.out` C: full-size b10 flip exit 0; `fs3b.out` E: one-ulp-apart exit 0, sound windows 0 undetermined rows; `test_ulp_cases_stay_undetermined` | (unchanged) |
| F1 test expectations | `test_rc_cmp10` `:374` case 2 now 1 (b_op below the bound on both sides decides `below`=True, L9's False disagrees); `test_relation_words_inside_the_bar` asserts no undetermined row; `test_comparator.test_planted_contrast` `{"contrast_j": 3}`; `test_rc_cmp8.test_each_relation_word_flipped_fails` reverted to "every relation-word flip fails" and `test_widened_flipped_fails` runs unwidened again | suite OK; Fable `fs3b.out` F: 15 existing tests under BI2, 0 failures | — |
| F2 p42 code | `P42_REFUSAL_CODE`, `refused_code(..., P42_REFUSAL_CODE)` | Opus `p42`: P0 control exit 0, all 32 swapped codes exit 2; `P42ProducerCodeTests` (pins + 32 subtests); `test_rc_cmp10.test_every_copy_must_print_the_same_member_code` now expects non-zero | Opus `p42.out` at 1affc4208: all 32 exit 0; in-test mock (expected dropped): exit 0 |
| F3 literal pins | test only | `LiteralPinTests.test_by_construction_true_literals` | (pin, no behaviour change) |
| F4 direction | `compare_contrasts` direction row, `DIRECTION_WORDS`, `word(vocabulary=)` | corrected probe: D0 None exit 0; D1 False, D2 "", D3 0, D4 [], D5 "banana", D6 "positive" exit 2; `DirectionTests` | corrected probe at a 1affc4208 worktree: D1-D4 exit 0 (D5, D6: 2); in-test mock (falsy read as none): exit 0 |
| F5 trigger vocabulary/repeats | per-position trigger row | Opus `garbage`: G1 banana, G2 duplicate, G3 outcome: exit 2; `TriggerVocabularyTests` | Opus `garbage.out` at 1affc4208: G2 exit 0; in-test mock (old open-set rule): exit 0 |

Note on Opus `probe_cmp10.py direction`: its D cases were vacuous. `contrast_rows(c)` returns the DECODE rows, and
the probe filtered them for PREFILL, so no row was mutated. D1-D4 exiting 0 at 1affc4208 was the control,
not the finding. I wrote a corrected probe (`contrast_rows(c, PREFILL)`) and ran it at both commits (table above).
The finding is still real: at 1affc4208 the corrected D1-D4 exit 0.

## Verification

- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute
  -t .` at `d97e55d1f`: `Ran 406 tests in 566.235s`, `OK (skipped=18)`, exit 0.
- Opus `probe_cmp10.py` at head: `eq` (above), `p42` (32 of 32 exit 2), `garbage` (3 of 3 exit 2), `direction`
  (vacuous, see note; corrected probe above).
- Fable `fs3.py`: A 0 undetermined rows on both sound windows; B 0 wrong words exit 0; C head: sound 0/0, b10 flip
  0, b10 identical with a missing trigger 2. `fs3b.py`: E as above; F 15 tests, 0 failures.
- Fable `sweep.py` + `classify.py`: running at `d97e55d1f`; result added in a follow-up commit.
- The lead's full-size window rerun at this head is still to do (laptop).

## FILES CHANGED

- `scripts/compare_b5_recompute.py`: `Comparison.atom` (F1), `Comparison.word` (`vocabulary`, F4), the direction
  row and the per-position trigger rows in `compare_contrasts` (F4, F5), `DIRECTION_WORDS`, `P42_REFUSAL_CODE` and
  the p42 branch of `compare_sensitivity` (F2), module docstring.
- `tests/independent_recompute/test_rc_cmp11.py` (new, 13 tests).
- `tests/independent_recompute/test_rc_cmp10.py`: below-screen-bound case 2, `test_relation_words_inside_the_bar`,
  `test_every_copy_must_print_the_same_member_code` (now non-zero, with the 1affc4208 counterfactual).
- `tests/independent_recompute/test_rc_cmp8.py`: `test_each_relation_word_flipped_fails` reverted to every flip
  failing; `test_widened_flipped_fails` over both windows again.
- `tests/independent_recompute/test_comparator.py`: `test_planted_contrast` expectation.
- `.codex-report/RC-CMP-11.md` (this report).

## DECISIONS I MADE

1. **F1 uses Fable's form** (`l9 == ours and l9_threshold == threshold`), as the brief states, not Opus's
   (`same(l9, l9_threshold) and ours == threshold`). Fable's form also decides identical non-zero differences
   (the b10 identical case C and the below-bound case), which Opus's leaves open. Python `==` treats -0.0 and 0.0 as
   equal, so a ±0 pair is decided too. A decided test reads `test(ours, threshold)`, which is the exact relation.
2. **F2 takes the stricter reading: the full pin.** The issuer's rule (`normalized_rows`: `strict_valid = not problems
   and not precheck['reasons']` with `p42_precheck=True`; `_project_kept_cell`: `strict_valid is not True` raises
   `record_invalid`) gives `record_invalid` for the registered p42 cell, provided the cell reaches the kernel. It
   does reach the kernel when the pack's other cells are computed, which the comparator requires elsewhere. This
   excludes both codes the reviews named (`kept_units_below_minimum`, `whole_window_allowance_unrecorded`). RC-CMP-10's
   report records that the full-size window prints `record_invalid`.
3. **F4: an absent `direction` key is now `None`** (DISAGREE `missing_or_null`) instead of `"none"`. The engine always
   prints the key (`claims.py:414`), and the comment already said "absence is not" a value. I also added a
   vocabulary check on the undetermined path, so a falsy or foreign word inside the bar cannot ride on agreeing
   numbers.
4. **F5 applies to decided positions too.** A decided duplicate was already caught by the whole-list row, so the
   extra check changes no outcome there; one rule for every position is simpler.
5. **F3 line numbers.** The producer prints `mean_and_half_width_equal_primary` at `sensitivity.py:302` and
   `bound_independent_values_equal_primary` at `:344`, the reverse of the brief. The pin tests match the text,
   not the line numbers.

## OPEN ISSUES

- The full-size window must stay exit 0 at this head (lead, laptop). The p42 code pin (F2) and the absent-direction
  rule (F4) are the two changes that could newly refuse a producer output, if the full-size producer prints a
  different p42 code or omits `direction`. RC-CMP-10's report records `record_invalid` for the full-size window.
- `origin/main` was force-updated during this run (`341adaf41...d77ae428a`, seen on fetch). The pins read the
  fetched `d77ae428a`. I did not merge main into the lane.

## NEEDS_RULING

1. **F2 scope (record).** The pin assumes the registered p42 cell always reaches the kernel's row check. A real
   window where a p42 member fails an earlier kernel check (`record_identity_mismatch`, `member_count_invalid`) would
   print another code and refuse here. That is the safe side, but it is an over-refusal if Ed considers such a
   window sound.
2. RC-CMP-10 NEEDS_RULING 2-4 stand unchanged (loo at a kept n of 1 or 2; finalized-manifest binding; L9-conditional
   history entries, Fable F2 NOTE).
