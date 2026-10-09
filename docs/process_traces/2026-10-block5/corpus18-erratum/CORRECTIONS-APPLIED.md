# Corrections applied to `ERRATUM.md` after the cold ruling

Written 2026-10-09 by the Opus 5.5 seat that applied the corrections. The cold ruling (`RULING.md`, section E)
admitted the erratum with 14 numbered corrections. This file says where each one landed in `ERRATUM.md`, what
else had to change so that no sentence of the draft contradicts the ruling, and what in the ruling could not
be applied cleanly. The seat changed `ERRATUM.md`, wrote this file, and changed nothing else: no code, no
configuration, no git state. It opened no file of a claim window.

Line numbers are lines of `ERRATUM.md` as this seat left it (1,955 lines; the draft had 964). "R" and "P"
numbers are the numbered edits of its section 4.5 (R for the registration, P for the analysis plan).

## 1. The 14 corrections

| # | The ruling's correction, in short | Where it landed in `ERRATUM.md` |
|---|---|---|
| 1 | Replace the rule with section B items 1 to 6, word for word, and the worked example. n is "10, 11 or 12 at the desk; the in-window bound, which decides nothing, rests on 10 to 18". Section 2.5 stays as the reason, with the power table and the in-corpus-drift sentence; replace the bullet "The claims stay honest; they get less sharp". | Section 2.1, lines 268 to 376: the six items quoted (278 to 312), the worked example quoted (320 to 328), the same example in numbers (330 to 346), the n sentence (366 to 369). Section 2.2, lines 378 to 411. Section 2.5, lines 464 to 554: power table (501 to 517), in-corpus drift (519 to 522), the replaced bullet (530 to 538), why (d) (544 to 554). Section 8 J1, lines 1821 to 1833. In section 4.5: R15 (1103), R19 to R21 (1176 to 1272), P2 (1454). |
| 2 | The seal commit carries three files; add to 4.5 the lines 750-756, 1650, 2523-2524, 3026-3027, 5542, 5690, and 88, 3094, 3110, 4498, 5773; say brief §9 step 2 is departed from and why. | Section 0, term "Seal documents, seal commit" (143 to 148). Section 4.3, "The seal commit: three files, one parent" and "Why three files and not one" (830 to 848). Section 4.4, steps 7 and 8 (923 to 935). Section 7, gate 4 (1711 to 1729). In section 4.5: 750-756 is R4 (1010); 1650 is R7 (1029); 2523-2524 is R12 (1071); 3026-3027 is R24 (1290); 5542 is R34 (1369); 5690 is R35 (1377); 88 is R2 (998); 3094 is R27 (1319); 3110 is R28 (1329); 4498 is R31 (1346); 5773 is R37 (1392). |
| 3 | Replace the two "no step looks at an energy" sentences with the ruled sentence; add the per-reason count to analysis plan line 597. | The ruled sentence, word for word: section 2.2 (392 to 395) and section 3, first bullet (574 to 583). The mechanism built from the code: 397 to 411. In section 4.5: the sentence inside the new 5.3 text, R21 (1198 to 1272); the analysis plan's addition, P2 (1454 to 1467). |
| 4 | Draft 2.5 fourth bullet and the J1 text: as correction 1. | Lines 530 to 543 and 1821 to 1833. |
| 5 | Margin: "may lose up to eight members to status, validity or physics; one refused or indeterminate member still gives `neg8.bound_not_derived`." | Section 2.1, "The margin, and its limit" (356 to 365). In section 4.5: the new title of 5.3, R14 (1097), and the last two sentences of R15 (1103 to 1119). |
| 6 | Add gate 5 of section D; the pin addendum is written before the first arm. | Section 7, gate 5 (1731 to 1739). Section 4.3, table F (856 to 863). Section 8 J6 (1866 to 1872). Section 0, term "Harvest lane, harvest pin" (149 to 152). |
| 7 | Add gate 4(c), the text gate, with the search list of A.7. | Section 7, gate 4(c) (1716 to 1728). Section 4.5, table "Lines of the registration that hold a first-seal value and stay" (1427 to 1444), which tells the gate's reader which hits are expected. |
| 8 | `chain.py` unchanged; new deviation 9, in the ruling's words. | Section 4.1, two table rows (the `DEVIATIONS` row and the sizer's `source` row). Section 4.3: `chain.py` removed from the change list, "What must not change" (865 to 872), "Count" (874 to 878). Section 4.5: R33 (1352), deviation 9 word for word. Section 8 J5 (1854 to 1864). |
| 9 | 5.3 text: the refuter's three points. | Section 4.2, finding F2, "Two more facts about route 2" (724 to 743) and the diagram's last boxes. In section 4.5: R17 (1140 to 1167), parts (a) to (e); part (e) carries the three points. |
| 10 | Section 6: step 3 struck; step 4 replaced by A.10's bound. | Section 6, lines 1640 to 1667. Section 8 J7 (1874 to 1879). |
| 11 | Procedure (a): the two numbers of A.18 and the fallback stated as the arm rule. | Section 7, procedure (a) (1795 to 1804), and gate 8 (1760 to 1770). |
| 12 | Table C/D and 4.7: the harvest-lane files and the tests of D item 5; `bound_count` 18, `planned_bound_bundles` unchanged; the six corpus files enter the inventory only through `external_inputs`. | Section 4.3: "Two descriptive fields" (808 to 810), "What the inventory lists" (850 to 854), table F (856 to 863). Section 4.2, finding F3 (762 to 766). Section 4.7, lines 1535 to 1562. Section 4.5: deviation 8 in R33 (1352). |
| 13 | Sections 5 and 7: superseded attempts do not count toward rule 1; the post-restart checks and the macOS build check; the dead-man desk check before GAMMA. | Section 5, "The superseded attempts and the re-arm rule" (1595 to 1600). Section 7, gate 8 (1760 to 1770) and "One desk check before GAMMA" (1778 to 1790). In section 4.5: R38, the Q16 entry (1397), and P3 (1469). |
| 14 | Preamble item 1: "The ruling's reason for (a) was wrong; this erratum's rule is (d), ruled 2026-10-09." | Lines 24 to 31, the sentence word for word, followed by a gloss of "(a)", "(d)" and "bound". |

