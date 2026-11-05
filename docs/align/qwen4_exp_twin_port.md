# Qwen3.8-Flash-Next (`qwen4_exp`) MLX twin port

Status: **PROVISIONAL**. The port matches the official reference on a tiny
random model that exercises every layer type, in fp32 to ~6e-6 on logits of
magnitude ~4. **It has not been run on the released weights.** No real
checkpoint was downloaded or converted, and no M3 Max throughput or energy
number exists yet. The live gates are listed at the end.

Lane: `lane/2026-11-05-align-flashnext-twin`. Purpose: run the strongest open
model that fits a 128 GB M3 Max (Qwen3.8-Flash-Next: 125B MoE, 6B active,
plus a 51B n-gram embedding) on the pinned stack (mlx 0.31.2, mlx-lm 0.31.3)
for SHADE-Arena agent-monitoring energy measurements. The stack is not
bumped: mlx-lm loads the port through `config.json` `"model_file"`
(`mlx_lm/utils.py:325-331`).

## Files

| File | Role |
|---|---|
| `joulewise/align/models/qwen4_exp_twin.py` | The port: `Model`, `ModelArgs`, caches, the n-gram store, `sanitize()`. Self-contained, imports only numpy, mlx and mlx_lm, because the converter copies it into each converted model directory. |
| `scripts/align_convert_qwen4_exp_twin.py` | Streams an HF checkpoint to the twin format, with mixed precision, an off-GPU n-gram store and a sha256 manifest. |
| `tests/align/test_qwen4_exp_twin_parity.py` | Gold parity test: the official reference (venv-ref) vs the port (venv-mlx). |
| `scripts/align_qwen4_exp_twin_ngram_bench.py` | Resident memory and per-token latency of the n-gram table, on a scaled synthetic table. |
| `scripts/align_qwen4_exp_twin_memory.py` | Resident-memory model per component and scheme, plus state at 40,960 tokens. |

Authority: `.engine/transformers-qwen4_exp/modeling_qwen4_exp.py`. The
installed transformers 5.22.1 copy differs only cosmetically and in how eager
float masks are combined. The test uses SDPA boolean masks, where the two
copies agree bit for bit (asserted: max diff 0.0). The community MLX port was
not consulted.

## Design

**Residual stream.** The residual stream is `hc_count` (4) concatenated
copies of the hidden state (`mx.tile` of the embedding). Each branch reads
through `GatedResidual`: a grouped (1+w) RMSNorm, a low-rank sigmoid read
gate, and a stream mean. It writes `hyper + out ⊗ (2·sigmoid(inject/hc))`.
The final `hyper_connection_mixer` (no write gate) feeds `lm_head` directly.
There is no final norm, matching the reference.

