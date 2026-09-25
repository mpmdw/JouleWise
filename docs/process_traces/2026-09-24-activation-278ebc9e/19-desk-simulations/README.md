# R-Q4(a) desk simulations, 2026-09-24

## Terms and decisions

A **block** is one paired contrast. The unit σ is the standard deviation of a block's local random error before any night-wide disturbance. An **admissible half-width** w is the largest allowed timing-caused movement of one measured block; w/σ states its size relative to that local error. A **calibration sample** estimates the false-effect floor, and an independent **analysis sample** supplies a claim. The true effect δ is measured in the same σ units. A **component** is one of twelve related contrasts in a night. Each simulated night draws one disturbance shared by its twelve components, so a joint verdict is counted from the twelve actual decisions in that trial.

The **point floor** is the production `_floor_estimate` without timing intervals. The **guarded floor** F is the production `comparative_false_effect_floor` after exact admissible-set corner enumeration and its small-sample guard. The production `dominance_ratio` gives R = corner-widened unguarded floor / point unguarded floor. The D-165 component label passes at R ≥ 2; the registered joint label requires all twelve components to pass. This ratio describes the constructed uncertainty accounting, not a physical source of energy variation. It should be reported continuously with w.

The **directional claim** is the actual `estimate_paired_blocks` interval and `claims.evaluate_claim` decision with the production `holm_adjust` over twelve two-sided p-values. Holm adjustment controls a family's multiple-testing threshold by ordering its p-values and scaling them by remaining tests. Its `direction_supported` outcome is an admission; `not_resolvable` or `not_estimable` is a refusal; `unresolved` is a judged but unadmitted result. The branch with `equivalence={method: tost_v1, margin: 4σ}` is separately exercised with the production `tost_p_value`; TOST means two one-sided tests asking whether an effect lies inside a chosen equivalence margin. This branch uses unadjusted α=0.05 as a diagnostic, so its rates are not a frozen-family equivalence claim.

An **equivalence night** compares a new set of valid, resolved timing bounds with an old corpus. The current rule passes when the new maximum does not exceed the old maximum and the new range does not exceed the old range. It is inconclusive below six retained captures. The simulation calls the production `epoch_equivalence_check.evaluate_session` numerical decision on synthetic retained values. The synthetic adapter bypasses ledger-byte authentication; the simulation says nothing about custody refusal rates. The proposed replacement in [equivalence_replacement.md](equivalence_replacement.md) uses a mean-equivalence interval and a sample-variance ratio.

## Generating models and grid

All four models have a unit-scale local error and a disturbance shared across twelve components. **Gaussian** draws normal local errors. **Heavy-tailed** draws variance-one Student t errors with three degrees of freedom. **Within-night drift** adds a centered linear trend across ordered blocks. **Shared plus local timing** splits each allowed timing width into w/2 shared across the night and w/2 local to each block, then draws each timing offset uniformly inside its half-width; the production ordinary floor still receives the full w for each block. The last model also splits stochastic variation into a night term and local terms. A shared disturbance is drawn anew for the old and new equivalence nights; treating captures within one night as independent therefore risks undercoverage.

The floor and claim grid crosses four models × calibration n={5,8} × analysis n={10,30} × δ/σ={0,2,5} × w/σ={0.5,1,2}: **144 cells, 30 trials per cell**, twelve components per trial. The production exact-corner floor caps calibration n at 16. The separate seed-278 smoke uses n=10 and w/σ={0.5,0.75,1,1.5,2}, 400 trials per width. The equivalence grid crosses four models × old-corpus n={12,17} × retained m={4,6,7,12} × {no change, +3σ mean, +5σ mean, ×4 variance} × six proposed parameter pairs: **768 cells, 600 trials per cell**. Its m=4 cells are intentionally inconclusive. All seeds and model definitions are in [sim.py](sim.py) and `results/metadata.json`.

## Rate definitions

