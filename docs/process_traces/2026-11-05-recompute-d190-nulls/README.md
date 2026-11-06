# Synthetic D-190 acceptance evidence

All inputs are generated fixtures, with fresh storage under the clone's
`.scratch-d190/r2/.scratch-s10f/tmp/`. No real study custody is read.

- `synthetic_run.py`: exact readiness-lane runner, executed from the
  detached `b5/analysis-r2` worktree at `.scratch-d190/r2`. One driver worker,
  existing joined-harness synthetic Git seams, real arithmetic. It runs the
  current clone's independent recompute and comparator after the r2 driver.
- `summarize.py`: value-free counts, exits, source/config/artifact hashes,
  exact child argv and coverage totals. Recompute source hash is checked
  against the program hash in the outputs before writing a summary.
- `baseline-summary.json`: item 1, recompute/comparator at a43d84b27.
- `patched-summary.json`: item 2, a second complete fresh r2 driver run,
  followed by the patched recompute and comparator; exits 0/0/0.
- `null_probe.py` / `n1-summary.json`: item 2's 26-field n=1 probe against
  real engine synthetic null shapes. No full-window coverage is claimed.
- `tests-summary.json`: sequential targeted modules, including the initial
  outdated worked-example failure and its corrected successful rerun.

Launch and verification commands, limitations and interpretation live in
[the run report](../../run_reports/2026-11-05-recompute-d190-nulls.md).
Full synthetic input/custody bundles are retained in ignored scratch;
these tracked summaries intentionally contain no energy operands.
