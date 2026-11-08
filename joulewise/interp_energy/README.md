# Interpretability and energy desk tools

This package joins the six wave-1 components of the
[design study](../../docs/research-audits/2026-11-07/interp-weight-edit-energy.md).
It provides synthetic software checks and exploratory arithmetic. Native MLX,
model-specific behaviour, and measurement validity remain **PROVISIONAL**.
The [ASTRA draft](../../docs/registrations/astra_2ch_v0_draft.md) and
[analysis draft](../../docs/analysis/astra_2ch/ANALYSIS-PLAN-v0-draft.md) are
**NOT REGISTERED**. The package is not an implementation of that full plan.
The [integration report](../../docs/run_reports/interp-energy-desk/INTEGRATION.md)
records review findings, draft incompatibilities, tests and open decisions.

## Modules and experiments

| Module / document | Study experiment | Public entry points and limits |
|---|---|---|
| `weight_edits` | Stage 0 edit kit; T fixed-token edits; later H1/H2 strength/bound studies | `SparseDelta`, `RankOneUpdate`, `AblationMask`, `MagnitudePruning`, `Scale`, `SignFlip`, `WeightSwap`, `parameter_hashes`, `weights_sha256`. Dense floating-point primitives; no verified Astra diff loader or direction-fitting algorithm. |
| `ablation_artifact` / `weight_edits.AblationReplacement` | Idea 12, ABLATION-ARTIFACT | Zero/mean/resample/constant replacements of explicit matrix selections; sham control; common activation `where`, traversal statistics, desk grid planner and synthetic demo. [Design and materiality rule](../../docs/registrations/ablation_artifact_v0_draft.md). No native grid runner or acquisition. |
| `forced_decode` | Stage 0 teacher forcing; Stage 1 T physics channel | `replay`, `MLXBackend`, `NumpyBackend`, `ReplayResult`, `token_sequence_sha256`, `weight_file_identity`. Fixed IDs, fresh model-specific caches, synchronous forwards and diagnostics. |
| `reference` | Synthetic validation of T | `NumpyReferenceModel`: tiny causal-attention model with real growing K/V arrays; no model files. |
| `behaviour_channel` | Stage 1 F behaviour channel; later H1 frontier arithmetic | `Answer`, `EnergyModel`, `CapScenario`, `answer_energy`, `summarize_answers`, `compare_answers`, `compare_scenarios`. Count-based predictions only; no free-generation runner, scorer, calibration fitting or measured-energy reducer. |
| `lockin` | LOCKIN-SWAP / PRBS instrument proposal | `Schedule`, `NoiseModel`, `make_schedule`, `simulate_trace`, `demodulate`, `abba_differences`, `estimate_abba`. Synthetic traces, exploratory block inference; no hardware acquisition or promised lock-in gain. |
| `power` | Study §2.2 sizing / PSD-gated lock-in feasibility | `plan_power`, `study_reference`. Independent-unit normal planning; no TOST or registered claim decision. |
| `rail_data_dependence` | S1 Apple-GPU data dependence; Stage 1 P instrument ladder | `Settings`, `make_plan`, `synthetic_weight`, `abba_schedule`, `execute_plan`, `MLXBackend`, `NumpyDryBackend`. Fixed dispatch counts within a geometry/dtype; dry mode is a tiny float32 CPU surrogate. |
| `operand_stats` | P fill descriptors; possible later H4 toggle work | `hamming_weight`, `zero_fraction`, `bit_toggle_rate`, `operand_statistics`, `combine_statistics`, bf16 encoding helpers. Host storage descriptors, not observed hardware bus activity. |
| `capture_hooks` | Future authorized P capture | `existing_capture`: lifecycle wrapper around existing powermetrics and KM003C collectors. External native use only; tests mock both collectors. |
| ASTRA registration / analysis drafts | Proposed Stage 1 P/F/T pilot | Design and proposed estimators only, with seven open slots. They authorize no collection or downloads. |

## API and optional dependencies

Use module-qualified names so the replay and operand-ladder backends cannot be
confused:

