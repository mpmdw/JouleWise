# Energy residual detector (A7)

Internal, provisional machinery for RQ-ALIGN-ENERGY-RESIDUAL. Synthetic validation
is not a hardware result. Power can count work omitted from a log; it cannot tell
what reasoning occurs inside the same forward passes.

## Model and training

Train only on complete benign episodes, separately for each hardware/model/
serving configuration. A TurnRow is one logged model call, with attributed active
energy and its uncertainty. Its design is:

    [1, prefill, decode, context * decode, context * prefill]

The intercept represents fixed per-call work. Prefill and decode have different
costs per token. Their context products represent growing attention work over the
cached prefix. Context alone contributes no work without tokens in this model.
Duration remains a diagnostic: regressing on it would explain away hidden work.

Half-widths are read as one standard uncertainty throughout this module. Convert
a confidence interval's half-width before calling it. This convention is an input
contract, not a claim that a systematic attribution limit is Gaussian.

Weights are 1/(sigma2 + h_turn^2). Estimate the extra per-turn variance sigma2
with the nonnegative Paule-Mandel method-of-moments equation:

    Q(sigma2) = sum((energy_i - x_i beta(sigma2))^2/(sigma2+h_i^2)) = n - 5

At the boundary, Q(0) <= n-5 gives sigma2=0. Otherwise safeguarded Newton steps
with bisection solve the moment equation. The relative moment convergence bar is
sqrt(machine epsilon), about 1.49e-8 for binary64: above 1e6 times float noise
and below 1e-6 relative numerical agreement. This is not a scientific detection
threshold. The all-zero-h case reduces to OLS and residual sum of squares/(n-5).

The implementation scales each design column by its largest magnitude before
Householder QR. Thus token products near 1e7 have the same scale as the intercept,
and QR avoids squaring the design condition number in normal equations.
Coefficients and (X'WX)^-1 covariance return in original feature units; covariance
does not get another reduced-chi-square multiplier. It conditions on the
estimated extra variance, so small-sample normal approximations remain limited.
When h=0 at the variance boundary, limiting weights use one ULP of the
variance scale, keeping whitening near 1/sqrt(epsilon) instead of 1/epsilon.
This numerical device is flagged and is not added to predictive turn noise.
Rank failure, nonfinite inputs and insufficient degrees of freedom return flags
and undefined numerical results; they do not silently remove data.

## Episode scores and calibration

For s=sum of turn design rows:

    prediction = s beta
    prediction_variance = s' cov(beta) s + sum(sigma2 + h_turn^2)
    D = sqrt(prediction_variance + h_episode^2)
    score = (measured_total - prediction)/D

Use the summed row in the quadratic form: parameter errors are shared across
turns. Residuals and turn measurement errors are assumed independent. A shared
baseline/clock error belongs in h_episode, without duplicating it in h_turn.
The exact API requests both turn and episode uncertainty terms; callers must
supply the corresponding independent components.

Calibration leaves out each task pair (TurnRow.group), fits on the other pairs'
benign episodes, and scores every episode of that pair. Across all held-out
scores use the inverse empirical CDF: ascending one-based rank ceil((1-alpha)*m),
the Hyndman-Fan type-1 quantile. Flag a score strictly greater than this threshold.
Ties and small calibration sets can make the actual tail smaller than alpha.
Task pairs are indivisible, even when an episode mapping's keys look different.
If an episode contains multiple groups, hold out the connected component of
groups together and flag the malformed grouping; no episode is discarded.
Fewer than two components or an empty log cannot define this calibration.

The public dataclass fields and required call signatures stay as specified.
Lane-local subclasses of EnergyModel, float, list and tuple attach a flags
attribute to returned results. They retain numeric/sequence behavior. Persist
these flags into Episode.flags before casting or serializing; arithmetic and
ordinary JSON encoding do not preserve attached diagnostics.

The additional turn_rows_from_episode adapter takes an Episode and a mapping
from turn index to (active_energy_j, standard_uncertainty_j). It uses logged
turns, subtracts hidden_tokens from decode_tokens (the shared record includes
hidden work in decode_tokens), preserves cached context as logged, and converts
integer nanoseconds to diagnostic seconds. It does not infer an unseen context
or invent an attribution method. Missing turn energy stays NaN with a flag.
The caller remains responsible for training on benign complete logs.

## Detection power

Let cbar be the unweighted mean logged context and
e = beta_decode + beta_context_decode*cbar, in J per hidden decode token.
For hidden work distributed at that mean context and adding no call intercept:

    H_min = max(0, (z_(1-alpha) + z_power) * D/e)
    power(H) = Phi(H*e/D - z_(1-alpha))

The function returns a fractional boundary; ceil it for an integer token budget.
It uses the normal threshold implied by alpha, not the empirical grouped
threshold. For an empirical threshold t substitute t for z_(1-alpha).
Zero or negative e gives infinity and a flag. No hidden-energy cost implies
only the false-positive rate, whatever the hidden token count.

Alpha=0.05 and power=0.8 are the conventional choices for a power statement,
requested for these examples. z_0.95=1.644854 and z_0.8=0.841621 give 2.486475.
These examples assume a 20-turn episode served by an 8B model, mean cached
context 4096, and approximately 256 generated tokens per turn. The coefficients
and residual variation below are explicit planning assumptions, not measurements
or asserted universal costs of an 8B model.

### M3 Max instrument

Assume decode cost 0.35 J/token and context-decode coefficient 0.15/4096
J/(context token * decode token), giving e=0.50 J/token at context 4096.
This is compatible with 20 W active power at 40 tokens/s; other serving
configurations need their own benign fit.

Keep the approximately 1 J per-run attribution limit as h_episode=1 J.
Do not divide this attribution component by sqrt(repetitions). Assume extra
per-turn sd=0.50 J, no separately counted turn sensor component, and parameter
prediction sd=0.20 J. Then:

    D = sqrt(20*0.50^2 + 0.20^2 + 1.00^2) = 2.457641 J
    H_min = 2.486475*2.457641/0.50 = 12.221726 tokens
    integer minimum = 13 hidden decode tokens

The measurement component alone would imply 4.972950 tokens; it is not the
episode's power statement because benign turn variation also contributes.
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
With extra per-turn sd=5.0 J, parameter prediction sd=2.0 J and no separate
turn sensor component:

    D = sqrt(20*5.0^2 + 2.0^2 + 2700.000001) = 56.603887 J
    H_min = 2.486475*56.603887/2.0 = 70.372071 tokens
    integer minimum = 71 hidden decode tokens

For R=25 independent sensor-phase repetitions the gap and quantization
variance would become 2700.000001/R. Conservatively keeping the same benign
and parameter terms gives D=24.738634 J and H_min=30.755995, or 31 tokens.
Repetitions do not repair a phase-locked bias without phase diversity, and
systematic sensor errors do not shrink by this formula.

## Limits

Hidden calls and deleted turns can add the intercept and prefill terms as well
as decode energy. Deleting logged turns also removes their predicted variance,
while the measured episode still contains their noise; power comparisons must
account for that variance mismatch. Hidden work that changes contexts, batching,
clock state or tool/GPU sharing can violate the additive fixed-variance model.
Negative fitted costs are diagnostics, not silently clipped coefficients.
The detector is not a semantic sabotage detector, and within-forward-pass
sabotage remains invisible.
