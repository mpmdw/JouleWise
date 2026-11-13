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

---

# Second pass (2026-11-13)

Research lead (Fable 5.2). Written 2026-11-13 08:47 PST (`date`). Same rulings (RL-111 to RL-136), same terminology rule, same file and commit. New items are written against `origin/main` text, not against the builder's branch.

## Result

- **(a) 15 more changes can be made now** (A20 to A34). None needs an outcome.
- **(b) 2 more changes wait on a slot** (B8 on the Block 6 release, B9 on the S-14 cut).
- **5 more claims have no support** (U7 to U11). Four have a fix in (a). U8, the provenance of Figure B1, needs a check first.
- **A1 to A19 contradict nothing in the newly read ranges.** Two of them use words that the newly read methods text does not define, and one row of my first-pass table can be misread. The three amendments are under "Re-check of A1 to A19".
- **One new ruling is made in this pass and needs entering:** Tier E is retired (A32).
- **The two most important findings:**
  1. §4.8 as written gives the wrong outcome word for a contrast in a session with an undefined drift screen. A reader would take "not estimable"; the registered plan and RL-114 give "not resolvable". A7 and B3 depend on this (A26, A27).
  2. Figure B1's caption says the capture was re-derived under the current clock mapping. The figure file was last changed on 30 August 2026 and prints four values that the text still holds as placeholders (U8).

## What I read, and what I did not

**Read in full in this pass.**

- `paper1.md` lines 300-504 (§4.2 to §4.8) and 848-1010 (§6.2 to §6.6).
- `paper1.md` lines 1888-1971 (Appendix D). The file has 1,971 lines. My first-pass limits section stopped at 1887 and did not say that Appendix D was unread. It is read now.
- Re-read for cross-checks: lines 549-575 and 596-612 (§5.3, §5.4), 1010-1046 (§6.7), 1244-1252 and 1280-1291 (§7.3), 1856-1887 (Appendix C), and every figure caption (lines 289-294, 542-548, 614-626, 1174-1180, 1449-1455, 1850-1854).
- `variants/README.md`, `tierB_bytes_one_pass.md`, `tierD_bytes_registered_design.md`, `tierE_floor_version.md`, in full.
- `figures/build_figures.py` in full, and every text label of the five `fig_p1_*.svg` files and of `docs/paper/figures/fig4_edge_excursions.svg` (Figure B1).
- Rulings: RL-114, RL-121 (opening and ruling), RL-128 and RL-136 in full; the others by term. Decision log at `origin/audit/2026-11-10-fable` @ `fce872428`.
- `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` lines 345-358 and 416-436; `docs/registrations/block6_replication_DRAFT.md` lines 237 and 575-579.

**Arithmetic I checked, all consistent.**

- Table 2 per-token values; Table 3 against Table 4 through the guard factors and the allowance; Table S5 drift terms against Table S6; Table S7 corpus and reference counts; Table 5 decision intervals, per-token values and the size of both Holm-adjusted p-values.
- Every synthetic example in Appendix D.1 to D.6.

**Not checked.**

- `claims.py`, to confirm which reason code an undefined screen raises. A27 rests on RL-114's statement of the word and on the plan's list.
- Whether Figure B1 was regenerated after August (U8).
- The BYTES record behind Tier D's "nineteen" (U9).
- `fill_check_b5.py`, `licence_check_b5.py` and `build_fill_index.py`. Where an item changes a table header that a fill program may emit, the item says so.

**One action outside my file.** I ran `git fetch origin` in `/Volumes/JW-EXT/jw-wt/rs-main` to see whether the paper had moved. It updated that clone's remote-tracking refs. `origin/main` is now `32fd7c1e0`; nothing under `docs/paper/paper1/` changed between `62ca4197c` and it, so every line number stands. I should not have fetched in a shared clone without saying so first.

**Blind status.** Unchanged: blind to Block 6 and to v4. No custody, archive, session or outcome path was opened. I ran no analysis program and no test. Block-5-aware. I modified no file but this one.

