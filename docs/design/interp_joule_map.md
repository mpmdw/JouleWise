# JOULE-MAP: in-situ marginal decode energy on unified memory

2026-11-07 — **BANKED / PROVISIONAL, desk design and synthetic tooling only.**
This is ranked idea 9 of the [design study](../research-audits/2026-11-07/interp-weight-edit-energy.md#3-ranked-idea-table),
with both attacks in [checks §4](../research-audits/2026-11-07/interp-weight-edit-energy-checks.md#4-joule-map-per-component-energy-attribution-of-a-transformer-on-apple-gpu-seat-1-fable).
It grants no Mac window. Measurement experiments 1/2, BYTES, ALIGN and the paper
freeze retain their priority. No Block 5 outcome, capture, or pipeline is needed.

## Question, prior art and scope

At batch one and specified context, how many joules per forced decode token
does retaining a particular component cost, conditional on a fixed downstream
trajectory? Report attention and MLP by layer, embedding lookup and LM head,
plus group removals to test additivity. These are **marginal savings**, not
intrinsic component energy or necessarily additive shares. Negative estimates
and intervals crossing zero must remain visible.

The source study/checks describe [CLEAR, *Dissecting Transformers: A 'CLEAR'
Perspective towards Green AI*, arXiv 2510.02810](https://arxiv.org/abs/2510.02810)
as cached-input, isolated component repetitions on NVIDIA GPUs, including
attention/MLP/norms/embedding/head. They describe [HYMELL, Shokoufa et al.,
*Multi-Level Modeling of LLM Inference Latency and Energy via Hybrid
Analytical-ML Predictors*, arXiv 2608.06723](https://arxiv.org/abs/2608.06723)
as isolated operator/block energy and latency modeling on NVIDIA. These citations
and descriptions come from the supplied local audit; this desk run made **no
network requests and did not independently reopen either paper**. The checks'
unverified Apple NPU and layer-pruning literature gaps remain open before registration.

The proposed contribution is a **test**, not a first-ever claim: in-situ removal
inside an Apple-GPU decode, retaining original weights in unified memory;
per-layer conditional marginals, long-context strata, an explicit downstream
control and additivity budget, with separately labeled GPU/rails/DC/residual
boundaries. Isolated replay does not preserve this scheduling/residency context.
Unified memory couples CPU, GPU, cache and DRAM work on a shared fabric; removal
can change bandwidth competition, dispatch, cache behavior, DVFS and duration.
The experiment measures those effects jointly on each boundary. **GPU rail is
not pure compute; DC minus rails is not a DRAM meter.** The latter also contains
CPU/unreported circuitry, conversion losses and mismatch uncertainty.

## Three-arm correction at fixed tokens

Use the existing [forced replay](../../joulewise/interp_energy/forced_decode.py),
fresh model-default caches, batch one, identical prompt, complete forced token
sequence, prefill chunking and diagnostic policy in every arm. Do not truncate
at EOS. Each target has three arms:

| Arm | Target execution | Output delivered downstream |
|---|---|---|
| F (`full`) | Original computation | Its actual output |
| C (`clamped`) | Original computation, **evaluated even if discarded** | Resident replacement tape |
| S (`removed`) | No target call, original weights still resident | The identical replacement tape |

For a residual attention or MLP branch, a zero tape makes the containing
residual block an identity at that branch. Do not return the input as the branch
output: the existing residual add would then double it. An embedding or LM-head
tape instead replaces that module's array output; an embedding lookup streams
one row, not the whole embedding matrix. Tied embedding/head weights remain
resident, and their calls are separate targets, never counted as two resident
weight sets. A whole-layer removal needs an explicit residual-block adapter;
joint attention/MLP branch removal retains norms and is not a whole-layer skip.

Two tape policies should be prepared **before** measured work:

1. **Primary: reference-output tape.** Capture outputs for every target call,
   including every prefill chunk, on an unedited fixed-token replay. Materialize
   and retain device arrays. C and S deliver the reference trajectory; validate
   logits against F before using a run. For a joint target, capture all its seams
   on the same reference replay. This controls downstream activation values
   without doing a CPU activation copy per token.
2. **Sensitivity: zero or a separately prepared mean/resample tape.** C and S
   share a perturbed trajectory. Their difference is a conditional marginal
   under that trajectory. Compare it to the reference-tape result. The original
   target's input/operands may change, so this cannot identify a universal cost.

For either gross or above-idle episode energy, divided by the same decode count N:

```text
raw saving       = (E_F - E_S) / N
control shift    = (E_F - E_C) / N
corrected saving = raw saving - control shift = (E_C - E_S) / N
E_above_idle     = E_gross - P_idle * measured_duration
```

Fixed tokens remove output-length/context differences, **not** downstream
activation changes. C versus S holds the latter fixed, which is why a simple
F-versus-skip experiment is insufficient. F minus C is a diagnostic control
shift: with zero replacement it includes downstream data dependence; even with
reference replacement it includes clamp/instrumentation costs. It is not a
pure causal estimate of semantic behavior. No regression on KL alone can
subtract an unknown switching effect.

The [array seam](../../joulewise/interp_energy/component_intervention.py) is
explicit, serial and uncompiled. `ComponentGate.episode()` resets and checks its
tape cursor; `invoke()` evaluates C's discarded result to prevent MLX dead-code
elimination. `wrap_mlx_component()` imports MLX lazily and retains the original
module as `inner`. Install wrappers once in all arms before hashing and warmup.
Barrier/evaluation and tape-access costs change the schedule. C minus S includes
the cost of materializing the target; it is an **instrumented marginal**, not a
claim about an uninstrumented fused pipeline. Bound that difference with nulls.

Existing [weight edits](../../joulewise/interp_energy/weight_edits.py) provide
value-only zero/scale/sign/projection controls and identities. Dense zero weights
retain shape, bytes and kernels; they do **not** implement removal. The synthetic
integration test applies/reverts `Scale` and proves the call count is retained.
Use `WeightSwap`/binding for real model leaves; do not write another edit engine.

## Architecture validity gates

- This implementation is a single-array seam, with no model discovery or
  automatic monkey patching of arbitrary architectures. It does not support
  compiled graphs, tuple-returning modules, MoE routing or shared hybrid state.
  Explicit adapters and parity tests precede any extension.
- Every target owns its cache. C updates the target's cache; S omits it. That
  omitted K/V work is part of the attention marginal. Other layers' cache/mask
  offsets must remain correct. **Llama uses cache[0] for a shared mask offset**:
  skipping the first attention cache's update is invalid without an independent
  context-position adapter. The new native attention test deliberately removes
  the last layer's attention. Per-layer production support, especially layer 0,
  remains an open adapter gate; synthetic tests are not proof of it.
- For MoE, fixed tokens do not fix expert selection. Replay recorded indices
  (and define whether mixing weights are also clamped) throughout both arms,
  verify active experts/bytes, and retain a routing-null. Until that exists,
  restrict this tool to dense models. Dropping a router without a replay policy
  is undefined, not an energy measurement of the router.
- Validate shapes/dtypes, finiteness (including replacement arrays), cache
  advancement, full logits, target call counts and unchanged parameter hashes
  before telemetry. Tapes must be immutable while in use. A short or unused
  tape fails; equal shapes alone cannot prove semantic/call-order parity.
- Keep resident tapes and weights in all arms, record their footprint and
  swapping/pressure observations. Full reference-output tapes can be large:
  at width 4096, bf16, 4096 calls, one seam is about 32 MiB, while a 128k-wide
  head tape is about 1 GiB. Never spill a tape into SSD paging to fit a grid.
  Blocking/shorter replays change the estimand and need fresh sizing.

## Interleaving, reduction and uncertainty

`interleaved_plan(targets, n_units, seed=...)` randomizes target order per unit,
and permutes the first three arms independently for each target, then reverses
them: e.g. F,C,S,S,C,F or S,F,C,C,F,S. Six members form a contrast unit. Retain
randomization and actual times; no post-outcome member deletion or n expansion.
The analysis does not require equal duration or an idealized slot clock.

For each six-member target unit, interpolate each arm's two J/token observations
to the mean of the two central member midpoints. Thus all three arms evaluate
at the same time, canceling an **affine drift in J/token** with unequal episode
durations. It does not promise cancellation of nonlinear thermal response,
power drift times arm-dependent duration, schedule-correlated noise, or changing
DVFS. Freeze curvature/clock/baseline allowances before confirmatory analysis.

The [reducer](../../joulewise/interp_energy/joule_map.py) accepts `Episode`
records of already integrated decode energies; it never follows a source path.
It refuses incomplete/duplicate/non-palindromic units, overlaps, mixed token,
prompt, policy, weight or source identities, changing target tapes, and unmatched
cross-target unit rosters. It keeps context and boundary strata separate.
`source_kind` is `synthetic` or `unvalidated-native`; neither label authenticates
a source. The output always says `PROVISIONAL_DESK_ANALYSIS`.

Circular moving-block percentile bootstrap resamples **whole matched units**,
using the same draws for all targets and additivity contrasts in a stratum.
Block length one assumes independent units. Select longer block length from a
noise/autocorrelation pilot; at least four blocks are required mechanically,
but four alone does not establish adequate coverage. Seed, confidence, number
of draws, block length and unit order are retained. Intervals are approximate
and pointwise; a confirmatory map needs a prospective multiplicity policy.
No automatic stopping, native result issuance, TOST or detection claim exists.

Per-member `energy_bound_j` plus `idle_bound_w * duration_s` (above-idle only)
propagate with absolute interpolation/contrast weights. A mean worst-case bound
widens each bootstrap CI into a separate `sensitivity_interval`. It does not
shrink as independent noise. These are **caller-supplied** allowances, including
time anchoring, calibration and clamp overhead as appropriate; zero values are
not evidence of zero instrument error. Existing D-078 claim-side/floor doctrine
and authentic bundle reduction remain required for future claims.

An additivity specification names disjoint `parts`, their `joint` removal and
a prospective `budget_j_per_token`. The audit bootstraps sum(part C−S) minus
joint C−S with covariance preserved. It calls `within_budget` only when the
whole sensitivity interval lies inside ±budget. The caller owns whether the
named parts truly partition the joint. Do not normalize marginals to 100%.
Also compare the partition to full-minus-all-removed, retaining the measured
all-removed residual (norms, dispatch, diagnostics, etc.). That extra check must
use the same instrumented policy and a declared reference-output tape; full
energy need not equal any sum of component costs.

Collect GPU rail, canonical rails, DC and a carefully aligned DC−rails residual
as separate reductions with separate baseline/error terms. Construct a residual
from synchronized native observations; conservatively combine its bounds.
The current map reports separate per-boundary CIs; it does not compute
cross-boundary covariance or purport to be an authenticated run-bundle reducer.
Record clocks, thermal state, active GPU frequency, tokens/s and contention.
Frequency or kernel-mix shifts are mechanisms/validity issues, never covariates
to regress away silently.

At batch one, FLOPs and streamed weight bytes are collinear for dense modules;
attention FLOPs and KV bytes also scale together with context. Report J/token,
and optionally descriptive J/estimated removed GB with a byte-model caveat.
Do not fit separately identified J/FLOP and J/GB without an arithmetic-intensity
axis such as batch sizes 1/4/16 or a separately designed prefill contrast.
No hardware traffic counters or KB coefficient transfer are assumed.

## Behavior accounting beyond fixed tokens

The map prices work; it does not judge capability. For a free-running edited
model, record length, context exposure, correctness and (if relevant) expert
counts, and use the existing [behavior channel](../../joulewise/interp_energy/behaviour_channel.py)
with explicitly sourced, architecture/context-specific coefficients. Its paired
bootstrap concerns answer units; do not substitute token rows for answers.
Only use above-idle map coefficients with above-idle predictions, adding the
measured duration/idle term explicitly when predicting gross energy.

If a later experiment needs measured total free-run savings, replay both the
base-produced sequence sF and removed-produced sequence sS through both models.
The exact symmetric decomposition of **episode energy** is:

```text
E_F(sF) - E_S(sS)
 = 0.5 * [(E_F(sF)-E_S(sF)) + (E_F(sS)-E_S(sS))]  # fixed-path difference
 + 0.5 * [(E_F(sF)-E_F(sS)) + (E_S(sF)-E_S(sS))]  # path/count difference
```

Those raw fixed-path differences can each receive the three-arm control
diagnostic; do not relabel the corrected conditional marginal as the entire
fixed-path difference. Different sF/sS lengths mean totals must be combined
before dividing, not by averaging per-token rates. This crossover is a later
run design, not implemented collection here. Surgical value edits keep bytes
and dispatches fixed; the map alone cannot infer their switching residual or
quality benefit. Keep the study's null/bound framing.

## Banked run plan and native handoff

1. **Desk acceptance now.** Run the three synthetic/import modules below one
   process at a time, and inspect `--plan-only` and `--demo`. Synthetic truth
   covers two layers, attention/MLP, embedding/head, a control shift, unequal
   durations, drift, idle power and a deliberate non-additive joint target.
2. **Native desk parity later, no model downloads.** On an authorized
   Metal-capable non-measurement Mac, run the new four-test native module below.
   It uses a random two-layer width-16 Llama, not model files. Then finish cache0,
   tuple/hybrid/tied-head adapter gates as needed. Confirm before proposing
   a collector window; importability skips validate no native behavior.
3. **Pilot only after lead allocation, in an agent-free quiet window.** Start
   with one already-approved dense model, one context and two large targets
   (all-MLP/all-attention), plus one A/A sham and retained/reference-clamp null.
   Keep a no-removal wrapper baseline; compare its logits and dispatch behavior
   to the original model outside measured work. Use fresh idle brackets and
   both rails/DC; estimate variability and systematic clamp allowance, not an
   assumed 1/sqrt(time) extrapolation. Abort on invalid caches, nonfinite
   activations, paging, kernel fallback, unmatched frequency or failed nulls.
4. **Size and freeze a sampled grid from that pilot.** Candidate context rungs
   512/4096/16384; large type removals, embedding/head, a few early/middle/late
   layer attention/MLP targets, joint removals and nulls. Small norms/embedding
   may be unresolved; group them or report bounds. Full-attention architectures
   may show growing KV cost; linear-attention/hybrid predictions need separate
   architecture-specific byte models. No head-level map is promised.
5. **Confirmatory window only under existing lead authority.** Fix target
   roster, n, tape policy, block length, budgets, multiplicity and validity rules
   before observing contrasts. Keep raw bundles immutable. Bootstrap intervals
   cannot replace the owning floor/claim-side uncertainty rules.

Illustrative sizing reuses `power.plan_power`: 2000 J / 100 s per member,
10 J effect, 3 J SD **per corrected six-member unit** (assumed, not a transferred
pair SD), 2 J systematic allowance. A two-hour budget fits 12 units for **one
target/context** before overhead. The normal approximation's required count
can be below the reducer's four-block minimum; honor the larger design need.
Eight targets × three contexts × twelve units × six members ×100 s = **48
member-hours**, plus tapes/warmup/idle/cooldowns/nulls. A sampled pilot is the
next step, not a 0.5-night full grid. A ~50 J member cannot be assumed sufficient
for a one-layer contrast; size in joules on the actual boundary.

```sh
python3.13 -B -m unittest tests.interp_energy.test_joule_map -v
python3 -B -m unittest tests.interp_energy.test_component_intervention -v
python3.13 -B -m unittest tests.interp_energy.test_integration -v
python3.13 -B scripts/interp_energy/joule_map.py --plan-only
python3.13 -B scripts/interp_energy/joule_map.py --demo --seed 0

# LEAD ONLY, outside the sandbox on an authorized native desk Mac:
python3.13 -B -m unittest tests.interp_energy.test_joule_map_mlx -v
```

For a named synthetic episode file, serialize `dataclasses.asdict(Episode(...))`
into `{"episodes": [...], "additivity": [...]}` (empty additivity is allowed),
then use `--input file.json`. No other fields, nested locators or automatic
directory discovery are consumed. All digests and source labels are supplied
identity assertions; upstream evidence must establish their truth. The CLI
has no execute/capture path, accesses only that explicitly named file, and
prints JSON. Do not point it at sealed study data.
