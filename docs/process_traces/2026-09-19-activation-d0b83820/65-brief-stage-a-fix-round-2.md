SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/arm_retry.py", "docs/process/NIGHT_HANDBACK.md", "tests/test_arm_retry.py", "tests/test_gen_evidence_night.py"]

# STAGE-A-EVIDENCE-EXECUTOR-01 fix round 2 — the two full-replay findings of record 60 (row 9)

Cwd is a DETACHED worktree at the fix-round-1 head `__HEAD__` (`git log -1`). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; scratch under `/tmp`; no `sudo`, no `powermetrics`. Interpreter `/Users/edr/code/JouleWise/.venv/bin/python` (read-only use). Do not commit.

Read as a file: `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/60-full-replay-stagea.md`.

1. `tests.test_arm_retry.test_both_document_blocks_are_exact` fails because `docs/process/NIGHT_HANDBACK.md`'s GENERATED policy block (rendered by `joulewise/arm_retry.render_policy()`) was hand-edited to add/alter the `night_refused_registration` refusal row. Fix: put the ruled row text ("The plan's registration is not a ruled registration digest, or the registration's bound chain-source digest differs from the plan's chain." — keep whatever wording fix round 1 settled on, but SOURCE it from `arm_retry`'s refusal table), re-render the block into the handback exactly as the renderer emits it, revert the hand edit, and pin the row through the renderer in `tests/test_arm_retry.py`. Verify `test_both_document_blocks_are_exact` passes and that the handback's non-generated amendments from rounds 1–2 (the :134 clause, the :563–575 sentence) are untouched.
2. `tests.test_git_fixture_maintenance.test_every_test_module_routes_git_initialization_through_shared_helper` fails because `tests/test_gen_evidence_night.py:41` initializes git directly. Fix: use `tests/git_fixture.init_git_fixture` like every other module; verify the maintenance test passes and `test_gen_evidence_night` still passes.

Bench: `tests.test_arm_retry`, `tests.test_git_fixture_maintenance`, `tests.test_gen_evidence_night`, `tests.test_night_gate`; `git diff --stat` within scope. Report: `claude-codex-report/v1` envelope for `--genre implementation`; JSON header under 8000 bytes.
