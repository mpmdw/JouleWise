# R22-2 structural replacements — synthetic qualification, Sol1

Branch: `align/2026-11-08-r22-sim-sol`; base `09d7b3c7fc5aecd74ffe7b24eeb36ef5377c3bf8`.
**SYNTHETIC ONLY / PROVISIONAL.** This report qualifies a proposed rule, not
hardware, the live scorer, actual exclusion rates, or a registration change.
R22-2 and the relative-SD priors are taken only from the task-authorized Git
text `origin/main:RUN_STATE.md` item 234 at `e9b94bd400a384db8cba42fcfba76cb6330d2fc0`.
The task's sealed-data restrictions override any unsealing language in that
historical text. No measurement data or outcome report is a simulation input.

**Intake disclosure:** the Git excerpt around item 234 inadvertently included
adjacent item 232, a numerical Block 5 result summary. No underlying
measurement path or result document was opened, and those values are not
used or reproduced in this study. Only the task-authorized R22-5 priors enter
the model. This session therefore cannot claim complete outcome blindness;
a fresh blind replication is appropriate if the lead requires that standard.

**Finding: R22-2 improves yield and maximum-rule FPR in the hot-state stress cases, but structural blindness alone does not preserve the no-bar oracle threshold.** With hot-correlated bars at q=.25, e=.10, tau=.5 s_r and no trend, R22 maximum FPR is 4.040% [4.017,4.063] versus oracle 2.321% [2.309,2.333], no-replacement 4.438% [4.409,4.467], and old count stop 4.636% [4.606,4.666]. The paired threshold shift is −.221 s_r [−.224,−.217]. Applying the same gate to future tests changes R22 FPR to 2.245% [2.231,2.260], a different target population. A .75 s_r frozen margin is the smallest tested repair to oracle-level mean FPR across this grid; nominal-target repair needs the separately qualified larger candidate below. The current C10 cap qualifies only 88.049%/52.559% of studies at q=1/8 or 1/4 and e=.10.

## Model and comparisons

The earlier [B3 Sol1 simulator](simulate_sol1.py) supplies rank arithmetic,
Gaussian tail integration, exact member-count probabilities, and Monte Carlo
interval helpers. The roster remains seven assigned fresh benign members per
pair per window, with separate thresholds for `spam_filter_update` and
`bank_transfer_2`. The roster/rank authority and limitations are documented
in [B3-SIM-sol1.md](B3-SIM-sol1.md), citing `pilot_protocol_v4.md:151,542–591`
and `joulewise/align/apple/v4_estimands.py:75`. No fit, sabotage, W1, anchor,
sentinel or development member contributes to m. Fresh benign C9/C10 members
count in place of a barred window; there are no ad hoc member top-ups.

There are ten potential calibration attempts in a predeclared order. A whole
window bar affects both pairs. Eligible member loss is independent Bernoulli
with probability e=.10 in the primary grid and .20 in a stress grid; it is
independent of state, bars and residuals. This deliberately isolates structural
selection. It does not assert that real member exclusions are independent.

For each pair p, window j (zero-based), member i:

`S[p,j,i] = epsilon[p,j,i] + tau*Z[j] + b*j`, with `epsilon ~ iid N(0,1)`.

The residual SD is `s_r=1`. Window state is shared by all 14 members; states
are independent across windows. Three structural-bar mechanisms are used:

| Mechanism | State | Bar probability |
|---|---|---|
| gaussian_independent | Z~N(0,1) | q |
| hot_independent | H~Bernoulli(.25); Z=(H−.25)/sqrt(.25·.75) | q |
| hot_correlated | Same hot/cool state | 3q when hot, q/3 when cool |

Every mechanism has marginal bar probability q∈{1/8,1/4}. This is the final
whole-window bar probability after the allowed retry policy; individual retry
attempts and their wall time are not simulated. In the correlated
case the conditional rates are .375/.041667 and .75/.083333. Thus a structural
bar can be completely blind to scores/counts and still remove high-score
states disproportionately. This direction and strength are prospective
stress assumptions, not an inference about U1–U3 or the actual machine.
The shared-state intraclass correlation is tau²/(1+tau²); it is .20 at tau=.5.

The drift grid is tau/s_r∈{0,.13,.21,.25,.5,.8076923077}, with b∈{0,.05} s_r
per potential window. The mandatory {0,.25,.5} grid is present. R22-5's
`tau_rel=.0013` (stress `.0021`) is an energy-relative prior, not a residual-
relative SD. The conversion is `tau/s_r = tau_rel/(s_r/E)`:

