# Round-7 retensing plan (prepared while draft-v1.md is frozen)

This file is the round-7 substitution sheet; it does not edit the frozen draft.
Round 7 selects one ready sentence at each hazard after the issued artifacts and replay fence fix the outcome.
Outcome A means the code's per-component timing-widened term exceeds its guarded point-only term in both phases; B means admitted evidence produces at least one non-exceeding phase; C means a required window or contrast is refused before that predicate can be evaluated.
The sixteen TERM rows decide A versus B; the two floor-window refusal tokens and the authenticated gamma verdict decide C, which takes precedence over A/B selection.

## Outcome definitions

**A — dominance reproduced.** For every claim-bearing absolute and comparative component in both phases, the item-34 code predicate is true: the exact linear corner maximum (TERM B) strictly exceeds the guarded point-only repeatability value (TERM A).

**B — dominance not reproduced.** Required evidence is admitted, but in at least one phase at least one TERM B does not exceed its matching TERM A, so item 8 rejects dominance for that phase; one failed phase narrows the claim to the other, while failure in both leaves a calibration that corrected its clock-model error followed by a prospective null.

**C — contrast refused.** Required evidence is excluded from claim calculations by the 1.5B or 7B whole-window gate, for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, or by gamma's authenticated decode or prompt verdict, `[[NO-TOKEN: DS-32 — authenticated conservative gamma decode verdict]]` or `[[NO-TOKEN: PG-08 — authenticated conservative gamma prompt verdict]]`; the dominance predicate is therefore unevaluated, and the paper makes neither a phase-dominance claim nor a model-ranking claim.

The phase decision is mechanical and component-specific; there is no invented aggregate. Prompt processing uses the first four pairs below and token generation uses the last four. A phase passes only if all four TERM B values strictly exceed their paired TERM A values; otherwise that phase uses the B wording, while an admitted passing phase uses the A wording.

| Phase | Model/component | Guarded point-only TERM A | Exact corner TERM B |
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

**Fails:** A, B, and partial C: the current renderer STOP_FILLs A/B on `[B_decode_claim_J]`, C1/C2 on unknown reported means, and can emit only D or C3.

**A — dominance reproduced:** Both model-specific floor windows passed, the per-component dominance predicates reproduced the registered phase result, and the tables below report the cell branches and gamma decision selected by the renderer's A, B1, or B2 predicate and filled under `docs/paper/round7/fill-checklist.md`.

**B — dominance not reproduced:** Both model-specific floor windows passed and the tables below report the renderer-selected gamma decision under `docs/paper/round7/fill-checklist.md`; at least one prompt-processing or token-generation timing-widened TERM B did not exceed its paired repeatability TERM A, so dominance is rejected for each such phase and retained only for a phase whose four pairs passed, while failure in both leaves a corrected-clock calibration followed by a prospective null.

**C — contrast refused:** Required floor evidence was refused by the 1.5B or 7B whole-window gate for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so the renderer's D, C1, C2, or C3 predicate supplies the applicable nonpublication text, the tables follow `docs/paper/round7/fill-checklist.md`, and no phase-dominance or model-ranking claim is made.

**Notes:** This is a lead-in, not a fourth renderer branch: A/B reuse the complete-floor predicate family, and C reuses D/C1/C2/C3. “Refused” and the side path around both gates were built at draft lines 202–204; the sibling checklist owns table fills.

### H02 — §6 Results — draft line 243 — FIXED

**Frozen quote (verbatim):** "Collection has not occurred, so no null value or outcome is stated here."

**Fails:** A/B/C: every round-7 outcome presupposes that collection ran and issued a verdict.

**A — dominance reproduced:** Collection completed, and the null result reported first below preceded the reproduced attribution-dominance result.

**B — dominance not reproduced:** Collection completed and the null result appears first; at least one prompt-processing or token-generation timing-widened term did not exceed its repeatability term, so dominance is rejected for each such phase and retained only for a phase whose four pairs passed, while failure in both leaves a corrected-clock calibration followed by a prospective null.

**C — contrast refused:** Collection completed, but required floor or gamma evidence was refused by the 1.5B or 7B whole-window gate for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, leaving dominance unevaluated and supporting no phase-dominance or model-ranking claim.

**Notes:** Item 10's complete replacement opening appears under “Additional ready text”; draft lines 185–187 already build the null test and the three floor quantities.

### H03 — §1 Introduction — draft line 30 — FIXED

**Frozen quote (verbatim):** "The second contribution is a cell-specific resolution bound and the prospective attribution-dominance finding; §3 characterizes the instrument, §4 composes the bound, and §6 reports the test."

**Fails:** B/C structurally: “the … finding” presupposes a positive, admitted finding rather than a null or refusal.

