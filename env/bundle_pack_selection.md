# REPRO-2 prep: bundle-pack selection (no publishing yet)

Spec: `docs/specs/c027/doc-009_repro-001_authority_and_repro.md` Part B,
REPRO-2 decision 1. This file records the recommended selection and
measured sizes only; packing/publishing is separate REPRO-2 work.

## Recommended pack contents (spec decision 1: 3 bundles)

Sizes measured 2026-07-09 with `du -sh` on the main checkout's `runs/`
(bundles are untracked; they live only in the primary working tree):

| Bundle | Model | `du -sh` |
| --- | --- | --- |
| `runs/example-mac-mlx-local__r1` | Qwen2.5-1.5B-Instruct-4bit | 16M |
| `runs/example-mac-mlx-local__r2` | Qwen2.5-1.5B-Instruct-4bit | 16M |
| `runs/example-mac-mlx-qwen35-122b-512t__r1` | Qwen3.5-122B-A10B-4bit | 20M |

Total: ~52 MiB — one 1.5B and one 122B rep satisfy the P2-027 model-coverage
requirement; the second 1.5B rep (r2) adds repetition-level consistency for
+16 MiB. Per spec open question 4, dropping r2 for a minimal 2-bundle
(~36 MiB) pack is acceptable at the lead's discretion.

For reference, the full corpus (all six strict-valid bundles):
r1/r2/r3 of `example-mac-mlx-local` at 16M each and r1/r2/r3 of
`example-mac-mlx-qwen35-122b-512t` at 20M each.

## Next steps (not done here)

Pack with PR #25 tooling, copy `env/analysis-lock.txt` into the pack
directory, tar, and publish as a GitHub Release asset (`repro-pack-v1`)
with the top-level sha256 in the release body — see spec REPRO-2
decisions 2-4 and the dirty-tree fence (open question 3).
