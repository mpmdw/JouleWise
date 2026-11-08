**ADMIT_WITH_FIXES — draft desk kit only.** Committed locally on `align/2026-11-07-adversary-kit-review`; tree clean, nothing pushed.

Fixed three bugs with failing-first regressions: incomplete cache evaluation, `SystemExit` bypassing sampler cleanup, and symlink manifest reads. Changes cover two code files, four test modules, and three documents.

Verification:

- `tests.align.test_squeeze_config` — 9 passed.
- `tests.align.test_squeeze_control` — 10 passed.
- `scripts/check_squeeze_overlay.py` — 8 passed against the pinned runner.
- Config validation, targeted compilation and diff checks passed.
- Native MLX module — 2 skipped.

Open gates: public identities reveal dose assignments; joint false-alarm calibration, detection power and adaptive robustness remain unestablished. Next, the lead should review the patch and run `python3.13 -B -m unittest tests.align.test_squeeze_native` with MLX/Metal.

[Full review and test tails](/Users/edr/code/CapstoneProject/jw-wt/sol-kit-review/docs/align/squeeze/sol/kit-review.md) · [Run report and file inventory](/Users/edr/code/CapstoneProject/jw-wt/sol-kit-review/docs/run_reports/2026-11-07-adversary-kit-review.md)

Commits: `343671290` (fixes), `1baa9c2a3` (review). No network, sealed-data access, measurements, full suite, or coordination-state edits.