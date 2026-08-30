Delta re-audit complete. Read the new plan in full, the pre-fix version, the prior audit, and the frozen draft in situ at every cited line.

## 1. Prior findings — resolution status (34)

**Fully resolved (27):** BL-1 (`TERM A/B` now confined to the plan's own outcome table, explicitly labelled "registry vocabulary"; zero occurrences in any A/B/C/D prose), BL-3, BL-4, BL-5, BL-6, BL-9, BL-10, BL-12, BL-14 ("gamma" now absent from the file entirely), SF-1, SF-3, SF-5, SF-6, SF-7, SF-8, SF-9, SF-10/15, SF-11, SF-12, SF-13, SF-14, SF-16, N-1, N-2, N-3, N-4.

**Partially resolved (7):**
- **BL-2** — "whole-window gate" is gone and the collision with §4's "whole-window drift allowance" is cured, but the replacement noun phrase **"floor window"** occurs 0 times in the draft. See F1.
- **BL-7** — U02–U05 cover the four sentences the prior audit named, but the new census itself surfaces two more uncovered future-tense sentences (line 11 "the prospective collection will not test the transfer"; line 264 "The two contrasts will form one Holm family…") and supplies **no ready text**. Mixed tense therefore remains inside the Abstract and the line-264 paragraph. See F6.
- **BL-8** — outcome D exists now, but its algebra is wrong. See F4.
- **BL-11** — the *number* prints once (Item 10), but `[PLAIN_LANGUAGE_RESULT_null]` prints in Item 10 **and** in H11 one sentence later. See S1.
- **BL-13** — registry IDs are out of prose ✓, but the caption/column contradiction is deferred to a sibling checklist rather than resolved: Table 2 keeps "Gross J/request", "J per prompt token", "J per output token" while the caption says no such value is reported. See S10.
- **SF-2** — one carrier per section is honoured, but consecutive-sentence boilerplate returned at finer grain. See S6.
- **SF-4** — registration voice holds for H12–H17; H18/H19 use present tense. See S4.

**Not resolved:** none.

## 2. Blockers (7)

**F1 — `floor window` and `claim-anchored limit` are unbuilt, and debut in the Abstract.** H06 C: *"the model's floor window could not supply a claim-anchored limit"*. `grep -c "floor window" draft-v1.md` = 0; `claim-anchored` = 1, at line **88** (§3), after the Abstract. Also in H01 A/B, H08 C, H27 C, H28 C, Item 10 C. **This is the original signature returning.** Rewrite H06 C: "The 1.5B or 7B records were excluded before any claim calculation, because the measurement session that would have supplied their limit did not produce one (§3 names the artifact's outcome for this) …". Elsewhere: "the 1.5B or 7B measurement session whose floor it supplies".

**F2 — "separately admitted" is unbuilt and carries a load-bearing distinction.** H09 C ("that separately admitted number"), H11 C, U02 C, Item 10 C. `grep -c "separately admitted"` = 0. The distinction it encodes — the null block is characterization evidence, admitted independently of the contrast evidence — exists only in the plan's Notes and never in the paper. Rewrite: "the identical-condition null block, whose evidence was admitted independently of the model comparison".

**F3 — REGRESSION: H17 C's antecedent is a variant that is not selected.** Post-fix H17 C opens *"**The same** registered transport assumption remained untested"*. Under C the A=B sentence is never printed, so "the same" points at nothing in the draft. (Pre-fix H17 C was self-standing — the fix round created this.) Rewrite: "The registration fixed each cell's timing term as measured with commanded GPU pulses and transported to sustained mixed inference load; that transport remained untested, and refused evidence supported no transport, phase-dominance, or model-ranking claim."

**F4 — outcome D is orthogonal to A/B/C but modelled as exclusive.** The plan's own H11 Notes say the null block is "admitted separately from the floor-window contrast evidence" — so the characterization campaign not running says nothing about whether dominance was reproduced. Yet Item 10 offers A|B|C|D as four alternatives, and **Item 10 D states no dominance outcome at all**, so under D §6's Results opening silently drops the paper's central result. Fix: make D a *prefix* clause combinable with A/B/C ("The identical-condition null block … was not collected in this campaign, so no null number is reported; the published floors below stand without their own falsification test. " + the A/B/C sentence).

**F5 — D is not propagated to the two other sentences on draft line 243.** The preamble scopes D to "H09, H10, H11, and Item 10". But **H02** (same line, last sentence) reads under every variant "Collection completed, and §6 reports the null result first…", and **U02** reads "The null row supported the floor only because…". Both are false under D. H11 has a D variant; its neighbours in the same paragraph do not.

**F6 — U02 converts a criterion into an assertion of a pass, and no failed-null branch exists.** Frozen: "It **will support** the floor **only if** every block interval contains zero…". U02 A=B: "The null row **supported** the floor **only because** every block interval **contained** zero…". If the null block fails containment, this sentence is false — and Table 1 (draft line 95) says "A completed failure withdraws that cell's floor from claim use", i.e. a failed null is consequential and live. Add a failed-null variant, or retense as a criterion: "The null row supported the floor on the registered criterion: every block interval had to contain zero, the mean interval to lie inside plus or minus the comparator, and the largest absolute block difference not to exceed it."

**F7 — U01 C puts "claim gate" in the Abstract, unbuilt.** *"because the evidence reached neither claim gate"*. The draft first builds gates at line **23** (§1: "The decision has two separate gates"); nothing on line 11 does. H06 C carefully avoided this term; U01 C reintroduces it three sentences later. Rewrite: "…because the required evidence was excluded before either test could be applied".

## 3. Should-fixes (14)

**S1** — Item 10 A/B/C and H11 A=B/C both print `[PLAIN_LANGUAGE_RESULT_null]`, in consecutive sentences. H11 → "The same null row also reports its mean block difference and composed interval and its same-cell comparator."
**S2** — H11's "the largest absolute block difference **already printed above**" is unpaid pointer work; delete the clause with S1's rewrite.
**S3** — five false or materially wrong "built at draft line N" Notes claims (12 spot-checked, 5 fail): H12 "model pair — draft lines 21 and 23" (Qwen2.5 / 4-bit appear first at **247**); H14/H15/H23/H25 "prompt processing / token generation — draft line 15" (line 15 says *prefill* and *decode*; the plain names are built at **11**); H17 "`_v4` transfer limitation — draft line **164**" (164 is the 9.724 ms bracket screen); H29 "short-prefill negative result — draft lines **252–258**" (252 is a LaTeX fragment, 258 is the next heading; the section is 245–256); H18 "total standard error / issued degrees of freedom — draft line **198**" (198 has neither). The Notes lines are the verification surface — false ones defeat the audit.
**S4** — H18 ("The registered analysis **forms**") and H19 ("the two raw p-values **are** ordered") are present-tense inside a subsection where H12–H17 are past. Line 264 would read: frozen *will form* + H18 *forms* + H19 *are ordered* + U06 *remains* — four tenses in one paragraph, in the file that exists to remove exactly that.
**S5** — H05 A=B "the analysis **constructed**" vs H05 C "the analysis **constructs**" at the same site.
**S6** — consecutive-sentence boilerplate: H13/H14/H15 C end "…was admitted under the same refusal" three sentences running; H18 C and H19 C both end "…and no phase-dominance or model-ranking claim follows" back-to-back. Collapse H13–H15 C to one sentence; H19 C → "Nor were two p-values available to order."
**S7** — §1's designated refusal carrier is H08 C (draft line **31**), but H03 C uses "under the same refusal" at line **30**. The reader meets the back-reference first; its only prior antecedent is the Abstract's. Swap the carrier to H03, or make H03 C read "under the refusal stated in the abstract".
**S8** — Item 60's paragraph now opens with two consecutive sentences both asserting tamper evidence ("The repository provides internal consistency and tamper evidence…" / "The repository is tamper-evident…"). The ruled sentence is verbatim, so fix sentence 1: "The record proves internal consistency, not third-party provenance."
**S9** — H26 A=B "only the floor gate is reported when its **exact conservative outcome** issues" — `conservative` occurs 0 times in the draft; and a conditional does not belong in a table caption.
**S10** — H20 A=B "the issued artifacts define no **reported-mean field**" is artifact-schema vocabulary in prose (`reported-mean` = 0 in draft). Say "no issued artifact reports a gross phase-energy value or its endpoints for these cells." Same caption still contradicts three live table columns (BL-13 residue).
**S11** — H22 A adds a third item ("then the ratio of its timing-widened value to its point-only repeatability value") to a table whose only floor column is "Cell floor (labeled)"; no rendering is specified. H22 B silently drops the label with no explanation, though the frozen column header still promises one.
**S12** — H29 B "…(Sections 3–4) **produced the result**, while the falsifier **decided** as §6 reports" — "produced the result" is content-free, and "decided" appears twice in one sentence ("decidable and decided it" … "decided as §6 reports").
**S13** — "claim calculations" (H05 C, H06 C) is a new near-synonym for the draft's built "could support a claim" / "claim-bearing"; use the built form.
**S14** — H16 C "no claim-bearing detection-floor artifact **issued**" — intransitive "issued" is internal jargon; "no claim-bearing detection floor was published".

## 4. Nits (4)

**N1** H06 C's parenthetical "(§3 names the artifact's outcome for this)" is the only section pointer in an Abstract that has none. **N2** H07's Notes count the phrase "By the rule stated below" but the sentence reads "with the outcome decided by the rule stated below". **N3** H27 A's "Because edge placement dominated repeatability in both phases" restates the immediately preceding frozen sentence's condition, and drops "edge placement" from "characterize the named workload boundary". **N4** H10 carries outcome labels ("A = B — characterization collected") on what is purely a routing instruction.

