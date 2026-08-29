# Round-7 retensing plan (prepared while draft-v1.md is frozen)

> **STATUS (2026-08-29): HELD at the standing escalation trigger — NOT yet usable for mechanical substitution.**
> Two consecutive pedagogy audits (`docs/process_traces/2026-08-27-t26/paper-round7-prep/01-…`, `02-…`) failed with the same signature: technical vocabulary shipped into A/B/C prose that the frozen draft does not build before the insertion line, debuting in the Abstract (round 1: "TERM A/B", "whole-window gate", "gamma"; round 2 after the fix: "floor window", "claim-anchored limit", "separately admitted", "exact conservative outcome", "claim gate"); the Sol fidelity seat (`03-…`) independently found the same class (`1.5B`/`7B`/`§3` at draft lines 11/31/243). No third editing round was run. The remaining findings in `02-…` (7 blockers, 14 should-fixes, 4 nits) and `03-…` F1/F2 await the magistrate's ruling on the structural cure.
> Verified and standing: all 35 frozen quotes are byte-exact on their named draft lines; all 24 tokens and 20 row ids exist in the registry; Item 60 byte-matches Addendum 8; TERM semantics match `joulewise/detection_floor.py`.

This file is the round-7 substitution sheet; it does not edit the frozen draft.
Round 7 selects one ready sentence at each hazard after the issued artifacts and replay fence fix the outcome.
Outcome A means the code's per-component timing-widened term exceeds its guarded point-only term in both phases; B means admitted evidence produces at least one non-exceeding phase; C means a required window or contrast is refused before that predicate can be evaluated; D means the characterization campaign was not run.
The sixteen registry TERM rows decide A versus B. The two floor-window refusal tokens and the demonstration contrast's decode and prompt verdicts decide C, which takes precedence over A/B selection. The fill manifest's `characterization.run` field decides D only at H09, H10, H11, and Item 10.

At fill time, print only the refusal-reason token or tokens for windows that actually refused. Never print both candidate tokens joined by “or”: print one issued reason for one refused window, or both issued reasons separately if both windows refused.

## Outcome definitions

**Outcome A — dominance reproduced.** For every claim-bearing absolute and comparative component in both phases, the item-34 code predicate is true: the exact linear corner maximum (registry vocabulary: TERM B) strictly exceeds the guarded point-only repeatability value (registry vocabulary: TERM A).

**Outcome B — dominance not reproduced.** Required evidence is admitted, but in at least one phase at least one registry TERM B does not exceed its matching registry TERM A, so item 8 rejects dominance for that phase; one failed phase narrows the claim to the other, while failure in both leaves a calibration that corrected its clock-model error followed by a prospective null.

**Outcome C — contrast refused.** The 1.5B or 7B floor window was refused before its evidence reached either claim gate, with `[REFUSAL_REASON_1p5B_floor_window]` and `[REFUSAL_REASON_7B_floor_window]` as the only permitted floor-window reason tokens, or the demonstration contrast lacked an authenticated decode or prompt verdict (`[[NO-TOKEN: DS-32 — authenticated conservative decode verdict]]`; `[[NO-TOKEN: PG-08 — authenticated conservative prompt verdict]]`). The dominance predicate is therefore unevaluated, and the paper makes neither a phase-dominance claim nor a model-ranking claim.

**Outcome D — characterization campaign not run.** The fill manifest records `characterization.run` as false, so no authenticated characterization report can supply the null row; no characterization placeholder is printed without a supplier.

The phase decision is mechanical and component-specific; there is no invented aggregate. Prompt processing uses the first four pairs below and token generation uses the last four. A phase passes only if all four TERM B values strictly exceed their paired TERM A values; otherwise that phase uses the B wording, while an admitted passing phase uses the A wording.

| Phase | Model/component | Guarded point-only TERM A (registry vocabulary) | Exact corner TERM B (registry vocabulary) |
|---|---|---|---|
| prompt processing | 1.5B absolute | `[TERM_A_1p5B_prompt_abs_J]` | `[TERM_B_1p5B_prompt_abs_J]` |
| prompt processing | 1.5B comparative | `[TERM_A_1p5B_prompt_cmp_J]` | `[TERM_B_1p5B_prompt_cmp_J]` |
| prompt processing | 7B absolute | `[TERM_A_7B_prompt_abs_J]` | `[TERM_B_7B_prompt_abs_J]` |
| prompt processing | 7B comparative | `[TERM_A_7B_prompt_cmp_J]` | `[TERM_B_7B_prompt_cmp_J]` |
| token generation | 1.5B absolute | `[TERM_A_1p5B_decode_abs_J]` | `[TERM_B_1p5B_decode_abs_J]` |
| token generation | 1.5B comparative | `[TERM_A_1p5B_decode_cmp_J]` | `[TERM_B_1p5B_decode_cmp_J]` |
| token generation | 7B absolute | `[TERM_A_7B_decode_abs_J]` | `[TERM_B_7B_decode_abs_J]` |
| token generation | 7B comparative | `[TERM_A_7B_decode_cmp_J]` | `[TERM_B_7B_decode_cmp_J]` |

The published component quantity is the corner-widened floor, which is at least TERM B; the published cell's resolution bound is the larger component floor, and the artifact's `floor_gate_j` is the separately drift-added gate. Neither published quantity substitutes for TERM B in the falsifier. Where a phase-specific source sentence needs narrowing, select the A sentence for a passing phase and the B sentence for a failing phase; where one source sentence covers both phases, its A/B wording states the mechanical all-four rule explicitly.

## Substitution table

### H01 — §6 Demonstration results — draft line 274 — VARIANT-SELECTED

**Frozen quote (verbatim):** "**[RESULT PENDING ISSUED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into these tables, and none appears anywhere in this paper except the explicitly labeled instrument diagnostics of Sections 3, 6, and 7.]**"

**Fails:** A, B, and partial C: the current fill machinery cannot produce a complete paper-facing lead-in for every admitted or refused outcome.

**A — dominance reproduced:** Both model floor windows were admitted; the tables below report the issued cells and the registered contrast decisions.

**B — dominance not reproduced:** Both model floor windows were admitted; the tables below report the issued cells and registered contrast decisions, but at least one timing-widened value did not exceed its point-only repeatability value, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B floor window was refused before its evidence reached either claim gate, recording the artifact outcome already named in the Results opening as the reason; the tables omit quantities that no issued artifact supplies, and no phase-dominance or model-ranking claim is made.

