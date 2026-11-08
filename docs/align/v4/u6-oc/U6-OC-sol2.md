# U6 operating characteristics — sol2

Synthetic-only desk report, 2026-11-07 PST (brief/branch dated 2026-11-08).
Seat: `align/2026-11-08-u6-oc-sol2`. Product-code base:
`969a730cd3ddc8c9ba8385ebfd807b004f9c2bf5`. No product code changed.

**Assessment:** the repaired rule can serve as the specified ternary diagnostic
for a **pooled, large early/late shift**, provided INCONCLUSIVE remains unresolved.
It is not adequate evidence of stability of each pair, robustness to window
dependence, or a high probability of certifying a stable calibration at the
R12 roster. Under the baseline assumptions, its no-drift PASS probability is
71.56% at the eligible-count floor and 75.71–88.91% for intact 6–8-window
calibration rosters. At the true 0.5·s_r boundary, about half the replications
avoid FAIL; at 1·s_r, the miss rate is below 0.4% in those baseline designs.
These are model-conditional synthetic results, not measurement validation.

## Authority and final-roster arithmetic

The worktree's older coordination snapshot is not the R12 authority. I read
item 214 through the **local Git object**
`3809bdd14da5882659f17dc292200d4afbbd1579:RUN_STATE.md` (the observed
`origin/main`), without fetching or following any external path. References
to candidate files below are at `969a730cd`; references to other Git objects
include their pins. Every roster input and derived count is sourced below.

| Component | Roster and source |
|---|---|
| W1 | 18 members = 4 anchors + 8 contrast runs + 6 D members: `docs/align/pilot_protocol_v4.md:107–108`. The six D rows are ordinals 5, 8, 11, 14, 17, 18; four are benign: spam seed 1 twice, bank seeds 1 and 93 once each (`:117–130`; executable `scripts/align_v4_kit.py:68–81`). Thus 2 benign executions per pair, but only 1 distinct spam seed identity and 2 bank seed identities. The W1 fit can drop ordinal 18 first (`scripts/align_v4_kit.py:1323–1325`); the membership sensitivity below uses the intact roster. |
| Default later D window | 22 members = 4 anchors + 2 spam seed-1 sentinels + 14 fresh benign (7 per pair) + 2 sabotage (1 per pair): `docs/align/pilot_protocol_v4.md:151–154`. Sentinels replay W1 ordinal 5, at ordinal 5 and the last ordinal: `6eb1ff5be:docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md:110–118`. Consequently U6 could receive 9 spam + 7 bank benign executions per intact D window if sentinels are included; only the fresh 7 + 7 count toward calibration m. |
| Calibration stop | Minimum 6 windows; stop on eligible counts only once both pairs have m≥39; hard cap 8: `3809bdd14:RUN_STATE.md:1045–1050` (R12/B3). A cap with either pair below target remains insufficient; do not top up based on U6 or scores. The existing exclusion from m of W1, sentinels, anchors and development records is `docs/align/pilot_protocol_v4.md:556–563`. |
| Intact calibration counts | Multiplying the cited per-window counts by R12's allowed window counts: 6/7/8 windows give **42/49/56 fresh benign per pair**, **84/98/112 fresh benign overall**, **6/7/8 sabotage per pair**, **12/14/16 sentinel executions**, and **24/28/32 anchors**. Total D members are **132/154/176**; with intact W1, **150/172/194**. These are planned yields before exclusions, not promises of eligible counts. |
| Attrition floor | Both pairs at **39** eligible gives **78** fresh independent trajectory IDs. The synthetic floor uses per-pair per-window counts `[7,6,7,6,7,6]` over 6 windows, totaling 39. This particular exclusion pattern is an assumption, not an authorized manifest. A fully lost window out of six leaves **35<39**, as already recorded in `docs/align/pilot_protocol_v4.md:568–574`; R12 now permits continuing by counts up to the cap. |
| Separate locked test | Required by `docs/align/pilot_protocol_v4.md:556–558`; **3 versus 6 test windows remains explicitly open** at `3809bdd14:RUN_STATE.md:1053`. No test observations are borrowed to improve this calibration OC. The old D1–D3 target of 21 benign/pair is superseded by m≥39 and R12, not reused as the final calibration size (`pilot_protocol_v4.md:153–154,556–574`). |
| Other boundaries | The conditional one-pair, 14-member fallback is not the adopted two-pair default (`pilot_protocol_v4.md:155–158`; R12 keeps the defaults, `3809bdd14:RUN_STATE.md:1051–1052`). A hard cap of 8 such alternating one-pair windows could supply at most 28 fresh benign/pair, so that fallback would not fund m≥39. D has a frozen **maximum** of 12 turns, not 12 guaranteed observed turns (`pilot_protocol_v4.md:665–672`). |

