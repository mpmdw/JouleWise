# qwen4_exp differential: Sol port vs Opus twin vs transformers reference

GOAL item 3 (`docs/align/qwen4_exp_port/GOAL.md`). Date: 2026-11-05. Laptop (M4 Air), analysis-priority rules: every stage ran under `nice -n 20 taskpolicy -b`, `OMP_NUM_THREADS=2`, `TMPDIR=/private/tmp/jwdiff`. Peak RSS was 374 MB for the reference stage and 389 MB for the MLX stage.

| | Ref | File |
|---|---|---|
| Sol port | `lane/2026-11-05-align-flashnext-port` @ 28d153449 | `joulewise/align/models/qwen4_exp.py` (`S:<line>`) |
| Opus twin | `lane/2026-11-05-align-flashnext-twin` @ ad56248a5 | `joulewise/align/models/qwen4_exp_twin.py` (`T:<line>`) |
| Reference | transformers 5.22.1 (installed, identical in `venv-both` and `venv-ref`), torch 2.15.0, CPU, `attn_implementation="sdpa"`, `experts_implementation` resolved to `grouped_mm` | `transformers/models/qwen4_exp/modeling_qwen4_exp.py` (`HF:<line>`) |
| MLX stack | mlx 0.31.2, mlx-lm 0.31.3, GPU | both ports loaded through `mlx_lm.utils.load_model` (the `model_file` hook) |
| Script | `scripts/qwen4exp_differential.py` (this branch) | stages `ref`, `convert`, `mlx`, `diag`, `report` |

The lanes' `.engine/transformers-qwen4_exp` copy differs from the installed 5.22.1 file only in how eager (float) masks are combined. Under `sdpa` both take the same boolean `attention_mask & selected_token_mask` path, so the installed library is the authority used here. Community PR #1788 was neither read nor run.

## Verdict

1. **fp32: the two ports agree with each other and with the reference to float noise in every scenario.** Sol vs twin: max abs at most 5.6e-6. Each port vs the reference: at most 9.6e-6 (logit scale 3.85, cosine 1.000000). Greedy generation of 32 tokens is identical across all three. Per layer and per component, every Sol/twin/reference difference is at most 6.7e-6.
2. **The only fp32 disagreement beyond noise is a QSA exact tie (D0), and neither port is wrong.** It is a 0.12 logit difference: one relu-zero tie at layer 3, where `torch.topk`'s tie order differs from the ports' shared rule. Sol's "score descending, block index ascending" and the twin's "earliest block" **are the same rule**: they select identical sets, also on a forced all-ties probe. When the reference breaks the tie the same way, everything agrees to 9.6e-6.
3. **bf16: the ports differ by up to 0.23 (short context) and 0.29 (320 tokens), the size of the reference's own bf16-vs-fp32 error (0.16 and 0.30).** Op-level bf16 rounding choices explain all of it. They are resolved against the reference in D2-D9, with file:line in both ports and in the reference. Sol with `jw_bf16_fp32_ops` is the closer port in most places, but **both ports differ from the reference in some bf16 ops**: hyper-connection silu, the PLE gate divisor and the expert SwiGLU. The twin is right on the MoE combine, conv silu, PLE gate sum and RoPE frequencies.
4. **Prototype canonical numerics** (Sol + 7 op-level changes, `apply_canonical` in the script): every component, fed the reference's exact bf16 input, matches the bf16 reference **bitwise** (fraction of equal elements >= 0.969 for DeltaNet, 0.999 for the MoE, 1.000 for the rest). The one exception is the QSA attention core, where torch's CPU SDPA does not even reproduce itself bitwise (D9). End to end, the prototype is the closest to the bf16 reference: prefill max abs 0.094 (Sol 0.148, twin 0.195), cosine 0.99995.
5. **Bugs found:** (D1) the twin's converter cannot read a bf16 checkpoint, and the released one is bf16. (D2) Sol's RoPE inverse frequencies differ from the reference in 15 of 32 entries at the released config, a phase drift of up to 9.8e-4 rad by 33K positions. (D8) Both ports round the PLE divisor sqrt(hidden) to bf16, which changes 36% of gate values at hidden 2560. Neither port's own parity test could see D8: both use hidden 64, where sqrt(hidden) = 8 exactly.

## Setup

