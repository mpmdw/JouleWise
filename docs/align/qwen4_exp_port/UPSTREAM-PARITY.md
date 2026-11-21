# Flash-Next parity at mlx-lm c4c9c76

## Implementations

| Implementation | Version and source |
| --- | --- |
| Transformers reference | 5.22.1, PyTorch 2.12.0 on CPU, eager attention |
| Upstream mlx-lm | Git source at `c4c9c762cc797fd979fc98645f5db5112753bbe9`, MLX 0.32.3 on Metal. [Merged PR #1788](https://github.com/ml-explore/mlx-lm/pull/1788) |
| JouleWise comparison port | `97d780d5959f2d295b953c4d497b8859ef7f1175`, MLX 0.32.3 on Metal. Module SHA-256 `f4ec75d16f0af0517b63e202abeef704c9a775e9111949ab003250d51d982c37`. [Historical port evidence](canonical.md) |
| Vendored runtime test | MLX 0.31.2, mlx-lm 0.31.3, Transformers 5.12.1 |

The upstream parity runs use the installed mlx-lm source, unmodified. The
vendored runtime test uses the JouleWise copy on its separate runtime pins.
The vendor changes are absolute imports, eager annotations for the anonymous
0.31.3 loader, and the upstream `normalize_qk` helper absent in 0.31.3.

## Tiny matrix design

Three random checkpoints per dtype on Apple Silicon. A/B/C reuse the mlx-vlm
audit's configs and prompt IDs and the canonical gold harness's weight
initializer, including nonzero RMSNorm offsets and PLE convolution weights.
Both MLX sides receive the same serialized Transformers tensors. The harness
exports the fused expert tensors and partitions the HF n-gram table into
equal row shards. Upstream's sanitizer splits gate/up and the n-gram table
by head and folds norm scales. JouleWise's sanitizer keeps fused expert
weights and the harness writes the n-gram rows into its paged format. Both
loads check all model parameter names and shapes. Each dtype uses its own
export from the CPU model cast to that dtype.

| Fixture | Seed | Layers, zero-indexed | Prompt | QSA budget/ratio/index heads | Streams | Routed experts/top-k |
| --- | ---: | --- | ---: | --- | ---: | --- |
| A | 1105 | DeltaNet + PLE, QSA | 11 tokens | 4 / 2 / 2 | 2 | 4 / 2 |
| B | 2116 | DeltaNet, DeltaNet + PLE, DeltaNet, QSA | 40 tokens | 8 / 4 / 2 | 4 | 8 / 3 |
| C | 3217 | DeltaNet, DeltaNet + PLE, DeltaNet, QSA | 40 tokens | 8 / 4 / 16 | 4 | 8 / 3 |

Prompts contain EOS to exercise the n-gram history reset. Each layer runs a
shared expert and routed MoE. The harness requires the QSA masks to remove
visible tokens in every fixture. The comparison records components on full
prefill, logits on full prefill and cached token-by-token replay, and eight
independent cached greedy continuation tokens per implementation.

Per row the floating-point gate uses maximum absolute error, with no relative
tolerance. FP32 uses `1e-4`, the existing gold threshold. BF16 uses
`max(1e-4, 1.5 × max|HF_bf16 − HF_fp32|)`, the existing gold multiplier
applied to each corresponding fixture and tensor, including the MLX pair.
This uses the reference's observed same-shape dtype change as the scale.
Indexer masks, sorted selected expert sets, and greedy tokens require exact
agreement. These gates apply to the tested tensors and prompts.

## Tiny results

All three pairs passed every FP32 row. All indexer masks and all 48 greedy
continuation tokens agreed per pair across the six fixtures. The upstream
BF16 final logits exceeded the row bound in A. The routed expert sets
differed in BF16 B and C. The remaining BF16 discrepancies are listed below.

Each cell is **FP32 / BF16**. Values are the maximum absolute difference
across the matching rows. For indexer masks, router sets and greedy tokens,
the values are counts of unequal entries across the matching rows.
Parentheses show failed rows over total rows when there is a failure.
Thresholds are stored per fixture and row in the [full results](evidence/tiny-results.json).

| Component or output | HF–upstream | HF–JouleWise | Upstream–JouleWise |
| --- | ---: | ---: | ---: |
| L0 hidden | 1.669e-06 / **0.2188 (1/3)** | 1.669e-06 / 0 | 7.153e-07 / **0.2188 (1/3)** |
| L1 hidden | 5.782e-06 / **0.2725 (1/3)** | 6.109e-06 / 0.01562 | 5.364e-06 / **0.2725 (1/3)** |
| L2 hidden | 5.707e-06 / 0.2986 | 5.677e-06 / 0.02344 | 5.722e-06 / 0.2986 |
| L3 hidden | 5.648e-06 / 0.2861 | 5.513e-06 / 0.1172 | 5.484e-06 / 0.2881 |
| DeltaNet | 1.669e-06 / **0.151 (6/7)** | 2.839e-06 / 0.01172 | 2.593e-06 / **0.151 (6/7)** |
| QSA | 3.874e-07 / **0.02417 (1/3)** | 3.874e-07 / 0.003906 | 2.98e-07 / **0.02441 (1/3)** |
| QSA indexer mask | 0 / 0 | 0 / 0 | 0 / 0 |
| Attention HC mix | 9.835e-07 / **0.09375 (4/10)** | 1.132e-06 / 0.007812 | 1.132e-06 / **0.09375 (4/10)** |
| Attention HC inject | 2.384e-07 / **0.01562 (6/10)** | 2.384e-07 / 0.007812 | 2.384e-07 / **0.01562 (5/10)** |
| MLP HC mix | 9.239e-07 / **0.09277 (4/10)** | 1.132e-06 / 0.007812 | 1.103e-06 / **0.09277 (4/10)** |
| MLP HC inject | 2.384e-07 / **0.02344 (6/10)** | 4.768e-07 / 0.007812 | 3.576e-07 / **0.02344 (6/10)** |
| MoE | 4.172e-07 / **0.2119 (3/10)** | 6.035e-07 / 0.1028 | 3.651e-07 / **0.2119 (3/10)** |
| Router expert sets | 0 / **13 (7/10)** | 0 / **3 (1/10)** | 0 / **10 (7/10)** |
| Shared expert | 4.023e-07 / **0.03754 (3/10)** | 6.668e-07 / 0.003906 | 5.178e-07 / **0.03802 (3/10)** |
| N-gram rows | 0 / 0 | 0 / 0 | 0 / 0 |
| PLE | 5.484e-06 / **0.1719 (1/3)** | 5.96e-06 / 0 | 4.768e-06 / **0.1719 (1/3)** |
| Final HC mixer | 8.941e-07 / **0.08105 (1/3)** | 8.643e-07 / 0.03125 | 8.345e-07 / **0.08203 (1/3)** |
| Prefill logits | 1.967e-06 / **0.1875 (1/3)** | 2.086e-06 / 0.05469 | 1.729e-06 / **0.1875 (1/3)** |
| Cached replay logits | 1.907e-06 / **0.1953 (1/3)** | 2.384e-06 / 0.01562 | 1.311e-06 / **0.1953 (1/3)** |
| Greedy tokens | 0 / 0 | 0 / 0 | 0 / 0 |

### Rows outside tolerance

Every failing comparison is represented by a fixture, row, and pair below.
The full results record the bound, maximum-error coordinate, the two values,
RMS error and unequal-entry count for each row. The row reproduction command
in the next section accepts each of these fixture and row names.

| Fixture | Pair | Failing rows |
| --- | --- | --- |
| A-bf16 | HF–upstream | `L0.attn_hc.inject`, `L0.attn_hc.mix`, `L0.delta`, `L0.hidden`, `L0.mlp_hc.inject`, `L0.mlp_hc.mix`, `L0.moe`, `L0.shared`, `L1.attn_hc.mix`, `L1.hidden`, `L1.mlp_hc.inject`, `L1.mlp_hc.mix`, `L1.moe`, `L1.qsa`, `L1.shared`, `logits`, `mixer`, `stepwise` |
| A-bf16 | Upstream–JouleWise | `L0.attn_hc.inject`, `L0.attn_hc.mix`, `L0.delta`, `L0.hidden`, `L0.mlp_hc.inject`, `L0.mlp_hc.mix`, `L0.moe`, `L0.shared`, `L1.attn_hc.mix`, `L1.hidden`, `L1.mlp_hc.inject`, `L1.mlp_hc.mix`, `L1.moe`, `L1.qsa`, `L1.shared`, `logits`, `mixer`, `stepwise` |
| B-bf16 | HF–upstream | `L0.attn_hc.inject`, `L0.attn_hc.mix`, `L0.delta`, `L0.mlp_hc.mix`, `L0.router`, `L1.delta`, `L1.mlp_hc.inject`, `L1.moe`, `L1.router`, `L2.router` |
| B-bf16 | Upstream–JouleWise | `L0.attn_hc.inject`, `L0.attn_hc.mix`, `L0.delta`, `L0.mlp_hc.mix`, `L0.router`, `L1.delta`, `L1.mlp_hc.inject`, `L1.moe`, `L1.router`, `L2.router` |
| C-bf16 | HF–upstream | `L0.attn_hc.inject`, `L0.attn_hc.mix`, `L0.delta`, `L0.mlp_hc.inject`, `L0.mlp_hc.mix`, `L0.router`, `L0.shared`, `L1.attn_hc.inject`, `L1.delta`, `L1.mlp_hc.inject`, `L1.ple`, `L1.router`, `L2.attn_hc.inject`, `L2.delta`, `L2.router`, `L3.attn_hc.inject`, `L3.mlp_hc.inject`, `L3.router` |
| C-bf16 | HF–JouleWise | `L3.router` |
| C-bf16 | Upstream–JouleWise | `L0.attn_hc.inject`, `L0.attn_hc.mix`, `L0.delta`, `L0.mlp_hc.inject`, `L0.mlp_hc.mix`, `L0.router`, `L0.shared`, `L1.attn_hc.inject`, `L1.delta`, `L1.mlp_hc.inject`, `L1.ple`, `L1.router`, `L2.attn_hc.inject`, `L2.delta`, `L2.router`, `L3.mlp_hc.inject`, `L3.router` |

### Shared checkpoint digests

| Fixture | HF tensor export SHA-256 |
| --- | --- |
| A-bf16 | `d812c7fe84b37737779d3e5892d61a2f20116026c93e5044f08eb6fb40b93ef9` |
| A-fp32 | `2e33426e86762fbb54a5a7bc9c602708c118ef6b9eb593e669ba3678b3c6ea1d` |
| B-bf16 | `70c606327d96f9884d881d13d1b7b521767e88d5c1617dd060c5fde0c73746d0` |
| B-fp32 | `bd48338d929d0dc3f1f5a128363b1d339d80e243a2a0db47502fca2331b49c36` |
| C-bf16 | `d01af734d720e9efe231011dc5960990db3df508d2ff5c7cd482e592f2387db1` |
| C-fp32 | `c89052881c346d07c0ec243e975c958772cf5e313f5423b57503e25685733b96` |

## Reproduction

The tests use local source and weights generated by the CPU reference.
`PORT` is a checkout at `97d780d5959f2d295b953c4d497b8859ef7f1175`.
`WORK/venvs/reference` contains Torch 2.12.0 and Transformers 5.22.1.
`WORK/venvs/mlx` contains MLX 0.32.3 and mlx-lm installed from the merged
checkout at `c4c9c762cc797fd979fc98645f5db5112753bbe9`.

```sh
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
nice -n 10 "$WORK/venvs/reference/bin/python" scripts/qwen4_upstream_parity.py reference "$WORK/tiny" --port "$PORT"
nice -n 10 "$WORK/venvs/mlx/bin/python" scripts/qwen4_upstream_parity.py upstream "$WORK/tiny"
nice -n 10 "$WORK/venvs/mlx/bin/python" scripts/qwen4_upstream_parity.py port "$WORK/tiny" --port "$PORT"
nice -n 10 "$WORK/venvs/mlx/bin/python" scripts/qwen4_upstream_parity.py compare "$WORK/tiny"
```

Each stage accepts `--case A|B|C` and `--dtype fp32|bf16`. For a BF16
comparison the same fixture's FP32 reference output supplies the tolerance.
`compare --case B --dtype fp32 --row L3.indexer` prints a single row with the
maximum-error coordinate and the values on both sides. A layer row uses
`L<index>.<component>`. Each fixture's `config.json`, `hf.safetensors`
and per-implementation NumPy output are produced locally.

## Discrepancies isolated in upstream code

| Probe | Merged commit observation | Local candidate |
| --- | --- | --- |
| Transformers spelling `indexed_attention` | Changing only the QSA layer spelling in A fails model construction with `ValueError: 'full_attention' is not in list`. The released checkpoint's `full_attention` spelling constructs the model. | Accepts both spellings. |
| `norm_topk_prob=False` | A's first MoE on three fixed FP32 vectors still renormalizes the selected weights. The selected full-softmax mass is 0.90658, 0.99979 and 0.91576. Max output difference from weighting the same experts by their unrenormalized mass is 0.14441. | Max difference 0. |
| BF16 grouped RMSNorm | On A's input embeddings, the upstream folded scale differs from the FP32 `1+w` scale by up to 0.00390625. The upstream group-norm output differs by up to 0.015625 from FP32 normalization and scaling rounded once to BF16. | — |
| BF16 DeltaNet decay | On the three BF16 input pairs in the probe, mlx-lm's `compute_g` differs from FP32 addition and softplus by up to 0.000380525. Transformers promotes `a` before adding the bias. | — |

The RMSNorm and decay probes isolate arithmetic choices. The tiny decoder
traces include propagation through earlier components. Fixture A's BF16
prefill logit error is 0.09765625 against HF, with a 0.0635108 bound.
Fixtures B and C have upstream prefill errors of 0.1875 and 0.140625 with
bounds of 0.288588 and 0.206586 respectively.

The [configuration and router diff](qwen4_exp-config-router.diff) applies to
`c4c9c76`. The candidate results are from loading a separate local file
containing that diff. The vendored runtime file retains the upstream model
arithmetic. The [merged](evidence/upstream-probe.json),
[candidate](evidence/patched-probe.json) and [BF16](evidence/bf16-probe.json)
probe records include the input scopes and maximum-error coordinates.

```sh
nice -n 10 "$WORK/venvs/mlx/bin/python" scripts/qwen4_upstream_probe.py "$WORK/tiny/A-fp32"
nice -n 10 "$WORK/venvs/mlx/bin/python" scripts/qwen4_upstream_probe.py "$WORK/tiny/A-bf16" --bf16
```

## ALIGN model_file setup

For a local upstream-layout mlx-lm checkpoint, copy
[`qwen4_exp_upstream.py`](../../../joulewise/align/models/qwen4_exp_upstream.py)
alongside its `config.json` and set `"model_file": "qwen4_exp_upstream.py"`.
The source in the existing ALIGN model config remains the checkpoint directory.
The runtime test builds a tiny local checkpoint and tokenizer, opens it via
`MlxRuntimeAdapter.prepare`, and compares sparse cached decode against a fresh
prefill. The 210 GB JouleWise artifact uses its bundled historical model file
and its own packed experts and paged n-gram layout.

## Converted SSD artifact

The second experiment is **MLX-vs-MLX implementation agreement on converted
weights**. It has no Transformers reference. The local artifact manifest
SHA-256 is `6b481f145fcd3ab0242251be30ca460cc67e484652de11553332605833a1c3f9`.
The harness checks the manifest digest and the selected tensor ranges. It
reads the source files in read-only mode.

The two layers use the same weights from one layer at a time. The harness
splits the packed gate/up tensors, scales and biases at the output-row
boundary for upstream, leaving the 6-bit affine group-64 payload intact.
Upstream's layout also joins hyper-connection down and inject projections and
folds offset norms. Inputs are seeded BF16 tensors and fixed token IDs for
each layer and length. The PLE comparison calls upstream's hash and PLE
forward methods with per-head gathers backed by the artifact's BF16 row file.
The JouleWise side uses its own hash and the same row file. The upstream
checkpoint-wide loader and its resident n-gram embeddings are outside this
run.

The real-weight screen uses maximum absolute error with
`atol = max(1e-4, 0.02 × max|JouleWise output|)`. This sets a 2% output-range
agreement screen for BF16 operations on identical converted weights. N-gram
rows, sparse indexer masks and routed expert sets require exact agreement.

Values are **max absolute error / bound** for upstream vs JouleWise.
All other pairs have no measurement in this experiment. The JSON links
include each maximum-error coordinate and values. The router column gives
changed expert-set rows and rows tied at the JouleWise BF16 cutoff.

| Layer and tokens | Attention | Attention HC mix | Full hidden | Isolated MoE | Same-index experts | Shared expert | Router changed / tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [L1, 16, DeltaNet + PLE](evidence/real/L1.json) | 0.0039062 / 0.010547 | 0.023438 / 0.047188 | 0.0078125 / 0.025938 | **0.0025482 / 0.00035645** | 0.00045776 / 0.00064453 | 0.00024414 / 0.00071777 | 2 / 2 |
| [L2, 16, DeltaNet](evidence/real/L2.json) | 0.0019531 / 0.0082813 | 0.023438 / 0.051875 | 0.019531 / 0.024688 | **0.011108 / 0.0009375** | 0.00036621 / 0.0023242 | 0.00036621 / 0.001709 | 4 / 5 |
| [L3, 16, QSA](evidence/real/L3.json) | 0.0048828 / 0.015 | 0.011719 / 0.033906 | 0.023438 / 0.036094 | **0.0022202 / 0.00032715** | 0.00024414 / 0.00085938 | 0.00012207 / 0.00046875 | 1 / 2 |
| [L7, 16, QSA](evidence/real/L7.json) | 0.0092773 / 0.029531 | 0.015625 / 0.054375 | 0.015625 / 0.035313 | **0.0019073 / 0.00042969** | 0.00042725 / 0.00062256 | 0.00024414 / 0.00072266 | 1 / 3 |
| [L3, 2056, QSA](evidence/real/L3-sparse.json) | 0.0075684 / 0.015781 | 0.023438 / 0.047813 | 0.026855 / 0.035781 | **0.0039062 / 0.00052734** | 0.00036621 / 0.0021094 | 0.00024414 / 0.0011084 | 129 / 236 |

Layer 1 n-gram rows matched exactly across all 16 heads. The PLE output
error was 0.00292969 against a 0.00691406 bound. The 2056-token layer 3
test pruned visible tokens on five queries in each implementation and
its indexer masks matched exactly.

All changed router rows had a tie at the JouleWise BF16 cutoff. Upstream
projects router inputs in FP32. The JouleWise port computes BF16 router
logits, then ranks their FP32 softmax probabilities. Both routed expert
implementations stayed within the screen with the same indices. The
unconstrained MoE output exceeded the screen in all five runs.

The largest selected layer payload was 2.27 GB. Peak MLX memory was
5.27 GB in the 2056-token run. Each layer ran in a separate process.

```sh
for layer in 1 2 3 7; do
  nice -n 10 "$WORK/venvs/mlx/bin/python" scripts/qwen4_real_layer_parity.py \
    "$ARTIFACT" "$PORT" "$layer" "$WORK/L$layer.json"
done
nice -n 10 "$WORK/venvs/mlx/bin/python" scripts/qwen4_real_layer_parity.py \
  "$ARTIFACT" "$PORT" 3 "$WORK/L3-sparse.json" --tokens 2056
```

`ARTIFACT` is the local `/Volumes/JW-EXT/flashnext/work/artifact` directory.
