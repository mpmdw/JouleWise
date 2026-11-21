# 2026-11-21 Flash-Next upstream parity

Draft [JouleWise PR #927](https://github.com/mpmdw/JouleWise/pull/927) targets
`main` from `align/2026-11-21-flashnext-upstream-parity`. The checkout started
at `64e29575d83f7e0ebde359653703c39c4a9b7ce6`.

| Commit | Change |
| --- | --- |
| `bcb53bcfdfb144dca48ee23c428762c3b13f7ad6` | Vendor the merged mlx-lm model with its MIT license, adapt the anonymous loader imports and add a pinned-runtime adapter test. |
| This commit | Add the tiny and byte-range layer harnesses, the recorded comparisons and the isolated upstream discrepancy reproductions. |

## Results

- Three random text configurations, each in FP32 and BF16, ran through
  Transformers 5.22.1, unmodified mlx-lm `c4c9c76`, and the historical
  JouleWise port at `97d780d59`. Every FP32 row met its gate. All sparse
  masks and 48 greedy continuation tokens matched per pair. The upstream
  BF16 prefill and cached logits in A exceeded the HF-derived bound.
- The real-weight run covered layers 1 and 2 (DeltaNet), 3 and 7 (QSA), and
  layer 1 PLE. Layer 3 also ran past the sparse budget. N-gram rows agreed
  exactly. All isolated MoEs exceeded their BF16 agreement screen. The
  router differences occurred on rows tied at the BF16 cutoff in the
  JouleWise port. Isolated experts with a common route and complete decoder
  outputs stayed within their respective screens. This was an MLX-vs-MLX
  check of converted weights.
- Two FP32 probes reproduced a rejected Transformers layer-type spelling
  and ignored `norm_topk_prob=False`. Both passed with the proposed
  two-change diff loaded from a separate local file. The vendored model
  uses the merged implementation with loader compatibility changes.
- The [fact sheet](../align/qwen4_exp_port/UPSTREAM-PARITY.md) contains the
  matrices, all out-of-bound rows, tolerances, artifact and checkpoint
  digests, and replay commands.

## Verification and resources

- The local pinned runtime passed
  `tests.test_qwen4_upstream_model_file` on MLX 0.31.2, mlx-lm 0.31.3 and
  Transformers 5.12.1. This opens a synthetic local checkpoint in
  `MlxRuntimeAdapter.prepare` and exercises sparse cached decode.
- The two existing MLX adapter modules passed their 50 stdlib tests. The
  vendored integration test skipped in that stdlib invocation and passed
  in the pinned runtime above.
- The Air's task scratch directory was
  `/Volumes/JW-EXT/scratch/pl-d-flashnext-upstream-parity`. Three venvs,
  wheel archives and each generated fixture stayed there. The 55 wheel
  archives totaled 237,894,711 bytes and the upstream shallow Git pack
  totaled 624,822 bytes, plus small Git and package metadata. Model
  weights were generated locally for the tiny fixtures. The 210 GB
  artifact was read in place and the manifest digest matched
  `6b481f145fcd3ab0242251be30ca460cc67e484652de11553332605833a1c3f9`.
  The native tests used offline Hub settings, `nice`, bounded workers
  and one loaded real layer per process.
- The local quick tier hit an existing timed fake-sampler test,
  `test_timeout_retains_220_complete_slow_frames_after_term_delay`.
  It observed zero complete frames instead of 220 on the branch retry
  and on a fresh extraction of the baseline commit. The local quick
  tier was stopped after the baseline reproduction.
- The full suite runs in the PR's hosted CI shards. On the vendor commit,
  build, installed-wheel, fences and quick passed. The full run was still
  in progress before the evidence commit. The gate ledger job skips
  draft PRs.

**NEEDS_SPEC** — None.

## Audit round 1 remediation

The round 1 audit blocked `588196e19` on one verified HIGH. The pinned
mlx-lm Metal kernel silently omitted the last 16 key coordinates in
fixture A with a 48-wide DeltaNet head. The vendor restores the dispatch
guard from `c4c9c76`. Every key width below 32 or indivisible by 32
now takes the portable recurrence. Supported widths still take the Metal
kernel during GPU inference.

The permanent adapter regression checks widths 16, 32, 48, 64, 80 and
128 through `model_file`. It compares prefill and cached decode with
the portable recurrence and verifies the selected kernel path. The
`vendor` stage in `scripts/qwen4_upstream_parity.py` also reproduces the
audit with Transformers 5.22.1 fixture A, seed 1105 and width 48. Its
FP32 prefill bound is `1e-4`.

| Width 48 prefill comparison | Before guard | After guard |
| --- | ---: | ---: |
| Transformers–vendor max absolute error | 0.8405828 | 1.3113e-6 |
| Upstream–vendor max absolute error | 0.8405834 | 0 |

The pre-fix replay exited with a parity failure. The fixed replay passed
the prefill, cached replay and eight greedy tokens against both reference
implementations. [Before](../align/qwen4_exp_port/evidence/vendor-width48-before.json) ·
[After](../align/qwen4_exp_port/evidence/vendor-width48-after.json)

The MED finding is a follow-up. The chained BF16 bound passed a halved
`B-bf16/L0.moe` output in the audit. An independent fixed-input,
fixed-route BF16 component gate requires a separate oracle and tolerance.
The fact sheet records the observed sensitivity limit. The three LOW
findings confirmed the published fixture replay, real-weight labeling
and download record.

The pinned adapter regressions, 50 stdlib adapter checks and generated
state check passed locally. This round reused the three SSD venvs and
generated the width-48 fixture locally. The full suite runs on the updated
draft in hosted CI.

## Audit round 2 remediation

The round 2 audit blocked `f1fa8e5e1` on the pinned loader accepting
upstream NVFP4 checkpoints. The original pinned stack changed the argmax
at 38 of 39 prefill positions on the unscaled fixture and produced a
maximum logit error of 9.3359375. Loading the per-expert global-scale
variant reached a `TypeError` in the pinned quantization API.

The vendored `model_file` accepts unquantized weights and native MLX affine
weight quantization. Validation checks top-level and nested metadata,
including per-layer overrides, before the pinned loader quantizes the
model. Tensor checks reject integer scale encodings and global scales
even when the declared mode is affine. The fact sheet qualifies the
checkpoint setup and includes an offline regression for both NVFP4
variants and one 6-bit affine control.

The upstream quantizer reproduced the audit's NVFP4 payload digests from
fixture C. A replay of the old vendor reproduced both failure modes.
Both NVFP4 variants now raise an explicit format error. The 6-bit affine
control passed against upstream at the `1e-4` bound for cached prefill and
decode. [Before](../align/qwen4_exp_port/evidence/pinned-quantization-before.json) ·
[After](../align/qwen4_exp_port/evidence/pinned-quantization-after.json)

Four pinned runtime tests passed, including the six-width dispatch and
decode coverage from round 1. The 50 stdlib adapter checks and generated
state check passed. This round reused the SSD venvs and the published
synthetic fixture weights. Hosted CI runs the full suite on the new
draft head.

The MED fixed-input, fixed-route BF16 oracle remains a follow-up. The
round 2 width-48 replay refuted the old HIGH on that case. The LOW findings
confirmed the fixture replay, the labeling of the SSD comparison and the
download record.
