# Qwen4 real-weight gold parity harness

This implements GOAL items 5 and 11 as an offline, resumable, one-unit-at-a-time
prefill comparison against **official Transformers 5.22.1**. It does not run the
Block-5 pipeline, read study measurements, convert a whole model, download code,
or use community PR #1788. Decode/cache parity remains GOAL item 2.

Entry point: `scripts/run_qwen4_gold_parity.py`. Frameworks live in separate
processes; the coordinator imports neither Torch nor MLX. Input/trace exchange
uses non-object `.npy` files. Only the explicit adapter module is imported on the
MLX side. No port branch is implicitly selected or copied from another checkout.

## Running

Use the local reference venv to run the coordinator (NumPy and safetensors are
needed). Every child gets two compute threads, offline HF flags, disabled user
site packages, and a repo-local HF cache. No tokenizer or configuration path is
followed to another data root. Supply an explicit local checkpoint directory.

Tiny checkpoint, created by the official model's `save_pretrained`:

```bash
/private/tmp/jwsol/venv-ref/bin/python -B scripts/run_qwen4_gold_parity.py \
  --checkpoint /private/tmp/jwflash-gold-tiny \
  --output /private/tmp/jwflash-gold-selftest \
  --make-tiny
```

Without `--mlx-module`, this uses an intentionally incomplete NumPy **stub**.
Exit 2 and `STUB_NOT_VALIDATED` are expected; this cannot establish MLX parity.
The following independent check validates the streamed reference against a full
tiny HF model. The oracle refuses configs larger than the tiny fixture limits
and checkpoints over 16 MiB; it must never load the real model:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 \
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
/private/tmp/jwsol/venv-ref/bin/python -B -m joulewise.align.qwen4_gold.tiny_oracle \
  --checkpoint /private/tmp/jwflash-gold-tiny \
  --output /private/tmp/jwflash-gold-selftest
```

Laptop, selected real layers (zero-based):

```bash
/private/tmp/jwsol/venv-ref/bin/python -B scripts/run_qwen4_gold_parity.py \
  --checkpoint /private/tmp/jwflash-weights \
  --output /private/tmp/jwflash-gold-real \
  --layers 2,3 --no-endpoints \
  --mlx-module /absolute/local/path/to/port_gold_adapter.py \
  --adapter-dependency /absolute/local/path/to/qwen4_exp.py
```

The default runs fp32 and bf16 on both seeded random and actual reference-chain
inputs. On a partial download, missing layer-0/1 weights block the real chain;
random cases still run. An embedding repeated into streams is **only** layer 0's
real input. The harness never presents it as layer 2's real activation. Omit
`--no-endpoints` to include embeddings, final mixer/norm, and the full vocabulary
head. Missing endpoint tensors produce explicit reference errors.

Full 48-layer MBP run, once all official checkpoint shards and a port adapter are
local (this is agent-compatible correctness work, never a quiet energy capture):

```bash
/private/tmp/jwsol/venv-ref/bin/python -B scripts/run_qwen4_gold_parity.py \
  --checkpoint /absolute/local/path/to/official-bf16 \
  --output /absolute/local/path/to/gold-report \
  --layers all --max-gb 12 \
  --mlx-module /absolute/local/path/to/port_gold_adapter.py \
  --adapter-dependency /absolute/local/path/to/qwen4_exp.py \
  --prompts-json /absolute/local/path/to/fixed-tokenized-prompts.json \
  --resume
