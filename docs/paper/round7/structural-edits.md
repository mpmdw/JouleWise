# Round-7 structural-edit sheet (frozen draft remains read-only)

**STATUS (2026-08-31): READY FOR JOINT PEDAGOGY RE-ADJUDICATION, EXCEPT S04'S PLACEMENT IS PROPOSED PENDING LEAD RULING.**

This sheet supplies the draft-side repairs ordered by D-1 of `05-ADJUDICATION-DISPOSITION.md`. It does not edit `draft-v1.md`. Every quoted passage below is byte-exact in the frozen 672-line draft with SHA-256 `939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab`.

At substitution time, apply these rows together with the corrected retensing plan. Result tokens containing `[PREFILL_LENGTH]` remain `UNRESOLVED-UNTIL-G2A`; nothing in this sheet supplies a campaign result. The ratios 10.92, 5.92, and 7.02 are retained pilot evidence under the retired calculation, never `_v5` campaign results.

## S01 — Build the registered ratio at its first draft use — draft line 21

**Disposition coverage:** R1, first-use portion.

**Frozen quote (verbatim; draft line 21):**

> The finding is falsified for a phase if the timing-widened bound does not exceed the point-only repeatability bound.

**Replacement:** The falsifier fixed before collection forms a quotient for each registered component in each cell: its numerator is the complete bound after every allowed interval edge moves and the full point formula is recalculated, before the later small-sample multiplier and whole-window drift allowance; its denominator is the same bound calculated from the observed point values alone. Call this quotient \(R\). Boundary placement passes this test only when every \(R\) is at least 2, with equality passing. The threshold of 2 was fixed before collection as a safety factor: allowed edge movement must add at least one entire point-only bound, rather than merely make the quotient greater than 1, which any positive interval width can do. The older coded exceedance predicate remains only as the cell's diagnostic label and does not select the paper's result.

**Authority:** `docs/decision_log.md` D-165 body and R-5 completion; `06-COLD-GATE-RULING.md` R-1, including its all-components quantifier, exact-equality rule, zero-denominator refusal, and explanation that a threshold above 1 must not be tautological; D-1 of `05-ADJUDICATION-DISPOSITION.md`.

## S02 — Replace the old exceedance construction with full-floor \(R\) — draft line 185

**Disposition coverage:** R1, §4 construction and worked example.

**Frozen quote (verbatim; draft line 185):**

