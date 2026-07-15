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

All wire rules live in `docs/contracts/bridge_protocol.md`
(`bridge-protocol/v1.1`) — the ONE home. This section is the operating
sequence, not the contract.

1. Read root `AGENTS.md`; run Mission M0 for substantial work.
2. Choose the transport using contract §4. Use the audited CLI path when the
   contract requires durable evidence.
3. Build the applicable contract §1 header. For writes, open the session with
   `scripts/bridge session-open` and use its returned header fragment.
4. Call project MCP `codex` with the Git-root `cwd`, model `gpt-5.6-sol`,
   config
   `{"model_reasoning_effort":"<selected-effort>","mcp_servers":{"claude":{"enabled":false}}}`,
   `on-request` approvals, and the narrowest sandbox. Put the contract's origin
   and hop headers in developer instructions.
5. Validate the return under contract §2. Handle early returns and routing
   changes under §§3-4 on the thread required by §5.
6. After writes, run `scripts/bridge session-close` as specified by contract
   §6. Keep primitives for recovery or adjudicated overrides.
7. Inspect every diff, replay the required lead checks, and adjudicate the
   worker's result. The lead owns final verification.

These enforcement boundaries remain explicit:

- `WRITE_SCOPE` is exhaustive; never infer additional scope from tests, generated files, repository instructions, or work believed necessary for completion.
- Never start or continue a `[QUIET-MAC]` measurement while an agent session is active.
- Never use `danger-full-access` or sandbox/approval bypass flags.
- Bridge depth is one hop: a Claude-originated Sol session must not call Claude by MCP, `claude -p`, or any other launcher.
- A missing, duplicated, malformed, or non-final required envelope is protocol failure, never success.

Reverse-consult operation is documented by contract §8 and
`.agents/skills/claude-consult/SKILL.md`.

The project `.mcp.json` pins `gpt-5.6-sol` with `high` only as a safe fallback
and disables the reverse Claude server for every Claude-originated session;
explicit per-task selection remains mandatory.

## Audited path

For D-050/D-064 runs, prefer `~/.local/bin/codex-run-v3` with model, selected
effort, genre, and exhaustive write scope. If unavailable, set
`CODEX_REASONING_EFFORT` to the selected tier and use `scripts/codex-bridge`.
