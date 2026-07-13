---
name: codex
description: Run OpenAI Codex gpt-5.6-sol inside Claude Code with difficulty-matched effort and JouleWise bridge safety.
---

# Sol bridge for Claude Code

Use when the user requests Codex/Sol, a second model is useful, or JouleWise
orchestration assigns work to Sol.

## Effort selection

Choose before launch and always pass the choice explicitly:

- `high` — default: bounded/mechanical tasks, docs/config, a straightforward
  implementation, a named FIX contract, or an ordinary focused review.
- `xhigh` — hard individual tasks: design-bearing decisions, cross-contract or
  multi-component work, non-local root-cause analysis, adversarial/integration
  review, or ambiguity where the cost of a wrong judgment is material.
- `ultra` — only when the Sol session itself must spawn subagents. Never use it
  as a quality upgrade for a single-agent task.

When uncertain between `high` and `xhigh`, start `high`; escalate a fresh or
continued session only when the task actually exhibits an xhigh trigger.

## Primary MCP path

1. Read root `AGENTS.md`; run Mission M0 for substantial work. Never launch
   agent load during `[QUIET-MAC]` measurement.
2. Call project MCP `codex` with the Git-root `cwd`, model `gpt-5.6-sol`, config
   `{"model_reasoning_effort":"<selected-effort>","mcp_servers.claude.enabled":false}`,
   `on-request` approvals, and the narrowest sandbox.
3. Put `BRIDGE_ORIGIN: claude` and `BRIDGE_HOPS_REMAINING: 0` in developer
   instructions. Sol must not call the project Claude MCP, `claude -p`, or any
   other Claude launcher; Claude owns cross-model discussion.
4. Keep the thread id; use `codex-reply` for the same role. Inspect diffs and
   replay lead verification before accepting work.

The project `.mcp.json` pins `gpt-5.6-sol` with `high` only as a safe fallback
and disables the reverse Claude server for every Claude-originated session;
explicit per-task selection remains mandatory.

## Audited path

For D-050/D-064 runs, prefer `~/.local/bin/codex-run-v3` with model, selected
effort, genre, and exhaustive write scope. If unavailable, set
`CODEX_REASONING_EFFORT` to the selected tier and use `scripts/codex-bridge`.

Never use bypass flags, `danger-full-access`, or a second bridge hop.
