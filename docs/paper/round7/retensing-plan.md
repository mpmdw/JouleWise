# Round-7 retensing plan (prepared while draft-v1.md is frozen)

> **PARKED (cold ruling, 2026-08-31): usable ONLY through the campaign fill
> session's live adjudication.** The final pre-data adjudication returned 3
> blockers / 13 should-fixes (`docs/process_traces/2026-08-31-registry-v5/11-final-adjudication-opus.md`);
> the fill session cures that worklist FIRST (`12-PARK-DISPOSITION.md`), then
> applies these sheets under a fresh seat. No further pre-data rounds.


> **STATUS (2026-08-31, cold-ruled perimeter round executed): HELD — the six adjudication-2 blockers and eight should-fixes are installed; awaiting the one final fresh joint pedagogy adjudication before mechanical substitution.**
> The rewrite implements the magistrate's R-1 through R-6 rulings, D-164, D-165 including its completed R-5, D-166 as amended, and reviewer-panel desk items 6, 10, 12, 13, and 16. The `_v5` registry is the only token vocabulary. `[PREFILL_LENGTH]` and every token containing it remain parameterized until the authenticated G2-a selection record issues.
> Verified and preserved: every pre-existing frozen quote remains byte-exact on its named draft line. Item 60 now opens with the D-161 sentence, retains only the ruled internal-consistency clause after it, and drops the old first sentence. Outcome D is a prefix that combines with A, B, or C rather than a fourth exclusive result.

This file is the round-7 substitution sheet; it does not edit the frozen draft.
Round 7 selects one ready sentence at each hazard after authenticated artifacts and the replay check fix the outcome.
Outcome A means every registered independent-corner ratio is at least 2 and every required comparative shared-error replay ratio is also at least 2. Outcome B means admitted evidence leaves at least one of those ratios below 2. Outcome C means required evidence was excluded before the comparison could be evaluated. Outcome D means the separate identical-workload characterization was not collected; its sentence is prefixed to the selected A, B, or C result wherever the null row is discussed.

At fill time, print only the refusal-reason token or tokens for windows that actually refused. Never print both candidate tokens joined by “or”: print one issued reason for one refused window, or both issued reasons separately if both windows refused.

## Outcome definitions

**Outcome A — boundary-placement dominance reproduced.** For each absolute and comparative component of every Qwen3-1.7B and Qwen3-8B prompt-processing and token-generation cell, divide the complete unguarded bound made after allowing every registered interval edge to move by the complete unguarded bound made from the observed point values alone. Both quantities are taken before the small-sample multiplier \(g(n)\) and whole-window allowance. Every quotient must be at least 2. For each comparative component, repeat the calculation while forcing the calibration error shared by a four-run block to move together, again using unguarded floors; every such quotient must also be at least 2. Only then may the paper say boundary placement at least doubled the component bound.

**Outcome B — boundary-placement dominance not reproduced.** Required evidence was usable, but at least one independent-edge quotient was below 2, or at least one comparative shared-error quotient was below 2. The paper states which component failed and withdraws the dominance sentence for that component; if all components in the other phase pass, the result narrows to that phase, while failures in both phases leave the corrected calibration followed by a result that did not reproduce the registered doubling.

**Outcome C — comparison refused.** The Qwen3-1.7B or Qwen3-8B measurement window was excluded, with `[REFUSAL_REASON_1p7B_floor_window]` or `[REFUSAL_REASON_8B_floor_window]` printed only for the window that actually failed, or the demonstration lacked an authenticated token-generation or prompt-processing verdict (`[[NO-TOKEN: DS-32 — authenticated conservative decode verdict]]`; `[[NO-TOKEN: PG-08 — authenticated conservative prefill verdict]]`). No quotient or directional model comparison is reported from excluded evidence.

**Outcome D — prefix: identical-workload characterization not collected.** When `characterization.run` is false, prepend the ruled no-characterization sentence to the selected A, B, or C result. No null-row token is printed because no authenticated characterization report supplies one.

The decision is component-specific; no average of ratios is invented. Exact equality at 2 passes. For example, a complete unguarded interval-edge bound of 3.0 J divided by a complete unguarded point-only bound of 1.5 J gives 2.0 and passes; neither operand includes \(g(n)\) or the window allowance. A comparative shared-error replay ratio of 1.8 withdraws the dominance sentence even if the independent-edge ratio is 2.0. The older code predicate survives only as the cell's diagnostic label: its TERM B and TERM A values do not select A or B.

| Phase | Model/component | Independent-edge ratio used by the headline | Shared-error ratio disclosed | Diagnostic-label terms only |
|---|---|---|---|---|
| prompt processing | Qwen3-1.7B absolute | `[R_1p7B_prefill_p[PREFILL_LENGTH]_abs]` | `[R_cm_1p7B_prefill_p[PREFILL_LENGTH]_abs]` = `not_applicable` because subtracting the cell mean cancels one uniform shared shift | `[TERM_A_1p7B_prefill_p[PREFILL_LENGTH]_abs_J]`; `[TERM_B_1p7B_prefill_p[PREFILL_LENGTH]_abs_J]` |
| prompt processing | Qwen3-1.7B comparative | `[R_1p7B_prefill_p[PREFILL_LENGTH]_cmp]` | `[R_cm_1p7B_prefill_p[PREFILL_LENGTH]_cmp]` | `[TERM_A_1p7B_prefill_p[PREFILL_LENGTH]_cmp_J]`; `[TERM_B_1p7B_prefill_p[PREFILL_LENGTH]_cmp_J]` |
| prompt processing | Qwen3-8B absolute | `[R_8B_prefill_p[PREFILL_LENGTH]_abs]` | `[R_cm_8B_prefill_p[PREFILL_LENGTH]_abs]` = `not_applicable` for the same cancellation | `[TERM_A_8B_prefill_p[PREFILL_LENGTH]_abs_J]`; `[TERM_B_8B_prefill_p[PREFILL_LENGTH]_abs_J]` |
| prompt processing | Qwen3-8B comparative | `[R_8B_prefill_p[PREFILL_LENGTH]_cmp]` | `[R_cm_8B_prefill_p[PREFILL_LENGTH]_cmp]` | `[TERM_A_8B_prefill_p[PREFILL_LENGTH]_cmp_J]`; `[TERM_B_8B_prefill_p[PREFILL_LENGTH]_cmp_J]` |
| token generation | Qwen3-1.7B absolute | `[R_1p7B_decode_abs]` | `[R_cm_1p7B_decode_abs]` = `not_applicable` for the same cancellation | `[TERM_A_1p7B_decode_abs_J]`; `[TERM_B_1p7B_decode_abs_J]` |
| token generation | Qwen3-1.7B comparative | `[R_1p7B_decode_cmp]` | `[R_cm_1p7B_decode_cmp]` | `[TERM_A_1p7B_decode_cmp_J]`; `[TERM_B_1p7B_decode_cmp_J]` |
| token generation | Qwen3-8B absolute | `[R_8B_decode_abs]` | `[R_cm_8B_decode_abs]` = `not_applicable` for the same cancellation | `[TERM_A_8B_decode_abs_J]`; `[TERM_B_8B_decode_abs_J]` |
| token generation | Qwen3-8B comparative | `[R_8B_decode_cmp]` | `[R_cm_8B_decode_cmp]` | `[TERM_A_8B_decode_cmp_J]`; `[TERM_B_8B_decode_cmp_J]` |

Every token containing `[PREFILL_LENGTH]` remains unresolved until the G2-a record selects one rung. The absolute shared-error entries are not missing results: `not_applicable` is the registered result because a uniform shared timing shift disappears when each absolute observation is expressed as a deviation from its cell mean. A comparative shared-error value is mandatory, and a value below 2 selects B even when every independent-edge ratio passes.

## Substitution table

### H01 — §6 Demonstration results — draft line 274 — VARIANT-SELECTED

**Frozen quote (verbatim):** "**[RESULT PENDING ISSUED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into these tables, and none appears anywhere in this paper except the explicitly labeled instrument diagnostics of Sections 3, 6, and 7.]**"

**Fails:** A, B, and partial C: the current fill machinery cannot produce a complete paper-facing lead-in for every admitted or refused outcome.

**A — dominance reproduced:** Both model-specific measurement windows supplied usable records; the tables below report each issued cell, each registered comparison decision, and every independent-edge and shared-error ratio used to support the statement that boundary placement at least doubled the component bound. Every ratio uses the complete unguarded corner and point floors before \(g(n)\) and the whole-window allowance.

**B — dominance not reproduced:** Both model-specific measurement windows supplied usable records; the tables below report each issued cell and comparison decision, but at least one independent-edge or required shared-error ratio—calculated from the complete unguarded corner and point floors before \(g(n)\) and the whole-window allowance—was below 2, so the paper withdraws the doubling statement for every component that failed.

