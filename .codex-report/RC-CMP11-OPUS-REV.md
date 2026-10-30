VERDICT: ACCEPT

# RC-CMP11-OPUS-REV: blocking delta review of RC-CMP-11 (1affc4208..f6a54deed)

Branch `review/2026-10-30-rc-cmp11-opus-rev` from `f6a54deed`. I used synthetic fixtures only and did not open or
search for any real block-5, block-6 or BYTES data. I ran `python3.13` with `TMPDIR=/tmp/rcrevtmp` (outside the
checkout, no float-like token). Producers were read as text from `origin/main` (`0f34b2ca2` at fetch). Probes and
outputs are in `.codex-report/rc-cmp11-opus-rev/`. The RC-CMP10 probe headers print a static "at 1affc4208" label,
but every run below is at `f6a54deed`.

## Findings (ranked)

None blocking. All F1-F5 closures hold under execution, and no false pass is left in the probed space.

- **N1 (NOTE, over-refusal only, non-blocking).** The fix places `equals_primary` among the equality words (true at
  equality), but the producer does not test numeric equality. `sensitivity.py:56-59 _same` compares canonical
  digests and "distinguishes signed zero and JSON number representations". The comparator's recompute word
  (`scripts/compare_b5_recompute.py:3021`, `lambda a, b: a == b`) and its atom (`NE` on sensitivity - primary)
  both treat `-0.0`/`0.0` and `1`/`1.0` as equal. Before this round, an identical diff of 0 sat inside the bar and
  the row passed as undetermined. After F1 (`:289`), the test is decided and the producer's correct word
  DISAGREEs. `probe_cmp11.py zero` (unit call of `relation_words`, identical values on both sides):
  ```
  Z0 0.0 -> 0.0 (control): producer equals_primary=True comparator row=(True, True, AGREE, None)
  Z1 0.0 -> -0.0: producer equals_primary=False comparator row=(False, True, DISAGREE, None)
  Z2 1 (int) -> 1.0: producer equals_primary=False comparator row=(False, True, DISAGREE, None)
  ```
  This only refuses, on the safe side, and it needs a signed-zero or int-typed floor/allowance value. The
  synthetic windows and the lead's full-size window carry neither. If such a value is ever plausible, the fix is to
  derive the recompute's word as the producer does (canonical JSON / `repr` equality, sign-aware) and to decide the
  atom on `math.copysign`-aware identity. Otherwise, record this case.
- **N2 (NOTE, scope of NEEDS_RULING 1).** One more producer path can give the p42 cell another code. The issuer
  (`paper_reported_energy_issuer.py:116-117`) raises `whole_window_allowance_unrecorded` per cell when the cell's
  claim family has no allowance `> 0.0` (`inputs.py:4406-4424`, so an allowance of exactly `0.0` counts as
  unrecorded). The lead's argument ("other cells computed ⇒ allowance recorded") holds only if a computed cell
  shares the p42 cell's family. Either way, the pin can only over-refuse, never pass falsely. I add this to the
  ruling, not to the fixes.

## Answers

**(1) Probes rerun at f6a54deed.**
- `probe_cmp10.py eq` (`eq.out`): E1-E9 all exit 2; E0 control 0. U1-U4 (full-size b10 flip; L9 exactly 0.0 vs
  ±1e-16) exit 0, whole-list row `AGREE within_bar_undetermined`.
- `p42` (`p42.out`): P0 control 0, producer code in fixture `paper_reported_energy_record_invalid`; all 32 other
  closed codes exit 2.
- `garbage` (`garbage.out`): G1 banana, G2 duplicate, G3 `outcome` all exit 2.
- `direction`: the lead is right that my RC-CMP10 D cases were vacuous. `contrast_rows(c)` defaults to DECODE,
  and the filter kept only PREFILL, so no row was mutated (`direction.out` shows L9 `'none'` in every case). The
  corrected `probe_cmp11.py direction` (`direction11.out`) mutates 2 rows per case. D0 None gives 0. D1 False,
  D2 `''`, D3 0, D4 `[]`, D5 banana and D6 `positive` on a non-supported contrast each give 2. D7 (key absent)
  gives 2 (`required_key_absent:.../direction`).
