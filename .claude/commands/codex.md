---
description: Delegate a task to gpt-5.6-sol through the project MCP server
argument-hint: <task, review request, or follow-up>
---

Delegate `$ARGUMENTS` through `.claude/agents/codex.md` and return an
adjudicated summary.

Run `.claude/skills/codex/SKILL.md` for effort selection, the launch sequence,
and its t3-only applicability boundary. The ONE home for wire policy is
`docs/contracts/bridge_protocol.md` (`bridge-protocol/v1.1`). Preserve the
returned thread for same-objective continuations; always inspect the diff,
replay the lead checks, and adjudicate before reporting.

These enforcement boundaries remain explicit:

- `WRITE_SCOPE` is exhaustive; never infer additional scope from tests, generated files, repository instructions, or work believed necessary for completion.
- Never start or continue a `[QUIET-MAC]` measurement while an agent session is active.
- Never use `danger-full-access` or sandbox/approval bypass flags.
- Bridge depth is one hop: a Claude-originated Sol session must not call Claude by MCP, `claude -p`, or any other launcher.
- A missing, duplicated, malformed, or non-final required envelope is protocol failure, never success.