```

The default 12 GiB aggregate budget also works on the MBP. A larger explicit
`--max-gb` (up to 110) is available for longer prompts after checking free memory.
Neither the full checkpoint nor the full n-gram table is ever instantiated.
Workers are serial. Interrupt and repeat **the same command** with `--resume`
to continue across sessions. Each completed case and partial per-layer JSON/Markdown are durable immediately; even
an interrupted overall run can resume before a final summary exists.

## Inputs, precision, and coverage

`--prompts-json` is a list of objects, each with a unique safe `name` and a
nonempty `input_ids` list. Include `text`, tokenizer revision, and tokenization
provenance for the final study-independent gold run. Tokenization is done in
advance; this harness never silently fetches a tokenizer. The built-in two
fixtures are fixed numeric token sequences (not claimed to encode particular
English sentences). They include two sequence lengths and a literal token zero.
Each prompt runs separately with no padding; EOS semantics come from config.

Real inputs start with exact checkpoint embedding rows and follow the official
reference layer outputs, independently for fp32 and bf16. MLX receives that
same reference input at every layer, even after a candidate divergence, so
errors cannot cascade into the next layer's input. Each layer also receives
seeded Gaussian inputs. Their RMS is matched to that layer's real input when
available; otherwise the explicit `--random-scale` fallback is 1.0. The seed,
scale, exact input arrays and hashes are retained, with immutable per-case input
snapshots for both workers. Random inputs exercise all
residual streams independently; real layer-0 streams repeat the same embedding.

Both workers cast the same bf16 checkpoint values and float32 exchange inputs to
the requested compute dtype. The reference uses CPU eager attention and the
official PyTorch DeltaNet fallback. No attention/DeltaNet/MoE mathematics is
reimplemented in the harness. Meta construction avoids eager full allocations.
Only the official expert module's matrix storage is replaced by indexed disk
slice proxies; its official `forward` still computes routing and accumulation.

QSA top-k tie order is fixed, not left to torch. The official indexer selects
blocks with `scores.topk(k, dim=0)`; relu makes a block score exactly `0.0`
whenever every indexer head's dot product is `<= 0`, and `torch.topk` leaves
the order of equal values unspecified, so on an exact tie straddling the k-th
score the official selected set is not a function of the inputs. Inside the
indexer's forward only, the reference worker's `topk` returns the stable
(score descending, block ascending) order, one of torch's permitted outputs;
scores are untouched and every other selection is the same set. This is the
canonical port's rule (D0) and its validation reference ("REF"). Reference
metadata records `qsa_topk` call and straddling-tie counts. The MoE router's
top-k is not touched. Found natively: the tiny fp32 random case at layer 3 has
a three-way exact-zero tie for the second block of query 8 (blocks 0, 1, 3);
the canonical rule picks block 0, unpatched torch picked block 1, and the
resulting one-row mask difference propagated into every downstream trace.

The reference observes:

- DeltaNet or QSA attention output; DeltaNet gated norm or Q/K norms; exact QSA
  visibility mask.
- Router logits, normalized top-k weights and chosen experts; complete MoE output
  including the shared expert.
- For both hyper-connections: grouped RMS norm, mixed input, incoming residual,
  injection gates, and the resulting flattened streams.
- PLE output, independently generated n-gram hash ids, gathered embeddings, and
  key/query/convolution norms.
- Embedding output, final hyper-connection mixer norm/output, and full head logits.

The official config's `ple_layer_ids` is **one-based**: `[2]` means decoder index
1. There is no separate final RMSNorm in this reference; it is part of
`hyper_connection_mixer`. QSA for the real checkpoint has budget 2048; the short
built-in prompts do not exercise budget truncation. Tiny config uses budget 4
and longer prompts to exercise selection. Supply longer tokenized prompts to
cover real QSA pruning; that coverage must be stated separately from short-prompt
parity. Batch/padding, decoding, MTP and generation are outside this harness.

## Indexed access and memory

`IndexedCheckpoint` finds text keys through `embed_tokens.weight`, supporting
both `model.language_model.*` (official multimodal checkpoint) and `model.*`
(tiny text checkpoint). An unsharded `model.safetensors` is also supported.
All data access uses `safetensors.safe_open(...).get_slice(...)`, with bounds
on expert/embedding access. It never calls `load_file` for the full checkpoint.
Index shard names must be basenames; shard symlinks and `restricted` paths are
refused. Config absolute paths are inert text.

Expert tensors use a single expert index on axis 0; both official packed and HF
`save_pretrained` unpacked projection layouts are supported. Main embeddings
use only unique requested rows. The head streams 1024 output rows at a time.
The n-gram table uses numeric `shard_N` order and the official `torch.chunk`
partition layout (uniform parts, possibly shorter last part). Only unique rows
needed by the actual hash ids are gathered. Part 0's shape establishes offsets;
unused parts' data are never read. Both adapters must compute their own hash ids
before gathering rows, so hash mistakes cannot be hidden by reference features.

The MLX venv's NumPy has no bf16 dtype. Its loader decodes a safetensors BF16
slice as raw uint16 storage via NumPy's temporary dtype registry, then performs
the exact IEEE bit shift into fp32 before casting in MLX. A targeted test compares
this with Torch's bf16 decoding. No Torch import is needed in the MLX process.

The coordinator reserves its own peak RSS plus 256 MiB of headroom from
`--max-gb`. Each child has a 50 ms self-monitor of peak RSS; the parent also
samples RSS where `ps` is permitted. A breach terminates the worker and cannot
pass. RSS is checked again after completion. Individual decoded slices are capped at
256 MiB fp32, with at most 1024 embedding/head rows per read. The coordinator
also bounds random input allocation before generating it. Live adapters must set MLX's
allocator limit and report a finite nonnegative peak MLX allocation (missing metadata fails); the coordinator conservatively
adds that allocation to RSS when checking the budget. These are sampled guards,
not an OS hard limit: adapters must bound individual allocations and never
materialize a giant table. On this sandbox `ps` is denied, so self-monitoring is
the active guard. The tiny oracle is bounded separately by its config/size caps.

## Adapter contract v1 (both ports)

Pass a local `.py` module to `--mlx-module`. A standalone module may be the port itself or a thin wrapper. Ports with
package-relative imports (such as `mlx_lm.models`) need a standalone wrapper
that imports the port through its normal package context. Hash every separately imported port file with repeatable
`--adapter-dependency` flags; a changed dependency invalidates resume.
The coordinator passes these as `request["adapter_dependencies"]`, a map of
absolute source paths to SHA256 digests, also recorded in `provenance.json`.
The canonical adapter requires `qwen4_exp.py` and `canonical_converter.py`
(or `align_convert_qwen4_exp.py`), verifies their frozen digests, and imports
their source bytes by file location. Its worker metadata records both source
paths/digests and checks the converter's canonical module pin. It never imports
the model from `joulewise.align.models`.

```python
GOLD_ADAPTER_VERSION = 1
GOLD_ADAPTER_KIND = "mlx"  # "stub" always withholds validation

