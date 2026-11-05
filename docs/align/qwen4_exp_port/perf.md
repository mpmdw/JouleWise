# qwen4_exp port: performance (GOAL item 8, phase P5)

Date: 2026-11-05. Branch: `lane/2026-11-05-qwen4exp-port-perf`. This covers
the kernels, the targets, the critical path, and the measurement plan for the
128 GB M3 Max measurement Mac.

Code:

- `joulewise/align/models/qwen4_exp_kernels.py` holds the reusable kernels. It
  imports only `mlx` and `mlx_lm`, so the canonical module can vendor it.
- `joulewise/align/models/qwen4_exp_kernel_bench.py` holds the per-layer
  microbenchmarks at real dims, plus a full-depth synthetic model.
- `tests/align/test_qwen4_exp_kernels.py` checks every fast path against a
  literal pure-MLX reference (27 tests).
- `scripts/qwen4_exp_kernels_torch_check.py` cross-checks real-dim layers
  against the official transformers reference.
- `perf_m4_2026-11-05/*.json` holds the raw results behind every number below.

Authority is transformers 5.22.1 `models/qwen4_exp`. `HF:<line>` cites
`.engine/transformers-qwen4_exp/modeling_qwen4_exp.py`.

> **Measurement caveat.** All numbers come from the M4 MacBook Air (10-core
> GPU, 24 GB). It was running a long CPU analysis job the whole time (load
> average 30-40, CPU 100%), and it is passively cooled. Streaming bandwidth
> varied from 44 to 85 GB/s during the session (spec: 120). Medians are
> therefore pessimistic and noisy, and p10 is often 20-40% lower. Every M3 Max
> number is an extrapolation (§6) until the Mac plan (§9) runs.

## 1. Answers in brief

| Question | Answer |
|---|---|
| Can the Gated DeltaNet use mlx-lm's Metal kernel? | **Yes, unchanged. Only the call site needs an adapter.** The recurrence is identical. The callers in `qwen3_next.py` / `qwen3_5.py` use an l2norm eps of 1.28e-4 instead of 1e-6. They compute the gates in bf16 and use a silu gate. qwen4_exp needs eps 1e-6 (via `rms_norm` eps = 1e-6/Dk, an exact identity), fp32 gates, and a sigmoid gate (§2). |
| QSA indexer | Block keys are cached once per completed block (exact). Decode-time scoring touches only the cached block keys. There is a dense fast path at kv <= 2051. **New Metal kernel:** block-sparse prefill attention, O(L x 2051) instead of O(L x T). It is 3.4x faster than dense-masked SDPA at 16K and keeps the cost flat to 40K (§3). |
| MoE | `gather_qmm` with a fused gate_up [E, 2I, H], as HF stores it, so 2 gathers per token. The shared expert can be folded in as expert 512 when it has the same bits. Mixed 3/4-bit is free per projection or layer, but not per expert. Ranking must use fp32 probabilities: mlx-lm ranks bf16 probabilities. Router cost is negligible (§4). |
| Biggest decode cost | Weight bandwidth: 5.80 GB/token at the e3_ple4_other8 recipe, of which the *dense* GDN projections are 38%. Second is ~4100 kernel dispatches/token (§6, §8). |
| Biggest prefill cost | MoE `gather_qmm` at ~10 rows per expert per 512-token chunk (59% of a chunk). A 2048-token chunk halves its per-token cost. At long context, QSA attention dominated until the sparse kernel (§8). |
| M3 Max targets | Decode **>= 30 tok/s** (stretch 40, bandwidth floor 52). Prefill **>= 400 tok/s** with 512-token chunks, **>= 550 tok/s** with 2048 (§7). |

## 2. Gated DeltaNet: reuse `mlx_lm.models.gated_delta.gated_delta_kernel`

**Math (HF:245-248, 403-448, 570-602).** For each value head h, token t,
and S in [Dk, Dv]:

```
q, k  <- x * rsqrt(sum(x^2) + 1e-6)          (fp32; use_qk_l2norm_in_kernel=True)
q     <- q / sqrt(Dk)
g      = -exp(A_log) * softplus(a.float() + dt_bias)    (fp32 log-decay)
beta   = sigmoid(b)                                     (model dtype, then fp32)
S      = S * exp(g);  S = S + k (x) ((v - S^T k) * beta);  y = S^T q
```

