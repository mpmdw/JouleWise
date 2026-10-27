# Paper 1 by 30 November: plan and contingencies

Written 2026-10-27 by the lead (Claude Code session 015ASG1T, laptop) at Ed's request: "how can we make sure we have a
strong paper/deliverable by end of nov? make a contingency plan in case bytes doesnt go as well or analysis struggles".
Dates are estimates. Every decision below is about schedule and scope, never about results: each fallback is chosen by
date and by what has finished, so no choice depends on what any number turns out to be.

## 1. Why Paper 1 is robust to its own results

Paper 1's core contribution is the method and its honest limits: how finely a laptop's own sensors can split energy
between phases, the detection floor, the attribution floor, the replication, and the automated pipeline that produced
it under pre-registration and blinding. Its value does not depend on any comparison coming out a particular way. A
model comparison reported as "not resolvable" is a finding, and pre-registration is what makes it publishable rather
than a failed experiment. The same holds for BYTES: a law that fails on held-out models says what else drives
energy. **We never need a particular outcome. We only need the pipeline to finish.**

## 2. The tiers (decided by date and completion, never by result)

| Tier | Contents | Needs |
|---|---|---|
| **A, full** | Part 1: block-5 numbers and the block-6 replication. Part 2: the registered BYTES result (both stages), plus the extension models | everything on time |
| **B** | Part 1 full. Part 2: BYTES at its registered one-pass minimum, extension models dropped or reported as available | BYTES pass 2 incomplete |
| **C** | Part 1: block-5 numbers, with block 6 reported as collected and its release following as an addendum. Part 2 as A or B | block-6 release slips past ~22 Nov |
| **D, floor** | Part 1: block-5 numbers. Part 2: BYTES as a pre-registered design with its instrument-check evidence (not used for claims) and a statement of when results follow | block-5 release lands but BYTES analysis cannot finish |
| **E, last resort** | The method and diagnostic paper already merged (synthetic demonstrations and historical captures), plus the automation pipeline as a methods contribution, with block 5 and BYTES described as registered and collected | block-5 release itself slips past ~20 Nov |

Tier E exists so that 30 November never produces nothing. It is unlikely: the block-5 release is gated by one
program (L9), which now has someone working on it, a fix in hand and a clear path.

## 3. Checkpoints

The lead checks each date against these conditions, records the call in RUN_STATE and tells Ed in one line.

| Date | Condition | If not met |
|---|---|---|
| **1 Nov** | L9 accepted: both cross-family reviews done, fixes in, CI green | Escalate: the lead takes L9's remaining fixes directly; parallel steps stay deferred; no new L9 features |
| **3 Nov** | Block-5 blind dry run started on the measurement Mac | Hold BYTES for the dry run regardless of the s1 exception (Ed already allowed this, ruling 6a) |
| **5 Nov** | BYTES collection closed (registered end) | By rule: whatever counts is what BYTES has. Tier B if pass 2 is short |
| **8 Nov** | Block-5 release done (dry run, recompute agreement, release record) | Writing switches to Tier C for block 6 now, not later |
| **12 Nov** | BYTES stage 1 committed | Tier D for Part 2 if stage 1 cannot finish by 15 Nov |
| **15 Nov** | All Paper 1 results that will make it are in hand | Freeze scope. Anything later becomes an addendum after submission |
| **22 Nov** | Full draft to Ed | Cut the writing: shorter discussion, appendix moved to supplementary material |
| **30 Nov** | Paper 1 ready | — |

## 4. Risks and what protects against each

1. **L9 review finds a blocker.** Two reviews run in parallel, not in series. The laptop runs full-size tests about
   4 times faster than the cloud machines. Fixes stay minimal and in non-governed code. A defect class seen twice gets a
   structural rule, not another round.
2. **The real dry run refuses on real data.** Most of that risk is caught before it happens by the cached full-size
   run, the run-wide check that turns any safety-timer firing into a refusal, and the synthetic
   recompute-versus-analysis comparison (RC-CMP-1). Two Mac gaps are reserved for the dry run, one for the run and one
   for a cure and rerun.