**A — dominance reproduced:** The second contribution is the cell-specific resolution bound and the reproduced attribution-dominance result; §3 characterizes the instrument, §4 composes the bound, and §6 reports the test.

**B — dominance not reproduced:** The second contribution is the cell-specific resolution bound and its negative falsification result: at least one prompt-processing or token-generation timing-widened term did not exceed its repeatability term, so dominance is rejected for each such phase and retained only for a phase whose four pairs passed, while failure in both leaves a corrected-clock calibration followed by a prospective null; §§3–4 construct the terms and §6 reports the test.

**C — contrast refused:** The second contribution is the guarded construction that refused required floor or gamma evidence at the 1.5B or 7B whole-window gate for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`; §3 characterizes the instrument, §4 composes admitted bounds, and §6 reports why no phase-dominance or model-ranking claim follows.

**Notes:** “Resolution bound” is physically built at draft lines 15–19 before this site; C spells out the exclusion and consequence instead of using an unglossed “admission”.

### H04 — §7 Discussion and limitations — draft line 296 — FIXED heading

**Frozen quote (verbatim):** "What the finding changes"

**Fails:** B/C structurally: it assumes that an attribution-dominance finding was made.

**A — dominance reproduced:** What reproduced dominance changes

**B — dominance not reproduced:** What changes when a prompt-processing or token-generation timing-widened term does not exceed repeatability, rejecting dominance for that phase and leaving a corrected-clock calibration followed by a prospective null if both phases fail

**C — contrast refused:** What the refused 1.5B, 7B, or gamma evidence establishes — and why no phase-dominance or model-ranking claim follows

**Notes:** Heading forms intentionally remain headings. Draft lines 292–294 already establish the discussion context; the following paragraph must use the same selected outcome.

### H05 — §Abstract — draft line 11 — FIXED

**Frozen quote (verbatim):** "For each group of like-for-like runs, called a cell, the analysis will construct the cell's resolution bound — the artifact calls it the detection floor — “the largest false difference this measurement system can manufacture.”"

**Fails:** C: refused evidence need not yield a claim-bearing cell bound.

**A — dominance reproduced:** For each admitted group of like-for-like runs, called a cell, the analysis constructed the cell's resolution bound — the artifact calls it the detection floor — “the largest false difference this measurement system can manufacture.”

**B — dominance not reproduced:** For each admitted group of like-for-like runs, called a cell, the analysis constructed the cell's resolution bound — the artifact calls it the detection floor, “the largest false difference this measurement system can manufacture” — but at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** Required records failed the 1.5B or 7B whole-window checks for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so the code excluded them from claim calculations, constructed no claim-bearing cell resolution bound from them, and supports no phase-dominance or model-ranking claim.

**Notes:** A/B pass the first-use test by building the physical quantity before naming “resolution bound” and then giving item 21's gloss; C deletes “detection floor” because no artifact quantity issued.

### H06 — §Abstract — draft line 11 — FIXED

**Frozen quote (verbatim):** "The results will test whether boundary assignment contributes more than run-to-run variation to the bound for prompt processing and token generation on the named configuration."

**Fails:** C: admission refusal leaves the dominance predicate unevaluated.

**A — dominance reproduced:** In both prompt processing and token generation, every exact corner term exceeded its guarded point-only repeatability term, so boundary assignment contributed more than run-to-run variation on the named configuration.

**B — dominance not reproduced:** At least one prompt-processing or token-generation timing-widened exact corner term did not exceed its guarded point-only repeatability term, so dominance is rejected for each such phase and retained only for a phase whose four comparisons passed, while failure in both leaves a corrected-clock calibration followed by a prospective null.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused required evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so the boundary-versus-repeatability predicate remained unevaluated and the paper makes no phase-dominance or model-ranking claim.

**Notes:** The preceding abstract sentences physically build boundary reassignment and ordinary variation. The eight TERM pairs in “Outcome definitions” supply the per-phase decision without an aggregate.

### H07 — §1 Introduction — draft line 21 — FIXED

**Frozen quote (verbatim):** "The two components will be produced independently for every phase cell that could support a claim."

**Fails:** C: refused evidence may produce no admissible component pair.

**A — dominance reproduced:** The guarded point-only repeatability value and the exact corner maximum were produced independently for every admitted absolute and comparative phase component, and every corner value was larger.

**B — dominance not reproduced:** The guarded point-only repeatability value and timing-widened exact corner maximum were produced independently, and at least one prompt-processing or token-generation corner value did not exceed its paired repeatability value, so dominance is rejected for each such phase and retained only for a phase whose four pairs passed, while failure in both leaves a corrected-clock calibration followed by a prospective null.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused the records needed to form a component pair for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so dominance remained unevaluated and no phase-dominance or model-ranking claim is made.

**Notes:** Draft lines 15–19 build repeatability, boundary reassignment, and the cell bound; this replacement glosses “point-only” as the value formed before allowed edge positions widen energy.

### H08 — §1 Introduction — draft line 31 — FIXED

**Frozen quote (verbatim):** "The third contribution is the decision behavior the prospective demonstration will exercise — two gates, printed refusals, and the resolvability rule; §5 defines when collection stops, and §6 will report the resulting decisions."

**Fails:** C: evidence refusal bypasses both claim gates, so the stated two-gate exercise does not occur.

**A — dominance reproduced:** The third contribution is the demonstration's recorded decision behavior — separate magnitude and direction gates, printed refusals, and the resolvability rule; §5 defines collection stops, and §6 reports the decisions.

**B — dominance not reproduced:** The third contribution is the demonstration's recorded decision behavior — separate magnitude and direction gates, printed refusals, and the resolvability rule — while at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed; §§5–6 define and report the decisions.

**C — contrast refused:** Required evidence entered neither claim gate because the 1.5B or 7B whole-window gate refused it for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`; §5 defines that stop, §6 prints it, and no phase-dominance or model-ranking claim is made.