GQA: v-head h reads k-head `h // (Hv/Hk)` (`repeat_interleave`, 48/16 = 3).
HF runs `torch_chunk_gated_delta_rule` for prefill and the recurrent rule for
decode. They are mathematically identical (the chunked form is the exact WY
rewrite).

**mlx-lm 0.31.3 kernel.** It runs exactly this per-step recurrence. S is
stored as [Dv, Dk] and the multiplicative decay is exp(g). Its GQA index is
`hv / (Hv/Hk)`, which is `repeat_interleave`. The real dims qualify:
Dk = 128 is divisible by 32, and Dv = 128 by 4. So the kernel itself is
reused unchanged. Three call-site differences need the adapter
(`gated_delta()`):

1. **l2norm eps.** The qwen3_next/3_5 callers compute
   `Dk**-1 * rms_norm(q, eps=1e-6)`, which equals
   `q * rsqrt(sum q^2 + Dk*1e-6) / sqrt(Dk)`. The effective eps is
   **1.28e-4**, not 1e-6. With rms_norm eps = `1e-6/Dk` the identity
   `Dk**-0.5 * rms_norm(x, eps/Dk) = x * rsqrt(sum x^2 + eps)` is exact
   (`gdn_qk_normalize`). It matters: on the real-dim layer cross-check, the
   mlx-lm normalization gives 2.8e-5 error against HF, and the adapter gives
   5.5e-6. With small-norm keys the error exceeds 1e-2
   (`test_native_mlx_lm_normalization_is_not_hf`).
2. **Precision.** HF computes `softplus(a.float() + dt_bias)` and feeds fp32
   q/k into the recurrence. mlx-lm adds `a + dt_bias` in bf16 and feeds bf16
   q/k. The adapter casts first. The kernel then emits fp32 y, which is cast
   to the model dtype as HF does. Measured cost of fp32 q/k: none (7.9 vs
   8.2 ms per 512 tokens; 0.164 vs 0.157 ms per decode step).
3. **Gated norm** (`Qwen4ExpTextRMSNormGated`). `output_gate_type` is
   `"sigmoid"`, so the gate is `sigmoid(z)`, not silu. The weight is plain
   (not 1+w), applied as `w * norm(x).to(dtype)` (`rms_norm_gated`).

Also: the state layout is [B, Hv, Dv, Dk]. HF's is the transpose
(`gdn_state_to_hf`). Snapshots compared against the reference need the
transpose. For padding, mlx-lm's masked kernel leaves the state unchanged on
masked steps. HF zeroes the inputs, so k = v = 0, and the state decays by
exp(g). These are identical for left padding from a zero state, the only
case generation produces (`test_left_padding_mask`).

**Conv.** The causal depthwise width-4 conv uses `mx.conv1d(groups=C)`. In
bf16 it is bit-identical to the fp32 sum of the 4 products rounded once
(tested), and it beats 4 shifted FMAs: 0.024 vs 0.096 ms decode, 1.8 vs
7.4 ms per 512 tokens.

**Validation against the official reference**
(`scripts/qwen4_exp_kernels_torch_check.py`, fp32): a whole
`Qwen4ExpTextGatedDeltaNet` at real dims (hidden 2560, 16/48 heads) runs
through the HF chunked path against the kernel composition, with
max|diff| = 5.5e-6 (scale 1.6). The HF recurrent rule with an initial state
matches to 1.1e-8 (y) and 1.8e-7 (state).