| Hypothetical residual CV s_r/E | Prior tau/s_r | Stress tau/s_r |
|---|---:|---:|
| 1.00% | .13 | .21 |
| .26% | .50 | .8076923 |

Neither CV is measured or adopted. W1/C1 must supply the actual conversion.
There are 72 primary settings (three mechanisms × two q × six tau × two b)
and 12 e=.20 hot-correlated sensitivities (tau=0,.5,.8076923): **84 settings**.

All four designs share the same synthetic C1–C10 score/member/bar tape:

* `oracle8`: use C1–C8, pretending structural bars never occur. Independent
  member exclusions remain. Require both m≥39.
* `fixed8_no_replace`: attempt C1–C8 once, discard structurally barred windows,
  retain all eligible members of the rest, and require both m≥39. It may use
  fewer than eight counted windows; this is the old fixed-eight-attempt
  comparator. If eight *counted* windows were mandatory here too, its
  qualification would instead be P(no bar in C1–C8) times oracle qualification.
* `old_count6`: stop at the first attempted n∈{6,7,8} with both m≥39, otherwise
  fail at eight. Bars and member exclusions affect counts. No reserves.
* `r22`: take the first eight unbarred windows in C1–C10. Stop at the eighth
  admitted window. C9/C10 are attempted only to replace a structural bar,
  never to repair low m. A barred C9 consumes an attempt. Fewer than eight
  admitted windows at the cap is insufficient even if both m already exceed
  39; eight admitted windows with low m is also insufficient. No C11 exists.

No threshold or score enters any collection decision. Labels for different
structural causes are combined into the same hypothetical bar event; actual
classification of U1–U3/capture/retry outcomes remains the lead's contract.

Three strict `score > threshold` rules are reported. `maximum` uses rank m.
`rank05` uses ceil(.95*(m+1)), which is rank 38 at m=39. `literal38` always
uses rank 38, as explicitly requested; its nominal FPR is *not* 5% once m
increases. For example at m=56 it is 19/57=33.333%, under iid continuous
scores. These rules must not be conflated, and there is no score-based
subsampling to force m=39.

## FPR denominator and uncertainty

The common future roster is T1–T3 at potential positions 11–13 for every
design, so unused reserves are not quietly reassigned. The b=.05 case has
calibration mean shifts 0–.45 s_r and test shifts .50/.55/.60 s_r. This common
horizon isolates collection rules; an immediately-after-stop calendar is a
different prospective design. With b=0 the calendar choice has no effect.

`fpr` is the expected future strict exceedance probability averaged over
independent calibration studies that qualify. Future Gaussian residual/state
tails are integrated exactly; it is the Monte Carlo expectation of realized
future-window risk, not an empirical alarm fraction from three test windows
and not a guarantee on each realized calibration study. No calibration failure
is counted as a true negative.

Two future populations are explicit in the CSV:

* `fpr`: a latent, scorable benign member from **all** future window states.
  This is the counterfactual oracle/no-bar selection diagnostic. In a real
  capture-failure window no such score is available.
* `future_pass_fpr`: condition the future window on passing the **same frozen
  structural gate** as calibration. Independent member exclusion cancels.
  For hot-correlated bars the future admitted hot probability is
  `.25*(1−3q)/(1−q)`, i.e. .178571 or .083333, rather than .25. A barred test
  window stays unavailable; it is never assigned no-alarm credit.

One independent Monte Carlo unit is the entire two-pair study. Each setting
has 100,000 studies with fixed seed `202611082201` and memory chunk 2,000.
The two pair risks are averaged *within* study before computing pair-mean
intervals. Separate pair rows are saved. Wilson intervals cover count
probabilities; normal study-level standard errors cover mean risks and paired
differences, all pointwise 95% Monte Carlo intervals. They describe numerical
error under this model, not model uncertainty, simultaneous coverage, a live
FPR confidence bound, or a conditional conformal guarantee.

Each design's headline FPR conditions on its own qualification. Paired
`delta_threshold_oracle` and `delta_fpr_oracle` use the **intersection** of
that design's and oracle qualification; `delta_fixed8` uses the corresponding
intersection too. This prevents differing failure populations from being
misrepresented as a threshold effect. It remains a contrast within jointly
viable tapes, not a population-wide causal estimate. Different parameter settings
reuse random tapes; within-setting comparisons are paired.

