# Claude Code Notes

This repository has a project-local bridge to a full Codex session, plus an
audited CLI fallback.

## Primary Path: Codex MCP

The tracked `.mcp.json` starts `codex mcp-server`. Claude Code exposes its two
entry points as the `codex` tool (start a session) and `codex-reply` (continue
the returned thread). The first tool accepts the working directory, sandbox,
approval policy, model, developer instructions, and arbitrary Codex config
overrides. The small MCP surface is a session launcher: the resulting Codex
session can use the skills, plugins, MCP tools, browser/image tools, goals, and
other capabilities available in that installed Codex runtime.

On the first launch from a clone, run Claude Code and approve the project
server when prompted; Claude intentionally requires per-project approval for
tracked `.mcp.json` servers. Then verify the bridge:

```bash
scripts/check-codex-mcp.mjs
```

For every new call:

- Set `cwd` to this repository root explicitly.
- Use `read-only` for analysis/review and `workspace-write` only when edits are
  requested. Use `on-request` approvals; never use `danger-full-access` or a
  dangerous bypass flag.
- Tell Codex to follow root `AGENTS.md`. For substantial JouleWise work, the
  prompt must name the requested output and the relevant Mission M0 context.
- Keep the returned thread id and use `codex-reply` for follow-ups instead of
  silently starting over.
- Inspect Codex's diff and run the appropriate lead verification before
  reporting success. Never delegate a `[QUIET-MAC]` measurement run: the agent
  load would contaminate it.

The tracked Claude subagent `.claude/agents/codex.md` and `/codex` command in
`.claude/commands/codex.md` encode this route for a clean clone.

## Audited CLI Path

Use `scripts/codex-bridge` when a substantial delegated run needs D-050's
prompt/response/log hashes and invocation manifest, or when a CLI-native review
is preferable. It supports `new`, `resume --last` or a session id, and
`review`, runs at the repository root, mirrors the final response to
`.codex-bridge/last-message.md`, and writes the durable local audit trail under
`.codex-bridge/`.

Use `scripts/codex-run` for the older hardened, timeout-bounded single-call
protocol used by orchestration harnesses. Do not use Codex's dangerous bypass
flags through either path.

For ordinary implementation work, run `docs/agent_playbook.md` Mission M0
before choosing work from `TASK_QUEUE.md`; delegation and review work must also
follow `docs/orchestration.md`.