**C — contrast refused:** At least one model-specific measurement window failed a required recorded check before its values could enter the comparison; the Results opening states the issued reason, the tables omit quantities without a supplier, and the paper reports neither a directional model comparison nor a boundary-placement quotient from the excluded records.

**Notes:** The sibling checklist owns branch selection and fill mechanics. The ratio columns come only from the D-165 registry rows above. The sibling checklist's STOP_FILL rows govern every table fill.

### H02 — §6 Results — draft line 243 — FIXED

**Frozen quote (verbatim):** "Collection has not occurred, so no null value or outcome is stated here."

**Fails:** A/B/C: every round-7 outcome presupposes that collection ran and issued a verdict.

**A — dominance reproduced:** Superseded by Item 10; insert no sentence from H02 at this site.

**B — dominance not reproduced:** Superseded by Item 10; insert no sentence from H02 at this site.

**C — contrast refused:** Superseded by Item 10; insert no sentence from H02 at this site.

**D — prefix: characterization not run:** Superseded by Item 10; insert no sentence from H02 at this site.

**Notes:** Item 10 supplies the complete insertable Results opening, including the D prefix. H02 is routing metadata only, exactly like H10, and contributes no paper sentence.

### H03 — §1 Introduction — draft line 30 — FIXED

**Frozen quote (verbatim):** "The second contribution is a cell-specific resolution bound and the prospective attribution-dominance finding; §3 characterizes the instrument, §4 composes the bound, and §6 reports the test."

**Fails:** B/C structurally: “the … finding” presupposes a positive, admitted finding rather than a null or refusal.

**A — dominance reproduced:** The second contribution is the cell-specific resolution bound and the finding that allowing registered boundary movement at least doubled every component bound; §3 characterizes the instrument, §4 composes the bound, and §6 reports the ratios.

**B — dominance not reproduced:** The second contribution is the cell-specific resolution bound and the result that at least one registered ratio was below 2; §3 characterizes the instrument, §4 composes the bound, and §6 identifies each component that failed.

**C — contrast refused:** The second contribution is the cell-specific resolution-bound construction and the recorded exclusion of evidence that failed a required check; §3 characterizes the instrument, §4 composes bounds from usable records, and §6 explains why the excluded records support no directional model result.

**Notes:** Cell and its resolution bound are physically built at draft lines 15–19. Each branch states the ratio or the physical exclusion without relying on later vocabulary.

### H04 — §7 Discussion and limitations — draft line 296 — FIXED heading

**Frozen quote (verbatim):** "What the finding changes"

**Fails:** B/C structurally: it assumes that an attribution-dominance finding was made.

**A — dominance reproduced:** What a twofold boundary contribution changes

**B — dominance not reproduced:** What a below-two ratio changes

**C — contrast refused:** What excluded comparison evidence establishes

**Notes:** Heading forms intentionally remain headings. First-use audit: dominance / null outcome — draft line 21; refused contrast — draft lines 23 and 202–204. Draft lines 292–294 establish the discussion context, and the following paragraph uses the same selected outcome.

### H05 — §Abstract — draft line 11 — FIXED

**Frozen quote (verbatim):** "For each group of like-for-like runs, called a cell, the analysis will construct the cell's resolution bound — the artifact calls it the detection floor — “the largest false difference this measurement system can manufacture.”"

**Fails:** C: refused evidence need not yield a claim-bearing cell bound.

**A = B — admitted evidence:** For each group of like-for-like runs, called a cell, the analysis constructed the cell's resolution bound — the artifact calls it the detection floor — “the largest false difference this measurement system can manufacture.”

**C — contrast refused:** For each group of like-for-like runs, called a cell, the analysis constructs the cell's resolution bound — the artifact calls it the detection floor — “the largest false difference this measurement system can manufacture”; no such bound was constructed for a cell whose records failed a required check.

**Notes:** Cell is glossed inline as a group of like-for-like runs, and the bound receives its physical definition before either paper name. This Abstract sentence is the sole “largest false difference” glossary after the item-13 de-duplication blocks below.

### H06 — §Abstract — draft line 11 — FIXED

**Frozen quote (verbatim):** "The results will test whether boundary assignment contributes more than run-to-run variation to the bound for prompt processing and token generation on the named configuration."

**Fails:** C: admission refusal leaves the dominance predicate unevaluated.

**A — dominance reproduced:** In both prompt processing and token generation, the bound after allowing every registered boundary movement—that is, every movement allowed by the rule fixed before collection—was at least twice the bound from repeated point measurements alone, and the same was true when timing error shared within each four-run comparison moved together.

**B — dominance not reproduced:** In at least one phase, a bound after allowing registered boundary movement—movement allowed by the rule fixed before collection—was less than twice its point-measurement bound, or the quotient fell below 2 when timing error shared within a four-run comparison moved together; the paper identifies each failed component instead of calling it dominated by boundary placement.

**C — contrast refused:** A required record was missing or failed a check fixed before collection, so the comparison was not calculated and the paper reports no direction between the models and no conclusion about whether boundary placement at least doubled the bound.

**Notes:** This is the Abstract's sole full ratio-result and exclusion carrier. Each technical action is built from physical movement, repeated point measurements, and shared four-run timing before the quotient is used.

### H07 — §1 Introduction — draft line 21 — FIXED

**Frozen quote (verbatim):** "The two components will be produced independently for every phase cell that could support a claim."

**Fails:** C: refused evidence may produce no admissible component pair.

**A — dominance reproduced:** The two components—the spread among repeated runs within one model arm and the between-model difference formed by subtracting the two A energies from the two B energies and dividing by two—were produced independently for every phase cell used in a claim; allowing calibrated boundary movement at least doubled each component bound, including each comparison recalculated with its shared timing error moving together.

**B — dominance not reproduced:** The same two components were produced independently for every usable phase cell, but at least one boundary-movement quotient was below 2 under the rule stated below.

**C — contrast refused:** A component pair was not calculated where required records failed a fixed check, so those records support neither a boundary-movement quotient nor a directional comparison between models.

**Notes:** Repeated-run spread, boundary reassignment, and phase cell are physically built at draft lines 15–19. The A branch states both independent and shared-error forcing conditions.

### H08 — §1 Introduction — draft line 31 — FIXED

**Frozen quote (verbatim):** "The third contribution is the decision behavior the prospective demonstration will exercise — two gates, printed refusals, and the resolvability rule; §5 defines when collection stops, and §6 will report the resulting decisions."

**Fails:** C: evidence refusal bypasses both claim gates, so the stated two-gate exercise does not occur.

**A — dominance reproduced:** The third contribution is the demonstration's recorded decision behavior — one check asks whether the measured difference exceeds the cell bound, a second asks whether the uncertainty range points in the registered direction, and failed checks print reasons; §5 defines collection stops, and §6 reports the decisions.

**B — dominance not reproduced:** The third contribution is the same recorded decision behavior, while the separate boundary-movement test reports every quotient below 2; §5 defines collection stops, and §6 reports both kinds of decision.

**C — contrast refused:** A model's required measurement records failed a fixed check before reaching either comparison check; §5 defines that stop, §6 prints its reason, and the excluded records support no direction between models and no boundary-movement quotient.

**Notes:** The two checks are physically glossed before their later formal names. This is §1's sole complete exclusion carrier.

### H09 — §4 The resolution bound and how it is composed — draft line 187 — FIXED

**Frozen quote (verbatim):** "Passing the identical-condition null block at the corner-widened resolution bound tests the bound itself, and §6 reports that null number first."

**Fails:** C: no admitted null number is guaranteed.

**A = B — characterization collected:** The identical-condition null block tests the bound itself: with the same workload in A and B, every nonzero block difference is manufactured by the measurement system, so the block passes only when its largest absolute difference stays inside the corner-widened resolution bound; the Results section reports that number first.

**C — contrast refused:** The identical-condition null block uses records governed separately from the model comparison: with the same workload in A and B, every nonzero block difference is manufactured by the measurement system, so it passes only when its largest absolute difference stays inside the corner-widened resolution bound; the Results section reports that number before the comparison's exclusion reason.

**D — prefix: characterization not run:** The identical-condition null block would test the bound by comparing a workload with itself, but it was not collected; the Results section therefore prints no null number before the selected A, B, or C comparison result.

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

**C — contrast refused:** The null row came from records governed independently of the model comparison and reports the largest absolute block difference already printed above, its mean block difference and composed interval, its same-cell comparator, and the registered outcome `[PLAIN_LANGUAGE_RESULT_null]`; the later exclusion applies only to the model-comparison records.

