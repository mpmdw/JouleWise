# T3 doctrine amendment map — T3-AMEND-01

Date: 2026-08-05  
Binding source: `docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md`  
Scope: amendment drafting only; the frozen 2026-08-03 packet and rulings are
unchanged.

**Version recommendation (lead ratifies): bump `bridge-protocol/v1.1` to
`bridge-protocol/v1.2`.** The amendments add normative routing, provenance,
ingestion-event, approval-evidence, native-write custody, and reverse-consult
eligibility semantics. Per the lead ruling, the contract itself remains
labelled v1.1 in this branch pending ratification.

## Amendment inventory

Each ID below occurs exactly once in this table. “LANDED” names the ONE
normative home. “LEAD-BENCH” is an out-of-repository home and includes complete
draft text below. “OUT-OF-SCOPE” is an in-repository home outside this worker's
write allowlist and likewise includes complete text where a write remains.
“CHECKED / NO NEW WRITE” identifies a disposition whose owning text already
landed or which imposed no additional amendment.

| ID | Synthesis amendment or disposition checked | Disposition and exact landing site |
|---|---|---|
| A01 | Q1a — prohibit t3 Full access now; prohibition does not depend on exact flag mapping | **LANDED** — `docs/contracts/bridge_protocol.md` §4, “T3-mediated presentation, routing, and provenance,” Full-access paragraph. |
| A02 | Q1a — version-bound argv/process-table custody artifact owed at the next t3 session | **LANDED** — `.claude/skills/codex/SKILL.md` §Transport selection, post-sequence amendment-exhibit paragraph. |
| A03 | Q1a / E9 — Auto cards are post-hoc notifications and never approval evidence | **LANDED** — contract §4, t3 approval-evidence paragraph. |
| A04 | Q1a / E10 / SX4 — thread-side approval reports are inadmissible; anything needing Ed's eyes uses Supervised and approval claims use harness events | **LANDED** — contract §4, t3 approval-evidence paragraph; launch-side execution pointer in the Claude skill §Transport selection. |
| A05 | Q1b — no pattern-kills; only manifest PIDs with start-time and ancestry verification | **LANDED UNMODIFIED** — contract §6, immediately after stale-lease handling. |
| A06 | Q1c — t3 checkpoint revert fencing plus active-lease resolution and fresh invocation/lease before delegation resumes | **LANDED** — contract §6, checkpoint-revert paragraph. |
| A07 | Q1d — t3-native Codex is Ed-direct only and never lead-delegated or gate-bearing | **LANDED** — contract §4, native-thread paragraph. |
| A08 | Q1d — material native-output consumption requires a tracked ingestion event binding session identity, output digest, disposition, and process-trace location | **LANDED** — contract §4, native-thread paragraph. |
| A09 | Q1e — tracked subagent route narrowed to substantial background/parallel Sol rounds needing lifecycle visibility; steward has no implementation/adjudication authority | **LANDED** — contract §4, tracked-subagent paragraph; operating selection in `.claude/skills/codex/SKILL.md` §Transport selection step 2. |
| A10 | Q1e — conditional route is a two-arc pilot recording view use, wrapper failures, latency, and Fable overhead | **LANDED** — contract §4, tracked-subagent paragraph; skill step 2 points to it. |
| A11 | Q1e — wrapper invocation counts under D-080 and is not silently deduplicated from the child | **LANDED** — contract §4, tracked-subagent paragraph. |
| A12 | Q2 — work-chunk-anchored cadence shape is affirmed but is non-operative until numeric and mechanical D-080 text lands | **LEAD-BENCH** — global `council` skill; full replacement text in LB-1. No in-repo text presents the trigger as operative. |
| A13 | Q2 — numeric backstop, manifest-consumption definition, and mechanical anchor enumeration | **LEAD-BENCH** — global `council` skill; full amendment in LB-1. |
| A14 | Q2 — reconcile D-080 clause 4(ii)'s stale zero-unique-catch citation | **LEAD-BENCH** — global `council` skill; full replacement text in LB-1. |
| A15 | Q2b / SX1 — A52 remains blocked on two legs: D-080 amendment and Ed's runner choice; duplicate row is a queue nit | **OUT-OF-SCOPE** — `TASK_QUEUE.md` and its owning `docs/process/state_kernel.json`; full row and dedup instruction in OS-1. |
| A16 | Q3a — clean worktree/equivalently doctrine-free convening and judge contamination disclosure | **CHECKED / NO NEW WRITE** — already landed in `docs/process/coldgate_charter_registry.md` §Convening procedure before this session; charter-v3 fold-in remains **OUT-OF-SCOPE** with full text in OS-2. |
| A17 | Q3b — minimal validator remains owed | **CHECKED / NO NEW WRITE** — already specified in `docs/process/coldgate_charter_registry.md` §Minimal validator and queued as `COLDGATE-VALIDATOR-01`; implementation is not part of this amendment scope. |
| A18 | Q3c — paired sealed cold Fable judge + Sol refuter mechanism affirmed | **CHECKED / NO NEW WRITE** — current contract is not the mechanism's home; ratified charter v2 §5 already contains the composition and sealing rule. |
| A19 | Q3d — charter v2 digest `099de884…c95d81` ratified | **CHECKED / NO NEW WRITE** — registry operative row already records RATIFIED after Ed's 2026-08-05 ack. |
| A20 | Q3d — charter v3 should relax “exact line range” to exact mechanical identification sufficient for verbatim verification | **OUT-OF-SCOPE** — `docs/process/coldgate_charter.md` §4; complete replacement sentence in OS-2. |
| A21 | Q3e — merged standing-Ed-directive effort rule | **LANDED SUBSTANCE-VERBATIM** — `.claude/skills/codex/SKILL.md` §Effort selection. Contract §10 already identifies that section as the ONE effort-policy home, so no duplicate contract pointer was added. |
| A22 | Q4 — “TUI operation remains available” only outside `[QUIET-MAC]`; claim runs use an ordinary guarded shell with zero agent sessions | **LANDED** — contract §4, final t3-routing paragraph. |
| A23 | Q4 / SX2 — corrected provenance of Sol's full-shadow dissent | **CHECKED / NO NEW WRITE** — the correction is an evidence-record matter and already lives in frozen cure exhibit SX2 plus the synthesis; it creates no bridge rule. |
| A24 | Q5 — `originator` is a provenance hint within the four-axis record, never sole discriminator or authority-bearing | **LANDED** — contract §4, four-axis provenance paragraph. |
| A25 | Q5 — observed values are version-bound to 0.146.0; unknowns fail closed | **LANDED** — contract §4, four-axis provenance paragraph. |
| A26 | Q5 — corroborate `originator` using authoritative §4 route and §6 `owner_kind` | **LANDED** — contract §4 provenance paragraph and §6 `owner_kind` paragraph. |
| A27 | Q5 / §8 — `originator` cannot create top-level reverse-consult authority | **LANDED** — contract §8, top-level eligibility paragraph. `.agents/skills/claude-consult/SKILL.md` already points normatively to contract §8 and therefore needs no duplicate rule. |
| A28 | SX5 — t3 is preferred/main driver when in use, never mandatory or exclusive; plain Claude Code sessions receive no t3 ceremony | **LANDED** — contract §4 opening t3 paragraph and `.claude/skills/codex/SKILL.md` §Transport selection applicability paragraph; `.claude/agents/codex.md` and `.claude/commands/codex.md` point to that operating home. |
| A29 | Acceptance forward-binding — future native-write gates are predeclared and bind route/session to manifest and result; no future retrospective designation | **LANDED** — contract §7, native-write acceptance-gate paragraph. |
| A30 | Phone-approval gate — Supervised clearance rests on SX4 harness-event custody; Auto caveat binds as doctrine | **LANDED** — normative evidence rules in contract §4; the historical gate clearance remains in the synthesis/SX4 rather than being duplicated as wire policy. |
| A31 | Cold-packet-handoff — cleared-with-exception only with the clean-launch cure and Ed ack | **CHECKED / NO NEW WRITE** — registry convening cure and `RUN_STATE.md` 2026-08-05 ack already record both legs; no additional bridge amendment follows. |
| A32 | Checkpoint-restore and app-death gates remain OPEN with predeclared lease/idempotence and recovery-state criteria | **OUT-OF-SCOPE STATUS** — no in-scope bridge text may claim these gates cleared; carry-forward text in OS-3 for their owning acceptance-gate record. |