## Availability: m≥39 and eight counted windows are separate gates

Exact count probabilities are independent of mechanism, tau and b by construction. Percent with 95% Monte Carlo CIs; the table quotes hot-correlated runs for the four q/e settings. Exact probabilities are included in the CSV and checked by the simulator.

| q | e | Design | P(m≥39 both) | P(qualified) | Exact qualification % |
|---:|---:|---|---|---|---:|
| 0.125 | 0.1 | oracle8 | 100.000 [99.996, 100.000] | 100.000 [99.996, 100.000] | 99.999009 |
| 0.125 | 0.1 | fixed8_no_replace | 75.969 [75.703, 76.233] | 75.969 [75.703, 76.233] | 75.893887 |
| 0.125 | 0.1 | old_count6 | 75.969 [75.703, 76.233] | 75.969 [75.703, 76.233] | 75.893887 |
| 0.125 | 0.1 | r22 | 97.449 [97.349, 97.545] | 88.129 [87.927, 88.328] | 88.048912 |
| 0.25 | 0.1 | oracle8 | 100.000 [99.996, 100.000] | 100.000 [99.996, 100.000] | 99.999009 |
| 0.25 | 0.1 | fixed8_no_replace | 40.838 [40.534, 41.143] | 40.838 [40.534, 41.143] | 40.866503 |
| 0.25 | 0.1 | old_count6 | 40.838 [40.534, 41.143] | 40.838 [40.534, 41.143] | 40.866503 |
| 0.25 | 0.1 | r22 | 79.502 [79.251, 79.751] | 52.592 [52.282, 52.901] | 52.558760 |
| 0.125 | 0.2 | oracle8 | 95.553 [95.423, 95.679] | 95.553 [95.423, 95.679] | 95.674333 |
| 0.125 | 0.2 | fixed8_no_replace | 47.574 [47.265, 47.884] | 47.574 [47.265, 47.884] | 47.568343 |
| 0.125 | 0.2 | old_count6 | 47.574 [47.265, 47.884] | 47.574 [47.265, 47.884] | 47.568343 |
| 0.125 | 0.2 | r22 | 87.456 [87.249, 87.660] | 84.125 [83.897, 84.350] | 84.241044 |
| 0.25 | 0.2 | oracle8 | 95.553 [95.423, 95.679] | 95.553 [95.423, 95.679] | 95.674333 |
| 0.25 | 0.2 | fixed8_no_replace | 19.470 [19.226, 19.717] | 19.470 [19.226, 19.717] | 19.575276 |
| 0.25 | 0.2 | old_count6 | 19.470 [19.226, 19.717] | 19.470 [19.226, 19.717] | 19.575276 |
| 0.25 | 0.2 | r22 | 59.742 [59.438, 60.046] | 50.255 [49.945, 50.565] | 50.285741 |

The count stop and fixed-eight-attempt rule have identical completion probability because the same final C1–C8 roster is available. R22 has exactly eight counted windows when it qualifies. With q=.25, P(at least eight unbarred in ten)=52.5593% even with zero member attrition; two reserves are not a high-reliability supply guarantee. Requiring eight counted windows in the no-replacement comparator would reduce its structural-only qualification to 34.3609% or 10.0113% at q=1/8 or 1/4, respectively.

## Future all-window FPR at the requested drift levels

Primary e=.10, b=0, hot-correlated bars. Each cell is percent [95% MC CI]. Both pairs have the same generating law; these are study-level pair means, with separate pair rows in the score CSV.

### maximum

| q | tau/s_r | Oracle, no bars | Fixed8, no replacement | Old count stop | R22 |
|---:|---:|---|---|---|---|
| 0.125 | 0 | 1.951 [1.942, 1.959] | 2.110 [2.100, 2.121] | 2.280 [2.268, 2.291] | 1.954 [1.945, 1.963] |
| 0.125 | 0.25 | 2.031 [2.022, 2.040] | 2.451 [2.438, 2.463] | 2.647 [2.634, 2.660] | 2.270 [2.260, 2.281] |
| 0.125 | 0.5 | 2.321 [2.309, 2.333] | 3.159 [3.141, 3.177] | 3.420 [3.401, 3.440] | 2.919 [2.904, 2.935] |
| 0.25 | 0 | 1.951 [1.942, 1.959] | 2.183 [2.169, 2.198] | 2.294 [2.279, 2.310] | 1.963 [1.951, 1.975] |
| 0.25 | 0.25 | 2.031 [2.022, 2.040] | 2.934 [2.915, 2.953] | 3.075 [3.055, 3.095] | 2.656 [2.640, 2.671] |
| 0.25 | 0.5 | 2.321 [2.309, 2.333] | 4.438 [4.409, 4.467] | 4.636 [4.606, 4.666] | 4.040 [4.017, 4.063] |

