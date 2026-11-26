# ALIGN v4 S fit draft · 2026-11-26

RL-221 §4.7 authorizes this synthetic-only draft on
`align/2026-11-26-s-fourterm-draft`, based on the W1 signing line at
`ece96f9c5`.

- `series_release_prints(..., s_four_term=True)` selects the decode-only
  design with `P·D′` appended. The scorer uses the existing leave-one-member-out
  fits and rejects deficient training designs. The default report matched
  the W1 baseline byte for byte on two synthetic rosters.
- `joulewise/align/apple/rl176.py` is the sole changed registration-bound
  file. The S statistic, superiority level and report words use the existing
  logic.
- The planted-truth tests compare production with the independent exact
  normal-equation twin and exercise an instructed holdout whose training
  rows all have the same turn-0 prompt size. The focused S suites passed.

Command results and the required stored-record projection are in
`/Volumes/JW-EXT/scratch/sol-s-fourterm-1126/REPORT.md`. The research lead
owns the RL-223 choice and any authorization for the stored-record count.
