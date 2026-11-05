# Static audit: mlx-vlm `qwen4_exp` (Qwen3.8-Flash-Next) vs the official transformers reference

Date: 2026-11-05. Auditor: Opus 5.5 subagent, read-only. Context: GOAL.md (CORRECTION entry), contribution (a).

## Verdict

**LIKELY DEFECTS** overall. There is one definite defect, in an advertised path.

- **Single-request text generation**, with or without chunked prefill, is **faithful to the reference up to bf16 precision**. This is the path JouleWise would use. Every structural component matches, including the QSA indexer, the n-gram PLE hash, hyper-connections, `1 + w` norms, MoE wiring and RoPE. The remaining differences only change results in bf16. At most one of them can change a discrete choice: which expert the router picks at near-ties, and which blocks QSA selects at near-ties.
- **Batched generation with ragged left padding is wrong.** This includes the continuous batching that the module README advertises as supported, and batched speculative verification. When any row of the batch is left-padded, every QSA layer drops its sparse selection and attends densely. The trigger is a row whose visible context exceeds 512 complete blocks, which is 2052 or more tokens. Equal-length batches and single requests are not affected.

## Provenance and method

- Source: `Blaizzy/mlx-vlm`. The GitHub API now resolves this name to `Neywa-Labs/mlx-vlm`, so the repo was transferred.
  - Latest release `v0.7.12` (published 2026-11-04, tag commit `7230940302cbe602054650f18a2f77db945bc57a`).
  - `main` at `5cdc659bdd427225b42d65c3c66da35e1fb5e493` (2026-11-05T02:18Z).
- **`mlx_vlm/models/qwen4_exp/*` is byte-identical at the tag and at main** (same blob SHAs). So is every shared dependency audited here: `qwen3_5/{language,gated_delta,speculative_verifier}.py`, `qwen3_5_moe/language.py`, `switch_layers.py`, `cache.py`, `rope_utils.py` and `quantized_verifier.py`.
- Fetched as text only (contents API, base64-decoded) into `/private/tmp/jwmlxvlm-src/{main,v0.7.12,deps-main}/*.txt`, with checksums in `/private/tmp/jwmlxvlm-src/SHA256SUMS`. Nothing was imported, installed or executed. The one computation below is stdlib-only Python written for this audit.
- Reference: transformers `modeling_qwen4_exp.py` and `configuration_qwen4_exp.py`, plus the real `config.json`. All are under `jw-wt/opus-flashnext-twin/.engine/`.
- Second reading: the Sol port `jw-wt/sol-flashnext-port/joulewise/align/models/qwen4_exp.py` (+ `qwen4_exp_tables.py`). It is parity-verified to 6e-8 fp32.
- Citation prefixes used below:
  - `vlm:` = `mlx_vlm/models/qwen4_exp/language.py`.
  - `vlm/<file>:` = other files in `qwen4_exp/`.
  - `q35:` = `mlx_vlm/models/qwen3_5/language.py`.
  - `q35gd:` = `qwen3_5/gated_delta.py`.
  - `q35sv:` = `qwen3_5/speculative_verifier.py`.
  - `q35moe:` = `qwen3_5_moe/language.py`.
  - `ref:` = `modeling_qwen4_exp.py`.
  - `cfg:` = `configuration_qwen4_exp.py`.
  - `sol:` = the Sol port's `qwen4_exp.py`.

### Decode routing (it decides which code is actually run)

- **Single-token decode with a cache** goes to `Qwen4ExpBatchInvariantForward` (`q35:1872-1892` → `vlm:2088-2104`). This holds whenever `lm_head` is unquantized or uses the optimized affine head. That class reuses `Qwen3_5BatchInvariantForward._attention / _gated_delta / _feed_forward` (`q35sv:74-292`). Its own overrides are `_model`, `_layer`, `_ple`, `_hyper_connection`, `_qsa_attention` and the q/k normalisation (`vlm:1776-2056`).
- **Prefill** goes through `Qwen4ExpModel.__call__` (`vlm:1602-1738`). For batches with a batch cache, it runs **row by row on the unpadded rows** and then merges the caches (`vlm:1624-1711`).

## Ranked deviation list