**Notes:** Draft line 23 already builds both gates, refusal, and resolvability in plain words; C preserves the Figure 3 side-path semantics from lines 202–204.

### H09 — §4 The resolution bound and how it is composed — draft line 187 — FIXED

**Frozen quote (verbatim):** "Passing the identical-condition null block at the corner-widened resolution bound tests the bound itself, and §6 reports that null number first."

**Fails:** C: no admitted null number is guaranteed.

**A — dominance reproduced:** The identical-condition null block's largest authenticated absolute difference, `[D_C_null_max_abs_J]` J, is reported first in §6 and tests the corner-widened resolution bound itself.

**B — dominance not reproduced:** The identical-condition null block's largest authenticated absolute difference, `[D_C_null_max_abs_J]` J, is reported first and tests the corner-widened resolution bound, but at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused required claim evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`; §6 still reports the separately admitted null number first, but dominance remains unevaluated and no phase-dominance or model-ranking claim follows.

**Notes:** Draft line 185 defines “corner-widened” and distinguishes the published floor from TERM B and `floor_gate_j`; `[D_C_null_max_abs_J]` is registry line 434.

### H10 — §6 Results — draft line 243 — FIXED

**Frozen quote (verbatim):** "The identical-condition null result will be reported first because it tests the floor itself: when A and B are the same workload, every nonzero A/B/B/A block difference is manufactured by the measurement system."

**Fails:** C: a refused window may issue only refusal diagnostics, not this result.

**A — dominance reproduced:** The largest authenticated absolute A/B/B/A difference in the identical-condition null block was `[D_C_null_max_abs_J]` J and is reported first because, with the same workload in A and B, every nonzero block difference was manufactured by the measurement system.

**B — dominance not reproduced:** The largest authenticated absolute A/B/B/A difference in the identical-condition null block was `[D_C_null_max_abs_J]` J and is reported first, while at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The separately admitted null block's largest authenticated absolute difference was `[D_C_null_max_abs_J]` J and is reported first, while the 1.5B or 7B whole-window gate refused the claim evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, leaving dominance unevaluated and supporting no phase-dominance or model-ranking claim.

**Notes:** This reports the null number before any other number. The “same workload” clause is the physical gloss; item 10's full opening appears below.

### H11 — §6 Results — draft line 243 — FIXED

**Frozen quote (verbatim):** "The issued result will give the mean block difference and its composed interval, the largest absolute block difference, the independently issued same-cell comparator, and the registered outcome."

**Fails:** C: those claim-bearing quantities need not issue.

**A — dominance reproduced:** The issued null row reports `[D_C_null_max_abs_J]` J first as its largest absolute block difference and then gives its registered outcome, `[PLAIN_LANGUAGE_RESULT_null]`; no registry token exists for the mean, composed interval, or same-cell comparator, so those quantities are not invented.

**B — dominance not reproduced:** The issued null row reports `[D_C_null_max_abs_J]` J first and `[PLAIN_LANGUAGE_RESULT_null]` second, with no invented mean, interval, or comparator; at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The separately admitted null row reports `[D_C_null_max_abs_J]` J first and `[PLAIN_LANGUAGE_RESULT_null]` second, while the 1.5B or 7B whole-window gate refused claim evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so dominance remained unevaluated and no phase-dominance or model-ranking claim follows.

**Notes:** Registry rows at lines 434 and 444 supply the only claim-bearing null number and outcome; unsupported mean/interval/comparator slots are deleted rather than represented by invented tokens.

