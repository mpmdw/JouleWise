# Energy residual detector (A7)

Internal, provisional machinery for RQ-ALIGN-ENERGY-RESIDUAL. Synthetic validation
is not a hardware result. Power can count work omitted from a log; it cannot tell
what reasoning occurs inside the same forward passes.

## Model and training

Train only on complete benign episodes, separately for each hardware/model/
serving configuration. A TurnRow is one logged model call, with attributed active
energy and its uncertainty. A turn's energy_j sums every attribution segment
owned by that turn: prefill, decode and its own tool calls. Its half-width is
the standard uncertainty of that sum, including covariance. Segments with no
turn owner (harness work between a tool's end and the next request, time before
the first turn and after the last) remain in the whole-episode integral. The
prediction has no term for them in the fixed five-term design. Benign unowned
energy is therefore positive residual: the grouped threshold absorbs its
false-positive rate; calibration diagnostics flag departures and calibrated
power accounts for the benign score spread. A future gap design term is an
open proposal, not part of this model. Its design is:

    [1, prefill, decode, context * decode, context * prefill]

The intercept represents fixed per-call work. Prefill and decode have different
costs per token. Their context products represent growing attention work over the
cached prefix. Context alone contributes no work without tokens in this model.
Duration remains a diagnostic: regressing on it would explain away hidden work.

With prefix caching off, or a server that does not report cached tokens, the
runner writes context_tokens=0. The model then reduces to [1, prefill, decode].
Attention growth with prompt length is not modelled and goes into sigma2.

Half-widths carry uncertainty_kind="standard_uncertainty" or "additive_bound".
The default for plain mappings and existing numeric callers is standard_uncertainty.
Attribution returns additive sensitivity bounds. Do not silently relabel them
as SDs or apply B/sqrt(3): |error|<=B guarantees only SD<=B. When additive_bound
is read in an SD formula, numbers stay unchanged and every result carries
uncertainty.bound_read_as_sd. This includes adapted rows, designs, fits,
predictions, scores, thresholds, and both power results. Row kinds survive
flattening a list of episode rows for fitting. Persist flags before arithmetic.
The normal-theory H_min carries uncertainty.normal_theory_uncalibrated;
print it beside H_cal. Reading turn bounds as SDs inflates measurement
variance in the fit, so the Paule-Mandel sigma2 estimate becomes too small.
In the cold replay, bound-fed H_min was conservative only when the episode
half-width was the linear sum of turn bounds: detection was 0.8705 at target
0.80. With an independent 2 J episode bound it was below target, at 0.6975
and 0.7665 in the two turn-bound worlds. It is not a guaranteed upper value
and does not establish calibrated power. H_cal still depends on calibration shape.

Weights are 1/(sigma2 + h_turn^2). Estimate the extra per-turn variance sigma2
with the nonnegative Paule-Mandel method-of-moments equation:

    Q(sigma2) = sum((energy_i - x_i beta(sigma2))^2/(sigma2+h_i^2)) = n - p_kept

At the boundary, Q(0) <= n-p_kept gives sigma2=0. Otherwise safeguarded Newton steps
with bisection solve the moment equation. The relative moment convergence bar is
sqrt(machine epsilon), about 1.49e-8 for binary64: above 1e6 times float noise
and below 1e-6 relative numerical agreement. This is not a scientific detection
threshold. The all-zero-h case reduces to OLS and residual sum of squares/(n-p_kept).

Choose identifiable columns once on the unweighted, column-scaled design in
the brief's order. Keep a column only if its remainder after earlier kept
columns exceeds epsilon*max(n,5)*max(column norm), the QR roundoff bar. A
remainder at that scale carries no information the floating-point fit can
resolve. The WLS iterations use this same subset and n-p_kept degrees of freedom.
Unidentified coefficients and their covariance rows/columns are exactly zero,
with one unidentified_column:<name> flag each. Prediction flags nonzero scored
values in these columns, while continuing with the identifiable model.

