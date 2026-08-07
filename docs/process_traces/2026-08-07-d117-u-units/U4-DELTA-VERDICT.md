Reading additional input from stdin...
2026-08-07T20:20:30.058236Z ERROR codex_models_manager::cache: failed to load models cache: missing field `base_instructions` at line 94 column 5
OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: high
reasoning summaries: none
session id: 019fdde2-6853-7422-89c0-aa2c98e2bf4e
--------
user
DELTA RE-AUDIT of U4's amendment round (read-only; write no files; FINAL MESSAGE in neutral engineering language, conclusions only, no code quotes beyond file:line). Branch impl/d117-u4-regression at HEAD. Context at origin/main: docs/process_traces/2026-08-07-plan-factory/OPUS-EXAM-U4-U8.md (the examination) and MAGISTRATE-DISPOSITIONS.md (adopted amendments FIX-A..F). Diff: git diff origin/main...HEAD.
(1) Verify FIX-A..F closed. Specifically: is the terminal-sequence oracle now DERIVED from the production receipt path rather than asserted (and does the happy path actually drive claim_bracket_session_slot)? Does the allowance test fail if max() is replaced by either operand alone or by min() — mutate and report? Is the L5 test real (a candidate under another window's runs_root refused, both with and without a binding)? 
(2) Hunt introduced defects: did the fixture changes break any previously-passing vector? Are the 3 staged/skipped tests still correctly staged behind U2 (not silently disabled)? Does anything now depend on U1 internals in a way that would break when U1 merges to main?
(3) Same-signature statement per original defect class (stale-memo-literal; one-sided-branch test): survives yes/no.
Run the module + calibration focused suites; report exact tails. CLEAN needs a checks-performed line.
codex
I’ll perform a read-only delta audit against `origin/main`, including in-memory mutation checks for the allowance oracle, then run the requested focused suites and report only conclusions with exact command tails.
exec
/bin/zsh -lc "git status --short --branch && rg -n \"ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next\" RUN_STATE.md && rg -n \"Current Queue|Do-Not-Do-Yet\" TASK_QUEUE.md && sed -n '1,240p' docs/agent_playbook.md && sed -n '1,260p' docs/orchestration.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
## impl/d117-u4-regression...origin/impl/d117-u4-regression
2008:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
2043:## ACTIVE_STOP_CARD
2182:## Current Project Status
2743:## Known Workspace State
96:Current Queue region is the sole live work-selection view.
213:## Current Do-Not-Do-Yet List
306:## Current Queue
# Agent Playbook: Ordered Missions

Audience: an agent (or human) told "go do the next step" with no other
context. This file turns the project's plans into self-contained,
executable missions. Each mission says what to read, what to do, how to
verify, and what to update afterward.

Division of labor (D-023 discipline — do not duplicate):

- **This file owns:** the operational wrapper per mission (read-first
  lists, execution order, verification commands, handoff checklists) and
  the code-level pointers from the 2026-07-05 external code review that
  exist nowhere else.
- **It points to:** `docs/phase_N/phase_N_plan.md` for objectives, gates,
  acceptance criteria, and fallbacks; `docs/phase_2/
  hardware_slice_implementation_guide.md` for hardware-slice pinned APIs;
  `docs/decision_log.md` for settled decisions; the phase exit checklists
  for current per-item status.
- **No status lives here.** To find out what is already done, read
  `RUN_STATE.md` and the exit checklists. To find out what outranks what,
  read `TASK_QUEUE.md`. If this playbook and a plan disagree, the plan
  wins; fix the drift in the same run.

## How To Pick A Mission

1. Run Mission M0 (preflight) — always.
2. Take the highest-ranked task in `TASK_QUEUE.md` whose gate is open.
3. Find its mission below and execute it. One mission per session unless
   the first finishes early and cleanly.

Gate summary (check the queue/checklists for live status; this is just
the dependency shape):

```text
ungated, any time:      M1 (Slice 2N), M2 (backup protocol prep), M3 (related work)
needs user/advisor:     M4 (D-016 model selection), and the P1 evidence gates
needs D-016 + install:  M5 (2G MLX)
needs auth session:     M6 (2H powermetrics)
needs M5+M6:            M7 (2I Mac slice — the flagship)
needs P1-006 evidence:  M8 (2K/2L remote-target live validation;
                         2K fixture-first stack merged 2026-07-08 via PR #11)
needs M7:               M9 (2M baselines)
post-docs branch:       M10 Stage 3.0.1 verdict is replay_supported
                         after lead live re-verification
needs 2M baselines:     M10 later pairing-feasibility matrix + split runs
```

---

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
  file retained verbatim").
- Change: implement **D-024** (already decided — read it first): an
  immutable `RunContext` dataclass (config, clock, run_id, bundle_path,
  raw_dir, logs_dir, outputs_dir, optional node_role=None) constructed
  by the controller after bundle creation and passed to adapter
  lifecycle methods (exact placement — per-method parameter vs
  construction-time — is yours to pin; record the choice as a D-024
  amendment note). Add `RunBundleWriter.raw_path(name)`/`write_raw` as
  the writer-side counterpart (validated, collision-checked). Update
  `docs/contracts/adapter_contracts.md` in the same run. Do NOT hand
  adapters the writer itself — D-024 rejects that option; context is
  data, not capability.
- Tests: mock telemetry writes a fixture raw file via the context;
  bundle contains it; immutability (no overwrite after finalize); the
  no-raw-output mock path still passes; mocks ignore unused context
  fields (single lifecycle code path preserved).

### 2N.2 Measured window excludes sampler startup

- Today: `stage_started(measured_run)` is timestamped before
  `thermal_state` and `start_sampling` (controller.py ~lines 346-357),
  and the reducer integrates from that stage-start. Under `SystemClock`,
  sampler spawn latency (sudo probe, process start, first sample) lands
  inside the measured window — inflating gross energy, idle-subtraction
  duration, and TTFT. `FakeClock` collapses the interval to zero, so the
  existing suite cannot catch it.
- Change: open the measured window only after sampling is confirmed
  started (reorder), or emit explicit `sampling_started`/
  `sampling_stopped` marker events and make the reducer integrate
  between markers. Keep the D-013 quiescent rule intact (controller only
  blocks on the runtime inside the window). Record the choice
  (decision-log entry; it pins reducer semantics).
- Tests: a fake telemetry adapter whose `start_sampling` advances the
  injected clock by a simulated latency; assert the reducer's window
  excludes it (energy and TTFT unchanged vs a zero-latency run).

### 2N.3 Reducer token-count fallback

- Today: `energy_token_j` requires `workload_profile.prompt_tokens` from
  config (reduce.py ~lines 302, 511-521); a `prompt_text`-only config
  (like `configs/examples/mac_mlx_local.json`) silently yields `None`
  for the headline per-token metric, even though the runtime's observed
  `token_count`/`output_token_count` are already written to
  `metadata.json` (controller.py ~lines 532-536).
- Change: reducer falls back to observed counts from metadata; record
  which source was used (additive optional summary/quality field, e.g.
  `token_count_source: "config" | "runtime_observed"` — R-015 allows
  additive).
- Tests: prompt_text-only bundle produces non-None `energy_token_j`
  with source `runtime_observed`; config-supplied counts still win;
  neither present → None (unchanged).

### 2N.4 Rail-summation timestamp contract

- Today: `_summed_curve` groups rails by exact float `timestamp_s`
  equality (reduce.py ~lines 129-131). A real adapter emitting per-rail
  rows with slightly skewed timestamps silently produces an interleaved
  per-rail curve and badly undersummed energy — wrong number, no error.
- Change: either (a) detect misalignment (per-timestamp rail set !=
  manifest) and return a structured reduction failure naming the rail
  and skew, or (b) bucket timestamps within a tolerance derived from the
  sampling interval. Decide, log the decision, and document the
  contract in `docs/contracts/adapter_contracts.md` (today it is only a
  bundle.py comment).
- Tests: skewed-timestamp fixture → structured failure (or correct
  bucketed sum); aligned fixture unchanged to 9 decimals.

### 2N.5 Config schema accepts emitted configs

- Today: `BenchmarkConfig.to_dict()` emits `null` for absent optionals
  (`asdict`), but the hand-written exported JSON Schema declares those
  properties non-nullable (e.g. `quantization.bits`, schemas.py ~line
  379) — a bundle's normalized `config.json` fails validation against
  `print-config-schema` output.
- Change: pick one — (a) omit-None serialization (cleaner artifact;
  changes config bytes and therefore config hashes — acceptable ONLY
  while no real bundles exist, so decide now), or (b) schema declares
  nullable optionals. Either way: decision-log entry, and a round-trip
  test.
- Tests: every emitted normalized example config validates against the
  exported schema. CI has no `jsonschema` package (D-009): either write
  the check against the specific fields (nullability + required keys) or
  gate a full-validator test behind `skipUnless(jsonschema)`. Also
  assert config-hash stability with a pinned expected hash so future
  serialization changes fail loudly.

### 2N.6 Post-hoc `reduce` verb + structured reducer failures

- Today: `reduce_bundle` is importable but has no CLI verb, and raises
  uncaught `FileNotFoundError`/`JSONDecodeError` on missing/corrupt
  `config.json`/`metadata.json` (reduce.py ~lines 341-352) despite its
  docstring's "never crashes" claim. The "a reducer bug never re-runs
  hardware" story needs a user-facing path.
- Change: `python3 -m joulewise reduce <bundle-dir>` — re-derives and
  rewrites `summary_metrics.json` (document that this is the one
  sanctioned post-finalize mutation, or write to a versioned name —
  check D-011 and log the choice); degenerate inputs return structured
  failures. Match `run`'s exit-code scheme (0/2/3) and one greppable
  result line.
- Tests: reduce a valid bundle → identical metrics; corrupt/missing
  artifacts → structured failure + correct exit code; CLI help updated.

### 2N.7 Report/reducer rail-policy alignment (via 2N.8)

- Today: the report's trace chart falls back to summing ALL rails when
  the manifest is empty or matches nothing (report.py ~lines 187-209),
  while the reducer excludes non-manifest rails or fails — a chart can
  display energy the summary excluded.
- Change: do 2N.8 first, then implement both consumers' rail policy in
  the shared reader (D-025 is explicit: no spot fix). The report must
  never contradict the summary.
- Tests: manifest-mismatch bundle renders with the aligned behavior;
  normal bundle chart unchanged.

### 2N.8 Shared bundle read layer (`BundleReader`)
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


codex
The working tree is clean, there is no active stop card, and the requested branch is checked out. The two examination documents are not present in this branch’s worktree path, so I’m resolving them directly from `origin/main` as requested rather than treating their absence as evidence.
exec
/bin/zsh -lc "git rev-parse --short HEAD && git rev-parse --short origin/main && git ls-tree -r --name-only origin/main | rg 'OPUS-EXAM-U4-U8|MAGISTRATE-DISPOSITIONS|plan-factory' && rg --files -g 'AGENTS.md' -g '"'!vendor'"' -g '"'!node_modules'"' && git diff --stat origin/main...HEAD && git diff --name-status origin/main...HEAD && git log --oneline --decorate origin/main..HEAD" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
4b82180
1b66032
docs/process_traces/2026-08-07-plan-factory/DRAFT-MOE_GATES.md
docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md
docs/process_traces/2026-08-07-plan-factory/DRAFT-PROBES.md
docs/process_traces/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md
docs/process_traces/2026-08-07-plan-factory/DRAFT-REASONCODE.md
docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md
docs/process_traces/2026-08-07-plan-factory/DRAFT-U4.md
docs/process_traces/2026-08-07-plan-factory/DRAFT-U8.md
docs/process_traces/2026-08-07-plan-factory/MAGISTRATE-DISPOSITIONS.md
docs/process_traces/2026-08-07-plan-factory/OPUS-EXAM-PROBES-PROSE.md
docs/process_traces/2026-08-07-plan-factory/OPUS-EXAM-QUANT-MOE.md
docs/process_traces/2026-08-07-plan-factory/OPUS-EXAM-REASONCODE-NEVERZERO.md
docs/process_traces/2026-08-07-plan-factory/OPUS-EXAM-U4-U8.md
docs/process_traces/2026-08-07-plan-factory/PLAN-U4-extracted.md
docs/process_traces/2026-08-07-plan-factory/PLAN-U8-extracted.md
site_capsule/AGENTS.md
AGENTS.md
 joulewise/calibration_bracketing.py                |  372 +++++-
 joulewise/calibration_ledger.py                    | 1274 +++++++++++++++++-
 scripts/reserve_calibration_window_bracket.py      |  141 ++
 scripts/validate_powermetrics_fiducial.py          |  359 ++++-
 .../calibration_live_three_window/scenario.json    |  168 +++
 tests/test_calibration_bracketing.py               |  363 +++++
 tests/test_calibration_ledger.py                   |  583 +++++++-
 tests/test_calibration_live_three_window.py        | 1400 ++++++++++++++++++++
 tests/test_powermetrics_fiducial.py                |  256 ++++
 9 files changed, 4808 insertions(+), 108 deletions(-)
M	joulewise/calibration_bracketing.py
M	joulewise/calibration_ledger.py
A	scripts/reserve_calibration_window_bracket.py
M	scripts/validate_powermetrics_fiducial.py
A	tests/fixtures/calibration_live_three_window/scenario.json
M	tests/test_calibration_bracketing.py
M	tests/test_calibration_ledger.py
A	tests/test_calibration_live_three_window.py
M	tests/test_powermetrics_fiducial.py
4b82180 (HEAD -> impl/d117-u4-regression, origin/impl/d117-u4-regression) U4 amendment round (FIX-A..F): terminal sequence DERIVED from production receipt count (76 + 3x5 = 91, superseding the memo's stale 85 three-receipt model); allowance test now straddles the 0.010818 bound so both max() branches are exercised; L5 named; positive count oracle; per-window verdict issuance; real discovery-authority test
50404be U4 speculative implementation: synthetic three-window live-ledger regression (19 tests, 3 staged behind U2) — built from the pre-examination plan; carries the stale sequence-85 oracle and a one-sided D-110 allowance test, both closed in the next round
f665dd4 Merge main (D-117 index fix) into U1 branch
c645bd7 U1: two-slot ledger bracket-session capability + exact binding + writer integration, through fix round 1 (L5 mandatory window/runs_root binding; D-109 universe preservation; mid-window pin refusal; exclusive slot claim; candidate-leak closure; WAL torn-tail recovery; discriminating crash/rollback tests; CLI dry-run parity)

exec
/bin/zsh -lc "git show origin/main:docs/process_traces/2026-08-07-plan-factory/OPUS-EXAM-U4-U8.md | sed -n '1,360p' && git show origin/main:docs/process_traces/2026-08-07-plan-factory/MAGISTRATE-DISPOSITIONS.md | sed -n '1,420p' && git show origin/main:docs/process_traces/2026-08-07-plan-factory/PLAN-U4-extracted.md | sed -n '1,360p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
# Opus examination — DRAFT-U4 and DRAFT-U8 (D-117 plan factory)

Examiner: Opus 5 (lieutenant lens: contract + execution).
Date: 2026-08-07.
Ground truth read: `desk` @ `3b5a794` (main); D-117 (`docs/decision_log.md` tail);
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`;
`docs/process_traces/2026-08-07-night-hardening/FINDINGS-REGISTER.md`;
`docs/phase_2/window_runbook.md`; `docs/phase_2/refusal_scope_spec.md`;
branch `impl/d117-u1-ledger-session` @ `f665dd4` (source read, not just diffstat).

## Custody note (read this first — it affects what was examined)

The two files named in the charge are **truncated snapshots**. Both
`docs/process_traces/2026-08-07-plan-factory/DRAFT-U4.md` (8,764 lines) and
`DRAFT-U8.md` (10,692 lines) were custodied at commit `3b5a794` *while the Sol
runs were still streaming*: DRAFT-U4.md ends mid-`exec` inside a source dump,
and contains **no final message at all**. The complete transcripts are the live
files `scratchpad/plans/draft-u4.md` (9,275 lines) and `draft-u8.md` (11,191
lines). I examined the final markdown blocks of the **live** files, extracted to
`scratchpad/plans/PLAN-U4-extracted.md` (lines 8765–9020 of draft-u4.md) and
`PLAN-U8-extracted.md` (lines 10693–10942 of draft-u8.md).

> **Amendment C-0 (custody, applies to the whole plan-factory batch):** re-custody
> all eight drafts from the live scratchpad files. The committed U4 draft does not
> contain the plan it is named for; anyone reviewing from the repo copy alone is
> reviewing nothing. Verify the other six drafts for the same truncation before the
> Fable review.

**Speculative branches produced no evidence.** `impl/d117-u4-regression` is at
`f665dd4` (== U1 tip, zero own commits) and `impl/d117-u8-readiness` is at
`0d9392f` (== main-ish, zero own commits); neither exists at origin. There is no
implementation diff to read as evidence of what the plans produce in practice.
This examination is of the plans on their own terms.

---

# PLAN U4 — synthetic three-window live-ledger regression

## Verdict: **ACCEPT-WITH-AMENDMENTS**

The plan is unusually strong on enumeration. I checked its coverage against the
memo's normative list line by line: all 7 memo proof obligations are named tests
(plus one extra on the issuance prefix), and all 12 memo refusal-vector bullets
decompose into 30 named tests with setups and oracles — 3/3 import, 4/4
session-receipt, 4/4 head/chain, 5/5 observation-universe, 4/4 binding, 5/5
endpoint-eligibility, systematic, range-expansion, count-boundary, and 2 of the
successor-prefix vectors staged. The arithmetic is self-consistent (8 + 30 = 38
active, + 5 staged = 43). Every API it names (`append_bracket_session_receipt`,
`finalize_bracket_session_slot`, `terminal_head_pin_for_session`,
`abort_bracket_session`, `build_calibration_bracket_binding`,
`discover_calibration_candidates`, `prepare_historical_import`,
`bootstrap_historical_import`, `_valid_acceptance_bound`, `MAX_AGE_S`) exists on
`f665dd4`, and every refusal code it asserts (16 checked) is a real spelling in
the landed taxonomy. That is a materially better grounding rate than the memo
itself achieved.

It is not ACCEPT because three of its central oracles are either **stale against
landed U1**, **unable to discriminate the implementation they name**, or
**structurally divergent from the operational path the three nights will run**.

### (a) Completeness — gaps

- **G1. The terminal-sequence oracle is stale.** The plan freezes "three receipts
  per window → sequence 85" from the memo, and *deliberately avoids the
  production writer* to hit it ("do not emit optional writer-claim receipts").
  But U1 as landed is not a three-receipt model: `calibration_ledger.py` defines
  `BRACKET_SESSION_SLOT_CLAIM_EVENT = "bracket-session-slot-claim"` and
  `claim_bracket_session_slot()` appends "one process-death-stable exclusive
  claim"; the operator-facing writer `scripts/validate_powermetrics_fiducial.py`
  calls `claim_bracket_session_slot` (line 409) before
  `finalize_bracket_session_slot` (line 467). The real three-night ledger is
  therefore 5 receipts/window and terminates at **91**, not 85. The plan
  acknowledges this in a risk bullet and then chooses the number over the path.
- **G2. Committed-pin cadence is unspecified for the happy path.** Step 5 says
  "advance the synthetic committed pin before opening the next session" with no
  statement of whether committed-pin enforcement is active during construction.
  Committed-pin discipline appears only inside one negative test
  (`test_uncommitted_terminal_head_pin_refuses`, which builds its own temp git
  repo). The operational reality — three quiet nights separated by two *repo
  commits* of `configs/calibration/calibration_ledger_head.json` — is never
  proven end to end.
- **G3. No NEEDS_SCOPE protocol.** The plan says "No production modules … or
  existing tests are in scope" but never states what the implementer does when
  the regression exposes a genuine U1/U2 defect (the likely outcome for an
  integration regression). U8's plan states this; U4's does not.
- **G4. `fixture_spec.json`'s role is undefined.** The plan lists its contents
  but never says whether it is *consumed* by the harness (authoritative) or
  merely *documentation duplicated in code*. If the latter, it can drift silently
  and is dead weight in the write scope.
- **G5. Test-double boundary is under-specified.** "the raw-physics refit is
  replaced with a deterministic test double returning each evidence file's exact
  decimal bound" — the plan does not name the seam (function/module) being
  doubled, so two implementers would double different things. It also does not
  state a guard that the double is *not* in effect for any test whose oracle is a
  bound value.

### (b) Correctness against the memo/decisions

- The memo's own hedge licenses the fix for G1: *"the ideal terminal sequence is
  85 **under the proposed three-receipt session model**"* (memo, §Synthetic
  three-window live-ledger regression). U1's landed model is a five-receipt
  model. The memo is superseded by the implementation it authorized; the plan
  should say so rather than route around the production writer to preserve a
  literal.
- The count-boundary test is arithmetically right and I verified it against
  D-116: issued corpus is 30 valid, threshold is 38, "eight further valid
  same-epoch observations would" trigger `corpus_doubles_from_19_to_38`. Three
  windows contribute 6 valid live observations → **36**. The plan's "extend with
  two further" reaches 38 correctly.
- The plan's synthetic issued acceptance artifact is built by *cloning the
  production artifact's numeric fields, swapping in 19 generated corpus
  identities "while retaining the original bound lexemes and arithmetic", and
  recomputing `derivation_sha256`*. That artifact's bound is **not derivable from
  its own prior set**. D-116 records that the real artifact was "Emitted
  deterministically (not hand-edited) from the historical-import finalizations."
  A hand-patched parent will either mask a U2 successor defect or force the
  staged successor tests to be written around the inconsistency.
- Everything else I checked (import exclusion, six-candidate universe, binding
  exactness, D-110 `max(observed_drift_s, 0.010818)`) matches D-110 cl.1/D-102
  pin 3 and D-116 as recorded.

### (c) Ratified invariants

Fail-closed: respected — every vector's oracle is a refusal, and the
re-chain-before-mutate discipline (`_rechain()`) is exactly right, since it
prevents "broken hash" from masquerading as "semantic refusal". Append-only
custody: respected — no ledger truncation outside explicit rollback vectors.
No touching real custody artifacts: **respected and load-bearing** — the plan
byte-authenticates the *real* issued artifact read-only (step 1) and does all
mutation on synthetic trees in tempdirs. Minimal additive edits: N/A (test-only
scope). No concerns here.

### (d) Test quality — one near-tautology, confirmed

- **T1 (blocking).** `test_d110_never_zero_allowance_is_embedded_once_in_all_three_verdicts`
  **cannot discriminate a broken implementation.** The fixture pins endpoint
  bounds alpha `0.025/0.026`, beta `0.027/0.028`, gamma `0.029/0.030` — every
  observed drift is `0.001`, and every one is below the `0.010818` screen. The
  applied allowance is therefore `0.010818` in all three windows, so the test
  passes identically against `max(drift, 0.010818)`, against the constant
  `0.010818`, and against `min(...)`. The one branch D-110 exists to protect —
  drift *above* the never-zero floor — is never taken.
- **T2.** `test_three_receipt_sessions_terminate_at_sequence_85` is
  construction-shaped: the plan chooses the API path that produces 85 and then
  asserts 85. It discriminates nothing about the path the operator will run.
- **T3.** Several universe tests ("supply the tuple", omit/add/duplicate) exercise
  the *guard on a caller-supplied candidate tuple*, not discovery. Only
  `test_candidate_discovery_never_invokes_loader_for_import_marked_observations`
  (a call-count spy — good design) is discovery-driven. There is no test proving
  the production path derives the universe from the snapshot without caller
  supply.
- Everything else is genuinely discriminating. The mutation-with-rechain
  discipline, the cross-window binding swap, the sibling-fork-with-valid-hash
  vector, and the T1-mismatch vector (internally consistent under a *different*
  T1) are the kind of vectors that catch real defects.

### (e) Scope discipline

Exhaustive and minimal, and **narrower than the memo** — the memo licensed
`tests/fixtures/calibration_live_three_window/**` (a glob); the plan commits to
exactly one JSON file plus one test module. That is the right direction. The only
scope defect is the missing NEEDS_SCOPE clause (G3).

### (f) What it misses that the register/memo require

- **M1. L5 by name.** The register: *"bracket selection can BORROW another
  window's receipts (global candidate scan; no runs_root/intended-pair binding)…
  U1 review MUST include this scenario as a regression vector."* U1's fix round
  added "L5 mandatory window/runs_root binding". U4 is the *integration*
  regression where three windows share one ledger — the exact topology L5
  described — yet no test names `runs_root`/`window_id` binding. The neighbor-
  substitution and cross-window-binding tests are adjacent but not the same
  assertion.
- **M2. No positive count-boundary oracle.** The operationally load-bearing fact
  is that the no-failure three-window campaign ends at **36 valid** — two short
  of the D-102 trigger. Nothing in the plan asserts this. It matters because any
  calibration retry, any fourth window (including Ed's optional 256-token prefill
  plan), or any extra fiducial crosses 38 and forces a successor mid-campaign.
- **M3. Per-window verdict issuance is never modelled.** Step 6 evaluates all
  three verdicts from a single sequence-85 (really 91) terminal snapshot. But the
  memo's §5A closing bookend runs *per window*: alpha's verdict is emitted at
  alpha's closeout, when the ledger holds only alpha's two live observations. The
  regression never proves (i) that alpha's verdict is issuable from its own
  terminal snapshot, nor (ii) that it remains re-verifiable at the campaign's
  terminal head after beta and gamma appended. If (ii) fails the campaign is
  broken and U4 will not have caught it.
- **M4.** No cross-window openness vector: beta's session left open while alpha's
  already-issued verdict is re-verified.

### U4 amendment list (paste-ready)

1. **Supersede the 85 oracle.** Build the fixture through the production writer
   path including `claim_bracket_session_slot` (as
   `scripts/validate_powermetrics_fiducial.py:409` does). Rename the test
   `test_three_windows_terminate_at_the_production_writer_sequence` and assert
   the derived value (3 sessions × 5 receipts = 15 → sequence **91**) *computed
   from a named module constant*, not a hardcoded literal. Additionally assert
   the two semantically load-bearing counts that are model-independent:
   `len(sessions) == 3` and `len(live_observations) == 6`. Record in
   `fixture_spec.json` that the memo's "85" is superseded by landed U1.
2. **Add a second, claim-free sequence variant only if the lead rules that the
   direct open/finalize path remains supported.** If it is not supported, delete
   the direct-API construction entirely; do not keep a fixture built by a path no
   operator will run.
3. **Make the D-110 allowance test discriminating (blocking).** Add a fourth
   synthetic window (or re-pin gamma) whose endpoint bounds give
   `observed_drift_s > 0.010818` — e.g. `0.029 / 0.045` (drift `0.016`). Assert
   `applied_allowance == observed_drift` on that window and
   `applied_allowance == 0.010818` on the sub-floor windows, in the same test, so
   `max()` is discriminated from a constant. Assert `embedding_count == 1` on
   both branches.
4. **Derive the synthetic acceptance artifact, do not patch it.** Emit it by
   running the same deterministic derivation used for D-116 over the 19 synthetic
   corpus members, so the synthetic parent's bound is reproducible from its own
   prior set. If that emitter is not importable within U4's write scope, raise
   `NEEDS_SCOPE` naming the emitter — do not ship an arithmetically inconsistent
   parent that the staged U2 successor tests must be written around.
5. **Run the whole happy path inside one temporary git repo with committed-pin
   enforcement ON.** Commit `configs/calibration/calibration_ledger_head.json`
   at each window boundary (mirroring the two real inter-night commits) and add
   `test_three_windows_require_two_intervening_committed_pin_advances` — a
   positive proof of the campaign's commit cadence, and the counterpart to the
   existing uncommitted-head refusal.
6. **Name L5 explicitly.** Add
   `test_candidate_under_another_windows_runs_root_cannot_bracket_this_window`:
   place a fully authentic, causal, same-epoch, fresh live observation under
   alpha's `runs_root` and attempt to bracket beta's science with it *absent* a
   binding (the original global-scan defect) and *with* a binding naming it.
   Both must refuse, and the refusal must cite the window/runs_root binding, not
   only the binding digest.
7. **Add the positive count-boundary oracle.**
   `test_no_failure_three_window_campaign_ends_at_36_valid_below_the_38_trigger`,
   asserting the trigger is *not* fired and that adding exactly two further valid
   same-epoch observations fires `corpus_doubles_from_19_to_38`. Comment the
   operational consequence (a fourth window or any calibration retry crosses it).
8. **Add per-window verdict issuance.**
   `test_alpha_verdict_issues_from_its_own_terminal_snapshot_and_re_verifies_at_campaign_terminal_head`
   — issue alpha's verdict at its own terminal head, then re-verify the identical
   verdict bytes against the campaign terminal snapshot after beta and gamma
   appended. Repeat for beta. This is the operational path; the single-snapshot
   evaluation is the memo's convenience, not §5A's procedure.
9. **Add cross-window openness.**
   `test_open_beta_session_does_not_invalidate_alphas_issued_verdict_but_blocks_a_campaign_terminal_pin`.
10. **Add a discovery-authority test.**
    `test_verdict_path_derives_candidate_universe_from_snapshot_without_caller_supply`
    — prove at least one production entry point does not accept a caller-supplied
    tuple, so the omit/add/duplicate guards are not the only universe defence.
11. **Name the doubled seam.** State the exact function being replaced by the
    deterministic bound-returning double, and add an assertion that the double is
    inactive in any test whose oracle is a bound/allowance value.
12. **Add the NEEDS_SCOPE clause:** "If the regression exposes a defect in U1/U2
    production code, early-return `NEEDS_SCOPE` naming the file and the failing
    vector. Do not widen scope, and do not weaken an oracle to make a test pass."
13. **Define `fixture_spec.json`'s authority:** it is *consumed* by the harness
    as the single source of the expected literals (sequences, counts, bounds,
    epoch, T1 vector); the test module must not restate any of them. Add
    `test_fixture_spec_is_the_sole_source_of_expected_literals` or drop the file
    from scope.

### U4 — three highest-risk gaps

1. **The regression will certify a ledger shape the three nights will not
   produce.** The plan routes around `claim_bracket_session_slot` to preserve the
   memo's "85". The production writer claims before finalizing, so the real
   campaign ledger interleaves claim receipts that U4 never exercises through
   discovery, binding, or verdict evaluation. This is the failure mode the whole
   unit exists to prevent, reintroduced by fidelity to a superseded literal.
   (Amendments 1, 2.)
2. **The D-110 never-zero test cannot fail.** Every fixture window has drift
   `0.001`, below the `0.010818` screen; the test passes against a hardcoded
   constant. D-110 cl.1 binds the never-zero allowance to *every mint under
   D-117*; U4 is where it is supposed to be proven, and as drafted it is not.
   (Amendment 3.)
3. **Per-window verdict issuance and the inter-night commit cadence are both
   unproven.** The plan evaluates from one terminal snapshot inside one process;
   the campaign issues three verdicts across three nights separated by committed
   pin advances. A defect in either — an alpha verdict that will not re-verify at
   the terminal head, or a pin-commit step that refuses — strands night two or
   three, which is exactly the charge the night-hardening register set.
   (Amendments 5, 8.)

---

# PLAN U8 — frozen-plan readiness validator + runbook §5A amendment

## Verdict: **REWORK**

The validator half is good work: the check table is comprehensive, the refusal
semantics are correctly fail-closed with no warning tier, the "no filesystem
writes / no repair" posture is right, the read-once-then-parse-and-hash-from-
captured-bytes rule closes a real TOCTOU class, and the plan directly and
competently closes the register's R6 (`readiness_launch_path_not_absolute` plus
a separate test for collection *and* whole-window verdict `--runs-dir`) and R7
(never-kill-verdict). The refusal to accept a self-declared acceptance JSON in
favour of U2's authenticated registry closes L4's core.

It is REWORK, not ACCEPT-WITH-AMENDMENTS, for three independent reasons, any one
of which is disqualifying:

1. The runbook amendment as specified **conflicts with four ratified sections of
   the document it edits** and violates the minimal-additive-edit invariant.
2. The plan **leaves the pre-flight calibration screen (§5B) untouched**, so the
   ratified runbook would carry two contradictory pre-science screens and a
   retry rule the frozen zero-retry ledger capability cannot represent.
3. The plan **is not executable**: it opens with "Begin implementation only
   after…" five unmet dependencies and closes with eight open questions, five of
   which are load-bearing design decisions (plan-tree contract, absolute-path
   syntax, fresh-root rule, reason-code closure, waiver canonical bytes). The
   charge's bar is "zero further design decisions." It fails that bar by its own
   admission.

### (a) Completeness — gaps

- **G1.** Five blocking dependencies (U1 final, U2 registry+probe, U5–U7 plan-tree
  and launch representation, reason-code unit landed, clean integration head) —
  of which U2, U5, U6, U7 do not exist and the reason-code unit is an *unratified
  candidate* (register: "Candidate small unit (U1.6) … Decide at the readiness
  gate"). Nothing in U8 can start.
- **G2.** Eight open questions, five design-bearing. Q2 (which artifact is the
  transitive hash closure), Q3 (literal argv vs expansion), Q4 (absent vs empty
  fresh root), Q6 (reason-code schema identity), and Q8 (waiver canonical bytes)
  each change the validator's code. Recommendations are offered but not ruled.
- **G3.** **The receipt has no custody destination.** The validator "performs no
  filesystem writes" and emits the receipt to stdout. Nowhere does the plan or
  the runbook amendment say where that receipt is written, that its SHA is
  recorded in §12 close-out, or that it is preserved as immutable window
  evidence. The PASS evidence for arming a claim window is, as drafted,
  ephemeral terminal output.
- **G4.** **The receipt is never bound to the arm.** There is no timestamp, no
  max-age/TTL, and no requirement that the bracket-session capability receipt
  record `readiness_receipt_sha256`. An operator can validate, then arm an hour
  later after any state change. The memo explicitly requires the opposite: the
  order manifest must carry "**arm-time attachment slots for the readiness
  record**, session capability, and actual receipt identifiers."
- **G5.** **The readiness record has no provenance requirement.** It is an
  arbitrary absolute path plus an operator-supplied `--expected-record-sha256`.
  Both are under the operator's (or an agent's) hand; regenerating the record and
  its expected SHA together passes. A fail-closed validator is only as strong as
  the provenance of what it validates.
- **G6.** Exit `2` is overloaded across malformed arguments, check failures, and
  "normalized internal refusal." The D-116 consumer gauntlet already caught
  "exit-3 masking" as a blocker; this reintroduces the class. An operator cannot
  distinguish a flag typo from "the machine is not ready."
- **G7.** The `readiness_*` code namespace (~30 new codes) has no declared home.
  `docs/phase_2/refusal_scope_spec.md` is "the ONE home for reason-code scoping";
  S2 defaults unknown codes to GLOBAL (safe), and S4 makes any S1 scope move a
  mandatory cold gate. The plan neither registers the namespace nor states that
  readiness codes are out of S1's domain. This is the register's URGENT "shadow
  taxonomy" defect, reproduced.
- **G8.** The validator runs at §5A step 1, *before* the clock/network-time step
  (step 4). Nothing re-verifies network-time-off, the settle, or absence of a
  pending time sync after that step. See M2 below.

### (b) Correctness against the memo/runbook/decisions

- **Divergence from memo §5A.** Memo step 3: *"Correct the clock against the
  trusted source, record the correction and `usingnetworktime` state, turn
  network time off, **and settle for at least 180 seconds**."* The plan's opening
  step 4 is "Correct the clock against the trusted source; record prior
  network-time state; disable network time" — the 180-second settle is **dropped
# Plan-factory dispositions (magistrate, 2026-08-07)

## BINDING SYSTEMIC RULE (adopted from the U4/U8 examination)

**Every numeric or structural oracle a downstream plan takes from the
D-117 design memo MUST be re-derived from the LANDED branch, and any
divergence recorded in the plan.** The memo is a design document written
before U1 existed; U1 superseded some of its literals. Confirmed instance:
the memo's "ideal terminal sequence is 85 **under the proposed
three-receipt session model**" — landed U1 uses FIVE receipts per window
(session capability, exclusive slot claim, pre finalization, post
finalization, terminal pin path), so the real no-failure terminal sequence
is 91, and a regression pinned to 85 would certify a ledger shape the
three nights will never produce. This rule binds U4-U10 and any plan
derived from the memo.

## U4 — synthetic three-window regression: ACCEPT WITH AMENDMENTS

Strong enumeration (all 7 proof obligations + 12 refusal-vector bullets
decomposed into 30 named tests; every named API and all 16 refusal codes
verified real on the landed branch). Blocking amendments before landing:

1. **Supersede the sequence-85 oracle** — drive the happy path through the
   PRODUCTION writer path including the exclusive slot claim; assert the
   derived value (91) from a module constant plus model-independent counts
   (3 sessions, 6 live observations).
2. **The D-110 never-zero test currently CANNOT FAIL** — every fixture
   drift is 0.001, below the 0.010818 screen, so the max() branch is never
   exercised; it passes against max(), against the bare constant, and
   against min(). Add a window with drift > 0.010818 and assert BOTH
   branches. This is the one clause D-110 exists to protect.
3. Derive the synthetic acceptance artifact through the D-116 emitter (or
   NEEDS_SCOPE it) — do not ship a parent whose bound is not derivable
   from its own prior set.
4. Name L5 explicitly (a test that a candidate under another window's
   runs_root cannot bracket this window, with and without a binding).
5. Per-window verdict issuance + committed-pin cadence across window
   boundaries (the nights are three separate closeouts, not one snapshot).
6. Add the positive count oracle (no-failure campaign ends at 36 valid,
   two short of the 38 trigger) + a NEEDS_SCOPE clause.
Remaining amendments 7-13 in OPUS-EXAM-U4-U8.md are adopted as written.

## U8 — readiness validator + runbook amendment: REWORK

The validator half is good (fail-closed with no warning tier, TOCTOU-safe
read-once-then-hash, closes register R6 and R7, resolves acceptance via
U2's registry). It is REWORKED for three independent reasons:

1. **The runbook edit would put contradictory normative instructions into
   a ratified operator document read at 2 a.m.**: §5B still licenses a
   cause-removal retry that a two-slot session CANNOT represent; the plan
   restates §8/§9/§11 orderings inside §5A (a clock-stabilization
   section); and it DROPS the mandatory 180 s settle from the very
   sequence its test would freeze. Restructure as additive
   "### D-117 §nn amendment" blocks per the runbook's own convention, and
   reconcile §5B (zero retries) or NEEDS_RULING it.
2. **The readiness gate is unbound and uncustodied** — the receipt goes to
   stdout and nowhere else, has no timestamp/TTL, is never referenced by
   the capability receipt, and the record's provenance plus its expected
   SHA are both operator-supplied. Every individual check is fail-closed;
   the gate as a whole is not.
3. **It is not implementable yet** (five unmet dependencies, five
   design-bearing open questions) and sequencing it now would invert the
   memo's dependency order, forcing U5-U7 to match a plan-tree contract
   invented by U8.

**Next action for U8 is NOT an implementation round.** It is: the two
rulings (zero-retry semantics; whether the readiness reason codes enter
the ratified refusal spec's S1 domain — an S4 cold-gate move if so), then
the U5-U7 plan-tree/launch-manifest contract.

## Note on the speculative implementations

U2/U4/U8 speculative implementations were launched BEFORE this
examination. They are evidence for the council, not landing candidates.
U4's output must be re-gated against amendments 1-6 above; U8's output is
superseded by the REWORK verdict and must not be landed on the runbook.

## PROBES — ACCEPT WITH AMENDMENTS (22 named; full list in OPUS-EXAM-PROBES-PROSE.md)

Probe A (spec-decode pilot) verified executable in principle: every cited
mlx_lm CLI flag exists at the pin, the byte-identity check is PROVABLY
sound (acceptance is exact-match; --temp 0 gives argmax before any
sampler stage). Blocking amendments:
1. `$OUT` is referenced but never assigned — the commands as written fail
   on paste. (A1)
2. The decision rule can fire on contradictory evidence ("either 7B
   workload" closes even if the longer run shows a win) — make 7B/512
   governing; a split between lengths is INCONCLUSIVE. (A2)
3. **The chosen prompt is near-zero-entropy** ("count 1 to 1000"), so a
   0.5B draft hits near-ceiling acceptance: the probe measures spec
   decode's BEST case, the opposite of what a cheap kill-gate needs. Add
   a frozen free-prose governing cell; keep the list prompt as a labelled
   upper bound. (A3)
4. **Write the inference assumption down**: E = P̄·t, so CLOSE is licensed
   only under P̄_on >= R·P̄_off (near-certain, since spec-on does K draft
   forwards plus one (K+1)-position target forward per emitted token) —
   and state the converse, that a throughput WIN does not imply an energy
   win. (A4)
5. Fix the K-scope inconsistency (one K=3 result cannot close a
   K-manipulation program) and record the generation_tps first-token
   timer bias (~2% at N=128; conservative for CLOSE, anti-conservative
   for SURVIVES). (A5, A8)

Probe B (GPU cadence): the gate citation points at the WRONG DEVICE — the
cited line is in the NVIDIA 3050 section; the 3080 Ti section carries
R-006 (schedule only after Stage 3.0 verdicts + rehearsed runbook), so
the gate is not merely "does Ed have access" and whether a non-claim
characterization sits inside R-006 is a cold-gate question. Also: declare
the emitted bound an explicit UPPER bound (NVML cannot separate DVFS ramp
from sensor filter), and re-price ~1.5x (thermal re-admission is not
free). Note for the funding decision: a PASS at 100 ms already forbids
any stage shorter than ~400 ms under the plan's own rule — a boundary
PASS may be operationally useless.

## RESULTS_PROSE — examination VOID (stale input), re-run ordered

The examiner read the pre-fix truncated copy and reported "no
deliverable". Lead-verified against the completed file: the deliverable
EXISTS (35 [VALUE] placeholders across the three variants plus the §6
shell). Its derived ACCEPTANCE CONTRACT is adopted regardless and binds
the re-examination and the eventual prose:
- **P1** no summed-threshold leakage: F_cell + B_claim is DISCLOSURE
  only; the interval is never compared to the sum.
- **P5/P6** "not resolvable" is never written as "no difference"; and
  Variant B must SPLIT into B1 (floor-gate refusal) and B2
  (direction-gate refusal) because the sentences differ.
- **P7** Variant C's natural framing is FALSE: under D-095's
  cross_stack_armwise_max.v1, losing one floor window makes the contrast
  NOT EVALUABLE, not "partially claimable".
P1 and P7 are the two easiest variants to write fluently and the hardest
to write correctly; the summed-threshold error reads as doctrine
compliance to a skimming reviewer.

## REASON-CODE PLUMBING — ACCEPT WITH AMENDMENTS + two magistrate rulings

Verified good by the examiner against primary evidence: append-compatibility
is real (every reader is field-selective; rows lacking a field are already a
first-class case), the spec amendment is correctly treated as needing
ratification, and the backfill is custody-safe (append-only annotations keyed
by target row hash, conflicts refuse). Blocking amendments:

1. **PIN THE FIELD PLACEMENT: top-level sibling, NOT inside
   `idle_admission_core`.** The latter enters the six-key semantic-identity
   projection and would turn every same-basis re-verdict into
   `whole_window_verdict_conflict`. And the identity projection itself is
   NOT to be edited to accommodate the field — test the key list to freeze
   that.
2. **Golden characterization test BEFORE the refactor**: pin the existing
   `idle_admission_core_verdict` output by canonical sha256 first; all 13
   proposed tests cover only the new field, so the old behavior is currently
   unguarded days before the nights.
3. **Operational trap to encode**: replay verification against a HISTORICAL
   runs root APPENDS a campaign-log row and thereby breaks the issued
   artifacts' whole-file `campaign_log_sha256` pin. Any backfill or replay
   must work on copies, never on a pinned root.

**MAGISTRATE RULING A (the examiner flagged this as not lieutenant-decidable):
may the plumbing land ahead of the spec amendment? YES, SPLIT.** The CODE
plumbing (top-level, additive, append-compatible) may land ahead — it captures
evidence without changing any ratified semantics, and the three nights are
what make it urgent. The SPEC AMENDMENT (bringing the shadow codes into the
ratified spec's S1 domain) is a separate ratification and MUST NOT be assumed
by the code: until ratified, the new reason codes live in an explicitly
declared namespace OUTSIDE S1, frozen in one module tuple with an equality
test. Landing the code does not pre-empt the ratification; it must not read
as having done so.

**GOVERNANCE HOLE FOUND (record it, do not paper over it):** the ratified
`docs/phase_2/refusal_scope_spec.md` cites D-083 as its authority, but D-083
is the B3 disclosure ruling, and the decision log contains NO row for the
refusal-scope spec at all. The spec is operating as a ratified ONE-home with
no ledger entry behind it. This needs an Ed/cold-gate ruling on its actual
status before any S1-domain move is attempted — it is now item 8 on the
rulings list.

## PRICE-OF-NEVER-ZERO — ACCEPT WITH AMENDMENTS + one magistrate ruling

The arithmetic is VERIFIED CORRECT — the examiner reproduced the operator
order numerically against the retired mint (corner-widen -> guard ->
per-component family-matched allowance -> max). Blocking amendments:

1. **PAPER COLLISION (blocker).** `draft-v1.md` already has a section
   "Measured, never-zero drift allowance" — and that is the NEG-8 ENERGY
   allowance. The TIMING rule (D-102 pin 3) is introduced in §3. The plan
   titles its subsection "the never-zero rule" and hangs the forward
   reference off §4, so it would quantify one allowance while appearing to
   quantify the other — and that error survives into print. Retitle to name
   the TIMING allowance explicitly and attach it to §3's rule.
2. Read `0.010818` from the issued acceptance artifact rather than
   hardcoding it (this is the L4 defect class recurring).
3. Probe the re-reduction seam FIRST; if it will not take an external bound,
   the failure mode is a desk-script reimplementation of floor arithmetic
   feeding the paper — which is unacceptable.
4. The sensitivity artifact must be schema-INCOMPATIBLE with a floor artifact
   (it can never be mistaken for one); prefill cells have no diagnostic
   analogue (mint1 is decode-only) and wait on U3/U10.

**MAGISTRATE RULING B: may a counterfactual verdict appear in the paper? NO.**
The paper may report the floor ARITHMETIC with and without the never-zero
timing bound — that is a computed quantity from custodied inputs. It must NOT
tabulate a "verdict without" column: a verdict is an ISSUED artifact, and a
counterfactual verdict has no artifact behind it. State the arithmetic delta
and what it would imply; never render a verdict that was never issued.

## BINDING PORTFOLIO RULES (adopted from the quant/MoE re-examination)

**R1 — No P2 or stretch-paper work may touch the mint / pinset /
`detection_floor` file set until U10 closes.** Both second-paper plans
independently rediscovered the same blocker; the cardinality limits are
hardcoded in THREE places (schema_v2.json, the generalized mint, AND the
consumer `detection_floor.py`, which additionally requires per-component
roles exactly {"decode","prefill"} and pins cross_stack_armwise_max.v1 as
a constant). A three-decode-cell aggregate therefore fails on cardinality
AND on role pairing. Touching that file set before U10 puts the capstone's
nights hostage to a second paper.

**R2 — Every kill threshold is expressed as a MULTIPLE OF A PROJECTED
FLOOR, never as a joule literal and never at 1x.** Projection basis: the
one measured precedent, 13.998037 J comparative on a 192.386233 J member
mean = 7.3% of member energy. This supersedes every "~5 J" and every bare
joule gate in the portfolio's plans.

## QUANTIZATION (P2) — REWORK (bounded), and the night count changes

The plan has exactly two kill gates and NEITHER can return a decision:
- **Gate 1 cannot PASS.** The existing Q4 artifact stores every
  non-quantized parameter as F16 and its config carries NO "mode" key;
  the plan converts at `--dtype bfloat16`, and mlx_lm 0.31.3 always writes
  `"mode": "affine"`. Byte-identity with the existing artifact is
  impossible BY CONSTRUCTION on two independent grounds, before converter
  packing even enters. Fix: a three-way Q4-EQUIVALENCE verdict (not
  byte-identity) plus a fourth `--dtype float16` conversion arm.
- **Gate 2 cannot DECIDE.** With five off-window ABBA blocks the interval
  is too wide for either branch to fire; "hold for Ed" is the near-certain
  outcome. Fix: >=3x projected-floor Go rule (R2) and a FAIL_PRECISION
  rule.
- Move the 4-hour occupancy projection INTO Gate 1 (computable there from
  the memo's 92.7 s / 147 min / 188.4 min structure) — one to two months
  earlier than currently scheduled.
- **NIGHT COUNT: 3 -> 4.** This is a portfolio number in ADJUDICATION, so
  it is Ed's to accept, not an amendment I can make in place.
- Correction to a carried fact: the `--hf-path/--revision` unexecutability
  does NOT apply here — this plan resolves the SHA via the API and passes
  a local snapshot dir, which is the correct workaround.

## MoE (STRETCH) — ACCEPT WITH AMENDMENTS

Technically the stronger document: every source citation verified exactly
against the INSTALLED runtime (block L110, top_k L117, inds L131, scores
L132, switch_mlp L136), the metadata-first-line check verified against
real on-disk structure, and the disk precondition correctly FAILED against
real numbers. Gates DG2/DG3/DG4 genuinely kill. Structural amendments:
1. **No effect-size gate exists anywhere in DG1-DG4** — the most likely
   killer sits BEHIND a 32-48 h runtime fork. Add DG2.5: projected-floor
   sizing at >=3x, before the fork.
2. Move the active-parameter-ratio check into DG1 (computable from the
   remote index file with NO 17 GB download) — and note it is likely
   marginal, since the dense partner is tied-embeddings and the MoE is not.
3. **"Two-night minimum" is arithmetically unreachable** for three floored
   arms (150 members against Alpha's 50 at 188.4 min). Honest number: 4.
- Correction to a carried fact: the ~34 GB cache-then-mirror doubling does
  NOT apply (hub 1.22.0 renames into place on the same filesystem); the
  28 GiB / 97%-full disk finding STANDS and the second 17.2 GB mirror
  remains impossible on that volume.
codex
# U4 implementation plan — synthetic three-window live-ledger regression

## Baseline and constraints

Implement against U1 commit `f665dd4` (`impl/d117-u1-ledger-session` and the local `origin/…` ref both point there). A fresh remote lookup was impossible because network DNS is unavailable; no fetch was performed because this was explicitly read-only.

U4 remains logically downstream of U1 and U2. The non-successor portion can be prepared against U1; U4 must not merge with successor tests still skipped.

## Exact `WRITE_SCOPE`

Only:

- `tests/fixtures/calibration_live_three_window/fixture_spec.json`
- `tests/test_calibration_live_three_window.py`

No production modules, configuration, registry, bookkeeping, generated state, or existing tests are in scope.

## Fixture specification

`fixture_spec.json` will contain:

- Schema/version identifier for the U4 fixture.
- The expected production issued-anchor facts:
  - acceptance artifact SHA-256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`;
  - cutoff sequence `76`;
  - cutoff head `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`;
  - inventory `{valid: 30, systematic-invalid: 2, ordinary-invalid: 6}`.
- Exact six-field epoch copied from the issued artifact.
- One complete ten-field T1 vector:
  - `hardware_model`
  - `os_build`
  - `powermetrics_sha256`
  - `sampling_interval_ms`
  - `anchor_method_version`
  - `mlx_version`
  - `pulse_protocol_id`
  - `power_policy`
  - `estimator_revision`
  - `protocol_sha256`
- Three explicit window records: `alpha`, `beta`, `gamma`, each with unique session, window, plan, evidence-root, and runs-root suffixes.
- Window timing far enough apart to make causal/stale mutations unambiguous:
  - alpha science `[1_000_000, 1_000_100]`, endpoints `999_990/1_000_110`;
  - beta `[2_000_000, 2_000_100]`, endpoints `1_999_990/2_000_110`;
  - gamma `[3_000_000, 3_000_100]`, endpoints `2_999_990/3_000_110`.
- Endpoint decimal bounds below the issued range ceiling and with drift below the `0.010818` screen:
  - alpha `0.025/0.026`;
  - beta `0.027/0.028`;
  - gamma `0.029/0.030`.
- Expected capability/finalization sequences:
  - alpha `77/78/79`;
  - beta `80/81/82`;
  - gamma `83/84/85`.
- Expected candidate count `6`, imported candidate count `0`, final sequence `85`, and allowance literal `0.010818`.

Identifiers must be explicitly synthetic; they must not pre-empt U5–U7’s final campaign identifiers.

## Construction algorithm

`tests/test_calibration_live_three_window.py` will define a reusable `FixtureHarness`.

1. Load and byte-authenticate the checked-in issued acceptance artifact. Assert its exact SHA, sequence-76 cutoff, 38-member prior set, and 30/2/6 inventory.

2. Materialize 38 synthetic custody directories in a temporary checkout. Preserve the issued artifact’s attempt IDs and dispositions. Each directory gets deterministic:
   - `raw/powermetrics.plist`
   - `events.jsonl`
   - `power_trace.csv`
   - `instrument_evidence.json`
   - `manifest.json`

3. Build the historical disposition table and custody manifest, then call the public `prepare_historical_import`/`bootstrap_historical_import` path. Assert:
   - 76 receipts;
   - alternating historical reservation/finalization semantics;
   - 38 content-distinct observations;
   - 30 valid, two systematic-invalid, six ordinary-invalid;
   - every observation is import-marked;
   - the chain and generated sequence-76 head pin authenticate.

4. Construct a structurally valid synthetic issued acceptance artifact:
   - clone the production artifact’s policy/numeric fields;
   - bind its cutoff to the synthetic sequence-76 head;
   - replace the prior set with the 38 generated observations;
   - replace the 19 derivation-corpus identities/hashes with the first 19 generated valid members while retaining the original bound lexemes and arithmetic;
   - recompute `derivation_sha256`;
   - assert `_valid_acceptance_bound` before use.
   
   Patch only the acceptance-loader boundary to supply this artifact. Do not patch ledger loading, candidate discovery, binding validation, or bracket evaluation.

5. For each window, starting from the current pinned head:
   - call `append_bracket_session_receipt` with exactly two immutable slots;
   - call `finalize_bracket_session_slot` directly for `pre`, then `post`;
   - do not emit optional writer-claim receipts, preserving the memo’s three-receipt/session sequence model;
   - obtain the terminal pin through `terminal_head_pin_for_session`;
   - load a pinned snapshot with the sequence-76 baseline;
   - build the window binding with `build_calibration_bracket_binding`;
   - advance the synthetic committed pin before opening the next session.

6. After gamma, load exactly one immutable sequence-85 snapshot. Call `discover_calibration_candidates` once and reuse that exact six-candidate tuple and snapshot for all three evaluations.

7. Candidate custody remains fully hash-authenticated. Only the raw-physics refit is replaced with a deterministic test double returning each evidence file’s exact decimal bound; this keeps receipt, manifest, evidence, content-ID, epoch, T1, protocol, and path authentication live.

8. Structural mutation tests use a common `_rechain()` helper that recomputes sequence, predecessor, and receipt digests. This distinguishes semantic refusal from trivial broken-hash refusal.

## Named proof-obligation tests

| Test | Required proof |
|---|---|
| `test_issued_prefix_has_exact_76_receipt_38_observation_30_2_6_semantics` | Both the production anchor and generated prefix carry the ruled issuance shape. |
| `test_final_snapshot_discovers_exactly_six_live_and_zero_imported_candidates` | Six live candidates; no import-marked observation reaches candidate loading. |
| `test_alpha_beta_gamma_bind_only_their_own_pre_post_pairs` | Each binding resolves to its own two attempt/content/receipt digests. |
| `test_all_six_live_endpoints_are_same_epoch_causal_fresh_protocol_and_t1_valid` | Exact epoch/T1/protocol equality and causal/fresh timing for every endpoint. |
| `test_neighboring_endpoint_cannot_substitute_for_any_bound_endpoint` | Replacing either endpoint with any of the other five candidates refuses. |
| `test_all_three_verdicts_consume_same_complete_final_candidate_universe` | All verdicts pass only with the same final snapshot and complete six-candidate tuple; discovery occurs once. |
| `test_three_receipt_sessions_terminate_at_sequence_85` | Receipt events and sequences are exactly `76 + 3 × 3 = 85`. |
| `test_d110_never_zero_allowance_is_embedded_once_in_all_three_verdicts` | All three results record `max(drift, 0.010818)`, value `0.010818`, `embedding_count == 1`, and the correct operative decimal. |

## Named refusal-vector tests

### Import boundary

| Test | Setup and oracle |
|---|---|
| `test_import_marker_removal_refuses_authenticated_issuance_prefix` | Convert one fully re-chained import reservation/finalization pair to ordinary live events. Evaluation must refuse with `calibration_ledger_baseline_missing`. |
| `test_import_candidate_leakage_refuses_complete_universe_check` | Add a candidate derived from an import observation to the supplied tuple. Expect `calibration_ledger_off_ledger_artifact`. |
| `test_candidate_discovery_never_invokes_loader_for_import_marked_observations` | Spy on the observation-to-candidate loader; it must be called exactly six times, all after sequence 76. |

### Session/finalization integrity

| Test | Setup and oracle |
|---|---|
| `test_missing_session_or_finalization_receipt_refuses` | Subtests remove a capability, pre finalization, or post finalization and fully re-chain. Require session conflict/open refusal and no passing evaluation. |
| `test_duplicate_session_or_finalization_receipt_refuses` | Duplicate an open receipt and, separately, a finalization. Expect `calibration_ledger_bracket_session_conflict`. |
| `test_reordered_finalization_receipts_refuse` | Put post before pre and re-chain. Expect session conflict. |
| `test_conflicting_session_or_finalization_identity_refuses` | Change session identity, reserved attempt, custody, or plan hash on a later event and re-chain. Expect session conflict. |
| `test_open_session_refuses_claim_evaluation_and_terminal_pin` | Stop after a valid pre finalization. Snapshot contains `calibration_ledger_bracket_session_open`; terminal-pin creation and evaluation both refuse. |
| `test_abandoned_slot_without_governed_abort_refuses` | Finalize pre as abandoned but omit `abort_bracket_session`. The session remains open and cannot yield a terminal pin or candidate. |

### Head and chain authority

| Test | Setup and oracle |
|---|---|
| `test_physical_head_pin_mismatch_refuses` | Keep the pin at 76 while the physical chain reaches 85. Expect `calibration_ledger_head_mismatch`. |
| `test_rollback_from_pinned_terminal_head_refuses` | Pin sequence 85, truncate the physical chain to 84. Expect `calibration_ledger_rollback`. |
| `test_sibling_fork_refuses_even_when_pin_names_fork_tip` | Append a correctly hashed sibling transition and pin that tip. Expect `calibration_ledger_chain_conflict`. |
| `test_uncommitted_terminal_head_pin_refuses` | In a temporary Git repo, commit the sequence-76 pin, advance it to 85 without committing, and load with committed-pin enforcement. Expect `calibration_ledger_head_uncommitted`. |

### Complete observation universe

| Test | Setup and oracle |
|---|---|
| `test_omitted_registered_observation_refuses` | Remove one of six candidates from the supplied tuple. Expect `calibration_ledger_off_ledger_artifact`. |
| `test_added_registered_observation_invalidates_frozen_six_candidate_universe` | Append and pin a seventh authentic valid live observation, then supply the old six. Expect off-ledger refusal. |
| `test_duplicate_supplied_observation_refuses` | Duplicate one candidate while retaining tuple length. Expect off-ledger refusal from the duplicate/cardinality guard. |
| `test_off_ledger_observation_refuses` | Add a well-formed candidate with no receipt. Expect off-ledger refusal. |
| `test_content_substituted_observation_refuses` | Keep attempt/receipt identity but replace content or artifact hashes. Expect off-ledger refusal. |

### Binding integrity

| Test | Setup and oracle |
|---|---|
| `test_missing_bracket_binding_refuses` | Evaluate a session-backed window with no binding. Expect `calibration_bracket_binding_missing`. |
| `test_tampered_bracket_binding_refuses` | Alter an endpoint or identity without updating the binding digest. Expect `calibration_bracket_binding_invalid`. |
| `test_swapped_bracket_binding_endpoints_refuse` | Swap pre/post and recompute the outer digest. Exact role comparison must still reject it. |
| `test_cross_window_bracket_binding_refuses` | Supply alpha’s authentic binding to beta, and vice versa. Expect binding-invalid refusal. |

### Endpoint eligibility

| Test | Setup and oracle |
|---|---|
| `test_noncausal_bound_endpoint_refuses` | Move a bound pre after science start or post before science end; rebuild evidence and receipts. Expect bracket-missing/binding refusal, never neighbor substitution. |
| `test_stale_bound_endpoint_refuses` | Place a causal endpoint beyond `MAX_AGE_S`. Expect `instrument_calibration_stale`. |
| `test_t1_mismatched_bound_endpoint_refuses` | Make reservation, evidence, and receipt internally consistent under a different T1 value while science keeps the original T1. Expect `instrument_calibration_bracket_missing`. |
| `test_non_v3_protocol_endpoint_refuses` | Make one authentic endpoint v2 rather than the claim-bearing v3 protocol. Expect bracket-missing refusal. |
| `test_identity_epoch_mismatch_refuses` | Change one acceptance identity field in the evaluated science binding. Expect `calibration_acceptance_bound_stale` with that field listed. |
| `test_systematic_live_observation_refuses_under_prior_artifact` | Classify one live observation systematic-invalid. Expect stale/refusal and the systematic trigger; no successor is consulted. |

### D-102 triggers available under U1

| Test | Setup and oracle |
|---|---|
| `test_range_expanding_live_observation_refuses_prior_artifact_and_requires_successor` | Set one valid endpoint above `0.03355875667989999`. The prior artifact must become stale with `new_valid_same_identity_capture_expands_observed_range`. |
| `test_observation_count_at_38_refuses_prior_artifact_and_requires_successor` | Extend the base 30+6 valid inventory with two further authenticated valid same-epoch observations. At 38, require `corpus_doubles_from_19_to_38` and stale refusal. |

## Tests staged behind U2

Keep these methods in the same module to preserve the exact U4 write scope. While U2’s public API/design brief is unavailable, mark them with an explicit `unittest.skip` reason. Imports of U2 APIs must occur inside the skipped methods so the module remains importable.

Before U4 merges, U2 must land, the skips must be removed, and all five tests must pass:

- `test_range_expanding_live_observation_passes_only_with_authenticated_successor`
  - Judge the range expander under the prior artifact, stop before science, build/register a successor over the complete governed prefix, finalize the session, and prove the final bracket passes only under that successor.

- `test_count_boundary_passes_only_with_authenticated_successor`
  - Reach exactly 38 valid same-epoch observations, refuse the prior artifact, then prove a deterministic registered successor restores eligibility.

- `test_successor_cannot_absorb_systematic_observation_as_valid`
  - Attempt to include or relabel a systematic observation in the successor corpus. U2 must refuse; a successor cannot launder it.

- `test_successor_refuses_omitted_authenticated_prefix_observation`
  - Omit any import or finalized live observation at or before the successor cutoff, recompute otherwise self-consistent bytes, and require registry/validator refusal.

- `test_successor_refuses_changed_authenticated_prefix_observation`
  - Change content ID, disposition, epoch, attempt identity, or receipt/cutoff identity in the authenticated prefix and require refusal.

Use skip-marking rather than a separate module: a second module is outside the frozen U4 scope and makes it easier for the canonical suite to overlook the staged vectors. Skips are temporary branch state, not an acceptable merged U4 outcome.

## Verification

During pre-U2 staging:

```sh
python3 -m unittest tests.test_calibration_live_three_window
```

Expected: 38 active tests pass and exactly five U2-dependent tests skip.

After U2 lands:

```sh
python3 -m unittest tests.test_calibration_live_three_window
python3 -m unittest tests.test_calibration_live_three_window
python3 -m unittest discover -s tests
```

Acceptance:

- 43 U4 tests pass;
- zero U4 skips remain;
- two consecutive focused runs produce identical semantic receipts, bindings, successor bytes, and trigger outcomes for the same fixture root;
- canonical suite passes;
- no production or bookkeeping files changed.

## Estimated size

- `fixture_spec.json`: approximately 180–300 lines.
- Test harness and 43 tests: approximately 1,100–1,450 lines.
- Total: approximately 1,300–1,750 lines.
- Focused runtime target: under 20 seconds by constructing one pristine base tree per class and copying it for mutation tests.

## Risks and mitigations

- **Sequence-85 versus U1 claim receipts:** U1 added optional persistent slot-claim events. Exercising those through the production writer would yield five receipts per window and terminate at 91. This plan follows the memo’s explicit 85 oracle by calling the public open/finalize APIs directly. Existing U1 tests retain claim/concurrency coverage.
- **Synthetic acceptance authentication:** synthetic historical evidence cannot reproduce the off-repo production content hashes. U4 therefore validates the real issued artifact separately, then uses a structurally validated synthetic issued artifact at the loader boundary. All downstream ledger, custody, candidate, binding, and evaluation checks remain live.
- **Mutation tests becoming trivial:** every semantic mutation is re-chained and re-pinned unless the vector specifically targets hashes or heads.
- **Reason stacking:** tests assert the exact refusal when only one contract should fire; deliberately compound malformed cases assert the required primary taxonomy plus a failed verdict.
- **U2 API uncertainty:** successor semantics and oracles are frozen above, but the mechanical adapter cannot be completed until the U2 brief/public API lands.
- **Runtime from 44 custody trees:** build the pristine fixture once and copy it per test; do not regenerate all physics artifacts for every vector.

## Lead questions

1. Confirm that sequence 85 is the normative U4 oracle and that optional U1 slot-claim receipts are intentionally excluded from this semantic regression. Recommended: keep 85 here and add any claim-enabled production-path integration check under U1’s writer tests, not U4.
2. Ratify the successor corpus rule: all content-distinct, valid, same-epoch observations through the authenticated cutoff; systematic, ordinary-invalid, abandoned, unresolved, and duplicates remain recorded but excluded.
3. Confirm that U4 may use the structurally valid synthetic issued artifact described above rather than requiring the unavailable off-repo production ledger/custody bytes.
4. Decide whether the five temporary successor skips may exist on an intermediate U4 branch. Recommended: yes during staging, but never in the merged U4 commit.
5. Confirm `f665dd4` remains the intended U1 integration base, since a fresh origin lookup was unavailable in this read-only environment.
tokens used

exec
/bin/zsh -lc "git show origin/main:docs/process_traces/2026-08-07-plan-factory/MAGISTRATE-DISPOSITIONS.md | rg -n -C 8 'FIX-[A-F]|U4' && git show origin/main:docs/process_traces/2026-08-07-plan-factory/OPUS-EXAM-U4-U8.md | rg -n -C 5 'T1 \\(blocking\\)|M1\\.|M2\\.|M3\\.|U4 amendment list'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
1-# Plan-factory dispositions (magistrate, 2026-08-07)
2-
3:## BINDING SYSTEMIC RULE (adopted from the U4/U8 examination)
4-
5-**Every numeric or structural oracle a downstream plan takes from the
6-D-117 design memo MUST be re-derived from the LANDED branch, and any
7-divergence recorded in the plan.** The memo is a design document written
8-before U1 existed; U1 superseded some of its literals. Confirmed instance:
9-the memo's "ideal terminal sequence is 85 **under the proposed
10-three-receipt session model**" — landed U1 uses FIVE receipts per window
11-(session capability, exclusive slot claim, pre finalization, post
12-finalization, terminal pin path), so the real no-failure terminal sequence
13-is 91, and a regression pinned to 85 would certify a ledger shape the
14:three nights will never produce. This rule binds U4-U10 and any plan
15-derived from the memo.
16-
17:## U4 — synthetic three-window regression: ACCEPT WITH AMENDMENTS
18-
19-Strong enumeration (all 7 proof obligations + 12 refusal-vector bullets
20-decomposed into 30 named tests; every named API and all 16 refusal codes
21-verified real on the landed branch). Blocking amendments before landing:
22-
23-1. **Supersede the sequence-85 oracle** — drive the happy path through the
24-   PRODUCTION writer path including the exclusive slot claim; assert the
25-   derived value (91) from a module constant plus model-independent counts
--
33-   NEEDS_SCOPE it) — do not ship a parent whose bound is not derivable
34-   from its own prior set.
35-4. Name L5 explicitly (a test that a candidate under another window's
36-   runs_root cannot bracket this window, with and without a binding).
37-5. Per-window verdict issuance + committed-pin cadence across window
38-   boundaries (the nights are three separate closeouts, not one snapshot).
39-6. Add the positive count oracle (no-failure campaign ends at 36 valid,
40-   two short of the 38 trigger) + a NEEDS_SCOPE clause.
41:Remaining amendments 7-13 in OPUS-EXAM-U4-U8.md are adopted as written.
42-
43-## U8 — readiness validator + runbook amendment: REWORK
44-
45-The validator half is good (fail-closed with no warning tier, TOCTOU-safe
46-read-once-then-hash, closes register R6 and R7, resolves acceptance via
47-U2's registry). It is REWORKED for three independent reasons:
48-
49-1. **The runbook edit would put contradictory normative instructions into
--
66-
67-**Next action for U8 is NOT an implementation round.** It is: the two
68-rulings (zero-retry semantics; whether the readiness reason codes enter
69-the ratified refusal spec's S1 domain — an S4 cold-gate move if so), then
70-the U5-U7 plan-tree/launch-manifest contract.
71-
72-## Note on the speculative implementations
73-
74:U2/U4/U8 speculative implementations were launched BEFORE this
75-examination. They are evidence for the council, not landing candidates.
76:U4's output must be re-gated against amendments 1-6 above; U8's output is
77-superseded by the REWORK verdict and must not be landed on the runbook.
78-
79-## PROBES — ACCEPT WITH AMENDMENTS (22 named; full list in OPUS-EXAM-PROBES-PROSE.md)
80-
81-Probe A (spec-decode pilot) verified executable in principle: every cited
82-mlx_lm CLI flag exists at the pin, the byte-identity check is PROVABLY
83-sound (acceptance is exact-match; --temp 0 gives argmax before any
84-sampler stage). Blocking amendments:
130-mutation on synthetic trees in tempdirs. Minimal additive edits: N/A (test-only
131-scope). No concerns here.
132-
133-### (d) Test quality — one near-tautology, confirmed
134-
135:- **T1 (blocking).** `test_d110_never_zero_allowance_is_embedded_once_in_all_three_verdicts`
136-  **cannot discriminate a broken implementation.** The fixture pins endpoint
137-  bounds alpha `0.025/0.026`, beta `0.027/0.028`, gamma `0.029/0.030` — every
138-  observed drift is `0.001`, and every one is below the `0.010818` screen. The
139-  applied allowance is therefore `0.010818` in all three windows, so the test
140-  passes identically against `max(drift, 0.010818)`, against the constant
--
161-exactly one JSON file plus one test module. That is the right direction. The only
162-scope defect is the missing NEEDS_SCOPE clause (G3).
163-
164-### (f) What it misses that the register/memo require
165-
166:- **M1. L5 by name.** The register: *"bracket selection can BORROW another
167-  window's receipts (global candidate scan; no runs_root/intended-pair binding)…
168-  U1 review MUST include this scenario as a regression vector."* U1's fix round
169-  added "L5 mandatory window/runs_root binding". U4 is the *integration*
170-  regression where three windows share one ledger — the exact topology L5
171-  described — yet no test names `runs_root`/`window_id` binding. The neighbor-
172-  substitution and cross-window-binding tests are adjacent but not the same
173-  assertion.
174:- **M2. No positive count-boundary oracle.** The operationally load-bearing fact
175-  is that the no-failure three-window campaign ends at **36 valid** — two short
176-  of the D-102 trigger. Nothing in the plan asserts this. It matters because any
177-  calibration retry, any fourth window (including Ed's optional 256-token prefill
178-  plan), or any extra fiducial crosses 38 and forces a successor mid-campaign.
179:- **M3. Per-window verdict issuance is never modelled.** Step 6 evaluates all
180-  three verdicts from a single sequence-85 (really 91) terminal snapshot. But the
181-  memo's §5A closing bookend runs *per window*: alpha's verdict is emitted at
182-  alpha's closeout, when the ledger holds only alpha's two live observations. The
183-  regression never proves (i) that alpha's verdict is issuable from its own
184-  terminal snapshot, nor (ii) that it remains re-verifiable at the campaign's
185-  terminal head after beta and gamma appended. If (ii) fails the campaign is
186-  broken and U4 will not have caught it.
187-- **M4.** No cross-window openness vector: beta's session left open while alpha's
188-  already-issued verdict is re-verified.
189-
190:### U4 amendment list (paste-ready)
191-
192-1. **Supersede the 85 oracle.** Build the fixture through the production writer
193-   path including `claim_bracket_session_slot` (as
194-   `scripts/validate_powermetrics_fiducial.py:409` does). Rename the test
195-   `test_three_windows_terminate_at_the_production_writer_sequence` and assert
--
448-§5B reconciliation, receipt custody binding) fall *outside* those three files and
449-are neither NEEDS_SCOPE'd nor deferred to a named owner.
450-
451-### (f) What it misses that the register/memo require
452-
453:- **M1.** L4's second half — *"de-duplicating the hardcoded literal"* — is
454-  untouched (`0.033558756679900` in §5B:406 and its `0.01` policy-JSON twin from
455-  the paper-fidelity queue). Outside scope, but must be NEEDS_SCOPE'd with an
456-  owner, not silently dropped.
457:- **M2.** R5 (wall-clock vs monotonic cooldown) — no operator mitigation.
458:- **M3.** The memo's order-manifest requirement for "arm-time attachment slots
459-  for the readiness record" — the plan emits a receipt that attaches to nothing.
460-- **M4.** Memo closing step 6 requires the network-time restoration be *recorded*;
461-  the plan restores it but adds no §12 close-out field.
462-- **M5.** §5B's retry rules vs the frozen zero-retry policy (see (b)).
463-

exec
/bin/zsh -lc "git show origin/main:docs/process_traces/2026-08-07-plan-factory/MAGISTRATE-DISPOSITIONS.md | sed -n '17,43p' && git show origin/main:docs/process_traces/2026-08-07-plan-factory/OPUS-EXAM-U4-U8.md | sed -n '190,255p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
## U4 — synthetic three-window regression: ACCEPT WITH AMENDMENTS

Strong enumeration (all 7 proof obligations + 12 refusal-vector bullets
decomposed into 30 named tests; every named API and all 16 refusal codes
verified real on the landed branch). Blocking amendments before landing:

1. **Supersede the sequence-85 oracle** — drive the happy path through the
   PRODUCTION writer path including the exclusive slot claim; assert the
   derived value (91) from a module constant plus model-independent counts
   (3 sessions, 6 live observations).
2. **The D-110 never-zero test currently CANNOT FAIL** — every fixture
   drift is 0.001, below the 0.010818 screen, so the max() branch is never
   exercised; it passes against max(), against the bare constant, and
   against min(). Add a window with drift > 0.010818 and assert BOTH
   branches. This is the one clause D-110 exists to protect.
3. Derive the synthetic acceptance artifact through the D-116 emitter (or
   NEEDS_SCOPE it) — do not ship a parent whose bound is not derivable
   from its own prior set.
4. Name L5 explicitly (a test that a candidate under another window's
   runs_root cannot bracket this window, with and without a binding).
5. Per-window verdict issuance + committed-pin cadence across window
   boundaries (the nights are three separate closeouts, not one snapshot).
6. Add the positive count oracle (no-failure campaign ends at 36 valid,
   two short of the 38 trigger) + a NEEDS_SCOPE clause.
Remaining amendments 7-13 in OPUS-EXAM-U4-U8.md are adopted as written.

## U8 — readiness validator + runbook amendment: REWORK
### U4 amendment list (paste-ready)

1. **Supersede the 85 oracle.** Build the fixture through the production writer
   path including `claim_bracket_session_slot` (as
   `scripts/validate_powermetrics_fiducial.py:409` does). Rename the test
   `test_three_windows_terminate_at_the_production_writer_sequence` and assert
   the derived value (3 sessions × 5 receipts = 15 → sequence **91**) *computed
   from a named module constant*, not a hardcoded literal. Additionally assert
   the two semantically load-bearing counts that are model-independent:
   `len(sessions) == 3` and `len(live_observations) == 6`. Record in
   `fixture_spec.json` that the memo's "85" is superseded by landed U1.
2. **Add a second, claim-free sequence variant only if the lead rules that the
   direct open/finalize path remains supported.** If it is not supported, delete
   the direct-API construction entirely; do not keep a fixture built by a path no
   operator will run.
3. **Make the D-110 allowance test discriminating (blocking).** Add a fourth
   synthetic window (or re-pin gamma) whose endpoint bounds give
   `observed_drift_s > 0.010818` — e.g. `0.029 / 0.045` (drift `0.016`). Assert
   `applied_allowance == observed_drift` on that window and
   `applied_allowance == 0.010818` on the sub-floor windows, in the same test, so
   `max()` is discriminated from a constant. Assert `embedding_count == 1` on
   both branches.
4. **Derive the synthetic acceptance artifact, do not patch it.** Emit it by
   running the same deterministic derivation used for D-116 over the 19 synthetic
   corpus members, so the synthetic parent's bound is reproducible from its own
   prior set. If that emitter is not importable within U4's write scope, raise
   `NEEDS_SCOPE` naming the emitter — do not ship an arithmetically inconsistent
   parent that the staged U2 successor tests must be written around.
5. **Run the whole happy path inside one temporary git repo with committed-pin
   enforcement ON.** Commit `configs/calibration/calibration_ledger_head.json`
   at each window boundary (mirroring the two real inter-night commits) and add
   `test_three_windows_require_two_intervening_committed_pin_advances` — a
   positive proof of the campaign's commit cadence, and the counterpart to the
   existing uncommitted-head refusal.
6. **Name L5 explicitly.** Add
   `test_candidate_under_another_windows_runs_root_cannot_bracket_this_window`:
   place a fully authentic, causal, same-epoch, fresh live observation under
   alpha's `runs_root` and attempt to bracket beta's science with it *absent* a
   binding (the original global-scan defect) and *with* a binding naming it.
   Both must refuse, and the refusal must cite the window/runs_root binding, not
   only the binding digest.
7. **Add the positive count-boundary oracle.**
   `test_no_failure_three_window_campaign_ends_at_36_valid_below_the_38_trigger`,
   asserting the trigger is *not* fired and that adding exactly two further valid
   same-epoch observations fires `corpus_doubles_from_19_to_38`. Comment the
   operational consequence (a fourth window or any calibration retry crosses it).
8. **Add per-window verdict issuance.**
   `test_alpha_verdict_issues_from_its_own_terminal_snapshot_and_re_verifies_at_campaign_terminal_head`
   — issue alpha's verdict at its own terminal head, then re-verify the identical
   verdict bytes against the campaign terminal snapshot after beta and gamma
   appended. Repeat for beta. This is the operational path; the single-snapshot
   evaluation is the memo's convenience, not §5A's procedure.
9. **Add cross-window openness.**
   `test_open_beta_session_does_not_invalidate_alphas_issued_verdict_but_blocks_a_campaign_terminal_pin`.
10. **Add a discovery-authority test.**
    `test_verdict_path_derives_candidate_universe_from_snapshot_without_caller_supply`
    — prove at least one production entry point does not accept a caller-supplied
    tuple, so the omit/add/duplicate guards are not the only universe defence.
11. **Name the doubled seam.** State the exact function being replaced by the
    deterministic bound-returning double, and add an assertion that the double is
    inactive in any test whose oracle is a bound/allowance value.
12. **Add the NEEDS_SCOPE clause:** "If the regression exposes a defect in U1/U2
    production code, early-return `NEEDS_SCOPE` naming the file and the failing
    vector. Do not widen scope, and do not weaken an oracle to make a test pass."
13. **Define `fixture_spec.json`'s authority:** it is *consumed* by the harness
    as the single source of the expected literals (sequences, counts, bounds,

exec
/bin/zsh -lc "git show origin/main:docs/process_traces/2026-08-07-plan-factory/OPUS-EXAM-U4-U8.md | sed -n '255,275p' && nl -ba tests/test_calibration_live_three_window.py | sed -n '1,280p' && nl -ba tests/fixtures/calibration_live_three_window/scenario.json | sed -n '1,240p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
    as the single source of the expected literals (sequences, counts, bounds,
    epoch, T1 vector); the test module must not restate any of them. Add
    `test_fixture_spec_is_the_sole_source_of_expected_literals` or drop the file
    from scope.

### U4 — three highest-risk gaps

1. **The regression will certify a ledger shape the three nights will not
   produce.** The plan routes around `claim_bracket_session_slot` to preserve the
   memo's "85". The production writer claims before finalizing, so the real
   campaign ledger interleaves claim receipts that U4 never exercises through
   discovery, binding, or verdict evaluation. This is the failure mode the whole
   unit exists to prevent, reintroduced by fidelity to a superseded literal.
   (Amendments 1, 2.)
2. **The D-110 never-zero test cannot fail.** Every fixture window has drift
   `0.001`, below the `0.010818` screen; the test passes against a hardcoded
   constant. D-110 cl.1 binds the never-zero allowance to *every mint under
   D-117*; U4 is where it is supposed to be proven, and as drafted it is not.
   (Amendment 3.)
3. **Per-window verdict issuance and the inter-night commit cadence are both
   unproven.** The plan evaluates from one terminal snapshot inside one process;
     1	"""Synthetic D-117 three-window live-ledger integration regression."""
     2	
     3	from __future__ import annotations
     4	
     5	import copy
     6	from dataclasses import replace
     7	from decimal import Decimal
     8	import hashlib
     9	import json
    10	from pathlib import Path
    11	import subprocess
    12	import tempfile
    13	from types import SimpleNamespace
    14	import unittest
    15	from unittest.mock import patch
    16	
    17	from joulewise.calibration_bracketing import (
    18	    CalibrationCandidate,
    19	    _canonical_sha256 as bracketing_canonical_sha256,
    20	    _valid_acceptance_bound,
    21	    build_calibration_bracket_binding,
    22	    calibration_bracket_for_bundles,
    23	    discover_calibration_candidates,
    24	    evaluate_calibration_bracket,
    25	    load_calibration_acceptance_bound,
    26	    validate_calibration_bracket_binding,
    27	)
    28	from joulewise.calibration_ledger import (
    29	    BRACKET_SESSION_FINALIZATION_EVENT,
    30	    BRACKET_SESSION_OPEN_EVENT,
    31	    BRACKET_SESSION_SLOT_CLAIM_EVENT,
    32	    GOVERNED_ARTIFACTS,
    33	    HISTORICAL_IMPORT_FINALIZATION_EVENT,
    34	    HISTORICAL_IMPORT_RESERVATION_EVENT,
    35	    LEDGER_SCHEMA,
    36	    RECEIPT_SCHEMA,
    37	    abort_bracket_session,
    38	    append_bracket_session_receipt,
    39	    canonical_json_bytes,
    40	    canonical_sha256,
    41	    claim_bracket_session_slot,
    42	    content_id_from_artifact_hashes,
    43	    finalize_bracket_session_slot,
    44	    load_calibration_ledger_snapshot,
    45	    terminal_head_pin_for_session,
    46	)
    47	from joulewise.powermetrics_fiducial import (
    48	    MAX_AGE_S,
    49	    PROTOCOL_ID,
    50	    PROTOCOL_V2_ID,
    51	)
    52	from joulewise.schemas import CalibrationBracketingPolicy
    53	from scripts import validate_powermetrics_fiducial as production_writer
    54	
    55	
    56	_FIXTURE = (
    57	    Path(__file__).parent
    58	    / "fixtures"
    59	    / "calibration_live_three_window"
    60	    / "scenario.json"
    61	)
    62	_USE_WINDOW_BINDING = object()
    63	_ISSUANCE_BASE_SEQUENCE = 76
    64	_LIVE_SESSION_COUNT = 3
    65	_PRODUCTION_RECEIPTS_PER_SESSION = 5
    66	_EXPECTED_TERMINAL_SEQUENCE = (
    67	    _ISSUANCE_BASE_SEQUENCE
    68	    + _LIVE_SESSION_COUNT * _PRODUCTION_RECEIPTS_PER_SESSION
    69	)
    70	
    71	
    72	def _hash(label: str) -> str:
    73	    return hashlib.sha256(label.encode("utf-8")).hexdigest()
    74	
    75	
    76	def _content_hashes(label: str) -> dict[str, str]:
    77	    return {
    78	        "manifest.json": _hash(f"{label}:manifest"),
    79	        "instrument_evidence.json": _hash(f"{label}:evidence"),
    80	    }
    81	
    82	
    83	def _receipt(core: dict) -> dict:
    84	    value = copy.deepcopy(core)
    85	    value.pop("receipt_digest", None)
    86	    value["receipt_digest"] = canonical_sha256(value)
    87	    return value
    88	
    89	
    90	def _ledger_bytes(receipts: list[dict]) -> bytes:
    91	    return b"".join(canonical_json_bytes(row) + b"\n" for row in receipts)
    92	
    93	
    94	def _pin_for(receipt: dict) -> dict:
    95	    return {
    96	        "sequence": receipt["sequence"],
    97	        "head_digest": receipt["receipt_digest"],
    98	        "ledger_schema": LEDGER_SCHEMA,
    99	    }
   100	
   101	
   102	def _pin_bytes(pin: dict) -> bytes:
   103	    return (json.dumps(pin, sort_keys=True) + "\n").encode("utf-8")
   104	
   105	
   106	def _write_synthetic_custody(custody: Path, label: str) -> None:
   107	    for relative in GOVERNED_ARTIFACTS:
   108	        path = custody / relative
   109	        path.parent.mkdir(parents=True, exist_ok=True)
   110	        path.write_bytes(f"{label}:{relative}".encode("utf-8"))
   111	
   112	
   113	class CalibrationLiveThreeWindowTests(unittest.TestCase):
   114	    """Exercise one issuance-equivalent prefix and its three live sessions."""
   115	
   116	    @classmethod
   117	    def setUpClass(cls) -> None:
   118	        cls.scenario = json.loads(_FIXTURE.read_text(encoding="utf-8"))
   119	        cls.epoch = dict(cls.scenario["identity_epoch"])
   120	        cls.t1 = dict(cls.scenario["t1_bindings"])
   121	
   122	        cls._class_tmp = tempfile.TemporaryDirectory()
   123	        root = Path(cls._class_tmp.name)
   124	        runtime_windows = []
   125	        for source in cls.scenario["windows"]:
   126	            window = copy.deepcopy(source)
   127	            window["runs_root"] = str(root / "night-roots" / window["name"])
   128	            runtime_windows.append(window)
   129	        cls.windows = {
   130	            row["name"]: row for row in runtime_windows
   131	        }
   132	        cls.policy = CalibrationBracketingPolicy(
   133	            require_bracket=True,
   134	            calibration_bracket_max_drift_s=0.010,
   135	        )
   136	
   137	        source = load_calibration_acceptance_bound()
   138	        if source is None:
   139	            raise AssertionError("checked-in issued acceptance artifact is unavailable")
   140	        source_path = Path(
   141	            "configs/calibration/calibration_acceptance_d079_v2.json"
   142	        )
   143	        if hashlib.sha256(source_path.read_bytes()).hexdigest() != cls.scenario[
   144	            "source_acceptance_sha256"
   145	        ]:
   146	            raise AssertionError("fixture source acceptance pin drifted")
   147	
   148	        base_receipts, acceptance = cls._build_issuance_equivalent_base(source)
   149	        cls.base_receipts = base_receipts
   150	        cls.acceptance = acceptance
   151	        cls.base_sequence = len(base_receipts)
   152	        cls.base_digest = base_receipts[-1]["receipt_digest"]
   153	
   154	        ledger = root / "runs" / "ledger.jsonl"
   155	        pin = root / "configs" / "calibration" / "head.json"
   156	        ledger.parent.mkdir(parents=True)
   157	        pin.parent.mkdir(parents=True)
   158	        ledger.write_bytes(_ledger_bytes(base_receipts))
   159	        pin.write_bytes(_pin_bytes(_pin_for(base_receipts[-1])))
   160	
   161	        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
   162	        subprocess.run(
   163	            ["git", "config", "user.email", "tests@joulewise.invalid"],
   164	            cwd=root,
   165	            check=True,
   166	        )
   167	        subprocess.run(
   168	            ["git", "config", "user.name", "JouleWise tests"],
   169	            cwd=root,
   170	            check=True,
   171	        )
   172	        subprocess.run(
   173	            ["git", "add", pin.relative_to(root).as_posix()],
   174	            cwd=root,
   175	            check=True,
   176	        )
   177	        subprocess.run(
   178	            ["git", "commit", "-qm", "pin issuance-equivalent head"],
   179	            cwd=root,
   180	            check=True,
   181	        )
   182	
   183	        bindings: dict[str, dict] = {}
   184	        closeouts: dict[str, dict] = {}
   185	        for window in runtime_windows:
   186	            attempts = {
   187	                slot: f"d117-{window['name']}-{slot}" for slot in ("pre", "post")
   188	            }
   189	            slots = {
   190	                slot: {
   191	                    "attempt_id": attempts[slot],
   192	                    "custody_locator": (
   193	                        f"{window['runs_root']}/instrument_validation/"
   194	                        f"{attempts[slot]}"
   195	                    ),
   196	                    "identity_epoch": cls.epoch,
   197	                    "t1_bindings": cls.t1,
   198	                }
   199	                for slot in ("pre", "post")
   200	            }
   201	            append_bracket_session_receipt(
   202	                ledger,
   203	                session_id=window["session_id"],
   204	                window_id=window["window_id"],
   205	                plan_id=window["plan_id"],
   206	                plan_sha256=window["plan_sha256"],
   207	                evidence_root_id=window["evidence_root_id"],
   208	                runs_root=window["runs_root"],
   209	                slots=slots,
   210	                head_pin_path=pin,
   211	                require_committed_pin=True,
   212	                repo_root=root,
   213	            )
   214	            for slot in ("pre", "post"):
   215	                lifecycle = production_writer._CaptureLedgerLifecycle(
   216	                    ledger_path=ledger,
   217	                    head_pin_path=pin,
   218	                    attempt_id=attempts[slot],
   219	                    custody_locator=slots[slot]["custody_locator"],
   220	                    identity_epoch=cls.epoch,
   221	                    t1_bindings=cls.t1,
   222	                    session_id=window["session_id"],
   223	                    slot=slot,
   224	                    require_committed_pin=False,
   225	                )
   226	                # The synthetic issuance prefix has hash-only import custody.
   227	                # Keep that fixture boundary while exercising the production
   228	                # writer's reservation validation, exclusive claim, and
   229	                # finalization path for every live endpoint.
   230	                def load_without_import_custody(*args, **kwargs):
   231	                    kwargs["verify_custody"] = False
   232	                    return load_calibration_ledger_snapshot(*args, **kwargs)
   233	
   234	                with patch.object(
   235	                    production_writer,
   236	                    "load_calibration_ledger_snapshot",
   237	                    side_effect=load_without_import_custody,
   238	                ):
   239	                    lifecycle.begin()
   240	                _write_synthetic_custody(
   241	                    Path(slots[slot]["custody_locator"]), attempts[slot]
   242	                )
   243	                lifecycle.capture_wall_time_s = str(
   244	                    window[f"{slot}_capture_s"]
   245	                )
   246	                lifecycle.exact_bound_lexeme_s = window[f"{slot}_bound_s"]
   247	                _receipt_value, terminal_pin = lifecycle.finalize("valid")
   248	                if slot == "pre":
   249	                    if terminal_pin is not None:
   250	                        raise AssertionError("pre finalization emitted a terminal pin")
   251	                elif terminal_pin is None:
   252	                    raise AssertionError("post finalization omitted its terminal pin")
   253	            pin_value = terminal_pin
   254	            pin.write_bytes(_pin_bytes(pin_value))
   255	            subprocess.run(
   256	                ["git", "add", pin.relative_to(root).as_posix()],
   257	                cwd=root,
   258	                check=True,
   259	            )
   260	            subprocess.run(
   261	                ["git", "commit", "-qm", f"pin {window['name']} closeout"],
   262	                cwd=root,
   263	                check=True,
   264	            )
   265	            closeout_snapshot = load_calibration_ledger_snapshot(
   266	                ledger,
   267	                pin,
   268	                baseline_sequence=cls.base_sequence,
   269	                baseline_digest=cls.base_digest,
   270	                require_committed_pin=True,
   271	                verify_custody=False,
   272	                repo_root=root,
   273	            )
   274	            bindings[window["name"]] = build_calibration_bracket_binding(
   275	                closeout_snapshot,
   276	                session_id=window["session_id"],
   277	                window_id=window["window_id"],
   278	                plan_id=window["plan_id"],
   279	                plan_sha256=window["plan_sha256"],
   280	                evidence_root_id=window["evidence_root_id"],
     1	{
     2	  "schema_version": "joulewise.synthetic_calibration_live_three_window.v1",
     3	  "source_acceptance_sha256": "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985",
     4	  "issuance_equivalent_base": {
     5	    "receipt_count": 76,
     6	    "observation_count": 38,
     7	    "disposition_counts": {
     8	      "valid": 30,
     9	      "systematic-invalid": 2,
    10	      "ordinary-invalid": 6
    11	    },
    12	    "synthetic_additions_to_n19_derivation_corpus": {
    13	      "valid": 11,
    14	      "systematic-invalid": 2,
    15	      "ordinary-invalid": 6
    16	    }
    17	  },
    18	  "identity_epoch": {
    19	    "os_build": "synthetic-d117-os",
    20	    "hardware_model": "synthetic-d117-mac",
    21	    "power_policy": "synthetic-ac-high-power",
    22	    "sampling_interval_ms": 100,
    23	    "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
    24	    "pulse_protocol_id": "powermetrics_pulse_fiducial_v3"
    25	  },
    26	  "t1_bindings": {
    27	    "hardware_model": "synthetic-d117-mac",
    28	    "os_build": "synthetic-d117-os",
    29	    "powermetrics_sha256": "c2f8ef614953475fcc9af95b6aaaf1d5b8c43a0f4c682f72f56c6503945b3b94",
    30	    "sampling_interval_ms": 100,
    31	    "anchor_method_version": "powermetrics_native_second_censored_intersection_v1",
    32	    "mlx_version": "synthetic-mlx",
    33	    "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
    34	    "power_policy": "synthetic-ac-high-power",
    35	    "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
    36	    "protocol_sha256": "9eaf92f85136e234c56ea3ffd34392a73c313d4a092cabf308f5f5aaff9a31b1"
    37	  },
    38	  "windows": [
    39	    {
    40	      "name": "alpha",
    41	      "session_id": "session-d117-alpha",
    42	      "window_id": "plan-d117-floor-qwen25-1p5b-v1",
    43	      "plan_id": "plan-d117-floor-qwen25-1p5b-v1",
    44	      "plan_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    45	      "evidence_root_id": "evidence-d117-floor-qwen25-1p5b-v1",
    46	      "runs_root": "/synthetic/d117/alpha",
    47	      "window_start_s": 105.0,
    48	      "window_end_s": 115.0,
    49	      "pre_capture_s": 100.0,
    50	      "post_capture_s": 120.0,
    51	      "pre_bound_s": "0.025000",
    52	      "post_bound_s": "0.026000"
    53	    },
    54	    {
    55	      "name": "beta",
    56	      "session_id": "session-d117-beta",
    57	      "window_id": "plan-d117-floor-qwen25-7b-v1",
    58	      "plan_id": "plan-d117-floor-qwen25-7b-v1",
    59	      "plan_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    60	      "evidence_root_id": "evidence-d117-floor-qwen25-7b-v1",
    61	      "runs_root": "/synthetic/d117/beta",
    62	      "window_start_s": 125.0,
    63	      "window_end_s": 135.0,
    64	      "pre_capture_s": 121.0,
    65	      "post_capture_s": 140.0,
    66	      "pre_bound_s": "0.026500",
    67	      "post_bound_s": "0.027000"
    68	    },
    69	    {
    70	      "name": "gamma",
    71	      "session_id": "session-d117-gamma",
    72	      "window_id": "plan-d117-contrast-qwen25-1p5b-vs-7b-v1",
    73	      "plan_id": "plan-d117-contrast-qwen25-1p5b-vs-7b-v1",
    74	      "plan_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    75	      "evidence_root_id": "evidence-d117-contrast-qwen25-1p5b-vs-7b-v1",
    76	      "runs_root": "/synthetic/d117/gamma",
    77	      "window_start_s": 145.0,
    78	      "window_end_s": 155.0,
    79	      "pre_capture_s": 141.0,
    80	      "post_capture_s": 160.0,
    81	      "pre_bound_s": "0.028000",
    82	      "post_bound_s": "0.029000"
    83	    }
    84	  ],
    85	  "expected_live_extension": {
    86	    "session_count": 3,
    87	    "live_observation_count": 6,
    88	    "receipt_model_supersession": {
    89	      "superseded": {
    90	        "authority": "design-memo proposed three-receipt session model",
    91	        "receipts_per_session": 3,
    92	        "terminal_sequence": 85
    93	      },
    94	      "landed": {
    95	        "authority": "U1 production writer lifecycle",
    96	        "receipts_per_session": 5,
    97	        "events": [
    98	          "bracket-session-open",
    99	          "bracket-session-slot-claim:pre",
   100	          "bracket-session-slot-finalization:pre",
   101	          "bracket-session-slot-claim:post",
   102	          "bracket-session-slot-finalization:post"
   103	        ],
   104	        "terminal_sequence_oracle": "module-level _EXPECTED_TERMINAL_SEQUENCE derived by the production-path regression"
   105	      }
   106	    },
   107	    "candidate_count": 6,
   108	    "imported_candidate_count": 0,
   109	    "allowance_rule": "max(observed_drift_s,bracket_screen_s)",
   110	    "never_zero_allowance_s": "0.010818",
   111	    "valid_observation_count": {
   112	      "issuance": 30,
   113	      "after_three_live_windows": 36,
   114	      "corpus_doubling_trigger": 38,
   115	      "shortfall": 2
   116	    },
   117	    "allowance_branch_vectors": [
   118	      {
   119	        "window": "alpha",
   120	        "branch": "bracket_screen_s",
   121	        "pre_bound_s": "0.025000",
   122	        "post_bound_s": "0.026000",
   123	        "observed_drift_s": "0.001000",
   124	        "selected_allowance_s": "0.010818"
   125	      },
   126	      {
   127	        "window": "beta",
   128	        "branch": "observed_drift_s",
   129	        "pre_bound_s": "0.020000",
   130	        "post_bound_s": "0.031000",
   131	        "observed_drift_s": "0.011000",
   132	        "selected_allowance_s": "0.011000"
   133	      }
   134	    ],
   135	    "cross_window_openness": [
   136	      {
   137	        "closeout": "alpha",
   138	        "candidate_windows": ["alpha"]
   139	      },
   140	      {
   141	        "closeout": "beta",
   142	        "candidate_windows": ["alpha", "beta"]
   143	      },
   144	      {
   145	        "closeout": "gamma",
   146	        "candidate_windows": ["alpha", "beta", "gamma"]
   147	      }
   148	    ]
   149	  },
   150	  "staged_successor_vectors": {
   151	    "range_expanding_live_observation": {
   152	      "bound_s": "0.040000",
   153	      "expected_trigger": "new_valid_same_identity_capture_expands_observed_range"
   154	    },
   155	    "d102_count_boundary": {
   156	      "additional_valid_observations": 2,
   157	      "expected_total_valid_same_epoch": 38,
   158	      "expected_trigger": "corpus_doubles_from_19_to_38"
   159	    },
   160	    "successor_prior_set_integrity": {
   161	      "mutations": [
   162	        "omit_authenticated_prefix_member",
   163	        "change_authenticated_prefix_member"
   164	      ],
   165	      "expected_outcome": "refuse"
   166	    }
   167	  }
   168	}

exec
/bin/zsh -lc "nl -ba tests/test_calibration_live_three_window.py | sed -n '280,620p' && nl -ba tests/test_calibration_live_three_window.py | sed -n '620,980p' && nl -ba tests/test_calibration_live_three_window.py | sed -n '980,1420p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
   280	                evidence_root_id=window["evidence_root_id"],
   281	                runs_root=window["runs_root"],
   282	            )
   283	            closeouts[window["name"]] = {
   284	                "snapshot": closeout_snapshot,
   285	                "ledger_bytes": ledger.read_bytes(),
   286	                "pin_bytes": pin.read_bytes(),
   287	                "pin_commit": subprocess.run(
   288	                    ["git", "rev-parse", "HEAD"],
   289	                    cwd=root,
   290	                    check=True,
   291	                    capture_output=True,
   292	                    text=True,
   293	                ).stdout.strip(),
   294	            }
   295	
   296	        cls.bindings = bindings
   297	        cls.closeouts = closeouts
   298	        cls.final_ledger_bytes = ledger.read_bytes()
   299	        cls.final_pin_bytes = pin.read_bytes()
   300	
   301	    @classmethod
   302	    def tearDownClass(cls) -> None:
   303	        cls._class_tmp.cleanup()
   304	
   305	    @classmethod
   306	    def _build_issuance_equivalent_base(
   307	        cls, source: dict
   308	    ) -> tuple[list[dict], dict]:
   309	        artifact = copy.deepcopy(source)
   310	        artifact["identity_epoch"] = dict(cls.epoch)
   311	        artifact["prior_observation_set"]["epoch_catalog"] = {
   312	            "d079_epoch": dict(cls.epoch)
   313	        }
   314	
   315	        observations: list[dict] = []
   316	        receipt_members: list[dict] = []
   317	        for member in artifact["derivation_corpus"]["members"]:
   318	            hashes = {
   319	                "manifest.json": member["manifest_sha256"],
   320	                "instrument_evidence.json": member[
   321	                    "instrument_evidence_sha256"
   322	                ],
   323	            }
   324	            content_id = content_id_from_artifact_hashes(hashes)
   325	            if content_id is None:
   326	                raise AssertionError("derivation member lacks a content identity")
   327	            receipt_members.append(
   328	                {
   329	                    "attempt_id": member["member_id"],
   330	                    "content_id": content_id,
   331	                    "artifact_sha256": hashes,
   332	                    "disposition": "valid",
   333	                    "bound_s": member["b_fiducial_s"],
   334	                }
   335	            )
   336	
   337	        additions = cls.scenario["issuance_equivalent_base"][
   338	            "synthetic_additions_to_n19_derivation_corpus"
   339	        ]
   340	        for disposition, count in additions.items():
   341	            for index in range(count):
   342	                attempt_id = f"synthetic-import-{disposition}-{index:02d}"
   343	                hashes = _content_hashes(attempt_id)
   344	                content_id = content_id_from_artifact_hashes(hashes)
   345	                if content_id is None:
   346	                    raise AssertionError("synthetic import lacks a content identity")
   347	                receipt_members.append(
   348	                    {
   349	                        "attempt_id": attempt_id,
   350	                        "content_id": content_id,
   351	                        "artifact_sha256": hashes,
   352	                        "disposition": disposition,
   353	                        "bound_s": (
   354	                            "0.040000"
   355	                            if disposition == "systematic-invalid"
   356	                            else "0.026000"
   357	                        ),
   358	                    }
   359	                )
   360	
   361	        receipts: list[dict] = []
   362	        predecessor = "0" * 64
   363	        import_inputs = {
   364	            "disposition_table": _hash("synthetic-d117-disposition-table"),
   365	            "custody_manifest": _hash("synthetic-d117-custody-manifest"),
   366	        }
   367	        for index, member in enumerate(
   368	            sorted(receipt_members, key=lambda row: row["attempt_id"]), start=1
   369	        ):
   370	            custody = f"/synthetic/d117/import/{member['attempt_id']}"
   371	            reservation = _receipt(
   372	                {
   373	                    "schema_version": RECEIPT_SCHEMA,
   374	                    "ledger_schema": LEDGER_SCHEMA,
   375	                    "sequence": len(receipts) + 1,
   376	                    "predecessor_digest": predecessor,
   377	                    "event": HISTORICAL_IMPORT_RESERVATION_EVENT,
   378	                    "attempt_id": member["attempt_id"],
   379	                    "content_id": None,
   380	                    "artifact_sha256": {},
   381	                    "identity_epoch": dict(cls.epoch),
   382	                    "t1_bindings": dict(cls.t1),
   383	                    "capture_wall_time_s": None,
   384	                    "exact_bound_lexeme_s": None,
   385	                    "disposition": "pending",
   386	                    "custody_locator": custody,
   387	                    "historical_import_input_sha256": import_inputs,
   388	                }
   389	            )
   390	            receipts.append(reservation)
   391	            predecessor = reservation["receipt_digest"]
   392	            finalization = _receipt(
   393	                {
   394	                    "schema_version": RECEIPT_SCHEMA,
   395	                    "ledger_schema": LEDGER_SCHEMA,
   396	                    "sequence": len(receipts) + 1,
   397	                    "predecessor_digest": predecessor,
   398	                    "event": HISTORICAL_IMPORT_FINALIZATION_EVENT,
   399	                    "attempt_id": member["attempt_id"],
   400	                    "content_id": member["content_id"],
   401	                    "artifact_sha256": member["artifact_sha256"],
   402	                    "identity_epoch": dict(cls.epoch),
   403	                    "t1_bindings": dict(cls.t1),
   404	                    "capture_wall_time_s": str(float(index)),
   405	                    "exact_bound_lexeme_s": member["bound_s"],
   406	                    "disposition": member["disposition"],
   407	                    "custody_locator": custody,
   408	                }
   409	            )
   410	            receipts.append(finalization)
   411	            predecessor = finalization["receipt_digest"]
   412	            observations.append(
   413	                {
   414	                    "content_id": member["content_id"],
   415	                    "epoch_id": "d079_epoch",
   416	                    "disposition": member["disposition"],
   417	                    "attempt_id": member["attempt_id"],
   418	                }
   419	            )
   420	
   421	        cutoff = {
   422	            "sequence": len(receipts),
   423	            "head_digest": receipts[-1]["receipt_digest"],
   424	            "ledger_schema": LEDGER_SCHEMA,
   425	        }
   426	        artifact["ledger_cutoff"] = {
   427	            **cutoff,
   428	            "role": "issued_acceptance_baseline",
   429	        }
   430	        artifact["prior_observation_set"]["cutoff"] = cutoff
   431	        artifact["prior_observation_set"]["observations"] = observations
   432	        counts = {
   433	            disposition: sum(
   434	                row["disposition"] == disposition for row in observations
   435	            )
   436	            for disposition in ("ordinary-invalid", "systematic-invalid", "valid")
   437	        }
   438	        artifact["backfill_candidate"]["candidate_inventory"] = counts
   439	        artifact["derivation_sha256"] = bracketing_canonical_sha256(
   440	            {
   441	                key: value
   442	                for key, value in artifact.items()
   443	                if key != "derivation_sha256"
   444	            }
   445	        )
   446	        if not _valid_acceptance_bound(artifact):
   447	            raise AssertionError("synthetic issued acceptance artifact is invalid")
   448	        return receipts, artifact
   449	
   450	    def setUp(self) -> None:
   451	        self.tmp = tempfile.TemporaryDirectory()
   452	        self.root = Path(self.tmp.name)
   453	        self.ledger = self.root / "ledger.jsonl"
   454	        self.pin = self.root / "head.json"
   455	        self.ledger.write_bytes(self.final_ledger_bytes)
   456	        self.pin.write_bytes(self.final_pin_bytes)
   457	        self.receipts = [
   458	            json.loads(line) for line in self.final_ledger_bytes.splitlines()
   459	        ]
   460	        self.snapshot = self._load_snapshot()
   461	        self.candidates = self._discover(self.snapshot)
   462	
   463	    def tearDown(self) -> None:
   464	        self.tmp.cleanup()
   465	
   466	    def _load_snapshot(
   467	        self,
   468	        *,
   469	        ledger: Path | None = None,
   470	        pin: Path | None = None,
   471	        require_committed_pin: bool = False,
   472	        repo_root: Path | None = None,
   473	    ):
   474	        return load_calibration_ledger_snapshot(
   475	            ledger or self.ledger,
   476	            pin or self.pin,
   477	            baseline_sequence=self.base_sequence,
   478	            baseline_digest=self.base_digest,
   479	            require_committed_pin=require_committed_pin,
   480	            verify_custody=False,
   481	            repo_root=repo_root or self.root,
   482	        )
   483	
   484	    @staticmethod
   485	    def _candidate(observation) -> CalibrationCandidate:
   486	        return CalibrationCandidate(
   487	            relative_path=observation.custody_locator,
   488	            manifest_sha256=observation.artifact_sha256["manifest.json"],
   489	            evidence_sha256=observation.artifact_sha256[
   490	                "instrument_evidence.json"
   491	            ],
   492	            protocol_id=observation.t1_bindings["pulse_protocol_id"],
   493	            capture_wall_time_s=float(observation.capture_wall_time_s),
   494	            b_fiducial_s=observation.exact_bound_lexeme_s,
   495	            bindings=dict(observation.t1_bindings),
   496	            attempt_id=observation.attempt_id,
   497	            content_id=observation.content_id,
   498	            ledger_receipt_digest=observation.receipt_digest,
   499	            bracket_session_id=observation.bracket_session_id,
   500	            bracket_slot=observation.bracket_slot,
   501	            bracket_window_id=observation.bracket_window_id,
   502	            bracket_plan_id=observation.bracket_plan_id,
   503	            bracket_plan_sha256=observation.bracket_plan_sha256,
   504	            bracket_evidence_root_id=observation.bracket_evidence_root_id,
   505	            bracket_runs_root=observation.bracket_runs_root,
   506	        )
   507	
   508	    def _discover(self, snapshot):
   509	        with patch(
   510	            "joulewise.calibration_bracketing._candidate_from_observation",
   511	            side_effect=self._candidate,
   512	        ):
   513	            return discover_calibration_candidates(snapshot)
   514	
   515	    def _evaluate(
   516	        self,
   517	        window_name: str,
   518	        *,
   519	        snapshot=None,
   520	        candidates=None,
   521	        binding=_USE_WINDOW_BINDING,
   522	        bindings=None,
   523	    ):
   524	        window = self.windows[window_name]
   525	        selected_binding = (
   526	            self.bindings[window_name]
   527	            if binding is _USE_WINDOW_BINDING
   528	            else binding
   529	        )
   530	        with patch(
   531	            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
   532	            return_value=self.acceptance,
   533	        ):
   534	            return evaluate_calibration_bracket(
   535	                self.candidates if candidates is None else candidates,
   536	                window_start_s=window["window_start_s"],
   537	                window_end_s=window["window_end_s"],
   538	                bindings=self.t1 if bindings is None else bindings,
   539	                policy=self.policy,
   540	                ledger_snapshot=self.snapshot if snapshot is None else snapshot,
   541	                bracket_binding=selected_binding,
   542	                bracket_window_id=window["window_id"],
   543	                bracket_plan_id=window["plan_id"],
   544	                bracket_plan_sha256=window["plan_sha256"],
   545	                bracket_evidence_root_id=window["evidence_root_id"],
   546	                bracket_runs_root=window["runs_root"],
   547	            )
   548	
   549	    def _variant_snapshot(self, receipts: list[dict], pin: dict | None = None):
   550	        self.ledger.write_bytes(_ledger_bytes(receipts))
   551	        if pin is None:
   552	            pin = _pin_for(receipts[-1])
   553	        self.pin.write_bytes(_pin_bytes(pin))
   554	        return self._load_snapshot()
   555	
   556	    @staticmethod
   557	    def _rechain(receipts: list[dict]) -> list[dict]:
   558	        result: list[dict] = []
   559	        predecessor = "0" * 64
   560	        for sequence, source in enumerate(receipts, start=1):
   561	            row = copy.deepcopy(source)
   562	            row["sequence"] = sequence
   563	            row["predecessor_digest"] = predecessor
   564	            row = _receipt(row)
   565	            result.append(row)
   566	            predecessor = row["receipt_digest"]
   567	        return result
   568	
   569	    @staticmethod
   570	    def _rehash_binding(binding: dict) -> dict:
   571	        value = copy.deepcopy(binding)
   572	        value["binding_digest"] = bracketing_canonical_sha256(
   573	            {
   574	                key: item
   575	                for key, item in value.items()
   576	                if key != "binding_digest"
   577	            }
   578	        )
   579	        return value
   580	
   581	    def _receipt_index(
   582	        self, session_id: str, event: str, slot: str | None = None
   583	    ) -> int:
   584	        return next(
   585	            index
   586	            for index, row in enumerate(self.receipts)
   587	            if row.get("session_id") == session_id
   588	            and row.get("event") == event
   589	            and (slot is None or row.get("slot") == slot)
   590	        )
   591	
   592	    def test_issuance_equivalent_base_has_76_receipts_and_30_2_6_dispositions(
   593	        self,
   594	    ) -> None:
   595	        expected = self.scenario["issuance_equivalent_base"]
   596	        prefix = self.snapshot.receipts[: self.base_sequence]
   597	        imported = [
   598	            row
   599	            for row in self.snapshot.observations
   600	            if row.sequence <= self.base_sequence
   601	        ]
   602	        counts = {
   603	            disposition: sum(row.disposition == disposition for row in imported)
   604	            for disposition in ("valid", "systematic-invalid", "ordinary-invalid")
   605	        }
   606	        self.assertEqual(self.base_sequence, _ISSUANCE_BASE_SEQUENCE)
   607	        self.assertEqual(len(prefix), expected["receipt_count"])
   608	        self.assertEqual(len(imported), expected["observation_count"])
   609	        self.assertEqual(counts, expected["disposition_counts"])
   610	        self.assertTrue(all(row.is_historical_import for row in imported))
   611	
   612	    def test_exactly_six_live_candidates_and_zero_imported_candidates(self) -> None:
   613	        with patch(
   614	            "joulewise.calibration_bracketing._candidate_from_observation",
   615	            side_effect=self._candidate,
   616	        ) as authenticate:
   617	            candidates = discover_calibration_candidates(self.snapshot)
   618	        authenticated_attempts = {
   619	            call.args[0].attempt_id for call in authenticate.call_args_list
   620	        }
   620	        }
   621	        imported_attempts = {
   622	            row.attempt_id
   623	            for row in self.snapshot.observations
   624	            if row.is_historical_import
   625	        }
   626	        expected = self.scenario["expected_live_extension"]
   627	        self.assertEqual(len(candidates), expected["candidate_count"])
   628	        self.assertEqual(authenticated_attempts & imported_attempts, set())
   629	        self.assertTrue(all(candidate.bracket_session_id for candidate in candidates))
   630	
   631	    def test_bundle_path_uses_ledger_discovery_as_candidate_authority(self) -> None:
   632	        window = self.windows["gamma"]
   633	        reader = SimpleNamespace(
   634	            measured_window=lambda: SimpleNamespace(
   635	                start_s=window["window_start_s"],
   636	                end_s=window["window_end_s"],
   637	            ),
   638	            metadata=lambda: {
   639	                "instrument_calibration": {"bindings": dict(self.t1)}
   640	            },
   641	        )
   642	        with (
   643	            patch(
   644	                "joulewise.calibration_bracketing.BundleReader",
   645	                return_value=reader,
   646	            ),
   647	            patch(
   648	                "joulewise.calibration_bracketing._candidate_from_observation",
   649	                side_effect=self._candidate,
   650	            ),
   651	            patch(
   652	                "joulewise.calibration_bracketing.discover_calibration_candidates",
   653	                wraps=discover_calibration_candidates,
   654	            ) as discover,
   655	            patch(
   656	                "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
   657	                return_value=self.acceptance,
   658	            ),
   659	        ):
   660	            result, reasons = calibration_bracket_for_bundles(
   661	                Path(window["runs_root"]),
   662	                [Path(window["runs_root"]) / "science-member"],
   663	                self.policy,
   664	                ledger_snapshot=self.snapshot,
   665	                bracket_binding=self.bindings["gamma"],
   666	                bracket_window_id=window["window_id"],
   667	                bracket_plan_id=window["plan_id"],
   668	                bracket_plan_sha256=window["plan_sha256"],
   669	                bracket_evidence_root_id=window["evidence_root_id"],
   670	            )
   671	        discover.assert_called_once_with(self.snapshot)
   672	        self.assertEqual(reasons, ())
   673	        self.assertEqual(result["status"], "passed")
   674	        self.assertEqual(
   675	            [result[slot]["attempt_id"] for slot in ("pre", "post")],
   676	            ["d117-gamma-pre", "d117-gamma-post"],
   677	        )
   678	
   679	    def test_alpha_beta_gamma_each_bind_only_their_own_pre_post_pair(self) -> None:
   680	        for name, window in self.windows.items():
   681	            with self.subTest(window=name):
   682	                resolved = validate_calibration_bracket_binding(
   683	                    self.bindings[name],
   684	                    self.snapshot,
   685	                    window_id=window["window_id"],
   686	                    plan_id=window["plan_id"],
   687	                    plan_sha256=window["plan_sha256"],
   688	                    evidence_root_id=window["evidence_root_id"],
   689	                    runs_root=window["runs_root"],
   690	                )
   691	                self.assertIsNotNone(resolved)
   692	                result, reasons = self._evaluate(name)
   693	                self.assertEqual(reasons, ())
   694	                self.assertEqual(result["status"], "passed")
   695	                self.assertEqual(
   696	                    [result[slot]["attempt_id"] for slot in ("pre", "post")],
   697	                    [f"d117-{name}-pre", f"d117-{name}-post"],
   698	                )
   699	
   700	    def test_all_six_are_same_epoch_causal_fresh_protocol_and_t1_eligible(
   701	        self,
   702	    ) -> None:
   703	        observations = {
   704	            row.attempt_id: row
   705	            for row in self.snapshot.observations
   706	            if not row.is_historical_import
   707	        }
   708	        self.assertEqual(len(observations), 6)
   709	        for name, window in self.windows.items():
   710	            pre = observations[f"d117-{name}-pre"]
   711	            post = observations[f"d117-{name}-post"]
   712	            with self.subTest(window=name):
   713	                self.assertEqual(dict(pre.identity_epoch), self.epoch)
   714	                self.assertEqual(dict(post.identity_epoch), self.epoch)
   715	                self.assertEqual(dict(pre.t1_bindings), self.t1)
   716	                self.assertEqual(dict(post.t1_bindings), self.t1)
   717	                self.assertEqual(pre.t1_bindings["pulse_protocol_id"], PROTOCOL_ID)
   718	                self.assertEqual(post.t1_bindings["pulse_protocol_id"], PROTOCOL_ID)
   719	                self.assertLessEqual(float(pre.capture_wall_time_s), window["window_start_s"])
   720	                self.assertGreaterEqual(float(post.capture_wall_time_s), window["window_end_s"])
   721	                self.assertLessEqual(
   722	                    window["window_end_s"] - float(pre.capture_wall_time_s),
   723	                    MAX_AGE_S,
   724	                )
   725	                self.assertLessEqual(
   726	                    float(post.capture_wall_time_s) - window["window_start_s"],
   727	                    MAX_AGE_S,
   728	                )
   729	
   730	    def test_no_neighboring_endpoint_can_substitute_for_a_bound_endpoint(self) -> None:
   731	        names = list(self.windows)
   732	        for index, name in enumerate(names):
   733	            neighbor = names[(index + 1) % len(names)]
   734	            tampered = copy.deepcopy(self.bindings[name])
   735	            tampered["endpoints"]["post"] = copy.deepcopy(
   736	                self.bindings[neighbor]["endpoints"]["post"]
   737	            )
   738	            tampered = self._rehash_binding(tampered)
   739	            with self.subTest(window=name, neighbor=neighbor):
   740	                _result, reasons = self._evaluate(name, binding=tampered)
   741	                self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
   742	
   743	    def test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding(
   744	        self,
   745	    ) -> None:
   746	        beta = self.windows["beta"]
   747	        by_attempt = {candidate.attempt_id: candidate for candidate in self.candidates}
   748	        foreign_pre = by_attempt["d117-alpha-pre"]
   749	        foreign_post = by_attempt["d117-gamma-post"]
   750	        self.assertNotEqual(foreign_pre.bracket_runs_root, beta["runs_root"])
   751	        self.assertNotEqual(foreign_post.bracket_runs_root, beta["runs_root"])
   752	        self.assertLessEqual(foreign_pre.capture_wall_time_s, beta["window_start_s"])
   753	        self.assertGreaterEqual(foreign_post.capture_wall_time_s, beta["window_end_s"])
   754	
   755	        _result, reasons = self._evaluate("beta", binding=None)
   756	        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))
   757	
   758	        result, reasons = self._evaluate(
   759	            "beta", binding=self.bindings["beta"]
   760	        )
   761	        self.assertEqual(reasons, ())
   762	        self.assertEqual(
   763	            [result[slot]["attempt_id"] for slot in ("pre", "post")],
   764	            ["d117-beta-pre", "d117-beta-post"],
   765	        )
   766	        self.assertNotIn(
   767	            foreign_pre.attempt_id,
   768	            {result["pre"]["attempt_id"], result["post"]["attempt_id"]},
   769	        )
   770	        self.assertNotIn(
   771	            foreign_post.attempt_id,
   772	            {result["pre"]["attempt_id"], result["post"]["attempt_id"]},
   773	        )
   774	
   775	    def test_each_night_issues_its_verdict_at_a_committed_closeout(self) -> None:
   776	        expected = self.scenario["expected_live_extension"]
   777	        pin_commits = []
   778	        pin_digests = []
   779	        for index, vector in enumerate(expected["cross_window_openness"], start=1):
   780	            name = vector["closeout"]
   781	            snapshot = self.closeouts[name]["snapshot"]
   782	            pin_value = json.loads(self.closeouts[name]["pin_bytes"])
   783	            candidates = self._discover(snapshot)
   784	            candidate_window_ids = {
   785	                candidate.bracket_window_id for candidate in candidates
   786	            }
   787	            expected_window_ids = {
   788	                self.windows[window_name]["window_id"]
   789	                for window_name in vector["candidate_windows"]
   790	            }
   791	            with self.subTest(closeout=name):
   792	                self.assertEqual(snapshot.refusal_reasons, ())
   793	                self.assertEqual(len(snapshot.bracket_sessions), index)
   794	                self.assertEqual(
   795	                    len(
   796	                        [
   797	                            observation
   798	                            for observation in snapshot.observations
   799	                            if not observation.is_historical_import
   800	                        ]
   801	                    ),
   802	                    index * 2,
   803	                )
   804	                self.assertEqual(
   805	                    snapshot.head_sequence,
   806	                    self.base_sequence + index * _PRODUCTION_RECEIPTS_PER_SESSION,
   807	                )
   808	                self.assertEqual(pin_value["sequence"], snapshot.head_sequence)
   809	                self.assertEqual(pin_value["head_digest"], snapshot.head_digest)
   810	                self.assertEqual(candidate_window_ids, expected_window_ids)
   811	                result, reasons = self._evaluate(
   812	                    name,
   813	                    snapshot=snapshot,
   814	                    candidates=candidates,
   815	                    binding=self.bindings[name],
   816	                )
   817	                self.assertEqual(reasons, ())
   818	                self.assertEqual(result["status"], "passed")
   819	                self.assertEqual(
   820	                    result["acceptance"]["ledger_snapshot"]["sequence"],
   821	                    snapshot.head_sequence,
   822	                )
   823	            pin_commits.append(self.closeouts[name]["pin_commit"])
   824	            pin_digests.append(pin_value["head_digest"])
   825	        self.assertEqual(len(set(pin_commits)), _LIVE_SESSION_COUNT)
   826	        self.assertEqual(len(set(pin_digests)), _LIVE_SESSION_COUNT)
   827	
   828	    def test_final_closeout_replays_all_verdicts_with_complete_universe(self) -> None:
   829	        snapshots = []
   830	        for name in self.windows:
   831	            result, reasons = self._evaluate(name, candidates=self.candidates)
   832	            self.assertEqual(reasons, ())
   833	            snapshots.append(result["acceptance"]["ledger_snapshot"])
   834	        self.assertEqual(snapshots, [snapshots[0]] * 3)
   835	        self.assertEqual(snapshots[0]["sequence"], _EXPECTED_TERMINAL_SEQUENCE)
   836	        for name in self.windows:
   837	            _result, reasons = self._evaluate(
   838	                name, candidates=self.candidates[:-1]
   839	            )
   840	            self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))
   841	
   842	    def test_production_writer_receipts_end_at_derived_terminal_sequence(self) -> None:
   843	        live = self.snapshot.receipts[self.base_sequence :]
   844	        expected = self.scenario["expected_live_extension"]
   845	        receipt_model = expected["receipt_model_supersession"]["landed"]
   846	        self.assertEqual(self.snapshot.head_sequence, _EXPECTED_TERMINAL_SEQUENCE)
   847	        self.assertEqual(
   848	            len(live),
   849	            expected["session_count"] * _PRODUCTION_RECEIPTS_PER_SESSION,
   850	        )
   851	        self.assertEqual(
   852	            receipt_model["receipts_per_session"],
   853	            _PRODUCTION_RECEIPTS_PER_SESSION,
   854	        )
   855	        for index, window in enumerate(self.windows.values()):
   856	            start = index * _PRODUCTION_RECEIPTS_PER_SESSION
   857	            rows = live[start : start + _PRODUCTION_RECEIPTS_PER_SESSION]
   858	            self.assertEqual(
   859	                [row["event"] for row in rows],
   860	                [
   861	                    BRACKET_SESSION_OPEN_EVENT,
   862	                    BRACKET_SESSION_SLOT_CLAIM_EVENT,
   863	                    BRACKET_SESSION_FINALIZATION_EVENT,
   864	                    BRACKET_SESSION_SLOT_CLAIM_EVENT,
   865	                    BRACKET_SESSION_FINALIZATION_EVENT,
   866	                ],
   867	            )
   868	            self.assertEqual({row["session_id"] for row in rows}, {window["session_id"]})
   869	            self.assertEqual(
   870	                [row["slot"] for row in rows[1:]],
   871	                ["pre", "pre", "post", "post"],
   872	            )
   873	        live_observations = [
   874	            observation
   875	            for observation in self.snapshot.observations
   876	            if not observation.is_historical_import
   877	        ]
   878	        self.assertEqual(
   879	            len(self.snapshot.bracket_sessions), expected["session_count"]
   880	        )
   881	        self.assertEqual(
   882	            {session.state for session in self.snapshot.bracket_sessions},
   883	            {"finalized"},
   884	        )
   885	        self.assertEqual(
   886	            len(live_observations), expected["live_observation_count"]
   887	        )
   888	        self.assertTrue(
   889	            all(
   890	                observation.observation_kind == "bracket-session-finalized"
   891	                and observation.disposition == "valid"
   892	                for observation in live_observations
   893	            )
   894	        )
   895	
   896	    def test_d110_allowance_selects_both_max_operands_across_windows(self) -> None:
   897	        expected = self.scenario["expected_live_extension"]
   898	        by_attempt = {candidate.attempt_id: candidate for candidate in self.candidates}
   899	        for vector in expected["allowance_branch_vectors"]:
   900	            name = vector["window"]
   901	            overridden = dict(by_attempt)
   902	            for slot in ("pre", "post"):
   903	                attempt_id = f"d117-{name}-{slot}"
   904	                overridden[attempt_id] = replace(
   905	                    overridden[attempt_id],
   906	                    b_fiducial_s=vector[f"{slot}_bound_s"],
   907	                )
   908	            candidates = tuple(
   909	                overridden[candidate.attempt_id] for candidate in self.candidates
   910	            )
   911	            with self.subTest(window=name, branch=vector["branch"]):
   912	                observed = Decimal(vector["observed_drift_s"])
   913	                screen = Decimal(expected["never_zero_allowance_s"])
   914	                if vector["branch"] == "bracket_screen_s":
   915	                    self.assertLess(observed, screen)
   916	                else:
   917	                    self.assertEqual(vector["branch"], "observed_drift_s")
   918	                    self.assertGreater(observed, screen)
   919	                result, reasons = self._evaluate(name, candidates=candidates)
   920	                self.assertEqual(reasons, ())
   921	                allowance = result["acceptance"]["allowance"]
   922	                self.assertEqual(allowance["rule"], expected["allowance_rule"])
   923	                self.assertEqual(
   924	                    result["acceptance"]["drift"]["observed_s"],
   925	                    vector["observed_drift_s"],
   926	                )
   927	                self.assertEqual(
   928	                    allowance["value_s"], vector["selected_allowance_s"]
   929	                )
   930	                self.assertEqual(allowance["embedding_count"], 1)
   931	
   932	    def test_no_failure_campaign_has_36_valid_observations_two_short_of_trigger(
   933	        self,
   934	    ) -> None:
   935	        expected = self.scenario["expected_live_extension"][
   936	            "valid_observation_count"
   937	        ]
   938	        issuance_valid = {
   939	            observation.content_id
   940	            for observation in self.snapshot.observations
   941	            if observation.is_historical_import
   942	            and observation.disposition == "valid"
   943	            and dict(observation.identity_epoch) == self.epoch
   944	        }
   945	        valid_same_epoch = {
   946	            observation.content_id
   947	            for observation in self.snapshot.observations
   948	            if observation.disposition == "valid"
   949	            and dict(observation.identity_epoch) == self.epoch
   950	        }
   951	        self.assertEqual(len(issuance_valid), expected["issuance"])
   952	        self.assertEqual(
   953	            len(valid_same_epoch), expected["after_three_live_windows"]
   954	        )
   955	        self.assertEqual(
   956	            expected["corpus_doubling_trigger"] - len(valid_same_epoch),
   957	            expected["shortfall"],
   958	        )
   959	        for name in self.windows:
   960	            result, reasons = self._evaluate(name)
   961	            self.assertEqual(reasons, ())
   962	            self.assertNotIn(
   963	                "corpus_doubles_from_19_to_38",
   964	                result["acceptance"]["prospective_rederivation"][
   965	                    "observed_triggers"
   966	                ],
   967	            )
   968	
   969	    def test_refuses_import_marker_removal_import_leakage_or_discovery_regression(
   970	        self,
   971	    ) -> None:
   972	        marker_removed = copy.deepcopy(self.receipts)
   973	        marker_removed[1]["event"] = "finalization"
   974	        marker_removed[1] = _receipt(marker_removed[1])
   975	        snapshot = self._variant_snapshot(marker_removed)
   976	        self.assertIn("calibration_ledger_attempt_conflict", snapshot.refusal_reasons)
   977	
   978	        first_import = next(
   979	            row
   980	            for row in self.snapshot.observations
   980	            for row in self.snapshot.observations
   981	            if row.is_historical_import and row.disposition == "valid"
   982	        )
   983	        leaked = replace(first_import, observation_kind="live-capture")
   984	        leaked_snapshot = replace(
   985	            self.snapshot,
   986	            observations=tuple(
   987	                leaked if row.attempt_id == leaked.attempt_id else row
   988	                for row in self.snapshot.observations
   989	            ),
   990	        )
   991	        leaked_candidates = self._discover(leaked_snapshot)
   992	        _result, reasons = self._evaluate(
   993	            "alpha", snapshot=leaked_snapshot, candidates=leaked_candidates
   994	        )
   995	        self.assertEqual(reasons, ("calibration_ledger_baseline_missing",))
   996	
   997	        imported_candidate = self._candidate(first_import)
   998	        _result, reasons = self._evaluate(
   999	            "alpha", candidates=(*self.candidates, imported_candidate)
  1000	        )
  1001	        self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))
  1002	
  1003	    def test_refuses_missing_duplicate_reordered_or_conflicting_session_receipts(
  1004	        self,
  1005	    ) -> None:
  1006	        alpha_session = self.windows["alpha"]["session_id"]
  1007	        post_claim = self._receipt_index(
  1008	            alpha_session, BRACKET_SESSION_SLOT_CLAIM_EVENT, "post"
  1009	        )
  1010	        post_final = self._receipt_index(
  1011	            alpha_session, BRACKET_SESSION_FINALIZATION_EVENT, "post"
  1012	        )
  1013	        session_open = self._receipt_index(
  1014	            alpha_session, BRACKET_SESSION_OPEN_EVENT
  1015	        )
  1016	        variants: dict[str, list[dict]] = {}
  1017	        variants["missing"] = (
  1018	            self.receipts[:post_final] + self.receipts[post_final + 1 :]
  1019	        )
  1020	        variants["duplicate"] = (
  1021	            self.receipts[: post_final + 1]
  1022	            + [copy.deepcopy(self.receipts[post_final])]
  1023	            + self.receipts[post_final + 1 :]
  1024	        )
  1025	        reordered = copy.deepcopy(self.receipts)
  1026	        reordered[post_claim], reordered[post_final] = (
  1027	            reordered[post_final],
  1028	            reordered[post_claim],
  1029	        )
  1030	        variants["reordered"] = reordered
  1031	        conflicting = copy.deepcopy(self.receipts)
  1032	        conflicting[session_open]["window_id"] = "conflicting-alpha-window"
  1033	        conflicting[session_open] = _receipt(conflicting[session_open])
  1034	        variants["conflicting"] = conflicting
  1035	
  1036	        for name, receipts in variants.items():
  1037	            with self.subTest(vector=name):
  1038	                snapshot = self._variant_snapshot(receipts)
  1039	                self.assertTrue(
  1040	                    {
  1041	                        "calibration_ledger_chain_conflict",
  1042	                        "calibration_ledger_bracket_session_conflict",
  1043	                    }
  1044	                    & set(snapshot.refusal_reasons)
  1045	                )
  1046	
  1047	    def test_refuses_open_or_abandoned_session_without_governed_closure(self) -> None:
  1048	        open_snapshot = self._variant_snapshot(self.receipts[:-1])
  1049	        self.assertIn(
  1050	            "calibration_ledger_bracket_session_open",
  1051	            open_snapshot.refusal_reasons,
  1052	        )
  1053	
  1054	        gamma_session = self.windows["gamma"]["session_id"]
  1055	        post_claim = self._receipt_index(
  1056	            gamma_session, BRACKET_SESSION_SLOT_CLAIM_EVENT, "post"
  1057	        )
  1058	        abandoned = copy.deepcopy(self.receipts[:post_claim])
  1059	        abandoned[-1]["disposition"] = "abandoned"
  1060	        abandoned = self._rechain(abandoned)
  1061	        abandoned_snapshot = self._variant_snapshot(abandoned)
  1062	        self.assertIn(
  1063	            "calibration_ledger_bracket_session_open",
  1064	            abandoned_snapshot.refusal_reasons,
  1065	        )
  1066	
  1067	    def test_refuses_head_pin_mismatch_rollback_fork_or_uncommitted_terminal_head(
  1068	        self,
  1069	    ) -> None:
  1070	        mismatch_pin = {
  1071	            "sequence": _EXPECTED_TERMINAL_SEQUENCE,
  1072	            "head_digest": "f" * 64,
  1073	            "ledger_schema": LEDGER_SCHEMA,
  1074	        }
  1075	        mismatch = self._variant_snapshot(self.receipts, mismatch_pin)
  1076	        self.assertIn("calibration_ledger_head_mismatch", mismatch.refusal_reasons)
  1077	
  1078	        rollback = self._variant_snapshot(
  1079	            self.receipts[:-1], json.loads(self.final_pin_bytes)
  1080	        )
  1081	        self.assertIn("calibration_ledger_rollback", rollback.refusal_reasons)
  1082	
  1083	        forked = copy.deepcopy(self.receipts)
  1084	        fork_index = self._receipt_index(
  1085	            self.windows["gamma"]["session_id"],
  1086	            BRACKET_SESSION_SLOT_CLAIM_EVENT,
  1087	            "pre",
  1088	        )
  1089	        forked[fork_index]["predecessor_digest"] = "e" * 64
  1090	        forked[fork_index] = _receipt(forked[fork_index])
  1091	        fork = self._variant_snapshot(forked)
  1092	        self.assertIn("calibration_ledger_chain_conflict", fork.refusal_reasons)
  1093	
  1094	        repo = self.root / "synthetic-repo"
  1095	        ledger = repo / "runs" / "ledger.jsonl"
  1096	        pin = repo / "configs" / "calibration" / "head.json"
  1097	        ledger.parent.mkdir(parents=True)
  1098	        pin.parent.mkdir(parents=True)
  1099	        ledger.write_bytes(self.final_ledger_bytes)
  1100	        pin.write_bytes(self.final_pin_bytes)
  1101	        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
  1102	        subprocess.run(
  1103	            ["git", "config", "user.email", "tests@joulewise.invalid"],
  1104	            cwd=repo,
  1105	            check=True,
  1106	        )
  1107	        subprocess.run(
  1108	            ["git", "config", "user.name", "JouleWise tests"],
  1109	            cwd=repo,
  1110	            check=True,
  1111	        )
  1112	        subprocess.run(
  1113	            ["git", "add", pin.relative_to(repo).as_posix()],
  1114	            cwd=repo,
  1115	            check=True,
  1116	        )
  1117	        subprocess.run(
  1118	            ["git", "commit", "-qm", "pin synthetic terminal head"],
  1119	            cwd=repo,
  1120	            check=True,
  1121	        )
  1122	        pin.write_text(
  1123	            json.dumps(json.loads(self.final_pin_bytes), indent=2) + "\n",
  1124	            encoding="utf-8",
  1125	        )
  1126	        uncommitted = self._load_snapshot(
  1127	            ledger=ledger,
  1128	            pin=pin,
  1129	            require_committed_pin=True,
  1130	            repo_root=repo,
  1131	        )
  1132	        self.assertIn(
  1133	            "calibration_ledger_head_uncommitted", uncommitted.refusal_reasons
  1134	        )
  1135	
  1136	    def test_refuses_omitted_added_duplicated_off_ledger_or_substituted_observations(
  1137	        self,
  1138	    ) -> None:
  1139	        imported = next(
  1140	            row
  1141	            for row in self.snapshot.observations
  1142	            if row.is_historical_import and row.disposition == "valid"
  1143	        )
  1144	        fake = replace(
  1145	            self.candidates[0],
  1146	            attempt_id="synthetic-off-ledger",
  1147	            content_id=_hash("synthetic-off-ledger-content"),
  1148	            ledger_receipt_digest=_hash("synthetic-off-ledger-receipt"),
  1149	        )
  1150	        variants = {
  1151	            "omitted": self.candidates[:-1],
  1152	            "added": (*self.candidates, fake),
  1153	            "duplicated": (*self.candidates, self.candidates[0]),
  1154	            "off-ledger": (*self.candidates, self._candidate(imported)),
  1155	            "content-substituted": (
  1156	                replace(self.candidates[0], content_id=_hash("substituted-content")),
  1157	                *self.candidates[1:],
  1158	            ),
  1159	        }
  1160	        for name, candidates in variants.items():
  1161	            with self.subTest(vector=name):
  1162	                _result, reasons = self._evaluate("alpha", candidates=candidates)
  1163	                self.assertEqual(
  1164	                    reasons, ("calibration_ledger_off_ledger_artifact",)
  1165	                )
  1166	
  1167	    def test_refuses_missing_tampered_swapped_or_cross_window_bracket_binding(
  1168	        self,
  1169	    ) -> None:
  1170	        _result, reasons = self._evaluate("alpha", binding=None)
  1171	        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))
  1172	
  1173	        tampered = copy.deepcopy(self.bindings["alpha"])
  1174	        tampered["window_id"] = "tampered-without-digest-update"
  1175	        _result, reasons = self._evaluate("alpha", binding=tampered)
  1176	        self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
  1177	
  1178	        swapped = copy.deepcopy(self.bindings["alpha"])
  1179	        swapped["endpoints"]["pre"], swapped["endpoints"]["post"] = (
  1180	            swapped["endpoints"]["post"],
  1181	            swapped["endpoints"]["pre"],
  1182	        )
  1183	        swapped = self._rehash_binding(swapped)
  1184	        _result, reasons = self._evaluate("alpha", binding=swapped)
  1185	        self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
  1186	
  1187	        _result, reasons = self._evaluate(
  1188	            "alpha", binding=self.bindings["beta"]
  1189	        )
  1190	        self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
  1191	
  1192	    def test_refuses_noncausal_stale_t1_protocol_or_epoch_mismatched_endpoint(
  1193	        self,
  1194	    ) -> None:
  1195	        gamma = self.windows["gamma"]
  1196	        indexes = {
  1197	            "open": next(
  1198	                index
  1199	                for index, row in enumerate(self.receipts)
  1200	                if row.get("session_id") == gamma["session_id"]
  1201	                and row["event"] == BRACKET_SESSION_OPEN_EVENT
  1202	            ),
  1203	            "pre": next(
  1204	                index
  1205	                for index, row in enumerate(self.receipts)
  1206	                if row.get("session_id") == gamma["session_id"]
  1207	                and row.get("event") == BRACKET_SESSION_FINALIZATION_EVENT
  1208	                and row.get("slot") == "pre"
  1209	            ),
  1210	            "post": next(
  1211	                index
  1212	                for index, row in enumerate(self.receipts)
  1213	                if row.get("session_id") == gamma["session_id"]
  1214	                and row.get("event") == BRACKET_SESSION_FINALIZATION_EVENT
  1215	                and row.get("slot") == "post"
  1216	            ),
  1217	        }
  1218	
  1219	        variants: dict[str, tuple[list[dict], tuple[str, ...]]] = {}
  1220	        noncausal = copy.deepcopy(self.receipts)
  1221	        noncausal[indexes["pre"]]["capture_wall_time_s"] = str(
  1222	            gamma["window_start_s"] + 1.0
  1223	        )
  1224	        variants["noncausal"] = (
  1225	            self._rechain(noncausal),
  1226	            ("calibration_bracket_binding_invalid",),
  1227	        )
  1228	
  1229	        stale = copy.deepcopy(self.receipts)
  1230	        stale[indexes["post"]]["capture_wall_time_s"] = str(
  1231	            gamma["window_start_s"] + MAX_AGE_S + 1.0
  1232	        )
  1233	        variants["stale"] = (
  1234	            self._rechain(stale),
  1235	            ("instrument_calibration_stale",),
  1236	        )
  1237	
  1238	        wrong_t1 = copy.deepcopy(self.receipts)
  1239	        wrong_t1[indexes["open"]]["slots"]["pre"]["t1_bindings"][
  1240	            "mlx_version"
  1241	        ] = "wrong-mlx"
  1242	        wrong_t1[indexes["pre"]]["t1_bindings"]["mlx_version"] = "wrong-mlx"
  1243	        variants["t1"] = (
  1244	            self._rechain(wrong_t1),
  1245	            ("calibration_bracket_binding_invalid",),
  1246	        )
  1247	
  1248	        wrong_protocol = copy.deepcopy(self.receipts)
  1249	        for row in (
  1250	            wrong_protocol[indexes["open"]]["slots"]["pre"],
  1251	            wrong_protocol[indexes["pre"]],
  1252	        ):
  1253	            row["t1_bindings"]["pulse_protocol_id"] = PROTOCOL_V2_ID
  1254	            row["identity_epoch"]["pulse_protocol_id"] = PROTOCOL_V2_ID
  1255	        variants["protocol"] = (
  1256	            self._rechain(wrong_protocol),
  1257	            ("calibration_bracket_binding_invalid",),
  1258	        )
  1259	
  1260	        wrong_epoch = copy.deepcopy(self.receipts)
  1261	        for row in (
  1262	            wrong_epoch[indexes["open"]]["slots"]["pre"],
  1263	            wrong_epoch[indexes["pre"]],
  1264	        ):
  1265	            row["t1_bindings"]["os_build"] = "wrong-os-build"
  1266	            row["identity_epoch"]["os_build"] = "wrong-os-build"
  1267	        variants["epoch"] = (
  1268	            self._rechain(wrong_epoch),
  1269	            ("calibration_bracket_binding_invalid",),
  1270	        )
  1271	
  1272	        for name, (receipts, expected_reasons) in variants.items():
  1273	            with self.subTest(vector=name):
  1274	                snapshot = self._variant_snapshot(receipts)
  1275	                binding = build_calibration_bracket_binding(
  1276	                    snapshot,
  1277	                    session_id=gamma["session_id"],
  1278	                    window_id=gamma["window_id"],
  1279	                    plan_id=gamma["plan_id"],
  1280	                    plan_sha256=gamma["plan_sha256"],
  1281	                    evidence_root_id=gamma["evidence_root_id"],
  1282	                    runs_root=gamma["runs_root"],
  1283	                )
  1284	                _result, reasons = self._evaluate(
  1285	                    "gamma",
  1286	                    snapshot=snapshot,
  1287	                    candidates=self._discover(snapshot),
  1288	                    binding=binding,
  1289	                )
  1290	                self.assertEqual(reasons, expected_reasons)
  1291	
  1292	    def test_refuses_systematic_classification(self) -> None:
  1293	        window = {
  1294	            "session_id": "session-d117-systematic",
  1295	            "window_id": "plan-d117-systematic-refusal",
  1296	            "plan_id": "plan-d117-systematic-refusal",
  1297	            "plan_sha256": "d" * 64,
  1298	            "evidence_root_id": "evidence-d117-systematic-refusal",
  1299	            "runs_root": "/synthetic/d117/systematic-refusal",
  1300	        }
  1301	        attempts = {
  1302	            slot: f"d117-systematic-{slot}" for slot in ("pre", "post")
  1303	        }
  1304	        slots = {
  1305	            slot: {
  1306	                "attempt_id": attempts[slot],
  1307	                "custody_locator": (
  1308	                    f"{window['runs_root']}/instrument_validation/{attempts[slot]}"
  1309	                ),
  1310	                "identity_epoch": self.epoch,
  1311	                "t1_bindings": self.t1,
  1312	            }
  1313	            for slot in ("pre", "post")
  1314	        }
  1315	        append_bracket_session_receipt(
  1316	            self.ledger,
  1317	            **window,
  1318	            slots=slots,
  1319	            head_pin_path=self.pin,
  1320	            require_committed_pin=False,
  1321	        )
  1322	        claim_bracket_session_slot(
  1323	            self.ledger,
  1324	            session_id=window["session_id"],
  1325	            slot="pre",
  1326	            attempt_id=attempts["pre"],
  1327	            claim_id="synthetic-systematic-pre-claim",
  1328	        )
  1329	        finalize_bracket_session_slot(
  1330	            self.ledger,
  1331	            session_id=window["session_id"],
  1332	            slot="pre",
  1333	            disposition="systematic-invalid",
  1334	            custody_locator=slots["pre"]["custody_locator"],
  1335	            artifact_sha256=_content_hashes(attempts["pre"]),
  1336	            identity_epoch=self.epoch,
  1337	            t1_bindings=self.t1,
  1338	            capture_wall_time_s="170.0",
  1339	            exact_bound_lexeme_s="0.040000",
  1340	        )
  1341	        abort_bracket_session(
  1342	            self.ledger,
  1343	            session_id=window["session_id"],
  1344	            reason="synthetic systematic preflight refusal",
  1345	        )
  1346	        self.pin.write_bytes(
  1347	            _pin_bytes(
  1348	                terminal_head_pin_for_session(
  1349	                    self.ledger, session_id=window["session_id"]
  1350	                )
  1351	            )
  1352	        )
  1353	        snapshot = self._load_snapshot()
  1354	        candidates = self._discover(snapshot)
  1355	        result, reasons = self._evaluate(
  1356	            "alpha", snapshot=snapshot, candidates=candidates
  1357	        )
  1358	        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
  1359	        self.assertIn(
  1360	            "new_systematic_failure_challenges_preflight_screen",
  1361	            result["acceptance"]["prospective_rederivation"][
  1362	                "observed_triggers"
  1363	            ],
  1364	        )
  1365	
  1366	    @unittest.skip("U2 successor engine pending")
  1367	    def test_range_expanding_live_observation_requires_successor(self) -> None:
  1368	        vector = self.scenario["staged_successor_vectors"][
  1369	            "range_expanding_live_observation"
  1370	        ]
  1371	        self.assertEqual(
  1372	            vector["expected_trigger"],
  1373	            "new_valid_same_identity_capture_expands_observed_range",
  1374	        )
  1375	
  1376	    @unittest.skip("U2 successor engine pending")
  1377	    def test_d102_observation_count_boundary_requires_successor(self) -> None:
  1378	        vector = self.scenario["staged_successor_vectors"][
  1379	            "d102_count_boundary"
  1380	        ]
  1381	        self.assertEqual(vector["expected_total_valid_same_epoch"], 38)
  1382	
  1383	    @unittest.skip("U2 successor engine pending")
  1384	    def test_successor_prior_set_refuses_omitted_or_changed_authenticated_prefix(
  1385	        self,
  1386	    ) -> None:
  1387	        vector = self.scenario["staged_successor_vectors"][
  1388	            "successor_prior_set_integrity"
  1389	        ]
  1390	        self.assertEqual(
  1391	            vector["mutations"],
  1392	            [
  1393	                "omit_authenticated_prefix_member",
  1394	                "change_authenticated_prefix_member",
  1395	            ],
  1396	        )
  1397	
  1398	
  1399	if __name__ == "__main__":
  1400	    unittest.main()

exec
/bin/zsh -lc "nl -ba tests/test_calibration_live_three_window.py | sed -n '679,970p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
   679	    def test_alpha_beta_gamma_each_bind_only_their_own_pre_post_pair(self) -> None:
   680	        for name, window in self.windows.items():
   681	            with self.subTest(window=name):
   682	                resolved = validate_calibration_bracket_binding(
   683	                    self.bindings[name],
   684	                    self.snapshot,
   685	                    window_id=window["window_id"],
   686	                    plan_id=window["plan_id"],
   687	                    plan_sha256=window["plan_sha256"],
   688	                    evidence_root_id=window["evidence_root_id"],
   689	                    runs_root=window["runs_root"],
   690	                )
   691	                self.assertIsNotNone(resolved)
   692	                result, reasons = self._evaluate(name)
   693	                self.assertEqual(reasons, ())
   694	                self.assertEqual(result["status"], "passed")
   695	                self.assertEqual(
   696	                    [result[slot]["attempt_id"] for slot in ("pre", "post")],
   697	                    [f"d117-{name}-pre", f"d117-{name}-post"],
   698	                )
   699	
   700	    def test_all_six_are_same_epoch_causal_fresh_protocol_and_t1_eligible(
   701	        self,
   702	    ) -> None:
   703	        observations = {
   704	            row.attempt_id: row
   705	            for row in self.snapshot.observations
   706	            if not row.is_historical_import
   707	        }
   708	        self.assertEqual(len(observations), 6)
   709	        for name, window in self.windows.items():
   710	            pre = observations[f"d117-{name}-pre"]
   711	            post = observations[f"d117-{name}-post"]
   712	            with self.subTest(window=name):
   713	                self.assertEqual(dict(pre.identity_epoch), self.epoch)
   714	                self.assertEqual(dict(post.identity_epoch), self.epoch)
   715	                self.assertEqual(dict(pre.t1_bindings), self.t1)
   716	                self.assertEqual(dict(post.t1_bindings), self.t1)
   717	                self.assertEqual(pre.t1_bindings["pulse_protocol_id"], PROTOCOL_ID)
   718	                self.assertEqual(post.t1_bindings["pulse_protocol_id"], PROTOCOL_ID)
   719	                self.assertLessEqual(float(pre.capture_wall_time_s), window["window_start_s"])
   720	                self.assertGreaterEqual(float(post.capture_wall_time_s), window["window_end_s"])
   721	                self.assertLessEqual(
   722	                    window["window_end_s"] - float(pre.capture_wall_time_s),
   723	                    MAX_AGE_S,
   724	                )
   725	                self.assertLessEqual(
   726	                    float(post.capture_wall_time_s) - window["window_start_s"],
   727	                    MAX_AGE_S,
   728	                )
   729	
   730	    def test_no_neighboring_endpoint_can_substitute_for_a_bound_endpoint(self) -> None:
   731	        names = list(self.windows)
   732	        for index, name in enumerate(names):
   733	            neighbor = names[(index + 1) % len(names)]
   734	            tampered = copy.deepcopy(self.bindings[name])
   735	            tampered["endpoints"]["post"] = copy.deepcopy(
   736	                self.bindings[neighbor]["endpoints"]["post"]
   737	            )
   738	            tampered = self._rehash_binding(tampered)
   739	            with self.subTest(window=name, neighbor=neighbor):
   740	                _result, reasons = self._evaluate(name, binding=tampered)
   741	                self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
   742	
   743	    def test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding(
   744	        self,
   745	    ) -> None:
   746	        beta = self.windows["beta"]
   747	        by_attempt = {candidate.attempt_id: candidate for candidate in self.candidates}
   748	        foreign_pre = by_attempt["d117-alpha-pre"]
   749	        foreign_post = by_attempt["d117-gamma-post"]
   750	        self.assertNotEqual(foreign_pre.bracket_runs_root, beta["runs_root"])
   751	        self.assertNotEqual(foreign_post.bracket_runs_root, beta["runs_root"])
   752	        self.assertLessEqual(foreign_pre.capture_wall_time_s, beta["window_start_s"])
   753	        self.assertGreaterEqual(foreign_post.capture_wall_time_s, beta["window_end_s"])
   754	
   755	        _result, reasons = self._evaluate("beta", binding=None)
   756	        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))
   757	
   758	        result, reasons = self._evaluate(
   759	            "beta", binding=self.bindings["beta"]
   760	        )
   761	        self.assertEqual(reasons, ())
   762	        self.assertEqual(
   763	            [result[slot]["attempt_id"] for slot in ("pre", "post")],
   764	            ["d117-beta-pre", "d117-beta-post"],
   765	        )
   766	        self.assertNotIn(
   767	            foreign_pre.attempt_id,
   768	            {result["pre"]["attempt_id"], result["post"]["attempt_id"]},
   769	        )
   770	        self.assertNotIn(
   771	            foreign_post.attempt_id,
   772	            {result["pre"]["attempt_id"], result["post"]["attempt_id"]},
   773	        )
   774	
   775	    def test_each_night_issues_its_verdict_at_a_committed_closeout(self) -> None:
   776	        expected = self.scenario["expected_live_extension"]
   777	        pin_commits = []
   778	        pin_digests = []
   779	        for index, vector in enumerate(expected["cross_window_openness"], start=1):
   780	            name = vector["closeout"]
   781	            snapshot = self.closeouts[name]["snapshot"]
   782	            pin_value = json.loads(self.closeouts[name]["pin_bytes"])
   783	            candidates = self._discover(snapshot)
   784	            candidate_window_ids = {
   785	                candidate.bracket_window_id for candidate in candidates
   786	            }
   787	            expected_window_ids = {
   788	                self.windows[window_name]["window_id"]
   789	                for window_name in vector["candidate_windows"]
   790	            }
   791	            with self.subTest(closeout=name):
   792	                self.assertEqual(snapshot.refusal_reasons, ())
   793	                self.assertEqual(len(snapshot.bracket_sessions), index)
   794	                self.assertEqual(
   795	                    len(
   796	                        [
   797	                            observation
   798	                            for observation in snapshot.observations
   799	                            if not observation.is_historical_import
   800	                        ]
   801	                    ),
   802	                    index * 2,
   803	                )
   804	                self.assertEqual(
   805	                    snapshot.head_sequence,
   806	                    self.base_sequence + index * _PRODUCTION_RECEIPTS_PER_SESSION,
   807	                )
   808	                self.assertEqual(pin_value["sequence"], snapshot.head_sequence)
   809	                self.assertEqual(pin_value["head_digest"], snapshot.head_digest)
   810	                self.assertEqual(candidate_window_ids, expected_window_ids)
   811	                result, reasons = self._evaluate(
   812	                    name,
   813	                    snapshot=snapshot,
   814	                    candidates=candidates,
   815	                    binding=self.bindings[name],
   816	                )
   817	                self.assertEqual(reasons, ())
   818	                self.assertEqual(result["status"], "passed")
   819	                self.assertEqual(
   820	                    result["acceptance"]["ledger_snapshot"]["sequence"],
   821	                    snapshot.head_sequence,
   822	                )
   823	            pin_commits.append(self.closeouts[name]["pin_commit"])
   824	            pin_digests.append(pin_value["head_digest"])
   825	        self.assertEqual(len(set(pin_commits)), _LIVE_SESSION_COUNT)
   826	        self.assertEqual(len(set(pin_digests)), _LIVE_SESSION_COUNT)
   827	
   828	    def test_final_closeout_replays_all_verdicts_with_complete_universe(self) -> None:
   829	        snapshots = []
   830	        for name in self.windows:
   831	            result, reasons = self._evaluate(name, candidates=self.candidates)
   832	            self.assertEqual(reasons, ())
   833	            snapshots.append(result["acceptance"]["ledger_snapshot"])
   834	        self.assertEqual(snapshots, [snapshots[0]] * 3)
   835	        self.assertEqual(snapshots[0]["sequence"], _EXPECTED_TERMINAL_SEQUENCE)
   836	        for name in self.windows:
   837	            _result, reasons = self._evaluate(
   838	                name, candidates=self.candidates[:-1]
   839	            )
   840	            self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))
   841	
   842	    def test_production_writer_receipts_end_at_derived_terminal_sequence(self) -> None:
   843	        live = self.snapshot.receipts[self.base_sequence :]
   844	        expected = self.scenario["expected_live_extension"]
   845	        receipt_model = expected["receipt_model_supersession"]["landed"]
   846	        self.assertEqual(self.snapshot.head_sequence, _EXPECTED_TERMINAL_SEQUENCE)
   847	        self.assertEqual(
   848	            len(live),
   849	            expected["session_count"] * _PRODUCTION_RECEIPTS_PER_SESSION,
   850	        )
   851	        self.assertEqual(
   852	            receipt_model["receipts_per_session"],
   853	            _PRODUCTION_RECEIPTS_PER_SESSION,
   854	        )
   855	        for index, window in enumerate(self.windows.values()):
   856	            start = index * _PRODUCTION_RECEIPTS_PER_SESSION
   857	            rows = live[start : start + _PRODUCTION_RECEIPTS_PER_SESSION]
   858	            self.assertEqual(
   859	                [row["event"] for row in rows],
   860	                [
   861	                    BRACKET_SESSION_OPEN_EVENT,
   862	                    BRACKET_SESSION_SLOT_CLAIM_EVENT,
   863	                    BRACKET_SESSION_FINALIZATION_EVENT,
   864	                    BRACKET_SESSION_SLOT_CLAIM_EVENT,
   865	                    BRACKET_SESSION_FINALIZATION_EVENT,
   866	                ],
   867	            )
   868	            self.assertEqual({row["session_id"] for row in rows}, {window["session_id"]})
   869	            self.assertEqual(
   870	                [row["slot"] for row in rows[1:]],
   871	                ["pre", "pre", "post", "post"],
   872	            )
   873	        live_observations = [
   874	            observation
   875	            for observation in self.snapshot.observations
   876	            if not observation.is_historical_import
   877	        ]
   878	        self.assertEqual(
   879	            len(self.snapshot.bracket_sessions), expected["session_count"]
   880	        )
   881	        self.assertEqual(
   882	            {session.state for session in self.snapshot.bracket_sessions},
   883	            {"finalized"},
   884	        )
   885	        self.assertEqual(
   886	            len(live_observations), expected["live_observation_count"]
   887	        )
   888	        self.assertTrue(
   889	            all(
   890	                observation.observation_kind == "bracket-session-finalized"
   891	                and observation.disposition == "valid"
   892	                for observation in live_observations
   893	            )
   894	        )
   895	
   896	    def test_d110_allowance_selects_both_max_operands_across_windows(self) -> None:
   897	        expected = self.scenario["expected_live_extension"]
   898	        by_attempt = {candidate.attempt_id: candidate for candidate in self.candidates}
   899	        for vector in expected["allowance_branch_vectors"]:
   900	            name = vector["window"]
   901	            overridden = dict(by_attempt)
   902	            for slot in ("pre", "post"):
   903	                attempt_id = f"d117-{name}-{slot}"
   904	                overridden[attempt_id] = replace(
   905	                    overridden[attempt_id],
   906	                    b_fiducial_s=vector[f"{slot}_bound_s"],
   907	                )
   908	            candidates = tuple(
   909	                overridden[candidate.attempt_id] for candidate in self.candidates
   910	            )
   911	            with self.subTest(window=name, branch=vector["branch"]):
   912	                observed = Decimal(vector["observed_drift_s"])
   913	                screen = Decimal(expected["never_zero_allowance_s"])
   914	                if vector["branch"] == "bracket_screen_s":
   915	                    self.assertLess(observed, screen)
   916	                else:
   917	                    self.assertEqual(vector["branch"], "observed_drift_s")
   918	                    self.assertGreater(observed, screen)
   919	                result, reasons = self._evaluate(name, candidates=candidates)
   920	                self.assertEqual(reasons, ())
   921	                allowance = result["acceptance"]["allowance"]
   922	                self.assertEqual(allowance["rule"], expected["allowance_rule"])
   923	                self.assertEqual(
   924	                    result["acceptance"]["drift"]["observed_s"],
   925	                    vector["observed_drift_s"],
   926	                )
   927	                self.assertEqual(
   928	                    allowance["value_s"], vector["selected_allowance_s"]
   929	                )
   930	                self.assertEqual(allowance["embedding_count"], 1)
   931	
   932	    def test_no_failure_campaign_has_36_valid_observations_two_short_of_trigger(
   933	        self,
   934	    ) -> None:
   935	        expected = self.scenario["expected_live_extension"][
   936	            "valid_observation_count"
   937	        ]
   938	        issuance_valid = {
   939	            observation.content_id
   940	            for observation in self.snapshot.observations
   941	            if observation.is_historical_import
   942	            and observation.disposition == "valid"
   943	            and dict(observation.identity_epoch) == self.epoch
   944	        }
   945	        valid_same_epoch = {
   946	            observation.content_id
   947	            for observation in self.snapshot.observations
   948	            if observation.disposition == "valid"
   949	            and dict(observation.identity_epoch) == self.epoch
   950	        }
   951	        self.assertEqual(len(issuance_valid), expected["issuance"])
   952	        self.assertEqual(
   953	            len(valid_same_epoch), expected["after_three_live_windows"]
   954	        )
   955	        self.assertEqual(
   956	            expected["corpus_doubling_trigger"] - len(valid_same_epoch),
   957	            expected["shortfall"],
   958	        )
   959	        for name in self.windows:
   960	            result, reasons = self._evaluate(name)
   961	            self.assertEqual(reasons, ())
   962	            self.assertNotIn(
   963	                "corpus_doubles_from_19_to_38",
   964	                result["acceptance"]["prospective_rederivation"][
   965	                    "observed_triggers"
   966	                ],
   967	            )
   968	
   969	    def test_refuses_import_marker_removal_import_leakage_or_discovery_regression(
   970	        self,

exec
/bin/zsh -lc 'git branch -a --contains f665dd4 && git show --stat --oneline 4b82180 && git diff --unified=80 50404be..4b82180 -- tests/test_calibration_live_three_window.py tests/fixtures/calibration_live_three_window/scenario.json' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
+ impl/d117-u1-ledger-session
+ impl/d117-u2-successor
* impl/d117-u4-regression
  remotes/origin/impl/d117-u1-ledger-session
  remotes/origin/impl/d117-u2-successor
  remotes/origin/impl/d117-u4-regression
4b82180 U4 amendment round (FIX-A..F): terminal sequence DERIVED from production receipt count (76 + 3x5 = 91, superseding the memo's stale 85 three-receipt model); allowance test now straddles the 0.010818 bound so both max() branches are exercised; L5 named; positive count oracle; per-window verdict issuance; real discovery-authority test
 .../calibration_live_three_window/scenario.json    |  61 ++-
 tests/test_calibration_live_three_window.py        | 472 ++++++++++++++++++---
 2 files changed, 482 insertions(+), 51 deletions(-)
diff --git a/tests/fixtures/calibration_live_three_window/scenario.json b/tests/fixtures/calibration_live_three_window/scenario.json
index b8e02f1..07769bc 100644
--- a/tests/fixtures/calibration_live_three_window/scenario.json
+++ b/tests/fixtures/calibration_live_three_window/scenario.json
@@ -8,106 +8,161 @@
       "valid": 30,
       "systematic-invalid": 2,
       "ordinary-invalid": 6
     },
     "synthetic_additions_to_n19_derivation_corpus": {
       "valid": 11,
       "systematic-invalid": 2,
       "ordinary-invalid": 6
     }
   },
   "identity_epoch": {
     "os_build": "synthetic-d117-os",
     "hardware_model": "synthetic-d117-mac",
     "power_policy": "synthetic-ac-high-power",
     "sampling_interval_ms": 100,
     "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
     "pulse_protocol_id": "powermetrics_pulse_fiducial_v3"
   },
   "t1_bindings": {
     "hardware_model": "synthetic-d117-mac",
     "os_build": "synthetic-d117-os",
     "powermetrics_sha256": "c2f8ef614953475fcc9af95b6aaaf1d5b8c43a0f4c682f72f56c6503945b3b94",
     "sampling_interval_ms": 100,
     "anchor_method_version": "powermetrics_native_second_censored_intersection_v1",
     "mlx_version": "synthetic-mlx",
     "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
     "power_policy": "synthetic-ac-high-power",
     "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
     "protocol_sha256": "9eaf92f85136e234c56ea3ffd34392a73c313d4a092cabf308f5f5aaff9a31b1"
   },
   "windows": [
     {
       "name": "alpha",
       "session_id": "session-d117-alpha",
       "window_id": "plan-d117-floor-qwen25-1p5b-v1",
       "plan_id": "plan-d117-floor-qwen25-1p5b-v1",
       "plan_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
       "evidence_root_id": "evidence-d117-floor-qwen25-1p5b-v1",
       "runs_root": "/synthetic/d117/alpha",
       "window_start_s": 105.0,
       "window_end_s": 115.0,
       "pre_capture_s": 100.0,
       "post_capture_s": 120.0,
       "pre_bound_s": "0.025000",
       "post_bound_s": "0.026000"
     },
     {
       "name": "beta",
       "session_id": "session-d117-beta",
       "window_id": "plan-d117-floor-qwen25-7b-v1",
       "plan_id": "plan-d117-floor-qwen25-7b-v1",
       "plan_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
       "evidence_root_id": "evidence-d117-floor-qwen25-7b-v1",
       "runs_root": "/synthetic/d117/beta",
       "window_start_s": 125.0,
       "window_end_s": 135.0,
       "pre_capture_s": 121.0,
       "post_capture_s": 140.0,
       "pre_bound_s": "0.026500",
       "post_bound_s": "0.027000"
     },
     {
       "name": "gamma",
       "session_id": "session-d117-gamma",
       "window_id": "plan-d117-contrast-qwen25-1p5b-vs-7b-v1",
       "plan_id": "plan-d117-contrast-qwen25-1p5b-vs-7b-v1",
       "plan_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
       "evidence_root_id": "evidence-d117-contrast-qwen25-1p5b-vs-7b-v1",
       "runs_root": "/synthetic/d117/gamma",
       "window_start_s": 145.0,
       "window_end_s": 155.0,
       "pre_capture_s": 141.0,
       "post_capture_s": 160.0,
       "pre_bound_s": "0.028000",
       "post_bound_s": "0.029000"
     }
   ],
   "expected_live_extension": {
     "session_count": 3,
     "live_observation_count": 6,
-    "receipts_per_session": 3,
-    "terminal_sequence": 85,
+    "receipt_model_supersession": {
+      "superseded": {
+        "authority": "design-memo proposed three-receipt session model",
+        "receipts_per_session": 3,
+        "terminal_sequence": 85
+      },
+      "landed": {
+        "authority": "U1 production writer lifecycle",
+        "receipts_per_session": 5,
+        "events": [
+          "bracket-session-open",
+          "bracket-session-slot-claim:pre",
+          "bracket-session-slot-finalization:pre",
+          "bracket-session-slot-claim:post",
+          "bracket-session-slot-finalization:post"
+        ],
+        "terminal_sequence_oracle": "module-level _EXPECTED_TERMINAL_SEQUENCE derived by the production-path regression"
+      }
+    },
     "candidate_count": 6,
     "imported_candidate_count": 0,
     "allowance_rule": "max(observed_drift_s,bracket_screen_s)",
-    "never_zero_allowance_s": "0.010818"
+    "never_zero_allowance_s": "0.010818",
+    "valid_observation_count": {
+      "issuance": 30,
+      "after_three_live_windows": 36,
+      "corpus_doubling_trigger": 38,
+      "shortfall": 2
+    },
+    "allowance_branch_vectors": [
+      {
+        "window": "alpha",
+        "branch": "bracket_screen_s",
+        "pre_bound_s": "0.025000",
+        "post_bound_s": "0.026000",
+        "observed_drift_s": "0.001000",
+        "selected_allowance_s": "0.010818"
+      },
+      {
+        "window": "beta",
+        "branch": "observed_drift_s",
+        "pre_bound_s": "0.020000",
+        "post_bound_s": "0.031000",
+        "observed_drift_s": "0.011000",
+        "selected_allowance_s": "0.011000"
+      }
+    ],
+    "cross_window_openness": [
+      {
+        "closeout": "alpha",
+        "candidate_windows": ["alpha"]
+      },
+      {
+        "closeout": "beta",
+        "candidate_windows": ["alpha", "beta"]
+      },
+      {
+        "closeout": "gamma",
+        "candidate_windows": ["alpha", "beta", "gamma"]
+      }
+    ]
   },
   "staged_successor_vectors": {
     "range_expanding_live_observation": {
       "bound_s": "0.040000",
       "expected_trigger": "new_valid_same_identity_capture_expands_observed_range"
     },
     "d102_count_boundary": {
       "additional_valid_observations": 2,
       "expected_total_valid_same_epoch": 38,
       "expected_trigger": "corpus_doubles_from_19_to_38"
     },
     "successor_prior_set_integrity": {
       "mutations": [
         "omit_authenticated_prefix_member",
         "change_authenticated_prefix_member"
       ],
       "expected_outcome": "refuse"
     }
   }
 }
diff --git a/tests/test_calibration_live_three_window.py b/tests/test_calibration_live_three_window.py
index 5b78f20..6ff841e 100644
--- a/tests/test_calibration_live_three_window.py
+++ b/tests/test_calibration_live_three_window.py
@@ -1,276 +1,377 @@
 """Synthetic D-117 three-window live-ledger integration regression."""
 
 from __future__ import annotations
 
 import copy
 from dataclasses import replace
+from decimal import Decimal
 import hashlib
 import json
 from pathlib import Path
 import subprocess
 import tempfile
+from types import SimpleNamespace
 import unittest
 from unittest.mock import patch
 
 from joulewise.calibration_bracketing import (
     CalibrationCandidate,
     _canonical_sha256 as bracketing_canonical_sha256,
     _valid_acceptance_bound,
     build_calibration_bracket_binding,
+    calibration_bracket_for_bundles,
     discover_calibration_candidates,
     evaluate_calibration_bracket,
     load_calibration_acceptance_bound,
     validate_calibration_bracket_binding,
 )
 from joulewise.calibration_ledger import (
     BRACKET_SESSION_FINALIZATION_EVENT,
     BRACKET_SESSION_OPEN_EVENT,
+    BRACKET_SESSION_SLOT_CLAIM_EVENT,
+    GOVERNED_ARTIFACTS,
     HISTORICAL_IMPORT_FINALIZATION_EVENT,
     HISTORICAL_IMPORT_RESERVATION_EVENT,
     LEDGER_SCHEMA,
     RECEIPT_SCHEMA,
     abort_bracket_session,
     append_bracket_session_receipt,
     canonical_json_bytes,
     canonical_sha256,
+    claim_bracket_session_slot,
     content_id_from_artifact_hashes,
     finalize_bracket_session_slot,
     load_calibration_ledger_snapshot,
     terminal_head_pin_for_session,
 )
 from joulewise.powermetrics_fiducial import (
     MAX_AGE_S,
     PROTOCOL_ID,
     PROTOCOL_V2_ID,
 )
 from joulewise.schemas import CalibrationBracketingPolicy
+from scripts import validate_powermetrics_fiducial as production_writer
 
 
 _FIXTURE = (
     Path(__file__).parent
     / "fixtures"
     / "calibration_live_three_window"
     / "scenario.json"
 )
 _USE_WINDOW_BINDING = object()
+_ISSUANCE_BASE_SEQUENCE = 76
+_LIVE_SESSION_COUNT = 3
+_PRODUCTION_RECEIPTS_PER_SESSION = 5
+_EXPECTED_TERMINAL_SEQUENCE = (
+    _ISSUANCE_BASE_SEQUENCE
+    + _LIVE_SESSION_COUNT * _PRODUCTION_RECEIPTS_PER_SESSION
+)
 
 
 def _hash(label: str) -> str:
     return hashlib.sha256(label.encode("utf-8")).hexdigest()
 
 
 def _content_hashes(label: str) -> dict[str, str]:
     return {
         "manifest.json": _hash(f"{label}:manifest"),
         "instrument_evidence.json": _hash(f"{label}:evidence"),
     }
 
 
 def _receipt(core: dict) -> dict:
     value = copy.deepcopy(core)
     value.pop("receipt_digest", None)
     value["receipt_digest"] = canonical_sha256(value)
     return value
 
 
 def _ledger_bytes(receipts: list[dict]) -> bytes:
     return b"".join(canonical_json_bytes(row) + b"\n" for row in receipts)
 
 
 def _pin_for(receipt: dict) -> dict:
     return {
         "sequence": receipt["sequence"],
         "head_digest": receipt["receipt_digest"],
         "ledger_schema": LEDGER_SCHEMA,
     }
 
 
 def _pin_bytes(pin: dict) -> bytes:
     return (json.dumps(pin, sort_keys=True) + "\n").encode("utf-8")
 
 
+def _write_synthetic_custody(custody: Path, label: str) -> None:
+    for relative in GOVERNED_ARTIFACTS:
+        path = custody / relative
+        path.parent.mkdir(parents=True, exist_ok=True)
+        path.write_bytes(f"{label}:{relative}".encode("utf-8"))
+
+
 class CalibrationLiveThreeWindowTests(unittest.TestCase):
     """Exercise one issuance-equivalent prefix and its three live sessions."""
 
     @classmethod
     def setUpClass(cls) -> None:
         cls.scenario = json.loads(_FIXTURE.read_text(encoding="utf-8"))
         cls.epoch = dict(cls.scenario["identity_epoch"])
         cls.t1 = dict(cls.scenario["t1_bindings"])
+
+        cls._class_tmp = tempfile.TemporaryDirectory()
+        root = Path(cls._class_tmp.name)
+        runtime_windows = []
+        for source in cls.scenario["windows"]:
+            window = copy.deepcopy(source)
+            window["runs_root"] = str(root / "night-roots" / window["name"])
+            runtime_windows.append(window)
         cls.windows = {
-            row["name"]: row for row in cls.scenario["windows"]
+            row["name"]: row for row in runtime_windows
         }
         cls.policy = CalibrationBracketingPolicy(
             require_bracket=True,
             calibration_bracket_max_drift_s=0.010,
         )
 
         source = load_calibration_acceptance_bound()
         if source is None:
             raise AssertionError("checked-in issued acceptance artifact is unavailable")
         source_path = Path(
             "configs/calibration/calibration_acceptance_d079_v2.json"
         )
         if hashlib.sha256(source_path.read_bytes()).hexdigest() != cls.scenario[
             "source_acceptance_sha256"
         ]:
             raise AssertionError("fixture source acceptance pin drifted")
 
         base_receipts, acceptance = cls._build_issuance_equivalent_base(source)
         cls.base_receipts = base_receipts
         cls.acceptance = acceptance
         cls.base_sequence = len(base_receipts)
         cls.base_digest = base_receipts[-1]["receipt_digest"]
 
-        cls._class_tmp = tempfile.TemporaryDirectory()
-        root = Path(cls._class_tmp.name)
-        ledger = root / "ledger.jsonl"
-        pin = root / "head.json"
+        ledger = root / "runs" / "ledger.jsonl"
+        pin = root / "configs" / "calibration" / "head.json"
+        ledger.parent.mkdir(parents=True)
+        pin.parent.mkdir(parents=True)
         ledger.write_bytes(_ledger_bytes(base_receipts))
         pin.write_bytes(_pin_bytes(_pin_for(base_receipts[-1])))
 
+        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
+        subprocess.run(
+            ["git", "config", "user.email", "tests@joulewise.invalid"],
+            cwd=root,
+            check=True,
+        )
+        subprocess.run(
+            ["git", "config", "user.name", "JouleWise tests"],
+            cwd=root,
+            check=True,
+        )
+        subprocess.run(
+            ["git", "add", pin.relative_to(root).as_posix()],
+            cwd=root,
+            check=True,
+        )
+        subprocess.run(
+            ["git", "commit", "-qm", "pin issuance-equivalent head"],
+            cwd=root,
+            check=True,
+        )
+
         bindings: dict[str, dict] = {}
-        for window in cls.scenario["windows"]:
+        closeouts: dict[str, dict] = {}
+        for window in runtime_windows:
             attempts = {
                 slot: f"d117-{window['name']}-{slot}" for slot in ("pre", "post")
             }
             slots = {
                 slot: {
                     "attempt_id": attempts[slot],
                     "custody_locator": (
                         f"{window['runs_root']}/instrument_validation/"
                         f"{attempts[slot]}"
                     ),
                     "identity_epoch": cls.epoch,
                     "t1_bindings": cls.t1,
                 }
                 for slot in ("pre", "post")
             }
             append_bracket_session_receipt(
                 ledger,
                 session_id=window["session_id"],
                 window_id=window["window_id"],
                 plan_id=window["plan_id"],
                 plan_sha256=window["plan_sha256"],
                 evidence_root_id=window["evidence_root_id"],
                 runs_root=window["runs_root"],
                 slots=slots,
                 head_pin_path=pin,
-                require_committed_pin=False,
+                require_committed_pin=True,
+                repo_root=root,
             )
             for slot in ("pre", "post"):
-                finalize_bracket_session_slot(
-                    ledger,
-                    session_id=window["session_id"],
-                    slot=slot,
-                    disposition="valid",
+                lifecycle = production_writer._CaptureLedgerLifecycle(
+                    ledger_path=ledger,
+                    head_pin_path=pin,
+                    attempt_id=attempts[slot],
                     custody_locator=slots[slot]["custody_locator"],
-                    artifact_sha256=_content_hashes(attempts[slot]),
                     identity_epoch=cls.epoch,
                     t1_bindings=cls.t1,
-                    capture_wall_time_s=str(window[f"{slot}_capture_s"]),
-                    exact_bound_lexeme_s=window[f"{slot}_bound_s"],
+                    session_id=window["session_id"],
+                    slot=slot,
+                    require_committed_pin=False,
                 )
-            pin_value = terminal_head_pin_for_session(
-                ledger, session_id=window["session_id"]
-            )
+                # The synthetic issuance prefix has hash-only import custody.
+                # Keep that fixture boundary while exercising the production
+                # writer's reservation validation, exclusive claim, and
+                # finalization path for every live endpoint.
+                def load_without_import_custody(*args, **kwargs):
+                    kwargs["verify_custody"] = False
+                    return load_calibration_ledger_snapshot(*args, **kwargs)
+
+                with patch.object(
+                    production_writer,
+                    "load_calibration_ledger_snapshot",
+                    side_effect=load_without_import_custody,
+                ):
+                    lifecycle.begin()
+                _write_synthetic_custody(
+                    Path(slots[slot]["custody_locator"]), attempts[slot]
+                )
+                lifecycle.capture_wall_time_s = str(
+                    window[f"{slot}_capture_s"]
+                )
+                lifecycle.exact_bound_lexeme_s = window[f"{slot}_bound_s"]
+                _receipt_value, terminal_pin = lifecycle.finalize("valid")
+                if slot == "pre":
+                    if terminal_pin is not None:
+                        raise AssertionError("pre finalization emitted a terminal pin")
+                elif terminal_pin is None:
+                    raise AssertionError("post finalization omitted its terminal pin")
+            pin_value = terminal_pin
             pin.write_bytes(_pin_bytes(pin_value))
-            terminal_snapshot = load_calibration_ledger_snapshot(
+            subprocess.run(
+                ["git", "add", pin.relative_to(root).as_posix()],
+                cwd=root,
+                check=True,
+            )
+            subprocess.run(
+                ["git", "commit", "-qm", f"pin {window['name']} closeout"],
+                cwd=root,
+                check=True,
+            )
+            closeout_snapshot = load_calibration_ledger_snapshot(
                 ledger,
                 pin,
                 baseline_sequence=cls.base_sequence,
                 baseline_digest=cls.base_digest,
-                require_committed_pin=False,
+                require_committed_pin=True,
                 verify_custody=False,
+                repo_root=root,
             )
             bindings[window["name"]] = build_calibration_bracket_binding(
-                terminal_snapshot,
+                closeout_snapshot,
                 session_id=window["session_id"],
                 window_id=window["window_id"],
                 plan_id=window["plan_id"],
                 plan_sha256=window["plan_sha256"],
                 evidence_root_id=window["evidence_root_id"],
                 runs_root=window["runs_root"],
             )
+            closeouts[window["name"]] = {
+                "snapshot": closeout_snapshot,
+                "ledger_bytes": ledger.read_bytes(),
+                "pin_bytes": pin.read_bytes(),
+                "pin_commit": subprocess.run(
+                    ["git", "rev-parse", "HEAD"],
+                    cwd=root,
+                    check=True,
+                    capture_output=True,
+                    text=True,
+                ).stdout.strip(),
+            }
 
         cls.bindings = bindings
+        cls.closeouts = closeouts
         cls.final_ledger_bytes = ledger.read_bytes()
         cls.final_pin_bytes = pin.read_bytes()
 
     @classmethod
     def tearDownClass(cls) -> None:
         cls._class_tmp.cleanup()
 
     @classmethod
     def _build_issuance_equivalent_base(
         cls, source: dict
     ) -> tuple[list[dict], dict]:
         artifact = copy.deepcopy(source)
         artifact["identity_epoch"] = dict(cls.epoch)
         artifact["prior_observation_set"]["epoch_catalog"] = {
             "d079_epoch": dict(cls.epoch)
         }
 
         observations: list[dict] = []
         receipt_members: list[dict] = []
         for member in artifact["derivation_corpus"]["members"]:
             hashes = {
                 "manifest.json": member["manifest_sha256"],
                 "instrument_evidence.json": member[
                     "instrument_evidence_sha256"
                 ],
             }
             content_id = content_id_from_artifact_hashes(hashes)
             if content_id is None:
                 raise AssertionError("derivation member lacks a content identity")
             receipt_members.append(
                 {
                     "attempt_id": member["member_id"],
                     "content_id": content_id,
                     "artifact_sha256": hashes,
                     "disposition": "valid",
                     "bound_s": member["b_fiducial_s"],
                 }
             )
 
         additions = cls.scenario["issuance_equivalent_base"][
             "synthetic_additions_to_n19_derivation_corpus"
         ]
         for disposition, count in additions.items():
             for index in range(count):
                 attempt_id = f"synthetic-import-{disposition}-{index:02d}"
                 hashes = _content_hashes(attempt_id)
                 content_id = content_id_from_artifact_hashes(hashes)
                 if content_id is None:
                     raise AssertionError("synthetic import lacks a content identity")
                 receipt_members.append(
                     {
                         "attempt_id": attempt_id,
                         "content_id": content_id,
                         "artifact_sha256": hashes,
                         "disposition": disposition,
                         "bound_s": (
                             "0.040000"
                             if disposition == "systematic-invalid"
                             else "0.026000"
                         ),
                     }
                 )
 
         receipts: list[dict] = []
         predecessor = "0" * 64
         import_inputs = {
             "disposition_table": _hash("synthetic-d117-disposition-table"),
             "custody_manifest": _hash("synthetic-d117-custody-manifest"),
         }
         for index, member in enumerate(
             sorted(receipt_members, key=lambda row: row["attempt_id"]), start=1
         ):
             custody = f"/synthetic/d117/import/{member['attempt_id']}"
             reservation = _receipt(
                 {
                     "schema_version": RECEIPT_SCHEMA,
                     "ledger_schema": LEDGER_SCHEMA,
                     "sequence": len(receipts) + 1,
                     "predecessor_digest": predecessor,
                     "event": HISTORICAL_IMPORT_RESERVATION_EVENT,
@@ -400,625 +501,900 @@ class CalibrationLiveThreeWindowTests(unittest.TestCase):
             bracket_window_id=observation.bracket_window_id,
             bracket_plan_id=observation.bracket_plan_id,
             bracket_plan_sha256=observation.bracket_plan_sha256,
             bracket_evidence_root_id=observation.bracket_evidence_root_id,
             bracket_runs_root=observation.bracket_runs_root,
         )
 
     def _discover(self, snapshot):
         with patch(
             "joulewise.calibration_bracketing._candidate_from_observation",
             side_effect=self._candidate,
         ):
             return discover_calibration_candidates(snapshot)
 
     def _evaluate(
         self,
         window_name: str,
         *,
         snapshot=None,
         candidates=None,
         binding=_USE_WINDOW_BINDING,
         bindings=None,
     ):
         window = self.windows[window_name]
         selected_binding = (
             self.bindings[window_name]
             if binding is _USE_WINDOW_BINDING
             else binding
         )
         with patch(
             "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
             return_value=self.acceptance,
         ):
             return evaluate_calibration_bracket(
                 self.candidates if candidates is None else candidates,
                 window_start_s=window["window_start_s"],
                 window_end_s=window["window_end_s"],
                 bindings=self.t1 if bindings is None else bindings,
                 policy=self.policy,
                 ledger_snapshot=self.snapshot if snapshot is None else snapshot,
                 bracket_binding=selected_binding,
                 bracket_window_id=window["window_id"],
                 bracket_plan_id=window["plan_id"],
                 bracket_plan_sha256=window["plan_sha256"],
                 bracket_evidence_root_id=window["evidence_root_id"],
                 bracket_runs_root=window["runs_root"],
             )
 
     def _variant_snapshot(self, receipts: list[dict], pin: dict | None = None):
         self.ledger.write_bytes(_ledger_bytes(receipts))
         if pin is None:
             pin = _pin_for(receipts[-1])
         self.pin.write_bytes(_pin_bytes(pin))
         return self._load_snapshot()
 
     @staticmethod
     def _rechain(receipts: list[dict]) -> list[dict]:
         result: list[dict] = []
         predecessor = "0" * 64
         for sequence, source in enumerate(receipts, start=1):
             row = copy.deepcopy(source)
             row["sequence"] = sequence
             row["predecessor_digest"] = predecessor
             row = _receipt(row)
             result.append(row)
             predecessor = row["receipt_digest"]
         return result
 
     @staticmethod
     def _rehash_binding(binding: dict) -> dict:
         value = copy.deepcopy(binding)
         value["binding_digest"] = bracketing_canonical_sha256(
             {
                 key: item
                 for key, item in value.items()
                 if key != "binding_digest"
             }
         )
         return value
 
+    def _receipt_index(
+        self, session_id: str, event: str, slot: str | None = None
+    ) -> int:
+        return next(
+            index
+            for index, row in enumerate(self.receipts)
+            if row.get("session_id") == session_id
+            and row.get("event") == event
+            and (slot is None or row.get("slot") == slot)
+        )
+
     def test_issuance_equivalent_base_has_76_receipts_and_30_2_6_dispositions(
         self,
     ) -> None:
         expected = self.scenario["issuance_equivalent_base"]
         prefix = self.snapshot.receipts[: self.base_sequence]
         imported = [
             row
             for row in self.snapshot.observations
             if row.sequence <= self.base_sequence
         ]
         counts = {
             disposition: sum(row.disposition == disposition for row in imported)
             for disposition in ("valid", "systematic-invalid", "ordinary-invalid")
         }
+        self.assertEqual(self.base_sequence, _ISSUANCE_BASE_SEQUENCE)
         self.assertEqual(len(prefix), expected["receipt_count"])
         self.assertEqual(len(imported), expected["observation_count"])
         self.assertEqual(counts, expected["disposition_counts"])
         self.assertTrue(all(row.is_historical_import for row in imported))
 
     def test_exactly_six_live_candidates_and_zero_imported_candidates(self) -> None:
         with patch(
             "joulewise.calibration_bracketing._candidate_from_observation",
             side_effect=self._candidate,
         ) as authenticate:
             candidates = discover_calibration_candidates(self.snapshot)
         authenticated_attempts = {
             call.args[0].attempt_id for call in authenticate.call_args_list
         }
         imported_attempts = {
             row.attempt_id
             for row in self.snapshot.observations
             if row.is_historical_import
         }
-        self.assertEqual(len(candidates), 6)
+        expected = self.scenario["expected_live_extension"]
+        self.assertEqual(len(candidates), expected["candidate_count"])
         self.assertEqual(authenticated_attempts & imported_attempts, set())
         self.assertTrue(all(candidate.bracket_session_id for candidate in candidates))
 
+    def test_bundle_path_uses_ledger_discovery_as_candidate_authority(self) -> None:
+        window = self.windows["gamma"]
+        reader = SimpleNamespace(
+            measured_window=lambda: SimpleNamespace(
+                start_s=window["window_start_s"],
+                end_s=window["window_end_s"],
+            ),
+            metadata=lambda: {
+                "instrument_calibration": {"bindings": dict(self.t1)}
+            },
+        )
+        with (
+            patch(
+                "joulewise.calibration_bracketing.BundleReader",
+                return_value=reader,
+            ),
+            patch(
+                "joulewise.calibration_bracketing._candidate_from_observation",
+                side_effect=self._candidate,
+            ),
+            patch(
+                "joulewise.calibration_bracketing.discover_calibration_candidates",
+                wraps=discover_calibration_candidates,
+            ) as discover,
+            patch(
+                "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
+                return_value=self.acceptance,
+            ),
+        ):
+            result, reasons = calibration_bracket_for_bundles(
+                Path(window["runs_root"]),
+                [Path(window["runs_root"]) / "science-member"],
+                self.policy,
+                ledger_snapshot=self.snapshot,
+                bracket_binding=self.bindings["gamma"],
+                bracket_window_id=window["window_id"],
+                bracket_plan_id=window["plan_id"],
+                bracket_plan_sha256=window["plan_sha256"],
+                bracket_evidence_root_id=window["evidence_root_id"],
+            )
+        discover.assert_called_once_with(self.snapshot)
+        self.assertEqual(reasons, ())
+        self.assertEqual(result["status"], "passed")
+        self.assertEqual(
+            [result[slot]["attempt_id"] for slot in ("pre", "post")],
+            ["d117-gamma-pre", "d117-gamma-post"],
+        )
+
     def test_alpha_beta_gamma_each_bind_only_their_own_pre_post_pair(self) -> None:
         for name, window in self.windows.items():
             with self.subTest(window=name):
                 resolved = validate_calibration_bracket_binding(
                     self.bindings[name],
                     self.snapshot,
                     window_id=window["window_id"],
                     plan_id=window["plan_id"],
                     plan_sha256=window["plan_sha256"],
                     evidence_root_id=window["evidence_root_id"],
                     runs_root=window["runs_root"],
                 )
                 self.assertIsNotNone(resolved)
                 result, reasons = self._evaluate(name)
                 self.assertEqual(reasons, ())
                 self.assertEqual(result["status"], "passed")
                 self.assertEqual(
                     [result[slot]["attempt_id"] for slot in ("pre", "post")],
                     [f"d117-{name}-pre", f"d117-{name}-post"],
                 )
 
     def test_all_six_are_same_epoch_causal_fresh_protocol_and_t1_eligible(
         self,
     ) -> None:
         observations = {
             row.attempt_id: row
             for row in self.snapshot.observations
             if not row.is_historical_import
         }
         self.assertEqual(len(observations), 6)
         for name, window in self.windows.items():
             pre = observations[f"d117-{name}-pre"]
             post = observations[f"d117-{name}-post"]
             with self.subTest(window=name):
                 self.assertEqual(dict(pre.identity_epoch), self.epoch)
                 self.assertEqual(dict(post.identity_epoch), self.epoch)
                 self.assertEqual(dict(pre.t1_bindings), self.t1)
                 self.assertEqual(dict(post.t1_bindings), self.t1)
                 self.assertEqual(pre.t1_bindings["pulse_protocol_id"], PROTOCOL_ID)
                 self.assertEqual(post.t1_bindings["pulse_protocol_id"], PROTOCOL_ID)
                 self.assertLessEqual(float(pre.capture_wall_time_s), window["window_start_s"])
                 self.assertGreaterEqual(float(post.capture_wall_time_s), window["window_end_s"])
                 self.assertLessEqual(
                     window["window_end_s"] - float(pre.capture_wall_time_s),
                     MAX_AGE_S,
                 )
                 self.assertLessEqual(
                     float(post.capture_wall_time_s) - window["window_start_s"],
                     MAX_AGE_S,
                 )
 
     def test_no_neighboring_endpoint_can_substitute_for_a_bound_endpoint(self) -> None:
         names = list(self.windows)
         for index, name in enumerate(names):
             neighbor = names[(index + 1) % len(names)]
             tampered = copy.deepcopy(self.bindings[name])
             tampered["endpoints"]["post"] = copy.deepcopy(
                 self.bindings[neighbor]["endpoints"]["post"]
             )
             tampered = self._rehash_binding(tampered)
             with self.subTest(window=name, neighbor=neighbor):
                 _result, reasons = self._evaluate(name, binding=tampered)
                 self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
 
-    def test_all_three_verdicts_use_one_complete_candidate_universe(self) -> None:
+    def test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding(
+        self,
+    ) -> None:
+        beta = self.windows["beta"]
+        by_attempt = {candidate.attempt_id: candidate for candidate in self.candidates}
+        foreign_pre = by_attempt["d117-alpha-pre"]
+        foreign_post = by_attempt["d117-gamma-post"]
+        self.assertNotEqual(foreign_pre.bracket_runs_root, beta["runs_root"])
+        self.assertNotEqual(foreign_post.bracket_runs_root, beta["runs_root"])
+        self.assertLessEqual(foreign_pre.capture_wall_time_s, beta["window_start_s"])
+        self.assertGreaterEqual(foreign_post.capture_wall_time_s, beta["window_end_s"])
+
+        _result, reasons = self._evaluate("beta", binding=None)
+        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))
+
+        result, reasons = self._evaluate(
+            "beta", binding=self.bindings["beta"]
+        )
+        self.assertEqual(reasons, ())
+        self.assertEqual(
+            [result[slot]["attempt_id"] for slot in ("pre", "post")],
+            ["d117-beta-pre", "d117-beta-post"],
+        )
+        self.assertNotIn(
+            foreign_pre.attempt_id,
+            {result["pre"]["attempt_id"], result["post"]["attempt_id"]},
+        )
+        self.assertNotIn(
+            foreign_post.attempt_id,
+            {result["pre"]["attempt_id"], result["post"]["attempt_id"]},
+        )
+
+    def test_each_night_issues_its_verdict_at_a_committed_closeout(self) -> None:
+        expected = self.scenario["expected_live_extension"]
+        pin_commits = []
+        pin_digests = []
+        for index, vector in enumerate(expected["cross_window_openness"], start=1):
+            name = vector["closeout"]
+            snapshot = self.closeouts[name]["snapshot"]
+            pin_value = json.loads(self.closeouts[name]["pin_bytes"])
+            candidates = self._discover(snapshot)
+            candidate_window_ids = {
+                candidate.bracket_window_id for candidate in candidates
+            }
+            expected_window_ids = {
+                self.windows[window_name]["window_id"]
+                for window_name in vector["candidate_windows"]
+            }
+            with self.subTest(closeout=name):
+                self.assertEqual(snapshot.refusal_reasons, ())
+                self.assertEqual(len(snapshot.bracket_sessions), index)
+                self.assertEqual(
+                    len(
+                        [
+                            observation
+                            for observation in snapshot.observations
+                            if not observation.is_historical_import
+                        ]
+                    ),
+                    index * 2,
+                )
+                self.assertEqual(
+                    snapshot.head_sequence,
+                    self.base_sequence + index * _PRODUCTION_RECEIPTS_PER_SESSION,
+                )
+                self.assertEqual(pin_value["sequence"], snapshot.head_sequence)
+                self.assertEqual(pin_value["head_digest"], snapshot.head_digest)
+                self.assertEqual(candidate_window_ids, expected_window_ids)
+                result, reasons = self._evaluate(
+                    name,
+                    snapshot=snapshot,
+                    candidates=candidates,
+                    binding=self.bindings[name],
+                )
+                self.assertEqual(reasons, ())
+                self.assertEqual(result["status"], "passed")
+                self.assertEqual(
+                    result["acceptance"]["ledger_snapshot"]["sequence"],
+                    snapshot.head_sequence,
+                )
+            pin_commits.append(self.closeouts[name]["pin_commit"])
+            pin_digests.append(pin_value["head_digest"])
+        self.assertEqual(len(set(pin_commits)), _LIVE_SESSION_COUNT)
+        self.assertEqual(len(set(pin_digests)), _LIVE_SESSION_COUNT)
+
+    def test_final_closeout_replays_all_verdicts_with_complete_universe(self) -> None:
         snapshots = []
         for name in self.windows:
             result, reasons = self._evaluate(name, candidates=self.candidates)
             self.assertEqual(reasons, ())
             snapshots.append(result["acceptance"]["ledger_snapshot"])
         self.assertEqual(snapshots, [snapshots[0]] * 3)
-        self.assertEqual(snapshots[0]["sequence"], 85)
+        self.assertEqual(snapshots[0]["sequence"], _EXPECTED_TERMINAL_SEQUENCE)
         for name in self.windows:
             _result, reasons = self._evaluate(
                 name, candidates=self.candidates[:-1]
             )
             self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))
 
-    def test_ideal_three_receipt_sessions_end_at_terminal_sequence_85(self) -> None:
+    def test_production_writer_receipts_end_at_derived_terminal_sequence(self) -> None:
         live = self.snapshot.receipts[self.base_sequence :]
         expected = self.scenario["expected_live_extension"]
-        self.assertEqual(self.snapshot.head_sequence, expected["terminal_sequence"])
-        self.assertEqual(len(live), 9)
-        for index, window in enumerate(self.scenario["windows"]):
-            rows = live[index * 3 : index * 3 + 3]
+        receipt_model = expected["receipt_model_supersession"]["landed"]
+        self.assertEqual(self.snapshot.head_sequence, _EXPECTED_TERMINAL_SEQUENCE)
+        self.assertEqual(
+            len(live),
+            expected["session_count"] * _PRODUCTION_RECEIPTS_PER_SESSION,
+        )
+        self.assertEqual(
+            receipt_model["receipts_per_session"],
+            _PRODUCTION_RECEIPTS_PER_SESSION,
+        )
+        for index, window in enumerate(self.windows.values()):
+            start = index * _PRODUCTION_RECEIPTS_PER_SESSION
+            rows = live[start : start + _PRODUCTION_RECEIPTS_PER_SESSION]
             self.assertEqual(
                 [row["event"] for row in rows],
                 [
                     BRACKET_SESSION_OPEN_EVENT,
+                    BRACKET_SESSION_SLOT_CLAIM_EVENT,
                     BRACKET_SESSION_FINALIZATION_EVENT,
+                    BRACKET_SESSION_SLOT_CLAIM_EVENT,
                     BRACKET_SESSION_FINALIZATION_EVENT,
                 ],
             )
             self.assertEqual({row["session_id"] for row in rows}, {window["session_id"]})
-            self.assertEqual([rows[1]["slot"], rows[2]["slot"]], ["pre", "post"])
+            self.assertEqual(
+                [row["slot"] for row in rows[1:]],
+                ["pre", "pre", "post", "post"],
+            )
+        live_observations = [
+            observation
+            for observation in self.snapshot.observations
+            if not observation.is_historical_import
+        ]
+        self.assertEqual(
+            len(self.snapshot.bracket_sessions), expected["session_count"]
+        )
+        self.assertEqual(
+            {session.state for session in self.snapshot.bracket_sessions},
+            {"finalized"},
+        )
+        self.assertEqual(
+            len(live_observations), expected["live_observation_count"]
+        )
+        self.assertTrue(
+            all(
+                observation.observation_kind == "bracket-session-finalized"
+                and observation.disposition == "valid"
+                for observation in live_observations
+            )
+        )
 
-    def test_d110_never_zero_allowance_remains_active_for_all_verdicts(self) -> None:
+    def test_d110_allowance_selects_both_max_operands_across_windows(self) -> None:
         expected = self.scenario["expected_live_extension"]
-        for name in self.windows:
-            with self.subTest(window=name):
-                result, reasons = self._evaluate(name)
+        by_attempt = {candidate.attempt_id: candidate for candidate in self.candidates}
+        for vector in expected["allowance_branch_vectors"]:
+            name = vector["window"]
+            overridden = dict(by_attempt)
+            for slot in ("pre", "post"):
+                attempt_id = f"d117-{name}-{slot}"
+                overridden[attempt_id] = replace(
+                    overridden[attempt_id],
+                    b_fiducial_s=vector[f"{slot}_bound_s"],
+                )
+            candidates = tuple(
+                overridden[candidate.attempt_id] for candidate in self.candidates
+            )
+            with self.subTest(window=name, branch=vector["branch"]):
+                observed = Decimal(vector["observed_drift_s"])
+                screen = Decimal(expected["never_zero_allowance_s"])
+                if vector["branch"] == "bracket_screen_s":
+                    self.assertLess(observed, screen)
+                else:
+                    self.assertEqual(vector["branch"], "observed_drift_s")
+                    self.assertGreater(observed, screen)
+                result, reasons = self._evaluate(name, candidates=candidates)
                 self.assertEqual(reasons, ())
                 allowance = result["acceptance"]["allowance"]
                 self.assertEqual(allowance["rule"], expected["allowance_rule"])
-                self.assertEqual(allowance["value_s"], expected["never_zero_allowance_s"])
+                self.assertEqual(
+                    result["acceptance"]["drift"]["observed_s"],
+                    vector["observed_drift_s"],
+                )
+                self.assertEqual(
+                    allowance["value_s"], vector["selected_allowance_s"]
+                )
                 self.assertEqual(allowance["embedding_count"], 1)
 
+    def test_no_failure_campaign_has_36_valid_observations_two_short_of_trigger(
+        self,
+    ) -> None:
+        expected = self.scenario["expected_live_extension"][
+            "valid_observation_count"
+        ]
+        issuance_valid = {
+            observation.content_id
+            for observation in self.snapshot.observations
+            if observation.is_historical_import
+            and observation.disposition == "valid"
+            and dict(observation.identity_epoch) == self.epoch
+        }
+        valid_same_epoch = {
+            observation.content_id
+            for observation in self.snapshot.observations
+            if observation.disposition == "valid"
+            and dict(observation.identity_epoch) == self.epoch
+        }
+        self.assertEqual(len(issuance_valid), expected["issuance"])
+        self.assertEqual(
+            len(valid_same_epoch), expected["after_three_live_windows"]
+        )
+        self.assertEqual(
+            expected["corpus_doubling_trigger"] - len(valid_same_epoch),
+            expected["shortfall"],
+        )
+        for name in self.windows:
+            result, reasons = self._evaluate(name)
+            self.assertEqual(reasons, ())
+            self.assertNotIn(
+                "corpus_doubles_from_19_to_38",
+                result["acceptance"]["prospective_rederivation"][
+                    "observed_triggers"
+                ],
+            )
+
     def test_refuses_import_marker_removal_import_leakage_or_discovery_regression(
         self,
     ) -> None:
         marker_removed = copy.deepcopy(self.receipts)
         marker_removed[1]["event"] = "finalization"
         marker_removed[1] = _receipt(marker_removed[1])
         snapshot = self._variant_snapshot(marker_removed)
         self.assertIn("calibration_ledger_attempt_conflict", snapshot.refusal_reasons)
 
         first_import = next(
             row
             for row in self.snapshot.observations
             if row.is_historical_import and row.disposition == "valid"
         )
         leaked = replace(first_import, observation_kind="live-capture")
         leaked_snapshot = replace(
             self.snapshot,
             observations=tuple(
                 leaked if row.attempt_id == leaked.attempt_id else row
                 for row in self.snapshot.observations
             ),
         )
         leaked_candidates = self._discover(leaked_snapshot)
         _result, reasons = self._evaluate(
             "alpha", snapshot=leaked_snapshot, candidates=leaked_candidates
         )
         self.assertEqual(reasons, ("calibration_ledger_baseline_missing",))
 
         imported_candidate = self._candidate(first_import)
         _result, reasons = self._evaluate(
             "alpha", candidates=(*self.candidates, imported_candidate)
         )
         self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))
 
     def test_refuses_missing_duplicate_reordered_or_conflicting_session_receipts(
         self,
     ) -> None:
+        alpha_session = self.windows["alpha"]["session_id"]
+        post_claim = self._receipt_index(
+            alpha_session, BRACKET_SESSION_SLOT_CLAIM_EVENT, "post"
+        )
+        post_final = self._receipt_index(
+            alpha_session, BRACKET_SESSION_FINALIZATION_EVENT, "post"
+        )
+        session_open = self._receipt_index(
+            alpha_session, BRACKET_SESSION_OPEN_EVENT
+        )
         variants: dict[str, list[dict]] = {}
-        variants["missing"] = self.receipts[:80] + self.receipts[81:]
+        variants["missing"] = (
+            self.receipts[:post_final] + self.receipts[post_final + 1 :]
+        )
         variants["duplicate"] = (
-            self.receipts[:81]
-            + [copy.deepcopy(self.receipts[80])]
-            + self.receipts[81:]
+            self.receipts[: post_final + 1]
+            + [copy.deepcopy(self.receipts[post_final])]
+            + self.receipts[post_final + 1 :]
         )
         reordered = copy.deepcopy(self.receipts)
-        reordered[79], reordered[80] = reordered[80], reordered[79]
+        reordered[post_claim], reordered[post_final] = (
+            reordered[post_final],
+            reordered[post_claim],
+        )
         variants["reordered"] = reordered
         conflicting = copy.deepcopy(self.receipts)
-        conflicting[78]["window_id"] = "conflicting-alpha-window"
-        conflicting[78] = _receipt(conflicting[78])
+        conflicting[session_open]["window_id"] = "conflicting-alpha-window"
+        conflicting[session_open] = _receipt(conflicting[session_open])
         variants["conflicting"] = conflicting
 
         for name, receipts in variants.items():
             with self.subTest(vector=name):
                 snapshot = self._variant_snapshot(receipts)
                 self.assertTrue(
                     {
                         "calibration_ledger_chain_conflict",
                         "calibration_ledger_bracket_session_conflict",
                     }
                     & set(snapshot.refusal_reasons)
                 )
 
     def test_refuses_open_or_abandoned_session_without_governed_closure(self) -> None:
         open_snapshot = self._variant_snapshot(self.receipts[:-1])
         self.assertIn(
             "calibration_ledger_bracket_session_open",
             open_snapshot.refusal_reasons,
         )
 
-        abandoned = copy.deepcopy(self.receipts[:-1])
+        gamma_session = self.windows["gamma"]["session_id"]
+        post_claim = self._receipt_index(
+            gamma_session, BRACKET_SESSION_SLOT_CLAIM_EVENT, "post"
+        )
+        abandoned = copy.deepcopy(self.receipts[:post_claim])
         abandoned[-1]["disposition"] = "abandoned"
-        abandoned[-1]["content_id"] = None
-        abandoned[-1]["artifact_sha256"] = {}
         abandoned = self._rechain(abandoned)
         abandoned_snapshot = self._variant_snapshot(abandoned)
         self.assertIn(
             "calibration_ledger_bracket_session_open",
             abandoned_snapshot.refusal_reasons,
         )
 
     def test_refuses_head_pin_mismatch_rollback_fork_or_uncommitted_terminal_head(
         self,
     ) -> None:
         mismatch_pin = {
-            "sequence": 85,
+            "sequence": _EXPECTED_TERMINAL_SEQUENCE,
             "head_digest": "f" * 64,
             "ledger_schema": LEDGER_SCHEMA,
         }
         mismatch = self._variant_snapshot(self.receipts, mismatch_pin)
         self.assertIn("calibration_ledger_head_mismatch", mismatch.refusal_reasons)
 
         rollback = self._variant_snapshot(
             self.receipts[:-1], json.loads(self.final_pin_bytes)
         )
         self.assertIn("calibration_ledger_rollback", rollback.refusal_reasons)
 
         forked = copy.deepcopy(self.receipts)
-        forked[83]["predecessor_digest"] = "e" * 64
-        forked[83] = _receipt(forked[83])
+        fork_index = self._receipt_index(
+            self.windows["gamma"]["session_id"],
+            BRACKET_SESSION_SLOT_CLAIM_EVENT,
+            "pre",
+        )
+        forked[fork_index]["predecessor_digest"] = "e" * 64
+        forked[fork_index] = _receipt(forked[fork_index])
         fork = self._variant_snapshot(forked)
         self.assertIn("calibration_ledger_chain_conflict", fork.refusal_reasons)
 
         repo = self.root / "synthetic-repo"
         ledger = repo / "runs" / "ledger.jsonl"
         pin = repo / "configs" / "calibration" / "head.json"
         ledger.parent.mkdir(parents=True)
         pin.parent.mkdir(parents=True)
         ledger.write_bytes(self.final_ledger_bytes)
         pin.write_bytes(self.final_pin_bytes)
         subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
         subprocess.run(
             ["git", "config", "user.email", "tests@joulewise.invalid"],
             cwd=repo,
             check=True,
         )
         subprocess.run(
             ["git", "config", "user.name", "JouleWise tests"],
             cwd=repo,
             check=True,
         )
         subprocess.run(
             ["git", "add", pin.relative_to(repo).as_posix()],
             cwd=repo,
             check=True,
         )
         subprocess.run(
             ["git", "commit", "-qm", "pin synthetic terminal head"],
             cwd=repo,
             check=True,
         )
         pin.write_text(
             json.dumps(json.loads(self.final_pin_bytes), indent=2) + "\n",
             encoding="utf-8",
         )
         uncommitted = self._load_snapshot(
             ledger=ledger,
             pin=pin,
             require_committed_pin=True,
             repo_root=repo,
         )
         self.assertIn(
             "calibration_ledger_head_uncommitted", uncommitted.refusal_reasons
         )
 
     def test_refuses_omitted_added_duplicated_off_ledger_or_substituted_observations(
         self,
     ) -> None:
         imported = next(
             row
             for row in self.snapshot.observations
             if row.is_historical_import and row.disposition == "valid"
         )
         fake = replace(
             self.candidates[0],
             attempt_id="synthetic-off-ledger",
             content_id=_hash("synthetic-off-ledger-content"),
             ledger_receipt_digest=_hash("synthetic-off-ledger-receipt"),
         )
         variants = {
             "omitted": self.candidates[:-1],
             "added": (*self.candidates, fake),
             "duplicated": (*self.candidates, self.candidates[0]),
             "off-ledger": (*self.candidates, self._candidate(imported)),
             "content-substituted": (
                 replace(self.candidates[0], content_id=_hash("substituted-content")),
                 *self.candidates[1:],
             ),
         }
         for name, candidates in variants.items():
             with self.subTest(vector=name):
                 _result, reasons = self._evaluate("alpha", candidates=candidates)
                 self.assertEqual(
                     reasons, ("calibration_ledger_off_ledger_artifact",)
                 )
 
     def test_refuses_missing_tampered_swapped_or_cross_window_bracket_binding(
         self,
     ) -> None:
         _result, reasons = self._evaluate("alpha", binding=None)
         self.assertEqual(reasons, ("calibration_bracket_binding_missing",))
 
         tampered = copy.deepcopy(self.bindings["alpha"])
         tampered["window_id"] = "tampered-without-digest-update"
         _result, reasons = self._evaluate("alpha", binding=tampered)
         self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
 
         swapped = copy.deepcopy(self.bindings["alpha"])
         swapped["endpoints"]["pre"], swapped["endpoints"]["post"] = (
             swapped["endpoints"]["post"],
             swapped["endpoints"]["pre"],
         )
         swapped = self._rehash_binding(swapped)
         _result, reasons = self._evaluate("alpha", binding=swapped)
         self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
 
         _result, reasons = self._evaluate(
             "alpha", binding=self.bindings["beta"]
         )
         self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
 
     def test_refuses_noncausal_stale_t1_protocol_or_epoch_mismatched_endpoint(
         self,
     ) -> None:
         gamma = self.windows["gamma"]
         indexes = {
             "open": next(
                 index
                 for index, row in enumerate(self.receipts)
                 if row.get("session_id") == gamma["session_id"]
                 and row["event"] == BRACKET_SESSION_OPEN_EVENT
             ),
             "pre": next(
                 index
                 for index, row in enumerate(self.receipts)
                 if row.get("session_id") == gamma["session_id"]
+                and row.get("event") == BRACKET_SESSION_FINALIZATION_EVENT
                 and row.get("slot") == "pre"
             ),
             "post": next(
                 index
                 for index, row in enumerate(self.receipts)
                 if row.get("session_id") == gamma["session_id"]
+                and row.get("event") == BRACKET_SESSION_FINALIZATION_EVENT
                 and row.get("slot") == "post"
             ),
         }
 
         variants: dict[str, tuple[list[dict], tuple[str, ...]]] = {}
         noncausal = copy.deepcopy(self.receipts)
         noncausal[indexes["pre"]]["capture_wall_time_s"] = str(
             gamma["window_start_s"] + 1.0
         )
         variants["noncausal"] = (
             self._rechain(noncausal),
             ("calibration_bracket_binding_invalid",),
         )
 
         stale = copy.deepcopy(self.receipts)
         stale[indexes["post"]]["capture_wall_time_s"] = str(
             gamma["window_start_s"] + MAX_AGE_S + 1.0
         )
         variants["stale"] = (
             self._rechain(stale),
             ("instrument_calibration_stale",),
         )
 
         wrong_t1 = copy.deepcopy(self.receipts)
         wrong_t1[indexes["open"]]["slots"]["pre"]["t1_bindings"][
             "mlx_version"
         ] = "wrong-mlx"
         wrong_t1[indexes["pre"]]["t1_bindings"]["mlx_version"] = "wrong-mlx"
         variants["t1"] = (
             self._rechain(wrong_t1),
             ("calibration_bracket_binding_invalid",),
         )
 
         wrong_protocol = copy.deepcopy(self.receipts)
         for row in (
             wrong_protocol[indexes["open"]]["slots"]["pre"],
             wrong_protocol[indexes["pre"]],
         ):
             row["t1_bindings"]["pulse_protocol_id"] = PROTOCOL_V2_ID
             row["identity_epoch"]["pulse_protocol_id"] = PROTOCOL_V2_ID
         variants["protocol"] = (
             self._rechain(wrong_protocol),
             ("calibration_bracket_binding_invalid",),
         )
 
         wrong_epoch = copy.deepcopy(self.receipts)
         for row in (
             wrong_epoch[indexes["open"]]["slots"]["pre"],
             wrong_epoch[indexes["pre"]],
         ):
             row["t1_bindings"]["os_build"] = "wrong-os-build"
             row["identity_epoch"]["os_build"] = "wrong-os-build"
         variants["epoch"] = (
             self._rechain(wrong_epoch),
             ("calibration_bracket_binding_invalid",),
         )
 
         for name, (receipts, expected_reasons) in variants.items():
             with self.subTest(vector=name):
                 snapshot = self._variant_snapshot(receipts)
                 binding = build_calibration_bracket_binding(
                     snapshot,
                     session_id=gamma["session_id"],
                     window_id=gamma["window_id"],
                     plan_id=gamma["plan_id"],
                     plan_sha256=gamma["plan_sha256"],
                     evidence_root_id=gamma["evidence_root_id"],
                     runs_root=gamma["runs_root"],
                 )
                 _result, reasons = self._evaluate(
                     "gamma",
                     snapshot=snapshot,
                     candidates=self._discover(snapshot),
                     binding=binding,
                 )
                 self.assertEqual(reasons, expected_reasons)
 
     def test_refuses_systematic_classification(self) -> None:
         window = {
             "session_id": "session-d117-systematic",
             "window_id": "plan-d117-systematic-refusal",
             "plan_id": "plan-d117-systematic-refusal",
             "plan_sha256": "d" * 64,
             "evidence_root_id": "evidence-d117-systematic-refusal",
             "runs_root": "/synthetic/d117/systematic-refusal",
         }
         attempts = {
             slot: f"d117-systematic-{slot}" for slot in ("pre", "post")
         }
         slots = {
             slot: {
                 "attempt_id": attempts[slot],
                 "custody_locator": (
                     f"{window['runs_root']}/instrument_validation/{attempts[slot]}"
                 ),
                 "identity_epoch": self.epoch,
                 "t1_bindings": self.t1,
             }
             for slot in ("pre", "post")
         }
         append_bracket_session_receipt(
             self.ledger,
             **window,
             slots=slots,
             head_pin_path=self.pin,
             require_committed_pin=False,
         )
+        claim_bracket_session_slot(
+            self.ledger,
+            session_id=window["session_id"],
+            slot="pre",
+            attempt_id=attempts["pre"],
+            claim_id="synthetic-systematic-pre-claim",
+        )
         finalize_bracket_session_slot(
             self.ledger,
             session_id=window["session_id"],
             slot="pre",
             disposition="systematic-invalid",
             custody_locator=slots["pre"]["custody_locator"],
             artifact_sha256=_content_hashes(attempts["pre"]),
             identity_epoch=self.epoch,
             t1_bindings=self.t1,
             capture_wall_time_s="170.0",
             exact_bound_lexeme_s="0.040000",
         )
         abort_bracket_session(
             self.ledger,
             session_id=window["session_id"],
             reason="synthetic systematic preflight refusal",
         )
         self.pin.write_bytes(
             _pin_bytes(
                 terminal_head_pin_for_session(
                     self.ledger, session_id=window["session_id"]
                 )
             )
         )
         snapshot = self._load_snapshot()
         candidates = self._discover(snapshot)
         result, reasons = self._evaluate(
             "alpha", snapshot=snapshot, candidates=candidates
         )
         self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
         self.assertIn(
             "new_systematic_failure_challenges_preflight_screen",
             result["acceptance"]["prospective_rederivation"][
                 "observed_triggers"
             ],
         )
 
     @unittest.skip("U2 successor engine pending")
     def test_range_expanding_live_observation_requires_successor(self) -> None:
         vector = self.scenario["staged_successor_vectors"][
             "range_expanding_live_observation"
         ]
         self.assertEqual(
             vector["expected_trigger"],
             "new_valid_same_identity_capture_expands_observed_range",
         )
 
     @unittest.skip("U2 successor engine pending")
     def test_d102_observation_count_boundary_requires_successor(self) -> None:
         vector = self.scenario["staged_successor_vectors"][
             "d102_count_boundary"
         ]
         self.assertEqual(vector["expected_total_valid_same_epoch"], 38)
 
     @unittest.skip("U2 successor engine pending")
     def test_successor_prior_set_refuses_omitted_or_changed_authenticated_prefix(
         self,
     ) -> None:
         vector = self.scenario["staged_successor_vectors"][
             "successor_prior_set_integrity"
         ]
         self.assertEqual(
             vector["mutations"],
             [
                 "omit_authenticated_prefix_member",
                 "change_authenticated_prefix_member",
             ],
         )
 
 
 if __name__ == "__main__":
     unittest.main()

exec
/bin/zsh -lc "git show 50404be:tests/test_calibration_live_three_window.py | nl -ba | sed -n '250,430p' && rg -n \"def .*acceptance|emit.*acceptance|derivation_corpus|D-116|valid_acceptance\" joulewise scripts tests | head -200" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
   250	                        "artifact_sha256": hashes,
   251	                        "disposition": disposition,
   252	                        "bound_s": (
   253	                            "0.040000"
   254	                            if disposition == "systematic-invalid"
   255	                            else "0.026000"
   256	                        ),
   257	                    }
   258	                )
   259	
   260	        receipts: list[dict] = []
   261	        predecessor = "0" * 64
   262	        import_inputs = {
   263	            "disposition_table": _hash("synthetic-d117-disposition-table"),
   264	            "custody_manifest": _hash("synthetic-d117-custody-manifest"),
   265	        }
   266	        for index, member in enumerate(
   267	            sorted(receipt_members, key=lambda row: row["attempt_id"]), start=1
   268	        ):
   269	            custody = f"/synthetic/d117/import/{member['attempt_id']}"
   270	            reservation = _receipt(
   271	                {
   272	                    "schema_version": RECEIPT_SCHEMA,
   273	                    "ledger_schema": LEDGER_SCHEMA,
   274	                    "sequence": len(receipts) + 1,
   275	                    "predecessor_digest": predecessor,
   276	                    "event": HISTORICAL_IMPORT_RESERVATION_EVENT,
   277	                    "attempt_id": member["attempt_id"],
   278	                    "content_id": None,
   279	                    "artifact_sha256": {},
   280	                    "identity_epoch": dict(cls.epoch),
   281	                    "t1_bindings": dict(cls.t1),
   282	                    "capture_wall_time_s": None,
   283	                    "exact_bound_lexeme_s": None,
   284	                    "disposition": "pending",
   285	                    "custody_locator": custody,
   286	                    "historical_import_input_sha256": import_inputs,
   287	                }
   288	            )
   289	            receipts.append(reservation)
   290	            predecessor = reservation["receipt_digest"]
   291	            finalization = _receipt(
   292	                {
   293	                    "schema_version": RECEIPT_SCHEMA,
   294	                    "ledger_schema": LEDGER_SCHEMA,
   295	                    "sequence": len(receipts) + 1,
   296	                    "predecessor_digest": predecessor,
   297	                    "event": HISTORICAL_IMPORT_FINALIZATION_EVENT,
   298	                    "attempt_id": member["attempt_id"],
   299	                    "content_id": member["content_id"],
   300	                    "artifact_sha256": member["artifact_sha256"],
   301	                    "identity_epoch": dict(cls.epoch),
   302	                    "t1_bindings": dict(cls.t1),
   303	                    "capture_wall_time_s": str(float(index)),
   304	                    "exact_bound_lexeme_s": member["bound_s"],
   305	                    "disposition": member["disposition"],
   306	                    "custody_locator": custody,
   307	                }
   308	            )
   309	            receipts.append(finalization)
   310	            predecessor = finalization["receipt_digest"]
   311	            observations.append(
   312	                {
   313	                    "content_id": member["content_id"],
   314	                    "epoch_id": "d079_epoch",
   315	                    "disposition": member["disposition"],
   316	                    "attempt_id": member["attempt_id"],
   317	                }
   318	            )
   319	
   320	        cutoff = {
   321	            "sequence": len(receipts),
   322	            "head_digest": receipts[-1]["receipt_digest"],
   323	            "ledger_schema": LEDGER_SCHEMA,
   324	        }
   325	        artifact["ledger_cutoff"] = {
   326	            **cutoff,
   327	            "role": "issued_acceptance_baseline",
   328	        }
   329	        artifact["prior_observation_set"]["cutoff"] = cutoff
   330	        artifact["prior_observation_set"]["observations"] = observations
   331	        counts = {
   332	            disposition: sum(
   333	                row["disposition"] == disposition for row in observations
   334	            )
   335	            for disposition in ("ordinary-invalid", "systematic-invalid", "valid")
   336	        }
   337	        artifact["backfill_candidate"]["candidate_inventory"] = counts
   338	        artifact["derivation_sha256"] = bracketing_canonical_sha256(
   339	            {
   340	                key: value
   341	                for key, value in artifact.items()
   342	                if key != "derivation_sha256"
   343	            }
   344	        )
   345	        if not _valid_acceptance_bound(artifact):
   346	            raise AssertionError("synthetic issued acceptance artifact is invalid")
   347	        return receipts, artifact
   348	
   349	    def setUp(self) -> None:
   350	        self.tmp = tempfile.TemporaryDirectory()
   351	        self.root = Path(self.tmp.name)
   352	        self.ledger = self.root / "ledger.jsonl"
   353	        self.pin = self.root / "head.json"
   354	        self.ledger.write_bytes(self.final_ledger_bytes)
   355	        self.pin.write_bytes(self.final_pin_bytes)
   356	        self.receipts = [
   357	            json.loads(line) for line in self.final_ledger_bytes.splitlines()
   358	        ]
   359	        self.snapshot = self._load_snapshot()
   360	        self.candidates = self._discover(self.snapshot)
   361	
   362	    def tearDown(self) -> None:
   363	        self.tmp.cleanup()
   364	
   365	    def _load_snapshot(
   366	        self,
   367	        *,
   368	        ledger: Path | None = None,
   369	        pin: Path | None = None,
   370	        require_committed_pin: bool = False,
   371	        repo_root: Path | None = None,
   372	    ):
   373	        return load_calibration_ledger_snapshot(
   374	            ledger or self.ledger,
   375	            pin or self.pin,
   376	            baseline_sequence=self.base_sequence,
   377	            baseline_digest=self.base_digest,
   378	            require_committed_pin=require_committed_pin,
   379	            verify_custody=False,
   380	            repo_root=repo_root or self.root,
   381	        )
   382	
   383	    @staticmethod
   384	    def _candidate(observation) -> CalibrationCandidate:
   385	        return CalibrationCandidate(
   386	            relative_path=observation.custody_locator,
   387	            manifest_sha256=observation.artifact_sha256["manifest.json"],
   388	            evidence_sha256=observation.artifact_sha256[
   389	                "instrument_evidence.json"
   390	            ],
   391	            protocol_id=observation.t1_bindings["pulse_protocol_id"],
   392	            capture_wall_time_s=float(observation.capture_wall_time_s),
   393	            b_fiducial_s=observation.exact_bound_lexeme_s,
   394	            bindings=dict(observation.t1_bindings),
   395	            attempt_id=observation.attempt_id,
   396	            content_id=observation.content_id,
   397	            ledger_receipt_digest=observation.receipt_digest,
   398	            bracket_session_id=observation.bracket_session_id,
   399	            bracket_slot=observation.bracket_slot,
   400	            bracket_window_id=observation.bracket_window_id,
   401	            bracket_plan_id=observation.bracket_plan_id,
   402	            bracket_plan_sha256=observation.bracket_plan_sha256,
   403	            bracket_evidence_root_id=observation.bracket_evidence_root_id,
   404	            bracket_runs_root=observation.bracket_runs_root,
   405	        )
   406	
   407	    def _discover(self, snapshot):
   408	        with patch(
   409	            "joulewise.calibration_bracketing._candidate_from_observation",
   410	            side_effect=self._candidate,
   411	        ):
   412	            return discover_calibration_candidates(snapshot)
   413	
   414	    def _evaluate(
   415	        self,
   416	        window_name: str,
   417	        *,
   418	        snapshot=None,
   419	        candidates=None,
   420	        binding=_USE_WINDOW_BINDING,
   421	        bindings=None,
   422	    ):
   423	        window = self.windows[window_name]
   424	        selected_binding = (
   425	            self.bindings[window_name]
   426	            if binding is _USE_WINDOW_BINDING
   427	            else binding
   428	        )
   429	        with patch(
   430	            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
scripts/calibration_ledger_bootstrap.py:48:    _valid_acceptance_bound,
scripts/calibration_ledger_bootstrap.py:145:def _issued_acceptance_artifact(
scripts/calibration_ledger_bootstrap.py:265:    if not _valid_acceptance_bound(artifact):
scripts/calibration_ledger_bootstrap.py:266:        raise ValueError("deterministically emitted acceptance artifact is invalid")
scripts/calibration_ledger_bootstrap.py:270:def _prepare_issued_acceptance_artifact(
tests/test_calibration_bracketing.py:25:    _valid_acceptance_bound,
tests/test_calibration_bracketing.py:161:def _unissued_acceptance_fixture_bytes() -> bytes:
tests/test_calibration_bracketing.py:170:def _unissued_acceptance_fixture() -> dict:
tests/test_calibration_bracketing.py:172:    assert _valid_acceptance_bound(artifact)
tests/test_calibration_bracketing.py:239:    assert _valid_acceptance_bound(artifact)
tests/test_calibration_bracketing.py:360:def _evaluate_with_unissued_acceptance(
tests/test_calibration_bracketing.py:442:        self.assertTrue(_valid_acceptance_bound(artifact))
tests/test_calibration_bracketing.py:491:        self.assertTrue(_valid_acceptance_bound(artifact))
tests/test_calibration_bracketing.py:561:        self.assertTrue(_valid_acceptance_bound(artifact))
tests/test_calibration_bracketing.py:581:        self.assertFalse(_valid_acceptance_bound(artifact))
tests/test_calibration_bracketing.py:600:    def test_unknown_acceptance_artifact_role_refuses(self) -> None:
tests/test_calibration_bracketing.py:610:        self.assertFalse(_valid_acceptance_bound(artifact))
tests/test_calibration_bracketing.py:657:                issued["derivation_corpus"], source["derivation_corpus"]
tests/test_calibration_bracketing.py:792:    def test_acceptance_prior_set_must_equal_import_marked_cutoff_prefix(self) -> None:
tests/test_calibration_bracketing.py:1452:    def test_identity_epoch_violation_refuses_stale_acceptance_bound(self) -> None:
tests/test_calibration_bracketing.py:1685:        for index, member in enumerate(artifact["derivation_corpus"]["members"]):
tests/test_calibration_bracketing.py:1806:    def test_acceptance_artifact_rederives_from_decimal_member_table(self) -> None:
tests/test_calibration_bracketing.py:1809:        self.assertEqual(artifact["derivation_corpus"]["n"], 19)
tests/test_calibration_bracketing.py:1815:        tampered["derivation_corpus"]["members"][0]["b_fiducial_s"] = "0.030"
tests/test_calibration_bracketing.py:1823:        self.assertFalse(_valid_acceptance_bound(tampered))
tests/test_calibration_bracketing.py:1846:        self.assertTrue(_valid_acceptance_bound(rekeyed))
tests/verify_calibration_acceptance_corpus.py:43:    for member in artifact["derivation_corpus"]["members"]:
tests/test_mint_floor_artifact.py:139:    def test_folded_digest_acceptance_preserves_fail_closed_negatives(
scripts/build_site.py:1512:def roadmap_acceptance_summary(acceptance: str) -> str:
joulewise/schemas.py:2179:            "required": ["emitted_count", "tokens_proposed", "tokens_accepted", "target_emitted_count", "acceptance_rate"],
tests/test_cli.py:192:    def test_strict_reducer_version_acceptance_matrix(self) -> None:
tests/test_axi_mock_spec.py:163:    def test_parameterized_proposal_acceptance_target_id_and_timestamp_cases(self) -> None:
tests/test_corpus_strict_validation.py:26:    def test_six_frozen_acceptance_gate_bundles_pass_strict_read_only(self) -> None:
joulewise/axi_decode_config.py:429:CANCELLED_COUNTER_KEYS = {"tokens_proposed", "tokens_accepted", "target_emitted_count", "emitted_count", "acceptance_rate"}
joulewise/axi_decode_config.py:552:            if counters["tokens_accepted"] != 0 or counters["target_emitted_count"] != 0 or counters["emitted_count"] != 0 or counters["acceptance_rate"] != 0.0:
joulewise/axi_decode_config.py:579:    "target_emitted_count", "acceptance_rate",
tests/test_calibration_live_three_window.py:20:    _valid_acceptance_bound,
tests/test_calibration_live_three_window.py:317:        for member in artifact["derivation_corpus"]["members"]:
tests/test_calibration_live_three_window.py:338:            "synthetic_additions_to_n19_derivation_corpus"
tests/test_calibration_live_three_window.py:446:        if not _valid_acceptance_bound(artifact):
tests/test_calibration_ledger.py:29:    _valid_acceptance_bound,
tests/test_calibration_ledger.py:1075:        emitted_path = self.root / "issued-acceptance.json"
tests/test_calibration_ledger.py:1123:        self.assertEqual(issued["artifact"]["derivation_corpus"]["n"], 19)
tests/test_calibration_ledger.py:1221:        self.assertTrue(_valid_acceptance_bound(tampered))
tests/test_calibration_ledger.py:1246:        self.assertTrue(_valid_acceptance_bound(tampered))
joulewise/calibration_bracketing.py:176:def _valid_acceptance_bound(value: Any) -> bool:
joulewise/calibration_bracketing.py:184:    corpus = value.get("derivation_corpus")
joulewise/calibration_bracketing.py:446:def load_calibration_acceptance_bound(
joulewise/calibration_bracketing.py:458:def _acceptance_bound_from_authenticated_bytes(
joulewise/calibration_bracketing.py:477:    if not _valid_acceptance_bound(value):
joulewise/calibration_bracketing.py:482:def _authenticated_explicit_acceptance_bound(
joulewise/calibration_bracketing.py:493:def _acceptance_artifact_sha256(artifact: Mapping[str, Any]) -> str:
joulewise/calibration_bracketing.py:1344:    corpus_members = artifact["derivation_corpus"]["members"]
tests/fixtures/calibration_live_three_window/scenario.json:12:    "synthetic_additions_to_n19_derivation_corpus": {

exec
/bin/zsh -lc "nl -ba scripts/calibration_ledger_bootstrap.py | sed -n '130,300p' && git diff 50404be..4b82180 -- tests/test_calibration_live_three_window.py | rg -n '"'^[-+].*(deriv|accept|_build_issuance|NEEDS_SCOPE|fixture)'"'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
   130	            _write_issued_artifact_payload(staging, payload)
   131	            staging.flush()
   132	            os.fsync(staging.fileno())
   133	        os.replace(staging_path, destination)
   134	        staging_path = None
   135	    finally:
   136	        if staging_descriptor >= 0:
   137	            os.close(staging_descriptor)
   138	        if staging_path is not None:
   139	            try:
   140	                staging_path.unlink()
   141	            except FileNotFoundError:
   142	                pass
   143	
   144	
   145	def _issued_acceptance_artifact(
   146	    plan: Any,
   147	    source_artifact: Mapping[str, Any],
   148	    *,
   149	    source_artifact_raw: bytes | None = None,
   150	) -> dict[str, Any]:
   151	    """Build the D-079 issued artifact only from the prepared ledger prefix."""
   152	
   153	    if source_artifact_raw is None:
   154	        authenticated_source = _authenticated_explicit_acceptance_bound(
   155	            source_artifact
   156	        )
   157	    else:
   158	        authenticated_source = _acceptance_bound_from_authenticated_bytes(
   159	            source_artifact_raw
   160	        )
   161	        if (
   162	            authenticated_source is not None
   163	            and dict(source_artifact) != authenticated_source
   164	        ):
   165	            authenticated_source = None
   166	    if authenticated_source is None:
   167	        raise ValueError(
   168	            "acceptance artifact source does not match its role-indexed byte pin"
   169	        )
   170	    if (
   171	        plan.final_sequence != _D079_ISSUANCE_SEQUENCE
   172	        or plan.head_digest != _D079_ISSUANCE_HEAD_DIGEST
   173	        or len(plan.receipts) != _D079_ISSUANCE_SEQUENCE
   174	    ):
   175	        raise ValueError("ledger plan is not the ruled D-079 issuance cutoff")
   176	    if any(
   177	        receipt.get("event")
   178	        not in {
   179	            HISTORICAL_IMPORT_RESERVATION_EVENT,
   180	            HISTORICAL_IMPORT_FINALIZATION_EVENT,
   181	        }
   182	        for receipt in plan.receipts
   183	    ):
   184	        raise ValueError("issued prior set requires an import-only ledger prefix")
   185	
   186	    # Clone the authenticated source, not the caller's mapping. This preserves
   187	    # the reviewed schema-field order that defines the issued file pin and
   188	    # makes output independent of caller key insertion order.
   189	    artifact = json.loads(
   190	        json.dumps(dict(authenticated_source), allow_nan=False)
   191	    )
   192	    epoch_catalog = artifact["prior_observation_set"]["epoch_catalog"]
   193	    observations: list[dict[str, Any]] = []
   194	    for receipt in plan.receipts:
   195	        if receipt["event"] != HISTORICAL_IMPORT_FINALIZATION_EVENT:
   196	            continue
   197	        epoch_ids = [
   198	            epoch_id
   199	            for epoch_id, epoch in epoch_catalog.items()
   200	            if dict(epoch) == dict(receipt["identity_epoch"])
   201	        ]
   202	        if len(epoch_ids) != 1:
   203	            raise ValueError("ledger observation does not map to one artifact epoch")
   204	        observations.append(
   205	            {
   206	                "content_id": receipt["content_id"],
   207	                "epoch_id": epoch_ids[0],
   208	                "disposition": receipt["disposition"],
   209	                "attempt_id": receipt["attempt_id"],
   210	            }
   211	        )
   212	    disposition_counts = {
   213	        disposition: sum(
   214	            observation["disposition"] == disposition
   215	            for observation in observations
   216	        )
   217	        for disposition in sorted(_D079_ISSUANCE_INVENTORY)
   218	    }
   219	    if (
   220	        len(observations) != 38
   221	        or disposition_counts != _D079_ISSUANCE_INVENTORY
   222	        or len({row["content_id"] for row in observations}) != len(observations)
   223	        or len({row["attempt_id"] for row in observations}) != len(observations)
   224	    ):
   225	        raise ValueError("ledger prefix does not have the ruled 30/2/6 inventory")
   226	
   227	    cutoff = {
   228	        "sequence": plan.final_sequence,
   229	        "head_digest": plan.head_digest,
   230	        "ledger_schema": LEDGER_SCHEMA,
   231	    }
   232	    artifact["schema_version"] = ACCEPTANCE_BOUND_SCHEMA
   233	    artifact["artifact_role"] = "issued"
   234	    artifact["issuance"] = {
   235	        "status": "issued",
   236	        "claim_eligible": True,
   237	        "reason": (
   238	            "D-109 R2 raw-physics and artifact-hash verification is bound "
   239	            "by the authenticated historical-import cutoff"
   240	        ),
   241	    }
   242	    artifact["ledger_cutoff"] = {
   243	        **cutoff,
   244	        "role": "issued_acceptance_baseline",
   245	    }
   246	    artifact["prior_observation_set"]["cutoff"] = cutoff
   247	    artifact["prior_observation_set"]["observations"] = observations
   248	    artifact["backfill_candidate"].update(
   249	        {
   250	            "status": "issued",
   251	            "candidate_inventory": disposition_counts,
   252	            "production_issuance_blocked": False,
   253	            "required_verification": (
   254	                "complete: lead-owned raw-physics and artifact-hash verification"
   255	            ),
   256	        }
   257	    )
   258	    artifact["derivation_sha256"] = _canonical_sha256(
   259	        {
   260	            key: value
   261	            for key, value in artifact.items()
   262	            if key != "derivation_sha256"
   263	        }
   264	    )
   265	    if not _valid_acceptance_bound(artifact):
   266	        raise ValueError("deterministically emitted acceptance artifact is invalid")
   267	    return artifact
   268	
   269	
   270	def _prepare_issued_acceptance_artifact(
   271	    plan: Any,
   272	    source_artifact: Mapping[str, Any],
   273	    *,
   274	    source_artifact_raw: bytes | None = None,
   275	) -> PreparedIssuedAcceptanceArtifact:
   276	    """Build and fully validate the exact artifact bytes before any commit."""
   277	
   278	    artifact = _issued_acceptance_artifact(
   279	        plan,
   280	        source_artifact,
   281	        source_artifact_raw=source_artifact_raw,
   282	    )
   283	    expected_cutoff = {
   284	        "sequence": plan.final_sequence,
   285	        "head_digest": plan.head_digest,
   286	        "ledger_schema": LEDGER_SCHEMA,
   287	    }
   288	    expected_observations = []
   289	    epoch_catalog = artifact["prior_observation_set"]["epoch_catalog"]
   290	    for receipt in plan.receipts:
   291	        if receipt["event"] != HISTORICAL_IMPORT_FINALIZATION_EVENT:
   292	            continue
   293	        epoch_ids = [
   294	            epoch_id
   295	            for epoch_id, epoch in epoch_catalog.items()
   296	            if dict(epoch) == dict(receipt["identity_epoch"])
   297	        ]
   298	        if len(epoch_ids) != 1:
   299	            raise ValueError("ledger observation does not map to one artifact epoch")
   300	        expected_observations.append(
174:+                # Keep that fixture boundary while exercising the production
312:+                "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
313:+                return_value=self.acceptance,
420:+                    result["acceptance"]["ledger_snapshot"]["sequence"],
444:+    def test_production_writer_receipts_end_at_derived_terminal_sequence(self) -> None:
536:+                    result["acceptance"]["drift"]["observed_s"],
576:+                result["acceptance"]["prospective_rederivation"][

exec
/bin/zsh -lc "git show -s --format=fuller 4b82180 && git show -s --format=%B 4b82180 && git show -s --format=%B 50404be && git diff 50404be..4b82180 -- tests/test_calibration_live_three_window.py | sed -n '1,950p' | rg -n 'FIX-|NEEDS_SCOPE|emitter|sole source|double|open_beta|cross.window|per.window|allowance|l5|derived|receipt'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
commit 4b821807fd03690f20e91e1323ce92862f96feee
Author:     Ed R <edr@Eds-MacBook-Pro.local>
AuthorDate: Fri Aug 7 13:20:28 2026 -0700
Commit:     Ed R <edr@Eds-MacBook-Pro.local>
CommitDate: Fri Aug 7 13:20:28 2026 -0700

    U4 amendment round (FIX-A..F): terminal sequence DERIVED from production receipt count (76 + 3x5 = 91, superseding the memo's stale 85 three-receipt model); allowance test now straddles the 0.010818 bound so both max() branches are exercised; L5 named; positive count oracle; per-window verdict issuance; real discovery-authority test
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
U4 amendment round (FIX-A..F): terminal sequence DERIVED from production receipt count (76 + 3x5 = 91, superseding the memo's stale 85 three-receipt model); allowance test now straddles the 0.010818 bound so both max() branches are exercised; L5 named; positive count oracle; per-window verdict issuance; real discovery-authority test

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

U4 speculative implementation: synthetic three-window live-ledger regression (19 tests, 3 staged behind U2) — built from the pre-examination plan; carries the stale sequence-85 oracle and a one-sided D-110 allowance test, both closed in the next round

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

37:     append_bracket_session_receipt,
99:         cls.base_sequence = len(base_receipts)
100:         cls.base_digest = base_receipts[-1]["receipt_digest"]
110:         ledger.write_bytes(_ledger_bytes(base_receipts))
111:         pin.write_bytes(_pin_bytes(_pin_for(base_receipts[-1])))
194:+                _receipt_value, terminal_pin = lifecycle.finalize("valid")
255:+    def _receipt_index(
260:+            for index, row in enumerate(self.receipts)
266:     def test_issuance_equivalent_base_has_76_receipts_and_30_2_6_dispositions(
274:         self.assertEqual(len(prefix), expected["receipt_count"])
343:+    def test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding(
379:+        for index, vector in enumerate(expected["cross_window_openness"], start=1):
443:-    def test_ideal_three_receipt_sessions_end_at_terminal_sequence_85(self) -> None:
444:+    def test_production_writer_receipts_end_at_derived_terminal_sequence(self) -> None:
445:         live = self.snapshot.receipts[self.base_sequence :]
451:+        receipt_model = expected["receipt_model_supersession"]["landed"]
458:+            receipt_model["receipts_per_session"],
503:-    def test_d110_never_zero_allowance_remains_active_for_all_verdicts(self) -> None:
504:+    def test_d110_allowance_selects_both_max_operands_across_windows(self) -> None:
510:+        for vector in expected["allowance_branch_vectors"]:
524:+                screen = Decimal(expected["never_zero_allowance_s"])
532:                 allowance = result["acceptance"]["allowance"]
533:                 self.assertEqual(allowance["rule"], expected["allowance_rule"])
534:-                self.assertEqual(allowance["value_s"], expected["never_zero_allowance_s"])
540:+                    allowance["value_s"], vector["selected_allowance_s"]
542:                 self.assertEqual(allowance["embedding_count"], 1)
575:+                "corpus_doubles_from_19_to_38",
585:     def test_refuses_missing_duplicate_reordered_or_conflicting_session_receipts(
589:+        post_claim = self._receipt_index(
592:+        post_final = self._receipt_index(
595:+        session_open = self._receipt_index(
599:-        variants["missing"] = self.receipts[:80] + self.receipts[81:]
601:+            self.receipts[:post_final] + self.receipts[post_final + 1 :]
604:-            self.receipts[:81]
605:-            + [copy.deepcopy(self.receipts[80])]
606:-            + self.receipts[81:]
607:+            self.receipts[: post_final + 1]
608:+            + [copy.deepcopy(self.receipts[post_final])]
609:+            + self.receipts[post_final + 1 :]
611:         reordered = copy.deepcopy(self.receipts)
618:         conflicting = copy.deepcopy(self.receipts)
620:-        conflicting[78] = _receipt(conflicting[78])
622:+        conflicting[session_open] = _receipt(conflicting[session_open])
625:         for name, receipts in variants.items():
630:-        abandoned = copy.deepcopy(self.receipts[:-1])
632:+        post_claim = self._receipt_index(
635:+        abandoned = copy.deepcopy(self.receipts[:post_claim])
654:         forked = copy.deepcopy(self.receipts)
656:-        forked[83] = _receipt(forked[83])
657:+        fork_index = self._receipt_index(
663:+        forked[fork_index] = _receipt(forked[fork_index])
669:                 for index, row in enumerate(self.receipts)
676:                 for index, row in enumerate(self.receipts)

codex
The amendment adds the intended production lifecycle and both allowance branches, but I’m checking whether the assertions are truly mutation-sensitive rather than trusting their names. I’m now running the U4 module and the three calibration-focused suites independently so their exact outcomes and skip counts remain attributable.
exec
/bin/zsh -lc 'python3 -m unittest tests.test_calibration_bracketing' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
exec
/bin/zsh -lc 'python3 -m unittest tests.test_calibration_ledger' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
exec
/bin/zsh -lc 'python3 -m unittest tests.test_calibration_live_three_window' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
exec
/bin/zsh -lc 'python3 -m unittest tests.test_powermetrics_fiducial' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 652ms:
...s.........s........s
----------------------------------------------------------------------
Ran 23 tests in 0.680s

OK (skipped=3)

 succeeded in 3444ms:
.............
----------------------------------------------------------------------
Ran 39 tests in 3.474s

OK

 succeeded in 9578ms:
....................................
----------------------------------------------------------------------
Ran 46 tests in 9.609s

OK

 succeeded in 29897ms:
......................refusing: frozen powermetrics fiducial protocol is missing, incomplete, or disagrees with executable constants
..................
----------------------------------------------------------------------
Ran 40 tests in 29.923s

OK

exec
/bin/zsh -lc "rg -n \"max\\(|observed_drift|allowance\" joulewise/calibration_bracketing.py | tail -80 && nl -ba joulewise/calibration_bracketing.py | sed -n '1320,1435p' && rg -n \"skip|U2 successor|successor engine\" tests/test_calibration_live_three_window.py tests/test_calibration_bracketing.py tests/test_calibration_ledger.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
381:            "maximum_s": str(max(values)),
382:            "range_s": str(max(values) - min(values)),
391:    maximum_id = member_ids[values.index(max(values))]
423:        or operatives.get("allowance_rule")
424:        != "max(observed_drift_s,bracket_screen_s)"
426:        != "max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s"
434:        (max(values) - min(values)).quantize(
438:        and max(values).quantize(
1047:        "calibration_drift_allowance_s": None,
1409:    if any(value < min(corpus_values) or value > max(corpus_values) for value in new_valid_values):
1463:        pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
1493:    endpoint_max_decimal = max(pre_decimal, post_decimal)
1513:            "observed_drift_decimal_s": str(drift_decimal),
1558:    excess = max(drift_decimal - screen, Decimal(0))
1577:    allowance = max(drift_decimal, screen)
1578:    operative_bound = endpoint_max_decimal + allowance
1581:            "calibration_drift_allowance_s": float(allowance),
1585:    result["acceptance"]["allowance"] = {
1586:        "rule": "max(observed_drift_s,bracket_screen_s)",
1587:        "value_s": str(allowance),
1656:            window_end_s=max(window.end_s for window in windows),
1684:                window_end_s=max(window.end_s for window in windows),
1694:        window_end_s=max(window.end_s for window in windows),
  1320	                bracket_window_id,
  1321	                bracket_plan_id,
  1322	                bracket_plan_sha256,
  1323	                bracket_evidence_root_id,
  1324	                expected_runs_root,
  1325	            ):
  1326	                return result, ("calibration_bracket_binding_invalid",)
  1327	    # v2 remains an authenticated validation/reduction artifact, but only the
  1328	    # 59-pulse v3 protocol carries the governed 95/95 claim calibration.
  1329	    matching = [
  1330	        candidate
  1331	        for candidate in candidates
  1332	        if candidate.protocol_id == PROTOCOL_ID
  1333	        and all(
  1334	            candidate.bindings.get(field) == bindings.get(field)
  1335	            for field in V2_BINDING_FIELDS
  1336	        )
  1337	    ]
  1338	    matching_decimals: dict[int, Decimal] = {}
  1339	    for candidate in matching:
  1340	        candidate_decimal = _candidate_decimal(candidate)
  1341	        if candidate_decimal is None or candidate_decimal < 0:
  1342	            return result, ("instrument_calibration_invalid",)
  1343	        matching_decimals[id(candidate)] = candidate_decimal
  1344	    corpus_members = artifact["derivation_corpus"]["members"]
  1345	    observed_triggers = result["acceptance"]["prospective_rederivation"][
  1346	        "observed_triggers"
  1347	    ]
  1348	    if (
  1349	        protocol_sha256(PROTOCOL_ID) != prospective.get("protocol_sha256")
  1350	        or _current_estimator_code_sha256()
  1351	        != dict(prospective["estimator_code_sha256"])
  1352	    ):
  1353	        observed_triggers.append("protocol_or_estimator_byte_change")
  1354	    prior_ids = {
  1355	        observation["content_id"]
  1356	        for observation in artifact["prior_observation_set"]["observations"]
  1357	    }
  1358	    distinct_observations = {
  1359	        observation.content_id: observation
  1360	        for observation in ledger_snapshot.observations
  1361	        if observation.content_id is not None
  1362	    }
  1363	    distinct_live_observations = {
  1364	        content_id: observation
  1365	        for content_id, observation in distinct_observations.items()
  1366	        if not observation.is_historical_import
  1367	    }
  1368	    new_observations = [
  1369	        observation
  1370	        for content_id, observation in sorted(distinct_live_observations.items())
  1371	        if content_id not in prior_ids
  1372	    ]
  1373	    new_observations.extend(
  1374	        sorted(
  1375	            (
  1376	                observation
  1377	                for observation in ledger_snapshot.post_cutoff_live_observations(
  1378	                    cutoff["sequence"]
  1379	                )
  1380	                if observation.content_id is None
  1381	            ),
  1382	            key=lambda observation: (observation.sequence, observation.attempt_id),
  1383	        )
  1384	    )
  1385	    if any(
  1386	        observation.classification_disposition
  1387	        not in {"valid", "systematic-invalid", "ordinary-invalid"}
  1388	        for observation in new_observations
  1389	    ):
  1390	        return result, ("calibration_observation_unclassifiable",)
  1391	    valid_same_epoch = [
  1392	        observation
  1393	        for observation in distinct_observations.values()
  1394	        if observation.disposition == "valid"
  1395	        and dict(observation.identity_epoch) == dict(identity_epoch)
  1396	    ]
  1397	    if len(valid_same_epoch) >= 38:
  1398	        observed_triggers.append("corpus_doubles_from_19_to_38")
  1399	    corpus_values = [
  1400	        Decimal(member["b_fiducial_s"]) for member in corpus_members
  1401	    ]
  1402	    new_valid_values = [
  1403	        value
  1404	        for observation in new_observations
  1405	        if observation.disposition == "valid"
  1406	        and dict(observation.identity_epoch) == dict(identity_epoch)
  1407	        and (value := _decimal(observation.exact_bound_lexeme_s)) is not None
  1408	    ]
  1409	    if any(value < min(corpus_values) or value > max(corpus_values) for value in new_valid_values):
  1410	        observed_triggers.append(
  1411	            "new_valid_same_identity_capture_expands_observed_range"
  1412	        )
  1413	    if any(
  1414	        observation.disposition == "systematic-invalid"
  1415	        and dict(observation.identity_epoch) == dict(identity_epoch)
  1416	        for observation in new_observations
  1417	    ):
  1418	        observed_triggers.append(
  1419	            "new_systematic_failure_challenges_preflight_screen"
  1420	        )
  1421	    # R2 trigger evaluation ranges over the observation universe, not the
  1422	    # narrower bracket-candidate set.  A governed aborted PRE can therefore
  1423	    # stale the acceptance artifact even when no eligible endpoint pair is
  1424	    # available for this window.
  1425	    observation_stale_triggers = [
  1426	        trigger
  1427	        for trigger in observed_triggers
  1428	        if trigger == "new_systematic_failure_challenges_preflight_screen"
  1429	    ]
  1430	    if observation_stale_triggers:
  1431	        result["acceptance"]["freshness"].update(
  1432	            {
  1433	                "status": "stale",
  1434	                "reason": "prospective_rederivation_required",
  1435	                "stale_triggers": observation_stale_triggers,
tests/test_calibration_ledger.py:1066:    @unittest.skipUnless(
tests/test_calibration_bracketing.py:612:    @unittest.skipUnless(
tests/test_calibration_live_three_window.py:1366:    @unittest.skip("U2 successor engine pending")
tests/test_calibration_live_three_window.py:1376:    @unittest.skip("U2 successor engine pending")
tests/test_calibration_live_three_window.py:1383:    @unittest.skip("U2 successor engine pending")

exec
/bin/zsh -lc "sed -n '1,120p' joulewise/calibration_bracketing.py && rg -n \"calibration_bracketing\" joulewise/calibration_ledger.py joulewise/bundle_reader.py scripts/validate_powermetrics_fiducial.py | head -80" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
"""Claim-time pre/post powermetrics fiducial calibration bracketing.

The bracket carries a nonparametric 95/95 calibration-distribution bound into
claims only under the registered T1-T3 transfer assumptions; it does not turn
either finite sample maximum into an unconditional instrument property.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from pathlib import Path
from typing import Any, Mapping, Sequence

from joulewise.bundle_read import BundleReadError, BundleReader
from joulewise.calibration_ledger import (
    IDENTITY_EPOCH_FIELDS,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
    LedgerObservation,
    content_id_from_artifact_hashes,
)
from joulewise.powermetrics_fiducial import (
    CAPTURE_TIME_FIELD,
    MAX_AGE_S,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    REGION_COVERAGE_RESOLUTION_S,
    RESIDUAL_REGION_METHOD,
    V2_BINDING_FIELDS,
    capture_wall_time_from_events,
    protocol_pulse_count,
    protocol_sha256,
    verify_stored_evidence_physics,
)
from joulewise.schemas import CalibrationBracketingPolicy

BRACKET_SCHEMA = "joulewise.instrument_calibration_bracket.v1"
BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
ACCEPTANCE_FIXTURE_SCHEMA = (
    "joulewise.calibration_acceptance_bound.v2.fixture.v1"
)
ACCEPTANCE_EVALUATION_SCHEMA = "joulewise.calibration_acceptance_evaluation.v2"
DEFAULT_ACCEPTANCE_BOUND_PATH = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "calibration"
    / "calibration_acceptance_d079_v2.json"
)
DEFAULT_ACCEPTANCE_BOUND_SHA256 = (
    "9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb"
)
ISSUED_ACCEPTANCE_BOUND_SHA256 = (
    "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
)
_REPO_ROOT = Path(__file__).resolve().parents[1]
ESTIMATOR_CODE_PATHS = (
    "joulewise/powermetrics_fiducial.py",
    "joulewise/uncertainty_evidence.py",
    "joulewise/adapters/powermetrics.py",
    "joulewise/reduce.py",
)
ACCEPTANCE_IDENTITY_FIELDS = IDENTITY_EPOCH_FIELDS
_D102_OPERATIVE_VALUES = {
    "bracket_screen_s": "0.010818",
    "preflight_level_screen_s": "0.033558756679900",
    "max_budgetable_excess_s": "0.001275166090593858",
    "maximum_budgetable_drift_s": "0.012093166090593858",
}


@dataclass(frozen=True)
class CalibrationCandidate:
    relative_path: str
    manifest_sha256: str
    evidence_sha256: str
    protocol_id: str
    capture_wall_time_s: float
    # Production authentication stores the source decimal lexeme here.  Float
    # remains accepted only for backwards-compatible synthetic callers; the
    # authenticated loader below never takes that branch.
    b_fiducial_s: Decimal | str | float
    bindings: Mapping[str, Any]
    attempt_id: str | None = None
    content_id: str | None = None
    ledger_receipt_digest: str | None = None
    bracket_session_id: str | None = None
    bracket_slot: str | None = None
    bracket_window_id: str | None = None
    bracket_plan_id: str | None = None
    bracket_plan_sha256: str | None = None
    bracket_evidence_root_id: str | None = None
    bracket_runs_root: str | None = None

    def descriptor(self) -> dict[str, Any]:
        bound = _candidate_decimal(self)
        return {
            "relative_path": self.relative_path,
            "manifest_sha256": self.manifest_sha256,
            "evidence_sha256": self.evidence_sha256,
            "protocol_id": self.protocol_id,
            "capture_wall_time_s": self.capture_wall_time_s,
            # This descriptor is the recorded reducer boundary.  Keep both the
            # exact acceptance lexeme and its explicit binary64 projection.
            "b_fiducial_s": float(bound) if bound is not None else self.b_fiducial_s,
            "b_fiducial_decimal_s": str(bound) if bound is not None else None,
            "attempt_id": self.attempt_id,
            "content_id": self.content_id,
            "ledger_receipt_digest": self.ledger_receipt_digest,
            "bracket_session_id": self.bracket_session_id,
            "bracket_slot": self.bracket_slot,
            "bracket_window_id": self.bracket_window_id,
            "bracket_plan_id": self.bracket_plan_id,
            "bracket_plan_sha256": self.bracket_plan_sha256,
            "bracket_evidence_root_id": self.bracket_evidence_root_id,
            "bracket_runs_root": self.bracket_runs_root,
rg: joulewise/bundle_reader.py: No such file or directory (os error 2)

codex
The mutation probe is being done entirely in memory: the production module source is compiled with one local expression substitution per subprocess, and only the allowance regression is executed. No repository file is modified.
exec
/bin/zsh -lc "ALLOWANCE_MUTANT=\"drift_decimal\" python3 -c \"import importlib.util, os, pathlib, sys, types, unittest\\nname = \\\"joulewise.calibration_bracketing\\\"\\npath = pathlib.Path(\\\"joulewise/calibration_bracketing.py\\\")\\nsource = path.read_text()\\nold = \\\"allowance = max(drift_decimal, screen)\\\"\\nreplacement = \\\"allowance = \\\" + os.environ[\\\"ALLOWANCE_MUTANT\\\"]\\nassert source.count(old) == 1\\nsource = source.replace(old, replacement)\\nmodule = types.ModuleType(name)\\nmodule.__file__ = str(path.resolve())\\nmodule.__package__ = \\\"joulewise\\\"\\nmodule.__spec__ = importlib.util.spec_from_file_location(name, path)\\nsys.modules[name] = module\\nexec(compile(source, str(path), \\\"exec\\\"), module.__dict__)\\nsuite = unittest.defaultTestLoader.loadTestsFromName(\\\"tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows\\\")\\nresult = unittest.TextTestRunner(verbosity=1).run(suite)\\nraise SystemExit(0 if result.wasSuccessful() else 1)\\n\"" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 exited 1 in 0ms:
  File "<string>", line 1
    import importlib.util, os, pathlib, sys, types, unittest\nname = "joulewise.calibration_bracketing"\npath = pathlib.Path("joulewise/calibration_bracketing.py")\nsource = path.read_text()\nold = "allowance = max(drift_decimal, screen)"\nreplacement = "allowance = " + os.environ["ALLOWANCE_MUTANT"]\nassert source.count(old) == 1\nsource = source.replace(old, replacement)\nmodule = types.ModuleType(name)\nmodule.__file__ = str(path.resolve())\nmodule.__package__ = "joulewise"\nmodule.__spec__ = importlib.util.spec_from_file_location(name, path)\nsys.modules[name] = module\nexec(compile(source, str(path), "exec"), module.__dict__)\nsuite = unittest.defaultTestLoader.loadTestsFromName("tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows")\nresult = unittest.TextTestRunner(verbosity=1).run(suite)\nraise SystemExit(0 if result.wasSuccessful() else 1)\n
                                                             ^
SyntaxError: unexpected character after line continuation character

exec
/bin/zsh -lc "ALLOWANCE_MUTANT=\"screen\" python3 -c \"import importlib.util, os, pathlib, sys, types, unittest\\nname = \\\"joulewise.calibration_bracketing\\\"\\npath = pathlib.Path(\\\"joulewise/calibration_bracketing.py\\\")\\nsource = path.read_text()\\nold = \\\"allowance = max(drift_decimal, screen)\\\"\\nreplacement = \\\"allowance = \\\" + os.environ[\\\"ALLOWANCE_MUTANT\\\"]\\nassert source.count(old) == 1\\nsource = source.replace(old, replacement)\\nmodule = types.ModuleType(name)\\nmodule.__file__ = str(path.resolve())\\nmodule.__package__ = \\\"joulewise\\\"\\nmodule.__spec__ = importlib.util.spec_from_file_location(name, path)\\nsys.modules[name] = module\\nexec(compile(source, str(path), \\\"exec\\\"), module.__dict__)\\nsuite = unittest.defaultTestLoader.loadTestsFromName(\\\"tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows\\\")\\nresult = unittest.TextTestRunner(verbosity=1).run(suite)\\nraise SystemExit(0 if result.wasSuccessful() else 1)\\n\"" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 exited 1 in 0ms:
  File "<string>", line 1
    import importlib.util, os, pathlib, sys, types, unittest\nname = "joulewise.calibration_bracketing"\npath = pathlib.Path("joulewise/calibration_bracketing.py")\nsource = path.read_text()\nold = "allowance = max(drift_decimal, screen)"\nreplacement = "allowance = " + os.environ["ALLOWANCE_MUTANT"]\nassert source.count(old) == 1\nsource = source.replace(old, replacement)\nmodule = types.ModuleType(name)\nmodule.__file__ = str(path.resolve())\nmodule.__package__ = "joulewise"\nmodule.__spec__ = importlib.util.spec_from_file_location(name, path)\nsys.modules[name] = module\nexec(compile(source, str(path), "exec"), module.__dict__)\nsuite = unittest.defaultTestLoader.loadTestsFromName("tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows")\nresult = unittest.TextTestRunner(verbosity=1).run(suite)\nraise SystemExit(0 if result.wasSuccessful() else 1)\n
                                                             ^
SyntaxError: unexpected character after line continuation character

exec
/bin/zsh -lc "ALLOWANCE_MUTANT=\"min(drift_decimal, screen)\" python3 -c \"import importlib.util, os, pathlib, sys, types, unittest\\nname = \\\"joulewise.calibration_bracketing\\\"\\npath = pathlib.Path(\\\"joulewise/calibration_bracketing.py\\\")\\nsource = path.read_text()\\nold = \\\"allowance = max(drift_decimal, screen)\\\"\\nreplacement = \\\"allowance = \\\" + os.environ[\\\"ALLOWANCE_MUTANT\\\"]\\nassert source.count(old) == 1\\nsource = source.replace(old, replacement)\\nmodule = types.ModuleType(name)\\nmodule.__file__ = str(path.resolve())\\nmodule.__package__ = \\\"joulewise\\\"\\nmodule.__spec__ = importlib.util.spec_from_file_location(name, path)\\nsys.modules[name] = module\\nexec(compile(source, str(path), \\\"exec\\\"), module.__dict__)\\nsuite = unittest.defaultTestLoader.loadTestsFromName(\\\"tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows\\\")\\nresult = unittest.TextTestRunner(verbosity=1).run(suite)\\nraise SystemExit(0 if result.wasSuccessful() else 1)\\n\"" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 exited 1 in 0ms:
  File "<string>", line 1
    import importlib.util, os, pathlib, sys, types, unittest\nname = "joulewise.calibration_bracketing"\npath = pathlib.Path("joulewise/calibration_bracketing.py")\nsource = path.read_text()\nold = "allowance = max(drift_decimal, screen)"\nreplacement = "allowance = " + os.environ["ALLOWANCE_MUTANT"]\nassert source.count(old) == 1\nsource = source.replace(old, replacement)\nmodule = types.ModuleType(name)\nmodule.__file__ = str(path.resolve())\nmodule.__package__ = "joulewise"\nmodule.__spec__ = importlib.util.spec_from_file_location(name, path)\nsys.modules[name] = module\nexec(compile(source, str(path), "exec"), module.__dict__)\nsuite = unittest.defaultTestLoader.loadTestsFromName("tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows")\nresult = unittest.TextTestRunner(verbosity=1).run(suite)\nraise SystemExit(0 if result.wasSuccessful() else 1)\n
                                                             ^
SyntaxError: unexpected character after line continuation character

2026-08-07T20:22:46.991553Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "ALLOWANCE_MUTANT=\"min(drift_decimal, screen)\" python3 - <<'PY'
import importlib.util, os, pathlib, sys, types, unittest
name = \"joulewise.calibration_bracketing\"
path = pathlib.Path(\"joulewise/calibration_bracketing.py\")
source = path.read_text()
old = \"allowance = max(drift_decimal, screen)\"
replacement = \"allowance = \" + os.environ[\"ALLOWANCE_MUTANT\"]
assert source.count(old) == 1
source = source.replace(old, replacement)
module = types.ModuleType(name)
module.__file__ = str(path.resolve())
module.__package__ = \"joulewise\"
module.__spec__ = importlib.util.spec_from_file_location(name, path)
sys.modules[name] = module
exec(compile(source, str(path), \"exec\"), module.__dict__)
suite = unittest.defaultTestLoader.loadTestsFromName(\"tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows\")
result = unittest.TextTestRunner(verbosity=1).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
exec
/bin/zsh -lc "ALLOWANCE_MUTANT=\"drift_decimal\" python3 - <<'PY'
import importlib.util, os, pathlib, sys, types, unittest
name = \"joulewise.calibration_bracketing\"
path = pathlib.Path(\"joulewise/calibration_bracketing.py\")
source = path.read_text()
old = \"allowance = max(drift_decimal, screen)\"
replacement = \"allowance = \" + os.environ[\"ALLOWANCE_MUTANT\"]
assert source.count(old) == 1
source = source.replace(old, replacement)
module = types.ModuleType(name)
module.__file__ = str(path.resolve())
module.__package__ = \"joulewise\"
module.__spec__ = importlib.util.spec_from_file_location(name, path)
sys.modules[name] = module
exec(compile(source, str(path), \"exec\"), module.__dict__)
suite = unittest.defaultTestLoader.loadTestsFromName(\"tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows\")
result = unittest.TextTestRunner(verbosity=1).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
exec
/bin/zsh -lc "ALLOWANCE_MUTANT=\"screen\" python3 - <<'PY'
import importlib.util, os, pathlib, sys, types, unittest
name = \"joulewise.calibration_bracketing\"
path = pathlib.Path(\"joulewise/calibration_bracketing.py\")
source = path.read_text()
old = \"allowance = max(drift_decimal, screen)\"
replacement = \"allowance = \" + os.environ[\"ALLOWANCE_MUTANT\"]
assert source.count(old) == 1
source = source.replace(old, replacement)
module = types.ModuleType(name)
module.__file__ = str(path.resolve())
module.__package__ = \"joulewise\"
module.__spec__ = importlib.util.spec_from_file_location(name, path)
sys.modules[name] = module
exec(compile(source, str(path), \"exec\"), module.__dict__)
suite = unittest.defaultTestLoader.loadTestsFromName(\"tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows\")
result = unittest.TextTestRunner(verbosity=1).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 exited 1 in 350ms:
F
======================================================================
FAIL: test_d110_allowance_selects_both_max_operands_across_windows (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows) (window='beta', branch='observed_drift_s')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py", line 927, in test_d110_allowance_selects_both_max_operands_across_windows
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        allowance["value_s"], vector["selected_allowance_s"]
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: '0.010818' != '0.011000'
- 0.010818
+ 0.011000


----------------------------------------------------------------------
Ran 1 test in 0.374s

FAILED (failures=1)

 exited 1 in 355ms:
F
======================================================================
FAIL: test_d110_allowance_selects_both_max_operands_across_windows (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows) (window='alpha', branch='bracket_screen_s')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py", line 927, in test_d110_allowance_selects_both_max_operands_across_windows
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        allowance["value_s"], vector["selected_allowance_s"]
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: '0.001000' != '0.010818'
- 0.001000
+ 0.010818


----------------------------------------------------------------------
Ran 1 test in 0.377s

FAILED (failures=1)

 exited 1 in 358ms:
FF
======================================================================
FAIL: test_d110_allowance_selects_both_max_operands_across_windows (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows) (window='alpha', branch='bracket_screen_s')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py", line 927, in test_d110_allowance_selects_both_max_operands_across_windows
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        allowance["value_s"], vector["selected_allowance_s"]
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: '0.001000' != '0.010818'
- 0.001000
+ 0.010818


======================================================================
FAIL: test_d110_allowance_selects_both_max_operands_across_windows (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows) (window='beta', branch='observed_drift_s')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py", line 927, in test_d110_allowance_selects_both_max_operands_across_windows
    self.assertEqual(
    ~~~~~~~~~~~~~~~~^
        allowance["value_s"], vector["selected_allowance_s"]
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: '0.010818' != '0.011000'
- 0.010818
+ 0.011000


----------------------------------------------------------------------
Ran 1 test in 0.378s

FAILED (failures=2)

2026-08-07T20:22:55.150502Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "python3 - <<'PY'
import ast, subprocess
old = subprocess.run(['git','show','50404be:tests/test_calibration_live_three_window.py'], check=True, capture_output=True, text=True).stdout
new = open('tests/test_calibration_live_three_window.py').read()
def names(src):
    tree=ast.parse(src)
    return sorted(n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_'))
o=set(names(old)); n=set(names(new))
print('OLD',len(o)); print('\\n'.join(sorted(o)))
print('NEW',len(n)); print('\\n'.join(sorted(n)))
print('REMOVED',len(o-n)); print('\\n'.join(sorted(o-n)))
print('ADDED',len(n-o)); print('\\n'.join(sorted(n-o)))
PY

git diff --check origin/main...HEAD && git status --short --branch" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
OLD 19
test_all_six_are_same_epoch_causal_fresh_protocol_and_t1_eligible
test_all_three_verdicts_use_one_complete_candidate_universe
test_alpha_beta_gamma_each_bind_only_their_own_pre_post_pair
test_d102_observation_count_boundary_requires_successor
test_d110_never_zero_allowance_remains_active_for_all_verdicts
test_exactly_six_live_candidates_and_zero_imported_candidates
test_ideal_three_receipt_sessions_end_at_terminal_sequence_85
test_issuance_equivalent_base_has_76_receipts_and_30_2_6_dispositions
test_no_neighboring_endpoint_can_substitute_for_a_bound_endpoint
test_range_expanding_live_observation_requires_successor
test_refuses_head_pin_mismatch_rollback_fork_or_uncommitted_terminal_head
test_refuses_import_marker_removal_import_leakage_or_discovery_regression
test_refuses_missing_duplicate_reordered_or_conflicting_session_receipts
test_refuses_missing_tampered_swapped_or_cross_window_bracket_binding
test_refuses_noncausal_stale_t1_protocol_or_epoch_mismatched_endpoint
test_refuses_omitted_added_duplicated_off_ledger_or_substituted_observations
test_refuses_open_or_abandoned_session_without_governed_closure
test_refuses_systematic_classification
test_successor_prior_set_refuses_omitted_or_changed_authenticated_prefix
NEW 23
test_all_six_are_same_epoch_causal_fresh_protocol_and_t1_eligible
test_alpha_beta_gamma_each_bind_only_their_own_pre_post_pair
test_bundle_path_uses_ledger_discovery_as_candidate_authority
test_d102_observation_count_boundary_requires_successor
test_d110_allowance_selects_both_max_operands_across_windows
test_each_night_issues_its_verdict_at_a_committed_closeout
test_exactly_six_live_candidates_and_zero_imported_candidates
test_final_closeout_replays_all_verdicts_with_complete_universe
test_issuance_equivalent_base_has_76_receipts_and_30_2_6_dispositions
test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding
test_no_failure_campaign_has_36_valid_observations_two_short_of_trigger
test_no_neighboring_endpoint_can_substitute_for_a_bound_endpoint
test_production_writer_receipts_end_at_derived_terminal_sequence
test_range_expanding_live_observation_requires_successor
test_refuses_head_pin_mismatch_rollback_fork_or_uncommitted_terminal_head
test_refuses_import_marker_removal_import_leakage_or_discovery_regression
test_refuses_missing_duplicate_reordered_or_conflicting_session_receipts
test_refuses_missing_tampered_swapped_or_cross_window_bracket_binding
test_refuses_noncausal_stale_t1_protocol_or_epoch_mismatched_endpoint
test_refuses_omitted_added_duplicated_off_ledger_or_substituted_observations
test_refuses_open_or_abandoned_session_without_governed_closure
test_refuses_systematic_classification
test_successor_prior_set_refuses_omitted_or_changed_authenticated_prefix
REMOVED 3
test_all_three_verdicts_use_one_complete_candidate_universe
test_d110_never_zero_allowance_remains_active_for_all_verdicts
test_ideal_three_receipt_sessions_end_at_terminal_sequence_85
ADDED 7
test_bundle_path_uses_ledger_discovery_as_candidate_authority
test_d110_allowance_selects_both_max_operands_across_windows
test_each_night_issues_its_verdict_at_a_committed_closeout
test_final_closeout_replays_all_verdicts_with_complete_universe
test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding
test_no_failure_campaign_has_36_valid_observations_two_short_of_trigger
test_production_writer_receipts_end_at_derived_terminal_sequence
## impl/d117-u4-regression...origin/impl/d117-u4-regression

2026-08-07T20:23:01.233416Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "rg -n \"class _CaptureLedgerLifecycle|def begin|claim_bracket_session_slot|def finalize\" scripts/validate_powermetrics_fiducial.py | head -80 && nl -ba scripts/validate_powermetrics_fiducial.py | sed -n '350,500p' && nl -ba joulewise/calibration_ledger.py | sed -n '1,170p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
60:    claim_bracket_session_slot,
352:class _CaptureLedgerLifecycle:
391:    def begin(self) -> None:
409:            claim_bracket_session_slot(
457:    def finalize(
634:    def finalize_abandoned(
   350	
   351	
   352	class _CaptureLedgerLifecycle:
   353	    """Route one writer attempt through ordinary or bracket-session APIs."""
   354	
   355	    def __init__(
   356	        self,
   357	        *,
   358	        ledger_path: Path,
   359	        head_pin_path: Path,
   360	        attempt_id: str,
   361	        custody_locator: str,
   362	        identity_epoch: Mapping[str, Any],
   363	        t1_bindings: Mapping[str, Any],
   364	        session_id: str | None = None,
   365	        slot: str | None = None,
   366	        require_committed_pin: bool = True,
   367	    ) -> None:
   368	        if (session_id is None) != (slot is None):
   369	            raise CalibrationLedgerError(
   370	                "bracket session id and slot must be supplied together"
   371	            )
   372	        self.ledger_path = Path(ledger_path)
   373	        self.head_pin_path = Path(head_pin_path)
   374	        self.attempt_id = attempt_id
   375	        self.custody_locator = custody_locator
   376	        self.identity_epoch: Mapping[str, Any] = identity_epoch
   377	        self.t1_bindings: Mapping[str, Any] = t1_bindings
   378	        self.capture_wall_time_s: str | None = None
   379	        self.exact_bound_lexeme_s: str | None = None
   380	        self.session_id = session_id
   381	        self.slot = slot
   382	        self.require_committed_pin = require_committed_pin
   383	        self.claim_id = uuid.uuid4().hex
   384	        self.begun = False
   385	        self.closed = False
   386	
   387	    @property
   388	    def is_bracket_session(self) -> bool:
   389	        return self.session_id is not None
   390	
   391	    def begin(self) -> None:
   392	        """Reserve ordinarily, or authenticate a previously reserved slot."""
   393	
   394	        if self.begun:
   395	            raise CalibrationLedgerError("capture ledger lifecycle already began")
   396	        if self.is_bracket_session:
   397	            assert self.session_id is not None and self.slot is not None
   398	            _validate_reserved_bracket_slot(
   399	                self.ledger_path,
   400	                self.head_pin_path,
   401	                session_id=self.session_id,
   402	                slot=self.slot,
   403	                attempt_id=self.attempt_id,
   404	                custody_locator=self.custody_locator,
   405	                identity_epoch=self.identity_epoch,
   406	                t1_bindings=self.t1_bindings,
   407	                require_committed_pin=self.require_committed_pin,
   408	            )
   409	            claim_bracket_session_slot(
   410	                self.ledger_path,
   411	                session_id=self.session_id,
   412	                slot=self.slot,
   413	                attempt_id=self.attempt_id,
   414	                claim_id=self.claim_id,
   415	            )
   416	        else:
   417	            append_pending_receipt(
   418	                self.ledger_path,
   419	                attempt_id=self.attempt_id,
   420	                custody_locator=self.custody_locator,
   421	                identity_epoch=self.identity_epoch,
   422	                t1_bindings=self.t1_bindings,
   423	                head_pin_path=self.head_pin_path,
   424	                require_committed_pin=self.require_committed_pin,
   425	            )
   426	        self.begun = True
   427	
   428	    def abandon(self, reason: str) -> Mapping[str, Any] | None:
   429	        """Best-effort governed closure for an interrupted writer."""
   430	
   431	        if not self.begun or self.closed:
   432	            return None
   433	        if self.is_bracket_session:
   434	            assert self.session_id is not None
   435	            receipt = abort_bracket_session(
   436	                self.ledger_path,
   437	                session_id=self.session_id,
   438	                reason=reason,
   439	            )
   440	        else:
   441	            receipt = finalize_attempt_receipt(
   442	                self.ledger_path,
   443	                attempt_id=self.attempt_id,
   444	                disposition="abandoned",
   445	                custody_locator=self.custody_locator,
   446	                artifact_sha256=ledger_artifact_hashes(
   447	                    Path(self.custody_locator)
   448	                ),
   449	                identity_epoch=self.identity_epoch,
   450	                t1_bindings=self.t1_bindings,
   451	                capture_wall_time_s=self.capture_wall_time_s,
   452	                exact_bound_lexeme_s=self.exact_bound_lexeme_s,
   453	            )
   454	        self.closed = True
   455	        return receipt
   456	
   457	    def finalize(
   458	        self, disposition: str
   459	    ) -> tuple[Mapping[str, Any], dict[str, Any] | None]:
   460	        """Finalize the exact attempt and return any terminal head candidate."""
   461	
   462	        if not self.begun or self.closed:
   463	            raise CalibrationLedgerError("capture ledger lifecycle is not open")
   464	        artifacts = ledger_artifact_hashes(Path(self.custody_locator))
   465	        if self.is_bracket_session:
   466	            assert self.session_id is not None and self.slot is not None
   467	            receipt = finalize_bracket_session_slot(
   468	                self.ledger_path,
   469	                session_id=self.session_id,
   470	                slot=self.slot,
   471	                disposition=disposition,
   472	                custody_locator=self.custody_locator,
   473	                artifact_sha256=artifacts,
   474	                identity_epoch=self.identity_epoch,
   475	                t1_bindings=self.t1_bindings,
   476	                capture_wall_time_s=self.capture_wall_time_s,
   477	                exact_bound_lexeme_s=self.exact_bound_lexeme_s,
   478	            )
   479	            if self.slot == "pre" and disposition != "valid":
   480	                receipt = abort_bracket_session(
   481	                    self.ledger_path,
   482	                    session_id=self.session_id,
   483	                    reason=f"pre_capture_{disposition}",
   484	                )
   485	            self.closed = True
   486	            head_pin = (
   487	                None
   488	                if self.slot == "pre" and disposition == "valid"
   489	                else terminal_head_pin_for_session(
   490	                    self.ledger_path, session_id=self.session_id
   491	                )
   492	            )
   493	            return receipt, head_pin
   494	        receipt = finalize_attempt_receipt(
   495	            self.ledger_path,
   496	            attempt_id=self.attempt_id,
   497	            disposition=disposition,
   498	            custody_locator=self.custody_locator,
   499	            artifact_sha256=artifacts,
   500	            identity_epoch=self.identity_epoch,
     1	"""Authenticated calibration-observation receipt ledger (D-109).
     2	
     3	The ledger closes workflow omission, unregistered evidence, and rollback or
     4	stale-head consumption.  It does not defend against a malicious trusted
     5	writer or an authority that rewrites both Git and the complete ledger
     6	history.  Version 1 is deliberately a single-authority, single-machine
     7	protocol.
     8	
     9	Each ordinary capture is represented by two immutable hash-chained receipts:
    10	a reservation with disposition ``pending`` written before capture state
    11	exists, then exactly one finalization.  Bracket sessions reserve both slots in
    12	one capability and append an exclusive slot-claim before either writer creates
    13	capture state.  Evaluation consumes one frozen snapshot whose physical head
    14	must equal the repository-committed head pin.
    15	
    16	Ordinary appends use a crash-recovery sidecar beside the ledger.  The writer
    17	fsyncs a complete intended ledger line to the sidecar before touching the
    18	ledger, appends and fsyncs the ledger, then removes the sidecar.  A loader only
    19	recognizes a torn final line when its bytes are an exact prefix of that
    20	authenticated sidecar payload.  The next governed writer completes only the
    21	missing suffix (never deletes ledger bytes) and durably records a separate
    22	recovery-evidence JSON object before clearing the sidecar.
    23	"""
    24	
    25	from __future__ import annotations
    26	
    27	import fcntl
    28	import hashlib
    29	import json
    30	import os
    31	import re
    32	import stat
    33	import subprocess
    34	import tempfile
    35	from collections.abc import Mapping, Sequence
    36	from dataclasses import dataclass
    37	from pathlib import Path
    38	from types import MappingProxyType
    39	from typing import Any, BinaryIO
    40	
    41	from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
    42	
    43	
    44	LEDGER_SCHEMA = "joulewise.calibration_observation_ledger.v1"
    45	RECEIPT_SCHEMA = "joulewise.calibration_observation_receipt.v1"
    46	BRACKET_SESSION_SCHEMA = "joulewise.calibration_window_bracket_session.v1"
    47	BRACKET_SESSION_OPEN_EVENT = "bracket-session-open"
    48	BRACKET_SESSION_SLOT_CLAIM_EVENT = "bracket-session-slot-claim"
    49	BRACKET_SESSION_FINALIZATION_EVENT = "bracket-session-slot-finalization"
    50	BRACKET_SESSION_ABORT_EVENT = "bracket-session-abort"
    51	BRACKET_SESSION_SLOTS = ("pre", "post")
    52	APPEND_JOURNAL_SCHEMA = "joulewise.calibration_ledger_append_journal.v1"
    53	APPEND_RECOVERY_SCHEMA = "joulewise.calibration_ledger_append_recovery.v1"
    54	HISTORICAL_IMPORT_TABLE_SCHEMA = (
    55	    "joulewise.calibration_historical_import_table.v1"
    56	)
    57	HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA = (
    58	    "joulewise.calibration_historical_import_custody_manifest.v1"
    59	)
    60	HISTORICAL_IMPORT_EVENT_PREFIX = "historical-import-v1"
    61	HISTORICAL_IMPORT_RESERVATION_EVENT = (
    62	    f"{HISTORICAL_IMPORT_EVENT_PREFIX}-reservation"
    63	)
    64	HISTORICAL_IMPORT_FINALIZATION_EVENT = (
    65	    f"{HISTORICAL_IMPORT_EVENT_PREFIX}-finalization"
    66	)
    67	GENESIS_DIGEST = "0" * 64
    68	REPO_ROOT = Path(__file__).resolve().parents[1]
    69	DEFAULT_LEDGER_PATH = REPO_ROOT / "runs" / "calibration_observation_ledger.jsonl"
    70	DEFAULT_HEAD_PIN_PATH = (
    71	    REPO_ROOT / "configs" / "calibration" / "calibration_ledger_head.json"
    72	)
    73	
    74	IDENTITY_EPOCH_FIELDS = (
    75	    "os_build",
    76	    "hardware_model",
    77	    "power_policy",
    78	    "sampling_interval_ms",
    79	    "estimator_revision",
    80	    "pulse_protocol_id",
    81	)
    82	T1_FIELDS = tuple(V2_BINDING_FIELDS)
    83	FINAL_DISPOSITIONS = frozenset(
    84	    {"valid", "systematic-invalid", "ordinary-invalid", "abandoned"}
    85	)
    86	HISTORICAL_IMPORT_DISPOSITIONS = frozenset(
    87	    {"valid", "systematic-invalid", "ordinary-invalid"}
    88	)
    89	ALL_DISPOSITIONS = FINAL_DISPOSITIONS | {"pending"}
    90	CONTENT_ID_ARTIFACTS = (
    91	    "instrument_evidence.json",
    92	    "manifest.json",
    93	)
    94	GOVERNED_ARTIFACTS = (
    95	    "raw/powermetrics.plist",
    96	    "events.jsonl",
    97	    "power_trace.csv",
    98	    "instrument_evidence.json",
    99	    "manifest.json",
   100	)
   101	MANIFEST_BOUND_ARTIFACTS = tuple(
   102	    name for name in GOVERNED_ARTIFACTS if name != "manifest.json"
   103	)
   104	EVIDENCE_BOUND_ARTIFACTS = (
   105	    "raw/powermetrics.plist",
   106	    "events.jsonl",
   107	    "power_trace.csv",
   108	)
   109	_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
   110	
   111	# Stable refusal taxonomy.  Consumers propagate these exact spellings into
   112	# claim barriers; no malformed or unresolved history is silently omitted.
   113	REFUSAL_TAXONOMY: Mapping[str, str] = MappingProxyType(
   114	    {
   115	        "calibration_ledger_missing": "the pinned non-genesis ledger is absent",
   116	        "calibration_ledger_malformed": "ledger, receipt, or head-pin schema is malformed",
   117	        "calibration_ledger_chain_conflict": "sequence or predecessor linkage is not one linear chain",
   118	        "calibration_ledger_attempt_conflict": "an attempt has duplicate or conflicting state transitions",
   119	        "calibration_ledger_bracket_session_conflict": "a bracket session has duplicate, reordered, or conflicting state transitions",
   120	        "calibration_ledger_bracket_slot_claimed": "a bracket session slot already has an exclusive writer claim",
   121	        "calibration_ledger_bracket_session_open": "a bracket session has not finalized both slots or recorded a governed abort",
   122	        "calibration_ledger_content_conflict": "one content identity has conflicting authenticated classifications",
   123	        "calibration_ledger_pending": "at least one reservation is unresolved",
   124	        "calibration_ledger_head_uncommitted": "the head pin differs from the Git HEAD bytes",
   125	        "calibration_ledger_head_mismatch": "the physical head differs from the committed pin",
   126	        "calibration_ledger_rollback": "the physical ledger is a proper prefix of the pinned head",
   127	        "calibration_ledger_recovery_required": "the final ledger line is a journal-authenticated torn append requiring governed recovery",
   128	        "calibration_ledger_baseline_missing": "the acceptance cutoff is not in the current chain",
   129	        "calibration_ledger_custody_invalid": "receipt-bound evidence bytes are absent or hash-invalid",
   130	        "calibration_ledger_snapshot_required": "claim evaluation did not receive one immutable snapshot",
   131	        "calibration_ledger_off_ledger_artifact": "a calibration artifact is not registered in the snapshot",
   132	        "calibration_observation_unclassifiable": "a governed observation has no ruled disposition",
   133	    }
   134	)
   135	
   136	
   137	class CalibrationLedgerError(ValueError):
   138	    """A writer-side ledger operation cannot preserve the D-109 contract."""
   139	
   140	
   141	def _jsonable(value: Any) -> Any:
   142	    if isinstance(value, Mapping):
   143	        return {key: _jsonable(item) for key, item in value.items()}
   144	    if isinstance(value, (list, tuple)):
   145	        return [_jsonable(item) for item in value]
   146	    return value
   147	
   148	
   149	def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
   150	    return json.dumps(
   151	        _jsonable(value),
   152	        sort_keys=True,
   153	        separators=(",", ":"),
   154	        ensure_ascii=False,
   155	        allow_nan=False,
   156	    ).encode("utf-8")
   157	
   158	
   159	def canonical_sha256(value: Mapping[str, Any]) -> str:
   160	    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
   161	
   162	
   163	def _is_sha256(value: object) -> bool:
   164	    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None
   165	
   166	
   167	def _normalized_vector(
   168	    value: Mapping[str, Any] | None,
   169	    fields: Sequence[str],
   170	) -> dict[str, Any]:

2026-08-07T20:23:11.050926Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc 'git rev-parse --short impl/d117-u1-ledger-session && git rev-parse --short origin/impl/d117-u1-ledger-session && git rev-parse --short impl/d117-u2-successor && git rev-parse --short origin/impl/d117-u2-successor && git log --oneline --decorate --graph --max-count=30 --all --simplify-by-decoration' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
1cf7a42
1cf7a42
399ffeb
399ffeb
* 4b82180 (HEAD -> impl/d117-u4-regression, origin/impl/d117-u4-regression) U4 amendment round (FIX-A..F): terminal sequence DERIVED from production receipt count (76 + 3x5 = 91, superseding the memo's stale 85 three-receipt model); allowance test now straddles the 0.010818 bound so both max() branches are exercised; L5 named; positive count oracle; per-window verdict issuance; real discovery-authority test
| * 1b66032 (origin/main, origin/HEAD, main) RUN_STATE near-final: 8 Ed rulings owed, U-unit state (U1 PR #111, U3 delta pending, U2 cold-gate exhibit, U8 held on REWORK), binding rules adopted, corrected portfolio night counts
|/  
| * 399ffeb (origin/impl/d117-u2-successor, impl/d117-u2-successor) U2 speculative implementation (COLD-GATE EXHIBIT — not a landing candidate): D-102 successor engine with registry authentication, deterministic Decimal derivation, trigger probing, guarded publication. All 12 contested design choices implemented at the design brief's recommended answer and tagged COLD-GATE-Q1..Q12 so the gate can flip any ruling with a minimal diff.
|/  
| * 454f777 (origin/impl/d117-u3-pinset-v2, impl/d117-u3-pinset-v2) U3 FIX-1b/6b/8: authenticated postcollection pins (named equality check per custody field against supplied evidence — presence no longer satisfies a pin), three-way six-decimal/full-precision/report consistency with the coordinated-inconsistency regression, production-CLI authentication path test, implementation-independent golden fixture
|/  
| * 6b497d7 (origin/impl/d117-u8-readiness, impl/d117-u8-readiness) U8 speculative implementation (EVIDENCE ONLY — examination verdict is REWORK; do not land): frozen-plan readiness validator + additive D-117 runbook bookends. Blocked pending two rulings — zero-retry semantics vs the runbook's still-live cause-removal retry paragraph, and whether readiness reason codes enter the ratified refusal spec's S1 domain (an S4 cold-gate move).
|/  
| * 1cf7a42 (origin/impl/d117-u1-ledger-session, impl/d117-u1-ledger-session) U1 FIX-6b: deterministic idempotent append-recovery evidence (recomputed from journal record + ledger tail; matching evidence resumes to journal clearing; genuine mismatch still refuses) + subprocess crash and mismatch regressions
|/  
* 6a70707 (impl/paper-mvp-complete) Merge pull request #110 from mpmdw/impl/paper-mvp-complete
* d9b8c5f (origin/impl/paper-mvp-complete) Merge main (D-117 index-row CI fix) into paper branch
* d85b4f9 (origin/impl/d079-issuance) test: reconcile suite to the ISSUED D-079 anchor — decouple synthetic scenarios from live committed anchor state; add live-anchor lock-in
* 71bf5ce (origin/impl/issuance-consumer) Merge remote-tracking branch 'origin/main' into impl/issuance-consumer
* ee4f1a5 (origin/impl/paper-draft-v1) paper(draft-v1): apply method-fidelity review — third-failure closes WINDOW not stage (blocker); bracket-drift screen added; qualify powermetrics validation to timing-attribution; define idle-subtracted energy
* 83572a2 (origin/impl/quiet-guard) Merge remote-tracking branch 'origin/main' into impl/quiet-guard
* f08158e (origin/impl/ledger-bootstrap) Merge remote-tracking branch 'origin/main' into impl/ledger-bootstrap
* 5b229f6 (origin/impl/validator-rootpins) Merge remote-tracking branch 'origin/main' into impl/validator-rootpins
* f650d28 (origin/impl/queue-registration) bookkeeping: registration batch — retire COLDGATE-VALIDATOR-01 + WINB-R06-DISPOSITION-01; register COLDGATE-HANDOFF-01, CGV-HARDEN-01, T3-PROV-SCHEMA-01, CODEX-BRIDGE-SANDBOX-01; MINT-GENERALIZE dep split; MET-WINDOW-C re-scope + start fence; runbook D-113 cl.9 clock-retry prohibition
* 0bea908 (origin/impl/coldgate-validator) Merge remote-tracking branch 'origin/main' into impl/coldgate-validator
* e8f1042 (origin/impl/codex-fast-tier) Merge remote-tracking branch 'origin/main' into impl/codex-fast-tier
*   9b02539 Merge pull request #98 from mpmdw/impl/test-speed
|\  
| * 61c7d2c (origin/impl/test-speed) TEST-SPEED-01 Phase 1: module-atomic test shard-runner + CI shard matrix
* |   32d72fd Merge pull request #99 from mpmdw/impl/d100-bii-binding
|\ \  
| * | 751e6ee (origin/impl/d100-bii-binding, impl/d100-bii-binding) D-108 fix round 1 (audit F1): restore the top-level failed-summary allowlist
* | | 87fb143 (origin/impl/nvidia-retention-flake) NVIDIA-RETENTION-FLAKE-01: hermetic per-test retention roots (close the shared-custody-path flake)
| |/  
|/|   
* | 4e94e70 (origin/impl/mint-generalize) MINT-GENERALIZE-01: generalized mint sibling with authenticated per-plan pinsets
* |   200e6db Merge PR #95: MANIFEST-CONTRAST-01, analysis-manifest v3 (branch at audited head e94d4a7)
|\ \  
| |/  
|/|   
| * e94d4a7 (origin/impl/manifest-contrast-v3, impl/manifest-contrast-v3) v3 embedded-floor-bytes round (ruled): claim artifacts embed the SHA-verified floor artifact; one authenticated derivation source for runtime and validation; mutable evidence_root_ids field deleted
* | 05d99b6 (origin/impl/met-dangler-disposition, impl/met-dangler-disposition) D-100 brief-repair round: content-general b-i byte sweep (any-hit-voids over every file under every custody root) and closed b-ii inventory (exact set equality + per-file admission-phase schema validation)
|/  
*   cb860e1 Merge pull request #93 from mpmdw/impl/cooldown-gauntlet-c3
|\  
| * 6070ac4 (origin/impl/cooldown-gauntlet-c3) C3 pin exactness: freeze the F1 misclassification set literally ({21..26}) — any deviation in either direction hard-fails
* | 3e251bf (origin/impl/microdelta-f2-hardening) D-096 F2: harden micro_delta generate_configs --k — canonicalize (sorted set) and refuse stale k outputs before any write
|/  
*   67d268a Merge pull request #91 from mpmdw/impl/cooldown-gauntlet
|\  

2026-08-07T20:23:17.113972Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc 'git log --oneline f665dd4..origin/impl/d117-u1-ledger-session && git diff --stat f665dd4..origin/impl/d117-u1-ledger-session && git diff --name-status f665dd4..origin/impl/d117-u1-ledger-session && git merge-tree $(git merge-base HEAD origin/impl/d117-u1-ledger-session) HEAD origin/impl/d117-u1-ledger-session | rg -n '"'"'^(changed in both|CONFLICT|<<<<<<<|=======|>>>>>>>|added in both|removed in)'"' || true" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
1cf7a42 U1 FIX-6b: deterministic idempotent append-recovery evidence (recomputed from journal record + ledger tail; matching evidence resumes to journal clearing; genuine mismatch still refuses) + subprocess crash and mismatch regressions
 joulewise/calibration_ledger.py  |  21 +++++--
 tests/test_calibration_ledger.py | 126 +++++++++++++++++++++++++++++++++++++++
 2 files changed, 141 insertions(+), 6 deletions(-)
M	joulewise/calibration_ledger.py
M	tests/test_calibration_ledger.py

2026-08-07T20:23:22.215194Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "rg -n \"open_beta|cross_window_openness|campaign_terminal|re.verif|identical verdict|fixture_spec|sole.source|double|patch\\(\" tests/test_calibration_live_three_window.py tests/fixtures/calibration_live_three_window/scenario.json && git diff --unified=3 50404be..4b82180 -- tests/test_calibration_live_three_window.py | sed -n '280,620p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
tests/test_calibration_live_three_window.py:509:        with patch(
tests/test_calibration_live_three_window.py:530:        with patch(
tests/test_calibration_live_three_window.py:613:        with patch(
tests/test_calibration_live_three_window.py:643:            patch(
tests/test_calibration_live_three_window.py:647:            patch(
tests/test_calibration_live_three_window.py:651:            patch(
tests/test_calibration_live_three_window.py:655:            patch(
tests/test_calibration_live_three_window.py:779:        for index, vector in enumerate(expected["cross_window_openness"], start=1):
tests/test_calibration_live_three_window.py:963:                "corpus_doubles_from_19_to_38",
tests/fixtures/calibration_live_three_window/scenario.json:135:    "cross_window_openness": [
tests/fixtures/calibration_live_three_window/scenario.json:158:      "expected_trigger": "corpus_doubles_from_19_to_38"
         }
-        self.assertEqual(len(candidates), 6)
+        expected = self.scenario["expected_live_extension"]
+        self.assertEqual(len(candidates), expected["candidate_count"])
         self.assertEqual(authenticated_attempts & imported_attempts, set())
         self.assertTrue(all(candidate.bracket_session_id for candidate in candidates))
 
+    def test_bundle_path_uses_ledger_discovery_as_candidate_authority(self) -> None:
+        window = self.windows["gamma"]
+        reader = SimpleNamespace(
+            measured_window=lambda: SimpleNamespace(
+                start_s=window["window_start_s"],
+                end_s=window["window_end_s"],
+            ),
+            metadata=lambda: {
+                "instrument_calibration": {"bindings": dict(self.t1)}
+            },
+        )
+        with (
+            patch(
+                "joulewise.calibration_bracketing.BundleReader",
+                return_value=reader,
+            ),
+            patch(
+                "joulewise.calibration_bracketing._candidate_from_observation",
+                side_effect=self._candidate,
+            ),
+            patch(
+                "joulewise.calibration_bracketing.discover_calibration_candidates",
+                wraps=discover_calibration_candidates,
+            ) as discover,
+            patch(
+                "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
+                return_value=self.acceptance,
+            ),
+        ):
+            result, reasons = calibration_bracket_for_bundles(
+                Path(window["runs_root"]),
+                [Path(window["runs_root"]) / "science-member"],
+                self.policy,
+                ledger_snapshot=self.snapshot,
+                bracket_binding=self.bindings["gamma"],
+                bracket_window_id=window["window_id"],
+                bracket_plan_id=window["plan_id"],
+                bracket_plan_sha256=window["plan_sha256"],
+                bracket_evidence_root_id=window["evidence_root_id"],
+            )
+        discover.assert_called_once_with(self.snapshot)
+        self.assertEqual(reasons, ())
+        self.assertEqual(result["status"], "passed")
+        self.assertEqual(
+            [result[slot]["attempt_id"] for slot in ("pre", "post")],
+            ["d117-gamma-pre", "d117-gamma-post"],
+        )
+
     def test_alpha_beta_gamma_each_bind_only_their_own_pre_post_pair(self) -> None:
         for name, window in self.windows.items():
             with self.subTest(window=name):
@@ -578,49 +740,232 @@ class CalibrationLiveThreeWindowTests(unittest.TestCase):
                 _result, reasons = self._evaluate(name, binding=tampered)
                 self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
 
-    def test_all_three_verdicts_use_one_complete_candidate_universe(self) -> None:
+    def test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding(
+        self,
+    ) -> None:
+        beta = self.windows["beta"]
+        by_attempt = {candidate.attempt_id: candidate for candidate in self.candidates}
+        foreign_pre = by_attempt["d117-alpha-pre"]
+        foreign_post = by_attempt["d117-gamma-post"]
+        self.assertNotEqual(foreign_pre.bracket_runs_root, beta["runs_root"])
+        self.assertNotEqual(foreign_post.bracket_runs_root, beta["runs_root"])
+        self.assertLessEqual(foreign_pre.capture_wall_time_s, beta["window_start_s"])
+        self.assertGreaterEqual(foreign_post.capture_wall_time_s, beta["window_end_s"])
+
+        _result, reasons = self._evaluate("beta", binding=None)
+        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))
+
+        result, reasons = self._evaluate(
+            "beta", binding=self.bindings["beta"]
+        )
+        self.assertEqual(reasons, ())
+        self.assertEqual(
+            [result[slot]["attempt_id"] for slot in ("pre", "post")],
+            ["d117-beta-pre", "d117-beta-post"],
+        )
+        self.assertNotIn(
+            foreign_pre.attempt_id,
+            {result["pre"]["attempt_id"], result["post"]["attempt_id"]},
+        )
+        self.assertNotIn(
+            foreign_post.attempt_id,
+            {result["pre"]["attempt_id"], result["post"]["attempt_id"]},
+        )
+
+    def test_each_night_issues_its_verdict_at_a_committed_closeout(self) -> None:
+        expected = self.scenario["expected_live_extension"]
+        pin_commits = []
+        pin_digests = []
+        for index, vector in enumerate(expected["cross_window_openness"], start=1):
+            name = vector["closeout"]
+            snapshot = self.closeouts[name]["snapshot"]
+            pin_value = json.loads(self.closeouts[name]["pin_bytes"])
+            candidates = self._discover(snapshot)
+            candidate_window_ids = {
+                candidate.bracket_window_id for candidate in candidates
+            }
+            expected_window_ids = {
+                self.windows[window_name]["window_id"]
+                for window_name in vector["candidate_windows"]
+            }
+            with self.subTest(closeout=name):
+                self.assertEqual(snapshot.refusal_reasons, ())
+                self.assertEqual(len(snapshot.bracket_sessions), index)
+                self.assertEqual(
+                    len(
+                        [
+                            observation
+                            for observation in snapshot.observations
+                            if not observation.is_historical_import
+                        ]
+                    ),
+                    index * 2,
+                )
+                self.assertEqual(
+                    snapshot.head_sequence,
+                    self.base_sequence + index * _PRODUCTION_RECEIPTS_PER_SESSION,
+                )
+                self.assertEqual(pin_value["sequence"], snapshot.head_sequence)
+                self.assertEqual(pin_value["head_digest"], snapshot.head_digest)
+                self.assertEqual(candidate_window_ids, expected_window_ids)
+                result, reasons = self._evaluate(
+                    name,
+                    snapshot=snapshot,
+                    candidates=candidates,
+                    binding=self.bindings[name],
+                )
+                self.assertEqual(reasons, ())
+                self.assertEqual(result["status"], "passed")
+                self.assertEqual(
+                    result["acceptance"]["ledger_snapshot"]["sequence"],
+                    snapshot.head_sequence,
+                )
+            pin_commits.append(self.closeouts[name]["pin_commit"])
+            pin_digests.append(pin_value["head_digest"])
+        self.assertEqual(len(set(pin_commits)), _LIVE_SESSION_COUNT)
+        self.assertEqual(len(set(pin_digests)), _LIVE_SESSION_COUNT)
+
+    def test_final_closeout_replays_all_verdicts_with_complete_universe(self) -> None:
         snapshots = []
         for name in self.windows:
             result, reasons = self._evaluate(name, candidates=self.candidates)
             self.assertEqual(reasons, ())
             snapshots.append(result["acceptance"]["ledger_snapshot"])
         self.assertEqual(snapshots, [snapshots[0]] * 3)
-        self.assertEqual(snapshots[0]["sequence"], 85)
+        self.assertEqual(snapshots[0]["sequence"], _EXPECTED_TERMINAL_SEQUENCE)
         for name in self.windows:
             _result, reasons = self._evaluate(
                 name, candidates=self.candidates[:-1]
             )
             self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))
 
-    def test_ideal_three_receipt_sessions_end_at_terminal_sequence_85(self) -> None:
+    def test_production_writer_receipts_end_at_derived_terminal_sequence(self) -> None:
         live = self.snapshot.receipts[self.base_sequence :]
         expected = self.scenario["expected_live_extension"]
-        self.assertEqual(self.snapshot.head_sequence, expected["terminal_sequence"])
-        self.assertEqual(len(live), 9)
-        for index, window in enumerate(self.scenario["windows"]):
-            rows = live[index * 3 : index * 3 + 3]
+        receipt_model = expected["receipt_model_supersession"]["landed"]
+        self.assertEqual(self.snapshot.head_sequence, _EXPECTED_TERMINAL_SEQUENCE)
+        self.assertEqual(
+            len(live),
+            expected["session_count"] * _PRODUCTION_RECEIPTS_PER_SESSION,
+        )
+        self.assertEqual(
+            receipt_model["receipts_per_session"],
+            _PRODUCTION_RECEIPTS_PER_SESSION,
+        )
+        for index, window in enumerate(self.windows.values()):
+            start = index * _PRODUCTION_RECEIPTS_PER_SESSION
+            rows = live[start : start + _PRODUCTION_RECEIPTS_PER_SESSION]
             self.assertEqual(
                 [row["event"] for row in rows],
                 [
                     BRACKET_SESSION_OPEN_EVENT,
+                    BRACKET_SESSION_SLOT_CLAIM_EVENT,
                     BRACKET_SESSION_FINALIZATION_EVENT,
+                    BRACKET_SESSION_SLOT_CLAIM_EVENT,
                     BRACKET_SESSION_FINALIZATION_EVENT,
                 ],
             )
             self.assertEqual({row["session_id"] for row in rows}, {window["session_id"]})
-            self.assertEqual([rows[1]["slot"], rows[2]["slot"]], ["pre", "post"])
+            self.assertEqual(
+                [row["slot"] for row in rows[1:]],
+                ["pre", "pre", "post", "post"],
+            )
+        live_observations = [
+            observation
+            for observation in self.snapshot.observations
+            if not observation.is_historical_import
+        ]
+        self.assertEqual(
+            len(self.snapshot.bracket_sessions), expected["session_count"]
+        )
+        self.assertEqual(
+            {session.state for session in self.snapshot.bracket_sessions},
+            {"finalized"},
+        )
+        self.assertEqual(
+            len(live_observations), expected["live_observation_count"]
+        )
+        self.assertTrue(
+            all(
+                observation.observation_kind == "bracket-session-finalized"
+                and observation.disposition == "valid"
+                for observation in live_observations
+            )
+        )
 
-    def test_d110_never_zero_allowance_remains_active_for_all_verdicts(self) -> None:
+    def test_d110_allowance_selects_both_max_operands_across_windows(self) -> None:
         expected = self.scenario["expected_live_extension"]
-        for name in self.windows:
-            with self.subTest(window=name):
-                result, reasons = self._evaluate(name)
+        by_attempt = {candidate.attempt_id: candidate for candidate in self.candidates}
+        for vector in expected["allowance_branch_vectors"]:
+            name = vector["window"]
+            overridden = dict(by_attempt)
+            for slot in ("pre", "post"):
+                attempt_id = f"d117-{name}-{slot}"
+                overridden[attempt_id] = replace(
+                    overridden[attempt_id],
+                    b_fiducial_s=vector[f"{slot}_bound_s"],
+                )
+            candidates = tuple(
+                overridden[candidate.attempt_id] for candidate in self.candidates
+            )
+            with self.subTest(window=name, branch=vector["branch"]):
+                observed = Decimal(vector["observed_drift_s"])
+                screen = Decimal(expected["never_zero_allowance_s"])
+                if vector["branch"] == "bracket_screen_s":
+                    self.assertLess(observed, screen)
+                else:
+                    self.assertEqual(vector["branch"], "observed_drift_s")
+                    self.assertGreater(observed, screen)
+                result, reasons = self._evaluate(name, candidates=candidates)
                 self.assertEqual(reasons, ())
                 allowance = result["acceptance"]["allowance"]
                 self.assertEqual(allowance["rule"], expected["allowance_rule"])
-                self.assertEqual(allowance["value_s"], expected["never_zero_allowance_s"])
+                self.assertEqual(
+                    result["acceptance"]["drift"]["observed_s"],
+                    vector["observed_drift_s"],
+                )
+                self.assertEqual(
+                    allowance["value_s"], vector["selected_allowance_s"]
+                )
                 self.assertEqual(allowance["embedding_count"], 1)
 
+    def test_no_failure_campaign_has_36_valid_observations_two_short_of_trigger(
+        self,
+    ) -> None:
+        expected = self.scenario["expected_live_extension"][
+            "valid_observation_count"
+        ]
+        issuance_valid = {
+            observation.content_id
+            for observation in self.snapshot.observations
+            if observation.is_historical_import
+            and observation.disposition == "valid"
+            and dict(observation.identity_epoch) == self.epoch
+        }
+        valid_same_epoch = {
+            observation.content_id
+            for observation in self.snapshot.observations
+            if observation.disposition == "valid"
+            and dict(observation.identity_epoch) == self.epoch
+        }
+        self.assertEqual(len(issuance_valid), expected["issuance"])
+        self.assertEqual(
+            len(valid_same_epoch), expected["after_three_live_windows"]
+        )
+        self.assertEqual(
+            expected["corpus_doubling_trigger"] - len(valid_same_epoch),
+            expected["shortfall"],
+        )
+        for name in self.windows:
+            result, reasons = self._evaluate(name)
+            self.assertEqual(reasons, ())
+            self.assertNotIn(
+                "corpus_doubles_from_19_to_38",
+                result["acceptance"]["prospective_rederivation"][
+                    "observed_triggers"
+                ],
+            )
+
     def test_refuses_import_marker_removal_import_leakage_or_discovery_regression(
         self,
     ) -> None:
@@ -658,19 +1003,34 @@ class CalibrationLiveThreeWindowTests(unittest.TestCase):
     def test_refuses_missing_duplicate_reordered_or_conflicting_session_receipts(
         self,
     ) -> None:
+        alpha_session = self.windows["alpha"]["session_id"]
+        post_claim = self._receipt_index(
+            alpha_session, BRACKET_SESSION_SLOT_CLAIM_EVENT, "post"
+        )
+        post_final = self._receipt_index(
+            alpha_session, BRACKET_SESSION_FINALIZATION_EVENT, "post"
+        )
+        session_open = self._receipt_index(
+            alpha_session, BRACKET_SESSION_OPEN_EVENT
+        )
         variants: dict[str, list[dict]] = {}
-        variants["missing"] = self.receipts[:80] + self.receipts[81:]
+        variants["missing"] = (
+            self.receipts[:post_final] + self.receipts[post_final + 1 :]
+        )
         variants["duplicate"] = (
-            self.receipts[:81]
-            + [copy.deepcopy(self.receipts[80])]
-            + self.receipts[81:]
+            self.receipts[: post_final + 1]
+            + [copy.deepcopy(self.receipts[post_final])]
+            + self.receipts[post_final + 1 :]
         )
         reordered = copy.deepcopy(self.receipts)
-        reordered[79], reordered[80] = reordered[80], reordered[79]
+        reordered[post_claim], reordered[post_final] = (
+            reordered[post_final],
+            reordered[post_claim],
+        )
         variants["reordered"] = reordered
         conflicting = copy.deepcopy(self.receipts)
-        conflicting[78]["window_id"] = "conflicting-alpha-window"
-        conflicting[78] = _receipt(conflicting[78])

exec
/bin/zsh -lc "rg -n \"runs_root|expected_runs_root|bracket_runs_root\" joulewise/calibration_bracketing.py | head -120 && nl -ba joulewise/calibration_bracketing.py | sed -n '700,930p' && nl -ba joulewise/calibration_bracketing.py | sed -n '1190,1330p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
97:    bracket_runs_root: str | None = None
120:            "bracket_runs_root": self.bracket_runs_root,
519:    "runs_root",
544:    runs_root: Path | str,
556:        str(Path(runs_root).absolute()),
566:            session.runs_root,
592:        "runs_root": session.runs_root,
620:    runs_root: Path | str | None = None,
640:    ) or runs_root is None:
642:    expected_runs_root = str(Path(runs_root).absolute())
648:        ("runs_root", expected_runs_root),
660:        or binding.get("runs_root") != session.runs_root
747:    directory: Path, *, runs_root: Path
751:    root = Path(runs_root).resolve()
882:        runs_root=custody.parent.parent,
925:        bracket_runs_root=observation.bracket_runs_root,
1029:    bracket_runs_root: Path | str | None = None,
1188:            "global_runs_root_scan": False,
1265:            or candidate.bracket_runs_root != observation.bracket_runs_root
1284:            or bracket_runs_root is None
1287:        expected_runs_root = str(Path(bracket_runs_root).absolute())
1295:            runs_root=expected_runs_root,
1307:            "runs_root": bracket_binding["runs_root"],
1318:                candidate.bracket_runs_root,
1324:                expected_runs_root,
1599:    runs_root: Path,
1703:        bracket_runs_root=runs_root,
   700	        != post.receipt_digest
   701	    ):
   702	        return None
   703	    return resolved[0], resolved[1]
   704	
   705	
   706	def _binding_evidence_authentic(
   707	    evidence: Mapping[str, Any], bindings: Mapping[str, Any]
   708	) -> bool:
   709	    binding_evidence = evidence.get("binding_evidence")
   710	    binary = (
   711	        binding_evidence.get("powermetrics_binary")
   712	        if isinstance(binding_evidence, Mapping)
   713	        else None
   714	    )
   715	    power_policy = (
   716	        binding_evidence.get("power_policy")
   717	        if isinstance(binding_evidence, Mapping)
   718	        else None
   719	    )
   720	    # Canonical form MUST match the generation (powermetrics_fiducial) and
   721	    # reduce-side consumers byte-for-byte: ensure_ascii=False (delta-review
   722	    # P2 — the ASCII-default form made authentic non-ASCII binding vectors
   723	    # unmatchable as bracket candidates).
   724	    canonical = json.dumps(
   725	        dict(bindings),
   726	        sort_keys=True,
   727	        separators=(",", ":"),
   728	        ensure_ascii=False,
   729	        allow_nan=False,
   730	    ).encode("utf-8")
   731	    return bool(
   732	        isinstance(binding_evidence, Mapping)
   733	        and binding_evidence.get("schema_version")
   734	        == "joulewise.instrument_binding_evidence.v1"
   735	        and binding_evidence.get("binding_vector_sha256")
   736	        == hashlib.sha256(canonical).hexdigest()
   737	        and isinstance(binary, Mapping)
   738	        and binary.get("sha256") == bindings.get("powermetrics_sha256")
   739	        and isinstance(binary.get("path"), str)
   740	        and bool(binary.get("path"))
   741	        and isinstance(power_policy, Mapping)
   742	        and power_policy.get("id") == bindings.get("power_policy")
   743	    )
   744	
   745	
   746	def load_calibration_candidate(
   747	    directory: Path, *, runs_root: Path
   748	) -> CalibrationCandidate | None:
   749	    """Authenticate one standalone validation directory from primary bytes."""
   750	
   751	    root = Path(runs_root).resolve()
   752	    try:
   753	        directory = Path(directory).resolve(strict=True)
   754	        relative = directory.relative_to(root).as_posix()
   755	        manifest_raw = (directory / "manifest.json").read_bytes()
   756	        manifest = json.loads(manifest_raw)
   757	    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
   758	        return None
   759	    artifacts = manifest.get("artifacts") if isinstance(manifest, Mapping) else None
   760	    if (
   761	        not relative
   762	        or not isinstance(artifacts, Mapping)
   763	        or manifest.get("schema_version")
   764	        != "joulewise.instrument_validation_manifest.v1"
   765	    ):
   766	        return None
   767	    members: dict[str, bytes] = {}
   768	    for name, expected in artifacts.items():
   769	        if not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts:
   770	            return None
   771	        try:
   772	            member = (directory / name).resolve(strict=True)
   773	            member.relative_to(directory)
   774	            raw = member.read_bytes()
   775	        except (OSError, ValueError):
   776	            return None
   777	        if not _valid_sha256(expected) or hashlib.sha256(raw).hexdigest() != expected:
   778	            return None
   779	        members[name] = raw
   780	    try:
   781	        evidence_raw = members["instrument_evidence.json"]
   782	        events_raw = members["events.jsonl"]
   783	        powermetrics_raw = members["raw/powermetrics.plist"]
   784	        evidence = json.loads(evidence_raw)
   785	    except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
   786	        return None
   787	    if not isinstance(evidence, Mapping):
   788	        return None
   789	    protocol_id = evidence.get("protocol_id")
   790	    bindings = evidence.get("bindings")
   791	    capture = evidence.get(CAPTURE_TIME_FIELD)
   792	    if (
   793	        protocol_id not in {PROTOCOL_V2_ID, PROTOCOL_ID}
   794	        or evidence.get("schema_version") != "joulewise.instrument_evidence.v1"
   795	        or manifest.get("protocol_id") != protocol_id
   796	        or manifest.get("pulse_count") != protocol_pulse_count(str(protocol_id))
   797	        or not isinstance(bindings, Mapping)
   798	        or any(bindings.get(field) in (None, "") for field in V2_BINDING_FIELDS)
   799	        or not _binding_evidence_authentic(evidence, bindings)
   800	        or bindings.get("pulse_protocol_id") != protocol_id
   801	        or bindings.get("protocol_sha256") != protocol_sha256(str(protocol_id))
   802	        or evidence.get("pulse_count") != protocol_pulse_count(str(protocol_id))
   803	        or evidence.get("anchor_method_version")
   804	        != "powermetrics_native_second_censored_intersection_v1"
   805	        or evidence.get("residual_region_method") != RESIDUAL_REGION_METHOD
   806	        or not isinstance(
   807	            evidence.get("residual_region_coverage_assumption"), str
   808	        )
   809	        or not evidence.get("residual_region_coverage_assumption")
   810	        or evidence.get("residual_region_coverage_resolution_s")
   811	        != REGION_COVERAGE_RESOLUTION_S
   812	        or evidence.get("max_age_s") != MAX_AGE_S
   813	        or isinstance(capture, bool)
   814	        or not isinstance(capture, int | float)
   815	        or not math.isfinite(float(capture))
   816	        or float(capture) < 0.0
   817	    ):
   818	        return None
   819	    artifact_hashes = evidence.get("artifact_sha256")
   820	    if (
   821	        not isinstance(artifact_hashes, Mapping)
   822	        or artifact_hashes.get("events.jsonl")
   823	        != hashlib.sha256(events_raw).hexdigest()
   824	        or artifact_hashes.get("raw/powermetrics.plist")
   825	        != hashlib.sha256(powermetrics_raw).hexdigest()
   826	    ):
   827	        return None
   828	    try:
   829	        authenticated_capture = capture_wall_time_from_events(events_raw)
   830	        effective_bound = verify_stored_evidence_physics(
   831	            evidence, powermetrics_raw, events_raw
   832	        )
   833	    except (KeyError, TypeError, ValueError):
   834	        return None
   835	    if abs(float(capture) - authenticated_capture) > 1.0:
   836	        return None
   837	    try:
   838	        decimal_evidence = json.loads(
   839	            evidence_raw,
   840	            parse_float=str,
   841	            parse_int=str,
   842	        )
   843	    except (UnicodeDecodeError, json.JSONDecodeError):
   844	        return None
   845	    stored_lexeme = (
   846	        decimal_evidence.get("b_fiducial_s")
   847	        if isinstance(decimal_evidence, Mapping)
   848	        else None
   849	    )
   850	    stored_decimal = _decimal(stored_lexeme)
   851	    if (
   852	        stored_decimal is not None
   853	        and float(stored_decimal) == float(effective_bound)
   854	    ):
   855	        effective_bound_lexeme = stored_lexeme
   856	    else:
   857	        # A physical re-fit can widen beyond the stored scalar. Its returned
   858	        # representation becomes the re-derivation source lexeme; no later
   859	        # acceptance comparison converts that value through binary64 again.
   860	        effective_bound_lexeme = str(float(effective_bound))
   861	    return CalibrationCandidate(
   862	        relative_path=relative,
   863	        manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
   864	        evidence_sha256=hashlib.sha256(evidence_raw).hexdigest(),
   865	        protocol_id=str(protocol_id),
   866	        capture_wall_time_s=float(capture),
   867	        b_fiducial_s=effective_bound_lexeme,
   868	        bindings=dict(bindings),
   869	    )
   870	
   871	
   872	def _candidate_from_observation(
   873	    observation: LedgerObservation,
   874	) -> CalibrationCandidate | None:
   875	    """Authenticate one valid ledger observation from its custody locator."""
   876	
   877	    if observation.disposition != "valid" or observation.content_id is None:
   878	        return None
   879	    custody = Path(observation.custody_locator)
   880	    candidate = load_calibration_candidate(
   881	        custody,
   882	        runs_root=custody.parent.parent,
   883	    )
   884	    if candidate is None:
   885	        return None
   886	    bound = _candidate_decimal(candidate)
   887	    receipt_bound = _decimal(observation.exact_bound_lexeme_s)
   888	    try:
   889	        receipt_capture = float(observation.capture_wall_time_s)
   890	    except (TypeError, ValueError):
   891	        return None
   892	    if (
   893	        candidate.manifest_sha256
   894	        != observation.artifact_sha256.get("manifest.json")
   895	        or candidate.evidence_sha256
   896	        != observation.artifact_sha256.get("instrument_evidence.json")
   897	        or content_id_from_artifact_hashes(observation.artifact_sha256)
   898	        != observation.content_id
   899	        or bound is None
   900	        or receipt_bound is None
   901	        or bound != receipt_bound
   902	        or candidate.capture_wall_time_s != receipt_capture
   903	        or any(
   904	            candidate.bindings.get(field) != observation.t1_bindings.get(field)
   905	            for field in V2_BINDING_FIELDS
   906	        )
   907	        or any(
   908	            candidate.bindings.get(field) != observation.identity_epoch.get(field)
   909	            for field in ACCEPTANCE_IDENTITY_FIELDS
   910	        )
   911	    ):
   912	        return None
   913	    return replace(
   914	        candidate,
   915	        relative_path=observation.custody_locator,
   916	        attempt_id=observation.attempt_id,
   917	        content_id=observation.content_id,
   918	        ledger_receipt_digest=observation.receipt_digest,
   919	        bracket_session_id=observation.bracket_session_id,
   920	        bracket_slot=observation.bracket_slot,
   921	        bracket_window_id=observation.bracket_window_id,
   922	        bracket_plan_id=observation.bracket_plan_id,
   923	        bracket_plan_sha256=observation.bracket_plan_sha256,
   924	        bracket_evidence_root_id=observation.bracket_evidence_root_id,
   925	        bracket_runs_root=observation.bracket_runs_root,
   926	    )
   927	
   928	
   929	def discover_calibration_candidates(
   930	    ledger_snapshot: CalibrationLedgerSnapshot,
  1190	            "observed_triggers": [],
  1191	        },
  1192	        "numeric_semantics": {
  1193	            "comparisons": "decimal",
  1194	            "reducer_boundary": "binary64_recorded_below",
  1195	        },
  1196	        "ledger_snapshot": {
  1197	            "ledger_schema": ledger_snapshot.ledger_schema,
  1198	            "sequence": ledger_snapshot.head_sequence,
  1199	            "head_digest": ledger_snapshot.head_digest,
  1200	            "baseline_sequence": ledger_snapshot.baseline_sequence,
  1201	            "baseline_digest": ledger_snapshot.baseline_digest,
  1202	            "load_count": 1,
  1203	        },
  1204	        "preflight": None,
  1205	        "drift": None,
  1206	    }
  1207	    if stale_fields:
  1208	        return result, ("calibration_acceptance_bound_stale",)
  1209	    observations_by_attempt = ledger_snapshot.observation_by_attempt
  1210	    finalized_session_ids = {
  1211	        session.session_id
  1212	        for session in ledger_snapshot.bracket_sessions
  1213	        if session.state == "finalized"
  1214	    }
  1215	    registered_valid = {
  1216	        (
  1217	            observation.attempt_id,
  1218	            observation.content_id,
  1219	            observation.receipt_digest,
  1220	        )
  1221	        for observation in ledger_snapshot.observations
  1222	        if observation.disposition == "valid"
  1223	        and not observation.is_historical_import
  1224	        and (
  1225	            observation.bracket_session_id is None
  1226	            or observation.bracket_session_id in finalized_session_ids
  1227	        )
  1228	    }
  1229	    supplied_valid = {
  1230	        (
  1231	            candidate.attempt_id,
  1232	            candidate.content_id,
  1233	            candidate.ledger_receipt_digest,
  1234	        )
  1235	        for candidate in candidates
  1236	    }
  1237	    # Even the low-level evaluator requires the complete ledger enumeration.
  1238	    # This prevents a caller from narrowing the registered universe to a
  1239	    # favorable subset while still passing per-candidate membership checks.
  1240	    if supplied_valid != registered_valid or len(candidates) != len(supplied_valid):
  1241	        return result, ("calibration_ledger_off_ledger_artifact",)
  1242	    for candidate in candidates:
  1243	        observation = (
  1244	            observations_by_attempt.get(candidate.attempt_id)
  1245	            if isinstance(candidate.attempt_id, str)
  1246	            else None
  1247	        )
  1248	        if (
  1249	            observation is None
  1250	            or observation.disposition != "valid"
  1251	            or candidate.content_id != observation.content_id
  1252	            or candidate.ledger_receipt_digest != observation.receipt_digest
  1253	            or candidate.manifest_sha256
  1254	            != observation.artifact_sha256.get("manifest.json")
  1255	            or candidate.evidence_sha256
  1256	            != observation.artifact_sha256.get("instrument_evidence.json")
  1257	            or candidate.bracket_session_id != observation.bracket_session_id
  1258	            or candidate.bracket_slot != observation.bracket_slot
  1259	            or candidate.bracket_window_id != observation.bracket_window_id
  1260	            or candidate.bracket_plan_id != observation.bracket_plan_id
  1261	            or candidate.bracket_plan_sha256
  1262	            != observation.bracket_plan_sha256
  1263	            or candidate.bracket_evidence_root_id
  1264	            != observation.bracket_evidence_root_id
  1265	            or candidate.bracket_runs_root != observation.bracket_runs_root
  1266	        ):
  1267	            return result, ("calibration_ledger_off_ledger_artifact",)
  1268	    has_session_candidates = any(
  1269	        candidate.bracket_session_id is not None for candidate in candidates
  1270	    )
  1271	    bound_observations: tuple[LedgerObservation, LedgerObservation] | None = None
  1272	    if has_session_candidates:
  1273	        if (
  1274	            bracket_binding is None
  1275	            or not all(
  1276	                isinstance(value, str) and bool(value)
  1277	                for value in (
  1278	                    bracket_window_id,
  1279	                    bracket_plan_id,
  1280	                    bracket_plan_sha256,
  1281	                    bracket_evidence_root_id,
  1282	                )
  1283	            )
  1284	            or bracket_runs_root is None
  1285	        ):
  1286	            return result, ("calibration_bracket_binding_missing",)
  1287	        expected_runs_root = str(Path(bracket_runs_root).absolute())
  1288	        bound_observations = validate_calibration_bracket_binding(
  1289	            bracket_binding,
  1290	            ledger_snapshot,
  1291	            window_id=bracket_window_id,
  1292	            plan_id=bracket_plan_id,
  1293	            plan_sha256=bracket_plan_sha256,
  1294	            evidence_root_id=bracket_evidence_root_id,
  1295	            runs_root=expected_runs_root,
  1296	        )
  1297	        if bound_observations is None:
  1298	            return result, ("calibration_bracket_binding_invalid",)
  1299	        result["bracket_binding"] = {
  1300	            "schema_version": BRACKET_BINDING_SCHEMA,
  1301	            "binding_digest": bracket_binding["binding_digest"],
  1302	            "session_id": bracket_binding["session_id"],
  1303	            "window_id": bracket_binding["window_id"],
  1304	            "plan_id": bracket_binding["plan_id"],
  1305	            "plan_sha256": bracket_binding["plan_sha256"],
  1306	            "evidence_root_id": bracket_binding["evidence_root_id"],
  1307	            "runs_root": bracket_binding["runs_root"],
  1308	        }
  1309	        bound_session_id = str(bracket_binding["session_id"])
  1310	        for candidate in candidates:
  1311	            if candidate.bracket_session_id != bound_session_id:
  1312	                continue
  1313	            if (
  1314	                candidate.bracket_window_id,
  1315	                candidate.bracket_plan_id,
  1316	                candidate.bracket_plan_sha256,
  1317	                candidate.bracket_evidence_root_id,
  1318	                candidate.bracket_runs_root,
  1319	            ) != (
  1320	                bracket_window_id,
  1321	                bracket_plan_id,
  1322	                bracket_plan_sha256,
  1323	                bracket_evidence_root_id,
  1324	                expected_runs_root,
  1325	            ):
  1326	                return result, ("calibration_bracket_binding_invalid",)
  1327	    # v2 remains an authenticated validation/reduction artifact, but only the
  1328	    # 59-pulse v3 protocol carries the governed 95/95 claim calibration.
  1329	    matching = [
  1330	        candidate

exec
/bin/zsh -lc "nl -ba joulewise/calibration_bracketing.py | sed -n '500,705p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
   500	    )
   501	
   502	
   503	def _valid_sha256(value: Any) -> bool:
   504	    return (
   505	        isinstance(value, str)
   506	        and len(value) == 64
   507	        and all(char in "0123456789abcdef" for char in value)
   508	    )
   509	
   510	
   511	_BRACKET_BINDING_KEYS = {
   512	    "schema_version",
   513	    "ledger_schema",
   514	    "session_id",
   515	    "window_id",
   516	    "plan_id",
   517	    "plan_sha256",
   518	    "evidence_root_id",
   519	    "runs_root",
   520	    "capability_receipt_digest",
   521	    "terminal_head",
   522	    "endpoints",
   523	    "binding_digest",
   524	}
   525	_BRACKET_ENDPOINT_KEYS = {
   526	    "attempt_id",
   527	    "receipt_digest",
   528	    "content_digest",
   529	}
   530	
   531	
   532	def _binding_core(binding: Mapping[str, Any]) -> dict[str, Any]:
   533	    return {key: value for key, value in binding.items() if key != "binding_digest"}
   534	
   535	
   536	def build_calibration_bracket_binding(
   537	    ledger_snapshot: CalibrationLedgerSnapshot,
   538	    *,
   539	    session_id: str,
   540	    window_id: str,
   541	    plan_id: str,
   542	    plan_sha256: str,
   543	    evidence_root_id: str,
   544	    runs_root: Path | str,
   545	) -> dict[str, Any]:
   546	    """Bind one frozen window to its exact finalized session endpoints."""
   547	
   548	    if not isinstance(ledger_snapshot, CalibrationLedgerSnapshot) or not ledger_snapshot.valid:
   549	        raise ValueError("bracket binding requires a valid pinned ledger snapshot")
   550	    session = ledger_snapshot.bracket_session_by_id.get(session_id)
   551	    expected_identity = (
   552	        window_id,
   553	        plan_id,
   554	        plan_sha256,
   555	        evidence_root_id,
   556	        str(Path(runs_root).absolute()),
   557	    )
   558	    if (
   559	        session is None
   560	        or session.state != "finalized"
   561	        or (
   562	            session.window_id,
   563	            session.plan_id,
   564	            session.plan_sha256,
   565	            session.evidence_root_id,
   566	            session.runs_root,
   567	        )
   568	        != expected_identity
   569	    ):
   570	        raise ValueError("bracket session does not match the frozen window identity")
   571	    pre = session.finalized_slots.get("pre")
   572	    post = session.finalized_slots.get("post")
   573	    if (
   574	        pre is None
   575	        or post is None
   576	        or pre.disposition != "valid"
   577	        or post.disposition != "valid"
   578	        or pre.content_id is None
   579	        or post.content_id is None
   580	        or post.sequence != ledger_snapshot.head_sequence
   581	        or post.receipt_digest != ledger_snapshot.head_digest
   582	    ):
   583	        raise ValueError("bracket session endpoints are not valid at the terminal head")
   584	    binding: dict[str, Any] = {
   585	        "schema_version": BRACKET_BINDING_SCHEMA,
   586	        "ledger_schema": LEDGER_SCHEMA,
   587	        "session_id": session.session_id,
   588	        "window_id": session.window_id,
   589	        "plan_id": session.plan_id,
   590	        "plan_sha256": session.plan_sha256,
   591	        "evidence_root_id": session.evidence_root_id,
   592	        "runs_root": session.runs_root,
   593	        "capability_receipt_digest": session.capability_receipt_digest,
   594	        "terminal_head": {
   595	            "sequence": post.sequence,
   596	            "head_digest": post.receipt_digest,
   597	            "ledger_schema": LEDGER_SCHEMA,
   598	        },
   599	        "endpoints": {
   600	            role: {
   601	                "attempt_id": observation.attempt_id,
   602	                "receipt_digest": observation.receipt_digest,
   603	                "content_digest": observation.content_id,
   604	            }
   605	            for role, observation in (("pre", pre), ("post", post))
   606	        },
   607	    }
   608	    binding["binding_digest"] = _canonical_sha256(binding)
   609	    return binding
   610	
   611	
   612	def validate_calibration_bracket_binding(
   613	    binding: Mapping[str, Any],
   614	    ledger_snapshot: CalibrationLedgerSnapshot,
   615	    *,
   616	    window_id: str | None = None,
   617	    plan_id: str | None = None,
   618	    plan_sha256: str | None = None,
   619	    evidence_root_id: str | None = None,
   620	    runs_root: Path | str | None = None,
   621	) -> tuple[LedgerObservation, LedgerObservation] | None:
   622	    """Return the exact authenticated pair, or ``None`` on any substitution."""
   623	
   624	    if (
   625	        not isinstance(binding, Mapping)
   626	        or set(binding) != _BRACKET_BINDING_KEYS
   627	        or binding.get("schema_version") != BRACKET_BINDING_SCHEMA
   628	        or binding.get("ledger_schema") != LEDGER_SCHEMA
   629	        or not _valid_sha256(binding.get("plan_sha256"))
   630	        or not _valid_sha256(binding.get("capability_receipt_digest"))
   631	        or not _valid_sha256(binding.get("binding_digest"))
   632	        or binding.get("binding_digest") != _canonical_sha256(_binding_core(binding))
   633	        or not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
   634	        or not ledger_snapshot.valid
   635	    ):
   636	        return None
   637	    if any(
   638	        not isinstance(value, str) or not value
   639	        for value in (window_id, plan_id, plan_sha256, evidence_root_id)
   640	    ) or runs_root is None:
   641	        return None
   642	    expected_runs_root = str(Path(runs_root).absolute())
   643	    for field, expected in (
   644	        ("window_id", window_id),
   645	        ("plan_id", plan_id),
   646	        ("plan_sha256", plan_sha256),
   647	        ("evidence_root_id", evidence_root_id),
   648	        ("runs_root", expected_runs_root),
   649	    ):
   650	        if binding.get(field) != expected:
   651	            return None
   652	    session = ledger_snapshot.bracket_session_by_id.get(str(binding.get("session_id")))
   653	    if (
   654	        session is None
   655	        or session.state != "finalized"
   656	        or binding.get("window_id") != session.window_id
   657	        or binding.get("plan_id") != session.plan_id
   658	        or binding.get("plan_sha256") != session.plan_sha256
   659	        or binding.get("evidence_root_id") != session.evidence_root_id
   660	        or binding.get("runs_root") != session.runs_root
   661	        or binding.get("capability_receipt_digest")
   662	        != session.capability_receipt_digest
   663	    ):
   664	        return None
   665	    terminal = binding.get("terminal_head")
   666	    endpoints = binding.get("endpoints")
   667	    if (
   668	        not isinstance(terminal, Mapping)
   669	        or set(terminal) != {"sequence", "head_digest", "ledger_schema"}
   670	        or terminal.get("ledger_schema") != LEDGER_SCHEMA
   671	        or isinstance(terminal.get("sequence"), bool)
   672	        or not isinstance(terminal.get("sequence"), int)
   673	        or not _valid_sha256(terminal.get("head_digest"))
   674	        or not isinstance(endpoints, Mapping)
   675	        or set(endpoints) != {"pre", "post"}
   676	    ):
   677	        return None
   678	    resolved: list[LedgerObservation] = []
   679	    for role in ("pre", "post"):
   680	        endpoint = endpoints.get(role)
   681	        observation = session.finalized_slots.get(role)
   682	        if (
   683	            not isinstance(endpoint, Mapping)
   684	            or set(endpoint) != _BRACKET_ENDPOINT_KEYS
   685	            or observation is None
   686	            or observation.disposition != "valid"
   687	            or observation.content_id is None
   688	            or endpoint.get("attempt_id") != observation.attempt_id
   689	            or endpoint.get("receipt_digest") != observation.receipt_digest
   690	            or endpoint.get("content_digest") != observation.content_id
   691	        ):
   692	            return None
   693	        resolved.append(observation)
   694	    post = resolved[1]
   695	    if (
   696	        terminal.get("sequence") != post.sequence
   697	        or terminal.get("head_digest") != post.receipt_digest
   698	        or post.sequence > len(ledger_snapshot.receipts)
   699	        or ledger_snapshot.receipts[post.sequence - 1].get("receipt_digest")
   700	        != post.receipt_digest
   701	    ):
   702	        return None
   703	    return resolved[0], resolved[1]
   704	
   705	

exec
/bin/zsh -lc 'BASE=$(git merge-base HEAD origin/main); printf '"'%s\\n' \""'$BASE"; git diff --name-status "$BASE"..origin/main | head -200; git diff --name-only "$BASE"..origin/main | rg '"'"'^(joulewise|scripts|tests)/'"' || true; git merge-tree \""'$BASE" HEAD origin/main | rg -n '"'"'^(changed in both|CONFLICT|<<<<<<<|=======|>>>>>>>|added in both|removed in)'"' || true" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 29ms:
codex
The U1 branch has advanced by one recovery-only commit after U4’s base. There are no textual conflicts and none of U4’s imported interfaces changed; I’m also executing U4 against that newer U1 module in memory to verify the merge-order claim rather than relying only on the diff.
exec
/bin/zsh -lc "python3 - <<'PY'
import importlib.util
import pathlib
import subprocess
import sys
import types
import unittest
name = \"joulewise.calibration_ledger\"
path = pathlib.Path(\"joulewise/calibration_ledger.py\")
source = subprocess.run(
    [\"git\", \"show\", \"origin/impl/d117-u1-ledger-session:joulewise/calibration_ledger.py\"],
    check=True,
    capture_output=True,
    text=True,
).stdout
module = types.ModuleType(name)
module.__file__ = str(path.resolve())
module.__package__ = \"joulewise\"
module.__spec__ = importlib.util.spec_from_file_location(name, path)
sys.modules[name] = module
exec(compile(source, str(path), \"exec\"), module.__dict__)
suite = unittest.defaultTestLoader.loadTestsFromName(\"tests.test_calibration_live_three_window\")
result = unittest.TextTestRunner(verbosity=1).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 609ms:
...s.........s........s
----------------------------------------------------------------------
Ran 23 tests in 0.626s

OK (skipped=3)

exec
/bin/zsh -lc "git show origin/main:docs/process_traces/2026-08-07-d117-u-units/U1-DELTA-VERDICT.md | sed -n '1,320p' && git show origin/main:docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md | sed -n '1,320p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: high
reasoning summaries: none
session id: 019fdd9a-1425-7992-ad27-791f78697b68
--------
user
Your previous final message was blocked by a content filter. Re-emit the delta re-audit CONCLUSIONS ONLY, from work already done — do not redo any analysis, do not quote code, do not include probe scripts or attack phrasing. Neutral engineering language. Format: (1) closure table FIX-1..FIX-8, each CLOSED/PARTIAL/NOT-CLOSED with one plain sentence of evidence; (2) any newly introduced defects found, by severity, one plain sentence each with file:line; (3) same-signature statement: does any original defect class survive in a new form — yes/no per class; (4) checks-performed line. Nothing else.
codex
### 1. Closure table

| Fix | Status | Evidence |
|---|---|---|
| FIX-1 | CLOSED | Cross-root L5 borrowing was refused through mandatory window, plan, evidence-root, and `runs_root` matching. |
| FIX-2 | CLOSED | A finalized systematic-invalid PRE from an aborted session remained in the observation universe and activated the preflight-screen freshness trigger. |
| FIX-3 | CLOSED | Generic head-pin generation refused both session-open and PRE-finalization receipts. |
| FIX-4 | CLOSED | Concurrent begins accepted exactly one claimant, and the rejected lifecycle could not abort the accepted writer’s session. |
| FIX-5 | CLOSED | Neither open-session nor aborted-session observations appeared in candidate discovery. |
| FIX-6 | PARTIAL | The specified single torn-tail recovery succeeded, but an additional interruption after recovery evidence is written can leave subsequent recovery permanently conflicting. |
| FIX-7 | CLOSED | Crash closure uses a real subprocess exit, reservation ordering is behaviorally checked, and committed-pin rollback has a session-loader regression. |
| FIX-8 | CLOSED | Malformed reservation input received the same refusal in dry-run and execute modes. |

### 2. Newly introduced defects

- BLOCKER — [joulewise/calibration_ledger.py:2320](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:2320): if recovery completes a partial append and records evidence but stops before journal clearing at line 2372, the next recovery computes different evidence counters, reports `append recovery evidence conflicts`, and cannot complete governed closure.

### 3. Same-signature statement

- L5 cross-window borrowing: NO.
- Aborted-observation universe deletion: NO.
- Mid-window pin escape: NO.
- Concurrent double-arm: NO.
- Nonterminal candidate leakage: NO.
- Torn-tail unrecoverability: YES — the class survives at a later recovery boundary.
- Non-discriminating crash/rollback coverage: NO.
- Dry-run/execute validation divergence: NO.

### 4. Checks performed

Eight mandated focused scenarios passed; D-116 issued-prefix replay remained byte-identical at SHA-256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f` with sequence 76 and no refusal reasons; read-only consumer-path review and the additional recovery-boundary subprocess check reproduced the blocker above.
tokens used
342,841
### 1. Closure table

| Fix | Status | Evidence |
|---|---|---|
| FIX-1 | CLOSED | Cross-root L5 borrowing was refused through mandatory window, plan, evidence-root, and `runs_root` matching. |
| FIX-2 | CLOSED | A finalized systematic-invalid PRE from an aborted session remained in the observation universe and activated the preflight-screen freshness trigger. |
| FIX-3 | CLOSED | Generic head-pin generation refused both session-open and PRE-finalization receipts. |
| FIX-4 | CLOSED | Concurrent begins accepted exactly one claimant, and the rejected lifecycle could not abort the accepted writer’s session. |
| FIX-5 | CLOSED | Neither open-session nor aborted-session observations appeared in candidate discovery. |
| FIX-6 | PARTIAL | The specified single torn-tail recovery succeeded, but an additional interruption after recovery evidence is written can leave subsequent recovery permanently conflicting. |
| FIX-7 | CLOSED | Crash closure uses a real subprocess exit, reservation ordering is behaviorally checked, and committed-pin rollback has a session-loader regression. |
| FIX-8 | CLOSED | Malformed reservation input received the same refusal in dry-run and execute modes. |

### 2. Newly introduced defects

- BLOCKER — [joulewise/calibration_ledger.py:2320](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:2320): if recovery completes a partial append and records evidence but stops before journal clearing at line 2372, the next recovery computes different evidence counters, reports `append recovery evidence conflicts`, and cannot complete governed closure.

### 3. Same-signature statement

- L5 cross-window borrowing: NO.
- Aborted-observation universe deletion: NO.
- Mid-window pin escape: NO.
- Concurrent double-arm: NO.
- Nonterminal candidate leakage: NO.
- Torn-tail unrecoverability: YES — the class survives at a later recovery boundary.
- Non-discriminating crash/rollback coverage: NO.
- Dry-run/execute validation divergence: NO.

### 4. Checks performed

Eight mandated focused scenarios passed; D-116 issued-prefix replay remained byte-identical at SHA-256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f` with sequence 76 and no refusal reasons; read-only consumer-path review and the additional recovery-boundary subprocess check reproduced the blocker above.

---
MAGISTRATE NOTES (2026-08-07): (1) The delta session's original full report was
blocked by a Sol-side content classifier (adversarial-audit vocabulary false
positive — the codex-delegation §Security class, first observed on OUTPUT);
recovered via resume with a neutral-language re-emission; the truncated original
is in the session scratchpad only. (2) FIX-1..5,7,8 CLOSED; D-116 issued-prefix
replay byte-identical. (3) FIX-6 PARTIAL + introduced BLOCKER at the recovery
boundary → FIX-6b launched with a lead-pinned idempotent-recovery shape.
STOP-CONDITION (binding): if the next delta finds the torn-tail/recovery class
again, the next spend is a rule-11 consult — no round three.
Reading additional input from stdin...
OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: xhigh
reasoning summaries: none
session id: 019fddc4-9db0-7c70-bc6f-d1900f9de9af
--------
user
DELTA RE-AUDIT of FIX-6b (read-only; write no files; FINAL MESSAGE in neutral engineering language — conclusions only, no code quotes beyond file:line, no attack phrasing). Branch impl/d117-u1-ledger-session at HEAD. The prior delta found FIX-6 PARTIAL with one introduced blocker: if append recovery completed a partial append and wrote recovery evidence but stopped before journal clearing, the next recovery computed different evidence counters, reported an evidence conflict, and governed closure was permanently blocked. FIX-6b implemented a lead-pinned idempotent shape: evidence derived deterministically from the journal record and ledger tail alone; matching recomputation resumes to journal clearing; genuine mismatch still refuses.
CHARGE: (1) verify FIX-6b closes it — re-run the crash-after-evidence-before-clear scenario via subprocess and confirm full governed closure on the next recovery; confirm the genuine-mismatch case still refuses; confirm the original torn-tail regression still passes. (2) Hunt NEW recovery-boundary states the fix opens: crash DURING journal clearing; crash after clearing but before the next append; two concurrent recoveries; a journal record whose target bytes were already fully appended; a journal that survives from an earlier unrelated append. (3) Re-verify the D-116 issued-prefix replay is byte-identical (SHA aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f, sequence 76). (4) SAME-SIGNATURE STATEMENT, explicit: does the torn-tail/recovery-boundary class survive in ANY form — yes/no. A YES fires an escalation trigger (the next spend is a design consult, not another fix round), so answer it precisely and support it. Report the focused ledger suite tail; CLEAN needs a checks-performed line.
codex
I’ll perform the audit read-only, using temporary directories for crash simulations and disabling bytecode writes. I’ll first establish the branch/state and governing D-116/D-117 contracts, then run the focused recovery scenarios and issued-prefix hash check.
  → Inspect repository state and governing D-116/D-117 contracts
  • Trace FIX-6b recovery implementation and existing focused tests
  • Run subprocess crash and recovery-boundary scenarios
  • Verify D-116 issued-prefix replay hash and sequence
  • Run focused ledger suite and report conclusions
exec
/bin/zsh -lc 'git status --short --branch && rg -n "ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next" RUN_STATE.md && rg -n "Current Queue|Do-Not-Do-Yet|D-116|D-117|FIX-6" TASK_QUEUE.md && rg -n "Mission M0|D-116|D-117|FIX-6|ledger|recovery" docs/agent_playbook.md docs/orchestration.md AGENT_PLAN.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
## impl/d117-u1-ledger-session...origin/impl/d117-u1-ledger-session
2008:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
2043:## ACTIVE_STOP_CARD
2182:## Current Project Status
2743:## Known Workspace State
96:Current Queue region is the sole live work-selection view.
213:## Current Do-Not-Do-Yet List
306:## Current Queue
docs/orchestration.md:151:| `docs/stream_logs/` | Per-stream decision ledgers, committed WITH the code they justify: every non-trivial in-stream decision (`A-1..A-30`, `B-1..B-46`, …) with mandatory evidence pointers; wrong pins are SUPERSEDED in place, never erased. |
docs/orchestration.md:152:| `docs/run_reports/` | One record per working session: outcomes, verification evidence, a per-layer catch/yield table, the delegation-calibration ledger, restart instructions. |
docs/orchestration.md:158:Instrumentation ledgers close the loop on the process itself:
docs/orchestration.md:283:better ones (now the v2 ledger and calibration formats), and review
docs/orchestration.md:319:  receipt anchoring, and recovery primitives are defined only in
docs/orchestration.md:331:  `docs/run_reports/` provide live templates for ledgers and trace
docs/agent_playbook.md:26:1. Run Mission M0 (preflight) — always.
docs/agent_playbook.md:50:## Mission M0: Preflight (every session)

exec
/bin/zsh -lc "sed -n '50,118p' docs/agent_playbook.md
sed -n '1,380p' docs/orchestration.md
sed -n '2040,2225p' RUN_STATE.md
sed -n '2740,2845p' RUN_STATE.md
sed -n '200,370p' TASK_QUEUE.md
sed -n '1,240p' AGENT_PLAN.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
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

exec
/bin/zsh -lc 'git show origin/main:docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md | tail -120' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
   527	        self.assertTrue(journal_path.exists())
   528	        evidence_path = calibration_ledger._append_recovery_path(
   529	            self.ledger, journal["operation_id"]
   530	        )
   531	        evidence_before_retry = evidence_path.read_bytes()
   532	        evidence = json.loads(evidence_before_retry)
   533	        self.assertEqual(
   534	            evidence["observed_suffix_bytes"],
   535	            len(journal["payload"].encode("utf-8")),
   536	        )
   537	        self.assertEqual(evidence["recovered_bytes"], 0)
   538	
   539	        retried = self._abort_session_in_subprocess(kill_before_clear=False)
   540	        self.assertEqual(retried.returncode, 0, retried.stderr.decode())
   541	        self.assertFalse(journal_path.exists())
   542	        self.assertEqual(evidence_path.read_bytes(), evidence_before_retry)
   543	
   544	        self._write_pin(
   545	            terminal_head_pin_for_session(
   546	                self.ledger, session_id="session-alpha"
   547	            )
   548	        )
   549	        recovered = self._snapshot()
   550	        self.assertEqual(recovered.refusal_reasons, ())
   551	        self.assertEqual(recovered.bracket_sessions[0].state, "aborted")
   552	        self.assertEqual(
   553	            recovered.observations[0].disposition,
   554	            "systematic-invalid",
   555	        )
   556	
   557	    def test_recovery_refuses_conflicting_existing_evidence(self) -> None:
   558	        journal = self._create_torn_session_finalization()
   559	        killed = self._abort_session_in_subprocess(kill_before_clear=True)
   560	        self.assertEqual(killed.returncode, -signal.SIGKILL)
   561	        journal_path = calibration_ledger._append_journal_path(self.ledger)
   562	        evidence_path = calibration_ledger._append_recovery_path(
   563	            self.ledger, journal["operation_id"]
   564	        )
   565	        evidence = json.loads(evidence_path.read_bytes())
   566	        evidence["recovered_bytes"] = 1
   567	        mismatched = canonical_json_bytes(evidence) + b"\n"
   568	        evidence_path.write_bytes(mismatched)
   569	        ledger_before_retry = self.ledger.read_bytes()
   570	
   571	        with self.assertRaisesRegex(
   572	            CalibrationLedgerError, "append recovery evidence conflicts"
   573	        ):
   574	            abort_bracket_session(
   575	                self.ledger,
   576	                session_id="session-alpha",
   577	                reason="recover_torn_systematic_pre",
   578	            )
   579	        self.assertTrue(journal_path.exists())
   580	        self.assertEqual(self.ledger.read_bytes(), ledger_before_retry)
   581	        self.assertEqual(evidence_path.read_bytes(), mismatched)
   582	
  7489	## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)
  7490	
  7491	**Date:** 2026-08-06 (Fable magistrate, overnight; issuance pre-authorized by Ed 2026-08-05 conditional on the gate passing).
  7492	**Status:** EXECUTED. This retires the schema fixture and issues the authoritative calibration acceptance artifact — the anchor all future floor-mint claims authenticate against. D-110 re-mint condition (b) ("R2 backfill verified, ledger bootstrapped, head pinned") is now SATISFIED; (a) was satisfied by PR #100, (c) by PR #105. **MINT-GENERALIZE-01 is UNBLOCKED for the re-mint.**
  7493	
  7494	**What was written.**
  7495	- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis historical-import chain (git-ignored local custody artifact, sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`; deterministic from the custodied inputs below + the raw evidence; MUST be backed up per the runbook before the re-mint consumes it).
  7496	- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
  7497	- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
  7498	- Reproducibility inputs custodied at `docs/process_traces/2026-08-06-d079-issuance-coldgate/` (disposition table sha `5da820aa…`, custody manifest sha `99cbf3df…`, execute summary, ledger sha).
  7499	
  7500	**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).

All requested checks completed at clean HEAD; no repository files changed.
  ✓ Inspect repository state and governing D-116/D-117 contracts
  ✓ Trace FIX-6b recovery implementation and existing focused tests
  ✓ Run subprocess crash and recovery-boundary scenarios
  ✓ Verify D-116 issued-prefix replay hash and sequence
  ✓ Run focused ledger suite and report conclusions
codex
## Delta re-audit: CLEAN

At `1cf7a42048a5bfe3841b699c430bf6ebc7cd0664`, FIX-6b closes the prior blocker.

- Crash after recovery evidence but before journal clearing: next recovery matched the existing evidence, cleared the journal, completed governed abort, authenticated the terminal pin, and produced no refusal reasons. [calibration_ledger.py:2302](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:2302)
- Genuine evidence mismatch still refuses while preserving the ledger, journal, and mismatched evidence. [test_calibration_ledger.py:557](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/tests/test_calibration_ledger.py:557)
- Original torn-tail recovery passes through governed abort and clean authenticated closure. [test_calibration_ledger.py:384](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/tests/test_calibration_ledger.py:384)

Recovery-boundary results:

- Crash during clearing, after unlink but before directory fsync: retry closed successfully.
- Crash after clearing but before the requested append: retry closed successfully.
- Two concurrent recoveries: one completed; the serialized second process refused the already-terminal session. One evidence object remained and the journal was cleared.
- Fully appended journal target: recovery recognized the complete target, emitted deterministic evidence with zero recovered bytes, cleared the journal, and preserved the terminal closure.
- Journal from an earlier append followed by unrelated bytes: refused without mutation as a genuine journal/ledger mismatch.

D-116 replay was byte-identical: SHA-256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`, 76 receipts, terminal sequence 76, terminal digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`.

Same-signature statement: **NO — the torn-tail/recovery-boundary defect class does not survive in any tested legitimate recovery state.** The stale unrelated-journal case is a genuine mismatch and correctly remains fail-closed.

Checks performed: three named recovery regressions passed; five additional subprocess boundary scenarios passed; D-116 deterministic replay matched; focused ledger suite tail: `Ran 48 tests in 9.765s` / `OK`. Workspace remained clean; no files were written.
tokens used
162,380
## Delta re-audit: CLEAN

At `1cf7a42048a5bfe3841b699c430bf6ebc7cd0664`, FIX-6b closes the prior blocker.

- Crash after recovery evidence but before journal clearing: next recovery matched the existing evidence, cleared the journal, completed governed abort, authenticated the terminal pin, and produced no refusal reasons. [calibration_ledger.py:2302](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:2302)
- Genuine evidence mismatch still refuses while preserving the ledger, journal, and mismatched evidence. [test_calibration_ledger.py:557](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/tests/test_calibration_ledger.py:557)
- Original torn-tail recovery passes through governed abort and clean authenticated closure. [test_calibration_ledger.py:384](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/tests/test_calibration_ledger.py:384)

Recovery-boundary results:

- Crash during clearing, after unlink but before directory fsync: retry closed successfully.
- Crash after clearing but before the requested append: retry closed successfully.
- Two concurrent recoveries: one completed; the serialized second process refused the already-terminal session. One evidence object remained and the journal was cleared.
- Fully appended journal target: recovery recognized the complete target, emitted deterministic evidence with zero recovered bytes, cleared the journal, and preserved the terminal closure.
- Journal from an earlier append followed by unrelated bytes: refused without mutation as a genuine journal/ledger mismatch.

D-116 replay was byte-identical: SHA-256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`, 76 receipts, terminal sequence 76, terminal digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`.

Same-signature statement: **NO — the torn-tail/recovery-boundary defect class does not survive in any tested legitimate recovery state.** The stale unrelated-journal case is a genuine mismatch and correctly remains fail-closed.

Checks performed: three named recovery regressions passed; five additional subprocess boundary scenarios passed; D-116 deterministic replay matched; focused ledger suite tail: `Ran 48 tests in 9.765s` / `OK`. Workspace remained clean; no files were written.

codex
The L5 check does not execute the required negative case: its no-binding arm fails because the binding is absent, while its binding arm uses beta’s correct binding and expects success. I’m confirming that weakness with an in-memory mutation that makes the evaluator trust the binding’s own `runs_root`; the named L5 test should fail if it genuinely protects the caller-to-root binding.
exec
/bin/zsh -lc "python3 - <<'PY'
import importlib.util
import pathlib
import sys
import types
import unittest
name = \"joulewise.calibration_bracketing\"
path = pathlib.Path(\"joulewise/calibration_bracketing.py\")
source = path.read_text()
needle = \"expected_runs_root = str(Path(runs_root).absolute())\"
assert source.count(needle) == 1
source = source.replace(needle, \"expected_runs_root = str(binding.get('runs_root'))\")
needle = \"expected_runs_root = str(Path(bracket_runs_root).absolute())\"
assert source.count(needle) == 1
source = source.replace(needle, \"expected_runs_root = str(bracket_binding.get('runs_root'))\")
module = types.ModuleType(name)
module.__file__ = str(path.resolve())
module.__package__ = \"joulewise\"
module.__spec__ = importlib.util.spec_from_file_location(name, path)
sys.modules[name] = module
exec(compile(source, str(path), \"exec\"), module.__dict__)
suite = unittest.defaultTestLoader.loadTestsFromName(
    \"tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding\"
)
result = unittest.TextTestRunner(verbosity=1).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 279ms:
.
----------------------------------------------------------------------
Ran 1 test in 0.306s

OK

exec
/bin/zsh -lc 'python3 -m unittest -v tests.test_calibration_live_three_window' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 554ms:
test_all_six_are_same_epoch_causal_fresh_protocol_and_t1_eligible (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_all_six_are_same_epoch_causal_fresh_protocol_and_t1_eligible) ... ok
test_alpha_beta_gamma_each_bind_only_their_own_pre_post_pair (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_alpha_beta_gamma_each_bind_only_their_own_pre_post_pair) ... ok
test_bundle_path_uses_ledger_discovery_as_candidate_authority (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_bundle_path_uses_ledger_discovery_as_candidate_authority) ... ok
test_d102_observation_count_boundary_requires_successor (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d102_observation_count_boundary_requires_successor) ... skipped 'U2 successor engine pending'
test_d110_allowance_selects_both_max_operands_across_windows (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_d110_allowance_selects_both_max_operands_across_windows) ... ok
test_each_night_issues_its_verdict_at_a_committed_closeout (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_each_night_issues_its_verdict_at_a_committed_closeout) ... ok
test_exactly_six_live_candidates_and_zero_imported_candidates (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_exactly_six_live_candidates_and_zero_imported_candidates) ... ok
test_final_closeout_replays_all_verdicts_with_complete_universe (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_final_closeout_replays_all_verdicts_with_complete_universe) ... ok
test_issuance_equivalent_base_has_76_receipts_and_30_2_6_dispositions (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_issuance_equivalent_base_has_76_receipts_and_30_2_6_dispositions) ... ok
test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding) ... ok
test_no_failure_campaign_has_36_valid_observations_two_short_of_trigger (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_no_failure_campaign_has_36_valid_observations_two_short_of_trigger) ... ok
test_no_neighboring_endpoint_can_substitute_for_a_bound_endpoint (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_no_neighboring_endpoint_can_substitute_for_a_bound_endpoint) ... ok
test_production_writer_receipts_end_at_derived_terminal_sequence (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_production_writer_receipts_end_at_derived_terminal_sequence) ... ok
test_range_expanding_live_observation_requires_successor (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_range_expanding_live_observation_requires_successor) ... skipped 'U2 successor engine pending'
test_refuses_head_pin_mismatch_rollback_fork_or_uncommitted_terminal_head (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_refuses_head_pin_mismatch_rollback_fork_or_uncommitted_terminal_head) ... ok
test_refuses_import_marker_removal_import_leakage_or_discovery_regression (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_refuses_import_marker_removal_import_leakage_or_discovery_regression) ... ok
test_refuses_missing_duplicate_reordered_or_conflicting_session_receipts (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_refuses_missing_duplicate_reordered_or_conflicting_session_receipts) ... ok
test_refuses_missing_tampered_swapped_or_cross_window_bracket_binding (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_refuses_missing_tampered_swapped_or_cross_window_bracket_binding) ... ok
test_refuses_noncausal_stale_t1_protocol_or_epoch_mismatched_endpoint (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_refuses_noncausal_stale_t1_protocol_or_epoch_mismatched_endpoint) ... ok
test_refuses_omitted_added_duplicated_off_ledger_or_substituted_observations (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_refuses_omitted_added_duplicated_off_ledger_or_substituted_observations) ... ok
test_refuses_open_or_abandoned_session_without_governed_closure (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_refuses_open_or_abandoned_session_without_governed_closure) ... ok
test_refuses_systematic_classification (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_refuses_systematic_classification) ... ok
test_successor_prior_set_refuses_omitted_or_changed_authenticated_prefix (tests.test_calibration_live_three_window.CalibrationLiveThreeWindowTests.test_successor_prior_set_refuses_omitted_or_changed_authenticated_prefix) ... skipped 'U2 successor engine pending'

----------------------------------------------------------------------
Ran 23 tests in 0.585s

OK (skipped=3)

exec
/bin/zsh -lc 'git status --short --branch && git diff --check origin/main...HEAD && git rev-parse HEAD && git rev-parse origin/impl/d117-u1-ledger-session' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
## impl/d117-u4-regression...origin/impl/d117-u4-regression
4b821807fd03690f20e91e1323ce92862f96feee
1cf7a42048a5bfe3841b699c430bf6ebc7cd0664

exec
/bin/zsh -lc "nl -ba joulewise/calibration_bracketing.py | sed -n '160,455p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4
 succeeded in 0ms:
   160	        result = Decimal(str(value))
   161	    else:
   162	        return None
   163	    return result if result.is_finite() else None
   164	
   165	
   166	def _current_estimator_code_sha256() -> dict[str, str] | None:
   167	    try:
   168	        return {
   169	            relative: hashlib.sha256((_REPO_ROOT / relative).read_bytes()).hexdigest()
   170	            for relative in ESTIMATOR_CODE_PATHS
   171	        }
   172	    except OSError:
   173	        return None
   174	
   175	
   176	def _valid_acceptance_bound(value: Any) -> bool:
   177	    """Validate the D-102 artifact from its decimal-source member table."""
   178	
   179	    if not isinstance(value, Mapping):
   180	        return False
   181	    core = {key: item for key, item in value.items() if key != "derivation_sha256"}
   182	    identity = value.get("identity_epoch")
   183	    prospective = value.get("prospective_rederivation")
   184	    corpus = value.get("derivation_corpus")
   185	    prior = value.get("prior_observation_set")
   186	    cutoff = value.get("ledger_cutoff")
   187	    issuance = value.get("issuance")
   188	    backfill = value.get("backfill_candidate")
   189	    derivation = value.get("decimal_derivation")
   190	    role = value.get("artifact_role")
   191	    if role == "schema_fixture_unissued":
   192	        role_valid = (
   193	            value.get("schema_version") == ACCEPTANCE_FIXTURE_SCHEMA
   194	            and isinstance(issuance, Mapping)
   195	            and issuance.get("status") == "unratified_fixture"
   196	            and issuance.get("claim_eligible") is False
   197	            and isinstance(cutoff, Mapping)
   198	            and cutoff.get("sequence") == 0
   199	            and cutoff.get("head_digest") == "0" * 64
   200	            and cutoff.get("role")
   201	            == "fixture_genesis_not_a_production_issuance_cutoff"
   202	            and isinstance(backfill, Mapping)
   203	            and backfill.get("status") == "unratified_candidate_only"
   204	            and backfill.get("production_issuance_blocked") is True
   205	        )
   206	        allowed_prior_dispositions = {
   207	            "valid",
   208	            "systematic-invalid",
   209	            "ordinary-invalid",
   210	            "blind-holdout",
   211	            "unresolved",
   212	        }
   213	    elif role == "issued":
   214	        role_valid = (
   215	            value.get("schema_version") == ACCEPTANCE_BOUND_SCHEMA
   216	            and isinstance(issuance, Mapping)
   217	            and issuance.get("status") == "issued"
   218	            and issuance.get("claim_eligible") is True
   219	            and isinstance(cutoff, Mapping)
   220	            and isinstance(cutoff.get("sequence"), int)
   221	            and not isinstance(cutoff.get("sequence"), bool)
   222	            and cutoff.get("sequence") > 0
   223	            and _valid_sha256(cutoff.get("head_digest"))
   224	            and cutoff.get("head_digest") != "0" * 64
   225	            and cutoff.get("role") == "issued_acceptance_baseline"
   226	            and isinstance(backfill, Mapping)
   227	            and backfill.get("status") == "issued"
   228	            and backfill.get("production_issuance_blocked") is False
   229	        )
   230	        allowed_prior_dispositions = {
   231	            "valid",
   232	            "systematic-invalid",
   233	            "ordinary-invalid",
   234	        }
   235	    else:
   236	        return False
   237	    if (
   238	        not role_valid
   239	        or value.get("acceptance_id") != "d079_calibration_acceptance_v2_n19"
   240	        or value.get("decision_ids") != ["D-102", "D-109"]
   241	        or value.get("derivation_sha256") != _canonical_sha256(core)
   242	        or not isinstance(identity, Mapping)
   243	        or set(identity) != set(ACCEPTANCE_IDENTITY_FIELDS)
   244	        or any(identity.get(field) in (None, "") for field in ACCEPTANCE_IDENTITY_FIELDS)
   245	        or not isinstance(prospective, Mapping)
   246	        or prospective.get("calendar_expiry") is not None
   247	        or prospective.get("trigger_observation_rule")
   248	        != "judge_under_prior_artifact_never_self_fit"
   249	        or prospective.get("protocol_sha256") != protocol_sha256(PROTOCOL_ID)
   250	        or not isinstance(prospective.get("estimator_code_sha256"), Mapping)
   251	        or set(prospective["estimator_code_sha256"]) != set(ESTIMATOR_CODE_PATHS)
   252	        or any(
   253	            not _valid_sha256(item)
   254	            for item in prospective["estimator_code_sha256"].values()
   255	        )
   256	        or not isinstance(prospective.get("triggers"), list)
   257	        or set(prospective["triggers"])
   258	        != {
   259	            "identity_field_change",
   260	            "protocol_or_estimator_byte_change",
   261	            "new_valid_same_identity_capture_expands_observed_range",
   262	            "corpus_doubles_from_19_to_38",
   263	            "new_systematic_failure_challenges_preflight_screen",
   264	        }
   265	        or not isinstance(corpus, Mapping)
   266	        or corpus.get("n") != 19
   267	        or not isinstance(corpus.get("members"), list)
   268	        or len(corpus["members"]) != 19
   269	        or not isinstance(cutoff, Mapping)
   270	        or cutoff.get("ledger_schema") != LEDGER_SCHEMA
   271	        or not isinstance(prior, Mapping)
   272	        or prior.get("cutoff")
   273	        != {
   274	            "sequence": cutoff.get("sequence"),
   275	            "head_digest": cutoff.get("head_digest"),
   276	            "ledger_schema": cutoff.get("ledger_schema"),
   277	        }
   278	        or not isinstance(prior.get("epoch_catalog"), Mapping)
   279	        or set(prior["epoch_catalog"]) != {"d079_epoch"}
   280	        or prior["epoch_catalog"].get("d079_epoch") != identity
   281	        or not isinstance(prior.get("observations"), list)
   282	        or not isinstance(derivation, Mapping)
   283	        or derivation.get("numeric_semantics") != "decimal_source_lexemes"
   284	    ):
   285	        return False
   286	    member_ids: list[str] = []
   287	    values: list[Decimal] = []
   288	    for member in corpus["members"]:
   289	        if (
   290	            not isinstance(member, Mapping)
   291	            or set(member)
   292	            != {
   293	                "member_id",
   294	                "source_directory",
   295	                "b_fiducial_s",
   296	                "manifest_sha256",
   297	                "instrument_evidence_sha256",
   298	            }
   299	            or not isinstance(member.get("member_id"), str)
   300	            or not isinstance(member.get("source_directory"), str)
   301	            or not _valid_sha256(member.get("manifest_sha256"))
   302	            or not _valid_sha256(member.get("instrument_evidence_sha256"))
   303	        ):
   304	            return False
   305	        bound = _decimal(member.get("b_fiducial_s"))
   306	        if bound is None or bound < 0:
   307	            return False
   308	        member_ids.append(member["member_id"])
   309	        values.append(bound)
   310	    if len(set(member_ids)) != 19 or member_ids != sorted(member_ids):
   311	        return False
   312	
   313	    prior_ids: list[str] = []
   314	    prior_attempt_ids: list[str] = []
   315	    prior_member_ids: set[str] = set()
   316	    for observation in prior["observations"]:
   317	        if (
   318	            not isinstance(observation, Mapping)
   319	            or set(observation)
   320	            != {"content_id", "epoch_id", "disposition", "attempt_id"}
   321	            or not _valid_sha256(observation.get("content_id"))
   322	            or observation.get("epoch_id") != "d079_epoch"
   323	            or observation.get("disposition") not in allowed_prior_dispositions
   324	            or not isinstance(observation.get("attempt_id"), str)
   325	            or not observation.get("attempt_id")
   326	        ):
   327	            return False
   328	        prior_ids.append(observation["content_id"])
   329	        prior_attempt_ids.append(observation["attempt_id"])
   330	        if observation["attempt_id"] in member_ids:
   331	            prior_member_ids.add(observation["attempt_id"])
   332	    if (
   333	        len(prior_ids) != len(set(prior_ids))
   334	        or len(prior_attempt_ids) != len(set(prior_attempt_ids))
   335	        or prior_member_ids != set(member_ids)
   336	    ):
   337	        return False
   338	    if role == "issued":
   339	        disposition_counts = {
   340	            disposition: sum(
   341	                observation["disposition"] == disposition
   342	                for observation in prior["observations"]
   343	            )
   344	            for disposition in sorted(allowed_prior_dispositions)
   345	        }
   346	        if (
   347	            len(prior["observations"]) != 38
   348	            or cutoff["sequence"] != 2 * len(prior["observations"])
   349	            or backfill.get("candidate_inventory") != disposition_counts
   350	        ):
   351	            return False
   352	    member_content_ids = {
   353	        content_id_from_artifact_hashes(
   354	            {
   355	                "manifest.json": member["manifest_sha256"],
   356	                "instrument_evidence.json": member[
   357	                    "instrument_evidence_sha256"
   358	                ],
   359	            }
   360	        )
   361	        for member in corpus["members"]
   362	    }
   363	    if None in member_content_ids or not member_content_ids.issubset(set(prior_ids)):
   364	        return False
   365	
   366	    statistics = derivation.get("source_statistics")
   367	    rounding = derivation.get("rounding")
   368	    operatives = derivation.get("ratified_operatives")
   369	    if not all(isinstance(item, Mapping) for item in (statistics, rounding, operatives)):
   370	        return False
   371	    with localcontext() as context:
   372	        context.prec = 80
   373	        count = Decimal(len(values))
   374	        mean = sum(values, Decimal(0)) / count
   375	        sample_sd = (
   376	            sum((item - mean) ** 2 for item in values) / Decimal(len(values) - 1)
   377	        ).sqrt()
   378	        quantum = Decimal("0.000000000000000001")
   379	        expected_statistics = {
   380	            "minimum_s": str(min(values)),
   381	            "maximum_s": str(max(values)),
   382	            "range_s": str(max(values) - min(values)),
   383	            "mean_presentation_s": str(
   384	                mean.quantize(quantum, rounding=ROUND_HALF_EVEN)
   385	            ),
   386	            "sample_sd_presentation_s": str(
   387	                sample_sd.quantize(quantum, rounding=ROUND_HALF_EVEN)
   388	            ),
   389	        }
   390	    minimum_id = member_ids[values.index(min(values))]
   391	    maximum_id = member_ids[values.index(max(values))]
   392	    if (
   393	        statistics.get("minimum_s") != expected_statistics["minimum_s"]
   394	        or statistics.get("maximum_s") != expected_statistics["maximum_s"]
   395	        or statistics.get("range_s") != expected_statistics["range_s"]
   396	        or statistics.get("minimum_member_id") != minimum_id
   397	        or statistics.get("maximum_member_id") != maximum_id
   398	        or not isinstance(statistics.get("mean_presentation_s"), Mapping)
   399	        or statistics["mean_presentation_s"].get("value")
   400	        != expected_statistics["mean_presentation_s"]
   401	        or statistics["mean_presentation_s"].get("label")
   402	        != "rounded_presentation"
   403	        or not isinstance(statistics.get("sample_sd_presentation_s"), Mapping)
   404	        or statistics["sample_sd_presentation_s"].get("value")
   405	        != expected_statistics["sample_sd_presentation_s"]
   406	        or statistics["sample_sd_presentation_s"].get("label")
   407	        != "rounded_presentation"
   408	        or statistics.get("prediction_95_two_draw_s")
   409	        != "0.008826584887500717"
   410	        or statistics.get("prediction_99_two_draw_s")
   411	        != "0.012093166090593858"
   412	        or rounding.get("mode") != "ROUND_HALF_EVEN"
   413	        or not isinstance(rounding.get("operative_bracket_screen"), Mapping)
   414	        or rounding["operative_bracket_screen"].get("quantum_s") != "0.000001"
   415	        or rounding["operative_bracket_screen"].get("value_s")
   416	        != _D102_OPERATIVE_VALUES["bracket_screen_s"]
   417	        or not isinstance(rounding.get("preflight_level_screen"), Mapping)
   418	        or rounding["preflight_level_screen"].get("quantum_s")
   419	        != "0.000000000000001"
   420	        or rounding["preflight_level_screen"].get("value_s")
   421	        != _D102_OPERATIVE_VALUES["preflight_level_screen_s"]
   422	        or any(operatives.get(key) != item for key, item in _D102_OPERATIVE_VALUES.items())
   423	        or operatives.get("allowance_rule")
   424	        != "max(observed_drift_s,bracket_screen_s)"
   425	        or operatives.get("operative_bound_rule")
   426	        != "max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s"
   427	        or operatives.get("embedding_count") != 1
   428	    ):
   429	        return False
   430	    screen = Decimal(_D102_OPERATIVE_VALUES["bracket_screen_s"])
   431	    maximum = Decimal(_D102_OPERATIVE_VALUES["maximum_budgetable_drift_s"])
   432	    excess = Decimal(_D102_OPERATIVE_VALUES["max_budgetable_excess_s"])
   433	    return (
   434	        (max(values) - min(values)).quantize(
   435	            Decimal("0.000001"), rounding=ROUND_HALF_EVEN
   436	        )
   437	        == screen
   438	        and max(values).quantize(
   439	            Decimal("0.000000000000001"), rounding=ROUND_HALF_EVEN
   440	        )
   441	        == Decimal(_D102_OPERATIVE_VALUES["preflight_level_screen_s"])
   442	        and screen + excess == maximum
   443	    )
   444	
   445	
   446	def load_calibration_acceptance_bound(
   447	    path: Path = DEFAULT_ACCEPTANCE_BOUND_PATH,
   448	) -> dict[str, Any] | None:
   449	    """Load the file-pinned D-102 acceptance artifact fail-closed."""
   450	
   451	    try:
   452	        raw = Path(path).read_bytes()
   453	    except OSError:
   454	        return None
   455	    return _acceptance_bound_from_authenticated_bytes(raw)

2026-08-07T20:25:46.733537Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
codex
## Delta verdict: NOT CLEAN

| Amendment | Status | Conclusion |
|---|---|---|
| FIX-A — production terminal sequence | CLOSED | The oracle is calculated as 76 + 3×5, the happy path executes the production lifecycle, and the resulting ledger contains both slot-claim receipts per session. The value 5 remains a test-module constant, but the test independently verifies the five-event production shape. [test_calibration_live_three_window.py:63](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:63), [test_calibration_live_three_window.py:215](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:215), [validate_powermetrics_fiducial.py:391](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/scripts/validate_powermetrics_fiducial.py:391) |
| FIX-B — two-sided allowance oracle | CLOSED | Both operands are exercised. Replacing max with observed drift alone failed on alpha; replacing it with the screen alone failed on beta; replacing it with min failed on both. [test_calibration_live_three_window.py:896](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:896) |
| FIX-C — D-116-derived parent | PARTIAL | The parent is internally arithmetically valid and retains the authentic 19-member derivation corpus, but it is still manually reconstructed and rehashed rather than emitted through the D-116 emitter or escalated through NEEDS_SCOPE. [test_calibration_live_three_window.py:306](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:306) |
| FIX-D — L5 cross-root regression | NOT CLOSED | The no-binding arm refuses only because no binding exists; the binding arm uses beta’s correct binding and expects success. It never supplies a binding naming foreign-root endpoints. A mutation that made evaluation trust the binding’s own `runs_root` survived: `Ran 1 test in 0.306s` / `OK`. [test_calibration_live_three_window.py:743](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:743) |
| FIX-E — per-window issuance and commit cadence | PARTIAL | Each closeout has a committed pin and independently passing verdict, followed by terminal-head replay. The test does not compare the originally issued verdict bytes with terminal replay, and the required open-beta/alpha-verdict vector is absent. [test_calibration_live_three_window.py:775](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:775) |
| FIX-F — positive count boundary and scope gate | PARTIAL | The active test proves 36 valid observations and absence of the trigger. Adding exactly two observations and observing the trigger remains an explicit U2-skipped placeholder; no NEEDS_SCOPE clause was added. [test_calibration_live_three_window.py:932](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:932), [test_calibration_live_three_window.py:1376](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:1376) |

No previously active vector was broken by the fixture amendment; the surviving and renamed vectors pass. The production bundle entry point now genuinely derives candidates through ledger discovery. [test_calibration_live_three_window.py:631](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:631)

The three U2 vectors are visibly staged, not silently disabled: all carry the explicit U2-pending skip reason and the module reports exactly three skips. Their bodies are placeholders rather than successor integrations, so they are correctly gated but not ready merely by removing the decorators. [test_calibration_live_three_window.py:1366](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:1366)

Current U1 integration does not break U4. U1’s newer head changes only append-recovery implementation/tests, has no merge conflict with U4, and the U4 module passed against the newer ledger module in memory. U4 does depend on private U1 seams, which is a future refactoring risk but not a current merge blocker. [test_calibration_live_three_window.py:215](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:215), [test_calibration_live_three_window.py:508](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:508)

Same-signature statement:

- Stale-memo-literal: NO. Sequence 85 remains only as explicitly superseded fixture history.
- One-sided-branch test: NO. All three requested allowance mutations fail.

Checks performed:

- U4 module: `Ran 23 tests in 0.680s` / `OK (skipped=3)`.
- Calibration bracketing: `Ran 39 tests in 3.474s` / `OK`.
- Calibration ledger: `Ran 46 tests in 9.609s` / `OK`.
- Powermetrics fiducial: `Ran 40 tests in 29.923s` / `OK`.
- U4 against current U1 head: `Ran 23 tests in 0.626s` / `OK (skipped=3)`.
- Allowance mutants: drift-only `FAILED (failures=1)`; screen-only `FAILED (failures=1)`; min `FAILED (failures=2)`.
- L5 root-validation mutant: `Ran 1 test in 0.306s` / `OK`, confirming the coverage gap.
- `git diff --check` passed; workspace remained clean.
tokens used
177,215
## Delta verdict: NOT CLEAN

| Amendment | Status | Conclusion |
|---|---|---|
| FIX-A — production terminal sequence | CLOSED | The oracle is calculated as 76 + 3×5, the happy path executes the production lifecycle, and the resulting ledger contains both slot-claim receipts per session. The value 5 remains a test-module constant, but the test independently verifies the five-event production shape. [test_calibration_live_three_window.py:63](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:63), [test_calibration_live_three_window.py:215](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:215), [validate_powermetrics_fiducial.py:391](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/scripts/validate_powermetrics_fiducial.py:391) |
| FIX-B — two-sided allowance oracle | CLOSED | Both operands are exercised. Replacing max with observed drift alone failed on alpha; replacing it with the screen alone failed on beta; replacing it with min failed on both. [test_calibration_live_three_window.py:896](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:896) |
| FIX-C — D-116-derived parent | PARTIAL | The parent is internally arithmetically valid and retains the authentic 19-member derivation corpus, but it is still manually reconstructed and rehashed rather than emitted through the D-116 emitter or escalated through NEEDS_SCOPE. [test_calibration_live_three_window.py:306](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:306) |
| FIX-D — L5 cross-root regression | NOT CLOSED | The no-binding arm refuses only because no binding exists; the binding arm uses beta’s correct binding and expects success. It never supplies a binding naming foreign-root endpoints. A mutation that made evaluation trust the binding’s own `runs_root` survived: `Ran 1 test in 0.306s` / `OK`. [test_calibration_live_three_window.py:743](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:743) |
| FIX-E — per-window issuance and commit cadence | PARTIAL | Each closeout has a committed pin and independently passing verdict, followed by terminal-head replay. The test does not compare the originally issued verdict bytes with terminal replay, and the required open-beta/alpha-verdict vector is absent. [test_calibration_live_three_window.py:775](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:775) |
| FIX-F — positive count boundary and scope gate | PARTIAL | The active test proves 36 valid observations and absence of the trigger. Adding exactly two observations and observing the trigger remains an explicit U2-skipped placeholder; no NEEDS_SCOPE clause was added. [test_calibration_live_three_window.py:932](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:932), [test_calibration_live_three_window.py:1376](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:1376) |

No previously active vector was broken by the fixture amendment; the surviving and renamed vectors pass. The production bundle entry point now genuinely derives candidates through ledger discovery. [test_calibration_live_three_window.py:631](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:631)

The three U2 vectors are visibly staged, not silently disabled: all carry the explicit U2-pending skip reason and the module reports exactly three skips. Their bodies are placeholders rather than successor integrations, so they are correctly gated but not ready merely by removing the decorators. [test_calibration_live_three_window.py:1366](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:1366)

Current U1 integration does not break U4. U1’s newer head changes only append-recovery implementation/tests, has no merge conflict with U4, and the U4 module passed against the newer ledger module in memory. U4 does depend on private U1 seams, which is a future refactoring risk but not a current merge blocker. [test_calibration_live_three_window.py:215](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:215), [test_calibration_live_three_window.py:508](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u4/tests/test_calibration_live_three_window.py:508)

Same-signature statement:

- Stale-memo-literal: NO. Sequence 85 remains only as explicitly superseded fixture history.
- One-sided-branch test: NO. All three requested allowance mutations fail.

Checks performed:

- U4 module: `Ran 23 tests in 0.680s` / `OK (skipped=3)`.
- Calibration bracketing: `Ran 39 tests in 3.474s` / `OK`.
- Calibration ledger: `Ran 46 tests in 9.609s` / `OK`.
- Powermetrics fiducial: `Ran 40 tests in 29.923s` / `OK`.
- U4 against current U1 head: `Ran 23 tests in 0.626s` / `OK (skipped=3)`.
- Allowance mutants: drift-only `FAILED (failures=1)`; screen-only `FAILED (failures=1)`; min `FAILED (failures=2)`.
- L5 root-validation mutant: `Ran 1 test in 0.306s` / `OK`, confirming the coverage gap.
- `git diff --check` passed; workspace remained clean.
