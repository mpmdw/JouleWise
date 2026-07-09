# 2026-07-09 Claude Code → Codex MCP Bridge

## Summary

User-directed hardening of the repository's Claude Code → Codex path. The
existing `.mcp.json` was structurally correct, but Claude had not approved the
project server, the Claude subagent/command were ignored machine-local files,
Codex had no root `AGENTS.md`, and there was no repeatable protocol-level
health check. The bridge is now durable in the repository and live-verified in
both directions of a Codex thread.

This changed process tooling only. No experiment code, methodology, schema,
hardware state, research claim, phase gate, or campaign data changed.

## Planning Audit And Queue Ranking

- Exact goal: make Claude Code able to start and continue a full Codex session
  from this repository while preserving JouleWise's documented orchestration,
  stop-card, review, and machine-state rules.
- Prior state inspected: root `README.md`, `CLAUDE.md`, `AGENT_PLAN.md`,
  `PROJECT_STATUS.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, Mission M0,
  `docs/orchestration.md`, D-050, the prior bridge run reports, `.mcp.json`,
  `.claude/`, and all three Codex bridge scripts.
- Inherited assumptions: the installed Codex and Claude Code authentication is
  user-owned; project MCP approval must remain an explicit Claude security
  decision; D-050's audited CLI path remains useful even after MCP becomes the
  primary interactive path.
- Queue classification: `CODEX-BRIDGE`, P0 Safety, `[AGENT]`. It executed now
  because it was an explicit user request and closes two process hazards:
  Codex sessions could bypass the repo intake rules, and delegated agent load
  could be sent into a `[QUIET-MAC]` measurement lane.
- Acceptance evidence: tracked entry points on a clean clone, live MCP schema
  inspection, Claude project approval, a real read-only Claude → Codex call,
  same-thread continuation, and a no-diff smoke result.
- Explicit non-goals: no dangerous bypass flags, no user-wide MCP install, no
  experimental feature enablement, no hardware/measurement execution, no
  commit/push/PR, and no advisor-status change.

## Changes

- Added root `AGENTS.md` so every Codex session rooted here inherits Mission
  M0 intake, stop-card precedence, queue/authority rules, verification and
  handoff duties, and the hard prohibition on delegating `[QUIET-MAC]`
  measurement work.
- Changed `.gitignore` narrowly so only `.claude/agents/codex.md` and
  `.claude/commands/codex.md` become tracked; unrelated local Claude state
  remains ignored.
- Reworked the Claude subagent and `/codex` command to use the project MCP
  `codex` / `codex-reply` tools as the primary full-session route, with
  explicit cwd, sandbox, approval, thread-continuation, diff-review, and
  process rules.
- Expanded `CLAUDE.md` into the repository authority for the primary MCP path,
  the D-050-audited CLI fallback, first-use approval, and verification.
- Added executable `scripts/check-codex-mcp.mjs`. It checks both CLIs, validates
  `.mcp.json`, performs a real MCP initialize + `tools/list` handshake, asserts
  the start/continuation schemas and full-session controls, and rejects
  pending, failed, or disconnected Claude project state.

## Verification

Installed versions:

```text
codex-cli 0.144.0
Claude Code 2.1.205
```

Protocol and configuration checks:

```text
node --check scripts/check-codex-mcp.mjs
bash -n scripts/codex-bridge scripts/codex-run
git diff --check
python3 -m unittest discover -s tests
  Ran 877 tests in 30.587s
  OK (skipped=10)
scripts/check-codex-mcp.mjs
  PASS: codex-cli 0.144.0
  PASS: Claude Code 2.1.205 (Claude Code)
  PASS: project MCP exposes full-session codex controls and codex-reply continuation
  PASS: Claude Code approved the codex server for /Users/edr/code/JouleWise
```

The direct MCP handshake returned exactly two launcher tools:

- `codex`, with `prompt`, `cwd`, `sandbox`, `approval-policy`, `model`,
  `developer-instructions`, and arbitrary `config` controls.
- `codex-reply`, with the returned `threadId` and a continuation prompt.

End-to-end interactive smoke:

- Claude Code approved only the tracked project `codex` server.
- Claude called `codex` in `/Users/edr/code/JouleWise`, read-only,
  `on-request`, with instructions to follow `AGENTS.md` and make no edits.
- Codex read `AGENTS.md` and `RUN_STATE.md`, returned
  `JOULEWISE_CODEX_MCP_OK`, and correctly reported that the CP-5 stop card was
  cleared and no stop card is active.
- Claude continued Codex thread `019f489c-800d-7372-b10e-dcb9fdca7a73`
  through `codex-reply`; it returned `JOULEWISE_CODEX_REPLY_OK`.
- Claude reported no files edited by the smoke. The lead diff check confirmed
  only this session's intended bridge/tooling/docs changes.

## Process Trace

- Active stop card at start: none (the CP-5 card is explicitly CLEARED).
- Skills/playbooks used: OpenAI docs skill; repository planning-reflection
  protocol; Mission M0; `docs/orchestration.md`.
- Subagents / delegated sessions:
  - role/lens: read-only Claude → Codex MCP start/continuation smoke.
  - model: installed Codex default via `codex mcp-server`.
  - prompt path or hash: interactive smoke, reproduced in the Verification
    section; no committed raw prompt file.
  - output path: interactive Claude session; success tokens and stable thread
    id reproduced above.
  - disposition: accepted as bridge evidence; no implementation content.
- Worktrees / branches / PRs: none.
- Invocation manifest path, if any: none; the only delegated call was the
  bounded smoke. D-050's audited `scripts/codex-bridge` remains required for
  substantial delegated implementation runs.
- Ephemeral artifacts:
  - path: `/tmp/probe-codex-mcp.mjs`.
  - stable id: superseded by tracked `scripts/check-codex-mcp.mjs`.
  - promoted_to: `scripts/check-codex-mcp.mjs`.
  - not_promoted_reason: n/a.
- Council/debate scorecard, if any: none; this was ordinary process tooling,
  not a methodology/schema/claim/hardware decision.
- Stop state at initial end: no active stop card; changes were left uncommitted
  pending user direction.

## Follow-Up Push

The user subsequently directed that all Codex-invocation files be pushed to
`main`. Commit `1d7c415` isolated the nine bridge/process files and was
fast-forwarded to `origin/main`. Concurrent C-027 council-review changes in the
working tree were explicitly excluded and left untouched.

## Next

Claude Code can now use the tracked `codex` subagent or `/codex` command in
this directory. Normal project work remains governed by the unchanged queue
and machine-state lanes. No site regeneration/deployment was performed because
this did not change advisor-visible research state; the follow-up request was
limited to committing and pushing the Codex invocation surface.
