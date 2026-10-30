VERDICT: ACCEPT

# RC-CMP11-FABLE-REV: delta review of RC-CMP-11 (`1affc4208..f6a54deed`)

Seat RC-CMP11-FABLE-REV, Fable 5.1, cloud, synthetic only; no real block-5/6/BYTES data opened or searched for.
Branch `review/2026-10-30-rc-cmp11-fable-rev` at `f6a54deed`. `/usr/bin/python3.13` (3.13.17),
`TMPDIR=/tmp/claude-0/rccmpeleven_fable_tmp` (outside the checkout, no float-like token). Evidence in
`.codex-report/rc-cmp11-fable-rev/`. `.codex-report/RC-CMP-11.md` read as claims. Producers read as text at
`origin/main` = `0f34b2ca2` in this clone (the report's `d77ae428a` exists here as a commit; the pin tests read
`origin/main` and pass against `0f34b2ca2`). The lead's full-size window result is a claim I cannot re-run here.

**Summary.** Every RC-CMP-11 claim I re-executed holds. Suite at this head: `Ran 406 tests`, `OK (skipped=18)`,
exit 0 (`suite.out`); the 13 new tests pass individually (`rc_cmp11_tests.out`). My RC-CMP-10 F1 battery at this head
(`fs3b.out`): the 8 wrong relation words that exited 0 at `1affc4208` (my `rc-cmp10-fable-rev/fs3.out` B) now all
exit non-zero, all 20 negations exit 2, both sound windows exit 0 with 0 undetermined rows, the full-size b10 flip
and the one-ulp-apart case stay exit 0, and the identical-b10 missing-trigger case exits 2. Deletion sweep: 5035
deletions, exit-0 set byte-identical to RC-CMP-10's 643, **0 undeclared** (`sweep.out`, `classify.out`). The
exact-equality rule is correctly encoded for all 15 relations the comparator's words read (`eq_words.out` C, 0
mismatches). The p42 pin matches the issuer's own output on the synthetic pack (`p42_code.out`). Three NOTEs, no fix
required.

## Findings (ranked)

**F1 (NOTE). `equals_primary`: the producer's `_same` is a canonical-JSON digest, the comparator's test is float
equality.** `sensitivity.py:56-59` (origin/main) says the digest "distinguishes signed zero and JSON number
representations, unlike Python numeric equality"; the comparator's recompute-side word is `relation(..., a == b)`
(`scripts/compare_b5_recompute.py:3011-3030`) and its atom is `NE(sensitivity - primary, 0)`, now decided when
bit-identical (`:289`). Executed (`eq_words.out` D): for primary `0.0` / sensitivity `-0.0` (and `1` / `1.0`) the
producer prints `equals_primary` False while the comparator derives True on identical numbers, so a decided row would
DISAGREE. This is an over-refusal, never a false pass, and it is not shown reachable: both sides' values come from
the same computation under an equal bound, and the recompute's numeric rows would agree. Before RC-CMP-11 the same
pair was undetermined and passed. Not a fix; recorded so a signed-zero DISAGREE on `equals_primary` is read correctly.

**F2 (NOTE). `widened` is encoded as `!=`, the producer prints `>`; they coincide only because `b_sens` is a max.**
Comparator `:2794-2797` (`b_sens != b_op`, atom `NE`); producer `sensitivity.py:279` (`sensitivity_bound_s >
b_fiducial_s`) with `bracket.py:384-387` `b_sens = max(_bound(operative), _bound(b_max.value_s))`, so `b_sens >= b_op`
always and `!=` is `>`. At equality both are False (`eq_words.out` C). The `max` is the fact the encoding rests on and
is not pinned by a test; a one-line pin of `bracket.py`'s `max(` would make it a literal pin like the others.

**F3 (NOTE, my script). `fs3.py` SC closure now fails with `error=internal TypeError`** (`fs3b.out` C SC lines) because
`Comparison.word` gained the `vocabulary` keyword (`:242`) and my RC-CMP-10 `word_sc` patch does not accept it. SC was
the closure I rejected at RC-CMP-10; its lines in `fs3b.out` are an artefact of my script, not of the comparator.
Head and BI columns are unaffected.

## Answers

**1. fs3/fs3b and the deletion sweep at this head.** `fs3b.out` A: sound windows widened/unwidened exit 0, **0**
undetermined rows (RC-CMP-10: 11 and 21). B: all 20 relation/widened negations exit 2 at head (RC-CMP-10: 8 wrong
words exited 0); summary line `WRONG words ... exit 0 at head: 0`. C: full-size b10 flip (+3.55e-15 vs -1.78e-15,
L9 `['estimate_sign']`) exit 0 row AGREE; b10 identical +3.55e-15 both sides with no printed trigger exit 2. E: one
ulp apart (+3.55e-15 vs +3.5500000000000004e-15) exit 0; identical with the trigger on both sides exit 0. F: the 15
existing WithinBar/ConditionalFamily/LeaveOneOut/SensitivityFixture tests, 0 failures. Sweep (`sweep.out`): 5035
deletions, exits `{1: 1701, 2: 2691, 0: 643}`; the 643 exit-0 labels are byte-identical to RC-CMP-10's (28
deletions moved from exit 2 to exit 1, both non-zero); `classify.out`: 523 text/label/restricted, 15 `flag_count`, 3
`machine_absent`, 42 verdict-internal list members, 7 limitation/reason codes, 21+14 kept-units fields, 18 recompute
unread fields, **0 UNDECLARED**. No producer-unconditional deletion exits 0 undeclared.

