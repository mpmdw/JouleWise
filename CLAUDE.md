# Claude Code Notes

This repository has a local Codex bridge for second-agent work.

- Use the project subagent named `codex` when the user asks Claude Code to delegate to Codex.
- Direct shell entry point: `scripts/codex-bridge new`, `scripts/codex-bridge resume --last`, or `scripts/codex-bridge review`.
- Codex runs from this repository root and mirrors its final response to `.codex-bridge/last-message.md`.
- A project MCP server named `codex` is declared in `.mcp.json`; approve it in Claude Code if prompted.
- For ordinary JouleWise implementation sessions, follow `docs/agent_playbook.md` Mission M0 before choosing work from `TASK_QUEUE.md`.
