# Qwen3.8-Flash-Next real-weight layer parity: layers 2 (GatedDeltaNet) and 3 (QSA)

GOAL item 5 (`docs/align/qwen4_exp_port/GOAL.md`), early laptop pass, 2026-11-05.
Port under test: `joulewise/align/models/qwen4_exp.py` at `e9f5ed799` (lane `lane/2026-11-05-align-flashnext-port`),
sha256 `4f3163af0d2dd143d200cc0e69088d84225ccb9c6442708c1a5f36c41dae7ac6`.
Reference: transformers 5.22.1 `models/qwen4_exp` (eager attention, eager experts), torch 2.15.0.
MLX 0.31.2, mlx-lm 0.31.3, one venv (`/private/tmp/jwsol/venv-both`).
Harness: `scripts/qwen4exp_real_layer_parity.py`.

## Verdict

**PASS** for layer 2 (GatedDeltaNet + MoE) and layer 3 (QSA with indexer + MoE) against the gates
below. One reference divergence is flagged and needs a policy decision: the QSA top-k order among exactly
tied blocks (finding 1). It is not a port defect.

The tables below show the worst case over 6 inputs (3 fixed-id prompts and 3 seeded random stream sets;
54 tokens per layer and mode). "Max rel" is max|port - ref| / max|ref|.

| Check | fp32 | bf16 |
|---|---|---|
| L2: all 9 captured tensors, prefill | max rel <= 5.8e-6, 1-cos <= 6.3e-12 | consensus-token error vs fp32 truth = 1.28x (DeltaNet), 1.54x (router), 1.74x (MoE), 1.43x (layer) of the official bf16 error (gate <= 2x) |
| L2: same, stepwise with caches | max rel <= 1.3e-6 | same picture |
| L2: expert sets, exact per token | 54/54 prefill, 54/54 stepwise | 21 port-vs-ref flips, 21/21 fp32 near-ties (ranks 9-12, <= 0.009 from boundary vs bf16 logit error <= 0.059) |
| L3: all 9 captured tensors, prefill | max rel <= 5.6e-6, 1-cos <= 3.8e-12 | consensus ratios 1.24 / 1.25 / 1.23 / 1.24 |
| L3: same, stepwise with caches | max rel <= 1.5e-6 | same picture |
| L3: expert sets | 54/54 prefill, 54/54 stepwise | 14 flips, 14/14 near-ties (ranks 10-12, <= 0.013 vs <= 0.037) |
| L3 short-prompt indexer | official selection == causal 24/24; port dense shortcut 24/24 | same |
| Prefill vs stepwise inside the port (layer out) | L2 4.9e-6, L3 1.5e-6 (reference: 6.8e-6, 3.4e-6) | within bf16 noise; flips are near-ties |
| Long QSA (T=2304), dense rows (< 2051) | 2.7e-6 | 4.5e-3 (1-cos 1.1e-5) |
| Long QSA, sparse rows, raw | 1.5e-2 on 14/253 rows with different key sets | 6.5e-3 |
| Long QSA, rows with different selection | 14/14 exact ties at score 0.0 | 12 exact ties + 1 near-tie (gap 4.9e-4 rel) |
| Long QSA, official attention forced to the port's selection | sparse rows 1.8e-6 | 5.2e-3 (= dense-row bf16 level) |
| Long QSA, port chunked prefill vs port stepwise | 1.7e-6, selection identical | 1 near-tie row |
| 6-bit routed experts (MLX affine, group 64), vs bf16 port | n/a | moe_out rel L2 2.1-2.6%, layer_out 0.4-1.2%, 1-cos <= 3.4e-4; routing and attention unchanged |

No mismatch that the tiny-model gold parity missed was found in any of these areas:
- head counts: 24 q / 2 kv heads; 16 k / 48 v DeltaNet heads with ratio-3 repeat-interleave;
- partial RoPE: 64 of 256 dims, and 64 of 128 dims in the indexer;
- the mRoPE sections, which are inert for text;
- the indexer budget and ratio: 2048 tokens, 512 blocks;
- `1 + w` norm folding;
- the 512 / top-10 router with normalized top-k;
- the sigmoid shared-expert gate;
- the hyper-connection low-rank 320 and the 4 streams.

The real config differs from the tiny gold config in each of these places.

## What was compared

**Weights.** The official bf16 shards (sha256-verified against HF), read with `safetensors.safe_open` through
`model.safetensors.index.json`. Only layer 2 / layer 3 tensors and the needed `embed_tokens` rows are read.
Both sides get bit-identical values: torch receives the bf16 tensors (upcast exactly for fp32), and MLX receives
the same bf16 bit patterns. Port parameter names and layouts (conv1d transpose, fused `gate_up_proj` split,
`model.language_model.` prefix) come from the port's own `Model.sanitize`. Its strict `load_weights` succeeded,
so no parameter was left at its initial value.

**Reference driver.** The official `Qwen4ExpTextModel.forward` is used, built on the `meta` device with the
real config (48 layers, `layer_idx` correct). Only layer L is materialized. Layers other than L are
pass-throughs, layer L-1 injects the test streams, and the final mixer is a pass-through. Positions,
the 4-D eager masks, the indexer position history and `DynamicCache` (prefill and stepwise) are therefore
produced by transformers itself, not by the harness.

