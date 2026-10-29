STATUS: BLOCKED in progress (milestones 1-2 of 3 pushed: G7, F2)

# RC-CMP-7 seat report

bridge-report/v1 · scheduled seat RC-CMP-7 (lead: joulewise-28, block-5 lead) · branch
`lane/2026-10-27-recompute-comparator`, base `1134bbf58`. Synthetic data only: no real block-5/6 or BYTES data was
opened or searched for. Interpreter `/usr/bin/python3.13`; `TMPDIR=/tmp/claude-0/rcseven` (outside the checkout).

## SUMMARY

Milestones 1 (G7) and 2 (F2) are done; F3 follows. This draft is replaced by the final report.

- **G7.** `run_phase_energy_j` takes its key universe from L9's step-2 selection (the kept units of L9's kept-units
  record) and applies it to both sides. A member that the window's sealed plan tree registers as a NEG-8 reference is
  excluded and listed as `compared_in:<family>`.
  - RC-CMP-4's window at `1134bbf58` gives exit 1 with 162 failing run rows, the same count RC-CMP-4 reported. At the
    new head it gives exit 0.
  - Opus G7.1 now passes. Opus G7.2 now DISAGREEs.
- **F2.** Two changes:
  - A line gate admits only the line words the producer writes in each section, with that word's keys.
  - The two broad subtrees are now enumerated leaf names. Every claim word the recompute re-derives is compared
    exactly.

  Opus's relabel sweep now has 0 exits (58 at `1134bbf58`).
