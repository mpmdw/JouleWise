# JouleWise Qwen3.8-Flash-Next text port

**PROVISIONAL — MLX numerical and real-model validation are release blockers.**
This is owned code for mlx **0.31.2** / mlx-lm **0.31.3**, loaded through the
pinned library's `config.json` `model_file` seam. No stack pin changes.

Ed's 2026-11-05 precision decision ("as close to the full fp16 as i can get")
selects **maxfit**: routed `switch_mlp` experts alone are affine 6-bit, group
size 64. **Every other floating weight is native, unquantized bf16**:
attention, QSA indexer, DeltaNet, routers/gates, shared experts,
hyper-connections, embeddings/head, PLE projections/convolution and norms.
The PLE table is **bf16 on disk**, accessed through mmap. **maxfit5** is the
fallback with only the routed experts reduced to 5-bit, still group size 64.
Neither profile permits a different group size or PLE storage. Existing CLI
defaults remain compatible; select these profiles explicitly.

## Memory planning

`joulewise.align.models.qwen4_exp_memory.memory_model` enumerates every text
tensor from the local HF config. The release has **176,943,899,520 text
parameters**: 120,795,955,200 routed expert parameters, 51,200,245,760 PLE table
parameters, and 4,947,698,560 others. Vision/MTP are omitted.

At context 40,960, chunk 64 and batch 1, the selected profiles have these
**decimal GB (10^9 bytes)** planning estimates, including bf16 affine
scales/biases and the unmeasured 3 GB runtime reserve:

| Component / constraint | maxfit | maxfit5 |
|---|---:|---:|
| Routed experts (6 / 5 bits, group 64) | 98.146713600 | 83.047219200 |
| All other resident weights (bf16) | 9.895397120 | 9.895397120 |
| **Resident weight total** | **108.042110720** | **92.942616320** |
| Cache/state + chunk workspace | 4.637355528 | 4.637355528 |
| **Estimated GPU peak** | **112.679466248** | **97.579971848** |
| **Headroom vs 115.4 GB GPU working set** | **2.720533752** | **17.820028152** |
| PLE table on disk (bf16) | 102.400491520 | 102.400491520 |
| Physical upper estimate, including PLE pages | 134.154302728 | 119.054808328 |

Memory is a hardware constraint. `memory_model` returns a JSON-serializable
`MemoryReport` with `fits_gpu_working_set(limit_bytes)`, replacing the old
80 GB budget flag. JSON fields `gpu_working_set_limit_bytes`,
`gpu_working_set_headroom_bytes` and `fits_gpu_working_set` use 115,400,000,000
bytes by default; supply `gpu_working_set_limit_bytes` to the function or
`--gpu-working-set-bytes` to the CLI for a different device limit. Headroom is
signed and equality fits. These estimates do not establish actual GPU peaks.

For comparison, the earlier profiles below use group size 64, bf16 retained
tensors and bf16 affine scales/biases. Columns 8/6/4/3 quantize eligible leaves
at that width; indexer, DeltaNet, routers, norms and convolutions remain bf16.
Mixed means routed experts q4 and other eligible leaves q8. No table column
claims measured GPU allocation.

| GPU resident component | 8 bits | 6 bits | 4 bits | 3 bits | Mixed |
|---|---:|---:|---:|---:|---:|
| Routed experts | 128.3457 | 98.1467 | 67.9477 | 52.8482 | 67.9477 |
| Token embedding / head | 1.3509 | 1.0330 | 0.7152 | 0.5562 | 1.3509 |
| Hyper connections | 0.6816 | 0.5217 | 0.3618 | 0.2818 | 0.6816 |
| DeltaNet | 4.1730 | 4.1730 | 4.1730 | 4.1730 | 4.1730 |
| Attention | 0.6351 | 0.4856 | 0.3362 | 0.2615 | 0.6351 |
| QSA indexer | 0.0393 | 0.0393 | 0.0393 | 0.0393 | 0.0393 |
| Shared experts | 0.2507 | 0.1917 | 0.1327 | 0.1032 | 0.2507 |
| Routers / shared gates | 0.1261 | 0.1261 | 0.1261 | 0.1261 | 0.1261 |
| PLE projections / conv | 0.0350 | 0.0268 | 0.0186 | 0.0145 | 0.0350 |
| PLE table | 0 | 0 | 0 | 0 | 0 |
| **Weight total** | **135.6373** | **104.7439** | **73.8506** | **58.4039** | **75.2393** |
| **Estimated peak, chunk 64** | **140.2746** | **109.3813** | **78.4879** | **63.0413** | **79.8767** |