**2. Exact-equality semantics.** Correct for every relation word, no misclassified word. `eq_words.out` A: `atom` at
bit-identical number and threshold gives `within=False` with truth GT/LT/NE False and LE/GE True; B: thresholds or
numbers one ulp apart stay undetermined; `+0.0`/`-0.0` is decided (Python `==`); NaN is never decided. C, producer
relation at equality next to the comparator's encoding, 15 of 15 agree: `equals_primary` (`_same`, NE-not-any: True),
`not_below_primary` (`>=`, GE: True), `widened` (`>`, NE: False, F2), `below_screen_bound` (`<`, LT: False), cross-window
`agree` (`abs(delta) <= hypot`, LE on the margin: True; `a - b <= 0` is `a <= b` for finite binary64), `plausible`
(`0 < rho <= 1`, `machine - rail >= 0`: GT/LE/GE, same expressions), `holm_reject` (`adjusted_p <= threshold`,
`multiplicity.py:157`, LE: True), dominance branch (`ratio >= DOMINANCE_THRESHOLD`, GE: True), `above_floor`
(`abs(estimate) <= floor` is not above, `claims.py:343`; loo `floor_status` `>`; GT: False), sign (`> 0.0` /
`_sign`, GT/LT: False at 0), interval contains zero (`lower <= 0.0 <= upper`, `claims.py:370-371`, LE/GE: True),
magnitude trigger (`abs(loo - full) > 0.25 * threshold`, GT with `times(0.25, floor)`: False). The only gap is the
representation one in F1, which is not a relation misclassification.

**3. Closed?** Yes. No new row, key, selector or route is derived from the recompute's output: the direction row
reads L9's printed value (`None` only for a printed `None`, absence is `None`, `:2248-2252`) against a pinned
vocabulary (`DIRECTION_WORDS` `:2505`, pinned to `claims.py` by `test_direction_words_pinned`); the per-position
trigger rows require membership in `INFLUENCE_TRIGGERS` (pinned to the engine) printed once (`:2356`); the p42 code
is a literal (`:2932`) pinned to the kernel line, the issuer's `strict_valid` rule and the issuer's own output;
the two `True` literals are pinned to `sensitivity.py`. The sweep's exit-0 residue is unchanged and entirely declared.
The RC-CMP-10 F1 value-binding gap is closed by the `atom` rule, and `test_rc_cmp8.test_each_relation_word_flipped_fails`
is back to "every flip fails" (verified in the suite and in `fs3b.out` F).

**4. The p42 code pin.** No false pass: `refused_code(..., P42_REFUSAL_CODE)` (`:2969-2981`) returns the code only when
the projection's refused cell, the record, its disclosure copy and its block line all print the same member code and it
equals the literal; the 32 other codes exit non-zero (`test_every_other_member_code_refuses`). No over-refusal on a sound
window that I can construct: the issuer builds the p42 rows itself (`paper_reported_energy_issuer.py:52-127`), so
the kernel's earlier codes in `_project_kept_cell` (`paper_reported_energy.py:502-525`: `schema_invalid`,
`record_identity_mismatch`, `member_count_invalid`) need a row the issuer did not build; the one pack-wide code,
`whole_window_allowance_unrecorded`, is per metric family of the window (`inputs.py:4405-4424`,
`whole_window_drift_allowances.get(family)`), so it cannot refuse the p42 cell while the pack's other cells compute;
and `strict_valid` is False for a p42 member whether from the precheck or from a strict-invalid bundle (`:125`), both
giving `record_invalid` (`:524-525`). Executed: the issuer prints `paper_reported_energy_record_invalid` for the
registered p42 cell on the s8 synthetic pack (`p42_code.out`). A sound window whose p42 members pass the precheck
would print status `computed`, which the pre-existing `p42_status` row refuses by registration, not by this pin.
RC-CMP-11 NEEDS_RULING 1 stands as stated (a p42 member failing an identity check is not a sound window).

## Evidence (`.codex-report/rc-cmp11-fable-rev/`)

- `suite.out`: the brief's command at `f6a54deed`, `Ran 406 tests in 514.393s` / `OK (skipped=18)` / exit 0.
- `rc_cmp11_tests.out`: `test_rc_cmp11` verbose, 13 ok.
- `fs3.py`, `fs3b.py`, `fs3b.out`: my RC-CMP-10 FS3 battery and closure battery at this head (answer 1).
- `sweep.py`, `sweep.out`, `classify.py`, `classify.out`: the deletion sweep and classifier (answer 1).
- `eq_words.py`, `eq_words.out`: the exact-equality probe per relation and the F1 representation gap (answer 2).
- `p42_code.out`: the issuer's p42 code on the synthetic pack against `P42_REFUSAL_CODE` (answer 4).

## Pruning tally (gate policy rule 9)

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| suite at `f6a54deed` | yes | no | no | `suite.out`, 406 OK |
| fs3/fs3b battery at head | yes | no (0 wrong words exit 0; ulp cases exit 0) | no | `fs3b.out` |
| deletion sweep + RC-CMP-9 classifier | yes | no (0 undeclared, set unchanged) | no | `sweep.out`, `classify.out` |
| per-relation equality probe | yes | no (15/15; F1 representation NOTE) | no | `eq_words.out` |
| p42 code derivation on the synthetic pack | yes | no | no | `p42_code.out` |
