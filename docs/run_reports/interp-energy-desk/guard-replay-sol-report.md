Committed `24ff5ddc1` on `ops/2026-11-08-guard-replay`. Worktree clean; nothing pushed.

Added the replay harness, committed host-trace corpus, synthetic tests, guard inventory, replay rule, and recorder specification. Production guard behavior is unchanged.

Regression replay flags:

- Pre-#691 QuietGuard: **2/5 benign incidents refused (40%)**.
- Pre-R0-L3 SMC: **3/3 refused (100%)**.

Verification:

- `python3.13 -B -m unittest tests.test_guard_replay`: **34 passed**.
- `python3.13 -B -m unittest tests.hazards.test_contention`: **48 passed, 3 native skips**.
- Targeted compilation, report hashes, reproducibility, and protected-file checks passed.

The corpus is sparse and incident-selected; it does **not** qualify a live guard. The proposed 5% bound needs lead acceptance, followed by representative traces and native checks.

[Full handoff, changed files, commands, and next steps](/Users/edr/code/CapstoneProject/jw-wt/sol-guard-replay/docs/run_reports/2026-11-08-guard-replay.md)