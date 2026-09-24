# 53 — Bookkeeping fidelity lens (Opus 5.5, read-only) on `edcd045b..f3d4448f`

Scope: RUN_STATE top block, kernel notes and statuses (A280, A282, A291, A292, A293, A294, A295), README "Now" paragraph, ledger L-043..L-049, `tests/test_gen_state.py`. Checked against record 00 items 1–36, records 27, 29, 36, 39, 46, 50, 02d, 07d, 15/10, 15/20/21, 30/21, and `gh pr view 403`.

## Verdict

1 BLOCKER, 5 SHOULD-FIX, 10 NIT. Check (3) passes. Check (2) passes in RUN_STATE, kernel and TASK_QUEUE, but **fails in README**.

## Verified correct (executed this session)

- `gh pr view 403`: merge `edcd045bea8a…`, head `69fd5daf47fe…`, MERGED. Matches RUN_STATE, TASK_QUEUE and the test comment.
- Replay: 7,044 tests with 0 failures at `2235eecb` (item 32). Kernel count is 245 (`len(tasks)`); `updated` is 2026-09-24; A294/A295 were moved into TERMINAL_IDS and the TASK_QUEUE completed table.
- All 23 new `2026-09-24-activation-a65fb4fa/...` evidence paths in the kernel exist on disk.
- Ledger arithmetic: 42 + 7 = 49 rows; 24 + 7 = 31 fully evidenced; 31 + 18 = 49. L-044 has 12 findings (1 + 8 + 3, per item 15). L-046 has 17 (1 + 12 + 4, per item 25). L-043's two missed catches are 15/10 M1/M2. L-047 is consistent with items 29, 31 and 33. L-049 has 2 BLOCKERs, all accepted (record 29).
- A291 stress facts: I1 ran 300 registrations with 0 violations against the unfixed checker (36:40). Seeds 291013 and 291014 each ran 300 registrations with 0 violations (46:38–39). Report 50 labels S1 as the D5 same-signature repeat, so the kernel's "S1 same-signature YES" is correct.
- 15/10 Q1: `merge_order`, `min_correct` and `holm_m` go to A293 and `cap_bound_fraction` to A292 as mandatory CONSUMED rows. The PROVISIONAL reduce column comes from Q16. The FT-9 text matches addendum line 74. A280's carried fields match 02d lines 687–690.
- Check (2): the RUN_STATE step (2) and the A291 `status_note` both carry item 36 correctly: the trigger fired, a blind Sol plus Opus consult comes next, then a cold Fable gate on the fix-round-2 plan before any code, then I2 and I3. A grep of RUN_STATE, the kernel, TASK_QUEUE and README finds no surviving "delta re-audit of 20cd29de, then I2" instruction.
- Check (3): nothing presents AP-5M as adopted. A282, A293 and README all say adoption is pending Ed, and the kernel contains no "adopted AP-5M" or similar string.

## BLOCKER

**B1 — The README describes A291 as if it were only waiting on tests (fails check 2; contradicts item 36 and record 50).** The current text says: "review found and fixed errors in both, and the packer now passes two stress runs … It still needs tests that vary every registered field and required rule, tests that deliberately break individual checks, and final independent reviews." It leaves out three facts: delta 50's open BLOCKER, the F1 verdict "FIX INTRODUCED A NEW DEFECT", and the escalation to a consult and a cold gate. Replace the sentence from "A separate checker was committed" through "final independent reviews." with:

> A separate checker was committed before the packer code, and review found and fixed errors in it. The packer passes two stress runs of 300 planned schedules each. However, the latest independent review found that the packer's final self-check (its *seal*) accepted a deliberately forged schedule that placed one problem group in two captures at once, which the separate checker rejects. It also found a second error of the same kind as the one just repaired. Because the same kind of error has survived two rounds, the next step is not another repair. First, two AI models from different vendors each propose a structural fix without seeing the other's proposal (the leading candidate is one shared list of rules that the seal enforces and the checker mirrors). Then a fresh reviewer with no stake in the work must approve that plan before any code changes. After that come tests that vary every recorded input setting and required rule, tests that deliberately break individual checks, and final independent reviews.

## SHOULD-FIX

