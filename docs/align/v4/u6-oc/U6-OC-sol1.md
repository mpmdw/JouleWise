# U6 operating characteristics — Sol1

Synthetic desk study, 2026-11-07 PST (brief/branch dated 2026-11-08).
Branch: `align/2026-11-08-u6-oc-sol1`; product baseline `969a730cd`.

**Assessment: adequate as a limited, pooled common-drift diagnostic under
independent trajectories; not qualified as a reliable stability certificate
or as a per-window claim veto.** At the six-window intact roster, no drift
gives 76.08% PASS, 0.47% FAIL and 23.44% INCONCLUSIVE. A 30% underestimate
of s_r makes 68.11% INCONCLUSIVE. Modest shared window variation makes the
trajectory-only uncertainty unreliable. These are model-conditional synthetic
results, not observations of the study machine. No rule amendment is installed.

## Authority and roster, with number provenance

References without an object prefix are at `969a730cd`. R12 is absent from
this branch's old restart file, but exists in the already-local Git object
`3809bdd14da5882659f17dc292200d4afbbd1579` (`origin/main` at intake).
`3809bdd14:RUN_STATE.md:1045` identifies item 214/R12;
`:1050` adopts B3: **minimum 6 calibration windows, cap 8, stop on eligible
counts only when both pairs have m >= 39**. This supersedes the pending cap
at `docs/align/pilot_protocol_v4.md:568-574`. No fetch or other network
operation was performed. Object-prefixed references can be inspected with
`git show <object>:<file> | nl -ba` entirely through permitted repo objects.

| Component | Programmed shape and U6 treatment | Source of every roster number |
|---|---|---|
| W1 | 18 members: 4 anchors, 8 contrasts, 6 D episodes. D benign episodes are ordinals 5, 8, 17, 18; 17 repeats 5, so 3 distinct D benign trajectory identities. D sabotage is at 11, 14. The final optional development member 18 may be dropped prospectively for fit. W1 is selection data, never an extra calibration window. | `docs/align/pilot_protocol_v4.md:107-130`; executable `scripts/align_v4_kit.py:63-82`; drop rule `:1323-1325`. |
| Each default D window | 22 episodes: 4 anchors + 2 sentinel replays + 14 fresh benign (7 per pair) + 2 fresh sabotage (1 per pair). Fresh benign are the primary U6 roster here. Sabotage, anchors and contrast rows do not enter this benign residual test. | `docs/align/pilot_protocol_v4.md:151-158`. The two pairs and W1 trajectory identities are explicit in `scripts/align_v4_kit.py:64-81`. |
| Seed/trajectory identity | Each fresh D member is a new seed-index trajectory within its pair. Held-out indices begin at 2; W1 uses 1 and 93; 91-99 are reserved development. The two sentinels repeat the same W1 ordinal-5 seed-1 spam trajectory, including across D windows. Replays are repeated records, never new independent calibration units. | `docs/align/pilot_protocol_v4.md:151-154,170-175`; sentinel admissibility/fallback `:655-663`. |
| Calibration | Stop at 6-8 windows using counts only; m >= 39 **per pair**, never 39 pooled. Intact capacities: 6x7=42, 7x7=49, 8x7=56 per pair; respectively 84, 98, 112 fresh benign trajectories pooled. Minimum successful balanced retained example: 39+39=78. These totals are arithmetic from the cited count and window rules. | `3809bdd14:RUN_STATE.md:1050`; `docs/align/pilot_protocol_v4.md:556-574`. |
| Locked test | Separate from calibration. R12 leaves **3 versus 6** test windows unresolved. If the same 7-per-pair/window shape is adopted, that is 21 versus 42 benign per pair. `T3-if-same-shape` is explicitly hypothetical; the six-window test case has the same conditional OC as C6, with no calibration/test pooling. | `3809bdd14:RUN_STATE.md:1053`; separate cohort and exclusions `docs/align/pilot_protocol_v4.md:556-566`. |
| Turns | Registered D ceiling is 12, not 12 observed turns. Use 3 synthetic completed turns as an assumption, sensitivity at 1, 6 and 12. No actual completed-turn distribution was read. | Ceiling: `docs/align/pilot_protocol_v4.md:80,668`; kit assertion `scripts/align_v4_kit.py:1589-1590`; absence of a turn guarantee `docs/align/pilot_protocol_v4.md:715-720`. |

