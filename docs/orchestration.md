# The Orchestration Process

How this project is actually built: a human researcher directing a
multi-model AI system whose workflow is itself a deliberate, versioned,
self-instrumenting piece of engineering. This document is the single
in-repo description of that process. (The executable playbooks live
outside the repository as reusable "skills" so they transfer to future
projects; this page describes what they do and where their evidence
lands in this repo.) Binding role and process changes live in
`docs/decision_log.md`; this page avoids copying volatile model versions.

## Roles: a lead, independent implementers/reviewers, and a human at the top

- **Ed (researcher)** sets research direction, methodology
  non-negotiables (raw-evidence bundles, dual-basis capture with gross-energy
  headlines, named
  measurement boundaries, no unauditable claims), hardware/access
  decisions, and — critically — *process policy*: every rule below
  traces to a standing instruction issued after an observed failure or
  opportunity. External-facing claims and merge authority derive from
  him (he granted the lead conditional self-merge authority on
  2026-07-08 once the review gate had proven itself).
- **The designated lead** owns
  decomposition, triage, design adjudication, every final diff gate,
  all live/hardware verification, merge decisions, bookkeeping, and
  process evolution. Other agents save lead capacity without inheriting
  final authority; all escalation paths terminate at the lead.
- **Independent implementation and review agents** do the heavy reading and
  writing: implementation against pinned specs, adversarial review
  lenses, test writing, test *auditing* (never of its own tests — a
  fresh instance audits), docs drafting, and review of the lead's own
  consequential decisions. Cross-model review is load-bearing by
  design: the attributed per-layer catch record (below) shows the two
  roles consistently catching different classes of defect.
- **Specialist agents** handle bounded sweeps (for example, docs
  consistency) and, when a stream genuinely needs
  mid-stream judgment, as a stream director. AMENDED by D-129
  (Ed, 2026-08-09): lieutenant-directed executor lanes are the standing
  default shape under the lead-token economy (current model assignments
  live in D-129 and the memory index, not here) — the "exception rather
  than the default" framing below reflects the C-009/C-010 record of
  its day and is superseded for current operation (see the decision log).