**Gated DeltaNet (36 layers).** The causal depthwise conv uses a K-1 history
in the cache and accumulates in fp32, rounding once. Its silu then runs in
fp32 on that rounded output and rounds once, as torch's bf16 silu does
(`nn.silu` on bf16 rounds twice, which put the layer's bf16 error at
1.08-1.09x the reference's own bf16 noise instead of 1.005-1.007x). q and k get the
reference's fp32 `l2norm(eps=1e-6)` on the sum of squares, q is scaled by
Dk^-0.5, beta is `sigmoid(b)` in the model dtype, and
`g = -exp(A_log)·softplus(a + dt_bias)` is computed in fp32. The recurrence
uses mlx-lm's Metal `gated_delta_kernel` (fp32 state [B, Hv, Dv, Dk]) for both
prefill and decode. The exact ops recurrence (`gated_delta_ops`) runs on CPU,
and also on GPU whenever `linear_key_head_dim` is not a multiple of 32: the
kernel splits Dk over one 32-lane simdgroup, so Dk = 48 silently covered 32
of the 48 key dims and Dk < 32 does not compile. The release has Dk = 128.
The output gate is a norm-before-gate RMSNorm with `output_gate_type`
(sigmoid for the release).
Padding is handled as in the reference: inputs at padded positions are
zeroed, so state stays zero.

**QSA (12 layers).** The attention is gated GQA: `q_proj` emits
[query | gate] per head, q/k get (1+w) norms, partial RoPE (64 of 256 dims,
rotate-half), and the output is multiplied by `sigmoid(gate)`. The indexer
follows the reference:

- `index_qk_proj` → 4 query heads + 1 key head;
- q gets a norm, then RoPE at its own position;
- each block is the mean of 4 raw keys, then `k_layernorm`, then RoPE at the
  block's first position;
- `score = Σ_heads relu(q·k) / sqrt(128)`;
- select the top `budget/ratio` = 512 complete blocks, plus the incomplete
  tail.

Block keys are computed once, when a block completes, and kept in
`QSACache.blk_keys`. A block depends only on its own tokens and start
position, so this matches recomputing them every step, and trimming is exact.
When every query has at most 512 complete blocks (contexts up to 2,051
tokens), QSA reduces exactly to causal attention, and the port then skips
scoring.

**MoE.** The router softmax, top-10 and renormalisation run in fp32, as in
the reference. Stock mlx-lm Qwen MoE does this in bf16, which ties and flips
routes among 512 experts. Experts go through `SwitchGLU`, plus the sigmoid
`shared_expert_gate` × shared expert.

**PLE n-gram layer (decoder layer 2).** The hash ids are computed on the host
in exact int64: splitmix multipliers, 16 prime head vocabularies after 20M,
the EOS-reset shift rule, and XOR then mod then offset. Decode takes a
pure-int fast path, bit-identical over 40k EOS-heavy random trials. The
gathered rows feed the gated key/value projection and the dilated (×3)
depthwise short conv, whose 9-step history lives in the cache. The last two
token ids are kept in the cache as n-gram context.

**Off-GPU n-gram table.** `NgramTable` memory-maps one file per PLE layer of
fixed-size row records (`f32`, `bf16`, `q8` or `q4`; q8/q4 are affine with
fp16 scale and bias per 32-column group). A forward:

1. hashes the ids;
2. issues `MADV_WILLNEED` for the touched rows, so cold pages arrive
   concurrently;
3. gathers only those rows;
4. dequantizes them on the host;
5. hands a (B, S, 2560) array to MLX.

The table is never an MLX parameter. `io="pread"` (an `F_NOCACHE` fd) is
available when file-cache growth must be zero. The table counts major page
faults so a measurement bracket can disclose page-ins.

**Caches.**

- `QSACache(KVCache)` holds K/V, the raw indexer keys and the block keys.
  Positions are padding-aware (token `i` of a row padded by `p` sits at
  position `i - p`, the mlx-lm `BatchKVCache` convention), and `trim()` is
  exact.
- Linear layers use `ArraysCache`: [conv, recurrent], plus
  [ple_conv, ngram_ctx] on PLE layers.
- `Model.snapshot_cache` and `restore_cache` are zero-copy checkpoints,
  because MLX arrays are immutable and slots are rebound.
- `make_cache(left_padding=[...])` builds a left-padded batch.
- `generate_step` works unchanged, including chunked prefill.

**Query-chunked attention.** mlx 0.31.2 has no fused full-attention kernel for
head_dim 256 (measured: SDPA materialises ~H·S·L bf16 scores). Prefill
queries are processed in chunks of 512 rows. Rows are independent, so results
are unchanged (tested). This bounds the transient to ~1.06 GB at 40,960
context, whatever the prefill step.

**Converter.**

- It reads one source shard at a time and one tensor at a time. With
  `--hf-repo` it fetches each shard via the official `huggingface_hub`, and
  with `--delete-source-shards` it deletes each shard once consumed.
- Expert layouts: per-expert keys (as `save_pretrained` writes them) are
  quantized on arrival and stacked when a layer is complete. Fused
  `gate_up_proj` [E, 2I, H] (as in the released shards) is split. Both give
  bitwise-identical output (tested).
- N-gram `shard_K` parts are written at numeric offsets into the store. The
  checkpoint's I64 hash buffers are checked against the port's recomputation,
  then dropped.
- `--pins` refuses any shard whose sha256 does not match.
- Completeness gate: every port parameter must be present with the right
  shape, and every attention layer must have its indexer, or the run fails.
- `mx.quantize` is pinned to the CPU stream. mlx 0.31.2 rounds differently
  on CPU and GPU (reproduced here), so the device is part of artifact
  identity and is recorded in `twin_manifest.json`, alongside the sha256 of
  every output, the converter commit, the policy and per-category bytes.

**Default precision recipe.** Routed experts are affine 4-bit, group 64.
Embeddings, `lm_head`, attention q/k/v/o, DeltaNet qkv/z/out, the shared
expert, the hyper-connection read projections and the PLE key/value are
8-bit. These stay bf16:

- the router;
- the shared-expert gate;
- the whole QSA indexer;
- DeltaNet a/b;
- the hyper-connection write gates;
- all norms, convs, `A_log` and `dt_bias`.

They are small (~0.2 GB in total) and they make discrete selections. The QSA
indexer is never dropped. The n-gram table defaults to q8 (`--ngram-format`
q4 halves it).

## Deviations from the reference

1. **DeltaNet algorithm.** Prefill uses the recurrent kernel, where the
   reference uses its chunked algorithm. They are mathematically identical,
   with fp32-level differences (≤6e-6 here).
2. **QSA top-k ties.** These break toward the lowest block index, which is
   deterministic. `torch.topk` leaves tie order unspecified (lowest-first for
   small CPU inputs, not for large ones). Exact ties need every head's score
   to be ≤ 0 for several blocks at the boundary.
3. **Positions** are always padding-aware. They equal the reference under
   `generate()`, which derives positions from the attention mask. They differ
   from a bare reference `forward()` on a padded batch without `position_ids`.
4. **bf16 rounding points.** The port accumulates in fp32 and rounds once
   where the reference CPU kernels' accumulation is unspecified: depthwise
   convs, the expert weighted sum (the reference uses bf16 `index_add_` in
   expert order), the hyper-connection stream mean and the PLE gate dot
   product. (1+w) norms use the raw `w` in fp32. Unlike mlx-lm's qwen3_5,
   `1+w` is not folded into bf16 weights, which would round it to 2^-7.
   The DeltaNet and PLE conv activations evaluate silu in fp32 and round
   once, like torch. The other silu sites (hyper-connection read gate,
   shared expert, routed experts inside mlx-lm's `SwitchGLU`) still use
   `nn.silu` in the model dtype, which rounds after the sigmoid and after
   the multiply.
5. **Fully padded query rows** attend to themselves so they stay finite.
   Their outputs are discarded, as in the reference.
6. **N-gram table** lives off-GPU, optionally quantized (q8/q4). The
   reference keeps it as a bf16 `nn.Embedding`.
7. **Omitted:** MTP (the reference ignores `mtp.*`, so it does not change
   next-token logits), vision, `input_embeddings`, non-default RoPE (YaRN is
   refused, not approximated), KV-cache quantization, prompt-cache files, and
   mlx-lm `BatchGenerator` merge/filter.

## Test evidence

`python3 -m unittest tests.align.test_qwen4_exp_twin_parity`: **20 tests,
OK** (~50 s on the loaded M4 Air; ref stage peak RSS 377 MB, MLX stage
186 MB). The test skips when the venvs are absent or
`JW_SKIP_TWIN_PARITY=1`.

Tiny config: hidden 64, 8 layers (L L L QSA L L L QSA), PLE at layers 2 and
5 (two `ple_layer_index` values), 8 experts top-3, hc 4, and an indexer with
budget 8 / ratio 4 (top-2 blocks). On the 37-token prompt, 26 of 37 queries
are sparse and 392 block-token slots are excluded per layer. Every parameter
is randomised (norm offsets, PLE convs and n-gram rows included). The
checkpoint is `save_pretrained` into 112 shards, plus a fake `mtp.*` shard and
a fused-expert re-layout.

Max |Δlogit| (logit scale 3.5-4.3; per-row RMS and top-1 agreement are in the
summary JSON):

| Scenario | max abs | RMS | top-1 | Bound |
|---|---|---|---|---|
| fp32 full prefill vs reference | 5.72e-06 | 7.1e-07 | 1.000 | 2e-4 |
| fp32 cached stepwise decode (20 + 17) vs reference | 3.10e-06 | 5.4e-07 | 1.000 | 2e-4 |
| left-padded batch + 4 decode steps, row 0 / row 1 vs reference | 3.81e-06 / 3.93e-06 | 6e-07 | 1.000 | 2e-4 |
| batch-1 seq B + decode vs reference | 4.44e-06 | 5.7e-07 | 1.000 | 2e-4 |
| trimmed cache + re-prefill vs reference | 2.74e-06 | 4.9e-07 | 1.000 | 2e-4 |
| `mlx_lm.generate_step` greedy (prefill step 16): tokens / logprobs | 8/8 equal / 2.4e-06 | | | equal / 2e-4 |
| MLX prefill vs MLX stepwise | 2.47e-06 | 4.7e-07 | 1.000 | 1e-4 |
| batch-1 vs left-padded (MLX): sparse QSA path / dense path (short, + 2 decode steps) | 2.38e-06 / 1.19e-06 | 4.5e-07 | 1.000 | 1e-4 |
| KV trim + re-prefill vs fresh (same call split) | **0 (bitwise)** | 0 | 1.000 | exact |
| KV trim + re-prefill vs fresh single call | 1.85e-06 | 4.1e-07 | 1.000 | 1e-4 |
| DeltaNet snapshot/restore: logits, restored state, re-run state | **bitwise equal** | | | exact |
| query-chunked attention (chunk 5): sparse / dense / padded vs reference | 1.73e-06 / 1.01e-06 / 3.64e-06 | | 1.000 | 1e-4 / 1e-4 / 2e-4 |
| `sanitize()` on raw HF tensors vs converter output | bitwise equal (217 params) | | | exact |
| fused-expert vs per-expert checkpoint conversion | bitwise equal (445 tensors) | | | exact |
| reference: pinned copy vs installed transformers; reloads of both layouts | 0.0 | | | exact |
| *bf16 noise floor: reference bf16 vs reference fp32* | *2.87e-01* | *2.06e-02* | 1.000 | — |
| MLX bf16 vs reference fp32 (prefill = stepwise) | 8.80e-02 | 1.45e-02 | 1.000 | ≤ noise floor (max and RMS) |
| MLX bf16 vs reference bf16 (prefill / stepwise) | 2.70e-01 / 2.66e-01 | 2.4e-02 | 1.000 | ≤ 1.5 × floor |
| mixed quant (q4 experts, q8 dense, q8 n-gram) vs MLX bf16 | 3.79e-01 (rel 0.105) | 6.0e-02 | 0.973 | rel ≤ 0.15, top-1 ≥ 0.85 |
| quantization attribution: q4 experts / q8 dense / q8 n-gram / q4 n-gram only | 0.26 / 0.32 / 0.26 / 0.44 | 0.041 / 0.040 / 0.026 / 0.076 | 0.973 / 0.973 / 0.973 / 0.946 | informational |
| *sensitivity: reference with indexer made dense / n-gram table zeroed* | *0.431 / 3.68* | | 0.946 / 0.135 | ≫ fp32 bound |

How to read the table:

- The bf16 rows have no exact target. The reference's own bf16 run is 0.287
  from its fp32 run (a discrete jump at one position). The port's bf16 run is
  closer to fp32 than that, in both max and RMS. Most of the MLX-vs-reference
  bf16 disagreement is the reference's jump.
- The quantization rows use random tiny weights, which are chaotic: bf16
  alone moves logits by 0.29. They test plumbing and give relative
  attribution. **They predict nothing about real-model quality.**
- The sensitivity rows show what a missing indexer (0.43) or a missing PLE
  path (3.7) would cost. That is 2,000-18,000× the fp32 bound, so the fp32
  agreement is not vacuous.

Converter checks in the same run:

- the mixed recipe re-converted from a staged copy whose shards are deleted
  as they are consumed is byte-identical (sha256);
- every source shard passed pin verification, and a wrong pin aborts the run;
- the 1 `mtp.*` tensor was dropped;
- all 6 n-gram hash buffers matched the recomputation;
- 4-bit module count 24 and 8-bit 90, both exactly as the policy predicts.

## N-gram table: residency and latency (measured)

`scripts/align_qwen4_exp_twin_ngram_bench.py --rows 6000000 --format q4`. The
synthetic table uses the real row geometry (160 dims, 100-byte q4 records,
16 lookups per token with the real hash spec) at 1/53 of the real row count
(600 MB). It was written through `F_NOCACHE`, so the first mmap pass is cold.
2,048 decode tokens, then one 2,048-token prefill gather. **Machine: the
shared M4 Air, under heavy load (load average 13-35) and memory pressure.**
Treat latencies as upper bounds and RSS deltas as noisy: the OS reclaims the
process's clean pages, hence the negative deltas.

Host time per token is hash + gather/dequant + lazy `mx.array` creation. In
the model this array joins the step graph, so there is no extra GPU sync.

| Pass | mean µs | p50 | p99 | hash | gather+dequant | to mx | major faults/token | RSS ΔKB/token | MLX active Δ | 2,048-token prefill gather |
|---|---|---|---|---|---|---|---|---|---|---|
| pread + F_NOCACHE | 1,486 | 1,407 | 3,038 | 16 | 1,463 | 8 | 0.01 | (−59) | 5 KB | 1,399 ms |
| mmap, cold, no prefetch | 867 | 755 | 2,167 | 13 | 849 | 5 | 10.7 | 102 | 5 KB | 38 ms |
| mmap, warm (same tokens) | 56 | 54 | 119 | 13 | 38 | 5 | 0.00 | (−7) | 5 KB | 35 ms |
| **mmap, cold, WILLNEED prefetch (default)** | **310** | 276 | 798 | 13 | 292 | 5 | 10.7 | 170 | 5 KB | 36 ms |

Conclusions:

- MLX active memory grows by a constant 5 KB: the table is not GPU-resident.
- Warm lookups cost ~56 µs per token. Cold rows cost ~0.3 ms per token with
  prefetch, about 2.8× faster than serial faults.
- `pread` is a fallback only. It is too slow for prefill.
- File-cache growth for the real 32 GB q4 table is bounded by
  16 pages × 16 KiB = 256 KiB per token, i.e. ≤10.7 GB at 40,960 tokens.
  These are clean, reclaimable pages in unified memory, and less when
  n-grams repeat.

## Memory model (real config)

`scripts/align_qwen4_exp_twin_memory.py` (exact shapes from the port, the
converter's own policy, group 64, bf16 scales and biases). Its byte formulas
reproduce the converter manifests exactly: `--check-manifest` matches on the
fp32, bf16, mixed and experts-only tiny conversions. The text decoder has
125.74 B params; MTP and vision are excluded.

Weights (GB, decimal):

| Component | params (B) | bf16 | q8 | q6 | q4 | q3 | **mixed e4/d8** | mixed e3/d8 | mixed e3/d6 |
|---|---|---|---|---|---|---|---|---|---|
| routed experts | 120.796 | 241.59 | 128.35 | 98.15 | 67.95 | 52.85 | **67.95** | 52.85 | 52.85 |
| DeltaNet | 2.087 | 4.17 | 2.22 | 1.70 | 1.18 | 0.92 | **2.23** | 2.23 | 1.71 |
| hyper-connections | 0.641 | 1.28 | 0.68 | 0.52 | 0.36 | 0.28 | **0.69** | 0.69 | 0.53 |
| embed_tokens | 0.636 | 1.27 | 0.68 | 0.52 | 0.36 | 0.28 | **0.68** | 0.68 | 0.52 |
| lm_head | 0.636 | 1.27 | 0.68 | 0.52 | 0.36 | 0.28 | **0.68** | 0.68 | 0.52 |
| attention (q/k/v/o, norms) | 0.598 | 1.20 | 0.64 | 0.49 | 0.34 | 0.26 | **0.64** | 0.64 | 0.49 |
| shared experts | 0.236 | 0.47 | 0.25 | 0.19 | 0.13 | 0.10 | **0.25** | 0.25 | 0.19 |
| router | 0.063 | 0.13 | 0.07 | 0.05 | 0.04 | 0.03 | **0.13** | 0.13 | 0.13 |
| PLE dense | 0.033 | 0.07 | 0.03 | 0.03 | 0.02 | 0.01 | **0.03** | 0.03 | 0.03 |
| QSA indexer | 0.020 | 0.04 | 0.02 | 0.02 | 0.01 | 0.01 | **0.04** | 0.04 | 0.04 |
| **weights** | 125.74 | 251.49 | 133.61 | 102.17 | 70.73 | 55.02 | **73.30** | 58.20 | 56.98 |

State at 40,960 tokens (batch 1):

| State | GB |
|---|---|
| KV (bf16) | 1.007 |
| QSA raw indexer keys | 0.126 |
| QSA block keys | 0.031 |
| DeltaNet recurrent (fp32) | 0.113 |
| DeltaNet conv | 0.002 |
| PLE conv + context | 0.0002 |
| **Total** | **1.28** |

Estimated prefill transient peak (prefill step 2,048, query chunk 512):

| Transient | GB |
|---|---|
| SDPA fallback scores | 1.06 |
| QSA scores and masks | 0.67 |
| hidden streams | 0.34 |
| MoE activations | 0.31 |
| **Total** | **~2.37** |

The transient figure is an estimate, not a measurement.

| Scheme | resident estimate | vs 80 GB |
|---|---|---|
| bf16 | 255.15 GB | over |
| uniform q8 | 137.26 GB | over |
| uniform q6 | 105.83 GB | over |
| uniform q4 | 74.39 GB | fits |
| uniform q3 | 58.67 GB | fits |
| **mixed e4/d8 (default)** | **76.95 GB (71.67 GiB)** | **fits, ~3 GB margin** |
| mixed e3/d8 | 61.85 GB | fits |
| mixed e3/d6 | 60.64 GB | fits |

N-gram table on disk, never MLX-resident:

| Format | GB |
|---|---|
| bf16 | 102.40 |
| q8 | 57.60 |
| q4 | 32.00 |

These byte totals agree with the lane's independent weights plan
(`docs/align/flashnext_weights_plan.md`, not part of this change): a 73.21 GB
core with its slightly different 8-bit set, and a 57.6 / 32.0 GB table.

## Limitations and open issues

1. **Not validated on the released weights.** Before any measurement:
   - convert with `--pins` and `--hash-sources`;
   - load;
   - check greedy-generation sanity;
   - compare perplexity on a fixed corpus against a reference runtime
     (transformers or vLLM on a GPU host) for the chosen recipe.

   The tiny test cannot detect quality loss from quantization.
2. **Disk does not fit.** The core is 73.3 GB, plus the table (32.0 GB at q4,
   57.6 GB at q8), against ~82 GB free on the measurement Mac (and its
   40 GiB floor). Options:
   - convert on and run from an external SSD (`--ngram-dir` can place the
     table there);
   - or free roughly 25-60 GB plus the floor.

   The lane plan reaches the same conclusion.
3. **Memory margin is thin.** The resident estimate is 76.95 GB against an
   80 GB target. The MLX buffer cache can hold freed buffers above the
   active figure, so set `mx.set_cache_limit` and check `mx.get_peak_memory`
   on the first real run. The n-gram file cache (≤10.7 GB at 40,960 tokens,
   reclaimable) shares unified memory. 3-bit experts (61.9 GB) are the
   fallback, at unknown quality cost.
4. **Host sync per forward.** The n-gram rows depend on the token ids just
   fed, so each step waits for the previous token before building its graph.
   This loses mlx-lm's async overlap of graph construction with GPU work.
   Host gather cost is ~56 µs per token warm and ~0.3 ms cold. The
   graph-build stall at real scale is unmeasured.
5. **Page-ins inside measurement brackets** are an energy/latency hazard.
   `NgramTable.major_faults` exposes them per table. The harness should
   record and disclose them, or prewarm deliberately and register that.
6. **head_dim-256 SDPA is unfused in mlx 0.31.2.** Prefill is slower and
   draws more energy than a fused kernel would. Decode uses the vector
   kernel. This is an artifact of the pinned MLX version; disclose it with
   prefill energy numbers.
7. **Prompt-cache reuse.** The DeltaNet `ArraysCache` is not trimmable, so
   `EpisodePromptCache` takes its `untrimmable_rewrite` fallback (a full
   rebuild) on any history divergence, like other hybrid models.
   `snapshot_cache` / `restore_cache` could make rewinds exact but are not
   wired into the harness.
8. **Route A (Qwen's FP8 n-gram bytes verbatim) is not implemented.** The
   converter encodes the bf16 n-gram parts to f32/bf16/q8/q4 only.
9. **QSA tie-break.** Exact score ties at the top-512 boundary follow the
   lowest-index rule, which the reference does not specify.
10. **Unsupported:** MTP / speculative decoding, vision, YaRN or other RoPE
    scaling, KV quantization, prompt-cache files, mlx-lm batch generation.
11. **CPU-pinned quantization makes artifacts host-specific.** A conversion
    on another Mac should be checked bitwise against a reference conversion
    of one shard before its outputs are trusted.

## How to run

```bash
# parity (needs venv-ref + venv-mlx; ~1 min, <0.4 GB per stage)
TMPDIR=/private/tmp/jwtwin-tmp nice -n 10 python3 -m unittest tests.align.test_qwen4_exp_twin_parity -v
# keep the work dir and its summary.json: JW_TWIN_KEEP=1

# conversion (measurement Mac; staging and output on a volume with room)
HF_HOME=/Volumes/X/hf HF_XET_CACHE=/Volumes/X/xet TMPDIR=/Volumes/X/tmp \
  venv-mlx/bin/python scripts/align_convert_qwen4_exp_twin.py \
  --hf-repo Qwen/Qwen3.8-Flash-Next --revision <40-hex> --src /Volumes/X/staging \
  --out /Volumes/X/flashnext-twin --expert-bits 4 --dense-bits 8 --ngram-format q4 \
  --delete-source-shards --pins <pins.json> --pins-repo bf16

# memory model / n-gram bench
venv-mlx/bin/python scripts/align_qwen4_exp_twin_memory.py --context 40960
venv-mlx/bin/python scripts/align_qwen4_exp_twin_ngram_bench.py --dir /private/tmp/jwtwin-tmp/ngram_bench
```
