# 10 — Cold Fable gate ruling: packet A282-AP5M-01 (AP-5M draft v2 → v3)

Judge: Claude Fable 5.1, fresh session, no loop context, 2026-09-24. Foreground only; no subagents or background tasks. Read set: the charter, `00-charge.md`, the 26 exhibits here. No other process_traces file, RUN_STATE, TASK_QUEUE, memory, council log or doctrine file was opened.

## 0. Disclosure, anchors, method

**Auto-loaded before I could refuse:** the harness injected `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md` and the memory index `MEMORY.md`. None was used for any ruling; no memory file was opened.

**Digests.** Method: `python3 scripts/validate_gate_packet.py` (receipt `coldgate-validator-receipt/v2`) plus `shasum -a 256`.

| Item | Expected | Observed | Result |
|---|---|---|---|
| Charter, run 1 (deliberate typo) | `…c95d82` | `099de884…c95d81` | REFUSE `charter_trusted_observed_mismatch`, rc=2 |
| Charter, run 2 | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | same | PASS |
| Packet `00-charge.md` | `b8a7525abac7680a4a162babd941ed3b2319f5a36c1ac7a68f5cbb208884f02c` | same | PASS |
| Exhibits | 26 manifest rows | 26 observed = expected | PASS, rc=0 |

Every charge quote relied on was re-read at its exhibit line; all matched. Arithmetic re-run in Python: Clopper–Pearson one-sided 95 % lower bound for 3 of 64 = 0.0129 (0.83 correct); the Q5 Holm example (kept: both reject; removed: neither); V2 394–399 (21.5, 11.5, 2.5, 5, 25 J); the record-18 counterexample (lever 0, bias 10δ).

**Packet hygiene.** Complete and neutral for Q1–Q18. Two NITs, neither changing a verdict: (H1) SIR 565 is quoted as live but sits in a passage marked "SUPERSEDED (2026-07-13, WO-032/D-047)" (SIR 562–566); the rule is restated live in the D-047 "Corrected gate inputs" section (SIR ≈594), which v3 cites instead. (H2) B16 7 is a seat's summary of rulings, a narrative source; not relied on.

**Precedence applied.** Ed-ratified decisions (DL) and contracts (DF, AP) outrank cold-gate rulings on code lanes (G21, G45, G45A), which outrank consults (R20, R08), which outrank design packets (C, S19). Where they collide, the higher controls and the collision is named.

## 1. Rulings Q1–Q18