**Notes:** Branch bookkeeping stays here: admitted A/B use the renderer's A, B1, or B2 predicate; refused C uses D, C1, C2, or C3; the sibling checklist owns the path and fill mechanics. First-use audit: model floor windows / issued cells — floor cells and publication rule at draft lines 185–189; contrast decisions / claim gates — draft lines 23 and 193–204; point-only repeatability / timing-widened — draft lines 21 and 185; corrected-clock calibration / prospective null — draft lines 17 and 21. The sibling checklist's STOP_FILL rows govern every table fill.

### H02 — §6 Results — draft line 243 — FIXED

**Frozen quote (verbatim):** "Collection has not occurred, so no null value or outcome is stated here."

**Fails:** A/B/C: every round-7 outcome presupposes that collection ran and issued a verdict.

**A — dominance reproduced:** Collection completed, and §6 reports the null result first before the reproduced attribution-dominance result.

**B — dominance not reproduced:** Collection completed, and §6 reports the null result first before the falsifier result stated in the Results opening.

**C — contrast refused:** Collection completed, but the required evidence was excluded under the same refusal; §6 records the reason, and no phase-dominance or model-ranking claim follows.

**Notes:** Item 10 supplies the complete Results opening. First-use audit: identical-condition null / floor test — draft lines 95 and 185–187; attribution dominance / falsifier — draft line 21; claim gates / refusal — draft lines 23 and 202–204.

### H03 — §1 Introduction — draft line 30 — FIXED

**Frozen quote (verbatim):** "The second contribution is a cell-specific resolution bound and the prospective attribution-dominance finding; §3 characterizes the instrument, §4 composes the bound, and §6 reports the test."

**Fails:** B/C structurally: “the … finding” presupposes a positive, admitted finding rather than a null or refusal.

**A — dominance reproduced:** The second contribution is the cell-specific resolution bound and the reproduced attribution-dominance result; §3 characterizes the instrument, §4 composes the bound, and §6 reports the test.

**B — dominance not reproduced:** The second contribution is the cell-specific resolution bound and the result under the falsifier stated above; §3 characterizes the instrument, §4 composes the bound, and §6 reports the test.

**C — contrast refused:** The second contribution is the cell-specific resolution-bound construction under the same refusal; §3 characterizes the instrument, §4 composes admitted bounds, and §6 reports why no phase-dominance or model-ranking claim follows.

**Notes:** First-use audit: cell-specific resolution bound — physically built at draft lines 15–19; falsifier / timing-widened and point-only repeatability — draft line 21; refusal / claim consequence — draft line 23. The back-references “under the falsifier stated above” and “under the same refusal” are six and four words.

### H04 — §7 Discussion and limitations — draft line 296 — FIXED heading

**Frozen quote (verbatim):** "What the finding changes"

**Fails:** B/C structurally: it assumes that an attribution-dominance finding was made.

**A — dominance reproduced:** What reproduced dominance changes

**B — dominance not reproduced:** What the null outcome changes

**C — contrast refused:** What a refused contrast establishes

**Notes:** Heading forms intentionally remain headings. First-use audit: dominance / null outcome — draft line 21; refused contrast — draft lines 23 and 202–204. Draft lines 292–294 establish the discussion context, and the following paragraph uses the same selected outcome.

### H05 — §Abstract — draft line 11 — FIXED

**Frozen quote (verbatim):** "For each group of like-for-like runs, called a cell, the analysis will construct the cell's resolution bound — the artifact calls it the detection floor — “the largest false difference this measurement system can manufacture.”"

**Fails:** C: refused evidence need not yield a claim-bearing cell bound.

**A = B — admitted evidence:** For each group of like-for-like runs, called a cell, the analysis constructed the cell's resolution bound — the artifact calls it the detection floor — “the largest false difference this measurement system can manufacture.”

**C — contrast refused:** For each group of like-for-like runs, called a cell, the analysis constructs the cell's resolution bound — the artifact calls it the detection floor — “the largest false difference this measurement system can manufacture”; for any 1.5B or 7B cell excluded from claim calculations, no bound that could support a claim was constructed.

**Notes:** First-use audit: cell — glossed inline as a group of like-for-like runs; resolution bound / detection floor — quantity built and both names glossed inline; claim calculations / bound that could support a claim — plain consequence glossed inline and formalized later at draft lines 86 and 193–204. The Abstract prints no refusal-reason identifier; H06 carries its sole refusal explanation, and §3 later names the artifact outcome family.

### H06 — §Abstract — draft line 11 — FIXED

**Frozen quote (verbatim):** "The results will test whether boundary assignment contributes more than run-to-run variation to the bound for prompt processing and token generation on the named configuration."

**Fails:** C: admission refusal leaves the dominance predicate unevaluated.

**A — dominance reproduced:** In both prompt processing and token generation, the energy that uncertain boundary placement can move exceeded the spread between repeated identical runs, so boundary assignment contributed more than run-to-run variation on the named configuration.

**B — dominance not reproduced:** In at least one phase, the energy that uncertain boundary placement can move did not exceed the spread between repeated identical runs; if both phases failed, the paper retains its boundary calibration and reports a prospective null — the test fixed before collection found no phase in which boundary assignment exceeded repeated-run spread.

**C — contrast refused:** The records were excluded from claim calculations because the model's floor window could not supply a claim-anchored limit (§3 names the artifact's outcome for this), so the boundary-versus-repeatability test remained unevaluated and the paper makes no phase-dominance or model-ranking claim.

**Notes:** This is the Abstract's sole full falsifier carrier and sole full refusal carrier. First-use audit: prompt processing / token generation — draft line 11's opening clause; uncertain boundary placement / repeated-run spread — physically built in the preceding Abstract sentences at draft line 11; prospective null — glossed inline as the result of a test fixed before collection; boundary calibration — built by the preceding pulse-train sentence at draft line 11; claim-anchored limit / artifact outcome — glossed inline and named formally at draft line 88. No §4 vocabulary or raw refusal identifier appears here.

### H07 — §1 Introduction — draft line 21 — FIXED

**Frozen quote (verbatim):** "The two components will be produced independently for every phase cell that could support a claim."

**Fails:** C: refused evidence may produce no admissible component pair.

**A — dominance reproduced:** The two components — the spread among repeated runs, and the energy that calibrated boundary uncertainty can move across the edge — were produced independently for every phase cell that carried a claim, and the second was larger in each.