**D — characterization campaign not run:** No issued null row supplies a largest absolute block difference, mean block difference, composed interval, same-cell comparator, or registered outcome because the characterization campaign was not run.

**Notes:** The null number is not reprinted here; Item 10 prints it once. Mean block difference, composed interval, same-cell comparator, and largest absolute block difference are built at draft lines 95 and 243. Registry line 454 supplies `[PLAIN_LANGUAGE_RESULT_null]`; the null block uses characterization records governed independently of the model-comparison records.

### H12 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "The prospective demonstration will compare 4-bit Qwen2.5 7B with 1.5B on the named M3 Max, MLX, and *powermetrics* configuration."

**Fails:** A/B/C temporally: at round 7 the campaign is no longer prospective; under C the comparison may remain unevaluated.

**A = B — admitted comparison:** The demonstration was registered before collection to compare 4-bit Qwen3-8B with Qwen3-1.7B on the named M3 Max, MLX, and *powermetrics* configuration, and its usable records were analyzed as registered.

**C — contrast refused:** The demonstration was registered before collection to compare 4-bit Qwen3-8B with Qwen3-1.7B on the named M3 Max, MLX, and *powermetrics* configuration, but a required-record failure prevented the directional comparison from being evaluated.

**Notes:** Registration voice preserves the subsection's fixed-before-collection force. The model pair and named machine/software/counter configuration are fixed inline.

### H13 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "Each contrast will use ten independent A/B/B/A blocks, where A is 1.5B, B is 7B, and one block difference is `(B1 + B2 - A1 - A2)/2`."

**Fails:** C: an admission refusal can prevent ten admitted blocks.

**A = B — admitted comparison:** The demonstration was registered to use ten independent A/B/B/A blocks per comparison, with A as Qwen3-1.7B, B as Qwen3-8B, and one block difference equal to `(B1 + B2 - A1 - A2)/2`; the usable comparisons ran with that order and count.

**C — contrast refused:** The same ten-block order and formula were registered, but a required-record failure left no usable ten-block comparison from which to report a direction.

**Notes:** The A/B/B/A order and block-difference formula are built at draft lines 227–229; the model-letter mapping is fixed inline.

### H14 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "Token generation will use the fixed 128-token prompt."

**Fails:** some C cases: refusal can occur before any admitted token-generation run.

**A = B — admitted comparison:** As fixed before collection, each token-generation member rendered one of eight real prompts through the Qwen3 chat template—the fixed formatting rule that converts a prompt into the model's input sequence—with thinking disabled, meaning that the model's optional reasoning-output mode was switched off. It then generated exactly 512 output tokens by always choosing the highest-scored next token.

**C — contrast refused:** The token-generation workload still used one of the same eight real prompts, the same fixed input-formatting rule, the model's optional reasoning-output mode switched off, and a forced 512-token output, but a required-record failure prevented the model comparison from being evaluated.

**Notes:** The sentence makes the execution reproducible: prompt set, rendering method, thinking policy, selection rule, and output count are all fixed by V5-WL-001 through V5-WL-004.

### H15 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "Prompt processing will use the fixed synthetic 256-token prompt with identical token identifiers across model tokenizers."

**Fails:** some C cases: refusal can occur before that arm runs.

**A = B — admitted comparison:** Prompt processing used `[PREFILL_LENGTH]` prompt tokens. Before collection, the G2-a rule tested 512, 1024, 2048, and 4096 tokens in that order with at least five Qwen3-1.7B probe runs per length; a length passed only when every probe had at least five power records overlapping prompt processing. Five was a two-record safety margin above the three overlapping records needed to calculate a phase. The shortest passing length became `[PREFILL_LENGTH]`; if none passed, collection used 4096, and that fallback alone was not a comparison refusal. The authenticated selection record then fixed the prompt text and token identifiers.

**C — contrast refused:** The same rule selected `[PREFILL_LENGTH]`, using 4096 when no shorter length passed; using that fallback did not itself select refusal. The comparison was refused only for its issued failure: a final overlap count below 3 printed the program's `not_resolvable_sample_count` reason, while a count of 3 or 4 printed the recorded reason “below the pre-registered count floor of 5,” meaning that the phase was calculable but missed the stricter five-record design minimum, and disclosed the calculable result beside it. Any other required-record failure printed its own issued reason.

**Notes:** `[PREFILL_LENGTH]` stays parameterized until G2-a. Example: five probe runs with counts 6, 5, 7, 5, and 8 pass a length, while 6, 5, 4, 7, and 8 do not because every one of the five runs must reach five records. Large-model probes are recorded but do not select the length. The final count split preserves the two ruled refusal meanings and keeps the two-comparison Holm family unchanged.

### H16 — §6 Demonstration fixed before collection — draft line 262 — FIXED

**Frozen quote (verbatim):** "Each model and phase will have its own cell's resolution bound — the artifact calls it the detection floor — **the largest false difference this measurement system can manufacture**."

**Fails:** C: refused cells publish no claim-bearing floor.

**A = B — admitted cells:** The registration assigned each model-and-phase cell its own resolution bound, called the detection floor, and every cell supported by usable records later published its own bound.

**C — contrast refused:** The registration assigned each model-and-phase cell its own resolution bound, but a cell whose records failed a required check published neither a bound nor a label.

**Notes:** The Abstract owns the one physical “largest false difference” glossary. This site retains the formal names without repeating that definition.

### H17 — §6 Demonstration fixed before collection — draft line 262 — FIXED

**Frozen quote (verbatim):** "Its timing term will be measured with commanded GPU pulses and transported to sustained mixed inference load; that transport is an explicit assumption, and the prospective collection does not test it."

**Fails:** some C cases: admission can refuse before an applicable timing term is established.

**A = B — de-duplicated limitation:** Remove this sentence; the Abstract, Discussion, and Conclusion each retain one audience-appropriate statement of the pulse-to-inference assumption.

**C — de-duplicated limitation:** Remove this sentence; excluding comparison records does not change the pulse-to-inference assumption retained in the Abstract, Discussion, and Conclusion.

**Notes:** Reviewer item 13 limits the transfer statement to those three locations.

### H18 — §6 Demonstration fixed before collection — draft line 264 — FIXED

**Frozen quote (verbatim):** "Each raw two-sided Student-*t* p-value will use the contrast estimate divided by its total standard error and its issued degrees of freedom."

**Fails:** C: an unevaluated contrast has no raw p-value.

**A = B — admitted contrast:** The registered analysis formed each raw two-sided Student-*t* p-value from the contrast estimate divided by its total standard error and issued degrees of freedom.

**C — contrast refused:** When required comparison records were excluded, no raw p-value was formed and neither a directional model result nor a boundary-movement quotient was reported from them.

**Notes:** Two-sided Student-*t* p-value, contrast estimate, total standard error, and issued degrees of freedom are built at draft line 198.

### H19 — §6 Demonstration fixed before collection — draft line 264 — FIXED

**Frozen quote (verbatim):** "After ordering the two p-values, the smaller will be compared with 0.025, then, only if it passes, the larger with 0.05."

**Fails:** C: refusal can leave no two p-values to order.

**A = B — admitted contrasts:** As registered, the two raw p-values were ordered; the smaller was compared with 0.025 and, only after it passed, the larger was compared with 0.05.

**C — contrast refused:** When required comparison records were excluded, there were no two p-values to order and neither a directional model result nor a boundary-movement quotient was reported from them.

**Notes:** Raw p-values and ordered Holm thresholds are built at draft lines 198 and 264; U08 supplies the retensed family sentence.

### H20 — §6 Demonstration results — draft line 276 — FIXED

**Frozen quote (verbatim):** "A gross cell will contain the issued phase-energy estimate and composed lower and upper endpoints."

**Fails:** C and currently A/B: refusal issues no claim-bearing cell, and the admitted branches still have no issued reported-mean fields or composed endpoints.

**A = B — issued artifacts:** The Gross J/request column was defined as the mean phase energy per selected request with lower and upper endpoints after the known uncertainties were included. No value was reported because the issued artifacts defined neither that mean-energy field nor its endpoints, and no floor component was substituted for either quantity.

**C — contrast refused:** The Gross J/request column was defined as the mean phase energy per selected request with lower and upper endpoints after the known uncertainties were included. No value was reported from excluded records because the issued artifacts defined neither that mean-energy field nor its endpoints, and no floor component was substituted for either quantity.

**Notes:** First-use audit: gross phase-energy value / reported mean — table context at draft lines 276–283 and glossed inline by the missing field; composed endpoints — draft lines 193–200; floor component — draft lines 178–189. Registry rows DS-09, DS-13, DS-17, and DS-21 move to bookkeeping here. The table columns remain; their fill is governed by the checklist's exact STOP_FILL sentences for those four rows. “Under the same refusal” is four words.

