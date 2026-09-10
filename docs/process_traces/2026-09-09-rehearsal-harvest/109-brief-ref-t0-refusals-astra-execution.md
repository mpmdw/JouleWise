SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Refuter — PR #312 (three T0 clock refusal tests), EXECUTION lens (gpt-6-astra, medium, genre review, read-only)

Worktree: this one, detached at 6e0bbf67 (PR head = tests commit + merge of main). Diff under review: `git diff afaeffef..6e0bbf67 -- tests/test_arm_readiness_evidence_t0.py` (37 added lines, three methods). Authority: root-cause consult 99 §Regression proposals (/Users/edr/code/JouleWise-wt-magistrate-1ef89702/docs/process_traces/2026-09-09-rehearsal-harvest/99-rootcause-arm-load-ci-astra-report.md) and seat report 108 (same directory).
Refute, by reading and (if this sandbox permits — it may lack a writable temp dir; say so and fall back to static reasoning; never fabricate tails) by execution:
1. For each test, name the production guard it pins (path:line in joulewise/arm_readiness_evidence_t0.py: the `_capture` field validation; the RAW anchor span check; the live-artifact check) and show the exact detail string is what production raises — a test that pins a string production never emits would be vacuous.
2. Mutation: for one test, reason what happens if the production guard were removed (the helper `_assert_clock_refusal` must FAIL, not pass silently); quote the helper (~line 1165) to show it asserts the refusal rather than swallowing it.
3. Portability: none of the three reads the host clock (they use SYNTHETIC_MONOTONIC_NS / literal 5e11); confirm by grep; state whether they hold on a small-uptime Linux runner and on this Mac.
4. Production untouched (`git diff --stat afaeffef..6e0bbf67 -- joulewise scripts` empty). Same-signature statement.
Report claude-codex-report/v1, genre review, header < 8192 bytes (verdict = {counts, findings} only); body = disposition per item with quotes/tails.
