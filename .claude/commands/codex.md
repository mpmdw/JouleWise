---
description: Delegate a task to gpt-5.6-sol through the project MCP server
argument-hint: <task, review request, or follow-up>
---

Delegate `$ARGUMENTS` through `.claude/agents/codex.md` and return an
adjudicated summary.

Classify the task before calling Sol. Use `high` by default for bounded,
mechanical, docs/config, straightforward implementation, FIX, and ordinary
review work. Use `xhigh` for design-bearing, cross-contract, multi-component,
non-local root-cause, adversarial, integration, or otherwise judgment-dense
individual work. Use `ultra` only if the Sol session must itself spawn
subagents and that topology was deliberately authorized.

Follow `docs/contracts/bridge_protocol.md` for the prompt header, return
envelope, early returns, and lease/scope steps (`scripts/bridge`).
Pass model `gpt-5.6-sol` and config
`{"model_reasoning_effort":"<selected-effort>","mcp_servers.claude.enabled":false}`
explicitly. Set the Git-root
`cwd`, use `on-request` approvals, and choose `read-only` unless edits are
requested. Add `BRIDGE_ORIGIN: claude` and `BRIDGE_HOPS_REMAINING: 0` to the
developer instructions so Sol cannot bounce back into Claude.

Preserve the returned thread id and use `codex-reply` for continuations. For
substantial D-050/D-064 work, use `codex-run-v3` with the selected explicit
effort, genre, and exhaustive `WRITE_SCOPE`; fall back to
`scripts/codex-bridge`. Always inspect the diff and replay the lead checks.
