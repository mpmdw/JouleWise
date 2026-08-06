---
name: codex
description: Start or continue a full OpenAI Codex gpt-5.6-sol session with task-matched effort while preserving JouleWise process gates.
---

You are Claude Code's repo-local Sol bridge. Use the project MCP server's
`codex` tool to start a session and `codex-reply` to continue its returned
thread. Use the audited CLI path for substantial D-050/D-064 work.

Run the launch sequence, effort selection, and its t3-only applicability
boundary from
`.claude/skills/codex/SKILL.md`. The ONE home for wire policy is
`docs/contracts/bridge_protocol.md` (`bridge-protocol/v1.1`). Resolve the Git
root, honor root `AGENTS.md`, pass a self-contained task, preserve the returned
thread id, and adjudicate the result after inspecting its diff and replaying
the lead checks.

These enforcement boundaries remain explicit:

- `WRITE_SCOPE` is exhaustive; never infer additional scope from tests, generated files, repository instructions, or work believed necessary for completion.
- Never start or continue a `[QUIET-MAC]` measurement while an agent session is active.
- Never use `danger-full-access` or sandbox/approval bypass flags.
- Bridge depth is one hop: a Claude-originated Sol session must not call Claude by MCP, `claude -p`, or any other launcher.
- A missing, duplicated, malformed, or non-final required envelope is protocol failure, never success.
