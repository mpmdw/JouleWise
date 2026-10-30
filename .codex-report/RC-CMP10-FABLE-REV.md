VERDICT: ACCEPT_WITH_FIXES

# RC-CMP10-FABLE-REV: delta review of RC-CMP-10 (`f9f86869e..1affc4208`, excluding the merge `ab4029f7b`)

Seat RC-CMP10-FABLE-REV, Fable 5.1, cloud, synthetic only; no real block-5/6/BYTES data opened or searched for.
Branch `review/2026-10-30-rc-cmp10-fable-rev` at `1affc4208`. `/usr/bin/python3.13`,
`TMPDIR=/tmp/claude-0/rccmpten_fable_tmp` (outside the checkout, no float-like token). Evidence in
`.codex-report/rc-cmp10-fable-rev/`. Producers read as text at this head (`joulewise/b5_analysis/{disclosures,
sensitivity,archive}.py`, `configs/analysis/b5/recompute_bars.json`). Reviews read: my RC-CMP9-FABLE-REV and
`review/2026-10-30-rc-cmp9-opus-rev`; `.codex-report/RC-CMP-10.md` read as claims.

**Summary.** Every RC-CMP-10 claim I re-executed holds: `Ran 393 tests` / `OK (skipped=18)` / exit 0 in 650 s
(`suite.out`); my deletion sweep gives exactly the report's 5035 / `{1: 1673, 2: 2719, 0: 643}` with **0 undeclared**
(`sweep.out`, `classify.out`); my RC-CMP-9 probes confirm F1-F4 closed (`probes.out`). FS2 and FS4 are sound as
built (answers 3, 4). FS3 as applied to the relation words is the one defect: a word L9 derives by exact equality or
`>=` on the very numbers it prints is no longer compared when those numbers are unchanged, so a **wrong** word
(contradicting L9's own printed values and the recompute's identical values) exits 0 (F1). The fix is the closure the
brief names, one line in `Comparison.atom`, executed here: it catches all 8 wrong words and the identical-number
trigger case, keeps both sound windows and the full-size b10 flip passing, and leaves the undetermined mechanism
for the genuinely noisy case (answer 2).

## Findings (ranked)

**F1 (MEDIUM, fix). A wrong relation word on bit-identical numbers exits 0.** `Comparison.atom`
(`scripts/compare_b5_recompute.py:280`) marks a test undetermined whenever either side's number lies within the bar
of its threshold, and `Comparison.word` (`:249-266`) then compares only the numbers, never the words. For
`relation_words` (`:2984`) the test is sensitivity minus primary against 0, so an unchanged value is always
undetermined (DECISIONS 4), and the same holds for `widened` (`:2773`) when b_sens = b_op and for a loo trigger when
both estimates are identical. Executed (`fs3.out` B): of the 20 relation/widened words negated in every L9 copy, **8
exit 0 at this head although L9's own printed numbers say the opposite word**: unwidened `equals_primary` (reported,
floor), `not_below_primary` (reported, floor, contrast), `widened` (alpha, beta), and the widened prefill floor's
`not_below_primary`. The recompute's values are identical to L9's in every case. Likewise (`fs3.out` C) decode loo b10
at +3.55e-15 on **both** sides with L9 printing no `estimate_sign` trigger and the recompute raising one: exit 0.
RC-CMP-8's `test_each_relation_word_flipped_fails` required these flips to fail; `test_rc_cmp8.py:554` now asserts
they pass. The producer derives each of these words from exactly the values it prints (`sensitivity.py:303-304,
320-321, 345-346, 279`: `_same`, `>=`, `>`; `disclosures.py:1099`), and no bar family prints at reduced precision
(`recompute_bars.json`: no `printed_decimals`), so identical binary64 numbers on both sides evaluate every test
identically on both sides. Fix (`fs3b.py` `atom_bi2`), in `atom` after `:280`:
```
if within and l9 == ours and l9_threshold == threshold: within = False   # bit-identical numbers decide the test
```
Under it (`fs3b.out` E): both sound windows exit 0 with 0 undetermined rows; all 8 wrong words exit 2; b10 identical
with a missing trigger exit 2, with the trigger on both sides exit 0; the full-size b10 flip (+3.55e-15 vs -1.78e-15)
still `AGREE`/exit 0, and a one-ulp-apart flip still exits 0. Two tests encode the reversed behaviour and change with
it (`fs3b.out` F): `test_rc_cmp10.py:391` (case 2: L9 `below=False` with b_op below the bound, identical on both
sides, asserted to pass) and `:417` (asserts a `within_bar_undetermined` row on the unwidened window, where every
test is now decided). `test_rc_cmp8.py:554` can revert to "every flip fails".