**False admission** means a favorable decision in a declared adverse state: a directional claim when δ=0, an equivalence PASS after a shift or variance change, or (as a diagnostic proxy only) a D-165 pass at w/σ=0.5. **Missed effect** means no favorable decision when the declared favorable state holds: a directional claim with δ>0, an equivalence FAIL under no change, or a D-165 failure at w/σ=2. The D-165 proxies are operational labels, not physical ground truth. **Coverage** means that an interval contains its generating value: the claim's 95% metrology interval or expanded decision interval, the floor's guarded prediction containing a future block and its width, or the proposed rule's 90% mean-difference interval. The old equivalence and D-165 ratios have no confidence interval and hence no interval-coverage rate. **Refusal** means `not_resolvable`/`not_estimable` in claims, zero-denominator or outside-domain refusal for the ratio, or INCONCLUSIVE for the equivalence rules. A FAIL is not a refusal.

Each floor/claim cell has 360 component decisions and 30 joint decisions. Each equivalence cell has 600 nights. The largest binomial Monte Carlo standard errors are about 0.026 and 0.020, respectively, before comparison across cells. Rates are conditional on the synthetic data and the stated modeling choices.

## Headline results

The tables below are calculated from the tracked CSV and JSON cell outputs. They are descriptive across cells, not a substitute for a registered experiment.

**D-165 ratio.** Each entry averages twelve cells for that model and width (two calibration sizes × three effects × two analysis sizes). The single-component and joint rates are counted from the same shared trials.

| Model | w/σ | Median R | One component R≥2 | All twelve R≥2 |
|---|---:|---:|---:|---:|
| Gaussian | 0.5 / 1 / 2 | 1.46 / 1.94 / 2.94 | 0.025 / 0.407 / 0.996 | 0 / 0 / 0.953 |
| Heavy t3 | 0.5 / 1 / 2 | 1.57 / 2.16 / 3.44 | 0.100 / 0.618 / 0.953 | 0 / 0.011 / 0.550 |
| Linear drift | 0.5 / 1 / 2 | 1.40 / 1.82 / 2.73 | 0.012 / 0.277 / 0.978 | 0 / 0 / 0.781 |
| Shared plus local | 0.5 / 1 / 2 | 1.58 / 2.13 / 2.89 | 0.075 / 0.645 / 0.991 | 0 / 0.036 / 0.919 |

At the narrow-width proxy w/σ=0.5, joint false-admission was 0 across all four models. At the wide-width proxy w/σ=2, joint missed-effect rates were 0.047, 0.450, 0.219 and 0.081, respectively. The ratio had no refusal in these cells; it has no coverage interval. For example, the shared-plus-local model at w/σ=1 had component passage 0.645 and observed joint passage 0.036. Multiplying 0.645 twelve times gives 0.005, a different answer.

**Claim admission and coverage.** Means across all models, calibration sizes, analysis sizes and widths at each effect. A rate of 1 means every counted component in the aggregated cells had that outcome.

| True effect δ/σ | False directional admission | Missed directional effect | 95% interval coverage | Expanded decision coverage | Guarded floor prediction coverage | Directional refusal | Diagnostic TOST admission | Diagnostic TOST refusal |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.000 | — | 0.565 | 0.951 | 0.999 | 1.000 | 0.052 | 0.948 |
| 2 | — | 1.000 | 0.556 | 0.948 | 0.999 | 1.000 | 0.052 | 0.947 |
| 5 | — | 0.840 | 0.565 | 0.951 | 0.999 | 0.840 | 0.000 | 0.946 |

The mean guarded floor across cells' medians was about 8.5σ with these small calibration sizes and nonzero widths; it is a future-block bound. The n=10 point-only seed-278 smoke median was 2.571σ, versus SD(mean of ten)=0.316σ, consistent with the ruling's 2.53σ and 0.31σ. The diagnostic TOST margin of 4σ is below many floor values and therefore often refuses equivalence even when the true effect is zero. Its false equivalence admission at δ=5σ was zero; its missed-equivalence rate at δ=0 was 0.948. These are not family-adjusted equivalence figures.

