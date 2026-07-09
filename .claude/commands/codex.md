---
description: Delegate a task to a full Codex session through the project MCP server
argument-hint: <task, review request, or follow-up>
---

Delegate `$ARGUMENTS` to the repo-local Codex MCP server and return an
adjudicated summary.

Follow `.claude/agents/codex.md`: read root `AGENTS.md`, honor stop cards and
machine-state lanes, set the MCP call's `cwd` to the Git root, use `on-request`
approvals, and choose `read-only` unless the request explicitly requires edits.
Use `workspace-write` for requested edits; never use `danger-full-access`.

Tell Codex it is a Claude Code subagent and ask for findings, changed files,
verification, blockers, and handoff notes. Permit any applicable capabilities
available inside its installed runtime. Preserve the returned thread id and use
`codex-reply` when `$ARGUMENTS` is a continuation of a Codex thread already in
this Claude conversation.

If the task is substantial enough to require D-050's invocation manifest, use
`scripts/codex-bridge` instead and consume `.codex-bridge/last-message.md`.
Always inspect the diff and run the required lead-side verification before
reporting success.
