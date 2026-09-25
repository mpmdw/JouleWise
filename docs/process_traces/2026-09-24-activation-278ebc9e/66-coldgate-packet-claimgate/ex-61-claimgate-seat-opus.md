# Opus 5.5 — blind council seat on the claim-admission gate and the equivalence rule

**Main point.** The current gate refuses real effects because it compares two different kinds of number, not because it is too strict. It compares the mean of n blocks with a floor built to bound **one future block**. That floor includes `sqrt(1+1/n)`, the largest single deviation, and the small-sample guard (`joulewise/detection_floor.py:871-881`; `claims.py:343-344`; `estimators.py:450-469`). The fix is to give each kind of estimate its matching floor. O-21's form `|estimate| > F` survives unchanged; O-21 already says the floor must be *applicable* (`…02a24110/01-ed-rulings-harvest-and-reply-miss.md:43`). The second finding is that night-level shocks mainly damage **equivalence** claims, not directional ones.

## (a) Directional rule R-D

**Estimand.** θ is the registered signed paired contrast: the mean of (B−A) in joules over the registered blocks, window class and epoch. The claim is scoped to the nights or envelopes actually measured. If the claim is to generalise to the machine, blocks must span G ≥ 3 nights or envelopes, and the standard error comes from the G cluster means with df = G−1.

**Inputs.**
- The analysis blocks give θ̂, SE and h = t(0.975, df)·SE.
- B is the mean per-block anchor half-width (the deterministic bound), already inside the decision interval (`estimators.py:486-489`).
- The calibration gives k ≥ 10 same-condition A/A block deltas c_i. "Same-condition" means the same metric, window class and epoch. Spreading them over ≥ 3 nights is recommended.

**New estimate-level floor, the "false mean-effect floor":**
```
F_mean = g(k) · ( |c̄| + t(0.975, k−1) · s_c · sqrt(1/n + 1/k) ) + B_corner
```
- B_corner is the worst-case corner shift of a mean. When all block signs align it equals the mean of the w_i.
- g(k) is the existing guard factor (`detection_floor.py:850-854`).
- This is the largest false **mean** effect of an n-block A/A contrast.
- |c̄| carries the part of the floor that no A/B interval can see: any instrument asymmetry that makes A/A read as nonzero.
- The existing block floor, F_block, stays in force for window admission (`52-ap5m-v5-draft/01-ap5m-draft-v5.md:51`) and for single-block claims.

**Admit `direction_supported` only if all three hold:**
1. The Holm-adjusted two-sided p < 0.05 across the frozen family (AP-5M: m = 5, missing hypotheses kept, `multiplicity.py:49-77`).
2. The decision interval θ̂ ± (h+B) excludes 0.
3. |θ̂| > F_mean, a strict point test.

**No new code path in `claims.py`.** The caller passes F_mean as `floor_gate_j`, with a new floor-class and rule version. Two small additions are needed: a `comparative_false_mean_effect_floor(deltas, n_analysis, widths)` beside `detection_floor.py:1132`, and a metadata field so that an F_block value can never be passed for a mean.

**Minimum effect.** A sign claim needs no δ_min beyond F_mean. If the wording says "by more than X", register δ_min ≥ F_mean in joules. Then require the decision interval's lower bound > δ_min, and apply Holm to the shifted-null p = P(T > (|θ̂|−δ_min)/SE). F must **not** become "lower bound > F_mean": F_mean already contains the sampling term, so that would count it twice. This follows D-078 cl.11 and the D-083 addendum (`docs/decision_log.md:4803-4814,11291-11303`).

**Scale, illustrative only.** Take a contrast scatter s_c ≈ 0.5 J (the repeatability of 0.29–0.49 J per member, `decision_log.md:4757-4763`), k = 10 and n = 30. The stochastic part of F_mean is then ≈ 0.2 + 2.26·0.5·0.365 ≈ 0.6 J, and F_mean ≈ 0.6 J + B. The ~1 J anchor term B dominates. The old "≈5 J bar" was F_block + B, which the addendum demoted to a non-gating planning figure (`decision_log.md:11275-11283`).

**AP-5M mapping.** The contrast is Δ_L = log R_L(b_high) − log R_L(b_low) (`01-ap5m-draft-v5.md:65-67`). The instrument's false effect on log C in cell j is approximately F_mean,j / e_j. The matched floor is F_log = Σ over the four (model, budget) cells of F_mean,j / ê_j, with worst-case corners adding. The test is |Δ̂_L| > F_log. The floor applies only to the energy numerator; accuracy sampling in p is not an instrument effect and belongs in the bootstrap.