**B — dominance not reproduced:** The two components were produced independently for every phase cell that carried a claim, with the outcome decided by the rule stated below.

**C — contrast refused:** No component pair was admitted where required records were excluded, so dominance remained unevaluated and no phase-dominance or model-ranking claim is made.

**Notes:** First-use audit: repeated-run spread / boundary reassignment / phase cell — physically built at draft lines 15–19; calibrated boundary uncertainty — draft lines 17 and 19; outcome rule — stated in the unchanged sentences later on draft line 21; required-record exclusion and claim consequence — explained inline and built fully at draft line 23. “By the rule stated below” is five words.

### H08 — §1 Introduction — draft line 31 — FIXED

**Frozen quote (verbatim):** "The third contribution is the decision behavior the prospective demonstration will exercise — two gates, printed refusals, and the resolvability rule; §5 defines when collection stops, and §6 will report the resulting decisions."

**Fails:** C: evidence refusal bypasses both claim gates, so the stated two-gate exercise does not occur.

**A — dominance reproduced:** The third contribution is the demonstration's recorded decision behavior — separate magnitude and direction gates, printed refusals, and the resolvability rule; §5 defines collection stops, and §6 reports the decisions.

**B — dominance not reproduced:** The third contribution is the demonstration's recorded decision behavior — separate magnitude and direction gates, printed refusals, and the resolvability rule — with the falsifier decided as stated above; §5 defines collection stops, and §6 reports the decisions.

**C — contrast refused:** The 1.5B or 7B floor window was refused before its evidence reached either claim gate; §3 names the artifact's outcome, §5 defines that stop, §6 prints it, and no phase-dominance or model-ranking claim is made.

**Notes:** This is §1's sole full refusal carrier; the unchanged draft line 21 is §1's falsifier carrier. First-use audit: magnitude and direction gates / printed refusal / resolvability rule — draft line 23; floor-window side path around both gates — draft lines 202–204; artifact outcome-name family — draft line 88. “With the falsifier decided as stated above” is seven words.

### H09 — §4 The resolution bound and how it is composed — draft line 187 — FIXED

**Frozen quote (verbatim):** "Passing the identical-condition null block at the corner-widened resolution bound tests the bound itself, and §6 reports that null number first."

**Fails:** C: no admitted null number is guaranteed.

**A = B — characterization collected:** The identical-condition null block tests the bound itself: with the same workload in A and B, every nonzero block difference is manufactured by the measurement system, so the block passes only when its largest absolute difference stays inside the corner-widened resolution bound; §6 reports that number first.

**C — contrast refused:** The identical-condition null block tests the bound itself: with the same workload in A and B, every nonzero block difference is manufactured by the measurement system, so the block passes only when its largest absolute difference stays inside the corner-widened resolution bound; §6 reports that separately admitted number first.

**D — characterization campaign not run:** The identical-condition null block tests the bound itself: with the same workload in A and B, every nonzero block difference is manufactured by the measurement system, so the block passes only when its largest absolute difference stays inside the corner-widened resolution bound; §6 reports whether that block was collected.

**Notes:** First-use audit: identical-condition null / A/B/B/A block mechanism — draft lines 95 and 185–187; corner-widened resolution bound — draft line 185 immediately before this sentence; largest absolute difference containment — draft line 95. No number is printed in §4.

### H10 — §6 Results — draft line 243 — FIXED

**Frozen quote (verbatim):** "The identical-condition null result will be reported first because it tests the floor itself: when A and B are the same workload, every nonzero A/B/B/A block difference is manufactured by the measurement system."

**Fails:** C: a refused window may issue only refusal diagnostics, not this result.

**A = B — characterization collected:** Superseded by Item 10; insert no second opening sentence at this site.

**C — contrast refused:** Superseded by Item 10; insert no second opening sentence at this site.

**D — characterization campaign not run:** Superseded by Item 10; insert no second opening sentence at this site.

**Notes:** Item 10 replaces this frozen sentence and is the only §6 opening. First-use audit: no paper-facing technical term is introduced by these routing instructions. Superseded by Item 10.

### H11 — §6 Results — draft line 243 — FIXED

**Frozen quote (verbatim):** "The issued result will give the mean block difference and its composed interval, the largest absolute block difference, the independently issued same-cell comparator, and the registered outcome."

**Fails:** C: those claim-bearing quantities need not issue.

**A = B — characterization collected:** The issued null row reports the largest absolute block difference already printed above, its mean block difference and composed interval, its same-cell comparator, and the registered outcome `[PLAIN_LANGUAGE_RESULT_null]`.

**C — contrast refused:** The separately admitted null row reports the largest absolute block difference already printed above, its mean block difference and composed interval, its same-cell comparator, and the registered outcome `[PLAIN_LANGUAGE_RESULT_null]`; the refusal clause applies only to the contrast evidence.

**D — characterization campaign not run:** No issued null row supplies a largest absolute block difference, mean block difference, composed interval, same-cell comparator, or registered outcome because the characterization campaign was not run.

**Notes:** The null number is not reprinted here; Item 10 prints it once. First-use audit: mean block difference / composed interval / same-cell comparator / largest absolute block difference — draft lines 95 and 243; registered outcome — draft lines 86 and 95. Registry row 444 supplies `[PLAIN_LANGUAGE_RESULT_null]`; the null block is characterization evidence admitted separately from the floor-window contrast evidence.

### H12 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "The prospective demonstration will compare 4-bit Qwen2.5 7B with 1.5B on the named M3 Max, MLX, and *powermetrics* configuration."

**Fails:** A/B/C temporally: at round 7 the campaign is no longer prospective; under C the comparison may remain unevaluated.

**A = B — admitted comparison:** The demonstration was registered before collection to compare 4-bit Qwen2.5 7B with 1.5B on the named M3 Max, MLX, and *powermetrics* configuration, and ran as registered.

**C — contrast refused:** The demonstration was registered before collection to compare 4-bit Qwen2.5 7B with 1.5B on the named M3 Max, MLX, and *powermetrics* configuration, but the comparison was not evaluated under the same refusal.

**Notes:** Registration voice preserves the subsection's fixed-before-collection force. First-use audit: model pair / M3 Max / MLX / *powermetrics* configuration — draft lines 21 and 23; registered comparison — fixed design built at draft lines 23 and 260; refusal — draft lines 202–204. “Under the same refusal” is four words.

