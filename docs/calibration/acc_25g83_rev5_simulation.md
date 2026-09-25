# 25G83 registration Revision 5 desk simulation (2026-09-25)

Authority: ACCEPTANCE-25G83-02 final texts §5 R5(k), R10. Replay: `python3 scripts/sim_acc_25g83_rev5.py --trials 200`; seed 25098312. This is a desk simulation, not live capture or acceptance issuance.

Each trial draws 24 prospective B values under one of four models, assigns validity independently at 30/38 (the Interactive-context yield used in the prior desk design), and follows the registered path: W1 count-only futility at fewer than 6 valid, W2, and count-only W3 only when W1+W2 have fewer than 12 valid. Every valid member is retained. The script uses issuer corpus statistics, quantiles, floored S, and C=max(predecessor C,Q99,S), and projects the production bracket allowance through the issued r7 reference. It tests a zero true contrast with an observed timing artifact of 80% of the bracket bound. Gaussian, heavy-tailed with two fixed 0.15 s additions in 24 slots, serial AR(1), and block drift in both 12-slot blocks are run. A later bracket draw supplies the level-screen probe. No equivalence branch exists.

| Model | W1 futility | W3 | Excursion-limited | Zero headroom | Later level-screen refusal (exact 95% interval) | Bracket pass | Floor pass | Decision interval pass | False admission |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Gaussian | 1/200 | 0/200 | 0/200 | 196/200 | 10/200, 5.0% (2.42–9.00%) | 189/200 | 0/200 | 0/200 | 0/200 |
| Heavy-tailed, two excursions | 1/200 | 0/200 | 118/200 | 72/200 | 9/200, 4.5% (2.08–8.37%) | 190/200 | 0/200 | 0/200 | 0/200 |
| Serially dependent AR(1) | 0/200 | 0/200 | 0/200 | 195/200 | 6/200, 3.0% (1.11–6.42%) | 194/200 | 0/200 | 0/200 | 0/200 |
| Block drift, both blocks | 1/200 | 0/200 | 0/200 | 0/200 | 22/200, 11.0% (7.02–16.18%) | 177/200 | 0/200 | 0/200 | 0/200 |

For each 0/200 false-admission cell, the exact one-sided 95% binomial upper bound is `1 − 0.05^(1/200) = 1.4867%`, conventionally ≤1.5%. The level-screen intervals are exact two-sided Clopper-Pearson bounds, inverted from binomial tails by the replay script. Rates are per all 200 planned trials, including stopped trials. Level-screen refusal is a prospective later-bracket probe on trials reaching derivation; the numerator above is divided by all 200 for the table, so it is a lower bound on the conditional refusal rate. The W3 branch was present but did not fire at this assumed valid yield. A zero observed false-admission count is not a release criterion. Any non-zero admission through the bracket, false-effect floor, or decision-interval gates reopens council review.

The simulation covers these specified models and one yield assumption; it cannot establish independence of real captures, live Interactive cadence, or the actual post-merge acceptance. W1's cadence stop is separately governed by the raw-plist report; this desk draw does not synthesize launchd or powermetrics records.

A separate yield stress replay, `python3 scripts/sim_acc_25g83_rev5.py --trials 200 --valid-probability 0.5`, exercises the W3 branch without changing any B model. W1 futility counts were 71, 81, 85, 82; count-only W3 openings were 25, 19, 24, 23 for Gaussian, heavy-tailed, serial and block-drift respectively. All four had zero shortfalls after W3 and zero false admissions; each 0/200 admission still has the ≤1.5% one-sided bound. This 50% yield is a stress case, not a prediction for Interactive captures.
