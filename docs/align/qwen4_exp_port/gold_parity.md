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
pair has cosine 0. Expert sets, PLE ids and QSA masks require exact agreement.
Fp32's bound accommodates reduction order. BF16's approximately four
unit-roundoff steps near one is a **provisional engineering bound**, with cosine
also constraining aggregate error. It is not a theorem about deep-model quality
and is never automatically widened. Inspect failures against fp32 and the
individual trace; do not fit a bound to a failing port.

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

See the dated run report for exact commands, hashes, counts, peak memory and
limitations. Neither independent port branch was present in this clone when
checked; local executions used the explicit stub. The sandbox cannot initialize
MLX's Metal device, even when requesting the CPU device. Consequently local
Torch execution and harness self-tests must not be presented as MLX parity.
