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
3. Form a self-contained prompt with the exact task, output, authority/spec
   pointers, exclusions, and verification expectations.
4. Select effort by difficulty and pass it explicitly:
   - `high` is the default for bounded/mechanical work, docs/config edits,
     straightforward implementations, named FIX rounds, and ordinary reviews;
   - `xhigh` is for design-bearing decisions, cross-contract or multi-component
     work, non-local root causes, adversarial/integration reviews, and other
     judgment-dense individual tasks;
   - `ultra` is only for a Sol session that must itself spawn subagents, and
     only when the user or lead deliberately chose that topology.
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
7. Preserve the thread id and use `codex-reply` for follow-ups. Inspect every
   diff and replay the required lead checks before accepting the result.

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