- **Image-heavy analysis uses the designated image-capable review route** per
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
   green. Gate ledger: twelve-row PR-body table (`.github/pull_request_template.md`), checked by
   `scripts/check_gate_ledger.py` in the advisory `gate-ledger` workflow — see D-170. **Final-head rule:** any commit that lands after the last
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
   matching verification workflow with severity-tiered refuters. Sessions
   that change front-facing state refresh `docs/site/DRIFT.md`; no agent
   regenerates or deploys the site. Automation informs and Ed deploys
   manually, per D-068 and `RUN_STATE.md` end-of-work step 8.
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
| `docs/process/state_kernel.json` | Source of truth for work selection: active gates, dependencies, and machine-state lanes ([QUIET-MAC] / [AGENT] / [ED-EXTERNAL]). |
| `TASK_QUEUE.md` | Generated detailed queue projection plus dated history; do not hand-copy its live rows into reader docs. |
| `RUN_STATE.md` | Intake pointer with the generated restart projection. History lives in run reports. |
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
  zero-defect streaks. (One layer, the default specialist review lens, was
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

## Spend guardrails (WO-022; R2 ruled, Ed-ratified 2026-07-13)

The following policy text is the R2-ratified section, landed verbatim per
audit work order WO-022 (`docs/reviews/2026-07-13-comprehensive-audit/`).

SPEND GUARDRAILS (capstone benchmark bands) — provisional calibration constants; review after two completed arcs; sunset at capstone submission.

1. ACCOUNTING SOURCE. Sol spend: `codex-usage` local accounting (the standing snapshot convention), corroborated by codex-run-v3 manifest `token_usage` rows where populated. The extraction window must cover the full arc — sum incremental snapshots for multi-day arcs; a single trailing-24h view is insufficient. Fable spend: estimated from local usage accounting; each snapshot names its method and price-table version. Price table v2026-07 (pinned until amended): GPT-5.6-sol $5/$30 per M in/out, cached input $0.50; Fable 5 $10/$50, cache reads $1. All figures are estimates, not billing truth, and are recorded as such. Missing data is recorded as `accounting_unknown`, never as zero.

2. DENOMINATOR AND CACHED-TOKEN TREATMENT. Token bands count total tokens (cached + uncached, all directions) exactly as codex-usage reports them — cached tokens are never excluded (exclusion invites cache-heavy gaming). Dollar figures apply cached pricing honestly. Cross-family aggregate ceilings bind in combined estimated dollars, because raw cross-family token sums are not commensurable (C-028: Sol ~180x the token volume, Fable ~3.4x the cost).

3. BOUNDARIES AND ATTRIBUTION. An arc = one council-log C-row, opened at its first delegated session, closed at its closeout snapshot. A work order = one WO/task id. Failed calls, retries, resumes, refuters, fix rounds, delta re-audits, lead usage, and subagents all count against the initiating WO and arc. Arcs and WOs may not be split, renamed, or reopened to reset counters.

4. BANDS. Each dimension is independent. SOFT crossing = record-and-continue: flag in the spend snapshot plus a one-line justification in the council row. HARD crossing = pause-and-ask Ed before any NEW delegated work in that category; in-flight sessions finish; quiet-machine measurement is never interrupted.

   | Scope | Soft | Hard |
   |---|---|---|
   | Sol high session | 6M tokens | 12M |
   | Sol xhigh session | 8M | 16M |
   | Sol ultra session | 40M | 60M |
   | Bench-effort WO | 10M / 3 Sol sessions / ~$40 combined | 20M / 6 / ~$80 |
   | Session-effort WO | 30M / 8 Sol sessions / ~$100 combined | 60M / 12 / ~$200 |
   | Arc | 100M / 25 Sol sessions / ~$400 combined / 6 Sol active-hours / 2 elapsed days | 200M / 40 / ~$800 / 12 h / 4 days |

   WO dollar figures are best-effort: when per-WO Fable attribution is accounting_unknown, the token/session pair binds. Ultra: at most 2 INTENDED ultra sessions per arc, each with a pre-run recorded statement of why xhigh is insufficient and what bounded subagent work it will perform; an unintended ultra is recorded as an anomaly and still counts.

   Calibration anchors (recorded so recalibration stays honest): healthy xhigh ≈ 2.3–3.5M tokens/session (C-030 post effort-fix; C-028 average); the recorded broken state averaged ~9M. C-028 (330.6M / 59 sessions / ~$1,050 / ~17.5h) crosses every substantive arc HARD dimension — it is the anti-example. The 2026-07-13 comprehensive audit (~30 Sol sessions + ~70 Fable agents, Ed-authorized) crosses arc SOFT on session count only — the intended "exceptional: justify and continue" outcome.

5. CHECKPOINTS (procedural; owner = the Fable lead). (a) At arc open: predeclare one accepted deliverable increment for the arc — a corpus/measurement result, analysis/figure/report increment, evaluator requirement, or cited advancement of a D-060 gate — and classify planned delegated work as deliverable-facing or process-facing (mixed sessions count as process-facing unless separately attributable). (b) Before each next delegated call: check the completed session against its tier band (a lightweight glance, not a full snapshot); no runtime killing is promised — evaluation happens on completed sessions before any resume, replacement, or new call. (c) At WO close and arc close: take the spend snapshot and evaluate all bands. One missed checkpoint blocks new process-facing delegation until reconciled.

6. DELIVERABLE-PROGRESS TRIPWIRE (binds while ANY D-060 gate is unmet). If process-facing combined estimated cost exceeds 33% of arc cost OR $250 — whichever occurs first — HARD pause-and-ask Ed before further process-facing delegation. Independently, an arc that closes with process-facing spend but NO accepted deliverable increment pauses further non-exempt process work even if the 33% threshold was not crossed.

7. EXCEPTIONS AND OVERRIDES. Gate-closing work is deliverable-facing by definition. Correctness-defect and data-preservation work may override the allocation tripwire but is always fully counted. Ed direction is NOT a blanket exemption (the finding's own exemplar — bridge v1/v1.1 — was Ed-directed): it is a recorded override carrying an incremental budget and an expiry, and its spend counts.

8. NAMED-FAILURE BAR FOR PROCESS INNOVATION. Any NEW process layer, tool, skill, wrapper version, or contract version requires a decision-log entry citing: (a) a named recorded failure it addresses, (b) why existing controls did not cover it, (c) the smallest new layer that does, (d) its applicability predicate, (e) its marginal budget, (f) a sunset/retirement condition. Absent that entry, it is D-060 breadth and waits for the gates.

9. KEEP-DEFENDER GUARANTEE. No cap consequence auto-deletes a review layer. Layers with recorded unique catches survive any cap; a cap response batches, rescopes, or seeks Ed approval — never silently drops catch-bearing gates (final-head, integration, lead-live, claim/evidence safeguards).

10. MECHANISM. This policy is PROCEDURAL, not mechanical: no checker script is built now (adding process code during an overengineering correction is self-defeating; the arithmetic is a handful of numbers already recorded at existing snapshot points). Two recorded accounting discrepancies or skipped checkpoints across two arcs constitute the named failure that authorizes an executable checker with tests — via the §8 bar.

11. RECALIBRATION AND OWNERSHIP. Band values are calibration constants: the lead may amend SOFT values at arc close with evidence via a one-line decision-log amendment; HARD values and this section's structure are Ed-owned. Scheduled review after two completed arcs. The whole policy sunsets at capstone submission.

Court amendments (T09, folded at the register): canonical session
inclusion uses manifest-corroborated sessions with known token records;
resume rows are deduplicated; non-manifest sessions are reported only as
a labeled upper bound. The 2026-07-13 audit anchor in section 4 is
estimated/accounting_unknown until an audit-close spend snapshot receipts
it (docs/reviews/2026-07-13-comprehensive-audit/receipts/
WO-022-audit-close-spend.json); only a receipted anchor may be used for
recalibration.

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
  hashes plus the `sandbox` mode the launch actually received
  (`review` is read-only; `new` and `resume` are workspace-write).
- Workspace-write bridge ceremony: `scripts/bridge session-open` and
  `session-close`; the reduced discussion header, tolerant return envelope,
  receipt anchoring, and recovery primitives are defined only in
  `docs/contracts/bridge_protocol.md` (`bridge-protocol/v1.1`).
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
- Skill-only: exact conductor sequencing, delegated-agent prompt/consumption
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

## Addendum 2026-09-04 — direct seats, replay custody, and cold-gate isolation

This addendum records execution details exposed by the 2026-09-02/03
hands-free work. It does not change the standing rule that a stream director is
used when a stream needs continuing judgment.

### Direct model seats

A *direct seat* is a bounded model invocation started by the lead through the
runner, without a second model session whose only job is to start and watch it.
After the lead has fixed the role, prompt, authority, and review lens, use the
direct seat; retain a stream director only when that director will make real
mid-stream judgments. This avoids paying for an otherwise passive wrapper while
preserving lead review of every merge-bound result
(`docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`,
“2026-09-03 21:05 update”).

Before a direct runner invocation, record its checkout, starting revision,
comparison base, write scope, output path, report genre, and expected
verification. Put a read-only seat in a clean disposable checkout or archive,
because lead-created untracked files can make the runner report a scope failure
even when the seat changed nothing. Keep the machine-readable report envelope
within its declared byte limit and put detailed audits in the prose body. A
runner failure caused only by pre-existing, explicitly attributed dirt is not a
semantic verdict; the lead records and adjudicates the mismatch before using
the result
(`docs/process_traces/2026-09-02-dx-registry/MAGISTRATE-NOTES.md`;
`docs/process_traces/2026-09-02-dx-registry/22a-terra-243-protocol-failure.md`;
`docs/process_traces/2026-09-02-hands-free-week/17i-watchdog-04-refuter-execution.md`).

After an interrupted wrapper or usage cutoff, inspect the named worktree,
branch, report, status file, and log before launching a replacement. A finished
model run may outlive the wrapper that started it; harvesting that evidence is
the first recovery action, and blind relaunch is prohibited
(`docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`,
“Resume sequence after a usage stall”).

### Replay custody

A *replay* is a repeated check used to show that a reviewed result still holds
at a named candidate revision or integration tree. Run a merge-bearing replay
in a clean disposable tree, record the exact revision and merge parents, the
working directory, full command, unpiped log, exit status, and stable tail. Run
each mutation from a fresh baseline or verify the restored file digest before
the next mutation. When reproducibility of a generated artifact is claimed,
reissue it at the candidate revision and compare bytes with the issued artifact
(`docs/process_traces/2026-09-02-hands-free-week/17c-planpin-06-fix-round-1.md`;
`docs/process_traces/2026-09-02-hands-free-week/17h-watchdog-03-fix-round-1.md`;
`docs/process_traces/2026-09-02-paper-d-dg071/43-integration-replay-and-terminal-review-e7425eef.md`).

### Cold-gate packets and seats

A *cold gate* is an independent review performed before an irreversible process
mechanism is accepted or installed. Its packet must use neutral, separable
questions; distinguish executed observations from proposals; time- or
revision-pin volatile facts; and list every load-bearing source or bounded
excerpt with its path, digest, and relevant span. Commands in the packet must
be checked for side effects: a mode-changing option followed by `--help` is not
assumed to be read-only. Contrary evidence and competing positions receive the
same level of detail
(`docs/process_traces/2026-09-02-hands-free-week/12-coldgate-opus-refutation-packet-11.md`,
“Q8 — Packet hygiene”; `docs/process_traces/2026-09-02-hands-free-week/14-coldgate-fable-ruling-packet-11.md`,
“Q8 — Packet hygiene”).

Every cold-gate seat receives a distinct scratch directory and sealed output.
It must not read another seat's scratch material or answer before its prescribed
independent read order is complete; the lead opens and compares the outputs
only after both are sealed. The first watchdog convening shared scratch space,
and the relaunch cured that defect by separating the seats
(`docs/process_traces/2026-09-02-hands-free-week/15-watchdog-gate-synthesis.md`).

### First-use evidence

A *first-use review* checks that a defined term or code literal is built or
glossed before a reader must rely on it. For contract edits that add, move, or
rename such terms, the pre-landing first-use table is mandatory. A behavioral
clause also needs an executed probe of its first real use; a vocabulary pass or
an implemented mechanism cannot substitute for that probe
(`docs/process_traces/2026-09-03-kernel-batch/01-lieutenant-report.md`,
“Item 1 — the D-171 addendum”; `docs/process_traces/2026-09-02-hands-free-week/17k-watchdog-05-refuter-contract.md`,
finding F4).
