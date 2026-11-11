Committed locally on `ops/2026-11-11-r1-followup-kit`:

- `8c07cf7f8` — W1-base merge.
- `bc27a808e` — RL-84 fixes.
- `774ba7ded` — [round-4 report and remaining checks](/Volumes/JW-EXT/jw-wt/sol-r1fu-build-r4/docs/run_reports/2026-11-11-r1-followup-kit.md:563).

32 targeted tests passed. One follow-up test failed; its fixture correction awaits rerun. PREQUAL, next-arm, fresh trace and both closures remain incomplete. `thermal.py` is unchanged. Worktree clean; nothing pushed.

I mishandled the trace interrupt. Its synthetic child **PID 68087 remains running**, and the sandbox denied stopping it. Please run `kill -INT 68087` in Terminal—only that PID—before resuming tests.