### literal38

| q | tau/s_r | Oracle, no bars | Fixed8, no replacement | Old count stop | R22 |
|---:|---:|---|---|---|---|
| 0.125 | 0 | 25.932 [25.902, 25.962] | 19.974 [19.921, 20.026] | 13.550 [13.511, 13.588] | 25.929 [25.896, 25.961] |
| 0.125 | 0.25 | 26.063 [26.028, 26.098] | 21.335 [21.279, 21.392] | 14.709 [14.666, 14.751] | 27.456 [27.419, 27.493] |
| 0.125 | 0.5 | 26.366 [26.320, 26.411] | 22.984 [22.920, 23.048] | 16.315 [16.264, 16.367] | 29.105 [29.058, 29.152] |
| 0.25 | 0 | 25.932 [25.902, 25.962] | 17.130 [17.059, 17.201] | 12.956 [12.903, 13.009] | 25.946 [25.905, 25.988] |
| 0.25 | 0.25 | 26.063 [26.028, 26.098] | 19.937 [19.858, 20.016] | 15.406 [15.345, 15.468] | 29.390 [29.343, 29.437] |
| 0.25 | 0.5 | 26.366 [26.320, 26.411] | 23.352 [23.265, 23.440] | 18.663 [18.591, 18.736] | 32.990 [32.935, 33.045] |

### rank05

| q | tau/s_r | Oracle, no bars | Fixed8, no replacement | Old count stop | R22 |
|---:|---:|---|---|---|---|
| 0.125 | 0 | 3.899 [3.887, 3.910] | 4.213 [4.198, 4.228] | 4.553 [4.537, 4.569] | 3.900 [3.888, 3.913] |
| 0.125 | 0.25 | 4.024 [4.011, 4.038] | 4.794 [4.776, 4.811] | 5.173 [5.154, 5.192] | 4.444 [4.429, 4.459] |
| 0.125 | 0.5 | 4.444 [4.426, 4.461] | 5.854 [5.829, 5.879] | 6.309 [6.283, 6.336] | 5.431 [5.410, 5.453] |
| 0.25 | 0 | 3.899 [3.887, 3.910] | 4.359 [4.338, 4.380] | 4.577 [4.555, 4.598] | 3.915 [3.899, 3.931] |
| 0.25 | 0.25 | 4.024 [4.011, 4.038] | 5.630 [5.604, 5.656] | 5.894 [5.867, 5.921] | 5.094 [5.074, 5.115] |
| 0.25 | 0.5 | 4.444 [4.426, 4.461] | 7.864 [7.826, 7.901] | 8.193 [8.154, 8.232] | 7.176 [7.145, 7.206] |

## Structural selection, admitted tests, and relative-energy priors

The next table isolates selection from Gaussian versus hot-mixture score shape: b=0, e=.10, tau=.5. Δthreshold and ΔFPR are paired R22−oracle on common qualification. Threshold units are s_r; FPR units are percent and differences are percentage points.

| Mechanism | q | R22 maximum FPR, all | Oracle maximum FPR, all | Δmaximum threshold | Δmaximum FPR | R22 maximum FPR, future passing gate |
|---|---:|---|---|---|---|---|
| gaussian_independent | 0.125 | 2.196 [2.185, 2.208] | 2.191 [2.180, 2.201] | -0.001 [-0.002, 0.000] | 0.002 [-0.004, 0.009] | 2.196 [2.185, 2.208] |
| gaussian_independent | 0.25 | 2.206 [2.191, 2.221] | 2.191 [2.180, 2.201] | -0.003 [-0.006, -0.001] | 0.013 [0.003, 0.023] | 2.206 [2.191, 2.221] |
| hot_independent | 0.125 | 2.325 [2.312, 2.338] | 2.321 [2.309, 2.333] | -0.001 [-0.002, 0.001] | 0.004 [-0.003, 0.012] | 2.325 [2.312, 2.338] |
| hot_independent | 0.25 | 2.336 [2.319, 2.353] | 2.321 [2.309, 2.333] | -0.002 [-0.004, 0.001] | 0.007 [-0.004, 0.019] | 2.336 [2.319, 2.353] |
| hot_correlated | 0.125 | 2.919 [2.904, 2.935] | 2.321 [2.309, 2.333] | -0.103 [-0.104, -0.101] | 0.504 [0.493, 0.514] | 2.339 [2.327, 2.352] |
| hot_correlated | 0.25 | 4.040 [4.017, 4.063] | 2.321 [2.309, 2.333] | -0.221 [-0.224, -0.217] | 1.210 [1.190, 1.229] | 2.245 [2.231, 2.260] |