**S1 — README: "arm" means two different things.** The README's own glossary (line 8) defines an *arm* as "one pre-registered workload or comparison track". The new paragraph uses the word in its scheduling sense instead. Replace "after the earlier arm check" with "after the check made when the night was scheduled". Replace "Nothing is armed." with "No measurement night is currently scheduled."

**S2 — README repeats wording that installation check 39 flagged as a BLOCKER.** The phrase is "handles an overlong attempt without losing a problem". Check 39 F1 flagged categorical no-drop wording in 07d as a BLOCKER: under T-14/T-15, a problem can end as a typed terminal refusal. Replace with: "and, when an attempt runs too long, retries it in smaller captures so that every problem ends either measured or with a recorded reason why it was not."

**S3 — README uses internal shorthand without explanation.** The unexplained terms are "registered field", "energy reducer", "statistical estimator" and "reviewed capture record". The old paragraph explained "reducer"; the new one does not. Replace "The later energy reducer and statistical estimator wait for that reviewed capture record and the analysis rules." with "The later steps that add up measured energy per problem group and compute the statistics wait for that reviewed schedule record and the analysis rules." (The B1 text already replaces "registered field".)

**S4 — Kernel A291 `acceptance.evidence` is missing the record that sets its next action.** Add `"docs/process_traces/2026-09-24-activation-a65fb4fa/50-a291-fix1-delta.md B1 BLOCKER (seal and cache), S1 same-signature (D5 YES), S2 seed diversity"` and `"docs/process_traces/2026-09-24-activation-a65fb4fa/36-a291-implementer-i1-report.md I1 stress run"`. In the record-00 entry, change "items 3, 8, 11, 13, 15, 18–19, 22 and 26–31" to "items 3, 8, 11, 13, 15, 18–19, 22, 26–31, 33 and 36".

**S5 — A282 status is `queued`, which renders as "READY [AGENT] | Redraft packet C as AP-5M" in TASK_QUEUE,** even though no agent work remains until Ed replies. A successor that picks work by status could start a redraft. This is the magistrate's call: add an Ed-decision dependency (status `blocked`), or add "no agent action until Ed replies" at the start of the status_note.

## NIT

- **N1.** Kernel A291 evidence label "FT-1..FT-14 and I2 gate": the addendum 15/20/21 contains no I2 gate. Use "FT-1..FT-14 (stage-agnostic culprit rule; FT-9 runner obligation)".
- **N2.** Kernel A282 summary: "has passed the cold ruling, paired refuter, addendum …". The refuter found a BLOCKER, so the draft did not pass it. Use: "The version-4 proposal installs the cold ruling as amended by the addendum after the paired refuter; its 28 operative texts passed the byte-exact installation check, and the check's paraphrase BLOCKERs were fixed at 1f07c4ec."
- **N3.** Kernel A291 note: "F1-F4 arithmetic confirmed". Report 50 gives F1 as "FIX INTRODUCED A NEW DEFECT". Use "F1–F4 arithmetic confirmed on legal rosters; F1's fix introduced S1".
- **N4.** The structural-cure candidate in RUN_STATE and the kernel ("the seal enforces and the checker mirrors") drifts from record 36's wording ("one invariant table consumed by both, the checker staying independently written"). Carry the record wording.
- **N5.** README, question E3 (07d:35): E3 also asks which thinking mode is primary. Use "how the models decode answers and which reasoning mode is primary".
- **N6.** README, question O-21 (30/21 A17): use "whether a claimed energy difference must also exceed the instrument's minimum resolvable difference".
- **N7.** L-043: "refusing minima at requeue exits" reads as if refusing were correct. Use "minima wrongly refusing at requeue exits".
- **N8.** L-049: lens 27 had 8 findings (2 BLOCKER, 5 should-fix, 1 nit), all accepted. Use "2 BLOCKER + 5 MATERIAL + 1 NIT; all 8 accepted".
- **N9.** Kernel A280 note omits `scorer_id`, which 02d:689 lists as CARRIED to "A292 and the runner". Add it to the consumed list.
- **N10.** The README "Now" overwrite removes 09-23's pilot result (11 of 12 captures kept) from every README paragraph. Earlier bookkeeping also overwrote, so this is optional; one "Previously (2026-09-23)" sentence would keep it.

No other mismatches found in the numbers, shas, record references or statuses checked above.