**F2 (NOTE). The two L9-conditional history entries are the one one-sided condition in the table.**
`history_printed` (`:1370`) reads L9's disclosure only, by necessity (the archive's g10 flag codes and the steps'
re-harvest accounts have no registered source). Consequences, executed (`fs4.out`): an unrequested g10 line dropped,
or printed with any `codes` (H1, H3, H3b), exits 0; its `redraw_cycles` is bound to the index (H2 exit 2); a
re-harvest account's `reason`, pins, digests and survivor counts are declared unbound (H8 exit 0) while its existence
follows `harvest_once` (H7/H11/H12). A one-sided omission of an unrequested g10 line is therefore invisible. To
close it by registration, the window index would carry the g10 codes (it already carries `g10_requested` and
`g10_redraw_cycles`) — a ruling for Ed, not a comparator change (NEEDS_RULING 3 stands as declared).

**F3 (NOTE). FS2 accepts any member code for the p42 cell** (`refused_code` `:2942`, `expected=None`): all 33
codes of `REPORTED_REFUSAL_CODES` pass in every copy (`fs2.out` S2), including the below-minimum code (S1). Not a
false pass of a claim (answer 3); the sharper pin (`paper_reported_energy_record_invalid`, what the issuer prints
for the registered p42 cell, `producer_fixtures.p42_refusal_code()`) is available by the new literal-pin rule if Ed
wants the code itself fixed (NEEDS_RULING 1).

## Answers

**1. Sweep and probes at this head.** `sweep.py` (unchanged walk): 5035 single deletions, exits
`{1: 1673, 2: 2719, 0: 643}`; `classify.py` with the RC-CMP-9 classes: 523 text/label/restricted, 15 `flag_count`
and 3 `machine_absent` (NEEDS_RULING RC-CMP-9 4), **0** `attempt_count/causes` (was 3), **0** verdict
`removed_block_ids` members (was 2), **0** fill identity pins (was 2), 42 verdict-internal list members
(`included_bundle_ids/N` 36, `variance_contributions/N` 2+2, `reason_codes/N` 2+2; declared, their keys now required),
7 limitations/reason codes, 21+14 kept-units record fields, 18 recompute unread fields: **0 UNDECLARED**. No
producer-unconditional deletion exits 0 undeclared. My RC-CMP-9 probes (`probes.out`): F1 closed (P1, P3, P4, X1, X3,
X4, X5 exit 0; P2.a/b, P3.a/b, P4.a/b non-zero with the table rows named); F2 closed (P6.a 2, P6.b 2, P7.a 1);
F4 closed (P8 exit 2); F3 pinned (`test_extended_fill_precondition`); everything else as at RC-CMP-9 (P0 0, P5 2/2,
P9.a 2, P9.b 0 declared, P10 2/2, P11 1/1, P12 2/2, P13 0/0).

**2. FS3 within-bar rule.** Yes: a wrong `equals_primary`, `not_below_primary` or `widened` word exits 0 whenever the
values are unchanged (8 cases, F1; `outcome_equals_primary` happens to stay decided on this fixture because its
outcome tests are far from their thresholds, but the same rule applies to it). The by-construction booleans are
unaffected (compared exactly against True, `fs3.out` B: exit 2 in every case). **"Bit-identical values on both
sides count as decided" is the right closure**, and it is sound in general, not only for the relation words: the
undetermination exists to absorb cross-side rounding, and identical binary64 numbers and thresholds have none, so
both producers' tests have the same truth value and the words must agree. It is one line in `atom` (F1), it keeps
the genuinely noisy case undetermined (b10 +3.55e-15 vs -1.78e-15 passes; one ulp apart passes), and it changes the
two test expectations named. The alternative I also executed, requiring each side's word to equal the comparator's
`decide` over that side's own truth values (`fs3.py` SC), catches the same 8 but refuses the full-size b10 flip
(`fs3.out` C), because the trigger `decide` does not reproduce the producer's trigger derivation on L9's side; it is
not the closure to take.