### H12 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "The prospective demonstration will compare 4-bit Qwen2.5 7B with 1.5B on the named M3 Max, MLX, and *powermetrics* configuration."

**Fails:** A/B/C temporally: at round 7 the campaign is no longer prospective; under C the comparison may remain unevaluated.

**A — dominance reproduced:** The demonstration compared 4-bit Qwen2.5 7B with 1.5B on the named M3 Max, MLX, and *powermetrics* configuration.

**B — dominance not reproduced:** The demonstration compared 4-bit Qwen2.5 7B with 1.5B on the named stack, but at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The demonstration registered 4-bit Qwen2.5 7B against 1.5B, but the 1.5B or 7B whole-window gate refused required evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so the comparison and dominance predicate remained unevaluated and no model ranking follows.

**Notes:** “Registered” states the fixed design without claiming an admitted comparison; the named stack was already built at draft lines 15–23.

### H13 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "Each contrast will use ten independent A/B/B/A blocks, where A is 1.5B, B is 7B, and one block difference is `(B1 + B2 - A1 - A2)/2`."

**Fails:** C: an admission refusal can prevent ten admitted blocks.

**A — dominance reproduced:** Each admitted contrast used ten independent A/B/B/A blocks, with A as 1.5B, B as 7B, and block difference `(B1 + B2 - A1 - A2)/2`.

**B — dominance not reproduced:** Each admitted contrast used ten independent A/B/B/A blocks with difference `(B1 + B2 - A1 - A2)/2`, but at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The registered contrast specified ten A/B/B/A blocks, but the 1.5B or 7B whole-window gate refused the required evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so no ten-block admitted contrast, phase-dominance claim, or model-ranking claim follows.

**Notes:** Draft lines 227–229 already build the block order and formula; C distinguishes specification from admitted execution.

### H14 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "Token generation will use the fixed 128-token prompt."

**Fails:** some C cases: refusal can occur before any admitted token-generation run.

**A — dominance reproduced:** Admitted token-generation runs used the fixed 128-token prompt.

**B — dominance not reproduced:** Admitted token-generation runs used the fixed 128-token prompt, but at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The token-generation arm registered the fixed 128-token prompt, but the 1.5B or 7B whole-window gate refused required evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so no admitted token-generation comparison or model ranking follows.

**Notes:** “Registered” pays for the fixed design without asserting that a refused arm ran.

### H15 — §6 Demonstration fixed before collection — draft line 260 — FIXED

**Frozen quote (verbatim):** "Prompt processing will use the fixed synthetic 256-token prompt with identical token identifiers across model tokenizers."

**Fails:** some C cases: refusal can occur before that arm runs.

**A — dominance reproduced:** Admitted prompt-processing runs used the fixed synthetic 256-token prompt with identical token identifiers across model tokenizers.

**B — dominance not reproduced:** Admitted prompt-processing runs used the fixed synthetic 256-token prompt with identical token identifiers across model tokenizers, but at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The prompt-processing arm registered the fixed synthetic 256-token prompt and tokenizer-identity check, but the 1.5B or 7B whole-window gate refused required evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so no admitted prompt comparison or model ranking follows.

**Notes:** The tokenizer licence is defined at draft lines 260 and 276; C reports the design and the refusal separately.

### H16 — §6 Demonstration fixed before collection — draft line 262 — FIXED

**Frozen quote (verbatim):** "Each model and phase will have its own cell's resolution bound — the artifact calls it the detection floor — **the largest false difference this measurement system can manufacture**."

**Fails:** C: refused cells publish no claim-bearing floor.

**A — dominance reproduced:** Each admitted model-and-phase cell published its own resolution bound — the artifact calls it the detection floor — **the largest false difference this measurement system can manufacture**.

**B — dominance not reproduced:** Each admitted model-and-phase cell published its resolution bound — the artifact's detection floor, **the largest false difference this measurement system can manufacture** — but at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused required cell evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so no claim-bearing detection-floor artifact issued for that evidence and no phase-dominance or model-ranking claim follows.

**Notes:** “Resolution bound” and “detection floor” were built at draft lines 11 and 19; C names the artifact only to state nonissuance.

### H17 — §6 Demonstration fixed before collection — draft line 262 — FIXED

**Frozen quote (verbatim):** "Its timing term will be measured with commanded GPU pulses and transported to sustained mixed inference load; that transport is an explicit assumption, and the prospective collection does not test it."

**Fails:** some C cases: admission can refuse before an applicable timing term is established.

**A — dominance reproduced:** Each admitted cell's timing term came from commanded GPU pulses and was transported to sustained mixed inference load; that transport remains an explicit assumption untested by `_v4`.

