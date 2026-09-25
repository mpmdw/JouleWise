# R-ACC-2(k): v4 acceptance-size desk simulation

This extends the R-Q4(a) simulation in this directory to compare a prospective 12-member acceptance corpus with 19 members. It is a seeded desk calculation, not a v4 capture, an issued artifact, or a live claim. The 24 synthetic B values represent two 12-slot windows under the proposed 2 s v4 pulse. The script does not replay pulse interiors or capture validity; those have a separate gate in ruling 1(b). No existing trace-19 result is changed.

For each model and n, 200 trials construct an acceptance screen and a zero-true-effect claim. A later bracket PRE and POST have 1 ms Gaussian difference. The apparent claim effect is 80% of the bracket's timing allowance multiplied by a 33 W power step, plus 0.30 J independent block noise; the true energy contrast is zero. A separate 10,000-trial sample estimates the chance that a later PRE exceeds the corpus maximum (the level-screen refusal rate). The two samples have fixed, separate seeds.

The four B models are:

| Model | Synthetic B process |
|---|---|
| Gaussian | Independent normal values, mean 0.030 s, SD 0.002 s. |
| Heavy excursions | The same base values, with exactly two 0.15 s additions at slots 6 and 18 of 24. A later observation has 2/24 excursion probability. Members are retained regardless of B. |
| Serial AR(1) | Normal innovations with lag-one correlation 0.8 and stationary SD 0.002 s. The later observation continues the series. |
| Block drift | First 12 slots have −0.004 s and second 12 have +0.004 s shifts around 0.030 s, with SD 0.0015 s. The later observation stays in the high block. |

The production issuer supplies Decimal corpus statistics, the two-draw Q99, quantized range, S=max(range, 0.010818 s), and the predecessor/Q99 ceiling. The script applies the ruled changes C=max(predecessor C, Q99, S), zero headroom when C=S, no B-based exclusion, `excursion_limited` at two members above 0.075 s, and issuance refusal above 0.25 s. It does not invoke the current CLI for n=12: that CLI still hard-codes n=19 and strict S<C. The production bracket's issued r7 allowance projection is called to check its single-embedding max(drift,S) rule, while the simulated v4 screen and ceiling are projected from the issuer values. The production comparative floor, paired estimator, decision interval, and five-outcome claim gate decide the claim. The simulated bracket passes only if the later PRE is at or below the level screen and drift is at or below C. The r6 predecessor screen challenge is diagnostic only, as ruled in 2(g).

## Verdict table

False admission is a `direction_supported` claim after the bracket, floor, and decision-interval gates. Rates below are observed counts; zero in 200 trials is not a mathematical zero-risk guarantee. The level-screen denominator is 10,000 independent simulated futures for each row.

| Model | n | False admission | Later level-screen refusal |
|---|---:|---:|---:|
| Gaussian | 12 | 0/200 (0.0%) | 778/10,000 (7.78%) |
| Gaussian | 19 | 0/200 (0.0%) | 568/10,000 (5.68%) |
| Heavy excursions | 12 | 0/200 (0.0%) | 445/10,000 (4.45%) |
| Heavy excursions | 19 | 0/200 (0.0%) | 307/10,000 (3.07%) |
| Serial AR(1) | 12 | 0/200 (0.0%) | 1,807/10,000 (18.07%) |
| Serial AR(1) | 19 | 0/200 (0.0%) | 1,165/10,000 (11.65%) |
| Block drift | 12 | 0/200 (0.0%) | 9,992/10,000 (99.92%) |
| Block drift | 19 | 0/200 (0.0%) | 1,273/10,000 (12.73%) |

**admission zero: YES** (in the specified finite simulation). The ruling's reference rates 1/(n+1) are 7.69% at n=12 and 5.00% at n=19. They apply to exchangeable continuous observations; the Gaussian estimates are close within Monte Carlo variation. Fixed excursion positions, serial dependence, and a later high-drift block violate that premise, so their level-screen rates need not match the reference. In particular, n=12 sees only the low block in the drift model, making almost every later high-block observation fail the level screen. This is a yield concern, even though no false claim passed the simulated gates.

Across the 200 claim trials per row, every corpus was issuable under the >0.25 s rule. The n=19 heavy-excursion corpora were all labelled `excursion_limited`; n=12 contained one excursion and was never so labelled. No modeled apparent claim cleared either the guarded floor or the decision interval. `results_acc_n12/verdict.csv` and `.json` preserve the gate counts, zero-headroom counts, seeds, and rates.

Reproduce from the repository root with `PYTHONDONTWRITEBYTECODE=1 python3 docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/sim_acc_n12.py --trials 200 --screen-trials 10000`. The script writes only `results_acc_n12/`. Because rev 4 and its issuer/bracket changes are not yet installed, this is a numerical precondition study, not end-to-end artifact authentication. Once those changes land, the lead should run the live issuer and bracket path before treating a v4 acceptance artifact as claim eligible.
