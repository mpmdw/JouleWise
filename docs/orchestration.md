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
  design: the recorded catches show the two model families consistently
  catching different classes of defect.
- **Specialist agents** handle bounded sweeps and investigations. The
  lieutenant-directed lanes of D-129 are superseded by the current roles
  below.
- **Image-heavy analysis uses the designated image-capable review route** per
  C-012, after the site-observatory stream's image-critique rounds.
- **Invited-peer validation is allowed to overturn lead designs**; C-014
  recorded two lead designs overturned by an invited peer before
  implementation.

### Current roles (Ed, 2026-09-29)

The current model for each seat is named in Ed's 2026-09-29 decision, the
decision-log entry "Gates are anti-spiral, never a bar on refinement;
network time stays OFF; the 09-29 team", which lands with the 2026-09-29
records PR; it is not repeated here.

- The **orchestrator** is the designated lead, working in an interactive
  session with Ed. It decomposes work, rules on design questions,
  dispositions review findings, reads the exact merge candidate, and holds
  merge authority. The headless relaunch loop ("magistrate") runs only while
  no stop is set: a local `STOP` file or a remote branch named `ops/stop*`
  holds it, and removing the stop releases it. When it runs, it follows the
  same rules as the orchestrator, from the step list that the top block of
  `RUN_STATE.md` names.
- The **default execution seat** implements, audits, and serves as a
  consult peer. Another model family is used only after a recorded,
  noticeable weakness of the default seat.
- **Investigator agents** are dispatched at will for bounded reading and
  sweeps.
- A **cold judge** is a fresh session that has not inherited the working
  lane's assumptions. It rules on a mechanically assembled packet, and it
  gives the cold final pass on merge code that touches measurement,
  calibration or claims (ledger row 4). When a cold gate is convened is set
  out below under "Cold gates, councils and round limits".

The lieutenant role and its list of things it could not decide alone are
retired by that decision: the orchestrator decides everything except what
is reserved to a cold gate or to Ed. These roles distribute reading and coordination;
they do not transfer final verification, hardware operation, scientific
scope, or publication authority.

### Cold gates, councils and round limits (process prune, 2026-09-29)

Ed authorized this prune on 2026-09-29 (summary and evidence in
`docs/process_prune_2026-09-29.md`). A gate exists to stop a death loop of
useless investigation or token burn, or to protect a number; it is never a
bar on refining a component whose defects are shrinking.

- **When a cold gate is convened.** Only for: (a) a registration, analysis
  plan or estimator constant; (b) a claim-bearing result (a calibration
  issued for claim use, a number the paper will print); (c) an irreversible
  action: deleting evidence, committing a measurement window, publishing;
  (d) a choice Ed has reserved to himself or to a cold gate. Fixture repair,
  scope grants, reading a ruling's own clause, process wording and
  "waiting" turn ends are the orchestrator's calls, recorded in the session
  record.
- **Refuter disagreement.** A cold ruling on a claim path is paired with one
  refuter. If the refuter disagrees, the judge (or the orchestrator, when
  the finding bears on no number) writes ONE erratum that settles it. There
  is no refuter on the erratum and no further chain.
- **No fixed round caps.** The same defect class failing twice in a row
  sends the next spend to a consult, not a third identical round (D-087,
  D-088; D-132 says stop rules target doom loops, never a converging
  component). Any clause that limits rounds must name where the question
  goes when the limit is reached ("escalate to a consult", "to a cold gate",
  "to Ed"); a clause that says "stop for good" or "no round N" is read that
  way (Ed's 2026-09-29 decision).
- **Councils.** A design question gets two blind seats from different model
  families (the default execution seat plus one reviewing-family seat). A
  cold judge is added only when the two disagree on a science question.
  A four-model council runs only when Ed asks for one (this thins D-184).
- **No deliberate-adversary ("forger") seats.** Guards against a deliberate
  forger retire under D-161; the prune reports found the forger seats caught
  nothing a replay refusal had not already refused. Mistake-shaped fuzz and
  mutation (delete-the-guard) tests on number-bearing code stay.
- **Enforcement charges ask first:** "can one setting or one command remove
  this hazard?" Network time is the example: it stays OFF (Ed,
  2026-09-29), with one OFF receipt per window at arm, instead of an
  enforcement machine.

