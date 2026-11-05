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
| File layout: `TextModelArgs` + validation, `ModelArgs(text_config)`, `Model.language_model`, `sanitize` | C:79-249, C:1841-1948 | twin T:66-217, T:1455-1524 | mlx-lm house style for a VLM checkpoint's text path (`qwen3_5.py`); one file under the sha256 pin (Sol's sibling `qwen4_exp_tables.py` is folded in) |
| Legacy top-level `rope_theta` / `partial_rotary_factor` folded into `rope_parameters`; `rope_scaling` refused | C:126-144 | new (review finding) | `BaseModelArgs.from_dict` would drop them silently |
| Weight names HF -> MLX, mtp / vision dropped | C:1744-1761 | twin T:1385-1403 | |
| n-gram hash buffers checked against the config at load and conversion | C:1776-1784, C:1894-1897 | Sol S:651-657 | catches a hash-layout drift instead of silently mis-hashing |
| n-gram ids: `NgramHashSpec` (splitmix multipliers, primes, `_shift_right_ignore_eos`, decode fast path) | C:263-382 | twin T:232-357 | same ids as Sol (PLE agrees to 7e-7 fp32) |
| n-gram table: `NgramTable` (f32/bf16/q8/q4 records, mmap or `F_NOCACHE` pread, dedupe, fault counters), never GPU-resident | C:392-561 | twin T:364-548 | GOAL item 6: the bf16 table stays on disk, paged |
| RMSNorm `(1 + w)`, grouped | C:582-599 | twin T:556-577 (`mx.fast.rms_norm` on fp32) | same math as HF:143-163, fused |
| Gated RMSNorm (DeltaNet output) | C:602-619 | twin T:580-595 | HF:170-187 rounding order (norm rounded to dtype, times weight, times fp32 gate) |
| RoPE inverse frequencies, float64 pow rounded once | C:627-637 | twin T:649-667 | D2: 32/32 entries equal to the reference at the released config (rope_theta 1e7, rotary_dim 64; Sol 15/32 differ). At the released config only: the recipe is not torch's fp32 pow in general (63/64 at theta 1e6, rotary 128), so re-verify inv_freq bitwise for any other theta / rotary_dim |
| RoPE application: explicit rotate-half, cos/sin cast to the model dtype, computed once per forward | C:640-659, C:1112-1133 | twin T:670-686, T:833-847 | perf critic HIGH: `mx.fast.rope` changes bf16 indexer selection; used in main attention too (the bitwise-exact choice) |
| sigmoid: fp32, rounded once, ALWAYS (no `jw_bf16_fp32_ops` flag) | C:576-579; sites: HC C:1155, C:1161, attention gate C:1446, DeltaNet beta C:951, shared-expert gate C:1545, PLE C:1580 | Sol S:229-233 | D3: torch evaluates bf16 sigmoid in fp32; `mx.sigmoid` on bf16 differs on 3% |
| silu: fp32, rounded once, everywhere | C:569-573; sites: DeltaNet conv C:1210, PLE conv C:1593, HC C:1154, experts C:1506, shared expert C:1484 | twin T:627-636 + new sites | D4 (conv), D5 (HC), expert/shared SwiGLU (both ports used bf16 `nn.silu` / mlx-lm `swiglu`) |
| Hyper-connection | C:1136-1162 | Sol S:263-279 structure; fp32 stream mean (both, T:871) | D3, D5 |
| DeltaNet short conv: `mx.conv1d` (`nn.Conv1d`, groups = C) | C:1183, C:1210 | Sol S:282-287 | bit-identical to the fp32 sum rounded once and ~4x faster than the twin's tap loop (perf §2) |
| DeltaNet recurrence: perf eps adapter `Dk**-0.5 * rms_norm(x, 1e-6/Dk)` on mlx-lm's unchanged `gated_delta_kernel`; fp32 softplus/decay (mlx-vlm P2); beta rounded once | C:933-960 | perf P:71-146 (its `gdn_gates` bf16 `mx.sigmoid` replaced by the rounded-once sigmoid) | exact identity of HF l2norm (HF:247-250, 296-301); fused |
| Mask-aware DeltaNet seam: masked steps leave the state unchanged; mask from `create_ssm_mask(h, cache)` | C:1193-1220, C:1720 | Sol S:243-260, S:320-342 | equals HF's zeroed inputs for left padding from a zero state |
| QSA indexer scores `sum_h relu(q_h . kb) / sqrt(Di)` in fp32 | C:1299-1304 | twin T:1052-1056 (layout of perf P:317-326) | D7: the rounded quotient decides which near-equal scores tie |
| QSA tie rule: score desc, block asc, as a mask (`partition` + `cumsum`), no host sync | C:662-678, C:1333 | twin T:689-707 | D0: same set as Sol's rule; Sol's `qsa_topk` synced `mx.any(...).item()` per QSA layer per call (S:363) |
| QSA per-block key cache: pooled + normed + roped once per completed block, per-row padding phase, exact under trim | C:751-875 (`Qwen4ExpQSACache`), C:1256-1286 | twin T:715-787, T:986-1007 (the perf design, P:711-777) | Sol recomputed every block key on every call (S:397-404) |
| QSA attention core + policy: dense causal while every query sees <= K blocks; masked SDPA below `qsa_sparse_prefill_min_kv` (6144); block-sparse Metal prefill kernel above; decode: masked SDPA below `qsa_sparse_decode_min_kv` (8192), gather + SDPA above. No prefill cap. | C:968-1109, C:1306-1406, C:1449-1471 | perf P:445-708 (kernel source verbatim, P:523-590) | replaces both ports' cores (same function; Sol's per-query gather and the twin's masked SDPA are O(S x L)); Sol's 64-token `jw_max_prefill_tokens` cap is gone |
| Token lists for the kernel / decode gather, with per-row left padding and a self slot for pad queries | C:1390-1406 | perf P:483-509, generalised | perf open issue 3 (left-padded batches) and mlx-vlm D1 (ragged decode keeps the selection) |
| MoE router: fp32 softmax, `argpartition` on fp32 probabilities, fp32 renorm, cast | C:1531-1539 | both (identical) | mlx-vlm P1; perf §4 |
| MoE experts: fused `gate_up_proj` [E, 2I, H] (`SwitchLinear`, so load-time `gather_qmm` quantization applies), silu rounded once | C:1487-1509 | perf P:814-861 + new silu | two gathers per token instead of three |
| MoE combine: k weighted rows summed in fp32, rounded once | C:1544 | twin T:1195 | D6: the reference's default `grouped_mm` experts path (transformers `moe.py`) |
| PLE gate: bf16 product, fp32 sum rounded once, fp32 division by sqrt(hidden) rounded once | C:1577-1578 | twin T:1224 sum + new divide | D8: MLX rounds a Python divisor to bf16: sqrt(2560) = 50.596 becomes 50.5 at the released hidden size 2560 (the released `config.json`; 2048 is only the HF config class default), changing 35.9% of all bf16 values in [2^-8, 2^8) (36.5% of the differential's gate values) |
| PLE dilated conv + mask | C:1549-1593 | Sol S:536-561 (`nn.Conv1d(dilation)`) + twin T:1215-1242 (mask, history) | |
| Caches: cache-carried left padding on mlx-lm's `ArraysCache(left_padding)` / `make_mask` / `advance` protocol | C:695-748, C:883-893 | twin T:715-799 (`make_cache(left_padding)`) rebuilt on the mlx-lm protocol | house style (`create_ssm_mask`) |
| Caches: serializable `state` / `meta_state`, registered in `mlx_lm.models.cache` for `load_prompt_cache` | C:720-737, C:818-851, C:879-880 | Sol S:131-198 | ALIGN prefix reuse; the twin's `QSACache.state` setter raised (T:782-784) |
| Snapshot / restore (hybrid prefix rewrite) | C:896-923 | twin T:802-825, extended to the ArraysCache padding counters | |
| Precision profiles `maxfit` (6-bit g64 experts, all else bf16, bf16 n-gram on disk) / `maxfit5` / `bf16` / `fp32` / `mixed` | C:1790-1833 | Sol ST:157-222; `mixed` keep-float list = twin T:1421-1447 + Sol's | GOAL precision target |
| Converter: streaming header inventory, raw bf16 passthrough, bounded row slices, sha256 manifest + verify, maxfit | `scripts/align_convert_qwen4_exp.py` | Sol SC (whole structure) | twin's converter could not read bf16 (D1) |


## Deviations and decisions

1. **Router fold not adopted.** The recommendation's MoE row also suggests folding `shared_expert_gate` into the router matmul (513 rows, perf §4). Not done: it renames the router parameter away from the reference's layout, perf §4 measures the router as negligible, and a 513-wide GEMM was not shown bitwise-equal to the 512-wide one. Deferred to P5 (performance), where it can be measured on the Mac.
2. **RoPE in main attention stays explicit.** The recommendation allows `mx.fast.rope` in main attention only if a bf16 parity run accepts it. The explicit HF-exact form is bitwise in isolation and costs nothing measurable at this size, so it is used everywhere.
3. **No runtime caps.** Sol's `jw_max_prefill_tokens` (64, a consequence of its O(S x budget) per-query gather) and `jw_context_cap` (40,960) are dropped. Prefill chunking is mlx-lm's `prefill_step_size`; the context cap belongs to the runner's `max_tokens`, as in mlx-lm house style.
4. **Dispatch thresholds are config fields** (`qsa_sparse_prefill_min_kv`, `qsa_sparse_decode_min_kv`, defaults 6144 / 8192 from the M4 crossovers), so the Mac re-measurement (perf §9) needs no code change. Every path computes the same function (tests (d), (g)).
5. **Perf kernels generalised to left padding.** The perf track assumed unpadded rows (perf open issue 3). Token lists and masks here carry each row's padding phase, and pad queries attend to themselves (outputs discarded, kept finite). Test (d) runs a left-padded batch through the kernel and the gather path against the reference.
6. **Fused-norm rounding at hidden 192.** The recommendation's fused `mx.fast.rms_norm` (twin) leaves ~0.1% one-ulp bf16 flips in the hyper-connection stream mix at hidden 192. Sol's explicit norm is no better (probed on the captured inputs: 0.99935 vs 0.99909), so it is fp32 reduction order inside the 192-wide RMS; the prototype's 1.000 was measured at hidden 96. The floor is 0.998, and the weights path is 1.000.
7. **Router ties.** `argpartition` and `torch.topk` both leave ties unspecified. The bf16 reference has exact k-th = (k+1)-th probability ties on 24 of 7,928 router rows (none in fp32); a tied swap picks a different expert with the same weight. Logged by test (e); real-weight parity must stay tie-aware for the router too (as PR #669 found for near-ties).
8. **Converter imports mlx.** The shared rules (names, expected shapes from the module's own lazy parameters, precision policy, n-gram record format) come from the module, so even unquantized conversion imports mlx; Sol's numpy-only path is gone. Sol kept a second, independent parameter enumeration (`parameter_shapes`); here the strict inventory check is against the module itself, which is what `load_model(strict=True)` enforces anyway.
9. **n-gram record format** is the twin's (`NgramTable`: f32 / bf16 / q8 / q4 with fp16 scales), not Sol's (f32 scales). maxfit uses bf16, where both formats are the raw bf16 bits.
10. **Unsupported, failing loudly:** BatchGenerator cache `merge` / `extend` / `filter` (cache-carried padding; same as Sol), `input_embeddings` (PLE needs token ids; same as twin), KV-cache quantization (it would drop the indexer state).
11. **Bound for (f).** "Quantized vs bf16 within the bound" is made testable as: the maxfit model must equal the fp32 reference run with the SAME dequantized 6-bit expert weights, within (b)'s 1.25x bf16-noise bound. The quantization effect itself (maxfit vs bf16) is measured and reported, not bounded: it is a property of the recipe, not of the port.

## Test evidence

`tests/align/test_qwen4_exp_canonical.py`: **16 tests, all pass** (native, `/private/tmp/jwsol/venv-both`: mlx 0.31.2, mlx-lm 0.31.3, torch 2.15.0, transformers 5.22.1; under `nice -n 20 taskpolicy -b`, `OMP_NUM_THREADS=2`, `TMPDIR=/private/tmp/jwcanon`). Peak RSS 837 MB. The reference stage (torch, CPU-starved by the analysis job, 7% of a core) took 524 s once and is cached; a full rerun after a module change (reconversion + the quantized reference) takes 61 s, a cached rerun 28 s.

Fixture: one tiny random `Qwen4ExpForConditionalGeneration` (vision tower included), saved in bf16 with `max_shard_size="200KB"` in the released serialization (`model.language_model.*`, per-expert `mlp.experts.{e}.*`, n-gram `shard_{0..3}` + hash buffers) plus a fake `mtp.*` file; converted by the canonical converter (fp32, bf16, maxfit) and loaded through `mlx_lm.utils.load_model` after manifest verification. Text config: 8 layers (DeltaNet x3, QSA, DeltaNet x3, QSA), hidden **192** (sqrt not bf16-representable, multiple of 64 for the maxfit recipe), hc 4, 4 q / 2 kv heads of 64, partial rotary 0.25, QSA indexer 4 x 32 with budget 16 / ratio 4 (top-4 blocks: 21 of the 40-token prompt's queries drop blocks), DeltaNet 2 k / 4 v heads of 32, MoE 8 experts top-3, PLE at layers 2 and 5 (`ple_layer_index` 0 and 1), EOS inside every prompt. The reference's experts implementation resolved to `grouped_mm`.

Scenarios: `prefill` (40 tokens), `stepwise` (one token at a time), `chunked` (7-token chunks), `padded_row0/1` (left-padded batch, 8 pads, then 4 cached decode steps; the reference uses `attention_mask` and `position_ids = cumsum - 1`), `long_prefill` / `long_decode` / `long_chunked` (320 tokens; prefill 304 then 16 decode steps; 64-token chunks), greedy (32 tokens).

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
| padded_row1 | 5.72e-06 | 1.000000 | 1.000 |
| long_chunked | 9.78e-06 | 1.000000 | 1.000 |

Greedy 32 tokens, fp32: port == REF on **32/32** tokens. bf16: first divergence from REF bf16 = None (None = identical 32/32). Also identical through mlx-lm's `generate_step` with 16-token prefill chunks.

### (b) bf16 bound (port vs REF fp32 <= 1.25x noise; port vs REF bf16 <= 1.5x noise; noise = REF bf16 vs REF fp32)

| scenario | noise | port vs REF fp32 | ratio | port vs REF bf16 | ratio |
|---|---:|---:|---:|---:|---:|
| prefill | 0.0739 | 0.0700 | **0.95** | 0.0708 | **0.96** |
| stepwise | 0.0676 | 0.0739 | **1.09** | 0.0664 | **0.98** |
| chunked | 0.0739 | 0.0697 | **0.94** | 0.0708 | **0.96** |
| long_prefill | 0.3132 | 0.2351 | **0.75** | 0.2773 | **0.89** |
| long_decode | 0.1482 | 0.1092 | **0.74** | 0.1582 | **1.07** |
| long_chunked | 0.3132 | 0.2516 | **0.80** | 0.2969 | **0.95** |
| padded_row0 | 0.0739 | 0.0677 | **0.92** | 0.0708 | **0.96** |
| padded_row1 | 0.2883 | 0.2004 | **0.70** | 0.0938 | **0.33** |

### (c) isolated components, bf16: minimum over layers of the fraction of elements bitwise equal to the reference

| component | canonical | differential prototype (hidden 96) | floor |
|---|---:|---:|---:|
| attn_hc.mixed | 0.999 | 1.000 | 0.998 |
| attn_hc.weights | 1.000 | 1.000 | 0.999 |
| mlp_hc.mixed | 0.999 | 1.000 | 0.998 |
| mlp_hc.weights | 1.000 | 1.000 | 0.999 |
| DeltaNet | 0.991 | 0.969 | 0.95 |
| ple | 1.000 | 1.000 | 0.999 |
| QSA whole layer | 0.485 | 0.457 | reported (D9) |
| router.logits | 1.000 | 1.000 | 1.0 |
| expert sets | 1.000 | 1.000 | 1.0 |
| moe | 0.999 | 0.999 | 0.99 |
| mixer | 1.000 | 1.000 | 0.999 |
| head | 1.000 | 1.000 | 0.999 |
| QSA block selection, rows differing (L3, L7) | 0/21, 0/21 | 0/21, 0/21 | 0 |

fp32 isolated: every component within 9.54e-07 of the reference.

### (d) port-internal invariants (max abs)

| invariant | fp32 | bf16 |
|---|---:|---:|
| prefill_vs_stepwise | 4.05e-06 | 0.0352 |
| prefill_vs_chunked | 4.22e-06 | 0.0781 |
| long_prefill_vs_chunked | 5.78e-06 | 0.2383 |
| padded_row0_vs_batch1 | 3.81e-06 | 0.0703 |
| padded_row1_vs_batch1 | 5.13e-06 | 0.0000 |

Snapshot / detour / restore / re-prefill (QSA trim + DeltaNet restore), short (40) and long (320, sparse QSA, partial block trimmed) prefixes, fp32 and bf16: max abs 0.0 (bitwise), DeltaNet states bitwise after restore: True. Prompt-cache `save_prompt_cache` / `load_prompt_cache` round trip (single row, and a left-padded batch): bitwise.

Left-padded batch with both sparse thresholds at 0 (prefill through the Metal kernel, 2 calls; decode through the gather path, 8 calls) vs REF fp32: row 0 4.89e-06, row 1 5.72e-06.

### (e) ties

| count | fp32 | bf16 |
|---|---:|---:|
| REF QSA top-k calls / straddling exact ties (all scenarios) | 1912 / 8 | 1912 / 8 |
| REF router rows / exact k-th = (k+1)-th fp32-probability ties | 7928 / 0 | 7928 / 24 |
| REF 4101-token prefill: QSA calls / ties | 8196 / 0 | - |
| forced-tie probe (indexer projection zeroed): REF straddling ties | 21 | - |

Port-side (diagnostic `record_selection`) on the 40-token prompt: straddling ties per QSA layer {'3': 1, '7': 0}, sparse queries {'3': 21, '7': 21}. Port vs REFdefault (torch's own CPU tie order): prefill 3.76e-06, long prefill 0.1223; REF vs REFdefault: 0.00e+00, 0.1223, i.e. the whole difference is the tie order. Forced-tie probe: port vs REF (lowest index) 3.76e-06.

### (f) maxfit (6-bit group-64 experts, everything else bf16) vs the bound

| scenario | maxfit vs REF fp32 with the same dequantized experts | ratio to noise (<= 1.25) | quantization effect: maxfit vs bf16 port | REF q6 vs REF fp32 |
|---|---:|---:|---:|---:|
| prefill | 0.0585 | **0.79** | 0.1836 | 0.1981 |
| stepwise | 0.0750 | **1.11** | 0.2031 | 0.1981 |
| long_prefill | 0.2004 | **0.64** | 0.2656 | 0.2606 |

### (g) 4101-token sparse prefill through the block-sparse Metal kernel

| comparison | fp32 | bf16 |
|---|---:|---:|
| kernel path vs transformers (dense SDPA under the QSA mask, REF tie rule) | 8.20e-06 | - |
| port dense-masked SDPA path vs transformers | 7.39e-06 | - |
| kernel path vs port dense-masked path | 4.05e-06 | 0.1680 (cos 0.999995) |
| 1024-token chunked kernel prefill vs one shot | 3.01e-06 | 0.0156 |
| port bf16 vs port fp32 (scale of bf16 error at this length) | - | 0.3768 |

Kernel calls: 2 (both QSA layers), dense-masked calls in the comparison model: 2.


## Components where the fixes did not reach a bitwise result

- **QSA attention core** (whole QSA layer ~0.48 bitwise in bf16): differential D9, a reference artifact. torch's CPU bf16 SDPA is not bitwise reproducible across call contexts; every wrapper op is exact and the block selection is identical. Not gated.
- **Hyper-connection stream mix**: 0.999 rather than the prototype's 1.000 (about 1 bf16 ulp on 0.1% of elements) at hidden 192, from fp32 reduction order (deviation 6). The MoE matches the prototype (0.999); the HC weights path, router logits, expert sets, PLE, mixer and head are 1.000.
- **DeltaNet**: 0.991 (the prototype reached 0.969): the fp32 state recurrence runs in a different order from torch's chunked rule.

None of these moves the end-to-end bf16 result outside the bound: worst ratios are 1.09 (vs fp32 REF, bound 1.25) and 1.07 (vs bf16 REF, bound 1.5), against the prototype's 1.01 / 1.05 and Sol's 1.15 / 1.05 at hidden 96.

## Pin

`joulewise/align/models/qwen4_exp.py` sha256 `55aecaeac2e72518957e72a33aaf2b0a470e865e9bec7961e30870d93b11a37f` at this PR's head (the converter copies it into every artifact and records `module_sha256` in `manifest.json`; `load_verified_model` checks a pinned manifest hash before executing it).

## Reproduce

```
cd <clone>
OMP_NUM_THREADS=2 TMPDIR=/private/tmp/jwcanon JW_CANON_WORK=/private/tmp/jwcanon/work \
  nice -n 20 taskpolicy -b /private/tmp/jwsol/venv-both/bin/python -m unittest -v tests.align.test_qwen4_exp_canonical
```

Every measured number is written to `$JW_CANON_WORK/ref-<hash>/results.json`.

## Follow-ups

- P4/P11 real-weight parity: compare QSA selections and router expert sets modulo exact ties and log both tie rates (test (e) shows bf16 router ties are not rare: 24 of 7,928 rows here).
- P5: re-measure the dispatch thresholds on the M3 Max (`qsa_sparse_prefill_min_kv`, `qsa_sparse_decode_min_kv` in config.json), and evaluate the router fold (deviation 1).
- P6: the memory model must count the QSA indexer cache (raw keys + block keys, about 13 MB per QSA layer at 40,960 tokens) and the kernel's token lists ([S, 2051] int32 per prefill chunk).

