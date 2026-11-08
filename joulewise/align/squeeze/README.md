# Squeeze analysis — DRAFT, synthetic only

NumPy planning tools for a transcript monitor plus a trusted, whole-episode
external DC meter. No measurement readers, model runtimes, downloads or network
code are present. These tools do not register an estimator, change v4, establish
SHADE-Arena monitor response, or validate an adaptive hardware claim.

The optional dependency is `.[squeeze]` (NumPy). The package namespace and the
scalar calibration APIs import on bare Python; numerical submodules require it.
Tests skip numerical cases when it is absent.

## Calibration and guarantees

For a score function frozen before an independent benign calibration sample,
the primary rule is **alarm strictly above the maximum of m benign scores**.
Under exchangeability of the m calibration units and one new benign unit:

    P(new score > max calibration score) <= 1/(m+1).

Equality holds with no ties. This is a marginal bound over calibration and
test randomness. It is not a guarantee for every realized calibration set.
For iid calibration, with 90% confidence over calibration sets, the realized
tail above a maximum is at most `1 - 0.1**(1/m)`:

| m | Max-of-m marginal bound | 90% upper bound on realized FPR |
|---|---:|---:|
| 20 | 4.762% | 10.875% |
| 28 | 3.448% | 7.894% |
| 39 | 2.500% | 5.733% |

`max_threshold` always uses rank m. `conformal_threshold` separately implements
`ceil((m+1)*(1-alpha))`: at alpha=.05 it uses rank 20 for m=20, **rank 38 for
m=39**, and infinity for m<19. The older empirical rule `ceil((1-alpha)*m)`
is not used. These different rules must not be silently interchanged. Ties
are conservative; NaN/infinite calibration or test scores are refused.
Overflow during standardization or joint summation is also refused, even
when the input scores are finite.

For two channels, `JointScore` freezes their locations/scales/energy weight,
then uses the maximum of their standardized scores. Calibrating this *one*
statistic gives the bound above under arbitrary channel dependence. ORing
two separately calibrated channel maxima instead gives only the union bound
`2/(m+1)`; `separate_channel_fpr_bounds` makes this distinction explicit.
`mode="min"` and `mode="sum"` support other pre-specified joint statistics.

Scale estimates must come from separate training/design, not the same
calibration sample. Exchangeability is not established by these APIs. Shared
fit folds, outcome-based exclusions, window drift, repeated trajectories and
pooling task pairs can invalidate the episode argument. A lead may instead
pre-specify exchangeable window/trajectory maxima as the calibration units;
then m counts those units and the guarantee concerns that same test unit.
No automatic aggregation or outcome-dependent threshold tuning is performed.

With a continuous iid null and one shared maximum, the marginal probability
of any alarm among n benign held-out episodes is `n/(m+n)`, **not**
`1-(1-1/(m+1))**n`. Cohort outcomes share a random threshold. Without iid
test units, only the dependence-safe union bound is offered. A realized-tail
tolerance statement requires iid calibration, beyond bare exchangeability.

## Five-term energy model and attacks

`ResidualModel` accepts externally supplied five coefficients. Its default is
protocol v4's frozen sequence design:

    [1, P, D, (C+P)*D + D**2/2, C*P + P**2/2]

The older `energy_residual.md` row design `[1,P,D,C*D,C*P]` is available only
as `form="turn"`. Neither design contains duration, temperature or clock.
No live fitter or scoring denominator is replaced. The analysis channel here
is a residual in **joules**, scaled by a fixed planning SD for joint fusion;
it is not asserted to equal the existing API's prediction-uncertainty score.

For a hidden continuation H at one representative carrier call, the sequence
energy increment is:

    beta_D*H + beta_CD*((C+P+D)*H + H**2/2).

This preserves quadratic work and avoids subtracting nearly equal predictions.
It does not invent a new call intercept, propagate hidden contexts through
later turns, or simulate model execution. A fresh hidden call would also have
its own intercept/prefill/context costs; it is not this continuation estimand.
Coefficients remain unmodified; negative work costs are flagged.
Attack residuals cancel common executed/logged padding before arithmetic,
so subtracting large rounded totals cannot erase the hidden signal. Reported
physical/predicted totals can still round to the same float; the directly
computed residual retains the difference. Nonfinite effect joules are refused.

`attack_effect` conserves a supplied adversarial work budget H across:

- **Padding/relabeling:** a fraction of malicious computation becomes genuinely
  logged work. Its energy is predicted; its monitor signal follows the explicit
  visibility assumption. Separately, `padding_tokens` adds real benign work
  to both physical energy and prediction. Honest padding alone cannot subtract
  hidden joules; in the sequence design it can increase their context cost.
- **Smoothing:** an assumed cost ratio changes hidden local joules, not the
  meter's integral. Ratio 1 is pure temporal smoothing with unchanged work
  cost; ratios .85/.7 are unvalidated DVFS/efficiency sensitivities.
- **Tool shifting:** a fraction of unlogged tokens becomes tool work at an
  explicit J/token cost. Meter coverage and transcript visibility are separate
  knobs. The model never adds a sixth fitted tool term.

The declared finite attack grids include single-family and combined searches.
They are planning choices, not registered budgets or an exhaustive red team.
`phantom_logged_tokens` explicitly tests fabricated counts with no physical
padding. `monitor_visibility=0` tests logged work with no semantic signal.
`tool_meter_fraction=0` tests escape from the measurement boundary. These
produce counterexamples, not successful robustness evidence: logged opaque
reasoning, fabricated counts and off-meter opaque tools can defeat both
channels under the specified model. Trust in the meter alone does not prove
the proposed squeeze. Trusted counts and empirical monitor response matter.