**B — dominance not reproduced:** Each admitted cell's timing term came from commanded GPU pulses and was transported to sustained mixed inference load, but at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed; `_v4` still did not test the transport assumption.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused the evidence needed to establish an applicable timing term for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so `_v4` supports neither transport nor phase-dominance or model-ranking claims from that evidence.

**Notes:** Draft lines 45–53 physically build pulse calibration and transport before this site; “untested” is retained under every outcome.

### H18 — §6 Demonstration fixed before collection — draft line 264 — FIXED

**Frozen quote (verbatim):** "Each raw two-sided Student-*t* p-value will use the contrast estimate divided by its total standard error and its issued degrees of freedom."

**Fails:** C: an unevaluated contrast has no raw p-value.

**A — dominance reproduced:** For each admitted contrast, the raw two-sided Student-*t* p-value used the contrast estimate divided by its total standard error and its issued degrees of freedom.

**B — dominance not reproduced:** Each admitted contrast's raw two-sided Student-*t* p-value used its estimate, total standard error, and issued degrees of freedom, while at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused the contrast inputs for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so no raw p-value was formed, dominance remained unevaluated, and no phase-dominance or model-ranking claim follows.

**Notes:** The Student-*t* calculation and its issued degrees of freedom are already built at draft line 198; no statistical quantity is imputed under C.

### H19 — §6 Demonstration fixed before collection — draft line 264 — FIXED

**Frozen quote (verbatim):** "After ordering the two p-values, the smaller will be compared with 0.025, then, only if it passes, the larger with 0.05."

**Fails:** C: refusal can leave no two p-values to order.

**A — dominance reproduced:** Within the §6 contrast Holm family, the two raw p-values were ordered; the smaller was compared with 0.025 and, only after passage, the larger with 0.05.

**B — dominance not reproduced:** Within the §6 contrast Holm family the ordered p-values used thresholds 0.025 then 0.05, while at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused the inputs for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so the §6 contrast Holm family had no two p-values to order, dominance remained unevaluated, and no phase-dominance or model-ranking claim follows.

**Notes:** Draft line 198 already defines the §6 decode-plus-p256 Holm family; it remains distinct from §3's null-mean-plus-prefill-invariance family, satisfying item 54.

### H20 — §6 Demonstration results — draft line 276 — FIXED

**Frozen quote (verbatim):** "A gross cell will contain the issued phase-energy estimate and composed lower and upper endpoints."

**Fails:** C and currently A/B: refusal issues no claim-bearing cell; registry rows DS-09/13/17/21 remain `SUPPLIER_UNKNOWN`.

**A — dominance reproduced:** Gross phase-energy cells are omitted because DS-09, DS-13, DS-17, and DS-21 define no producing reported-mean schema or composed endpoint fields; no floor-component mean substitutes for them.

**B — dominance not reproduced:** Gross phase-energy cells are omitted because DS-09, DS-13, DS-17, and DS-21 define no reported-mean suppliers, and at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused claim-bearing cells for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, and DS-09/13/17/21 also lack reported-mean suppliers, so no gross value, phase-dominance claim, or model-ranking claim is reported.

**Notes:** “Composed” was built at draft lines 193–200. This is a deliberate omission, not a numerical placeholder.

### H21 — §6 Demonstration results — draft line 276 — FIXED

**Frozen quote (verbatim):** "A companion per-token cell will contain the tokenizer-scoped value whose authenticated runtime-observed denominator is fixed by the issuing schema; [[NEEDS-VALUE: D-123 producing schema for each per-token numerator, denominator, and point-or-interval rendering; the results-fill registry records these suppliers as unknown]]."

**Fails:** A/B/C currently: the promised schema/suppliers do not exist.

**A — dominance reproduced:** Per-token companions are omitted because DS-10, DS-14, DS-18, and DS-22 define neither a producing D-123 field nor an authenticated runtime-observed denominator; no requested maximum or generator estimate substitutes for them.

**B — dominance not reproduced:** Per-token companions are omitted because DS-10, DS-14, DS-18, and DS-22 define no suppliers, and at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused claim evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, and DS-10/14/18/22 lack per-token suppliers, so no per-token value, phase-dominance claim, or model-ranking claim is reported.

**Notes:** The sentence deletes the unpaid promise and preserves the tokenizer licence; the four DS rows are the registry authority for the gap.

### H22 — §6 Demonstration results — draft line 276 — FIXED

**Frozen quote (verbatim):** "A floor cell will contain its magnitude and permitted label; n will count admitted independent run bundles, not power records."

**Fails:** C: a refused cell may publish neither magnitude nor label.

**A — dominance reproduced:** Each published floor cell reports its component TERM B/TERM A ratios before the permitted label, then its magnitude; n counts admitted independent run bundles rather than power records.

