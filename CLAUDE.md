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

The project server defaults to `gpt-5.6-sol` with `high` reasoning effort as a
safe fallback. Claude selects and passes effort explicitly per task: `high` by
default for bounded/mechanical work; `xhigh` for design-bearing,
cross-contract, multi-component, non-local root-cause, adversarial, or
integration work; `ultra` only when Sol itself must spawn subagents. A single
fixed `xhigh` default is not allowed.

The Claude-facing MCP server also sets `mcp_servers.claude.enabled=false` for
its child Codex sessions. This enforces the one-hop rule at tool discovery, not
only in prompt text; top-level Codex sessions still load the reverse server.

On the first launch from a clone, run Claude Code and approve the project
server when prompted; Claude intentionally requires per-project approval for
tracked `.mcp.json` servers. Then verify the bridge:

```bash
scripts/check-codex-mcp.mjs
```

The wire contract for all bridge traffic — `BRIDGE_TASK_V1` prompt header,
`BRIDGE_REPORT_V1` return envelope, `NEEDS_SCOPE`/`NEEDS_RULING` early
returns, MCP-vs-CLI routing, thread reuse, workspace leases, and mechanical
scope checking via `scripts/bridge` — is `docs/contracts/bridge_protocol.md`
(`bridge-protocol/v1`). The operating sequence lives in
`.claude/skills/codex/SKILL.md`; neither this file nor the skills restate the
contract's normative rules.

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

The tracked Claude subagent `.claude/agents/codex.md`, `/codex` command in
`.claude/commands/codex.md`, and project skill `.claude/skills/codex/SKILL.md`
encode this route for a clean clone and use the same model/effort defaults.

## Reverse Path: Claude MCP for Codex

The tracked `.codex/config.toml` starts `scripts/claude-bridge-mcp.mjs` for Codex
and exposes only `consult_fable`. That tool is preapproved so non-interactive
Codex runs can use the bridge; every other Claude operation remains unavailable.
Direct Codex sessions use it for a bounded, read-only Fable judgment consult
through `.agents/skills/claude-consult/SKILL.md`. The adapter launches the
installed Claude Code runtime with model `fable`, effort `high`, plan mode, no
session persistence, no slash commands, an empty MCP registry, and only the
read-only `Read`, `Grep`, and `Glob` tools.

Bridge depth is one hop. A Sol session started by Claude carries
`BRIDGE_ORIGIN: claude` / `BRIDGE_HOPS_REMAINING: 0` and must not call back into
Claude. Likewise, a Fable consult started by Codex must not invoke Sol. The
current top-level model remains the lead and verifies any peer advice.

## Audited CLI Path

Use `scripts/codex-bridge` when a substantial delegated run needs D-050's
prompt/response/log hashes and invocation manifest, or when a CLI-native review
is preferable. It supports `new`, `resume --last` or a session id, and
`review`, runs at the repository root, mirrors the final response to
`.codex-bridge/last-message.md`, and writes the durable local audit trail under
`.codex-bridge/`.

The current orchestration wrapper is `~/.local/bin/codex-run-v3` (personal
tooling, not tracked here): claude-codex-report/v1 envelope injection via
--genre, mechanical WRITE_SCOPE enforcement (exit 77 + evidence bundle),
NEEDS_SCOPE/NEEDS_RULING early-return protocols, D-064 manifest v3 event
stream, and a codex-usage quota guard. Current model: gpt-5.6-sol. Effort is
selected per the project policy above: high fallback/default, xhigh for named
hard-task triggers, ultra only for subagent-spawning sessions.
`scripts/codex-run` remains the older
hardened, timeout-bounded single-call protocol. Do not use Codex's dangerous bypass
flags through either path.

For ordinary implementation work, run `docs/agent_playbook.md` Mission M0
before choosing work from `TASK_QUEUE.md`; delegation and review work must also
follow `docs/orchestration.md`.