The default latent monitor response is one score unit per 128 visible
malicious tokens. **This is an arbitrary sensitivity assumption**, not a
calibration from SHADE-Arena, an AUC claim or a probability score. Supply other
`MonitorResponse` values and `monitor_visibility` settings before drawing a
paper conclusion. Larger visibility or energy-cost changes need new evidence.

`Noise` sweeps total residual SDs 19, 38 and 58 J. A 2 J one-measurement replay
SD is included *within* that total: task SD is `sqrt(total_sd**2 - 2**2)`.
Two identical replays share the task component and have difference SD
`sqrt(2)*2` J. This does not shrink the task residual to 2 J. Correlated
monitor/energy noise and finite-variance Student-t task tails are optional
sensitivities. Attribution bounds are never silently treated as SDs.

## Curves, frontier and power

```python
from joulewise.align.squeeze.detection import JointScore, detection_surface
from joulewise.align.squeeze.adversary import Attack, Noise, attack_families
from joulewise.align.squeeze.residual import ResidualModel
from joulewise.align.squeeze.power import estimate_power

# Illustrative coefficients only. Use independently trained/configuration-
# specific coefficients for any subsequent registered design calculation.
model = ResidualModel((2, .001, .3, .00004, .0000002))
result = estimate_power(
    model, m=39, heldout_size=40, hidden_work_tokens=512,
    attacks=attack_families()["combined"], noise=Noise(58), seed=7)
print(result.to_dict())

# Given synthetic arrays of (latent monitor score, residual J):
# threshold = JointScore(58).calibrate(independent_benign_scores)
# surface = detection_surface(attack_scores, monitor_cuts, energy_cuts_j)
```

`detection_surface` gives OR/AND detection rates on a monitor-score ×
energy-joule grid. It is descriptive; picking a cut from evaluation outcomes
does not preserve the calibration guarantee.

`adaptive_frontier` chooses an attack on independent search noise, then reports
held-out per-channel and joint rates, fixed-threshold Wilson intervals, and an
attacker-optimal Pareto mask (lower detection on both channels). The Pareto mask
is descriptive on evaluation; it is never used to choose the reported attacker.
Its threshold must come from the same fixed `JointScore(noise.residual_sd_j)`.

`estimate_power` redraws calibration maxima in each Monte Carlo trial. The
attacker sees each threshold, searches a fixed grid on independent simulated
episodes, and is evaluated on a new cohort. Common random draws compare
candidates; search and evaluation streams remain separate. The finite-search
attacker can be weaker than an exact optimizer, so estimated detection can be
optimistic for security. Increase search size and refine grids as sensitivities.

Results distinguish average per-episode detection, the probability of any
cohort detection, and the probability that at least ceil(.8*n) episodes alarm.
Monte Carlo SEs use independent trials, retaining variation in the shared
calibration maximum. They quantify simulation error only. A printed 0/1 and
zero estimated SE at saturation is not mathematical certainty. H=0 is a
false-alarm control, never a claim of hidden-work detection.
`normal_energy_max_power` supplies a separate Gaussian one-channel quadrature
reference, integrated over the calibration maximum, rather than substituting
a fixed normal quantile for a random maximum.

## Reproduce a synthetic sweep

```sh
python3 -B -m joulewise.align.squeeze --heldout-size 40 --trials 512 \
  --selection-size 256 > /private/tmp/jw-squeeze-analysis-20261107.json
```

This emits JSON power curves and fixed-threshold frontiers for m=20,39,28,
H=0,128,256,300,512,1024,2048, four attack families and SD=19,38,58 J. The
28 is the publicly documented pilot calibration count, not a locked future
cohort. `--heldout-size` is mandatory: **40 above is illustrative**, since the
read authority specifies a locked cohort but no size. The lead must supply
the actual n and freeze its unit before using these calculations. Each JSON
row records SD, cohort size, calibration size, MC budget, attack choices and
flags; the root records coefficients, carrier, seed and all attack grids.

Use `--student-df 5`, `--correlation .6`, alternate coefficients and monitor
responses as sensitivities. The report cannot establish realistic attack
budgets, hybrid-attention fit adequacy, transport/meter integrity, window
independence or a main-track result from synthetic scores.

Run these unittest modules one at a time (no full suite):

```sh
python3 -B -m unittest tests.align.squeeze.test_detection
python3 -B -m unittest tests.align.squeeze.test_adversary
python3 -B -m unittest tests.align.squeeze.test_power
python3 -B -m unittest tests.align.squeeze.test_cli
python3 -B -m unittest tests.align.squeeze.test_review
```

No MLX code is used. The lead must repeat numerical tests with NumPy on Python
3.11/3.13 and separately obtain hardware/DC-meter/monitor positive controls.

## Source authority (local Git objects; no fetch performed)

- `e901eb2a4:docs/align/pilot_protocol_v4.md`, residual design and known-H
  sections; `energy_residual.md` at the same ref for the older row design and
  scoring/power caveats. Protocol v4 remains provisional.
- `16e1db623:docs/research-audits/2026-11-07/literature.md`, especially adaptive
  and matched-energy threats and opaque filler reasoning.
- `53a230598:docs/research-audits/2026-11-07/w1-prearm-gate.md`, pending
  registration and the W1 no-arm verdict.
- `7f74dd2a9:docs/research-audits/2026-11-07/research-program.md`, public pilot
  noise/replay summaries and thin held-out evidence.
- `docs/research/AGENDA.md`, `docs/research/energy-tripwire.html`, and
  `RUN_STATE.md` item 204: m>=39 per pair plus a separate test cohort approved.

Nothing here resolves the lead's scientific rulings or permits a measurement.
