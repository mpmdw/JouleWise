# HANDOFF — Architectural-Axes Intake & Process Amendments (AXI)

**From:** Ed, via advisory session 2026-07-14
**To:** Orchestrator (Claude Fable) instance, operating under this repo's standing rules
**Repo:** JouleWise, main @ d285989 or later
**Authority:** This document carries Ed's explicit direction, including one
override of a standing freeze (§2.1). Everything here still flows through
the repo's normal pipeline — councils, D-entries, queue rows, review
layers, run reports. Nothing in this document licenses skipping a gate
that isn't explicitly amended below.

---

## 0. Orchestrator conduct — read first

1. **Onboard normally.** Read `RUN_STATE.md` (including any
   ACTIVE_STOP_CARD), `TASK_QUEUE.md`, `docs/orchestration.md`, the
   audit checkpoint under `docs/reviews/2026-07-13-comprehensive-audit/`,
   and `docs/decision_log.md` tail before acting. If repo state
   contradicts this document (it was written against d285989), repo
   wins; surface the conflict to Ed rather than guessing.
2. **Equilibrium clause.** The comprehensive audit (declared 2026-07-13)
   remains the active gate for feature work and campaign prep. This
   handoff does NOT dissolve it. Your first working arc is: record Ed's
   decisions (§2, allowed under the gate as decision-log/process work),
   then resume and complete the audit fix-wave and adjudication, THEN
   launch the extension streams (§4). Window A ordering
   (shakedown → floor smoke → floors → baselines) is untouched and
   outranks everything in §4.
3. **Ask, don't assume.** §5 lists decisions that are Ed's. Present them
   as a single batched question set at the START of your session (with
   the defaults noted), not one-at-a-time mid-stream. Proceed on
   defaults only where §5 marks a default as safe-to-assume.
4. **Standing review pipeline applies to every diff:** design-argument
   round → counterreview → test amplification → writer-never-reviews-
   own-tests audit → your diff gate → final-head rule → integration
   review after parallel merges. You (the orchestrator/lead) do not
   write implementation code; you gate, verify, and direct. Live
   hardware verification is never delegated and never simulated.
5. **Bookkeeping arc per session** is amended by §3 (site step changes)
   but otherwise standard: run report, queue reconciliation, RUN_STATE
   update, docs-consistency sweep.

---

## 1. Context you don't have (summary of the advisory session)

Ed's advisor (Dr. Rivoire — power-measurement SME, JouleSort lead author)
reviewed the proposal and raised three substantive points, all now
adjudicated with Ed:

- **Idle subtraction:** subtracting idle penalizes energy-proportional
  devices and rewards high-idle ones; for split runs, subtracting both
  nodes' idles deletes exactly the cost the crossover question (Q1)
  adjudicates. Resolution (Ed-directed, ratify per §2.2): dual-basis
  reporting with **gross energy as the headline basis for all
  cross-device, cross-configuration, and split-vs-monolithic claims**;
  idle-subtracted retained as a clearly-labeled within-device marginal
  view, never used to rank devices. Q4's fixed term (E = fixed +
  prefill + decode) is **fit on gross energy** across the workload
  sweep, so fixed is estimated from data — capturing idle + model
  residency + runtime overhead — not assumed equal to the measured idle
  baseline. Note: bundles already record both bases over preserved raw
  traces, so this is a reporting/wording change, not re-measurement.
- **Batching:** batch=1 decode is the pathological case for a
  bandwidth-bound phase; batch B amortizes weight reads, so J/token can
  fall severalfold. Batching is also the operational answer to the
  energy-proportionality problem and extends Q4 falsifiably
  (E(B) = fixed + B·marginal). Ed wants batching thoroughly
  investigated, plus broad architectural support (§1.1).
- **Benchmark vs harness:** terminology now split — harness =
  instrument; benchmark = the frozen workload suite + run rules +
  strict validator layered on it. Reader-facing docs should use this
  split consistently.

An updated proposal reflecting all of this exists in Ed's Google Drive
("Senior Capstone Proposal — JouleWise (rev. 2026-07-14, repo-aligned)").
The repo's front-facing docs have NOT yet been updated to match — that's
part of this handoff (§4, stream S-0).

### 1.1 The extension agenda (Ed's directive)