**3. FS2 p42 code.** Sound for the claim, not a false-pass route. The claim is the registered refused exit: the
projection must list the cell as refused (S5 exit 2) and not as computed (S6 exit 1); every copy must print status
`refused` (S9 exit 2) and a code (S7 exit 2); the recompute's status must be `expected_unresolvable` (S8 exit 2); the
code must be a member (S3 exit 2) and identical in every copy (S4 exit 2). Nothing is re-derived, and the code is not a
claim number. The refused non-p42 cell (FABLE F1) is pinned to the below-minimum code: a member code that is not it
fails (S11 exit 2, S10 control 0). The residual freedom (any member, 33 of 33 pass) is F3 / NEEDS_RULING 1.

**4. FS4 history lines.** Existence is index-derived for `attempt_count`, `attempt_history`, requested `g10` and
`superseded_history` (a line for a plan the index lacks: H4 exit 2; duplicated: H5 exit 2; wrong pack: H6 exit 2;
verdict, cause order and count bound: H13/H14 exit 2). The index is the file L9's record names by digest
(`window_index_digest_differs`), and the producer refuses an archive verdict that differs from the index entry's
(`archive.py:125`), so the index verdict is the printed verdict by construction. The two `history_printed` entries are
**output-derived (L9 only)**: an unrequested `g10` carries one index-bound number (`redraw_cycles`, H2) and the
archive's flag counts (`codes`, unbound, H3); a `reharvest_account` carries step-record words and counts (unbound,
H8), with its existence bound to `harvest_once` (H7, H11, H12). Neither carries a recompute claim: the recompute reads
no archive and no steps record. The one-sided omission (an unrequested g10 line L9 should have printed) is F2.

**5. Closed?** **Yes, as a class, with F1 open as a value-binding gap, not an existence gap.** No table entry, row
constructor, selector or route exists, is keyed or is routed by the recompute's output; every new entry's key source
is the registry or the digest-bound index; `history_printed` is the one condition read on one side only, and it
switches on checks bound to the index (answer 4). The sweep's exit-0 residue is entirely declared. What F1 reopens is
a word whose comparison was made conditional on a numeric bar and thereby lost for the exact-equality case; the fix
restores it without reintroducing the over-refusal FS3 was built to remove.

## Evidence (`.codex-report/rc-cmp10-fable-rev/`)

- `suite.out`: the brief's command at `1affc4208`, `Ran 393 tests in 649.681s` / `OK (skipped=18)` / exit 0.
- `sweep.py`, `sweep.out`, `classify.py`, `classify.out`: answer 1.
- `probes.py`, `probes_extra.py`, `probes.out`: my RC-CMP-9 P0-P13 and X1-X5 at this head.
- `fs3.py`, `fs3.out`: FS3 (A undetermined rows, B 20 word negations under head/BI/SC, C soundness, D copy flip).
- `fs3b.py`, `fs3b.out`: the proposed closure (BI2) battery and the existing tests under it.
- `fs2.py`, `fs2.out`: FS2 S0-S11. `fs4.py`, `fs4.out`: FS4 H0-H15.

## Pruning tally (gate policy rule 9)

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| suite at `1affc4208` | yes | no | no | `suite.out`, 393 OK |
| deletion sweep + RC-CMP-9 classifier | yes | no | no (0 undeclared) | `sweep.out`, `classify.out` |
| RC-CMP-9 F1-F4 probes re-run | yes | no | no (all closed as claimed) | `probes.out` |
| FS3 word negations on unchanged values | yes | yes (8 wrong words exit 0; b10 identical) | no | `fs3.out` B/C |
| FS3 proposed closure, soundness and existing tests | yes | no | no (two tests encode the reversed behaviour) | `fs3b.out` |
| FS2 p42 code routes | yes | no | no | `fs2.out` |
| FS4 index-keyed and L9-conditional history | yes | no | no | `fs4.out` |
