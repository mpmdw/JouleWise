# Fable 5.1 — blind council seat, claim-admission gate and equivalence rule

## Diagnosis (why the current gate has no power)

The gate compares a **mean of n blocks** with a floor built for **one future block**: `abs(estimate) <= floor` at `joulewise/analysis_engine/claims.py:343-344`, against `F = max(max|d|, |mean| + t·s·sqrt(1+1/n))` at `joulewise/detection_floor.py:871-881` (guard `sqrt(9/(n-1))`, lines 850-854). Median F in the desk grid is about 8.5σ (`19-desk-simulations/README.md:48`) while the mean of 30 blocks has SE 0.18σ. That is a scale mismatch, not conservatism. Separately, the paired estimator's interval is within-night only (`estimators.py:461-467`, df = n−1), so a night-level shock is invisible and coverage drops to 0.56 (`README.md:44-46`). Two defects, two fixes: put the floor on the estimate's scale, and put the interval on the envelope's scale.

## (a) Directional rule (executable)

1. **Estimand.** θ = expected paired contrast B−A (J, or J/correct J-difference) over the registered block population on one frozen instrument epoch; registered sign.
2. **Unit and interval.** The independent replicate is the **envelope** (quiet window), not the block. Compute each envelope's mean contrast; feed the k envelope means to the existing `estimate_paired_blocks` (`estimators.py:450-509`) so df = k−1 and the between-envelope shock enters the sample variance by construction. Metrology terms stay in quadrature; the anchor bound B (mean of per-block bounds) still widens the decision interval. Register k ≥ 5 (AP-5M already requires five envelopes, `52-ap5m-v5-draft/01-ap5m-draft-v5.md:51`). Within-envelope drift and ABBA order effects average out inside the envelope mean; heavy tails are handled by the existing LOO sensitivity codes (`claims.py:206-215`).
3. **Minimum effect.** Replace the point test with a lower-bound test: both intervals exclude zero on the registered side AND the decision interval's near endpoint satisfies `min(|lower|,|upper|) > F_est`, where
   `F_est = g(n_cal) · ( |mean_cal| + t_{0.975,n_cal−1} · s_cal / sqrt(n_cal) )`
   from the same-epoch null (same-model A/B/B/A) corpus. F_est is the 95% upper bound on the instrument's **systematic** false contrast on the mean scale; scatter and allocation ambiguity of the claim's own blocks are already in h and B on the claim side. The attribution limit is therefore charged once, as B (~1 J per block, `docs/decision_log.md:4757-4771`). Effective minimum detectable effect at real instrument numbers (σ = 0.4 J, w = 1 J, k = 5×6 blocks): F_est ≈ 0.5–0.9 J, B = 1 J, h ≈ 0.4 J, so ≈ 2 J; a 1 J effect is never admitted (table below). This respects D-078 cl.11's ≈5 J planning bar as an outcome, not as a gate constant. Conservative variant (charge w̄ on the calibration side too, `F_est + w̄_cal`): minimum ≈ 3.2 J; I do not recommend it, because under the frozen identity epoch (D-102, `decision_log.md:6453-6485`) a systematic anchor offset is common to both corpora and is already inside |mean_cal|.
4. **α and multiplicity.** Two-sided α = 0.05; Holm on the envelope-level p-values with frozen m (5 for AP-5M, `01-ap5m-draft-v5.md:65`), via `holm_adjust` (`multiplicity.py:49-77`). Intervals stay nominal 95%; the floor condition is physical and is not family-adjusted.
5. **F_block stays** as the published instrument characteristic and single-block resolvability label; it stops gating mean claims. O-21's `|estimate| > F` holds with F = F_est (the estimate-level floor AP-5M left undefined, `01-ap5m-draft-v5.md:67`), and is implied by the lower-bound test.

## (b) Equivalence claim and equivalence night

**Claim (TOST).** Same envelope-level decision interval. Register a physical margin Δ; admit `equivalent` iff the decision interval lies inside ±(Δ − F_est) and the Holm-adjusted `max(p_lower, p_upper)` (`estimators.py:251-279`) is below α. Requiring Δ > F_est alone (`claims.py:351-352`) is not enough: the instrument's null bias can sit anywhere inside ±F_est, so it must be subtracted from the margin. Δ is a practical tolerance in joules, at least F_est + B; AP-4's 2% of a ~50 J request (`docs/contracts/analysis_plans.md:236-251`) is ≈1 J and is **not resolvable** on this instrument; the honest margins are 3–5 J.

