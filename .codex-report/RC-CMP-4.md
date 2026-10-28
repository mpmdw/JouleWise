# RC-CMP-4 seat report

bridge-report/v1 · branch `report/2026-10-28-rc-cmp-4` cut from `lane/2026-10-27-recompute-comparator` at
`e5ccf720b`. Synthetic data only; no real block-5/6 or BYTES data was opened.

## STATUS: IN PROGRESS

- 2026-10-28 15:21 UTC: L9 full-size synthetic dry run started (read-only worktree of `lane/2026-10-27-l9-2` at
  `2b3047d5b`, L9's own fixture `chain_fixture` with `JW_B5_S10_REAL_PROGRAMS=1`, L9's `JoinedHarness(...).execute()`,
  scratch driver outside any tracked path). Window restored at 15:22 UTC.
- 15:23 UTC: independent recompute at `e5ccf720b` on the restored bytes (20,317 input files): exit 0 in 24 s.
  Comparator waits for L9's step 11.
- 19:59 UTC: L9 reached step 9 (steps 0-6 and 8 logged; driver alive, about 4 h 40 min in). The recompute's input
  file set was hashed before L9 started (`inputs-before.sha256`, 20,317 files) and will be rehashed after it ends.
- 21:43 UTC: a container restart (worker restart, uptime reset) killed the first dry run during step 10 alpha, after
  6 h 20 min. L9's driver refuses an existing run directory (`custody_preflight`, `custody_run_directory_exists`), so
  it cannot resume. The killed custody is kept as `run-killed1` in scratch. Relaunched from a fresh restore at
  21:44 UTC. The restored input file set (20,317 files) is byte-identical to the first restore, and the recompute
  output on it is byte-identical to the first one (sha256 `affa6f5c…bb06d6c4`).
