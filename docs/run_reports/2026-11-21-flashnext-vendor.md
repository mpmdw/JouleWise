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