def run_gold(request: dict, checkpoint):
    # Import MLX and the chosen independent port here.
    # Configure allocator limit from request["max_memory_bytes"].
    # Build just request["unit"] with checkpoint.text, load identical weights.
    # Return fully evaluated NumPy arrays and explicit runtime metadata.
    return traces, {
        "device": "metal",
        "mlx_version": "...",
        "peak_mlx_bytes": 0,  # actual mx.get_peak_memory() after evaluation
    }
```

`request` supplies `schema`, `checkpoint`, `unit` (`"embed"`, `"final"`, `"head"`,
or a zero-based layer index **string**), `dtype` (`"fp32"`/`"bf16"`), batch-shaped
`input_ids`, optional `hidden` `.npy` path, `input_mode`, `seed`, `random_scale`,
`threads=2`, and `max_memory_bytes`. No reference output or hidden trace is
passed to the adapter. Disable dropout/cache and use the same no-padding causal
prefill. Derive RoPE positions `0..S-1` on all three axes; no cache is used.

The checkpoint API is `config`, `text`, `prefix`, `weight_map`, `info(name)`
(shape/storage dtype), `read(name, selection, framework="mlx", dtype=...)`,
`rows(name, ids, framework="mlx", dtype=...)` and
`ngram_rows(base, ids, framework="mlx", dtype=...)`. `base` is the name through
`ngram_embedding`, without `.weight` or `.shard_N.weight`. A large expert read
uses `(expert_index, slice(None), slice(None))`. Use `dtype="native"` to read persistent integer PLE hash buffers without
floating conversion; load checkpoint multipliers, vocab sizes and offsets rather
than regenerating them from config. Missing reference buffers fail closed.
Raw stored norms retain their original convention; fold `1+w` only if the port's norm implementation needs it.
Do not concatenate expert tensors or n-gram partitions into resident arrays.

Return a dictionary of NumPy arrays with these exact names/layouts (`B` batch,
`S` sequence, `H` hidden, `C` streams, `E` experts, `K` routed experts):

| Names | Layout/meaning |
|---|---|
| `output` | Layer `[B,S,C*H]`; embed repeated streams `[B,S,C*H]`; final `[B,S,H]`; head `[B,S,vocab]` |
| `embedding` | Before stream replication `[B,S,H]` (embed unit only) |
| `attention`, `moe` | `[B,S,H]`, after output projection / after routed+shared sum |
| `router.logits` | `[B*S,E]`, before softmax |
| `router.experts`, `router.weights` | `[B*S,K]`, indices and corresponding normalized weights |
| `attn.norm`, `mlp.norm` | `[B,S,C*H]`, grouped norm output |
| `attn.mix`, `mlp.mix` | `[B,S,H]`, hyper-connection mixed input |
| `attn.residual`, `mlp.residual` | `[B,S,C*H]`, incoming residual |
| `attn.inject`, `mlp.inject` | `[B,S,C]`, injection weights |
| `attn.streams`, `mlp.streams` | `[B,S,C*H]`, after injection; `mlp.streams == output` |
| `attention.gated_norm` | `[B*S*linear_value_heads,linear_value_dim]` (DeltaNet only) |
| `attention.q_norm`, `attention.k_norm` | `[B,S,heads,head_dim]`, before transpose/RoPE (QSA only) |
| `qsa.mask` | bool `[B,1,S,S]`, indexer-selected visibility, before combining causal mask |
| `ple.ngram_ids` | integer `[B,S,(ngram_size-1)*heads_per_ngram]` |
| `ple.embedding` | `[B,S,ple_embed_dim]`, concatenated selected embeddings |
| `ple`, `ple.norm_key`, `ple.norm_query`, `ple.norm_conv` | `[B,S,C*H]` |
| `final.norm` | `[B,S,C*H]` (final unit only) |
| `<norm>.input` | For every norm trace listed in gate amendment A1: the exact tensor that norm consumed, same layout as its output |
| `attention.gated_norm.gate` | DeltaNet only: the gate tensor `z` the gated norm consumed, `[B*S*linear_value_heads,linear_value_dim]` |

Flatten streams in `(stream,hidden)` order. Floating traces are evaluated and
exported as fp32; preserve integer/bool ids/masks. The required trace set is
computed from actual config and unit. Missing traces, shape mismatch, nonfinite
values, worker failure, memory overrun and stub identity all prevent PASS.
Expert choices compare exact **sets per token**, with order agreement also
reported. Routing weights are sorted with their corresponding expert ids before
comparison, allowing different top-k ordering of the same set.

## Gates, reports, and resume

Fixed before comparisons:

| Compute dtype | Elementwise gate | Cosine floor |
|---|---|---:|
| fp32 | `abs(a-b) <= 1e-4 + 1e-4*abs(a)` | 0.999999 |
| bf16 | `abs(a-b) <= 0.03125 + 0.03125*abs(a)` | 0.999 |

All elements **and** cosine must pass. The coordinator streams contiguous `.npy` traces in bounded chunks, including
full head logits; it does not retain whole fp64 copies or mmap pages. Reports
include maximum absolute error,
maximum relative error (denominator floor `1e-12`), relative L2 error, cosine,
and fraction within tolerance. Zero versus zero has cosine 1; a zero/nonzero
pair has cosine 0. Expert sets, PLE ids and QSA masks require exact agreement
(QSA masks against the tie-ordered reference above).
Fp32's bound accommodates reduction order. Each BF16 allowance is four representable steps near one (`0.03125 = 4*2^-7`);
the combined `atol+rtol*abs(a)` allowance is eight such steps at `abs(a)=1`
(sixteen unit roundoffs). This is a **provisional engineering bound**, with
cosine also constraining aggregate error. It is not a theorem about deep-model quality
and is never automatically widened. Inspect failures against fp32 and the
individual trace; do not fit a bound to a failing port.

### Gate amendment A1: input-conditioned normalization outputs (2026-11-05)

**What.** These traces are the outputs of RMSNorm-like operations; this is the
complete list of traced normalization outputs:

| Trace | Official module | Formula | Weight (relative to text prefix) | Group |
|---|---|---|---|---|
| `attn.norm` | `attn_hyper_connection.hc_norm` (`Qwen4ExpTextRMSNorm`) | offset | `layers.N.attn_hyper_connection.hc_norm.weight` | `hidden_size` |
| `mlp.norm` | `mlp_hyper_connection.hc_norm` | offset | `layers.N.mlp_hyper_connection.hc_norm.weight` | `hidden_size` |
| `final.norm` | `hyper_connection_mixer.hc_norm` (the only final norm) | offset | `hyper_connection_mixer.hc_norm.weight` | `hidden_size` |
| `attention.q_norm`, `attention.k_norm` | QSA `self_attn.q_norm`/`k_norm` | offset | `layers.N.self_attn.{q,k}_norm.weight` | `head_dim` |
| `attention.gated_norm` | DeltaNet `linear_attn.norm` (`Qwen4ExpTextRMSNormGated`) | gated | `layers.N.linear_attn.norm.weight` | `linear_value_head_dim` |
| `ple.norm_key`, `ple.norm_query`, `ple.norm_conv` | PLE `ple.norm_*` | offset | `layers.N.ple.norm_*.weight` | `hidden_size` |

offset: `y = x / sqrt(mean_G(x^2) + eps) * (1 + w)`, mean over contiguous groups
of `G` channels of the last axis. gated: `y = w * x / sqrt(mean(x^2) + eps) *
act(z)`, `act = output_gate_type or hidden_act` (sigmoid for the real
checkpoint; silu default). `eps = rms_norm_eps`. Untraced norms (QSA indexer
`q_layernorm`/`k_layernorm`, DeltaNet's in-kernel q/k l2norm) are not
separately gated; they remain covered only through downstream traces.

Both workers additionally export `<norm>.input` (and `attention.gated_norm.gate`),
captured at the norm call itself (reference: a forward pre-hook; MLX: the
wrapper's call arguments). They are required traces. For each norm trace the
coordinator reads `w` from the checkpoint (never from a worker; rounded to bf16
for bf16 cases, as the official module holds bf16 parameters) and recomputes
`f` in float64 for each side from **its own** input. The trace passes only if
all of the following hold, each under the **unchanged** dtype tolerance above:

1. `mlx_op`: `|y_mlx - f(x_mlx)| <= atol + rtol*|f(x_mlx)|` everywhere, and cosine floor.
2. `reference_op`: the same for `y_ref` against `f(x_ref)`. This is reference
   self-consistency and also validates the harness's transcription of `f`.
3. `input` (and `gate_input`): the two sides' norm inputs pass the plain gate.
   The auxiliary traces also appear as their own gated metrics.
4. chained `y_ref` vs `y_mlx`: cosine floor unchanged, and elementwise
   `|y_ref - y_mlx| <= atol + rtol*|y_ref| + P`, with the propagated bound `P` below.

The plain chained elementwise result is still reported (`unpropagated_pass`,
`fraction_within_unpropagated`) but is informative; the top-level `max_abs`,
`max_relative`, `relative_l2` and `cosine` are the chained ones. Metric entries
carry `gate: "A1-input-conditioned"`; reports carry `gate_amendments`.

**Derivation of `P`.** For one group, `r = sqrt(mean(x^2) + eps)` and
`y_c = s_c x_c / r` (`s = 1 + w`). Since `dr/dx_j = x_j / (G r)`,
`dy_c/dx_j = s_c (delta_cj / r - x_c x_j / (G r^3))`. With an input
perturbation bounded by `e_x = max |x_ref - x_mlx|` (the input trace's measured
max abs diff over the whole trace), to first order

`|dy_c| <= |s_c| / r * (|dx_c| + |x_c| * sum_j |x_j||dx_j| / (G r^2))
       <= |s_c| / r * e_x * (1 + |x_c| * mean|x| / r^2) = P_c`.

`|s_c| / r` is the per-element gain; the bracket is the correlated RMS term
(at most `1 + |x_c|/r`). For the gated norm the gate input adds
`|w_c| |n_c| L e_z` with `n_c = x_c / r`, `e_z` the gate's measured max abs
diff and `L` the activation's Lipschitz constant (sigmoid 1/4, silu 1.1), and
`s_c` becomes `w_c * act(z_c)`. `r`, `mean|x|`, `x_c`, `z_c` are taken from the
reference input in float64. Second-order terms are `O(e_x^2 / r^2)`; criteria
1-3 bound everything else independently.

**Why the chained comparison alone is wrong for norm outputs.** Every trace is
compared against a reference computed from the reference's own upstream
values. An RMSNorm multiplies its input error by `|s_c|/r`, which for a
small-RMS row and a large `|1 + w_c|` reaches about 10^3, far more than any
non-normalizing op in the layer. A fixed absolute tolerance then fails on
legitimate upstream fp32 rounding that passed its own gate one trace earlier,
while saying nothing about whether the norm itself is right. Conditioning on
each side's own input isolates the norm op exactly; the propagated bound keeps
a declared, derivable limit on the chained difference.

**What still fails** (unit tests in `NormGateTests`): a wrong weight on one
channel (a 0.1% change) or the wrong `w` vs `1 + w` convention; a different
eps (1e-5 vs 1e-6 at row RMS 0.03); normalization over the wrong axis or stream
grouping (whole `C*H` instead of per-stream `H`, or over the sequence); a wrong
gate activation; a corrupted reference output; and inputs that differ
genuinely (both sides self-consistent but the chained cosine falls below the
floor, or one large localized input error, which fails the input gate instead
of buying a loose allowance). The observed outlier-gain case passes.

**Triggering evidence.** The first real-weight streamed run (work
`/private/tmp/jwgold-run/work`, pinned revision above) stopped at layer 0. Of
8 cases only `tokens-b-fp32-real` failed, on one trace, `mlp.norm`: exactly 1
of 81,920 elements outside the elementwise gate, index `(0,0,3820)`,
reference -0.43276, MLX -0.43293, diff 1.70e-4 against an allowance of
1.43e-4; cosine 1-3.3e-12, relative L2 2.57e-6. Its input `attn.streams`
passed its own gate (max abs 6.0e-7); at that element the inputs were
-4.773969e-4 vs -4.775831e-4 (diff 1.86e-7). The per-element gain
`|1+w_c|/r` there is 906.5 (`1+w_c = 2.60`, about 4.7x the median `|1+w|` of
0.55; row RMS `r = 2.87e-3`), against a median gain of 163. The exact
float64 propagation `|f(x_ref) - f(x_mlx)|` at that element is 1.6967e-4,
equal to the observed difference to four digits; the op errors are 2.6e-9
(reference) and 8.5e-9 (MLX). The difference is upstream fp32 rounding
amplified by the norm gain, not a port error.

**Offline re-evaluation of the saved layer-0 artifacts** with
`scripts/qwen4_gold_regate_legacy.py` (no worker, no download; norm weights
from the hash-verified restaged view `work/staging/views/0`). The legacy cases
lack `*.input` traces; `attn.norm`'s input is the case `input.npy` cast to the
compute dtype (both workers read it), `mlp.norm`'s is each side's own
`attn.streams`. `attention.gated_norm` consumed untraced tensors and keeps its
stored plain-gate PASS (A1 applies on rerun). All 8 cases PASS under A1:

| Case | Stored | A1 | `mlp.norm` chained max abs | max `P` | input max abs | op max rel (mlx / ref) |
|---|---|---|---:|---:|---:|---:|
| tokens-a-fp32-real | PASS | PASS | 7.46e-5 | 1.91e-3 | 7.45e-7 | 1.86e-7 / 1.81e-7 |
| tokens-a-fp32-random | PASS | PASS | 3.53e-5 | 6.23e-4 | 1.34e-6 | 1.85e-7 / 2.16e-7 |
| tokens-b-fp32-real | **FAIL** | PASS | 1.70e-4 | 1.47e-3 | 5.96e-7 | 1.80e-7 / 2.23e-7 |
| tokens-b-fp32-random | PASS | PASS | 6.01e-5 | 1.06e-3 | 8.49e-7 | 1.93e-7 / 2.36e-7 |
| tokens-a-bf16-real | PASS | PASS | 0.0625 | 0.626 | 2.44e-4 | 3.89e-3 / 3.89e-3 |
| tokens-a-bf16-random | PASS | PASS | 0.0625 | 0.903 | 1.95e-3 | 3.89e-3 / 3.89e-3 |
| tokens-b-bf16-real | PASS | PASS | 0.0625 | 1.20 | 4.88e-4 | 3.89e-3 / 3.89e-3 |
| tokens-b-bf16-random | PASS | PASS | 0.0625 | 0.608 | 4.88e-4 | 3.89e-3 / 3.89e-3 |

`attn.norm` in every case: input identical (`P = 0`), chained max abs
<= 2.9e-6 (fp32) / 0 (bf16), op max rel <= 2.2e-7 (fp32) / 3.9e-3 (bf16, one
bf16 rounding). At the failing element the bound is 1.43e-4 + `P` 6.03e-4 =
7.46e-4; the largest diff/bound ratio over the trace is 0.23.

**Adopted after seeing a failure; why this is not result-fitting.** This
amendment was written after, and because of, the layer-0 failure above. It is
nevertheless not fitted to that result: (a) no tolerance constant changed:
`atol`, `rtol` and the cosine floors are those fixed before any comparison;
(b) the added allowance `P` is a closed-form first-order derivation from the
official formula, the checkpoint weight and the measured input error, with no
free parameter, and is applied to every norm trace in every unit, not to one
element or one layer; (c) it adds gates rather than removing them: each norm
op is now checked against its own input on both sides (which the old chained
gate could not do at all), the reference's self-consistency is checked, and
the new auxiliary input traces are gated; (d) the plain chained result is still
reported for every norm trace, so any reader can see where A1 changed a verdict;
(e) its sensitivity to real defects is fixed by the unit tests above, written
with the amendment. The non-norm traces and their gates are untouched. Results
computed before A1 are not comparable verbatim: the harness fingerprint
changes, and the streamed run must be repeated in a fresh work directory.

`layer-NNN.json` and `.md` aggregate all cases for each layer; `embed`, `final`,
and `head` have equivalent reports. Per-case directories hold requests, worker
logs, every trace, metrics and artifact hashes. `provenance.json` records config,
index, selected shard hashes, actual manifest coverage, input prompts, source
hashes, package versions and tolerances. A supplied `sha256.txt` is checked for
each listed selected file; a missing entry is recorded as uncovered, never
claimed authenticated. Hashes establish local reproducibility, not independent
proof of official origin. No evidence is written into the checkpoint directory. Workers verify config/index
digests and reject shards that were absent when hashed or whose inode, size,
mtime or ctime changed; file stamps are checked before reads and after execution.
A download completing mid-run therefore requires a new invocation fingerprint.

Resume rehashes selected checkpoint bytes and all reused `.npy` artifacts. It
requires matching config/index, harness source, adapter and declared dependencies,
framework versions/reference source, prompts, seed, scale and memory setting.
Old provenance is preserved when the fingerprint changes.
A changed request preserves old case files under `.attempt-N`. Reference/MLX
worker errors are retried. A failed numerical comparison or stub report is
reused only when its full fingerprint and artifacts are unchanged. Keep source
and interpreter environments fixed throughout a long full run. Do not infer
full coverage from a subset run: `full_48_layer_gold` is true only after all 48
layers plus endpoints pass both input modes and both dtypes. Short prompts still
need the QSA-pruning coverage caveat above.

`summary.json` has exit status 0 only for a complete pass of the requested
coverage; otherwise the CLI exits 2. Missing real predecessors produce
`BLOCKED_REAL_INPUT`, independently of random-input results. A stub never earns
PASS, including when a particular embedding trace happens to match exactly.

## Local execution evidence (2026-11-05)

See the [dated run report](../../run_reports/2026-11-05-flashnext-gold-parity.md)
for exact commands, hashes, counts, peak memory and limitations. Neither independent port branch was present in this clone when
checked; local executions used the explicit stub. The sandbox cannot initialize
MLX's Metal device, even when requesting the CPU device. Consequently local
Torch execution and harness self-tests must not be presented as MLX parity.

## Streaming laptop run plan (2026-11-05)

`scripts/run_qwen4_gold_stream.py` stages weights from **Qwen/Qwen3.8-Flash-Next**,
revision `de4b8e4d43b917e7706784d8bb445c9af86a3540`. This is a separate online
coordinator; the existing parity workers remain offline and serial. All Hub
storage, including partial downloads, is under `--work/staging`; Xet is
disabled. Before a shard is used, its complete bytes must match the pinned
revision's HF LFS SHA256 and size from `get_paths_info`. Config/index bytes are
checked against their Git blob identities. No tokenizer is downloaded.

### Disk constraint and the shared-shard ruling

The default `--shared-shards retain` follows the requested whole-shard policy:
keep a shared original until its last unit. **This policy cannot fit the stated
laptop disk budget.** The index places embeddings with layer 9, layer 1 with
layer 10, layer 2 with layer 19, layer 3 with layer 29, layer 4 with layer 39,
and layer 5 with layer 47. Official meta-model shapes plus the supplied index
prove a **24.110 GiB lower bound at layer 8**, before headers, MTP bytes, traces,
or the 25 GiB reserve. `retain` therefore refuses the default 12 GiB staging
plan before downloading weight shards. Raising the cap alone does not create
the missing free space.

The explicit alternative `--shared-shards restage` authenticates a full source
shard, copies only the current unit's tensor bytes into a local safetensors
view, records the source hash, selected names and derived file hash, and deletes
the original. Later users download the shared original again. No floating
conversion occurs in this view. This alternative is implemented and tested on
tiny checkpoints, but **the lead must approve this exception to whole-shard
retention before selecting it for the laptop run**. It is never selected
silently. Source, budgets, policy, adapter/dependencies, runtimes and prompts
are frozen in the invocation fingerprint; use a fresh work directory to change
them.

### Native commands

Run these outside the no-network implementation sandbox. First extract the
already available canonical source without merging its branch:

```bash
GOLD_CANONICAL=/private/tmp/jw-gold-canonical-65763077
mkdir -p "$GOLD_CANONICAL"
git show 65763077aec03235d149517f6c97a7cda987a74c:joulewise/align/models/qwen4_exp.py > "$GOLD_CANONICAL/qwen4_exp.py"
git show 65763077aec03235d149517f6c97a7cda987a74c:scripts/align_convert_qwen4_exp.py > "$GOLD_CANONICAL/canonical_converter.py"