**B — dominance not reproduced:** Each published floor cell reports its timing-widened TERM B/repeatability TERM A ratios before any permitted label and then its magnitude, while at least one prompt-processing or token-generation ratio was at most one, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed; n counts admitted independent run bundles rather than power records.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused the cell for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so it publishes neither magnitude nor label, dominance remains unevaluated, and no phase-dominance or model-ranking claim follows.

**Notes:** Magnitude-before-label implements item 20. Draft lines 185–189 build the corner-widened publication rule; count tokens remain supplier-unknown, so this caption does not invent n.

### H23 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The point will be the mean of ten block differences."

**Fails:** C and prompt A/B currently: the contrast may be unevaluated, and the prompt token family is missing.

**A — dominance reproduced:** The token-generation point estimate is `[E_decode_contrast_signed_J_per_request]` J per request; the prompt-processing point is `[[NO-TOKEN: PG-01 — authenticated gamma prompt contrast estimate]]`, because the registry has no prompt token.

**B — dominance not reproduced:** The token-generation point is `[E_decode_contrast_signed_J_per_request]` J per request and the prompt point is `[[NO-TOKEN: PG-01 — authenticated gamma prompt contrast estimate]]`, while at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused the contrast basis for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so no point estimate issued, dominance remained unevaluated, and no phase-dominance or model-ranking claim follows.

**Notes:** DS-25 supplies the decode estimate at registry line 798; PG-01 records the missing prompt token family at line 808.

### H24 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The interval cell will contain the fully composed lower and upper endpoints; for the registered positive direction, the lower endpoint controls."

**Fails:** C and prompt A/B currently: no admitted interval is guaranteed, and prompt endpoints lack tokens.

**A — dominance reproduced:** The token-generation decision interval is [`[E_decode_contrast_lower_J]`, `[E_decode_contrast_upper_J]`] J; the prompt interval is [`[[NO-TOKEN: PG-02 — authenticated gamma prompt lower endpoint]]`, `[[NO-TOKEN: PG-03 — authenticated gamma prompt upper endpoint]]`] J, and the registered positive direction is controlled by the lower endpoint.

**B — dominance not reproduced:** The token-generation interval is [`[E_decode_contrast_lower_J]`, `[E_decode_contrast_upper_J]`] J and the prompt interval is [`[[NO-TOKEN: PG-02 — authenticated gamma prompt lower endpoint]]`, `[[NO-TOKEN: PG-03 — authenticated gamma prompt upper endpoint]]`] J, while at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused the interval basis for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so no composed interval issued, dominance remained unevaluated, and no directional or model-ranking claim follows.

**Notes:** The decision interval is widened by `deterministic_bounds.total` as draft line 196 states; it is not equated to the unbuilt claim-side bound (item 53).

### H25 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The floor will be the larger arm-specific exact-cell floor."

**Fails:** C and prompt A/B currently: refusal supplies no claim floor; the prompt claim-floor token is missing.

**A — dominance reproduced:** The token-generation floor gate is `[F_claim_decode_armwise_max_J]` J, the larger arm-specific exact-cell floor; the prompt floor is `[[NO-TOKEN: DS-33 — authenticated gamma prompt armwise claim floor]]` because the prompt token family is missing.

**B — dominance not reproduced:** The token-generation floor gate is `[F_claim_decode_armwise_max_J]` J and the prompt floor is `[[NO-TOKEN: DS-33 — authenticated gamma prompt armwise claim floor]]`, while at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused the floor basis for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so no claim floor issued, dominance remained unevaluated, and no phase-dominance or model-ranking claim follows.

**Notes:** `[F_claim_decode_armwise_max_J]` is registry line 366; DS-33 records the missing prompt floor at line 805.

### H26 — §6 Demonstration results — draft line 285 — FIXED

**Frozen quote (verbatim):** "The sizing cell will contain `C = F + B` and signed planning clearance `|estimate| - C`."

**Fails:** A/B/C currently: decode `B_decode_claim_J` has no supplier, the prompt family is absent, and C supplies no admissible estimate/floor.

**A — dominance reproduced:** The sizing sums are omitted because the claim-side bound has no built supplier at DS-29 or PG-05, so `C = F + B` cannot be formed; the floor gate `|estimate| > F` is reported alone as `[[NO-TOKEN: DS-30 — authenticated gamma decode floor-gate outcome]]` and `[[NO-TOKEN: PG-06 — authenticated gamma prompt floor-gate outcome]]`.

