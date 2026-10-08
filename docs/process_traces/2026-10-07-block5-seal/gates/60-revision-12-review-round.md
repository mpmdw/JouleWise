# Registration revision 12: the review round (two reviewers, one revision; 2026-10-07)

## What this record is

The **registration** of measurement block 5 (`configs/campaigns/v5_claim_25g83/registration_block5.md`) is the
document that fixes, before any data exists, what the block's three measurement windows measure and which recorded
conditions remove data. The **analysis plan** and the **flag catalog** beside it fix how the numbers are computed
and what each recorded condition does. Revision 12 of the registration and the plan is the revision that was
sealed.

Revision 12 was written on 2026-10-07 by five writers, each on one region of the text, and merged. It had to carry
48 changes that the judge of the seal gate's first stage had written out word for word (the ruling numbers them
T-1 to T-48), and new text for sections 2, 11 and 12. Before the seal gate's second stage read it, the merged text
went through one review round of two reviewers and one reviser, as the workflow `wf_1461d6ae-369`:

- The **verbatim reviewer** (Opus 5.5) checked that each of the 48 changes stands in the text exactly as the judge
  wrote it, in the section the judge named, and that the new sections agree with the code. It found no blocker:
  one MAJOR finding, four MINOR and five notes.
- The **pedagogy reviewer** (Opus 5.5) read only the text the writers themselves had added and checked that every
  term is built before it is used and that every count adds up. It found five MAJOR findings, fifteen MINOR and
  four notes.
- The **reviser** (Opus 5.5) applied all of them and returned the text at commit `f7c643457` of the design branch
  `design/2026-10-05-v5-claim-block-draft`, with two cures marked for the orchestrator's ruling.

None of the three seats wrote a file for its result; each returned it to the workflow. This record was made from
the workflow's journal on 2026-10-08 by the seat that assembled the seal's record commit. Line numbers in the
findings are those of the reviewed commit `7e5eaa6c9`, not of the sealed text.

Source of all three parts: the workflow journal `/Users/edr/.claude/projects/-Users-edr-code-JouleWise/e4fc0437-3e56-4860-a119-d14d766031f7/subagents/workflows/wf_1461d6ae-369/journal.jsonl` (SHA-256 when this record was written: `b367c257ad54ec8552d20d4d0aeaa9032e90d81ac8a29354c8cfd25bbc4e9d1d`), rows 16, 15 and 18 counting from 0. The text under each heading is the seat's own, whole and unchanged. Only the headings and the bold labels were added.

## Part 1. The verbatim reviewer (agent `a9348f7c5d934a9e1`)

- **Reviewer:** Verbatim reviewer (Opus 5.5), registration revision 12, read-only
- **Reviewed head:** 7e5eaa6c938c67aa402c8f857be03199739ba2c5
- **T items checked:** 48

Findings (10):

### V-0 (NOTE)

**Document.** registration_block5.md, analysis_plan_block5.md, flag_catalog.json

**Where.** whole documents at 7e5eaa6c9 (registration SHA-256 5b0a7870..., plan 56a304ec..., both recomputed)

**What.** Overall result: no BLOCKER. No ruling is weakened, paraphrased, misplaced or missed in the judge's text. Sections 2, 11 and 12 agree with SEAL_LANDING.md, REGISTRATION_FACTS facts 1 to 24 and table D, and with the code at the integration head cc0b3446d, except the one count in V-2.