JW_GOLD_CANONICAL_MODULE="$GOLD_CANONICAL/qwen4_exp.py" \
JW_GOLD_CANONICAL_CONVERTER="$GOLD_CANONICAL/canonical_converter.py" \
PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 \
/private/tmp/jwsol/venv-both/bin/python -B -m unittest tests.test_qwen4_gold_stream

JW_GOLD_CANONICAL_MODULE="$GOLD_CANONICAL/qwen4_exp.py" \
JW_GOLD_CANONICAL_CONVERTER="$GOLD_CANONICAL/canonical_converter.py" \
PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 \
/private/tmp/jwsol/venv-both/bin/python -B -m unittest -v tests.test_qwen4_gold_canonical_adapter
```

The combined native venv must contain Transformers 5.22.1, Torch, NumPy,
safetensors, MLX 0.31.2 and mlx-lm 0.31.3. The last two are the canonical
converter's pins. Native tests cover the MLX sparse gather and canonical
6-bit/group-64 quantization, bf16 passthrough, and per-tensor conversion resume.
They skip when MLX or the explicit canonical paths are unavailable.
The adapter module's native tests run `--make-tiny` through the actual parity
workers for fp32 and bf16, checking every trace and all seven tiny units, then
run the streaming driver with a local-only shard source, sparse PLE, byte-subset
restaging, and completed-run resume. They require PASS under the unchanged
tolerances. CPU-only tests cover converter mapping completeness against the
official tiny index, packed/unpacked expert shapes, saved hash buffers and
source provenance. Native MLX results remain unverified until this command runs
on Metal; skipping is not parity evidence.

Use the repository's **gold/v1 canonical adapter** below:
the canonical model file does not declare `run_gold`. Hash all separately
imported adapter sources with additional `--adapter-dependency` flags.
After the shared-shard ruling, the laptop command is:

```bash
GOLD_ADAPTER="$PWD/joulewise/align/qwen4_gold/canonical_adapter.py"
GOLD_WORK="$PWD/runs/qwen4-gold-stream-20261105"