- `hist` (`hist.out`): `control=0 mutations=356 exits={1: 73, 0: 128, 2: 155}`. This is identical to RC-CMP-10.
  The class is unchanged and stays under RC-CMP-10 NEEDS_RULING 4 (L9-conditional history entries), out of scope
  for this round.
- Fable `fs3.py` (`fs3.out`): A gives 0 undetermined rows on both sound windows. B: "WRONG words ... that exit 0
  at head: 0". C head: sound 0/0, full-size b10 flip 0, b10 identical with a trigger mismatch 2. D gives 2. The
  SC-closure rows end in `internal TypeError`. That is the probe's own `word_sc` mock lacking the new
  `vocabulary` parameter, not head behaviour.
- Fable `fs3b.py` (`fs3b.out`): E sound windows 0 with 0 undetermined. The full-size flip and the one-ulp-apart
  case each give 0. b10 identical with no trigger gives 2. F: `ran=15 failures=0 errors=0`.
- A strict claim over equal values fails: E6 (`widened` True at b_sens == b_op) exits 2, and the suite's
  `test_strict_claim_over_equal_values_fails` (`below` True at b_op == SCREEN_BOUND_S) passes.

**(2) Relation-word classification.** I checked each atom against its producer line:
- positive `> 0` / negative `< 0` (claims.py `numeric_estimate > 0.0`).
- above_floor `>` (`abs(estimate) <= floor` → not above).
- decision/metrology ends `<= 0` / `>= 0` (claims.py `lower <= 0.0 <= upper`).
- reject `<= alpha` (artifact.py:738).
- magnitude `>` (sensitivity.py:184 `> 0.25 * threshold`).
- agree `<=` (disclosures.py:440, against hypot; `a-b<=0` ⇔ `a<=b` for finite binary64).
- rho `0 <` and `<= 1`, machine-rail `>= 0` (disclosures.py:653).
- below `<` (disclosures.py:1099).
- widened: `NE` against producer `>` (sensitivity.py:279). These are equivalent because `b_sens = max(op, b_max)`
  (bracket.py:384).
- not_below_primary `>=` (sensitivity.py:304/321/346).
- dominance ratio `>=` (dominance_closeout.py:524 "R >= 2").

Strict words are false at equality, and non-strict and equality words are true. The one misclassification is
`equals_primary` (N1): it is digest equality, not `==`, and the mismatch shows only at signed zero or int/float.

**(3) p42 pin.** I found no false pass. `refused_code` (`:2980`) now needs `code == P42_REFUSAL_CODE`, a closed-set
member, in all four copies. All 32 substitutes refuse. The pin matches `_project_kept_cell`
(paper_reported_energy.py:524-525), the issuer's `strict_valid` line and the issuer's own synthetic output. For a
sound window, the earlier per-row raises in `_project_kept_cell` (`record` schema, `record_identity_mismatch`,
`member_count_invalid`) all mean malformed input. `kept_units_below_minimum` is raised after the row check, so it
cannot pre-empt `record_invalid` unless no p42 row is kept. The remaining sound-window over-refusal path is N2.

**(4) New output-derived checks or unpinned literals.** I found none.
- `P42_REFUSAL_CODE` is pinned (`P42ProducerCodeTests`).
- `DIRECTION_WORDS` is pinned to claims.py text and asserted.
- `INFLUENCE_TRIGGERS` is AST-pinned to `sensitivity.influence_triggers`.
- `printed.count(word) == 1` (`:2356`) reads L9's printed list only to narrow, never to supply the expected value.
- The F1 identity reads one L9-side and one recompute-side number.
- The `vocabulary` check (`:267-268`) adds a condition and supplies no word.

## Suite

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
with `TMPDIR=/tmp/rcrevtmp`: `Ran 406 tests in 578.268s`, `OK (skipped=18)`, exit 0 (`suite.out`).
