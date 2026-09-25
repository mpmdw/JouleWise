# 65 — Synthesis of the D-184 council on the claim-admission gate and the equivalence rule (magistrate, Opus 5.5)

Four blind seats answered brief 58 on packet 55: Sol 59, Astra 60, Opus 61 and Fable 62. This synthesis binds nothing; a cold Fable judge rules on packet 66.

Terms:
- **Claim gate:** `joulewise/analysis_engine/claims.py`, which admits a paper sentence about an energy difference only when its conditions pass.
- **F:** the instrument floor, meaning the largest false effect the instrument can produce on a null (A vs A) comparison.
- **B:** the deterministic clock-anchor bound, charged once per claim.
- **Holm m = 5:** AP-5M's multiplicity correction across its five difficulty levels.

## Where all four agree

1. **The replicate unit is the night or envelope (cluster), not the block.** Shared shocks enter only through between-cluster variance. The current gate treats block scatter as the standard error, which is why its nominal interval covers only about 56 %.
2. **The floor is on the wrong scale.** Today a MEAN of n blocks is compared with a ONE-BLOCK prediction floor, which is ≈√n too conservative and makes real effects unadmittable. The floor must sit on the estimate's (mean's) scale: Opus `F_mean`, Fable `F_est`, Sol `F_est`. It stays a separate, strict physical condition (O-21), charged once, with B on the claim side.
3. **A directional claim requires an interval bound, not a point estimate:**
   - the Holm-adjusted test at m = 5, with missing hypotheses kept;
   - the anchor-widened decision interval excluding zero on the registered side;
   - the magnitude condition against the estimate-scale floor or a registered minimum.
4. **The equivalence margin is a physical tolerance in joules**, with the interval (1−2α, anchor-widened, clustered) strictly inside it. A "4σ" diagnostic margin is not a registration. Clustering is mandatory for equivalence claims.
5. **The equivalence NIGHT ("instrument unchanged") must test both location and spread** (variance), with a calibrated false-FAIL rate. The proposed TOST replacement's blindness to a ×4 variance increase is unacceptable.

## Where they differ

- **Interval construction.** Astra inverts an exact night-level sign-flip test, which makes no normality assumption; Fable and Opus use a t interval on cluster means, df = k−1 (Fable feeds envelope means to the existing `estimate_paired_blocks`); Sol uses a dependence-preserving resample of whole nights.
- **Magnitude test.**
  - Fable: the decision interval's NEAR endpoint must exceed F_est, a lower-bound test.
  - Opus: a strict point test |θ̂| > F_mean plus the interval excluding 0. Opus proposes no new code path: the caller passes F_mean.
  - Sol: the lower confidence bound must exceed a registered τ, and separately the point estimate must exceed F_est.
  - Astra: a composite-null minimum-effect test |θ| ≤ d, plus |θ̂| > F.
- **The replicate count and scope.** Opus says G ≥ 3 clusters to generalise and otherwise scope the claim to the nights measured. Fable says k ≥ 5 envelopes, which AP-5M already has. Sol and Astra say night-level, with a one-night claim worded as that night only.
- **Equivalence-claim margin.** Fable says the interval must sit inside ±(Δ − F_est) with Δ ≥ F_est + B, and puts honest margins at 3–5 J. Opus says M ≥ max(tolerance, F_mean). Sol says M > F_est.
- **Equivalence-night parameters.**
  - Astra: a mean within ±3 ms, and within-night and night-mean variance ratios in (¼, 4).
  - Sol: 2σ with variance ratio [½, 2], labelled as proxies.
  - Fable: INCONCLUSIVE below m = 8, a location TOST, a spread test against the operative screens.
  - Opus: the old corpus spans ten windows (a1–a10), not one night as the desk model assumed. The simulation must be re-based on that.
- **Fable's worked numbers.** At σ = 0.4 J, w = 1 J and k = 5 × 6 blocks, the effective minimum detectable effect is ≈2 J, and a 1 J effect is never admitted.

## Proposed rulings (the magistrate's; the judge may amend any)

- **CG-1 (directional).** Envelope means are the replicate: k ≥ 5 envelopes, df = k−1. Estimate-scale floor `F_est = g(n_cal)·(|mean_cal| + t_{0.975,n_cal−1}·s_cal/√n_cal)` from the same-epoch null corpus. Admit `direction_supported` iff all three hold:
  - Holm-adjusted p < 0.05 (m = 5, missing kept);
  - the decision interval θ̂ ± (h + B) excludes 0 on the registered side;
  - the interval's near endpoint exceeds F_est (Fable's lower-bound form, the most conservative of the four that still admits real effects).
  Astra's exact sign-flip interval is a registered SENSITIVITY analysis. A claim scoped beyond the measured nights requires at least 3 distinct nights.
- **CG-2 (equivalence claim).** Register a physical margin Δ ≥ F_est + B. Admit iff the clustered 90 % decision interval lies inside ±(Δ − F_est) and the Holm-adjusted TOST p < 0.05.
- **CG-3 (equivalence night).**
  - INCONCLUSIVE below retained m = 8.
  - Location: TOST on the mean timing bound with a physical tolerance (Astra's ±3 ms ≈ 0.1 J at 33 W is the proposal).
  - Spread: both within-night and night-mean variance ratios inside (¼, 4).
  - Before registration, simulate on a desk model re-based on the actual a1–a10 corpus structure. Report false-FAIL at no change and power against +5σ and ×4 variance.
- **CG-4 (implementation).** One PR, full tier, with rules before data. `claims.py` gains the envelope-cluster path and the estimate-scale floor. The existing block floor stays for window admission. Every constant has a D-numbered addendum. The desk simulation is re-run on the new rules and committed before any claim-bearing use. AP-5M v5's claim section cites CG-1/CG-2 by id.
