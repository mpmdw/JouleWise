# JCORRECT-FLOOR-01: Opus 5.5 seat answer (blind)

**Reading the evidence.** Every number I computed is a desk figure, not a measurement. The simulation script is `/tmp/152c9255/jc-opus/sim.py` and its sensitivity run is `sim_s03.py`, with outputs `out.txt` and `out_s03.txt`. Both are scratch files; I committed nothing. Any number marked **(assumed)** has no repo measurement behind it. The only real null energies I found are the July P2-015 records in `docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json`. They come from Qwen2.5-1.5B on an older epoch and are **NON-CLAIM**. I use them only to set the scale of the noise.

## Framing correction (read first)

The question's worked example puts the "±1 correct answer" noise in the wrong place. AP-5M v5 never counts correct answers inside a quiet block:

- **Where correctness comes from.** Correctness `p` comes from accuracy runs outside quiet windows, with n ≥ 128 problems per level (`52-ap5m-v5-draft/01-ap5m-draft-v5.md:10` R-Q3(4)).
- **Where energy comes from.** Energy `e` is J/attempt on a quiet subsample. Each quiet trace must byte-match its accuracy-run trace (`:10` R-Q3(5), `:47`, `:49`). The estimand is `C = e/p` (`:57`).
- **Consequence.** In a same-seed null block the correct count is fixed by construction. The randomness in correctness is a *sampling* property of the 128 accuracy problems. It is not an instrument property. It belongs in the claim's standard error, not in the floor.

**The real problem is a gap in the claim side (BLOCKER).** CG-1 builds the standard error only from scatter between envelopes (`91-claimgate-final-texts-v2.md:3`: "Feed the k envelope observations … df = k−1"). The accuracy term, and the subsample term, are identical in every envelope, so that scatter never sees them.

- **The sampling error is large.** In my simulation the accuracy part of the level contrast has SD **0.114** in natural-log units (assumed p values, n = 128).
- **Result with CG-1 as written.** With the energy-only floor and an envelope-only standard error, the gate admits a false direction in **38.5 % of levels and 90.8 % of five-level families at true effect 0** (`out.txt`).
- **This holds under both (a) and (c).** The fix is a claim-side term, specified in J1.

## J1: Choose (c), a dimensionless log-scale estimand with a matched, derived floor

**Why (c) and not (a).**
1. **The binding text already uses a ratio.** R-Q3(7) makes the confirmatory hypothesis "the sign of log R_L" (`01-ap5m-draft-v5.md:10`, `:65`). That quantity has no units. An additive J/correct primary under (a) contradicts the binding text or needs a second, unit-mapped estimand. The draft itself leaves that mapping OPEN (`:67`).
2. **(a)'s null measures an estimand AP-5M does not use.** A null block's "J/correct" would be block joules divided by the block's own correct count. The registered estimator divides by the accuracy from the 128-problem run (`:57`). Under the pinned seed, (a)'s null correct counts are identical in both slots. So (a) reduces numerically to "J null ÷ a constant", which is the division WR-9 forbids (`06-…/21-coldgate-fable-cgw-addendum-ruling.md:81`).
3. **One J floor cannot serve every cell.** Block energy varies across (model, level, budget) by roughly 100× **(assumed)**: from about 30 J/attempt for 1.7B with thinking off to about 1 kJ/attempt for 8B at a 2k budget. The July nulls show absolute scatter growing roughly like √E:
   - 0.022 J SD at 0.25 J (8.8 %);
   - 0.22 J SD at 24 J (0.9 %);
   - 0.70 J SD at 193 J (0.36 %).

   (`extraction-verified.json`, DF-RQ short/mid rows and DF-SU level row.) A floor in joules taken at one scale is too small at larger blocks and too large at smaller ones. A log-scale floor transfers far better.
4. **I do not argue for (b).** J/attempt is not the question, and the log floor below is built from joule measurements anyway.

**Derivation rule (replicable).**

- **Estimand per level L.**
  Δ_L = [ln C_8B,L,b_hi − ln C_8B,L,b_lo] − [ln C_1.7B,L,b_hi − ln C_1.7B,L,b_lo], with C = e/p.
  Because ln C = ln e − ln p, the instrument touches only the four ln e terms.
- **Claim observation per claim envelope j of model m.**
  y_m(j) = ln value_b(j) − ln value_a(j).
  Here value_a and value_b are CG-1's envelope means of block-level gross J/attempt (A slot = b_lo, B slot = b_hi). The energy part of the estimate is Δ̂_L^E = mean_j y_8B − mean_j y_1.7B. The full estimate is Δ̂_L = Δ̂_L^E − Â_L, where Â_L = ln(p̂_8hi/p̂_8lo) − ln(p̂_1.7hi/p̂_1.7lo).