### H21 — §6 Demonstration results — draft line 276 — FIXED

**Frozen quote (verbatim):** "A companion per-token cell will contain the tokenizer-scoped value whose authenticated runtime-observed denominator is fixed by the issuing schema; [[NEEDS-VALUE: D-123 producing schema for each per-token numerator, denominator, and point-or-interval rendering; the results-fill registry records these suppliers as unknown]]."

**Fails:** A/B/C currently: the promised producing schema and authenticated denominator fields do not exist.

**A = B — issued artifacts:** Each per-token column was defined as phase energy divided by the prompt- or output-token count observed while that run executed. No value was reported because the issued artifacts defined neither the runtime-observed energy numerator nor the observed token-count denominator, and neither a prompt- or output-token count requested of the runtime nor a count reported by the generation library was substituted for the count observed during execution.

**C — contrast refused:** Each per-token column was defined as phase energy divided by the prompt- or output-token count observed while that run executed. No value was reported from excluded records because the issued artifacts defined neither the runtime-observed energy numerator nor the observed token-count denominator, and neither a prompt- or output-token count requested of the runtime nor a count reported by the generation library was substituted for the count observed during execution.

**Notes:** First-use audit: per-token value / runtime-observed numerator and denominator — table context and inline gloss at draft line 276; tokenizer scope — draft lines 260 and 276. Registry rows DS-10, DS-14, DS-18, and DS-22 move to bookkeeping here. The table columns remain; their fill is governed by the checklist's exact STOP_FILL sentences for those four rows. “Under the same refusal” is four words.

### H22 — §6 Demonstration results — draft line 276 — FIXED

**Frozen quote (verbatim):** "A floor cell will contain its magnitude and permitted label; n will count admitted independent run bundles, not power records."

**Fails:** C: a refused cell may publish neither magnitude nor label.

**A — dominance reproduced:** Each published floor cell reported its magnitude, independent-edge ratio, and code-generated diagnostic label, and n counted independent run bundles that passed every entry check rather than power records. Absolute rows printed the shared-error ratio as `not_applicable` because, under the registered replay's idealization that one shared timing error moves every run's energy by the same amount, subtracting the cell mean cancels that energy displacement exactly; comparative rows reported the replayed shared-error ratio.

**B — dominance not reproduced:** Each published floor cell reported the same magnitude, ratio, diagnostic-label, and independent-bundle-count columns. Absolute rows printed the shared-error ratio as `not_applicable` because, under the registered replay's idealization that one shared timing error moves every run's energy by the same amount, subtracting the cell mean cancels that energy displacement exactly; comparative rows reported the replayed shared-error ratio. The paper identified every independent-edge ratio below 2 and every comparative shared-error ratio below 2 and withdrew the boundary-doubling sentence for those components; the code-generated label remained diagnostic rather than the headline test.

**C — contrast refused:** A cell whose records failed a required check published no magnitude, ratio, label, or independent-bundle count, and those records supported neither a boundary-doubling sentence nor a directional model result.

**Notes:** Magnitude precedes ratios and diagnostic label. The absolute `not_applicable` value is a registered mathematical result, not missing data.

### H23 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The point will be the mean of ten block differences."

**Fails:** C and prompt A/B currently: the contrast may be unevaluated, and the prompt token family is missing.

**A = B — admitted contrast:** The point-estimate column was defined as the mean of ten block differences. The token-generation mean was `[E_decode_contrast_signed_J_per_request]` J per request; no issued artifact supplied a prompt-processing point estimate.

**C — contrast refused:** The point-estimate column would have contained the mean of ten block differences, but no point estimate was reported from records that failed a required check, and those records supported neither a directional model result nor a boundary-movement quotient.

**Notes:** Point estimate and mean of ten block differences are built at draft lines 227–229 and 285; token generation and prompt processing are built at draft line 15. Registry line 372 supplies `[E_decode_contrast_signed_J_per_request]`. `[[NO-TOKEN: PG-01 — authenticated prompt contrast estimate]]` records the missing prompt token family in Notes only; registry line 824 is the stopped row.

### H24 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The interval cell will contain the fully composed lower and upper endpoints; for the registered positive direction, the lower endpoint controls."

**Fails:** C and prompt A/B currently: no admitted interval is guaranteed, and prompt endpoints lack tokens.

**A = B — admitted contrast:** The token-generation decision interval was [`[E_decode_contrast_lower_J]`, `[E_decode_contrast_upper_J]`] J; no issued artifact supplied a prompt-processing interval, and, because the registered direction was positive, the lower endpoint was the one that decided the direction gate.

**C — contrast refused:** No composed interval was reported from records that failed a required check, so those records supported neither a direction nor a boundary-movement quotient.

**Notes:** Decision interval, complete endpoints, and registered positive direction are built at draft lines 193–204 and 285. The interval is widened by the deterministic total built at draft line 196; it is not equated to the separately registered claim-side bound. Registry row DS-26 supplies `[E_decode_contrast_lower_J]` and `[E_decode_contrast_upper_J]`. `[[NO-TOKEN: PG-02 — authenticated prompt lower and upper endpoints]]` stays in Notes only; PG-03 is retired because PG-02 owns both slots at the one interval site.

### H25 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The floor will be the larger arm-specific exact-cell floor."

**Fails:** C and prompt A/B currently: refusal supplies no claim floor; the prompt claim-floor token is missing.

**A = B — admitted contrast:** The token-generation claim floor was `[F_claim_decode_armwise_max_J]` J, the larger arm-specific exact-cell floor; no issued artifact supplied a prompt-processing claim floor.

**C — contrast refused:** No claim floor was reported from records that failed a required check, so those records supported neither a direction nor a boundary-movement quotient.

**Notes:** Claim floor and larger arm-specific exact-cell floor are built at draft lines 193–204 and 285. Registry line 376 supplies `[F_claim_decode_armwise_max_J]`. `[[NO-TOKEN: DS-33 — authenticated prompt armwise claim floor]]` stays in Notes only; registry line 822 is the stopped row.

### H26 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The sizing cell will contain `C = F + B` and signed planning clearance `|estimate| - C`."

**Fails:** A/B/C currently: decode `B_decode_claim_J` has no supplier, the prompt family is absent, and C supplies no admissible estimate/floor.

**A = B — admitted contrast:** The sizing column was defined as `C = F + B`, where F is the applicable cell floor and B is the separately registered claim-side bound; its signed planning clearance was the measured magnitude minus C. The sum was not formed because no issued artifact supplied B, and no floor-gate outcome was reported because no authenticated artifact issued the result of checking whether the measured magnitude exceeded F.

**C — contrast refused:** For records that failed a required check, the sizing sum `C = F + B` was not formed and neither a directional model result nor a boundary-movement quotient was reported.

**Notes:** The sizing sum, signed planning clearance, and floor gate are built at draft lines 272 and 285; draft lines 196 and 285 distinguish the claim-side bound from the deterministic total. Registry lines 818 and 827 govern the absent claim-side bounds. `[[NO-TOKEN: DS-30 — authenticated decode floor-gate outcome]]` and `[[NO-TOKEN: PG-06 — authenticated prompt floor-gate outcome]]` stay in Notes only; registry lines 819 and 828 are the stopped rows.

### H27 — §7 What the finding changes — draft line 298 — FIXED

**Frozen quote (verbatim):** "Experimental practice must therefore change upstream: characterize edge placement for the named workload boundary, form a separate bound for each configuration cell, and size a comparison against that bound before collection."

**Fails:** B/C structurally: under the positive heading, “therefore” treats reproduced dominance as established.

**A — dominance reproduced:** Because every independent-edge and required shared-error ratio was at least 2, practice changes upstream: characterize the named workload boundary, form a bound for each configuration cell, and size the comparison before collection.

**B — dominance not reproduced:** At least one registered ratio was below 2, so the practice change is narrower: characterize edge placement for the named workload boundary and form a separate bound per configuration cell before sizing any comparison, while reporting which components did and did not reach the registered doubling.

**C — contrast refused:** A model-specific measurement window failed a required recorded check before its values could enter the comparison, so the protocol demonstrates that incomplete evidence is stopped with a reason but supports neither a directional model result nor a boundary-movement quotient from those records.

**Notes:** This is Section 7's sole full ratio-result and exclusion carrier. Under A, all independent and required shared-error ratios passed by definition.

### H28 — §10 Conclusion — draft line 356 — FIXED

**Frozen quote (verbatim):** "For each `_v4` prefill and decode cell, the test compares the point-only repeatability bound with the same cell after calibrated phase-edge positions widen its energy range."

