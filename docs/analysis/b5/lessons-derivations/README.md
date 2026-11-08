# Derivations for LESSONS-FOR-V4-V5.md

Stdlib scripts. The counts and durations they use are copied from the Block 5 sources named in LESSONS §0. Only
`timeline.py` writes a file, and it needs none of the custody data, because the stage timestamps are literals.

| Script | What it computes | Section |
|---|---|---|
| `times.py` | stage schedule and interpolated member times | §1.1 |
| `hazard.py` | per-second contention hazard fits (MLE, profile CI), predicted against observed, references | §1.2, §2.1-2.2 |
| `v4proj.py` | v4 episode flag probability and P(>= 39 eligible per pair) under member and window loss | §2.3-2.4 |
| `timeline.py` | writes `docs/ops/guard-replay-corpus/b5/b5-loss-timeline.json` (run from this directory) | §1.1 |
