# Paper 1: methods-and-claims consistency pass against RL-111 to RL-133

Research lead (Fable 5.2). Written 2026-11-13 08:33 PST (`date`).

## Result

- **(a) 19 changes can be made now.** None needs an outcome.
- **(b) 7 changes wait on a slot.** Four wait on the S-14 cut, two on the Block 6 release, one on the W1 slot session.
- **The W1 gate rulings change no sentence of Paper 1.** The draft has no W1, thermal-gate or v4 text: §10 is an empty heading and RL-9 keeps ALIGN results out. RL-122 item 4 and RL-131 §3 item 5 bind the v4 manuscript and anything seat 13 writes in §10. Item B6 gives that text.
- **The Block 6 rulings are almost entirely missing from the draft, not contradicted by it.** The draft describes only the primary block's recomputation. It never says that a different program prints the replication's numbers, what the second side compares, or that those choices were made after the primary release. Most Block 6 items below are insertions.
- **Two new rulings are made in this pass and need entering in the decision log:** fixture cost is disclosed, in §8.3 only (B5); and the blinding sentence of §5.6 is reworded from a universal negative to the rule plus its recorded departures (A19).

## What I read, and what I did not

**Read.**

- `docs/paper/paper1/paper1.md` at `origin/main` @ `62ca4197c` (CANONICAL.md row "Paper 1 text"). All line numbers below are in that file at that commit.
  - Read in full: lines 1-300, 504-848, 1010-1887.
  - Searched by term only, not read: lines 300-504 (§4.2-§4.8) and 848-1010 (§6.2-§6.6).
- `variants/tierC_block6_addendum.md` in full; `fill_index.md` rows 26 and 27; `OUTLINE-MAP-2026-11-11.md` by term.
- RL-111 to RL-133 in full, on `origin/audit/2026-11-10-fable` @ `8137f18e7`. Also RL-9, RL-48, RL-98, RL-99, RL-101, RL-102, RL-110.
- `docs/registrations/block6_s17_entries_DRAFT_2026-11-10.md` (R0 to R3, R12), DLE-2, and the pin paragraph files `fable-s14-pin-paragraph.md` and `fable-rl126-proportionality.md` §4.

**Not checked.**

- The other variants (tiers B, D, E) and the figures.
- Whether the pinned program's final bytes behave as RL-133 rules. The fix delta was still in review when I wrote this.
- The terminology rule is taken from the brief. I found no committed record of it.

**Blind status.** Blind to Block 6 and to v4: no custody, archive, session or outcome path was opened. I ran no program and no test. Block-5-aware. I modified no file but this one.

## Slots used in part (b)

| Slot | Closes when | Outcome-bearing |
|---|---|---|
| `S14-CUT` | The three full archives are re-read on the final bytes, the closed nine and denied-26 are read, PR #748 is merged and S-14 is cut | No. Synthetic sessions only |
| `B6-RELEASE` | The real block run has exited and Block 6 is released | Yes |
| `W1-SLOT` | The slot session's desk table and floor census exist and no trigger T1 to T4 fired (RL-131 §2 item 5) | No. Rehearsal temperatures only |

---

## (a) Changes that can be made now

### Terminology (Ed, 2026-11-13: session, block, no "night")

**A1. `paper1.md:533-534` (§5.2).** The definition does not say a session is an armed span, never names member runs, and states "no AI agent process on the machine" as a fact, which §8.3 contradicts.

- Current: "A **session** is one unattended collection of a whole pack on the laptop, of roughly six hours, with no other workload and no AI agent process on the machine."
- Replacement: "A **session** is one armed span on the measurement laptop: one unattended collection of a whole pack, of roughly six hours. Its runs are its **member runs**. No other workload is permitted, and a live AI agent process is treated as a hazard (Sections 5.3 and 8.3)."
- Follows from: Ed's terminology; §8.1 and §8.3 of the draft, which record agent processes during sessions.

**A2. `paper1.md:551` (§5.3).** "Block" is used from the abstract on and never defined.