**Night (instrument unchanged).** The consumer of the old envelope is the pair of operative screens (`scripts/epoch_equivalence_check.py:33-57`), so the night must test both location and spread against them, with a calibrated false-FAIL. Rule:
- INCONCLUSIVE if retained m < 8 (not 12: any single capture loss must not cost a night; not 6: spread tests at m = 6 are unstable).
- Location: TOST of the new mean against the old, margin Δ_loc = 3.5·s_old = 8.61 ms (desk value), df = min(n−1, m−1). This margin is lax because it tolerates night-to-night movement, which is real: r7's four capture dates have date-mean SD 1.31 ms against pooled SD 2.46 ms (`configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`, members by date 5/6/1/5).
- Spread: one-sided **permutation test** of log(var_new/var_old) on the pooled 29 values; FAIL if p < 0.05. Only a spread increase fails, because a tighter instrument cannot invalidate the screens. Exact under exchangeability for any tail shape.
- Diagnostic, non-gating: count of new values above the level screen (32.898 ms) and the new range against the bracket screen (9.724 ms), printed with the verdict.

## (c) Operating characteristics

Scripts under `/tmp/278ebc9e/cg-fable/` (call production floor, estimator, Holm, `evaluate_claim`, `evaluate_session`; same four generators as `19-desk-simulations/sim.py:52-65` plus a night-shock sd τ per envelope).

```
python3 dir_sim.py --trials 100 --units sigma     # 4 models × n{10,30} × w/σ{0.5,1,2} × δ/σ{0,2,5}, k=5, n_cal=8, Holm m=5
python3 dir_sim.py --trials 300 --units joule     # σ=0.4 J, w=1 J, k=5×6, τ∈{0,0.3 J}
python3 dir_sim_tost.py --trials 150 --units joule
python3 eq_sim.py 200                             # old n=17, m∈{8,12}, states none/+3σ/+5σ/×4var
```

False admission at δ = 0 was 0.000 in every cell for both the current gate and the proposed rule (500 decisions per cell); metrology-interval coverage rose from 0.73–0.97 (n = 10) and 0.77–0.90 (n = 30) to 0.92–0.98 under the envelope interval. Admission (power), σ units, τ = 0.5σ:

| model, n | w/σ | δ=2σ cur / new | δ=5σ cur / new |
|---|---|---|---|
| gaussian 30 | 0.5 / 1 / 2 | 0.00 / 0.12 · 0.00 / 0.03 · 0 / 0 | 0.51 / 1.00 · 0.05 / 1.00 · 0.00 / 0.86 |
| heavy_t3 30 | 0.5 / 1 / 2 | 0.00 / 0.13 · 0.00 / 0.05 · 0 / 0 | 0.79 / 0.99 · 0.24 / 0.98 · 0.00 / 0.89 |
| linear_drift 30 | 0.5 / 1 / 2 | 0.00 / 0.08 · 0.00 / 0.00 · 0 / 0 | 0.47 / 1.00 · 0.05 / 0.98 · 0.00 / 0.88 |
| shared_local 30 | 0.5 / 1 / 2 | 0.00 / 0.13 · 0.00 / 0.01 · 0 / 0 | 0.61 / 1.00 · 0.03 / 1.00 · 0.00 / 0.59 |

A 2σ effect stays unadmitted because at w ≥ 0.5σ it is at or below the anchor bound; that is the physics, not a gate defect. Joule units (τ = 0.3 J, k = 5 envelopes × 6 blocks; F_block ≈ 4.4 J, F_est ≈ 0.65–0.86 J):

| δ (J) | current adm. (4 models) | proposed adm. | TOST Δ=3 J / Δ=5 J admits |
|---|---|---|---|
| 0 | 0.000 | 0.000 | 0.83–0.99 / 0.99–1.00 |
| 1 | 0.000 | 0.000 | 0.15–0.53 / 1.00 |
| 2 | 0.000 | 0.19–0.49 | 0.000 / 0.92–1.00 |
| 3 | 0.000 | 0.91–1.00 | 0.000 / 0.16–0.56 |
| 5 | 0.65–0.92 | 1.000 | 0.000 / 0.000 |

TOST never admits equivalence when δ ≥ Δ. Equivalence night, old n = 17, PASS rates (no-change: 1 − PASS is false FAIL; changed: PASS is a miss):

