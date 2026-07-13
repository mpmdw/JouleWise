---
name: codex
description: Start or continue a full OpenAI Codex gpt-5.6-sol session with task-matched effort while preserving JouleWise process gates.
---

You are Claude Code's repo-local Sol bridge.

Use the project MCP server's `codex` tool as the primary path. It starts a full
Codex session; `codex-reply` continues the returned thread. Use Sol when the
user requests it, a second model is valuable, or JouleWise orchestration assigns
implementation/review work.

Before delegation:

1. Resolve the Git root and read root `AGENTS.md`. For substantial work, run
   Mission M0 and read `docs/orchestration.md`; an active stop card overrides
   the ordinary queue.
2. Never send Sol a `[QUIET-MAC]` measurement task.
3. Form a self-contained prompt per `docs/contracts/bridge_protocol.md`
   (`bridge-protocol/v1.1`): use `scripts/bridge session-open` for writes and
   embed its header fragment; use the reduced header for qualifying read-only
   discussion. MCP turns end in the tolerant single-final-line
   `BRIDGE_REPORT_V1` envelope; an audited CLI run with a valid
   `claude-codex-report/v1` body is trailer-exempt. Missing required output is
   a protocol failure.
4. Select effort per `.claude/skills/codex/SKILL.md` §Effort selection: high
   default; xhigh for design-bearing/judgment-dense; ultra only for
   subagent-spawning.
5. Start `codex` with `cwd` set to the Git root, `approval-policy: on-request`,
   model `gpt-5.6-sol`, config
   `{"model_reasoning_effort":"<selected-effort>","mcp_servers.claude.enabled":false}`,
   and the narrowest
   sandbox: `read-only` for analysis/review or `workspace-write` only for
   requested edits. Never use `danger-full-access`.
6. Include developer instructions with `BRIDGE_ORIGIN: claude` and
   `BRIDGE_HOPS_REMAINING: 0`. Tell Sol not to call the project Claude MCP,
   `claude -p`, or another Claude launcher; the Claude lead owns any discussion
   round. Require findings, changed files, tests, blockers, and handoff notes.
7. Preserve the thread id and use `codex-reply` for follow-ups. After writes,
   run `scripts/bridge session-close`; it retains leases on early returns and
   non-OK scope verdicts. Inspect every diff and replay the required lead
   checks before accepting the result.

For a substantial D-050/D-064 call, prefer
`~/.local/bin/codex-run-v3 -m gpt-5.6-sol --effort <selected-effort>` with a
genre and exhaustive `WRITE_SCOPE` for writes. If unavailable, use the tracked
fallback with the same selected effort:

```bash
CODEX_REASONING_EFFORT=high scripts/codex-bridge new <<'PROMPT'
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
You are being called by Claude Code as a Codex subagent. Do not invoke Claude.
Follow AGENTS.md and the named authority files.
Task: ...
Return: concise findings, changed files, verification, blockers.
PROMPT
```

The fallback supports `resume --last`, `resume SESSION_ID`, and `review`.
Never use dangerous bypass flags on either path.
