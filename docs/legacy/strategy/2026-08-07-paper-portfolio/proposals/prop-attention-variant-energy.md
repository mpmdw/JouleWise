OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: high
reasoning summaries: none
session id: 019fdd0c-c279-7bf3-8ea4-f0b81f6f9cb5
--------
user
PAPER-PROPOSAL DEVELOPMENT SESSION (one of a 20-direction parallel fan-out).

You are developing ONE candidate research-paper direction for the JouleWise project
into a full, reviewable proposal. Work read-mostly; do NOT create or modify any files —
your final message IS the deliverable. You may read any repo file.

== PROJECT BRIEF (state as of 2026-08-07) ==
JouleWise is Ed's undergraduate CS capstone: treating Apple's `powermetrics` software
power counter as a calibrated scientific instrument for phase-resolved (prefill vs
decode), single-request LLM inference energy on one named M3 Max stack (MLX, Qwen2.5
family, 4-bit). Core findings/machinery to date: in-window bracketed pulse-train
calibration of timing attribution; the instrument is ATTRIBUTION-LIMITED (~1 J per
phase member from ~30 ms edge uncertainty × ~33 W swings; repetition cannot average it
away), not noise-limited; detection floors composed from repeatability + worst-case
attribution + measured never-zero drift, published labelled; TWO separate claim gates
(floor clearance; interval-supported direction) with a practical ~5 J sizing bar for
phase contrasts; fail-closed collection protocol (pre-registration, admission gates,
ABBA counterbalancing, hash-bound custody chains, refusal log as evidence). MVP paper
draft is complete-in-structure (docs/paper/draft-v1.md) with demonstration values
pending. The claim path (decision D-117, adopted today): THREE fresh prospective quiet
windows — 1.5B decode floor, 7B decode floor, 1.5B-vs-7B decode contrast — each
live-bracketed under an issued calibration-acceptance regime; prefill floor cells ride
the floor windows; a 256-token prefill contrast arm is an open option (128-token
prefill contrast is MARGINAL vs the bar — custodied desk check).
Steps from here: 3 quiet-mac nights (operator bookends only) + desk work (window plans,
mint pinsets, extraction specs, regression) → mint floors → populate the paper →
capstone submission; then an ICPE-class version.

== CONTEXT AND CONSTRAINTS ==
- Advisor: Suzanne Rivoire (JouleSort co-author) — sets a real metrology bar; plain
  language required in reader-facing text.
- Venue ladder: capstone (CSCSU-class) → ICPE full research track is the realistic
  ambitious target; top-tier only if a mechanism/split research bet lands.
- Hardware: M3 Max MacBook Pro 128 GB (the instrumented unit); an RTX 3080 Ti desktop
  rig; optional Jetsons; a Yokogawa WT310E wall meter is NOT owned but may be BORROWED
  from the advisor's lab (claim C8 ratified the wall-meter axis as future work).
- Measurement economics: each claim window is a 2-4 h quiet night with operator
  bookends; effects must clear the two gates (~5 J practical sizing for phase
  contrasts on this stack; workload LENGTH is the free lever since attribution error
  is ~duration-independent).
- Ed's ORIGINAL research goals (pre-metrology-pivot, still wanted long-term):
  mechanism-level energy profiling as a third metrics axis alongside quality+latency —
  speculative decoding, multi-token prediction (MTP), mixture-of-experts (MoE)
  routing, KV/attention variants (e.g. KDA), and SPLIT/disaggregated inference across
  consumer devices; a modular harness where every experiment axis (model, inference
  technique, workload, size) is swappable; energy-honest leaderboard/reporting
  critique. Repo context worth reading: docs/strategy/2026-08-06-impressiveness-roadmap.md,
  docs/research_question_registry.md, docs/research_question_bank.md,
  docs/paper/draft-v1.md (esp. §§3-5), CLAIMS_STATUS.md, docs/decision_log.md (D-117,
  at end of file).

== YOUR DELIVERABLE (final message, markdown, ~600-1200 words) ==
1. TITLE + one-sentence thesis.
2. PROJECT-BRIEF-AND-STEPS paragraph: half a page restating the current project state
   and the concrete steps from today to THIS paper (audience: Ed deciding what to
   fund with nights/desk time).
3. CONTRIBUTIONS (3-5, numbered, each falsifiable).
4. EXPERIMENT PLAN sized against the instrument: cells, contrasts, expected effect
   magnitudes vs the ~5 J sizing bar (estimate from public knowledge + repo
   diagnostics you can find; state which effects might NOT clear and what the refusal
   would mean), number of quiet windows needed, desk-work list, any new harness
   capability required (and whether it violates the frozen single-request boundary).
5. HARDWARE/INSTRUMENT needs (owned / borrowed / new; wall-meter dependency yes/no).
6. VENUE fit + why (capstone chapter? ICPE? workshop?), and how it BUILDS ON the MVP
   paper (shared method sections, what's new).
7. RISKS + KILL CRITERIA (what desk evidence would kill it before spending a night).
8. RELATION TO ED'S ORIGINAL GOALS: which original axis it serves, or state plainly
   that it does not.
Be concrete and quantitative wherever possible; flag every number you are unsure of.

== HARD CONSTRAINT (Ed, binding) ==
Every proposal MUST turn the EXISTING material into a solid scientific paper: the
calibrated instrument and its custody/fail-closed protocol machinery, the
attribution-limited finding, the banked diagnostics, the data the three D-117 windows
will produce (decode floors for 1.5B and 7B, prefill floor riders, the decode
contrast), and modest extensions collectible on the owned hardware under the SAME
instrument discipline. Do NOT propose work that abandons the instrument or needs
apparatus/data without a concrete path (the borrowed WT310E wall meter is allowed
where justified as an extension of existing material). If your assigned direction
cannot honestly be built from existing material, SAY SO PLAINLY and shrink it to the
version that can — a smaller honest paper beats an unmoored ambitious one.

== REQUIRED READING (read these in the repo before writing anything) ==
docs/paper/draft-v1.md (the whole draft — every proposal must state what it reuses
from it); CLAIMS_STATUS.md; the D-117 entry at the end of docs/decision_log.md;
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md (exactly what the three
windows produce, budgets, mint machinery); docs/strategy/2026-08-06-impressiveness-roadmap.md;
docs/research_question_registry.md; docs/research_question_bank.md;
docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md.

== YOUR ASSIGNED DIRECTION (attention-variant-energy) ==
Attention-mechanism energy contrasts on consumer silicon: KDA/GQA/sliding-window/full attention at matched quality, phase-resolved, under floors. (Original mechanism goal.)

codex
I’ll build this as an honest extension of the existing metrology paper, with special attention to whether KDA/GQA/sliding-window/full-attention comparisons are actually runnable and likely to clear the ~5 J bar on the frozen MLX/M3 Max path. I’ll first read the required evidence and current stop/queue state, then quantify a minimal experiment matrix and explicit desk-stage kill criteria.
  → Read required paper, decision, trace, strategy, and research files plus repository safety state
  • Extract instrument budgets, D-117 outputs, attention support, and effect-size evidence
  • Draft and cross-check the reviewable proposal against all requested sections
exec
/bin/zsh -lc 'git status --short --branch && rg -n "ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next" RUN_STATE.md && rg -n "Current Queue|Do-Not-Do-Yet|Do Not Do Yet|Mission M0|M0" TASK_QUEUE.md docs/agent_playbook.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## main...origin/main
2004:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
2039:## ACTIVE_STOP_CARD
2178:## Current Project Status
2739:## Known Workspace State
docs/agent_playbook.md:26:1. Run Mission M0 (preflight) — always.
docs/agent_playbook.md:50:## Mission M0: Preflight (every session)
docs/agent_playbook.md:56:2. Read `TASK_QUEUE.md`'s Current Queue and Do-Not-Do-Yet list.
docs/agent_playbook.md:326:in the run report. Never close it silently (Do-Not-Do-Yet list).
docs/agent_playbook.md:356:- Land Slice 2N first (Do-Not-Do-Yet list) — 2G builds on the post-2N
docs/agent_playbook.md:472:The M0 step-6 handoff list, plus: if you changed an adapter or bundle
TASK_QUEUE.md:96:Current Queue region is the sole live work-selection view.
TASK_QUEUE.md:213:## Current Do-Not-Do-Yet List
TASK_QUEUE.md:306:## Current Queue
TASK_QUEUE.md:362:| A31 | DOC-008-INTAKE | P4 Polish | READY [AGENT] | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
TASK_QUEUE.md:440:| A31 | DOC-008-INTAKE | P4 Polish | READY | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |

exec
/bin/zsh -lc "sed -n '2039,2215p' RUN_STATE.md; sed -n '2739,2815p' RUN_STATE.md; tail -n 120 RUN_STATE.md; sed -n '213,390p' TASK_QUEUE.md; sed -n '50,95p' docs/agent_playbook.md; wc -l docs/paper/draft-v1.md CLAIMS_STATUS.md docs/decision_log.md docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md docs/strategy/2026-08-06-impressiveness-roadmap.md docs/research_question_registry.md docs/research_question_bank.md docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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
`docs/run_reports/2026-07-18-claude-codex-pet-observer.md`.

Committed 2026-07-18 on `impl/env-guard-cooldown` (after the D-077
packet boundary `6d80039`) with a lead execution review at the bench:
IPC socket ownership/permission checks, PID-checked host-task lock,
interrupt-on-terminate, no-network sandbox policy, and one-hop rule all
verified in `scripts/codex-app-bridge.mjs`; real-socket fake-router
tests plus observer lifecycle tests included; canonical suite green
lead-side (`Ran 1722 tests`, `OK (skipped=12)`). The same commit
carries the doctor-driven CLAUDE.md trims (global + repo; content
deduplicated into `.claude/skills/codex/SKILL.md`, which is the
operating home) and stamp-only `docs/site/*.html` provenance refresh.

## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending

Window A floors contamination diagnosed from primary data: macOS Ventura
*video* screensaver on an awake display contaminated 43/50 suite-calibration
bundles (~+30% energy, −11% throughput; engage at HID-idle +20 min, dismiss on
unlock — pmset assertion log corroborated to the second). The six "low"
su-ABBA runs (18:16–18:36 UTC) are the only CLEAN suite runs; comparative
suite floors (4.923 J item / 24.62 J suite) are transition artifacts. The
professor's power-source hypothesis is refuted (AC/140 W/100% throughout).
Details: memory note + `docs/run_reports/2026-07-17-environment-guard.md`.

Branch `impl/env-guard-cooldown` (pushed, commit e2813ee) holds the D-077
response: environment-guard preflight (+`--arm-quiet-mode`), per-run idle
admission gate, cooldown v2, unwaivable `environment_admission_failed` claim
barrier, policy sidecars, contract/doc updates. Design consult (Sol xhigh,
thread 019f7356-32d3) adjudicated and encoded; implementation by Sol xhigh
(thread 019f7362-6627, resumed via codex-bridge after an MCP transport
timeout); session-close scope check SCOPE_OK; full suite green lead-side
(OK, 12 skips). Lead bench fix included: `pmset -g systemstate` parser now
accepts the live "Capabilities are:" form (was null → fail-closed on real
hardware); fixtures pinned to verbatim live output.

RESUME (in order):
1. Relaunch the adversarial review round (was stopped mid-run at checkpoint):
   fresh read-only Sol xhigh, execution lens, over `git diff main...impl/env-guard-cooldown`
   (prompt shape in `.codex-bridge/` prompt snapshots); lead holds the
   contract lens (done for cooldown_gate/claim-barrier/anchor hunks).
2. Triage findings → fix rounds (defect-shaped regressions) → DELTA RE-AUDIT.
3. Live-validate flagged probes during next quiet-window prep:
   `pmset -g systemstate` display-asleep form + screensaver-engaged probe
   while a screensaver is actually running (run report flags
   `live_validation_provisional`).
4. PR per operation-loop §5 gate shape; then re-run suite ABBA calibration
   under the new guard ([QUIET-MAC], needs Ed) — floors D-076 figures for
   suite comparative cells must be recomputed/caveated pending re-run.

Status: **CLEARED 2026-07-11.** Every clearance criterion met: all
checkpoint-#4 resume items executed (P2-044 fix+merge #55; P2-037
audit dispositions → two fix rounds + approved NEEDS_SCOPE expansion +
delta re-audit → #58; P2-043 #57; P2-045 #56); the four held hardening
PRs #50-#53 merged after the cross-stream integration review over the
combined tree (38 pre-merge cross-stream failures caught and fixed; 1
review blocker confirmed by refuters → PR #59; SF1 refuted; SF3 →
queue row P2-049); DOC-008 kernel refreshed at final head (schema v2,
authority field, branch impl/doc008-kernel awaiting PR); bookkeeping
arc complete (run report, C-028 council entry with layer catch-rates
and ~57-invocation spend record, D-064 ratified incl. manifest v3 +
claude-codex-report/v1 + WRITE_SCOPE enforcement; queue reconciled;
consistency sweep; site regen+deploy). All clearance-time opens since CLOSED same day: #59 MERGED, DOC-008
MERGED (#60). Remaining queue heads: P2-049/P2-050/TOOL-01.

## Superseded stop card (CP-5)

Status: **CLEARED 2026-07-09** by the CP-5 resume session. Every
clearance criterion was met: all three worktree diffs lead-gated
(envgate live-gated against the real affine mock bundle) and merged as
PRs #23/#24/#25; PR #22 merged after a fresh final-head pass; the
methodology synthesis and suite_next specs packet adjudicated (CP-6 in
the stream log); all accepted pre-campaign changes landed and merged
(PRs #26/#27/#28); both post-merge integration reviews CLEAN; queue
rank 0 closed. Full record:
`docs/run_reports/2026-07-09-cp5-resume.md`. No stop card is active.

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
  `docs/decision_log.md` remains the policy authority, exit checklists own
  phase completion, and evidence artifacts own scientific truth.
- Retained corpus and session scratchpad evidence are immutable.

## Historical Next-Work Snapshot (superseded 2026-07-15)

The following 2026-07-13 narrative is retained for chronology only. It is not
a live queue or restart instruction; the generated work-selection region is
the sole selector.

The comprehensive whole-project audit is the declared gate (Ed,
2026-07-13): method proposal pending Ed's approval, then the audit runs
and its findings are adjudicated before any further feature work. After
that: Window A in the first clean quiet-machine window (C-019/P2-015-SMOKE,
  (skipped=10)`, lead-run.
- Live lead gates this session (real MLX, Qwen2.5-1.5B via `.venv`, mock
  telemetry): single-prompt + TWO full 48-item jw_mixed suite runs
  (pre-merge old manifests, then final merged main with the REGENERATED
  manifests) — all strict-valid; 48/48 hash-domain closures on the
  real tokenizer; output token ids, model artifact hash, pinned sampler,
  and package versions verified present in the bundles.
- Envelope gate live: honest `envelope_failed[E1]` on the mock affine
  bundle; refusals for wrong-profile/malformed/mixed inputs; exit codes
  0/2/3.
- Bundle pack live: pack → verify(0) → tamper → verify(2).
- Manifest regen: byte-identical double-regen; all realized counts 512;
  new effective shas 855be4e5 (mixed) / 0316283d (sentinel).
- CI green on every merged head (PR #27's first merge-ref run failed on
  a cross-branch fixture interaction; fixed test-side, then green).
- Post-merge integration reviews (both waves): CLEAN, incl. an
  end-to-end mock campaign → strict → envelope-gate → pack → verify flow
  and a D-033 legacy-identity spoof probe that failed closed.
- `validate-bundle --strict` green over all 6 real corpus bundles under
  the new era rule (PR #22 live gate: 6/6 valid, tamper fails named).

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
  `docs/decision_log.md` remains the policy authority, exit checklists own
  phase completion, and evidence artifacts own scientific truth.
- Retained corpus and session scratchpad evidence are immutable.

## Historical Next-Work Snapshot (superseded 2026-07-15)

The following 2026-07-13 narrative is retained for chronology only. It is not
a live queue or restart instruction; the generated work-selection region is
the sole selector.

The comprehensive whole-project audit is the declared gate (Ed,
2026-07-13): method proposal pending Ed's approval, then the audit runs
and its findings are adjudicated before any further feature work. After
that: Window A in the first clean quiet-machine window (C-019/P2-015-SMOKE,
then P2-015 floors, P2-006 baselines), with post-audit [AGENT] heads
P2-050 adjudication, SITE-02, and P2-027 publication prep outside quiet
windows. `TASK_QUEUE.md` remains the ordering authority.

Hardware-gated (unchanged): 2K/2L (P1-006; NV-GATE-2 additions from
C-027 apply at live promotion), wall meter (P1-003), topology (P1-004),
calendar mapping (P1-008).

## Reference Decisions And Blockers (non-selection context)

These pointers retain external-dependency context but do not rank or select
work. The generated region controls task selection.

- Supervisor approval and scope pending (P1-001, R-001 — mitigation
  holding); gates FULL D-016 closure.
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Git author identity on this machine auto-selected as
  `Ed R <edr@Eds-MacBook-Pro.local>`. Amend future commits if a
  different identity is needed.
## Current Do-Not-Do-Yet List

- (satisfied 2026-06-12) The mock bundle/reducer path and report generator
  now exist; dashboard/report work is no longer blocked.
- (satisfied 2026-06-12) The mock lifecycle is runnable, so live
  MLX/powermetrics implementation may proceed once its hardware gates open
  (P1-002 + D-016); follow `docs/phase_2/hardware_slice_implementation_guide.md`.
- (resolved 2026-06-12) Hailo feasibility has a verdict
  (`unsupported_workload`); do not implement a Hailo backend — report it as
  an applicability finding.
- Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in
  D-008; implementation waits).
- Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate
  (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware
  pairings, or borrow-window scheduling before 2M baselines and the Stage
  3.0 verdicts exist (C-007 wording fix; was previously stated as a
  blanket Phase 3 hold that contradicted the queue).
- Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the
  rehearsed runbook exist (R-006).
- Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has
  produced data.
- Do not close D-016 (model selection) without P1-001 supervisor scope or an
  explicit user go-ahead.
- (satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own
  gates (D-016 + `[mac]` install; privileged sample + D-004 sudoers) open —
  build on the post-2N seams (RunContext raw evidence, D-026 markers,
  D-027 rail rows, 2N.3 observed-token fallback).

## Queue Maintenance

At the end of substantial work:

- Update live status, rank, dependencies, and new tasks in
  `docs/process/state_kernel.json`.
- Remove terminal tasks from the kernel only after their owning completion
  evidence supports closure; preserve the dated Completed row here.
- Run `python3 scripts/gen_state.py`; never hand-edit generated queue or
  restart rows.
- Keep hand-authored edits here to policy, completed/history records, and
  non-selection context.

## Intake Batch Owed To The Kernel (2026-07-30/31)

**PARTIALLY FOLDED 2026-07-30.** Six rows —
`COOLDOWN-JOIN-GAUNTLET-01`, `QA-10A-JOIN-OMISSION`,
`QA-10B-EXISTING-RETRY`, `MINT-GENERALIZE-01`, `MANIFEST-CONTRAST-01`,
and `SUPERSESSION-DUP-REFUSAL-01` — were folded into
`docs/process/state_kernel.json` on 2026-07-30; their staged rows were
removed from this table. Of the six, only `MINT-GENERALIZE-01` and
`SUPERSESSION-DUP-REFUSAL-01` remain LIVE as of 2026-08-02: the
gauntlet trio retired with PR #93 and `MANIFEST-CONTRAST-01` with
PR #95 (see the completed table).
`COOLDOWN-JOIN-DA1-01` followed on 2026-07-31 (D-093), in the same pass
that retired `P2-015` to the completed table and closed
`QUEUE-RECONCILE-01`; both of those staged rows were removed too. It was
short-lived as a live row: DA-1 closed later the same day inside the
gauntlet's commit 2 and `COOLDOWN-JOIN-DA1-01` is now retired to the
completed table (PR #91, `67d268a`).

**The rows that remain below are STAGED, not live**, and stay staged by
magistrate scope decision 2026-07-30 (the P2/P3/P4 residue is not
competing for this window's selection). Work selection is the generated
region below; nothing here competes with it until the magistrate folds a
row into `docs/process/state_kernel.json` and runs
`python3 scripts/gen_state.py`. They are recorded here — hand-authored,
outside the generated markers — so the 2026-07-29/30 arc's owed rows
cannot be lost between the ruling and the kernel refresh (kernel refresh
is magistrate-owned).

Sources: `docs/decision_log.md` D-083..D-093; `docs/council_log.md` C-039
addendum + addendum II; the delegated related-work sweep
(`docs/run_reports/2026-07-30-sweep-techniques.md`); the
`splitwise_decode_v1` campaign doc §2
(`docs/phase_2/splitwise_decode_campaign.md`, on main since `27ffc91`).

| ID | Priority | Lane | Task | Evidence / Acceptance | Authority |
|---|---|---|---|---|---|
| QA-1-COOLDOWN-LAUNDER | P0 Safety | [AGENT] | **CLOSED at `16c7af0` (FIX-10, 2026-07-30).** The fail-open declared-occurrence edge the FIX-9 delta re-audit found (a member declaring `bundle_ids: ["x", "x"]` with only one usable `physical_members` row resolved via the one-row fast path without the supersession matcher) is closed by declared-occurrence tallying; both defect-shaped regressions failed pre-fix and pass post-fix. The FIX-10 delta re-audit confirmed this shape closed while finding the two successor edges now carried as the LIVE kernel rows `QA-10A-JOIN-OMISSION` and `QA-10B-EXISTING-RETRY` (folded 2026-07-30; see the generated region below). | Closed: fast path licensed only at declared count exactly 1; regressions in `SupersessionAwareCooldownJoinTests`; lead-verified 48/48 focused. | [D-086/D-088](docs/decision_log.md); FIX-10 delta re-audit 2026-07-30 |
| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
| MDE-ADOPT-01 | P2 Next Slice | [AGENT] | Powered MDE for the **repeatability arm** + workload-sizing inversion: replace the informal repeatability statistic with δ\* = 2.80·σ_D/√m (α = 0.05, power 0.80) over ABBA pair differences, and size the pilot with m ≥ 2.80²·σ_D²/δ². Desk work on existing data; makes the ad hoc "+5 J claim-side" principled. | Floor computation carries a powered MDE for the repeatability arm with its α and power stated. **Hard boundary, do not cross:** this does NOT apply to the systematic arm — RSS composition is valid only for independent random components, and RSS-ing a worst-case attribution bound as if it were an SD is anti-conservative. `max(repeatability, corner) + drift` stays. | [Sweep-techniques top-10 #1 + §5](docs/run_reports/2026-07-30-sweep-techniques.md) |
| MIN-WINDOW-RULE-01 | P2 Next Slice | [AGENT] | Minimum-window rule + loop-to-60 s for short phases: declare a duration-conditional validity domain (N× the powermetrics cadence; SPEC's 60 s reached by looping the workload if shorter) and **fail-close** phases below it. Attacks the attribution-dominated 6–14 J floors directly, since edge error amortizes with window length. | A declared, enforced validity domain with phases below it refused rather than reported. Note the coupling: changing workload duration resizes the science, so any loop-to-60 s change is a pre-registration change and therefore Ed's call (see `FLOOR-WORKLOAD-SIZING-01`). | [Sweep-techniques top-10 #3](docs/run_reports/2026-07-30-sweep-techniques.md) |
| BATTERY-CROSSCHECK-01 | P2 Next Slice | [QUIET-MAC] | Internal dual-instrument cross-check **before** any wall meter: validate powermetrics integrals against an independent on-device channel (battery/SMC drain over long windows; channel-sum vs package reconciliation) and publish the agreement bound **with its validity domain**. Narrows "never externally validated" without a purchase. | A published agreement bound with its stated validity domain. Caution carried from the same memo: embedded telemetry (BMC/SMC) must NOT be treated as a trusted second reference without its own characterization — the bound is a cross-check, not a calibration. | [Sweep-techniques top-10 #4](docs/run_reports/2026-07-30-sweep-techniques.md) |
| REFUSAL-VOCAB-RATIFY-01 | P1 Phase Gate | [AGENT] + magistrate | Ratification question, deferred out of cold gate F1: reordering the separation-validation phases would **alter refusal precedence**, which D-087 placed in "vocabulary-ratification territory". The refusal vocabulary needs a ruling before any reorder is attempted. | A ruling on the refusal vocabulary and precedence, recorded in the decision log; only then may a phase reorder be proposed. | [D-087](docs/decision_log.md); refusal-scope spec v1 (`ea16730`, on main via PR #88) |
| MOCK-SAMPLER-PROV-01 | P4 Polish | [AGENT] | (Cold-gate finding **F2**.) The mock runtime should emit **truthful sampler provenance**; today the integration tests rewrite metadata to inject a sampler — a test-honesty item. | Mock runtime emits real sampler provenance and the metadata-rewriting test helper is deleted. Mitigated meanwhile: mock bundles are already refused at claim binding by `MOCK_TELEMETRY_CLAIM_REFUSAL`, so there is no claim exposure. | [D-087](docs/decision_log.md) (F2 disposition) |
| COOLDOWN-JOIN-FIXTURE-01 | P4 Polish | [AGENT] | (FIX-9 delta re-audit finding **QA-2**.) No repository fixture composes the **real** supersession validator/reader with the cooldown join; the FIX-9 regressions stub the reader, which is adequate for join/matcher behavior and insufficient as custody-path closure. | A real validator-reader-join fixture exercising the composed custody path end-to-end. | [C-039 addendum](docs/council_log.md); FIX-9 delta re-audit QA-2 |
| MINT-TOCTOU-01 | P4 Polish | [AGENT] | (Audit finding **Audit-F1**, adjudicated QUEUE.) TOCTOU between the mint's pre-check and its authenticated artifact read. Requires concurrent mutation of a frozen input; a different signature from the FIX-8 defect class. | Either the read is made atomic with the pre-check, or the exposure is recorded as an accepted limitation with its precondition stated. | Session ledger, staged-mint section; D-087 sibling dispositions |
| FLOOR-ARTIFACT-SHA-PIN-01 | P2 Next Slice | [AGENT] | Review finding **B2** — artifact-SHA pin. **Detail owed:** the finding's text lives in the review packet, not in the session ledger; whoever promotes this row must restate the defect from the packet before it can be READY per the Ready/Shelf rule. | Not yet acceptance-specified — promote to READY only after the B2 finding text is recovered and restated. | Session ledger, F2 disposition paragraph ("register at bookkeeping with … B2 artifact-SHA-pin row") |
| EXACT-SET-REGRESSION-01 | P2 Next Slice | [AGENT] | Review finding **S2** — exact-set regression. **Detail owed** (same caveat as B2): the ledger names the row but not its content. Likely adjacent to D-086 root cause 1 (exact-set vs governed-subset matching when `--evaluation-basis-sha256` is omitted), but that adjacency is **inference and must be confirmed against the packet**, not assumed. | Not yet acceptance-specified — promote to READY only after the S2 finding text is recovered and restated. | Session ledger, F2 disposition paragraph |
| COLLECTOR-NIT-B1 | P4 Polish | [AGENT] | Review finding **B1** collector nit (distinct from the refuted B1 `device.boundary` placeholder finding — do not conflate). **Detail owed**, same caveat as B2/S2. | Not yet acceptance-specified. | Session ledger, F2 disposition paragraph |
| SITE-ROADMAP-PAGINATE-01 | P3 Tooling | [AGENT] | Paginate or shard the site roadmap page: `roadmap.html` emits one card per live kernel row and now sits at 29,620 of the 30,000-byte capsule shard budget (98.7%) after the 2026-07-30 kernel fold — the NEXT intake fold breaks `CapsulePackError`. | `build_site` succeeds with at least 10 additional live kernel rows; no shard exceeds budget; existing roadmap content preserved. | Kernel-refresh finding 2026-07-30 (session report) |
| DOC-RUNSDIR-ABS-01 | P4 Polish | [AGENT] | Tool contract doc note: the extraction CLI's `--runs-dir` **must be an absolute path**. Document it at the tool contract, and consider a fail-closed check rather than leaving it as operator lore. | Doc note landed; optionally a refusal on a relative `--runs-dir` with a regression. | [D-086](docs/decision_log.md) (queued from lieutenant findings) |
| LITREAD-VERIFY-01 | P4 Polish | [AGENT] | Pre-submission verbatim re-verification of the two load-bearing related-work sources against the **PDFs of record**: TokenPowerBench (arXiv **2512.03024**) and "The Illusion of Power Capping in LLM Decode" (arXiv **2605.11999**). Both were read in full text during the sweep, but through WebFetch's extraction model against the arXiv HTML renders. | Every quote and number cited in a submission re-checked against the PDF. **Note the id correction:** TokenPowerBench is 2512.03024; 2605.11999 is the Illusion paper — earlier handoff text conflated the two. | [Sweep-techniques access summary](docs/run_reports/2026-07-30-sweep-techniques.md) |

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
     194 docs/paper/draft-v1.md
     179 CLAIMS_STATUS.md
    7566 docs/decision_log.md
     489 docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md
     214 docs/strategy/2026-08-06-impressiveness-roadmap.md
     134 docs/research_question_registry.md
    1095 docs/research_question_bank.md
      33 docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md
    9904 total

exec
/bin/zsh -lc 'cat docs/paper/draft-v1.md; cat CLAIMS_STATUS.md; rg -n "D-117|Decision D-117|### D-117|## D-117" docs/decision_log.md; tail -n 260 docs/decision_log.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# JouleWise: Detection Floors for LLM Inference Energy Measurement on Consumer Silicon

## 1. Introduction

Energy numbers for large language model (LLM) inference now appear in leaderboards, systems papers, product comparisons, and policy debates. Published estimates for apparently similar queries can differ by an order of magnitude, yet the numbers are rarely accompanied by an error bar that says how small a difference the measurement method can actually distinguish. This omission is especially consequential on consumer hardware. Apple's `powermetrics` utility makes processor power estimates available without a laboratory meter and is therefore attractive for repeated experiments, but, to our knowledge, it has not been validated in published work as an instrument for separating the energy of LLM inference phases. Apple describes its outputs as estimates; treating them as exact readings can turn timing uncertainty at a phase boundary into a spurious energy difference.

The core difficulty is physical as much as statistical. Energy is the integral of power over time. An experiment may repeat consistently and still assign energy to the wrong phase if a power sample near the boundary between prompt processing and token generation is placed on the wrong side. Averaging more repetitions reduces random scatter but does not remove that attribution error. Slow changes in thermal or background state can add a second false difference over a long collection session.

We argue that a software power counter should be treated as a scientific instrument rather than as a logging convenience. The instrument must be calibrated in the same session in which it is used; each reported result must carry a detection floor, meaning the smallest false effect that the calibrated method could plausibly produce under the stated conditions; and the analysis must decline a directional claim when the observed effect cannot clear that floor and its own measurement uncertainty. JouleWise implements this discipline for phase-resolved, single-request LLM inference on one named Apple-silicon machine and software stack. The runtime emits the phase boundaries because it drives the workload, while `powermetrics` supplies the power samples integrated between those boundaries.

This scope is deliberately narrow. A measurement characterizes one physical unit, operating-system build, runtime and library stack, model artifact, quantization, tokenizer, sampling policy, single-request execution policy, telemetry backend, and measurement boundary. It does not establish that an Apple hardware class or vendor is more efficient than another platform. Without an external power meter, absolute values remain internal to the named `powermetrics` system-on-chip boundary; same-boundary contrasts can still be scientifically useful when they pass the calibration and floor gates. Gross joules per request are the primary energy metric. Joules per prompt or output token are tokenizer-scoped companion metrics and are never treated as tokenizer-independent work units.

This paper makes the following contributions:

1. (C-i) an in-window calibration method that measures timing-attribution error for phase-resolved energy integration;
2. (C-ii) detection floors composed from measured repeatability, worst-case attribution, and measured drift — published with every result;
3. (C-iii) a fail-closed collection protocol (admission gates, ABBA ordering, custody chains, pre-registration) with its refusal log as evidence;
4. (C-iv) full instrument characterization: linearity, null response across magnitudes, empirical floor verification, phase-attribution causal consistency, drift/settle;
5. (C-v) demonstration measurements: phase-resolved J/token for two model sizes with a pre-registered contrast [+ quantization ladder if window budget allows];
6. (C-vi) open tool + hash-bound reproducible artifacts.

## 2. Background and the gap

### Energy-benchmarking rules

The first relevant lineage is formal energy benchmarking. MLPerf Power and the associated Standard Performance Evaluation Corporation methodology treat uncertainty and validity as properties of each measured run. They require a qualified analyzer, uncertainty evaluated at the observed load, fixed measurement ranges, synchronized clocks, sufficiently long intervals, invalid-sample accounting, and explicit treatment of battery-backed systems [MLPerfPower]. These rules establish an important principle: a benchmark result is not valid merely because the meter has a specification sheet. The evidence recorded during the run must show that the measurement operated inside its accepted conditions. These standards, however, assume external instruments and data-center-style workloads; they do not provide a method for validating phase boundaries reported by a software counter on a consumer system.

### Software-counter validation

The second lineage validates software-visible energy counters against external power. Intel's Running Average Power Limit (RAPL) counters have been studied through lag alignment, regression against wall power, counter-resolution tests, sampler-overhead audits, and thermal controls [RAPLInAction]. Jay and Ostapenco's CCGRID 2023 study likewise shows that the gap between a software meter and wall power can depend on load rather than behave as one fixed offset, and it refrains from component-level conclusions when no reference instrument observes the component [JayOstapenco]. This work provides a strong model for whole-machine scale validation. It does not define a detection limit for a reported effect, does not validate `powermetrics` on Apple silicon, and cannot by itself establish whether software samples were assigned to the correct LLM phase. A wall meter observes a total; phase attribution needs a separate timing experiment.

### LLM energy studies

The third lineage measures LLM energy across models, hardware, and workloads. TokenPowerBench reports prompt-processing and token-generation energy with phase-appropriate token denominators; ML.ENERGY, Silicon Showdown, and Intelligence-per-Watt broaden empirical coverage across deployed systems [TokenPowerBench; MLENERGY; SiliconShowdown; IntelligencePerWatt]. This breadth makes inference energy visible, but the nearest studies do not jointly characterize counter timing, repeatability, drift, and the minimum resolvable effect. Phase labels are consequently easy to read as exact even when the method does not report the boundary events, alignment uncertainty, or a floor below which a difference should be refused.

The specific gap is therefore not another energy table. To our knowledge, no published work combines phase-resolved LLM energy on consumer silicon, a per-measurement error budget, and validation of `powermetrics` timing attribution under its named measurement boundary (as distinct from validating its absolute counter gain or whole-system energy scale, which would require an external meter). JouleWise fills that gap by making instrument characterization and refusal behavior the primary result; model comparisons are demonstrations of what the characterized instrument can and cannot resolve.

## 3. In-window calibration method (C-i)

### Measurement model and boundary

JouleWise measures one sequential request at a time. Prompt processing (often called *prefill*) converts the input sequence into the model's internal state; token generation (often called *decode*) produces output tokens from that state. Because the experiment controls the runtime, it records the start and stop of these phases directly in the runtime event stream rather than inferring them from shapes in the power trace. The reducer then integrates the named `powermetrics` system-on-chip power channels between each pair of phase events using trapezoidal integration.

The runtime and the telemetry sampler do not share a perfect clock. Operating-system launch latency, timestamp anchoring, and the sampler's averaging behavior can shift an apparent edge. A phase-energy estimate must therefore be an interval, not only a point. The calibration asks a concrete question: if software commands a load pulse at a known time, how far can the rising and falling edges of that pulse appear displaced in the sampled power trace?

### Bracketed pulse-train calibration

Immediately before and after every claim-bearing collection window—that is, a window eligible to support a reader-facing scientific claim—JouleWise runs a fresh pulse-train calibration under the same machine, operating-system, power-supply, and telemetry state as the science workload. The current protocol commands 59 graphics-processor matrix-multiplication pulses. Their durations are fixed in advance, their gaps follow a deterministic low-discrepancy schedule rather than a single repeated period, and quiet baselines of at least 4.5 seconds separate the fitted regions. The varied schedule reduces the risk that the calibration accidentally locks to the telemetry sampler's cadence. The 59-pulse design supports the pre-registered nonparametric 95/95 bound: a conservative bound intended to cover at least 95% of the calibration population with 95% confidence under the stated transfer assumptions.

For each pulse, the estimator compares the commanded interval with the observed power plateau and fits the start-edge and stop-edge lags independently. This distinction matters. A common shift of both edges may leave pulse energy nearly unchanged, while an early start combined with a late stop can add energy at both boundaries. The calibration therefore retains a bound for the instrument's edge-placement error rather than collapsing the evidence to one best-fit lag.

Each science member, meaning one recorded workload run, also carries a local bound on how its runtime clock is anchored to the trace, including the observed span between wall time and a monotonic clock that is not adjusted by network synchronization. For a reported phase, the analysis combines the member-local common shift, the calibration edge bound, and the clock-span term. It evaluates the energy integral at all four combinations of early and late start and stop edges, while scanning the allowed common shift exactly. The minimum and maximum of those integrals form the admissible energy interval. The physical intuition is simple: the interval asks how much energy could move into or out of the phase if both boundaries were placed at their most adverse calibrated positions.

The pre- and post-window calibrations form a bracket around the measurements. Both must be authenticated, fresh, and causally outside the science interval. The operative bound is the larger of the two. Separately, the absolute difference between the pre- and post-window calibrations is screened against a derived bracket-drift limit of about 10.82 ms: a small repeatability-only excess is propagated into every floor and claim, while an identified systematic defect cannot be absorbed by that budget. If the post-window bound is larger than the one used when a member was first reduced, the member must be re-reduced through the pre-specified path with the wider bound or it cannot support a claim; metadata is never patched to make the bounds agree. A pre-flight level screen also runs before the first science member. It rejects a calibration whose fitted lag is outside the previously characterized family, such as a graphics-processor frequency ramp that the pulse model could mistake for a timing shift. A retry is allowed only after a specific cause is identified and removed, within the retry count frozen before collection. Repeating merely until a favorable calibration appears would be selection on the outcome.

This procedure validates timing attribution, not the gain of the power counter. The pulses are graphics-processor matrix multiplications under a relatively light central-processor load, so transfer of their timing bound to sustained mixed-load inference is an explicit assumption. The in-session bracket, empirical floor probes in Section 6, and stack-specific labels constrain that assumption; only an external meter could additionally validate the absolute whole-system scale.

## 4. Detection-floor composition (C-ii)

A *detection floor* is a practical guard against false observed effects for one declared condition family: the same telemetry backend, metric, window type, workload profile, and stack identity. One such family forms a measurement cell. The floor is not a claim that a population percentile has been estimated exactly. JouleWise computes separate absolute and comparative floors and takes their maximum for the cell. An absolute floor measures how far repeated measurements of the same condition wander from their mean. A comparative floor measures the apparent difference between labels that are deliberately made identical and collected in A/B/B/A order.

### Repeatability and false-comparison guards

For an absolute cell with energies \(E_i\), residuals \(r_i=E_i-\bar E\), sample standard deviation \(s_r\), and \(n\) valid bundles, the point guard is

\[
F_{\mathrm{abs,point}}=\max\left(\max_i |r_i|,
t_{0.975,n-1}s_r\sqrt{1+1/n}\right).
\]

For \(n\) valid null-comparison blocks with within-block deltas \(\delta_i\), the corresponding guard is

\[
F_{\mathrm{cmp,point}}=\max\left(\max_i |\delta_i|,
|\bar\delta|+t_{0.975,n-1}s_\delta\sqrt{1+1/n}\right).
\]

The observed maximum protects against a false effect already seen; the Student-*t* prediction term protects against one additional observation under the repeatability model. Small samples receive a pre-registered guard factor, and fewer than five valid bundles or blocks are treated only as development evidence, not as a claim gate. Items within one bundle are not counted as independent repetitions.

### Worst-case timing attribution

Point repeatability is not the full floor. Each energy value is an interval from the timing calibration in Section 3. The floor computation evaluates the complete point-floor estimator over the joint corners of all member intervals that pass the admission and evidence gates, then takes the largest value. For a null A/B/B/A block, the four signed member intervals are propagated through the contrast together. This corner calculation is deliberately conservative: a systematic boundary-placement error is not independent Gaussian noise, so adding it in root-sum-square form would understate the worst case. The published floor is no smaller than the largest accepted attribution width.

This calculation revealed a stable and important limitation of the present instrument. Ordinary repeatability is smaller than the uncertainty caused by placing samples at phase edges: approximately one joule can be assigned to the wrong phase when a roughly 30 ms timing uncertainty meets a power change of roughly 33 W. The instrument is therefore *attribution-limited*, not *noise-limited*. More repetitions can refine the repeatability term, but they cannot average away this boundary-placement limit.

### Measured, never-zero drift allowance

Drift is a slow change in the machine or measurement response over the collection window. It is measured rather than assumed away. Each prospective window includes three fixed reference runs at the start, one at the midpoint, and three at the end. Gross energy and idle-subtracted energy are treated as separate claim families (idle-subtracted energy is gross energy minus the measured idle mean power multiplied by the phase duration). For each family, the protocol derives a repeatability bound from a settled reference corpus and measures the largest excursion among the start mean, midpoint, and end mean. The allowance is

\[
A_{\mathrm{drift}}=\max(\text{observed start/mid/end excursion},
\text{derived reference-repeatability bound}).
\]

Consequently, a passing drift screen never means zero drift. The allowance remains positive even in an exceptionally stable window, and the midpoint protects against an interior excursion that similar endpoints would miss. No duration-scaling law is applied because the available evidence does not identify a physical law relating drift to elapsed time.

For each absolute or comparative component, the guarded, corner-widened value is increased once by its matching drift allowance. The operative floor for a cell is then

\[
F_{\mathrm{cell}}=\max(F_{\mathrm{abs}},F_{\mathrm{cmp}}),
\]

not their sum. Cross-window components keep their own calibration basis and allowance; an allowance is never added again at the cell or reporting level. Operative floor values and their full decomposition for each demonstration stack are withheld here until the corrected artifacts are issued: **[RESULT PENDING RE-MINT]**.

### LABELLED publication and the effective decision bar

When timing attribution dominates, the floor remains publishable only through the **LABELLED** path. Every artifact and reader-facing result must identify the limit as attribution-limited, publish the corner-widened value rather than the smaller point diagnostic, retain the point-only repeatability number as a non-publishing diagnostic, and carry `floor_source = E_clock_anchor_shift_bound_j`. This field names energy uncertainty caused by shifting the phase edges within the calibrated clock-anchor bound as the dominant term. The label prevents a precise repeatability number from masquerading as the instrument's total resolving power.

The floor is only one side of a claim decision. The calibrated floor bounds a false effect produced by the calibration condition; the confidence or decision interval for the particular measured contrast separately carries that contrast's timing-attribution uncertainty. These are distinct uses of the same physical uncertainty and both are required. The effective bar is therefore

\[
\text{effective clearable effect}=F_{\mathrm{cell}}+B_{\mathrm{claim}},
\]

where \(B_{\mathrm{claim}}\) is the claim-side measurement bound. For the measured phase-contrast regime, this combined bar is approximately 5 J. Neither term may be removed as an apparent double count. Effects below the floor are reported as *not resolvable*, not as zero, equal, or evidence of no difference. A directional claim is made only when the effect and its interval clear the applicable bar.

## 5. Fail-closed collection protocol (C-iii)

*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is one uninterrupted two-to-four-hour window with one power state, one instrument identity, fresh calibration before and after, a fresh drift-bound corpus, and one verdict over the exact member set. Work that does not fit with at least a 20% failure margin is split prospectively into another independently calibrated window.

### Pre-registration and admission

Before quiet time, the operator freezes the run identifiers, membership, stage order, comparison definitions, calibration retry count, acceptance thresholds, extraction specification, code revision, and an initially empty waiver list. Every configuration is validated and dry-run against a fresh output root. These choices are made before outcomes are visible. Pre-registration here is executable: the launcher and final verifier check the frozen values rather than relying on a narrative promise.

Each stage then passes admission gates immediately before measurement. The approved power supply and power policy must be unchanged; displays must be asleep; the screensaver and low-power mode must be off; thermal pressure must be nominal; and central- and graphics-processor activity must meet the quiet-state criteria. Known background work is allowed to finish before the window, followed by a settling interval, rather than being ignored during analysis. Runtime and telemetry identities, clock anchoring, sample cadence, calibration freshness, and post-run environment observations are also checked. No environment override can produce a claim-bearing member.

### Counterbalanced order

Comparisons use A/B/B/A blocks, abbreviated **ABBA**. Conditions A and B are measured in the order A, B, B, A, with ordinary cooldown between members. Averaging the two outer A observations and the two inner B observations cancels a linear time trend within the block to first order. For null-floor calibration, A and B are aliases of the exact same configuration and payload, so any nonzero block delta is a false comparative effect. For scientific contrasts, the A and B definitions are frozen in advance, and the contrast is computed within each block before blocks are aggregated. ABBA reduces common drift; it does not replace the measured whole-window drift allowance.

### Evidence custody and refusals

Every member is a self-contained bundle of configuration, raw power trace, runtime events, environment observations, and derived summary. Cryptographic hashes bind those files to the campaign manifest. Failed or interrupted artifacts are never deleted or overwritten. An occupied retry slot is moved to a quarantine area outside the active runs root; the exact member is recollected only under an allowed retry; and an append-only supersession record names which occurrence governs. Two present bundles for one occurrence refuse. The final whole-window verdict binds the exact member-occurrence set, calibration bracket, policy, and drift evidence by hash, so a later consumer cannot silently select a more favorable subset.

Collection does not continue indefinitely through environmental interruptions. Each stage attempt stops at its first member failure, and after the same cause fails a window stage for the third time the window itself closes rather than being retried; in actual operation, nights with three environmental member interruptions were closed and preserved as salvage rather than repeatedly retried. The surviving data may remain diagnostic, but it becomes claim-bearing only if the pre-registered verdict and extraction rules accept the exact resulting basis. This abandon-after-three rule limits outcome-dependent retrying and makes the cost of a noisy environment visible.

The custody chain continues after collection. The immutable corpus is backed up before extraction. The extractor re-authenticates member hashes, required files and cross-file consistency, calibration identity, environment admission, complete campaign membership, cooldown evidence, phase metric identity, and the whole-window drift allowance. It excludes or refuses a cell according to the frozen rules; missing uncertainty never becomes zero. The current artifact boundary is stated honestly: until floor artifacts are independently bound to their source extraction, a claim-bearing floor must be produced by protocol-controlled extraction in the same controlled custody session as the analysis that consumes it. A standalone floor file is not independently claim-licensing.

The refusal log is part of the evaluation, not an embarrassment to omit. It records contaminated members, out-of-family calibration, stale drift evidence, unresolved clock anchors, duplicate occurrences, and below-floor effects. In one real end-of-night case, the governed re-evaluation refused a window because a member's internal clock alignment could not be resolved. Independent adjudication found that refusal correct. The result remained non-claim-bearing: an example of the fail-closed design working as intended, not a software defect to be bypassed.

## 6. Instrument characterization (C-iv)

Instrument characterization asks whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload is therefore a test signal, not yet the scientific finding. All tests retain the same calibration, admission, custody, and floor rules as the later demonstration measurements. Existing campaign fragments are not promoted where the governing whole-window verdict did not pass; the table marks the required claim-bearing results explicitly.

| Property | Characterization method | What a passing result would establish | Claim-bearing result |
|---|---|---|---|
| Linearity | Hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. Regress gross request and decode energy on the runtime-observed output count; inspect residual structure as well as the fitted slope. | Energy responds proportionally over the tested dynamic range, and the fitted per-token slope can serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
| Null response across magnitudes | Run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes. Evaluate the paired deltas against zero and against the predicted decision envelopes. | The comparison path does not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range are contained by the error model. A non-significant result alone is insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
| Empirical floor verification | Use the pre-registered linearity slope to create micro-deltas with predicted effects near 0.5, 1, 1.5, and 3 times the declared floor. Test positive and negative directions in counterbalanced blocks. | Sub-floor effects are refused while sufficiently super-floor effects clear in both directions. This is an operational check of the detection boundary, not a validation of the counter's absolute gain. | **[PENDING WINDOW C]** |
| Phase-attribution causal consistency | First compare the sum of separately integrated phase energies with the gross energy over their enclosing request. Then vary output length while holding prompt tokens fixed and fit the slope of prefill energy against output length. | Phase accounting is additive within its stated boundaries, and energy assigned to prefill does not acquire a systematic dependence on work that occurs later in decode. Together these tests challenge both missing energy and cross-phase leakage. | **[PENDING WINDOW C]** |
| Drift and settling | Place long controlled holds and fixed reference workloads through the window, including start, midpoint, and end references. After operator or stage activity, repeat the reference while recording the time required for thermal and admission observables to stabilize; compare it with the 180 s operating convention. | The measured drift trajectory is contained by the published allowance, and the chosen settling time is supported or revised from observed recovery rather than convenience. Endpoint agreement alone is not enough if the midpoint reveals curvature. | **[PENDING WINDOW C]** |
| Between-session stability | Repeat calibrations, null blocks, and floor cells across at least three sessions or days with the full stack identity recorded. | The calibration and floor are stable enough to reuse only under their declared freshness and identity rules, or reveal that a new session must mint a new floor. | **[PENDING WINDOW C]** |

Linearity and the null ladder test complementary failure modes. A smooth response can still carry an offset, and a zero-centered null can coexist with a nonlinear scale. The micro-delta experiment then closes the loop by using the measured slope to place effects deliberately below and above the declared decision boundary. Success requires the instrument to refuse the former and resolve the latter in both directions; merely observing larger effects with larger workloads is not sufficient.

The causal tests address the most important phase-specific risk. Additivity checks conservation inside the declared request boundary: phase intervals should reconcile with the enclosing total, subject to explicitly labeled setup or gap intervals. Causal invariance checks direction: holding the prompt fixed while increasing later decode work should not change energy attributed to earlier prefill. A nonzero prefill slope would indicate boundary leakage, shared-state coupling that invalidates the simple phase model, or both; it would narrow the claim rather than be explained away.

Temporal characterization separates slow drift from thermal settling. Start, midpoint, and end references expose whole-window curvature, while post-transition references estimate how long the system takes to return to its admitted state after operator activity or stage churn. Repetition across days tests whether one session's calibration is representative under identical recorded bindings. Internal channel-sum versus package reconciliation is retained as a secondary consistency check. External wall-power regression remains conditional on a suitable meter and would validate totals only; the pulse experiment remains the evidence for phase splitting.

Every resulting figure and table will identify the physical unit, operating-system version and build, runtime and relevant library versions, model artifact hash, quantization, tokenizer identity, sampler and output policy, configured and realized batch/concurrency policy, measurement boundary, and telemetry backend. Silent omission is not permitted. Measurements support stack-specific conclusions only; independent replication or a calibrated boundary bridge would be required for hardware-class, vendor-class, or cross-boundary rankings.

## 7. Demonstration results (C-v)

**[RESULT PENDING RE-MINT]**

This section will report phase-resolved gross joules per request for two model sizes, with tokenizer-scoped joules per prompt token and per output token as companion metrics. It will contain the pre-registered same-boundary model-size contrast, its interval, the complete floor decomposition, the claim-side bound, the effect-to-floor ratio, and the final resolvable/unresolved verdict. No demonstration energy value from the superseded mint is carried into this draft. A quantization ladder will be included only if it is collected under its own stack-specific floors and the frozen window budget permits it.

## 8. Related work

### LLM inference energy measurement

TokenPowerBench provides one of the closest reporting structures: it separates prompt-processing and token-generation energy, uses phase-appropriate token denominators, and groups results by context length [TokenPowerBench]. Its disclosed method, however, does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation, and continuous batching makes an “active phase” label difficult to interpret when requests overlap. JouleWise adopts phase-specific reporting but restricts its primary scope to one sequential request, where runtime-emitted phase boundaries are well posed and can be calibrated.

The Illusion of Power Capping in LLM Decode samples graphics-processor power, integrates those samples, repeats configurations, and cross-checks sufficiently long operations against a separate hardware energy counter [IllusionPowerCapping]. This is a stronger measurement template than an unqualified software reading. Its counter agreement, run-to-run variation, snapshot fallback, and timing alignment nevertheless remain separate diagnostics rather than one bound on the reported effect, and its long sweeps do not use a drift-control ordering. JouleWise composes those classes of uncertainty into a decision rule for each contrast.

Apple-focused system comparisons reinforce the need for boundary labels. Silicon Showdown compares a graphics-board boundary on one platform with a whole-system-on-chip `powermetrics` boundary on Apple hardware, while runtimes and precision stacks also differ [SiliconShowdown]. Intelligence-per-Watt and ML.ENERGY similarly emphasize breadth across deployed inference configurations [IntelligencePerWatt; MLENERGY]. Such studies answer valuable systems questions, but unlike boundaries and software stacks cannot by themselves support a hardware-class causal ranking. JouleWise therefore makes the named stack and measurement boundary part of every result and prioritizes within-boundary effects.

### Software power counters and measurement standards

RAPL in Action established a validation agenda for commodity software counters: align lag before comparing streams, model wall power rather than assuming identity, account for temporal correlation, warm the system, measure sampler overhead, and inspect update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. Jay and Ostapenco likewise regress software readings against wall power and show that disagreement varies with load; they avoid claims about subtotals that the reference meter cannot observe [JayOstapenco]. JouleWise follows this epistemic boundary. A future external meter could test total gain and load dependence, but it would not validate how a total is divided between prefill and decode. The in-window pulse train addresses that distinct question.

MLPerf Power and SPEC require load-specific analyzer uncertainty, fixed ranges, clock synchronization, minimum intervals, invalid-sample accounting, and controlled battery behavior [MLPerfPower]. JouleWise translates their per-run reject-on-missing-evidence principle to a consumer software counter. The difference is that its principal uncertainty is not only an analyzer specification; it includes whether samples at a software-defined phase edge belong inside or outside the integral.

### Metrology and experimental discipline

Prospective paired minimum-detectable-effect methods estimate the smallest effect a planned paired study has adequate statistical power to find. They size the study from the variance of paired differences and can impose a one-way prior ratchet: observed variability may raise the planned threshold but may not lower it after outcomes are seen [PairedMDE]. JouleWise uses that logic for prospective workload sizing, but it does not treat the worst-case attribution term as independent random noise. Root-sum-square composition would be anti-conservative for a systematic edge-placement bound. Instead, the analysis maximizes over calibrated edge positions, measures drift with bracketed references, and publishes the resulting floor with the effect.

This emphasis changes the role of failed runs. A rejected admission, stale calibration, contaminated member, or below-floor contrast is evidence about the instrument's operating domain. Hash-bound raw traces, runtime events, configurations, supersessions, verdicts, and pre-registration records make that evidence re-reducible. The refusal is retained rather than disappearing behind a final average.

### Split and disaggregated inference

Split, or disaggregated, inference places prompt processing and token generation on different devices and transfers intermediate state between them. Revisiting Disaggregation Energy reports that the energy outcome depends on load, baseline, and transfer conditions on its evaluated two-graphics-processor node [RevisitingDisaggregationEnergy]. DualScale studies phase placement and per-phase power control on homogeneous server hardware [DualScale]. Prima.cpp includes whole-run energy and communication accounting but not a per-stage energy split [PrimaCPP], while SplitZip characterizes lossless transfer compression without making an energy claim [SplitZip].

JouleWise does not claim a new split scheduler in this paper. Split inference is instead a demanding future demonstration of the instrument because it introduces two physical boundaries, a transfer interval, and clock alignment across devices. A valid comparison would have to measure both ends, name each boundary, and clear a pre-registered floor or calibrated bridge. Whether splitting saves energy remains an empirical outcome; the reusable contribution is a method that can issue, qualify, or refuse the result.
# Claims Status

**The single standing home for "what can we actually claim right now."**
Every scientific number the project can publish, is holding, or must not
repeat — with its exact validity state and blocker. Refresh this file
whenever claim-bearing state changes (a verdict, a mint, a merge in the
D-095 chain, an adjudication); quote verdicts as issued, never
reinterpreted. Companion docs: `RUN_STATE.md` (session pointer),
`WINDOW_STATUS.md` (machine state), `docs/decision_log.md` (policy).

Last updated: **2026-08-07** (D-117: the historical re-mint path is
SUPERSEDED — structurally closed at main after the D-116 issuance
(candidate discovery excludes import-marked receipts by design); the
claim path forward is THREE PROSPECTIVE WINDOWS — fresh 1.5B decode
floor, fresh 7B decode floor, fresh decode contrast — live-bracketed
under the issued acceptance regime, with prefill floor cells riding
both floor windows. Prior "re-mint conditions" in this file are
historical: D-109 landed (PR #100), issuance executed (D-116, PR #109),
validator pin widening landed (PR #105). Full record:
`docs/process_traces/2026-08-06-d110-remint-fork/`.)

Earlier header (2026-08-03 night, for the record): D-108/D-109 ruled +
executed; D-110 made mint #1 retroactively NON-CLAIM-BEARING; window B
re-evaluation STOPPED → D-112; mint-1 re-derivability proven
byte-identical; report: `docs/run_reports/2026-08-03-16h-runway.md`.

---

## 1. VALID — minted, mainline, citable

**NONE at this checkpoint.** D-110 (2026-08-03, sweep finding RT-1)
made mint #1 and every number derived from it retroactively
non-claim-bearing: its floors embed a never-zero allowance of ZERO
where D-102 pin 3 mandates +max(drift, 0.010818 s) (~+43% on the a10
operative bound). The previously-listed values (operative 7.377086 J;
a10 components 3.823787 / 3.592138 J; window C comparative 7.377086 J)
move to §5 until the re-mint. The DERIVATION toolchain itself is
proven honest: the full pinned replay (2026-08-03) reproduced both
extraction reports, the artifact, and the statement BYTE-IDENTICAL
(`docs/process_traces/2026-08-03-q1-remint-bytecompare/`). The taint is
semantic (the selector the era used), not derivational.
**2026-08-07 (D-117):** the historical re-mint order is SUPERSEDED —
all three former re-mint conditions completed (D-109 via PR #100;
issuance via D-116/PR #109; pin widening via PR #105) and the FIRST
consumption attempt then proved historical consumption structurally
closed at main. Replacement: three prospective windows (D-117 cl.2);
the never-zero allowance correction binds their mints. All four PASSED
window verdicts remain untainted (sweep RT-5), but pre-genesis windows
CANNOT be claim-consumed — their role is diagnostic and
rule-establishing only.

**Standing measurement fact (D-078 cl.11, Ed-ratified):** the instrument
is attribution-limited (~1 J), not noise-limited (~0.3 J). Floors
publish LABELLED with the widened number; the effective clearable
effect for phase contrasts is floor + claim-side bound ≈ 5 J. No
instrument-tightening program.

## 2. EVIDENCE-BEARING — collected and verdict-PASSED, awaiting a specific gate

| Candidate claim | Value (prose-only until gated) | Window / verdict | Blocker |
|---|---|---|---|
| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
| **1.5B-vs-7B decode contrast** (demonstration study #1) | **Registered claim metric (frozen v3 manifest): `phase_energy_j.decode`, 7B−1.5B = 141.29 J per block.** The widely-quoted 146.730349 J (σ 0.241 J, n=10 ABBA) is the `idle_subtracted_energy_j` whole-request DIAGNOSTIC — quote it only labelled as such, never as the claim (sweep DC-1; both reproduce byte-exactly from disk). | `window_contrast_20260730`, **PASSED** | **RE-SCOPED by D-117 (2026-08-07):** `window_contrast_20260730` is pre-genesis and cannot be claim-consumed; values are DIAGNOSTIC and the design template for the fresh contrast window (D-117 cl.2). The D-095 chain now runs through the prospective windows' mints. |

## 3. COLLECTED — verdicts FAILED as-issued; adjudication RULED (D-100, 2026-08-01)

The machinery adjudication is complete (MET-VERDICT-ADJ-01 → D-100 cold-
gate synthesis). Both verdicts **stand as issued, permanently by
construction**: any licensed re-evaluation appends a NEW row under
`consumption_semantics_id: salvage_dangler_exclusion_v1` with a new
pinned basis; the original FAILED rows are never edited and govern
default consumption. Outcomes per window:

- **Window A: permanently non-claim-bearing.** Its only post-cal retry
  binds a T1-incompatible power-policy identity (immutable evidence; the
  machinery's rejection was CORRECT), so no calibration bracket can ever
  form. C1 re-collects in a future window.
- **Window B: TERMINALLY CLAIM-RETIRED (D-113, Ed ruling 2026-08-05):
  RETAINED_IMMUTABLE / PERMANENTLY_NON_CLAIM_BEARING.** Ed chose
  abandonment over salvage ("soundness and quality of the project and
  claims above all"): no re-evaluation or claim consumption will ever
  occur; the WB-specific D-100/D-106/D-108 license chain is retired
  (general machinery survives for other windows);
  `WINB-R06-DISPOSITION-01` closes ABANDONED_FOR_FRESH_COLLECTION;
  labelled read-only forensic/diagnostic use remains permitted ("Window
  B, original verdict FAILED, D-113 claim-retired, non-claim
  evidence"). Every still-desired WB claim component re-collects fresh
  beginning Window C — no WB member enters a replacement claim basis.
  The F7 scope question is ANSWERED: whole-window voiding is affirmed
  as the current semantics (a cell-scoped alternative only via the
  D-083 cold gate; not built). Historical record of the 2026-08-03
  attempt below. The whole chain executed: D-108 ruled
  (clause (c) retired), row `D100-BII-BINDING-01` CLOSED (PR #99 +
  clause-(d) three-occurrence digest-bound re-record), closure +
  membership-binding artifacts authored and dry-authorized, D-093 scan
  clean 1/1, frozen corpus verified byte-identical (210+4 files, zero
  mismatches). The governed re-evaluation then REFUSED pre-verdict:
  survivor consumption failed on `mtadd-p2048o0128-r06`'s
  collection-time clock-anchor failure (`native_intersection_empty`) —
  the cold gate ruled this CORRECT fail-closed machinery (classification
  (i), convergent instruments; record
  `docs/process_traces/2026-08-03-winB-reeval-stop/`). No licensed
  channel removes r06 (exclusion cap spent on r08; not a dangler;
  waivers forbidden), and the NEG-8 drift bound expired 2026-08-02, so
  no PASS path exists under the license as drawn. Original FAILED
  verdict untouched. The WB NEG-8 bound re-mint obligation is MOOT
  under D-113; the near-run-time freshness rule continues to bind
  every future window (runbook + D-078, by cross-reference).

| Paper claim | Campaign | Collected | State after D-100 |
|---|---|---|---|
| **C1 — linearity** | `linearity_ramp` | **40/40** (window A) | DEAD for claims (window A permanent FAIL); re-collect (window C/D); data usable as design input (micro_delta slope) + corroboration diagnostics only |
| **C2 — null ladder** | `null_ladder` | o0128 + o0512 collected in window B — **returned to uncollected-for-claim state (D-113)**; o2048 never collected | Re-collect ALL of C2 fresh (window C, or split per the frozen plan); no WB member enters a replacement claim basis |
| **C3 — micro-delta** | `micro_delta` | not collected | Plan is draft-pending-slope by design; slope fit may consume window A ramp as DESIGN input (not a claim) |
| **C4 — additivity** | `additivity_shapes` | 23/24 single-root collected in window B — **returned to uncollected-for-claim state (D-113)**; 21/24 window-A corroborating remain labelled non-claim diagnostics | Re-collect C4 fresh (window C/D per the frozen plan). F7 ANSWERED by D-113: whole-window voiding affirmed as current semantics; no cell-scoped salvage |
| **C5 — long holds** | `long_holds` | not collected → window C | — |

## 4. Standing gates on EVERY claim consumption

1. ~~D-088 cl.3(c) three-check bench scan~~ — **LIFTED 2026-08-02**: the
   cooldown-join gauntlet closed (commit 3 merged, PR #93 `cb860e1`);
   the landed machinery now enforces these properties structurally
   (result-map completeness, counting domain, authenticated v2
   discrimination).
2. ~~D-093 raw-vs-validated supersession-record scan~~ — **LIFTED
   2026-08-02** with the gauntlet's close per its row contract; the
   validated reader boundary (PR #91) plus the commit-3 authenticated
   catalog own raw-record visibility permanently.
3. Verdicts consumed as issued; overrides only via the cold-gate path
   with written dissent Ed sees. (UNCHANGED — permanent.)
4. NEW (D-105): while `C3-RECOGNIZER-EXACT-01` is open, the tail
   recognizer's accepted set may only shrink, and the custody sidecar +
   writer-side key assertion may not be weakened.

## 5. DO NOT QUOTE — retired, void, or wrong-as-stated

- **ALL mint #1 floors as claims (D-110, 2026-08-03): operative
  7.377086 J, a10 components 3.823787 / 3.592138 J, window C
  comparative 7.377086 J** — retroactively non-claim-bearing (zero
  allowance where D-102 pin 3 mandates +max(drift, 0.010818 s));
  citable again only after the ruled re-mint under the repaired
  selector.
- **146.730349 J as "the contrast claim"** — it is the
  idle_subtracted_energy_j whole-request diagnostic; the registered
  claim metric is phase_energy_j.decode = 141.29 J (sweep DC-1). Either
  number only as prose with its metric named, neither as a gated claim
  yet.

- **3.17 / 2.94 J** floors — pre-allowance attribution-width
  diagnostics only (D-079 cl.5).
- **3.592138 J as "the decode floor"** — it is the isolated absolute
  component; the operative floor is 7.377086 J (D-084).
- **4.923 J item / 24.62 J suite** comparative floors — Ventura
  screensaver contamination artifacts (2026-07-17 campaign).
- Old window B (`04_phase_prefill_abba`) figures — verdict FAILED
  (`instrument_calibration_mismatch`, GPU DVFM ramp aliasing), corpus
  preserved but not claim-bearing.
- All pre-repair (pre-D-078) powermetrics corpora for claim use —
  time-anchor defect (D-078 soundness gate).
- Window A/B metrology numbers as claims — see §3 (verdicts FAILED as
  issued; window A permanently dead for claims; window B only via a NEW Ed ruling (D-112: the re-evaluation was performed 2026-08-03 and correctly refused; license exhausted as drawn).
- **Window A C1 linearity figures in any claim context** — the corpus
  is design-input/diagnostic only, permanently (D-100 + the immutable
  T1-incompatible retry).

## 6. Instrument findings queued for the paper (not claims yet)

- **Clock-anchor knife-edge** (2026-08-01 Sol consult, accepted): at
  197 s capture length the native-second intersection margin is ~±1 ms
  and the unmodeled wall/monotonic rate (~−12 ppm ≈ 2.3 ms/capture)
  exceeds it; pass/fail is quantization-phase luck. Desk item:
  rate-aware anchor design; directly publishable as a metrology
  limitation/finding.
- **Quiet-state definition**: validated windows now include suspended
  cloud sync (bird-SIGSTOP protocol) — claims describe that controlled
  state, not an arbitrary unattended Mac.
- **Operator-session streaming hazard**: the operating session's own
  output streaming can fail a member's idle admission (window B
  failure #3) — a reproducible environmental-validity observation.
7084:> **2026-08-07 supersession (D-117):** clause 3's historical re-mint
7088:> allowance correction STAND and bind the D-117 mints.
7249:> **2026-08-07 amendment (D-117 cl.4):** the readiness dependency on
7507:## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired
   duplication of thresholds into this entry. A Window C mint is a
   fresh mint, not a re-mint.
7. **Fresh-claim reset.** Every still-desired Window-B claim component
   routes to fresh collection beginning with Window C; no Window B
   member counts toward replacement claims (C2's o0128/o0512 and C4's
   Window-B members return to uncollected-for-claim state).
   MET-WINDOW-C-01 must be re-scoped from its remainder-only shape to a
   fresh-claim plan; if the full replacement exceeds the runbook's
   2-4 hour envelope with references, calibrations, and >=20% failure
   margin, it splits prospectively across windows C and D rather than
   compressing the night.
8. **STANDING PRINCIPLE (Ed's prerogative, operationalized):** for
   irreversible claim-bearing collection, schedule pressure, sunk cost,
   and convenience never justify weakening a soundness gate; unknown or
   unresolved known-failure state is NO-GO; when salvage and fresh
   collection differ materially in epistemic quality and fresh
   collection is feasible, fresh collection is the default. PAIRED
   GUARDRAIL (anti-rigor-spiral, with D-078): more data or more process
   is required only when it closes a named validity threat or
   materially improves a planned claim — smaller independent windows, a
   narrower claim, or no claim may be MORE rigorous than
   over-collection. Escalation stays event-driven (repeated known
   failure, new producer for a refusal spelling, identity-epoch change,
   consumer failure after clean collection); no new recurring
   ceremonies. Mechanization is ONE hard start fence on the
   claim-window task (a reviewed frozen-plan readiness record + every
   hard dependency satisfied, verified by the ordinary launcher), not a
   new governance subsystem.
9. **Window C readiness: NO-GO until the consult's precondition gates
   are green** (consult record Q4, the ONE home for the full list):
   frozen fresh scope with runtime budget; desk toolchain + D-078 chain
   complete on merged main including the ISSUED D-079 acceptance
   artifact and the D-110 (b)+(c) re-mint chain; instrument/machine
   identity gates including the 140 W adapter discrepancy and a fresh
   §5A; quiet-guard status used honestly (installed-INACTIVE is not a
   Window C control; the proven zero-agent guarded-shell path with
   independent census is the default); and one frozen GO/NO-GO
   checklist with no in-night policy decisions. The runbook
   §5A-vs-§13.1 member-level clock-retry inconsistency must be resolved
   BEFORE the plan freeze; rigor-first default is NO member-level
   anchor retry without a prospective ruling.

**Consult dissents recorded (adopted):** kept-local-never-consumed was
rejected in favor of claim-retired-with-labelled-forensic-use; the
strict F7 answer is semantics-confirmation, not causal-scope truth;
D-110 condition (c) is readiness assurance for Window C, not
contamination physics; an installed-inactive quiet guard contributes
nothing to the Window C assurance case.

**Consequences.** CLAIMS_STATUS Window B section gains the terminal
labels; kernel row WINB-R06-DISPOSITION-01 retires as ABANDONED (same
session, after in-flight read-only sessions clear); MET-WINDOW-C-01
re-scope and the claim-window start fence register as queued work;
RUN_STATE's parked-decisions list drops D-113.

## D-114: T3-CHAIN DESCOPE — t3 stays the interactive control plane; t3-resident-during-measurement-windows is DROPPED (Ed directive, supersedes the 2026-08-03 T3-DRIVE priority)

**Date:** 2026-08-05 (Ed, in-thread, during the desk session).
**Status:** RATIFIED by the directive's own author. This reverses Ed's
2026-08-03 ~23:55 T3-DRIVE-PRIORITY directive. Under rule 11 a
lieutenant may not self-exempt from a standing priority; that
constraint does not bind Ed reversing his own instruction, so no cold
gate was convened. The lead proposed the descope shape; Ed ruled.

**Question.** The t3-drive chain (host-wide quiet lease, refuse-at-arm,
resident watcher, t3 handoff/relaunch, README banner projection, plus
an app-up/app-down characterization pair to decide app-adjacent window
admissibility) had grown a root-owned, sudo-capable, credential-bearing
surface — a 7-blocker focused audit on commit 1 alone, and a design
consult showing the credential could not be honestly removed without
also revising Q10/Q11/Q13/Q19/Q24 as a set. Ed: "is the juice worth the
squeeze for a UX improvement of using t3 as a control plane?" and "I am
tired of wasting time on this control plane stuff and want to get back
to the project."

**Ruling.**
1. **KEEP — t3 as the INTERACTIVE control plane.** Ed drives sessions
   from t3, including remotely and away from the measurement machine.
   This costs nothing and requires no guard machinery.
2. **DROP — t3 resident during measurement windows.** Claim windows
   return to the proven path: quit t3, ordinary guarded shell, zero
   agent sessions, fresh §5A, walk away. Every successful claim window
   to date used exactly this path. The app-up admissibility question is
   therefore MOOT, not answered.
3. **QUIET-GUARD-01 re-scoped to COMMIT 1 ONLY** — the host-wide quiet
   lease and process census, installed-INACTIVE. Retained on non-t3
   merit: it gives the ordinary guarded-shell launcher a MECHANICAL
   refuse-at-arm census, replacing today's procedural eyeballing. Its
   seven audit blockers are still fixed to the safety bar before it
   lands (it is root-adjacent regardless of who calls it).
4. **SHELVED:** QUIET-GUARD commits 2-4 (launcher interception, t3
   handoff + resident watcher, t3-relaunch + banner projection + all
   credential handling); T3-CHAR-PAIR-01 (BOTH arms — the r03 re-capture
   and the app-DOWN arm); WO-T3-VIS-01; SEC5A-REMOTE-01 (its
   programmatic substrate lived in the dropped scope).
5. **T3-DRIVE-PRIORITY gate LIFTED** (`active_global_gates: []`); the
   project queue is ungated. The two in-flight t3-adjacent desk items
   (T3-AMEND-01 doctrine bookkeeping, COLDGATE-VALIDATOR-01) finish
   because both are cheap, near-complete, and independently useful.
6. **Q13's degraded tail is ACCEPTED as an edge case** (Ed, explicit):
   if a relaunch fails and no session returns, there is no remote
   signal. A failed relaunch requires physical presence anyway, so
   local discovery at next login is sufficient. This retires the
   requirement that motivated the unattended-push credential.
7. **Q10 (guard git identity WITH unattended push) is SUPERSEDED** —
   moot under the descope; no credential enters any guard path.

**Design record preserved for any future revival** (from the 2026-08-05
credential consult, before the descope was ruled): a credentialed
network pusher running DURING a quiet window contradicts the window's
defining property. The correct shape is credentials only at the
unprivileged interactive boundary (pre-arm and post-window pushes), a
PRE-ARMED SERVER-SIDE DEAD-MAN ALARM for the no-return case (which also
catches total host death), a dedicated non-login service UID rather
than HOME-restore env scrubbing (root is otherwise ambiently
credential-reachable via git helpers / SSH / Keychain), and a banner
that can only truthfully say ARMING_REQUESTED pre-window.

**Consequences.** The successor's queue is the science queue: the two
open soundness-sweep blockers (RT-1 mint-floor understatement; voided
numbers on README/PROJECT_STATUS), the a10 phase-floor extraction, and
MINT-GENERALIZE-01 — whose D-110 condition (a) was satisfied the same
day by the CAL-BRACKET merge (PR #100, `f75d12b`).

## D-115: Quiet-guard Q2 setup authority is a FIXED INSTALLATION CAPABILITY, not general root authority (Commit-1 packet entry; renumbered from the contract's proposed D-114 marker)

**Date:** 2026-08-05 (lead adjudication, Fable magistrate session).
**Status:** ADJUDICATED under Ed's standing Q2 license (2026-08-05
ratification batch: Q2 proceeds on lead defaults subject to Ed veto).
**Numbering note:** the Commit-1 worker proposed this entry as D-114
inside `docs/contracts/quiet_guard.md` (it does not own the decision
log, correctly). D-114 was consumed the same day by the T3-CHAIN
DESCOPE, so this entry is D-115; the contract marker renumbers to
D-115 in the Commit-1 fix round. **Packet-letter deviation, ruled:**
the IMPL-PACKET file map places this entry in Commit 1's delta, but
the branch forked before D-114 landed and an in-branch append would
manufacture a merge conflict in this file; the entry lands on main and
is merged back into `impl/quiet-guard`, which satisfies the packet's
purpose (binding authority exists before the capability merges) with
cleaner custody.

**Question.** Q2 asked what authority the one-time
`scripts/setup_quiet_guard.sh` sudo session exercises when it creates
the root-owned quiet-guard state under
`/Library/Application Support/JouleWise/quiet-guard/`.

**Ruling.**
1. **Capability boundary.** The setup script exercises a fixed
   installation capability: create the root-owned state/install
   directories, install the fixed-command privileged helper and the
   narrow `sudoers.d` command aliases, and write `live_promotion=false`.
   It confers NO general root authority; nothing outside that
   enumerated set is licensed. Normal guard operation is `sudo -n`
   against the fixed command aliases only, and the helper drops to the
   invoking uid/gid before any agent child executes.
2. **Binding conditions on the capability** (from the 2026-08-05
   adversarial audits qg-audit-A/B; the capability is not validly
   exercised without them):
   a. **Fresh interactive authorization** — the installer must
      invalidate any cached sudo timestamp (`sudo -k`) before
      requesting authorization, so a cached ticket can never silently
      convert repository state into root-executed code.
   b. **Authenticated content** — what is installed must be
      authenticated against pinned digests of the reviewed artifacts
      (or an equivalently strong provenance check), not merely parsed
      for syntactic validity; root-staging closes copy races but does
      not authenticate what was staged.
   c. **Real interpreter isolation** — the installed helper runs with
      genuine isolation guarantees (no site initialization, no
      user-site, no environment hooks: `-I`-equivalent), matching the
      contract's isolation claim.
3. **Inactive by construction.** Commit 1 installs INACTIVE:
   `live_promotion=false`, `arm` refuses (`t3_char_pair_verdict_missing`),
   and no launcher, chain, watcher, or projection code is in scope
   (D-114 descope). Activation requires a separate, later, Ed-visible
   step and is not licensed by this entry.

**Consequences.** The Commit-1 fix round renumbers the contract marker
and implements conditions 2a-2c with discriminating regressions; the
QUIET-GUARD-01 row cannot land while any condition lacks enforcement.

## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)

**Date:** 2026-08-06 (Fable magistrate, overnight; issuance pre-authorized by Ed 2026-08-05 conditional on the gate passing).
**Status:** EXECUTED. This retires the schema fixture and issues the authoritative calibration acceptance artifact — the anchor all future floor-mint claims authenticate against. D-110 re-mint condition (b) ("R2 backfill verified, ledger bootstrapped, head pinned") is now SATISFIED; (a) was satisfied by PR #100, (c) by PR #105. **MINT-GENERALIZE-01 is UNBLOCKED for the re-mint.**

**What was written.**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis historical-import chain (git-ignored local custody artifact, sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`; deterministic from the custodied inputs below + the raw evidence; MUST be backed up per the runbook before the re-mint consumes it).
- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
- Reproducibility inputs custodied at `docs/process_traces/2026-08-06-d079-issuance-coldgate/` (disposition table sha `5da820aa…`, custody manifest sha `99cbf3df…`, execute summary, ledger sha).

**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).

**Window-B completeness note (soundness-critical, for any reviewer asking "why Window-B in the anchor?").** The `prior_observation_set` correctly includes 6 `window_metrologyB` **calibration fiducial** observations (2 valid: `e0ce33f5`, `8c3bfe9e`), as mandated by D-109 R2.3/R2.8 completeness (every content-distinct governed CALIBRATION observation). This is NOT a D-113 violation: D-113 retired Window B's WINDOW CLAIM consumption (its null-ladder/additivity science members), not the calibration fiducials collected in that period; the general calibration machinery survives per D-113. These fiducials are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound.

**Gate history (the process earned its keep on the anchor).** Two rule-11 cold gates. Cold gate #1 (on the plan) HELD correctly — the naive JSON-edit plan had no issued-artifact consumer (F1) and would have invalidated the whole-core digest (F2). That forced a real consumer implementation, which then ran the full C-028 gauntlet: adversarial audit (consumer proven false-ACCEPT-resistant; 3 emission/execute blockers incl. ledger-commit-BEFORE-artifact-validation) → fix → delta (exit-3 masking) → fix → final delta ACCEPT. Cold gate #2 (on the exact bytes): both lenses PROCEED on CONTENT (head/dispositions/B1/R2 all independently reproduced); HOLD on sequencing only — the consumer had to land on main before writing the issued artifact, else the anchor bricks. Resolved by merging PR #108 first, then executing against consumer-present main, with the co-landing verification (`_valid_acceptance_bound(issued)=True`) confirmed post-write. Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`.

**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.

## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired

**Date:** 2026-08-07 (Ed directive, in-thread; transcribed by the Fable
magistrate. Ed, verbatim: "if i recall for a paper ready at the quality
needed we need 3 more machine quiet nights and a lot of desk work",
with an explicit go to "execute all the deskwork" — read together with
his 2026-08-06 in-thread MVP-scope directive "a little more than just
decode, at least decode/prefill". His ruling moots a cold gate: apex
authority per rule 11.)
**Status:** ADOPTED. Full technical record:
`docs/process_traces/2026-08-06-d110-remint-fork/` (DIAGNOSIS: the
structural closure live-reproduced at `c537386`; Sol xhigh consult run
`20260806T165843Z-10884`; SYNTHESIS: magistrate concurrence).

1. **The D-110 clause-3 re-mint order (historical a10 consumption under
   the corrected selector) is SUPERSEDED.** The issued ledger holds only
   import-marked receipts; candidate discovery excludes imports by
   design; future live receipts cannot causally bracket past windows.
   The order is structurally unsatisfiable at main, not merely
   inconvenient. D-110's OTHER holdings STAND untouched: mint #1 and
   derivatives remain non-claim-bearing, and the never-zero
   `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3)
   BINDS every mint under this entry.
2. **Replacement: three compact prospective claim windows** — fresh
   1.5B decode floor, fresh 7B decode floor, fresh 1.5B-vs-7B contrast
   — each with fresh §5A, live pre/post calibration receipts appended
   to the issued ledger, own verdict + head-pin + custody. Claims
   chain: historical corpus → issued D-079 acceptance rule → live
   brackets → prospective floors → prospective contrast. Honest
   framing preserved from the consult: historical data establish the
   RULE; live receipts bracket all claim-bearing science.
3. **Scope (Ed's decode/prefill directive):** prefill FLOOR cells ride
   both floor windows (cheap, same members' prefill phase). The model
   contrast is DECODE-ONLY by default: the 2026-08-07 desk feasibility
   check (`docs/process_traces/2026-08-07-prefill-feasibility/`) found
   the 128-token prefill contrast MARGINAL against the effective bar
   (interval overlaps it). A prospectively frozen ≥256-token prefill
   contrast arm remains an OPEN ED OPTION (estimand change +
   ~110 core minutes, likely its own window) — not adopted here.
4. **D-113 rewire:** its readiness dependency on the historical re-mint
   completing is REMOVED. The three-window P1 closure PRECEDES the
   broader MET-WINDOW-C-01 C2/C4/C5 replacement campaign (grounds:
   Ed's paper-first priority stack, 2026-08-06).
5. **Naming:** "Window D" is unavailable (collides with
   `runs_window_d_20260726` and D-113's reserved terminology); the
   three windows receive new immutable plan/root identifiers at plan
   freeze.
6. **Option 1 (finite-allowlist historical candidacy) is PRESERVED as
   a versioned contingency ONLY**, requiring a rule-11 cold gate before
   any implementation (semantics sketch: consult response §3). The
   historical corpora remain untouched on disk, non-claim-bearing per
   D-110 cl.1, logs sha-verified.
7. **Unblocked desk queue** (consult §4): freeze three window plans +
   budgets; 1.5B decode floor plan from the proven 10-absolute/40-null
   design; generalized mint pinsets with per-plan six-decimal literals
   (the D-084 hard literal `7.377086` refuses any corrected mint under
   every option — closure is per-plan supply via the generalized path);
   extraction specs / order manifests / evidence-root ids / contrast
   manifest; synthetic three-window live-ledger integration regression;
   D-102 successor-artifact packet; results/methods prose placeholders.

exec
/bin/zsh -lc "sed -n '1,110p' docs/paper/draft-v1.md; sed -n '111,230p' docs/paper/draft-v1.md; cat CLAIMS_STATUS.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# JouleWise: Detection Floors for LLM Inference Energy Measurement on Consumer Silicon

## 1. Introduction

Energy numbers for large language model (LLM) inference now appear in leaderboards, systems papers, product comparisons, and policy debates. Published estimates for apparently similar queries can differ by an order of magnitude, yet the numbers are rarely accompanied by an error bar that says how small a difference the measurement method can actually distinguish. This omission is especially consequential on consumer hardware. Apple's `powermetrics` utility makes processor power estimates available without a laboratory meter and is therefore attractive for repeated experiments, but, to our knowledge, it has not been validated in published work as an instrument for separating the energy of LLM inference phases. Apple describes its outputs as estimates; treating them as exact readings can turn timing uncertainty at a phase boundary into a spurious energy difference.

The core difficulty is physical as much as statistical. Energy is the integral of power over time. An experiment may repeat consistently and still assign energy to the wrong phase if a power sample near the boundary between prompt processing and token generation is placed on the wrong side. Averaging more repetitions reduces random scatter but does not remove that attribution error. Slow changes in thermal or background state can add a second false difference over a long collection session.

We argue that a software power counter should be treated as a scientific instrument rather than as a logging convenience. The instrument must be calibrated in the same session in which it is used; each reported result must carry a detection floor, meaning the smallest false effect that the calibrated method could plausibly produce under the stated conditions; and the analysis must decline a directional claim when the observed effect cannot clear that floor and its own measurement uncertainty. JouleWise implements this discipline for phase-resolved, single-request LLM inference on one named Apple-silicon machine and software stack. The runtime emits the phase boundaries because it drives the workload, while `powermetrics` supplies the power samples integrated between those boundaries.

This scope is deliberately narrow. A measurement characterizes one physical unit, operating-system build, runtime and library stack, model artifact, quantization, tokenizer, sampling policy, single-request execution policy, telemetry backend, and measurement boundary. It does not establish that an Apple hardware class or vendor is more efficient than another platform. Without an external power meter, absolute values remain internal to the named `powermetrics` system-on-chip boundary; same-boundary contrasts can still be scientifically useful when they pass the calibration and floor gates. Gross joules per request are the primary energy metric. Joules per prompt or output token are tokenizer-scoped companion metrics and are never treated as tokenizer-independent work units.

This paper makes the following contributions:

1. (C-i) an in-window calibration method that measures timing-attribution error for phase-resolved energy integration;
2. (C-ii) detection floors composed from measured repeatability, worst-case attribution, and measured drift — published with every result;
3. (C-iii) a fail-closed collection protocol (admission gates, ABBA ordering, custody chains, pre-registration) with its refusal log as evidence;
4. (C-iv) full instrument characterization: linearity, null response across magnitudes, empirical floor verification, phase-attribution causal consistency, drift/settle;
5. (C-v) demonstration measurements: phase-resolved J/token for two model sizes with a pre-registered contrast [+ quantization ladder if window budget allows];
6. (C-vi) open tool + hash-bound reproducible artifacts.

## 2. Background and the gap

### Energy-benchmarking rules

The first relevant lineage is formal energy benchmarking. MLPerf Power and the associated Standard Performance Evaluation Corporation methodology treat uncertainty and validity as properties of each measured run. They require a qualified analyzer, uncertainty evaluated at the observed load, fixed measurement ranges, synchronized clocks, sufficiently long intervals, invalid-sample accounting, and explicit treatment of battery-backed systems [MLPerfPower]. These rules establish an important principle: a benchmark result is not valid merely because the meter has a specification sheet. The evidence recorded during the run must show that the measurement operated inside its accepted conditions. These standards, however, assume external instruments and data-center-style workloads; they do not provide a method for validating phase boundaries reported by a software counter on a consumer system.

### Software-counter validation

The second lineage validates software-visible energy counters against external power. Intel's Running Average Power Limit (RAPL) counters have been studied through lag alignment, regression against wall power, counter-resolution tests, sampler-overhead audits, and thermal controls [RAPLInAction]. Jay and Ostapenco's CCGRID 2023 study likewise shows that the gap between a software meter and wall power can depend on load rather than behave as one fixed offset, and it refrains from component-level conclusions when no reference instrument observes the component [JayOstapenco]. This work provides a strong model for whole-machine scale validation. It does not define a detection limit for a reported effect, does not validate `powermetrics` on Apple silicon, and cannot by itself establish whether software samples were assigned to the correct LLM phase. A wall meter observes a total; phase attribution needs a separate timing experiment.

### LLM energy studies

The third lineage measures LLM energy across models, hardware, and workloads. TokenPowerBench reports prompt-processing and token-generation energy with phase-appropriate token denominators; ML.ENERGY, Silicon Showdown, and Intelligence-per-Watt broaden empirical coverage across deployed systems [TokenPowerBench; MLENERGY; SiliconShowdown; IntelligencePerWatt]. This breadth makes inference energy visible, but the nearest studies do not jointly characterize counter timing, repeatability, drift, and the minimum resolvable effect. Phase labels are consequently easy to read as exact even when the method does not report the boundary events, alignment uncertainty, or a floor below which a difference should be refused.

The specific gap is therefore not another energy table. To our knowledge, no published work combines phase-resolved LLM energy on consumer silicon, a per-measurement error budget, and validation of `powermetrics` timing attribution under its named measurement boundary (as distinct from validating its absolute counter gain or whole-system energy scale, which would require an external meter). JouleWise fills that gap by making instrument characterization and refusal behavior the primary result; model comparisons are demonstrations of what the characterized instrument can and cannot resolve.

## 3. In-window calibration method (C-i)

### Measurement model and boundary

JouleWise measures one sequential request at a time. Prompt processing (often called *prefill*) converts the input sequence into the model's internal state; token generation (often called *decode*) produces output tokens from that state. Because the experiment controls the runtime, it records the start and stop of these phases directly in the runtime event stream rather than inferring them from shapes in the power trace. The reducer then integrates the named `powermetrics` system-on-chip power channels between each pair of phase events using trapezoidal integration.

The runtime and the telemetry sampler do not share a perfect clock. Operating-system launch latency, timestamp anchoring, and the sampler's averaging behavior can shift an apparent edge. A phase-energy estimate must therefore be an interval, not only a point. The calibration asks a concrete question: if software commands a load pulse at a known time, how far can the rising and falling edges of that pulse appear displaced in the sampled power trace?

### Bracketed pulse-train calibration

Immediately before and after every claim-bearing collection window—that is, a window eligible to support a reader-facing scientific claim—JouleWise runs a fresh pulse-train calibration under the same machine, operating-system, power-supply, and telemetry state as the science workload. The current protocol commands 59 graphics-processor matrix-multiplication pulses. Their durations are fixed in advance, their gaps follow a deterministic low-discrepancy schedule rather than a single repeated period, and quiet baselines of at least 4.5 seconds separate the fitted regions. The varied schedule reduces the risk that the calibration accidentally locks to the telemetry sampler's cadence. The 59-pulse design supports the pre-registered nonparametric 95/95 bound: a conservative bound intended to cover at least 95% of the calibration population with 95% confidence under the stated transfer assumptions.

For each pulse, the estimator compares the commanded interval with the observed power plateau and fits the start-edge and stop-edge lags independently. This distinction matters. A common shift of both edges may leave pulse energy nearly unchanged, while an early start combined with a late stop can add energy at both boundaries. The calibration therefore retains a bound for the instrument's edge-placement error rather than collapsing the evidence to one best-fit lag.

Each science member, meaning one recorded workload run, also carries a local bound on how its runtime clock is anchored to the trace, including the observed span between wall time and a monotonic clock that is not adjusted by network synchronization. For a reported phase, the analysis combines the member-local common shift, the calibration edge bound, and the clock-span term. It evaluates the energy integral at all four combinations of early and late start and stop edges, while scanning the allowed common shift exactly. The minimum and maximum of those integrals form the admissible energy interval. The physical intuition is simple: the interval asks how much energy could move into or out of the phase if both boundaries were placed at their most adverse calibrated positions.

The pre- and post-window calibrations form a bracket around the measurements. Both must be authenticated, fresh, and causally outside the science interval. The operative bound is the larger of the two. Separately, the absolute difference between the pre- and post-window calibrations is screened against a derived bracket-drift limit of about 10.82 ms: a small repeatability-only excess is propagated into every floor and claim, while an identified systematic defect cannot be absorbed by that budget. If the post-window bound is larger than the one used when a member was first reduced, the member must be re-reduced through the pre-specified path with the wider bound or it cannot support a claim; metadata is never patched to make the bounds agree. A pre-flight level screen also runs before the first science member. It rejects a calibration whose fitted lag is outside the previously characterized family, such as a graphics-processor frequency ramp that the pulse model could mistake for a timing shift. A retry is allowed only after a specific cause is identified and removed, within the retry count frozen before collection. Repeating merely until a favorable calibration appears would be selection on the outcome.

This procedure validates timing attribution, not the gain of the power counter. The pulses are graphics-processor matrix multiplications under a relatively light central-processor load, so transfer of their timing bound to sustained mixed-load inference is an explicit assumption. The in-session bracket, empirical floor probes in Section 6, and stack-specific labels constrain that assumption; only an external meter could additionally validate the absolute whole-system scale.

## 4. Detection-floor composition (C-ii)

A *detection floor* is a practical guard against false observed effects for one declared condition family: the same telemetry backend, metric, window type, workload profile, and stack identity. One such family forms a measurement cell. The floor is not a claim that a population percentile has been estimated exactly. JouleWise computes separate absolute and comparative floors and takes their maximum for the cell. An absolute floor measures how far repeated measurements of the same condition wander from their mean. A comparative floor measures the apparent difference between labels that are deliberately made identical and collected in A/B/B/A order.

### Repeatability and false-comparison guards

For an absolute cell with energies \(E_i\), residuals \(r_i=E_i-\bar E\), sample standard deviation \(s_r\), and \(n\) valid bundles, the point guard is

\[
F_{\mathrm{abs,point}}=\max\left(\max_i |r_i|,
t_{0.975,n-1}s_r\sqrt{1+1/n}\right).
\]

For \(n\) valid null-comparison blocks with within-block deltas \(\delta_i\), the corresponding guard is

\[
F_{\mathrm{cmp,point}}=\max\left(\max_i |\delta_i|,
|\bar\delta|+t_{0.975,n-1}s_\delta\sqrt{1+1/n}\right).
\]

The observed maximum protects against a false effect already seen; the Student-*t* prediction term protects against one additional observation under the repeatability model. Small samples receive a pre-registered guard factor, and fewer than five valid bundles or blocks are treated only as development evidence, not as a claim gate. Items within one bundle are not counted as independent repetitions.

### Worst-case timing attribution

Point repeatability is not the full floor. Each energy value is an interval from the timing calibration in Section 3. The floor computation evaluates the complete point-floor estimator over the joint corners of all member intervals that pass the admission and evidence gates, then takes the largest value. For a null A/B/B/A block, the four signed member intervals are propagated through the contrast together. This corner calculation is deliberately conservative: a systematic boundary-placement error is not independent Gaussian noise, so adding it in root-sum-square form would understate the worst case. The published floor is no smaller than the largest accepted attribution width.

This calculation revealed a stable and important limitation of the present instrument. Ordinary repeatability is smaller than the uncertainty caused by placing samples at phase edges: approximately one joule can be assigned to the wrong phase when a roughly 30 ms timing uncertainty meets a power change of roughly 33 W. The instrument is therefore *attribution-limited*, not *noise-limited*. More repetitions can refine the repeatability term, but they cannot average away this boundary-placement limit.

### Measured, never-zero drift allowance

Drift is a slow change in the machine or measurement response over the collection window. It is measured rather than assumed away. Each prospective window includes three fixed reference runs at the start, one at the midpoint, and three at the end. Gross energy and idle-subtracted energy are treated as separate claim families (idle-subtracted energy is gross energy minus the measured idle mean power multiplied by the phase duration). For each family, the protocol derives a repeatability bound from a settled reference corpus and measures the largest excursion among the start mean, midpoint, and end mean. The allowance is

\[
A_{\mathrm{drift}}=\max(\text{observed start/mid/end excursion},
\text{derived reference-repeatability bound}).
\]

Consequently, a passing drift screen never means zero drift. The allowance remains positive even in an exceptionally stable window, and the midpoint protects against an interior excursion that similar endpoints would miss. No duration-scaling law is applied because the available evidence does not identify a physical law relating drift to elapsed time.

For each absolute or comparative component, the guarded, corner-widened value is increased once by its matching drift allowance. The operative floor for a cell is then

\[
F_{\mathrm{cell}}=\max(F_{\mathrm{abs}},F_{\mathrm{cmp}}),
\]

not their sum. Cross-window components keep their own calibration basis and allowance; an allowance is never added again at the cell or reporting level. Operative floor values and their full decomposition for each demonstration stack are withheld here until the corrected artifacts are issued: **[RESULT PENDING RE-MINT]**.

### LABELLED publication and the effective decision bar

When timing attribution dominates, the floor remains publishable only through the **LABELLED** path. Every artifact and reader-facing result must identify the limit as attribution-limited, publish the corner-widened value rather than the smaller point diagnostic, retain the point-only repeatability number as a non-publishing diagnostic, and carry `floor_source = E_clock_anchor_shift_bound_j`. This field names energy uncertainty caused by shifting the phase edges within the calibrated clock-anchor bound as the dominant term. The label prevents a precise repeatability number from masquerading as the instrument's total resolving power.

The floor is only one side of a claim decision. The calibrated floor bounds a false effect produced by the calibration condition; the confidence or decision interval for the particular measured contrast separately carries that contrast's timing-attribution uncertainty. These are distinct uses of the same physical uncertainty and both are required. The effective bar is therefore

\[
\text{effective clearable effect}=F_{\mathrm{cell}}+B_{\mathrm{claim}},
\]

where \(B_{\mathrm{claim}}\) is the claim-side measurement bound. For the measured phase-contrast regime, this combined bar is approximately 5 J. Neither term may be removed as an apparent double count. Effects below the floor are reported as *not resolvable*, not as zero, equal, or evidence of no difference. A directional claim is made only when the effect and its interval clear the applicable bar.

## 5. Fail-closed collection protocol (C-iii)

*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is one uninterrupted two-to-four-hour window with one power state, one instrument identity, fresh calibration before and after, a fresh drift-bound corpus, and one verdict over the exact member set. Work that does not fit with at least a 20% failure margin is split prospectively into another independently calibrated window.

### Pre-registration and admission

Before quiet time, the operator freezes the run identifiers, membership, stage order, comparison definitions, calibration retry count, acceptance thresholds, extraction specification, code revision, and an initially empty waiver list. Every configuration is validated and dry-run against a fresh output root. These choices are made before outcomes are visible. Pre-registration here is executable: the launcher and final verifier check the frozen values rather than relying on a narrative promise.

Each stage then passes admission gates immediately before measurement. The approved power supply and power policy must be unchanged; displays must be asleep; the screensaver and low-power mode must be off; thermal pressure must be nominal; and central- and graphics-processor activity must meet the quiet-state criteria. Known background work is allowed to finish before the window, followed by a settling interval, rather than being ignored during analysis. Runtime and telemetry identities, clock anchoring, sample cadence, calibration freshness, and post-run environment observations are also checked. No environment override can produce a claim-bearing member.

### Counterbalanced order

Comparisons use A/B/B/A blocks, abbreviated **ABBA**. Conditions A and B are measured in the order A, B, B, A, with ordinary cooldown between members. Averaging the two outer A observations and the two inner B observations cancels a linear time trend within the block to first order. For null-floor calibration, A and B are aliases of the exact same configuration and payload, so any nonzero block delta is a false comparative effect. For scientific contrasts, the A and B definitions are frozen in advance, and the contrast is computed within each block before blocks are aggregated. ABBA reduces common drift; it does not replace the measured whole-window drift allowance.

### Evidence custody and refusals

Every member is a self-contained bundle of configuration, raw power trace, runtime events, environment observations, and derived summary. Cryptographic hashes bind those files to the campaign manifest. Failed or interrupted artifacts are never deleted or overwritten. An occupied retry slot is moved to a quarantine area outside the active runs root; the exact member is recollected only under an allowed retry; and an append-only supersession record names which occurrence governs. Two present bundles for one occurrence refuse. The final whole-window verdict binds the exact member-occurrence set, calibration bracket, policy, and drift evidence by hash, so a later consumer cannot silently select a more favorable subset.

Collection does not continue indefinitely through environmental interruptions. Each stage attempt stops at its first member failure, and after the same cause fails a window stage for the third time the window itself closes rather than being retried; in actual operation, nights with three environmental member interruptions were closed and preserved as salvage rather than repeatedly retried. The surviving data may remain diagnostic, but it becomes claim-bearing only if the pre-registered verdict and extraction rules accept the exact resulting basis. This abandon-after-three rule limits outcome-dependent retrying and makes the cost of a noisy environment visible.

The custody chain continues after collection. The immutable corpus is backed up before extraction. The extractor re-authenticates member hashes, required files and cross-file consistency, calibration identity, environment admission, complete campaign membership, cooldown evidence, phase metric identity, and the whole-window drift allowance. It excludes or refuses a cell according to the frozen rules; missing uncertainty never becomes zero. The current artifact boundary is stated honestly: until floor artifacts are independently bound to their source extraction, a claim-bearing floor must be produced by protocol-controlled extraction in the same controlled custody session as the analysis that consumes it. A standalone floor file is not independently claim-licensing.

The refusal log is part of the evaluation, not an embarrassment to omit. It records contaminated members, out-of-family calibration, stale drift evidence, unresolved clock anchors, duplicate occurrences, and below-floor effects. In one real end-of-night case, the governed re-evaluation refused a window because a member's internal clock alignment could not be resolved. Independent adjudication found that refusal correct. The result remained non-claim-bearing: an example of the fail-closed design working as intended, not a software defect to be bypassed.

## 6. Instrument characterization (C-iv)

Instrument characterization asks whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload is therefore a test signal, not yet the scientific finding. All tests retain the same calibration, admission, custody, and floor rules as the later demonstration measurements. Existing campaign fragments are not promoted where the governing whole-window verdict did not pass; the table marks the required claim-bearing results explicitly.

| Property | Characterization method | What a passing result would establish | Claim-bearing result |
|---|---|---|---|
| Linearity | Hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. Regress gross request and decode energy on the runtime-observed output count; inspect residual structure as well as the fitted slope. | Energy responds proportionally over the tested dynamic range, and the fitted per-token slope can serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
| Null response across magnitudes | Run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes. Evaluate the paired deltas against zero and against the predicted decision envelopes. | The comparison path does not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range are contained by the error model. A non-significant result alone is insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
| Empirical floor verification | Use the pre-registered linearity slope to create micro-deltas with predicted effects near 0.5, 1, 1.5, and 3 times the declared floor. Test positive and negative directions in counterbalanced blocks. | Sub-floor effects are refused while sufficiently super-floor effects clear in both directions. This is an operational check of the detection boundary, not a validation of the counter's absolute gain. | **[PENDING WINDOW C]** |
| Phase-attribution causal consistency | First compare the sum of separately integrated phase energies with the gross energy over their enclosing request. Then vary output length while holding prompt tokens fixed and fit the slope of prefill energy against output length. | Phase accounting is additive within its stated boundaries, and energy assigned to prefill does not acquire a systematic dependence on work that occurs later in decode. Together these tests challenge both missing energy and cross-phase leakage. | **[PENDING WINDOW C]** |
| Drift and settling | Place long controlled holds and fixed reference workloads through the window, including start, midpoint, and end references. After operator or stage activity, repeat the reference while recording the time required for thermal and admission observables to stabilize; compare it with the 180 s operating convention. | The measured drift trajectory is contained by the published allowance, and the chosen settling time is supported or revised from observed recovery rather than convenience. Endpoint agreement alone is not enough if the midpoint reveals curvature. | **[PENDING WINDOW C]** |
| Between-session stability | Repeat calibrations, null blocks, and floor cells across at least three sessions or days with the full stack identity recorded. | The calibration and floor are stable enough to reuse only under their declared freshness and identity rules, or reveal that a new session must mint a new floor. | **[PENDING WINDOW C]** |

Linearity and the null ladder test complementary failure modes. A smooth response can still carry an offset, and a zero-centered null can coexist with a nonlinear scale. The micro-delta experiment then closes the loop by using the measured slope to place effects deliberately below and above the declared decision boundary. Success requires the instrument to refuse the former and resolve the latter in both directions; merely observing larger effects with larger workloads is not sufficient.

The causal tests address the most important phase-specific risk. Additivity checks conservation inside the declared request boundary: phase intervals should reconcile with the enclosing total, subject to explicitly labeled setup or gap intervals. Causal invariance checks direction: holding the prompt fixed while increasing later decode work should not change energy attributed to earlier prefill. A nonzero prefill slope would indicate boundary leakage, shared-state coupling that invalidates the simple phase model, or both; it would narrow the claim rather than be explained away.

Temporal characterization separates slow drift from thermal settling. Start, midpoint, and end references expose whole-window curvature, while post-transition references estimate how long the system takes to return to its admitted state after operator activity or stage churn. Repetition across days tests whether one session's calibration is representative under identical recorded bindings. Internal channel-sum versus package reconciliation is retained as a secondary consistency check. External wall-power regression remains conditional on a suitable meter and would validate totals only; the pulse experiment remains the evidence for phase splitting.

Every resulting figure and table will identify the physical unit, operating-system version and build, runtime and relevant library versions, model artifact hash, quantization, tokenizer identity, sampler and output policy, configured and realized batch/concurrency policy, measurement boundary, and telemetry backend. Silent omission is not permitted. Measurements support stack-specific conclusions only; independent replication or a calibrated boundary bridge would be required for hardware-class, vendor-class, or cross-boundary rankings.

## 7. Demonstration results (C-v)

**[RESULT PENDING RE-MINT]**

This section will report phase-resolved gross joules per request for two model sizes, with tokenizer-scoped joules per prompt token and per output token as companion metrics. It will contain the pre-registered same-boundary model-size contrast, its interval, the complete floor decomposition, the claim-side bound, the effect-to-floor ratio, and the final resolvable/unresolved verdict. No demonstration energy value from the superseded mint is carried into this draft. A quantization ladder will be included only if it is collected under its own stack-specific floors and the frozen window budget permits it.

## 8. Related work

### LLM inference energy measurement

TokenPowerBench provides one of the closest reporting structures: it separates prompt-processing and token-generation energy, uses phase-appropriate token denominators, and groups results by context length [TokenPowerBench]. Its disclosed method, however, does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation, and continuous batching makes an “active phase” label difficult to interpret when requests overlap. JouleWise adopts phase-specific reporting but restricts its primary scope to one sequential request, where runtime-emitted phase boundaries are well posed and can be calibrated.

The Illusion of Power Capping in LLM Decode samples graphics-processor power, integrates those samples, repeats configurations, and cross-checks sufficiently long operations against a separate hardware energy counter [IllusionPowerCapping]. This is a stronger measurement template than an unqualified software reading. Its counter agreement, run-to-run variation, snapshot fallback, and timing alignment nevertheless remain separate diagnostics rather than one bound on the reported effect, and its long sweeps do not use a drift-control ordering. JouleWise composes those classes of uncertainty into a decision rule for each contrast.

Apple-focused system comparisons reinforce the need for boundary labels. Silicon Showdown compares a graphics-board boundary on one platform with a whole-system-on-chip `powermetrics` boundary on Apple hardware, while runtimes and precision stacks also differ [SiliconShowdown]. Intelligence-per-Watt and ML.ENERGY similarly emphasize breadth across deployed inference configurations [IntelligencePerWatt; MLENERGY]. Such studies answer valuable systems questions, but unlike boundaries and software stacks cannot by themselves support a hardware-class causal ranking. JouleWise therefore makes the named stack and measurement boundary part of every result and prioritizes within-boundary effects.

### Software power counters and measurement standards

RAPL in Action established a validation agenda for commodity software counters: align lag before comparing streams, model wall power rather than assuming identity, account for temporal correlation, warm the system, measure sampler overhead, and inspect update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. Jay and Ostapenco likewise regress software readings against wall power and show that disagreement varies with load; they avoid claims about subtotals that the reference meter cannot observe [JayOstapenco]. JouleWise follows this epistemic boundary. A future external meter could test total gain and load dependence, but it would not validate how a total is divided between prefill and decode. The in-window pulse train addresses that distinct question.

MLPerf Power and SPEC require load-specific analyzer uncertainty, fixed ranges, clock synchronization, minimum intervals, invalid-sample accounting, and controlled battery behavior [MLPerfPower]. JouleWise translates their per-run reject-on-missing-evidence principle to a consumer software counter. The difference is that its principal uncertainty is not only an analyzer specification; it includes whether samples at a software-defined phase edge belong inside or outside the integral.

### Metrology and experimental discipline

Prospective paired minimum-detectable-effect methods estimate the smallest effect a planned paired study has adequate statistical power to find. They size the study from the variance of paired differences and can impose a one-way prior ratchet: observed variability may raise the planned threshold but may not lower it after outcomes are seen [PairedMDE]. JouleWise uses that logic for prospective workload sizing, but it does not treat the worst-case attribution term as independent random noise. Root-sum-square composition would be anti-conservative for a systematic edge-placement bound. Instead, the analysis maximizes over calibrated edge positions, measures drift with bracketed references, and publishes the resulting floor with the effect.

This emphasis changes the role of failed runs. A rejected admission, stale calibration, contaminated member, or below-floor contrast is evidence about the instrument's operating domain. Hash-bound raw traces, runtime events, configurations, supersessions, verdicts, and pre-registration records make that evidence re-reducible. The refusal is retained rather than disappearing behind a final average.

### Split and disaggregated inference

Split, or disaggregated, inference places prompt processing and token generation on different devices and transfers intermediate state between them. Revisiting Disaggregation Energy reports that the energy outcome depends on load, baseline, and transfer conditions on its evaluated two-graphics-processor node [RevisitingDisaggregationEnergy]. DualScale studies phase placement and per-phase power control on homogeneous server hardware [DualScale]. Prima.cpp includes whole-run energy and communication accounting but not a per-stage energy split [PrimaCPP], while SplitZip characterizes lossless transfer compression without making an energy claim [SplitZip].

JouleWise does not claim a new split scheduler in this paper. Split inference is instead a demanding future demonstration of the instrument because it introduces two physical boundaries, a transfer interval, and clock alignment across devices. A valid comparison would have to measure both ends, name each boundary, and clear a pre-registered floor or calibrated bridge. Whether splitting saves energy remains an empirical outcome; the reusable contribution is a method that can issue, qualify, or refuse the result.
# Claims Status

**The single standing home for "what can we actually claim right now."**
Every scientific number the project can publish, is holding, or must not
repeat — with its exact validity state and blocker. Refresh this file
whenever claim-bearing state changes (a verdict, a mint, a merge in the
D-095 chain, an adjudication); quote verdicts as issued, never
reinterpreted. Companion docs: `RUN_STATE.md` (session pointer),
`WINDOW_STATUS.md` (machine state), `docs/decision_log.md` (policy).

Last updated: **2026-08-07** (D-117: the historical re-mint path is
SUPERSEDED — structurally closed at main after the D-116 issuance
(candidate discovery excludes import-marked receipts by design); the
claim path forward is THREE PROSPECTIVE WINDOWS — fresh 1.5B decode
floor, fresh 7B decode floor, fresh decode contrast — live-bracketed
under the issued acceptance regime, with prefill floor cells riding
both floor windows. Prior "re-mint conditions" in this file are
historical: D-109 landed (PR #100), issuance executed (D-116, PR #109),
validator pin widening landed (PR #105). Full record:
`docs/process_traces/2026-08-06-d110-remint-fork/`.)

Earlier header (2026-08-03 night, for the record): D-108/D-109 ruled +
executed; D-110 made mint #1 retroactively NON-CLAIM-BEARING; window B
re-evaluation STOPPED → D-112; mint-1 re-derivability proven
byte-identical; report: `docs/run_reports/2026-08-03-16h-runway.md`.

---

## 1. VALID — minted, mainline, citable

**NONE at this checkpoint.** D-110 (2026-08-03, sweep finding RT-1)
made mint #1 and every number derived from it retroactively
non-claim-bearing: its floors embed a never-zero allowance of ZERO
where D-102 pin 3 mandates +max(drift, 0.010818 s) (~+43% on the a10
operative bound). The previously-listed values (operative 7.377086 J;
a10 components 3.823787 / 3.592138 J; window C comparative 7.377086 J)
move to §5 until the re-mint. The DERIVATION toolchain itself is
proven honest: the full pinned replay (2026-08-03) reproduced both
extraction reports, the artifact, and the statement BYTE-IDENTICAL
(`docs/process_traces/2026-08-03-q1-remint-bytecompare/`). The taint is
semantic (the selector the era used), not derivational.
**2026-08-07 (D-117):** the historical re-mint order is SUPERSEDED —
all three former re-mint conditions completed (D-109 via PR #100;
issuance via D-116/PR #109; pin widening via PR #105) and the FIRST
consumption attempt then proved historical consumption structurally
closed at main. Replacement: three prospective windows (D-117 cl.2);
the never-zero allowance correction binds their mints. All four PASSED
window verdicts remain untainted (sweep RT-5), but pre-genesis windows
CANNOT be claim-consumed — their role is diagnostic and
rule-establishing only.

**Standing measurement fact (D-078 cl.11, Ed-ratified):** the instrument
is attribution-limited (~1 J), not noise-limited (~0.3 J). Floors
publish LABELLED with the widened number; the effective clearable
effect for phase contrasts is floor + claim-side bound ≈ 5 J. No
instrument-tightening program.

## 2. EVIDENCE-BEARING — collected and verdict-PASSED, awaiting a specific gate

| Candidate claim | Value (prose-only until gated) | Window / verdict | Blocker |
|---|---|---|---|
| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
| **1.5B-vs-7B decode contrast** (demonstration study #1) | **Registered claim metric (frozen v3 manifest): `phase_energy_j.decode`, 7B−1.5B = 141.29 J per block.** The widely-quoted 146.730349 J (σ 0.241 J, n=10 ABBA) is the `idle_subtracted_energy_j` whole-request DIAGNOSTIC — quote it only labelled as such, never as the claim (sweep DC-1; both reproduce byte-exactly from disk). | `window_contrast_20260730`, **PASSED** | **RE-SCOPED by D-117 (2026-08-07):** `window_contrast_20260730` is pre-genesis and cannot be claim-consumed; values are DIAGNOSTIC and the design template for the fresh contrast window (D-117 cl.2). The D-095 chain now runs through the prospective windows' mints. |

## 3. COLLECTED — verdicts FAILED as-issued; adjudication RULED (D-100, 2026-08-01)

The machinery adjudication is complete (MET-VERDICT-ADJ-01 → D-100 cold-
gate synthesis). Both verdicts **stand as issued, permanently by
construction**: any licensed re-evaluation appends a NEW row under
`consumption_semantics_id: salvage_dangler_exclusion_v1` with a new
pinned basis; the original FAILED rows are never edited and govern
default consumption. Outcomes per window:

- **Window A: permanently non-claim-bearing.** Its only post-cal retry
  binds a T1-incompatible power-policy identity (immutable evidence; the
  machinery's rejection was CORRECT), so no calibration bracket can ever
  form. C1 re-collects in a future window.
- **Window B: TERMINALLY CLAIM-RETIRED (D-113, Ed ruling 2026-08-05):
  RETAINED_IMMUTABLE / PERMANENTLY_NON_CLAIM_BEARING.** Ed chose
  abandonment over salvage ("soundness and quality of the project and
  claims above all"): no re-evaluation or claim consumption will ever
  occur; the WB-specific D-100/D-106/D-108 license chain is retired
  (general machinery survives for other windows);
  `WINB-R06-DISPOSITION-01` closes ABANDONED_FOR_FRESH_COLLECTION;
  labelled read-only forensic/diagnostic use remains permitted ("Window
  B, original verdict FAILED, D-113 claim-retired, non-claim
  evidence"). Every still-desired WB claim component re-collects fresh
  beginning Window C — no WB member enters a replacement claim basis.
  The F7 scope question is ANSWERED: whole-window voiding is affirmed
  as the current semantics (a cell-scoped alternative only via the
  D-083 cold gate; not built). Historical record of the 2026-08-03
  attempt below. The whole chain executed: D-108 ruled
  (clause (c) retired), row `D100-BII-BINDING-01` CLOSED (PR #99 +
  clause-(d) three-occurrence digest-bound re-record), closure +
  membership-binding artifacts authored and dry-authorized, D-093 scan
  clean 1/1, frozen corpus verified byte-identical (210+4 files, zero
  mismatches). The governed re-evaluation then REFUSED pre-verdict:
  survivor consumption failed on `mtadd-p2048o0128-r06`'s
  collection-time clock-anchor failure (`native_intersection_empty`) —
  the cold gate ruled this CORRECT fail-closed machinery (classification
  (i), convergent instruments; record
  `docs/process_traces/2026-08-03-winB-reeval-stop/`). No licensed
  channel removes r06 (exclusion cap spent on r08; not a dangler;
  waivers forbidden), and the NEG-8 drift bound expired 2026-08-02, so
  no PASS path exists under the license as drawn. Original FAILED
  verdict untouched. The WB NEG-8 bound re-mint obligation is MOOT
  under D-113; the near-run-time freshness rule continues to bind
  every future window (runbook + D-078, by cross-reference).

| Paper claim | Campaign | Collected | State after D-100 |
|---|---|---|---|
| **C1 — linearity** | `linearity_ramp` | **40/40** (window A) | DEAD for claims (window A permanent FAIL); re-collect (window C/D); data usable as design input (micro_delta slope) + corroboration diagnostics only |
| **C2 — null ladder** | `null_ladder` | o0128 + o0512 collected in window B — **returned to uncollected-for-claim state (D-113)**; o2048 never collected | Re-collect ALL of C2 fresh (window C, or split per the frozen plan); no WB member enters a replacement claim basis |
| **C3 — micro-delta** | `micro_delta` | not collected | Plan is draft-pending-slope by design; slope fit may consume window A ramp as DESIGN input (not a claim) |
| **C4 — additivity** | `additivity_shapes` | 23/24 single-root collected in window B — **returned to uncollected-for-claim state (D-113)**; 21/24 window-A corroborating remain labelled non-claim diagnostics | Re-collect C4 fresh (window C/D per the frozen plan). F7 ANSWERED by D-113: whole-window voiding affirmed as current semantics; no cell-scoped salvage |
| **C5 — long holds** | `long_holds` | not collected → window C | — |

## 4. Standing gates on EVERY claim consumption

1. ~~D-088 cl.3(c) three-check bench scan~~ — **LIFTED 2026-08-02**: the
   cooldown-join gauntlet closed (commit 3 merged, PR #93 `cb860e1`);
   the landed machinery now enforces these properties structurally
   (result-map completeness, counting domain, authenticated v2
   discrimination).
2. ~~D-093 raw-vs-validated supersession-record scan~~ — **LIFTED
   2026-08-02** with the gauntlet's close per its row contract; the
   validated reader boundary (PR #91) plus the commit-3 authenticated
   catalog own raw-record visibility permanently.
3. Verdicts consumed as issued; overrides only via the cold-gate path
   with written dissent Ed sees. (UNCHANGED — permanent.)
4. NEW (D-105): while `C3-RECOGNIZER-EXACT-01` is open, the tail
   recognizer's accepted set may only shrink, and the custody sidecar +
   writer-side key assertion may not be weakened.

## 5. DO NOT QUOTE — retired, void, or wrong-as-stated

- **ALL mint #1 floors as claims (D-110, 2026-08-03): operative
  7.377086 J, a10 components 3.823787 / 3.592138 J, window C
  comparative 7.377086 J** — retroactively non-claim-bearing (zero
  allowance where D-102 pin 3 mandates +max(drift, 0.010818 s));
  citable again only after the ruled re-mint under the repaired
  selector.
- **146.730349 J as "the contrast claim"** — it is the
  idle_subtracted_energy_j whole-request diagnostic; the registered
  claim metric is phase_energy_j.decode = 141.29 J (sweep DC-1). Either
  number only as prose with its metric named, neither as a gated claim
  yet.

- **3.17 / 2.94 J** floors — pre-allowance attribution-width
  diagnostics only (D-079 cl.5).
- **3.592138 J as "the decode floor"** — it is the isolated absolute
  component; the operative floor is 7.377086 J (D-084).
- **4.923 J item / 24.62 J suite** comparative floors — Ventura
  screensaver contamination artifacts (2026-07-17 campaign).
- Old window B (`04_phase_prefill_abba`) figures — verdict FAILED
  (`instrument_calibration_mismatch`, GPU DVFM ramp aliasing), corpus
  preserved but not claim-bearing.
- All pre-repair (pre-D-078) powermetrics corpora for claim use —
  time-anchor defect (D-078 soundness gate).
- Window A/B metrology numbers as claims — see §3 (verdicts FAILED as
  issued; window A permanently dead for claims; window B only via a NEW Ed ruling (D-112: the re-evaluation was performed 2026-08-03 and correctly refused; license exhausted as drawn).
- **Window A C1 linearity figures in any claim context** — the corpus
  is design-input/diagnostic only, permanently (D-100 + the immutable
  T1-incompatible retry).

## 6. Instrument findings queued for the paper (not claims yet)

- **Clock-anchor knife-edge** (2026-08-01 Sol consult, accepted): at
  197 s capture length the native-second intersection margin is ~±1 ms
  and the unmodeled wall/monotonic rate (~−12 ppm ≈ 2.3 ms/capture)
  exceeds it; pass/fail is quantization-phase luck. Desk item:
  rate-aware anchor design; directly publishable as a metrology
  limitation/finding.
- **Quiet-state definition**: validated windows now include suspended
  cloud sync (bird-SIGSTOP protocol) — claims describe that controlled
  state, not an arbitrary unattended Mac.
- **Operator-session streaming hazard**: the operating session's own
  output streaming can fail a member's idle admission (window B
  failure #3) — a reproducible environmental-validity observation.

exec
/bin/zsh -lc "nl -ba docs/paper/draft-v1.md | sed -n '80,194p'; nl -ba CLAIMS_STATUS.md | sed -n '1,179p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
    80	### Worst-case timing attribution
    81	
    82	Point repeatability is not the full floor. Each energy value is an interval from the timing calibration in Section 3. The floor computation evaluates the complete point-floor estimator over the joint corners of all member intervals that pass the admission and evidence gates, then takes the largest value. For a null A/B/B/A block, the four signed member intervals are propagated through the contrast together. This corner calculation is deliberately conservative: a systematic boundary-placement error is not independent Gaussian noise, so adding it in root-sum-square form would understate the worst case. The published floor is no smaller than the largest accepted attribution width.
    83	
    84	This calculation revealed a stable and important limitation of the present instrument. Ordinary repeatability is smaller than the uncertainty caused by placing samples at phase edges: approximately one joule can be assigned to the wrong phase when a roughly 30 ms timing uncertainty meets a power change of roughly 33 W. The instrument is therefore *attribution-limited*, not *noise-limited*. More repetitions can refine the repeatability term, but they cannot average away this boundary-placement limit.
    85	
    86	### Measured, never-zero drift allowance
    87	
    88	Drift is a slow change in the machine or measurement response over the collection window. It is measured rather than assumed away. Each prospective window includes three fixed reference runs at the start, one at the midpoint, and three at the end. Gross energy and idle-subtracted energy are treated as separate claim families (idle-subtracted energy is gross energy minus the measured idle mean power multiplied by the phase duration). For each family, the protocol derives a repeatability bound from a settled reference corpus and measures the largest excursion among the start mean, midpoint, and end mean. The allowance is
    89	
    90	\[
    91	A_{\mathrm{drift}}=\max(\text{observed start/mid/end excursion},
    92	\text{derived reference-repeatability bound}).
    93	\]
    94	
    95	Consequently, a passing drift screen never means zero drift. The allowance remains positive even in an exceptionally stable window, and the midpoint protects against an interior excursion that similar endpoints would miss. No duration-scaling law is applied because the available evidence does not identify a physical law relating drift to elapsed time.
    96	
    97	For each absolute or comparative component, the guarded, corner-widened value is increased once by its matching drift allowance. The operative floor for a cell is then
    98	
    99	\[
   100	F_{\mathrm{cell}}=\max(F_{\mathrm{abs}},F_{\mathrm{cmp}}),
   101	\]
   102	
   103	not their sum. Cross-window components keep their own calibration basis and allowance; an allowance is never added again at the cell or reporting level. Operative floor values and their full decomposition for each demonstration stack are withheld here until the corrected artifacts are issued: **[RESULT PENDING RE-MINT]**.
   104	
   105	### LABELLED publication and the effective decision bar
   106	
   107	When timing attribution dominates, the floor remains publishable only through the **LABELLED** path. Every artifact and reader-facing result must identify the limit as attribution-limited, publish the corner-widened value rather than the smaller point diagnostic, retain the point-only repeatability number as a non-publishing diagnostic, and carry `floor_source = E_clock_anchor_shift_bound_j`. This field names energy uncertainty caused by shifting the phase edges within the calibrated clock-anchor bound as the dominant term. The label prevents a precise repeatability number from masquerading as the instrument's total resolving power.
   108	
   109	The floor is only one side of a claim decision. The calibrated floor bounds a false effect produced by the calibration condition; the confidence or decision interval for the particular measured contrast separately carries that contrast's timing-attribution uncertainty. These are distinct uses of the same physical uncertainty and both are required. The effective bar is therefore
   110	
   111	\[
   112	\text{effective clearable effect}=F_{\mathrm{cell}}+B_{\mathrm{claim}},
   113	\]
   114	
   115	where \(B_{\mathrm{claim}}\) is the claim-side measurement bound. For the measured phase-contrast regime, this combined bar is approximately 5 J. Neither term may be removed as an apparent double count. Effects below the floor are reported as *not resolvable*, not as zero, equal, or evidence of no difference. A directional claim is made only when the effect and its interval clear the applicable bar.
   116	
   117	## 5. Fail-closed collection protocol (C-iii)
   118	
   119	*Fail-closed* means that missing, inconsistent, stale, or contaminated evidence produces a refusal rather than an optimistic default. The collection unit is one uninterrupted two-to-four-hour window with one power state, one instrument identity, fresh calibration before and after, a fresh drift-bound corpus, and one verdict over the exact member set. Work that does not fit with at least a 20% failure margin is split prospectively into another independently calibrated window.
   120	
   121	### Pre-registration and admission
   122	
   123	Before quiet time, the operator freezes the run identifiers, membership, stage order, comparison definitions, calibration retry count, acceptance thresholds, extraction specification, code revision, and an initially empty waiver list. Every configuration is validated and dry-run against a fresh output root. These choices are made before outcomes are visible. Pre-registration here is executable: the launcher and final verifier check the frozen values rather than relying on a narrative promise.
   124	
   125	Each stage then passes admission gates immediately before measurement. The approved power supply and power policy must be unchanged; displays must be asleep; the screensaver and low-power mode must be off; thermal pressure must be nominal; and central- and graphics-processor activity must meet the quiet-state criteria. Known background work is allowed to finish before the window, followed by a settling interval, rather than being ignored during analysis. Runtime and telemetry identities, clock anchoring, sample cadence, calibration freshness, and post-run environment observations are also checked. No environment override can produce a claim-bearing member.
   126	
   127	### Counterbalanced order
   128	
   129	Comparisons use A/B/B/A blocks, abbreviated **ABBA**. Conditions A and B are measured in the order A, B, B, A, with ordinary cooldown between members. Averaging the two outer A observations and the two inner B observations cancels a linear time trend within the block to first order. For null-floor calibration, A and B are aliases of the exact same configuration and payload, so any nonzero block delta is a false comparative effect. For scientific contrasts, the A and B definitions are frozen in advance, and the contrast is computed within each block before blocks are aggregated. ABBA reduces common drift; it does not replace the measured whole-window drift allowance.
   130	
   131	### Evidence custody and refusals
   132	
   133	Every member is a self-contained bundle of configuration, raw power trace, runtime events, environment observations, and derived summary. Cryptographic hashes bind those files to the campaign manifest. Failed or interrupted artifacts are never deleted or overwritten. An occupied retry slot is moved to a quarantine area outside the active runs root; the exact member is recollected only under an allowed retry; and an append-only supersession record names which occurrence governs. Two present bundles for one occurrence refuse. The final whole-window verdict binds the exact member-occurrence set, calibration bracket, policy, and drift evidence by hash, so a later consumer cannot silently select a more favorable subset.
   134	
   135	Collection does not continue indefinitely through environmental interruptions. Each stage attempt stops at its first member failure, and after the same cause fails a window stage for the third time the window itself closes rather than being retried; in actual operation, nights with three environmental member interruptions were closed and preserved as salvage rather than repeatedly retried. The surviving data may remain diagnostic, but it becomes claim-bearing only if the pre-registered verdict and extraction rules accept the exact resulting basis. This abandon-after-three rule limits outcome-dependent retrying and makes the cost of a noisy environment visible.
   136	
   137	The custody chain continues after collection. The immutable corpus is backed up before extraction. The extractor re-authenticates member hashes, required files and cross-file consistency, calibration identity, environment admission, complete campaign membership, cooldown evidence, phase metric identity, and the whole-window drift allowance. It excludes or refuses a cell according to the frozen rules; missing uncertainty never becomes zero. The current artifact boundary is stated honestly: until floor artifacts are independently bound to their source extraction, a claim-bearing floor must be produced by protocol-controlled extraction in the same controlled custody session as the analysis that consumes it. A standalone floor file is not independently claim-licensing.
   138	
   139	The refusal log is part of the evaluation, not an embarrassment to omit. It records contaminated members, out-of-family calibration, stale drift evidence, unresolved clock anchors, duplicate occurrences, and below-floor effects. In one real end-of-night case, the governed re-evaluation refused a window because a member's internal clock alignment could not be resolved. Independent adjudication found that refusal correct. The result remained non-claim-bearing: an example of the fail-closed design working as intended, not a software defect to be bypassed.
   140	
   141	## 6. Instrument characterization (C-iv)
   142	
   143	Instrument characterization asks whether the complete measurement system behaves predictably when driven by signals whose qualitative answer is known in advance. The workload is therefore a test signal, not yet the scientific finding. All tests retain the same calibration, admission, custody, and floor rules as the later demonstration measurements. Existing campaign fragments are not promoted where the governing whole-window verdict did not pass; the table marks the required claim-bearing results explicitly.
   144	
   145	| Property | Characterization method | What a passing result would establish | Claim-bearing result |
   146	|---|---|---|---|
   147	| Linearity | Hold the prompt profile fixed and ramp the requested output from 128 to 2048 tokens. Regress gross request and decode energy on the runtime-observed output count; inspect residual structure as well as the fitted slope. | Energy responds proportionally over the tested dynamic range, and the fitted per-token slope can serve as the known-effect standard for floor probes on this stack. It would not establish linearity outside the tested range or on another stack. | **[PENDING WINDOW C]** |
   148	| Null response across magnitudes | Run identical A-equals-B ABBA blocks at short, medium, and long output magnitudes. Evaluate the paired deltas against zero and against the predicted decision envelopes. | The comparison path does not create a directional effect merely because total energy or duration changes, and false contrasts across the tested range are contained by the error model. A non-significant result alone is insufficient; the interval must be interpreted relative to the floor. | **[PENDING WINDOW C]** |
   149	| Empirical floor verification | Use the pre-registered linearity slope to create micro-deltas with predicted effects near 0.5, 1, 1.5, and 3 times the declared floor. Test positive and negative directions in counterbalanced blocks. | Sub-floor effects are refused while sufficiently super-floor effects clear in both directions. This is an operational check of the detection boundary, not a validation of the counter's absolute gain. | **[PENDING WINDOW C]** |
   150	| Phase-attribution causal consistency | First compare the sum of separately integrated phase energies with the gross energy over their enclosing request. Then vary output length while holding prompt tokens fixed and fit the slope of prefill energy against output length. | Phase accounting is additive within its stated boundaries, and energy assigned to prefill does not acquire a systematic dependence on work that occurs later in decode. Together these tests challenge both missing energy and cross-phase leakage. | **[PENDING WINDOW C]** |
   151	| Drift and settling | Place long controlled holds and fixed reference workloads through the window, including start, midpoint, and end references. After operator or stage activity, repeat the reference while recording the time required for thermal and admission observables to stabilize; compare it with the 180 s operating convention. | The measured drift trajectory is contained by the published allowance, and the chosen settling time is supported or revised from observed recovery rather than convenience. Endpoint agreement alone is not enough if the midpoint reveals curvature. | **[PENDING WINDOW C]** |
   152	| Between-session stability | Repeat calibrations, null blocks, and floor cells across at least three sessions or days with the full stack identity recorded. | The calibration and floor are stable enough to reuse only under their declared freshness and identity rules, or reveal that a new session must mint a new floor. | **[PENDING WINDOW C]** |
   153	
   154	Linearity and the null ladder test complementary failure modes. A smooth response can still carry an offset, and a zero-centered null can coexist with a nonlinear scale. The micro-delta experiment then closes the loop by using the measured slope to place effects deliberately below and above the declared decision boundary. Success requires the instrument to refuse the former and resolve the latter in both directions; merely observing larger effects with larger workloads is not sufficient.
   155	
   156	The causal tests address the most important phase-specific risk. Additivity checks conservation inside the declared request boundary: phase intervals should reconcile with the enclosing total, subject to explicitly labeled setup or gap intervals. Causal invariance checks direction: holding the prompt fixed while increasing later decode work should not change energy attributed to earlier prefill. A nonzero prefill slope would indicate boundary leakage, shared-state coupling that invalidates the simple phase model, or both; it would narrow the claim rather than be explained away.
   157	
   158	Temporal characterization separates slow drift from thermal settling. Start, midpoint, and end references expose whole-window curvature, while post-transition references estimate how long the system takes to return to its admitted state after operator activity or stage churn. Repetition across days tests whether one session's calibration is representative under identical recorded bindings. Internal channel-sum versus package reconciliation is retained as a secondary consistency check. External wall-power regression remains conditional on a suitable meter and would validate totals only; the pulse experiment remains the evidence for phase splitting.
   159	
   160	Every resulting figure and table will identify the physical unit, operating-system version and build, runtime and relevant library versions, model artifact hash, quantization, tokenizer identity, sampler and output policy, configured and realized batch/concurrency policy, measurement boundary, and telemetry backend. Silent omission is not permitted. Measurements support stack-specific conclusions only; independent replication or a calibrated boundary bridge would be required for hardware-class, vendor-class, or cross-boundary rankings.
   161	
   162	## 7. Demonstration results (C-v)
   163	
   164	**[RESULT PENDING RE-MINT]**
   165	
   166	This section will report phase-resolved gross joules per request for two model sizes, with tokenizer-scoped joules per prompt token and per output token as companion metrics. It will contain the pre-registered same-boundary model-size contrast, its interval, the complete floor decomposition, the claim-side bound, the effect-to-floor ratio, and the final resolvable/unresolved verdict. No demonstration energy value from the superseded mint is carried into this draft. A quantization ladder will be included only if it is collected under its own stack-specific floors and the frozen window budget permits it.
   167	
   168	## 8. Related work
   169	
   170	### LLM inference energy measurement
   171	
   172	TokenPowerBench provides one of the closest reporting structures: it separates prompt-processing and token-generation energy, uses phase-appropriate token denominators, and groups results by context length [TokenPowerBench]. Its disclosed method, however, does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation, and continuous batching makes an “active phase” label difficult to interpret when requests overlap. JouleWise adopts phase-specific reporting but restricts its primary scope to one sequential request, where runtime-emitted phase boundaries are well posed and can be calibrated.
   173	
   174	The Illusion of Power Capping in LLM Decode samples graphics-processor power, integrates those samples, repeats configurations, and cross-checks sufficiently long operations against a separate hardware energy counter [IllusionPowerCapping]. This is a stronger measurement template than an unqualified software reading. Its counter agreement, run-to-run variation, snapshot fallback, and timing alignment nevertheless remain separate diagnostics rather than one bound on the reported effect, and its long sweeps do not use a drift-control ordering. JouleWise composes those classes of uncertainty into a decision rule for each contrast.
   175	
   176	Apple-focused system comparisons reinforce the need for boundary labels. Silicon Showdown compares a graphics-board boundary on one platform with a whole-system-on-chip `powermetrics` boundary on Apple hardware, while runtimes and precision stacks also differ [SiliconShowdown]. Intelligence-per-Watt and ML.ENERGY similarly emphasize breadth across deployed inference configurations [IntelligencePerWatt; MLENERGY]. Such studies answer valuable systems questions, but unlike boundaries and software stacks cannot by themselves support a hardware-class causal ranking. JouleWise therefore makes the named stack and measurement boundary part of every result and prioritizes within-boundary effects.
   177	
   178	### Software power counters and measurement standards
   179	
   180	RAPL in Action established a validation agenda for commodity software counters: align lag before comparing streams, model wall power rather than assuming identity, account for temporal correlation, warm the system, measure sampler overhead, and inspect update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. Jay and Ostapenco likewise regress software readings against wall power and show that disagreement varies with load; they avoid claims about subtotals that the reference meter cannot observe [JayOstapenco]. JouleWise follows this epistemic boundary. A future external meter could test total gain and load dependence, but it would not validate how a total is divided between prefill and decode. The in-window pulse train addresses that distinct question.
   181	
   182	MLPerf Power and SPEC require load-specific analyzer uncertainty, fixed ranges, clock synchronization, minimum intervals, invalid-sample accounting, and controlled battery behavior [MLPerfPower]. JouleWise translates their per-run reject-on-missing-evidence principle to a consumer software counter. The difference is that its principal uncertainty is not only an analyzer specification; it includes whether samples at a software-defined phase edge belong inside or outside the integral.
   183	
   184	### Metrology and experimental discipline
   185	
   186	Prospective paired minimum-detectable-effect methods estimate the smallest effect a planned paired study has adequate statistical power to find. They size the study from the variance of paired differences and can impose a one-way prior ratchet: observed variability may raise the planned threshold but may not lower it after outcomes are seen [PairedMDE]. JouleWise uses that logic for prospective workload sizing, but it does not treat the worst-case attribution term as independent random noise. Root-sum-square composition would be anti-conservative for a systematic edge-placement bound. Instead, the analysis maximizes over calibrated edge positions, measures drift with bracketed references, and publishes the resulting floor with the effect.
   187	
   188	This emphasis changes the role of failed runs. A rejected admission, stale calibration, contaminated member, or below-floor contrast is evidence about the instrument's operating domain. Hash-bound raw traces, runtime events, configurations, supersessions, verdicts, and pre-registration records make that evidence re-reducible. The refusal is retained rather than disappearing behind a final average.
   189	
   190	### Split and disaggregated inference
   191	
   192	Split, or disaggregated, inference places prompt processing and token generation on different devices and transfers intermediate state between them. Revisiting Disaggregation Energy reports that the energy outcome depends on load, baseline, and transfer conditions on its evaluated two-graphics-processor node [RevisitingDisaggregationEnergy]. DualScale studies phase placement and per-phase power control on homogeneous server hardware [DualScale]. Prima.cpp includes whole-run energy and communication accounting but not a per-stage energy split [PrimaCPP], while SplitZip characterizes lossless transfer compression without making an energy claim [SplitZip].
   193	
   194	JouleWise does not claim a new split scheduler in this paper. Split inference is instead a demanding future demonstration of the instrument because it introduces two physical boundaries, a transfer interval, and clock alignment across devices. A valid comparison would have to measure both ends, name each boundary, and clear a pre-registered floor or calibrated bridge. Whether splitting saves energy remains an empirical outcome; the reusable contribution is a method that can issue, qualify, or refuse the result.
     1	# Claims Status
     2	
     3	**The single standing home for "what can we actually claim right now."**
     4	Every scientific number the project can publish, is holding, or must not
     5	repeat — with its exact validity state and blocker. Refresh this file
     6	whenever claim-bearing state changes (a verdict, a mint, a merge in the
     7	D-095 chain, an adjudication); quote verdicts as issued, never
     8	reinterpreted. Companion docs: `RUN_STATE.md` (session pointer),
     9	`WINDOW_STATUS.md` (machine state), `docs/decision_log.md` (policy).
    10	
    11	Last updated: **2026-08-07** (D-117: the historical re-mint path is
    12	SUPERSEDED — structurally closed at main after the D-116 issuance
    13	(candidate discovery excludes import-marked receipts by design); the
    14	claim path forward is THREE PROSPECTIVE WINDOWS — fresh 1.5B decode
    15	floor, fresh 7B decode floor, fresh decode contrast — live-bracketed
    16	under the issued acceptance regime, with prefill floor cells riding
    17	both floor windows. Prior "re-mint conditions" in this file are
    18	historical: D-109 landed (PR #100), issuance executed (D-116, PR #109),
    19	validator pin widening landed (PR #105). Full record:
    20	`docs/process_traces/2026-08-06-d110-remint-fork/`.)
    21	
    22	Earlier header (2026-08-03 night, for the record): D-108/D-109 ruled +
    23	executed; D-110 made mint #1 retroactively NON-CLAIM-BEARING; window B
    24	re-evaluation STOPPED → D-112; mint-1 re-derivability proven
    25	byte-identical; report: `docs/run_reports/2026-08-03-16h-runway.md`.
    26	
    27	---
    28	
    29	## 1. VALID — minted, mainline, citable
    30	
    31	**NONE at this checkpoint.** D-110 (2026-08-03, sweep finding RT-1)
    32	made mint #1 and every number derived from it retroactively
    33	non-claim-bearing: its floors embed a never-zero allowance of ZERO
    34	where D-102 pin 3 mandates +max(drift, 0.010818 s) (~+43% on the a10
    35	operative bound). The previously-listed values (operative 7.377086 J;
    36	a10 components 3.823787 / 3.592138 J; window C comparative 7.377086 J)
    37	move to §5 until the re-mint. The DERIVATION toolchain itself is
    38	proven honest: the full pinned replay (2026-08-03) reproduced both
    39	extraction reports, the artifact, and the statement BYTE-IDENTICAL
    40	(`docs/process_traces/2026-08-03-q1-remint-bytecompare/`). The taint is
    41	semantic (the selector the era used), not derivational.
    42	**2026-08-07 (D-117):** the historical re-mint order is SUPERSEDED —
    43	all three former re-mint conditions completed (D-109 via PR #100;
    44	issuance via D-116/PR #109; pin widening via PR #105) and the FIRST
    45	consumption attempt then proved historical consumption structurally
    46	closed at main. Replacement: three prospective windows (D-117 cl.2);
    47	the never-zero allowance correction binds their mints. All four PASSED
    48	window verdicts remain untainted (sweep RT-5), but pre-genesis windows
    49	CANNOT be claim-consumed — their role is diagnostic and
    50	rule-establishing only.
    51	
    52	**Standing measurement fact (D-078 cl.11, Ed-ratified):** the instrument
    53	is attribution-limited (~1 J), not noise-limited (~0.3 J). Floors
    54	publish LABELLED with the widened number; the effective clearable
    55	effect for phase contrasts is floor + claim-side bound ≈ 5 J. No
    56	instrument-tightening program.
    57	
    58	## 2. EVIDENCE-BEARING — collected and verdict-PASSED, awaiting a specific gate
    59	
    60	| Candidate claim | Value (prose-only until gated) | Window / verdict | Blocker |
    61	|---|---|---|---|
    62	| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
    63	| **1.5B-vs-7B decode contrast** (demonstration study #1) | **Registered claim metric (frozen v3 manifest): `phase_energy_j.decode`, 7B−1.5B = 141.29 J per block.** The widely-quoted 146.730349 J (σ 0.241 J, n=10 ABBA) is the `idle_subtracted_energy_j` whole-request DIAGNOSTIC — quote it only labelled as such, never as the claim (sweep DC-1; both reproduce byte-exactly from disk). | `window_contrast_20260730`, **PASSED** | **RE-SCOPED by D-117 (2026-08-07):** `window_contrast_20260730` is pre-genesis and cannot be claim-consumed; values are DIAGNOSTIC and the design template for the fresh contrast window (D-117 cl.2). The D-095 chain now runs through the prospective windows' mints. |
    64	
    65	## 3. COLLECTED — verdicts FAILED as-issued; adjudication RULED (D-100, 2026-08-01)
    66	
    67	The machinery adjudication is complete (MET-VERDICT-ADJ-01 → D-100 cold-
    68	gate synthesis). Both verdicts **stand as issued, permanently by
    69	construction**: any licensed re-evaluation appends a NEW row under
    70	`consumption_semantics_id: salvage_dangler_exclusion_v1` with a new
    71	pinned basis; the original FAILED rows are never edited and govern
    72	default consumption. Outcomes per window:
    73	
    74	- **Window A: permanently non-claim-bearing.** Its only post-cal retry
    75	  binds a T1-incompatible power-policy identity (immutable evidence; the
    76	  machinery's rejection was CORRECT), so no calibration bracket can ever
    77	  form. C1 re-collects in a future window.
    78	- **Window B: TERMINALLY CLAIM-RETIRED (D-113, Ed ruling 2026-08-05):
    79	  RETAINED_IMMUTABLE / PERMANENTLY_NON_CLAIM_BEARING.** Ed chose
    80	  abandonment over salvage ("soundness and quality of the project and
    81	  claims above all"): no re-evaluation or claim consumption will ever
    82	  occur; the WB-specific D-100/D-106/D-108 license chain is retired
    83	  (general machinery survives for other windows);
    84	  `WINB-R06-DISPOSITION-01` closes ABANDONED_FOR_FRESH_COLLECTION;
    85	  labelled read-only forensic/diagnostic use remains permitted ("Window
    86	  B, original verdict FAILED, D-113 claim-retired, non-claim
    87	  evidence"). Every still-desired WB claim component re-collects fresh
    88	  beginning Window C — no WB member enters a replacement claim basis.
    89	  The F7 scope question is ANSWERED: whole-window voiding is affirmed
    90	  as the current semantics (a cell-scoped alternative only via the
    91	  D-083 cold gate; not built). Historical record of the 2026-08-03
    92	  attempt below. The whole chain executed: D-108 ruled
    93	  (clause (c) retired), row `D100-BII-BINDING-01` CLOSED (PR #99 +
    94	  clause-(d) three-occurrence digest-bound re-record), closure +
    95	  membership-binding artifacts authored and dry-authorized, D-093 scan
    96	  clean 1/1, frozen corpus verified byte-identical (210+4 files, zero
    97	  mismatches). The governed re-evaluation then REFUSED pre-verdict:
    98	  survivor consumption failed on `mtadd-p2048o0128-r06`'s
    99	  collection-time clock-anchor failure (`native_intersection_empty`) —
   100	  the cold gate ruled this CORRECT fail-closed machinery (classification
   101	  (i), convergent instruments; record
   102	  `docs/process_traces/2026-08-03-winB-reeval-stop/`). No licensed
   103	  channel removes r06 (exclusion cap spent on r08; not a dangler;
   104	  waivers forbidden), and the NEG-8 drift bound expired 2026-08-02, so
   105	  no PASS path exists under the license as drawn. Original FAILED
   106	  verdict untouched. The WB NEG-8 bound re-mint obligation is MOOT
   107	  under D-113; the near-run-time freshness rule continues to bind
   108	  every future window (runbook + D-078, by cross-reference).
   109	
   110	| Paper claim | Campaign | Collected | State after D-100 |
   111	|---|---|---|---|
   112	| **C1 — linearity** | `linearity_ramp` | **40/40** (window A) | DEAD for claims (window A permanent FAIL); re-collect (window C/D); data usable as design input (micro_delta slope) + corroboration diagnostics only |
   113	| **C2 — null ladder** | `null_ladder` | o0128 + o0512 collected in window B — **returned to uncollected-for-claim state (D-113)**; o2048 never collected | Re-collect ALL of C2 fresh (window C, or split per the frozen plan); no WB member enters a replacement claim basis |
   114	| **C3 — micro-delta** | `micro_delta` | not collected | Plan is draft-pending-slope by design; slope fit may consume window A ramp as DESIGN input (not a claim) |
   115	| **C4 — additivity** | `additivity_shapes` | 23/24 single-root collected in window B — **returned to uncollected-for-claim state (D-113)**; 21/24 window-A corroborating remain labelled non-claim diagnostics | Re-collect C4 fresh (window C/D per the frozen plan). F7 ANSWERED by D-113: whole-window voiding affirmed as current semantics; no cell-scoped salvage |
   116	| **C5 — long holds** | `long_holds` | not collected → window C | — |
   117	
   118	## 4. Standing gates on EVERY claim consumption
   119	
   120	1. ~~D-088 cl.3(c) three-check bench scan~~ — **LIFTED 2026-08-02**: the
   121	   cooldown-join gauntlet closed (commit 3 merged, PR #93 `cb860e1`);
   122	   the landed machinery now enforces these properties structurally
   123	   (result-map completeness, counting domain, authenticated v2
   124	   discrimination).
   125	2. ~~D-093 raw-vs-validated supersession-record scan~~ — **LIFTED
   126	   2026-08-02** with the gauntlet's close per its row contract; the
   127	   validated reader boundary (PR #91) plus the commit-3 authenticated
   128	   catalog own raw-record visibility permanently.
   129	3. Verdicts consumed as issued; overrides only via the cold-gate path
   130	   with written dissent Ed sees. (UNCHANGED — permanent.)
   131	4. NEW (D-105): while `C3-RECOGNIZER-EXACT-01` is open, the tail
   132	   recognizer's accepted set may only shrink, and the custody sidecar +
   133	   writer-side key assertion may not be weakened.
   134	
   135	## 5. DO NOT QUOTE — retired, void, or wrong-as-stated
   136	
   137	- **ALL mint #1 floors as claims (D-110, 2026-08-03): operative
   138	  7.377086 J, a10 components 3.823787 / 3.592138 J, window C
   139	  comparative 7.377086 J** — retroactively non-claim-bearing (zero
   140	  allowance where D-102 pin 3 mandates +max(drift, 0.010818 s));
   141	  citable again only after the ruled re-mint under the repaired
   142	  selector.
   143	- **146.730349 J as "the contrast claim"** — it is the
   144	  idle_subtracted_energy_j whole-request diagnostic; the registered
   145	  claim metric is phase_energy_j.decode = 141.29 J (sweep DC-1). Either
   146	  number only as prose with its metric named, neither as a gated claim
   147	  yet.
   148	
   149	- **3.17 / 2.94 J** floors — pre-allowance attribution-width
   150	  diagnostics only (D-079 cl.5).
   151	- **3.592138 J as "the decode floor"** — it is the isolated absolute
   152	  component; the operative floor is 7.377086 J (D-084).
   153	- **4.923 J item / 24.62 J suite** comparative floors — Ventura
   154	  screensaver contamination artifacts (2026-07-17 campaign).
   155	- Old window B (`04_phase_prefill_abba`) figures — verdict FAILED
   156	  (`instrument_calibration_mismatch`, GPU DVFM ramp aliasing), corpus
   157	  preserved but not claim-bearing.
   158	- All pre-repair (pre-D-078) powermetrics corpora for claim use —
   159	  time-anchor defect (D-078 soundness gate).
   160	- Window A/B metrology numbers as claims — see §3 (verdicts FAILED as
   161	  issued; window A permanently dead for claims; window B only via a NEW Ed ruling (D-112: the re-evaluation was performed 2026-08-03 and correctly refused; license exhausted as drawn).
   162	- **Window A C1 linearity figures in any claim context** — the corpus
   163	  is design-input/diagnostic only, permanently (D-100 + the immutable
   164	  T1-incompatible retry).
   165	
   166	## 6. Instrument findings queued for the paper (not claims yet)
   167	
   168	- **Clock-anchor knife-edge** (2026-08-01 Sol consult, accepted): at
   169	  197 s capture length the native-second intersection margin is ~±1 ms
   170	  and the unmodeled wall/monotonic rate (~−12 ppm ≈ 2.3 ms/capture)
   171	  exceeds it; pass/fail is quantization-phase luck. Desk item:
   172	  rate-aware anchor design; directly publishable as a metrology
   173	  limitation/finding.
   174	- **Quiet-state definition**: validated windows now include suspended
   175	  cloud sync (bird-SIGSTOP protocol) — claims describe that controlled
   176	  state, not an arbitrary unattended Mac.
   177	- **Operator-session streaming hazard**: the operating session's own
   178	  output streaming can fail a member's idle admission (window B
   179	  failure #3) — a reproducible environmental-validity observation.

codex
The core evidence is already forcing a narrower paper than the direction’s label suggests: the repository’s validated stack is Qwen2.5/MLX, where “GQA” is a model-architecture property rather than a runtime switch, and KDA is not yet an established drop-in path. I’m checking the frozen three-window budgets and the research registry now so the proposal distinguishes a fundable same-stack attention study from comparisons that would confound model family, quality, or runtime.
exec
/bin/zsh -lc "sed -n '1,170p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md; sed -n '171,340p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md; sed -n '341,520p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Complete D-117 freeze design: three prospective windows fit the envelope, but live-ledger sessions, multi-cell minting, and D-102 successor generation must land before any arm.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "dbb9685669ac76ea65bf458b78eeb98d94bc6a80",
    "head_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "upstream_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The current ledger cannot safely reserve both bookend observations under one unchanged committed head",
        "detail": "The append path requires the physical ledger head to equal the committed pin before each reservation. Finalizing the pre observation advances the physical head, so an ordinary post reservation cannot occur without an intervening pin advance or a new bracket-session capability.",
        "recommendation": "Implement an atomic two-slot bracket-session capability plus exact postcollection bracket binding before freezing arm packets."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The generalized mint is still decode-only and single-plan/single-cell",
        "detail": "The current generalized path hard-checks phase_energy_j.decode and a decode phase target. It cannot mint the two prefill riders or D-095's required combined multi-cell, multi-plan floor artifact.",
        "recommendation": "Introduce pinset v2 with per-plan component pins and an aggregate four-cell artifact pinset."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "No usable D-102 successor-artifact path exists for a live-prefixed ledger",
        "detail": "The issued acceptance artifact is exact-byte pinned and prior-set verification assumes the issuance corpus. A valid range-expanding live observation could therefore stop a campaign before member one or prevent its verdict.",
        "recommendation": "Pre-build and cold-gate a deterministic successor builder, registry, live-prefix verification, and trigger-time operator procedure."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The referenced prefill-feasibility synthesis is absent at the inspected HEAD",
        "detail": "docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md does not exist in this worktree even though RUN_STATE says the trace was custodied.",
        "recommendation": "Recover or commit the trace before lead ratification; this memo uses D-117's adopted summary as authority."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "Current queue rows still encode superseded C/D and D-110 gates",
        "detail": "TASK_QUEUE.md still presents MET-WINDOW-C-01 and MINT-GENERALIZE-01 under terminology and blockers superseded by D-117.",
        "recommendation": "Regenerate queue/state views from the owning state kernel after the plan-freeze decision is ratified."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "94a24e562290b59f7b40908315bbae7a032ea47e",
          "94a24e562290b59f7b40908315bbae7a032ea47e"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "94a24e562290b59f7b40908315bbae7a032ea47e$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "test -f docs/decision_log.md && test -f docs/process_traces/2026-08-06-d110-remint-fork/CONSULT-RESPONSE.md && test ! -e docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "FLAG1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "main advanced concurrently from dbb9685 to 94a24e5 during the read-only consult; the final state was re-inspected and remained clean.",
      "needs": "Freeze implementation scopes against 94a24e5 or a later explicitly reviewed head."
    },
    {
      "id": "FLAG2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No suites were run because this was a read-only design consult with no implementation.",
      "needs": "Each implementation unit below carries focused and canonical-suite obligations."
    }
  ]
}
```

## Findings

### F1 — Live-ledger bookending is not yet armable (blocker)

D-116’s issued ledger is the correct trust root, and D-117 correctly requires fresh live pre/post observations. The obstacle is mechanical: the present append path requires the physical ledger head to match the committed pin when reserving an attempt. Once the pre observation is finalized, that equality no longer holds for an ordinary post reservation.

The best design is an atomic `calibration_window_bracket_session.v1` capability:

1. At the pre-bookend, under a clean committed head, append one receipt reserving exactly two immutable slots: `pre` and `post`, each with its attempt ID, plan ID/SHA, evidence-root ID, expected time role, and shared session ID.
2. Finalize the pre slot before member one.
3. Leave the post slot prospectively open without treating it as an unresolved candidate or permitting claim evaluation.
4. Finalize or explicitly abort the post slot at the closing bookend.
5. Commit the terminal ledger head once, then issue an exact `calibration_bracket_binding.v1` mapping the frozen plan and evidence root to the two finalized content/receipt digests.
6. Candidate discovery still examines the complete live candidate universe; the binding selects the claimed pair but cannot hide extra candidates.

This is preferable to a source commit after the pre observation: that would mutate the repository and readiness head inside every quiet-window procedure. Two ordinary reservations appended in advance are also inferior because the outstanding post reservation would look unresolved unless ledger semantics were widened anyway.

Base plans should freeze calibration retry count at zero. A failed pre observation aborts before member one and closes the unused post slot; a failed post makes the physical attempt non-claim-bearing. If the lead wants one cause-removal retry, the session capability needs additional prospectively numbered slots and deterministic selection semantics before freeze—never an improvised retry.

Ideal no-failure receipt evolution from the issued sequence-76 head is three receipts per window—session capability, pre finalization, post finalization—ending at sequence 85 after all three windows. Exact sequence numbers are arm-time facts, not desk-frozen plan literals.

### F2 — The mint path needs a real v2, not another widened literal list (blocker)

The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:

- one plan and one artifact cell;
- `phase_energy_j.decode` only;
- `["phase","decode"]` only;
- no aggregate artifact over independently collected plans.

D-095 requires one multi-cell floor artifact whose 1.5B and 7B cells remain independently stack-scoped. D-117 adds prefill cells to both floor plans. The correct closure is therefore one four-cell artifact, not two loosely associated artifacts:

| Cell | Producer | Metric | Scientific family |
|---|---|---|---|
| 1.5B decode | 1.5B floor plan | `phase_energy_j.decode` | existing `df-ph-decode` |
| 1.5B prefill rider | 1.5B floor plan | `phase_energy_j.prefill` | new exact rider family |
| 7B decode | 7B floor plan | `phase_energy_j.decode` | D-085 `df-ph-decode-qwen25-7b` |
| 7B prefill rider | 7B floor plan | `phase_energy_j.prefill` | new exact rider family |

Each producer gets a component pinset; an aggregate pinset hard-checks both components and mints `d117-qwen25-phase-floor-set-v1`. Gamma consumes the two decode cells through D-095’s predeclared transport groups. It does not relabel contrast configs as floor configs.

### F3 — The D-102 successor packet is a pre-arm dependency (blocker)

A valid pre calibration can expand the observed range or approach the valid-observation limit. The issued artifact cannot absorb that live prefix today. The campaign therefore needs the following on disk and cold-gated before its first §5A arm:

- deterministic successor builder and validator;
- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
- generalized prior-set validation over a complete authenticated import-plus-live prefix;
- exact Decimal arithmetic, rounding, budget, prediction, and screen reproduction from D-079;
- a dry-run fixture that produces exact successor bytes and expected head pin;
- trigger-disposition logic that judges the range-expanding observation under the prior artifact before incorporating it into the successor;
- operator commands for pre-trigger and post-trigger branches.

I recommend deriving a successor from all content-distinct, valid, same-epoch observations through the chosen cutoff. Systematic, ordinary-invalid, aborted, or unresolved attempts remain recorded but excluded. The lead should explicitly ratify that corpus rule because D-102 establishes the successor obligation but does not fully spell out this live-prefix derivation policy.

At the pre bookend, a range expansion stops the chain before member one: close or preserve the bracket session according to the frozen state machine, commit the current ledger head, build and authenticate the successor, revalidate, then proceed. A post range expansion follows the same process after science but before the verdict. Systematic mismatch is a refusal, never something a successor can launder.

### F4 — Referenced trace missing (should-fix)

The named `docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md` is absent at `94a24e5`. D-117 itself records the adopted conclusion, so this memo treats the following as governing:

- floor prefill cells ride the floor-window decode members;
- gamma remains decode-only;
- the historical 128-token prefill contrast was marginal;
- a prospectively frozen 256-token contrast remains Ed’s option.

The missing trace prevents verification of any additional numerical assumptions it may contain. In particular, this memo does not freeze a 256-token runtime or effect-size target.

### F5 — Queue terminology is superseded (should-fix)

`TASK_QUEUE.md` still carries `MET-WINDOW-C-01`, prospective “C/D” splitting, and an old `MINT-GENERALIZE-01` D-110 blocker. Those rows cannot govern this work. D-117 clause 5 owns the namespace, and the live `RUN_STATE.md` block now recognizes that ruling. The queue should be regenerated after ratification, not manually interpreted during arm readiness.

### Ranked design decisions and rejected alternatives

1. **Use a two-slot ledger session capability and exact bracket binding.** Rejected: implicit reuse of neighboring observations, mid-window Git pin commits, or pre-reserving ordinary unresolved observations.

2. **Mint one four-cell floor artifact through pinset v2.** Rejected: two unrelated floor artifacts, summing arm floors, or weakening D-095’s independently stack-scoped maximum.

3. **Freeze zero calibration retries in the base plans.** Rejected: unbounded cause-removal retries and post hoc choice among observations. A retry-enabled variant requires a different capability state machine before freeze.

4. **Make prefill a metric rider over the exact decode members.** Rejected: copying the old dedicated 4096-prompt/64-output prefill workload, because that would add members and estimate a different condition. Post hoc extraction without a pre-registered cell is also insufficient.

5. **Treat the 256-token contrast as a fourth window plan.** Rejected: appending it to gamma later, which would change gamma’s plan SHA, member universe, order, multiplicity, runtime, and verdict basis.

6. **Use semantic immutable identifiers without dates or letters.** Rejected: `Window D`, C/D, and date-derived identities. Attempt dates belong in custody metadata, not scientific identity.

7. **Use a two-stage pin freeze.** Desk time freezes every knowable identifier, schema, member list, hash, and rule. Six-decimal operative values freeze only after governed collection and extraction. Rejected: placeholder literals presented as valid pins or any mint-time derivation.

### Proven template lineage

The templates are scientific and structural sources, not claim evidence.

| Plan | Files treated as the proven template | What is reused |
|---|---|---|
| 1.5B floor | `configs/campaigns/p2_015_floors/calibration_plan.json`; its SHA sidecar and generator; `02_phase_absolute/p2015-df-ph-decode-abs-r01.json` through `r10.json`; `05_phase_decode_abba/`’s forty decode configs and manifest; root `order_manifest.json`; `configs/floor_mint/a10_extraction_spec.json`; `configs/floor_mint/window_c_extraction_spec.json` | Exact Qwen2.5-1.5B stack identity, 10 absolute members, ten fixed A/B/B/A null blocks, runtime/config conventions, extraction shape |
| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
| Decode contrast | Entire `configs/campaigns/splitwise_decode_v1/`, particularly the plan, generator, forty configs, root/stage manifests, condition families, and `analysis_manifest_v3.json` | A=1.5B, B=7B, ten ABBA blocks, B−A orientation, v3 estimator and cross-stack floor rule |
| Operational references | `configs/campaigns/neg8_reference_corpus/` and the existing start/mid/end reference manifests | Twelve-member same-window NEG8 binding plus 3/1/3 references |

The old `02_phase_absolute/order_manifest.json` contains thirty interleaved decode, prefill, and short-prefill configs. It must not be copied as the new absolute manifest. Only its ten decode configs are the alpha source; the new ten-entry manifest is regenerated and independently hashed.

Historical results are diagnostic inputs only. No old evidence-root ID, calibration bracket, member output, or operative floor literal enters a prospective claim basis.

### Immutable identifier proposal

| Placeholder | Frozen plan ID | Evidence-root ID | Physical root |
|---|---|---|---|
| W-alpha | `plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-1p5b-v1` | `runs_d117_floor_qwen25_1p5b_v1` |
| W-beta | `plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-7b-v1` | `runs_d117_floor_qwen25_7b_v1` |
| W-gamma | `plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1` | `evidence-d117-contrast-qwen25-1p5b-vs-7b-v1` | `runs_d117_contrast_qwen25_1p5b_vs_7b_v1` |

Each also gets a separately named bound root ending in `_bound`. Failed physical attempts receive custody attempt suffixes outside the scientific ID; the clean evidence root is never silently reused.

### Common order-manifest contract

Every root manifest should bind:

- plan ID, exact plan SHA, generator SHA, and model/runtime revisions;
- ordered stage records with exact stage-manifest ID, SHA, expected member count, predecessor, and successor;
- exact relative config paths and config SHAs—no globs or directory discovery;
- ordinal, member ID, ABBA block and slot where applicable;
- fixed reference and NEG8 manifests;
- the prefill rider mapping for floor members;
- frozen attempt policy, including zero calibration retries and no outcome-driven top-ups;
- evidence-root ID and expected fresh physical path;
- hashes of condition families, extraction spec, and analysis manifest;
- arm-time attachment slots for the readiness record, session capability, and actual receipt identifiers without modifying frozen plan bytes.

An ABBA stage manifest records each block as `A1,B1,B2,A2`. Splitting blocks 1–5 and 6–10 around the midpoint reference does not reset block numbering.

### Per-window plans

#### Alpha — 1.5B decode floor plus prefill rider

| Stage | Members | Order |
|---|---:|---|
| Pre calibration | 1 live observation | Finalize reserved `pre` slot before science |
| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
| Start references | 3 | Frozen triplet |
| Absolute floor | 10 | `abs-r01` through `abs-r10` |
| Null half 1 | 20 | ABBA blocks 1–5 |
| Midpoint reference | 1 | Frozen midpoint |
| Null half 2 | 20 | ABBA blocks 6–10 |
| End references | 3 | Frozen triplet |
| Post calibration | 1 live observation | Finalize reserved `post` slot |
| Closeout | 0 science members | Terminal head pin, bracket binding, verdict, dual-root backup |

Science count is 50; operational captures are 12 bound, 7 references, and 2 calibrations. The prefill rider adds no member and no runtime.

The rider is a new condition family over the same 128-prompt/512-output decode bundles. It must pre-register `phase_energy_j.prefill`, phase precheck `["phase","prefill"]`, exact tokenizer/model/config identity, the same ten absolute members and forty null members, its estimator, n=10 block basis, and both absolute and comparative floor rules. It is not the old dedicated prefill condition.

The extraction spec contains four cells: decode absolute, decode comparative, prefill absolute, and prefill comparative. It names 100 cell-member references but exactly 50 unique bundles. Each cell supplies an exact member list, config hash list, expected n, condition-family hash, metric key, phase precheck, order-manifest pin, calibration basis, and evidence-root ID. Missing prefill phases, fallback values, or member discovery outside the list are fatal.

#### Beta — 7B decode floor plus prefill rider

The schedule is identical to alpha: pre calibration; 12 NEG8; start 3; absolute 10; ABBA blocks 1–5; midpoint 1; blocks 6–10; end 3; post calibration.

The decode condition remains D-085’s `df-ph-decode-qwen25-7b`; the fresh plan does not rename settled scientific semantics. The new prefill-rider family pins `phase_energy_j.prefill` over the exact 7B decode members and stack revision.

Its extraction contract is the same four-cell/50-unique-bundle shape as alpha. Old 7B values—absolute 6.294380… J and comparative 13.998036… J—are budget/design diagnostics only and are not pre-registered pins.

#### Gamma — 1.5B-versus-7B decode contrast

| Stage | Members | Order |
|---|---:|---|
| Pre calibration | 1 live observation | Finalize `pre` slot |
| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
| Start references | 3 | Frozen triplet |
| Contrast half 1 | 20 | ABBA blocks 1–5 |
| Midpoint reference | 1 | Frozen midpoint |
| Contrast half 2 | 20 | ABBA blocks 6–10 |
| End references | 3 | Frozen triplet |
| Post calibration | 1 live observation | Finalize `post` slot |
| Closeout | 0 science members | Pin, binding, verdict, backup, then analysis |

The frozen manifest remains decode-only:

- A is the exact 1.5B stack; B is the exact 7B stack.
- Metric is exactly `phase_energy_j.decode`.
- Estimand orientation is B−A.
- Design is ten A/B/B/A blocks, n=10 block estimates.
- Estimator is `abba_block_arm_mean_difference_t_v1`.
- Test is two-sided at family alpha 0.05, with the positive direction stated as the scientific hypothesis rather than used to change the test.
- `equivalence_margin` and `mde` remain null unless prospectively ruled otherwise.
- Floor rule remains `cross_stack_armwise_max.v1`: independently resolve the 1.5B and 7B decode cells and take their maximum, never their sum.
- Claim-side anchor bounds remain separate from the detection-floor operation.
- The finalized analysis basis pins the exact forty member paths, config hashes, stack identities, floor artifact bytes, calibration binding, and evidence root.

### Runtime evidence and budgets

Historical evidence in `docs/phase_2/splitwise_decode_campaign.md` §4 supplies:

- 1.5B decode member: 92.7 s, measured n=40;
- 1.5B reference member: 90.5 s, measured n=7;
- 7B decode member: approximately 97 s from the measured/probed anchor;
- 1.5B/7B mixed ABBA half: about 31.6 min raw member time.

The stage allowances incorporate the configured 30-second idle, warmup/teardown, stage arm overhead, and cooldown conventions. The pre-calibration allowance includes the required 180-second post-admin settle. The separate ten-minute untouched quiet-idle gate is added before applying the 20% margin.

| Component, minutes | Alpha | Beta | Gamma |
|---|---:|---:|---:|
| Pre calibration bracket | 8 | 8 | 8 |
| 12 NEG8 bound members | 22 | 22 | 22 |
| Bound evaluation | 1 | 1 | 1 |
| Start 3 references | 8 | 8 | 8 |
| Absolute 10 | 19 | 20 | — |
| ABBA blocks 1–5 | 34 | 36 | 35 |
| Midpoint reference | 5 | 5 | 5 |
| ABBA blocks 6–10 | 34 | 36 | 35 |
| End 3 references | 8 | 8 | 8 |
| Post calibration bracket | 8 | 8 | 8 |
| Campaign subtotal | 147 | 152 | 130 |
| Untouched pre-arm idle | 10 | 10 | 10 |
| Base occupancy | 157 | 162 | 140 |
| With 20% failure margin | **188.4** | **194.4** | **168.0** |
| Hours | **3.14 h** | **3.24 h** | **2.80 h** |
| 2–4 h envelope | Pass | Pass | Pass |

The margin is time headroom, not authority to add members, replace a cap-hit observation, or top up an unfavorable result. The fixed manifest and frozen failure policy decide scientific validity.

### §5A operator bookends

Before each window:

1. Verify the reviewed plan/readiness record, fresh empty roots, model artifacts, charger/AC state, power policy, OS/tool identity, empty waiver set, and current acceptance artifact.
2. Verify the physical ledger head equals the authenticated committed pin.
3. Correct the clock against the trusted source, record the correction and `usingnetworktime` state, turn network time off, and settle for at least 180 seconds.
4. Establish zero-agent/zero-output-streaming conditions and complete ten untouched minutes of daemon idle.
5. Append the exact two-slot bracket session capability.
6. Capture and finalize the pre observation; run the acceptance and D-102 trigger probe.
7. Only after every gate is green, emit the one-line arm message and walk away.

At the closing bookend:

1. Capture the post observation before changing power, network-time, or workload state.
2. Finalize the post slot or write the governed failure/abort closure.
3. Commit and authenticate the terminal ledger head.
4. Emit the exact bracket binding and whole-window verdict from one immutable ledger snapshot.
5. Back up evidence and bound roots with verified return code and hashes.
6. Restore network time and record the restoration only after measurement completion and custody closeout.

### Prefill floor claim eligibility

A rider is claim-eligible only if desk freeze already binds:

- exact metric and phase path;
- exact workload parameters, model/tokenizer revision, seeds, quantization, runtime, sampling, and telemetry mode;
- absolute and comparative member lists and order manifests;
- exact condition-family ID and hash;
- n and estimator;
- calibration cell, acceptance artifact role, and D-110 allowance rule;
- extraction failure behavior;
- allowed consumer families.

For each metric, the operative floor is the maximum of independently evaluated absolute and comparative components. Apply D-110 once as `A_s = max(observed_drift, 0.010818)`. Never sum components and never borrow a decode floor for prefill.

### Two-stage mint freeze

**Desk-frozen pin requirements**

For each floor plan, freeze:

- plan ID, declared SHA, sidecar SHA, and actual artifact SHA;
- evidence-root ID;
- four intended cell roles across the two plans;
- condition-family IDs/hashes;
- metric and phase-precheck paths;
- absolute and comparative order-manifest IDs/hashes;
- extraction-spec SHA and exact members;
- expected counts;
- model/runtime/config hashes;
- calibration acceptance artifact ID/SHA/derivation rule;
- D-110 never-zero allowance rule;
- aggregate artifact ID and transport allowlists.

These live in a non-mintable `pin_requirements.v2` artifact. Unresolved values must be structurally absent or explicitly marked unresolved; the file cannot satisfy the final pinset schema.

**Postcollection-frozen pins**

After passed verdicts and governed extraction, freeze separately for each of the four cells:

- absolute and comparative evaluation-basis SHA/count;
- exact accepted pre/post receipt and content digests;
- bracket-binding SHA and terminal ledger head;
- observed drift and applied allowance;
- extraction-report SHA;
- absolute, comparative, and operative values;
- the operative literal formatted independently as exactly six decimals using the repository’s `.6f` convention.

The lead independently recomputes each six-decimal literal from primary extraction bytes. The mint only compares supplied literals and hashes; it does not calculate them. The old `7.377086` literal is never reused.

Gamma has no producer mint. Its consumer pinset instead binds the exact combined floor artifact bytes, the two decode-cell IDs, its plan/order/analysis manifests, and its finalized evaluation basis.

### Synthetic three-window live-ledger regression

The fixture begins with the exact issued-ledger semantics: 76 receipts, including 38 historical import observations—30 valid, 2 systematic, 6 ordinary-invalid. Candidate discovery must exclude every import-marked observation.

The no-failure live extension adds three bracket capabilities and six finalized live observations. From one immutable final snapshot, the regression must prove:

- exactly six live candidates and zero imported candidates;
- alpha, beta, and gamma each bind only their own pre/post pair;
- all six are same-epoch, causal, fresh, within protocol and T1 limits;
- no neighboring endpoint can substitute for a bound endpoint;
- all three verdicts use the same complete candidate universe;
- the ideal terminal sequence is 85 under the proposed three-receipt session model;
- the D-110 never-zero allowance remains active.

Required refusal vectors:

- import-marker removal, import leakage, or candidate-discovery regression;
- missing, duplicate, reordered, or conflicting session/finalization receipts;
- open or abandoned session without a governed closure;
- physical-head/pin mismatch, rollback, fork, or uncommitted terminal head;
- omitted, added, duplicated, off-ledger, or content-substituted observations;
- missing, tampered, swapped, or cross-window bracket binding;
- noncausal endpoint, stale endpoint, T1 failure, protocol failure, or epoch mismatch;
- systematic classification;
- one range-expanding live observation requiring a successor;
- the observation-count boundary reaching the D-102 limit;
- a successor whose prior set omits or changes an authenticated prefix.

### Optional 256-token prefill contrast

Clean attachment inside frozen gamma is impossible. Adding the arm changes the workload, metric family, members, order, runtime, multiplicity, plan digest, evidence root, and verdict basis.

If Ed adopts it, create a fourth independently frozen, independently calibrated plan and evidence root. It may attach later only in a higher-level synthesis/claim packet that references gamma and the new prefill result as sibling artifacts. Gamma’s bytes remain unchanged.

The floor riders here use the prefill phase of the 128-prompt decode workload. They do not automatically transport to a prospectively defined 256-token contrast. The fourth plan needs either exact matching prefill floor cells or a separately predeclared and justified transport rule. No placeholder members or plan ID should be added to gamma now.

### Freeze order and lead gates

1. **Ruling gate:** lead accepts the session-capability semantics, zero-retry policy, successor corpus rule, four-cell artifact shape, and fourth-window treatment.
2. **Toolchain gate:** ledger session/binding, successor builder, pinset v2, multi-cell mint, prefill metric support, and three-window regression all land and pass focused plus canonical suites.
3. **Desk freeze gate:** generate all three campaign packs; freeze identifiers, model revisions, configs, manifests, condition families, extraction/analysis specs, budgets, failure policy, and hashes. Six-decimal values do not yet exist.
4. **Per-window arm gate:** attach current clean head, acceptance artifact, physical/committed ledger equality, fresh roots, exact environment preflight, empty waivers, §5A evidence, and bracket-session identifiers.
5. **Pre-science trigger gate:** finalize the pre observation and either accept it, issue a governed successor, or abort before member one.
6. **Post-window gate:** finalize post, commit terminal head, issue bracket binding, verdict, and verified backup.
7. **Floor mint gate:** after alpha and beta pass, run governed four-cell extraction, independently freeze literals, mint the combined artifact, and require `validate_floor_artifact` to return no findings.
8. **Gamma claim gate:** pass the whole-window verdict, finalize the v3 basis, run D-093 root scanning, resolve both decode arm floors from exact combined-artifact bytes, and apply the armwise maximum.

### Work-order list with enforced WRITE_SCOPE units

| Unit | Exact write scope | Invariants and tests | Dependency |
|---|---|---|---|
| U1 — ledger session and binding | `joulewise/calibration_ledger.py`; `joulewise/calibration_bracketing.py`; `scripts/reserve_calibration_window_bracket.py`; `tests/test_calibration_ledger.py`; `tests/test_calibration_bracketing.py` | Two immutable slots, one-use finalization, governed abort, no unresolved-candidate leakage, exact binding, head/pin refusals. Focused ledger/bracketing tests plus full suite. | Foundation; independent of U3 |
| U2 — D-102 successor engine | `joulewise/calibration_bracketing.py`; `scripts/build_calibration_acceptance_successor.py`; `configs/calibration/calibration_acceptance_registry.json`; `tests/test_calibration_acceptance_successor.py` | Complete authenticated live prefix, deterministic bytes, parent ancestry, exact Decimal derivation, range/count triggers, systematic refusal. Focused cold-gate fixtures plus full suite. | Sequential after U1 because of shared bracketing semantics |
| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
| U4 — three-window ledger regression | `tests/fixtures/calibration_live_three_window/**`; `tests/test_calibration_live_three_window.py` | Exact issuance fixture, import exclusion, six live candidates, three causal bindings, successor and refusal vectors. | After U1 and U2 |
| U5 — alpha campaign pack | `configs/campaigns/d117_floor_qwen25_1p5b_v1/**`; `configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json`; `tests/test_d117_floor_qwen25_1p5b_plan.py` | Exact 10+40 schedule, split midpoint, two metric riders, 50 unique bundles, fresh IDs, deterministic regeneration. | After U3 schema/IDs freeze; parallel with U6 |
| U6 — beta campaign pack | `configs/campaigns/d117_floor_qwen25_7b_v1/**`; `configs/floor_mint/d117_qwen25_7b_extraction_spec.json`; `tests/test_d117_floor_qwen25_7b_plan.py` | Same as U5, retaining D-085 stack/family identity. | After U3; parallel with U5 |
| U7 — gamma campaign pack | `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/**`; `tests/test_d117_decode_contrast_plan.py` | Forty ABBA members, decode-only metric, B−A orientation, v3 estimator, exact four-cell artifact consumer pins, no prefill placeholder. | After U3 floor cell/transport IDs freeze |
| U8 — operator/readiness packet | `docs/phase_2/window_runbook.md`; `scripts/validate_frozen_plan_readiness.py`; `tests/test_frozen_plan_readiness.py` | §5A sequence, session capability, pre-trigger successor gate, fresh roots, empty waivers, terminal binding/pin/backup. | After U1, U2, U5–U7 |
| U9 — state and custody bookkeeping | `docs/process/state_kernel.json`; `RUN_STATE.md`; `TASK_QUEUE.md`; `CLAIMS_STATUS.md`; `docs/run_reports/2026-08-07-d117-plan-freeze.md` | D-117 vocabulary, no C/D plan references, exact frozen digests, generated-view consistency. | Lead-owned, after all desk artifacts pass |
| U10 — postcollection pin closure | `scripts/floor_mint_pinsets/d117_qwen25_1p5b_v2.json`; `scripts/floor_mint_pinsets/d117_qwen25_7b_v2.json`; `scripts/floor_mint_pinsets/d117_qwen25_phase_floor_set_v2.json`; `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.json`; `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.sha256` | Only postcollection facts; independent literal recomputation; exact receipt/binding/head pins; validator returns no findings. | Sequential after alpha and beta pass |

Every unit should run its focused tests and `python3 -m unittest discover -s tests`. Shared files make U1→U2 sequential; U1 and U3 can proceed independently. U5 and U6 can proceed independently after U3 freezes the vocabulary. U7 waits for final floor-cell and transport identifiers. U10 is deliberately absent from the desk freeze.

### What the lead should double-check

- Recover the missing prefill-feasibility trace and compare its exact 256-token assumptions with this fourth-window conclusion.
- Ratify the two-slot ledger capability against D-109/D-116, especially whether an open post slot may exist during the pre-science successor probe.
- Decide explicitly between zero calibration retries and a prospectively numbered retry-capability variant.
- Ratify the D-102 successor corpus rule: all content-distinct valid same-epoch observations through the cutoff.
- Confirm that D-085’s 7B decode family ID is preserved and contrast transport uses allowlists rather than relabeling configs.
- Confirm pinset v2 supports multiple producer plans while preserving byte-for-byte v1 behavior.
- Verify the 20% allowance does not become permission for member replacement or result-driven top-up.
- Recheck full model revisions, local artifact hashes, runtime version, charger identity, and post-move environment at each arm.
- Independently calculate all four `.6f` operative literals from primary extraction bytes.
- Verify every one of the fifty floor bundles actually contains the registered prefill phase; a missing phase must fail extraction.
- Ensure gamma takes the maximum of the two decode arm floors, never their sum, and retains separate claim-side anchor bounds.
- Ensure the 128-prompt prefill riders are not presented as a floor for a later 256-token contrast without exact transport evidence.
- Regenerate the active queue from the state kernel so superseded C/D and D-110 gates cannot be mistaken for arm authority.
- Freeze against the final reviewed repository head; this consult began at `dbb9685` and ended cleanly at concurrently advanced `94a24e5`.

## Residual risk

No live timings, calibration observations, successor generation, or mint replay were performed. Runtime estimates therefore inherit historical-machine variance; the 20% margin is the current mitigation.

The absent feasibility synthesis limits review of the optional 256-token arm. Its attachment architecture is sound, but its member count, runtime, estimand, and floor transport remain intentionally unfrozen.
exec
/bin/zsh -lc 'cat docs/strategy/2026-08-06-impressiveness-roadmap.md; cat docs/research_question_registry.md; cat docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The strongest feasibility-weighted path is a clean C/D metrology campaign, external wall validation, and an evaluation-ready artifact before adding one hypothesis-driven expansion.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "head_end": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "upstream_end": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The paper's claim-bearing experimental spine is not yet complete",
        "detail": "D-110 still withholds the floor and contrast artifacts pending issuance/remint, while D-113 requires fresh Window C collection, prospectively split into D if needed."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "D-041 is not the mechanism-level fence",
        "detail": "D-041 governs external-benchmark import/export and limits the export shim to an energy layer; AXI mechanism studies are governed primarily by D-070, D-075, their analysis plans, and runtime feasibility verdicts."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Venue and calendar ambition remain unbound",
        "detail": "The report deadline, colloquium, 3080 Ti window, and venue-specific evidence-by dates remain TBD, preventing rational allocation of measurement nights."
      },
      {
        "id": "F4",
        "severity": "nit",
        "title": "The requested methods draft is not on main",
        "detail": "docs/paper/draft-v1.md exists on impl/paper-draft-v1 but is absent from main; the branch version was inspected for this review."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse --abbrev-ref HEAD && git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "665fd5821f74e579071fba9ddd9717b77ded6a01",
          "main",
          "origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "665fd5821f74e579071fba9ddd9717b77ded6a01\\nmain\\norigin/main"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "test ! -e docs/paper/draft-v1.md && git cat-file -e impl/paper-draft-v1:docs/paper/draft-v1.md && printf 'draft_main=absent\\ndraft_branch=present\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "draft_main=absent",
          "draft_branch=present"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "draft_main=absent\\ndraft_branch=present"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The prompt identifies docs/paper/draft-v1.md as current, but it is present only on the impl/paper-draft-v1 branch.",
      "needs": "Lead should integrate or otherwise disposition the paper-draft branch."
    },
    {
      "id": "FL2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No test suite was run because this was a read-only strategic synthesis with no repository modifications.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — Finish the claim-bearing metrology spine before expanding

The instrument and its evidence machinery are unusually mature, but the paper still lacks a complete claim-bearing characterization result. The 1.5B/7B contrast passed collection gates and is a compelling preliminary demonstration, yet D-110 prevents formal use until the issuance/remint chain completes. D-113 then requires fresh Window C collection—split into D if necessary—without importing any retired Window B member. See [D-113](/Users/edr/code/JouleWise/docs/decision_log.md:7240) and the [current paper outline](/Users/edr/code/JouleWise/docs/run_reports/2026-07-30-paper-outline-v1.md:1).

That is the critical path. A broad paper with incomplete C1–C6 evidence will look less serious than a narrower paper that cleanly demonstrates linearity, null response, empirical floor behavior, additivity, drift/settling, and between-session stability.

D-113’s rigor-first posture forbids:

- Salvaging failed A/B data into replacement claim cells.
- Excluding an inconvenient member after seeing results.
- Compressing an oversized campaign into one night.
- Weakening calibration, whole-window, clock, or custody gates for schedule reasons.
- Adding process or repetitions without a named validity threat or material claim benefit.

It explicitly permits—and often prefers—smaller independent windows, narrower claims, and cutting an expansion.

### F2 — Exact D-041 ruling and the real mechanism fence

D-041 is titled “Benchmark interop — frozen-subset imports + marker-shim energy layer.” It fences:

- External benchmark imports to hash-frozen subsets with identity, licensing, and contamination records.
- Export to a marker-emitting shim where the external harness owns prompts, generation semantics, and accuracy; JouleWise owns capture, bundle assembly, marker validation, and energy reduction.
- Joined reporting to observed energy beside the external metric artifact—never JouleWise accuracy, pass@k-per-joule, leaderboard standing, or intelligence-per-joule.
- Implementation to after 2M and P2-010a, unless D-034 is explicitly reopened.
- Interop expansion to be cut before core Mac characterization under schedule pressure.

Thus, “unfencing D-041” would require completing 2M and P2-010a—or an explicit decision reopening D-034/D-041 sequencing—then passing P2-022’s marker feasibility spike and writing an analysis-plan row before any L2 claim. It still would not authorize mechanism attribution.

The KDA/speculative-decode/MTP/MoE program is instead governed by D-070/D-075 and the AXI contracts:

- Post-core/floor sequencing.
- L2 ceiling for named studies unless Q4’s independent L3 machinery applies.
- Direct observability rather than inference from configuration.
- Output/quality-equivalence controls.
- Named forbidden generalizations.

The current feasibility facts matter:

- External-draft speculative generation exists, but pinned `mlx-lm` lacks actual proposal counts and decode-step emission boundaries.
- Native MTP is unsupported: the pinned runtime does not execute the heads.
- KDA/hybrid comparisons currently involve cross-model confounding and unverified long-context execution.
- MoE mechanism language requires auditable routing evidence; otherwise the claim must remain a named-model energy comparison, not routing attribution.
- No tracked repository document uses “KDA” as a governed project axis; it appears in the nonbinding mechanism-literature sweep, not D-041.

### Ranked roadmap

Planning estimates below assume the current 2–4-hour claim-window protocol, at least 20% failure margin, and physical Ed preparation through §5A.

| Rank | Expansion | Why it impresses reviewers | Estimated effort and Ed-present sessions | Dependencies and principal risk | Decision required |
|---:|---|---|---|---|---|
| **1** | **Complete C1–C7 cleanly: remint, fresh C/D, and stability** | Converts the strongest idea—the instrument and its refusal behavior—into actual evidence. This is the difference between an elaborate methodology and a metrology paper. | **3–6 weeks after desk gates; 2 mandatory nights plus 1 contingency/short stability session.** | D-079 issued artifact; D-110 remint; reviewed frozen-plan record; fresh §5A; C/D split if scope cannot fit. Risk: another environmental or clock refusal. | Reserve the core nights now and prohibit breadth work from consuming them. |
| **2** | **External wall-meter validation of totals, C8** | Directly addresses the obvious reviewer question: “Does `powermetrics` agree with physical input power?” It materially upgrades absolute-scale credibility. | **4–8 weeks; 1 pilot plus 1 confirmatory session.** The confirmatory run may share a later frozen campaign only after the importer and protocol pass independently. | Professional AC analyzer, safe inline fixture, synchronized export, fixed ranges, load-specific uncertainty, battery charge neutralization, held-out regression. It validates totals only—not phase allocation. | D-092 already decided “yes”; Ed/advisor must now authorize purchase/loan, budget, and an evidence-by date. |
| **3** | **Artifact-evaluation-quality release** | Hash-bound raw-to-figure reproducibility is a genuine differentiator and unusually well aligned with JouleWise’s thesis. Reviewers can verify refusals and re-derive results rather than trust screenshots. | **4–6 weeks; 0 measurement nights.** | Sanitized raw-bundle subset, one-command validation/reduction/figure path, locked environment, quick/full tracks, immutable archive/DOI, clear hardware-free replay. Risk: privacy, dataset size, and Mac-only collection requirements. | Decide whether the target is merely open source or formal ICPE-style artifact evaluation, and which evidence may be public. |
| **4** | **Designed workload-shape matrix with held-out prediction—Q4/L3** | A predictive fixed-plus-marginal model validated on held-out cells is substantially more serious than “we ran more prompts.” It can earn L3 rather than another collection of L1/L2 points. | **6–10 weeks; approximately 2–3 nights.** | P2-006 baseline sizing, AP-1, 4×3 grid, predeclared holdouts, residual/sensitivity analysis, floor audit. Risk: the simple model may fail its holdouts—which must be reported honestly. | Fund the full designed matrix or omit the predictive claim; do not replace it with opportunistic workload breadth. |
| **5** | **Quality-gated BF16/Q8/Q4 quantization ladder** | A clean same-family ladder with error bars and output-divergence reporting can adjudicate the reported q4-vs-q8 anomaly. Strong workshop demonstration; moderate novelty. | **4–8 weeks; 1–2 nights.** Quality screening can run outside quiet windows. | One frozen source revision, reproducible conversions, 256-item quality gate, 32-item energy subset, stack-specific floors. Risk: quality may not be equivalent or quantization may alter cadence beyond existing calibration support. | Choose the model family before conversion; accept a quality/energy trade-off result if equivalence fails. |
| **6** | **Second-unit replication after multi-day same-unit stability** | This is the clearest path beyond single-machine claims and toward L4. It demonstrates that the artifact and calibration method transfer, not merely that one laptop is stable. | **4–8 weeks once access exists; 2 sessions on the second unit, 0–2 Ed-present depending on operator.** | A second comparable Apple unit, frozen stack or explicitly modeled version difference, independent calibration and artifact execution. Risk: OS/hardware drift may make it replication-aware rather than directly pooled. | Secure a second unit/collaborator or explicitly retain the single-unit ceiling. |
| **7** | **One mechanism-level study, conditional on a hard feasibility gate** | **Highest scientific ceiling.** A controlled batch-1 speculative-decode or MTP energy result could be genuinely novel; KDA/context slope or MoE routing is also interesting if attribution is identifiable. | **2–3-week desk feasibility gate; if passed, another 6–12 weeks and roughly 2 nights.** | New/forked runtime instrumentation, direct proposal/acceptance events, output identity/equivalence, mechanism-specific AP and floors. MTP currently cannot execute; KDA is confounded; MoE routing visibility is uncertain. | Pick exactly one mechanism and a kill date. Recommended first choice: external-draft speculative decode, because it offers the cleanest same-target on/off contrast if observability can be added. |
| **8** | **Split inference: synthetic transfer plus one offline split pairing** | Demonstrates the instrument under two boundaries, a transfer interval, and cross-device clocks. A complete per-stage bundle is impressive even without a crossover. | **2–4 months; roughly 3–5 two-device measurement sessions.** Live split adds more and should remain stretch. | Schema v0.2, remaining replay verdicts, two-node telemetry, clock bounds, transfer bench, 3080 Ti window, two links, wall/host boundary or lower-bound wording. Risk is high and the engineering can dominate the paper. | Commit only to synthetic transfer plus offline replay; authorize live split separately after offline results. |
| **9** | **Additional model families, generic workloads, Jetsons** | Useful corroboration, but mostly incremental unless each addition tests a predeclared hypothesis or provides independent replication. More rows do not overcome the single-unit or boundary limitations. | **3–8 weeks and 1–2 nights per coherent axis/device.** | New model lineage, adapter, quality and floor cells; Jetson remains optional and remote pins are provisional. | Add only a model or device that changes the claim—not merely the size of a results table. |

For the wall-meter path, the right class is a calibrated bench AC power analyzer, not an inexpensive consumer plug. A concrete baseline is the Yokogawa WT310E: its manufacturer lists 10 readings/s, USB export, 0.1%-of-reading plus 0.05%-of-range basic accuracy, high crest-factor capability, and a **$2,935 base US price** before calibration/fixture costs. Actual suitability still depends on calculating uncertainty at the Mac’s observed load and using a safe inline fixture. Borrowing an in-calibration unit from an engineering lab is preferable to spending several thousand dollars. [Yokogawa WT310E specifications and current price](https://tmi.yokogawa.com/us/solutions/products/power-analyzers/digital-power-meter-wt300e/).

### Venue ambition

| Tier | What the current/expanded project can support | What should be present |
|---|---|---|
| **CSCSU** | After remint and clean C/D, this should be a strong undergraduate-conference submission. The latest published rules allow technical papers and extensive experimentation, with **5 pages including references**. [CSCSU 2026 guidance](https://cscsu-conference.github.io/) | C1–C6 core, one demonstration, crisp limitations, compact artifact pointer. Wall validation and split are not necessary. |
| **EuroMLSys/HotCarbon workshop** | The natural near-term research target. EuroMLSys’s latest call uses 6 pages excluding references; HotCarbon uses 5 pages excluding references and no appendix. [EuroMLSys](https://euromlsys.eu/), [HotCarbon CFP](https://hotcarbon.org/cfp) | Clean metrology core, model contrast, wall validation if available, and polished artifact. EuroMLSys is the better technical-method fit; HotCarbon needs a stronger sustainability-metrics argument. |
| **ICPE Emerging/WIP** | Appropriate if the core is strong but external validation, replication, or the broader predictive evaluation remains incomplete. The 2026 track used a 6-page format. [ICPE Emerging Research](https://icpe2026.spec.org/tracks-and-submissions/emerging-research-track/) | Validated core, transparent open gaps, early artifact, and a credible expansion plan. |
| **ICPE full research track** | Plausible over months, but not yet supported by the current evidence. ICPE 2027 lists research and artifact tracks but their details and dates remain TBA. The 2026 research track used 10 pages and judged novelty, technical quality, and scientific soundness; 2026’s reported full-paper acceptance rate was 28%. [ICPE 2027](https://icpe2027.spec.org/tracks-and-submissions/research-paper-track/), [2026 research criteria](https://icpe2026.spec.org/tracks-and-submissions/research-paper-track/), [acceptance history](https://icpe.spec.org/past-conferences/) | C1–C8, cross-day stability, artifact-ready release, and at least one deeper contribution: held-out Q4 prediction, second-unit replication, or a successful mechanism study. Split is not required. |

ICPE’s artifact track is especially aligned: it asks for documented, consistent, complete, exercisable artifacts, permanent archival availability, and practical setup/reproduction instructions. [ICPE artifact-evaluation criteria](https://icpe2026.spec.org/tracks-and-submissions/artifact-evaluation-track/).

### Critical path to the strongest defensible version

1. **Now:** finish D-079 issuance and the D-110 remint chain; integrate or disposition the draft branch; set actual calendar and venue evidence-by dates.
2. **In parallel:** borrow/order the wall analyzer and build its importer, synchronization, and held-out validation protocol without assuming it will arrive in time.
3. **First hardware block:** freeze and collect Window C, then D if the complete replacement cannot fit with the required margin. Add a third short day/session only if needed for the stated stability claim.
4. **Immediately after each passing window:** produce the governed artifacts, deterministic figures, claim-index entries, and experimental prose. Do not wait for all expansions before writing.
5. **Artifact block:** publish a sanitized, hash-bound raw-to-figure package with a fast hardware-free reproduction path and archival DOI.
6. **Second hardware block:** run external wall validation.
7. **Choose one expansion:** Q4 held-out prediction for the strongest ICPE case; quantization for the safest workshop enhancement; or mechanism work only if its short feasibility gate passes.
8. **Only then consider split inference.** Start it only if the 3080 Ti window is dated and the transfer/offline-replay path is rehearsed before hardware access.
9. **Freeze the dataset early:** reserve at least six weeks before submission for figures, claims audit, paper compression, artifact dry runs, and advisor review.

The strongest realistic paper is therefore: **C1–C8 metrology + the already-collected 1.5B/7B demonstration + one designed extension + an independently usable artifact.** That is more coherent and defensible than a larger model/device matrix or an unfinished split system.

### F3 — Five decisions Ed/advisor must make

1. **Venue and publication sequence.** Choose CSCSU-only, workshop-first, or ICPE-full ambition, and verify whether a workshop publication may later be extended for ICPE. Build a 10-page master manuscript even if the first submission is shorter.

2. **Physical measurement budget.** Recommended commitment: **5–7 Ed-present sessions**—C, D, one contingency/stability repeat, wall pilot/confirmation, and one extension. An ICPE-full attempt with Q4 and second-unit work likely needs **8–10 total sessions** across operators.

3. **Meter execution.** D-092 has already answered “yes.” The remaining decision is: borrow versus buy, approximately $3,000-class budget, calibration/fixture responsibility, and a cutoff date after which C8 is cleanly removed.

4. **Mechanism ambition.** Do not ask simply “unfence D-041.” Decide whether to retain D-070’s all-five-axis commitment or narrow it to one paper-worthy study. Recommended rule: two-to-three-week feasibility gate for speculative-decode observability; if it fails, return immediately to Q4/quantization.

5. **External hardware priority.** Decide whether scarce coordination goes to a second Apple unit, the 3080 Ti split study, or Jetsons. Recommendation: second-unit replication first, 3080 Ti second, Jetsons last.

### F4 — Draft-state correction

The methods draft was inspected from `impl/paper-draft-v1` at commit `af0b7195`; it is one commit ahead of and one commit behind `main`. It already reflects the right rigor: result placeholders remain pending remint, all characterization rows are pending Window C, and the split section is framed as future demonstration work. It should be integrated deliberately so the paper itself becomes the continuously updated claim-state surface.

## Residual risk

- The mechanism-literature sweep is explicitly desk research, not governed project evidence. Any “first measured” novelty claim needs a fresh literature search immediately before submission.
- Venue formats and deadlines cited above are current published 2026 rules or incomplete 2027 pages; 2027 calls may change.
- Measurement-night estimates are planning ranges, not validated campaign runtimes.
- Wall validation cannot establish phase attribution, and one external meter does not create cross-device generality.
- Even an excellent single-Mac study remains stack-specific under the claims ladder unless second-unit or cross-lab replication lands.# Research Question Registry

Purpose: this is the canonical live index for JouleWise research questions,
capability claims, application ideas, and methodology artifacts. It normalizes
aliases, status, claim ceilings, owners, gates, and pre-hardware readiness so
claims and campaign plans can point to one row. Promotion rules are unchanged
from `docs/research_question_bank.md`: promotion still requires a named RQ slot
in `PROJECT_STATUS.md`, a data plan that does not displace queue ranks above
it, and scope fit.

Maintenance rule: registry rows are LIVE state. The research question bank
remains the historical and deliberative record, including council wording,
kills, quarantines, and amendments. Single-writer split: update this registry
for current indexing and cross-references; update the bank only when recording
new deliberation history.

Column legend:

- `canonical_id`: stable row key for the live index.
- `aliases`: other IDs, names, or capability-map labels for the same question.
- `question_type`: one of `research question`, `capability claim`,
  `application idea`, or `methodology artifact`.
- `status`: `promoted`, `banked`, `candidate`, `killed`, `answered-L1`, or
  the review-specific `candidate (C-023)`.
- `claim_ceiling`: highest claim level currently allowed by the bank, review,
  or capability map, before future evidence upgrades.
- `forbidden_upgrade`: short reminder of language the row cannot support.
- `AP owner`: analysis-plan owner if already named; otherwise `none-yet`.
- `campaign owner`: queue row, phase, or campaign owner if already named.
- `gate_class`: dominant gate class: `hardware`, `software`, `floor`,
  `substrate`, or `coordination`.
- `pre_hardware_preparable`: `fully`, `analysis-plan-only`, or `no`.
- `one-line note`: indexing note, not a re-adjudication.

## Registry Table

| canonical_id | aliases | question_type | status | claim_ceiling | forbidden_upgrade | AP owner | campaign owner | gate_class | pre_hardware_preparable | one-line note |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | Split reduces energy | research question | promoted | L2 boundary-labeled; stronger only with calibration | no uncalibrated cross-boundary total-energy winner | none-yet | Phase 3 split; P1-004; P1-006 | hardware | fully | Central split question; total energy must be decomposed and boundary-labeled. |
| Q2 | Link bandwidth sensitivity | research question | promoted | L2 | no nominal-link crossover without measured links | none-yet | Phase 3 split; P1-004 | hardware | fully | Clean interconnect sensitivity question; link throughput and transfer energy must be measured. |
| Q3 | Split energy-latency Pareto | research question | promoted | L2 | no Pareto claim without frozen set and latency metric | none-yet | Phase 3 split | hardware | fully | Requires a fixed comparison set and latency metric per figure. |
| Q4 | Fixed-vs-marginal energy model; C5-2.14 cache-policy coefficient rider | research question | promoted | L3 | no holdout-prediction claim without AP-1 floor and residual checks | AP-1 | P2-019 q4_l3_shape_grid_v1 | floor | analysis-plan-only | Strongest predictive science row; includes compositional split-energy prediction only when transfer terms exist. C5-2.14 is a candidate rider capped at L2, earliest PF, with no coefficient-direction claim below P2-015 floors ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| Q5 | Ranking stability | research question | promoted | L2 | no uncalibrated cross-device winner; no ranking where gap below MDE | AP-3 | 2M; Window B grid | floor | analysis-plan-only | Promoted within-machine ranking question; workload-axis analogue C5-W.3 remains a separate candidate row. |
| Q6 | Boundary sensitivity; C5-2.10 boundary-directional bias quantification | research question | promoted | L2; L4 only with replication | no wall/rail conclusion flip claim without paired boundary plan | none-yet | P1-003 wall meter; F11 | hardware | fully | Registry indexes C5-2.10 as the C5 elaboration of promoted Q6. |
| RQ-METHOD-FLOOR | Detection floor; noise floor; short-difference resolvability; phase/item identifiability flags; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | banked | L1 methodology | no below-floor effect language except `not resolvable`; no module-energy fraction or regression-slope attribution | none-yet | P2-015 | floor | analysis-plan-only | Methodology centerpiece and prerequisite for most comparative claims; the candidate module-attribution nonclaim attaches here at earliest NS instead of becoming a row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.11 | Dark silicon; rail utilization; ANE-dark finding | research question | candidate | L2 structural | no true silicon-energy fraction from modeled rails | none-yet | P2-009 rich telemetry; C5-1.8 runtime grid | software | analysis-plan-only | Measures modeled-rail utilization structure, not physical absolute rail truth. |
| C5-1.3 | CPU:GPU phase division; rail/DVFS phase signatures; prefill/decode power asymmetry | research question | candidate | L2 structural | no short-phase joules when windows are under-resolved | none-yet | 2M with P2-009 | floor | analysis-plan-only | Merges the banked CPU:GPU phase question with C5-1.3 telemetry framing. |
| RQ-KV-GROWTH | KV-growth decode drift; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | banked | L1/L2 chunked | no per-token joule claims; no attention-vs-FFN fraction from context slopes | none-yet | none | floor | analysis-plan-only | Candidate riders, earliest PF: bounded-window KV marginal slope and named-artifact attention/context slope; both retain chunked-window/floor discipline and stay attached rather than becoming independent rows ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.5 | Cooldown recovery as thermal characterization; cooldown-recovery curves | research question | candidate | L1/L2 | no claim that power recovery proves thermal-state equality | none-yet | none | floor | analysis-plan-only | Turns cooldown tails and cap-hit rates into reportable methodology evidence. |
| C5-1.10 | Failure frontier | research question | candidate | L1/L2 descriptive | no silent discard of failures; no population claim from one memory class | none-yet | none | software | analysis-plan-only | Structured `unsupported`, fit, swap, throttle, and cap-hit outcomes become data. |
| C5-1.7 | Cold-start / keep-warm energy; reload-vs-resident scheduling | research question | banked | L2 after harness extension | no breakeven without load-window and resident-idle sampling | none-yet | none | software | analysis-plan-only | Review and bank both identify reload-vs-resident as the same question. |
| C5-1.9 | Energy-per-correct-answer vs difficulty; MoE-vs-dense controlled ladder | research question | banked | L2 after envelope and denominator guards | no intelligence-per-joule; no `difficulty causes energy` | AP-5 | P2-010a plus P2-010b plus later scored campaign | substrate | analysis-plan-only | Correctness remains quarantined annotation under the C-004/C-014 rules. |
| C5-2.5 | Speculative-decoding energy; C5-2.5b proposal-work rider; C5-2.5c break-even rider | research question | banked | L2 | no efficiency claim without output equivalence and accepted-token accounting | none-yet | none | software | analysis-plan-only | C5-2.5c is the primary PF Q4 rider, C5-2.5b its PF secondary, and C5-2.5d the mandatory PF contamination control; C5-2.5a remains a deferred NS bank rider. `C-023-OUTPUT-IDENTITY` binds all efficiency contrasts ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-POWER-MODE | Power-mode Pareto | research question | banked | L2 possible | no OS-mode conclusion until power mode is a first-class config field | none-yet | none | software | analysis-plan-only | Waits on config/environment capture for OS power modes. |
| RQ-INTELLIGENCE-PER-JOULE | General joules-per-solved-task; intelligence-per-joule | research question | killed | none | no general intelligence-per-joule ratio | none-yet | none | substrate | no | Killed/quarantined by C-003/C-004; controlled ladder is the surviving minimal form. |
| RQ-AUDITABLE-EVIDENCE | Can JouleWise produce auditable local-LLM energy evidence? | capability claim | answered-L1 | L0/L1 | no physical calibration claim from strict validation alone | none-yet | existing Mac/MLX/powermetrics bundles | software | no | Artifact contribution, not a research question. |
| RQ-QWEN25-SMOKE | Qwen2.5-1.5B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from smoke result | none-yet | 2026-07-06 2I | software | no | Legit instrument observation for one named stack/workload. |
| RQ-QWEN35-SMOKE | Qwen3.5-122B-A10B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from n=3 | none-yet | 2026-07-07 flagship addendum | software | no | Legit instrument observation for one named stack/workload. |
| RQ-TWO-MODEL-ACTIVE-NONCLAIM | Did the two observed models demonstrate active-parameter scaling? | capability claim | answered-L1 | L1 hypothesis only | no active-parameter scaling claim | none-yet | 122B addendum; capability map | floor | no | Negative guard: two points are consistent with a hypothesis but do not support scaling. |
| RQ-SHORT-PREFILL-RESOLVABILITY | Are short prefill phase joules resolvable?; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | answered-L1 | L1 `not resolvable` | no standalone short-prefill joule result; no relabeling request phases as module phases | none-yet | Phase 4 observation | floor | no | Existing cadence precedent owns the candidate module-attribution guard, earliest NS; no separate methodology row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MLX-KV-REPLAY | Same-machine MLX KV replay token identity and size prediction; C5-2.13 | capability claim | answered-L1 | L1 feasibility | no cross-machine portability claim | none-yet | Stage 3.0.1 | software | no | The L1 feasibility result remains answered; candidate C5-2.13, earliest PF and capped at L2, attaches the same-machine energy-crossover rider without cross-stack generalization ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MAC-BASELINES | Per-profile Mac baselines | capability claim | candidate | L1 per condition | no novelty or comparison claim without AP/floor | none-yet | 2M | floor | analysis-plan-only | Necessary baseline corpus, not a headline by itself. |
| RQ-SHAPE-ENERGY | Workload shape changes request energy | research question | candidate | L2 | no causal token-shape claim beyond AP-2 contrasts | AP-2 | 2M | floor | analysis-plan-only | Distinct from Q4 because it describes shape contrasts rather than holdout prediction. |
| C5-1.1 | Active-parameter energy scaling | research question | candidate | L2 pairwise only unless larger predeclared model set | no active+total+KV regression on 4-6 models | none-yet | P2-024 shortlist | floor | analysis-plan-only | C-014 caps the tempting wording; registry hygiene, not re-adjudication. |
| C5-1.2 | Context-length energy scaling; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | candidate | L2/L3 if modeled | no short-prompt phase point claims; no wall implication from SoC rails | none-yet | none | floor | analysis-plan-only | Natural local-inference question with chunked phase limits; the two candidate PF riders remain capped at L2 and forbid module attribution from context-associated slopes ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.4 | DVFS residency as throttling early-warning | research question | candidate | L2 if prediction rule fixed | no prediction claim without horizon and rule | none-yet | none | software | analysis-plan-only | Convert characterization to a predeclared warning rule before claiming prediction. |
| C5-1.6 | Sampling-strategy energy overhead | research question | candidate | L2 if above floor | no telemetry-perturbation claim from this row | none-yet | P2-024 shortlist | floor | analysis-plan-only | Bank row is greedy vs temperature/top-p/beam overhead, not sampler instrumentation cost. |
| C5-1.8 | Runtime energy attribution; same-silicon kernel-layer provenance rider | research question | candidate | L2 stack-vs-stack | no `belongs to runtime` or `belongs to kernel layer` language when artifacts/formats differ; no runtime-agnostic kernel claim | none-yet | P2-024 shortlist | floor | analysis-plan-only | Candidate NV provenance rider stays inside the stack-conditioned comparison; it does not mint C5-1.13 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.12 | Quantization benefit decomposition, Mac leg | research question | candidate | L2 | no quantization efficiency claim without output divergence reporting | none-yet | P2-024 shortlist | floor | analysis-plan-only | Splits benefit into lower watts vs shorter time on one stack/family. |
| C5-W.1 | Category beyond token counts; Token-Shape Sufficiency Null | research question | candidate | L2 | no category effect below floor or without shape control | AP-4 | jw_mixed_v1 after P2-010a | substrate | analysis-plan-only | Strong null-or-effect design for workload-category residuals. |
| C5-W.2 | Thinking-token inflation | research question | candidate | L2 | no cognition claim; attribute only to emitted-token/stop distributions | none-yet | jw_mixed_v1 natural-EOS pilot | substrate | analysis-plan-only | Operational-cost view for reasoning models under natural EOS. |
| C5-W.3 | Category energy-ranking stability; workload-axis Q5 analogue | research question | candidate | L2 | no category ranking claim where rank gap is below MDE or without workload-expansion gate | none-yet | jw_mixed_v1 workload expansion | substrate | analysis-plan-only | Workload-axis analogue of promoted Q5, not the same ratified question; asks whether code/long-context/reasoning categories flip model/quant ordering. |
| C5-I.3 | C5-W.4; FLORES tokenizer fertility tax | research question | candidate | L2 | no tokenizer efficiency ranking without semantic and token-matched legs | none-yet | FLORES after HumanEval smoke | substrate | fully | C5-I.3 and C5-W.4 are the same FLORES fertility question. |
| C5-I.1 | External benchmark energy signatures | research question | candidate | L2 | no benchmark capability or accuracy claim | none-yet | import/export contracts | substrate | fully | Needs matched shape/output policy before family-level energy signatures. |
| C5-I.2 | Published-difficulty strata vs energy | research question | candidate | L1 association; L2 only if preplanned repeated bundles | no `difficulty causes energy` | none-yet | import/export contracts | substrate | fully | Weak/secondary because source difficulty labels are heterogeneous. |
| C5-I.4 | Harness overhead floor | methodology artifact | candidate | L1/L2 | no item energy claim when harness overhead dominates unnoticed | none-yet | P2-022 shim | substrate | fully | Methodology question for marked external harnesses. |
| C5-I.5 | Prompt-template energy sensitivity | research question | candidate | L2 | no prompt-quality or capability claim | none-yet | import/export contracts | substrate | fully | Same external item, canonical vs JouleWise-rendered prompt format. |
| RQ-CONTENT-SENTINEL | Synthetic prompt content sentinel; fixed-shape content sensitivity | research question | candidate | L2 | no content-effect claim unless realized shape/stop policy stays matched and effect clears floor; no broad content-neutrality claim beyond the five tested AP-6 conditions | AP-6 | P2-020 content sentinel | substrate | analysis-plan-only | Tests whether synthetic prompt content matters at fixed shape under the AP-6 ids-native no-BOS sentinel design. |
| RQ-ENERGY-VARIANCE | Sampling-induced energy variance; energy-at-risk per prompt; lucky-short-reasoning variance | research question | candidate | L2 within boundary | no intelligence-per-joule or correctness-causal claim (C-004 quarantine); variance claims need repeated-bundle n sized for variance estimation and floor-gated residuals; per-bundle sampler seeds must be recorded | none-yet | none (post-floor; reasoning model on current Mac feasible) | floor | analysis-plan-only | Ed-added 2026-07-09 row: distribution (not just mean) of request energy for a fixed hard prompt under sampling; decomposable into reasoning-length vs residual variance via recorded output token IDs + deterministic replay of sampled paths (P2-025 capture + 3.0.1 replay make paths replayable). |
| RQ-SESSION-SHAPE | Session-shape energy | research question | candidate | L2/L3 depending holdout | no app-session prediction without holdout validation | none-yet | suite profiles after P2-010a | substrate | analysis-plan-only | Tests whether Q4 coefficients compose in realistic session ecology. |
| RQ-ORDER-POSITION | Order-position effects | methodology artifact | candidate | L2 | no category/thermal inference without executable order policy | none-yet | suite profiles after ordering executability | substrate | analysis-plan-only | Drift/order probe; not a headline result. |
| RQ-CACHE-PREFIX | Cache/prefix economics; C5-2.13 | research question | candidate | L2 | no bundled cache-state conclusion without exact cache policy; no crossover generalization beyond the measured prompt-length ladder | none-yet | none | software | analysis-plan-only | Covers prefix reuse, resident state, and prompt-cache warmth; candidate C5-2.13 attaches a same-machine/same-stack energy crossover at earliest PF ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-AXI-HYBRID-PAIR | Named hybrid (SSM/attention)-vs-pure-transformer pair | research question | candidate | L2 pair-specific characterization | no architecture-class efficiency generalization, causal SSM-mechanism attribution, or tokenizer-blind ranking from one named pair | none-yet | post-floors named-pair campaign | floor | analysis-plan-only | Earliest PF; floor-gated and bindingly worded as “this named pair”; controlled-pair availability remains NEEDS-WEB ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-EXTERNAL-MARKED-RUNNER | External marked-runner energy layer | capability claim | candidate | L1/L2 with AP row | no accuracy, leaderboard, pass@k, or capability interpretation | none-yet | P2-022 | substrate | fully | Export-layer feasibility becomes research only when overhead/energy comparisons are specified. |
| RQ-HUMANEVAL-IMPORT-SMOKE | HumanEval import smoke | capability claim | candidate | L0/L1 | no coding-capability, pass@k, or accuracy claim | none-yet | P2-023 | substrate | no | Plumbing smoke for frozen external subset provenance. |
| C5-2.1 | Quantization decomposition, cross-stack | research question | candidate | L2 | no cross-boundary quant winner without calibration | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Extends C5-1.12 to CUDA/GGUF legs. |
| C5-2.2 | Batch size and prefill/decode energy split | research question | candidate | L2 | no serving conclusion without latency-bound policy | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Strong systems question for serving-style hardware and batching backend. |
| C5-2.3 | Predicted-vs-measured KV economics | research question | candidate | L2 | no KV economics claim without measured payload/link/deserialization terms | none-yet | P1-004 plus P1-006 | hardware | fully | One of the strongest Phase 3 questions; useful even if live split fails. |
| C5-2.4 | KV-cache quantization end-to-end; C5-2.11 on-device MLX leg | research question | candidate | L2 | no byte-saving equals energy-saving claim | none-yet | none | software | analysis-plan-only | Transfer leg still depends on cache portability; candidate C5-2.11 is the PF on-device MLX-scoped leg and also binds output-equivalence evidence ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.11 | On-device quantized-KV energy | research question | candidate | L2, per-boundary, MLX-scoped | no byte-saving-equals-energy-saving claim; no cross-runtime generalization from MLX alone; no quality-neutrality claim without C-023-style output-equivalence evidence | none-yet | post-floors Mac cache-policy campaign | floor | analysis-plan-only | Earliest PF; indexed under C5-2.4/C5-1.12/C-023-QUALITY-EQUIV-QUANT and runnable without the transfer leg ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.6 | Request coalescing under latency bound | research question | candidate | L2 | no scheduler optimum without arrival trace and latency policy | none-yet | none | hardware | analysis-plan-only | Useful but drifts toward scheduler research. |
| C5-2.7 | Device perf/W rankings with runtime held constant; kernel-provenance rider | research question | candidate | L2 within boundary; L4 with second unit/calibration | no generic hardware or cross-vendor kernel-API ranking from heterogeneous boundaries | none-yet | P1-006; 3080 Ti borrow window | hardware | fully | Candidate NV rider records attention-kernel/BLAS/graph provenance and remains per-boundary at L2; NEEDS-WEB feasibility stays open ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.8 | Placement-policy optimality from Q4 coefficients | research question | candidate | L2/L3 | no optimal-placement claim without measured split validation cells | none-yet | Phase 3 full set | hardware | fully | Uses Q4 coefficients plus measured transfer costs to choose placement. |
| C5-2.9 | Local-vs-datacenter crossover economics | research question | candidate | scenario result only | no measured-equivalent cloud comparison | none-yet | P1-003 plus P1-004 | hardware | analysis-plan-only | Surviving scenario form of the carbon-label kill. |
| C5-3.1 | Machine-to-machine variance; generalizability floor | research question | candidate | L4 enabler | no population claim from one unit | none-yet | second M-series unit | hardware | fully | Cheapest route from stack-specific to replication-aware claims. |
| C5-3.2 | Battery-path energy and modeled-rail validation | research question | candidate | L2/L4 bridge | no full-system claim from modeled rails alone | none-yet | USB-C PD analyzer | hardware | fully | Complements AC wall meter with a second physical boundary. |
| C5-3.3 | Cross-ISA NPU/SoC comparison; backend-provenance rider | research question | candidate | L4 only after replication | no broad cross-ISA claim before platform-specific adapter study; no NVIDIA-vs-AMD efficiency claim from single units or heterogeneous boundaries | none-yet | new platform adapters | hardware | analysis-plan-only | Candidate PC provenance rider is capped at L1 and records backend identity now; it creates no AMD science commitment ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-3.4 | Phone-class edge inference | capability claim | candidate | L0/L1 first | no promised phone science before telemetry feasibility | none-yet | phone feasibility | hardware | no | Feasibility verdict may be the result. |
| C5-3.5 | Cross-lab replication | methodology artifact | candidate | L4 enabler | no public benchmark credibility claim without replication | none-yet | external lab coordination | coordination | fully | Coordination-gated credibility layer. |
| C-023-TELEMETRY-PERTURBATION | Telemetry perturbation cost | methodology artifact | candidate (C-023) | L1/L2 floor component | no near-floor claim without telemetry-on/off ABBA check | none-yet | P2-015 component | floor | analysis-plan-only | New coverage-gap row; distinct from C5-1.6 sampling-strategy overhead. |
| C-023-VERSION-DRIFT | OS/runtime version-drift forensics; OS/driver/runtime update forensics | research question | candidate (C-023) | L1/L2 stack-conditioned | no version regression claim without before/after pinned bundles | none-yet | none | software | analysis-plan-only | Turns version churn into a named science/application row. |
| C-023-MARKER-JITTER | Marker/window jitter sensitivity; sampler-phase jitter sensitivity | methodology artifact | candidate (C-023) | L1 methodology; blocker for phase/item claims | no phase/item joule claim without jitter/sampler-phase sensitivity bound | none-yet | P2-015 or claim gate | floor | analysis-plan-only | Quantifies reducer sensitivity to timestamp jitter and sampler phase offset. |
| C-023-OUTPUT-IDENTITY | Output-token identity effects; binding gate for C5-2.5a/b/c/d | methodology artifact | candidate (C-023) | L1/L2 depending comparison | no quant/runtime/spec-decoding efficiency claim without equivalence or divergence report | none-yet | none | software | analysis-plan-only | Fixed output-token count is not fixed decoded work; binding for the PF/NS speculative-decoding riders admitted by D-075 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-IDLE-STATIONARITY | Idle-baseline stationarity | methodology artifact | candidate (C-023) | L1 methodology | no idle-subtracted conclusion without idle model-choice sensitivity | none-yet | P2-015 component | floor | analysis-plan-only | D-067 CLOSED the headline-basis question: gross energy within the named boundary is primary. This row stays alive only to test how idle-model choice affects conclusions in the labeled within-device SECONDARY view. |
| C-023-QUALITY-EQUIV-QUANT | Quality-equivalent quantization comparisons; C5-2.11 gate | research question | candidate (C-023) | L2 after equivalence rule | no quantization efficiency or quality-neutrality claim without AP-level equivalence rule | none-yet | none | software | analysis-plan-only | C5-2.11's candidate PF on-device KV leg binds this gate; footprint savings alone do not establish energy or quality neutrality ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-COEFF-TRANSPORT | Coefficient transport synthetic-to-realistic; energy model portability across workload mixtures | research question | candidate (C-023) | L2/L3 depending holdout | no realistic-session prediction from synthetic grid without transport validation | none-yet | suite traces after Q4 | substrate | analysis-plan-only | Explicitly tests Q4 coefficient transport from synthetic grids to realistic app traces. |
| APP-PROMPT-PROFILER | Prompt/template energy profiler | application idea | candidate | internal L1/L2 only | no prompt-quality claim | none-yet | none | software | analysis-plan-only | Product-facing use of prompt/template energy sensitivity. |
| APP-BUNDLE-POWER-BUG | Attach-a-bundle power-bug repro | application idea | candidate | L0/L1 support workflow | no general bug diagnosis without reproduced bundle | none-yet | none | software | analysis-plan-only | Uses bundle completeness as a maintainer repro artifact. |
| APP-CI-ENERGY-GATES | CI energy-regression gates | application idea | candidate | internal L1/L2 after floors | no CI failure threshold below detection floor | none-yet | P2-015 prerequisite | floor | analysis-plan-only | Needs floors, env snapshots, and baseline-refresh policy. |
| APP-VENDOR-PRESS-AUDIT | Vendor/press claim audit | application idea | candidate | boundary-named L1/L2 | no absolute device-energy verdict without calibration | none-yet | none | hardware | analysis-plan-only | Can audit specific boundary/workload claims, not universal efficiency. |
| APP-MODEL-CARDS | Practitioner energy model cards / leaderboard | application idea | candidate | internal only until L4 replication | no public leaderboard before cross-lab replication | none-yet | C5-3.5 prerequisite | coordination | analysis-plan-only | Internal table can exist; public version is killed until replication. |
| APP-TEACHING-INSTRUMENT | Teaching instrument | application idea | candidate | pedagogical L0/L1 | no research generalization from teaching bundles | none-yet | none | software | analysis-plan-only | Uses bundles for methodology labs on boundaries, floors, and uncertainty. |
| APP-STANDARDS-CONTRIBUTION | Bundle contract as standards contribution | application idea | candidate | methodology artifact proposal | no claim to be the standard | none-yet | none | coordination | analysis-plan-only | Exports the artifact format and validation discipline. |
| APP-CARBON-LABELS | Carbon labels | application idea | killed | none | no carbon label without wall meter and grid assumptions | none-yet | none | hardware | no | Killed as product label; C5-2.9 is the surviving scenario question. |
| APP-BATTERY-RUNTIME | Battery-runtime estimates without calibration | application idea | killed | none | no battery-runtime estimate without system-level calibration | none-yet | none | hardware | no | Explicitly deferred/killed by the application shortlist. |
| APP-LOCAL-CLOUD-ROUTING | Local-vs-cloud routing product | application idea | killed | none | no routing product while cloud side is unmeasured | none-yet | none | hardware | no | Killed product form; scenario analysis remains C5-2.9. |

## Attribution Limits

The rows whose historical wording most invited over-attribution are:

- `C5-1.1`: active-parameter energy scaling. The C-014 amendment caps
  4-6-model designs at descriptive L2 pairwise contrasts unless the model set
  grows enough for a predeclared one-covariate fit, and forbids fitting
  active+total+KV covariates on 4-6 model points. The claims ladder also
  prevents L1 active-parameter-scaling language; the capability map records
  the current two-model observation as a non-claim.
- `C5-1.8`: runtime energy attribution. The bank already says comparisons
  where formats force different artifacts are stack-vs-stack comparisons.
  The registry therefore forbids wording that energy "belongs to the runtime"
  unless the artifact/runtime identity problem is actually controlled.

This subsection is hygiene for claims indexing. It does not re-adjudicate the
ratified C-014/C-015 bank decisions.
# Prefill-contrast feasibility desk check — synthesis (2026-08-07)

Sol scout (read-only, high, gpt-5.6-sol) over historical diagnostics;
prompt + full response in this directory. ALL NUMBERS NON-CLAIM /
DIAGNOSTIC.

**Verdict: MARGINAL at the historical 128-token workload.** Best-evidence
matched ABBA diagnostic (decode-contrast window's off-manifest prefill
field, 20v20 members, identical prompt hash): 7B−1.5B prefill delta
5.809930 J point vs the ~5 J practical bar (D-078 cl.11 / D-083 wording
control — two separately enforced gates, not one summed threshold);
composed contrast half-width ~1.81 J puts the interval lower edge ~4.0 J,
BELOW the bar. Independent cross-window subtraction corroborates
(5.903 J).

**Length is the lever:** 1.5B prefill scales ~proportionally with prompt
length (128→4096 tokens predicts within ~3.3%); a prospectively frozen
256-token prompt projects ~11.6 J (~2.3× bar). NO long-prompt 7B corpus
exists — the projection is an extrapolation and workload resizing is a
preregistration decision (estimand change).

**Recommended default (scout + magistrate CONCUR):** claim prefill
FLOORS; keep the model contrast decode-only; state the 128-token
marginality as a limitation. The 256-token contrast is Ed's ruling
(needs_ruling row): +~110 core minutes, likely splits into its own
window.

**Consumed by:** the MVP paper draft §7 "Prospective workload sizing"
(qualitative, no diagnostic joules quoted per the draft's
no-demo-values discipline) and the pending fork/window planning.
Scout flags F1 (D-083 wording preserved), F2 (no long-prompt 7B
evidence), F3 (CLAIMS_STATUS staleness vs D-116 — check before window
freeze) all noted.

exec
/bin/zsh -lc "nl -ba docs/strategy/2026-08-06-impressiveness-roadmap.md | sed -n '1,120p'; nl -ba docs/strategy/2026-08-06-impressiveness-roadmap.md | sed -n '121,240p'; nl -ba docs/research_question_registry.md | sed -n '1,160p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
     1	```json
     2	{
     3	  "schema": "claude-codex-report/v1",
     4	  "genre": "review",
     5	  "status": "findings",
     6	  "completion": "complete",
     7	  "summary": "The strongest feasibility-weighted path is a clean C/D metrology campaign, external wall validation, and an evaluation-ready artifact before adding one hypothesis-driven expansion.",
     8	  "workspace": {
     9	    "base_requested": null,
    10	    "base_mode": "informational",
    11	    "head_start": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    12	    "head_end": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    13	    "upstream_end": "665fd5821f74e579071fba9ddd9717b77ded6a01",
    14	    "branch": "main"
    15	  },
    16	  "pathspec": [],
    17	  "unowned_dirty": [],
    18	  "verdict": {
    19	    "findings": [
    20	      {
    21	        "id": "F1",
    22	        "severity": "blocker",
    23	        "title": "The paper's claim-bearing experimental spine is not yet complete",
    24	        "detail": "D-110 still withholds the floor and contrast artifacts pending issuance/remint, while D-113 requires fresh Window C collection, prospectively split into D if needed."
    25	      },
    26	      {
    27	        "id": "F2",
    28	        "severity": "should_fix",
    29	        "title": "D-041 is not the mechanism-level fence",
    30	        "detail": "D-041 governs external-benchmark import/export and limits the export shim to an energy layer; AXI mechanism studies are governed primarily by D-070, D-075, their analysis plans, and runtime feasibility verdicts."
    31	      },
    32	      {
    33	        "id": "F3",
    34	        "severity": "should_fix",
    35	        "title": "Venue and calendar ambition remain unbound",
    36	        "detail": "The report deadline, colloquium, 3080 Ti window, and venue-specific evidence-by dates remain TBD, preventing rational allocation of measurement nights."
    37	      },
    38	      {
    39	        "id": "F4",
    40	        "severity": "nit",
    41	        "title": "The requested methods draft is not on main",
    42	        "detail": "docs/paper/draft-v1.md exists on impl/paper-draft-v1 but is absent from main; the branch version was inspected for this review."
    43	      }
    44	    ]
    45	  },
    46	  "verification": [
    47	    {
    48	      "id": "V1",
    49	      "kind": "inspection",
    50	      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse --abbrev-ref HEAD && git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true",
    51	      "cwd": ".",
    52	      "observed": {
    53	        "result": "pass",
    54	        "exit_code": 0,
    55	        "tail": [
    56	          "665fd5821f74e579071fba9ddd9717b77ded6a01",
    57	          "main",
    58	          "origin/main"
    59	        ]
    60	      },
    61	      "expected": {
    62	        "exit_code": 0,
    63	        "tail_regex": "665fd5821f74e579071fba9ddd9717b77ded6a01\\nmain\\norigin/main"
    64	      }
    65	    },
    66	    {
    67	      "id": "V2",
    68	      "kind": "inspection",
    69	      "cmd": "test ! -e docs/paper/draft-v1.md && git cat-file -e impl/paper-draft-v1:docs/paper/draft-v1.md && printf 'draft_main=absent\\ndraft_branch=present\\n'",
    70	      "cwd": ".",
    71	      "observed": {
    72	        "result": "pass",
    73	        "exit_code": 0,
    74	        "tail": [
    75	          "draft_main=absent",
    76	          "draft_branch=present"
    77	        ]
    78	      },
    79	      "expected": {
    80	        "exit_code": 0,
    81	        "tail_regex": "draft_main=absent\\ndraft_branch=present"
    82	      }
    83	    }
    84	  ],
    85	  "flags": [
    86	    {
    87	      "id": "FL1",
    88	      "kind": "baseline_drift",
    89	      "level": "nonblocking",
    90	      "text": "The prompt identifies docs/paper/draft-v1.md as current, but it is present only on the impl/paper-draft-v1 branch.",
    91	      "needs": "Lead should integrate or otherwise disposition the paper-draft branch."
    92	    },
    93	    {
    94	      "id": "FL2",
    95	      "kind": "verification_gap",
    96	      "level": "nonblocking",
    97	      "text": "No test suite was run because this was a read-only strategic synthesis with no repository modifications.",
    98	      "needs": ""
    99	    }
   100	  ]
   101	}
   102	```
   103	
   104	## Findings
   105	
   106	### F1 — Finish the claim-bearing metrology spine before expanding
   107	
   108	The instrument and its evidence machinery are unusually mature, but the paper still lacks a complete claim-bearing characterization result. The 1.5B/7B contrast passed collection gates and is a compelling preliminary demonstration, yet D-110 prevents formal use until the issuance/remint chain completes. D-113 then requires fresh Window C collection—split into D if necessary—without importing any retired Window B member. See [D-113](/Users/edr/code/JouleWise/docs/decision_log.md:7240) and the [current paper outline](/Users/edr/code/JouleWise/docs/run_reports/2026-07-30-paper-outline-v1.md:1).
   109	
   110	That is the critical path. A broad paper with incomplete C1–C6 evidence will look less serious than a narrower paper that cleanly demonstrates linearity, null response, empirical floor behavior, additivity, drift/settling, and between-session stability.
   111	
   112	D-113’s rigor-first posture forbids:
   113	
   114	- Salvaging failed A/B data into replacement claim cells.
   115	- Excluding an inconvenient member after seeing results.
   116	- Compressing an oversized campaign into one night.
   117	- Weakening calibration, whole-window, clock, or custody gates for schedule reasons.
   118	- Adding process or repetitions without a named validity threat or material claim benefit.
   119	
   120	It explicitly permits—and often prefers—smaller independent windows, narrower claims, and cutting an expansion.
   121	
   122	### F2 — Exact D-041 ruling and the real mechanism fence
   123	
   124	D-041 is titled “Benchmark interop — frozen-subset imports + marker-shim energy layer.” It fences:
   125	
   126	- External benchmark imports to hash-frozen subsets with identity, licensing, and contamination records.
   127	- Export to a marker-emitting shim where the external harness owns prompts, generation semantics, and accuracy; JouleWise owns capture, bundle assembly, marker validation, and energy reduction.
   128	- Joined reporting to observed energy beside the external metric artifact—never JouleWise accuracy, pass@k-per-joule, leaderboard standing, or intelligence-per-joule.
   129	- Implementation to after 2M and P2-010a, unless D-034 is explicitly reopened.
   130	- Interop expansion to be cut before core Mac characterization under schedule pressure.
   131	
   132	Thus, “unfencing D-041” would require completing 2M and P2-010a—or an explicit decision reopening D-034/D-041 sequencing—then passing P2-022’s marker feasibility spike and writing an analysis-plan row before any L2 claim. It still would not authorize mechanism attribution.
   133	
   134	The KDA/speculative-decode/MTP/MoE program is instead governed by D-070/D-075 and the AXI contracts:
   135	
   136	- Post-core/floor sequencing.
   137	- L2 ceiling for named studies unless Q4’s independent L3 machinery applies.
   138	- Direct observability rather than inference from configuration.
   139	- Output/quality-equivalence controls.
   140	- Named forbidden generalizations.
   141	
   142	The current feasibility facts matter:
   143	
   144	- External-draft speculative generation exists, but pinned `mlx-lm` lacks actual proposal counts and decode-step emission boundaries.
   145	- Native MTP is unsupported: the pinned runtime does not execute the heads.
   146	- KDA/hybrid comparisons currently involve cross-model confounding and unverified long-context execution.
   147	- MoE mechanism language requires auditable routing evidence; otherwise the claim must remain a named-model energy comparison, not routing attribution.
   148	- No tracked repository document uses “KDA” as a governed project axis; it appears in the nonbinding mechanism-literature sweep, not D-041.
   149	
   150	### Ranked roadmap
   151	
   152	Planning estimates below assume the current 2–4-hour claim-window protocol, at least 20% failure margin, and physical Ed preparation through §5A.
   153	
   154	| Rank | Expansion | Why it impresses reviewers | Estimated effort and Ed-present sessions | Dependencies and principal risk | Decision required |
   155	|---:|---|---|---|---|---|
   156	| **1** | **Complete C1–C7 cleanly: remint, fresh C/D, and stability** | Converts the strongest idea—the instrument and its refusal behavior—into actual evidence. This is the difference between an elaborate methodology and a metrology paper. | **3–6 weeks after desk gates; 2 mandatory nights plus 1 contingency/short stability session.** | D-079 issued artifact; D-110 remint; reviewed frozen-plan record; fresh §5A; C/D split if scope cannot fit. Risk: another environmental or clock refusal. | Reserve the core nights now and prohibit breadth work from consuming them. |
   157	| **2** | **External wall-meter validation of totals, C8** | Directly addresses the obvious reviewer question: “Does `powermetrics` agree with physical input power?” It materially upgrades absolute-scale credibility. | **4–8 weeks; 1 pilot plus 1 confirmatory session.** The confirmatory run may share a later frozen campaign only after the importer and protocol pass independently. | Professional AC analyzer, safe inline fixture, synchronized export, fixed ranges, load-specific uncertainty, battery charge neutralization, held-out regression. It validates totals only—not phase allocation. | D-092 already decided “yes”; Ed/advisor must now authorize purchase/loan, budget, and an evidence-by date. |
   158	| **3** | **Artifact-evaluation-quality release** | Hash-bound raw-to-figure reproducibility is a genuine differentiator and unusually well aligned with JouleWise’s thesis. Reviewers can verify refusals and re-derive results rather than trust screenshots. | **4–6 weeks; 0 measurement nights.** | Sanitized raw-bundle subset, one-command validation/reduction/figure path, locked environment, quick/full tracks, immutable archive/DOI, clear hardware-free replay. Risk: privacy, dataset size, and Mac-only collection requirements. | Decide whether the target is merely open source or formal ICPE-style artifact evaluation, and which evidence may be public. |
   159	| **4** | **Designed workload-shape matrix with held-out prediction—Q4/L3** | A predictive fixed-plus-marginal model validated on held-out cells is substantially more serious than “we ran more prompts.” It can earn L3 rather than another collection of L1/L2 points. | **6–10 weeks; approximately 2–3 nights.** | P2-006 baseline sizing, AP-1, 4×3 grid, predeclared holdouts, residual/sensitivity analysis, floor audit. Risk: the simple model may fail its holdouts—which must be reported honestly. | Fund the full designed matrix or omit the predictive claim; do not replace it with opportunistic workload breadth. |
   160	| **5** | **Quality-gated BF16/Q8/Q4 quantization ladder** | A clean same-family ladder with error bars and output-divergence reporting can adjudicate the reported q4-vs-q8 anomaly. Strong workshop demonstration; moderate novelty. | **4–8 weeks; 1–2 nights.** Quality screening can run outside quiet windows. | One frozen source revision, reproducible conversions, 256-item quality gate, 32-item energy subset, stack-specific floors. Risk: quality may not be equivalent or quantization may alter cadence beyond existing calibration support. | Choose the model family before conversion; accept a quality/energy trade-off result if equivalence fails. |
   161	| **6** | **Second-unit replication after multi-day same-unit stability** | This is the clearest path beyond single-machine claims and toward L4. It demonstrates that the artifact and calibration method transfer, not merely that one laptop is stable. | **4–8 weeks once access exists; 2 sessions on the second unit, 0–2 Ed-present depending on operator.** | A second comparable Apple unit, frozen stack or explicitly modeled version difference, independent calibration and artifact execution. Risk: OS/hardware drift may make it replication-aware rather than directly pooled. | Secure a second unit/collaborator or explicitly retain the single-unit ceiling. |
   162	| **7** | **One mechanism-level study, conditional on a hard feasibility gate** | **Highest scientific ceiling.** A controlled batch-1 speculative-decode or MTP energy result could be genuinely novel; KDA/context slope or MoE routing is also interesting if attribution is identifiable. | **2–3-week desk feasibility gate; if passed, another 6–12 weeks and roughly 2 nights.** | New/forked runtime instrumentation, direct proposal/acceptance events, output identity/equivalence, mechanism-specific AP and floors. MTP currently cannot execute; KDA is confounded; MoE routing visibility is uncertain. | Pick exactly one mechanism and a kill date. Recommended first choice: external-draft speculative decode, because it offers the cleanest same-target on/off contrast if observability can be added. |
   163	| **8** | **Split inference: synthetic transfer plus one offline split pairing** | Demonstrates the instrument under two boundaries, a transfer interval, and cross-device clocks. A complete per-stage bundle is impressive even without a crossover. | **2–4 months; roughly 3–5 two-device measurement sessions.** Live split adds more and should remain stretch. | Schema v0.2, remaining replay verdicts, two-node telemetry, clock bounds, transfer bench, 3080 Ti window, two links, wall/host boundary or lower-bound wording. Risk is high and the engineering can dominate the paper. | Commit only to synthetic transfer plus offline replay; authorize live split separately after offline results. |
   164	| **9** | **Additional model families, generic workloads, Jetsons** | Useful corroboration, but mostly incremental unless each addition tests a predeclared hypothesis or provides independent replication. More rows do not overcome the single-unit or boundary limitations. | **3–8 weeks and 1–2 nights per coherent axis/device.** | New model lineage, adapter, quality and floor cells; Jetson remains optional and remote pins are provisional. | Add only a model or device that changes the claim—not merely the size of a results table. |
   165	
   166	For the wall-meter path, the right class is a calibrated bench AC power analyzer, not an inexpensive consumer plug. A concrete baseline is the Yokogawa WT310E: its manufacturer lists 10 readings/s, USB export, 0.1%-of-reading plus 0.05%-of-range basic accuracy, high crest-factor capability, and a **$2,935 base US price** before calibration/fixture costs. Actual suitability still depends on calculating uncertainty at the Mac’s observed load and using a safe inline fixture. Borrowing an in-calibration unit from an engineering lab is preferable to spending several thousand dollars. [Yokogawa WT310E specifications and current price](https://tmi.yokogawa.com/us/solutions/products/power-analyzers/digital-power-meter-wt300e/).
   167	
   168	### Venue ambition
   169	
   170	| Tier | What the current/expanded project can support | What should be present |
   171	|---|---|---|
   172	| **CSCSU** | After remint and clean C/D, this should be a strong undergraduate-conference submission. The latest published rules allow technical papers and extensive experimentation, with **5 pages including references**. [CSCSU 2026 guidance](https://cscsu-conference.github.io/) | C1–C6 core, one demonstration, crisp limitations, compact artifact pointer. Wall validation and split are not necessary. |
   173	| **EuroMLSys/HotCarbon workshop** | The natural near-term research target. EuroMLSys’s latest call uses 6 pages excluding references; HotCarbon uses 5 pages excluding references and no appendix. [EuroMLSys](https://euromlsys.eu/), [HotCarbon CFP](https://hotcarbon.org/cfp) | Clean metrology core, model contrast, wall validation if available, and polished artifact. EuroMLSys is the better technical-method fit; HotCarbon needs a stronger sustainability-metrics argument. |
   174	| **ICPE Emerging/WIP** | Appropriate if the core is strong but external validation, replication, or the broader predictive evaluation remains incomplete. The 2026 track used a 6-page format. [ICPE Emerging Research](https://icpe2026.spec.org/tracks-and-submissions/emerging-research-track/) | Validated core, transparent open gaps, early artifact, and a credible expansion plan. |
   175	| **ICPE full research track** | Plausible over months, but not yet supported by the current evidence. ICPE 2027 lists research and artifact tracks but their details and dates remain TBA. The 2026 research track used 10 pages and judged novelty, technical quality, and scientific soundness; 2026’s reported full-paper acceptance rate was 28%. [ICPE 2027](https://icpe2027.spec.org/tracks-and-submissions/research-paper-track/), [2026 research criteria](https://icpe2026.spec.org/tracks-and-submissions/research-paper-track/), [acceptance history](https://icpe.spec.org/past-conferences/) | C1–C8, cross-day stability, artifact-ready release, and at least one deeper contribution: held-out Q4 prediction, second-unit replication, or a successful mechanism study. Split is not required. |
   176	
   177	ICPE’s artifact track is especially aligned: it asks for documented, consistent, complete, exercisable artifacts, permanent archival availability, and practical setup/reproduction instructions. [ICPE artifact-evaluation criteria](https://icpe2026.spec.org/tracks-and-submissions/artifact-evaluation-track/).
   178	
   179	### Critical path to the strongest defensible version
   180	
   181	1. **Now:** finish D-079 issuance and the D-110 remint chain; integrate or disposition the draft branch; set actual calendar and venue evidence-by dates.
   182	2. **In parallel:** borrow/order the wall analyzer and build its importer, synchronization, and held-out validation protocol without assuming it will arrive in time.
   183	3. **First hardware block:** freeze and collect Window C, then D if the complete replacement cannot fit with the required margin. Add a third short day/session only if needed for the stated stability claim.
   184	4. **Immediately after each passing window:** produce the governed artifacts, deterministic figures, claim-index entries, and experimental prose. Do not wait for all expansions before writing.
   185	5. **Artifact block:** publish a sanitized, hash-bound raw-to-figure package with a fast hardware-free reproduction path and archival DOI.
   186	6. **Second hardware block:** run external wall validation.
   187	7. **Choose one expansion:** Q4 held-out prediction for the strongest ICPE case; quantization for the safest workshop enhancement; or mechanism work only if its short feasibility gate passes.
   188	8. **Only then consider split inference.** Start it only if the 3080 Ti window is dated and the transfer/offline-replay path is rehearsed before hardware access.
   189	9. **Freeze the dataset early:** reserve at least six weeks before submission for figures, claims audit, paper compression, artifact dry runs, and advisor review.
   190	
   191	The strongest realistic paper is therefore: **C1–C8 metrology + the already-collected 1.5B/7B demonstration + one designed extension + an independently usable artifact.** That is more coherent and defensible than a larger model/device matrix or an unfinished split system.
   192	
   193	### F3 — Five decisions Ed/advisor must make
   194	
   195	1. **Venue and publication sequence.** Choose CSCSU-only, workshop-first, or ICPE-full ambition, and verify whether a workshop publication may later be extended for ICPE. Build a 10-page master manuscript even if the first submission is shorter.
   196	
   197	2. **Physical measurement budget.** Recommended commitment: **5–7 Ed-present sessions**—C, D, one contingency/stability repeat, wall pilot/confirmation, and one extension. An ICPE-full attempt with Q4 and second-unit work likely needs **8–10 total sessions** across operators.
   198	
   199	3. **Meter execution.** D-092 has already answered “yes.” The remaining decision is: borrow versus buy, approximately $3,000-class budget, calibration/fixture responsibility, and a cutoff date after which C8 is cleanly removed.
   200	
   201	4. **Mechanism ambition.** Do not ask simply “unfence D-041.” Decide whether to retain D-070’s all-five-axis commitment or narrow it to one paper-worthy study. Recommended rule: two-to-three-week feasibility gate for speculative-decode observability; if it fails, return immediately to Q4/quantization.
   202	
   203	5. **External hardware priority.** Decide whether scarce coordination goes to a second Apple unit, the 3080 Ti split study, or Jetsons. Recommendation: second-unit replication first, 3080 Ti second, Jetsons last.
   204	
   205	### F4 — Draft-state correction
   206	
   207	The methods draft was inspected from `impl/paper-draft-v1` at commit `af0b7195`; it is one commit ahead of and one commit behind `main`. It already reflects the right rigor: result placeholders remain pending remint, all characterization rows are pending Window C, and the split section is framed as future demonstration work. It should be integrated deliberately so the paper itself becomes the continuously updated claim-state surface.
   208	
   209	## Residual risk
   210	
   211	- The mechanism-literature sweep is explicitly desk research, not governed project evidence. Any “first measured” novelty claim needs a fresh literature search immediately before submission.
   212	- Venue formats and deadlines cited above are current published 2026 rules or incomplete 2027 pages; 2027 calls may change.
   213	- Measurement-night estimates are planning ranges, not validated campaign runtimes.
   214	- Wall validation cannot establish phase attribution, and one external meter does not create cross-device generality.
   215	- Even an excellent single-Mac study remains stack-specific under the claims ladder unless second-unit or cross-lab replication lands.     1	# Research Question Registry
     2	
     3	Purpose: this is the canonical live index for JouleWise research questions,
     4	capability claims, application ideas, and methodology artifacts. It normalizes
     5	aliases, status, claim ceilings, owners, gates, and pre-hardware readiness so
     6	claims and campaign plans can point to one row. Promotion rules are unchanged
     7	from `docs/research_question_bank.md`: promotion still requires a named RQ slot
     8	in `PROJECT_STATUS.md`, a data plan that does not displace queue ranks above
     9	it, and scope fit.
    10	
    11	Maintenance rule: registry rows are LIVE state. The research question bank
    12	remains the historical and deliberative record, including council wording,
    13	kills, quarantines, and amendments. Single-writer split: update this registry
    14	for current indexing and cross-references; update the bank only when recording
    15	new deliberation history.
    16	
    17	Column legend:
    18	
    19	- `canonical_id`: stable row key for the live index.
    20	- `aliases`: other IDs, names, or capability-map labels for the same question.
    21	- `question_type`: one of `research question`, `capability claim`,
    22	  `application idea`, or `methodology artifact`.
    23	- `status`: `promoted`, `banked`, `candidate`, `killed`, `answered-L1`, or
    24	  the review-specific `candidate (C-023)`.
    25	- `claim_ceiling`: highest claim level currently allowed by the bank, review,
    26	  or capability map, before future evidence upgrades.
    27	- `forbidden_upgrade`: short reminder of language the row cannot support.
    28	- `AP owner`: analysis-plan owner if already named; otherwise `none-yet`.
    29	- `campaign owner`: queue row, phase, or campaign owner if already named.
    30	- `gate_class`: dominant gate class: `hardware`, `software`, `floor`,
    31	  `substrate`, or `coordination`.
    32	- `pre_hardware_preparable`: `fully`, `analysis-plan-only`, or `no`.
    33	- `one-line note`: indexing note, not a re-adjudication.
    34	
    35	## Registry Table
    36	
    37	| canonical_id | aliases | question_type | status | claim_ceiling | forbidden_upgrade | AP owner | campaign owner | gate_class | pre_hardware_preparable | one-line note |
    38	|---|---|---|---|---|---|---|---|---|---|---|
    39	| Q1 | Split reduces energy | research question | promoted | L2 boundary-labeled; stronger only with calibration | no uncalibrated cross-boundary total-energy winner | none-yet | Phase 3 split; P1-004; P1-006 | hardware | fully | Central split question; total energy must be decomposed and boundary-labeled. |
    40	| Q2 | Link bandwidth sensitivity | research question | promoted | L2 | no nominal-link crossover without measured links | none-yet | Phase 3 split; P1-004 | hardware | fully | Clean interconnect sensitivity question; link throughput and transfer energy must be measured. |
    41	| Q3 | Split energy-latency Pareto | research question | promoted | L2 | no Pareto claim without frozen set and latency metric | none-yet | Phase 3 split | hardware | fully | Requires a fixed comparison set and latency metric per figure. |
    42	| Q4 | Fixed-vs-marginal energy model; C5-2.14 cache-policy coefficient rider | research question | promoted | L3 | no holdout-prediction claim without AP-1 floor and residual checks | AP-1 | P2-019 q4_l3_shape_grid_v1 | floor | analysis-plan-only | Strongest predictive science row; includes compositional split-energy prediction only when transfer terms exist. C5-2.14 is a candidate rider capped at L2, earliest PF, with no coefficient-direction claim below P2-015 floors ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    43	| Q5 | Ranking stability | research question | promoted | L2 | no uncalibrated cross-device winner; no ranking where gap below MDE | AP-3 | 2M; Window B grid | floor | analysis-plan-only | Promoted within-machine ranking question; workload-axis analogue C5-W.3 remains a separate candidate row. |
    44	| Q6 | Boundary sensitivity; C5-2.10 boundary-directional bias quantification | research question | promoted | L2; L4 only with replication | no wall/rail conclusion flip claim without paired boundary plan | none-yet | P1-003 wall meter; F11 | hardware | fully | Registry indexes C5-2.10 as the C5 elaboration of promoted Q6. |
    45	| RQ-METHOD-FLOOR | Detection floor; noise floor; short-difference resolvability; phase/item identifiability flags; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | banked | L1 methodology | no below-floor effect language except `not resolvable`; no module-energy fraction or regression-slope attribution | none-yet | P2-015 | floor | analysis-plan-only | Methodology centerpiece and prerequisite for most comparative claims; the candidate module-attribution nonclaim attaches here at earliest NS instead of becoming a row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    46	| C5-1.11 | Dark silicon; rail utilization; ANE-dark finding | research question | candidate | L2 structural | no true silicon-energy fraction from modeled rails | none-yet | P2-009 rich telemetry; C5-1.8 runtime grid | software | analysis-plan-only | Measures modeled-rail utilization structure, not physical absolute rail truth. |
    47	| C5-1.3 | CPU:GPU phase division; rail/DVFS phase signatures; prefill/decode power asymmetry | research question | candidate | L2 structural | no short-phase joules when windows are under-resolved | none-yet | 2M with P2-009 | floor | analysis-plan-only | Merges the banked CPU:GPU phase question with C5-1.3 telemetry framing. |
    48	| RQ-KV-GROWTH | KV-growth decode drift; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | banked | L1/L2 chunked | no per-token joule claims; no attention-vs-FFN fraction from context slopes | none-yet | none | floor | analysis-plan-only | Candidate riders, earliest PF: bounded-window KV marginal slope and named-artifact attention/context slope; both retain chunked-window/floor discipline and stay attached rather than becoming independent rows ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    49	| C5-1.5 | Cooldown recovery as thermal characterization; cooldown-recovery curves | research question | candidate | L1/L2 | no claim that power recovery proves thermal-state equality | none-yet | none | floor | analysis-plan-only | Turns cooldown tails and cap-hit rates into reportable methodology evidence. |
    50	| C5-1.10 | Failure frontier | research question | candidate | L1/L2 descriptive | no silent discard of failures; no population claim from one memory class | none-yet | none | software | analysis-plan-only | Structured `unsupported`, fit, swap, throttle, and cap-hit outcomes become data. |
    51	| C5-1.7 | Cold-start / keep-warm energy; reload-vs-resident scheduling | research question | banked | L2 after harness extension | no breakeven without load-window and resident-idle sampling | none-yet | none | software | analysis-plan-only | Review and bank both identify reload-vs-resident as the same question. |
    52	| C5-1.9 | Energy-per-correct-answer vs difficulty; MoE-vs-dense controlled ladder | research question | banked | L2 after envelope and denominator guards | no intelligence-per-joule; no `difficulty causes energy` | AP-5 | P2-010a plus P2-010b plus later scored campaign | substrate | analysis-plan-only | Correctness remains quarantined annotation under the C-004/C-014 rules. |
    53	| C5-2.5 | Speculative-decoding energy; C5-2.5b proposal-work rider; C5-2.5c break-even rider | research question | banked | L2 | no efficiency claim without output equivalence and accepted-token accounting | none-yet | none | software | analysis-plan-only | C5-2.5c is the primary PF Q4 rider, C5-2.5b its PF secondary, and C5-2.5d the mandatory PF contamination control; C5-2.5a remains a deferred NS bank rider. `C-023-OUTPUT-IDENTITY` binds all efficiency contrasts ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    54	| RQ-POWER-MODE | Power-mode Pareto | research question | banked | L2 possible | no OS-mode conclusion until power mode is a first-class config field | none-yet | none | software | analysis-plan-only | Waits on config/environment capture for OS power modes. |
    55	| RQ-INTELLIGENCE-PER-JOULE | General joules-per-solved-task; intelligence-per-joule | research question | killed | none | no general intelligence-per-joule ratio | none-yet | none | substrate | no | Killed/quarantined by C-003/C-004; controlled ladder is the surviving minimal form. |
    56	| RQ-AUDITABLE-EVIDENCE | Can JouleWise produce auditable local-LLM energy evidence? | capability claim | answered-L1 | L0/L1 | no physical calibration claim from strict validation alone | none-yet | existing Mac/MLX/powermetrics bundles | software | no | Artifact contribution, not a research question. |
    57	| RQ-QWEN25-SMOKE | Qwen2.5-1.5B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from smoke result | none-yet | 2026-07-06 2I | software | no | Legit instrument observation for one named stack/workload. |
    58	| RQ-QWEN35-SMOKE | Qwen3.5-122B-A10B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from n=3 | none-yet | 2026-07-07 flagship addendum | software | no | Legit instrument observation for one named stack/workload. |
    59	| RQ-TWO-MODEL-ACTIVE-NONCLAIM | Did the two observed models demonstrate active-parameter scaling? | capability claim | answered-L1 | L1 hypothesis only | no active-parameter scaling claim | none-yet | 122B addendum; capability map | floor | no | Negative guard: two points are consistent with a hypothesis but do not support scaling. |
    60	| RQ-SHORT-PREFILL-RESOLVABILITY | Are short prefill phase joules resolvable?; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | answered-L1 | L1 `not resolvable` | no standalone short-prefill joule result; no relabeling request phases as module phases | none-yet | Phase 4 observation | floor | no | Existing cadence precedent owns the candidate module-attribution guard, earliest NS; no separate methodology row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    61	| RQ-MLX-KV-REPLAY | Same-machine MLX KV replay token identity and size prediction; C5-2.13 | capability claim | answered-L1 | L1 feasibility | no cross-machine portability claim | none-yet | Stage 3.0.1 | software | no | The L1 feasibility result remains answered; candidate C5-2.13, earliest PF and capped at L2, attaches the same-machine energy-crossover rider without cross-stack generalization ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    62	| RQ-MAC-BASELINES | Per-profile Mac baselines | capability claim | candidate | L1 per condition | no novelty or comparison claim without AP/floor | none-yet | 2M | floor | analysis-plan-only | Necessary baseline corpus, not a headline by itself. |
    63	| RQ-SHAPE-ENERGY | Workload shape changes request energy | research question | candidate | L2 | no causal token-shape claim beyond AP-2 contrasts | AP-2 | 2M | floor | analysis-plan-only | Distinct from Q4 because it describes shape contrasts rather than holdout prediction. |
    64	| C5-1.1 | Active-parameter energy scaling | research question | candidate | L2 pairwise only unless larger predeclared model set | no active+total+KV regression on 4-6 models | none-yet | P2-024 shortlist | floor | analysis-plan-only | C-014 caps the tempting wording; registry hygiene, not re-adjudication. |
    65	| C5-1.2 | Context-length energy scaling; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | candidate | L2/L3 if modeled | no short-prompt phase point claims; no wall implication from SoC rails | none-yet | none | floor | analysis-plan-only | Natural local-inference question with chunked phase limits; the two candidate PF riders remain capped at L2 and forbid module attribution from context-associated slopes ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    66	| C5-1.4 | DVFS residency as throttling early-warning | research question | candidate | L2 if prediction rule fixed | no prediction claim without horizon and rule | none-yet | none | software | analysis-plan-only | Convert characterization to a predeclared warning rule before claiming prediction. |
    67	| C5-1.6 | Sampling-strategy energy overhead | research question | candidate | L2 if above floor | no telemetry-perturbation claim from this row | none-yet | P2-024 shortlist | floor | analysis-plan-only | Bank row is greedy vs temperature/top-p/beam overhead, not sampler instrumentation cost. |
    68	| C5-1.8 | Runtime energy attribution; same-silicon kernel-layer provenance rider | research question | candidate | L2 stack-vs-stack | no `belongs to runtime` or `belongs to kernel layer` language when artifacts/formats differ; no runtime-agnostic kernel claim | none-yet | P2-024 shortlist | floor | analysis-plan-only | Candidate NV provenance rider stays inside the stack-conditioned comparison; it does not mint C5-1.13 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    69	| C5-1.12 | Quantization benefit decomposition, Mac leg | research question | candidate | L2 | no quantization efficiency claim without output divergence reporting | none-yet | P2-024 shortlist | floor | analysis-plan-only | Splits benefit into lower watts vs shorter time on one stack/family. |
    70	| C5-W.1 | Category beyond token counts; Token-Shape Sufficiency Null | research question | candidate | L2 | no category effect below floor or without shape control | AP-4 | jw_mixed_v1 after P2-010a | substrate | analysis-plan-only | Strong null-or-effect design for workload-category residuals. |
    71	| C5-W.2 | Thinking-token inflation | research question | candidate | L2 | no cognition claim; attribute only to emitted-token/stop distributions | none-yet | jw_mixed_v1 natural-EOS pilot | substrate | analysis-plan-only | Operational-cost view for reasoning models under natural EOS. |
    72	| C5-W.3 | Category energy-ranking stability; workload-axis Q5 analogue | research question | candidate | L2 | no category ranking claim where rank gap is below MDE or without workload-expansion gate | none-yet | jw_mixed_v1 workload expansion | substrate | analysis-plan-only | Workload-axis analogue of promoted Q5, not the same ratified question; asks whether code/long-context/reasoning categories flip model/quant ordering. |
    73	| C5-I.3 | C5-W.4; FLORES tokenizer fertility tax | research question | candidate | L2 | no tokenizer efficiency ranking without semantic and token-matched legs | none-yet | FLORES after HumanEval smoke | substrate | fully | C5-I.3 and C5-W.4 are the same FLORES fertility question. |
    74	| C5-I.1 | External benchmark energy signatures | research question | candidate | L2 | no benchmark capability or accuracy claim | none-yet | import/export contracts | substrate | fully | Needs matched shape/output policy before family-level energy signatures. |
    75	| C5-I.2 | Published-difficulty strata vs energy | research question | candidate | L1 association; L2 only if preplanned repeated bundles | no `difficulty causes energy` | none-yet | import/export contracts | substrate | fully | Weak/secondary because source difficulty labels are heterogeneous. |
    76	| C5-I.4 | Harness overhead floor | methodology artifact | candidate | L1/L2 | no item energy claim when harness overhead dominates unnoticed | none-yet | P2-022 shim | substrate | fully | Methodology question for marked external harnesses. |
    77	| C5-I.5 | Prompt-template energy sensitivity | research question | candidate | L2 | no prompt-quality or capability claim | none-yet | import/export contracts | substrate | fully | Same external item, canonical vs JouleWise-rendered prompt format. |
    78	| RQ-CONTENT-SENTINEL | Synthetic prompt content sentinel; fixed-shape content sensitivity | research question | candidate | L2 | no content-effect claim unless realized shape/stop policy stays matched and effect clears floor; no broad content-neutrality claim beyond the five tested AP-6 conditions | AP-6 | P2-020 content sentinel | substrate | analysis-plan-only | Tests whether synthetic prompt content matters at fixed shape under the AP-6 ids-native no-BOS sentinel design. |
    79	| RQ-ENERGY-VARIANCE | Sampling-induced energy variance; energy-at-risk per prompt; lucky-short-reasoning variance | research question | candidate | L2 within boundary | no intelligence-per-joule or correctness-causal claim (C-004 quarantine); variance claims need repeated-bundle n sized for variance estimation and floor-gated residuals; per-bundle sampler seeds must be recorded | none-yet | none (post-floor; reasoning model on current Mac feasible) | floor | analysis-plan-only | Ed-added 2026-07-09 row: distribution (not just mean) of request energy for a fixed hard prompt under sampling; decomposable into reasoning-length vs residual variance via recorded output token IDs + deterministic replay of sampled paths (P2-025 capture + 3.0.1 replay make paths replayable). |
    80	| RQ-SESSION-SHAPE | Session-shape energy | research question | candidate | L2/L3 depending holdout | no app-session prediction without holdout validation | none-yet | suite profiles after P2-010a | substrate | analysis-plan-only | Tests whether Q4 coefficients compose in realistic session ecology. |
    81	| RQ-ORDER-POSITION | Order-position effects | methodology artifact | candidate | L2 | no category/thermal inference without executable order policy | none-yet | suite profiles after ordering executability | substrate | analysis-plan-only | Drift/order probe; not a headline result. |
    82	| RQ-CACHE-PREFIX | Cache/prefix economics; C5-2.13 | research question | candidate | L2 | no bundled cache-state conclusion without exact cache policy; no crossover generalization beyond the measured prompt-length ladder | none-yet | none | software | analysis-plan-only | Covers prefix reuse, resident state, and prompt-cache warmth; candidate C5-2.13 attaches a same-machine/same-stack energy crossover at earliest PF ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    83	| RQ-AXI-HYBRID-PAIR | Named hybrid (SSM/attention)-vs-pure-transformer pair | research question | candidate | L2 pair-specific characterization | no architecture-class efficiency generalization, causal SSM-mechanism attribution, or tokenizer-blind ranking from one named pair | none-yet | post-floors named-pair campaign | floor | analysis-plan-only | Earliest PF; floor-gated and bindingly worded as “this named pair”; controlled-pair availability remains NEEDS-WEB ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    84	| RQ-EXTERNAL-MARKED-RUNNER | External marked-runner energy layer | capability claim | candidate | L1/L2 with AP row | no accuracy, leaderboard, pass@k, or capability interpretation | none-yet | P2-022 | substrate | fully | Export-layer feasibility becomes research only when overhead/energy comparisons are specified. |
    85	| RQ-HUMANEVAL-IMPORT-SMOKE | HumanEval import smoke | capability claim | candidate | L0/L1 | no coding-capability, pass@k, or accuracy claim | none-yet | P2-023 | substrate | no | Plumbing smoke for frozen external subset provenance. |
    86	| C5-2.1 | Quantization decomposition, cross-stack | research question | candidate | L2 | no cross-boundary quant winner without calibration | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Extends C5-1.12 to CUDA/GGUF legs. |
    87	| C5-2.2 | Batch size and prefill/decode energy split | research question | candidate | L2 | no serving conclusion without latency-bound policy | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Strong systems question for serving-style hardware and batching backend. |
    88	| C5-2.3 | Predicted-vs-measured KV economics | research question | candidate | L2 | no KV economics claim without measured payload/link/deserialization terms | none-yet | P1-004 plus P1-006 | hardware | fully | One of the strongest Phase 3 questions; useful even if live split fails. |
    89	| C5-2.4 | KV-cache quantization end-to-end; C5-2.11 on-device MLX leg | research question | candidate | L2 | no byte-saving equals energy-saving claim | none-yet | none | software | analysis-plan-only | Transfer leg still depends on cache portability; candidate C5-2.11 is the PF on-device MLX-scoped leg and also binds output-equivalence evidence ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    90	| C5-2.11 | On-device quantized-KV energy | research question | candidate | L2, per-boundary, MLX-scoped | no byte-saving-equals-energy-saving claim; no cross-runtime generalization from MLX alone; no quality-neutrality claim without C-023-style output-equivalence evidence | none-yet | post-floors Mac cache-policy campaign | floor | analysis-plan-only | Earliest PF; indexed under C5-2.4/C5-1.12/C-023-QUALITY-EQUIV-QUANT and runnable without the transfer leg ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    91	| C5-2.6 | Request coalescing under latency bound | research question | candidate | L2 | no scheduler optimum without arrival trace and latency policy | none-yet | none | hardware | analysis-plan-only | Useful but drifts toward scheduler research. |
    92	| C5-2.7 | Device perf/W rankings with runtime held constant; kernel-provenance rider | research question | candidate | L2 within boundary; L4 with second unit/calibration | no generic hardware or cross-vendor kernel-API ranking from heterogeneous boundaries | none-yet | P1-006; 3080 Ti borrow window | hardware | fully | Candidate NV rider records attention-kernel/BLAS/graph provenance and remains per-boundary at L2; NEEDS-WEB feasibility stays open ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    93	| C5-2.8 | Placement-policy optimality from Q4 coefficients | research question | candidate | L2/L3 | no optimal-placement claim without measured split validation cells | none-yet | Phase 3 full set | hardware | fully | Uses Q4 coefficients plus measured transfer costs to choose placement. |
    94	| C5-2.9 | Local-vs-datacenter crossover economics | research question | candidate | scenario result only | no measured-equivalent cloud comparison | none-yet | P1-003 plus P1-004 | hardware | analysis-plan-only | Surviving scenario form of the carbon-label kill. |
    95	| C5-3.1 | Machine-to-machine variance; generalizability floor | research question | candidate | L4 enabler | no population claim from one unit | none-yet | second M-series unit | hardware | fully | Cheapest route from stack-specific to replication-aware claims. |
    96	| C5-3.2 | Battery-path energy and modeled-rail validation | research question | candidate | L2/L4 bridge | no full-system claim from modeled rails alone | none-yet | USB-C PD analyzer | hardware | fully | Complements AC wall meter with a second physical boundary. |
    97	| C5-3.3 | Cross-ISA NPU/SoC comparison; backend-provenance rider | research question | candidate | L4 only after replication | no broad cross-ISA claim before platform-specific adapter study; no NVIDIA-vs-AMD efficiency claim from single units or heterogeneous boundaries | none-yet | new platform adapters | hardware | analysis-plan-only | Candidate PC provenance rider is capped at L1 and records backend identity now; it creates no AMD science commitment ([evaluation](process_traces/2026-07-17-extension-axes/)). |
    98	| C5-3.4 | Phone-class edge inference | capability claim | candidate | L0/L1 first | no promised phone science before telemetry feasibility | none-yet | phone feasibility | hardware | no | Feasibility verdict may be the result. |
    99	| C5-3.5 | Cross-lab replication | methodology artifact | candidate | L4 enabler | no public benchmark credibility claim without replication | none-yet | external lab coordination | coordination | fully | Coordination-gated credibility layer. |
   100	| C-023-TELEMETRY-PERTURBATION | Telemetry perturbation cost | methodology artifact | candidate (C-023) | L1/L2 floor component | no near-floor claim without telemetry-on/off ABBA check | none-yet | P2-015 component | floor | analysis-plan-only | New coverage-gap row; distinct from C5-1.6 sampling-strategy overhead. |
   101	| C-023-VERSION-DRIFT | OS/runtime version-drift forensics; OS/driver/runtime update forensics | research question | candidate (C-023) | L1/L2 stack-conditioned | no version regression claim without before/after pinned bundles | none-yet | none | software | analysis-plan-only | Turns version churn into a named science/application row. |
   102	| C-023-MARKER-JITTER | Marker/window jitter sensitivity; sampler-phase jitter sensitivity | methodology artifact | candidate (C-023) | L1 methodology; blocker for phase/item claims | no phase/item joule claim without jitter/sampler-phase sensitivity bound | none-yet | P2-015 or claim gate | floor | analysis-plan-only | Quantifies reducer sensitivity to timestamp jitter and sampler phase offset. |
   103	| C-023-OUTPUT-IDENTITY | Output-token identity effects; binding gate for C5-2.5a/b/c/d | methodology artifact | candidate (C-023) | L1/L2 depending comparison | no quant/runtime/spec-decoding efficiency claim without equivalence or divergence report | none-yet | none | software | analysis-plan-only | Fixed output-token count is not fixed decoded work; binding for the PF/NS speculative-decoding riders admitted by D-075 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
   104	| C-023-IDLE-STATIONARITY | Idle-baseline stationarity | methodology artifact | candidate (C-023) | L1 methodology | no idle-subtracted conclusion without idle model-choice sensitivity | none-yet | P2-015 component | floor | analysis-plan-only | D-067 CLOSED the headline-basis question: gross energy within the named boundary is primary. This row stays alive only to test how idle-model choice affects conclusions in the labeled within-device SECONDARY view. |
   105	| C-023-QUALITY-EQUIV-QUANT | Quality-equivalent quantization comparisons; C5-2.11 gate | research question | candidate (C-023) | L2 after equivalence rule | no quantization efficiency or quality-neutrality claim without AP-level equivalence rule | none-yet | none | software | analysis-plan-only | C5-2.11's candidate PF on-device KV leg binds this gate; footprint savings alone do not establish energy or quality neutrality ([evaluation](process_traces/2026-07-17-extension-axes/)). |
   106	| C-023-COEFF-TRANSPORT | Coefficient transport synthetic-to-realistic; energy model portability across workload mixtures | research question | candidate (C-023) | L2/L3 depending holdout | no realistic-session prediction from synthetic grid without transport validation | none-yet | suite traces after Q4 | substrate | analysis-plan-only | Explicitly tests Q4 coefficient transport from synthetic grids to realistic app traces. |
   107	| APP-PROMPT-PROFILER | Prompt/template energy profiler | application idea | candidate | internal L1/L2 only | no prompt-quality claim | none-yet | none | software | analysis-plan-only | Product-facing use of prompt/template energy sensitivity. |
   108	| APP-BUNDLE-POWER-BUG | Attach-a-bundle power-bug repro | application idea | candidate | L0/L1 support workflow | no general bug diagnosis without reproduced bundle | none-yet | none | software | analysis-plan-only | Uses bundle completeness as a maintainer repro artifact. |
   109	| APP-CI-ENERGY-GATES | CI energy-regression gates | application idea | candidate | internal L1/L2 after floors | no CI failure threshold below detection floor | none-yet | P2-015 prerequisite | floor | analysis-plan-only | Needs floors, env snapshots, and baseline-refresh policy. |
   110	| APP-VENDOR-PRESS-AUDIT | Vendor/press claim audit | application idea | candidate | boundary-named L1/L2 | no absolute device-energy verdict without calibration | none-yet | none | hardware | analysis-plan-only | Can audit specific boundary/workload claims, not universal efficiency. |
   111	| APP-MODEL-CARDS | Practitioner energy model cards / leaderboard | application idea | candidate | internal only until L4 replication | no public leaderboard before cross-lab replication | none-yet | C5-3.5 prerequisite | coordination | analysis-plan-only | Internal table can exist; public version is killed until replication. |
   112	| APP-TEACHING-INSTRUMENT | Teaching instrument | application idea | candidate | pedagogical L0/L1 | no research generalization from teaching bundles | none-yet | none | software | analysis-plan-only | Uses bundles for methodology labs on boundaries, floors, and uncertainty. |
   113	| APP-STANDARDS-CONTRIBUTION | Bundle contract as standards contribution | application idea | candidate | methodology artifact proposal | no claim to be the standard | none-yet | none | coordination | analysis-plan-only | Exports the artifact format and validation discipline. |
   114	| APP-CARBON-LABELS | Carbon labels | application idea | killed | none | no carbon label without wall meter and grid assumptions | none-yet | none | hardware | no | Killed as product label; C5-2.9 is the surviving scenario question. |
   115	| APP-BATTERY-RUNTIME | Battery-runtime estimates without calibration | application idea | killed | none | no battery-runtime estimate without system-level calibration | none-yet | none | hardware | no | Explicitly deferred/killed by the application shortlist. |
   116	| APP-LOCAL-CLOUD-ROUTING | Local-vs-cloud routing product | application idea | killed | none | no routing product while cloud side is unmeasured | none-yet | none | hardware | no | Killed product form; scenario analysis remains C5-2.9. |
   117	
   118	## Attribution Limits
   119	
   120	The rows whose historical wording most invited over-attribution are:
   121	
   122	- `C5-1.1`: active-parameter energy scaling. The C-014 amendment caps
   123	  4-6-model designs at descriptive L2 pairwise contrasts unless the model set
   124	  grows enough for a predeclared one-covariate fit, and forbids fitting
   125	  active+total+KV covariates on 4-6 model points. The claims ladder also
   126	  prevents L1 active-parameter-scaling language; the capability map records
   127	  the current two-model observation as a non-claim.
   128	- `C5-1.8`: runtime energy attribution. The bank already says comparisons
   129	  where formats force different artifacts are stack-vs-stack comparisons.
   130	  The registry therefore forbids wording that energy "belongs to the runtime"
   131	  unless the artifact/runtime identity problem is actually controlled.
   132	
   133	This subsection is hygiene for claims indexing. It does not re-adjudicate the
   134	ratified C-014/C-015 bank decisions.

exec
/bin/zsh -lc "sed -n '1,75p' docs/research_question_registry.md; sed -n '76,160p' docs/research_question_registry.md; sed -n '190,240p' docs/strategy/2026-08-06-impressiveness-roadmap.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Research Question Registry

Purpose: this is the canonical live index for JouleWise research questions,
capability claims, application ideas, and methodology artifacts. It normalizes
aliases, status, claim ceilings, owners, gates, and pre-hardware readiness so
claims and campaign plans can point to one row. Promotion rules are unchanged
from `docs/research_question_bank.md`: promotion still requires a named RQ slot
in `PROJECT_STATUS.md`, a data plan that does not displace queue ranks above
it, and scope fit.

Maintenance rule: registry rows are LIVE state. The research question bank
remains the historical and deliberative record, including council wording,
kills, quarantines, and amendments. Single-writer split: update this registry
for current indexing and cross-references; update the bank only when recording
new deliberation history.

Column legend:

- `canonical_id`: stable row key for the live index.
- `aliases`: other IDs, names, or capability-map labels for the same question.
- `question_type`: one of `research question`, `capability claim`,
  `application idea`, or `methodology artifact`.
- `status`: `promoted`, `banked`, `candidate`, `killed`, `answered-L1`, or
  the review-specific `candidate (C-023)`.
- `claim_ceiling`: highest claim level currently allowed by the bank, review,
  or capability map, before future evidence upgrades.
- `forbidden_upgrade`: short reminder of language the row cannot support.
- `AP owner`: analysis-plan owner if already named; otherwise `none-yet`.
- `campaign owner`: queue row, phase, or campaign owner if already named.
- `gate_class`: dominant gate class: `hardware`, `software`, `floor`,
  `substrate`, or `coordination`.
- `pre_hardware_preparable`: `fully`, `analysis-plan-only`, or `no`.
- `one-line note`: indexing note, not a re-adjudication.

## Registry Table

| canonical_id | aliases | question_type | status | claim_ceiling | forbidden_upgrade | AP owner | campaign owner | gate_class | pre_hardware_preparable | one-line note |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | Split reduces energy | research question | promoted | L2 boundary-labeled; stronger only with calibration | no uncalibrated cross-boundary total-energy winner | none-yet | Phase 3 split; P1-004; P1-006 | hardware | fully | Central split question; total energy must be decomposed and boundary-labeled. |
| Q2 | Link bandwidth sensitivity | research question | promoted | L2 | no nominal-link crossover without measured links | none-yet | Phase 3 split; P1-004 | hardware | fully | Clean interconnect sensitivity question; link throughput and transfer energy must be measured. |
| Q3 | Split energy-latency Pareto | research question | promoted | L2 | no Pareto claim without frozen set and latency metric | none-yet | Phase 3 split | hardware | fully | Requires a fixed comparison set and latency metric per figure. |
| Q4 | Fixed-vs-marginal energy model; C5-2.14 cache-policy coefficient rider | research question | promoted | L3 | no holdout-prediction claim without AP-1 floor and residual checks | AP-1 | P2-019 q4_l3_shape_grid_v1 | floor | analysis-plan-only | Strongest predictive science row; includes compositional split-energy prediction only when transfer terms exist. C5-2.14 is a candidate rider capped at L2, earliest PF, with no coefficient-direction claim below P2-015 floors ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| Q5 | Ranking stability | research question | promoted | L2 | no uncalibrated cross-device winner; no ranking where gap below MDE | AP-3 | 2M; Window B grid | floor | analysis-plan-only | Promoted within-machine ranking question; workload-axis analogue C5-W.3 remains a separate candidate row. |
| Q6 | Boundary sensitivity; C5-2.10 boundary-directional bias quantification | research question | promoted | L2; L4 only with replication | no wall/rail conclusion flip claim without paired boundary plan | none-yet | P1-003 wall meter; F11 | hardware | fully | Registry indexes C5-2.10 as the C5 elaboration of promoted Q6. |
| RQ-METHOD-FLOOR | Detection floor; noise floor; short-difference resolvability; phase/item identifiability flags; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | banked | L1 methodology | no below-floor effect language except `not resolvable`; no module-energy fraction or regression-slope attribution | none-yet | P2-015 | floor | analysis-plan-only | Methodology centerpiece and prerequisite for most comparative claims; the candidate module-attribution nonclaim attaches here at earliest NS instead of becoming a row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.11 | Dark silicon; rail utilization; ANE-dark finding | research question | candidate | L2 structural | no true silicon-energy fraction from modeled rails | none-yet | P2-009 rich telemetry; C5-1.8 runtime grid | software | analysis-plan-only | Measures modeled-rail utilization structure, not physical absolute rail truth. |
| C5-1.3 | CPU:GPU phase division; rail/DVFS phase signatures; prefill/decode power asymmetry | research question | candidate | L2 structural | no short-phase joules when windows are under-resolved | none-yet | 2M with P2-009 | floor | analysis-plan-only | Merges the banked CPU:GPU phase question with C5-1.3 telemetry framing. |
| RQ-KV-GROWTH | KV-growth decode drift; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | banked | L1/L2 chunked | no per-token joule claims; no attention-vs-FFN fraction from context slopes | none-yet | none | floor | analysis-plan-only | Candidate riders, earliest PF: bounded-window KV marginal slope and named-artifact attention/context slope; both retain chunked-window/floor discipline and stay attached rather than becoming independent rows ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.5 | Cooldown recovery as thermal characterization; cooldown-recovery curves | research question | candidate | L1/L2 | no claim that power recovery proves thermal-state equality | none-yet | none | floor | analysis-plan-only | Turns cooldown tails and cap-hit rates into reportable methodology evidence. |
| C5-1.10 | Failure frontier | research question | candidate | L1/L2 descriptive | no silent discard of failures; no population claim from one memory class | none-yet | none | software | analysis-plan-only | Structured `unsupported`, fit, swap, throttle, and cap-hit outcomes become data. |
| C5-1.7 | Cold-start / keep-warm energy; reload-vs-resident scheduling | research question | banked | L2 after harness extension | no breakeven without load-window and resident-idle sampling | none-yet | none | software | analysis-plan-only | Review and bank both identify reload-vs-resident as the same question. |
| C5-1.9 | Energy-per-correct-answer vs difficulty; MoE-vs-dense controlled ladder | research question | banked | L2 after envelope and denominator guards | no intelligence-per-joule; no `difficulty causes energy` | AP-5 | P2-010a plus P2-010b plus later scored campaign | substrate | analysis-plan-only | Correctness remains quarantined annotation under the C-004/C-014 rules. |
| C5-2.5 | Speculative-decoding energy; C5-2.5b proposal-work rider; C5-2.5c break-even rider | research question | banked | L2 | no efficiency claim without output equivalence and accepted-token accounting | none-yet | none | software | analysis-plan-only | C5-2.5c is the primary PF Q4 rider, C5-2.5b its PF secondary, and C5-2.5d the mandatory PF contamination control; C5-2.5a remains a deferred NS bank rider. `C-023-OUTPUT-IDENTITY` binds all efficiency contrasts ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-POWER-MODE | Power-mode Pareto | research question | banked | L2 possible | no OS-mode conclusion until power mode is a first-class config field | none-yet | none | software | analysis-plan-only | Waits on config/environment capture for OS power modes. |
| RQ-INTELLIGENCE-PER-JOULE | General joules-per-solved-task; intelligence-per-joule | research question | killed | none | no general intelligence-per-joule ratio | none-yet | none | substrate | no | Killed/quarantined by C-003/C-004; controlled ladder is the surviving minimal form. |
| RQ-AUDITABLE-EVIDENCE | Can JouleWise produce auditable local-LLM energy evidence? | capability claim | answered-L1 | L0/L1 | no physical calibration claim from strict validation alone | none-yet | existing Mac/MLX/powermetrics bundles | software | no | Artifact contribution, not a research question. |
| RQ-QWEN25-SMOKE | Qwen2.5-1.5B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from smoke result | none-yet | 2026-07-06 2I | software | no | Legit instrument observation for one named stack/workload. |
| RQ-QWEN35-SMOKE | Qwen3.5-122B-A10B smoke consumption | capability claim | answered-L1 | L1 | no comparative scaling claim from n=3 | none-yet | 2026-07-07 flagship addendum | software | no | Legit instrument observation for one named stack/workload. |
| RQ-TWO-MODEL-ACTIVE-NONCLAIM | Did the two observed models demonstrate active-parameter scaling? | capability claim | answered-L1 | L1 hypothesis only | no active-parameter scaling claim | none-yet | 122B addendum; capability map | floor | no | Negative guard: two points are consistent with a hypothesis but do not support scaling. |
| RQ-SHORT-PREFILL-RESOLVABILITY | Are short prefill phase joules resolvable?; RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM | methodology artifact | answered-L1 | L1 `not resolvable` | no standalone short-prefill joule result; no relabeling request phases as module phases | none-yet | Phase 4 observation | floor | no | Existing cadence precedent owns the candidate module-attribution guard, earliest NS; no separate methodology row ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MLX-KV-REPLAY | Same-machine MLX KV replay token identity and size prediction; C5-2.13 | capability claim | answered-L1 | L1 feasibility | no cross-machine portability claim | none-yet | Stage 3.0.1 | software | no | The L1 feasibility result remains answered; candidate C5-2.13, earliest PF and capped at L2, attaches the same-machine energy-crossover rider without cross-stack generalization ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-MAC-BASELINES | Per-profile Mac baselines | capability claim | candidate | L1 per condition | no novelty or comparison claim without AP/floor | none-yet | 2M | floor | analysis-plan-only | Necessary baseline corpus, not a headline by itself. |
| RQ-SHAPE-ENERGY | Workload shape changes request energy | research question | candidate | L2 | no causal token-shape claim beyond AP-2 contrasts | AP-2 | 2M | floor | analysis-plan-only | Distinct from Q4 because it describes shape contrasts rather than holdout prediction. |
| C5-1.1 | Active-parameter energy scaling | research question | candidate | L2 pairwise only unless larger predeclared model set | no active+total+KV regression on 4-6 models | none-yet | P2-024 shortlist | floor | analysis-plan-only | C-014 caps the tempting wording; registry hygiene, not re-adjudication. |
| C5-1.2 | Context-length energy scaling; C5-2.12; RQ-AXI-ATTN-CONTEXT-SLOPE | research question | candidate | L2/L3 if modeled | no short-prompt phase point claims; no wall implication from SoC rails | none-yet | none | floor | analysis-plan-only | Natural local-inference question with chunked phase limits; the two candidate PF riders remain capped at L2 and forbid module attribution from context-associated slopes ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.4 | DVFS residency as throttling early-warning | research question | candidate | L2 if prediction rule fixed | no prediction claim without horizon and rule | none-yet | none | software | analysis-plan-only | Convert characterization to a predeclared warning rule before claiming prediction. |
| C5-1.6 | Sampling-strategy energy overhead | research question | candidate | L2 if above floor | no telemetry-perturbation claim from this row | none-yet | P2-024 shortlist | floor | analysis-plan-only | Bank row is greedy vs temperature/top-p/beam overhead, not sampler instrumentation cost. |
| C5-1.8 | Runtime energy attribution; same-silicon kernel-layer provenance rider | research question | candidate | L2 stack-vs-stack | no `belongs to runtime` or `belongs to kernel layer` language when artifacts/formats differ; no runtime-agnostic kernel claim | none-yet | P2-024 shortlist | floor | analysis-plan-only | Candidate NV provenance rider stays inside the stack-conditioned comparison; it does not mint C5-1.13 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-1.12 | Quantization benefit decomposition, Mac leg | research question | candidate | L2 | no quantization efficiency claim without output divergence reporting | none-yet | P2-024 shortlist | floor | analysis-plan-only | Splits benefit into lower watts vs shorter time on one stack/family. |
| C5-W.1 | Category beyond token counts; Token-Shape Sufficiency Null | research question | candidate | L2 | no category effect below floor or without shape control | AP-4 | jw_mixed_v1 after P2-010a | substrate | analysis-plan-only | Strong null-or-effect design for workload-category residuals. |
| C5-W.2 | Thinking-token inflation | research question | candidate | L2 | no cognition claim; attribute only to emitted-token/stop distributions | none-yet | jw_mixed_v1 natural-EOS pilot | substrate | analysis-plan-only | Operational-cost view for reasoning models under natural EOS. |
| C5-W.3 | Category energy-ranking stability; workload-axis Q5 analogue | research question | candidate | L2 | no category ranking claim where rank gap is below MDE or without workload-expansion gate | none-yet | jw_mixed_v1 workload expansion | substrate | analysis-plan-only | Workload-axis analogue of promoted Q5, not the same ratified question; asks whether code/long-context/reasoning categories flip model/quant ordering. |
| C5-I.3 | C5-W.4; FLORES tokenizer fertility tax | research question | candidate | L2 | no tokenizer efficiency ranking without semantic and token-matched legs | none-yet | FLORES after HumanEval smoke | substrate | fully | C5-I.3 and C5-W.4 are the same FLORES fertility question. |
| C5-I.1 | External benchmark energy signatures | research question | candidate | L2 | no benchmark capability or accuracy claim | none-yet | import/export contracts | substrate | fully | Needs matched shape/output policy before family-level energy signatures. |
| C5-I.2 | Published-difficulty strata vs energy | research question | candidate | L1 association; L2 only if preplanned repeated bundles | no `difficulty causes energy` | none-yet | import/export contracts | substrate | fully | Weak/secondary because source difficulty labels are heterogeneous. |
| C5-I.4 | Harness overhead floor | methodology artifact | candidate | L1/L2 | no item energy claim when harness overhead dominates unnoticed | none-yet | P2-022 shim | substrate | fully | Methodology question for marked external harnesses. |
| C5-I.5 | Prompt-template energy sensitivity | research question | candidate | L2 | no prompt-quality or capability claim | none-yet | import/export contracts | substrate | fully | Same external item, canonical vs JouleWise-rendered prompt format. |
| RQ-CONTENT-SENTINEL | Synthetic prompt content sentinel; fixed-shape content sensitivity | research question | candidate | L2 | no content-effect claim unless realized shape/stop policy stays matched and effect clears floor; no broad content-neutrality claim beyond the five tested AP-6 conditions | AP-6 | P2-020 content sentinel | substrate | analysis-plan-only | Tests whether synthetic prompt content matters at fixed shape under the AP-6 ids-native no-BOS sentinel design. |
| RQ-ENERGY-VARIANCE | Sampling-induced energy variance; energy-at-risk per prompt; lucky-short-reasoning variance | research question | candidate | L2 within boundary | no intelligence-per-joule or correctness-causal claim (C-004 quarantine); variance claims need repeated-bundle n sized for variance estimation and floor-gated residuals; per-bundle sampler seeds must be recorded | none-yet | none (post-floor; reasoning model on current Mac feasible) | floor | analysis-plan-only | Ed-added 2026-07-09 row: distribution (not just mean) of request energy for a fixed hard prompt under sampling; decomposable into reasoning-length vs residual variance via recorded output token IDs + deterministic replay of sampled paths (P2-025 capture + 3.0.1 replay make paths replayable). |
| RQ-SESSION-SHAPE | Session-shape energy | research question | candidate | L2/L3 depending holdout | no app-session prediction without holdout validation | none-yet | suite profiles after P2-010a | substrate | analysis-plan-only | Tests whether Q4 coefficients compose in realistic session ecology. |
| RQ-ORDER-POSITION | Order-position effects | methodology artifact | candidate | L2 | no category/thermal inference without executable order policy | none-yet | suite profiles after ordering executability | substrate | analysis-plan-only | Drift/order probe; not a headline result. |
| RQ-CACHE-PREFIX | Cache/prefix economics; C5-2.13 | research question | candidate | L2 | no bundled cache-state conclusion without exact cache policy; no crossover generalization beyond the measured prompt-length ladder | none-yet | none | software | analysis-plan-only | Covers prefix reuse, resident state, and prompt-cache warmth; candidate C5-2.13 attaches a same-machine/same-stack energy crossover at earliest PF ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-AXI-HYBRID-PAIR | Named hybrid (SSM/attention)-vs-pure-transformer pair | research question | candidate | L2 pair-specific characterization | no architecture-class efficiency generalization, causal SSM-mechanism attribution, or tokenizer-blind ranking from one named pair | none-yet | post-floors named-pair campaign | floor | analysis-plan-only | Earliest PF; floor-gated and bindingly worded as “this named pair”; controlled-pair availability remains NEEDS-WEB ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| RQ-EXTERNAL-MARKED-RUNNER | External marked-runner energy layer | capability claim | candidate | L1/L2 with AP row | no accuracy, leaderboard, pass@k, or capability interpretation | none-yet | P2-022 | substrate | fully | Export-layer feasibility becomes research only when overhead/energy comparisons are specified. |
| RQ-HUMANEVAL-IMPORT-SMOKE | HumanEval import smoke | capability claim | candidate | L0/L1 | no coding-capability, pass@k, or accuracy claim | none-yet | P2-023 | substrate | no | Plumbing smoke for frozen external subset provenance. |
| C5-2.1 | Quantization decomposition, cross-stack | research question | candidate | L2 | no cross-boundary quant winner without calibration | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Extends C5-1.12 to CUDA/GGUF legs. |
| C5-2.2 | Batch size and prefill/decode energy split | research question | candidate | L2 | no serving conclusion without latency-bound policy | none-yet | P1-006 CUDA/3050 manifests | hardware | fully | Strong systems question for serving-style hardware and batching backend. |
| C5-2.3 | Predicted-vs-measured KV economics | research question | candidate | L2 | no KV economics claim without measured payload/link/deserialization terms | none-yet | P1-004 plus P1-006 | hardware | fully | One of the strongest Phase 3 questions; useful even if live split fails. |
| C5-2.4 | KV-cache quantization end-to-end; C5-2.11 on-device MLX leg | research question | candidate | L2 | no byte-saving equals energy-saving claim | none-yet | none | software | analysis-plan-only | Transfer leg still depends on cache portability; candidate C5-2.11 is the PF on-device MLX-scoped leg and also binds output-equivalence evidence ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.11 | On-device quantized-KV energy | research question | candidate | L2, per-boundary, MLX-scoped | no byte-saving-equals-energy-saving claim; no cross-runtime generalization from MLX alone; no quality-neutrality claim without C-023-style output-equivalence evidence | none-yet | post-floors Mac cache-policy campaign | floor | analysis-plan-only | Earliest PF; indexed under C5-2.4/C5-1.12/C-023-QUALITY-EQUIV-QUANT and runnable without the transfer leg ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.6 | Request coalescing under latency bound | research question | candidate | L2 | no scheduler optimum without arrival trace and latency policy | none-yet | none | hardware | analysis-plan-only | Useful but drifts toward scheduler research. |
| C5-2.7 | Device perf/W rankings with runtime held constant; kernel-provenance rider | research question | candidate | L2 within boundary; L4 with second unit/calibration | no generic hardware or cross-vendor kernel-API ranking from heterogeneous boundaries | none-yet | P1-006; 3080 Ti borrow window | hardware | fully | Candidate NV rider records attention-kernel/BLAS/graph provenance and remains per-boundary at L2; NEEDS-WEB feasibility stays open ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-2.8 | Placement-policy optimality from Q4 coefficients | research question | candidate | L2/L3 | no optimal-placement claim without measured split validation cells | none-yet | Phase 3 full set | hardware | fully | Uses Q4 coefficients plus measured transfer costs to choose placement. |
| C5-2.9 | Local-vs-datacenter crossover economics | research question | candidate | scenario result only | no measured-equivalent cloud comparison | none-yet | P1-003 plus P1-004 | hardware | analysis-plan-only | Surviving scenario form of the carbon-label kill. |
| C5-3.1 | Machine-to-machine variance; generalizability floor | research question | candidate | L4 enabler | no population claim from one unit | none-yet | second M-series unit | hardware | fully | Cheapest route from stack-specific to replication-aware claims. |
| C5-3.2 | Battery-path energy and modeled-rail validation | research question | candidate | L2/L4 bridge | no full-system claim from modeled rails alone | none-yet | USB-C PD analyzer | hardware | fully | Complements AC wall meter with a second physical boundary. |
| C5-3.3 | Cross-ISA NPU/SoC comparison; backend-provenance rider | research question | candidate | L4 only after replication | no broad cross-ISA claim before platform-specific adapter study; no NVIDIA-vs-AMD efficiency claim from single units or heterogeneous boundaries | none-yet | new platform adapters | hardware | analysis-plan-only | Candidate PC provenance rider is capped at L1 and records backend identity now; it creates no AMD science commitment ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C5-3.4 | Phone-class edge inference | capability claim | candidate | L0/L1 first | no promised phone science before telemetry feasibility | none-yet | phone feasibility | hardware | no | Feasibility verdict may be the result. |
| C5-3.5 | Cross-lab replication | methodology artifact | candidate | L4 enabler | no public benchmark credibility claim without replication | none-yet | external lab coordination | coordination | fully | Coordination-gated credibility layer. |
| C-023-TELEMETRY-PERTURBATION | Telemetry perturbation cost | methodology artifact | candidate (C-023) | L1/L2 floor component | no near-floor claim without telemetry-on/off ABBA check | none-yet | P2-015 component | floor | analysis-plan-only | New coverage-gap row; distinct from C5-1.6 sampling-strategy overhead. |
| C-023-VERSION-DRIFT | OS/runtime version-drift forensics; OS/driver/runtime update forensics | research question | candidate (C-023) | L1/L2 stack-conditioned | no version regression claim without before/after pinned bundles | none-yet | none | software | analysis-plan-only | Turns version churn into a named science/application row. |
| C-023-MARKER-JITTER | Marker/window jitter sensitivity; sampler-phase jitter sensitivity | methodology artifact | candidate (C-023) | L1 methodology; blocker for phase/item claims | no phase/item joule claim without jitter/sampler-phase sensitivity bound | none-yet | P2-015 or claim gate | floor | analysis-plan-only | Quantifies reducer sensitivity to timestamp jitter and sampler phase offset. |
| C-023-OUTPUT-IDENTITY | Output-token identity effects; binding gate for C5-2.5a/b/c/d | methodology artifact | candidate (C-023) | L1/L2 depending comparison | no quant/runtime/spec-decoding efficiency claim without equivalence or divergence report | none-yet | none | software | analysis-plan-only | Fixed output-token count is not fixed decoded work; binding for the PF/NS speculative-decoding riders admitted by D-075 ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-IDLE-STATIONARITY | Idle-baseline stationarity | methodology artifact | candidate (C-023) | L1 methodology | no idle-subtracted conclusion without idle model-choice sensitivity | none-yet | P2-015 component | floor | analysis-plan-only | D-067 CLOSED the headline-basis question: gross energy within the named boundary is primary. This row stays alive only to test how idle-model choice affects conclusions in the labeled within-device SECONDARY view. |
| C-023-QUALITY-EQUIV-QUANT | Quality-equivalent quantization comparisons; C5-2.11 gate | research question | candidate (C-023) | L2 after equivalence rule | no quantization efficiency or quality-neutrality claim without AP-level equivalence rule | none-yet | none | software | analysis-plan-only | C5-2.11's candidate PF on-device KV leg binds this gate; footprint savings alone do not establish energy or quality neutrality ([evaluation](process_traces/2026-07-17-extension-axes/)). |
| C-023-COEFF-TRANSPORT | Coefficient transport synthetic-to-realistic; energy model portability across workload mixtures | research question | candidate (C-023) | L2/L3 depending holdout | no realistic-session prediction from synthetic grid without transport validation | none-yet | suite traces after Q4 | substrate | analysis-plan-only | Explicitly tests Q4 coefficient transport from synthetic grids to realistic app traces. |
| APP-PROMPT-PROFILER | Prompt/template energy profiler | application idea | candidate | internal L1/L2 only | no prompt-quality claim | none-yet | none | software | analysis-plan-only | Product-facing use of prompt/template energy sensitivity. |
| APP-BUNDLE-POWER-BUG | Attach-a-bundle power-bug repro | application idea | candidate | L0/L1 support workflow | no general bug diagnosis without reproduced bundle | none-yet | none | software | analysis-plan-only | Uses bundle completeness as a maintainer repro artifact. |
| APP-CI-ENERGY-GATES | CI energy-regression gates | application idea | candidate | internal L1/L2 after floors | no CI failure threshold below detection floor | none-yet | P2-015 prerequisite | floor | analysis-plan-only | Needs floors, env snapshots, and baseline-refresh policy. |
| APP-VENDOR-PRESS-AUDIT | Vendor/press claim audit | application idea | candidate | boundary-named L1/L2 | no absolute device-energy verdict without calibration | none-yet | none | hardware | analysis-plan-only | Can audit specific boundary/workload claims, not universal efficiency. |
| APP-MODEL-CARDS | Practitioner energy model cards / leaderboard | application idea | candidate | internal only until L4 replication | no public leaderboard before cross-lab replication | none-yet | C5-3.5 prerequisite | coordination | analysis-plan-only | Internal table can exist; public version is killed until replication. |
| APP-TEACHING-INSTRUMENT | Teaching instrument | application idea | candidate | pedagogical L0/L1 | no research generalization from teaching bundles | none-yet | none | software | analysis-plan-only | Uses bundles for methodology labs on boundaries, floors, and uncertainty. |
| APP-STANDARDS-CONTRIBUTION | Bundle contract as standards contribution | application idea | candidate | methodology artifact proposal | no claim to be the standard | none-yet | none | coordination | analysis-plan-only | Exports the artifact format and validation discipline. |
| APP-CARBON-LABELS | Carbon labels | application idea | killed | none | no carbon label without wall meter and grid assumptions | none-yet | none | hardware | no | Killed as product label; C5-2.9 is the surviving scenario question. |
| APP-BATTERY-RUNTIME | Battery-runtime estimates without calibration | application idea | killed | none | no battery-runtime estimate without system-level calibration | none-yet | none | hardware | no | Explicitly deferred/killed by the application shortlist. |
| APP-LOCAL-CLOUD-ROUTING | Local-vs-cloud routing product | application idea | killed | none | no routing product while cloud side is unmeasured | none-yet | none | hardware | no | Killed product form; scenario analysis remains C5-2.9. |

## Attribution Limits

The rows whose historical wording most invited over-attribution are:

- `C5-1.1`: active-parameter energy scaling. The C-014 amendment caps
  4-6-model designs at descriptive L2 pairwise contrasts unless the model set
  grows enough for a predeclared one-covariate fit, and forbids fitting
  active+total+KV covariates on 4-6 model points. The claims ladder also
  prevents L1 active-parameter-scaling language; the capability map records
  the current two-model observation as a non-claim.
- `C5-1.8`: runtime energy attribution. The bank already says comparisons
  where formats force different artifacts are stack-vs-stack comparisons.
  The registry therefore forbids wording that energy "belongs to the runtime"
  unless the artifact/runtime identity problem is actually controlled.

This subsection is hygiene for claims indexing. It does not re-adjudicate the
ratified C-014/C-015 bank decisions.

The strongest realistic paper is therefore: **C1–C8 metrology + the already-collected 1.5B/7B demonstration + one designed extension + an independently usable artifact.** That is more coherent and defensible than a larger model/device matrix or an unfinished split system.

### F3 — Five decisions Ed/advisor must make

1. **Venue and publication sequence.** Choose CSCSU-only, workshop-first, or ICPE-full ambition, and verify whether a workshop publication may later be extended for ICPE. Build a 10-page master manuscript even if the first submission is shorter.

2. **Physical measurement budget.** Recommended commitment: **5–7 Ed-present sessions**—C, D, one contingency/stability repeat, wall pilot/confirmation, and one extension. An ICPE-full attempt with Q4 and second-unit work likely needs **8–10 total sessions** across operators.

3. **Meter execution.** D-092 has already answered “yes.” The remaining decision is: borrow versus buy, approximately $3,000-class budget, calibration/fixture responsibility, and a cutoff date after which C8 is cleanly removed.

4. **Mechanism ambition.** Do not ask simply “unfence D-041.” Decide whether to retain D-070’s all-five-axis commitment or narrow it to one paper-worthy study. Recommended rule: two-to-three-week feasibility gate for speculative-decode observability; if it fails, return immediately to Q4/quantization.

5. **External hardware priority.** Decide whether scarce coordination goes to a second Apple unit, the 3080 Ti split study, or Jetsons. Recommendation: second-unit replication first, 3080 Ti second, Jetsons last.

### F4 — Draft-state correction

The methods draft was inspected from `impl/paper-draft-v1` at commit `af0b7195`; it is one commit ahead of and one commit behind `main`. It already reflects the right rigor: result placeholders remain pending remint, all characterization rows are pending Window C, and the split section is framed as future demonstration work. It should be integrated deliberately so the paper itself becomes the continuously updated claim-state surface.

## Residual risk

- The mechanism-literature sweep is explicitly desk research, not governed project evidence. Any “first measured” novelty claim needs a fresh literature search immediately before submission.
- Venue formats and deadlines cited above are current published 2026 rules or incomplete 2027 pages; 2027 calls may change.
- Measurement-night estimates are planning ranges, not validated campaign runtimes.
- Wall validation cannot establish phase attribution, and one external meter does not create cross-device generality.
- Even an excellent single-Mac study remains stack-specific under the claims ladder unless second-unit or cross-lab replication lands.
exec
/bin/zsh -lc "sed -n '1,220p' docs/research_question_bank.md; sed -n '221,440p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Research Question Bank

Candidate research questions the instrument can answer, beyond the named
set in `PROJECT_STATUS.md`. Populated from council sessions C-003/C-004
(2026-07-07; see `docs/council_log.md` for positions and votes). Promotion
out of the bank requires: a named RQ slot in `PROJECT_STATUS.md`, a data
plan that does not displace queue ranks above it, and (post P1-001) scope
fit. Killed ideas stay recorded with their cause of death.

Canonical live index: `docs/research_question_registry.md`. The registry is
the current index for aliases, status, claim ceilings, owners, and gates; this
bank remains the historical and deliberative record.

## Promoted 2026-07-07 (now Q4-Q6 in PROJECT_STATUS)

- **Q4 Fixed-vs-marginal energy model** — fit
  `E = fixed + prefill(prompt_tokens) + decode(output_tokens)` per
  target/model/quantization; predicts which workloads flatter which
  devices and enables compositional split-energy prediction (predict
  split-run energy from monolithic coefficients + transfer measurements,
  validate on a subset) — the method that makes Q1 answerable at scale.
  Subsumes the prefill-scaling-exponent question. L3 wording requires AP-1
  in `docs/contracts/analysis_plans.md` (2026-07-08, C-014).
- **Q5 Ranking stability** — do within-machine rankings survive workload
  changes (prompt/output/quantization regimes), or where do they flip?
  Cross-device extension is hardware-gated. Uses the 2M matrix directly
  as a substrate; rank wording follows AP-3 in
  `docs/contracts/analysis_plans.md` (2026-07-08, C-014).
- **Q6 Boundary sensitivity** — do conclusions change when measured at
  platform rails vs AC wall power? (Gated on the wall meter, P1-003/R-007;
  reframes calibration as a research result.)

## Methodology centerpiece (deliberately NOT a numbered RQ — C-003 vote)

- **Detection floor / noise floor**: the smallest idle-subtracted energy
  difference each target/telemetry backend can honestly resolve. Observed
  motivation: idle baseline stddev (5.4 W) exceeded its mean (3.5 W) in
  the first real capture. Pairs with the reducer feature all council
  members converged on: **phase/item identifiability flags** (windows with
  fewer than N samples report a flag, not a bare joule value).

## Banked (viable, not yet promoted)

- **Dark silicon / rail utilization**: what fraction of a SoC's rails does
  a runtime energize? (Measured: ANE at 0.0 W through 512 tokens of MLX
  decode — the most quotable standalone finding to date.)
- **CPU:GPU energy division by phase**: does the rail mix shift between
  compute-bound prefill and memory-bound decode? Upstream of split
  economics.
- **KV-growth decode drift**: does per-token energy rise with sequence
  position? Valid only in CHUNKED form — token cadence (~4 ms) far
  outruns the power sampler (~113 ms); no per-token joule claims.
- **Cooldown recovery as thermal characterization**: recovery time vs
  preceding run intensity; cap-hit rates (observed: one 305 s cap-hit vs a
  117 s recovery in the first flagship experiment).
- **Failure frontier**: structured `unsupported` bundles as data — which
  model/quant/context combinations fit, fail, or throttle. Competitors
  discard their failures.
- **Cold-start / keep-warm energy**: model-load joules and the reload-vs-
  resident breakeven. Needs sampling outside the current measured window
  (harness extension).
- **Energy-per-correct-answer vs difficulty** (C-004): instrumented by the
  `affine_mod_ladder_v1` scored workload profile (see below). Claim shape
  pinned by the council: "energy per correct answer rises as accuracy
  falls under a controlled per-attempt energy envelope" — difficulty is
  DESIGNED to hold token budget approximately constant, and observed
  token/stop-reason distributions must be reported to verify residual
  EOS/output-length effects are negligible (wrong-answers-terminate-early
  would bias the curve's magnitude). NOT "difficulty causes energy."
  Amendment 2026-07-08 (C-014): before any scored campaign, an
  envelope-validation smoke gate must show level-invariant emitted-token
  and stop-reason distributions; energy/correct also requires the binomial
  guard in AP-5 (`docs/contracts/analysis_plans.md`). The full 64-level
  scored campaign is deferred until C5-1.9 has a claims-index/figure
  consumer.
- **Speculative-decoding energy**: joules per accepted token with/without
  a draft model. Needs runtime support + quality-equivalence controls.
- **Power-mode Pareto**: energy-latency tradeoff across OS power modes;
  wait until power mode is a first-class config/environment field.
- **Deferred (C-003/C-004 unanimous): general joules-per-solved-task /
  intelligence-per-joule** — drags in accuracy-evaluation policy before
  the measurement dataset matures, and sits in Intelligence per Watt's
  lane where JouleWise is least differentiated. The quarantined ladder
  profile above is the minimal version that survives.

## Instrument expansions adopted by C-004 (queue P2-009 / P2-010)

- **P2-009 rich telemetry (land FIRST — zero capture cost):** parse the
  already-captured-but-discarded plist fields — per-cluster E/P-core DVFS
  residency histograms, per-core frequencies/idle/parking, GPU
  freq/dvfm_states/idle_ratio/sw-requested-vs-achieved state, vendor
  combined_power as a cross-check — plus per-bundle environment snapshots
  (battery/charger state, Low Power Mode, memory pressure, load, display
  state; all sudo-free). Evidence this matters: decode pins the GPU at
  1380 MHz / idle_ratio 0.0 / ~22 W, and the contaminated idle window was
  mechanically visible in `gpu.idle_ratio` (first half at 13 W / 1363 MHz
  before true idle) — parsing it turns our contamination anecdote into an
  automated idle-quality gate. Opt-in `rich_telemetry` tier later: the
  `tasks` sampler (per-process attribution — the direct answer to
  background contamination), disk/network samplers.
- **P2-010 scored workload suite v1:** `affine_mod_ladder_v1` per the
  C-004 design (seed-deterministic SHA-256-derived modular recurrences;
  difficulty = iteration count with prompt shape and answer length fixed;
  exact-integer scoring; levels `{1, 2, 4, 8, 16, 32, 64}`, 16 items/level;
  suite-per-bundle with item/level marker events; level-window energy
  primary; per-item flagged unidentifiable below minimum samples;
  correctness lives in stdlib `joulewise/workloads.py`, scored by the
  reducer so summaries stay re-reducible). Quarantine rules (C-004):
  one optional workload profile, correctness as annotation, no
  "difficulty causes energy" claims. Amendment 2026-07-08 (C-014):
  P2-010 splits into P2-010a suite substrate and P2-010b smoke ladder;
  the full scored ladder remains deferred as above.
  Amendment 2026-07-08 (D-047.1): the level set is the ratified
  powers-of-two set above, not a linear 1..64 sweep.

# Suite architecture v2, benchmark interop, and capability map (Council C-015, 2026-07-08)

## Suite mechanism

C-015 adopts one suite mechanism for benchmark breadth: a suite CAMPAIGN is
`B` whole-suite bundles x `k` distinct items; each suite bundle executes
its `k` items once (`r_within = 1`).
Replication is the count of whole-suite bundles (`B >= 5`, top-up to
`B = 10` near the floor). Item windows inside one bundle are breadth and
attribution evidence, not independent `n` (D-038/AP rules).

Within-bundle repeats are reserved for sentinel items. They estimate
order/cache/thermal effects and same-session repeatability; they never
inflate `n` (C-015). There are no per-item micro-cooldowns by default:
back-to-back execution is a named session ecology, not a flaw. Order
rotates round-robin or Latin-square across bundles, with `item_index`,
`block_index`, `position`, `prev_item`, `prefix_group`, and `order_seed`
recorded (C-015).

Split a suite into balanced blocks when measured wall time exceeds roughly
10-15 minutes or when drift sentinels / floor identifiability degrade.
The first default is `k = 24`; mature panels may use `k = 48` only after
Window A floors and drift checks are clean (C-015). Throughput arithmetic:
`suite_items_per_hour = 3600 * k / (load + idle + cooldown + k * item_runtime)`,
which buys roughly 3-15x item coverage versus one-item bundles, while
`B` remains the `n` and items remain breadth (C-015).

Architectural line: after P2-010a, no workload expansion gets bespoke
marker/window plumbing. New benchmarks are manifests plus generators.
`affine_mod_ladder_v1`, `jw_mixed_v1`, `q4_l3_shape_grid_v1`, the content
sentinel, and benchmark imports are all profiles of the same suite
manifest, marker, and window mechanism (C-015).

## Minimal substrate scope

P2-010a is capped to the minimal generic substrate (C-015): suite/item/block/level
markers, `BundleReader.item_windows()`, source/category/output-policy
fields, per-item token/stop/response hashes, order/cache metadata, manifest
validation, and the per-item validity/status model below. Future
`docs/contracts/run_bundle_layout.md` fields for suite/item/block/level
markers and per-item outputs land with implementation, not in this docs batch
(C-015).

P2-010a status enum:

- `succeeded`
- `malformed`
- `capped`
- `runtime_failed`
- `below_floor`
- `excluded_from_claim`

Aggregation rules (C-015): a block or suite remains claim-usable when the
predeclared aggregation level has enough `succeeded` item windows, paired
markers validate, strict bundle validation passes, and failed/excluded
items are reported rather than silently dropped. `below_floor` items may
contribute only to block/suite-level windows, not item-level joule claims.
`malformed`, `capped`, and `runtime_failed` items remain provenance and
failure-frontier evidence but do not enter numeric claim denominators
unless an AP row predeclares that status as part of the endpoint.
`excluded_from_claim` is an explicit analysis decision with a reason and
does not make the surrounding strict-valid bundle unusable by itself.

Deferred from P2-010a (C-015): scorers, import-specific fields, and rich
difficulty machinery until suite profiles need them.

## `suite_manifest` field sketch

Trimmed P2-010a substrate scope (C-015):

```yaml
schema_version
suite_id
suite_profile
suite_revision
suite_seed
generator:
  name
  version
  parameters_hash
analysis_contract:
  independent_unit
  primary_window_class
  allowed_aggregation_levels
execution_policy:
  order_policy
  within_bundle_repeats
  cooldown_policy
  cache_policy
  warmup_policy
  default_output_policy
source_manifest:
  source_id
  source_kind
  revision
  subset_id
  subset_sha256
  license
  contamination_note
items:
  - item_id
    item_type
    category
    difficulty:
      axis
      value
      scale
      label
      source
      quarantine_note
    shape:
      planned_prompt_tokens
      planned_output_tokens
      prompt_level
      decode_level
    source:
      source_item_id
      source_sha256
      prompt_template_id
      license
      contamination_note
    grouping:
      condition_id
      block_id
      level_id
      prefix_group_id
    output_policy
    status_policy
    tags
markers:
  suite_start_event
  suite_end_event
  block_start_event
  block_end_event
  level_start_event
  level_end_event
  item_start_event
  item_end_event
outputs:
  per_item_response_hash
  per_item_token_count
  per_item_stop_reason
  per_item_status
```

Amendments 2026-07-08 (D-044/D-045/D-046): the sketch is historical and
receives these additive pins. `outputs` gains `per_item_response_text`,
with response text carried in `outputs/suite_items.jsonl` (D-045.8).
`markers` and `outputs` are optional in authored manifests, materialized
to pinned defaults, validated when present, and included in the canonical
effective-manifest hash (D-044/D-045.3). Items gain an additive,
mutually-exclusive `prompt_token_ids` source for ids-native sentinels,
with per-item prompt identity using the D-033 token-ID hash
(D-045.5/D-046).

Deferred fields (C-015): `scoring.scorer_id`,
`scoring.expected_answer_hash`, `scoring.correctness_quarantine`, import-
specific source fields, and richer grouping/difficulty structures such as
`pair_id` and `holdout_role` until a profile and AP row need them.
AP-5's smoke-ladder acceptance already requires level-window energy, so
the deferral condition is met at birth (verification catch, C-015).

## Difficulty metadata rule

Difficulty is first-class quarantined item metadata (C-015):
`{axis, value, scale, label, source}`. Shape is not difficulty:
`q4_l3_shape_grid_v1` prompt/decode cells stay under `shape`, not
`difficulty`. Difficulty metadata enables stratified analysis and envelope
checks; it never licenses "difficulty causes energy" or
intelligence-per-joule wording, and the C-004 quarantine composes.

## Benchmark import

`benchmark_import` is a thin source-to-suite manifest that composes with
the C-005 frozen-subset discipline: hash-manifested subsets, never
"latest split" (C-015). Field sketch:

```text
schema_version
manifest_id
suite_profile
source_benchmark:
  source_id
  name
  upstream_url
  citation
  license_id
  license_text_sha256
  redistribution_policy
  revision_or_commit
  retrieval_date
  source_archive_sha256
  source_split
contamination:
  note
  known_public_benchmark
  intended_use
  prohibited_claims
subset:
  selection_rule
  selection_rule_sha256
  selector_version
  selected_item_ids
  selected_item_ids_sha256
  canonical_subset_json_sha256
prompt_mapping:
  prompt_template_id
  prompt_template_sha256
  source_fields_used
  render_policy
  rendered_prompt_sha256_policy
  output_policy
expected_answer:
  source_field
  stored_as
  expected_answer_sha256
  quarantine: true
  scorer_allowed: false
items:
  suite_item_id
  source_item_id
  source_row_sha256
  source_position
  type_label
  difficulty_label
  difficulty_source
  category
  level
  prompt_template_id
  expected_answer_sha256
  license_override
  contamination_override
  shape_hints
  tags
```

First target: HumanEval as a plumbing smoke import, not a difficulty or
accuracy paper (C-015). Rationale: MIT license, small recognizable corpus,
contamination is explicit and quarantined, 256/512-token code completions
clear the observed ~9 Hz item-window floor more plausibly than one-letter
answers, and `difficulty_label = none/source_not_provided` is acceptable
for a plumbing smoke. MMLU and tinyBenchmarks are rejected as first import
targets because they drag the project toward short-answer score estimation
or benchmark-score estimation. FLORES is the second import target for
tokenizer/multilingual science (C5-W.4/C5-I.3), not the first plumbing
target (C-015).

Claims unlocked by imports (C-015): L0 "JouleWise can freeze and execute an
external benchmark subset as suite items with auditable provenance"; L1
"on a named stack/boundary/output policy, external-shaped items produced
observed item/subset energy and token/stop distributions"; L2 only after an
AP row and repeated strict-valid bundles. Never claim accuracy, pass@k,
capability, benchmark-score standing, or intelligence per joule from this
layer (C-015/C-004).

## Export / energy layer

C-015 adopts a marker-emitting shim for export. The external harness owns
prompts, generation semantics, accuracy artifacts, and metric artifacts.
JouleWise owns power capture, bundle assembly, marker validation, and
energy reduction. The full contract lives in
`docs/contracts/adapter_contracts.md`.

P2-022 is a verdict-shaped feasibility spike (C-015) with verdicts:

- `external_markers_supported`
- `partial(<limitation>)`
- `external_markers_unsupported`

(contract home: docs/contracts/adapter_contracts.md)

P2-022 inherits D-035 subprocess isolation and D-036 computed-verdict
discipline. Its scope is pinned to energy-layer feasibility only (C-015):
3+ marked items, external result artifact hashed, strict bundle valid, no
accuracy interpretation, no leaderboard join, no pass@k-energy ratio, and
no general adapter framework. Any L2 energy comparison from the shim needs
strict bundles, repeated runs, same or calibrated boundary, and an AP row
(C-015).

## Kill / defer

Kill or defer:

- leaderboard integration.
- live dataset fetching.
- "latest split" support.
- JouleWise accuracy scoring beyond quarantined annotation.
- external judge calls, retries, pass@k, or benchmark-score normalization.
- full adapter per harness as the first export path.
- generation-callable wrapper as the first export path.
- MMLU/tinyBenchmarks as first import.
- public energy model-card leaderboard before cross-lab replication.
- per-item uncertainty treated as independent replication.
- any intelligence-per-joule ratio.

## New questions

Interop questions adopted by C-015:

- **C5-I.1 External benchmark energy signatures:** Do imported benchmark
  families have distinguishable energy profiles after matching token shape
  and output policy? Ceiling L2, no capability claim.
- **C5-I.2 Published-difficulty strata vs energy:** Do source-provided
  difficulty or published accuracy strata correlate with energy/stop
  behavior? Ceiling L1 association unless preplanned repeated-bundle L2;
  never "difficulty causes energy."
- **C5-I.3 FLORES tokenizer fertility tax:** For semantic-matched vs
  token-matched FLORES items, how much energy follows tokenizer fertility
  by script/language? Ceiling L2.
- **C5-I.4 Harness overhead floor:** For external harnesses, when does
  harness/process overhead dominate item energy? Ceiling L1/L2
  measurement-method result.
- **C5-I.5 Prompt-template energy sensitivity:** For the same external
  item, how much does canonical vs JouleWise-rendered prompt format change
  energy? Ceiling L2.

Architecture-unlocked candidates, recorded post-2O/post-floor and not
promised campaign work (C-015):

- **Session-shape energy:** does a realistic mixed session cost what
  fixed+prompt+decode coefficients predict, or is there a session overhead
  term?
- **Order-position effects:** how much does energy drift by item position
  after controlling for shape and category?
- **Cache/prefix economics:** what is the joule benefit of prefix reuse,

exec
/bin/zsh -lc "sed -n '441,660p' docs/research_question_bank.md; sed -n '661,880p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
  resident model state, or prompt-cache warmth versus cold independent
  requests?
- **Reload-vs-resident scheduling:** at what item/session length does
  suite-style batching dominate one-request bundles in total energy and
  wall time?

## Capability map by claim ceiling

### Today

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Can JouleWise produce auditable local-LLM energy evidence? | L0/L1 | "The harness can execute `<target/runtime/telemetry>` and preserve config, metadata, events, raw power trace, raw telemetry, outputs, and reducer summary in a strict-valid run bundle." | Existing Mac/MLX/powermetrics bundles; strict bundle layout. | Strict validation proves re-derivation of recorded evidence, not independent hardware rerun. |
| What did Qwen2.5-1.5B consume on the M3 Max for the 512-output-token smoke workload? | L1 | "On `M3 Max / MLX / powermetrics SoC rails`, under `<workload/output policy>`, Qwen2.5-1.5B-4bit observed `<mean gross J>` request energy, `<TTFT>`, and `<throughput>` across 3 strict-valid bundles." | 2026-07-06 2I: about 47 J gross, about 94 ms TTFT, about 257 tok/s, gross CV 1.4%. | Idle-subtracted result is contaminated in rep 1; use gross for the cleanest current instrument result. |
| What did Qwen3.5-122B-A10B consume on the same workload? | L1 | "On `M3 Max / MLX / powermetrics SoC rails`, under the same 512-output-token workload, Qwen3.5-122B-A10B-4bit observed `<mean gross J>` request energy, `<TTFT>`, and `<throughput>` across 3 strict-valid bundles." | 2026-07-07: about 304 J gross, about 270 ms TTFT, about 46 tok/s, gross CV 0.3%. | L1 only; n=3 is below comparative protocol. |
| Did the two observed models demonstrate active-parameter scaling? | No; L1 hypothesis only | "The two observed Mac/MLX/powermetrics points are consistent with a fixed/marginal decode-time hypothesis, but they do not support an active-parameter scaling claim." | 122B addendum and claims-ladder downgrade. | Model size, architecture, quantization, and runtime details are confounded. |
| Are short prefill phase joules resolvable at current powermetrics cadence? | L1 "not resolvable" | "On `M3 Max / MLX / powermetrics`, short-prefill phase energy for `<~94 ms window>` is not resolvable at the observed sampling cadence and must not be reported as a standalone joule result." | Observed about 8.8-8.9 Hz; Phase 4 says about 94 ms prefill has fewer than one sample. | Sampler cadence remains near current observed rate. |
| Can same-machine MLX KV replay preserve token identity and size prediction? | L1 feasibility result | "On this M3 Max / mlx-lm stack, prompt-cache replay was supported for `<prompt length>`: resumed greedy decode matched monolithic tokens and measured cache size was within `<delta>` of the KV-size prediction." | Stage 3.0.1: 1024/2048 prompt cache, 64/64 tokens identical, +0.018%/+0.009% size delta. | Same machine/same venv only; not cross-machine portability. |

### After Window A

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| What is the detection floor per metric/window? | L1 methodology result | "For `<target/backend/metric/window class>`, differences below `<floor>` J are not resolvable; supported comparisons use `max(floor_abs_j, floor_cmp_j)`." | P2-015 calibration. | Calibration machine state is representative of later quiet campaigns. |
| What are per-profile Mac baselines? | L1 per condition | "On `M3 Max / MLX / powermetrics`, `<model>` under `<profile>` observed `<energy_request_j>`, `<gross J>`, `<mJ/output-token>`, `<TTFT>`, and `<throughput>` with 95% t-intervals over n=5." | 2M: `short_short`, `long_short`, `short_long`, `mid_mid`. | Output-token denominator and output policy must be runtime-observed/pinned. |
| Does workload shape change request energy on one stack? | L2 | "Within `M3 Max / MLX / powermetrics`, `<profile A>` differed from `<profile B>` for `<model>` by `<effect>` on `<metric/window>`, with n=5 per condition, CIs, manifest order, and effect above floor." | 2M + AP-2. | Drift sentinels and block-position metadata LANDED 2026-07-08 (PR #15). |
| Is prefill/decode power asymmetry visible at long context? | L2 | "Within `M3 Max / MLX / powermetrics`, `long_short` and `short_long` differed in gross phase-window power/energy structure by `<effect>`, above the Window A floor; short-prefill windows remain not resolvable." | 2M/AP-2. | Phase claims are gross-only until phase-idle modeling exists. |
| Do same-boundary efficiency rankings flip across 2M profiles? | L2 | "Within `M3 Max / MLX / powermetrics`, `<condition A>` ranked above `<condition B>` for `<metric>` on `<shape>` only where rank gap exceeded comparison MDE; otherwise the result is an unresolved tie." | 2M + AP-3. | Two-model/four-shape grid may produce unresolved ties rather than rank claims. |
| Do rail/DVFS signatures differ by phase? | L2 structural, not absolute rail truth | "Within `M3 Max / MLX / powermetrics`, rich telemetry showed `<GPU/CPU/ANE/DVFS>` structure differed between `<phase/profile>` and `<phase/profile>`; the claim is about modeled-rail structure, not full-system watts." | 2M with P2-009 rich telemetry. | Powermetrics rails are modeled SoC subsystems, not wall power. |

### After Window B + substrate

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Can Q4 fit fixed + prompt + decode energy terms? | L3 | "For `<target/model/quant/policy>`, the categorical model `E = fixed + prompt_level + decode_level` predicted held-out cells `(512,256)` and `(4096,512)` within `<error>` after floor and residual checks." | P2-019 `q4_l3_shape_grid_v1`, AP-1. | Holdouts may fail or effects may be below floor, forcing L1/L2 downgrade. |
| Do rankings stay stable on the full shape grid? | L2 | "Within the same boundary, `<model/quant/runtime A>` ranked above `<B>` on `<shape/metric>` only where rank gap exceeded comparison MDE; otherwise unresolved tie." | Window B grid + AP-3. | Rank gaps may be smaller than MDE. |
| Does synthetic prompt content matter at fixed shape? | L2 | "At equal shape, `<content condition>` differed from repeated-seed control by `<delta>` on request energy, with n sized from Window A and above floor." | P2-020 content sentinel, AP-6. | Realized shape/stop policy must stay matched. |
| Does category explain energy beyond token counts? | L2 | "On the common `512/256 fixed_budget_exact` stratum, category residual after controlling for shape was `<delta>`; equivalence/null only if the residual CI lies entirely within ±2% of request energy AND the 2% margin exceeds max(floor_abs_j, floor_cmp_j) (AP-4 gate)." | `jw_mixed_v1` identification core after P2-010a; AP-4. | Small category deltas may be below floor. |
| Does natural-EOS "thinking" inflate reasoning-model energy? | L2 | "For `<reasoning model>`, natural-EOS reasoning requests consumed `<delta>` more request energy than fixed-budget controls, attributable to observed emitted-token/stop-reason distributions, not hidden correctness filtering." | `jw_mixed_v1` natural-EOS pilot. | Output-length inflation must be observed cleanly; no accuracy/judge claim. |
| Is multilingual tokenizer fertility an energy tax? | L2 | "For `<script/language>`, semantic-matched energy differed from token-matched controls by `<delta>`; token-matched null/effect reported separately." | `jw_mixed_v1` multilingual legs; FLORES after HumanEval smoke. | Source licensing and tokenizer-shape matching must be exact. |
| Energy per correct answer under controlled envelope? | L2, only after P2-010b/full scored run | "On the controlled affine ladder, `<model class>` observed `<energy_per_correct>` at `<level band>` only where level-window energy cleared floor and the correctness denominator guard passed; no intelligence-per-joule claim." | P2-010a substrate + P2-010b smoke + later scored campaign; AP-5. | Envelope validation and binomial guard can force `not estimable`. |
| External marked-runner energy layer? | L1/L2 with AP row | "External harness `<X>` version `<Y>` reported metric artifact `<Z>`; JouleWise measured energy for the same marked item/subset windows." | P2-022 shim spike, then AP-covered repetitions only. | Harness markers must pair, stay inside measured windows, and preserve hashed result artifacts. |
| HumanEval import smoke? | L0/L1 | "JouleWise froze and executed a HumanEval subset as suite items with auditable provenance and observed item/subset energy under a named output policy." | P2-023 after P2-022. | Plumbing smoke only; no pass@k, accuracy, or coding-capability interpretation. |

P2-022 shim and P2-023 HumanEval rows are post-2M + substrate (Window B not required).

### Hardware-gated

| Question | Ceiling | Ladder-compliant claim template | Campaign | Weakest assumption |
|---|---:|---|---|---|
| Does split inference reduce energy? | L2 boundary-labeled; stronger with wall calibration | "For `<device pair/link/model/shape>`, split total energy `<prefill + serialize + transfer + deserialize + decode>` was `<less/greater>` than the better monolithic reference by `<delta>`, with boundaries named and calibration status stated." | Phase 3 split; Q1/F4/F5. | Cross-boundary sums are descriptive unless calibrated. |
| How sensitive is split energy to link speed? | L2 | "For `<payload/model/pair>`, changing `<1GbE/2.5GbE/10GbE>` changed transfer energy/time by `<delta>` and moved/did not move the crossover within the measured range." | P1-004 links + transfer bench. | Link throughput must be measured, not assumed. |
| What is the split energy-latency Pareto frontier? | L2 | "Within `<comparison set>`, `<configuration>` is Pareto-frontier because no measured alternative had both lower energy/token and lower `<latency metric>`." | Phase 3 + F6. | Latency metric choice must be fixed per figure. |
| Does measurement boundary change conclusions? | L2; L4 only with replication | "For `<condition pair>`, the conclusion under platform rails `<matched/flipped>` under `wall_meter AC` by `<delta>`." | P1-003 wall meter; Q6/F11. | Wall-meter synchronization/export quality. |
| Do KV-size predictions match measured transfer economics? | L2 | "For `<runtime/model/link>`, analytic KV size predicted serialized payload within `<error>` and transfer energy/GiB within `<interval>`." | P1-004 + P1-006; C5-2.3. | Runtime cache format must be portable or explicitly scoped. |
| Do device rankings generalize beyond one machine? | L2 within boundary; L4 with second unit/calibration | "Across named `<units/stacks>`, `<finding>` replicated under stated workloads and boundaries; cross-boundary quantitative ranking uses named calibration bundles." | P1-006 devices, second unit, wall/USB-C, cross-lab. | Unit-to-unit variance may dominate current floors. |
| Local-vs-datacenter full-system crossover? | Scenario result, not measured-equivalent cloud claim | "Under documented external datacenter-energy assumptions and local `wall_meter AC` measurement, local request energy was `<less/greater>` than the modeled remote alternative for `<workload>`." | Wall meter + network leg; C5-2.9. | Cloud-side energy remains assumption-based, not measured by JouleWise. |

C-015 records three unscheduled cheap campaigns as a select-after-floors
shortlist, not stealth scope: C5-1.6 sampler ABBA, C5-1.12 quantization
benefit decomposition, and C5-1.8 runtime energy attribution. Queue row
P2-024 owns the post-Window-A selection.


# Hardware-gated research agenda — steelmanned potential (Council C-005)

Drafted 2026-07-07 by council C-005 (session shape B; see
`docs/council_log.md` C-005 for positions, adjudications, and dissents).
Format follows `docs/research_question_bank.md`: candidate questions, not
promotions — promotion still requires a named RQ slot in
`PROJECT_STATUS.md`, a data plan that does not displace queue ranks, and
scope fit. IDs here are `C5-<tier>.<n>` to avoid colliding with Q1-Q6.

Every question below survived a devil's-advocate (examiner) round; the
scoping is deliberate, not decorative. Standing kills re-affirmed and
inherited by everything here: no per-token joule claims (~9 Hz sampler vs
~4 ms token cadence — chunked windows only), no unqualified absolute-joule
claims from modeled rails, no general intelligence-per-joule, claim
wording "on this M3 Max / MLX / powermetrics" until a second unit or lab
exists, and present-tense capability claims only for landed code (P2-010 scored suite is QUEUED,
not landed (D-014/P2-011 aggregation and P2-009 telemetry LANDED 2026-07-07)).
(Amendment 2026-07-08: the P2-010 substrate + affine core + generator
engine are now LANDED (PRs #17-#20, D-044..D-047); still not landed:
envelope-gate script, real-tokenizer manifests, all suite campaigns.)

## Why this instrument matters (steelman preamble, examiner-scoped)

**Auditability is the differentiator, not topic novelty.** Energy
benchmarks exist (MLPerf Power; TokenPowerBench; ML.ENERGY-style
datacenter work) — what does not exist is local-inference joules/token
that a skeptic can re-derive: JouleWise publishes self-contained bundles
where config, raw power trace, vendor telemetry, event log, and outputs
are preserved and `validate-bundle --strict` proves the summary re-reduces
identically from raw evidence. Energy tables are otherwise unauditable at
exactly the step that matters.

**Energy per request is becoming the binding constraint on local AI.**
Battery, thermal envelope, and sustained throughput all reduce to joules
per completed request. Latency says whether a local model feels fast
once; `energy_request_j` with uncertainty says whether it can run all day.
The instrument already resolves this at CV 0.3-1.4% across repetitions.

**Apple-Silicon unified memory is a clean window into the memory-bound
decode regime.** The measured 1.5B vs 122B-MoE pair showed energy/token
numerically aligning with the active-parameter ratio while decode power
stayed nearly flat (~23.5 → ~27.5 W). That is hypothesis-generating, not
a scaling result (see C5-1.1), but it demonstrates that the instrument can
see the shape of the regime that throughput benchmarks cannot.

**Negative results are structured data.** did-not-fit, throttle,
contaminated-idle, and cap-hit outcomes produce complete `unsupported` or
quality-flagged bundles. Competitors discard their failures; here the
feasibility frontier is itself a reportable dataset (this is how a
negative Hailo verdict stays a finding).

**The benchmark can referee efficiency claims.** Quantization, runtime,
and architecture "efficiency" claims mix latency, memory, and energy with
no common accounting. Typed configs + one reducer + named measurement
boundaries make within-boundary refereeing possible today and boundary-
labeled cross-target comparisons possible with planned hardware.

**Q4's fixed-vs-marginal model turns benchmark data into engineering
budgets.** `E = fixed + prefill(p) + decode(d)` per target/model/quant
lets an app team budget a workload distribution (an agent session, a RAG
pipeline) from benchmark coefficients — the bridge from instrument to
battery-life engineering.

**The split study is a first-of-kind edge measurement.** Prefill/decode
disaggregation is argued from datacenter throughput; nobody has measured
the ENERGY crossover on local links with both-end power sampling and
per-stage decomposition (prefill/serialize/transfer/deserialize/decode).
Either verdict — crossover exists or doesn't in range — is publishable.
(Examiner note, recorded as standing tension: this is also the most
hardware-gated item in the agenda; the feasibility-first Phase 3 ladder
is the mitigation.)

**The infrastructure outlives any single result.** Every future target is
forced through the same contract (config → bundle → strict re-reduction →
boundary-named summary). The M3 Max numbers are the demo; the reusable
referee is the contribution.

## TIER 1 — answerable with current hardware (M3 Max alone)

Landed software (P2-009 rich telemetry, P2-011 uncertainty
aggregation, 2M campaign tooling — all 2026-07-07) is available;
queued software (P2-010 scored suite) is assumed where noted; no new
hardware. (Amendment 2026-07-08: the suite substrate/ladder-core/
generators are landed, PRs #17-#20; campaign execution still pending.) Throughput reality: ~30-75 bundles/hour makes n=10-20 designs
cheap.

- **C5-1.1 Active-parameter energy scaling (the honest version of the
  122B observation).** Does decode energy/token scale with active rather
  than total parameters across dense and MoE models on one pinned stack?
  Measure on the named M3 Max / MLX / powermetrics SoC-rail boundary:
  gross decode-window joules, mean power, and throughput across 4-6 model
  points (dense 1.5B/7B/14B bridge + ≥2 MoE), same quant recipe, pinned MLX
  version, fixed shapes, n≥5 interleaved; fit gross mJ/token ~ active_params
  (+ total-param/KV covariates) with intervals. Any idle-subtracted result is
  a labeled within-device secondary sensitivity view, not the scaling
  headline (D-067).
  Hardware: now. Methodology: runtime is part of the condition — rerun
  after MLX updates as a separate condition. Threat: model families
  differ in more than active params; the dense bridge and quant pinning
  carry the inference. Who cares: efficient-ML and MoE architecture
  researchers; local-inference benchmark authors. Amendment 2026-07-08
  (C-014): with 4-6 model points, this supports descriptive L2 pairwise
  contrasts only unless the model set grows enough for a predeclared
  one-covariate fit; never fit active+total+KV covariates on 4-6 model
  points.

- **C5-1.2 Context-length energy scaling.** Where does measured energy
  stop being linear in prompt length? Measure: prefill/decode energy over
  prompt 128→8192 (fixed decode 64/256), n≥5; unsupported cells recorded.
  Hardware: now. Methodology: chunked windows; short-prompt prefill
  reported "unresolved at sampler resolution", never 0.03 J-style point
  claims. Threat: SoC boundary underrepresents unified-memory traffic —
  directional bias for long-context (examiner #11); flag pending Q6
  calibration. Who cares: long-context model teams, serving researchers.

- **C5-1.3 Phase-resolved compute-vs-memory signatures (uses landed P2-009 telemetry).**
  Does the rail mix and DVFS residency shift between compute-bound
  prefill and memory-bound decode, and how does the shift move with model
  size/quant? Measure: per-phase CPU:GPU energy division, GPU
  frequency/dvfm residency, idle_ratio across the 2M matrix. Hardware:
  now. Methodology: promotes the banked "CPU:GPU division by phase" item
  with the telemetry that makes it cheap. Threat: modeled rails — claims
  are about STRUCTURE (ratios, shifts), not absolute rail watts. Who
  cares: Apple/Metal/MLX performance engineers, systems-paper authors.

- **C5-1.4 DVFS residency as a throttling early-warning (uses landed P2-009 telemetry).**
  Do residency histograms and idle_ratio drift predict throttling before
  energy/throughput visibly degrade under sustained inference? Measure:
  20-60 min sustained blocks; per-rep energy, residency, cap-hit rates,
  recovery slopes; n≥5 blocks. Hardware: now. Methodology: cooldown-gate
  records and interleaving separate warmup, drift, and throttling.
  Threat: one chassis/ambient; report as within-target characterization.
  Who cares: laptop-inference tool builders, mobile/edge systems
  researchers, thermal-management teams.

- **C5-1.5 Cooldown-recovery curves and the energy tail (promotes banked
  item).** Recovery time and excess idle joules vs preceding run
  intensity; is the tail material to honest energy/request accounting?
  Measure: post-run recovery traces after an intensity ladder; time-to-
  baseline, cap-hit rate, excess joules; n≥5. Hardware: now. Threat:
  ambient sensitivity — record environment snapshots (P2-009). Who
  cares: on-device serving teams, benchmark methodology authors.

- **C5-1.6 Sampling-strategy energy overhead (power-gated).** Does
  temperature/top-p/beam sampling cost measurable energy beyond
  deterministic decoding at fixed output length? Measure: greedy vs
  sampled at fixed decode caps, recorded stop reasons; PRECONDITION:
  measured detection floor first; n≥10 paired ABBA. Hardware: now.
  Threat: plausibly below floor at n=5 — the null ("sampler choice is
  energy-free at this resolution") is the likely and still-reportable
  result. Who cares: runtime maintainers, generation-defaults tuning.

- **C5-1.7 Keep-warm vs reload breakeven (promotes banked cold-start
  item; harness extension).** Model-load joules, resident idle-power
  delta, cold-vs-warm TTFT → breakeven interarrival time per
  model/quant. Measure: load-window sampling (extension: measure outside
  current window), idle-resident deltas, n≥5. Hardware: now. Threat:
  idle-resident delta may be near the detection floor for small models;
  report identifiability. Model-load/warmup trace capture was reviewed and
  DEFERRED by C-015 (R2 items 14-15); it must land before any C5-1.7
  corpus. Who cares: desktop-assistant and agent-framework teams,
  serverless-inference researchers.

- **C5-1.8 Runtime energy attribution.** How much of measured inference
  energy belongs to the runtime, not the model? Same model artifact
  (where format permits) across MLX vs llama.cpp-Metal vs ollama on the
  same machine. Measure: energy/token, power, TTFT, rail mix over a
  shared shape grid, n≥5; artifact hashes and versions pinned. Hardware:
  now. Methodology: where formats force different artifacts (MLX vs
  GGUF), the comparison is stack-vs-stack, stated as such. Threat:
  version churn — this question is BUILT on the pinning discipline
  rather than wounded by it. Who cares: runtime maintainers, local-LLM
  users, model publishers choosing release formats.

  **2026-07-17 kernel-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **NV**. On the 3080 Ti, same model artifact where format
  permits: llama.cpp-CUDA vs vLLM (TensorRT-LLM gated on Ampere-support
  verification) — how much energy variance tracks kernel-library identity vs
  runtime scheduler? Ceiling: **L2 stack-vs-stack**. Forbidden upgrade: **no
  `belongs to the kernel layer` language when artifacts/formats differ; no
  runtime-agnostic kernel claims**. This is an amendment to C5-1.8, not a new
  C5-1.13 thesis. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-1.9 MoE-vs-dense energy per correct answer, quarantined (needs
  P2-010).** Under the controlled-envelope ladder, do MoE and dense
  models at similar quality bands differ in energy per correct answer?
  Measure: affine_mod_ladder_v1 level-window energy + exact scoring;
  token/stop-reason distributions reported (EOS-bias audit). Hardware:
  now. Methodology: C-004 quarantine binds — correctness is an
  annotation; claim template "on this controlled ladder", never
  intelligence-per-joule. Who cares: MoE architecture teams, benchmark-
  methodology reviewers.

- **C5-1.10 The failure frontier as an energy dataset (promotes banked
  item).** Which model × quant × context cells fit, fail, swap, or
  throttle on 128 GB unified memory — with pre-failure energy and memory
  pressure recorded? Measure: full matrix including structured
  `unsupported` bundles, env snapshots. Hardware: now. Threat: one
  memory configuration; frame as the 128 GB-class frontier. Who cares:
  model release engineers, hardware buyers, benchmark authors.

- **C5-1.11 Dark-silicon rail utilization, systematized (promotes banked
  item; needs P2-009).** What fraction of the SoC's rails does each
  runtime/model pair energize (ANE-dark being the first quotable
  instance)? Measure: per-rail energy share and residency by phase
  across the runtime grid of C5-1.8. Hardware: now. Threat: modeled
  rails — report utilization structure, cross-checked against vendor
  combined_power. Who cares: accelerator vendors, runtime implementers.

- **C5-1.12 Quantization benefit decomposition, Mac leg.** For MLX quant
  variants of one family (4/8-bit), how much energy benefit is lower
  power vs shorter time? Measure: decode energy, mean power, throughput
  per quant at fixed shapes, n≥5. Hardware: now (extends to Tier 2 for
  CUDA/GGUF legs). Threat: quant recipes change outputs — greedy-diff
  and report divergence. Who cares: quantization researchers, edge
  deployment teams.

## Workload/query-set expansion (first-class topic, Tier 1 hardware)

Today's workloads are single-prompt fixed-shape grids plus the queued
affine ladder. (Amendment 2026-07-08: the affine ladder CORE is landed,
PRs #17-#20; the envelope-gate script and smoke campaign remain queued.) The council's workload lens designed the expansion; the
examiner frame was applied up front: at fixed token shape, most category
differences may collapse into token counts — that null is itself a
publishable result, named here the **Token-Shape Sufficiency Null**.

**Category taxonomy and expected energy mechanisms.** Six categories,
each with a mechanistic reason energy could differ and an honest
distinguishability call:
chat/instruction (high output-length variance under natural EOS; expected
NULL at fixed shape — the ecological baseline); code generation
(decode-heavy, distinct stop-reason behavior; near-null at fixed budget
unless tokenizer throughput differs on code tokens); summarization/
long-context (prefill-heavy, KV growth — YES, distinguishable via prefill
energy/TTFT/phase mix); reasoning/CoT (thinking-token inflation on
reasoning models — YES, the category effect most likely to be large,
directly measurable on the already-benchmarked Qwen3.5-122B); structured
JSON extraction (early valid-close stops make short answers cheap —
collapses at fixed envelope; probes EOS bias); multilingual (tokenizer
fertility differs sharply by script — YES when semantically matched,
expected null when token-matched; run BOTH, the pair separates fertility
from semantics).

**Realistic-vs-synthetic discipline (hybrid, both by design).**
Deterministic seed-derived synthetic profiles are the CONTROLS
(reproducible, shape-matched, redistribution-safe); pinned realistic
exemplars are the ecological probes (licensing/contamination/tokenizer
caveats recorded per source). Every realistic category runs in two modes:
`fixed_budget_exact` (greedy, EOS suppressed, fixed max_tokens — the
headline category-at-fixed-shape comparison) and `natural_eos` (greedy,
EOS allowed, stop reasons recorded — the operational-cost view). EOS-bias
rule inherited from C-004: natural termination is a workload property,
not a fairness control; wrong/short/refusal answers looking energy-cheap
must be visible in stop-reason distributions, never hidden.

**Sources to pin (hash-manifested frozen subsets, never "latest split"):**
LMSYS-Chat-1M for chat SHAPE distributions (terms-gated, not for
redistribution — derive synthetic shapes from it); HumanEval/MBPP-style
code prompts (MIT, contaminated — prompt exemplars only, no accuracy
claims); public-domain/government texts + synthetic needle controls for
summarization; GSM8K/MMLU-style items for reasoning shapes (MIT on HF,
contaminated — shape not correctness); synthetic fixed-schema records for
JSON; FLORES-200 for multilingual (CC BY-SA, parallel sentences enable
the semantic-matched leg). Where licenses are uncertain, synthetic wins.

**Concrete recommendation — `jw_mixed_v1` (adopt as the first official
workload expansion).** Amendment 2026-07-08 (C-014): this supersedes the
C-005 fixed-budget-full-first sequencing; the C-005 category/source
discipline otherwise remains intact. Phase 1 is the identification core:
all 6 categories at the common-shape identification stratum, `512/256`
`fixed_budget_exact`, synthetic + realistic where licensing is clean.
Phase 2 is a natural-EOS pilot with >=4 items/category on reasoning, JSON,
chat, and multilingual. Phase 3 is the full category panels, gated on
above-floor structure from Phases 1-2. The original full panel remains the
expansion target after the gate: 6 categories x 8 items = 48 items per
target/model/quant, n=5, categories interleaved round-robin, with the
C-005 category shapes (chat 512/256; code 4x512/256 + 4x1024/512;
summarization 4096/256; reasoning 512/512; JSON extraction 1024/128;
multilingual FLORES 8 languages semantic-matched then token-matched
512/256; ~240 bundles = 3-8 hours per target/model/quant at observed
throughput) unless the Phase 1/2 gate amends them. Harness needs (all additive): `workload_profile.category` +
`source_manifest` + sha256 + per-item `output_policy` fields; category as
a campaign-matrix axis alongside shape (never instead of it); per-item
stop reason/emitted-token/response hash in outputs; reuse P2-010a item
windows + identifiability flags; aggregation waits on P2-011. Out of
scope stays out: no accuracy evals, no judges, no retries — correctness
only as quarantined annotation. Category claims follow AP-4 in
`docs/contracts/analysis_plans.md`.
Amendment 2026-07-08 (D-046 and deferred-binding B6 disposition):
`jw.multiling` synthetic is phase-1 control material, not a C5-W.4 FLORES
replacement; the FLORES 6-vs-8 language count and token-matched
substitution decision are deferred to the FLORES/source session.

**Questions it unlocks (Tier 1):**

- **C5-W.1 Does category explain energy beyond token counts?** Paired
  synthetic controls vs realistic exemplars at identical shape; either a
  category effect or the Token-Shape Sufficiency Null — both reportable.
  Threat: small deltas need the detection floor first (examiner #2). The
  reportable comparison is AP-4 in `docs/contracts/analysis_plans.md`,
  using the common-shape stratum and the predeclared equivalence margin
  from C-014. Who cares: benchmark authors, app engineers budgeting
  features.
- **C5-W.2 Does thinking-token inflation dominate reasoning-model request
  energy?** Fixed-budget vs natural-EOS on the reasoning flagship;
  measures the energy price of "thinking" as output-length inflation.
  Who cares: reasoning-model teams, agent builders choosing modes.
- **C5-W.3 Is category energy-ranking stable across models and quants?**
  The workload-axis analogue of Q5; do code/long-context/reasoning flip
  the ordering? Who cares: procurement, model-selection tooling.
- **C5-W.4 Tokenizer fertility as an energy tax.** Semantic-matched vs
  token-matched multilingual pairs isolate joules attributable to
  tokenizer choice per script. Who cares: multilingual deployment,
  tokenizer designers.


## TIER 2 — unlocked by already-planned hardware gates

Gates by name: P1-006 device access (owned RTX 3050; Jetson Orin Nano),
the 3080 Ti borrow window (Phase 3 interconnect sweep only), P1-003 wall
meter decision (R-007), P1-004 network topology (1GbE / 2.5GbE / optional
10GbE).

- **C5-2.1 Quantization decomposition, cross-stack.** C5-1.12 extended
  to llama.cpp-CUDA/vLLM on the 3050: is the time-vs-watts split of
  quantization benefit hardware-dependent? Gate: P1-006. Threat:
  nvidia-smi board boundary ≠ SoC boundary — within-target decomposition
  first, cross-target only boundary-labeled. Who cares: quantization and
  runtime teams.

- **C5-2.2 Batch size and the prefill/decode energy split.** Does
  static batching reshape gross energy/request and the phase split under
  an interactive latency bound? Measure: B in {1,2,4,8,16}, group gross
  energy and gross joules/request within the named target/telemetry
  boundary, latency distribution, and structured memory-fit failures.
  The Mac leg is MINTED (2026-07-16: AXI-SB verdict `supported` on pinned
  mlx-lm 0.31.3, lead-run B∈{2,4} live probes with full per-request
  observability — `docs/specs/axi/sb_static_batch_verdict.md`); execution
  still requires the follow-on batch adapter row, P2-015 floors, and its own
  scheduled quiet-Mac block. The serving-style leg remains gated on P1-006.
  Continuous batching is a post-capstone extension (D-070).
  Who cares: serving researchers, scheduler developers.

- **C5-2.3 Predicted-vs-measured KV economics.** Does the analytic
  kv-size model predict serialized cache size, transfer energy, and
  deserialize energy? Measure: transfer joules/GiB both ends over
  payload ladder 16 MiB-2 GiB per link; deserialize windows; predicted
  vs actual deltas calibrate the model. Gates: P1-004 links + any second
  node (P1-006). Methodology: both-end sampling, clock-offset bounds
  flagged; this is the instrument's designed home turf. Who cares:
  disaggregated-inference researchers, KV-cache system builders.

- **C5-2.4 KV-cache quantization end-to-end.** Does q8_0 cache save
  energy after serialize/deserialize overhead, or only bytes? Gates:
  P1-006 + P1-004 (llama.cpp cache portability spike verdict). Who
  cares: llama.cpp maintainers, KV-compression researchers.

- **C5-2.5 Speculative decoding joules per ACCEPTED token (promotes
  banked item).** With/without draft model at output equivalence.
  Measure: total joules, acceptance rate, joules/accepted-token, n≥5.
  Gate: runtime support (MLX or 3050 stack). Methodology: the
  accepted-token denominator is the trap the harness's token accounting
  defuses. Who cares: speculative-decoding researchers, runtime teams.

  **2026-07-17 DSpark/DFlash candidate riders (D-075).** These remain
  riders on C5-2.5, not four independent theses; every effect is floor-gated
  and `C-023-OUTPUT-IDENTITY` is binding. Evidence for all four:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

  - **C5-2.5a — cross-method contrast.** Status: **candidate (deferred
    rider)**; earliest phase: **NS**. At matched target model, quantization,
    prompt roster, and output equivalence, do a fixed-K block-diffusion
    drafter (DFlash) and a variable-K confidence-scheduled drafter (DSpark)
    differ in gross request energy and gross J/committed-output-token on the

exec
/bin/zsh -lc "sed -n '881,1095p' docs/research_question_bank.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
    same MLX stack? Ceiling: **L2**. Forbidden upgrade: **No cross-method
    efficiency generalization beyond the measured target/runtime/tokenizer
    pair; accepted-draft J/token stays a mechanism diagnostic, never the
    on/off efficiency denominator (token_normalization.md D-037 rider).** It
    stays out of the committed standalone set until a prospective
    cross-mechanism design is affordable.

  - **C5-2.5b — proposal-work secondary.** Status: **candidate**; earliest
    phase: **PF**. Is proposal length an energy knob: holding drafter and
    target fixed, does gross J/committed-output-token vary systematically
    with realized mean proposed-K (DFlash block-size sweep 8/16 vs DSpark's
    dynamic schedule), i.e. does per-round proposed work enter the Q4
    coefficients? Ceiling: **L2**. Forbidden upgrade: **No claim that
    K-scheduling saves energy in general; result scoped to one
    runtime/target/boundary, and realized per-round tokens_proposed must be
    runtime-observed, never inferred from the configured cap.**

  - **C5-2.5c — primary Q4 break-even rider.** Status: **candidate**;
    earliest phase: **PF**. Drafter-overhead economics: at what aggregate
    acceptance rate does spec-on gross energy break even with spec-off for
    each drafter class (block-diffusion vs semi-autoregressive vs native MTP
    if a supported runtime lands), at matched output? Ceiling: **L2**.
    Forbidden upgrade: **No serving-system or cross-hardware generalization
    from one pair; the MTP arm is contingent on an AXI-SC supported verdict
    and is a separate frozen family (FAM-AXI-SPEC-NATIVE-MTP), never pooled
    with draft_model arms.**

  - **C5-2.5d — mandatory contamination control.** Status: **candidate**;
    earliest phase: **PF**. Hybrid-lookup contamination bound: how much does
    mlx-dspark's drafter-free n-gram lookup path (on by default) shift
    measured gross energy and acceptance accounting vs `--no-lookup-drafts`,
    quantified as an attribution-contamination diagnostic? Ceiling: **L2
    (diagnostic/methods row)**. Forbidden upgrade: **No mechanism-yield or
    efficiency claim from mixed-origin rounds; the row exists to justify the
    mode pin, not to rank lookup vs drafter.**

- **C5-2.6 Energy-optimal request coalescing under a latency bound.**
  Replayed arrival traces × coalescing windows → joules/request vs
  p95 latency Pareto. Gate: P1-006. Who cares: edge gateways, serving
  schedulers.

- **C5-2.7 Device perf/W rankings with runtime held constant (extends
  Q5, doesn't duplicate it).** Same llama.cpp build/model/quant across
  M3 Max / 3050 / Orin (+3080 Ti in window): do rankings survive
  workload changes when the RUNTIME variable is removed? Gates: P1-006,
  borrow window. Threat: boundary heterogeneity — ranking claims are
  per-boundary until wall-calibrated (C5-2.9). Who cares: hardware
  reviewers, edge procurement.

  **2026-07-17 kernel-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **NV**. When the runtime is held constant (same llama.cpp
  build/model/quant) across M3 Max Metal and 3080 Ti CUDA, does recorded
  kernel-layer identity (attention kernel, BLAS backend, graph mode) explain
  residual energy structure beyond device? Ceiling: **L2 within each
  measurement boundary; per-boundary only until wall-calibrated (C5-2.9)**.
  Forbidden upgrade: **no cross-vendor kernel-API efficiency ranking; no
  cross-device winner across heterogeneous boundaries**. Evidence:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.8 Placement-policy optimality from Q4 coefficients.** Can
  fitted fixed+marginal coefficients + measured transfer costs choose
  the energy-optimal prefill/decode placement, validated against
  measured splits? Gates: full Phase 3 set (P1-006, P1-004, borrow
  window). Methodology: modeled-vs-measured labeled; composite bundles.
  Who cares: disaggregated-serving and placement-policy researchers.

- **C5-2.9 Local-vs-datacenter crossover economics (survivor of the
  carbon-label kill).** When is a local request energy-cheaper than
  shipping it out — full-system watts, transfer included, datacenter
  side as DOCUMENTED published-figure assumptions, never measured-
  equivalent? Gates: P1-003 wall meter (+P1-004 for transfer leg).
  Methodology: the wall meter is what makes the local side full-system
  honest; boundary-directional bias (examiner #11) is why SoC rails
  alone can't carry this. Who cares: sustainability-of-ML community,
  enterprise local-vs-cloud deciders.

- **C5-2.10 Boundary-directional bias quantification (elevates Q6).**
  Not just "does the boundary change conclusions" but WHICH comparisons
  flip: memory-heavy vs compute-heavy conditions should diverge
  rail-vs-wall differently. Gate: P1-003. Methodology: pairs with
  C5-1.2/C5-2.3 threat notes; turns their caveat into a measured
  correction. Who cares: every downstream consumer of cross-target
  numbers; measurement-methodology reviewers.

- **C5-2.11 On-device quantized-KV energy.** Status: **candidate**;
  earliest phase: **PF**. Does quantized KV cache (`kv_bits` 8/4, mlx-lm)
  reduce gross request energy for long-context decode on-device, or only
  memory footprint? Ceiling: **L2, per-boundary, MLX-scoped; un-gated variant
  of C5-2.4 (no transfer leg, runnable on the D-073 fleet now)**. Forbidden
  upgrade: **No byte-saving-equals-energy-saving claim (inherits C5-2.4's
  ban); no cross-runtime generalization from MLX alone; no quality-neutrality
  claim without C-023-style output-equivalence evidence**. Attachments:
  C5-2.4, C5-1.12, and C-023-QUALITY-EQUIV-QUANT. Evidence: [2026-07-17
  extension-axis evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.12 Bounded-window KV marginal-slope rider.** Status:
  **candidate**; earliest phase: **PF**. Does a bounded evicting window
  (`RotatingKVCache` via `max_kv_size`) flatten the marginal J/token slope
  over long generations versus an unbounded step-growing `KVCache`? Ceiling:
  **L2 in chunked windows only (RQ-KV-GROWTH discipline: token cadence
  outruns power sampling)**. Forbidden upgrade: **No per-token joule claims
  below the cadence/sampling floor; no output-equivalence assumption —
  eviction changes generations, so contrasts are work-matched, never
  output-matched**. This is an amendment under C5-1.2/RQ-KV-GROWTH, not an
  independent thesis. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.13 Serialized prompt-cache crossover rider.** Status:
  **candidate**; earliest phase: **PF**. Is save+load+replay of a serialized
  prompt cache energy-cheaper than re-prefill at prompt length N on the same
  machine, and where is the crossover? Ceiling: **L2 same-machine,
  same-stack (promotes answered-L1 RQ-MLX-KV-REPLAY to an energy claim)**.
  Forbidden upgrade: **No cross-machine or cross-stack portability claim
  (RQ-MLX-KV-REPLAY's existing ban); no generalization beyond the measured
  prompt-length ladder**. This is an amendment under RQ-CACHE-PREFIX and
  RQ-MLX-KV-REPLAY, not an independent thesis. Evidence: [2026-07-17
  extension-axis evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-2.14 Q4 cache-policy coefficient rider.** Status: **candidate**;
  earliest phase: **PF**. Do KV-cache-policy contrasts move the fitted Q4
  coefficients in the predicted direction (marginal per-token term down
  under quantized KV, fixed term unchanged)? Ceiling: **L2; L3 only through
  Q4/AP-1's existing holdout machinery (D-070 clause 5)**. The candidate
  rider itself remains capped at L2. Forbidden upgrade: **No new-thesis
  framing — this is a Q4 stress test, not a KV-energy model; no
  coefficient-direction claim below P2-015 detection floors**. Evidence:
  [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

## TIER 3 — requiring new acquisitions (hardware class + rough cost tier)

- **C5-3.1 Machine-to-machine variance / generalizability floor.** A
  second M-series unit (used M1/M2/M4, ~$500-1500) answers the
  examiner's sharpest structural attack: which Tier-1 findings replicate
  on a second box, and what is unit-to-unit variance relative to the
  detection floor? Also unlocks chassis-thermal comparisons (Air vs Pro
  fanless/fanned envelopes). This is the cheapest purchase that converts
  "on this M3 Max" claims into population claims.

- **C5-3.2 Battery-path energy and modeled-rail validation.** A USB-C PD
  power analyzer (~$100-300) measures DC input on battery-excluded runs
  and cross-checks powermetrics' modeled rails at a second physical
  boundary — a cheap partial answer to the modeled-vs-measured attack,
  complementary to the AC wall meter.

- **C5-3.3 Cross-ISA NPU/SoC comparison.** AMD Ryzen-AI mini-PC and/or
  Snapdragon-X laptop (~$800-2000 each): do the dark-silicon and
  active-param-scaling structures hold beyond Apple's stack? Requires
  one new telemetry adapter per platform (the adapter contract is the
  deliverable that makes this tractable).

  **2026-07-17 backend-provenance rider (D-075).** Status: **candidate**;
  earliest phase: **PC**. Record kernel/backend build provenance
  (CUDA/Metal/HIP target, kernel library ids) in all bundles now so a
  post-capstone AMD/ROCm replication leg is comparable without re-running the
  NVIDIA/Mac corpus. Candidate-rider ceiling: **L1 feasibility**; the parent
  row's separate L4 replication posture is not an intake upgrade. Forbidden
  upgrade: **no NVIDIA-vs-AMD efficiency claim from single
  units or heterogeneous boundaries; no cross-ISA claim before a
  platform-specific adapter study**. Evidence: [2026-07-17 extension-axis
  evaluation](process_traces/2026-07-17-extension-axes/).

- **C5-3.4 Phone-class edge inference.** One flagship phone
  (~$800-1200) + llama.cpp/MLX-swift: the actual battery-constrained
  edge story. Honest note: telemetry access on phones is the hard part;
  a feasibility verdict (possibly `unsupported`) is itself the
  publishable first result, exactly like Hailo.

- **C5-3.5 Cross-lab replication (zero hardware, the credibility
  acquisition).** A second lab runs the frozen suite from published
  bundles + configs. Gates every public-facing application (leaderboard,
  standard, audit service); costs coordination, not money.

## Unexpected-applications shortlist (beyond papers)

Ranked by usefulness × lowest extra work; every public-facing one carries
the internal-first ladder from the examiner round.

1. **Prompt/template energy profiler** — product engineers measure the
   joule cost of system-prompt/RAG-template variants; ~3-8 person-days
   (prompt-matrix configs + diff report); rides per-request joules +
   phase attribution. Available now.
2. **Attach-a-bundle power-bug repro** — runtime maintainers receive
   "model got slow/hot" reports as reproducible bundles; ~5-10 days
   (issue template + doc); rides bundle completeness. Available now;
   mundane and high-leverage.
3. **CI energy-regression gates** for MLX/llama.cpp — nightly pinned-host
   run fails on mJ/token regressions; ~5-15 days; rides strict
   validation + config hashing. PRECONDITIONS (examiner): measured
   detection floor as the threshold unit, env snapshots (P2-009),
   baseline-refresh policy across OS updates.
4. **Vendor/press claim audit** — "efficient" claims answered with
   boundary-named measured bundles; ~5-10 days. Defensible as "on this
   boundary, this workload"; overclaims if framed as absolute device
   energy without wall calibration.
5. **Practitioner energy model cards / leaderboard** — joules/token with
   uncertainty next to quality scores; ~5-10 days internal. Ladder:
   internal table → published methodology → cross-lab public table
   (C5-3.5); public version is KILLED until then.
6. **OS/driver/runtime update forensics** — before/after bundles detect
   power-behavior regressions from macOS/MLX updates (DVFS residency
   makes it mechanistic); ~5-15 days; stronger with landed P2-009 rich telemetry.
7. **Teaching instrument** — a measurement-methodology lab course (idle
   subtraction, boundaries, uncertainty, negative results) with bundles
   as graded artifacts; ~5-12 days.
8. **Bundle contract as a standards contribution** — the run-bundle
   layout + boundary table + strict validator packaged as a proposed
   artifact format for edge-LLM energy (MLPerf-Power-adjacent); ~15-30
   days. Export the methodology; do not claim to BE the standard.

Deferred/killed applications: carbon LABELS (needs wall meter + grid
assumptions; see C5-2.9 for the surviving question), battery-runtime
estimates without system-level calibration, local-vs-cloud ROUTING as a
product (cloud side unmeasurable today).

exec
/bin/zsh -lc "rg -n -i \"\\bKDA\\b|GQA|grouped.query|sliding.window|full attention|attention variant|hybrid attention|linear attention|attention mechanism|num_key_value_heads|sliding_window\" docs configs joulewise tests pyproject.toml requirements* 2>/dev/null | head -n 400" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
zsh:1: no matches found: requirements*

exec
/bin/zsh -lc "rg -n -i \"\\bKDA\\b|GQA|grouped.query|sliding.window|full attention|attention variant|hybrid attention|linear attention|attention mechanism|num_key_value_heads|sliding_window\" docs configs joulewise tests pyproject.toml 2>/dev/null | head -n 500" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
tests/test_audit_cli_examples.py:177:                    "num_key_value_heads": 5,
tests/test_kv_size.py:32:            {"text_config": {"num_hidden_layers": 48, "num_key_value_heads": 2, "head_dim": 256}}
tests/test_kv_size.py:40:                "num_key_value_heads": 16,
tests/test_kv_size.py:44:                    "num_key_value_heads": 2,
tests/test_kv_size.py:55:                "text_config": {"num_hidden_layers": 28, "num_key_value_heads": 2},
tests/test_kv_size.py:65:                    "num_key_value_heads": 2,
tests/test_kv_size.py:75:                "num_key_value_heads": 2,
tests/test_kv_size.py:95:                "num_key_value_heads": 2,
tests/test_kv_size.py:107:                    "num_key_value_heads": 2,
tests/test_kv_size.py:120:                        "num_key_value_heads": 2,
docs/strategy/2026-08-06-impressiveness-roadmap.md:134:The KDA/speculative-decode/MTP/MoE program is instead governed by D-070/D-075 and the AXI contracts:
docs/strategy/2026-08-06-impressiveness-roadmap.md:146:- KDA/hybrid comparisons currently involve cross-model confounding and unverified long-context execution.
docs/strategy/2026-08-06-impressiveness-roadmap.md:148:- No tracked repository document uses “KDA” as a governed project axis; it appears in the nonbinding mechanism-literature sweep, not D-041.
docs/strategy/2026-08-06-impressiveness-roadmap.md:162:| **7** | **One mechanism-level study, conditional on a hard feasibility gate** | **Highest scientific ceiling.** A controlled batch-1 speculative-decode or MTP energy result could be genuinely novel; KDA/context slope or MoE routing is also interesting if attribution is identifiable. | **2–3-week desk feasibility gate; if passed, another 6–12 weeks and roughly 2 nights.** | New/forked runtime instrumentation, direct proposal/acceptance events, output identity/equivalence, mechanism-specific AP and floors. MTP currently cannot execute; KDA is confounded; MoE routing visibility is uncertain. | Pick exactly one mechanism and a kill date. Recommended first choice: external-draft speculative decode, because it offers the cleanest same-target on/off contrast if observability can be added. |
joulewise/kv_size.py:51:                "could not resolve num_key_value_heads or MHA fallback num_attention_heads"
joulewise/kv_size.py:57:            "num_attention_heads must be divisible by num_key_value_heads"
joulewise/kv_size.py:75:        n_kv_heads=_positive_int(n_kv_heads, "num_key_value_heads"),
joulewise/kv_size.py:151:    return _positive_int(value, "num_key_value_heads")
joulewise/kv_size.py:155:    primary = mapping.get("num_key_value_heads")
joulewise/kv_size.py:158:        primary_int = _positive_int(primary, "num_key_value_heads")
joulewise/kv_size.py:162:                "num_key_value_heads and num_kv_heads disagree; KV-head metadata is ambiguous"
docs/test_audit_2026-07-07.md:30:| K3 | should-fix | `joulewise/kv_size.py:extract_kv_params` | `multi_query: true` without KV-head count falls back to full attention heads. | `tests/test_audit_cli_examples.py::CliAndKVSizeBugPins.test_multi_query_true_uses_one_kv_head` (`expectedFailure`) |
docs/run_reports/2026-07-30-sweep-mechanisms.md:25:**Attention variants (GQA / MLA / linear / delta / hybrid)**
docs/run_reports/2026-07-30-sweep-mechanisms.md:26:- [arXiv 2605.11999](https://arxiv.org/abs/2605.11999) — GQA vs MLA vs Gated DeltaNet vs Mamba2 decode energy on H200. Key: decode draws only 137–300 W on a 700 W GPU across all variants (bandwidth-saturated before power-limited); clock locking recovers up to **32% of decode energy**; the linear/hybrid pattern shows heavy prefill recouped by cheap decode, **halving total request energy vs GQA** at production batch sizes.
docs/run_reports/2026-07-30-sweep-mechanisms.md:27:- [Kimi Linear / KDA, arXiv 2510.26692](https://arxiv.org/abs/2510.26692) — KDA (finer-gated DeltaNet) + MLA hybrid, 48B-A3B released; **75% KV-cache reduction, up to 6× decode throughput at 1M context**. Throughput/memory claims only — no measured energy.
docs/run_reports/2026-07-30-sweep-mechanisms.md:28:- Implied effect shape: full attention's J/token grows with context (KV reads); linear layers' does not. Nobody has published the on-device energy-vs-context *slope*.
docs/run_reports/2026-07-30-sweep-mechanisms.md:74:| 5 | Hybrid-linear vs full-attn: J/tok-vs-context slope | GQA slope from KV reads; linear ~flat; tens of % at 16–32k ctx | context-sweep design, per-point Δ ≥ 50–100 J | ~5–10× (**runtime risk**) |
docs/run_reports/2026-07-30-sweep-mechanisms.md:86:5. **Attention slope**: on-device d(J/tok)/d(context) for hybrid-delta vs full attention — 2605.11999 is H200-only and whole-request.
docs/stream_logs/2026-07-07-p2013-integrity.md:593:- **Decision:** `num_key_value_heads` and `num_kv_heads` may both appear
docs/stream_logs/2026-07-17-axes-foldin.md:62:| RQ-AXI-ATTN-KERNEL-AB | Duplicates runtime/kernel attribution and first requires a llama.cpp or equivalent adapter; a kernel toggle cannot identify an attention mechanism. |
docs/phase_3/phase_3_plan.md:65:expected transfer times). Derivation, for standard multi-/grouped-query
docs/run_reports/2026-07-30-sweep-techniques.md:35:The real methods quarry of the six. GQA/MLA/GDN/Mamba2 on one H200; NVML at 50 ms with trapezoidal integration; 10–20 reps, 3 warmups, medians with published max-stddev (≤3%, typically <0.5%).
docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:167:  "axis": "Transformer architecture variants (dense vs MoE vs hybrid/SSM-mixers) and attention mechanisms (GQA vs MLA vs sliding-window vs sparse) as energy-profile subjects, including whether attention-vs-FFN phase attribution is in scope of the current event model",
docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json:168:  "summary": "Sol's read-only high-effort assessment (bridge run 20260717T071639Z-74891, OK, valid envelope; lead checks replayed) splits this axis in two. The hybrid/SSM-mixer half is the valuable part: it stresses whether Q4's work coefficients survive when context-growing attention is replaced by recurrent state — a genuinely different stress than the already-committed MoE axis (conditional FFN activation, D-070) — and near-runnable subjects exist (Granite 4.0 H-Micro 3B vs Micro 3B as a named same-family hybrid/transformer pair; the state-spaces transformerpp/mamba2attn/mamba2 2.7B trio trained on the same 300B Pile tokens as the scientifically strongest but runtime-unverified design; Qwen3.5-4B DeltaNet-hybrid vs the already-mirrored Qwen3-4B GQA as a stack-generation contrast). The attention-mechanism half is currently weak: no MLA/GQA or SWA/full pair survives single-axis scrutiny (DeepSeek-V2-Lite MLA is confounded with MoE/size/tokenizer; Gemma generations change everything at once), llama.cpp's --swa-full is a cache-allocation toggle not an attention toggle, and --flash-attn is a kernel A/B not a mechanism A/B; sparse attention has no verified local execution path (Phi-3-small's block-sparse kernels are Triton/CUDA, NEEDS-WEB whether they actually execute on the fleet). On attribution: attention-vs-FFN time-slicing is OUT of scope of the landed event model — AXI-SA phases are request-lifecycle-level (phase_start/phase_end with request_phase_ordinal), powermetrics cadence cannot resolve per-layer intervals, and the RQ-SHORT-PREFILL-RESOLVABILITY precedent already rules out sub-cadence joule claims — so the honest designs are whole-request contrasts (nothing new needed) and fixed-output decode-phase context-length regressions whose context-associated slope must never be renamed an \"attention energy fraction\". Enrichment verdict medium overall: medium-high for the mixer sub-axis, low-medium marginal for attention mechanisms today since C5-1.2/RQ-KV-GROWTH already carry the context/KV-scaling question.",
docs/process_traces/2026-08-06-d079-issuance-coldgate/FABLE-COLD-PROCEED.jsonl:50:{"parentUuid":"bb94d8c8-c273-4b0c-9ae5-1b17e4ee5995","isSidechain":true,"agentId":"ad24a0f43262b600c","message":{"model":"claude-opus-4-8","id":"msg_011CdmC8Lu9j7mnUiYUmQgby","type":"message","role":"assistant","content":[{"type":"thinking","thinking":"","signature":"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"}],"stop_reason":null,"stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cache_creation_input_tokens":2053,"cache_read_input_tokens":68248,"cache_creation":{"ephemeral_5m_input_tokens":2053,"ephemeral_1h_input_tokens":0},"output_tokens":3,"service_tier":"standard","inference_geo":"not_available"},"diagnostics":null},"requestId":"req_011CdmC8KUpWvLB4hwu5vydF","attributionAgent":"general-purpose","type":"assistant","uuid":"8aa54256-6fcd-4069-83fb-24af267d03e4","timestamp":"2026-08-06T08:38:55.821Z","effort":"high","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:18:{"parentUuid":"f4593aea-dece-47d7-9c8f-04796e9bb788","isSidechain":true,"agentId":"a46e6644985dd75fd","message":{"model":"claude-opus-4-8","id":"msg_011CdmMavM5N4GRPUfQm14MP","type":"message","role":"assistant","content":[{"type":"thinking","thinking":"","signature":"EugHCokBCBAYAipAfkx5lOGOLkg3RO4FpGoSQpJiKQx+3pQ22jRZejaqjbQoe3edkDgobkcEogpfTjfe8NLAXXvQWjRVuDsM9UIEHzIPY2xhdWRlLW9wdXMtNC04OABCCHRoaW5raW5nWiRjYTM3M2E0YS1lOTJiLTRhZGYtYTkxNy0zZTQ1NWVjZGQ5ZmESDGJ88zyTawXWHYaGoBoMJCafJUnVj9Iig8CHIjC2BWy894QWtFu2c/pA1zxhYEGLwNTVw+fR209UrChNU46fXANHseoBWOr33WgUERYqiwZMxRV/sWQ1oswtMXcI85GI2Q3m0pvpmWUVnwMeoq2Fxo8UWWA4Kjg2OFIIkgLTaRpzEil422jFCnTCM+ku75L7+7cuy7CNMH+bM/oOcauuaTCA9Cwk7DnHX7bZi0r62q9VmY2H/j85cUft7/6n/lGypAuhO3Ueio9pUFsON8Pr1j5kdfcNeFF4WAmgczH2Aq9fdrgct73ONapID35jHf1wdxEz/exuAzaqeS+z93DTd6GPZtrBkNQeYHczLh/ifyEAWzZIXPttqHyDsVuy2fw2vlxdY5xWFi4QpbbRWhJrHrcD23z9/Uep6zDkdMt6Mv9IqhOe+pu3KWfDP/rjzcZgOainTdYEauQ+OjvnFzSsMDHyPV1belstVPF66MIuRi2pjiX015On2u6azxjGJqkzNLld4mp459wuzYzNql1dfexH/Qoa4W1Y8nW/mu0iq6CkHLq7cWRvX2aXzqoZ0ZlFH/zKpF5uxdwgK41aLx+bpGqaVhQIYY0JU6qEAGz5NC6JuQWTzfSTQCaucufys3Q7PXAicqgPBVrerd2pFXr+Mgn1/ZmRA2bgQq9unvZ0vx7UQn+vqr5TcIK8jfsYIYevrX+KSHHdnCFStITVCq2XkiSpPAcSIVulK7eGn+wnN3ndHczqXqJlfx9B3NsPYLsCWvaW/ldI/3yc4kOQSij7+qOLbJcy+wK/gX+2YMvPXWPHtIvahWmC215WqeTChgxY5RgPm+2TujMfpI0BTBP8ObJyqaklZ3Y2Kgi8C0DTj51v+J+CEz5XGUbQuZmMQHt0n+TssFncy0hgp90BZ2cjtBHotEmvycbOYCobi8hQchM5BMVPenyYxMASBUSF67DLHuJUAKze6/IkTqwjBfz05S/yroVkbApvk+OY8cvkjNFOwq8towCwkr1scZ90U9rc+icllleZd4ErqXZ08mOFXvLBTEWINKq9j5vsyqUNaIgUp6YG9KjcbnV3PnAFilmFTxuS5Gz8RB1VJoVJDo3aEQxVgnEwzykj3pfx/7KaF4iX98PGsXl1uPKp2RgB"}],"stop_reason":null,"stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cache_creation_input_tokens":1789,"cache_read_input_tokens":65733,"cache_creation":{"ephemeral_5m_input_tokens":1789,"ephemeral_1h_input_tokens":0},"output_tokens":2,"service_tier":"standard","inference_geo":"not_available"},"diagnostics":null},"requestId":"req_011CdmMau2wvQAk8XTFJhFMJ","attributionAgent":"general-purpose","type":"assistant","uuid":"b8a9f1b1-5246-4738-8e74-0cc5891eb9a8","timestamp":"2026-08-06T10:42:42.116Z","effort":"high","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:61:{"parentUuid":"8bcd9309-00a0-4b37-83c8-45c1d522c5d9","isSidechain":true,"agentId":"a46e6644985dd75fd","message":{"model":"claude-opus-4-8","id":"msg_011CdmMo43X5HujduVEko1gP","type":"message","role":"assistant","content":[{"type":"thinking","thinking":"","signature":"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"}],"stop_reason":null,"stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cache_creation_input_tokens":5829,"cache_read_input_tokens":88251,"cache_creation":{"ephemeral_5m_input_tokens":5829,"ephemeral_1h_input_tokens":0},"output_tokens":2,"service_tier":"standard","inference_geo":"not_available"},"diagnostics":null},"requestId":"req_011CdmMnzmpTJeaEbv6DEBhz","attributionAgent":"general-purpose","type":"assistant","uuid":"faca733b-932d-4d71-82c0-365cf375150d","timestamp":"2026-08-06T10:45:49.497Z","effort":"high","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:99:{"parentUuid":"d9dca5c0-ad6f-46c4-9b53-5cb84114835a","isSidechain":true,"agentId":"a46e6644985dd75fd","message":{"model":"claude-opus-4-8","id":"msg_011CdmNCut3ycsV4mDuwR72r","type":"message","role":"assistant","content":[{"type":"thinking","thinking":"","signature":"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"}],"stop_reason":null,"stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cache_creation_input_tokens":3550,"cache_read_input_tokens":121994,"cache_creation":{"ephemeral_5m_input_tokens":3550,"ephemeral_1h_input_tokens":0},"output_tokens":2,"service_tier":"standard","inference_geo":"not_available"},"diagnostics":null},"requestId":"req_011CdmNCu3SumhNvnYFRBiY9","attributionAgent":"general-purpose","type":"assistant","uuid":"3f7d4a09-bcb3-4f3f-8471-461e864267f2","timestamp":"2026-08-06T10:52:13.317Z","effort":"high","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}

exec
/bin/zsh -lc "sed -n '1,130p' docs/run_reports/2026-07-30-sweep-mechanisms.md; sed -n '140,190p' docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json; sed -n '1,120p' docs/run_reports/2026-07-30-sweep-techniques.md; rg -n \"D-070|D-075\" docs/decision_log.md | tail -n 20" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Related-work sweep — mechanism-level energy literature and candidate contrasts (2026-07-30)

**Origin:** delegated literature/landscape sweep, 2026-07-30 — Fable subagent
under the magistrate's 7B-floor-window session
(`abec37a6-31cd-4c56-a8a8-9448acaf12be`), agent `a83c5494c5a4c4533`. This file is the
agent's final deliverable message, extracted verbatim from the session
transcript; the raw JSONL transcript and the intermediate raw related-work
capture are session-scoped scratch and are deliberately NOT committed.

**Status:** desk research, not project evidence. Nothing here is a JouleWise
measurement, a claim, or a ratified decision. Adopted items become queue rows
or decision-log entries in their own right; see `TASK_QUEUE.md` intake batch
2026-07-30.

---

All verification done. Here is the deliverable.

---

# Mechanism-level energy literature sweep — reachability map for JouleWise

## (i) Mechanism-by-mechanism energy literature summary

**Attention variants (GQA / MLA / linear / delta / hybrid)**
- [arXiv 2605.11999](https://arxiv.org/abs/2605.11999) — GQA vs MLA vs Gated DeltaNet vs Mamba2 decode energy on H200. Key: decode draws only 137–300 W on a 700 W GPU across all variants (bandwidth-saturated before power-limited); clock locking recovers up to **32% of decode energy**; the linear/hybrid pattern shows heavy prefill recouped by cheap decode, **halving total request energy vs GQA** at production batch sizes.
- [Kimi Linear / KDA, arXiv 2510.26692](https://arxiv.org/abs/2510.26692) — KDA (finer-gated DeltaNet) + MLA hybrid, 48B-A3B released; **75% KV-cache reduction, up to 6× decode throughput at 1M context**. Throughput/memory claims only — no measured energy.
- Implied effect shape: full attention's J/token grows with context (KV reads); linear layers' does not. Nobody has published the on-device energy-vs-context *slope*.

**Speculative decoding**
- [arXiv 2504.17674](https://arxiv.org/abs/2504.17674) (Energy Considerations of LLM Inference; full numbers via HTML) — spec decode: **−29.14% energy at batch ≤16, +25.65% at batch 128** (verify overhead dominates when compute-saturated). Combined optimizations: up to 73% total reduction.
- [TokenPowerBench, arXiv 2512.03024](https://arxiv.org/html/2512.03024v1) — J/token, J/response metrics; corroborates ~29% small-batch savings.
- [Survey 2411.13157](https://arxiv.org/abs/2411.13157) — latency-only; **no energy numbers** in the survey. Batch-1 on-device (the regime where spec decode should help most) has *no published energy measurement anywhere I found*.

**Multi-token prediction (MTP)**
- No measured energy results found at all — only speedup claims (2–3×, e.g. [FastMTP](https://openreview.net/forum?id=J7xDwZSyI4), [vLLM MTP docs](https://docs.vllm.ai/en/latest/features/speculative_decoding/mtp/)). Open checkpoints with MTP heads: [MiMo-7B](https://deepwiki.com/XiaomiMiMo/MiMo/2.2-multiple-token-prediction), DeepSeek-V3, Qwen3-Next.

**MoE (routing, expert count, shared experts)**
- [arXiv 2606.21428](https://arxiv.org/abs/2606.21428) — **the one Apple-silicon paper**: OLMoE-1B-7B vs Llama-3.2-1B on M2 Pro + Jetson. MoE = **2.1× energy/token on Jetson**, ~10% behind on M2 Pro; **routing itself is <9% of MoE-block compute** — the penalty is total-parameter footprint, dispatch, KV pressure.
- [arXiv 2504.17674](https://arxiv.org/abs/2504.17674) — MoE **+54.24% energy vs dense OLMo-1B at matched active params** (A100-class).
- [Where Do the Joules Go, arXiv 2601.22076](https://arxiv.org/html/2601.22076v1) — opposite regime: MoE **3.56× less energy** than dense of similar *total* params (H100/B200, vLLM, large batch). The dense-baseline convention (matched-active vs matched-total) flips the sign — a point of genuine confusion the literature hasn't resolved cleanly.

**KV cache (size, quantization, paging)**
- [KVQuant 2401.18079](https://arxiv.org/pdf/2401.18079), [SKVQ 2405.06219](https://arxiv.org/pdf/2405.06219), [KV-compression review 2508.06297](https://arxiv.org/html/2508.06297v1) — 4.8× compression, latency wins, up to ~7× theoretical speedup at 200k ctx — **all memory/latency; zero measured J/token anywhere**. 2601.22076 shows KV pressure raises energy/token 1.5–2.1× indirectly (batch limiting).

**Weight quantization**
- [arXiv 2504.03360](https://arxiv.org/pdf/2504.03360) (edge), [Price of Prompting 2407.16893](https://arxiv.org/pdf/2407.16893) — 4-bit gains **1.35–2.95×** total energy vs unquantized; one edge benchmark shows Llama-3.2-1B fp16=159 J/tok, q8=76, q4≈84 (q4 *worse* than q8 — dequant-bottleneck anomaly worth testing). Caveat everywhere: savings require hardware-native low-precision paths.

## (ii) Concrete measurable pairs (runtime status)

| Contrast | Arm A | Arm B | 4-bit size | Runtime status |
|---|---|---|---|---|
| Spec decode on/off | Qwen2.5-7B (or Qwen3-8B) alone | same + 0.5B/0.6B draft | ~4.4 GB | **Verified**: `mlx_lm.generate --draft-model` exists ([issue #250](https://github.com/ml-explore/mlx-lm/issues/250), [#1132](https://github.com/ml-explore/mlx-lm/issues/1132)) |
| Weight quant ladder | model-4bit | same model 8bit / bf16 | 4–16 GB | **Verified** (mlx-community ships all levels) |
| KV-cache quant | `--kv-bits 4` | fp16 cache | same model | **Verified**: kv quantization in mlx-lm ([mlx-examples #1075](https://github.com/ml-explore/mlx-examples/commit/85ffd2c)) |
| MoE vs dense (matched active, same family) | mlx-community/Qwen3-30B-A3B-4bit (**verified exists**) | Qwen3-4B-4bit | ~17 GB vs ~2.3 GB | Qwen3-MoE runs widely in mlx-lm (checkpoint verified; arch file not individually confirmed — *low risk*) |
| MoE vs dense (lit-comparable) | OLMoE-1B-7B (`olmoe.py` **verified in mlx-lm**) | OLMo-2-1B / Llama-3.2-1B | ~4 GB | Verified arch file; replicates 2606.21428's exact pair |
| Hybrid delta-attention | mlx-community/Kimi-Linear-48B-A3B-Instruct-4bit (**verified exists**; `kimi_linear.py` **verified in mlx-lm**) | Qwen3-30B-A3B (full-attn MoE, similar active) | ~27 GB | Cross-model confound; long-context stability in MLX **unverified** |
| Hybrid GDN | mlx-community/Qwen3-Next-80B-A3B-Instruct-4bit (**verified exists**; `gated_delta.py` in mlx-lm) | Qwen3-30B-A3B | ~45 GB | **Unverified** end-to-end |
| MoE top-k knob | Qwen3-30B-A3B, `num_experts_per_tok=8` | same checkpoint, k=4 (config edit) | same weights | **Unverified but mechanically plausible** — single-mechanism, same-weights knob |
| MTP | MiMo-7B-Base (heads in checkpoint) | — | — | **Not reachable**: no MLX MTP support (vLLM only) |
| RWKV / RecurrentGemma / Zamba | — | — | — | **Not in mlx-lm** — drop |

## (iii) Ranked reachable claims — effect/floor arithmetic

Baseline: 7B-4bit decode = 0.376 J/tok, 1.5B = 0.098 J/tok (JouleWise measured). Floor: 6–14 J now, ~2–5 J after tightening. Workload 512–8192 tok.

| Rank | Contrast | Effect estimate | Δ at feasible workload | Effect/floor (14 J) |
|---|---|---|---|---|
| 1 | Weight quant 4b vs 8b (7B) | +60–90% J/tok (bandwidth ∝ bytes) → Δ≈0.22–0.34 J/tok | ×2048 tok ≈ **450–700 J** | **~35–50×** |
| 2 | Spec decode on/off (7B+0.5B) | ±10–30% → Δ≈0.04–0.11 J/tok | ×2048 ≈ **80–230 J** | **~6–16×** |
| 3 | MoE vs dense matched-active | +30–100% of ~0.1–0.15 J/tok dense | ×2048 ≈ **60–300 J** | **~5–20×** |
| 4 | KV-quant 4b vs fp16, long ctx | Qwen2.5-7B KV ≈57 KB/tok fp16 → ~9.6% of decode bandwidth at 8k ctx; save ~75% of it ≈ 3.5% avg over 0→8k | ×8192 ≈ **~100 J** (concentrated late — phase resolution helps) | **~7×** at full 8k; marginal below 4k |
| 5 | Hybrid-linear vs full-attn: J/tok-vs-context slope | GQA slope from KV reads; linear ~flat; tens of % at 16–32k ctx | context-sweep design, per-point Δ ≥ 50–100 J | ~5–10× (**runtime risk**) |
| 6 | MoE top-k slope (same weights) | expert-FFN energy ~∝ k; maybe 20–40% of J/tok | ×2048 ≈ 100–250 J | ~10× (**mechanism knob unverified**) |
| — | MTP | — | — | **unreachable** (no runtime) |

All effect estimates except row 1's bandwidth scaling are extrapolations from server-class literature — flagged as such; that gap is the point.

## (iv) What each claim says that the literature can't

1. **Spec decode**: "On batch-1 unified-memory inference, speculative decoding changes decode energy by X% ± CI" — first *measured* on-device energy verdict incl. the **sign** (all lit is server GPU batch sweeps; mlx overhead could plausibly flip it — issue #250 hints the spec-decode step is slower).
2. **Quantization**: CI-bounded J/token-vs-bits curve on Apple silicon, adjudicating the q4>q8 anomaly the edge literature reports without error bars.
3. **MoE**: whether the +54% matched-active GPU penalty survives unified memory, phase-resolved — direct extension of 2606.21428 (M2 Pro, one pair, coarse) with the sign-flip (matched-active vs matched-total) pinned down on one instrument.
4. **KV quant**: the first measured energy number of any kind — lit has only memory/latency.
5. **Attention slope**: on-device d(J/tok)/d(context) for hybrid-delta vs full attention — 2605.11999 is H200-only and whole-request.

## Top-3 recommended first campaigns

1. **Speculative decoding on/off (Qwen2.5-0.5B→7B, models already characterized)** — cleanest single-mechanism ABBA in existence (identical target weights, flag-toggled), verified runtime, open sign question, 6–16× floor clearance.
2. **Weight-quant ladder (Qwen 7B/8B at 4/8/16-bit)** — 35–50× floor clearance, checkpoints trivially available, and it calibrates the bytes-moved→joules model every other campaign's predictions rest on.
3. **MoE vs dense matched-active (Qwen3-30B-A3B vs Qwen3-4B, plus the OLMoE/OLMo-2 lit-replication pair)** — settles the matched-active vs matched-total sign flip on unified memory and directly extends the only existing Apple-silicon result.

Sources: [2605.11999](https://arxiv.org/abs/2605.11999) · [2504.17674](https://arxiv.org/abs/2504.17674) · [2606.21428](https://arxiv.org/abs/2606.21428) · [2411.13157](https://arxiv.org/abs/2411.13157) · [2510.26692](https://arxiv.org/abs/2510.26692) · [2601.22076](https://arxiv.org/html/2601.22076v1) · [2512.03024](https://arxiv.org/html/2512.03024v1) · [2504.03360](https://arxiv.org/pdf/2504.03360) · [2401.18079](https://arxiv.org/pdf/2401.18079) · [2405.06219](https://arxiv.org/pdf/2405.06219) · [mlx-lm models](https://github.com/ml-explore/mlx-lm/tree/main/mlx_lm/models) · [mlx-lm #250](https://github.com/ml-explore/mlx-lm/issues/250) · [mlx-lm #1132](https://github.com/ml-explore/mlx-lm/issues/1132) · [mlx-examples #1075](https://github.com/ml-explore/mlx-examples/commit/85ffd2c96a45a8cb900f95a2ded61d858d673399)  "candidate_rows": [
   {
    "id_suggestion": "C5-2.5/MTP-MAC",
    "question": "For one exact target artifact and output policy on the M3 Max, how does native MTP change gross request energy, gross J per committed output token, and accepted-proposal yield versus spec-off?",
    "ceiling": "L2, stack-conditioned (D-070 cap)",
    "forbidden_upgrade": "No efficiency claim without exact output identity (C-023-OUTPUT-IDENTITY), runtime-observed loaded MTP heads, and accepted/proposed accounting per token_normalization.md; committed-burst length is never the accepted-token denominator."
   },
   {
    "id_suggestion": "C5-2.5/MECHANISM",
    "question": "Does eliminating the separate drafter model (native MTP vs DSpark vs DFlash external drafters) change the Q4 fixed-vs-work energy decomposition — i.e., is the external drafter's residency a measurable fixed-cost term?",
    "ceiling": "L2",
    "forbidden_upgrade": "No component-level energy attribution and no 'zero-cost drafting' language — MTP heads still add resident parameters and verification compute; no pooling of mechanisms in one AP-SPEC registry (contract permits exactly one enabled mechanism per registry; cross-mechanism contrast needs a new prospective design)."
   },
   {
    "id_suggestion": "C5-2.5/MTP-DEPTH",
    "question": "Within one pinned artifact and runtime, how do MTP head-count/draft-depth policies change acceptance rate and gross request energy?",
    "ceiling": "L2",
    "forbidden_upgrade": "No optimal-depth or scheduler-policy claim from a post-hoc sweep; no cross-architecture depth comparison until candidate-position counting semantics (heads/depth/tree topology to linear proposed positions) are frozen — the contract deliberately does not derive tokens_proposed from head_count x draft_depth."
   }
  ],
  "enrichment_score": "medium",
  "feasibility": "Mac/MLX today: NOT runnable for native MTP. Grounded locally (stronger than Sol's NEEDS-WEB — Sol missed the repo venv): pinned mlx-lm 0.31.3 at /Users/edr/code/JouleWise/.venv/.../mlx_lm strips MTP weights at load — qwen3_next.py:455 drops all \"mtp.\" keys, mimo_v2_flash.py:364 drops \"model.mtp*\", mimo.py:189 drops \"model.mtp_layers.\" — so MTP-bearing architectures (Qwen3-Next, MiMo) load as plain causal LMs with heads discarded. The same mlx-lm DOES ship external-draft speculative decoding (generate.py:473 speculative_generate_step), and the vendored mlx-dspark clone (/Users/edr/code/mlx-dspark-vendor, verified at 2facf791) implements DSpark+DFlash but has no native-MTP path — so the Mac burst-decode leg is served by external-draft mechanisms today. Whether any newer mlx-lm release or third-party MLX project executes MTP heads at inference: NEEDS-WEB. 3080 Ti (12 GiB): the only named MTP-bearing model that plausibly fits is Xiaomi MiMo-7B quantized (model knowledge, unverified); DeepSeek-V3, Qwen3-Next-80B, and GLM-4.5-class do not fit 12 GiB; vLLM MTP-method support and per-round proposed/accepted counter hooks for the pinned vllm_runtime adapter: NEEDS-WEB. Mac 128 GB fits Qwen3-Next/GLM-Air-class quantized memory-wise, but that is moot without an MLX MTP execution path. AMD/other: outside the D-073 fleet, not evaluated. Note: the concurrently running AXI-SC spike (worktree JouleWise-wt/axi-sc) is probing exactly mlx-lm 0.31.3 spec/MTP observability; my grounding predicts its verdict = external-draft supported, native-MTP unsupported.",
  "harness_difficulty": "The landed AXI-SA surface already carries native MTP as a first-class mode, deeper than schema-only: SpeculationPolicy mode enum {off, draft_model, native_mtp} with cross-field null rules and the native-target-hash-equals-runtime-hash invariant (joulewise/axi_decode_config.py:217-241, 664); mode-agnostic proposed/accepted/emitted counter validation identical for both enabled mechanisms (axi_decode_config.py:488-497; contract line 406 'exactly the same proposal and acceptance semantics'); DecodeCounterRollup + gross_energy_per_accepted_draft_token_j in reducer 0.6.0 (joulewise/schemas.py:1564-1700); dedicated registry IDs ap_spec_native_mtp_front_v1/_campaign_v1 and family FAM-AXI-SPEC-NATIVE-MTP-MATCHED-OUTPUT (sa_burst_decode_contract.md:853-856); native-MTP fixtures and ~27 native_mtp test references plus the mock spec adapter. What is missing is entirely runtime-side: (1) an MLX decode primitive that actually executes MTP heads with per-round counters — new-subsystem scale on the Mac today since pinned mlx-lm strips the heads (drops to one-session adapter work only if an upstream primitive appears); (2) a live adapter emitting AxiDecodeEmission/AxiRuntimeResult for the mechanism — session-scale on CUDA if vLLM exposes hooks (NEEDS-WEB); (3) runtime-observed head provenance (loaded MTP tensor inventory validated against NativeMTPIdentity) — currently the adapter could assert native_mtp over a stripped artifact and pass validation, a real gap Sol identified; (4) a frozen candidate-position counting rule for head/depth/tree topologies (head_count, draft_depth, head_configuration are currently opaque positives). Per-head acceptance evidence would need an events.v2 successor (exact-keyed metadata) or a raw sidecar.",
  "risks": "Axis-killers: MLX never lands MTP-head execution for a fleet-fitting artifact (the pinned runtime demonstrably discards the heads today); released/converted checkpoints omit or strip auxiliary heads so even a willing runtime has nothing to execute; heads prove to be training-only auxiliaries with acceptance too low to clear P2-015 energy floors. Embarrassment modes: adapter asserts native_mtp identity over a stripped artifact and passes validation (no runtime-observed head provenance yet); H x D or committed-burst length mistaken for the proposed/accepted denominators — including the vendored mlx-dspark trap where public accept_lengths stores committed (accepted+bonus) tokens (Sol's unique catch: x_mlx_dspark is NOT valid C5-2.5 accounting as-is); DSpark conflated with native MTP because both are DeepSeek-associated (DSpark is a separate semi-autoregressive drafter, mode=draft_model under the contract's artifact-locus rule); 'no separate drafter' promoted to 'no extra residency/compute'; mechanism results pooled across DSpark/DFlash/MTP despite the one-mechanism-per-registry rule; Mac results generalized to the 3080 Ti despite disjoint model fits. Process risk: the axis's Mac leg could consume a spike/adapter budget and still return runtime_unavailable — the AXI-SB mint-on-supported-verdict pattern (and the in-flight AXI-SC spike) is the right containment.",
  "summary": "Native MTP is the best-covered and least-runnable of the burst-decode mechanisms: the landed AXI-SA contract already treats it as a first-class speculation mode with its own identity object, registry IDs, family, fixtures, and identical counter semantics to external-draft, so essentially zero new contract surface is needed — but no reachable runtime executes MTP heads today. The decisive grounded fact (which Sol flagged NEEDS-WEB and I resolved at the bench): pinned mlx-lm 0.31.3 in the repo venv strips MTP weights at model load for every MTP-bearing architecture it ships (qwen3_next, mimo, mimo_v2_flash), while fully supporting external-draft speculation — so the Mac leg's characterized burst-decode claims should route to DSpark/DFlash now, with native MTP held as a gated feasibility row. The scientific case for keeping it is real and Q4-shaped: self-drafting removes the external drafter's residency and forwards, making the drafter's fixed-cost term the experimental variable — the cleanest mechanism-level stress of E = fixed + coefficients*work in the whole speculation axis. The C5-2.5 denominator story survives intact under native MTP (proposed = realized candidate positions submitted to verification, never head_count x draft_depth; accepted excludes the bonus token; J/accepted-token stays a spec-on-only mechanism-yield diagnostic with no drafter-energy attribution possible or claimed), with one naming caution: report language should say 'accepted proposal (draft/MTP) token'. Fleet-wise, MiMo-7B is the only named candidate plausibly spanning both legs (model knowledge, unverified); the 12 GiB CUDA cap eliminates DeepSeek-V3/Qwen3-Next/GLM-class. Ranking for the Mac leg: DSpark first, DFlash second, native MTP third as a four-gate spike (heads in source weights, retained through conversion, executed with round counters, exact-output on/off smoke). Enrichment is medium: high distinctness but low near-term askability, and the in-flight AXI-SC spike will supply the authoritative mlx-lm verdict either way."
 },
 {
  "axis": "Transformer architecture variants (dense vs MoE vs hybrid/SSM-mixers) and attention mechanisms (GQA vs MLA vs sliding-window vs sparse) as energy-profile subjects, including whether attention-vs-FFN phase attribution is in scope of the current event model",
  "summary": "Sol's read-only high-effort assessment (bridge run 20260717T071639Z-74891, OK, valid envelope; lead checks replayed) splits this axis in two. The hybrid/SSM-mixer half is the valuable part: it stresses whether Q4's work coefficients survive when context-growing attention is replaced by recurrent state — a genuinely different stress than the already-committed MoE axis (conditional FFN activation, D-070) — and near-runnable subjects exist (Granite 4.0 H-Micro 3B vs Micro 3B as a named same-family hybrid/transformer pair; the state-spaces transformerpp/mamba2attn/mamba2 2.7B trio trained on the same 300B Pile tokens as the scientifically strongest but runtime-unverified design; Qwen3.5-4B DeltaNet-hybrid vs the already-mirrored Qwen3-4B GQA as a stack-generation contrast). The attention-mechanism half is currently weak: no MLA/GQA or SWA/full pair survives single-axis scrutiny (DeepSeek-V2-Lite MLA is confounded with MoE/size/tokenizer; Gemma generations change everything at once), llama.cpp's --swa-full is a cache-allocation toggle not an attention toggle, and --flash-attn is a kernel A/B not a mechanism A/B; sparse attention has no verified local execution path (Phi-3-small's block-sparse kernels are Triton/CUDA, NEEDS-WEB whether they actually execute on the fleet). On attribution: attention-vs-FFN time-slicing is OUT of scope of the landed event model — AXI-SA phases are request-lifecycle-level (phase_start/phase_end with request_phase_ordinal), powermetrics cadence cannot resolve per-layer intervals, and the RQ-SHORT-PREFILL-RESOLVABILITY precedent already rules out sub-cadence joule claims — so the honest designs are whole-request contrasts (nothing new needed) and fixed-output decode-phase context-length regressions whose context-associated slope must never be renamed an \"attention energy fraction\". Enrichment verdict medium overall: medium-high for the mixer sub-axis, low-medium marginal for attention mechanisms today since C5-1.2/RQ-KV-GROWTH already carry the context/KV-scaling question.",
  "harness_difficulty": "Landed and sufficient for whole-request contrasts: gross_request/gross_batch_group window classes, events v2 with request-scoped phases and decode_emission (docs/specs/axi/sa_burst_decode_contract.md §§1-4), reducer 0.6.0, model/quant/artifact identity in ModelConfig (joulewise/schemas.py:349) plus MLX adapter runtime capture (joulewise/adapters/mlx_runtime.py:148), and — importantly — the stack-identity table already reserves 'Kernel/library where known: attention implementation' (docs/contracts/token_normalization.md:132), so attention-mechanism identity has a contractual home. The joulewise.axi_decode_config.v1 extension (joulewise/axi_decode_config.py) covers only batch_policy and speculation — it carries no architecture-taxonomy fields, and unknown config keys do not enter normalized identity (schemas.py extension handling), so an auditable architecture manifest (mechanism, layer pattern, Q/KV heads, trained window, SSM type, source-config digest) is new surface: bench-size if kept as campaign-side selection evidence, session-size if promoted into normalized metadata. Context-sweep regression designs are session-size and largely reuse C5-1.2/RQ-KV-GROWTH machinery plus an analysis plan. A matched-quant conversion + S-D-style G1-G10 receipts for a hybrid pair is session-size. Attention-vs-FFN module attribution is NOT in scope of the current event model: request-level phases cannot be relabeled module phases, and adding per-layer markers would not create power samples at per-layer timescales (powermetrics cadence; RQ-SHORT-PREFILL-RESOLVABILITY precedent, docs/research_question_registry.md:60) — module-isolating synthetic microbenchmarks or per-layer instrumentation are each a new subsystem, and the latter may remain unsuitable even after instrumentation. A llama.cpp adapter for the 3080 Ti is multi-session: RuntimeBackend.LLAMA_CPP exists (joulewise/schemas.py:184) but resolve_runtime has no branch for it (joulewise/adapters/__init__.py:147-150, verified).",
  "feasibility": "Mac/MLX today: strongest leg. Falcon-H1 hybrids have MLX-LM support and mlx-community 4-bit artifacts (Sol web memo, huggingface.co/mlx-community/Falcon-H1-3B-Instruct-4bit); Granite 4.0 hybrid (Mamba2/attention) MLX and GGUF artifacts exist per IBM/HF cards, though same-recipe conversion receipts are still needed; DeepSeek MLA support is in current MLX-LM releases (~8.8 GB 4-bit V2-Lite fits the 128 GB Mac easily); Qwen3-4B-4bit and Qwen3.5-122B-A10B-4bit are already mirrored locally under /Users/edr/jw_models/mlx-community/. The state-spaces controlled trio is NEEDS-WEB + load-smoke: only mamba2-2.7b was confirmed in an mlx-community collection; generic mlx-lm loadability of transformerpp/mamba2attn under one pinned revision is unverified. 3080 Ti (12 GiB, D-073): JouleWise's only CUDA path today is the vLLM adapter over the node-worker protocol (joulewise/adapters/__init__.py:135-146) — no llama.cpp adapter exists despite the enum, so GGUF-based attention/hybrid subjects are not yet a campaign path on that node; DeepSeek-V2-Lite at 12 GiB is borderline (NEEDS-WEB/load verification). Sparse attention: no credible fleet path — Phi-3-small's documented block-sparse kernels target Triton/CUDA and actual sparse execution under local runtimes is NEEDS-WEB; a dense fallback must not be labeled a sparse-attention measurement. AMD/other: no adapter surface at all; out of scope per D-073 fleet posture. Same-artifact toggles: llama.cpp --flash-attn on|off is a genuine kernel A/B; --swa-full changes SWA cache allocation, not the mask; MLX-LM --max-kv-size is a rotating-cache policy, not a mechanism toggle; no MLA weight-absorption or SWA-mask-disable flag was established (NEEDS-WEB/source audit at the pinned revision).",
  "candidate_rows": [
   {
    "id_suggestion": "RQ-AXI-HYBRID-PAIR",
    "question": "For one predeclared, gate-passing hybrid(SSM/attention)-vs-pure-transformer pair (leading candidate: Granite 4.0 H-Micro 3B vs Micro 3B; preferred if runtime-enabled: the state-spaces 2.7B same-corpus trio) under matched runtime, quantization recipe, prompts, and output policy, how do gross request and decode-phase energy differ across governed context lengths?",
    "ceiling": "L2 pair-specific characterization (D-070 clause 5)",
    "forbidden_upgrade": "No architecture-class efficiency generalization, no causal SSM-mechanism attribution, and no tokenizer-blind ranking from one named model pair; 'this named pair' wording binding per the S-D scorecard idiom."
   },
   {
    "id_suggestion": "RQ-AXI-ATTN-CONTEXT-SLOPE",
    "question": "Within each named artifact, how does fixed-decoded-output decode-phase gross energy change with initial context length, and are slope/saturation regimes (full-attention growth vs SWA/SSM saturation) repeatable above the P2-015 floor?",
    "ceiling": "L2 boundary-labeled regression characterization",
    "forbidden_upgrade": "No conversion of the context-associated coefficient into an attention-vs-FFN energy fraction, per-token rail claim, or module-level attribution; composes with C5-1.2/RQ-KV-GROWTH chunked-window limits rather than superseding them."
   },
   {
    "id_suggestion": "RQ-AXI-ATTN-KERNEL-AB",
    "question": "For one artifact and pinned runtime build, does a documented attention-kernel toggle (e.g. llama.cpp --flash-attn on|off) change gross request energy while C-023-OUTPUT-IDENTITY equivalence gates pass?",
    "ceiling": "L2 same-stack A/B characterization",
    "forbidden_upgrade": "No attention-mechanism, cross-runtime, cross-hardware, or architecture-class efficiency conclusion from a kernel-implementation toggle; gated on the 3080 Ti leg acquiring an actual llama.cpp or equivalent adapter."
   },
   {
# Related-work sweep — metrology technique extraction (2026-07-30)

**Origin:** delegated literature/landscape sweep, 2026-07-30 — Fable subagent
under the magistrate's 7B-floor-window session
(`abec37a6-31cd-4c56-a8a8-9448acaf12be`), agent `ad4442c056ee24f5c`. This file is the
agent's final deliverable message, extracted verbatim from the session
transcript; the raw JSONL transcript and the intermediate raw related-work
capture are session-scoped scratch and are deliberately NOT committed.

**Status:** desk research, not project evidence. Nothing here is a JouleWise
measurement, a claim, or a ratified decision. Adopted items become queue rows
or decision-log entries in their own right; see `TASK_QUEUE.md` intake batch
2026-07-30.

---

All three deep-read agents have reported with full-text access to every work (one via an archived mirror, plus the SPEC methodology doc that holds the actual PTDaemon numbers). Consolidated deliverable follows.

# JouleWise metrology deep-read: technique extraction

Access summary up front: **all six works read in full text.** TokenPowerBench, Illusion of Power Capping, MLPerf Power, Paired-MDE, and Beginner's Guide via arXiv HTML/PDF; RAPL in Action via an archived accepted-manuscript mirror (ACM DL paywalled); Jay/Ostapenco via the ENS-Lyon author PDF (HAL file link blocked). The MLPerf numeric thresholds live in the SPEC Power & Performance Methodology (June 2025), which was also read. Two unverified minor items: SPEC's accepted-device list details and MLPerf-tiny instrument models.

---

## 1. TokenPowerBench (arXiv 2512.03024, AAAI'26) — [abs](https://arxiv.org/abs/2512.03024) · [full HTML](https://arxiv.org/html/2512.03024)

**Adopt/adapt:** (i) Double decomposition of E_total — by phase (Eq. 1) AND by hardware component (Eq. 2) — as a reporting skeleton; powermetrics' CPU/GPU/ANE/DRAM channels enable a cheap internal-consistency gate (channel sum vs package energy). (ii) Context-length binning (0–2K/2K–5K/5K–10K) for J/token instead of one scalar. (iii) Their metric family (energy/token, energy/response, energy/second, peak power, prefill energy) as a report-column checklist.

**Reporting that works:** per-phase J/token comparisons with per-phase denominators (input tokens for prefill, output tokens for decode) — field-standard normalization.

**Avoid (this paper is a metrology cautionary tale):** phase tagging asserted but never specified — "each power sample is tagged with the active stage" is the *entire* disclosed mechanism (no boundary event, no alignment rule, no tag-timing error; confirmed absent on two independent reads). No sampling rate stated anywhere. Zero repetitions/variance/error bars. No idle baseline, no external validation, continuous-batching overlap silently ignored. Key reframe for JouleWise: **its "single-request sequential only" restriction is what makes phase attribution well-defined — present it as a scoping decision, not just a weakness.** JouleWise's pulse-train calibration is precisely what this paper lacks.

## 2. The Illusion of Power Capping in LLM Decode (arXiv 2605.11999) — [abs](https://arxiv.org/abs/2605.11999) · [full HTML](https://arxiv.org/html/2605.11999)

The real methods quarry of the six. GQA/MLA/GDN/Mamba2 on one H200; NVML at 50 ms with trapezoidal integration; 10–20 reps, 3 warmups, medians with published max-stddev (≤3%, typically <0.5%).

**Adopt/adapt:** (i) **Internal dual-instrument cross-validation**: they validate sampled-power integrals against the independent NVML hardware energy counter and publish the agreement bound (2%, valid only for ops ≥200 ms). JouleWise's pre-wall-meter analogue: cross-check powermetrics integrals against an independent on-device channel (battery/SMC drain deltas over long windows) and publish the number with its validity domain. (ii) **Duration-conditional validity**: they name where the method breaks (<100 ms), the affected fraction (44% of prefill configs), and a declared fallback — slots directly into JouleWise's fail-closed gates as a minimum-window rule in units of powermetrics cadence. (iii) **Effect/noise ratio as a standard column** ("spread exceeds noise by 1.2–27×") plus their extra move: distinguishing "above floor" from "operationally meaningful." (iv) **Weight-controlled ablation** (same base weights, one variable changed via TransMLA) — for any JouleWise A/B, hold everything bit-identical and say so. (v) Max-stddev printed in figure captions. (vi) Mechanistic corroboration (rooflines) — corroborate energy splits with powermetrics' utilization/frequency channels so claims aren't single-signal. (vii) Pareto-frontier operating-point template.

**Reporting that works:** mJ/token separately per phase; energy–throughput Pareto scatter where an ineffective knob shows as a degenerate blob; crossovers reported as (batch, seq) coordinates; explicit limitations list.

**Avoid / JouleWise's open lane:** they never compose their error terms (2% counter agreement, ≤3% stddev, unquantified snapshot-fallback error, 50 ms alignment) into a bound on the headline 24–32% savings; no drift control across hours-long sweeps (thermal drift aliases into the clock axis — exactly what ABBA prevents); median + ±1 s.d. mismatch; microbenchmarked phases ≠ in-situ phases. **Nobody yet measures phase energy in situ with quantified attribution error — that combination is JouleWise's differentiator.**

## 3. RAPL in Action (TOMPECS '18) + Jay/Ostapenco (CCGRID '23) — [RAPL mirror](https://web.archive.org/web/2024id_/https://scispace.com/pdf/rapl-in-action-experiences-in-using-rapl-for-power-29ewz97e1j.pdf) · [CCGRID PDF](https://perso.ens-lyon.fr/laurent.lefevre/pdf/CCGRID2023_Ostapenco_Jay_Lefevre.pdf) · [HAL](https://inria.hal.science/hal-04030223) · [artifact](https://github.com/vladostp/an-experimental-comparison-of-software-based-power-meters)

**Adopt/adapt (Khan):** model-based validation, not identity: fit wall = f(software channels), report MAE/RMSE/MAPE on held-out data with channel ablation (Haswell GAM: 1.7% MAPE — the literature benchmark for "good"). Lag-hunt via cross-correlation before comparing streams (they found 10–24 s lags). Autocorrelation-aware stats (subsample/block before fitting). ≥2-min warm-up (kills a ~10–12% thermal power drift they measured, 37→74 °C). Instrument-overhead audit (with/without sampler; <1.2% even at 1 kHz). And the **counter-mechanics checklist** — overflow period, update granularity/jitter, non-atomicity, missing timestamps — is exactly the audit nobody has run on powermetrics' internal counters.

**Adopt/adapt (Jay/Ostapenco):** closest published template for the powermetrics-vs-wall study: fixed machine config, N=10 reps, 1-min cooldowns, component-targeted workloads (their compute/memory/mixed maps to decode-heavy/prefill-heavy/idle), automated + published artifact. Resample-then-correlate, **then regress with wall as response** — their headline: slope 1.17–1.18, i.e. the software-vs-wall gap is load-dependent, **never a constant offset**, and must be characterized per node. Their §V-C2 honesty: refuse to rank where no reference exists — the wall meter validates *totals only*; phase splits stay validated only by the pulse-train method and should be labelled so. Disclose campaign energy (theirs: ~480 kWh).

**Avoid:** consumer-grade reference with no stated accuracy class (Khan's Plugwise, internally inconsistent 0.1 vs 10 Hz); publishing accuracy claims where no reference exists (Khan's EC2 arm); leading with Pearson r (0.95–0.99 doesn't discriminate — slope/intercept/MAPE do); reference sampling slower than the tool under test (CCGRID's 1 Hz reference was their binding constraint); trusting embedded telemetry (BMC/SMC) as a second reference without characterization.

## 4. MLPerf Power (arXiv 2410.12032) + SPEC methodology — [full HTML](https://arxiv.org/html/2410.12032v2) · [SPEC PDF](https://www.spec.org/power/docs/SPEC-Power_and_Performance_Methodology.pdf) · [MLC power rules](https://raw.githubusercontent.com/mlcommons/inference_policies/master/power_measurement.adoc)

What their rules would demand of a laptop measurement: analyzer with **computed overall uncertainty <1% AC / <1.5% DC at your actual load** (formula: %-of-reading×P + digit counts, ÷P), NIST-traceable calibration within a year, crest-factor capability ≥3 (and an explicit warning that adapters **<75 W have high crest factors** that inflate meter error — exactly the Apple-silicon regime); **autoranging forbidden** — a ranging run to find peak V/I, then fixed ranges for record runs; ≥1 Hz logging; **≥60 s minimum windows, looping the workload if shorter**; NTP-grade clock sync between meter logger and SUT; per-window validity accounting (count of unknown samples, count of over-uncertainty samples, average uncertainty — uncertainty is a per-run reported quantity with a pass threshold, not a datasheet citation); Active Idle as a first-class measured segment (fixed delay to idle, then ≥240 s, measured *after* load in descending order); load levels defined as % of max measured throughput, never CPU utilization; ambient ≥20 °C reported per interval. **Battery clause (SPEC §6.5): a battery-backed system cannot produce valid wall comparisons unless charge flow is neutralized** — charge-inhibited, pinned charge state, or DC-side metering, disclosed either way. AC- and DC-referenced measurements are separate references, never interchangeable.

**Reporting that works:** per-interval table (avg W/V/A/PF, min ambient, perf metric, invalid-sample counts, avg uncertainty) — a ready-made run-manifest schema; load-level curves rather than single points; metrics named to forbid cross-benchmark comparison (supports JouleWise's LABELLED-floors convention).

**Avoid:** component-level proxies for system claims; TDP/PSU ratings as measurements; ad hoc idle settle times; publishing any window whose per-sample uncertainty was never computed.

## 5. Paired-MDE pre-registration (arXiv 2605.28873) — [abs](https://arxiv.org/abs/2605.28873) · [full HTML](https://arxiv.org/html/2605.28873)

**Adopt/adapt:** (i) The powered-MDE machinery, transposed to continuous energy with ABBA pair differences: `δ* = (z_{1−α/2}+z_{1−β})·σ_D/√m` and the workload-sizing inversion `m ≥ (z_{1−α/2}+z_{1−β})²·σ_D²/δ²` (2.80² at α=0.05, power 0.80) — **exactly the machinery the planned workload-sizing pilot needs**; pairing enters solely through σ_D, which absorbs ABBA drift cancellation the same way their ρ_d absorbs joint structure. (ii) The five-line pre-registration template with the **fail-closed prior-ratchet**: pre-register a conservative σ_D prior; if the campaign's observed U95 exceeds it, the floor recomputes at max(prior, U95) — ratchets up, never down. Grafts cleanly onto JouleWise's admission gates. (iii) The known-noise-model check: test whether observed run-to-run scatter matches an analytic noise reference before blaming instrument pathology. (iv) The systematic-error doctrine: when a systematic dominates the effect (their prompt template; JouleWise's attribution corner), **engineer it away by protocol before budgeting it**.

**Honest verdict on floor composition:** improves the *statistical* arm (JouleWise's repeatability statistic is not currently a powered quantity; theirs is, and it makes the ad hoc "claim-side ≈ floor + 5 J" replaceable by a principled δ* at stated power). Does **not** improve the *systematic* arm: their only composition is RSS of variance estimates, valid only for independent random components — RSS-ing JouleWise's worst-case attribution bound as if it were an SD would be anti-conservative. **JouleWise's max(repeatability, corner) + drift remains defensible**; the standard conservative alternative they never derive is linear addition (δ*_stat + B_attr + drift).

**Avoid (their own limitations):** they failed to retain per-example data and so couldn't run the paired analysis their own paper advocates — retain per-run/per-pair raw records or ABBA is unfalsifiable; the bound assumes i.i.d. — small-m ABBA campaigns under drift need block-aware variance estimates and exact tests, stated explicitly.

## 6. Beginner's Guide to Power Measurement (arXiv 2412.17830, NREL 35 pp) — [abs](https://arxiv.org/abs/2412.17830) · [PDF](https://arxiv.org/pdf/2412.17830) (HTML renders fail; PDF full)

**Adopt/adapt:** direct validation of the dual family ("report both absolute energy use and marginal power use"), with concrete upgrades: (i) **percentile-based idle** — their Scenario 2 defined idle as the 2nd percentile of power over a six-month window per node class, cross-validated by least-squares regression of active-idle offsets across repeated experiments — adapt as JouleWise's idle convention instead of a single dedicated idle run; (ii) **propagate idle variance** into the idle_subtracted number's uncertainty (baseline is "highly variable" per device and history); (iii) **active-idle awareness**: quiescent idle ≠ idle-during-load — stall-heavy phases break the subtraction assumption, so quiescent-baseline subtraction *overstates* attributable phase energy; (iv) always report runtime-on-hardware and peak power alongside energy (§3, §2.6.4 checklist); (v) fix and *report* power-management state (macOS power mode, display, thermal conditions per run).

**Avoid:** ranking on marginal energy alone (their two-device example flips winners between marginal and absolute); Nyquist/aliasing misreads on spiky loads (mitigated by repetitions — count them into m); comparing numbers measured under different methodology/scope. Note: the guide never mentions powermetrics or Apple Silicon, is qualitative throughout (its sole calibration number: physical = 1.059 × CodeCarbon), and its generic verdict — validate software readings against direct hardware measurement — points straight at the wall-meter gap. Nothing in it competes with JouleWise's floor arithmetic.

---

# TOP-10 improvements, ranked by value-for-effort

1. **Powered MDE for the repeatability arm + workload-sizing inversion** (Paper 5). Replace the informal repeatability statistic with δ* = 2.80·σ_D/√m (α=0.05, power 0.80) over ABBA pair differences, and size the pilot with m ≥ 2.80²·σ_D²/δ². Desk work on existing data; makes the ad hoc "+5 J claim-side" principled.
2. **Pre-registration prior-ratchet on the floor** (Paper 5). Pre-register a conservative σ_D prior per campaign; if observed U95(σ_D) exceeds it, floor recomputes at max(prior, U95) — never down. A few lines in the claims/gates machinery; converts pre-registration into an ex-ante detectability guarantee a reviewer can check before seeing numbers.
3. **Minimum-window rule + loop-to-60 s for short phases** (Papers 2, 4). Declare a duration-conditional validity domain (N× powermetrics cadence; SPEC's 60 s via workload looping) and fail-close phases below it — directly attacks the attribution-dominated 7–14 J floors, since edge error amortizes with window length.
4. **Internal dual-instrument cross-check before any wall meter** (Paper 2). Validate powermetrics integrals against an independent on-device channel (battery/SMC drain over long windows; channel-sum vs package reconciliation per TokenPowerBench Eq. 2) and publish the agreement bound with its validity domain — narrows "never externally validated" for free.
5. **Wall-meter validation designed to SPEC/Khan/CCGRID spec** (Papers 3a/3b/4) when D-018 lands. Meter with computed <1% uncertainty at 5–60 W loads (mind the <75 W crest-factor trap), battery charge neutralized (SPEC §6.5 or the run is invalid), ranging-then-fixed-range runs, lag-hunt, resample, then **regress wall = a·powermetrics + b per machine** (expect a ≠ 1 — never a constant offset) with held-out MAPE + channel ablation; wall validates totals only — phase splits stay pulse-train-validated and labelled as such.
6. **Per-window validity accounting in run manifests** (Paper 4/SPEC §8.2.2). Add invalid-sample count, over-threshold-uncertainty count, and average uncertainty as per-window reported quantities with pass thresholds — a natural extension of the existing fail-closed gates, and the schema reviewers of MLPerf-lineage work expect.
7. **Idle upgraded to a first-class measured segment** (Papers 4, 6). Percentile-based idle definition, fixed settle delay then a minimum idle window (SPEC: 240 s) measured after load, idle variance propagated into idle_subtracted uncertainty, and an explicit active-idle caveat on phase-level subtraction. Mostly convention + small analysis changes.
8. **Effect/floor ratio + "operationally meaningful" column in claim reports** (Paper 2). Report every claimed effect as a multiple of its floor, and separately state whether an above-floor effect matters in operational terms — one column, large credibility gain.
9. **powermetrics counter-mechanics audit** (Paper 3a). Run Khan's checklist against powermetrics itself: sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead (with/without sampler at each cadence) — the characterization nobody has published for Apple Silicon, and a citable contribution in its own right.
10. **Reporting-format adoptions** (Papers 1, 2, 3a, 6): per-phase J/token with per-phase denominators and context-length bins; max-stddev in figure captions; a Khan-style one-row-per-property summary table; runtime-on-hardware + peak power beside every energy number; campaign-energy disclosure. Pure formatting; matches the advisor plain-language standing rule.

**Cross-cutting strategic finding:** no paper measures phase energy *in situ* with quantified attribution error — TokenPowerBench asserts tagging without specifying it; the Illusion paper sidesteps via microbenchmarks; CCGRID explicitly refuses to adjudicate sub-total attribution without a reference. JouleWise's pulse-train-calibrated in-window attribution plus composed floors is genuinely unoccupied ground; the single-request-sequential scope is what makes it well-posed and should be framed as a design decision. Also confirmed: the max() composition for the systematic arm survives contact with all six papers — Paper 5's RSS applies only to independent random components, and linear addition is the only more-conservative published alternative.

Local artifacts: extracted full texts (RAPL, CCGRID, SPEC methodology) were saved by the validation agent under `/private/tmp/claude-501/-Users-edr-code-JouleWise/abec37a6-31cd-4c56-a8a8-9448acaf12be/scratchpad/` (session-scoped; copy out if wanted).95:| D-070 | Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings | accepted |
100:| D-075 | Extension-axis intake: ranked fold-in without new thesis proliferation | accepted |
3551:   the existing Q4/AP-1 holdout machinery (D-070 clause 5).
3709:## D-070: Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings
3873:## D-075: Extension-axis intake — ranked fold-in without new thesis proliferation
3882:index; D-070 keeps these axes as stress tests of Q4, caps candidate
3913:   violates D-070's single-Q4-thesis posture.
3925:D-070 remains the authority for Ed's axis commitments and quiet-Mac ordering.
3929:undetectable; or Ed changes the D-070 commitment set. Revisit by amending the

exec
/bin/zsh -lc "sed -n '3709,3940p' docs/decision_log.md; jq -c '.[]? | select((.axis // \"\") | test(\"attention mechanisms\"; \"i\"))' docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json 2>/dev/null || true" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## D-070: Architectural-axes extension agenda (AXI): scope, claim posture, batch-axis rulings

- Date: 2026-07-14 (Ed-directed; provenance `docs/axi-handoff.md`
  §1.1/§4/§5 plus Ed's rulings recorded this session)
- Status: accepted (C-033 coherence-reviewed)
- Phase: Phase 2+ research program

Decision:

1. **Agenda.** Once the harness works, it must be able to characterize
   architectural inference features generally — static batching,
   speculative decoding / MTP, MoE vs dense, quantization, and
   reasoning-length variance — framed as stress tests of the single Q4
   thesis (E = fixed + coefficients·work), not five new theses.
2. **Claim posture.** Instrument support (L0 smoke bundles) for ALL
   axes. Ed ruling 2026-07-14 (supersedes the handoff's narrower
   default): ALL five axes get characterized-claim commitments with
   dedicated quiet-Mac hardware time — it is Ed's own hardware and Ed
   wants maximum axis flexibility. Sequencing and floor discipline are
   unchanged: every AP remains floor-gated on P2-015 floors,
   `TASK_QUEUE.md` remains the ordering authority, Window A outranks
   everything, and no AXI stream consumes a [QUIET-MAC] window until
   Window A completes.
3. **Batch axis (Ed ruling).** STATIC batching only for the capstone:
   AP-BATCH covers B ∈ {1,2,4,8,16} static dispatch. Continuous
   batching is DEFERRED as a post-capstone, NV-gated extension — not
   killed. BINDING continuous-ready design constraint so the deferral
   stays additive rather than rework: all batch-related event schema is
   **request-scoped, not run-scoped** — token and phase events carry a
   `request_id`; each request gets its own lifecycle envelope
   (submit/prefill/decode/complete) even though static runs happen to
   synchronize them; no schema assumption that all sequences share one
   prefill boundary or one decode window. The reducer MAY exploit
   synchronization for static-mode metrics but MUST NOT require it at
   the schema level. Schema placement pin: `request_id` lives in event
   `metadata` (`events.jsonl` `metadata.request_id`) — the five-key
   event contract gains no sixth top-level key. Request-grouped
   lifecycle/phase pairing is NEW-version reducer dispatch, purely
   additive; legacy arms stay frozen and no existing bundle is
   re-dispatched (D-066 clause 2). Rationale: a single model instance
   with B KV
   caches is memory-feasible on current hardware; only the serving
   scheduler is hardware-gated, so a future continuous stream (load
   generator, steady-state detection, energy-per-token-at-offered-load
   metric) becomes purely additive on top.
4. **Registry.** Existing rows already carry the axes — the C5-* rows
   live in `docs/research_question_bank.md`; the C-023-* and RQ-* rows
   live in `docs/research_question_registry.md` (D-055): C5-2.2 and
   C5-2.6 (batching), C5-2.5 + C-023-OUTPUT-IDENTITY (spec decode),
   C5-1.1 / C5-1.9 / RQ-TWO-MODEL-ACTIVE-NONCLAIM (MoE/dense), C5-1.12
   + C-023-QUALITY-EQUIV-QUANT (quantization), RQ-ENERGY-VARIANCE +
   C5-W.2 (reasoning variance). Two new rows to mint at their gates:
   a **Mac-batching leg of C5-2.2** (minted ONLY on an S-B `supported`
   verdict), and **MOE×BATCH** (candidate, ceiling L2, forbidden
   upgrade: no MoE-serving-efficiency generalization from one pair).
5. **Ceilings.** Everything caps at L2 (L3 only through Q4/AP-1's
   existing holdout machinery); ceilings move only via replication rows
   (C5-3.1). No live claims from fixture-first code; PROVISIONAL until
   first live hardware contact.

Options considered: (a) five independent theses — rejected (dilutes
Q4 and is unfundable in the timeline); (b) axes as Q4 stress tests
with narrow claim commitments (the handoff default: MoE/dense +
batching only) — superseded by Ed's ruling; (c) axes as Q4 stress
tests with all-axes commitment — chosen by Ed.

Open item: the D-016 matched dense/MoE model pair remains with Ed and
the advisor; stream S-D presents the proposal (same family, matched
active params; fallback matched total) — do not finalize unilaterally.

Revisit triggers: an S-B `unsupported` verdict removes the Mac-batching
leg (the dated negative verdict is filed as a finding, Hailo idiom);
measured P2-015 floors that make a predeclared AXI effect size
undetectable send that AP back for redesign before any campaign is
scheduled.

## D-071: G10 memory-fit rule ratified (axi-sd-memory-fit-shape-v1); device-list review opened

Date: 2026-07-16. Owner: Ed (ruling given in-session; recorded verbatim
in intent).

1. **Ratified:** the `axi-sd-memory-fit-shape-v1` probe shape (batch 1,
   frozen 8,192-token prompt, exactly 128 EOS-masked greedy decode
   tokens, cold KV, no offload/swap), the peak-measurement semantics
   (load-start through decode token 128, full time series, one named
   counter per target), and the `H_t >= max(1 GiB, 0.15 * C_t)` reserve.
   G10 scoring may proceed; the scorecard's PROPOSED-FOR-ED status is
   cleared.
2. **Cap constant tracks the device list.** The 8 GiB capacity cap
   stands FOR NOW because it encodes D-016's 8 GB-class cross-target
   promise. Ed's conditional ("if we have to stick to the cap and
   device list for maximum research viability, fine — ratify") opens a
   device-list review: Ed's actual fleet is a 128 GB M3 Max MacBook
   Pro, a 3080 Ti (12 GiB VRAM) rig, and one or two Jetsons available
   if useful. A Sol xhigh brief (consult, this session) must answer:
   what research opportunity is lost by dropping the Jetson/8 GB tier
   and re-flooring the cap at the 3080 Ti class; the cap constant moves
   only by a recorded D-016 amendment after Ed reads that brief.
3. **Model-family direction (Ed):** prefer a best-in-class small model
   people actually use (Gemma-class or a current small Qwen) for the
   D-016 primary family; the brief must weigh re-pinning costs against
   the currently-pinned Qwen2.5-1.5B-Instruct (existing corpus, quant
   ladder §8, manifests). Big models are NOT closed off — they live in
   the Mac-only subsystem (Option A shape), never silently in the
   cross-target track.

## D-072: Standing self-merge-with-full-gate authority (gh merges included)

Date: 2026-07-16. Owner: Ed. Ed's session-scoped delegation ("handle
the merge yourself if all is well") is made STANDING: the lead may
self-merge agent-authored PRs via gh when and only when the complete
gate shape ran — fresh oversight reviews with distinct angles, lead
triage with recorded dispositions, fix rounds each delta-re-audited,
CI green on the final head, and a fresh pass over any post-review
commit (final-head rule). Ed may flag any PR as Ed-merge-only at any
time. This supersedes the per-session-delegation reading recorded
after the 2026-07-13 harness denial (C-032 row context): the denial
episode concerned standing-authorization-ONLY merges without an
explicit Ed grant; this entry IS that explicit grant. Evidence of the
gate shape lands in each merge commit body and the session run report.

Lease-adjudication note extension (2026-07-16): Ed approved the
remaining retained-lease batch — the three benign
ATTRIBUTION_INDETERMINATE closes from the AXI spec-design phase (lead
commits moving HEAD under long parallel leases; every diff verified
and landed) and the recurring session-open directory-normalization
artifact (5th instance; TOOL-01 carries the defect). Recorded per the
same adjudicated class as the 2026-07-15 approvals above.

## D-073: D-016 device-list amendment — Mac + 3080 Ti primary fleet, 12 GiB cap

Date: 2026-07-16. Owner: Ed (ruled on the D-071 brief,
`docs/process_traces/2026-07-16-device-list-brief/brief.md`). The
primary cross-target fleet is the 128 GB M3 Max Mac and the 3080 Ti
(12 GiB) rig; the G10 capacity cap re-floors from 8 GiB to **12 GiB**
(3080 Ti class sets the floor). Jetson hardware is retained as
OPTIONAL, non-cap-setting replication — the edge/8 GiB cell can be
added later as a replication row without re-deciding this. The split
study's two nodes are the Mac and the 3080 Ti rig. Big models remain
open via the Mac-only subsystem (D-071 clause 3). Follow-ons ruled by
Ed same session: (a) conditional primary-model repin remains open with
a WIDENED candidate search under the new cap (Ed: "is there really
nothing better than Qwen3-1.7B? Gemma 4B or something?") — 3-4B-class
models now fit comfortably; (b) dense/MoE pair re-search under the
12 GiB cap (OLMo dense arm failed G4 as published — see the OLMo
verification record in the same trace directory).

## D-074: Conditional Qwen3-4B primary repin + OLMo-1B conversion spike authorized

Date: 2026-07-16. Owner: Ed (ruled on the 12 GiB model search,
`docs/process_traces/2026-07-16-device-list-brief/model-search-12gib.md`).
(1) Qwen3-4B becomes the D-016 primary CONDITIONALLY: the repin lands
only when the evidence gates pass (immutable source/license,
MLX-Q4/GGUF-Q4/CUDA artifact receipts, three-runtime generation,
G10 at the 12 GiB cap, KV receipts, thinking-mode policy pinned);
any gate failure retains Qwen2.5-1.5B. New evidence era on success:
manifests + quant ladder regenerate from one frozen source revision;
Qwen2.5 results preserved as legacy. Runner-up Qwen3-1.7B; Gemma-3-4B
rejected for the gated custom license + multimodal MLX seam.
(2) The time-boxed OLMo-1B original-format→MLX conversion spike is
authorized; success revives the matched OLMoE pair, failure files the
dated negative finding and the pair defers (Option C) without
re-litigation. Both execute next session as agent-lane work.

## D-075: Extension-axis intake — ranked fold-in without new thesis proliferation

- Date: 2026-07-17
- Status: accepted (Ed-directed intake via the 2026-07-17 evaluation)
- Phase: Phase 2+ research program

Context: Ed directed a six-axis evaluation and ratified the resulting roadmap
at `docs/process_traces/2026-07-17-extension-axes/roadmap-synthesis.md`.
D-055 keeps C5 deliberation in the bank and the registry as the canonical live
index; D-070 keeps these axes as stress tests of Q4, caps candidate
commitments at L2, and reserves commitment authority to Ed. The disposition
ledger is `docs/stream_logs/2026-07-17-axes-foldin.md`.

Decision:

1. Admit C5-2.5c as the primary speculative-decoding Q4 break-even rider,
   C5-2.5b as its proposal-work secondary, and C5-2.5d as a mandatory
   contamination control. Preserve C5-2.5a in the deliberative bank as a
   deferred candidate rider only; it is not a standalone campaign commitment
   before a prospective cross-mechanism design is affordable. All four retain
   the evaluation's exact ceilings and forbidden upgrades, and
   C-023-OUTPUT-IDENTITY is binding.
2. Admit C5-2.11 as the on-device MLX quantized-KV candidate and attach it to
   C5-2.4, C5-1.12, and C-023-QUALITY-EQUIV-QUANT. Preserve C5-2.12,
   C5-2.13, and C5-2.14 only as candidate riders on the existing
   context/KV-growth, prompt-cache/replay, and Q4/AP-1 homes.
3. Admit one new canonical RQ row, RQ-AXI-HYBRID-PAIR, at an L2 named-pair
   ceiling. Attach the attention/context-slope and module-attribution
   refinements to existing rows. Record kernel/backend provenance as
   amendments to C5-1.8, C5-2.7, and C5-3.3, not new theses.
4. Keep the roadmap's do-not-fold set out of the canonical row set. Its
   negative dispositions and all unresolved feasibility questions remain in
   the stream ledger, including explicit **NEEDS-WEB** markers. Intake does
   not convert an unresolved runtime, model-pair, adapter, or device-fit
   question into a capstone commitment.

Options considered:

1. Mint every evaluated suggestion as an independent live question. Rejected:
   it duplicates existing homes, imports unidentifiable mechanism claims, and
   violates D-070's single-Q4-thesis posture.
2. Admit only the top three ranked items. Rejected: the lower-cost controls,
   riders, and provenance amendments prevent predictable attribution errors
   without creating independent theses.
3. Apply the roadmap's ranked fold-in and explicit exclusions. Chosen by Ed.

Considerations: this is research-agenda intake, not campaign scheduling or
evidence promotion. Every admitted candidate/rider remains floor-gated,
earliest-phase tagged, capped at L2 unless an already-existing parent row's
separate machinery says otherwise, and subject to its named forbidden
upgrade. The published corpus remains claim-evidence-flagged; no fixture,
runtime feasibility result, or registry entry is live energy evidence.
D-070 remains the authority for Ed's axis commitments and quiet-Mac ordering.

Revisit triggers: a relevant **NEEDS-WEB** feasibility finding lands; a named
runtime/pair becomes unsupported; P2-015 floors make a predeclared effect
undetectable; or Ed changes the D-070 commitment set. Revisit by amending the
owning row and this decision's ledger, never by silently promoting an excluded
candidate.

## D-076: Site capacity right-sizing (AUD-WO-039 review) — measured-first budgets

Date: 2026-07-17/18. Owner: lead under Ed's "host the brief" directive
(the capacity decision event AUD-WO-039 fenced on). Ruling, encoded in
tests with PR #76: the 1 MiB Lakebed hard cap is inviolate; the
measured-artifact budget is 1,000,000 B (measured mode via the pinned
validator, SITE-02 loud-discovery discipline); the 943,718 B
conservative-estimate guard remains ONLY as fallback when measured mode
{"axis":"Transformer architecture variants (dense vs MoE vs hybrid/SSM-mixers) and attention mechanisms (GQA vs MLA vs sliding-window vs sparse) as energy-profile subjects, including whether attention-vs-FFN phase attribution is in scope of the current event model","summary":"Sol's read-only high-effort assessment (bridge run 20260717T071639Z-74891, OK, valid envelope; lead checks replayed) splits this axis in two. The hybrid/SSM-mixer half is the valuable part: it stresses whether Q4's work coefficients survive when context-growing attention is replaced by recurrent state — a genuinely different stress than the already-committed MoE axis (conditional FFN activation, D-070) — and near-runnable subjects exist (Granite 4.0 H-Micro 3B vs Micro 3B as a named same-family hybrid/transformer pair; the state-spaces transformerpp/mamba2attn/mamba2 2.7B trio trained on the same 300B Pile tokens as the scientifically strongest but runtime-unverified design; Qwen3.5-4B DeltaNet-hybrid vs the already-mirrored Qwen3-4B GQA as a stack-generation contrast). The attention-mechanism half is currently weak: no MLA/GQA or SWA/full pair survives single-axis scrutiny (DeepSeek-V2-Lite MLA is confounded with MoE/size/tokenizer; Gemma generations change everything at once), llama.cpp's --swa-full is a cache-allocation toggle not an attention toggle, and --flash-attn is a kernel A/B not a mechanism A/B; sparse attention has no verified local execution path (Phi-3-small's block-sparse kernels are Triton/CUDA, NEEDS-WEB whether they actually execute on the fleet). On attribution: attention-vs-FFN time-slicing is OUT of scope of the landed event model — AXI-SA phases are request-lifecycle-level (phase_start/phase_end with request_phase_ordinal), powermetrics cadence cannot resolve per-layer intervals, and the RQ-SHORT-PREFILL-RESOLVABILITY precedent already rules out sub-cadence joule claims — so the honest designs are whole-request contrasts (nothing new needed) and fixed-output decode-phase context-length regressions whose context-associated slope must never be renamed an \"attention energy fraction\". Enrichment verdict medium overall: medium-high for the mixer sub-axis, low-medium marginal for attention mechanisms today since C5-1.2/RQ-KV-GROWTH already carry the context/KV-scaling question.","harness_difficulty":"Landed and sufficient for whole-request contrasts: gross_request/gross_batch_group window classes, events v2 with request-scoped phases and decode_emission (docs/specs/axi/sa_burst_decode_contract.md §§1-4), reducer 0.6.0, model/quant/artifact identity in ModelConfig (joulewise/schemas.py:349) plus MLX adapter runtime capture (joulewise/adapters/mlx_runtime.py:148), and — importantly — the stack-identity table already reserves 'Kernel/library where known: attention implementation' (docs/contracts/token_normalization.md:132), so attention-mechanism identity has a contractual home. The joulewise.axi_decode_config.v1 extension (joulewise/axi_decode_config.py) covers only batch_policy and speculation — it carries no architecture-taxonomy fields, and unknown config keys do not enter normalized identity (schemas.py extension handling), so an auditable architecture manifest (mechanism, layer pattern, Q/KV heads, trained window, SSM type, source-config digest) is new surface: bench-size if kept as campaign-side selection evidence, session-size if promoted into normalized metadata. Context-sweep regression designs are session-size and largely reuse C5-1.2/RQ-KV-GROWTH machinery plus an analysis plan. A matched-quant conversion + S-D-style G1-G10 receipts for a hybrid pair is session-size. Attention-vs-FFN module attribution is NOT in scope of the current event model: request-level phases cannot be relabeled module phases, and adding per-layer markers would not create power samples at per-layer timescales (powermetrics cadence; RQ-SHORT-PREFILL-RESOLVABILITY precedent, docs/research_question_registry.md:60) — module-isolating synthetic microbenchmarks or per-layer instrumentation are each a new subsystem, and the latter may remain unsuitable even after instrumentation. A llama.cpp adapter for the 3080 Ti is multi-session: RuntimeBackend.LLAMA_CPP exists (joulewise/schemas.py:184) but resolve_runtime has no branch for it (joulewise/adapters/__init__.py:147-150, verified).","feasibility":"Mac/MLX today: strongest leg. Falcon-H1 hybrids have MLX-LM support and mlx-community 4-bit artifacts (Sol web memo, huggingface.co/mlx-community/Falcon-H1-3B-Instruct-4bit); Granite 4.0 hybrid (Mamba2/attention) MLX and GGUF artifacts exist per IBM/HF cards, though same-recipe conversion receipts are still needed; DeepSeek MLA support is in current MLX-LM releases (~8.8 GB 4-bit V2-Lite fits the 128 GB Mac easily); Qwen3-4B-4bit and Qwen3.5-122B-A10B-4bit are already mirrored locally under /Users/edr/jw_models/mlx-community/. The state-spaces controlled trio is NEEDS-WEB + load-smoke: only mamba2-2.7b was confirmed in an mlx-community collection; generic mlx-lm loadability of transformerpp/mamba2attn under one pinned revision is unverified. 3080 Ti (12 GiB, D-073): JouleWise's only CUDA path today is the vLLM adapter over the node-worker protocol (joulewise/adapters/__init__.py:135-146) — no llama.cpp adapter exists despite the enum, so GGUF-based attention/hybrid subjects are not yet a campaign path on that node; DeepSeek-V2-Lite at 12 GiB is borderline (NEEDS-WEB/load verification). Sparse attention: no credible fleet path — Phi-3-small's documented block-sparse kernels target Triton/CUDA and actual sparse execution under local runtimes is NEEDS-WEB; a dense fallback must not be labeled a sparse-attention measurement. AMD/other: no adapter surface at all; out of scope per D-073 fleet posture. Same-artifact toggles: llama.cpp --flash-attn on|off is a genuine kernel A/B; --swa-full changes SWA cache allocation, not the mask; MLX-LM --max-kv-size is a rotating-cache policy, not a mechanism toggle; no MLA weight-absorption or SWA-mask-disable flag was established (NEEDS-WEB/source audit at the pinned revision).","candidate_rows":[{"id_suggestion":"RQ-AXI-HYBRID-PAIR","question":"For one predeclared, gate-passing hybrid(SSM/attention)-vs-pure-transformer pair (leading candidate: Granite 4.0 H-Micro 3B vs Micro 3B; preferred if runtime-enabled: the state-spaces 2.7B same-corpus trio) under matched runtime, quantization recipe, prompts, and output policy, how do gross request and decode-phase energy differ across governed context lengths?","ceiling":"L2 pair-specific characterization (D-070 clause 5)","forbidden_upgrade":"No architecture-class efficiency generalization, no causal SSM-mechanism attribution, and no tokenizer-blind ranking from one named model pair; 'this named pair' wording binding per the S-D scorecard idiom."},{"id_suggestion":"RQ-AXI-ATTN-CONTEXT-SLOPE","question":"Within each named artifact, how does fixed-decoded-output decode-phase gross energy change with initial context length, and are slope/saturation regimes (full-attention growth vs SWA/SSM saturation) repeatable above the P2-015 floor?","ceiling":"L2 boundary-labeled regression characterization","forbidden_upgrade":"No conversion of the context-associated coefficient into an attention-vs-FFN energy fraction, per-token rail claim, or module-level attribution; composes with C5-1.2/RQ-KV-GROWTH chunked-window limits rather than superseding them."},{"id_suggestion":"RQ-AXI-ATTN-KERNEL-AB","question":"For one artifact and pinned runtime build, does a documented attention-kernel toggle (e.g. llama.cpp --flash-attn on|off) change gross request energy while C-023-OUTPUT-IDENTITY equivalence gates pass?","ceiling":"L2 same-stack A/B characterization","forbidden_upgrade":"No attention-mechanism, cross-runtime, cross-hardware, or architecture-class efficiency conclusion from a kernel-implementation toggle; gated on the 3080 Ti leg acquiring an actual llama.cpp or equivalent adapter."},{"id_suggestion":"RQ-AXI-MODULE-ATTRIBUTION-NONCLAIM","question":"Negative-guard methodology row: record that attention-vs-FFN within-token energy attribution is not resolvable under the current event model and powermetrics cadence (request-level phases only; RQ-SHORT-PREFILL-RESOLVABILITY precedent), so any future module claim requires a new microbenchmark subsystem and its own contract.","ceiling":"L1 methodology ('not resolvable')","forbidden_upgrade":"No module-energy fraction, no relabeling of request phases as module phases, no inference of module shares from regression slopes."}],"risks":"Family/tokenizer confounding is the dominant risk — no available attention pair is a true single-axis contrast, so every claim must stay named-pair L2 and gross-request-first per docs/contracts/token_normalization.md, and reviewers will probe exactly this. Quantization sensitivity may differ between SSM and attention layers, breaking 'same recipe' comparability. Runtime fallback kernels can silently make a 'hybrid' or 'sparse' subject execute a different path than its architecture label (worst case: dense-fallback measurements labeled sparse-attention). Cache-policy toggles masquerade as attention toggles (--swa-full, --max-kv-size). Output divergence at long context can fail C-023-OUTPUT-IDENTITY gates mid-campaign. The regression design invites the exact over-attribution the registry polices elsewhere (context-slope renamed attention-fraction). Fleet asymmetry: until a llama.cpp adapter lands, the whole axis is effectively Mac-only, weakening cross-target framing. Finally, this axis competes for the same quiet-Mac windows as the five already-committed D-070 axes, and Window A outranks everything.","enrichment_score":"medium"}

web search: 
web search: site:github.com/ml-explore/mlx-lm Kimi Linear model support KDA mlx-lm ...
web search: 
web search: Kimi Linear KDA official paper 2510.26692 github moonshotai ...
codex
The fundable version is now clear: a causal four-way KDA/GQA/SWA/full-attention paper is not available from today’s checkpoints. KDA-versus-GQA would be a cross-model comparison with MoE, tokenizer, training, and size confounds, while current cache/kernel flags are not mechanism toggles. I’m therefore framing the honest proposal around one same-checkpoint sliding-window→full-attention ablation, with KDA/GQA retained only as named, non-causal context unless a desk gate finds a genuinely matched pair. This keeps the D-117 core intact and makes “refuse the mechanism claim” a predeclared outcome.
Completed the required repository reading, checked the current attention-axis feasibility record and governing decisions, and verified current primary public sources for KDA and MLX attention support. The proposal is narrowed to a same-checkpoint attention-window ablation because the requested four-way mechanism comparison is presently confounded.
  ✓ Read required paper, decision, trace, strategy, and research files plus repository safety state
  ✓ Extract instrument budgets, D-117 outputs, attention support, and effect-size evidence
  ✓ Draft and cross-check the reviewable proposal against all requested sections
codex
# Windowed Attention Under an Attribution-Limited Energy Instrument

**Thesis:** On one calibrated M3 Max stack, a same-checkpoint sliding-window-versus-full-attention ablation can test whether reducing long-context KV traffic produces a resolvable decode-energy saving, while the instrument must refuse broader KDA-versus-GQA mechanism claims when model and quality controls do not identify the cause.

## Project brief and steps

JouleWise already has the scientific spine of a strong metrology paper: runtime-emitted prefill/decode boundaries, in-window pulse-train calibration, LABELLED detection floors, separate floor-clearance and interval-direction gates, and a fail-closed custody protocol. Its central result is that `powermetrics` phase measurement is attribution-limited—about 1 J can move across a phase boundary from roughly 30 ms edge uncertainty and a 33 W swing—rather than noise-limited. More repetitions cannot remove that systematic term; phase contrasts should therefore be sized around the practical ≈5 J decision bar. Historical diagnostics indicate a large 1.5B-versus-7B decode effect (`phase_energy_j.decode` ≈141.29 J), but D-117 correctly makes all pre-genesis measurements non-claim-bearing.

The first investment remains the three D-117 windows: 1.5B floor plus prefill rider (budget 3.14 h), 7B floor plus prefill rider (3.24 h), and 1.5B-versus-7B decode contrast (2.80 h). Before arming them, desk work must finish the two-slot live-calibration ledger session, D-102 acceptance-successor path, four-cell mint, prefill extraction support, synthetic ledger regression, frozen plans, and pinsets. Passed windows then mint two decode floors, two prefill floors, and the decode contrast and populate the existing paper.

Only after that core closes should this attention extension spend nights. The requested causal four-way KDA/GQA/sliding/full comparison is not presently honest: released Kimi Linear combines KDA, MLA, MoE, a different tokenizer, and different training, so comparison with Qwen GQA cannot isolate attention. Its reported 75% KV-cache reduction and up-to-6× throughput are not energy measurements. [Moonshot’s model card](https://huggingface.co/moonshotai/Kimi-Linear-48B-A3B-Base) The paper should shrink to a same-checkpoint sliding-window/full-attention ablation; KDA/GQA remain named, non-causal context unless desk work discovers a genuinely controlled pair.

## Contributions

1. **Prospective phase metrology:** Mint claim-bearing 1.5B and 7B prefill/decode floors and a decode model-size contrast; any failed calibration, custody, floor, or interval gate falsifies the corresponding claim.

2. **Attention-window ablation:** Test whether forced full attention consumes more decode energy than native sliding-window attention above the trained window, using identical weights, tokenizer, quantization, runtime, prompts, and outputs.

3. **Causal sanity check:** Require the same two modes to be unresolved below the sliding-window length. A clear below-window difference would falsify the interpretation that the long-context effect comes from windowed KV access.

4. **Mechanism-claim refusal rule:** Demonstrate that architecture labels alone do not license KDA/GQA energy attribution; unmatched quality, changed outputs, or an unverified runtime path produces a published refusal.

## Experiment plan

Desk-gate one MLX-supported, 4–7B-class checkpoint whose native sliding-window mask can be changed to full attention without changing weights. Freeze an architecture manifest containing layer pattern, window size, Q/KV heads, source-config digest, runtime commit, and executed cache type. Use fixed token-ID prompts, greedy EOS-masked 512-token decode, and two contexts: one below the window and one approximately four times the window. A 256-prompt desk roster must establish exact output-token identity; merely similar prose is insufficient.

After that gate, use three additional quiet windows:

- **Native-window floor:** at both contexts, five absolute members and five null ABBA blocks per cell: 10 absolute plus 40 null runs total.
- **Forced-full floor:** identical design under the full-attention mode.
- **Science contrast:** five ABBA blocks at each context, 40 runs total, full-minus-window orientation.

Every window retains live pre/post calibration, 12 same-window bound members, 3/1/3 drift references, immutable membership, and 20% runtime margin. Budget **2.5–4 h each, uncertain until timed pilots**; reject any plan that cannot fit four hours.

At the short context, expect **<5 J, uncertain**, hence a scientifically useful unresolved result. At the long context, a rough estimate is **10–80 J, highly uncertain**: the diagnostic Qwen2.5-7B decode level is about 192 J for 512 outputs, and longer-context KV reads could move energy by roughly 5–30%. Server evidence finds much larger architecture effects—up to roughly half of request energy—but on H200 and production batches, so it is only a sizing prior, not transportable evidence. [H200 attention-energy study](https://arxiv.org/abs/2605.11999) Require a desk-pilot projected effect of at least **10 J (2× the practical bar)** before spending a night.

This adds architecture identity, a verified mask/cache toggle, dual-context campaign generation, and output-identity gating. It does **not** violate the frozen single-request boundary and adds no per-layer energy attribution.

## Hardware and instrument needs

Owned M3 Max, 128 GB, the existing MLX/`powermetrics` instrument, and locally stored model artifacts are sufficient. No RTX, Jetson, or new acquisition is required. The WT310E is **not a dependency**: it could validate whole-machine totals later, but it cannot validate prefill/decode or attention-layer attribution.

## Venue and relationship to the MVP

The D-117-only paper is a strong capstone/CSCSU submission. A successful attention ablation raises it toward EuroMLSys, HotCarbon, or ICPE Emerging Research. ICPE full-track becomes credible if the effect clears both gates, the short-context control behaves correctly, and the artifact is reproducible.

Reuse MVP Sections 1–6 almost intact: measurement boundary, bracketed calibration, floor composition, attribution-limited finding, ABBA protocol, custody, and refusal evidence. D-117 replaces the pending demonstration section. New material is one architecture-manifest subsection, the output-equivalence gate, and the attention-window results.

## Risks and kill criteria

Kill the extension before hardware if no checkpoint offers a source-proven same-weight toggle; MLX silently falls back to another cache/kernel; exact outputs diverge materially; the model swaps or misses admission; long-context pilot projection is below 10 J; or the frozen campaign exceeds four hours with margin. Never reinterpret a cache-allocation flag as an attention mechanism. If killed, publish the solid D-117 metrology paper and retain the attention study as a documented feasibility refusal.

## Relation to Ed’s original goals

This directly serves the original mechanism-level attention/KV axis and tests whether the modular harness can swap an inference mechanism while preserving scientific controls. It does not yet satisfy the broader KDA, MTP, MoE-routing, or split-inference goals; it establishes the disciplined template those studies would need.
tokens used
188,039
# Windowed Attention Under an Attribution-Limited Energy Instrument

**Thesis:** On one calibrated M3 Max stack, a same-checkpoint sliding-window-versus-full-attention ablation can test whether reducing long-context KV traffic produces a resolvable decode-energy saving, while the instrument must refuse broader KDA-versus-GQA mechanism claims when model and quality controls do not identify the cause.

## Project brief and steps

JouleWise already has the scientific spine of a strong metrology paper: runtime-emitted prefill/decode boundaries, in-window pulse-train calibration, LABELLED detection floors, separate floor-clearance and interval-direction gates, and a fail-closed custody protocol. Its central result is that `powermetrics` phase measurement is attribution-limited—about 1 J can move across a phase boundary from roughly 30 ms edge uncertainty and a 33 W swing—rather than noise-limited. More repetitions cannot remove that systematic term; phase contrasts should therefore be sized around the practical ≈5 J decision bar. Historical diagnostics indicate a large 1.5B-versus-7B decode effect (`phase_energy_j.decode` ≈141.29 J), but D-117 correctly makes all pre-genesis measurements non-claim-bearing.

The first investment remains the three D-117 windows: 1.5B floor plus prefill rider (budget 3.14 h), 7B floor plus prefill rider (3.24 h), and 1.5B-versus-7B decode contrast (2.80 h). Before arming them, desk work must finish the two-slot live-calibration ledger session, D-102 acceptance-successor path, four-cell mint, prefill extraction support, synthetic ledger regression, frozen plans, and pinsets. Passed windows then mint two decode floors, two prefill floors, and the decode contrast and populate the existing paper.

Only after that core closes should this attention extension spend nights. The requested causal four-way KDA/GQA/sliding/full comparison is not presently honest: released Kimi Linear combines KDA, MLA, MoE, a different tokenizer, and different training, so comparison with Qwen GQA cannot isolate attention. Its reported 75% KV-cache reduction and up-to-6× throughput are not energy measurements. [Moonshot’s model card](https://huggingface.co/moonshotai/Kimi-Linear-48B-A3B-Base) The paper should shrink to a same-checkpoint sliding-window/full-attention ablation; KDA/GQA remain named, non-causal context unless desk work discovers a genuinely controlled pair.

## Contributions

1. **Prospective phase metrology:** Mint claim-bearing 1.5B and 7B prefill/decode floors and a decode model-size contrast; any failed calibration, custody, floor, or interval gate falsifies the corresponding claim.

2. **Attention-window ablation:** Test whether forced full attention consumes more decode energy than native sliding-window attention above the trained window, using identical weights, tokenizer, quantization, runtime, prompts, and outputs.

3. **Causal sanity check:** Require the same two modes to be unresolved below the sliding-window length. A clear below-window difference would falsify the interpretation that the long-context effect comes from windowed KV access.

4. **Mechanism-claim refusal rule:** Demonstrate that architecture labels alone do not license KDA/GQA energy attribution; unmatched quality, changed outputs, or an unverified runtime path produces a published refusal.

## Experiment plan

Desk-gate one MLX-supported, 4–7B-class checkpoint whose native sliding-window mask can be changed to full attention without changing weights. Freeze an architecture manifest containing layer pattern, window size, Q/KV heads, source-config digest, runtime commit, and executed cache type. Use fixed token-ID prompts, greedy EOS-masked 512-token decode, and two contexts: one below the window and one approximately four times the window. A 256-prompt desk roster must establish exact output-token identity; merely similar prose is insufficient.

After that gate, use three additional quiet windows:

- **Native-window floor:** at both contexts, five absolute members and five null ABBA blocks per cell: 10 absolute plus 40 null runs total.
- **Forced-full floor:** identical design under the full-attention mode.
- **Science contrast:** five ABBA blocks at each context, 40 runs total, full-minus-window orientation.

Every window retains live pre/post calibration, 12 same-window bound members, 3/1/3 drift references, immutable membership, and 20% runtime margin. Budget **2.5–4 h each, uncertain until timed pilots**; reject any plan that cannot fit four hours.

At the short context, expect **<5 J, uncertain**, hence a scientifically useful unresolved result. At the long context, a rough estimate is **10–80 J, highly uncertain**: the diagnostic Qwen2.5-7B decode level is about 192 J for 512 outputs, and longer-context KV reads could move energy by roughly 5–30%. Server evidence finds much larger architecture effects—up to roughly half of request energy—but on H200 and production batches, so it is only a sizing prior, not transportable evidence. [H200 attention-energy study](https://arxiv.org/abs/2605.11999) Require a desk-pilot projected effect of at least **10 J (2× the practical bar)** before spending a night.

This adds architecture identity, a verified mask/cache toggle, dual-context campaign generation, and output-identity gating. It does **not** violate the frozen single-request boundary and adds no per-layer energy attribution.

## Hardware and instrument needs

Owned M3 Max, 128 GB, the existing MLX/`powermetrics` instrument, and locally stored model artifacts are sufficient. No RTX, Jetson, or new acquisition is required. The WT310E is **not a dependency**: it could validate whole-machine totals later, but it cannot validate prefill/decode or attention-layer attribution.

## Venue and relationship to the MVP

The D-117-only paper is a strong capstone/CSCSU submission. A successful attention ablation raises it toward EuroMLSys, HotCarbon, or ICPE Emerging Research. ICPE full-track becomes credible if the effect clears both gates, the short-context control behaves correctly, and the artifact is reproducible.

Reuse MVP Sections 1–6 almost intact: measurement boundary, bracketed calibration, floor composition, attribution-limited finding, ABBA protocol, custody, and refusal evidence. D-117 replaces the pending demonstration section. New material is one architecture-manifest subsection, the output-equivalence gate, and the attention-window results.

## Risks and kill criteria

Kill the extension before hardware if no checkpoint offers a source-proven same-weight toggle; MLX silently falls back to another cache/kernel; exact outputs diverge materially; the model swaps or misses admission; long-context pilot projection is below 10 J; or the frozen campaign exceeds four hours with margin. Never reinterpret a cache-allocation flag as an attention mechanism. If killed, publish the solid D-117 metrology paper and retain the attention study as a documented feasibility refusal.

## Relation to Ed’s original goals

This directly serves the original mechanism-level attention/KV axis and tests whether the modular harness can swap an inference mechanism while preserving scientific controls. It does not yet satisfy the broader KDA, MTP, MoE-routing, or split-inference goals; it establishes the disciplined template those studies would need.