> Each arrow means that the named value supplies the calculation to its right. The interval-driven term is reported separately from the point guard. A component is labelled *attribution-limited* only when at least one interval has positive width, the exact linear corner maximum used by the code's predicate strictly exceeds the guarded point-only value, and no other refusal condition is present; the emitted corner-widened guarded floor (the artifact's field name is `corner_widened_guarded_floor_j`), never the smaller point value, is then published. The attribution-dominance sentence—the falsifier—tests that exact per-component linear corner maximum against the guarded point-only value; the null-containment sentence tests the published corner-widened guarded floor, which is at least that exact maximum; and the magnitude-gate sentence tests the drift-added floor gate (the artifact's field name is `floor_gate_j`), whose added whole-window drift allowance is not a timing term, so substituting either later quantity into the falsifier would test a different proposition.

**Replacement:** Each arrow means that the named value supplies the calculation to its right. For each absolute and comparative component, first calculate the complete point-only formula from steps 1 or 2 without the later multiplier \(g(n)\) or window allowance. Then let every admitted energy or block-difference interval take its lower or upper endpoint in every joint combination; at each combination recalculate that same complete formula, including its maximum observed magnitude, mean, and sample standard deviation, and retain the largest value. The independent-edge ratio is

\[
R=\frac{\text{largest complete unguarded floor after full corner re-evaluation}}
        {\text{complete unguarded floor from the observed point values}}.
\]

If the denominator is zero, the calculation refuses rather than emitting infinity or an undefined value. Exact equality at \(R=2\) passes. The threshold was fixed before collection as a twofold safety factor: the admitted timing envelope must increase the complete point-only bound by at least one more copy of that bound, rather than pass merely because a positive interval makes \(R>1\). Every registered component in every claim-bearing cell must pass; mixed outcomes are reported by component and do not support the all-components sentence.

The retained numbers give a worked example, but only as **pilot evidence under the retired calculation, not campaign results**: \(3.153/0.2888=10.92\), \(2.922/0.4934=5.92\), and \(2.184/0.3113=7.02\) after rounding. These examples also show that the numerator is the whole floor recalculated at a corner, not a timing term divided by a scatter term.

The older coded predicate survives only as the cell's diagnostic label. Publication still applies \(g(n)\) and the component's window allowance to the corner-widened value, the null-containment test still uses that published guarded floor, and the magnitude gate still uses the final cell floor; neither later quantity is substituted into \(R\).

**Authority:** `docs/decision_log.md` D-165 body and R-5 completion; `06-COLD-GATE-RULING.md` R-1 and its full-floor-corner definition; draft line 103 for the retained pilot pairs; `docs/paper/results-fill-registry.md` D-165 ratio rows; D-1 of `05-ADJUDICATION-DISPOSITION.md`.

## S03 — Add the comparative shared-error replay — before draft line 187

**Disposition coverage:** R2 and SF-2's mechanism premise.

**Frozen anchor quote (verbatim; draft line 187):**

> Passing the identical-condition null block at the corner-widened resolution bound tests the bound itself, and §6 reports that null number first.

**Ready insertion immediately before the anchor:** The comparative shared-error replay starts from each authenticated four-run block before its timing width is collapsed into one number. For block \(j\), it reconstructs a shared excursion \(q_j\) from the registered onset and offset sweeps around their zero point, including the recorded zero-point-to-block-difference discrepancy, and a local half-width \(\ell_j\) equal to half the sum of that block's four member-residual half-widths. It then rebuilds the block difference as

\[
\delta'_j=\delta_j+s q_j+e_j\ell_j,
\]

where the one shared sign \(s\in\{-1,+1\}\) is the same for every block and each local sign \(e_j\in\{-1,+1\}\) is chosen independently. The replay enumerates both shared signs and every combination of local signs. At every such corner it recalculates the complete comparative unguarded floor—both the largest absolute block difference and the prediction expression built from the new mean and sample standard deviation—and retains the maximum. Dividing that maximum by the comparative point-only unguarded floor gives \(R_{cm}\). A comparative \(R_{cm}<2\) withdraws the boundary-dominance sentence even when independent-edge \(R\ge2\).

Absolute rows do not report this comparative replay as though it were a measurement. They print `not_applicable`: the registered absolute estimator first subtracts its cell mean, so under the replay's stated idealization that one shared fiducial timing error displaces every observation uniformly, that displacement cancels exactly. This cancellation is the reason for `not_applicable`, not evidence that a shared timing error is physically absent.

**Authority:** `docs/decision_log.md` D-165 R-5 completion; D-165-as-amended index row; `06-COLD-GATE-RULING.md` R-2; the registered replay in `configs/campaigns/d117_contrast_v5/generate_configs.py` (`_common_mode_split`, `replay_common_mode_dominance`, and the `d165_shared_sign_local_corner_replay.v1` registration); `docs/paper/results-fill-registry.md` comparative and absolute R_cm rows.

## S04 — Methods disclosure for the contingent subtitle — PROPOSED placement before draft line 187

**Disposition coverage:** BL-8.

**Status:** **PROPOSED — content is ruled, but neither D-165 nor the D-1/D-2 disposition fixes the sentence's exact Methods home.** The lead must accept or relocate this insertion before mechanical substitution.

**Frozen anchor quote (verbatim; draft line 187):**

> Passing the identical-condition null block at the corner-widened resolution bound tests the bound itself, and §6 reports that null number first.

**Proposed insertion after S03 and immediately before the anchor:** The subtitle uses *attribution-limited* only when every independent-edge component ratio in every cell is at least 2 and no required comparative shared-error ratio is below 2; a missing or excluded ratio does not select that subtitle.

**Authority:** Sentence content: D-165 R-4, D-165's binding index row, and the results-fill registry's “Protocol-first title and contingent subtitle” rule. Placement: **PROPOSED by this round; no authority supplied by the disposition.**

## S05 — Preserve the A/B/B/A build and sign convention — draft lines 55 and 57

**Disposition coverage:** BL-4.

**Frozen passage 1 (verbatim; draft line 55):**

> Figure 2 maps that bracket onto one complete measurement window. The gray horizontal arrow across the top points in the direction of session time. Blue-outlined boxes at the two ends are the pre-window and post-window calibration pulse trains; the blue bracket joining them says that the timing bound is measured on both sides of the science work and that the operative bound uses the larger capture plus a measured, never-zero allowance for change between them. The gray admission-gate box is the immediate pre-measurement check: its accompanying note names quiet state, power policy, thermal pressure, clock anchoring, and calibration freshness, and says that a failed check refuses the stage. The three small gray bars in the opening reference box, the single bar in the midpoint box, and the three bars in the closing reference box are fixed-workload reference runs used to measure drift. Between them, the two large white science-stage boxes contain small gray run bars grouped into A/B/B/A blocks—condition A, condition B, condition B, condition A. Box widths are illustrative rather than elapsed-time measurements, and the figure contains no measured data.

**Frozen passage 2 (verbatim; draft line 57):**

> The pale lower inset expands one A/B/B/A block. Its black vertical axis is measured value and its horizontal slot sequence runs from slot 1 through slot 4. A dashed sloping gray line, identified by a short gray leader, represents steady drift. Four circles lie on that line: white A circles occupy slots 1 and 4, while blue B circles occupy slots 2 and 3. The dashed blue vertical line marks the common average position in time. The two blue brackets below the circles show that the mean time of the two B runs and the mean time of the two A runs both land on that line. The right-hand notes state the consequence: steady linear drift subtracts from \((B_1+B_2-A_1-A_2)/2\), whose positive sign means B used more energy; curvature does not cancel and remains covered by the reference-derived whole-window drift allowance. Counterbalancing therefore reduces common linear drift but never replaces the measured allowance.

**Replacement for both passages:** Figure 2 orders the before-and-after pulse calibrations, entry check, reference runs, and science blocks within one measurement window. Each science block uses A/B/B/A order—condition A, condition B, condition B, condition A—and names the four measured energies \(A_1,B_1,B_2,A_2\) in that order. Its block difference is \((B_1+B_2-A_1-A_2)/2\); a positive value means condition B used more energy than condition A. Matching the average run time of the two A members to that of the two B members cancels steady linear drift, while curvature remains covered by the separately measured whole-window allowance.

**Authority:** D-1 of `05-ADJUDICATION-DISPOSITION.md` (BL-4); the frozen draft's only sign-convention sentence at line 57 and forward method definition at line 229. The aligned H39 replacement in `retensing-plan.md` uses this same ready text.

## S06 — Replace the retired fixed-p256 Holm-family member — draft line 198

**Disposition coverage:** BL-9, first survivor.

**Frozen quote (verbatim; draft line 198):**

> The primary family uses two-sided Holm correction at \(\alpha=0.05\) with \(m=2\), for the registered decode and fixed-p256 prompt-processing contrasts; this is the contrast family of Section 6, a different family from the Section 3 containment family. Order their raw \(p\)-values \(p_{(1)}\le p_{(2)}\); compare \(p_{(1)}\) with \(0.025\), then compare \(p_{(2)}\) with \(0.05\) only if the first comparison passes. If one estimate is missing, its slot remains in the denominator: the remaining finite value is still tested first against 0.025, while the missing contrast cannot reject.

**Replacement:** The primary family used two-sided Holm correction at \(\alpha=0.05\) with \(m=2\) for the registered token-generation and `[PREFILL_LENGTH]`-token prompt-processing contrasts; this was the contrast family of Section 6, distinct from the Section 3 containment family. The two raw \(p\)-values were ordered as \(p_{(1)}\le p_{(2)}\); \(p_{(1)}\) was compared with \(0.025\), and \(p_{(2)}\) was compared with \(0.05\) only if the first comparison passed. If one estimate was missing, its slot remained in the denominator: the remaining finite value was still tested first against 0.025, while the missing contrast could not reject.

**Authority:** D-166-as-amended index row; `docs/paper/results-fill-registry.md` G2-a and `[PREFILL_LENGTH]` rows; D-1 of `05-ADJUDICATION-DISPOSITION.md` (BL-9). `[PREFILL_LENGTH]` remains unresolved until the authenticated G2-a record and prompt-pin cross-check issue.

## S07 — Replace the retired 256-token survivor in the arm description — draft line 260

**Disposition coverage:** BL-9, second survivor.

**Frozen quote (verbatim; draft line 260):**

> This is not decode-only: the 256-token prefill arm prospectively overrides the earlier decode-only default.

**Replacement:** This was not a token-generation-only demonstration: its prompt-processing arm used `[PREFILL_LENGTH]` prompt tokens selected by the four-rung G2-a rule. `[PREFILL_LENGTH]` remains unresolved until the authenticated selection record and prompt-pin cross-check issue.

**Authority:** D-166-as-amended index row; `docs/paper/results-fill-registry.md` G2-a and workload bindings; D-1 of `05-ADJUDICATION-DISPOSITION.md` (BL-9).

## S08 — Rebuild the surviving conclusion criterion — draft line 356

**Disposition coverage:** R1, conclusion survivor. Existing plan blocks H28, H29, and H47 still replace their separately quoted sentences in the same paragraph.

**Frozen quote (verbatim; draft line 356):**

> Where edge placement contributes more than repeatability, phase-boundary attribution dominates the cell’s resolution bound on the named M3 Max, MLX, and *powermetrics* configuration; where it does not, the claim falls.

**A — dominance reproduced:** Because every independent-edge component ratio and every required comparative shared-error ratio was at least 2, boundary placement at least doubled every component bound on the named M3 Max, MLX, and *powermetrics* configuration.

**B — dominance not reproduced:** At least one independent-edge component ratio or required comparative shared-error ratio was below 2, so the paper identifies every failed component and makes no boundary-doubling claim for it.

**C — contrast refused:** Required comparison evidence was excluded before the ratios could be evaluated, so the paper reports neither a boundary-doubling result nor a directional model result from those records.

**Authority:** D-165 body and R-5 completion; `06-COLD-GATE-RULING.md` R-1 and R-2; D-1 of `05-ADJUDICATION-DISPOSITION.md`.

## S09 — Rename the registered campaign in Discussion — draft line 294

**Disposition coverage:** BL-10, first survivor.

**Frozen quote (verbatim; draft line 294):**

> Nothing in the frozen `_v4` campaign tests that transfer.

**Replacement:** Nothing in the frozen `_v5` campaign tested that transfer.

**Authority:** D-164 body (`_v4` was never collected; `_v5` is the registered replacement); D-1 of `05-ADJUDICATION-DISPOSITION.md` (BL-10).

## S10 — Rename both registered-campaign references in Future Work — draft line 314

**Disposition coverage:** BL-10, second and third survivors.

**Frozen quote (verbatim; draft line 314):**

> This directly tests the transport assumption that `_v4` leaves open. It is queued for the first post-campaign diagnostic window and does not enter `_v4`: that pack is frozen, and any non-configuration change requires a new family generation.

**Replacement:** This would directly test the transport assumption that `_v5` left open. It is queued for the first post-campaign diagnostic window and does not enter `_v5`: that pack is frozen, and any non-configuration change requires a new family generation.

**Authority:** D-164 body; D-1 of `05-ADJUDICATION-DISPOSITION.md` (BL-10).

## S11 — Rename the registered campaign in the Conclusion limitation — draft line 358

**Disposition coverage:** BL-10, fourth survivor.

**Frozen quote (verbatim; draft line 358):**

> More importantly, `_v4` transports a timing bound measured with commanded GPU pulses under light CPU load to sustained mixed inference without testing that load-regime assumption.

**Replacement:** More importantly, `_v5` applied a timing bound measured with commanded GPU pulses under light CPU load to sustained mixed inference without testing that load-regime assumption.

**Authority:** D-164 body; D-1 of `05-ADJUDICATION-DISPOSITION.md` (BL-10).

## Structural disposition map

| Adjudication ID | Structural row(s) | Cure |
|---|---|---|
| R1 | S01, S02, S08 | Builds \(R\), its threshold and worked pilot example; removes every surviving exceedance criterion. |
| R2 | S03 | Builds the registered shared/local replay and \(R_{cm}\), including withdrawal and absolute cancellation. |
| BL-4 | S05 | Preserves A/B/B/A expansion, symbol definitions, formula, and positive-sign meaning. |
| BL-8 | S04 | Supplies the ruled Methods sentence; exact placement remains explicitly PROPOSED. |
| BL-9 | S06, S07 | Removes both fixed-256 survivors while preserving `UNRESOLVED-UNTIL-G2A`. |
| BL-10 | S09, S10, S11, plus plan H28 | Makes the Discussion, Future Work, and consecutive Conclusion paragraphs consistently `_v5`. |