- **Null envelope (the matched rule).** The registered claim envelope schedule for model m, with every B-slot item replaced by its A-slot item:
  - same problem IDs, the pinned seed, the b_lo configuration;
  - the level whose pilot-measured J/attempt is lowest for that model (the smallest energy gives the largest relative scatter, so this errs large);
  - n_reg = 10 blocks, envelopes retaining fewer than n_reg are excluded and listed (CG-1);
  - every member trace byte-matches its accuracy-run trace, and mismatches count against the registered ceiling.

  If A291 v5 does not pair budgets inside one envelope, the null still applies "the claim's observation function to an envelope whose B configuration equals its A configuration".
- **Null observation.** x_m(i) = ln value_b(i) − ln value_a(i), computed on null envelope i of model m.
- **Pairing across models.** ν(i) = x_8B(i) − x_1.7B(i). The i-th retained 8B null envelope is paired with the i-th retained 1.7B one, in start-time order; the two models' null windows alternate. k_cal = min(retained per model) ≥ 5. Surplus envelopes are the latest ones; they are excluded and listed.
- **Floor.** F_Δ = g(k_cal)·(|mean ν| + t_{0.975,k_cal−1}·s_ν/√k_cal). This is CG-1's formula verbatim, applied to the estimand's own null.
  - g is `small_sample_guard_factor` (`joulewise/detection_floor.py:846-855`, `GUARD_REFERENCE_N = 10` at `:121`).
  - At k_cal = 5: g = 1.5 and t = 2.776.
  - Unit: `ln_ratio`. No division of joules by a correct count occurs anywhere.
- **Worked example (assumed values).**
  - x_8B = (+.004, −.003, +.006, +.001, −.002)
  - x_1.7B = (+.002, +.005, −.004, +.003, .000)
  - ν = (.002, −.008, .010, −.002, −.002); mean 0.0000; s_ν 0.00663
  - F_Δ = 1.5·(0 + 2.776·0.00663/√5) = **0.0124**, meaning a 1.2 % change in the ratio of J/correct ratios.
- **How correctness randomness enters: on the claim side only.**
  SE_Δ² = s_y8²/k_8 + s_y1.7²/k_1.7 + V_shared.
  - V_shared is the registered paired-bootstrap variance of Â_L. It resamples level-L problem IDs jointly across all four cells, which share the same problems (R-Q3(1)). Add the subsample term for ln e, using accuracy-run token counts only as a variance proxy, never as the headline.
  - V_shared enters once and is not divided by k. Use df = 2(k−1) until the tested v5 estimator (`:61`) fixes it.
  - The clock-anchor bound on the log scale is B_Δ = Σ over the four cells of B_c/ē_c (first-order, worst case).
- **Power at planned k = 5, with the corrected standard error** (`out.txt`, `out_s03.txt`, assumed p and scatter):
  - Floor size: F_Δ median 0.022 at 0.7 % envelope scatter, and 0.095 at 3 %. The floor does **not bind**, because Holm × SE_Δ ≈ 3 × 0.12.
  - False admission: 0.1 %/level, 0.3 %/family.
  - Power at Δ = 0.20: 4 %/level. At Δ = 0.30: 22 %/level (19 % at 3 % scatter).
  - Raising n_acc to 200 (the maximum R-Q3(4) allows): 10 % and 46 %/level.
  - **Power is limited by the number of accuracy problems, not by k or the floor.** Adding quiet windows buys almost nothing.
  - For contrast, (a) with seeds varied in the null gives a median floor of **0.59**. That hides effects below about 80 % and reaches only 5 %/level power at Δ = 0.30.
  - The 19-desk-simulations evidence tests the v1 gate (`19-desk-simulations/README.md`, "Claim admission" table). It does not apply to F_est, so I ran my own simulation.
- **Direction of error.**
  - Using b_lo and the lowest-energy level errs large (conservative) if noise is additive or grows like √E.
  - It errs small if bias grows faster than energy (thermal carry-over at b_hi); see J5.
  - Keeping correctness out of the floor errs neither way **only if** V_shared is installed. Without it the gate errs catastrophically small.