### H13 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "Each contrast will use ten independent A/B/B/A blocks, where A is 1.5B, B is 7B, and one block difference is `(B1 + B2 - A1 - A2)/2`."

**Fails:** C: an admission refusal can prevent ten admitted blocks.

**A = B — admitted comparison:** The demonstration was registered to use ten independent A/B/B/A blocks per contrast, with A as 1.5B, B as 7B, and block difference `(B1 + B2 - A1 - A2)/2`, and admitted contrasts ran as registered.

**C — contrast refused:** The demonstration was registered to use ten independent A/B/B/A blocks per contrast, with A as 1.5B, B as 7B, and block difference `(B1 + B2 - A1 - A2)/2`, but no ten-block contrast was admitted under the same refusal.

**Notes:** First-use audit: A/B/B/A block order / block-difference formula — draft lines 227–229; independent block / model-letter mapping — glossed inline; admitted contrast — draft lines 86 and 227–229. “Under the same refusal” is four words.

### H14 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "Token generation will use the fixed 128-token prompt."

**Fails:** some C cases: refusal can occur before any admitted token-generation run.

**A = B — admitted comparison:** As registered, token generation used the fixed 128-token prompt.

**C — contrast refused:** The token-generation arm registered the fixed 128-token prompt, but no token-generation comparison was admitted under the same refusal.

**Notes:** First-use audit: token generation — draft line 15; fixed 128-token prompt / registered arm — glossed inline at this source site. “Under the same refusal” is four words.

### H15 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "Prompt processing will use the fixed synthetic 256-token prompt with identical token identifiers across model tokenizers."

**Fails:** some C cases: refusal can occur before that arm runs.

**A = B — admitted comparison:** As registered, prompt processing used the fixed synthetic 256-token prompt with identical token identifiers across model tokenizers.

**C — contrast refused:** The prompt-processing arm registered the fixed synthetic 256-token prompt and identical token identifiers across model tokenizers, but no prompt-processing comparison was admitted under the same refusal.

**Notes:** First-use audit: prompt processing — draft line 15; fixed synthetic 256-token prompt / tokenizer identity — glossed inline at this source site and carried into the table at draft line 276. “Under the same refusal” is four words.

### H16 — §6 Demonstration fixed before collection — draft line 262 — FIXED

**Frozen quote (verbatim):** "Each model and phase will have its own cell's resolution bound — the artifact calls it the detection floor — **the largest false difference this measurement system can manufacture**."

**Fails:** C: refused cells publish no claim-bearing floor.

**A = B — admitted cells:** The registration assigned each model-and-phase cell its own resolution bound — the artifact calls it the detection floor — **the largest false difference this measurement system can manufacture**; every admitted cell later published its own bound.

**C — contrast refused:** The registration assigned each model-and-phase cell its own resolution bound, but no claim-bearing detection-floor artifact issued for evidence excluded under the same refusal.

**Notes:** First-use audit: model-and-phase cell — draft lines 15, 19, and 21; resolution bound / detection floor / physical gloss — draft lines 11 and 19; admitted cell / claim-bearing — draft lines 86 and 185–189. “Under the same refusal” is four words.

### H17 — §6 Demonstration fixed before collection — draft line 262 — FIXED

**Frozen quote (verbatim):** "Its timing term will be measured with commanded GPU pulses and transported to sustained mixed inference load; that transport is an explicit assumption, and the prospective collection does not test it."

**Fails:** some C cases: admission can refuse before an applicable timing term is established.

**A = B — registered assumption:** The registration fixed each cell's timing term as measured with commanded GPU pulses and transported to sustained mixed inference load; that transport remained an explicit assumption untested by `_v4`.

**C — contrast refused:** The same registered transport assumption remained untested, and refused evidence supported no transport, phase-dominance, or model-ranking claim.

**Notes:** First-use audit: cell timing term / commanded GPU pulses / transport to sustained mixed inference load — draft lines 45–53 and 164; `_v4` transfer limitation — draft lines 19 and 164. No outcome boilerplate restates the falsifier.

### H18 — §6 Demonstration fixed before collection — draft line 264 — FIXED

**Frozen quote (verbatim):** "Each raw two-sided Student-*t* p-value will use the contrast estimate divided by its total standard error and its issued degrees of freedom."

**Fails:** C: an unevaluated contrast has no raw p-value.

**A = B — admitted contrast:** The registered analysis forms each raw two-sided Student-*t* p-value from the contrast estimate divided by its total standard error and issued degrees of freedom.

**C — contrast refused:** Under the same refusal, no raw p-value is formed and no phase-dominance or model-ranking claim follows.

**Notes:** First-use audit: two-sided Student-*t* p-value / contrast estimate / total standard error / issued degrees of freedom — draft line 198; admitted contrast — draft lines 86 and 198. “Under the same refusal” is four words.

### H19 — §6 Demonstration fixed before collection — draft line 264 — FIXED

**Frozen quote (verbatim):** "After ordering the two p-values, the smaller will be compared with 0.025, then, only if it passes, the larger with 0.05."

**Fails:** C: refusal can leave no two p-values to order.

**A = B — admitted contrasts:** As registered, the two raw p-values are ordered; the smaller is compared with 0.025 and, only after it passes, the larger with 0.05.

**C — contrast refused:** Under the same refusal, there are no two p-values to order and no phase-dominance or model-ranking claim follows.

**Notes:** First-use audit: raw p-values / ordered Holm thresholds — draft lines 198 and 264; the preceding unchanged sentence at draft line 264 is the sole §6 Holm-family tag, so this sentence does not retag it. “Under the same refusal” is four words.

### H20 — §6 Demonstration results — draft line 276 — FIXED

**Frozen quote (verbatim):** "A gross cell will contain the issued phase-energy estimate and composed lower and upper endpoints."

**Fails:** C and currently A/B: refusal issues no claim-bearing cell, and the admitted branches still have no issued reported-mean fields or composed endpoints.

**A = B — issued artifacts:** No gross phase-energy value is reported: the issued artifacts define no reported-mean field or composed endpoints for these cells, and no floor component is substituted for one.

**C — contrast refused:** No gross phase-energy value is reported under the same refusal: the issued artifacts define no reported-mean field or composed endpoints for these cells, and no floor component is substituted for one.