| # | Class | Component | Summary |
|---|---|---|---|
| D1 | **Definite bug** | QSA, batching | With a left-padded batch cache, decode and multi-token verify discard the QSA selection mask and run dense ragged attention. |
| P1 | Possible bug (bf16) | MoE router | Softmax probabilities are rounded to bf16 before top-k and renormalisation, so adjacent logits can tie and pick a different expert. |
| P2 | Possible bug (bf16) | Gated DeltaNet | `softplus(a + dt_bias)` and the q/k L2 normalisation run in bf16; the reference uses fp32. This causes recurrent-state drift. |
| P3 | Possible bug (ties/bf16) | QSA top-k | `argpartition` and `torch.topk` differ on exact ties, which relu makes possible (exact-zero scores). bf16 RoPE rounding also differs, so near-ties at block 512 can flip. |
| P4 | Possible bug (server/APC path) | Batching, PLE, QSA caches | Right-padded "APC mixed prefill": the per-row merge drops the `prepare(right_padding, lengths)` metadata, and the PLE windows ignore `lengths`. |
| P5 | Possible bug / unsupported | Batching without a cache | A left-padded batch with `cache=None` is treated as unpadded: attention is not padding-masked and PLE hashes pad ids instead of EOS. |
| L1 | Deliberate | Quantization predicate | `--quantize` quantizes the QSA indexer, hyper-connection projections and gates at the global bit width. The router and shared-expert gate use 8-bit. The PLE falls back to group 32. |
| L2 | Deliberate (documented) | PLE storage | The external PLE store supports only 4-bit (affine g32 or nvfp4 g16). There is no bf16 paging. |
| L3 | Deliberate | Weights | `mtp.*` is dropped (as in the reference). `A_log` is kept in fp32 (`cast_predicate`). |
| E1–E13 | Equivalent rewrites | various | See the component sections: Metal sequential DeltaNet kernel, block-summary caching, fixed-width top-k, single-rounding RoPE and gated norm, row-wise padded prefill, and others. |
| N1–N3 | Latent hazards | various | Silent state reset on batch-size mismatch; negative scatter indices in `build_mask`; hash buffers loaded unvalidated. None is reachable in the audited paths. |

### D1: ragged-batch QSA falls back to dense attention (definite)

**Reference.** Every indexed-attention call ANDs the causal/padding mask with the indexer's selection mask (`ref:841-847`). This holds with or without padding.

**mlx-vlm, main path** (`Qwen4ExpAttention.__call__`, `vlm:1099-1122`):

1. The indexer runs first (`vlm:1099`).
2. For L = 1 with a left-padded `BatchQSAKVCache`, the mask is the string `"left_padded_decode"`. It is produced by `_create_qwen4_exp_attention_mask` → `_create_qwen3_5_attention_mask` (`vlm:1564-1582`, `q35:278-292`).
3. Because the mask is "a string other than causal", the code returns `super().__call__(..., mask=mask)` (`vlm:1112-1122`), discarding the selection.
4. Qwen3.5 attention then runs `_qwen3_5_left_padded_attention` (`q35:1007-1021`, `q35:878-940`). That is dense over each row's unpadded keys, with `mask=None`.

**mlx-vlm, batch-invariant decode path** (the one actually used for decode):

1. `_qsa_attention` builds `qsa_mask` (`vlm:1871-1874`).
2. It merges only when `mask is None`, `"causal"`, or an array (`vlm:1876-1885`). With `mask == "left_padded_decode"` the QSA mask is dropped.
3. `_attention` then routes `left_padded_decode` or `length > 1` to the same dense ragged helper (`q35sv:97-112`).
4. For multi-token verify on a padded batch, the boolean mask array (which already contains the QSA mask) is also ignored. `_qwen3_5_left_padded_attention` never reads its `mask` argument (`q35:878-940`).

**Concrete input.** Batch of 2 prompts, 3000 and 2990 tokens. Row 1 has 10 left pads; after the merge `left_padding = [0, 10]`. Greedy decode.

- At the first decode step, row 0 has 3001 visible tokens, which is 750 complete blocks, more than 512.
- The reference attends the top-512 blocks plus the tail: at most 2051 keys.
- mlx-vlm attends all 3001 keys in each of the 12 QSA layers, so the logits differ.
- The same prompts run as single requests (or as an equal-length batch) take the sparse path correctly. That gives a clean A/B comparison.

**Scope.** Continuous batching in `mlx_vlm.server`/`BatchGenerator` becomes ragged as soon as requests of different lengths share a batch. Batched MTP speculative verify is also affected. Single requests are not affected.

**Fix sketch** (for an upstream PR). In both paths, treat `"left_padded_decode"` like an array mask:

- materialise the left-padding mask, AND it with `build_mask(selection)` (which is already left-padding-aware, `vlm:1042-1081`), and call masked SDPA; or
- extend the QSA kernel with a per-row `left_padding` offset.

---

## Component audit

### 1. QSA indexer

| Aspect | Reference | mlx-vlm | Sol port | Finding |
|---|---|---|---|---|
| Projection split q (4×128) / k (1×128) | `ref:675-702` | `vlm:826-830, 890-892` | `sol:307, 314-317` | Match |
| q: `q_layernorm` (`1 + w`) then partial RoPE (64 of 128 dims) at current positions | `ref:703-704` | `vlm:893, 905, 843-847` → fused MRoPE kernel (half-split pairs `d, d+32`; dims ≥ 64 passed through, `rope_utils.py:569-652`) | `sol:316` | Match (E5 for rounding) |
| Raw keys appended to the index cache **before** any early exit | `ref:706-707` | `vlm:895-898` (before the `vlm:902` early return) | `sol:318-321` | Match |
| Blocks formed from each query's **visible** tokens (left padding offsets block boundaries) | `ref:721-729` | `block_starts = left_padding + j·4` (`vlm:914-915`); valid iff `j < (query_end − lp)//4` (`vlm:1013-1017`) | `sol:328-337` | Match (left-padding only, which is the only supported padding) |
| Block summary: fp32 mean of 4 raw keys → cast to raw dtype → `k_layernorm` → RoPE at the block's **first token position** | `ref:731-740` | `vlm:960-987` (positions from the cached position history, `vlm:970-986`) | `sol:331-333` | Match |
| Score = Σ_heads relu(q·k) / √128, in fp32 | `ref:742-745` | `vlm:1007-1011` | `sol:334` | Match (the √D scale is applied after the sum in both; monotone either way) |
| Budget: `block_topk = 2048/4 = 512`; `topk(min(512, n_complete))` | `ref:674, 747` | Fixed width 512 with −inf padding, `argpartition`, invalid → −1 (`vlm:1020-1031`); dense causal when `complete ≤ 512` (`vlm:1077-1080`) | `sol:338-340` | **E3 equivalent**: when there are > 512 valid blocks, all scores are ≥ 0 and finite, so no −1 or −inf enters the top-512 |
| Tail = the incomplete visible block (includes the query itself); the query's own token is attended only if its block is selected when `visible % 4 == 0` | `ref:752-753` | `vlm:1070-1073` (mask) and `vlm/qsa_kernel.py:111-140` (kernel) | `sol:343-345` | Match, including the self-exclusion quirk |
| Tie-breaking | `torch.topk` (unspecified on ties) | `mx.argpartition` (unspecified on ties) | `argpartition` | **P3** |
| Decode incremental path | Recomputes everything per step | Early exit to dense while `key_len//4 ≤ 512` (`vlm:902-903`). Normalised+roped block summaries cached on the cache and extended only by newly completed blocks (`vlm:916-1003`). Cleared on trim/filter/extend/padding (`vlm:162-169, 337, 363, 447, 549, 1000-1003`) | Recomputes | **E2/E4 equivalent** |
| Sparse execution | Boolean mask over all keys | Metal kernel over selected blocks ∪ tail, online softmax in fp32, used only for zero padding and bf16/fp16 (`vlm/qsa_kernel.py:22-166, 209-265`). Otherwise `build_mask` + masked SDPA (`vlm/qsa_kernel.py:387-396`) | Per-query KV gather | **E12 equivalent** (`key_pos < query_end` and the tail both reproduce the causal bound) |
| Padded batches | Mask-driven | Correct selection is computed and then **discarded** | n/a | **D1** |

Note **N2**. For −1 blocks, `build_mask` forms token indices `lp−4..lp−1` (`vlm:1053-1067`), which can be negative when `lp < 4`. This is harmless today for two reasons: such rows are only used when `complete ≤ 512`, where the causal branch replaces them (`vlm:1077-1080`), and MLX scatter wraps signed indices within the row. It is fragile.

### 2. Gated DeltaNet

