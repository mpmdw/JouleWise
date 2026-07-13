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

1. Read root `AGENTS.md`; run Mission M0 for substantial work. Never launch
   agent load during `[QUIET-MAC]` measurement.
2. ROUTE by interaction shape (contract §4): MCP for interactive/discussion
   and short bounded turns; audited CLI (`codex-run-v3`, fallback
   `scripts/codex-bridge`) for autonomous, evidence-heavy, or long runs.
3. For a read-only interactive `GENRE: discussion` turn, use the reduced-header
   fast path in contract §1. Default to a context capsule with section-level
   authority anchors, current HEAD plus dirty/concurrent-writer state when
   repository-dependent, settled and rejected choices, and what remains open.
4. For workspace writes, choose one invocation id and run `scripts/bridge
   session-open ...`; embed its `header_fragment` unchanged. Overlap
   hard-blocks. The lease/baseline/thread primitives remain available for
   explicit recovery and lead overrides.
5. Call project MCP `codex` with the Git-root `cwd`, model `gpt-5.6-sol`,
   config
   `{"model_reasoning_effort":"<selected-effort>","mcp_servers":{"claude":{"enabled":false}}}`,
   `on-request` approvals, and the narrowest sandbox. The prompt begins with
   the applicable full or discussion-lane `BRIDGE_TASK_V1` header (contract
   §1) and carries `OUTPUT_PROTOCOL: bridge-report/v1`.
6. Put `BRIDGE_ORIGIN: claude` and `BRIDGE_HOPS_REMAINING: 0` in developer
   instructions. Sol must not call the project Claude MCP, `claude -p`, or
   any other Claude launcher; Claude owns cross-model discussion.
7. On return, parse the tolerant `BRIDGE_REPORT_V1` envelope: it has one
   sentinel, one final-line JSON object, the five required typed fields, and
   may carry unknown additional keys. Absent, duplicated, malformed, or
   non-final remains protocol failure, never success. Honor
   NEEDS_SCOPE/NEEDS_RULING by answering on the SAME thread with
   prospective-only scope expansion; on `route_cli`, re-dispatch per §4.
8. After writes, run `scripts/bridge session-close --invocation-id ID --status
   STATUS`. It receipt-anchors scope checking, releases only a clean completed
   session, and retains the lease for early returns or non-OK verdicts. Use
   primitives only for recovery or adjudicated overrides.
9. Thread reuse follows contract §5 (continue for rulings/fixes/deltas; fresh for
   new lenses, independence, or stale context; record `resume_policy`).
   A same-objective peer channel is never independent review. Proposal diffs
   remain read-only advice with `pathspec: []` and the aggregate size ceiling
   in the contract; the lead applies and verifies them. When applying one,
   keep the required durable thread/diff-or-hash/revision/proposer/application/
   verification provenance record.
10. The reverse `consult_fable` tool has a per-call `effort` field; Codex-side
    selection and the returned effort echo are documented in
    `.agents/skills/claude-consult/SKILL.md`.

The project `.mcp.json` pins `gpt-5.6-sol` with `high` only as a safe fallback
and disables the reverse Claude server for every Claude-originated session;
explicit per-task selection remains mandatory.

## Audited path

For D-050/D-064 runs, prefer `~/.local/bin/codex-run-v3` with model, selected
effort, genre, and exhaustive write scope. If unavailable, set
`CODEX_REASONING_EFFORT` to the selected tier and use `scripts/codex-bridge`.

Never use bypass flags, `danger-full-access`, or a second bridge hop.