**Lazy experts (all 512 never materialized).** The reference `Qwen4ExpTextExperts` runs its unmodified
eager loop. Its `gate_up_proj` / `down_proj` are replaced by an object that reads one selected expert slice
from the fused checkpoint tensor on demand. The port's `switch_mlp` is replaced by a wrapper that receives
the port router's own indices, reads only those experts, maps them through the port's sanitize, builds a
compact mlx-lm `SwitchGLU` (the class the port uses) and remaps the indices. The largest compact stack
was 81 experts.

**Inputs.**
- Tokenizer: the official `tokenizer.json` is not available offline (only `tokenizer_config.json`), so
  **fixed token ids** are used.
  - The three prompts have 8, 9 and 10 tokens. They mix the official special ids (`<|im_start|>`
    248045, `<|im_end|>` 248046, `<think>` 248068, `</think>` 248069, eos 248044) with seeded
    ordinary ids.
  - The input stream is `embed_tokens(ids)` tiled `hc_count`=4 times, exactly as the official forward does.
- Three seeded random stream sets with 8, 9 and 10 tokens, N(0, s^2), independent per hyper-connection
  stream. s = 0.00808 is the RMS of the real embedding rows.

**Captured and compared (port vs reference, same dtype):**
- the attention hyper-connection: mixed input and injection weights;
- the DeltaNet or QSA sublayer output;
- the stream after the attention residual;
- the MLP hyper-connection: mixed input and injection weights;
- router logits;
- per-token expert sets, compared exactly;
- the MoE output (routed plus gated shared expert);
- the full layer output (4 x 2560 streams).

Every input is run as a full prefill and as token-by-token decoding with the native caches of each
framework (`DynamicCache` / `Qwen4ExpRecurrentCache` / `Qwen4ExpAttentionCache`).