## (b) Equivalence claim and equivalence night

**Equivalence claim.**
- **Margin.** Register M in joules, with M ≥ max(practical tolerance, F_mean). Today `claims.py:352` demands M > F, and F_block's median in the simulation grid was ~8.5σ (`19-desk-simulations/README.md:48`), so almost no sensible margin qualifies. F_mean fixes that.
- **Interval.** The 90% (1−2α) t interval widened by B must lie inside (−M, M), and the Holm-adjusted TOST p must be < 0.05.
- **Clustering is mandatory for equivalence.** The standard error must come from G ≥ 3 night or envelope clusters, or be inflated by a between-night variance τ² estimated from multi-night A/A calibration. The simulation below shows why: without it, false equivalence at the margin reaches 0.18.

**Equivalence night, rule R-N (instrument unchanged).** Two facts from the r7 calibration file change the design:
- The old corpus spans ten capture windows, a1–a10 (`configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:157,164`, `source_directory` fields). The desk model instead drew it from one night (`sim.py:213`).
- Every capture re-measures its own fiducial offset b and drift: `operative_bound_rule` and `allowance_rule max(observed_drift_s, bracket_screen_s)` (`…_r7.json:489-490`).

The rule, with m ≥ 12 retained captures:
1. **Level test.** The upper prediction bound (x̄_new − x̄_old) + t(0.95, 16)·s_old·sqrt(1 + 1/17) must be below Δ = 3.5·s_old = 8.61 ms. The new night's mean is treated as one draw from the multi-night population. Physically, Δ ≈ 33 W × 8.6 ms ≈ 0.28 J, below the repeatability (the ~31 ms ↔ ~1 J conversion is at `decision_log.md:4763`).
2. **Spread/tail test.** FAIL if **≥ 6 of 12** new values fall outside the old [min, max]. Under exchangeable data this test needs no distributional assumption; the exchangeable null is P(K ≥ 5) = 0.031, and K ≥ 6 is lower still.

**Variance side.** No rule that uses one night with m = 12 got both ≤ 5% false FAIL and strong detection of a fourfold variance increase once night shocks exist. Mine detects ×4 variance 0.34–0.41 and ×16 variance 0.77–0.92.

- Physically, ×4 variance moves b's SD from 2.46 to 4.9 ms. That is ≈ 0.16 J, and each capture's bound widens itself from its own measured b.
- What actually needs checking is **floor transfer**: does the old F still describe the new night? Add a direct A/A spot-check on the equivalence night: 6 A/A blocks, FAIL if ≥ 2 have |d_i| > F_block. If blocks are independent and each exceeds with probability ≤ 0.05, the false-FAIL rate is ≈ 0.033 (binomial). **This is not simulated**, and night dependence would inflate it.

## (c) Operating characteristics

The scripts reuse the desk `noise` and `shared_shock` generators and the production `holm_adjust`, `student_t_*` and `small_sample_guard_factor`.

```
python3 /tmp/278ebc9e/cg-opus/sim_opus.py 200 12 same_night   # 192 cells: 4 models×k{5,8,10,16}×n{10,30}×w{.5,1,2}; 2400 comps/cell
python3 /tmp/278ebc9e/cg-opus/sim_opus.py 200 12 indep_night  # calibration on a different night (own shock)
python3 /tmp/278ebc9e/cg-opus/sim_opus.py 200 5  indep_night  # Holm m=5
python3 /tmp/278ebc9e/cg-opus/night_opus.py 2000; python3 /tmp/278ebc9e/cg-opus/night_variants.py
```

**R-D directional admission** (current gate for comparison: 2σ 0.000, 5σ 0.160; `README.md:44-46`):

| Calibration | δ=0 false admission, mean (worst cell) | 2σ power | 5σ power | Decision-interval coverage |
|---|---|---|---|---|
| Same night | 0.000 (0.001) | 0.267 | 0.925 | 0.950 |
| Independent night, m=12 | 0.004 (**0.059**, shared_local k16 n10 w.5) | 0.253 | 0.929 | 0.951 |
| Independent night, m=5 | 0.004 (0.063) | 0.254 | 0.929 | 0.950 |

- **By calibration size k** (independent night), 2σ / 5σ power: k=5 0.081/0.777; k=8 0.232/0.965; k=10 0.317/0.985; k=16 0.381/0.990. At n=30, w=0.5σ, 2σ power is 0.615 at k=10 and 0.723 at k=16.
- **By anchor width w** (n=30), 2σ / 5σ power: w=0.5σ 0.505/0.983; w=1σ 0.289/0.966; w=2σ 0.034/0.866.
- **By model**, 5σ power ranges 0.912–0.948 and 2σ power 0.198–0.290.