The context cap is **40,960**, from `scripts/align_pilot_kit.py:CONTEXT_CAP`,
not the model's 262,144 training-position limit. At batch 1 and this cap:

| Persistent cache/state | Bytes |
|---|---:|
| KV (12 indexed layers, 2 KV heads, dimension 256, bf16 K/V) | 1,006,632,960 |
| Raw QSA keys (12 × 128 × context × bf16) | 125,829,120 |
| QSA validity | 491,520 |
| DeltaNet recurrent fp32 state (36 × 48 × 128 × 128) | 113,246,208 |
| DeltaNet convolution history | 2,211,840 |
| PLE dilated convolution history | 184,320 |
| PLE token history | 8 |
| **Total** | **1,248,595,976** |

Chunk 64 workspace estimate is 3,388,759,552 bytes, including a deliberately
unmeasured **3 GB runtime/allocator reserve**, sparse gathered KV, fp32 indexer
scores/DeltaNet buffers, activations and one layer's cache growth copy. Chunk
256 raises mixed peak to 80,759,813,384 bytes. Converted configs enforce
`jw_max_prefill_tokens=64` and `jw_context_cap=40960`; pass
`prefill_step_size=64` to generation (mlx-lm's default is too large).

The selected profiles' bf16 offloaded table occupies **102,400,491,520 disk
bytes**. At 160 elements per row, a token gathers 16 rows / **5,120 logical
bytes** before duplicates. BF16 rows have no scales/biases and undergo no
affine dequantization: only gathered uint16 payloads expand to fp32 and are
cast to the activation dtype in the PLE module. For legacy profiles, q4 uses
28,160,135,168 bytes including per-row fp32 scale/bias (1,408 logical bytes
per token); q8 uses 53,760,258,048 bytes.

**Offload does not eliminate physical page-cache memory.** A uniform-access
estimate over 40,960 tokens touches about **10.19 GB** of 16-KiB file pages
with bf16 PLE (8.93 GB with q4). The conservative page-span upper bound is
21.47 GB. Maxfit's physical upper estimate is **134.15 GB before OS/other
processes**, exceeding the target's 128 GB despite its estimated GPU fit;
maxfit5 is 119.05 GB. File pages are reclaimable; neither the page-cache
estimate nor the 3 GB reserve is a hard allocation bound. The small 2.72 GB
maxfit GPU margin also needs real validation. Both profiles fit the stated
115.4 GB GPU working set **on paper**.
Actual peak and zero swap must be measured before an ALIGN window. A model
estimate alone cannot guarantee that a machine never swaps.

Reproduce byte accounting without allocating model tensors:

```sh
python3 -B -m joulewise.align.models.qwen4_exp_memory tests/align/fixtures/qwen4_exp_text_config.json --chunk-tokens 64
```

Memory tests: `python3 -B -m unittest tests.align.test_qwen4_exp_memory` —
3 PASS. Includes the actual kit cap, official expert/PLE parameter counts,
maxfit precision/storage, hardware-limit boundaries and signed headroom,
JSON serialization and context/chunk/bit-width tradeoffs.

## Architecture and authority

The authority is the supplied official Qwen/Hugging Face Transformers
reference, not an existing MLX checkpoint. Source SHA256 pins at intake:

| Local source | SHA256 |
|---|---|
| `transformers-qwen4_exp/modeling_qwen4_exp.py` | `3424f1b7a7e4d690c87a43758d791f37cede3fcb7e75f52e80ca498f9b84276e` |
| `transformers-qwen4_exp/configuration_qwen4_exp.py` | `bb1d71db625fb50d1bf86589032edaa9c0f00f8ba2b9f1d06946aa0a8eeae246` |
| `hf-flashnext/config.json` | `889658f2508e8c61d409b02e70e0d78d8d4452ec65aaafbe129805d213d2e74b` |

The runtime consists of two owned files: `qwen4_exp.py` and
`qwen4_exp_tables.py`. Conversion copies and hashes both. No imports from the
community port, Transformers or mlx-vlm occur at runtime. NumPy handles host
integer hashing and file rows; the only model backend dependencies are the
pinned MLX/MLX-LM libraries. The package initializer imports no backend, so
ordinary JouleWise and bare-Python CI remain usable.

| Component | Reference derivation and implementation |
|---|---|
| DeltaNet | Official lines 389-617: normalized q/k, fp32 recurrent delta update, decay `exp(-exp(A_log) * softplus(a + dt_bias))`, sigmoid beta, depthwise causal conv and gated RMSNorm. Calls the pinned native gated-delta kernel with fp32 q/k/v and state, preserving the exact sum-plus-epsilon normalization. Small key dimensions use native ops. |
| QSA | Lines 663-889: pool complete blocks of visible raw keys, normalize, rotate at block starts, score by summed positive q·k over index heads, choose budget/compression blocks and append the query's partial tail. Retains raw index keys in cache. Selected K/V are gathered per query for SDPA rather than building dense attention scores over the entire history. |
| MoE | Lines 891-988: fp32 softmax router, normalized top-10 routing, 512 routed SwiGLU experts plus one sigmoid-gated shared expert. Pinned SwitchGLU stores separate gate/up/down tensors; conversion splits the fused gate/up on its penultimate axis. |
| Hyper connections | Lines 990-1020: grouped RMSNorm over four streams, low-rank sigmoid mixing, stream mean and sigmoid block injection; final mixer returns one text stream. |
| PLE | Lines 1028-1245: exact SplitMix64 multipliers, per-head prime vocabularies, XOR hashing with EOS resets, per-stream key/query gates and dilated depthwise convolution. Hash arithmetic stays CPU int64. |

The unmerged community port was read only as a second opinion (SHA256
`d6470a2131a64ff37024dfffd2b5bc8c3f4db625f0f3b1ceec7fe346852c1a87`).
Ideas cross-checked there: per-row block alignment / query-local tails
(`qwen4_exp.py:252-344`, re-derived from official 716-750); indexer-aware cache
trim (901-925, re-derived from official cached raw-key use and pinned
`KVCache.trim`); checking reconstructed hash constants (1173-1190, re-derived
from official 1035-1100). Host mmap offload, streamed safetensors conversion,
the strict tensor inventory and sparse K/V gather are owned designs. No
community module was imported, executed or copied wholesale.

## Deliberate differences and limits

- **Deterministic QSA ties.** Complete blocks are selected and emitted by
  `(score descending, block index ascending)` in prefill, chunked prefill and
  stepwise decode. Block indices are relative to each row's first real token;
  causal visibility and the query-local incomplete tail are unchanged. Exact
  zero ties are common because each head contributes `relu(q·k)`; no epsilon
  is added to scores. The official Torch topk leaves ties unspecified, so
  different tied subsets can legitimately produce different attention output.
  `qsa_topk` uses argpartition and an exact cutoff-count check. If no tie
  straddles the cut, it sorts only the K selected blocks (index first, then a
  stable score sort). If any row straddles, it stably sorts all N blocks.
  Selection cost is O(N + K log K) normally, O(N log N) on the tied fallback,
  plus one host synchronization for the tie check. Early queries' masked
  `-inf` ties can also trigger the fallback in a prefill batch. This costs
  more than the previous unordered argpartition; native latency is unmeasured.
  The forced-ties gold variant exports actual MLX block orders and replays
  them by patching both Torch topk APIs **only inside QSA**. It compares all
  three modes and checks that an alternative admissible zero-tie subset
  changes logits. This isolates agreement modulo ties without changing MoE.
- **Optional bf16 accuracy (default ON).** Set the JSON boolean
  `jw_bf16_fp32_ops=false` to recover the previous bf16 arithmetic. The
  default `true` evaluates hyper-connection stream means and sigmoid gates
  in fp32, then casts each result back to its original bf16 activation dtype.
  This covers hyper mixing/injection, attention output, shared-expert, PLE
  and DeltaNet beta gates. The already-fp32 gated norm is unchanged. For beta,
  the port uses pinned mlx-lm's same `compute_g`, recurrent ops and native
  kernel dispatch with the promoted-and-rounded sigmoid result. SiLU,
  projections and products retain their original arithmetic. Other input
  dtypes, including fp32, take the original operations without new casts.
  The flag is read from flat/nested text config (an outer override wins),
  defaults on for configurations lacking the field in this runtime and is
  explicit in new converter output.
  Changing runtime code/config requires a new artifact and manifest pin.
  The reported single-op bf16 error excess of 1.2–1.6× Torch suggests roughly
  **17–38% less error for the affected operations** if fp32 evaluation reaches
  Torch-like accuracy on matched inputs. This is an expectation from the
  supplied finding, not a measured improvement here or a layer/logit bound;
  bf16 rounding, unchanged SiLU, matmuls and error propagation remain.
  Casts and fp32 temporary buffers add unmeasured latency/workspace. Native
  `tests.align.test_qwen4_exp_precision` checks four-stream means/sigmoid
  accuracy, the disabled legacy path, beta ops/kernel dispatch and bitwise
  fp32 flag equivalence in prefill/chunks/steps. All native results are pending.
- **Text only.** Official `Qwen4ExpForCausalLM` lines 1568-1664 uses no MTP
  module. Ordinary next-token logits therefore need neither the speculative
  MTP head nor the vision tower. Their checkpoint keys are explicitly logged
  as omissions. Image/video inputs and speculative MTP are unsupported.
- **Norms retain raw HF weights.** Official RMSNorm lines 141-166 computes
  normalization and `1 + weight` in fp32 before casting. This port does the
  same. DeltaNet's gated norm remains conventional. There is no fold and no
  guess about already-folded oMLX/Vontra weights. Only our explicit
  `hf-zero-centered-v1` artifact representation is accepted.
- **Padding is explicit initial left padding.** QSA groups begin at the first
  real token of each row; padding cannot change block RoPE positions. The
  public call accepts a boolean `attention_mask`. Holes, right padding and
  padding introduced after cached tokens fail explicitly. All-padding rows
  have their attention output discarded. Automatic BatchGenerator cache
  merge is unsupported and raises rather than silently losing index state.
- **Cache ownership.** Indexed layers subclass native KVCache; serialized
  state is K, V, raw index keys, validity. Trimming crops all four together.
  Recurrent layers subclass ArraysCache: convolution history, fp32 recurrence
  `[B,Hv,Dv,Dk]` (native orientation, transpose of the official state), PLE
  convolution history and int32 token history, plus offset metadata. Native
  save/load sees registered class names. Recurrent state cannot be trimmed;
  whole-hybrid rewrites rebuild or restore a snapshot. Indexer-dropping cache
  quantization is explicitly refused.
- **Disk PLE.** HF table shards stream in numeric order into a row-major
  bf16/fp32 or row-affine q4/q8 table. Advanced NumPy indexing copies unique
  gathered rows; bf16 rows expand by bit conversion, and q4/q8 rows are
  dequantized. Only gathered rows transfer to MLX. The
  mapped table never appears in `model.parameters()`. Large construction
  without a disk descriptor is refused. q4 uses low nibble first, one fp32
  scale and bias per row; this file format is independent of MLX weight
  packing. mmap relies on normal OS page-cache eviction.
- **Bounded single-stream operation.** Converted configurations expose the
  40,960 runtime position limit at the top level, and enforce 64-token chunks
  and the consumed-token cap. Batch-1 is the memory budget. Explicit padded
  batches are for correctness testing and require their own memory estimate.
  Existing ALIGN runtime warmup currently omits `prefill_step_size`; it must
  be threaded through warmup and stream options before this artifact can be
  admitted to a campaign. Anchor configuration and runtime code were not
  changed in this task.

## Conversion and integrity

`scripts/align_convert_qwen4_exp.py` reads safetensors headers and at most
about 32 MiB of row data per source slice (plus packed/copy buffers).
It never constructs the full HF or MLX model. It accepts both the release's
fused expert layout and `save_pretrained` per-expert tensors, nested
`model.language_model` prefixes, monolithic PLE and `shard_N` PLE tensors.
It validates all expected shapes and every text tensor, including indexer
weights/norms and saved hash constants, before creating output.

Supported profiles: `fp32`, `bf16`, `3`, `4`, `6`, `8`, `mixed`, **`maxfit`**,
**`maxfit5`**. Maxfit/maxfit5 quantize every routed expert to 6/5-bit at group
64 and store all other weights and PLE in bf16; omitted `--ple-storage`
selects bf16 for these two profiles. Incompatible storage/group overrides and
expert widths fail explicitly. Mixed uses
q4 experts and q8 eligible other leaves; indexer, DeltaNet, norms, routers
and convolutions remain bf16. Unsupported narrow quantization groups retain
source precision. No parent Attention module is replaced by a quantized
module. Indexer retention is enforced structurally, not inferred from an
apparently coherent generation.

Each output safetensors file holds one target tensor and its quantization
metadata if applicable, written by slices. The index maps each tensor to its
file. The completion manifest records input hashes, output payload hashes,
stack pins, profile, omissions and norm representation. A failure leaves an
incomplete directory without a completion manifest. The output directory
must be new; never overwrite an existing converted artifact.

For the 102.4 GB bf16 PLE output, one source shard is mapped at a time and
bounded slices append to a single row-major `.bf16.bin` file per layer.
Existing bf16 payloads copy unchanged, including exact stored bits, without
fp32 expansion/re-rounding. Other floating inputs round to bf16 in bounded
slices. The manifest's `ple_tables` records descriptors, total byte sizes and
each source shard's input filename/tensor and output row/byte ranges, alongside
the input/output hashes. No whole-table concatenation or eager GPU allocation
is needed. The flat file preserves the existing mmap lookup contract.

The manifest hashes every converter output **except itself**; the CLI prints
its SHA256 to pin in the lead's artifact ledger. Use
`load_verified_model(directory, externally_recorded_manifest_sha256)` from
the converter module to verify the externally pinned manifest, complete file
inventory and every payload hash **before** executing custom Python. It also
checks stack versions and suppresses bytecode-cache writes. Merely calling
upstream `mlx_lm.load` does not perform these integrity checks. Keep artifacts
immutable and launch with `PYTHONDONTWRITEBYTECODE=1`.

## Evidence in this clone

All checks are synthetic, offline and serial. No full suite, study pipeline,
real measurement data, restricted directory or model checkpoint was read.

| Check | Result |
|---|---|
| BF16 mmap exact bits/no affine metadata; row encoding/gathering, EOS/chunk hashing and bounds | 4 PASS |
| Maxfit policies for every tiny/release tensor, bf16 shard streaming/spans, tiny HF conversion/dtypes, strict inventory and manifest tampering | 6 PASS |
| Component memory model, maxfit peaks/headroom and actual kit cap | 3 PASS |
| Official reference fp32 and bf16 prefill vs stepwise | 2 PASS |
| **MLX vs HF fp32/bf16 and forced QSA ties; mixed, maxfit and maxfit5 vs native bf16** | **6 SKIPPED: no MLX in selected sandbox interpreter; native Metal unavailable here** |

The gold fixture has 194,564 parameters, two layer types, short sparse QSA
budget overflow, EOS boundaries, nonzero PLE convolution and nonzero norm
weights. HF self-consistency max absolute error is 7.45058e-08 in fp32 and
0.0 in bf16. These values say nothing about the still-unrun MLX worker.

Prospective acceptance bounds: fp32 atol 2e-5 / rtol 2e-4; bf16 atol .004 /
rtol .02; mixed vs bf16 atol .04 / rtol .15 **and RMSE <= .012**;
**maxfit vs bf16 atol .008 / rtol .03 and RMSE <= .002**;
**maxfit5 vs bf16 atol .016 / rtol .06 and RMSE <= .004**. The maxfit workers
also check every non-expert weight's native bf16 dtype and bitwise equality
to baseline, packed expert dtypes/shapes and native module bits/groups,
bf16 scale/bias metadata, exhaustive artifact inventories and bf16 PLE disk
lengths. The MLX
worker checks full prefill and stepwise gold logits, internal chunk/step
parity, causality, left padding and cached continuation, attention trim and
re-prefill, native recurrent snapshot/restore, and quantized output. Any
failure must be investigated; these tolerances have not been empirically
validated on MLX and must not be silently widened.

Synthetic mmap evidence (warm files, separate fresh processes, 128 token
lookups, 16 rows/token; RSS is process high-water, not GPU residency):

| Table / mode | Peak RSS before → after (bytes) | Median / p95 lookup | Logical bytes/token |
|---|---:|---:|---:|
| 128 MiB bf16, dim 256, mmap | 38,617,088 → 70,270,976 | 44.646 / 55.342 µs | 8,192 |
| Same, eager mapped + copy | 36,028,416 → 307,101,696 | 7.334 / 9.142 µs | 8,192 |
| 32 MiB q4, dim 160, mmap | 38,600,704 → 62,390,272 | 68.126 / 161.798 µs | 1,408 |
| Same q4, eager copy, identical row decoder | 37,961,728 → 105,168,896 | 38.896 / 51.081 µs | 1,408 |

The older bf16 eager timing used direct gathering without deduplication;
the q4 comparison uses identical lookup/dequantization and equal checksums.
Creation warmed the files. Logical row bytes are not physical disk reads;
cold real-model latency and SSD traffic remain unmeasured.

## Target-Mac plan and release gates

1. **First run the tiny gold gate on a device-capable Mac**, with the exact
   pinned MLX interpreter and a separate Torch/Transformers interpreter:

   ```sh
   JW_QWEN_REF_PYTHON=/private/tmp/jwsol/venv-ref/bin/python \
   JW_QWEN_MLX_PYTHON=/private/tmp/jwsol/venv-mlx/bin/python \
   /private/tmp/jwsol/venv-ref/bin/python -B -m unittest tests.align.test_qwen4_exp_parity
   ```

   Required result: all eight tests pass, **zero skips**, with worker error
   logs retained. The environment-specific paths are examples from this
   session; use existing appropriate venvs on the target, without modifying
   the protected venvs. A fresh reviewer must audit implementation and tests
   before release; no independent review was run in this offline task.

   Also run `tests.align.test_qwen4_exp_qsa.TestNativeQSA` and
   `tests.align.test_qwen4_exp_precision` in the native MLX interpreter,
   serially. Require all nine native tests to pass without skips. The
   precision test prints single-op RMSE against matched-input fp64 oracles;
   retain those results, then repeat the real-layer comparison outside this
   blinded sandbox to quantify the actual gain.

2. Ed obtains the official HF bf16 checkpoint/tokenizer at an **immutable HF
   revision**, separately authorizing any network transfer. That revision is
   not supplied in this brief and remains to be resolved. Preserve full
   input hashes. Budget roughly 565 GB of disk plus margin for bf16 source and
   maxfit converted copies; do not attempt real conversion/inference on this 24 GB
   laptop. Download/conversion are preparation, never part of an energy run.

3. On the 128 GB target, in the pinned venv, convert a local mirror:

   ```sh
   python -B scripts/align_convert_qwen4_exp.py artifacts/qwen4-exp-hf artifacts/qwen4-exp-maxfit --profile maxfit --group-size 64 --ple-storage bf16
   ```

   Record the printed manifest SHA256, owned-module hashes, HF revision and
   checkpoint hashes in the lead's model provenance. Validate the manifest
   before loading. Also record the tokenizer and chat-template hashes. No
   config or artifact can change after admission without new pins/tests.
   If maxfit cannot pass the hardware gate, create a separate new artifact
   with `--profile maxfit5 --group-size 64 --ple-storage bf16` and repeat its
   gates; never substitute q4/q8 PLE or quantize non-expert weights.

4. Wire `prefill_step_size=64` through model-specific warmup and stream
   options, preserving anchor settings. Use batch 1 and the same 40,960-token
   consumed-context cap. Run the actual endpoint/prompt-cache lifecycle,
   including append, EOS, rewrite fallback and snapshot restoration, before
   selecting this artifact for ALIGN. The current default warmup needs this
   integration step; a successful standalone load is insufficient.

5. Check real-model English/code coherence and greedy repeatability using
   the official chat template. For NLL, freeze a non-study, public text
   fixture and token IDs, compare a few short windows against the official
   bf16 reference, and report mean/max logit errors, mean NLL and NLL delta.
   The whole 354+ GB bf16 model cannot fit on the 128 GB Mac: use a verified
   layer-wise CPU/disk-offload reference on short windows, or a separate
   sufficiently large reference host. Do not use a second quantization as
   the gold reference. Full-model maxfit/maxfit5 error/NLL acceptance must be
   agreed and recorded before campaign admission; the tiny random tolerance is not an
   empirical real-model quality bound.

6. Measure cold and warm PLE lookup latency/physical reads, prefill tok/s,
   decode tok/s, MLX peak allocated/cache memory, process RSS and total
   memory pressure. Exercise short prompts, chunked 40,960 context, and
   checkpoint/restore. Observe swap-used and swap-in/out counters throughout
   admission and the eventual measurement. File-backed page-ins are expected
   from PLE and are different from swap. Require zero swap use/activity and
   sufficient OS/monitor headroom; abort on swap or memory pressure. If
   reserve adequacy or quality fails, re-plan precision/chunking and re-pin;
   do not continue an energy measurement with swapping.

7. The lead owns the final real-model/peak-memory gate and a clean
   agent-free measurement window. Do not start quiet-Mac collection from an
   agent session. Cross-backend parity, real-model coherence/NLL, memory
   peak, SSD behavior, integration and tok/s are all **OPEN** here.

Implementation and exact focused-check results:
[maxfit run report](../run_reports/2026-11-05-align-flashnext-maxfit.md).
