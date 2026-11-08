# Behaviour-channel desk analysis

`behaviour_channel.py` and `scripts/interp_energy/behaviour_energy.py` predict
energy from supplied counts and coefficients. They never collect power, load a
model, fit coefficients, discover datasets or resolve provenance strings. This
is exploratory Stage 0 tooling for [the design study](../../docs/research-audits/2026-11-07/interp-weight-edit-energy.md)
and its [checks](../../docs/research-audits/2026-11-07/interp-weight-edit-energy-checks.md),
not a registration or hardware validation. The implementation is standard
library only; importing it requires neither MLX nor Torch.

## Model and units

For an answer with `p` prefill tokens, `d` decode tokens, and full answer-window
duration `t` seconds:

```text
K = p*d + d*(d-1)/2
E_gross = fixed_j + a*p + b*d + c*K + idle_w*t
```

`a` and `b` are J/token; `c` is J/(decode token × context token), abbreviated
`context_j_per_token_squared`. `K` sums the contexts `p, ..., p+d-1`, one per
reported decode token. Use matching token conventions when calibrating. This
is a linear context-cost approximation, not a universal hardware law. No
extra quadratic prefill term is implied.

With `coefficient_basis: "above_idle"`, token coefficients and `fixed_j` exclude
idle. Adding the supplied idle baseline gives gross energy; the above-idle
secondary view is also reported. `duration_s` is mandatory in both arms if
either has nonzero `idle_w`: token counts alone do not identify idle joules
or the counterfactual idle decomposition. With
`coefficient_basis: "gross"`, coefficients/fixed overhead already include idle;
`idle_w` must be zero and the above-idle result is null. This follows D-067's
gross-first reporting rule and avoids charging idle twice. Rates, context
slope, fixed overhead and power must be nonnegative, finite numbers.

J/correct is **total modeled energy of all attempts / number correct**. It is
not the average energy of correct attempts. Zero correct answers yields null
with an explicit inference status; no pseudocount is added.

## Exact decomposition and uncertainty

Let `x = (p, d, K, t, 1)` and `theta = (a, b, c, idle_w, fixed_j)`. For energy
per answer, `u` is the mean of `x`. For energy per correct, `u = mean(x) /
accuracy`. The change is always edited minus base:

```text
behaviour = ((theta_edit + theta_base)/2) · (u_edit - u_base)
rate      = (theta_edit - theta_base) · ((u_edit + u_base)/2)
delta     = behaviour + rate
```

Both arms must use the same coefficient basis. The caller must also supply
coefficients for the same physical energy boundary (for example GPU rail or DC).
This symmetric allocation splits the work/rate interaction equally between
the two channels. It is an accounting identity (up to floating point rounding),
not a causal identification of operand-switching physics. The output also
breaks it into:

- `token_count_j`: behaviour from prefill/decode counts and context exposure.
- `per_token_j`: changes in prefill/decode/context coefficients at midpoint work.
- `idle_duration_j` and `idle_power_j`: duration and baseline-power effects.
- `fixed_count_j` and `fixed_rate_j`: fixed-overhead exposure and coefficient effects.

`behaviour_j = token_count_j + idle_duration_j + fixed_count_j` and
`rate_j = per_token_j + idle_power_j + fixed_rate_j`. Per answer, the fixed-count
term is zero. Per correct it also captures changing attempts per correct answer.
Thus a correctness-only improvement can reduce J/correct even at fixed tokens.
With a shared energy model all rate terms are zero **by assumption**. This
cannot establish that a real weight edit has zero fixed-token energy effect.

The delta method uses normal intervals from analytic influence functions. For
`m = mean(x)`, correctness mean `r`, and a coefficient vector `q`, the per-correct
influence is `[q·(x-m) - (q·m/r)*(correct-r)] / r`. This retains the covariance
of energy, correctness and, in paired mode, both arms. Percentile bootstrap
intervals resample whole problem pairs and recompute all ratios; unpaired mode
resamples the two arms independently. Each arm needs at least two independent
units. Paired IDs must be unique with matching rosters; input ordering need not
match. Use one independent problem/block per ID. Repeated seeds within the same
problem need a separately specified cluster analysis and are not supported.