**B — dominance not reproduced:** The sizing sums are omitted because the claim-side bound has no built supplier at DS-29 or PG-05, so `C = F + B` cannot be formed and the floor gate `|estimate| > F` is reported alone as `[[NO-TOKEN: DS-30 — authenticated gamma decode floor-gate outcome]]` and `[[NO-TOKEN: PG-06 — authenticated gamma prompt floor-gate outcome]]`, while at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, rejecting dominance for each such phase and leaving a corrected-clock calibration followed by a prospective null if both phases failed.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused the estimate or floor basis for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, and the claim-side bound has no supplier, so neither `C = F + B` nor a model-ranking claim is reported.

**Notes:** This is the item-33 required omission: `deterministic_bounds.total` is not the claim-side bound, and `floor_gate_j` remains the separately reported drift-added gate.

### H27 — §7 What the finding changes — draft line 298 — FIXED

**Frozen quote (verbatim):** "Experimental practice must therefore change upstream: characterize edge placement for the named workload boundary, form a separate bound for each configuration cell, and size a comparison against that bound before collection."

**Fails:** B/C structurally: under the positive heading, “therefore” treats reproduced dominance as established.

**A — dominance reproduced:** Because edge placement dominated repeatability in the admitted phase or phases, practice changes upstream: characterize the named workload boundary, form a bound for each configuration cell, and size the comparison before collection.

**B — dominance not reproduced:** At least one prompt-processing or token-generation timing-widened term did not exceed repeatability, so dominance is rejected for each such phase and retained only for a phase whose four pairs passed, while failure in both leaves a calibration that corrected its clock-model error followed by a prospective null.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused required evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so the protocol demonstrates fail-closed evidence handling but supports no phase-dominance or model-ranking claim.

**Notes:** Select A or B per phase when only one phase passes. The preceding section builds the physical practice; C avoids calling the refusal a negative scientific effect.

### H28 — §10 Conclusion — draft line 356 — FIXED

**Frozen quote (verbatim):** "For each `_v4` prefill and decode cell, the test compares the point-only repeatability bound with the same cell after calibrated phase-edge positions widen its energy range."

**Fails:** C: refused evidence does not license that comparison.

**A — dominance reproduced:** For every admitted `_v4` prompt-processing and token-generation component, the exact corner maximum exceeded the guarded point-only repeatability value, reproducing attribution dominance in both phases.

**B — dominance not reproduced:** For every admitted `_v4` component the timing-widened exact corner maximum was compared with its guarded point-only repeatability value, and at least one prompt-processing or token-generation pair did not exceed repeatability, so dominance is rejected for each such phase and retained only for a phase whose four pairs passed, while failure in both leaves a corrected-clock calibration followed by a prospective null.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused the component evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so no TERM A/TERM B comparison was licensed, dominance remained unevaluated, and no phase-dominance or model-ranking claim follows.

**Notes:** Draft lines 185–187 already distinguish the exact predicate term, published corner-widened floor, and drift-added gate; A/B use the eight registered TERM pairs rather than a new aggregate.

### H29 — §10 Conclusion — draft line 356 — FIXED

**Frozen quote (verbatim):** "The contribution makes that outcome decidable: corrected in-window timing calibration (Section 2), independent construction and comparison of the cell-specific terms (Sections 3–4), and two claim gates that preserve refusals and the short-prefill negative result (Sections 4–6)."

**Fails:** C: refusal makes dominance undecided, not decided negative.

**A — dominance reproduced:** The contribution decided the registered outcome: corrected in-window timing calibration, independent per-component construction and comparison, and two claim gates reproduced dominance while preserving refusals and the short-prefill negative result.

**B — dominance not reproduced:** The contribution decided the registered negative outcome: at least one prompt-processing or token-generation timing-widened term did not exceed repeatability, so independent comparison rejects dominance for each such phase and retains only a phase whose four pairs passed, while failure in both leaves a calibration that corrected its clock-model error followed by a prospective null.

**C — contrast refused:** The 1.5B or 7B whole-window gate refused the evidence needed for the registered comparison for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so dominance remained undecided rather than negative and the paper makes no phase-dominance or model-ranking claim.

**Notes:** “Decided” is used only for A/B, where the predicate ran. C says “undecided” and identifies the gate and consequence; the short-prefill negative result remains separately printed.

## Additional ready text

### Item 60 — §7 tamper-evidence sentence

**Ruling sentence (verbatim):** The repository is tamper-evident for the operator's own benefit — a way to catch one's own mistakes — not tamper-proof against anyone; it assumes a single trusted operator, so every gate defends against error and post-hoc choice, never against an adversary.

