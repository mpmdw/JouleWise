---
description: Delegate a task to gpt-5.6-sol through the project MCP server
argument-hint: <task, review request, or follow-up>
---

Delegate `$ARGUMENTS` through `.claude/agents/codex.md` and return an
adjudicated summary.

Select effort per `.claude/skills/codex/SKILL.md` §Effort selection: high
default; xhigh for design-bearing/judgment-dense; ultra only for
subagent-spawning.

Follow `docs/contracts/bridge_protocol.md` (`bridge-protocol/v1.1`) for the
full or discussion-lane prompt header, tolerant final-line return envelope,
early returns, and lease/scope rules. Use `scripts/bridge session-open` and
`session-close` for writes; primitives remain recovery tools.
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