Under stationary independent bars, the first eight admitted window marks have exactly the same distribution as eight oracle windows, even conditional on reaching eight before C10. Small discrepancies in the independent-control table are Monte Carlo fluctuation, including pointwise intervals that exclude zero on this reused-tape grid; the model has no expected selection effect there. Correlated bars instead change the admitted state law to P(hot | not barred), which replacements do not undo. Forward trend additionally changes the calendar distribution.


Conditioning future test windows on the same gate changes the target population. It must be declared prospectively, with barred test windows disclosed as unavailable. It cannot establish the original all-window oracle claim, and clustering/forward drift still require qualification.

B5-informed **scale assumptions**, q=.25, e=.10, hot-correlated bars; no data-based s_r conversion is available:

| tau/s_r | b/window | Oracle maximum FPR | R22 maximum FPR, all | R22 maximum FPR, passing gate | R22 rank05 FPR, all | R22 literal38 FPR, all |
|---:|---:|---|---|---|---|---|
| 0.130000 | 0 | 1.969 [1.961, 1.978] | 2.250 [2.237, 2.263] | 1.972 [1.960, 1.983] | 4.421 [4.403, 4.439] | 27.655 [27.611, 27.699] |
| 0.130000 | 0.05 | 4.214 [4.198, 4.230] | 4.392 [4.370, 4.415] | 3.918 [3.897, 3.938] | 8.133 [8.104, 8.162] | 39.385 [39.333, 39.436] |
| 0.210000 | 0 | 2.005 [1.996, 2.014] | 2.503 [2.489, 2.518] | 1.990 [1.978, 2.002] | 4.847 [4.827, 4.866] | 28.802 [28.756, 28.848] |
| 0.210000 | 0.05 | 4.228 [4.212, 4.244] | 4.782 [4.758, 4.807] | 3.930 [3.909, 3.951] | 8.731 [8.700, 8.763] | 40.512 [40.459, 40.565] |
| 0.807692 | 0 | 2.906 [2.886, 2.926] | 6.741 [6.699, 6.782] | 2.965 [2.944, 2.986] | 10.597 [10.547, 10.647] | 36.364 [36.300, 36.428] |
| 0.807692 | 0.05 | 4.861 [4.833, 4.890] | 9.825 [9.770, 9.880] | 4.745 [4.713, 4.777] | 14.893 [14.829, 14.957] | 45.724 [45.652, 45.797] |

Complete forward-trend and member-loss sensitivities for every design/rule are in the CSV and unabridged stdout. Positive b is an extra stress model, not a measured trend.

## Smallest tested prospective repair

Two repairs address different problems. First, if “rank 38” meant a 5% rule, freeze the m-dependent rank ceil(.95*(m+1)); a constant rank 38 fails the iid negative control. The simulation does not silently make this change.

Second, to counter structural selection against the all-window target, the bounded candidate tested here adds a **prospectively frozen margin c·s_r** to both the maximum and rank05 cutoffs. It changes no collection decision or m. The grid c∈{0,.1,.2,.3,.4,.5,.75,1} was predeclared in the script; the following is an exploratory choice among that grid, not a fitted real-data constant or a distribution-free correction.