**Notes:** First-use audit: gross phase-energy value / reported mean — table context at draft lines 276–283 and glossed inline by the missing field; composed endpoints — draft lines 193–200; floor component — draft lines 178–189. Registry rows DS-09, DS-13, DS-17, and DS-21 move to bookkeeping here. The table columns remain; their fill is governed by the checklist's exact STOP_FILL sentences for those four rows. “Under the same refusal” is four words.

### H21 — §6 Demonstration results — draft line 276 — FIXED

**Frozen quote (verbatim):** "A companion per-token cell will contain the tokenizer-scoped value whose authenticated runtime-observed denominator is fixed by the issuing schema; [[NEEDS-VALUE: D-123 producing schema for each per-token numerator, denominator, and point-or-interval rendering; the results-fill registry records these suppliers as unknown]]."

**Fails:** A/B/C currently: the promised producing schema and authenticated denominator fields do not exist.

**A = B — issued artifacts:** No per-token value is reported: the issued artifacts define no runtime-observed numerator and denominator field for these cells, and no requested maximum or generator estimate is substituted for one.

**C — contrast refused:** No per-token value is reported under the same refusal: the issued artifacts define no runtime-observed numerator and denominator field for these cells, and no requested maximum or generator estimate is substituted for one.

**Notes:** First-use audit: per-token value / runtime-observed numerator and denominator — table context and inline gloss at draft line 276; tokenizer scope — draft lines 260 and 276. Registry rows DS-10, DS-14, DS-18, and DS-22 move to bookkeeping here. The table columns remain; their fill is governed by the checklist's exact STOP_FILL sentences for those four rows. “Under the same refusal” is four words.

### H22 — §6 Demonstration results — draft line 276 — FIXED

**Frozen quote (verbatim):** "A floor cell will contain its magnitude and permitted label; n will count admitted independent run bundles, not power records."

**Fails:** C: a refused cell may publish neither magnitude nor label.

**A — dominance reproduced:** Each published floor cell reports its magnitude, then the ratio of its timing-widened value to its point-only repeatability value, then the permitted label as that ratio's one-line consequence; n counts admitted independent run bundles, not power records.

**B — dominance not reproduced:** Each published floor cell reports its magnitude, then the ratio of its timing-widened value to its point-only repeatability value; at least one timing-widened value did not exceed point-only repeatability under the falsifier stated above, and n counts admitted independent run bundles, not power records.

**C — contrast refused:** Under the same refusal, no floor-cell magnitude or label is published, dominance remains unevaluated, and no phase-dominance or model-ranking claim follows.

**Notes:** First-use audit: published floor cell / magnitude / permitted label — draft lines 185–189; timing-widened / point-only repeatability — draft lines 21 and 185; admitted independent run bundles / power records — glossed inline at this source site. Magnitude precedes ratio and label per items 20 and 34. “Under the falsifier stated above” and “under the same refusal” are six and four words.

### H23 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The point will be the mean of ten block differences."

**Fails:** C and prompt A/B currently: the contrast may be unevaluated, and the prompt token family is missing.

**A = B — admitted contrast:** The token-generation point estimate is `[E_decode_contrast_signed_J_per_request]` J per request; no issued artifact supplies a prompt-processing point estimate.

**C — contrast refused:** No contrast point estimate is reported under the same refusal, and no phase-dominance or model-ranking claim follows.

**Notes:** First-use audit: point estimate / mean of ten block differences — draft lines 227–229 and 285; token generation / prompt processing — draft line 15. Registry row DS-25 supplies `[E_decode_contrast_signed_J_per_request]` at line 362. `[[NO-TOKEN: PG-01 — authenticated prompt contrast estimate]]` records the missing prompt token family in Notes only (registry row PG-01, line 808). “Under the same refusal” is four words.

### H24 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The interval cell will contain the fully composed lower and upper endpoints; for the registered positive direction, the lower endpoint controls."

**Fails:** C and prompt A/B currently: no admitted interval is guaranteed, and prompt endpoints lack tokens.

**A = B — admitted contrast:** The token-generation decision interval is [`[E_decode_contrast_lower_J]`, `[E_decode_contrast_upper_J]`] J; no issued artifact supplies a prompt-processing interval, and, because the registered direction is positive, the lower endpoint is the one that decides the direction gate.

**C — contrast refused:** No composed interval is reported under the same refusal, dominance remains unevaluated, and no phase-dominance, directional, or model-ranking claim follows.

**Notes:** First-use audit: decision interval / fully composed endpoints / registered positive direction — draft lines 193–204 and 285; direction gate — draft lines 23 and 202–204. The interval is widened by the deterministic total built at draft line 196; it is not equated to the separately registered claim-side bound. Registry rows DS-26 supply `[E_decode_contrast_lower_J]` and `[E_decode_contrast_upper_J]` at lines 363–364. `[[NO-TOKEN: PG-02 — authenticated prompt lower endpoint]]` and `[[NO-TOKEN: PG-03 — authenticated prompt upper endpoint]]` stay in Notes only (registry lines 809–810). “Under the same refusal” is four words.

### H25 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The floor will be the larger arm-specific exact-cell floor."

**Fails:** C and prompt A/B currently: refusal supplies no claim floor; the prompt claim-floor token is missing.

**A = B — admitted contrast:** The token-generation claim floor is `[F_claim_decode_armwise_max_J]` J, the larger arm-specific exact-cell floor; no issued artifact supplies a prompt-processing claim floor.

**C — contrast refused:** No claim floor is reported under the same refusal, dominance remains unevaluated, and no phase-dominance or model-ranking claim follows.

**Notes:** First-use audit: claim floor / larger arm-specific exact-cell floor — draft lines 193–204 and 285; prompt processing / token generation — draft line 15. Registry line 366 supplies `[F_claim_decode_armwise_max_J]`. `[[NO-TOKEN: DS-33 — authenticated prompt armwise claim floor]]` stays in Notes only (registry row DS-33, line 806). “Under the same refusal” is four words.

### H26 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The sizing cell will contain `C = F + B` and signed planning clearance `|estimate| - C`."

**Fails:** A/B/C currently: decode `B_decode_claim_J` has no supplier, the prompt family is absent, and C supplies no admissible estimate/floor.

**A = B — admitted contrast:** The sizing sum `C = F + B` is not formed because no issued artifact supplies the claim-side bound; only the floor gate is reported when its exact conservative outcome issues.

**C — contrast refused:** Under the same refusal, the sizing sum `C = F + B` is not formed, and no phase-dominance or model-ranking claim is reported.