## LEAD-BENCH full text

### LB-1 — global `council` skill: D-080 amendment

Home: `/Users/edr/.claude/skills/council/SKILL.md`, section “Standing
fresh-eyes sweep.” This is outside the repository and requires lead/Ed
ratification. Replace the current **Cadence — ONE unit, not several** paragraph
with the following, and replace anti-ritual clause (ii) as shown. All other
D-080 clauses remain unchanged.

> **Cadence — work-chunk anchors with one numeric backstop.** The sweep becomes
> due immediately after the first mechanically recorded anchor event since the
> previous completed sweep. The anchor events are exactly:
>
> 1. **Substantial-round consumption:** a lead-authored D-064 `run_consumed`
>    event with disposition `consumed` for an invocation whose opening bridge
>    header records `TASK_SHAPE: autonomous`.
> 2. **Merge-wave close:** the lead commits a run-report or council disposition
>    that identifies the final commit IDs for a completed wave of one or more
>    related merges.
> 3. **Adjudication close:** the lead commits the final synthesis or disposition
>    for a rule-11 gate, with the instrument outputs and per-question outcomes
>    identified.
>
> Multiple anchor events recorded before one due sweep completes are coalesced
> into that one sweep and are listed in its packet; they do not create duplicate
> sweeps. The numeric starvation backstop is **10 materially consumed
> invocations** since the previous completed sweep. “Materially consumed
> invocation” has one mechanical meaning: an invocation for which the tracked
> D-064 manifest contains a lead-authored `run_consumed` event with disposition
> `consumed`. `rejected` and `deferred` dispositions do not count. Every actual
> invocation retains its own count: retries and resumes count through their own
> invocation rows, and a tracked route-(b) wrapper invocation is not
> deduplicated from its audited child invocation. Completing a sweep resets the
> backstop counter. A reactive trigger consult resets it only under D-080's
> existing asymmetric-reset rule, when that consult carried all mechanical
> sweep-packet sections.
>
> The value 10 is retained from D-080 as the explicit provisional backstop and
> is recalibrated only through the existing two-session calibration rule. This
> amendment replaces the former invocation-count-plus-phase-boundary cadence;
> it does not change composition, packet contents, the anti-ritual termination
> rule, or any reactive trigger. The work-chunk shape is non-operative until
> this full amendment is ratified in the global skill.

