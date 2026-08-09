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

A standing Ed effort directive controls over a ruled gate composition's
stated tier, which is a default unless expressly marked mandatory. Every
deviation is recorded at launch, in the gate record, and in synthesis — ruled
tier, applied tier, directive cited, original reasoning preserved — visible to
Ed. If an expressly mandatory tier conflicts with a standing directive, do not
launch or consume the instrument until Ed prospectively rules. A failed or
materially degraded round under a capped tier is supporting datum for
escalation, never a prerequisite for requesting it. The lead may not raise or
lower a ruled tier on its own authority.

## Transport selection

All wire rules live in `docs/contracts/bridge_protocol.md`
(`bridge-protocol/v1.1`) — the ONE home. This section is the operating
sequence, not the contract.

Apply contract §4's t3 applicability and preferred-presentation-plane rule.

1. Read root `AGENTS.md`; run Mission M0 for substantial work.
2. Choose the transport and apply the tracked-subagent limits, pilot record,
   and accounting rule by reference to contract §4.
3. Build the applicable contract §1 header. For writes, open the session with
   `scripts/bridge session-open` and use its returned header fragment.
4. For a substantial background or parallel Sol round that needs
   operator-visible lifecycle state, use the preferred background route: set
   `CODEX_REASONING_EFFORT` to the selected tier and call
   `scripts/codex-bridge new` or `scripts/codex-bridge review`. For MCP, call
   project tool `codex` with the
   Git-root `cwd`, model `gpt-5.6-sol`, config
   `{"model_reasoning_effort":"<selected-effort>","mcp_servers":{"claude":{"enabled":false}}}`,
   `on-request` approvals, and the narrowest sandbox. Put the contract's origin
   and hop headers in developer instructions or the bridge prompt.
   Fast Mode is the standing DEFAULT on both `scripts/codex-bridge` and
   `codex-run-v3`; `CODEX_SERVICE_TIER=default` is the per-call opt-out;
   CODEX ONLY, never Anthropic fast.
5. Validate the return under contract §2. Handle early returns and routing
   changes under §§3-4 on the thread required by §5.
6. After writes, run `scripts/bridge session-close` as specified by contract
   §6. Keep primitives for recovery or adjudicated overrides.
7. Inspect every diff, replay the required lead checks, and adjudicate the
   worker's result. The lead owns final verification.

At the next t3-mediated session after the 2026-08-03 doctrine gate, capture the
owed Full-access mapping amendment exhibit before citing any UI-to-flag mapping
as evidence. Bind one observation to the t3 and CLI versions, selected UI mode,
timestamp, full child argv, and a process-table record containing PID, start
time, and ancestry; store the capture at a tracked process-trace location. The
contract §4 prohibition already binds independently of this exhibit. Apply
contract §4's approval-evidence rules.

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
effort, genre, and exhaustive write scope. If it is unavailable, use
`scripts/codex-bridge` only for a substantial background or parallel Sol round
that needs operator-visible lifecycle state; set `CODEX_REASONING_EFFORT` to
the selected tier. Otherwise return to contract §4 and select the matching
foreground route.

## Session observability + recovery (WO-027)

The native Codex pet does not consume the external observer JSONL. It follows
running local conversations owned by the Codex desktop app. On Ed's configured
machine, `.codex-bridge/app-host-thread-id` selects a dedicated app-owned task;
`scripts/codex-bridge` uses `scripts/codex-app-bridge.mjs` to start the real Sol
turn there. The script serializes calls on that host task, captures the final
answer from its rollout, and interrupts the app turn if the wrapper is
terminated. `CODEX_APP_BRIDGE=off` explicitly selects the standalone CLI
fallback. Do not claim native pet visibility for standalone `codex exec` or
MCP sessions.

The observer JSONL remains a separate audit/diagnostic surface. The script
publishes `RUNNING` and terminal `FINISHED` events, but those records do not
drive pet behavior.

Live visibility and discovery for bridge-launched sessions use the
`.codex-bridge/` audit trail (this replaced the deleted `scripts/codex-watch`;
replacement demonstrated live in the 2026-07-14 audit-resume session, which
monitored two concurrent Sol implementations this way):

- Discover RUNNING sessions: `ls -lt .codex-bridge/*.log` — the log exists
  from launch, but `.status` files and manifest rows are written only at
  exit, so a `.log` with no matching `.status` file is a live (or crashed,
  incomplete) run. Its filename is the run id the follow command needs.
- Discover finished sessions: `ls -lt .codex-bridge/*.status` (one
  `OK`/`FAILED rc=N` file per run id) and
  `.codex-bridge/invocation_manifest.jsonl` rows.
- Follow live: `tail -f .codex-bridge/<run-id>.log` (the full tee'd stream).
- Final message: `.codex-bridge/responses/<run-id>.response.md`, mirrored to
  `.codex-bridge/last-message.md`.

Recovery recipe (preserved from codex-watch) for a session with NO bridge
trail — e.g. a crashed wrapper or a raw `codex exec`: the Codex CLI writes a
rollout JSONL per session under `~/.codex/sessions/YYYY/MM/DD/`.

- Discover: newest-first by mtime, e.g.
  `find ~/.codex/sessions -name '*.jsonl' -mmin -480 | xargs ls -lt`.
- Live processes: `ps -axo pid,etime,command | grep 'codex exec'`.
- Read a rollout: each line is an event typed by `payload.type` (with
  `session_meta` also appearing as top-level `event.type` in current
  rollouts): `session_meta` (has `cwd`), `user_message`, `agent_message`,
  `function_call` (arguments hold the command), `token_count`
  (`info.total_token_usage.total_tokens`), or `task_complete`
  (`last_agent_message` is the final response). `tail -f` follows a live
  session; the session id in the filename is the `resume` target.
