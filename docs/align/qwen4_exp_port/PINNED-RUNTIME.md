# Flash-Next on the pinned ALIGN runtime

Copy [`qwen4_exp_upstream.py`](../../../joulewise/align/models/qwen4_exp_upstream.py)
next to the local checkpoint's `config.json`. Set
`"model_file": "qwen4_exp_upstream.py"` and the top-level `qwen4_norm_layout`
based on the exported tensors. Use `"zero_centered"` for HF or mlx-vlm
weights stored as `w` and `"folded"` for mlx-lm weights stored as `1 + w`.
The field describes the bytes in the checkpoint, so an export that folds
norm weights must write `"folded"` in its output config. Point the ALIGN
model source at that directory. The file derives from mlx-lm `c4c9c76` and uses MLX 0.31.2 and
mlx-lm 0.31.3. The 210 GB JouleWise-layout artifact continues to use its own
bundled loader and paged n-gram table.

## Supported formats and paths

| Surface | Supported |
| --- | --- |
| Schedule | At least four text layers. Three `linear_attention` layers followed by one `full_attention` layer, repeated up to the configured layer count. An omitted `layer_types` uses this schedule. `full_attention_interval` is 4. |
| PLE and DeltaNet | `ple_layer_ids=[2]` (one-indexed), `ple_conv_kernel_size=4`, `linear_conv_kernel_dim=4`, and `ngram_size=3`. |
| Sparse attention and hyper-connections | Enabled QSA on `full_attention` layers with a positive indexer head count and head dimension, one indexer KV head, compression ratio 4, and a positive budget divisible by 4. `hc_count=4`. |
| Text switches | Bias-free attention with zero dropout, untied embeddings, SiLU with a sigmoid output gate, shared and routed experts, and normalized top-k (the default). Default text RoPE has `partial_rotary_factor=0.25`, `mrope_interleaved=true`, and `mrope_section=[11,11,10]`. |
| MTP metadata | One hybrid `full_attention` layer with `rope_theta=10000000`, `mtp_use_hidden_state_from_layer=null`, and shared embeddings. Declare the `mtp` mapping, `mtp_num_hidden_layers=1`, and `mtp_use_dedicated_embeddings=false`. ALIGN generates through the text trunk. |
| Weight dtype | FP32 and BF16 checkpoint tensors. |
| Norm layout | Explicit top-level `qwen4_norm_layout` with `zero_centered` or `folded`. |
| Quantized weights | Native MLX affine, with a top-level `quantization` mapping. Group sizes 32, 64 and 128 and bit widths 2, 3, 4, 5, 6 and 8 are the pinned API's affine domain. Per-module overrides follow normalized, merged and repartitioned weights. Parts combined in one destination module must share its packing. |
| Generation | Single-request token-ID `stream_generate`, chunked prefill and cached decode with the model's unquantized in-memory caches. ALIGN can reuse a common episode prefix and rebuild its cache on a rewrite. |
| Kernels | Pinned SDPA and DeltaNet. The DeltaNet Metal kernel runs for key widths divisible by 32 and at least 32. The portable recurrence covers other key widths. |

Model dimensions, head counts, expert counts, vocabulary and total layer
count may scale within this structure. The loader raises
`UnsupportedByPinnedRuntime` with the field name for a structural mismatch
or missing norm layout declaration.

The loader raises `UnsupportedByPinnedRuntime` for unsupported checkpoint
formats and declared generation options. These include NVFP4 with and without
global scales, MXFP4, MXFP8, other quantization modes, legacy quantization
methods, activation quantization, FP16 weights, and quantized or rotating KV
caches. It also rejects declared batching, speculative decoding, saved prompt
caches and input embeddings. `BatchGenerator` takes an already loaded model, so
its cache setup raises the same error before prefill, even for one prompt.
Direct batched inputs, padded or foreign caches, and direct input embeddings
also raise this error at the model boundary.

The generation surface comes from the single-request `stream_generate`
calls and the `EpisodePromptCache` path in the ALIGN runner lanes
`9c40e4e5d`, `e901eb2a4`, and `9dbcb7c55`.

## Audit regressions

| Reproduction | Result on the pinned adapter |
| --- | --- |
| DeltaNet width 48 | FP32 prefill error against Transformers fell from 0.8405828 to `1.3113e-6`. The native suite covers widths 16, 32, 48, 64, 80 and 128. [Before](evidence/vendor-width48-before.json) · [After](evidence/vendor-width48-after.json) |
| NVFP4, unscaled and per-expert global scale | Before the guard, the unscaled model changed 38 of 39 prefill argmaxes and the scaled model raised a `TypeError`. Both now raise `UnsupportedByPinnedRuntime`. A uniform 6-bit affine control stays within `1.02e-6` of upstream across prefill and cached decode. [Before](evidence/pinned-quantization-before.json) · [After](evidence/pinned-quantization-after.json) |
| `BatchGenerator` with the audit prompts | The generator refuses at cache setup. Cached single-request decode on the same audit weights yields tokens 9 and 48, matching the Transformers reference. [Replay](evidence/audit-3-pinned-runtime.json) |
| Four 4-bit affine PLE shards under a 6-bit default | All four remapped heads load as 4-bit. Prefill and cached decode errors against upstream are `2.3842e-7` and `1.4902e-7`. [Replay](evidence/audit-3-pinned-runtime.json) |
| Width-one PLE and DeltaNet convolution caches | The local patch makes both caches retain zero steps at width 1. The audit 4 control matches Transformers at token 50. The structure gate requires width 4, and the native suite retains in-memory prefill and streaming coverage of the cache helper at widths 1, 2 and 4. [Replay and patch](UPSTREAM-PARITY-ADDENDUM-1.md) |
| Zero-centered norm weights with PLE disabled | The pinned loader refuses the exact mlx-vlm export at `text_config.ple_layer_ids`. Two released-structure checkpoints with identical tensor names exercise explicit `zero_centered` and `folded` declarations. [Replay and patch](UPSTREAM-PARITY-ADDENDUM-1.md) |

Run the native regressions in the existing pinned venv. `FIXTURES` points
to the local synthetic `C-fp32` and `C-bf16` directories generated by the
[parity harness](https://github.com/mpmdw/JouleWise/pull/927). The
quantization probe builds the two upstream NVFP4 regressions and the affine
control from those fixtures. The checkpoints are generated locally.

```sh
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1
nice -n 10 "$WORK/venvs/runtime/bin/python" -B -m unittest tests.test_qwen4_upstream_model_file
QUANTS=$(mktemp -d "$WORK/pinned-quants.XXXXXXXX")
nice -n 10 "$WORK/venvs/mlx/bin/python" -B scripts/qwen4_pinned_quantization_probe.py prepare "$QUANTS" --fixtures "$FIXTURES"
nice -n 10 "$WORK/venvs/runtime/bin/python" -B scripts/qwen4_pinned_quantization_probe.py verify "$QUANTS"
```

For release-structure parity, `FIXTURES` contains B and C in FP32 and
BF16 with Transformers, upstream and canonical traces. `PARITY` is the
`scripts/qwen4_upstream_parity.py` path from the merged evidence checkout.
The pinned replay attaches released MTP metadata and the appropriate norm
layout declaration to a temporary checkpoint using the same weights.

```sh
nice -n 10 "$WORK/venvs/runtime/bin/python" -B scripts/qwen4_pinned_release_parity.py "$FIXTURES" --harness "$PARITY" --output "$WORK/pinned-release-parity.json"
```
