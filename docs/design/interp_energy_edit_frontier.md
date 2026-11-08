# Energy/capability frontiers for compute-allocation edits

**2026-11-07 — DESK tooling and experiment proposal, NOT REGISTERED.**
This implements arithmetic for ranked ideas 2–3 of the
[study](../research-audits/2026-11-07/interp-weight-edit-energy.md#3-ranked-idea-table)
and addresses [checks §13](../research-audits/2026-11-07/interp-weight-edit-energy-checks.md).
All examples and tests are synthetic. No measurement, model download, window
reservation, or Block 5 access is authorized by this document. The existing
[ASTRA registration draft](../registrations/astra_2ch_v0_draft.md) and
[analysis draft](../analysis/astra_2ch/ANALYSIS-PLAN-v0-draft.md) retain their
open slots and own the proposed Stage 1 gates. Nothing here closes them.

## Estimands and energy law

For each variant a, with the same n independent problems:

```text
accuracy_a = sum_i correct_ia / n
J/answer_a = sum_i E_ia / n
J/correct_a = sum_i E_ia / sum_i correct_ia
K_ia = p_ia*d_ia + d_ia*(d_ia - 1)/2
E_pred_ia = fixed + a*p_ia + b*d_ia + c*K_ia + idle_w*duration_ia
```

The numerator includes wrong and cap-hit attempts. Zero correct is undefined,
printed as null with a reason. Fewer than three correct gets a sparse-count
flag; this is descriptive, not the application of a registered claim guard.
A cap hit is `decode_tokens == cap_tokens`; stopping reasons beyond this
arithmetic are not inferred. Failed technical attempts/missing scores cannot
be represented as completed correct/incorrect rows: resolve them under a
frozen eligibility policy and disclose spent energy and missingness upstream.
Do not silently drop them to make a matched roster.

The implementation calls the existing `behaviour_channel.answer_energy` and
`summarize_answers`; it does not introduce a competing energy formula.
The integrated linear context term is the package's approximation motivated
by Wu, Han, Ruf, Grari, Detyniecki, **“Prefill, Decode, and Context: A Measured
Energy Law for Agentic LLM Serving,” NeurIPS 2026 workshop**
([source cited by the study](https://neurips.cc/virtual/2026/170701)).
The study/checks report a three-term prefill/decode/KV-context law preferred
over token-only baselines. This session did not fetch that source; this tool
does not claim to reproduce its exact fitted model or transfer its coefficients.

Coefficients must be separately calibrated for the architecture, dtype,
device, runtime, batch size, timing/counting convention and boundary. They
are inputs, with required provenance. Fit on disjoint calibration prompts;
freeze before evaluating edited variants. A shared law tests work sufficiency;
variant-specific laws must be declared in advance and calibrated separately,
or residuals can be fitted away. The hybrid Astra model and a full-attention
model require different coefficients. ALIGN's 30B coefficients do not transfer.

Gross energy is primary (D-067). An `above_idle` model restores
`idle_w*duration`; nonzero idle requires every duration. A `gross` model must
have zero `idle_w` because idle is already included. The behaviour API charges
**d** decode tokens at contexts `p,...,p+d-1`. The ASTRA draft instead counts
**D−1** decode calls after full prompt prefill. Neither that draft nor the
forced-decode timing boundary is changed here. Align counts and calibration
before joining data; otherwise a residual is a counting mismatch.

## Pareto coordinates and uncertainty

The primary frontier minimizes **gross J/answer** and maximizes accuracy.
A second view minimizes **gross J/correct** at each accuracy; its denominator
shares the correctness data, so it is not an independent capability axis.
The tool reports both and labels the costs. Raw `prefill + decode` tokens
provide a diagnostic frontier, with no joule conversion. A point dominates
another only if it is no worse on both axes and strictly better on one.
Exact ties both survive. There is no numerical dominance tolerance.

The bootstrap samples n whole problem IDs with replacement. Every draw uses
the **same IDs across every variant and observation/prediction**, retaining
energy/correctness, between-arm and residual covariance. Names and IDs sort
canonically, so permuting input arrays does not change a seeded report.
All ratios and frontiers are recomputed on each draw. Coordinate and paired
contrast CIs are marginal percentile intervals at the requested confidence.

Frontier membership frequency is a resampling stability diagnostic, not a
posterior probability of optimality, superiority test, or simultaneous
confidence set. Coordinate rectangles do not form a simultaneous frontier
band. An undefined J/correct draw withholds its coordinate/contrast CI. If
any arm has an undefined ratio on any draw, **all inclusion frequencies for
that ratio frontier are withheld**: excluding that arm would artificially
promote competitors. Undefined point costs are listed explicitly. Do not
search seeds or reduce bootstrap draws to obtain an available interval.

These sampling CIs condition on the supplied coefficients and exclude meter,
battery, baseline, timing, calibration, and other systematic uncertainties.
Boundary accuracies cannot recover unobserved successes/failures. Sparse
correctness can dominate uncertainty even when energy is precise. No formal
power, equivalence, claim-floor, or binomial coverage guarantee is implemented.
The existing ASTRA draft's metrological/ratio methods remain separate work.

## Comparing observations with the behaviour prediction

All variants may optionally supply `observed_gross_j`, one full-window gross
value per item at the declared boundary, plus opaque provenance. Predicted
and supplied-observation frontiers stay separate. For each nonbaseline arm:

```text
delta_pred = predicted_variant - predicted_baseline
delta_obs  = observed_variant  - observed_baseline
residual   = delta_obs - delta_pred
```

Each quantity has paired CIs, per answer and per correct, using the same draw.
This comparison asks what the prefill/decode/context prediction misses.
A raw-token frontier alone is insufficient. A positive residual is excess
energy relative to the frozen behaviour law, not evidence for weight
switching: calibration error, runtime hooks, routing, counting, battery and
clock differences are alternatives. Switching needs the separate forced-token
T experiment and its independent meter/floor evidence.

`boundary="dc"` means the caller's accepted whole-machine DC definition;
for ASTRA that includes signed battery assist. Cable-only data must not be
passed as that quantity. `rails` and `gpu_rail` are separate reports with
their own coefficients; they do not independently validate whole-machine
physics. The tool validates numbers and identities, not acquisition evidence.

## Offline API and JSON

Public API: `joulewise.interp_energy.edit_frontier.Variant`,
`analyze_variants`, `pareto_frontier`. Imports require only stdlib. The CLI
reads exactly one named JSON and prints strict JSON to stdout. It never
discovers runs, opens provenance strings, loads a model or starts telemetry.

```json
{
  "model_id": "synthetic model; dtype/runtime pinned by caller",
  "evaluation_id": "synthetic fixture; one seed per item",
  "boundary": "dc",
  "baseline": "base",
  "variants": [
    {
      "name": "base", "cap_tokens": 100,
      "model": {
        "prefill_j_per_token": 0.02, "decode_j_per_token": 0.1,
        "context_j_per_token_squared": 0.0005,
        "coefficient_basis": "gross", "source": "synthetic, not calibrated"
      },
      "answers": [
        {"problem_id": "p1", "prefill_tokens": 10, "decode_tokens": 90, "correct": true},
        {"problem_id": "p2", "prefill_tokens": 20, "decode_tokens": 100, "correct": false}
      ]
    },
    {
      "name": "edited", "cap_tokens": 100,
      "model": {
        "prefill_j_per_token": 0.02, "decode_j_per_token": 0.1,
        "context_j_per_token_squared": 0.0005,
        "coefficient_basis": "gross", "source": "same synthetic law"
      },
      "answers": [
        {"problem_id": "p1", "prefill_tokens": 10, "decode_tokens": 30, "correct": true},
        {"problem_id": "p2", "prefill_tokens": 20, "decode_tokens": 50, "correct": true}
      ]
    }
  ]
}
```

This deliberately tiny example has sparse correctness and withheld ratio CIs.
For an optional observation, add, for example,
`"observed_gross_j": {"p1": 12.0, "p2": 18.0}` and
`"observation_source": "synthetic observations"` **to each variant**, with its
own values. Unknown fields, duplicate JSON keys, nonfinite energies, missing
provenance, partial observations, duplicate IDs, roster mismatches and outputs
above the stated cap fail. A budget arm may have a smaller cap; this is a
treatment, retained in the report. It does not license extrapolation across
unrun cap settings. Model/runtime/dtype and evaluation IDs are caller-defined
provenance, not file locations. One report is one cohort and one boundary.

```sh
python3.13 -B scripts/interp_energy/edit_frontier.py --demo --seed 0
python3.13 -B scripts/interp_energy/edit_frontier.py synthetic-frontier.json --bootstrap-samples 2000 --seed 0
```

## Proposed experiment: variants, items and window cost

This is a proposal for later clean, lead-controlled Mac windows after the
study's existing priorities. An active agent session cannot collect data.
No production model or weights are accessed for this desk task.

Reuse Stage 1's four arms and item-level F export after authorized release:
Qwen3.5-0.8B **bf16** base/thinking-on, Astra released edit/thinking-on,
base/thinking-off, and base/thinking-on/8k. Do not regenerate existing F items
merely for this report. Wave-1 `SparseDelta`, resident `WeightSwap`, forced
decode, operand ladder, capture hooks and ASTRA P/T design are the existing
building blocks. There is no new generation runner or direction extractor.
Released-diff import/hash validation remains a lead-owned readiness gap.

Proposed Stage 2 core, **100 independent items, one paired seed per item per
arm**, with order randomized within item blocks, batch/concurrency one:

| Cohort | Core variants | Items and cap |
|---|---|---|
| Hybrid Qwen3.5-0.8B bf16 | base/on; Astra alpha=1/on; base/off; base/on/8k budget | Same fixed 100 MATH-500 items; 32,768 maximum, 8,192 for budget arm |
| Full-attention R1-Distill-Qwen-1.5B, dtype fixed before calibration | base; re-derived ThinkEdit length-raising edit; ASC-style concise runtime vector; 4k budget control | Same frozen 100 items within this cohort; 16,384 maximum, 4,096 for budget arm |

The dense model is a candidate architecture, not a claim of native support.
ThinkEdit requires a separate disjoint direction-discovery set and held-out
evaluation; it raises overly short reasoning and may leave average length
nearly unchanged. The concise arm is explicitly a **runtime hook**. Folding
an additive vector into a bias-free projection needs a bias and separate
runtime validation; do not call it an ordinary projection edit. The budget
controls isolate what surgery buys beyond a simple stopping rule. An optional
presence-penalty control is added only before freezing the roster/arm plan.

Proposed strength extension: hybrid alpha={0.25,0.5,0.75} on the same items
(alpha=0/base already exists), plus one intermediate concise strength on the
dense cohort. Apply scaled deltas using the existing edit primitives; verify
identities, bf16 rounding and software behaviour before any energy window.
No new direction is claimed to reproduce the released Astra discovery.
Additional 8k/16k/32k panels must be independently planned and reported per
cap; never infer their accuracy by truncating a completed 32k answer.

**Cost arithmetic, all assumptions, not measured throughput or lengths:**

| Component | Assumed mean decode lengths per arm | Decode tokens | Throughput assumption | Decode hours |
|---|---|---:|---:|---:|
| Hybrid core, 100 items × 4 arms | 30.8k, 14.2k, 14k, 8k | 6.70M | 150–250 tok/s | 7.4–12.4 |
| Dense core, 100 × 4 | 8k, 10k, 4k, 4k | 2.60M | 60–120 tok/s | 6.0–12.0 |
| Hybrid intermediate strengths, 100 × 3 | 28k, 22k, 18k | 6.80M | 150–250 tok/s | 7.6–12.6 |
| Dense intermediate concise strength, 100 × 1 | 6k | 0.60M | 60–120 tok/s | 1.4–2.8 |

Core decode is 13.5–24.5 h. Add a **25% planning allowance** for prompt
prefill, sampling overhead, cooldown, warmup and swaps, **2 h** disjoint
calibration, and **4.5 h** P/T/AA planning allowance: **23.4–37.1 h**, about
**3–5 eight-hour windows**. Core plus strengths is approximately **34.5–56.3 h**,
about **5–8 windows** under those assumptions. This makes the study's 4–7-night
headline conditional on measured speed and the chosen panel. T units must
be sized in joules from a local A/A′ pilot; the 4.5 h allowance is not a
validated residual bound. Unexpected long paths can consume every cap.

The all-cap core ceiling is 15.97M decode tokens: hybrid 10.65M, dense 5.32M.
At the slower assumed speeds that is 44.4 h of decode alone; with the same
allowances, about 62.0 h. Strength extensions and extra caps add cost. Bench
speed and pilot path distributions on already-authorized models, then freeze
sample size, strengths and nights prospectively. Do not stop on a favorable
frontier or add items until a preferred arm wins. Four sampled seeds per
problem would multiply decode by four and require **cluster bootstrap**, which
this version rejects; neither seeds nor tokens are independent new problems.

Even 100 items yields only about eight baseline correct if the study's
7.9% rate transfers. That is a precision concern, not a reason to borrow a
hardware floor or overstate a J/correct ratio. The 40-item Stage 1 pilot is
descriptive. Population accuracy and between-session variation require a
separate sample-size and statistical plan before confirmatory use.

## Readiness and handoff

Before any collection: resolve ASTRA open slots, authorize local model/diff
availability, verify tiny native tests, verify target-model loading/cache
reset and released-diff identities, reproduce behaviour in a software-only
smoke, measure throughput, freeze calibration/counting/checker/rosters/seeds
and blind codes, and establish accepted boundary/systematic evidence. These
are proposed live readiness steps, not completed checks or new kernel tasks.

No new MLX code is needed for this arithmetic module. The existing native
tests remain unrun here; the lead should run each separately on an authorized
Metal-capable non-measurement machine, using only the tiny synthetic models:

```sh
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_forced_decode_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_mlx_native -v
```

MLX importability gates are preserved. A skip is not Metal validation. Do not
run these native modules in this sandbox. This module's own synthetic unittest
commands and results are in the dated run report. The exact next desk step is
lead review of the input/estimand/counting contract; subsequent calibration and
measurement require their own authorized, unblinded inputs and quiet session.