env -u HF_HUB_OFFLINE -u TRANSFORMERS_OFFLINE \
/private/tmp/jwsol/venv-ref/bin/python -B scripts/run_qwen4_gold_stream.py \
  --work "$GOLD_WORK" \
  --ref-python /private/tmp/jwsol/venv-ref/bin/python \
  --mlx-python /private/tmp/jwsol/venv-mlx/bin/python \
  --mlx-module "$GOLD_ADAPTER" \
  --adapter-dependency "$GOLD_CANONICAL/qwen4_exp.py" \
  --adapter-dependency "$GOLD_CANONICAL/canonical_converter.py" \
  --shared-shards restage --min-free-gb 25 --max-staging-gb 12 \
  --max-gb 12 --timeout 3600 --resume --keep-going
```

`--keep-going` records a unit whose parity does not PASS (`status: FAIL` in
`manifest.json`, with its failing cases and traces) and continues. This is valid
because every unit's real input is the predecessor's **official reference**
`output.npy` (`Harness.case` returns `reference/output.npy`), never an MLX
output, so a candidate failure cannot contaminate later inputs. A reference
error, a broken reference chain, or a guard failure still stops the driver.
Failed units are not converted with `--convert-out`. `summary.json` then has
`status: FAIL`, a `failures` list (unit, case, failing and missing traces),
`full_48_layer_gold: false`, and the CLI exits 2; the same list is printed at
the end. A recorded FAIL unit is integrity-checked on resume and never silently
rerun. `--keep-going` does not enter the invocation fingerprint, since it does
not change any comparison.

Add `--plan-only` to that same command first to save exact pinned file sizes and
download estimates without downloading weight shards. Remove only `--plan-only`
to start; repeat the actual command unchanged after sleep or interruption.
The built-in two token prompts are fixed lengths 9 and 8, including token zero.
An explicit `--prompts-json` may replace them before starting a fresh run.

### Downloads, disk peak, and timing

With original retention, all 131 source shards are touched: approximately
**360 GB** downloaded, even though 333 vision tensors and 31 MTP tensors are
excluded from computation. Their bytes share shards with text weights, so
skipping these tensors does not avoid their physical download. `restage`
repeats shared downloads and the two hash-buffer shards: plan approximately
**460 GB**, with the authoritative byte count in
`manifest.json -> storage.restage_download_bytes` after the metadata preflight.
The offline shape projection is a lower bound, not authenticated file metadata.

For the short built-in prompts, budget roughly **9 GiB staging plus 3 GiB
retained traces/inputs/reports**; these are planning estimates, not observed
real-weight peaks. Both downloads and byte-subset writes enforce the 12 GiB
staging cap and the 25 GiB free-space reserve using current disk usage. Partial
downloads count toward staging. Reference/MLX workers remain within the existing
12 GiB aggregate sampled memory guard. Longer prompts increase trace/logit
storage substantially; the staging cap does not cap retained evidence.

Do not quote an unmeasured per-unit time. Measure embeddings, layer 0, QSA
layer 3, and the PLE extraction phase on the laptop. Sum each case's
`reference.elapsed_seconds` and `mlx.elapsed_seconds` in the unit JSON; default
decoder units have eight cases (two prompts × two dtypes × real/random).
Add source bytes / measured download throughput, complete-shard SHA256 time,
and local subset-copy time. Extrapolate separately by actual config layer type;
include the approximately 104 GB PLE-shard download phase once, plus shared
re-downloads from the plan. Suspend/sleep and network retry time are additional.

### Durable chain, sparse PLE, and PASS

Every real input is the predecessor's official reference `output.npy`, for
each prompt and dtype independently. That flattened `[B,S,C*H]` array includes
all residual streams. The reference's existing persisted traces and case input
snapshots are reused; `manifest.json` records the chain paths, completed-unit
result paths/hashes and artifact hashes. A completed unit, a completed case
inside an interrupted unit, and committed PLE rows survive restart. Resume
rehashes reused evidence and refuses changed invocation inputs. Cache/KV decode
state is absent because this is a cache-free prefill test.

The PLE planning worker constructs the official 5.22.1 NGramEmbedding on meta,
loads its three checkpoint I64 buffers, and calls its unchanged hashing
`forward` on the fixed prompts. Only the final embedding gather is replaced
with an index recorder. Each table partition contributes exact raw bf16 row
bytes to `.npy` files, with tensor name, row ids, source LFS hash and row-file
hash. Both backends receive the same sparse checkpoint shim. The reference
still computes its own ids; the adapter must independently compute its ids.
Any unrecorded lookup raises. This is equivalent to the full table for these
fixed prompts because prefill lookup indices depend on tokens, EOS/context and
the checkpoint hash buffers, not hidden states; all other table rows are unused.
The unittest independently compares sparse and full official tiny-table
forwards, including EOS, duplicates, partition boundaries and both dtypes.

GOAL item 5 can be recorded PASS only after the real, pinned source run has
`summary.json` status `PASS`, all 51 units (embed, 0–47, final, head) complete,
and `coverage.full_48_layer_gold == true`, using a real MLX adapter. Every
required intermediate trace must satisfy the unchanged harness tolerances;
router expert sets, PLE ids and QSA masks must agree exactly. No missing cases,
stub, sparse miss, hash failure or memory failure may be waived. Retain the
shared-shard ruling with the result. Short prompts do not establish real QSA
budget truncation, decode/cache parity, full-model quality, or GOAL item 11's
separate full-checkpoint-resident Mac validation. **No real MLX PASS is claimed
by this implementation run.**

### Optional conversion output

Choose conversion at the initial invocation by appending:

```bash
  --convert-out /absolute/lead/chosen/Dropbox-or-external-volume/qwen4-maxfit \
  --canonical-converter "$GOLD_CANONICAL/canonical_converter.py" \
  --canonical-module "$GOLD_CANONICAL/qwen4_exp.py"
```

Each unit is exported only after its parity passes. The worker uses the
canonical mapping, shape/chunk/writer helpers and `quantization_for` policy:
6-bit group-64 routed experts and bf16 other floating weights. Hash buffers
remain exact integers in unit metadata. Each unit has a SHA256 manifest and
resumable per-tensor progress. PLE conversion re-downloads its source shards and
copies the **entire** bf16 table into canonical row-record order after parity;
its committed spans survive interruption. This adds roughly 104 GB of source
downloads in restaging mode. It never exports the sparse parity rows as a full
table.

These outputs are unit fragments (`complete_model: false`), requiring assembly
and canonical full-model validation before loading as one model. Full maxfit
output needs roughly 210 GB, including the approximately 102 GB PLE table.
A Dropbox directory on the same nearly full SSD does not provide that capacity
automatically. Use sufficient local/external capacity; guards stop otherwise.
There is no cloud upload, eviction, or Dropbox API integration. Output files
must remain readable for resume integrity checks.
