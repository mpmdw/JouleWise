# qwen4_exp canonical MLX module (P3)

GOAL items 2-4 (`docs/align/qwen4_exp_port/GOAL.md`), phase P3: converge the Sol port and the Opus twin into ONE module, in mlx-lm house style, loaded through mlx-lm 0.31.3's `model_file` hook on the pinned stack (mlx 0.31.2, mlx-lm 0.31.3; no pin bump).

| Artifact | Path |
|---|---|
| Module (one file) | `joulewise/align/models/qwen4_exp.py` (`C:<line>` below) |
| Converter | `scripts/align_convert_qwen4_exp.py` |
| Tests | `tests/align/test_qwen4_exp_canonical.py` |

Sources, all read-only:

| Tag | Source |
|---|---|
| `S:` | Sol port, `lane/2026-11-05-align-flashnext-port` @ 28d153449, `joulewise/align/models/qwen4_exp.py` (`qwen4_exp_tables.py` as `ST:`, converter as `SC:`) |
| `T:` | Opus twin, `lane/2026-11-05-align-flashnext-twin` @ ad56248a5, `joulewise/align/models/qwen4_exp_twin.py` |
| `P:` | perf track, PR #670 `lane/2026-11-05-qwen4exp-port-perf` @ 1aeb9ff88, `joulewise/align/models/qwen4_exp_kernels.py` |
| `D0`-`D10` | the differential, `differential_sol_vs_twin.md` (binding recommendation) |
| `HF:` | transformers 5.22.1 `models/qwen4_exp/modeling_qwen4_exp.py` |

The mlx-vlm audit's D1 (ragged-batch QSA discards the selection), P1 (bf16 router ranking) and P2 (bf16 DeltaNet gating) are avoided by construction; no mlx-vlm code was copied. Community PR #1788 was neither read nor run.

## Per-component provenance

Every row follows the differential's convergence table ("Adopt" column) and the P3 brief. `C:` cites the canonical module.