| Margin c | Worst paired ΔFPR vs oracle, maximum | Worst paired ΔFPR vs oracle, rank05 | Worst mean maximum FPR | Worst mean rank05 FPR |
|---:|---|---|---|---|
| 0 | 3.677 [3.624, 3.730] | 4.703 [4.642, 4.763] | 10.426 [10.368, 10.484] | 15.838 [15.771, 15.905] |
| 0.1 | 2.601 [2.551, 2.652] | 3.230 [3.172, 3.288] | 9.350 [9.297, 9.404] | 14.365 [14.302, 14.428] |
| 0.2 | 1.607 [1.559, 1.654] | 1.882 [1.829, 1.934] | 8.355 [8.306, 8.404] | 12.987 [12.929, 13.046] |
| 0.3 | 0.726 [0.683, 0.769] | 0.823 [0.784, 0.863] | 7.437 [7.392, 7.482] | 11.703 [11.648, 11.757] |
| 0.4 | 0.144 [0.114, 0.175] | -0.049 [-0.087, -0.011] | 6.594 [6.553, 6.635] | 10.508 [10.457, 10.558] |
| 0.5 | -0.387 [-0.416, -0.357] | -0.846 [-0.884, -0.809] | 5.822 [5.784, 5.859] | 9.399 [9.353, 9.446] |
| 0.75 | -1.482 [-1.511, -1.454] | -2.537 [-2.573, -2.501] | 4.180 [4.151, 4.209] | 6.988 [6.950, 7.025] |
| 1 | -1.812 [-1.823, -1.802] | -3.567 [-3.582, -3.552] | 2.910 [2.888, 2.932] | 5.050 [5.021, 5.079] |

Paired common-success contrasts do not compare the full, different qualification populations. For margin choice, also compare each design’s own qualified mean FPR to the oracle’s own qualified mean. The following conservative pointwise normal interval uses the sum of the two standard errors as an upper bound on the standard error of their difference (Cauchy bound); it does not pretend the samples are independent.

| Margin c | Worst own-population Δmaximum FPR | Worst own-population Δrank05 FPR |
|---:|---|---|
| 0 | 5.153 [5.064, 5.242] | 6.853 [6.746, 6.960] |
| 0.1 | 4.077 [3.993, 4.161] | 5.380 [5.278, 5.482] |
| 0.2 | 3.082 [3.002, 3.162] | 4.003 [3.904, 4.101] |
| 0.3 | 2.164 [2.088, 2.240] | 2.718 [2.624, 2.812] |
| 0.4 | 1.321 [1.249, 1.393] | 1.523 [1.433, 1.613] |
| 0.5 | 0.566 [0.503, 0.630] | 0.612 [0.553, 0.672] |
| 0.75 | -0.533 [-0.572, -0.495] | -1.078 [-1.130, -1.026] |
| 1 | -1.340 [-1.373, -1.307] | -2.376 [-2.422, -2.331] |

The smallest **tested** margin with both the own-population and paired-common-success upper ΔFPR bounds ≤0 in every one of the 84 settings is **0.75 s_r**. The smaller .5 s_r margin passes the paired-intersection comparison but fails the own-population comparison; it must not be called restoration of the oracle FPR. No initial-grid margin through 1.0 s_r meets both nominal mean targets across all 84 settings: at 1.0 the worst maximum FPR remains 2.910% [2.888,2.932], and rank05 remains 5.050% [5.021,5.079]. Matching the oracle is weaker than restoring nominal FPR because clustering/forward drift already affect the oracle. These are pointwise bounds, not simultaneous coverage.

An independent-seed validation used seed 202611082202, 200,000 studies per selected setting. Settings were selected as the discovery grid’s worst upper-bound contrasts/risks for the two chosen margins; this validates these settings, not the unsearched model space. The complete rows are in [r22-validation-sol1.json](r22-validation-sol1.json).

| Setting (q,e,tau,b; hot-correlated) | Margin | Rule | Mean FPR | Own-population ΔFPR vs oracle |
|---|---:|---|---|---|
| (0.25,0.1,0.807692,0) | 0.75 | maximum | 2.369 [2.357, 2.382] | -0.537 [-0.564, -0.510] |
| (0.25,0.1,0.807692,0) | 0.75 | rank05 | 4.149 [4.131, 4.166] | -1.068 [-1.105, -1.031] |
| (0.25,0.1,0.807692,0) | 1.25 | maximum | 0.993 [0.986, 0.999] | -1.914 [-1.934, -1.894] |
| (0.25,0.1,0.807692,0) | 1.25 | rank05 | 1.885 [1.875, 1.894] | -3.332 [-3.361, -3.304] |
| (0.25,0.2,0.807692,0.05) | 0.75 | maximum | 4.173 [4.153, 4.194] | -1.094 [-1.136, -1.052] |
| (0.25,0.2,0.807692,0.05) | 0.75 | rank05 | 6.989 [6.963, 7.016] | -1.985 [-2.039, -1.930] |
| (0.25,0.2,0.807692,0.05) | 1.25 | maximum | 1.954 [1.943, 1.965] | -3.313 [-3.345, -3.280] |
| (0.25,0.2,0.807692,0.05) | 1.25 | rank05 | 3.535 [3.520, 3.551] | -5.438 [-5.482, -5.395] |
| (0.25,0.1,0.807692,0.05) | 0.75 | maximum | 3.869 [3.850, 3.888] | -0.995 [-1.034, -0.956] |
| (0.25,0.1,0.807692,0.05) | 0.75 | rank05 | 6.459 [6.435, 6.484] | -1.812 [-1.862, -1.761] |
| (0.25,0.1,0.807692,0.05) | 1.25 | maximum | 1.785 [1.775, 1.795] | -3.079 [-3.110, -3.049] |
| (0.25,0.1,0.807692,0.05) | 1.25 | rank05 | 3.217 [3.202, 3.231] | -5.055 [-5.095, -5.014] |