---

## (a) Changes that can be made now

### Terminology

**A20. `paper1.md:432` (§4.6).** "Block" here means a quad (the code's word), which collides with A2.

- Current: "a sensitivity replay in which a block-level energy allowance derived from shared edge movements is applied with *one* sign across all quads,"
- Replacement: "a sensitivity replay in which each quad's energy allowance, derived from shared edge movements, is applied with *one* sign across all quads,"
- `n_b` in §4.3 stays; its words ("kept quads") define it.
- Follows from: Ed's terminology; analysis plan lines 351-352 ("an additive energy change of one shared sign across all kept quads").

**A21. `paper1.md:1869`, `:1858` and `:1713` (Appendix C; §9).** The registered Floor transfer sentence says "floor blocks" and "block timescale" for quads. It is quoted verbatim twice with no gloss. Line 942 already paraphrases it correctly with "quads".

- Line 1869: append after the closing quotation mark: " [block: a quad]".
- Line 1858, current: "The registered sentences say "window"; the body says "session" for the same thing." Replacement: the same sentence, followed by "One registered sentence says "block" for a quad; the body says "quad"."
- Line 1713, current: "calibrated on floor blocks transfers unchanged". Replacement: "calibrated on floor blocks [quads] transfers unchanged", in the style of line 379 ("members [runs]").
- Follows from: Ed's terminology; A2.

**A22. `paper1.md:896` (§6.3).** "Arm gate" is defined nowhere. "Armed" means allowed to start (§5.3), and A1 builds "session" on it.

- Current: "All four published floors of Table 3, which are the arm gates of the two contrasts, are attribution-limited"
- Replacement: "All four published floors of Table 3, which are the floor gates of the two contrasts' sides (Section 4.5), are attribution-limited"
- Follows from: Ed's terminology (one meaning for "armed"); §4.5 lines 410-413.

**A23. `paper1.md:887`, `:894`, `:1052`, `:416`; `fill_index.md:28`.** One name is used for two quantities. §4.5 line 404 defines the operative floor per form, before the guard and the allowance. Table 3's "Operative floor" column is the larger of the two forms after both, which §4.5 calls the floor gate. Table 5 prints the same numbers (10.18, 8.84) as "Floor gate".

- Line 887, header, current: "Operative floor (J)". Replacement: "Floor gate (J)".
- Line 894, current: "the operative column is the larger of those drift-widened values". Replacement: "the floor-gate column is the larger of those drift-widened values (Section 4.5)".
- Line 1052 and `fill_index.md:28`, current: "attribution floors, operative floors, dominance ratios". Replacement: "attribution floors, floor gates, dominance ratios". A9 edits a later clause of the same placeholder; the two do not overlap.
- Line 416, current: "and the resulting minted floor". Replacement: "and the resulting published floor". Lines 896 to 924 say "published".
- If a fill program emits the Table 3 header, change it there.
- Follows from: §4.5 lines 404 and 410-413 of the draft; Appendix D.4, which uses "operative floor" in the per-form sense.

**A24. `paper1.md:963` (§6.5).** A contrast is not a cell, and the minimum meant is the contrast's.

- Current: "each over 4 quads, one fewer than the cell minimum of 5;"
- Replacement: "each over 4 quads, one fewer than a contrast's minimum of 5 kept quads (Section 4.8);"
- It matters beside A7, which says a contrast with two to four kept quads is not estimable. The reader must see that this is the same minimum and that the leave-one-out check is exempt from it.
- Follows from: §4.3 ("reported cell") and §4.8 line 468 of the draft.

**A25. `paper1.md:969` and `:880` (§6.5, §6.2).** The same status has two labels, and one refusal has no reason.

- Line 969, current: "the registered pipeline could not compute this line; the independent recomputation's value, uncompared, is"
- Replacement: "the registered pipeline refused this line (refused, ⟨code from the ledger row⟩); the independent recomputation's value, recompute only; not compared, is"
- Line 880 already has both parts and does not change.
- The builder takes the code from the Block 5 ledger. If the pipeline has no such line and refused nothing, the clause reads "the registered pipeline does not print this line", and that comes back to me, because §5.3 promises the line.
- Follows from: §6.7 line 1014 ("carries its label where it is printed"); §8.2 control 6 ("refusals with reasons"). See U11.

### Block 6: words the comparison text needs from the methods

**A26. `paper1.md:457-458` (§4.7).** A7 and B3 say "a session whose drift screen is undefined". The methods text never uses the word.

- Current: "A session that fails is excluded; one that cannot compute the screen (too few survivors) cannot count."
- Replacement: "A session that fails is excluded. A session with too few clean corpus runs or too few surviving references has an **undefined** screen (Appendix D.6): it has no drift allowance, and it cannot count."
- Follows from: `block6_replication_DRAFT.md:237` and `:578` (N2: "no drift allowance, so no B and no floor"); RL-114.

**A27. `paper1.md:488-490` (§4.8).** The list is a simplification that sends a reader to the wrong word. A missing drift allowance reads as "a required input is missing", so not estimable. The registered precedence puts an unknown required error term in the not-resolvable set, and RL-114 records that the first program returns not resolvable for such a session, or not estimable below five quads.

- Current: "- **not estimable**: a required input is missing or invalid;" and "- **not resolvable**: there is no floor, or |d̄| does not exceed the floor gate, or the decision interval contains zero while the metrology interval does not;"
- Replacement: "- **not estimable**: a required input is missing or invalid, which includes fewer than five kept quads;" and "- **not resolvable**: there is no floor, or a required error term is unknown, or |d̄| does not exceed the floor gate, or the decision interval contains zero while the metrology interval does not. A session with an undefined drift screen (Section 4.7) has no allowance, so no deterministic bound D and no decision interval, and its contrast falls here;"
- Follows from: analysis plan lines 420-431 (`insufficient_complete_blocks` in the not-estimable set; `required_error_term_unknown` in the not-resolvable set); RL-114 ("What the code does", and fix item 2).
- Limit: I did not read `claims.py`. If the code raises a different reason for the same word, the first clause changes and the second stands.

### Results text

**A28. `paper1.md:856-863`, `:894`, `:938-946` (captions of Tables 2, 3 and 5).** The print rule is only in a source comment (line 721). A reader who computes m ± (h + B) from Tables 2 and S5 gets [23.33, 29.17] for 1.7B prefill; the table prints [23.32, 29.19].

- Add to the Table 2 caption, after "Interval = m ± (h + B) (Section 4.3).": "Means are rounded to nearest, interval ends outward and floors up, so a printed interval can be one last digit wider at each end than the printed terms give."
- Add to the Table 5 caption: "Interval ends are rounded outward."
- Add to the Table 3 caption: "Floors are rounded up."
- Follows from: RL-52 print-precision rule ("Estimates round to nearest. Interval ends round outward. Floors round up."), decision log line 2473. Tables S5 and S6 already state their rounding.

**A29. `paper1.md:386` and `:85-86` (§4.5, §1.3).** See U7.

- Line 386, current: "hence the smallest real difference the instrument can resolve."
- Replacement: "hence the smallest difference that this analysis will call resolved in that session."
- Lines 85-86, current: "and hence the smallest real difference it can resolve (Section 4.5);"
- Replacement: "and hence the smallest difference the registered analysis will call resolved in one session (Section 4.5);"
- The title is not changed. It asks the question; these two sentences answer it too strongly.
- Follows from: line 396 of the draft ("It is not a deterministic bound on future errors"); the Table 3 caption ("a property of this machine, stack, boundary and session").

### Figures

**A30. Figure 3: `figures/build_figures.py:76`, `:80`, `:94`; `paper1.md:622`.** The figure says "outcome" where it means an attempt's verdict. In this paper an outcome is a contrast's outcome word, which the blinding rule covers. The caption says the figure has "no outcomes" while the figure's title says outcomes are filled.

- Script line 76, current: "Order of collection (registered rotation; outcomes are filled from harvest records)". Replacement: "Order of collection (registered rotation; attempt verdicts are filled from harvest records)".
- Script line 94, current: "outcome: filled at release". Replacement: "verdict: filled at release".
- Script line 80, current: "re-arm a pack until claim-usable". Replacement: "re-arm a pack until it has an analysed session". "Claim-usable" is not defined in the body; §5.3 says "analysed session".
- Caption line 622, current: "Rows are rounds of the replication block;". Replacement: "Rows are the primary block and the rounds of the replication block;". The first row is the primary block.
- Regenerate `fig_p1_session_ledger.svg` from the script.
- Follows from: A19 (the rule names "outcome word"); §5.3 lines 571-574 of the draft.

**A31. Figure 5: `paper1.md:1451-1455`; `figures/build_figures.py:141`.**

- Caption, current: "Agents develop and review code in cloud and local sessions, run on the measurement laptop between sessions,"
- Replacement: "Agents develop and review code in the cloud and locally, run on the measurement laptop between sessions,". "Session" keeps one meaning, as in A12.
- Caption, append: "The analysis-host column shows the primary block. In the replication block the recomputation's functions print the numbers and a second side is compared with them (Section 5.7)."
- Script line 141, current: "collection: no agent alive". Replacement: "collection: no agent may be alive". The caption and the script's own comment (line 135) state a rule, not a fact; see U5.
- Regenerate `fig_p1_pipeline.svg`.
- Follows from: A1; A12; A14; RL-99.

Figures 1, 2 and 4 need no change. Figure 2's "settle" label agrees with A6, and its "about six hours" with A1 and A3.

### Variants

**A32. `variants/tierE_floor_version.md:3` and `variants/README.md:13`. Ruling, made in this pass: Tier E is retired.**

- Its condition is that the primary-block release slips. The primary block is released and §6 prints its values, so the condition cannot occur. The README says a tier is chosen "by date and by what has finished".
- Line 3, prepend to the comment: "Retired 2026-11-13: the primary block is released, so this tier's condition cannot occur. Historical template, not maintained."
- README line 13, "Use when" cell, current: "Primary-block release itself slips past about 20 November". Replacement: "Retired 2026-11-13: the primary block is released".
- The file's text is not edited. It holds three claims that are now false (U10) and uses "block" for a quad (line 53). Retiring it costs less than repairing it. Deleting it, with `fill_index.md` rows 100 and 101, is the lead's choice.
- Precedent: Tier B, which the decision log already calls a historical contingency template.

**A33. `variants/tierD_bytes_registered_design.md:41-42`.** Two phrases differ from §7.3 (lines 1248-1250) for the same fact.

- Current: "the HC3 intervals' plain 95% coverage in 400 synthetic campaigns per simulated world was at least 0.9475, above the registered floor of 0.93."
- Replacement: "in synthetic campaigns of 400 draws per simulated world, the HC3 intervals' plain 95% coverage was at least 0.9475 in every world and fit, above a pre-set floor of 0.93."
- "Registered" is the stronger word. The main text says "pre-set" and I found the value in no registration.
- Follows from: §7.3 of the draft.

**A34. `variants/tierB_bytes_one_pass.md:26`.** A stale reference, in a comment.

- Current: "the registration's per-model rule also appears in paper1.md §6.3." Replacement: "... in paper1.md §7.3." §6.3 is now "Detection floors".

---

## (b) Changes that wait on a slot

### B8. Figure 3 and `P1-LEDGER` (`paper1.md:622-625`; `build_figures.py:1`, `:17`, `:94`). Slot `B6-RELEASE`

When the attempt verdicts are filled, three statements stop being true together: the caption's "Schematic of the registered ordering, with no outcomes", the footer the script puts on every figure ("Schematic. No measured data"), and the script's first line.

- Fill rule: each cell takes a verdict word and a cause family only (as line 734 prints for the primary block). No outcome word, energy, floor or count of kept units enters the figure.
- Caption, replacement at the fill: "Figure 3. The registered ordering with each attempt's verdict. Rows are the primary block and the rounds of the replication block; cells are the attempts of each pack in the registered rotation, with BYTES sessions interleaved between rounds (Section 7.2). Verdicts are from the harvest records; the figure holds no energy."
- Footer for this figure only: "Attempt verdicts from harvest records. No energies; widths not to scale."
- The primary row could be filled today from line 734. I leave it with the rest so that the figure is generated once.
- Follows from: A19; A30; §5.3 ("Re-arming may depend only on structure").

### B9. Figure 5 label "synthetic full-size tests, CI" (`build_figures.py:138`). Slot `S14-CUT`

- Stands if B1 closes at N = 3 of 3 packs read at full volume by the pinned program.
- If N is below 3: "synthetic tests in production shape, CI".
- Either way the label does not claim a full-size closed loop; B1 and B2 say what was shown.
- Follows from: RL-98 term 3; RL-123 §1; RL-126 §1.

---

## Re-check of A1 to A19 against the newly read ranges

No first-pass edit contradicts §4.2 to §4.8, §6.2 to §6.6 or Appendix D. Three amendments, all to my own text:

**A7, amended.** It says "drift-screen run" and "screen run". §4.7 and Table S7 call these reference runs and corpus runs.

- In the inserted paragraph, current: "An excluded drift-screen run is read but is not a compared run, and its trace flags do not stop the comparison; a screen run that is not excluded stays a compared run,"
- Replacement: "An excluded reference or corpus run of the drift screen (Section 4.7) is read but is not a compared run, and its trace flags do not stop the comparison; a reference or corpus run that is not excluded stays a compared run,"
- "A session whose drift screen is undefined" stays. A26 defines it, and A27 gives the reason for the word that the second side requires.
- Follows from: RL-121 ("every start, midpoint and end reference on the roster, and every corpus run").

**A1, amended.** It defines a session as "one armed span" in §5.2, one section before §5.3 defines "armed".

- In the replacement, after "one armed span on the measurement laptop", insert "(armed: allowed to start, Section 5.3)".

**First-pass table, row RL-128.** I wrote "Paper 1's sessions ran without probes". Line 1008 prints "563 monitor probes inside target phases". These are different things: RL-128's is a remote status probe by a dedicated key, and line 1008 counts the hazard monitor's own samples. The row should read "Paper 1's sessions ran without status probes". If RL-128's probe ever reaches paper text it is called a "status probe", never a bare "probe".

**Checked and consistent, no change.**

| First-pass item | Newly read text | Result |
|---|---|---|
| A5 ("member runs") | Line 379, "kept members [runs]" | Agrees |
| A6 ("settle" is a duration) | Figure 2 label and caption | Agrees |
| A7 (two to four kept quads: not estimable) | §4.8 line 468; line 963 (leave-one-out over 4 quads) | Agrees once A24 and A27 are in |
| A7 (Holm with p = 1.0 for the short contrast) | §4.8 line 479 ("keeps the family size at two") | Agrees |
| A7, B7 ("not independently recomputed") | Lines 1008 and 1014 use the phrase for the primary block | Same meaning |
| A7 (scaled-allowance line) | Appendix D.6; line 1089 | Same line |
| A9 (Table 6 producer labels) | §6.2 to §6.5 quantities | Agrees; see A23 for one name |
| A14, A17 (what the recomputation covered) | Table S8 | Agrees |
| A19 (the rule) | Line 417 ("the blind ruling of 12 October") | Agrees |

---

## Claims in the newly read text that no ruling or record supports

**U7. `paper1.md:386` and `:85-86`.** "The smallest real difference the instrument can resolve."

- The floor is a threshold of one estimator in one session. Line 396 says it is not a bound on future errors, and the Table 3 caption ties it to the session.
- A larger real difference can still fail (the decision interval), and more units would lower the floor. Neither sentence can be shown.
- Fix: A29.

**U8. `paper1.md:1850-1854` (Figure B1).** The alt text says "re-derived with the current clock method"; the caption says "under the current clock mapping".

- `docs/paper/figures/fig4_edge_excursions.svg` was last changed on 30 August 2026 (`49b258d23`). §8.3 (line 1603) says the rate-aware design was only queued in August.
- The figure prints "59 of 59 are late", "49 of 59 are early", "+13 ms" and "−5.5 ms". Appendix B holds exactly these four as unfilled placeholders (DX-010 to DX-013), "re-derived under the current rate-aware mapping". If the re-derived values differ, the figure and the text will disagree.
- The figure also says "published bound" and "published B_fiducial = 30.07 ms", with a "1.13 ms clock-anchor term". These are the methods draft's terms, not this paper's.
- I did not verify either way. Before DX-010 to DX-013 are filled, the builder checks whether the figure was regenerated under the current mapping.
  - If yes: cite the generating commit in the caption's source comment. Nothing else changes.
  - If no: regenerate it from the same re-derivation that fills DX-010 to DX-013, or change the alt text and caption to "as drawn for the methods draft on 30 August 2026, under the clock mapping of that date; the values in the text are re-derived under the current mapping".
- Not counted in (a) because the check comes first. It needs no outcome.

**U9. `variants/tierD_bytes_registered_design.md:40`.** "Agreed on every printed field in nineteen synthetic agreement campaigns."

- The main text (§7.3, lines 1287-1290) states the agreement rule and no count. I found "nineteen" in no other paper or registration file.
- Fix when Tier D is used: cite the record, or drop the count and keep the rule. A33 covers the second sentence.

**U10. `variants/tierE_floor_version.md:40`, `:31-32`, `:43`, `:41-42`.**

- Line 40: "have been read by no person or agent". The universal negative of U1, and false for the primary block.
- Lines 31-32 and 43: "whose every output sentence was fixed before data"; "Every number they will print, and every sentence under each outcome, is fixed in the registrations". False for the replication since the §17 entries: the producer labels and the agreement counts were fixed after its collection.
- Lines 41-42 and 64: "the independent recomputation's agreement" for both blocks. Wrong for the replication (RL-99).
- Fix: A32 retires the file.

**U11. `paper1.md:969`.** "The registered pipeline could not compute this line." No reason is given. Line 880 gives the refusal code for the same kind of line, and §8.2 control 6 says refusals carry reasons. Fix: A25.

**Not verified in this pass, and not contradicted by anything I read.**

- `paper1.md:313`: 59 pulses of one second on a schedule of varied gaps.
- `paper1.md:896`: the floor source name `E_clock_anchor_shift_bound_j` and the class of all four floors.
- `paper1.md:1008`: the CPU-seconds and probe counts of the monitor-cost sentence.
- Tier D's and Tier B's BYTES statements other than U9 and A33. No ruling in RL-111 to RL-136 bears on them.

## Guards for later fills (no edit now), added in this pass

- Appendix C keeps "block" in the Floor transfer sentence, as it keeps "window". A21 glosses it; the sentence is not reworded.
- Run names such as `neg8-window-end-r2` (Table S7) and the code `whole_window_verdict_provenance_invalid` (line 880) are registered identifiers and stay.
- Table S4's caption says "plateau" of the battery-thermistor readings. That is a harvest flag of Paper 1. It is not the W1 gate, and B6's forbidden words do not apply to it.
- Tier C is covered by A18 and U2. Tier D and Tier B are BYTES-only apart from A33 and A34, and no "night" appears in any variant, figure or figure script.