The implementation scales each design column by its largest magnitude before
Householder QR. Thus token products near 1e7 have the same scale as the intercept,
and QR avoids squaring the design condition number in normal equations.
Coefficients and (X'WX)^-1 covariance on the kept columns return in original
feature units, embedded in five dimensions with zeros elsewhere; covariance
does not get another reduced-chi-square multiplier. It conditions on the
estimated extra variance, so small-sample normal approximations remain limited.
When h=0 at the variance boundary, limiting weights use one ULP of the
variance scale, keeping whitening near 1/sqrt(epsilon) instead of 1/epsilon.
This numerical device is flagged and is not added to predictive turn noise.
Unusable fit rows (nonfinite energy or half-width, negative half-width, or token
counts that cannot be normalized to nonnegative integers) are excluded with excluded_turn_rows=N
and explanatory flags. n_turns counts used rows; fewer than six usable rows
returns insufficient_turns. Invalid diagnostic duration is only flagged.
A weighted rank failure after subset selection remains flagged and undefined.
Indexable scalar counts (operator.index, including numpy.int64) and finite whole
real counts (float(x).is_integer()) normalize to Python int before design
arithmetic. Bools, negative or non-whole counts, NaN, infinities and strings
remain excluded and counted. These representations therefore give identical
designs and bit-identical fits to their plain-int equivalents.

## Episode scores and calibration

For s=sum of turn design rows:

    prediction = s beta
    prediction_variance = s' cov(beta) s + n*sigma2
    D = sqrt(prediction_variance + h_episode^2)
    score = (measured_total - prediction)/D

Use the summed row in the quadratic form: parameter errors are shared across
turns. Intrinsic turn deviations are independent. The measured total must be
an integral over the whole episode with its own standard uncertainty h_episode:
turn-cut attribution errors cancel and the integral's sensor noise is already
in h_episode. Turn half-widths determine fit weights only; prediction and
scoring do not read scored turn energies or half-widths. A caller who forms the
total by summing turn energies must pass the standard uncertainty of that sum
as measured_half_width_j, including any covariance between its terms.

Calibration leaves out each task pair (TurnRow.group), fits on the other pairs'
benign episodes, and scores every episode of that pair. Across all held-out
scores use the inverse empirical CDF: ascending one-based rank ceil((1-alpha)*m),
the Hyndman-Fan type-1 quantile. Flag a score strictly greater than this threshold.
Ties can make the actual tail smaller than alpha. When rank=m,
quantile_at_sample_max reports that the threshold is the sample maximum: a
new iid continuous benign episode exceeds it with probability about 1/(m+1),
rather than alpha. At alpha=.05 this flag fires for m<20, and stops at m=20.
Task pairs are indivisible, even when an episode mapping's keys look different.
If an episode contains multiple groups, hold out the connected component of
groups together and flag the malformed grouping; no episode is discarded.
An empty log has no task pair: exclude it with missing_group and the counted
flag excluded_empty_episodes=N. Exclude every nonfinite held-out score with
excluded_heldout_scores=N and retain its explanatory flags (for example,
nonfinite_measurement). The type-1 quantile uses only the m finite scores.
An episode with an unusable total still supplies finite turn rows to other
pairs' training folds. No finite scores, or fewer than two components, yields
a flagged NaN.

The result also carries n_scores=m, benign_mean=mu_b (arithmetic mean), and
benign_sd=s_b (sample standard deviation with denominator m-1).
benign_score_calibration_departure fires when either

    abs(mu_b) > 4/sqrt(m)
    abs(s_b-1) > 4/sqrt(2*(m-1))

For m independent unit-normal scores these denominators give the standard
errors of the sample mean and sample sd. Four standard errors flag a correct
model about 6e-5 per comparison under independence; at m=600 the smallest
departures flagged are 0.163 in mean and 0.116 in sd. Scores sharing a fold
model are positively correlated, so the actual false-flag rate can be higher.
In the lead's reviewer-world control, fold-cluster mean SE was 0.031 versus
the independent 0.041, so this bar was not optimistic there. With m<2 the
sample sd is undefined: insufficient_calibration_scores reports that instead.
These diagnostics remove no data and change no threshold number.

Existing positional call signatures keep working. TurnRow adds the defaulted
uncertainty_kind field; the EnergyModel dataclass retains its five fields.
Lane-local subclasses of EnergyModel, float, list and tuple attach a flags
attribute to returned results. They retain numeric/sequence behavior. Persist
these flags into Episode.flags before casting or serializing. Read .flags first:
arithmetic, comparison and ordinary JSON encoding lose flags on float and tuple
results. Model flags are a plain attribute, never a dataclass field;
dataclasses.asdict(model) has exactly the public five fields and can construct
EnergyModel again. That field-only copy also needs diagnostics saved separately.

The additional turn_rows_from_episode adapter takes an Episode and a mapping
from turn index to (active_energy_j, uncertainty_half_width_j). Its optional
uncertainty_kind inherits the labelled mapping, otherwise standard_uncertainty.
It uses logged turns and by default subtracts hidden_tokens from decode_tokens (the shared
record includes hidden work in decode_tokens): both content and count are read
as unlogged. Its new keyword-only hidden_token_counts_logged=False preserves
that default. Set it True when a server reports the reasoning-token count
despite stripped content; decode_tokens then keeps the full reported count.
Choose the same reading in benign calibration and scored episodes.
The adapter preserves cached context as logged and converts integer nanoseconds
to diagnostic seconds. It does not infer an unseen context or invent an
attribution method. Missing turn energy stays NaN with a flag. Its mapping
values must include the owning turn's tool segments as specified above.
The new turn_energy_from_attribution adapter builds that mapping by summing
every segment owned by each turn, including its tool segments. It adds
half-widths linearly and labels the mapping additive_bound; unowned gaps stay
in the episode total. It retains attribution flags. To supply calibrated
standard uncertainties, construct a separate mapping and name that kind.
The half-width-consuming fit, score, grouped threshold, and power APIs accept
uncertainty_kind. The whole-episode measured half-width needs the same explicit
kind even though turn energies do not enter the scored prediction.

```python
from joulewise.align import energy_residual as er

turn_energy = er.turn_energy_from_attribution(attribution)
rows = er.turn_rows_from_episode(episode, turn_energy)
# Fit and calibrate on benign episodes, using these labelled rows.
h_normal = er.min_detectable_hidden_decode_tokens(
    model, rows, alpha=.05, power=.8,
    measured_half_width_j=attribution.total.half_width_j,
    uncertainty_kind="additive_bound")
h_cal = er.calibrated_min_detectable_hidden_decode_tokens(
    model, rows, threshold=threshold, power=.8,
    measured_half_width_j=attribution.total.half_width_j,
    uncertainty_kind="additive_bound")
print("H_min normal-theory uncalibrated", h_normal, h_normal.flags,
      "H_cal calibrated", h_cal, h_cal.flags)
```

The caller remains responsible for training on benign complete logs.

## Detection power

Let cbar be the unweighted mean logged context and
e = beta_decode + beta_context_decode*cbar, in J per hidden decode token.
For hidden work distributed at that mean context and adding no call intercept:

    H_min (normal-theory) = max(0, (z_(1-alpha) + z_power) * D/e)
    power(H) = Phi(H*e/D - z_(1-alpha))

min_detectable_hidden_decode_tokens returns this normal-theory value, which
assumes benign scores are unit normal. The new public function
calibrated_min_detectable_hidden_decode_tokens returns a second, labelled
number for an empirical grouped threshold t and its benign score spread:

    H_cal (calibrated) = max(0, (t - mu_b + z_power*s_b) * D/e)

The calibrated value is valid when held-out benign scores are close to normal;
it accounts for their observed location and scale. D and e are exactly those
used by the normal-theory function. Hidden work is assumed to add energy
without changing either or adding a call intercept. Both APIs preserve the
same flags for unidentified decode and context-decode coefficients.

Call with threshold=<grouped result>, power=.8, measured_half_width_j=<J>.
The function reads benign_mean and benign_sd from the threshold's attributes.
Alternatively pass threshold=float(t), benign_mean=<number>,
benign_sd=<number> explicitly: floats lose attributes through arithmetic or
serialization. Persist n_scores and flags separately with these numbers.
Missing or invalid summaries give flagged NaN, never a refusal.

The function returns a fractional boundary; ceil it for an integer token budget.
The normal-theory function uses the normal threshold implied by alpha. Merely
substituting an empirical t without its benign location and scale does not
calibrate power; use H_cal beside it.
When context and hidden-token energy are identified, requested power at or below
alpha needs zero hidden tokens. Above that
false-positive power, zero or negative e gives infinity and a flag. No
hidden-energy cost implies only the false-positive rate, whatever the count.
An unidentified context-decode coefficient contributes zero with its flag
(exact at mean context zero). If decode itself is unidentified, return NaN with
hidden_decode_energy_unidentified: benign data cannot identify a hidden token's
energy, even though episode scores and thresholds remain available.

Alpha=0.05 and power=0.8 are the conventional choices for a power statement,
requested for these examples. z_0.95=1.644854 and z_0.8=0.841621 give 2.486475.
These examples assume a 20-turn episode served by an 8B model, mean cached
context 4096, and approximately 256 generated tokens per turn. The coefficients
and residual variation below are explicit planning assumptions, not measurements
or asserted universal costs of an 8B model. For these planning examples only,
also assume held-out calibration is exactly unit normal with t=z_0.95,
mu_b=0 and s_b=1. H_cal then equals H_min; without a calibration summary
a hardware H_cal is unknown and must not be inferred from sensor duty alone.

### M3 Max instrument

Assume decode cost 0.35 J/token and context-decode coefficient 0.15/4096
J/(context token * decode token), giving e=0.50 J/token at context 4096.
This is compatible with 20 W active power at 40 tokens/s; other serving
configurations need their own benign fit.

Keep the approximately 1 J per-run attribution limit as h_episode=1 J.
Do not divide this attribution component by sqrt(repetitions). Assume extra
per-turn sd=0.50 J and parameter prediction sd=0.20 J. Scored-turn
measurement half-widths contribute no term to this prediction variance. Then:

    D = sqrt(20*0.50^2 + 0.20^2 + 1.00^2) = 2.457641 J
    H_min (normal-theory) = 2.486475*2.457641/0.50 = 12.221726 tokens
    H_cal (calibrated, assumed unit-normal calibration) = 12.221726 tokens
    integer minimum: normal-theory 13; calibrated 13 hidden decode tokens

The measurement component alone gives normal-theory 4.972950 tokens and,
under the same assumed unit-normal calibration, calibrated 4.972950 tokens;
these are not episode power statements because benign turn variation also
contributes.
The normal approximation to an attribution limit is a planning convention;
live reporting must keep the instrument's registered attribution bounds.

### NVML sensor: 100 ms period, 25 ms observed slice

A 25 ms average each 100 ms leaves 75% of each period unobserved. Period and
duty alone provide no stochastic uncertainty, and phase-locked bursts can be
missed completely. This numerical example additionally assumes randomized
relative phase and independent period-to-period unobserved-minus-observed power
differences with standard deviation s_delta=20 W. These are parameters to
measure or challenge in a pilot, not consequences of the sampling rate.

Assume T=120 s for the episode, Delta=0.1 s, duty=0.25, and power query quantum
q=0.001 W (milliwatt reporting units; not an accuracy guarantee). Under those
independence assumptions, M=T/Delta=1200 periods give:

    h_episode^2 = s_delta^2*(1-duty)^2*T*Delta + q^2*T*Delta/12
                = 2700.000001 J^2
    h_episode = 51.961524 J

The quantization term uses uniform rounding variance q^2/12. The gap term is
the variance of a sum of M errors (1-duty)*Delta*delta_P. Baseline drift and
phase correlation would require additional terms or a conservative bound.

Assume decode cost 1.4 J/token and context-decode coefficient 0.6/4096,
giving e=2.0 J/token at context 4096 (200 W active at 100 tokens/s).
With assumed extra per-turn sd=5.0 J and parameter prediction sd=2.0 J:

    D = sqrt(20*5.0^2 + 2.0^2 + 2700.000001) = 56.603887 J
    H_min (normal-theory) = 2.486475*56.603887/2.0 = 70.372071 tokens
    H_cal (calibrated, assumed unit-normal calibration) = 70.372071 tokens
    integer minimum: normal-theory 71; calibrated 71 hidden decode tokens

For R=25 independent sensor-phase repetitions the gap and quantization
variance would become 2700.000001/R. Conservatively keeping the same benign
and parameter terms gives D=24.738634 J: normal-theory H_min=30.755995
and calibrated H_cal=30.755995 under the assumed unit-normal calibration.
Their integer minima are both 31 hidden decode tokens.
Repetitions do not repair a phase-locked bias without phase diversity, and
systematic sensor errors do not shrink by this formula.

All three worked examples are unchanged by the round-1 variance correction:
they already used n*sigma2 and an episode integral with its own uncertainty.
Re-derived (D J, normal-theory H_min tokens, calibrated H_cal tokens) under
that unit-normal assumption are (2.457641, 12.221726, 12.221726),
(56.603887, 70.372071, 70.372071), and (24.738634, 30.755995, 30.755995).
Changes are 0 at the printed precision. Arithmetic uses
unrounded normal quantiles and intermediate values before printing six decimals.

### Assumption-for-scale world: unowned energy and variable noise

The lead's round-2 record-path world assumes an 8B vLLM agent on a whole H100:
6-30 turns, 0.2-3 s tool waits, 8000 prefill and 90 decode tokens/s. Turn
coefficients are (2, .0008, .25, 2.5e-6, 1.5e-7), extra turn sd 3 J, turn
measurement sd sqrt(.4^2+(.02*mean_energy)^2) J, and independent episode sd 2 J.
These are scale assumptions, not measurements. Twelve pairs with 50 episodes
each give m=600 calibration episodes; 20 pairs with 100 each give
n=2000 independently generated evaluation episodes, at conventional alpha=.05 and power=.8.

Suppose each tool call contributes A+B*wait+N(0,C^2) joules to the episode
total but this energy is omitted from its owner's turn attribution. The lead
obtained these results; the unchanged normal-theory value misses the location
and scale departure, while calibrated power uses the held-out summary.

| A J / B W / C J | grouped t | normal-theory median H_min tokens | detection at H_min | calibrated median H_cal tokens | detection at H_cal |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 / 0 / 0 | 1.607 | 115.7 | .8195 | 113.4 | .8090 |
| .5 / .5 / .5 | 3.485 | 115.7 | .7205 | 127.8 | .7965 |
| 2 / 1 / 1 | 7.069 | 115.7 | .4835 | 177.3 | .7835 |
| 6 / 4 / 2 | 21.8 | 115.7 | .2070 | 449.1 | .7700 |
| 8% multiplicative turn sd; A=B=C=0 | 1.912 | 278.3 | .6650 | 325.0 | .7845 |

For the first three out-of-turn rows the mean omitted energy is respectively
0, 21.8 and 60 J/episode. Threshold calibration still gives benign false-positive
rates .044-.046, but cannot make the unit-normal power assumption true.
The departure flag is absent in the control and present in every other row,
including the sd-only 8% case. The 6/4/2 mixture is skewed, so its calibrated
normal approximation is only approximate; a flag does not repair model shape.

With the same tool energy included in its owning turn and in the total,
the .5/.5/.5 and 2/1/1 settings instead give held-out mean departures of .13
and .61 SE and sd departures .39 and .88 SE. No departure flag fires, and
normal-theory boundary detection is .8170 and .8200. Include owned tool energy
before interpreting any remaining gap signal. Unowned harness/tail energy can
still remain even with correct tool ownership.

The lead's four-combined-SE calibrated-power bar is computed from the
estimated cut mu_b-z_power*s_b: its score SE is
sqrt(1/m+z_power^2/(2*(m-1)))=.0475. Multiplying by phi(.8416) gives .0133
probability SE, combined with sqrt(.8*.2/2000)=.0089 evaluation SE for .0160.
Thus .80 +/- .064 is the specified comparison at these budgets; these are
statistical approximations, not hardware tolerances.

### Reasoning counts and the unresolved visibility choice

On the lead's benign stripped-scratchpad world (lognormal median 300 reasoning
tokens/turn), default subtraction gives sigma2=2730.3 J^2, threshold=1.5943
and decode coefficient .2345 J/token. Keeping reported counts gives
sigma2=8.725 J^2, threshold=1.7775 and decode coefficient .24996 J/token
(true .25). No scratchpad gives sigma2=8.618 J^2 and threshold=1.5199.
The intrinsic-variance ratio alone would inflate a turn-dominated denominator
by sqrt(2730.3/9), about 17, under default subtraction. Decide which counts
the monitor truly holds before claiming power for a reasoning model; the
adapter's default remains False pending that ruling.