### What the prune keeps, and the number each protects

- The arm notice (Ed can answer NO), the STOP file, and the stand-down
  fence that clears agent sessions before a window's first capture: they
  keep the machine quiet, since a running agent adds measured joules.
- The pre-arm triple audit (owner directive, GitHub issue #416): three
  blind audits that re-derive the calibration from raw capture files at the
  frozen code head before any claim-bearing run. It runs once per frozen
  code or protocol change, not once per window: the measurement Mac is
  dedicated, windows run back-to-back at the cadence the science needs
  (Ed, 2026-09-29: "nights" are metaphorical), and only physics waits sit
  between them (clean dwell, battery float, recovered idle power, network
  time OFF). Harvest is automated raw-byte validation plus an independent
  arithmetic check; full suites, lenses and cold passes run per code change.
- The cold science gate's raw re-derivation of a candidate calibration:
  every constant recomputed from the raw capture bytes, not read from the
  candidate's own report.
- The Impact statement on every pull request: it routes anything that can
  change a number to the full tier.
- Write-scope fences on the pinned estimator files, whose digests define the
  calibration.
- The whole suite on the merged tree before merge: it has caught failures
  that every lens and the final pass missed.

### Records

- One running record per session, appended as work happens. A headless
  relaunch that finds nothing to do writes no record and makes no commit.
- One `RUN_STATE.md` top block per session, not per relaunch; it is replaced
  at the session's end, and history lives in the session record.
- Verbatim quotation is kept for Ed's words only. Rulings, briefs and seat
  reports are cited by path, not copied.
- The writing standard (build every term before its first use) binds the
  paper and owner-facing prose (README, advisor and owner briefs). Internal
  records, rulings, `RUN_STATE.md` and decision-log entries need to be
  correct and plain, not explainer-grade; they get no pedagogy pass.
- Email Ed on a change of state only: arming or standing down a window, a
  question he must answer, a verdict he asked for, or a fault. A quiet
  relaunch sends no email.

### The one pruning rule

At the end of every session the orchestrator lists each gate or check that
ran this session and what it caught that touched a number. Any mechanism with
no such catch in its last three sessions is proposed for deletion to Ed. This
replaces the pruning rules that were written and never applied: the
two-zero-sessions drop and the D-061 per-layer yield tally, the D-080
standing sweep cadence, the spend guardrails below, and the
post-large-workload reassessment.

## The loop, end to end

Every substantial session runs one conductor procedure:

1. **Intake** — run Mission M0 in `docs/agent_playbook.md`. It begins at the
   generated `RUN_STATE.md` restart view, selects the kernel or generated queue
   row, and follows that row's authority and acceptance pointers; never
   re-decide anything the decision log settled.
2. **Decompose** — split work into genuinely independent streams
   (disjoint expected diff footprints), one git worktree + branch each;
   assign each stream a review tier by *cost of being wrong*
   (measurement-semantics and contract-bearing work gets the full
   pipeline; docs get a light tier). Preflight gates: hardware-shaped
   streams require a confirmed device inventory; anything pinned
   without live validation carries a PROVISIONAL label; measurement
   sessions require a no-agent "quiet machine" lock.
3. **Per-stream pipeline** — for each reviewable unit: implementation, then
   an independent review by a non-author with a lens that executes the code
   (a contract lens as well when a contract changes) → the lead's recorded
   disposition of every finding (fixed, deferred to a named lane, or
   rejected with a reason) → fixes → a delta review of the fixes when they
   touch number-bearing code → the lead's diff read. Docs, records and
   test-only fix rounds get no delta review; CI checks them.

### One writer per working tree (the two-writer rule)

At most one process may write a working tree at a time. The lead counts as a
writer: lead bookkeeping, cleanup, formatting, conflict resolution, and
“small” post-review edits may not overlap a worker that can modify the same
tree. Parallel writers require separate worktrees/branches and disjoint
expected diff footprints. Review-only readers may overlap only when their
tools are guaranteed read-only.

Before taking write ownership, the writer must identify the tree and branch,
wait for every prior writer to finish or be explicitly stopped, inspect
`git status --short --branch`, and preserve all pre-existing changes. Before
lead bookkeeping begins, the lead must declare the tree quiescent. No cleanup
or generated-file refresh may run over another writer’s uncommitted work.

If overlap is discovered, stop new writes; capture the branch, HEAD, status,
and diffs for both owners; preserve both versions; and let the lead reconcile
them. Never resolve an ownership collision by discarding or reverting work by
inference.

Writer separation and reviewer separation are distinct. The author of a
change or test may not be its sole fresh reviewer/auditor. Any lead or worker
content edit after the last fresh review creates a new final-head review
obligation. Lead-owned live/hardware gates remain lead-owned and are not a
writer-separation violation.

### Credential-boundary push handoff

“Push green commits promptly” is an outcome, not permission to copy or bypass
credentials. If the current environment cannot authenticate, it must hand the
exact reviewed commit to a named authenticated pusher instead of accumulating
silent local-only state.

The blocked environment must: (1) finish the authorized local checks; (2)
record the repository, branch, remote, exact commit SHA, clean/dirty status,
and review/CI state; (3) name the authenticated pusher and an explicit
ISO-8601 deadline no later than the next dependent session or any claim of
remote/advisor freshness; and (4) record the handoff in the run report and the
live queue. If missing remote state makes restart unsafe, create an active stop
card. Credentials themselves are never transferred.

The authenticated pusher must verify that the received branch resolves to the
recorded SHA, rerun any environment-bound required gate, push that exact SHA to
the named remote/ref, and record the remote ref/SHA confirmation. If the SHA
changes, normal review and final-head rules reapply before push or merge.

Until remote confirmation exists, status must say `LOCAL_ONLY — PUSH PENDING`;
the project must not claim that GitHub, a PR, a deployment, or an advisor-facing
snapshot contains the change. A missed deadline becomes an explicit
`[ED-EXTERNAL]` blocker, not an informal “push when convenient” note.

This procedure does not expand commit, push, merge, or deployment authority.

4. **Lead live gates** — never delegated: the lead runs the real flow
   (real corpus, real CLI, real hardware where present). This layer has
   repeatedly caught blockers no other layer saw, including defects
   whose own tests were green because the tests encoded the same wrong
   assumption as the code.
5. **Merge gate** — multi-commit series land as branch + PR. The gate
   ledger is the `## Gate ledger` section of the PR body
   (`.github/pull_request_template.md`), checked by
   `scripts/check_gate_ledger.py` in the `gate-ledger` workflow, a required
   status check on `main` since 2026-09-24 (D-170). It is D-118 thinned on
   2026-09-29 to six keys, each protecting something real: (1) independent
   review by a non-author, with a lens that executes the code; (2) the whole
   suite on the merged tree; (3) CI green on the final head, whose sha the
   row names; (4) a cold final pass on merge code that touches measurement,
   calibration or claims; (5) every finding dispositioned (fixed, deferred
   to a named lane, or rejected with a reason), with no counting of fix
   rounds; (6) the Impact statement. Rows 1-5 take `RUN <sha-or-path>`
   evidence. **Final-head rule:** a commit that lands after review and
   touches number-bearing code gets a fresh review of that commit before
   merge; a later docs, records or test-only commit needs only green CI.

   **Rule TIER-01 (cold-gated by COUNCIL-407-01 §G5 on 2026-09-24; endorsed by Ed in GitHub issue #415 on 2026-09-25; light tier thinned 2026-09-29).**
   1. A change is FULL-TIER if it can alter any of: (i) a raw-bundle byte or recorded timestamp; (ii) a reduced energy, time, token count or correctness score; (iii) an admit, refuse, select or exclude decision over bundles, nights, blocks, envelopes or items; (iv) a unit or an uncertainty; (v) a registration, prospective manifest, analysis plan or estimator constant; (vi) a published number or sentence in the paper, README claims or claim renderers. This includes, without limiting (i)–(vi): `joulewise/clock.py`, `controller.py`, the night driver and chain, collectors and runtime adapters, calibration, scoring, packers, reducers, estimators, admission predicates, arm readiness and census, and everything under `configs/campaigns` and `configs/model_panels`. Any change to code or configs is FULL-TIER; docs, records and tests are LIGHT-TIER.
   2. Every PR body carries `Tier: full|light` and a six-line Impact statement answering (i)–(vi), each answer starting with Yes or No. The checker refuses a light tier with any Yes. Any disagreement about the tier resolves to full.
   3. FULL-TIER needs ledger rows 1, 2, 3 and 5 with evidence; row 4 may read `N/A (no measurement, calibration or claim code)` only when every Impact line is No. LIGHT-TIER needs the Impact statement, CI green on the final head (row 3) and, when tests changed, the whole suite (row 2; docs-only PRs write `N/A (docs only)`); rows 1, 4 and 5 read `N/A (light tier)`. A light-tier PR runs no audit rounds.
   4. Revert trigger: until the day-30 review, every material defect found after merge is logged with the tier of the PR that merged it in `docs/process/tier01_defect_log.md`. If any defect that changes a recorded, reduced or published number entered under LIGHT-TIER, TIER-01 is suspended at once (all changes full tier) and may be reinstated only by a new cold gate.
   5. Day-30 review 2026-10-25: the orchestrator records the light-tier merge count and escape count in the decision log; the rule continues only by a recorded decision.

6. **Integration review** — only for a merge wave of two or more PRs
   that change measurement code: one dedicated review hunts *interaction*
   defects no single-stream review can see. The whole suite on the merged
   tree (ledger row 2) covers a single PR.
7. **Bookkeeping** — the one running session record (see "Records" above);
   the intake pointer and queue refreshed; CI's documentation fences
   (`tests.test_docs_freshness`, `gen_state --check`) check drift. Records
   and bookkeeping land as light-tier PRs with no audit rounds.
8. **Same-session distillation** — lessons fold into the process
   playbooks the same session they are learned. Measured effect: one
   failure mode recurred five times before its fix was distilled, zero
   times after. The current operation-loop also runs its §0
   primary-deliverable check and §8 shipped-check before the session is
   considered done.
9. **Post-landing verification and close-out** — landed work that can
   change a number gets the lead's live verification. D-136 retires
   the site lane from routine sessions: agents do not refresh, regenerate, or
   deploy it. The retained `docs/site/DRIFT.md` file is only a reference if Ed
   chooses the manual workflow dispatch; Ed deploys the site after that manual
   regeneration.
10. **Mechanism audit (the final step)** — the one pruning rule above: list
    each gate or check that ran this session and what it caught that
    touched a number; propose to Ed the deletion of any mechanism with no
    such catch in its last three sessions.

### Session-end fixture census

- Run `python3 scripts/fixture_orphan_census.py --fail-on-orphans` before
  handing off a session and record its JSON rows and count. Exit 0 means an
  empty census, 1 means registered fixtures with parent PID 1 were found,
  and 2 means observation or registry validation failed (not a clean census).
  Without `--fail-on-orphans`, successful observation exits 0 even with matches.
- Fixture authors extend `tests/fixture_signatures.json` with a unique `id`,
  a `command_regex` specific to the fixture's displayed argv, and a `source`
  pointing to its launcher. Add positive and non-fixture negative cases to
  `tests/test_fixture_orphan_census.py`. Do not register generic production
  worker or model commands. The NV5 fixture runs the real node worker against
  a fake vLLM; its task path distinguishes it from production workers.
- The watchdog records the same census and count in its launch-time
  `fixture_orphan_census` event in `events.jsonl`. An acquisition error has
  null count/rows and an error message. This is informational: launch refusals
  and the night gate's agent census are unchanged. This bounded sentinel increment
  does not wire prewindow refusal or culling. It never signals a process;
  any future culling workflow needs separate authorization and identity
  revalidation outside plan spans. A ps snapshot is observation, not kill authority.

### Stop cards and paused work

When a session stops with live work in progress, the lead creates or updates
the rich card under `docs/stop_cards/`, sets the kernel's `active_stop_card`
pointer and affected task pointers, and regenerates the two views. While
active, the generated card wrapper is the single restart authority and
overrides every lower
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
bookkeeping cannot fit: write the stop card, update its pointer and affected
tasks in `docs/process/state_kernel.json`, and run `python3
scripts/gen_state.py`. Never hand-edit either generated view.

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

- **Per-layer yield (retired 2026-09-29):** the D-061 per-layer tally was
  last kept in early September and never fired. The one pruning rule above
  replaces it: a session-end list of what each gate caught that touched a
  number.
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

Councils are expensive instruments. The shape is set above under "Cold
gates, councils and round limits": two blind seats from different model
families, a cold judge only when they disagree on a science question, and
a four-model council only when Ed asks. For ordinary implementation, use
one executing review lens plus the lead's disposition.

A council leaves one disposition table: finding → ruling → owner →
artifact, queue row or decision entry. A decision it promotes is written
to the decision log in the same session.

## Spend guardrails (WO-022) — retired 2026-09-29

The WO-022 spend guardrails (bands, arc snapshots, the 33% process-facing
tripwire, the named-failure bar and sunset entries for new layers) were
ratified on 2026-07-13 and never applied: no spend snapshot or
process-facing classification appears in any record from 2026-09-22 to
2026-09-29, although the tripwire would have fired on that week's work.
They are retired by the owner-authorized prune of 2026-09-29
(`docs/process_prune_2026-09-29.md`) and replaced by the one pruning rule
under "Cold gates, councils and round limits". The full text is in this
file at commit `32ff9013`. The anti-spiral rule that remains is: the same
defect class twice in a row goes to a consult, and usage limits are
logistics, not verdicts.

## Historical topology (retained context, not the current role contract)

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
- Delegated-seat verification: run
  `python3 scripts/quick_suite.py --tier touched --since <BASE_HEAD>` before
  handing back; paste its summary. The default `--tier quick` runs the state
  and documentation fences plus measured modules below `--max-seconds` (default
  five seconds), excluding exclusive and split modules. A211
  (`TEST-CANONICAL-PATH-DEPENDENCY-01`) modules with canonical-checkout
  dependencies are explicitly denied in both tiers and single-module replays
  until that lane fixes them; the worktree-local `R7F_CORPUS_ROOT` override
  remains in force. Touched adds tests
  naming changed paths/modules, matching test-name prefixes, edited tests, and
  every module with an unknown weight. Every exclusion is listed. Each module
  uses the shard runner in a fresh process with a temporary directory outside
  the checkout; `--workers` bounds parallelism, and touched exclusive modules
  run alone. Measurements above three times the timing-map weight print a
  `STALE WEIGHT` finding. Failures include an exact single-module replay command.
  CI runs quick first on Python 3.13 with four workers after interpreter
  selection; ordinary and exclusive test jobs require its success. The lead
  retains ownership of full-suite and live verification.
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
