SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["scripts/sample_quiet_predicate_evidence.py", "tests/test_sample_quiet_predicate_evidence.py"]

# Fix round 5 — lane QUIET-PREDICATE-EVIDENCE-01 harness: delta re-audit round 4 findings R1 (Markdown group identity) and R2 (test-time grace)

Cwd is the linked worktree of branch `feat/2026-09-18-quiet-predicate-evidence-harness` at the round-4 head (`git log -1`). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; scratch under `/tmp` only; no `sudo`, no `powermetrics`, no live `collect` with power. Nothing is armed. Interpreter `/Users/edr/code/JouleWise/.venv/bin/python` (read-only use). Do not commit. Do not end your turn before the report is complete.

Read as files: `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/20a-triage-delta-reaudit-round-4.md` (the ruled fix shape) and `20-delta-reaudit-round-4-astra.md` (R1/R2 with file:line and the edge-probe log under `/tmp/jw-reaudit4-232/`).

## Do

1. R1: in `summarize()`'s Markdown renderer (~lines 1065–1077), add a `boot_id` column to all three tables, and an `os_build` column when any row carries that field (mirror `comparison_fields`); regression: two idle rows, same repeat/census, boot A at 1 W and boot B at 9 W → the rendered Markdown contains two rows distinguishable by their boot ids (assert on the rendered text, not only on JSON).
2. R2: add keyword `join_grace_s: float = 5.0` to `load()` (production default unchanged; do NOT add a CLI flag); the first `process.join(timeout=…)` uses it. In the escalation regression (stuck child, `exit_delay=60`) pass `join_grace_s=0.2`; keep the one-second clean-exit regression on the production default so it still proves the 5 s grace accepts a slow correct exit. Expect the module wall time to drop back toward ≈ 9 s (the S6 subprocess and the real-load test remain).

Nothing else changes. Every other test and the real-load test's assertion set stay byte-identical (the re-audit will diff the AST).

## Bench acceptance (execute; paste tails)

- Module twice under unittest: 44 tests OK (45 if you add the R1 regression as a new test — say which), wall times.
- Mutations on `/tmp` copies (worktree byte-identical, `git status` before/after): `pool-across-boots` (must now also fail the Markdown regression), `cleanup-silent` (must still fail with the short grace), plus `cores`, `clock`, `burn-noop`, `window-skip` as a smoke set. Paste failing test names.
- `git diff --stat`: only the two scoped files.

## Report

`claude-codex-report/v1` envelope for `--genre implementation`; JSON header under 8000 bytes; commands with outcomes.