All 14 are applied.

## 2. Further edits that the corrections forced

Each of these follows from a correction; none adds a rule.

| Where | What changed | Why |
|---|---|---|
| Title, status line, lines 1 to 22 | The title names the cap. The status is "admitted with corrections", with the sentence that the ruling governs. A paragraph tells the two rulings apart. | The task's required status line. The draft said "the ruling" for the consult ruling of ALPHA attempt 3 and once called it "the cold ruling" (draft line 31); with a second ruling in play that word had to be pinned. |
| Section 0 | Nine terms added before their first use: collection code and desk code, committed order, collected manifest and prune, in-window bound, core reader and builder, route 1 and route 2, monitor join, clean bound and cap, seal documents and seal commit, harvest lane and harvest pin. The NEG-8 corpus term says 12 under the first seal and 18 now. | The ruled rule uses every one of these words. The writing standard requires each to be built before it is used. |
| Section 2.4 | A row for n = 11 (t = 2.228) in the multiplier table; the row for 18 is marked "in-window bound only". | Under rule (d) the deciding bound rests on 10, 11 or 12 members. |
| Section 3 | Three table rows (the physics drop now runs always; the formula is not edited; the window's code is byte-identical) and a bullet on the cap. | So that "what does not change" does not contradict the desk change. |
| Section 4.1 | A row for `neg8_corpus_physics`, the one method the desk rule changes. | The section's claim "no live logic holds 12" stays true; the reader is told where the desk change is. |
| Section 4.4 | Step 6 (per-pack diff check) and step 7 (the commands that fill the placeholders) added; the old step 6 is now step 8 and says three files. | The task asks for the command behind each placeholder. |
| Section 4.5, R1 and P1 | An amendment clause in each document's status line. | **Not ordered by the ruling.** Without it a file headed "Revision 12, 2026-10-07" would hold text of 2026-10-09. The magistrate may strike both. |
| Section 4.5, R11 | Line 2272 of the registration, `"planned_bytes": 24045944832`, changes to `25190989824`. | Found by search. The ruling's list has the number with commas (line 2261); this is the same number in the thresholds block, without commas. |
| Section 4.5, R26 | 35,700 s → 37,500 s and 32,725 s → 34,375 s on line 3069. | These are 125 × 300 and 125 × 275; the draft's row for lines 3068 to 3072 missed them. |
| Section 4.5, R27 and R28 | Lines 3095, 3096, 3111, 3112 (BETA and GAMMA sums) change with 3094 and 3110. | The ruling names 3094 and 3110; the next two lines of each list carry the same sum for the other two packs. |
| Section 4.5, R13(c), R18(b), R20 | Three worked examples of the registration (corpus retry, the closed list, the physics drop) reworked on 18 members. | Each said "of 12" or "the other 11". |
| Section 4.5, R17(c), R17(d), R19 | The re-screen's case (c), the words "physics-clean bound", and the physics drop's mechanism sentence now say that the clean bound is built on every window and that the clean manifest also leaves out the capped members. | Rule item 3. |
| Section 4.5, R38 | A new entry Q16 in the registration's section 14. | The draft's "14, new entry" row, written out. It also carries correction 13's sentence and the list of what stays as history. |
| Section 4.5, R39 | One sentence beside lines 6123 and 6153. | The ruling, minor finding 12: they "stay as history with one sentence saying so". |
| Section 4.5, P4 | A dated entry in the analysis plan's section 14. | That section lists every revision's changes. |
| Section 4.5, rule 2 | Line 354 of the analysis plan must stay line 354. | `tests/fixtures/d165_rationale_allowlist.json` names that line; found by search. |
| Section 4.7 | The test list is split into window side and harvest lane; the draft's test "n = 18 uses t = 2.110" is dropped. | No deciding bound rests on 18. |
| Section 7, gate 4(c) | Three searches added to the ruling's list: `24045944832`; the old H_claim `a64000884`; an unfilled placeholder. | They follow from R11, R7/R34 and the placeholders. |
| Section 9.2 | What this seat read, computed and did not run. | The draft's section 9 covered the drafting seat only. |

Section 4.5 has 39 numbered registration edits and 4 analysis-plan edits, and 12 placeholders (listed with
their commands at lines 972 to 988).

## 3. What in the ruling could not be applied cleanly

Stated exactly. Nothing here was resolved by this seat.

1. **A multiplier in rule item 4.** The ruling's section B item 4 says "The t multipliers are 2.262, 2.201,
   2.201 at n = 10, 11, 12 (unchanged)". The code's table (`joulewise/aggregate.py` lines 41 to 59) gives
   2.228 at 10 degrees of freedom, which is n = 11. The item is quoted word for word in section 2.1, and the
   paragraph after it (lines 314 to 318) says that the table governs and that "(unchanged)" settles the
   intent. The registration edits print no multiplier for n = 11, so nothing sealed depends on the figure.
   The magistrate may want one line from the judge, or may accept the reading.

2. **Which of two behaviours the registration registers for a stored bracket with another NEG-8 condition.**
   Correction 9 and required test (c) both say "still fails or re-derives correctly". The sealed sentence at
   registration lines 2838 to 2840 says "In case (a), any other NEG-8 condition leaves the screen failed",
   and the code guard behind it (harvest pin line 5233) stops applying once the clean bound exists on every
   window (line 4915). This seat wrote the ruling's own "or" into R17(e) and left lines 2838 to 2840 as
   sealed. If the harvest-lane test shows "re-derives correctly" and not "fails", that sealed sentence is no
   longer exact, and it is in the seal commit by then. **The magistrate decides** whether the harvest-lane
   build is required to keep "fails", or whether lines 2838 to 2840 get an edit before the seal commit.

3. **Lines 750 to 756.** The ruling says the seal commit must carry edits to the plan-tree digests "at
   750-756". Lines 750 to 752 are inside a sentence dated to the int5 head `fe28e5a0c`, which stays true. R4
   edits lines 754 to 756 (the "At H_claim" sentence) and leaves 750 to 752 as dated history, and the table
   of lines that stay says so. If the magistrate reads the ruling as "no old digest remains", R4 must be
   widened.

4. **The rehearsal's pass condition.** Section D gate 7 says the record shows "the clean bound built from 12
   with 6 under `beyond_cap`". That is exact only if all 18 rehearsal members are clean. Gate 7 is written
   as ruled. If a rehearsal member aborts or is dropped, the ruling does not say whether "12 used, fewer
   than 6 beyond the cap" passes.

5. **Main's copy of `tests/test_harvest_b5_window.py`.** The ruling puts the draft's section 4.7 list on the
   window side (section D, "What changes", item 5) and the new harvest tests on the harvest lane. That file
   is in the 4.7 list and also exists, 644 lines longer, on the lane. Section 4.7 says: on main only the
   fixed numbers change, and the lane's copy wins the merge conflict. That is this seat's reading of two
   statements of the ruling, not a sentence of the ruling.

6. **Predicted numbers.** The spans, deadlines, chain lengths and disk figures in R9 to R11 and R22 to R30
   are the drafting seat's arithmetic; the refuter reproduced them, and nobody has run the sizer. Rule 4 of
   section 4.5 makes the writer check each against the regenerated `sizing_b5.json` and stop on a
   difference.

## Lead's decisions on the seven open points (magistrate activation 1aed44f9, 2026-10-09 07:25 PDT)

1. **t at n = 11.** The ruling's rule item 4 prints 2.201 for n = 10, 11, 12 "2.262, 2.201, 2.201". The
   code's table (`joulewise/aggregate.py` lines 41 to 59) gives 2.262 at 9 degrees of freedom (n = 10),
   2.228 at 10 (n = 11) and 2.201 at 11 (n = 12). This is a slip of transcription in the ruling, not a
   ruling on the multiplier: the code is unchanged and governs, and the registration text states 2.228
   for n = 11. No further gate: no number a program computes changes.
2. **A stored bracket that carries a NEG-8 condition other than the two "underived" ones.** The sealed
   text (lines 2838 to 2840) says the window fails the screen; that stays. The desk builder's test must
   show a failure in that case. If the builder implemented "re-derives", the review returns it.
3. Lines 750 to 752 stay as dated history; lines 754 to 756 are edited. Accepted.
4. **The rehearsal's pass condition** is the rule, not the full count: the clean bound is built from the
   first 12 clean members in committed order when at least 12 are clean, from all of them when 10 or 11
   are, and the record lists the rest under `beyond_cap`. A rehearsal that keeps fewer than 10 has not
   exercised the path and is repeated.
5. On the merge of the harvest lane with the new seal commit, the lane's copy of
   `tests/test_harvest_b5_window.py` wins and the number edits are re-applied to it. Accepted.
6. The two status-line clauses the correcting seat added (R1, P1) stay.
7. The sizing figures in section 4.6 are predictions until the sizer has run; the builder's report
   replaces them, and the seal commit's text takes the sizer's output, not the prediction.
