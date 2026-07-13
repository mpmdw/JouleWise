# JouleWise Agent Instructions

These instructions apply to every Codex session rooted in this repository,
including sessions started by Claude Code through the project MCP server.

## Delegated-session write authority

A session is delegated when its prompt contains `SESSION_MODE: delegated` or a
`WRITE_SCOPE:` field.

For every delegated session, `WRITE_SCOPE` is the exhaustive repository write
allowlist. It takes precedence over all repository-local workflow instructions,
including this file's end-of-work checklist and instructions to update
`RUN_STATE.md`, `TASK_QUEUE.md`, plans, reports, generated documentation, or tests.
Those files are lead-owned unless their exact paths are explicitly included in
`WRITE_SCOPE`.

Repository instructions may require a delegated worker to read or inspect a file,
but they never implicitly authorize writing it. Test failures, consistency repairs,
generated artifacts, tidy-tree work, and work believed necessary for completion do
not expand the allowlist.

If an unlisted write appears necessary, the worker must preserve that path, complete
independent authorized work, and stop with a blocking scope-expansion request.

The same early-return rule applies to any blocking decision that is not the
worker's to make — naming, contract semantics, spec conflicts, authority gaps.
Do not guess and do not invent: finish independent authorized work, then stop
with a blocking question (the NEEDS_RULING shape: question, options considered,
recommendation, blocked work). The lead always resumes compliant early-returns
with an answer; a short round-trip is always cheaper than a wrong guess. Only
the lead can approve an expansion through a new or resumed prompt. Approval is
prospective; an already-made out-of-scope edit remains a scope violation.

For lead sessions without a `WRITE_SCOPE` field, the normal end-of-work
expectations below continue to apply.

## Intake And Authority

For any substantial task:

1. Read the targeted sections of `RUN_STATE.md`: `ACTIVE_STOP_CARD`, Current
   Project Status, Known Workspace State, and What Is Next. An active stop card
   overrides every other restart or queue pointer.
2. Read the Current Queue and Do-Not-Do-Yet sections of `TASK_QUEUE.md`. Triage
   a new user request there before treating it as ordinary next work.
3. Run Mission M0 in `docs/agent_playbook.md`. For delegation, review, or
   multi-stream work, also read `docs/orchestration.md` before landing changes.
4. Consult the owning plan, contract, exit checklist, and targeted decision-log
   entries instead of re-deciding settled policy. The source-of-truth map is in
   `AGENT_PLAN.md`.
5. Inspect `git status --short --branch` and preserve unrelated or untracked
   user work.

Direct, bounded questions may use a smaller read set, but stop cards, workspace
safety, and machine-state lanes always apply.

## Machine-State Safety

A Codex or Claude session is agent load. Never start or continue a
`[QUIET-MAC]` measurement task from this bridge: no production campaigns,
detection-floor captures, powermetrics sessions, or other quiet-window data
collection. Report the gate and hand it back for a clean, lead-controlled
session. `[AGENT]` work is compatible with this bridge; `[ED-EXTERNAL]` work
requires the user.

Never present fixture-first or mock evidence as live hardware validation.
Preserve PROVISIONAL labels until the owning live gate is actually satisfied.

## Bidirectional Agent Bridge

This repository supports one bounded cross-model hop in either direction:

- Claude Code may start or continue Sol through the project Codex MCP server.
  Such prompts must carry `BRIDGE_ORIGIN: claude` and
  `BRIDGE_HOPS_REMAINING: 0`; the Claude-side MCP configuration also disables
  the reverse Claude server inside that Sol session.
- A top-level Codex session may request a read-only Fable judgment consult via
  the project Claude MCP `consult_fable` tool and
  `.agents/skills/claude-consult`. The tracked MCP adapter pins Fable/high,
  plan mode, no session persistence, no slash commands, an empty MCP registry,
  and only read/search tools. The project allowlists and preapproves only this
  consult tool.

Never bounce one bridge call back through the other, never use the reverse path
from a Claude-originated Sol session, and never delegate final verification or
authority decisions. The top-level caller remains lead and adjudicates the
peer's advice.

The full wire contract is `docs/contracts/bridge_protocol.md`
(`bridge-protocol/v1`) — prompt header, return envelope, early returns,
routing, thread semantics, leases, and scope checking. A Sol session working
under this bridge MUST: honor the `BRIDGE_TASK_V1` header (especially
`WRITE_SCOPE` — never infer extra scope); end every MCP turn with the
`BRIDGE_REPORT_V1` sentinel plus one minified JSON line (an audited CLI run
with a valid `claude-codex-report/v1` body is trailer-exempt); return
`NEEDS_SCOPE`/`NEEDS_RULING` instead of guessing; return `PARTIAL` with a
`route_cli` flag when MCP work outgrows a short bounded turn; and run the
end-of-turn self scope audit against the provided baseline manifest. Claude
verifies mechanically with `scripts/bridge scope-check`; the self-audit is
defense-in-depth, not the backstop.

## Work And Verification

- Follow the repository contracts and keep raw evidence and run bundles
  immutable.
- Prefer bounded, reviewable changes. Do not commit, push, merge, deploy, or
  perform destructive Git operations unless the user explicitly requests it or
  the current lead instructions clearly grant that authority.
- Use the narrowest safe sandbox and request approval for actions that need
  more access. Never use dangerous sandbox/approval bypass flags.
- For code changes, run the relevant focused checks and the canonical suite:
  `python3 -m unittest discover -s tests`. Docs-only or tooling-only work may
  use targeted checks when the run report explains why the full suite was not
  needed.
- If installed Codex skills, plugins, MCP tools, browser/image tools, goals, or
  multi-agent capabilities materially help the assigned task, use them under
  their own instructions and the same repository safety rules. Do not install,
  authorize, or publish external integrations without user authority.
- The lead owns final diff review, live/hardware gates, merge decisions, and
  adjudication of delegated findings, per `docs/orchestration.md`.

## Handoff

Return a concise summary with findings, changed files, verification, blockers,
and the next exact step. A substantial run must also update `RUN_STATE.md`,
`TASK_QUEUE.md`, and a dated report under `docs/run_reports/`; update
`PROJECT_STATUS.md` only when advisor-visible state changed. Record delegated
process evidence at the level required by D-050 and `docs/orchestration.md`.