Verdicts: AFFIRM (a stated pick), TEXT (I write different text), NEW RULE (no source; text supplied for Ed's adoption), ED (reserved). Severity is of the v2 defect. Texts T-n appear once, in §3.

**Q1 — Guard. AFFIRM (a): observed count ≥ 3, expressly amending AP-5's wording for AP-5M. BLOCKER → T-1, T-2.** AP 274 says "binomial lower-bound" and AP 258–278 define no bound or confidence. SIR 464 calls the guard "a deterministic property of the item set", which only an observed count is; C 130–133 says "an observed count"; R20 15 `sparse(g) = min(Σc8[g], Σc17[g]) < 3` was adopted by G21 (§Q1 AMEND D2) and G45 52 AFFIRMED `min_correct 3` as a constant asserted equal to the AP-5M text. Under (b) that constant is void: a 95 % lower bound on 3/64 is 0.83, so the ruled pseudocode never runs as written. The v2 revision ruling ("restore binomial-lower-bound as operative") is overruled by the later gate rulings; I disagree with the lead's v2 disposition. Amending AP-5's words is claim policy: Ed adopts under E2.

**Q2 — Smoke gate. TEXT ((b)+(c)). BLOCKER → T-3.** AP 270 requires a passing gate. SIR E1–E4 are level-invariance tests for a ladder whose prompts differ by one digit (SIR 572); for MATH, E2–E4 fail by construction (C 24, 11–12) and cannot be pass predicates. E1 survives in MATH form: legal stops are end-of-sequence or cap, with `capped := generated_tokens ≥ cap` agreeing with `stop_reason` (G21R R9, 15). Two further predicates follow from ruled machinery: strict-valid bundles (AP 270) and the registered worst-case timing bound, whose breach is a physics refusal (G21 80; R20 71). Missed by charge and v2: `cap_bound_fraction 0.20` is a ruled constant (G45 52); the gate reports cap-hit fraction against it. SIR requires a decision-log entry for threshold changes: the D-166 addendum carries T-3. Ed adopts.

**Q3 — Floor and anchor. TEXT: (a)(ii) anchor only in the widening, floor as a separate per-window gate; (b) block-window `floor_gate_j` from the P2-015 manifest, `floor_j` deleted from the estimator; (c) 1 J relabelled. BLOCKER → T-4, T-5, T-6.** D-078 clause 11, Ed-ratified (DL 4802–4813): the floor gate contains the anchor term, the decision interval separately consumes the anchor bound, "these are different objects". DF 160–170: acceptance is two separate checks, `|estimate| > F` and zero-exclusion by the widened interval; the sum "is only a prospective planning/sizing diagnostic", `"not_an_acceptance_gate": true` (DF 155). DF 75–84: an attribution-limited floor is itself sourced from `E_clock_anchor_shift_bound_j`, so reading (i) puts the anchor into the interval twice. G21 D5a (68) ruled the share-scaled form on a code lane without citing the discipline and cannot amend an Ed-ratified decision; its structure (`k`, `s`, point bounds `s = 1`) stands and its bracket becomes `anchor_j`. The departure is stated for the record; Ed adopts. (b) No block-window artifact exists (V2 120; AP 272 "pending-P2-015 … for level windows"); DF 66–74 defines the manifest row. (c) ≈1 J is the per-phase anchor envelope (DL 4761–4764; RQB 1603); operative phase floors are 3.823787 J prefill and 7.377086 J decode gate after D-084 (DL 5026–5035).

**Q4 — Endpoints, resampling. (a) AFFIRM percentile-only; point bounds reported beside. (b) AFFIRM K10's two-stage draw as registration text. (c) TEXT: AP-5M names RNG and quantile rule; seed value stays in registration. MATERIAL → T-7.** C 112–113 is the only endpoint rule; each replicate already carries the anchor widening, so folding s = 1 bounds into the ends re-applies one term with no source. M9 (S19 19) requires a block-aware draw; D5a's `k` and `s` (G21 68; R20 69) presuppose parents-then-problems.

**Q5 — Holm membership. TEXT (b): flag-forced NR levels leave the sort; m = 5. MATERIAL → T-8.** R20 19–21 runs `holm` "over tested groups"; a level whose status is fixed by a flag is not under test. Keeping it can only loosen thresholds for the rest (0.012 and 0.014 reject behind a flagged 0.002; neither rejects without it), the anti-conservative direction. NE groups are the ruled analogue (C 85).

**Q6 — Spread in merged groups; recapture bound. (a) TEXT: whole group NR. (b) NEW RULE: one recapture per (arm, level), separate from S8. MATERIAL → T-9.** The group is the unit of test; constituents have no R (G21 Split 1, 19); dropping the flagged cell's windows would let an energy-side event alter a count-only partition. G21R R6's bound (12) covers the ceiling item only; G45 71 and G45A 44, 58 say "until a registered recapture" with no count.

**Q7 — Drift threshold. (a) TEXT: δ_upper from the shakedown night. (b) NEW RULE: `budget_j = 0.01 × min(projected cell energy)`. (c) AFFIRM `blocks_per_cell` = P = parents per cell per model. (d) TEXT: NE first, then NR listing all flags. MATERIAL → T-10, T-11.** G21C 22 and R20 70 say "from the pilot"; the bench pilot measures no energy (G21R 17; S19 14), so the shakedown is the only measured-energy step. G21 70 requires the budget "with its derivation"; none exists. 1 % of the smaller cell moves R by about 1 % against ×/÷ 1.59 (S19 30). G45A (P) fixes only NE over `spread_exceeded`.

**Q8 — Drift model. TEXT (a)+(b). MATERIAL → T-12.** Record 18's counterexample holds (f = δ|x − 5|, 8B at 0 and 10, 1.7B at 5 and 5: lever 0, bias 10δ). V2 170–173 holds only for drift linear in index with one shared slope, which G21 80 and R08 8 also assume; V1 95 said "linear" and v2 dropped it.

**Q9 — Retry tails across nights. TEXT: fresh envelopes extend the same night to its registered maximum; leftovers are `night_exhausted`, cured only by the K22 recapture; indices and the lever are per night, level lever = max over nights. MATERIAL → T-13.** M12 (S19 22) says "within the night"; G45A (N) 48 and (E) 50 place retries "at an index above the reporting envelope's", one index space. A recapture night runs both models adjacent (G21R 12), so it balances itself; a continuous index would count the gap between nights as drift.

**Q10 — Which attempt counts. TEXT (a). MATERIAL → T-14.** G45A (S) 52: each item in exactly one non-superseded block; G21R R9 15: windows keyed by (block_id, attempt), voided excluded. Energy and outcome must come from the same execution.

**Q11 — Failed check in the S8 recapture. TEXT (a): terminal for the arm, flag `s_per_token_upper_falsified`. MATERIAL → T-15.** R20 71: the output "flags that the registered `s_per_token_upper` was false for that arm"; G21R R6 (ii): a falsified registered bound is a physics/evidence refusal. Repeating (b) cannot repair a false bound; (c) lets a falsified input pass.

**Q12 — 10 % trigger. AFFIRM omission. NIT → T-16.** R08 15 left it open after rejecting paired retry on cost. Its hazard is covered: the lever is recomputed after every requeue (G21 70; R20 70) and excess is NR(`drift_exceeded`) pending balanced recapture (G21R 17).

**Q13 — Reason for withholding L\*. TEXT: refuter's (i) and (ii) operative; gate-21 sentence historical. MATERIAL → T-17.** G21's own table lets NE gaps license L\* (`11e88` → 4, line 49; `eee18` → 5, line 56), contradicting "a gap there is the selection M12 forbids" (23). The verdict stands; only the recorded rationale changes.

**Q14 — Claim sentence. AFFIRM V2 869–881 plus NE reason codes. NIT → T-18.** Satisfies G21 (a) 27, G21R R4 10 and G21 Split 1 19; R18 N27 and my re-derivation find the three examples consistent.

**Q15 — Idle reference. AFFIRM (a) report-only. NIT → T-19.** M7 (S19 17) and R08 7 permit a covariate use and define none; D-045.7 keeps energies gross.

**Q16 — Registration numbers; budget unit. (a) AFFIRM leaving envelope length, cap ladder, budget value and seed to the registration packet, which AP-5M names and requires hashed before any test problem. (b) TEXT: unit is "windows", "night" glossed once. NIT → T-20.** S19 30, H18 119–120 say windows; G21C 7 and PB 7 (600 s / 480 s) are planning figures.

**Q17 — Draw and eligibility. (a) AFFIRM: adopt V2 483–489 verbatim, "proposed" removed. (b) TEXT. MATERIAL → T-21.** Importer verified: `_GROUPED` (IMP 103) runs after `\!`, `\,` removal (117) and `{,}` → `,` (127); `plain_comma_ambiguous` (192–196) rejects any comma left after removing `\,`, `,\!`, `{,}`; `eligible_records` excludes on it (215). So `1{,}000`, `1,\!000`, `1\,000` qualify and `1,000` is excluded.

**Q18 — Five added fields. AFFIRM keep, AP-5 order, "(added)" marks. NIT.** No prohibition (AP 258–278; R17 124).

## 2. Findings the charge missed

- **MATERIAL (Q2):** `cap_bound_fraction 0.20` (G45 52) absent from v2's smoke text; in T-3.
- **MATERIAL (Q3):** V2 step 7 (246) uses `floor_j` without the O-12 flag (R18 G1); T-5 removes `floor_j`.
- **NIT (H1):** cite SIR's D-047 correction, not line 565.
- **Appendix A F7 promoted → T-22:** M40 C2 (49) strips one trailing percent on both sides without rescaling and discloses (`\frac12\%`, `\frac12`) as accepted; "as an exact rational number" (V2 73) overstates.
- **Appendix A F5 → T-23:** AG 336 computes `power_w × overlap duration`, not "per-record energy counters falling in it" (V2 86).
- Appendix A otherwise stands. O-1 to O-16 close with these texts (v3 §6 marks each "closed by ruling 30/10"); O-17–O-20 (Ed's E1–E4) stay open.


## 3. Final texts (paste verbatim into v3)

Each entry names its target; install as written.

**T-1 — replaces V2 §2.1 lines 202–205.**
- **Denominator guard, sparse, merge, group, pooled.** The *denominator guard* is an observed count: a model passes at a level (or merged group) when at least 3 of its attempts there are correct. A level is *sparse* in an arm when either model fails the guard there (K9). A sparse level is *merged* with a neighbour in a fixed order (§2.4), decided on correct counts only. The result is a set of *groups*: single levels or merged runs such as "4–5". A merged group is tested as one hypothesis; its constituent levels are *pooled* and each carries `pooled_in` (the group's levels). AP-5M expressly replaces AP-5's phrase "binomial lower-bound must be >=3 correct per level" with this observed count for this plan; the substitution is part of what Ed adopts under E2.

**T-2 — row field "Denominator provenance requirement" (V2 §2.8); delete "pending O-2" at V2 309 and "(O-2)" at V2 803.**
Exact scorer output plus emitted-token and stop-reason audit. Observed count of correct attempts ≥ 3 per model per level; a level where either model has fewer than 3 merges in the fixed order of §2.4, else the group is `not estimable (sparse_after_merges)`. This is an observed count (a fixed property of the frozen problem set), not a confidence bound; for AP-5M it replaces AP-5's "binomial lower-bound" wording.

**T-3 — replaces V2 K21 (745–753); the row's "Inclusion/exclusion" field points to K21; the D-166 addendum carries this clause as the decision-log entry changing the smoke thresholds.**
**K21 — pre-campaign smoke gate.** AP-5 requires an envelope-validation smoke gate that passes before any scored campaign (`analysis_plans.md:270`). AP-5's defined checks were written for a ladder whose prompts differ by one digit; for MATH, emitted-token mean and distribution and prompt-token count change with level by design, so those checks are not pass conditions here. The AP-5M smoke gate is the shakedown night (M4) and PASSES only when all of the following hold on every envelope of that night: (G1) every bundle is strict-valid; (G2) every attempt's `stop_reason` is either the end-of-sequence token or the cap, `capped := generated_tokens ≥ cap_tokens[arm]` agrees with `stop_reason` on every row, and no other stop reason (error, timeout, malformed) occurs; (G3) every block's markers lie inside its envelope's usable interior and no block's elapsed seconds exceed its registered worst case (`cap_tokens × s_per_token_upper + prefill_s`). Reported per (model, arm, level) with no pass threshold: emitted-token mean and distribution, prompt-token count, cap-hit fraction beside the registered `cap_bound_fraction` (0.20), and the early-stop-bias descriptor (mean emitted tokens of incorrect minus correct attempts; AP-5's E5). A failed gate records `smoke_failed([reasons])`; no scored campaign starts; the cause is cured and recorded and the shakedown repeated; no registered value beyond those the pilot may set (K2) changes on its account. A G3 failure also falsifies `s_per_token_upper` for that arm; the registration is re-derived before any repeat.

**T-4 — replaces V2 §2.1 lines 108–120 from "(i) The *floor*" to "(O-12)."**
(i) The *floor*: the smallest energy difference the instrument can distinguish from zero for a given window class, published as `floor_gate_j = max(floor_abs_j, floor_cmp_j)` by the calibration manifest (`docs/phase_2/detection_floor.md`, "Floor Artifact Semantics"): `floor_abs_j` is the larger of the largest absolute residual and the prediction bound `t_0.975 · s_r · √(1 + 1/n)` over repeated identical cells; `floor_cmp_j` is the same construction over same-condition A-B-B-A contrast deltas. Floors are calibrated per *window class* (request, phase, level, block …). AP-5M's window class is the block window; its floor row does not yet exist and is a registration prerequisite (row, Floor gate). The published per-phase figures are historical planning context only: an anchor envelope of about 0.7–1.0 J per phase boundary (D-078 clause 11) and operative phase floors of 3.823787 J prefill and 7.377086 J decode gate (D-079 as amended by D-084). No block-window value may be inferred from them. (ii) The *anchor bound* `anchor_j` (`E_clock_anchor_shift_bound_j`): the most energy that can be assigned to the wrong window because the marker clock and the sampler's clock may be offset; it is the only instrument term inside the interval. Under D-078 clause 11 the floor and the anchor bound play separate roles and neither may be dropped as a double count: the floor gates each block window; the anchor bound widens the interval.

**T-5 — procedure (V2 §2.2): step 2 last two sentences; steps 7 and 8 bound expressions; K11 and the §2.5 worked replicate change the same way.**
Step 2: "Refuse any block window at or below `floor_gate_j` for the block-window class (row, Floor gate); the refusal is `below_floor` and the window is not counted." Step 7: "point bounds with U = Σ k·anchor_j per model (K11)". Step 8: "add bound u = k·anchor_j·s". K11: "u = k·anchor_j·s, with k the block's counted windows for that model and s its drawn-token share; point bounds use s = 1. This departs from gate 21 D5a's bracket `(floor_j + anchor_j)` because D-078 clause 11 and `detection_floor.md` assign the floor to a separate gate; D5a's per-replicate share-scaled structure is kept."

**T-6 — row field "Floor gate".**
Every counted block window must exceed `floor_gate_j = max(floor_abs_j, floor_cmp_j)` from the P2-015 calibration manifest row for this backend, gross energy, the block-window class and the scored-campaign condition family, issued and hashed before registration seals; a block window at or below it is refused (`below_floor`) and never counted. The floor never enters the interval; the anchor bound never gates a window.

**T-7 — replaces V2 191–192 and step 11; K10 589–593 stand with "proposed text pending O-4" removed; replaces V2 594–595.**
"The *interval* runs from the 2.5th percentile of the replicate low-side ratios to the 97.5th percentile of the replicate high-side ratios (K11); its ends are `lo` and `hi`. The point bounds (s = 1) are reported beside it as `point_low` and `point_high` and do not alter `lo` or `hi`." Lines 594–595: "Replicates use Python's `random.Random(seed)` with the seed fixed in the registration packet; percentiles are linear interpolation between order statistics. Both are registered so the interval can be rebuilt exactly."

**T-8 — replaces V2 step 10 (252–256).**
10. **Holm**, m = 5 fixed, over the tested groups. A group is *tested* when it is estimable and no constituent level was forced NR before testing by `spread_exceeded` or `drift_exceeded`. NE groups and flag-forced NR groups are not tested: their p-values are computed and reported but excluded from the sort, and m stays 5. (A flag-forced level cannot change status whatever its p-value; leaving it in the sort could only loosen the thresholds for the others.)

**T-9 — replaces V2 223–224; the second part is new clause K22, flagged at step 4.**
- **spread_exceeded, drift_exceeded.** Flags that a cell lost its minimum spread after capture, or that a level's executed drift lever exceeded `max_gap`. Either flag on any constituent makes the whole group NR with that reason and `flagged_levels` listing the constituents; the group's numbers are still printed. **K22 — flag recapture bound.** For each (arm, level) at most one registered recapture may cure `spread_exceeded`, `drift_exceeded`, `unattributed_overrun` or `night_exhausted`, all causes together: on a later census-clean window, both models' missing or displaced parents are re-run with the same problems, packed to equal mean position within that window. If the level still carries any of these flags afterwards, it is NR terminal under this registration. This bound is separate from S8's one recapture of a ceiling-violating problem.

**T-10 — replaces the drift-threshold sentences of V2 167–174 (with T-12) and the O-7 item; K12 carries the same sentences.**
The *drift threshold* is `max_gap = budget_j / (δ_upper · P)`, with P the number of parent blocks per cell per model (the registered n ÷ problems per block). `δ_upper` (joules per block per slot) is registered from the shakedown night: each model runs one fixed block of pilot problems twice, in its first and last envelopes of that night, and δ_upper is the larger model's |E_last − E_first| ÷ (slot separation); a shakedown lacking either pair refuses registration. `budget_j` is registered as 0.01 × the smaller of the two models' projected cell energies (shakedown seconds per token × pilot token totals × mean shakedown power), so the admitted bias moves R_L by at most about one percent. Both numbers and `max_gap` are hashed in the registration packet before any test problem runs.

**T-11 — replaces V2 step 12 (259–260); K16 carries the same rule.**
12. **Group status** by the three-way test (S2); then flags, in this precedence: NE(`ceiling_violation`) first; otherwise NR listing every applicable reason in the order `spread_exceeded`, `drift_exceeded`; every applicable flag is recorded true whatever the printed status.

**T-12 — replaces V2 170–174 from "If a block's energy shifts".**
The registered drift model is: gross block energy drifts linearly in envelope index with one slope, of magnitude at most δ_upper joules per block per slot, shared by both models. Under that model a level's between-model bias is at most δ_upper × P × lever, and lever 0 cancels the drift exactly. For any other drift shape this rule bounds nothing; it is the registered tolerance, not a proof. `max_gap` is defined in K12; the packer aims for lever 0 and a roster is accepted if lever ≤ `max_gap`.

**T-13 — insert after V2 line 103 (Night) and as clause K23, flagged at step 5.**
Retries and reschedules extend the same night: a "fresh envelope" is appended to that night's schedule up to its registered maximum envelope count. Any block unfinished when the night ends is the terminal refusal `night_exhausted`; its cell is unresolved until the K22 recapture. Envelope indices start at 0 in every night. A level's drift lever is computed within each night over that night's counted windows, and the level's lever is the largest of its nights' levers.

**T-14 — insert after V2 line 153.**
- **Counted attempt.** For every problem and model exactly one attempt is *counted*: the one whose window is counted. Its correct flag and generated tokens are the problem's values in every computation. Every superseded attempt's answer and tokens are recorded and never used. When a superseded and a counted attempt of one problem disagree in correctness, `attempt_divergence` is recorded for disclosure (expected never under greedy decoding, possible under seeded sampling).

**T-15 — replaces V2 894–895.**
If during the S8 recapture any of the night's other blocks for that arm exceeds `s_per_token_upper`, the registered bound is falsified for the arm: `crossover_level` stays null with reason `ceiling_violation_unresolved`, terminal under this registration; the arm's results still print with `s_per_token_upper_falsified: true`; a further recapture requires a new registration.

**T-16 — replaces V2 O-8 (1143–1145).**
- **O-8 (retry trigger): closed.** The 10 %-retried trigger is not adopted. Its hazard, position imbalance after retries, is covered by K12: the executed roster's lever is recomputed after every requeue and an excess is NR(`drift_exceeded`) pending the K22 recapture.

**T-17 — replaces V2 line 887.**
*Source: 21/10 §Q1, Split 3 cure text. VERBATIM.* AP-5M records two reasons for withholding L\*: (i) the censored outcome leaves the count-only merge partition undetermined; (ii) the violation falsifies the registered bound `s_per_token_upper`, a physics/evidence refusal (21/11 R6). The gate-21 sentence "a gap there is the selection M12 forbids" is preserved as the historical statement; it is not the operative reason, because the ruled table lets count-based NE gaps license L\*.

**T-18 — V2 869–881: delete "PROPOSED … (this seat's drafting, for the gate; O-3)"; in the rules sentence replace "NE levels under 'not estimable'" with:**
NE levels under "not estimable" followed by the reason code in parentheses, e.g. "Level 3 not estimable (sparse_after_merges)".

**T-19 — row field "Order/blocking/covariates", last sentence; and V2 530–531.**
The idle reference (idle-slot energy per envelope, per model) is recorded and reported beside results per window; no computation in this plan adjusts any energy or R_L by it, and any exploratory use is labelled exploratory.

**T-20 — V2 502–504 and 1177–1179; same unit wherever the mechanical n rule is explained.**
The "registered window budget" is a number of capture windows (a *window* is what this file calls a night); the value is fixed in the registration packet (O-14). O-18: "planning figures (record 18) are about 12 windows for n = 64 and about 23 for n = 128, at 4–5 windows a day."

**T-21 — replaces V2 477–480 from "parses as".**
parses as an integer, a decimal, a grouped integer (thousands separated only by the TeX forms `{,}`, `,\!` or the thin space `\,`, which the importer removes before parsing), a/b, or `\frac{a}{b}`: `5`, `-\frac{3}{4}`, `0.25`, `10\%` and `1{,}000` qualify; `\sqrt{2}`, `3\pi` and `(1,2)` do not. A reference containing a bare comma, such as `1,000`, is a *plain-comma* reference and is excluded, because a bare comma could separate thousands or list two answers.

**T-22 — V2 72–74, replace "compares it with the reference as an exact rational number".**
canonicalises both the boxed answer and the reference (removing TeX spacing, dollar signs, one trailing percent or degree sign without rescaling, a unit word and a leading "x =") and compares the results as exact rational numbers; so `44\%` matches `44`, and the disclosed accepted pair (`\frac12\%`, `\frac12`) is caught only by the per-cell audit, not by the scorer.

**T-23 — V2 line 86, replace the last sentence.**
Energy in a time interval is the sum, over sampler records, of each record's power times the duration of its overlap with the interval.

END OF RULING. Severity: BLOCKER Q1, Q2, Q3 (cured by text); MATERIAL Q4–Q11, Q13, Q17 and the two §2 items; NIT Q12, Q14–Q16, Q18, H1, H2. Ed decides E1–E4 and adopts AP-5M; every NEW RULE above is text for that adoption, not policy.
