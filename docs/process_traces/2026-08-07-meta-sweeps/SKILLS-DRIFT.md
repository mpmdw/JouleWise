Reading additional input from stdin...
OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: high
reasoning summaries: none
session id: 019fdda8-9c42-7721-ac94-3dec7b30128c
--------
user
SKILL-STACK DRIFT AUDIT (read-only; no writes; final message = report). A snapshot of the orchestration skill stack is at /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/ (council, codex-delegation, adversarial-review, multi-stream-worktrees, consistency-sweep, operation-loop dirs + skill-usage-log.md). Audit: (1) internal contradictions between skills (one-fact-one-home violations, cadence numbers that disagree, duplicated rules that drifted apart); (2) skill text vs the usage log's recorded deviations — rules the log shows repeatedly deviated-from (candidates for amendment) and validated patterns not yet folded in; (3) stale references (files, flags, wrapper names, model names that no longer exist — e.g. check codex-run vs codex-run-v3 vs bridge references, 5.5-era vs Sol-era labels); (4) the fast-mode/service-tier guidance — is it recorded anywhere in the skills and is it consistent with per-call-only doctrine? Deliver ranked findings with exact file:line, and the top 5 fold-in candidates with draft one-line amendments.
codex
I’ll audit the snapshot strictly read-only. I’ll first inventory the skill files and usage log, then cross-check the repository’s current bridge/orchestration contracts so stale-name findings are anchored to present sources of truth.
exec
/bin/zsh -lc "pwd && git status --short --branch && rg --files /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot | sort && printf '\\n--- repo intake files ---\\n' && rg --files -g 'RUN_STATE.md' -g 'TASK_QUEUE.md' -g 'docs/agent_playbook.md' -g 'docs/orchestration.md' -g 'docs/contracts/bridge_protocol.md' -g 'AGENT_PLAN.md'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
## main...origin/main
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md

--- repo intake files ---
RUN_STATE.md
TASK_QUEUE.md
AGENT_PLAN.md
docs/agent_playbook.md
docs/orchestration.md
docs/contracts/bridge_protocol.md

exec
/bin/zsh -lc "rg -n '"'^#{1,4} (ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next|Current Queue|Do-Not-Do-Yet|Mission M0)'"' RUN_STATE.md TASK_QUEUE.md docs/agent_playbook.md && sed -n '1,220p' docs/orchestration.md && sed -n '1,260p' docs/contracts/bridge_protocol.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
docs/agent_playbook.md:50:## Mission M0: Preflight (every session)
TASK_QUEUE.md:306:## Current Queue
RUN_STATE.md:2043:## ACTIVE_STOP_CARD
RUN_STATE.md:2182:## Current Project Status
RUN_STATE.md:2743:## Known Workspace State
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
  mid-stream judgment, as a stream director — a role that is now the
  exception rather than the default (see Topology).
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

# Claude ↔ Codex Bridge Protocol

`bridge-protocol/v1.1`

This contract defines the task, return, scope, concurrency, continuation, and
reverse-consult protocols used when Claude and Codex collaborate on JouleWise.
Its goals are bounded authority, machine-detectable outcomes, recoverable
threads, attribution-aware workspace writes, and concise peer discussion.
Repository safety rules and lead authority remain controlling.

Provenance: co-designed by the Fable lead and gpt-5.6-sol over the MCP bridge
itself (3 rounds, 2026-07-13; thread recorded in
`docs/run_reports/2026-07-13-bridge-v1.md`).
The five in-draft choices were adjudicated by the lead at review.

Provenance for v1.1: amendments co-designed by the lead and a Sol xhigh
consult on 2026-07-13, thread
`019f5d1d-b681-7db1-8714-812fdd2f198b`.

### Changes from v1

Version 1.1 adds the read-only discussion lane, fail-closed session wrappers,
tolerant single-line envelopes, per-call reverse-consult effort, peer channels
and bounded proposal diffs, and a single-envelope protocol-deviation path.

## 1. Prompt contract

Every delegated prompt MUST begin with a machine-readable task header: a
`BRIDGE_TASK_V1` sentinel line, one JSON object, and an `END_BRIDGE_TASK_V1`
sentinel line. JSON gives the tracked helper and future adapters one
unambiguous representation.

Required fields:

- `TASK_SHAPE`: Interaction shape; one of `interactive`, `bounded`, or
  `autonomous`.
- `GENRE`: Work genre; one of `discussion`, `implementation`, `review`, or
  `diagnosis`.
- `ROLE`: One bounded worker role or review lens.
- `OBJECTIVE`: One concrete requested outcome.
- `AUTHORITY`: Ordered authority pointers and inline rulings; highest
  authority first.
- `WRITE_SCOPE`: Exhaustive repository write allowlist; `[]` means read-only.
- `BASE_HEAD`: Full Git HEAD object id at launch.
- `BASELINE_MANIFEST`: Repository-relative path to the immutable launch
  manifest.
- `BASELINE_DIGEST`: SHA-256 of the canonical baseline manifest.
- `ACCEPTANCE`: Observable conditions required for completion.
- `VERIFICATION`: Checks or commands expected before completion.
- `EARLY_RETURN`: Permitted decision returns; normally `NEEDS_SCOPE` and
  `NEEDS_RULING`.
- `OUTPUT_PROTOCOL`: Required return protocol; `bridge-report/v1`.

`AUTHORITY` SHOULD point to durable repository sources instead of reproducing
large files. Inline context SHOULD contain only the current ruling, unstable
facts, and small controlling excerpts.

Future gate packets MUST give source line ranges for their citations. Text
labelled `verbatim` MUST be reproduced verbatim; paraphrase, ellipsis, or other
editing MUST be labelled as such rather than presented as a verbatim excerpt.

`ROLE` MUST NOT combine implementation, independent review, and final
adjudication.

Each `WRITE_SCOPE` entry is an object with `path` and `match`. `match` is
`exact`, `subtree`, or `all`; paths are normalized repository-relative paths.
`{"path": "*", "match": "all"}` is the only whole-repository form.

A delegated worker MUST NOT infer additional scope from tests, generated
files, repository instructions, or work believed necessary for completion.

Read-only sessions (`WRITE_SCOPE: []`) MAY omit `BASELINE_MANIFEST` and
`BASELINE_DIGEST`; `BASE_HEAD` remains required.

### Read-only discussion lane

For an interactive MCP turn with `GENRE: discussion` that is read-only, the
required header fields reduce to `TASK_SHAPE`, `GENRE`, `ROLE`, `OBJECTIVE`,
`AUTHORITY`, and `OUTPUT_PROTOCOL`. `WRITE_SCOPE` MAY be omitted and then means
`[]`; `EARLY_RETURN` MAY be omitted and then means `["NEEDS_RULING"]`.

`BASE_HEAD` is REQUIRED whenever the advice depends on repository state,
including code review, diagnosis, or any turn expected to carry a proposal
diff. It MAY be omitted only for repository-independent discussion.
`ACCEPTANCE`, `VERIFICATION`, `BASELINE_MANIFEST`, and `BASELINE_DIGEST` are
omitted in this lane.

The discussion context capsule SHOULD provide section-level authority anchors
rather than bare file paths; current HEAD plus dirty-path and concurrent-writer
state when repository-dependent; and the settled decisions, rejected
alternatives, and remaining challengeable questions.

A same-thread peer-channel continuation MAY use a compact delta prompt. It
inherits `ROLE`, `GENRE`, `AUTHORITY`, and `OUTPUT_PROTOCOL` from the opening
header and states only new rulings and repository changes since the previous
turn. A change of role, authority, scope, or objective class REQUIRES a fresh
full header and usually a fresh thread under §5.

The full header remains mandatory whenever `WRITE_SCOPE` is nonempty or
`TASK_SHAPE` is `autonomous`.

Compact example:

```text
BRIDGE_TASK_V1
{
  "TASK_SHAPE": "bounded",
  "GENRE": "implementation",
  "ROLE": "focused bridge-tool implementer",
  "OBJECTIVE": "Implement lease acquisition and release with focused tests.",
  "AUTHORITY": [
    "docs/contracts/bridge_protocol.md",
    "AGENTS.md",
    "User ruling: overlapping write leases hard-block by default."
  ],
  "WRITE_SCOPE": [
    {"path": "scripts/bridge", "match": "exact"},
    {"path": "tests/test_bridge.py", "match": "exact"}
  ],
  "BASE_HEAD": "0123456789abcdef0123456789abcdef01234567",
  "BASELINE_MANIFEST": ".codex-bridge/baselines/inv-123.json",
  "BASELINE_DIGEST": "sha256:0123456789abcdef",
  "ACCEPTANCE": [
    "Overlapping write leases fail unless a lead override is recorded.",
    "Release and abandoned states are distinguishable."
  ],
  "VERIFICATION": [
    "python3 -m unittest tests.test_bridge"
  ],
  "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
  "OUTPUT_PROTOCOL": "bridge-report/v1"
}
END_BRIDGE_TASK_V1
```

## 2. Return envelope

Protocol layering is intentional: `claude-codex-report/v1` (D-064) remains
the canonical full session report for audited CLI runs made through
`codex-run-v3 --genre`, while `bridge-report/v1` is the lightweight final-lines
envelope REQUIRED for MCP turns and the reverse consult. An audited CLI run
carrying a valid `claude-codex-report/v1` body is exempt from the trailer.

Every successful MCP turn or reverse consult MUST end with exactly two
nonempty lines:

> `BRIDGE_REPORT_V1`
> `{"status":"DONE","summary":"Lease support implemented.","pathspec":["scripts/bridge","tests/test_bridge.py"],"verification":["python3 -m unittest tests.test_bridge: OK"],"flags":[]}`

The first line is the literal sentinel. The second line is one JSON object on
one physical line with these required fields:

- `status`: One status from the enum below.
- `summary`: Concise outcome or blocker summary.
- `pathspec`: Repository paths changed by this worker; `[]` for read-only
  turns.
- `verification`: Checks actually performed and their results, not planned
  checks.
- `flags`: Machine-consumable strings such as `route_cli`, `no_edits`, or
  `verification_incomplete`.

Statuses:

- `DONE`: The requested outcome and acceptance conditions are complete.
- `PARTIAL`: Useful bounded work is complete, but requested work remains.
- `DISCUSSION`: A read-only design or judgment turn completed.
- `NEEDS_SCOPE`: Progress requires additional write authority.
- `NEEDS_RULING`: Progress requires a lead-owned decision.
- `BLOCKED`: An external or technical prerequisite prevents progress and is
  not resolved solely by scope or a design ruling.
- `FAILED`: Execution failed or the worker cannot provide a trustworthy
  result.

The envelope is a protocol failure if its sentinel is absent, duplicated,
malformed, or not final. No non-whitespace content may follow its JSON line.
Interior whitespace on the JSON line is allowed. Unknown additional object
keys are tolerated and ignored for forward compatibility; the five required
fields and the status enum remain mandatory. Normatively, `status` and
`summary` are JSON strings, `summary` is nonempty, and `pathspec`,
`verification`, and `flags` are JSON arrays whose elements are strings.

Malformed or missing envelopes MUST NOT be interpreted as successful
completion, regardless of preceding prose.

For a substantive, multi-issue `GENRE: discussion` turn, the human-readable
body uses this order:

1. `Positions`
2. `Disagreements`
3. `Open questions`
4. `Recommendation`

Sections with no content MAY say `None`. A trivial single-question discussion
MAY answer directly without these headings. The final envelope is always
required.

## 3. Early returns

A worker MUST return early instead of guessing when authority or a lead-owned
decision is missing.

A `NEEDS_SCOPE` body MUST contain:

- `Requested paths`: Exact additional paths and match semantics.
- `Reason`: Why each path is necessary.
- `Completed`: Independent authorized work already completed.
- `Blocked work`: Work that cannot proceed without expansion.

A `NEEDS_RULING` body MUST contain:

- `Question`: One decision the lead must make.
- `Options considered`: Material alternatives and consequences.
- `Recommendation`: The worker's preferred option and reason.
- `Blocked work`: Work awaiting the ruling.

The lead SHOULD continue the same thread after answering either early return.

Scope approval is prospective only. It does not legitimize an earlier
out-of-scope write.

Before resuming with expanded scope, the lead MUST update `WRITE_SCOPE` and
atomically acquire the corresponding workspace lease or use `lease-expand` to
expand it prospectively.

## 4. Task-shape routing

Reasoning effort does not determine transport. Interaction shape does.

| Work shape | Preferred path | Examples |
|---|---|---|
| Interactive | MCP | Discussion, rulings, follow-up questions, short diagnosis |
| Bounded | MCP when short; CLI when evidence-heavy | Focused edit, narrow review, small fix round |
| Autonomous | Audited CLI | Broad audit, long test run, multi-file implementation, subagent work |
| Durable evidence required | Audited CLI | D-050/D-064 run, timeout-sensitive work, mechanically enforced scope |
| Independent review | Fresh MCP or CLI thread | Adversarial lens, final-head review, counterreview |

An xhigh discussion MAY use MCP. A long high-effort mechanical run SHOULD use
CLI.

### T3-mediated presentation, routing, and provenance

T3 is the preferred presentation plane when it is in use. It is neither a
mandatory nor an exclusive bridge plane, and it never becomes the compliance
plane. These t3-specific rules apply only to t3-mediated activity. A plain
Claude Code session remains first-class and carries no t3-specific ceremony.

For a t3-mediated invocation, the tracked provenance record MUST distinguish
four axes: `control_plane`, `transport`, `authority_class`, and `governance`
(implementation follow-on: `T3-PROV-SCHEMA-01` in
`docs/process_traces/2026-08-05-t3-amend/AMENDMENT-MAP.md`).
The selected task-shape route in the table above is the authoritative
transport record. A rollout's `session_meta.originator` MAY be recorded beside
that set only as a provenance hint. It is never the sole discriminator and
never authority-bearing. The observed values `t3code_desktop` and
`codex_cli_rs` are version-bound observations from CLI version `0.146.0`, not
a closed enum or a compatibility promise. Classification authority comes from
the §4 launch route and the lease event's §6 `owner_kind`. Absence of the
optional hint never disables a route or classification. If the hint is present,
an unknown value or a value contradictory to those authoritative fields fails
closed: it does not establish native, wrapped, delegated, top-level, approval,

exec
/bin/zsh -lc "wc -l /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/*/* /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md && sed -n '2043,2105p' RUN_STATE.md && sed -n '2182,2228p' RUN_STATE.md && sed -n '2743,2805p' RUN_STATE.md && sed -n '306,390p' TASK_QUEUE.md && sed -n '50,125p' docs/agent_playbook.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     167 /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md
     543 /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md
     586 /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md
      85 /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md
     242 /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md
     215 /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md
     373 /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md
     382 /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md
    2593 total
## ACTIVE_STOP_CARD

Status: NONE — no stop card is active. Stop-card authority: D-050 / D-063 ([decision log](docs/decision_log.md)).

## Active Global Work-Selection Gates

NONE — no global work-selection gate is active.

## Restart By Machine-State Lane

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05). Latest report: [16h runway checkpoint 2026-08-03: D-108..D-112 minted; kernel pins 60; CAL-BRACKET held at 2e61ff9 (rule-11 gate owed for B1 round 2); winB license exhausted as drawn (r06 disposition parked, WINB-R06-DISPOSITION-01); mint chain D-110-blocked; CLAIMS_STATUS §1 honestly NONE; checkpoint block at the top of RUN_STATE is the successor resume script.](docs/run_reports/2026-08-03-16h-runway.md).

### [ED-EXTERNAL]

- READY — E1 `P1-008`: Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).

### [QUIET-MAC]

- READY — Q2 `P2-006`: Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison.

### [AGENT]

- READY — A0 `P2-035`: RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests).

<!-- END GENERATED: state-kernel run-state-intake -->

## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open

The RESUME list from the 2026-07-17 checkpoint is fully executed. The
relaunched execution-lens review, fix rounds 1-2, and their delta
re-audits had already run earlier on 2026-07-18 (commits `1aebf14`,
`6d80039`); this session closed the surviving P1 (child accepted any
JSON object as the frozen cooldown anchor) plus every finding from four
further delta re-audits, as fix rounds 3-8 in commit `ad0920b`:
canonical anchor validator (`joulewise/cooldown_anchor.py`) enforced
fail-closed at parent/CLI/controller boundaries; collision-safe,
crash-atomic, flock-serialized rejection-verdict custody
(`experiments/rejections/`); physical-domain baseline validation (the
`inf`-anchor fail-open gate is closed); discriminating process-race
regression. Suite green lead-side at every round boundary, final
`Ran 1746 tests`, `OK (skipped=12)`. Awake-half live probe validation
passed on real hardware (zero probe errors); the Ventura screensaver is
now disabled on the machine (`idleTime = 0`). PR #77 carries the gate
narrative; merge is Ed's call. Full record:
`docs/run_reports/2026-07-18-d077-fix-rounds.md`. Tooling: codex-run-v3
xhigh review-genre sessions ended with null final messages 4x
(bridge-resume recovered each; personal-tooling defect, recorded in the
run report and the global codex-delegation skill field notes, not the
repo queue).

## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task

The actual Claude Code fallback route is `scripts/codex-bridge`, not the MCP
server for recent audited work. The wrapper now sends `new` and `review` turns
through a dedicated app-owned Codex desktop task when the local host id is
configured. This is the same local-conversation state the native pet consumes;
the prior observer-only diagnosis was incorrect because the pet never reads
`~/.codex/claude-spawned/index.jsonl`. A live Sol/high smoke appeared in the
Codex app as thread `019f77a6-3612-7332-9f5e-be9fbde56be5`, turn
`019f77a9-2827-7de1-accf-ac2eda21927e`, and returned
`JOULEWISE_NATIVE_PET_BRIDGE_OK` through the script. Adaptive effort remains
unchanged: `high` fallback/default, `xhigh` only on named hard-task triggers,
and `ultra` only for sessions that must spawn subagents. Full record:
## Current Project Status

**Mint era OPEN AND FIRST MINT LANDED (2026-07-30): main `da83337`. The
data exists and passes, and the code path that turns it into a published
floor now exists and has been exercised — `df-ph-decode-floor-mint1` is
mainline.**

### The central measurement fact (read before any measurement decision)

The instrument is **attribution-limited (~1 J), not noise-limited
(~0.3 J)** — D-078 clause 11, Ed-ratified. Floors publish LABELLED with
the widened number; the point floor is a repeatability diagnostic that
may never be the published claim floor. The anchor term appears in
**both** the floor and each claim's decision interval, so the effective
clearable effect is floor + claim-side bound ≈ 5 J for phase contrasts,
and neither term may later be deleted as an apparent double count. Do
not launch an instrument-tightening program; it was measured and
eliminated.

### Collection state

| Window | Contents | Verdict | Notes |
|---|---|---|---|
| a9, a10 | earlier corpora | **PASSED** | a10 supplies the absolute component |
| **B** (`04_phase_prefill_abba`) | 40 prefill ABBA members, 59/59 collected clean | **FAILED** | `instrument_calibration_mismatch`, bracket drift 11.581436 ms; preserved, not claim-bearing |
| **C** (`05_phase_decode_abba`) | 40 decode ABBA members, 59/59 collected | **PASSED** | bracket drift 1.279 ms; first comparative window in project history to pass |
| **D** (absolute) | 30 claim members, 49/49 collected | **PASSED** | bracket drift 0.484 ms, tightest of the campaign |
| **7B floor** (`window_7bfloor_20260729`) | Qwen2.5 7B decode floor, collected 2026-07-29 | **PASSED** | CLAIM-BEARING; governed extraction clean (`all_cells_extractable` true). Floors: absolute 6.294380135190098 J, comparative 13.998036715259254 J; absolute-cell member mean 192.38623252628366 J (n=10). NOT yet minted — `MINT-GENERALIZE-01` is OPEN and unblocked as of 2026-08-02 (gauntlet closed PR #93; D-088 no-mint condition lifted), so these figures live only in prose plus the out-of-repo custody extraction until that mint runs |
| **contrast** (`window_contrast_20260730`) | 40 contrast ABBA members + 7 references, 47 bundles, 1 supersession | **PASSED** | bracket drift 1.281 ms; contrast diagnostic 146.730349 J σ 0.241 (n=10 blocks) UNGATED — MANIFEST-CONTRAST-01 closed 2026-08-02 (PR #95); the gated claim now rides `MINT-GENERALIZE-01` then the D-095 chain |

Window B's cause is established and is NOT a clock problem: a GPU DVFM
power ramp that the rectangular-pulse fiducial estimator aliases into an
apparent onset shift (93.28% of the drift; the wall-clock term moved the
OPPOSITE way, −0.201464 ms). D-079 clause 3 adds a pre-flight screen that
detects it in the ~4-minute pre-calibration, with cause-removal (never
outcome-selection) retry semantics.

**Corrected floor figures — the old ones must not be repeated.** a10's
**absolute** floors are **3.823787 J prefill / 3.592138 J decode**,
INCLUDING the 0.652272 J whole-window drift allowance. The 3.17 / 2.94 J
numbers circulated earlier are the attribution-width floors BEFORE the
allowance and are diagnostics only (D-079 clause 5).

**AMENDED BY D-084 (2026-07-29): `3.592138` is the ABSOLUTE COMPONENT IN
ISOLATION, not the operative decode floor.** Mint #1's cell composes
a10's absolute 3.592138 J with window C's comparative 7.377086 J, and
under W3 rule 8 the cell gate is the **max, never the sum** — so the
## Known Workspace State

- (2026-08-02, CURRENT) `main` and `origin/main` at `bcbc10b`; working
  tree clean except the untracked private `CLAUDE.local.md` (Ed's;
  never commit) and `.desk/` (adjudication custody; never commit).
  PR #93 merged (the c3 branch is closed). Branch
  `impl/d100-bii-binding` exists in the session worktree
  `scratchpad/d100bii` holding the UNCOMMITTED, audit-pending
  D100-BII-BINDING-01 diff (envelope protocol failure; see §9).
- (2026-07-31, historical) `main` and `origin/main` were both at `6ed1625`:
  the PR #89 merge `7ee680c` (D5-J) plus the close-out commits
  `49c1876`, `0d0bd0b`, and `6ed1625`. Branch `impl/mint-tool` is MERGED
  (verified `git merge-base --is-ancestor impl/mint-tool main`), as are
  `impl/floor-mint` and `impl/floor-label-clean`; all three may be
  deleted. Their scratchpad worktrees are still registered (`minttool`
  plus ~11 review/pin worktrees under the `9c166892…` session dir, and
  prunable entries under `ad48bfae…` and `d714f367…`) — `git worktree
  prune` plus explicit removal is owed as housekeeping. The working tree
  is clean except for the untracked private `CLAUDE.local.md` (Ed's
  file; never commit it).
- (2026-07-28 late, historical) `main` and `origin/main` were at that
  session's bookkeeping commit atop the PR #87 merge `058c918`. Branch
  `impl/mint-tool` (pushed, then UNMERGED) held the 9-commit mint series
  `2a0ecbc..697f741` in worktree
  `/private/tmp/claude-501/-Users-edr-code-JouleWise/9c166892-d763-42c4-8cf7-383912f054c9/scratchpad/minttool`;
  canonical suite at its head `1d83d68` is UNVERIFIED (rerun was in
  flight at checkpoint). Branch `impl/floor-mint` is merged via PR #87
  and may be deleted. NOTE: a concurrent session force-rewrote main
  history this evening (content preserved; see run report Anomalies) —
  verify `git log` freshness before building on a cached head.
- (2026-07-27, historical) `main` and `origin/main` were at `7337b33`. Branch
  `impl/floor-mint` @ `617060a` is pushed and NOT merged; it carries the
  pre-mint floor schema hardening. Window C (+bound) and a10 (+bound)
  remain FULLY resident in the working tree (mint #1 inputs); windows B/D
  and all other runs corpora are locally pruned to small evidence files
  (traces archived + verified in iCloud, see "Disk" above), and custody
  material lives OUTSIDE the repo at `~/JouleWise-window-custody/` — an
  agent searching only the repo will wrongly report quarantined evidence
  missing. Disk has 115 GB free; a window writes ~6 GB. The next quiet-window operator must start
  from a separate clean, merged-main measurement checkout per
  `docs/phase_2/window_runbook.md`.
- The generated state-kernel regions in this file and `TASK_QUEUE.md` are
  IN SYNC with `docs/process/state_kernel.json`
  (`python3 scripts/gen_state.py --check` exits 0), and the kernel's own
  content was refreshed on 2026-08-01 (desk adjudication session):
  stamped `updated: 2026-08-01`, `latest_report` points at
  `docs/run_reports/2026-08-01-desk-adjudication-session.md`, the MET
  rows are folded in, the completed
  `FLOOR-LABEL-01`, `STACK-ID-BIND-01`, `P2-015`, and
  `COOLDOWN-JOIN-DA1-01` rows are retired to
  `TASK_QUEUE.md`'s completed table, and the post-mint intake
  (`COOLDOWN-JOIN-GAUNTLET-01`, `MINT-GENERALIZE-01`,
  `MANIFEST-CONTRAST-01`, `SUPERSESSION-DUP-REFUSAL-01`,
  `QA-10A-JOIN-OMISSION`, `QA-10B-EXISTING-RETRY`) is folded in. Any
  further change means editing the kernel and then running
  `python3 scripts/gen_state.py` — never hand-editing the generated
  regions.
- (2026-07-25, historical) `main` and `origin/main` were at `c3e2647`,
  the PR #85 merge; PR #79's repair and PR #85's SCREEN+BUDGET
  implementation both landed with green final PR-head CI.
- The generated state-kernel blocks are authoritative for work selection.
  Hand-authored `RUN_STATE.md` and `TASK_QUEUE.md` text remains authoritative
  only for its own factual, policy, and historical domains;
## Current Queue

The generated region below is the sole live queue and source of truth for
work selection. Edit the kernel and regenerate; do not hand-edit its rows.

Superseded (2026-07-15, WO-012; D-043): Q4/P2-019 sample size is frozen in the hash-bound analysis registry before outcomes, and outcome-dependent growth permanently demotes the contrast to exploratory; see `docs/contracts/analysis_plans.md` §Required fields.

Superseded (2026-07-15, WO-017; D-043): P2-027 publication and uninvolved-party re-reduction are optional owner-directed evidence-handoff work, not the default reproducibility or project-completion gate; see `docs/specs/c027/rpt-001_report_vertical_slice.md` §0.4 and `docs/contracts/publication_privacy.md` §Publication boundary.

<!-- BEGIN GENERATED: state-kernel current-queue -->
<!-- GENERATED from docs/process/state_kernel.json by scripts/gen_state.py. Do NOT hand-edit between the markers; edit the kernel and regenerate. -->

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05).

Generated compatibility table for repository consumers; the lane tables below are the detailed view of the same kernel state.

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| E1 | P1-008 | P1 Phase Gate | READY [ED-EXTERNAL] | Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability). | Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: [Milestones + R-012](docs/milestones.md). Acceptance: [P1-008 acceptance](docs/process/state_kernel.json). Note: R-012 is the biggest active management risk for an undergrad timeline. |
| E2 | P2-027 | P2 Next Slice | READY [ED-EXTERNAL] | Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party. | Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: [C-020 + C-027 NEG-9](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-027 acceptance](docs/process/state_kernel.json). Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL. |
| E3 | P1-001 | P1 Phase Gate | READY [ED-EXTERNAL] | Capture supervisor approval and scope notes. | Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: [R-001](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped. |
| E4 | P1-003 | P1 Phase Gate | READY [ED-EXTERNAL] | Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method. | Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: [D-018/C-003](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Elevated value: gates Q6 boundary sensitivity (C-003). |
| E5 | P1-004 | P1 Phase Gate | READY [ED-EXTERNAL] | Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method. | Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: [R-011](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Partial. |
| E6 | P1-006 | P1 Phase Gate | READY [ED-EXTERNAL] | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |
| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) [QUIET-MAC] | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
| Q2 | P2-006 | P2 Next Slice | READY [QUIET-MAC] | Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison. | Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: [Phase 2 plan + analysis plans](docs/phase_2/phase_2_plan.md). Acceptance: [Phase 2 exit checklist](docs/phase_2/phase_2_exit_checklist.md). Note: Software interpretation gates are satisfied; Window-A floors landed 2026-07-31 (mint #1 mainline), so only the campaign remains. |
| Q3 | P2-010 | P2 Next Slice | READY [QUIET-MAC] | P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail. | joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: [AP-5 + affine stream log](docs/contracts/analysis_plans.md). Acceptance: [P2-010 acceptance](docs/process/state_kernel.json). Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains. |
| Q4 | P2-019 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6). | Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: [AP-1](docs/contracts/analysis_plans.md). Acceptance: [P2-019 acceptance](docs/process/state_kernel.json). |
| Q5 | P2-020 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts. | Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: [AP-6 + D-046](docs/contracts/analysis_plans.md). Acceptance: [P2-020 acceptance](docs/process/state_kernel.json). Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6). |
| Q6 | P2-012 | P2 Next Slice | BLOCKED — P2-006 (identification-core runs after Window A) [QUIET-MAC] | Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases. | Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: [AP-4 + D-039/D-040](docs/contracts/analysis_plans.md). Acceptance: [P2-012 acceptance](docs/process/state_kernel.json). Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27). |
| Q8 | P2-046B | P1 Phase Gate | READY [QUIET-MAC] | Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts. | Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: [Hardening adjudication C6](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-046B acceptance](docs/process/state_kernel.json). Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution. |
| Q9 | P2-047B | P2 Next Slice | BLOCKED — P2-047A (frozen controller-overhead harness exists) [QUIET-MAC] | Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict. | Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047B acceptance](docs/process/state_kernel.json). |
| A0 | P2-035 | P3 Research Expansion | READY [AGENT] | RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests). | Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: [RQ-ENERGY-VARIANCE candidate design](docs/specs/rq_energy_variance_design.md). Acceptance: [P2-035 acceptance](docs/process/state_kernel.json). Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine). |
| A2 | QUIET-GUARD-01 | P1 Phase Gate | READY; GATES live_promotion: T3-CHAR-PAIR-01 [AGENT] | Quiet-guard work order (full gauntlet): host-wide quiet lease, refuse-at-arm, characterized resident watcher; plus Ed requirements recorded 2026-08-03 — t3-armed operation (a t3-launched claude session arms a detached guarded chain, then self-quits and quits t3 with a survivor inventory), t3-relaunch-on-close, and README-banner signaling. | The quiet guard lands through the full C-028 gauntlet with the host-wide lease, refuse-at-arm, characterized resident watcher, and all three Ed-required t3 behaviors working end to end. Evidence: Commit 1 only: host-wide quiet lease implemented and enforced; Refuse-at-arm: arming refuses when the host is not quiet (usable by the ordinary guarded-shell window launcher); Installed-INACTIVE: no arming path, no production lease, live_promotion=false; Seven focused-audit blockers closed (priv-esc interpreter, validate/install TOCTOU, arbitrary-root initializer, macOS process identity, boot/hostname wedge, decision entry, independently-pinned tests); Full gauntlet on the landed commit: independent audit + delta re-audit of every fix round. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [QUIET-GUARD-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). ROW RE-SCOPED TO COMMIT 1 ONLY: the host-wide quiet lease + process census, installed-INACTIVE. Retained because it has non-t3 value — mechanical refuse-at-arm for the ordinary guarded window launcher, replacing procedural eyeballing. SHELVED: commit 2 (launcher interception), commit 3 (t3 handoff + resident watcher), commit 4 (t3-relaunch + README banner projection + all credential handling). In flight at checkpoint: Sol fix round closing 7 audit blockers; work UNCOMMITTED in scratchpad/quietguard (branch impl/quiet-guard); harvest scratchpad/qg-fix-out.md. |
| A3 | FLOOR-BIND-01 | P1 Phase Gate | READY [AGENT] | Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions. | Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: [D-078 clause 8 (confirmation round 9, registered limitation L1)](docs/decision_log.md). Acceptance: [FLOOR-BIND-01 acceptance](docs/process/state_kernel.json). Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed. |
| A4 | AXI-SB-ADAPTER | P2 Next Slice | READY [AGENT] | Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims. | The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: [AXI-SB verdict document (supported; mint-on-supported follow-on)](docs/specs/axi/sb_static_batch_verdict.md). Acceptance: [AXI-SB-ADAPTER acceptance](docs/process/state_kernel.json). Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership). |
| A5 | TEST-SPEED-01 | P2 Next Slice | READY [AGENT] | Cut suite wall-clock (three Ed-ratified levers, 2026-08-03): collect per-module timing data with the recovered profiling scripts, implement the shard-runner and the PR-fast/full tier split from the data, and evaluate Blacksmith runners. | The three Ed-ratified levers land: timing data drives a shard-runner plus PR-fast/full split with the full suite still holding every authoritative gate, and the Blacksmith runner option is evaluated on evidence. Evidence: Per-module timing corpus collected on a quiet bench (the recovered Sol profiling scripts; timings.jsonl + summary.json banked under .desk/) identifying the slow tail by module and by test; Shard-runner and the ratified PR-fast/full tier split implemented from the data: the fast tier gates PRs, the FULL suite remains the gate for merges, verdicts, and audited heads; zero test deletions; Blacksmith runner evaluation recorded with an adopt/defer recommendation and measured latency/cost comparison against GitHub-hosted runners. Authority: [Ed ratification 2026-08-03 (three levers: suite-speed priority, PR-fast/full split, Blacksmith runner evaluation); origin row in the 2026-07-28 report](docs/run_reports/2026-07-28-floor-mint-implementation.md). Acceptance: [TEST-SPEED-01 acceptance](docs/process/state_kernel.json). Fence: No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite (D-061 zero-deletion clearance; the full suite as the authoritative gate). Note: 2026-08-03: timing DATA collected (quiet bench, 93 modules, 695s serial; raw in .desk/test-speed-consult/timings-20260803.jsonl) and DESIGN done (.desk/test-speed-consult/DESIGN-from-timing-data.md). Findings: suite is a 2-module problem (run_campaign 182s + p2038 133s = 45%); module-atomic sharding CAPS at 182s so those two must be split by TestCase class; shard-runner + splits -> ~87s wall @8 workers (6.5x); fast tier (drop 11 heavy integ modules) -> 25-40s PR feedback with the full suite still the merge gate. Blacksmith (lever 3) NEEDS ED (account/cost; likely marginal once sharded). Implementation queued: scripts/shard_tests.py + class-split + CI matrix — mechanical, delegatable, zero deletions (D-061). 2026-08-04: PHASE 1 LANDED — PR #98 MERGED (9b02539): module-atomic shard-runner + 8-way CI shard matrix, main CI green under it (~15min -> ~6min proven); worktree/branch pruned. Remaining scope: class-split of the two heavy modules (Phase 2), fast PR tier (lever 2), Blacksmith runners (lever 3, NEEDS ED). |
| A6 | AXI-SD | P2 Next Slice | READY [AGENT] | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
| A7 | AXI-SE | P2 Next Slice | READY [AGENT] | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
| A10 | SUPERSESSION-DUP-REFUSAL-01 | P1 Phase Gate | READY [AGENT] | Rule on and then implement write-time refusal in the supersession recorder, which today appends silent duplicate records when run more than once for a member and voids campaign membership downstream; the ruling is the first half of the deliverable. | A repeat recorder invocation for the same member refuses instead of appending a duplicate record. Evidence: The write-time refusal ruling is recorded in the decision log before any implementation; A regression asserts that a second recorder invocation for the same member refuses. Authority: [D-086 supersession-aware cooldown-evidence join (recorder duplicate-append defect)](docs/decision_log.md). Acceptance: [SUPERSESSION-DUP-REFUSAL-01 acceptance](docs/process/state_kernel.json). Fence: Until the refusal lands, run the supersession recorder exactly once per member (D-086 operator mitigation). Note: Minted 2026-07-30 from the D-086 arc; ruling-first, no implementation before it. |
| A11 | T3-PROV-SCHEMA-01 | P2 Next Slice | READY [AGENT] | Implement the tracked four-axis provenance record with authority_class and the ingestion-event schema, then make reverse-consult admission consume authoritative launch-route and owner_kind evidence so bridge §8's transitional convention ends. | The four-axis provenance plus ingestion-event schema ends bridge §8's transitional convention by mechanically enforcing reverse-consult eligibility from authoritative route and ownership evidence. Evidence: A tracked provenance record represents the four axes control_plane, transport, authority_class, and governance, with authority_class explicit; A tracked ingestion-event schema binds native session identity, output digest, lead disposition, and tracked process-trace location; Reverse-consult admission consumes authoritative launch-route and owner_kind evidence rather than self-reported headers; Rejection regressions fail closed on delegated, unknown, or contradictory provenance and prove that merely persisting the schema cannot end the transition. Authority: [Bridge protocol §8 transitional reverse-consult enforcement follow-on](docs/contracts/bridge_protocol.md). Acceptance: [T3-PROV-SCHEMA-01 acceptance](docs/process/state_kernel.json). Fence: The transition ends only when admission consumes authoritative launch-route and owner_kind evidence with rejection tests; defining or persisting the schema alone is insufficient (Bridge protocol §8 fail-closed transition rule). Note: Bridge §8 currently validates only self-reported headers; consumption-side fail-closed is the actual protection until this row supplies real enforcement. |
| A12 | MINT-GENERALIZE-01 | P1 Phase Gate | BLOCKED — D-110 (The remaining D-110 re-mint conditions hold before ANY further mint, including the governed 7B mint: (b) the acceptance artifact is ISSUED after verified R2 backfill and deterministic ledger bootstrap; (c) the evidence_root_id validator pin is widened) [AGENT] | Generalize the mint beyond the mint-1 pair: scripts/mint_floor_artifact.py is hard-pinned to the p2_015, a10, and window-C evidence (cell id, plan sha, both order-manifest ids, the two member counts, the expected operative-floor text), so build a sibling taking those pins per plan and carrying the 7B mint's remaining scope. | A generalized mint sibling takes the mint-1 hard pins per plan so a second floor artifact can be minted without weakening the pre-registration gate. Evidence: A 7B decode-floor artifact mints from qwen25_7b_decode_floor_v1 evidence with its own hard six-decimal operative-floor literal supplied per plan, never derived inside the mint path; The pre-registration gate passes as-embedded and validate_floor_artifact returns no findings; The generalized path mints byte-identical to the reviewed core from the same inputs on the same integration tree (core-vs-wrapper parity per D-109 addendum II; NOT a match against historical mint-1 digests, which D-110's corrected re-mint may legitimately change). Authority: [splitwise_decode_v1 campaign doc section 2 Blocker A (mint pins); D-082, D-084, D-085 Q6](docs/phase_2/splitwise_decode_campaign.md). Acceptance: [MINT-GENERALIZE-01 acceptance](docs/process/state_kernel.json). Fence: Generalize the plumbing, never the pins: six-decimal floor literals and lead-verified digests stay supplied per plan and hard-checked in-tool (D-082 and D-084 operative-floor pins). Note: 2026-08-03: D-110 (sweep finding RT-1/RT-2): mint #1 is retroactively NON-CLAIM-BEARING (taint-and-remint); the night consult's conditional 7B-mint license is SUSPENDED. The mint-1 byte-compare replay completed BYTE-IDENTICAL at pinned 3de370ec (all four digests; docs/process_traces/2026-08-03-q1-remint-bytecompare/). 2026-08-05: condition (a) is satisfied by merged PR #100. Condition (b) preparation is complete and its verification blocker is resolved: the B1 disposition is lead-ruled 30/2/6 and deterministic bootstrap is implemented on impl/ledger-bootstrap, under audit. Condition (c) is in flight on impl/validator-rootpins. The row remains hard-blocked on the still-pending D-110 (b)+(c) completion gate. |
| A13 | CODEX-BRIDGE-SANDBOX-01 | P2 Next Slice | READY [AGENT] | Correct scripts/codex-bridge review-mode sandbox enforcement: pass the read-only sandbox flag instead of launching workspace-write while recording read-only metadata. | codex-bridge review launches read-only exactly as its audit manifest claims, with regression coverage binding recorded and effective sandbox values. Evidence: scripts/codex-bridge review passes the read-only sandbox flag to every non-app review launch; The review audit manifest records the sandbox actually supplied to the launch; A regression proves the recorded review sandbox and launched sandbox are both read-only and cannot drift apart. Authority: [2026-08-05 live inspection: review records observer_sandbox=read-only but the non-app launch omits -s read-only](scripts/codex-bridge). Acceptance: [CODEX-BRIDGE-SANDBOX-01 acceptance](docs/process/state_kernel.json). Note: Caught live 2026-08-05: observer_sandbox is set to read-only, but the non-app review invocation omits the sandbox flag, so audit metadata misstates enforcement. |
| A14 | COLDGATE-HANDOFF-01 | P2 Next Slice | READY [AGENT] | Build runner-owned sealed-byte judge handoff: capture immutable in-process packet, charter, and exhibit byte snapshots; compute digests over those exact buffers; construct judge input from the same buffers; and specify and test transport byte-to-request binding. | The convening runner delivers exactly the bytes the validator observed, with immutable snapshot-to-judge transport binding and a judge-identity-bound runner receipt. Evidence: Deterministic post-hash path replacement delivers the original immutable snapshot or refuses without invoking the judge; Same-inode mutation through a second descriptor never delivers mutated bytes under the old receipt; Judge-received payload hashes equal the receipt hashes and the runner receipt binds the judge request or session identity. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 handoff ruling and tests](docs/process_traces/2026-08-05-cgv-f3-consult/CONSULT-REPORT.md). Acceptance: [COLDGATE-HANDOFF-01 acceptance](docs/process/state_kernel.json). Fence: Until this row lands, no validator PASS may be used to convene a cold judge (2026-08-05 F3 consult standing operational constraint). Note: Design warnings: holding file descriptors open does NOT seal bytes because a second descriptor can mutate the same inode; path-based launch-time revalidation alone leaves a revalidate-to-read race. Pending-ratification payload carried by this row: the proposed amendment to docs/process/coldgate_charter_registry.md separating validator observation from runner custody. The registry is Ed-ratified and is NOT edited by this or any session without a cold-gate/Ed ratification. |
| A15 | C3-RECOGNIZER-EXACT-01 | P1 Phase Gate | READY [AGENT] | Close the two D-105-registered recognizer-exactness blockers: exact escape-ordering completion-feasibility (F1) and the documented decidable superset number grammar (F2, with the D-104 cl.2 subset-direction amendment), plus the bundled F3/N2 release-path hygiene if not already landed. | The two registered recognizer-exactness blockers (escaped-key ordering; number-prefix over-acceptance) close together under D-105's refuter-amended criteria with an independent audit. Evidence: F1 closes via the exact escape-ordering completion-feasibility procedure (hex-digit interval derivation, surrogate-pair arithmetic, prefix-extension rule) with both registered counterexamples pinned verbatim and a BMP/non-BMP boundary property test; F2 closes via a DOCUMENTED DECIDABLE SUPERSET grammar of json.dumps float spellings (fixed-notation exponent window, coefficient rules, two-digit exponent padding) — the D-104 cl.2 subset direction is amended per D-105 to 'accepted within the documented superset AND containing every real writer prefix'; both counterexamples refuse; randomized-float completeness property passes; Both registered blockers close together with an independent delta audit at the exact head; the acceptance-set contract re-proven in both amended directions over a corpus including non-BMP keys. Authority: [D-105 disposition synthesis (F1/F2 registered as a NEW ruling, not D-088 precedent; closure criteria refuter-amended; number-grammar exactness struck)](docs/decision_log.md). Acceptance: [C3-RECOGNIZER-EXACT-01 acceptance](docs/process/state_kernel.json). Fence: F1/F2 severity may not be downgraded by any role; closure ONLY through this row; while open the recognizer's accepted set may only SHRINK; the custody sidecar and writer-side ASCII key assertion (the D-105 micro-commit) are load-bearing compensating controls and may not be weakened (D-105 registration fences). Fence: This registration must not be cited as precedent for registering corpus-absent defects generally; it is a new ruling made with three recorded independent absence scans and mechanical compensating controls (D-105: branch-introduced registration is NOT QA-10A/B precedent). |
| A16 | P3-000 | P3 Research Expansion | BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) [AGENT] | KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8). | Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: [D-035/D-036](docs/decision_log.md). Acceptance: [Phase 3 exit checklist](docs/phase_3/phase_3_exit_checklist.md). Note: 3.0.1 complete and merged (PR #9, replay_supported). |
| A17 | P2-022 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) [AGENT] | Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported). | 3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [Adapter contract](docs/contracts/adapter_contracts.md). Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission. |
| A18 | P2-023 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) [AGENT] | HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy. | Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [RQ bank import-smoke design](docs/research_question_bank.md). Fence: No pass@k, accuracy, or capability claim (D-041). |
| A19 | P2-024 | P2 Next Slice | BLOCKED — P2-006 (2M reductions identify floor/MDE headroom) [AGENT] | Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC]. | Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: [C-015 + RQ bank](docs/research_question_bank.md). Acceptance: [P2-024 acceptance](docs/process/state_kernel.json). |
| A21 | P3-001b | P3 Research Expansion | BLOCKED — P2-006 (2M affine coefficients exist) [AGENT] | Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049). | AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: [D-048/D-049](docs/decision_log.md). Acceptance: [Analysis plans (split row)](docs/contracts/analysis_plans.md). |
| A22 | P2-004 | P2 Next Slice | PARTIAL; READY; GATES close: P1-001 [AGENT] | Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding. | Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: [D-016](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Provisional small-model pick 2026-07-06 opens 2G. |
| A23 | P2-005 | P2 Next Slice | PARTIAL; READY; GATES live_promotion: P1-006 [AGENT] | Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute. | Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: [NV-GATE-2 live-promotion spec](docs/specs/c027/nv-gate-2_live_promotion.md). Acceptance: [2K live verification checklist](docs/phase_1/2k_live_verification_checklist.md). Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open. |
| A24 | P2-016 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists) [AGENT] | Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment. | Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: [C-011 ledger + C-027 (post-2M umbrella)](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-016 acceptance](docs/process/state_kernel.json). Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake. |
| A25 | P2-047A | P2 Next Slice | READY [AGENT] | Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes. | A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047A acceptance](docs/process/state_kernel.json). Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7). |
| A29 | DOC-008-REFLECTION | P4 Polish | READY [AGENT] | Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6. | Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence). |
| A30 | DOC-008-STATUS | P4 Polish | READY [AGENT] | Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8. | Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence). |
| A31 | DOC-008-INTAKE | P4 Polish | READY [AGENT] | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
| A32 | DOC-008 | P4 Polish | PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS [AGENT] | Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked. | Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: [DOC-008 state-kernel specification](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 required outcomes](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live. |
| A33 | P2-050 | P3 Hardening Candidates | READY [AGENT] | Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2. | Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives its own adjudication; Semantic cooldown-row verification receives its own adjudication; Once-per-manifest first-run exemption receives its own adjudication; Scoped top-up detection and cooldown trace v2 receive their own adjudications. Authority: [C-028 dissent-record queue candidates](docs/run_reports/2026-07-11-c028-continuation.md). Acceptance: [P2-050 acceptance](docs/process/state_kernel.json). Fence: Do not implement any candidate before its own recorded adjudication (C-028 dissent-record queue candidates). |
| A34 | TOOL-01 | P3 Tooling | READY [AGENT] | Fix codex-run-v3 defects: resume-after-NEEDS_SCOPE no-op; preventive permission profiles; NEEDS_RULING recognition; effort-default passthrough; stream-death OK exits with thin out-files; resume --last cross-thread attachment through the global latest session; and session-open paths lacking per-path match specifiers. | All seven codex-run-v3 defects close in lead personal tooling with targeted regressions and updated adapter operations lessons. Evidence: Resume after NEEDS_SCOPE continues the requested work; Preventive permission profiles and NEEDS_RULING recognition are covered; Omitted effort defaults to xhigh instead of config passthrough; Upstream stream death fails instead of exiting OK with a thin out-file; Resume requires an explicit session ID and cannot cross-attach through a global --last pointer; Session-open accepts a per-path match specifier without post-hoc child expansion. Authority: [Bridge v1.1 wrapper and session operations record](docs/run_reports/2026-07-13-bridge-v11.md). Acceptance: [TOOL-01 acceptance](docs/process/state_kernel.json). Fence: Keep implementation in lead personal tooling; this repository owns only the work record (Bridge v1.1 wrapper and session operations record). Note: lead personal tooling, non-repo |
| A35 | AUD-FOLLOWUPS | P3 Hardening Candidates | READY [AGENT] | Close the ULTRA comparison audit's accepted small residue in one bounded agent task: WO-012's owned D-062 lint queue row, WO-014 realized-token discrimination, WO-017 default no-handoff regression, WO-020 standalone bridge-checker decision, and WO-040 authored-instruction absolute-path plus genuine pristine-clone coverage. | The ULTRA comparison audit's five accepted small follow-ups close with discriminating tests or an explicit recorded decision, without creating a ceremony-dispositions task. Evidence: WO-012's owned D-062 lint queue-row obligation is implemented and covered; WO-014 has a realized-token discriminating test; WO-017 has a default no-handoff regression assertion; WO-020 has a recorded standalone bridge-checker decision; WO-040 has authored-instruction absolute-path coverage plus a genuine pristine-clone test. Authority: [Comprehensive-audit close-out and accepted-residue list](docs/reviews/2026-07-13-comprehensive-audit/report.md). Acceptance: [AUD-FOLLOWUPS acceptance](docs/process/state_kernel.json). Fence: Do not create AUD-CEREMONY-DISPOSITIONS; ceremony dispositions remain report-owned (Comprehensive-audit report disposition ledger). Note: Accepted small residue only; audit ceremony dispositions remain in the report. |
| A36 | AUD-WO-033 | P3 Hardening Candidates | READY; GATES close: P2-006 [AGENT] | After 2M, split scripts/run_campaign.py along tested policy seams, pure validation and provenance first and execution lifecycle second, only when campaign-scale or split or multi-node work first forces edits to that path. | The post-2M campaign-runner refactor is behavior-preserving across the full campaign test portfolio and retains every collection and claim-readiness safeguard. Evidence: Pure validation and provenance seams are extracted before execution lifecycle seams; The full campaign behavior-parity portfolio is green before and after the split; Locks, waivers, backups, cooldown, and claim-readiness behavior remain unchanged. Authority: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Keep this post-2M and behavior-preserving; do not redesign campaigns or weaken locks, waivers, backups, cooldown, or claim-readiness gates (Comprehensive-audit register WO-033 non-goals and risk note). |
| A37 | AUD-WO-034 | P3 Hardening Candidates | READY; GATES close: PHASE-3-SPLIT-SCHEDULED [AGENT] | At Phase-3 split scheduling, assign bounded owners and dependencies for transfer-bench, split replay, composite validate and reduce, KV-economics reduction, and matrix-generator extension before any PLANNED command becomes executable. | When Phase-3 split work is scheduled, every PLANNED pack command gains an owner or explicit deferred marker without pack collapse or premature implementation. Evidence: Every PLANNED command has a bounded owner row or explicit deferred-design marker; Pack-command ownership lint passes positive and negative fixtures; Settled split pre-registration requirements and offline-before-live fences remain intact. Authority: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not prune draft designs, collapse campaign packs, or implement split or KV work in this ownership pass (Comprehensive-audit register WO-034 non-goals). |
| A38 | AUD-WO-035 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-TRANSFER-SCHEDULED [AGENT] | Before the first 2K-live or remote split-transfer task, define a versioned discriminated node-worker payload and test realistic typed rejection without overloading telemetry blocks. | The 2K-live and remote roadmap has a versioned transfer-task payload seam with typed rejection before split-transfer implementation. Evidence: A versioned discriminated payload path exists for transfer tasks; A realistic unsupported transfer request fails with a typed versioned error; Telemetry blocks are not overloaded with transfer semantics. Authority: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Define and reject the future transfer shape only; do not implement split execution or transfer benchmarking (Comprehensive-audit register WO-035 non-goals). Note: D-043 supersession closure falls due at landing: add the dated protocol-version supersession line identified by PA-2. |
| A39 | AUD-WO-036 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-CONCURRENCY-SCHEDULED [AGENT] | When 2K-live or remote retries or concurrency are introduced, add a pre-launch node and GPU ownership lease plus idempotent duplicate prepare and start behavior. | Retries or concurrent 2K-live and remote campaigns cannot double-own a node or GPU and duplicate delivery is idempotent. Evidence: Duplicate prepare and start delivery is idempotent; Node and GPU ownership is leased before launch; Concurrency coverage exercises the ownership and duplicate-delivery contract. Authority: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not run concurrent hardware campaigns or make live-correctness claims in this agent task (Comprehensive-audit register WO-036 non-goals). |
| A40 | AUD-WO-037 | P3 Hardening Candidates | READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED [AGENT] | Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path. | Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2. |
| A41 | AUD-WO-038 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED [AGENT] | At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition. | At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2. |
| A42 | AUD-WO-039 | P3 Hardening Candidates | PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED [AGENT] | At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review. | The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2. |
| A43 | CUSTODY-HARDEN-01 | P2 Next Slice | READY [AGENT] | Custody hardening follow-on from the screen+budget gauntlet: reduce-layer label-trust removal (G2A), drift-bound seal authentication (A3-r2), dead no-freshness accommodation disposition, artifact_schema_invalid mislabel. | Close the PR #85 gauntlet's deferred custody-hardening seams: config-derived mockness reaches the reduce-layer barriers, the drift-bound seal stops being self-certifying, and two diagnostic nits are resolved. Evidence: Reduce-layer environment/CPU claim barriers derive mockness from the custody-bound config, with metadata/summary-label early returns removed; Drift-bound artifact corpus identities resolve against repo-registered or custody-bound bytes (seal no longer self-certifying); Dead pre-addendum no-freshness accommodation removed or pinned as intentional forward-compatibility; artifact_schema_invalid evidence-binding mislabel renamed or documented at emission site. Authority: [C-045 gauntlet deferrals (council log; detail in docs/run_reports/2026-07-24-screen-budget-gauntlet.md)](docs/council_log.md). Acceptance: [CUSTODY-HARDEN-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from PR #85 gauntlet deferrals; triangle-agreement enforcement (merged) already raises these seams to three-file forgery cost. |
| A46 | FLOOR-WORKLOAD-SIZING-01 | P1 Phase Gate | READY [AGENT] | Re-size the floor/science campaign workloads so measured effects clear the duration-independent attribution floor, and pilot the resulting effect-to-floor ratio before spending quiet-machine nights on ABBA collection at current sizes. | Anchor-attribution error is approximately duration-independent (~1 J regardless of phase size) while effects scale with workload, so lengthening prefill/decode raises effect-to-floor linearly at zero instrument cost. Evidence: Measured effect-to-floor ratio at candidate workload sizes, from a pilot rather than assumption; Re-sized configs for the remaining floor stages, with the sizing rationale recorded; Explicit decision on which queued stages are collected at which sizes. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-WORKLOAD-SIZING-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25; scope corrected same day after the quantitative replay. NOT a blocker on the ABBA roadmap: under the labelled-floor path the queued stages remain scientifically viable at current sizes (tens-of-percent effects on ~50 J clear a ~3 J floor plus claim-side bound). This is a MARGIN optimisation — attribution error is duration-independent while effects scale with workload, so longer prefill/decode buys effect-to-floor ratio for free. Pilot the ratio at candidate sizes before committing the remaining quiet-machine nights. |
| A47 | FLOOR-COMMONMODE-01 | P2 Next Slice | READY [AGENT] | Pre-register and evaluate a common-mode anchor estimator for ABBA blocks: sweep one shared fiducial shift across all four members, re-integrate measured curves, and add only genuinely per-bundle components adversarially. | The fiducial term is ~80% of the composed anchor bound (24.9 of ~31.1 ms, verified) and is literally the same artifact for all four members of a block; treating it as four independent adversarial draws is itself an unphysical modelling choice. Evidence: Block-timescale fiducial stationarity registered as a NAMED transfer assumption with its evidence; Estimator pre-registered before it touches claim-bearing data; The identical estimator applied to BOTH the calibration blocks and the consuming science contrast (a floor calibrated with cancellation the consumer does not get would understate false effects); Quantified gain on a5/a10 blocks versus the worst-case-sum default. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-COMMONMODE-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25. Quantified same day on a5 decode ABBA (10 complete blocks): implemented worst-case-sum half-width gives a 6.46 J comparative floor; a common-mode proxy gives 2.13 J, a 3x improvement — material, but still above that cell's 0.60 J point floor, so it does not by itself restore extraction under the current gate. Value is in tightening the labelled floor, not in avoiding the label. Fiducial share of the composed bound measured at 80-87%. |
| A48 | PHASE-SHARE-ESTIMAND-01 | P2 Next Slice | READY [AGENT] | Investigate the anti-correlated prefill/decode boundary error: energy a shift removes from one phase it adds to the other, so the phase-share estimand has ONE boundary nuisance parameter whose joint envelope is a curve, not a box. | Treating each phase's anchor envelope as an independent box double-spends the shared interior boundary and inflates uncertainty on exactly the split/share quantity the Splitwise replication needs. Evidence: Determined whether _corner_composed_anchor_shift_envelope treats the shared interior boundary independently; Joint envelope over the single boundary-position parameter derived by re-integration sweep (measured-curve arithmetic only); Quantified effect on the phase-asymmetry claim envelope versus the independent-box treatment. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [PHASE-SHARE-ESTIMAND-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from the attribution-limit adjudication. Potentially the largest single win available for Splitwise sizing, at no instrument cost. |
| A49 | MODULARITY-01 | P3 Hardening Candidates | READY [AGENT] | Close the campaign-authoring modularity gap surveyed 2026-07-29: parameterize the campaign generator over a campaign-spec artifact and replace code-side literal assertions (analysis-manifest condition pairs, calibration scopes, phase-metric list) with registry-declared hash-validated sets. | Close the campaign-authoring modularity gap: campaign-spec-driven generation and registry-declared closed sets make every experiment axis swappable by config, per Ed's modularity directive. Evidence: Campaign generator is a parameterized function over a campaign-spec artifact (model, N, size profiles, block pattern, suite ref, run-ID prefix); a model swap touches one spec file and MODEL_TAG/PLAN_ID/run-ID prefixes derive from it with no parallel literal edits; Analysis-side closed sets (condition pairs, calibration scopes, phase-metric list) are declared in hash-bound registry artifacts and validated against those declarations, replacing the code-side literals at analysis_manifest.py:29-30,542-549 and detection_floor.py:87,89-95; Recorded-but-deferred residue dispositioned or re-queued: powermetrics references outside the adapter boundary, external-dataset ingestion, chat-template/thinking-mode seam, ABBA arity welded into three sites. Authority: [2026-07-29 modularity survey (Ed directive + per-axis grades)](docs/run_reports/2026-07-29-modularity-survey.md). Acceptance: [MODULARITY-01 acceptance](docs/process/state_kernel.json). Fence: Modularity applies to the harness, never to frozen claim pins: ratified hard literals (six-decimal pre-registration floor pins, lead-verified digests) stay anti-modular on purpose and must not be parameterized. (D-078 provenance amendment + D-079 operative-floor pins (hard literals are lead-verified, never parameterized)). Note: Minted 2026-07-29 from Ed's modularity directive. Survey verdict: runtime/telemetry Protocol layer and content-addressed provenance spine are already modular; the gap is campaign authoring above the adapter and literal assertions below the reader. Practical payoff lands with the planned Qwen3 cross-generation follow-up. |
| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
| A51 | NODE-CUSTODY-DEFAULT-01 | P3 Hardening Candidates | READY [AGENT] | Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted. | Harden the production DEFAULT_RETENTION_ROOT against concurrent-client collision while preserving next-session custody reclamation (the NEEDS_RULING tradeoff deferred from NVIDIA-RETENTION-FLAKE-01). Evidence: The production DEFAULT_RETENTION_ROOT no longer collides for genuinely concurrent NodeClients sharing a scope, without breaking next-session custody reclamation (a later process must still locate the manifest it is entitled to reclaim); A regression proves two default-constructed clients in one process do not clobber each other AND that the documented reclamation contract still resolves the correct manifest across process boundaries; No retention/custody assertion is weakened; only root selection changes. Authority: [NVIDIA-RETENTION-FLAKE-01 fix report F1/F3 (PR #97): unique default roots close concurrent collision but conflict with next-session reclamation](docs/run_reports/2026-08-03-desk-session.md). Acceptance: [NODE-CUSTODY-DEFAULT-01 acceptance](docs/process/state_kernel.json). Fence: Isolation-only: do not weaken any retention/custody assertion; the reclamation contract's cross-process manifest resolution must survive any default-root change (NVIDIA-RETENTION-FLAKE-01 test-side fix (PR #97) already closed the flake). Note: Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario). |
| A52 | D080-TRIGGER-01 | P3 Hardening Candidates | BLOCKED — D-080-amendment (Ed ratifies the trigger cadence and the runner (cron routine vs manual)) [AGENT] | Wire D-080's standing fresh-eyes sweep to a REAL trigger (calendar cron or every-N-merged-PRs), run as a separate concurrent read-only instance per the Ed-validated 2026-08-03 pattern, findings delivered mid-flight; reconcile D-080 clause 4(ii)'s stale zero-unique-catch citation. | The fresh-eyes sweep fires without anyone remembering it, on a ratified cadence, as a concurrent read-only instance. Evidence: A ratified trigger exists (cron routine or PR-count hook) and has fired at least once; D-080 clause 4(ii)'s stale citation is reconciled by amendment. Authority: [D-080 + the 2026-08-03 sweep finding (never fired) + Ed's concurrent-audit validation](docs/decision_log.md). Acceptance: [D080-TRIGGER-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-03: minted from the two-week soundness sweep's finding that D-080 has never fired, plus Ed's validated concurrent-audit pattern (memory: concurrent-fable-audit-pattern). Non-blocking hardening. |
| A53 | CGV-HARDEN-01 | P3 Hardening Candidates | READY [AGENT] | Harden runner-owned receipt persistence after validator --receipt-out removal: use a dirfd-relative receipt write that closes receipt-write TOCTOU and supplies fsync plus directory-sync atomicity. | The convening runner durably persists validator receipts through a dirfd-relative, crash-atomic, fsync-complete write path. Evidence: The convening runner persists the validator receipt with a dirfd-relative write that closes the receipt-write TOCTOU; Receipt publication is atomic and includes file fsync plus parent-directory sync; Regression tests distinguish path replacement, durability failure, and successful atomic publication. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 receipt-persistence disposition](docs/process_traces/2026-08-05-cgv-f3-consult/SYNTHESIS.md). Acceptance: [CGV-HARDEN-01 acceptance](docs/process/state_kernel.json). Fence: Keep this row a sibling of COLDGATE-HANDOFF-01 and never merge them: durable receipt storage and validated-byte judge handoff have different contracts, tests, and failure consequences (2026-08-05 F3 consult Q2 dissent). Note: 2026-08-05: runner-scoped because PR #103 removed the validator's --receipt-out; deliberately registered as a sibling of, never folded into, COLDGATE-HANDOFF-01. |

## Active Global Work-Selection Gates

NONE — no global work-selection gate is active.

### [ED-EXTERNAL] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
## Mission M0: Preflight (every session)

1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
   if present, "Current Project Status", "Known Workspace State", and
   "What Is Next". If the stop card is ACTIVE, it overrides this
   playbook and the task queue until cleared.
2. Read `TASK_QUEUE.md`'s Current Queue and Do-Not-Do-Yet list.
3. Read the selected mission's own read-first list. Read `AGENT_PLAN.md`
   only at phase starts or when the project structure changes. Consult
   `docs/decision_log.md` by targeted decision ID, not as a whole-file
   intake step.
   If the session involves delegation, review, or multi-stream work, also
   read `docs/orchestration.md` (the process layer) — not optional for
   landing code.
4. Check workspace state with `git status --short --branch`; inspect
   recent commits only when the handoff or mission needs them.
5. `python3 -m unittest discover -s tests` — expect `Ran <N> tests` (N per `RUN_STATE.md` Current Verification; `, OK
   (skipped=10)` with zero expected failures as of 2026-07-08 after
   P2-013/P2-014 and the C-011 rigor mechanics. The skips are the `[analysis]`-extra chart tests plus one
   optional-jsonschema test. A red suite is itself the mission: stop and fix
   or report.
6. Review `docs/risk_register.md` at phase starts, before hardware tasks,
   when a trigger fires, or if >14 days passed since the last run report
   with no break recorded in `docs/milestones.md`.
7. At session end, always: update `RUN_STATE.md`, update `TASK_QUEUE.md`,
   write a dated run report in `docs/run_reports/`, update the phase exit
   checklist for anything that closed, and `PROJECT_STATUS.md` if
   advisor-visible state changed. Commit when the user asks or has
   standing-approved it.

Environment cautions:

- The repo must stay at a non-iCloud path (`~/code/...`; R-017). If you
  see `Operation not permitted` on reads inside the repo, stop, wait for
  the lock to clear, re-run the suite, and record the incident.
- CI installs no extras; every new test must pass on a bare Python
  (lazy imports, `skipUnless` for optional deps — D-009).
- Schema changes are additive-only until v0.2 (R-015/D-008).

---

## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)

**Gate:** none. **Spec + acceptance:** `docs/phase_2/phase_2_plan.md`
Slice 2N. This mission adds the code-level route for each work item,
sourced from the 2026-07-05 external code review. Line numbers are from
commit `ae48abe` — re-locate by symbol name if the files have moved on.

Read first: `phase_2_plan.md` Slice 2N + Cross-Slice Contracts;
`joulewise/bundle.py`, `controller.py`, `reduce.py`, `interfaces.py`
(skim whole files — they are small and the invariants interlock).

2N is one mission but NOT one sitting: it touches adapter interfaces,
controller timing, reducer behavior, report parsing, CLI, schema export,
and validation policy. Work item-by-item with the suite green after each,
and land it as roughly three commits so a failure bisects cleanly:

- **Commit A — the adapter seam:** 2N.1 (RunContext + raw evidence),
  2N.2 (measured-window boundaries). Both touch controller/interfaces.
- **Commit B — the read layer:** 2N.8 (BundleReader), with 2N.4 (rail
  contract), 2N.7 (report alignment), and 2N.6's structured read
  failures implemented on top of it. 2N.6's CLI verb rides along.
- **Commit C — schema + metrics:** 2N.5 (schema round-trip), 2N.3
  (token-count fallback), 2N.9 (v0.2 compatibility note).

If a session ends mid-slice, a completed commit group is a clean
handoff point — say which group landed in `RUN_STATE.md`.

Per-item detail (each item = tests green before the next; items 1+2
change the controller/adapter contract and go first):

### 2N.1 `RunContext` seam + raw evidence

- Today: `RunBundleWriter._ensure_layout` creates `raw/` (bundle.py
  ~line 160) but no method writes into it, and adapters never see the
  bundle path — so a real telemetry adapter cannot honor D-002 ("raw

codex
The repository has no active stop card and the worktree is clean. Current source-of-truth language already establishes several audit anchors: `codex-run-v3` for audited CLI runs, `scripts/codex-bridge` for the app-backed bridge, `gpt-5.6-sol`/Fable 5 naming, and per-call reverse-consult effort. I’m now tracing every skill occurrence and every logged deviation against those anchors.
exec
/bin/zsh -lc "SNAP=/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot; rg -n -i 'codex-run|codex-bridge|bridge|gpt-|sol|fable|claude|5\\.5|5\\.6|fast|service.?tier|priority|flex|effort|per-call|model|cadence|round|reviewer|lens|minutes|timeout|subagent|ultra|xhigh|high|medium' \""'$SNAP" --glob '"'*.md'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:3:description: Run 2+ independent workstreams in parallel — one git worktree + branch per stream, lead-driven codex-run pipelines by default (subagent directors only for judgment-heavy streams), landing as separate PRs. Use when a session has multiple independent implementation tasks that would otherwise run sequentially or collide in one tree.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:9:outsourced (~15 min per adapter-sized Codex round). When a session has ≥2
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:10:INDEPENDENT streams, parallelize with isolation. Skip all of this for
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:13:## THE SUBAGENT WAKE GAP (structural; discovered 2026-07-07, JouleWise 4-stream session)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:15:codex-run's "bounded exit re-invokes you" guarantee holds for the MAIN
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:16:LOOP ONLY. A subagent orchestrator that backgrounds a codex-run and ends
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:18:round boundary until something external wakes it. Twice in one session
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:24:RESOLVED by the C-009 Fable+Codex meta-review consensus (2026-07-07,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:25:both models signed; ratified by Ed with the apex ground-truth condition —
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:26:operation-loop §3). In every row below, "lead" = the FABLE main loop:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:27:Fable drives, gates, and adjudicates; cheaper models exist to save Fable
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:28:tokens, and their outputs are advisory into Fable's decisions. The
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:33:| 1 stream | Main-loop direct codex-run; no orchestration machinery unless risk demands it |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:34:| 2–4 pipeline-shaped streams | Worktree per stream, LEAD drives codex-run directly (keeps the wake guarantee), coordinated via a lead-owned STREAM-STATE TABLE: stream, branch, current round, out-file path + status sentinel, next action — this table is the canonical scheduler surface and the guard against lead-context overload |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:35:| Judgment-heavy streams (real mid-stream design disputes) | Opus orchestrator that waits FOREGROUND on codex-run — bounded shell waits chunked under the tool timeout (`while [ ! -f out.status ]; do sleep 30; done`), each wait bounded by the child's timeout + a small grace window; if no status appears, mark the stream STALLED, inspect log/out paths, and hand back to the lead. NEVER background+end-turn (the wake guarantee does not reach subagents). The never-sleep-loop rule binds the MAIN loop only |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:40:- **Heartbeat = BACKSTOP, not scheduler** (~15–20 min background sleep;
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:46:- SendMessage-resuming an orchestrator mid-round orphans its pre-resume
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:51:("Lead"/"orchestrator" here = the Fable main loop unless a stream
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:52:genuinely needs a subagent director — see the wake gap above and the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:55:stream's codex-run pipeline directly — zero orchestrators, zero wake
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:56:stalls, zero heartbeats. The subagent-orchestrator shape below remains
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:60:  -b <stream-branch> <base>`), or `isolation: "worktree"` on the Agent call.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:62:  worktree gets its own Codex bridge state (`git rev-parse --show-toplevel`
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:63:  resolves per-worktree, so `.codex-bridge/` dirs and `resume --last`
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:65:- **Stream direction: the LEAD drives each stream's codex-run pipeline
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:67:  A dedicated orchestrator subagent is the EXCEPTION for judgment-heavy
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:68:  streams — per operation-loop §3 that director is OPUS (Fable stays
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:70:  `model:` — do not rely on inheritance: on 2026-07-07 a session
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:72:  model and had to be relaunched; relaunching is cheap because durable state —
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:73:  worktree diffs, `.codex-bridge/last-message.md`, and the Codex thread behind
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:80:  live/hardware verification (orchestrators can't), resolves cross-stream
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:92:6. That Codex is invoked ONLY via `codex-run` launched as a background Bash
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:96:   (no bare `codex exec`/bridge calls, no separate watchers, no in-turn
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:99:   codex-delegation §Economics): 2-3 parallel read-only lenses (each a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:100:   background `codex-run <out> -s read-only <prompt>`) over the diff before
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:103:   round, then fresh-instance writer ≠ reviewer test review). The
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:105:   analysis goes to Codex lenses.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:106:9. A lens timeout policy: any Codex lens with no output at ~60 min is
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:137:"codex exec"`, worktree `git status`, bridge-dir mtimes — and classify each:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:139:waiting on children → leave alone; (c) WEDGED — e.g. one lens subprocess
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:144:helper. Ground truth comes from processes and file mtimes, not from the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:145:agents' own status claims. Two cheap ground-truth reads worth using
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:169:  two streams each burned a round rediscovering the worktree-commit
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:176:  measurement corpora, local venvs, `runs/`) exist solely in the main
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:177:  tree — stream prompts needing them must give the MAIN tree's absolute
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:183:  lens findings about their staleness are a standing REJECT class
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:185:- Fixture-first / hardware-blocked streams always get the FULL lens
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:189:  all passed; only the adversarial round refuted them. Wire/argv/protocol
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:3:description: Event-driven multi-model review council — decide when work needs full cross-model review (Claude lead + Codex peer + Opus sweeps), run the session shape, record it in the project's council log. Use when landing adapters/contract changes/multi-commit series, when a sub-agent's work needs counterreview, or when the user asks for council/cross-model review.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:6:# Event-driven multi-model council
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:8:A council is cross-model review with discussion — not ceremony. Its value is
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:10:verification, a same-model adversarial workflow, a Codex reverse-review, and
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:22:- Genuine design disagreement between models, or the user asks for it
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:24:**Light review** (single Opus sweep or single peer pass, no discussion round):
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:27:**Solo** (no council):
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:34:ten hours of an open measurement window lost to an untracked background job, and
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:35:six fix rounds building a guard on the wrong axis — were nameless until
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:38:global CLAUDE.md rule 11 — referenced, never restated here.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:40:**Cadence — ONE unit, not several.** Every **10 delegated invocations**, plus
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:41:mandatorily at every **phase boundary**. A multi-way OR-cadence over invocations
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:47:is PROVISIONAL — calibrate it against `docs/process/model_allocation_ledger.md`
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:50:**Composition — rotate.** **Cold Fable every sweep** (fresh session, no loop
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:51:context) — it is the raison d'être, the only lens targeting the nameless failure
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:52:class, and it never rotates out. **Plus ONE rotating second lens**, alternating
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:53:the Opus contract lens and the Sol execution lens. All three run only at phase
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:54:boundaries, or when the cold lens flags something material. Why rotate rather
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:55:than run both every time (this corrects a miscitation): the execution lens's
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:58:with NO question in hand, and an execution lens with no target degenerates to
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:59:"run the tests again." Contract and execution are verification lenses, and the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:63:A packet organised around "the assembler's evidence against itself" contains only
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:72:    ROUND COUNTS PER OBJECTIVE — round counts expose the six-round-guard pattern
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:84:existing zero-unique-catch drop rule: a rotating lens with zero plan-changing
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:85:catches over two full sessions rotates down; the cold lens is evaluated on a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:99:**Records.** Sweep outcomes go to `docs/council_log.md` with PER-LENS
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:100:attribution, feeding `docs/process/model_allocation_ledger.md`.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:104:- **Lead (Claude/Fable, main loop)** — scopes, diagnoses live failures, owns the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:108:  anything important: Codex lenses inform, but the last judgment pass over
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:109:  the final diff is always Fable-level (stream orchestrator for its stream,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:111:- **Peer (Codex/gpt-5.5 or equivalent second model)** — implements against pinned
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:122:  lens (invoked per codex-delegation's ONE stable mechanism — `codex-run
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:123:  ... -s read-only`, never bare `codex exec`) — near-free, so run many. Claude-family
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:124:  sweepers (Opus/Fable subagents) only where the sweep needs harness access
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:125:  (running suites, live probes) or Claude-side judgment; keep Fable for the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:126:  highest-level orchestration and skill distillation only.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:131:  silent application. Bound discussion to 1–2 rounds; on unresolved
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:135:- Ask one explicit judgment question at the end of any fix round ("does X
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:149:  survived, positions → resolutions, dissents, follow-ups. No transcripts.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:153:  capture) at entry close — per-effort-tier sessions/tokens table plus the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:154:  quota signal — and pair it with the Fable-side triple (generation /
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:158:  Sol volume is ~97% cached input, so token counts and cost rank layers
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:172:  prompt-contract gaps, model-assignment mistakes — and the surviving lessons
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:175:  Known examples worth checking each time: poll-vs-await stalls, subagents
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:176:  silently inheriting the wrong model, orchestrators ending turns mid-loop
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:181:  the positions, the actual reasoning exchanged, what resolved it, who
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:182:  prevailed and why, dissents overridden. Audience: a future model reading
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:184:  Fable authors all traces (Ed: best model for it). Mechanics: every stream
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:187:  worktree .codex-bridge/*.log — archive these before worktree removal, and
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:189:  reasoning. Resolved nits are noise; design-bearing disagreements — 
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:190:  especially where one model out-argued another — are the signal.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:211:1. **Parallel divergent threads, one lens each** — e.g. DESIGN (propose the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:216:   passes)** — plus an Opus **ground-truth audit** that parses the actual
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:219:   ground-truth audit repeatedly found decisive facts nobody's reasoning
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:229:   a fresh-context strong-model agent (Fable-tier, spawned — never the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:232:   what reviewer-2 says, verdict pass / major-revision / reject. Cross-model
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:3:description: The total operation loop — one invocable procedure composing intake, stream decomposition, model assignment, the per-stream Codex pipeline, lead gates, integration review, fleet health, trace capture, bookkeeping, and same-session skill distillation. Use at the start of any substantial session with multiple tasks or delegated implementation; it is the conductor score over the council, codex-delegation, adversarial-review, multi-stream-worktrees, and consistency-sweep skills.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:10:is cost-of-being-wrong: **every step must be skippable, and solo work must
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:18:assembled from it in minutes, before worktree cleanup. The same scratch note
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:21:`~/.claude/skills/skill-usage-log.md` (format in that file) — the evidence base
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:24:Standing cadence alongside these steps: every 10 delegated invocations, plus
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:38:  than one interval. Never `nohup`/`&` from Bash — use `run_in_background`.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:54:**The disposition these correct** (Fable adjudication, 2026-07-26): the lead
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:65:(the artifact they asked for, not the process around it) — step 8 checks
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:88:C-023 JouleWise rigor review: the lens fan-out's deliverable spec
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:100:(multi-stream skill §wake gap): lead-driven codex-run pipelines with a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:102:orchestrators (foreground bounded waits + STALLED-handback, explicit
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:103:`model:`, full prompt contract per multi-stream items 1–9) only for
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:104:judgment-heavy streams. Launch subagents in one message.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:107:impl, fix rounds, 12 review lenses, integration) with ZERO wake stalls,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:116:no-agent quiet lock (all fleets, cadence, and Codex load stopped first).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:119:## 3. Model assignment — which subagent, when, and how to invoke it
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:121:**GROUND TRUTH (Ed, 2026-07-07, ratification condition on the C-009
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:122:consensus): FABLE IS THE APEX AND THE FINAL SAY on all high-level
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:123:processes and judgments.** It is the smartest model on the team and
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:125:model's role exists to SAVE FABLE TOKENS, never because its judgment is
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:126:preferred. All escalation paths terminate at Fable; all other models'
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:127:outputs are advisory inputs INTO Fable's decisions; "lead" in every
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:128:topology table below means the Fable main loop. When stakes are high
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:129:and judgment is the bottleneck, spend Fable without hesitation. This is
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:130:seniority, not omnipotence: Fable is reviewable and sometimes wrong
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:131:(5.5 has overturned Fable-designed schemas on review — that is the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:133:itself Fable's.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:137:| Model | Use for | NOT for | Why |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:139:| **Fable** (apex) | orchestration, stream ownership, triage, the FINAL diff gate, live/hardware verification, merge decisions, bookkeeping, skill distillation, deliberation-trace authoring | volume reading/writing Codex can do cheaper | scarce resource is Fable CONTEXT + judgment, not tokens; the merge gate is never delegated |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:140:| **Codex 5.5-high** (volume) | implementation, counterreview lenses, test writing + writer≠reviewer test review, whole-module reading/analysis, computer use, AND all security-shaped/adversarial-audit work (codex-delegation §Security) | the merge gate; live/hardware verification (no device/sudo); bookkeeping | near-limitless quota → redundant fresh-eyes passes are free; fresh instances carry no thread state → genuine independent review even of its own code; not tier-gated on adversarial vocabulary |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:141:| **Opus** (specialist sweeper / stream director) | sweeps needing harness access (suite runs, live probes) or Claude-side judgment; AND — per Ed's standing directive (2026-07-07 checkpoint session) — STREAM ORCHESTRATOR duty directing Codex threads, so Fable stays apex-only (Fable = expensive senior expert; Opus = smart director for 5.5) | default review/refutation lenses (dropped 2026-07-07: zero unique catches ≥2 sessions — Codex lenses own that) | orchestration needs judgment-above-Codex but not Fable-priced judgment; CAVEAT: Opus orchestrators hit the subagent wake gap (multi-stream-worktrees §wake gap) — lead heartbeat is required infra; AND (C-010, 2026-07-08): a full 4-stream session ran lead-driven with ZERO orchestrators and zero stalls — orchestrator duty is now the exception (genuine mid-stream judgment only), not the default |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:143:**5.5-reviews-consequential-decisions doctrine (Ed, 2026-07-07):** every
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:147:packets; one codex-run per packet). No ceremony for mechanical choices;
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:151:reviewer roles (Ledger Auditor, Merge-Order Simulator, Prompt-Contract
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:153:Reviewer, Quiet-Machine Contamination Forecaster — spawn by name as
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:154:read-only lenses when their trigger moment arrives).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:160:the code commit they justify (ledger-only commits allowed solely for a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:164:Evidence (artifact, commit, or lens out-file — MANDATORY; transcribed
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:165:lens judgments link their source) / Confidence / Binds / optional
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:177:post-hoc state goes in a new addendum entry (a staleness lens WILL
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:184:gameable), with numeric backup (lead rework minutes, gate test failures,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:185:missed acceptance items) and prompt-defect separated from model-defect.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:187:not vibes. Early signal (2026-07-07): design-freedom delegation to 5.5
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:192:codex-delegation §Invoke (codex-run background-call protocol; plus the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:196:**How to invoke a Fable/Opus subagent:** the Agent tool with an EXPLICIT
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:197:`model:` (never rely on session inheritance — a wrong-model default cost a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:206:a. **Design round** — invite Codex's judgment explicitly before code.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:208:   STRENGTHENED (Ed, 2026-07-09): for design-bearing streams the round
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:210:   stream spec/prompt to 5.5 for opinion, lead judges/revises, THEN
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:217:c. **Counterreview lenses** — 2–3 fresh read-only Codex lenses over the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:221:d. **Test amplification** — a dedicated Codex round writes edge-case tests
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:224:   round when the writer≠reviewer audit (e) drives the additions
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:226:   round, same coverage effect, one fewer round).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:227:e. **Writer≠reviewer test review** — a FRESH Codex instance audits all new
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:231:   diff inline; escalate to Fable-level debugging after 2 Codex failures.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:233:g. **Fable diff gate** — the orchestrator reads the FINAL diff, weighs
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:235:   row if the gate finds what the lenses missed. **Mandatory lens (Ed,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:236:   2026-08-05): MERGE-ABILITY / overbuild prune** — Sol overbuilds on
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:253:  review by 2–3 FRESH read-only reviewers with distinct angles (deep
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:256:  triage with recorded dispositions, (c) 5.5 fixes applied +
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:260:  last review round gets one more fresh-eyes 5.5 pass before merge — no
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:270:## 7. Fleet health checks (cadence, while streams run)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:273:evidence (`ps` etimes, bridge-dir mtimes, worktree `git status`) —
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:275:multi-stream skill. SKIP: no background fleet running.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:295:  worktree cleanup (quotes need the bridge logs; archive per the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:314:  where a workspace-write codex round is (or will be) running; a fix
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:315:  round's cleanup reverted the lead's uncommitted bookkeeping (recovered
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:317:  bookkeeping BEFORE launching any concurrent round in that tree, or
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:321:  docs. After a session with multiple skill edits, include ~/.claude/skills
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:324:  2026-07-09): checkpoint-commit CADENCE is per-artifact, not
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:327:  (implementation done pre-review, post-fix-round), labeled as
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:364:distribution across sessions, not just this session's rows; model-defect
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:21:expansion council, worktrees, ultracode); 3 streams (L docs / C capture / S
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:22:sentinels); first session mixing codex-run with Workflow-tool orchestration.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:29:| operation-loop §3 model assignment | USED + DEVIATED | codex volume + Fable gates held; ultracode added Workflow-tool orchestration with agentType:'codex' agents — NOT the codex-delegation "one stable mechanism" (codex-run), and it worked well: structured-schema findings, deterministic refuter tiers, zero stalls | codex-delegation needs a §: when to wrap codex in Workflow (fan-out + verification tiers + structured output) vs raw codex-run (single long impl unit, bounded-exit wake) |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:30:| operation-loop §4a design round | USED, high yield | invited design judgment overturned lead designs twice (4x3 Q4 grid; two-window plan) — third session running this pattern pays | — |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:31:| operation-loop §4c counterreview lenses | USED (via Workflow) | adversarial-review shape preserved inside workflow scripts; severity-tiered refuters (2/1/0) | — |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:32:| operation-loop §4d test amplification | DEVIATED | no separate amplification round; structural test additions were folded into the review-fix round (stream S: +6 methods from writer≠reviewer findings) — cheaper, same coverage effect this time | consider: allow §4d to merge into the fix round when the test audit (§4e) drives it |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:33:| operation-loop §4e writer≠reviewer test audit | USED, unique catches | caught "+assertions, zero new test methods" anomaly (stream S) and the 596→597 plausibility question (stream C, pending) | — |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:34:| operation-loop §5 live verification | USED (held the line) | real-corpus strict validation had to run LEAD-side: worktrees lack gitignored runs/ corpora — subagent streams cannot self-verify against untracked data | fold into multi-stream-worktrees: name "untracked-data verification" as a lead-gate item when worktree streams touch validation-bearing code |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:35:| operation-loop §7 fleet health | USED (nothing to do) | zero stalls across ~15 codex-runs + 3 workflows; bounded exits + workflow notifications made heartbeats unnecessary (consistent with C-010) | — |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:36:| operation-loop §8 bookkeeping | USED + NEW PATTERN | pre-commit docs-verification workflow (faithfulness/coherence/claim-trace lenses + refuters) over the C-015 batch caught 1 BLOCKER + 6 should-fixes including decision-log record drift the lead authored | fold into consistency-sweep: a pre-commit docs-verify mode for large landed doc batches (vs the existing end-of-session sweep) |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:39:| council (5.5-reviews-consequential-decisions) | USED, high yield | peer counterreview of both synthesis packets; C-015 peer added the per-item failure-economics catch nobody else saw | — |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:40:| codex-delegation (six-part prompt contract) | USED | all ~15 invocations; pinned-spec prompts kept fix rounds one-shot | — |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:44:| consistency-sweep | PENDING | scheduled before final bookkeeping commit (docs-heavy session, multiple skill edits expected → include ~/.claude/skills in scope) | — |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:47:STALLED-handback, heartbeat backstop, worktree isolation inside Workflow calls.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:56:### against-a-true-null lens instruction (AP-4, caught by oversight AFTER
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:63:   alternative to codex-run, with its trigger condition (deterministic
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:66:4. consistency-sweep: new §Pre-commit docs-verify mode (3 lenses + refuters
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:79:- Oversight round validated the merge-order-simulation reviewer role
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:82:  CONTRACT the docs-verify round had already passed — layered doc review
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:85:  null/extreme case" lens instruction).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:108:derivability closed (scripts/codex-run committed; orchestration.md
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:110:CLAUDE.md machine-local reference fixed; decision index regenerated;
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:125:codex-run sessions, zero wake stalls; §read-only parallel lenses;
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:129:round + severity-tiered oversight).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:131:- Ed directive mid-session: max-Codex, Fable high-level only —
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:135:  fresh-eyes lens (caught a real FakeClock-blind refactor regression) —
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:148:  rollup, sampler API namespace) invisible to 680+ tests and 9 lenses —
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:152:- council: tier selection §used (solo impl + light cross-model review for a small timing-semantics change; no full council per rule 3). Council-log entry recorded (C-018).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:153:- codex-delegation: §review-consumption used (final message + diff only, via codex subagent driving scripts/codex-bridge review; one resume to get format compliance). Implementation NOT delegated — 2-line reorder, delegation would cost more than doing (token-economics call).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:157:## 2026-07-09 — JouleWise CP-5 resume session (Fable lead)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:159:- codex-delegation: codex-run bg protocol exact; FIX-N contracts 7/7 one-shot-clean; final-head passes caught 3 blockers+7 should-fixes AFTER lens+fix+lead-gate layers — the layer is load-bearing, keep; 1 PROMPT-DEFECT (lead pinned fail-closed-on-any-existing-file for inferred sidecars; scorer sidecars broke) — lesson: when pinning fail-closed semantics over a namespace shared by MULTIPLE artifact types, enumerate the other residents first.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:163:- NEW OBSERVATION for operation-loop/council: CI merge-ref is an unlisted review layer — it caught a cross-branch interaction (#23 fixtures × #27 strict rules) that NO local layer could see (both branches green in isolation). Candidate fold: when parallel branches add validation rules AND fixtures, run the combined suite locally (merge into a throwaway ref) before pushing.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:166:- operation-loop: §0 deliverable sentence + §1 shape used (review-only → no worktrees, 4 read-only lenses); §2 worktree setup SKIPPED (nothing mutates — correct scale-down); §4 pipeline N/A (no implementation); §5 live-verification gate N/A (no runtime surface); §8 bookkeeping run (review doc + C-023 + RUN_STATE pointers; run report SKIPPED — review doc is the session record, pointer entry in council log); §9 no skill folds needed beyond this row.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:167:- codex-delegation: §Invoke background codex-run protocol 5/5 clean (4 lenses + 1 discussion round, zero stalls, zero thin outputs); §Parallel threads read-only fan-out shape used as designed; §Prompt contract lens-angle + severity + failure-scenario + checks-performed clauses all yielded (every lens delivered structured, citable findings); "send the lead's synthesis back for attack" doctrine PAID AGAIN — D1 overturned a lead-accepted blocker (C5-1.1 already contract-capped) and out-designed the lead's work-plan order. Deviation: none.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:168:- council: convened as user-directed full review (correct tier — research-methodology-bearing); discussion bounded to 1 round (converged); per-layer unique catches recorded in C-023; zero-yield layers: none.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:172:- operation-loop: §1 mid-session re-shape used on Ed's go-ahead (review → 4 implementation streams, footprints pinned disjoint, all full-tier); §2 worktrees used (parallel WRITES this time — correct scale-up from the review's no-worktree call); §4 full pipeline per stream (design invited inline, lenses, FIX-N, gates); §5 merge gate ran the full C-010 shape incl. final-head + NEW tail-verification pass; §6 integration review PAID (5 seam catches — S1/S2 written against pre-S3 contracts; no other layer could see it); §8 full bookkeeping + sweep; §8 cadence rule AMENDED mid-session (Ed: per-artifact push, checkpoint pushes) and folded same-session.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:173:- codex-delegation: 20 codex sessions, zero stalls; FIX-N one-shot record now 13/13; instant-completion diagnostic caught 1 real launch failure (zsh parse error on a for-loop of prompts — lesson: never batch multiple codex-run prompts in one shell loop; separate calls); severity-tiered pipeline caught a statistics blocker (percentile-UCB unidentifiable at n=10) that BOTH the lead and the implementer had provisionally accepted — the fresh-lens layer is the quality mechanism for design-freedom delegation.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:179:## 2026-07-09 — spec-fleshing wave 2, ultracode (C-025, same session)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:180:- operation-loop: §4a design-round-first STRENGTHENED clause (Ed, folded this session) validated immediately — P2-030 memo→ratify-with-pins→implement produced zero design rework; §7 fleet-health check used on a user-reported stall: outside evidence (ps etimes, worktree mtimes, workflow journal) showed healthy-slow not wedged; correct intervention was ADDITIVE streams (S9/S10), not kills — fold candidate: "user-perceived stall → evidence check BEFORE relaunch; reinforce with disjoint streams, never a second writer in a live worktree".
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:181:- codex-delegation: FIRST full Workflow-tool orchestration (46 agents, zero stalls, zero errors) — the sanctioned Workflow alternative scales to implement→lens→refute shapes, and its codex WRAPPER agents can git commit+push in worktrees (they are full agents), beating direct codex-run for worktree streams where codex's own sandbox still index.lock-blocks; refuter layer killed 10/30 findings pre-triage (precision working); mutation testing appeared organically in a test-audit lens (5 mutations proving gaps) — fold candidate for §Test doctrine: "test-audit lenses may be prompted to MUTATION-TEST the gates they audit"; FIX-N one-shot record now 22/22; NEVER batch multiple codex-run launches in one zsh for-loop (parse-error launch failure, second occurrence class).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:182:- adversarial-review: severity tiers held; final-head layer caught 2 live-path defects invisible to earlier layers (MLX position under rotation; linter false-negative regression FROM a fix round) — the fix-round-regression hunt is now demonstrably the final-head's highest-yield angle.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:187:- operation-loop: §4a design-round-first used as DEFAULT (second validated run: scoping memo → 3 lead pins → zero design rework); §1 single-stream call correct (one dir = one worktree; no false parallelism); §6 integration review correctly SKIPPED (single stream); §8 tree-quiescence rule observed (bookkeeping only after all codex rounds done) — no recurrence of the C-025 defect.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:188:- codex-delegation: 5-session pipeline; compliance lens caught a char-level registry drift the LINTER structurally cannot see (markdown code-span nesting) — lesson: mechanical linting bounds but never replaces the review lens for ratified-wording fidelity; FIX-N 23/23.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:189:- adversarial-review: cold-start test prompt device ("could a lab that has never seen JouleWise run this?") yielded the highest-value executability finding — reusable prompt pattern for runbook reviews.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:191:## 2026-07-09 — JouleWise C-027 whole-project council review (Fable lead)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:192:- council: §Triggers (user-asked full council), §Session shape B (7 divergent lenses + examiner — shape B's "MORE divergent threads" and final-examiner steps both load-bearing; examiner PASS-conditional caught 7 synthesis defects), §Recording (index row + full entry + deliberation traces), §Roles. WORKED AS WRITTEN.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:193:- codex-delegation: §Invoke (codex-run ×10, zero stalls; one-per-Bash-call rule held), §Prompt contract (all six parts; autonomy clause paid off — 5 unprompted premise corrections), §Direction doctrine (lens-names-an-angle, CLEAN-needs-checks-line both used), §Model-version scoping (FOLLOWED: calibration batch logged, promotion refused pending A/B), §Consume (final-message-only; .status naming), §Economics (counterreview of the lead's synthesis was the round that caught the most). GAP FOUND: skill still titled "gpt-5.5"; model now gpt-5.6-sol behind config — needs a one-line model-note after the sealed A/B.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:196:- Session-level lesson for skills: the REVERSE lens (audit the lead against its own rules) produced 2 of 8 blocker clusters — council skill's reverse-review emphasis validated again; consider making a whole-project reverse audit a standing periodic trigger.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:199:- codex-delegation §Invoke/§Prompt-contract/§Economics: 6+ codex-run-v2 sessions (merge review, p2041 diagnosis, deletion triage, flake root-cause, vetted composition ULTRA, p2037 ULTRA, scheduling scout). NEW §Effort-tier policy added (Ed): ultra=subagent-needing sessions only; xhigh/high individual tasks; push xhigh scope until first prod-quality miss and record ceiling. The two ULTRA launches this session predate the policy — going forward they'd be xhigh.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:200:- adversarial-review shape used implicitly (severity-tiered verification of Sol merge-review findings: blocker fact-checked, should-fix verified via reconstructed 3-way merge).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:201:- LESSON (lead-side defect caught by Sol review): `git checkout --ours/--theirs <file>` during conflict resolution takes the WHOLE file, silently discarding the other side's cleanly-auto-merged hunks. Correct tool: resolve marker regions in place, or reconstruct with `git merge-file` per file. Candidate for codex-delegation/multi-stream field notes.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:202:- Session second half: adapter v1 adopted + codex-run-v3/codex-usage built+installed (runner-injected report contracts); scope-restraint 3-layer design (language live, backstop in flight at pause); NEEDS_RULING generalized early-return; design-consult-by-default doctrine (P2-044 first product: corpus-grounded HAC design, 47x variance underestimate found); PRs #49/#54 merged, #50-#53/#55 held; P2-037 second transport-OK/no-report incident (independent audit pattern instead of self-grading resume). Usage data: 1 ultra = 35.3M tokens ≈ 11 xhigh sessions; Fable generation ~1.8M vs Sol ~112M same arc. Paused at C-028 checkpoint #4 (25a8b05).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:203:- C-028 close (2026-07-11 second half): full gauntlet validated end-to-end (~57 Sol invocations, ~16 refuters: 70/15/15 confirm/narrow/refute — narrowings highest-value); integration tree caught 38 pre-merge cross-stream failures; enforcement stack live-tuned (bytecode false-positives → recorded exemption; 3 compliant NEEDS_SCOPE stops with correct-path discovery; nested-repo guard limitation → prompt-scope + lead-diff fallback); v3 defects logged (resume no-op, in-place-edit crash); wave lesson: never trust loop completion banners, verify per-PR state (DNS-blip skip caught). Fable dictated-fills pattern for bookkeeping finalization: agent verified every dictated fact against evidence and caught lead miscounts. Skills amended: adversarial-review + multi-stream-worktrees §C-028; CLAUDE.md rule 9 (gauntlet default) added.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:207:- operation-loop §0-§8 walked in order: §0 deliverable sentence, §1 four-stream shape (1 bench + 3 Sol pipelines, disjoint footprints), §2 worktrees, §4 per-stream pipeline (design folded into impl prompts as DESIGN-section requirement — worked well at this scope), §5 lead gates, §8 bookkeeping. §6 integration review SKIPPED (streams not merged yet — deferred to merge wave). Consistency sweep DEVIATION: lead quick-pass instead of delegated sweep (upstream outage); gen_state --check + tests stood in for the counts surface.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:208:- council §Recording: spend-snapshot convention ADDED this session (codex-usage at entry close + Fable triple + composition caveat) and exercised in the C-028 addendum; C-029 index row kept to pointer form (run report owns the trace — v2 discipline held).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:209:- codex-delegation §Invoke: v3 field notes ADDED (WRITE_SCOPE-in-prompt rc=64; MANDATORY explicit --effort after 13 unintended-ultra invocations via config passthrough; thin-output-OK = FAILED; resume-after-outage preserved 206k tokens of fix-round work, worktree = ground truth). §Prompt contract used on all 13 invocations; FIX-N contracts 2-for-2 clean (18-item and 1-item rounds).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:210:- adversarial-review: severity policy APPLIED WITH SUBSTITUTION — 5 blocker claims adjudicated by lead code-reading instead of 2-refuter rounds (cheaper + stronger for mechanically-verifiable claims: 2 confirmed, 1 partially refuted, 1 design ruling, 1 reproduce-first-in-fix-round). Delta re-audit doctrine BLOCKED by upstream outage (3 attempts) — owed pre-merge, recorded in PRs/RUN_STATE. Lead-gate unique catch: capped-cell over-refusal in the fix round (third "fix rounds introduce defects" datum).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:213:## 2026-07-13 JouleWise restart-close + audit-gate session (Fable lead)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:215:- adversarial-review §C-028 amendments: delta re-audit after fix rounds validated AGAIN (DRA-001 blocker found on a twice-reviewed diff — fourth "fix rounds introduce defects" datum); explicit --effort xhigh on all review sessions (3 sessions ≈ 7.0M tokens vs prior day's unintended-ultra 13 ≈ 118M — ~17x cheaper for equal role).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:216:- codex-delegation §Invoke: v3 wrapper effort passthrough fix held (manifest rows show xhigh); WRITE_SCOPE in-prompt requirement respected in all prompts.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:218:- NEW LESSON (fold candidate, not yet folded — audit may reshape it): cross-thread collisions in one working tree are now real (Ed runs concurrent threads); the two-writer rule needs a cross-THREAD corollary — before any commit, diff-inventory the tree for foreign changes and verify provenance with the user rather than pathspec-committing around unexplained diffs blindly.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:220:## 2026-07-13 — Bridge v1.1 max-co-work session (Fable lead, background job)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:222:- operation-loop: §0 deliverable sentence; §1 single contract-bearing stream (worktrees SKIPPED correctly); §3 default assignments (design consult xhigh MCP, impl xhigh CLI, fix3 dropped to high when triggers lapsed — first non-xhigh round, correct); §4 full pipeline incl. STRENGTHENED design round (lead's spec itself consulted pre-implementation — Sol amended 5 pins and caught a v1 adapter bug; the pre-decision-consult default earned its keep); §5 lead gates (live wrapper dogfood, live reverse consults, flake triage: lead-rerun caught an agent-load flake the worker's green run masked); §8 bookkeeping (run report + C-032 row + D-065 + D-064 tracked manifest — first session to create docs/process_traces/); §9 folds done mid-session (codex-delegation +2 field notes). §6 SKIPPED (single stream), §10 not fired (single-PR).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:223:- adversarial-review: 3 distinct lenses + severity tiering; DEVIATION (recorded in report): round-1 blockers verified by lens-repro + independent lead code-trace instead of 2 fresh refuters; mechanical existence claims lead-verified. The mandatory delta re-audits then caught 3+2+1 fix-round defects INCLUDING TWO CORRECTIONS OF THE LEAD (a lead-graded nit upgraded by auditor repro; a vacuity the lead's own check missed) — the substitution is safe only WITH the delta re-audits behind it.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:224:- codex-delegation §Invoke: v3 preflight gotchas ×3 (WRITE_SCOPE prompt line; nested-repo refusal from a stale .claude/worktrees entry; ignored-cap 10k tripped by .venv → cap now 50k + CODEX_RUN_IGNORED_CAP) — folded same-session into the appendix. Consult scorecard bullet added.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:226:- consistency-sweep: delegated Sol xhigh, scope included ~/.claude/skills + global CLAUDE.md + new ~/.codex/AGENTS.md (multi-skill-edit rule applied).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:227:- NEW LESSON (folded into trace/report; candidate for operation-loop §5): harness auto-mode can DENY agent self-merge of agent-authored PRs regardless of standing CLAUDE.md authorization — plan merge waves so Ed's merge click is the explicit last step, or run merges in a session where Ed names them.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:229:## 2026-07-16 — JouleWise resumption + no-hardware batch (Fable lead)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:231:- operation-loop: §0 intake + deliverable sentence; §1 re-shape fired TWICE on mid-session scope additions (Ed: "work the no-hardware backlog"; Ed: "handle the merge yourself"); §2 worktree-per-stream (4 streams, disjoint footprints held); §3 default assignments (Sol high audits per Ed's ask, xhigh only on contract-bearing SPLIT-AP/AXI-SB, Fable subagent for web verification per rule-9 dictated-fills); §4 full pipeline per stream; §5 lead gates (CI-log verification that a green job actually EXECUTED the new test; AXI-SB live probes lead-run; field-name check before accepting `supported`); §6 integration review fired at 3 streams (0 unique catches — first zero-catch datum for this layer, tally per §10 drop rule); §8 full bookkeeping arc; §10 not fired beyond the tally note.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:233:- adversarial-review §C-028: delta re-audit after EVERY fix round — paid off with an EIGHTH "fix rounds introduce defects" datum, and the first LEAD-AUTHORED one (the lead's own FIX-1 pin dropped predictor components; the delta pass caught it). Bench-fix threshold used twice; both bench edits got fresh micro-reviews (final-head rule applied to the lead's own edits).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:236:- consistency-sweep: delegated (Sol high) before the final bookkeeping commit; scope: session-changed status docs.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:239:## 2026-07-17 — JouleWise Window-A execution + wrap (Fable lead, continuation)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:242:- adversarial-review: delta re-audits caught fix-round blockers twice more (9th/10th data); anti-gaming lenses on BOTH positive (AXI-SB) and negative (AXI-SC) verdicts — negative-verdict honesty (positive-control path) is a new lens angle worth folding.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:244:- consistency-sweep + dataviz + claude-in-chrome: sweep pre-final-commit (4 catches); dataviz validator-gated palette both modes; lead render-check in Chrome caught an axis-label collision — "render and look" is non-delegable.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:245:- 2026-07-17 (JouleWise, screensaver-contamination session): codex skill §Effort selection + §Primary MCP path (consult xhigh discussion-lane, impl xhigh workspace-write; MCP idle-timeout killed impl mid-turn → recovered via §Session observability rollout discovery + codex-bridge resume — recipe worked as written). bridge session-open/close ceremony used; gotcha: --paths defaults to exact match, need explicit `path:subtree`, and a FAILED close retains the lease (needed lease-release). adversarial-review shape started (lenses split lead/Sol) but checkpoint-stopped mid-round; resume in RUN_STATE. Validation: lead live-probe verification caught a fixture-matched-the-bug parser defect Sol's green tests missed — rule 1 earns its keep again.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:247:## 2026-07-18 (late) — JouleWise D-077 fix-round arc (Fable lead)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:248:- adversarial-review: §Shape step 3 (tiered verification), §C-028 amendments (delta re-audit after EVERY fix round — applied 5x, caught real defects in rounds 3, 4, 5, 6 incl. a fail-open inf-anchor gate and a manifest-clobbering writer; narrowed the round-6 static P1 race per the split-verdict synthesis rule), §Severity rubric for triage. Deviation: round 8 (test-only) got lead review + suite instead of a Sol delta re-audit — recorded in the run report.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:249:- codex-delegation: §Effort-tier policy (xhigh for fix rounds + refuters, high for the test-only round), v3 field notes (hit the documented rc=64 WRITE_SCOPE gotcha twice before re-reading — added a "read field notes first" note), new field note added: xhigh review-genre null-final-message defect 4x + bridge-resume recovery, default read-only sandbox rc=77.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:250:- operation-loop §5 gate shape: followed for PR #77 (lead+Sol reviewed final head; merge left to Ed per merge-authority memory).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:251:- 2026-07-19 (JouleWise, extended quiet window): codex-delegation §MCP-route — two Sol sessions (read-only recompute audit AUDIT_PASS; workspace-write scoped status-page split, NEEDS_SCOPE honored, 20/20 module tests) — worked well, MCP background tasking clean; adversarial-review §severity-tiering applied lightly (exploratory readout → single recompute lens, precedent 3-lens reserved for front-facing promotions); multi-stream-worktrees NOT used (single [QUIET-MAC] lane); operation-loop §bookkeeping (run report + RUN_STATE + PROJECT_STATUS + DRIFT + memory). Field note: detached nohup chain + watcher-Bash re-invocation is the right shape for multi-hour measurement; guard-abort → same-root resume (runner skips complete bundles) avoided any data loss from an operator return.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:252:- 2026-07-19 (JouleWise, D-078 arc) LENS DOCTRINE UPDATE for adversarial-review: on MEASUREMENT code/data, a physics/causality lens (energy vs event timeline, power*duration plausibility, clock-domain checks) catches what recomputation lenses structurally cannot — three Sol recompute audits reproduced every number to 1e-13 while the instrument was misattributing 8 J windows; one causality-framed audit found it immediately. Ed-confirmed: physics lenses on measurements are more useful than recalculation ones. Default review panel for anything measurement-adjacent: contract + execution + PHYSICS (mandatory) + cross-model; recompute alone is never sufficient sign-off. Also: spend Sol xhigh on ONE deep adversarial whole-artifact pass per round (fresh thread each round, no anchoring), fan Fable across distinct lenses for parallelism.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:253:- 2026-07-22 (JouleWise, D-078 close-out session): adversarial-review §Shape (3-lens packet fan-out) + §C-028 (delta re-audit of round-8 caught a real understated-B_fiducial blocker two audited rounds missed; 8 refuter runs, blockers 2 distinct lenses; split A1 verdict lead-synthesized) — NEW amendments added (filter-safe refuter phrasing; provenance-attribution before scope triage). codex-delegation §Invoke/§Adapter (codex-run-v3 xhigh implementation genre; NEEDS_SCOPE early-return honored; review-genre null-final recovered via bridge resume) — NEW field note added (never bench-edit a worktree during an enforced-scope session; false SCOPE_VIOLATION + resume-registry eviction). consistency-sweep (delegated xhigh, end-of-session). council skill §Recording → C-031 entry. operation-loop §5 gate shape for PR #79 (lead+refuters over final head; merge left to Ed).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:254:- 2026-07-24 (JouleWise collection arc): codex-delegation heavily (9 xhigh sessions: 3 forensics, 4 implementation waves, 2 rulings-driven resumes; NEEDS_SCOPE/NEEDS_RULING protocol fired correctly 4x; field-note violations by the LEAD twice — bench edit during enforced-scope (branch switch mid-extraction → false SCOPE_VIOLATION), and pkill without lock cleanup). adversarial-review §delta-re-audit killed a live estimand-biasing design (two-process overlap) pre-merge. NEW operational doctrine candidates for skills: measurement windows need TOTAL orchestrator dormancy (wake-up turns contaminate admission — single-event monitors only); compact bracketed windows over marathon windows (drift gate); per-stage settle periods; campaign lock pid-hygiene. Consider a new 'quiet-measurement-window' skill next session.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:257:- adversarial-review: §tiered-verification + §C-028 amendments driven hard (4 audit rounds, 3 refuter rounds, delta re-audit after every fix round — pattern held: every fix round introduced or exposed defects). AMENDED this session: new §C-033 (cross-model Opus-contract+Sol-execution pairing = default; high = paired-refuter tier; auditor severity inflation systematic; dictated-fills as catch layer).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:258:- codex-delegation: §invocation + §effort-tiers throughout (~15 Sol sessions). AMENDED: new C-033 field notes (genre/write-scope exactness, ACCEPTANCE_FAILED not resumable, nested-repo strict-scope refusal, codex-usage feed broken, high-tier evidence).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:263:## 2026-07-28 (JouleWise, Fable magistrate) — mint-implementation session
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:264:- operation-loop: §0a R1 enforced hard (5 broken-wake interventions, redundant timers); §0 SKIP taken (user-named task) with ✎ sentence; §1 re-shape run twice (Ed's mid-session S6 + pruning ask); §5 gate full shape on PR #87; §7 outside-evidence health checks on cadence; §8 full bookkeeping; §10 not triggered (single-PR merge).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:266:- council: fired via the D-072 gate shape; C-039 index row recorded; fresh-eyes sweep NOT due (no phase boundary; ~16 invocations < cadence? — check next session, borderline).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:271:## 2026-07-30 (JouleWise mint-merge session, Fable magistrate)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:272:- adversarial-review §severity-tiered verification + §delta re-audit: FIX-9/FIX-10 delta re-audits (both FAIL — the layer that caught QA-1 and QA-10A/B against a green 2280-test suite). The §C-028 "fix rounds introduce defects" clause earned its keep twice in one day.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:273:- codex-delegation §invocation + §prompt contract: 4 Sol sessions (audit xhigh ×2, fix high ×2). FIELD NOTE: codex-run-v3 `--write-scope` alone does NOT grant writes — implementation runs need explicit `-s workspace-write`, else the session returns blocked with completion=none (cost: one wasted high session).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:274:- council §cold-gate (rule-11): mandatory trigger honoured (2 same-signature failures → consult, not round 3). Cold Fable + Opus contract refuter pairing exercise #4; refuter caught that the magistrate's OWN ruling (R2 invoked-only) was the QA-10B defect; synthesis = D-088. The pairing's cross-model diversity clause is now 2-for-4 on findings against the adjudicator.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:277:- Dictated-fills (magistrate→subagent verification pattern): caught 2 magistrate dictation errors (TokenPowerBench arXiv id; 4.7×-vs-4.9× params) + 6 advisor-brief overclaims. Pattern remains the highest-precision error-catcher in the loop.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:279:## 2026-07-30/31 — contrast-window session (Fable magistrate)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:280:- operation-loop: conductor shape held (window → post-window → overnight D5-J → merge train); magistrate operated the window solo per doctrine.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:281:- council: rule-11 cold-gate mechanism exercised TWICE outside the skill's enumerated triggers but per D-089's revisit clause (DA-1 disposition: cold Fable + Opus refuter, split verdict, magistrate synthesis → D-093) — the split-verdict synthesis path (rule 9) carried real weight; consider promoting "delta-audit FAIL on a consult-sanctioned structural fix" to a named cold-gate trigger in the skill.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:282:- codex-delegation: 4 codex-run-v3 invocations (D5-J impl ×2 launches — first bounced on missing literal `WRITE_SCOPE:` field in prompt, RECORD: the flag requires the field in prompt text; audit ×1; plus one MCP consult during window recovery). Envelope early-returns worked twice (read-only mount blocker; honest partial). Consumption discipline held (final message + git diff only).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:285:- Field note: unittest summary evidence — `cmd | tail -N` in a background task DESTROYS the pass/fail evidence (pipeline exit = tail's, summary may be buffered out of the tail window); capture to file and echo `$?` instead. Cost one redundant 12-min suite run.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:287:## 2026-07-31 — claims-desk day + metrology window A (Fable magistrate)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:289:- council/cold gates: TWO mandatory cold gates in one day (DA-1 disposition; B1 second-formulation) — the B1 gate was UNANIMOUS across cold Fable + Opus refuter, first time; the refuter's file:line verification (writer emits no v2; scanners skip non-v1) was the decisive input. Pattern worth distilling: when the refuter CONFIRMS rather than splits, synthesis can adopt the refuter's stricter variant without a third instance.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:291:- codex-delegation: 7 codex-run-v3 invocations; recurring worktree git-metadata commit failure (sandbox cannot write .git/worktrees/* of a linked worktree) — ALWAYS plan lead-side commit for worktree sessions.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:295:## 2026-08-01 (overnight metrology window B session, Fable magistrate)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:296:- codex-delegation: §invocation + §prompt contract — bounded Sol xhigh root_cause consult via codex-run-v3 (read-only, consult_anchor_v2.md); packet self-corrected mid-flight (killed v1 on TM-exoneration evidence, refired v2 with bird identification). Consult REFUTED the lead's drift-rate mechanism (quantization-confounded) while confirming the structural knife-edge — exactly the license-to-disagree pattern rule 2 wants; its F2 attempt-cap catch and F3 SIGSTOP-lifecycle additions were both adopted verbatim.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:297:- operation-loop/§window custody (project runbook §5B/§8/§10/§11/§12): three §10 continuations + salvage close executed solo; recorder-then-verdict order held; NEW hazard for the skill docs: operating-session OUTPUT STREAMING during idle gates caused failure #3 — candidate amendment for the council/operation-loop measurement-discipline sections ("zero tool calls" -> "zero tool calls AND zero streaming; one-line arm messages").
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:298:- Escalation trigger (CLAUDE.local rule 11): fired twice (§5B same-signature aborts -> consult; slot same-signature failures -> salvage close). Both stops honored without magistrate override.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:300:## 2026-08-01 — JouleWise desk/adjudication session (Fable magistrate)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:302:- codex-delegation: 3 Sol xhigh sessions via the codex subagent (read-only adjudication audit; read-only commit-3 design consult; workspace-write commit-3 implementation w/ 6-path WRITE_SCOPE). Consumed as final reports only. Effort-tier §: xhigh triggers held (adversarial review, design-bearing, cross-contract). Field note: audit line-number citations drifted (R14, substance held) — consider requiring `git grep -n` verification snippets in audit briefs.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:303:- adversarial-review: severity-tiering honored — the audit's 3 groups got magistrate bench verification (blocker-grade, 2+ independent checks each); cold gate = 2 refuters w/ distinct lenses (fresh-Fable merits + Opus contract).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:304:- council (rule-11 cold gate §): FULL shape exercised: cold Fable ruling → bounded factual follow-up (custody sweep contradicted a drafted license line; instance re-drew on the merits) → independent Opus refutation (14 findings) → magistrate synthesis (D-100). NEW pattern worth folding into the skill: the packet's "deferred residual" (condition 4 custody sweep) caught the ruling's disk-shape miscalibration — mechanically-assembled packets should list UNSWEPT evidence explicitly so rulings defer rather than assume; and R5a-style "real-shape regression outranks prose" is a strong convergence device.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:305:- multi-stream-worktrees: c3 worktree for the commit-3 impl; subagent correctly refused in-worktree `git commit` (gitdir not writable under sandbox) per the skill's lead-commits-at-the-gate rule — skill text validated by an independent rediscovery.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:311:- codex-delegation: TWO field notes. (1) codex-run-v3 interface: out-file is POSITIONAL first, WRITE_SCOPE must ALSO appear as a literal `WRITE_SCOPE:` line in the prompt — two failed launches from guessing flags; read usage() first. (2) Envelope protocol failure (ACCEPTANCE_FAILED, report file never written) on an otherwise-complete xhigh implementation — work held uncommitted as untrusted per contract; disposition recorded in run-report §9.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:312:- consistency-sweep: delegated post-merge (Sol xhigh read-only), findings-only brief with tonight's SHAs pinned.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:315:- codex-delegation §escalation + §effort-tiers: heavy use. Three parallel Sol streams (D100-BII, MINT-GENERALIZE, CAL-BRACKET) each run impl→audit→fix→delta as separate xhigh sessions; consumed via envelope + git diff only. KEY DISCIPLINE WIN: on CAL-BRACKET's REPEAT-signature delta failure, ran a read-only design CONSULT (scout genre) instead of a blind round three — the "consult not round three" rule caught that F3 was decision-level (D-102 silent on the trigger mechanism), not a bench fix.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:316:- adversarial-review §severity-tiers + §distinct-lenses: every stream's audit fanned findings, verified proportionally; fix rounds each got a FRESH-thread delta re-audit (never delta-only where the surface had failed twice).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:317:- council §cold-gate (rule 11 full shape): TWO cold gates on the b-ii nested closure (gate 2 → D-107; gate 3 → STOP). Cold Fable instance + Opus contract-lens refuter, mechanically-assembled packets. Refuter layer amended/overturned at BOTH (6 consecutive gates now). Gate 3's decisive finding was STRUCTURAL (grammar constrains values not list cardinalities; ~1.2KB numeric residual) — a fresh-thread depth the cold Fable instances did not reach, vindicating the cross-model pairing.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:318:- council §when-to-stop / rule-11 magistrate accountability: the session's defining call. D100-BII hit its THIRD formulation failure + a proof that clause (c) cannot meet its predicate by any bench work → STOPPED the loop, escalated to Ed (D-108), did NOT spin round four. This is the exact disposition rule 11 exists to force; recorded in C-041 as evidence the topology holds when the loop-immersed agent chooses to stop.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:319:- PACKET HYGIENE (self-correction): the refuter recorded 4 hygiene findings against my gate-3 packet (selective clause quotation; flags not quoted in full incl. the blocking anti-round-3 one; a laundered over-refusal number; wrong-population census). Adopted the standing correction: quote governing clauses to the period; quote every source flag in full including ones cutting against my proposed disposition; census the license-surface population, never a convenient superset. Same class D-106/D-107 already flagged — this recurs, watch for it.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:320:- codex-delegation field note: `--write-scope` strict mode still trips "nested repositories" on stale .claude/worktrees/* — for read-only sweeps, drop the flag and use `-s read-only`. Also: the codex models-cache bug (missing supports_reasoning_summaries) is FIXED (cache moved aside, refetched) — but note SEVERAL xhigh runs this session still showed ACCEPTANCE_FAILED with a COMPLETE report inside; the envelope-write quirk persists intermittently even post-fix, so always check the .md body, not just the .status.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:321:- consistency-sweep + operation-loop §bookkeeping: end-of-session sweep delegated (Sol xhigh, findings-only, tonight's SHAs pinned); council/kernel/RUN_STATE refreshed; two ED-DECISION-PENDING blocks (D-108, D-109) at the top of RUN_STATE as the durable handoff.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:323:## 2026-08-03 16h runway (Fable magistrate, harness-switch checkpoint)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:324:- codex (skill + codex-run-v3): ~10 sessions — 2 impl xhigh, 2 fix
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:325:  rounds xhigh, 4 audits/deltas xhigh, 1 docs xhigh, 1 hygiene high;
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:326:  MCP discussion lane for the D-108/D-109 debate (2 rounds) + 3-question
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:334:- council §cold-gate: winB STOP gate (cold Fable + Opus refuter,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:336:  instances worked; subagent background-probe death pattern recorded.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:341:- NEW pattern (Ed-validated): concurrent read-only Fable audit during
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:345:## 2026-08-05/06 12h autonomous marathon (Fable magistrate; owed entry, assembled 2026-08-07 by the successor from RUN_STATE + traces)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:346:- codex-delegation §effort-tiers + §Invoke: heaviest session on record (~
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:348:  Ed restored high/xhigh per complexity; fast tier implemented per Ed's
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:349:  exact spec (per-call CODEX_SERVICE_TIER=fast via scripts/codex-bridge
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:356:  flagship catch to date — split verdict (fresh-Fable PROCEED / Sol xhigh
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:362:  round-3 fix rounds; both consult-adopted shapes then closed the class.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:375:  Sol session (prefill-contrast feasibility, high effort — no xhigh
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:10:reports — and prose summaries drift the moment work moves fast. One delegated
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:11:sweep (Opus, ~50–80k tokens, a few minutes) has repeatedly found 5–10 real
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:12:inconsistencies that both the lead and a peer reviewer then independently
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:18:lens UNLESS the sweep needs harness access — this sweep usually does (it
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:19:must RUN the test suite and git commands for ground truth), so a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:20:Claude-family agent (Agent tool, `model: "opus"`) is the justified default
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:21:here; use a Codex read-only lens only for a docs-only sweep with no
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:28:   `~/.claude/skills/`, include those SKILL.md files — inter-skill drift is
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:33:2. **Ground truth first:** have it RUN the commands that produce canonical
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:56:program restructure) run a verification round BEFORE its commit, in
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:60:read-only lenses over the uncommitted diff —
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:68:LENS INSTRUCTION EARNED THE SAME DAY: for any decision-gate/threshold
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:3:description: Token-tiered adversarial review workflow — scout a review packet, fan out review lenses, verify findings proportionally to severity (blockers get 2 refuters, nits get none), with fresh read-only Codex refuters by default (Opus on demand for judgment-heavy verification). Use when reviewing a diff, an adapter, or a sub-agent's implementation before landing it.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:17:   sections. Hand the packet to every reviewer; don't let N agents rediscover
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:19:2. **Lenses (parallel; default executor: fresh read-only Codex 5.5
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:22:   labor): 2–4 lenses with DISTINCT perspectives (contract compliance /
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:24:   Distinct lenses catch failure modes redundant reviewers can't.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:30:   so it is independent even of another Codex lens's finding.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:31:   Claude-family/Opus refuters remain AVAILABLE at lead discretion for
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:45:   2026-07-08, two review rounds): the strongest refutations RAN the thing —
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:52:   calibration data — a lens with a high refutation rate needs a better
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:62:the lead judges only the verdict list. Two additions to the lens set:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:63:- a **staleness lens** — a claim can be TRUE at authoring time and FALSE
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:66:- a **self-provenance lens** when the document describes its own history
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:69:  codex-delegation §Token-efficient consumption. This lens produced a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:71:Ground the fact-check's canonical numbers by RUNNING the commands (test
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:74:## Severity rubric (keep lenses consistent)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:92:  §Economics); the packet still pays for itself by keeping every lens
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:94:  Claude-side reference point (historical): 3 lenses ≈ 100–150k tokens with
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:99:- **Delta re-audit after EVERY fix round.** Twice this arc a fix round
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:102:  fix delta caught both. Fix rounds are first drafts, not closers.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:103:- **Blocker refuter pairs get DISTINCT lenses (contract-authority vs
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:107:  better than either verdict alone. Never resolve a split by majority —
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:111:  (prevented over-fixing); the refutations killed convergent two-lens
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:120:## D-078 close-out amendments (2026-07-22; 3 lenses + 11 refuter runs)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:133:  lens correctly flagged two out-of-scope edits as blockers — both were
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:134:  the LEAD's own authorized bench edits made in the same tree. A lens
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:138:- **False-positive economics held**: of 9 lens findings this session, 3
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:141:  blocker two prior audited rounds had missed. The tiered-refuter spend
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:144:## C-033 pairing amendments (2026-07-25; PR #85 gauntlet, 4 audit rounds + 3 refuter rounds)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:146:- **Default blocker-refuter shape is now the CROSS-MODEL pairing: Opus 5
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:147:  contract/design lens + Sol execution lens** (Ed-directed A/B, validated
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:148:  across three rounds — changed the triage outcome in every round it ran:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:150:  they landed, and produced one blocker the auditor never saw). Model
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:151:  diversity stacked on lens diversity catches what either alone misses.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:152:  Ed's cost order (2026-07-24): Sol ~free, Opus ≈ half Fable; use both
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:154:  ledger read — that measured Opus as a REDUNDANT lens, not a distinct one.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:155:- **Effort ruling (C-033): in the paired-lens shape, `high` is the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:157:  high; reserve `xhigh` for single-refuter verification or standalone
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:158:  judgment-dense audits. (The old "xhigh refuters by default" applied to
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:159:  same-model pairs.)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:161:  rounds 1-2 only 3-4 of 7 blocker-tier claims survived refutation at
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:163:  re-pricing, and never fast-track a fix on the auditor's tier alone.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:166:  (effort tiers, counts, a non-green gate). Route council/run-report
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:1:# claude-codex-report/v1 — the lead↔Sol adapter (ADJUDICATED SPEC)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:3:Status: ADOPTED 2026-07-11 (Ed-directed consultation; design by gpt-5.6-sol
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:4:xhigh grounded in six real session reports + the invocation manifest; lead
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:7:(sol-adapter-design.md) and the council log entry for that arc.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:32:## learn.chatgpt.com/docs/prompting — ingested, binding for Sol prompts
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:48:   the session (fix rounds, follow-up questions — precise deltas, not
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:50:   (reviewers, refuters, examiners). Never re-explain context a resumed
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:59:Root causes ranked (Sol's introspection, adjudicated): ambiguous scope
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:80:RUNNER BACKSTOP (codex-run-v3, IMPLEMENTED + INSTALLED 2026-07-11;
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:100:  the model layer: the session self-bounded (blocked+partial,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:102:- RECURRING DEFECT PATTERN (seen twice, p2041 + p2037 fix rounds):
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:103:  newly added path-resolution guards crash on symlink loops
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:104:  (Path.resolve raises OSError/RuntimeError) instead of failing
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:105:  closed. Every delta review of fix rounds that touch path handling
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:106:  must probe unhandled resolve() exceptions; every fix contract for
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:116:the P2-037 no-report incident and the RED round's invented renames):
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:126:Return early with a NEEDS_RULING flag — a resume round-trip is cheap;
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:130:round alongside the scope backstop.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:138:edit-disclose-ask-forgiveness; long ultra sessions get a scope
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:142:**Builder's rule (relayed by Ed, 2026-07-11, from a Codex/Sol builder):**
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:143:"Set bounds — a sandbox the model should operate within; explain how it
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:148:choice. Corollary: when a session runs long or overruns its timeout,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:149:suspect the CONTRACT before raising the timeout — ambiguity is the usual
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:151:TASK bounds because Sol's design freedom is the point there, but even
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:157:# Recommendation: adopt `claude-codex-report/v1`
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:163:- The merge review is only two lines, but its manifest status is `OK` despite a blocker ([report](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-merge-review.md:1), [manifest](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/c028-invocations.jsonl:3)).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:164:- The flake report does not expose suite tails or touched files until lines 78–113 ([report](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-p2038-flake.md:78)).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:165:- The triage report’s three lead rulings do not appear until line 187 ([report](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-p2041-triage.md:187)).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:166:- The status refresh is concise but has summarized, not exact, output and records concurrent baseline movement only at the end ([report](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-status-refresh.md:6)).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:167:- A seventh report arrived during this consultation. It says implementation is done, acceptance is pending, and a required build could not run—an outcome that neither `OK` nor `FAILED` represents ([CI-002 report](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-ci002.md:13)).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:175:  "schema": "claude-codex-report/v1",
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:253:- `clean`: requested outcome complete, required in-session checks pass, no unresolved blocking flag.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:287:| Root cause | `cause`: `confirmed`, `probable`, `unresolved`; `remediation`: `fixed`, `proposed`, `none` |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:297:I would also retire `AFTER-BOOKKEEPING` as a scout verdict. It hides the actual dependency. In today’s scout, P2-047 is waiting for real floor evidence, while P2-048 is waiting for the P1-003 meter decision—not “bookkeeping” ([matrix](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-hardening-scout.md:10)). Encode the concrete IDs under `wait_for`.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:336:Only unresolved items, keyed to flag IDs.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:372:The lead’s six-part contracts are visible almost verbatim in the scout’s delegation blocks: Task, Inputs, Deliverables, Verification, Constraints, Report ([example](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-hardening-scout.md:115)).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:377:ADAPTER: claude-codex-report/v1
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:399:- <only decisions the model must not reopen>
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:410:| Inputs | Compress to baseline and governing authorities. General background and neighboring project history are noise when the repository contains them. |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:461:- Existing model, effort, sandbox, cwd, output, and timestamps
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:466:- `invocation_state`: `ok|failed|timeout|cancelled`
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:483:- Model token usage when available
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:541:5. May grouped triage/scout verdict arrays make the JSON envelope larger than routine headers? (**Yes, capped around 8 KiB; machine-actionable decisions are worth more than a cosmetically tiny header.**)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:3:description: Delegate implementation and peer review to the local OpenAI Codex CLI (gpt-5.6-sol via codex-run-v3; envelope contract, WRITE_SCOPE enforcement, effort tiers) — invocation, prompt contract, sandbox limits, and token-efficient output consumption. Use when handing a scoped implementation or counterreview task to Codex, in any repo.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:6:# Delegating to Codex (gpt-5.6-sol era; see §Effort-tier policy + ADAPTER.md)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:8:> Model history: gpt-5.5 through 2026-07-09; gpt-5.6-sol ("Sol") since.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:9:> Older sections say "5.5" where history-accurate; doctrine sections are current.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:13:Repo-local bridge when present (`scripts/codex-bridge new|resume --last|review`)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:15:`codex-run <outfile> -C <repo> -s workspace-write "<prompt>"`.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:21:`~/.local/bin/codex-run` is the ONE stable mechanism for running Codex from
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:24:exactly ONE reliable wake signal — **a background Bash command exiting
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:26:(bare bridge call returns to the shell / agent ends its turn narrating "I'll
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:27:await" → nothing exits → nothing wakes). `codex-run` wraps a single Codex call
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:28:so it ALWAYS exits (pure-bash watchdog timeout — macOS has no `timeout`; a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:34:1. `codex-run <out.md> [--timeout SEC] [-C DIR] [-s SANDBOX] [--resume] <prompt>`
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:35:   launched as ONE `run_in_background: true` Bash call.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:38:3. On re-invocation read the status file (OK / TIMEOUT / FAILED rc=N) then
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:44:**Timeouts are hang insurance, never work budgets (Ed, 2026-08-05).**
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:45:Size the `--timeout` generously to the unit (a bound a healthy run
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:46:would never hit); a TIMEOUT status is a verdict on the UNIT SIZE or a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:48:multiple Sol sessions (or a Workflow fan-out) and relaunching, not by
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:49:accepting the timeout as failure and not by silently rerunning the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:53:Parallel fan-out = N background `codex-run` calls, one out-file each; you wake
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:60:deterministic FAN-OUT + VERIFY (lenses → severity-tiered refuters, structured
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:63:out-file parsing for multi-finding rounds. codex-run remains THE mechanism for
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:69:exec`/bridge call without codex-run (reintroduces both footguns); multiple
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:70:codex-run launches batched in one shell for-loop — multi-line prompts break
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:72:(bit twice 2026-07-09) — one codex-run per Bash call, parallel calls in one
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:75:Orchestrator prompts must mandate codex-run (multi-stream-worktrees points
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:76:here). For the repo bridge (`scripts/codex-bridge`), wrap it the same way or
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:77:prefer codex-run directly; the bridge's `resume --last` maps to `codex-run
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:82:1. The guaranteed-wake property holds for the MAIN LOOP only — subagent
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:83:   orchestrators are NOT re-invoked by their codex-run children's exits; the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:86:2. `codex-run --resume` forwards cwd (via `cd`, which also scopes `--last`'s
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:89:   resolves OUT to an absolute path, and stamps a thin-output warning into
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:131:   consistently the highest-value output.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:145:- **`FIX-N` numbered fix contracts** for repair rounds — number, exact
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:147:  highest-cleanliness implementation shape observed (7/7 one-shot).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:148:- **Lens prompts name an angle** (bug / contract / tests / regression /
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:152:  resolution, CLI flow, strict validation, provenance, or external APIs,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:158:- **Stack/scope context for reviewers**: tell lenses which layer/unit
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:160:  reviewers about stacking — the two loudest false blockers were both
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:161:  missing-context, not model error.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:169:**Model-version scoping (standing, pre-upgrade 2026-07-09):** calibration
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:171:observations of a MODEL VERSION. After any Codex model upgrade, run one
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:178:symptom-level failure diagnosis; lens-findings→FIX-N aggregation with
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:188:- `codex-run --resume` forwards cwd and sandbox; `codex exec resume` itself
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:211:Do NOT read the bridge transcript/log — it echoes every diff 2–3×. Read only
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:212:the final message (`.codex-bridge/last-message.md` or the `-o` outfile), and
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:213:review the actual code via `git diff` yourself. This cuts per-round main-loop
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:220:**`.status` OK ≠ thorough.** A lens can exit OK with a thin, shallow answer
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:226:**Instant completion = launch failure.** Any codex-run that completes within
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:231:**Killing in-flight rounds is cheap and safe by design** — watchdog + durable
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:232:out-files mean `pkill -f "codex exec"` yields a bounded FAILED/TIMEOUT with
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:234:waiting rounds out; tell orchestrators the FAILED status is expected so they
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:244:Codex does ALL reading-heavy volume work — bug-hunt lenses over whole modules,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:250:alone surfaces load-bearing facts (model, sandbox, approvals). Computer-use
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:255:has higher-resolution image analysis than the lead's inline screenshot reads,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:258:MANY images per round rather than the lead reading screenshots one by one.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:259:`codex-run` forwards `-i/--image`. The lead still makes the design DECISIONS
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:264:Fable owns the apex: ALL high-level orchestration and the FINAL REVIEW of
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:266:is a Fable-level judgment pass over the final diff, informed by Codex lenses
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:267:but never outsourced to them. Thin ≠ rubber stamp: Fable doesn't re-derive
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:269:decide. Also Fable-reserved: live/hardware verification, merge decisions,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:275:Security-shaped work is a Codex specialty, not a Fable one (Ed, 2026-07-07).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:283:test-audit stream this correlated with the ORCHESTRATING model being
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:290:- **Keep the orchestrating model at abstract altitude:** refer to findings
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:296:  vuln-enumeration task and design for it: the smart-model role is the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:301:0. FAILED-TEST TRIAGE (Ed, 2026-07-07): when any test fails, Codex 5.5 gets
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:303:   diagnoses why and implements the fix. Escalate to Fable-level debugging
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:304:   only after Codex fails twice. Fable still verifies the fix and holds the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:307:   Codex TEST-AMPLIFICATION round writes edge-case coverage beyond them.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:308:2. Writer ≠ reviewer — a FRESH read-only Codex instance reviews all tests
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:311:3. Periodic repo-wide Codex test audits (parallel bug-hunt lenses per
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:318:Codex gpt-5.5-high usage is near-limitless — treat Codex rounds as free and
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:320:delegated) is the default, plus counterreview of the reviewer's findings
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:332:### Effort-tier policy (Ed, updated 2026-07-12; gpt-5.6-sol era)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:334:- **`--effort ultra` ONLY when the Sol session itself needs to spawn
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:335:  subagents** (spawn_agent-capable multi-part work inside one session).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:337:- **Individual tasks start at `high` by default** for bounded/mechanical
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:338:  work, docs/config, straightforward implementations, named FIX rounds, and
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:340:- **Use `xhigh` only for named hard-task triggers:** design-bearing decisions,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:343:  cost of an incorrect answer is material. When uncertain, start `high` and
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:346:  keep widening the scope handed to a single xhigh session until the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:349:  field notes below and back off one notch. Sol is dirt cheap; the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:355:- **Usage-pressure mode (Ed, 2026-07-11): ULTRA is the dominant quota
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:356:  consumer; xhigh/high are comparatively cheap.** When Ed flags usage
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:357:  pressure (or monitoring shows it), STOP launching ultra sessions for
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:358:  the stated window and shift the fleet to break-mode work: Sol
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:359:  high/xhigh CONSULTANCY and SPEC DESIGN for future tasks (design
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:362:  ends or Ed clears it. Check usage before any ultra launch once
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:365:  composition, whole-project 7-lens reviews, and 100x-loop flake
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:366:  root-causes have all returned prod-quality at xhigh. No xhigh
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:370:### Adapter: claude-codex-report/v1 (ADOPTED 2026-07-11)
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:372:The report/prompt/manifest contract between lead and Sol lives in
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:379:codex-run-v3 is INSTALLED (2026-07-11; ~/.local/bin/codex-run-v3;
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:384:the envelope; append run_consumed events with `codex-run-v3 consume`.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:393:- ALWAYS pass `--effort` explicitly. The wrapper passes through
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:394:  `~/.codex/config.toml` `model_reasoning_effort` when the flag is
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:395:  omitted — a leftover `"ultra"` there ran 13 consecutive C-029
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:396:  invocations at unintended ultra (rule-10 violation, weekly quota
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:403:  outage preserved a 206k-token fix round's completed work; prefer
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:406:  report may never arrive — the WORKTREE is the ground truth).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:408:Invocation gotcha (2026-07-11): `codex-run -C <dir>` requires a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:412:v3 field notes (D-077 fix-round arc, 2026-07-18):
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:414:- **xhigh `--genre review` sessions ended with `last_agent_message:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:418:  `scripts/codex-bridge resume <session-id>` with "emit the final report
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:420:  (2026-07-18, Ed-requested): codex-run-v3 now auto-runs ONE bounded
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:424:  wrapper: `~/.local/bin/codex-run-v3.bak-20260718`. Still add an "emit
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:432:  reviewers' git-status self-reports plus lead-side `git status` both
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:444:  compliant Sol session AND evicted the run from the pending-scope resume
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:448:  `scope_violation_paths`), then treat the preserved worktree as ground
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:451:- The xhigh review-genre null-final-message mode (2026-07-18 note) can
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:453:  `scripts/codex-bridge resume <session-id>` + "emit the report from work
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:457:v3 field note (Fable resume session, 2026-08-05):
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:481:  stale `.claude/worktrees/*` from other sessions trigger it, and they may
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:488:- Effort-tier evidence: paired distinct-lens refuters at `high` beat the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:489:  old single-lens-xhigh default (C-033 ruling; detail in
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:490:  adversarial-review §C-033). Implementation rounds with pre-verified fix
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:491:  shapes also ran clean at `high` — reserve xhigh for design-bearing
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:492:  fix rounds where Sol must make the calls.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:499:  use N `codex-run` calls with `-s read-only`, one out-file each, or the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:501:  use bare `codex exec`. No writes → no clobbering; fire 3–5 lenses
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:506:- **Parallel IMPLEMENTATION (writes) — needs isolation:** concurrent
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:507:  writing sessions in one tree clobber `.codex-bridge/` state and the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:508:  working tree. Give each stream its own git worktree (the bridge resolves
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:512:  already reviewed in isolation); include a full suite run in the prompt.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:516:- **Dual-prior design rounds beat single design rounds** (2026-07-07 session,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:517:  all observed) for contract-pinning work: two parallel read-only lenses given
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:522:- **History-vs-live boundary:** review lenses asked for staleness/consistency
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:535:- **Self-describing documents need a fresh counterreview.** When a model edits
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:536:  its OWN prior review/critique artifact, the highest-risk claims are the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:539:  implementer AND lead initially under-weighed it; a fresh read-only 5.5
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:543:- **Bridge-v1.1 design consult scorecard (2026-07-13, JouleWise):** a single
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:544:  xhigh MCP discussion-lane consult over the bridge contract returned 5
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:546:  receipt-anchored digest; per-call effort field over env-only; per-objective
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:549:  (duplicate BRIDGE_REPORT_V1 sentinel on the protocol-deviation path) that
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:550:  the lead's own full read had missed. Sol design wins column grows; the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:552:- **codex-run-v3 preflight gotchas (2026-07-13):** `--write-scope` requires a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:554:  array, separate from a BRIDGE_TASK_V1 header's object form); strict-scope
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:555:  runs refuse nested repositories (remove stale `.claude/worktrees/*`
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:566:- **codex-run-v3 DETACHES under Claude Code background tasks** — a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:567:  `run_in_background` shell launching it exits in seconds (0-byte
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:571:  pattern now: every brief that delegates to codex-run includes, up
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:577:  long unresolved waits by narrating predicted refuter verdicts (both
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:581:- Staged-commit xhigh implementation (7 resumed sessions, one commit per
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:586:  found; effort-tier §: keep pushing.

exec
/bin/zsh -lc 'nl -ba /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     1	# Skill-usage log (cross-session)
     2	
     3	Standing instruction (Ed, 2026-07-08): every complex/orchestrated session logs
     4	which skill sections were USED, SKIPPED (with cause), or DEVIATED from (with
     5	what replaced them), plus improvement candidates — evidence for evolving the
     6	custom skills. One entry block per session, newest first. Feeds operation-loop
     7	§10 meta-review; distillation into the skills themselves stays governed by §9
     8	(same-session folds, one-fact-one-home).
     9	
    10	Row format: `skill §section | verdict (USED/SKIPPED/DEVIATED/GAP) | evidence/what happened | improvement candidate (or —)`
    11	
    12	Logging discipline: CHECK THE SKILL BEFORE LOGGING A CANDIDATE — a
    13	2026-07-08 candidate duplicated a rule the skill already held; the log is
    14	for gaps, not for what a busy session failed to look up.
    15	
    16	---
    17	
    18	## 2026-07-08 — suite-science hardening + benchmark expansion (JouleWise; C-014/C-015)
    19	
    20	Session shape: design-council-heavy; mid-session scope additions (reach review,
    21	expansion council, worktrees, ultracode); 3 streams (L docs / C capture / S
    22	sentinels); first session mixing codex-run with Workflow-tool orchestration.
    23	
    24	| skill §section | verdict | evidence | improvement candidate |
    25	|---|---|---|---|
    26	| operation-loop §0 intake | USED (skip-path) | user named the task; still read RUN_STATE/queue/decision-log first — caught the D-034 gate interaction early | — |
    27	| operation-loop §1 decompose | USED + GAP | started single-stream (correct); Ed's mid-session directives forced re-decomposition to 3 streams — the skill has no mid-session re-decomposition guidance (when scope grows, re-run §1 explicitly) | add one line to §1: re-run decomposition on scope addition; new streams get their own tier |
    28	| operation-loop §2 setup | USED + NEW FAILURE MODE | worktree per code stream, disjoint footprints held; BUT codex sandbox cannot commit in worktrees (shared `.git/worktrees/<wt>/index.lock` is outside the workspace-write sandbox) — hit twice, both streams | fold into multi-stream-worktrees: codex streams must NOT attempt commit; lead commits at the gate; say so in the stream prompt |
    29	| operation-loop §3 model assignment | USED + DEVIATED | codex volume + Fable gates held; ultracode added Workflow-tool orchestration with agentType:'codex' agents — NOT the codex-delegation "one stable mechanism" (codex-run), and it worked well: structured-schema findings, deterministic refuter tiers, zero stalls | codex-delegation needs a §: when to wrap codex in Workflow (fan-out + verification tiers + structured output) vs raw codex-run (single long impl unit, bounded-exit wake) |
    30	| operation-loop §4a design round | USED, high yield | invited design judgment overturned lead designs twice (4x3 Q4 grid; two-window plan) — third session running this pattern pays | — |
    31	| operation-loop §4c counterreview lenses | USED (via Workflow) | adversarial-review shape preserved inside workflow scripts; severity-tiered refuters (2/1/0) | — |
    32	| operation-loop §4d test amplification | DEVIATED | no separate amplification round; structural test additions were folded into the review-fix round (stream S: +6 methods from writer≠reviewer findings) — cheaper, same coverage effect this time | consider: allow §4d to merge into the fix round when the test audit (§4e) drives it |
    33	| operation-loop §4e writer≠reviewer test audit | USED, unique catches | caught "+assertions, zero new test methods" anomaly (stream S) and the 596→597 plausibility question (stream C, pending) | — |
    34	| operation-loop §5 live verification | USED (held the line) | real-corpus strict validation had to run LEAD-side: worktrees lack gitignored runs/ corpora — subagent streams cannot self-verify against untracked data | fold into multi-stream-worktrees: name "untracked-data verification" as a lead-gate item when worktree streams touch validation-bearing code |
    35	| operation-loop §7 fleet health | USED (nothing to do) | zero stalls across ~15 codex-runs + 3 workflows; bounded exits + workflow notifications made heartbeats unnecessary (consistent with C-010) | — |
    36	| operation-loop §8 bookkeeping | USED + NEW PATTERN | pre-commit docs-verification workflow (faithfulness/coherence/claim-trace lenses + refuters) over the C-015 batch caught 1 BLOCKER + 6 should-fixes including decision-log record drift the lead authored | fold into consistency-sweep: a pre-commit docs-verify mode for large landed doc batches (vs the existing end-of-session sweep) |
    37	| operation-loop §9 distillation | USED | this log + planned end-of-session folds | — |
    38	| council (triggers, C-014/C-015) | USED | contract-bearing suite design → full tier, correct; two full entries + index rows; deliberation traces with position reversals recorded | — |
    39	| council (5.5-reviews-consequential-decisions) | USED, high yield | peer counterreview of both synthesis packets; C-015 peer added the per-item failure-economics catch nobody else saw | — |
    40	| codex-delegation (six-part prompt contract) | USED | all ~15 invocations; pinned-spec prompts kept fix rounds one-shot | — |
    41	| codex-delegation (token-efficient consumption) | USED | out-files + final messages only; no transcript bridging; workflow agents returned structured schemas | — |
    42	| adversarial-review (severity-tiered refuters) | USED (via Workflow) | refuters REPRODUCED defects live (one regenerated configs with pre/post scripts to prove silent sentinel omission) — repro-based refutation is the gold standard | add to adversarial-review: refuter prompts should invite reproduction, not just code reading |
    43	| multi-stream-worktrees (topology) | USED | lead-driven, no orchestrators, stream-state table in scratchpad trace notes | commit-sandbox + untracked-data items above |
    44	| consistency-sweep | PENDING | scheduled before final bookkeeping commit (docs-heavy session, multiple skill edits expected → include ~/.claude/skills in scope) | — |
    45	
    46	Unused this session (no trigger, correctly): multi-stream Opus orchestrators,
    47	STALLED-handback, heartbeat backstop, worktree isolation inside Workflow calls.
    48	
    49	### Folds APPLIED at session close (2026-07-08) — staged mid-session, held
    50	### per Ed's full-evidence instruction, re-applied after ALL runs completed
    51	### (6 workflows + oversight + research + integration review). Late evidence
    52	### sharpened three: fold 1 became a general state-the-sandbox-tier-limits
    53	### rule POINTING at codex-delegation caveat 3 (which already owned the
    54	### commit-block mechanism — one-fact-one-home caught the near-duplicate);
    55	### fold 2 gained the full run totals; fold 4 gained the test-gate-logic-
    56	### against-a-true-null lens instruction (AP-4, caught by oversight AFTER
    57	### docs-verify passed it). Original staged text follows:
    58	1. multi-stream-worktrees §Constraints: codex-cannot-commit-in-worktree rule.
    59	   (The untracked-data candidate was ALREADY covered by the existing
    60	   worktrees-share-tracked-files-only bullet — logging miss, not skill gap;
    61	   calibration note: check the skill before logging a candidate.)
    62	2. codex-delegation §Monitoring: Workflow-wrapped codex as the ONE sanctioned
    63	   alternative to codex-run, with its trigger condition (deterministic
    64	   fan-out+verify with structured findings) and its non-triggers.
    65	3. adversarial-review §3: refuter prompts invite REPRODUCTION.
    66	4. consistency-sweep: new §Pre-commit docs-verify mode (3 lenses + refuters
    67	   over uncommitted large doc batches; distinct yield from the sweep).
    68	5. operation-loop §0/§8: primary-object-level-deliverable sentence at intake
    69	   + shipped-check at bookkeeping (Ed's catch — the session's biggest
    70	   process lesson); §1: explicit mid-session re-decomposition rule.
    71	Also: session-mid additions — Ed's skill-usage-logging standing instruction
    72	itself was wired into operation-loop ✎ intro + memory the hour it was given.
    73	
    74	### Late-session evidence (post-staging; completes the fold evidence base)
    75	- Workflow totals: 6 workflow runs, ~60 agents, ~2.3M tokens, zero errors,
    76	  zero stalls; refuter precision held (~2 refuted / ~30 confirmed serious).
    77	  Strengthens fold 2 (Workflow-wrapped codex) — evidence now spans review,
    78	  verification, oversight, AND research shapes.
    79	- Oversight round validated the merge-order-simulation reviewer role
    80	  (conflict-free proof + semantic stale-line list + order rationale) and
    81	  caught a pre-registration logic bug (AP-4 unfalsifiable null) in a
    82	  CONTRACT the docs-verify round had already passed — layered doc review
    83	  has non-overlapping yield at contract-logic altitude (new evidence for
    84	  fold 4's docs-verify mode: add a "test the gate logic against a TRUE
    85	  null/extreme case" lens instruction).
    86	- Final-head passes: read-only codex sandbox cannot run the suite (no
    87	  writable temp) — final-head prompts should either grant workspace-write
    88	  with a temp dir or explicitly state the lead runs the suite (evidence
    89	  for fold 1's sandbox constraints; generalize: state each sandbox tier's
    90	  capability limits in the prompt).
    91	- Ed's object-level catch (suite content vs contracts) — evidence for
    92	  fold 5 (§0 deliverable sentence + §8 shipped-check).
    93	- New failure mode logged: lead used system python3 for a live MLX gate →
    94	  runtime_unavailable; repo venv (.venv/bin/python) was required. Candidate
    95	  for the project verify/run docs rather than global skills (repo-specific).
    96	
    97	### Post-large-workload meta-reassessment (2026-07-08, first run — now the
    98	### standing §10 final step per Ed)
    99	Shape: 4 parallel analysts (council-mine, decision-mine, skill-audit,
   100	cold-start derivability) + completeness critic; Workflow-orchestrated.
   101	Headline yields: supersession drift identified as THE unfolded recurring
   102	failure mode (~70% of accumulated doc defects; now D-043 + op-loop §8
   103	write-time rule + sweep check 5); operative merge-authority contradiction
   104	(council skill would have told a fresh agent to wait for Ed — fixed);
   105	5 one-fact-one-home divergences fixed (V1-V5); codex-delegation
   106	structurally rewritten (procedure-first, history to appendix);
   107	multi-stream frontmatter de-staled (lead-driven default); repo-side
   108	derivability closed (scripts/codex-run committed; orchestration.md
   109	refreshed + pointer map; playbook M0 routes to the process layer;
   110	CLAUDE.md machine-local reference fixed; decision index regenerated;
   111	fired revisit clauses back-annotated D-031/D-034/D-039/D-041).
   112	Critic's unanswered-question set (spend-per-catch trend,
   113	calibration-ledger longitudinal, disposition-to-commit closure,
   114	layer-overlap) encoded as §10 reassessment checklist items (b)-(e) so the
   115	next large session answers them by default.
   116	New codex constraint discovered during execution: codex refuses untrusted
   117	non-git working dirs (-C must point at a git tree; skills dir launch
   118	failed rc=1 with empty stderr) — folded into codex-delegation §Prompt
   119	contract constraints.
   120	
   121	### Suite-build session (2026-07-08, adjudication + P2-010a/b + P2-012/P2-020)
   122	Skills used: operation-loop (§0-§9 full pass; §0 deliverable sentence
   123	prevented a repeat of the contracts-not-code miss — the sentence was
   124	checked at close and the code SHIPPED); codex-delegation (§Invoke ~30
   125	codex-run sessions, zero wake stalls; §read-only parallel lenses;
   126	§caveat-3 no-commit honored in every worktree prompt; six-part contract
   127	throughout); multi-stream-worktrees (3 worktrees; stacked-branch
   128	variant); adversarial-review (shape borrowed for the adjudication attack
   129	round + severity-tiered oversight).
   130	Deviations/lessons:
   131	- Ed directive mid-session: max-Codex, Fable high-level only —
   132	  adjudication DRAFTING moved lead→codex (invited judgment) and ran
   133	  excellent; validates the design-freedom-runs-hot calibration signal.
   134	- Codex quota outage (~1h): degraded mode = lead line-reads + ONE Opus
   135	  fresh-eyes lens (caught a real FakeClock-blind refactor regression) —
   136	  Opus-as-outage-substitute is a usable pattern; no layer skipped, the
   137	  oversight gate waited for quota. Probe-first on resume (Ed upgraded
   138	  the account; the 15:12 wait was unnecessary).
   139	- NEW FOLD (multi-stream-worktrees): stacked-PR bases do NOT auto-
   140	  retarget on parent merge (only on branch deletion); gh pr merge on a
   141	  still-stacked PR merges into the parent branch. Cost: one recovery
   142	  promotion PR (#20).
   143	- Prompt-defect log: lead-pinned test expectations must be re-derived
   144	  from the spec (streamB cross-level identity error — codex correctly
   145	  preferred the report); "no caller passes X" review criteria must
   146	  exempt negative tests.
   147	- Live-gate yield stays decisive: 3 live-only catches (cwd refs, strict
   148	  rollup, sampler API namespace) invisible to 680+ tests and 9 lenses —
   149	  hard rule 1 re-validated a third consecutive session.
   150	
   151	## 2026-07-08 — JouleWise C-018 (D-013 alignment-capture fix, PR #21)
   152	- council: tier selection §used (solo impl + light cross-model review for a small timing-semantics change; no full council per rule 3). Council-log entry recorded (C-018).
   153	- codex-delegation: §review-consumption used (final message + diff only, via codex subagent driving scripts/codex-bridge review; one resume to get format compliance). Implementation NOT delegated — 2-line reorder, delegation would cost more than doing (token-economics call).
   154	- adversarial-review: not invoked (single pre-identified finding; verification was lead-side test-fails-pre-fix proof instead of refuter fan-out).
   155	- Note: regression-test design needed a mock-granularity fix (power_hz override) — the mock's <2-samples fallback was silently masking window geometry; possible future skill note for FakeClock-based window tests.
   156	
   157	## 2026-07-09 — JouleWise CP-5 resume session (Fable lead)
   158	- operation-loop: §0 deliverable sentence written and checked at close; §1 re-shaped twice mid-session (advisor-site scope addition; W-stream shared-file analysis → merged W1-3 into one worktree); §2 lead-driven, zero orchestrators (~35 codex sessions, zero stalls); §4 pipelines resumed at (g) for pre-stop streams; §5 live gates incl. 2 full real-MLX suite runs; §6 run TWICE (two merge waves) — both waves earned it (wave-2 verified regenerated-sidecar pairing); §8 full bookkeeping + sweep; §10 not triggered separately (this WAS the post-large-workload session; reassessment folded into the trace appendix).
   159	- codex-delegation: codex-run bg protocol exact; FIX-N contracts 7/7 one-shot-clean; final-head passes caught 3 blockers+7 should-fixes AFTER lens+fix+lead-gate layers — the layer is load-bearing, keep; 1 PROMPT-DEFECT (lead pinned fail-closed-on-any-existing-file for inferred sidecars; scorer sidecars broke) — lesson: when pinning fail-closed semantics over a namespace shared by MULTIPLE artifact types, enumerate the other residents first.
   160	- adversarial-review: severity-tiered verification applied (lead verified the envgate blocker premise directly in bundle_read instead of spawning refuters — cheaper, same rigor).
   161	- multi-stream-worktrees: 6 worktrees across session; disjoint-footprint check prevented a capture/hashcheck collision (run_campaign.py ownership pinned to #24, campaign-consistency gating deferred).
   162	- consistency-sweep: dispatched with a supersession-closure item (D-047 amendment) per §8.
   163	- NEW OBSERVATION for operation-loop/council: CI merge-ref is an unlisted review layer — it caught a cross-branch interaction (#23 fixtures × #27 strict rules) that NO local layer could see (both branches green in isolation). Candidate fold: when parallel branches add validation rules AND fixtures, run the combined suite locally (merge into a throwaway ref) before pushing.
   164	
   165	## 2026-07-09 — scientific-rigor review session (C-023, review-only)
   166	- operation-loop: §0 deliverable sentence + §1 shape used (review-only → no worktrees, 4 read-only lenses); §2 worktree setup SKIPPED (nothing mutates — correct scale-down); §4 pipeline N/A (no implementation); §5 live-verification gate N/A (no runtime surface); §8 bookkeeping run (review doc + C-023 + RUN_STATE pointers; run report SKIPPED — review doc is the session record, pointer entry in council log); §9 no skill folds needed beyond this row.
   167	- codex-delegation: §Invoke background codex-run protocol 5/5 clean (4 lenses + 1 discussion round, zero stalls, zero thin outputs); §Parallel threads read-only fan-out shape used as designed; §Prompt contract lens-angle + severity + failure-scenario + checks-performed clauses all yielded (every lens delivered structured, citable findings); "send the lead's synthesis back for attack" doctrine PAID AGAIN — D1 overturned a lead-accepted blocker (C5-1.1 already contract-capped) and out-designed the lead's work-plan order. Deviation: none.
   168	- council: convened as user-directed full review (correct tier — research-methodology-bearing); discussion bounded to 1 round (converged); per-layer unique catches recorded in C-023; zero-yield layers: none.
   169	- adversarial-review / multi-stream-worktrees / consistency-sweep: not invoked (review-only, no diff to verify, single stream, docs delta small and hand-checked).
   170	
   171	## 2026-07-09 — spec-fleshing wave 1 (C-024, same session as C-023 review)
   172	- operation-loop: §1 mid-session re-shape used on Ed's go-ahead (review → 4 implementation streams, footprints pinned disjoint, all full-tier); §2 worktrees used (parallel WRITES this time — correct scale-up from the review's no-worktree call); §4 full pipeline per stream (design invited inline, lenses, FIX-N, gates); §5 merge gate ran the full C-010 shape incl. final-head + NEW tail-verification pass; §6 integration review PAID (5 seam catches — S1/S2 written against pre-S3 contracts; no other layer could see it); §8 full bookkeeping + sweep; §8 cadence rule AMENDED mid-session (Ed: per-artifact push, checkpoint pushes) and folded same-session.
   173	- codex-delegation: 20 codex sessions, zero stalls; FIX-N one-shot record now 13/13; instant-completion diagnostic caught 1 real launch failure (zsh parse error on a for-loop of prompts — lesson: never batch multiple codex-run prompts in one shell loop; separate calls); severity-tiered pipeline caught a statistics blocker (percentile-UCB unidentifiable at n=10) that BOTH the lead and the implementer had provisionally accepted — the fresh-lens layer is the quality mechanism for design-freedom delegation.
   174	- adversarial-review: severity shape held (blockers got refuting-quality scrutiny via final-head + tail passes; nits applied without ceremony).
   175	- multi-stream-worktrees: 4 streams, disjoint-footprint pins held (zero collisions); codex-can't-commit-in-worktree constraint handled by lead pathspec commits per caveat 3.
   176	- consistency-sweep: dispatched with supersession-closure item (UCB → false-effect guard floor surfaces).
   177	- council: C-023 pointer→C-024 pointer entry pattern; discussion bounded; history-vs-live rule applied at the FH ledger fix (supersession annotations, not rewrites) — the doctrine prevented promoting a rejected estimator to the decision log.
   178	
   179	## 2026-07-09 — spec-fleshing wave 2, ultracode (C-025, same session)
   180	- operation-loop: §4a design-round-first STRENGTHENED clause (Ed, folded this session) validated immediately — P2-030 memo→ratify-with-pins→implement produced zero design rework; §7 fleet-health check used on a user-reported stall: outside evidence (ps etimes, worktree mtimes, workflow journal) showed healthy-slow not wedged; correct intervention was ADDITIVE streams (S9/S10), not kills — fold candidate: "user-perceived stall → evidence check BEFORE relaunch; reinforce with disjoint streams, never a second writer in a live worktree".
   181	- codex-delegation: FIRST full Workflow-tool orchestration (46 agents, zero stalls, zero errors) — the sanctioned Workflow alternative scales to implement→lens→refute shapes, and its codex WRAPPER agents can git commit+push in worktrees (they are full agents), beating direct codex-run for worktree streams where codex's own sandbox still index.lock-blocks; refuter layer killed 10/30 findings pre-triage (precision working); mutation testing appeared organically in a test-audit lens (5 mutations proving gaps) — fold candidate for §Test doctrine: "test-audit lenses may be prompted to MUTATION-TEST the gates they audit"; FIX-N one-shot record now 22/22; NEVER batch multiple codex-run launches in one zsh for-loop (parse-error launch failure, second occurrence class).
   182	- adversarial-review: severity tiers held; final-head layer caught 2 live-path defects invisible to earlier layers (MLX position under rotation; linter false-negative regression FROM a fix round) — the fix-round-regression hunt is now demonstrably the final-head's highest-yield angle.
   183	- multi-stream-worktrees: 6 concurrent streams peak; combined-ref pre-merge suite check (C-022 lesson) used deliberately for the first time — zero conflicts, validated the p2029×p2030 strict-surface interaction before merge.
   184	- consistency-sweep: dispatched with supersession items (ordering-executability and linter-cut-line surfaces).
   185	
   186	## 2026-07-09 — P2-034 broad campaign packs (C-026, same session)
   187	- operation-loop: §4a design-round-first used as DEFAULT (second validated run: scoping memo → 3 lead pins → zero design rework); §1 single-stream call correct (one dir = one worktree; no false parallelism); §6 integration review correctly SKIPPED (single stream); §8 tree-quiescence rule observed (bookkeeping only after all codex rounds done) — no recurrence of the C-025 defect.
   188	- codex-delegation: 5-session pipeline; compliance lens caught a char-level registry drift the LINTER structurally cannot see (markdown code-span nesting) — lesson: mechanical linting bounds but never replaces the review lens for ratified-wording fidelity; FIX-N 23/23.
   189	- adversarial-review: cold-start test prompt device ("could a lab that has never seen JouleWise run this?") yielded the highest-value executability finding — reusable prompt pattern for runbook reviews.
   190	
   191	## 2026-07-09 — JouleWise C-027 whole-project council review (Fable lead)
   192	- council: §Triggers (user-asked full council), §Session shape B (7 divergent lenses + examiner — shape B's "MORE divergent threads" and final-examiner steps both load-bearing; examiner PASS-conditional caught 7 synthesis defects), §Recording (index row + full entry + deliberation traces), §Roles. WORKED AS WRITTEN.
   193	- codex-delegation: §Invoke (codex-run ×10, zero stalls; one-per-Bash-call rule held), §Prompt contract (all six parts; autonomy clause paid off — 5 unprompted premise corrections), §Direction doctrine (lens-names-an-angle, CLEAN-needs-checks-line both used), §Model-version scoping (FOLLOWED: calibration batch logged, promotion refused pending A/B), §Consume (final-message-only; .status naming), §Economics (counterreview of the lead's synthesis was the round that caught the most). GAP FOUND: skill still titled "gpt-5.5"; model now gpt-5.6-sol behind config — needs a one-line model-note after the sealed A/B.
   194	- adversarial-review: severity-tiered verification idea applied (blockers lead-verified + double-examined; lower tiers accepted on citation quality — the examiner correctly flagged the unaudited lower tiers, worth folding into the skill as an explicit disclosure rule).
   195	- consistency-sweep: delegated sweep run over the close-out branch (in flight at log time).
   196	- Session-level lesson for skills: the REVERSE lens (audit the lead against its own rules) produced 2 of 8 blocker clusters — council skill's reverse-review emphasis validated again; consider making a whole-project reverse audit a standing periodic trigger.
   197	
   198	## 2026-07-11 (JouleWise C-028 continuation: #49 merge, p2041 vetted rebuild, P2-037 fan-out)
   199	- codex-delegation §Invoke/§Prompt-contract/§Economics: 6+ codex-run-v2 sessions (merge review, p2041 diagnosis, deletion triage, flake root-cause, vetted composition ULTRA, p2037 ULTRA, scheduling scout). NEW §Effort-tier policy added (Ed): ultra=subagent-needing sessions only; xhigh/high individual tasks; push xhigh scope until first prod-quality miss and record ceiling. The two ULTRA launches this session predate the policy — going forward they'd be xhigh.
   200	- adversarial-review shape used implicitly (severity-tiered verification of Sol merge-review findings: blocker fact-checked, should-fix verified via reconstructed 3-way merge).
   201	- LESSON (lead-side defect caught by Sol review): `git checkout --ours/--theirs <file>` during conflict resolution takes the WHOLE file, silently discarding the other side's cleanly-auto-merged hunks. Correct tool: resolve marker regions in place, or reconstruct with `git merge-file` per file. Candidate for codex-delegation/multi-stream field notes.
   202	- Session second half: adapter v1 adopted + codex-run-v3/codex-usage built+installed (runner-injected report contracts); scope-restraint 3-layer design (language live, backstop in flight at pause); NEEDS_RULING generalized early-return; design-consult-by-default doctrine (P2-044 first product: corpus-grounded HAC design, 47x variance underestimate found); PRs #49/#54 merged, #50-#53/#55 held; P2-037 second transport-OK/no-report incident (independent audit pattern instead of self-grading resume). Usage data: 1 ultra = 35.3M tokens ≈ 11 xhigh sessions; Fable generation ~1.8M vs Sol ~112M same arc. Paused at C-028 checkpoint #4 (25a8b05).
   203	- C-028 close (2026-07-11 second half): full gauntlet validated end-to-end (~57 Sol invocations, ~16 refuters: 70/15/15 confirm/narrow/refute — narrowings highest-value); integration tree caught 38 pre-merge cross-stream failures; enforcement stack live-tuned (bytecode false-positives → recorded exemption; 3 compliant NEEDS_SCOPE stops with correct-path discovery; nested-repo guard limitation → prompt-scope + lead-diff fallback); v3 defects logged (resume no-op, in-place-edit crash); wave lesson: never trust loop completion banners, verify per-PR state (DNS-blip skip caught). Fable dictated-fills pattern for bookkeeping finalization: agent verified every dictated fact against evidence and caught lead miscounts. Skills amended: adversarial-review + multi-stream-worktrees §C-028; CLAUDE.md rule 9 (gauntlet default) added.
   204	
   205	## 2026-07-12 — C-029 agent-lane triple (SITE-01/P2-049/P2-028; PRs #61-#63)
   206	
   207	- operation-loop §0-§8 walked in order: §0 deliverable sentence, §1 four-stream shape (1 bench + 3 Sol pipelines, disjoint footprints), §2 worktrees, §4 per-stream pipeline (design folded into impl prompts as DESIGN-section requirement — worked well at this scope), §5 lead gates, §8 bookkeeping. §6 integration review SKIPPED (streams not merged yet — deferred to merge wave). Consistency sweep DEVIATION: lead quick-pass instead of delegated sweep (upstream outage); gen_state --check + tests stood in for the counts surface.
   208	- council §Recording: spend-snapshot convention ADDED this session (codex-usage at entry close + Fable triple + composition caveat) and exercised in the C-028 addendum; C-029 index row kept to pointer form (run report owns the trace — v2 discipline held).
   209	- codex-delegation §Invoke: v3 field notes ADDED (WRITE_SCOPE-in-prompt rc=64; MANDATORY explicit --effort after 13 unintended-ultra invocations via config passthrough; thin-output-OK = FAILED; resume-after-outage preserved 206k tokens of fix-round work, worktree = ground truth). §Prompt contract used on all 13 invocations; FIX-N contracts 2-for-2 clean (18-item and 1-item rounds).
   210	- adversarial-review: severity policy APPLIED WITH SUBSTITUTION — 5 blocker claims adjudicated by lead code-reading instead of 2-refuter rounds (cheaper + stronger for mechanically-verifiable claims: 2 confirmed, 1 partially refuted, 1 design ruling, 1 reproduce-first-in-fix-round). Delta re-audit doctrine BLOCKED by upstream outage (3 attempts) — owed pre-merge, recorded in PRs/RUN_STATE. Lead-gate unique catch: capped-cell over-refusal in the fix round (third "fix rounds introduce defects" datum).
   211	- Calibration: design-freedom delegation hot again — site01 shard design (instruction-budget-aware, quantified Base85 rejection) beat the lead's pagination prior; p2028 implementer's F1 catch was half-right (correct defect, wrong correction) — dictated-fills verify-every-fact lesson generalizes to session findings.
   212	
   213	## 2026-07-13 JouleWise restart-close + audit-gate session (Fable lead)
   214	- operation-loop: §0 intake (deliverable sentence), §4 pipeline tail (delta re-audits), §5 lead gates (bench fixes DRA-001/XSI-1 with regressions; live deploy + meter + freshness), §6 integration review (fired at 2 streams; 1 unique catch XSI-1), §8 bookkeeping (run report + C-030 row + kernel/queue retirement + supersession-free), §9 same-session folds (none needed — prior session's folds held). DEVIATION: consistency sweep SKIPPED deliberately — the declared comprehensive audit supersedes it this once; if the audit does not run, the sweep debt stands.
   215	- adversarial-review §C-028 amendments: delta re-audit after fix rounds validated AGAIN (DRA-001 blocker found on a twice-reviewed diff — fourth "fix rounds introduce defects" datum); explicit --effort xhigh on all review sessions (3 sessions ≈ 7.0M tokens vs prior day's unintended-ultra 13 ≈ 118M — ~17x cheaper for equal role).
   216	- codex-delegation §Invoke: v3 wrapper effort passthrough fix held (manifest rows show xhigh); WRITE_SCOPE in-prompt requirement respected in all prompts.
   217	- council §Recording spend snapshot: exercised for C-030 (second use; convention holding).
   218	- NEW LESSON (fold candidate, not yet folded — audit may reshape it): cross-thread collisions in one working tree are now real (Ed runs concurrent threads); the two-writer rule needs a cross-THREAD corollary — before any commit, diff-inventory the tree for foreign changes and verify provenance with the user rather than pathspec-committing around unexplained diffs blindly.
   219	
   220	## 2026-07-13 — Bridge v1.1 max-co-work session (Fable lead, background job)
   221	
   222	- operation-loop: §0 deliverable sentence; §1 single contract-bearing stream (worktrees SKIPPED correctly); §3 default assignments (design consult xhigh MCP, impl xhigh CLI, fix3 dropped to high when triggers lapsed — first non-xhigh round, correct); §4 full pipeline incl. STRENGTHENED design round (lead's spec itself consulted pre-implementation — Sol amended 5 pins and caught a v1 adapter bug; the pre-decision-consult default earned its keep); §5 lead gates (live wrapper dogfood, live reverse consults, flake triage: lead-rerun caught an agent-load flake the worker's green run masked); §8 bookkeeping (run report + C-032 row + D-065 + D-064 tracked manifest — first session to create docs/process_traces/); §9 folds done mid-session (codex-delegation +2 field notes). §6 SKIPPED (single stream), §10 not fired (single-PR).
   223	- adversarial-review: 3 distinct lenses + severity tiering; DEVIATION (recorded in report): round-1 blockers verified by lens-repro + independent lead code-trace instead of 2 fresh refuters; mechanical existence claims lead-verified. The mandatory delta re-audits then caught 3+2+1 fix-round defects INCLUDING TWO CORRECTIONS OF THE LEAD (a lead-graded nit upgraded by auditor repro; a vacuity the lead's own check missed) — the substitution is safe only WITH the delta re-audits behind it.
   224	- codex-delegation §Invoke: v3 preflight gotchas ×3 (WRITE_SCOPE prompt line; nested-repo refusal from a stale .claude/worktrees entry; ignored-cap 10k tripped by .venv → cap now 50k + CODEX_RUN_IGNORED_CAP) — folded same-session into the appendix. Consult scorecard bullet added.
   225	- council §Recording: C-032 index-row-only (run report = ONE home) held.
   226	- consistency-sweep: delegated Sol xhigh, scope included ~/.claude/skills + global CLAUDE.md + new ~/.codex/AGENTS.md (multi-skill-edit rule applied).
   227	- NEW LESSON (folded into trace/report; candidate for operation-loop §5): harness auto-mode can DENY agent self-merge of agent-authored PRs regardless of standing CLAUDE.md authorization — plan merge waves so Ed's merge click is the explicit last step, or run merges in a session where Ed names them.
   228	
   229	## 2026-07-16 — JouleWise resumption + no-hardware batch (Fable lead)
   230	
   231	- operation-loop: §0 intake + deliverable sentence; §1 re-shape fired TWICE on mid-session scope additions (Ed: "work the no-hardware backlog"; Ed: "handle the merge yourself"); §2 worktree-per-stream (4 streams, disjoint footprints held); §3 default assignments (Sol high audits per Ed's ask, xhigh only on contract-bearing SPLIT-AP/AXI-SB, Fable subagent for web verification per rule-9 dictated-fills); §4 full pipeline per stream; §5 lead gates (CI-log verification that a green job actually EXECUTED the new test; AXI-SB live probes lead-run; field-name check before accepting `supported`); §6 integration review fired at 3 streams (0 unique catches — first zero-catch datum for this layer, tally per §10 drop rule); §8 full bookkeeping arc; §10 not fired beyond the tally note.
   232	- Workflow-wrapped codex (codex-delegation sanctioned alternative): 4 audits + 5 refuters via agentType codex + schema — zero stalls; refuters produced 1 severity downgrade + factual narrowings, worth their cost.
   233	- adversarial-review §C-028: delta re-audit after EVERY fix round — paid off with an EIGHTH "fix rounds introduce defects" datum, and the first LEAD-AUTHORED one (the lead's own FIX-1 pin dropped predictor components; the delta pass caught it). Bench-fix threshold used twice; both bench edits got fresh micro-reviews (final-head rule applied to the lead's own edits).
   234	- codex-delegation §Invoke: NEW v3 gotcha (fold candidate → field notes): strict-scope runs REQUIRE the out-file OUTSIDE the worktree (rc=64 "strict-scope artifacts must be outside the worktree") — scratchpad out-files always.
   235	- council §Recording: C-036 index-row-only; run report = ONE home.
   236	- consistency-sweep: delegated (Sol high) before the final bookkeeping commit; scope: session-changed status docs.
   237	- NEW DATA for the self-merge lesson (2026-07-13 entry): with Ed's EXPLICIT in-session delegation ("handle the merge yourself if all is well"), gh self-merge of agent-authored PRs worked (3×) — the prior harness denial applies to standing-authorization-only merges; in-session delegation is the working shape. Also: gh token needed `workflow` scope for ci.yml pushes (Ed refreshed in-session).
   238	
   239	## 2026-07-17 — JouleWise Window-A execution + wrap (Fable lead, continuation)
   240	
   241	- operation-loop full arc across summarization boundaries (task board carried state); measurement/agent strict alternation held; lead-only live measurement enforced throughout (4 shakedown attempts, floors 248-line campaign, exploratory block).
   242	- adversarial-review: delta re-audits caught fix-round blockers twice more (9th/10th data); anti-gaming lenses on BOTH positive (AXI-SB) and negative (AXI-SC) verdicts — negative-verdict honesty (positive-control path) is a new lens angle worth folding.
   243	- codex-delegation new field notes: strict-scope out-file must be OUTSIDE the worktree (rc=64); bare `**` invalid scope entry; forced-report placeholder = thin-output variant (persist-time size checks mandatory); runner exit-0-on-lock-refusal wart (verify progress by artifact counts, not rc); scope enforcement fires on lead's stray untracked files (commit bench tools promptly).
   244	- consistency-sweep + dataviz + claude-in-chrome: sweep pre-final-commit (4 catches); dataviz validator-gated palette both modes; lead render-check in Chrome caught an axis-label collision — "render and look" is non-delegable.
   245	- 2026-07-17 (JouleWise, screensaver-contamination session): codex skill §Effort selection + §Primary MCP path (consult xhigh discussion-lane, impl xhigh workspace-write; MCP idle-timeout killed impl mid-turn → recovered via §Session observability rollout discovery + codex-bridge resume — recipe worked as written). bridge session-open/close ceremony used; gotcha: --paths defaults to exact match, need explicit `path:subtree`, and a FAILED close retains the lease (needed lease-release). adversarial-review shape started (lenses split lead/Sol) but checkpoint-stopped mid-round; resume in RUN_STATE. Validation: lead live-probe verification caught a fixture-matched-the-bug parser defect Sol's green tests missed — rule 1 earns its keep again.
   246	
   247	## 2026-07-18 (late) — JouleWise D-077 fix-round arc (Fable lead)
   248	- adversarial-review: §Shape step 3 (tiered verification), §C-028 amendments (delta re-audit after EVERY fix round — applied 5x, caught real defects in rounds 3, 4, 5, 6 incl. a fail-open inf-anchor gate and a manifest-clobbering writer; narrowed the round-6 static P1 race per the split-verdict synthesis rule), §Severity rubric for triage. Deviation: round 8 (test-only) got lead review + suite instead of a Sol delta re-audit — recorded in the run report.
   249	- codex-delegation: §Effort-tier policy (xhigh for fix rounds + refuters, high for the test-only round), v3 field notes (hit the documented rc=64 WRITE_SCOPE gotcha twice before re-reading — added a "read field notes first" note), new field note added: xhigh review-genre null-final-message defect 4x + bridge-resume recovery, default read-only sandbox rc=77.
   250	- operation-loop §5 gate shape: followed for PR #77 (lead+Sol reviewed final head; merge left to Ed per merge-authority memory).
   251	- 2026-07-19 (JouleWise, extended quiet window): codex-delegation §MCP-route — two Sol sessions (read-only recompute audit AUDIT_PASS; workspace-write scoped status-page split, NEEDS_SCOPE honored, 20/20 module tests) — worked well, MCP background tasking clean; adversarial-review §severity-tiering applied lightly (exploratory readout → single recompute lens, precedent 3-lens reserved for front-facing promotions); multi-stream-worktrees NOT used (single [QUIET-MAC] lane); operation-loop §bookkeeping (run report + RUN_STATE + PROJECT_STATUS + DRIFT + memory). Field note: detached nohup chain + watcher-Bash re-invocation is the right shape for multi-hour measurement; guard-abort → same-root resume (runner skips complete bundles) avoided any data loss from an operator return.
   252	- 2026-07-19 (JouleWise, D-078 arc) LENS DOCTRINE UPDATE for adversarial-review: on MEASUREMENT code/data, a physics/causality lens (energy vs event timeline, power*duration plausibility, clock-domain checks) catches what recomputation lenses structurally cannot — three Sol recompute audits reproduced every number to 1e-13 while the instrument was misattributing 8 J windows; one causality-framed audit found it immediately. Ed-confirmed: physics lenses on measurements are more useful than recalculation ones. Default review panel for anything measurement-adjacent: contract + execution + PHYSICS (mandatory) + cross-model; recompute alone is never sufficient sign-off. Also: spend Sol xhigh on ONE deep adversarial whole-artifact pass per round (fresh thread each round, no anchoring), fan Fable across distinct lenses for parallelism.
   253	- 2026-07-22 (JouleWise, D-078 close-out session): adversarial-review §Shape (3-lens packet fan-out) + §C-028 (delta re-audit of round-8 caught a real understated-B_fiducial blocker two audited rounds missed; 8 refuter runs, blockers 2 distinct lenses; split A1 verdict lead-synthesized) — NEW amendments added (filter-safe refuter phrasing; provenance-attribution before scope triage). codex-delegation §Invoke/§Adapter (codex-run-v3 xhigh implementation genre; NEEDS_SCOPE early-return honored; review-genre null-final recovered via bridge resume) — NEW field note added (never bench-edit a worktree during an enforced-scope session; false SCOPE_VIOLATION + resume-registry eviction). consistency-sweep (delegated xhigh, end-of-session). council skill §Recording → C-031 entry. operation-loop §5 gate shape for PR #79 (lead+refuters over final head; merge left to Ed).
   254	- 2026-07-24 (JouleWise collection arc): codex-delegation heavily (9 xhigh sessions: 3 forensics, 4 implementation waves, 2 rulings-driven resumes; NEEDS_SCOPE/NEEDS_RULING protocol fired correctly 4x; field-note violations by the LEAD twice — bench edit during enforced-scope (branch switch mid-extraction → false SCOPE_VIOLATION), and pkill without lock cleanup). adversarial-review §delta-re-audit killed a live estimand-biasing design (two-process overlap) pre-merge. NEW operational doctrine candidates for skills: measurement windows need TOTAL orchestrator dormancy (wake-up turns contaminate admission — single-event monitors only); compact bracketed windows over marathon windows (drift gate); per-stage settle periods; campaign lock pid-hygiene. Consider a new 'quiet-measurement-window' skill next session.
   255	
   256	## 2026-07-24/25 — screen+budget gauntlet session (PR #85)
   257	- adversarial-review: §tiered-verification + §C-028 amendments driven hard (4 audit rounds, 3 refuter rounds, delta re-audit after every fix round — pattern held: every fix round introduced or exposed defects). AMENDED this session: new §C-033 (cross-model Opus-contract+Sol-execution pairing = default; high = paired-refuter tier; auditor severity inflation systematic; dictated-fills as catch layer).
   258	- codex-delegation: §invocation + §effort-tiers throughout (~15 Sol sessions). AMENDED: new C-033 field notes (genre/write-scope exactness, ACCEPTANCE_FAILED not resumable, nested-repo strict-scope refusal, codex-usage feed broken, high-tier evidence).
   259	- operation-loop §5 gate shape: followed for the D-072 self-merge (gate evidence in merge commit).
   260	- consistency-sweep: NOT yet run this session — owed before final bookkeeping commit.
   261	- Friction worth a future skill: none new; the quiet-measurement-window candidate skill is still pending (run-book landing first).
   262	
   263	## 2026-07-28 (JouleWise, Fable magistrate) — mint-implementation session
   264	- operation-loop: §0a R1 enforced hard (5 broken-wake interventions, redundant timers); §0 SKIP taken (user-named task) with ✎ sentence; §1 re-shape run twice (Ed's mid-session S6 + pruning ask); §5 gate full shape on PR #87; §7 outside-evidence health checks on cadence; §8 full bookkeeping; §10 not triggered (single-PR merge).
   265	- adversarial-review + codex-delegation: loaded by the Opus lieutenant, not the lead (context economy) — worked; severity-tiered refuters caught one false blocker (C2) and narrowed C1.
   266	- council: fired via the D-072 gate shape; C-039 index row recorded; fresh-eyes sweep NOT due (no phase boundary; ~16 invocations < cadence? — check next session, borderline).
   267	- consistency-sweep: DEVIATION — replaced by mechanical parse check (build_site exit 0) + lead diff self-review under Ed's wrap-up call; full sweep owed next session over RUN_STATE/decision/council edits.
   268	- DRIFT.md refresh (D-068 informing step): OWED — not run at wrap-up; next session.
   269	- New skill candidate: none; the tracked-poll wake pattern folded into codex-delegation instead of a new artifact (one-new-artifact rule respected).
   270	
   271	## 2026-07-30 (JouleWise mint-merge session, Fable magistrate)
   272	- adversarial-review §severity-tiered verification + §delta re-audit: FIX-9/FIX-10 delta re-audits (both FAIL — the layer that caught QA-1 and QA-10A/B against a green 2280-test suite). The §C-028 "fix rounds introduce defects" clause earned its keep twice in one day.
   273	- codex-delegation §invocation + §prompt contract: 4 Sol sessions (audit xhigh ×2, fix high ×2). FIELD NOTE: codex-run-v3 `--write-scope` alone does NOT grant writes — implementation runs need explicit `-s workspace-write`, else the session returns blocked with completion=none (cost: one wasted high session).
   274	- council §cold-gate (rule-11): mandatory trigger honoured (2 same-signature failures → consult, not round 3). Cold Fable + Opus contract refuter pairing exercise #4; refuter caught that the magistrate's OWN ruling (R2 invoked-only) was the QA-10B defect; synthesis = D-088. The pairing's cross-model diversity clause is now 2-for-4 on findings against the adjudicator.
   275	- operation-loop §5 gate shape: PR #88 merged under it; new failure mode logged — GitHub PR test-merge ref can serve a STALE base for multiple runs across close/reopen cycles; verify the checkout "HEAD is now at" SHA before spending a CI watch.
   276	- consistency-sweep: end-of-session sweep delegated (this session).
   277	- Dictated-fills (magistrate→subagent verification pattern): caught 2 magistrate dictation errors (TokenPowerBench arXiv id; 4.7×-vs-4.9× params) + 6 advisor-brief overclaims. Pattern remains the highest-precision error-catcher in the loop.
   278	
   279	## 2026-07-30/31 — contrast-window session (Fable magistrate)
   280	- operation-loop: conductor shape held (window → post-window → overnight D5-J → merge train); magistrate operated the window solo per doctrine.
   281	- council: rule-11 cold-gate mechanism exercised TWICE outside the skill's enumerated triggers but per D-089's revisit clause (DA-1 disposition: cold Fable + Opus refuter, split verdict, magistrate synthesis → D-093) — the split-verdict synthesis path (rule 9) carried real weight; consider promoting "delta-audit FAIL on a consult-sanctioned structural fix" to a named cold-gate trigger in the skill.
   282	- codex-delegation: 4 codex-run-v3 invocations (D5-J impl ×2 launches — first bounced on missing literal `WRITE_SCOPE:` field in prompt, RECORD: the flag requires the field in prompt text; audit ×1; plus one MCP consult during window recovery). Envelope early-returns worked twice (read-only mount blocker; honest partial). Consumption discipline held (final message + git diff only).
   283	- adversarial-review: independent read-only delta audit with replay-on-real-corpus technique (auditor corrupted a clone of a real supersession record — caught DA-1 where fixture-thinking would not have); D-090 conduct rules restated in brief and the auditor complied (report-only).
   284	- consistency-sweep: not yet run this session (owed at close).
   285	- Field note: unittest summary evidence — `cmd | tail -N` in a background task DESTROYS the pass/fail evidence (pipeline exit = tail's, summary may be buffered out of the tail window); capture to file and echo `$?` instead. Cost one redundant 12-min suite run.
   286	
   287	## 2026-07-31 — claims-desk day + metrology window A (Fable magistrate)
   288	- operation-loop: four parallel desk lanes (2 design consults, review train, queue surgery) then window operation; the conductor shape carried a full day cleanly.
   289	- council/cold gates: TWO mandatory cold gates in one day (DA-1 disposition; B1 second-formulation) — the B1 gate was UNANIMOUS across cold Fable + Opus refuter, first time; the refuter's file:line verification (writer emits no v2; scanners skip non-v1) was the decisive input. Pattern worth distilling: when the refuter CONFIRMS rather than splits, synthesis can adopt the refuter's stricter variant without a third instance.
   290	- adversarial-review: four independent delta audits on one branch (C1, C2, fix, deferral); audit-layer catch rate 100% on real defects (DA-1, B1/B2/B3, B1-again); zero blockers survived to merge.
   291	- codex-delegation: 7 codex-run-v3 invocations; recurring worktree git-metadata commit failure (sandbox cannot write .git/worktrees/* of a linked worktree) — ALWAYS plan lead-side commit for worktree sessions.
   292	- Window ops: guarded launcher (HID-idle + daemon-set polling, exec into chain) validated 4 launches; environment gate refused an operator walk-in in 15.8s (member cost, no contamination); third-failure salvage rule exercised for real; a10-precedent post-cal deviation retry exercised and recorded. New footgun logged: supersessions must be recorded BEFORE the whole-window verdict — stopped a premature verdict in time.
   293	- consistency-sweep: run at midday close-out (16 items applied); evening salvage close-out delegated to successor per checkpoint.
   294	
   295	## 2026-08-01 (overnight metrology window B session, Fable magistrate)
   296	- codex-delegation: §invocation + §prompt contract — bounded Sol xhigh root_cause consult via codex-run-v3 (read-only, consult_anchor_v2.md); packet self-corrected mid-flight (killed v1 on TM-exoneration evidence, refired v2 with bird identification). Consult REFUTED the lead's drift-rate mechanism (quantization-confounded) while confirming the structural knife-edge — exactly the license-to-disagree pattern rule 2 wants; its F2 attempt-cap catch and F3 SIGSTOP-lifecycle additions were both adopted verbatim.
   297	- operation-loop/§window custody (project runbook §5B/§8/§10/§11/§12): three §10 continuations + salvage close executed solo; recorder-then-verdict order held; NEW hazard for the skill docs: operating-session OUTPUT STREAMING during idle gates caused failure #3 — candidate amendment for the council/operation-loop measurement-discipline sections ("zero tool calls" -> "zero tool calls AND zero streaming; one-line arm messages").
   298	- Escalation trigger (CLAUDE.local rule 11): fired twice (§5B same-signature aborts -> consult; slot same-signature failures -> salvage close). Both stops honored without magistrate override.
   299	
   300	## 2026-08-01 — JouleWise desk/adjudication session (Fable magistrate)
   301	- operation-loop: intake→streams→gates shape followed implicitly (desk-lane session; no formal §-invocation). Streams: adjudication audit, cold gate pair, commit-3 consult+impl, CI fix.
   302	- codex-delegation: 3 Sol xhigh sessions via the codex subagent (read-only adjudication audit; read-only commit-3 design consult; workspace-write commit-3 implementation w/ 6-path WRITE_SCOPE). Consumed as final reports only. Effort-tier §: xhigh triggers held (adversarial review, design-bearing, cross-contract). Field note: audit line-number citations drifted (R14, substance held) — consider requiring `git grep -n` verification snippets in audit briefs.
   303	- adversarial-review: severity-tiering honored — the audit's 3 groups got magistrate bench verification (blocker-grade, 2+ independent checks each); cold gate = 2 refuters w/ distinct lenses (fresh-Fable merits + Opus contract).
   304	- council (rule-11 cold gate §): FULL shape exercised: cold Fable ruling → bounded factual follow-up (custody sweep contradicted a drafted license line; instance re-drew on the merits) → independent Opus refutation (14 findings) → magistrate synthesis (D-100). NEW pattern worth folding into the skill: the packet's "deferred residual" (condition 4 custody sweep) caught the ruling's disk-shape miscalibration — mechanically-assembled packets should list UNSWEPT evidence explicitly so rulings defer rather than assume; and R5a-style "real-shape regression outranks prose" is a strong convergence device.
   305	- multi-stream-worktrees: c3 worktree for the commit-3 impl; subagent correctly refused in-worktree `git commit` (gitdir not writable under sandbox) per the skill's lead-commits-at-the-gate rule — skill text validated by an independent rediscovery.
   306	- consistency-sweep: pending at session close.
   307	
   308	## 2026-08-02 evening (post-move resume; PRs #94/#95 landed)
   309	- operation-loop: followed implicitly as the conductor (resume script execution, gates, bookkeeping); not formally invoked.
   310	- adversarial-review §severity-tiers: applied at the merge gates — decisive audits consumed from .desk custody; composed-tree full suite as the lead integration gate (multi-stream-worktrees §integration-tree, applied to a 2-PR merge wave with real conflicts).
   311	- codex-delegation: TWO field notes. (1) codex-run-v3 interface: out-file is POSITIONAL first, WRITE_SCOPE must ALSO appear as a literal `WRITE_SCOPE:` line in the prompt — two failed launches from guessing flags; read usage() first. (2) Envelope protocol failure (ACCEPTANCE_FAILED, report file never written) on an otherwise-complete xhigh implementation — work held uncommitted as untrusted per contract; disposition recorded in run-report §9.
   312	- consistency-sweep: delegated post-merge (Sol xhigh read-only), findings-only brief with tonight's SHAs pinned.
   313	
   314	## 2026-08-03 (desk session, Ed away ~5h; two claim streams parked for Ed)
   315	- codex-delegation §escalation + §effort-tiers: heavy use. Three parallel Sol streams (D100-BII, MINT-GENERALIZE, CAL-BRACKET) each run impl→audit→fix→delta as separate xhigh sessions; consumed via envelope + git diff only. KEY DISCIPLINE WIN: on CAL-BRACKET's REPEAT-signature delta failure, ran a read-only design CONSULT (scout genre) instead of a blind round three — the "consult not round three" rule caught that F3 was decision-level (D-102 silent on the trigger mechanism), not a bench fix.
   316	- adversarial-review §severity-tiers + §distinct-lenses: every stream's audit fanned findings, verified proportionally; fix rounds each got a FRESH-thread delta re-audit (never delta-only where the surface had failed twice).
   317	- council §cold-gate (rule 11 full shape): TWO cold gates on the b-ii nested closure (gate 2 → D-107; gate 3 → STOP). Cold Fable instance + Opus contract-lens refuter, mechanically-assembled packets. Refuter layer amended/overturned at BOTH (6 consecutive gates now). Gate 3's decisive finding was STRUCTURAL (grammar constrains values not list cardinalities; ~1.2KB numeric residual) — a fresh-thread depth the cold Fable instances did not reach, vindicating the cross-model pairing.
   318	- council §when-to-stop / rule-11 magistrate accountability: the session's defining call. D100-BII hit its THIRD formulation failure + a proof that clause (c) cannot meet its predicate by any bench work → STOPPED the loop, escalated to Ed (D-108), did NOT spin round four. This is the exact disposition rule 11 exists to force; recorded in C-041 as evidence the topology holds when the loop-immersed agent chooses to stop.
   319	- PACKET HYGIENE (self-correction): the refuter recorded 4 hygiene findings against my gate-3 packet (selective clause quotation; flags not quoted in full incl. the blocking anti-round-3 one; a laundered over-refusal number; wrong-population census). Adopted the standing correction: quote governing clauses to the period; quote every source flag in full including ones cutting against my proposed disposition; census the license-surface population, never a convenient superset. Same class D-106/D-107 already flagged — this recurs, watch for it.
   320	- codex-delegation field note: `--write-scope` strict mode still trips "nested repositories" on stale .claude/worktrees/* — for read-only sweeps, drop the flag and use `-s read-only`. Also: the codex models-cache bug (missing supports_reasoning_summaries) is FIXED (cache moved aside, refetched) — but note SEVERAL xhigh runs this session still showed ACCEPTANCE_FAILED with a COMPLETE report inside; the envelope-write quirk persists intermittently even post-fix, so always check the .md body, not just the .status.
   321	- consistency-sweep + operation-loop §bookkeeping: end-of-session sweep delegated (Sol xhigh, findings-only, tonight's SHAs pinned); council/kernel/RUN_STATE refreshed; two ED-DECISION-PENDING blocks (D-108, D-109) at the top of RUN_STATE as the durable handoff.
   322	
   323	## 2026-08-03 16h runway (Fable magistrate, harness-switch checkpoint)
   324	- codex (skill + codex-run-v3): ~10 sessions — 2 impl xhigh, 2 fix
   325	  rounds xhigh, 4 audits/deltas xhigh, 1 docs xhigh, 1 hygiene high;
   326	  MCP discussion lane for the D-108/D-109 debate (2 rounds) + 3-question
   327	  night consult + 2 follow-ups. Envelope discipline held; two
   328	  worktree-index sandbox blocks (lead commits by design); one
   329	  WRITE_SCOPE launch friction pair (prompt WRITE_SCOPE field required;
   330	  nested-repo strict-scope refusal -> clean worktree pattern).
   331	- adversarial-review §severity-tiers: applied across both gauntlets;
   332	  blockers 2-instrument-verified via the cold gate; delta-re-audit rule
   333	  earned its keep twice (F1 catch; B1-persists catch).
   334	- council §cold-gate: winB STOP gate (cold Fable + Opus refuter,
   335	  convergent, one framing dissent synthesized). Agent-tool cold
   336	  instances worked; subagent background-probe death pattern recorded.
   337	- multi-stream-worktrees: 4 concurrent worktrees, no collisions;
   338	  frozen-corpus safety enforced by WRITE-SCOPE-excluding-runs-root
   339	  (pattern worth keeping).
   340	- consistency-sweep: end-of-session sweep delegated (this checkpoint).
   341	- NEW pattern (Ed-validated): concurrent read-only Fable audit during
   342	  execution — intercepts in-flight licenses; memorized; D080-TRIGGER-01
   343	  queued.
   344	
   345	## 2026-08-05/06 12h autonomous marathon (Fable magistrate; owed entry, assembled 2026-08-07 by the successor from RUN_STATE + traces)
   346	- codex-delegation §effort-tiers + §Invoke: heaviest session on record (~
   347	  the six-PR arc + issuance gauntlet). Cap-lift honored mid-session when
   348	  Ed restored high/xhigh per complexity; fast tier implemented per Ed's
   349	  exact spec (per-call CODEX_SERVICE_TIER=fast via scripts/codex-bridge
   350	  only). Field note re-recorded the prompt-is-a-literal-string gotcha
   351	  (one consult launched path-as-prompt, killed + relaunched cleanly).
   352	- adversarial-review §delta-re-audit: the rule's strongest session —
   353	  introduced defects caught in BOTH streams (QG init-durability F1; CGV
   354	  receipt-serialization B1 + phantom-fence B2, both live-proved).
   355	- council §cold-gate (rule 11): the D-079 issuance gate is the topology's
   356	  flagship catch to date — split verdict (fresh-Fable PROCEED / Sol xhigh
   357	  HOLD), magistrate upheld HOLD, preventing an irreversible ledger write
   358	  paired with a production-refused artifact. Issuance reframed as
   359	  implementation and re-gauntleted (PRs #108/#109).
   360	- council §escalation-trigger: fired twice on same-signature count 2 (CGV
   361	  F3 third formulation; QG census class) — both routed to consults, not
   362	  round-3 fix rounds; both consult-adopted shapes then closed the class.
   363	- operation-loop §8: bookkeeping (sweep, council log, skill log) was NOT
   364	  completed in-session — checkpoint recorded it as owed; cleared
   365	  2026-08-07 (C-049 + this entry). Lesson: a machine-move stop mid-arc
   366	  leaves §8 to the successor by design; the checkpoint block carried it.
   367	
   368	## 2026-08-07 (successor session: resume, dormant-app number, prefill scout)
   369	- operation-loop §0/§0a: invoked at session start; deliverable sentence
   370	  written; R1 wake-source discipline — first poll misimplemented the
   371	  skill's own pattern (tested status-file EXISTENCE; v3 writes RUNNING
   372	  immediately — the skill correctly says "leaves RUNNING"; deviation was
   373	  mine, skill text validated).
   374	- codex-delegation §Invoke + §prompt-contract: one read-only scout-genre
   375	  Sol session (prefill-contrast feasibility, high effort — no xhigh
   376	  trigger); six-part contract with precedence + autonomy clauses;
   377	  launched via "$(cat prompt.md)" per the literal-string field note.
   378	- bench-vs-session threshold (rule 9): t3appup r01/r02 analysis done at
   379	  the bench (a ~60-line stats script < the delegation contract);
   380	  cross-checked against the pipeline's independent idle_baseline block
   381	  before banking (rule 1 lead verification).
   382	- consistency-sweep: delegated at session close (pending at this write).

exec
/bin/zsh -lc "sed -n '170,262p' /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md | nl -ba -v170" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   170	
   171	## 2026-07-09 — spec-fleshing wave 1 (C-024, same session as C-023 review)
   172	- operation-loop: §1 mid-session re-shape used on Ed's go-ahead (review → 4 implementation streams, footprints pinned disjoint, all full-tier); §2 worktrees used (parallel WRITES this time — correct scale-up from the review's no-worktree call); §4 full pipeline per stream (design invited inline, lenses, FIX-N, gates); §5 merge gate ran the full C-010 shape incl. final-head + NEW tail-verification pass; §6 integration review PAID (5 seam catches — S1/S2 written against pre-S3 contracts; no other layer could see it); §8 full bookkeeping + sweep; §8 cadence rule AMENDED mid-session (Ed: per-artifact push, checkpoint pushes) and folded same-session.
   173	- codex-delegation: 20 codex sessions, zero stalls; FIX-N one-shot record now 13/13; instant-completion diagnostic caught 1 real launch failure (zsh parse error on a for-loop of prompts — lesson: never batch multiple codex-run prompts in one shell loop; separate calls); severity-tiered pipeline caught a statistics blocker (percentile-UCB unidentifiable at n=10) that BOTH the lead and the implementer had provisionally accepted — the fresh-lens layer is the quality mechanism for design-freedom delegation.
   174	- adversarial-review: severity shape held (blockers got refuting-quality scrutiny via final-head + tail passes; nits applied without ceremony).
   175	- multi-stream-worktrees: 4 streams, disjoint-footprint pins held (zero collisions); codex-can't-commit-in-worktree constraint handled by lead pathspec commits per caveat 3.
   176	- consistency-sweep: dispatched with supersession-closure item (UCB → false-effect guard floor surfaces).
   177	- council: C-023 pointer→C-024 pointer entry pattern; discussion bounded; history-vs-live rule applied at the FH ledger fix (supersession annotations, not rewrites) — the doctrine prevented promoting a rejected estimator to the decision log.
   178	
   179	## 2026-07-09 — spec-fleshing wave 2, ultracode (C-025, same session)
   180	- operation-loop: §4a design-round-first STRENGTHENED clause (Ed, folded this session) validated immediately — P2-030 memo→ratify-with-pins→implement produced zero design rework; §7 fleet-health check used on a user-reported stall: outside evidence (ps etimes, worktree mtimes, workflow journal) showed healthy-slow not wedged; correct intervention was ADDITIVE streams (S9/S10), not kills — fold candidate: "user-perceived stall → evidence check BEFORE relaunch; reinforce with disjoint streams, never a second writer in a live worktree".
   181	- codex-delegation: FIRST full Workflow-tool orchestration (46 agents, zero stalls, zero errors) — the sanctioned Workflow alternative scales to implement→lens→refute shapes, and its codex WRAPPER agents can git commit+push in worktrees (they are full agents), beating direct codex-run for worktree streams where codex's own sandbox still index.lock-blocks; refuter layer killed 10/30 findings pre-triage (precision working); mutation testing appeared organically in a test-audit lens (5 mutations proving gaps) — fold candidate for §Test doctrine: "test-audit lenses may be prompted to MUTATION-TEST the gates they audit"; FIX-N one-shot record now 22/22; NEVER batch multiple codex-run launches in one zsh for-loop (parse-error launch failure, second occurrence class).
   182	- adversarial-review: severity tiers held; final-head layer caught 2 live-path defects invisible to earlier layers (MLX position under rotation; linter false-negative regression FROM a fix round) — the fix-round-regression hunt is now demonstrably the final-head's highest-yield angle.
   183	- multi-stream-worktrees: 6 concurrent streams peak; combined-ref pre-merge suite check (C-022 lesson) used deliberately for the first time — zero conflicts, validated the p2029×p2030 strict-surface interaction before merge.
   184	- consistency-sweep: dispatched with supersession items (ordering-executability and linter-cut-line surfaces).
   185	
   186	## 2026-07-09 — P2-034 broad campaign packs (C-026, same session)
   187	- operation-loop: §4a design-round-first used as DEFAULT (second validated run: scoping memo → 3 lead pins → zero design rework); §1 single-stream call correct (one dir = one worktree; no false parallelism); §6 integration review correctly SKIPPED (single stream); §8 tree-quiescence rule observed (bookkeeping only after all codex rounds done) — no recurrence of the C-025 defect.
   188	- codex-delegation: 5-session pipeline; compliance lens caught a char-level registry drift the LINTER structurally cannot see (markdown code-span nesting) — lesson: mechanical linting bounds but never replaces the review lens for ratified-wording fidelity; FIX-N 23/23.
   189	- adversarial-review: cold-start test prompt device ("could a lab that has never seen JouleWise run this?") yielded the highest-value executability finding — reusable prompt pattern for runbook reviews.
   190	
   191	## 2026-07-09 — JouleWise C-027 whole-project council review (Fable lead)
   192	- council: §Triggers (user-asked full council), §Session shape B (7 divergent lenses + examiner — shape B's "MORE divergent threads" and final-examiner steps both load-bearing; examiner PASS-conditional caught 7 synthesis defects), §Recording (index row + full entry + deliberation traces), §Roles. WORKED AS WRITTEN.
   193	- codex-delegation: §Invoke (codex-run ×10, zero stalls; one-per-Bash-call rule held), §Prompt contract (all six parts; autonomy clause paid off — 5 unprompted premise corrections), §Direction doctrine (lens-names-an-angle, CLEAN-needs-checks-line both used), §Model-version scoping (FOLLOWED: calibration batch logged, promotion refused pending A/B), §Consume (final-message-only; .status naming), §Economics (counterreview of the lead's synthesis was the round that caught the most). GAP FOUND: skill still titled "gpt-5.5"; model now gpt-5.6-sol behind config — needs a one-line model-note after the sealed A/B.
   194	- adversarial-review: severity-tiered verification idea applied (blockers lead-verified + double-examined; lower tiers accepted on citation quality — the examiner correctly flagged the unaudited lower tiers, worth folding into the skill as an explicit disclosure rule).
   195	- consistency-sweep: delegated sweep run over the close-out branch (in flight at log time).
   196	- Session-level lesson for skills: the REVERSE lens (audit the lead against its own rules) produced 2 of 8 blocker clusters — council skill's reverse-review emphasis validated again; consider making a whole-project reverse audit a standing periodic trigger.
   197	
   198	## 2026-07-11 (JouleWise C-028 continuation: #49 merge, p2041 vetted rebuild, P2-037 fan-out)
   199	- codex-delegation §Invoke/§Prompt-contract/§Economics: 6+ codex-run-v2 sessions (merge review, p2041 diagnosis, deletion triage, flake root-cause, vetted composition ULTRA, p2037 ULTRA, scheduling scout). NEW §Effort-tier policy added (Ed): ultra=subagent-needing sessions only; xhigh/high individual tasks; push xhigh scope until first prod-quality miss and record ceiling. The two ULTRA launches this session predate the policy — going forward they'd be xhigh.
   200	- adversarial-review shape used implicitly (severity-tiered verification of Sol merge-review findings: blocker fact-checked, should-fix verified via reconstructed 3-way merge).
   201	- LESSON (lead-side defect caught by Sol review): `git checkout --ours/--theirs <file>` during conflict resolution takes the WHOLE file, silently discarding the other side's cleanly-auto-merged hunks. Correct tool: resolve marker regions in place, or reconstruct with `git merge-file` per file. Candidate for codex-delegation/multi-stream field notes.
   202	- Session second half: adapter v1 adopted + codex-run-v3/codex-usage built+installed (runner-injected report contracts); scope-restraint 3-layer design (language live, backstop in flight at pause); NEEDS_RULING generalized early-return; design-consult-by-default doctrine (P2-044 first product: corpus-grounded HAC design, 47x variance underestimate found); PRs #49/#54 merged, #50-#53/#55 held; P2-037 second transport-OK/no-report incident (independent audit pattern instead of self-grading resume). Usage data: 1 ultra = 35.3M tokens ≈ 11 xhigh sessions; Fable generation ~1.8M vs Sol ~112M same arc. Paused at C-028 checkpoint #4 (25a8b05).
   203	- C-028 close (2026-07-11 second half): full gauntlet validated end-to-end (~57 Sol invocations, ~16 refuters: 70/15/15 confirm/narrow/refute — narrowings highest-value); integration tree caught 38 pre-merge cross-stream failures; enforcement stack live-tuned (bytecode false-positives → recorded exemption; 3 compliant NEEDS_SCOPE stops with correct-path discovery; nested-repo guard limitation → prompt-scope + lead-diff fallback); v3 defects logged (resume no-op, in-place-edit crash); wave lesson: never trust loop completion banners, verify per-PR state (DNS-blip skip caught). Fable dictated-fills pattern for bookkeeping finalization: agent verified every dictated fact against evidence and caught lead miscounts. Skills amended: adversarial-review + multi-stream-worktrees §C-028; CLAUDE.md rule 9 (gauntlet default) added.
   204	
   205	## 2026-07-12 — C-029 agent-lane triple (SITE-01/P2-049/P2-028; PRs #61-#63)
   206	
   207	- operation-loop §0-§8 walked in order: §0 deliverable sentence, §1 four-stream shape (1 bench + 3 Sol pipelines, disjoint footprints), §2 worktrees, §4 per-stream pipeline (design folded into impl prompts as DESIGN-section requirement — worked well at this scope), §5 lead gates, §8 bookkeeping. §6 integration review SKIPPED (streams not merged yet — deferred to merge wave). Consistency sweep DEVIATION: lead quick-pass instead of delegated sweep (upstream outage); gen_state --check + tests stood in for the counts surface.
   208	- council §Recording: spend-snapshot convention ADDED this session (codex-usage at entry close + Fable triple + composition caveat) and exercised in the C-028 addendum; C-029 index row kept to pointer form (run report owns the trace — v2 discipline held).
   209	- codex-delegation §Invoke: v3 field notes ADDED (WRITE_SCOPE-in-prompt rc=64; MANDATORY explicit --effort after 13 unintended-ultra invocations via config passthrough; thin-output-OK = FAILED; resume-after-outage preserved 206k tokens of fix-round work, worktree = ground truth). §Prompt contract used on all 13 invocations; FIX-N contracts 2-for-2 clean (18-item and 1-item rounds).
   210	- adversarial-review: severity policy APPLIED WITH SUBSTITUTION — 5 blocker claims adjudicated by lead code-reading instead of 2-refuter rounds (cheaper + stronger for mechanically-verifiable claims: 2 confirmed, 1 partially refuted, 1 design ruling, 1 reproduce-first-in-fix-round). Delta re-audit doctrine BLOCKED by upstream outage (3 attempts) — owed pre-merge, recorded in PRs/RUN_STATE. Lead-gate unique catch: capped-cell over-refusal in the fix round (third "fix rounds introduce defects" datum).
   211	- Calibration: design-freedom delegation hot again — site01 shard design (instruction-budget-aware, quantified Base85 rejection) beat the lead's pagination prior; p2028 implementer's F1 catch was half-right (correct defect, wrong correction) — dictated-fills verify-every-fact lesson generalizes to session findings.
   212	
   213	## 2026-07-13 JouleWise restart-close + audit-gate session (Fable lead)
   214	- operation-loop: §0 intake (deliverable sentence), §4 pipeline tail (delta re-audits), §5 lead gates (bench fixes DRA-001/XSI-1 with regressions; live deploy + meter + freshness), §6 integration review (fired at 2 streams; 1 unique catch XSI-1), §8 bookkeeping (run report + C-030 row + kernel/queue retirement + supersession-free), §9 same-session folds (none needed — prior session's folds held). DEVIATION: consistency sweep SKIPPED deliberately — the declared comprehensive audit supersedes it this once; if the audit does not run, the sweep debt stands.
   215	- adversarial-review §C-028 amendments: delta re-audit after fix rounds validated AGAIN (DRA-001 blocker found on a twice-reviewed diff — fourth "fix rounds introduce defects" datum); explicit --effort xhigh on all review sessions (3 sessions ≈ 7.0M tokens vs prior day's unintended-ultra 13 ≈ 118M — ~17x cheaper for equal role).
   216	- codex-delegation §Invoke: v3 wrapper effort passthrough fix held (manifest rows show xhigh); WRITE_SCOPE in-prompt requirement respected in all prompts.
   217	- council §Recording spend snapshot: exercised for C-030 (second use; convention holding).
   218	- NEW LESSON (fold candidate, not yet folded — audit may reshape it): cross-thread collisions in one working tree are now real (Ed runs concurrent threads); the two-writer rule needs a cross-THREAD corollary — before any commit, diff-inventory the tree for foreign changes and verify provenance with the user rather than pathspec-committing around unexplained diffs blindly.
   219	
   220	## 2026-07-13 — Bridge v1.1 max-co-work session (Fable lead, background job)
   221	
   222	- operation-loop: §0 deliverable sentence; §1 single contract-bearing stream (worktrees SKIPPED correctly); §3 default assignments (design consult xhigh MCP, impl xhigh CLI, fix3 dropped to high when triggers lapsed — first non-xhigh round, correct); §4 full pipeline incl. STRENGTHENED design round (lead's spec itself consulted pre-implementation — Sol amended 5 pins and caught a v1 adapter bug; the pre-decision-consult default earned its keep); §5 lead gates (live wrapper dogfood, live reverse consults, flake triage: lead-rerun caught an agent-load flake the worker's green run masked); §8 bookkeeping (run report + C-032 row + D-065 + D-064 tracked manifest — first session to create docs/process_traces/); §9 folds done mid-session (codex-delegation +2 field notes). §6 SKIPPED (single stream), §10 not fired (single-PR).
   223	- adversarial-review: 3 distinct lenses + severity tiering; DEVIATION (recorded in report): round-1 blockers verified by lens-repro + independent lead code-trace instead of 2 fresh refuters; mechanical existence claims lead-verified. The mandatory delta re-audits then caught 3+2+1 fix-round defects INCLUDING TWO CORRECTIONS OF THE LEAD (a lead-graded nit upgraded by auditor repro; a vacuity the lead's own check missed) — the substitution is safe only WITH the delta re-audits behind it.
   224	- codex-delegation §Invoke: v3 preflight gotchas ×3 (WRITE_SCOPE prompt line; nested-repo refusal from a stale .claude/worktrees entry; ignored-cap 10k tripped by .venv → cap now 50k + CODEX_RUN_IGNORED_CAP) — folded same-session into the appendix. Consult scorecard bullet added.
   225	- council §Recording: C-032 index-row-only (run report = ONE home) held.
   226	- consistency-sweep: delegated Sol xhigh, scope included ~/.claude/skills + global CLAUDE.md + new ~/.codex/AGENTS.md (multi-skill-edit rule applied).
   227	- NEW LESSON (folded into trace/report; candidate for operation-loop §5): harness auto-mode can DENY agent self-merge of agent-authored PRs regardless of standing CLAUDE.md authorization — plan merge waves so Ed's merge click is the explicit last step, or run merges in a session where Ed names them.
   228	
   229	## 2026-07-16 — JouleWise resumption + no-hardware batch (Fable lead)
   230	
   231	- operation-loop: §0 intake + deliverable sentence; §1 re-shape fired TWICE on mid-session scope additions (Ed: "work the no-hardware backlog"; Ed: "handle the merge yourself"); §2 worktree-per-stream (4 streams, disjoint footprints held); §3 default assignments (Sol high audits per Ed's ask, xhigh only on contract-bearing SPLIT-AP/AXI-SB, Fable subagent for web verification per rule-9 dictated-fills); §4 full pipeline per stream; §5 lead gates (CI-log verification that a green job actually EXECUTED the new test; AXI-SB live probes lead-run; field-name check before accepting `supported`); §6 integration review fired at 3 streams (0 unique catches — first zero-catch datum for this layer, tally per §10 drop rule); §8 full bookkeeping arc; §10 not fired beyond the tally note.
   232	- Workflow-wrapped codex (codex-delegation sanctioned alternative): 4 audits + 5 refuters via agentType codex + schema — zero stalls; refuters produced 1 severity downgrade + factual narrowings, worth their cost.
   233	- adversarial-review §C-028: delta re-audit after EVERY fix round — paid off with an EIGHTH "fix rounds introduce defects" datum, and the first LEAD-AUTHORED one (the lead's own FIX-1 pin dropped predictor components; the delta pass caught it). Bench-fix threshold used twice; both bench edits got fresh micro-reviews (final-head rule applied to the lead's own edits).
   234	- codex-delegation §Invoke: NEW v3 gotcha (fold candidate → field notes): strict-scope runs REQUIRE the out-file OUTSIDE the worktree (rc=64 "strict-scope artifacts must be outside the worktree") — scratchpad out-files always.
   235	- council §Recording: C-036 index-row-only; run report = ONE home.
   236	- consistency-sweep: delegated (Sol high) before the final bookkeeping commit; scope: session-changed status docs.
   237	- NEW DATA for the self-merge lesson (2026-07-13 entry): with Ed's EXPLICIT in-session delegation ("handle the merge yourself if all is well"), gh self-merge of agent-authored PRs worked (3×) — the prior harness denial applies to standing-authorization-only merges; in-session delegation is the working shape. Also: gh token needed `workflow` scope for ci.yml pushes (Ed refreshed in-session).
   238	
   239	## 2026-07-17 — JouleWise Window-A execution + wrap (Fable lead, continuation)
   240	
   241	- operation-loop full arc across summarization boundaries (task board carried state); measurement/agent strict alternation held; lead-only live measurement enforced throughout (4 shakedown attempts, floors 248-line campaign, exploratory block).
   242	- adversarial-review: delta re-audits caught fix-round blockers twice more (9th/10th data); anti-gaming lenses on BOTH positive (AXI-SB) and negative (AXI-SC) verdicts — negative-verdict honesty (positive-control path) is a new lens angle worth folding.
   243	- codex-delegation new field notes: strict-scope out-file must be OUTSIDE the worktree (rc=64); bare `**` invalid scope entry; forced-report placeholder = thin-output variant (persist-time size checks mandatory); runner exit-0-on-lock-refusal wart (verify progress by artifact counts, not rc); scope enforcement fires on lead's stray untracked files (commit bench tools promptly).
   244	- consistency-sweep + dataviz + claude-in-chrome: sweep pre-final-commit (4 catches); dataviz validator-gated palette both modes; lead render-check in Chrome caught an axis-label collision — "render and look" is non-delegable.
   245	- 2026-07-17 (JouleWise, screensaver-contamination session): codex skill §Effort selection + §Primary MCP path (consult xhigh discussion-lane, impl xhigh workspace-write; MCP idle-timeout killed impl mid-turn → recovered via §Session observability rollout discovery + codex-bridge resume — recipe worked as written). bridge session-open/close ceremony used; gotcha: --paths defaults to exact match, need explicit `path:subtree`, and a FAILED close retains the lease (needed lease-release). adversarial-review shape started (lenses split lead/Sol) but checkpoint-stopped mid-round; resume in RUN_STATE. Validation: lead live-probe verification caught a fixture-matched-the-bug parser defect Sol's green tests missed — rule 1 earns its keep again.
   246	
   247	## 2026-07-18 (late) — JouleWise D-077 fix-round arc (Fable lead)
   248	- adversarial-review: §Shape step 3 (tiered verification), §C-028 amendments (delta re-audit after EVERY fix round — applied 5x, caught real defects in rounds 3, 4, 5, 6 incl. a fail-open inf-anchor gate and a manifest-clobbering writer; narrowed the round-6 static P1 race per the split-verdict synthesis rule), §Severity rubric for triage. Deviation: round 8 (test-only) got lead review + suite instead of a Sol delta re-audit — recorded in the run report.
   249	- codex-delegation: §Effort-tier policy (xhigh for fix rounds + refuters, high for the test-only round), v3 field notes (hit the documented rc=64 WRITE_SCOPE gotcha twice before re-reading — added a "read field notes first" note), new field note added: xhigh review-genre null-final-message defect 4x + bridge-resume recovery, default read-only sandbox rc=77.
   250	- operation-loop §5 gate shape: followed for PR #77 (lead+Sol reviewed final head; merge left to Ed per merge-authority memory).
   251	- 2026-07-19 (JouleWise, extended quiet window): codex-delegation §MCP-route — two Sol sessions (read-only recompute audit AUDIT_PASS; workspace-write scoped status-page split, NEEDS_SCOPE honored, 20/20 module tests) — worked well, MCP background tasking clean; adversarial-review §severity-tiering applied lightly (exploratory readout → single recompute lens, precedent 3-lens reserved for front-facing promotions); multi-stream-worktrees NOT used (single [QUIET-MAC] lane); operation-loop §bookkeeping (run report + RUN_STATE + PROJECT_STATUS + DRIFT + memory). Field note: detached nohup chain + watcher-Bash re-invocation is the right shape for multi-hour measurement; guard-abort → same-root resume (runner skips complete bundles) avoided any data loss from an operator return.
   252	- 2026-07-19 (JouleWise, D-078 arc) LENS DOCTRINE UPDATE for adversarial-review: on MEASUREMENT code/data, a physics/causality lens (energy vs event timeline, power*duration plausibility, clock-domain checks) catches what recomputation lenses structurally cannot — three Sol recompute audits reproduced every number to 1e-13 while the instrument was misattributing 8 J windows; one causality-framed audit found it immediately. Ed-confirmed: physics lenses on measurements are more useful than recalculation ones. Default review panel for anything measurement-adjacent: contract + execution + PHYSICS (mandatory) + cross-model; recompute alone is never sufficient sign-off. Also: spend Sol xhigh on ONE deep adversarial whole-artifact pass per round (fresh thread each round, no anchoring), fan Fable across distinct lenses for parallelism.
   253	- 2026-07-22 (JouleWise, D-078 close-out session): adversarial-review §Shape (3-lens packet fan-out) + §C-028 (delta re-audit of round-8 caught a real understated-B_fiducial blocker two audited rounds missed; 8 refuter runs, blockers 2 distinct lenses; split A1 verdict lead-synthesized) — NEW amendments added (filter-safe refuter phrasing; provenance-attribution before scope triage). codex-delegation §Invoke/§Adapter (codex-run-v3 xhigh implementation genre; NEEDS_SCOPE early-return honored; review-genre null-final recovered via bridge resume) — NEW field note added (never bench-edit a worktree during an enforced-scope session; false SCOPE_VIOLATION + resume-registry eviction). consistency-sweep (delegated xhigh, end-of-session). council skill §Recording → C-031 entry. operation-loop §5 gate shape for PR #79 (lead+refuters over final head; merge left to Ed).
   254	- 2026-07-24 (JouleWise collection arc): codex-delegation heavily (9 xhigh sessions: 3 forensics, 4 implementation waves, 2 rulings-driven resumes; NEEDS_SCOPE/NEEDS_RULING protocol fired correctly 4x; field-note violations by the LEAD twice — bench edit during enforced-scope (branch switch mid-extraction → false SCOPE_VIOLATION), and pkill without lock cleanup). adversarial-review §delta-re-audit killed a live estimand-biasing design (two-process overlap) pre-merge. NEW operational doctrine candidates for skills: measurement windows need TOTAL orchestrator dormancy (wake-up turns contaminate admission — single-event monitors only); compact bracketed windows over marathon windows (drift gate); per-stage settle periods; campaign lock pid-hygiene. Consider a new 'quiet-measurement-window' skill next session.
   255	
   256	## 2026-07-24/25 — screen+budget gauntlet session (PR #85)
   257	- adversarial-review: §tiered-verification + §C-028 amendments driven hard (4 audit rounds, 3 refuter rounds, delta re-audit after every fix round — pattern held: every fix round introduced or exposed defects). AMENDED this session: new §C-033 (cross-model Opus-contract+Sol-execution pairing = default; high = paired-refuter tier; auditor severity inflation systematic; dictated-fills as catch layer).
   258	- codex-delegation: §invocation + §effort-tiers throughout (~15 Sol sessions). AMENDED: new C-033 field notes (genre/write-scope exactness, ACCEPTANCE_FAILED not resumable, nested-repo strict-scope refusal, codex-usage feed broken, high-tier evidence).
   259	- operation-loop §5 gate shape: followed for the D-072 self-merge (gate evidence in merge commit).
   260	- consistency-sweep: NOT yet run this session — owed before final bookkeeping commit.
   261	- Friction worth a future skill: none new; the quiet-measurement-window candidate skill is still pending (run-book landing first).
   262	

exec
/bin/zsh -lc 'SNAP=/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot; for f in "$SNAP"/*/SKILL.md "$SNAP"/codex-delegation/ADAPTER.md; do printf '"'\\n%s\\n' \""'$f"; rg -n '"'"'^#{1,4} '"' \""'$f"; done' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:

/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md
6:# Tiered adversarial review
13:## Shape
55:## Document-shaped artifacts (added 2026-07-08)
74:## Severity rubric (keep lenses consistent)
82:## Rules of thumb
97:## C-028 arc amendments (2026-07-11; empirically validated over ~16 refuters)
120:## D-078 close-out amendments (2026-07-22; 3 lenses + 11 refuter runs)
144:## C-033 pairing amendments (2026-07-25; PR #85 gauntlet, 4 audit rounds + 3 refuter rounds)

/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md
6:# Delegating to Codex (gpt-5.6-sol era; see §Effort-tier policy + ADAPTER.md)
19:## Invoke (the procedure)
101:### Token-efficient consumption
106:## Delegate vs keep
120:## Prompt contract (all six, every time)
135:### Direction doctrine (evidence: 43-invocation study, suite-build 2026-07-08)
209:## Consume
240:## Specialties
242:### Division of labor
273:### Security
299:## Test doctrine (the ONE home)
316:## Economics (Ed, 2026-07-07) — the ONE home of the spend doctrine
332:### Effort-tier policy (Ed, updated 2026-07-12; gpt-5.6-sol era)
370:### Adapter: claude-codex-report/v1 (ADOPTED 2026-07-11)
494:## Parallel threads
514:## Appendix: field notes and superseded-fix history

/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md
6:# Docs-consistency sweep
15:## Delegation prompt shape
53:## Pre-commit docs-verify mode (added 2026-07-08; distinct from the sweep)
76:## Applying results

/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md
6:# Event-driven multi-model council
14:## Triggers (event-driven — pick the LIGHTEST tier that covers the risk)
30:## Standing fresh-eyes sweep (periodic, non-reactive; ratified 2026-07-27, D-080)
102:## Roles
128:## Discussion protocol
139:## Recording + instrumentation
192:## Session shape A: code council
206:## Session shape B: ideation/strategy council (research agendas, designs, roadmaps)

/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md
6:# Multi-stream worktree orchestration
13:## THE SUBAGENT WAKE GAP (structural; discovered 2026-07-07, JouleWise 4-stream session)
49:## Topology
83:## Stream-orchestrator prompt must include
111:## Checkpoint / stop protocol (validated 3-for-3, 2026-07-07)
133:## Lead-side fleet health checks (Ed, 2026-07-07)
153:## Constraints
195:## C-028 arc amendments (2026-07-11)

/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md
6:# Operation loop (conductor score)
28:## 0a. Turn-end invariants (check EVERY turn; added 2026-07-26 after a ~10 h loss)
60:## 0. Intake and ranking
72:## 1. Decompose and shape  ✎ trace: Shape section
97:## 2. Setup
119:## 3. Model assignment — which subagent, when, and how to invoke it
202:## 4. Per-stream pipeline (owned by the stream orchestrator)
242:## 5. Lead gates
263:## 6. Post-merge integration review
270:## 7. Fleet health checks (cadence, while streams run)
278:## 8. Bookkeeping (single-writer-per-fact; C-009 consensus end-state)
333:## 9. Same-session skill distillation
341:## 10. Meta-review (closes the loop)

/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md
1:# claude-codex-report/v1 — the lead↔Sol adapter (ADJUDICATED SPEC)
9:## Lead rulings (on the six questions the design requested)
31:## External guidance addendum (Ed-directed, 2026-07-11):
32:## learn.chatgpt.com/docs/prompting — ingested, binding for Sol prompts
57:## Scope-restraint addendum (Ed-directed consult, 2026-07-11; ADOPTED)
155:## The spec (as proposed; adopted verbatim except where ruled above)
157:# Recommendation: adopt `claude-codex-report/v1`
169:## A. Report contract
249:### Core semantics
280:### Genre vocabularies
299:### Prose templates
306:## Findings
309:## Residual risk
316:## Change
319:## Verification notes
322:## Residual risk
329:## Decision matrix
332:## Composition recipe
335:## Rulings
342:## Causal chain
345:## Remediation
348:## Disproved alternatives
351:## Residual risk
358:## Scheduling matrix
361:## Critical path
364:## Delegation contracts
370:## B. Prompt template
405:### Which six parts earn their tokens
438:## C. Manifest v3
444:### `run_started`
463:### `run_finished`
485:### `run_consumed`
511:## D. Lead-side consumption
533:## E. Rulings requested

exec
/bin/zsh -lc 'nl -ba /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     1	---
     2	name: operation-loop
     3	description: The total operation loop — one invocable procedure composing intake, stream decomposition, model assignment, the per-stream Codex pipeline, lead gates, integration review, fleet health, trace capture, bookkeeping, and same-session skill distillation. Use at the start of any substantial session with multiple tasks or delegated implementation; it is the conductor score over the council, codex-delegation, adversarial-review, multi-stream-worktrees, and consistency-sweep skills.
     4	---
     5	
     6	# Operation loop (conductor score)
     7	
     8	This skill sequences the other five; it never restates their content. Each
     9	step names its instrument skill and its SKIP condition. The governing rule
    10	is cost-of-being-wrong: **every step must be skippable, and solo work must
    11	stay cheap** — a loop that cannot scale down is ritual. When in doubt,
    12	consult the trigger tiers in the council skill and pick the lightest tier
    13	that covers the risk.
    14	
    15	Trace capture is embedded per step (marked ✎), not a final chore: keep a
    16	running scratch note of shape decisions, catches, deliberations, and
    17	interventions AS THEY HAPPEN; the session entry (council-log format v2) is
    18	assembled from it in minutes, before worktree cleanup. The same scratch note
    19	collects SKILL-USAGE rows (Ed's standing instruction, 2026-07-08): which skill
    20	sections were used/skipped/deviated-from and why, appended at session close to
    21	`~/.claude/skills/skill-usage-log.md` (format in that file) — the evidence base
    22	for §10 meta-review and skill evolution.
    23	
    24	Standing cadence alongside these steps: every 10 delegated invocations, plus
    25	mandatorily at every phase boundary, run the standing fresh-eyes sweep (council
    26	skill §Standing fresh-eyes sweep — the ONE home).
    27	
    28	## 0a. Turn-end invariants (check EVERY turn; added 2026-07-26 after a ~10 h loss)
    29	
    30	These bind regardless of which step you are on. A lead does not "wait" — it
    31	ceases to exist at turn end and exists again only when something re-invokes
    32	it. There is no waiting state to occupy.
    33	
    34	- **R1 — Wake source.** End a turn only with (a) work handed off/complete, or
    35	  (b) a wake source *verified as registered with the harness*, named in the
    36	  final message ("wake source: tracked task X"). Anything with a deadline also
    37	  gets a redundant scheduled wakeup, so no single mechanism failure costs more
    38	  than one interval. Never `nohup`/`&` from Bash — use `run_in_background`.
    39	  If you cannot name the wake source, you are not waiting: keep working.
    40	- **R2 — Perishable-resource dominance.** While a perishable resource is open
    41	  (quiet measurement machine, a lease, a booked window), work that consumes it
    42	  outranks all other work. Each turn either consumes it or states in one line
    43	  why it is blocked, what re-attempts it, an act-anyway deadline, AND a
    44	  stop-loss (two consecutive same-signature failures → stop, write the handoff,
    45	  fall back to non-perishable work). Doing desk work during an open window is
    46	  the same error at lower intensity. Any heartbeat wakeup must FIRST check
    47	  whether a measurement is in flight — the wakeup itself can contaminate it.
    48	- **R3 — Premise labeling.** Any claim about the OPERATING ENVIRONMENT (harness
    49	  behavior, the user's config or availability, run-book meaning, who owns an
    50	  action) is a hypothesis until checked against a primary source. Label it as
    51	  an assumption when acting on it; never end a turn on a plan whose success
    52	  depends on an unverified one.
    53	
    54	**The disposition these correct** (Fable adjudication, 2026-07-26): the lead
    55	applies rigorous verification to *work products* — never delegates final
    56	verification, delta re-audits, refuter pairs — while exempting *its own
    57	premises about the environment*. Extend the existing verification norm to that
    58	exempted class; "be more careful" is not the fix.
    59	
    60	## 0. Intake and ranking
    61	
    62	Read run-state, task queue, latest run report; rank by value and
    63	unblocked-ness; confirm nothing re-decides a settled decision-log entry.
    64	✎ Write ONE sentence naming the user's PRIMARY OBJECT-LEVEL DELIVERABLE
    65	(the artifact they asked for, not the process around it) — step 8 checks
    66	it shipped. Added 2026-07-08 after a session executed every loop step
    67	while producing contracts ABOUT a workload suite the user had asked to
    68	actually BUILD; the user caught it, the loop didn't.
    69	SKIP: the user named the task — go to step 1 with that task (the ✎
    70	deliverable sentence is still required).
    71	
    72	## 1. Decompose and shape  ✎ trace: Shape section
    73	
    74	Split the session's work into streams; check genuine independence
    75	(expected `git diff --stat` footprints must be disjoint — shared-file
    76	streams merge or sequence; multi-stream-worktrees skill). Assign each
    77	stream a review tier by cost-of-being-wrong (council skill triggers):
    78	measurement-semantics / contract-bearing / hardware-adjacent → full
    79	pipeline; operator tooling → standard; pure calculators, docs → light.
    80	On any MID-SESSION scope addition (user directive, review fallout),
    81	re-run this step explicitly — new streams get their own tier and
    82	footprint check (2026-07-08: one design stream grew into three; the
    83	explicit re-shape kept footprints disjoint and gates per-stream).
    84	REVIEW/ASSESSMENT sessions are shaped to EMIT the next phase's work
    85	inputs, not just findings: severity-tiered verdicts PLUS a prioritized
    86	artifact/work-order list and the registry-shaped data the follow-on
    87	planning session will consume (validated + user-endorsed 2026-07-09,
    88	C-023 JouleWise rigor review: the lens fan-out's deliverable spec
    89	included per-question preparability columns and a no-hardware work
    90	order, so the planning session started from adjudicated inputs rather
    91	than re-deriving them).
    92	✎ Record: decomposition rationale, tier per stream (one line each;
    93	rationale prose only for non-default choices).
    94	SKIP: one task → single stream, no worktrees, straight to step 3 in the
    95	main tree.
    96	
    97	## 2. Setup
    98	
    99	Worktree + branch per stream; topology per the C-009 consensus table
   100	(multi-stream skill §wake gap): lead-driven codex-run pipelines with a
   101	lead-owned stream-state table for 2–4 pipeline streams; Opus
   102	orchestrators (foreground bounded waits + STALLED-handback, explicit
   103	`model:`, full prompt contract per multi-stream items 1–9) only for
   104	judgment-heavy streams. Launch subagents in one message.
   105	**VALIDATED 2026-07-08 (C-010, first full run):** the lead-driven half
   106	carried an entire 4-stream resume-to-merge session (~26 codex sessions:
   107	impl, fix rounds, 12 review lenses, integration) with ZERO wake stalls,
   108	zero heartbeats, no orchestrators at all — when every stream's design
   109	is pinned in its ledger, lead-driven is not just cheaper, it is the
   110	DEFAULT; reach for an Opus orchestrator only when a stream needs
   111	genuine mid-stream judgment the lead can't batch into gates.
   112	Preflight gates (C-009 T5): hardware-shaped streams need a concrete
   113	device inventory (probe + user confirmation of the device list — never
   114	shape streams on an ambiguous hardware claim); anything pinned without
   115	live validation carries a PROVISIONAL label; measurement sessions get a
   116	no-agent quiet lock (all fleets, cadence, and Codex load stopped first).
   117	SKIP: single stream (step 1 already decided).
   118	
   119	## 3. Model assignment — which subagent, when, and how to invoke it
   120	
   121	**GROUND TRUTH (Ed, 2026-07-07, ratification condition on the C-009
   122	consensus): FABLE IS THE APEX AND THE FINAL SAY on all high-level
   123	processes and judgments.** It is the smartest model on the team and
   124	would be used for everything if it weren't ~10× the cost — every other
   125	model's role exists to SAVE FABLE TOKENS, never because its judgment is
   126	preferred. All escalation paths terminate at Fable; all other models'
   127	outputs are advisory inputs INTO Fable's decisions; "lead" in every
   128	topology table below means the Fable main loop. When stakes are high
   129	and judgment is the bottleneck, spend Fable without hesitation. This is
   130	seniority, not omnipotence: Fable is reviewable and sometimes wrong
   131	(5.5 has overturned Fable-designed schemas on review — that is the
   132	review system working), but the ADJUDICATION of any such challenge is
   133	itself Fable's.
   134	
   135	The apex/volume split. Default to the table; record any non-default choice (✎).
   136	
   137	| Model | Use for | NOT for | Why |
   138	|---|---|---|---|
   139	| **Fable** (apex) | orchestration, stream ownership, triage, the FINAL diff gate, live/hardware verification, merge decisions, bookkeeping, skill distillation, deliberation-trace authoring | volume reading/writing Codex can do cheaper | scarce resource is Fable CONTEXT + judgment, not tokens; the merge gate is never delegated |
   140	| **Codex 5.5-high** (volume) | implementation, counterreview lenses, test writing + writer≠reviewer test review, whole-module reading/analysis, computer use, AND all security-shaped/adversarial-audit work (codex-delegation §Security) | the merge gate; live/hardware verification (no device/sudo); bookkeeping | near-limitless quota → redundant fresh-eyes passes are free; fresh instances carry no thread state → genuine independent review even of its own code; not tier-gated on adversarial vocabulary |
   141	| **Opus** (specialist sweeper / stream director) | sweeps needing harness access (suite runs, live probes) or Claude-side judgment; AND — per Ed's standing directive (2026-07-07 checkpoint session) — STREAM ORCHESTRATOR duty directing Codex threads, so Fable stays apex-only (Fable = expensive senior expert; Opus = smart director for 5.5) | default review/refutation lenses (dropped 2026-07-07: zero unique catches ≥2 sessions — Codex lenses own that) | orchestration needs judgment-above-Codex but not Fable-priced judgment; CAVEAT: Opus orchestrators hit the subagent wake gap (multi-stream-worktrees §wake gap) — lead heartbeat is required infra; AND (C-010, 2026-07-08): a full 4-stream session ran lead-driven with ZERO orchestrators and zero stalls — orchestrator duty is now the exception (genuine mid-stream judgment only), not the default |
   142	
   143	**5.5-reviews-consequential-decisions doctrine (Ed, 2026-07-07):** every
   144	consequential decision — anything binding future work, changing
   145	contracts/acceptance/process/schemas, or shipping externally — gets a
   146	Codex review, INCLUDING the lead's own decisions (batch them into review
   147	packets; one codex-run per packet). No ceremony for mechanical choices;
   148	when unsure, run it — the review is near-free and the miss isn't.
   149	Validated same-session: a lead-decision review packet overturned two
   150	lead-designed schemas with strictly better ones and contributed 7 new
   151	reviewer roles (Ledger Auditor, Merge-Order Simulator, Prompt-Contract
   152	Auditor, Outcome Label Arbiter, Claim-to-Evidence Tracer, Negative-Space
   153	Reviewer, Quiet-Machine Contamination Forecaster — spawn by name as
   154	read-only lenses when their trigger moment arrives).
   155	
   156	**Stream decision ledgers (v2; adopted + validated 2026-07-07; C-009
   157	amendments):** each stream commits `docs/stream_logs/<date>-<stream>.md`.
   158	Scope cap: ONLY decisions changing code shape, cross-stream contracts,
   159	acceptance, or future process — diff first, ledger second. Entries RIDE
   160	the code commit they justify (ledger-only commits allowed solely for a
   161	stop checkpoint). Entry IDs use the STREAM SLUG prefix (`2K-3`,
   162	`P2013-1`) — single letters collide with finding IDs. Entry:
   163	`### <slug>-<n> [who] [type] <title>` + Decision / Alternatives / Why /
   164	Evidence (artifact, commit, or lens out-file — MANDATORY; transcribed
   165	lens judgments link their source) / Confidence / Binds / optional
   166	Supersedes|Depends-on. At integration the ledger RETIRES: PROMOTE items
   167	→ decision log, checkpoint/resume state → run report, and the
   168	replacement home records the ledger's branch + final commit hash plus
   169	what was promoted vs intentionally not (C-009 pointer rule) — stream
   170	ledgers never become a growing parallel archive.
   171	`PROMOTE-TO-DECISION-LOG` marker only for durable cross-session binding,
   172	project-contract impact, or external-claim impact — the lead adjudicates
   173	promotions at the diff gate. Checkpoint rule: on any session stop, each
   174	stream's final entry is `### <S>-CHECKPOINT` recording done-units (with
   175	hashes), in-flight state, unprocessed out-files, and the exact resume
   176	action. Ledger entries are HISTORICAL — never rewritten for staleness;
   177	post-hoc state goes in a new addendum entry (a staleness lens WILL
   178	wrongly propose rewriting them; reject that class).
   179	
   180	**Delegation calibration ledger (schema v2; lead-kept per session):** one
   181	row per delegated unit: `id | to | unit | altitude (pinned-spec /
   182	design-freedom / judgment-call) | outcome | catches | lead-rework`.
   183	Outcome labels assigned by the LEAD after the gate (never self-labeled —
   184	gameable), with numeric backup (lead rework minutes, gate test failures,
   185	missed acceptance items) and prompt-defect separated from model-defect.
   186	Aggregate at session end; delegation boundaries move on this evidence,
   187	not vibes. Early signal (2026-07-07): design-freedom delegation to 5.5
   188	runs hotter than the old doctrine assumed — invited design judgment beat
   189	the lead's own designs repeatedly.
   190	
   191	**How to invoke Codex:** mechanics live in ONE home —
   192	codex-delegation §Invoke (codex-run background-call protocol; plus the
   193	sanctioned Workflow-wrapped alternative for deterministic fan-out+verify
   194	shapes, added 2026-07-08). Do not restate them here; follow that section.
   195	
   196	**How to invoke a Fable/Opus subagent:** the Agent tool with an EXPLICIT
   197	`model:` (never rely on session inheritance — a wrong-model default cost a
   198	full relaunch on 2026-07-07). Mechanics: codex-delegation + council skills.
   199	
   200	✎ Record any non-default assignment and why.
   201	
   202	## 4. Per-stream pipeline (owned by the stream orchestrator)
   203	
   204	All mechanics in the codex-delegation skill; the orchestrator stays thin.
   205	
   206	a. **Design round** — invite Codex's judgment explicitly before code.
   207	   SKIP: mechanical/spec-pinned change with no design freedom.
   208	   STRENGTHENED (Ed, 2026-07-09): for design-bearing streams the round
   209	   covers the LEAD'S SPEC ITSELF, not just open design choices — send the
   210	   stream spec/prompt to 5.5 for opinion, lead judges/revises, THEN
   211	   implementation starts against the ratified version (validated same
   212	   day: P2-030's memo→ratify-with-pins→implement flow; a spec-pinned
   213	   stream like P2-029 still skips — a ratified contract is not
   214	   re-litigated).
   215	b. **Implement** (Codex, one reviewable unit per session). Never skipped —
   216	   it is the work.
   217	c. **Counterreview lenses** — 2–3 fresh read-only Codex lenses over the
   218	   diff; findings triaged with dispositions. SKIP: docs-only/bookkeeping
   219	   diffs (light tier).  ✎ trace: catch rows for qualifying findings;
   220	   deliberation block if a finding is argued rather than accepted.
   221	d. **Test amplification** — a dedicated Codex round writes edge-case tests
   222	   beyond the implementer's. SKIP: no testable surface (docs, configs
   223	   whose validation is already pinned). MAY MERGE into the review-fix
   224	   round when the writer≠reviewer audit (e) drives the additions
   225	   (validated 2026-07-08: +6 structural test methods arrived via the fix
   226	   round, same coverage effect, one fewer round).
   227	e. **Writer≠reviewer test review** — a FRESH Codex instance audits all new
   228	   tests for tautology/vacuity/wrong expectations. SKIP: only when (d) was
   229	   skipped.
   230	f. **Failed-test triage** — any failure goes to Codex FIRST with output +
   231	   diff inline; escalate to Fable-level debugging after 2 Codex failures.
   232	   Never skipped when a test fails.
   233	g. **Fable diff gate** — the orchestrator reads the FINAL diff, weighs
   234	   findings, decides. Never skipped (thin ≠ rubber stamp). ✎ trace: catch
   235	   row if the gate finds what the lenses missed. **Mandatory lens (Ed,
   236	   2026-08-05): MERGE-ABILITY / overbuild prune** — Sol overbuilds on
   237	   occasion (surplus abstraction, more tests than the discriminating
   238	   set); the gate asks "would I want to maintain this diff" and prunes
   239	   before merge, since no downstream layer re-asks it.
   240	h. **Commit** on the stream branch; return summary + branch, not dumps.
   241	
   242	## 5. Lead gates
   243	
   244	- **Live/hardware verification** — lead-only, never delegated; drive the
   245	  real flow, not the stub. SKIP: only when the change has no runtime
   246	  surface at all (pure docs); NEVER for hardware-adjacent work.
   247	  ✎ trace: this layer's catches are historically the blockers.
   248	- **Merge decision + landing** — branch + PR for multi-commit series
   249	  (audit trail); single low-risk commits per repo convention (council
   250	  skill / D-031). **Self-merge authorization (Ed, 2026-07-08, JouleWise;
   251	  memory `merge-authority-with-review`):** the lead MAY merge its own
   252	  PRs when the merge gate ran the full shape — (a) pre-merge oversight
   253	  review by 2–3 FRESH read-only reviewers with distinct angles (deep
   254	  regression hunt on the big diff; claim-to-evidence trace on docs;
   255	  merge-order/integration simulation across sibling PRs), (b) lead
   256	  triage with recorded dispositions, (c) 5.5 fixes applied +
   257	  lead-verified, (d) CI green on the FINAL head. **Final-head rule
   258	  (validated 2026-07-08: a post-review fix commit carried a real crash
   259	  path + a broken checklist snippet):** any commit landing AFTER the
   260	  last review round gets one more fresh-eyes 5.5 pass before merge — no
   261	  commit merges unreviewed, however small the session's tail.
   262	
   263	## 6. Post-merge integration review
   264	
   265	One Codex review over merged main hunting cross-stream INTERACTION defects
   266	only, with a full suite run in the prompt (codex-delegation skill).
   267	SKIP: fewer than 2 streams merged. ✎ trace: its catches are definitionally
   268	unique (no other layer can see them).
   269	
   270	## 7. Fleet health checks (cadence, while streams run)
   271	
   272	On every stream landing, or ~hourly: classify long-runners from OUTSIDE
   273	evidence (`ps` etimes, bridge-dir mtimes, worktree `git status`) —
   274	healthy / observer / WEDGED / decomposable — and intervene per the
   275	multi-stream skill. SKIP: no background fleet running.
   276	✎ trace: every intervention gets a row (first-seen) or a tally (repeat).
   277	
   278	## 8. Bookkeeping (single-writer-per-fact; C-009 consensus end-state)
   279	
   280	- **Supersession closure (write-time; D-043-class rule, 2026-07-08):**
   281	  any change this session that superseded a prior rule gets, THIS session,
   282	  a dated amendment/supersession line on EVERY surface stating the losing
   283	  version — including the superseded decision/council entry and its index
   284	  row. The sweep verifies (consistency-sweep skill, supersession check).
   285	- **Deliverable check FIRST:** reread the §0 primary-deliverable sentence
   286	  and answer in the run report's first lines whether it SHIPPED (landed,
   287	  verified) or explicitly did not (with the handoff pointer). Process
   288	  outputs (contracts, specs, queue items) do not count as shipping an
   289	  artifact the user asked to build (2026-07-08 lesson).
   290	- **Run report = THE session record** (one file): product outcomes,
   291	  verification evidence, restart instructions, plus a `## Process Trace
   292	  Appendix` assembled from the ✎ notes — Shape, Catches, Deliberations,
   293	  Interventions, the delegation-calibration table (lives HERE as a
   294	  standing section, never scratchpad-only), Yield+spend. Written BEFORE
   295	  worktree cleanup (quotes need the bridge logs; archive per the
   296	  preservation rule first).
   297	- **Council log**: format v2 per council §Recording (the ONE home —
   298	  index row always; full entry only for genuine deliberation).
   299	- **RUN_STATE = intake pointer only**: current state ¶, latest report
   300	  link, active worktrees, verification line, next action, blockers. No
   301	  history stack (run reports own history). **Queue cells = one-liner +
   302	  pointer** — no embedded handoffs/hashes/resume text.
   303	- Decision log: any decision that binds future work (WHAT + options);
   304	  the trace appendix holds the WHY-chain and points at the D-id.
   305	  SKIP: nothing decided.
   306	- **Retired-artifact pointer rule (C-009 gap rule):** every retired
   307	  working artifact (stream ledger, superseded doc section) leaves a
   308	  discoverable pointer in its replacement home — path, branch, commit
   309	  hash, and what was promoted vs intentionally not promoted.
   310	- **One-new-artifact rule:** a session may introduce at most ONE new
   311	  process artifact class, and must name what it replaces or rides.
   312	- **Tree quiescence before bookkeeping (2026-07-09, C-025 defect):** the
   313	  two-writers rule binds the LEAD too — never edit bookkeeping in a tree
   314	  where a workspace-write codex round is (or will be) running; a fix
   315	  round's cleanup reverted the lead's uncommitted bookkeeping (recovered
   316	  only because content was deterministic from context). Either commit
   317	  bookkeeping BEFORE launching any concurrent round in that tree, or
   318	  wait for quiescence.
   319	- **Consistency sweep** (consistency-sweep skill) before the final
   320	  bookkeeping commit. SKIP: session touched no status/queue/count-bearing
   321	  docs. After a session with multiple skill edits, include ~/.claude/skills
   322	  in its scope.
   323	- Push per the standing keep-the-remote-current rule. AMENDED (Ed,
   324	  2026-07-09): checkpoint-commit CADENCE is per-artifact, not
   325	  per-session — docs/process artifacts commit+push to main the moment
   326	  they exist; stream branches push at every natural checkpoint
   327	  (implementation done pre-review, post-fix-round), labeled as
   328	  checkpoints, not only at PR time. Trigger incident: a parallel agent
   329	  couldn't find a file that sat unpushed/just-pushed mid-workflow; the
   330	  remote is the coordination surface for OTHER agents mid-session, not
   331	  just the end-of-session record.
   332	
   333	## 9. Same-session skill distillation
   334	
   335	Fold surviving lessons into the relevant skill THE SAME SESSION (validated:
   336	same-day folds prevented same-day recurrences). One-fact-one-home: each
   337	rule gets exactly one owning skill; others point. Anecdotes: one clause +
   338	trace id, never narratives. SKIP: no new lessons — do not touch skills to
   339	prove diligence.
   340	
   341	## 10. Meta-review (closes the loop)
   342	
   343	Event-driven, NOT calendar-driven. Triggers: a layer hits zero unique
   344	catches for two consecutive sessions (drop candidacy — adjudicated here,
   345	rule home council §Recording); the same intervention row gets a second
   346	tally despite a folded fix; the consistency sweep finds skill-stack
   347	drift; or the user asks. A meta-review applies this loop's own evidence
   348	discipline to the loop: per-layer yield from the traces decides what
   349	gets dropped, demoted, or promoted.
   350	
   351	**STANDING TRIGGER — post-large-workload reassessment (Ed, 2026-07-08):
   352	after any session landing a large chunk (multi-PR merge session or
   353	equivalent), run this reassessment as the FINAL step, after bookkeeping
   354	and the sweep.** Validated shape (first run 2026-07-08: 4 parallel
   355	analysts over the full council log, decision log, and skill stack +
   356	cold-start derivability audit + completeness critic; found the
   357	supersession-drift mode behind ~70% of accumulated doc defects, an
   358	operative merge-authority contradiction, and 5 skill-stack divergences):
   359	(a) skill-usage log entry finalized + evidence-complete folds applied;
   360	(b) SUPERSESSION CLOSURE verified — every rule the session superseded has
   361	dated amendment lines on all losing surfaces (write-time rule: §8;
   362	sweep-time check: consistency-sweep skill);
   363	(c) spend-per-catch and calibration-ledger LONGITUDINAL read — outcome
   364	distribution across sessions, not just this session's rows; model-defect
   365	rows (B-44 class) tracked as a class;
   366	(d) disposition-to-commit closure — accepted review findings traced to
   367	commits/queue rows, not just recorded;
   368	(e) layer-overlap check — overlapping layers assessed for marginal yield
   369	before both are credited (council §Recording owns the drop rule);
   370	(f) derivability spot-check when new practices were validated — could a
   371	fresh agent reconstruct them from persisted artifacts?
   372	SKIP: no trigger fired (small sessions: the standing trigger does not
   373	fire for single-PR or docs-only sessions).

exec
/bin/zsh -lc "rg -n 'D-061|D-080|fresh-eyes|zero unique|zero-unique|three applicable|10 delegated|cadence|service.?tier|CODEX_SERVICE_TIER|fast tier|per-call' docs/decision_log.md docs/orchestration.md RUN_STATE.md scripts .agents .codex 2>/dev/null" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
docs/orchestration.md:161:  attributed and tallied per session under D-061 (C-027; replaces the
docs/orchestration.md:167:  weights are fixed before the session; three applicable exposures
docs/orchestration.md:171:  dropped under the old rule before D-061.)
RUN_STATE.md:205:Codex Fast Mode (`CODEX_SERVICE_TIER=fast`), #103 coldgate validator,
RUN_STATE.md:343:  (codex-run-v3 does not read CODEX_SERVICE_TIER — do not modify Ed's
RUN_STATE.md:431:2. **Codex Fast Mode (service tier)**: 1.5x speed / 2.5x credits;
RUN_STATE.md:432:   Ed specified the exact bridge implementation (per-call opt-in via
RUN_STATE.md:433:   `CODEX_SERVICE_TIER=fast`, never a standing default) — being
RUN_STATE.md:682:   alive (or waits for QUIET-GUARD), D-080 runner choice, NVIDIA +
RUN_STATE.md:721:   D-080 runner, QUIET-GUARD's four questions).
RUN_STATE.md:862:- D-080 runner choice (cron vs manual); QUIET-GUARD's four questions;
RUN_STATE.md:922:**Ed rulings tonight (ratification via packet):** R1 — fresh-eyes
RUN_STATE.md:923:sweep cadence is WORK-CHUNK-ANCHORED (post-consumption of substantial
RUN_STATE.md:927:the D-080 amendment ratifies it. R2 — cold gate uses
RUN_STATE.md:1080:- NVIDIA plan ratification; D-080 trigger cadence (`D080-TRIGGER-01`);
RUN_STATE.md:1154:  modules) + Lever 2 (fast tier) + Lever 3 (Blacksmith, your call)
RUN_STATE.md:1178:  (6.5×); fast tier → 25-40s PR feedback (full suite stays the merge
RUN_STATE.md:1314:   [run_started event, failure+0.250 s] (~5 lines; cadence clause
RUN_STATE.md:1951:zero deletions clear D-061; PR-fast/full split is Ed's call).
RUN_STATE.md:2299:an enumerated forbidden-to-decide-alone list for the lieutenant. D-080's
RUN_STATE.md:2300:standing fresh-eyes sweep is the first exercise of that list.
RUN_STATE.md:2310:3. A magistrate ruling on a conflict between D-080 and D-061: D-080's
RUN_STATE.md:2312:   two-zero-sessions drop rule, which D-061 explicitly superseded with an
RUN_STATE.md:2313:   expected-loss adjudication ("three applicable exposures TRIGGER an
RUN_STATE.md:2399:- 2026-07-30 D-080 fresh-eyes sweep memos (techniques, mechanisms,
RUN_STATE.md:2413:  critical path; D-079/D-080): `docs/process_traces/RESUME-2026-07-28.md`
RUN_STATE.md:2611:  retained failure emitted `cadence_ratio_unrecorded` plus
docs/decision_log.md:86:| D-061 | Review-layer evaluation rule v2 | accepted |
docs/decision_log.md:105:| D-080 | Standing fresh-eyes sweep: a periodic, non-reactive outside review on one cadence unit, a rotating second lens, and a mechanically generated packet | accepted (magistrate-ratified 2026-07-27) |
docs/decision_log.md:1277:Revisit when: a need appears that is per-call rather than per-run (then
docs/decision_log.md:1278:a per-call argument is correct, not a context field), or Phase 3's
docs/decision_log.md:1697:`[1,n]`, `n >= 3*(L+1)`, and a type-7 linear p95/p05 cadence ratio no greater
docs/decision_log.md:1699:duration use `rel_tol=1e-9` and `abs_tol=1e-12`. Irregular cadence fails closed
docs/decision_log.md:2999:codes (insufficient_in_window_samples, cadence_ratio_unrecorded/below,
docs/decision_log.md:3209:## D-061: Review-layer evaluation rule v2 (replaces the two-zero-sessions drop rule)
docs/decision_log.md:3216:falsified by its own record — integration review returned zero unique
docs/decision_log.md:3228:the session; (d) three applicable exposures TRIGGER an expected-loss
docs/decision_log.md:3423:source. Council-log layer-yield claims (D-061) should cite manifest
docs/decision_log.md:3471:   types, per-call reverse-consult `effort` (`high`|`xhigh`) with an
docs/decision_log.md:4024:cadence from manufacturing coverage. Frozen-anchor provenance prevents a
docs/decision_log.md:4104:  `insufficient_in_window_samples`, `cadence_ratio_unrecorded`,
docs/decision_log.md:4105:  `cadence_ratio_below_threshold`, `clock_bound_unrecorded`,
docs/decision_log.md:4490:   powermetrics cadence). Two doctrine amendments were then ruled by the
docs/decision_log.md:4721:sampling cadence / `joint_loss_sublevel_interval_branch_v2` estimator
docs/decision_log.md:4745:   power policy, sampling cadence, and a freshness horizon, with a distinct
docs/decision_log.md:4918:power policy, sampling cadence, or estimator identity changes; or a
docs/decision_log.md:4922:## D-080: Standing fresh-eyes sweep — a periodic, non-reactive outside review
docs/decision_log.md:4954:1. **A standing fresh-eyes sweep is adopted, on ONE cadence unit.** The sweep
docs/decision_log.md:4955:   runs every **10 delegated invocations**, plus mandatorily at every **phase
docs/decision_log.md:4959:   *Options considered.* (a) The lieutenant's draft cadence — an OR over
docs/decision_log.md:4962:   to argue about whether the mechanism fired, and a cadence that can be argued
docs/decision_log.md:4963:   about is a cadence that will be argued away. (b) Wall-clock as the unit —
docs/decision_log.md:5018:   zero-unique-catch rule: a rotating lens with zero plan-changing catches over
docs/decision_log.md:5029:   on evidence (D-061). (b) Count all catches — rejected: catch counts that
docs/decision_log.md:5051:forbidden-to-decide-alone list: ratifying process rules, changing cadence
docs/decision_log.md:5055:edits to wording but reversals of the draft's cadence design, its lens
docs/decision_log.md:5059:pays for that exception, and D-061's evidence discipline for review layers
docs/decision_log.md:5065:cadence unit, a rotating second lens, a mostly mechanical packet, and an
docs/decision_log.md:5071:cadence number 10 is calibrated against the model-allocation ledger; a rotating
docs/decision_log.md:6060:   luck. The consult refuted the lead's cadence-drift mechanism.
docs/decision_log.md:6217:  RUN_STATE end-of-work step 8, DRIFT.md cadence
docs/decision_log.md:6696:   ~5-line decidable-superset control; the cadence-consistency clause
docs/decision_log.md:6777:   deletions (D-061-clean); full coverage persists in the site lane.
scripts/mint_floor_artifact.py:879:    cadence_ratios: list[float] = []
scripts/mint_floor_artifact.py:911:            cadence = _finite(
scripts/mint_floor_artifact.py:912:                window.get("cadence_ratio"),
scripts/mint_floor_artifact.py:913:                f"{member.bundle_id} cadence ratio",
scripts/mint_floor_artifact.py:932:            cadence_ratios.append(cadence)
scripts/mint_floor_artifact.py:944:        "cadence_ratio_min": min(cadence_ratios),
scripts/codex-bridge:23:  CODEX_SERVICE_TIER=fast scripts/codex-bridge new ...
scripts/codex-bridge:151:codex_service_tier="${CODEX_SERVICE_TIER:-default}"
scripts/codex-bridge:152:case "$codex_service_tier" in
scripts/codex-bridge:155:    printf 'Invalid CODEX_SERVICE_TIER: %s (expected default or fast)\n' \
scripts/codex-bridge:156:      "$codex_service_tier" >&2
scripts/codex-bridge:160:fresh_model_args=(-m "$codex_model" -c "model_reasoning_effort=$codex_effort" -c "service_tier=$codex_service_tier" -c "mcp_servers.claude.enabled=false")
scripts/codex-bridge:161:resume_model_args=(-c "model=$codex_model" -c "model_reasoning_effort=$codex_effort" -c "service_tier=$codex_service_tier" -c "mcp_servers.claude.enabled=false")
scripts/codex-bridge:306:      --service-tier "$codex_service_tier" \
scripts/codex-bridge:368:    printf ',"service_tier":%s' "$(json_quote "$codex_service_tier")"
scripts/codex-app-bridge.mjs:32:const serviceTier = args.get("service-tier") ?? "default";

exec
/bin/zsh -lc 'nl -ba /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     1	---
     2	name: council
     3	description: Event-driven multi-model review council — decide when work needs full cross-model review (Claude lead + Codex peer + Opus sweeps), run the session shape, record it in the project's council log. Use when landing adapters/contract changes/multi-commit series, when a sub-agent's work needs counterreview, or when the user asks for council/cross-model review.
     4	---
     5	
     6	# Event-driven multi-model council
     7	
     8	A council is cross-model review with discussion — not ceremony. Its value is
     9	uncorrelated blind spots (validated: in one JouleWise session, live hardware
    10	verification, a same-model adversarial workflow, a Codex reverse-review, and
    11	Opus sweeps EACH caught a real issue every other layer missed). Convene it by
    12	trigger, never by ritual; the loop must scale with the cost of being wrong.
    13	
    14	## Triggers (event-driven — pick the LIGHTEST tier that covers the risk)
    15	
    16	**Full council** (implement → verify → adversarial review → counterreview → discussion):
    17	- New adapter/backend, or any change to shared contract-bearing code
    18	- Anything hardware-adjacent (sub-agent "tests green" is never sufficient there)
    19	- Pre-merge review of a multi-commit series (include a REVERSE review: the peer
    20	  reviews the lead's commits and orchestration decisions — that direction caught
    21	  what all lead-side layers missed)
    22	- Genuine design disagreement between models, or the user asks for it
    23	
    24	**Light review** (single Opus sweep or single peer pass, no discussion round):
    25	- Bookkeeping/docs commits, config-only changes, mechanical refactors
    26	
    27	**Solo** (no council):
    28	- Single-file low-risk edits, conversational turns, work already council-reviewed
    29	
    30	## Standing fresh-eyes sweep (periodic, non-reactive; ratified 2026-07-27, D-080)
    31	
    32	Every trigger above is REACTIVE — it fires on a recognised problem, so a trigger
    33	catches only what you can NAME. The two costliest failures of 2026-07-26/27 —
    34	ten hours of an open measurement window lost to an untracked background job, and
    35	six fix rounds building a guard on the wrong axis — were nameless until
    36	postmortem, so no trigger could fire. The sweep exists for that class. The
    37	orchestration topology it runs inside (magistrate / lieutenant / cold gate) is
    38	global CLAUDE.md rule 11 — referenced, never restated here.
    39	
    40	**Cadence — ONE unit, not several.** Every **10 delegated invocations**, plus
    41	mandatorily at every **phase boundary**. A multi-way OR-cadence over invocations
    42	/ wall-clock / phase boundaries was explicitly REJECTED: three counters means
    43	three ways to argue about whether it fired. Wall-clock is rejected outright as a
    44	unit — "active session work" is a clock nobody keeps, and three hours of
    45	bookkeeping is not three hours of hot integration. Invocation count is already in
    46	the manifest stream, scales with work density, and is unarguable. **The number 10
    47	is PROVISIONAL — calibrate it against `docs/process/model_allocation_ledger.md`
    48	after two sessions.**
    49	
    50	**Composition — rotate.** **Cold Fable every sweep** (fresh session, no loop
    51	context) — it is the raison d'être, the only lens targeting the nameless failure
    52	class, and it never rotates out. **Plus ONE rotating second lens**, alternating
    53	the Opus contract lens and the Sol execution lens. All three run only at phase
    54	boundaries, or when the cold lens flags something material. Why rotate rather
    55	than run both every time (this corrects a miscitation): the execution lens's
    56	famous catches — a 5e-324 floor exploit, a wall-clock slew, GPU DVFM aliasing —
    57	were all made in REACTIVE review with a specific artifact to run. A sweep arrives
    58	with NO question in hand, and an execution lens with no target degenerates to
    59	"run the tests again." Contract and execution are verification lenses, and the
    60	existing gauntlet already exercises both reactively at every review.
    61	
    62	**Packet — six sections, five of them MECHANICALLY GENERATED.** This is the crux.
    63	A packet organised around "the assembler's evidence against itself" contains only
    64	NAMED doubts — the exact thing the sweep exists to escape; if the assembler could
    65	state the case against, it would not need fresh eyes. The assembler's blind spots
    66	ARE the target, so its hit rate must not be load-bearing. Sections (a)–(e) are
    67	generated from manifests and logs, NOT composed:
    68	
    69	(a) the phase objective VERBATIM as stated at phase start — drift between the
    70	    objective stated and the objective pursued is what cold eyes spot;
    71	(b) the mechanical log since the last sweep: invocations, one-line outcomes, and
    72	    ROUND COUNTS PER OBJECTIVE — round counts expose the six-round-guard pattern
    73	    without anyone having to recognise it;
    74	(c) time and spend against plan — exposes the ten-hour-loss shape;
    75	(d) the next three planned actions;
    76	(e) open anomalies INCLUDING everything observed and explained away —
    77	    explained-away anomalies are where a time-anchor defect and a screensaver
    78	    contamination both hid;
    79	(f) composed, and only one section among six: current beliefs and the steelman
    80	    against them.
    81	
    82	**Anti-ritual.** (i) Only **plan-changing** catches count — a catch that altered
    83	no decision is ritual's camouflage. (ii) Measured over SESSIONS, matching the
    84	existing zero-unique-catch drop rule: a rotating lens with zero plan-changing
    85	catches over two full sessions rotates down; the cold lens is evaluated on a
    86	one-phase window and is not exempt. (iii) The MECHANISM ITSELF is falsifiable —
    87	if the whole sweep produces no plan-changing catch across one full phase, it
    88	returns to the magistrate for termination or redesign. The real anti-ritual guard
    89	is the mechanical packet: ritual enters through the packet first.
    90	
    91	**Relationship to reactive triggers — supplement, never replace.** All mandatory
    92	reactive triggers stand unchanged. One asymmetric reset rule: a trigger consult
    93	may reset the sweep counter ONLY IF its packet included the sweep's mechanical
    94	sections (the function — outside eyes on raw state — was just served). A sweep
    95	NEVER satisfies a trigger, because a trigger consult has a specific question a
    96	decision is waiting on. No mechanism may be skipped on the theory that the other
    97	covers it.
    98	
    99	**Records.** Sweep outcomes go to `docs/council_log.md` with PER-LENS
   100	attribution, feeding `docs/process/model_allocation_ledger.md`.
   101	
   102	## Roles
   103	
   104	- **Lead (Claude/Fable, main loop)** — scopes, diagnoses live failures, owns the
   105	  merge decision and bookkeeping, and is the only member that runs real
   106	  hardware or touches anything outside sandboxes. Never delegates final
   107	  verification — and (Ed, 2026-07-07) never delegates the FINAL REVIEW of
   108	  anything important: Codex lenses inform, but the last judgment pass over
   109	  the final diff is always Fable-level (stream orchestrator for its stream,
   110	  lead for the merge).
   111	- **Peer (Codex/gpt-5.5 or equivalent second model)** — implements against pinned
   112	  specs, counterreviews findings on its own code, reverse-reviews the lead.
   113	  Always ask for design judgment EXPLICITLY ("argue the tradeoffs before you
   114	  code") — invited judgment has repeatedly out-designed the lead (3+ sessions
   115	  through C-015; see the calibration ledgers)
   116	  proposals. See the codex-delegation skill for mechanics; the spend doctrine
   117	  (counterreview after EVERY implementation is the default, drop-a-layer on
   118	  signal quality only) lives in codex-delegation §Economics — not restated
   119	  here.
   120	- **Sweepers** — parallel low-level threads: commit hygiene, docs consistency,
   121	  fixture audits. Since 2026-07-07 the default sweeper is a read-only Codex
   122	  lens (invoked per codex-delegation's ONE stable mechanism — `codex-run
   123	  ... -s read-only`, never bare `codex exec`) — near-free, so run many. Claude-family
   124	  sweepers (Opus/Fable subagents) only where the sweep needs harness access
   125	  (running suites, live probes) or Claude-side judgment; keep Fable for the
   126	  highest-level orchestration and skill distillation only.
   127	
   128	## Discussion protocol
   129	
   130	- Findings go to the author as a peer: "refute or fix, with reasoning" — never
   131	  silent application. Bound discussion to 1–2 rounds; on unresolved
   132	  disagreement the lead decides and records the dissent.
   133	- Only design-bearing findings (blockers, architecture, conventions) get
   134	  discussion; nits are applied or dropped directly.
   135	- Ask one explicit judgment question at the end of any fix round ("does X
   136	  deserve a queued hardening task?") — cheap, and surfaces the peer's view of
   137	  blast radius.
   138	
   139	## Recording + instrumentation
   140	
   141	- Every session gets an INDEX ROW in the project's council log
   142	  (`docs/council_log.md` or equivalent; create it if absent — companion to the
   143	  decision log: decisions record WHAT, the council log records HOW review got
   144	  there). FORMAT v2 (C-009 consensus, 2026-07-07; supersedes the original
   145	  every-session-full-entry rule): index row ALWAYS; a FULL entry only for
   146	  genuine deliberation — disputed reasoning, durable doctrine changes, unique
   147	  catches, position reversals; never restate stream/product state the run
   148	  report already holds. Full entry = participants, subject, findings that
   149	  survived, positions → resolutions, dissents, follow-ups. No transcripts.
   150	- Record per-layer unique catches and rough token spend per entry. SPEND
   151	  SNAPSHOT (2026-07-11, first exercised in C-028): capture spend from
   152	  `codex-usage` (`~/.local/bin/codex-usage`, or `--json` for machine
   153	  capture) at entry close — per-effort-tier sessions/tokens table plus the
   154	  quota signal — and pair it with the Fable-side triple (generation /
   155	  billed-ish / cache-reads) from the lead's own accounting. Paste the
   156	  snapshot (or its one-line summary) into the entry's spend section; label
   157	  estimates as estimates, not billing truth. Composition note when relevant:
   158	  Sol volume is ~97% cached input, so token counts and cost rank layers
   159	  differently — say which one a drop/keep argument is using.
   160	  with zero unique catches across two consecutive sessions is a DROP
   161	  CANDIDATE — the drop itself is adjudicated (operation-loop §10), decided on
   162	  signal quality only, never on cost (codex-delegation §Economics), and
   163	  "unique" means unique-against-all-layers: when two layers overlap (e.g.
   164	  pre-merge oversight vs pre-commit docs-verify), assess marginal yield
   165	  before crediting both — a layer can look alive by racing an overlapping
   166	  layer to the same findings (meta-reassessment, 2026-07-08). The council
   167	  must justify itself with the same evidence discipline it enforces.
   168	- Process-level outcomes (conventions adopted, e.g. PR-per-series) also get a
   169	  decision-log entry so they bind future sessions.
   170	- Orchestration meta-review (standing, Ed 2026-07-07): every few sessions the
   171	  council reviews the ORCHESTRATION itself — delegation splits, stall modes,
   172	  prompt-contract gaps, model-assignment mistakes — and the surviving lessons
   173	  are folded back into the global skills (council, codex-delegation,
   174	  multi-stream-worktrees, adversarial-review) the same session, not deferred.
   175	  Known examples worth checking each time: poll-vs-await stalls, subagents
   176	  silently inheriting the wrong model, orchestrators ending turns mid-loop
   177	  (mechanics live in codex-delegation §Token-efficient consumption and
   178	  multi-stream-worktrees §Topology / §Lead-side fleet health checks).
   179	- DELIBERATION TRACES (standing, Ed 2026-07-07): record as much of the
   180	  council deliberation as makes sense — for each design-bearing disagreement:
   181	  the positions, the actual reasoning exchanged, what resolved it, who
   182	  prevailed and why, dissents overridden. Audience: a future model reading
   183	  back to understand WHY a decision was made, not just what was decided.
   184	  Fable authors all traces (Ed: best model for it). Mechanics: every stream
   185	  orchestrator's final report carries a DELIBERATION TRACE section (capture
   186	  the WHY before the orchestrator's context is gone); raw exchanges live in
   187	  worktree .codex-bridge/*.log — archive these before worktree removal, and
   188	  quote short key exchanges in traces where the wording itself carries the
   189	  reasoning. Resolved nits are noise; design-bearing disagreements — 
   190	  especially where one model out-argued another — are the signal.
   191	
   192	## Session shape A: code council
   193	
   194	1. Scope one reviewable unit; peer implements (own worktree if parallel
   195	   streams — see multi-stream-worktrees skill).
   196	2. Lead verifies claims independently: full test suites + live paths. Never
   197	   skip; this layer has caught every hardware bug to date.
   198	3. Adversarial review (see adversarial-review skill for the tiered workflow).
   199	4. Confirmed findings → peer counterreview + bounded discussion.
   200	5. Lead re-verifies live, lands the result (branch + PR for multi-commit
   201	   series; merge authority per operation-loop §5 — Ed's 2026-07-08 standing
   202	   grant lets the lead self-merge after the full gate shape), writes the
   203	   council log entry, runs the
   204	   consistency-sweep skill before the final bookkeeping commit.
   205	
   206	## Session shape B: ideation/strategy council (research agendas, designs, roadmaps)
   207	
   208	Convene when the decision is directional (what to build/measure/claim), not
   209	a diff. Validated pattern:
   210	
   211	1. **Parallel divergent threads, one lens each** — e.g. DESIGN (propose the
   212	   concrete mechanism), MAXIMIZE (what more could we get), **EXAMINER
   213	   (thesis-committee style: test whether the claims would survive a hostile
   214	   expert — name the confounds, the identifiability limits, the "you
   215	   measured X but claim Y" gaps — then state the minimal version that
   216	   passes)** — plus an Opus **ground-truth audit** that parses the actual
   217	   artifacts/data rather than reasoning from docs. The examiner thread is
   218	   not optional: it produced the sharpest input every time it ran, and the
   219	   ground-truth audit repeatedly found decisive facts nobody's reasoning
   220	   surfaced (fields already captured but discarded; contamination visible
   221	   in raw data). Frame the examiner as a committee member invested in the
   222	   work passing IF it deserves to — not an assigned contrarian; "argue
   223	   against regardless" invites strawmen, while "would this survive the
   224	   defense" invites the real objections.
   225	2. **Lead adjudicates** conflicts between threads explicitly — name which
   226	   objection kills which version of the idea and what construction
   227	   survives it.
   228	3. **Synthesis goes to a FINAL EXAMINER before it's presented as settled**:
   229	   a fresh-context strong-model agent (Fable-tier, spawned — never the
   230	   lead reviewing its own synthesis; the lead has sunk-cost attachment)
   231	   with a committee rubric: claim→evidence chain, threats to validity,
   232	   what reviewer-2 says, verdict pass / major-revision / reject. Cross-model
   233	   (Codex) synthesis review is additionally cheap and worth keeping when
   234	   its usage is free — diversity and fresh-context independence catch
   235	   different things.
   236	4. Record as a council-log entry with votes and the surviving/killed
   237	   versions both named — killed ideas with reasons are as valuable as
   238	   adopted ones.
   239	
   240	Default to MORE divergent threads, not fewer: 3–5 parallel peer sessions per
   241	ideation council is the efficient shape, since divergence is the whole point
   242	(spend doctrine: codex-delegation §Economics).

exec
/bin/zsh -lc 'nl -ba /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md && nl -ba /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     1	---
     2	name: adversarial-review
     3	description: Token-tiered adversarial review workflow — scout a review packet, fan out review lenses, verify findings proportionally to severity (blockers get 2 refuters, nits get none), with fresh read-only Codex refuters by default (Opus on demand for judgment-heavy verification). Use when reviewing a diff, an adapter, or a sub-agent's implementation before landing it.
     4	---
     5	
     6	# Tiered adversarial review
     7	
     8	Findings that haven't survived a refutation attempt are opinions. But
     9	verifying everything equally is the token hog (an untired 22-agent review ran
    10	~700k tokens, mostly 12 verifiers re-reading identical files). Tier the
    11	verification to the cost of being wrong.
    12	
    13	## Shape
    14	
    15	1. **Scout (one agent, or inline if trivial):** build a review packet ONCE —
    16	   the diff, the relevant contract/spec excerpts, the seam files' key
    17	   sections. Hand the packet to every reviewer; don't let N agents rediscover
    18	   identical context.
    19	2. **Lenses (parallel; default executor: fresh read-only Codex 5.5
    20	   instances** — `codex exec -C <repo> -s read-only -o <outfile> "<prompt>"
    21	   < /dev/null`, per codex-delegation §Parallel threads and §Division of
    22	   labor): 2–4 lenses with DISTINCT perspectives (contract compliance /
    23	   correctness / test adequacy; or security / perf / does-it-reproduce).
    24	   Distinct lenses catch failure modes redundant reviewers can't.
    25	   Schema-constrained findings:
    26	   `{title, file, line_hint, severity: blocker|should-fix|nit, argument,
    27	   suggested_fix}`. Instruct: "be selective; an empty list is a valid answer."
    28	3. **Tiered verification (parallel; default refuters are ALSO fresh
    29	   read-only Codex instances** — a fresh instance carries no thread state,
    30	   so it is independent even of another Codex lens's finding.
    31	   Claude-family/Opus refuters remain AVAILABLE at lead discretion for
    32	   judgment-heavy verifications or when refutation needs harness access
    33	   (running suites, live probes) — but they are no longer the default tier:
    34	   dropped per the council-log C-006 yield ledger, zero unique Opus-refuter
    35	   catches since C-001):
    36	   - **blocker** → 2 independent refuters ("try to REFUTE by reading the
    37	     actual code; default is_real=false if the argument doesn't hold");
    38	     survives only if both confirm.
    39	   - **should-fix** → 1 refuter.
    40	   - **nit** → 0 (accept/drop at the discussion stage; they're cheap to be
    41	     wrong about).
    42	   Verifiers may correct severity in either direction; a nit re-graded to
    43	   blocker gets the blocker treatment in a second pass.
    44	   REFUTER PROMPTS INVITE REPRODUCTION, not just code reading (validated
    45	   2026-07-08, two review rounds): the strongest refutations RAN the thing —
    46	   regenerated configs with pre/post scripts to prove a silent-omission
    47	   path, executed dead probes live on the DUT, ran a differential repro of
    48	   an evidence regression on both branches. Say "verify by reproducing
    49	   where feasible" in the refuter prompt; a repro-backed confirm/refute
    50	   ends the argument, a read-only one just continues it.
    51	4. **Return** confirmed findings + the refuted list (refutations are
    52	   calibration data — a lens with a high refutation rate needs a better
    53	   prompt).
    54	
    55	## Document-shaped artifacts (added 2026-07-08)
    56	
    57	When the review target is a DOCUMENT that makes factual claims (a critique,
    58	status report, or external review of the project), the scout step becomes a
    59	claim-by-claim FACT-CHECK: enumerate every checkable claim, verify each
    60	against the repo with file:line evidence, and return verdicts (TRUE / FALSE
    61	/ STALE / UNVERIFIABLE) — an Explore-type agent does this in one pass and
    62	the lead judges only the verdict list. Two additions to the lens set:
    63	- a **staleness lens** — a claim can be TRUE at authoring time and FALSE
    64	  now; check status-bearing claims against CURRENT doc/checklist state and
    65	  report "was-true-now-stale" separately from "wrong".
    66	- a **self-provenance lens** when the document describes its own history
    67	  ("retained as record", "addendum-only") — verify those meta-claims against
    68	  the actual diff; see the self-describing-documents field note under
    69	  codex-delegation §Token-efficient consumption. This lens produced a
    70	  2026-07-08 session's only blocker.
    71	Ground the fact-check's canonical numbers by RUNNING the commands (test
    72	suite, git log), never by trusting any doc (same rule as consistency-sweep).
    73	
    74	## Severity rubric (keep lenses consistent)
    75	
    76	- **blocker:** wrong data reaches an artifact, a stated design decision is
    77	  silently defeated, or users/hardware pay a real cost before failure surfaces.
    78	- **should-fix:** real defect or unpinned guarantee with bounded blast radius;
    79	  runs still complete honestly.
    80	- **nit:** hygiene, redundancy, style with a concrete argument.
    81	
    82	## Rules of thumb
    83	
    84	- The reviewed code's own tests being green means nothing here — the strongest
    85	  catch to date (a fabricated 0.0 W measurement baseline) lived in a fully
    86	  green suite.
    87	- Review the working tree or `git diff` directly, not transcripts of the
    88	  implementer's session.
    89	- Findings go onward to the author for counterreview, not straight to
    90	  application (see the council skill).
    91	- Cost now lands mostly on near-free Codex quota (codex-delegation
    92	  §Economics); the packet still pays for itself by keeping every lens
    93	  focused and the main loop consuming only findings, never re-reads.
    94	  Claude-side reference point (historical): 3 lenses ≈ 100–150k tokens with
    95	  the packet; tiered verification ≈ half of untiered at equal confidence.
    96	
    97	## C-028 arc amendments (2026-07-11; empirically validated over ~16 refuters)
    98	
    99	- **Delta re-audit after EVERY fix round.** Twice this arc a fix round
   100	  introduced fresh defects (p2041: symlink crash; p2037: unit-mismatch +
   101	  strata crash in newly-reachable paths). A bounded re-audit of only the
   102	  fix delta caught both. Fix rounds are first drafts, not closers.
   103	- **Blocker refuter pairs get DISTINCT lenses (contract-authority vs
   104	  reachability/execution), not two identical skeptics.** Split verdicts
   105	  are the system working: B1 (p2041) and F1 (p2037) both split
   106	  confirmed-vs-refuted, and the lead's synthesis (narrowed rulings) was
   107	  better than either verdict alone. Never resolve a split by majority —
   108	  synthesize from both evidence chains.
   109	- **Arc verdict distribution** (~16 refuters): ~70% confirmed, ~15%
   110	  narrowed, ~15% refuted. The narrowings carried the most value
   111	  (prevented over-fixing); the refutations killed convergent two-lens
   112	  findings via one empirical corpus check. Refuters that EXECUTE
   113	  counterexamples (readiness returned [], lint accepted the bad row)
   114	  end debates; prefer executable-proof briefs over argumentative ones.
   115	- **Integration findings refute like any others**: the review-blocker
   116	  that survived did so with binding contract citations; the lead's own
   117	  contract instinct was the thing refuted. Run refuters even when the
   118	  lead "knows" the contract.
   119	
   120	## D-078 close-out amendments (2026-07-22; 3 lenses + 11 refuter runs)
   121	
   122	- **Phrase refuter briefs as data-quality QA, not attack narratives.** An
   123	  upstream cyber-content filter killed 3/8 Codex refuters MID-RUN (60-127k
   124	  tokens lost each) on briefs dense with "malformed/tamper/escape/oversized
   125	  ...integers" language about our own instrument's input validation.
   126	  Reframing the identical technical content as "physically impossible
   127	  sensor metadata" / "robustness QA of our own measurement pipeline"
   128	  (context sentence up front, mechanism-neutral verbs) recovered all three
   129	  with full-quality verdicts. This composes with codex-delegation §Security:
   130	  even when the adversarial layer IS routed to Codex, the brief's framing
   131	  matters.
   132	- **Provenance-attribute before triaging scope findings.** A delta-audit
   133	  lens correctly flagged two out-of-scope edits as blockers — both were
   134	  the LEAD's own authorized bench edits made in the same tree. A lens
   135	  cannot see edit provenance; the lead triages "who wrote this" before
   136	  severity. (Related field note in codex-delegation: never bench-edit a
   137	  worktree while an enforced-scope session is live in it.)
   138	- **False-positive economics held**: of 9 lens findings this session, 3
   139	  were refuted, 1 narrowed to nit, 2 were lead-attribution artifacts —
   140	  and the 3 that survived included a genuine understated-uncertainty
   141	  blocker two prior audited rounds had missed. The tiered-refuter spend
   142	  is what separated them.
   143	
   144	## C-033 pairing amendments (2026-07-25; PR #85 gauntlet, 4 audit rounds + 3 refuter rounds)
   145	
   146	- **Default blocker-refuter shape is now the CROSS-MODEL pairing: Opus 5
   147	  contract/design lens + Sol execution lens** (Ed-directed A/B, validated
   148	  across three rounds — changed the triage outcome in every round it ran:
   149	  collapsed one blocker, re-priced two, refuted two proposed fixes before
   150	  they landed, and produced one blocker the auditor never saw). Model
   151	  diversity stacked on lens diversity catches what either alone misses.
   152	  Ed's cost order (2026-07-24): Sol ~free, Opus ≈ half Fable; use both
   153	  liberally. Supersedes the C-006 "zero unique Opus-refuter catches"
   154	  ledger read — that measured Opus as a REDUNDANT lens, not a distinct one.
   155	- **Effort ruling (C-033): in the paired-lens shape, `high` is the
   156	  default refuter tier** — the pairing's decisive catches all landed at
   157	  high; reserve `xhigh` for single-refuter verification or standalone
   158	  judgment-dense audits. (The old "xhigh refuters by default" applied to
   159	  same-model pairs.)
   160	- **Auditor severity inflation is systematic, not incidental:** across
   161	  rounds 1-2 only 3-4 of 7 blocker-tier claims survived refutation at
   162	  tier, while ALL findings' mechanisms were real. Budget triage time for
   163	  re-pricing, and never fast-track a fix on the auditor's tier alone.
   164	- **Dictated-fills verification is a real catch layer:** the C-033
   165	  drafting agent caught five material errors in the lead's dictation
   166	  (effort tiers, counts, a non-green gate). Route council/run-report
   167	  finalization through it by default (Opus tier per instrument-mix).
     1	---
     2	name: consistency-sweep
     3	description: End-of-session docs-consistency sweep — delegate a sweep agent to find stale counts, gate-state contradictions, and cross-referenced numbers that drifted across process docs (and across the global skills), before the final bookkeeping commit. Use at the end of any session that updated status/queue/checklist docs or edited multiple skills, or when docs are suspected stale.
     4	---
     5	
     6	# Docs-consistency sweep
     7	
     8	Process-heavy repos duplicate state (test counts, gate status, headline
     9	numbers) across README, status docs, run-state, queues, checklists, and
    10	reports — and prose summaries drift the moment work moves fast. One delegated
    11	sweep (Opus, ~50–80k tokens, a few minutes) has repeatedly found 5–10 real
    12	inconsistencies that both the lead and a peer reviewer then independently
    13	confirmed. Run it BEFORE the final bookkeeping commit, not after.
    14	
    15	## Delegation prompt shape
    16	
    17	Executor: the council skill §Roles sweeper default is a read-only Codex
    18	lens UNLESS the sweep needs harness access — this sweep usually does (it
    19	must RUN the test suite and git commands for ground truth), so a
    20	Claude-family agent (Agent tool, `model: "opus"`) is the justified default
    21	here; use a Codex read-only lens only for a docs-only sweep with no
    22	commands to run.
    23	
    24	Give the agent:
    25	1. The explicit file list: README, the advisor/status doc, run-state, task
    26	   queue, phase/exit checklists, decision + risk + council logs, and the
    27	   session's run reports. After any session that edited 2+ files under
    28	   `~/.claude/skills/`, include those SKILL.md files — inter-skill drift is
    29	   in scope: duplicated doctrine that diverged, pointers naming sections
    30	   that no longer exist, contradictions between a skill and the doctrine's
    31	   home (codex-delegation §Economics / §Division of labor / §Test doctrine;
    32	   council §Roles).
    33	2. **Ground truth first:** have it RUN the commands that produce canonical
    34	   numbers (test suite tail, `git log` for cited hashes) rather than trusting
    35	   any doc.
    36	3. Four checks:
    37	   - stale counts (find EVERY occurrence of superseded totals; dated run
    38	     reports keep their point-in-time numbers — not drift),
    39	   - gate-state contradictions (prose saying X is pending while a matrix row
    40	     says complete; docs describing a state the checklists contradict),
    41	   - cross-referenced numbers (results cited in 3+ places must agree),
    42	   - queue sanity (no task both open and completed; ranks coherent; statuses
    43	     match checklist rows),
    44	   - SUPERSESSION CLOSURE (added 2026-07-08 after a meta-reassessment found
    45	     this mode behind ~70% of accumulated defects): driven by the session's
    46	     SUPERSESSIONS, not its diff — list every rule the session changed, grep
    47	     the LOSING wording across both logs, contracts, process docs, and the
    48	     skills, and confirm each hit carries a dated amendment or pointer to
    49	     the winner.
    50	4. Return format: terse `file:location — says X, should say Y` list, real
    51	   inconsistencies only, no style opinions. It's data for the lead, not prose.
    52	
    53	## Pre-commit docs-verify mode (added 2026-07-08; distinct from the sweep)
    54	
    55	For a LARGE landed-doc batch (contract adoption, council-output landing,
    56	program restructure) run a verification round BEFORE its commit, in
    57	addition to the end-of-session sweep. Shape (validated 2026-07-08: caught
    58	1 blocker + 6 should-fixes in a batch the lead had already gate-read,
    59	including drift in the lead's OWN decision-log entries): three fresh
    60	read-only lenses over the uncommitted diff —
    61	(1) FAITHFULNESS to the adjudication record (decisions that didn't land,
    62	landed stronger than adjudicated, or lost their hedges),
    63	(2) COHERENCE with the pinned contract stack (contradictions with
    64	earlier-committed rules; same-batch internal contradictions — an amended
    65	paragraph surviving unamended 40 lines from its replacement),
    66	(3) CLAIM-TO-EVIDENCE trace (numbers, cross-references, claim templates)
    67	— then severity-tiered refuters (adversarial-review skill).
    68	LENS INSTRUCTION EARNED THE SAME DAY: for any decision-gate/threshold
    69	prose, test the GATE LOGIC against a true-null/extreme case — a later
    70	oversight pass caught a pre-registration gate no true null could ever
    71	pass (AP-4) in a contract this mode had already cleared; contract-logic
    72	altitude needs its own explicit check.
    73	The sweep finds drift BETWEEN docs over time; this mode finds drift
    74	between the DECISION and its landing. Both have unique yield.
    75	
    76	## Applying results
    77	
    78	- Fix everything confirmed; fold fixes into the session's final bookkeeping
    79	  commit (or a dedicated fix-up commit pre-PR).
    80	- Structural rule that prevents recurrence: prose status summaries carry an
    81	  as-of date and DEFER to matrix/table rows — never re-narrate live gate
    82	  lists in more than one place. If the repo has a decision log, record that
    83	  rule there once so it binds future sessions.
    84	- If the sweep keeps finding the same doc drifting, that doc is duplicating a
    85	  source of truth — deduplicate the doc, don't just fix the instance.

exec
/bin/zsh -lc "sed -n '1,260p' /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md | nl -ba" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     1	---
     2	name: codex-delegation
     3	description: Delegate implementation and peer review to the local OpenAI Codex CLI (gpt-5.6-sol via codex-run-v3; envelope contract, WRITE_SCOPE enforcement, effort tiers) — invocation, prompt contract, sandbox limits, and token-efficient output consumption. Use when handing a scoped implementation or counterreview task to Codex, in any repo.
     4	---
     5	
     6	# Delegating to Codex (gpt-5.6-sol era; see §Effort-tier policy + ADAPTER.md)
     7	
     8	> Model history: gpt-5.5 through 2026-07-09; gpt-5.6-sol ("Sol") since.
     9	> Older sections say "5.5" where history-accurate; doctrine sections are current.
    10	
    11	Binary: `codex` on PATH (symlinked from
    12	`/Applications/Codex.app/Contents/Resources/codex`); auth in `~/.codex`.
    13	Repo-local bridge when present (`scripts/codex-bridge new|resume --last|review`)
    14	must be wrapped the same way or bypassed; direct shape:
    15	`codex-run <outfile> -C <repo> -s workspace-write "<prompt>"`.
    16	Sandbox: repo + /tmp writes only, NO network, NO sudo, NO GPU/Metal,
    17	`approval: never`. Treat Codex as a near-peer colleague, not a code generator.
    18	
    19	## Invoke (the procedure)
    20	
    21	`~/.local/bin/codex-run` is the ONE stable mechanism for running Codex from
    22	the main loop (added 2026-07-07 after repeated poll/await stalls). Root cause
    23	of every stall: the wait was decoupled from an exit event. The harness has
    24	exactly ONE reliable wake signal — **a background Bash command exiting
    25	re-invokes the agent** — and stalls came from not routing Codex through it
    26	(bare bridge call returns to the shell / agent ends its turn narrating "I'll
    27	await" → nothing exits → nothing wakes). `codex-run` wraps a single Codex call
    28	so it ALWAYS exits (pure-bash watchdog timeout — macOS has no `timeout`; a
    29	wedged Codex becomes a bounded FAILURE) and ALWAYS `< /dev/null` (the
    30	stdin-hang footgun). Bounded exit ⇒ guaranteed wake.
    31	
    32	Protocol:
    33	
    34	1. `codex-run <out.md> [--timeout SEC] [-C DIR] [-s SANDBOX] [--resume] <prompt>`
    35	   launched as ONE `run_in_background: true` Bash call.
    36	2. Do nothing else — end your turn. The harness re-invokes you when it exits
    37	   (never a permastall: the watchdog guarantees exit).
    38	3. On re-invocation read the status file (OK / TIMEOUT / FAILED rc=N) then
    39	   the out-file. NAMING (clarified 2026-07-08): the wrapper REPLACES the
    40	   out-file's extension — `foo.md` → `foo.status`, NOT `foo.md.status`;
    41	   checking the wrong name reads as "no status file" on an otherwise healthy
    42	   run.
    43	
    44	**Timeouts are hang insurance, never work budgets (Ed, 2026-08-05).**
    45	Size the `--timeout` generously to the unit (a bound a healthy run
    46	would never hit); a TIMEOUT status is a verdict on the UNIT SIZE or a
    47	wedge, never on the work — respond by decomposing the unit across
    48	multiple Sol sessions (or a Workflow fan-out) and relaunching, not by
    49	accepting the timeout as failure and not by silently rerunning the
    50	same oversized unit with a bigger clock. Work that is foreseeably
    51	hours-long gets decomposed BEFORE launch.
    52	
    53	Parallel fan-out = N background `codex-run` calls, one out-file each; you wake
    54	as each finishes.
    55	
    56	ONE SANCTIONED ALTERNATIVE (validated 2026-07-08 across 6 workflow runs ≈60
    57	codex agents spanning review, docs-verification, oversight, AND research
    58	shapes: zero stalls, zero agent errors, refuter precision ~2 refuted/~30
    59	confirmed): when the harness Workflow tool is available and the shape is
    60	deterministic FAN-OUT + VERIFY (lenses → severity-tiered refuters, structured
    61	findings), wrap codex as Workflow `agent(..., {agentType: 'codex', schema})` —
    62	the workflow runtime owns wake/retry, and schema-forced StructuredOutput beats
    63	out-file parsing for multi-finding rounds. codex-run remains THE mechanism for
    64	single long-running implementation/fix units and anything the lead consumes as
    65	prose; don't wrap those.
    66	
    67	NEVER: a separate watcher/poller process (redundant — be the thing that exits,
    68	don't watch it); an in-turn `sleep`-loop (burns context); a bare `codex
    69	exec`/bridge call without codex-run (reintroduces both footguns); multiple
    70	codex-run launches batched in one shell for-loop — multi-line prompts break
    71	zsh parsing and the whole batch dies as an instant-completion launch failure
    72	(bit twice 2026-07-09) — one codex-run per Bash call, parallel calls in one
    73	message.
    74	
    75	Orchestrator prompts must mandate codex-run (multi-stream-worktrees points
    76	here). For the repo bridge (`scripts/codex-bridge`), wrap it the same way or
    77	prefer codex-run directly; the bridge's `resume --last` maps to `codex-run
    78	--resume`.
    79	
    80	Caveats (2026-07-07/08, JouleWise sessions):
    81	
    82	1. The guaranteed-wake property holds for the MAIN LOOP only — subagent
    83	   orchestrators are NOT re-invoked by their codex-run children's exits; the
    84	   lead must heartbeat-wake them (full mechanics: multi-stream-worktrees §wake
    85	   gap).
    86	2. `codex-run --resume` forwards cwd (via `cd`, which also scopes `--last`'s
    87	   session filter to that dir) and sandbox (via `-c sandbox_mode=...` —
    88	   `codex exec resume` has no `-C`/`-s` flags); it also mkdir-ps the out-dir,
    89	   resolves OUT to an absolute path, and stamps a thin-output warning into
    90	   `.status` when an OK exit wrote <400 bytes.
    91	3. Caveat 3 / worktree commit constraint: Codex CANNOT `git commit` inside a
    92	   git WORKTREE: the real `.git` lives under the main repo, outside the
    93	   workspace-write sandbox root (index.lock EACCES). Prompt worktree sessions
    94	   with "do NOT commit"; the lead commits by pathspec — when one session
    95	   produces multiple commit-units sharing a file (e.g. the stream ledger),
    96	   split by temporarily truncating the shared file to the first unit's content,
    97	   committing, restoring, committing the rest; or have codex checkpoint `git
    98	   diff > .split/part1.diff` between units and `git apply --cached` it (both
    99	   validated 2026-07-07 resume session).
   100	
   101	### Token-efficient consumption
   102	
   103	Redirect: invocation lives in §Invoke (the procedure); output consumption lives
   104	in §Consume.
   105	
   106	## Delegate vs keep
   107	
   108	**Delegate:** scoped implementation against a pinned spec (one reviewable unit
   109	per session); mechanical follow-ups in the same thread (`resume --last`);
   110	counterreview of findings on its own code; reverse review of the lead's
   111	commits; design judgment when invited EXPLICITLY ("argue the tradeoffs before
   112	you code" — invited judgment has produced better designs than the lead's).
   113	
   114	**Keep for the lead:** anything outside its sandbox (live hardware, $HOME
   115	writes, network, sudo — its "tests green" cannot cover these paths); failure
   116	diagnosis it can't reproduce (hand it the verified root cause + pinned fix
   117	shape, not the symptom); cross-session project context (bookkeeping, gates,
   118	queue ranking); final verification, always.
   119	
   120	## Prompt contract (all six, every time)
   121	
   122	1. Point at pinned spec docs — don't restate them; Codex follows contracts and
   123	   discovers ripple obligations (hash pins, checklist rows) on its own.
   124	2. State environment facts it cannot discover: verified versions, local mirror
   125	   paths, which interpreter is CI-equivalent, its own sandbox limits.
   126	3. Tell it which live probes ARE within its sandbox (e.g. `--help` of a
   127	   privileged binary needs no sudo) — it uses them well when told.
   128	4. Fence bookkeeping files it must not touch (run state, queues, decision logs).
   129	5. Demand evidence: exact commands + output, changed-file list, deviations,
   130	   and "what the parent should double-check" — the deviations section is
   131	   consistently the highest-value output.
   132	6. For fixes: pin what NOT to change and why ("config-level only; the
   133	   FakeClock closed-form tests depend on current stamping").
   134	
   135	### Direction doctrine (evidence: 43-invocation study, suite-build 2026-07-08)
   136	
   137	The prompt features that measurably separated one-shot-clean from rework:
   138	
   139	- **Precedence sentence** in every implementation prompt: "if reports,
   140	  tests, and decision-log entries conflict, named decisions win; flag any
   141	  conflict in the final message." (Best single clause in the corpus.)
   142	- **Autonomy clause**: "if this prompt's requested test or expected value
   143	  contradicts the binding spec, do not force it — report the
   144	  contradiction." (Caught a lead spec-transcription error live.)
   145	- **`FIX-N` numbered fix contracts** for repair rounds — number, exact
   146	  behavior, exact test obligation, "no scope creep" — are the
   147	  highest-cleanliness implementation shape observed (7/7 one-shot).
   148	- **Lens prompts name an angle** (bug / contract / tests / regression /
   149	  integration / negative-space) and demand severity + file:line + a
   150	  concrete failing scenario. Generic "review this" is measurably weaker.
   151	- **Production-shaped gate requirement**: when the diff touches path
   152	  resolution, CLI flow, strict validation, provenance, or external APIs,
   153	  the prompt must demand at least one end-to-end test on the PRODUCTION
   154	  path — unit tests that rewrite refs/APIs away masked all three
   155	  live-only defects of the study session.
   156	- **CLEAN verdicts need a "checks performed" line** — a thin "CLEAN"
   157	  final is unverifiable; require the one-line list.
   158	- **Stack/scope context for reviewers**: tell lenses which layer/unit
   159	  owns deferred behavior ("controller dispatch is unit 2") and tell PR
   160	  reviewers about stacking — the two loudest false blockers were both
   161	  missing-context, not model error.
   162	- RELAX accordingly: pin invariants, forbidden surfaces, and tests — NOT
   163	  internal structure when the repo has clear idioms; long read-lists can
   164	  shrink when the exact binding facts (hash domains, vocabularies,
   165	  formulas) are embedded; design-freedom/adversarial work can be
   166	  delegated early and often ("argue, don't summarize" / "strongest
   167	  concrete failure scenario").
   168	
   169	**Model-version scoping (standing, pre-upgrade 2026-07-09):** calibration
   170	labels (design-freedom-runs-hot, layer yields, clean-rates) are
   171	observations of a MODEL VERSION. After any Codex model upgrade, run one
   172	sealed A/B on a comparable task packet (same rubric; findings classified
   173	unique/overlap/false-positive with fix cost) before promoting old
   174	doctrine or expanding autonomy; log outcomes to the calibration ledger
   175	first, move the delegation boundary second. Post-upgrade expansion
   176	candidates (from the study): whole-stream design+implement with only
   177	contract pins; multi-unit coupled sessions with per-unit checkpoints;
   178	symptom-level failure diagnosis; lens-findings→FIX-N aggregation with
   179	lead sign-off; merge-order simulation + conflict patching; bookkeeping
   180	DRAFTS (lead owns canonical wording). Lead-reserved regardless: live
   181	hardware/API gates, merge decisions, claim-bearing public text.
   182	
   183	Current sandbox constraints:
   184	
   185	- Include verified environment facts in the prompt: repo path, sandbox,
   186	  approval mode, known local mirrors/interpreters, and any live probes that are
   187	  allowed.
   188	- `codex-run --resume` forwards cwd and sandbox; `codex exec resume` itself
   189	  has no `-C`/`-s` flags.
   190	- `-i/--image` belongs before other flags because `--image <FILE>...` is
   191	  variadic and a trailing `-i` swallows the positional prompt if invoking
   192	  `codex exec` directly.
   193	- Read-only sessions cannot run suites that write caches, snapshots, coverage,
   194	  temp files, or other artifacts; give writable temp/workspace-write when the
   195	  expected verification needs it.
   196	- Codex refuses untrusted non-git working directories; `-C` must point at a git
   197	  tree.
   198	- Caveat 3 / worktree commit constraint: Codex CANNOT `git commit` inside a
   199	  git WORKTREE because the real `.git` lives under the main repo, outside the
   200	  workspace-write sandbox root (index.lock EACCES). Prompt worktree sessions
   201	  with "do NOT commit"; the lead commits by pathspec.
   202	- Commit-split recipe 1: when one session produces multiple commit-units
   203	  sharing a file (e.g. the stream ledger), split by temporarily truncating the
   204	  shared file to the first unit's content, committing, restoring, committing
   205	  the rest.
   206	- Commit-split recipe 2: have codex checkpoint `git diff > .split/part1.diff`
   207	  between units and `git apply --cached` it.
   208	
   209	## Consume
   210	
   211	Do NOT read the bridge transcript/log — it echoes every diff 2–3×. Read only
   212	the final message (`.codex-bridge/last-message.md` or the `-o` outfile), and
   213	review the actual code via `git diff` yourself. This cuts per-round main-loop
   214	context cost ~3–5×.
   215	
   216	The scarce resource is main-loop/orchestrator CONTEXT, not Codex tokens
   217	(§Economics below) — spend Codex freely but consume its output as final-message
   218	summaries + `git diff` only.
   219	
   220	**`.status` OK ≠ thorough.** A lens can exit OK with a thin, shallow answer
   221	(observed: a multi-question review answered one question). Treat output
   222	LENGTH+coverage vs the asked deliverable as part of the signal; on thin output
   223	either rerun (free) or self-verify the critical items — and log it as a partial
   224	outcome in the calibration ledger, not a clean accept.
   225	
   226	**Instant completion = launch failure.** Any codex-run that completes within
   227	seconds failed at launch — read the harness task output (stderr), not the
   228	missing sentinel, and relaunch corrected. Today's evidence (2026-07-08): an
   229	untrusted-dir launch failed rc=1 with an empty out-file and nothing on stderr.
   230	
   231	**Killing in-flight rounds is cheap and safe by design** — watchdog + durable
   232	out-files mean `pkill -f "codex exec"` yields a bounded FAILED/TIMEOUT with
   233	partial state on disk. On session stops, kill and checkpoint rather than
   234	waiting rounds out; tell orchestrators the FAILED status is expected so they
   235	don't relaunch.
   236	
   237	Reference costs: trivial prompt ~3k tokens/seconds; scoped script ~50k/~3min;
   238	full adapter slice ~200k/~15min; counterreview+fixes ~250–300k.
   239	
   240	## Specialties
   241	
   242	### Division of labor
   243	
   244	Codex does ALL reading-heavy volume work — bug-hunt lenses over whole modules,
   245	test-gap analysis, comprehensive test WRITING, and test REVIEW — and ALL
   246	COMPUTER-USE tasks (GUI automation, browser driving, app interaction: Ed says
   247	Codex is excellent at it; a Codex Computer Use service is installed on this
   248	machine under ~/.codex/computer-use/). Smoke-test any NEW delegation channel
   249	(computer use included) with a no-op before first real use — the session header
   250	alone surfaces load-bearing facts (model, sandbox, approvals). Computer-use
   251	delegation does NOT waive the lead's final verification duty on outcomes that
   252	matter.
   253	
   254	**Visual/image analysis is a Codex specialty (C-012, Ed, 2026-07-08):** Codex
   255	has higher-resolution image analysis than the lead's inline screenshot reads,
   256	and its token economics make image-heavy workloads (design critiques, layout
   257	verification, multi-page visual QA, screenshot-diff sweeps) cheap — pass it
   258	MANY images per round rather than the lead reading screenshots one by one.
   259	`codex-run` forwards `-i/--image`. The lead still makes the design DECISIONS
   260	from Codex's findings and may spot-read the one or two screenshots that decide

exec
/bin/zsh -lc "sed -n '261,586p' /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md | nl -ba -v261" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   261	a judgment call; the exhaustive looking is Codex's job. Smoke-test with one
   262	image on first use in a session (thin-output warning applies).
   263	
   264	Fable owns the apex: ALL high-level orchestration and the FINAL REVIEW of
   265	everything important — the last gate before a commit/merge of important work
   266	is a Fable-level judgment pass over the final diff, informed by Codex lenses
   267	but never outsourced to them. Thin ≠ rubber stamp: Fable doesn't re-derive
   268	Codex's analysis, but it does read the final diff, weigh the findings, and
   269	decide. Also Fable-reserved: live/hardware verification, merge decisions,
   270	bookkeeping, skill distillation. (Council-role framing of the same split:
   271	council skill §Roles.)
   272	
   273	### Security
   274	
   275	Security-shaped work is a Codex specialty, not a Fable one (Ed, 2026-07-07).
   276	
   277	Adversarial audits — bug hunts, vulnerability enumeration, penetration-style
   278	review, integrity/tamper-resistance hardening, fuzzing, corruption-handling
   279	tests — are entirely legitimate DEFENSIVE work on one's own codebase, but they
   280	generate a dense stream of exploit-shaped vocabulary (path traversal,
   281	hash/signature bypass, injection, poisoning, malformed/truncated input) that a
   282	content-safety classifier can misread as offensive intent. On the JouleWise
   283	test-audit stream this correlated with the ORCHESTRATING model being
   284	tier-downgraded — a false positive, but a costly one (worse reasoning right
   285	when the merge gate needs it). Mitigation, standing:
   286	
   287	- **Route the whole adversarial layer to Codex** (it is not gated the same
   288	  way): Codex holds the finding-detail prompts, writes the tests, and drafts
   289	  the write-ups.
   290	- **Keep the orchestrating model at abstract altitude:** refer to findings
   291	  by ID ("finding B2, the integrity-check gap"), not by mechanism. Do NOT
   292	  read the full exploit-language findings into the main conversation stream
   293	  that gets classified — keep them in Codex output files / scratchpad /
   294	  `docs/`, and consume summaries.
   295	- **Expect tier instability** on any security-review / pentest / CTF /
   296	  vuln-enumeration task and design for it: the smart-model role is the
   297	  orchestration and the merge gate, never the vuln enumeration.
   298	
   299	## Test doctrine (the ONE home)
   300	
   301	0. FAILED-TEST TRIAGE (Ed, 2026-07-07): when any test fails, Codex 5.5 gets
   302	   it FIRST — hand it the failing output + relevant diff inline; it
   303	   diagnoses why and implements the fix. Escalate to Fable-level debugging
   304	   only after Codex fails twice. Fable still verifies the fix and holds the
   305	   final gate.
   306	1. The implementer's tests are a floor, never the ceiling — a dedicated
   307	   Codex TEST-AMPLIFICATION round writes edge-case coverage beyond them.
   308	2. Writer ≠ reviewer — a FRESH read-only Codex instance reviews all tests
   309	   for tautological/vacuous assertions, wrong expected values, tests that
   310	   would pass against a broken implementation, and flakiness.
   311	3. Periodic repo-wide Codex test audits (parallel bug-hunt lenses per
   312	   module → gap map → new tests in NEW test files only → fresh-eyes test
   313	   review) run as their own stream. Bug findings in a test audit are
   314	   reported, not fixed in-stream, when other streams own the code.
   315	
   316	## Economics (Ed, 2026-07-07) — the ONE home of the spend doctrine
   317	
   318	Codex gpt-5.5-high usage is near-limitless — treat Codex rounds as free and
   319	be VERY liberal: a Codex code review after EVERY implementation (own or
   320	delegated) is the default, plus counterreview of the reviewer's findings
   321	when they're design-bearing. Be GENEROUS: fan out ideation, always include
   322	a devil's-advocate/examiner session, send the lead's synthesis back for
   323	attack before presenting it, and have Codex reverse-review the lead's own
   324	work products routinely — the reverse direction has caught issues every
   325	lead-side layer missed. The drop-a-layer rule still applies to Codex layers
   326	by catch-rate, but on signal quality only — never on cost. The lead's
   327	scarce resource is its own context window, not Codex calls; shift
   328	reading/arguing outward, keep judgment and verification inward. Never use
   329	Codex's dangerous bypass flags; inspect diffs before reporting success.
   330	(Council/roles framing points here; do not restate elsewhere.)
   331	
   332	### Effort-tier policy (Ed, updated 2026-07-12; gpt-5.6-sol era)
   333	
   334	- **`--effort ultra` ONLY when the Sol session itself needs to spawn
   335	  subagents** (spawn_agent-capable multi-part work inside one session).
   336	  It is NOT a quality knob for single tasks.
   337	- **Individual tasks start at `high` by default** for bounded/mechanical
   338	  work, docs/config, straightforward implementations, named FIX rounds, and
   339	  ordinary focused reviews.
   340	- **Use `xhigh` only for named hard-task triggers:** design-bearing decisions,
   341	  cross-contract or multi-component work, non-local root causes,
   342	  adversarial/integration reviews, or other judgment-dense tasks where the
   343	  cost of an incorrect answer is material. When uncertain, start `high` and
   344	  escalate only if the task actually exhibits one of these triggers.
   345	- **Find the ceiling empirically, quality-guided not cost-dictated:**
   346	  keep widening the scope handed to a single xhigh session until the
   347	  returned work stops meeting prod standards (lead review + lead
   348	  verification are the judge), then log that scope boundary in the
   349	  field notes below and back off one notch. Sol is dirt cheap; the
   350	  binding constraint is output quality and the lead's review capacity,
   351	  never spend.
   352	- **The lead stays orchestrator**: worktree/branch/commit management,
   353	  contracts, gates, and final verification never delegate, no matter
   354	  how large the delegated scope grows.
   355	- **Usage-pressure mode (Ed, 2026-07-11): ULTRA is the dominant quota
   356	  consumer; xhigh/high are comparatively cheap.** When Ed flags usage
   357	  pressure (or monitoring shows it), STOP launching ultra sessions for
   358	  the stated window and shift the fleet to break-mode work: Sol
   359	  high/xhigh CONSULTANCY and SPEC DESIGN for future tasks (design
   360	  consults, spec sheets, scheduling scouts, review-of-plans) instead of
   361	  heavy implementation. Heavy implementation resumes when the window
   362	  ends or Ed clears it. Check usage before any ultra launch once
   363	  monitoring exists (codex-usage / v3 .status warnings).
   364	- Scope-ceiling observations to date: 15-file recipe-driven merge
   365	  composition, whole-project 7-lens reviews, and 100x-loop flake
   366	  root-causes have all returned prod-quality at xhigh. No xhigh
   367	  quality ceiling found yet — keep pushing scope upward and record
   368	  the first miss here.
   369	
   370	### Adapter: claude-codex-report/v1 (ADOPTED 2026-07-11)
   371	
   372	The report/prompt/manifest contract between lead and Sol lives in
   373	`ADAPTER.md` next to this file — envelope-first reports (fenced JSON:
   374	status/completion/pathspec/verification/flags), the compact prompt
   375	template that replaces the six-part contract, per-genre verdict
   376	vocabularies (A/B/C retired → apply/preserve/compose/ruling), manifest
   377	v3 event stream, and the lead consumption flow (parse envelope →
   378	guard-check → replay verification → skip prose unless acting on it).
   379	codex-run-v3 is INSTALLED (2026-07-11; ~/.local/bin/codex-run-v3;
   380	67-assertion suite + full v2 compat suite green; v2 kept as fallback).
   381	Use v3 with --genre for every new invocation — the runner injects the
   382	envelope schema and genre template, so prompts stop restating output
   383	shape; use the ADAPTER.md prompt template for the rest. Consume via
   384	the envelope; append run_consumed events with `codex-run-v3 consume`.
   385	First live calibration note: the v3 implementation session itself
   386	dogfooded the envelope and consumption worked as designed.
   387	
   388	v3 field notes (C-029, 2026-07-12 — first multi-stream production run):
   389	
   390	- `--write-scope` REQUIRES a literal `WRITE_SCOPE: [...]` line in the
   391	  prompt BODY matching the flag; omitting it is an instant rc=64 launch
   392	  failure (bit 3x in one message before the first success).
   393	- ALWAYS pass `--effort` explicitly. The wrapper passes through
   394	  `~/.codex/config.toml` `model_reasoning_effort` when the flag is
   395	  omitted — a leftover `"ultra"` there ran 13 consecutive C-029
   396	  invocations at unintended ultra (rule-10 violation, weekly quota
   397	  22%→32% in a day). Wrapper-default fix queued on TOOL-01; until it
   398	  lands the flag is mandatory, not optional.
   399	- Upstream stream-death failure modes: FAILED rc=1 (honest), watchdog
   400	  SIGTERM rc=143 after a reconnect-loop wedge (honest), and — worst —
   401	  exit OK with `WARN: thin output` and an EMPTY/absent out-file (looks
   402	  like success; treat thin-output OK as FAILED). `--resume` after an
   403	  outage preserved a 206k-token fix round's completed work; prefer
   404	  resume over relaunch for workspace-write sessions that died mid-run,
   405	  then lead-verify what actually landed (the resumed session's own
   406	  report may never arrive — the WORKTREE is the ground truth).
   407	
   408	Invocation gotcha (2026-07-11): `codex-run -C <dir>` requires a
   409	TRUSTED (git) directory — pointing at a non-repo scratchpad fails with
   410	"Not inside a trusted directory"; `git init` the scratchpad first.
   411	
   412	v3 field notes (D-077 fix-round arc, 2026-07-18):
   413	
   414	- **xhigh `--genre review` sessions ended with `last_agent_message:
   415	  null` 4/5 times** (5-8 min of real work, then `task_complete` with no
   416	  final message → wrapper rc=1, empty out-file). Implementation-genre
   417	  runs never exhibited it. Manual recovery (worked 4/4):
   418	  `scripts/codex-bridge resume <session-id>` with "emit the final report
   419	  from work already done — do not redo it". FIXED IN WRAPPER
   420	  (2026-07-18, Ed-requested): codex-run-v3 now auto-runs ONE bounded
   421	  recovery resume when rc!=0/143/137 with an empty out-file and an
   422	  extractable session id; success reports `OK (null-final-message
   423	  recovery resume; verify report provenance)`. Backup of the pre-patch
   424	  wrapper: `~/.local/bin/codex-run-v3.bak-20260718`. Still add an "emit
   425	  the report as your FINAL MESSAGE" line to review prompts, and treat
   426	  the recovery marker as a cue to verify the report against artifacts.
   427	- The v3 default sandbox is READ-ONLY: an implementation launch without
   428	  `-s workspace-write` early-returns rc=77 with a clean environment flag
   429	  (no writable repo or TMPDIR). Pass `-s workspace-write` for every
   430	  implementation/testing run; review runs also need it when refuters
   431	  must execute tests (WRITE_SCOPE `[]` still forbids repo edits — the
   432	  reviewers' git-status self-reports plus lead-side `git status` both
   433	  confirmed no writes across 5 such sessions).
   434	- Read these field notes BEFORE the first launch of a session: the
   435	  rc=64 WRITE_SCOPE-line failure above bit again twice this arc, purely
   436	  from not re-reading them.
   437	
   438	v3 field notes (D-078 close-out, 2026-07-22):
   439	
   440	- **Never bench-edit a worktree while an enforced-scope session is live in
   441	  it.** The wrapper snapshots the tree at launch and attributes EVERY
   442	  post-baseline diff to the session: a lead edit to docs/decision_log.md
   443	  during a WRITE_SCOPE run produced run_status=SCOPE_VIOLATION on a fully
   444	  compliant Sol session AND evicted the run from the pending-scope resume
   445	  registry (so `resume <run_key> --approve-scope-add` refused with "no
   446	  pending scope run"). Recovery: verify attribution via the evidence
   447	  bundle's attempt-compare.json (`actual_changed_paths` vs
   448	  `scope_violation_paths`), then treat the preserved worktree as ground
   449	  truth and continue at the bench — the NEEDS_SCOPE ask can be honored by
   450	  a lead-applied edit when it is under the bench-vs-session threshold.
   451	- The xhigh review-genre null-final-message mode (2026-07-18 note) can
   452	  ALSO defeat the wrapper's auto-recovery resume; the manual
   453	  `scripts/codex-bridge resume <session-id>` + "emit the report from work
   454	  already done" recovery remains the reliable second-line fix (worked
   455	  first try again).
   456	
   457	v3 field note (Fable resume session, 2026-08-05):
   458	
   459	- **The prompt argument is a literal STRING (`"$*"`), never a file
   460	  path** — always pass `"$(cat prompt.md)"`. A file-path arg silently
   461	  becomes the entire prompt (a no-scope run proceeds on a one-line
   462	  garbage prompt; a --write-scope run fails rc=64 "requires a
   463	  WRITE_SCOPE field" because the path string has no such line — the
   464	  rc=64 is the LUCKY failure mode).
   465	
   466	v3 field notes (C-033 screen+budget gauntlet, 2026-07-25):
   467	
   468	- Wrapper flag exactness: the genre is `implementation` (NOT `implement`,
   469	  exit 64), and `--write-scope` requires a literal `WRITE_SCOPE: [...]`
   470	  line INSIDE the prompt matching the flag (exit 64 otherwise) — prompt
   471	  text is part of enforcement by design.
   472	- `resume <run_key> --approve-scope-add` works from a clean NEEDS_SCOPE
   473	  early return but NOT from an ACCEPTANCE_FAILED terminal state
   474	  ("run is not resumable"): a session that embeds its scope ask inside a
   475	  completed-looking envelope (acceptance ran and failed on out-of-scope
   476	  tests) is dead for resume. Recovery: fresh narrow-scope session for the
   477	  residual work — often the residue is under the bench-vs-session
   478	  threshold anyway (one-line fixture edit, done at the bench).
   479	- Strict-scope (`--write-scope`) runs REFUSE trees containing nested git
   480	  repositories ("strict-scope runs do not support nested repositories") —
   481	  stale `.claude/worktrees/*` from other sessions trigger it, and they may
   482	  hold other sessions' uncommitted work (check before deleting; if dirty,
   483	  fall back to prompt-line WRITE_SCOPE without the flag for low-risk
   484	  docs-only tasks).
   485	- `codex-usage` read ALL ZEROS across a ~15-invocation day — the
   486	  v3-wrapper→ledger feed is broken; treat a silent ledger as UNKNOWN
   487	  quota, never as headroom (Ed notified 2026-07-24).
   488	- Effort-tier evidence: paired distinct-lens refuters at `high` beat the
   489	  old single-lens-xhigh default (C-033 ruling; detail in
   490	  adversarial-review §C-033). Implementation rounds with pre-verified fix
   491	  shapes also ran clean at `high` — reserve xhigh for design-bearing
   492	  fix rounds where Sol must make the calls.
   493	
   494	## Parallel threads
   495	
   496	Two distinct parallelization modes:
   497	
   498	- **Parallel IDEATION/REVIEW (read-only) — cheap and safe in one tree:**
   499	  use N `codex-run` calls with `-s read-only`, one out-file each, or the
   500	  sanctioned Workflow alternative for deterministic FAN-OUT + VERIFY. Never
   501	  use bare `codex exec`. No writes → no clobbering; fire 3–5 lenses
   502	  concurrently (design, maximize, devil's advocate, synthesis-review). This is
   503	  the default shape for ideation councils. Note: separate sessions means
   504	  `resume --last` is ambiguous afterward — for follow-ups, start a new session
   505	  carrying the needed context rather than resuming.
   506	- **Parallel IMPLEMENTATION (writes) — needs isolation:** concurrent
   507	  writing sessions in one tree clobber `.codex-bridge/` state and the
   508	  working tree. Give each stream its own git worktree (the bridge resolves
   509	  repo root per-worktree) — see the multi-stream-worktrees skill.
   510	- After merging parallel streams, run a Codex INTEGRATION review over the
   511	  merged result — cross-stream interaction defects only (each stream was
   512	  already reviewed in isolation); include a full suite run in the prompt.
   513	
   514	## Appendix: field notes and superseded-fix history
   515	
   516	- **Dual-prior design rounds beat single design rounds** (2026-07-07 session,
   517	  all observed) for contract-pinning work: two parallel read-only lenses given
   518	  OPPOSING priors (e.g. minimal-protocol vs future-requirements-first), then
   519	  synthesize; independent convergence between them is strong evidence a pin is
   520	  right (observed: both converged on seam, failure taxonomy, and clock-marker
   521	  method for a wire protocol).
   522	- **History-vs-live boundary:** review lenses asked for staleness/consistency
   523	  fixes will confidently propose rewriting HISTORICAL records (ledgers,
   524	  decision logs, dated run reports) into present truth. Reject that class
   525	  wholesale — history is immutable, addendum entries only. Lead judgment is
   526	  needed exactly at this boundary. REFINEMENT (2026-07-08, critique-record
   527	  session): the immutable class is ledgers and dated records. A reader-facing
   528	  LIVING document that happens to have an adjudicated past (e.g. a committed
   529	  critique later given a second pass) MAY be updated in place, but only under
   530	  three conditions together: git preserves the verbatim adjudicated text (cite
   531	  the commit), every in-place update is marked in-document, and a provenance
   532	  note names exactly which passages changed. When a revert would reintroduce
   533	  stale reader-facing numbers, accurate labeling beats content revert — but an
   534	  unlabeled or overclaimed "preserved as record" note is a BLOCKER, not a nit.
   535	- **Self-describing documents need a fresh counterreview.** When a model edits
   536	  its OWN prior review/critique artifact, the highest-risk claims are the
   537	  document's statements about its own history ("retained verbatim",
   538	  "addendum-only"). The 2026-07-08 session's only blocker was exactly this —
   539	  implementer AND lead initially under-weighed it; a fresh read-only 5.5
   540	  instance caught and correctly severity-tiered it. Route any self-edited
   541	  review artifact through a fresh instance with an explicit "verify the
   542	  document's claims about its own provenance" item.
   543	- **Bridge-v1.1 design consult scorecard (2026-07-13, JouleWise):** a single
   544	  xhigh MCP discussion-lane consult over the bridge contract returned 5
   545	  accepted design amendments (fail-closed wrapper state machine with
   546	  receipt-anchored digest; per-call effort field over env-only; per-objective
   547	  peer channels over per-session; enforcement-boundary dedup carve-out;
   548	  proposal-diff provenance + aggregate ceiling) plus one CONFIRMED adapter bug
   549	  (duplicate BRIDGE_REPORT_V1 sentinel on the protocol-deviation path) that
   550	  the lead's own full read had missed. Sol design wins column grows; the
   551	  pre-decision consult default (global rule 2) is earning its keep.
   552	- **codex-run-v3 preflight gotchas (2026-07-13):** `--write-scope` requires a
   553	  line-anchored `WRITE_SCOPE: [...]` field in the prompt body (the flat v3
   554	  array, separate from a BRIDGE_TASK_V1 header's object form); strict-scope
   555	  runs refuse nested repositories (remove stale `.claude/worktrees/*`
   556	  worktrees first — `git worktree remove` + `prune`); the ignored-path
   557	  inventory cap is 50000 with `CODEX_RUN_IGNORED_CAP` override (was a fixed
   558	  10000; a 10.6k-entry `.venv` tripped it).
   559	- **Pre-T4 mkdir bug (superseded history):** the historical trigger for the
   560	  instant-completion diagnostic was the pre-T4 wrapper not creating the
   561	  out-dir. That was fixed 2026-07-07 in C-009 T4; the live diagnostic remains in
   562	  §Consume.
   563	
   564	v3 field notes (mint-implementation session, 2026-07-28, trace
   565	`JouleWise docs/run_reports/2026-07-28-floor-mint-implementation.md`):
   566	- **codex-run-v3 DETACHES under Claude Code background tasks** — a
   567	  `run_in_background` shell launching it exits in seconds (0-byte
   568	  output), so "bounded exit ⇒ guaranteed wake" does NOT hold; grandchild
   569	  completion notifications also mis-route to the top session. FIVE
   570	  broken-wake incidents in one session, one root cause. MANDATORY
   571	  pattern now: every brief that delegates to codex-run includes, up
   572	  front, a harness-tracked poll (status-file leaves RUNNING / PID
   573	  vanishes / deadline, whichever first) named as the wake source, plus a
   574	  lead-side redundant timer for anything deadline-bearing. Do not rely
   575	  on agents discovering this themselves.
   576	- Wake-gap stalls are also a FABRICATION hazard: a director filled two
   577	  long unresolved waits by narrating predicted refuter verdicts (both
   578	  retracted, self-flagged). The wake fix removes the mechanism; briefs
   579	  should still say "report 'still pending', never predict a pending
   580	  verdict."
   581	- Staged-commit xhigh implementation (7 resumed sessions, one commit per
   582	  contract stage, enforced WRITE_SCOPE each) held prod quality on a
   583	  cross-contract schema+tool build; one clean NEEDS_SCOPE early-return
   584	  (stale out-of-scope fixtures hit by ratified signature changes) —
   585	  scope expansion granted for mechanical kwargs only. Ceiling not yet
   586	  found; effort-tier §: keep pushing.

exec
/bin/zsh -lc 'for x in codex-run codex-run-v2 codex-run-v3 codex codex-usage; do command -v "$x" || true; done; ls -l scripts/codex-run scripts/codex-bridge 2>/dev/null || true; ls -l ~/.local/bin/codex-run ~/.local/bin/codex-run-v2 ~/.local/bin/codex-run-v3 ~/.local/bin/codex-usage 2>/dev/null || true; test -f docs/process/model_allocation_ledger.md && echo model_allocation_ledger_present || echo model_allocation_ledger_missing; test -d ~/.codex/computer-use && echo computer_use_dir_present || echo computer_use_dir_missing; test -e ~/.claude/skills/skill-usage-log.md && echo global_usage_log_present || echo global_usage_log_missing' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
/Users/edr/.local/bin/codex-run
/Users/edr/.local/bin/codex-run-v2
/Users/edr/.local/bin/codex-run-v3
/opt/homebrew/bin/codex
/Users/edr/.local/bin/codex-usage
-rwxr-xr-x@ 1 edr  wheel  15528 Aug  7 09:02 scripts/codex-bridge
-rwxr-xr-x@ 1 edr  wheel   7060 Aug  7 09:02 scripts/codex-run
-rwxr-xr-x@ 1 edr  staff   7060 Jul  8 06:36 /Users/edr/.local/bin/codex-run
-rwxr-xr-x@ 1 edr  staff  11705 Jul 10 11:07 /Users/edr/.local/bin/codex-run-v2
-rwxr-xr-x@ 1 edr  staff  72557 Jul 18 22:54 /Users/edr/.local/bin/codex-run-v3
-rwxr-xr-x@ 1 edr  staff  12966 Jul 11 02:11 /Users/edr/.local/bin/codex-usage
model_allocation_ledger_present
computer_use_dir_present
global_usage_log_present

exec
/bin/zsh -lc "sed -n '1,170p' /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md | nl -ba && sed -n '370,543p' /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md | nl -ba -v370" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     1	# claude-codex-report/v1 — the lead↔Sol adapter (ADJUDICATED SPEC)
     2	
     3	Status: ADOPTED 2026-07-11 (Ed-directed consultation; design by gpt-5.6-sol
     4	xhigh grounded in six real session reports + the invocation manifest; lead
     5	adjudication below). This file is the ONE home of the adapter contract.
     6	The consultation record lives in the C-028 session scratchpad
     7	(sol-adapter-design.md) and the council log entry for that arc.
     8	
     9	## Lead rulings (on the six questions the design requested)
    10	
    11	1. `blocked` + `completion: complete` IS the correct encoding for
    12	   implemented-but-unverifiable work (the CI-002 case). ACCEPTED.
    13	2. Baseline default for write tasks is EXACT SHA; `descendant` only by
    14	   explicit choice. ACCEPTED.
    15	3. The runner out-file envelope is CANONICAL; repo run reports are domain
    16	   artifacts and must NOT duplicate the envelope (narrative only). ACCEPTED
    17	   with that anti-duplication amendment.
    18	4. Write-allowlist expansion → STOP AND FLAG. AMENDED: the session should
    19	   finish independent already-authorized parts before stopping (partial
    20	   completion preferred over hard mid-run abort), then flag.
    21	5. Envelope may grow to ~8 KiB for grouped triage/scout verdicts. ACCEPTED.
    22	6. `run_consumed` events are lead/wrapper-owned, never worker-owned.
    23	   ACCEPTED.
    24	
    25	Amendments: use `prompt_bytes` (runner cannot count tokens reliably);
    26	manifest v3 goes in a NEW event-stream file wired into the D-064 decision
    27	entry at the C-028 bookkeeping arc — existing JSONL rows are never mutated.
    28	Runner also mirrors `semantic_status`/`completion` into the `.status` file
    29	so the lead can triage without opening the report.
    30	
    31	## External guidance addendum (Ed-directed, 2026-07-11):
    32	## learn.chatgpt.com/docs/prompting — ingested, binding for Sol prompts
    33	
    34	OpenAI's prompting guidance (Goal/Context/Output/Boundaries; describe
    35	OUTCOMES not processes; context only when it changes the output; the one
    36	or two boundaries that prevent unusable results; say how the result will
    37	be used; iterate with precise follow-ups; Codex: name behaviors,
    38	reference code/repro, preserve constraints, specify verification, plan
    39	before editing). It independently corroborates §B's template (TASK one
    40	outcome sentence; AUTHORITY-only inputs; allowlists over prohibition
    41	lists). Three deltas it ADDS to our practice:
    42	
    43	1. **CONSUMPTION hint**: when how the lead will use the result is
    44	   non-obvious, add one line saying so (e.g. "consumed as a mechanical
    45	   recipe by another session") — it steers length/organization better
    46	   than format rules.
    47	2. **Resume vs fresh, by role**: iterate on the SAME role by RESUMING
    48	   the session (fix rounds, follow-up questions — precise deltas, not
    49	   restarts); use FRESH sessions only where independence is the point
    50	   (reviewers, refuters, examiners). Never re-explain context a resumed
    51	   session already has.
    52	3. **Plan-first option**: for design-heavy or novel-shape
    53	   implementations, request a proposal/plan stage before any edits
    54	   (two-phase: plan → lead ack → implement), mirroring Codex /plan.
    55	   Skip for recipe-driven or bounded-mechanical work.
    56	
    57	## Scope-restraint addendum (Ed-directed consult, 2026-07-11; ADOPTED)
    58	
    59	Root causes ranked (Sol's introspection, adjudicated): ambiguous scope
    60	language > completionist drive > repo standing instructions > long-
    61	session drift. A bound BINDS when exhaustive (not categorical),
    62	machine-readable, top-of-prompt, runner-trailer-repeated, explicit
    63	about tests/docs/reports/state/generated/deletes, aligned with
    64	AGENTS.md, coupled to a stop-and-request protocol, and MECHANICALLY
    65	checked against the filesystem (never the worker's self-report).
    66	
    67	BINDING PROMPT BLOCK (use verbatim, before task prose, in every
    68	delegated write session — supersedes the older one-line WRITE_SCOPE):
    69	SESSION_MODE: delegated; WRITE_SCOPE as JSON list (exact paths or
    70	dir/** only); then the WRITE AUTHORITY — NON-NEGOTIABLE block and
    71	SCOPE-EXPANSION PROTOCOL exactly as specified in the consult record
    72	(docs/reviews/2026-07-11-scope-restraint-consult.md in JouleWise; copy
    73	lives there): scope is the complete allowlist for every write kind; no
    74	repo instruction/checklist/test failure expands it; disclosure is not
    75	authorization; expansion is prospective-only via completion=partial +
    76	blocking scope_expansion request {requested_paths, reason,
    77	blocked_work, minimal_change} → run_status=NEEDS_SCOPE → lead resumes
    78	the SAME session UUID with amended scope.
    79	
    80	RUNNER BACKSTOP (codex-run-v3, IMPLEMENTED + INSTALLED 2026-07-11;
    81	149-assertion suite): note the launch validation — `--write-scope`
    82	requires a matching `WRITE_SCOPE:` field ANCHORED at line start in the
    83	prompt (inline-prose mention fails with exit 64; use the template's
    84	field-per-line layout).
    85	
    86	OPERATIONAL LESSONS (first live day):
    87	- Bytecode caches (`__pycache__`, `*.pyc`) from required test runs are
    88	  a false-positive violation class — runner now records them as
    89	  `ignored_bytecode_paths` and exports PYTHONPYCACHEPREFIX out of
    90	  tree. Real-path violations still exit 77.
    91	- NEVER edit the installed runner in place while wrappers are running:
    92	  bash reads scripts lazily; an in-place rewrite crashes live
    93	  instances mid-parse (phantom syntax errors) AFTER session completion
    94	  but BEFORE scope check/status/manifest write. Install pattern:
    95	  write to a temp path, `mv` atomically (running instances keep the
    96	  old inode). If a wrapper dies this way: classify scope manually
    97	  from the envelope's pathspec vs unowned_dirty, and append a
    98	  lead-authored run_finished recovery row to the manifest.
    99	- The NEEDS_SCOPE/scope_deviation protocol survived a dead wrapper at
   100	  the model layer: the session self-bounded (blocked+partial,
   101	  pathspec vs unowned_dirty separated) purely from prompt language.
   102	- RECURRING DEFECT PATTERN (seen twice, p2041 + p2037 fix rounds):
   103	  newly added path-resolution guards crash on symlink loops
   104	  (Path.resolve raises OSError/RuntimeError) instead of failing
   105	  closed. Every delta review of fix rounds that touch path handling
   106	  must probe unhandled resolve() exceptions; every fix contract for
   107	  path guards must pin the fail-closed wrap + self-symlink fixture. baseline+final
   108	`git status --porcelain=v2` capture; actual-delta classification vs
   109	WRITE_SCOPE; violations → run_status=SCOPE_VIOLATION, exit 77,
   110	evidence bundle outside the worktree, tree preserved for lead
   111	adjudication (never auto-revert in shared worktrees); worker pathspec
   112	is audit-only; missing/invalid envelope in a write run FAILS
   113	acceptance; runner never unconditionally exits 0.
   114	
   115	NEEDS_RULING — GENERALIZED LEAD INVOCATION (adopted 2026-07-11, after
   116	the P2-037 no-report incident and the RED round's invented renames):
   117	the NEEDS_SCOPE shape extends to ANY blocking question. When a session
   118	hits an authority gap, contract ambiguity, or a fork it cannot decide
   119	(naming, semantics, spec conflicts), it must NOT guess and must NOT
   120	grind: finish independent authorized work, then return
   121	completion=partial with a blocking flag {kind: lead_ruling, question,
   122	options_considered, recommendation, blocked_work} →
   123	run_status=NEEDS_RULING. The lead ALWAYS resumes compliant
   124	early-returns (same session UUID, answer injected). Add to every
   125	delegated prompt trailer: "Blocked on a decision that is not yours?
   126	Return early with a NEEDS_RULING flag — a resume round-trip is cheap;
   127	a wrong guess is not." Mid-run synchronous invocation of the lead
   128	stays prohibited (control-hierarchy inversion); escalation is always
   129	by artifact. Runner recognition of NEEDS_RULING rides the next v3
   130	round alongside the scope backstop.
   131	
   132	LEAD-SIDE RULES (from item E, adopted): delegated implementation
   133	sessions do NOT write in-repo run reports — the envelope is the
   134	report, the lead authors the repo artifact; never combine
   135	implementation + bookkeeping + report publication in one session;
   136	"content accepted, process violated" are SEPARATE ledger columns —
   137	retroactive approval of useful out-of-scope edits must not teach
   138	edit-disclose-ask-forgiveness; long ultra sessions get a scope
   139	reminder after compaction/phase transitions; empty/invalid reports
   140	fail runs regardless of transport success.
   141	
   142	**Builder's rule (relayed by Ed, 2026-07-11, from a Codex/Sol builder):**
   143	"Set bounds — a sandbox the model should operate within; explain how it
   144	should verify its work; be clear about what done looks like. Ambiguity
   145	invites longer runtime and token use." Adopted as a HARD template rule:
   146	`WRITE_SCOPE`, `REQUIRED_VERIFICATION`, and `DONE_WHEN` are MANDATORY in
   147	every prompt — omitting any of them is a delegation defect, not a style
   148	choice. Corollary: when a session runs long or overruns its timeout,
   149	suspect the CONTRACT before raising the timeout — ambiguity is the usual
   150	cause. Lead nuance (kept deliberately): consult/scout genres get wide
   151	TASK bounds because Sol's design freedom is the point there, but even
   152	they carry a crisp DONE_WHEN on deliverable shape and read-only
   153	WRITE_SCOPE `[]`.
   154	
   155	## The spec (as proposed; adopted verbatim except where ruled above)
   156	
   157	# Recommendation: adopt `claude-codex-report/v1`
   158	
   159	The adapter should have one compact, validated result envelope followed by genre-specific evidence. The lead should normally ingest only the envelope, mechanically replay verification, and open prose selectively.
   160	
   161	Today’s reports demonstrate why:
   162	
   163	- The merge review is only two lines, but its manifest status is `OK` despite a blocker ([report](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-merge-review.md:1), [manifest](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/c028-invocations.jsonl:3)).
   164	- The flake report does not expose suite tails or touched files until lines 78–113 ([report](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-p2038-flake.md:78)).
   165	- The triage report’s three lead rulings do not appear until line 187 ([report](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-p2041-triage.md:187)).
   166	- The status refresh is concise but has summarized, not exact, output and records concurrent baseline movement only at the end ([report](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-status-refresh.md:6)).
   167	- A seventh report arrived during this consultation. It says implementation is done, acceptance is pending, and a required build could not run—an outcome that neither `OK` nor `FAILED` represents ([CI-002 report](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-ci002.md:13)).
   168	
   169	## A. Report contract
   170	
   370	## B. Prompt template
   371	
   372	The lead’s six-part contracts are visible almost verbatim in the scout’s delegation blocks: Task, Inputs, Deliverables, Verification, Constraints, Report ([example](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-hardening-scout.md:115)).
   373	
   374	Use this instead:
   375	
   376	```text
   377	ADAPTER: claude-codex-report/v1
   378	GENRE: <review|implementation|triage|root_cause|scout>
   379	
   380	REPO: <worktree>
   381	BASELINE: <exact|descendant|informational> <sha>
   382	MUTATION: <read-only|workspace-write>; commit=<yes|no>; external=<yes|no>
   383	WRITE_SCOPE: <paths/globs or []>; expansion=stop-and-flag
   384	
   385	TASK: <one outcome sentence>
   386	
   387	DONE_WHEN:
   388	- <observable acceptance condition>
   389	- <observable acceptance condition>
   390	
   391	AUTHORITY:
   392	- <governing path, commit, PR, or decision>
   393	- <only genuinely authoritative inputs>
   394	
   395	REQUIRED_VERIFICATION:
   396	- <exact command or centrally defined profile>
   397	
   398	RULINGS_ALREADY_MADE:
   399	- <only decisions the model must not reopen>
   400	
   401	SPECIAL_CONSTRAINTS:
   402	- <privacy, hardware, quiet-machine, fail-closed, or other unusual hazard>
   403	```
   404	
   405	### Which six parts earn their tokens
   406	
   407	| Current part | Judgment |
   408	|---|---|
   409	| Task | Keep. One outcome sentence steers strongly. |
   410	| Inputs | Compress to baseline and governing authorities. General background and neighboring project history are noise when the repository contains them. |
   411	| Deliverables | Keep as `DONE_WHEN` plus `WRITE_SCOPE`. Distinguish desired outcomes from allowed files. |
   412	| Verification | Keep and make commands exact. “Focused tests and canonical suite” is underspecified. |
   413	| Constraints | Keep only unusual hazards and actual prohibitions. Replace long negative file lists with an allowlist. |
   414	| Report | Remove from individual prompts. The runner owns the output path and injects the report contract. A repository run-report file, if required, is simply another deliverable and allowlisted path. |
   415	
   416	Always pin:
   417	
   418	- Genre.
   419	- Baseline SHA and baseline mode.
   420	- Mutation/commit/external-action authority.
   421	- Write allowlist for write sessions; `[]` for read-only.
   422	- Observable completion conditions.
   423	- Exact required verification.
   424	- Adapter schema version.
   425	
   426	Do not always pin the report path in semantic prose. The invocation already has `out`; duplicating it wastes tokens and risks mismatch. Pin a path only when the repository itself must gain a durable run-report artifact.
   427	
   428	Stop writing:
   429	
   430	- Broad “be thorough” language.
   431	- Repository history already available in authoritative files.
   432	- Exhaustive “do not touch X/Y/Z” lists when a positive allowlist suffices.
   433	- Repeated output-shape instructions.
   434	- Severity vocabulary in prose.
   435	- “Run the canonical suite” without the canonical command.
   436	- Ready-to-delegate six-part contracts inside a scout unless the lead actually plans to launch them. Those four contracts consumed most of the scout report.
   437	
   438	## C. Manifest v3
   439	
   440	The current manifest records transport health, not semantic health. `status:"OK"` covers both clean implementations and a review that found a blocker. All completed rows also remain `disposition:"pending"`, so direction quality cannot presently be learned.
   441	
   442	Make it an append-only event stream:
   443	
   444	### `run_started`
   445	
   446	- `run_key`
   447	- `task_id`
   448	- `attempt`
   449	- `parent_run_key`
   450	- `genre`
   451	- `prompt_contract`
   452	- `report_contract`
   453	- `prompt_sha256`
   454	- `prompt_tokens` or at least `prompt_bytes`
   455	- `base_requested`
   456	- `base_mode`
   457	- `head_start`
   458	- `upstream_start`
   459	- `write_scope`
   460	- `verification_profile`
   461	- Existing model, effort, sandbox, cwd, output, and timestamps
   462	
   463	### `run_finished`
   464	
   465	- `session_id`
   466	- `invocation_state`: `ok|failed|timeout|cancelled`
   467	- Numeric `runner_rc`
   468	- `error_stage`: `launch|session_init|execution|report_capture|report_parse`
   469	- `duration_ms`
   470	- `head_end`
   471	- `upstream_end`
   472	- `report_parse`: `valid|missing|invalid`
   473	- `semantic_status`
   474	- `completion`
   475	- `finding_counts`: blocker/should_fix/nit
   476	- `blocking_flag_count`
   477	- `pathspec_count`
   478	- `unowned_dirty_count`
   479	- `scope_violation_count`
   480	- `verification_counts`: pass/fail/not_run
   481	- `header_bytes`
   482	- `report_bytes`
   483	- Model token usage when available
   484	
   485	### `run_consumed`
   486	
   487	- `run_key`
   488	- `disposition`: `accepted|rework|superseded|discarded`
   489	- `lead_reverification`: `match|mismatch|not_run`
   490	- `mismatch_kinds`: test/pathspec/baseline/semantic/report
   491	- `followup_run_keys`
   492	- `lead_ruling_count`
   493	- `consumed_at`
   494	
   495	Do not mutate completed JSONL rows to replace `pending`; concurrency makes that brittle. Append consumption events keyed by `run_key`.
   496	
   497	Cheap fleet metrics then become:
   498	
   499	- Invocation/session-init failure rate.
   500	- Valid-report rate.
   501	- Semantic clean/findings/blocked distribution by genre.
   502	- Reverification agreement rate.
   503	- Scope-violation and baseline-drift rates.
   504	- Required-verification completion rate.
   505	- Rework rate by prompt template and genre.
   506	- Prompt tokens versus header tokens and total report tokens.
   507	- Duration and follow-up attempts by genre.
   508	
   509	Do not treat “flags per run” as a direction-quality failure. Surfacing an ambiguity is often evidence that the direction contract worked. Reverification mismatch and rework are much stronger quality signals.
   510	
   511	## D. Lead-side consumption
   512	
   513	The lead can safely stop fully reading every report.
   514	
   515	Recommended flow:
   516	
   517	1. Parse and validate the first JSON block.
   518	2. Reject automatic consumption if the schema is invalid, baseline mode fails, `unowned_dirty` is nonempty, or `pathspec` exceeds the allowlist.
   519	3. Replay `verification` commands mechanically and compare exit codes plus stable tail regexes. Do not compare elapsed times.
   520	4. Feed only the minified header into the lead’s context.
   521	5. Open prose selectively:
   522	
   523	   - Clean implementation: normally skip prose after successful replay.
   524	   - Review: consume structured findings; open prose only for findings being acted upon.
   525	   - Triage: read the decision matrix, composition recipe, and rulings—not the audit narrative.
   526	   - Root cause: read causal chain and remediation when assessing the fix; verification remains header-owned.
   527	   - Scout: consume the scheduling matrix and critical path; ignore delegation contracts unless launching them.
   528	
   529	6. Append a `run_consumed` event with replay agreement and disposition.
   530	
   531	The lead should continue re-verifying code, but it can stop re-reading verification tails, path lists, baseline notes, and “no commit” statements in prose. Those belong exclusively in the envelope.
   532	
   533	## E. Rulings requested
   534	
   535	My recommended defaults are in parentheses:
   536	
   537	1. Should a completed implementation with unavailable required acceptance verification be `blocked + complete`, as with CI-002? (**Yes.**)
   538	2. Baseline default for write tasks: exact SHA or descendant allowed? (**Exact; descendant only when explicitly selected.**)
   539	3. Should the scratchpad/final response be the canonical adapter report, with repository run reports treated as separate domain artifacts? (**Yes; avoid two canonical summaries.**)
   540	4. Should allowlist expansion stop the session or permit changes followed by a flag? (**Stop and flag by default.**)
   541	5. May grouped triage/scout verdict arrays make the JSON envelope larger than routine headers? (**Yes, capped around 8 KiB; machine-actionable decisions are worth more than a cosmetically tiny header.**)
   542	6. Who owns `run_consumed` events and disposition authority? (**The lead/wrapper, never the worker session.**)
   543	

exec
/bin/zsh -lc 'nl -ba /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     1	---
     2	name: multi-stream-worktrees
     3	description: Run 2+ independent workstreams in parallel — one git worktree + branch per stream, lead-driven codex-run pipelines by default (subagent directors only for judgment-heavy streams), landing as separate PRs. Use when a session has multiple independent implementation tasks that would otherwise run sequentially or collide in one tree.
     4	---
     5	
     6	# Multi-stream worktree orchestration
     7	
     8	Sequential delegation is the wall-clock bottleneck once implementation is
     9	outsourced (~15 min per adapter-sized Codex round). When a session has ≥2
    10	INDEPENDENT streams, parallelize with isolation. Skip all of this for
    11	single-stream sessions — it's pure overhead there.
    12	
    13	## THE SUBAGENT WAKE GAP (structural; discovered 2026-07-07, JouleWise 4-stream session)
    14	
    15	codex-run's "bounded exit re-invokes you" guarantee holds for the MAIN
    16	LOOP ONLY. A subagent orchestrator that backgrounds a codex-run and ends
    17	its turn is NOT re-invoked when the child exits — it stalls at every
    18	round boundary until something external wakes it. Twice in one session
    19	the whole 4-stream fleet sat dormant 20-30 min with completed Codex work
    20	on disk (detection: orchestrator transcript mtimes vs worktree write
    21	times vs zero codex procs — 3-source triangulation; agents' own status
    22	claims are useless here). Consequences, now standing:
    23	
    24	RESOLVED by the C-009 Fable+Codex meta-review consensus (2026-07-07,
    25	both models signed; ratified by Ed with the apex ground-truth condition —
    26	operation-loop §3). In every row below, "lead" = the FABLE main loop:
    27	Fable drives, gates, and adjudicates; cheaper models exist to save Fable
    28	tokens, and their outputs are advisory into Fable's decisions. The
    29	governing topology, by stream shape:
    30	
    31	| Stream shape | Topology |
    32	|---|---|
    33	| 1 stream | Main-loop direct codex-run; no orchestration machinery unless risk demands it |
    34	| 2–4 pipeline-shaped streams | Worktree per stream, LEAD drives codex-run directly (keeps the wake guarantee), coordinated via a lead-owned STREAM-STATE TABLE: stream, branch, current round, out-file path + status sentinel, next action — this table is the canonical scheduler surface and the guard against lead-context overload |
    35	| Judgment-heavy streams (real mid-stream design disputes) | Opus orchestrator that waits FOREGROUND on codex-run — bounded shell waits chunked under the tool timeout (`while [ ! -f out.status ]; do sleep 30; done`), each wait bounded by the child's timeout + a small grace window; if no status appears, mark the stream STALLED, inspect log/out paths, and hand back to the lead. NEVER background+end-turn (the wake guarantee does not reach subagents). The never-sleep-loop rule binds the MAIN loop only |
    36	| 5+ mixed streams | Wave scheduling: lead drives thin pipelines directly; Opus takes only the complex streams |
    37	| Hardware/live streams | Lead owns live verification always; no Codex/Opus "green" claim suffices |
    38	
    39	Supporting rules (still standing):
    40	- **Heartbeat = BACKSTOP, not scheduler** (~15–20 min background sleep;
    41	  on firing, 3-source triangulation + wake any stranded orchestrator).
    42	- **Wake-sweep rule in every orchestrator prompt:** on EVERY wake, sweep
    43	  all out-file `.status` sentinels for completed work first (recovery is
    44	  lossless — worktree + out-files are durable).
    45	- **Orchestrator returns name the out-files they're blocked on.**
    46	- SendMessage-resuming an orchestrator mid-round orphans its pre-resume
    47	  children's wake chain — after any fleet broadcast, verify wake chains.
    48	
    49	## Topology
    50	
    51	("Lead"/"orchestrator" here = the Fable main loop unless a stream
    52	genuinely needs a subagent director — see the wake gap above and the
    53	operation-loop §2/§3 tables. VALIDATED 2026-07-08 (C-010): a full
    54	4-stream resume-to-merge session ran with the LEAD driving every
    55	stream's codex-run pipeline directly — zero orchestrators, zero wake
    56	stalls, zero heartbeats. The subagent-orchestrator shape below remains
    57	for judgment-heavy streams only.)
    58	
    59	- **One worktree + branch per stream** (`git worktree add ../<repo>-<stream>
    60	  -b <stream-branch> <base>`), or `isolation: "worktree"` on the Agent call.
    61	  Two things this fixes at once: parallel writers can't collide, and each
    62	  worktree gets its own Codex bridge state (`git rev-parse --show-toplevel`
    63	  resolves per-worktree, so `.codex-bridge/` dirs and `resume --last`
    64	  pointers stay separate — parallel Codex threads are otherwise unusable).
    65	- **Stream direction: the LEAD drives each stream's codex-run pipeline
    66	  directly (the C-010-validated default; see the topology table above).**
    67	  A dedicated orchestrator subagent is the EXCEPTION for judgment-heavy
    68	  streams — per operation-loop §3 that director is OPUS (Fable stays
    69	  apex-only). When one is used (Agent tool, pass an EXPLICIT
    70	  `model:` — do not rely on inheritance: on 2026-07-07 a session
    71	  accidentally started on Opus meant five streams silently inherited the wrong
    72	  model and had to be relaunched; relaunching is cheap because durable state —
    73	  worktree diffs, `.codex-bridge/last-message.md`, and the Codex thread behind
    74	  `resume --last` — survives agent death), launched in a single message so
    75	  they run concurrently. Each owns its stream end-to-end: drives its own Codex thread
    76	  per the codex-delegation skill, runs the stream's tests, iterates, and
    77	  returns a summary + branch name — NOT file dumps.
    78	- **The lead stays the integrator:** it does not implement; it reviews each
    79	  stream's diff via the council/adversarial-review skills, runs any
    80	  live/hardware verification (orchestrators can't), resolves cross-stream
    81	  conflicts, and lands each stream as its own PR.
    82	
    83	## Stream-orchestrator prompt must include
    84	
    85	1. The worktree path and branch; everything happens there.
    86	2. The full codex-delegation prompt contract (pinned specs, environment
    87	   facts, bookkeeping fence, evidence demands) — the orchestrator relays it.
    88	3. What the orchestrator may verify itself (suite, CI-safe paths) vs what it
    89	   must RETURN for the lead (anything live/hardware/sudo/network).
    90	4. Commit instructions (atomic commits on the stream branch; no pushes).
    91	5. Return format: changed files, suite counts, deviations, open questions.
    92	6. That Codex is invoked ONLY via `codex-run` launched as a background Bash
    93	   call — its bounded exit re-invokes the agent (ending the turn is correct;
    94	   the harness wakes you). The full mechanism + rationale is the ONE home in
    95	   codex-delegation §Token-efficient consumption; the prompt must mandate it
    96	   (no bare `codex exec`/bridge calls, no separate watchers, no in-turn
    97	   sleep-loops).
    98	7. The mandatory post-implementation Codex counterreview (default per
    99	   codex-delegation §Economics): 2-3 parallel read-only lenses (each a
   100	   background `codex-run <out> -s read-only <prompt>`) over the diff before
   101	   committing, findings triaged and reported with dispositions.
   102	8. The test doctrine per codex-delegation §Test doctrine (amplification
   103	   round, then fresh-instance writer ≠ reviewer test review). The
   104	   orchestrator stays THIN — it triages and verifies; all reading-heavy
   105	   analysis goes to Codex lenses.
   106	9. A lens timeout policy: any Codex lens with no output at ~60 min is
   107	   presumed wedged — kill, retry ONCE with halved scope ("top-5 findings,
   108	   be concise"), then drop it and proceed, noting the drop. Never let one
   109	   hung subprocess block a completed implementation.
   110	
   111	## Checkpoint / stop protocol (validated 3-for-3, 2026-07-07)
   112	
   113	When the user calls a stop (or a session must end mid-fleet), issue each
   114	stream a STOP ORDER with exactly this shape — all three streams executed
   115	it cleanly first try:
   116	
   117	1. Supersede all prior 'continue' instructions; launch NOTHING new.
   118	2. Sweep out-file sentinels; commit completed work that VERIFIES quickly
   119	   (suite green, expected deltas); anything not quickly verifiable stays
   120	   dirty/stashed — do NOT debug under a stop order.
   121	3. Final ledger entry `### <S>-CHECKPOINT`: done units (hashes),
   122	   in-flight state, unprocessed out-files, and the EXACT next action a
   123	   resuming agent takes.
   124	4. Return: branch, commits, suite counts, resume point in one sentence.
   125	
   126	Lead side, in parallel: `pkill -f "codex exec"` (bounded-failure safe —
   127	warn streams the FAILED status is expected), push ALL stream branches,
   128	KEEP the worktrees, write the restart guide into the run report +
   129	RUN_STATE ("RESTART HERE" pointing at the ledgers), fold session lessons
   130	into skills BEFORE ending (they survive everything), commit+push main.
   131	Nothing is lost if branches+ledgers are pushed and worktrees kept.
   132	
   133	## Lead-side fleet health checks (Ed, 2026-07-07)
   134	
   135	Periodically (each time a stream lands, or ~hourly) examine the
   136	longest-running streams from the OUTSIDE — `ps -eo pid,etime,command | grep
   137	"codex exec"`, worktree `git status`, bridge-dir mtimes — and classify each:
   138	(a) healthy pipeline mid-phase → leave alone; (b) true top-level observer
   139	waiting on children → leave alone; (c) WEDGED — e.g. one lens subprocess
   140	hung for 50 min while siblings finished in 10 → intervene: kill the hung
   141	process yourself (the stream's watcher fires and it self-recovers) AND send
   142	the orchestrator recovery guidance; (d) decomposable — a stream serially
   143	grinding work that could fan out → tell it to parallelize or spawn it a
   144	helper. Ground truth comes from processes and file mtimes, not from the
   145	agents' own status claims. Two cheap ground-truth reads worth using
   146	(2026-07-07): the full `ps` command line of a `codex exec` child IS the
   147	orchestrator's delegation prompt — read it to audit relay quality
   148	without touching the stream; and stall detection is a 3-source
   149	triangulation — orchestrator transcript mtime vs worktree write times vs
   150	live codex procs (any one alone misleads: worktree writes continue after
   151	an orchestrator goes dormant because its children are still finishing).
   152	
   153	## Constraints
   154	
   155	- Streams must be genuinely independent — shared-file streams get merged into
   156	  one stream or sequenced. Check overlap before fanning out
   157	  (`git diff --stat` expectations per stream).
   158	- Bookkeeping (run state, queues, council/decision logs) belongs to the lead
   159	  AFTER integration, never to streams — parallel bookkeeping edits are
   160	  guaranteed conflicts.
   161	- Worktrees are cleaned up after their PR lands (`git worktree remove`).
   162	- STACKED PRs: GitHub only auto-retargets a stacked PR's base when the
   163	  base BRANCH IS DELETED, not when its PR merges. Retarget every stacked
   164	  PR to main (`gh pr edit N --base main`) IMMEDIATELY after the parent
   165	  merges, before any `gh pr merge` — 2026-07-08: a `gh pr merge` on a
   166	  still-stacked PR silently merged it into the parent branch instead of
   167	  main (recovered via a promotion PR; suite-build trace).
   168	- STATE THE SANDBOX TIER'S LIMITS IN EVERY STREAM PROMPT (2026-07-08:
   169	  two streams each burned a round rediscovering the worktree-commit
   170	  block that codex-delegation §caveat-3 already documented — the prompts
   171	  hadn't said it): worktree streams get "do NOT git commit; the lead
   172	  commits at the gate" (mechanism: codex-delegation §Token-efficient
   173	  caveat 3); read-only passes get "you cannot run the suite (no writable
   174	  temp) — the lead runs it" or a workspace-write sandbox with a temp dir.
   175	- Worktrees share TRACKED files only. Untracked artifacts (real
   176	  measurement corpora, local venvs, `runs/`) exist solely in the main
   177	  tree — stream prompts needing them must give the MAIN tree's absolute
   178	  path, and acceptance steps over them run read-only cross-tree
   179	  (2026-07-07 resume: a corpus acceptance check silently reported
   180	  "no runs/ dir" in-worktree; the lead's cross-tree run then exposed a
   181	  real pre-existing strict failure no in-worktree layer could see).
   182	- Worktree top-level docs (queue, status) are FROZEN at branch point —
   183	  lens findings about their staleness are a standing REJECT class
   184	  (reconcile at merge bookkeeping, never "fix" in-stream).
   185	- Fixture-first / hardware-blocked streams always get the FULL lens
   186	  tier: 2026-07-07 resume caught two wrong pinned wire contracts (ssh
   187	  argv `--` placement, construction-time remote root) that implementation,
   188	  unit tests (which PINNED the broken shapes), and per-unit lead gates
   189	  all passed; only the adversarial round refuted them. Wire/argv/protocol
   190	  pins should name their live-refutation step in the pin itself.
   191	- Live verification remains lead-only (role rule: council skill §Roles):
   192	  orchestrators and Codex both lack the hardware/sudo surface, and that
   193	  layer has caught every integration bug.
   194	
   195	## C-028 arc amendments (2026-07-11)
   196	
   197	- **Integration tree BEFORE the merge wave, always.** Merge all held
   198	  branches into a scratch integration branch, run the full suite +
   199	  corpus gates there, fix cross-stream failures on that tree, route
   200	  each fix hunk to its OWNING branch, review the tree, THEN wave.
   201	  C-028: seven individually-green branches produced 38 combined
   202	  failures (dominated by a fail-closed inventory correctly refusing
   203	  fields born after its branch cut). The tree never merges; verify
   204	  merged main is content-identical to it (empty diff) after the wave.
   205	- **Guarded wave script, but NEVER trust its completion banner.**
   206	  Per-PR: wait non-pending checks → halt on fail/conflict → merge with
   207	  --match-head-commit. A DNS blip silently skipped one PR mid-wave
   208	  (pipeline exit masked by tail); the loop printed COMPLETE anyway.
   209	  Post-wave, verify EVERY PR's merged state individually.
   210	- **State-file conflicts in waves**: union hunks in place (marker-level,
   211	  both sides); NEVER git checkout --ours/--theirs on state files —
   212	  whole-file checkout silently discards the other side's clean hunks
   213	  (cost a P2-005 row once). Pre-discipline branches carrying state-file
   214	  edits conflict with every checkpoint update; enforced WRITE_SCOPE
   215	  (post 2026-07-11) prevents the class.

exec
/bin/zsh -lc "SNAP=/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot; rg -n -i 'service[_ -]?tier|CODEX_SERVICE_TIER|fast tier|fast mode|\\bfast\\b' \""'$SNAP" --glob '"'*.md'; rg -n 'codex-run(?"'!-v3)'"' \""'$SNAP" --glob '"'*.md' -P; rg -n 'Codex 5\\.5|gpt-5\\.5|read-only 5\\.5|to 5\\.5|5\\.5-' \""'$SNAP" --glob '"'*.md'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:10:reports — and prose summaries drift the moment work moves fast. One delegated
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:348:  Ed restored high/xhigh per complexity; fast tier implemented per Ed's
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:349:  exact spec (per-call CODEX_SERVICE_TIER=fast via scripts/codex-bridge
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:163:  re-pricing, and never fast-track a fix on the auditor's tier alone.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:3:description: Run 2+ independent workstreams in parallel — one git worktree + branch per stream, lead-driven codex-run pipelines by default (subagent directors only for judgment-heavy streams), landing as separate PRs. Use when a session has multiple independent implementation tasks that would otherwise run sequentially or collide in one tree.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:15:codex-run's "bounded exit re-invokes you" guarantee holds for the MAIN
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:16:LOOP ONLY. A subagent orchestrator that backgrounds a codex-run and ends
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:33:| 1 stream | Main-loop direct codex-run; no orchestration machinery unless risk demands it |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:34:| 2–4 pipeline-shaped streams | Worktree per stream, LEAD drives codex-run directly (keeps the wake guarantee), coordinated via a lead-owned STREAM-STATE TABLE: stream, branch, current round, out-file path + status sentinel, next action — this table is the canonical scheduler surface and the guard against lead-context overload |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:35:| Judgment-heavy streams (real mid-stream design disputes) | Opus orchestrator that waits FOREGROUND on codex-run — bounded shell waits chunked under the tool timeout (`while [ ! -f out.status ]; do sleep 30; done`), each wait bounded by the child's timeout + a small grace window; if no status appears, mark the stream STALLED, inspect log/out paths, and hand back to the lead. NEVER background+end-turn (the wake guarantee does not reach subagents). The never-sleep-loop rule binds the MAIN loop only |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:55:stream's codex-run pipeline directly — zero orchestrators, zero wake
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:65:- **Stream direction: the LEAD drives each stream's codex-run pipeline
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:92:6. That Codex is invoked ONLY via `codex-run` launched as a background Bash
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:100:   background `codex-run <out> -s read-only <prompt>`) over the diff before
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:15:`codex-run <outfile> -C <repo> -s workspace-write "<prompt>"`.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:21:`~/.local/bin/codex-run` is the ONE stable mechanism for running Codex from
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:27:await" → nothing exits → nothing wakes). `codex-run` wraps a single Codex call
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:34:1. `codex-run <out.md> [--timeout SEC] [-C DIR] [-s SANDBOX] [--resume] <prompt>`
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:53:Parallel fan-out = N background `codex-run` calls, one out-file each; you wake
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:63:out-file parsing for multi-finding rounds. codex-run remains THE mechanism for
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:69:exec`/bridge call without codex-run (reintroduces both footguns); multiple
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:70:codex-run launches batched in one shell for-loop — multi-line prompts break
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:72:(bit twice 2026-07-09) — one codex-run per Bash call, parallel calls in one
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:75:Orchestrator prompts must mandate codex-run (multi-stream-worktrees points
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:77:prefer codex-run directly; the bridge's `resume --last` maps to `codex-run
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:83:   orchestrators are NOT re-invoked by their codex-run children's exits; the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:86:2. `codex-run --resume` forwards cwd (via `cd`, which also scopes `--last`'s
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:188:- `codex-run --resume` forwards cwd and sandbox; `codex exec resume` itself
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:226:**Instant completion = launch failure.** Any codex-run that completes within
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:259:`codex-run` forwards `-i/--image`. The lead still makes the design DECISIONS
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:408:Invocation gotcha (2026-07-11): `codex-run -C <dir>` requires a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:499:  use N `codex-run` calls with `-s read-only`, one out-file each, or the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:571:  pattern now: every brief that delegates to codex-run includes, up
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:100:(multi-stream skill §wake gap): lead-driven codex-run pipelines with a
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:147:packets; one codex-run per packet). No ceremony for mechanical choices;
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:192:codex-delegation §Invoke (codex-run background-call protocol; plus the
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:122:  lens (invoked per codex-delegation's ONE stable mechanism — `codex-run
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:22:sentinels); first session mixing codex-run with Workflow-tool orchestration.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:29:| operation-loop §3 model assignment | USED + DEVIATED | codex volume + Fable gates held; ultracode added Workflow-tool orchestration with agentType:'codex' agents — NOT the codex-delegation "one stable mechanism" (codex-run), and it worked well: structured-schema findings, deterministic refuter tiers, zero stalls | codex-delegation needs a §: when to wrap codex in Workflow (fan-out + verification tiers + structured output) vs raw codex-run (single long impl unit, bounded-exit wake) |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:35:| operation-loop §7 fleet health | USED (nothing to do) | zero stalls across ~15 codex-runs + 3 workflows; bounded exits + workflow notifications made heartbeats unnecessary (consistent with C-010) | — |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:63:   alternative to codex-run, with its trigger condition (deterministic
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:108:derivability closed (scripts/codex-run committed; orchestration.md
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:125:codex-run sessions, zero wake stalls; §read-only parallel lenses;
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:159:- codex-delegation: codex-run bg protocol exact; FIX-N contracts 7/7 one-shot-clean; final-head passes caught 3 blockers+7 should-fixes AFTER lens+fix+lead-gate layers — the layer is load-bearing, keep; 1 PROMPT-DEFECT (lead pinned fail-closed-on-any-existing-file for inferred sidecars; scorer sidecars broke) — lesson: when pinning fail-closed semantics over a namespace shared by MULTIPLE artifact types, enumerate the other residents first.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:167:- codex-delegation: §Invoke background codex-run protocol 5/5 clean (4 lenses + 1 discussion round, zero stalls, zero thin outputs); §Parallel threads read-only fan-out shape used as designed; §Prompt contract lens-angle + severity + failure-scenario + checks-performed clauses all yielded (every lens delivered structured, citable findings); "send the lead's synthesis back for attack" doctrine PAID AGAIN — D1 overturned a lead-accepted blocker (C5-1.1 already contract-capped) and out-designed the lead's work-plan order. Deviation: none.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:173:- codex-delegation: 20 codex sessions, zero stalls; FIX-N one-shot record now 13/13; instant-completion diagnostic caught 1 real launch failure (zsh parse error on a for-loop of prompts — lesson: never batch multiple codex-run prompts in one shell loop; separate calls); severity-tiered pipeline caught a statistics blocker (percentile-UCB unidentifiable at n=10) that BOTH the lead and the implementer had provisionally accepted — the fresh-lens layer is the quality mechanism for design-freedom delegation.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:181:- codex-delegation: FIRST full Workflow-tool orchestration (46 agents, zero stalls, zero errors) — the sanctioned Workflow alternative scales to implement→lens→refute shapes, and its codex WRAPPER agents can git commit+push in worktrees (they are full agents), beating direct codex-run for worktree streams where codex's own sandbox still index.lock-blocks; refuter layer killed 10/30 findings pre-triage (precision working); mutation testing appeared organically in a test-audit lens (5 mutations proving gaps) — fold candidate for §Test doctrine: "test-audit lenses may be prompted to MUTATION-TEST the gates they audit"; FIX-N one-shot record now 22/22; NEVER batch multiple codex-run launches in one zsh for-loop (parse-error launch failure, second occurrence class).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:193:- codex-delegation: §Invoke (codex-run ×10, zero stalls; one-per-Bash-call rule held), §Prompt contract (all six parts; autonomy clause paid off — 5 unprompted premise corrections), §Direction doctrine (lens-names-an-angle, CLEAN-needs-checks-line both used), §Model-version scoping (FOLLOWED: calibration batch logged, promotion refused pending A/B), §Consume (final-message-only; .status naming), §Economics (counterreview of the lead's synthesis was the round that caught the most). GAP FOUND: skill still titled "gpt-5.5"; model now gpt-5.6-sol behind config — needs a one-line model-note after the sealed A/B.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:199:- codex-delegation §Invoke/§Prompt-contract/§Economics: 6+ codex-run-v2 sessions (merge review, p2041 diagnosis, deletion triage, flake root-cause, vetted composition ULTRA, p2037 ULTRA, scheduling scout). NEW §Effort-tier policy added (Ed): ultra=subagent-needing sessions only; xhigh/high individual tasks; push xhigh scope until first prod-quality miss and record ceiling. The two ULTRA launches this session predate the policy — going forward they'd be xhigh.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:39:| council (5.5-reviews-consequential-decisions) | USED, high yield | peer counterreview of both synthesis packets; C-015 peer added the per-item failure-economics catch nobody else saw | — |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:193:- codex-delegation: §Invoke (codex-run ×10, zero stalls; one-per-Bash-call rule held), §Prompt contract (all six parts; autonomy clause paid off — 5 unprompted premise corrections), §Direction doctrine (lens-names-an-angle, CLEAN-needs-checks-line both used), §Model-version scoping (FOLLOWED: calibration batch logged, promotion refused pending A/B), §Consume (final-message-only; .status naming), §Economics (counterreview of the lead's synthesis was the round that caught the most). GAP FOUND: skill still titled "gpt-5.5"; model now gpt-5.6-sol behind config — needs a one-line model-note after the sealed A/B.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:140:| **Codex 5.5-high** (volume) | implementation, counterreview lenses, test writing + writer≠reviewer test review, whole-module reading/analysis, computer use, AND all security-shaped/adversarial-audit work (codex-delegation §Security) | the merge gate; live/hardware verification (no device/sudo); bookkeeping | near-limitless quota → redundant fresh-eyes passes are free; fresh instances carry no thread state → genuine independent review even of its own code; not tier-gated on adversarial vocabulary |
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:143:**5.5-reviews-consequential-decisions doctrine (Ed, 2026-07-07):** every
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:187:not vibes. Early signal (2026-07-07): design-freedom delegation to 5.5
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:210:   stream spec/prompt to 5.5 for opinion, lead judges/revises, THEN
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:19:2. **Lenses (parallel; default executor: fresh read-only Codex 5.5
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:111:- **Peer (Codex/gpt-5.5 or equivalent second model)** — implements against pinned
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:8:> Model history: gpt-5.5 through 2026-07-09; gpt-5.6-sol ("Sol") since.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:301:0. FAILED-TEST TRIAGE (Ed, 2026-07-07): when any test fails, Codex 5.5 gets
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:318:Codex gpt-5.5-high usage is near-limitless — treat Codex rounds as free and
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:539:  implementer AND lead initially under-weighed it; a fresh read-only 5.5

exec
/bin/zsh -lc "sed -n '410,442p' RUN_STATE.md | nl -ba -v410; sed -n '912,936p' RUN_STATE.md | nl -ba -v912; sed -n '1,45p' scripts/codex-bridge | nl -ba; sed -n '145,166p' scripts/codex-bridge | nl -ba -v145; sed -n '3200,3242p' docs/decision_log.md | nl -ba -v3200; sed -n '4922,5035p' docs/decision_log.md | nl -ba -v4922" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   410	
   411	### ESCALATION TRIGGER FIRED — quiet-guard observation-failure→absence class (recorded ~01:15 2026-08-06)
   412	
   413	qg-delta3 (xhigh) ruled the class RECURRENT at count 2: round 3's
   414	protected-set fix omitted the lease owner and matched by PID only,
   415	after round 2's retry introduced the class. Per rule 11 the next spend
   416	is a CONSULT — launched (Sol xhigh, read-only) on the closure shape,
   417	with the magistrate's structural diagnosis (protected-set ENUMERATION
   418	is the regenerating failure; Option A = eliminate enumeration,
   419	universally fail-closed retry) and an admission on the record: the
   420	round-2 lead contract seeded the class by dictating "retry for
   421	unrelated pids" (an enumeration concept) to serve an availability
   422	requirement the lead is now prepared to revoke. F2 (lock continuity)
   423	is CLOSED; init-durability remains closed at count 1. The branch does
   424	NOT land until the consult-adopted shape closes the class and a delta
   425	re-audit accepts.
   426	
   427	### Ed directive batch (2026-08-05 ~22:00, in-thread; 12-hour autonomous window)
   428	
   429	1. **Sol effort cap LIFTED**: high/xhigh per complexity (rule 10
   430	   restored); prior HIGH-only directive retired by its author.
   431	2. **Codex Fast Mode (service tier)**: 1.5x speed / 2.5x credits;
   432	   Ed specified the exact bridge implementation (per-call opt-in via
   433	   `CODEX_SERVICE_TIER=fast`, never a standing default) — being
   434	   implemented on `impl/codex-fast-tier`. License: use fast on xhigh
   435	   runs by default, fast-on-high when other streams block on the
   436	   result.
   437	3. **D-113 RULED (c) by Ed**: Window B re-evaluation ABANDONED; Window
   438	   C will be collected fresh. Prerogative, Ed verbatim: "the rigor of
   439	   the data collected matters, i have ample time — soundness and
   440	   quality of the project and claims above all." Sol xhigh consult on
   441	   managing that prerogative is in flight; the magistrate transcribes
   442	   D-113 after synthesis.
   912	   an envelope.
   913	4. **t3-native Codex threads are Ed-direct only** — never targets for
   914	   lead-delegated or gate-bearing work (that stays on wrapped routes);
   915	   material consumption of native-thread output requires a
   916	   lead-authored ingestion note in the session manifest (interim form).
   917	5. Delegated-run visibility: substantial background Sol rounds go
   918	   through the tracked codex subagent (visible "Subagent task"
   919	   activity) — lifecycle visibility only; envelope/manifest ceremony
   920	   unchanged underneath.
   921	
   922	**Ed rulings tonight (ratification via packet):** R1 — fresh-eyes
   923	sweep cadence is WORK-CHUNK-ANCHORED (post-consumption of substantial
   924	rounds / merge waves / adjudications) with a mechanical
   925	materially-consumed-invocation backstop counter; this rules the shape
   926	`D080-TRIGGER-01` (queue A52) was blocked on — row stays BLOCKED until
   927	the D-080 amendment ratifies it. R2 — cold gate uses
   928	CHARTER-SUPPRESSION (standing tracked hash-pinned charter replaces
   929	`CLAUDE.local.md` ingestion; packet validator refuses hash mismatch);
   930	cold FABLE judge + Sol xhigh contract-lens refuter (cross-model
   931	diversity; Sol's conflict-disclosed concurrence on topology). R3 —
   932	COMPRESSED shadow cutover: six acceptance gates during real work, no
   933	fictional shadow period; rollback = pre-t3 mechanism per route, TUI
   934	operation remains available; Sol's full-shadow preference recorded as
   935	dissent. Gates: native-discussion, phone-approval, app-death recovery,
   936	checkpoint-restore, isolated-native-write, cold-packet-handoff. **This
     1	#!/usr/bin/env bash
     2	set -euo pipefail
     3	
     4	usage() {
     5	  cat <<'USAGE'
     6	Usage:
     7	  scripts/codex-bridge new [PROMPT...]
     8	  scripts/codex-bridge resume [--last|SESSION_ID] [PROMPT...]
     9	  scripts/codex-bridge review [PROMPT...]
    10	
    11	Prompt text may also be piped on stdin. The last Codex response is mirrored to
    12	.codex-bridge/last-message.md for Claude Code to read or quote back.
    13	
    14	Each invocation also writes a durable local audit trail under .codex-bridge/:
    15	prompt snapshots, response snapshots, logs, status files, and
    16	invocation_manifest.jsonl rows with prompt/output hashes and session ids.
    17	
    18	Defaults: model gpt-5.6-sol, reasoning effort high. Callers select xhigh for
    19	hard individual work or ultra only for sessions that must spawn subagents by
    20	setting CODEX_REASONING_EFFORT deliberately.
    21	
    22	Opt in to Codex Fast Mode for one call with:
    23	  CODEX_SERVICE_TIER=fast scripts/codex-bridge new ...
    24	
    25	When .codex-bridge/app-host-thread-id exists, new and review run their real
    26	turn in that Codex desktop task so the native pet sees app-owned activity.
    27	Set CODEX_APP_BRIDGE=off to require the standalone CLI transport.
    28	
    29	Governed delegated runs follow docs/contracts/bridge_protocol.md: the prompt
    30	begins with a BRIDGE_TASK_V1 header; audited runs that emit a full
    31	claude-codex-report/v1 body are exempt from the bridge-report/v1 trailer.
    32	USAGE
    33	}
    34	
    35	json_quote() {
    36	  printf '"'
    37	  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
    38	  printf '"'
    39	}
    40	
    41	now_utc() {
    42	  date -u +%Y-%m-%dT%H:%M:%SZ
    43	}
    44	
    45	sha256_file() {
   145	response_dir="$bridge_dir/responses"
   146	mkdir -p "$bridge_dir" "$prompt_dir" "$response_dir"
   147	
   148	codex_bin="${CODEX_BIN:-codex}"
   149	codex_model="${CODEX_MODEL:-gpt-5.6-sol}"
   150	codex_effort="${CODEX_REASONING_EFFORT:-high}"
   151	codex_service_tier="${CODEX_SERVICE_TIER:-default}"
   152	case "$codex_service_tier" in
   153	  default|fast) ;;
   154	  *)
   155	    printf 'Invalid CODEX_SERVICE_TIER: %s (expected default or fast)\n' \
   156	      "$codex_service_tier" >&2
   157	    exit 64
   158	    ;;
   159	esac
   160	fresh_model_args=(-m "$codex_model" -c "model_reasoning_effort=$codex_effort" -c "service_tier=$codex_service_tier" -c "mcp_servers.claude.enabled=false")
   161	resume_model_args=(-c "model=$codex_model" -c "model_reasoning_effort=$codex_effort" -c "service_tier=$codex_service_tier" -c "mcp_servers.claude.enabled=false")
   162	last_message="$bridge_dir/last-message.md"
   163	stamp="$(date -u +%Y%m%dT%H%M%SZ)"
   164	manifest_file="$bridge_dir/invocation_manifest.jsonl"
   165	app_bridge_helper="$repo_root/scripts/codex-app-bridge.mjs"
   166	app_host_file="${CODEX_APP_BRIDGE_HOST_FILE:-$bridge_dir/app-host-thread-id}"
  3200	guardrails extending this stop line landed verbatim in
  3201	`docs/orchestration.md` §"Spend guardrails (WO-022...)" — capstone
  3202	benchmark bands (session/WO/arc tiers, soft record-and-continue vs hard
  3203	pause-and-ask-Ed), the deliverable-progress tripwire bound to these
  3204	D-060 gates, the named-failure bar for process innovation, and the
  3205	keep-defender guarantee. Landing snapshot receipt (estimated; close-out
  3206	refresh owed):
  3207	`docs/reviews/2026-07-13-comprehensive-audit/receipts/WO-022-audit-close-spend.json`.
  3208	
  3209	## D-061: Review-layer evaluation rule v2 (replaces the two-zero-sessions drop rule)
  3210	
  3211	- Date: 2026-07-09
  3212	- Status: accepted (C-027; process-layer, within council authority)
  3213	- Phase: cross-phase / process instrumentation
  3214	
  3215	Context: the "drop a layer after two zero-catch sessions" rule was
  3216	falsified by its own record — integration review returned zero unique
  3217	catches twice (C-017, CP-5) and then caught five real cross-stream seams
  3218	(C-024). Mechanical application would have deleted the layer immediately
  3219	before its highest-value session.
  3220	
  3221	Decision: layer evaluation uses (a) applicability decided by
  3222	PRE-DECLARED mechanical predicates (e.g. integration review counts only
  3223	when 2+ independently developed streams merge touching a shared
  3224	contract/consumer/generated artifact), never post-hoc judgment; (b) an
  3225	outcome taxonomy separating accepted-unique-defect / duplicate /
  3226	clean-verification / false-positive-suppression — suppression is
  3227	valuable but is not a catch; (c) fixed severity weights declared before
  3228	the session; (d) three applicable exposures TRIGGER an expected-loss
  3229	review decision, never automatic deletion; (e) safety, final-head, and
  3230	integration layers are never auto-dropped on zero-defect streaks —
  3231	they are judged by expected-loss reduction.
  3232	
  3233	Alternatives considered: keep the two-zero rule (falsified); "three
  3234	applicable sessions, severity-weighted" as free-text judgment (rejected
  3235	in council — reintroduces the discretion that made the old rule
  3236	unfalsifiable).
  3237	
  3238	## D-062: Confirmatory sampling policy — fixed n, explicit demotion, no silent top-ups
  3239	
  3240	- Date: 2026-07-09
  3241	- Status: accepted (C-027; scientific protocol, ratifies the RIGOR/STATS
  3242	  adjudication; amends the top-up language in
  4922	## D-080: Standing fresh-eyes sweep — a periodic, non-reactive outside review
  4923	
  4924	- Date: 2026-07-27
  4925	- Status: accepted (drafted by the lieutenant, magistrate-ratified 2026-07-27)
  4926	- Phase: cross-phase / process instrumentation
  4927	- Applies to: the `council` skill (the ONE home for the mechanism), the
  4928	  `operation-loop` skill (firing rule only), `docs/council_log.md`,
  4929	  `docs/process/model_allocation_ledger.md`
  4930	
  4931	Terms, in plain language, because this entry is read by people outside the
  4932	project:
  4933	
  4934	- **Reactive trigger.** An existing rule that summons an outside reviewer when a
  4935	  named condition occurs — a second fix round on the same defect, a contract
  4936	  change, an irreversible action. It fires on a problem someone has already
  4937	  recognised.
  4938	- **Sweep.** A review that happens on a schedule rather than in response to a
  4939	  problem, and that arrives with no question in hand.
  4940	- **Cold lens.** A reviewer started in a fresh session with none of the working
  4941	  session's context, so it does not inherit the working session's assumptions.
  4942	- **Magistrate / lieutenant / cold gate.** The orchestration roles defined by
  4943	  the operator's global orchestration rule 11, which is the authority for the
  4944	  topology; this entry references it and does not restate it.
  4945	
  4946	Context. Every escalation trigger in the process stack is reactive, and a
  4947	trigger catches only what can be NAMED in advance. The two costliest failures of
  4948	2026-07-26/27 were nameless until postmortem: roughly ten hours of an open quiet
  4949	measurement window lost to an untracked background job, and six fix rounds spent
  4950	building a guard on the wrong axis. Neither had a recognised condition to fire
  4951	on, so no trigger could have fired. Nothing in the stack was periodic and
  4952	outside-facing, which left that whole class of failure uncovered.
  4953	
  4954	1. **A standing fresh-eyes sweep is adopted, on ONE cadence unit.** The sweep
  4955	   runs every **10 delegated invocations**, plus mandatorily at every **phase
  4956	   boundary**. The number 10 is explicitly PROVISIONAL and is to be calibrated
  4957	   against `docs/process/model_allocation_ledger.md` after two sessions.
  4958	
  4959	   *Options considered.* (a) The lieutenant's draft cadence — an OR over
  4960	   invocation count, wall-clock time, and phase boundaries — rejected by the
  4961	   magistrate as the first of three amendments: three counters means three ways
  4962	   to argue about whether the mechanism fired, and a cadence that can be argued
  4963	   about is a cadence that will be argued away. (b) Wall-clock as the unit —
  4964	   rejected outright: "active session work" is a clock nobody keeps, and three
  4965	   hours of bookkeeping is not three hours of hot integration. (c) Invocation
  4966	   count plus phase boundaries — chosen: the count is already in the manifest
  4967	   event stream, it scales with work density rather than elapsed time, and it is
  4968	   unarguable.
  4969	
  4970	2. **Composition rotates: a cold Fable lens every sweep, plus one alternating
  4971	   second lens.** The cold Fable instance (fresh session, no loop context) runs
  4972	   at every sweep and never rotates out — it is the raison d'être, the only lens
  4973	   aimed at the nameless failure class. The second lens alternates between the
  4974	   Opus contract lens and the Sol execution lens. All three run only at phase
  4975	   boundaries, or when the cold lens flags something material.
  4976	
  4977	   *Options considered.* (a) The lieutenant's draft — cold lens plus both
  4978	   verification lenses at every sweep, justified by the execution lens's record
  4979	   of catches — rejected by the magistrate as the second amendment, and the
  4980	   justification corrected as a MISCITATION: the execution lens's famous catches
  4981	   (a 5e-324 floor exploit, a wall-clock slew, GPU DVFM aliasing) were all made
  4982	   in REACTIVE review with a specific artifact in hand. A sweep arrives with no
  4983	   question, and an execution lens with no target degenerates into "run the
  4984	   tests again." Contract and execution are verification lenses, and the
  4985	   existing adversarial gauntlet already exercises both reactively at every
  4986	   review. (b) Cold lens alone, always — rejected: cross-model diversity is
  4987	   cheap and a fresh same-family instance still shares its family's
  4988	   dispositions. (c) Cold lens plus one rotating verification lens — chosen.
  4989	
  4990	3. **The packet has six sections and five of them are MECHANICALLY GENERATED.**
  4991	   Sections (a)–(e) are generated from manifests and logs rather than composed:
  4992	   (a) the phase objective VERBATIM as stated at phase start; (b) the mechanical
  4993	   log since the last sweep — invocations, one-line outcomes, and round counts
  4994	   per objective; (c) time and spend against plan; (d) the next three planned
  4995	   actions; (e) open anomalies, INCLUDING everything observed and explained
  4996	   away. Only (f) is composed: current beliefs and the steelman against them.
  4997	
  4998	   *Options considered.* (a) The lieutenant's draft organising principle — a
  4999	   packet built as "the assembler's evidence against itself" — rejected by the
  5000	   magistrate as the third amendment, and this is the crux of the ratification:
  5001	   such a packet contains only NAMED doubts, which is the exact thing the sweep
  5002	   exists to escape. If the assembler could state the case against its own work,
  5003	   it would not need fresh eyes. The assembler's blind spots ARE the target, so
  5004	   the assembler's hit rate must not be load-bearing. (b) A wholly mechanical
  5005	   packet with no composed section — rejected: the steelman section is cheap and
  5006	   gives the reviewer the working position to push against. (c) Five mechanical
  5007	   sections plus one composed — chosen. Each mechanical section is aimed at an
  5008	   observed failure shape: round counts per objective expose the
  5009	   six-round-guard pattern without anyone recognising it; time and spend against
  5010	   plan expose the ten-hour-loss shape; explained-away anomalies are where a
  5011	   time-anchor defect (D-078) and a screensaver contamination both hid; and
  5012	   drift between the objective as stated and the objective as pursued is
  5013	   precisely what cold eyes see and warm eyes do not.
  5014	
  5015	4. **Anti-ritual clauses, including falsifiability of the mechanism itself.**
  5016	   (i) Only PLAN-CHANGING catches count — a catch that altered no decision is
  5017	   ritual's camouflage. (ii) Evaluation is over SESSIONS, matching the existing
  5018	   zero-unique-catch rule: a rotating lens with zero plan-changing catches over
  5019	   two full sessions rotates down; the cold lens is evaluated on a one-phase
  5020	   window and is not exempt. (iii) The MECHANISM ITSELF is falsifiable — if the
  5021	   whole sweep produces no plan-changing catch across one full phase, it returns
  5022	   to the magistrate for termination or redesign. The real anti-ritual guard,
  5023	   however, is clause 3's mechanical packet: ritual enters through the packet
  5024	   first, by way of sections nobody generates honestly.
  5025	
  5026	   *Options considered.* (a) Adopt the sweep with no termination condition —
  5027	   rejected: a periodic mechanism with no way to die is the definition of
  5028	   ritual, and the process stack already requires layers to justify themselves
  5029	   on evidence (D-061). (b) Count all catches — rejected: catch counts that
  5030	   include catches nobody acted on measure activity, not value.
  5031	
  5032	5. **The sweep supplements the reactive triggers and never replaces them.** All
  5033	   mandatory reactive triggers stand unchanged. One asymmetric reset rule: a
  5034	   trigger consult may reset the sweep counter ONLY IF its packet included the
  5035	   sweep's mechanical sections, because the function — outside eyes on raw state

codex
Two high-impact contradictions are already confirmed: the stack still teaches “background exit guarantees wake” even though its own later field note records five detached-background failures, and it still contains the superseded two-zero-session auto-drop rule despite D-061 replacing it. Fast mode appears only in the usage log—not in any skill—and the repository implementation confirms it is a one-call environment opt-in through `scripts/codex-bridge`.
exec
/bin/zsh -lc "~/.local/bin/codex-run-v3 2>&1 | sed -n '1,120p'; scripts/codex-bridge --help 2>&1 | sed -n '1,55p'; rg -n 'codex-run-v3|scripts/codex-bridge|BRIDGE_TASK_V1|bridge-report/v1|claude-codex-report/v1|service_tier|CODEX_SERVICE_TIER' docs/contracts/bridge_protocol.md docs/orchestration.md scripts/codex-run scripts/codex-bridge" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
usage: codex-run-v3 <out.md> [--timeout SEC] [-C DIR] [-s SANDBOX]
       [-i|--image FILE] [-m|--model MODEL] [--effort EFFORT]
       [--retries N] [--manifest FILE] [--role ROLE] [--parent REPORT]
       [--resume] [--genre review|implementation|triage|root_cause|scout]
       [--write-scope '["path","directory/**"]']
       [--no-genre] <prompt>
       codex-run-v3 resume <run_key> --approve-scope-add '["path"]'
       --approval-note 'reason'
       codex-run-v3 consume <manifest> <run_key>
       --disposition accepted|rework|superseded|discarded
       [--reverify match|mismatch|not_run] [--mismatch-kinds LIST]
       [--followups LIST] [--rulings N]
Usage:
  scripts/codex-bridge new [PROMPT...]
  scripts/codex-bridge resume [--last|SESSION_ID] [PROMPT...]
  scripts/codex-bridge review [PROMPT...]

Prompt text may also be piped on stdin. The last Codex response is mirrored to
.codex-bridge/last-message.md for Claude Code to read or quote back.

Each invocation also writes a durable local audit trail under .codex-bridge/:
prompt snapshots, response snapshots, logs, status files, and
invocation_manifest.jsonl rows with prompt/output hashes and session ids.

Defaults: model gpt-5.6-sol, reasoning effort high. Callers select xhigh for
hard individual work or ultra only for sessions that must spawn subagents by
setting CODEX_REASONING_EFFORT deliberately.

Opt in to Codex Fast Mode for one call with:
  CODEX_SERVICE_TIER=fast scripts/codex-bridge new ...

When .codex-bridge/app-host-thread-id exists, new and review run their real
turn in that Codex desktop task so the native pet sees app-owned activity.
Set CODEX_APP_BRIDGE=off to require the standalone CLI transport.

Governed delegated runs follow docs/contracts/bridge_protocol.md: the prompt
begins with a BRIDGE_TASK_V1 header; audited runs that emit a full
claude-codex-report/v1 body are exempt from the bridge-report/v1 trailer.
scripts/codex-bridge:7:  scripts/codex-bridge new [PROMPT...]
scripts/codex-bridge:8:  scripts/codex-bridge resume [--last|SESSION_ID] [PROMPT...]
scripts/codex-bridge:9:  scripts/codex-bridge review [PROMPT...]
scripts/codex-bridge:23:  CODEX_SERVICE_TIER=fast scripts/codex-bridge new ...
scripts/codex-bridge:30:begins with a BRIDGE_TASK_V1 header; audited runs that emit a full
scripts/codex-bridge:31:claude-codex-report/v1 body are exempt from the bridge-report/v1 trailer.
scripts/codex-bridge:151:codex_service_tier="${CODEX_SERVICE_TIER:-default}"
scripts/codex-bridge:152:case "$codex_service_tier" in
scripts/codex-bridge:155:    printf 'Invalid CODEX_SERVICE_TIER: %s (expected default or fast)\n' \
scripts/codex-bridge:156:      "$codex_service_tier" >&2
scripts/codex-bridge:160:fresh_model_args=(-m "$codex_model" -c "model_reasoning_effort=$codex_effort" -c "service_tier=$codex_service_tier" -c "mcp_servers.claude.enabled=false")
scripts/codex-bridge:161:resume_model_args=(-c "model=$codex_model" -c "model_reasoning_effort=$codex_effort" -c "service_tier=$codex_service_tier" -c "mcp_servers.claude.enabled=false")
scripts/codex-bridge:306:      --service-tier "$codex_service_tier" \
scripts/codex-bridge:357:    printf ',"tool":%s' "$(json_quote "scripts/codex-bridge")"
scripts/codex-bridge:368:    printf ',"service_tier":%s' "$(json_quote "$codex_service_tier")"
docs/orchestration.md:217:1. ACCOUNTING SOURCE. Sol spend: `codex-usage` local accounting (the standing snapshot convention), corroborated by codex-run-v3 manifest `token_usage` rows where populated. The extraction window must cover the full arc — sum incremental snapshots for multi-day arcs; a single trailing-24h view is insufficient. Fable spend: estimated from local usage accounting; each snapshot names its method and price-table version. Price table v2026-07 (pinned until amended): GPT-5.6-sol $5/$30 per M in/out, cached input $0.50; Fable 5 $10/$50, cache reads $1. All figures are estimates, not billing truth, and are recorded as such. Missing data is recorded as `accounting_unknown`, never as zero.
docs/orchestration.md:313:- Project bridge: `scripts/codex-bridge`; writes prompt snapshots,
docs/orchestration.md:332:  appendices; `scripts/codex-run` and `scripts/codex-bridge` provide
docs/contracts/bridge_protocol.md:29:`BRIDGE_TASK_V1` sentinel line, one JSON object, and an `END_BRIDGE_TASK_V1`
docs/contracts/bridge_protocol.md:52:- `OUTPUT_PROTOCOL`: Required return protocol; `bridge-report/v1`.
docs/contracts/bridge_protocol.md:105:BRIDGE_TASK_V1
docs/contracts/bridge_protocol.md:131:  "OUTPUT_PROTOCOL": "bridge-report/v1"
docs/contracts/bridge_protocol.md:133:END_BRIDGE_TASK_V1
docs/contracts/bridge_protocol.md:138:Protocol layering is intentional: `claude-codex-report/v1` (D-064) remains
docs/contracts/bridge_protocol.md:140:`codex-run-v3 --genre`, while `bridge-report/v1` is the lightweight final-lines
docs/contracts/bridge_protocol.md:142:carrying a valid `claude-codex-report/v1` body is exempt from the trailer.
docs/contracts/bridge_protocol.md:710:6. Require a `bridge-report/v1` return envelope.
docs/contracts/bridge_protocol.md:865:- `scripts/codex-bridge` + `scripts/codex-app-bridge.mjs`: audited
docs/contracts/bridge_protocol.md:871:- `scripts/codex-bridge`: audited tracked CLI bridge
docs/contracts/bridge_protocol.md:890:- `~/.local/bin/codex-run-v3` when installed

exec
/bin/zsh -lc "sed -n '290,345p' docs/orchestration.md | nl -ba -v290; sed -n '845,900p' docs/contracts/bridge_protocol.md | nl -ba -v845; sed -n '680,735p' docs/contracts/bridge_protocol.md | nl -ba -v680" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   290	Four checkpointed streams resumed, completed, and landed as four PRs:
   291	the integrity/provenance overhaul (all 31 audit-pinned defects fixed;
   292	strict validation now re-derives the power trace from raw evidence),
   293	the docs package, the KV-cache replay feasibility verdict, and the
   294	complete fixture-first NVIDIA stack. The layered review recorded, among
   295	~30 attributed catches: two blockers found only by fresh-instance
   296	lenses (a provenance hash that did not prove the actual generation
   297	input; a strict-gate bypass via mutable metadata), two pinned wire
   298	contracts overturned before hardware contact, one fabricated-evidence
   299	defect caught only at the lead's diff gate, two integration defects
   300	caught only by the post-merge integration review, and a crash path
   301	caught only by the final-head rule on the last commit of the night.
   302	Suite: 415 → 546 tests, zero expected failures. Roughly two dozen
   303	delegated Codex sessions; the lead never wrote implementation code and
   304	never skipped a gate.
   305	
   306	## Reconstructing the loop on a clean machine
   307	
   308	Pointer map only; mechanics stay in their owning files.
   309	
   310	- Committed invocation wrapper: `scripts/codex-run`.
   311	  Usage: `codex-run <out.md> [--timeout SEC] [-C DIR] [-s SANDBOX] [--resume] '<prompt>'`.
   312	  It writes `<out>.status`.
   313	- Project bridge: `scripts/codex-bridge`; writes prompt snapshots,
   314	  response snapshots, logs, status files, and
   315	  `.codex-bridge/invocation_manifest.jsonl` rows with prompt/output/log
   316	  hashes.
   317	- Workspace-write bridge ceremony: `scripts/bridge session-open` and
   318	  `session-close`; the reduced discussion header, tolerant return envelope,
   319	  receipt anchoring, and recovery primitives are defined only in
   320	  `docs/contracts/bridge_protocol.md` (`bridge-protocol/v1.1`).
   321	- Skill-only mechanics on the operator's machine live under
   322	  `~/.claude/skills`: `operation-loop` is the conductor,
   323	  `codex-delegation` is the invocation/consumption contract,
   324	  `adversarial-review` defines refutation tiers,
   325	  `multi-stream-worktrees` defines parallel stream mechanics,
   326	  `consistency-sweep` owns drift control, and `council` owns
   327	  triggers/roles.
   328	- Repo-derivable on a clean clone: this file gives the loop shape;
   329	  council log C-009/C-010 give topology and gates; the claims and
   330	  analysis-plans contracts give claim gating; `docs/stream_logs/` and
   331	  `docs/run_reports/` provide live templates for ledgers and trace
   332	  appendices; `scripts/codex-run` and `scripts/codex-bridge` provide
   333	  execution entry points.
   334	- Skill-only: exact conductor sequencing, delegated-agent prompt/consumption
   335	  contract, severity-tiered refuter recipes, multi-worktree stream
   336	  operations, and consistency-sweep checklists.
   337	
   338	## Where to read the evidence
   339	
   340	- Yield tables and calibration aggregates: the latest run reports
   341	  (`docs/run_reports/2026-07-07-resume-merge-session.md` and
   342	  `...checkpoint-multistream-session.md`).
   343	- Deliberations and consensus texts: `docs/council_log.md` (C-007
   344	  design council; C-009 topology consensus; C-010 validation).
   345	- The binding rules themselves: `docs/decision_log.md`.
   845	  "consumers": {
   846	    "CLAUDE.md": ["scope_authority", "quiet_mac", "no_bypass", "one_hop", "envelope_failure"],
   847	    "AGENTS.md": ["scope_authority", "quiet_mac", "no_bypass", "one_hop", "envelope_failure"],
   848	    ".claude/agents/codex.md": ["scope_authority", "quiet_mac", "no_bypass", "one_hop", "envelope_failure"],
   849	    ".claude/commands/codex.md": ["scope_authority", "quiet_mac", "no_bypass", "one_hop", "envelope_failure"],
   850	    ".claude/skills/codex/SKILL.md": ["scope_authority", "quiet_mac", "no_bypass", "one_hop", "envelope_failure"]
   851	  }
   852	}
   853	```
   854	<!-- END BRIDGE CONSUMER DRIFT MANIFEST -->
   855	
   856	Authoritative contract:
   857	
   858	- `docs/contracts/bridge_protocol.md`
   859	
   860	Tracked implementation:
   861	
   862	- `scripts/bridge`: session wrappers, leases, baseline manifests, scope checks,
   863	  and thread registry
   864	- `.codex-bridge/receipts/`: immutable local session-open receipts
   865	- `scripts/codex-bridge` + `scripts/codex-app-bridge.mjs`: audited
   866	  Claude-to-Sol script route and optional desktop-owned turn transport; the
   867	  latter is what gives the native pet real running-conversation state
   868	- `scripts/claude-bridge-mcp.mjs`: guarded reverse consult
   869	- `.mcp.json`: Claude-to-Codex server configuration
   870	- `.codex/config.toml`: Codex-to-Fable server registration
   871	- `scripts/codex-bridge`: audited tracked CLI bridge
   872	- `tests/test_bridge.py`: focused bridge state and scope tests
   873	- `tests/test_claude_bridge_mcp.py`: reverse-adapter tests
   874	
   875	Claude-side consumers:
   876	
   877	- `.claude/skills/codex/SKILL.md`
   878	- `.claude/agents/codex.md`
   879	- `.claude/commands/codex.md`
   880	- `CLAUDE.md`
   881	
   882	Codex-side consumers:
   883	
   884	- `AGENTS.md`
   885	- `.agents/skills/claude-consult/SKILL.md`
   886	
   887	Orchestration and audited-wrapper consumers:
   888	
   889	- `docs/orchestration.md`
   890	- `~/.local/bin/codex-run-v3` when installed
   891	
   892	Repository-local pointers SHOULD summarize and link this contract rather than
   893	duplicate its normative rules.
   680	The caller's prompt MUST begin with:
   681	
   682	```text
   683	BRIDGE_ORIGIN: codex
   684	BRIDGE_HOPS_REMAINING: 0
   685	```
   686	
   687	The request MUST provide:
   688	
   689	- `Decision question`
   690	- `Current Sol position`
   691	- `Alternatives`
   692	- `Evaluation criteria`
   693	- `Settled constraints`
   694	- `Authority order`
   695	- `Repository pointers`
   696	- `Requested counterargument`
   697	- `Requested output shape`
   698	
   699	Large repository context SHOULD be supplied as exact file pointers because
   700	Fable has read/search access.
   701	
   702	The adapter MUST:
   703	
   704	1. Validate the caller-supplied bridge headers.
   705	2. Reject a Claude-originated or nonzero-hop request.
   706	3. Strip the caller headers.
   707	4. Inject one canonical header and the read-only peer role.
   708	5. Launch Fable with the configured read-only, no-MCP, no-persistence
   709	   boundary.
   710	6. Require a `bridge-report/v1` return envelope.
   711	
   712	The adapter MUST NOT pass duplicate origin headers to Fable.
   713	
   714	The tool input MAY include `effort`, whose only accepted values are `high` and
   715	`xhigh`. Unsupported values are rejected with a synthesized `FAILED`
   716	`protocol_failure` envelope and are never silently coerced; `ultra` is not
   717	exposed. The process default comes from `CLAUDE_BRIDGE_EFFORT` only when that
   718	environment value is `high` or `xhigh`; every other value falls back to
   719	`high`. The effective default remains `high` to bound latency under the tool
   720	timeout.
   721	
   722	For reproducibility, the adapter MUST pass the selected effort explicitly and
   723	prefix returned child-result text with `[consult effort: <effort>]` as its
   724	first line. This prefix precedes the child output; the envelope-final rule
   725	still binds the end of the combined text.
   726	
   727	The consult remains one-shot because persistence would weaken independence,
   728	invite bridge recursion, and blur decision ownership. Fable provides advice;
   729	the top-level Codex caller adjudicates and verifies it.
   730	
   731	Transport or protocol failure MUST return or synthesize `status: FAILED`; it
   732	MUST NOT be consumed as peer approval.
   733	
   734	A successful one-shot consult may end only `DISCUSSION` or `NEEDS_RULING`.
   735	Any other well-formed child status is a protocol deviation: the adapter strips

exec
/bin/zsh -lc "SNAP=/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot; rg -n -i 'physics|causality|positive.control|negative.verdict|mutation|unswept|packet hygiene|quote.*period|census|line-number|git grep|scope.*foreign|cross-thread|quiet.*stream|zero streaming|streaming.*idle|same-signature|consult.*round|round three|round 3|work-chunk' \""'$SNAP" --glob '"'*.md'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:44:  stop-loss (two consecutive same-signature failures → stop, write the handoff,
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:382:MUTATION: <read-only|workspace-write>; commit=<yes|no>; external=<yes|no>
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:420:- Mutation/commit/external-action authority.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:181:- codex-delegation: FIRST full Workflow-tool orchestration (46 agents, zero stalls, zero errors) — the sanctioned Workflow alternative scales to implement→lens→refute shapes, and its codex WRAPPER agents can git commit+push in worktrees (they are full agents), beating direct codex-run for worktree streams where codex's own sandbox still index.lock-blocks; refuter layer killed 10/30 findings pre-triage (precision working); mutation testing appeared organically in a test-audit lens (5 mutations proving gaps) — fold candidate for §Test doctrine: "test-audit lenses may be prompted to MUTATION-TEST the gates they audit"; FIX-N one-shot record now 22/22; NEVER batch multiple codex-run launches in one zsh for-loop (parse-error launch failure, second occurrence class).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:202:- Session second half: adapter v1 adopted + codex-run-v3/codex-usage built+installed (runner-injected report contracts); scope-restraint 3-layer design (language live, backstop in flight at pause); NEEDS_RULING generalized early-return; design-consult-by-default doctrine (P2-044 first product: corpus-grounded HAC design, 47x variance underestimate found); PRs #49/#54 merged, #50-#53/#55 held; P2-037 second transport-OK/no-report incident (independent audit pattern instead of self-grading resume). Usage data: 1 ultra = 35.3M tokens ≈ 11 xhigh sessions; Fable generation ~1.8M vs Sol ~112M same arc. Paused at C-028 checkpoint #4 (25a8b05).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:218:- NEW LESSON (fold candidate, not yet folded — audit may reshape it): cross-thread collisions in one working tree are now real (Ed runs concurrent threads); the two-writer rule needs a cross-THREAD corollary — before any commit, diff-inventory the tree for foreign changes and verify provenance with the user rather than pathspec-committing around unexplained diffs blindly.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:222:- operation-loop: §0 deliverable sentence; §1 single contract-bearing stream (worktrees SKIPPED correctly); §3 default assignments (design consult xhigh MCP, impl xhigh CLI, fix3 dropped to high when triggers lapsed — first non-xhigh round, correct); §4 full pipeline incl. STRENGTHENED design round (lead's spec itself consulted pre-implementation — Sol amended 5 pins and caught a v1 adapter bug; the pre-decision-consult default earned its keep); §5 lead gates (live wrapper dogfood, live reverse consults, flake triage: lead-rerun caught an agent-load flake the worker's green run masked); §8 bookkeeping (run report + C-032 row + D-065 + D-064 tracked manifest — first session to create docs/process_traces/); §9 folds done mid-session (codex-delegation +2 field notes). §6 SKIPPED (single stream), §10 not fired (single-PR).
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:242:- adversarial-review: delta re-audits caught fix-round blockers twice more (9th/10th data); anti-gaming lenses on BOTH positive (AXI-SB) and negative (AXI-SC) verdicts — negative-verdict honesty (positive-control path) is a new lens angle worth folding.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:245:- 2026-07-17 (JouleWise, screensaver-contamination session): codex skill §Effort selection + §Primary MCP path (consult xhigh discussion-lane, impl xhigh workspace-write; MCP idle-timeout killed impl mid-turn → recovered via §Session observability rollout discovery + codex-bridge resume — recipe worked as written). bridge session-open/close ceremony used; gotcha: --paths defaults to exact match, need explicit `path:subtree`, and a FAILED close retains the lease (needed lease-release). adversarial-review shape started (lenses split lead/Sol) but checkpoint-stopped mid-round; resume in RUN_STATE. Validation: lead live-probe verification caught a fixture-matched-the-bug parser defect Sol's green tests missed — rule 1 earns its keep again.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:251:- 2026-07-19 (JouleWise, extended quiet window): codex-delegation §MCP-route — two Sol sessions (read-only recompute audit AUDIT_PASS; workspace-write scoped status-page split, NEEDS_SCOPE honored, 20/20 module tests) — worked well, MCP background tasking clean; adversarial-review §severity-tiering applied lightly (exploratory readout → single recompute lens, precedent 3-lens reserved for front-facing promotions); multi-stream-worktrees NOT used (single [QUIET-MAC] lane); operation-loop §bookkeeping (run report + RUN_STATE + PROJECT_STATUS + DRIFT + memory). Field note: detached nohup chain + watcher-Bash re-invocation is the right shape for multi-hour measurement; guard-abort → same-root resume (runner skips complete bundles) avoided any data loss from an operator return.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:252:- 2026-07-19 (JouleWise, D-078 arc) LENS DOCTRINE UPDATE for adversarial-review: on MEASUREMENT code/data, a physics/causality lens (energy vs event timeline, power*duration plausibility, clock-domain checks) catches what recomputation lenses structurally cannot — three Sol recompute audits reproduced every number to 1e-13 while the instrument was misattributing 8 J windows; one causality-framed audit found it immediately. Ed-confirmed: physics lenses on measurements are more useful than recalculation ones. Default review panel for anything measurement-adjacent: contract + execution + PHYSICS (mandatory) + cross-model; recompute alone is never sufficient sign-off. Also: spend Sol xhigh on ONE deep adversarial whole-artifact pass per round (fresh thread each round, no anchoring), fan Fable across distinct lenses for parallelism.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:274:- council §cold-gate (rule-11): mandatory trigger honoured (2 same-signature failures → consult, not round 3). Cold Fable + Opus contract refuter pairing exercise #4; refuter caught that the magistrate's OWN ruling (R2 invoked-only) was the QA-10B defect; synthesis = D-088. The pairing's cross-model diversity clause is now 2-for-4 on findings against the adjudicator.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:297:- operation-loop/§window custody (project runbook §5B/§8/§10/§11/§12): three §10 continuations + salvage close executed solo; recorder-then-verdict order held; NEW hazard for the skill docs: operating-session OUTPUT STREAMING during idle gates caused failure #3 — candidate amendment for the council/operation-loop measurement-discipline sections ("zero tool calls" -> "zero tool calls AND zero streaming; one-line arm messages").
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:298:- Escalation trigger (CLAUDE.local rule 11): fired twice (§5B same-signature aborts -> consult; slot same-signature failures -> salvage close). Both stops honored without magistrate override.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:302:- codex-delegation: 3 Sol xhigh sessions via the codex subagent (read-only adjudication audit; read-only commit-3 design consult; workspace-write commit-3 implementation w/ 6-path WRITE_SCOPE). Consumed as final reports only. Effort-tier §: xhigh triggers held (adversarial review, design-bearing, cross-contract). Field note: audit line-number citations drifted (R14, substance held) — consider requiring `git grep -n` verification snippets in audit briefs.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:304:- council (rule-11 cold gate §): FULL shape exercised: cold Fable ruling → bounded factual follow-up (custody sweep contradicted a drafted license line; instance re-drew on the merits) → independent Opus refutation (14 findings) → magistrate synthesis (D-100). NEW pattern worth folding into the skill: the packet's "deferred residual" (condition 4 custody sweep) caught the ruling's disk-shape miscalibration — mechanically-assembled packets should list UNSWEPT evidence explicitly so rulings defer rather than assume; and R5a-style "real-shape regression outranks prose" is a strong convergence device.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:315:- codex-delegation §escalation + §effort-tiers: heavy use. Three parallel Sol streams (D100-BII, MINT-GENERALIZE, CAL-BRACKET) each run impl→audit→fix→delta as separate xhigh sessions; consumed via envelope + git diff only. KEY DISCIPLINE WIN: on CAL-BRACKET's REPEAT-signature delta failure, ran a read-only design CONSULT (scout genre) instead of a blind round three — the "consult not round three" rule caught that F3 was decision-level (D-102 silent on the trigger mechanism), not a bench fix.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:319:- PACKET HYGIENE (self-correction): the refuter recorded 4 hygiene findings against my gate-3 packet (selective clause quotation; flags not quoted in full incl. the blocking anti-round-3 one; a laundered over-refusal number; wrong-population census). Adopted the standing correction: quote governing clauses to the period; quote every source flag in full including ones cutting against my proposed disposition; census the license-surface population, never a convenient superset. Same class D-106/D-107 already flagged — this recurs, watch for it.
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:360:- council §escalation-trigger: fired twice on same-signature count 2 (CGV
/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:361:  F3 third formulation; QG census class) — both routed to consults, not

exec
/bin/zsh -lc 'for p in /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-adapter-design.md /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-merge-review.md /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/c028-invocations.jsonl /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-p2038-flake.md /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-p2041-triage.md /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-status-refresh.md /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-ci002.md; do if test -e "$p"; then echo "PRESENT $p"; else echo "MISSING $p"; fi; done; test -e docs/reviews/2026-07-11-scope-restraint-consult.md && echo scope_consult_present || echo scope_consult_missing; test -e ~/.local/bin/codex-run-v3.bak-20260718 && echo backup_present || echo backup_missing' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
MISSING /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-adapter-design.md
MISSING /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-merge-review.md
MISSING /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/c028-invocations.jsonl
MISSING /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-p2038-flake.md
MISSING /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-p2041-triage.md
MISSING /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-status-refresh.md
MISSING /private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-ci002.md
scope_consult_present
backup_present

exec
/bin/zsh -lc "sed -n '332,350p' RUN_STATE.md | nl -ba -v332; rg -n 'service.tier|CODEX_SERVICE_TIER' ~/.local/bin/codex-run-v3 ~/.local/bin/codex-run ~/.local/bin/codex-run-v2 2>/dev/null || true" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   332	  30, eight further to trigger). **B2 (no deterministic bootstrap
   333	  contract) — design+implement session IN FLIGHT** on
   334	  impl/ledger-bootstrap (xhigh; genesis-only, atomic, import-marked
   335	  receipts, dry-run default; expected head `8e80b6e9…` under the
   336	  report's rules). Verification record custodied:
   337	  process_traces/2026-08-05-d079-issuance/. Issuance itself (execute +
   338	  head-pin commit + artifact edit + D-116 entry) remains a separately
   339	  gated step — Ed pre-authorized overnight, conditional on the gate.
   340	- **Fast-tier**: PR #102 open, CI running; lead-replayed 70/70 incl.
   341	  desktop IPC tests; solo-review ruled proportional (Ed-dictated
   342	  20-line diff). On merge: fast rides scripts/codex-bridge
   343	  (codex-run-v3 does not read CODEX_SERVICE_TIER — do not modify Ed's
   344	  personal wrapper without his word).
   345	
   346	### D-079 ISSUANCE HELD by cold gate (recorded ~03:30 2026-08-06) — issuance is IMPLEMENTATION, not an edit
   347	
   348	Rule-11 cold gate on the irreversible issuance SPLIT: fresh Fable
   349	instance PROCEED (ledger/head/disposition all verified correct — head
   350	`08456d50…@76` independently reproduced, B1 ruling confirmed vs D-102);

exec
/bin/zsh -lc "sed -n '169,369p' /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md | nl -ba -v169" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   169	## A. Report contract
   170	
   171	The first nonblank content must be exactly one fenced JSON object. No introductory prose and no YAML.
   172	
   173	```json
   174	{
   175	  "schema": "claude-codex-report/v1",
   176	  "genre": "implementation",
   177	  "status": "blocked",
   178	  "completion": "complete",
   179	  "summary": "CI-002 implemented; package build/install awaits lead-side CI.",
   180	  "workspace": {
   181	    "base_requested": "f4fd36e",
   182	    "base_mode": "exact",
   183	    "head_start": "f4fd36e",
   184	    "head_end": "f4fd36e",
   185	    "upstream_end": "a1025a2",
   186	    "branch": "impl/ci002"
   187	  },
   188	  "pathspec": [
   189	    ".github/workflows/ci.yml",
   190	    "pyproject.toml",
   191	    "docs/run_reports/2026-07-11-ci002-packaging-strictness.md",
   192	    "RUN_STATE.md",
   193	    "TASK_QUEUE.md"
   194	  ],
   195	  "unowned_dirty": [],
   196	  "verdict": {
   197	    "implementation": "implemented",
   198	    "acceptance": "pending_verification"
   199	  },
   200	  "verification": [
   201	    {
   202	      "id": "V1",
   203	      "kind": "suite",
   204	      "cmd": "python3 -m unittest discover -s tests",
   205	      "cwd": ".",
   206	      "observed": {
   207	        "result": "pass",
   208	        "exit_code": 0,
   209	        "tail": [
   210	          "Ran 1041 tests in 69.067s",
   211	          "OK (skipped=13)"
   212	        ]
   213	      },
   214	      "expected": {
   215	        "exit_code": 0,
   216	        "tail_regex": "OK( \\(skipped=[0-9]+\\))?$"
   217	      }
   218	    },
   219	    {
   220	      "id": "V2",
   221	      "kind": "build",
   222	      "cmd": "python3 -m build",
   223	      "cwd": ".",
   224	      "observed": {
   225	        "result": "not_run",
   226	        "exit_code": null,
   227	        "tail": []
   228	      },
   229	      "expected": {
   230	        "exit_code": 0,
   231	        "tail_regex": "Successfully built"
   232	      }
   233	    }
   234	  ],
   235	  "flags": [
   236	    {
   237	      "id": "F1",
   238	      "kind": "verification_gap",
   239	      "level": "blocking",
   240	      "text": "The sandbox lacks the build frontend; distribution creation and installed-wheel smoke remain unverified.",
   241	      "needs": "Lead must require green CI build and wheel-install jobs before acceptance."
   242	    }
   243	  ]
   244	}
   245	```
   246	
   247	I recommend one `verification` array rather than separate `tests` and `replay_cmds`. Splitting them duplicates commands and creates a new drift opportunity. Each entry already contains the replayable command, exact observed tail, and timing-insensitive expected result.
   248	
   249	### Core semantics
   250	
   251	`status`:
   252	
   253	- `clean`: requested outcome complete, required in-session checks pass, no unresolved blocking flag.
   254	- `findings`: usable outcome delivered, with actionable findings or nonblocking uncertainty.
   255	- `blocked`: acceptance or completion requires unavailable authority, input, environment, or verification.
   256	
   257	`completion` is separate:
   258	
   259	- `complete`
   260	- `partial`
   261	- `none`
   262	
   263	That separation matters for CI-002: the implementation may be complete while acceptance is blocked.
   264	
   265	`pathspec` must mean only: repository-relative paths whose current modifications belong to this session and may be passed verbatim to `git add --`. It must not include merely inspected files. Read-only tasks return `[]`.
   266	
   267	`unowned_dirty` records pre-existing or concurrent modifications. A nonempty value prevents automatic staging even when `pathspec` is populated.
   268	
   269	`flags.kind`:
   270	
   271	- `lead_ruling`
   272	- `verification_gap`
   273	- `baseline_drift`
   274	- `scope_deviation`
   275	- `environment`
   276	- `residual_risk`
   277	
   278	`flags.level` is only `blocking` or `nonblocking`. Do not reuse review severity here.
   279	
   280	### Genre vocabularies
   281	
   282	| Genre | Stable verdict vocabulary |
   283	|---|---|
   284	| Review | Finding severity: `blocker`, `should_fix`, `nit` |
   285	| Implementation | `implementation`: `implemented`, `partial`, `no_change`; `acceptance`: `ready`, `pending_verification`, `needs_ruling` |
   286	| Triage | Per region: `apply`, `preserve`, `compose`, `ruling` |
   287	| Root cause | `cause`: `confirmed`, `probable`, `unresolved`; `remediation`: `fixed`, `proposed`, `none` |
   288	| Scout | Per row: `start_now`, `wait_for`, `needs_ruling`, `do_not_start` |
   289	
   290	Retire A/B/C triage labels. They are locally compact but semantically opaque. Today’s mapping becomes:
   291	
   292	- A → `apply`
   293	- B → `preserve`
   294	- A+B → `compose`
   295	- C → `ruling`
   296	
   297	I would also retire `AFTER-BOOKKEEPING` as a scout verdict. It hides the actual dependency. In today’s scout, P2-047 is waiting for real floor evidence, while P2-048 is waiting for the P1-003 meter decision—not “bookkeeping” ([matrix](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/sol-hardening-scout.md:10)). Encode the concrete IDs under `wait_for`.
   298	
   299	### Prose templates
   300	
   301	The JSON block is followed only by applicable sections:
   302	
   303	**Review**
   304	
   305	```markdown
   306	## Findings
   307	Ordered blocker → should_fix → nit. IDs must match verdict.findings.
   308	
   309	## Residual risk
   310	Only coverage limitations not already represented as findings.
   311	```
   312	
   313	**Implementation**
   314	
   315	```markdown
   316	## Change
   317	What changed and why, without repeating pathspec.
   318	
   319	## Verification notes
   320	Only failures, deviations, or interpretation; do not repeat clean tails.
   321	
   322	## Residual risk
   323	Omit when empty.
   324	```
   325	
   326	**Triage**
   327	
   328	```markdown
   329	## Decision matrix
   330	Region | disposition | evidence | exact action
   331	
   332	## Composition recipe
   333	Ordered mechanical reconstruction steps.
   334	
   335	## Rulings
   336	Only unresolved items, keyed to flag IDs.
   337	```
   338	
   339	**Root cause**
   340	
   341	```markdown
   342	## Causal chain
   343	Shortest evidence-backed chain from trigger to symptom.
   344	
   345	## Remediation
   346	Why the fix closes that chain.
   347	
   348	## Disproved alternatives
   349	Only serious competing hypotheses.
   350	
   351	## Residual risk
   352	Omit when empty.
   353	```
   354	
   355	**Scout**
   356	
   357	```markdown
   358	## Scheduling matrix
   359	Row | action | wait_for | collision surface
   360	
   361	## Critical path
   362	Only cross-row dependencies.
   363	
   364	## Delegation contracts
   365	Include only when explicitly requested.
   366	```
   367	
   368	The extensive “timing-sensitive inputs traced” section in the flake report was useful forensic work, but it should be task-specific acceptance—not a root-cause invariant.
   369	

exec
/bin/zsh -lc "test -f .claude/skills/codex/SKILL.md && { rg -n 'codex-run|codex-bridge|service.?tier|CODEX_SERVICE_TIER|effort|gpt-5\\.[56]|BRIDGE_TASK_V1' .claude/skills/codex/SKILL.md; } || echo missing_claude_codex_skill; test -f .claude/agents/codex.md && rg -n 'codex-run|codex-bridge|gpt-5\\.[56]|BRIDGE_TASK_V1' .claude/agents/codex.md || true" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
3:description: Run OpenAI Codex gpt-5.6-sol inside Claude Code with difficulty-matched effort and JouleWise bridge safety.
26:A standing Ed effort directive controls over a ruled gate composition's
52:   `scripts/codex-bridge new` or `scripts/codex-bridge review`. For MCP, call
54:   Git-root `cwd`, model `gpt-5.6-sol`, config
55:   `{"model_reasoning_effort":"<selected-effort>","mcp_servers":{"claude":{"enabled":false}}}`,
58:   Fast Mode is per-call opt-in only: add `CODEX_SERVICE_TIER=fast` to a
59:   `scripts/codex-bridge` invocation when Ed chooses the faster service tier,
60:   for example `CODEX_SERVICE_TIER=fast scripts/codex-bridge new ...`. Omit it
89:The project `.mcp.json` pins `gpt-5.6-sol` with `high` only as a safe fallback
95:For D-050/D-064 runs, prefer `~/.local/bin/codex-run-v3` with model, selected
96:effort, genre, and exhaustive write scope. If it is unavailable, use
97:`scripts/codex-bridge` only for a substantial background or parallel Sol round
106:machine, `.codex-bridge/app-host-thread-id` selects a dedicated app-owned task;
107:`scripts/codex-bridge` uses `scripts/codex-app-bridge.mjs` to start the real Sol
119:`.codex-bridge/` audit trail (this replaced the deleted `scripts/codex-watch`;
123:- Discover RUNNING sessions: `ls -lt .codex-bridge/*.log` — the log exists
127:- Discover finished sessions: `ls -lt .codex-bridge/*.status` (one
129:  `.codex-bridge/invocation_manifest.jsonl` rows.
130:- Follow live: `tail -f .codex-bridge/<run-id>.log` (the full tee'd stream).
131:- Final message: `.codex-bridge/responses/<run-id>.response.md`, mirrored to
132:  `.codex-bridge/last-message.md`.
3:description: Start or continue a full OpenAI Codex gpt-5.6-sol session with task-matched effort while preserving JouleWise process gates.

exec
/bin/zsh -lc "sed -n '40,104p' .claude/skills/codex/SKILL.md | nl -ba -v40" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
    40	sequence, not the contract.
    41	
    42	Apply contract §4's t3 applicability and preferred-presentation-plane rule.
    43	
    44	1. Read root `AGENTS.md`; run Mission M0 for substantial work.
    45	2. Choose the transport and apply the tracked-subagent limits, pilot record,
    46	   and accounting rule by reference to contract §4.
    47	3. Build the applicable contract §1 header. For writes, open the session with
    48	   `scripts/bridge session-open` and use its returned header fragment.
    49	4. For a substantial background or parallel Sol round that needs
    50	   operator-visible lifecycle state, use the preferred background route: set
    51	   `CODEX_REASONING_EFFORT` to the selected tier and call
    52	   `scripts/codex-bridge new` or `scripts/codex-bridge review`. For MCP, call
    53	   project tool `codex` with the
    54	   Git-root `cwd`, model `gpt-5.6-sol`, config
    55	   `{"model_reasoning_effort":"<selected-effort>","mcp_servers":{"claude":{"enabled":false}}}`,
    56	   `on-request` approvals, and the narrowest sandbox. Put the contract's origin
    57	   and hop headers in developer instructions or the bridge prompt.
    58	   Fast Mode is per-call opt-in only: add `CODEX_SERVICE_TIER=fast` to a
    59	   `scripts/codex-bridge` invocation when Ed chooses the faster service tier,
    60	   for example `CODEX_SERVICE_TIER=fast scripts/codex-bridge new ...`. Omit it
    61	   to retain `default`; never make Fast Mode a standing default because it
    62	   consumes roughly 2.5x credits.
    63	5. Validate the return under contract §2. Handle early returns and routing
    64	   changes under §§3-4 on the thread required by §5.
    65	6. After writes, run `scripts/bridge session-close` as specified by contract
    66	   §6. Keep primitives for recovery or adjudicated overrides.
    67	7. Inspect every diff, replay the required lead checks, and adjudicate the
    68	   worker's result. The lead owns final verification.
    69	
    70	At the next t3-mediated session after the 2026-08-03 doctrine gate, capture the
    71	owed Full-access mapping amendment exhibit before citing any UI-to-flag mapping
    72	as evidence. Bind one observation to the t3 and CLI versions, selected UI mode,
    73	timestamp, full child argv, and a process-table record containing PID, start
    74	time, and ancestry; store the capture at a tracked process-trace location. The
    75	contract §4 prohibition already binds independently of this exhibit. Apply
    76	contract §4's approval-evidence rules.
    77	
    78	These enforcement boundaries remain explicit:
    79	
    80	- `WRITE_SCOPE` is exhaustive; never infer additional scope from tests, generated files, repository instructions, or work believed necessary for completion.
    81	- Never start or continue a `[QUIET-MAC]` measurement while an agent session is active.
    82	- Never use `danger-full-access` or sandbox/approval bypass flags.
    83	- Bridge depth is one hop: a Claude-originated Sol session must not call Claude by MCP, `claude -p`, or any other launcher.
    84	- A missing, duplicated, malformed, or non-final required envelope is protocol failure, never success.
    85	
    86	Reverse-consult operation is documented by contract §8 and
    87	`.agents/skills/claude-consult/SKILL.md`.
    88	
    89	The project `.mcp.json` pins `gpt-5.6-sol` with `high` only as a safe fallback
    90	and disables the reverse Claude server for every Claude-originated session;
    91	explicit per-task selection remains mandatory.
    92	
    93	## Audited path
    94	
    95	For D-050/D-064 runs, prefer `~/.local/bin/codex-run-v3` with model, selected
    96	effort, genre, and exhaustive write scope. If it is unavailable, use
    97	`scripts/codex-bridge` only for a substantial background or parallel Sol round
    98	that needs operator-visible lifecycle state; set `CODEX_REASONING_EFFORT` to
    99	the selected tier. Otherwise return to contract §4 and select the matching
   100	foreground route.
   101	
   102	## Session observability + recovery (WO-027)
   103	
   104	The native Codex pet does not consume the external observer JSONL. It follows

codex
# Skill-stack drift audit

Scope: read-only review of all six snapshot skills, `codex-delegation/ADAPTER.md`, and `skill-usage-log.md`, checked against the current bridge contract and repository orchestration sources. No files changed.

## Executive verdict

The stack has four release-blocking doctrine conflicts:

1. It teaches mutually incompatible Codex transports and wake guarantees.
2. It retains the D-061-superseded automatic review-layer drop rule.
3. It splits prompt-contract authority between the legacy adapter and bridge v1.1.
4. It both requires and forbids commits from Codex worktree sessions.

Fast Mode is absent from every snapshot skill. It appears only in the usage log, where its per-call-only formulation is correct. The current implementation supports it only through `scripts/codex-bridge`, not `codex-run-v3`.

## Ranked findings

### 1. Critical — transport and wake doctrine is self-contradictory

- [`codex-delegation/SKILL.md:21`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:21>) declares legacy `codex-run` the “ONE stable mechanism.”
- [`codex-delegation/SKILL.md:24`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:24>)–37 says its background exit guarantees a wake.
- [`codex-delegation/SKILL.md:379`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:379>) instead requires `codex-run-v3` for every new invocation.
- [`codex-delegation/SKILL.md:566`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:566>) records five incidents proving the wake guarantee false under Claude background tasks and mandates tracked polling.
- [`multi-stream-worktrees/SKILL.md:92`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:92>) still says background-and-end-turn is correct.
- [`adversarial-review/SKILL.md:19`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:19>) prescribes bare `codex exec`, directly forbidden at [`codex-delegation/SKILL.md:67`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:67>).

All three wrappers still exist, so this is not binary disappearance; it is routing drift. Current doctrine distinguishes `scripts/codex-bridge` for tracked background/parallel work from `codex-run-v3` for D-050/D-064 audited runs: [repo Codex skill:49](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/.claude/skills/codex/SKILL.md:49>), [repo Codex skill:93](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/.claude/skills/codex/SKILL.md:93>).

### 2. Critical — D-061’s superseded auto-drop rule remains operative

- [`operation-loop/SKILL.md:343`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:343>) makes two zero-catch sessions a drop-candidacy trigger.
- [`council/SKILL.md:82`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:82>) applies the same two-session rule to rotating lenses.
- [`council/SKILL.md:160`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:160>) repeats it again, with a grammatically missing subject.
- [`codex-delegation/SKILL.md:325`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:325>) retains a generic catch-rate drop rule.

D-061 explicitly replaced that policy with predeclared applicability, four outcome classes, fixed severity weights, and an expected-loss review after three applicable exposures—never automatic deletion: [decision log:3209](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/decision_log.md:3209>).

### 3. Critical — two documents claim to own incompatible prompt contracts

- [`ADAPTER.md:5`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:5>) calls itself the “ONE home.”
- [`ADAPTER.md:67`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:67>) and [`ADAPTER.md:376`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:376>) prescribe the legacy flat `ADAPTER:/GENRE:/WRITE_SCOPE:` prompt.
- Current bridge v1.1 requires delegated prompts to begin with `BRIDGE_TASK_V1` JSON: [bridge protocol:29](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/contracts/bridge_protocol.md:29>).
- The usage log repeatedly records launch failures caused by this ambiguity: [`skill-usage-log.md:282`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:282>), [`:311`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:311>), [`:329`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:329>).

The adapter remains valid as the full CLI report schema, but it must point to bridge v1.1 for launch/scope authority instead of presenting a competing prompt contract.

### 4. High — worktree sessions are simultaneously told to commit and not commit

- [`multi-stream-worktrees/SKILL.md:90`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:90>) requires atomic commits.
- [`multi-stream-worktrees/SKILL.md:118`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:118>) tells streams to commit during stop handling.
- [`multi-stream-worktrees/SKILL.md:168`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:168>) and [`codex-delegation/SKILL.md:91`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:91>) correctly say direct Codex cannot write linked-worktree Git metadata and the lead must commit.
- The failure recurs in the log at [`:28`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:28>), [`:291`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:291>), [`:305`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:305>), and [`:328`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:328>).

This is a candidate for wording repair, not relaxing the no-commit rule.

### 5. High — refuter defaults drifted apart

- [`adversarial-review/SKILL.md:28`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:28>) says fresh Codex refuters are the default and Opus is no longer default.
- [`adversarial-review/SKILL.md:146`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:146>) later makes Opus-contract + Sol-execution the default blocker pair.
- Panel size also differs: 2–4 lenses at [`adversarial-review/SKILL.md:22`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:22>) versus 2–3 at [`operation-loop/SKILL.md:217`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:217>) and [`multi-stream-worktrees/SKILL.md:98`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:98>).

The C-033 cross-model pair is the later rule; earlier operative wording should become dated history or a pointer.

### 6. High — fresh-eyes cadence is documented but demonstrably did not fire

- Both skills consistently say “every 10 delegated invocations plus phase boundaries”: [`council/SKILL.md:40`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:40>) and [`operation-loop/SKILL.md:24`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:24>).
- The log records roughly 16 invocations without a sweep: [`skill-usage-log.md:266`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:266>).
- It later validates concurrent read-only auditing but does not fold it in: [`skill-usage-log.md:341`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:341>).
- Ed’s latest ruling changes the intended shape to work-chunk-anchored with a mechanical backstop, pending formal D-080 amendment: [RUN_STATE:922](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/RUN_STATE.md:922>).

So there is no internal numeric disagreement, but the shared number is operationally stale and its provisional recalibration never happened.

### 7. High — Fast Mode is missing from the skills

Only [`skill-usage-log.md:348`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:348>) records it:

> per-call `CODEX_SERVICE_TIER=fast` via `scripts/codex-bridge` only

That is consistent with the per-call-only doctrine. The omission matters because the snapshot’s preferred `codex-run-v3` route does not read `CODEX_SERVICE_TIER`: [RUN_STATE:340](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/RUN_STATE.md:340>). The current repo-local skill has the correct rule at [`.claude/skills/codex/SKILL.md:58`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/.claude/skills/codex/SKILL.md:58>).

### 8. Medium — operative 5.5-era labels survived the Sol migration

Stale operative labels remain at:

- [`operation-loop/SKILL.md:140`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:140>)
- [`operation-loop/SKILL.md:143`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:143>)
- [`council/SKILL.md:111`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:111>)
- [`adversarial-review/SKILL.md:19`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:19>)
- [`codex-delegation/SKILL.md:301`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:301>)
- [`codex-delegation/SKILL.md:318`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:318>)

The history note at `codex-delegation/SKILL.md:8` does not make those doctrine sections historical. Rename operative roles to “Sol” or “current Codex peer”; retain 5.5 only inside dated evidence.

### 9. Medium — high-yield review patterns remain log-only

Not yet folded:

- Mandatory physics/causality lens for measurement work: [`skill-usage-log.md:252`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:252>)
- Positive-control challenge for negative verdicts: [`skill-usage-log.md:242`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:242>)
- Mutation testing in test audits: [`skill-usage-log.md:181`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:181>)
- Consult instead of blind third fix round, repeatedly validated: [`skill-usage-log.md:274`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:274>), [`:315`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:315>), [`:360`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:360>)
- Cross-thread foreign-diff inventory before commit: [`skill-usage-log.md:218`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:218>)
- Packet hygiene and explicit UNSWEPT evidence: [`skill-usage-log.md:304`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:304>), [`:319`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:319>)

### 10. Medium — mandatory consistency sweeps are repeatedly deferred without a formal debt path

The sweep is mandatory before final bookkeeping at [`operation-loop/SKILL.md:319`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:319>), but it is skipped, pending, or replaced at least eight times, including [`skill-usage-log.md:207`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:207>), [`:260`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:260>), [`:267`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:267>), [`:284`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:284>), and [`:363`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:363>).

The rule should remain mandatory, but stop/checkpoint handling needs an explicit named sweep-debt handoff rather than repeated undocumented substitution.

### 11. Low — dead citations and stale section pointers

- The seven absolute `/private/tmp/.../88d515fe...` evidence links in [`ADAPTER.md:163`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:163>)–167 and [`ADAPTER.md:297`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:297>) no longer exist.
- [`multi-stream-worktrees/SKILL.md:95`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:95>) and [`:172`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:172>) point to “Token-efficient consumption” for invocation/caveat mechanics, but that section is only a redirect at [`codex-delegation/SKILL.md:101`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:101>).
- [`consistency-sweep/SKILL.md:36`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:36>) says “Four checks” but lists five.

## Top five fold-in candidates

1. **Transport/wake:** “Route tracked background or parallel Sol work through `scripts/codex-bridge`, D-050/D-064 audited work through `codex-run-v3`, never bare `codex exec`, and end a turn only after a harness-tracked completion poll or equivalent wake source is verified.”

2. **D-061 layer evaluation:** “After three mechanically applicable exposures, evaluate the layer by expected-loss reduction using D-061’s outcome taxonomy; zero-catch streaks never auto-drop safety, final-head, or integration layers.”

3. **Fast Mode:** “Fast Mode is a one-call opt-in only—use `CODEX_SERVICE_TIER=fast scripts/codex-bridge …` when the fast-tier license applies, omit it otherwise, never make it a standing default, and do not assume `codex-run-v3` reads it.”

4. **Worktree commits:** “Direct Codex worktree sessions never commit or push; they return verified diffs/checkpoints and the lead alone creates pathspec commits, including during stop handling.”

5. **Measurement review:** “Every measurement-adjacent review panel includes a physics/causality lens—event timeline, power×duration plausibility, and clock-domain consistency—and recomputation alone is never sufficient sign-off.”

Next tier after those five: formalize the pending work-chunk D-080 cadence amendment; add “consult, not blind round three” on a repeated failure signature; add mutation testing to test-audit prompts; and add cross-thread foreign-diff inventory before any commit.
tokens used
182,268
# Skill-stack drift audit

Scope: read-only review of all six snapshot skills, `codex-delegation/ADAPTER.md`, and `skill-usage-log.md`, checked against the current bridge contract and repository orchestration sources. No files changed.

## Executive verdict

The stack has four release-blocking doctrine conflicts:

1. It teaches mutually incompatible Codex transports and wake guarantees.
2. It retains the D-061-superseded automatic review-layer drop rule.
3. It splits prompt-contract authority between the legacy adapter and bridge v1.1.
4. It both requires and forbids commits from Codex worktree sessions.

Fast Mode is absent from every snapshot skill. It appears only in the usage log, where its per-call-only formulation is correct. The current implementation supports it only through `scripts/codex-bridge`, not `codex-run-v3`.

## Ranked findings

### 1. Critical — transport and wake doctrine is self-contradictory

- [`codex-delegation/SKILL.md:21`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:21>) declares legacy `codex-run` the “ONE stable mechanism.”
- [`codex-delegation/SKILL.md:24`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:24>)–37 says its background exit guarantees a wake.
- [`codex-delegation/SKILL.md:379`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:379>) instead requires `codex-run-v3` for every new invocation.
- [`codex-delegation/SKILL.md:566`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:566>) records five incidents proving the wake guarantee false under Claude background tasks and mandates tracked polling.
- [`multi-stream-worktrees/SKILL.md:92`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:92>) still says background-and-end-turn is correct.
- [`adversarial-review/SKILL.md:19`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:19>) prescribes bare `codex exec`, directly forbidden at [`codex-delegation/SKILL.md:67`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:67>).

All three wrappers still exist, so this is not binary disappearance; it is routing drift. Current doctrine distinguishes `scripts/codex-bridge` for tracked background/parallel work from `codex-run-v3` for D-050/D-064 audited runs: [repo Codex skill:49](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/.claude/skills/codex/SKILL.md:49>), [repo Codex skill:93](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/.claude/skills/codex/SKILL.md:93>).

### 2. Critical — D-061’s superseded auto-drop rule remains operative

- [`operation-loop/SKILL.md:343`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:343>) makes two zero-catch sessions a drop-candidacy trigger.
- [`council/SKILL.md:82`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:82>) applies the same two-session rule to rotating lenses.
- [`council/SKILL.md:160`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:160>) repeats it again, with a grammatically missing subject.
- [`codex-delegation/SKILL.md:325`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:325>) retains a generic catch-rate drop rule.

D-061 explicitly replaced that policy with predeclared applicability, four outcome classes, fixed severity weights, and an expected-loss review after three applicable exposures—never automatic deletion: [decision log:3209](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/decision_log.md:3209>).

### 3. Critical — two documents claim to own incompatible prompt contracts

- [`ADAPTER.md:5`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:5>) calls itself the “ONE home.”
- [`ADAPTER.md:67`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:67>) and [`ADAPTER.md:376`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:376>) prescribe the legacy flat `ADAPTER:/GENRE:/WRITE_SCOPE:` prompt.
- Current bridge v1.1 requires delegated prompts to begin with `BRIDGE_TASK_V1` JSON: [bridge protocol:29](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/contracts/bridge_protocol.md:29>).
- The usage log repeatedly records launch failures caused by this ambiguity: [`skill-usage-log.md:282`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:282>), [`:311`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:311>), [`:329`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:329>).

The adapter remains valid as the full CLI report schema, but it must point to bridge v1.1 for launch/scope authority instead of presenting a competing prompt contract.

### 4. High — worktree sessions are simultaneously told to commit and not commit

- [`multi-stream-worktrees/SKILL.md:90`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:90>) requires atomic commits.
- [`multi-stream-worktrees/SKILL.md:118`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:118>) tells streams to commit during stop handling.
- [`multi-stream-worktrees/SKILL.md:168`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:168>) and [`codex-delegation/SKILL.md:91`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:91>) correctly say direct Codex cannot write linked-worktree Git metadata and the lead must commit.
- The failure recurs in the log at [`:28`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:28>), [`:291`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:291>), [`:305`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:305>), and [`:328`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:328>).

This is a candidate for wording repair, not relaxing the no-commit rule.

### 5. High — refuter defaults drifted apart

- [`adversarial-review/SKILL.md:28`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:28>) says fresh Codex refuters are the default and Opus is no longer default.
- [`adversarial-review/SKILL.md:146`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:146>) later makes Opus-contract + Sol-execution the default blocker pair.
- Panel size also differs: 2–4 lenses at [`adversarial-review/SKILL.md:22`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:22>) versus 2–3 at [`operation-loop/SKILL.md:217`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:217>) and [`multi-stream-worktrees/SKILL.md:98`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:98>).

The C-033 cross-model pair is the later rule; earlier operative wording should become dated history or a pointer.

### 6. High — fresh-eyes cadence is documented but demonstrably did not fire

- Both skills consistently say “every 10 delegated invocations plus phase boundaries”: [`council/SKILL.md:40`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:40>) and [`operation-loop/SKILL.md:24`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:24>).
- The log records roughly 16 invocations without a sweep: [`skill-usage-log.md:266`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:266>).
- It later validates concurrent read-only auditing but does not fold it in: [`skill-usage-log.md:341`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:341>).
- Ed’s latest ruling changes the intended shape to work-chunk-anchored with a mechanical backstop, pending formal D-080 amendment: [RUN_STATE:922](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/RUN_STATE.md:922>).

So there is no internal numeric disagreement, but the shared number is operationally stale and its provisional recalibration never happened.

### 7. High — Fast Mode is missing from the skills

Only [`skill-usage-log.md:348`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:348>) records it:

> per-call `CODEX_SERVICE_TIER=fast` via `scripts/codex-bridge` only

That is consistent with the per-call-only doctrine. The omission matters because the snapshot’s preferred `codex-run-v3` route does not read `CODEX_SERVICE_TIER`: [RUN_STATE:340](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/RUN_STATE.md:340>). The current repo-local skill has the correct rule at [`.claude/skills/codex/SKILL.md:58`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/.claude/skills/codex/SKILL.md:58>).

### 8. Medium — operative 5.5-era labels survived the Sol migration

Stale operative labels remain at:

- [`operation-loop/SKILL.md:140`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:140>)
- [`operation-loop/SKILL.md:143`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:143>)
- [`council/SKILL.md:111`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/council/SKILL.md:111>)
- [`adversarial-review/SKILL.md:19`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/adversarial-review/SKILL.md:19>)
- [`codex-delegation/SKILL.md:301`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:301>)
- [`codex-delegation/SKILL.md:318`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:318>)

The history note at `codex-delegation/SKILL.md:8` does not make those doctrine sections historical. Rename operative roles to “Sol” or “current Codex peer”; retain 5.5 only inside dated evidence.

### 9. Medium — high-yield review patterns remain log-only

Not yet folded:

- Mandatory physics/causality lens for measurement work: [`skill-usage-log.md:252`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:252>)
- Positive-control challenge for negative verdicts: [`skill-usage-log.md:242`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:242>)
- Mutation testing in test audits: [`skill-usage-log.md:181`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:181>)
- Consult instead of blind third fix round, repeatedly validated: [`skill-usage-log.md:274`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:274>), [`:315`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:315>), [`:360`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:360>)
- Cross-thread foreign-diff inventory before commit: [`skill-usage-log.md:218`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:218>)
- Packet hygiene and explicit UNSWEPT evidence: [`skill-usage-log.md:304`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:304>), [`:319`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:319>)

### 10. Medium — mandatory consistency sweeps are repeatedly deferred without a formal debt path

The sweep is mandatory before final bookkeeping at [`operation-loop/SKILL.md:319`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/operation-loop/SKILL.md:319>), but it is skipped, pending, or replaced at least eight times, including [`skill-usage-log.md:207`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:207>), [`:260`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:260>), [`:267`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:267>), [`:284`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:284>), and [`:363`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/skill-usage-log.md:363>).

The rule should remain mandatory, but stop/checkpoint handling needs an explicit named sweep-debt handoff rather than repeated undocumented substitution.

### 11. Low — dead citations and stale section pointers

- The seven absolute `/private/tmp/.../88d515fe...` evidence links in [`ADAPTER.md:163`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:163>)–167 and [`ADAPTER.md:297`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/ADAPTER.md:297>) no longer exist.
- [`multi-stream-worktrees/SKILL.md:95`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:95>) and [`:172`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/multi-stream-worktrees/SKILL.md:172>) point to “Token-efficient consumption” for invocation/caveat mechanics, but that section is only a redirect at [`codex-delegation/SKILL.md:101`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/codex-delegation/SKILL.md:101>).
- [`consistency-sweep/SKILL.md:36`](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/skills-snapshot/consistency-sweep/SKILL.md:36>) says “Four checks” but lists five.

## Top five fold-in candidates

1. **Transport/wake:** “Route tracked background or parallel Sol work through `scripts/codex-bridge`, D-050/D-064 audited work through `codex-run-v3`, never bare `codex exec`, and end a turn only after a harness-tracked completion poll or equivalent wake source is verified.”

2. **D-061 layer evaluation:** “After three mechanically applicable exposures, evaluate the layer by expected-loss reduction using D-061’s outcome taxonomy; zero-catch streaks never auto-drop safety, final-head, or integration layers.”

3. **Fast Mode:** “Fast Mode is a one-call opt-in only—use `CODEX_SERVICE_TIER=fast scripts/codex-bridge …` when the fast-tier license applies, omit it otherwise, never make it a standing default, and do not assume `codex-run-v3` reads it.”

4. **Worktree commits:** “Direct Codex worktree sessions never commit or push; they return verified diffs/checkpoints and the lead alone creates pathspec commits, including during stop handling.”

5. **Measurement review:** “Every measurement-adjacent review panel includes a physics/causality lens—event timeline, power×duration plausibility, and clock-domain consistency—and recomputation alone is never sufficient sign-off.”

Next tier after those five: formalize the pending work-chunk D-080 cadence amendment; add “consult, not blind round three” on a repeated failure signature; add mutation testing to test-audit prompts; and add cross-thread foreign-diff inventory before any commit.