The 1.25 s_r line is an explicitly **post-discovery extension** tested with a fresh seed. At 1.0 s_r only two distinct settings fail a nominal bound: hot-correlated, q=.25, tau=.8076923, b=.05, with e=.10 or .20. The fresh-seed validation covers both. For the other 82 settings, increasing the margin from 1.0 to 1.25 decreases risk for every study, so the existing 1.0 upper bounds remain conservative bounds on the 1.25 mean risk. Thus 1.25 is the smallest tested nominal-target candidate on this finite grid with both fresh-seed exception checks passing; values in (1.0,1.25) were not searched. This is model-limited evidence and is not a live guarantee.

The added margin controls FPR inflation in this model; it does not make the threshold an unbiased estimate of the oracle cutoff. This margin requires a residual scale fixed before the calibration block, a qualified common scorer, an explicit future-population rule, supported-runtime reproduction, and a power/detection-cost assessment. It is a prospective lead/statistics choice, not permission to repair observed scores. Matching test admission is a smaller policy change *if the scientific target is explicitly the admitted population*; the future-pass numbers above quantify it, but do not justify an all-window claim. Arbitrary score/state-dependent missingness, persistent states, heavy tails and unmodeled trends can defeat a fixed margin.

The availability cap is a separate prospective ruling. Under independent bars and e=.10, at least **11** total attempts at q=1/8 (96.103% structural completion) or **14** at q=1/4 (96.173%) are needed to exceed 95% eight-window supply; for 99%, **13** (99.702%) or **16** (99.253%). Multiply by 99.9990% for the independent member-count target. At e=.20 even eight intact windows have only 95.6743% both-pair yield, so increasing attempts alone cannot reach 99%. These are planning alternatives, not an expansion of R22-2’s C10 cap.

## Quoted program output

The availability fields are q, e, design, P(m≥39 both), P(qualified), E[attempted]. Risk fields are mechanism, q, e, tau, b, design, maximum, rank05, literal38. Risk units are percent:

```text
SYNTHETIC ONLY seed=202611082201 studies/scenario=100000 scenarios=84
Percent, pointwise 95% MC CIs; dFPR/dthreshold paired on common oracle success.
0.25 0.1 oracle8 100.000[99.996,100.000] 100.000[99.996,100.000] 8.000[8.000,8.000]
0.25 0.1 fixed8_no_replace 40.838[40.534,41.143] 40.838[40.534,41.143] 8.000[8.000,8.000]
0.25 0.1 old_count6 40.838[40.534,41.143] 40.838[40.534,41.143] 7.796[7.793,7.799]
0.25 0.1 r22 79.502[79.251,79.751] 52.592[52.282,52.901] 9.601[9.597,9.605]
hot_correlated 0.25 0.1 0.5 0.0 oracle8 2.321[2.309,2.333] 4.444[4.426,4.461] 26.366[26.320,26.411]
hot_correlated 0.25 0.1 0.5 0.0 fixed8_no_replace 4.438[4.409,4.467] 7.864[7.826,7.901] 23.352[23.265,23.440]
hot_correlated 0.25 0.1 0.5 0.0 old_count6 4.636[4.606,4.666] 8.193[8.154,8.232] 18.663[18.591,18.736]
hot_correlated 0.25 0.1 0.5 0.0 r22 4.040[4.017,4.063] 7.176[7.145,7.206] 32.990[32.935,33.045]
Outputs: r22-{counts,scores,fixes}-sol1.csv r22-metadata-sol1.json; elapsed=592.4s
```