**Fails:** C: refused evidence does not license that comparison.

**A — dominance reproduced:** For every usable `_v5` Qwen3-1.7B and Qwen3-8B prompt-processing and token-generation component, the complete unguarded interval-edge bound was divided by the complete unguarded point-only bound before \(g(n)\) and the whole-window allowance, and the quotient was at least 2; every comparative quotient remained at least 2 when timing error shared within a four-run block moved together, using the same unguarded inputs.

**B — dominance not reproduced:** For every usable `_v5` component the complete unguarded corner floor was divided by the complete unguarded point floor before \(g(n)\) and the whole-window allowance, but at least one independent-edge or required shared-error quotient was below 2, so the paper identifies each failed component instead of claiming boundary placement doubled its bound.

**C — contrast refused:** A Qwen3-1.7B or Qwen3-8B measurement window failed a required recorded check before its values could enter the comparison, so those records support neither a quotient comparing interval-edge and point-only bounds nor a directional result between models.

**Notes:** This is Section 10's sole full ratio-result and exclusion carrier. Paper prose describes the physical quotient rather than TERM labels.

### H29 — §10 Conclusion — draft line 356 — FIXED

**Frozen quote (verbatim):** "The contribution makes that outcome decidable: corrected in-window timing calibration (Section 2), independent construction and comparison of the cell-specific terms (Sections 3–4), and two claim gates that preserve refusals and the short-prefill negative result (Sections 4–6)."

**Fails:** C: refusal makes dominance undecided, not decided negative.

**A — dominance reproduced:** The contribution made the outcome decidable and decided it: corrected in-window timing calibration (Section 2) and independent per-component construction (Sections 3–4) produced ratios of at least 2 under both required timing-error treatments, while the two directional-comparison checks (Sections 4–6) preserved exclusions and the short-prompt negative result.

**B — dominance not reproduced:** The contribution made the outcome decidable and decided it: the same construction produced at least one ratio below 2, while the two directional-comparison checks preserved exclusions and the short-prompt negative result.

**C — contrast refused:** The contribution fixed the calculation in advance but did not invent a value from excluded records: corrected in-window timing calibration (Section 2), independent per-component construction (Sections 3–4), and two directional-comparison checks (Sections 4–6) preserve the reason for exclusion and the short-prompt negative result without reporting a quotient or model direction from those records.

**Notes:** Every contribution sentence retains the section pointers required by item 31 and describes each later formal check in plain words.

## Approved future-tense and census sentences

R-5 approved U01–U06 and the two additional census sentences as round-7 scope. They do not renumber or enlarge the ruled set of 29 `H` hazards. Draft line 262's sentence “No floor will transport across model, phase, or prompt length.” remains a standing rule and is unchanged.

### U01 — §Abstract — draft line 11 — APPROVED-R7

**Frozen quote (verbatim):** "A model-size comparison will exercise the decision rule: report a direction only when the observed difference clears the bound and its uncertainty interval supports the direction fixed before collection; otherwise print a refusal."

**A = B — decision exercised:** The model-size comparison exercised the decision rule: it reported a direction only when the observed difference cleared the bound and its uncertainty interval — the range after known measurement uncertainties were included — supported the direction fixed before collection; otherwise it printed a refusal.

**C — contrast refused:** The model-size comparison exercised the decision rule by printing the reason that required records failed before either comparison check; it reported no direction.

**Notes:** First-use audit: model-size comparison / decision rule / direction — glossed inline and introduced by the preceding Abstract material at draft line 11; resolution bound — built earlier on draft line 11; uncertainty interval — glossed inline as the range after known measurement uncertainties were included; refusal — glossed inline as reporting no direction.

### U02 — §6 Results — draft line 243 — APPROVED-R7

**Frozen quote (verbatim):** "It will support the floor only if every block interval contains zero, the mean interval lies inside plus or minus the comparator, and the largest absolute block difference does not exceed it."

**A = B — characterization collected:** The null row supported the floor only because every block interval contained zero, the mean interval lay inside plus or minus the comparator, and the largest absolute block difference did not exceed it.

**C — contrast refused:** The null row used records governed independently of the model comparison and supported the floor only because every block interval contained zero, the mean interval lay inside plus or minus the comparator, and the largest absolute block difference did not exceed it.

**D — prefix: characterization not run:** No null row exists because the identical-workload blocks were not collected; prepend this sentence to the selected A, B, or C comparison result and omit the A/B/C null-row sentence above.

**Notes:** Null row, intervals, comparator, and largest absolute block difference are built at draft lines 95 and 243. D composes with the contrast outcome and suppresses only the null-row sentence.

### U03 — §6 Demonstration results — draft line 285 — APPROVED-R7

**Frozen quote (verbatim):** "The claim-side bound column will be filled only when its supplier is built after the prospective campaign; it is registered as unresolved until then."

**A = B — supplier-dependent column:** No claim-side bound is reported unless an issued artifact supplies it; the deterministic total that widens the decision interval is not a substitute.

**C — contrast refused:** No claim-side bound is reported from records that failed a required check; the deterministic total that widens the decision interval is not a substitute.

**Notes:** First-use audit: claim-side bound / supplier / registered omission — draft lines 196 and 272 distinguish the claim-side bound from the deterministic total, and the table column at draft line 285 names its role; the checklist's STOP_FILL rows supply the exact omission wording. “Under the same refusal” is four words.

### U04 — §6 Demonstration results — draft line 285 — APPROVED-R7

**Frozen quote (verbatim):** "The floor gate will pass only when `|estimate| > F`; the direction gate will pass only when both interval endpoints are positive."

**A = B — gates evaluated:** The floor gate passed only when `|estimate| > F`; the direction gate passed only when both interval endpoints were positive.

**C — contrast refused:** Neither the floor gate nor the direction gate was evaluated when required records failed before reaching them.

**Notes:** First-use audit: floor gate / direction gate — draft lines 23 and 193–204; estimate / floor `F` / interval endpoints — draft lines 193–204 and 285. “Under the same refusal” is four words.

### U05 — §6 Demonstration results — draft line 285 — APPROVED-R7

**Frozen quote (verbatim):** "The verdict will support the registered contrast only when evidence admission, Holm, floor, and direction checks all pass; otherwise it will print the exact refusal."

**A = B — verdict issued:** The verdict supported the registered contrast only when evidence admission, Holm, floor, and direction checks all passed; otherwise it printed the exact refusal.

**C — contrast refused:** The verdict printed the exact reason because required records failed before reaching either comparison check, and it supported no registered contrast.

**Notes:** First-use audit: registered contrast / evidence admission / Holm / floor and direction checks — draft lines 86, 193–204, 227–229, and 264; exact refusal — draft lines 202–204. This sentence states the verdict rule once without restating the dominance falsifier.

### U06 — §6 Demonstration fixed before collection — draft line 264 — APPROVED-R7

**Frozen quote (verbatim):** "A missing or non-estimable member will remain in the frozen family of two and will not shrink the denominator."

**A = B — registered multiplicity rule:** A missing or non-estimable member remains in the frozen family of two and does not shrink the denominator.

**C — contrast refused:** A missing or non-estimable member remains in the frozen family of two and does not shrink the denominator even when required records cause the comparison to be excluded.

**Notes:** The Holm family and its two registered comparisons are built in the preceding sentence and at draft line 198.

### U07 — §Abstract — draft line 11 — APPROVED-R7 census addition

**Frozen quote (verbatim):** "This scale comes from commanded calibration pulses and is assumed to apply to sustained mixed inference load; the prospective collection will not test the transfer."

**A = B — collection completed:** The boundary scale came from commanded calibration pulses and was assumed to apply to sustained mixed inference load; this collection did not test whether the boundary scale measured with pulses also covered inference.

**C — contrast refused:** The same boundary scale came from commanded calibration pulses and was assumed to apply to sustained mixed inference load; excluding comparison records did not test whether the boundary scale measured with pulses also covered inference.

**Notes:** This is the Abstract's one retained transfer sentence. It names the source, destination, and untested question without relying on the later formal word “transport.”

### U08 — §6 Demonstration fixed before collection — draft line 264 — APPROVED-R7 census addition

**Frozen quote (verbatim):** "The two contrasts will form one Holm family with alpha = 0.05 and m = 2, a different family from the two-property containment family of Section 3."

**A = B — registered family:** The token-generation and `[PREFILL_LENGTH]`-token prompt-processing comparisons formed one two-test Holm family with alpha = 0.05 and m = 2, distinct from the two-test containment family in Section 3.

**C — contrast refused:** The same two registered comparison slots remained one Holm family with alpha = 0.05 and m = 2 when one or both comparisons were excluded; a missing value did not remove its slot.