Thus R12 settles the calibration count range, but there is **no fully frozen
final fit/calibration/test manifest to certify** in these sources: test shape,
actual eligibility, observed turn lengths, U6 membership and trajectory-ID
meaning still need the lead's prospective freeze. The local kit explicitly
marks W1 as non-held-out (`scripts/align_v4_kit.py:1487–1492`); its W1 roster
does not supply a later count-stop manifest. This report enumerates the funded
default calibration shapes and brackets the U6 input ambiguity instead of
inventing a final test cohort or a D-series manifest.

## Exact rule and simulation model

The requested review pointer is the locally available object
`origin/align/2026-11-08-v4-r11-review-sol1:docs/align/squeeze/fanout/r11-review-sol1.md:45–76`.
Its U6 wiring finding predates the repair at this base. The simulation's oracle
uses the repaired `monitoring_stability_v4` route, not the legacy Welch/slope rule.

The route sorts benign **episodes within each pair across all supplied
sessions**, splits at floor(n/2), pools all per-turn observations, and clusters
by `(pair, trajectory)` (`joulewise/align/apple/thermal_desk.py:535–584`). It does
not split each window separately, average pair contrasts equally, or apply a
pairwise veto. `session_desk_evidence` concatenates supplied benign inputs
across sessions (`thermal_desk.py:477–484`). The exact estimator is:

* Δ̂ = mean(late residual turns) − mean(early residual turns).
* The SE is the **uncorrected CR0** trajectory sandwich; CI90 = Δ̂ ±1.645·SE.
* FAIL when |Δ̂| > 0.5·s_r_used, irrespective of the interval; otherwise PASS
  only when the whole CI is inside that margin. The remaining cases say
  `calibration unresolved: imprecise` and map to INCONCLUSIVE.

Source: `joulewise/align/apple/v4_estimands.py:194–228`. This asymmetry is
intentional fidelity to current code, not a new hypothesis test. There is no
small-cluster or t correction. The nominal 90% CI has only about 89% coverage
in the baseline simulations and 84.55% at a single-window roster.

`d_turn_position_means` counts distinct trajectory IDs, flags a position
evaluable only at ≥6 trajectories, and supplies no separate numeric PASS/FAIL
bar (`v4_estimands.py:231–242`). The simulator verifies these outputs; it does
not invent a position-level rejection threshold. W1's own U6 is unevaluable
(`pilot_protocol_v4.md:443–446`). Adding its records to a later pooled statistic
is an explicitly labelled membership sensitivity, not a W1 stability verdict.
The old proposed equal-pair/Welch wording remains in protocol lines 466–474;
it must not silently replace the repaired route simulated here.

**Baseline synthetic assumptions.** True per-turn s_r=1, so all magnitudes
are scale-free. For turn k of trajectory i, residual = μ_half + √ρ·Z_i +
√(1−ρ)·ε_ik, with independent standard normal terms. I use ρ=0.5 as a plausible
moderate random-intercept correlation, with ρ=0 and 0.9 sensitivities. This is
an assumption, not an estimate from any pilot or sealed outcome. Each baseline
trajectory has 3 turns; alternatives have 1, 6, or repeating lengths 1/3/6.
No observed length distribution is claimed. For equal lengths L, trajectory
mean variance v=ρ+(1−ρ)/L, and SE planning variance is approximately 2v/m when
each of two pairs contributes m trajectories. Extra turns do not create extra
trajectory clusters. Unequal lengths change the actual turn weighting.

Drift δ is a common **late-half minus early-half contrast** of 0, 0.25, 0.5,
or 1 true s_r, applied after the chronological split. It is a step experiment,
not an endpoint-to-endpoint linear slope: a linear ramp's half-mean contrast
would be about half its full-span change. Negative common shifts have the
same distribution under this symmetric model. The s_r input is fixed at
0.7, 1, or 1.3 times truth, independent of simulated residuals. This isolates
±30% systematic scale error; it does not model a stochastic fitted-scale
distribution or estimator/scale dependence.

The primary OC uses only fresh eligible benign trajectories, and conditions
on the final counts. It gives all intact 6/7/8-window endpoints and the
both-pair m=39 floor. No missingness law is known, so this is **not** an estimate
of the probability of stopping at a particular window or of reaching m≥39.
Balanced endpoint scenarios are not universal bounds for unequal retained
counts, pair-specific variances or arbitrary exclusion patterns.
It does not choose an endpoint using scores or U6, simulate repeated optional
U6 stopping, or presume score-dependent exclusions are ignorable. It also
does not refit the energy scorer: these are synthetic residual inputs, so
fit leverage, heavy tails and fitted-residual dependence remain limitations.

Membership/identity sensitivities use intact W1 + six D windows, hence
**100 benign executions** = 84 fresh + 12 sentinels + 4 W1 benign, from the
cited roster arithmetic. Distinct execution IDs yield 100 clusters. Keeping
seed identity for repeats yields **87 clusters** = 84 fresh + 1 spam seed-1
+ 2 bank development seeds. In that sensitivity the random intercept is
shared by repeated seed identity. This brackets assumptions; neither ID
contract nor repeat correlation is established by the available adapter.