If a bootstrap draw has zero correct answers for an arm needed by a statistic,
its ratio is undefined. The tool reports the count and withholds that statistic's
bootstrap interval instead of silently deleting those draws. In the small Astra
base arm this can happen frequently. Finite delta-method intervals with few
correct answers remain asymptotic approximations; all-correct samples also have
a boundary warning. Neither method guarantees nominal coverage for sparse
ratios or tiny samples.

Intervals condition on supplied coefficients; calibration uncertainty,
systematic baseline bounds, instrument floors, multiplicity and claim gates
are **not included**. This does not replace D-053's registered contrast analysis
or the BYTES worst-case metrological bounds. No outcomes are dropped.

## JSON CLI

Supply explicit coefficients and provenance. This deliberately synthetic model
is an example only; there are no default J/token values:

```json
{
  "base_model": {
    "prefill_j_per_token": 0.02,
    "decode_j_per_token": 0.10,
    "context_j_per_token_squared": 0.0000005,
    "idle_w": 0,
    "fixed_j": 1,
    "coefficient_basis": "above_idle",
    "source": "synthetic example, not calibrated"
  }
}
```

Save this as `model.json`, then run from the repository root:

```sh
python3.13 -B scripts/interp_energy/behaviour_energy.py scenario model.json \
  --prefill-tokens 256 --noncap-tokens 3000 5000 8000
```

Scenario defaults reproduce the study's public-rate arithmetic: cap 32,768,
base/edit cap-hit fractions .930/.331, accuracy .079/.481. These are changeable
CLI parameters. Noncap lengths are assumptions. At lengths 3k/5k/8k, decode
tokens per correct fall by about 14.5/13.2/11.7 times. These ratios describe
that cap and configuration, not the best base-model setting. Include base
thinking-off and budget-cap comparators in a later experiment. Scenario outputs
have no CIs because the percentages do not identify a sampling distribution.
Context exposure is averaged across the capped/uncapped mixture; plugging the
mean length into a quadratic would underestimate it. All noncap answers are
assumed to have the supplied length; their real length variance would add
context exposure. Nonzero idle power needs
`--base-duration-s` and `--edited-duration-s` (expected full-window durations).

For observed counts, add `base` and `edited` arrays to that JSON. An optional
`edited_model` object allows different costs; otherwise the base model is
shared. Each answer has this shape:

```json
{"problem_id": "synthetic-1", "prefill_tokens": 256,
 "decode_tokens": 100, "correct": true, "duration_s": 2.5}
```

Provide at least two answers per arm, then:

```sh
python3.13 -B scripts/interp_energy/behaviour_energy.py compare answers.json \
  --bootstrap-samples 2000 --confidence .95 --seed 0
```

Both commands write JSON to stdout; redirect to a new file if desired. Inputs
are never modified. Unknown fields, duplicate keys, nonfinite values, nonboolean
correctness, fractional/negative token counts, and mismatched pair rosters fail
with a CLI usage error. `source` and `coefficient_basis` are required explicitly
by the CLI. The tool reads only the named JSON, with no nested path resolution.

## Public, unblinded parameter leads

Read these tracked documents as text; do not follow their external data/archive
paths. The tool does not read any of them automatically.

- [Study §1.2](../../docs/research-audits/2026-11-07/interp-weight-edit-energy.md#12-how-big-is-the-behaviour-term-for-astra)
  gives the published cap/accuracy arithmetic and labels 0.05–0.15 J/token for
  the 0.8B model as a planning estimate, requiring fresh calibration. The ALIGN
  30B MoE rates do not transfer to the small hybrid model.
- [Research question bank](../../docs/research_question_bank.md), PC-4/PC-5/PC-6,
  discusses decode throughput, KV growth and small-model planning anchors.
- [Known-bytes slot](../../docs/process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md)
  publishes GPU rail 0.0087901, rails 0.0092431 and DC 0.0388927 J/GB of the
  rotate-minus-repeat logical-byte contrast. These are boundary-specific
  **J/GB, not J/token** and are latency-bound microbenchmark contrasts. Using
  them requires an independently justified bytes/token mapping and regime
  transfer; multiplying by model bytes alone is not a calibration.
- [Known-bytes reading rule](../../docs/registrations/bytes_known_bytes_reading_rule_DRAFT.md)
  documents idle subtraction and worst-case bounds; its half-widths are not
  standard errors and must not be treated as bootstrap input noise.

No sealed Block 5 measurements are needed. A lead must later supply matched,
unblinded calibration and measurement evidence before making energy claims.
There are no MLX/native tests for this pure arithmetic component.