## Verification and reproduction

The one-process pilot measured 10,000 synthetic studies in .616 seconds
(memory chunk 2,000). No pipeline optimization, cache,
parallel worker pool, model inference, energy measurement or throughput claim
is made. The sandbox rejected `nice` with `setpriority: Operation not permitted`;
both numerical runs continued at ordinary priority, one process and one
numerical thread. The warning is preserved in both stderr logs. Memory batching
is synthetic-only. The byte-identical replay check
runs the same synthetic scenario twice; all 1,024 structural-bar tapes are
also checked against an independent scalar selection loop.

```sh
nice -n 10 env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 -B docs/align/v4/b3-sim/simulate_r22_sol1.py > docs/align/v4/b3-sim/r22-run-sol1.txt 2> docs/align/v4/b3-sim/r22-checks-sol1.txt
```

The fresh-seed check is reproducible from the delivered selection manifest:

```sh
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 -B docs/align/v4/b3-sim/validate_r22_sol1.py
```

Its three settings × 200,000 studies completed in 35.9 seconds. See the
[validation runner](validate_r22_sol1.py), [stdout](r22-validation-run-sol1.txt)
and [stderr](r22-validation-checks-sol1.txt). The checked-in selection manifest
records the initial-grid margin decision and the post-discovery 1.25 extension.

Python 3.14.6 / NumPy 2.2.6 is the installed numerical environment. Python
3.13 has no NumPy here (verified without installing anything). Python 3.13
AST parsing passes. The earlier simulator's explicit-ufunc/large-array
immutability safeguards are retained. The lead should reproduce with supported
Python 3.11/3.13 + NumPy off this busy machine before adopting constants.

Focused checks:

* New simulator: eight unittest checks pass, including every bar tape, no
  count top-up, replacement failure/cap, rank boundaries and strict ties,
  no-bars identity, integrated tails/immutability, exact probability
  enumeration, and deterministic serialized replay.
* All 84 settings assert simulated qualification against independent exact
  binomial sums; tau=0,b=0 asserts FPR against exact random-m rank expectations.
* Earlier `simulate_sol1.py --check`: six checks pass (.483 s).
* `python3.13 -B -m unittest tests.align.test_v4_estimands`: 15 pass (.002 s).
* No full suite, pytest, measurement pipeline, weights, network, external
  checkout, real restricted path or other-job inspection/control. No MLX code
  changed, so no new MLX/native test is required by this artifact. Native
  common-scorer and final-eligibility gates remain lead-owned.

One completed 84-setting run took 592.4 seconds. The stdlib output audit checked 336 count rows, 3,024 score rows and 1,344 margin rows, pair means, CI ordering, exact hot-admission fractions, and source/helper digests. CSV files were normalized from the stdlib writer’s CRLF to LF only; parsed rows were proved identical. [r22-normalization-sol1.json](r22-normalization-sol1.json) binds raw hashes in the metadata to delivered LF hashes. No numeric result or executed source changed.

Source/helper hashes, environment, elapsed time and raw output hashes are in
[r22-metadata-sol1.json](r22-metadata-sol1.json). Complete raw stdout and
checks are [r22-run-sol1.txt](r22-run-sol1.txt) and
[r22-checks-sol1.txt](r22-checks-sol1.txt); numeric tables are
[counts](r22-counts-sol1.csv), [scores](r22-scores-sol1.csv) and
[prospective margins](r22-fixes-sol1.csv).

The task branch was precreated and clean at intake and was retained. The brief
explicitly prohibits coordination writes; `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json` and `tests/test_gen_state.py` remain unchanged.
No kernel task, decision-log ruling, registration change, push or deployment
is made. Handoff notes belong to this report and the dated run-report pointer.

## Remaining decisions and next exact step

The lead should reject a blanket “structural-only replacement preserves fixed-8 FPR” claim when the gate can correlate with hot states. Decide the all-window versus admitted-window target, the literal38 versus m-dependent rank semantics, and the required availability probability before W1 registration. Then reproduce this script on supported Python/NumPy, convert the R22-5 prior using a prospective W1/C1 residual scale, and rule the smallest acceptable margin/admission design and power cost. No policy is installed here. Actual bar dependence, drift persistence, residual tails, scorer/eligibility validity, and the calendar after unused reserves remain uncertain.
