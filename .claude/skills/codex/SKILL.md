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
(`bridge-protocol/v1`) — the ONE home. This section is the operating
sequence, not the contract.

1. Read root `AGENTS.md`; run Mission M0 for substantial work. Never launch
   agent load during `[QUIET-MAC]` measurement.
2. ROUTE by interaction shape (contract §4): MCP for interactive/discussion
   and short bounded turns; audited CLI (`codex-run-v3`, fallback
   `scripts/codex-bridge`) for autonomous, evidence-heavy, or long runs.
3. For workspace writes, choose one invocation id; pass it to `lease-acquire
   --invocation-id ID`, `baseline --invocation-id ID`, and `thread-record
   --invocation-id ID --state pending`. Overlap hard-blocks.
4. Call project MCP `codex` with the Git-root `cwd`, model `gpt-5.6-sol`,
   config
   `{"model_reasoning_effort":"<selected-effort>","mcp_servers":{"claude":{"enabled":false}}}`,
   `on-request` approvals, and the narrowest sandbox. The prompt begins with
   the `BRIDGE_TASK_V1` header (contract §1) carrying WRITE_SCOPE, BASE_HEAD,
   baseline pointers, acceptance, and `OUTPUT_PROTOCOL: bridge-report/v1`.
5. Put `BRIDGE_ORIGIN: claude` and `BRIDGE_HOPS_REMAINING: 0` in developer
   instructions. Sol must not call the project Claude MCP, `claude -p`, or
   any other Claude launcher; Claude owns cross-model discussion.
6. On return: parse the `BRIDGE_REPORT_V1` envelope (absent/duplicated/
   malformed/non-final = protocol failure, never success); honor
   NEEDS_SCOPE/NEEDS_RULING by answering on the SAME thread with
   prospective-only scope expansion; on `route_cli`, re-dispatch per §4.
7. After writes, run `scripts/bridge scope-check ... --expect-digest
   sha256:...` using the baseline output; only SCOPE_OK needs no adjudication.
   Then record the new thread state and release the lease when work closes.
8. Thread reuse per contract §5 (continue for rulings/fixes/deltas; fresh for
   new lenses, independence, or stale context; record `resume_policy`).

The project `.mcp.json` pins `gpt-5.6-sol` with `high` only as a safe fallback
and disables the reverse Claude server for every Claude-originated session;
explicit per-task selection remains mandatory.

## Audited path

For D-050/D-064 runs, prefer `~/.local/bin/codex-run-v3` with model, selected
effort, genre, and exhaustive write scope. If unavailable, set
`CODEX_REASONING_EFFORT` to the selected tier and use `scripts/codex-bridge`.

Never use bypass flags, `danger-full-access`, or a second bridge hop.