- Current: "The primary block (registered internally as measurement block 5) collected one analysed session of each pack."
- Replacement: "A **block** is a registered set of sessions. The primary block (registered internally as measurement block 5) collected one analysed session of each pack."
- Follows from: Ed's terminology.

**A3. `paper1.md:578` (§5.4).** A time-of-day word, and wrong for one of the three analysed sessions (line 736: the contrast session started 04:20 UTC, which is 21:20 local).

- Current: "A single session says how much a number moves from run to run on one afternoon, and nothing about whether it holds on another day."
- Replacement: "A single session says how much a number moves from run to run within about six hours, and nothing about whether it holds on another day."
- Follows from: Ed's terminology; line 736 of the draft.

**A5. `paper1.md:248` and `:250` (§3.4, Table S1).** "Member window" is defined nowhere, and the counts are counts of runs.

- Current (248): "over the model's member windows" and "No member window fell outside the hard plausibility band".
- Replacement: "over the model's member runs" and "No member run fell outside the hard plausibility band".
- Current (250, table header): "Member windows". Replacement: "Member runs".
- Follows from: Ed's terminology; §3.2 defines ρ "for each run".

**A6. `paper1.md:534` (§5.2).** "Settle" is the registered name of a fixed wait. Beside the RL-131 rule against settled-start wording it reads as a claim about the machine's state.

- Current: "a 60 s settle;"
- Replacement: "a fixed 60 s idle wait (registered as the settle; it is a duration, not a test of the machine's state);"
- Follows from: RL-131 §3 item 5, applied by analogy; `block6_replication_DRAFT.md:317-318` ("*settle* is a 60 s idle wait"). The Figure 2 caption keeps the name.

**A10. `paper1.md:1462` (§8.1 table, primary-block row).**

- Current: "installed two launchd jobs: a night job that started the session program at a calendar t0, and a dead-man job."
- Replacement: "installed two launchd jobs: a launch job that started the session program at a calendar t0, and a dead-man job."
- The job labels in the FACT S9-02 comment (`com.joulewise.night`) are code literals and stay.
- Follows from: Ed's terminology.

**A11. `paper1.md:1468-1469` (§8.1).**

- Current: "whether to run, re-run, schedule and arm measurement windows passed to the headless supervisory agent on 6 November 2026, after all three collections had closed. It covers a later study's windows on the same laptop, not these collections."
- Replacement: the same two sentences with "measurement sessions" and "a later study's sessions".
- Follows from: Ed's terminology; line 1858 of the draft ("the body says 'session'").

**A12. `paper1.md:1551` (§8.3).**

- Current: "In other windows on the same laptop, agent sessions alive at t0 caused refused arms with nothing captured."
- Replacement: "In other measurement sessions on the same laptop, agent processes alive at t0 caused refused arms with nothing captured."
- "Agent sessions" becomes "agent processes" so that "session" keeps one meaning in the sentence.
- Follows from: Ed's terminology.

**A13. `paper1.md:1616-1618` (§8.3).**

- Current: "On a later study's night on the same laptop, the session program refused before measuring, because a directory it needed had been created with the wrong owner. The night's top-level result still read GO"
- Replacement: "In a session of a later study on the same laptop, the session program refused before measuring, because a directory it needed had been created with the wrong owner. The session's top-level result still read GO"
- `night/result.json` in the FACT S9-06 comment is a path and stays.
- Follows from: Ed's terminology.

**A16. `paper1.md:1832` (Appendix A).**

- Current: "| Pack; session; attempt | Frozen plan for one session; one unattended collection; one try at a session (5.2, 5.3) |"
- Replacement: "| Block; pack; session; member run; attempt | A registered set of sessions; frozen plan for one session; one armed span on the laptop, an unattended collection of a whole pack; one run of a session; one try at a session (5.2, 5.3) |"
- Follows from: Ed's terminology.

### Block 6: what the comparison is, stated as design

**A4. `paper1.md:579-580` (§5.4).** True as written, and now incomplete. The collection design predates every primary number. The printing program, the comparison's precision and coverage, and the fixture entry were decided after the primary release.