**Notes:** First-use audit: sizing sum `C = F + B` / signed planning clearance / floor gate — draft lines 272 and 285; claim-side bound — draft lines 196 and 285 distinguish it from the deterministic total. This is the item-33 omission. Registry rows DS-29 and PG-05 govern the absent claim-side bounds. `[[NO-TOKEN: DS-30 — authenticated decode floor-gate outcome]]` and `[[NO-TOKEN: PG-06 — authenticated prompt floor-gate outcome]]` stay in Notes only (registry lines 803 and 813). “Under the same refusal” is four words.

### H27 — §7 What the finding changes — draft line 298 — FIXED

**Frozen quote (verbatim):** "Experimental practice must therefore change upstream: characterize edge placement for the named workload boundary, form a separate bound for each configuration cell, and size a comparison against that bound before collection."

**Fails:** B/C structurally: under the positive heading, “therefore” treats reproduced dominance as established.

**A — dominance reproduced:** Because edge placement dominated repeatability in both phases, practice changes upstream: characterize the named workload boundary, form a bound for each configuration cell, and size the comparison before collection.

**B — dominance not reproduced:** Dominance was rejected wherever a timing-widened term failed to exceed repeatability, so the upstream change practice must still make is narrower: characterize edge placement for the named workload boundary and form a separate bound per configuration cell before sizing any comparison, whether or not edge placement dominates in a given phase.

**C — contrast refused:** The 1.5B or 7B floor window was refused before its evidence reached either claim gate, so the protocol demonstrates fail-closed evidence handling but supports no phase-dominance or model-ranking claim.

**Notes:** This is §7's sole full falsifier carrier and sole full refusal carrier. First-use audit: edge placement / repeatability / timing-widened — draft lines 19, 21, and 185; configuration-cell bound / sizing before collection — draft lines 193–204 and 260–285; fail-closed refusal — draft lines 202–204 and 300. Under A, both phases passed by definition.

### H28 — §10 Conclusion — draft line 356 — FIXED

**Frozen quote (verbatim):** "For each `_v4` prefill and decode cell, the test compares the point-only repeatability bound with the same cell after calibrated phase-edge positions widen its energy range."

**Fails:** C: refused evidence does not license that comparison.

**A — dominance reproduced:** For every admitted `_v4` prompt-processing and token-generation component, the timing-widened value exceeded the point-only repeatability value, reproducing attribution dominance in both phases.

**B — dominance not reproduced:** For every admitted `_v4` component the timing-widened value was compared with its point-only repeatability value, and at least one value did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B floor window was refused before its evidence reached either claim gate, so no comparison of the timing-widened value against the point-only repeatability value was licensed, dominance remained unevaluated, and no phase-dominance or model-ranking claim follows.

**Notes:** This is §10's sole full falsifier carrier and sole full refusal carrier. First-use audit: `_v4` prompt-processing and token-generation components — draft lines 185–189 and 260–264; timing-widened / point-only repeatability — draft lines 21 and 185; claim gates / refusal — draft lines 193–204; corrected-clock calibration / prospective null — draft lines 17 and 21. Paper prose uses the draft's physical names, not registry TERM labels.

### H29 — §10 Conclusion — draft line 356 — FIXED

**Frozen quote (verbatim):** "The contribution makes that outcome decidable: corrected in-window timing calibration (Section 2), independent construction and comparison of the cell-specific terms (Sections 3–4), and two claim gates that preserve refusals and the short-prefill negative result (Sections 4–6)."

**Fails:** C: refusal makes dominance undecided, not decided negative.

**A — dominance reproduced:** The contribution made that outcome decidable and decided it: corrected in-window timing calibration (Section 2) and independent per-component construction and comparison (Sections 3–4) reproduced dominance, while two claim gates (Sections 4–6) preserved the refusals and the short-prefill negative result.

**B — dominance not reproduced:** The contribution made that outcome decidable and decided it: corrected in-window timing calibration (Section 2) and independent per-component construction and comparison (Sections 3–4) produced the result, while the falsifier decided as §6 reports and two claim gates (Sections 4–6) preserved refusals and the short-prefill negative result.

**C — contrast refused:** The contribution made the registered comparison decidable but left dominance undecided rather than negative: corrected in-window timing calibration (Section 2), independent per-component construction (Sections 3–4), and two claim gates (Sections 4–6) preserved the refusal and the short-prefill negative result without licensing a phase-dominance or model-ranking claim.

**Notes:** First-use audit: corrected in-window timing calibration — draft lines 17 and 35–82; independent per-component construction — draft lines 178–189; claim gates / refusals — draft lines 193–204; short-prefill negative result — draft lines 23 and 252–258. Every contribution sentence retains the section pointers required by item 31. “The falsifier decided as §6 reports” is six words.

## Uncovered future-tense sentences on hazard lines (NEEDS-RULING: beyond the ruled 29)

These six blocks do not renumber or enlarge the ruled set of 29 `H` hazards. They are proposed because leaving them unchanged would mix future and completed tense inside paragraphs otherwise retensed in round 7. Draft line 262's sentence “No floor will transport across model, phase, or prompt length.” remains a standing rule — no change proposed.

### U01 — §Abstract — draft line 11 — NEEDS-RULING

**Frozen quote (verbatim):** "A model-size comparison will exercise the decision rule: report a direction only when the observed difference clears the bound and its uncertainty interval supports the direction fixed before collection; otherwise print a refusal."

**A = B — decision exercised:** The model-size comparison exercised the decision rule: it reported a direction only when the observed difference cleared the bound and its uncertainty interval — the range after known measurement uncertainties were included — supported the direction fixed before collection; otherwise it printed a refusal.

**C — contrast refused:** The model-size comparison exercised the decision rule by printing a refusal because the evidence reached neither claim gate; it reported no direction.

**Notes:** First-use audit: model-size comparison / decision rule / direction — glossed inline and introduced by the preceding Abstract material at draft line 11; resolution bound — built earlier on draft line 11; uncertainty interval — glossed inline as the range after known measurement uncertainties were included; refusal — glossed inline as reporting no direction.

### U02 — §6 Results — draft line 243 — NEEDS-RULING

**Frozen quote (verbatim):** "It will support the floor only if every block interval contains zero, the mean interval lies inside plus or minus the comparator, and the largest absolute block difference does not exceed it."