**Notes:** The sentence replaces the superseded fixed-p256 wording while preserving the two-test denominator required by D-166's split-refusal branch.

### Census of `will ` on the hazard lines

| Draft line | `will ` sentence(s) found | Treatment |
|---:|---|---|
| 11 | construct the resolution bound; test boundary assignment; model-size comparison exercises the decision rule; collection does not test transfer | H05; H06; U01; U07 |
| 21 | produce the two components | H07 |
| 23 | demonstrate how the result governs a claim | H49 |
| 25 | characterize one physical configuration; not establish, compare, or transfer beyond it | H50 |
| 30 | none | H03 has no `will ` occurrence |
| 31 | exercise the decision behavior; report the decisions | H08 covers the full sentence |
| 187 | none | H09 has no `will ` occurrence |
| 243 | report null first; give null quantities; support-floor criterion; collection not occurred | H10; H11; U02; H02 |
| 260 | compare models; use ten blocks; use fixed token-generation prompt; use fixed prompt-processing prompt | H12; H13; H14; H15 |
| 262 | publish cell bound; transport timing term; “No floor will transport…” | H16; H17; standing rule — no change proposed |
| 264 | form Holm family; form p-value; compare ordered p-values; missing-member denominator | U08; H18; H19; U06 |
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

**Full replacement paragraph:** The repository is tamper-evident for the operator's own benefit — a way to catch one's own mistakes — not tamper-proof against anyone; it assumes a single trusted operator, so every gate defends against error and post-hoc choice, never against an adversary. It provides internal consistency, not third-party provenance. The 748 bundles made with the retired clock-anchor calculation remain auditable under that calculation but are permanently barred from claims: admission rejects their method label, and reprocessing claim energies under the replacement method after seeing the data would be retrospective analysis. These are limits on what the record proves, not exceptions to its gates.

**Notes:** R-4 requires this order. The D-161 sentence opens verbatim, the one short scope clause follows verbatim, and the frozen paragraph's old first sentence is dropped. “These” remains plural because the paragraph names two limits: third-party/adversarial provenance and the retired bundles' permanent claim bar.

### Item 10 — §6 null row first (A / B / C / D)

Use the following as the opening of “### Results.” If characterization ran, print this lead sentence before the selected A, B, or C continuation: “The largest authenticated absolute A/B/B/A difference in the identical-condition null block was `[D_C_null_max_abs_J]` J, and its registered outcome was `[PLAIN_LANGUAGE_RESULT_null]`.” Neither token may be filled without the authenticated characterization report.

**A — dominance reproduced:** For every absolute and comparative component, the complete unguarded bound after full interval-edge corner re-evaluation was divided by the same complete unguarded bound calculated from the observed point values alone, before \(g(n)\) and the whole-window allowance. Every resulting independent-edge quotient was at least 2, and every comparative quotient remained at least 2 when timing error shared within each four-run block moved together using the same unguarded inputs, so the registered boundary-doubling result held in both phases.

**B — dominance not reproduced:** For every absolute and comparative component with usable evidence, the complete unguarded bound after full interval-edge corner re-evaluation was divided by the same complete unguarded bound calculated from the observed point values alone, before \(g(n)\) and the whole-window allowance. At least one resulting independent-edge quotient was below 2, or one comparative quotient fell below 2 when timing error shared within each four-run block moved together using the same unguarded inputs; the Results identify each failed component and make the boundary-doubling statement only for a phase whose required ratios all passed.

**C — contrast refused:** A required model-comparison record failed a check fixed before collection, so the opening prints only the issued reason for the affected records and reports neither a directional model result nor a boundary-movement quotient from them.

**D — prefix: characterization campaign not run:** The identical-condition null block, which tests the resolution bound itself by comparing a workload with itself, was not collected in this campaign, so no null number is reported and the published floors below stand without their own falsification test; that test is the first item of future work.

**Notes:** D is the R-3 prefix and its sentence is unchanged from the ruled D text. When D applies, print it instead of the tokenized characterization lead, then append A, B, or C. When characterization ran, print the tokenized lead, then append A, B, or C. H10 is superseded, so the null number prints once; H11 refers to it without reprinting it. At fill time, print only `[REFUSAL_REASON_1p7B_floor_window]`, only `[REFUSAL_REASON_8B_floor_window]`, or both as separate reasons if both windows failed.

The Section 3 Holm family remains the null-mean and prefill-invariance containment pair; the Section 6 Holm family contains the token-generation and `[PREFILL_LENGTH]`-token prompt-processing comparisons. These are two distinct families of two, not one family of four.

## Reviewer-panel desk additions

Every block below is **ADDED-R7** under reviewer-panel synthesis §3. Existing hazard identifiers remain unchanged.

### H30 — Appendix A.3.6 — draft line 652 — ADDED-R7 (item 6: 95/95 label)

**Frozen quote (verbatim):** "Because the bound is the sample maximum over 59 draws from it, it is a \"95/95\" bound: with at least 95 % confidence it exceeds at least 95 % of that distribution (the probability that all 59 draws fall below the 95th percentile is 0.95⁵⁹ ≈ 0.048, so 1 − 0.95⁵⁹ ≥ 0.95). It is not a deterministic out-of-sample guarantee."

**Replacement:** The pulse portion of the calibration bound is the largest of 118 observed onset and offset excursions from 59 commanded pulses in one capture; the clock-anchor allowance is then added. Because those pulses share one capture and the paper has not shown independence across pulse order or between onset and offset errors, this value is reported as the observed sample maximum, not as a “95/95” population-coverage bound. It is not a deterministic out-of-sample guarantee.

**Why and worked example:** The old calculation (1-0.95^{59}=0.9515) requires 59 independent draws. A trend shared across pulse order or correlated onset/offset errors breaks that premise, so the observed maximum remains factual while the population label is withdrawn.

### H31 — §3 prose after Table 1 — insertion before draft line 99; source phrase at draft line 94 — ADDED-R7 (item 10: n=40 versus n=16)

**Frozen source quote (verbatim; draft line 94):** "Evaluate each slope at every joint corner of the authenticated energy intervals."

**Insertion as prose immediately after Table 1 and before the paragraph at draft line 99; do not insert inside the workload-response table cell:** In the workload-response row, “every corner” is evaluated analytically rather than by listing `2^40 = 1,099,511,627,776` endpoint combinations. The ordinary-least-squares slope is a weighted sum of the 40 energies, so its minimum uses the lower endpoint for every positive weight and the upper endpoint for every negative weight, and its maximum reverses those choices. The separate component calculation described later refuses exact enumeration above `n=16` because it recomputes a mean and standard deviation at each corner, a step this linear slope does not require.

**Why:** This states the executable distinction. Forty intervals are tractable here because only two sign-selected endpoint vectors are needed; the nonlinear component formula retains the enumeration cap.

### H32 — §9 Evidence and code availability — draft line 350 — ADDED-R7 (item 12: floor binding)

**Frozen quote (verbatim):** "Until FLOOR-BIND-01 closes, a floor may support a claim only when governed extraction and the consuming analysis run in the same lead-controlled custody session under the same manifest, with the extraction gates demonstrably executed."

**Replacement:** Independent re-reduction requires a separate consumer that starts from the released primary bytes and fixed manifest. It must rederive every included member and every allowed timing width, compare that complete set with the floor artifact, and refuse any mismatch before comparison analysis; for example, if the floor artifact lists ten four-run blocks but the manifest-derived set contains nine, the consumer must stop rather than use the floor. Because that consumer does not yet exist, a floor may support a claim only when governed extraction and the consuming analysis run in the same lead-controlled custody session under the same manifest, with the extraction checks demonstrably executed.

**Why:** The replacement states the missing mechanism, its failure behavior, and the present limitation without exposing the internal work-order name.

### H33 — §1 resolution-bound paragraph — draft line 19 — ADDED-R7 (item 13: one physical glossary)

**Frozen quote (verbatim):** "For runs that share the same phase, workload, model, hardware, software, and power definition, JouleWise constructs the cell's resolution bound — the artifact calls it the detection floor — “the largest false difference this measurement system can manufacture.” It includes ordinary repeat-to-repeat variation and the energy that calibrated uncertainty in boundary placement could move across a phase edge. The timing component is measured with commanded graphics-processor pulses inside the same uninterrupted collection session in which it is used. Carrying that component to sustained mixed inference load is an assumption, not a tested result; §7 treats this as the primary limitation."

**Replacement:** For runs that share the same phase, workload, model, hardware, software, and power definition, JouleWise constructs a separate resolution bound for each cell from ordinary repeat-to-repeat variation and the energy that calibrated boundary uncertainty could move across the phase edge. Its timing component comes from commanded graphics-processor pulses captured inside the same uninterrupted collection session.

