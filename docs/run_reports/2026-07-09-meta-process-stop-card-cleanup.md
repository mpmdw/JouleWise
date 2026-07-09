# 2026-07-09 Meta-Process Stop-Card And Bridge Audit Cleanup

## Summary

User-directed process cleanup after a review of council usage,
skill/tool invocation logging, run-state bookkeeping, and CP-5 handoff
risk.

No CP-5 implementation work was resumed, gated, merged, cleaned, or
adjudicated. The goal was to make the paused work easy to resume once
token limits reset, harder to bypass accidentally, and to make future
Codex bridge invocations auditable by prompt/output/log hash.

## Changes Landed

- Added an ACTIVE CP-5 stop card to `RUN_STATE.md`, including paused
  work inventory, artifact pointers, status terms, and clearance
  criteria.
- Demoted normal restart and next-work pointers while the stop card is
  active.
- Updated `TASK_QUEUE.md` so active stop cards outrank normal queue
  ranking, and added the ready/shelf rule for half-finished work.
- Updated `docs/run_reports/README.md` with stop-card intake and the
  required process-trace template for substantial delegated runs.
- Updated `docs/orchestration.md` with the stop-card contract,
  checkpoint status vocabulary, invocation-manifest rule, ephemeral
  artifact pointer rule, and council scorecard/disposition requirements.
- Updated `docs/agent_playbook.md` Mission M0 so preflight honors active
  stop cards.
- Added D-050 to `docs/decision_log.md`.
- Updated `scripts/codex-bridge` so each invocation writes:
  - a prompt snapshot under `.codex-bridge/prompts/`,
  - a response snapshot under `.codex-bridge/responses/`,
  - a unique log and status file,
  - and an `.codex-bridge/invocation_manifest.jsonl` row containing
    run id, mode, session id when present, target session id for resume,
    prompt/output/log paths and SHA-256 hashes, status, and pending
    disposition fields.

## CP-5 Preservation

CP-5 remains the active rank-0 task. Resume authority is still
`docs/stream_logs/2026-07-08-precampaign-review.md`, CP-5 section near
the bottom. The off-repo durable checkpoint pointer remains:

```text
~/.claude/projects/-Users-edr-code-JouleWise/ae807c57-7163-4f10-8532-42e8cfacdaff/checkpoint-2026-07-08/
```

Do not remove CP-5 worktrees, merge PR #22, or consume the methodology
synthesis outside the CP-5 resume sequence.

## Verification

Process/tooling change. Python test suite not run.

Commands run:

```text
bash -n scripts/codex-bridge
CODEX_BIN=/bin/echo scripts/codex-bridge new audit smoke prompt
```

The fake-Codex smoke wrote a manifest row with prompt/output/log hashes.

Manual consistency check:

- `RUN_STATE.md` active stop card points to CP-5 first.
- `TASK_QUEUE.md` rank 0 remains `RESUME-CP5`.
- Run-report intake now allows a stop card to outrank the latest report.
- Agent playbook M0 now checks for the stop card before normal mission
  selection.
- `scripts/codex-bridge` preserves the existing `last-message.md`
  behavior while adding durable per-run prompt/response/log artifacts.

## Next

When Ed says to resume or when token budget resets, start with
`RUN_STATE.md` `ACTIVE_STOP_CARD`, then execute `TASK_QUEUE.md` rank 0
from the CP-5 stream-log sequence.