**Is a new kernel needed?** Not for correctness. For speed: the kernel
processes T sequentially per threadgroup and is latency-bound (7.9 ms per
512 tokens per layer on the M4, about 20% of a GDN layer's prefill). A
pure-MLX chunked (WY, Neumann-doubling inverse) prototype agreed to 4e-8 but
was 1.5-2.5x *slower* (11.7 vs 7.9 ms at 512, 51 vs 21 ms at 2048) and used
far more memory. So the mlx-lm kernel stays. A register-blocked prefill
variant is optional future work (§10).

M4 layer timings (8-bit projections): decode 0.98 ms/layer (p10 0.89), and
39.6 ms per 512-token chunk (p10 31.7). `mx.compile` on the whole decode
layer body cut it 26% (1.17 to 0.86 ms) with bitwise-identical output.

## 3. QSA: indexer, cache layout, decode scoring, sparse attention

**Semantics (HF:663-765), for an unpadded row.** The indexer projects
hidden to 4 query heads plus 1 shared key head, both of dim 128.

- q gets `q_layernorm` (1+w) and RoPE over its first 64 dims at its own
  position.
- Raw keys are cached *un-normalized and un-roped*.
- For a query at p, `nvis = (p+1)//4` complete blocks are visible. Block j's
  key is `RoPE_{pos=4j}(k_layernorm(mean_fp32(raw[4j:4j+4])))`.
- The score is `s_j = sum_h relu(q_h . kb_j) / sqrt(128)`.
- Selected: the tokens of the top-min(512, nvis) blocks, plus the always-kept
  tail `4*nvis..p`.
- The mask is ANDed with causal and drives full GQA attention
  (24 q / 2 kv heads, dim 256, sigmoid output gate).

**Facts the fast paths use (all exact):**

1. Block key j depends only on its 4 raw keys and on position 4j. It is
   computed **once**, when block j completes, and cached. HF recomputes every
   block key for every query.
2. If nvis <= 512, everything visible is selected. So for kv length
   <= 4*(512+1)-1 = **2051** the mask is plain causal and scoring is
   skipped.
3. RoPE at positions 4*(offset+i) is `mx.fast.rope(scale=4, offset=offset)`.
   It is exact in fp32 for positions < 2^24.

**Cache layout (`QSAIndexerCache`, per QSA layer).**

- Raw keys are [B, T, 128] in the model dtype, as HF's `update_indexer`
  caches them. They are needed for the open tail block and for `trim`.
- Block keys are [B, T//4, 128]. Both buffers grow in 1024-token steps.
- `trim(n)` drops whole and partial blocks. The partial block reopens as the
  tail, and its key is recomputed on completion
  (`test_incremental_cache_matches_one_shot_and_trims`).
- Memory at 40,960 tokens: raw 10.5 MB plus blocks 2.6 MB per layer, so
  157 MB for 12 layers. The cache is required anyway, for trim and the tail.

**Decode-time incremental scoring.**

- Each step appends 1 raw key. Every 4th step, 1 block key is computed.
- The step then scores q (4x128) against all nvis cached block keys: one
  fp32 matmul, relu, and a head sum. Then `argpartition` picks the top 512.
- This is O(nvis) per step and cannot be made incremental, because q changes
  every step. It is cheap: 0.07-0.2 ms on the M4 for 2048-32768 blocks,
  dominated by dispatch.
- Attention then runs over only the selected 2048+tail rows. The rows are
  gathered by token index straight from the cache buffer (no copy of the
  cache), then go through `mx.fast.scaled_dot_product_attention` (the vector
  kernel supports D = 256).
- M4 decode attention per layer:

| context | dense full (not QSA semantics) | QSA dense SDPA + mask | QSA gather + SDPA |
|---:|---:|---:|---:|
| 4,096 | 0.24 | 0.37 | 0.49 |
| 8,192 | 0.41 | 0.51 | 0.48 |
| 16,384 | 0.96 | 1.12 (p10 0.57) | 0.47 |
| 32,768 | 1.81 | 0.98 | 0.54 |
| 40,960 | 2.67 | 1.36 | 0.60 |

  Policy (`qsa_decode_attention`): dense causal at <= 2051, mask + SDPA
  below `QSA_SPARSE_DECODE_MIN_KV` = 8192, gather above. All three compute
  the same function (`test_decode_attention_paths_agree`). On the M3 Max the
  crossover should move up because of its higher bandwidth. Re-measure.

**Prefill: why a new Metal kernel.**

- MLX 0.31.2 has **no fused prefill SDPA for head_dim 256**. It materializes
  [B, 24, L, T] scores: 200 MB for L = 512 at 8K, and >2 GB per layer at the
  40K cap.
- Dense SDPA under the QSA mask costs O(L x T): 23 / 63 / 136 ms per
  512-query chunk at 4K / 8K / 16K, about 400 ms at 40K (extrapolated).
- QSA only needs O(L x 2051).
- `qsa_sparse_attention` is a `mx.fast.metal_kernel` that takes per-query
  token lists ([B, L, 2051] int32, -1 = unused) built from the block top-k
  (`qsa_select_token_indices`). No [L, T] mask is built.
- Layout: one threadgroup per (query, kv head). Each of its 3 simdgroups owns
  4 of the 12 query heads that share that kv head, so every K/V row is
  fetched once into L1.
- Scores are lane-per-token: a lane computes a full 256-dim dot with q from
  threadgroup memory, so there is no per-token `simd_sum`. Online softmax
  runs per 32-token tile. P.V is lane-per-8-dims, with p broadcast by
  `simd_shuffle`. Accumulation is fp32.
- The kernel reads only the indexed rows of the whole preallocated KV buffer.
  A contiguous buffer avoids `metal_kernel`'s copy of a strided slice.

| 512-query chunk ending at | dense SDPA + mask | **sparse kernel** | token selection (indices) |
|---:|---:|---:|---:|
| 4,096 | 23.0 ms | 27.8 ms | 6.2 ms |
| 8,192 | 63.2 | **40.3** | 12.7 |
| 16,384 | 136.1 | **40.5** | 11.1 |
| 32,768 | (~270, memory-capped) | **33.7** | 18.4 |
| 40,960 | (~400) | **34.3** | 13.7 |

Policy (`qsa_prefill_attention`): causal SDPA at <= 2051, mask + SDPA below
`QSA_SPARSE_PREFILL_MIN_KV` = 6144, the kernel above. Whole QSA layer, M4,
8-bit, per 512-token chunk: 39.7 ms at 2K, 66 at 8K, 71 at 16K, 76 at 32K,
81 at 40K. Before the kernel it was 139 ms at 8K and 225 ms at 16K. Kernel
efficiency is about 0.7 TFLOPS, roughly 30% of this M4's bf16 GEMM. An
MMA version that uses the 12 GQA heads as the M dimension is the next step
(§10). At L = 1 the kernel lacks parallelism (2 ms), so decode keeps gather
+ SDPA.

**Validation.** On random inputs, every path matches a literal per-query
transcription of HF's loop (`qsa_reference_mask`) up to top-k ties. The sparse
kernel matches SDPA under the same mask to 2e-5 in fp32 (`test_sparse_*`).
Against the official `Qwen4ExpTextQSAIndexer` at real indexer dims (hidden
2560, budget lowered to 64 so T = 160 is sparse), the mask agrees except for
**8 entries, all on blocks whose score equals the K-th score exactly**.

**Top-k ties are a real parity hazard.** relu makes s_j = 0 whenever all 4
head dot products are negative. When fewer than K blocks score > 0, the K-th
score is 0 and the zero-score blocks tie. `torch.topk` on CPU picks among them
in an implementation-defined order, which is neither lowest nor highest index
(probed). `mx.argpartition` also picks arbitrarily. Exact mask parity is
therefore impossible there, so tests compare modulo exact ties, and the
real-weight parity run must log the tie rate.

## 4. MoE: 512 experts, 10 routed + 1 shared

**Router (HF:947-965).** `logits = x W^T` in the model dtype, then softmax in
**fp32**, top-10 of the fp32 probabilities, renormalize, and cast. mlx-lm's
`Qwen3NextSparseMoeBlock` calls `mx.softmax(bf16, precise=True)`. That
*returns bf16* probabilities and ranks those. Among 512 experts, bf16 rounding
collapses distinct probabilities into ties, which reorders near-equal experts
(`test_router_ranks_fp32_probabilities`). `moe_router` ranks fp32. The router
weights are concatenated with `shared_expert_gate` (513 rows), so one matmul
serves both. Router cost: 0.028 ms/token in decode, 1.2-2.7 ms per 512-token
chunk; 126 MB/token bf16 over 48 layers (2.2% of decode bytes). Quantizing it
is not worth the risk.

**Experts.** HF stores `gate_up_proj` [512, 1280, 2560] fused (gate rows
first) and `down_proj` [512, 2560, 640]. `FusedSwitchGLU` keeps the fusion:
one `gather_qmm` for gate+up and one for down, against mlx-lm's 3. The
sorted path is used when there are >= 64 (token, expert) picks.
`fold_shared_expert` appends the shared expert, whose intermediate is also
640, as expert 512. 10+1 experts then run in the same 2 calls, weighted by
`sigmoid(shared_expert_gate)`.

| M4, per layer, 3-bit experts | decode (ms, p10) | 512-token chunk (ms, p10) |
|---|---:|---:|
| split3 (mlx-lm SwitchGLU) + separate shared MLP | 0.51 (0.49) | 86.6 (63.3) |
| fused gate_up + separate shared MLP | 0.60 (0.56) | 85.1 (72.7) |
| fused gate_up + shared folded | 0.91 (0.47) | 78.9 (62.3) |

Differences between variants are within this machine's noise. The fused and
folded form has the fewest dispatches (22 against 26 per decode step), so it
is the default. Use split when the shared expert is kept at different bits.

**Mixed 3/4-bit.** `gather_qmm` takes one `bits` value per call. So mixing
per *projection* (e.g. gate_up 3-bit and down 4-bit) or per *layer* costs
nothing. M4 decode step, p10 across the three variants: 3/3 0.47-0.56 ms,
4/4 0.54-0.57 ms, 3/4 0.50-0.53 ms. Decode bytes per token per layer: 26.3 / 33.0 / 28.5 MB.
Mixing *per expert* (hot experts at 4-bit) needs two gathers with
partitioned indices, which costs a second dispatch pair per layer. Not
recommended.

**Prefill scales with chunk length.** Tokens per expert = chunk x 10 / 512,
which is ~10 at chunk 512. The gather_qmm then runs at ~0.7 TFLOPS against
2.0 for a dense qmm. Measured per-token cost (fused and folded, 3-bit):

| chunk | 64 | 256 | 512 | 1024 | 2048 |
|---|---:|---:|---:|---:|---:|
| µs/token/layer | 282 | 191 | 198 | 129 | 111 (p10 92) |

Validation: fp32 against a dense per-token loop (sorted and unsorted paths,
quantized 4/4, 3/3, 3/4 against the dequantized reference), < 1e-4. Against
the official `Qwen4ExpTextSparseMoeBlock` (64 experts, top-10, shared), the
split form is 1.1e-5 off and the folded form 1.2e-5 (scale 3.7).

## 5. Other per-layer costs (M4, 8-bit)

- **Hyper-connections.** There are 2 per layer, so 96 per token. Each is a
  grouped norm, 10240->320->10240, sigmoid, a mix, and a 4-way inject.
  Decode costs 0.23 ms (p10 0.16) for only 7 MB of weights: it is
  dispatch-bound (18 dispatches). A 512-token chunk costs 8.2 ms. Over 96
  per token that adds up to ~12% of decode bytes and as much again in
  overhead.
- **lm_head.** 248,320 x 2560 costs 8.4 ms at 8-bit (675 MB) and 7.2 ms
  (p10 4.6) at 4-bit. In prefill only the last position needs it, and
  mlx-lm's prefill never evaluates chunk logits.
- **Dispatch overhead** was 7.9 µs per tiny op on this loaded M4. A decode
  step has ~4100 dispatches: GDN 23, QSA 39, HC 18 x 2, MoE 22 per layer.
  These were counted from the graph with `mx.export_to_dot`.

## 6. Whole model: bytes, measurement, M3 Max extrapolation

**Decode bytes per token (from the config).** Affine quantization stores a
bf16 scale and bias per group of 64, so it costs bits/8 + 1/16 bytes per
param. The model has 6.66 B active params/token including lm_head (the card
says 6B, excluding it).

| e3_ple4_other8 (feasibility candidate) | GB/token | share |
|---|---:|---:|
| GDN projections (36 layers, 57.9M each, 8-bit) | 2.215 | 38.2% |
| routed experts (48 x 10 x 4.92M, 3-bit) | 1.032 | 17.8% |
| hyper-connections (97 x 6.6M, 8-bit) | 0.683 | 11.8% |
| lm_head (636M, 8-bit) | 0.675 | 11.6% |
| QSA projections (12 x 51.4M, 8-bit) | 0.656 | 11.3% |
| GDN recurrent state read+write (fp32) | 0.226 | 3.9% |
| router (bf16) | 0.126 | 2.2% |
| shared expert (3-bit) | 0.103 | 1.8% |
| QSA KV reads (sparse, <= 2051 tokens) | 0.050 | 0.9% |
| PLE projections and n-gram rows | 0.035 | 0.6% |
| **total** | **5.803** | |

Other recipes: e3/other-6 is 4.80 GB, e3/other-4 3.80, e4/other-8 6.13, and
uniform 4-bit 4.12 GB/token. **The bits of the dense "other" matrices, not the
experts', set decode speed.**

**M4 full-depth synthetic model.** This is 48 layers in the real pattern,
with real per-layer dims and bits (8-bit other, 3-bit folded experts) and one
weight set per layer type. Every layer has its own caches, and the weights of
each layer exceed the GPU caches.

| | M4 result |
|---|---|
| decode, context 1K / 8K / 16K | 111 / 139 / 145 ms/token median, p10 93 / 84 / 97 (excl. lm_head 8.4 ms) |
| prefill, chunk 512 from empty | 4.88 s, **105 tok/s** |

Breakdown from the per-layer numbers: MoE ~59%, GDN ~22%, HC ~12%, QSA ~7%.
Decode is bandwidth-dominated: 5.04 GB/token of synthetic weights and state
at the ~50 GB/s this machine sustained at that time.

**Extrapolation to the M3 Max** (40-core GPU, 128 GB, 400 GB/s spec,
14.2 TFLOPS fp32 peak). Assumptions:

- (a) Bandwidth-bound parts reach 75% of spec, which is 300 GB/s.
- (b) Compute-bound parts reach ~70% of peak, about 10 TFLOPS. Against the
  2.4-2.7 TFLOPS bf16 GEMM measured here, that is about 4.1x.
- (c) Dispatch costs ~3-4 µs/op on an unloaded M3 Max P-core, against
  ~8 µs here under load. MLX encodes token t+1 while the GPU runs token t,
  so most of it overlaps.
- (d) There is no swapping, and expert/weight placement is as resident
  (GOAL item 6).

| | bound | estimate |
|---|---|---|
| decode, e3_ple4_other8, <= 16K | bandwidth floor 19.3 ms (52 tok/s); plus 4-8 ms GPU launch gaps; CPU encode 12-16 ms (overlapped) | **25-33 ms, 30-40 tok/s** |
| decode, e3/other-6 | floor 16.0 ms (62 tok/s) | 35-45 tok/s |
| prefill, chunk 512 | weight-FLOP ceiling 750 tok/s (13.3 GFLOP/token) | 105 x 4.1 = **~430 tok/s** |
| prefill, chunk 2048 | MoE 1.8x per token, at 59% of the time | **~580 tok/s** |
| prefill at 32-40K context | the QSA layer adds ~40 ms per chunk (M4) with the sparse kernel | **~390 tok/s**; without the kernel, ~2x slower |

## 7. Targets (P5): batch 1, e3_ple4_other8, M3 Max, quiet, no swap

| metric | floor (bound) | **target** (P5 acceptance) | stretch |
|---|---:|---:|---:|
| decode tok/s, context <= 8K | 52 | **30** | 40 |
| decode tok/s, context 32-40K | ~50 | **27** | 36 |
| prefill tok/s, first turn (chunk 512) | 750 | **400** | 500 |
| prefill tok/s, chunk 2048 | 750 | **550** | 650 |
| prefill tok/s for a turn's new tokens at 32-40K offset | | **350** | 450 |
| TTFT, 8K-token prompt (chunk 2048) | | **<= 15 s** | 12 s |

**Per `reasoning_effort` (low / medium / xhigh).** Effort changes the number
of generated tokens, and therefore the context during decode. It does not
change the per-token work. With QSA sparse decode, per-token attention cost
is nearly flat beyond 8K. So the decode target applies at each effort at its
own context mix: low and medium mostly fall in the <= 8K row, and xhigh
reaches the 32-40K row. Record, per effort:

- prompt tok/s and TTFT
- decode tok/s, both overall and per 8K context bucket
- tokens generated and the final context
- peak memory and swap (must be 0)

A run passes if every bucket meets its row.

## 8. Critical path

**Decode** (~25-33 ms/token estimated):

1. **Weight bandwidth, 5.8 GB/token.** The levers are the "other" bits
   (8 to 6 saves 1.0 GB, ~17%) and lm_head bits. Both are quality-gated
   (GOAL items 6 and 7).
2. **Dispatch count, ~4100/token.** The levers:
   - `mx.compile` on per-layer bodies: -26% on GDN decode, bitwise-identical.
   - Projection fusion, already in the benches: GDN qkv|z|b|a as one qmm, QSA
     q|gate|k|v as one, router|shared-gate as one, and the folded shared
     expert.
   - A fused hyper-connection kernel. HC is 96 small dispatch-bound blocks
     per token.
3. QSA decode attention stays ~0.5-0.6 ms/layer (M4) to 40K via gather.

**Prefill** (~1.2 s per 512-token chunk estimated):

1. **MoE `gather_qmm`** (59%): ~10 rows/expert at chunk 512. Use chunk 2048,
   or 4096 if memory allows. Beyond that, a better small-M `gather_qmm` is
   MLX upstream work.
2. **GDN** (22%): projections plus the latency-bound recurrence (~20% of the
   layer).
3. **QSA at long context.** It was dominant (dense O(L x T)); it is now
   bounded by the sparse kernel. The next targets are the kernel's efficiency
   (MMA) and the indexer selection (13-18 ms per chunk-layer at 32-40K on the
   M4).

**Port integration (the real critical path to measuring any of this).** The
canonical module (P3) must call these kernels: the GDN adapter, `QSAIndexerCache`,
`qsa_prefill_attention` / `qsa_decode_attention`, and the fused and folded
MoE. Its cache must expose the full KV buffer to the sparse kernel.

## 9. Measurement plan on the Mac

The Mac is not an energy measurement here. Never run during a `[QUIET-MAC]`
window or while measurement sessions are active, and keep a no-swap check.

1. **Calibrate and microbenchmark** (about 10 min; no model weights):
   `python -m joulewise.align.models.qwen4_exp_kernel_bench --suite all --iters 15 --mem-gb 24 --json mac_<date>.json`.
   It records GEMM/qmm TFLOPS, streaming GB/s, dispatch µs, compile gain, MoE
   chunk scaling, and every per-layer table above. This replaces §6's
   assumptions with measured factors.
2. **Set the thresholds** from the crossovers: `QSA_SPARSE_PREFILL_MIN_KV`,
   `QSA_SPARSE_DECODE_MIN_KV`, and the prefill step size (512 / 1024 / 2048 /
   4096; `--suite model --prefill-chunks ...`).
3. **Full-depth synthetic run** at the chosen recipe and contexts 1K, 8K, 16K,
   32K, 40K: `--suite model --model-contexts ... --other-bits 8`. This gives
   the expected tok/s before real weights exist on the box.
4. **Real converted model** (after P6/P7 conversion):
   - Run `mlx_lm.generate` through the canonical module with a fixed prompt
     set: the 8 item-7 benchmark prompts plus 2 synthetic long-context
     prompts, at 8K and 32K tokens of filler with a question.
   - Run each prompt at each `reasoning_effort` with fixed seeds and
     `max_tokens` caps of 8K for low and medium and 32K for xhigh.
   - Log prompt tok/s, TTFT, per-bucket decode tok/s, tokens, final context,
     MLX peak, and process RSS. Watch `vm.swapusage` before and after, and
     abort on any swap growth.
5. **Compare against §7.** If decode misses by more than 20%, capture one
   decode step with Metal System Trace. Separate GPU busy time from encode
   gaps, then apply the §8 levers in order.

## 10. Open issues

1. **QSA top-k ties** (§3). Exact relu-zero ties at the K-th score make
   HF/MLX mask parity tie-dependent. Seen in the real-dim cross-check
   (8 entries). Gold and real-weight parity must compare modulo ties and
   report the tie rate. Fixed tie-breaking cannot reproduce torch CPU's order.
2. **MLX 0.31.2 `mx.fast.rope` bug.** With B > 1, T == 1 and a scalar
   offset, batch rows >= 1 get position 0. A [B] offset array is correct.
   `rope_offset()` works around it, and a test documents it. mlx-lm's
   `BatchKVCache` passes arrays and is unaffected, but the canonical module
   must not pass an int offset with B > 1. This deserves an upstream MLX
   report (external, so Ed's call).
3. **Left-padded batches.** HF forms QSA blocks from each row's *visible*
   indices, so block phase is per row. The fast paths (block-key cache,
   selection, token lists) assume unpadded rows, i.e. batch-1, the
   measurement mode. GOAL item 2's "batch-1 = left-padded" needs per-row
   block offsets (`mx.fast.rope` accepts [B] offsets).
4. **RoPE inv_freq rounding at long positions.** `mx.fast.rope` derives
   inv_freq internally, and HF computes `1/(1e7**(i/64))` in torch fp32. A
   1-ulp difference becomes ~1e-3 rad at position 40K. That is irrelevant
   for tiny-config parity, but long-context fp32 parity may need
   `freqs=` built exactly as HF does.
5. **The reference copy has drifted.** The venv-ref install of
   `modeling_qwen4_exp.py` differs from `.engine/`: it uses an additive-mask
   eager path for the QSA mask combination. The bool/SDPA path and the
   selection logic are identical.
6. **Measurement quality** (caveat at top). Medians come from a loaded,
   passively cooled M4. The full-depth chunk-2048 prefill came out *slower*
   per token than 512 (92 vs 105 tok/s), even though MoE alone is 1.8x
   faster at 2048. That is inconclusive under memory pressure; re-measure on
   the Mac. The long-context QSA *layer* decode numbers (3.5-3.9 ms at
   32-40K) include KV-buffer growth inside the 12-step timing window, so use
   the attention-only table for context scaling.
7. **Resource-rule excursions.** Two benchmark processes briefly exceeded the
   ~3 GB guideline. Generating a bf16 lm_head peaked at 3.8 GB, because MLX
   random ops peak at ~3x the output size. The full-depth chunk-2048 prefill
   peaked at 4.07 GB. Weight generation is now row-blocked (peak 1.05x), and
   the depth benchmark defaults to chunk 512. System memory stayed 40-56% free.
8. **Sparse-kernel efficiency** is ~0.7 TFLOPS. A simdgroup-MMA version with
   the 12 GQA heads padded to M = 16 should be 2-3x faster. Next after that
   is a fused score + radix top-k for the indexer at long context.
9. **GDN prefill kernel** is optional: a register-blocked or prefetching
   variant of the mlx-lm kernel, worth up to ~15% of GDN-layer prefill.
10. **The shared-expert fold** needs the shared expert at the routed experts'
    quantization (3-bit in e3_ple4_other8). If the recipe keeps it at higher
    bits, use the split variant; the difference is within noise.

## 11. Reproduce

```sh
# tests (MLX venv; CI skips them, since it has no mlx)
nice -n 10 /private/tmp/jwsol/venv-mlx/bin/python -m unittest -v tests.align.test_qwen4_exp_kernels
# official-reference cross-check (two venvs)
HF_HUB_OFFLINE=1 /private/tmp/jwsol/venv-ref/bin/python scripts/qwen4_exp_kernels_torch_check.py gen /tmp/x.npz
/private/tmp/jwsol/venv-mlx/bin/python scripts/qwen4_exp_kernels_torch_check.py check /tmp/x.npz
# benchmarks (as run here: 2 threads, nice 10, TMPDIR set)
python -m joulewise.align.models.qwen4_exp_kernel_bench --suite {calib,gdn,qsa,moe,misc,model} --json out.json
```