| Component | Canonical | Taken from | Why (differential item) |
|---|---|---|---|
| File layout: `TextModelArgs` + validation, `ModelArgs(text_config)`, `Model.language_model`, `sanitize` | C:84-254, C:1947-2054 | twin T:66-217, T:1455-1524 | mlx-lm house style for a VLM checkpoint's text path (`qwen3_5.py`); one file under the sha256 pin (Sol's sibling `qwen4_exp_tables.py` is folded in) |
| Legacy top-level `rope_theta` / `partial_rotary_factor` folded into `rope_parameters`; `rope_scaling` refused | C:131-149 | new (review finding) | `BaseModelArgs.from_dict` would drop them silently |
| Weight names HF -> MLX, mtp / vision dropped | C:1850-1867 | twin T:1385-1403 | |
| n-gram hash buffers checked against the config at load and conversion | C:1882-1890, C:2000-2003 | Sol S:651-657 | catches a hash-layout drift instead of silently mis-hashing |
| n-gram ids: `NgramHashSpec` (splitmix multipliers, primes, `_shift_right_ignore_eos`, decode fast path) | C:268-387 | twin T:232-357 | same ids as Sol (PLE agrees to 7e-7 fp32) |
| n-gram table: `NgramTable` (f32/bf16/q8/q4 records, mmap or `F_NOCACHE` pread, dedupe, fault counters, optional byte offset inside a larger file), never GPU-resident | C:397-584 | twin T:364-548 | GOAL item 6: the bf16 table stays on disk, paged. Prefetch advises pages relative to the mapping's real start (round 1) |
| RMSNorm `(1 + w)`, grouped | C:605-622 | twin T:556-577 (`mx.fast.rms_norm` on fp32) | same math as HF:143-163, fused |
| Gated RMSNorm (DeltaNet output) | C:625-642 | twin T:580-595 | HF:170-187 rounding order (norm rounded to dtype, times weight, times fp32 gate) |
| RoPE inverse frequencies, float64 pow rounded once | C:650-663 | twin T:649-667 | D2: 32/32 entries equal to the reference at the released config (rope_theta 1e7, rotary_dim 64; Sol 15/32 differ). At the released config only: the recipe is not torch's fp32 pow in general (63/64 at theta 1e6, rotary 128), so re-verify inv_freq bitwise for any other theta / rotary_dim |
| RoPE application: explicit rotate-half, cos/sin cast to the model dtype, computed once per forward | C:666-685, C:1202-1223 | twin T:670-686, T:833-847 | perf critic HIGH: `mx.fast.rope` changes bf16 indexer selection; used in main attention too (the bitwise-exact choice) |
| sigmoid: fp32, rounded once, ALWAYS (no `jw_bf16_fp32_ops` flag) | C:599-602; sites: HC C:1245, C:1251, attention gate C:1536, DeltaNet beta C:1038, shared-expert gate C:1648, PLE C:1684 | Sol S:229-233 | D3: torch evaluates bf16 sigmoid in fp32; `mx.sigmoid` on bf16 differs on 3% |
| silu: fp32, rounded once, everywhere | C:592-596; sites: DeltaNet conv C:1300, PLE conv C:1697, HC C:1244, experts C:1605, shared expert C:1583 | twin T:627-636 + new sites | D4 (conv), D5 (HC), expert/shared SwiGLU (both ports used bf16 `nn.silu` / mlx-lm `swiglu`) |
| Hyper-connection | C:1226-1252 | Sol S:263-279 structure; fp32 stream mean (both, T:871) | D3, D5 |
| DeltaNet short conv: `mx.conv1d` (`nn.Conv1d`, groups = C) | C:1273, C:1300 | Sol S:282-287 | bit-identical to the fp32 sum rounded once and ~4x faster than the twin's tap loop (perf §2) |
| DeltaNet recurrence: perf eps adapter `Dk**-0.5 * rms_norm(x, 1e-6/Dk)` on mlx-lm's unchanged `gated_delta_kernel`; fp32 softplus/decay (mlx-vlm P2); beta rounded once | C:1020-1047 | perf P:71-146 (its `gdn_gates` bf16 `mx.sigmoid` replaced by the rounded-once sigmoid) | exact identity of HF l2norm (HF:247-250, 296-301); fused |
| Mask-aware DeltaNet seam: masked steps leave the state unchanged; mask from `create_ssm_mask(h, cache)` | C:1283-1310, C:1826 | Sol S:243-260, S:320-342 | equals HF's zeroed inputs for left padding from a zero state |
| QSA indexer scores `sum_h relu(q_h . kb) / sqrt(Di)` in fp32 | C:1389-1394 | twin T:1052-1056 (layout of perf P:317-326) | D7: the rounded quotient decides which near-equal scores tie |
| QSA tie rule: score desc, block asc, as a mask (`partition` + `cumsum`), no host sync | C:688-704, C:1423 | twin T:689-707 | D0: same set as Sol's rule; Sol's `qsa_topk` synced `mx.any(...).item()` per QSA layer per call (S:363) |
| QSA per-block key cache: pooled + normed + roped once per completed block, per-row padding phase, exact under trim; the raw-key and block-key writes are tied to the layer output (`mx.depends`), so they run with their own token even when no query reads them | C:804-929 (`Qwen4ExpQSACache`), C:1346-1376, C:1538-1545 | twin T:715-787, T:986-1007 (the perf design, P:711-777) | Sol recomputed every block key on every call (S:397-404). Round 1: without the tie, dense-regime writes piled up unevaluated and ran in one burst at the first sparse token (mlx-lm #1662 class) |
| QSA attention core + policy: dense causal while every query sees <= K blocks; masked SDPA below `qsa_sparse_prefill_min_kv` (6144); block-sparse Metal prefill kernel above; decode: masked SDPA below `qsa_sparse_decode_min_kv` (8192), gather + SDPA above. No prefill cap. | C:1055-1199, C:1396-1496, C:1547-1570 | perf P:445-708 (kernel source verbatim, P:523-590) | replaces both ports' cores (same function; Sol's per-query gather and the twin's masked SDPA are O(S x L)); Sol's 64-token `jw_max_prefill_tokens` cap is gone |
| Token lists for the kernel / decode gather, with per-row left padding and a self slot for pad queries | C:1480-1496 | perf P:483-509, generalised | perf open issue 3 (left-padded batches) and mlx-vlm D1 (ragged decode keeps the selection) |
| MoE router: fp32 softmax, `argpartition` on fp32 probabilities, fp32 renorm, cast | C:1634-1642 | both (identical) | mlx-vlm P1; perf §4 |
| MoE experts: fused `gate_up_proj` [E, 2I, H] (`SwitchLinear`, so load-time `gather_qmm` quantization applies), silu rounded once | C:1586-1608 | perf P:814-861 + new silu | two gathers per token instead of three |
| MoE combine: k weighted rows summed in fp32, rounded once | C:1647 | twin T:1195 | D6: the reference's default `grouped_mm` experts path (transformers `moe.py`) |
| PLE gate: bf16 product, fp32 sum rounded once, fp32 division by sqrt(hidden) rounded once | C:1681-1682 | twin T:1224 sum + new divide | D8: MLX rounds a Python divisor to bf16: sqrt(2560) = 50.596 becomes 50.5 at the released hidden size 2560 (the released `config.json`; 2048 is only the HF config class default), changing 35.9% of all bf16 values in [2^-8, 2^8) (36.5% of the differential's gate values) |
| PLE dilated conv + mask | C:1652-1697 | Sol S:536-561 (`nn.Conv1d(dilation)`) + twin T:1215-1242 (mask, history) | |
| Caches: cache-carried left padding on mlx-lm's `ArraysCache(left_padding)` / `make_mask` / `advance` protocol; `left_padding` derived on the host from `padding - offset` | C:727-801, C:948-958 | twin T:715-799 (`make_cache(left_padding)`) rebuilt on the mlx-lm protocol | house style (`create_ssm_mask`). Round 1: the inherited lazy `left_padding -= n` grew one graph node and Metal buffer per step on every non-first linear layer (mlx-lm #1632) |
| Caches: serializable `state` / `meta_state`, registered in `mlx_lm.models.cache` for `load_prompt_cache`; dispatch on the `qwen4_exp_cache` format marker, never class identity | C:774-791, C:873-906, C:937-946 | Sol S:131-198 | ALIGN prefix reuse; the twin's `QSACache.state` setter raised (T:782-784). Round 1: every load rebinds the registered classes, so two loaded models must interoperate |
| Snapshot / restore (hybrid prefix rewrite) | C:965-1010 | twin T:802-825, extended to the ArraysCache padding counters | Round 1: every entry (layer count and kind, one offset, QSA not forward in time, padding, batch size) is checked before anything is mutated |
| Precision profiles `maxfit` (6-bit g64 experts, all else bf16, bf16 n-gram on disk) / `maxfit5` / `bf16` / `fp32` / `mixed` | C:1896-1939 | Sol ST:157-222; `mixed` keep-float list = twin T:1421-1447 + Sol's | GOAL precision target. Evidence: maxfit and maxfit5 under bound (f); `mixed` (lossy, no reference bound) checked for layout, q4 codec bound, finiteness and cosine (needs `--ngram-group-size` dividing the n-gram head dim) |
| Converter: streaming header inventory, raw bf16 passthrough, bounded row slices, tensors packed into shards of at most 4 GiB, sha256 manifest (files and 256 MiB chunks hashed in parallel, `F_NOCACHE`) + verify, maxfit; `load_verified_model` requires the manifest pin and the module pin and runs the module from its hashed bytes | `scripts/align_convert_qwen4_exp.py` | Sol SC (whole structure) | twin's converter could not read bf16 (D1). Round 1: one file per tensor (1163 open fds), an optional pin, path-based module import and single-threaded hashing were fixed |


## Deviations and decisions

1. **Router fold not adopted.** The recommendation's MoE row also suggests folding `shared_expert_gate` into the router matmul (513 rows, perf §4). Not done: it renames the router parameter away from the reference's layout, perf §4 measures the router as negligible, and a 513-wide GEMM was not shown bitwise-equal to the 512-wide one. Deferred to P5 (performance), where it can be measured on the Mac.
2. **RoPE in main attention stays explicit.** The recommendation allows `mx.fast.rope` in main attention only if a bf16 parity run accepts it. The explicit HF-exact form is bitwise in isolation and costs nothing measurable at this size, so it is used everywhere.
3. **No runtime caps.** Sol's `jw_max_prefill_tokens` (64, a consequence of its O(S x budget) per-query gather) and `jw_context_cap` (40,960) are dropped. Prefill chunking is mlx-lm's `prefill_step_size`; the context cap belongs to the runner's `max_tokens`, as in mlx-lm house style.
4. **Dispatch thresholds are config fields** (`qsa_sparse_prefill_min_kv`, `qsa_sparse_decode_min_kv`, defaults 6144 / 8192 from the M4 crossovers), so the Mac re-measurement (perf §9) needs no code change. Every path computes the same function (tests (d), (g)).
5. **Perf kernels generalised to left padding.** The perf track assumed unpadded rows (perf open issue 3). Token lists and masks here carry each row's padding phase, and pad queries attend to themselves (outputs discarded, kept finite). Test (d) runs a left-padded batch through the kernel and the gather path against the reference.
6. **Fused-norm rounding at hidden 192.** The recommendation's fused `mx.fast.rms_norm` (twin) leaves ~0.1% one-ulp bf16 flips in the hyper-connection stream mix at hidden 192. Sol's explicit norm is no better (probed on the captured inputs: 0.99935 vs 0.99909), so it is fp32 reduction order inside the 192-wide RMS; the prototype's 1.000 was measured at hidden 96. The floor is 0.998, and the weights path is 1.000.
7. **Router ties.** `argpartition` and `torch.topk` both leave ties unspecified, and torch's CPU order among tied experts is not reproducible (on 458 tied rows of a synthetic 512-expert router it took the lowest index 227 times, the highest 215 and another 16), so no deterministic port rule can match it. A tied swap selects a different expert of equal weight. **At the released scale ties are common, not rare** (validation round 1): the real-weight parity seat's bf16 prefill has exact k-th = (k+1)-th probability ties on **8 of 54 router rows at layer 2 in the official model (7 in the canonical port)** and 5 of 54 (official) / 3 (canonical) at layer 3, 0 in fp32; every one of the 6 expert-set flips at layer 2 is such a tie. A synthetic router at hidden 2048, 512 experts, top-10 with bf16 logits ties on 11-15% of rows. On this suite's 8-expert fixture the bf16 reference ties on far fewer rows (test (e)), which understated the real rate. Real-weight parity (P4/P11) must compare router expert sets modulo exact ties and log both tie rates; a deterministic tie rule on both sides (score descending, index ascending, as `TopkSpy` already does for the indexer) is the way to make bf16 end-to-end comparisons expert-exact.
8. **Converter imports mlx.** The shared rules (names, expected shapes from the module's own lazy parameters, precision policy, n-gram record format) come from the module, so even unquantized conversion imports mlx; Sol's numpy-only path is gone. Sol kept a second, independent parameter enumeration (`parameter_shapes`); here the strict inventory check is against the module itself, which is what `load_model(strict=True)` enforces anyway.
9. **n-gram record format** is the twin's (`NgramTable`: f32 / bf16 / q8 / q4 with fp16 scales), not Sol's (f32 scales). maxfit uses bf16, where both formats are the raw bf16 bits.
10. **Unsupported, failing loudly:** the whole BatchGenerator cache protocol, `filter` / `extend` / `extract` / `merge` / `prepare` / `finalize`, on both cache classes (cache-carried padding and the indexer state; round 1 closed `extract` / `prepare` / `finalize`, which were inherited and silently wrong), setting `left_padding` from outside, `input_embeddings` (PLE needs token ids; same as twin), KV-cache quantization (it would drop the indexer state).
11. **Bound for (f).** "Quantized vs bf16 within the bound" is made testable as (b)'s bound on the same weights. The maxfit (or maxfit5) model must equal the fp32 reference run with the SAME dequantized expert weights (dequantized in fp32, the kernel's own `scale * q + bias`) within 1.25x that reference's own bf16 error: the bf16 reference with those weights vs the fp32 one. Round 1 replaced the earlier denominator, the unquantized model's bf16 noise, which does not cover bf16 flips of near-tied experts that the quantized weights happen to create. The quantization effect itself (vs the bf16 port) is measured and reported, not bounded: it is a property of the recipe, not of the port.
12. **Attention core rounding is the backend's** (validation round 1, replacing the earlier "reference artifact" reading of D9). The port calls `mx.fast.scaled_dot_product_attention` and its own block-sparse kernel. On identical bf16 inputs (probe `qsa_core_probe.py`, QSA-like masks, 40 and 320 queries):
    - MLX's fused SDPA at head_dim 64, MLX's decode kernel (any head_dim) and the block-sparse kernel keep fp32 scores and fp32 probabilities through P.V: 0.9998-1.0 bitwise against an fp32-score, fp32-probability eager core.
    - torch's CPU bf16 SDPA rounds the unnormalised probabilities exp(s - m) to bf16 before P.V, inside a blocked online softmax: 0.958 (40 queries) / 0.847 (320) against that emulation, 0.61-0.68 against MLX. It is reproducible across thread counts and batch composition (Fable), so it is not reference noise.
    - MLX's unfused fallback at head_dim 256 (the released config's prefill) rounds scores and probabilities to bf16, exactly HF's `eager` order: 1.0 / 0.9998 against it.

    Matching torch's kernel bitwise would need an unfused core that reproduces its blocking, so the port keeps the backend's order (more precise than torch's at head_dim 64). Test (c) gates the QSA layer against the same layer with an fp32-probability core (`Fp32ProbabilityAttention`). For P4 at the released config: prefill can match an `eager` reference's core bitwise and decode an fp32-probability core; neither matches torch `sdpa` bitwise.

## Test evidence

`tests/align/test_qwen4_exp_canonical.py`: **31 tests, all pass** (18 parity tests in `CanonicalParityTest`, 13 validation-round-1 regressions in `ValidationRound1Test`). Native run in `/private/tmp/jwsol/venv-both` (mlx 0.31.2, mlx-lm 0.31.3, torch 2.15.0, transformers 5.22.1), under `nice -n 20 taskpolicy -b`, `OMP_NUM_THREADS=2`, `TMPDIR=/private/tmp/jwcanon`. Peak RSS 914 MiB. The full run that built the torch reference (v6) took 187 s, 89 s of it the reference. The confirmation rerun at the final test commit, with the reference cached, took 58 s (peak RSS 845 MiB).

Fixture: one tiny random `Qwen4ExpForConditionalGeneration` (vision tower included), saved in bf16 with `max_shard_size="200KB"` in the released serialization: `model.language_model.*`, per-expert `mlp.experts.{e}.*`, n-gram `shard_{0..3}` plus hash buffers, and a fake `mtp.*` file. It is converted by the canonical converter (fp32, bf16, maxfit, maxfit5, mixed), and every model is loaded through `load_verified_model` with the manifest sha256 recorded at conversion and the converter's module pin.
- Text config: 8 layers (DeltaNet x3, QSA, DeltaNet x3, QSA); hidden **192** (sqrt not bf16-representable, a multiple of 64 for the maxfit recipe); hc 4; 4 q / 2 kv heads of 64; partial rotary 0.25.
- QSA indexer: 4 x 32 with budget 16 / ratio 4 (top-4 blocks: 21 of the 40-token prompt's queries drop blocks).
- DeltaNet 2 k / 4 v heads of 32; MoE 8 experts top-3; PLE at layers 2 and 5 (`ple_layer_index` 0 and 1); EOS inside every prompt.
- The references are built as `from_pretrained` builds them (fp32 RoPE `inv_freq` in both dtypes, checked buffer by buffer). The experts implementation resolved to `grouped_mm`.

Scenarios:
- `prefill` (40 tokens), `stepwise` (one token at a time), `chunked` (7-token chunks).
- `padded_row0/1`: a left-padded batch with **5** pads (not a multiple of the ratio), then 4 cached decode steps; the reference uses `attention_mask` and `position_ids = cumsum - 1`. `padded_chunked_*` is the same batch prefilled in 7-token chunks.
- `long_prefill` / `long_decode` / `long_chunked`: 320 tokens; prefill 304 then 16 decode steps; 64-token chunks.
- `longk_prefill`: 4101 tokens.
- greedy: 32 tokens.

### (a) fp32 gold parity: port vs REF, max abs logit difference (bound 1e-4; logit scale ~3.8)

| scenario | max abs | cos | top-1 |
|---|---:|---:|---:|
| prefill | 3.76e-06 | 1.000000 | 1.000 |
| stepwise | 3.71e-06 | 1.000000 | 1.000 |
| chunked | 4.29e-06 | 1.000000 | 1.000 |
| long_prefill | 7.15e-06 | 1.000000 | 1.000 |
| long_decode | 2.52e-06 | 1.000000 | 1.000 |
| greedy_logits | 2.15e-06 | 1.000000 | 1.000 |
| padded_row0 | 3.87e-06 | 1.000000 | 1.000 |
| padded_row1 | 6.32e-06 | 1.000000 | 1.000 |
| padded_chunked_row0 | 5.17e-06 | 1.000000 | 1.000 |
| padded_chunked_row1 | 5.84e-06 | 1.000000 | 1.000 |
| long_chunked | 9.78e-06 | 1.000000 | 1.000 |

Greedy, 32 tokens:
- fp32: port == REF on **32/32** tokens.
- bf16: no divergence from REF bf16 (identical 32/32).
- Also identical through mlx-lm's `generate_step` with 16-token prefill chunks.

### (b) bf16 bound (port vs REF fp32 <= 1.25x noise; port vs REF bf16 <= 1.5x noise; noise = REF bf16 vs REF fp32)

Re-measured against the corrected bf16 reference (validation round 1, N1). The earlier reference rounded RoPE `inv_freq` to bf16, which inflated the noise at long context (0.3132 at 320 tokens, now 0.2351), so the earlier margins were too generous.

| scenario | noise | port vs REF fp32 | ratio | port vs REF bf16 | ratio |
|---|---:|---:|---:|---:|---:|
| prefill | 0.0730 | 0.0700 | **0.96** | 0.0703 | **0.96** |
| stepwise | 0.0730 | 0.0739 | **1.01** | 0.0703 | **0.96** |
| chunked | 0.0730 | 0.0697 | **0.96** | 0.0781 | **1.07** |
| long_prefill | 0.2351 | 0.2351 | **1.00** | 0.2168 | **0.92** |
| long_decode | 0.1375 | 0.1092 | **0.79** | 0.1250 | **0.91** |
| long_chunked | 0.2351 | 0.2516 | **1.07** | 0.2344 | **1.00** |
| padded_row0 | 0.0730 | 0.0677 | **0.93** | 0.0703 | **0.96** |
| padded_chunked_row0 | 0.0730 | 0.0697 | **0.96** | 0.0703 | **0.96** |
| padded_row1 | 0.2883 | 0.2004 | **0.70** | 0.0938 | **0.33** |
| padded_chunked_row1 | 0.2883 | 0.2004 | **0.70** | 0.0938 | **0.33** |
| longk_prefill (4101) | 0.3770 | 0.3768 | **1.00** | 0.3350 | **0.89** |

### (c) isolated components, bf16: minimum over layers of the fraction of elements bitwise equal to the reference

| component | canonical | differential prototype (hidden 96) | gate |
|---|---:|---:|---:|
| attn_hc.mixed | 1.000 | 1.000 | 0.998 |
| attn_hc.weights | 1.000 | 1.000 | 0.999 |
| mlp_hc.mixed | 0.999 | 1.000 | 0.998 |
| mlp_hc.weights | 1.000 | 1.000 | 0.999 |
| DeltaNet | 0.991 | 0.969 | 0.95 |
| ple | 1.000 | 1.000 | 0.999 |
| QSA whole layer vs torch's SDPA core | 0.530 (L3 0.555) | 0.457 | reported (deviation 12) |
| QSA whole layer vs an fp32-probability core | 0.996 (L7 0.9995) | - | 0.99 |
| router.logits | 0.997 | 1.000 | 0.99, and every flip explained |
| expert sets | 0.975 | 1.000 | every difference an exact tie |
| moe (rows with equal expert sets) | 0.999 | 0.999 | 0.99 |
| mixer | 1.000 | 1.000 | 0.999 |
| head | 0.9998 | 1.000 | 0.999 |
| QSA block selection, rows differing (L3, L7) | 0/21, 0/21 | 0/21, 0/21 | 0 |

Router and expert-set differences against the corrected reference: one router logit at L7, 1 bf16 ulp, where the dot product cancels. Its exact value is 5.7e-05 and sum |terms| = 13.8, so the fp32 accumulation bound is 1.6e-4 and either rounding is legitimate. One expert-set row at L5 is an exact k-th = (k+1)-th probability tie with identical logits. Both are explained by rule, and an unexplained difference fails the test. fp32 isolated: every component within 9.54e-07 of the reference.

### (d) port-internal invariants (max abs)

| invariant | fp32 | bf16 |
|---|---:|---:|
| prefill_vs_stepwise | 4.05e-06 | 0.0352 |
| prefill_vs_chunked | 4.22e-06 | 0.0781 |
| long_prefill_vs_chunked | 5.78e-06 | 0.2383 |
| padded_chunked_vs_oneshot | 5.01e-06 | 0.0430 |
| padded_row0_vs_batch1 | 3.81e-06 | 0.0703 |
| padded_row1_vs_batch1 | 4.53e-06 | 0.0000 |

Snapshot / detour / restore / re-prefill (QSA trim + DeltaNet restore), short (40) and long (320, sparse QSA, partial block trimmed) prefixes, fp32 and bf16: max abs 0.0 (bitwise); DeltaNet states bitwise after restore. Prompt-cache `save_prompt_cache` / `load_prompt_cache` round trip (single row, a left-padded batch, fewer tokens than one block): bitwise.

Sparse paths forced (both thresholds 0), against REF fp32:
- Left-padded batch prefilled one-shot through the Metal kernel (2 calls): rows 4.89e-06 / 7.87e-06.
- The same batch in 7-token chunks (8 kernel calls): 5.17e-06 / 5.25e-06.
- Decode through the gather path (8 calls each).
- One row decoded 16 steps through the gather path (32 calls, 8 through the one-row `mx.take` branch): 3.56e-06.

### (e) ties

| count | fp32 | bf16 |
|---|---:|---:|
| REF QSA top-k calls / straddling exact ties (all scenarios) | 1918 / 8 | 1918 / 8 |
| REF router rows / exact k-th = (k+1)-th fp32-probability ties | 7928 / 0 | 7928 / 31 |
| REF 4101-token prefill: QSA calls / ties | 8196 / 0 | 8196 / 0 |
| forced-tie probe (indexer projection zeroed): REF straddling ties | 21 | - |

- Port side (diagnostic `record_selection`) on the 40-token prompt: straddling ties per QSA layer {'3': 1, '7': 0}; sparse queries {'3': 21, '7': 21}.
- Port vs REFdefault (torch's own CPU tie order): prefill 3.76e-06, long prefill 0.1223. REF vs REFdefault: 0.00e+00 and 0.1223. The whole difference is the tie order.
- Forced-tie probe: port vs REF (lowest index) 3.76e-06.
- The router tie rate here (31 of 7,928 bf16 rows, 8 experts) understates the released model's (deviation 7).

### (f) expert-quantized profiles vs the bound

The bound is (b)'s on the same weights. The quantized port vs the fp32 REF with the same dequantized experts (dequantized in fp32, exactly the kernel's `scale * q + bias`) must stay within 1.25x that reference's own bf16 error (the bf16 REF with those weights vs the fp32 one). Round 1 corrected two things in the earlier version of this test:
- It used the unquantized model's noise as the denominator. That fails maxfit5 (1.95) on four bf16 flips of near-tied experts (fp32 margins 4e-5 to 3e-3), three of which the reference's own bf16 run makes too.
- It used bf16-rounded dequantized weights (5.6e-3 off the kernel's).

| profile, scenario | port vs REF-q fp32 | REF-q's own bf16 error | ratio (<= 1.25) | ratio to the unquantized noise (old denominator) | quantization effect: vs bf16 port | REF-q fp32 vs REF fp32 |
|---|---:|---:|---:|---:|---:|---:|
| maxfit (6-bit) prefill | 0.0580 | 0.1181 | **0.49** | 0.79 | 0.1836 | 0.1986 |
| maxfit stepwise | 0.0758 | 0.1474 | **0.51** | 1.04 | 0.2031 | 0.1986 |
| maxfit long_prefill | 0.2042 | 0.2568 | **0.79** | 0.87 | 0.2656 | 0.2602 |
| maxfit5 (5-bit) prefill | 0.1422 | 0.1344 | **1.06** | 1.95 | 0.2109 | 0.2046 |
| maxfit5 stepwise | 0.1370 | 0.1344 | **1.02** | 1.88 | 0.1641 | 0.2046 |
| maxfit5 long_prefill | 0.2312 | 0.2895 | **0.80** | 0.98 | 0.2603 | 0.2396 |

Both profiles load as exactly 16 `QuantizedSwitchLinear` (6-bit / 5-bit, group 64), with everything else float.

`mixed` is a lossy recipe with no reference-derived bound. Converted with `ngram_group_size=16` (the fixture's n-gram head dim is 16; the default 32 is refused before anything is written), it gives:
- a loaded quantization layout equal to the policy module by module: 54 quantized modules, experts 4-bit, other wide linears including `lm_head` and `embed_tokens` 8-bit, router / indexer / DeltaNet / hyper-connection / conv float;
- q4 n-gram records within the codec bound of the bf16 source rows;
- finite logits, prefill vs REF fp32 cos 0.9959 (gate 0.99), top-1 0.85.

The n-gram record codec: f32 and bf16 exact; q8 / q4 within half a step plus the fp16 rounding of scale and bias, per group (groups 16 / 32 / 64).

### (g) 4101-token sparse prefill through the block-sparse Metal kernel

| comparison | fp32 | bf16 |
|---|---:|---:|
| kernel path vs transformers (dense SDPA under the QSA mask, REF tie rule) | 8.20e-06 | - |
| port dense-masked SDPA path vs transformers | 7.39e-06 | - |
| kernel path vs port dense-masked path | 4.05e-06 | 0.1680 (cos 0.999995) |
| 1024-token chunked kernel prefill vs one shot | 3.01e-06 | 0.0156 |
| port bf16 vs port fp32 (scale of bf16 error at this length) | - | 0.3768 |

Kernel calls: 2 (both QSA layers); dense-masked calls in the comparison model: 2. The port's bf16 4101-token prefill against both references is in (b).

### Validation-round-1 regressions (`ValidationRound1Test`)

| test | result |
|---|---|
| dense-regime indexer writes run with their token (budget 1024, 400 decode steps, logits-only evaluation) | 0 deferred graph nodes at 100 / 200 / 400 steps; residual active-memory growth 0 B |
| long padded decode (1536 steps, active memory every 32) | 0 `left_padding` chain nodes; growth rate -3.0 to 0.8 B/step beyond the caches' own bytes over four runs (gate 8; the old chain: 18.4) |
| load_verified_model pins | missing / empty / re-pinned manifest, lying `module_sha256`, missing module pin: all refused, tampered code never runs |
| artifact after a plain mlx-lm load | verifies (bytecode reported, never run); planted `.pyc` not run; symlink / nested / changed files refused |
| refused restore | cache unchanged, continuation bitwise |
| BatchGenerator protocol | 12 / 12 `NotImplementedError` |
| two loaded module copies | snapshot / restore / decode bitwise on reloaded foreign-class caches |
| kernel with 3 / 7 / 8 indices; 2-token chunk through the kernel | within 1e-5; == dense path within 2e-5 |
| n-gram table 100000 bytes into a file | mmap and pread rows bitwise with prefetch |
| shards | 1 file at the default 4 GiB; 39 at 256 KiB, bitwise-identical logits; +3 fds held by a lazy load |
| manifest hashing | plain sha256 up to 256 MiB, chunked above; files and chunks hashed concurrently; `F_NOCACHE` on every range; pre-round-1 manifests verify |
| bf16 reference buffers | `inv_freq` fp32 in both references, every buffer equal to `from_pretrained`'s |


## Components where the fixes did not reach a bitwise result

- **QSA attention core** (whole QSA layer 0.555 / 0.530 bitwise against torch's SDPA in bf16): a systematic rounding-order difference inside the attention kernels, deviation 12; not a reference artifact (the earlier reading of D9 was wrong: torch's CPU SDPA is reproducible). Against the same layer with an fp32-probability core it is 0.996 / >= 0.999 (gated at 0.99), and the block selection is identical.
- **Hyper-connection stream mix**: 0.999 rather than the prototype's 1.000 (about 1 bf16 ulp on 0.1% of elements) at hidden 192, from fp32 reduction order (deviation 6). The MoE matches the prototype (0.999 on rows with equal expert sets); the HC weights path, PLE and mixer are 1.000, the head 0.9998.
- **Router logits and expert sets**: 0.997 and 0.975, against the prototype's 1.000 / 1.000. Against the corrected reference, one logit flips by 1 ulp under cancellation (fp32 accumulation order) and one row's expert set is an exact probability tie; neither is a port difference (test (c) explains each by rule).
- **DeltaNet**: 0.991 (the prototype reached 0.969): the fp32 state recurrence runs in a different order from torch's chunked rule.

None of these moves the end-to-end bf16 result outside the bound: worst ratios are 1.07 (vs fp32 REF, bound 1.25) and 1.07 (vs bf16 REF, bound 1.5), against the prototype's 1.01 / 1.05 and Sol's 1.15 / 1.05 at hidden 96 (and the round-0 1.09 / 1.07 against the uncorrected bf16 reference).

## Validation round 1

Four seats validated the PR head `ce911c6e7` (module sha256 `55aecaea…b11a37f`): real-weight parity (ADMIT), adversarial numerics, adversarial systems, and a Fable cold checkpoint pass (all ADMIT_WITH_FIXES). The seats returned 17 findings, plus an adversarial verification of the systems HIGH, which came back REAL. Findings, probes and outputs: `/private/tmp/jwcanonval/` (`findings-all.json`; the round's own probes: `/private/tmp/jwcanon/r1/`). Every finding is fixed or corrected. Each code fix has a regression test, `ValidationRound1Test` unless noted, that fails on the code before the fix (shown per commit) and passes after it. For the two findings that were gaps in coverage, not defects, a mutation check shows the new test catching a bug the old suite missed.

| # | Seat | Severity | Finding | Disposition | Commit | Regression (before → after) |
|---|---|---|---|---|---|---|
| S1 | systems (verified REAL) | HIGH | QSA indexer writes (raw keys, block pooling / norm / RoPE) not on the logits graph in the dense regime (< budget + ratio = 2052 tokens) or between block completions: deferred, then one burst at the first sparse token, or dropped | fixed: `mx.depends(out, [raw_keys, block_keys])` in `QSAAttention` | 4b491b2e4 | `test_r1_dense_regime_indexer_writes_run_with_their_token`: 6106 deferred nodes, +194 KB residual over 300 steps → 0 nodes, +1 KB |
| S2 | systems | MEDIUM | `Qwen4ExpLinearCache.advance`'s lazy `left_padding -= n` (mlx-lm #1632): an unbounded chain on every non-first linear layer of a padded batch | fixed: `left_padding` derived from host `padding - offset`; advance moves only the offset; external set refused | 3e5194e41, 5da65e001 | `test_r1_long_padded_decode_memory_does_not_grow` (1536 steps, active memory every 32, growth rate fitted between cache-capacity steps): chain nodes growing to 2370, 18.4 B/step → 0 nodes, -3.0 to 0.8 B/step |
| S3 | systems | MEDIUM | `load_verified_model(dir, None)` loaded a re-signed tampered module and ran it; `module_sha256` never checked | fixed: manifest pin and module pin (`MODULE_SHA256`) both required, fail closed; `module_sha256` == the `qwen4_exp.py` entry == the pin; the test fixture now loads every model this way | 35bba4fd5 | `test_r1_load_verified_model_requires_both_pins`: tampered module loaded and ran (pin None, and re-pinned) → refused before any code runs |
| S4 | systems | LOW | `restore_cache` mutated linear caches before meeting a forward-in-time QSA entry (half-restored cache) | fixed: every entry validated first (count, kinds, one offset, QSA direction, padding, batch) | f9b8ad79a | `test_r1_refused_restore_leaves_the_cache_untouched`: offsets [40,40,40,20,...], padding mismatch accepted → ValueError, cache unchanged, continuation bitwise |
| S5 | systems | LOW | block-sparse kernel failed to build for < 8 token-list entries (`constant` vs `device` address space) | fixed: `auto ip` | 8c1213aac | `test_r1_sparse_kernel_with_fewer_than_8_indices`: process abort (Metal library build) → 3 / 7 / 8 indices within 1e-5, a 2-token chunk through the kernel == the dense path |
| S6 | systems | LOW | `extract` / `prepare` / `finalize` inherited and silently wrong; QSA cache lacked them (AttributeError); "fails loudly" relied on an mlx-lm internal | fixed: the whole BatchGenerator protocol raises on both classes | 64d575909 | `test_r1_batch_generator_protocol_fails_loudly`: 5 AttributeErrors + 2 silent accepts → 12 NotImplementedErrors |
| S7 | systems | LOW | one safetensors file per tensor (1163 on the released structure), all held open by `load_model` | fixed: tensors packed into ≤ 4 GiB shards (`--shard-gb`) | 8a65076b5 | `test_r1_converter_packs_shards_and_bounds_open_files`: 209 files (214 fds in the seat's probe) → 1 file, +3 fds for a lazy load; 39 small shards give bitwise-identical logits |
| S8 | systems | LOW | each load rebinds `mlx_lm.models.cache.Qwen4Exp*Cache`; another model's `snapshot_cache` refused the reloaded caches | fixed: dispatch on the `qwen4_exp_cache` format marker | f0707cd92 | `test_r1_caches_work_across_two_loaded_module_copies`: TypeError → snapshot / restore / decode bitwise |
| S9 | systems | LOW | verified artifact broken by any plain mlx-lm load (`__pycache__`), payload symlinks accepted, path-based exec (planted `.pyc`), check-then-use gaps | fixed: module compiled from its hashed bytes, config from its hashed bytes, `__pycache__` tolerated and reported, symlinks / nested / non-regular entries refused, n-gram tables opened before return, (dev, ino, size, mtime) re-checked after load; documented as the only load path | 33fd589f7 | `test_r1_verified_artifact_survives_plain_load_and_refuses_links`: "manifest file inventory mismatch" after a plain load (symlink accepted per the seat's probe) → verifies, a live planted `.pyc` does not run, symlink / nested / changed refused |
| S10 | systems | LOW | single-threaded, page-cache-polluting manifest hashing (~136 s per verified load of the real artifact) | fixed: files and 256 MiB chunks hashed on a thread pool with `F_NOCACHE`; plain sha256 kept for files ≤ 256 MiB; scheme recorded (format v2) | 808fff7c5 | `test_r1_manifest_hashing_is_parallel_chunked_and_uncached`: no parallel path → barrier-verified concurrency for files and chunks; 0.66 → 2.15 GB/s with 4 workers (1 GiB, background QoS) |
| N1 | numerics | MEDIUM | bf16 reference built by `.to(torch.bfloat16)`, which rounds the RoPE `inv_freq` buffer to bf16 (3.3e-3) | fixed: `_from_config(dtype=...)` + checkpoint values, buffers checked against `from_pretrained`'s; (b) re-run with a 4101-token bf16 scenario; (c) router / expert / MoE checks made tie- and cancellation-aware (the corrected reference showed one exact expert tie and one cancellation flip) | d4fb36f62 | `test_r1_bf16_reference_is_built_as_from_pretrained`: bf16 `inv_freq` (3.3e-3 off) → fp32, equal to `from_pretrained`'s; (b) re-measured above: worst ratios 1.07 / 1.07, 4101 tokens 1.00 / 0.89 |
| N2 | numerics | LOW | router tie rate at real scale understated (0.3% on the 8-expert fixture) | corrected: deviation 7 and follow-up use the real-weight seat's counts (8 of 54 bf16 prefill rows official, 7 canonical, layer 2; 5 / 3 at layer 3); deterministic tie rule on both sides recommended for P4 | 57f530716 | doc |
| F1 | Fable | MEDIUM | QSA core ~0.48 bitwise mis-attributed to "torch CPU SDPA not reproducible" | corrected with a probe: kernel rounding order (MLX fp32 P vs torch bf16 exp; MLX head_dim-256 fallback = HF eager); not a port defect; gated against an fp32-probability core (deviation 12) | e45679b88, 8aceb1dd2 | (c) `mix.qsa_vs_fp32P_core` ≥ 0.99 (measured 0.996 at L3, 0.9995 at L7; against torch's SDPA 0.555 / 0.530, reported) |
| F2 | Fable | LOW | `PAD_B = 8` a multiple of `RATIO`: per-row branch of `_update_blocks` and chunked padded prefill unexercised | fixed in the suite: `PAD_B = 5`, chunked padded prefill in (a), (b), (d) and through the kernel | 303a984e3 | mutation M1 (`M = min(...)` in `_update_blocks`): padded row 1 vs its own single-row run 5.96e-06 at the old `PAD_B = 8` (passes unnoticed), 0.176 at `PAD_B = 5` (caught; 0.176 vs REF) |
| F3 | Fable | LOW | single-row decode gather branch never compared with the reference | fixed in the suite: one-row long decode through the gather path, `paths.gather_single` counter | b35d17b8a | mutation M2 (drop a selected token in the one-row branch): long decode at default thresholds (what the old suite ran) 2.5e-06 (unnoticed), one-row gather decode vs REF 0.086 (caught) |
| F4 | Fable | LOW | `mixed` / `maxfit5` listed as delivered without evidence; `mixed` unconvertible at the default group; q8 / q4 codec untested | evidence added: maxfit5 under (f); `mixed` layout / codec / sanity; codec bounds; `--ngram-group-size`; early refusal. (f) itself corrected (exact fp32 dequantization; ratio to the dequantized reference's own bf16 error) | 52b06a25d | maxfit5 under the corrected (f): 1.06 / 1.02 / 0.80 (under the old proxy denominator it read 1.93 from near-tie expert flips the reference's own bf16 run shares) |
| F5 | Fable | LOW | provenance numbers stated for a non-released config: the PLE row's "hidden 2560" (Fable took 2048 as released) and an unscoped RoPE "bit-identical" | recomputed: the released `config.json` has hidden_size **2560** (2048 is only the HF class default), so the D8 number stands, now stated with its population (35.9% of all bf16 values in [2^-8, 2^8); 36.5% of the differential's gate values; 2.3% it would be at 2048). RoPE scoped to the released config (32/32 at theta 1e7 / rotary 64; 63/64 at theta 1e6 / rotary 128) | 92f6343f3 | doc (probe `provenance_probe.py`) |
| R1 | real-weight parity | LOW | `NgramTable._prefetch` passed the file offset to `madvise` on a mapping that starts at the rounded-down offset | fixed: row 0's position measured inside the mapping; `NgramTable(offset=...)` for tables inside larger files | 31bc9bc2f | `test_r1_ngram_table_inside_a_larger_file`: "madvise start out of bounds" → rows bitwise, spans cover the rows |
| V | refutation of S1 | - | adversarial verification: REAL (6021 / 13554 nodes at 1000 steps, 212 ms transition step, fix keeps tokens identical) | fixed by S1 | 4b491b2e4 | as S1 |

## Pin

`joulewise/align/models/qwen4_exp.py` sha256 `af26a5a5bf15a6c475f21637989c5f03c6f8bd3a3e0b8824ac99765a99f7f95f` after MISSING-11 (it was `f4ec75d16f0af0517b63e202abeef704c9a775e9111949ab003250d51d982c37` after validation round 1 and `55aecaeac2e72518957e72a33aaf2b0a470e865e9bec7961e30870d93b11a37f` at the round-0 head `ce911c6e7`). It is pinned in two places:
- `MODULE_SHA256` in `scripts/align_convert_qwen4_exp.py`, the module `load_verified_model` runs by default. The suite checks it against the file (`test_r1_load_verified_model_requires_both_pins` fails if it is stale).
- this section, which is a record and is not checked.

The converter copies the module into every artifact and records `module_sha256` (== its `qwen4_exp.py` entry) in `manifest.json`. `load_verified_model(dir, expected_manifest_sha256)` fails closed without the artifact's manifest sha256 (recorded when it was converted; the CLI prints it), and refuses an artifact whose module differs from the module pin unless `expected_module_sha256` is given explicitly. It compiles the module from the bytes it hashed. Artifact format `joulewise-qwen4-exp-canonical-v2`: sharded weights, chunked digests for files over 256 MiB.

### MISSING-11 compiled decode boundary

Batch-one, single-token calls after the initial token compile each decoder
layer with `mx.compile(..., shapeless=False)`. The input and output tuple
carries every mutable cache array; position-dependent RoPE, the SSM mask and
the PLE lookup are also array arguments rather than captured trace values.
Multi-token prefill, batched calls and the first token remain uncompiled.
`compile_decode: false` in `config.json` is the bitwise-reference switch.

Because `qwen4_exp.py` is part of each artifact, existing artifacts do **not**
acquire this change. In the live kit's step-8 clone, make a new artifact by
copying the old artifact directory, replacing only `qwen4_exp.py`, and writing
a new `manifest.json` whose `files["qwen4_exp.py"]` and `module_sha256` are the
new module digest (then recompute the externally recorded manifest digest).
Do not reconvert or touch weight/table payloads. Gold units must be re-attested
against that new manifest/module pair.

The native-Mac gate is all three kit checks, not just the new regression:

```
python -m unittest -v tests.align.test_qwen4_exp_canonical
# Then run the Saturday kit's step-8 gold-adapter tiny command.
# Then run the Saturday kit's step-8 live tiny command against /Volumes/JW-EXT.
```

The canonical module includes the 64-step compiled/uncompiled identity test:
it compares logits and every cache array for linear, PLE and QSA layers,
prefills QSA past 2051 tokens, and restores a midpoint snapshot to exercise a
QSA trim. These are native MLX/Metal checks and intentionally skip where MLX
is unavailable.

## Reproduce

```
cd <clone>
OMP_NUM_THREADS=2 TMPDIR=/private/tmp/jwcanon JW_CANON_WORK=/private/tmp/jwcanon/work \
  nice -n 20 taskpolicy -b /private/tmp/jwsol/venv-both/bin/python -m unittest -v tests.align.test_qwen4_exp_canonical
```

Every measured number is written to `$JW_CANON_WORK/ref-<hash>/results.json`.

## Follow-ups

- P4/P11 real-weight parity: compare QSA selections and router expert sets modulo exact ties and log both tie rates. Router ties are frequent at the released scale (8 of 54 bf16 prefill rows at layer 2, deviation 7); patch the reference router's topk to the deterministic (score desc, index asc) rule, and give the port the same rule, before reading bf16 end-to-end expert-set comparisons.
- P5: re-measure the dispatch thresholds on the M3 Max (`qsa_sparse_prefill_min_kv`, `qsa_sparse_decode_min_kv` in config.json), and evaluate the router fold (deviation 1).
- P6: the memory model must count the QSA indexer cache (raw keys + block keys, about 13 MB per QSA layer at 40,960 tokens) and the kernel's token lists ([S, 2051] int32 per prefill chunk).

