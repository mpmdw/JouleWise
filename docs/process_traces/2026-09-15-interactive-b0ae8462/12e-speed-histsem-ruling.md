# 12e — TEST-SPEED-01 HISTSEM ruling (magistrate b0ae8462, 2026-09-15 23:45 PDT)

H1 (one `git cat-file --batch` per pack) ADOPTED: byte-identical over every blob of every fixture, CLI 73.5 → 59.7 s,
committed on `perf/2026-09-15-histsem-batch`. H2 (pack-only sparse checkout) DROPPED: a real probe refused a valid
historical generator (`d117_contrast_qwen25_1p5b_vs_7b_v1` imports `joulewise` outside the pack), so the sparse set
would have to include the package tree and the saving collapses. The module's own before-timing did not complete under
load; the branch lands as a small PR after the installer with its module timing recorded in CI. Net: a modest cut; the
shard-weight refresh on the CI branch already removed this module from the critical path.