**TOST** (M = 4σ, B-widened 90% interval, Holm m=12, M > F_mean required):
- At δ=0, equivalence is admitted 0.833–0.840.
- At δ = M (the boundary), false equivalence averages 0.026–0.029. By model it is 0.013–0.061, and the worst cell is **0.176** (shared_local, k8 n30 w0.5, interval coverage 0.66).
- At δ=5σ, false equivalence is 0.001.

**Equivalence night, PASS rates** (ranges across the four models; old corpus laid out over ten windows like r7):

| State | R-N (K≥6) | Desk proposal | Current rule |
|---|---|---|---|
| No change | 0.914–0.950 | 0.991–1.000 | 0.543–0.692 |
| +3σ | 0.006–0.024 | 0.340–0.459 | 0.005–0.043 |
| +5σ | 0.000 (K≥5 run) | 0.000–0.004 | 0.000–0.018 |
| ×4 variance | 0.590–0.663 | 0.921–0.957 | 0.041–0.152 |
| ×16 variance | 0.082–0.232 | — | — |

- With the desk's single-night old corpus, R-N's no-change PASS falls to 0.717–0.919 and ×4 variance PASS is 0.394–0.551.
- R-N FAILs a +3σ shift (7.4 ms), which is inside Δ. This is deliberate: an equivalence test must *show* the shift is small, not merely fail to see it.

## (d) What stays a physical condition, not a statistical one

These are not statistical tests and should not be adjusted for multiplicity:
- F_mean and F_block, which bound instrument-made false effects.
- B, the anchor bound, which is deterministic and stays inside the interval.
- The window-admission floor.
- Epoch identity: the 25G83 acceptance and the network-time-off admission.
- Byte-match ceilings and p > 0.

F stays a **point** conjunction, as Ed ruled, and no F+B sum is ever gated (`decision_log.md:11291-11303`).

## (e) What would show R-D wrong, what it costs, what it affects

**Falsifier.** Run a real A/A calibration over ≥ 3 nights. If the between-night contrast SD τ is comparable to F_mean's stochastic term, a leave-one-night-out replay of R-D on those A/A data will admit more than 0.05/m. The simulation already shows this pressure: 0.059 at k=16, w=0.5σ, where F_mean is small. If it happens, F_mean must add t·τ, estimated from nights.

**Cost.**
- One floor function and one floor-class/version field.
- A caller change in the gamma contrast producer.
- For AP-5M, the F_log conversion and cluster ids in the bootstrap.
- For R-N, a roughly 40-line replacement of the verdict core at `scripts/epoch_equivalence_check.py:480-536`, frozen before its first night, plus the A/A spot-check.

**Rules before data.** The prospective comparison is unperformed and AP-5M v5 is unadopted, so registering R-D now is clean. Past epoch-equivalence verdicts keep their historical bytes, and R-N applies only prospectively. I did not audit for existing `direction_supported` artifacts; the magistrate should grep for them. Anything admitted under F_block cleared a floor that was usually larger.

## (f) What the question misses

1. **Framing.** This is not a "strictness" question. Tuning α cannot fix a gate that compares mismatched quantities; only matching the floor to the estimate can.
2. **The shock model is an assumption, not a measurement.** The desk shock is additive on the *contrast*. An additive energy shock would cancel under ABBA pairing, so the 0.56 metrology coverage depends on that assumption. The size of τ is the key missing measurement, and multi-night A/A calibration provides it.
3. **The old corpus is multi-night.** The r7 corpus spans ten windows, which changes every equivalence-night rate in the packet.
4. **The equivalence night tests a proxy.** Downstream bounds re-measure b per capture and protect themselves. Floor transfer is the property actually consumed, and only an energy A/A spot-check tests it directly.
5. **The cheapest power lever is calibration size.** k=5→16 raises 2σ power from 0.08 to 0.38 (0.18→0.72 at n=30, w=0.5σ). That is cheaper than more analysis blocks.
6. **Some effects are unresolvable by physics.** At w=2σ, a 2σ effect is unresolvable by any honest rule (power 0.034). Report that as an instrument limit; do not engineer the gate around it.

**Scope note.** These are synthetic, model-conditional rates. The simulation scripts live only under `/tmp/278ebc9e/cg-opus/`; I wrote nothing to the repo.