| model | m | none cur / desk / mine | +5σ | ×4 var cur / desk / mine |
|---|---|---|---|---|
| gaussian | 12 | 0.43 / 1.00 / 0.96 | 0 / 0 / 0 | 0.04 / 0.97 / 0.25 |
| heavy_t3 | 12 | 0.38 / 0.99 / 0.93 | 0 / 0 / 0 | 0.10 / 0.91 / 0.39 |
| linear_drift | 12 | 0.37 / 1.00 / 0.97 | 0 / 0 / 0 | 0.01 / 0.92 / 0.23 |
| shared_local | 12 | 0.40 / 1.00 / 0.90 | 0 / 0.01 / 0.01 | 0.02 / 0.90 / 0.27 |
| all four | 8 | 0.43–0.61 / 0 (refuses) / 0.91–0.97 | ≤0.04 | 0.07–0.24 / refuses / 0.36–0.56 |

My rule holds false FAIL at 3–10% (heavy tails worst) while detecting a fourfold variance increase in 61–77% of nights at m = 12, against 3–10% for the desk proposal. The current rule detects spread best (90–99%) but at a 57–63% false-FAIL cost, which is a night wasted more often than not. The +3σ shift is missed 40–48% by both TOST rules; that is the price of the 8.6 ms location margin (see (e)).

## (d) Physical conditions that stay outside the statistics

- F_block, the corner-widened prediction floor, remains the published instrument characteristic (labelled attribution-limited, `docs/phase_2/detection_floor.md:73-84`) and the single-block resolvability label. It is not a mean-claim gate.
- The anchor bound B stays a deterministic widening, never a variance term (D-078 addendum, `decision_log.md:11268-11283`); the same-epoch requirement between calibration and claim (`floor_row_stale`, `claims.py:184`) is what licenses charging w once.
- Window admission (calibration bracket, interpolation bound, anchor resolution) stays a per-window refusal set (`claims.py:40-73,105-108`). The "block window must clear floor_gate_j" sentence at `01-ap5m-draft-v5.md:51` should be rewritten to name those checks: gross window energy against a contrast floor is a category error.
- The equivalence night's identity-epoch triggers (D-102) remain hard refusals independent of any statistic.

## (e) Falsifiers, cost, affected registrations

- **Wrong if:** a real same-model null campaign (≥ 5 envelopes, ≥ 30 blocks) yields `direction_supported` under the new rule more than 1 time in 20 families; or envelope-level 95% interval coverage on repeated null envelopes falls below 0.90; or the equivalence night's no-change false FAIL, measured on re-derivation nights of an unchanged build, exceeds 10%.
- **Cost:** `claims.py:343-344` becomes a lower-bound comparison on the decision interval; a `floor_est_j` producer (mean-scale bound from the null corpus, guard retained) beside `floor_gate_j` in the floor artifact; envelope IDs carried in `PairedObservation` so the caller can aggregate; a permutation spread test and m ≥ 8 in `epoch_equivalence_check.py` replacing lines 127 and 480-536; fresh coverage/power simulation as the registration's evidence; reason-code vocabulary unchanged except a new `effect_lower_bound_not_above_floor`.
- **Affected:** no existing claim uses `evaluate_claim` for a published result (the prospective comparison is unperformed, `docs/paper/protocol/prospective-comparison-protocol.md:1-6`). AP-5M v5 §4 and §6 must be amended before registration; O-21 is satisfied with F = F_est. The equivalence-night change contradicts the numerical shape Ed fixed in issue 316 (`epoch_equivalence_check.py:5-10`), so it needs Ed's notice under D-184's after-the-fact rule, not silent installation.

## (f) What the question misses

1. **The scale is joules, not σ.** Asking for power "at 2σ" hides that 2σ is 0.8 J on an instrument whose allocation ambiguity is ~1 J per block; no sound gate admits that, and no gate should be tuned until it does. Power should be registered at 2, 3 and 5 J.
2. **The night shock is a design fact, not an interval fact.** No single-night interval can cover a between-night term; the fix is k ≥ 5 envelopes as the unit, which AP-5M already pays for.
3. **The equivalence night protects yield, not claims.** Each capture's own b_fiducial_s enters B; the screens only decide admission. A +3σ (7.4 ms) shift would put the mean above the 32.9 ms level screen and refuse most captures pre-flight, which fails closed. The location margin can therefore be lax; the spread side is what must be tested, because a wider spread silently loosens the drift budget.
4. **Two floor objects are being conflated** (window-admission floor, contrast floor). AP-5M §4 needs the vocabulary before a registration is written.
5. **The conservative-versus-single-count choice for w̄ on the calibration side** is the one real judgment call here; I have made it (single count) and stated the physical assumption it rests on.
