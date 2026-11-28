Committed 7 local commits on the assigned branch, ending at `e9b36735e`. Clean worktree; no push.

- Built both guard layers, runner initialization, and the 368-site allowlist.
- Recorded and fixed one real `caffeinate` leak before execution.
- Guard: 11 tests passed; inventory: 2 passed; focused repair and executed closure passed.
- Several legacy checks, dynamic closure, and registration hit caps. Failures and unrun modules are documented. No bound production files changed.

[Full report](/Volumes/JW-EXT/jw-wt/sol-w1-host-guard/docs/run_reports/2026-11-11-w1-host-guard.md) includes commits, verification, residual risks, and an intake overread involving adjacent B5 discussion.

**NEEDS_RULING:** Accept the guard-specific grep check while preserving existing production `PYTHONPATH` references? Recommended; the literal zero-reference requirement remains blocked by the brief’s prohibition on production edits.