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

Select effort only as specified by `.claude/skills/codex/SKILL.md` §Effort
selection.

The Claude-facing MCP server disables the reverse Claude server for its child
Codex sessions; top-level Codex sessions still load the reverse server.

On the first launch from a clone, run Claude Code and approve the project
server when prompted; Claude intentionally requires per-project approval for
tracked `.mcp.json` servers. Then verify the bridge:

```bash
scripts/check-codex-mcp.mjs
```

The ONE home for bridge wire policy is `docs/contracts/bridge_protocol.md`
(`bridge-protocol/v1.1`). The launch sequence lives in
`.claude/skills/codex/SKILL.md`.

For every new call:

- Set `cwd` to this repository root explicitly.
- Use `read-only` for analysis/review and `workspace-write` only when edits are
  requested. Use `on-request` approvals.
- Tell Codex to follow root `AGENTS.md`. For substantial JouleWise work, the
  prompt must name the requested output and the relevant Mission M0 context.
- Keep the returned thread id and use `codex-reply` for follow-ups instead of
  silently starting over.
- Inspect Codex's diff and run the appropriate lead verification before
  reporting success.

The enforcement boundaries remain local because prompt text is part of their
enforcement:

- `WRITE_SCOPE` is exhaustive; never infer additional scope from tests, generated files, repository instructions, or work believed necessary for completion.
- Never start or continue a `[QUIET-MAC]` measurement while an agent session is active.
- Never use `danger-full-access` or sandbox/approval bypass flags.
- Bridge depth is one hop: a Claude-originated Sol session must not call Claude by MCP, `claude -p`, or any other launcher.
- A missing, duplicated, malformed, or non-final required envelope is protocol failure, never success.

The tracked Claude subagent `.claude/agents/codex.md`, `/codex` command in
`.claude/commands/codex.md`, and project skill `.claude/skills/codex/SKILL.md`
encode this route for a clean clone and use the same model/effort defaults.

## Reverse Path: Claude MCP for Codex

The tracked `.codex/config.toml` starts `scripts/claude-bridge-mcp.mjs` for Codex
and exposes only `consult_fable`. That tool is preapproved so non-interactive
Codex runs can use the bridge; every other Claude operation remains unavailable.
Direct Codex sessions use it for a bounded, read-only Fable judgment consult
through `.agents/skills/claude-consult/SKILL.md`; the reverse wire rules are in
contract §8. The current top-level model remains the lead and verifies any
peer advice.

## Audited CLI Path

Use `scripts/codex-bridge` when a substantial delegated run needs D-050's
prompt/response/log hashes and invocation manifest, or when a CLI-native review
is preferable. It supports `new`, `resume --last` or a session id, and
`review`, runs at the repository root, mirrors the final response to
`.codex-bridge/last-message.md`, and writes the durable local audit trail under
`.codex-bridge/`.

The current orchestration wrapper is `~/.local/bin/codex-run-v3` (personal
tooling, not tracked here). It supplies the audited report and D-064 evidence
path described by the contract. Current model: gpt-5.6-sol.
`scripts/codex-run` remains the older
hardened, timeout-bounded single-call protocol.

For ordinary implementation work, run `docs/agent_playbook.md` Mission M0
before choosing work from `TASK_QUEUE.md`; delegation and review work must also
follow `docs/orchestration.md`.
