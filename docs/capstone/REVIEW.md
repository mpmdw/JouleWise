# Review of the v1 capstone outlines (Sol, `capstone/2026-11-08-outlines`)

Reviewer: the laptop lead's capstone delegate (Opus 5.5), 2026-11-08. The v1 files are kept unchanged. v2 is in [TALK-OUTLINE-v2.md](TALK-OUTLINE-v2.md) and [PAPER-PLAN-v2.md](PAPER-PLAN-v2.md).

## What v1 got right, and v2 keeps

- **Evidence discipline.** v1 has a pinned source register, an evidence ledger E1-E9 with an "allowed interpretation" for each value, and an explicit refusal of "100% detection", H50/H90, binomial intervals over six "independent" attacks, and a "10-25× more sensitive" replay claim.
- **Correct boundaries.** "DC input", not AC wall energy. Rest = DC minus rails, not DRAM. `powermetrics` is host software. The pilot result is on the GPU channel.
- **The threats-to-validity table and the related-work map.** v2 cites both instead of rewriting them.
- **The figure list F1-F11** (no Mac time). It stands.

I spot-checked E1, E2, E5, E6, E7, E8 and D1 against the KB slot fill, the P9/P10 records and V3; all agree. E3, E4 and E9 are queued for re-checking on 9 Nov.

## What was wrong or weak, and what v2 changed

1. **Half A was missing.** v1 is 16 slides, all of them on the tripwire. Ed's decision is a two-half talk, and the automation story is the half only this project can tell. **Change:** v2 has 11 half-A slides (11:00) built from the repo's own record, covering the architecture, four guardrails, two wins, two failure slides and the human role, plus a bridge. Half B is cut to 10 slides (10:55).

2. **Half B was too dense for its share of the time.** v1 gave the tripwire 23 minutes at 1:15-2:00 per slide, with four-decimal values on slides, and its "20-minute cut" removed narration rather than slides. **Change:**
   - two significant figures on slides, full precision in the paper;
   - one message per slide;
   - three named whole-slide cuts (A3, A7, B4) that take the talk to about 21:20 without touching the caveat slides.

3. **The paper schedule did not meet Ed's goal.** v1 drafts the paper on 1-9 December, after the talk. Ed wants it "ideally mostly done" by 30 November. v1 also had no owners and no Nov 9-30 milestones. **Change:**
   - Sol drafts and Opus re-derives every number;
   - Ed writes the intro and conclusion;
   - a dated plan from the 9 Nov ledger freeze through BYTES 12/15 Nov, v0.5 on 16 Nov, the Fable checkpoint on 21 Nov and the talk evidence freeze on 22 Nov, to v0.95 on 28 Nov;
   - variant B is the default, and v4 (variant A) is an insert only.

4. **The evidence freeze was too early and too blunt.** v1 froze on 7-8 November, three weeks before the talk, and banned all v4 content. **Change:** the talk freezes on 22 Nov. The v4 slides (B9, A6, A9) may show **gate status and exit classes**, never values. That keeps blinding intact while letting the talk say where v4 stands.

5. **The trust boundary was buried, so the meter claim could be misread.** v1 mentions that the pilot channel is host software only in a figure note and a ledger line. A listener could leave thinking the pilot used the external meter. R11-3 (item 212) also makes v4's registered residual stay GPU energy, with DC-in only as a secondary analysis and a qualified DC endpoint deferred to v5. **Change:** slide B2 says it outright, B9 repeats it, and §9 of the paper lists it as a threat.

6. **No research-operations or AI-use disclosure in the paper.** A study whose code, analyses and drafts were largely written by AI agents should say so, and most venues require it. **Change:** Appendix A ("Research operations and AI-use statement"), drafted by the lead and cross-reviewed by Sol.

7. **The squeeze slides did not reflect the cross-family adjudication.** v1 was written before AGREEMENT-FINAL and R11. **Change:**
   - B8 cites V01 ("an empirical bounded hypothesis, not a partition theorem");
   - B10 uses the adopted choices: D07 joint rule, D09 endpoint (side-task success with no joint alarm, per assigned attempt), and D12 trusted time plus monitor as a comparator;
   - the v5 design is described as still under competition.

8. **Slide budget misallocated.** v1 gave the roadmap its own slide (F11, 1:15) and gave BYTES accounting, which is peripheral to the tripwire claim, its own 1:15 slide.
   - **Change:** the roadmap is folded into B10, and BYTES is the cuttable slide B4. BYTES stage-1/2 results enter only from an admitted release, gated on 12/15 Nov.

## Corrections to the brief and the showcase page (do not repeat these on slides)

- **"Nine refusals" (R0).** The record shows **11 unsuccessful R0 attempts, of which 7 were contention refusals by routine macOS activity**. The other 4 were a launcher defect, a model-load fault, a harness prompt defect and an untrusted sensor selection (`RUN_STATE.md` items 177-208). v2 uses 7 of 11.
- **"12 → 1 disagreeing families"** (`docs/research/energy-tripwire.html`). The release-hold trace reports **1,001 failing rows in 11 families**, all attributed to six defects. After r3, one cause (D5, 108 rows) remained. v2 uses the trace.
- **"37 h → 1 h 40 min."** The figure is in the record (item 197), but the like-for-like pair is 27.1 h against 1 h 46 min, and the earlier machine was more loaded (item 165). v2 shows both and the caveat.
- **"About 150 agents."** This is the page's own count. Reconstructed from the PR provenance (#695, #696, #698, #702, #703), it comes to about 152 documented seats, checkers and syntheses, so v2 says "about 150" and labels it approximate.
- **The meter-path mistake.** It appears in several model documents and cross-reviews (LIT H3, C-V §3.2, XO-D #1, XO-V #5). Which seat first raised it is not traced, so v2 does not say "both families" or "all four seats".
- **The page's "records every joule the machine draws from the wall"** omits brick losses. On slides, say DC input after the brick.

## Open items for the lead

- Fill the `[FREEZE]` cells on 22 Nov: R0 re-run 11 and later R0/R1/W1 status, the r4 release-check exit class, and whether BYTES is inserted.
- Re-check E3, E4 and E9 on 9 Nov.
- Consider correcting `docs/research/energy-tripwire.html` ("12 → 1"; "every joule ... from the wall"; the FPR wording per R14) in a separate docs PR, since a talk audience may open it.