**Long sparse-QSA test (layer 3, attention sublayer).** With `indexer_budget` = 2048, the indexer only
drops blocks once a query has more than 512 complete blocks, at query 2051 and later. The short prompts
therefore exercise only the dense case, where the official indexer selects every causal key; this was
checked, and the port's `t <= budget` shortcut is exact there. Sparse selection is tested separately:
- Sequence: T = 2304 tokens (253 sparse queries).
- Input: the official layer-3 attention hyper-connection applied to tiled real embeddings of seeded ids.
- Reference: one-shot prefill and stepwise decoding.
- Port: chunked prefill (64-token chunks, the port's `jw_max_prefill_tokens`) and stepwise decoding.
- Selected key sets are compared per query.

## Tolerances (fixed before the full run)

- **fp32.**
  - Expectation: both sides compute the same IEEE fp32 math with different kernels:
    - Metal GEMM vs CPU BLAS;
    - recurrent Metal gated-delta kernel vs official chunked UT-transform;
    - SDPA vs eager softmax.
  - Expected discrepancy: about u * sqrt(K) per GEMM (u = 6e-8, K up to 10240), compounded over about 5
    chained GEMMs and nonlinearities, so about 1e-5 relative.
  - Gate:
    - normwise max rel (= max|port - ref| / max|ref|) <= 1e-4 for every tensor;
    - 1 - cos <= 1e-6;
    - expert sets identical on every token.
- **bf16.**
  - Each op rounds to 8 significant bits (unit roundoff 2^-9), and the two frameworks round at different
    points, so bit equality is not expected. A fixed absolute bound would be arbitrary, so the gate is
    reference-relative:
    - (i) on consensus tokens (bf16 port, bf16 reference and the fp32 reference all route to the same
      experts), the port's rel-L2 error against the fp32 reference must be <= 2x the official bf16
      reference's own error;
    - (ii) every port-vs-reference expert-set difference must be a near-tie in the fp32 truth. Every
      swapped expert must lie within 2x that token's bf16 router-logit error of the fp32 top-10/11
      boundary.
  - Reason for (ii): routing is discontinuous, so near-tie flips are inherent to bf16 and occur between
    the official bf16 prefill and stepwise paths too.
- **Sparse QSA selection.**
  - Selections must agree on every query, except where blocks have exactly equal official scores at the
    top-k boundary. The reference's order among tied blocks is unspecified: `torch.topk` documents no
    tie order and the port uses `mx.argpartition`.
  - Gate: every differing row must be tie-explained.
  - Given identical selection, outputs must meet the dense gates above. This is checked by running the
    official attention with its indexer forced to the port's selection.

## Results

### Generated tables: layer 2 (linear_attention)

| dtype | mode | tensor | max abs | max rel | max (1 - cos) |
|---|---|---|---|---|---|
| fp32 | prefill | attn_hc_mixed | 3.34e-06 | 1.35e-06 | 2.1e-13 |
| fp32 | prefill | attn_hc_inject | 1.55e-06 | 1.18e-06 | 4.0e-13 |
| fp32 | prefill | attn_out | 2.65e-06 | 4.83e-06 | 2.5e-12 |
| fp32 | prefill | mid_stream | 3.58e-06 | 5.00e-06 | 2.5e-12 |
| fp32 | prefill | mlp_hc_mixed | 1.48e-05 | 2.69e-06 | 2.6e-12 |
| fp32 | prefill | mlp_hc_inject | 2.21e-06 | 1.32e-06 | 2.4e-13 |
| fp32 | prefill | router_logits | 1.50e-05 | 3.67e-06 | 3.3e-12 |
| fp32 | prefill | moe_out | 5.36e-06 | 5.69e-06 | 6.3e-12 |
| fp32 | prefill | layer_out | 8.11e-06 | 5.79e-06 | 3.4e-12 |
| fp32 | prefill | expert sets (exact, per token) | 54/54 | | |
| fp32 | step | attn_hc_mixed | 8.05e-07 | 3.56e-07 | 1.1e-14 |
| fp32 | step | attn_hc_inject | 2.38e-07 | 1.73e-07 | 5.2e-15 |
| fp32 | step | attn_out | 2.98e-07 | 7.07e-07 | 1.8e-13 |
| fp32 | step | mid_stream | 3.50e-07 | 7.08e-07 | 1.8e-13 |
| fp32 | step | mlp_hc_mixed | 4.29e-06 | 7.40e-07 | 1.9e-13 |
| fp32 | step | mlp_hc_inject | 5.36e-07 | 3.59e-07 | 1.6e-14 |
| fp32 | step | router_logits | 4.77e-06 | 9.89e-07 | 2.5e-13 |
| fp32 | step | moe_out | 1.43e-06 | 1.19e-06 | 3.1e-13 |
| fp32 | step | layer_out | 2.62e-06 | 1.34e-06 | 2.2e-13 |
| fp32 | step | expert sets (exact, per token) | 54/54 | | |
| bf16 | prefill | attn_hc_mixed | 1.56e-02 | 7.69e-03 | 5.3e-06 |
| bf16 | prefill | attn_hc_inject | 7.81e-03 | 6.49e-03 | 5.0e-06 |
| bf16 | prefill | attn_out | 6.84e-03 | 1.47e-02 | 7.0e-05 |
| bf16 | prefill | mid_stream | 7.81e-03 | 1.38e-02 | 7.7e-05 |
| bf16 | prefill | mlp_hc_mixed | 1.25e-01 | 1.65e-02 | 8.5e-05 |
| bf16 | prefill | mlp_hc_inject | 1.56e-02 | 9.66e-03 | 1.4e-05 |
| bf16 | prefill | router_logits | 6.25e-02 | 1.75e-02 | 8.1e-05 |
| bf16 | prefill | moe_out | 3.12e-02 | 4.01e-02 | 3.7e-03 |
| bf16 | prefill | layer_out | 4.69e-02 | 3.33e-02 | 1.4e-03 |
| bf16 | prefill | expert sets (exact, per token) | 42/54 | | |
| bf16 | step | attn_hc_mixed | 1.56e-02 | 7.69e-03 | 5.3e-06 |
| bf16 | step | attn_hc_inject | 7.81e-03 | 6.49e-03 | 5.0e-06 |
| bf16 | step | attn_out | 6.84e-03 | 1.47e-02 | 6.9e-05 |
| bf16 | step | mid_stream | 7.81e-03 | 1.38e-02 | 7.7e-05 |
| bf16 | step | mlp_hc_mixed | 1.25e-01 | 1.65e-02 | 8.5e-05 |
| bf16 | step | mlp_hc_inject | 1.17e-02 | 7.85e-03 | 1.2e-05 |
| bf16 | step | router_logits | 6.25e-02 | 1.83e-02 | 7.9e-05 |
| bf16 | step | moe_out | 3.12e-02 | 3.93e-02 | 3.7e-03 |
| bf16 | step | layer_out | 6.25e-02 | 3.33e-02 | 1.4e-03 |
| bf16 | step | expert sets (exact, per token) | 45/54 | | |

| bf16 vs fp32 reference (truth) | port bf16 max rel | ref bf16 max rel | worst ratio max abs | worst ratio rel L2 |
|---|---|---|---|---|
| attn_hc_mixed | 8.11e-03 | 6.47e-03 | 1.35 | 1.17 |
| attn_out | 1.87e-02 | 1.22e-02 | 2.26 | 1.30 |
| mlp_hc_mixed | 1.48e-02 | 1.02e-02 | 1.81 | 1.33 |
| router_logits | 2.05e-02 | 1.18e-02 | 1.89 | 1.43 |
| moe_out | 3.92e-02 | 3.89e-02 | 2.06 | 6.22 |
| layer_out | 2.99e-02 | 2.23e-02 | 2.53 | 2.74 |
| expert sets equal to fp32 truth | port 40/54 | ref 45/54 | | |

Consensus tokens (bf16 port, bf16 ref and fp32 truth route identically): 37/54

| consensus tokens, vs fp32 truth | port bf16 rel L2 | ref bf16 rel L2 | worst ratio rel L2 | port bf16 max abs | ref bf16 max abs |
|---|---|---|---|---|---|
| attn_out | 1.18e-02 | 9.29e-03 | 1.28 | 7.47e-03 | 6.68e-03 |
| router_logits | 1.36e-02 | 1.20e-02 | 1.54 | 8.38e-02 | 4.31e-02 |
| moe_out | 1.87e-02 | 1.66e-02 | 1.74 | 3.44e-02 | 5.00e-02 |
| layer_out | 1.37e-02 | 1.21e-02 | 1.43 | 4.72e-02 | 7.84e-02 |

bf16 expert-set differences between port and reference: 21 token-mode pairs; near-ties in the fp32 truth: 21/21; swapped experts' fp32 ranks [9, 10, 11, 12]; max fp32 distance to boundary 0.00906 vs bf16 logit error up to 0.0587.

| bf16 cases with expert flips: agreeing tokens only | mode | moe_out max rel | layer_out max rel | layer_out 1 - cos |
|---|---|---|---|---|
| real_prompt0 (6/8 tokens) | prefill | 3.29e-02 | 3.33e-02 | 8.9e-05 |
| real_prompt0 (7/8 tokens) | step | 3.29e-02 | 3.33e-02 | 8.0e-05 |
| real_prompt1 (8/9 tokens) | prefill | 7.18e-03 | 7.52e-03 | 7.2e-05 |
| real_prompt2 (8/10 tokens) | prefill | 8.01e-03 | 1.08e-02 | 5.7e-05 |
| real_prompt2 (8/10 tokens) | step | 8.01e-03 | 1.08e-02 | 5.6e-05 |
| random0 (5/8 tokens) | prefill | 7.84e-03 | 1.48e-02 | 8.8e-05 |
| random0 (5/8 tokens) | step | 7.84e-03 | 1.48e-02 | 8.8e-05 |
| random1 (6/9 tokens) | prefill | 8.17e-03 | 1.67e-02 | 9.0e-05 |
| random1 (7/9 tokens) | step | 8.17e-03 | 1.67e-02 | 8.9e-05 |
| random2 (9/10 tokens) | prefill | 4.87e-03 | 6.47e-03 | 9.2e-05 |
| random2 (9/10 tokens) | step | 4.87e-03 | 6.47e-03 | 9.1e-05 |

| q6 routed experts (group 64) | mode | rel L2 vs bf16 | max rel vs bf16 | 1 - cos vs bf16 | rel L2 vs fp32 truth (q) | rel L2 vs fp32 truth (bf16) |
|---|---|---|---|---|---|---|
| moe_out | prefill | 2.60e-02 | 2.24e-02 | 3.4e-04 | 1.12e-01 | 1.10e-01 |
| moe_out | step | 2.58e-02 | 2.24e-02 | 3.3e-04 | 1.12e-01 | 1.10e-01 |
| layer_out | prefill | 1.22e-02 | 1.63e-02 | 7.4e-05 | 4.82e-02 | 4.72e-02 |
| layer_out | step | 1.20e-02 | 1.63e-02 | 7.2e-05 | 4.83e-02 | 4.72e-02 |
Routing unchanged by expert quantization: True; attention output bit-identical: True.

| self-consistency (stepwise vs prefill, layer out) | dtype | max abs | max rel | expert sets equal |
|---|---|---|---|---|
| port | fp32 | 9.54e-06 | 4.86e-06 | True |
| port | bf16 | 1.90e-02 | 1.48e-02 | False |
| ref | fp32 | 1.22e-05 | 6.79e-06 | True |
| ref | bf16 | 3.12e-02 | 7.52e-03 | False |

Run: 171.7 s; peak phys_footprint 3.158 GB (peak RSS 2.287 GB, MLX peak 2.518 GB); checkpoint bytes read 0.721 GB; min memory_pressure free 44%; expert reads {"L2_fp32": {"expert_reads": 1968, "max_port_expert_stack": 81, "ref_distinct_experts_touched": 260}, "L2_bf16": {"expert_reads": 1971, "max_port_expert_stack": 81, "ref_distinct_experts_touched": 264}}.

### Generated tables: layer 3 (full_attention)

| dtype | mode | tensor | max abs | max rel | max (1 - cos) |
|---|---|---|---|---|---|
| fp32 | prefill | attn_hc_mixed | 3.22e-06 | 1.49e-06 | 2.7e-13 |
| fp32 | prefill | attn_hc_inject | 3.19e-06 | 2.27e-06 | 3.1e-13 |
| fp32 | prefill | attn_out | 3.46e-06 | 3.29e-06 | 2.5e-12 |
| fp32 | prefill | mid_stream | 5.72e-06 | 3.28e-06 | 2.5e-12 |
| fp32 | prefill | mlp_hc_mixed | 2.57e-05 | 5.59e-06 | 3.2e-12 |
| fp32 | prefill | mlp_hc_inject | 2.68e-06 | 1.86e-06 | 3.8e-13 |
| fp32 | prefill | router_logits | 2.15e-05 | 3.89e-06 | 3.8e-12 |
| fp32 | prefill | moe_out | 6.41e-07 | 3.73e-06 | 5.5e-12 |
| fp32 | prefill | layer_out | 5.66e-06 | 3.33e-06 | 2.6e-12 |
| fp32 | prefill | expert sets (exact, per token) | 54/54 | | |
| fp32 | step | attn_hc_mixed | 5.96e-07 | 3.30e-07 | 1.2e-14 |
| fp32 | step | attn_hc_inject | 2.38e-07 | 1.85e-07 | 5.2e-15 |
| fp32 | step | attn_out | 7.15e-07 | 5.30e-07 | 1.1e-13 |
| fp32 | step | mid_stream | 7.15e-07 | 5.15e-07 | 1.1e-13 |
| fp32 | step | mlp_hc_mixed | 6.91e-06 | 1.48e-06 | 1.7e-13 |
| fp32 | step | mlp_hc_inject | 4.77e-07 | 3.98e-07 | 2.0e-14 |
| fp32 | step | router_logits | 2.86e-06 | 7.74e-07 | 2.1e-13 |
| fp32 | step | moe_out | 1.34e-07 | 8.83e-07 | 3.2e-13 |
| fp32 | step | layer_out | 7.75e-07 | 5.12e-07 | 1.2e-13 |
| fp32 | step | expert sets (exact, per token) | 54/54 | | |
| bf16 | prefill | attn_hc_mixed | 1.56e-02 | 1.08e-02 | 9.0e-06 |
| bf16 | prefill | attn_hc_inject | 7.81e-03 | 6.85e-03 | 9.1e-06 |
| bf16 | prefill | attn_out | 1.56e-02 | 1.16e-02 | 3.8e-05 |
| bf16 | prefill | mid_stream | 1.56e-02 | 1.27e-02 | 4.8e-05 |
| bf16 | prefill | mlp_hc_mixed | 1.88e-01 | 4.05e-02 | 6.3e-05 |
| bf16 | prefill | mlp_hc_inject | 1.17e-02 | 9.04e-03 | 1.2e-05 |
| bf16 | prefill | router_logits | 6.25e-02 | 1.48e-02 | 6.9e-05 |
| bf16 | prefill | moe_out | 2.54e-02 | 1.67e-01 | 3.0e-03 |
| bf16 | prefill | layer_out | 3.03e-02 | 2.17e-02 | 1.2e-04 |
| bf16 | prefill | expert sets (exact, per token) | 47/54 | | |
| bf16 | step | attn_hc_mixed | 1.56e-02 | 1.08e-02 | 9.0e-06 |
| bf16 | step | attn_hc_inject | 7.81e-03 | 6.85e-03 | 9.1e-06 |
| bf16 | step | attn_out | 1.17e-02 | 9.95e-03 | 3.7e-05 |
| bf16 | step | mid_stream | 1.56e-02 | 1.27e-02 | 4.7e-05 |
| bf16 | step | mlp_hc_mixed | 1.56e-01 | 3.38e-02 | 6.0e-05 |
| bf16 | step | mlp_hc_inject | 7.81e-03 | 6.54e-03 | 1.0e-05 |
| bf16 | step | router_logits | 6.25e-02 | 1.72e-02 | 6.8e-05 |
| bf16 | step | moe_out | 2.49e-02 | 1.63e-01 | 5.7e-03 |
| bf16 | step | layer_out | 3.12e-02 | 3.26e-02 | 2.4e-04 |
| bf16 | step | expert sets (exact, per token) | 47/54 | | |

Short-prompt indexer: official selection == causal on 24/24 runs; port dense shortcut on 24/24.

| bf16 vs fp32 reference (truth) | port bf16 max rel | ref bf16 max rel | worst ratio max abs | worst ratio rel L2 |
|---|---|---|---|---|
| attn_hc_mixed | 7.94e-03 | 5.89e-03 | 2.23 | 1.23 |
| attn_out | 1.22e-02 | 9.07e-03 | 2.45 | 1.24 |
| mlp_hc_mixed | 2.18e-02 | 1.82e-02 | 1.58 | 1.23 |
| router_logits | 1.39e-02 | 9.33e-03 | 1.98 | 1.23 |
| moe_out | 1.65e-01 | 1.42e-01 | 14.77 | 6.16 |
| layer_out | 3.28e-02 | 3.12e-02 | 3.19 | 1.81 |
| expert sets equal to fp32 truth | port 46/54 | ref 49/54 | | |

Consensus tokens (bf16 port, bf16 ref and fp32 truth route identically): 44/54

| consensus tokens, vs fp32 truth | port bf16 rel L2 | ref bf16 rel L2 | worst ratio rel L2 | port bf16 max abs | ref bf16 max abs |
|---|---|---|---|---|---|
| attn_out | 8.53e-03 | 7.61e-03 | 1.24 | 1.65e-02 | 7.78e-03 |
| router_logits | 9.76e-03 | 8.85e-03 | 1.25 | 4.46e-02 | 3.88e-02 |
| moe_out | 1.36e-02 | 1.19e-02 | 1.23 | 2.56e-03 | 1.92e-03 |
| layer_out | 9.86e-03 | 8.57e-03 | 1.24 | 1.98e-02 | 1.98e-02 |

bf16 expert-set differences between port and reference: 14 token-mode pairs; near-ties in the fp32 truth: 14/14; swapped experts' fp32 ranks [10, 11, 12]; max fp32 distance to boundary 0.0126 vs bf16 logit error up to 0.0367.

| bf16 cases with expert flips: agreeing tokens only | mode | moe_out max rel | layer_out max rel | layer_out 1 - cos |
|---|---|---|---|---|
| real_prompt1 (8/9 tokens) | prefill | 1.06e-02 | 8.85e-03 | 3.8e-05 |
| real_prompt1 (8/9 tokens) | step | 1.06e-02 | 8.85e-03 | 3.7e-05 |
| real_prompt2 (9/10 tokens) | prefill | 1.44e-02 | 9.43e-03 | 4.4e-05 |
| real_prompt2 (9/10 tokens) | step | 1.92e-02 | 9.43e-03 | 4.3e-05 |
| random0 (7/8 tokens) | prefill | 1.92e-02 | 8.98e-03 | 4.6e-05 |
| random0 (7/8 tokens) | step | 1.92e-02 | 8.98e-03 | 4.5e-05 |
| random1 (7/9 tokens) | prefill | 1.14e-02 | 1.02e-02 | 5.3e-05 |
| random1 (8/9 tokens) | step | 1.21e-02 | 1.02e-02 | 5.1e-05 |
| random2 (8/10 tokens) | prefill | 1.92e-02 | 1.05e-02 | 4.8e-05 |
| random2 (7/10 tokens) | step | 1.60e-02 | 1.05e-02 | 4.4e-05 |

| q6 routed experts (group 64) | mode | rel L2 vs bf16 | max rel vs bf16 | 1 - cos vs bf16 | rel L2 vs fp32 truth (q) | rel L2 vs fp32 truth (bf16) |
|---|---|---|---|---|---|---|
| moe_out | prefill | 2.06e-02 | 2.20e-02 | 2.1e-04 | 1.11e-01 | 1.10e-01 |
| moe_out | step | 2.06e-02 | 2.20e-02 | 2.1e-04 | 7.45e-02 | 7.18e-02 |
| layer_out | prefill | 4.12e-03 | 5.24e-03 | 8.5e-06 | 2.23e-02 | 2.21e-02 |
| layer_out | step | 4.11e-03 | 4.42e-03 | 8.4e-06 | 1.49e-02 | 1.46e-02 |
Routing unchanged by expert quantization: True; attention output bit-identical: True.

| self-consistency (stepwise vs prefill, layer out) | dtype | max abs | max rel | expert sets equal |
|---|---|---|---|---|
| port | fp32 | 1.73e-06 | 1.51e-06 | True |
| port | bf16 | 2.89e-02 | 3.10e-02 | False |
| ref | fp32 | 6.02e-06 | 3.41e-06 | True |
| ref | bf16 | 3.91e-03 | 2.36e-03 | True |

Long sparse-QSA test: T=2304, budget 2048, ratio 4; queries >= 2051 drop blocks.

| dtype | comparison | rows | max abs | max rel | 1 - cos | selection rows differing |
|---|---|---|---|---|---|---|
| fp32 | port_prefill_vs_ref_prefill | dense_queries | 4.65e-06 | 2.68e-06 | 1.3e-12 | 14 |
| fp32 | port_prefill_vs_ref_prefill | sparse_queries | 2.27e-02 | 1.52e-02 | 3.8e-06 | 14 |
| fp32 | port_step_vs_ref_step | dense_queries | 6.41e-07 | 3.70e-07 | 1.3e-13 | 14 |
| fp32 | port_step_vs_ref_step | sparse_queries | 2.27e-02 | 1.52e-02 | 3.8e-06 | 14 |
| fp32 | port_step_vs_port_prefill | dense_queries | 2.98e-06 | 1.72e-06 | 6.9e-13 | 0 |
| fp32 | port_step_vs_port_prefill | sparse_queries | 1.91e-06 | 1.28e-06 | 5.4e-13 | 0 |
| fp32 | ref_step_vs_ref_prefill | dense_queries | 4.17e-06 | 2.41e-06 | 1.3e-12 | 0 |
| fp32 | ref_step_vs_ref_prefill | sparse_queries | 2.92e-06 | 1.95e-06 | 1.2e-12 | 0 |
| fp32 | port_prefill_vs_ref_forced_port_selection | dense_queries | 4.65e-06 | 2.68e-06 | 1.3e-12 | forced equal |
| fp32 | port_prefill_vs_ref_forced_port_selection | sparse_queries | 2.74e-06 | 1.83e-06 | 1.3e-12 | forced equal |
| bf16 | port_prefill_vs_ref_prefill | dense_queries | 7.81e-03 | 4.48e-03 | 1.1e-05 | 13 |
| bf16 | port_prefill_vs_ref_prefill | sparse_queries | 9.77e-03 | 6.54e-03 | 1.6e-05 | 13 |
| bf16 | port_step_vs_ref_step | dense_queries | 8.79e-03 | 5.04e-03 | 1.5e-05 | 12 |
| bf16 | port_step_vs_ref_step | sparse_queries | 9.77e-03 | 6.54e-03 | 1.6e-05 | 12 |
| bf16 | port_step_vs_port_prefill | dense_queries | 7.81e-03 | 4.48e-03 | 6.5e-06 | 1 |
| bf16 | port_step_vs_port_prefill | sparse_queries | 7.81e-03 | 5.21e-03 | 2.9e-07 | 1 |
| bf16 | ref_step_vs_ref_prefill | dense_queries | 1.95e-03 | 1.12e-03 | 3.6e-10 | 0 |
| bf16 | ref_step_vs_ref_prefill | sparse_queries | 0.00e+00 | 0.00e+00 | 0.0e+00 | 0 |
| bf16 | port_prefill_vs_ref_forced_port_selection | dense_queries | 7.81e-03 | 4.48e-03 | 1.1e-05 | forced equal |
| bf16 | port_prefill_vs_ref_forced_port_selection | sparse_queries | 7.81e-03 | 5.24e-03 | 1.5e-05 | forced equal |

- fp32: official dense rows == causal: True; sparse rows proper subsets: True; selected keys per sparse query: [2048, 2051]; timing {'t_ref_prefill': 5.2, 't_ref_step': 70.4, 't_port_prefill': 1.0, 't_port_step': 13.2, 't_ref_forced_prefill': 2.4}
  - tie_analysis_port_prefill_vs_ref_prefill: 14 rows differ, 14 explained by exact ties at the top-k boundary (boundary scores [0.0]), not explained: 0; zero-score blocks per sparse query {'min': 0, 'max': 26, 'mean': 4.84}
  - tie_analysis_port_step_vs_ref_step: 14 rows differ, 14 explained by exact ties at the top-k boundary (boundary scores [0.0]), not explained: 0; zero-score blocks per sparse query {'min': 0, 'max': 26, 'mean': 4.84}
- bf16: official dense rows == causal: True; sparse rows proper subsets: True; selected keys per sparse query: [2048, 2051]; timing {'t_ref_prefill': 88.8, 't_ref_step': 85.2, 't_port_prefill': 0.6, 't_port_step': 10.4, 't_ref_forced_prefill': 105.7}
  - tie_analysis_port_prefill_vs_ref_prefill: 13 rows differ, 12 explained by exact ties at the top-k boundary (boundary scores [0.0]), not explained: 1; zero-score blocks per sparse query {'min': 0, 'max': 26, 'mean': 4.84}
  - tie_analysis_port_step_vs_ref_step: 12 rows differ, 12 explained by exact ties at the top-k boundary (boundary scores [0.0]), not explained: 0; zero-score blocks per sparse query {'min': 0, 'max': 26, 'mean': 4.84}
- bf16 vs fp32 reference prefill: port max rel 1.32e-02 (1-cos 1.6e-05), reference max rel 1.29e-02 (1-cos 1.3e-05)
- RoPE tables (fp32, positions 0..2303): {"rotary_dim": 64, "inv_freq_max_abs": 1.4901161193847656e-08, "inv_freq_ulps_differing": 15, "cos_max_abs": 6.101839244365692e-05, "sin_max_abs": 6.101094186306e-05, "port_cos_vs_fp64_max_abs": 6.0135379744349904e-05, "ref_cos_vs_fp64_max_abs": 6.012792916375298e-05}

Run: 493.4 s; peak phys_footprint 2.815 GB (peak RSS 2.109 GB, MLX peak 2.189 GB); checkpoint bytes read 1.199 GB; min memory_pressure free 45%; expert reads {"L3_fp32": {"expert_reads": 1840, "max_port_expert_stack": 70, "ref_distinct_experts_touched": 240}, "L3_bf16": {"expert_reads": 1842, "max_port_expert_stack": 70, "ref_distinct_experts_touched": 237}}.



## Findings

### 1. QSA top-k: exact score ties at the budget boundary are broken differently (not a port bug; needs a policy)

**What happens.** In the sparse regime, 14 of 253 sparse queries (fp32) select a different key set. Every
one of them is an exact tie. The official per-block score is sum over 4 heads of relu(q_h . k_block) / sqrt(128),
so it is exactly 0.0 whenever all four heads are negative. With real weights and real-embedding inputs,
0 to 26 visible blocks per sparse query score exactly 0 (mean 4.8).

**When it matters.** It only matters while the number of complete blocks is just over 512. At queries
2051 to about 2090, only 1 to 8 blocks are dropped, so the boundary falls among the zero-score blocks.
Later queries drop more blocks, the boundary moves into positive scores, and the selections agree exactly.

**Why the two sides differ.**
- The official code uses `scores.topk(...)` (torch CPU). The port uses `mx.argpartition(-scores, k-1)`
  (`qwen4_exp.py` `QSAIndexer.__call__`).
- Neither documents a tie order. In a direct probe, `mx.argpartition` kept the lowest tied indices, and
  `torch.topk` kept a subset that depends on its selection algorithm (sometimes the lowest, sometimes not).
- In the real run, the port's port-only blocks average index 155 and the reference-only blocks average
  index 381.

**Evidence.**
- `diag_L3_2304.json`: for every differing row, the blocks chosen by only one side have official score
  exactly 0.0, the 512th and 513th scores are both 0.0, and the query-local tails are equal.
- Official attention run with its indexer forced to the port's selection: the sparse rows then agree to
  1.8e-6 (fp32). The gather, tail, GQA, masks, gate and o_proj downstream of top-k are therefore exact.

**Impact.**
- Up to 1.5e-2 relative change in the attention output on the affected rows (fp32). This is a different,
  equally valid application of the same algorithm.
- Bit-parity with the reference at ties is not well defined. The official CUDA top-k and production
  kernels may order ties differently again.

**Recommendation for the port owner (not changed here).**
- Make the tie policy explicit and deterministic, for example a stable top-k on (score desc, block index asc),
  and document it.
- Write parity gates modulo exact ties, as this harness does.
- If the Qwen inference kernel's order becomes known, match it.

### 2. bf16 precision: the port is 1.2x to 1.7x noisier than the official bf16 path (within gate; not a semantic bug)

**What was measured.** On consensus tokens, the port's bf16 error against the fp32 reference is 1.23x to
1.74x the official bf16 reference's own error. There is no single outlier op: hyper-connection, DeltaNet
and MoE each carry about 1.2x to 1.5x.

**Single-op microtest** (`--bf16-op-microtest`, `bf16_op_microtest.json`): same bf16 inputs, error vs fp64.

| op | MLX error / torch-CPU error |
|---|---|
| `mx.sigmoid` | 1.35x |
| `nn.silu` | 1.21x |
| mlx-lm `swiglu` | 1.11x |
| 4-stream bf16 `mean` | 1.58x |
| bf16 matmul (K=10240) | 1.00x |

**Interpretation.** The excess comes from backend elementwise and reduction rounding, not from the port's
math.

**A cheap port-side option** (not changed, not tested): compute the hyper-connection stream mean and the
sigmoid gates in fp32 before casting.

**Practical relevance.** Low. The target precision is 6-bit experts, and its error is larger
(finding 4). bf16 routing flips relative to the fp32 truth also happen in the official bf16 path:
- L2: the port differs from truth on 14/54 tokens, the reference on 9/54;
- L3: the port on 8/54, the reference on 5/54.

### 3. bf16 routing near-ties are inherent

All 35 port-vs-reference expert-set differences (L2 21, L3 14) swap experts at fp32 ranks 9 to 12 whose
fp32 logits are within 0.013 of the top-10/11 boundary, while the per-token bf16 logit error is 0.016 to
0.059. The official bf16 reference also flips between its own prefill and stepwise on L2. The large
"all tokens" bf16 `moe_out` ratios in the generated tables (up to 6.2x rel L2) come from these flips. On
tokens that route identically, `moe_out` agrees to <= 1.9e-2 max rel (L3) and <= 3.3e-2 (L2).

**Gate note.** The sparse-QSA gate was written for exact ties. In bf16, one row (2269) is instead a
near-tie: official bf16-path scores 0.468216 and 0.467987. The port's own chunked prefill and stepwise
disagree on that row (64-row GEMM vs GEMV rounding of q), and the port's stepwise matches the reference.
This is the same near-tie criterion already applied to routing. It is stated here explicitly because the
written QSA gate did not anticipate bf16 near-ties.

### 4. 6-bit routed experts (requested by the coordinator)

**Setup.** MLX `mx.quantize` (affine, group 64, 6 bits) applied to the routed experts only, through
mlx-lm `SwitchLinear.to_quantized`, the converter's quantizer. Everything else stays bf16. Quantizing only
the selected experts is identical to quantizing the full stack, because groups run along each expert row.

**Results.**

| tensor | rel L2 vs bf16 port | max rel | 1-cos |
|---|---|---|---|
| L2 `moe_out` | 2.6% | 2.2e-2 | 3.4e-4 |
| L2 layer out | 1.2% | | |
| L3 `moe_out` | 2.1% | | 2.1e-4 |
| L3 layer out | 0.4% | | 8.5e-6 |

- Prefill and stepwise agree.
- Routing in the quantized layer is unchanged, as it must be: the router precedes the experts.
- The attention output is bit-identical.

**A-priori estimate.** For 6-bit affine quantization with group 64, the step is about range/63, which is
about 4.8 sigma/63. That gives roughly 2.2% relative weight noise per projection, and about 2% to 4% at
the routed-expert output, which matches. Against the fp32 truth, 6-bit adds about 0.2% on top of bf16's
error, which is dominated by routing flips.

**Not measured here:** the effect on downstream layers' routing.

### 5. RoPE tables at long positions (fp32, informational)

The port computes `theta ** (-i/d)` and the reference computes `1 / theta ** (i/d)`, so `inv_freq` differs
by 1 ulp in 15 of 32 entries. The cos/sin tables differ by up to 6.1e-5 at positions up to 2303, but both
are equally far from fp64 (6.01e-5 each), because fp32 rounding of `pos * inv_freq` dominates. The effect
is invisible in dense-row parity (2.7e-6 at T=2304). Both implementations' angle error grows linearly with
position (about 1e-3 rad near 40k). If fp32 parity at the 40k context cap is gated, budget for this, or
compute angles in fp64 on both sides.

## Memory and safety record

**Limits and guards.**
- Laptop: M4 Air, 24 GB, shared with the critical analysis job.
- Run settings: `nice -n 10`, `OMP_NUM_THREADS=2`, torch threads 2, `TMPDIR=/private/tmp/jwrealparity`,
  offline HF.
- `memory_pressure` was checked before every heavy step (58 checks), with a stop below 20% free.
  The minimum observed was 44% free.
- A watchdog would abort if `phys_footprint` exceeded 6 GB. It tracks `phys_footprint` rather than RSS
  because RSS does not include Metal buffers (checked: a 1 GiB MLX array leaves RSS unchanged).

**Peaks.**
- L2: `phys_footprint` 3.16 GB (RSS 2.29 GB, MLX 2.52 GB).
- L3: 2.82 GB (RSS 2.11 GB, MLX 2.19 GB).

**Experts.** No more than 81 experts were ever resident on the port side. The reference held one expert
at a time. All 512 were never materialized.

**Runtime.** L2 172 s, L3 493 s. Most of the L3 time is the eager bf16 CPU prefills at T=2304.

**Rules followed.**
- Nothing under `/Users/edr/jw-b5-*`, `/Users/edr/night-*` or any `restricted/` path was read.
- Community PR #1788 code was not executed.

**Coordination note.** The coordinator suggested cloning from `/Users/edr/jw-b5-analysis/.git`, which
conflicts with the no-`jw-b5-*` rule. The shared lane clone's object store borrows from that path, so this
branch was instead made as a blobless clone straight from GitHub, with no alternates. The shared lane
clone was left with a clean working tree.

## Limitations of this pass

- **Inputs are not true layer-2/3 activations.** Those would need layers 0 and 1, including the 51B-row
  n-gram PLE. The inputs here are network-entry streams (tiled embeddings) and random streams at the
  embedding scale.
  - The hyper-connection norm makes the sublayer inputs scale-free.
  - The residual streams are small at this scale, so the layer-output relative error is dominated by
    the injected sublayer outputs. This is the conservative direction.
- **Fixed token ids**, because no offline tokenizer is available.
- **Only batch 1 and unpadded inputs at real weights.** Left padding and batching remain covered only by
  the tiny-model gold gate.
- **One input for the long sparse-QSA test** (T = 2304).
- **Not covered here:** the n-gram PLE layer (layer 1; shard model-00005 is present but unused), the
  embeddings/head end-to-end, and the final mixer (shard model-00001 is not on the laptop).

## Reproduce

```
nice -n 10 env OMP_NUM_THREADS=2 TMPDIR=/private/tmp/jwrealparity HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  /private/tmp/jwsol/venv-both/bin/python -B scripts/qwen4exp_real_layer_parity.py \
  --weights /private/tmp/jwflash-weights --layer 2 --out /private/tmp/jwrealparity/L2.json
# same with --layer 3 (adds the T=2304 sparse-QSA test, --long-tokens)
# root-cause diagnostic for QSA selection differences:
#   ... --layer 3 --long-tokens 2304 --diagnose-indexer --out /private/tmp/jwrealparity/diag_L3_2304.json
# tables: python scripts/qwen4exp_real_layer_parity.py --summarize L2.json L3.json
```
Raw results: `docs/align/qwen4_exp_real_layer_parity_L2_L3/` (JSON from the runs above).