```python
from joulewise import interp_energy as ie

model = ie.reference.NumpyReferenceModel(seed=17)
backend = ie.forced_decode.NumpyBackend()
# Native counterparts: ie.forced_decode.MLXBackend() for model replay;
# ie.rail_data_dependence.MLXBackend() for the synthetic GPU ladder.
```

All public module namespaces load lazily. Importing them needs only the standard
library and starts no runtime, collector or network operation. Numerical desk
operations use the optional `interp-energy` NumPy extra. Model replay needs MLX
and mlx-lm for native execution; the native operand ladder needs MLX and NumPy.
Dependencies must already be installed for offline work. `rail_data_dependence.MlxBackend`
is a compatibility alias for the consistent `MLXBackend` spelling.

The shared `_common.py` owns lazy NumPy loading and canonical JSON hashing.
Validation specific to an edit, token stream, or statistical model stays in its
own module. JSON schemas remain component-specific; their field names, units
and statuses are not interchangeable.

## Weight edits, identities and replay

Edits act on a flat mutable mapping of dense NumPy/MLX arrays. Layout and dtype
stay fixed. Reversion restores saved bytes and checks hashes, including signed
zero and NaN payloads. A mask's `True` entries are zeroed; head selections require
an explicit axis and contiguous head size. Dense pruning leaves dense storage.
A rank-one update applies an already supplied direction; it does not fit ROME.

`AblationReplacement` shares the mask/axis selection and saved-byte restoration
of `AblationMask`. Mean uses explicit calibration rows' per-feature mean;
resample takes frozen donor-row indices; constant takes a scalar. All use
nonempty `[rows, features]` matrices. Weight and activation replacements are
distinct interventions. `replacement_for(template)` prepares a full runtime
operand outside timing; `ablation_artifact.replace_activation` uses the same
shape/dtype-matched `where` for each style and for the clean-residual patch.
Repeated means tie zero on row-transition statistics, while reduction-axis
statistics can differ; the proposed energy ordering needs native measurement.
Run the desk proposal with
`python3.13 -B -m joulewise.interp_energy.ablation_artifact --plan-only`, or the tiny NumPy demo
with `python3 -B -m joulewise.interp_energy.ablation_artifact --synthetic`.

```python
base_digest = ie.weight_edits.weights_sha256(model.weights)
edit = ie.weight_edits.SignFlip("output").apply(model.weights)
try:
    result = ie.forced_decode.replay(
        model, [1, 2, 3], [5, 4, 0, 8], backend=backend,
        vocab_size=model.vocab_size,
        model_weights_sha256=ie.weight_edits.weights_sha256(model.weights),
    )
finally:
    edit.revert()
assert ie.weight_edits.weights_sha256(model.weights) == base_digest
```

`weights_sha256` hashes a sorted manifest of parameter names, shapes, dtype
strings and raw-byte SHA-256 digests. `parameter_sha256` hashes one array's raw
bytes; `parameter_hashes` returns those hashes by name. Use the aggregate for
`replay` after **every** edit/swap. Hashing scans full parameters and belongs
outside timed work. `NumpyReferenceModel.weights_sha256()` uses the same helper.
The replay API labels supplied identities `caller-asserted`: it does not prove
that a detached mapping contains the model's current leaves.

`WeightSwap(parameters, edited, bind=...)` prepares both states once and supports
`switch("base")`, `switch("edited")`, `apply`, `revert`, `toggle` and `verify`.
NumPy scatters changed elements into the original arrays. MLX rebinds prepared
resident tensors, with synchronization; this does not promise partial physical
buffer writes. For a real MLX model, bind changed leaves back into it:

```python
# Native example only; run on an authorized non-measurement Metal machine.
# from mlx.utils import tree_unflatten
# bind = lambda changed: model.update(tree_unflatten(list(changed.items())))
```

Exclusive ownership, uncompiled forwards and evaluated/submitted inference
before swapping are required. Cache reset and durable schedule logging belong
to the caller. Every successful switch records monotonic start/completion and
logical changed bytes; full `verify()` scans run outside chips.