There is **not yet a completely finalized series manifest** in these sources.
The current kit's `ROSTER` is W1, not an executable R12 D-series manifest;
the default D shape is protocol authority. This study evaluates that shape
with R12's adopted stop, not an invented finalized test cohort. The alternative
one-pair/14-member fallback in protocol lines 156-158 is conditional on a
different duration decision and is not the default evaluated here.

Intact six-window calibration meets the target and must stop at six. C7-m49
and C8-m56 are **capacity sensitivities**, not attainable all-intact B3 stopping
paths. Actual extensions follow earlier losses and will usually retain fewer
members than those capacities. The m39 case represents successful attrition
at the threshold, not a guarantee that every valid stop is balanced. Stop
frequencies are simulated separately below; the fixed-roster OC tables are
not an unconditional mixture over attrition or over failed series.

## Exact rule and simulation model

`joulewise/align/apple/thermal_desk.py:535-584` takes per-turn residuals,
sorts episodes by time **within pair**, assigns floor(n/2) episodes early and
the remainder late, then pools the turn rows across pairs. Cluster identity
is `(pair, trajectory)` (`:569`). With equal lengths and equal pair sizes
this also gives equal pair weighting; the executable rule generally weights
by turns, not equally by pair. `session_desk_evidence` concatenates the supplied
session inputs before this split (`:477-484`). These are series halves when
all calibration sessions are supplied, not early/late halves reset in each
window. W1 itself cannot claim U6 (`docs/align/pilot_protocol_v4.md:443-446`).

`joulewise/align/apple/v4_estimands.py:194-228` uses the uncorrected CR0
cluster sandwich and the exact multiplier 1.645. With effect b and SE q:

- FAIL if |b| > 0.5*s_used, even when the interval overlaps the margin.
- Otherwise PASS if [b-1.645q, b+1.645q] lies inside +/-0.5*s_used.
- Otherwise INCONCLUSIVE, preserving `calibration unresolved: imprecise`.

The position helper counts distinct trajectories and marks a position
evaluable only at >=6 (`v4_estimands.py:231-242`); it adds no slope or second
verdict gate. Three-turn intact C6 gives 84 distinct trajectories at each
position. Synthetic one-turn profiles have no support at later positions.
The helper's evaluability label alone does not establish an energy tolerance
or actual support on the machine.

Normalize the true, per-turn residual SD to s_true=1. Primary noise model:

`r_it = sqrt(rho)*U_i + sqrt(1-rho)*epsilon_it`, independent standard normal
U and epsilon, rho=0.5; trajectories are independent. This represents a
moderate persistent trajectory component, **an assumption, not an estimate
from hardware**. Sensitivities rho=0 and 0.9 bracket that assumption.
The episode mean variance is exactly `v=rho+(1-rho)/L`; the script samples
that Gaussian sufficient statistic rather than generating and discarding
every turn. Its sandwich score for cluster g is

`sum_late L_i*(mean_i-mu_late)/N_late - sum_early L_i*(mean_i-mu_early)/N_early`.

Summing squared cluster scores gives the exact registered variance, including
repeated identities across halves. Nine in-memory comparisons against both
the actual desk and helper verify effect, SE, status and position means,
including ragged lengths and sentinel repetition. No estimator is refitted.

Add a common late-half step delta in {0, .25, .5, 1} times s_true. This is
**the early/late mean difference**, not the endpoint amplitude of a linear
ramp. For a continuous linear drift, the endpoint change is approximately
twice its half-mean difference. Negative steps have the same theoretical
OC by symmetry. The scale supplied to U6 is fixed at .7, 1 or 1.3 times
s_true; this is systematic scale-error sensitivity, not a model of random
s_r estimation or its covariance with the residuals.

Additional stresses: include the 12 sentinel records over six windows as
one additional shared spam trajectory; and introduce common window variance
eta=.2, replacing rho of the trajectory variance by rho-eta. In the latter
model `r_wit=sqrt(.2)*W_w+sqrt(.3)*U_i+sqrt(.5)*epsilon_wit`:
within-episode ICC stays .5, but different trajectories in a window have
correlation .2. This tests a dependence the registered trajectory sandwich
does not cover. No dependence assumption was selected using study outcomes.