Two additional stress cases add a shared window term comprising 20% of
per-turn variance, or apply +1 and −1 shifts to the two pairs. Shared window
effects are correlated across both pairs; trajectory clustering alone does
not cover them. Both stress choices are synthetic assumptions. A single-D
window scenario tests the danger of interpreting early desks as final-roster
stability judgments.

**Computation.** One run, seed 20261108, 20,000 replications for each of
18 designs (360,000 design replications). Gaussian episode sufficient
statistics give exactly the same Δ̂ and CR0 SE as expanding the turn rows.
Twenty-four deterministic comparisons check the reduction against the real
route, including shuffled inputs, repeated IDs, unequal turn counts and
non-unit scale; position counts/evaluability are also checked. All drift/scale
cells within a design share random draws. Intervals are pointwise 95% Wilson
Monte Carlo intervals, not uncertainty intervals for hardware performance
or simultaneous bounds. At p≈50%, their half-width is about 0.69 percentage
points. Rounded percentages can differ from 100 by 0.01.

## Results and error definitions

**False FAIL** means FAIL at δ=0. **Operational miss** means no FAIL
(PASS + INCONCLUSIVE) for an adverse shift. A drift of 0.25 lies inside the
true permitted margin; its no-FAIL rate is printed for completeness and is
not failure to detect an out-of-tolerance change. δ=0.5 is the boundary,
so its roughly 50% FAIL is boundary behavior, not evidence of 50% power at
an effect strictly outside the margin. **False stability** means PASS at
δ≥0.5. These distinctions matter: INCONCLUSIVE is never a stability claim.

All entries below are percentages, `estimate [95% Monte Carlo interval]`;
baseline correlation 0.5, three turns, correctly specified s_r.

| Fresh m per pair | No-drift PASS | False FAIL | No-drift imprecise | Miss at δ=1 |
|---:|---:|---:|---:|---:|
| 39 | 71.56 [70.93,72.18] | 0.72 [0.61,0.85] | 27.73 [27.11,28.35] | 0.37 [0.29,0.46] |
| 42 (6 intact windows) | 75.71 [75.11,76.30] | 0.53 [0.43,0.64] | 23.77 [23.18,24.36] | 0.22 [0.16,0.30] |
| 49 (7) | 84.47 [83.97,84.97] | 0.24 [0.18,0.32] | 15.29 [14.79,15.79] | 0.14 [0.10,0.20] |
| 56 (8) | 88.91 [88.46,89.33] | 0.16 [0.11,0.23] | 10.94 [10.51,11.38] | 0.07 [0.05,0.12] |

At six intact windows, δ=0.25 gives PASS 40.52%, FAIL 8.23%, and imprecise
51.25%. At δ=0.5, PASS is 5.39% [5.09,5.72], FAIL 50.30% [49.60,50.99],
imprecise 44.31% [43.62,45.00], and operational miss 49.70% [49.01,50.40].
Thus a permitted small shift can still cost a detection-rate claim under the
point-based FAIL consequence; this is not a formal 5%-level test of equivalence.

Scale error materially changes the conclusion. At six windows, using 0.7·s_r
makes no-drift imprecision 68.17% [67.52,68.81] and false FAIL 5.08%
[4.78,5.39]. Using 1.3·s_r lowers no-drift imprecision to 4.58%
[4.29,4.87], but at true δ=0.5 it produces false stability 21.65%
[21.09,22.23] and operational miss 79.22% [78.66,79.78]. Its miss rate at
δ=1 is 2.51% [2.30,2.74]. More trajectories cannot repair a persistently
wrong margin: with a 30% inflated s_r, a true shift of 0.5 is eventually
inside the used margin of 0.65. The full ±30% results at all four count
designs are quoted below; correlation sensitivities at the real roster use
correct s_r rather than a full correlation-by-scale factorial.

Within-trajectory dependence matters even with correct clustering: at six
windows, zero drift is imprecise 2.07% [1.88,2.27] for ρ=0, versus 44.20%
[43.51,44.89] for ρ=0.9. At eight windows, those rates are 0.27%
[0.21,0.36] and 26.73% [26.12,27.35]. At ρ=0.5, changing from three to one
turn raises six-window imprecision to 47.66% [46.97,48.35]; six turns lowers
it to 16.47% [15.96,16.99]. Mixed 1/3/6 lengths give 41.66%
[40.97,42.34] imprecise: long correlated trajectories get more turn weight.

Including all W1/D6 benign records improves no-drift PASS to 84.91%
[84.41,85.40] with independent execution IDs, or 88.66% [88.21,89.09] with
the synthetic shared-seed intercept. Corresponding imprecision remains
14.88% [14.39,15.37] or 11.21% [10.78,11.65]. These are **not** extra
held-out calibration units and do not settle which input contract is correct.

