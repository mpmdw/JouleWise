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
as the [proposed upstream diff](upstream-keep-last-zero.diff).

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