**A = B — characterization collected:** The null row supported the floor only because every block interval contained zero, the mean interval lay inside plus or minus the comparator, and the largest absolute block difference did not exceed it.

**C — contrast refused:** The separately admitted null row supported the floor only because every block interval contained zero, the mean interval lay inside plus or minus the comparator, and the largest absolute block difference did not exceed it.

**Notes:** First-use audit: null row / block interval / mean interval / comparator / largest absolute block difference — draft lines 95 and 243; floor containment test — draft lines 95 and 185–187. Outcome D is not added here; Item 10 supplies its no-characterization opening.

### U03 — §6 Demonstration results — draft line 285 — NEEDS-RULING

**Frozen quote (verbatim):** "The claim-side bound column will be filled only when its supplier is built after the prospective campaign; it is registered as unresolved until then."

**A = B — supplier-dependent column:** No claim-side bound is reported unless an issued artifact supplies it; the deterministic total that widens the decision interval is not a substitute.

**C — contrast refused:** No claim-side bound is reported under the same refusal; the deterministic total that widens the decision interval is not a substitute.

**Notes:** First-use audit: claim-side bound / supplier / registered omission — draft lines 196 and 272 distinguish the claim-side bound from the deterministic total, and the table column at draft line 285 names its role; the checklist's STOP_FILL rows supply the exact omission wording. “Under the same refusal” is four words.

### U04 — §6 Demonstration results — draft line 285 — NEEDS-RULING

**Frozen quote (verbatim):** "The floor gate will pass only when `|estimate| > F`; the direction gate will pass only when both interval endpoints are positive."

**A = B — gates evaluated:** The floor gate passed only when `|estimate| > F`; the direction gate passed only when both interval endpoints were positive.

**C — contrast refused:** Neither the floor gate nor the direction gate was evaluated under the same refusal.

**Notes:** First-use audit: floor gate / direction gate — draft lines 23 and 193–204; estimate / floor `F` / interval endpoints — draft lines 193–204 and 285. “Under the same refusal” is four words.

### U05 — §6 Demonstration results — draft line 285 — NEEDS-RULING

**Frozen quote (verbatim):** "The verdict will support the registered contrast only when evidence admission, Holm, floor, and direction checks all pass; otherwise it will print the exact refusal."

**A = B — verdict issued:** The verdict supported the registered contrast only when evidence admission, Holm, floor, and direction checks all passed; otherwise it printed the exact refusal.

**C — contrast refused:** The verdict printed the exact refusal because the required evidence did not reach either claim gate, and it supported no registered contrast.

**Notes:** First-use audit: registered contrast / evidence admission / Holm / floor and direction checks — draft lines 86, 193–204, 227–229, and 264; exact refusal — draft lines 202–204. This sentence states the verdict rule once without restating the dominance falsifier.

### U06 — §6 Demonstration fixed before collection — draft line 264 — NEEDS-RULING

**Frozen quote (verbatim):** "A missing or non-estimable member will remain in the frozen family of two and will not shrink the denominator."

**A = B — registered multiplicity rule:** A missing or non-estimable member remains in the frozen family of two and does not shrink the denominator.

**C — contrast refused:** A missing or non-estimable member remains in the frozen family of two and does not shrink the denominator under the same refusal.

**Notes:** First-use audit: missing or non-estimable member / frozen family of two / denominator — the Holm family and its two registered contrasts are built in the unchanged first sentence of draft line 264 and at draft line 198. “Under the same refusal” is four words.

### Census of `will ` on the hazard lines

| Draft line | `will ` sentence(s) found | Treatment |
|---:|---|---|
| 11 | construct the resolution bound; test boundary assignment; model-size comparison exercises the decision rule; collection does not test transfer | H05; H06; U01; “the prospective collection will not test the transfer” is uncovered and NEEDS-RULING because it is not in the director's enumerated U set |
| 21 | produce the two components | H07 |
| 30 | none | H03 has no `will ` occurrence |
| 31 | exercise the decision behavior; report the decisions | H08 covers the full sentence |
| 187 | none | H09 has no `will ` occurrence |
| 243 | report null first; give null quantities; support-floor criterion; collection not occurred | H10; H11; U02; H02 |
| 260 | compare models; use ten blocks; use fixed token-generation prompt; use fixed prompt-processing prompt | H12; H13; H14; H15 |
| 262 | publish cell bound; transport timing term; “No floor will transport…” | H16; H17; standing rule — no change proposed |
| 264 | form Holm family; form p-value; compare ordered p-values; missing-member denominator | “The two contrasts will form one Holm family…” is uncovered and NEEDS-RULING because it is not in the director's enumerated U set; H18; H19; U06 |
| 274 | none | H01 has no `will ` occurrence |
| 276 | gross cell; per-token cell; floor cell; bundle count | H20; H21; H22 |
| 285 | point; interval; floor; claim-side bound; sizing cell; floor/direction gates; verdict/refusal | H23; H24; H25; U03; H26; U04; U05 |
| 296 | none | H04 has no `will ` occurrence |
| 298 | none | H27 has no `will ` occurrence |
| 356 | none | H28 and H29 have no `will ` occurrence |

## Additional ready text

### Item 60 — §7 tamper-evidence sentence

**Ruling sentence (verbatim):** The repository is tamper-evident for the operator's own benefit — a way to catch one's own mistakes — not tamper-proof against anyone; it assumes a single trusted operator, so every gate defends against error and post-hoc choice, never against an adversary.

**Frozen paragraph replaced (verbatim):** "The repository provides internal consistency and tamper evidence, not third-party provenance. It assumes a single trusted operator and no same-user program attempting to alter evidence; a known interval between checking a floor-specification path and authorizing it could let such a program alter the authorization record, although a precommitted fingerprint prevents the swap from altering a published number. The 748 bundles made with the retired clock-anchor calculation remain auditable under that calculation but are permanently barred from claims: admission rejects their method label, and reprocessing claim energies under the replacement method after seeing the data would be retrospective analysis. These are limits on what the record proves, not exceptions to its gates."

**Full replacement paragraph:** The repository provides internal consistency and tamper evidence, not third-party provenance. The repository is tamper-evident for the operator's own benefit — a way to catch one's own mistakes — not tamper-proof against anyone; it assumes a single trusted operator, so every gate defends against error and post-hoc choice, never against an adversary. The 748 bundles made with the retired clock-anchor calculation remain auditable under that calculation but are permanently barred from claims: admission rejects their method label, and reprocessing claim energies under the replacement method after seeing the data would be retrospective analysis. These are limits on what the record proves, not exceptions to its gates.