**Why:** The Abstract keeps the one physical glossary. The transfer limitation remains in the Abstract, Discussion, and Conclusion.

### H34 — §2 transfer restatement — draft line 53 — ADDED-R7 (item 13)

**Frozen quote (verbatim):** "This calibrates edge placement under commanded GPU pulses and then transports that bound to sustained mixed inference load. That load-regime transfer is an applicability assumption, not a result: the pre/post bracket tests change across a window, but it does not test whether the pulse-derived bound transfers to inference."

**Replacement:** Commanded GPU pulses calibrated edge placement, but applying that bound to sustained mixed inference remained an untested assumption. The before-and-after bracket tested change across the measurement window; it did not test whether the pulse-derived bound applied to inference.

### H35 — §4 bracket paragraph — draft line 164 — ADDED-R7 (item 13)

**Frozen quote (verbatim):** "This screen was characterized with commanded GPU pulses and is transported to sustained mixed inference load; the frozen `_v4` campaign does not test that transfer."

**Replacement:** The timing envelopes applied a bound characterized with commanded GPU pulses to sustained mixed inference; this collection did not test that transfer.

### H36 — §7 repeated physical glossary — draft line 298 — ADDED-R7 (item 13)

**Frozen quote (verbatim):** "The cell's resolution bound—the artifact calls it the detection floor—is “the largest false difference this measurement system can manufacture.”"

**Replacement:** Delete this sentence; H05 owns the definition, and the surrounding Discussion already uses the established term.

### H37 — §8 related-work transfer restatement — draft line 326 — ADDED-R7 (item 13)

**Frozen quote (verbatim):** "The calibration uses commanded GPU pulses under a lighter CPU regime, however, and this capstone does not test whether its timing bound transfers unchanged to sustained mixed inference load (Section 7)."

**Replacement:** Delete this sentence; Section 7 owns the limitation, while the preceding related-work sentence retains the methodological distinction.

### H38 — Figure 1 prose walk — draft line 37 — ADDED-R7 (item 13)

**Frozen quote (verbatim):** "Figure 1 names the mechanism. Its horizontal time axis, vertical power axis, pale grid, and gray step rectangles show interval-average samples; the dashed trace is idealized underlying power. The lower gray bars name prefill and decode. The black vertical line is the runtime-recorded boundary, the blue band is its calibrated timing bound, and the hatched sliver is the energy that changes phase if the true boundary lies at a band edge. Double-headed arrows name one sampler interval and the power step; the blue callout arrow identifies the sliver. The legend and four notes name the marks, the high-power prefill and lower-power decode regimes, the blended sample at the boundary, and the unchanged request total."

**Replacement:** Figure 1 shows interval-average power around the recorded boundary between prompt processing and token generation, with the allowed boundary positions marked as a band. The hatched area is the energy reassigned between phases when the boundary moves across that band; the request total does not change.

### H39 — Figure 2 prose walk — draft lines 55 and 57 — ADDED-R7 (item 13)

**Frozen quote 1 (verbatim):** "Figure 2 maps that bracket onto one complete measurement window. The gray horizontal arrow across the top points in the direction of session time. Blue-outlined boxes at the two ends are the pre-window and post-window calibration pulse trains; the blue bracket joining them says that the timing bound is measured on both sides of the science work and that the operative bound uses the larger capture plus a measured, never-zero allowance for change between them. The gray admission-gate box is the immediate pre-measurement check: its accompanying note names quiet state, power policy, thermal pressure, clock anchoring, and calibration freshness, and says that a failed check refuses the stage. The three small gray bars in the opening reference box, the single bar in the midpoint box, and the three bars in the closing reference box are fixed-workload reference runs used to measure drift. Between them, the two large white science-stage boxes contain small gray run bars grouped into A/B/B/A blocks—condition A, condition B, condition B, condition A. Box widths are illustrative rather than elapsed-time measurements, and the figure contains no measured data."

**Frozen quote 2 (verbatim):** "The pale lower inset expands one A/B/B/A block. Its black vertical axis is measured value and its horizontal slot sequence runs from slot 1 through slot 4. A dashed sloping gray line, identified by a short gray leader, represents steady drift. Four circles lie on that line: white A circles occupy slots 1 and 4, while blue B circles occupy slots 2 and 3. The dashed blue vertical line marks the common average position in time. The two blue brackets below the circles show that the mean time of the two B runs and the mean time of the two A runs both land on that line. The right-hand notes state the consequence: steady linear drift subtracts from \((B_1+B_2-A_1-A_2)/2\), whose positive sign means B used more energy; curvature does not cancel and remains covered by the reference-derived whole-window drift allowance. Counterbalancing therefore reduces common linear drift but never replaces the measured allowance."

**Replacement for both quoted draft passages, aligned with structural sheet S05:** Figure 2 orders the before-and-after pulse calibrations, entry check, reference runs, and science blocks within one measurement window. Each science block uses A/B/B/A order—condition A, condition B, condition B, condition A—and names the four measured energies \(A_1,B_1,B_2,A_2\) in that order. Its block difference is \((B_1+B_2-A_1-A_2)/2\); a positive value means condition B used more energy than condition A. Matching the average run time of the two A members to that of the two B members cancels steady linear drift, while curvature remains covered by the separately measured whole-window allowance.

### H40 — Figure 3 prose walk — draft lines 202–204 — ADDED-R7 (item 13)

**Frozen quote (verbatim):** "Figure 3 separates evidence refusal from the two claim gates."

**Replacement for the two prose paragraphs before the Figure 3 image:** Figure 3 sends missing, stale, contaminated, duplicated, inconsistent, or unauthenticated records directly to a printed exclusion reason before either comparison check. Usable records first test whether the measured magnitude exceeds the cell floor: failure is *not resolvable*; if it passes but the complete uncertainty range does not settle the registered direction, the result is *direction unresolved* and no claim is made; only passage of both checks produces a direction.

### H41 — §2 channel timing — draft line 35 — ADDED-R7 (item 16, channel sentence)

**Insertion after the first sentence:** CPU, GPU, and neural-engine power are three fields in the same sampling record and therefore share its start and end time when clipped to a phase; in the worked record in Appendix A.3.1, approximately 0.917 W CPU, 0.009 W GPU, and 0.000 W neural-engine power all occupy the same 0.111 s interval, so no separate channel clock is assumed.

**Why:** The pulse fit uses GPU power to locate the shared record edge; phase integration then clips all three simultaneously sampled channel fields at that edge.

### H42 — §4 allowance accounting — draft line 177 — ADDED-R7 (item 16, absolute component and no double count)

**Insertion after step 6:** The absolute component remains in the paired-comparison floor because it covers energy variation within either model arm that A/B/B/A ordering does not remove, while each component's `A_k` covers curved or otherwise non-linear change across the measurement window after the order cancels only a steady linear trend; in the synthetic example below, the 0.4 J window allowance is added once to the 2.4984 J absolute and 2.6484 J comparative guarded terms, yielding 2.8984 J and 3.0484 J, after which the cell uses their maximum, 3.0484 J, rather than their sum.

### H43 — §3 prose after Table 1 — draft line 99 — ADDED-R7 (item 16, null power)

**Insertion as prose immediately after Table 1 and before the paragraph at draft line 99; do not insert inside the identical-condition table row:** Each magnitude tests only five fresh A/B/B/A blocks, so passage shows that those five manufactured differences and their intervals fit inside the earlier comparator but does not establish a 95% population-coverage claim or rule out a rare larger false difference. For example, with a 3 J comparator, five intervals inside `[-3, 3]` J pass the registered containment rule, while the paper makes no claim about what fraction of future blocks will remain inside that range.

### H44 — §7 further limitations — draft line 308 — ADDED-R7 (item 16, joule-versus-counter framing)

**Insertion after the first sentence:** The reported joules are internal integrals of the counter's CPU, GPU, and neural-engine channels, not an independently gain-checked measurement of physical energy. In Appendix A.3.1's worked record, the 0.103 J counter total agrees after rounding with 0.103 J computed from the same record's power fields; that internal agreement is not a comparison with a separate meter, so the supported result is phase attribution within this counter's stated boundary rather than absolute-joule accuracy against wall power.

### H45 — §6 model and table labels — draft lines 278–290 — ADDED-R7 (D-164/D-166)

