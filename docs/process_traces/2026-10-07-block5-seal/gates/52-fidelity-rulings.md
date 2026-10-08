# Orchestrator's rulings on the fidelity sweep and the seal-gate preparation findings (2026-10-07 16:20 PDT)

Inputs: `REG_FIDELITY.md` (this directory) and the findings F1 to F6 and the open items in
`../seal-gate/QUESTIONS.md` sections 3 and 4. These rulings bind the registration writers. Principle applied: the
code at the frozen head has had a triple audit and four cold passes; a sentence that misdescribes it is corrected to
the fact, unless the code's behaviour would put a wrong number into a claim, exclude clean data, or break blinding.
None of the items below does the first two, so **no item here changes code before the seal**. Two items go to the
seal gate's judge because they change a registered rule about a claim (marked JUDGE): writers leave those passages
untouched until the judge has ruled.

## List A (the text is corrected to the fact, exactly as `REG_FIDELITY.md` gives it)
A1 to A9 and A11 to A18: apply each "Correction (fact)" as written there.

- **A10 ("plus the sizing margin").** No such number exists and no code re-derives an allowance. Delete the
  erratum-free resizing rule. The fact to write: a chain stopped at its deadline leaves the window without a post
  calibration, so the window is not claim-usable; a larger member allowance is a change to the sealed sizing output
  and needs an erratum with a new sizing file pinned by an addendum to the seal record; the question goes to a
  consult first. Say also why the case is remote: the deadline is the chain's length if every member takes its
  longest allowed path (about 27 hours), against a projected chain of about 5 to 6 hours. Remove the matching
  sentence in section 10 that says this resizing needs no erratum.
- **A19 / C4 (the metrology term of the two GAMMA contrasts). JUDGE (question SG-13).** Leave plan 7.1 step 3, 7.2
  and the two 8.1 passages untouched until the ruling.

## List C (code disagrees with the registered design)
- **C1 (one lost GAMMA diagnostic reference makes the yield LOW).** The code stays. Write the fourth case: GAMMA's
  two one-member diagnostic stages are counted as science stages with a minimum of 1 of 1; one lost diagnostic member
  gives LOW; by chance that is about 5.3% of GAMMA windows; for these two stages a LOW does not indicate a
  systematic cause. The yield status stops nothing and removes nothing; it sends a notice. The magistrate brief
  carries the same sentence so a single lost diagnostic member does not hold the next arm. Giving the diagnostic role
  its own minimum goes to the post-block-5 list.
- **C2 (a RESTRICTED flag code is written by name into `derived/` files). JUDGE (question SG-12).** Leave section 8
  item 2 and plan lines 468 to 469 untouched until the ruling. Whatever the ruling,
  `FILL[B5-BLIND-CUSTODY-MAP]` lists `derived/flags.jsonl`, `derived/exclusions.json` and the per-code counts of
  `derived/window_flags.json` as restricted until the release event.
- **C3 (`instrument.precal_screen_failed` is never emitted).** The code stays. Write: no flag of that name is
  written; a pre fiducial bound above the pre screen stops the chain (journal reason
  `pre_calibration_screen_failed`, exit 12) and the window is removed by `calibration.no_bracket`, whose causes
  include the chain stops at exits 10, 11 and 12. The catalog entry's note says it is a reserved code with no
  emitter.