## Execution and quoted output

One full simulation run, 20,000 replicates for each of 16 profiles; each draw
is reused for the 12 drift/scale combinations. Independent profile streams
use seed `20261108 + profile_index`. Python 3.13, stdlib only; NumPy is not
installed and is not required. Full stdout is retained in
[U6-OC-sol1-output.txt](U6-OC-sol1-output.txt). All brackets below are pointwise
95% Wilson **Monte Carlo** intervals in percent, not uncertainty about whether
the synthetic model fits reality. The maximum MC half-width is about .69
percentage points; zero events still have a nonzero upper bound.

Command:

```sh
python3.13 -B docs/align/v4/u6-oc/simulate_u6_sol1.py > docs/align/v4/u6-oc/U6-OC-sol1-output.txt
```

Quoted primary output (matched s_r):

```text
PROFILE C6-m42: episodes=84, clusters=84, turns=[3], rho=0.5, eta=0, mean_se=0.17545, fail_rule=point outside
| drift/s_true | s_used/s_true | PASS % [95% MC] | FAIL % [95% MC] | IMPRECISE % [95% MC] |
| 0 | 1 | 76.08 [75.49,76.67] | 0.47 [0.39,0.58] | 23.44 [22.86,24.03] |
| 0.25 | 1 | 40.13 [39.45,40.81] | 8.08 [7.71,8.47] | 51.79 [51.10,52.48] |
| 0.5 | 1 | 5.09 [4.80,5.41] | 50.88 [50.18,51.57] | 44.03 [43.34,44.72] |
| 1 | 1 | 0.00 [0.00,0.02] | 99.74 [99.66,99.80] | 0.26 [0.20,0.34] |
```

The no-drift FAIL column is the **false-fail** rate. For drift, distinguish
an affirmative stability PASS from a **missed FAIL**, defined here as
PASS+INCONCLUSIVE. At C6/matched scale, missed-FAIL rates are 91.92%
[91.53,92.29] at .25, 49.12% [48.43,49.82] at .5, and .26% [.20,.34] at 1.
These intervals are complements of the FAIL intervals, not sums of marginal
intervals. Delta=.25 is *inside* the registered tolerance: its missed FAIL is
not inherently an error. At .5 the point-based decision necessarily fails
about half the time; sample size cannot make a boundary point decisive.

Scale error at the same C6 roster:

| delta | s_used/s_true | PASS % [95% MC] | FAIL % [95% MC] | IMPRECISE % [95% MC] |
|---:|---:|---:|---:|---:|
| 0 | .7 | 27.11 [26.49,27.73] | 4.78 [4.49,5.08] | 68.11 [67.47,68.76] |
| 0 | 1.3 | 95.72 [95.44,96.00] | .04 [.02,.09] | 4.23 [3.96,4.52] |
| .25 | .7 | 10.56 [10.14,10.99] | 29.30 [28.68,29.94] | 60.13 [59.45,60.81] |
| .25 | 1.3 | 72.75 [72.12,73.36] | 1.17 [1.03,1.32] | 26.09 [25.49,26.70] |
| .5 | .7 | .68 [.58,.80] | 80.46 [79.90,81.00] | 18.86 [18.32,19.41] |
| .5 | 1.3 | 21.57 [21.01,22.15] | 20.30 [19.75,20.86] | 58.12 [57.44,58.81] |
| 1 | .7 | 0 [0,.02] | 99.97 [99.94,99.99] | .03 [.01,.06] |
| 1 | 1.3 | .04 [.02,.07] | 97.61 [97.39,97.81] | 2.35 [2.15,2.57] |

Thus delta=1 missed FAIL is .03% [.01,.06] with low scale and 2.39%
[2.19,2.61] with high scale. High scale increases the tolerance itself: its
21.57% PASS at true delta=.5 is not calibrated to the true .5 boundary.

Roster/assumption sensitivity at no drift and matched scale (full drift x
scale grids for every row are in retained stdout):