| Aspect | Reference | mlx-vlm | Finding |
|---|---|---|---|
| Projections `in_proj_qkv / z / b / a`; split q/k/v = `[2048, 2048, 6144]`; 48 value heads over 16 key heads (value head h uses key head h // 3) | `ref:495-498, 556-575` | `q35:1136-1141, 1221-1228`; kernel `hk_idx = hv_idx / (Hv/Hk)` (`q35gd:38`); ops use `mx.repeat` (= `repeat_interleave`) (`q35gd:387-389`) | Match |
| Conv: depthwise K=4, silu; state = last K−1 pre-activation inputs | `ref:200-240, 528-553` (state length 4, equivalent) | `q35:1189-1219`, `q35sv:237-261`; `update_window(0, …, 3, lengths)` | **E7 equivalent** |
| β = sigmoid(b) in bf16 | `ref:570` | `q35gd:413-414` | Match |
| g = −exp(A_log)·softplus(a + dt_bias) | **fp32**: `a.float() + dt_bias` (`ref:572`) | `exp(−exp(A_log.f32) · softplus(a + dt_bias))` with `a` and `dt_bias` in **bf16** (`q35gd:407-409`); `dt_bias` is cast to bf16 by `cast_predicate` (`q35:2065-2072`) | **P2** (bf16 only); Sol port casts both to fp32 (`sol:292-293`) |
| q/k L2 norm (sum + 1e-6) and q·D^−½ | Done **after the cast to fp32** (`ref:289-299, 409-419`) | `_normalize_qk` / `_qwen4_normalize_gated_delta_qk` run on **bf16** conv output (`vlm:799-805, 1768-1773`) | **P2** (bf16 only); epsilon placement correct; Sol port casts first (`sol:286-290`) |
| Delta rule | Chunked UT solve (prefill), recurrent (decode), fp32 | Sequential Metal kernel, fp32 accumulators, decay → read → delta·β → write → read-out order identical to `ref:434-442` (`q35gd:66-98`); chunked scan only off-GPU (`q35gd:587-595`) | **E1 equivalent** |
| Recurrent state dtype | fp32 (`ref:357-360, 423-427`) | fp32 zeros (`q35gd:582-585`), kept via `update_recurrent` (`cache.py:934-960`) | Match |
| Padding | Zeroes the layer input (`ref:508`); pads still decay the state | Masks `mixed_qkv` and freezes the state at masked steps (`q35:1202-1206`, `q35gd:67-90`) | **E10 equivalent** for leading pads, since the state is zero before them |
| Gated norm | RMS in fp32 → cast → ·w (bf16) → ·sigmoid(z) in fp32 (`ref:176-185`); `output_gate_type="sigmoid"` | `mx.fast.rms_norm(x, w)` (one rounding) → fp32 ·sigmoid(z) (`vlm:772-787`) | **E6 equivalent** (≤ 1 bf16 ulp); weight not `1 + w`, correct |

### 3. Hyper-connection streams

- **Expansion.** The embedding is tiled 4× along features (`vlm:1713`, `vlm:2006`), matching `ref:1456`.
- **Mixer.** `hc_norm` is a grouped RMSNorm over each 2560-wide stream with `1 + w` (`vlm:1169-1173`, `vlm:741-754`). Then come `silu(down/4)`, `sigmoid(up)` and a mean over streams of weight × **normed** stream (`vlm:1185-1191`, `vlm:1741-1753`). This matches `ref:1008-1014`.
- **Injection.** `2·sigmoid(inject/4)` (`vlm:1755-1757`). The residual is `hyper_input + branch ⊗ w`, using the **un-normed** input, in stream-major layout (`vlm:1555-1561`, `vlm:1762-1765`). This matches `ref:1017-1018, 1291-1298`.
- **Contraction.** The final `hyper_connection_mixer` has no combine step and there is **no final norm** before `lm_head` (`vlm:1738`, `vlm:2041-2051`). This matches `ref:1469` and `ref:1637-1640`.
- Result: Match.

### 4. n-gram PLE

| Aspect | Reference | mlx-vlm | Finding |
|---|---|---|---|
| Applied at one-indexed `ple_layer_ids=[2]` (layer index 1), before the attention hyper-connection | `ref:1257, 1272-1275` | `vlm:1523-1529, 1541-1544` | Match |
| Hash constants: splitmix64, γ, M1, M2, `PRIME_1=10007`, seed default 1234 (absent from config.json), multipliers `2·(sm % half)+1` with `half = ((2^63−1)//vocab)//2` | `ref:1021-1044`, `cfg:155` | `vlm:1207-1232`, `vlm/config.py:55` | Identical; also identical to `qwen4_exp_tables.py:33-43` |
| Per-head prime vocab sizes (n-th prime after 2e7−1) and offsets; padded to a multiple of 128 | `ref:1083-1100` | `vlm:1326-1347` | Identical |
| EOS-segmented right shift, with the history seeded with EOS | `ref:1102-1116, 1126-1129` | `vlm:1374-1405` | Identical |
| Mixing: `t0·m0 ⊕ t1·m1 (⊕ t2·m2)` in int64, `% prime + offset`; 8 bigram + 8 trigram heads | `ref:1148-1163` | `vlm:1413-1428` | Match. No overflow: `t·m < 2^63` by construction, so the remainder sign convention is moot |
| Token history cache (last 2 ids) | `conv_state[2]` (`ref:1122-1142`) | `cache[3]` via `update_window` (`vlm:1398-1407`) | Match; covered by the speculative transaction (`cache.py:1038-1065`) |
| Table sharding: 128 checkpoint shards, concatenated on dim 0 | `cfg:62-64` | `ShardedEmbedding`, equal `divmod` split, `shard_i` → `shards.i` (`vlm:1255-1303`, `vlm/qwen4_exp.py:17, 74`) | **E8 equivalent** because `padded_vocab % 128 == 0`. A different split would fail loudly on shapes, not silently |
| Key/value projections, three grouped `1 + w` norms, gate `sign·√max(|g|,1e-6)`, `sigmoid(gate)·value` per stream | `ref:1231-1239` | `vlm:1492-1506` | Match |
| Dilated depthwise conv (K=4, dilation 3, state 9), silu, residual `gated + conv(normed)`; padding masked | `ref:1205-1244` | `vlm:1459-1483, 1507-1510` | Match |
| Pads replaced by EOS before hashing | `ref:1447-1452` | Pads never reach the PLE in batched prefill (row-wise on unpadded rows, `vlm:1652-1695`); fully padded rows seed an EOS history (`vlm:1662-1678`) | **E9 equivalent**; but see **P5** (no cache) and **P4** (right padding) |

Note **N3**. The int64 hash buffers are module arrays, so strict loading takes them from the checkpoint and does not validate them. The Sol port validates them (`sol:580-586`). Floating-point casting skips integers (`convert.py:345`), so they are not corrupted.

### 5. Norms and `1 + w`

- `Qwen4ExpRMSNorm` computes `x·rsqrt(mean x²+eps)·(1+w)` in fp32 and casts back. It has an optional group size (`vlm:741-769`), matching `ref:141-161`.
- It is used for the attention `q_norm`/`k_norm` (overriding the Qwen3.5 `nn.RMSNorm`, `vlm:1087-1088`), the indexer q/k norms, `hc_norm` and the three PLE norms.
- **No `+1` is folded at sanitize time.** The qwen4 `sanitize` replaces the Qwen3.5 one, which adds `+1` (`vlm/qwen4_exp.py:27-78` vs `qwen3_5.py:144-175`). So there is no double count.
- The DeltaNet gated norm correctly uses plain `w` (`vlm:772-787`).
- Result: Match.

### 6. MoE

| Aspect | Reference | mlx-vlm | Finding |
|---|---|---|---|
| Router | bf16 logits → **fp32** softmax → top-10 → fp32 renormalise → cast (`ref:956-965`) | bf16 logits → `softmax(precise=True)`, **output in bf16** → `argpartition` → renormalise in bf16 (`q35moe:35-44`; decode `q35sv:189-200`) | **P1** (bf16 only) |
| `norm_topk_prob` | Honoured (default True; absent from config.json) | Honoured in the main path; **always normalised** in the decode path (`q35sv:200`) | E11 equivalent here; latent if a config set False |
| Experts | `silu(gate)·up → down`, fused `gate_up_proj` split into first half = gate, second = up (`ref:938-940`) | `split_expert_projection` halves along rows (`switch_layers.py:51-74`); `SwiGLU` = `silu(gate)·up` (`switch_layers.py:225-230`, `activations.py:7-9`) | Match |
| Shared expert and gate | `sigmoid(shared_expert_gate(x))·MLP(x)` (`ref:979-985`) | `vlm:1201-1204`, `q35moe:49-52`, `q35sv:202-206` | Match |

**P1, concrete case** (stdlib bf16 rounding; script in this session's scratchpad). Router logits for one token are `[3.0]×9 + [0.5, 0.50390625] + [−1.0]×501`. The two contenders are adjacent bf16 values.

- fp32 probabilities are 0.0044755833 and 0.0044931001, so the reference deterministically picks expert 10.
- Both round to the same bf16 value, 0.00448608398, so `argpartition` sees an exact tie for the 10th slot and may pick expert 9.
- The same happens with `−1.0` replaced by `0.0`. With `−2.0` the probabilities stay distinct.
- This needs router logits with |l| ≲ 1 at the rank-10/11 boundary. A numerical test must establish how often real weights produce that.

### 7. RoPE

- **Text RoPE.** Partial factor 0.25 → 64 rotary dims of 256; θ = 1e7; `rope_type="default"`, no scaling. `inv_freq = 1/θ^(2i/64)` (`rope_utils.py:1043-1044` vs `ref:105-113`).
- **Pairing.** Half-split pairs `(d, d+32)`, matching `rotate_half` (`rope_utils.py:596-644` vs `ref:618-660`).
- **MRoPE.** Interleaved `[11, 11, 10]` with an identical selector (`rope_utils.py:512-517` vs `ref:129-138`). For text-only input the three position axes are equal, so it reduces to 1-D RoPE.
- **Rounding.** The reference casts cos/sin to bf16 and rotates in bf16 (`ref:127`). mlx-vlm rotates in fp32 and rounds once. This is **E5**: identical in fp32, ≤ 1 bf16 ulp per element in bf16. Here the reference is the less precise side.
- **Positions.** Text positions come from a cumulative sum over the attention mask (`q35:1689-1700`). Generation passes them explicitly from `get_input_embeddings` (`generate/ar.py:427-440`). Batched rows are sliced `[pad:]` (`vlm:1680-1685`), and decode uses per-row real offsets (`q35:1745-1753, 1826-1848`). This is consistent with the reference's left-padded positions.
- Result: Match.

### 8. Cache structures, trim and restore

- **QSA layers: `QSAKVCache`.** Holds the KV plus raw index keys, the full position history and the cached block summaries.
  - `trim` slices the index keys and positions to the KV offset and clears the summaries (`vlm:162-169`).
  - `to_quantized` keeps the indexer state in float (`vlm:257-267`).
  - Batch variant (`vlm:279-625`): merge, extend and extract keep index keys aligned with `BatchKVCache` left padding (`vlm:487-535`, `cache.py:1746-1775`).
  - Equivalent to the reference `update_indexer` + `indexer_position_ids` (`ref:706-707, 1423-1429`).
- **DeltaNet layers: `ArraysCache(4)`.** Slots are `[conv window, fp32 state, PLE conv window, PLE token history]` (`vlm:2226-2233`). Not trimmable (`cache.py:194`).
  - Speculative rollback records recurrent states and window views for **all four** slots. It refuses to commit if any slot changed without a record (`cache.py:934-1198`).
  - Speculative commit trims the append caches (`speculative/cache_state.py:230-288`).
  - Correct by construction for single requests.
- **N1 (latent).** A cached conv state or recurrent state whose batch size does not match is silently replaced with zeros (`q35:1189-1200`, `q35gd:557-561`). This is not reachable in the audited paths, but it would hide a batching bug rather than raise.

### 9. Sanitize and quantization predicates

**Sanitize** (`vlm/qwen4_exp.py:27-78`):

- drops `mtp.*`;
- converts official FP8 shards (`vlm/fp8.py`);
- splits `experts.gate_up_proj` into `switch_mlp.{gate,up}_proj` and moves `down_proj`;
- maps `ngram_embedding.shard_i` → `shards.i`;
- moves the conv axis `[C,1,K]` → `[C,K,1]`, guarded by `shape[-1] != 1`, so it is idempotent;
- maps `model.language_model.*` → `language_model.model.*` (`qwen3_5.py:15-24`);
- applies no norm shift.

All of these are correct.

**Quantization predicate** (`vlm:2235-2247`), **L1**:

- Everything with `to_quantized` is quantized at the global bits. That includes the QSA `index_qk_proj`, the hyper-connection `input_mix_weight_{down,up}` and `block_inject_weight`, DeltaNet `in_proj_{qkv,z,a,b}` and `out_proj`, attention projections, the PLE `key/value_proj`, `embed_tokens` and `lm_head`.
- **The indexer is quantized.**
- **The router (`mlp.gate`) and `shared_expert_gate` are quantized at 8-bit, group 64.**
- The PLE shards use a group-32 fallback; the README's example is 3-bit.
- Convolutions, norms, `A_log` and `dt_bias` are not Linear and stay in float.
- This deliberately trades fidelity for size. A quantized indexer changes which blocks top-k selects. mlx-vlm cannot express the GOAL's "6-bit experts, everything else bf16" without a custom predicate.

**PLE storage**, **L2**: the external PLE store is 4-bit only (`vlm/ple_storage.py:24-27, 316-344`). There is no bf16 paging.

The Sol port's predicate keeps the indexer, router, DeltaNet, convolutions and PLE out of quantization (`qwen4_exp_tables.py:174-199`).

### 10. Left padding and batching

- **Prefill.** Row-wise on unpadded rows, then merged (`vlm:1624-1711`). Equivalent to the reference (E9).
- **Decode / verify with ragged padding.** **D1.**
- **Right padding (APC mixed prefill, P4).**
  - `BatchGenerator` calls `prepare(right_padding, lengths)` on every cache before prefill (`generate/ar.py:2117-2128`).
  - The row-wise path rebuilds each cache with a fresh `merge` (`vlm:1702-1710`). That drops `BatchKVCache._right_padding` and `ArraysCache.lengths`, so the later `finalize()` roll has nothing to act on (`vlm:340-354`, `cache.py:1272-1277`).
  - The PLE windows `update_window(2|3, …)` ignore `lengths` (`vlm:1407, 1482`), unlike the DeltaNet conv window (`q35:1209-1211`).
  - Result: right-pad tokens may remain in the KV and index caches and in the PLE histories. This is unverified end to end because the BatchGenerator flow is large; the test is T5.
- **No cache (P5).** `LanguageModel.__call__` never forwards `mask` to the model (`q35:1898-1905`). The only padding source is the batch cache. A padded batch with `cache=None` therefore gets `"causal"` attention and pad-id PLE hashes (`vlm:1713-1717`). The reference masks pads and maps pad ids to EOS (`ref:1431-1452`).

---

## Tests to run once execution is approved

All tests compare against transformers 5.22.1 `qwen4_exp` (eager attention) on identical weights. "Tiny config" means a fixture like the Sol gold harness:

- hidden size 64, 4 layers `[lin, lin, lin, QSA]`, `ple_layer_ids=[2]`, `hc_count=4`, 8 experts / top-2 + shared;
- **indexer_budget=8, compress_ratio=4**, so `block_topk=2` and sparse attention starts at 12 visible tokens;
- vocab 512 and small n-gram primes.

Run fp32 unless stated. mlx-vlm code runs only after approval, in an isolated venv.

**T1 (D1, definite).** Ragged batched decode drops QSA.

1. Tiny config, fp32. Prompts A (20 tokens) and B (17 tokens), left-padded in one batch through `BatchQSAKVCache` (`left_padding=[0, 3]`). Greedy decode for 4 steps via the batch-invariant path, then via the main path (force a quantized `lm_head` or call `model.language_model.model` directly).
2. Compare each row's logits to (i) mlx-vlm single-request runs of A and of B, and (ii) the transformers left-padded batch with `attention_mask`.
3. **Expected**:
   - single-request vs reference ≤ 1e-4;
   - batched row A vs reference > 1e-3 from the first decode step, because 21 visible tokens give 5 complete blocks, more than 2;
   - instrumentation shows `qsa_mask` built but the SDPA call receiving `"left_padded_decode"`.
4. Repeat with a 3-token verify block (L=3) through `_speculative_verify`.
5. Control: an equal-length batch, A and A, must match the reference to ≤ 1e-4.
6. Real-scale confirmation (optional): the D1 concrete case with real weights at 6-bit or bf16, comparing the QSA layer-3 output for row 0 batched vs single.

**T2 (P1).** Router bf16 tie.

1. Unit level, bf16: one MoE block with `hidden_size=2560`, 512 experts. Set `gate.weight[:, 0] = [3.0]×9 + [0.5, 0.50390625] + [−1.0]×501` and the other columns 0. Input x = e₀.
2. Record:
   - the softmax output dtype (expected bf16);
   - the selected top-10 set from `Qwen3_5MoeSparseMoeBlock` and from `Qwen3_5BatchInvariantForward._feed_forward`;
   - the normalised weights.
3. Reference: `Qwen4ExpTextTopKRouter` on the same bf16 logits.
4. **Bug confirmed** if mlx-vlm selects expert 9 or orders the tie differently. Report the weight differences regardless.
5. Real weights: feed **reference** hidden states (captured at each MoE input) for 2k tokens of fixed text into mlx-vlm's router for all 48 layers. Report the fraction of (token, layer) pairs whose top-10 set differs, and the maximum |Δweight|.
6. Control: the Sol port's fp32 router must match the reference set exactly.

**T3 (P2).** DeltaNet bf16 gating and normalisation drift.

1. Load layer 0 `linear_attn` from the real shards. Use bf16 inputs taken from reference layer-0 hidden states for T = 8192 tokens of fixed text.
2. Compare the per-token output and the final state against the transformers reference (bf16, `torch_chunk_gated_delta_rule`) for:
   - (a) mlx-vlm as-is;
   - (b) mlx-vlm with `softplus(a.f32 + dt_bias.f32)` and fp32 L2 norm patched in a scratch copy;
   - (c) the Sol port.
3. Metrics:
   - relative Frobenius error of the state at T = 512 / 2048 / 8192;
   - max |Δoutput| per 512-token window.
4. **Bug threshold**: (a) error > 2× (b)/(c) and growing with T.
5. Also run fp32 (expected ≤ 1e-5 relative, i.e. equivalent).

**T4 (P3).** QSA ties and near-ties.

1. Constructed zero-score ties (tiny config, fp32): set `index_qk_proj` so the query and pooled keys are anti-aligned for all but one block, e.g. key rows = −query rows. Most block scores are then exactly 0 at 40 tokens (10 complete blocks > 2). Compare the per-query selected token sets from `build_mask` and the reference `selected_token_mask`. Report mismatches; they reflect implementation-defined ties on both sides.
2. Real weights, bf16: capture each QSA layer's `index_qk_proj` input from the reference at 8k context (fixed text). Run mlx-vlm `select_from_projected` on identical inputs and report:
   - the Jaccard overlap of selected blocks per query;
   - the count of queries whose 512th and 513th reference scores are exactly equal (including 0);
   - the minimum relative gap at the cut-off.
3. **Expected**: fp32 overlap = 1.0. bf16 overlap below 1.0 quantifies the effect.

**T5 (P4).** APC right padding.

1. Server or BatchGenerator with APC enabled. Two requests share a cached system prompt but have suffixes of different lengths (e.g. 7 and 3 tokens), so `right_pad_per_row = [0, 4]`.
2. After prefill, inspect the merged caches:
   - `BatchQSAKVCache.kv_cache._right_padding`, offsets and left padding;
   - whether the last 4 index keys of row 1 are pad keys;
   - `ArraysCache` slots 2 and 3 for row 1 vs the windows from a single-request run.
3. Compare greedy continuations with single-request runs (tiny config, fp32, ≤ 1e-4 expected if correct).

**T6 (P5).** Padded batch without a cache.

1. Tiny config, fp32. Call `LanguageModel(inputs, cache=None, attention_mask=mask)` with B=2 and left padding.
2. Compare each row's real-token logits to unpadded single-row forwards.
3. A mismatch confirms that padding is silently ignored without a cache. Classify it as unsupported unless a caller uses this path.

**Regression guards for the "equivalent" claims** (all expected to pass):

- **E-a.** Tiny config, fp32, single request: full-prefill and stepwise-decode logits vs the reference ≤ 1e-4. Cover both the QSA kernel path (bf16 run, bound stated) and the masked-dense fallback (fp32).
- **E-b.** Chunked prefill with `prefill_step_size ∈ {5, 7, 64}`, crossing the 2-block (tiny) sparse boundary inside a chunk. Logits identical to one-shot prefill (≤ 1e-5 fp32). This exercises the block-summary cache.
- **E-c.** QSA cache `trim(n)` + re-prefill equals a fresh prefill. Check that `index_block_keys` is cleared and `index_keys` / `index_position_ids` lengths equal the KV offset.
- **E-d.** PLE hash: for 10k random id sequences, including EOS runs and cached-context continuation, mlx-vlm `Qwen4ExpNGramEmbedding` row ids equal `qwen4_exp_tables.ngram_ids` and the reference ids exactly. This also covers int64 GPU arithmetic.
- **E-e.** Speculative rollback: verify a 3-token block, accept 1, and check that all four `ArraysCache` slots plus the QSA cache equal a non-speculative run.

## What a static audit cannot settle

The following depend on MLX runtime semantics and are covered by the tests above:

- the output dtype of `mx.softmax(…, precise=True)` (T2);
- `mx.argpartition` tie order (T2, T4);
- signed-index wraparound in `put_along_axis` (N2);
- int64 multiply/XOR/remainder on the Metal backend (E-d);
- whether a mismatch in the Metal QSA kernel's `simd_sum` reduction order matters beyond fp32 rounding (E-a).

The BatchGenerator/APC flow (P4) was read only where it touches the caches.
