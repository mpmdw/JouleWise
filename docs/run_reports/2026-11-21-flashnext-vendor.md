# 2026-11-21 Flash-Next vendor split

The lead split the reproducible parity results and the pinned runtime after
audit 3. [PR #927](https://github.com/mpmdw/JouleWise/pull/927) retains the
offline harness, evidence and fact sheet. The normal revert
`52f2e9c39` separates the vendor from that draft. The
`align/2026-11-21-flashnext-vendor` branch starts from main at `3a66be202`
and cherry-picks the original vendor work. Its final diff contains the
pinned model, compatibility tests, audit replays and setup instructions.

The runner search covered main, the ALIGN measurement lane `9c40e4e5d`,
the R1 integration lane `e901eb2a4`, and the Flash-Next engine lane
`9dbcb7c55`. Their Apple endpoints pass single-request token IDs to
`stream_generate`, with optional episode-prefix cache reuse. None calls
`BatchGenerator`. The model exposes matching attention and indexer cache
offsets for the episode-prefix length checks. ALIGN's existing rebuild
path handles history rewrites.

## Audit dispositions

- Round 1 verified the pinned Metal width defect. The dispatch guard keeps
  the portable path for unsupported widths. The pinned suite retains the
  48-wide regression alongside other supported and fallback widths.
- Round 2 verified the NVFP4 numerical failure and per-expert scale API
  failure. Both exact quants now raise the named format error. The probe
  retains a same-weights 6-bit affine control.
- Round 3 verified the batched offset defect. `BatchGenerator` now fails
  at cache setup, including the replay with both audit prompts and with a
  single prompt. Single-request decode matched Transformers on the same
  audit weights. The native test exercises the actual `stream_generate` path.
- Round 3 verified the lost affine PLE overrides. The loader now carries
  each source module's affine recipe through path renames, grouped
  projections and row-shard repartitioning. The replay loads four 4-bit
  PLE heads under a 6-bit default, and it matches upstream within
  `2.3842e-7`. The regression also covers a direct mixed-group override
  through prefix normalization.
- The independent fixed-input, fixed-route BF16 component gate remains
  a follow-up on the evidence lane.

Setup, the allowlist and digests appear in
[PINNED-RUNTIME.md](../align/qwen4_exp_port/PINNED-RUNTIME.md).
Nine pinned runtime tests and 50 stdlib adapter tests passed. The
state-generation checks passed on both branches. The parity matrix
recomputed byte for byte from the stored traces after the split.
Verification used the existing SSD venvs and local synthetic weights.
The runtime pins and SSD artifact remained in place. Hosted CI runs
the full suite on both drafts.

## Audit 4

The width-one PLE and DeltaNet convolutions both passed zero to
`_keep_last`. Their unpadded caches kept the prefix. The n-gram history
also uses this helper and has at least two n-gram orders when PLE is
active. The indexer appends keys to its KV cache and uses prefix slices
with nonnegative bounds.

Both width-one native regressions failed before the fix because their
caches kept four positions after the first chunk. After the shared fix,
61 pinned runtime and adapter tests passed. Coverage includes PLE
widths 1, 2 and 4 and DeltaNet width 1 through prefill and streaming.
The audit checkpoint regenerated with the same SHA-256. The patched
vendor and the patched upstream checkout both restored the one-token
continuation shape and token 50, with cached final-position error
`7.15256e-7` against Transformers. On the audit's width-one DeltaNet
checkpoint, cached and uncached final logits agreed within `5.36442e-7`.
The released config uses width 4 on both convolution paths.

The [addendum](../align/qwen4_exp_port/UPSTREAM-PARITY-ADDENDUM-1.md)
records the reproduction and the one-line upstream diff. Audit 4
changes are confined to PR #930. Verification used local venvs and
locally generated tiny weights. The released artifact was read only
for its configuration.

## Audit 5

The pinned loader validates the released text architecture before model
construction. It checks the three-DeltaNet/one-full-attention pattern,
one-indexed PLE layer 2, both convolution widths of 4, normalized top-k,
enabled QSA with one KV head and compression ratio 4, four hyper-connection
streams, and the released MTP declaration. The 48-layer artifact config
passed structure validation with the explicit norm label supplied in
memory. Only `config.json` was read from the artifact.

The loader applies the `1 + w` fold from the checkpoint's top-level
`qwen4_norm_layout`. Identical tensor names with each explicit layout
produce the same logits. The exact audit mlx-vlm export reproduced its
original digest and now raises `UnsupportedByPinnedRuntime` naming
`text_config.ple_layer_ids`. On upstream `c4c9c76`, the proposed diff and
explicit `zero_centered` label restored token 22 from token 27 and reduced
cached final-position max error from `2.26621` to `5.96046e-7`. The replay
used the existing mlx-vlm 0.7.12 code wheel and generated the weights locally.
[Defect 4 reproduction and patch](../align/qwen4_exp_port/UPSTREAM-PARITY-ADDENDUM-1.md#defect-4--zero-centered-norms-without-ple)

B and C were regenerated in FP32 and BF16 using the merged parity harness.
The pinned replay used the same weights with the released MTP declaration
and explicit norm label. Each fixture and dtype has 43 rows. The table
counts rows outside the original tolerances (`1e-4` FP32, reference dtype
drift bound for BF16, exact for routing, indexer masks and greedy tokens).

| Fixture | HF vs upstream | HF vs canonical | Upstream vs canonical | HF vs pinned | Upstream vs pinned | Canonical vs pinned |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B FP32 | 0 | 0 | 0 | 0 | 0 | 0 |
| C FP32 | 0 | 0 | 0 | 0 | 0 | 0 |
| B BF16 | 10 | 0 | 10 | 10 | 0 | 10 |
| C BF16 | 18 | 1 | 17 | 18 | 0 | 17 |

All greedy tokens matched. The 86 upstream-vs-pinned BF16 rows matched
exactly, with the same BF16 discrepancies against the other runtimes as
the merged evidence. The native and adapter suites passed 65 tests.
The regenerated 6-bit affine control stayed within `1.02e-6` of
upstream, and both NVFP4 variants raised `UnsupportedByPinnedRuntime`.