| Profile | PASS % [95% MC] | false FAIL % [95% MC] | IMPRECISE % [95% MC] |
|---|---:|---:|---:|
| Minimum retained, 39/pair | 71.83 [71.20,72.45] | .67 [.57,.79] | 27.50 [26.89,28.12] |
| Seven-window capacity, 49/pair | 83.72 [83.21,84.23] | .26 [.19,.34] | 16.02 [15.52,16.53] |
| Eight-window capacity, 56/pair | 89.23 [88.79,89.65] | .15 [.11,.21] | 10.62 [10.20,11.05] |
| C6 rho=0 | 97.94 [97.73,98.12] | .01 [0,.03] | 2.06 [1.87,2.27] |
| C6 rho=.9 | 54.47 [53.78,55.16] | 1.76 [1.59,1.95] | 43.77 [43.08,44.46] |
| C6 one turn | 49.44 [48.75,50.13] | 2.33 [2.13,2.55] | 48.23 [47.53,48.92] |
| C6 six turns | 83.03 [82.50,83.54] | .24 [.18,.32] | 16.73 [16.22,17.25] |
| C6 twelve turns (ceiling only) | 85.98 [85.50,86.46] | .15 [.11,.22] | 13.86 [13.39,14.35] |
| C6 common-window correlation .2 | 43.66 [42.97,44.34] | 20.12 [19.58,20.69] | 36.22 [35.56,36.89] |
| Three test windows, if same shape | 30.28 [29.65,30.92] | 4.56 [4.28,4.86] | 65.16 [64.50,65.82] |

With common-window correlation, delta=1 gives only 90.05% FAIL
[89.63,90.46], hence 9.95% missed FAIL [9.54,10.37], including 2.27% PASS
[2.08,2.49]. At delta=.5, PASS is 21.05% [20.49,21.62]. More turns do not
remove a trajectory or window component. See the sentinel-inclusion profile
for the effect of selecting that different benign input population; it never
increases m or treats the 12 repeated records as 12 independent clusters.

For a **single** D window, matched scale/no drift gives 1.48% PASS
[1.32,1.65], 25.23% false FAIL [24.63,25.83], 73.30% imprecise
[72.68,73.91]. If that failure is independently applied in every one of six
windows, `1-(1-.2523)^6` is about 82.5% probability of at least one false FAIL;
at eight it is about 90.2%. This is an analytic illustration under independent
windows, not a simulated R12 series-veto policy or an authorization to use one.

Count-only stopping output, from independent synthetic member/window losses:

| Member loss | Whole-window loss | Stop 6 % [95% MC] | Stop 7 | Stop 8 | Cap unresolved |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 100 [99.98,100] | 0 [0,.02] | 0 [0,.02] | 0 [0,.02] |
| .10 | 0 | 14.85 [14.36,15.34] | 83.42 [82.90,83.93] | 1.74 [1.56,1.93] | 0 [0,.02] |
| .15 | 0 | 1.14 [1.00,1.29] | 78.66 [78.08,79.22] | 19.96 [19.41,20.52] | .25 [.19,.33] |
| .05 | .10 | 37.51 [36.84,38.18] | 36.90 [36.23,37.57] | 17.53 [17.01,18.06] | 8.07 [7.70,8.46] |

These are assumptions about losses, not predictions of U3/battery/thermal
yield. They do not simulate informative exclusions, scorer fitting, or the
joint law of residuals and eligibility. An unresolved cap cannot become a
valid calibration by treating U6 as PASS.

## Fit for purpose and prospective choices

1. **At the registered size, retain an explicitly limited interpretation.**
   One prespecified pooled calibration look can detect a large common shift:
   delta=1 gives 99.74% FAIL in the baseline model. It does not assure a
   stability certificate: about one in four no-drift series is imprecise,
   rising to nearly seven in ten with low s_r and still worse with high ICC.
   Do not top up on U6 or spend the eighth window to improve an observed U6
   result: R12 authorizes extensions for counts only. Keep the current
   imprecise label and claim consequence (`pilot_protocol_v4.md:503-505,636-641`).

2. **If the requirement is >=95% no-drift PASS, increase independent benign
   trajectories prospectively rather than relaxing the margin.** For equal
   lengths and N independent trajectories, SE is approximately `2*sqrt(v/N)`.
   A sizing approximation is
   `N >= 4*v*(1.645+1.96)^2 / margin^2`.
   At L=3/rho=.5/matched scale, N is about 139 (about 70/pair), already above
   the default eight-window capacity of 112. A concrete simulated option is
   **14 benign per pair per window over six windows**, 84/pair, N=168:
   97.92% no-drift PASS [97.72,98.11], .01% false FAIL [0,.04]. Under low s_r
   it still gives only 74.53% PASS [73.92,75.12]. For protection against both
   rho=.9 and low s_r, the approximation needs about 397 trajectories; a
   **36/pair/window x six** candidate, 216/pair, N=432, gives 96.86% PASS
   [96.61,97.09] in that stress. These are changes to cost/roster and require
   fresh sizing and registration authority. They are not extra windows
   permitted by B3, and cannot cure shared-window dependence.