**Notes:** Director decision: scope sentence retained; item 60 replaces only the defensive framing. First-use audit: internal consistency / tamper evidence / third-party provenance / trusted operator / admission — all are already built in the frozen paragraph at draft line 310, and the replacement sentence glosses the threat-model distinction inline. “These” remains plural because the paragraph names two limits: third-party/adversarial provenance and the retired bundles' permanent claim bar.

### Item 10 — §6 null row first (A / B / C / D)

Use the following as the opening of “### Results.” When the characterization campaign ran, the null block's number is the first number printed. Registry row `[D_C_null_max_abs_J]` (line 434) supplies the number and `[PLAIN_LANGUAGE_RESULT_null]` (line 444) supplies its outcome; neither token may be filled without the authenticated characterization report.

**A — dominance reproduced:** The largest authenticated absolute A/B/B/A difference in the identical-condition null block was `[D_C_null_max_abs_J]` J, and its registered outcome was `[PLAIN_LANGUAGE_RESULT_null]`; with the floor thus tested first, the admitted comparisons of timing-widened values against point-only repeatability values reproduced attribution dominance in both phases.

**B — dominance not reproduced:** The largest authenticated absolute A/B/B/A difference in the identical-condition null block was `[D_C_null_max_abs_J]` J, and its registered outcome was `[PLAIN_LANGUAGE_RESULT_null]`; with the floor thus tested first, at least one admitted phase had a timing-widened value that did not exceed its point-only repeatability value, so dominance was rejected for that phase and retained only for a phase whose four comparisons passed, while failure in both leaves a corrected-clock calibration followed by a prospective null.

**C — contrast refused:** The largest authenticated absolute A/B/B/A difference in the separately admitted identical-condition null block was `[D_C_null_max_abs_J]` J, and its registered outcome was `[PLAIN_LANGUAGE_RESULT_null]`; the 1.5B or 7B floor window was then refused before its evidence reached either claim gate, recording `[REFUSAL_REASON_1p5B_floor_window]` / `[REFUSAL_REASON_7B_floor_window]` as the artifact's outcome name and reason, so dominance remained unevaluated and no phase-dominance or model-ranking claim follows.

**D — characterization campaign not run:** The identical-condition null block, which tests the resolution bound itself by comparing a workload with itself, was not collected in this campaign, so no null number is reported and the published floors below stand without their own falsification test; that test is the first item of future work.

**Notes:** H10 is superseded by this opening, so the null number prints once; H11 refers to it without reprinting it. First-use audit: identical-condition null / A/B/B/A mechanism — draft lines 95 and 185–187; timing-widened / point-only repeatability / attribution dominance — draft lines 21 and 185; corrected-clock calibration / prospective null — draft lines 17 and 21; floor-window side path / claim gates — draft lines 193–204; artifact outcome-name family — draft line 88; resolution bound — draft lines 11 and 19. At fill time, replace the slash-separated refusal alternatives with only the token or tokens that actually refused, never both joined by “or.” NEEDS-RULING: ruling item 10 has no fallback; D is proposed under item 64's precedent that no placeholder prints without a supplier.

The §3 Holm family remains the null-mean and prefill-invariance containment pair; the §6 Holm family remains the decode and fixed-p256 contrasts. These are two distinct families of two, not one family of four.

## Fidelity ledger

| Block | Draft line | Quote length (characters) | Placeholder tokens / missing-row markers used | Registry line(s) |
|---|---:|---:|---|---|
| H01 | 274 | 271 | — | — |
| H02 | 243 | 72 | — | — |
| H03 | 30 | 191 | — | — |
| H04 | 296 | 24 | — | — |
| H05 | 11 | 226 | — | — |
| H06 | 11 | 176 | — | — |
| H07 | 21 | 98 | — | — |
| H08 | 31 | 228 | — | — |
| H09 | 187 | 144 | — | — |
| H10 | 243 | 211 | — (superseded by Item 10) | — |
| H11 | 243 | 194 | `[PLAIN_LANGUAGE_RESULT_null]` | 444 |
| H12 | 260 | 129 | — | — |
| H13 | 260 | 133 | — | — |
| H14 | 260 | 53 | — | — |
| H15 | 260 | 121 | — | — |
| H16 | 262 | 182 | — | — |
| H17 | 262 | 200 | — | — |
| H18 | 264 | 140 | — | — |
| H19 | 264 | 120 | — | — |
| H20 | 276 | 98 | STOP_FILL rows DS-09, DS-13, DS-17, DS-21 in Notes | 782, 786, 790, 794 |
| H21 | 276 | 325 | STOP_FILL rows DS-10, DS-14, DS-18, DS-22 in Notes | 783, 787, 791, 795 |
| H22 | 276 | 126 | — | — |
| H23 | 285 | 52 | `[E_decode_contrast_signed_J_per_request]`; `NO-TOKEN PG-01` in Notes | 362, 808 |
| H24 | 285 | 144 | `[E_decode_contrast_lower_J]`, `[E_decode_contrast_upper_J]`; `NO-TOKEN PG-02`, `NO-TOKEN PG-03` in Notes | 363, 364, 809, 810 |
| H25 | 285 | 59 | `[F_claim_decode_armwise_max_J]`; `NO-TOKEN DS-33` in Notes | 366, 806 |
| H26 | 285 | 88 | `NO-TOKEN DS-30`, `NO-TOKEN PG-06` in Notes; STOP_FILL rows DS-29, PG-05 | 803, 813, 802, 812 |
| H27 | 298 | 225 | — | — |
| H28 | 356 | 173 | — | — |
| H29 | 356 | 278 | — | — |
| U01 | 11 | 230 | — | — |
| U02 | 243 | 191 | — | — |
| U03 | 285 | 149 | STOP_FILL claim-side-bound rows in Notes | 802, 812 |
| U04 | 285 | 129 | — | — |
| U05 | 285 | 165 | — | — |
| U06 | 264 | 110 | — | — |
| Item 10 | 243 | n/a (ruling replacement) | `[D_C_null_max_abs_J]`, `[PLAIN_LANGUAGE_RESULT_null]`, `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 434, 444, 298, 299 |
| Item 60 | 310 | n/a (ruling replacement) | — | — |