**Equivalence nights.** At old n=17, means over the four models. The proposed columns use Δ=3.5σ, α=0.05, variance-ratio bound B=20 and require all twelve retained captures. The current rule requires six. An m=4 night is a refusal for both rules; m=6 or 7 is a proposed-rule refusal.

| Retained m | Current PASS under no change | Proposed PASS under no change | Proposed worst-model false alarm | Refusal, both |
|---:|---:|---:|---:|---:|
| 4 | 0.000 | 0.000 | 0.000 | 1.000 |
| 6 | 0.586 | 0.000 | 0.000 | 0.000 current / 1.000 proposed |
| 7 | 0.560 | 0.000 | 0.000 | 0.000 current / 1.000 proposed |
| 12 | 0.420 | 0.995 | 0.013 | 0.000 |

For the registered candidate minimum m=12, the current rule's no-change false alarm is 0.580 on average; the proposed rule's is 0.005. At m=12 the proposed rule detects a +5σ shift in 0.978–0.998 of trials, but detects a fourfold variance increase in only 0.070–0.118. The proposed 90% mean-difference interval covers the true no-change difference in only 0.335–0.633 of m=12 cells because independent night shocks are not represented by within-night sample variance. The current rule has no interval-coverage measure.

## Interpretation

The D-165 joint verdict must be computed from shared trials. Reporting the independent marginal probability to the twelfth power changes the answer under a shared night disturbance. R follows the disclosed width and floor construction; it cannot establish that timing variation physically dominates the energy signal.

The claim gate compares a mean from n analysis blocks with a floor sized for a future block. The simulation exposes the resulting admission scale while preserving the exact production floor and the claim's Holm-adjusted admission path. The interval coverage columns reveal the separate effect of unmodeled night-wide disturbances: a within-night t interval can miss a night-level shift even when its deterministic width is included.

The existing equivalence rule's maximum-and-range comparison changes its pass probability as retained m changes. The proposed rule is sized at m=12, old n≥17; its verdict must be registered and implemented through a later gate before an actual night uses it. Its variance screen has weak power for a fourfold variance change, and the one-night t interval has poor coverage under independent night shocks. Those limits are part of the proposed rule's operating characteristics.

## Reproduction and scope

From this directory run `python3 sim.py --smoke` and `python3 sim.py --trials 30`. No model is loaded. The program uses Python's standard library and repository code from this worktree. It writes only `results/`. The numeric old-rule replay supplies synthetic already-retained rows to the real `evaluate_session`; custody authentication and observed capture-loss rates require real ledger records and are outside this experiment. The equivalence replacement is **PROPOSED**, not installed or registered. No night result or claim is made here.

The final run completed in 1:11.68 wall-clock minutes. Verification tails:

```text
$ python3 sim.py --smoke
n=10 point-only median_F=2.571 sigma; SD(mean)=0.316 sigma
w/sigma=0.50 P(R>=2)=0.000 median_F=3.767
w/sigma=0.75 P(R>=2)=0.100 median_F=4.308
w/sigma=1.00 P(R>=2)=0.412 median_F=5.007
w/sigma=1.50 P(R>=2)=0.953 median_F=6.254
w/sigma=2.00 P(R>=2)=1.000 median_F=7.537
$ python3 sim.py --trials 30
floor_claim_cells=144 trials=30
equivalence_cells=768 trials=600
results: floor_claim_cells.csv/.json equivalence_cells.csv/.json metadata.json
$ git status --short
?? docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/
```

The 0.000/0.100/0.412/0.953/1.000 seed-278 replay agrees within Monte Carlo error with the ruling's 0.00/0.11/0.41/0.94/1.00. A separate output check read 144 and 768 rows from both CSV and JSON, confirmed matching column names, and measured worst-model proposed no-change false alarm 0.0133 at old n=17, retained m=12. The magistrate owns the commit; these files remain uncommitted in this seat.