**Replacement rule:** First apply structural row S19, which replaces the complete Table 2 header and body with the retained columns plus the independent-edge and shared-error ratio columns and their exact registry-token cells. Then replace every `1.5B` row label with `Qwen3-1.7B`, every `7B` row label with `Qwen3-8B`, and identify prompt processing as `[PREFILL_LENGTH]` prompt tokens. In Table 3, replace `7B − 1.5B` with `Qwen3-8B − Qwen3-1.7B`; identify the token-generation arm in words as eight fixed real prompts formatted by Qwen3's fixed conversation rule, the optional reasoning-output mode switched off, and 512 output tokens generated by always choosing the highest-scored next token; identify the prompt-processing arm by `[PREFILL_LENGTH]`. Do not resolve `[PREFILL_LENGTH]` before the authenticated G2-a record and prompt-pin cross-check exist.

### H46 — §6 prompt-length rationale — draft lines 266–272 — ADDED-R7 (D-166 four-rung ladder)

**Byte-anchored frozen span (verbatim; draft lines 266–272, including the blank line 267):**

> ### Why 256 prompt tokens were selected
>
> The sizing evidence is diagnostic, not a demonstration result. Ten historical 128-token A/B/B/A blocks supplied a mean 7B-minus-1.5B prompt-processing difference of 5.809930 J. The design assumed proportional prompt-length scaling, so doubling the prompt supplied the projection
> \[
> \widehat\Delta_{256}=\frac{256}{128}(5.809930)=11.619860\ \mathrm{J}.
> \]
> The planning disclosure was `C = F + B`, where F is the applicable cell floor and B is the contrast's claim-side bound. That bound's supplier is not yet built: the registry registers it as unresolved and it is filled only after the prospective campaign issues its contrast artifact. The decision record gives only approximately 5 J for C, not its exact components: [[NEEDS-VALUE: exact cell-floor F, claim-side bound B (a separately registered quantity, not the deterministic total that widens the decision interval), and any fixed required margin used by the D-122 p256 sizing decision; checked D-122, D-139 A2, the prefill-feasibility synthesis and consult, and the current gamma manifest]]. With the disclosed approximation, 128-token clearance was `5.809930 - 5 = 0.809930 J`, or 1.16 times C; 256-token clearance was `11.619860 - 5 = 6.619860 J`, or 2.32 times C. That arithmetic selected 256. It is an **extrapolation**: none of the forty retained contrast configurations uses more than 128 prompt tokens, so the prospective arm will be the first direct longer-prompt 7B check within that evidence. No inventory of every historical corpus was compiled, so the paper claims absence only across those forty configurations.

**Replacement heading:** `### Why [PREFILL_LENGTH] prompt tokens were selected`

**Replacement for the entire byte-anchored prose/equation span:** Before collection, a four-length shakedown tested 512, 1024, 2048, and 4096 prompt tokens in that order with at least five Qwen3-1.7B probe runs at every length. A length passed only when every small-model probe contained at least five power records whose time overlapped prompt processing; five provided a safety margin of two records above the three needed to calculate a phase. For example, counts 5, 6, 7, 5, and 8 passed, while 5, 6, 4, 7, and 8 did not. The shortest passing length became `[PREFILL_LENGTH]`; Qwen3-8B probes were recorded but did not select it. If no length passed, collection still used 4096, and that fallback alone was not a refusal. A final count below 3 printed the reduction program's `not_resolvable_sample_count` reason; a count of 3 or 4 remained calculable but printed the recorded reason “below the pre-registered count floor of 5,” meaning that it missed the stricter five-record design minimum, beside that result. This split kept an instrument failure distinct from a stricter design choice and left the two-comparison Holm family unchanged.

### H47 — §10 demonstration identity — draft line 356 — ADDED-R7 (D-164/D-166)

**Frozen quote (verbatim):** "The fixed 7B-versus-1.5B comparison demonstrates the resulting decision behavior; it is not a model-size scaling law."

**Replacement:** The fixed Qwen3-8B-versus-Qwen3-1.7B comparison, using the registered real-prompt token-generation arm and `[PREFILL_LENGTH]`-token prompt-processing arm, demonstrates the resulting decision behavior; it is not a model-size scaling law.

### H48 — title and subtitle branch — draft lines 2–7 — ADDED-R7 (D-165)

**Replacement title:** `JouleWise — Measuring Phase Energy in LLM Inference on Apple Silicon`

**Subtitle rule:** Drop the two-title device and every `_v4` condition. The subtitle word “attribution-limited” may appear only if every independent-edge component ratio in every cell is at least 2 and no required comparative shared-error ratio is below 2; a missing or excluded ratio does not select the subtitle.

**Methods sentence (ruled content):** The subtitle uses *attribution-limited* only when every independent-edge component ratio in every cell is at least 2 and no required comparative shared-error ratio is below 2; a missing or excluded ratio does not select that subtitle.

**Methods home — RATIFIED:** Insert this sentence after the shared/local replay construction in structural sheet S03 and before the identical-condition-null sentence at frozen draft line 187. Structural sheet S04 records the same ratified placement; the cold ruling's verified packet history takes the magistrate's placement ratification on the record.

### H49 — §1 Introduction — draft line 23 — ADDED-R7 (SF-6)

**Frozen quote (verbatim):** "The planned model-size comparison will demonstrate how this measurement result governs a claim; it is not the paper's destination."

**Replacement:** The model-size comparison demonstrated how the measurement result governed a claim; it was not the paper's destination.

### H50 — §1 Introduction — draft line 25 — ADDED-R7 (SF-6)

**Frozen quote (verbatim):** "The result will characterize one physical machine, one MLX software stack, one *powermetrics* sampling configuration, and the processor power channels included in that counter. It will not establish whole-system energy without an external meter, compare vendors, or transfer a numerical bound to another machine, workload family, sampler cadence, or software stack."

**Replacement:** The result characterized one physical machine, one MLX software stack, one *powermetrics* sampling configuration, and the processor power channels included in that counter. It did not establish whole-system energy without an external meter, compare vendors, or transfer a numerical bound to another machine, workload family, sampler cadence, or software stack.

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
| H11 | 243 | 194 | `[PLAIN_LANGUAGE_RESULT_null]` | 454 |
| H12 | 260 | 129 | — | — |
| H13 | 260 | 133 | — | — |
| H14 | 260 | 53 | — | — |
| H15 | 260 | 121 | — | — |
| H16 | 262 | 182 | — | — |
| H17 | 262 | 200 | — | — |
| H18 | 264 | 140 | — | — |
| H19 | 264 | 120 | — | — |
| H20 | 276 | 98 | STOP_FILL rows DS-09, DS-13, DS-17, DS-21 in Notes | 798, 802, 806, 810 |
| H21 | 276 | 325 | STOP_FILL rows DS-10, DS-14, DS-18, DS-22 in Notes | 799, 803, 807, 811 |
| H22 | 276 | 126 | — | — |
| H23 | 285 | 52 | `[E_decode_contrast_signed_J_per_request]`; `NO-TOKEN PG-01` in Notes | 372, 824 |
| H24 | 285 | 144 | `[E_decode_contrast_lower_J]`, `[E_decode_contrast_upper_J]`; `NO-TOKEN PG-02` in Notes | 373, 374, 825 |
| H25 | 285 | 59 | `[F_claim_decode_armwise_max_J]`; `NO-TOKEN DS-33` in Notes | 376, 822 |
| H26 | 285 | 88 | `NO-TOKEN DS-30`, `NO-TOKEN PG-06` in Notes; STOP_FILL rows DS-29, PG-05 | 819, 828, 818, 827 |
| H27 | 298 | 225 | — | — |
| H28 | 356 | 173 | — | — |
| H29 | 356 | 278 | — | — |
| U01 | 11 | 230 | — | — |
| U02 | 243 | 191 | — | — |
| U03 | 285 | 149 | STOP_FILL claim-side-bound rows in Notes | 802, 812 |
| U04 | 285 | 129 | — | — |
| U05 | 285 | 165 | — | — |
| U06 | 264 | 110 | — | — |
| U07 | 11 | 169 | — | — |
| U08 | 264 | 154 | `[PREFILL_LENGTH]` | 161 |
| H30–H44 | added-R7 | n/a (reviewer additions) | no new result tokens | synthesis items 6, 10, 12, 13, 16 |
| H45–H47 | added-R7 | n/a (D-164/D-166 additions) | `[PREFILL_LENGTH]`; `_v5` registry vocabulary | 140–151 |
| H48 | added-R7 | n/a (D-165 title rule) | — | 265–273 |
| H49–H50 | 23, 25 | 130; 365 | — | — |
| Item 10 | 243 | n/a (ruling replacement) | `[D_C_null_max_abs_J]`, `[PLAIN_LANGUAGE_RESULT_null]`, `[REFUSAL_REASON_1p7B_floor_window]`, `[REFUSAL_REASON_8B_floor_window]` | 444, 454, 306, 307 |
| Item 60 | 310 | n/a (ruling replacement) | — | — |
