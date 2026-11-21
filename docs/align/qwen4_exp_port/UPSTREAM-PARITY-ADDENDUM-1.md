# Flash-Next upstream parity addendum 1

## Width-one convolution cache

In mlx-lm `c4c9c762cc797fd979fc98645f5db5112753bbe9`, `_keep_last`
uses `x[:, -n:]` when the cache has no padding lengths. With `n=0`, the
slice starts at zero and retains the entire prefix. A width-one PLE
convolution needs zero previous steps. After a cached prefix, the next
call concatenates that prefix with the new input and returns logits for
extra positions. Width-one DeltaNet convolution also calls `_keep_last`
with zero. Its reshape can fail on cached continuation.

FP32 fixture A (seed 1105) with `ple_conv_kernel_size=1` uses the same
synthetic weights in each row. Full-prefill and final-position cached
errors are maximum absolute logit differences against uncached
Transformers 5.22.1 CPU, with an FP32 tolerance of `1e-4`. The prompt IDs
are `[7, 8, 9, 10, 2, 12, 13, 14, 15, 16, 17]` and the cached continuation
feeds the final prompt ID after a ten-token prefix. The stream column
records the first greedy token for the full prompt.

| Implementation | Full-prefill error | One-token continuation shape | Cached final-position error | Greedy token |
| --- | ---: | --- | ---: | ---: |
| Transformers reference | — | — | — | 50 |
| Upstream `c4c9c76` | `9.53674e-7` | `(1, 11, 64)` | `1.72959` | 38 |
| Pinned vendor before patch | `9.53674e-7` | `(1, 11, 64)` | `1.72959` | 38 |
| Upstream `c4c9c76` with proposed patch | `9.53674e-7` | `(1, 1, 64)` | `7.15256e-7` | 50 |
| Pinned vendor with local patch | `9.53674e-7` | `(1, 1, 64)` | `7.15256e-7` | 50 |

The released artifact `config.json` sets both `ple_conv_kernel_size` and
`linear_conv_kernel_dim` to 4 in `text_config`, so neither convolution asks
to keep zero steps. The pinned vendor carries the same one-line change
as the [proposed upstream diff](upstream-keep-last-zero.diff). The vendor
rows above record the audit 4 runs. The current pinned loader rejects
that fixture at `text_config.ple_layer_ids` and rejects width one in an
otherwise released configuration at `text_config.ple_conv_kernel_size`.

## Offline reproduction

`WORK` is the scratch directory with the existing `reference`, `mlx`, and
`runtime` venvs. The `mlx` venv contains mlx-lm at `c4c9c76`. `GOLD` is the
canonical checkout at `97d780d59`. Run from the JouleWise vendor checkout.
The probe generates FP32 weights with SHA-256
`c4fe88d0128622dcd64f47ccabee230efe337a3f1752023c851e866142627520`.

```sh
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false
FIXTURE=$(mktemp -d "$WORK/ple-cache.XXXXXXXX")
nice -n 10 "$WORK/venvs/reference/bin/python" -B scripts/qwen4_ple_cache_probe.py prepare "$FIXTURE" --gold-checkout "$GOLD"
nice -n 10 "$WORK/venvs/mlx/bin/python" -B scripts/qwen4_ple_cache_probe.py upstream "$FIXTURE"
nice -n 10 "$WORK/venvs/runtime/bin/python" -B scripts/qwen4_ple_cache_probe.py pinned "$FIXTURE"
```

The minimal cache reproduction passes a `(1, 2, 1)` array to
`_keep_last(x, n=0, lengths=None)`. The original code returns shape
`(1, 2, 1)` and the patch returns `(1, 0, 1)`.

## Defect 4 — zero-centered norms without PLE

The Qwen4 RMSNorm tensors in an mlx-vlm 0.7.12 export store `w`, with
runtime scale `1 + w`. In mlx-lm `c4c9c76`, `sanitize` recognizes this
export by a `language_model.` weight key containing an n-gram shard name.
With `ple_layer_ids=[]`, the export contains no such keys. The loader
applies `w` as the scale and returns different logits. Its gated DeltaNet
output norm uses a direct scale.

FP32 fixture A, seed 1105, uses `ple_layer_ids=[]` and the same 11-token
prompt as the width-one reproduction. The comparisons use Transformers
5.22.1 CPU, with `atol=1e-4` and `rtol=0`. The first greedy token matches
the reference's final-position argmax when the fold is applied.

| Implementation | Full-prefill max error | Cached last-position max error | Next token |
| --- | ---: | ---: | ---: |
| Transformers reference | — | — | 22 |
| mlx-vlm 0.7.12 | `8.34465e-7` | — | 22 |
| Upstream `c4c9c76` and pinned vendor at `ab454f9e4` | `2.97393` | `2.26621` | 27 |
| Upstream `c4c9c76` with the proposed patch and `qwen4_norm_layout="zero_centered"` | `8.34465e-7` | `5.96046e-7` | 22 |

The released Flash-Next config has `ple_layer_ids=[2]`. A PLE-enabled
mlx-vlm export contains the n-gram shards that trigger the original
norm conversion, so this no-PLE defect is latent for the release. The
pinned `model_file` now requires `qwen4_norm_layout` for supported exports
and refuses the audit checkpoint at `text_config.ple_layer_ids`. The
[proposed upstream diff](upstream-explicit-norm-layout.diff) adds the
config field and retains the legacy inference rule for unlabelled
checkpoints. Re-exported tensors use the label for the representation
actually written.

### Offline reproduction

`WHEEL` points to `mlx_vlm-0.7.12-py3-none-any.whl`, the 3.64 MB published
code wheel. The SHA-256 is
`0412a883ed5f0ee2fe65e6c050819ae586ac76f1811f94a373b6293e92568e37`.
The probe generates the checkpoint locally. The mlx-vlm export has
SHA-256 `317a97de1b47af5217a290829f998ccbe035626e6cec800d4141a296945a25ff`.
`UPSTREAM` is the local mlx-lm `c4c9c76` checkout. Use the offline
environment and venvs above.

```sh
REPLAY=$(mktemp -d "$WORK/norm-layout.XXXXXXXX")
nice -n 10 "$WORK/venvs/reference/bin/python" -B scripts/qwen4_norm_layout_probe.py prepare "$REPLAY" --gold-checkout "$GOLD"
nice -n 10 "$WORK/venvs/mlx/bin/python" -B scripts/qwen4_norm_layout_probe.py export "$REPLAY" --wheel "$WHEEL"
nice -n 10 "$WORK/venvs/mlx/bin/python" -B scripts/qwen4_norm_layout_probe.py upstream "$REPLAY"
nice -n 10 "$WORK/venvs/runtime/bin/python" -B scripts/qwen4_norm_layout_probe.py pinned "$REPLAY"

PATCHED="$REPLAY/patched"
mkdir "$PATCHED"
git -C "$UPSTREAM" archive c4c9c76 mlx_lm | tar -xf - -C "$PATCHED"
git -C "$PATCHED" apply "$PWD/docs/align/qwen4_exp_port/upstream-explicit-norm-layout.diff"
cp "$WORK/venvs/mlx/lib/python3.13/site-packages/mlx_lm/_version.py" "$PATCHED/mlx_lm/"
PYTHONPATH="$PATCHED" nice -n 10 "$WORK/venvs/mlx/bin/python" -B scripts/qwen4_norm_layout_probe.py upstream-fixed "$REPLAY"
```