**Evidence.** Own parser and checker (not the merger's): /private/tmp/claude-501/-Users-edr-code-JouleWise/e4fc0437-3e56-4860-a119-d14d766031f7/scratchpad/verbatim/parse_t.py and check_t.py. All 48 old blocks occur once in revision 9 (9b0c680ed). 45 new blocks are byte-exact, once each, in the section the judge named. No old block survives. C-1 is in the catalog (rules.cell_unit_minimum 5). Code read for sections 2, 11, 12: harvest.py head_change_class (184-195), code_identity (5597-5731), _changed_paths, resolve_inputs (1465-1525), registration digest fault (1414), desk verdict interpreter (5199-5201); plan.py _locator, read_allowance (390), advance_ledger_pin (721), registration optional (819); night_agent_install.py 1234-1242; driver.py production_seams (676), --h-claim (712), driver_checkout (1833); scripts/harvest_b5_window.py (--sealed-inventory-path, --prepare-desk, ValueError to HARVEST_FAULT); tests/test_b5_seal_landing.py; tests/hazards/test_import_graph.py. Recounted: 150/165/123/123/120 files at 9395cecfb and at cc0b3446d; nine prefill_pin files with three digests; the UNSEALED_DRAFT labels and the two quoted note sentences; the three cited record digests (46446fa4..., fec2dc44..., 92ba27dc...); allowlist 33 = 29 + 4 with both quoted protects texts; guard g(5..9) and the t table; section 6.9 parse equal to revision 10 (9 values); plan line 354 unchanged. Orchestrator rulings also applied: seal-land F1 to F9 and H-8 to H-12, reg-fidelity F1, F2, F6 and C2, the five Q5 corrections, and the brief's late additions for regions a, d and e.

**Smallest fix.** None.

### V-1 (MAJOR)

**Document.** registration_block5.md

**Where.** section 8 item 2 (lines 4576-4578, the judge's T-32) against section 7.3 (4467-4469, 4474-4476), section 7.6 (4556-4558) and the custody map's 'Who may read a restricted path' (4637-4638)

**What.** T-32 is verbatim and says the three derived/ files' 'only in-block reader is the scheduler's read of claim_usable'. Untouched section 7.3 has the lead build the cause key of cell.below_minimum from 'the families of the member exclusions that removed the units' and test 'one shared cause' in collection.failure_histogram; section 7.6 says the re-arm rules read 'the codes and families of its flags and member exclusions'. Those reads can only be made in the restricted files. Not a writer error: the judge had section 7.3 in view (SG-11) and did not reconcile it. Region c and the merger flagged it (merger item 2); I confirm it is real, not wording.

**Evidence.** /Users/edr/code/JouleWise-wt-int5/joulewise/b5/harvest.py 7448-7456: harvest.json carries verdict, claim_usable, the flag total, yield and exclude_window_reasons only. Counts by code and family are written only to derived/window_flags.json (7432-7433); member exclusion codes only to derived/exclusions.json; collection.failure_histogram is a flag (7283-7315), so its content is only in derived/flags.jsonl. claim_usable itself is in harvest.json, so the scheduler never needs the three files.

**Smallest fix.** Orchestrator decides; the judge's sentence is not reworded. Either (a) add one sentence in section 7.3 and the same clause in the custody map's 'Who may read' paragraph: the two section 7.3 reads are made by the same automation, which passes on family names and refusal causes only, never a code whose blinding is RESTRICTED; and ask the stage-2 judge to confirm it beside T-32's 'only'. Or (b) restate section 7.3's cause key from releasable records only (harvest.json exclude_window_reasons, the driver's yield counts and stage.members_refused_pre_bundle_identical) and strike 'the codes and families of its flags and member exclusions' from section 7.6.

### V-2 (MINOR)

**Document.** registration_block5.md

**Where.** section 2, 'Before ALPHA-1's harvest', lines 1857-1858

**What.** Says 'the four details of the head comparison listed in section 0.18'. Section 0.18 lists five, and so does every other place. The writer counted the review's four findings (H-8 to H-11) and left out cold pass 5's H-12. This is the only sentence in sections 2, 11 or 12 I found at odds with the sources.

**Evidence.** Line 1508 'differs from it in five details' (H-8 to H-12); line 499 'five details'; lines 5248-5254 'five further changes ... H-8 to H-12'; /Users/edr/night-archive/gate-prune/wave-1007b/harvest-lane/WORKLIST.md rows H-8 to H-12. Section 2 item 1 (1654-1656) correctly says 'that gap and three smaller findings' for the review alone.

**Smallest fix.** Line 1858: 'the four details' becomes 'the five details'.

### V-3 (MINOR)

**Document.** sealed_inventory.json (the stub, same bytes on the design branch and in int5)

**Where.** todo.summary and todo.head

**What.** REGISTRATION_FACTS, 'Also outside the registration', second item, was not applied: the stub should say the filled file is committed in the seal commit, the child of H_claim. The file belonged to no region. todo.head also still lists H_claim's contents only up to lane L10. No program reads todo, and the stub is replaced whole in the seal commit, so this touches no number; but the stub's bytes stay in H_claim's tree.

**Evidence.** /Users/edr/code/JouleWise-wt-int5/configs/campaigns/v5_claim_25g83/sealed_inventory.json: todo.summary 'this stub is replaced at seal ... by the inventory of the commit H_claim'; todo.head '...the P3 round and lane L10, merged under the merge gates (registration 2 item 1, FILL[H-CLAIM])'. git log shows its last change at 763b678a7. /Users/edr/night-archive/gate-prune/wave-1007b/seal-land/REGISTRATION_FACTS.md lines 118-119.

**Smallest fix.** Integrator, before H_claim (the stub is a seal document, so the edit costs no window input): append to todo.summary 'The filled file is committed in the seal commit, the child of H_claim, because a file cannot name the commit that contains it', and shorten todo.head to point at registration section 2 item 1. Or the orchestrator dispositions it as a record and leaves it.

### V-4 (MINOR)

**Document.** registration_block5.md

**Where.** section 14 Q14, heading and body, lines 5745-5746 and 5755-5756

**What.** The heading still reads 'the seal gate confirms or asks for the tightening below' and the body says the tightening 'would be a change to collection code, made and reviewed before the seal'. Stage 1 did not rule on Q14 or Q15. Section 12 (5305-5309) limits stage 2 to the final text, the digests and the commit steps, after H_claim is fixed; a tightening would move H_claim. If sealed as written, the text carries a question addressed to a gate that has passed.

**Evidence.** /Users/edr/night-archive/gate-prune/seal-gate/RULING_STAGE1.md names no Q14 or Q15 (SG-11 step 3 covers Q3, Q4, Q5, Q7, Q10 only). Merger item 5.

**Smallest fix.** Orchestrator's call, one clause in the heading: 'Set by orchestrator ruling of 2026-10-07; stage 1 of the seal gate did not take it up; stage 2 confirms it, or the tightening is made before H_claim and the seal waits for it.' If the orchestrator rules that the present rule stands, say so and strike 'or asks for the tightening below'.

### V-5 (MINOR)

**Document.** registration_block5.md

**Where.** section 13, 'Final hashes' row, line 5413

**What.** 'Open again for one value: the final head itself' reads as if the B5-FINAL-HASHES marker stood for the head. The header and section 13's own paragraph say the marker stands only for file digests computed at H_claim and the head is the H-CLAIM marker. The row is carried over from revisions 9 and 10.

**Evidence.** Lines 41-45 (header: 'the SHA-256, computed at H_claim, of the one file that the marker's sentence names'); line 5427 ('B5-FINAL-HASHES marks each digest that is recomputed at that commit'); the marker stands at eight sites, all digests (726 three times, 2470, 2969; plan 211, 214, 368). Merger item 7.

**Smallest fix.** Replace 'Open again for one value: the final head itself, which carries the census interpreter rule (section 2 item 1, section 4.5); each digest so marked is checked again there.' with 'Open again for the digests at H_claim: each marked digest is recomputed there (the head itself is the H-CLAIM marker).'

### V-6 (NOTE)

**Document.** registration_block5.md

**Where.** section 0.12 line 1016 (T-27), section 7.5 lines 4524-4526 (T-40), section 8 item 2 lines 4582-4583 (T-32)

**What.** The three items that are not byte-exact are correct merges under the brief's rule and may stand (merger item 3). In each, every word of the ruling is the judge's; the differing words are text the judge carried over unchanged from revision 9. T-40's merge is needed, not just allowed: the judge's tail 'one collection head for the code they executed' would be false under the seal landing, where the windows run from S, p1 and p2.

**Evidence.** git show 7c19c9c79 (revision 11): line 742 already read '(built in "The strict check of a reference" below; at harvest'; lines 3829-3830 already read 'the same collection code: no collection-code file that a completed window executed may differ, byte for byte, in the commit a later window runs'. T-32 differs only in the filled marker, 'The custody map at the end of this section (B5-BLIND-CUSTODY-MAP)', which the brief assigned to region c; the map lists the three derived/ files (line 4625) as C2 requires. The reconciling paragraphs for 'H_claim plus pin-only commits' and 'stays at H_claim' (1548-1552, 4528-4533, 5013-5014) agree with each other and with SEAL_LANDING section 3; keep them (merger item 4).

**Smallest fix.** None. Tell the stage-2 judge of the three merges.

### V-7 (NOTE)

**Document.** registration_block5.md

**Where.** section 5.7, lines 3142 and 3235

**What.** Region b writes that the minimum was 8 in 'revisions 3 to 9'. Revisions 10 and 11 also said 8; region a writes 'Revisions 3 to 11' (lines 67-68, 450). The judge's own 'Revision 9 said 8' (T-4) and '8 in revisions 3 to 9' (T-18) are verbatim and stay.

**Evidence.** Lines 3142, 3235 against 67-68 and 450; merger item 6.

**Smallest fix.** In the two region-b phrases only: 'revisions 3 to 9' becomes 'revisions 3 to 11'.

### V-8 (NOTE)

**Document.** flag_catalog.json and the integration tree

**Where.** /Users/edr/code/JouleWise-wt-int5/configs/campaigns/v5_claim_25g83/ at cc0b3446d

**What.** For the integrator before H_claim, three points. (1) The brief requires the two catalogs to end byte-identical; they do not yet. (2) The registration's delta-pass precondition forbids touching the stale code comments before H_claim without a new cold pass. (3) Ten catalog notes describe behaviour the harvest lane has not landed yet, and the catalog freezes at H_claim.

**Evidence.** (1) Effect, family, klass, blinding and the rule agree for all 192 codes; 42 notes and the status note differ (int5 holds revision 9's notes; revision 11 to 12 changed exactly 10 notes, as the revision-12 list item 13 says). The ten rewritten notes and the status note are faithful to the rulings; the status note has no 'DRAFT' outside DRAFT_CODES and 'the code's draft', no 'NOT SEALED', and no H_claim hash. The note of code.executed_differs_from_sealed carries the corrected clause (table D's catalog item). (2) Registration section 2 item 1 (1668-1669): any change under joulewise/ or scripts/ after 9395cecfb needs a further delta cold pass. git diff 9395cecfb cc0b3446d touches only configs/ and tests/. The stale comments are joulewise/b5/driver.py:153 ('8-of-10 cell minimum') and the harvest docstring. (3) neg8.reference_lost, neg8.screen_failed, both malformed-flag notes and code.executed_differs_from_sealed say 'the harvest lane lands ... before ALPHA-1's harvest' (merger item 9).

**Smallest fix.** Copy the three design files into int5 before H_claim and recheck the three SHA-256s. Leave driver.py:153 as it is (section 5.7 lines 3141-3145 already states the fact; the harvest docstring is H-13 of the harvest lane). No text change for (3); if the lane lands differently, the notes are stale records, not effects.

### V-9 (NOTE)

**Document.** registration_block5.md

**Where.** section 2 item 1 (lines 1632-1633, 1645-1646, 1654-1655) and section 9.1 (4781-4782)

**What.** The sealed text pins the SHA-256 of three files that live outside the repository under night-archive. They match now. Any later edit to one of them makes a sealed digest wrong, and the registration cannot change after the seal commit.

**Evidence.** shasum -a 256 today: cold-pass-5/REPORT.md 46446fa4...e8ad; wave-1007b/seal-land/REVIEW.md fec2dc44...2f0a; wave-1007b/seal-land/ORCHESTRATOR_RULING.md 92ba27dc...fde4e. All three equal the printed values.

**Smallest fix.** Do not edit those three files again; copy them beside the seal record in the record commit so the digests stay checkable from the repository.

## Part 2. The pedagogy reviewer (agent `a8529ca2b0ba69215`)

- **Reviewer:** pedagogy (Opus 5.5), diff 1d97f0a60..7e5eaa6c9, writers' own text only
- **Reviewed head:** 7e5eaa6c938c67aa402c8f857be03199739ba2c5

Findings (24):

### P-01 (MAJOR)

**Document.** registration_block5.md

**Where.** §0.18, 'Window input' and 'H_claim' bullets, lines 1446-1452 (same gap in §6.5 lines 3714-3716 and the header gloss, lines 10-11)

**What.** The central term is defined so that it includes the ledger pin, which contradicts the definition of H_claim built on it. A window input is 'every file under configs/' that a window can read, with only the three seal documents excepted. The ledger pin is under configs/ and a window reads it (line 2507: the bracket reservation reads the ledger through the committed pin). So by the text a pin-only commit changes a window input after H_claim, 'the last commit that changes any window input'. A reader rebuilding the head comparison from §0.18 alone gets every window after ALPHA-1 removed.

**Evidence.** Line 1450: 'Three files under `configs/` are excepted: the seal documents, below.' Line 1473: 'Pin-only commit. A commit that changes only `configs/calibration/calibration_ledger_head.json`'. The exception is stated only later and elsewhere: §9.1 line 4771 ('other than the ledger pin and the three files the seal itself rewrites') and the catalog note of code.executed_differs_from_sealed.

**Smallest fix.** Line 1450: 'Four files under `configs/` are excepted: the ledger pin (`configs/calibration/calibration_ledger_head.json`, data that advances after each window; see Pin-only commit below) and the three seal documents, below.' Add the same six words '(other than the ledger pin and the seal documents)' at §6.5 line 3715.

### P-02 (MAJOR)

**Document.** registration_block5.md

**Where.** §0.10, line 871-872 against line 787

**What.** One phrase names two different triples inside one subsection. At line 787 'Three timing bounds limit δ' are b, s and m, in seconds. At line 871 B is 'the sum of the stratified averages of three timing bounds that every member records, of which a_i is the first'; these are three energy bounds in joules, and the other two are never named here. A reader will first read B as built from b, s and m, and cannot rebuild B from this section.

**Evidence.** Analysis plan §4 step 4 (line 232-236) names them: 'Every member records three non-negative energy bounds: E_clock_anchor_shift_bound_j ... E_interpolation_joint_edge_bound_j ... E_whole_window_drift_allowance_j'. The third is a drift allowance, not a timing bound.

**Smallest fix.** Line 871-872: replace 'three timing bounds that every member records, of which a_i is the first' with 'three energy bounds, in joules, that every member records (analysis plan §4 step 4): a_i; an interpolation bound, which is 0 for these traces; and half the window's NEG-8 drift allowance (§0.12)'.

### P-03 (MAJOR)

**Document.** registration_block5.md

**Where.** §2, 'Before ALPHA-1's harvest', line 1858

**What.** A precondition counts 'the four details of the head comparison listed in §0.18', but §0.18 lists five, as do the revision-12 list and §11. The reader cannot tell which of the five is not required before ALPHA-1's harvest.

**Evidence.** Line 1508: 'differs from it in five details'; line 499: 'five details of the head comparison'; line 5248: 'five further changes ... H-8 to H-12'; line 5171: 'Five parts of it'.

**Smallest fix.** Line 1858: 'four' -> 'five'.

### P-04 (MAJOR)

**Document.** registration_block5.md

**Where.** §5.3 lines 2762-2767; §6.5 line 3878; §9.1 lines 4744-4748

**What.** 'The evaluator' names two different functions. §5.3 calls `whole_window._derived_neg8_decision` 'the core's own evaluator' and then says 'The harvest hands the evaluator the verdict's completion time ... the evaluator replaces it'. §6.5 and §9.1 define the evaluator as `whole_window.evaluate_neg8_point_drift` and call `_derived_neg8_decision` 'the re-derivation'. The new age rule of §5.3 (which time the bound's age is judged at) therefore cannot be tied to one function.

**Evidence.** Line 2762: 'the core's own evaluator (`whole_window._derived_neg8_decision`)'. Line 4744: 'the **evaluator**, the function that screens the surviving references (`whole_window.evaluate_neg8_point_drift` ...); ... the re-derivation, the function that rebuilds a verdict ... (`whole_window._derived_neg8_decision`)'.

**Smallest fix.** In §5.3 lines 2762, 2765 and 2767 write 'the re-derivation' (or 'the core's re-derivation function') in place of 'evaluator', keeping 'evaluator' for `evaluate_neg8_point_drift` only; or, if the age rule lives in the evaluator proper, name that function at line 2765.

### P-05 (MAJOR)

**Document.** registration_block5.md

**Where.** §11 item 1, line 5032-5033, against the judge's (ii) at line 5017 and §0.18 line 1480

**What.** Where a class (ii) fix lives cannot be rebuilt. The judge's text says such fixes 'land in the desk checkout only'. The writer's next paragraph says 'commits of classes (ii) and (iii) go to the main branch'. §0.18 defines a desk checkout as 'any other checkout', §11's Terms as 'another checkout ... on this machine'. A checkout is not a branch, and the picture shows main receiving only M. The reader cannot tell which branch a harvest-lane commit is made on or what 'only' excludes.

**Evidence.** Line 5032: 'Third, commits of classes (ii) and (iii) go to the main branch and never into the measurement checkout'. Line 5017 (verbatim, not to be changed): 'which land in the desk checkout only'.

**Smallest fix.** Line 5032: 'Third, commits of classes (ii) and (iii) are made on a branch that only a desk checkout has checked out (main, once the seal's pull request has merged), and are never fetched, merged or checked out in the measurement checkout (§12 step 8), so no window can arm from them. "The desk checkout only" in (ii) means exactly this: any checkout but the measurement one.'

### P-06 (MINOR)

**Document.** registration_block5.md

**Where.** §0.18 line 1505; §6.5 line 3712; defined only at §11 line 5104

**What.** 'Executed roots' is used twice before it is built. §0.18 says four files 'lie outside a window's executed roots'; the definition (joulewise/, scripts/ and the window's own pack) arrives 3,600 lines later.

**Evidence.** Line 5104: 'The window's **executed roots** are `joulewise/`, `scripts/` and the window's own pack.'

**Smallest fix.** Line 1505: 'they lie outside a window's executed roots (`joulewise/`, `scripts/` and the window's own pack, the directories the executed-file inventory covers)'.

### P-07 (MINOR)

**Document.** registration_block5.md

**Where.** §11 item 1, worked example, line 5074

**What.** 'comparison (b)' is used before item 2 defines comparisons (a) and (b) at lines 5104 and 5114.

**Evidence.** Line 5074: 'ALPHA-1 was excluded: comparison (b) listed the GAMMA file as a changed window input.'

**Smallest fix.** Line 5074: 'the head comparison (comparison (b) of item 2) listed ...'.

### P-08 (MINOR)

**Document.** registration_block5.md

**Where.** §12, Stage 1 bullet, lines 5301-5304

**What.** The count does not add up as written: 'Of the seven, three change entries of the refusal allowlist and one test fixture ..., and four are the harvest lane' reads as 3 + 1 + 4 = 8.

**Evidence.** The ruling has K-1 to K-3 (allowlist; K-2 also touches the test catalog) and K-4 to K-7 (harvest). §13 line 5414 names K-1, K-2, K-3.

**Smallest fix.** 'Of the seven, three (the ruling's K-1 to K-3) change entries of the refusal allowlist (§6.11), one of them together with a test fixture (a data file that a test compares against); no program running inside a window loads either file. The other four (K-4 to K-7) are the harvest lane of §11 item 4 ...'

### P-09 (MINOR)

**Document.** registration_block5.md

**Where.** §0.12, new second paragraph, lines 934-944

**What.** The paragraph stands before every definition of the section and uses seven terms the section builds only below: reference, 'Lost references', 'loss test', 'the six physics codes', 'the two identity codes', 'fails the whole screen', and the harvest's loss list.

**Evidence.** Line 946 onward first defines 'Reference member'; 'Lost references' is line 998; the screen is built after that.

**Smallest fix.** Move lines 934-944 to follow the paragraph 'Who applies the loss test' (after line ~1097), where every term has been built; leave at 934 one sentence: 'Two of the rules below were set by the first stage of the seal gate and are applied by the harvest program pinned before ALPHA-1's harvest; the note after "Who applies the loss test" says which.'

### P-10 (MINOR)

**Document.** registration_block5.md

**Where.** §0.10, bullet b, line 792

**What.** 'the acceptance's bracket screen' is used before §0.11 builds either 'acceptance' or 'bracket screen'; only a section pointer stands in.

**Evidence.** Line 792: 'never less than 0.014531 s, the acceptance's bracket screen (§0.11; ...)'. §0.11 line 912 builds it: 'the **bracket screen** 0.014531 s (their range)'.

**Smallest fix.** Line 792: 'never less than 0.014531 s (the **bracket screen**: the range of the fiducial bounds over the captures from which the calibration acceptance, the registered record that says which captures may judge a window, was derived; §0.11)'. Have the writer confirm the gloss against §0.11's wording.

### P-11 (MINOR)

**Document.** registration_block5.md

**Where.** §14 Q5, line 5677, against §0.10 lines 889-892

**What.** The same 1.016 J is derived two ways with no bridge. §0.10 computes g × (P_on + P_off) + m × |P_off − P_on| from 1.0959 W and 32.0292 W. Q5 prints '0.031073829 s × 32.697 W', and 32.697 W appears nowhere else; a reader cannot rebuild it.

**Evidence.** Line 5677: 'a timing bound of 0.031073829 s × 32.697 W = 1.016 J'. Line 890: '0.024999593 × (1.0959 + 32.0292) + 0.006074236 × (32.0292 − 1.0959) = ... 1.0160 J'.

**Smallest fix.** Line 5677: replace the product by '1.016 J; §0.10 gives the arithmetic. In D-078's own round terms that is a total timing bound of 0.031073829 s at an effective 32.697 W, the bound divided by that time'.

### P-12 (MINOR)

**Document.** registration_block5.md

**Where.** §13, 'Final hashes' row, line 5413

**What.** The row says the marker is 'Open again for one value: the final head itself', which makes B5-FINAL-HASHES stand for a commit. The header (line 41) and the paragraph under the table (line 5427) say it stands only for digests computed at H_claim and that the head is H-CLAIM. Same marker, two meanings.

**Evidence.** Line 41: '`B5-FINAL-HASHES`: the SHA-256, computed at H_claim, of the one file that the marker's sentence names.'

**Smallest fix.** Line 5413: 'Open again for the digests at one commit, H_claim (the marker `H-CLAIM` names the commit itself): each digest so marked is computed again there.'

### P-13 (MINOR)

**Document.** registration_block5.md

**Where.** §12 step 6, line 5340-5341

**What.** 'the desk collectors (§6.1)' is the only occurrence of that phrase in the file; §6.1 does not use it. The check that proves the measurement checkout cannot be reproduced from the text.

**Evidence.** grep 'desk collectors' returns line 5340 only.

**Smallest fix.** Name the command: 'and the record-only collectors of §4.1 step 4, run by hand at the desk (`scripts/collect_window_flags.py --stage arm`, given H_claim as `--h-claim` and the sealed inventory), raise no flag whose code begins with `code.`' (writer to confirm the stage argument).

### P-14 (MINOR)

**Document.** analysis_plan_block5.md

**Where.** §7.1 step 3, lines 397-402

**What.** The glosses of 'metrology term', 'governed' and 'random-error variances' follow the judge's sentences that use them. The judge's text cannot be reworded, but the gloss can precede it.

**Evidence.** Line 391 (judge): 'Metrology term: the engine reads governed random-error variances only for ...'. Line 397: '(Terms of this step. The *metrology term* ...'.

**Smallest fix.** Move the parenthesis of lines 397-402 to stand before the judge's block, as the opening of item 3 ('3. (Terms of this step: ... ) Metrology term: the engine reads ...'). Both lie below line 354, so the pinned line is not moved.

### P-15 (MINOR)

**Document.** registration_block5.md

**Where.** 'What changed in revision 12', item 2, lines 454-466

**What.** The item uses 'reference', 'the whole screen', 'the midpoint', 'two diagnostic ones' and 'surviving references' with no gloss; they are built in §0.12, 480 lines on. Item 1 of the same list glosses its term (detection floor); this one does not.

**Evidence.** Line 456: 'A reference that succeeded but whose energy cannot be read is lost ..., and the surviving references decide. Before, it failed the whole screen'.

**Smallest fix.** Open item 2 with one sentence taken from §0.12: 'A window runs members of one fixed reference workload at its start, middle (the midpoint) and end; the NEG-8 screen tests the change between its start and end references against a bound, and a reference left out of that test is lost (§0.12).'

### P-16 (MINOR)

**Document.** registration_block5.md

**Where.** 'What changed in revision 12', item 1, line 450-451

**What.** 'the interval's half-width grows by a factor of 1.169 at 8 kept and 1.736 at 5' gives no baseline. The reader cannot tell the factor is against all 10 kept.

**Evidence.** §6.6 (judge) gives it: 't(0.975, n − 1) / t(0.975, 9) × √(10 / n)'.

**Smallest fix.** Line 450: 'compared with all 10 kept, the interval's half-width grows by ...'.

### P-17 (MINOR)

**Document.** registration_block5.md

**Where.** §2 item 1, pass 5, lines 1634-1636

**What.** Three unbuilt items in one clause: 'the census interpreter rule', 'the live launch of Sol R1' and 'a hit'. Sol R1 is a finding, so 'its live launch' has no referent; a hit is first explained in §4.5.

**Evidence.** Line 1635: '36 command lines, each given the verdict the pass's brief expected of the code at `9b0c680ed`; the live launch of Sol R1 is a hit'.

**Smallest fix.** 'It covers the census interpreter rule (§4.5: how the agent census reads the command line of a JavaScript runtime). The pass ran the matcher on 36 command lines and each got the expected verdict; a real `node` process started in the form that finding Sol R1 had shown to be missed (§4.5) was classed as an agent (a hit).'

### P-18 (MINOR)

**Document.** registration_block5.md

**Where.** header, lines 3, 17 and 46

**What.** Three terms are used in the header before their gloss: 'seal commit' (line 3; built at line 30), 'the seal gate's first stage' (line 17; glossed at line 21) and 'seats' (line 46; glossed at line 333 and in §0.1).

**Evidence.** Line 3: 'committed at the seal, in the seal commit (built with the companions below)'.

**Smallest fix.** Line 3: 'in the seal commit, the one commit that follows the final head of the code and carries this file's final bytes (built with the companions below)'. Line 17: 'the first stage of the seal gate (the cold gate that seals this file, §12)'. Line 46: 'the seats of the seal gate (a seat is one model session working to a written brief)'.

### P-19 (MINOR)

**Document.** registration_block5.md

**Where.** §11 Terms line 4955 against §0.18 line 1480

**What.** §0.18 defines 'a desk checkout' as any checkout other than the measurement one. §11 defines '**The** desk checkout' as 'another checkout of the same repository on this machine', as if there were one. §11 item 2 then introduces a third, the 'driver checkout', which by §0.18's definition is also a desk checkout. The reader cannot tell whether one particular checkout is meant where the judge's text says 'the desk checkout'.

**Evidence.** Line 1480: 'A **desk checkout** is any other checkout of the repository.' Line 4955: '**The desk checkout** is another checkout of the same repository on this machine'.

**Smallest fix.** Line 4955: 'A **desk checkout** (§0.18) is any checkout other than the measurement one; "the desk checkout" below is whichever one a desk program is run from. Its commit is what an addendum pins (item 4).'

### P-20 (MINOR)

**Document.** registration_block5.md

**Where.** §11 item 1, line 5014-5015

**What.** 'After the seal commit, H_claim is extended only by (i)...' uses 'extended' for a commit without saying what extending a commit is. Two of the four classes ((ii), (iii)) never enter the chain 'H_claim, seal commit, pin-only commits' that the previous sentence calls 'this chain and no other', so 'extended' cannot mean 'added to that chain'.

**Evidence.** Line 5013-5015: 'it means this chain and no other: H_claim, then the seal commit, then zero or more pin-only commits. After the seal commit, H_claim is extended only by (i) pin-only commits ...'.

**Smallest fix.** 'After the seal commit, the only commits that may be made anywhere in the repository during the block are of four classes, and only class (i) enters the measurement checkout: (i) ...'

### P-21 (NOTE)

**Document.** registration_block5.md

**Where.** §2 item 1 line 1636; §9.1 lines 4781-4806; diagrams of §0.18 and §11

**What.** The letter C carries three meanings: commit C = H_claim in both diagrams, cold pass 5's cases C1 to C14, and the catalog change C-1 of the ruling. §9.1's 'C6 below' and 'cases C4 to C10' follow a section in which C is a commit.

**Evidence.** Line 1523: 'C = H_claim'. Line 1636: '14 cases, C1 to C14'.

**Smallest fix.** At line 1636 and at the first use in §9.1 write 'cases the pass numbers C1 to C14 (not the commit C of §0.18's picture)'.

### P-22 (NOTE)

**Document.** flag_catalog.json

**Where.** note of neg8.reference_lost, against registration §0.12 lines 934-935 and 1025

**What.** The same set of new losses is counted three ways: the catalog note says stage 1 'added three kinds of loss'; §0.12 says 'Two rules' at line 934, made of one loss plus 'the four losses', and 'Four more losses' at line 1025.

**Evidence.** Catalog: 'Stage 1 of the seal gate ... added three kinds of loss'. Registration line 1025: 'Four more losses, set by the seal gate'.

**Smallest fix.** Catalog note: 'added five reasons for loss, in three groups: ...' (note text only; the catalog's SHA-256 then changes and must be re-synced with the integration tree before H_claim, so the reviser may prefer to leave this and accept the difference).

### P-23 (NOTE)

**Document.** registration_block5.md

**Where.** §0.18 line 1548, §7.5 line 4528, §11 item 1 line 5013

**What.** Three separate paragraphs explain how to read the judge's 'H_claim plus pin-only commits'. They agree, but each rebuilds the explanation with slightly different words, and §7.5's defines 'seal commit' a third time. One explanation and two pointers would be easier to hold.

**Evidence.** Line 4528: '*How to read "H_claim plus pin-only commits".* One more commit lies between ...'; line 1548: '**"H_claim plus pin-only commits".** Passages of §7.5, §11 and §14 ...'.

**Smallest fix.** Keep §0.18's paragraph; cut §7.5's to 'Read "H_claim plus pin-only commits" and "stays at H_claim" as §0.18 states: H_claim, the seal commit, then pin-only commits.' Leave §11's sentence.

### P-24 (NOTE)

**Document.** analysis_plan_block5.md

**Where.** §14, revision 11 and 12 entries, lines 938 and 995

**What.** 'Every line above §6's sentence on R_cm keeps its line number' gives a rule with no forcing reason, so a reader cannot tell why 23 lines are over-long or why judge's lines were made up by joining others.

**Evidence.** Line 995: 'Every line above §6's sentence on R_cm keeps its line number, as in revisions 10 and 11.'

**Smallest fix.** Line 995: add '(a test fixture, `tests/fixtures/d165_rationale_allowlist.json`, names that sentence by its line number, and the fixture cannot change in the seal commit; registration §12 step 4)'.

## Part 3. The reviser's return (agent `a237e669e0d5b2eac`)

The reviser's return follows whole. Its own headings are kept as it wrote them.

---

REVISER RETURN: registration revision 12, design branch

All 25 findings held and were applied; none was declined. Two were left to the orchestrator by the reviewer (V-1, V-4) and I applied a cure for each, so both need your ruling before stage 2.

**Final head:** `f7c643457cbf5766bb35954e2ff67e32b639a003` on `design/2026-10-05-v5-claim-block-draft`, pushed, worktree `/Users/edr/code/JouleWise-wt-ia-claim` clean. Start head was `7e5eaa6c9`.

**SHA-256 at the final head (`shasum -a 256`):**
- `registration_block5.md`: `2a2efc57fd2ab0cbbfb40a3d7a9942ae572bd79ac25ecfaf8732b5fb00de05e7` (6,079 lines)
- `analysis_plan_block5.md`: `453a5db814b7d6c88c1cf6f198d16338f8dc67848ea599cb74dbe6f43e4e2c6b` (999 lines)
- `flag_catalog.json`: `5d77c725d4bf482bd667ca4c3a926e2f6471d55d196cd4b4addee435da01ee8d` (unchanged)
- `sealed_inventory.json` (the stub, a fourth file I changed for V-3): `d3867165661e943887fa75ad743d744a09bcfd6387fb44008ba531f48b363388`; int5 still holds `39433d47…`

## Needs your ruling

1. **V-1 (MAJOR): applied as the reviewer's option (b).** It is isolated in commits `e9d224bb5` and `4f9a5981c`; revert both to take option (a) instead.
   - **Confirmed in code** (`joulewise/b5/harvest.py` at int5 `cc0b3446d`): `harvest.json` carries the verdict, `claim_usable`, the yield and `exclude_window_reasons`, and no member-exclusion code. The content of `collection.failure_histogram` is written only to `derived/flags.jsonl`.
   - **What changed in §7.3:** the cause key is built from released records only: the arm record, `exclude_window_reasons` with the catalog's families, and for `cell.below_minimum` the code itself. The short-window rule reads the driver's `stage.members_refused_pre_bundle_identical` from `night/hazard_result.json` (`flags_emitted`) and no longer reads the histogram.
   - **What followed:** §7.6's list of what the rules read; the custody map's "Who may read" paragraph; item 5 of the revision-12 list. The judge's T-32 sentence is untouched.
   - **Why (b):** it keeps the judge's "only" true as written. Option (a) adds a second reader of the restricted files, contradicts that sentence, and would need stage 2 to confirm it.
   - **Cost of (b):** two consecutive `cell.below_minimum` attempts go to a consult whatever removed their units. A LOW with a shared cause that never ran three members in a row no longer holds the next arm. Nobody may read the digit-redacted histogram during the block, which R3 would use to diagnose a refusal.
   - **Not a reviewer finding:** in the same paragraph I named §7.4's END STATE count as the one automation read of other restricted paths, because that paragraph's reader list omitted it.

2. **V-4 (MINOR): applied as a statement of fact, with no ruling made.** Stage 1 was not asked about the census limits: `STAGE1_DISPATCH.md` line 45 says "None of your questions is about the census rule", and Q14 was opened in revision 10.
   - Q14's heading now says stage 2 confirms the rule as it stands, or asks for the tightening, in which case the seal waits for a new H_claim. The body says a tightening moves H_claim.
   - Item 11 of the revision-12 list records it (`b97be7dbb`).
   - Either the stage-2 charge carries Q14, or you rule and the heading is changed. §12's description of stage 2 does not mention Q14; I left §12's scope alone.

3. **V-3 (MINOR): applied to the design branch's stub** (`todo.summary`, `todo.head`; commit `9d2438b6c`). No test or program reads `todo` or pins the stub's bytes. The integrator copies this fourth file into int5 before H_claim, or leaves int5's stub; the seal commit replaces it whole either way.

## Per finding

| Finding | Disposition |
|---|---|
| V-1 | applied, option (b); see above |
| V-2 / P-03 | applied: §2 "four details" is now "five" |
| V-3 | applied on the design branch's stub; see above |
| V-4 | applied; Q14 stays open for stage 2 |
| V-5 / P-12 | applied: the §13 row and the paragraph under the table say the final-hashes marker stands for digests at H_claim only |
| P-01 | applied: the ledger pin is excepted from window inputs in §0.18, §6.5, the header gloss and revision-12 list item 8 (code: `head_change_class` returns `pin_only`) |
| P-02 | applied: B's three energy bounds are named and set apart from b, s, m (checked against `paper_reported_energy.BOUND_KINDS` and `reduce._interpolation_joint_edge_bound_j`) |
| P-04 | applied: §5.3 says "re-derivation" for `_derived_neg8_decision`, which is the function that replaces the age time; "evaluator" is kept for `evaluate_neg8_point_drift` |
| P-05 | applied: §11 item 1 says what "land in the desk checkout only" means |
| P-06 | applied: "executed roots" glossed in §0.18 |
| P-07 | applied |
| P-08 | applied: K-1 to K-3 and K-4 to K-7 |
| P-09 | applied: the paragraph moved to a new item after "Who applies the loss test"; one pointer sentence stays at the head of §0.12 |
| P-10 | applied: bracket screen and acceptance glossed (range of the 24 captures, checked in the acceptance file) |
| P-11 | applied: 32.697 W is stated as a quotient, tied to §0.10 |
| P-13 | applied: the command is `scripts/collect_window_flags.py --stage desk` with `--h-claim` and `--sealed-inventory` (the reviewer guessed `arm`; the script and SEAL_LANDING step 7 say `desk`) |
| P-14 | applied, adapted: the gloss now closes step 2 of plan §7.1. Placing it inside item 3 would have split the judge's T-45 block. |
| P-15, P-16, P-17, P-18, P-19 | applied |
| P-20 | applied, adapted: "extension" is kept and defined, because the judge's T-41 ends "Each extension carries…". The reviewer's "only class (i) enters the measurement checkout" was corrected for class (iv), which enters after a re-issued seal. |

The merger's note on "revisions 3 to 11" (header) against "revisions 3 to 9" (§5.7) was left as it is: both are true, and the judge's own T-4 and T-18 say 9.

## The merger's five checks at the final head

1. **T items:** 45 of 48 new blocks byte-exact, once each, no old block surviving. T-27, T-32 and T-40 are the writers' reported merges, unchanged from the merged head.
2. **Catalog:** 192 codes, `rules.cell_unit_minimum` 5, effect, family, class and blinding equal to revision 10 for every code, same JSON form; it loads with int5's loader. Bytes unchanged.
3. **Pinned text:** plan line 354 unchanged in text and number. §6.9 heading, JSON block and whole section are byte-identical to revision 10. The §4.3 JSON block is byte-identical. The harvest's parser returns the same nine values. The D-165 scanner finds only the three allowlisted hits.
4. **Numbers:** no stale value. Every hit that differs from the merged head is a re-wrap of the same sentence or one of my glosses.
5. **Markers:** registration 14 (the six seal-fill names), plan 3 seal-fill plus 11 of lane L9's own, catalog 0.

No 64-character digest or 40-character commit name was added or lost in any file.

## Remaining FILL markers (line numbers at the final head)

**Registration:**
- 7: `B5-SEAL-RECORD`
- 742: `B5-FINAL-HASHES` ×3
- 1633: `H-CLAIM`
- 1717: `B5-SEAL-RECORD`
- 1726: `B5-PLANS-REGENERATED`
- 2269: `B5-PLANS-REGENERATED`
- 2505: `B5-FINAL-HASHES`
- 3008: `B5-FINAL-HASHES`
- 4644: `B5-RELEASE-EVENT`
- 5380: `B5-SEAL-SEATS`
- 5426: `B5-SEAL-RECORD`
- 5496: `H-CLAIM`

**Analysis plan, seal-fill:** 211, 214, 368: `B5-FINAL-HASHES`.

**Analysis plan, lane L9's own:**
- 63: `B5-ANALYSIS-CUSTODY-ROOT`
- 165: `V5-FINAL-PINSET`, `V5-V2-INPUT-MANIFEST`
- 166: `MINT-TO-CLOSEOUT-ADAPTER`
- 170: `REPORTED-ENERGY-ISSUER`
- 171: `DISCLOSURE-PRODUCER`, `CLAIM-VERDICT-TO-FILL-ADAPTER`
- 193: `B5-BLIND-DRY-RUN-RECORD`
- 385: `GAMMA-MANIFEST-EXCLUSIONS-BINDING`
- 694, 696: `DISCLOSURE-SITES`

**Catalog:** none.

**Stub `sealed_inventory.json`:** line 14, `B5-SEAL-RECORD` inside `todo.sealed_with`. I removed `FILL[H-CLAIM]` from `todo.head`.

## Commits on top of `7e5eaa6c9`

- `0143cfe92`: registration, every finding except V-1
- `908c870e1`: analysis plan, P-14
- `9d2438b6c`: the stub, V-3
- `e9d224bb5`: registration, V-1 alone
- `b97be7dbb`: revision-12 list, Q14 stays open
- `4f9a5981c`: revision-12 list, the V-1 change
- `f7c643457`: §0.18, only the ledger pin is said to be read by a window

## Paths

- Notes: `/Users/edr/night-archive/gate-prune/wave-1007b/reg-final-b/reviser/NOTES.md`
- Check outputs: `/private/tmp/claude-501/-Users-edr-code-JouleWise/e4fc0437-3e56-4860-a119-d14d766031f7/scratchpad/reviser/` (`checks_final.txt`, `check4_[a-g].final.txt`, `check4_[a-g].before.txt`)

---

## What followed the review round

From the session record (`WAVE.md` of the wave of 2026-10-07, entries of 23:35 and later) and the ruling of the
seal gate's second stage, part A (`../RULING_STAGE2.md`):

- The orchestrator ruled on the reviser's two open cures. For V-1, the reviser's cure stands: the rule that decides
  whether two failed attempts share a cause (registration section 7.3) is built only from records that may be
  opened during the block. For V-4, question 14 of the registration (the limits of the rule that detects agent
  processes) was closed on the evidence of cold pass 5 and was not left to the second stage.
- A last pass applied those two rulings, the late items that followed from the seal-rulings lane, and the four
  markers whose values are names; the text at commit `c7408819c` was the text the second stage's part A read.
- Part A confirmed both rulings (its sections C.1 and C.3), required three further text changes and one sentence in
  the refusal allowlist, and admitted the text with those changes.