3. **The independent recompute disagrees at release.** It is front-loaded on synthetic data. If a real disagreement
   still appears, the repair is disclosed, as the plan already requires.
4. **Block 6 slips.** Its release has to follow block 5's, and it needs its own driver, which is being built now, plus
   its registration's checks. Tier C reports block 6 as collected with the release as an addendum. The replication
   remains a strength even then, because the design and the collection are complete and pre-registered.
5. **BYTES loses sessions.**
   - The fit set (session 1) runs first; extension models are dropped first.
   - If the fit set itself cannot be collected, the three-line test is impossible. Part 2 then reports energy per token
     across the models collected, as a measured table without the law test (Tier D).
   - The 70B model's heat problem is handled by its council's fix, or by reporting it as not usable.
6. **The measurement Mac misbehaves.**
   - No agent process on it during sessions (directive #589).
   - No macOS or app updates on it until 30 November.
   - The loop's physical checks stay as they are.
7. **Writing takes longer than planned.** Writing starts now, not when numbers arrive (section 5).

## 5. Writing in parallel, starting now

These materials exist already:
- a merged methods draft (`docs/paper/draft-v2-skeleton.md`);
- a related-work draft;
- a figures plan;
- a results-fill registry, which maps every printed number to the artifact that issues it.

So the paper can be written now with placeholders, and numbers drop into tables when each release happens. Nothing in
the text waits on a number except the results paragraphs.

- **Now:** assemble the Paper 1 draft, with each section listed below. Prepare figures that need no numbers: the
  pipeline diagram, the phase-split illustration, the BYTES design, the session ledger.
  - Part 1 method: from the merged draft.
  - Part 2 design: from the BYTES registration.
  - The automation pipeline section.
  - Related work.
  - Limitations.
  - Results sections as templates bound to the results-fill registry.
- **On each release:** fill the tables, write the results paragraphs, and have the independent recompute's comparison
  table checked by one executing reader (gate policy).
- **Writing is not blind work.** Drafting text near the numbers must never change a registered analysis. Any analysis
  change after release goes through the plan's disclosed-repair route.

## 6. What Ed needs to do

1. Keep the measurement Mac free of interactive AI sessions and software updates until 30 November.
2. Read the draft on about 22 November.
3. Nothing else is needed from him for this plan; the checkpoints are the lead's to call.

## 7. DIFFICULTY collection overlaps Paper 1 writing (Ed, 2026-10-27)

Ed: "cant the difficulty measurements be takin WHILE im writing the paper 1??" Yes. Writing uses no measurement
time, so DIFFICULTY (Paper 2, `docs/registrations/difficulty_pack_v2.md`) collects on the measurement Mac from
about 6-10 November, while Paper 1 is written. Three things decide the start:
1. BYTES collection closes (5 Nov).
2. The DIFFICULTY v2 registration is sealed and its code merged, and the collection-code freeze audit is done. This
   prep runs in the cloud now.
3. Any block-5 or BYTES analysis step still assigned to the Mac (the dry run if `B5-TRANSFER: GO` is not given,
   and the BYTES stages) takes the Mac first, in the gaps reserved at 3 Nov and 8 Nov. DIFFICULTY sessions fill the
   rest.

Paper 1 never waits on DIFFICULTY. If a DIFFICULTY problem needs the lead's attention during the 15-22 Nov writing
window, Paper 1 goes first.

**Amended the same day (Ed):** "after bytes, i think agent-monitoring pilots ... is the highest prio research
candidate, even above difficulty if nothing in it relies on difficulty finishing". Nothing does. The alignment pipeline
(`lane/2026-10-21-align-integration`, `docs/align/PIPELINE.md` there) names no DIFFICULTY input. So the order on the
measurement Mac after BYTES closes is:
1. agent-monitoring pilots (local models, from about 6-10 Nov, during Paper 1 writing);
2. then DIFFICULTY.

Points 1-3 above apply to the pilots in place of DIFFICULTY. The prep seat ALIGN-READY-1 does the same readiness work
for the pilots that DIF-READY-1 does for DIFFICULTY. DIF-READY-1 continues at lower priority, since it is cloud-only
work.