**Executable text J1.** *AP-5M v5 registers Δ_L (natural-log ratio of the two models' b_hi/b_lo J/correct ratios) as the primary estimand of each level's hypothesis, unit `ln_ratio`, under CG-4(f)'s dimensionless branch. Its floor is F_Δ = g(k_cal)·(|mean ν| + t_{0.975,k_cal−1}·s_ν/√k_cal), where ν(i) = x_8B(i) − x_1.7B(i) and x_m(i) is the claim observation function applied to null envelope i of model m. Each null envelope is the registered claim envelope with every B-slot item replaced by its A-slot item: b_lo, the level with the lowest pilot J/attempt, pinned seed, n_reg = 10, byte-matched. Pairing is in start-time order; k_cal = min(retained per model) ≥ 5; surplus envelopes, the latest ones, are excluded and listed. The F_est unit enum gains `ln_ratio`, and the mint computes F_Δ from authenticated block joules without any correct count. **BLOCKER to freeze:** the claim standard error adds V_shared (registered paired problem bootstrap of the accuracy and subsample terms), once and undivided by k, and B enters as Σ B_c/ē_c. `estimators.py`'s refusal of non-`independent_run` terms (`cgw ruling:25`) gains a registered `shared_all_envelopes` scope for exactly this term. CG-4(e)'s simulation is re-run with V_shared before any claim. O-21 is applied as |Δ̂_L| > F_Δ, and Ed is told this in the CG-4(g) notice.*

## J2: Seeds and correctness noise

"Same model, same seed" **is** the correct null. The zero variance in correctness is right, not an understatement. The floor bounds what the *instrument* does when nothing differs. The scorer is deterministic, and byte-matched traces give identical answers, so the instrument produces no difference in correctness.

Varying seeds in the null would do three wrong things:
1. It would put real differences in the traces (different tokens, so different joules), so the null would no longer be "nothing differs".
2. It would measure correctness noise at the scale of a 10-problem block, while the estimand's p comes from 128 or more problems. That is the wrong size by about √12.8 ≈ 3.6×.
3. It would move sampling variance into a bias bound. That is the 0.59 floor above.

For a stochastic, scored workload, a null means: **identical inputs, seed and trace in both slots, so any measured difference comes from the instrument and run-to-run physics.** Sampling uncertainty (which problems were drawn) belongs in V_shared. Variation across seeds is outside the estimand's scope, because R-Q3(2) pins one seed. The claim wording must say "at the pinned seed". Any seed sensitivity analysis is descriptive only.

**Executable text J2.** *Null blocks use the pinned seed and the accuracy-run traces. Each null member's trace must byte-match its accuracy-run trace, and its correct count must equal the accuracy-run count. A mismatch is counted against the registered ceiling, and the block is excluded symmetrically. Claim text carries "at the registered sampling seed". Seed variation enters no floor and no confirmatory standard error.*

## J3: Whose calibration serves a cross-model contrast

**Both models.** The floor is the difference of the two models' nulls. Δ_L is a difference of two within-model contrasts, so any slot bias enters as β_8B − β_1.7B.

- **Why one model's null cannot stand in for the other.** The two models load the machine differently: 0.94 GB versus 4.3 GB of weights, 112 versus 144 KiB of KV cache per token (`13-…/20-coldgate-fable-council-ruling.md:16`). Their power draw, heat, and therefore thermal and frequency-state carry-over differ.
- **"Larger of the two" errs small** whenever the biases have opposite signs: |β_8B − β_1.7B| can reach |β_8B| + |β_1.7B|.
- **"Pooled" estimates (β_8B + β_1.7B)/2**, which is the wrong quantity.
- **"Calibrate 1.7B only"** would rely on the √E rule for the scatter. But the bias term most likely grows with power, so the shortcut fails in the direction that matters. I rejected it.

**Executable text J3.** *For a contrast whose conditions bind different model artifacts, the WR-3 field `calibration_model_artifact_sha256` becomes the sorted pair `calibration_model_artifact_sha256s`. It must equal `condition_model_artifact_sha256s` as a set, else `estimate_floor_model_mismatch`. The floor artifact carries both models' null envelope ids and the ν pairing. `floor_est_model_rule_unruled` is retired for contrasts that satisfy this rule and stays for any other cross-model shape.*

## J4: Scheduling

**Order:**
1. 25G83 acceptance: W1 and W2 at least 6 h apart, W3 only if the count falls short (`05-…/21-coldgate-fable-acc2-addendum-ruling.md:71` R5(b)). Then derivation, cold gate, issuance, G2-a, and the COUNCIL-407-01 calibration night (`:81` R15; `13-…:18`, `:54`).
2. The MATH pilot and its quiet shakedown. This fixes b_lo, the block shape, and the lowest-energy level.
3. The accuracy runs, outside quiet windows. These supply the reference traces and V_shared.
4. **10 null quiet windows** (5 per model, alternating models). Under WR-0, one window equals one envelope (`cgw:63`).
5. Mint, pin PR, freeze.
6. Claim windows: at least 5 per model, so at least 10.

The COUNCIL-407 calibration night cannot double as the null. Its envelopes are context-position rungs, not same-configuration ABBA blocks on MATH (`13-…:18`). The floor windows already planned in WR-10 are workload-mismatched for this estimand (`cgw:83`).

**Added cost.** My choice adds **10 quiet windows** before the first claim-bearing number, about 2–3 days at 4–5 windows per day. Choosing (a) would cost the same 10. The window count is driven by J3 (two models), not by (a) versus (c). If A291 v5 lets one quiet night hold several envelopes, as the calibration night's twelve 600 s envelopes do, the 10 could compress into 1–2 nights. That depends on A291 v5, not on this ruling.

**Executable text J4.** *Null windows run after the pilot and the accuracy runs and before freeze. They alternate models, starting with the model chosen by the registration seed, with 5 retained per model. No claim window is armed before the pin PR. The null window ids are disjoint from the claim window ids (WR-2(v)).*

## J5: What would show this choice wrong, and which step detects it

1. **Bias that grows faster than energy at b_hi**, such as thermal carry-over that exists only when the arms differ. A same-configuration null is blind to this by construction. **Detector (registered, free):** the ABBA/BAAB start alternation (R-Q4(b), `13-…:36`).
   - If the mean of y over ABBA-start envelopes differs from the BAAB-start mean by more than 2·SE, withhold with `floor_est_carryover_suspect`.
   - Weak secondary check: one-sided F test of the claim scatter s_y against the null scatter s_x per model. At df (4, 4) this detects only an SD ratio of about 2.5 or more; I state that weakness here.
2. **Non-deterministic replay** (MLX GPU kernels): same seed but different traces, which falsifies J2's premise. **Detector:** the byte-match count in the null and claim envelopes. If the ceiling is exceeded, correctness is stochastic at a fixed seed, and V_shared must add replay variance, measured by a repeated accuracy run.
3. **Accuracy SE much smaller than assumed**, for example with strictly nested budgets. The floor would then bind and its precision would matter. **Detector:** V_shared projected from the pilot, plus the CG-4(e) simulation re-run at registration. If F_Δ exceeds a third of the expected Holm threshold, raise k_cal to 10 (g = 1).
4. **Relative scatter much larger at the lowest-energy level than elsewhere.** This errs large and hides effects. **Detector:** printed descriptively (x scatter against block energy); non-gating.

**Executable text J5.** *Register `floor_est_carryover_suspect` (ABBA/BAAB split rule above), the byte-match ceiling applied to null envelopes, the pilot-projected V_shared, and the F_Δ-against-threshold check. Each is evaluated before any Δ_L is admitted. A tripped check makes that level `not_resolvable` and never falls back to another floor.*

## Where I expect the other seats to be wrong

- They will take the question's "±1 correct → ±17 %" at face value and put correctness noise into the floor, via (a) with varied seeds or an inflation factor. That gives a floor around 0.6 in log units and almost no power, and still leaves CG-1's standard error blind to accuracy sampling.
- They will miss that CG-1's envelope-only standard error omits the shared accuracy and subsample terms. That is 91 % familywise false admission at effect 0, and no floor choice fixes it.
- They will answer J3 with "the larger of the two", which errs small when the biases have opposite signs.
- They will treat the choice between (a) and (c) as what drives the window count. The two-model null (10 windows) drives it.

## Plain summary for Ed

- The headline compares how much energy each model spends per correct answer, and how that changes as the models are allowed to think longer.
- The "noise floor" should capture only what the power meter gets wrong. Whether an answer is right comes from a separate 128-problem test, so that uncertainty belongs in the error bars, not in the floor.
- The claim gate as written ignores that error-bar term. In a desk simulation it would announce a false difference 91 % of the time. This must be fixed before anything is registered.
- I recommend stating the result as a ratio, measuring the floor on that same ratio scale, and calibrating both models (10 extra quiet measurement windows).
- With realistic numbers, the main limit on what we can detect is the 128 test problems (a change of about 30 % or more), not the power meter.
- Two built-in checks catch the main ways this could fail: heat carrying over between runs, and repeat runs that do not reproduce.