- Current: "The replication block (registered internally as block 6) was designed before any primary-block number was seen, so that it would be collected whatever the primary block showed."
- Replacement: "The replication block (registered internally as block 6) was designed, registered and collected before any primary-block number was seen, so that it would be collected whatever the primary block showed. Which program prints its numbers, and how agreement with a second computation is shown, were fixed later, by dated entries made after the primary release and labelled as decided after primary-block outcomes were known (Sections 5.5 and 5.7). No entry changes the registered arithmetic."
- Follows from: §17-R0 (RL-25 flag 5, RL-30 S17-01); §17-R1; RL-98 term 3; RL-126 (the option table's prereg column).

**A7. `paper1.md:711` (§5.7): insert two paragraphs after "Part 2 uses an independent **twin** (Section 7.3)."** The section says nothing about the replication's comparison except its bar.

- Current text: none.
- Insert:

> **Replication block.** A different program prints the replication block's numbers. The printing program, here the *first program*, is the lean recomputation; it loads the primary block's recomputation functions, pinned by digest. The *second side* is a harvest twin, a contrast-engine twin, a checker for counting, floor pairing and the between-session arithmetic, and a reducer cross-check. Exclusions are re-derived from the stored flags under the replication catalog, which, as in the primary block, is not an independent detection of the hazards. The heavy registered pipeline was not run as an audit for this block.
>
> The comparison is made over the second side's keys only. A quantity that only the first program prints is not compared and not counted: it is recorded as *first-program-only*, with a count per class beside the compared, passed, failed and unmatched counts, and it does not change the verdict. A key that only the second side holds, with a value, fails. A row where both sides hold no value passes and is counted separately as *null on both sides*; that is agreement that a quantity is absent, not agreement on a number. Agreement is therefore stated over compared rows only, with those two counts beside it, and the rows agreeing on a value are the compared rows minus the null-on-both-sides rows. A class with no compared row carries no verdict. An excluded drift-screen run is read but is not a compared run, and its trace flags do not stop the comparison; a screen run that is not excluded stays a compared run, and a missing trace on it stops the comparison. A pinned input or a pinned session that is not supplied refuses the run by name.
>
> The second side has limits that are fixed by design. The cell and floor estimators of the two floor packs, and the dominance ratios copied from their output, have one producer in this block and print with the label *single-source*; the same pinned functions agreed with the registered analysis on the primary block in every compared family (Table S8). The labelled lines that rerun the estimators on another unit set, the scaled-allowance and single-step lines, the per-phase whole-machine line, and a contrast's ratio, per-token, t and cross-session fields print as *not independently recomputed*. For a session whose drift screen is undefined, the second side compares neither the screen row nor any contrast field, and requires only that the outcome word is not resolvable or not estimable. For a contrast with two to four kept quads it compares the count, the mean difference, its spread and the bounds; it does not compare p or the Holm-adjusted p, and requires that both are 1.0 and the word is not estimable. The Holm value of that session's other contrast is computed on both sides with p = 1.0 for the short one. Two inputs are shared and not independent: the engine twin is given the first program's floor gate, and the block check takes primary-block inclusion and the floor-binding defect mark from the first program.

- Check at `S14-CUT`: read these paragraphs once against the final pin paragraph. If a closure byte changed the behaviour, the text comes back to me.
- Follows from: §17-R1, §17-R2, §17-R3; RL-99; RL-101; RL-102; RL-110 term 4; RL-113; RL-114; RL-115; RL-121; RL-133 §1 and §2.

**A8. `paper1.md:715` and `fill_index.md:26` (placeholder `P1-RECOMPUTE`).** The spec asks for a family table with an agreement word for both blocks. Block 6 has classes, and a class with no compared row has no word.

- Current: "per block and compared family: applicable bar, number compared, observed largest difference and agreement word; name uncovered quantities and their separate reader checks; Block 5 uses recompute_bars.json fixed blind under DLE-0, Block 6 uses §12.3; checked by one executing reader before printing"
- Replacement: "Block 5, per compared family: applicable bar (recompute_bars.json, fixed blind under DLE-0), number compared, observed largest difference and agreement word. Block 6, per class: the S-13 bar (1 mJ for run phase energies, half a last printed digit otherwise), then compared, passed, failed, unmatched, null on both sides, agreeing on a value (compared minus null on both sides) and first-program-only; no agreement word for a class with no compared row. Both: name uncovered quantities and their separate reader checks; checked by one executing reader before printing"
- Follows from: RL-113 term 6 as amended by RL-133 §2; RL-133 §1c.

**A9. `paper1.md:1052` (placeholder `P1-B6-SIDEBYSIDE`).** Table 6 would print replication values with no producer label.

- Current: "...each counting replication session's value with interval, kept units, flags and its floor pairing (including any "floor from the primary block"); ..."
- Replacement: "...each counting replication session's value with interval, kept units, flags, its floor pairing (including any "floor from the primary block") and its producer label from the registered printed-quantity table (computed and compared; single-source; not independently recomputed; or the conditional label with the clause that applied to that session); ..."
- Follows from: RL-99 item 1; RL-101; RL-110 term 4; RL-114; RL-133 §1a (labels).

**A14. `paper1.md:1524-1526` (§8.2, control 5).**

- Current: "**Independent recomputation and a twin.** Separate code recomputes the primary block's core arithmetic with recorded collection-time judgments as inputs; uncovered quantities require separate checks (Section 5.7). BYTES requires agreement with its independent twin (Section 7.3), against a tolerance fixed in advance."
- Replacement: "**Independent recomputation and a twin.** Separate code recomputes the primary block's core arithmetic with recorded collection-time judgments as inputs; uncovered quantities require separate checks (Section 5.7). In the replication block that recomputation's functions print the numbers, and a second side of twins and a checker covers named families only; the floor-pack cell and floor estimators have one producer there and are labelled so (Section 5.7). BYTES requires agreement with its independent twin (Section 7.3), against a tolerance fixed in advance."
- Follows from: §17-R1; RL-99; RL-101.

**A15. `paper1.md:1702` (§9): insert a limitation after "Counter gain."**

- Current text: none.
- Insert: "**Replication comparison.** In the replication block the cell and floor estimators of the two floor packs have no second producer; they were compared on the primary block only. The second side covers counting, calibration, run phase energies, harvest bounds, the drift screen, the contrast engine, floor pairing and the between-session arithmetic. Its agreement counts cover compared rows only, and some compared rows agree that a value is absent, not on a number (Section 5.7)."
- Follows from: RL-48 F10; RL-99 item 2; RL-113; RL-133 §1c.

**A17. `paper1.md:1836` (Appendix A).** "Sharing nothing" is false for the replication block (RL-133 names two shared inputs, and the floor estimators have one producer). For the primary block it leaves out the shared inputs that §5.7 states.

- Current: "| Independent recomputation; twin | Second computation of headline numbers by code sharing nothing with the analysis (5.7, 7.3) |"
- Replacement: "| Independent recomputation; second side; twin | Primary block: a second computation of the core arithmetic by separate code, with recorded collection-time judgments as inputs. Replication block: the twins, checker and reducer cross-check set against the printing program; it covers named families only and takes two named inputs from that program. BYTES: a second implementation written from the registration (5.7, 7.3) |"
- Follows from: RL-99; RL-102; RL-133 §2 (inserted pin paragraph).

**A18. `variants/tierC_block6_addendum.md:24`, `:26`, `:40`.** Three statements that the rulings make wrong.

- Line 26, current: "because every replication rule was fixed before the primary block was released,"
- Replacement: "because the replication's counting rules, estimators and agreement word were fixed before the primary block was released, and the entries made after that release change which program prints and how agreement is shown, not the registered arithmetic,"
- Line 24, current: "(primary release done, blind dry run complete, independent recomputation agreeing)". Replacement: "(primary release done, blind dry run complete, second-side comparison agreeing)".
- Line 40, current: "recomputation's agreement table". With line 39 this reads "with the independent recomputation's agreement table". Replacement for the phrase across both lines: "with the agreement table of its second-side comparison (Section 5.7)".
- Follows from: §17-R0 ("Decided after Block 5 outcomes were known"); §17-R1; RL-99.

**A19. `paper1.md:666-667` (§5.6).** See "Claims no ruling or record supports", item U1. Listed here because it can be made now.

- Current: "From each block's first session until its release, no person or AI agent read a measured energy, power, phase duration, floor, ratio, contrast, outcome word or calibration value."
- Replacement: "The rule for each block, from its first session until its release, is that no person or AI agent reads a measured energy, power, phase duration, floor, ratio, contrast, outcome word or calibration value. Two recorded departures are stated below and in Section 8.2. For the replication block, which is not released, this is the rule in force, not a completed record."
- Follows from: a ruling made in this pass (to be entered). Supported by §5.6 paragraph 2 and §8.2 control 2 of the draft, which already disclose the two departures.

---

## (b) Changes that wait on a slot

### B1. `paper1.md:659` (§5.5): the replication block's change history, with the RL-98 term 3 departure. Slot `S14-CUT`

The section lists only the primary block's history. Insert after "...cannot be hidden by saying that the estimators were unchanged." and before the FACT H09 comment.

- Current text: none.
- Insert:

> The replication block's registration was changed by a set of dated entries in its change log, entered on ⟨S14-CUT: date PR #748 merged⟩, after the primary release. The set carries one framing line: the planned deadline, before the primary release, was not met, and the entries were decided after primary-block outcomes were known. Each entry names its kind, and none changes registered arithmetic. They name the printing program and the second side (Section 5.7), make the comparison's printed precision definite, label every printed quantity by its producers, record that the heavy registered pipeline was not run as an audit, and require production-shaped synthetic sessions to pass through the analysis before its commit is fixed (Section 5.6). One entry is a departure from the registered release procedure: "full-size ... through the real stage chain" was shown on single-pack synthetic sessions for ⟨S14-CUT: N⟩ of 3 packs, not on a closed nine-session loop; reader volume was also shown by a direct test at production size; and the first real-size run of the whole program over a closed block was the blind dry run. It changes no arithmetic and nothing about blinding.

- Predicted: N = 3. N counts only archives read by the pinned program (RL-123 §2 item 5).
- Follows from: RL-98 term 3; RL-123 §1; RL-126 §1; §17-R0; RL-25 flag 5 ("Paper 1's deviation list names it").

### B2. `paper1.md:685` (§5.6): the fixtures preceded the cut, and what the closed nine does not show. Slot `S14-CUT`

Insert as a new paragraph after "...with hidden multiplicative offsets (Section 7.3)." and before the FACT H11 comment.

- Current text: none.
- Insert:

> For the replication block the analysis program was fixed by commit (⟨S14-CUT: S-14 commit; program SHA-256⟩) before it read any replication custody path. Before that commit was fixed, as the registration requires, synthetic sessions written by the collection chain's own code, with only the instrument sources simulated, were generated and read by the program. They cover six registered shapes: runs that waited for idle admission, wait-cap and budget skips, runs with an unbounded clock anchor, campaign logs that mix member-run rows with the trailing whole-session row, compressed logs and sampler files, and one contrast unit spanning two sessions. There is one further fixture in which a simulated host action is denied, and one closed loop of nine counting sessions. The closed nine is a reduced-volume cohort: its ordinary sessions carry 65 s streams, so its equality of serial and pooled outputs, its wall time and its peak memory are reduced-volume results. No full-volume session went through a closed loop. Full volume through the real chain was shown on single-pack sessions, one per pack, ⟨S14-CUT: N⟩ of 3 packs read by the pinned program (⟨n⟩ generated on the analysis laptop, ⟨n⟩ on the measurement laptop, all read on the analysis laptop); they were not assembled into a loop. Section 5.5 records this as a departure.

- Predicted: N = 3; 1 generated on the analysis laptop, 2 on the measurement laptop.
- If the closed nine is lost or a slot departs from its predeclared value, this paragraph comes back to me.
- Follows from: §17-R12; RL-48 F1; RL-49 item 2; RL-123 §1 ("What (a) does not show"); RL-126 §1 items 1 to 4 and §4 (iii); RL-129 §7 item 2.

### B3. `paper1.md:1045` (§6.7) and `fill_index.md:27`: the agreement paragraph (`P1-RECOMPUTE-SUMMARY-B6`). Slot `B6-RELEASE`

- Current: "{{FILL: P1-RECOMPUTE-SUMMARY-B6 | the replication block's paragraph: compared families and counts, largest differences against that block's applicable bars (Block 6 §12.3), uncovered quantities and separate reader checks; any disclosed repair with its date and effect}}"
- Replacement, as final text with slots:

> **Replication block.** The second side (Section 5.7) was set against the printing program over ⟨k⟩ counting sessions, under the bars registered for this block: 1 mJ for run phase energies and half a last printed digit for printed quantities. The comparison exited ⟨exit⟩. Of ⟨compared⟩ compared rows, ⟨failed⟩ failed and ⟨unmatched⟩ were unmatched. ⟨both_null⟩ of the compared rows are null on both sides, which is agreement that a quantity is absent; ⟨compared − both_null⟩ rows agree on a value. A further ⟨first_program_only⟩ rows were printed by the first program only and were not compared; every one carries a label that allows non-comparison (Table ⟨n⟩). This is not a statement that every class passed: ⟨classes with no compared row⟩ classes have no compared row and carry no verdict. The cell and floor values of the two floor packs are single-source in this block: the same pinned functions agreed with the registered analysis on the primary block in every compared family (Table S8), and the second side agreed here for counting, calibration, run phase energies, harvest bounds, the drift screen, the contrast engine, floor pairing and the between-session arithmetic. ⟨Per session with an undefined drift screen, and per contrast with two to four kept quads: the session, and the sentence "its screen row and contrast fields (or: its p and Holm-adjusted p) were not compared; the outcome word was checked against the registered word for that state".⟩ ⟨Any refusal met on the run, by name or signature; any disclosed repair with its date and effect.⟩

- Rules for the fill:
  1. The three numbers are the totals of `compared`, `both_null` and their difference, taken from the public comparator (RL-133 §2, checklist step 2).
  2. The RL-113 term 7 label check, steps 1 to 13, is run on the restricted output before this paragraph is written. A stop comes to me.
  3. The clause "the second side agreed here for ..." is printed only for families whose class has `pass` true and `compared` above 0. A family with no compared row is dropped from the list and named.
  4. The paragraph does not use "independent recomputation" for this block.
- Follows from: RL-113 terms 6 and 7; RL-133 §2; RL-99 item 2; RL-110 term 4; RL-114 ("Paper"); RL-125 items 1 and 3.

### B4. `paper1.md:1527-1529` (§8.2, control 6): the known refusals. Slot `S14-CUT`

The heading "Fail-closed refusals with reasons" is true of the primary block's analysis and overstated for the replication's pinned program.

- Current: "**Fail-closed refusals with reasons.** In the primary block's registered analysis, a refusal at any step stops the steps after it. A tooling refusal is repaired blind and the step re-runs on identical bytes; a refusal that is a registered scientific outcome is the result and is printed as such."
- Replacement: the same text, followed by: "The replication block's pinned program stops without a named reason in three known cases, and writes no output in any of them: a run's idle sampler file absent, a pinned clock journal absent, and a pooled worker process that died. The first two mean the archive changed after its custody check. Each is read as a refusal: any exit other than success or a recorded disagreement is one, and the program is not edited on the real run."
- Waits on the cut because RL-133 §4 item 5 allows a further finding to change a closure byte. If the list of three changes, this text changes with it.
- Follows from: RL-125 item 4 (terms 2 and 4); RL-129 §1 term 2 (the fourth case, a missing copied record, was given a named refusal before the pin); RL-133 §1e LOW-3 and §2 ("Unnamed refusals").

### B5. `paper1.md:1544` and `:1631` (§8.3): fixture cost is disclosed. Slot `S14-CUT`

**Ruling, made in this pass (RL-127's question).** Yes, the paper discloses the fixture's cost, in §8.3 only, as one bullet. It is not methods and it enters no result. §8.3 exists for failures that cost time, the closed nine was forecast at about twelve hours against a predicted read of about 25 minutes, and the cause was mine (RL-126: "What I got wrong in RL-123"). The budget table of RL-127 and RL-132 stays out of the paper; one sentence states the rule.

- Line 1544, current: "The record runs to 10 November 2026." Replacement: "The record runs to 13 November 2026."
- Insert a new bullet after the "Analysis runtime is a defect" bullet and its FACT S9-07 comment (after line 1637):

> - **A rehearsal can cost far more than the analysis it rehearses.** The closed loop of nine synthetic sessions that the replication's analysis had to read before its commit was fixed (Section 5.6) took ⟨S14-CUT: generation wall⟩ to generate on the analysis laptop. The analysis read it in ⟨S14-CUT: serial read wall⟩. The time went to the collection chain's own waits and session rotation, not to data volume, so reducing the sessions' streams to 65 s saved little; a profile of one session before launch would have shown that. The fixture was kept because the registration fixes its place before the analysis commit, and because it was the only evidence for four of the six registered shapes, the closed loop, block arithmetic over more than one session, and the equality of serial and pooled outputs. Since 13 November 2026 one rehearsal attempt is budgeted at four times the wall time of the analysis it rehearses, and at most four hours; a longer one is profiled and ruled on before it starts.

- The existing "Analysis runtime" bullet is not changed. Its figures (27.1 h, 1 h 46 min) stay as they are, so the job-hunt handoff needs no notice.
- If the nine fails or is retired, the bullet comes back to me before it is used.
- Follows from: RL-126 §1 ("What I got wrong"), §2 and §4 (iii); RL-127 terms 1 and 3; RL-132 §2.

### B6. `paper1.md:1741` (§10, empty): the W1 gate, only if seat 13 describes the v4 design. Slot `W1-SLOT`

The draft has no sentence on the W1 gate, so nothing is wrong today. This item binds whatever is written. Paper 1 needs no gate description; RL-9 limits §10 to the v3 pilot as motivation, with its limits in the same sentence. If seat 13 chooses to describe the v4 measurement design, the gate is described in these words and no others:

> Before each gated member run, a gate waits until the die temperature is no more than 1.0 °C above a per-session reference and the machine reports no thermal throttling. Before each later agent turn in the gated condition, it waits until the die temperature is no more than 1.0 °C above its value when that run was released. The gate reads one die sensor. Its second channel is the same sensor's reading, rounded down to a multiple of 5 °C while the die cools above 35 °C, and adds no temperature constraint. The gate makes no claim that the machine has stopped cooling when a run starts: it can release while the die temperature is still falling. The heatsink is not held by the gate. The fixed schedule between member runs sets its start state, and its temperature is recorded in every gated member run and compared between conditions as a disclosure.

- Forbidden wording, wherever the gate appears: "settled", "settled start", "slope-controlled", "two thermometers", "two sensors", "the heatsink was controlled" or "held". The reference is an "upper guard", never a "target" (RL-117).
- The delivery check, if mentioned: "The delivery check confirms that the per-turn gate ran in the gated condition; it does not show a temperature difference between conditions." An equivalence verdict is worded as "the gate as run, with these waits and this turn-start difference, did not change turn energy by more than 6 J", never as "thermal start state does not matter" (RL-122 item 4). That sentence is a v4 result and does not appear in Paper 1.
- Waits on `W1-SLOT` because RL-131 §3 item 3 confirms the floor wording on gated member runs only after the slot session's floor census. If trigger T1 or T2 fires, or the role swap of RL-131 §2 item 6 is taken, the second and third sentences change and the text comes back to me.
- Terminology: "slot-producing night" and "R1 follow-up night" in the rulings become "the slot session" in any paper prose.
- Follows from: RL-122 §1 and items 2 and 4; RL-131 §1 and §3 items 3 and 5; RL-117; RL-9.

### B7. `paper1.md:1050` (§6.8): the sentence beside the single-source labels. Slot `B6-RELEASE`

Insert after "...with each session's interval, kept units and flags."

- Current text: none.
- Insert: "Each replication value carries its producer label. The values labelled single-source, the cells and floors of the two floor packs and the dominance ratios copied from them, were computed by one program in this block; what stands behind them is stated in Section 6.7. A value labelled not independently recomputed was computed once and checked by a separate reader against the released records."
- The last sentence is kept only if that reader check was done for Block 6 and is recorded. Otherwise it reads: "A value labelled not independently recomputed was computed once."
- Follows from: RL-99 items 1 and 2; RL-101; RL-102 ("no claim word rests on one of them without its label").

---

## Claims in the draft that no ruling or record supports

**U1. `paper1.md:666-667` (§5.6).** "no person or AI agent read a measured energy, power, phase duration, ... or calibration value."

- It is a universal negative. No record can establish it, and the next paragraph and §8.2 control 2 disclose two departures, one of them a timing read.
- For the replication block it is also stated in the past tense about a period that has not ended.
- Fix: A19.

**U2. `variants/tierC_block6_addendum.md:35`.** "No replication energy, floor, ratio, contrast estimate or outcome word has been read by any person or agent."

- The same problem. Replacement: "Under the block's rule no replication energy, floor, ratio, contrast estimate or outcome word may be read before its release, and the project record shows no such read."
- Not counted in (a). It is used only if tier C is used.

**U3. `paper1.md:1836` (Appendix A).** "code sharing nothing with the analysis". Fix: A17.

**U4. `paper1.md:578` (§5.4).** "on one afternoon". Contradicted by line 736 for the contrast session. Fix: A3.

**U5. `paper1.md:533-534` (§5.2).** "no AI agent process on the machine", stated as a property of a session. §8.3 records sessions in which one was present. Fix: A1.

**U6. `variants/tierC_block6_addendum.md:26`.** "every replication rule was fixed before the primary block was released". False since the §17 entries. Fix: A18.

**Not verified in this pass, and not contradicted by anything I read.**

- `paper1.md:1287`: the BYTES twin "written from the registration alone and sharing no code with it". I did not check it against the BYTES record.
- `paper1.md:590-591`: "Twenty-five of the primary block's 32 session-removing codes became flags only."
- Every claim in lines 300-504 and 848-1010, which I searched by term and did not read.

---

## Rulings in the range that change nothing in Paper 1

| Ruling | Why no change |
|---|---|
| RL-111, RL-112 | W1 signing evidence. No paper text |
| RL-116 to RL-120, RL-124 | W1 route, High Power, planning turns. v4 only; covered by B6 if §10 describes the design |
| RL-128 | The probe count goes in the v4 methods. Paper 1's sessions ran without probes |
| RL-130 | A side branch. Gates nothing |
| RL-132 §1 | A process-wrapper record. No analysis quantity |
| RL-125 item 2 | Copied-record file names. A pin-request matter; it reaches the paper only if a family fails RL-104 check 3 |
| RL-129 §6 | The three items that bind a read to the pinned closure. They belong in the `P1-RELEASE` and `P1-AVAIL` fills at `B6-RELEASE`; the placeholders need no change now |

## Guards for later fills (no edit now)

- When Block 6 releases, the abstract fill `P1-ABS-PART1` and conclusion branch 9.C must not call the replication's check an "independent recomputation". The phrase stays with the primary block.
- `paper1.md:162` and `:1109` use "blocks" for a model's expert weight blocks. That is a different sense and I leave it, since the two cannot be confused in context.
- Appendix C keeps "window" inside the registered sentences. Line 1858 already says so.