3. **Decide what FAIL is intended to assert.** The current point rule is not
   a level-5% test of exceeding the tolerance: boundary delta=.5 produces
   about 50% FAIL. A prospective interval-based FAIL rule,
   `abs(b)-1.645*SE > .5*s_used`, makes uncertainty symmetric with PASS.
   At C6/matched scale it gives 5.30% FAIL [5.00,5.62] at the boundary, but
   only 87.97% FAIL [87.51,88.41] at delta=1 (12.03% miss [11.59,12.49]).
   It does **not** improve PASS precision or fix low/high s_r or window
   clustering. Do not silently replace the point rule with this candidate.

4. **Freeze the estimand and dependence before a stability claim.** A pooled
   common-shift test can miss opposite pair drifts; with balanced equal-length
   pairs their mean effects cancel exactly. A repeated within-window drift
   pattern can likewise cancel between whole-series halves. Neither is the
   common late-half step simulated here. Choosing per-pair or within-window
   checks needs new OC and a prespecified multiple-look consequence. The
   eta=.2 stress already refutes an unconditional reliability claim for the
   present trajectory-only SE. More trajectories in the same six windows
   cannot supply more independent windows; a window-aware contrast/uncertainty
   and its required window count need their own prospective OC, not an
   unsupported correction factor in this report.

My recommendation before W1 is to **keep U6 as the prespecified pooled,
limited diagnostic unless the lead explicitly funds and registers a stronger
stability design**. If high-probability PASS is necessary, the 14/pair option
is a concrete baseline improvement, not robustness to the full sensitivity
set. A claim-veto interpretation must also resolve window dependence, s_r
estimation, fit uncertainty, test-only versus cumulative inputs, and whether
pair-specific drift matters. No single output here admits W1 or validates
the complete monitor/FPR/detection-rate claim.

## Verification, custody and handoff

- `python3.13 -B docs/align/v4/u6-oc/simulate_u6_sol1.py --check` — PASS:
  9 desk/helper equivalence fixtures plus classification/interval boundaries.
- `python3.13 -B -m unittest tests.align.test_v4_estimands` — 15 passed,
  .003 s.
- `python3.13 -B -m unittest tests.align.test_thermal_desk` — 25 passed,
  2.379 s. Modules ran sequentially. No full suite or pytest.
- Full Monte Carlo command above — exit 0; one run; 16 profiles x 20,000
  draws, plus 4 count-stop loss scenarios x 20,000 draws. Script syntax
  compile and `git diff --check` passed. No NumPy/MLX/Torch or model weights.
- Script SHA-256: `ff26e6832512579bb10954421f895e6e82d52a78d89b8a6677e6a3b8b9ba2c98`.
  Stdout SHA-256: `4f54909feb9c6f24f9e48d0e5ed44f3e2e54849b0575f7d0620191966fa0301e`.
- Files added: this report, `simulate_u6_sol1.py`, `U6-OC-sol1-output.txt`,
  and the handoff under `docs/run_reports/2026-11-07-u6-oc-sol1.md`.
  Product code and lead-owned coordination files are unchanged. No network,
  external study directory, real restricted directory, real measurement
  input, analysis pipeline, machine probe or running job was accessed.
- No MLX code or new native tests were added. This simulation needs no Metal
  run. The lead still owns actual W1/R1 qualification and the registered
  native/runtime gates outside this sandbox; these synthetic checks certify
  none of them.
- **Next exact step:** the lead compares the two independent OC reports,
  freezes the eligible U6 input population and look schedule together with
  the 3-versus-6 test cohort, and chooses the limited interpretation or a
  prospectively re-sized/re-derived stability rule before W1 registration.
  No coordination task was registered by this seat. Commit identity is in
  the Git commit carrying this report and the final handoff, not self-embedded.