- **C5 (one dwell sample with no anchor leaves the dwell's clock rules unjudged).** The code stays; A3's correction
  states it. Why it is acceptable for block 5: every member's own clock checks are made during the window and at
  the harvest, so no number rests on the dwell's verdict; the dwell only protects against starting a window on a
  drifting clock. Judging the series on the samples that did read goes to the post-block-5 list.
- **C6 (the "deliberately incomplete finalization" diagnostic).** Strike it from ALPHA-1's structural diagnostics in
  section 3 and say where it lives (the block-4 harvest script only).
- **C7 (eight catalog codes with no emitter, nine with C3).** They stay in the catalog as reserved codes. Each
  entry's note gains: "Reserved: no emitter at H_claim." Section 6.2 says that nine codes are reserved and names
  them.
- **C8 (END STATE across attempts and the fixed order ALPHA, BETA, GAMMA have no code).** Write, as section 7.3
  already does for its rule, that sections 7.2, 7.4 and 7.6 state rules the magistrate applies from the harvest
  verdicts; no code computes them (`first_claim_usable` has no caller outside tests). The magistrate brief carries
  the rules.
- **C9 (a chain killed before its first stage journaled is COLLECTED, not NO_COLLECTION).** Text to the fact.
- **C10 (the allowlist test admits DEFERRED_REPRESENTATION with an owner).** Text to the fact: section 6.11 names
  the fourth class, what it is for, and that it must name an owner.
- **C11 (four roster codes are EXCLUDE_MEMBER in the catalog; one ever removes a member under its own name).** Text
  and catalog notes to the fact.
- **C12 (assist energy is still computed and written to the withheld record after a charging read above 200 mA).**
  Text to the fact.

## Lists B, R and U
Apply every B and R correction as given. For U (undefined terms): build or gloss each term at its first use, or
delete it. In the analysis plan the line count above line 354 must not change
(`tests/fixtures/d165_rationale_allowlist.json` names that line): make U51 to U55, B42, B43 and R6 fit without adding
or removing a line above it, or report that it cannot be done and leave the test fixture to the integrator.

## From the seal-gate preparation (F1 to F6)
- **F1.** The two stale `extraction_spec.json` digests in plan section 4 (lines 211 and 214) and the three "re-tied
  at seal" phrases (lines 206, 291, 366): the final pass recomputes them at the final head and prints GAMMA's
  manifest digest. Mark them now with `FILL[B5-FINAL-HASHES]` so the final pass finds them.
- **F2.** Section 14 Q13's "nothing here changes collection" against section 7.5's definition of collection code by
  file: wait for the seal-landing ruling (the final pass writes it with sections 11 and 12).
- **F3 and F4.** The judge rules (SG-4 and the T, C, K marks).
- **F5.** `g3.recompute_failed` is listed as a window exclusion in the test fixture catalog and the allowlist while
  the catalog says DISCLOSE: the integrator aligns the fixture and the allowlist with the catalog after the judge's
  ruling on SG-3.
- **F6.** `identity_pins.json` and `sizing_b5.json` keep the `status` and `sealed` fields their generators write.
  No code reads them, and changing them would change sealed digests and break each generator's check for a label.
  Write in section 12: those two fields are generator labels written before the seal and are not updated; the seal
  record's SHA-256 of each file is what seals it.

## Open items with no owner (owners assigned)
- `FILL[B5-BLIND-CUSTODY-MAP]`: the final registration pass, from `../l9/map/x-blinding.md` and C2 above.
- `ATTRIBUTION-FLOOR-BINDING` (section 14 Q5): a separate investigation with one refuter, started today; the final
  pass fills it from that ruling.
- Section 14 Q4 (paper placement): not needed for the seal ("ideally before seal"); it waits for the owner's
  decision on one paper or two.
- Section 14 Q3 (ALPHA-1's contention flag rate): the desk session after ALPHA-1's harvest.
- The harvest-program addendum (section 11 item 4): write that the harvest program is pinned at H_claim by the
  sealed inventory, which lists its files; a separate addendum is written only when the harvest program changes
  (lane L9-NEG8), before the harvest that uses it.
- The #416 delta record for `fe28e5a0c..H_claim`: cold pass 5 and the independent executing review of the
  seal-landing lane; the final pass adds the row.
- `B5-ANALYSIS-CUSTODY-ROOT`: before the release event, with lane L9.

## Post-block-5 list (code changes deferred by these rulings)
- The GAMMA diagnostic role gets its own yield minimum (C1).
- The arm judges the dwell's clock series on the samples that did read (C5).
- Harvest-side redaction of RESTRICTED codes in `derived/`, if the judge rules for it (C2): lane L9, before any
  release.