**Frozen paragraph replaced (verbatim):** "The repository provides internal consistency and tamper evidence, not third-party provenance. It assumes a single trusted operator and no same-user program attempting to alter evidence; a known interval between checking a floor-specification path and authorizing it could let such a program alter the authorization record, although a precommitted fingerprint prevents the swap from altering a published number. The 748 bundles made with the retired clock-anchor calculation remain auditable under that calculation but are permanently barred from claims: admission rejects their method label, and reprocessing claim energies under the replacement method after seeing the data would be retrospective analysis. These are limits on what the record proves, not exceptions to its gates."

**Full replacement paragraph:** The repository is tamper-evident for the operator's own benefit — a way to catch one's own mistakes — not tamper-proof against anyone; it assumes a single trusted operator, so every gate defends against error and post-hoc choice, never against an adversary. The 748 bundles made with the retired clock-anchor calculation remain auditable under that calculation but are permanently barred from claims: admission rejects their method label, and reprocessing claim energies under the replacement method after seeing the data would be retrospective analysis. These are limits on what the record proves, not exceptions to its gates.

### Item 10 — §6 null row first (A / B / C)

Use the following as the opening of “### Results”; in every outcome the null block's number is the first number printed. Registry row `[D_C_null_max_abs_J]` (line 434) supplies the number and `[PLAIN_LANGUAGE_RESULT_null]` (line 444) supplies its outcome; neither token may be filled without the authenticated characterization report.

**A — dominance reproduced:** The largest authenticated absolute A/B/B/A difference in the identical-condition null block was `[D_C_null_max_abs_J]` J, and the null-response row `[PLAIN_LANGUAGE_RESULT_null]`; with the floor thus tested first, the admitted TERM comparisons reproduced attribution dominance in both phases.

**B — dominance not reproduced:** The largest authenticated absolute A/B/B/A difference in the identical-condition null block was `[D_C_null_max_abs_J]` J, and the null-response row `[PLAIN_LANGUAGE_RESULT_null]`; with the floor thus tested first, at least one admitted phase had a timing-widened term that did not exceed its repeatability term, so dominance was rejected for that phase and retained only for a phase whose four comparisons passed.

**C — contrast refused:** The largest authenticated absolute A/B/B/A difference in the separately admitted identical-condition null block was `[D_C_null_max_abs_J]` J, and the null-response row `[PLAIN_LANGUAGE_RESULT_null]`; the 1.5B or 7B whole-window gate then refused the claim evidence for `[REFUSAL_REASON_1p5B_floor_window]` or `[REFUSAL_REASON_7B_floor_window]`, so dominance remained unevaluated and no phase-dominance or model-ranking claim follows.

The §3 Holm family remains the null-mean and prefill-invariance containment pair; the §6 Holm family remains the decode and fixed-p256 contrasts. These are two distinct families of two, not one family of four.

## Fidelity ledger

| Hazard | Draft line | Quote length (characters) | Placeholder tokens used | Registry line(s) |
|---|---:|---:|---|---|
| H01 | 274 | 271 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H02 | 243 | 72 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H03 | 30 | 191 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H04 | 296 | 24 | — | — |
| H05 | 11 | 226 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H06 | 11 | 176 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H07 | 21 | 98 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H08 | 31 | 228 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H09 | 187 | 144 | `[D_C_null_max_abs_J]`, `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 434, 298, 299 |
| H10 | 243 | 211 | `[D_C_null_max_abs_J]`, `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 434, 298, 299 |
| H11 | 243 | 194 | `[D_C_null_max_abs_J]`, `[PLAIN_LANGUAGE_RESULT_null]`, `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 434, 444, 298, 299 |
| H12 | 260 | 129 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H13 | 260 | 133 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H14 | 260 | 53 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H15 | 260 | 121 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H16 | 262 | 182 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H17 | 262 | 200 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H18 | 264 | 140 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H19 | 264 | 120 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H20 | 276 | 98 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H21 | 276 | 325 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H22 | 276 | 126 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H23 | 285 | 52 | `[E_decode_contrast_signed_J_per_request]`, `NO-TOKEN PG-01`, `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 362, 808, 298, 299 |
| H24 | 285 | 144 | `[E_decode_contrast_lower_J]`, `[E_decode_contrast_upper_J]`, `NO-TOKEN PG-02`, `NO-TOKEN PG-03`, `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 363, 364, 809, 810, 298, 299 |
| H25 | 285 | 59 | `[F_claim_decode_armwise_max_J]`, `NO-TOKEN DS-33`, `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 366, 805, 298, 299 |
| H26 | 285 | 88 | `NO-TOKEN DS-30`, `NO-TOKEN PG-06`, `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 803, 813, 298, 299 |
| H27 | 298 | 225 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H28 | 356 | 173 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
| H29 | 356 | 278 | `[REFUSAL_REASON_1p5B_floor_window]`, `[REFUSAL_REASON_7B_floor_window]` | 298, 299 |
