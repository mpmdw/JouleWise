# JouleWise Qwen3.8-Flash-Next text port

**PROVISIONAL — MLX numerical and real-model validation are release blockers.**
This is owned code for mlx **0.31.2** / mlx-lm **0.31.3**, loaded through the
pinned library's `config.json` `model_file` seam. No stack pin changes.

## Memory planning

`joulewise.align.models.qwen4_exp_memory.memory_model` enumerates every text
tensor from the local HF config. The release has **176,943,899,520 text
parameters**: 120,795,955,200 routed expert parameters, 51,200,245,760 PLE table
parameters, and 4,947,698,560 others. Vision/MTP are omitted.

The table below is **decimal GB (10^9 bytes)**, group size 64, bf16 retained
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

The q4 offloaded table occupies **28,160,135,168 disk bytes**, including one
fp32 scale and bias per 160-element row. BF16 disk storage is 102,400,491,520
bytes; q8 is 53,760,258,048 bytes. Only gathered rows become MLX arrays.
At q4 a token gathers 16 rows / **1,408 logical bytes** before duplicates.

**Offload does not eliminate physical page-cache memory.** A uniform-access
estimate over 40,960 tokens touches about 8.93 GB of 16-KiB file pages. The
conservative page-span upper bound is 21.47 GB, giving a combined mixed
physical estimate of **101.35 GB before OS/other processes**, despite a
79.88 GB model peak. File pages are reclaimable; neither the page-cache
estimate nor the 3 GB reserve is a hard allocation bound. Model budget fits
the requested ~80 GB and the stated 115.4 GB GPU working set **on paper**.
Actual peak and zero swap must be measured before an ALIGN window. A model
estimate alone cannot guarantee that a machine never swaps.

Reproduce byte accounting without allocating model tensors:

```sh
python3 -B -m joulewise.align.models.qwen4_exp_memory tests/align/fixtures/qwen4_exp_text_config.json --chunk-tokens 64
```

Memory tests: `python3 -B -m unittest tests.align.test_qwen4_exp_memory` —
2 PASS. Includes the actual kit cap, official expert/PLE parameter counts,
mixed budget and context/chunk/bit-width tradeoffs.