## 5. Back-reference discipline

Carriers verified in **draft order**, not plan order: Abstract → H06 (falsifier + refusal) ✓, precedes U01 ✓. §1 → falsifier = frozen line 21 ✓ (H03/H07/H08 refer back in 5–7 words ✓); refusal = H08 C at line 31, **violated by H03 C at line 30** (S7). §6 Results → Item 10 ✓ (precedes H11, U02, H02). §6 Demonstration-fixed (260–264) → no local carrier by design; all eight back-refs resolve to Item 10 C at 243, which the reader has passed ✓ (heading order in the draft is Results 240 → negative result 245 → Demonstration-fixed 258). §6 tables → H01 at 274 ✓ precedes 276/285. §7 → H27 ✓ (sole hazard). §10 → H28 ✓ precedes H29. All back-references are ≤8 words as claimed. The only ordering failure is S7.

## 6. Verdict

**FAILS the first-use test.** Prior-round arithmetic: 27 of 34 findings fully resolved, 7 partial, 0 unresolved. New: **7 blockers, 14 should-fixes, 4 nits**, of which **3 are regressions introduced by this fix round** (F3 dangling antecedent in H17 C; S1 duplicated outcome token from the BL-11 fix; S8 consecutive restatement from the SF-14 fix).

**The original signature returned.** Four terms doing load-bearing technical work ship into paper prose with no build anywhere in the frozen draft — "floor window", "claim-anchored limit", "separately admitted", "exact conservative outcome" — and two of them, plus "claim gate", make their debut in the **Abstract**, which is exactly where BL-1/BL-2/BL-3 landed last round.