Replacement for anti-ritual clause (ii):

> (ii) Evaluation is over completed sweep sessions. A rotating lens with zero
> plan-changing catches over two full sweep sessions rotates down; the cold
> lens is evaluated over one full phase and is not exempt. This is the
> sweep-specific zero-catch rule and does not depend on a citation to a separate
> “existing” zero-unique-catch policy.

Drafting note: the numeric choice is not newly invented here; it retains
D-080's already accepted provisional value. The synthesis ratified the new
shape but makes it operative only when this complete amendment lands. Ed's
runner choice (cron routine versus manual) remains a separate unresolved leg.

## OUT-OF-SCOPE full text

### OS-1 — A52 queue/state-kernel correction

Owning paths: `docs/process/state_kernel.json` followed by generated
`TASK_QUEUE.md`. Keep exactly one A52 projection and replace the duplicate rows
with this single row (the generator/state-kernel edit must preserve the same
substance):

> | A52 | D080-TRIGGER-01 | P3 Hardening Candidates | BLOCKED — D-080 amendment + Ed runner ruling (cron routine vs manual) [AGENT] | After the D-080 numeric/mechanical cadence amendment lands, wire the standing fresh-eyes sweep to the Ed-selected runner as a separate concurrent read-only instance, with findings delivered mid-flight; reconcile D-080 clause 4(ii)'s stale zero-unique-catch citation. | The row does not unblock on the 2026-08-03 doctrine gate alone. It unblocks only when the full D-080 amendment lands and Ed rules the runner; acceptance then requires the ratified trigger to fire at least once without operator memory. Authority: D-080; `docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md` Q2/Q2b and SX1. |

### OS-2 — cold-gate charter v3 fold-ins

Owning path: `docs/process/coldgate_charter.md`. A byte change creates a new
candidate and requires its own gate. Insert this launch clause before current
§1:

> **Launch environment and disclosure.** Before convening a cold instance, the
> convener MUST verify that its launch environment will not auto-load operating
> doctrine, session memory, or narrative process/state documents. Use a git
> worktree where those sources are absent, or an equivalently verified
> doctrine-free context. Every cold ruling MUST open with a disclosure naming
> any doctrine or memory material present at launch, including “none observed.”
> Contamination does not void a ruling automatically; the ruling stands or
> falls on its verified evidence. Contamination discovered later that the judge
> failed to disclose voids the ruling.

In charter §4, replace the sentence beginning “Such an exhibit must state”
with:

> Such an exhibit must state: source path, immutable revision or digest, exact
> mechanical identification sufficient for verbatim verification, the
> proposition it addresses, and why non-narrative primary evidence is
> unavailable, with enough contiguous context to be checked for selective
> quotation.

### OS-3 — still-open acceptance gates

Owning acceptance-gate record (lead selects the existing canonical status
surface):

> **Checkpoint-restore: OPEN.** Before any workflow relies on checkpoint or
> restore, run a predeclared scratch-repository exercise that records before
> and after repository state, captured manifest/diff, active-lease resolution,
> a fresh invocation/lease and rebaseline, and idempotence.
>
> **App-death recovery: OPEN.** Evaluate the next real quit/relaunch against
> predeclared criteria for history/checkpoint, cwd/worktree, provider,
> permission mode, epoch continuity, and absence of a duplicated turn or side
> effect.

## Open questions

No new process-rule gap was exposed by this drafting. The already identified
Ed-owned D-080 runner choice (cron routine versus manual) remains pending; it
is an existing ruled dependency, not a new question. The protocol version bump
is a recommendation only and remains for lead ratification.

## Completeness cross-check

I reread the synthesis in four passes: the per-question table; “Reasoning on
the splits”; “Acceptance-gate dispositions”; and “What this gate ratifies now
vs owes.” I then cross-checked SX1–SX5 and the original operating orders 1a–1e.
The resulting 32 uniquely keyed rows cover every normative amendment, every
forward-binding acceptance caveat, every charter/queue item whose natural home
is outside the write scope, and the affirmed/no-new-draft dispositions needed
to show they were considered. No synthesis amendment is represented by more
than one row, and none is omitted.