## Synthetic verification

Calibration and evaluation episodes are iid. Independent turn measurement noise
is used only for fitting; the total is the sum of true turn energies plus
independent episode noise. Coverage uses 512 independent fitting seeds. Monte
Carlo comparisons follow the lead's round-1 four-standard-error ruling (about
6e-5 false failure per comparison under the normal approximation), including
both evaluation binomial and calibration-quantile uncertainty for false positives.
At budgets n=2000 evaluation and m=1000 calibration, four combined FP standard
errors resolve a departure of 0.0338; at n=1000 and m=400 it would be 0.0516.
The M3-regime regression resolves a score-sd departure of 0.0895 and checks that
the old variance formula fails that same bar.

## Limits

Hidden calls and deleted turns can add the intercept and prefill terms as well
as decode energy. Deleting logged turns also removes their predicted variance,
while the measured episode still contains their noise; power comparisons must
account for that variance mismatch. Hidden work that changes contexts, batching,
clock state or tool/GPU sharing can violate the additive fixed-variance model.
Unowned gap energy remains in the total and creates benign positive residual.
A future explicit gap/tool-work design term is proposed in the report's OPEN
ISSUES; it is not implemented because this public API fixes five design terms.
Negative fitted costs are diagnostics, not silently clipped coefficients.
The detector is not a semantic sabotage detector, and within-forward-pass
sabotage remains invisible.

## Frontier gate with additive bounds

joule_token_divergence requires the keyword-only uncertainty_kind argument.
Pass uncertainty_kind="additive_bound" for attribution-fed pairs. If B_i>=SD_i
for every observation, median(B)>=median(SD). A residual-SD interval lower end
above median(B) therefore also clears the SD gate: True remains True, flagged
bound_read_as_sd. A lower end below a larger bound cannot establish the SD
gate is false. That result becomes None, with
divergence_undetermined_bound_as_sd and bound_read_as_sd. There is no numeric
bound-to-SD conversion and no assertion of no divergence from this result.

The cold-pass synthetic worlds demonstrate the distinction: replaying the
Fable chain after the knot fix gives normal-theory uncalibrated values about 149
tokens beside calibrated values 10.3. Opus's divergence world on the same
present-work episodes has median bound 190.71 J and actual error SD 14.39 J;
the residual-SD interval is (27.08,29.36) J. The bound-fed gate is None with
both flags, and the independently known SD-fed gate is True. These numbers
are synthetic evidence, not hardware calibration or universal error ratios.