Once the harness works, Ed wants it able to characterize architectural
inference features generally: **static batching, speculative decoding /
MTP, MoE vs dense, quantization, reasoning-length variance** — framed as
stress tests of the single Q4 thesis, not five new theses. The registry
already contains most of the target rows: C5-2.2 and C5-2.6 (batching,
currently P1-006-gated), C5-2.5 and C-023-OUTPUT-IDENTITY (spec decode),
C5-1.1 / C5-1.9 / RQ-TWO-MODEL-ACTIVE-NONCLAIM (MoE/dense), C5-1.12 and
C-023-QUALITY-EQUIV-QUANT (quantization), RQ-ENERGY-VARIANCE and C5-W.2
(reasoning variance). Two genuinely new rows to mint: a **Mac-batching
leg of C5-2.2** (de-gates it from NVIDIA access) and **MOE×BATCH**
(expert-activation diversity vs batch size; candidate, ceiling L2,
forbidden upgrade: no MoE-serving-efficiency generalization from one
pair). Claim posture: **instrument support (L0 smoke bundles) for all
axes; characterized-claim commitments narrow** (§5.2).

---

## 2. Ed's decisions to record FIRST (allowed under the audit gate)

These are decision-log / process work, not feature work. Record each as
a D-entry with this handoff cited as provenance; where a council is
normally required for contract-bearing changes, hold a short recorded
session per standing rules, but the outcomes below are Ed-directed.

### 2.1 Spec-freeze override (explicit Ed override)

Ed: "I know we spec froze a way back but I'm overriding that." Record a
D-entry stating that the spec/contract freeze is lifted **for the scoped
purpose of the AXI extensions** (burst-decode metric semantics, batch
axis, idle-basis wording, and consequent schema/reducer/contract
changes), by Ed's authority, dated, with this document as rationale.
Contract changes still require their own D-entries and council review —
the override removes the freeze as a blocker, not the process. If any
existing stop card or audit rule conflicts with acting on this, record
the D-entry now and sequence the ACTION after audit clearance.

### 2.2 Idle reporting basis

Record the D-entry per §1: gross-headline for cross-device/split claims;
idle-subtracted as labeled secondary within-device view; Q4 fixed term
fit on gross. Rivoire's energy-proportionality argument is the recorded
rationale. Downstream doc fixes are stream S-0.

### 2.3 Site deploy becomes manual (process change)

Ed: take website building out of the automated loop. Record a D-entry:

- The standard end-of-session bookkeeping arc **no longer regenerates or
  deploys the Lakebed site.** Deploy is an Ed-manual action.
- What replaces it: a **site-drift report**. Implement the lightweight
  version first: a script (e.g., `scripts/site_drift.py` or a make
  target) that compares the deployed site's snapshot metadata (commit
  hash / status revision the live page claims) and key front-facing
  numbers against current repo state, and writes/refreshes a short
  `docs/site/DRIFT.md` listing what's stale and which sections need
  regeneration. Sessions that change front-facing state end by
  refreshing DRIFT.md instead of deploying. Spawning a subagent to do
  the diff (fetch live page, compare against repo docs) is an
  acceptable implementation if the script route is awkward — Ed is
  indifferent to mechanism, firm on outcome: **automation informs; Ed
  deploys.**
- The existing drift banner on the site remains as-is (it already
  self-reports staleness to readers).

### 2.4 Advisor-doc alignment is sanctioned front-facing work

The idle/batching/benchmark-vs-harness updates to PROJECT_STATUS.md,
README, and site source (stream S-0) are corrections of reader-facing
claims and terminology — the same class as the existing convention that
front-facing docs misstating claims get fixed. Sequence S-0 immediately
after audit clearance (or fold into the audit's own fix-wave if a
finding already covers the wording).

---

## 3. Amended bookkeeping arc (effective on recording §2.3)

Per session: run report → queue reconciliation → RUN_STATE update →
docs-consistency sweep → **refresh `docs/site/DRIFT.md` if front-facing
state changed** (no regen, no deploy). Everything else unchanged.

---

## 4. Work program (post-audit-clearance streams)

Sequencing: **S-0 first** (cheap, advisor-facing), then S-A (the
contract prerequisite), then S-B/S-C/S-D/S-E as parallel worktrees.
Each stream becomes a ranked queue row before work starts; TASK_QUEUE
remains the ordering authority; no stream outranks Window A rows or
consumes a [QUIET-MAC] window.

### S-0 — Front-facing alignment (docs only)

Apply the idle-basis wording (state the basis on every number,
gross-first for any cross-config number), the harness/benchmark
terminology split, and the batching/architectural agenda framing across
PROJECT_STATUS.md, README, and site sources. Update the registry: the
idle-basis D-entry closes the open question referenced by
C-023-IDLE-STATIONARITY's framing (the row itself — how idle model
choice affects conclusions — stays alive as a sensitivity check).
End by refreshing DRIFT.md so Ed can run one manual deploy.

### S-A — Burst-decode metric-semantics contract [contract-bearing; blocks S-C]

