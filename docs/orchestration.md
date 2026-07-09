# The Orchestration Process

How this project is actually built: a human researcher directing a
multi-model AI system whose workflow is itself a deliberate, versioned,
self-instrumenting piece of engineering. This document is the single
in-repo description of that process. (The executable playbooks live
outside the repository as reusable "skills" so they transfer to future
projects; this page describes what they do and where their evidence
lands in this repo.) As of 2026-07-08.

## Roles: an apex model, a volume model, and a human at the top

- **Ed (researcher)** sets research direction, methodology
  non-negotiables (raw-evidence bundles, idle subtraction, named
  measurement boundaries, no unauditable claims), hardware/access
  decisions, and — critically — *process policy*: every rule below
  traces to a standing instruction issued after an observed failure or
  opportunity. External-facing claims and merge authority derive from
  him (he granted the lead conditional self-merge authority on
  2026-07-08 once the review gate had proven itself).
- **The lead** (Claude — Anthropic's Fable-class model) is the apex:
  decomposition, triage, design adjudication, every final diff gate,
  all live/hardware verification, merge decisions, bookkeeping, and
  process evolution. Ground truth of the system: every other model's
  role exists to *save lead-model capacity*, never because its judgment
  is preferred; all escalation paths terminate at the lead.
- **The volume model** (OpenAI Codex, gpt-5.5) does the heavy reading
  and writing: implementation against pinned specs, adversarial review
  lenses, test writing, test *auditing* (never of its own tests — a
  fresh instance audits), docs drafting, and review of the lead's own
  consequential decisions. Cross-model review is load-bearing by
  design: the attributed per-layer catch record (below) shows the two
  models consistently catching different classes of defect.
- **A third model tier** (Claude Opus) serves as specialist sweeper
  (e.g. the docs-consistency sweep) and, when a stream genuinely needs
  mid-stream judgment, as a stream director — a role that is now the
  exception rather than the default (see Topology).
- **Image-heavy analysis routes to Codex** as standing doctrine from
  C-012, after the site-observatory stream's image-critique rounds.
- **Invited-peer validation is allowed to overturn lead designs**; C-014
  recorded two lead designs overturned by an invited peer before
  implementation.

## The loop, end to end

Every substantial session runs one conductor procedure:

1. **Intake** — read `RUN_STATE.md` (the intake pointer), the task
   queue, the latest run report; never re-decide anything the decision
   log settled.
2. **Decompose** — split work into genuinely independent streams
   (disjoint expected diff footprints), one git worktree + branch each;
   assign each stream a review tier by *cost of being wrong*
   (measurement-semantics and contract-bearing work gets the full
   pipeline; docs get a light tier). Preflight gates: hardware-shaped
   streams require a confirmed device inventory; anything pinned
   without live validation carries a PROVISIONAL label; measurement
   sessions require a no-agent "quiet machine" lock.
3. **Per-stream pipeline** — for each reviewable unit: an invited
   design-argument round (the implementer must argue trade-offs before
   coding), implementation, then a layered review stack:
   2–3 fresh-instance counterreview lenses over the diff → lead triage
   with recorded dispositions → fixes → a dedicated test-amplification
   round (an independent writer adds edge-case tests) → a
   writer≠reviewer test audit (a fresh instance hunts tautological,
   vacuous, or wrong-expectation tests) → the lead's diff gate.
4. **Lead live gates** — never delegated: the lead runs the real flow
   (real corpus, real CLI, real hardware where present). This layer has
   repeatedly caught blockers no other layer saw, including defects
   whose own tests were green because the tests encoded the same wrong
   assumption as the code.
5. **Merge gate** — multi-commit series land as branch + PR. Before any
   merge: a pre-merge oversight pass by 2–3 fresh reviewers with
   distinct angles (deep regression hunt; claim-to-evidence trace;
   merge-order simulation across sibling PRs), lead triage, fixes, CI
   green. **Final-head rule:** any commit that lands after the last
   review round gets one more fresh review before merge — no commit
   merges unreviewed, however small (its first application caught a
   crash path in a "trivial" post-review fix).
6. **Integration review** — after parallel streams merge, one dedicated
   review hunts *interaction* defects no single-stream review can see.
   Its catches are definitionally unique (first outing: two).
7. **Bookkeeping** — a single session record (run report) with a
   verbatim process-trace appendix; the intake pointer and queue
   refreshed; a delegated docs-consistency sweep before the final
   commit (its latest pass found 15 real drift items; earlier passes
   found 5–6). Large documentation batches add the pre-commit
   docs-verify mode; the `consistency-sweep` skill owns that shape,
   including the D-043 supersession check.
8. **Same-session distillation** — lessons fold into the process
   playbooks the same session they are learned. Measured effect: one
   failure mode recurred five times before its fix was distilled, zero
   times after. The current operation-loop also runs its §0
   primary-deliverable check and §8 shipped-check before the session is
   considered done.
9. **Post-landing verification and close-out** — landed work gets the
   matching verification workflow with severity-tiered refuters; site
   changes add the regen+redeploy close-out step pointed to by
   `RUN_STATE.md` end-of-work step 8.
10. **Meta-review (the final step)** — event-driven, not calendar-driven:
    when a review layer stops earning its keep, when an intervention
    repeats despite a folded fix, or when the user asks, the loop is
    reviewed with its own evidence discipline (see Topology for the
    consensus one such review produced). After large workloads the
    post-large-workload meta-reassessment (owned by operation-loop §10)
    always fires, and it runs LAST.

### Stop cards and paused work

When a session stops with live work in progress, the lead creates or
updates an `ACTIVE_STOP_CARD` at the top of `RUN_STATE.md`. While active,
that card is the single restart authority and overrides every lower
"what next" list, queue rank, mission guide, and run-report default.

A stop card must name:

- the resume authority and exact artifact pointer,
- the reason for stopping,
- worktrees, branches, PRs, and off-repo artifacts that must not be
  cleaned accidentally,
- status terms for each paused item,
- the first resume action, and
- the clearance criteria.

Use these status terms for paused work:

| Term | Meaning |
|---|---|
| `APPLIED_UNVERIFIED` | A worker reports code or docs are applied, but the lead has not gated the diff. Not merge-safe. |
| `LEAD_GATED` | The lead has reviewed and run the required local/live checks for the item. |
| `PR_OPEN_CI_GREEN` | A PR exists and CI is green, but merge authority has not yet fired. |
| `MERGED` | The accepted work has landed on main. |
| `UNREAD_UNADJUDICATED` | A report/synthesis exists but has not been consumed into decisions, queue rows, or rejected findings. |
| `ADJUDICATED` | Findings have explicit accept/reject/defer disposition and downstream artifacts are updated. |

Before an intentional pause, do the minimal stop sync even if full
bookkeeping cannot fit: update only `RUN_STATE.md`'s stop card and the
rank-0 queue row. That is enough to prevent accidental bypass.

## The artifact system (where rigor becomes auditable)

Each fact has exactly one home; everything else points at it:

| Artifact | Role |
|---|---|
| `docs/decision_log.md` | Binding design decisions, each with alternatives considered, consequences, and revisit conditions. The log is the count authority; nothing re-decides these silently. |
| `docs/council_log.md` | The deliberation record: review-council positions, reasoning exchanged, who prevailed, overridden dissents — so a future reader can reconstruct *why*, not just *what*. The log is the range/count authority. |
| `docs/contracts/` | Claim/evidence contracts: `claims_ladder.md` (D-037) plus `analysis_plans.md` (D-038) form the claim gate; strict validation is the evidence ticket. |
| `docs/stream_logs/` | Per-stream decision ledgers, committed WITH the code they justify: every non-trivial in-stream decision (`A-1..A-30`, `B-1..B-46`, …) with mandatory evidence pointers; wrong pins are SUPERSEDED in place, never erased. |
| `docs/run_reports/` | One record per working session: outcomes, verification evidence, a per-layer catch/yield table, the delegation-calibration ledger, restart instructions. |
| `TASK_QUEUE.md` | Ranked queue with machine-state lanes ([QUIET-MAC] / [AGENT] / [ED-EXTERNAL]) — a session picks the top task *compatible with the machine's state*, so agent load never contaminates measurements. |
| `RUN_STATE.md` | Intake pointer only: current state, latest report, next action. History lives in run reports. |
| `docs/risk_register.md` | Live risks with triggers and mitigation states. |

Instrumentation ledgers close the loop on the process itself:

- **Per-layer yield:** every review layer's unique catches are
  attributed and tallied per session under D-061 (C-027; replaces the
  earlier two-zero-sessions auto-drop, which the integration-review
  zero/zero/five sequence falsified): applicability is decided by
  PRE-DECLARED mechanical predicates; outcomes are classified
  accepted-unique-defect / duplicate / clean-verification /
  false-positive-suppression (suppression is not a catch); severity
  weights are fixed before the session; three applicable exposures
  TRIGGER an expected-loss review decision, never automatic deletion;
  safety/final-head/integration layers are never auto-dropped on
  zero-defect streaks. (One layer, the default Opus review lens, was
  dropped under the old rule before D-061.)
- **Delegation calibration:** every delegated unit gets a row — task
  altitude (pinned-spec / design-freedom / judgment-call), outcome
  (assigned by the lead after the gate, never self-labeled), catches,
  and lead rework minutes, with prompt-defects separated from
  model-defects. Delegation boundaries move on this evidence, not
  vibes. Current signal: pinned-spec delegation runs essentially
  defect-free; the serious defects cluster in volunteered additions and
  design-freedom wire contracts — which is exactly where the full lens
- **Invocation manifest:** substantial delegated/tool/skill runs get a
  lightweight manifest row per invocation. Minimum fields:
  `run_id`, `parent_report`, `role_or_lens`, `model`, `wrapper`,
  `session_id`, `prompt_sha256`, `prompt_path`, `output_path`, `status`,
  `consumed_by`, `disposition`, and `commit_or_pr`. Raw logs can stay
  out of git; every ephemeral artifact still needs a committed pointer
  row with `path`, `sha256` or stable id, `promoted_to`, and
  `not_promoted_reason`.

## Council discipline

Councils are expensive instruments. Use a full council for methodology,
measurement validity, schema/contract changes, claim boundaries, hardware
protocols, or explicit user requests. For ordinary implementation, use a
small number of targeted lenses plus lead adjudication.

Every high-impact council must leave a durable scorecard:

- unique catches by severity,
- accepted/rejected/deferred/false-positive counts,
- lead triage and rework time when practical,
- shipped artifacts,
- queue rows created or re-ranked,
- decision-log IDs promoted, and
- a disposition table: finding → ruling → owner → artifact/queue/decision
  target → closure check.

Deferred decision-log promotion is itself a tracked obligation, not
ambient prose in a report.

## Topology: how it evolved (an example of the loop improving itself)

- **v1 (2026-07-07 AM):** per-stream Fable orchestrator subagents, each
  driving its own Codex thread. Worked, but expensive at the apex tier.
- **v2 (2026-07-07 PM):** Opus orchestrators directing Codex, Fable
  apex-only. Ran four streams — and surfaced a structural flaw: subagent
  orchestrators are not woken by their childrens' completion (the "wake
  gap"), forcing the lead to babysit with heartbeats. The session's own
  trace captured two fleet-wide stalls.
- **Meta-review (C-009):** a signed cross-model consensus — two blind
  Codex analyses vs. the lead's blind position, one conferral round —
  produced a hybrid: the lead drives pipeline-shaped streams directly
  (inheriting the harness's only reliable wake guarantee); subagent
  directors are reserved for judgment-heavy streams.
- **Validation (C-010, 2026-07-08):** the first full session under the
  new topology ran ~26 Codex sessions across four streams — resume
  through merge — with zero coordination stalls, zero manual wake
  interventions, and no subagent stream directors at all.
  The consensus is now the stamped default.

The same mechanism has overturned the lead's own designs: a Codex
review of the lead's process schemas rejected two of them and supplied
better ones (now the v2 ledger and calibration formats), and review
lenses have refuted two of the lead's sanctioned wire-protocol pins
before they could reach hardware. Seniority is not infallibility; the
adjudication of every such challenge remains the lead's.

## What one session looks like (2026-07-07/08, the merge session)

Four checkpointed streams resumed, completed, and landed as four PRs:
the integrity/provenance overhaul (all 31 audit-pinned defects fixed;
strict validation now re-derives the power trace from raw evidence),
the docs package, the KV-cache replay feasibility verdict, and the
complete fixture-first NVIDIA stack. The layered review recorded, among
~30 attributed catches: two blockers found only by fresh-instance
lenses (a provenance hash that did not prove the actual generation
input; a strict-gate bypass via mutable metadata), two pinned wire
contracts overturned before hardware contact, one fabricated-evidence
defect caught only at the lead's diff gate, two integration defects
caught only by the post-merge integration review, and a crash path
caught only by the final-head rule on the last commit of the night.
Suite: 415 → 546 tests, zero expected failures. Roughly two dozen
delegated Codex sessions; the lead never wrote implementation code and
never skipped a gate.

## Reconstructing the loop on a clean machine

Pointer map only; mechanics stay in their owning files.

- Committed invocation wrapper: `scripts/codex-run`.
  Usage: `codex-run <out.md> [--timeout SEC] [-C DIR] [-s SANDBOX] [--resume] '<prompt>'`.
  It writes `<out>.status`.
- Project bridge: `scripts/codex-bridge`; writes prompt snapshots,
  response snapshots, logs, status files, and
  `.codex-bridge/invocation_manifest.jsonl` rows with prompt/output/log
  hashes.
- Skill-only mechanics on the operator's machine live under
  `~/.claude/skills`: `operation-loop` is the conductor,
  `codex-delegation` is the invocation/consumption contract,
  `adversarial-review` defines refutation tiers,
  `multi-stream-worktrees` defines parallel stream mechanics,
  `consistency-sweep` owns drift control, and `council` owns
  triggers/roles.
- Repo-derivable on a clean clone: this file gives the loop shape;
  council log C-009/C-010 give topology and gates; the claims and
  analysis-plans contracts give claim gating; `docs/stream_logs/` and
  `docs/run_reports/` provide live templates for ledgers and trace
  appendices; `scripts/codex-run` and `scripts/codex-bridge` provide
  execution entry points.
- Skill-only: exact conductor sequencing, Codex prompt/consumption
  contract, severity-tiered refuter recipes, multi-worktree stream
  operations, and consistency-sweep checklists.

## Where to read the evidence

- Yield tables and calibration aggregates: the latest run reports
  (`docs/run_reports/2026-07-07-resume-merge-session.md` and
  `...checkpoint-multistream-session.md`).
- Deliberations and consensus texts: `docs/council_log.md` (C-007
  design council; C-009 topology consensus; C-010 validation).
- The binding rules themselves: `docs/decision_log.md`.
- Per-decision, in-stream reasoning: `docs/stream_logs/`.