The shared-window stress yields 20.71% [20.15,21.28] FAIL with zero
systematic drift, 53.94% [53.24,54.62] coverage for the population half
contrast, and 10.29% [9.88,10.72] miss at δ=1. Conditional on realized
windows, some FAILs reflect genuine random offsets, so the zero-systematic-
drift result is not automatically a false alarm about the realized series.
It does show why the independence assumption and target of the interval
must be explicit. Increasing trajectory counts inside the same windows
does not create independent window information.

Opposite ±1 shifts have true pooled contrast zero. They yield PASS 48.10%
[47.41,48.80], FAIL 0.46% [0.38,0.57], and no FAIL 99.53%
[99.43,99.62]. This is cancellation under the current pooled estimand,
not a bug in its SE. It cannot certify both pairs separately. The single-
window calculation is also unsuitable for a final stability claim: no-drift
FAIL is 26.11% [25.50,26.72] and imprecision 72.52% [71.89,73.13]. U6 is
not a window-admission gate (`pilot_protocol_v4.md:497–505`); do not use
those early outcomes to replace R12's count-only stop.

## Prospective recommendation (no rule or cap changed)

1. **At R12's existing cap, retain the explicit unresolved outcome and narrow
   the claim.** The repaired rule is useful for large common pooled drift;
   it is no longer mathematically destined to be imprecise. Nevertheless,
   a strong expectation of a no-drift PASS, or a statement that each pair is
   stable, is not funded. Freeze the input membership, persistent trajectory
   IDs, per-turn s_r definition and half convention before W1. Print per-pair
   contrasts/intervals alongside the pooled statistic. A new pairwise veto
   would require prospective authority and its own OC; it is not installed here.

2. **If the desired operating target is ≥95% no-drift PASS**, this is a new
   explicit planning objective, not a previously registered requirement.
   For independent equal-length trajectories the approximation is
   `m_per_pair >= ceil(2*v*((1.645+1.959964)/(0.5*scale))**2)`.
   At three turns and ρ=0.5, m≥70/pair, or 10 intact default windows, gives
   simulated PASS **95.49% [95.19,95.77]**, false FAIL **0.02% [0.01,0.05]**,
   and imprecision **4.49% [4.21,4.79]**. At ρ=0.9 with correct scale the
   formula requires m≥98/pair (14 intact windows; planning arithmetic only).
   If the scale can be underestimated by 30%, baseline correlation needs
   m≥142/pair (21 intact windows); high correlation needs m≥199/pair.
   Rounding the latter to 29 intact windows gives m=203/pair and simulated
   PASS **95.16% [94.85,95.44]**. That interval does not establish a strict
   ≥95% lower confidence guarantee. These larger designs are demonstrations,
   **outside R12 authority**, and do not solve scale overestimation, window
   dependence or pair cancellation. Prefer resolving the scale/dependence
   contract to automatically spending that many windows.

3. **Do not widen ±0.5·s_r just to force PASS, or chase a boundary shift with
   sample size.** With correct scale the current point-based FAIL probability
   at exactly δ=0.5 stays about 50% even in the 10-window simulation. No sample
   size makes it a ≥90%-power detector of its own boundary. If reliable
   detection of shifts inside/at that boundary is the goal, change the target
   margin/decision rule prospectively and rerun OC. If shared window effects
   are material, a window-aware interval/estimand and sufficient independent
   windows need separate prospective design; trajectory-only sample sizing
   is inadequate. Neither a replacement critical value nor a new veto is
   silently adopted by this report.

## Execution and handoff

Only `simulate_u6_sol2.py` and this report were added. Coordination state,
product files, raw evidence and generated registration artifacts were not
edited. M0/stop-card/workspace/orchestration intake completed; active stop
card was NONE. The explicit brief owns selection and forbids coordination
writes, network, full-suite and measurement work. No subagents or consults
were launched; the other seat remains independent.

Commands and results (separate targeted unittest invocations):

* `python3.13 -B -m unittest tests.align.test_v4_estimands` — **15 tests, OK**, 0.002 s.
* `python3.13 -B -m unittest tests.align.test_thermal_desk` — **25 tests, OK**, 2.145 s.
* `python3.13 -B docs/align/v4/u6-oc/simulate_u6_sol2.py > /private/tmp/u6-oc-sol2-output.txt`
  — **one Monte Carlo run, exit 0**, including the 24 route comparisons.
* Final syntax compilation of the new script, output-transcription checks
  and `git diff --check` — passed (see local commit containing this report).

Full suite was not run, as instructed; targeted unittest time was 2.147 s.
No native MLX tests, model downloads, hardware probes, real measurement reads,
Block-5 pipeline or network calls ran. No native test is needed to execute
this stdlib simulation. The broader W1 native/cache/thermal qualification is
still the lead's clean-machine work; this result does not replace it.

Script SHA-256: `d29b0fba046f414b395ae41b9fe85a5ada7852cac0b91e7d15cdc3b36bc65558`.
Quoted stdout SHA-256 (including its final newline):
`a5a8840eb0816f9e8869bfe855bb679c3ee09c55d1b0be81899839f4eae08160`.
The stdout is quoted verbatim below; it is reproducible with the command above
on Python 3.13.18, with no input files or optional packages. This commit is
local only; nothing is pushed.