- Extend `docs/contracts/token_normalization.md` + schema:
  `tokens_proposed`, `tokens_accepted`, `acceptance_rate`,
  emission-event granularity in events.jsonl (N tokens per decode
  step), draft-model identity fields (null for native MTP heads).
- Generalize the reducer's per-generated-token and inter-token metrics
  for burst arrivals; freeze against legacy arms (no re-dispatch of
  existing bundles).
- Make C-023-OUTPUT-IDENTITY executable: output equivalence/divergence
  report required by any spec-decode efficiency claim.
- **Freeze the denominator rules into the P2-042 analysis manifest
  BEFORE any spec-decode bundle can exist.** Post-C-027, denominator
  ambiguity is made structurally impossible or nothing merges.
- Exit: schema + reducer + validator merged; a mock spec-decode adapter
  produces strict-valid bundles; manifest entry frozen; zero live claims.

### S-B — mlx-lm static-batch feasibility spike [time-boxed, verdict-shaped]

One session + one live-verification pass. Question: does pinned mlx-lm
support static batch generation with per-sequence token streams adequate
for the event model? `supported` → follow-on adapter row (batch_size
config knob, per-sequence token events). `unsupported` → C5-2.2 stays
P1-006-gated and the dated negative verdict is filed as a finding
(Hailo idiom). Mint the Mac-batching registry leg on a `supported`
verdict only.

### S-C — Spec-decode runtime spike [after S-A schema lands]

Leg 1: mlx-lm speculative/draft support on the Mac stack (live spike).
Leg 2: vLLM spec-decode fixture-first for the 2K slice (PROVISIONAL, NV-
GATE discipline). Survey native-MTP (draft-free) model candidates as a
model-selection input feeding D-016, not as runtime work.

### S-D — Model + quantization artifact groundwork [desk work]

Matched dense/MoE pair proposal for D-016 (same family, matched active
params; fallback matched total) with local mirrors + hash manifests.
Quantization ladder for C5-1.12: 2–3 quant levels of one model, mirrored
and hashed, with the quality-equivalence reporting rule predeclared per
C-023-QUALITY-EQUIV-QUANT.

### S-E — Analysis plans [desk work]

- **AP-BATCH:** E(B) = fixed + B·marginal fit on GROSS energy,
  B ∈ {1,2,4,8,16}, one model, one workload shape, n=5, predeclared
  breakpoint handling; framed as a Q4 coefficient stress test.
- **AP-5 extension:** dense/MoE contrast rides inside the 2M baseline
  campaign (zero extra quiet-machine cost) if D-016 selects the pair.
- **AP-SPEC:** spec-on vs spec-off at matched output policy; both
  denominators reported; equivalence-gated per S-A.
- All APs floor-gated: none executes before P2-015 publishes floors;
  every predeclared effect size is checked against the measured floor
  before its campaign is scheduled.

---

## 5. Decisions to put to Ed (batch these at session start)

1. **Audit-first confirmation** — default (safe to assume): resume and
   complete the audit fix-wave/adjudication before launching §4 streams;
   §2 D-entries recorded immediately regardless. Ask only if the audit
   scope makes S-0 awkward to sequence.
2. **Characterized-claim commitments** — default: MoE/dense (free via
   D-016 inside the 2M campaign) + static batching (one quiet-machine
   block, ~25 runs). Everything else = ordered stretch rungs below the
   split study on the descope ladder. **Confirm the ranking** — every
   stretch rung funded with quiet-Mac time is a session the interconnect
   sweep doesn't get. This is Ed's genuine trade-off; do not default it.
3. **D-016 model pair** — needs Ed (and advisor input in flight). Present
   S-D's proposal when ready; do not finalize unilaterally.
4. **Continuous batching** — default: out of capstone scope (per-token-
   at-offered-load deferred); static batch only. Confirm.
5. **Site-drift mechanism** — default: script + DRIFT.md; subagent diff
   acceptable alternative. Pick whichever is cleaner; only ask if both
   turn out awkward.
6. **Idle D-entry wording** — draft it, show Ed the final text before
   recording (it will be quoted to the advisor).

## 6. Explicit do-nots

- No live claims from fixture-first code; PROVISIONAL until first live
  hardware contact.
- No claim-ceiling renegotiation: everything in §4 caps at L2 (L3 only
  through Q4/AP-1's existing holdout machinery); ceilings move only via
  replication rows (C5-3.1).
- No quiet-machine consumption by §4 streams; [QUIET-MAC] windows belong
  to Window A until Ed says otherwise.
- No site regeneration or deployment by any agent, ever, effective §2.3.
- No skipping the batched §5 question set — Ed expects to be asked.