**One shared checkpoint.** `Qwen4ExpForConditionalGeneration` (tiny vision tower, dropped by both converters), randomised with nonzero values everywhere (twin's scheme: norm offsets, PLE convs, `A_log`, `dt_bias`). It was saved in **bf16** with `save_pretrained(max_shard_size="200KB")`, giving 28 shards in the released serialized layout: `model.language_model.*`, per-expert `mlp.experts.{e}.{gate,up,down}_proj`, and n-gram `ngram_embedding.shard_{0..3}` plus hash buffers. The reference loads its weights back from these files through `from_pretrained`, with a bitwise round-trip check against the in-memory model.

| Text config | Value |
|---|---|
| layers | 8: DeltaNet x3, QSA, DeltaNet x3, QSA. PLE on layers 2 and 5 (`ple_layer_index` 0 and 1) |
| hidden / hc | 96 / 4 (lowrank 32). sqrt(96) is not bf16-representable, as sqrt(2560) is not |
| attention | 4 q heads, 2 kv heads, head_dim 64, partial rotary 0.25 (16 dims), rope_theta 1e7, sigmoid output gate |
| QSA indexer | 4 heads x 32, compress ratio 4, budget 16, so the top 4 blocks are kept. The 40-token prompt has 21 sparse query rows (up to 10 blocks); the 320-token context has 80 blocks |
| DeltaNet | 2 k-heads / 4 v-heads, dims 32 (Dk % 32 == 0, so both ports run mlx-lm's Metal kernel), conv 4 |
| MoE | 8 experts, top 3, intermediate 64, shared expert 64 |
| PLE | ngram 3, 2 heads per ngram, embed 64, conv 4 (dilation 3), base 101, 4 shards |
| tokens | vocab 256, EOS = 1, EOS inside every prompt (n-gram segment resets) |

**Conversions, each with the port's own converter.** Sol: `align_convert_qwen4_exp.py --profile fp32|bf16 --ple-storage fp32|bf16`. Twin: `align_convert_qwen4_exp_twin.py --no-quantize --dtype float32|bfloat16 --ngram-format f32|bf16`. The twin's converter fails on the bf16 checkpoint (D1), so it read an exact fp32 upcast of the same files. **All 217 loaded parameters are bitwise identical between the ports, in fp32 and in bf16.** Sol is loaded with `jw_max_prefill_tokens` raised from its default 64 (S:80, written by its converter). bf16 runs Sol twice: with `jw_bf16_fp32_ops` on (default) and off.

**Scenarios** (identical inputs for all three; logits compared on valid positions):

| Name | What |
|---|---|
| prefill | 40-token prompt, one call |
| stepwise | the same 40 tokens one at a time through the cache |
| chunked | the same 40 tokens in 7-token chunks through the cache |
| padded_row0/1 | left-padded batch: row 0 is the 40-token prompt; row 1 has 8 pads + a 32-token prompt; then 4 cached decode steps. The reference uses `attention_mask` and `position_ids = cumsum - 1`; Sol uses `attention_mask`; the twin uses `make_cache(left_padding=...)` |
| long_prefill / long_chunked / long_decode | 320-token context crossing the QSA budget 20x; one call / 64-token chunks / prefill 304 then 16 cached decode steps |
| greedy | 32 greedy tokens after the 40-token prompt, plus a teacher-forced pass along the reference's path |

**Metrics.** Max abs; cosine over all logits; top-1 agreement. For component outputs in bf16: the fraction of elements that are **bitwise equal** to the reference after bf16 rounding.

**Reference tie order.** `torch.topk` (HF:749) leaves exact ties unspecified. "REF" is the reference with ties at the QSA cut broken score-descending, block-ascending: a stable sort inside the indexer only, never the MoE router. "REFdefault" is torch's own CPU order. Both were run (D0).

## Results

### fp32 (three-way): max abs / cosine

| scenario | Sol vs twin | Sol vs REF | twin vs REF | prototype vs REF |
|---|---:|---:|---:|---:|
| prefill | 4.35e-06 / 1.000000 | 4.47e-06 / 1.000000 | 4.01e-06 / 1.000000 | 4.35e-06 / 1.000000 |
| stepwise | 1.91e-06 / 1.000000 | 3.22e-06 / 1.000000 | 3.34e-06 / 1.000000 | 3.28e-06 / 1.000000 |
| chunked | 3.99e-06 / 1.000000 | 5.01e-06 / 1.000000 | 3.81e-06 / 1.000000 | 5.01e-06 / 1.000000 |
| padded_row0 | 3.16e-06 / 1.000000 | 5.60e-06 / 1.000000 | 4.83e-06 / 1.000000 | 5.01e-06 / 1.000000 |
| padded_row1 | 2.74e-06 / 1.000000 | 4.82e-06 / 1.000000 | 4.04e-06 / 1.000000 | 6.44e-06 / 1.000000 |
| long_prefill | 5.60e-06 / 1.000000 | 8.40e-06 / 1.000000 | 9.60e-06 / 1.000000 | 7.03e-06 / 1.000000 |
| long_decode | 1.55e-06 / 1.000000 | 3.61e-06 / 1.000000 | 4.38e-06 / 1.000000 | 4.02e-06 / 1.000000 |
| long_chunked | 5.60e-06 / 1.000000 | 7.55e-06 / 1.000000 | 8.94e-06 / 1.000000 | 8.46e-06 / 1.000000 |

Relative to the largest logit (3.85), every entry is at most 2.5e-6. Top-1 agreement is 1.000 everywhere. Greedy 32 tokens: identical for Sol, twin, prototype and REF.

### bf16: max abs / cosine

Port vs port:

| scenario | Sol vs twin | Sol (flag off) vs twin |
|---|---:|---:|
| prefill | 0.2109 / 0.999642 | 0.1875 / 0.999681 |
| stepwise | 0.2344 / 0.999616 | 0.2031 / 0.999666 |
| chunked | 0.2070 / 0.999638 | 0.1797 / 0.999682 |
| padded_row0 | 0.2109 / 0.999628 | 0.1875 / 0.999671 |
| padded_row1 | 0.2227 / 0.999792 | 0.2266 / 0.999745 |
| long_prefill | 0.2910 / 0.999618 | 0.2656 / 0.999595 |
| long_decode | 0.1758 / 0.999455 | 0.2227 / 0.999058 |
| long_chunked | 0.2871 / 0.999607 | 0.2656 / 0.999594 |

Against the bf16 reference:

| scenario | Sol | Sol (flag off) | twin | prototype |
|---|---:|---:|---:|---:|
| prefill | 0.1484 / 0.999770 | 0.1523 / 0.999766 | 0.1953 / 0.999772 | **0.0938 / 0.999952** |
| stepwise | 0.1484 / 0.999763 | 0.1602 / 0.999753 | 0.2031 / 0.999763 | **0.0898 / 0.999964** |
| chunked | 0.1484 / 0.999762 | 0.1523 / 0.999761 | 0.1797 / 0.999777 | **0.0918 / 0.999952** |
| padded_row0 | 0.1484 / 0.999766 | 0.1523 / 0.999764 | 0.1953 / 0.999774 | **0.0938 / 0.999955** |
| padded_row1 | 0.0859 / 0.999885 | 0.1172 / 0.999860 | 0.1836 / 0.999831 | **0.0312 / 0.999981** |
| long_prefill | 0.2559 / 0.999621 | 0.3398 / 0.999479 | 0.2988 / 0.999618 | **0.2422 / 0.999808** |
| long_decode | 0.2188 / 0.999221 | 0.3447 / 0.998792 | 0.2344 / 0.999598 | 0.2261 / 0.999387 |
| long_chunked | 0.2578 / 0.999608 | 0.3398 / 0.999481 | 0.2988 / 0.999618 | **0.2422 / 0.999806** |

Against the fp32 reference (accuracy). The last column is the reference's own bf16 error:

| scenario | Sol | Sol (flag off) | twin | prototype | REF bf16 |
|---|---:|---:|---:|---:|---:|
| prefill | 0.0971 / 0.999887 | 0.0777 / 0.999889 | 0.1945 / 0.999752 | 0.1583 / 0.999799 | 0.1583 / 0.999840 |
| stepwise | 0.0991 / 0.999885 | 0.0777 / 0.999885 | 0.2257 / 0.999739 | 0.1505 / 0.999821 | 0.1583 / 0.999839 |
| padded_row1 | 0.0942 / 0.999912 | 0.1097 / 0.999878 | 0.1285 / 0.999909 | 0.0825 / 0.999907 | 0.0820 / 0.999913 |
| long_prefill | 0.2757 / 0.999718 | 0.3089 / 0.999658 | 0.2582 / 0.999703 | 0.2855 / 0.999735 | 0.2992 / 0.999647 |
| long_decode | 0.1405 / 0.999885 | 0.2970 / 0.999210 | 0.1859 / 0.999546 | 0.1677 / 0.999835 | 0.2154 / 0.999319 |

Proposed bf16 bound for GOAL item 2, stated as ratios to the reference's own bf16 error ("noise" = REF bf16 vs REF fp32, max abs, per scenario):
- (a) port bf16 vs REF fp32 <= 1.25x noise;
- (b) port bf16 vs REF bf16 <= 1.5x noise.

These are the twin's own two criteria, with (a) relaxed from 1.0x to 1.25x. The reason: the reference's bf16 error is itself one draw of rounding noise. Here, rounding-order effects that no port can remove (D9; chunked vs recurrent DeltaNet) leave even the bitwise-faithful prototype at 1.01x on one scenario.

| worst scenario ratio | (a) vs REF fp32 | (b) vs REF bf16 | verdict |
|---|---:|---:|---|
| Sol | 1.15 (padded_row1) | 1.05 | passes |
| prototype | 1.01 (padded_row1) | 1.05 (long_decode) | passes |
| Sol (flag off) | 1.38 (long_decode) | 1.60 (long_decode) | fails |
| twin | 1.57 (padded_row1) | 2.24 (padded_row1) | fails (1.23x already on plain prefill) |

The twin's failure is caused by its native bf16 sigmoids (D3) plus the shared D5/D8 issues, not by a structural error. On cosine, (1 - cos) ratios to noise are at most 1.01 for Sol, 1.26 for the prototype and 1.65 for the twin.

### QSA tie effect (REFdefault = torch.topk's own CPU tie order): max abs

| scenario | REF vs REFdefault, fp32 | Sol vs REFdefault, fp32 | twin vs REFdefault, fp32 | REF vs REFdefault, bf16 |
|---|---:|---:|---:|---:|
| prefill / stepwise / chunked / padded_row0 | 0.1198 | 0.1198 | 0.1198 | 0.117-0.125 |
| padded_row1 | 0.0914 | 0.0914 | 0.0914 | 0.0879 |
| long_prefill / long_decode | 0 | 8.4e-06 / 3.6e-06 | 9.6e-06 / 4.4e-06 | 0 |

Ties at the cut in the reference: 11 of 2,060 top-k calls in each precision; one of them changes a selected block at layer 3 (D0). Greedy tokens are unchanged by the tie order.

### Greedy 32 tokens: first divergent token

| pair | first divergence | REF top-2 logit margin at that step |
|---|---:|---:|
| Sol vs twin, Sol vs REF, twin vs REF, prototype vs REF (fp32) | none (32/32) | - |
| Sol vs twin (bf16) | 16 | - |
| Sol (flag off) vs twin (bf16) | 28 | - |
| Sol vs REF bf16 | 26 | 0 (exact bf16 tie) |
| Sol (flag off) / twin / prototype vs REF bf16 | 16 | 0 (exact bf16 tie) |
| REF bf16 vs REF fp32 | 16 | 5.0e-3 |
| Sol vs REF fp32 | 16 | 5.0e-3 |
| twin, prototype vs REF fp32 | 28 | 2.4e-3 |
| Sol (flag off) vs REF fp32 | none (32/32) | - |

Every bf16 divergence lands on an exact bf16 logit tie in the reference (margin 0; bf16 spacing at logit 3.8 is 0.0156) or on an fp32 margin of 0.002-0.005. Teacher-forced along the reference's path, all ports agree with it to at most 4.8e-6 in fp32 (top-1 1.000) and 0.15-0.28 in bf16 (top-1 0.94-0.97).

### Port-internal invariants: max abs

| run | prefill vs stepwise | prefill vs chunked | long prefill vs 64-chunked | padded row 0 vs batch-1 | padded row 1 vs batch-1 |
|---|---:|---:|---:|---:|---:|
| Sol fp32 | 3.9e-06 | 6.4e-06 | 9.4e-06 | 3.6e-06 | 3.1e-06 |
| twin fp32 | 4.5e-06 | 4.1e-06 | 4.4e-06 | 5.7e-06 | 3.1e-06 |
| Sol bf16 | 0.0215 | 0.0215 | 0.1626 | 0 | 0 |
| twin bf16 | 0.0425 | 0 | 0.0164 | 0.0156 | 0 |

### Per-layer intermediates (item 3)

**fp32 (free-running prefill of the 40-token prompt).** For every layer and every component, the largest difference is 6.7e-6 for Sol vs twin, 5.6e-6 for Sol vs REF and 6.0e-6 for twin vs REF. The components are PLE contribution, attention and MLP hyper-connection mix and weights, DeltaNet out, QSA out, router logits, MoE out and the hyper-connection streams. Expert sets agree on 100% of tokens, and QSA block sets agree on 21/21 sparse rows at both QSA layers.

**bf16, free-running.** Max abs; "experts" is the fraction of tokens with the same expert set; "QSA" is the number of sparse query rows with a different block set (none of these differences is an exact tie).

| layer | component | Sol vs twin | Sol (off) vs twin | Sol vs REF | twin vs REF | prototype vs REF |
|---|---|---:|---:|---:|---:|---:|
| 0 | attn HC mix | 7.8e-03 | 7.8e-03 | 7.8e-03 | 7.8e-03 | 0 |
| 0 | DeltaNet out | 0.039 | 0.037 | 0.031 | 0.031 | 0 |
| 0 | router logits | 0.031 | 0.035 | 0.032 | 0.039 | 0 |
| 0 | MoE out | 0.128 | 0.126 | 0.129 | 0.094 | 1.2e-04 |
| 0 | streams | 0.141 | 0.156 | 0.141 | 0.129 | 0 |
| 0 | experts | 0.975 | 0.950 | 0.950 | 0.975 | 1.000 |
| 1 | PLE | 0.117 | 0.109 | 0.117 | 0.094 | 0 |
| 1 | DeltaNet out | 0.063 | 0.062 | 0.057 | 0.047 | 0 |
| 1 | router logits | 0.126 | 0.141 | 0.135 | 0.047 | 0 |
| 1 | streams | 0.203 | 0.195 | 0.203 | 0.141 | 7.8e-03 |
| 2 | DeltaNet out | 0.068 | 0.053 | 0.068 | 0.073 | 3.8e-06 |
| 2 | streams | 0.207 | 0.191 | 0.203 | 0.125 | 7.8e-03 |
| 3 | QSA out | 0.145 | 0.143 | 0.012 | 0.145 | 2.0e-03 |
| 3 | QSA block selection | 1/21 | 1/21 | 0/21 | 1/21 | 0/21 |
| 3 | router logits | 0.146 | 0.125 | 0.150 | 0.094 | 0.016 |
| 3 | experts | 0.975 | 0.975 | 0.950 | 0.975 | 1.000 |
| 3 | streams | 0.203 | 0.182 | 0.199 | 0.188 | 0.031 |
| 4 | PLE | 0.141 | 0.141 | 0.078 | 0.070 | 0.016 |
| 4 | DeltaNet out | 0.106 | 0.071 | 0.059 | 0.098 | 0.012 |
| 4 | MoE out | 0.091 | 0.089 | 0.091 | 0.023 | 3.9e-03 |
| 4 | streams | 0.250 | 0.258 | 0.258 | 0.220 | 0.047 |
| 5 | DeltaNet out | 0.136 | 0.132 | 0.156 | 0.104 | 0.033 |
| 5 | streams | 0.290 | 0.301 | 0.250 | 0.272 | 0.094 |
| 6 | DeltaNet out | 0.229 | 0.156 | 0.111 | 0.150 | 0.084 |
| 6 | streams | 0.374 | 0.367 | 0.258 | 0.348 | 0.105 |
| 7 | QSA out | 0.149 | 0.149 | 0.019 | 0.147 | 0.144 |
| 7 | QSA block selection | 2/21 | 2/21 | 0/21 | 2/21 | 1/21 |
| 7 | streams | 0.366 | 0.359 | 0.250 | 0.340 | 0.156 |

The full per-layer tables (every component, both precisions) are in `differential_sol_vs_twin_report.md`. The prototype reproduces the reference's bf16 hidden streams **bitwise through layer 0** and stays within one or two bf16 ulps through layer 2. The divergence that remains starts at the QSA attention core (D9). In the ports, the divergence starts at the first op of layer 0. The twin's bf16 block selection departs from the reference at both QSA layers; Sol's does not.

**bf16, isolated components.** Each port's module is fed the reference's exact bf16 input, so upstream divergence is removed and each component is judged on its own. Cells show the minimum over layers of the fraction of output elements bitwise equal to the reference.

| component | Sol | Sol (flag off) | twin | prototype | Sol vs twin | Sol (off) vs twin |
|---|---:|---:|---:|---:|---:|---:|
| attn / mlp HC mix | 0.956 | 0.560 | 0.641 | **1.000** | 0.642 | 0.729 |
| attn / mlp HC weights | 1.000 | 0.525 | 0.525 | **1.000** | 0.525 | 1.000 |
| DeltaNet | 0.205 | 0.203 | 0.498 | **0.969** (1.000 at layer 0) | 0.206 | 0.211 |
| PLE | 0.693 | 0.615 | 0.764 | **1.000** | 0.625 | 0.700 |
| QSA (whole layer) | 0.457 | 0.320 | 0.320 | 0.457 | 0.381 | 0.999 |
| QSA block selection | 0/21, 0/21 | 0/21, 0/21 | 0/21, 0/21 | 0/21, 0/21 | 0/21, 0/21 | 0/21, 0/21 |
| router logits | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| expert sets | 1.000 | 1.000 | 1.000 | 1.000 | - | - |
| MoE | 0.378 | 0.339 | 0.354 | **0.999** | 0.586 | 0.830 |
| final mixer | 0.967 | 0.562 | 0.657 | **1.000** | 0.656 | 0.729 |
| lm_head | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

In fp32 isolation every component of both ports matches the reference to at most 1.2e-6, and Sol vs twin to at most 7.8e-7.

Two cells settle structural questions. Sol (flag off) vs twin QSA = 0.999: Sol's per-query K/V gather and the twin's dense masked SDPA compute the same attention bit for bit; with the flag on, they differ only in the output-gate sigmoid. The first run of the prototype used the eager `index_add_` MoE combine and reached 0.853-0.865; with the `grouped_mm` fp32 combine it reaches 0.999 (D6).

## Disagreements, resolved against the reference

**D0. QSA exact ties at the top-k cut.** This is the only fp32 disagreement beyond noise.
- How the tie arises: a block's score is exactly 0.0 when every indexer head's dot product is <= 0 (relu). In the reference, 11 of 2,060 top-k calls have the K-th and (K+1)-th scores exactly equal. At layer 3, one sparse query row selects a different tied block in `torch.topk` (HF:749) than in the ports. The differing block's score equals the K-th score exactly (classified from the twin's recorded scores). This is the whole 0.12.
- Sol and the twin use the same rule:
  - Sol `qsa_topk` (S:345-369) is a stable argsort by score descending then block ascending. Its O(N) partition path, used when no tie crosses the cut, gives the same set.
  - The twin `topk_mask_lowest_index` (T:689-707) keeps `gt | (eq & cumsum(eq) <= need)`.
  - Both pick the same **set**. Order within it is irrelevant to attention, as the 0.999 bitwise gather-vs-mask agreement shows.
  - Forced-tie probe: one indexer projection is zeroed, so every visible block scores 0 (21 straddling ties). Sol and the twin give identical selections on 21/21 rows and logits within 3.8e-6.
- With the reference breaking ties the same way, all scenarios agree to 9.6e-6. **Neither port is wrong:** each is a deterministic member of the reference's tie-equivalence class, and torch's CPU tie order is implementation-defined. Real-weight QSA parity (GOAL items 5 and 11) must be tie-aware and log the tie rate, as the perf track also concluded.

**D1. Twin converter cannot read a bf16 checkpoint (twin bug).** `align_convert_qwen4_exp_twin.py:382-384` opens shards with `safe_open(path, framework="mlx")`. safetensors 0.8.0 builds those arrays through numpy, so it fails with `TypeError: data type 'bfloat16' not understood` (reproduced by `diag`). `mx.load` reads the same file as `mlx.core.bfloat16`. The released checkpoint is bf16; the twin's own parity test saves fp32, so it never hit this. Fix: read shards with `mx.load`, or with `safe_open(framework="numpy")` plus a uint16 view. Sol's converter passes raw bf16 bits through (`align_convert_qwen4_exp.py:151-174`).

**D2. RoPE inverse frequencies (Sol differs; twin is exact).** The reference computes `1.0 / (base ** (arange(0, dim, 2) / dim))` in fp32 (HF:114).
- Sol computes `theta ** (-arange/dim)` with MLX's fp32 `pow` (S:218). It differs in 3 of 8 entries at the test config and in **15 of 32 at the released config** (theta 1e7, rotary dim 64).
- The twin rounds a float64 pow once and takes the fp32 reciprocal (T:649-667). It differs in 0/8 and 0/32.
- Sol's phase error reaches 7.6e-6 rad by position 320, 1.2e-4 by 8K and **9.8e-4 by 40K**, and 1.2% of bf16 cos/sin values flip over 0-40K. That is invisible in this short test but a real disagreement at the 40,960-token cap, in main attention and in the indexer's block selection.
- **Twin is right.**

**D3. bf16 sigmoid (twin evaluates it natively; Sol rounds once with `jw_bf16_fp32_ops`).**
- torch evaluates bf16 `sigmoid` in fp32 and rounds once. Over all bf16 inputs in [-20, 20], `mx.sigmoid` on bf16 differs from torch on 3.0%; fp32-then-round differs on 0.0%.
- Sites:

| Site | Reference | Sol | Twin |
|---|---|---|---|
| DeltaNet beta | HF:572 | S:243-260 | T:942 |
| Attention output gate | HF:890 | S:469 | T:1146 |
| Hyper-connection sigmoids | HF:1015, 1022 | S:276-279 | T:868, 874 |
| Shared-expert gate | HF:988 | S:500 | T:1196 |
| PLE gate | HF:1242 | S:556 | T:1226 |

- **Sol (flag on) is right.** Turning the flag off also drops Sol's hyper-stream mean to MLX's bf16 `mean`, which differs from torch's fp32-accumulated mean on 33% of outputs (S:236-240). The twin always takes the mean in fp32, which is correct (T:871).
- The flag-off run is further from the bf16 reference: 0.34 vs 0.26 on long prefill, and 0.31 vs 0.28 against fp32. At short context it is slightly closer to fp32 (0.078 vs 0.097), a draw of rounding luck rather than semantics. **The canonical module should drop the flag: the promoted path is the reference semantics, not an option.**

**D4. Short-conv silu (Sol rounds twice; twin is exact).** The reference applies `F.silu` to the bf16 conv output (HF:241 DeltaNet, HF:1224 PLE), with one rounding. Sol uses `nn.silu` on bf16 (S:287), which differs from torch on 5.3% of bf16 inputs. The twin uses `silu_rounded_once` (T:627-636), which differs only on subnormal outputs (largest difference 1.2e-38). The conv itself is not the issue: `mx.conv1d` in bf16 is bit-identical to the fp32 sum rounded once (perf.md §2) and about 4x faster than the twin's 4-tap loop (T:598-624). **Twin is right on silu; keep Sol's `mx.conv1d`.**

**D5. Hyper-connection silu (both ports differ).** The reference computes `F.silu(input_mix_weight_down(normed) / hc)` (HF:1014). Both ports use bf16 `nn.silu` (S:276, T:867). The fix is fp32 silu rounded once; with it, the prototype's HC mix and weights are 1.000 bitwise at every layer.

**D6. MoE routed-output combine (Sol differs; twin matches the reference's default path).**
- The modeling file's own `Qwen4ExpTextExperts.forward` (HF:925-947) accumulates experts in bf16 with `index_add_`. But the class is wrapped by `@use_experts_implementation`, and `experts_implementation` resolves to `grouped_mm` (`modeling_utils.py:1882-1903`; recorded as `grouped_mm` in this run).
- That path, `grouped_mm_experts_forward`, sums the k weighted bf16 rows in fp32 and rounds once (`transformers/integrations/moe.py:499-505`, whose comment explains why).
- The twin does the same (T:1195). Sol sums in bf16 (S:499); MLX's bf16 `sum` accumulates in bf16 and differs from torch's on 80% of 64-term outputs.
- **Twin is right.** At k = 10 the twin's fp32 sum is also the more accurate choice. The prototype's isolated MoE goes from 0.86 with the `index_add_` emulation to 0.999 with the fp32 combine.

**D7. QSA score scale (Sol omits 1/sqrt(Di); twin matches).** HF:747 divides the head-summed relu scores by sqrt(index_head_dim). Sol does not (S:405). The twin does (T:1056). The division is monotone, so ranks are kept, but the rounded quotient can merge two adjacent fp32 scores into an exact tie, which the reference then resolves by its tie rule. Sol would order them strictly. No such case occurred here: the prototype, which divides, selects exactly Sol's blocks. **Twin is right**, for tie-set fidelity at real-weight scale.

**D8. PLE gate (both ports differ).** The reference computes `(key_normed * query_normed).sum(-1) / math.sqrt(hidden_size)` (HF:1240): a bf16 sum accumulated in fp32, then a division by the unrounded Python scalar (fp32 opmath).
- Sol sums in bf16 (S:554). The twin sums in fp32 and rounds once (T:1224), which is right.
- **Both then divide a bf16 MLX array by a Python float. MLX rounds that scalar to bf16 first:** sqrt(2560) = 50.596 becomes 50.5. That changes 28.8% of gate values at hidden 96 and **36.5% at the released hidden 2560**; dividing in fp32 and rounding once changes 0%.
- Fix: `(sum_fp32.astype(bf16).astype(fp32) / sqrt(H)).astype(bf16)`. The prototype's PLE is then 1.000 bitwise.
- Neither port's own parity test uses a hidden size with an inexact square root (both use 64).

**D9. QSA attention core in bf16: a reference artifact, not a port difference.** With identical bf16 q/k/v at layer 7 (no ties), MLX's fused SDPA output is bitwise equal to torch's CPU `sdpa_attention_forward` on 70.4% of elements, and equal to an fp32-exact emulation. More telling: re-running the reference's own layer-7 attention on the exact captured input, outside the full forward, matches its captured output on only **48.9%** of elements. Torch's CPU bf16 SDPA is not bitwise reproducible across call contexts. Everything around the core (q/k norms, RoPE, gate sigmoid, `o_proj`) is bitwise exact in the prototype. **No port change; keep fp32-accumulating attention (MLX SDPA or the perf kernel).**

**D10. Router and expert choice.** With identical inputs, router logits are bitwise equal across all three (1.000 at every layer, both precisions), and expert sets agree on 100% of tokens. Free-running bf16 expert-set differences (2.5-5% of tokens at some layers) follow from upstream activation differences (D3-D8); the router has no disagreement of its own.

## Convergence recommendation for the canonical module

Rules:
- Where the ports differ, take the reference-exact choice.
- Where both differ from the reference, take the fix that the prototype showed to be bitwise exact.
- Use the perf track's (PR #670) kernels where they are exact.

The prototype is Sol plus seven op-level changes; it is a numerics proof, not the module.

| Component | Adopt | Why |
|---|---|---|
| File layout: `TextModelArgs`, `ModelArgs(text_config)`, `Model.language_model`, `sanitize` | **Twin** (T:65-217, T:1385-1404, T:1455-1524) | Mirrors mlx-lm's own text port of a VLM checkpoint (`mlx_lm/models/qwen3_5.py`: `TextModelArgs`, `ModelArgs(text_config)`, the `model.language_model` → `language_model.model` mapping), so it is upstream house style. Validation mirrors the reference's `validate_architecture`. Sol's flat layout plus a sibling `qwen4_exp_tables.py` loaded through `spec_from_file_location` (S:25-30) puts a second file under GOAL item 4's sha256 pin. |
| RMSNorm (1 + w) | **Twin** (T:556-577, `mx.fast.rms_norm` on fp32) | Same math as the reference, fused. Both ports are 1-ulp fp32 in isolation. |
| RoPE frequencies | **Twin** `rope_inv_freq` (T:649-667) | 32/32 entries equal to the reference at the released config; Sol's differ in 15/32 (D2). |
| RoPE application | Already HF-exact in both (cos/sin cast to the model dtype, bf16 multiply-adds). Compute cos/sin once per forward as the twin's `_Step` does (T:833-847). | Perf critic HIGH item: `mx.fast.rope` (fp32 inside) changes bf16 indexer selection beyond ties, so the indexer must stay explicit. Use `mx.fast.rope` in main attention only if a bf16 parity run accepts it. |
| DeltaNet q/k normalisation and recurrence | Perf track's adapter: `Dk**-0.5 * rms_norm(q, eps=1e-6/Dk)`, an exact identity, feeding mlx-lm's `gated_delta_kernel` unchanged. Pass masks via Sol's seam (S:243-260), with masks from `create_ssm_mask(h, cache)`. | Fused and exact (perf: 5.5e-6 at real dims vs 2.8e-5 for mlx-lm's native eps). Both ports' explicit `rsqrt(sum + 1e-6)` is also exact but unfused. |
| DeltaNet and PLE short conv | **`mx.conv1d` (Sol, S:282-287) + silu in fp32 rounded once (twin, T:627-636)** | Exact and fast (D4). Isolated DeltaNet: 0.21 (Sol) and 0.50 (twin) become 0.97-1.00. |
| DeltaNet beta, attention gate, HC sigmoids, shared-expert gate, PLE sigmoid | **Sol's fp32 sigmoid rounded once** (S:229-233), always on; **drop `jw_bf16_fp32_ops`** | D3. |
| Hyper-connection | Sol's structure (S:263-279), fp32 mean (both), **silu rounded once (new)** | D5. 1.000 bitwise in the prototype. |
| QSA indexer scores | **Twin** `/ sqrt(Di)` (T:1052-1056) | D7. |
| QSA tie rule | Keep the shared rule (score descending, block ascending). Build it as the twin's mask (T:689-707) or the perf track's token-index builder, **not** Sol's `qsa_topk`. | Same set in both ports (D0). Sol's `mx.any(crosses).item()` (S:363) forces a GPU-to-host sync per QSA layer per call once the context exceeds the budget: 12 per decoded token at the released depth. |
| QSA block keys | **Twin's per-block cache** (`QSACache.blk_keys`, `_update_blocks`, T:715-787, T:986-1007), which is also the perf track's design | Sol recomputes every pooled, normed, roped block key on every call (S:397-404): O(T) work per decode step per QSA layer, with identical values. |
| QSA attention core | **Perf track (PR #670)**: dense causal at kv <= 2051, masked SDPA below 6144, the block-sparse Metal prefill kernel above, gather + SDPA for decode above 8192 | Sol's per-query K/V gather (S:454-468) copies `S x (budget + r - 1) x Hkv x D` per chunk, which is why Sol caps prefill chunks at 64 tokens. The twin's masked SDPA (T:1129-1144) is O(S x L). The two compute the same function bit for bit (0.999), but neither scales to 40K. |
| MoE router | Either (they are identical): fp32 softmax, `argpartition` on fp32 probabilities. Fold `shared_expert_gate` into the router matmul (perf). | Meets the perf requirement to rank fp32 probabilities. Remaining hazard: exact bf16 logit ties at the cut, where `argpartition` and `torch.topk` pick differently. Log their rate on real weights. |
| MoE experts | **Perf track's fused gate_up `gather_qmm`**, with **silu rounded once (new)** | Both ports use mlx-lm `SwitchGLU`, whose compiled `swiglu` evaluates silu in bf16. |
| MoE combine | **Twin**: fp32 sum of the k weighted rows, rounded once (T:1195) | D6: the reference's default `grouped_mm` path. |
| PLE n-gram ids and table | **Twin** `NgramHashSpec` + `NgramTable`, in the same file (T:273-548) | Ids identical to Sol's (PLE agrees to 7e-7 in fp32). Keeps the canonical module one hashed file, with f32/bf16/q8/q4 rows, mmap or `F_NOCACHE` pread, dedupe and fault counters for the paged-table work in GOAL item 6. |
| PLE gate | **Twin's fp32 sum (T:1224) + fp32 division by sqrt(H) (new)**, each rounded once | D8. |
| Caches and padding | Twin's cache-carried left padding (`make_cache(left_padding)`), rebuilt on mlx-lm's `ArraysCache(left_padding)` / `make_mask` protocol, **plus Sol's serializable cache state** (`state` / `meta_state` and registration in `mlx_lm.models.cache`, S:131-198) | House style carries padding in the cache (`create_attention_mask`, `create_ssm_mask`). ALIGN's prefix reuse needs prompt-cache save and load; the twin's `QSACache.state` setter raises (T:782-784). |
| Converter | **Sol's** (`scripts/align_convert_qwen4_exp.py`) | Raw bf16 passthrough, streaming, sha256 manifest, and the maxfit profiles the GOAL's memory plan is built on. The twin's cannot read the released bf16 checkpoint (D1). If the maxfit profile is ever lowered below "everything except experts in bf16", port the twin's keep-float list into Sol's predicate (router, shared gate, indexer, DeltaNet a/b, inject; T:1421-1447). |

**Net effect on the perf track's four findings.**
1. GDN eps `1e-6/Dk`: adopt; both ports already compute the same quantity unfused.
2. HF-exact bf16 RoPE in the indexer: both ports already do this. Combine it with the twin's exact `inv_freq`, which neither the perf track nor Sol had.
3. fp32 router ranking: both ports already do this.
4. Block-sparse QSA prefill kernel: adopt; it replaces both ports' attention cores, which compute the same function. Pair it with the twin's block-key cache and a host-sync-free tie rule.

## Follow-ups for the owning lanes

- Twin lane: fix D1 (bf16 source read). Its bf16 sigmoids (D3) explain why it misses its own bf16 noise-floor criteria on this checkpoint (worst 1.57x and 2.24x).
- Sol lane: fix D2 (RoPE `inv_freq`), D4 (conv silu), D6 (MoE combine), D7 (score scale), and make the promoted ops unconditional (D3).
- Both: D5 (HC silu), D8 (PLE gate divisor), and expert/shared SwiGLU silu. Add a parity config whose hidden size has an inexact square root, and add a bitwise isolated-component bf16 check to each parity test, as the `isolated` stage does here.
- Real-weight parity (GOAL items 5 and 11): QSA comparisons must be tie-aware and log ties per layer. Expect bf16 component checks to be bitwise except for the attention core (D9).

## Reproduce

```
cd <port-qwen4-exp clone>
nice -n 20 taskpolicy -b /private/tmp/jwsol/venv-both/bin/python scripts/qwen4exp_differential.py all --work /private/tmp/jwdiff/run1
# or stage by stage: ref | convert | mlx | diag | report  (each resumable)
```

Outputs: `ref.npz`, `ref_meta.json`, `results.json`, `diag.json`, `mlx_runs.npz` and `report.md` in `--work`. `differential_sol_vs_twin_report.md` is the `report.md` of this run.

Wall time was about 45 min. Almost all of it was the CPU-starved reference stage: the analysis job kept the machine at load 15-18, so the reference got 1-4% of a core. Its total CPU was about 60 s; the MLX stage took 74 s.