Replay prefills `prompt[:-1]` in fixed chunks. Step zero consumes `prompt[-1]`
and scores `forced[0]`; each later step consumes the previous forced token.
There are **D single-token calls** for D forced output tokens; no sampled or
argmax token is fed back, no EOS stops replay, and the final forced token stays
outside the cache. Fresh `mlx_lm.models.cache.make_prompt_cache(model)` objects
preserve model-specific KV/recurrent state implementations. Native hybrid
reset/support still needs verification.

MLX evaluates logits and cache states before completion timestamps. Diagnostic
log-probabilities, argmax and top-k run between forwards and add work. This is an
instrumented synchronous replay, with different overhead from normal asynchronous
generation. It is not yet the draft's logits-discarding T measurement runner:
the draft counts full prompt prefill plus D−1 decode calls. Resolve that timing
boundary and diagnostics policy before registering or calibrating T.

JSONL output has a `replay` header, `token` rows and a `complete` footer; absent
completion means incomplete output. Prompt, continuation and policy hashes must
match across paired arms. Token hashes use compact JSON integer arrays. Each
row includes the current weight digest. Diagnostics use full-vocabulary natural
log-probabilities; top-k tie membership is backend-defined. Use identical
runtime versions and policies across arms. File serialization follows replay.

A synthetic CLI needs no model files:

```sh
python3.13 -B scripts/interp_energy/forced_decode.py --dry-run --output /tmp/synthetic-replay.jsonl
```

The separate native CLI accepts an existing local safetensors directory via
`--model`, exact JSON IDs via `--prompt-tokens` and `--tokens`, and an exclusive
`--output`. `--prompt TEXT` uses raw encoding without added special tokens or a
chat template; saved baseline prompt IDs are preferable for pairs. Offline
flags/local tokenizer loading prohibit hub fallback. Its on-disk weight identity
is a sorted safetensors file manifest, distinct from the in-memory parameter
scheme; neither scheme proves later mutations. Reuse the same scheme across
arms. Never pass study-data paths to this desk tooling.

## Behaviour model and exploratory uncertainty

For prompt p, reported decode count d and full-window duration t:

```text
K = p*d + d*(d-1)/2
E_gross = fixed_j + prefill_j_per_token*p + decode_j_per_token*d
          + context_j_per_token_squared*K + idle_w*t
```

This is a linear context-cost approximation. Supplied coefficients must match
the model, dtype, runtime, physical boundary and counting convention. With
`coefficient_basis="above_idle"`, coefficients exclude idle and `idle_w*t`
restores gross energy. Nonzero idle power requires both arms' durations. With
`coefficient_basis="gross"`, idle is already included, `idle_w` must be zero,
and no above-idle view is inferred. Gross results come first (D-067).

J/correct uses **all attempts' energy / number correct**. Zero correct produces
null with an inference status. `compare_answers` pairs unique independent
problem IDs; repeated seeds of one problem need a separate cluster analysis.
Delta-method CIs retain energy/correctness and paired-arm covariance; bootstrap
resamples whole pairs and recomputes ratios. Any undefined zero-correct draw
withholds that statistic's bootstrap interval instead of dropping the draw.
Small/sparse samples can have poor coverage. Intervals condition on supplied
coefficients and exclude calibration error, systematic bounds and claim gates.

The exact symmetric accounting is, for midpoint coefficients/work:

```text
behaviour = mean(coefficients) dot (work_edit - work_base)
rate      = (coefficients_edit - coefficients_base) dot mean(work)
delta     = behaviour + rate
```

This allocates interaction equally; it does not causally identify switching.
Shared coefficients force the rate term to zero by assumption.
`compare_scenarios` projects a cap/noncap mixture without inventing a CI;
context exposure is averaged over that mixture, not evaluated at mean length.

The CLI reads only the named JSON. Every model requires explicit `source` and
`coefficient_basis`; source strings are opaque and never dereferenced. Example:

```json
{"base_model":{"prefill_j_per_token":0.02,"decode_j_per_token":0.1,
"coefficient_basis":"above_idle","source":"synthetic, not calibrated"}}
```

```sh
python3.13 -B scripts/interp_energy/behaviour_energy.py scenario model.json --prefill-tokens 256 --noncap-tokens 3000 5000 8000
python3.13 -B scripts/interp_energy/behaviour_energy.py compare answers.json --bootstrap-samples 2000 --confidence .95 --seed 0
```

For `compare`, add `base`/`edited` arrays of
`{"problem_id":"synthetic-1","prefill_tokens":256,"decode_tokens":100,"correct":true}`.
Provide at least two units per arm; include `duration_s` for nonzero idle. An
optional `edited_model` allows different costs. Unknown fields, duplicate JSON
keys, nonfinite values and mismatched pair rosters fail.

This model's d/context convention and null-ratio policy differ from the draft's
D−1 decode model and infinite EPC endpoints. It predicts energy from counts;
it does not implement the draft's measured-energy bootstrap, calibration
uncertainty, Clopper–Pearson, t intervals, floors or TOST.

## Lock-in, power planning and operand ladder

`lockin` uses A=−1, B=+1 and reports B−A in W. `make_schedule` supports square,
ABBA, randomized ABBA/BAAB and Manchester bi-phase coding. Manchester here is
not a maximal-length PRBS. Demodulation uses window-averaged signs, an optional
known-phase fundamental and fixed edge guards. HAC/block-bootstrap intervals
use chronological four-chip blocks; they assume dependence decays and cannot
protect against schedule-correlated drift. Simulation noise is uncalibrated;
a PSD/chip-length pilot must justify any native modulation gain.

`power.plan_power` sizes independent pairs/sessions using a known-SD normal
approximation. A pair's duration includes both replays. Systematic bounds never
average down; `detectable` is a planning screen, not a claim or equivalence test.

```sh
python3.13 -B scripts/interp_energy/power_analysis.py --paired-only
python3.13 -B scripts/interp_energy/rail_data_dependence.py --plan-only --out /tmp/synthetic-operand-plan
python3.13 -B scripts/interp_energy/rail_data_dependence.py --dry --out /tmp/synthetic-operand-dry
```

Plan-only uses no optional dependency. Dry runs execute tiny float32 CPU work,
with no collectors, no waits and no native dtype validation. Native workloads
hold shapes, activation inputs and dispatch counts fixed within a geometry/dtype;
4/8-bit arms use affine packed quantization. Host operand statistics describe
logical zeros, stored bits and a C-order tile proxy, not observed GPU toggles.
The default full ladder is broader than the draft P subset. The nominal 81.2
minute plan includes an assumed setup allowance; residency, native setup time,
matching dispatch time/frequency, meter cadence and real window sizing remain
unverified. Collection requires a separate lead-controlled quiet session; an
active agent must never run `--execute` or actual capture hooks.

## Verification and native handoff

Run unittest modules individually, one process at a time. All tests use tiny
synthetic arrays/configs; capture tests mock collectors. The integration module
checks edit/revert identities and logits, scheduled swaps with fixed tokens,
and fresh caches across package components:

```sh
python3.13 -B -m unittest tests.interp_energy.test_integration
```

The integration report lists every non-MLX module and its sandbox result.
Python 3.13 needs an existing NumPy installation for numerical tests; an
optional-dependency skip is not numerical verification. Python 3.11/3.13 CI
compatibility still needs confirmation with NumPy.

The lead must run these **outside this sandbox**, on an authorized Metal-capable
non-measurement machine, one module per process, without downloading weights:

```sh
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_forced_decode_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_mlx_native -v
```

They cover eight edit/swap tests, five replay tests including cross-component
resident swap/replay, and two tiny operand/encoding tests. Importability gates
allow bare installations to skip; a skip does not validate Metal. Hybrid model
support, real collectors, battery/clock alignment, A/A′ floors and the seven
ASTRA open slots remain separate lead-owned gates. No result here is live
hardware evidence or authorization to access sealed Block 5 outcomes.