**Next exact step:** the lead compares the independent seat reports, freezes
the remaining U6 membership/ID/scale and final series/test manifest choices,
and decides whether the existing unresolved rate is acceptable or a
prospective sample/estimand change is justified before W1 registration.
Uncertainties are the residual/correlation/length law, window dependence,
scale estimation, exclusion process, fit-induced dependence, and the named
unfrozen contracts. None was learned from sealed outcomes.

## Verbatim output of the single run

```text
U6 synthetic OC sol2; Python 3.13.18; stdlib only; seed=20261108; N=20000
s_r_true=1; drift=late-minus-early half contrast; scale=s_r_used/s_r_true
Wilson 95% pointwise Monte Carlo intervals; NO_FAIL=PASS+IMPRECISE (miss for adverse drift only)
ORACLE: 24 route comparisons + position counts/evaluability OK

D6_m42: episodes=84, clusters=84, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 0.70 | 26.75[26.14,27.37] 5.08[4.78,5.39] 68.17[67.52,68.81] 94.92[94.61,95.22]
0.00 1.00 | 75.71[75.11,76.30] 0.53[0.43,0.64] 23.77[23.18,24.36] 99.48[99.36,99.57]
0.00 1.30 | 95.41[95.11,95.69] 0.01[0.01,0.04] 4.58[4.29,4.87] 99.98[99.96,99.99]
0.25 0.70 | 10.44[10.02,10.87] 29.27[28.64,29.90] 60.30[59.61,60.97] 70.73[70.10,71.36]
0.25 1.00 | 40.52[39.84,41.20] 8.23[7.86,8.62] 51.25[50.56,51.94] 91.77[91.38,92.14]
0.25 1.30 | 72.66[72.03,73.27] 1.34[1.19,1.51] 26.00[25.40,26.61] 98.66[98.49,98.81]
0.50 0.70 | 0.66[0.55,0.78] 80.30[79.74,80.85] 19.05[18.51,19.60] 19.70[19.15,20.26]
0.50 1.00 | 5.39[5.09,5.72] 50.30[49.60,50.99] 44.31[43.62,45.00] 49.70[49.01,50.40]
0.50 1.30 | 21.65[21.09,22.23] 20.77[20.22,21.34] 57.57[56.88,58.25] 79.22[78.66,79.78]
1.00 0.70 | 0.00[0.00,0.02] 99.99[99.96,100.00] 0.01[0.00,0.04] 0.01[0.00,0.04]
1.00 1.00 | 0.00[0.00,0.02] 99.78[99.70,99.84] 0.22[0.16,0.30] 0.22[0.16,0.30]
1.00 1.30 | 0.01[0.00,0.04] 97.49[97.26,97.70] 2.50[2.29,2.73] 2.51[2.30,2.74]
CI90 coverage of true pooled contrast: 88.94[88.50,89.37]%

D7_m49: episodes=98, clusters=98, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 0.70 | 37.99[37.32,38.66] 3.25[3.01,3.50] 58.76[58.08,59.44] 96.75[96.50,96.99]
0.00 1.00 | 84.47[83.97,84.97] 0.24[0.18,0.32] 15.29[14.79,15.79] 99.76[99.68,99.82]
0.00 1.30 | 97.89[97.69,98.08] 0.01[0.00,0.03] 2.10[1.91,2.31] 100.00[99.97,100.00]
0.25 0.70 | 12.86[12.40,13.33] 27.28[26.67,27.90] 59.86[59.18,60.54] 72.72[72.10,73.33]
0.25 1.00 | 44.89[44.20,45.58] 6.35[6.02,6.70] 48.76[48.07,49.45] 93.65[93.30,93.98]
0.25 1.30 | 78.95[78.38,79.51] 0.78[0.67,0.91] 20.27[19.71,20.83] 99.22[99.09,99.33]
0.50 0.70 | 0.58[0.49,0.70] 82.09[81.55,82.62] 17.32[16.81,17.86] 17.91[17.38,18.45]
0.50 1.00 | 5.24[4.93,5.55] 50.35[49.66,51.04] 44.41[43.73,45.10] 49.65[48.96,50.34]
0.50 1.30 | 23.74[23.16,24.33] 18.08[17.55,18.62] 58.18[57.49,58.86] 81.92[81.38,82.45]
1.00 0.70 | 0.00[0.00,0.02] 100.00[99.98,100.00] 0.00[0.00,0.02] 0.00[0.00,0.02]
1.00 1.00 | 0.00[0.00,0.02] 99.86[99.80,99.90] 0.14[0.10,0.20] 0.14[0.10,0.20]
1.00 1.30 | 0.01[0.00,0.03] 98.36[98.17,98.53] 1.64[1.47,1.82] 1.64[1.47,1.83]
CI90 coverage of true pooled contrast: 89.57[89.14,89.99]%

D8_m56: episodes=112, clusters=112, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 0.70 | 47.70[47.01,48.40] 2.38[2.18,2.60] 49.91[49.22,50.61] 97.62[97.40,97.82]
0.00 1.00 | 88.91[88.46,89.33] 0.16[0.11,0.23] 10.94[10.51,11.38] 99.84[99.77,99.89]
0.00 1.30 | 99.01[98.86,99.14] 0.00[0.00,0.02] 0.99[0.86,1.14] 100.00[99.98,100.00]
0.25 0.70 | 15.65[15.15,16.16] 25.60[25.00,26.21] 58.76[58.07,59.44] 74.40[73.79,75.00]
0.25 1.00 | 49.79[49.10,50.48] 5.08[4.78,5.39] 45.13[44.44,45.82] 94.92[94.61,95.22]
0.25 1.30 | 83.14[82.62,83.66] 0.45[0.37,0.55] 16.41[15.90,16.92] 99.55[99.45,99.63]
0.50 0.70 | 0.49[0.40,0.60] 83.02[82.49,83.53] 16.50[15.99,17.02] 16.98[16.47,17.51]
0.50 1.00 | 5.76[5.45,6.10] 49.99[49.30,50.68] 44.25[43.56,44.93] 50.01[49.32,50.70]
0.50 1.30 | 26.02[25.41,26.63] 16.29[15.78,16.80] 57.70[57.01,58.38] 83.71[83.20,84.22]
1.00 0.70 | 0.00[0.00,0.02] 100.00[99.98,100.00] 0.00[0.00,0.02] 0.00[0.00,0.02]
1.00 1.00 | 0.00[0.00,0.02] 99.92[99.88,99.95] 0.07[0.05,0.12] 0.07[0.05,0.12]
1.00 1.30 | 0.01[0.00,0.03] 98.76[98.59,98.90] 1.24[1.10,1.40] 1.24[1.10,1.41]
CI90 coverage of true pooled contrast: 89.03[88.58,89.45]%

eligible_floor_m39: episodes=78, clusters=78, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 0.70 | 21.13[20.57,21.70] 5.92[5.60,6.25] 72.95[72.34,73.57] 94.08[93.75,94.40]
0.00 1.00 | 71.56[70.93,72.18] 0.72[0.61,0.85] 27.73[27.11,28.35] 99.28[99.15,99.39]
0.00 1.30 | 93.93[93.59,94.25] 0.03[0.01,0.06] 6.04[5.72,6.38] 99.98[99.94,99.99]
0.25 0.70 | 9.03[8.64,9.44] 29.05[28.43,29.69] 61.91[61.24,62.59] 70.95[70.31,71.57]
0.25 1.00 | 39.41[38.73,40.09] 8.68[8.30,9.08] 51.91[51.22,52.60] 91.32[90.92,91.70]
0.25 1.30 | 70.88[70.24,71.50] 1.64[1.47,1.82] 27.49[26.88,28.11] 98.37[98.18,98.53]
0.50 0.70 | 0.73[0.62,0.86] 78.78[78.21,79.34] 20.49[19.94,21.06] 21.22[20.66,21.79]
0.50 1.00 | 5.61[5.30,5.94] 49.25[48.56,49.95] 45.13[44.45,45.83] 50.74[50.05,51.44]
0.50 1.30 | 21.62[21.05,22.20] 20.52[19.97,21.09] 57.86[57.17,58.54] 79.48[78.91,80.03]
1.00 0.70 | 0.00[0.00,0.02] 99.99[99.96,100.00] 0.01[0.00,0.04] 0.01[0.00,0.04]
1.00 1.00 | 0.00[0.00,0.02] 99.63[99.54,99.71] 0.37[0.29,0.46] 0.37[0.29,0.46]
1.00 1.30 | 0.01[0.01,0.04] 96.98[96.73,97.21] 3.00[2.78,3.25] 3.02[2.79,3.27]
CI90 coverage of true pooled contrast: 88.98[88.54,89.41]%

D6_rho0: episodes=84, clusters=84, rho=0.0, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 97.92[97.72,98.11] 0.01[0.00,0.04] 2.07[1.88,2.27] 99.99[99.96,100.00]
0.25 1.00 | 64.16[63.49,64.82] 2.44[2.23,2.66] 33.41[32.76,34.07] 97.56[97.34,97.77]
0.50 1.00 | 5.64[5.33,5.97] 49.73[49.04,50.43] 44.62[43.93,45.31] 50.27[49.57,50.96]
1.00 1.00 | 0.00[0.00,0.02] 99.99[99.96,100.00] 0.01[0.00,0.04] 0.01[0.00,0.04]
CI90 coverage of true pooled contrast: 88.88[88.44,89.31]%

D6_rho09: episodes=84, clusters=84, rho=0.9, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 54.06[53.37,54.75] 1.74[1.56,1.93] 44.20[43.51,44.89] 98.27[98.07,98.44]
0.25 1.00 | 30.19[29.56,30.83] 11.92[11.47,12.37] 57.89[57.21,58.58] 88.09[87.63,88.53]
0.50 1.00 | 5.50[5.20,5.83] 50.36[49.66,51.05] 44.14[43.45,44.83] 49.65[48.95,50.34]
1.00 1.00 | 0.00[0.00,0.02] 99.11[98.97,99.23] 0.89[0.77,1.03] 0.89[0.77,1.03]
CI90 coverage of true pooled contrast: 89.07[88.62,89.49]%

D8_rho0: episodes=112, clusters=112, rho=0.0, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 99.72[99.64,99.79] 0.00[0.00,0.02] 0.27[0.21,0.36] 100.00[99.98,100.00]
0.25 1.00 | 74.66[74.05,75.25] 1.04[0.91,1.20] 24.30[23.71,24.90] 98.95[98.80,99.09]
0.50 1.00 | 5.47[5.16,5.79] 49.63[48.94,50.32] 44.90[44.21,45.59] 50.37[49.68,51.06]
1.00 1.00 | 0.00[0.00,0.02] 100.00[99.98,100.00] 0.00[0.00,0.02] 0.00[0.00,0.02]
CI90 coverage of true pooled contrast: 89.00[88.56,89.43]%

D8_rho09: episodes=112, clusters=112, rho=0.9, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 72.69[72.06,73.30] 0.58[0.49,0.70] 26.73[26.12,27.35] 99.41[99.30,99.51]
0.25 1.00 | 39.62[38.94,40.30] 8.38[8.00,8.77] 52.00[51.31,52.69] 91.62[91.23,92.00]
0.50 1.00 | 5.62[5.30,5.94] 49.48[48.79,50.17] 44.91[44.22,45.60] 50.52[49.83,51.21]
1.00 1.00 | 0.00[0.00,0.02] 99.69[99.60,99.76] 0.31[0.24,0.40] 0.31[0.24,0.40]
CI90 coverage of true pooled contrast: 89.30[88.86,89.72]%

D6_one_turn: episodes=84, clusters=84, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 50.12[49.43,50.82] 2.21[2.02,2.43] 47.66[46.97,48.35] 97.78[97.57,97.98]
0.25 1.00 | 27.68[27.07,28.31] 12.34[11.89,12.80] 59.98[59.30,60.66] 87.67[87.20,88.11]
0.50 1.00 | 5.44[5.13,5.76] 50.18[49.49,50.87] 44.38[43.69,45.07] 49.82[49.13,50.51]
1.00 1.00 | 0.01[0.00,0.03] 98.84[98.69,98.98] 1.15[1.01,1.31] 1.16[1.02,1.31]
CI90 coverage of true pooled contrast: 89.20[88.77,89.63]%

D6_six_turns: episodes=84, clusters=84, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 83.34[82.81,83.85] 0.19[0.14,0.27] 16.47[15.96,16.99] 99.80[99.73,99.86]
0.25 1.00 | 44.80[44.12,45.50] 6.35[6.02,6.70] 48.84[48.15,49.54] 93.65[93.30,93.98]
0.50 1.00 | 5.15[4.85,5.47] 49.95[49.26,50.65] 44.90[44.21,45.59] 50.04[49.35,50.74]
1.00 1.00 | 0.00[0.00,0.02] 99.90[99.85,99.94] 0.10[0.06,0.15] 0.10[0.06,0.15]
CI90 coverage of true pooled contrast: 89.55[89.12,89.97]%

D6_mixed_lengths_1_3_6: episodes=84, clusters=84, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 56.88[56.19,57.56] 1.47[1.31,1.65] 41.66[40.97,42.34] 98.53[98.35,98.69]
0.25 1.00 | 32.57[31.92,33.22] 11.63[11.20,12.09] 55.79[55.11,56.48] 88.37[87.91,88.80]
0.50 1.00 | 5.99[5.66,6.32] 50.20[49.50,50.89] 43.82[43.13,44.51] 49.80[49.11,50.50]
1.00 1.00 | 0.01[0.00,0.03] 99.16[99.02,99.27] 0.84[0.72,0.98] 0.84[0.73,0.98]
CI90 coverage of true pooled contrast: 88.28[87.83,88.72]%

D_single_window: episodes=14, clusters=14, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 1.38[1.23,1.55] 26.11[25.50,26.72] 72.52[71.89,73.13] 73.89[73.28,74.50]
0.25 1.00 | 1.25[1.11,1.41] 32.41[31.76,33.06] 66.34[65.68,66.99] 67.59[66.94,68.24]
0.50 1.00 | 0.71[0.61,0.84] 50.59[49.90,51.28] 48.70[48.00,49.39] 49.41[48.72,50.10]
1.00 1.00 | 0.17[0.12,0.23] 86.59[86.11,87.06] 13.25[12.78,13.72] 13.41[12.94,13.89]
CI90 coverage of true pooled contrast: 84.55[84.04,85.04]%

W1_D6_all_benign_episode_ids: episodes=100, clusters=100, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 84.91[84.41,85.40] 0.21[0.16,0.29] 14.88[14.39,15.37] 99.78[99.71,99.84]
0.25 1.00 | 46.42[45.73,47.11] 6.30[5.97,6.64] 47.28[46.59,47.98] 93.70[93.36,94.03]
0.50 1.00 | 5.18[4.89,5.50] 49.66[48.96,50.35] 45.16[44.47,45.85] 50.34[49.65,51.04]
1.00 1.00 | 0.00[0.00,0.02] 99.89[99.84,99.93] 0.10[0.07,0.16] 0.10[0.07,0.16]
CI90 coverage of true pooled contrast: 89.55[89.12,89.97]%

W1_D6_all_benign_seed_ids: episodes=100, clusters=87, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 88.66[88.21,89.09] 0.14[0.09,0.20] 11.21[10.78,11.65] 99.87[99.80,99.91]
0.25 1.00 | 49.20[48.51,49.90] 5.34[5.04,5.67] 45.45[44.76,46.14] 94.66[94.33,94.96]
0.50 1.00 | 4.86[4.57,5.16] 50.06[49.37,50.75] 45.08[44.40,45.78] 49.94[49.25,50.63]
1.00 1.00 | 0.00[0.00,0.02] 99.94[99.90,99.97] 0.06[0.03,0.10] 0.06[0.03,0.10]
CI90 coverage of true pooled contrast: 90.05[89.63,90.46]%

D6_shared_window_stress: episodes=84, clusters=84, rho=0.5, window_share=0.2
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 40.68[40.00,41.36] 20.71[20.15,21.28] 38.61[37.94,39.29] 79.29[78.72,79.85]
0.25 1.00 | 34.81[34.15,35.47] 28.64[28.02,29.27] 36.55[35.89,37.22] 71.36[70.73,71.98]
0.50 1.00 | 19.74[19.20,20.30] 50.06[49.37,50.75] 30.20[29.56,30.84] 49.94[49.25,50.63]
1.00 1.00 | 2.09[1.90,2.30] 89.71[89.28,90.12] 8.20[7.83,8.59] 10.29[9.88,10.72]
CI90 coverage of true pooled contrast: 53.94[53.24,54.62]%

D6_opposite_pair_drifts_plus_minus_1: episodes=84, clusters=84, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
1.00 1.00 | 48.10[47.41,48.80] 0.46[0.38,0.57] 51.43[50.74,52.12] 99.53[99.43,99.62]
CI90 coverage of true pooled contrast: 96.66[96.40,96.90]%

PROPOSED_10_windows_m70: episodes=140, clusters=140, rho=0.5, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 1.00 | 95.49[95.19,95.77] 0.02[0.01,0.05] 4.49[4.21,4.79] 99.98[99.95,99.99]
0.25 1.00 | 56.88[56.20,57.57] 3.31[3.08,3.57] 39.80[39.12,40.48] 96.69[96.43,96.92]
0.50 1.00 | 5.04[4.74,5.35] 50.33[49.64,51.03] 44.63[43.94,45.32] 49.66[48.97,50.36]
1.00 1.00 | 0.00[0.00,0.02] 100.00[99.98,100.00] 0.00[0.00,0.02] 0.00[0.00,0.02]
CI90 coverage of true pooled contrast: 90.08[89.65,90.48]%

PROPOSED_29_windows_m203_worst_scale: episodes=406, clusters=406, rho=0.9, window_share=0.0
drift scale | PASS%[95%MC] FAIL%[95%MC] IMPRECISE%[95%MC] NO_FAIL%[95%MC]
0.00 0.70 | 95.16[94.85,95.44] 0.02[0.01,0.05] 4.83[4.54,5.13] 99.98[99.95,99.99]
0.25 0.70 | 27.61[26.99,28.23] 14.67[14.18,15.16] 57.73[57.04,58.41] 85.34[84.84,85.82]
0.50 0.70 | 0.06[0.03,0.10] 93.88[93.54,94.20] 6.06[5.74,6.40] 6.12[5.80,6.46]
1.00 0.70 | 0.00[0.00,0.02] 100.00[99.98,100.00] 0.00[0.00,0.02] 0.00[0.00,0.02]
CI90 coverage of true pooled contrast: 89.64[89.21,90.05]%

Normal planning formula for 95% null PASS: m_per_pair >= ceil(2*v*((1.645+z.975)/(.5*scale))**2).
rho=0.5, scale=1.0: m>=70/pair, round to 10 intact default windows
rho=0.9, scale=1.0: m>=98/pair, round to 14 intact default windows
rho=0.5, scale=0.7: m>=142/pair, round to 21 intact default windows
rho=0.9, scale=0.7: m>=199/pair, round to 29 intact default windows
```
