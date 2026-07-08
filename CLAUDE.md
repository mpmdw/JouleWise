# Claude Code Notes

This repository has a local Codex bridge for second-agent work.

- Tracked entry points: `scripts/codex-run` for hardened single calls;
  `scripts/codex-bridge` for the project bridge (`new`, `resume --last`,
  `review`).
- A project MCP server named `codex` is declared in the tracked
  `.mcp.json`; approve it in Claude Code if prompted (the Codex CLI it
  launches must be installed locally). Machine-local conveniences that
  may be absent on a clean clone: the Claude Code subagent named `codex`
  and any Codex-related global skills.
- Codex runs from this repository root and mirrors its final response to `.codex-bridge/last-message.md`.
- For ordinary JouleWise implementation sessions, follow `docs/agent_playbook.md` Mission M0 before choosing work from `TASK_QUEUE.md`.
